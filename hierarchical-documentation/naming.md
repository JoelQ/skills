# Naming Techniques

Advanced naming techniques for identifiers: altitude, contrast, crossings,
vocabulary, and structural cooperation.

## Name for role, not structure

What does this thing *do here*? Name the role it plays, not the data structure it is.

`recipient_contractors` over `contractors`. Use existing domain predicates
(`work_order.assigned_to_contractor?`) over raw comparisons
(`assignee_type == "Contractor"`).

## Name at the right altitude

Names should be precise enough to distinguish from siblings, but no more
specific than the concept they represent.

- **Too low** (vague): `contractors` — which contractors? what role?
- **Too high** (exhaustive):
  `contractors_that_receive_project_records` — reads like a
  comment, breaks when logic changes
- **Right altitude** (role): `recipient_contractors` — distinguishes from other
  contractor collections, names what they do here

The test: could you make this more generic without losing signal? If so, it's at
the right altitude. If the name includes details that could change independently
of the concept, it's too specific.

## Name with structure

A name doesn't have to explain everything alone — it can work with surrounding
code to create compound meaning.

When a conditional has a passthrough branch and an action branch, the predicate
can name the state that makes the action unnecessary:

```ruby
if already_includes_subcontractors?(scope)
  scope
else
  scope.or(subcontractor_visibility_clause)
end
```

The `already_` prefix paired with a no-op true branch tells the reader the else
branch adds subcontractor visibility — without the name having to say so. The name
and the branch structure cooperate.

The pattern generalizes: `already_cached?` with a return-early,
`already_sorted?` with a passthrough. Each works because the reader sees "if
this is already done, skip; otherwise, do it."

## Name representation crossings

When code shifts between data representations, name the boundary explicitly. A
method like `to_relationships` makes the crossing from contractor paths to
contractor relationships visible. Hidden crossings are a major source of "wait, why
does this query return *that*?" confusion.

Similarly, `direct_contractors` names a crossing from a mixed result set
(contractors + subcontractors) to a filtered one. The name tells the reader the
input contains more than direct contractors.

## Name to create vocabulary

When a concept appears as a raw check at a call site, that's a signal it may
want to become a named predicate on the domain object.

```ruby
# Raw check — every call site knows the implementation
if contractor.relationship_type == "subcontractor"

# Named predicate — the model owns the concept
if contractor.subcontractor?
```

The trigger is noticing a *name is missing* — the code asks a domain question
using implementation terms. Adding the predicate gives the concept a name and
contributes another composable primitive to the model's vocabulary — building
toward a rich set of primitives that let future callers express new ideas by
combination rather than reimplementation.

## Name the contrast

When a name could be framed positively or negatively, match the framing to what
the reader is thinking about next.

- `direct_contractors` tells the reader what's *in* the result — use when the next
  question is "what will I be working with?"
- `exclude_subcontractors` tells the reader what was *removed* — use when the next
  question is "what won't be there?"

The test: after reading the name, does the reader have to mentally invert it to
understand the code that follows? If so, flip the framing.
