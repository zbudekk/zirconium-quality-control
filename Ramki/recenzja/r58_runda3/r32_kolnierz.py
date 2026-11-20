# P1 runda 3: kolnierz pokrywki vs czapka zebra w ustawieniach skrajnych (wlasna siatka polozen plytki i pokrywki)
import sys, os, math, time, functools
print = functools.partial(print, flush=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
FL = -45.0; u_ = np.array([math.cos(math.radians(FL)), math.sin(math.radians(FL))]); v_ = np.array([-u_[1], u_[0]])
R_PL, FL_PL, R_OT, FL_OT = 50.0, 49.3559, 50.3966, 49.7558
RW, R_GARB, R_DNO = 50.3, 49.6, 49.2
GARBY = (25.0, 155.0, 205.0, 335.0); POL_GARB = 5.7
# obrys plytki (uklad plytki)
phi = np.radians(np.arange(0, 360, 0.2)); beta = math.acos(FL_PL / R_PL)
dp = np.abs(((np.degrees(phi) - FL) + 180) % 360 - 180)
rr = np.where(np.radians(dp) < beta, FL_PL / np.cos(np.radians(dp)), R_PL)
OBR = np.c_[rr * np.cos(phi), rr * np.sin(phi)]
def rot(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a)); return np.array([[c, -s], [s, c]])
# zebro (uklad wkladki): rogi czesci przy polce (do Z 6 pelne 3,0 x do lica) i czapki
ZEBRO_PKT = np.array([u_ * u0 + v_ * v0 for u0 in (46.5, 49.756) for v0 in (-1.5, 1.5)])
# --- czapka zebra z siatki: trojkaty wkladki z Z >= 6.0 w obszarze zebra
Vw, _, _ = wczytaj(os.path.join(STL_NEW, 'ramka_wkladka_okragla_v2.stl')); Vw = Vw.copy(); Vw[..., 2] -= 3.5
cen = Vw.mean(axis=1); cu_ = cen[:, :2] @ u_; cv_ = cen[:, :2] @ v_
m = (Vw[:, :, 2].min(axis=1) >= 6.0 - 1e-6) & (cu_ > 46.0) & (cu_ < 49.8) & (np.abs(cv_) < 1.6) & (Vw[:, :, 2].max(axis=1) > 6.0 + 1e-6)
CAP = Vw[m]
print('trojkaty czapki zebra (Z > 6): %d; zasieg u %.3f..%.3f, |v| <= %.3f, Z %.3f..%.3f' % (len(CAP), (CAP[..., :2] @ u_).min(), (CAP[..., :2] @ u_).max(), np.abs(CAP[..., :2] @ v_).max(), CAP[..., 2].min(), CAP[..., 2].max()))
CAPP = np.unique(CAP.reshape(-1, 3), axis=0)
def pkt_troj(p, T):
    # odleglosc punktu p od trojkatow T (n,3,3) - Ericson
    a, b, c = T[:, 0], T[:, 1], T[:, 2]
    ab, ac, ap = b - a, c - a, p - a
    d1 = np.einsum('ij,ij->i', ab, ap); d2 = np.einsum('ij,ij->i', ac, ap)
    bp = p - b; d3 = np.einsum('ij,ij->i', ab, bp); d4 = np.einsum('ij,ij->i', ac, bp)
    cp = p - c; d5 = np.einsum('ij,ij->i', ab, cp); d6 = np.einsum('ij,ij->i', ac, cp)
    vc = d1 * d4 - d3 * d2; vb = d5 * d2 - d1 * d6; va = d3 * d6 - d5 * d4
    res = np.zeros_like(a)
    den = va + vb + vc; den[den == 0] = 1e-30
    v = vb / den; w = vc / den
    res[:] = a + ab * v[:, None] + ac * w[:, None]
    m1 = (d1 <= 0) & (d2 <= 0); res[m1] = a[m1]
    m2 = (d3 >= 0) & (d4 <= d3); res[m2] = b[m2]
    m3 = (d6 >= 0) & (d5 <= d6); res[m3] = c[m3]
    m4 = (vc <= 0) & (d1 >= 0) & (d3 <= 0) & ~(m1 | m2 | m3)
    t = d1[m4] / (d1[m4] - d3[m4]); res[m4] = a[m4] + ab[m4] * t[:, None]
    m5 = (vb <= 0) & (d2 >= 0) & (d6 <= 0) & ~(m1 | m2 | m3 | m4)
    t = d2[m5] / (d2[m5] - d6[m5]); res[m5] = a[m5] + ac[m5] * t[:, None]
    m6 = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0) & ~(m1 | m2 | m3 | m4 | m5)
    t = (d4[m6] - d3[m6]) / ((d4[m6] - d3[m6]) + (d5[m6] - d6[m6])); res[m6] = b[m6] + (c[m6] - b[m6]) * t[:, None]
    return np.linalg.norm(res - p, axis=1)
# --- polozenia plytki: obrot i przesuniecie dopuszczalne
kr = 0.02
g = np.arange(-0.46, 0.4601, kr); GX, GY = np.meshgrid(g, g); DPL = np.c_[GX.ravel(), GY.ravel()]; DPL = DPL[np.hypot(DPL[:, 0], DPL[:, 1]) <= 0.46]
plyt = []
for th in np.arange(-0.8, 0.801, 0.2):
    P = OBR @ rot(th).T
    ok = ((P @ u_).max() + DPL @ u_ <= FL_OT + 1e-9) & (np.hypot(P[None, :, 0] + DPL[:, None, 0], P[None, :, 1] + DPL[:, None, 1]).max(axis=1) <= R_OT + 1e-9)
    # zebro w rowku: rogi zebra w ukladzie plytki |v'| <= 1.8, u' >= 46.0
    Rt = rot(-th)
    for i in np.nonzero(ok)[0]:
        q = (ZEBRO_PKT - DPL[i]) @ Rt.T
        if np.all(np.abs(q @ v_) <= 1.8 + 1e-9) and np.all(q @ u_ >= 46.0 - 1e-9):
            plyt.append((th, DPL[i]))
print('polozenia plytki dopuszczalne: %d (obrot -0.8..0.8 co 0.2, przesuniecie co %.2f)' % (len(plyt), kr))
dmax = max(np.hypot(*d) for th, d in plyt); dmax_od = max(-(d @ u_) for th, d in plyt); dmax_do = max((d @ u_) for th, d in plyt)
print('   max przesuniecie plytki %.3f; od zebra (wzdluz -u) %.3f; w strone zebra %.3f' % (dmax, dmax_od, dmax_do))
# --- polozenia pokrywki wzgledem plytki
gc = np.arange(-0.36, 0.3601, kr); CX, CY = np.meshgrid(gc, gc); DCV = np.c_[CX.ravel(), CY.ravel()]; DCV = DCV[np.hypot(DCV[:, 0], DCV[:, 1]) <= 0.36]
def pokr_dopuszczalne(th_pl, osadzona):
    P = OBR @ rot(th_pl).T                     # obrys plytki wzgledem srodka plytki
    ok = np.hypot(P[None, :, 0] - DCV[:, None, 0], P[None, :, 1] - DCV[:, None, 1]).max(axis=1) <= RW + 1e-9
    if osadzona:
        for a in GARBY:
            for da in np.linspace(-POL_GARB, POL_GARB, 7):
                gp = DCV + R_GARB * np.array([math.cos(math.radians(a + da)), math.sin(math.radians(a + da))])
                rg = np.hypot(gp[:, 0], gp[:, 1])
                ang = np.degrees(np.arctan2(gp[:, 1], gp[:, 0])) - th_pl
                nad_scieciem = np.abs(((ang - FL) + 180) % 360 - 180) < math.degrees(beta) + 0.5
                ok &= (rg >= R_DNO - 1e-9) | nad_scieciem
    return DCV[ok]
for osadzona in (True, False):
    t0 = time.time()
    best_proj = (9, None); best_3d = (9, None); n_kol = 0; n_all = 0
    cache = {}
    for th, dpl in plyt:
        if th not in cache: cache[th] = pokr_dopuszczalne(th, osadzona)
        DC = cache[th]
        C = dpl[None, :] + DC                                  # srodek pokrywki w ukladzie wkladki
        # rzut: max |q - C| po wierzcholkach czapki (Z > 6) -> luz = RW - max
        dist = np.hypot(CAPP[None, :, 0] - C[:, None, 0], CAPP[None, :, 1] - C[:, None, 1]).max(axis=1)
        lz = RW - dist
        n_all += len(C)
        k = int(np.argmin(lz))
        if lz[k] < best_proj[0]: best_proj = (float(lz[k]), (round(th, 2), tuple(np.round(dpl, 3)), tuple(np.round(DC[k], 3))))
        # kolizja 3D (rzut z wierzcholkami Z >= 6.5)
        m65 = CAPP[:, 2] >= 6.5 - 1e-9
        d65 = np.hypot(CAPP[m65][None, :, 0] - C[:, None, 0], CAPP[m65][None, :, 1] - C[:, None, 1]).max(axis=1)
        n_kol += int((d65 >= RW).sum())
    print('   pokrywka: max przesuniecie wzgl. plytki %.3f, od zebra %.3f' % (max(np.hypot(D[:, 0], D[:, 1]).max() for D in cache.values()), max((-(D @ u_)).max() for D in cache.values())))
    print('pokrywka %s: ustawien %d; luz w rzucie lico kolnierza - czapka zebra min %.3f przy (obrot, plytka, pokrywka wzgl. plytki) %s; ustawien z wierzcholkiem czapki Z>=6,5 w kolnierzu: %d; %.0f s'
          % ('osadzona (garby nie siadaja na dnie rowka)' if osadzona else 'tylko kolnierz-plytka', n_all, best_proj[0], best_proj[1], n_kol, time.time() - t0))
    # odleglosc 3D w najgorszym ustawieniu: punkty dolnej krawedzi lica (Z 6.5) wokol osi zebra -> trojkaty czapki
    th, dpl, dc = best_proj[1]
    C = np.array(dpl) + np.array(dc)
    dm = 9
    for a in np.arange(-52, -38, 0.02):
        p = np.array([C[0] + RW * math.cos(math.radians(a)), C[1] + RW * math.sin(math.radians(a)), 6.5])
        dm = min(dm, float(pkt_troj(p, CAP).min()))
    print('   odleglosc 3D dolna krawedz lica kolnierza (Z 6,5) - czapka zebra w tym ustawieniu: %.3f' % dm)