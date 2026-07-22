---
name: structural-review
description: Analyze code structure by identifying leaky abstractions, naming domain concepts, and exploring alternative framings. Use when the user asks to review code structure, simplify an approach, question a design, raise the abstraction level, or check whether code structure aligns with the problem domain.
---

# Structural Review

Analyze whether code structure aligns with the problem domain through a
three-step diverge-converge process: name the domain concepts, spot leaky
abstractions, then generate and evaluate alternative framings.

## Analysis Process

Walk through each step explicitly. Steps 1-2 build the foundation — naming
the domain and identifying where the code diverges from it. Step 3 is a
diverge-converge process: generate multiple framings broadly before evaluating
any, then converge on the one that best closes the gap between code structure
and domain structure.

### Step 1: Name the Concepts

Before analyzing the code, identify and name the domain entities, relationships,
and operations at play. What are the nouns and verbs? What information does each
concept carry?

This is lightweight DDD — not bounded contexts and aggregates, just naming
things precisely. Build a vocabulary rooted in the domain, not the
implementation. Often the code uses implementation-flavored terms (e.g.,
"closure_rows" when the domain concept is "ancestor paths"). Naming that gap
reveals where abstractions are leaking.

Look for:
- Domain entities the code operates on but doesn't name
- Implementation terms used where domain terms would be clearer
- Concepts that span multiple data representations (the same "thing" lives in different tables or structures)
- Domain states represented as absence (nil, empty, missing key) rather than as
  a named concept — give these the same definitional weight as explicit concepts.
  If the domain has four states and the code names three, the fourth is not
  "the absence of the other three"; it is a concept the code has failed to reify.

Before moving to Step 2, verify each concept from Step 1 has a corresponding
representation in the code. Any concept that's absent, unnamed, or represented
as nil is a modeling gap — carry it into Step 2 as a finding before scanning
for anything else.

### Step 2: Spot the Leaks

Scan for places where a reader would pause and ask "why?" — specifically, where
the code forces the reader to think about **implementation machinery instead of
domain concepts**. These are leaky abstractions, not generic code smells (dead
code, duplication, etc. are a different concern).

Method-level awkwardness — nil guards, duplicated branches, explanatory
comments — is often a symptom of a structural issue, not the issue itself.
When you spot awkward code, follow it upstream: ask what modeling choice
produced this awkwardness. Report the modeling gap, not the symptom. The
method is where you notice the problem; the model is where it originates.

Leaks look like:
- Constraints that serve the approach, not the domain ("why does order matter in a set operation?")
- Implementation details surfacing in business logic ("why does depth-0 appear here?")
- Code requiring the reader to understand a data structure's internals to follow the logic
- Raw type checks or string comparisons where a domain predicate already exists
- Surprising requirements that every reviewer asks about
- Proxy checks: testing one property as a stand-in for a different property that
  actually matters ("why are we checking contractor tier when the question is
  about project ownership?"). The proxy derives from circumstantial evidence what could
  be observed directly as a settled fact in the data. Diagnostic: a reader asks
  "why is this concept relevant here?" and the answer is "it's a stand-in for
  another concept."
- Nil/null carrying domain semantics: code branches on nil to execute meaningful
  behavior (not error handling), meaning nil implicitly stands for a domain
  value — "guest user," "standard permission," "default behavior." This is
  primitive obsession in the context of nullability. Nil should mean "missing
  data," not a specific domain concept. Diagnostic: if you can finish the
  sentence "nil means ___" with something other than "absent" or "unknown," nil
  is projecting semantics that belong in an explicit value. The fix is
  reification — give the implicit concept a name and a representation.
- Comments that translate between the code's representation and the domain's
  vocabulary — e.g., "a blank X means Y" or "nil here indicates Z" — are the
  code confessing a modeling gap. The developer noticed the representation
  doesn't speak for itself and documented around it. Treat these as high-signal
  starting points.

The key question for each leak: **"Does the domain require this, or does the
current approach require this?"**

**Trace each gap outward before evaluating severity.** A modeling gap rarely
produces a single symptom — it ripples through every function that stores,
passes, returns, validates, or branches on the missing concept. For each gap
identified (from Step 1 or from a leak found above), follow the value through
the code: where is it produced? Where is it consumed? Where is it compared,
validated, or branched on? Each location where the gap forces awkward code — a
nil check, a special case, an explanatory comment, an ambiguous return value,
a collection that should contain it but doesn't — is a separate leak. Count
them. A gap that seems minor viewed at one call site often reveals itself as
the dominant structural issue once you see its full downstream footprint.

**Before proceeding to Step 3, group the leaks by root cause.** If three or more
leaks trace to the same structural choice (data shape, traversal order,
representation), name that shared root cause explicitly — it is the primary
target for Step 3, which must include at least one framing that eliminates it
entirely, not just reorganizes the code around it.

### Step 3: Diverge-Converge on Framings

The goal is to find where domain structure and code structure diverge, then
close the gap. This is a two-phase process: diverge first (generate breadth),
then converge (evaluate and pick).

#### Diverge

Don't anchor on the current approach. Describe the domain problem independently
of how the code solves it — if your problem description mentions specific
methods, variables, or entity types from the current code, you're describing
the approach, not the problem. Strip the implementation nouns.

Generate at least one framing per relevant mismatch axis before evaluating any.
Don't discard framings during generation. If Step 2 identified a root cause,
each framing must address it.

Mismatches show up along several axes (not exhaustive — pick what's relevant):

**Processing paradigm** — the code uses the wrong algorithm shape:
- Set operations vs. sequential iteration
- Query composition vs. procedural filtering
- Transformation pipelines vs. mutation
- Positive vs. negative filters (keep vs. exclude)
- Composition vs. orchestration
- Declarative vs. imperative

**Perspective** — the code frames the problem from the wrong entity's point of
view. Which entity's perspective makes the problem have fewer rules? If code
branches on entity type to dispatch behavior, the right protagonist may make
polymorphism a natural consequence rather than a technique.

**Representation (reification)** — a domain concept's structure exists implicitly
in the code but has no corresponding object. Data arrives in one shape (flat
rows, denormalized records, serialized blobs) but the domain operates on a
different shape (trees, graphs, sets). Compensating machinery accumulates:
manual path-tracking for trees, adjacency bookkeeping for graphs, dedup passes
for sets. If Step 1 named a concept whose structure exists in the domain but not
in the code, reifying it — converting to the right data structure at the
boundary rather than compensating throughout — often eliminates that machinery
entirely. A common failure mode is anchoring on the input shape: accepting the
structure the database or API hands you as the structure to process in.
Diagnostic: name what each data representation IS in structural terms —
serialization format, index, cache, projection. The category suggests the fix
(serialization → deserialize at the boundary, index → query it, projection →
fetch the source). Then check: does the code manually reimplement operations
that a well-known data structure provides natively (sorting children, computing
paths, finding neighbors)? If so, the code is operating on a serialized form
and should convert to the domain's native structure before processing.

#### Converge

Now evaluate. For each framing, sketch what the code would look like. The model
(code) should cover reality (domain) with minimal region where the abstraction
extends beyond what the domain requires. When machinery disappears because the
framing no longer needs it, that's a strong signal. The winning framing is the
one that eliminates the root cause with the least machinery, not the first one
that seems reasonable.

**Self-check:** For each framing, count how many Step 2 leaks it eliminates
outright — not mitigates, eliminates. If no framing eliminates more than one
or two, you are likely reorganizing within the current representation rather
than changing it. Revisit the shared root cause from the grouping step and
challenge the data structure itself.

A subtler version of the same trap: a framing eliminates several leaks but the
survivors still trace to the root cause from Step 2's grouping. This means
you've improved the algorithm within the representation, not changed the
representation. Test: does the framing still require compensating for the
input's shape — dedup passes, ordering constraints, manual bookkeeping? If so,
revisit the reification axis and ask what the input data IS (serialization
format? index? projection?), not how to process it better.

**Never dismiss a framing because the fix feels awkward in the current code.**
That awkwardness is the mismatch this skill exists to find. If a framing aligns
with the domain but doesn't slot neatly into the current implementation, the
implementation has a gap — that's confirming evidence, not a reason to stop
looking.

Not every review will have a paradigm-level insight. If the current approach
already maps well to the domain, state that briefly and conclude.

## Report Structure

**When Step 3 finds a better framing:**

1. **Domain model and root cause** — Steps 1-2 condensed as motivation. Name the
   domain concepts, identify the leaks, state the shared root cause. Just enough
   to make the framing recommendation legible.

2. **Recommended framing** — The framing from the converge phase that best closes
   the gap between code structure and domain structure. Sketch what the code
   looks like. For each change, include what's hard to read, *why* (rooted in a
   specific step), and a concrete suggestion with code.

3. **Alternative framings** (optional) — Curated for *divergence*, not coverage.
   Each alternative earns its spot by offering something the winner can't, tagged
   with the reason it's interesting:
   - *(incremental path)* — a stepping stone that's an easier sell or smaller PR,
     potentially the first commit toward the recommended framing
   - *(different paradigm)* — approaches the problem from a fundamentally
     different angle that could shift how someone thinks about it
   - *(comparable fit, different route)* — nearly as readable as the winner but
     via a very different decomposition, revealing something about the problem's
     structure

   Alternatives are sketches — enough to see the shape and understand why
   they're interesting, not enough to implement from. Omit mild improvements on
   the current approach and slight variations on the winner. Most reviews have
   zero to two alternatives worth surfacing.

4. **Summary table** — finding / impact level / effort.

**When the current approach fits the domain:**

Note briefly that the current approach maps well to the domain, and conclude.

## Additional Resources

For worked examples showing the analysis process applied to real refactorings,
see [examples.md](examples.md).
