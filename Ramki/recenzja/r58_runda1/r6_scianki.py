import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
FLAT = -45.0
cu, su = math.cos(math.radians(FLAT)), math.sin(math.radians(FLAT))
OSIE = {'A': (-31.8198, -31.8198), 'B': (-31.8198, 31.8198), 'C': (31.8198, 31.8198)}
def kier(az, el):
    return np.array((math.cos(math.radians(el)) * math.cos(math.radians(az)), math.cos(math.radians(el)) * math.sin(math.radians(az)), math.sin(math.radians(el))))
def klasa(p):
    r = math.hypot(p[0], p[1]); u = p[0] * cu + p[1] * su
    if abs(p[2] + 8) < 1e-3: return 'spod'
    if r > 49.9 or u > 49.33: return 'obrys'
    if r > 49.15 and -2.51 < p[2] < -1.49: return 'rowek_pokr'
    if p[2] > -0.01 or (r > 49.45 and p[2] > -0.55): return 'wierzch'
    return 'wewn'
def scianka(S, o, d, pomin_pierwsze=True):
    o = np.array(o, float)
    tr, sg = S.promien(o, d)
    if len(tr) < (2 if pomin_pierwsze else 1):
        return None
    t0 = tr[0] if pomin_pierwsze else 0.0
    t1 = tr[1] if pomin_pierwsze else tr[0]
    p = o + d * t1
    return (t1 - t0, klasa(p), tuple(np.round(p, 2)))
for nazwa in ['ramka_plytka_okragla_ramkowa_wieczorna_v2.stl', 'ramka_plytka_okragla_ramkowa_poranna_v2.stl']:
    S = Siatka(os.path.join(STL_NEW, nazwa), shift=(0, 0, -8))
    print('=====', nazwa)
    # sufit rowka klucza i kieszeni: promienie z sufitu (start w materiale, bez pomijania)
    def sufit(punkty, z):
        best = {}
        for (x, y) in punkty:
            o = (x, y, z + 1e-4)
            for el in (90, 75, 60, 45):
                for az in ([0] if el == 90 else range(0, 360, 20)):
                    w = scianka(S, o, kier(az, el), pomin_pierwsze=False)
                    if w is None: continue
                    kl = w[1]
                    if kl not in best or w[0] < best[kl][0]:
                        best[kl] = (round(w[0], 3), w[2], el, az)
        return best
    pts = [(u * cu - v * su, u * su + v * cu) for u in np.arange(43.1, 49.3, 0.3) for v in np.arange(-1.7, 1.71, 0.34)]
    print('rowek klucza sufit -> ', sufit(pts, -5.5))
    for k, (cx, cy) in OSIE.items():
        pts = [(cx + dx, cy + dy) for dx in np.arange(-2.4, 2.41, 0.4) for dy in np.arange(-2.4, 2.41, 0.4) if dx * dx + dy * dy <= 2.45 ** 2]
        print('kieszen %s sufit -> ' % k, sufit(pts, -5.8))
    # sciany boczne rowka klucza: z osi rowka, pomijajac pierwsze trafienie (sciana rowka)
    best = {}
    for u in np.arange(43.2, 49.3, 0.3):
        for z in (-7.6, -6.75, -5.6):
            for sgn in (1, -1):
                for el in (0, 30, 60):
                    for daz in (-45, -20, 0, 20, 45):
                        w = scianka(S, (u * cu, u * su, z), kier(FLAT + sgn * 90 + daz, el))
                        if w is None: continue
                        if w[1] not in best or w[0] < best[w[1]][0]:
                            best[w[1]] = (round(w[0], 3), w[2], round(u, 2), z, el, daz)
    print('rowek klucza boki -> ', best)
    # sciany boczne kieszeni z osi (pomijajac pierwsze trafienie), z elewacja
    for k, (cx, cy) in OSIE.items():
        best = {}
        for z in (-7.6, -6.9, -6.0):
            for az in np.arange(0, 360, 3):
                for el in (0, 30, 60):
                    w = scianka(S, (cx, cy, z), kier(az, el))
                    if w is None: continue
                    if w[1] not in best or w[0] < best[w[1]][0]:
                        best[w[1]] = (round(w[0], 3), w[2], z, float(az), el)
        print('kieszen %s boki -> ' % k, best)
    # dno rowka pokrywki -> wnetrze (tylko poziomo i do 30 st.)
    best = {}
    for az0 in np.arange(0, 360, 0.5):
        for z in (-1.52, -2.0, -2.48):
            c, s = math.cos(math.radians(az0)), math.sin(math.radians(az0))
            rr = 49.28 if abs(((az0 - FLAT) + 180) % 360 - 180) < 10 else 49.6
            o = (rr * c, rr * s, z)
            for daz in (-40, -20, 0, 20, 40):
                for el in (-30, 0, 30):
                    w = scianka(S, o, kier(az0 + 180 + daz, el))
                    if w is None: continue
                    if w[1] not in best or w[0] < best[w[1]][0]:
                        best[w[1]] = (round(w[0], 3), w[2], float(az0), z, daz, el)
    print('rowek pokrywki dno -> ', best)