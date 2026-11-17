# -*- coding: utf-8 -*-
"""R59 test koncowy T4 - wlasny pomiar siatek koordynatora (nie skrypty wykonawcy ani recenzenta).

Uzycie: python t4_pomiar_siatek.py <katalog Ramki>
Czyta: parametry.json (nowy uklad), archiwum/parametry_przed_R59_2026-11-14.json (stary uklad),
R59_wdrozenie_zmiany.md (objetosci z raportu), wyniki_v2/stl/ramka_plytka_*_v2.stl (12 plikow).
Metoda: promien pionowy z gory liczony wprost z trojkatow (numpy), bez bibliotek do sledzenia promieni.
Kryteria (plan pkt 14): szczelnosc, gabaryt, objetosc = raport +- 0,01 cm3; dno kazdego gniazda z = 4,00 +- 0,05
w punktach 2,0 mm od srodka; w srodkach gniazd STAREGO ukladu lezacych >= 1 mm poza nowymi obrysami
wierzch z = 8,00 +- 0,05.
"""
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import trimesh

RAMKI = Path(sys.argv[1])
TOL = 0.05
P = json.loads((RAMKI / "parametry.json").read_text(encoding="utf-8"))["plytka"]
PS = json.loads((RAMKI / "archiwum" / "parametry_przed_R59_2026-11-14.json").read_text(encoding="utf-8"))["plytka"]
GRUB = P["plate_thickness"]["value"]
GLEB = P["socket_depth"]["value"]
BOK = P["plate_size"]["value"]
SR_OKR = P["plate_round_d"]["value"]
RELIEF = P["number_relief_h"]["value"]
R_STOZKA = P["marker_cone_d"]["value"] / 2
DNO = GRUB - GLEB


def objetosci_z_raportu():
    out = {}
    tekst = (RAMKI / "R59_wdrozenie_zmiany.md").read_text(encoding="utf-8")
    wzor = r"\| `(ramka_plytka_[a-z0-9_]+_v2\.stl)`[^|]*\| [0-9a-f]{64} \| ([0-9]+,[0-9]+) \|"
    for m in re.finditer(wzor, tekst):
        out[m.group(1)] = float(m.group(2).replace(",", "."))
    return out


def cechy(par, pref):
    """Lista cech ukladu z rzedow: ("round", x, y, d) albo ("trough", x, y, l, w)."""
    out = []
    for r in par[pref + "_rows"]["value"]:
        for x in r["x"]:
            if r["type"] == "round":
                out.append(("round", x, r["y"], r["d"]))
            else:
                out.append(("trough", x, r["y"], r["l"], r["w"]))
    return out


def odl_do_obrysu(c, x, y):
    """Odleglosc punktu od obrysu gornego cechy (ujemna = wewnatrz)."""
    if c[0] == "round":
        return math.hypot(x - c[1], y - c[2]) - c[3] / 2
    pol = (c[3] - c[4]) / 2
    dx = max(abs(x - c[1]) - pol, 0.0)
    return math.hypot(dx, y - c[2]) - c[4] / 2


class Siatka:
    def __init__(self, plik):
        self.m = trimesh.load_mesh(str(plik), process=True)
        t = self.m.triangles
        self.a, self.b, self.c = t[:, 0], t[:, 1], t[:, 2]
        a, b, c = self.a, self.b, self.c
        self.den = (b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1])
        self.ok = np.abs(self.den) > 1e-12

    def z_gora(self, x, y):
        """Najwyzszy punkt siatki nad (x, y); None gdy promien nie trafia."""
        a, b, c, den = self.a, self.b, self.c, self.den
        with np.errstate(divide="ignore", invalid="ignore"):
            l1 = ((b[:, 1] - c[:, 1]) * (x - c[:, 0]) + (c[:, 0] - b[:, 0]) * (y - c[:, 1])) / den
            l2 = ((c[:, 1] - a[:, 1]) * (x - c[:, 0]) + (a[:, 0] - c[:, 0]) * (y - c[:, 1])) / den
        l3 = 1 - l1 - l2
        e = -1e-9
        w = self.ok & (l1 >= e) & (l2 >= e) & (l3 >= e)
        if not w.any():
            return None
        return float((l1[w] * a[w, 2] + l2[w] * b[w, 2] + l3[w] * c[w, 2]).max())


def blisko(z, cel):
    return z is not None and abs(z - cel) <= TOL


def main():
    obj = objetosci_z_raportu()
    typy = [
        ("wieczorna", "ev", ["", "_n1", "_n2", "_n3"], False),
        ("poranna", "mo", ["", "_n4", "_n5", "_n6"], False),
        ("okragla_wieczorna", "ev", ["", "_n8"], True),
        ("okragla_poranna", "mo", ["", "_n9"], True),
    ]
    bledy = 0
    lp = 0
    suma = dict(gniazd=0, gniazd_ok=0, sond_dna=0, sond_scian=0, sond_wierzchu=0, odwrotne=0, odwrotne_ok=0, pominiete=0)
    for typ, pref, sufiksy, okragla in typy:
        nowe = cechy(P, pref)
        stare = cechy(PS, pref)
        zn_nowe = [tuple(v) for v in P[pref + "_marker_pos"]["value"].values()]
        zn_stare = [tuple(v) for v in PS[pref + "_marker_pos"]["value"].values()]
        baza = "wieczorna" if pref == "ev" else "poranna"
        dolki = []
        cyfra = None
        if okragla:
            dolki = [tuple(v) for v in P["code_dimples_round"]["value"][baza].values()]
            cyfra = P["number_pos_round"]["value"][baza]
        # punkty kontroli odwrotnej: srodki starych gniazd, os starych rynienek co 5 mm, stare stozki
        kandydaci = []
        for c in stare:
            if c[0] == "round":
                kandydaci.append((c[1], c[2], "stare gniazdo fi%g" % c[3]))
            else:
                pol = (c[3] - c[4]) / 2
                for dx in np.arange(-pol, pol + 0.01, 5.0):
                    kandydaci.append((c[1] + float(dx), c[2], "stara rynienka"))
        kandydaci += [(x, y, "stary stozek") for x, y in zn_stare]
        for suf in sufiksy:
            lp += 1
            nazwa = "ramka_plytka_%s%s_v2.stl" % (typ, suf)
            s = Siatka(RAMKI / "wyniki_v2" / "stl" / nazwa)
            m = s.m
            lo, hi = m.bounds
            wym = hi - lo
            z_ocz = GRUB + (RELIEF if suf else 0.0)
            xy_ocz = SR_OKR if okragla else BOK
            vol = m.volume / 1000.0
            w_szczelna = bool(m.is_watertight) and m.body_count == 1 and bool(m.is_winding_consistent)
            w_gab = (abs(wym[0] - xy_ocz) <= TOL and abs(wym[1] - xy_ocz) <= TOL
                     and abs(wym[2] - z_ocz) <= TOL and abs(lo[2]) <= TOL)
            w_srodek = abs(lo[0] + hi[0]) <= 2 * TOL and abs(lo[1] + hi[1]) <= 2 * TOL
            w_vol = nazwa in obj and abs(vol - obj[nazwa]) <= 0.01
            g_ok = 0
            zle = []
            for c in nowe:
                x0, y0 = c[1], c[2]
                dna = [s.z_gora(x0 + dx, y0 + dy) for dx, dy in ((2.0, 0), (-2.0, 0), (0, 2.0), (0, -2.0))]
                suma["sond_dna"] += 4
                dobre = all(blisko(z, DNO) for z in dna)
                if c[0] == "round":
                    r = c[3] / 2
                    for k in range(8):
                        kat = math.pi * k / 4 + 0.2
                        zs = s.z_gora(x0 + (r - 0.3) * math.cos(kat), y0 + (r - 0.3) * math.sin(kat))
                        zw = s.z_gora(x0 + (r + 0.5) * math.cos(kat), y0 + (r + 0.5) * math.sin(kat))
                        suma["sond_scian"] += 1
                        suma["sond_wierzchu"] += 1
                        if zs is None or not (DNO - TOL <= zs <= GRUB - 0.5):
                            dobre = False
                        if not blisko(zw, GRUB):
                            dobre = False
                    zo = s.z_gora(x0, y0)   # otwor przelotowy: promien nie trafia w nic
                    if zo is not None and zo > 0.5:
                        dobre = False
                else:
                    pol = (c[3] - c[4]) / 2
                    for sx in (-1, 1):
                        for yy in (c[4] / 2 + 0.5, -(c[4] / 2 + 0.5)):
                            zw = s.z_gora(x0 + sx * pol * 0.5, y0 + yy)
                            suma["sond_wierzchu"] += 1
                            if not blisko(zw, GRUB):
                                dobre = False
                        zk = s.z_gora(x0 + sx * (pol + c[4] / 2 + 0.5), y0)
                        suma["sond_wierzchu"] += 1
                        if not blisko(zk, GRUB):
                            dobre = False
                        zd = s.z_gora(x0 + sx * (pol + c[4] / 2 - 2.0), y0)
                        suma["sond_dna"] += 1
                        if not blisko(zd, DNO):
                            dobre = False
                suma["gniazd"] += 1
                if dobre:
                    g_ok += 1
                    suma["gniazd_ok"] += 1
                else:
                    zle.append((c, dna))
            o_ok = 0
            o_n = 0
            o_pom = 0
            o_zle = []
            for x, y, opis in kandydaci:
                d = min(odl_do_obrysu(c, x, y) for c in nowe)
                d = min([d] + [math.hypot(x - zx, y - zy) - R_STOZKA for zx, zy in zn_nowe])
                d = min([d] + [math.hypot(x - px, y - py) - 1.0 for px, py in dolki])
                if cyfra is not None:
                    d = min(d, max(abs(x - cyfra[0]) - 1.8, abs(y - cyfra[1]) - 2.5))
                if d < 1.0:
                    o_pom += 1
                    continue
                o_n += 1
                z = s.z_gora(x, y)
                if blisko(z, GRUB):
                    o_ok += 1
                else:
                    o_zle.append((x, y, opis, z))
            suma["odwrotne"] += o_n
            suma["odwrotne_ok"] += o_ok
            suma["pominiete"] += o_pom
            wynik = w_szczelna and w_gab and w_srodek and w_vol and g_ok == len(nowe) and o_ok == o_n
            bledy += 0 if wynik else 1
            print("%2d %-44s %s | szczelna, 1 bryla: %s | gabaryt %.4f x %.4f x %.4f (ocz. %g x %g x %g): %s | "
                  "objetosc %.4f cm3 (raport %s): %s | gniazda (dno %.2f, sciana, wierzch): %d/%d | "
                  "odwrotne (wierzch %.2f): %d/%d, pominiete %d"
                  % (lp, nazwa, "OK  " if wynik else "FAIL", w_szczelna, wym[0], wym[1], wym[2], xy_ocz, xy_ocz, z_ocz,
                     w_gab and w_srodek, vol, obj.get(nazwa), w_vol, DNO, g_ok, len(nowe), GRUB, o_ok, o_n, o_pom))
            for c, dna in zle[:5]:
                print("     ZLE gniazdo", c, "dno:", dna)
            for o in o_zle[:5]:
                print("     ZLE odwrotne", o)
    print("RAZEM: plikow %d, FAIL %d; gniazd %d/%d; sondy dna %d, scian %d, wierzchu %d; punkty odwrotne %d/%d "
          "(pominiete jako pokrywajace sie z nowymi cechami: %d)"
          % (lp, bledy, suma["gniazd_ok"], suma["gniazd"], suma["sond_dna"], suma["sond_scian"], suma["sond_wierzchu"],
             suma["odwrotne_ok"], suma["odwrotne"], suma["pominiete"]))
    sys.exit(1 if bledy else 0)


main()
