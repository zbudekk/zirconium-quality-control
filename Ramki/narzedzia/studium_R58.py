# -*- coding: utf-8 -*-
"""studium_R58.py - rachunek luzow dla R58 (plytka okragla na ramke: magnesy, polki wkladki, klucz, rowek pokrywki).

Czyta parametry.json (rzedy gniazd ev_rows / mo_rows; wymiary rowka klucza i zebra z kluczy R58) i liczy dla obu typow plytki
odleglosci nowych cech od otworow o3, obrysow gniazd i krawedzi. Uruchomienie: python studium_R58.py [--rm 45] [--polka 10]
[--slot_r0 46 --slot_h 5 --zebro_w 3 --zebro_r0 46.5 --zebro_h 4.5]. Domyslne wartosci rowka i zebra = parametry.json.
Runda 2 (B1 recenzji): kolek klucza zastapiony zebrem przy scieciu; sciecie NIE blokuje obrotu (plytka wnika w sciecie wkladki
tylko 0,244 przy luzie 0,4) - obrot blokuje zebro, ktore nie miesci sie w kieszeni magnesu (warunek nizej); okno wejscia liczy K-67.
Runda 3 (P1 recenzji rundy 2): czesc zebra nad wierzchem wkladki konczy sie na round_key_rib_top_r1 (--zebro_r1) - warunek zapasu
do lica kolnierza pokrywki w najgorszym ustawieniu (plytka o luz otworu + pokrywka o luz pokrywki od strony zebra); K-67 mierzy z siatek.
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


def scianka_3d_rowek_gniazda(P, typ, kat, r0, w, h, R_scie):
    """Najmniejsza odleglosc 3D powierzchni rowka klucza (sufit Z -T + h, boki, czolo; u od r0 do sciecia) od powierzchni gniazd
    i rynienek (stozek 15 st. od Z 0 do -socket_depth, dno) - probkowanie co ok. 0,1 mm (rowek) i 0,05 mm (profil gniazda)."""
    T, dep = P['plate_thickness'], P['socket_depth']
    t = math.tan(math.radians(P['socket_wall_angle']))
    c, s = math.cos(math.radians(kat)), math.sin(math.radians(kat))
    zc = -T + h
    pkt = []
    nu = 40
    for i in range(nu + 1):
        u = r0 + (R_scie - r0) * i / nu
        for j in range(19):
            pkt.append((u, -w / 2 + w * j / 18, zc))
        for k in range(int(round(h / 0.25)) + 1):
            pkt += [(u, w / 2, zc - k * 0.25), (u, -w / 2, zc - k * 0.25)]
    for j in range(19):
        for k in range(int(round(h / 0.25)) + 1):
            pkt.append((r0, -w / 2 + w * j / 18, zc - k * 0.25))
    wiersze = P['ev_rows'] if typ == 'wieczorna' else P['mo_rows']
    best = (1e9, None)
    for wr in wiersze:
        for x0 in wr['x']:
            if wr['type'] == 'round':
                a, b, r_top = (x0, wr['y']), (x0, wr['y']), wr['d'] / 2
            else:
                hl = wr['l'] / 2 - wr['w'] / 2
                a, b, r_top = (x0 - hl, wr['y']), (x0 + hl, wr['y']), wr['w'] / 2
            for (u, v, z) in pkt:
                x, y = u * c - v * s, u * s + v * c
                dx, dy = b[0] - a[0], b[1] - a[1]
                L2 = dx * dx + dy * dy
                tt = 0.0 if L2 == 0 else max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / L2))
                rh = math.hypot(x - (a[0] + tt * dx), y - (a[1] + tt * dy))
                if rh - r_top > best[0] + 2:
                    continue
                d = min(math.hypot(rh - (r_top - dep * q / 80 * t), z + dep * q / 80) for q in range(81))
                d = min(d, min(math.hypot(rh - (r_top - dep * t) * q / 40, z + dep) for q in range(41)))
                if d < best[0]:
                    best = (d, '%s x %g y %g' % (wr['type'], x0, wr['y']))
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rm', type=float, default=45.0, help='promien osi magnesow (kieszenie plytki, kieszenie Halla)')
    ap.add_argument('--polka', type=float, default=10.0, help='bok polki czujnika (kwadrat wokol osi magnesu)')
    ap.add_argument('--wyst', type=float, default=47.0, help='promien wewnetrzny wystepu (polki obwodowej)')
    P = parametry()
    ap.add_argument('--slot_w', type=float, default=P['round_key_slot_w'])
    ap.add_argument('--slot_r0', type=float, default=P['round_key_slot_r0'])
    ap.add_argument('--slot_h', type=float, default=P['round_key_slot_h'])
    ap.add_argument('--zebro_w', type=float, default=P['round_key_rib_w'])
    ap.add_argument('--zebro_r0', type=float, default=P['round_key_rib_r0'])
    ap.add_argument('--zebro_h', type=float, default=P['round_key_rib_h'])
    ap.add_argument('--zebro_r1', type=float, default=P['round_key_rib_top_r1'], help='koniec czesci zebra nad wierzchem wkladki (runda 3)')
    a = ap.parse_args()
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
        d3, kto = scianka_3d_rowek_gniazda(P, typ, katy['D'], a.slot_r0, a.slot_w, a.slot_h, math.sqrt(R * R - (P['round_flat_w'] / 2) ** 2))
        war('rowek klucza (do Z %.1f): scianka 3D do gniazd/rynienki (%s)' % (-T + a.slot_h, kto), d3, 1.5)
    w = P['round_flat_w']
    dist = math.sqrt(R * R - (w / 2) ** 2)
    luz_o = P['round_insert_clearance']
    do = dist + luz_o
    luz = (a.slot_w - a.zebro_w) / 2
    print('\nKlucz: zebro %.1f w rowku %.1f -> luz %.2f na strone; obrot +-%.2f st. (na r %.1f); przesuniecie gniazda na r 40: %.2f (+ luz promieniowy %.1f)' % (
        a.zebro_w, a.slot_w, luz, math.degrees(luz / a.zebro_r0), a.zebro_r0, luz / a.zebro_r0 * 40, luz_o))
    war('przesuniecie gniazda od obrotu + luz promieniowy (kalibracja toleruje 1,25)', luz / a.zebro_r0 * 40 + luz_o, 1.25, wiekszy=False)
    war('zebro nie miesci sie w kieszeni magnesu: zasieg zebra (lico sciecia wkladki %.3f) - (rm + md/2)' % do, do - (a.rm + md / 2), 1.5)
    war('czolo zebra - koniec rowka plytki (r %.1f - %.1f)' % (a.zebro_r0, a.slot_r0), a.zebro_r0 - a.slot_r0, 0.4)
    war('nad zebrem: rowek %.1f - zebro %.1f' % (a.slot_h, a.zebro_h), a.slot_h - a.zebro_h, 0.4)
    war('zebro wyzsze niz kieszen magnesu (plytka w zlym obrocie nie siada): %.1f - %.1f' % (a.zebro_h, mdep), a.zebro_h - mdep, 1.0)
    c_z = P['round_key_rib_chamfer']
    war('wierzch zebra nad wkladka: dlugosc promieniowa (r1 - faza) - (r0 + faza) = %.1f - %.1f' % (a.zebro_r1 - c_z, a.zebro_r0 + c_z),
        (a.zebro_r1 - c_z) - (a.zebro_r0 + c_z), 0.5)
    rk = P['plate_round_d'] / 2 + P['cover_clearance'] - luz_o - P['cover_clearance']
    war('czesc zebra nad wierzchem wkladki: lico kolnierza w najgorszym ustawieniu r %.2f - koniec r1 %.2f (w rzucie)' % (rk, a.zebro_r1), rk - a.zebro_r1, 0.2)
    print('Sciecie: wnikanie plytki w sciecie wkladki %.3f < luz %.1f - sciecie NIE blokuje obrotu (tylko znak wzrokowy i oparcie zebra); '
          'plytka w zlym obrocie lezy na zebrze %.1f nad polka: przechyl ok. %.1f st.' % (R - do, luz_o, a.zebro_h, math.degrees(math.atan2(a.zebro_h, do + R))))
    zw = P['insert_opening'] / 2 + P['insert_wall_w']
    Ro = R + luz_o
    war('wkladka: scianka w osi (obrys %.1f, otwor o%.1f)' % (2 * zw, 2 * Ro), zw - Ro, 1.5)
    war('wkladka: dno w osi po odjeciu rowka kablowego (wystep r %.1f)' % a.wyst, zw - a.wyst - P['wire_rabbet_w'], 1.5)
    print('\nBLEDY: %d' % bledy[0])
    return 1 if bledy[0] else 0


if __name__ == '__main__':
    sys.exit(main())
