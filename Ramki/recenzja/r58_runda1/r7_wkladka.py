import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
from rastr import *
from collections import deque
D = os.path.dirname(os.path.abspath(__file__))
FLAT = -45.0
cu, su = math.cos(math.radians(FLAT)), math.sin(math.radians(FLAT))
OSIE = {'A': (-31.8198, -31.8198), 'B': (-31.8198, 31.8198), 'C': (31.8198, 31.8198), 'D': (31.8198, -31.8198)}
S = Siatka(os.path.join(STL_NEW, 'ramka_wkladka_okragla_v2.stl'), shift=(0, 0, -3.5))
lo, hi = S.bbox(); print('bbox uklad montazowy', np.round(lo, 4), np.round(hi, 4))
def od(x, y, z, az):
    c, s = math.cos(math.radians(az)), math.sin(math.radians(az))
    return S.pierwsze((x, y, z), (c, s, 0))
angs = np.arange(0, 360, 0.5)
dfl = np.abs(((angs - FLAT) + 180) % 360 - 180)
for z in (2.6, 3.0, 4.0, 4.75, 4.95, 5.25, 5.5, 5.9):
    r = np.array([od(0, 0, z, a) or np.nan for a in angs])
    przod = np.abs(((angs + 90) + 180) % 360 - 180) < 20
    m = (dfl > 12) & ~przod
    print('otwor Z %.2f: r %.4f..%.4f (poza scieciem i przodem); sciecie w osi %.4f; min wszystkie %.4f przy %.1f' % (z, np.nanmin(r[m]), np.nanmax(r[m]), r[np.argmin(np.abs(angs - 315))], np.nanmin(r), angs[np.nanargmin(r)]))
# sciecie: plaszczyzna, promienie rownolegle
for z in (2.6, 3.5, 4.75, 5.5):
    vals = []
    for v in (-4.0, -2.0, 0, 2.0, 4.0):
        t = S.pierwsze((-su * v, cu * v, z), (cu, su, 0))
        vals.append(round(t, 4) if t else None)
    print('sciecie Z %.2f (v -4..4):' % z, vals)
# sektor sciecia
r = np.array([od(0, 0, 4.0, a) or np.nan for a in angs])
sc = angs[r < 50.39]
print('sektor sciecia (r<50.39 na Z 4):', sc.min() if len(sc) else None, sc.max() if len(sc) else None, ' (oczek. -45 +- %.2f)' % math.degrees(math.acos(49.756 / 50.4)))
# wystep: promien na Z 1.25 poza polkami
rl = []
for a in angs:
    dd = min(abs(((a - k) + 180) % 360 - 180) for k in (225, 135, 45, -45))
    if dd < 15 or abs(((a + 90) + 180) % 360 - 180) < 22:
        continue
    rl.append(od(0, 0, 1.25, a))
print('wystep Z 1.25: r %.4f..%.4f (%d)' % (min(rl), max(rl), len(rl)))
for z in (0.3, 2.3):
    rl2 = [od(0, 0, z, a) for a in (0, 90, 180, 10, 170, 100)]
    print('wystep Z %.2f:' % z, np.round(rl2, 4))
# gorna powierzchnia wystepu i polek: mapa z gory w obszarze r < 50.4
k = 0.1; x0 = -66.0; nx = int(round(132 / k)) + 1; y0 = -53.5; ny = int(round(151 / k)) + 1
Zt = mapa_z(S.V, x0, y0, k, nx, ny, 'max'); Zb = mapa_z(S.V, x0, y0, k, nx, ny, 'min')
np.save(os.path.join(D, 'wkl_okr_gora.npy'), Zt); np.save(os.path.join(D, 'wkl_okr_spod.npy'), Zb)
X = x0 + np.arange(nx) * k; Y = y0 + np.arange(ny) * k
XX, YY = np.meshgrid(X, Y); RR = np.hypot(XX, YY)
m = (RR > 47.1) & (RR < 50.3) & np.isfinite(Zt)
print('wystep z gory (r 47.1..50.3): Z %.4f..%.4f, pkt %d' % (np.nanmin(Zt[m]), np.nanmax(Zt[m]), m.sum()))
for kk, (cx, cy) in OSIE.items():
    mm = (np.abs(XX - cx) <= 5.05) & (np.abs(YY - cy) <= 5.05) & (RR < 47.0)
    zz = Zt[mm]
    fin = np.isfinite(zz)
    # zasieg polki na Z 1.25: promienie od srodka polki w kierunku srodka plytki
    print('polka %s: pkt %d, z gory: Z %s..%s, bez trafienia %d (kieszen przelotowa)' % (kk, mm.sum(), np.round(np.nanmin(zz), 4) if fin.any() else None, np.round(np.nanmax(zz), 4) if fin.any() else None, (~fin).sum()))
    # krawedzie polki: z punktu (cx, cy) w strone osi -X/-Y (do srodka) na Z 1.25 od zewnatrz kwadratu
    sx, sy = math.copysign(1, cx), math.copysign(1, cy)
    tx = S.pierwsze((cx - sx * 8, cy, 1.25), (sx, 0, 0)); ty = S.pierwsze((cx, cy - sy * 8, 1.25), (0, sy, 0))
    print('   bok polki od strony srodka: x %.4f (oczek. %.4f), y %.4f (oczek. %.4f)' % (cx - sx * 8 + sx * tx, cx - sx * 5, cy - sy * 8 + sy * ty, cy - sy * 5))
    if kk != 'D':
        # kieszen Halla
        t = [S.pierwsze((cx, cy, z_), d) for z_ in (1.75,) for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0))]
        print('   kieszen Halla Z 1.75: srodek (%.4f, %.4f), %.4f x %.4f; przelot pion: %s' % (cx + (t[0] - t[1]) / 2, cy + (t[2] - t[3]) / 2, t[0] + t[1], t[2] + t[3], S.pierwsze((cx, cy, -5), (0, 0, 1))))
        for z_ in (0.5, 2.3):
            t = [S.pierwsze((cx, cy, z_), d) for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0))]
            print('   Z %.2f: %s' % (z_, np.round(t, 3)))
# kolek klucza
cx, cy = OSIE['D']
for z in (2.6, 3.25, 3.95, 4.1, 4.3, 4.45):
    k4 = []
    for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        t = S.pierwsze((cx + dx * 4, cy + dy * 4, z), (-dx, -dy, 0)); k4.append(4 - t if t else None)
    print('kolek Z %.2f: promienie +X -X +Y -Y %s' % (z, np.round(k4, 4)))
print('kolek wierzch:', 10 - S.pierwsze((cx, cy, 10), (0, 0, -1)))
# dawny kolek kwadratowy
print('dawny kolek (45.6, -45.6): pion z gory trafia Z', None if S.pierwsze((45.6, -45.6, 20), (0, 0, -1)) is None else 20 - S.pierwsze((45.6, -45.6, 20), (0, 0, -1)))
# scianka ramy w osiach i dno w osi
for az in (0, 90, 180, 270, -45, 225, 135, 45):
    for z in (0.75, 2.0, 3.75, 5.0):
        c, s = math.cos(math.radians(az)), math.sin(math.radians(az))
        tr, sg = S.promien((0, 0, z), (c, s, 0))
        segs = [(round(tr[i], 3), round(tr[i + 1], 3), round(tr[i + 1] - tr[i], 3)) for i in range(0, len(tr) - 1, 2)]
        print('os %4d Z %.2f: odcinki materialu %s' % (az, z, segs))