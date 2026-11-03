# -*- coding: utf-8 -*-
"""Audyt kluczy parametry.json <-> ramka_generator.py (bez bpy; dowolny Python 3.10+).

Użycie:  python audyt_kluczy.py [katalog Ramki]
Wypisuje: klucze w WYMAGANE_KLUCZE a nie w JSON, w JSON a nie w WYMAGANE_KLUCZE, klucze JSON nigdy nie czytane
w kodzie (martwe), klucze czytane w kodzie a nieistniejące w JSON, klucze DO_ZMIERZENIA i LICZONE z użyciem.
"""
import json, re, sys, os, collections

KAT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')
src = open(os.path.join(KAT, 'ramka_generator.py'), encoding='utf-8').read()
dane = json.load(open(os.path.join(KAT, 'parametry.json'), encoding='utf-8'))
flat, status, wzory = {}, {}, {}
for s, z in dane.items():
    if s.startswith('_'):
        continue
    for k, v in z.items():
        flat[k] = v.get('value')
        status[k] = v.get('status')
        if 'wzor' in v:
            wzory[k] = v['wzor']
m = re.search(r"WYMAGANE_KLUCZE = \{(.*?)\n\}", src, re.S)
wym = set(re.findall(r"'([a-zA-Z_0-9]+)'", m.group(1)))
used = collections.Counter()
for mm in re.finditer(r"P\[['\"]([a-zA-Z_0-9]+)['\"]\]", src):
    used[mm.group(1)] += 1
for mm in re.finditer(r"P\.get\(['\"]([a-zA-Z_0-9]+)['\"]", src):
    used[mm.group(1)] += 1
w_wzorach = collections.Counter()
for k, w in wzory.items():
    for t in re.findall(r"[a-zA-Z_][a-zA-Z_0-9]*", w):
        if t in flat:
            w_wzorach[t] += 1
print('WYMAGANE_KLUCZE: %d, klucze JSON: %d' % (len(wym), len(flat)))
print('w WYMAGANE a nie w JSON:', sorted(wym - set(flat)) or 'brak')
print('w JSON a nie w WYMAGANE:', sorted(set(flat) - wym) or 'brak')
print('czytane w kodzie a nie w JSON:', sorted(set(used) - set(flat)) or 'brak')
dyn = [l.strip() for l in src.splitlines() if re.search(r"P\[[^'\"]", l) and 'def ' not in l]
print('dynamiczne P[...] (do ręcznego sprawdzenia): %d linii' % len(dyn))
martwe = sorted(k for k in flat if k not in used)
print('\nKlucze JSON nigdy nie czytane literalnie w kodzie (%d):' % len(martwe))
for k in martwe:
    print('  %-24s status %-13s %s' % (k, status[k], ('tylko w polu wzor (%s)' % ', '.join(n for n, w in wzory.items() if re.search(r'\b%s\b' % k, w))) if w_wzorach[k] else 'MARTWY'))
print('\nDO_ZMIERZENIA (%d):' % sum(1 for s in status.values() if s == 'DO_ZMIERZENIA'))
for k in flat:
    if status[k] == 'DO_ZMIERZENIA':
        print('  %-24s użyć w kodzie: %d, w wzorach: %d' % (k, used[k], w_wzorach[k]))
print('\nLICZONE:')
for k, w in wzory.items():
    print('  %-18s = %s' % (k, w))
