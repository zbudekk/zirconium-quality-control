import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
np.set_printoptions(suppress=True)
FLAT = -45.0
def pr_zew(S, ang, z, r0=60.0):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    t = S.pierwsze((r0 * c, r0 * s, z), (-c, -s, 0))
    return None if t is None else r0 - t
def pr_od(S, x, y, z, ang):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return S.pierwsze((x, y, z), (c, s, 0))
def wyniki_plytki(nazwa, pelne=True):
    S = Siatka(os.path.join(STL_NEW, nazwa), shift=(0, 0, -8))
    W = {}
    angs = np.arange(0, 360, 0.5)
    for z in (-0.25, -1.0, -1.45, -1.55, -2.0, -2.45, -2.55, -3.0, -4.0, -7.5, -7.95):
        r = np.array([pr_zew(S, a, z) for a in angs])
        d = np.abs(((angs - FLAT) + 180) % 360 - 180)
        poza = d > 12
        W['r_z%.2f' % z] = (round(float(r[poza].min()), 4), round(float(r[poza].max()), 4))
        # sciecie: kat i odleglosc
        W['flat_z%.2f' % z] = round(float(r[np.argmin(np.abs(angs - 315.0))]), 4)
        W['rmin_all_z%.2f' % z] = (round(float(r.min()), 4), float(angs[np.argmin(r)]))
        if z == -4.0:
            # szerokosc cieciwy: zakres katow gdzie r < R - 0.01
            sc = angs[(r < 49.99)]
            W['flat_sektor'] = (float(sc.min()), float(sc.max()))
    # plaszczyzna sciecia na Z -7.5 promieniami rownoleglymi odsunietymi o v
    cu, su = math.cos(math.radians(FLAT)), math.sin(math.radians(FLAT))
    for v in (-6.0, -4.9, -2.5, 2.5, 4.9, 6.0):
        for z in (-4.0, -7.5, -2.0):
            o = (cu * 60 - su * v, su * 60 + cu * v, z)
            t = S.pierwsze(o, (-cu, -su, 0))
            W['flat_v%+.1f_z%.1f' % (v, z)] = None if t is None else round(60 - t, 4)
    # rowek: pionowe promienie przy r 49.6 (poza scieciem) i 49.3 (w scieciu)
    gz = []
    for a in np.arange(0, 360, 5):
        if abs(((a - FLAT) + 180) % 360 - 180) < 12:
            continue
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        tu = S.pierwsze((49.6 * c, 49.6 * s, -2.0), (0, 0, 1)); td = S.pierwsze((49.6 * c, 49.6 * s, -2.0), (0, 0, -1))
        gz.append((round(-2 + tu, 4), round(-2 - td, 4)))
    gz = np.array(gz)
    W['rowek_z_gora'] = (float(gz[:, 0].min()), float(gz[:, 0].max())); W['rowek_z_dol'] = (float(gz[:, 1].min()), float(gz[:, 1].max()))
    for v in (0.0, 3.0, 6.0):
        o = (cu * 49.28 - su * v, su * 49.28 + cu * v, -2.0)
        if np.hypot(o[0], o[1]) < 49.2:
            continue
        tu = S.pierwsze(o, (0, 0, 1)); td = S.pierwsze(o, (0, 0, -1))
        W['rowek_w_scieciu_v%.0f' % v] = (None if tu is None else round(-2 + tu, 4), None if td is None else round(-2 - td, 4))
    # kieszenie
    kie = {}
    for nm, (cx, cy) in (('A', (-31.8198, -31.8198)), ('B', (-31.8198, 31.8198)), ('C', (31.8198, 31.8198))):
        rr = []
        pts = []
        for a in np.arange(0, 360, 5):
            t = pr_od(S, cx, cy, -6.9, a)
            pts.append((cx + t * math.cos(math.radians(a)), cy + t * math.sin(math.radians(a))))
        P_ = np.array(pts)
        # dopasowanie okregu (algebraiczne)
        A_ = np.c_[2 * P_[:, 0], 2 * P_[:, 1], np.ones(len(P_))]
        b_ = (P_ ** 2).sum(1)
        sol = np.linalg.lstsq(A_, b_, rcond=None)[0]
        xc, yc = sol[0], sol[1]; rc = math.sqrt(sol[2] + xc * xc + yc * yc)
        dd = np.hypot(P_[:, 0] - xc, P_[:, 1] - yc)
        dno = S.pierwsze((cx, cy, -9), (0, 0, 1))
        # przy wejsciu (Z -7.95) i przy suficie (Z -5.85)
        r_wej = np.mean([pr_od(S, cx, cy, -7.95, a) for a in range(0, 360, 30)])
        r_suf = np.mean([pr_od(S, cx, cy, -5.85, a) for a in range(0, 360, 30)])
        ro = math.hypot(cx, cy)
        tr, sg = S.promien((cx, cy, -6.9), (cx / ro, cy / ro, 0))
        kie[nm] = dict(srodek=(round(xc, 4), round(yc, 4)), d=round(2 * rc, 4), d_min_max=(round(2 * dd.min(), 4), round(2 * dd.max(), 4)),
                       glebokosc=round(-9 + dno + 8, 4), d_wejscie=round(2 * r_wej, 3), d_sufit=round(2 * r_suf, 3),
                       scianka_do_krawedzi=round(float(tr[1] - tr[0]), 4), r_os=round(math.hypot(xc, yc), 4), kat=round(math.degrees(math.atan2(yc, xc)), 3))
    W['kieszenie'] = kie
    # rowek klucza
    ks = {}
    for u in (43.5, 44.5, 46.0, 48.0, 49.0):
        for z in (-7.9, -6.75, -5.6):
            o = (u * cu, u * su, z)
            tp = S.pierwsze(o, (-su, cu, 0)); tm = S.pierwsze(o, (su, -cu, 0))
            ks['u%.1f_z%.2f' % (u, z)] = None if (tp is None or tm is None) else (round(tp + tm, 4), round((tp - tm) / 2, 4))
    for u in (43.5, 45.0, 47.0, 49.0):
        t = S.pierwsze((u * cu, u * su, -9), (0, 0, 1))
        ks['h_u%.1f' % u] = round(-9 + t + 8, 4)
    t = S.pierwsze((46 * cu, 46 * su, -6.75), (-cu, -su, 0))
    ks['r0'] = round(46 - t, 4)
    for v in (-1.5, 0, 1.5):
        t = S.pierwsze((46 * cu - su * v, 46 * su + cu * v, -6.75), (-cu, -su, 0))
        ks['r0_v%.1f' % v] = round(46 - t, 4)
    W['rowek_klucza'] = ks
    return S, W
if __name__ == '__main__':
    for nazwa in sys.argv[1:] or ['ramka_plytka_okragla_ramkowa_wieczorna_v2.stl', 'ramka_plytka_okragla_ramkowa_poranna_v2.stl']:
        S, W = wyniki_plytki(nazwa)
        print('=====', nazwa)
        for k, v in W.items():
            print(k, v)