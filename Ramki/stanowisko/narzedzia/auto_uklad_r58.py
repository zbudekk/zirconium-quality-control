"""Pomiar rozpoznania ukladu plytki po dodaniu plytek okraglych ramkowych n1-n6 (R58) - paczka E3-O1 (21.11.2026).

Uzycie (z katalogu stanowisko/; jeden proces, bez puli):
    python narzedzia/auto_uklad_r58.py --wyjscie <katalog> --odniesienie <folder> [<folder> ...]
           [--kryteria 2,3,4,6,z] [--ustawienia <plik>] [--pola 100,90,80] [--ziarna-k2 4] [--ziarna-k4 2]
           [--pomiary-k6 10] [--limit N] [--wznow] [--uwaga "co jeszcze liczylo"]

Mierzy kryteria paczki E3-O1 (``Ramki/etap3/plan_plytki_okragle_n1-n6_2026-11-21.md`` sekcja 4) funkcja
``plate.rozpoznaj_uklad`` programu, bez zmiany kodu rozpoznania. Kandydaci "10" = wszystkie uklady z ``[plytki]``
ustawien, kandydaci "8" = te same bez ukladow ``okragla_ramkowa_*`` (stan sprzed paczki).

  2  skany syntetyczne plytek ramkowych: 6 numerow x ``--ziarna-k2`` ziaren x (bez numeru / z numerem zgodnym), pole
     fi 100, 10 kandydatow, z cieciem na gniazda: uklad = prawda, ``pewny``, gniazda prac = prawda;
  3  (bramka) skany odniesienia z folderow ``--odniesienie`` (``skan_*.stl`` + prawda ``.json``): parami 8 i 10
     kandydatow, bez numeru i z numerem z prawdy: ten sam uklad i nie gorsza pewnosc; lista przejsc ``powod``;
  4  (bramka) dla kazdego pola z ``--pola``: kazdy uklad, kazdy jego numer, ``--ziarna-k4`` ziaren, bez numeru i z numerem
     zgodnym, 10 kandydatow: ile "pewny ze zlym ukladem" (ma byc 0), ile niepewnych i z jakim ``powod``; dodatkowo
     (ziarno pierwsze) numer podany NIEZGODNY z plytka: inny numer tego samego ukladu, numer drugiej pory dnia, numer
     drugiego ksztaltu - co program zwraca (dla ukladow sprzed paczki takze przy 8 kandydatach);
  6  czas rozpoznania plytek R59 z folderow odniesienia: ``--pomiary-k6`` skanow, 8 i 10 kandydatow na przemian,
     mediana czasu sciennego; wzrost mediany nie wiekszy niz 1,0 s;
  z  plytka ramkowa z dolkami kodu zaslonietymi przez przedmiot lezacy na plytce (walec fi 4 x 3 mm na dolku, wierzch
     plytki pod nim usuniety): wszystkie dolki albo jeden dolek bitu ustawionego; pomiar dodatkowy, bez progu.

Kazdy przebieg jest dopisywany do ``<wyjscie>/przebiegi.jsonl`` zaraz po zakonczeniu (PC bywa restartowany);
``--wznow`` pomija przebiegi juz zapisane. Na koniec: ``<wyjscie>/auto_uklad_r58.json`` (podsumowanie + przebiegi)
i ``<wyjscie>/auto_uklad_r58.txt`` (tabela, ASCII). W wyniku sa tylko nazwy skanow syntetycznych i skroty ``sha16``
projektow z plikow prawdy - bez nazw plikow projektow. Kod wyjscia: 0 = wszystkie zmierzone kryteria spelnione,
1 = ktores niespelnione, 2 = blad wywolania.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import statistics
import sys
import time
import warnings
from collections import Counter
from pathlib import Path

KORZEN = Path(__file__).resolve().parent.parent
for _p in (KORZEN, KORZEN / "narzedzia"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import stanowisko  # noqa: E402, F401, I001 - przed trimesh (wylacza zapytania WMI modulu platform)

import numpy as np  # noqa: E402
import trimesh  # noqa: E402

import atrapy_koron  # noqa: E402
from stanowisko import plate, porownaj as PO, synth, uklad as U, ustawienia as UST  # noqa: E402

RAMKOWE = ("okragla_ramkowa_wieczorna", "okragla_ramkowa_poranna")
KRYTERIA = ("2", "3", "4", "6", "z")
PRZYROST_CZASU_MAX_S = 1.0  # kryterium 6
SKANOW_K2 = 48  # kryterium 2: 6 numerow x 4 ziarna x 2 tryby
POLA_FRAGMENTU_RODZINY = ("uklad", "odrzucony", "numer_z_dolkow", "numer_z_dolkow_wazny", "dolki_widoczne", "numer_podany_pasuje",
                          "ksztalt_niewyjasnione_mm2", "ksztalt_strefa_mm2")
PARA_PORY = {1: 4, 2: 5, 3: 6, 4: 1, 5: 2, 6: 3, 8: 9, 9: 8}  # ten sam numer kolejny plytki drugiej pory dnia
PROMIEN_ZASLONY = 2.0  # mm: walec na dolku kodu (dolek fi 2)
WYSOKOSC_ZASLONY = 3.0


# ----------------------------------------------------------------------------
# uklady, atrapy, skany
# ----------------------------------------------------------------------------
def uklady_kandydaci(ust: dict) -> tuple[list[U.UkladPlytki], list[U.UkladPlytki]]:
    """(10 kandydatow = wszystkie uklady z ``[plytki]``; 8 kandydatow = bez ukladow ramkowych), w kolejnosci z ustawien."""
    wszystkie = list(PO.uklady_z_ustawien(ust).values())
    return wszystkie, [u for u in wszystkie if u.nazwa not in RAMKOWE]


def atrapy(katalog: Path) -> list[Path]:
    """Trzy atrapy koron (siekacz, przedtrzonowy, trzonowy) - te same co w testach programu; pliki w ``katalog``."""
    katalog.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(3)
    pliki = []
    for i, typ in enumerate(("siekacz", "przedtrzonowy", "trzonowy")):
        W, L, H, g, amp = atrapy_koron.TYPY[typ]
        m = atrapy_koron.korona(W, L, H, g, amp, n_theta=96, n_u=120, rng=rng)
        p = katalog / f"a{i}_{typ}.stl"
        m.export(p)
        pliki.append(p)
    return pliki


def zaslon_dolki(skan: trimesh.Trimesh, uk: U.UkladPlytki, bity: list[str]) -> trimesh.Trimesh:
    """Kladzie na dolkach ``bity`` walec fi 4 x 3 mm i usuwa wierzch plytki pod nim (skaner nie widzi pod przedmiotem).

    Skan w ukladzie plytki (przed przycieciem do pola i przed losowa poza). ``synth.py`` nie ma takiej opcji - siatka
    jest skladana tutaj, generator zostaje bez zmian.
    """
    c = skan.triangles_center
    zostaw = np.ones(len(skan.faces), dtype=bool)
    czesci = []
    for d in uk.code_dimples:
        if d.bit not in bity:
            continue
        zostaw &= ~((np.hypot(c[:, 0] - d.x, c[:, 1] - d.y) <= PROMIEN_ZASLONY) & (c[:, 2] <= uk.thickness + 0.2))
        walec = trimesh.creation.cylinder(radius=PROMIEN_ZASLONY, height=WYSOKOSC_ZASLONY, sections=48)
        walec = walec.subdivide().subdivide()
        walec.apply_translation([d.x, d.y, uk.thickness + WYSOKOSC_ZASLONY / 2])
        walec.update_faces(walec.triangles_center[:, 2] > uk.thickness + 0.05)  # bez spodu: lezy na plytce
        czesci.append(walec)
    plytka = trimesh.Trimesh(skan.vertices, skan.faces[zostaw], process=False)
    plytka.remove_unreferenced_vertices()
    return trimesh.util.concatenate([plytka, *czesci])


def skan_syntetyczny(uk: U.UkladPlytki, numer: int, projekty: list[Path], seed: int, pole: float = 100.0, ust: dict | None = None,
                     zaslon: list[str] | None = None):
    """Sztuczny skan plytki ``uk`` nr ``numer``: 3 atrapy, losowa poza skanera, pole fi ``pole``, skala 1,22 / 1,0.

    ``zaslon`` (lista bitow) = dolki kodu zasloniete przedmiotem; wtedy przyciecie do pola i poza sa nakladane tutaj
    funkcjami ``synth.przytnij_do_kola`` i ``synth.losowa_poza_skanu`` (te same co w generatorze).
    """
    w = 1.0 if synth.poranna(uk.nazwa) else 1.22
    wspolne = dict(plytka=uk.nazwa, prace_na_plytce=len(projekty), wspolczynnik=(w, w), ubytki_na_prace=(0, 0))
    rng = np.random.default_rng(seed)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if not zaslon:
            op = synth.Opcje.z_toml(ust, poza_uklad=True, pole=float(pole), **wspolne)
            return synth.generuj_plytke(uk, numer, list(projekty), rng, op, seed)
        op = synth.Opcje.z_toml(ust, poza_uklad=False, **wspolne)
        skan, prawda = synth.generuj_plytke(uk, numer, list(projekty), rng, op, seed)
        skan = zaslon_dolki(skan, uk, zaslon)
        sr = rng.uniform(-1.5, 1.5, 2)
        skan = synth.przytnij_do_kola(skan, sr, float(pole) / 2)
        P = synth.losowa_poza_skanu(rng)
        skan.apply_transform(P)
        prawda.pole_d, prawda.pole_srodek, prawda.poza_skanu = float(pole), [float(sr[0]), float(sr[1])], P.tolist()
    return skan, prawda


def rozpoznaj(skan: trimesh.Trimesh, kandydaci: list[U.UkladPlytki], numer: int | None, ciecie: bool = False) -> dict:
    """Jedno wywolanie ``plate.rozpoznaj_uklad``; wyjatek = wpis z polem ``blad`` (brak wyniku). ``_wyr`` nie idzie do pliku."""
    t0 = time.perf_counter()
    try:
        with warnings.catch_warnings(record=True) as ostrz:
            warnings.simplefilter("always")
            wyr, info = plate.rozpoznaj_uklad(skan, kandydaci, numer=numer, ciecie=ciecie)
    except Exception as e:  # noqa: BLE001 - blad jednego skanu nie zatrzymuje pomiaru
        return {"wybrany": None, "pewny": False, "powod": None, "blad": f"{type(e).__name__}: {str(e)[:200]}",
                "czas_scienny_s": round(time.perf_counter() - t0, 3), "kandydatow": len(kandydaci), "numer_podany": numer}
    return {
        "wybrany": info["wybrany"], "pewny": bool(info["pewny"]), "powod": info["powod"], "blad": None,
        "numer": wyr.numer, "numer_zrodlo": wyr.numer_zrodlo, "numer_z_dolkow": wyr.numer_z_dolkow,
        "bity": list(wyr.bity), "czas_rozpoznania_s": info["czas_rozpoznania_s"], "czas_scienny_s": round(time.perf_counter() - t0, 3),
        "kandydatow": len(kandydaci), "numer_podany": numer,
        "rodzina": [{k: c.get(k) for k in POLA_FRAGMENTU_RODZINY} for c in info["kandydaci"] if c["stozki_pasuja"]],
        "ostrzezenia": [str(o.message)[:200] for o in ostrz][:6],
        "_wyr": wyr,
    }


def numery_niezgodne(uk: U.UkladPlytki, numer: int) -> list[tuple[str, int]]:
    """Numery podane NIEZGODNE z plytka ``uk`` nr ``numer``: (rodzaj, numer podany)."""
    wynik = []
    inne = [n for n in uk.numery if n != numer]
    if inne:
        wynik.append(("inny_numer_ukladu", inne[0]))
    wynik.append(("numer_drugiej_pory", PARA_PORY[numer]))
    rano = synth.poranna(uk.nazwa)
    wynik.append(("numer_drugiego_ksztaltu", (9 if rano else 8) if numer <= 6 else (4 if rano else 1)))
    return wynik


def klasa(w: dict) -> str:
    """dobry_pewny | dobry_niepewny | zly_niepewny | zly_pewny | brak_wyniku (wyjatek rozpoznania)."""
    if w.get("blad"):
        return "brak_wyniku"
    dobry = w["wybrany"] == w["prawda"]
    return ("dobry" if dobry else "zly") + ("_pewny" if w["pewny"] else "_niepewny")


# ----------------------------------------------------------------------------
# ocena kryteriow (funkcje bez liczenia - do testow)
# ----------------------------------------------------------------------------
def ocen_k2(wpisy: list[dict]) -> dict:
    ok = [w for w in wpisy if klasa(w) == "dobry_pewny" and w.get("gniazda_zgodne") is True]
    zle = [w for w in wpisy if w not in ok]
    return {"przebiegow": len(wpisy), "ok": len(ok), "pelny_zestaw": len(wpisy) >= SKANOW_K2,
            "spelnione": bool(wpisy) and len(ok) == len(wpisy) and len(wpisy) >= SKANOW_K2,
            "powody": dict(Counter(str(w["powod"]) for w in wpisy)),
            "numer_ok": sum(w.get("numer") == w["numer_prawda"] for w in wpisy),
            "zle": [{k: w.get(k) for k in ("skan", "tryb", "wybrany", "pewny", "powod", "gniazda_zgodne", "blad")} for w in zle]}


def ocen_k3(wpisy: list[dict]) -> dict:
    pary: dict[tuple, dict] = {}
    for w in wpisy:
        pary.setdefault((w["skan"], w["tryb"]), {})[w["kandydatow_zestaw"]] = w
    wiersze = []
    for (skan, tryb), p in sorted(pary.items()):
        if 8 not in p or 10 not in p:
            continue
        a, b = p[8], p[10]
        wiersze.append({
            "skan": skan, "tryb": tryb, "prawda": a["prawda"], "wybrany_8": a["wybrany"], "wybrany_10": b["wybrany"],
            "pewny_8": a["pewny"], "pewny_10": b["pewny"], "powod_8": a["powod"], "powod_10": b["powod"],
            "ten_sam_uklad": a["wybrany"] == b["wybrany"] and bool(a.get("blad")) == bool(b.get("blad")),
            "pewnosc_nie_gorsza": not (a["pewny"] and not b["pewny"]),
            "numer_ten_sam": (a.get("numer"), a.get("numer_zrodlo")) == (b.get("numer"), b.get("numer_zrodlo")),
            "zgodny_z_prawda_8": a["wybrany"] == a["prawda"], "zgodny_z_prawda_10": b["wybrany"] == b["prawda"],
            "macierz_roznica_max": b.get("macierz_roznica_max"),
        })
    dobre = [x for x in wiersze if x["ten_sam_uklad"] and x["pewnosc_nie_gorsza"]]
    skany = sorted({x["skan"] for x in wiersze})
    skany_ok = [s for s in skany if all(x["ten_sam_uklad"] and x["pewnosc_nie_gorsza"] for x in wiersze if x["skan"] == s)
                and {x["tryb"] for x in wiersze if x["skan"] == s} == {"bez_numeru", "z_numerem"}]
    per_tryb = {}
    for tryb in ("bez_numeru", "z_numerem"):
        r = [x for x in wiersze if x["tryb"] == tryb]
        per_tryb[tryb] = {
            "par": len(r), "ten_sam_uklad": sum(x["ten_sam_uklad"] for x in r), "pewnosc_nie_gorsza": sum(x["pewnosc_nie_gorsza"] for x in r),
            "pewny_8": sum(bool(x["pewny_8"]) for x in r), "pewny_10": sum(bool(x["pewny_10"]) for x in r),
            "zgodny_z_prawda_8": sum(x["zgodny_z_prawda_8"] for x in r), "zgodny_z_prawda_10": sum(x["zgodny_z_prawda_10"] for x in r),
            "numer_ten_sam": sum(x["numer_ten_sam"] for x in r),
            "przejscia_powod": dict(Counter(f"{x['powod_8']} -> {x['powod_10']}" for x in r)),
        }
    roznice = [x["macierz_roznica_max"] for x in wiersze if x["macierz_roznica_max"] is not None]
    return {"skanow": len(skany), "skanow_ok": len(skany_ok), "par": len(wiersze), "par_ok": len(dobre),
            "spelnione": bool(skany) and len(skany_ok) == len(skany), "per_tryb": per_tryb,
            "macierz_roznica_max": max(roznice) if roznice else None,
            "zle": [x for x in wiersze if x not in dobre], "pary": wiersze}


def ocen_k4(wpisy: list[dict], uklady: dict[str, list[int]] | None = None, ziarna_min: int = 2) -> dict:
    """``uklady``: nazwa -> numery (do sprawdzenia, czy zestaw jest pelny); bez niego pole ``pelny_zestaw`` = None."""
    per_pole = {}
    for pole in sorted({w["pole"] for w in wpisy}, reverse=True):
        r = [w for w in wpisy if w["pole"] == pole and w["kandydatow_zestaw"] == 10]
        zgodne = [w for w in r if w["tryb"] in ("bez_numeru", "z_numerem")]
        niezg = [w for w in r if w["tryb"] not in ("bez_numeru", "z_numerem")]
        niezg8 = [w for w in wpisy if w["pole"] == pole and w["kandydatow_zestaw"] == 8]
        pelny = None
        if uklady is not None:
            pelny = all(len({w["seed"] for w in zgodne if (w["prawda"], w["numer_prawda"], w["tryb"]) == (n, nr, t)}) >= ziarna_min
                        for n, numery in uklady.items() for nr in numery for t in ("bez_numeru", "z_numerem"))

        def licz(lista: list[dict]) -> dict:
            return {"przebiegow": len(lista), **{k: sum(klasa(w) == k for w in lista) for k in
                                                  ("dobry_pewny", "dobry_niepewny", "zly_niepewny", "zly_pewny", "brak_wyniku")}}

        def lista_zlych(lista: list[dict]) -> list[dict]:
            return [{k: w.get(k) for k in ("skan", "tryb", "numer_podany", "prawda", "numer_prawda", "wybrany", "pewny", "powod", "numer", "numer_zrodlo",
                                           "numer_z_dolkow")} for w in lista if klasa(w) == "zly_pewny"]

        per_uklad = {}
        for nazwa in sorted({w["prawda"] for w in zgodne}):
            per_uklad[nazwa] = {t: {**licz([w for w in zgodne if w["prawda"] == nazwa and w["tryb"] == t]),
                                    "powody": dict(Counter(str(w["powod"]) for w in zgodne if w["prawda"] == nazwa and w["tryb"] == t and not w.get("blad")))}
                                for t in ("bez_numeru", "z_numerem")}
        per_pole[str(pole)] = {
            "pelny_zestaw": pelny, "zgodne": licz(zgodne), "per_tryb": {t: licz([w for w in zgodne if w["tryb"] == t]) for t in ("bez_numeru", "z_numerem")},
            "niepewne": sum(klasa(w) in ("dobry_niepewny", "zly_niepewny") for w in zgodne),
            "dobry_niepewny_powody": dict(Counter(str(w["powod"]) for w in zgodne if klasa(w) == "dobry_niepewny")),
            "zly_niepewny_powody": dict(Counter(f"{w['prawda']} -> {w['wybrany']} ({w['powod']})" for w in zgodne if klasa(w) == "zly_niepewny")),
            "brak_wyniku_bledy": dict(Counter(str(w["blad"]).split(":")[0] for w in zgodne if w.get("blad"))),
            "zly_pewny_lista": lista_zlych(zgodne), "per_uklad": per_uklad,
            "niezgodne_10": {**licz(niezg), "zly_pewny_lista": lista_zlych(niezg)},
            "niezgodne_8": {**licz(niezg8), "zly_pewny_lista": lista_zlych(niezg8)},
        }
    zly_pewny = sum(p["zgodne"]["zly_pewny"] for p in per_pole.values())
    zly_pewny_niezg = sum(p["niezgodne_10"]["zly_pewny"] for p in per_pole.values())
    return {"per_pole": per_pole, "zly_pewny_zgodne": zly_pewny, "zly_pewny_niezgodne_10": zly_pewny_niezg,
            "zly_pewny_niezgodne_8": sum(p["niezgodne_8"]["zly_pewny"] for p in per_pole.values()),
            "pelny_zestaw": None if uklady is None else all(p["pelny_zestaw"] for p in per_pole.values()) and bool(per_pole),
            "spelnione": bool(per_pole) and zly_pewny == 0 and (uklady is None or all(p["pelny_zestaw"] for p in per_pole.values()))}


def ocen_k6(wpisy: list[dict]) -> dict:
    wynik: dict = {"per_tryb": {}}
    przyrosty = []
    for tryb in ("bez_numeru", "z_numerem"):
        c8 = {w["skan"]: w["czas_scienny_s"] for w in wpisy if w["tryb"] == tryb and w["kandydatow_zestaw"] == 8 and not w.get("blad")}
        c10 = {w["skan"]: w["czas_scienny_s"] for w in wpisy if w["tryb"] == tryb and w["kandydatow_zestaw"] == 10 and not w.get("blad")}
        skany = sorted(set(c8) & set(c10))
        if not skany:
            continue
        m8, m10 = statistics.median(c8[s] for s in skany), statistics.median(c10[s] for s in skany)
        roznice = [c10[s] - c8[s] for s in skany]
        wynik["per_tryb"][tryb] = {"pomiarow": len(skany), "mediana_8_s": round(m8, 3), "mediana_10_s": round(m10, 3), "przyrost_mediany_s": round(m10 - m8, 3),
                                   "mediana_roznic_par_s": round(statistics.median(roznice), 3), "max_roznica_pary_s": round(max(roznice), 3),
                                   "min_8_s": round(min(c8[s] for s in skany), 3), "max_8_s": round(max(c8[s] for s in skany), 3),
                                   "min_10_s": round(min(c10[s] for s in skany), 3), "max_10_s": round(max(c10[s] for s in skany), 3)}
        przyrosty.append(m10 - m8)
    wynik["przyrost_mediany_max_s"] = round(max(przyrosty), 3) if przyrosty else None
    wynik["spelnione"] = bool(przyrosty) and max(przyrosty) <= PRZYROST_CZASU_MAX_S
    return wynik


def ocen_z(wpisy: list[dict]) -> dict:
    per = {}
    for wariant in sorted({w["zaslona"] for w in wpisy}):
        for tryb in ("bez_numeru", "z_numerem"):
            r = [w for w in wpisy if w["zaslona"] == wariant and w["tryb"] == tryb]
            per[f"{wariant}/{tryb}"] = {
                "przebiegow": len(r), **{k: sum(klasa(w) == k for w in r) for k in ("dobry_pewny", "dobry_niepewny", "zly_niepewny", "zly_pewny", "brak_wyniku")},
                "powody": dict(Counter(str(w["powod"]) for w in r)), "numer_ok": sum(w.get("numer") == w["numer_prawda"] for w in r),
                "numer_zly": [{"skan": w["skan"], "numer_prawda": w["numer_prawda"], "numer": w.get("numer"), "numer_zrodlo": w.get("numer_zrodlo"),
                               "numer_z_dolkow": w.get("numer_z_dolkow"), "wybrany": w["wybrany"], "pewny": w["pewny"]}
                              for w in r if w.get("numer") != w["numer_prawda"]]}
    return {"skanow": len({w["skan"] for w in wpisy}), "per_wariant": per}


OCENY = {"2": ocen_k2, "3": ocen_k3, "4": ocen_k4, "6": ocen_k6, "z": ocen_z}


# ----------------------------------------------------------------------------
# tabela tekstowa (ASCII)
# ----------------------------------------------------------------------------
def tabela(wynik: dict) -> str:
    L = [f"auto_uklad_r58: {wynik['data']}  kandydaci 10: {', '.join(wynik['kandydaci_10'])}",
         f"uwaga: {wynik.get('uwaga') or '-'}"]
    k = wynik["kryteria"]
    tn = lambda v: "SPELNIONE" if v else "NIESPELNIONE"  # noqa: E731
    if "2" in k:
        o = k["2"]
        L += ["", f"KRYTERIUM 2 (ramkowe syntetyczne, pole 100, 10 kandydatow): {o['ok']} z {o['przebiegow']} uklad dobry, pewny, gniazda = prawda "
                  f"(numer zgodny {o['numer_ok']} z {o['przebiegow']}); powody {o['powody']} -> {tn(o['spelnione'])}"
                  + ("" if o["pelny_zestaw"] else " (zestaw niepelny)")]
        L += [f"  ZLE {z}" for z in o["zle"]]
    if "3" in k:
        o = k["3"]
        L += ["", f"KRYTERIUM 3 (BRAMKA; skany odniesienia, 8 vs 10 kandydatow): {o['skanow_ok']} z {o['skanow']} skanow ten sam uklad i nie gorsza pewnosc "
                  f"(pary {o['par_ok']} z {o['par']}; najwieksza roznica macierzy {o['macierz_roznica_max']}) -> {tn(o['spelnione'])}"]
        for tryb, p in o["per_tryb"].items():
            L.append(f"  {tryb:11s} par {p['par']}: ten sam uklad {p['ten_sam_uklad']}, pewnosc nie gorsza {p['pewnosc_nie_gorsza']}, pewny 8/10 kand. {p['pewny_8']}/{p['pewny_10']}, "
                     f"zgodny z prawda 8/10 kand. {p['zgodny_z_prawda_8']}/{p['zgodny_z_prawda_10']}, numer i zrodlo te same {p['numer_ten_sam']}")
            L += [f"      powod {a}: {n}" for a, n in sorted(p["przejscia_powod"].items())]
        L += [f"  ZLE {z['skan']} [{z['tryb']}] prawda {z['prawda']}: 8 -> {z['wybrany_8']} pewny={z['pewny_8']} {z['powod_8']}; 10 -> {z['wybrany_10']} pewny={z['pewny_10']} {z['powod_10']}"
              for z in o["zle"]]
    if "4" in k:
        o = k["4"]
        L += ["", f"KRYTERIUM 4 (BRAMKA; 10 kandydatow, kazdy uklad i numer, numer zgodny albo brak): pewny ze zlym ukladem {o['zly_pewny_zgodne']} -> {tn(o['spelnione'])}"
                  + ("" if o["pelny_zestaw"] in (True, None) else " (zestaw niepelny)"),
              f"  numer podany NIEZGODNY: pewny ze zlym ukladem {o['zly_pewny_niezgodne_10']} (10 kandydatow), {o['zly_pewny_niezgodne_8']} (8 kandydatow, uklady sprzed paczki)",
              "  pole  przebiegow  dobry_pewny  dobry_niepewny  zly_niepewny  zly_pewny  brak_wyniku"]
        for pole, p in o["per_pole"].items():
            z = p["zgodne"]
            L.append(f"  {pole:>5s} {z['przebiegow']:>10d} {z['dobry_pewny']:>12d} {z['dobry_niepewny']:>15d} {z['zly_niepewny']:>13d} {z['zly_pewny']:>10d} {z['brak_wyniku']:>12d}")
        for pole, p in o["per_pole"].items():
            L.append(f"  pole {pole}: niepewnych {p['niepewne']}; dobry uklad niepewny wg powodu {p['dobry_niepewny_powody']}; zly uklad niepewny {p['zly_niepewny_powody']}; "
                     f"brak wyniku {p['brak_wyniku_bledy']}")
            for nazwa, t in p["per_uklad"].items():
                L.append("    " + f"{nazwa:27s}" + "  ".join(
                    f"{tryb}: dp {x['dobry_pewny']} dn {x['dobry_niepewny']} zn {x['zly_niepewny']} zp {x['zly_pewny']} brak {x['brak_wyniku']} {x['powody']}" for tryb, x in t.items()))
            for nazwa_listy, lista in (("ZLY PEWNY", p["zly_pewny_lista"]), ("ZLY PEWNY (numer niezgodny, 10)", p["niezgodne_10"]["zly_pewny_lista"]),
                                       ("ZLY PEWNY (numer niezgodny, 8)", p["niezgodne_8"]["zly_pewny_lista"])):
                L += [f"    {nazwa_listy} {z}" for z in lista]
            for n in ("niezgodne_10", "niezgodne_8"):
                x = p[n]
                L.append(f"    {n}: przebiegow {x['przebiegow']}, dobry_pewny {x['dobry_pewny']}, dobry_niepewny {x['dobry_niepewny']}, zly_niepewny {x['zly_niepewny']}, "
                         f"zly_pewny {x['zly_pewny']}, brak_wyniku {x['brak_wyniku']}")
    if "6" in k:
        o = k["6"]
        L += ["", f"KRYTERIUM 6 (czas rozpoznania plytek R59, 8 vs 10 kandydatow): najwiekszy przyrost mediany {o['przyrost_mediany_max_s']} s (prog {PRZYROST_CZASU_MAX_S} s) -> {tn(o['spelnione'])}"]
        L += [f"  {tryb:11s} pomiarow {p['pomiarow']}: mediana 8 kand. {p['mediana_8_s']} s ({p['min_8_s']}-{p['max_8_s']}), 10 kand. {p['mediana_10_s']} s ({p['min_10_s']}-{p['max_10_s']}), "
              f"przyrost mediany {p['przyrost_mediany_s']} s, mediana roznic par {p['mediana_roznic_par_s']} s, max roznica pary {p['max_roznica_pary_s']} s" for tryb, p in o["per_tryb"].items()]
    if "z" in k:
        o = k["z"]
        L += ["", f"DODATKOWO (dolki kodu zasloniete przedmiotem, plytki ramkowe, pole 100, 10 kandydatow): skanow {o['skanow']}"]
        for nazwa, p in o["per_wariant"].items():
            L.append(f"  {nazwa:24s} przebiegow {p['przebiegow']}: dobry_pewny {p['dobry_pewny']}, dobry_niepewny {p['dobry_niepewny']}, zly_niepewny {p['zly_niepewny']}, zly_pewny {p['zly_pewny']}, "
                     f"brak {p['brak_wyniku']}; powody {p['powody']}; numer = prawda {p['numer_ok']} z {p['przebiegow']}")
            L += [f"      NUMER {z}" for z in p["numer_zly"]]
    b = wynik["bramka"]
    L += ["", "BRAMKA (kryteria 3 i 4): " + ("nie zmierzono w tym przebiegu (potrzebne oba kryteria)" if b["spelniona"] is None else ("SPELNIONA" if b["spelniona"] else "NIESPELNIONA"))]
    return "\n".join(str(x) for x in L).encode("ascii", "backslashreplace").decode("ascii") + "\n"


# ----------------------------------------------------------------------------
# przebieg
# ----------------------------------------------------------------------------
class Dziennik:
    """Przebiegi w ``przebiegi.jsonl``: dopisywane od razu; ``--wznow`` wczytuje zapisane i pomija powtorki."""

    def __init__(self, plik: Path, wznow: bool):
        self.plik = plik
        self.wpisy: list[dict] = []
        if wznow and plik.exists():
            self.wpisy = [json.loads(w) for w in plik.read_text(encoding="utf-8").split("\n") if w.strip()]
        elif plik.exists():
            plik.unlink()
        self.klucze = {self.klucz(w) for w in self.wpisy}

    @staticmethod
    def klucz(w: dict) -> tuple:
        return (w["kryterium"], w["skan"], w["tryb"], w.get("numer_podany"), w["kandydatow_zestaw"])

    def jest(self, **pola) -> bool:
        return self.klucz(pola) in self.klucze

    def dopisz(self, w: dict) -> None:
        w = {k: v for k, v in w.items() if not k.startswith("_")}
        self.wpisy.append(w)
        self.klucze.add(self.klucz(w))
        with self.plik.open("a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(w, ensure_ascii=True) + "\n")
        print(f"[{dt.datetime.now():%H:%M:%S}] k{w['kryterium']} {w['skan']} {w['tryb']} podany={w.get('numer_podany')} kand={w['kandydatow_zestaw']} -> "
              f"{w['wybrany']} pewny={w['pewny']} {w['powod'] or w.get('blad', '')[:60]} {w['czas_scienny_s']} s".encode("ascii", "backslashreplace").decode("ascii"), flush=True)


def _prawda_gniazda(prawda) -> set:
    return {p.gniazdo for p in prawda.prace}


def przebieg(a: argparse.Namespace) -> dict:
    ust = UST.wczytaj_ustawienia(a.ustawienia if a.ustawienia is not None else UST.PLIK_PRZYKLADU)
    k10, k8 = uklady_kandydaci(ust)
    zestawy = {10: k10, 8: k8}
    wg_nazwy = {u.nazwa: u for u in k10}
    if not set(RAMKOWE) <= set(wg_nazwy):
        raise SystemExit(f"w [plytki] ustawien nie ma ukladow {', '.join(RAMKOWE)} - pomiar wymaga 10 ukladow")
    a.wyjscie.mkdir(parents=True, exist_ok=True)
    dz = Dziennik(a.wyjscie / "przebiegi.jsonl", a.wznow)
    korony = atrapy(a.wyjscie / "atrapy")
    skany_odn = []
    for f in a.odniesienie or []:
        z = sorted(p for p in Path(f).glob("skan_*.stl") if p.with_suffix(".json").exists())
        skany_odn += z[: a.limit] if a.limit else z

    def uruchom(kryterium: str, skan_nazwa: str, siatka, prawda, tryb: str, numer, zestaw: int, ciecie: bool = False, **dodatkowe) -> dict | None:
        if dz.jest(kryterium=kryterium, skan=skan_nazwa, tryb=tryb, numer_podany=numer, kandydatow_zestaw=zestaw):
            return None
        w = rozpoznaj(siatka() if callable(siatka) else siatka, zestawy[zestaw], numer, ciecie=ciecie)
        w.update({"kryterium": kryterium, "skan": skan_nazwa, "tryb": tryb, "kandydatow_zestaw": zestaw, "prawda": prawda.plytka, "numer_prawda": prawda.numer,
                  "pole": prawda.pole_d, "prac": len(prawda.prace), **dodatkowe})
        if ciecie and not w.get("blad"):
            w["gniazda_zgodne"] = {f.gniazdo for f in w["_wyr"].fragmenty if f.status == "praca"} == _prawda_gniazda(prawda)
        return w

    # --- kryterium 2 ---
    if "2" in a.kryteria:
        zadania = [(n, nr, i) for n in RAMKOWE for nr in wg_nazwy[n].numery for i in range(a.ziarna_k2)]
        for n, nr, i in zadania[: a.limit] if a.limit else zadania:
            seed = 5800 + nr * 10 + i
            nazwa = f"syn_{n}_n{nr}_s{seed}_p100"
            if all(dz.jest(kryterium="2", skan=nazwa, tryb=t, numer_podany=p, kandydatow_zestaw=10) for t, p in (("bez_numeru", None), ("z_numerem", nr))):
                continue
            skan, prawda = skan_syntetyczny(wg_nazwy[n], nr, korony, seed, 100.0, ust)
            for tryb, podany in (("bez_numeru", None), ("z_numerem", nr)):
                w = uruchom("2", nazwa, skan, prawda, tryb, podany, 10, ciecie=True, seed=seed)
                if w:
                    dz.dopisz(w)

    # --- kryterium 3 ---
    if "3" in a.kryteria:
        if not skany_odn:
            raise SystemExit("kryterium 3: brak skanow odniesienia (--odniesienie <folder> ze skan_*.stl i prawda .json)")
        for plik in skany_odn:
            nazwa = f"{plik.parent.name}/{plik.stem}"
            prawda = synth.wczytaj_prawde(plik.with_suffix(".json"))
            tryby = (("bez_numeru", None), ("z_numerem", prawda.numer))
            if all(dz.jest(kryterium="3", skan=nazwa, tryb=t, numer_podany=p, kandydatow_zestaw=z) for t, p in tryby for z in (8, 10)):
                continue
            siatka = trimesh.load(plik, force="mesh")
            for tryb, podany in tryby:
                para = {}
                for zestaw in (8, 10):
                    w = uruchom("3", nazwa, siatka, prawda, tryb, podany, zestaw)
                    if w:
                        para[zestaw] = w
                if len(para) == 2 and not para[8].get("blad") and not para[10].get("blad") and para[8]["wybrany"] == para[10]["wybrany"]:
                    para[10]["macierz_roznica_max"] = float(np.abs(para[8]["_wyr"].macierz - para[10]["_wyr"].macierz).max())
                for w in para.values():
                    dz.dopisz(w)

    # --- kryterium 4 ---
    if "4" in a.kryteria:
        zadania = [(pole, u, nr, i) for pole in a.pola for u in k10 for nr in u.numery for i in range(a.ziarna_k4)]
        for pole, uk, nr, i in zadania[: a.limit] if a.limit else zadania:
            seed = 4000 + k10.index(uk) * 100 + nr * 10 + i
            nazwa = f"syn_{uk.nazwa}_n{nr}_s{seed}_p{pole:g}"
            lista = [("bez_numeru", None, 10), ("z_numerem", nr, 10)]
            if i == 0:
                for rodzaj, podany in numery_niezgodne(uk, nr):
                    lista.append((f"niezgodny:{rodzaj}", podany, 10))
                    if uk.nazwa not in RAMKOWE:
                        lista.append((f"niezgodny:{rodzaj}", podany, 8))
            if all(dz.jest(kryterium="4", skan=nazwa, tryb=t, numer_podany=p, kandydatow_zestaw=z) for t, p, z in lista):
                continue
            skan, prawda = skan_syntetyczny(uk, nr, korony, seed, pole, ust)
            for tryb, podany, zestaw in lista:
                w = uruchom("4", nazwa, skan, prawda, tryb, podany, zestaw, seed=seed)
                if w:
                    dz.dopisz(w)

    # --- kryterium 6 ---
    if "6" in a.kryteria:
        r59 = [p for p in skany_odn if not U.WZOR_WERSJI_UKLADU.search(synth.wczytaj_prawde(p.with_suffix(".json")).plytka)]
        if not r59:
            raise SystemExit("kryterium 6: brak skanow plytek R59 w folderach --odniesienie")
        n = min(a.pomiary_k6, len(r59))
        wybrane = [r59[round(j * (len(r59) - 1) / max(n - 1, 1))] for j in range(n)]
        rozgrzane = False
        for j, plik in enumerate(wybrane):
            nazwa = f"{plik.parent.name}/{plik.stem}"
            prawda = synth.wczytaj_prawde(plik.with_suffix(".json"))
            tryby = (("bez_numeru", None), ("z_numerem", prawda.numer))
            if all(dz.jest(kryterium="6", skan=nazwa, tryb=t, numer_podany=p, kandydatow_zestaw=z) for t, p in tryby for z in (8, 10)):
                continue
            siatka = trimesh.load(plik, force="mesh")
            if not rozgrzane:  # pierwsze wywolanie w procesie nie jest pomiarem (ladowanie bibliotek)
                rozpoznaj(siatka, k8, None)
                rozgrzane = True
            for tryb, podany in tryby:
                for zestaw in ((8, 10) if j % 2 == 0 else (10, 8)):  # na przemian: kolejnosc nie sprzyja zadnemu zestawowi
                    w = uruchom("6", nazwa, siatka, prawda, tryb, podany, zestaw, kolejnosc=j % 2)
                    if w:
                        dz.dopisz(w)

    # --- dodatkowo: dolki zasloniete ---
    if "z" in a.kryteria:
        zadania = [(n, nr) for n in RAMKOWE for nr in wg_nazwy[n].numery]
        for n, nr in zadania[: a.limit] if a.limit else zadania:
            uk = wg_nazwy[n]
            ustawione = [d.bit for d, b in zip(uk.code_dimples, U.UkladPlytki.bity_z_numeru(nr, uk.liczba_bitow)) if b]
            for wariant, bity in (("wszystkie_dolki", [d.bit for d in uk.code_dimples]), ("jeden_dolek", ustawione[:1])):
                seed = 6800 + nr
                nazwa = f"syn_{n}_n{nr}_s{seed}_p100_zaslona_{wariant}"
                tryby = (("bez_numeru", None), ("z_numerem", nr))
                if all(dz.jest(kryterium="z", skan=nazwa, tryb=t, numer_podany=p, kandydatow_zestaw=10) for t, p in tryby):
                    continue
                skan, prawda = skan_syntetyczny(uk, nr, korony, seed, 100.0, ust, zaslon=bity)
                for tryb, podany in tryby:
                    w = uruchom("z", nazwa, skan, prawda, tryb, podany, 10, ciecie=True, seed=seed, zaslona=wariant, zasloniete_bity=bity)
                    if w:
                        dz.dopisz(w)

    kryteria = {}
    for k in KRYTERIA:
        wpisy = [w for w in dz.wpisy if w["kryterium"] == k]
        if not wpisy:
            continue
        kryteria[k] = ocen_k4(wpisy, {u.nazwa: list(u.numery) for u in k10}, a.ziarna_k4) if k == "4" else OCENY[k](wpisy)
    bramka = kryteria["3"]["spelnione"] and kryteria["4"]["spelnione"] if "3" in kryteria and "4" in kryteria else None
    wynik = {
        "narzedzie": "auto_uklad_r58", "data": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "uwaga": a.uwaga,
        "kandydaci_10": [u.nazwa for u in k10], "kandydaci_8": [u.nazwa for u in k8],
        "parametry": {"kryteria": list(a.kryteria), "pola": list(a.pola), "ziarna_k2": a.ziarna_k2, "ziarna_k4": a.ziarna_k4, "pomiary_k6": a.pomiary_k6,
                      "limit": a.limit, "odniesienie": [Path(f).name for f in a.odniesienie or []], "prog_ksztaltu_mm2": plate.PROG_KSZTALTU_MM2},
        "kryteria": kryteria, "bramka": {"spelniona": bramka, "kryterium_3": kryteria.get("3", {}).get("spelnione"), "kryterium_4": kryteria.get("4", {}).get("spelnione")},
        "przebiegi": dz.wpisy,
    }
    (a.wyjscie / "auto_uklad_r58.json").write_text(json.dumps(wynik, ensure_ascii=True, indent=1) + "\n", encoding="ascii", newline="\n")
    tekst = tabela(wynik)
    (a.wyjscie / "auto_uklad_r58.txt").write_text(tekst, encoding="ascii", newline="\n")
    print(tekst)
    print(a.wyjscie / "auto_uklad_r58.json")
    return wynik


def _lista_kryteriow(s: str) -> tuple[str, ...]:
    k = tuple(x.strip() for x in s.split(",") if x.strip())
    if not k or any(x not in KRYTERIA for x in k):
        raise argparse.ArgumentTypeError(f"kryteria z listy {', '.join(KRYTERIA)} rozdzielone przecinkami, jest {s!r}")
    return k


def _lista_pol(s: str) -> tuple[float, ...]:
    try:
        pola = tuple(float(x) for x in s.split(",") if x.strip())
    except ValueError:
        raise argparse.ArgumentTypeError(f"srednice pola w mm rozdzielone przecinkami, jest {s!r}") from None
    if not pola or any(not 60 <= p <= 200 for p in pola):
        raise argparse.ArgumentTypeError(f"srednice pola z zakresu 60-200 mm, jest {s!r}")
    return pola


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], epilog="Opis kryteriow: naglowek pliku narzedzia/auto_uklad_r58.py.")
    ap.add_argument("--wyjscie", type=Path, required=True, help="katalog wynikow (przebiegi.jsonl, auto_uklad_r58.json, auto_uklad_r58.txt, atrapy/)")
    ap.add_argument("--odniesienie", type=Path, nargs="*", default=[], help="foldery skanow odniesienia (skan_*.stl + prawda .json) - kryteria 3 i 6")
    ap.add_argument("--kryteria", type=_lista_kryteriow, default=("2", "3", "4", "6"), help="ktore kryteria mierzyc: 2,3,4,6,z (domyslnie 2,3,4,6)")
    ap.add_argument("--ustawienia", type=Path, default=None, help="plik ustawien z [plytki] (domyslnie ustawienia.przyklad.toml programu)")
    ap.add_argument("--pola", type=_lista_pol, default=(100.0, 90.0, 80.0), help="kryterium 4: srednice pola skanu w mm (domyslnie 100,90,80)")
    ap.add_argument("--ziarna-k2", type=int, default=4, help="kryterium 2: ziaren na numer (domyslnie 4)")
    ap.add_argument("--ziarna-k4", type=int, default=2, help="kryterium 4: ziaren na numer i pole (domyslnie 2)")
    ap.add_argument("--pomiary-k6", type=int, default=10, help="kryterium 6: liczba skanow R59 (domyslnie 10)")
    ap.add_argument("--limit", type=int, default=0, help="proba: najwyzej tyle skanow na kryterium / folder (0 = wszystkie)")
    ap.add_argument("--wznow", action="store_true", help="nie kasuj przebiegi.jsonl - pomin przebiegi juz zapisane")
    ap.add_argument("--uwaga", default="", help="tekst do wyniku, np. co jeszcze liczylo w czasie pomiaru")
    return ap


def main(argv: list[str] | None = None) -> int:
    a = parser().parse_args(argv)
    if min(a.ziarna_k2, a.ziarna_k4, a.pomiary_k6) < 1 or a.limit < 0:
        parser().error("--ziarna-k2, --ziarna-k4, --pomiary-k6 musza byc >= 1, --limit >= 0")
    wynik = przebieg(a)
    return 0 if all(o.get("spelnione", True) for o in wynik["kryteria"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
