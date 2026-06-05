---
name: Diff Explainer
description: A calm, paper-like report that reads a git diff like a code reader's gloss — compact teaching entries beside mono source, line-range citations at rest, and on-demand highlights tying each gloss to its passage.
colors:
  paper: "oklch(98.2% 0.008 86)"
  paper-raised: "oklch(96.6% 0.008 86)"
  code-surface: "oklch(97.5% 0.005 92)"
  hairline: "oklch(82% 0.009 86)"
  hairline-strong: "oklch(66% 0.012 86)"
  ink: "oklch(19% 0.016 255)"
  ink-secondary: "oklch(34% 0.016 255)"
  muted: "oklch(46% 0.012 255)"
  accent-teal: "oklch(56% 0.11 215)"
  accent-ink: "oklch(40% 0.10 218)"
  accent-tint: "oklch(94.5% 0.035 215)"
  observation: "oklch(48% 0.13 250)"
  concept: "oklch(46% 0.16 300)"
  warn: "oklch(48% 0.10 70)"
  surprise: "oklch(50% 0.18 25)"
  add-bg: "oklch(95% 0.05 150)"
  add-bg-strong: "oklch(92.5% 0.075 150)"
  remove-bg: "oklch(95.5% 0.05 25)"
  remove-bg-strong: "oklch(93% 0.075 25)"
  hunk-bg: "oklch(96.5% 0.02 215)"
  tag-new-ink: "oklch(42% 0.12 150)"
  tag-mod-ink: "oklch(48% 0.10 75)"
  tag-infra-ink: "oklch(45% 0.15 300)"
  tag-deleted-ink: "oklch(47% 0.17 25)"
  tag-renamed-ink: "oklch(44% 0.13 250)"
  tag-binary-ink: "oklch(46% 0.01 250)"
typography:
  display:
    fontFamily: "'Iowan Old Style', 'Charter', 'Palatino Linotype', Palatino, Georgia, Cambria, 'Times New Roman', serif"
    fontSize: "clamp(1.9rem, 1.25rem + 1.45vw, 2.75rem)"
    fontWeight: 700
    lineHeight: 1.06
    letterSpacing: "-0.012em"
  headline:
    fontFamily: "'Charter', 'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, Cambria, 'Times New Roman', serif"
    fontSize: "1.2rem"
    fontWeight: 700
    lineHeight: 1.24
    letterSpacing: "normal"
  body:
    fontFamily: "'Charter', 'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, Cambria, 'Times New Roman', serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.52
    letterSpacing: "normal"
  gloss:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 400
    lineHeight: 1.46
    letterSpacing: "normal"
  code:
    fontFamily: "ui-monospace, 'SF Mono', 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, 'Liberation Mono', monospace"
    fontSize: "0.8rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  label:
    fontFamily: "ui-monospace, 'SF Mono', 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, 'Liberation Mono', monospace"
    fontSize: "0.66rem"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.02em"
rounded:
  sm: "4px"
  tag: "5px"
  md: "8px"
  card: "9px"
  lg: "10px"
spacing:
  xs: "4px"
  sm: "6px"
  md: "12px"
  lg: "18px"
  xl: "28px"
components:
  note:
    backgroundColor: "{colors.paper-raised}"
    textColor: "{colors.ink}"
    typography: "{typography.gloss}"
    rounded: "0 at rest, {rounded.md} when active"
    padding: "12px 12px 18px 42px"
  note-active:
    backgroundColor: "color-mix(in oklch, {colors.accent-tint} 54%, {colors.paper})"
    textColor: "{colors.ink}"
    typography: "{typography.gloss}"
    rounded: "{rounded.md}"
    padding: "12px 12px 18px 42px"
  tag-new:
    backgroundColor: "{colors.add-bg}"
    textColor: "{colors.tag-new-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.tag}"
    padding: "2px 7px"
  summary:
    backgroundColor: "color-mix(in oklch, {colors.paper-raised} 38%, {colors.paper})"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "0"
    padding: "12px 18px"
  diff-content:
    backgroundColor: "{colors.code-surface}"
    textColor: "{colors.ink-secondary}"
    typography: "{typography.code}"
    rounded: "0"
    padding: "0"
---

# Design System: Diff Explainer

## 1. Overview

**Creative North Star: "Code Reader's Gloss"**

The report reads like a compact reader's gloss for unfamiliar source: code is the primary evidence,
and the left column names the concepts, conventions, costs, and contextual cues a specific reader
may not recognize yet. The layout gives that gloss lane real width, roughly a third of the row on
desktop, so prose is a co-equal explanation rather than a squeezed margin note. Each gloss leads with
the term or convention, then carries quiet metadata (`Concept · L5–7`) as a citation back to the diff.
Selecting the gloss reveals those exact lines in the body with an accent highlight. The reader is
usually landing in an unfamiliar codebase, so the surface has one job before any other: make the
non-obvious parts legible without asking them to read an essay. The gloss→line link is the whole
interaction, and it is reinforced on demand, one gloss at a time, so the diff stays clean at rest
rather than carrying a permanent layer of connector marks.

This is a **light, paper-like** surface, not a dark IDE and not a blog layout. It borrows only the
vibe primitives of a confident technical essay: high-contrast ink, a forceful serif title, decisive
rules, and tactile code passages. The source passage gets the boldest single gesture: an ink-black
caption plate that frames the code as evidence without turning the whole page dark. The body is a
barely-warm paper (`oklch(98.2% 0.008 86)`), chosen to feel printed without turning into cream/sand.
Color is **restrained and strictly semantic**. Type does the heavy lifting: an editorial **serif for
prose** against a **mono for code** gives an instant, effortless read of "this is explanation" vs.
"this is the change," with no decorative chrome. Saturated color appears only where it carries
meaning: a diff add/remove tint, a gloss kind dot + label, a file tag, or the single calm teal that
marks the active gloss and its lines.

This system explicitly rejects: **GitHub/GitLab/Bitbucket diff chrome** (the report must not look
like the platform diff view the reader already knows, no `#0d1117` dark clone); **generic AI/SaaS
styling** (no purple gradients, glassmorphism, hero-metric cards, or tiny tracked uppercase
eyebrows); **noisy IDE chrome** (no gutters of line numbers, minimaps, toolbars, or panel stacks,
this is for reading, not editing); and **cold, corporate, compliance-PDF blandness** (it must read
as deliberately made and human).

**Key Characteristics:**
- Light paper reading surface with confident dark ink, never a dark IDE.
- Restrained palette: color is reserved for functional meaning, never decoration.
- One bold source plate per diff panel; the page stays light, but source regions have presence.
- Serif prose beside mono code, type rather than chrome carries the hierarchy.
- Two-column gloss-and-source layout; the gloss→line link is citation-based at rest and reinforced on demand by highlight.
- Color-blind safe by construction: every encoding pairs hue with a label, glyph, or position.

## 2. Colors

A cool near-neutral paper surface with ink text, plus a disciplined set of functional semantic hues that appear only where they mean something.

### Primary
- **Accent Teal** (`oklch(56% 0.11 215)`): the single calm, saturated accent. Marks the active commentary note's border, numeral, and citation chip, the highlighted diff lines' inset bar and horizontal rule markers, and the focus ring. Deliberately distinct from every semantic hue (diff green/red, the four card types, the six tags) so "active" never collides with "meaning." Used on <=10% of the surface at any moment.
- **Accent Ink** (`oklch(40% 0.10 218)`): the darker teal for text-weight accent, used on hunk-header text in the diff and on the active note's range chip, where the lighter accent would be too faint to read.
- **Accent Tint** (`oklch(94.5% 0.035 215)`): the pale teal wash behind an active note and its highlighted diff lines. The note wash is strong enough to read as selected, while the diff line carries the stronger selection cue through tint, line rules, and position.

### Secondary — Gloss Kinds
Each gloss kind is a distinct hue **and** a written label (see The No-Hue-Only Rule). Used on the `note-kind` text plus a small dot marker, never as a background stripe.
- **Context** (`oklch(48% 0.13 250)`): the default gloss, for local codebase context or ordinary observations.
- **Concept** (`oklch(46% 0.16 300)`): a teaching gloss that names a language or framework pattern.
- **Watch** (`oklch(48% 0.10 70)`): a caveat, cost, or behavior to keep in mind, not a code-review finding.
- **Notable** (`oklch(50% 0.18 25)`): something unexpected or worth special attention in the change.

### Tertiary — File Tags & Diff Tints
File tags carry both a hue and the tag word; diff lines carry both a tint and a `+`/`−` glyph.
- **Tag inks** — new `oklch(42% 0.12 150)`, mod `oklch(48% 0.10 75)`, infra `oklch(45% 0.15 300)`, deleted `oklch(47% 0.17 25)`, renamed `oklch(44% 0.13 250)`, binary `oklch(46% 0.01 250)`: each on a faint same-hue background, bordered in `currentColor`.
- **Diff Add** (`oklch(95% 0.05 150)`, highlighted `oklch(92.5% 0.075 150)`): green tint behind added lines, with ink text riding on top for legibility.
- **Diff Remove** (`oklch(95.5% 0.05 25)`, highlighted `oklch(93% 0.075 25)`): red tint behind removed lines.
- **Hunk** (`oklch(96.5% 0.02 215)`): the faint cool band behind a `@@` hunk header, with accent-ink italic text.

### Neutral
- **Paper** (`oklch(98.2% 0.008 86)`): the body background. Barely warm, close to printed paper, but still light and quiet.
- **Paper Raised** (`oklch(96.6% 0.008 86)`): the faintly distinct surface for gloss hover states, inline code, and line-number cells; tonal layering, not shadow, separates them from the page.
- **Code Surface** (`oklch(97.5% 0.005 92)`): the diff body background, a hair more material than the page so source passages have weight without becoming dark blocks.
- **Ink** (`oklch(19% 0.016 255)`): primary text, used for headings, gloss prose, and added/removed code. High-contrast and deliberate.
- **Ink Secondary** (`oklch(34% 0.016 255)`): context (unchanged) diff lines and file-header text; still a real reading color, never a faint elegant gray.
- **Muted** (`oklch(46% 0.012 255)`): small mono labels (summary keys, file index) and the rename arrow.
- **Hairline** (`oklch(82% 0.009 86)`) / **Hairline Strong** (`oklch(66% 0.012 86)`): the borders and dividers that do the separation work shadows would do elsewhere. Strong rules are allowed where they clarify document structure.

### Named Rules
**The Confident Paper Rule.** The paper and ink carry the page. Type may be bold and rules may be decisive, but saturated color appears only where it encodes meaning: a diff line, a gloss kind, a file tag, or the active link. If a color isn't carrying information, it doesn't belong on the surface.

**The No-Hue-Only Rule.** Every color-coded distinction is reinforced by a non-color cue: diff lines pair tint with a `+`/`−` glyph; gloss kinds pair hue with a written label and dot; file tags pair hue with the tag word and a `currentColor` border; the active highlight pairs the teal tint with a positional `inset 3px 0 0` marker and top/bottom rule markers on the line. The report must read fully in grayscale and to color-blind readers. This is a hard requirement, not a nicety.

**The One Teal Rule.** Exactly one accent hue (teal, hue `215`) means "active." It is kept off the entire semantic wheel (diff hues, gloss-kind hues, tag hues) so the eye never confuses "selected" with "this is an addition" or "this is a concept gloss."

## 3. Typography

**Display Font:** `Iowan Old Style` → Charter → `Palatino Linotype` → Palatino → Georgia → Cambria → serif. It keeps the report's editorial title character, but with a smaller, less compressed scale so it does not dominate the reading surface.
**Prose Font:** Charter → `Iowan Old Style` → `Palatino Linotype` → Palatino → Georgia → Cambria → serif. Charter is quieter at paragraph sizes, so long glosses read more evenly while staying in the same bookish family.
**Gloss Font:** `-apple-system` → BlinkMacSystemFont → `Segoe UI` → system-ui → sans-serif. Glosses are scan-first annotations, not essays, so they use a compact native sans while the report frame keeps its editorial serif.
**Code / Diff Font:** `ui-monospace` → `SF Mono` → `Cascadia Code` → `Source Code Pro` → Menlo → Consolas → monospace.

**Character:** the serif gives the report a considered, read-aloud frame; the gloss sans makes individual teaching entries faster to scan. Iowan carries display flavor; Charter carries the masthead summary and page frame; the native sans carries dense gloss prose. The mono keeps code unambiguous and column-aligned, but it should sit a half-step quieter than prose so inline code does not chop up sentences.

### Hierarchy
- **Display** (Iowan-led serif, 700, `clamp(1.9rem, 1.25rem + 1.45vw, 2.75rem)`, line-height 1.06, letter-spacing -0.012em): the report title in the masthead, balanced with `text-wrap: balance`.
- **Headline** (Charter-led serif, 700, 1.2rem, line-height 1.24): the file name heading, prefixed by a small mono `file-index` counter in muted ink.
- **Body** (Charter-led serif, 400, 1rem, line-height 1.52): the masthead summary values and editorial frame text.
- **Gloss body** (native sans, 400, 0.95rem, line-height 1.46): the commentary prose. The desktop gloss lane targets about `42ch`, wide enough for teaching prose without making the row feel dominated by code; the sans texture keeps it scan-friendly.
- **Code** (mono, 400, 0.8rem, line-height 1.5): the diff lines, the primary text of the body column.
- **Gloss title** (native sans, 650, 1rem, line-height 1.18): the term or convention being explained. This is the primary object of a gloss, but it should not overpower the paragraph.
- **Metadata** (mono, 600/500, 0.64-0.66rem): the gloss kind plus range citation (e.g. `Concept · L5–7`), file tags, and summary keys. Always short, never a sentence set in all-caps.

### Named Rules
**The Three-Voice Rule.** Serif speaks for the report frame, native sans speaks for scan-first glosses, and mono speaks for code, tags, and labels. Never blur them: gloss prose is not mono, code is not serif, and the masthead keeps the editorial serif voice.

**The Quiet Code Rule.** Inline code should clarify a term without becoming a badge wall. Keep inline `code` slightly smaller than surrounding prose, lightly underlined/boxed rather than pill-heavy, and reserve stronger mono weight for file headers, labels, selected line numbers, and true multi-line examples.

## 4. Elevation

Flat by default. This is paper, not stacked glass, and there are no drop shadows anywhere in the system. Depth is conveyed entirely through **tonal layering** (paper → paper-raised → code-surface, each a fraction distinct) and **hairline rules**. The masthead and code caption can use decisive ink rules; code passages get side and bottom hairlines so they read as stable source regions, while file-to-file separation uses quieter hairlines so the report does not become a stack of boxed sections.

### Named Rules
**The Flat-Paper Rule.** No drop shadows on glosses, panels, or tags. Separation comes from hairline rules, generous whitespace, and a faint tonal shift between gloss column and source body. Heavy black rules are reserved for the masthead and the top edge of a code passage, not repeated around every region.

**The No-Card Rule.** A gloss is an entry, not a card. It can receive a quiet hover or active wash, but its identity comes from title, metadata, prose, and citation rather than a persistent box.

**The One Bold Plate Rule.** The black code caption is the page's committed visual gesture. Do not add more heavy blocks elsewhere; the contrast works because the rest of the page stays calm.

## 5. Components

### Gloss Entry (signature)
- **Character:** a compact local teaching unit, set like an index entry beside source. It explains an unfamiliar concept, convention, caveat, or context cue, not a review finding.
- **Shape:** unboxed at rest: transparent background, a hairline divider between entries, and stable 12px horizontal padding so hover and active states do not shift text. It becomes a soft 8px-radius wash only on hover or active.
- **Title:** sans `note-title`, primary. It names the term or convention first (e.g. `ActiveRecord scopes`, `Association dependencies`).
- **Metadata:** mono `note-meta`, secondary. The `note-kind` carries the semantic label (`Concept`, `Context`, `Watch`, `Notable`) and a small same-hue dot; the `note-range` carries the citation (`L5–7`) as a tiny bordered chip. Muted at rest, recoloring the range to accent-ink when active.
- **States:** rest (transparent gloss entry); hover (`paper-raised` bg + 8px radius, 0.16s ease); focus-visible (2px accent outline, 2px offset); **active** (accent-tint wash, full accent-mixed border, numeral, title, and range citation in accent-ink). Active sets `aria-pressed="true"`.

### Diff Body (signature)
- **Character:** mono code lines, the primary text of the body column.
- **Shape:** source body as a document region, not a rounded widget: a mono file caption on an ink-black source plate, followed by code-surface lines with ink side and bottom rules. On narrow screens the page stacks, and long code scrolls inside the diff body rather than widening the document.
- **Folio numbers:** each rendered diff line gets a narrow, muted `dl-num` cell using the same `data-n` value the note range chips reference. This is not an IDE gutter with source line numbers; it is the report's annotation index.
- **Line types:** add (green tint + ink text), remove (red tint + ink text), hunk (cool band + accent-ink italic), context (ink-secondary). Add/remove always pair tint with a `+`/`−` glyph.
- **Highlighted (driven by the active gloss):** the gloss→line link itself, revealed on demand. Selecting a gloss adds an accent-tint background, top/bottom rule markers, and an `inset 3px 0 0` accent bar on the code of its lines, positional markers so the highlight survives grayscale. Add/remove lines blend their stronger semantic tint with the active teal instead of losing their identity. Only one gloss's range is lit at a time; at rest the body carries no link layer at all. The first highlighted line scrolls into view (`block: nearest`), instant under reduced motion.

### File Header / Tag
- **Character:** names the file under discussion and carries its change tag.
- **Tag:** an inline mono pill (0.66rem, 5px radius, `currentColor` border), the tag word (new / mod / infra / deleted / renamed / binary) **and** a distinct hue on a faint same-hue background. Never hue alone.

### Summary Block
- **Character:** the masthead's "what / why" abstract plus a one-line interaction hint.
- **Shape:** a `<dl>` on a lightly raised paper surface with a decisive top rule, capped at 72ch; mono uppercase keys in muted ink, serif values in ink, with an italic hint divided off by a hairline.

## 6. Do's and Don'ts

### Do:
- **Do** keep the surface light and paper-like; let strong ink and serif type carry the page.
- **Do** use one committed ink source plate to keep the report from feeling monotonous.
- **Do** reserve saturated color for functional meaning only (The Quiet Surface Rule).
- **Do** pair every color-coded distinction with a label, glyph, dot, or position (The No-Hue-Only Rule); the report must read in grayscale and for color-blind readers.
- **Do** keep glosses scan-first: native sans, compact leading, and low-bulk inline code.
- **Do** keep one teal as the only "active" hue, off the entire semantic wheel (The One Teal Rule).
- **Do** separate surfaces with hairlines and tonal shifts, never drop shadows (The Flat-Paper Rule).
- **Do** keep gloss prose around a `42ch` desktop measure and hit >=4.5:1 contrast for all body text.
- **Do** keep stacked layouts constrained with `minmax(0, 1fr)` and internal diff scrolling so mobile readers never get document-level horizontal drift.
- **Do** provide a `prefers-reduced-motion` alternative (kill smooth scroll and transitions) and full keyboard operation for the note↔line interaction.

### Don't:
- **Don't** make it look like **GitHub/GitLab/Bitbucket diff chrome** — no `#0d1117` dark clone, no platform-diff styling the reader already knows.
- **Don't** use **generic AI/SaaS styling**: no purple gradients, glassmorphism, hero-metric cards, or tiny tracked uppercase eyebrows.
- **Don't** add **noisy IDE chrome** — no source line gutters, minimaps, toolbars, or panel stacks. The only permitted numeric gutter is the quiet report folio index that note ranges reference.
- **Don't** let it feel **cold, corporate, or like a compliance PDF** — it should read as deliberately made and human.
- **Don't** use a `border-left` greater than 1px as a colored type stripe on notes (the banned side-stripe pattern); encode card type with the label + dot instead.
- **Don't** turn the body background into cream/sand/parchment. The paper may be barely warm, but it should still feel like a light technical document, not a themed stationery surface.
- **Don't** set body prose in a light "elegant" gray; bump toward ink until contrast is comfortable.
- **Don't** let "active" teal collide with any semantic hue; if selection looks like an add or a concept note, the accent has drifted onto the wheel.
