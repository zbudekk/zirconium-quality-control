# Wspolne narzedzia recenzenta R58 (niezalezne od generatora)
import numpy as np, struct, os, hashlib

STL_NEW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'wyniki_v2', 'stl')
STL_OLD = r'<MSI>\kod\qc\Ramki\wyniki_v2\stl'

def wczytaj(path):
    with open(path, 'rb') as f:
        d = f.read()
    n = struct.unpack('<I', d[80:84])[0]
    assert len(d) == 84 + 50 * n, (path, len(d), n)
    dt = np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    a = np.frombuffer(d, dtype=dt, count=n, offset=84)
    return a['v'].astype(np.float64), a['n'].astype(np.float64), d

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

def topologia(V):
    # zgrzewanie po dokladnych wartosciach float32
    P = V.reshape(-1, 3).astype(np.float32)
    uniq, inv = np.unique(P, axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    F = inv.reshape(-1, 3)
    deg = (F[:, 0] == F[:, 1]) | (F[:, 1] == F[:, 2]) | (F[:, 0] == F[:, 2])
    E = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    key_dir = E[:, 0].astype(np.int64) * (len(uniq) + 1) + E[:, 1]
    lo = np.minimum(E[:, 0], E[:, 1]); hi = np.maximum(E[:, 0], E[:, 1])
    key = lo.astype(np.int64) * (len(uniq) + 1) + hi
    u, cnt = np.unique(key, return_counts=True)
    bad_cnt = int((cnt != 2).sum())
    # zwroty: kazda krawedz skierowana tylko raz
    ud, cd = np.unique(key_dir, return_counts=True)
    dup_dir = int((cd > 1).sum())
    # skladowe spojnosci (po wierzcholkach przez trojkaty)
    parent = np.arange(len(uniq))
    def find(x):
        r = x
        while parent[r] != r:
            r = parent[r]
        while parent[x] != r:
            parent[x], x = r, parent[x]
        return r
    for a, b in np.concatenate([F[:, [0, 1]], F[:, [1, 2]]]):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    roots = len(set(find(i) for i in np.unique(F)))
    return dict(nv=len(uniq), nf=len(F), degenerate=int(deg.sum()), edges_not2=bad_cnt,
                dir_dup=dup_dir, components=roots, euler=len(uniq) - len(u) + len(F))

def objetosc(V):
    a, b, c = V[:, 0], V[:, 1], V[:, 2]
    return float(np.einsum('ij,ij->i', a, np.cross(b, c)).sum() / 6.0)

def pola(V):
    return 0.5 * np.linalg.norm(np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0]), axis=1)

class Siatka:
    def __init__(self, path, shift=(0, 0, 0), rotx180=False, rotz=0.0):
        V, N, raw = wczytaj(path)
        self.path = path
        self.raw = raw
        V = V.copy()
        if rotx180:
            V[..., 1] *= -1; V[..., 2] *= -1
        if rotz:
            c, s = np.cos(np.radians(rotz)), np.sin(np.radians(rotz))
            x = V[..., 0].copy(); y = V[..., 1].copy()
            V[..., 0] = c * x - s * y; V[..., 1] = s * x + c * y
        V = V + np.array(shift, float)
        self.V = V
        self.v0 = V[:, 0]; self.e1 = V[:, 1] - V[:, 0]; self.e2 = V[:, 2] - V[:, 0]
        nrm = np.cross(self.e1, self.e2)
        ln = np.linalg.norm(nrm, axis=1); ln[ln == 0] = 1
        self.nrm = nrm / ln[:, None]
        self.lo = V.min(axis=1); self.hi = V.max(axis=1)

    def bbox(self):
        P = self.V.reshape(-1, 3)
        return P.min(axis=0), P.max(axis=0)

    def promien(self, o, d, tmax=1e9, wszystkie=True):
        # przeciecia promienia o + t d (t > 0); zwraca posortowane t i znak (normalna . d: <0 wejscie)
        o = np.asarray(o, float); d = np.asarray(d, float); d = d / np.linalg.norm(d)
        # wstepny filtr bbox trojkatow wzdluz promienia
        end = o + d * min(tmax, 1000)
        blo = np.minimum(o, end) - 1e-6; bhi = np.maximum(o, end) + 1e-6
        m = np.all((self.hi >= blo) & (self.lo <= bhi), axis=1)
        idx = np.nonzero(m)[0]
        if len(idx) == 0:
            return np.array([]), np.array([])
        v0 = self.v0[idx]; e1 = self.e1[idx]; e2 = self.e2[idx]
        p = np.cross(d, e2)
        det = np.einsum('ij,ij->i', e1, p)
        ok = np.abs(det) > 1e-14
        inv = np.zeros_like(det); inv[ok] = 1.0 / det[ok]
        s = o - v0
        u = np.einsum('ij,ij->i', s, p) * inv
        q = np.cross(s, e1)
        v = (q @ d) * inv
        t = np.einsum('ij,ij->i', e2, q) * inv
        eps = 1e-9
        hit = ok & (u >= -eps) & (v >= -eps) & (u + v <= 1 + eps) & (t > 1e-9) & (t < tmax)
        t = t[hit]; sg = np.sign(self.nrm[idx][hit] @ d)
        order = np.argsort(t)
        t = t[order]; sg = sg[order]
        # scal duplikaty na krawedziach (ta sama odleglosc i znak)
        if len(t):
            keep = [0]
            for i in range(1, len(t)):
                if abs(t[i] - t[keep[-1]]) < 1e-7 and sg[i] == sg[keep[-1]]:
                    continue
                keep.append(i)
            t = t[keep]; sg = sg[keep]
        return t, sg

    def pierwsze(self, o, d, tmax=1e9):
        t, sg = self.promien(o, d, tmax)
        return (float(t[0]) if len(t) else None)

    def wewnatrz(self, p):
        # parzystosc w 3 kierunkach ukosnych, glosowanie
        p = np.asarray(p, float)
        dirs = [(0.123, 0.456, 0.881), (-0.613, 0.211, -0.761), (0.371, -0.902, 0.219)]
        votes = 0
        for d in dirs:
            t, sg = self.promien(p, d)
            votes += (len(t) % 2)
        return votes >= 2

    def przekroj_z(self, z):
        # odcinki przekroju plaszczyzna z = const
        V = self.V
        m = (self.lo[:, 2] <= z) & (self.hi[:, 2] >= z)
        segs = []
        for tri in V[m]:
            d = tri[:, 2] - z
            pts = []
            for i in range(3):
                a, b = tri[i], tri[(i + 1) % 3]
                da, db = d[i], d[(i + 1) % 3]
                if (da < 0 and db > 0) or (da > 0 and db < 0):
                    t = da / (da - db)
                    pts.append(a + t * (b - a))
            if len(pts) == 2:
                segs.append((pts[0][:2], pts[1][:2]))
        return segs