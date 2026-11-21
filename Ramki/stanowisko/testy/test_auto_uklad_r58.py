"""Rozpoznanie ukladu plytki przy 10 ukladach wbudowanych (8 dotychczasowych + 2 okragle ramkowe R58) - paczka E3-O1.

``plate.py`` nie jest zmieniany: kandydatami rozpoznania sa wszystkie uklady z ``[plytki]``, wiec po dodaniu ukladow
``okragla_ramkowa_*`` rodzina R59 ma 3 kandydatow (kwadrat, okragla testowa n8 / n9, okragla ramkowa n1-n6) zamiast 2.
Testy pokazuja, co z tego wynika: plytka ramkowa jest rozpoznawana po numerze z dolkow kodu, kwadrat R59 z numerem
podanym - po ksztalcie brzegu (dawniej: po numerze podanym), rodzina R54 - bez zmian. Liczniki na zestawach:
``narzedzia/auto_uklad_r58.py`` (kryteria 2, 3, 4, 6 paczki), raport ``raporty/E3-O1_2026-11-21.md``.
"""
from __future__ import annotations

import json
import warnings
from collections import Counter

import numpy as np
import pytest

import auto_uklad_r58 as AR
from stanowisko import plate, porownaj as PO, synth, uklad as U, ustawienia as UST

DOTYCHCZASOWE = ("wieczorna", "poranna", "okragla_wieczorna", "okragla_poranna",
                 "wieczorna_r54", "poranna_r54", "okragla_wieczorna_r54", "okragla_poranna_r54")
RAMKOWE = ("okragla_ramkowa_wieczorna", "okragla_ramkowa_poranna")
WSZYSTKIE = DOTYCHCZASOWE + RAMKOWE
RODZINY = {  # uklady o tym samym rozstawie stozkow znacznikow
    "wieczorna": {"wieczorna", "okragla_wieczorna", "okragla_ramkowa_wieczorna"},
    "poranna": {"poranna", "okragla_poranna", "okragla_ramkowa_poranna"},
    "wieczorna_r54": {"wieczorna_r54", "okragla_wieczorna_r54"},
    "poranna_r54": {"poranna_r54", "okragla_poranna_r54"},
}


def rodzina(nazwa: str) -> set[str]:
    return next(r for r in RODZINY.values() if nazwa in r)


@pytest.fixture(scope="module")
def ust():
    return UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU)


@pytest.fixture(scope="module")
def kandydaci(ust):
    """(10 kandydatow, 8 kandydatow) - dokladnie tak, jak bierze je program: wszystkie uklady z ``[plytki]``."""
    return AR.uklady_kandydaci(ust)


@pytest.fixture(scope="module")
def skany(korony, kandydaci, ust):
    """Po jednym skanie (3 atrapy, pole fi 100, losowa poza) dla kazdego z 10 ukladow; numer = pierwszy numer ukladu."""
    wg_nazwy = {u.nazwa: u for u in kandydaci[0]}
    return {n: (wg_nazwy[n], *AR.skan_syntetyczny(wg_nazwy[n], wg_nazwy[n].numery[0], korony, 580 + i, 100.0, ust)) for i, n in enumerate(WSZYSTKIE)}


@pytest.fixture(scope="module")
def rozpoznane(skany, kandydaci):
    """Rozpoznanie bez numeru na 10 kandydatach (pierwsze uruchomienie okna), z cieciem na gniazda."""
    wynik = {}
    for nazwa, (_, skan, _) in skany.items():
        with warnings.catch_warnings(record=True) as ostrz:
            warnings.simplefilter("always")
            wyr, info = plate.rozpoznaj_uklad(skan, kandydaci[0])
        wynik[nazwa] = (wyr, info, [str(o.message) for o in ostrz])
    return wynik


def _auto(skan, uklady, numer=None):
    with warnings.catch_warnings(record=True) as ostrz:
        warnings.simplefilter("always")
        wyr, info = plate.rozpoznaj_uklad(skan, uklady, numer=numer, ciecie=False)
    return wyr, info, [str(o.message) for o in ostrz]


# --- kandydaci ---------------------------------------------------------------------------------------
def test_kandydaci_to_wszystkie_uklady_wbudowane(kandydaci):
    k10, k8 = kandydaci
    assert [u.nazwa for u in k10] == list(WSZYSTKIE) == list(UST.UKLADY_WBUDOWANE)
    assert [u.nazwa for u in k8] == list(DOTYCHCZASOWE)


# --- (d) rozpoznanie na 10 ukladach ------------------------------------------------------------------
@pytest.mark.parametrize("nazwa", WSZYSTKIE)
def test_rozpoznaje_kazdy_z_dziesieciu_ukladow_bez_numeru(rozpoznane, skany, nazwa):
    wyr, info, _ = rozpoznane[nazwa]
    _, _, prawda = skany[nazwa]
    assert wyr.plytka == nazwa == info["wybrany"], info
    assert info["pewny"] is True, info
    assert wyr.jakosc["uklad_zgodny"] is True
    assert {f.gniazdo for f in wyr.fragmenty if f.status == "praca"} == {p.gniazdo for p in prawda.prace}
    wpisy = {k["uklad"]: k for k in info["kandydaci"]}
    assert set(wpisy) == set(WSZYSTKIE)
    assert {n for n, k in wpisy.items() if k["stozki_pasuja"]} == rodzina(nazwa)
    assert all(wpisy[n]["odrzucony"] == "stozki" for n in set(WSZYSTKIE) - rodzina(nazwa))


@pytest.mark.parametrize("nazwa", RAMKOWE)
def test_plytka_ramkowa_ma_numer_z_dolkow_i_po_nim_jest_rozpoznana(rozpoznane, skany, nazwa):
    wyr, info, _ = rozpoznane[nazwa]
    uk, _, prawda = skany[nazwa]
    assert info["powod"] == "numer_z_dolkow" and wyr.numer_zrodlo == "dolki" and wyr.numer == prawda.numer == uk.numery[0]
    wpisy = {k["uklad"]: k for k in info["kandydaci"]}
    testowa = nazwa.replace("_ramkowa", "")
    assert wpisy[nazwa]["numer_z_dolkow_wazny"] is True
    # okragla testowa ma te same dolki: czyta ten sam numer, ale nie jest to numer jej plytki (n8 / n9)
    assert wpisy[testowa]["numer_z_dolkow"] == prawda.numer and wpisy[testowa]["numer_z_dolkow_wazny"] is False
    # rowek pokrywki na obwodzie: model ramkowy wyjasnia brzeg skanu, model testowy nie
    assert wpisy[nazwa]["ksztalt_niewyjasnione_mm2"] + plate.PROG_KSZTALTU_MM2 <= wpisy[testowa]["ksztalt_niewyjasnione_mm2"]


@pytest.mark.parametrize("nazwa", RAMKOWE)
def test_wynik_ramkowej_jak_przy_ukladzie_wybranym_recznie(rozpoznane, skany, nazwa):
    wyr, _, _ = rozpoznane[nazwa]
    uk, skan, _ = skany[nazwa]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        reczny = plate.wyrownaj(skan, uk)
    assert np.allclose(wyr.macierz, reczny.macierz, rtol=0.0, atol=1e-9)
    assert (wyr.numer, wyr.numer_zrodlo, wyr.bity) == (reczny.numer, reczny.numer_zrodlo, reczny.bity)
    assert [(f.gniazdo, f.status, f.liczba) for f in wyr.fragmenty] == [(f.gniazdo, f.status, f.liczba) for f in reczny.fragmenty]


@pytest.mark.parametrize("nazwa", RAMKOWE)
def test_ramkowa_z_numerem_podanym_zgodnym(skany, kandydaci, nazwa):
    """Numer z ramki (magnesy) zgodny z dolkami: uklad ramkowy, pewnie; numer ma zrodlo ``podany``."""
    uk, skan, prawda = skany[nazwa]
    wyr, info, _ = _auto(skan, kandydaci[0], numer=prawda.numer)
    assert wyr.plytka == nazwa and info["pewny"] is True and info["powod"] == "numer_z_dolkow"
    assert (wyr.numer, wyr.numer_zrodlo, wyr.numer_z_dolkow) == (prawda.numer, "podany", prawda.numer)


@pytest.mark.parametrize("nazwa", ["wieczorna", "poranna"])
def test_kwadrat_r59_z_numerem_podanym_rozstrzyga_ksztalt(skany, kandydaci, nazwa):
    """ZMIANA wobec 8 ukladow: numer n1-n6 pasuje teraz do kwadratu i do okraglej ramkowej, wiec nie rozstrzyga -
    kwadrat R59 jest rozpoznawany po ksztalcie brzegu (nadal pewnie). Przy 8 kandydatach powod to ``numer_podany``."""
    uk, skan, prawda = skany[nazwa]
    wyr10, info10, _ = _auto(skan, kandydaci[0], numer=prawda.numer)
    wyr8, info8, _ = _auto(skan, kandydaci[1], numer=prawda.numer)
    assert wyr10.plytka == wyr8.plytka == nazwa
    assert (info8["pewny"], info8["powod"]) == (True, "numer_podany")
    assert (info10["pewny"], info10["powod"]) == (True, "ksztalt")
    assert (wyr10.numer, wyr10.numer_zrodlo) == (wyr8.numer, wyr8.numer_zrodlo) == (prawda.numer, "podany")
    assert np.allclose(wyr10.macierz, wyr8.macierz, rtol=0.0, atol=1e-9)


@pytest.mark.parametrize("nazwa", ["wieczorna_r54", "poranna_r54"])
def test_kwadrat_r54_z_numerem_podanym_bez_zmian(skany, kandydaci, nazwa):
    """Rodzina R54 nie ma ukladu ramkowego: numer podany rozstrzyga jak dotad."""
    _, skan, prawda = skany[nazwa]
    for uklady in kandydaci:
        wyr, info, _ = _auto(skan, uklady, numer=prawda.numer)
        assert wyr.plytka == nazwa and (info["pewny"], info["powod"]) == (True, "numer_podany")


@pytest.mark.parametrize("nazwa", ["okragla_wieczorna", "okragla_poranna"])
def test_okragla_testowa_bez_zmian(rozpoznane, skany, kandydaci, nazwa):
    """Plytki testowe n8 / n9: ten sam uklad, powod i numer przy 8 i przy 10 kandydatach."""
    _, skan, prawda = skany[nazwa]
    wyr10, info10, _ = rozpoznane[nazwa]
    wyr8, info8, _ = _auto(skan, kandydaci[1])
    assert info10["wybrany"] == info8["wybrany"] == nazwa
    assert (info10["pewny"], info10["powod"]) == (info8["pewny"], info8["powod"]) == (True, "numer_z_dolkow")
    assert (wyr10.numer, wyr10.numer_zrodlo) == (wyr8.numer, wyr8.numer_zrodlo) == (prawda.numer, "dolki")
    ramkowa = next(k for k in info10["kandydaci"] if k["uklad"] == nazwa.replace("okragla_", "okragla_ramkowa_"))
    assert ramkowa["numer_z_dolkow"] == prawda.numer and ramkowa["numer_z_dolkow_wazny"] is False


# --- numer podany NIEZGODNY z plytka (dane dla paczki O2, luka L4 planu) ----------------------------
def test_ramkowa_numer_podany_inny_niz_dolki_ten_sam_uklad(skany, kandydaci):
    """Ramkowa n1 z podanym 2: uklad dobry i pewny (dolki daja wazny numer), ale numerem wyniku jest numer PODANY (2),
    a numer z dolkow (1) zostaje tylko w polu ``numer_z_dolkow`` i w ostrzezeniu - program ich dzis nie konfrontuje."""
    _, skan, prawda = skany["okragla_ramkowa_wieczorna"]
    assert prawda.numer == 1
    wyr, info, ostrz = _auto(skan, kandydaci[0], numer=2)
    assert wyr.plytka == "okragla_ramkowa_wieczorna" and (info["pewny"], info["powod"]) == (True, "numer_z_dolkow")
    assert (wyr.numer, wyr.numer_zrodlo, wyr.numer_z_dolkow) == (2, "podany", 1)
    assert any("podany 2" in o and "odczytano 1" in o for o in ostrz)


def test_ramkowa_numer_podany_z_drugiej_pory_jest_pomijany(skany, kandydaci):
    """Ramkowa wieczorna n1 z podanym 4 (numer plytki porannej): stozki wybieraja rodzine wieczorna, numer 4 idzie do kosza
    z ostrzezeniem, numerem wyniku jest numer z dolkow."""
    _, skan, _ = skany["okragla_ramkowa_wieczorna"]
    wyr, info, ostrz = _auto(skan, kandydaci[0], numer=4)
    assert wyr.plytka == "okragla_ramkowa_wieczorna" and (info["pewny"], info["powod"]) == (True, "numer_z_dolkow")
    assert (wyr.numer, wyr.numer_zrodlo) == (1, "dolki")
    assert any("nie nale" in o for o in ostrz)


def test_kwadrat_numer_podany_inny_numer_tej_samej_rodziny(skany, kandydaci):
    """Kwadrat n1 z podanym 2: kwadrat nie ma dolkow w polu skanu, wiec numer podany jest przyjmowany bez sprawdzenia."""
    _, skan, prawda = skany["wieczorna"]
    assert prawda.numer == 1
    wyr, info, _ = _auto(skan, kandydaci[0], numer=2)
    assert wyr.plytka == "wieczorna" and (info["pewny"], info["powod"]) == (True, "ksztalt")
    assert (wyr.numer, wyr.numer_zrodlo, wyr.numer_z_dolkow) == (2, "podany", None)


# --- pole skanu mniejsze niz plytka (runda 2, uwaga 2 recenzji) --------------------------------------
# Ziarna 9300 + numer: przy polu 96 / 94 mm kazdy z tych skanow ma 3 stozki w polu (jest wynik), przy 90 / 80 - nie ma.
MALE_POLE = [("okragla_ramkowa_wieczorna", 2), ("wieczorna", 1), ("okragla_wieczorna", 8), ("okragla_ramkowa_poranna", 5), ("poranna", 4)]


@pytest.mark.parametrize("nazwa, nr, pole", [(n, nr, pole) for (n, nr), pole in zip(MALE_POLE, (96.0, 96.0, 96.0, 94.0, 94.0))])
def test_male_pole_96_i_94_uklad_dobry_i_pewny(korony, kandydaci, ust, nazwa, nr, pole):
    """Pole 96 / 94 mm: brzeg plytki uciety, 3 stozki w polu - JEST wynik i ma byc dobry i pewny (kryterium 4 w pytest).
    Test pada, gdy wybor ukladu w ``plate.py`` jest zepsuty (wstrzykniecie W10 recenzenta)."""
    uk = next(u for u in kandydaci[0] if u.nazwa == nazwa)
    skan, prawda = AR.skan_syntetyczny(uk, nr, korony, 9300 + nr, pole, ust)
    for numer in (None, prawda.numer):
        w = AR.rozpoznaj(skan, kandydaci[0], numer)
        w["prawda"] = nazwa
        assert AR.klasa(w) == "dobry_pewny", {k: v for k, v in w.items() if not k.startswith("_")}


@pytest.mark.parametrize("nazwa, nr, pole", [(n, nr, pole) for (n, nr), pole in zip(MALE_POLE, (90.0, 90.0, 90.0, 80.0, 80.0))])
def test_male_pole_90_i_80_brak_wyniku_blad_wyrownania(korony, kandydaci, ust, nazwa, nr, pole):
    """Pole 90 / 80 mm nie obejmuje 3 stozkow znacznikow: program NIE daje zadnego wyniku (``BladWyrownania``) - przy 10
    i przy 8 kandydatach. To jest zachowanie do utrwalenia: "0 pewnych zlych" przy tych polach znaczy "0 wynikow"."""
    uk = next(u for u in kandydaci[0] if u.nazwa == nazwa)
    skan, prawda = AR.skan_syntetyczny(uk, nr, korony, 9300 + nr, pole, ust)
    for uklady in kandydaci:
        for numer in (None, prawda.numer):
            w = AR.rozpoznaj(skan, uklady, numer)
            w["prawda"] = nazwa
            assert AR.klasa(w) == "brak_wyniku" and w["wybrany"] is None and w["blad"].startswith("BladWyrownania"), w


# --- granice rozpoznania: OGRANICZENIE ZNANE (runda 2, uwaga 1 recenzji PR #51) ----------------------
# Plytka okragla bez waznego numeru z dolkow (dolek zasloniety) i bez scianki bocznej w skanie jest przy 10 kandydatach
# brana za KWADRAT z ``pewny`` = True: dwa najlepsze uklady wg ksztaltu to wtedy okragla testowa i okragla ramkowa (roznia
# sie tylko rowkiem pokrywki na sciance bocznej), ksztalt nie rozstrzyga, a regula ``dolki_wykluczaja`` odrzuca oba kola.
# Koordynator przyjal to domyslnie jako opisane ograniczenie (do decyzji wlasciciela); poprawka = wariant C (zmiana reguly
# ksztaltu w ``plate.py``). Testy ponizej UTRWALAJA zachowanie dzisiejsze - po wariancie C maja zostac ODWROCONE.
# Liczby na zestawie: ``auto_uklad_r58.py --kryteria g``. Ziarna 9508 / 9902 = proby W7 i W9 recenzenta.
@pytest.fixture(scope="module")
def testowa_n8_zasloniety_dolek(korony, kandydaci, ust):
    """Plytka okragla testowa n8 z dolkiem D zaslonietym przedmiotem: ten sam skan przyciety do pola 98 i 100 mm."""
    uk = next(u for u in kandydaci[0] if u.nazwa == "okragla_wieczorna")
    return {pole: AR.skan_syntetyczny(uk, 8, korony, 9508, pole, ust, zaslon=["D"])[0] for pole in (98.0, 100.0)}


def test_ograniczenie_znane_testowa_z_zaslonietym_dolkiem_pole_98_to_pewny_kwadrat_do_odwrocenia_po_wariancie_c(testowa_n8_zasloniety_dolek, kandydaci):
    """OGRANICZENIE ZNANE, decyzja wlasciciela o wariancie C - po zmianie reguly w ``plate.py`` ten test ma zostac odwrocony.
    Pole 98 mm (scianki bocznej nie ma w skanie): przy 10 kandydatach KWADRAT, ``pewny`` = True, ``dolki_wykluczaja``;
    ta sama siatka przy 8 kandydatach (stan sprzed paczki E3-O1) - uklad dobry i pewny. To jest pogorszenie wprowadzone paczka."""
    skan = testowa_n8_zasloniety_dolek[98.0]
    wyr10, info10, _ = _auto(skan, kandydaci[0])
    assert (info10["wybrany"], info10["pewny"], info10["powod"]) == ("wieczorna", True, "dolki_wykluczaja")
    assert (wyr10.numer, wyr10.numer_zrodlo) == (None, "nieznany")
    wpisy = {k["uklad"]: k for k in info10["kandydaci"]}
    # ksztalt mowi "kolo" (kwadrat ma najwiecej niewyjasnionego brzegu), ale dwa kola roznia sie o mniej niz prog
    assert wpisy["wieczorna"]["ksztalt_niewyjasnione_mm2"] > max(wpisy[n]["ksztalt_niewyjasnione_mm2"] for n in ("okragla_wieczorna", "okragla_ramkowa_wieczorna")) + plate.PROG_KSZTALTU_MM2
    assert abs(wpisy["okragla_wieczorna"]["ksztalt_niewyjasnione_mm2"] - wpisy["okragla_ramkowa_wieczorna"]["ksztalt_niewyjasnione_mm2"]) < plate.PROG_KSZTALTU_MM2
    assert wpisy["okragla_wieczorna"]["numer_z_dolkow_wazny"] is False and wpisy["okragla_ramkowa_wieczorna"]["numer_z_dolkow_wazny"] is False
    wyr8, info8, _ = _auto(skan, kandydaci[1])
    assert (info8["wybrany"], info8["pewny"], info8["powod"]) == ("okragla_wieczorna", True, "ksztalt")


def test_testowa_z_zaslonietym_dolkiem_pole_100_ze_scianka_dobrze_i_pewnie(testowa_n8_zasloniety_dolek, kandydaci):
    """Granica ograniczenia: ta sama plytka przy polu 100 mm (scianka boczna w skanie) - dobrze i pewnie przy 10 kandydatach,
    bo rowek pokrywki modelu ramkowego na sciance bocznej daje roznice ksztaltu powyzej progu."""
    wyr, info, _ = _auto(testowa_n8_zasloniety_dolek[100.0], kandydaci[0])
    assert (info["wybrany"], info["pewny"], info["powod"]) == ("okragla_wieczorna", True, "ksztalt")
    wpisy = {k["uklad"]: k for k in info["kandydaci"]}
    assert wpisy["okragla_ramkowa_wieczorna"]["ksztalt_niewyjasnione_mm2"] - wpisy["okragla_wieczorna"]["ksztalt_niewyjasnione_mm2"] >= plate.PROG_KSZTALTU_MM2


def test_ograniczenie_znane_ramkowa_z_zaslonietymi_dolkami_bez_scianki_to_pewny_kwadrat_do_odwrocenia_po_wariancie_c(korony, kandydaci, ust):
    """OGRANICZENIE ZNANE, decyzja wlasciciela o wariancie C - po zmianie reguly w ``plate.py`` ten test ma zostac odwrocony.
    Plytka ramkowa n2, 4 dolki kodu zasloniete, pole 100 mm, skan BEZ scianki bocznej (konstrukcja: "skaner patrzacy z gory"):
    KWADRAT ``wieczorna``, ``pewny`` = True. Bez numeru podanego numer nieznany; z numerem z ramki - numer 2 ze zrodlem
    ``podany``. Gniazda kwadratu i kola sa te same, wiec mapa gniazd jest dobra - zla jest nazwa ukladu."""
    uk = next(u for u in kandydaci[0] if u.nazwa == "okragla_ramkowa_wieczorna")
    skan, prawda = AR.skan_syntetyczny(uk, 2, korony, 9902, 100.0, ust, zaslon=["A", "B", "C", "D"], bez_scianki=True)
    assert (prawda.plytka, prawda.numer, prawda.pole_d) == ("okragla_ramkowa_wieczorna", 2, 100.0)
    wyr, info, _ = _auto(skan, kandydaci[0])
    assert (info["wybrany"], info["pewny"], info["powod"]) == ("wieczorna", True, "dolki_wykluczaja")
    assert (wyr.numer, wyr.numer_zrodlo) == (None, "nieznany")
    wyr, info, _ = _auto(skan, kandydaci[0], numer=2)
    assert (info["wybrany"], info["pewny"], info["powod"]) == ("wieczorna", True, "dolki_wykluczaja")
    assert (wyr.numer, wyr.numer_zrodlo) == (2, "podany")
    kw, ram = next(u for u in kandydaci[0] if u.nazwa == "wieczorna"), uk
    assert kw.sockets == ram.sockets


def test_skan_bez_scianki_bocznej_nie_ma_trojkatow_scianki(korony, kandydaci, ust):
    """Konstrukcja skanu "bez scianki": w ukladzie plytki nie zostaje zaden trojkat ponizej wierzchu o srodku r >= 49 mm."""
    uk = next(u for u in kandydaci[0] if u.nazwa == "okragla_wieczorna")
    op = synth.Opcje.z_toml(ust, poza_uklad=False, plytka=uk.nazwa, prace_na_plytce=3, wspolczynnik=(1.22, 1.22), ubytki_na_prace=(0, 0))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        skan, _ = synth.generuj_plytke(uk, 8, list(korony), np.random.default_rng(1), op, 1)

    def scianka(m):
        c = m.triangles_center
        return int(((np.hypot(c[:, 0], c[:, 1]) >= AR.PROMIEN_SCIANKI) & (c[:, 2] < uk.thickness - 0.05)).sum())

    bez = AR.usun_scianke_boczna(skan, uk)
    assert scianka(skan) > 100 and scianka(bez) == 0 and len(bez.faces) == len(skan.faces) - scianka(skan)


# --- porownaj: caly przebieg z ukladem rozpoznanym automatycznie -------------------------------------
def test_porownaj_auto_rozpoznaje_plytke_ramkowa(skany, korony, ust, tmp_path):
    import shutil

    projekty = tmp_path / "projekty"
    projekty.mkdir()
    for i, p in enumerate(korony):
        shutil.copy(p, projekty / f"2026-11-21_p{i}-{['11', '14', '36'][i]}-crown_cad.stl")
    _, skan, prawda = skany["okragla_ramkowa_poranna"]
    p_stl, _ = synth.zapisz(skan, prawda, tmp_path, "skan_ramkowa_poranna")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wynik = PO.porownaj(p_stl, [projekty], PO.AUTO, ust, None, None, inspekcja=False)
    assert wynik["plytka"] == "okragla_ramkowa_poranna" and wynik["plytka_wybor"] == "auto" and wynik["uklad_zgodny"] is True
    assert wynik["uklad_auto"]["wybrany"] == "okragla_ramkowa_poranna" and wynik["uklad_auto"]["pewny"] is True
    assert wynik["numer"] == prawda.numer and wynik["numer_zrodlo"] == "dolki" and wynik["wspolczynnik"] == 1.0
    assert {g["gniazdo"] for g in wynik["gniazda"]} == {p.gniazdo for p in prawda.prace}


# --- narzedzie pomiarowe -----------------------------------------------------------------------------
def test_narzedzie_help_dziala(capsys):
    with pytest.raises(SystemExit) as koniec:
        AR.main(["--help"])
    assert koniec.value.code == 0
    pomoc = capsys.readouterr().out
    assert "--wyjscie" in pomoc and "--odniesienie" in pomoc and "--kryteria" in pomoc and pomoc.isascii()


def test_narzedzie_numery_niezgodne(kandydaci):
    wg = {u.nazwa: u for u in kandydaci[0]}
    assert AR.numery_niezgodne(wg["okragla_ramkowa_wieczorna"], 1) == [("inny_numer_ukladu", 2), ("numer_drugiej_pory", 4), ("numer_drugiego_ksztaltu", 8)]
    assert AR.numery_niezgodne(wg["poranna"], 5) == [("inny_numer_ukladu", 4), ("numer_drugiej_pory", 2), ("numer_drugiego_ksztaltu", 9)]
    assert AR.numery_niezgodne(wg["okragla_poranna_r54"], 9) == [("numer_drugiej_pory", 8), ("numer_drugiego_ksztaltu", 4)]


def _wpis(**pola) -> dict:
    w = {"kryterium": "4", "skan": "s", "tryb": "bez_numeru", "kandydatow_zestaw": 10, "prawda": "wieczorna", "numer_prawda": 1, "pole": 100.0,
         "seed": 1, "wybrany": "wieczorna", "pewny": True, "powod": "ksztalt", "blad": None, "numer": 1, "numer_zrodlo": "podany", "numer_podany": None}
    w.update(pola)
    return w


def test_narzedzie_ocena_bramki_liczy_pewny_zly_uklad():
    dobre = [_wpis(skan=f"s{i}", seed=i, tryb=t) for i in (1, 2) for t in ("bez_numeru", "z_numerem")]
    o = AR.ocen_k4(dobre, {"wieczorna": [1]}, 2)
    assert o["spelnione"] is True and o["zly_pewny_zgodne"] == 0 and o["per_pole"]["100.0"]["zgodne"]["dobry_pewny"] == 4
    # jeden skan pewny ze zlym ukladem = bramka niespelniona; niepewny zly uklad i brak wyniku jej nie lamia, ale sa liczone
    zly = AR.ocen_k4(dobre + [_wpis(skan="s9", seed=9, wybrany="okragla_ramkowa_wieczorna")], {"wieczorna": [1]}, 2)
    assert zly["spelnione"] is False and zly["zly_pewny_zgodne"] == 1 and zly["per_pole"]["100.0"]["zly_pewny_lista"][0]["skan"] == "s9"
    inne = AR.ocen_k4(dobre + [_wpis(skan="s8", seed=8, wybrany="okragla_wieczorna", pewny=False, powod="domyslny"),
                               _wpis(skan="s7", seed=7, wybrany=None, pewny=False, powod=None, blad="BladWyrownania: x"),
                               _wpis(skan="s6", seed=6, pewny=False, powod="domyslny")], {"wieczorna": [1]}, 2)
    p = inne["per_pole"]["100.0"]
    assert inne["spelnione"] is True and (p["zgodne"]["zly_niepewny"], p["zgodne"]["brak_wyniku"], p["zgodne"]["dobry_niepewny"], p["niepewne"]) == (1, 1, 1, 2)
    assert p["dobry_niepewny_powody"] == {"domyslny": 1}
    # numer niezgodny jest liczony osobno i nie wchodzi do licznika bramki; zestaw niepelny = niespelnione
    niezg = AR.ocen_k4(dobre + [_wpis(skan="s1", tryb="niezgodny:inny_numer_ukladu", numer_podany=2, wybrany="okragla_wieczorna")], {"wieczorna": [1]}, 2)
    assert niezg["spelnione"] is True and niezg["zly_pewny_niezgodne_10"] == 1
    assert AR.ocen_k4(dobre[:2], {"wieczorna": [1]}, 2)["spelnione"] is False


def test_narzedzie_ocena_par_8_i_10_kandydatow():
    def para(skan, tryb, w8, w10):
        return [_wpis(kryterium="3", skan=skan, tryb=tryb, kandydatow_zestaw=8, **w8), _wpis(kryterium="3", skan=skan, tryb=tryb, kandydatow_zestaw=10, **w10)]

    wpisy = para("a", "bez_numeru", {}, {}) + para("a", "z_numerem", {"powod": "numer_podany"}, {"powod": "ksztalt"})
    o = AR.ocen_k3(wpisy)
    assert o["spelnione"] is True and (o["skanow"], o["skanow_ok"], o["par"], o["par_ok"]) == (1, 1, 2, 2)
    assert o["per_tryb"]["z_numerem"]["przejscia_powod"] == {"numer_podany -> ksztalt": 1}
    gorsza = AR.ocen_k3(wpisy + para("b", "bez_numeru", {}, {"pewny": False, "powod": "domyslny"}) + para("b", "z_numerem", {}, {}))
    assert gorsza["spelnione"] is False and gorsza["skanow_ok"] == 1 and gorsza["zle"][0]["skan"] == "b"
    inny = AR.ocen_k3(wpisy + para("c", "bez_numeru", {}, {"wybrany": "okragla_ramkowa_wieczorna"}) + para("c", "z_numerem", {}, {}))
    assert inny["spelnione"] is False and inny["per_tryb"]["bez_numeru"]["ten_sam_uklad"] == 1
    lepsza = AR.ocen_k3(para("d", "bez_numeru", {"pewny": False}, {}) + para("d", "z_numerem", {}, {}))
    assert lepsza["spelnione"] is True  # pewnosc wieksza niz przy 8 kandydatach nie jest pogorszeniem


BRAK = {"wybrany": None, "pewny": False, "powod": None, "blad": "BladWyrownania: znaleziono 1 stozki"}
PUSTA_TABELA = {"data": "d", "kandydaci_10": [], "uwaga": "", "bramka": {"spelniona": None}}


def test_narzedzie_ocena_par_brak_wyniku_to_para_zla():
    """Runda 2, uwaga 3: para dobra tylko, gdy OBA przebiegi maja wynik. Brak wyniku przy 8 i 10 kandydatach naraz (np. zmiana,
    ktora psuje wyrownanie wszystkich skanow) nie moze dac "bramka spelniona"; takie pary sa liczone osobno."""
    def para(skan, tryb, w8, w10):
        return [_wpis(kryterium="3", skan=skan, tryb=tryb, kandydatow_zestaw=8, **w8), _wpis(kryterium="3", skan=skan, tryb=tryb, kandydatow_zestaw=10, **w10)]

    oba = AR.ocen_k3(para("a", "bez_numeru", BRAK, BRAK) + para("a", "z_numerem", BRAK, BRAK))
    assert oba["spelnione"] is False and (oba["skanow"], oba["skanow_ok"], oba["par"], oba["par_ok"], oba["par_bez_wyniku"]) == (1, 0, 2, 0, 2)
    assert oba["per_tryb"]["bez_numeru"]["bez_wyniku"] == 1 and oba["zle"][0]["bez_wyniku"] is True
    dobre = para("b", "bez_numeru", {}, {}) + para("b", "z_numerem", {}, {})
    jeden = AR.ocen_k3(dobre + para("c", "bez_numeru", {}, BRAK) + para("c", "z_numerem", {}, {}))
    assert jeden["spelnione"] is False and (jeden["skanow_ok"], jeden["par_ok"], jeden["par_bez_wyniku"]) == (1, 3, 1)
    tylko_8 = AR.ocen_k3(dobre + para("d", "bez_numeru", BRAK, {}) + para("d", "z_numerem", {}, {}))
    assert tylko_8["spelnione"] is False and tylko_8["par_bez_wyniku"] == 1
    czyste = AR.ocen_k3(dobre)
    assert czyste["spelnione"] is True and czyste["par_bez_wyniku"] == 0
    tekst = AR.tabela({**PUSTA_TABELA, "kryteria": {"3": oba}})
    assert "bez wyniku 2 z 2" in tekst and "NIESPELNIONE" in tekst


def test_narzedzie_ocena_bramki_wymaga_wyniku_przy_polu_100():
    """Runda 2, uwaga 3: pole 100 z samymi ``brak_wyniku`` to nie jest "0 pewnych zlych = spelnione"; wiersz werdyktu podaje
    "bez wyniku N z N" dla kazdego pola."""
    puste = [_wpis(skan=f"s{i}", seed=i, tryb=t, **BRAK) for i in (1, 2) for t in ("bez_numeru", "z_numerem")]
    o = AR.ocen_k4(puste, {"wieczorna": [1]}, 2)
    assert o["spelnione"] is False and o["zly_pewny_zgodne"] == 0 and o["wynikow_pole_100"] == 0
    assert o["per_pole"]["100.0"]["bez_wyniku"] == 4 and o["per_pole"]["100.0"]["zgodne"]["przebiegow"] == 4
    dobre = [_wpis(skan=f"s{i}", seed=i, tryb=t) for i in (1, 2) for t in ("bez_numeru", "z_numerem")]
    male = [_wpis(skan=f"m{i}", seed=i, tryb=t, pole=90.0, **BRAK) for i in (1, 2) for t in ("bez_numeru", "z_numerem")]
    mieszane = AR.ocen_k4(dobre + male, {"wieczorna": [1]}, 2)
    assert mieszane["spelnione"] is True and mieszane["wynikow_pole_100"] == 4 and mieszane["per_pole"]["90.0"]["bez_wyniku"] == 4
    # samo pole 90 (pola 100 nie ma w pomiarze): bramki nie da sie orzec
    assert AR.ocen_k4(male, {"wieczorna": [1]}, 2)["spelnione"] is False
    tekst = AR.tabela({**PUSTA_TABELA, "kryteria": {"4": mieszane}})
    assert "pole 100: bez wyniku 0 z 4" in tekst and "pole 90: bez wyniku 4 z 4" in tekst
    tekst = AR.tabela({**PUSTA_TABELA, "kryteria": {"4": o}})
    assert "pole 100: bez wyniku 4 z 4" in tekst and "NIESPELNIONE" in tekst


def test_narzedzie_ostrzezenia_i_bledy_bez_sciezek(monkeypatch):
    """Runda 2, uwaga 4: tekst ostrzezenia ``plate`` zawiera katalog modelu (na PC wlasciciela - z nazwa konta); do wyniku
    narzedzia idzie bez sciezki."""
    katalog = str(U.KATALOG_MODELI / "okragla_ramkowa_wieczorna")
    tekst = f"numer plytki z dolkow 0 nie ma modelu w {katalog} (sa: [1, 2, 3])"

    def z_bledem(skan, uklady, numer=None, ciecie=False):
        raise plate.BladWyrownania(f"brak pliku {katalog}")

    monkeypatch.setattr(plate, "rozpoznaj_uklad", z_bledem)
    w = AR.rozpoznaj(None, [], None)
    assert w["blad"].startswith("BladWyrownania: brak pliku") and "modele_plytek" not in w["blad"] and str(AR.KORZEN) not in w["blad"]

    def z_wynikiem(skan, uklady, numer=None, ciecie=False):
        warnings.warn(tekst, stacklevel=1)
        wyr = type("W", (), {"numer": None, "numer_zrodlo": "nieznany", "numer_z_dolkow": 0, "bity": []})()
        return wyr, {"wybrany": "wieczorna", "pewny": True, "powod": "ksztalt", "czas_rozpoznania_s": 0.0, "kandydaci": []}

    monkeypatch.setattr(plate, "rozpoznaj_uklad", z_wynikiem)
    w = AR.rozpoznaj(None, [], None)
    assert len(w["ostrzezenia"]) == 1 and w["ostrzezenia"][0].startswith("numer plytki z dolkow 0 nie ma modelu w")
    assert "modele_plytek" not in w["ostrzezenia"][0] and str(AR.KORZEN) not in w["ostrzezenia"][0]
    # wpis wczytany z pliku starszego przebiegu (--z-przebiegow) tez jest czyszczony
    stary = AR.bez_sciezek_w_wpisie({"ostrzezenia": [tekst], "blad": None, "wybrany": "wieczorna"})
    assert "modele_plytek" not in json.dumps(stary) and stary["wybrany"] == "wieczorna"


def test_narzedzie_granice_zestaw_i_ocena_poza_bramka():
    """Runda 2, uwaga 1: czesc "granice" (kryterium g) - zestaw, liczenie "pogorszenie wobec 8 kandydatow" i wiersz
    OGRANICZENIE osobno od wiersza BRAMKA; ocena nie ma pola ``spelnione`` (nie zmienia kodu wyjscia)."""
    z = AR.zadania_granice(3)
    assert Counter(x[0] for x in z) == {"testowa": 90, "ramkowa": 16, "kwadrat": 10}
    assert {(x[4], x[6]) for x in z if x[0] == "testowa"} == {(100.0, False), (99.0, False), (98.0, False), (97.0, False), (100.0, True)}
    assert {tuple(x[5]) for x in z if x[0] == "testowa"} == {(), ("D",), ("A", "B", "C", "D")} and {x[2] for x in z if x[0] == "ramkowa"} == {1, 2, 4, 5}
    assert all({zz for _, _, zz in x[7]} == {8, 10} for x in z if x[0] == "testowa")
    nazwy = [AR.nazwa_skanu_granic(x[1], x[2], x[3], x[4], x[5], x[6]) for x in z]
    assert len(set(nazwy)) == len(nazwy) and "syn_okragla_wieczorna_n8_s7080_p100_zaslD_bezscianki" in nazwy

    def g(skan, zestaw, **pola):
        return _wpis(kryterium="g", skan=skan, kandydatow_zestaw=zestaw, prawda="okragla_wieczorna", numer_prawda=8, czesc="testowa", zaslona="D",
                     **{"wybrany": "okragla_wieczorna", "bez_scianki": False, **pola})

    wpisy = [g("a", 8, pole=98.0), g("a", 10, pole=98.0, wybrany="wieczorna", powod="dolki_wykluczaja"),  # pogorszenie
             g("b", 8, pole=100.0), g("b", 10, pole=100.0),  # bez zmiany
             g("c", 8, pole=97.0, wybrany="wieczorna"), g("c", 10, pole=97.0, wybrany="wieczorna"),  # zle takze przy 8: nie pogorszenie
             g("d", 8, pole=100.0, bez_scianki=True), g("d", 10, pole=100.0, bez_scianki=True, **BRAK)]
    wpisy += [_wpis(kryterium="g", skan="r", tryb=t, numer_podany=p, prawda="okragla_ramkowa_wieczorna", numer_prawda=2, czesc="ramkowa", zaslona="ABCD", bez_scianki=True,
                    wybrany="wieczorna", powod="dolki_wykluczaja", numer=p, numer_zrodlo="podany" if p else "nieznany") for t, p in (("bez_numeru", None), ("z_numerem", 2))]
    wpisy += [_wpis(kryterium="g", skan="r2", prawda="okragla_ramkowa_wieczorna", numer_prawda=2, czesc="ramkowa", zaslona="ABCD", bez_scianki=False, pole=99.0,
                    wybrany="okragla_ramkowa_wieczorna")]
    wpisy += [_wpis(kryterium="g", skan="k", prawda="wieczorna", numer_prawda=2, czesc="kwadrat", zaslona="brak", bez_scianki=False, pole=98.0)]
    o = AR.ocen_g(wpisy)
    t = o["testowe"]
    assert "spelnione" not in o and (t["par"], t["pogorszenie"], t["zly_pewny_10"], t["zly_pewny_8"], t["gorzej_inaczej"]) == (4, 1, 2, 1, 1)
    assert (t["zaslona_i_brak_scianki"]["par"], t["zaslona_i_brak_scianki"]["pogorszenie"]) == (3, 1) and t["reszta"]["pogorszenie"] == 0
    assert t["per_zaslona_pole"]["D/98"]["pogorszenie"] == 1 and t["per_zaslona_pole"]["D/100 bez scianki"]["bez_wyniku_10"] == 1
    assert (o["ramkowe"]["przebiegow"], o["ramkowe"]["kwadrat_pewny"], o["ramkowe"]["dobry_pewny"]) == (3, 2, 1)
    assert o["ramkowe"]["per_pole_tryb"]["100 bez scianki/z_numerem"]["wynik"] == {"wieczorna pewny=True dolki_wykluczaja nr 2 (podany)": 1}
    assert (o["kwadraty"]["przebiegow"], o["kwadraty"]["dobry_pewny"]) == (1, 1)
    tekst = AR.tabela({**PUSTA_TABELA, "kryteria": {"g": o}})
    assert "OGRANICZENIE (poza bramka)" in tekst and "pogorszenie wobec 8 kandydatow: 1 z 4 par" in tekst and "pewny zly przy 10: 2 z 4" in tekst
    assert "jako kwadrat, pewny: 2 z 3" in tekst and tekst.index("BRAMKA (kryteria 3 i 4)") < tekst.index("OGRANICZENIE (poza bramka)")


def test_narzedzie_ocena_z_pliku_przebiegow(tmp_path, capsys):
    """``--z-przebiegow``: ocena zapisanych wpisow bez mierzenia (przeliczenie wynikow rundy 1 poprawionymi funkcjami)."""
    wpisy = [_wpis(kryterium="3", skan="odn/skan_1", tryb=t, kandydatow_zestaw=z, ostrzezenia=[f"nie ma modelu w {U.KATALOG_MODELI}"])
             for t in ("bez_numeru", "z_numerem") for z in (8, 10)]
    plik = tmp_path / "stare" / "przebiegi.jsonl"
    plik.parent.mkdir()
    plik.write_text("".join(json.dumps(w) + "\n" for w in wpisy), encoding="ascii", newline="\n")
    przed = plik.read_bytes()
    assert AR.main(["--wyjscie", str(tmp_path / "w"), "--z-przebiegow", str(plik)]) == 0
    capsys.readouterr()
    wynik = json.loads((tmp_path / "w" / "auto_uklad_r58.json").read_text(encoding="ascii"))
    o = wynik["kryteria"]["3"]
    assert (o["skanow_ok"], o["par_ok"], o["par"], o["par_bez_wyniku"], o["spelnione"]) == (1, 2, 2, 0, True)
    assert wynik["parametry"]["z_przebiegow"] == {"plikow": 1, "wpisow": 4} and list(wynik["kryteria"]) == ["3"]
    assert plik.read_bytes() == przed and not (tmp_path / "w" / "przebiegi.jsonl").exists() and not (tmp_path / "w" / "atrapy").exists()
    for nazwa in ("auto_uklad_r58.json", "auto_uklad_r58.txt"):
        dane = (tmp_path / "w" / nazwa).read_bytes()
        assert dane.isascii() and b"modele_plytek" not in dane and str(tmp_path).encode() not in dane, nazwa
    # ten sam plik z jedna para bez wyniku: kod 1
    wpisy[3].update(BRAK)
    plik.write_text("".join(json.dumps(w) + "\n" for w in wpisy), encoding="ascii", newline="\n")
    assert AR.main(["--wyjscie", str(tmp_path / "w2"), "--z-przebiegow", str(plik)]) == 1
    assert "bez wyniku 1 z 2" in capsys.readouterr().out


def test_narzedzie_ocena_czasu():
    wpisy = [_wpis(kryterium="6", skan=f"s{i}", tryb=t, kandydatow_zestaw=z, czas_scienny_s=3.0 + i * 0.1 + (0.6 if z == 10 else 0.0))
             for i in range(10) for t in ("bez_numeru", "z_numerem") for z in (8, 10)]
    o = AR.ocen_k6(wpisy)
    assert o["spelnione"] is True and o["przyrost_mediany_max_s"] == pytest.approx(0.6) and o["per_tryb"]["bez_numeru"]["pomiarow"] == 10
    wolne = [dict(w, czas_scienny_s=w["czas_scienny_s"] + (0.5 if w["kandydatow_zestaw"] == 10 else 0.0)) for w in wpisy]
    assert AR.ocen_k6(wolne)["spelnione"] is False


def test_narzedzie_maly_przebieg_zapisuje_wyniki(tmp_path, capsys):
    """Caly przebieg na 1 skanie (kryterium 2, --limit 1): pliki wyniku, ASCII + LF, bez nazw plikow projektow."""
    kod = AR.main(["--wyjscie", str(tmp_path / "w"), "--kryteria", "2", "--limit", "1"])
    capsys.readouterr()
    assert kod == 1  # zestaw niepelny (2 z 48 przebiegow) = kryterium niespelnione
    wynik = json.loads((tmp_path / "w" / "auto_uklad_r58.json").read_text(encoding="ascii"))
    o = wynik["kryteria"]["2"]
    assert (o["przebiegow"], o["ok"], o["pelny_zestaw"], o["spelnione"]) == (2, 2, False, False)
    assert wynik["bramka"]["spelniona"] is None and len(wynik["kandydaci_10"]) == 10 and len(wynik["kandydaci_8"]) == 8
    assert {w["tryb"] for w in wynik["przebiegi"]} == {"bez_numeru", "z_numerem"} and all(w["skan"].startswith("syn_okragla_ramkowa_") for w in wynik["przebiegi"])
    for nazwa in ("auto_uklad_r58.json", "auto_uklad_r58.txt", "przebiegi.jsonl"):
        dane = (tmp_path / "w" / nazwa).read_bytes()
        assert dane.isascii() and b"\r" not in dane and b".stl" not in dane, nazwa
    # --wznow nie liczy drugi raz
    assert AR.main(["--wyjscie", str(tmp_path / "w"), "--kryteria", "2", "--limit", "1", "--wznow"]) == 1
    capsys.readouterr()
    assert len((tmp_path / "w" / "przebiegi.jsonl").read_text(encoding="ascii").split("\n")) == 3
