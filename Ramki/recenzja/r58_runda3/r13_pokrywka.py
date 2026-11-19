import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
R2 = os.path.join(STL_NEW, '..', 'stl_r58_runda2')
S = Siatka(os.path.join(STL_NEW, 'ramka_pokrywka_okragla_v2.stl'), rotx180=True)
S2 = Siatka(os.path.join(R2, 'ramka_pokrywka_okragla_v2.stl'), rotx180=True)
print('bbox', np.round(S.bbox()[0], 4), np.round(S.bbox()[1], 4))
def tr(Sx, z, a, r0=0.0):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    t, sg = Sx.promien((r0 * c, r0 * s, z), (c, s, 0)); return t
for z in (-19.5, -13.0, -8.0, -5.5, -5.0, -4.5, -4.1, -3.9, -3.0, -2.5):
    angs = np.arange(0, 360, 0.05)
    brak = np.array([len(tr(S, z, a)) == 0 for a in angs])
    sek = []
    for i, a in enumerate(angs):
        if brak[i] and (i == 0 or not brak[i - 1]): sek.append([a, a])
        if brak[i]: sek[-1][1] = a
    print('Z %.2f: sektory przelotowe (srodek/szer. st.): %s' % (z, ['%.2f/%.2f' % ((s0 + s1) / 2, s1 - s0 + 0.05) for s0, s1 in sek if s1 - s0 < 20]))
rm = 51.05
for kat in (17.6, 32.4, 147.6, 162.4, 197.6, 212.4, 327.6, 342.4):
    c, s = math.cos(math.radians(kat)), math.sin(math.radians(kat)); tdir = np.array((-s, c, 0.0))
    out = []
    for z in (-13.0, -6.5, -5.0, -4.3):
        p = np.array((rm * c, rm * s, z)); a = S.pierwsze(p, tdir); b = S.pierwsze(p, -tdir)
        out.append('Z %.1f szer %.3f' % (z, (a or 0) + (b or 0)))
    tz = S.pierwsze((rm * c, rm * s, -25.0), (0, 0, 1))
    # srednica otworu z promieni pionowych przy v = 0 i +-0.75
    pion = []
    for v in (0.0, 0.75, -0.75):
        q = np.array((rm * c, rm * s, -5.0)) + v * tdir
        up = S.pierwsze(q, (0, 0, 1)); dn = S.pierwsze(q, (0, 0, -1))
        pion.append((round(-5 + up, 3), None if dn is None else round(-5 - dn, 3)))
    # przelotowosc otworu: promien radialny przez scianke na Z -5 w osi
    rr = tr(S, -5.0, kat)
    print('szczelina %.1f: %s; gora otworu/szczeliny w osi Z %.3f; pion (v 0/+0.75/-0.75) gora/dol: %s; przeciecia radialne na Z -5: %s' % (kat, '; '.join(out), -25 + tz, pion, np.round(rr, 3)))
diff = []
for z in np.arange(-19.9, -0.1, 0.5):
    for a in np.arange(0, 360, 0.5):
        t3 = tr(S, z, a); t2 = tr(S2, z, a)
        if len(t3) != len(t2) or (len(t3) and np.max(np.abs(np.array(t3) - np.array(t2))) > 1e-3):
            diff.append((round(z, 2), a))
print('roznice vs runda 2: %d probek, Z %s..%s, katy %s' % (len(diff), min(d[0] for d in diff), max(d[0] for d in diff), sorted(set(round(d[1]) for d in diff))))
# wierzch i garby bez zmian
print('spod wierzchu Z', -10 + S.pierwsze((0, 0, -10), (0, 0, 1)))
for kat in (25, 155, 205, 335):
    print('garb %d: wystep %.4f' % (kat, 50.3 - tr(S, -18.0, kat)[0]))