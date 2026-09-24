# Skills

A small collection of reusable agent skills for reviewing code, explaining changes, and improving development workflows.

## Common review workflow

For a thorough code review, these three skills are often used as successive passes:

1. **Structural Review** — align the code's overall shape with the domain.
2. **Method Review** — clarify the implementation one method at a time.
3. **Hierarchical Documentation** — polish names and comments before presenting the result.

## Commit Messages

[View the skill](commit-messages/SKILL.md)

Writes commit messages that explain the context, reasoning, and trade-offs behind a change—not merely the files that changed. Use it to leave future readers a durable narrative of why a decision was made.

## Diff Explainer

[View the skill](diff-explainer/SKILL.md)

Turns a Git diff into an interactive, reader-specific HTML walkthrough with concise teaching notes linked to relevant lines. Use it to understand or explain an unfamiliar change, especially when the language, framework, or project conventions are new to the reader.

## Structural Review

[View the skill](structural-review/SKILL.md)

Evaluates whether code structure matches the problem domain by naming concepts, finding leaky abstractions, and comparing alternative framings. Use it when an implementation feels awkward at a deeper level than method cleanup and you want to reconsider the model or overall approach. It is usually the first of the three review passes.

## Method Review

[View the skill](method-review/SKILL.md)

Reviews individual methods for clarity, with attention to decomposition, conditionals, boolean logic, and unnecessary machinery. Use it after Structural Review to improve local control flow without losing sight of the larger design.

## Hierarchical Documentation

[View the skill](hierarchical-documentation/SKILL.md)

Polishes names and comments so information lives at the most useful level of the code before human review. Use it as the final pass, after Structural Review and Method Review, to prepare the result for someone else.

## Retro

[View the skill](retro/SKILL.md)

Examines a coding session for moments when a human had to intervene, then proposes concrete improvements such as hooks, generators, verifiers, connectors, or new skills. Use it after a long or friction-heavy session to turn recurring pain into durable automation.
