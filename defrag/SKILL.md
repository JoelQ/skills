---
name: defrag
description: Analyze Claude Code or Codex sessions as runs of continuous agent work cut by stops where the human had to act, visualize each session as a bar coloured by what each run was for with named patterns above it, and suggest concrete changes (guidance, skills, scripts, verification, access) that let sessions run longer without the human. Use when asked to defrag, review session fragmentation, or find why sessions keep blocking.
---

# Defrag

A session is a bar of **runs** separated by **stops**. A run is continuous
agent work: compactions, subagent results, background notifications and
commands auto mode refused all stay inside it. A stop is a point where the
human had to act: reply to a finished turn, approve a permission prompt,
answer a question, approve a plan, log in, or interrupt.

The report has two audiences. The map (bars, colours, brackets) is for the
person to scan and draw their own conclusions, so everything on it is either
a fact from the logs or a name from a shared vocabulary. Your judgment goes
in a separate section of findings. Keep the two apart.

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

This is deterministic and records only facts. Each run has the human `prompt`
that started it (`opened_by` says whether that was a prompt, an approval or an
answer), the agent's `prior_agent_message`, `run_s`, tool counts and `mix`
(edits, reads, test runs, git, queries, shell, subagents), `compactions`,
`notifications`, `access_errors` and `auto_denied`. Each run ends in a `stop`
with a `kind` (ended, permission, question, plan, interrupted, or `last`),
`wait_s`, the human's `reply`, and `hard`: `permission`, `auth` or
`interrupt` when the stop was forced, otherwise null. Session `meta` includes
git `branches`, `stops` and `hard_stops`.

## 3. Load the vocabulary

```
python3 scripts/patterns.py show
```

This prints the work purposes, the shapes and the patterns seen in past
reports (from `~/.claude/defrag/patterns.json`, seeded from
`references/patterns-seed.json`). Reuse these names whenever they fit, so
reports stay comparable. `references/starter-vocabulary.md` has words for
stop reasons, responses and themes, and a bank of remedies.

## 4. Label

Go session by session, in order, with neighbouring runs in view.

**Each run: what it was for** (`work`). Label the purpose, not the activity
mix. A run that builds, tests and commits its own work is `build`. Use
`verify` or `ship` only for a run that existed just to check or just to
commit. Weigh continuity first (a run carries on the previous run's purpose),
then effort (where `mix` says the tool calls went), then the prompt. A brief
"yes, but also do X" does not change the purpose. When the signals disagree,
add `"confidence": "low"`. Rework is not a work type.

**Each stop: what happened.** `reason` is a short phrase for why the agent
stopped. `response` is what the human brought back (information, approval,
correction, new ask, unblock). Add a reusable `theme` for corrections and for
decisions the agent stopped on, and a `gist`: a short generic description
without names, paths or code. Don't judge whether a single stop was
avoidable. Avoidability belongs to patterns, because each stop in a rework
tail can be justified while the whole tail is waste.

**Patterns: the brackets** (`segments`). Mark stretches of runs by shape
first: gate, cluster, chain, long run, loop or tail. Then name each one from
the vocabulary by the work and stops inside it ("interview", "rework tail",
"closed loop"). Names describe structure and stay neutral: "scattered
approvals", not "babysitting". Not every run needs a bracket. Coin a new name
only when nothing fits, and define it in the codebook.

Write `labels.json`:

```json
{
  "codebook": {
    "work": [{"label": "build", "definition": "…"}],
    "segments": [{"label": "rework tail", "shape": "tail", "definition": "…"}]
  },
  "hard_cases": ["a correction that names a codebase convention"],
  "sessions": {
    "<meta.id or meta.file>": {
      "summary": "one generic sentence about what the session was for",
      "runs": {"0": {"work": "shape"}, "1": {"work": "build", "confidence": "low"}},
      "stops": {"0": {"reason": "asked", "response": "information", "gist": "explained the matching rule"}},
      "segments": [{"from": 0, "to": 5, "shape": "cluster", "label": "interview"}]
    }
  },
  "findings": [{"title": "…", "remedy_type": "verification", "body": "…with counts…", "fix": "…exact rule or setting…",
                "evidence": [{"session": "<id>", "from": 0, "to": 4}]}]
}
```

Run and stop keys are run indexes; stop `i` is the stop that ends run `i`.
The codebook lists only the names used in this report. Count one- or two-run
sessions but don't label them unless they show something unusual. For more
than ~300 runs, label in batches of sessions.

## 5. Write Claude's read

Look across sessions and patterns. Count before claiming. Questions worth
answering:

- Which patterns recur, and which ones carry the forced stops?
- What does a session that went well look like next to one that didn't? Sessions on the same task, or on the same git branch, make the best comparisons.
- What do the kickoffs of long runs and closed loops have in common?
- What are the recurring rework and decision themes?
- What ended each long run?

Write 3 to 7 findings, most useful first. Each names its evidence (counts,
patterns by name, and `evidence` ranges so the page can highlight them) and a
concrete fix tagged with a `remedy_type`: guidance, skill, script,
verification, access or workflow. Use exact text where it fits: allow rules
built from the real commands, CLAUDE.md lines, or a skill to extract. Note
anything the person already fixed during the period.

## 6. Record and render

```
python3 scripts/patterns.py record labels.json
python3 scripts/render.py sessions.json labels.json -o defrag.html
```

`record` adds this report's pattern names to the library and notes how many
were reused and how many are new. A vocabulary that has settled shows few new
names per report. Open the page for the person, or publish it as an artifact
if that's available. Then reply with the top three findings and their fixes
in a few lines, and mention any new pattern names. Offer to apply a fix
(settings, CLAUDE.md), and only edit those files when the person says yes.

## 7. Share mode (optional)

When the person wants to discuss results somewhere their transcripts can't go:

```
python3 scripts/share.py sessions.json labels.json -o defrag-share.md
```

This keeps only shapes, patterns, stop reasons, timings, command families,
themes, gists, the vocabulary and findings. Tell the person to read it before
sharing, because the text fields are written by you and could still carry
specifics.

## Testing

`scripts/synth.py OUT_DIR` writes synthetic Claude Code transcripts that
exercise every stop kind, compaction, notifications and an expired API login.
