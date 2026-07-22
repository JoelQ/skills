---
name: hierarchical-documentation
description: Polish code documentation before a human reviews it. Use as a final
  pass on code changes before presenting output to a human. Also trigger when a
  user asks to "clean up naming", "polish documentation", "improve readability",
  "prepare for commit", or points at a commit/branch for review. Given a scope
  (commit hash, "uncommitted changes", "divergence from main", etc.), rewrites
  code in place to improve documentation quality across identifiers and comments,
  then surfaces raw material for the commit message.
---

# Hierarchical Documentation

You are doing a final documentation pass on code changes before a human sees them.
The code's structure is assumed to be sound — your job is naming, comments, and
surfacing the right information at the right level. The goal: a reader should be
able to scan and understand the code with minimal mental effort.

## The documentation hierarchy

Information should live at the highest level that can hold it well. From most to
least accessible:

- **Identifiers** — variable names, method names, constants. Always visible,
  searchable, impossible to separate from what they describe. Always try here first.
- **Comments** — flexible but fragile. They can drift from the code they describe
  when code moves. Use when code alone can't carry the information.
- **Commit messages** — capture the *why of the change*, not the *why of the code*.
  Accessible only to those reading history; never assume a code reader will find them.

A good name often makes a comment unnecessary. A well-named thing with a good comment
often makes a commit message note unnecessary. Work top-down: encode as much as you
can at the highest level, and let the next level catch the overflow — the information
that genuinely couldn't fit above.

## Step 1: Determine scope

Translate the user's input into a concrete set of changed files:

- "uncommitted changes" → `git diff HEAD` and `git status` for untracked files
- "most recent commit" or a commit hash → `git show <hash> --stat` then read the files
- "divergence from main" / "this branch" → `git diff main...HEAD --name-only`
- A specific file path → just that file

Read the diff to understand what changed, then read the full content of each changed file.

## Step 2: Apply documentation improvements

Before diving in, identify the domain concepts the code operates on — key nouns
(entities, states, relationships) and verbs (operations, transitions). Think
about what a domain expert would call these things rather than deriving
vocabulary from the code's existing names. This is a 2-3 sentence mental model,
not a full domain analysis — just enough to ground naming decisions in the
domain rather than anchoring on implementation vocabulary that may already be
wrong.

Then work through the changed code applying the hierarchy. When you find an
issue, ask whether the fix belongs at a higher level before reaching for a
lower one.

### Identifiers (highest priority)

**Intention-revealing names.** If you erased the value and kept only the name,
would a reader still understand the purpose?

**Single level of abstraction (SLAP).** Extract low-level pieces into private
methods with descriptive names. This is introducing a missing identifier, not
restructuring — the concept already exists as an anonymous block of code;
you're giving it a name. This applies within a file or class.

**Extract inline boolean expressions** into named local variables or private
methods. Private methods are for clarity, not just reuse — a single caller is
reason enough.

**Express actual intent, not proxy conditions (Tell Don't Ask).**
`if !contractor.verification_code` tests an implementation detail;
`if contractor.pending_verification?` says what you mean. If the predicate
is general-purpose, note it for the relevant object in commit message notes
rather than making cross-object changes here.

**Context-specific names at callsites (DDD-light / ubiquitous language).**
`accessible_descendants` is more meaningful than `descendants` when you're in
a permissions context.

**Replace magic values with named constants.**

**Sniff test for implementation names.** Does this name describe how the data is
stored or processed, or what it represents in the business domain? Names that
describe storage/processing mechanics (e.g., `path_rows`, `link_pairs`) are
implementation names. Names that describe meaning (e.g., `contractor_paths`,
`subcontractor_relationships`) are domain names. Prefer the latter.

For advanced naming techniques (altitude, contrast, crossings, vocabulary, and
structural cooperation), see [naming.md](naming.md).

### Comments (use when code can't carry the information)

**Add a comment when:**
- A reader might wonder *why* the code is written this way
- A decision was made to *not* do something obvious — the absence needs explaining
- Something surprising is happening that could cause a future reader to pause
- There's a footgun or dangerous assumption that can't be eliminated by restructuring

**Remove a comment when:**
- It restates what the code already says clearly
- A rename or extraction has made it redundant

**Check for overflow.** After naming is complete, re-read the changed code as if
encountering it for the first time. What questions would a future reader have that
the identifiers don't answer? Common overflow: why this approach instead of an
obvious alternative, performance constraints that shaped the design, or a mental
model needed to reason about the code. Be wary of evaluating from your own
perspective — you already know the context from the conversation. The test is what
someone reading this code cold would wonder about.

**Place comments as close as possible to the code they describe.** A comment that
applies to one branch of an `if` belongs inside that branch, not above the whole
statement. Reference specific identifiers in comments where possible — this makes
the relationship between comment and code explicit and harder to accidentally break.

### What not to touch

Stay out of these areas — not because they don't matter, but because they are
structural concerns beyond naming and comments:

- **Public method signatures or interfaces** — callers depend on these; changing
  them is a structural decision, not a documentation one
- **Conditional structure** — flattening nested conditionals or restructuring
  branches is a logic/readability concern beyond naming and comments
- **Cross-object logic** — moving logic to a different object changes responsibilities
  and belongs in a structural review
- **Code outside the diff scope** — this pass is about the change at hand;
  opportunistic cleanups elsewhere create noise and scope creep

If you notice issues in these areas, capture them in commit message notes.

## Step 3: Write the changes

Write the improved files directly. If the code is already well-documented and no
meaningful improvements are possible, say so briefly and move to Step 4.

Run any relevant tests afterward to confirm nothing broke.

## Step 4: Review and suggest commit messages

Read the full commit messages in scope (not just oneliners). Treat them the same
way you treat code — they exist, they may be of varying quality, and they're an
artifact to review. Apply the hierarchy here too: if a commit message explains something that the
code now carries through naming or comments (from Step 2), note that it can be
dropped. If it contains something that *should* be pushed up to code but wasn't
caught in Step 2, go back and do that. Conversely, if you added a comment during
Step 2 that doesn't hold its weight as code documentation but matters as context
for the change, move it here instead.

Output a section with this structure:

**Commit message notes**
- **Suggest additions:** insights about why something was done this way, alternatives
  considered, anything surprising or non-obvious in the diff, structural smells
  identified but out of scope. If you know from the current conversation that
  alternatives were considered or certain approaches were ruled out, include that
  context here even if it's not visible in the code.
- **Suggest removals:** interim fix-up commits ("fix ts errors", "address review
  feedback") that you assume will be squashed — note them so the author knows you
  expect these to be folded in.
- **Flag keepers:** things already in a commit message that are important to preserve
  through a squash. Call these out so they don't get lost.

This is raw material for whoever writes the commit message — not a draft, and not
a recap of documentation changes made. If there's nothing meaningful to surface,
omit this section rather than padding it.

## Core principle

**You are polishing, not restructuring.** If you find something structural,
capture it in commit message notes and move on.

## Further reading

- [Hierarchy of Documentation](https://challahscript.com/hiearchy_of_documentation) — the framework behind this skill: identifiers > comments > commit messages, and why information should live at the highest level that can hold it well.
