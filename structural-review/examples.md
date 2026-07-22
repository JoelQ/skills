# Worked Example: Contractor Hierarchy Project Update

A refactoring that demonstrates each step of the analysis process. The code
determines which contractors' project records should receive a work-order update
when a subcontractor records one.

## The Original Code

```ruby
def contractors_for_project_update(project)
  closure_rows = ancestor_closure_rows
    .where(project_context: project)
    .or(ancestor_closure_rows.where(depth: 0))
    .order(depth: :asc)
    .includes(ancestor_contractor: :project_records)

  return [] if closure_rows.empty?

  ancestor_contractor_ids = closure_rows.map(&:ancestor_contractor_id)
  restricted_pairs = ContractorRelationship
    .where(parent_contractor_id: ancestor_contractor_ids,
           child_contractor_id: ancestor_contractor_ids,
           sharing_status: "restricted")
    .pluck(:parent_contractor_id, :child_contractor_id)
    .to_set

  contractors = [closure_rows.first.ancestor_contractor]

  closure_rows.each_cons(2) do |child_row, parent_row|
    next if restricted_pairs.include?(
      [parent_row.ancestor_contractor_id, child_row.ancestor_contractor_id]
    )
    contractors << parent_row.ancestor_contractor
  end

  contractors
end
```

## Step 1: Name the Concepts

The domain has three key concepts, each stored in a different representation:

- **Paths** (closure table) — transitive reachability between contractors. A
  path from A to C means A is an ancestor contractor of C. Paths carry a
  `project_context` but do not record the sharing status of each hop.
- **Relationships** (relationships table) — direct contractor/subcontractor
  connections. Each relationship has a `sharing_status` (`restricted` or
  unrestricted) that paths do not carry.
- **Contractors** (nodes) — the entities whose project records receive updates.

The code exposes partial, representation-shaped vocabulary:
`closure_rows`, `ancestor_contractor_ids`, and `restricted_pairs`. It names
contractors, but not paths or relationships as first-class concepts;
`restricted_pairs` describes a lookup structure rather than the relationship it
represents.

## Step 2: Spot the Leaks

Four things a reader would pause on:

1. **"Why include depth-0 rows?"** — Depth 0 is the self-referencing entry in
   the closure table. It is included so `each_cons(2)` has something to pair
   with the first real ancestor. This is a closure-table implementation detail
   leaking into business logic.

2. **"Why does order matter?"** — Rows are ordered by depth so `each_cons(2)`
   produces adjacent pairs. But the business rule ("share updates with
   unrestricted ancestors") is a set operation that does not require ordering.

3. **"Why a Set of ID pairs?"** — The `restricted_pairs` Set exists for O(1)
   lookup inside the loop. It is a performance optimization for the traversal
   approach, not a domain concept.

4. **"Why two separate queries?"** — The first query over-selects (it returns
   all project-context ancestors, including ones behind restricted
   relationships). The second query finds restricted pairs so Ruby can prune
   the over-selection. The two-pass pattern exists because the closure table
   does not carry relationship sharing status.

All four leaks trace back to the same root: **the code frames this as a
traversal problem (walk adjacent pairs, skip some) when the domain problem is a
set operation (which contractors should receive the update?).**

## Step 3: Generate Alternative Framings

The domain problem, stated independently: "Given a contractor and a project,
find all ancestor contractors reachable through unrestricted relationships."

**Framing A — Traversal (original):** Walk adjacent pairs in depth order, skip
restricted parents. Requires: depth ordering, depth-0 padding, Set of pairs,
`each_cons`.

**Framing B — Set difference:** All project-context ancestors, minus those
behind restricted relationships. Eliminates: depth ordering, depth-0,
`each_cons`. Still requires a negative filter (get everything, remove some).

**Framing C — Positive filter:** From all direct relationships between
ancestors, keep the unrestricted ones. Eliminates: even the set difference.
Asks a positive question ("which relationships allow sharing?") instead of a
negative one ("which relationships are restricted?").

**Framing D — Scoped query chain:**
```ruby
ancestors.in_project(project).to_relationships.unrestricted
```
Code maps 1:1 to domain concepts. Every method name is a domain term. Every dot
is a representation shift (paths → relationships → filtered relationships).

Each successive framing eliminates machinery. Framing D has the best overlap
between code structure and domain — the "invalid values" region (where the
abstraction extends beyond the domain) is minimal.

## Step 4: Make It Self-Documenting

With framing D chosen, apply the techniques:

- **Named the representation crossing** — `to_relationships` makes the shift
  from paths to relationships explicit. Without it, the crossing was hidden
  inside query mechanics.
- **Used existing vocabulary** — `unrestricted` already existed as a scope on
  `ContractorRelationship`. No new code needed.
- **Pushed generic operations to the domain object** — `to_relationships`
  belongs on `ContractorPath` (it is a general operation: "given paths, find
  the corresponding direct relationships"), not as a private method at the
  call site. `unrestricted` belongs on `ContractorRelationship`. This enriches
  both objects' vocabularies for any future caller.
- **Named up at the call site** — The public method
  `ancestor_contractors_for_project` gives a context-specific name to the
  composition.
- **Moved context-specific struct to its consumer** — `ProjectUpdateRecipients`
  moved from `Subcontractor` to `WorkOrderUpdateCreator`, the only place that
  uses it.

## The Result

```ruby
def ancestor_contractors_for_project(project)
  unrestricted_parent_ids = ancestors
    .in_project(project)
    .to_relationships
    .unrestricted
    .select(:parent_contractor_id)

  [self] + Contractor.where(id: unrestricted_parent_ids).includes(:project_records)
end
```

## Key Takeaway

The original code had the same four logical steps, but they were obscured by
machinery that served the traversal approach, not the domain. Naming the
concepts (step 1) gave vocabulary to describe the leaks (step 2). The leaks all
pointing to one root cause suggested a paradigm shift (step 3). The new paradigm
made self-documenting code almost automatic (step 4).

---

# Worked Example: The "Better Algorithm" Trap

A review that illustrates the subtler self-check failure: generating a framing
that eliminates several leaks by improving the algorithm, while the surviving
leaks still trace to the original root cause.

## The Code

A service builds a flat list of subcontractor rows for a tree-grid UI. Within a
project, each subcontractor has one direct parent, so the contractor hierarchy
is a tree even though it is stored as closure-table rows. The service fetches
one row per project path per descendant, deduplicates them to one per contractor,
iterates in depth order to build hierarchy paths with a mutable cache, and sorts
siblings alphabetically.

```ruby
def build_subcontractors(project)
  closure_rows = @contractor.descendants
    .in_project(project)
    .includes(:descendant_contractor, :direct_parent_relationship)
    .order(:depth)
    .to_a

  closure_rows = deduplicate_closure_rows(closure_rows)

  hierarchy_cache = {}

  closure_rows.filter_map do |row|
    relationship = row.direct_parent_relationship
    next unless relationship

    parent_path = hierarchy_cache[relationship.parent_contractor_id] || []
    path = parent_path + [row.id.to_s]
    hierarchy_cache[row.descendant_contractor_id] = path

    { id: row.id, name: row.descendant_contractor.name,
      type: relationship.relationship_type, depth: row.depth, hierarchy: path }
  end
end
```

## The Leaks

Five leaks, three sharing a root cause:

1. **Depth ordering** — required so the cache has parents before children
2. **Mutable cache** — compensates for not having tree structure
3. **Deduplication** — bridges per-project closure rows to per-contractor output
4. **ID-space crossing** — cache keyed by contractor IDs, paths built from closure-row IDs
5. **Silent nil guard** — `next unless relationship` drops unresolvable closure rows

Root cause of 1-3: **the code operates on closure rows (per-project ancestor
paths) but the domain is a tree of contractors.**

## The Trap: Framing B (Relationship Map)

A relationship-map framing replaces the mutable cache with a pre-built adjacency
map and computes each path independently by walking the map:

```ruby
parent_relationship = index_parent_relationships(closure_rows)

closure_rows.filter_map do |closure|
  relationship = parent_relationship[closure.descendant_contractor_id]
  next unless relationship
  { hierarchy: path_to_root(closure.descendant_contractor_id, parent_relationship), ... }
end
```

This eliminates three leaks: depth ordering (no processing-order dependency),
mutable cache (replaced by a static map), and ID-space crossing (paths use
contractor IDs). But deduplication and the nil guard survive — the code still
iterates over closure rows and compensates for their per-project granularity.

Applying the self-check: the surviving leaks still trace to the root cause
(operating on closure rows instead of contractors). The framing improved the
algorithm within the closure-row representation, not changed the representation.

## The Reification Framing

Asking "what IS a closure row?" rather than "how should we process closure rows?"
produces the key insight: closure rows are a **serialization format** for a tree.
The depth-ordered iteration with a mutable cache is **reimplementing tree
traversal** over serialized data.

The fix: deserialize at the boundary.

```ruby
tree = contractor.descendants
  .to_tree
  .sort_children_by { |node| node.value.name.downcase }

tree.with_materialized_paths.map do |path, node|
  { id: node.value.id, name: node.value.name,
    type: node.value.relationship_type,
    depth: path.length,
    hierarchy: path.map { |n| n.value.id.to_s } }
end
```

This eliminates all five leaks. Deduplication moves inside `to_tree` (a
serialization-boundary concern). Depth ordering, the cache, the ID crossing,
and the nil guard all disappear because tree operations (sorting children,
computing paths) are native to the data structure.

## The Lesson

The relationship-map framing was seductive because it eliminated three leaks
and felt like real progress. But it was solving the problem "how to process closure
rows better" rather than "what data structure does this problem want." The
diagnostic that would have caught it: the surviving leaks (deduplication, nil
guard) still compensated for the input's shape. The reification diagnostic —
"does the code manually reimplement operations a data structure provides
natively?" — points directly at the tree.
