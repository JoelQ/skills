#!/usr/bin/env python3
"""Merge extracted runs with labels and write the defrag report page.

Usage: render.py sessions.json labels.json [-o defrag.html] [--title TITLE]
"""
import argparse, json, os


RUN_FIELDS = ('work', 'confidence', 'gist')
STOP_FIELDS = ('reason', 'response', 'gist', 'theme')


def merge(sessions, labels):
    out = []
    by_id = labels.get('sessions', {})
    for s in sessions['sessions']:
        lab = by_id.get(s['meta'].get('id') or '') or by_id.get(s['meta']['file']) or {}
        rl, sl = lab.get('runs', {}), lab.get('stops', {})
        for r in s['runs']:
            l = rl.get(str(r['index']), {})
            for k in RUN_FIELDS:
                r[k] = l.get(k)
            l = sl.get(str(r['index']), {})
            for k in STOP_FIELDS:
                r['stop'][k] = l.get(k)
            r['stop']['reason'] = r['stop']['reason'] or r['stop']['kind']
        out.append({'meta': s['meta'], 'runs': s['runs'], 'summary': lab.get('summary'),
                    'segments': lab.get('segments', [])})
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
            'codebook': labels.get('codebook', {}), 'hard_cases': labels.get('hard_cases', []),
            'sessions': merge(json.load(open(a.sessions)), labels)}
    tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html')).read()
    blob = json.dumps(data).replace('</', '<\\/')
    open(a.out, 'w').write(tpl.replace('__DATA__', blob))
    print('wrote', a.out)


if __name__ == '__main__':
    main()
