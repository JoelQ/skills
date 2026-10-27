# Starter vocabulary

The work purposes, shapes and patterns live in `patterns-seed.json`, which
seeds the pattern library (`scripts/patterns.py show`). This file holds the
rest: words for stops, what the person brought back, themes, and a bank of
remedies. These are hypotheses from early prototyping. Use them when they fit
and coin new names when they don't.

## Labelling what a run was for

A run's `work` is its purpose, not its activity mix, and the list is closed.
Ask what the run delivers when it succeeds: understanding (`explore`), a
decision (`shape`), a change (`build`), a known failure fixed (`debug`),
confidence (`verify`) or landed work (`ship`). A run that builds a
feature, runs the tests and commits is `build`. `verify` and `ship` are their
own labels only when a run existed just for that ("run the suite", "commit
this"), because those small runs are the human touches defrag wants to remove.

Weigh three signals, in this order:

1. **Continuity.** A run carries on the previous run's purpose by default.
   "Yes, but also do X" after a build is still build.
2. **Effort.** The run's `mix` counts edits, reads, test runs, git and queries.
   Where most of the run's tool calls went outweighs a side request in the prompt.
3. **The prompt.** What was asked. It breaks ties and marks a real change of
   direction ("stop, let's rethink this").

When the signals disagree, set `"confidence": "low"`. Those runs render hatched.

Rework is not a work type. It is a relationship between runs (a correction,
then fixes) and shows up as a pattern such as `rework tail`.

## Stop reasons

Short phrases for `reason`, shown in tooltips and counted in the work-by-stop
grid. The extractor's `kind` and `hard` already cover the mechanical part.

- `finished`: reported the task done.
- `asked`: asked something only the person could answer.
- `checkpoint`: paused between steps of approved work to ask whether to go on.
- `proposed next step`: described what it would do next and waited.
- `handed back to check`: claimed a fix and asked the person to confirm it works.
- `blocked`: could not continue without a capability it lacked.
- `plan approval`: presented a plan for sign-off.
- `permission`, `auth block`, `interrupt`: forced stops; use them when `hard` is set.

## What the person brought back

For `response`, used under the hood (for example to spot a rework tail) and
shown in tooltips:

- `information`: facts, decisions or taste the agent could not have known.
- `approval`: a yes, a go-ahead, an approved tool call. Nothing new.
- `correction`: the output or understanding was wrong.
- `new ask`: a related piece of work added after the current one.
- `unblock`: logged in or granted access so the agent could continue.

A "yes" that picks between real options the agent could not decide is
`information`. A "yes" to "shall I proceed?" is `approval`.

## Themes

For corrections and for decisions the agent stopped on, write a short reusable
`theme`: "over-abstraction", "restating comments", "codebase test
convention", "naming", "which data source to trust", "whether to add a
migration". Reuse names so they aggregate. Recurring themes are the raw
material for rules and skills.

## Remedy types

Tag each finding with one:

- `guidance`: CLAUDE.md or AGENTS.md rules, or habits for kicking off work.
- `skill`: extract a repeated procedure or body of preferences into a skill.
- `script`: a deterministic tool the agent can call instead of improvising.
- `verification`: something that lets the agent check itself before handing back.
- `access`: permissions, allowlists, credentials and login preflight.
- `workflow`: how the person structures work (batching, parallel or background sessions, splitting sessions).

## Remedy ideas

Prefer a remedy grounded in the person's own data over one from this table.

| Pattern or cause | Remedies |
|---|---|
| Forced `permission` stops on a few repeated commands | Allow rules in `.claude/settings.json` built from the actual commands, e.g. `"Bash(git commit:*)"`. Consider auto mode. For Codex, approved-command rules |
| `auth block` stops (warehouse, observability, model API login) | Preflight script or SessionStart hook that checks each login and fails fast before a long run. Longer-lived or read-only agent credentials. Rule: "If a data source needs login, record the blocked item, continue with the rest, and list blocked items at the end" |
| `checkpoint chain` | CLAUDE.md: "Once I approve a plan, carry it through all phases. Stop only when blocked or when a decision changes scope." |
| `ship tail` | CLAUDE.md: "Commit when a unit of work is complete and tests pass." Allow git and gh commands. Say "commit when green, open a draft PR" in the kickoff |
| `interview` with mostly `approval` answers | Ask questions in one batch, each with a default, and proceed on any the person doesn't contest. Ask "what makes this succeed?" explicitly |
| `spec sprawl` | Have the agent draft a complete spec with defaults for the person to redline. Keep a "decide later" list for implementation details |
| `rework tail` after a `long run` | Write the success criterion into the plan as an acceptance check. Give the agent a way to verify itself: tests, screenshots, a lint or type-check hook |
| `visual check loop` | Give the agent a browser or screenshot tool and a rule to check UI changes itself before handing back |
| `rework cluster` on another session's branch | Capture recurring themes as CLAUDE.md conventions, and add a self-review step that checks the diff against them before each commit |
| `mid-build redirects` | Settle the approach before building: a short plan with the alternatives named |
| Recurring decision themes | A decision policy in CLAUDE.md ("prefer X over Y"; "for reversible choices, decide, note the assumption and continue") |
| Long waits before an `approval` | Run sessions in parallel or in the background so a stalled one costs less. Notifications when a session needs you |
