import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
from rastr import *
R2 = os.path.join(STL_NEW, '..', 'stl_r58_runda2')
FL = -45.0; cu, su = math.cos(math.radians(FL)), math.sin(math.radians(FL))
k = 0.1; x0 = -66.0; nx = int(round(132 / k)) + 1; y0 = -53.5; ny = int(round(151 / k)) + 1
X = x0 + np.arange(nx) * k; Y = y0 + np.arange(ny) * k; XX, YY = np.meshgrid(X, Y)
U = XX * cu + YY * su; Vv = -XX * su + YY * cu
def mapy(f, sz=-3.5):
    V, N, raw = wczytaj(f); V = V.copy(); V[..., 2] += sz
    return mapa_z(V, x0, y0, k, nx, ny, 'max'), mapa_z(V, x0, y0, k, nx, ny, 'min')
def rozn(A, B):
    a = np.isfinite(A); b = np.isfinite(B)
    return (a != b) | (a & b & (np.abs(np.nan_to_num(A) - np.nan_to_num(B)) > 0.005))
g3, s3 = mapy(os.path.join(STL_NEW, 'ramka_wkladka_okragla_v2.stl'))
g2, s2 = mapy(os.path.join(R2, 'ramka_wkladka_okragla_v2.stl'))
gk, sk = mapy(os.path.join(STL_OLD, 'ramka_wkladka_v2.stl'))
dg = rozn(g3, g2); ds = rozn(s3, s2)
print('wkladka r3 vs r2: z gory roznic %d (u %.2f..%.2f, |v| <= %.2f, Z r3 %.3f..%.3f, r2 %.3f..%.3f); od spodu %d' % (dg.sum(), U[dg].min(), U[dg].max(), np.abs(Vv[dg]).max(), np.nanmin(g3[dg]), np.nanmax(g3[dg]), np.nanmin(g2[dg]), np.nanmax(g2[dg]), ds.sum()))
poza = (np.abs(XX) > 51.35) | (np.abs(YY) > 51.35)
print('vs kwadratowa poza |x|,|y| > 51.35: z gory %d, od spodu %d' % ((rozn(g3, gk) & poza).sum(), (rozn(s3, sk) & poza).sum()))
S = Siatka(os.path.join(STL_NEW, 'ramka_wkladka_okragla_v2.stl'), shift=(0, 0, -3.5))
print('bbox montazowy', np.round(S.bbox()[0], 4), np.round(S.bbox()[1], 4))
for z in (5.5, 5.95, 6.05, 6.25, 6.5, 6.75, 6.95):
    t = S.pierwsze((60 * cu, 60 * su, z), (-cu, -su, 0)); t2 = S.pierwsze((40 * cu, 40 * su, z), (cu, su, 0))
    o = (48.0 * cu + su * 4, 48.0 * su - cu * 4, z); t3 = S.pierwsze(o, (-su, cu, 0)); o2 = (48.0 * cu - su * 4, 48.0 * su + cu * 4, z); t4 = S.pierwsze(o2, (su, -cu, 0))
    print('  zebro Z %.2f: od zewnatrz pierwsze trafienie u %.4f; od srodka czolo u %.4f; szerokosc na u 48: %s' % (z, 60 - t, 40 + t2, None if (t3 is None or t4 is None or t3 > 6) else round((4 - t4) - (-4 + t3), 4)))
for u in (47.0, 47.6, 48.0, 48.2, 48.5, 49.0, 49.2, 49.5, 49.74, 49.9):
    t = S.pierwsze((u * cu, u * su, 20), (0, 0, -1)); print('  wierzch w osi u %.2f: Z %.4f' % (u, 20 - t))
for v in (0.0, 0.4, 0.6, 1.0):
    t = S.pierwsze((47.9 * cu - su * v, 47.9 * su + cu * v, 20), (0, 0, -1)); print('  wierzch u 47.9 v %.1f: Z %.4f' % (v, 20 - t))
# ponizej Z 6 bez zmian: szerokosc i zasieg
for z in (2.6, 4.0, 5.9):
    t = S.pierwsze((60 * cu - su * 2.5, 60 * su + cu * 2.5, z), (-cu, -su, 0))
    print('  sciecie obok zebra (v 2.5) Z %.1f: u %.4f' % (z, 60 - t))
# wierzcholki czapki zebra (Z > 6.001) - zasieg
P = S.V.reshape(-1, 3); m = P[:, 2] > 6.001
Pu = P[m, 0] * cu + P[m, 1] * su; Pv = -P[m, 0] * su + P[m, 1] * cu
print('  wierzcholki Z > 6: %d, u %.4f..%.4f, |v| <= %.4f, r max %.4f, Z max %.4f' % (m.sum(), Pu.min(), Pu.max(), np.abs(Pv).max(), np.hypot(P[m, 0], P[m, 1]).max(), P[m, 2].max()))
# kanaly / Hall / otwor bez zmian -> spod = runda 2