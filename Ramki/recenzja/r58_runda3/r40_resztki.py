import re
for f in ['Ramki/plan_ramki_v2.md', 'Ramki/protokol_weryfikacji_v2.md']:
    L = open(f, encoding='utf-8').read().split('\n')
    for i, l in enumerate(L):
        if 'R58' in l and re.search(r'ko\u0142ek|ko\u0142ka|kolek|blokuj|blokad', l):
            for m in re.finditer(r'.{0,140}(ko\u0142ek|ko\u0142ka|kolek|blokuj|blokad).{0,140}', l):
                print('%s:%d: ...%s...' % (f, i + 1, m.group(0).encode('ascii', 'replace').decode()))