# Kolizje 3D: odcinki krawedzi siatki A vs trojkaty siatki B (siatka przestrzenna)
import numpy as np
from collections import defaultdict

def krawedzie(V):
    P = V.reshape(-1, 3)
    E = np.concatenate([V[:, [0, 1]], V[:, [1, 2]], V[:, [2, 0]]])
    key = np.sort(np.round(E.reshape(len(E), 6), 6).reshape(len(E), 2, 3).view(np.dtype((np.void, 24))).reshape(len(E), 2), axis=1)
    _, idx = np.unique(key, axis=0, return_index=True)
    return E[idx]

class Siatka3D:
    def __init__(self, V, cell=2.0):
        self.V = V; self.cell = cell
        lo = V.min(axis=1); hi = V.max(axis=1)
        self.lo = lo; self.hi = hi
        self.grid = defaultdict(list)
        a = np.floor(lo / cell).astype(int); b = np.floor(hi / cell).astype(int)
        for t in range(len(V)):
            for i in range(a[t, 0], b[t, 0] + 1):
                for j in range(a[t, 1], b[t, 1] + 1):
                    for k in range(a[t, 2], b[t, 2] + 1):
                        self.grid[(i, j, k)].append(t)
    def kandydaci(self, p, q):
        lo = np.minimum(p, q); hi = np.maximum(p, q)
        a = np.floor(lo / self.cell).astype(int); b = np.floor(hi / self.cell).astype(int)
        s = set()
        for i in range(a[0], b[0] + 1):
            for j in range(a[1], b[1] + 1):
                for k in range(a[2], b[2] + 1):
                    s.update(self.grid.get((i, j, k), ()))
        return np.fromiter(s, int) if s else np.zeros(0, int)

def odcinek_trojkaty(p, q, T, eps=1e-9):
    d = q - p
    v0 = T[:, 0]; e1 = T[:, 1] - v0; e2 = T[:, 2] - v0
    h = np.cross(d, e2)
    det = np.einsum('ij,ij->i', e1, h)
    ok = np.abs(det) > 1e-14
    inv = np.zeros_like(det); inv[ok] = 1 / det[ok]
    s = p - v0
    u = np.einsum('ij,ij->i', s, h) * inv
    qq = np.cross(s, e1)
    v = (qq @ d) * inv
    t = np.einsum('ij,ij->i', e2, qq) * inv
    hit = ok & (u > eps) & (v > eps) & (u + v < 1 - eps) & (t > eps) & (t < 1 - eps)
    return hit

def przeciecia(VA, VB, maks=50):
    """Liczba krawedzi A przecinajacych trojkaty B i krawedzi B przecinajacych trojkaty A (wnetrza, bez styku na krawedziach)."""
    wyn = []
    for X, Y in ((VA, VB), (VB, VA)):
        G = Siatka3D(Y)
        E = krawedzie(X)
        blo = Y.reshape(-1, 3).min(0) - 1e-6; bhi = Y.reshape(-1, 3).max(0) + 1e-6
        m = np.all((np.maximum(E[:, 0], E[:, 1]) >= blo) & (np.minimum(E[:, 0], E[:, 1]) <= bhi), axis=1)
        n = 0; przyk = []
        for p, q in E[m]:
            c = G.kandydaci(p, q)
            if len(c) == 0: continue
            h = odcinek_trojkaty(p, q, Y[c])
            if h.any():
                n += 1
                if len(przyk) < maks: przyk.append(((p + q) / 2).round(3))
        wyn.append((n, przyk))
    return wyn