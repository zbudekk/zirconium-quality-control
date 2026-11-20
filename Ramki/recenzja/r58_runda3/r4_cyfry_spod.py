import sys, os
import numpy as np
D = os.path.dirname(os.path.abspath(__file__))
k = 0.1; x0 = -50.5; nx = int(round(101 / k)) + 1
X = x0 + np.arange(nx) * k
for typ, nums, c in (('wieczorna', ['_n1', '_n2', '_n3'], (35, -26.5)), ('poranna', ['_n4', '_n5', '_n6'], (-44, 5.5))):
    for n in nums:
        Z = np.load(os.path.join(D, 'gora_%s%s.npy' % (typ, n)))
        i0 = int(round((c[0] - 3 - x0) / k)); i1 = int(round((c[0] + 3 - x0) / k))
        j0 = int(round((c[1] - 3.5 - x0) / k)); j1 = int(round((c[1] + 3.5 - x0) / k))
        print(typ, n)
        for j in range(j1, j0 - 1, -3):
            print('   ' + ''.join('#' if (np.isfinite(Z[j, i]) and Z[j, i] > 0.3) else ('.' if np.isfinite(Z[j, i]) else 'o') for i in range(i0, i1 + 1, 2)))
# spod: porownanie ze stara plytka (min Z)
sys.path.insert(0, D)
from siatka import *
from rastr import *
for typ in ('wieczorna', 'poranna'):
    V, N, raw = wczytaj(os.path.join(STL_OLD, 'ramka_plytka_okragla_%s_v2.stl' % typ)); V = V.copy(); V[..., 2] -= 8
    S0 = mapa_z(V, x0, x0, k, nx, nx, 'min')
    S1 = np.load(os.path.join(D, 'spod_%s.npy' % typ))
    a = np.isfinite(S0); b = np.isfinite(S1)
    dz = np.where(a & b, np.abs(S0 - S1), 0)
    XX, YY = np.meshgrid(X, X)
    diff = (a != b) | (dz > 0.005)
    print(typ, 'spod: roznice trafien', int((a != b).sum()), 'pkt dz>0.005', int((dz > 0.005).sum()))
    # czy roznice tylko w kieszeniach (r<=2.65 od osi) i rowku klucza
    ax = [(-31.8198, -31.8198), (-31.8198, 31.8198), (31.8198, 31.8198)]
    inn = np.zeros_like(diff)
    for cx, cy in ax:
        inn |= np.hypot(XX - cx, YY - cy) <= 2.65
    cu, su = np.cos(np.radians(-45)), np.sin(np.radians(-45))
    u = XX * cu + YY * su; v = -XX * su + YY * cu
    inn |= (u >= 42.95) & (np.abs(v) <= 1.85)
    print('   roznice poza kieszeniami i rowkiem klucza:', int((diff & ~inn).sum()), ' rowek/kieszenie bez roznicy (r<49.5):', int((inn & ~diff & (np.hypot(XX, YY) < 49.3)).sum()))