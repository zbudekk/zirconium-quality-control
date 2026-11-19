import os, re, difflib
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'wyniki_v2', 'raport'))
a = open(os.path.join(R, 'raport_wykonawcy_SPRAWDZ_iter12.md'), encoding='utf-8').read().splitlines()
b = open(os.path.join(R, 'raport_wykonawcy_SPRAWDZ_iter15.md'), encoding='utf-8').read().splitlines()
d = [l for l in difflib.unified_diff(a, b, lineterm='', n=0) if l.startswith(('+', '-')) and not l.startswith(('+++', '---'))]
print('linii roznych:', len(d))
for l in d[:60]:
    print(l[:300])