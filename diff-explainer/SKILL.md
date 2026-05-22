---
name: diff-explainer
description: Generates an interactive HTML report explaining a git diff — commentary cards on the left, clickable diff lines on the right. Use this skill when the user wants to understand, walk through, annotate, or document a diff, commit, changeset, or PR. This is for explaining/teaching the changes, not for finding bugs. Trigger on phrases like "explain this diff", "walk me through this PR", "annotate these changes", "help me understand what changed", or "what's going on in this commit" — even when the user doesn't explicitly ask for an HTML report. Especially useful when onboarding to a new codebase or learning an unfamiliar framework.
---

# Diff Explainer

Produces a two-column HTML report explaining a git diff: commentary on the left, the diff on the right, with clickable cards that highlight the relevant lines.

**This is not a generic diff explanation — it's an explanation of *this diff* for *this reader.*** The reader's background determines what's worth a card (dependency injection is noise to a Java dev, a key concept to a Ruby dev) and how each card frames things (e.g. "like a `Gemfile`", "like Ruby's `initializer`"). Calibrating to the reader is step 2 of the workflow and shapes everything that follows — skip it and the report becomes either condescending or impenetrable.

Your job is the **judgment** part — what's worth a card, how to phrase it, which lines it ties to. A bundled script handles all HTML assembly (escaping, classes, tags, file headers, line numbering, template substitution). You never write HTML for the report itself.

## Workflow

### 1. See the diff with line numbers

```bash
git diff | python3 scripts/build.py show
```

Use `--cached` for staged changes, `main..feature` for branch comparisons, etc. The output groups the diff by file and assigns each line a `data-n` value — your commentary will reference these in its `lines` field.

For context, also look at any new untracked files relevant to the change and skim a few comparable existing files to learn project conventions.

### 2. Calibrate to the reader

Before writing any commentary, establish what the reader knows. Their background is the lens for the whole report — two effects, in order of importance:

1. **What gets a card (the main thing).** A pattern that's invisible to one reader is a Concept card for another. Don't card things the reader already knows; do card things they don't. This is *the* reason calibration matters — picking which concepts deserve explanation is most of the work.
2. **How cards frame (the cherry on top).** When a card does need to explain something, anchor it in something familiar — "like a `Gemfile`", "this is .NET's answer to `useEffect`". Nice when available, but secondary to picking the right concepts to explain at all.

**You must know what the user *does* know — not just what they don't — before writing any commentary.** Positive background (the languages/frameworks they're comfortable with) is what tells you which concepts to skip (the reader already has them) and which to expand on (they don't). Negative-only background ("newer to .NET") doesn't pin this down — .NET is huge, and what needs explaining depends on what the reader brings with them. A Java dev needs different cards than a Ruby dev, even if both are "new to .NET".

What counts as knowing it:

- A user memory that names positive background (e.g. "comfortable with Ruby/Elm/TypeScript, learning .NET")
- A direct statement the user has made this session about what they know
- An answer from asking them — including a follow-up if the first answer is negative-only (e.g. "coming from another stack" → ask "which stack?")

What does **not** count:

- Inferring from the project's stack, the diff's language, the user's recent activity, the contents of CLAUDE.md, or any other property of the environment. *"This is a Rails project, so the user must know Rails"* is the exact rationalization to avoid — the user might be reading this repo precisely because they *don't* know it. The environment is the same regardless of what the human in front of you knows.
- Negative-only signals on their own ("they're newer to .NET") — you need positive grounding too

Absence of positive background is not permission to proceed — it is the trigger to ask. If none of the qualifying sources has the answer, ask: *"What languages/frameworks are you comfortable with, and which are you newer to? I'll tune the commentary accordingly."* Save the answer as a user memory so future invocations don't re-ask.

### 3. Write `commentary.json`

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
| `tag` | `new`, `mod`, `infra` | `infra` for Terraform, Helm, `.csproj`, Autofac modules, etc. — regardless of new vs modified |
| `type` | `observation`, `concept`, `warn`, `surprise` | Controls the card colour and default label prefix |
| `title` | short topic name | Appears after the colon in the card header |
| `label` | optional | Overrides the default prefix (e.g. `"Warning"` instead of `"Potential Issue"`) |
| `body` | plain text or HTML | Plain text gets wrapped in `<p>` automatically; for lists/code use inline HTML (`<ul>`, `<code>`) |
| `lines` | `"3"` or `"3,7-12"` | Comma-separated `data-n` values; range syntax with `-` |

Skip files you have nothing useful to say about — they'll still render in the report with no commentary.

### 4. Build the report

```bash
git diff | python3 scripts/build.py render commentary.json -o diff-report.html
open diff-report.html
```

Tell the user where the file is and offer to adjust commentary depth, add more files, or re-focus on specific parts.

---

## What makes good commentary

- **Prioritise the non-obvious.** Skip boilerplate. If a line is self-explanatory, don't write a card for it.
- **Connect to the rest of the system.** Note when something follows a convention from elsewhere in the repo, or deviates from it.
- **Use analogies.** For unfamiliar patterns, map them to something the reader already knows.
- **Flag real risks, not imaginary ones.** Only raise issues where there's a genuine concern — don't add noise.
- **Cover all layers.** Don't just explain the application code — infrastructure (Terraform, Helm), config (.csproj, Autofac), and plumbing files often need the most explanation.

## Card types — when to use which

- **observation** (blue, default) — neutral notes: a convention, a structural choice, how this connects elsewhere
- **concept** (purple) — explains a pattern, idiom, or framework feature the reader may not know
- **warn** (yellow) — a potential issue worth flagging; not a blocker
- **surprise** (red) — something inconsistent, unexpected, or non-obvious compared to the rest of the codebase
