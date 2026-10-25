#!/usr/bin/env python3
"""Write a content-free summary of a defrag run that can leave the machine.

Keeps: session shapes, the core handoff answers, labels, the codebook, timings,
mid-run handoff kinds, the first word(s) of permission-prompted commands,
gists, themes and findings. Drops: prompts, agent messages, paths, titles,
branch names and full commands.

Usage: share.py sessions.json labels.json [-o defrag-share.md] [--no-gists]
"""
import argparse, collections, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import merge  # noqa: E402

CORE = {'information': 'I', 'approval': 'A', 'rework': 'R', 'other': 'O'}
MULTI = ('git', 'npm', 'npx', 'yarn', 'pnpm', 'bundle', 'bin/rails', 'rails', 'python3', 'python',
         'docker', 'gh', 'make', 'cargo', 'go', 'kubectl', 'aws', 'gcloud')


def family(cmd):
    w = (cmd or '').replace('\\ ', '_').split()
    if not w:
        return '?'
    head = os.path.basename(w[0])
    return head + (' ' + w[1] if head in MULTI and len(w) > 1 and not w[1].startswith(('/', '-', '.')) else '')


def code(t):
    if t['index'] == 0:
        return 'K'
    c = CORE.get(t.get('contribution'), '?')
    return c + ('+' if t.get('could_continue') == 'yes' else '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sessions')
    ap.add_argument('labels')
    ap.add_argument('-o', '--out', default='defrag-share.md')
    ap.add_argument('--no-gists', action='store_true')
    a = ap.parse_args()
    labels = json.load(open(a.labels))
    S = merge(json.load(open(a.sessions)), labels)

    lab, core, cont, mid, fam, themes = (collections.Counter() for _ in range(6))
    branch_alias, lines = {}, []
    for i, s in enumerate(S, 1):
        for t in s['turns'][1:]:
            lab[t.get('label') or '?'] += 1
            core['%s/%s' % (t.get('could_continue') or '?', t.get('contribution') or '?')] += 1
            if t.get('theme'):
                themes[t['theme']] += 1
        for t in s['turns']:
            for h in t['handoffs']:
                mid[h['kind']] += 1
                if h['kind'] == 'permission':
                    fam[family(h.get('command'))] += 1
        br = ','.join(branch_alias.setdefault(b, 'branch-%s' % chr(65 + len(branch_alias)))
                      for b in s['meta'].get('branches', []) if b not in ('main', 'master'))
        m = s['meta']
        lines.append('### Session %d · %s · %s%s' % (i, m['start'][:10], m['source'], ' · ' + br if br else ''))
        lines.append('- %s%d turns · %.0f agent min · longest run %.0f min · %d mid-run handoffs · %d subagents · %d access errors · %d auto-denied' % (
            'pattern: %s · ' % s['pattern'] if s.get('pattern') else '', len(s['turns']), m['agent_s'] / 60,
            m.get('longest_run_s', 0) / 60, m['mid_run_handoffs'], m.get('subagents', 0), m.get('access_errors', 0),
            sum(len(t.get('auto_denied', [])) for t in s['turns'])))
        lines.append('- shape: `%s`' % ' '.join(code(t) + ('*%d' % len(t['handoffs']) if t['handoffs'] else '') for t in s['turns']))
        lines.append('- runs (min): %s' % ' '.join('%.0f' % (t['run_s'] / 60) for t in s['turns']))
        lines.append('- human gaps (min): %s' % ' '.join('%.0f' % (t['human_gap_s'] / 60) for t in s['turns'] if t['human_gap_s'] is not None))
        if not a.no_gists:
            if s.get('summary'):
                lines.append('- about: %s' % s['summary'])
            for t in s['turns'][1:]:
                bits = [t.get('label') or '?']
                if t.get('why_stopped'):
                    bits.append('stopped: ' + t['why_stopped'])
                if t.get('theme'):
                    bits.append('theme: ' + t['theme'])
                lines.append('  - %d %s · %s%s' % (t['index'], code(t), ' · '.join(bits), (': ' + t['gist']) if t.get('gist') else ''))
        lines.append('')

    out = ['# Defrag share summary', '',
           'Shape codes: K kickoff; then what the human added: I information, A approval only, R rework, O other. '
           '`+` = the agent could have continued without the human. `*n` = n mid-run handoffs.', '',
           '## Totals', '',
           '- sessions: %d' % len(S),
           '- could continue / human added: ' + ', '.join('%s %d' % kv for kv in core.most_common()),
           '- labels: ' + ', '.join('%s %d' % kv for kv in lab.most_common()),
           '- mid-run handoffs: ' + ', '.join('%s %d' % kv for kv in mid.most_common()),
           '- permission prompts by command family: ' + ', '.join('%s %d' % kv for kv in fam.most_common(12)),
           '- recurring themes: ' + ', '.join('%s (%d)' % kv for kv in themes.most_common(15)), '']
    if labels.get('codebook'):
        out += ['## Codebook', '']
        out += ['- **%s** (%d): %s' % (c['label'], lab.get(c['label'], 0), c.get('definition', '')) for c in labels['codebook']]
        out.append('')
    if labels.get('hard_cases'):
        out += ['## Hard to code', ''] + ['- ' + h for h in labels['hard_cases']] + ['']
    if labels.get('findings'):
        out += ['## Findings', '']
        for f in labels['findings']:
            out.append('- **%s** [%s] %s %s' % (f.get('title', ''), f.get('remedy_type', '?'), f.get('body', ''), f.get('fix', '')))
        out.append('')
    out += ['## Sessions', ''] + lines
    open(a.out, 'w').write('\n'.join(out))
    print('wrote', a.out, '- read it before sharing; gists, themes and the codebook are model-written')


if __name__ == '__main__':
    main()
