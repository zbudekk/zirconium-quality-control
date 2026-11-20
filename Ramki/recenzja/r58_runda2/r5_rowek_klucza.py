import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
FL = -45.0; cu, su = math.cos(math.radians(FL)), math.sin(math.radians(FL))
def kier(az, el):
    return np.array((math.cos(math.radians(el)) * math.cos(math.radians(az)), math.cos(math.radians(el)) * math.sin(math.radians(az)), math.sin(math.radians(el))))
def klasa(p):
    r = math.hypot(p[0], p[1]); u = p[0] * cu + p[1] * su
    if abs(p[2] + 8) < 1e-3: return 'spod'
    if r > 49.9 or u > 49.33: return 'obrys'
    if r > 49.15 and -2.51 < p[2] < -1.49: return 'rowek_pokr'
    if p[2] > -0.01 or (r > 49.45 and p[2] > -0.55): return 'wierzch'
    return 'wewn'
for nazwa in ['ramka_plytka_okragla_ramkowa_wieczorna_v2.stl', 'ramka_plytka_okragla_ramkowa_poranna_v2.stl']:
    S = Siatka(os.path.join(STL_NEW, nazwa), shift=(0, 0, -8))
    print('=====', nazwa)
    # obrys i rowek pokrywki
    angs = np.arange(0, 360, 1.0)
    for z in (-1.0, -2.0, -4.0, -7.5):
        rr = []
        for a in angs:
            if abs(((a - FL) + 180) % 360 - 180) < 12: continue
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            t = S.pierwsze((60 * c, 60 * s, z), (-c, -s, 0)); rr.append(60 - t)
        print('  promien Z %.1f: %.4f..%.4f' % (z, min(rr), max(rr)))
    for v in (-4.9, 4.9):
        for z in (-4.0, -7.5, -2.0, -1.0):
            o = (cu * 60 - su * v, su * 60 + cu * v, z); t = S.pierwsze(o, (-cu, -su, 0))
            print('  sciecie v %+.1f Z %.1f: %.4f' % (v, z, 60 - t))
    # rowek klucza
    for u in (46.2, 47.0, 48.0, 49.0, 49.3):
        out = []
        for z in (-7.9, -5.5, -3.1):
            o = (u * cu, u * su, z)
            tp = S.pierwsze(o, (-su, cu, 0)); tm = S.pierwsze(o, (su, -cu, 0))
            out.append('Z %.1f: %.4f (os %.4f)' % (z, tp + tm, (tp - tm) / 2))
        tz = S.pierwsze((u * cu, u * su, -9), (0, 0, 1))
        print('  rowek u %.1f: %s; sufit Z %.4f' % (u, '; '.join(out), -9 + tz))
    for z in (-7.5, -5.0, -3.2):
        for v in (-1.5, 0.0, 1.5):
            t = S.pierwsze((48 * cu - su * v, 48 * su + cu * v, z), (-cu, -su, 0))
            print('  koniec rowka (v %+.1f, Z %.1f): r0 %.4f' % (v, z, 48 - t))
    # material nad rowkiem w osi przy scieciu: pionowo od sufitu
    for u in (46.5, 48.0, 49.0, 49.25, 49.3):
        o = np.array((u * cu, u * su, -3.0 + 1e-4)); tr, sg = S.promien(o, (0, 0, 1))
        print('  nad sufitem rowka u %.2f: przeciecia w gore %s' % (u, np.round(-3 + tr, 4)))
    # scianki 3D z sufitu i bokow rowka
    best = {}
    for u in np.arange(46.1, 49.31, 0.2):
        for v in np.arange(-1.7, 1.71, 0.34):
            o = (u * cu - v * su, u * su + v * cu, -3.0 + 1e-4)
            for el in (90, 75, 60, 45, 30):
                for az in ([0] if el == 90 else range(0, 360, 15)):
                    d = kier(az, el); tr, sg = S.promien(o, d)
                    if not len(tr): continue
                    p = np.array(o) + d * tr[0]; kl = klasa(p)
                    if kl not in best or tr[0] < best[kl][0]:
                        best[kl] = (round(float(tr[0]), 3), tuple(np.round(p, 2)), round(u, 2), round(v, 2), el, az)
    print('  sufit rowka -> ', best)
    best = {}
    for u in np.arange(46.1, 49.31, 0.2):
        for z in (-7.6, -6.0, -4.5, -3.2):
            for sgn in (1, -1):
                for el in (-30, 0, 30, 60):
                    for daz in (-60, -30, 0, 30, 60):
                        d = kier(FL + sgn * 90 + daz, el)
                        tr, sg = S.promien((u * cu, u * su, z), d)
                        if len(tr) < 2: continue
                        p = np.array((u * cu, u * su, z)) + d * tr[1]; kl = klasa(p)
                        w = tr[1] - tr[0]
                        if kl not in best or w < best[kl][0]:
                            best[kl] = (round(float(w), 3), tuple(np.round(p, 2)), round(u, 2), z, sgn, el, daz)
    print('  boki rowka -> ', best)
    # czolo rowka (r0 46) w strone srodka i w gore
    best = {}
    for v in np.arange(-1.7, 1.71, 0.34):
        for z in (-7.6, -6.0, -4.5, -3.2):
            for el in (0, 30, 60):
                for daz in (-45, 0, 45):
                    d = kier(FL + 180 + daz, el); o = (47.0 * cu - su * v, 47.0 * su + cu * v, z)
                    tr, sg = S.promien(o, d)
                    if len(tr) < 2: continue
                    p = np.array(o) + d * tr[1]; kl = klasa(p); w = tr[1] - tr[0]
                    if kl not in best or w < best[kl][0]:
                        best[kl] = (round(float(w), 3), tuple(np.round(p, 2)), round(v, 2), z, el, daz)
    print('  czolo rowka -> ', best)