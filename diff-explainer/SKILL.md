---
name: diff-explainer
description: Generates an interactive HTML report explaining a git diff — commentary cards on the left, clickable diff lines on the right. Use this skill when the user wants to understand, walk through, annotate, or document a diff, commit, changeset, or PR. This is for explaining/teaching the changes, not for finding bugs. Trigger on phrases like "explain this diff", "walk me through this PR", "annotate these changes", "help me understand what changed", or "what's going on in this commit" — even when the user doesn't explicitly ask for an HTML report. Especially useful when onboarding to a new codebase or learning an unfamiliar framework.
---

# Diff Explainer

Produces a two-column HTML report: commentary on the left, the diff on the right, with clickable cards that highlight the relevant lines. Your job is the **judgment** — what's worth a card, how to phrase it, which lines it ties to. A bundled script handles all HTML assembly.

The report is **for a specific reader.** A pattern that's invisible to a Java dev is a Concept card for a Ruby dev. Calibrating to the reader (step 2) shapes everything that follows.

## Workflow

### 1. See the diff with line numbers

```bash
git diff | python3 scripts/build.py show
```

Use `--cached` for staged changes, `main..feature` for branch comparisons, etc. The output groups by file and assigns each line a `data-n` value — your commentary references these in its `lines` field.

For context, also look at any new untracked files relevant to the change and skim a few comparable existing files to learn project conventions.

### 2. Calibrate to the reader

Establish the reader's **positive background** — the languages/frameworks they're already comfortable with. Two things flow from this:

1. **What gets a card** (the main thing). A pattern invisible to one reader is a Concept card for another. Skip concepts the reader already has; explain the ones they don't.
2. **How cards frame** (secondary). When something needs explaining, anchor it in something familiar — "like a `Gemfile`", "this is .NET's answer to `useEffect`".

Negative-only signals ("newer to .NET") aren't enough on their own — .NET is huge, and a Java dev needs different cards than a Ruby dev, even if both are new to it.

Where positive background can come from:
- A user memory naming it ("comfortable with Ruby/Elm/TypeScript, learning .NET")
- A direct statement this session
- Asking the user

Don't infer it from the project's stack, the diff's language, CLAUDE.md, or recent activity — the user might be reading this repo *because* they don't know it.

If you don't have positive background, ask: *"What languages/frameworks are you comfortable with, and which are you newer to? I'll tune the commentary."* Save the answer to user memory so future invocations don't re-ask.

### 3. Check the diff size

```bash
git diff --shortstat
```

If additions + removals exceed ~1500 lines, ask the user to scope down before writing commentary — a report that big is expensive to generate and too dense to read. Suggest focusing on specific files or themes; the rest can render as panels with no commentary.

### 4. Write `commentary.json`

Save to `commentary.json` in the current directory. Schema:

```json
{
  "title": "feature/PR title",
  "summary_what": "one-sentence description of what the change does",
  "summary_why": "one-sentence description of why",
  "files": [
    {
      "path": "src/Auth.cs",
      "tag": "new",
      "cards": [
        {
          "type": "concept",
          "title": "Dependency injection",
          "body": "Like Ruby's initializer, but the container instantiates this. Registered in <code>Module.cs</code>.",
          "lines": "1-5"
        }
      ]
    }
  ]
}
```

**Field reference:**

| Field | Values | Notes |
|-------|--------|-------|
| `tag` | `new` (green), `mod` (yellow), `infra` (purple), `deleted` (red), `renamed` (blue), `binary` (grey) | `infra` overrides for Terraform, Helm, `.csproj`, Autofac modules, etc. Omit a file and the script infers the tag from the diff. |
| `type` | `observation` (blue), `concept` (purple), `warn` (yellow), `surprise` (red) | Controls colour and the default label prefix (`Observation`, `Concept`, `Potential Issue`, `Surprise`) |
| `title` | short topic name | Appears after the colon in the card header |
| `label` | optional | Overrides the default prefix (e.g. `"Warning"`) |
| `body` | plain text or HTML | Plain text gets wrapped in `<p>`; for lists/code use inline HTML (`<ul>`, `<code>`) |
| `lines` | `"3"` or `"3,7-12"` | Comma-separated `data-n` values; range syntax with `-` |

Skip files you have nothing useful to say about — they'll still render with no commentary.

### 5. Build the report

```bash
git diff | python3 scripts/build.py render commentary.json
```

The script writes a timestamped HTML file (e.g. `diff-report-2026-05-26-143052.html`), prints the path, and deletes `commentary.json`. Pass `-o <path>` to override.

Open it and share with the user:

```bash
open diff-report-<timestamp>.html
```

Offer to adjust depth, add more files, or refocus on specific parts.

---

## What makes good commentary

- **Prioritise the non-obvious.** Skip boilerplate. If a line is self-explanatory, don't card it.
- **Connect to the system.** Note when something follows or deviates from a convention elsewhere in the repo.
- **Use analogies.** Map unfamiliar patterns to something the reader already knows.
- **Flag real risks only.** Don't add noise.
- **Cover all layers.** Infrastructure (Terraform, Helm), config (.csproj, Autofac), and plumbing files often need the most explanation.

## A good card vs a bad card

**The test:** if your card disappeared, would the reader miss any information that isn't already in the diff? If no, don't write it.

(Examples below assume the reader is a JS/TS dev newer to Rails — adjust the cut for *your* reader.)

### Example 1 — framework idiom that a newcomer wouldn't catch

**Bad** (restates what the diff shows):

> **Observation: Adds an active scope**
>
> Defines a new scope on the `User` model that filters by `archived_at: nil`.

**Good** (teaches the idiom):

> **Concept: ActiveRecord scopes**
>
> A `scope` is Rails-speak for a named, chainable filter on a model. Calling `User.active` returns a query equivalent to `User.where(archived_at: nil)` — and because it's a relation, you can keep chaining: `User.active.where(role: :admin)`. Think of it as a method-named query you can compose. You'll see scopes everywhere in this codebase.

The bad card just narrates the diff. The good card teaches the Rails-specific concept that a JS dev wouldn't pattern-match on, and points to the broader role of scopes in the codebase. *That* is the skill's job.

### Example 2 — project convention that deviates from the framework default

**Bad** (notes the change but leaves the reader unsure if it's right):

> **Observation: Uses a form object**
>
> The controller calls `UserForm.new(params).save` instead of `User.create(params)`.

**Good** (grounds the convention so the reader can follow it):

> **Concept: Form objects — this project's convention, not Rails default**
>
> A typical Rails controller would write `User.create(user_params)` here. This codebase wraps that in a Form Object (`UserForm` in `app/forms/user_form.rb`), which combines validation, persistence, and after-save side-effects in one class. The closest JS analogy is a *service class* or *use-case object* — a wrapper that bundles validation, DB writes, and side-effects in one place instead of scattering them across the route handler. It's not a bug or a code smell — it's the project's chosen pattern, and you'll see it everywhere records are created. Follow the existing shape when adding new controllers: `Form.new(params).save` returns true/false like an ActiveRecord save would.

The bad card flags the existence of `UserForm` without explaining anything. The good card tells the newcomer: (1) this isn't what Rails normally does, (2) it's a deliberate project choice and you'll see it everywhere, (3) here's the shape to follow. That's how onboarding diffs earn their keep.
