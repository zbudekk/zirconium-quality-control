import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
from rastr import *
from collections import deque
D = os.path.dirname(os.path.abspath(__file__))
R1 = os.path.join(STL_NEW, '..', 'stl_r58_runda1')
FL = -45.0; cu, su = math.cos(math.radians(FL)), math.sin(math.radians(FL))
k = 0.1; x0 = -66.0; nx = int(round(132 / k)) + 1; y0 = -53.5; ny = int(round(151 / k)) + 1
X = x0 + np.arange(nx) * k; Y = y0 + np.arange(ny) * k; XX, YY = np.meshgrid(X, Y)
U = XX * cu + YY * su; Vv = -XX * su + YY * cu
def mapy(f):
    V, N, raw = wczytaj(f); V = V.copy(); V[..., 2] -= 3.5
    return mapa_z(V, x0, y0, k, nx, ny, 'max'), mapa_z(V, x0, y0, k, nx, ny, 'min')
def rozn(A, B):
    a = np.isfinite(A); b = np.isfinite(B)
    return (a != b) | (a & b & (np.abs(np.nan_to_num(A) - np.nan_to_num(B)) > 0.005))
g2, s2 = mapy(os.path.join(STL_NEW, 'ramka_wkladka_okragla_v2.stl'))
g1, s1 = mapy(os.path.join(R1, 'ramka_wkladka_okragla_v2.stl'))
gk, sk = mapy(os.path.join(STL_OLD, 'ramka_wkladka_v2.stl'))
np.save(os.path.join(D, 'wkl2_gora.npy'), g2)
dg = rozn(g2, g1); ds = rozn(s2, s1)
print('wkladka runda2 vs runda1: z gory roznic %d, od spodu %d' % (dg.sum(), ds.sum()))
if dg.any():
    print('   z gory: x %.2f..%.2f y %.2f..%.2f; u %.2f..%.2f v %.2f..%.2f' % (XX[dg].min(), XX[dg].max(), YY[dg].min(), YY[dg].max(), U[dg].min(), U[dg].max(), Vv[dg].min(), Vv[dg].max()))
if ds.any():
    print('   od spodu: x %.2f..%.2f y %.2f..%.2f' % (XX[ds].min(), XX[ds].max(), YY[ds].min(), YY[ds].max()))
ax, ay = np.abs(XX), np.abs(YY)
poza = (ax > 51.35) | (ay > 51.35)
print('vs kwadratowa poza |x|,|y| > 51.35: z gory %d, od spodu %d roznic' % ((rozn(g2, gk) & poza).sum(), (rozn(s2, sk) & poza).sum()))
S = Siatka(os.path.join(STL_NEW, 'ramka_wkladka_okragla_v2.stl'), shift=(0, 0, -3.5))
lo, hi = S.bbox(); print('bbox montazowy', np.round(lo, 4), np.round(hi, 4))
# zebro: szerokosc w funkcji Z i u
for z in (2.6, 3.5, 5.0, 5.9, 6.1, 6.5, 6.9):
    for u in (46.7, 47.5, 48.5, 49.5, 49.7):
        o = (u * cu + su * 4, u * su - cu * 4, z)      # v = -4
        t1 = S.pierwsze(o, (-su, cu, 0))
        o2 = (u * cu - su * 4, u * su + cu * 4, z)     # v = +4
        t2 = S.pierwsze(o2, (su, -cu, 0))
        if t1 is None or t2 is None or t1 > 6 or t2 > 6:
            print('  Z %.1f u %.1f: brak' % (z, u)); continue
        vl = -4 + t1; vp = 4 - t2
        print('  zebro Z %.1f u %.1f: v %.4f..%.4f szer %.4f' % (z, u, vl, vp, vp - vl))
for z in (2.6, 4.0, 5.5, 6.5, 6.95):
    t = S.pierwsze((40 * cu, 40 * su, z), (cu, su, 0))
    print('  czolo zebra Z %.2f: u %.4f' % (z, 40 + t))
for u in (46.6, 47.0, 47.6, 48.5, 49.5, 49.74, 49.8, 50.2):
    t = S.pierwsze((u * cu, u * su, 20), (0, 0, -1))
    print('  wierzch w osi u %.2f: Z %.4f' % (u, 20 - t))
for v in (0.0, 0.6, 1.2):
    t = S.pierwsze((48.5 * cu - su * v, 48.5 * su + cu * v, 20), (0, 0, -1))
    print('  wierzch u 48.5 v %.1f: Z %.4f' % (v, 20 - t))
# sciecie wkladki obok zebra
for v in (-4.0, -2.5, 2.5, 4.0):
    for z in (2.6, 4.75):
        t = S.pierwsze((-su * v, cu * v, z), (cu, su, 0))
        print('  sciecie v %+.1f Z %.2f: %.4f' % (v, z, t))
# kieszenie Halla, wystep, polki - jak runda 1
for nm, (cx, cy) in (('A', (-31.8198, -31.8198)), ('B', (-31.8198, 31.8198)), ('C', (31.8198, 31.8198))):
    t = [S.pierwsze((cx, cy, 1.75), d) for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0))]
    print('  Hall %s: %.4f x %.4f, srodek (%.4f, %.4f)' % (nm, t[0] + t[1], t[2] + t[3], cx + (t[0] - t[1]) / 2, cy + (t[2] - t[3]) / 2))
print('  otwor r (Z 4.75, 0/90/180 st.):', [round(S.pierwsze((0, 0, 4.75), (math.cos(math.radians(a)), math.sin(math.radians(a)), 0)), 4) for a in (0, 90, 180, 225, 135)])
print('  wystep r (Z 1.25, 0/90/180):', [round(S.pierwsze((0, 0, 1.25), (math.cos(math.radians(a)), math.sin(math.radians(a)), 0)), 4) for a in (0, 90, 180)])