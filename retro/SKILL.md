---
name: retro
description: Analyze a coding session for the moments a human had to intervene, then propose durable harness improvements — extracted skills, hooks, deterministic verifiers, generators, connectors, domain-specific scripts. Use when the user says /retro, asks for a retrospective, asks how a session went, or asks what could be automated or extracted from the work just done. Also offer after long or friction-heavy sessions.
---

# Retro

Find every moment a human had to step into the loop, and propose the mechanism
that makes each one unnecessary next time. The fix for a bad session is a
missing part of the harness, not a better prompt — so every finding must end at
something that can be built, wired, and run without the user remembering to ask.

An observation with no proposal is a failed retro. So is a proposal the user
cannot act on without a follow-up question.

Produce the report in one pass. Do not interview the user first and do not ask
permission to begin.

## 1. Scope the session

Default to the current session. Locate its transcript the way this harness
exposes one — a transcript store, a resume listing, a log directory — rather
than assuming a path. Find an earlier session the same way.

Use both sources: the transcript carries the narrative arc (user messages,
re-prompts, what was said out loud), the live context carries tool calls,
results, and reasoning. If the session was compacted, say so in the report and
treat tool-level detail from before the boundary as unreliable — compaction is
itself a finding (§2).

## 2. Find the interventions

Scan for every point where a human had to act for the system to keep making
progress:

| Signature in the transcript | Intervention type | What it implies |
|---|---|---|
| User negates, redirects, or asks for a redo | **Correction** | A constraint the system never enforced |
| User pastes a command's output, an error, a log, a screenshot | **Plumbing** | A signal the agent could not reach itself |
| User states a convention, invariant, or file location | **Context supply** | Knowledge that lives nowhere the agent looks |
| The same instruction appears twice, or is one the user gives every session | **Recurring steer** | The strongest candidate for a durable mechanism |
| A check fired and the agent misread it, patched around it, or thrashed | **Blind sensor** | The sensor exists but its output is not agent-actionable |
| A defect reached human review with no check that could have caught it | **Sensor gap** | Nothing in the system was watching |
| Long read/grep/probe sequences before finding the target, or reasoning about system state the agent cannot observe | **Flailing** | Missing vocabulary and missing observability |
| Work was thrown away and redone | **Rework** | Steps ran in the wrong order; a workflow problem |
| Context was compacted, or quality degraded in late turns | **Context pressure** | The session held more than it could use |

Record each with its turn and one sentence of what happened. The count matters
less than whether each one is likely to recur.

Note briefly which existing mechanisms caught something before the user had to.
Those are the parts of the harness paying off and worth extending.

## 3. Diagnose each intervention

Answer one question: **what did the system not know, not check, or not reach?**

- **Not know** — information existed somewhere but never reached the agent.
  Missing feedforward.
- **Not check** — the agent produced something wrong and nothing tested it.
  Missing feedback.
- **Not reach** — the information or tool existed but the agent had no way to
  touch it, so the user became the wire. Missing capability.

Name the root cause, not the symptom. "The agent wrote a bad migration
filename" is a symptom; "the filename algorithm lives in a generator the agent
never ran" is the cause, and it points at a different mechanism.

## 4. Choose a mechanism

Run each root cause down this funnel. Stop at the first level that can carry
the judgment.

1. **Encode it deterministically**, if the judgment can be. Inference is
   inconsistent; compile yesterday's judgment into tomorrow's tooling.
2. **Constrain what gets made, or verify what was made?** Constraining is
   cheaper — a generator, template, or schema means the agent never has to know
   the rule. Verifying is a linter, test, or check.
3. **Can the agent invoke it, and does its output flow back without a human?**
   If not, the mechanism is unfinished: add the hook, the allowed command, the
   connector. A tool the user has to run and paste is still plumbing.
4. **Can a narrow agent judge it after the fact?** A review skill with a single
   thesis of quality, run as a subagent so it does not spend the main context.
5. **Instruction text**, only if none of the above reach — and only as a routing
   line ("when touching X, run Y"), never a transfer of judgment.

Tag every proposal with its quadrant (model from Birgitta Böckeler):

|  | **Computational** | **Inferential** |
|---|---|---|
| **Feedforward** | Generator, template, scaffold, schema constraint, setup script, blocking hook | Instruction line, project doc, nearby example code |
| **Feedback** | Linter rule, test, type check, security scanner, dev logs, browser test, verifier script | Review skill, subagent audit, LLM-as-judge |

Inferential feedforward is the trap: the one quadrant that is never enforced,
only hoped for. If most proposals land there, the analysis stopped too early —
go back to §4.1.

Three rules constrain every choice:

- **Repair a blind sensor before adding a layer on top of it.** If a check
  fired and the agent misread it, the fix is that check's output — a clearer
  failure message, a wrapper reporting the actionable part — not an instruction
  explaining how to interpret it.
- **Remove the human from the wire before optimizing what flows through it.**
  A plumbing intervention is a capability or wiring problem first.
- **Propose portable mechanisms** — a skill, a hook, a script, a doc — not a
  rule file that only one harness reads.

### Mechanism catalog

| Mechanism | Reach for it when |
|---|---|
| **Generator / scaffold** | A file's shape, name, or wiring follows an algorithm. Running the generator becomes the agent's only job; the algorithm stays out of its head. |
| **Blocking hook** | A whole class of action should be refused at the boundary. The refusal message must say what to do instead, or the agent routes around the block. |
| **Verifier hook** | An existing check should run at a fixed event — before finish, after edit — so its failures land in the loop instead of in the user's lap. |
| **Custom lint rule** | A mistake is mechanically detectable. Be ambitious: rules not worth hand-writing are cheap now. Extend the linter already wired in rather than adding a second tool. |
| **Deterministic verifier script** | Correctness is checkable but no off-the-shelf tool checks it — an invariant across files, a config that must match a schema, a generated artifact that must match its source. Exit non-zero with a message naming the fix. |
| **Domain-specific script** | The agent flailed reasoning about raw tables, logs, or branches instead of domain concepts. Report the domain's own structure — the funnel, the buckets, the bail points — with hard-coded definitions so runs are comparable. |
| **Connector** | The agent needed a system it cannot touch: a database, dashboard, API, browser, issue tracker. The user copying data out of one is direct evidence. |
| **Extracted skill** | A named workflow was latent in the session — a sequence the user steered by hand that will recur. Also: a review pass with one clear thesis. |
| **Orchestration skill** | The pieces exist but the user sequenced them manually. Wrap the order into one invocable workflow, delegating expensive passes to subagents. |
| **Test or assertion** | A regression would be caught by a check that belongs in the suite anyway. |
| **Project doc** | Real knowledge that is not in the code and cannot be encoded — a decision history, an external system's behavior. Scoped and routable, not a brain dump. |
| **Context strategy** | Context pressure was the root cause: split the work, push a phase into a subagent, or persist state to a file between phases. |

## 5. Filter

Cut proposals that fail any of these:

- **Recurrence.** Would this friction plausibly happen again? A one-off
  misunderstanding needs no mechanism; recurring steers need one most.
- **Cost.** Every mechanism costs wall-clock time on every run, or agent
  attention on every turn, forever. Say the cost out loud for each proposal.
- **Goodhart.** Would the agent optimize this against the underlying goal? Proxy
  metrics — quality scores, coverage thresholds, complexity budgets — are where
  this bites. Prefer checking a property over scoring one.
- **Buildability.** Could the user say yes and get a working thing? If it needs
  a design conversation first, it is not ready.

Three proposals the user will build beat nine they will skim.

## 6. Report

Keep it dense. No preamble, no recap of the session's content. Name what went
wrong plainly — "opportunity" is not a finding.

```
## Session

One or two lines: what the work was, where the time actually went,
whether the transcript was complete.

## Interventions

| # | Turn | What happened | Type | Root cause |

## Proposals

For each, in priority order:

### N. <Imperative title>
**Quadrant** · **Cost:** <what it costs on every run>
What it is, in one or two sentences.
**Build:** the concrete artifact — file path, what it checks, what it
refuses, what the failure message says.
**Wiring:** how its output reaches the loop without a human.
**Evidence:** the intervention(s) it removes.

## Considered and rejected

One line each, with the reason.

## Open questions

Only where a recommendation genuinely turns on something the transcript
cannot show. Omit the section otherwise.
```

Rank proposals by leverage: how much intervention each removes, divided by cost
to build and cost to run. Deterministic mechanisms that constrain generation
usually win.

## 7. Build

Close with one line: which to build. On assent, build immediately and fully —
write the hook config, the generator, the script, the skill file — and verify
it runs. A retro that ends in a list of good intentions has failed the same way
one that ends in observations has.
