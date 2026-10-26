#!/usr/bin/env python3
"""Keep the work and pattern vocabulary stable across defrag reports.

The library lives outside any repo (default ~/.claude/defrag/patterns.json) and
starts from references/patterns-seed.json. Each report reuses names that fit
and records any new ones, so the library shows whether a small vocabulary of
patterns is emerging or every report keeps inventing new names.

Usage:
  patterns.py show [--library PATH]                 print the vocabulary to label with
  patterns.py record labels.json [--library PATH]   add this report's names, update counts,
                                                    and write the reused/new tally into labels.json
"""
import argparse, json, os, sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(HERE, '..', 'references', 'patterns-seed.json')
DEFAULT = os.path.expanduser('~/.claude/defrag/patterns.json')


def load(path):
    if os.path.exists(path):
        return json.load(open(path))
    lib = json.load(open(SEED))
    lib.setdefault('reports', [])
    for p in lib['patterns']:
        p.setdefault('seen', 0)
    return lib


def show(lib):
    print('Work: what a run was for')
    for w in lib['work']:
        print('  %-10s %s' % (w['label'], w['definition']))
    print('\nShapes: %s' % ', '.join('%s (%s)' % (k, v) for k, v in lib['shapes'].items()))
    print('\nPatterns (seen = occurrences across past reports)')
    for p in sorted(lib['patterns'], key=lambda p: -p.get('seen', 0)):
        print('  %-22s [%s] seen %d: %s' % (p['label'], p['shape'], p.get('seen', 0), p['definition']))
    for r in lib['reports'][-5:]:
        print('\nReport %s: %d sessions, %d patterns reused, new: %s' % (r['date'], r['sessions'], r['reused'], ', '.join(r['new']) or 'none'))


def record(lib, labels_path):
    labels = json.load(open(labels_path))
    known = {p['label']: p for p in lib['patterns']}
    defs = {d['label']: d for d in (labels.get('codebook') or {}).get('segments', [])}
    today, reused, new = date.today().isoformat(), set(), []
    for s in labels.get('sessions', {}).values():
        for g in s.get('segments', []):
            p = known.get(g['label'])
            if p is None:
                d = defs.get(g['label'], {})
                p = known[g['label']] = {'label': g['label'], 'shape': g.get('shape') or d.get('shape', '?'),
                                         'definition': d.get('definition', ''), 'seen': 0, 'first_seen': today}
                lib['patterns'].append(p)
                new.append(g['label'])
            elif g['label'] not in new:
                reused.add(g['label'])
            p['seen'] = p.get('seen', 0) + 1
            p['last_seen'] = today
    known_work = {w['label'] for w in lib['work']}
    for w in (labels.get('codebook') or {}).get('work', []):
        if w['label'] not in known_work:
            lib['work'].append({'label': w['label'], 'definition': w.get('definition', ''), 'first_seen': today})
    lib['reports'].append({'date': today, 'sessions': len(labels.get('sessions', {})), 'reused': len(reused), 'new': new})
    labels['library'] = {'reused': len(reused), 'new': new}
    json.dump(labels, open(labels_path, 'w'), indent=1)
    return reused, new


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('command', choices=('show', 'record'))
    ap.add_argument('labels', nargs='?')
    ap.add_argument('--library', default=DEFAULT)
    a = ap.parse_args()
    lib = load(a.library)
    if a.command == 'show':
        show(lib)
        return
    if not a.labels:
        sys.exit('record needs labels.json')
    reused, new = record(lib, a.labels)
    os.makedirs(os.path.dirname(os.path.abspath(a.library)), exist_ok=True)
    json.dump(lib, open(a.library, 'w'), indent=1)
    print('%d patterns reused, %d new (%s) -> %s' % (len(reused), len(new), ', '.join(new) or 'none', a.library), file=sys.stderr)


if __name__ == '__main__':
    main()
