import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
from rastr import *
import time
# Plytki ramkowe: mapy od spodu - wneki od spodu (kieszenie, rowek klucza, otwory)
out = {}
for typ, nums in (('wieczorna', ['', '_n1', '_n2', '_n3']), ('poranna', ['', '_n4', '_n5', '_n6'])):
    for n in nums:
        f = os.path.join(STL_NEW, 'ramka_plytka_okragla_ramkowa_%s%s_v2.stl' % (typ, n))
        V, N, raw = wczytaj(f)
        V = V.copy(); V[..., 2] -= 8.0   # uklad: wierzch 0, spod -8
        t0 = time.time()
        k = 0.1
        nx = int(round(101 / k)) + 1
        x0 = -50.5
        zmin = mapa_z(V, x0, x0, k, nx, nx, 'min')
        np.save(os.path.join(os.path.dirname(__file__), 'spod_%s%s.npy' % (typ, n)), zmin)
        # wneki: najnizsza powierzchnia > -8 + 0.01
        X = x0 + np.arange(nx) * k
        XX, YY = np.meshgrid(X, X)
        Rr = np.hypot(XX, YY)
        inside = Rr < 49.0
        rec = inside & np.isfinite(zmin) & (zmin > -7.99)
        hole = inside & ~np.isfinite(zmin)
        # etykietowanie skladowych
        from collections import deque
        lab = np.zeros(rec.shape, int); L = 0; comps = []
        for j0 in range(nx):
            for i0 in range(nx):
                if rec[j0, i0] and not lab[j0, i0]:
                    L += 1; q = deque([(j0, i0)]); lab[j0, i0] = L; pts = []
                    while q:
                        j, i = q.popleft(); pts.append((j, i))
                        for dj, di in ((1,0),(-1,0),(0,1),(0,-1)):
                            jj, ii = j + dj, i + di
                            if 0 <= jj < nx and 0 <= ii < nx and rec[jj, ii] and not lab[jj, ii]:
                                lab[jj, ii] = L; q.append((jj, ii))
                    pts = np.array(pts)
                    xs = X[pts[:, 1]]; ys = X[pts[:, 0]]; zs = zmin[pts[:, 0], pts[:, 1]]
                    comps.append(dict(n=len(pts), cx=round(float(xs.mean()), 3), cy=round(float(ys.mean()), 3), xmin=round(float(xs.min()), 2), xmax=round(float(xs.max()), 2),
                                      ymin=round(float(ys.min()), 2), ymax=round(float(ys.max()), 2), zmax=round(float(zs.max()), 4), zmin=round(float(zs.min()), 4),
                                      r=round(float(np.hypot(xs.mean(), ys.mean())), 3), ang=round(float(np.degrees(np.arctan2(ys.mean(), xs.mean()))), 2), area=round(len(pts) * k * k, 2)))
        print(os.path.basename(f), 'czas %.1f' % (time.time() - t0), 'otwory (pkt bez trafienia, r<49):', int(hole.sum()), 'wneki:', len(comps))
        for c in comps:
            print('   ', c)