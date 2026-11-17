# -*- coding: utf-8 -*-
"""R59 testy koncowe koordynatora T6, T8, T9, T10 - program stanowiska na czystej kopii galezi.

Uzycie (katalog biezacy = Ramki/stanowisko czystej kopii, PYTHONPATH jak w run.cmd):
    python t6_t10_program.py <folder projektow> <katalog roboczy> <t8_mapa_seed7001.json>
Wszystkie skany powstaja poleceniami programu (stanowisko.synth, stanowisko.porownaj) w osobnych procesach.
W wynikach tylko skroty projektow; mapa skrot -> nazwa pliku jest kasowana na koncu.
"""
import json
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import trimesh

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "narzedzia"))
from stanowisko import katalog as K  # noqa: E402
from stanowisko import synth as S  # noqa: E402
from stanowisko import uklad as U  # noqa: E402
import atrapy_koron  # noqa: E402

PROJ = Path(sys.argv[1])
D = Path(sys.argv[2])
BASE = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
MAPA = D / "_mapa_tmp.json"
NOWE = [("wieczorna", 1.22), ("poranna", 1.0), ("okragla_wieczorna", 1.22), ("okragla_poranna", 1.0)]
WYNIKI = []
BLEDY = []


def uruchom(modul, *arg):
    r = subprocess.run([sys.executable, "-m", modul, *[str(a) for a in arg]], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def synth(plytka, seed, wsp, kat, projekty=PROJ, dodatkowe=()):
    kat.mkdir(parents=True, exist_ok=True)
    kod, wyj = uruchom("stanowisko.synth", "--projekty", projekty, "--plytka", plytka, "--ile", 1, "--seed", seed,
                       "--wspolczynnik", wsp, "--poza-uklad", "--pole", 100, "--wyjscie", kat, "--mapa", MAPA, *dodatkowe)
    skany = sorted(kat.glob("skan_*_s%04d.stl" % seed))
    if kod != 0 or len(skany) != 1:
        raise RuntimeError("synth %s seed %s: kod %s, skanow %d: %s" % (plytka, seed, kod, len(skany), wyj[-400:]))
    return skany[0]


def numer_z_nazwy(skan):
    return int(skan.stem.split("_n")[-1].split("_s")[0])


def porownaj(skan, plytka, wsp, kat, prawda=True):
    kat.mkdir(parents=True, exist_ok=True)
    arg = ["--skan", skan, "--projekty", PROJ, "--plytka", plytka, "--wspolczynnik", wsp, "--wyjscie", kat, "--bez-png"]
    if not plytka.startswith("okragla"):
        arg += ["--numer", numer_z_nazwy(skan)]
    if prawda:
        arg += ["--prawda", skan.with_suffix(".json")]
    kod, wyj = uruchom("stanowisko.porownaj", *arg)
    p = kat / (skan.stem + "_wynik.json")
    if kod != 0 or not p.exists():
        raise RuntimeError("porownaj %s jako %s: kod %s: %s" % (skan.stem, plytka, kod, wyj[-400:]))
    return json.loads(p.read_text(encoding="utf-8")), wyj


def zapisz(test, nazwa, ok, opis):
    WYNIKI.append((test, nazwa, ok, opis))
    if not ok:
        BLEDY.append((test, nazwa, opis))
    print("%-4s %-46s %s  %s" % (test, nazwa, "OK  " if ok else "FAIL", opis), flush=True)


def rownolegle(zadania, ile=8):
    with ThreadPoolExecutor(max_workers=ile) as ex:
        return list(ex.map(lambda f: f(), zadania))


def t6():
    def jedno(pl, wsp, seed):
        def f():
            kat = D / "t6" / ("%s_%d" % (pl, seed))
            skan = synth(pl, seed, wsp, kat)
            w, _ = porownaj(skan, pl, wsp, kat / "wynik")
            m = w["metryki"]
            wyr = m["wyrownanie"]["max_przesuniecie_mm"]
            ok = (w.get("uklad_zgodny") is True and wyr < 0.05 and m["fragment_w_swoim_gniezdzie"] == m["fragmentow"]
                  and m["puste_ok"] and m["top1"] == m["prac_prawda"] and not m["podwojne"] and m["poza_gniazdem"] == 0)
            if pl.startswith("okragla"):
                ok = ok and m["numer_z_dolkow_ok"] is True and m["numer_odczytany"] == m["numer_prawda"]
            opis = ("wyrownanie %.4f mm; prac %d, fragment w swoim gniezdzie %d/%d, top-1 %d/%d, puste %s, numer %s vs %s (%s), "
                    "uklad_zgodny %s" % (wyr, m["prac_prawda"], m["fragment_w_swoim_gniezdzie"], m["fragmentow"], m["top1"],
                                         m["prac_prawda"], m["puste_ok"], m["numer_odczytany"], m["numer_prawda"],
                                         m["numer_zrodlo"], w.get("uklad_zgodny")))
            return skan, pl, wsp, ok, opis
        return f
    wyn = rownolegle([jedno(pl, wsp, seed) for pl, wsp in NOWE for seed in (9001, 9002, 9003)])
    for skan, pl, wsp, ok, opis in wyn:
        zapisz("T6", skan.stem, ok, opis)
    return [(skan, pl, wsp) for skan, pl, wsp, _, _ in wyn]


def mapa_wyniku(w):
    out = {}
    for g in w["gniazda"]:
        k = g["kandydaci"][0] if g.get("kandydaci") else {}
        out[str(g["gniazdo"])] = {"projekt": k.get("id") or k.get("projekt"), "match": g.get("status"),
                                  "status_gniazda": g.get("status_gniazda")}
    return out


def t8a():
    def jedno(pl, wsp):
        def f():
            kat = D / "t8a" / pl
            skan = synth(pl + "_r54", 7001, wsp, kat, dodatkowe=("--drgniecie", 0.1))
            w, _ = porownaj(skan, pl + "_r54", wsp, kat / "wynik")
            klucz = skan.stem.replace("_r54", "")
            wzor = BASE.get(klucz)
            if wzor is None:
                return skan, pl, wsp, False, "brak klucza %s w punkcie odniesienia (inny numer plytki?)" % klucz
            m = mapa_wyniku(w)
            rozne = [g for g in sorted(set(m) | set(wzor["gniazda"]), key=int) if m.get(g) != wzor["gniazda"].get(g)]
            ok = (not rozne and sorted(w["gniazda_puste"]) == sorted(wzor["gniazda_puste"])
                  and w["gniazda_podwojne"] == wzor["gniazda_podwojne"] and w["statusy_gniazd"] == wzor["statusy_gniazd"]
                  and w.get("uklad_zgodny") is True)
            opis = "gniazd z praca %d (wzor %d), rozne gniazda %s, puste zgodne %s, statusy %s" % (
                len(m), len(wzor["gniazda"]), rozne, sorted(w["gniazda_puste"]) == sorted(wzor["gniazda_puste"]),
                w["statusy_gniazd"] == wzor["statusy_gniazd"])
            return skan, pl, wsp, ok, opis
        return f
    wyn = rownolegle([jedno(pl, wsp) for pl, wsp in NOWE], 4)
    for skan, pl, wsp, ok, opis in wyn:
        zapisz("T8a", skan.stem, ok, opis)
    return [(skan, pl + "_r54", wsp) for skan, pl, wsp, _, _ in wyn]


def drugi_uklad(pl):
    return pl[:-4] if pl.endswith("_r54") else pl + "_r54"


def t8b(skany_nowe, skany_r54):
    def puste(pl, wsp):
        def f():
            return synth(pl, 9050, wsp, D / "t8b" / ("pusta_" + pl), dodatkowe=("--prace", 0)), pl, wsp
        return f
    uklady = NOWE + [(pl + "_r54", wsp) for pl, wsp in NOWE]
    skany_puste = rownolegle([puste(pl, wsp) for pl, wsp in uklady])

    def niezgodny(skan, pl, wsp, rodzaj):
        def f():
            inny = drugi_uklad(pl)
            w, wyj = porownaj(skan, inny, wsp, D / "t8b" / "wynik_niezgodne" / inny, prawda=False)
            zielone = (w.get("statusy_gniazd") or {}).get("zielony", 0)
            ok = w.get("uklad_zgodny") is False and zielone == 0 and not w.get("gniazda") and bool(w.get("uklad_komunikat"))
            return ("T8b", "%s jako %s (%s)" % (skan.stem, inny, rodzaj), ok,
                    "uklad_zgodny %s, zielone %s, gniazd w wyniku %d, pasujace %s"
                    % (w.get("uklad_zgodny"), zielone, len(w.get("gniazda") or []), w.get("uklady_pasujace")))
        return f

    def zgodny_pusty(skan, pl, wsp):
        def f():
            w, _ = porownaj(skan, pl, wsp, D / "t8b" / "wynik_zgodne" / pl, prawda=True)
            ok = w.get("uklad_zgodny") is True and not w.get("gniazda")
            return ("T8b", "%s jako %s (pusta, zgodna)" % (skan.stem, pl), ok,
                    "uklad_zgodny %s, fragmentow %d" % (w.get("uklad_zgodny"), len(w.get("gniazda") or [])))
        return f
    zad = [niezgodny(s, pl, wsp, "z pracami") for s, pl, wsp in skany_nowe + skany_r54]
    zad += [niezgodny(s, pl, wsp, "pusta") for s, pl, wsp in skany_puste]
    zad += [zgodny_pusty(s, pl, wsp) for s, pl, wsp in skany_puste]
    for test, nazwa, ok, opis in rownolegle(zad):
        zapisz(test, nazwa, ok, opis)


def t9():
    for pl in ("poranna", "okragla_poranna"):
        uk = U.wczytaj(pl)
        fi15 = [g for g in uk.gniazda_okragle() if g.d_top == 15]
        zapisz("T9", pl + ": gniazdo d_top == 15", len(fi15) > 0, "gniazd fi 15: %d" % len(fi15))
    uk = U.wczytaj("poranna")
    klasy = {}
    do_fi15 = []
    for plik in S.pliki_projektow(PROJ):
        m = S.wczytaj_projekt(plik)
        if m is None:
            continue
        g = K.gniazdo_dla(m, uk, 1.0, nazwa=plik.name)
        klucz = ("fi%g" % g["d_top"]) if g and g.get("typ") == "round" else (g.get("typ") if g else None) or "brak"
        klasy[klucz] = klasy.get(klucz, 0) + 1
        if g and g.get("typ") == "round" and g["d_top"] == 15:
            do_fi15.append(plik)
    zapisz("T9", "katalog.gniazdo_dla, 17 projektow, skala 1,0", len(do_fi15) >= 1,
           "najmniejsze pasujace gniazdo: %s; do fi 15: %s" % (dict(sorted(klasy.items())), [S.skrot_pliku(p) for p in do_fi15]))
    # Poprawka po pierwszym przebiegu (15.11): (1) "transformacja" z prawdy jest w ukladzie PLYTKI (poza skanu jest
    # osobno w "poza_skanu" i dotyczy calego skanu), wiec przenikanie liczy sie bez odwracania pozy; (2) projekt
    # graniczny moze przy innym losowaniu zmiescic sie w fi 12,5 - dlatego osadzenie w fi 15 sprawdzane jest wprost
    # funkcja programu, a w skanie z polecenia wymagane sa: gniazdo okragle, brak przenikania, rozpoznanie.
    gniazda15 = [g for g in uk.gniazda_okragle() if g.d_top == 15]
    for plik in do_fi15:
        skrot = S.skrot_pliku(plik)
        m = S.wczytaj_projekt(plik)
        m2 = m.copy()
        m2.apply_transform(S.orientacja_brzegiem_do_gory(m, "auto", plik.name))
        proby = 0
        udane = 0
        najw = 0.0
        for g in gniazda15:
            for seed in range(5):
                proby += 1
                T = S.osadz_w_gniezdzie(m2, g, np.random.default_rng(900 + seed))
                if T is not None:
                    udane += 1
                    najw = max(najw, float(S.przenikanie(trimesh.transform_points(m2.vertices, T), g)))
        zapisz("T9", "projekt %s: osadzenie wprost w fi 15" % skrot, udane == proby and najw <= 1e-6,
               "osadzen %d/%d (3 gniazda x 5 losowan), najwieksze przenikanie %.2e mm" % (udane, proby, najw))
        kat = D / "t9" / skrot
        zrodlo = kat / "projekty" / "z1"
        zrodlo.mkdir(parents=True, exist_ok=True)
        shutil.copy2(plik, zrodlo / plik.name)
        try:
            w15 = 0
            for seed in (9101, 9102, 9103, 9104, 9105):
                skan = synth("poranna", seed, 1.0, kat / ("skan_%d" % seed), projekty=kat / "projekty", dodatkowe=("--ubytki", "0-0"))
                prawda = json.loads(skan.with_suffix(".json").read_text(encoding="utf-8"))
                prace = prawda["prace"]
                ok = len(prace) == 1 and prace[0]["projekt"] == skrot
                opis = "prac %d" % len(prace)
                if ok:
                    g = uk.gniazdo(prace[0]["gniazdo"])
                    T = np.array(prace[0]["transformacja"], dtype=float)
                    V = trimesh.transform_points(m.vertices * prace[0]["wspolczynnik"], T)
                    prz = float(S.przenikanie(V, g))
                    w, _ = porownaj(skan, "poranna", 1.0, kat / ("wynik_%d" % seed))
                    gn = [x for x in w["gniazda"] if x["gniazdo"] == g.id]
                    rozp = bool(gn) and bool(gn[0]["kandydaci"]) and gn[0]["kandydaci"][0]["id"] == skrot and gn[0]["status"] == "zielony"
                    w15 += 1 if (g.okragle and g.d_top == 15) else 0
                    ok = g.okragle and prz <= 1e-6 and rozp
                    opis = "gniazdo %d fi%g, przenikanie %.2e mm, rozpoznana (top-1 i zielony match) %s, wyrownanie %.4f mm" % (
                        g.id, g.d_top, prz, rozp, w["metryki"]["wyrownanie"]["max_przesuniecie_mm"])
                zapisz("T9", "projekt %s w skanie (poranna, seed %d)" % (skrot, seed), ok, opis)
            print("     projekt %s: w fi 15 w %d z 5 skanow (reszta w fi 12,5 - projekt graniczny)" % (skrot, w15), flush=True)
        finally:
            shutil.rmtree(kat / "projekty", ignore_errors=True)


def t10():
    kat_m = D / "t10" / "mosty" / "z1"
    kat_m.mkdir(parents=True, exist_ok=True)
    skroty = []
    for i, seed in enumerate((101, 102)):
        p = kat_m / ("atrapa_mostu_%d.stl" % i)
        m = atrapy_koron.most(np.random.default_rng(seed))
        m.export(p)
        skroty.append(S.skrot_pliku(p))
        zapisz("T10", "atrapa mostu %d (seed %d)" % (i, seed), S.szerokosc_pracy(m) > S.PROG_MOSTU_MM,
               "szerokosc %.1f mm > prog %.0f" % (S.szerokosc_pracy(m), S.PROG_MOSTU_MM))

    def jedno(pl):
        def f():
            uk = U.wczytaj(pl)
            ryn = uk.rynienki()
            kat = D / "t10" / pl
            skan = synth(pl, 9201, 1.0, kat, projekty=D / "t10" / "mosty", dodatkowe=("--ubytki", "0-0"))
            prawda = json.loads(skan.with_suffix(".json").read_text(encoding="utf-8"))
            w, _ = porownaj(skan, pl, 1.0, kat / "wynik")
            osadzone = [p["gniazdo"] for p in prawda["prace"]]
            fr = [x for x in w["gniazda"] if x["gniazdo"] == ryn[0].id]
            ok = (len(ryn) == 1 and osadzone == [ryn[0].id] and len(prawda["pominiete"]) == 1
                  and set(prawda["pominiete"]) | {prawda["prace"][0]["projekt"]} == set(skroty)
                  and w["gniazda_podwojne"] == [] and len(w["gniazda"]) == 1 and len(fr) == 1 and w.get("uklad_zgodny") is True)
            opis = "rynienek %d (id %d); osadzone w gniazdach %s; pominiete %d; podwojne %s; fragmentow w wyniku %d" % (
                len(ryn), ryn[0].id, osadzone, len(prawda["pominiete"]), w["gniazda_podwojne"], len(w["gniazda"]))
            return pl, ok, opis
        return f
    for pl, ok, opis in rownolegle([jedno(pl) for pl, _ in NOWE], 4):
        zapisz("T10", "2 mosty na plytce %s" % pl, ok, opis)


def main():
    D.mkdir(parents=True, exist_ok=True)
    tylko = sys.argv[4].split(",") if len(sys.argv) > 4 else None   # np. "T9" - powtorka jednego testu
    try:
        if tylko is None or "T6" in tylko or "T8" in tylko:
            nowe = t6()
            r54 = t8a()
            t8b(nowe, r54)
        if tylko is None or "T9" in tylko:
            t9()
        if tylko is None or "T10" in tylko:
            t10()
    finally:
        usuniete = 0
        for p in list(D.rglob("mapa_projektow*.json")) + [MAPA]:
            if p.exists():
                p.unlink()
                usuniete += 1
        print("mapy skrot -> nazwa usuniete: %d" % usuniete)
    for t in ("T6", "T8a", "T8b", "T9", "T10"):
        w = [x for x in WYNIKI if x[0] == t]
        print("RAZEM %-4s %d/%d OK" % (t, sum(1 for x in w if x[2]), len(w)))
    print("FAIL: %d" % len(BLEDY))
    sys.exit(1 if BLEDY else 0)


main()
