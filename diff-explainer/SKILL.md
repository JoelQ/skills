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

Write to `diff-report.html` in the current working directory (or wherever the user specifies).

---

## HTML Template

Use this exact structure. The JavaScript and CSS are load-bearing — don't simplify them.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Diff Report</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace; background: #0d1117; color: #c9d1d9; line-height: 1.6; padding: 24px; }
  h1 { color: #58a6ff; font-size: 1.4em; margin-bottom: 8px; }
  h2 { color: #79c0ff; font-size: 1.1em; margin: 0 0 12px; }
  .summary { background: #1c2128; border: 1px solid #30363d; border-radius: 6px; padding: 16px; margin-bottom: 32px; max-width: 900px; }
  .summary p { margin-bottom: 8px; }
  .row { display: flex; align-items: stretch; margin-bottom: 48px; border-bottom: 1px solid #30363d; padding-bottom: 48px; }
  .row:last-child { border-bottom: none; }
  .commentary { width: 38%; padding-right: 24px; flex-shrink: 0; }
  .diff-panel { width: 62%; min-width: 0; }
  .note { background: #1c2128; border-left: 3px solid #58a6ff; padding: 12px 16px; margin: 12px 0; border-radius: 0 6px 6px 0; font-size: 0.9em; cursor: pointer; transition: background 0.15s, border-left-color 0.15s; }
  .note:hover { background: #22272e; }
  .note.active { background: #1f3a5f; border-left-color: #79c0ff; }
  .note.warn { border-left-color: #d29922; }
  .note.warn.active { background: #3d2e00; border-left-color: #e3b341; }
  .note.surprise { border-left-color: #f85149; }
  .note.surprise.active { background: #4a1c1c; border-left-color: #ff7b72; }
  .note.concept { border-left-color: #a371f7; }
  .note.concept.active { background: #2d1f4e; border-left-color: #bc8cff; }
  .note-label { font-weight: bold; font-size: 0.8em; text-transform: uppercase; margin-bottom: 4px; }
  .note.warn .note-label { color: #d29922; }
  .note.surprise .note-label { color: #f85149; }
  .note.concept .note-label { color: #a371f7; }
  .note p, .note ul { margin-top: 4px; }
  .note ul { padding-left: 18px; }
  .note li { margin-bottom: 4px; }
  code { background: #282c34; padding: 2px 6px; border-radius: 3px; font-size: 0.88em; color: #e6edf3; }
  .diff-file-header { background: #1c2128; border: 1px solid #30363d; border-radius: 6px 6px 0 0; padding: 10px 16px; font-weight: bold; color: #58a6ff; font-size: 0.9em; }
  .diff-content { border: 1px solid #30363d; border-top: none; border-radius: 0 0 6px 6px; overflow-x: auto; }
  .diff-content pre { padding: 0; font-size: 0.82em; white-space: pre; display: flex; flex-direction: column; }
  .diff-line { display: block; padding: 1px 16px; line-height: 1.5; transition: background 0.2s, outline 0.2s; }
  .diff-line.diff-add { background: #12261e; color: #7ee787; }
  .diff-line.diff-remove { background: #2d1215; color: #ffa198; }
  .diff-line.diff-context { color: #8b949e; }
  .diff-line.diff-hunk { color: #79c0ff; font-style: italic; }
  .diff-line.highlighted { outline: 1px solid #58a6ff; background: #1f3a5f !important; color: #e6edf3 !important; }
  .diff-line.highlighted.diff-add { background: #1a4a2e !important; color: #aff5b4 !important; outline-color: #7ee787; }
  .diff-line.highlighted.diff-remove { background: #5a2020 !important; color: #ffc1ba !important; outline-color: #ffa198; }
  .tag { display: inline-block; font-size: 0.7em; padding: 2px 6px; border-radius: 3px; margin-left: 8px; vertical-align: middle; }
  .tag-new { background: #12261e; color: #7ee787; border: 1px solid #238636; }
  .tag-mod { background: #1c2128; color: #d29922; border: 1px solid #d29922; }
  .tag-infra { background: #1c2128; color: #a371f7; border: 1px solid #a371f7; }
  @media (max-width: 1100px) {
    .row { flex-direction: column; }
    .commentary, .diff-panel { width: 100%; padding-right: 0; }
    .commentary { margin-bottom: 16px; }
  }
</style>
</head>
<body>

<h1><!-- feature/PR title --></h1>
<div class="summary">
  <p><strong>What this does:</strong> ...</p>
  <p><strong>Why:</strong> ...</p>
  <p style="margin-top:12px; font-size:0.85em; color:#8b949e;"><em>Click any commentary card to highlight the relevant lines in the diff.</em></p>
</div>

<!-- For each file, one .row: -->
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

<script>
document.addEventListener('DOMContentLoaded', function() {
  var activeNote = null;

  document.querySelectorAll('.note[data-lines]').forEach(function(note) {
    note.addEventListener('click', function(e) {
      e.stopPropagation();
      var row = note.closest('.row');
      var diffPanel = row.querySelector('.diff-panel');

      diffPanel.querySelectorAll('.diff-line.highlighted').forEach(function(el) {
        el.classList.remove('highlighted');
      });

      if (activeNote === note) {
        note.classList.remove('active');
        activeNote = null;
        return;
      }

      if (activeNote) activeNote.classList.remove('active');
      note.classList.add('active');
      activeNote = note;

      var lineNums = new Set();
      note.getAttribute('data-lines').split(',').forEach(function(part) {
        part = part.trim();
        if (part.indexOf('-') !== -1) {
          var bounds = part.split('-');
          for (var i = parseInt(bounds[0]); i <= parseInt(bounds[1]); i++) lineNums.add(i);
        } else {
          lineNums.add(parseInt(part));
        }
      });

      var first = null;
      diffPanel.querySelectorAll('.diff-line').forEach(function(line) {
        if (lineNums.has(parseInt(line.getAttribute('data-n')))) {
          line.classList.add('highlighted');
          if (!first) first = line;
        }
      });

      if (first) first.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });
  });

  document.addEventListener('click', function() {
    if (activeNote) {
      var row = activeNote.closest('.row');
      row.querySelector('.diff-panel').querySelectorAll('.diff-line.highlighted').forEach(function(el) {
        el.classList.remove('highlighted');
      });
      activeNote.classList.remove('active');
      activeNote = null;
    }
  });
});
</script>

</body>
</html>
```

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
