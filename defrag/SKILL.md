---
name: defrag
description: Analyze Claude Code or Codex sessions for how often the agent stopped and needed the human, visualize each session as a fragmented bar, and suggest concrete changes (guidance, skills, scripts, verification, access) that let sessions run longer without the human. Use when asked to defrag, review session fragmentation, or find why sessions keep blocking.
---

# Defrag

A session is a bar of agent runs separated by handoffs, the moments the agent
needed the human. Defrag finds which handoffs the agent could have done
without, what caused them, and what change would remove them. The goal is
continuous improvement of how the person works with agents, not a score.

The categories are still being discovered. Derive labels from the sessions in
front of you rather than fitting them to a predefined list.
`references/starter-vocabulary.md` holds earlier hypotheses and a bank of
remedies: borrow names from it when they fit, and ignore it when they don't.

## 1. Choose the sessions

Default: the current project's Claude Code sessions from the last 14 days.
For a person with several repos, offer `~/.claude/projects` as a whole.
Honor anything the person names instead: a project, a date range, specific
files, or Codex (`~/.codex/sessions`). Claude Code transcripts live in
`~/.claude/projects/<cwd-with-dashes>/*.jsonl`.

Work in a scratch directory (e.g. `/tmp/defrag-<date>/`), never inside the
person's repo.

## 2. Extract

```
python3 scripts/extract.py [PATHS...] --since YYYY-MM-DD --min-turns 2 -o sessions.json
```

This is deterministic and records only facts. Each turn has the human
`prompt`, the agent's `prior_agent_message`, `run_s` (agent time),
`human_gap_s` (time until the next prompt), tool and subagent counts,
`interrupted`, the mid-run `handoffs` (permission prompts, AskUserQuestion,
plan approvals), `access_errors` and `auto_denied`. Session `meta` includes
git `branches` and `longest_run_s`.

## 3. Code the handoffs

Every turn after the first is a handoff. For each one, read the prompt with
`prior_agent_message` and answer the two core questions. These are fixed so
runs stay comparable:

- `could_continue`: could the agent have kept going without the human? `yes`, `no` or `unclear`. Answer `yes` when a reasonable default, a rule, a check the agent could run itself, or access it could have had would have let it proceed.
- `contribution`: what did the human add? `information` (facts, decisions or taste the agent could not know), `approval` (go-ahead, yes, commit, continue: nothing new), `rework` (the output or understanding was wrong) or `other`.

Then describe it in your own words:

- `why_stopped`: a few words on why the agent handed back.
- `label`: a short free-form name for the kind of handoff.
- `theme`: for rework and for decisions the agent stopped on, the kind of thing (e.g. "naming", "test convention"). Reuse names so they aggregate.
- `gist`: a short generic description, without names, paths or code. The share export reuses it.

Work in two passes. First label freely, session by session. Then consolidate
the labels into a codebook of at most ~10 entries, each with a definition and
an example, and rename the turn labels to match. Cases that resist coding go
in `hard_cases`, because they are where the categories need work.

Write `labels.json`:

```json
{
  "codebook": [{"label": "phase go-ahead", "definition": "…", "example": "…"}],
  "hard_cases": ["a yes that both approved and chose between two options"],
  "sessions": {
    "<meta.id or meta.file>": {
      "summary": "one generic sentence about what the session was for",
      "pattern": "optional short name for the session's shape",
      "turns": {"1": {"could_continue": "yes", "contribution": "approval", "why_stopped": "asked whether to start phase 2",
                      "label": "phase go-ahead", "gist": "approved the next phase"}}
    }
  },
  "findings": [{"label": "phase go-ahead", "remedy_type": "guidance", "title": "…", "body": "…with counts…", "fix": "…exact rule or setting…"}]
}
```

Count one- or two-turn sessions (quick questions, one-off reports) but don't
code them unless they show something unusual. For more than ~300 handoffs,
code in batches of sessions and consolidate the codebook at the end.

## 4. Find patterns

Look across sessions. Count before claiming. Start from the handoffs where
`could_continue` is `yes`, since those are the ones the person wants gone.
Questions worth answering:

- **Up front:** How many turns go by before the first long run? Do the kickoffs of clean runs share something (a written spec, acceptance checks, named files)?
- **Mid-run:** Why did the agent stop when it could have continued? Which decisions, approvals, logins or access errors? How long did the session then sit idle?
- **Rework:** What are the recurring rework themes? Link sessions on the same git branch, since review and polish often happen in a later session.
- **Long runs:** For long autonomous sessions, what ended each long run?

Write 3 to 7 findings, most avoidable first. Each names the evidence (counts
and example sessions) and a concrete fix the person can make, tagged with a
`remedy_type`: guidance, skill, script, verification, access or workflow.
Use exact text where it fits: allow rules built from the real commands,
CLAUDE.md lines, or a skill to extract. Note anything the person already
fixed during the period, since that's the improvement loop working.

## 5. Render

```
python3 scripts/render.py sessions.json labels.json -o defrag.html
```

Open the page for the person, or publish it as an artifact if that's
available. Then reply with the top three findings and their fixes in a few
lines. Offer to apply a fix (settings, CLAUDE.md), and only edit those files
when the person says yes.

## 6. Share mode (optional)

When the person wants to discuss results somewhere their transcripts can't go:

```
python3 scripts/share.py sessions.json labels.json -o defrag-share.md
```

This keeps only shapes, the core answers, labels, the codebook, timings,
command families, themes and gists. Tell the person to read it before sharing,
because the text fields are written by you and could still carry specifics.
