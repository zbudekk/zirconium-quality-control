import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
S = Siatka(os.path.join(STL_NEW, 'ramka_pokrywka_okragla_v2.stl'), rotx180=True)
lo, hi = S.bbox(); print('bbox (wierzch Z 0)', np.round(lo, 4), np.round(hi, 4))
def od(z, az, x=0, y=0):
    c, s = math.cos(math.radians(az)), math.sin(math.radians(az))
    tr, sg = S.promien((x, y, z), (c, s, 0)); return tr
for z in (-3, -10, -16.5, -19.5):
    ri = []; ro = []
    for a in np.arange(0, 360, 2.5):
        tr = od(z, a)
        if len(tr) >= 2: ri.append(tr[0]); ro.append(tr[1])
    print('Z %g: r wewn %.4f..%.4f, zewn %.4f..%.4f (%d)' % (z, min(ri), max(ri), min(ro), max(ro), len(ri)))
t = S.pierwsze((0, 0, -10), (0, 0, 1)); print('spod wierzchu Z', -10 + t)
# garby: przeglad co 0.25 st. na Z -18
angs = np.arange(0, 360, 0.25)
r = np.array([(od(-18.0, a)[0] if len(od(-18.0, a)) else np.nan) for a in angs])
g = np.nan_to_num(r, nan=99) < 50.25
sek = []
for i, a in enumerate(angs):
    if g[i] and (i == 0 or not g[i - 1]): sek.append([a, a])
    if g[i]: sek[-1][1] = a
print('sektory garbow (r < 50.25):', sek); bez = angs[np.isnan(r)]; print('Z -18 bez trafienia (wyciecia): katy', bez.min() if len(bez) else None, '...', bez.max() if len(bez) else None, 'liczba', len(bez))
for s0, s1 in sek:
    m = (angs >= s0) & (angs <= s1)
    print('   srodek %.2f, rozpietosc %.2f st. (= %.2f mm na r 50.3), min r %.4f (wystep %.4f)' % ((s0 + s1) / 2, s1 - s0, math.radians(s1 - s0) * 50.3, r[m].min(), 50.3 - r[m].min()))
# profil garbu w Z na kacie 25
for kat in (25, 155, 205, 335):
    prof = []
    for z in np.arange(-19.0, -16.9, 0.1):
        prof.append(round(50.3 - od(z, kat)[0], 3))
    print('profil garbu %d (Z -19..-17 co 0.1): %s' % (kat, prof))
    c, s = math.cos(math.radians(kat)), math.sin(math.radians(kat))
    rr = 50.3 - 0.35
    tu = S.pierwsze((rr * c, rr * s, -18), (0, 0, 1)); td = S.pierwsze((rr * c, rr * s, -18), (0, 0, -1))
    print('   na r 49.95: Z %.3f..%.3f' % (-18 - td, -18 + tu))
# wyciecia palcowe
for zn in (-1, 1):
    y = zn * 48.8
    tp = S.pierwsze((0, y, -19.5), (1, 0, 0)); tm = S.pierwsze((0, y, -19.5), (-1, 0, 0))
    tz = S.pierwsze((0, zn * 51.05, -25), (0, 0, 1))
    print('wyciecie %s: szerokosc na Z -19.5 (y %.1f): %.3f, os x %.3f; gora wyciecia Z %.3f' % ('przod' if zn < 0 else 'tyl', y, tp + tm, (tp - tm) / 2, -25 + tz))
    for yy in (zn * 48.3, zn * 49.3):
        tp = S.pierwsze((0, yy, -19.5), (1, 0, 0)); tm = S.pierwsze((0, yy, -19.5), (-1, 0, 0))
        print('    y %.2f: szer %.3f' % (yy, (tp or 0) + (tm or 0)))
# kat wyciecia na r 50.3 -> polowa kata
print('polowa kata wyciecia na r 50.3: %.2f st.' % math.degrees(math.asin(15 / 50.3)))