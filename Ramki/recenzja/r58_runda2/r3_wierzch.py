import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
from rastr import *
from collections import deque
D = os.path.dirname(os.path.abspath(__file__))
k = 0.1; x0 = -50.5; nx = int(round(101 / k)) + 1
X = x0 + np.arange(nx) * k
def top(f):
    V, N, raw = wczytaj(f); V = V.copy(); V[..., 2] -= 8.0
    return mapa_z(V, x0, x0, k, nx, nx, 'max')
def comps(mask, Z):
    lab = np.zeros(mask.shape, int); L = 0; out = []
    for j0, i0 in zip(*np.nonzero(mask)):
        if lab[j0, i0]:
            continue
        L += 1; q = deque([(j0, i0)]); lab[j0, i0] = L; pts = []
        while q:
            j, i = q.popleft(); pts.append((j, i))
            for dj, di in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                jj, ii = j + dj, i + di
                if 0 <= jj < nx and 0 <= ii < nx and mask[jj, ii] and not lab[jj, ii]:
                    lab[jj, ii] = L; q.append((jj, ii))
        pts = np.array(pts); xs = X[pts[:, 1]]; ys = X[pts[:, 0]]
        out.append(dict(n=len(pts), cx=round(float(xs.mean()), 2), cy=round(float(ys.mean()), 2), x=(round(float(xs.min()), 2), round(float(xs.max()), 2)), y=(round(float(ys.min()), 2), round(float(ys.max()), 2))))
    return out
ref = {}
for typ, stare in (('wieczorna', ['', '_n8']), ('poranna', ['', '_n9'])):
    for s in stare:
        ref[typ + s] = top(os.path.join(STL_OLD, 'ramka_plytka_okragla_%s%s_v2.stl' % (typ, s)))
        np.save(os.path.join(D, 'gora_stara_%s%s.npy' % (typ, s)), ref[typ + s])
for typ, nums in (('wieczorna', ['', '_n1', '_n2', '_n3']), ('poranna', ['', '_n4', '_n5', '_n6'])):
    for n in nums:
        f = os.path.join(STL_NEW, 'ramka_plytka_okragla_ramkowa_%s%s_v2.stl' % (typ, n))
        Z = top(f)
        np.save(os.path.join(D, 'gora_%s%s.npy' % (typ, n)), Z)
        R = ref[typ]
        a = np.isfinite(Z); b = np.isfinite(R)
        niezg = (a != b)
        dz = np.where(a & b, np.abs(Z - R), 0)
        diff = niezg | (dz > 0.005)
        print(os.path.basename(f), 'punkty', int(a.sum()), 'roznica trafien', int(niezg.sum()), 'max dz (wspolne)', round(float(dz.max()), 4), 'pkt dz>0.005', int((dz > 0.005).sum()))
        for c in comps(diff, Z):
            # charakterystyka: srednie Z w ramkowej i starej
            print('    region', c)
        # wysokosci reliefu
        if n:
            print('    max Z', round(float(np.nanmax(Z)), 4))