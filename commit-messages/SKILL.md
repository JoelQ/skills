---
name: commit-messages
description: >-
  Write git commit messages in a narrative, reasoning-focused style. Use when creating
  commits, drafting commit messages, or when the user asks for help writing
  a commit message.
---

# Commit Messages

Write commit messages that tell the story of *why* a change was made, not
just what changed. The reader should come away understanding the context,
the decision, and the trade-offs.

## Subject Line

Format: `[TICKET-123] Imperative verb phrase (#PR)` when a ticket exists,
or just `Imperative verb phrase` for small fixes/tooling.

- **Imperative mood**: "Add", "Fix", "Remove", "Prevent", "Handle" --
  never past tense.
- **No conventional-commits prefixes**: No `feat:`, `fix:`, `chore:`.
- **50 chars max** Drop words the context already implies --
  e.g. "Add NOT NULL on" beats "Add NOT NULL constraint on" because
  "NOT NULL" already means constraint.
- PR number in parens at the end if it's a squash merge.

Examples:
- `[PROJ-123] Show contact subscriptions in CSV`
- `Fix flaky cypress test`
- `Remove unused field from API payload (#123)`

## Body

Separate from subject with a blank line. Wrap at 72 characters. Use
backticks for code references (class names, method names, constants)
in the body.

### Narrative Arc

Follow this structure (skip sections that aren't relevant for small
changes):

1. **Context / current state**: What the world looks like before this
   change. Ground the reader.
2. **Problem or motivation**: What's wrong, missing, or desired. Name
   the specific concept or mechanism behind the problem rather than
   describing it loosely. "Not enforced at the DB level" is better
   than "the database didn't match" because it tells the reader
   exactly what kind of gap exists. Go further and name the
   real-world trigger -- the actors, behaviors, or patterns that made
   this change necessary *now*. "Customers hit this on every page
   reload" is stronger than "the cache can go stale" because it
   names who's affected and why it's urgent.
3. **Solution**: The approach or strategy, not a play-by-play of the
   diff. Describe the *shape* of the change rather than enumerating
   files or functions. Use "This commit..." to demarcate from
   background.
4. **Design reasoning**: Why this approach. State constraints or
   principles, discuss alternatives considered. Connect facts to the
   specific concerns they address -- "the table is small" is an
   assertion; "the table is small enough that the lock will be
   near-instant" is reasoning. The reader shouldn't have to infer
   why a fact matters.
5. **Scope boundaries**: What's explicitly *not* included. Use phrases
   like "out of scope for this change" or "a follow-up will..."
6. **Incidental discoveries**: Anything found along the way. "While
   digging into this, I discovered..."
7. **Future work**: What should happen next, if anything.
8. **Living with this change**: When a change introduces a new
   constraint, convention, or tool, include practical guidance for
   developers who'll encounter it. What should they do when it
   gets in their way? When is it appropriate to override or work
   around it? This is distinct from future work -- it's a playbook
   for coexisting with the change.

### Voice and Tone

- **First person**: "I chose to", "I considered", "My philosophy was".
  The author is present in the narrative.
- **Conversational but precise**: Reads like explaining the change to a
  colleague over coffee, not like formal documentation.
- **Length tracks reasoning, not diff size**: A complex redesign gets
  section headers, diagrams, and benchmarks. But a subtle one-line
  bug fix that took days to hunt down can also warrant a page-long
  explanation tracing the investigation. Write as much as the
  *reasoning* demands, regardless of how many lines changed.

### Enrichment (use when relevant)

- **Section headers**: For long messages, use markdown-style headers
  (`Performance`, `Security`, `Notable choices`, etc.) with underlines
  or blank-line separation.
- **Cross-references**: Cite commit SHAs, PR numbers, Sentry links, or
  documentation URLs. The reader should be able to trace anything.
  Only reference durable artifacts — planning documents, conversation
  context, and internal phase labels (e.g. "Phase 1") don't survive
  into git history.
- **Existing conventions**: When the change follows an existing
  codebase pattern, name it ("following the pattern used by similar
  validation rules"). This orients the reader without requiring
  them to read other files.
- **Principles/constraints**: Before describing a solution, state the
  constraints that guided it as a numbered list.
- **Alternatives considered**: "I considered X but it broke constraint
  Y. Eventually I settled on Z."
- **Code snippets / payload shapes**: Include when they clarify the
  change (JSON shapes, SQL, small code examples).
- **Mermaid diagrams**: For complex control flow, show before/after as
  flowcharts or state diagrams.
- **Performance data**: Include benchmarks or query plan comparisons
  when the change has performance implications.
- **Security implications**: Call out security improvements even when
  they're a side effect.
- **Deployment safety**: Note whether the change is safe to deploy at
  any time, requires ordering, or is behind a feature flag. "This
  change was written to be safe to deploy any time."
- **Verification**: Describe how you confirmed the change works. "I
  verified this by...", "I was able to reproduce the error using..."
- **ENV variables**: When introducing new environment variables, list
  them explicitly.
- **State combinatorics**: For UI work, document the space of possible
  states (e.g. with TypeScript ADTs or a count of combinations).

### Recurring Phrases and Conventions

These signal phrases appear naturally and serve specific roles:

- "This commit..." -- demarcates what the diff does vs. background.
- "Note that..." -- adds caveats the reader should be aware of.
- "While digging into this, I discovered..." -- incidental findings.
- "out of scope for this change" -- explicit scope boundary.
- "I've already spent my refactoring budget" -- scope discipline.
- "This is purely a refactor" or "pure refactor (ish)" -- declares no
  behavior change, sometimes with noted small exceptions.
- "A follow-up will..." -- promises future work without blocking now.
- "Longer-term, we probably want to..." -- non-blocking future vision.

## Examples

### Small fix

```
Fix ExampleService class typo

While browsing the code I discovered a typo in the ExampleService API. A
constant was written as `Inte::ExampleService` rather than
`Integrations::ExampleService`.
```

### Bug fix

```
[PROJ-456] Fix flaky contact search spec (#234)

The contact search spec can flake when generated names for the "match" and
"non-match" contacts happen to overlap. This hard-codes the names for this
specific test and removes generated names from the factory.
```

### Feature with design reasoning

```
[PROJ-123] Show contact subscriptions in CSV

Currently we don't show subscription data for archived contacts in the CSV
export because the association we use only returns active contacts. We want
to show all subscriptions associated with the contact that are accessible to
the user.

I wanted to maintain 3 principles:

1. Permission logic stays in the permission layer
2. No N+1: subscription data must be batch-loadable
3. Serializer is active/archived-contact agnostic

I considered a variety of solutions but they kept breaking one or more
of these constraints. Eventually I settled on a solution that worked
like this:

- DB view aggregates subscription IDs as an array on each
  record. This is structural, no permission logic applied.
- Permission layer filters by tenant ID.
- Manual pre-loading of subscription IDs avoids N+1
```

### Refactor with before/after

```
[PROJ-789] Refactor session service

In the spirit of "make the change easy, then make the easy change",
this commit re-structures the entire tree of services into a form that
better suits the changes we're about to make.

Pure refactor (ish)
-------------------

This is mostly a pure refactor, with a couple small exceptions...

[... sections with mermaid diagrams showing before/after flow ...]
```

### Incremental Rollout Pattern

For risky or large changes, commit messages document a deliberate
incremental strategy:

1. Add nullable column / feature-flagged code (safe to deploy anytime)
2. Backfill existing data or enable flag
3. Make column non-nullable / remove flag (only after step 2 is done)

Each commit explains where it sits in the sequence: "Now that we've
cleaned up the existing API keys, we can safely add the stricter
constraints everywhere."

### Incident Chain Narrative

When fixing bugs introduced by earlier commits, tell the chain story:

```
In abc12345..., we started moving away from archived records. Then we
tried to rein it back in with def67890..., but this is subject to
the default scope again. This commit adds thorough testing to ensure
we neither *over* select nor *under* select records to delete.
```

## Anti-Patterns

- "Updated files" or "Various fixes" -- say what actually changed.
- Starting the body with what the commit does rather than why.
- Passive voice ("it was decided") -- use "I chose" or "we decided".
- Explaining what the diff shows -- the reader can see the diff. Explain
  the *reasoning* behind it.
- Including coordination notes for the current team ("go talk to X
  about the credentials", "we need to follow up in Slack") -- commit
  messages are for future readers, not present-day task management.
- Adding `feat:` / `fix:` prefixes.

## Workflow

When asked to commit:

1. Read the diff carefully.
2. Identify the *story*: what was the state before, what changed, why.
3. Draft subject line in imperative mood with ticket if available.
4. Write body following the narrative arc.
5. Add enrichment (cross-refs, diagrams, benchmarks) where it helps.
6. Verify line wrapping at 72 characters.
