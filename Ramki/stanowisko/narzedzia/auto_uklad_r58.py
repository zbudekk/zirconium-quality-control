"""Pomiar rozpoznania ukladu plytki po dodaniu plytek okraglych ramkowych n1-n6 (R58) - paczka E3-O1 (21.11.2026).

Uzycie (z katalogu stanowisko/; jeden proces, bez puli):
    python narzedzia/auto_uklad_r58.py --wyjscie <katalog> --odniesienie <folder> [<folder> ...]
           [--kryteria 2,3,4,6,g,z] [--ustawienia <plik>] [--pola 100,90,80] [--ziarna-k2 4] [--ziarna-k4 2]
           [--pomiary-k6 10] [--ziarna-g 3] [--limit N] [--wznow] [--uwaga "co jeszcze liczylo"]
    python narzedzia/auto_uklad_r58.py --wyjscie <katalog> --z-przebiegow <przebiegi.jsonl> [<przebiegi.jsonl> ...]

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
  g  "granice" - OGRANICZENIE (poza bramka), runda 2 recenzji: plytka okragla bez waznego numeru z dolkow, gdy w skanie
     nie ma scianki bocznej plytki. (a) plytki okragle testowe R59 n8 / n9: bez zaslony / dolek D zasloniety / 4 dolki
     zasloniete, pola 100, 99, 98, 97 mm i pole 100 ze skanem BEZ scianki bocznej (usuniete trojkaty ponizej wierzchu
     o srodku r >= 49 mm - "skaner patrzacy z gory"; konstrukcja, nie pomiar skanera), ``--ziarna-g`` ziaren, 8 i 10
     kandydatow: ile par "8: dobry i pewny -> 10: zly" i ile "pewny zly" przy 10; (b) plytki ramkowe n1, n2, n4, n5
     z 4 dolkami zaslonietymi, pola 100, 99, 98 i 100 bez scianki, bez numeru i z numerem zgodnym, 10 kandydatow: ile
     "kwadrat, pewny", jaki numer i zrodlo; (c) kontrola: kwadraty R59 n2 / n5 w polach jak (a), 10 kandydatow.
     Wynik nie wchodzi do wiersza BRAMKA ani do kodu wyjscia;
  z  plytka ramkowa z dolkami kodu zaslonietymi przez przedmiot lezacy na plytce (walec fi 4 x 3 mm na dolku, wierzch
     plytki pod nim usuniety): wszystkie dolki albo jeden dolek bitu ustawionego; pomiar dodatkowy, bez progu.

Kazdy przebieg jest dopisywany do ``<wyjscie>/przebiegi.jsonl`` zaraz po zakonczeniu (PC bywa restartowany);
``--wznow`` pomija przebiegi juz zapisane. ``--z-przebiegow`` niczego nie mierzy: ocenia wpisy z podanych plikow
``przebiegi.jsonl`` (np. wyniki wczesniejszego pomiaru po poprawce funkcji oceny). Na koniec: ``<wyjscie>/auto_uklad_r58.json`` (podsumowanie + przebiegi)
i ``<wyjscie>/auto_uklad_r58.txt`` (tabela, ASCII). W wyniku sa tylko nazwy skanow syntetycznych i skroty ``sha16``
projektow z plikow prawdy - bez nazw plikow projektow i bez sciezek katalogow (teksty ostrzezen i bledow ida przez
``baza.bez_sciezek``). Ocena: przebieg bez wyniku (wyjatek rozpoznania) nigdy nie liczy sie jako dobry - para 8 / 10
kandydatow bez wyniku jest para zla (kryterium 3), a kryterium 4 wymaga co najmniej jednego wyniku przy polu 100. Kod wyjscia: 0 = wszystkie zmierzone kryteria spelnione,
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
from stanowisko import baza as BA, plate, porownaj as PO, synth, uklad as U, ustawienia as UST  # noqa: E402

RAMKOWE = ("okragla_ramkowa_wieczorna", "okragla_ramkowa_poranna")
KRYTERIA = ("2", "3", "4", "6", "g", "z")
DOMYSLNE = ("2", "3", "4", "6", "g")
PRZYROST_CZASU_MAX_S = 1.0  # kryterium 6
SKANOW_K2 = 48  # kryterium 2: 6 numerow x 4 ziarna x 2 tryby
POLA_FRAGMENTU_RODZINY = ("uklad", "odrzucony", "numer_z_dolkow", "numer_z_dolkow_wazny", "dolki_widoczne", "numer_podany_pasuje",
                          "ksztalt_niewyjasnione_mm2", "ksztalt_strefa_mm2")
PARA_PORY = {1: 4, 2: 5, 3: 6, 4: 1, 5: 2, 6: 3, 8: 9, 9: 8}  # ten sam numer kolejny plytki drugiej pory dnia
PROMIEN_ZASLONY = 2.0  # mm: walec na dolku kodu (dolek fi 2)
WYSOKOSC_ZASLONY = 3.0
PROMIEN_SCIANKI = 49.0  # mm: trojkaty ponizej wierzchu o srodku dalej od osi plytki = scianka boczna (kryterium g)
POLA_GRANIC = ((100.0, False), (99.0, False), (98.0, False), (97.0, False), (100.0, True))  # (pole, bez scianki bocznej)
TESTOWE_GRANIC = (("okragla_wieczorna", 8), ("okragla_poranna", 9))
RAMKOWE_GRANIC = (("okragla_ramkowa_wieczorna", 1), ("okragla_ramkowa_wieczorna", 2), ("okragla_ramkowa_poranna", 4), ("okragla_ramkowa_poranna", 5))
KWADRATY_GRANIC = (("wieczorna", 2), ("poranna", 5))
KLASY = ("dobry_pewny", "dobry_niepewny", "zly_niepewny", "zly_pewny", "brak_wyniku")


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


def usun_scianke_boczna(skan: trimesh.Trimesh, uk: U.UkladPlytki) -> trimesh.Trimesh:
    """Skan w ukladzie plytki bez scianki bocznej: bez trojkatow ponizej wierzchu o srodku r >= 49,0 mm ("skaner patrzacy
    z gory"). Konstrukcja recenzenta PR #51 (proba W9 / D4), nie pomiar skanera."""
    c = skan.triangles_center
    scianka = (np.hypot(c[:, 0], c[:, 1]) >= PROMIEN_SCIANKI) & (c[:, 2] < uk.thickness - 0.05)
    bez = trimesh.Trimesh(skan.vertices, skan.faces[~scianka], process=False)
    bez.remove_unreferenced_vertices()
    return bez


def skan_syntetyczny(uk: U.UkladPlytki, numer: int, projekty: list[Path], seed: int, pole: float = 100.0, ust: dict | None = None,
                     zaslon: list[str] | None = None, bez_scianki: bool = False):
    """Sztuczny skan plytki ``uk`` nr ``numer``: 3 atrapy, losowa poza skanera, pole fi ``pole``, skala 1,22 / 1,0.

    ``zaslon`` (lista bitow) = dolki kodu zasloniete przedmiotem; ``bez_scianki`` = skan bez scianki bocznej plytki
    (``usun_scianke_boczna``). W obu przypadkach przyciecie do pola i poza sa nakladane tutaj funkcjami
    ``synth.przytnij_do_kola`` i ``synth.losowa_poza_skanu`` (te same co w generatorze).
    """
    w = 1.0 if synth.poranna(uk.nazwa) else 1.22
    wspolne = dict(plytka=uk.nazwa, prace_na_plytce=len(projekty), wspolczynnik=(w, w), ubytki_na_prace=(0, 0))
    rng = np.random.default_rng(seed)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if not zaslon and not bez_scianki:
            op = synth.Opcje.z_toml(ust, poza_uklad=True, pole=float(pole), **wspolne)
            return synth.generuj_plytke(uk, numer, list(projekty), rng, op, seed)
        op = synth.Opcje.z_toml(ust, poza_uklad=False, **wspolne)
        skan, prawda = synth.generuj_plytke(uk, numer, list(projekty), rng, op, seed)
        if zaslon:
            skan = zaslon_dolki(skan, uk, zaslon)
        if bez_scianki:
            skan = usun_scianke_boczna(skan, uk)
        sr = rng.uniform(-1.5, 1.5, 2)
        skan = synth.przytnij_do_kola(skan, sr, float(pole) / 2)
        P = synth.losowa_poza_skanu(rng)
        skan.apply_transform(P)
        prawda.pole_d, prawda.pole_srodek, prawda.poza_skanu = float(pole), [float(sr[0]), float(sr[1])], P.tolist()
    return skan, prawda


def bez_sciezek(tekst) -> str:
    """Tekst ostrzezenia / bledu bez sciezek katalogow (``plate`` wpisuje do ostrzezen katalog modelu, a ten na PC
    wlasciciela zawiera nazwe konta) - uwaga 4 recenzji PR #51."""
    return BA.bez_sciezek(str(tekst))


def bez_sciezek_w_wpisie(w: dict) -> dict:
    """Kopia wpisu przebiegu z ostrzezeniami i bledem bez sciezek (wpisy wczytane z pliku starszego pomiaru)."""
    w = dict(w)
    if w.get("ostrzezenia"):
        w["ostrzezenia"] = [bez_sciezek(o) for o in w["ostrzezenia"]]
    if w.get("blad"):
        w["blad"] = bez_sciezek(w["blad"])
    return w


def rozpoznaj(skan: trimesh.Trimesh, kandydaci: list[U.UkladPlytki], numer: int | None, ciecie: bool = False) -> dict:
    """Jedno wywolanie ``plate.rozpoznaj_uklad``; wyjatek = wpis z polem ``blad`` (brak wyniku). ``_wyr`` nie idzie do pliku."""
    t0 = time.perf_counter()
    try:
        with warnings.catch_warnings(record=True) as ostrz:
            warnings.simplefilter("always")
            wyr, info = plate.rozpoznaj_uklad(skan, kandydaci, numer=numer, ciecie=ciecie)
    except Exception as e:  # noqa: BLE001 - blad jednego skanu nie zatrzymuje pomiaru
        return {"wybrany": None, "pewny": False, "powod": None, "blad": f"{type(e).__name__}: {bez_sciezek(e)[:200]}",
                "czas_scienny_s": round(time.perf_counter() - t0, 3), "kandydatow": len(kandydaci), "numer_podany": numer}
    return {
        "wybrany": info["wybrany"], "pewny": bool(info["pewny"]), "powod": info["powod"], "blad": None,
        "numer": wyr.numer, "numer_zrodlo": wyr.numer_zrodlo, "numer_z_dolkow": wyr.numer_z_dolkow,
        "bity": list(wyr.bity), "czas_rozpoznania_s": info["czas_rozpoznania_s"], "czas_scienny_s": round(time.perf_counter() - t0, 3),
        "kandydatow": len(kandydaci), "numer_podany": numer,
        "rodzina": [{k: c.get(k) for k in POLA_FRAGMENTU_RODZINY} for c in info["kandydaci"] if c["stozki_pasuja"]],
        "ostrzezenia": [bez_sciezek(o.message)[:200] for o in ostrz][:6],
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
        # para jest dobra tylko, gdy OBA przebiegi maja wynik: brak wyniku w ktorymkolwiek = para zla, liczona osobno
        bez = bool(a.get("blad")) or bool(b.get("blad"))
        wiersze.append({
            "skan": skan, "tryb": tryb, "prawda": a["prawda"], "wybrany_8": a["wybrany"], "wybrany_10": b["wybrany"],
            "pewny_8": a["pewny"], "pewny_10": b["pewny"], "powod_8": a["powod"], "powod_10": b["powod"],
            "bez_wyniku": bez, "bez_wyniku_8": bool(a.get("blad")), "bez_wyniku_10": bool(b.get("blad")),
            "ten_sam_uklad": not bez and a["wybrany"] == b["wybrany"],
            "pewnosc_nie_gorsza": not bez and not (a["pewny"] and not b["pewny"]),
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
            "numer_ten_sam": sum(x["numer_ten_sam"] for x in r), "bez_wyniku": sum(x["bez_wyniku"] for x in r),
            "przejscia_powod": dict(Counter(f"{x['powod_8']} -> {x['powod_10']}" for x in r)),
        }
    roznice = [x["macierz_roznica_max"] for x in wiersze if x["macierz_roznica_max"] is not None]
    return {"skanow": len(skany), "skanow_ok": len(skany_ok), "par": len(wiersze), "par_ok": len(dobre),
            "par_bez_wyniku": sum(x["bez_wyniku"] for x in wiersze),
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
            "bez_wyniku": sum(klasa(w) == "brak_wyniku" for w in zgodne), "wynikow": sum(klasa(w) != "brak_wyniku" for w in zgodne),
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
    # "0 pewnych zlych" przy samych przebiegach bez wyniku nie jest spelnieniem: potrzebny co najmniej 1 wynik przy polu 100
    wynikow_100 = sum(p["wynikow"] for pole, p in per_pole.items() if float(pole) == 100.0)
    return {"per_pole": per_pole, "zly_pewny_zgodne": zly_pewny, "zly_pewny_niezgodne_10": zly_pewny_niezg, "wynikow_pole_100": wynikow_100,
            "zly_pewny_niezgodne_8": sum(p["niezgodne_8"]["zly_pewny"] for p in per_pole.values()),
            "pelny_zestaw": None if uklady is None else all(p["pelny_zestaw"] for p in per_pole.values()) and bool(per_pole),
            "spelnione": bool(per_pole) and zly_pewny == 0 and wynikow_100 > 0 and (uklady is None or all(p["pelny_zestaw"] for p in per_pole.values()))}


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


def _wariant_pola(w: dict) -> str:
    return f"{w['pole']:g}" + (" bez scianki" if w.get("bez_scianki") else "")


def ocen_g(wpisy: list[dict]) -> dict:
    """Granice rozpoznania (OGRANICZENIE, poza bramka) - bez pola ``spelnione``: wynik nie zmienia kodu wyjscia."""
    # (a) plytki okragle testowe: pary 8 / 10 kandydatow na tym samym skanie
    pary: dict[str, dict] = {}
    for w in wpisy:
        if w["czesc"] == "testowa":
            pary.setdefault(w["skan"], {})[w["kandydatow_zestaw"]] = w
    wiersze = []
    for skan, p in sorted(pary.items()):
        if 8 not in p or 10 not in p:
            continue
        a, b = p[8], p[10]
        k8, k10 = klasa(a), klasa(b)
        wiersze.append({"skan": skan, "prawda": a["prawda"], "zaslona": a["zaslona"], "pole": _wariant_pola(a), "klasa_8": k8, "klasa_10": k10,
                        "wybrany_8": a["wybrany"], "wybrany_10": b["wybrany"], "powod_8": a["powod"], "powod_10": b["powod"],
                        "pogorszenie": k8 == "dobry_pewny" and k10.startswith("zly"),
                        "gorzej_inaczej": k8 == "dobry_pewny" and k10 in ("dobry_niepewny", "brak_wyniku")})

    def licz_pary(r: list[dict]) -> dict:
        return {"par": len(r), "pogorszenie": sum(x["pogorszenie"] for x in r), "gorzej_inaczej": sum(x["gorzej_inaczej"] for x in r),
                "dobry_pewny_8": sum(x["klasa_8"] == "dobry_pewny" for x in r), "dobry_pewny_10": sum(x["klasa_10"] == "dobry_pewny" for x in r),
                "zly_pewny_8": sum(x["klasa_8"] == "zly_pewny" for x in r), "zly_pewny_10": sum(x["klasa_10"] == "zly_pewny" for x in r),
                "bez_wyniku_8": sum(x["klasa_8"] == "brak_wyniku" for x in r), "bez_wyniku_10": sum(x["klasa_10"] == "brak_wyniku" for x in r),
                "wynik_10": dict(Counter(f"{x['wybrany_10']} ({x['powod_10']})" for x in r))}

    kolejnosc_pol = [f"{p:g}" + (" bez scianki" if b else "") for p, b in POLA_GRANIC]
    pola = [p for p in kolejnosc_pol if any(x["pole"] == p for x in wiersze)] + sorted({x["pole"] for x in wiersze} - set(kolejnosc_pol))
    zaslony = [z for z in ("brak", "D", "ABCD") if any(x["zaslona"] == z for x in wiersze)] + sorted({x["zaslona"] for x in wiersze} - {"brak", "D", "ABCD"})
    graniczne = [x for x in wiersze if x["zaslona"] != "brak" and x["pole"] != "100"]  # dolek zasloniety i brak scianki bocznej w skanie
    testowe = {**licz_pary(wiersze),
               "zaslona_i_brak_scianki": licz_pary(graniczne),
               "reszta": licz_pary([x for x in wiersze if x not in graniczne]),
               "per_zaslona_pole": {f"{z}/{p}": licz_pary([x for x in wiersze if x["zaslona"] == z and x["pole"] == p]) for z in zaslony for p in pola},
               "pogorszone": [x for x in wiersze if x["pogorszenie"]]}
    # (b) plytki ramkowe z 4 dolkami zaslonietymi, 10 kandydatow
    ram = [w for w in wpisy if w["czesc"] == "ramkowa" and w["kandydatow_zestaw"] == 10]

    def kwadrat_pewny(w: dict) -> bool:
        return not w.get("blad") and bool(w["pewny"]) and w["wybrany"] == w["prawda"].replace("okragla_ramkowa_", "")

    def licz_ramkowe(r: list[dict]) -> dict:
        return {"przebiegow": len(r), "kwadrat_pewny": sum(kwadrat_pewny(w) for w in r), **{k: sum(klasa(w) == k for w in r) for k in KLASY},
                "wynik": dict(Counter(f"{w['wybrany']} pewny={w['pewny']} {w['powod']} nr {w.get('numer')} ({w.get('numer_zrodlo')})" for w in r))}

    pola_r = [p for p in kolejnosc_pol if any(_wariant_pola(w) == p for w in ram)]
    ramkowe = {**licz_ramkowe(ram),
               "per_pole_tryb": {f"{p}/{t}": licz_ramkowe([w for w in ram if _wariant_pola(w) == p and w["tryb"] == t]) for p in pola_r for t in ("bez_numeru", "z_numerem")},
               "kwadrat_pewny_lista": [{k: w.get(k) for k in ("skan", "tryb", "wybrany", "pewny", "powod", "numer", "numer_zrodlo", "numer_z_dolkow")} for w in ram if kwadrat_pewny(w)]}
    # (c) kontrola: kwadraty R59
    kw = [w for w in wpisy if w["czesc"] == "kwadrat" and w["kandydatow_zestaw"] == 10]
    kwadraty = {"przebiegow": len(kw), **{k: sum(klasa(w) == k for w in kw) for k in KLASY},
                "per_pole": {p: {"przebiegow": sum(_wariant_pola(w) == p for w in kw), "dobry_pewny": sum(_wariant_pola(w) == p and klasa(w) == "dobry_pewny" for w in kw)}
                             for p in kolejnosc_pol if any(_wariant_pola(w) == p for w in kw)},
                "powody": dict(Counter(str(w["powod"]) for w in kw))}
    return {"testowe": testowe, "ramkowe": ramkowe, "kwadraty": kwadraty}


def zadania_granice(ziarna: int) -> list[tuple]:
    """Zestaw kryterium g: (czesc, uklad, numer, ziarno, pole, zaslona - lista bitow, bez scianki, [(tryb, numer podany, zestaw)])."""
    wszystkie = ["A", "B", "C", "D"]
    z = []
    for n, nr in TESTOWE_GRANIC:
        for i in range(ziarna):
            for bity in ([], ["D"], wszystkie):
                for pole, bez in POLA_GRANIC:
                    z.append(("testowa", n, nr, 7000 + nr * 10 + i, pole, bity, bez, [("bez_numeru", None, 8), ("bez_numeru", None, 10)]))
    for n, nr in RAMKOWE_GRANIC:
        for pole, bez in POLA_GRANIC:
            if pole != 97.0:
                z.append(("ramkowa", n, nr, 7100 + nr, pole, wszystkie, bez, [("bez_numeru", None, 10), ("z_numerem", nr, 10)]))
    for n, nr in KWADRATY_GRANIC:
        for pole, bez in POLA_GRANIC:
            z.append(("kwadrat", n, nr, 7200 + nr, pole, [], bez, [("bez_numeru", None, 10)]))
    return z


def nazwa_skanu_granic(n: str, nr: int, seed: int, pole: float, bity: list[str], bez: bool) -> str:
    return f"syn_{n}_n{nr}_s{seed}_p{pole:g}" + ("_zasl" + "".join(bity) if bity else "") + ("_bezscianki" if bez else "")


OCENY = {"2": ocen_k2, "3": ocen_k3, "4": ocen_k4, "6": ocen_k6, "z": ocen_z, "g": ocen_g}


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
                  f"(pary {o['par_ok']} z {o['par']}; pary bez wyniku przy 8 albo 10 kand. sa zle: bez wyniku {o['par_bez_wyniku']} z {o['par']}; "
                  f"najwieksza roznica macierzy {o['macierz_roznica_max']}) -> {tn(o['spelnione'])}"]
        for tryb, p in o["per_tryb"].items():
            L.append(f"  {tryb:11s} par {p['par']}: ten sam uklad {p['ten_sam_uklad']}, pewnosc nie gorsza {p['pewnosc_nie_gorsza']}, pewny 8/10 kand. {p['pewny_8']}/{p['pewny_10']}, "
                     f"zgodny z prawda 8/10 kand. {p['zgodny_z_prawda_8']}/{p['zgodny_z_prawda_10']}, numer i zrodlo te same {p['numer_ten_sam']}, pary bez wyniku {p['bez_wyniku']}")
            L += [f"      powod {a}: {n}" for a, n in sorted(p["przejscia_powod"].items())]
        L += [f"  ZLE {z['skan']} [{z['tryb']}] prawda {z['prawda']}: 8 -> {z['wybrany_8']} pewny={z['pewny_8']} {z['powod_8']}; 10 -> {z['wybrany_10']} pewny={z['pewny_10']} {z['powod_10']}"
              for z in o["zle"]]
    if "4" in k:
        o = k["4"]
        L += ["", f"KRYTERIUM 4 (BRAMKA; 10 kandydatow, kazdy uklad i numer, numer zgodny albo brak): pewny ze zlym ukladem {o['zly_pewny_zgodne']} -> {tn(o['spelnione'])}"
                  + ("" if o["pelny_zestaw"] in (True, None) else " (zestaw niepelny)")
                  + ("" if o["wynikow_pole_100"] else " (brak wyniku przy polu 100 - bramki nie da sie orzec)"),
              "  " + ", ".join(f"pole {float(pole):g}: bez wyniku {p['bez_wyniku']} z {p['zgodne']['przebiegow']}" for pole, p in o["per_pole"].items()),
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
    if "g" in k:
        o = k["g"]
        t, r, kw = o["testowe"], o["ramkowe"], o["kwadraty"]
        g = t["zaslona_i_brak_scianki"]
        L += ["", "OGRANICZENIE (poza bramka) - granice rozpoznania: plytka okragla bez waznego numeru z dolkow, bez scianki bocznej w skanie",
              f"  plytki okragle testowe R59 n8 / n9 (8 vs 10 kandydatow, bez numeru podanego): pogorszenie wobec 8 kandydatow: {t['pogorszenie']} z {t['par']} par "
              f"(8: dobry i pewny -> 10: zly); pewny zly przy 10: {t['zly_pewny_10']} z {t['par']} (przy 8: {t['zly_pewny_8']} z {t['par']}); "
              f"8: dobry i pewny -> 10: niepewny albo bez wyniku: {t['gorzej_inaczej']}",
              f"    w tym dolek zasloniety i brak scianki w skanie (pola 99 / 98 / 97, pole 100 bez scianki): pogorszenie {g['pogorszenie']} z {g['par']} par, "
              f"pewny zly przy 10: {g['zly_pewny_10']} z {g['par']} (przy 8: {g['zly_pewny_8']}); pozostale przypadki: pogorszenie {t['reszta']['pogorszenie']} z {t['reszta']['par']}, "
              f"pewny zly przy 10: {t['reszta']['zly_pewny_10']} z {t['reszta']['par']}",
              "    zaslona/pole          par  8:dobry_pewny  10:dobry_pewny  8:zly_pewny  10:zly_pewny  pogorszenie  bez wyniku 8/10  wynik przy 10"]
        for nazwa, p in t["per_zaslona_pole"].items():
            L.append(f"    {nazwa:20s} {p['par']:>4d} {p['dobry_pewny_8']:>14d} {p['dobry_pewny_10']:>15d} {p['zly_pewny_8']:>12d} {p['zly_pewny_10']:>13d} {p['pogorszenie']:>12d} "
                     f"{str(p['bez_wyniku_8']) + '/' + str(p['bez_wyniku_10']):>16s}  {p['wynik_10']}")
        L.append(f"  plytki ramkowe n1, n2, n4, n5, 4 dolki zasloniete (10 kandydatow): jako kwadrat, pewny: {r['kwadrat_pewny']} z {r['przebiegow']} przebiegow; "
                 f"dobry_pewny {r['dobry_pewny']}, dobry_niepewny {r['dobry_niepewny']}, zly_niepewny {r['zly_niepewny']}, zly_pewny {r['zly_pewny']}, bez wyniku {r['brak_wyniku']}")
        for nazwa, p in r["per_pole_tryb"].items():
            L.append(f"    {nazwa:28s} przebiegow {p['przebiegow']}: kwadrat pewny {p['kwadrat_pewny']}, dobry_pewny {p['dobry_pewny']}; {p['wynik']}")
        L.append(f"  kontrola - kwadraty R59 n2 / n5 (10 kandydatow, bez numeru): dobry_pewny {kw['dobry_pewny']} z {kw['przebiegow']}; zly_pewny {kw['zly_pewny']}, niepewnych "
                 f"{kw['dobry_niepewny'] + kw['zly_niepewny']}, bez wyniku {kw['brak_wyniku']}; powody {kw['powody']}; per pole "
                 + ", ".join(f"{pole}: {x['dobry_pewny']} z {x['przebiegow']}" for pole, x in kw["per_pole"].items()))
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
            self.wpisy = self.wczytaj([plik])
        elif plik.exists():
            plik.unlink()
        self.klucze = {self.klucz(w) for w in self.wpisy}

    @staticmethod
    def wczytaj(pliki: list[Path]) -> list[dict]:
        return [bez_sciezek_w_wpisie(json.loads(w)) for p in pliki for w in Path(p).read_text(encoding="utf-8").split("\n") if w.strip()]

    @classmethod
    def z_plikow(cls, pliki: list[Path]) -> "Dziennik":
        """Dziennik tylko do oceny (``--z-przebiegow``): wpisy z podanych plikow, nic nie jest zapisywane ani kasowane."""
        dz = cls.__new__(cls)
        dz.plik, dz.wpisy = None, cls.wczytaj(pliki)
        dz.klucze = {cls.klucz(w) for w in dz.wpisy}
        return dz

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
    if a.z_przebiegow:  # sama ocena zapisanych przebiegow - nic nie jest mierzone
        dz, mierzone, korony = Dziennik.z_plikow(a.z_przebiegow), (), []
    else:
        dz, mierzone = Dziennik(a.wyjscie / "przebiegi.jsonl", a.wznow), a.kryteria
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
    if "2" in mierzone:
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
    if "3" in mierzone:
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
    if "4" in mierzone:
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
    if "6" in mierzone:
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
    if "z" in mierzone:
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

    # --- granice rozpoznania (OGRANICZENIE, poza bramka) ---
    if "g" in mierzone:
        zadania = zadania_granice(a.ziarna_g)
        for czesc, n, nr, seed, pole, bity, bez, lista in zadania[: a.limit] if a.limit else zadania:
            nazwa = nazwa_skanu_granic(n, nr, seed, pole, bity, bez)
            if all(dz.jest(kryterium="g", skan=nazwa, tryb=t, numer_podany=p, kandydatow_zestaw=z) for t, p, z in lista):
                continue
            skan, prawda = skan_syntetyczny(wg_nazwy[n], nr, korony, seed, pole, ust, zaslon=bity or None, bez_scianki=bez)
            for tryb, podany, zestaw in lista:
                w = uruchom("g", nazwa, skan, prawda, tryb, podany, zestaw, seed=seed, czesc=czesc, zaslona="".join(bity) or "brak", bez_scianki=bez)
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
        "parametry": {"kryteria": list(a.kryteria), "pola": list(a.pola), "ziarna_k2": a.ziarna_k2, "ziarna_k4": a.ziarna_k4, "pomiary_k6": a.pomiary_k6, "ziarna_g": a.ziarna_g,
                      "z_przebiegow": {"plikow": len(a.z_przebiegow), "wpisow": len(dz.wpisy)} if a.z_przebiegow else None,
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
    ap.add_argument("--kryteria", type=_lista_kryteriow, default=DOMYSLNE, help="ktore kryteria mierzyc: 2,3,4,6,g,z (domyslnie 2,3,4,6,g; g = granice rozpoznania, poza bramka)")
    ap.add_argument("--ustawienia", type=Path, default=None, help="plik ustawien z [plytki] (domyslnie ustawienia.przyklad.toml programu)")
    ap.add_argument("--pola", type=_lista_pol, default=(100.0, 90.0, 80.0), help="kryterium 4: srednice pola skanu w mm (domyslnie 100,90,80)")
    ap.add_argument("--ziarna-k2", type=int, default=4, help="kryterium 2: ziaren na numer (domyslnie 4)")
    ap.add_argument("--ziarna-k4", type=int, default=2, help="kryterium 4: ziaren na numer i pole (domyslnie 2)")
    ap.add_argument("--pomiary-k6", type=int, default=10, help="kryterium 6: liczba skanow R59 (domyslnie 10)")
    ap.add_argument("--ziarna-g", type=int, default=3, help="granice (g): ziaren na przypadek plytki okraglej testowej (domyslnie 3)")
    ap.add_argument("--z-przebiegow", type=Path, nargs="+", default=None, metavar="PLIK",
                    help="nie mierz: ocen wpisy z podanych plikow przebiegi.jsonl (wynik do --wyjscie)")
    ap.add_argument("--limit", type=int, default=0, help="proba: najwyzej tyle skanow na kryterium / folder (0 = wszystkie)")
    ap.add_argument("--wznow", action="store_true", help="nie kasuj przebiegi.jsonl - pomin przebiegi juz zapisane")
    ap.add_argument("--uwaga", default="", help="tekst do wyniku, np. co jeszcze liczylo w czasie pomiaru")
    return ap


def main(argv: list[str] | None = None) -> int:
    a = parser().parse_args(argv)
    if min(a.ziarna_k2, a.ziarna_k4, a.pomiary_k6, a.ziarna_g) < 1 or a.limit < 0:
        parser().error("--ziarna-k2, --ziarna-k4, --pomiary-k6, --ziarna-g musza byc >= 1, --limit >= 0")
    if a.z_przebiegow and any(not Path(p).is_file() for p in a.z_przebiegow):
        parser().error("--z-przebiegow: nie ma pliku " + ", ".join(Path(p).name for p in a.z_przebiegow if not Path(p).is_file()))
    wynik = przebieg(a)
    return 0 if all(o.get("spelnione", True) for o in wynik["kryteria"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
