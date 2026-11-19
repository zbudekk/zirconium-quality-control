# B1 runda 2: w jakich obrotach / przesunieciach plytka siada plasko na polce nowej wkladki (wlasna metoda 2.5D + obrys analitycznie)
import sys, os, math, time, functools
print = functools.partial(print, flush=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
from rastr import *
D = os.path.dirname(os.path.abspath(__file__))
SH = 2.5
# --- wkladka: przeszkody (Z > polka) w kole r <= 50.45, mapa z gory krok 0.1
Vw, _, _ = wczytaj(os.path.join(STL_NEW, 'ramka_wkladka_okragla_v2.stl')); Vw = Vw.copy(); Vw[..., 2] -= 3.5
kw = 0.1; xw0 = -50.6; nw = int(round(101.2 / kw)) + 1
Zw = mapa_z(Vw, xw0, xw0, kw, nw, nw, 'max')
Xw = xw0 + np.arange(nw) * kw; XW, YW = np.meshgrid(Xw, Xw); RW = np.hypot(XW, YW)
FLu = np.array([math.cos(math.radians(-45)), math.sin(math.radians(-45))])
# tylko przeszkody wewnatrz kola otworu (zebro): r < 50.3 i przed scieciem (u < 49.70)
UW = XW * FLu[0] + YW * FLu[1]
m_ob = np.isfinite(Zw) & (Zw > SH + 0.01) & (RW < 50.3) & (UW < 49.70)
OB = np.c_[XW[m_ob], YW[m_ob]]; HOB = Zw[m_ob] - SH
print('przeszkody wewnatrz otworu (poza sciana i scieciem): %d punktow, h %.3f..%.3f, u %.2f..%.2f' % (len(OB), HOB.min(), HOB.max(), (OB @ FLu).min(), (OB @ FLu).max()))
# --- obrys analitycznie (zmierzone: plytka R 50, sciecie 49.3559; otwor 50.3966, sciecie 49.7558)
R_PL, FL_PL, R_OT, FL_OT = 50.0, 49.3559, 50.3966, 49.7558
phi = np.radians(np.arange(0, 360, 0.25)); beta = math.acos(FL_PL / R_PL)
dp = np.abs(((np.degrees(phi) + 45) + 180) % 360 - 180)
rr = np.where(np.radians(dp) < beta, FL_PL / np.cos(np.radians(dp)), R_PL)
OBR = np.c_[rr * np.cos(phi), rr * np.sin(phi)][::2]
g = np.arange(-0.4, 0.4001, 0.1); DX, DY = np.meshgrid(g, g); DD = np.c_[DX.ravel(), DY.ravel()]; DD = DD[np.hypot(DD[:, 0], DD[:, 1]) <= 0.45]
def obrys_ok(th):
    c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
    P = OBR @ np.array([[c, s], [-s, c]])
    ok = (P @ FLu).max() + DD @ FLu <= FL_OT + 1e-6
    mx = np.hypot(P[None, :, 0] + DD[:, None, 0], P[None, :, 1] + DD[:, None, 1]).max(axis=1)
    return ok & (mx <= R_OT + 1e-6)
# --- plytki: mapa wnek od spodu (uklad plytki), krok 0.05, w pierscieniu r 40...50.5
kp = 0.05; xp0 = -50.5; npx = int(round(101 / kp)) + 1
def wneki(f, odwrocona=False):
    V, N, raw = wczytaj(f); V = V.copy(); V[..., 2] -= 8.0
    if odwrocona:
        V[..., 1] *= -1; V[..., 2] *= -1; V[..., 2] -= 8.0     # wierzch na Z -8 (spod), gniazda w dol
        V = V[:, ::-1, :]
    Zmin = mapa_z(V, xp0, xp0, kp, npx, npx, 'min')
    return Zmin + 8.0    # 0 = pelny spod, >0 wneka, NaN = brak materialu
def wneki_dyl(W, n=1):
    # poszerzenie wnek o n wezlow (gorna granica okien plaskich)
    A = np.nan_to_num(W, nan=99.0); B = A.copy()
    for dj in range(-n, n + 1):
        for di in range(-n, n + 1):
            B = np.maximum(B, np.roll(np.roll(A, dj, 0), di, 1))
    return B
def wneki_ero(W, n=1):
    A = np.nan_to_num(W, nan=99.0); B = A.copy()
    for dj in range(-n, n + 1):
        for di in range(-n, n + 1):
            B = np.minimum(B, np.roll(np.roll(A, dj, 0), di, 1))
    return B
def uniesienie(Wmap, th):
    """min po przesunieciach dopuszczalnych (obrys) z max po przeszkodach (h - wneka); None gdy brak przesuniec."""
    ok = obrys_ok(th)
    if not ok.any():
        return None, None
    c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
    Dd = DD[ok]
    Q = (OB[None, :, :] - Dd[:, None, :])                     # (nd, nob, 2)
    qx = c * Q[..., 0] + s * Q[..., 1]; qy = -s * Q[..., 0] + c * Q[..., 1]
    ii = np.clip(np.rint((qx - xp0) / kp).astype(int), 0, npx - 1); jj = np.clip(np.rint((qy - xp0) / kp).astype(int), 0, npx - 1)
    w = Wmap[jj, ii]
    L = np.maximum(HOB[None, :] - w, 0.0).max(axis=1)
    k = int(np.argmin(L))
    return float(L[k]), tuple(np.round(Dd[k], 3))
def przeglad(Wmap, katy):
    out = []
    for th in katy:
        L, d = uniesienie(Wmap, th)
        out.append((th, L, d))
    return out
def okna(wyn, prog=0.02):
    w = []; cur = None
    for th, L, d in wyn:
        if L is not None and L <= prog:
            if cur and abs(th - cur[1] - KROK) < 1e-6: cur[1] = th
            else: cur = [th, th]; w.append(cur)
        else:
            cur = None
    # polacz przez 360
    if len(w) > 1 and w[0][0] == 0.0 and abs(w[-1][1] - (360 - KROK)) < 1e-6:
        w[0][0] = w[-1][0] - 360; w.pop()
    return w
KROK = 0.25
katy = np.arange(0, 360, KROK)
t0 = time.time()
pliki = ['ramka_plytka_okragla_ramkowa_%s_v2.stl' % s for s in ('wieczorna', 'wieczorna_n1', 'wieczorna_n2', 'wieczorna_n3', 'poranna', 'poranna_n4', 'poranna_n5', 'poranna_n6')]
mapy = {}
for f in pliki:
    mapy[f] = wneki(os.path.join(STL_NEW, f))
ref = mapy[pliki[0]]
for f in pliki[1:]:
    A = np.nan_to_num(mapy[f], nan=-9); B = np.nan_to_num(ref, nan=-9)
    rr_ = np.hypot(*np.meshgrid(xp0 + np.arange(npx) * kp, xp0 + np.arange(npx) * kp))
    print('mapa wnek %s vs bazowa wieczorna (r > 44): roznych wezlow %d' % (f, int(((np.abs(A - B) > 1e-3) & (rr_ > 44)).sum())))
for f in pliki:
    warianty = [('poszerzone (gorna granica)', wneki_dyl(mapy[f]))]
    if f in (pliki[0], pliki[4]):
        warianty.append(('zwezone (dolna granica)', wneki_ero(mapy[f])))
    for nazwa, W in warianty:
        wyn = przeglad(W, katy)
        ok = okna(wyn)
        Ls = [L for th, L, d in wyn if L is not None]
        inne = [(th, L) for th, L, d in wyn if L is not None and 0.02 < L < 4.4]
        print('%s [%s]: okna plaskie %s; uniesienie min/max poza oknem %.3f / %.3f; katy z 0,02 < uniesienie < 4,4: %s; bez przesuniec dopuszczalnych: %d katow'
              % (f[28:], nazwa, ['%.2f..%.2f' % (a, b) for a, b in ok], min(L for th, L, d in wyn if L is not None and L > 0.02), max(Ls),
                 ('%d katow, %.2f..%.2f st., uniesienie %.2f..%.2f' % (len(inne), min(i[0] if i[0] < 180 else i[0] - 360 for i in inne), max(i[0] if i[0] < 180 else i[0] - 360 for i in inne), min(i[1] for i in inne), max(i[1] for i in inne))) if inne else 'brak',
                 sum(1 for th, L, d in wyn if L is None)))
    print('   czas %.0f s' % (time.time() - t0))
# n8 / n9 i plytka do gory dnem
for f, odw in (('ramka_plytka_okragla_wieczorna_n8_v2.stl', False), ('ramka_plytka_okragla_poranna_n9_v2.stl', False)):
    W = wneki_dyl(wneki(os.path.join(STL_OLD, f), odw)); wyn = przeglad(W, katy)
    Ls = [L for th, L, d in wyn if L is not None]
    print('%s: okna plaskie %s; uniesienie %.3f..%.3f' % (f, okna(wyn), min(Ls), max(Ls)))
for f in ('ramka_plytka_okragla_ramkowa_wieczorna_n1_v2.stl', 'ramka_plytka_okragla_ramkowa_poranna_n4_v2.stl'):
    W = wneki_dyl(wneki(os.path.join(STL_NEW, f), True)); wyn = przeglad(W, katy)
    Ls = [L for th, L, d in wyn if L is not None]
    print('%s DO GORY DNEM: okna plaskie %s; uniesienie %.3f..%.3f (min przy %s)' % (f[28:], okna(wyn), min(Ls), max(Ls), [th for th, L, d in wyn if L is not None and L == min(Ls)][:5]))
print('czas %.0f s' % (time.time() - t0))