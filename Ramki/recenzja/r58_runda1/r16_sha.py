import sys, os, re, hashlib, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import sha, STL_NEW, STL_OLD
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# 1. sha256_stl_po_R58.txt
txt = open(os.path.join(R, 'wyniki_v2', 'raport', 'sha256_stl_po_R58.txt'), encoding='utf-8').read()
print('--- sha256_stl_po_R58.txt')
for line in txt.splitlines():
    line = line.strip()
    if not line: continue
    h, f = line.split(None, 1); f = f.lstrip('*')
    p = os.path.join(R, 'wyniki_v2', f)
    act = sha(p) if os.path.isfile(p) else 'BRAK'
    print('OK ' if act == h else 'ZLE', f, h[:16], act[:16])
# 2. R58_wdrozenie_zmiany.md tabela
doc = open(os.path.join(R, 'R58_wdrozenie_zmiany.md'), encoding='utf-8').read()
print('--- R58_wdrozenie_zmiany.md')
for m in re.finditer(r'\|\s*`([^`]+\.(?:stl|json))`[^|]*\|\s*([0-9a-f]{64})\s*\|', doc):
    f, h = m.group(1), m.group(2)
    p = os.path.join(R, 'wyniki_v2', f) if f.startswith('json/') else (os.path.join(STL_NEW, f) if 'okragla_ramkowa' in f or f in ('ramka_wkladka_okragla_v2.stl', 'ramka_pokrywka_okragla_v2.stl') else None)
    if p is None or not os.path.isfile(p):
        print('?? ', f); continue
    act = sha(p)
    print('OK ' if act == h else 'ZLE', f, h[:16], act[:16])
# sekcja 8 (25 plikow)
sek8 = doc.split('## 8.')[1].split('## 9.')[0]
print('--- sekcja 8 vs pliki')
for m in re.finditer(r'\|\s*(\S+\.(?:stl|json))\s*\|\s*([0-9a-f]{64})\s*\|', sek8):
    f, h = m.group(1), m.group(2)
    p = os.path.join(STL_OLD, f) if f.endswith('.stl') else os.path.join(R, 'wyniki_v2', 'json', f)
    act = sha(p) if os.path.isfile(p) else 'BRAK'
    print('OK ' if act == h else 'ZLE', f, act[:16])
# 3. SHA256SUMS R59
print('--- SHA256SUMS_2026-11-16_R59.txt')
s = open(os.path.join(R, 'Ramki_pakiet', 'SHA256SUMS_2026-11-16_R59.txt'), encoding='utf-8').read()
n_ok = n_all = 0
for line in s.splitlines():
    line = line.strip()
    if not line or line.startswith('#'): continue
    parts = line.split(None, 1)
    if len(parts) != 2: continue
    h, f = parts; f = f.lstrip('*'); base = os.path.basename(f)
    if base.endswith('.stl'):
        p = os.path.join(STL_OLD, base)
    elif base.startswith('uklad_gniazd') and base.endswith('.json'):
        p = os.path.join(R, 'wyniki_v2', 'json', base)
    else:
        continue
    n_all += 1
    act = sha(p) if os.path.isfile(p) else 'BRAK'
    if act == h: n_ok += 1
    else: print('ZLE', f, h[:16], act[:16])
print('zgodnych %d z %d' % (n_ok, n_all))
print('STL w glownym repo:', len(glob.glob(os.path.join(STL_OLD, '*.stl'))), ' JSON w worktree:', sorted(os.path.basename(x) for x in glob.glob(os.path.join(R, 'wyniki_v2', 'json', '*.json'))))