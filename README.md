# Skills

A small collection of reusable agent skills for reviewing code, explaining changes, and improving development workflows.

## Common review workflow

For a thorough code review, these three skills are often used as successive passes:

1. **Structural Review** — align the code's overall shape with the domain.
2. **Method Review** — clarify the implementation one method at a time.
3. **Hierarchical Documentation** — polish names and comments before presenting the result.

## Commit Messages

<p>
  <img src="icons/readme/commit-messages.png" alt="Commit Messages icon" width="72" align="left">
  <a href="commit-messages/SKILL.md">View the skill</a><br>
  Writes commit messages that explain the context, reasoning, and trade-offs behind a change—not merely the files that changed. Use it to leave future readers a durable narrative of why a decision was made.
</p>
<br clear="left">

## Diff Explainer

<p>
  <img src="icons/readme/diff-explainer.png" alt="Diff Explainer icon" width="72" align="left">
  <a href="diff-explainer/SKILL.md">View the skill</a><br>
  Turns a Git diff into an interactive, reader-specific HTML walkthrough with concise teaching notes linked to relevant lines. Use it to understand or explain an unfamiliar change, especially when the language, framework, or project conventions are new to the reader.
</p>
<br clear="left">

## Structural Review

<p>
  <img src="icons/readme/structural-review.png" alt="Structural Review icon" width="72" align="left">
  <a href="structural-review/SKILL.md">View the skill</a><br>
  Evaluates whether code structure matches the problem domain by naming concepts, finding leaky abstractions, and comparing alternative framings. Use it when an implementation feels awkward at a deeper level than method cleanup and you want to reconsider the model or overall approach. It is usually the first of the three review passes.
</p>
<br clear="left">

## Method Review

<p>
  <img src="icons/readme/method-review.png" alt="Method Review icon" width="72" align="left">
  <a href="method-review/SKILL.md">View the skill</a><br>
  Reviews individual methods for clarity, with attention to decomposition, conditionals, boolean logic, and unnecessary machinery. Use it after Structural Review to improve local control flow without losing sight of the larger design.
</p>
<br clear="left">

## Hierarchical Documentation

<p>
  <img src="icons/readme/hierarchical-documentation.png" alt="Hierarchical Documentation icon" width="72" align="left">
  <a href="hierarchical-documentation/SKILL.md">View the skill</a><br>
  Polishes names and comments so information lives at the most useful level of the code before human review. Use it as the final pass, after Structural Review and Method Review, to prepare the result for someone else.
</p>
<br clear="left">

## Pentest

<p>
  <img src="icons/readme/pentest.png" alt="Pentest icon" width="72" align="left">
  <a href="pentest/SKILL.md">View the skill</a><br>
  Security-audits a user-specified subsystem by using adversarial RSpec request specs to probe authorization and data-exposure boundaries. Use it when you want executable evidence of vulnerabilities, plus a report of confirmed risks and verified defenses, rather than a purely speculative review.
</p>
<br clear="left">

## Retro

<p>
  <img src="icons/readme/retro.png" alt="Retro icon" width="72" align="left">
  <a href="retro/SKILL.md">View the skill</a><br>
  Examines a coding session for moments when a human had to intervene, then proposes concrete improvements such as hooks, generators, verifiers, connectors, or new skills. Use it after a long or friction-heavy session to turn recurring pain into durable automation.
</p>
<br clear="left">

## Defrag

<p>
  <img src="icons/readme/defrag.png" alt="Defrag icon" width="72" align="left">
  <a href="defrag/SKILL.md">View the skill</a><br>
  Charts Claude Code and Codex sessions as bars of agent runs cut by stops, the moments you had to act. Each run is coloured by what it was for, forced stops (permission prompts, logins, interrupts) stand out in red, and named patterns like "interview" or "rework tail" are bracketed above the bar from a vocabulary that persists between reports. Claude's own read comes separately, with guidance, skills, scripts, verification or access changes. Use it across a week or two of sessions to find why work keeps blocking on you. It's a sibling of Retro: Retro looks deep into one session, Defrag looks for patterns across many.
</p>
<br clear="left">
