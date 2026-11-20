import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
R1 = os.path.join(STL_NEW, '..', 'stl_r58_runda1')
S = Siatka(os.path.join(STL_NEW, 'ramka_pokrywka_okragla_v2.stl'), rotx180=True)
S1 = Siatka(os.path.join(R1, 'ramka_pokrywka_okragla_v2.stl'), rotx180=True)
print('bbox', np.round(S.bbox()[0], 4), np.round(S.bbox()[1], 4))
def tr(Sx, z, a, r0=0.0):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    t, sg = Sx.promien((r0 * c, r0 * s, z), (c, s, 0)); return t
# przeglad co 0.05 st. na roznych Z: gdzie brak sciany (przelot)
for z in (-19.5, -18.0, -15.0, -12.0, -8.5, -8.05, -7.95, -7.0, -3.0):
    angs = np.arange(0, 360, 0.05)
    brak = np.array([len(tr(S, z, a)) == 0 for a in angs])
    sek = []
    for i, a in enumerate(angs):
        if brak[i] and (i == 0 or not brak[i - 1]): sek.append([a, a])
        if brak[i]: sek[-1][1] = a
    print('Z %.2f: sektory bez sciany (srodek, szer. st.): %s' % (z, ['%.2f/%.2f' % ((s0 + s1) / 2, s1 - s0 + 0.05) for s0, s1 in sek]))
# szerokosc szczelin liniowo: promien styczny na r 51.05 (srodek scianki)
for kat in (17.6, 32.4, 147.6, 162.4, 197.6, 212.4, 327.6, 342.4):
    c, s = math.cos(math.radians(kat)), math.sin(math.radians(kat))
    p = np.array((51.05 * c, 51.05 * s, -15.0)); tdir = np.array((-s, c, 0.0))
    a = S.pierwsze(p, tdir); b = S.pierwsze(p, -tdir)
    tz = S.pierwsze((51.05 * c, 51.05 * s, -25.0), (0, 0, 1))
    print('szczelina %.1f st.: szerokosc (styczna na r 51.05, Z -15) %.4f, os przesunieta %.4f; gora szczeliny Z %.4f' % (kat, a + b, (a - b) / 2, -25 + tz))
# porownanie z runda 1: probki promieni w siatce katow i Z - rozne tylko w szczelinach?
diff = []
for z in np.arange(-19.9, -0.1, 0.5):
    for a in np.arange(0, 360, 0.5):
        t2 = tr(S, z, a); t1 = tr(S1, z, a)
        if len(t2) != len(t1) or (len(t2) and np.max(np.abs(np.array(t2) - np.array(t1))) > 1e-3):
            diff.append((round(z, 2), a))
print('roznice promieni vs runda 1: %d probek; Z %s..%s' % (len(diff), min(d[0] for d in diff) if diff else '-', max(d[0] for d in diff) if diff else '-'))
ks = sorted(set(round(d[1]) for d in diff))
print('   katy roznic (zaokr.):', ks)