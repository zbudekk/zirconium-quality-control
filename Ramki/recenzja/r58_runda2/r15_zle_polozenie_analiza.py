# Analiza zlego polozenia plytki ramkowej we wkladce okraglej (wymiary zmierzone z siatek)
import math, itertools
import numpy as np
R_PL, FL_PL = 50.0, 49.3559          # plytka: promien (wielobok 49.996..50), sciecie
R_OT, FL_OT = 50.3966, 49.7558       # otwor: promien (min wieloboku), sciecie wkladki
RM = 45.0; R_KIE = 2.598; R_KOL = 1.5; KS_R0 = 43.0; KS_W2 = 1.8
KOLEK = np.array([RM * math.cos(math.radians(-45)), RM * math.sin(math.radians(-45))])
u_ot = np.array([math.cos(math.radians(-45)), math.sin(math.radians(-45))])
KATY_KIE = {'A': 225.0, 'B': 135.0, 'C': 45.0}
HALL = {'A': 225.0, 'B': 135.0, 'C': 45.0}
# obrys plytki (w ukladzie plytki): okrag + sciecie na -45
phi = np.radians(np.arange(0, 360, 0.25))
r = np.full(phi.shape, R_PL)
dphi = np.abs(((np.degrees(phi) + 45) + 180) % 360 - 180)
pol = math.degrees(math.acos(FL_PL / R_PL))
m = dphi < pol
r[m] = FL_PL / np.cos(np.radians(dphi[m]))
OBR = np.c_[r * np.cos(phi), r * np.sin(phi)]
siatka_d = [np.array([dx, dy]) for dx in np.arange(-0.45, 0.451, 0.01) for dy in np.arange(-0.45, 0.451, 0.01) if dx * dx + dy * dy <= 0.45 ** 2]
D = np.array(siatka_d)
def wykonalne(theta, puste):
    c, s = math.cos(math.radians(theta)), math.sin(math.radians(theta))
    Rm = np.array([[c, -s], [s, c]])
    P = OBR @ Rm.T                                    # (n,2)
    # warunek obrysu dla wszystkich przesuniec: |P + d| <= R_OT, (P + d).u <= FL_OT
    pu = P @ u_ot
    ok = (pu.max() + D @ u_ot <= FL_OT + 1e-6)
    # promien: max_i |P_i + d| (wektorowo)
    big = P[::2]
    idx = np.nonzero(ok)[0]
    if len(idx):
        Dd = D[idx]
        mx = np.max(np.hypot(big[None, :, 0] + Dd[:, None, 0], big[None, :, 1] + Dd[:, None, 1]), axis=1)
        ok[idx[mx > R_OT + 1e-6]] = False
    if not ok.any():
        return None
    # kolek: w ktorej wnece
    wyn = []
    for i in np.nonzero(ok)[0]:
        d = D[i]
        gdzie = None
        # rowek klucza (uklad plytki)
        q = Rm.T @ (KOLEK - d)
        uu = q @ u_ot; vv = q @ np.array([-u_ot[1], u_ot[0]])
        if uu - R_KOL >= KS_R0 - 1e-6 and abs(vv) <= KS_W2 - R_KOL + 1e-6:
            gdzie = 'rowek'
        for k in puste:
            a = math.radians(KATY_KIE[k])
            cpk = d + Rm @ np.array([RM * math.cos(a), RM * math.sin(a)])
            if np.hypot(*(KOLEK - cpk)) <= R_KIE - R_KOL + 1e-6:
                gdzie = 'kieszen %s' % k
        if gdzie:
            wyn.append((gdzie, tuple(np.round(d, 3))))
    return wyn
KODY = {1: 'A', 2: 'B', 3: 'AB', 4: 'C', 5: 'AC', 6: 'BC'}
def odczyt(theta, magnesy):
    # magnes w kieszeni k po obrocie o theta trafia na kat KATY_KIE[k] + theta; czujnik, jesli w +-2 st. od HALL
    n = 0
    for k in magnesy:
        a = (KATY_KIE[k] + theta) % 360
        for h, ah in HALL.items():
            if abs(((a - ah) + 180) % 360 - 180) < 3:
                n += {'A': 1, 'B': 2, 'C': 4}[h]
    return n
print('sciecie plytki: polowa kata %.2f st.; wnikanie obrysu w sciecie wkladki przy obrocie: %.3f mm (luz promieniowy %.3f)' % (pol, R_PL - FL_OT, R_OT - R_PL))
for nazwa, puste in [('plytka bazowa (3 kieszenie puste)', 'ABC')] + [('n%d (magnesy %s)' % (n, KODY[n]), ''.join(k for k in 'ABC' if k not in KODY[n])) for n in range(1, 7)]:
    okna = []
    biez = None
    katy = sorted(set([round(x, 2) for x in np.arange(0, 360, 1.0)] + [round(b + x, 2) % 360 for b in (0, 90, 180, 270) for x in np.arange(-4, 4.01, 0.1)]))
    for th in katy:
        w = wykonalne(th, puste)
        if w:
            if biez and th - biez[1] <= 1.0 + 1e-9:
                biez[1] = th; biez[2] = w[0][0]
            else:
                biez = [th, th, w[0][0]]; okna.append(biez)
    opis = []
    for a, b, g in okna:
        thm = (a + b) / 2
        if nazwa.startswith('n'):
            n = int(nazwa[1]); rd = odczyt(thm, KODY[n])
            opis.append('%.2f..%.2f st. (kolek w: %s; odczyt ramki n=%d%s)' % (a, b, g, rd, '' if rd == n else ' ZLY'))
        else:
            opis.append('%.2f..%.2f st. (kolek w: %s)' % (a, b, g))
    print(nazwa + ': plytka lezy PLASKO dla obrotow: ' + '; '.join(opis))
# plytka z magnesem w kieszeni nad kolkiem / bez wneki: lezy na kolku - przechyl
for wys, opis in ((2.0, 'kolek pod pelnym spodem'), (1.8, 'kolek pod kieszenia z magnesem (0,2 wolne)')):
    # podparcie: kolek (r 45 na -45) i wystep po przeciwnej stronie (r ~ 49.7 na 135)
    L = RM + 49.7
    print('przechyl (%s): podniesienie %.1f -> kat %.2f st.; krawedz plytki przy kolku +%.2f; czujniki A i C +%.2f, B +%.2f' % (opis, wys, math.degrees(math.atan(wys / L)), wys * (L + R_PL - RM) / L, wys * (49.7) / L, wys * (49.7 - RM) / L))