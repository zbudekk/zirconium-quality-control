import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
from rastr import *
from collections import deque
D = os.path.dirname(os.path.abspath(__file__))
k = 0.1; x0 = -66.0; nx = int(round(132 / k)) + 1; y0 = -53.5; ny = int(round(151 / k)) + 1
X = x0 + np.arange(nx) * k; Y = y0 + np.arange(ny) * k
XX, YY = np.meshgrid(X, Y)
Zt = np.load(os.path.join(D, 'wkl_okr_gora.npy')); Zb = np.load(os.path.join(D, 'wkl_okr_spod.npy'))
V, N, raw = wczytaj(os.path.join(STL_OLD, 'ramka_wkladka_v2.stl')); V = V.copy(); V[..., 2] -= 3.5
Kt = mapa_z(V, x0, y0, k, nx, ny, 'max'); Kb = mapa_z(V, x0, y0, k, nx, ny, 'min')
np.save(os.path.join(D, 'wkl_kw_gora.npy'), Kt); np.save(os.path.join(D, 'wkl_kw_spod.npy'), Kb)
def roznice(A, B, nazwa):
    a = np.isfinite(A); b = np.isfinite(B)
    d = (a != b) | (a & b & (np.abs(np.nan_to_num(A) - np.nan_to_num(B)) > 0.005))
    print(nazwa, 'punktow z roznica', int(d.sum()))
    # podzial na strefy
    ax, ay = np.abs(XX), np.abs(YY)
    strefy = {
        'wewnatrz otworu kwadratu |x|,|y|<=48.4': (ax <= 48.45) & (ay <= 48.45),
        'rama 48.4..52.4 (bez wnetrza)': ((ax <= 52.45) & (ay <= 52.45)) & ~((ax <= 48.45) & (ay <= 48.45)),
        'poza rama (uszy, |x|>52.4 lub |y|>52.4)': ~((ax <= 52.45) & (ay <= 52.45)),
    }
    for nm, m in strefy.items():
        dd = d & m
        if dd.any():
            print('   %s: %d pkt, x %.2f..%.2f, y %.2f..%.2f' % (nm, dd.sum(), XX[dd].min(), XX[dd].max(), YY[dd].min(), YY[dd].max()))
        else:
            print('   %s: 0' % nm)
    return d
dg = roznice(Zt, Kt, 'Z GORY')
ds = roznice(Zb, Kb, 'OD SPODU')
# szczegoly roznic w ramie i poza: skladowe
def skladowe(mask, A, B):
    lab = np.zeros(mask.shape, int); L = 0; out = []
    for j0, i0 in zip(*np.nonzero(mask)):
        if lab[j0, i0]: continue
        L += 1; q = deque([(j0, i0)]); lab[j0, i0] = L; pts = []
        while q:
            j, i = q.popleft(); pts.append((j, i))
            for dj, di in ((1,0),(-1,0),(0,1),(0,-1)):
                jj, ii = j + dj, i + di
                if 0 <= jj < ny and 0 <= ii < nx and mask[jj, ii] and not lab[jj, ii]:
                    lab[jj, ii] = L; q.append((jj, ii))
        pts = np.array(pts)
        xs = X[pts[:, 1]]; ys = Y[pts[:, 0]]
        za = A[pts[:, 0], pts[:, 1]]; zb = B[pts[:, 0], pts[:, 1]]
        out.append((len(pts), round(xs.min(), 2), round(xs.max(), 2), round(ys.min(), 2), round(ys.max(), 2),
                    'okr Z %s..%s' % (np.round(np.nanmin(za), 2) if np.isfinite(za).any() else '-', np.round(np.nanmax(za), 2) if np.isfinite(za).any() else '-'),
                    'kw Z %s..%s' % (np.round(np.nanmin(zb), 2) if np.isfinite(zb).any() else '-', np.round(np.nanmax(zb), 2) if np.isfinite(zb).any() else '-')))
    return out
ax, ay = np.abs(XX), np.abs(YY)
poza_otw = ~((ax <= 48.45) & (ay <= 48.45))
print('Z GORY roznice poza otworem kwadratu (skladowe):')
for c in skladowe(dg & poza_otw, Zt, Kt): print('   ', c)
print('OD SPODU roznice poza otworem kwadratu (skladowe):')
for c in skladowe(ds & poza_otw, Zb, Kb): print('   ', c)