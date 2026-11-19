import sys, os, math
import numpy as np
from collections import deque
D = os.path.dirname(os.path.abspath(__file__))
k = 0.1; x0 = -66.0; nx = int(round(132 / k)) + 1; y0 = -53.5; ny = int(round(151 / k)) + 1
X = x0 + np.arange(nx) * k; Y = y0 + np.arange(ny) * k
def idx(x, y): return int(round((y - y0) / k)), int(round((x - x0) / k))
for nazwa, plik, osie in (('okragla', 'wkl_okr_spod.npy', {'A': (-31.82, -31.82), 'B': (-31.82, 31.82), 'C': (31.82, 31.82)}),
                          ('kwadratowa', 'wkl_kw_spod.npy', {'A': (-42.0, -42.0), 'B': (-42.0, 42.0), 'C': (42.0, 42.0)})):
    Zb = np.load(os.path.join(D, plik))
    print('====', nazwa)
    for kk, (cx, cy) in osie.items():
        j, i = idx(cx, cy)
        print('  %s: Zb w osi %s' % (kk, Zb[j, i]))
        for prog in (1.4, 0.9, 0.5):
            ok = np.isfinite(Zb) & (Zb >= prog)
            # kieszen (NaN) w otoczeniu 3 mm
            seen = np.zeros_like(ok); q = deque()
            for dj in range(-25, 26):
                for di in range(-25, 26):
                    jj, ii = j + dj, i + di
                    if not np.isfinite(Zb[jj, ii]) and abs(X[ii] - cx) < 2.6 and abs(Y[jj] - cy) < 2.85:
                        seen[jj, ii] = True; q.append((jj, ii))
            while q:
                a, b = q.popleft()
                for da, db in ((1,0),(-1,0),(0,1),(0,-1)):
                    aa, bb = a + da, b + db
                    if 0 <= aa < ny and 0 <= bb < nx and not seen[aa, bb] and ok[aa, bb]:
                        seen[aa, bb] = True; q.append((aa, bb))
            sx = math.copysign(1, cx)
            # cel: szczelina przy uchu (x +-64...66, y 88...90)
            cel = seen[idx(sx * 64, 89.0)] or seen[idx(sx * 64.5, 89.4)]
            ys = Y[np.nonzero(seen)[0]]; xs = X[np.nonzero(seen)[1]]
            print('     prog sufitu >= %.1f: zasieg %d komorek, x %.1f..%.1f, y %.1f..%.1f, dochodzi do (+-64, 89): %s' % (prog, seen.sum(), xs.min(), xs.max(), ys.min(), ys.max(), cel))
    # przekroj kanalu na przekatnej: sufit i szerokosc w funkcji t
    if nazwa == 'okragla':
        for kk, (cx, cy) in osie.items():
            d = np.array([cx, cy]) / math.hypot(cx, cy); nrm = np.array([-d[1], d[0]])
            prof = []
            for t in np.arange(3.0, 29.5, 1.0):
                p = np.array([cx, cy]) + d * t
                # szerokosc: ile komorek w poprzek z sufitem >= 0.9
                w = []
                for s in np.arange(-2.0, 2.01, 0.1):
                    q2 = p + nrm * s; jj, ii = idx(q2[0], q2[1])
                    w.append(Zb[jj, ii])
                w = np.array(w)
                jj, ii = idx(p[0], p[1])
                prof.append((round(t, 1), round(float(math.hypot(*p)), 1), None if not np.isfinite(Zb[jj, ii]) else round(float(Zb[jj, ii]), 2), round(float((np.nan_to_num(w, nan=9) >= 0.9).sum() * 0.1), 1)))
            print('  przekatna %s (t od osi, r, sufit, szer. >=0.9):' % kk, prof)