# Starter vocabulary

These are hypotheses from early prototyping, not a closed taxonomy. Use them
when they fit the data and set them aside when they don't. The labels in a run
come from the data (see SKILL.md, step 3). When a starter term fits, reusing
its name keeps runs comparable. When nothing fits, coin a new label and say so
in the codebook.

## Candidate handoff labels

Candidates for what happened at a handoff, seen in early sessions.

| label | Meaning | Example | Avoidable? |
|---|---|---|---|
| `kickoff` | First turn of the session | "Add retry logic to the sync job" | n/a |
| `new-info` | Adds requirements, decisions, data or answers the agent could not have known | "Prices in Thetford: T4 @ 115…" | No. This is the human's real contribution |
| `rubber-stamp` | Approves or accepts without adding information: "yes", "go ahead", "do the next one", accepting the agent's own recommended answer | "yes", "OK let's try that" | Yes |
| `correction` | Says the agent's output or understanding was wrong and asks for rework | "That's not what I wanted", "Why are we ignoring X?" | Partly. Points to a spec or verification gap |
| `review` | Feedback on output that needs human taste or judgment (visual, wording, design) | a screenshot with "spacing feels off" | Partly. Batch it, or let the agent self-check first |
| `chore` | Asks for a routine step the agent could have done unprompted: commit, push, run tests, kill servers, clean up | "commit this" | Yes |
| `status-check` | Asks where things stand, what's left, or what to do next | "What steps remain?" | Yes. The agent should have said |
| `new-ask` | Starts a different task in the same session | "Unrelated, can you also…" | Neutral |
| `unblock` | Did something outside the session so the agent could continue: logged in, granted access, started a service | "logged in, continue" | Mostly. Fix access before the run |

When two labels fit, pick the one that says most about why the session
stopped. A "yes" that answers a real either/or the agent could not decide is
`new-info`. A "yes" to "Shall I proceed?" is a `rubber-stamp`.

## Candidate reasons the agent stopped

Useful phrasings for `why_stopped`:

- `done`: reported the task complete.
- `question`: asked something only the human could answer.
- `confirm`: asked permission to continue ("Want me to…?", "Shall I proceed?").
- `checkpoint`: stopped after a phase of a plan that was already approved.
- `blocked`: hit an error it could not resolve.
- `blocked-access`: needed a login, token or access grant (see the turn's `access_errors`).
- `none`: no agent message (kickoff, or the turn was interrupted).

`confirm` and `checkpoint` yields followed by a `rubber-stamp` are the
purest fragmentation: two context switches that added nothing.

## Themes

For every `correction`, `review`, `question` or `confirm`, also write a short
`theme`: the kind of thing, reusable across sessions. Examples: "over-abstraction",
"restating comments", "codebase test convention", "naming", "scope creep", "which
data source to trust", "whether to add a migration". Reuse earlier theme names
so they aggregate. Recurring themes are the raw material for rules and skills.

## Mid-run handoffs (from the extractor)

- `permission`: a tool call needed human approval. `wait_s` includes command runtime for shell tools.
- `question`: the agent called AskUserQuestion mid-run.
- `plan-approval`: ExitPlanMode was shown for approval.

The extractor also records per turn `access_errors` (login, token or 401/403
failures), `auto_denied` (auto mode refused a command, e.g. git push), and
`subagents` (Task/Agent calls).

## Candidate session types

Each type has a different healthy shape:

- `quick`: a one- or two-turn question, query or report. Count it, don't score it.
- `hill-climb`: a long autonomous loop over many small fixes, often overnight. What matters is what ended each long run and how long the session sat idle afterwards.
- `feature`: build a defined change, from spec to PR.
- `research`: exploration or discussion. Usually `driving`.
- `polish`: review and rework of something built in an earlier session, often on the same git branch. Its corrections are the earlier session's rework, so link them by branch.

## Candidate session modes

- `blocked`: the agent had work it could do and stopped for the human. Fragmentation here costs throughput.
- `driving`: the human leads with data, ideas or questions, and the agent can't advance without them. Gaps here are not waste. Note the session but don't score it.
- `mixed`: phases of both, for example a driving spec discussion followed by blocked implementation.

## Candidate patterns

Shapes seen so far, for a session or a phase within one.

| Archetype | Shape | Healthy? |
|---|---|---|
| Spec, build, ship | Short cluster of `new-info`, one long run, one short tail | Yes |
| Interview, then build | Many short turns of Q&A, mostly `rubber-stamp` answers to agent proposals, then runs | Front half is avoidable |
| Phase-gated | Long runs separated by `checkpoint` yields and `rubber-stamp` go-aheads | Avoidable |
| Babysat | Long runs with many mid-run `permission` handoffs | Avoidable |
| Long tail | A main run followed by many `correction` / `review` turns | Points to spec or verification gaps |
| Review loop | Repeated `review` turns with short runs between | Partly inherent. Can be batched |
| Drift | `correction` or `new-ask` in the middle of implementation | Plan wasn't settled |
| Conversation you drive | Mostly `new-info`, short runs, mode `driving` | Fine |
| Spec sprawl | Long `driving` discussion before the first long run, drifting into implementation detail | Avoidable. Draft-and-redline beats Q&A |
| Hill-climb | One or a few very long runs ended by `blocked`/`blocked-access` yields, then long idle gaps | Healthy if runs end on `done` |
| Cross-session polish | A `polish` session full of `correction`/`review` on a branch an earlier session built | Rework moved, not avoided |

## Remedy types

The kinds of fix the person is looking for. Tag findings with one of these when it fits:

- `guidance`: CLAUDE.md or AGENTS.md rules, or prompt habits for kicking off work.
- `skill`: extract a repeated procedure or a body of preferences into a skill (a spec template, a review checklist, a codebase's conventions).
- `script`: a deterministic tool the agent can call instead of improvising (data pulls, report generation, environment setup).
- `verification`: something that lets the agent check itself before handing back (tests, linters, type checks, hooks, screenshot self-review).
- `access`: permissions, allowlists, credentials and login preflight.
- `workflow`: how the human structures work (batching, parallel or background sessions, when to split sessions).

## Remedy ideas

A bank of fixes that worked or made sense before. Prefer a remedy grounded in
the person's own data over one from this table.

| Cause | Remedies |
|---|---|
| `permission` on a few repeated commands | Allow rules in `.claude/settings.json` built from the actual commands, e.g. `"Bash(git commit:*)"`. Consider auto mode. For Codex, approved-command rules |
| `chore` commit/push/test/cleanup | CLAUDE.md rule, e.g. "Commit when a unit of work is complete and tests pass. Stop any servers you start before finishing." Or a Stop hook |
| `confirm` / `checkpoint` + `rubber-stamp` | CLAUDE.md rule: "Once I approve a plan, carry it through all phases. Only stop when blocked or when a decision changes scope." |
| Interview with many `rubber-stamp` answers | Ask clarifying questions in batches of 3–5, each with a recommended default, and proceed on defaults the human doesn't contest. Edit the interviewing skill accordingly |
| `status-check` | End every turn with what was done, what is left, and what (if anything) is needed from the human |
| `correction` after a long run | Better upfront spec (plan mode for larger changes), and give the agent a way to verify itself: tests, screenshots, a lint/type-check hook |
| `review` loops on visual work | Let the agent screenshot and critique its own output before handing back. Batch feedback into one message |
| `question` mid-run on discoverable facts | Put the fact in CLAUDE.md, or tell the agent where to look |
| `access_errors` / `unblock` | Preflight script or SessionStart hook that checks each needed login (warehouse, observability, cloud) and fails fast before a long run. Longer-lived or read-only agent credentials. Rule: "If a data source needs login, record the blocked item, continue with the rest, and list blocked items at the end" |
| `auto_denied` (e.g. git push) | Decide whether the block is wanted. If it is, end long runs with a ready-to-push summary instead of stopping mid-way |
| Recurring `correction`/`review` themes | Turn each recurring theme into a CLAUDE.md rule, a lint rule, or a review skill the agent runs on its own diff before handing back |
| Recurring `question`/`confirm` themes | A decision policy in CLAUDE.md ("prefer X over Y", "for reversible choices, decide, note the assumption and continue") |
| Spec sprawl | Have the agent draft a complete spec with defaults for the human to redline. Keep a "decide later" list for implementation details. A spec skill with fixed sections |
| Long human gaps before `rubber-stamp` | Run sessions in parallel or in the background so a stalled one costs less. Notifications when a session needs you |
