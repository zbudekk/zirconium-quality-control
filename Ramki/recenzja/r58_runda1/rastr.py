# Rasteryzacja map wysokosci (promienie pionowe) - niezalezna od generatora
import numpy as np

def mapa_z(V, x0, y0, krok, nx, ny, tryb='max', zakres_z=None):
    """V: (n,3,3). Siatka punktow x0 + i*krok, y0 + j*krok. Zwraca (ny, nx) z max/min Z powierzchni nad punktem (NaN = brak)."""
    out = np.full((ny, nx), np.nan)
    if tryb == 'max':
        out[:] = -np.inf
    else:
        out[:] = np.inf
    A = V[:, 0, :2]; B = V[:, 1, :2]; C = V[:, 2, :2]
    lo = V[:, :, :2].min(axis=1); hi = V[:, :, :2].max(axis=1)
    i0 = np.ceil((lo[:, 0] - x0) / krok - 1e-9).astype(int); i1 = np.floor((hi[:, 0] - x0) / krok + 1e-9).astype(int)
    j0 = np.ceil((lo[:, 1] - y0) / krok - 1e-9).astype(int); j1 = np.floor((hi[:, 1] - y0) / krok + 1e-9).astype(int)
    i0 = np.maximum(i0, 0); j0 = np.maximum(j0, 0); i1 = np.minimum(i1, nx - 1); j1 = np.minimum(j1, ny - 1)
    for t in range(len(V)):
        if i0[t] > i1[t] or j0[t] > j1[t]:
            continue
        if zakres_z is not None:
            if V[t, :, 2].max() < zakres_z[0] or V[t, :, 2].min() > zakres_z[1]:
                continue
        ii = np.arange(i0[t], i1[t] + 1); jj = np.arange(j0[t], j1[t] + 1)
        X, Y = np.meshgrid(x0 + ii * krok, y0 + jj * krok)
        a, b, c = A[t], B[t], C[t]
        det = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(det) < 1e-14:
            continue
        l1 = ((b[1] - c[1]) * (X - c[0]) + (c[0] - b[0]) * (Y - c[1])) / det
        l2 = ((c[1] - a[1]) * (X - c[0]) + (a[0] - c[0]) * (Y - c[1])) / det
        l3 = 1 - l1 - l2
        e = -1e-9
        m = (l1 >= e) & (l2 >= e) & (l3 >= e)
        if not m.any():
            continue
        Z = l1 * V[t, 0, 2] + l2 * V[t, 1, 2] + l3 * V[t, 2, 2]
        sub = out[j0[t]:j1[t] + 1, i0[t]:i1[t] + 1]
        if tryb == 'max':
            np.maximum(sub, np.where(m, Z, -np.inf), out=sub)
        else:
            np.minimum(sub, np.where(m, Z, np.inf), out=sub)
    out[~np.isfinite(out)] = np.nan
    return out

def wszystkie_z(V, x, y):
    """Wszystkie Z przeciec pionu (x, y) z siatka, posortowane."""
    lo = V[:, :, :2].min(axis=1); hi = V[:, :, :2].max(axis=1)
    m = (lo[:, 0] <= x) & (hi[:, 0] >= x) & (lo[:, 1] <= y) & (hi[:, 1] >= y)
    zs = []
    for tri in V[m]:
        a, b, c = tri[0], tri[1], tri[2]
        det = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(det) < 1e-14:
            continue
        l1 = ((b[1] - c[1]) * (x - c[0]) + (c[0] - b[0]) * (y - c[1])) / det
        l2 = ((c[1] - a[1]) * (x - c[0]) + (a[0] - c[0]) * (y - c[1])) / det
        l3 = 1 - l1 - l2
        if min(l1, l2, l3) >= -1e-9:
            zs.append(l1 * a[2] + l2 * b[2] + l3 * c[2])
    zs = sorted(zs)
    out = []
    for z in zs:
        if not out or abs(z - out[-1]) > 1e-7:
            out.append(z)
    return out