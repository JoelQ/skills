# Product

## Register

product

## Users

Developers reading a git diff they didn't write, most often while onboarding to an
unfamiliar codebase, language, or framework. They open the report to *understand*
a change — what it does, why, and which patterns they're not yet fluent in. They are
technically capable but may lack context on this specific stack. Their state is
usually "facing unfamiliar code," which carries some friction and uncertainty; the
report's job is to lower that friction. They read more than they edit. The report is
a generated, self-contained HTML artifact they open and scan, not an app they live in.

## Product Purpose

The diff-explainer skill turns a git diff into a two-column HTML report: commentary
cards on the left, the diff on the right, with cards that highlight the lines they
describe. It exists to *teach and explain* a changeset for a specific reader — not to
review it for bugs. Success is the reader closing the report understanding the change
and the codebase conventions behind it, with less intimidation than when they opened it.
The author's judgment (what's worth a card, how to phrase it) is the value; the report's
design must make that judgment easy to absorb.

## Brand Personality

Calm and clear above all. The report should feel like a knowledgeable colleague
quietly annotating code beside you — composed, precise, low-noise, never shouting.
Considered and human, not generated-and-forgotten. Reading-first: prose and code are
co-equal, and the experience is closer to a well-set annotated document than to a tool
chrome. Three words: **calm, lucid, considered.**

## Anti-references

- **GitHub / GitLab / Bitbucket diff UIs.** The current template is a faithful
  GitHub-dark clone; the report should have its own identity, not look like a diff view
  the reader already knows from the platform.
- **Generic AI/SaaS slop.** No purple gradients, glassmorphism, hero-metric cards, or
  tiny tracked uppercase eyebrows. Identity is earned through craft, not trend signifiers.
- **Noisy IDE chrome.** Not a busy editor of panels, gutters, minimaps, and toolbars.
  This is a surface for reading and understanding, not for editing.
- **Cold / corporate blandness.** Not a sterile enterprise-docs or compliance-PDF look.
  It should read as deliberately made and human.

## Design Principles

1. **Comprehension is the only metric.** Every visual decision is judged by whether it
   makes the change easier to understand. Decoration that competes with content loses.
2. **The annotation is the interface.** Prose commentary and code are co-equal partners,
   read together. The link between a card and its lines is the core interaction and must
   feel effortless. (Inspiration: literate-programming / annotated-source layouts.)
3. **Lower the intimidation.** The reader is on unfamiliar ground. Favor calm, scannable
   hierarchy and breathing room over density; the report should make hard code feel
   approachable, not more daunting.
4. **Distinct, never ornamental.** Earn a recognizable identity through typography,
   spacing, and restraint — the polish of a well-made dev tool (Raycast / Linear / Warp),
   not surface styling bolted on top.
5. **Meaning never depends on color alone.** Card types and diff tags (new / mod / warn /
   concept / surprise) must remain distinguishable in grayscale and to color-blind
   readers — pair color with label, shape, or icon.

## Accessibility & Inclusion

Target WCAG 2.1 AA: body text ≥4.5:1 contrast, large text ≥3:1, full keyboard operation
of the clickable cards, and a `prefers-reduced-motion` alternative for the highlight /
scroll behavior. **Color-blind safe is a hard requirement:** the new/mod/infra/deleted/
renamed tags and the observation/concept/warn/surprise card types must be distinguishable
without relying on hue — reinforce every color-coded distinction with a text label, icon,
or shape so the encoding survives deuteranopia/protanopia and grayscale printing.
