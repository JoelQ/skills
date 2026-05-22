---
name: diff-explainer
description: Generates a rich HTML diff explanation report for a git diff. Use this skill when the user asks to explain, annotate, or document a code diff, changeset, or PR — especially when onboarding to a new codebase or learning unfamiliar frameworks. Trigger for phrases like "explain this diff", "help me understand these changes", "generate a diff report", "annotate the PR", or "walk me through what changed". Particularly suited for .NET/C# codebases but works for any language.
---

# Diff Explainer

Produces a two-column HTML report explaining a git diff: commentary on the left, the diff on the right, with clickable cards that highlight the relevant lines.

## Audience

Tailor commentary depth to the user's background. This project's user has Ruby/Elm/TypeScript/FP experience but is learning .NET — explain .NET-specific patterns by analogy (e.g. "like Ruby's initializer", "like p-limit in Node") rather than assuming .NET familiarity. If you don't know the user's background, default to explaining framework-specific idioms.

## Workflow

### 1. Gather the diff

Run `git diff` (and `git diff --cached` for staged changes). Also read any new untracked files relevant to the change — they're often part of the same feature.

```bash
git diff
git diff --cached
```

For context, look at a few comparable existing files to understand project conventions (e.g. a sibling job class, a comparable config file).

### 2. Group changes into files

Organise the report by file. Each file gets one **row**: commentary on the left, diff on the right.

### 3. Write commentary

For each file, write 1–4 commentary cards. Each card should be one of:

- **Concept** (purple) — explains a pattern, idiom, or framework feature the reader may not know
- **Observation** (blue) — notes something worth knowing: a convention, a structural choice, how this connects to other parts of the system
- **Potential Issue** / **Warning** (yellow) — something that could be a problem (not a blocker, but worth flagging)
- **Surprise** (red) — something inconsistent, unexpected, or non-obvious compared to the rest of the codebase

Good cards explain the *why*, not just the *what*. Use analogies for unfamiliar patterns. Point out when something follows a convention elsewhere in the repo versus deviating from it.

Each card has a `data-lines` attribute (comma-separated line numbers or ranges like `"3,7-12"`) that links it to specific lines in the diff panel.

### 4. Number diff lines

Every `<span>` in the diff gets a `data-n` attribute (1-based, restarting per file). This is what the click-to-highlight interaction depends on.

### 5. Output the HTML file

Read `assets/template.html` and substitute these four placeholders:

| Placeholder | Replace with |
|-------------|---------------|
| `{{TITLE}}` | The feature/PR title (appears in `<title>` and `<h1>`) |
| `{{SUMMARY_WHAT}}` | One-sentence description of what the change does |
| `{{SUMMARY_WHY}}` | One-sentence description of why the change is being made |
| `{{ROWS}}` | The concatenated `<div class="row">…</div>` blocks, one per file |

Write the result to `diff-report.html` in the current working directory (or wherever the user specifies). The CSS and JavaScript in the template are load-bearing — leave them untouched.

---

## Row shape

Each file produces one `<div class="row">` block. Use this structure:

```html
<div class="row">
  <div class="commentary">
    <h2>N. Filename.cs <span class="tag tag-new">new</span></h2>

    <div class="note concept" data-lines="1-5">
      <div class="note-label">Concept: Title</div>
      <p>...</p>
    </div>

    <div class="note warn" data-lines="12-15">
      <div class="note-label">Potential Issue: Title</div>
      <p>...</p>
    </div>
  </div>

  <div class="diff-panel">
    <div class="diff-file-header">path/to/File.cs</div>
    <div class="diff-content"><pre>
<span class="diff-line diff-add" data-n="1">+first added line</span>
<span class="diff-line diff-context" data-n="2"> context line</span>
<span class="diff-line diff-remove" data-n="3">-removed line</span>
<span class="diff-line diff-hunk" data-n="4">@@ hunk header @@</span>
</pre></div>
  </div>
</div>
```

The `data-lines` attribute on each `.note` links it to the `data-n` values in the diff panel — that's the click-to-highlight mechanism.

---

## Diff line rendering rules

| Line type | CSS class | Prefix |
|-----------|-----------|--------|
| Added | `diff-add` | `+` |
| Removed | `diff-remove` | `-` |
| Context | `diff-context` | ` ` |
| Hunk header (`@@`) | `diff-hunk` | none |

Line numbers (`data-n`) restart at 1 for each file's `<pre>` block.

Tags on the file header: `tag-new` (new file), `tag-mod` (modified), `tag-infra` (infra/config).

---

## What makes good commentary

- **Prioritise the non-obvious.** Skip boilerplate. If a line is self-explanatory, don't write a card for it.
- **Connect to the rest of the system.** Note when something follows a convention from elsewhere in the repo, or deviates from it.
- **Use analogies.** For unfamiliar patterns, map them to something the reader already knows.
- **Flag real risks, not imaginary ones.** Only raise issues where there's a genuine concern — don't add noise.
- **Cover all layers.** Don't just explain the application code — infrastructure (Terraform, Helm), config (.csproj, Autofac), and plumbing files often need the most explanation.

---

## After writing the file

Open it in the browser:

```bash
open diff-report.html
```

Tell the user where the file is and offer to adjust the commentary depth, add more files, or re-focus on specific parts of the diff.
