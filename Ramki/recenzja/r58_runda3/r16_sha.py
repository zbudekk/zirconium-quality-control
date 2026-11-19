import sys, os, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import sha, STL_NEW, STL_OLD
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
txt = open(os.path.join(R, 'wyniki_v2', 'raport', 'sha256_stl_po_R58.txt'), 'rb').read()
print('sha256_stl_po_R58.txt: bajty nie-ASCII', sum(1 for b in txt if b > 127), 'CR', txt.count(b'\r'))
wpis = {}
for line in txt.decode('ascii').splitlines():
    if not line.strip(): continue
    m = re.match(r'^([0-9a-f]+) [ *](\S+)$', line)
    if not m:
        print('  LINIA ZLA:', repr(line)); continue
    h, f = m.groups()
    p = os.path.join(R, 'wyniki_v2', f)
    act = sha(p) if os.path.isfile(p) else 'BRAK'
    wpis[os.path.basename(f)] = h
    print('  %s len %d %s %s' % ('OK ' if act == h else 'ZLE', len(h), f, act[:12]))
doc = open(os.path.join(R, 'R58_wdrozenie_zmiany.md'), encoding='utf-8').read()
r2 = doc.split('# STAN PO RUNDZIE 3')[1].split('# STAN PO RUNDZIE 2')[0]
print('R58_wdrozenie_zmiany.md (sekcja rundy 3):')
for m in re.finditer(r'\|\s*`([^`]+\.(?:stl|json))`[^|]*\|\s*([^|]+?)\s*\|', r2):
    f, h = m.group(1), m.group(2)
    if not re.fullmatch(r'[0-9a-f]+', h): continue
    b = os.path.basename(f)
    p = os.path.join(R, 'wyniki_v2', f) if f.startswith('json/') else os.path.join(STL_NEW, f)
    act = sha(p) if os.path.isfile(p) else 'BRAK'
    print('  %s len %d %s  = txt: %s' % ('OK ' if act == h else 'ZLE', len(h), f, wpis.get(b) == h))
# inne 64-hex w sekcji R2 (warianty wkladki)
print('pelne sumy w R2 o dlugosci != 64:', [x for x in re.findall(r'\b[0-9a-f]{40,}\b', r2) if len(x) != 64])
# runda 1 odlozone
print('stl_r58_runda2 vs sumy rundy 2 (sekcja R2-0):')
r1 = doc.split('# STAN PO RUNDZIE 2')[1].split('# RUNDA 1')[0]
for m in re.finditer(r'\|\s*`([^`]+\.stl)`[^|]*\|\s*([0-9a-f]{64})\s*\|', r1):
    f, h = m.group(1), m.group(2)
    p = os.path.join(R, 'wyniki_v2', 'stl_r58_runda2', f)
    if os.path.isfile(p):
        print('  %s %s' % ('OK ' if sha(p) == h else 'ZLE', f))
# stare 25
s = open(os.path.join(R, 'Ramki_pakiet', 'SHA256SUMS_2026-11-16_R59.txt'), encoding='utf-8').read()
ok = n = 0
for line in s.splitlines():
    parts = line.strip().split(None, 1)
    if len(parts) != 2 or line.startswith('#'): continue
    h, f = parts; b = os.path.basename(f.lstrip('*'))
    if b.endswith('.stl') and 'TEST_SKANERA' not in b: p = os.path.join(STL_OLD, b)
    elif b.startswith('uklad_gniazd') and b.endswith('.json'): p = os.path.join(R, 'wyniki_v2', 'json', b)
    else: continue
    n += 1; ok += (os.path.isfile(p) and sha(p) == h)
print('stare pliki = SHA256SUMS R59: %d / %d' % (ok, n))