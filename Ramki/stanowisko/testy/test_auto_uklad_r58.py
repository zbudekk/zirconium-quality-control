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


# --- pole skanu mniejsze niz plytka: nigdy "pewny ze zlym ukladem" ----------------------------------
@pytest.mark.parametrize("nazwa, pole", [("okragla_ramkowa_wieczorna", 90.0), ("wieczorna", 90.0), ("okragla_wieczorna", 90.0),
                                         ("okragla_ramkowa_poranna", 80.0), ("poranna", 80.0)])
def test_male_pole_skanu_nie_daje_pewnego_zlego_ukladu(korony, kandydaci, ust, nazwa, pole):
    uk = next(u for u in kandydaci[0] if u.nazwa == nazwa)
    skan, prawda = AR.skan_syntetyczny(uk, uk.numery[0], korony, 5890, pole, ust)
    for numer in (None, prawda.numer):
        w = AR.rozpoznaj(skan, kandydaci[0], numer)
        w["prawda"] = nazwa
        assert AR.klasa(w) != "zly_pewny", w


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
