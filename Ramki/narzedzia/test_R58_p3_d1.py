# R58 runda 2: test P3 (wyczysc_wyniki chroni pliki kompletu R58) i D1 (waski wyjatek K-60 zrzut_parametrow_zgodny) bez Blendera.
# Moduly bpy / bmesh / mathutils zastapione stubami - testowane sa tylko funkcje plikowe generatora. Pracuje na katalogach tymczasowych
# (nic nie zapisuje w Ramki/). Uruchomienie: python narzedzia/test_R58_p3_d1.py <sciezka do Ramki>
import copy
import json
import math
import os
import shutil
import sys
import tempfile
import types

KAT = sys.argv[1]


class Vector(tuple):
    def __new__(cls, v):
        return tuple.__new__(cls, [float(x) for x in v])

    def normalized(self):
        n = math.sqrt(sum(c * c for c in self))
        return Vector([c / n for c in self])


mu = types.ModuleType('mathutils')
mu.Vector = Vector
mu.Matrix = type('Matrix', (), {})
mu.Euler = type('Euler', (), {})
bvh = types.ModuleType('mathutils.bvhtree')
bvh.BVHTree = type('BVHTree', (), {})
mu.bvhtree = bvh
sys.modules.update({'bpy': types.ModuleType('bpy'), 'bmesh': types.ModuleType('bmesh'), 'mathutils': mu, 'mathutils.bvhtree': bvh})
sys.path.insert(0, KAT)
import ramka_generator as G

sc_param = os.path.join(KAT, 'parametry.json')
P, _s, _l = G.wczytaj_parametry(sc_param)

print('== P3: wyczysc_wyniki na kopii katalogu (pliki puste o nazwach z wyniki_v2) ==')
tmp = tempfile.mkdtemp(prefix='r58_p3_')
os.makedirs(os.path.join(tmp, 'stl'))
os.makedirs(os.path.join(tmp, 'arkusze'))
os.makedirs(os.path.join(tmp, 'json'))
stare = ['ramka_plytka_wieczorna_n1_v2.stl', 'ramka_wkladka_v2.stl', 'ramka_plytka_okragla_wieczorna_n8_v2.stl', 'ramka_pokrywka_v2.stl']
r58 = [G.nazwa_stl(P, r) for r in G.rdzenie_R58(P)]
for n in stare + r58:
    open(os.path.join(tmp, 'stl', n), 'w').close()
open(os.path.join(tmp, 'arkusze', 'kody_plytek.md'), 'w').close()
for n in ('uklad_gniazd_okragla_ramkowa_wieczorna.json', 'uklad_gniazd_okragla_ramkowa_poranna.json'):
    open(os.path.join(tmp, 'json', n), 'w').close()
print('przed: stl %d (stare %d + R58 %d), arkusze %d, json %d' % (len(os.listdir(os.path.join(tmp, 'stl'))), len(stare), len(r58),
                                                                 len(os.listdir(os.path.join(tmp, 'arkusze'))), len(os.listdir(os.path.join(tmp, 'json')))))
pom = G.wyczysc_wyniki(tmp, P)
zost = sorted(os.listdir(os.path.join(tmp, 'stl')))
print('po:    stl %d, arkusze %d, json %d; pominiete przez wyczysc_wyniki: %d' % (len(zost), len(os.listdir(os.path.join(tmp, 'arkusze'))),
                                                                              len(os.listdir(os.path.join(tmp, 'json'))), len(pom)))
print('zostaly dokladnie pliki R58:', zost == sorted(r58), '; stare usuniete:', not any(n in zost for n in stare))
pom2 = G.wyczysc_wyniki(tmp)
print('wywolanie bez P (dawne zachowanie) usuwa wszystko w stl:', os.listdir(os.path.join(tmp, 'stl')) == [])
shutil.rmtree(tmp)

print('== D1: zrzut_parametrow_zgodny (K-60) ==')
biez = json.load(open(sc_param, encoding='utf-8'))
sc_wym = os.path.join(KAT, 'wyniki_v2', 'arkusze', 'arkusz_wymiarow.md')
tekst = open(sc_wym, encoding='utf-8').read()


def przypadek(opis, zmien):
    import re
    m = re.search(r'(## 6\. Pe.ny zrzut[^\n]*\n.*?```json\n)(.*?)(\n```)', tekst, re.S)
    zr = json.loads(m.group(2))
    zr = zmien(zr)
    t2 = tekst[:m.start(2)] + json.dumps(zr, ensure_ascii=False, indent=2) + tekst[m.end(2):]
    d = tempfile.mkdtemp(prefix='r58_d1_')
    p = os.path.join(d, 'arkusz_wymiarow.md')
    open(p, 'w', encoding='utf-8').write(t2)
    G._ZRZUT_UWAGA[:] = []
    w = G.zrzut_parametrow_zgodny(p, sc_param)
    print('%-80s -> %s' % (opis, 'zgodny' if w else 'NIE'))
    shutil.rmtree(d)


def z_kluczem(klucz, wartosc):
    def f(zr):
        for s, z in biez.items():
            if not s.startswith('_') and klucz in z:
                zr[s][klucz] = copy.deepcopy(z[klucz])
                if wartosc is not None:
                    zr[s][klucz]['value'] = wartosc
        return zr
    return f


def zmien_stary(zr):
    zr['plytka']['plate_size']['value'] = 97
    return zr


przypadek('zrzut R59 bez zmian (brak wszystkich kluczy R58)', lambda zr: zr)
przypadek('zrzut z jednym kluczem R58 o poprawnej wartosci (pozostalych brak)', z_kluczem('round_magnet_r', None))
przypadek('zrzut z jednym kluczem R58 o BLEDNEJ wartosci (pozostalych brak)', z_kluczem('round_magnet_r', 44))
przypadek('zrzut bez kluczy R58, ale zmieniony stary klucz plate_size', zmien_stary)


def pelny(zr):
    return copy.deepcopy(biez)


przypadek('zrzut = biezacy parametry.json (pelny)', pelny)
