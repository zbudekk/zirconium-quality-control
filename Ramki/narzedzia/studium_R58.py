# -*- coding: utf-8 -*-
"""studium_R58.py - rachunek luzow dla R58 (plytka okragla na ramke: magnesy, polki wkladki, klucz, rowek pokrywki).

Czyta parametry.json (rzedy gniazd ev_rows / mo_rows) i liczy dla obu typow plytki odleglosci nowych cech od
otworow o3, obrysow gniazd i krawedzi. Uruchomienie: python studium_R58.py [--rm 45] [--polka 10]
Tylko biblioteka standardowa. Wynik na stdout; kod 0 = wszystkie warunki spelnione.
"""
import argparse
import json
import math
import os
import sys

KAT = os.path.dirname(os.path.abspath(__file__))


def parametry():
    with open(os.path.join(KAT, '..', 'parametry.json'), encoding='utf-8') as f:
        surowe = json.load(f)
    P = {}
    for grupa, tresc in surowe.items():
        if grupa.startswith('_'):
            continue
        for k, v in tresc.items():
            P[k] = v['value'] if isinstance(v, dict) and 'value' in v else v
    return P


def gniazda(P, typ):
    wiersze = P['ev_rows'] if typ == 'wieczorna' else P['mo_rows']
    pitch = P['ev_trough_hole_pitch'] if typ == 'wieczorna' else P['mo_trough_hole_pitch']
    t = math.tan(math.radians(P['socket_wall_angle']))
    okr, ryn, otw = [], [], []
    for w in wiersze:
        for x in w['x']:
            if w['type'] == 'round':
                okr.append((x, w['y'], w['d'] / 2, w['d'] / 2 - P['socket_depth'] * t))
                otw.append((x, w['y']))
            else:
                ryn.append((x, w['y'], w['l'], w['w']))
                n = P['trough_hole_count']
                for i in range(n):
                    otw.append((x + (i - (n - 1) / 2) * pitch, w['y']))
    return okr, ryn, otw


def odl_pkt_prostokat(p, x0, x1, y0, y1):
    dx = max(x0 - p[0], 0.0, p[0] - x1)
    dy = max(y0 - p[1], 0.0, p[1] - y1)
    return math.hypot(dx, dy)


def odl_pkt_obrot_prostokat(p, c, kat, u0, u1, v0, v1):
    """prostokat w ukladzie (u wzdluz kierunku kat, v prostopadle), srodek ukladu w c"""
    ca, sa = math.cos(kat), math.sin(kat)
    u = (p[0] - c[0]) * ca + (p[1] - c[1]) * sa
    v = -(p[0] - c[0]) * sa + (p[1] - c[1]) * ca
    return odl_pkt_prostokat((u, v), u0, u1, v0, v1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rm', type=float, default=45.0, help='promien osi magnesow i kolka klucza')
    ap.add_argument('--polka', type=float, default=10.0, help='bok polki czujnika (kwadrat wokol osi magnesu)')
    ap.add_argument('--wyst', type=float, default=47.0, help='promien wewnetrzny wystepu (polki obwodowej)')
    ap.add_argument('--slot_w', type=float, default=3.6)
    ap.add_argument('--slot_r0', type=float, default=43.0)
    ap.add_argument('--slot_h', type=float, default=2.5)
    a = ap.parse_args()
    P = parametry()
    R = P['plate_round_d'] / 2
    T = P['plate_thickness']
    md, mdep = P['magnet_pocket_d'], P['magnet_pocket_depth']
    hole_r = P['socket_hole_d'] / 2
    dep = P['socket_depth']
    bledy = [0]

    def war(opis, wart, prog, wiekszy=True):
        ok = wart >= prog - 1e-9 if wiekszy else wart <= prog + 1e-9
        if not ok:
            bledy[0] += 1
        print('  %-3s %-78s %7.2f %s %g' % ('OK' if ok else 'NIE', opis, wart, '>=' if wiekszy else '<=', prog))

    katy = {'A': 225.0, 'B': 135.0, 'C': 45.0, 'D': -45.0}
    poz = {c: (a.rm * math.cos(math.radians(k)), a.rm * math.sin(math.radians(k))) for c, k in katy.items()}
    print('Osie (promien %.2f): ' % a.rm + ', '.join('%s (%.2f, %.2f)' % (c, poz[c][0], poz[c][1]) for c in 'ABCD'))
    war('scianka kieszen magnesu - krawedz plytki', R - a.rm - md / 2, 1.5)
    war('scianka kieszen magnesu - dno rowka pokrywki (w rzucie; rowek jest 3,3 wyzej)', R - P['cover_groove_depth'] - a.rm - md / 2, 1.5)
    for typ in ('wieczorna', 'poranna'):
        okr, ryn, otw = gniazda(P, typ)
        print('\n== %s: %d gniazd, %d rynienek, %d otworow o3; najdalszy otwor r = %.2f' % (
            typ, len(okr), len(ryn), len(otw), max(math.hypot(*o) for o in otw)))
        war('wystep obwodowy r >= %.1f: odstep od krawedzi najdalszego otworu' % a.wyst,
            a.wyst - max(math.hypot(*o) for o in otw) - hole_r, 3.0)
        for c in 'ABC':
            p = poz[c]
            d_otw = min(math.hypot(p[0] - o[0], p[1] - o[1]) for o in otw) - hole_r - md / 2
            war('magnes %s: scianka kieszen - najblizszy otwor o3 (w rzucie)' % c, d_otw, 1.5)
            nad = [g for g in okr if math.hypot(p[0] - g[0], p[1] - g[1]) < g[2] + md / 2]
            nad_r = [r for r in ryn if odl_pkt_prostokat(p, r[0] - r[2] / 2, r[0] + r[2] / 2, r[1] - r[3] / 2, r[1] + r[3] / 2) < md / 2]
            print('      gniazda nad kieszenia %s (rzuty sie nakladaja): %d okraglych, %d rynienek' % (c, len(nad), len(nad_r)))
        war('scianka pionowa dno gniazda - sufit kieszeni magnesu', T - dep - mdep, 1.5)
        for c in 'ABCD':
            p = poz[c]
            s = a.polka / 2
            d = min(odl_pkt_prostokat(o, p[0] - s, p[0] + s, p[1] - s, p[1] + s) for o in otw) - hole_r
            war('polka %s (%g x %g): odstep od krawedzi najblizszego otworu o3' % (c, a.polka, a.polka), d, 2.5)
        kat = math.radians(katy['D'])
        d = min(odl_pkt_obrot_prostokat(o, (0, 0), kat, a.slot_r0, R + 1, -a.slot_w / 2, a.slot_w / 2) for o in otw) - hole_r
        war('rowek klucza: scianka do najblizszego otworu o3 (w rzucie)', d, 1.5)
        war('rowek klucza: scianka pionowa dno gniazda - sufit rowka', T - dep - a.slot_h, 1.5)
    luz = (a.slot_w - 3.0) / 2
    print('\nKlucz: kolek o3 w rowku %.1f -> luz %.2f na strone; obrot +-%.2f st.; przesuniecie na r 40: %.2f (+ luz promieniowy 0,4)' % (
        a.slot_w, luz, math.degrees(luz / a.rm), luz / a.rm * 40))
    war('przesuniecie gniazda od obrotu + luz promieniowy (kalibracja toleruje 1,25)', luz / a.rm * 40 + 0.4, 1.25, wiekszy=False)
    w = P['round_flat_w']
    dist = math.sqrt(R * R - (w / 2) ** 2)
    luz_o = 0.4
    kat_pl = math.degrees(math.asin(w / 2 / R))
    kat_gr = math.degrees(math.acos((dist + luz_o) / R))
    print('Sciecie: polowa kata sciecia plytki %.2f st.; blokada zgrubna obrotu +-%.2f st.' % (kat_pl, kat_pl - kat_gr))
    zw = P['insert_opening'] / 2 + P['insert_wall_w']
    Ro = R + luz_o
    war('wkladka: scianka w osi (obrys %.1f, otwor o%.1f)' % (2 * zw, 2 * Ro), zw - Ro, 1.5)
    war('wkladka: dno w osi po odjeciu rowka kablowego (wystep r %.1f)' % a.wyst, zw - a.wyst - P['wire_rabbet_w'], 1.5)
    print('\nBLEDY: %d' % bledy[0])
    return 1 if bledy[0] else 0


if __name__ == '__main__':
    sys.exit(main())
