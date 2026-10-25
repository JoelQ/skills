#!/usr/bin/env python3
"""Merge extracted sessions with labels and write the defrag report page.

Usage: render.py sessions.json labels.json [-o defrag.html] [--title TITLE]
"""
import argparse, json, os


TURN_FIELDS = ('label', 'could_continue', 'contribution', 'why_stopped', 'gist', 'theme')


def merge(sessions, labels):
    out = []
    by_id = labels.get('sessions', {})
    for s in sessions['sessions']:
        lab = by_id.get(s['meta'].get('id') or '') or by_id.get(s['meta']['file']) or {}
        tl = lab.get('turns', {})
        for t in s['turns']:
            l = tl.get(str(t['index']), {})
            for k in TURN_FIELDS:
                t[k] = l.get(k)
        out.append({'meta': s['meta'], 'turns': s['turns'], 'pattern': lab.get('pattern'),
                    'summary': lab.get('summary')})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sessions')
    ap.add_argument('labels')
    ap.add_argument('-o', '--out', default='defrag.html')
    ap.add_argument('--title')
    a = ap.parse_args()
    labels = json.load(open(a.labels))
    data = {'title': a.title or labels.get('title'), 'findings': labels.get('findings', []),
            'codebook': labels.get('codebook', []), 'hard_cases': labels.get('hard_cases', []),
            'sessions': merge(json.load(open(a.sessions)), labels)}
    tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html')).read()
    blob = json.dumps(data).replace('</', '<\\/')
    open(a.out, 'w').write(tpl.replace('__DATA__', blob))
    print('wrote', a.out)


if __name__ == '__main__':
    main()
