import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
from rastr import *
from collections import deque
D = os.path.dirname(os.path.abspath(__file__))
R1 = os.path.join(STL_NEW, '..', 'stl_r58_runda1')
FL = -45.0; cu, su = math.cos(math.radians(FL)), math.sin(math.radians(FL))
k = 0.1; x0 = -50.5; nx = int(round(101 / k)) + 1
X = x0 + np.arange(nx) * k; XX, YY = np.meshgrid(X, X)
U = XX * cu + YY * su; Vv = -XX * su + YY * cu
def mapy(f):
    V, N, raw = wczytaj(f); V = V.copy(); V[..., 2] -= 8.0
    return mapa_z(V, x0, x0, k, nx, nx, 'max'), mapa_z(V, x0, x0, k, nx, nx, 'min')
def rozn(A, B):
    a = np.isfinite(A); b = np.isfinite(B)
    return (a != b) | (a & b & (np.abs(np.nan_to_num(A) - np.nan_to_num(B)) > 0.005))
rowek_nowy = (U >= 45.95) & (np.abs(Vv) <= 1.85)
rowek_stary = (U >= 42.95) & (np.abs(Vv) <= 1.85)
for typ, nums, stara in (('wieczorna', ['', '_n1', '_n2', '_n3'], ''), ('poranna', ['', '_n4', '_n5', '_n6'], '')):
    gs, ss = mapy(os.path.join(STL_OLD, 'ramka_plytka_okragla_%s_v2.stl' % typ))
    for n in nums:
        nm = 'ramka_plytka_okragla_ramkowa_%s%s_v2.stl' % (typ, n)
        g2, s2 = mapy(os.path.join(STL_NEW, nm))
        g1, s1 = mapy(os.path.join(R1, nm))
        dg = rozn(g2, g1); ds = rozn(s2, s1); dgo = rozn(g2, gs)
        print(nm)
        print('   wierzch runda2 vs runda1: roznic %d; wierzch vs okragla R59 (bazowa): roznic %d' % (dg.sum(), dgo.sum()))
        print('   spod runda2 vs runda1: roznic %d, poza obszarem starego+nowego rowka klucza: %d' % (ds.sum(), (ds & ~(rowek_nowy | rowek_stary)).sum()))
        # w obszarze nowego rowka (r < 49.3): sufit
        m = rowek_nowy & (np.hypot(XX, YY) < 49.3) & (U >= 46.1) & (np.abs(Vv) <= 1.7)
        print('   spod w rowku (u 46.1.., |v|<=1.7): Z %.4f..%.4f (pkt %d)' % (np.nanmin(s2[m]), np.nanmax(s2[m]), m.sum()))
        m2 = (U > 43.1) & (U < 45.9) & (np.abs(Vv) <= 1.7)
        print('   dawny rowek u 43.1..45.9: spod Z %.4f..%.4f (ma byc -8, pelny)' % (np.nanmin(s2[m2]), np.nanmax(s2[m2])))