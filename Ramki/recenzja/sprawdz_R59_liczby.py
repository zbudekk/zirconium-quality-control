# -*- coding: utf-8 -*-
"""
Recenzent R59 - pkt 8.4 / 8.5 / 8.8 (czesc rachunkowa, python bez pakietow dodatkowych):
 (1) liczby ukladu policzone niezaleznie z parametry.json (git HEAD) - do porownania z planem i protokolem,
 (2) K-05 a-h oraz zgodnosc 4 plikow JSON ukladu z modelem oczekiwanym z parametry.json (pole po polu),
 (3) K-62 (czesc z JSON), decyzje G0 (liczby gniazd, jedna rynienka przednia, numery, quantities bez zmian wzgledem
     archiwum parametrow sprzed R59), zestawienie cech starego ukladu.
Uruchomienie: python sprawdz_R59_liczby.py   (wynik: wyniki/liczby_R59.json + stdout)
"""
import json
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import sprawdz_R59_wspolne as W

BAZA = os.path.join(os.path.dirname(TU), "Ramki")
REF = os.path.join(TU, "ref", "Ramki")
WYN = os.path.join(TU, "wyniki")
PAR = W.wczytaj(os.path.join(REF, "parametry.json"))
PAR_ST = W.wczytaj(os.path.join(REF, "archiwum", "parametry_przed_R59_2026-11-14.json"))
RES = []


def rec(kid, ok, wartosc, oczek, waga="B"):
    RES.append({"id": kid, "wynik": "ZAL" if ok else "NIE", "wartosc": wartosc, "oczekiwane": oczek, "waga": waga})
    print("[%s] %s: %s | oczek: %s" % ("ZAL" if ok else "NIE", kid, wartosc, oczek))


def r3(v):
    return round(v, 3)


def sprawdz_json(typ, ksztalt):
    nazwa = "uklad_gniazd_%s%s.json" % ("okragla_" if ksztalt == "okragla" else "", typ)
    etyk = nazwa.replace("uklad_gniazd_", "").replace(".json", "")
    J = W.wczytaj(os.path.join(BAZA, "wyniki_v2", "json", nazwa))
    m = W.Model(PAR, typ, ksztalt)
    so = J["sockets"]
    rnd = [s for s in so if s["type"] == "round"]
    trg = [s for s in so if s["type"] == "trough"]
    # (a) liczby z rzedow parametry.json
    er = sum(1 for g in m.gniazda if g.rodzaj == "round")
    et = sum(1 for g in m.gniazda if g.rodzaj == "trough")
    rec("K-05a " + etyk, len(rnd) == er and len(trg) == et, "round/trough w JSON %d/%d" % (len(rnd), len(trg)), "%d/%d (z rzedow)" % (er, et))
    # zgodnosc pole po polu z modelem oczekiwanym
    roz = []
    if len(so) != len(m.gniazda):
        roz.append("liczba gniazd %d != %d" % (len(so), len(m.gniazda)))
    for s, g in zip(so, m.gniazda):
        if s["id"] != g.id or abs(s["x"] - g.x) > 1e-9 or abs(s["y"] - g.y) > 1e-9 or s["type"] != g.rodzaj:
            roz.append("id %s: JSON (%s; %s) %s, oczek. id %d (%g; %g) %s" % (s["id"], s["x"], s["y"], s["type"], g.id, g.x, g.y, g.rodzaj))
            continue
        if s["depth"] != m.glebokosc or s["hole_d"] != m.otwor_d:
            roz.append("id %d: depth/hole_d %s/%s" % (g.id, s["depth"], s["hole_d"]))
        if g.rodzaj == "round":
            db = g.d - 2 * m.glebokosc * m.tan
            if abs(s["d_top"] - g.d) > 1e-9 or abs(s["d_bottom"] - db) > 0.01:
                roz.append("id %d: d_top %s d_bottom %s (oczek. %g / %.4f)" % (g.id, s["d_top"], s["d_bottom"], g.d, db))
        else:
            if (s["l"], s["w"], s["hole_pitch"], s["hole_count"], s.get("angle", 0)) != (g.l, g.w, g.pitch, g.n_otw, 0):
                roz.append("id %d: rynienka %s" % (g.id, s))
    rec("JSON=parametry/sockets " + etyk, not roz, "gniazd %d, roznic %d %s" % (len(so), len(roz), roz[:5]), "kazde pole = model z parametry.json")
    roz = []
    for mk, z in zip(J["markers"], m.znaczniki):
        if mk["corner"] != z.nazwa or abs(mk["x"] - z.x) > 1e-9 or abs(mk["y"] - z.y) > 1e-9 or mk["d"] != m.marker_d or mk["depth"] != m.marker_gl:
            roz.append(mk)
    for dk in J["code_dimples"]:
        d = m.dolki[dk["bit"]]
        if abs(dk["x"] - d.x) > 1e-9 or abs(dk["y"] - d.y) > 1e-9 or dk["d"] != m.dolek_d or dk["depth"] != m.dolek_gl:
            roz.append(dk)
    nr = J.get("number_relief")
    if m.cyfra is None:
        if nr is not None:
            roz.append(nr)
    elif nr is None or abs(nr["x"] - m.cyfra[0]) > 1e-9 or abs(nr["y"] - m.cyfra[1]) > 1e-9 or nr["text_h"] != m.cyfra_h or nr["relief_h"] != m.relief_h:
        roz.append(nr)
    if J["thickness"] != m.gr or len(J["markers"]) != 3 or len(J["code_dimples"]) != 4:
        roz.append("thickness / liczba markers / code_dimples")
    if ksztalt == "okragla":
        f = J["flat"]
        if J["shape"] != "round" or J["d"] != 2 * m.R or J["size"] != 2 * m.R or abs(f["dist"] - m.flat_dist) > 1e-3 or \
                f["angle_deg"] != math.degrees(m.flat_ang) or f["chord_w"] != m.flat_w or J["magnet_pockets"] != [] or "notch" in J:
            roz.append("shape/d/size/flat/magnet_pockets/notch: %s" % json.dumps({k: J.get(k) for k in ("shape", "d", "size", "flat")}))
    else:
        nt = J["notch"]
        if J["shape"] != "square" or J["size"] != m.bok or (nt["x_min"], nt["x_max"], nt["y_min"], nt["y_max"]) != m.wyciecie:
            roz.append("shape/size/notch")
        mp = dict((p["corner"], (p["x"], p["y"], p["d"], p["depth"])) for p in J["magnet_pockets"])
        if mp != dict((k, (v[0], v[1], m.magnes_d, m.magnes_gl)) for k, v in m.magnesy.items()):
            roz.append("magnet_pockets %s" % mp)
    rec("JSON=parametry/reszta " + etyk, not roz, "markers 3, code_dimples 4, number_relief, ksztalt: roznic %d %s" % (len(roz), roz[:4]),
        "pola = parametry.json")
    return J, m


def k05_z_json(J, m, etyk):
    so = J["sockets"]
    cechy = []
    for s in so:
        if s["type"] == "round":
            cechy.append(W.Cecha("round", "id%d" % s["id"], (s["x"], s["y"]), (s["x"], s["y"]), s["d_top"] / 2.0, d=s["d_top"]))
        else:
            h = (s["l"] - s["w"]) / 2.0
            cechy.append(W.Cecha("trough", "id%d" % s["id"], (s["x"] - h, s["y"]), (s["x"] + h, s["y"]), s["w"] / 2.0, l=s["l"], w=s["w"]))
    # (b)
    grupy = {}
    for s in so:
        grupy.setdefault(s["y"], []).append(s["x"])
    nies = [y for y, xs in grupy.items() if any(min(abs(x + x2) for x2 in xs) > 0.01 for x in xs)]
    rec("K-05b " + etyk, not nies, "grup y: %d, niesymetrycznych %d %s" % (len(grupy), len(nies), nies), "kazda grupa y symetryczna wzgledem x = 0")
    # (c)
    mr = max((c.max_promien(), c.nazwa) for c in cechy)
    mx = max((c.max_abs_x(), c.nazwa) for c in cechy)
    my = max((c.max_abs_y(), c.nazwa) for c in cechy)
    rec("K-05c " + etyk, mr[0] <= m.zone_r and mx[0] <= m.zone / 2.0 + 1e-9 and my[0] <= m.zone / 2.0 + 1e-9,
        "max promien obrysu %.4f (%s); max |x|+r %.4f (%s); max |y|+r %.4f (%s)" % (mr[0], mr[1], mx[0], mx[1], my[0], my[1]),
        "<= %g; <= %g" % (m.zone_r, m.zone / 2.0))
    # (d)
    hb = m.bok / 2.0
    nz = hb - m.rog_strefa
    dn = min(W.odl_prostokat_cecha((min(sx * nz, sx * hb), max(sx * nz, sx * hb), min(sy * nz, sy * hb), max(sy * nz, sy * hb)), c)
             for c in cechy for sx in (-1, 1) for sy in (-1, 1))
    rec("K-05d " + etyk, dn > 0, "min odleglosc obrysu od kwadratu naroznego (|x| > %g i |y| > %g): %.3f" % (nz, nz, dn), "> 0")
    # (e)
    pary = sorted((cechy[i].odstep(cechy[j]), cechy[i].nazwa, cechy[j].nazwa) for i in range(len(cechy)) for j in range(i + 1, len(cechy)))
    rec("K-05e " + etyk, pary[0][0] >= m.wall_min - 1e-9, "min scianka %.4f (%s - %s); par < 3,005: %d; par ogolem %d" % (
        pary[0][0], pary[0][1], pary[0][2], sum(1 for p in pary if p[0] < 3.005), len(pary)), ">= %g" % m.wall_min)
    # (f)
    zf = [s["id"] for s in so if s["type"] == "round" and abs(s["d_bottom"] - (s["d_top"] - 2 * s["depth"] * math.tan(math.radians(15)))) > 0.01]
    rec("K-05f " + etyk, not zf, "d_bottom niezgodne: %d %s; wartosci %s" % (len(zf), zf, sorted(set((s["d_top"], s["d_bottom"]) for s in so if s["type"] == "round"))),
        "d_top - 2*4*tan(15) +-0,01")
    # (g)
    ids = [s["id"] for s in so]
    kol = sorted(so, key=lambda s: (s["y"], -s["x"]))
    rec("K-05g " + etyk, ids == list(range(1, len(so) + 1)) and [s["id"] for s in kol] == ids,
        "id %d...%d ciagle: %s; kolejnosc po (y rosnaco, x malejaco): %s" % (ids[0], ids[-1], ids == list(range(1, len(so) + 1)), [s["id"] for s in kol] == ids),
        "id 1...N, rzedami od przodu, w rzedzie malejace x, rzad mieszany po y wpisu")


def wypisz_liczby(typ, ksztalt):
    m = W.Model(PAR, typ, ksztalt)
    L = W.liczby_pelne(m)
    print("--- LICZBY %s %s (z parametry.json) ---" % (typ, ksztalt))
    print("  gniazda: %s; round %d, trough %d" % (L["liczby_gniazd"], L["round"], L["trough"]))
    print("  max promien obrysu: %.4f (%s); wpisy: %s" % (L["max_promien"][0], L["max_promien"][1],
                                                           "; ".join("%s -> %.2f" % (k, v[0]) for k, v in L["promienie_wpisow"].items())))
    print("  max |x|+r %.3f, max |y|+r %.3f; blok y %.2f...%.2f (%.2f)" % (L["max_abs_x"][0], L["max_abs_y"][0], L["blok_y"][0], L["blok_y"][1],
                                                                         L["blok_y"][1] - L["blok_y"][0]))
    print("  min scianka: %.4f (%s | %s); pary wpisow: %s" % (L["min_scianka"][0], L["min_scianka"][1], L["min_scianka"][2],
                                                             "; ".join("%s: %.3f" % (k, v[0]) for k, v in sorted(L["min_scianka_par_wpisow"].items()))))
    print("  kwadrat narozny: min odleglosc obrysu %.3f" % L["min_odl_do_kwadratu_naroznego"][0])
    for k in "ABC":
        z = L["znaczniki"][k]
        print("  znacznik %s %s: promien srodka %.3f, obrysu %.3f, scianka do gniazda %.3f (%s)" % (
            k, z["xy"], z["promien_srodka"], z["promien_obrysu"], z["scianka_do_gniazda"][0], z["scianka_do_gniazda"][1]))
    t = L["trojkat"]
    print("  trojkat znacznikow: AB %.2f, BC %.2f, AC %.2f; roznice bokow %.2f / %.2f / %.2f" % (
        t["AB"], t["BC"], t["AC"], abs(t["AB"] - t["BC"]), abs(t["BC"] - t["AC"]), abs(t["AB"] - t["AC"])))
    for k in "ABCD":
        d = L["dolki"][k]
        print("  dolek %s %s: promien srodka %.3f, do gniazda %.3f (%s), do znacznika %.3f (%s)%s" % (
            k, d["xy"], d["promien_srodka"], d["do_gniazda"][0], d["do_gniazda"][1], d["do_znacznika"][0], d["do_znacznika"][1],
            (", do krawedzi (okrag) %.3f, do sciecia %.3f" % (d["do_krawedzi_okrag"], d["do_sciecia"])) if ksztalt == "okragla"
            else (", do krawedzi %.3f" % d["do_krawedzi"])))
    if "cyfra" in L:
        c = L["cyfra"]
        print("  cyfra %s (prostokat 3,6 x 5): promien naroznika max %.3f, do gniazda %.3f (%s), do znacznika %.3f, do dolka %.3f%s" % (
            c["xy"], c["promien_naroznika_max"], c["do_gniazda"][0], c["do_gniazda"][1], c["do_znacznika"][0], c["do_dolka"][0],
            (", do sciecia %.3f" % c["do_sciecia"]) if "do_sciecia" in c else ""))
    if ksztalt == "kwadrat":
        print("  wyciecie D - gniazdo: %.3f (%s)" % (L["wyciecie_gniazdo"][0], L["wyciecie_gniazdo"][1]))
    else:
        print("  okragla: gniazdo - krawedz (sciana pionowa) %.3f (%s), do poczatku fazy %.3f; stozek - krawedz %.3f (%s); dolek - krawedz %.3f (%s);"
              " sciecie: odleglosc plaszczyzny %.4f, glebokosc %.4f, do gniazd %.3f (%s), do stozkow %.3f, do dolkow %.3f" % (
                  L["gniazdo_krawedz_okrag_min"][0], L["gniazdo_krawedz_okrag_min"][1], L["gniazdo_poczatek_fazy_min"],
                  L["znacznik_krawedz_min"][0], L["znacznik_krawedz_min"][1], L["dolek_krawedz_min"][0], L["dolek_krawedz_min"][1],
                  L["flat_dist"], L["flat_depth"], L["gniazdo_sciecie_min"][0], L["gniazdo_sciecie_min"][1],
                  L["znacznik_sciecie_min"][0], L["dolek_sciecie_min"][0]))
    return m, L


def main():
    os.makedirs(WYN, exist_ok=True)
    wyn = {"liczby": {}}
    Js = {}
    for typ in ("wieczorna", "poranna"):
        for ksztalt in ("kwadrat", "okragla"):
            etyk = ("okragla_" if ksztalt == "okragla" else "") + typ
            J, m = sprawdz_json(typ, ksztalt)
            Js[(typ, ksztalt)] = J
            k05_z_json(J, m, etyk)
            m, L = wypisz_liczby(typ, ksztalt)
            wyn["liczby"][etyk] = L
            zn = L["znaczniki"]
            t = L["trojkat"]
            ok = all(zn[k]["promien_srodka"] <= m.zone_r - m.marker_d / 2.0 and zn[k]["scianka_do_gniazda"][0] >= m.wall_min for k in "ABC")
            ok = ok and min(abs(t["AB"] - t["BC"]), abs(t["BC"] - t["AC"]), abs(t["AB"] - t["AC"])) >= 5.0
            ok = ok and L["dolek_gniazdo_min"][0] >= m.wall_min and L["dolek_znacznik_min"][0] >= 1.5
            rec("K-16 rachunek " + etyk, ok, "stozki: promien srodka max %.3f, scianka do gniazd min %.3f, roznica bokow trojkata min %.2f; dolek-gniazdo %.3f,"
                " dolek-stozek %.3f" % (max(zn[k]["promien_srodka"] for k in "ABC"), min(zn[k]["scianka_do_gniazda"][0] for k in "ABC"),
                                        min(abs(t["AB"] - t["BC"]), abs(t["BC"] - t["AC"]), abs(t["AB"] - t["AC"])),
                                        L["dolek_gniazdo_min"][0], L["dolek_znacznik_min"][0]),
                "<= %g; >= %g; >= 5; >= %g; >= 1,5" % (m.zone_r - m.marker_d / 2.0, m.wall_min, m.wall_min))
            if ksztalt == "okragla":
                c = L["cyfra"]
                ok = L["dolek_promien_min_max"][1] <= m.zone_r - m.wall_min and L["dolek_krawedz_min"][0] >= 1.5
                ok = ok and L["gniazdo_krawedz_min"][0] >= 1.5 and L["znacznik_krawedz_min"][0] >= 1.5 and L["sciecie_obrysy_min"] >= m.wall_min
                ok = ok and L["flat_depth"] >= m.flat_depth_min and c["promien_naroznika_max"] <= m.zone_r and c["do_gniazda"][0] >= m.wall_min
                rec("K-16/K-61f/K-62 rachunek " + etyk, ok, "dolek: promien max %.3f, do krawedzi %.3f; gniazdo-krawedz %.3f; stozek-krawedz %.3f; sciecie-obrysy %.3f;"
                    " glebokosc sciecia %.4f; cyfra: naroznik %.3f, do gniazda %.3f" % (
                        L["dolek_promien_min_max"][1], L["dolek_krawedz_min"][0], L["gniazdo_krawedz_min"][0], L["znacznik_krawedz_min"][0],
                        L["sciecie_obrysy_min"], L["flat_depth"], c["promien_naroznika_max"], c["do_gniazda"][0]),
                    "<= %g; >= 1,5; >= 1,5; >= 1,5; >= %g; >= %g; <= %g; >= %g" % (m.zone_r - m.wall_min, m.wall_min, m.flat_depth_min, m.zone_r, m.wall_min))
    for typ in ("wieczorna", "poranna"):
        rec("K-05h " + typ, Js[(typ, "okragla")]["sockets"] == Js[(typ, "kwadrat")]["sockets"],
            "sockets okraglej == sockets kwadratu: %s (%d pozycji)" % (Js[(typ, "okragla")]["sockets"] == Js[(typ, "kwadrat")]["sockets"],
                                                                      len(Js[(typ, "kwadrat")]["sockets"])), "identyczne (wszystkie pola)")
        rec("markers okragla = kwadrat " + typ, Js[(typ, "okragla")]["markers"] == Js[(typ, "kwadrat")]["markers"], "identyczne: %s" % (
            Js[(typ, "okragla")]["markers"] == Js[(typ, "kwadrat")]["markers"]), "identyczne")
    # --- decyzje G0 ---
    mw = W.Model(PAR, "wieczorna", "kwadrat")
    mp = W.Model(PAR, "poranna", "kwadrat")

    def licz(m):
        d = {}
        for g in m.gniazda:
            k = ("fi%g" % g.d) if g.rodzaj == "round" else ("rynienka %gx%g" % (g.l, g.w))
            d[k] = d.get(k, 0) + 1
        return d
    lw = licz(mw)
    lp = licz(mp)
    rec("G0/D1 wieczorna W-b", lw == {"rynienka 60x15": 1, "fi12": 6, "fi15": 12}, str(lw), "6 x fi 12 + 12 x fi 15 + 1 rynienka 60 x 15")
    rec("G0/D2 poranna P-e", lp == {"rynienka 50x13": 1, "fi12.5": 20, "fi15": 3}, str(lp), "20 x fi 12,5 + 3 x fi 15 + 1 rynienka 50 x 13, bez fi 7,5 i fi 10")
    for m, n in ((mw, "wieczorna"), (mp, "poranna")):
        tr = [g for g in m.gniazda if g.rodzaj == "trough"]
        ok = len(tr) == 1 and tr[0].id == 1 and all(tr[0].y < g.y for g in m.gniazda if g.rodzaj == "round") and tr[0].x == 0
        rec("G0/D3 rynienka " + n, ok and tr[0].n_otw == 4, "rynienek %d, id %s, y %s (przednia: y mniejsze od wszystkich gniazd), otworow %s, rozstaw %s" % (
            len(tr), tr[0].id, tr[0].y, tr[0].n_otw, tr[0].pitch), "1 rynienka przednia, 4 otwory, rozstaw jak dotad")
    mieszane = sorted(set(r["y"] for r in W.P(PAR, "mo_rows")))
    rec("G0/D2 rzedy mieszane", len(W.P(PAR, "mo_rows")) == 8 and len(mieszane) == 8, "wpisow mo_rows %d, roznych y %d: %s" % (
        len(W.P(PAR, "mo_rows")), len(mieszane), mieszane), "rzad mieszany = osobne wpisy o roznym y (8 wpisow)")
    # klucze zmienione wzgledem parametrow sprzed R59 (wartosc)
    zm = []
    for sec in PAR:
        if sec == "_meta":
            continue
        for k in sorted(set(PAR[sec]) | set(PAR_ST.get(sec, {}))):
            a = PAR[sec].get(k, {}).get("value", "BRAK") if k in PAR[sec] else "BRAK"
            b = PAR_ST.get(sec, {}).get(k, {}).get("value", "BRAK") if k in PAR_ST.get(sec, {}) else "BRAK"
            if a != b:
                zm.append("%s.%s" % (sec, k))
    oczek = ["plytka.code_dimples_round", "plytka.ev_marker_pos", "plytka.ev_rows", "plytka.mo_marker_pos", "plytka.mo_rows",
             "plytka.number_pos_round"]
    rec("G0 zakres zmian parametry.json", sorted(zm) == oczek, "klucze o zmienionej wartosci: %s; sekcji %d, kluczy %d" % (
        zm, len(PAR) - 1, sum(len(PAR[s]) for s in PAR if s != "_meta")), "tylko 6 kluczy ukladu; D3 (otwory), D5 (numery), D6 (quantities) bez zmian")
    rec("G0 dolki/cyfra okraglej wieczornej bez zmian", W.P(PAR, "code_dimples_round")["wieczorna"] == W.P(PAR_ST, "code_dimples_round")["wieczorna"]
        and W.P(PAR, "number_pos_round")["wieczorna"] == W.P(PAR_ST, "number_pos_round")["wieczorna"], "bez zmian", "bez zmian")
    ms = dict((t, W.Model(PAR_ST, t, "kwadrat")) for t in ("wieczorna", "poranna"))
    print("--- STARY UKLAD (archiwum parametrow): wieczorna %s; poranna %s" % (licz(ms["wieczorna"]), licz(ms["poranna"])))
    wyn["wyniki"] = RES
    nie = sum(1 for r in RES if r["wynik"] == "NIE")
    with open(os.path.join(WYN, "liczby_R59.json"), "w", encoding="utf-8") as f:
        json.dump(wyn, f, indent=1, default=str)
    print("LICZBY KONIEC: sprawdzen %d, NIE %d" % (len(RES), nie))
    return 0 if nie == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
