#!/usr/bin/env python3
"""Turn Claude Code or Codex transcripts into a list of turns and handoffs.

Output is one JSON document: {"sessions": [...]}. Each session holds turns; each
turn is one agent run started by a human prompt, plus the mid-run handoffs
(permission prompts, clarifying questions, plan approvals) that happened inside it.

Usage:
  extract.py [PATHS...] [--since 2026-09-01] [--min-turns 3] [-o sessions.json]

PATHS may be .jsonl files or directories (searched recursively). With no PATHS,
the Claude Code project folder for the current directory is used.
"""
import argparse, glob, json, os, re, sys
from datetime import datetime, timezone

TEXT_LIMIT = 600  # characters of human/agent text kept for labelling


def ts(s):
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s) / (1000 if s > 1e11 else 1)
    return datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()


def iso(t):
    return datetime.fromtimestamp(t, timezone.utc).isoformat().replace('+00:00', 'Z') if t else None


def clip(s, n=TEXT_LIMIT):
    s = ' '.join((s or '').split())
    return s if len(s) <= n else s[: n - 1] + '…'


def read_jsonl(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def new_turn(start, text):
    return {'start': start, 'end': start, 'prompt': clip(text), 'prior_agent_message': '',
            'tools': 0, 'tool_errors': 0, 'subagents': 0, 'interrupted': False, 'handoffs': [],
            'access_errors': [], 'auto_denied': []}


# Errors that mean the agent needs a human to log in or grant access
ACCESS = re.compile(r'\b(401|403)\b|unauthori[sz]ed|forbidden|expired (token|session|credentials)|token (has )?expired'
                    r'|(please|need to|must) (log ?in|login|sign in|authenticate)|not (logged|signed) in'
                    r'|authentication (failed|required|error)|re-?authenticate|sso login|mfa|permission denied \(publickey\)', re.I)
SUBAGENT_TOOLS = {'Task', 'Agent'}


def access_error(body):
    m = ACCESS.search(body or '')
    if not m:
        return None
    a = max(0, m.start() - 80)
    return clip(body[a:m.end() + 80], 200)


# ---------------------------------------------------------------- Claude Code

LOCAL_CMD = re.compile(r'^\s*<(command-name|command-message|local-command-(stdout|stderr|caveat))>')
INTERRUPT = re.compile(r'^\[Request interrupted by user')
REJECTED = re.compile(r"doesn't want to proceed|user (rejected|denied)|was rejected", re.I)
ASK_TOOLS = {'AskUserQuestion'}
PLAN_TOOLS = {'ExitPlanMode'}


REMINDER = re.compile(r'<system-reminder>.*?</system-reminder>', re.S)


def cc_text(content):
    if isinstance(content, list):
        content = '\n'.join(c.get('text', '') for c in content if isinstance(c, dict) and c.get('type') == 'text')
    return REMINDER.sub('', content).strip() if isinstance(content, str) else ''


def parse_claude_code(path):
    meta = {'source': 'claude-code', 'file': os.path.basename(path), 'id': None, 'cwd': None,
            'title': None, 'permission_modes': set(), 'local_commands': [], 'branches': set()}
    turns, cur, pending, last_agent_text = [], None, {}, ''
    for d in read_jsonl(path):
        t = d.get('type')
        if t in ('ai-title', 'custom-title'):
            meta['title'] = d.get('aiTitle') or d.get('customTitle') or d.get('title') or meta['title']
            continue
        if d.get('permissionMode'):
            meta['permission_modes'].add(d['permissionMode'])
        if t == 'permission-mode' and d.get('permissionMode'):
            meta['permission_modes'].add(d['permissionMode'])
        if t not in ('user', 'assistant') or d.get('isSidechain'):
            continue
        meta['id'] = meta['id'] or d.get('sessionId')
        if d.get('gitBranch') and d['gitBranch'] != 'HEAD':
            meta['branches'].add(d['gitBranch'])
        meta['cwd'] = meta['cwd'] or d.get('cwd')
        now = ts(d.get('timestamp'))
        content = (d.get('message') or {}).get('content')

        if t == 'assistant':
            for c in content if isinstance(content, list) else []:
                if c.get('type') == 'tool_use':
                    pending[c.get('id')] = (now, c.get('name'), c.get('input') or {})
                    if cur:
                        cur['tools'] += 1
                        cur['subagents'] += c.get('name') in SUBAGENT_TOOLS
                elif c.get('type') == 'text' and c.get('text', '').strip():
                    last_agent_text = c['text']
            if cur and now:
                cur['end'] = max(cur['end'], now)
            continue

        # user entries: tool results, real prompts, local commands, meta injections
        blocks = content if isinstance(content, list) else []
        results = [c for c in blocks if isinstance(c, dict) and c.get('type') == 'tool_result']
        if results:
            for r in results:
                call = pending.pop(r.get('tool_use_id'), None)
                if not cur:
                    continue
                cur['end'] = max(cur['end'], now or cur['end'])
                body = r.get('content')
                body = body if isinstance(body, str) else json.dumps(body)
                if r.get('is_error'):
                    cur['tool_errors'] += 1
                if not call:
                    continue
                started, name, args = call
                wait = round((now or started) - started, 1)
                decision = d.get('permissionDecision') or {}
                err = access_error(body[:4000]) if (r.get('is_error') or name in ('Bash', 'WebFetch') or name.startswith('mcp__')) else None
                if err:
                    cur['access_errors'].append({'tool': name, 'text': err})
                if decision.get('source') == 'config' and decision.get('decision') not in (None, 'accept', 'allow'):
                    cur['auto_denied'].append({'tool': name, 'command': clip(args.get('command') or '', 160),
                                               'reason': decision.get('reasonType')})
                rejected = bool(r.get('is_error') and REJECTED.search(body[:400]))
                if name in ASK_TOOLS:
                    cur['handoffs'].append({'kind': 'question', 'at': iso(started), 'wait_s': wait,
                                            'detail': clip(json.dumps(args), 300)})
                elif name in PLAN_TOOLS:
                    cur['handoffs'].append({'kind': 'plan-approval', 'at': iso(started), 'wait_s': wait,
                                            'rejected': rejected})
                elif rejected or (decision and decision.get('source') not in (None, 'config')):
                    cur['handoffs'].append({'kind': 'permission', 'at': iso(started), 'wait_s': wait,
                                            'tool': name, 'command': clip(args.get('command') or args.get('file_path') or '', 160),
                                            'rejected': rejected or decision.get('decision') in ('reject', 'deny')})
            continue
        if d.get('isMeta'):
            continue
        text = cc_text(content)
        if not text.strip():
            continue
        if LOCAL_CMD.match(text):
            m = re.search(r'<command-name>([^<]+)</command-name>', text)
            if m:
                meta['local_commands'].append(m.group(1).strip())
            continue
        if INTERRUPT.match(text):
            if cur:
                cur['interrupted'] = True
            continue
        cur = new_turn(now, text)
        cur['prior_agent_message'] = clip(last_agent_text, 400)
        turns.append(cur)
    meta['permission_modes'] = sorted(meta['permission_modes'])
    meta['branches'] = sorted(meta['branches'])
    return meta, turns


# ---------------------------------------------------------------------- Codex

def parse_codex(path):
    meta = {'source': 'codex', 'file': os.path.basename(path), 'id': None, 'cwd': None, 'title': None,
            'permission_modes': set(), 'local_commands': [], 'branches': []}
    turns, cur, calls, last_agent_text = [], None, {}, ''
    for d in read_jsonl(path):
        t, p = d.get('type'), d.get('payload') or {}
        now = ts(d.get('timestamp'))
        if t == 'session_meta':
            meta['id'], meta['cwd'] = p.get('id'), p.get('cwd')
        elif t == 'turn_context':
            meta['permission_modes'].add('%s/%s' % (p.get('approval_policy'), (p.get('sandbox_policy') or {}).get('type')))
        elif t == 'event_msg' and p.get('type') == 'task_started':
            cur = new_turn(now, '')
            cur['prior_agent_message'] = clip(last_agent_text, 400)
            cur['mode'] = p.get('collaboration_mode_kind')
            turns.append(cur)
        elif not cur:
            continue
        elif t == 'event_msg' and p.get('type') == 'item_completed':
            item = p.get('item') or {}
            if item.get('type') == 'UserMessage' and not cur['prompt']:
                cur['prompt'] = clip('\n'.join(c.get('text', '') for c in item.get('content', []) if c.get('type') == 'text'))
        elif t == 'event_msg' and p.get('type') in ('task_complete', 'turn_aborted'):
            cur['end'] = now
            cur['interrupted'] = p.get('type') == 'turn_aborted'
            last_agent_text = p.get('last_agent_message') or last_agent_text
        elif t == 'response_item':
            pt = p.get('type')
            if pt in ('function_call', 'custom_tool_call'):
                cur['tools'] += 1
                cur['subagents'] += 'agent' in (p.get('name') or '')
                args = p.get('arguments') or ''
                calls[p.get('call_id')] = (now, 'require_escalated' in args, args)
            elif pt in ('function_call_output', 'custom_tool_call_output'):
                c = calls.pop(p.get('call_id'), None)
                out = p.get('output') if isinstance(p.get('output'), str) else json.dumps(p.get('output'))
                if c and c[1]:
                    try:
                        a = json.loads(c[2])
                        cmd = a.get('cmd') or a.get('command') or ''
                        cmd = ' '.join(cmd) if isinstance(cmd, list) else cmd
                    except ValueError:
                        cmd = ''
                    cur['handoffs'].append({'kind': 'permission', 'at': iso(c[0]), 'wait_s': round(now - c[0], 1),
                                            'tool': 'shell', 'command': clip(cmd, 160),
                                            'rejected': bool(re.search(r'rejected|declined', (out or '')[:300], re.I))})
                if out and re.search(r'exited with code [1-9]', out[:300]):
                    cur['tool_errors'] += 1
                    err = access_error(out[:4000])
                    if err:
                        cur['access_errors'].append({'tool': 'shell', 'text': err})
            if now:
                cur['end'] = max(cur['end'], now)
    meta['permission_modes'] = sorted(meta['permission_modes'])
    return meta, turns


# ----------------------------------------------------------------------- main

def sniff(path):
    for d in read_jsonl(path):
        if d.get('type') in ('session_meta', 'response_item', 'event_msg', 'turn_context'):
            return parse_codex
        if d.get('type') in ('user', 'assistant', 'summary', 'queue-operation', 'mode', 'permission-mode'):
            return parse_claude_code
    return None


def default_paths():
    slug = re.sub(r'[^A-Za-z0-9]', '-', os.getcwd())
    return [os.path.expanduser('~/.claude/projects/' + slug)]


def expand(paths):
    for p in paths:
        p = os.path.expanduser(p)
        if os.path.isdir(p):
            for f in sorted(glob.glob(os.path.join(p, '**', '*.jsonl'), recursive=True)):
                if '/subagents/' not in f:
                    yield f
        elif p.endswith('.jsonl'):
            yield p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='*')
    ap.add_argument('--since', help='only sessions starting on or after this date (YYYY-MM-DD)')
    ap.add_argument('--min-turns', type=int, default=1)
    ap.add_argument('-o', '--out', default='-')
    a = ap.parse_args()
    since = ts(a.since + 'T00:00:00Z') if a.since else None
    sessions = []
    for f in expand(a.paths or default_paths()):
        parser = sniff(f)
        if not parser:
            continue
        meta, turns = parser(f)
        turns = [t for t in turns if t['start']]
        if len(turns) < a.min_turns or (since and turns[0]['start'] < since):
            continue
        for i, t in enumerate(turns):
            t['index'] = i
            t['run_s'] = round(t['end'] - t['start'], 1)
            nxt = turns[i + 1]['start'] if i + 1 < len(turns) else None
            t['human_gap_s'] = round(nxt - t['end'], 1) if nxt else None
            t['start'], t['end'] = iso(t['start']), iso(t['end'])
        meta['start'] = turns[0]['start']
        meta['turn_count'] = len(turns)
        meta['agent_s'] = round(sum(t['run_s'] for t in turns), 1)
        meta['mid_run_handoffs'] = sum(len(t['handoffs']) for t in turns)
        meta['longest_run_s'] = max(t['run_s'] for t in turns)
        meta['subagents'] = sum(t['subagents'] for t in turns)
        meta['access_errors'] = sum(len(t['access_errors']) for t in turns)
        sessions.append({'meta': meta, 'turns': turns})
    sessions.sort(key=lambda s: s['meta']['start'])
    doc = json.dumps({'sessions': sessions}, indent=1)
    if a.out == '-':
        print(doc)
    else:
        open(a.out, 'w').write(doc)
        print('%d sessions, %d turns -> %s' % (len(sessions), sum(len(s['turns']) for s in sessions), a.out), file=sys.stderr)


if __name__ == '__main__':
    main()
