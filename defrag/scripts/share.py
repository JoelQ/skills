#!/usr/bin/env python3
"""Write a content-free summary of a defrag run that can leave the machine.

Keeps: session shapes (work per run, soft and forced stops), patterns, stop
reasons, what the human brought back, timings, the first word(s) of
permission-prompted commands, gists, themes, the vocabulary and findings.
Drops: prompts, agent messages, paths, titles, branch names and full commands.

Usage: share.py sessions.json labels.json [-o defrag-share.md] [--no-gists]
"""
import argparse, collections, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import codebook, merge  # noqa: E402

MULTI = ('git', 'npm', 'npx', 'yarn', 'pnpm', 'bundle', 'bin/rails', 'rails', 'python3', 'python',
         'docker', 'gh', 'make', 'cargo', 'go', 'kubectl', 'aws', 'gcloud')


def family(cmd):
    w = (cmd or '').replace('\\ ', '_').split()
    if not w:
        return '?'
    head = os.path.basename(w[0])
    return head + (' ' + w[1] if head in MULTI and len(w) > 1 and not w[1].startswith(('/', '-', '.')) else '')


def letters(work_labels):
    """One letter per work label, so a session's shape fits on one line."""
    out, used = {}, set()
    for l in work_labels:
        for c in (l[:1].upper(), l[1:2].upper(), *'XYZQWJK'):
            if c and c not in used:
                out[l] = c
                used.add(c)
                break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sessions')
    ap.add_argument('labels')
    ap.add_argument('-o', '--out', default='defrag-share.md')
    ap.add_argument('--no-gists', action='store_true')
    a = ap.parse_args()
    labels = json.load(open(a.labels))
    S = merge(json.load(open(a.sessions)), labels)
    cb = codebook(labels)

    work, reasons, hard, resp, fam, themes, pats = (collections.Counter() for _ in range(7))
    for s in S:
        for r in s['runs']:
            work[r.get('work') or '?'] += 1
            st = r['stop']
            if st['kind'] == 'last':
                continue
            reasons[st.get('reason') or st['kind']] += 1
            resp[st.get('response') or '?'] += 1
            if st.get('hard'):
                hard[st['hard']] += 1
            if st['kind'] == 'permission':
                fam[family(st.get('command'))] += 1
            if st.get('theme'):
                themes[st['theme']] += 1
        for g in s.get('segments', []):
            pats[g['label']] += 1
    order = [w['label'] for w in cb.get('work', [])] + [w for w, _ in work.most_common()]
    code = letters(dict.fromkeys(order))

    branch_alias, lines = {}, []
    for i, s in enumerate(S, 1):
        m, runs = s['meta'], s['runs']
        br = ','.join(branch_alias.setdefault(b, 'branch-%s' % chr(65 + len(branch_alias)))
                      for b in m.get('branches', []) if b not in ('main', 'master'))
        shape = ''
        for r in runs:
            shape += code.get(r.get('work'), '?') + ('~' if r.get('confidence') == 'low' else '')
            if r['stop']['kind'] != 'last':
                shape += ' ! ' if r['stop'].get('hard') else ' | '
        lines.append('### Session %d · %s · %s · %s%s' % (i, m['start'][:10], m['source'], m.get('group', '?'), ' · ' + br if br else ''))
        lines.append('- %d runs · %d stops (%d forced) · %.0f agent min · longest run %.0f min · %d subagents · %d compactions' % (
            len(runs), m.get('stops', 0), m.get('hard_stops', 0), m['agent_s'] / 60, m.get('longest_run_s', 0) / 60,
            m.get('subagents', 0), m.get('compactions', 0)))
        lines.append('- shape: `%s`' % shape)
        if s.get('segments'):
            lines.append('- patterns: ' + ', '.join('%s [%s, runs %d-%d]' % (g['label'], g.get('shape', '?'), g['from'], g['to'])
                                                     for g in s['segments']))
        lines.append('- runs (min): %s' % ' '.join('%.0f' % (r['run_s'] / 60) for r in runs))
        lines.append('- waits (min): %s' % ' '.join('%.0f' % ((r['stop'].get('wait_s') or 0) / 60)
                                                     for r in runs if r['stop']['kind'] != 'last'))
        if not a.no_gists:
            if s.get('summary'):
                lines.append('- about: %s' % s['summary'])
            for r in runs:
                st, bits = r['stop'], []
                if st['kind'] == 'last':
                    continue
                bits.append(('forced: %s' % st['hard']) if st.get('hard') else 'handed back')
                bits.append(st.get('reason') or st['kind'])
                if st.get('response'):
                    bits.append('you: ' + st['response'])
                if st.get('theme'):
                    bits.append('theme: ' + st['theme'])
                lines.append('  - after run %d (%s) · %s%s' % (r['index'], r.get('work') or '?', ' · '.join(bits),
                                                            (': ' + st['gist']) if st.get('gist') else ''))
        lines.append('')

    legend = ', '.join('%s %s' % (c, l) for l, c in code.items() if work.get(l))
    out = ['# Defrag share summary', '',
           'Shape: one letter per run for what it was for (%s); `~` marks an unsure label. '
           '`|` is the agent handing back, `!` is a forced stop.' % legend, '',
           '## Totals', '',
           '- sessions: %d · runs: %d · stops: %d · forced: %d' % (len(S), sum(work.values()), sum(reasons.values()), sum(hard.values())),
           '- groups: ' + ', '.join('%s %d' % kv for kv in collections.Counter(s['meta'].get('group', '?') for s in S).most_common()),
           '- runs by work: ' + ', '.join('%s %d' % kv for kv in work.most_common()),
           '- stop reasons: ' + ', '.join('%s %d' % kv for kv in reasons.most_common()),
           '- forced stops: ' + ', '.join('%s %d' % kv for kv in hard.most_common()),
           '- what you brought back: ' + ', '.join('%s %d' % kv for kv in resp.most_common()),
           '- permission prompts by command family: ' + ', '.join('%s %d' % kv for kv in fam.most_common(12)),
           '- patterns: ' + ', '.join('%s %d' % kv for kv in pats.most_common()),
           '- recurring themes: ' + ', '.join('%s (%d)' % kv for kv in themes.most_common(15))]
    if labels.get('library'):
        lib = labels['library']
        out.append('- pattern library: %d reused, %d new this report (%s)' % (
            lib.get('reused', 0), len(lib.get('new', [])), ', '.join(lib.get('new', [])) or 'none'))
    out.append('')
    if cb.get('work') or cb.get('segments'):
        out += ['## Vocabulary', '']
        out += ['- **%s** (%d runs): %s' % (c['label'], work.get(c['label'], 0), c.get('definition', '')) for c in cb.get('work', [])]
        out += ['- pattern **%s** [%s] (%d): %s' % (c['label'], c.get('shape', '?'), pats.get(c['label'], 0), c.get('definition', ''))
                for c in cb.get('segments', [])]
        out.append('')
    if labels.get('hard_cases'):
        out += ['## Hard to label', ''] + ['- ' + h for h in labels['hard_cases']] + ['']
    kind = lambda f: f.get('kind') or ('suggestion' if f.get('fix') else 'observation')
    for head, k in (('What stands out', 'observation'), ('Things to try', 'suggestion')):
        fs = [f for f in labels.get('findings', []) if kind(f) == k]
        if fs:
            out += ['## ' + head, '']
            out += ['- **%s**%s %s %s' % (f.get('title', ''), ' [%s]' % f['remedy_type'] if f.get('remedy_type') else '',
                                          f.get('body', ''), f.get('fix', '')) for f in fs]
            out.append('')
    out += ['## Sessions', ''] + lines
    open(a.out, 'w').write('\n'.join(out))
    print('wrote', a.out, '- read it before sharing; gists, themes and the vocabulary are model-written')


if __name__ == '__main__':
    main()
