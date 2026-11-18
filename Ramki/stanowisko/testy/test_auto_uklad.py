"""Automatyczne rozpoznanie ukladu plytki (``plate.rozpoznaj_uklad``, ``porownaj`` z ``plytka="auto"``, okno).

Program ma sam rozpoznac, jaka plytka jest na skanie: wieczorna / poranna i uklad gniazd R59 / poprzedni R54 (rozstaw
stozkow znacznikow - cztery rozne trojkaty) oraz kwadrat / kolo (numer plytki albo ksztalt brzegu). Pierwsze prawdziwe
skany beda na starych plytkach (R54), a czlowiek nie ma wybierac ukladu z listy. Wynik dla rozpoznanego ukladu musi byc
taki sam jak przy ukladzie wybranym recznie. Liczniki na zestawach odniesienia: ``narzedzia/auto_uklad.py``.
"""
from __future__ import annotations

import os
import shutil
import warnings

import numpy as np
import pytest

from conftest import STANOWISKO
from stanowisko import match, plate, porownaj as PO, synth, uklad as U, ustawienia as UST

TYPY = ("wieczorna", "poranna", "okragla_wieczorna", "okragla_poranna")
WSZYSTKIE = TYPY + tuple(t + "_r54" for t in TYPY)


def _skan(nazwa: str, projekty, seed: int):
    """Sztuczny skan plytki ``nazwa``: losowa poza skanera, pole fi 100, skala 1,22 / 1,0 jak dla typu plytki."""
    uk = U.wczytaj(nazwa)
    w = 1.0 if synth.poranna(nazwa) else 1.22
    op = synth.Opcje.z_toml(plytka=nazwa, prace_na_plytce=len(projekty), wspolczynnik=(w, w), ubytki_na_prace=(0, 0), poza_uklad=True, pole=100.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        skan, prawda = synth.generuj_plytke(uk, uk.numery[0], list(projekty), np.random.default_rng(seed), op, seed)
    return uk, skan, prawda


@pytest.fixture(scope="module")
def skany(korony):
    """Po jednym skanie z 3 atrapami dla kazdego z 8 ukladow."""
    return {n: _skan(n, korony, seed=71 + i) for i, n in enumerate(WSZYSTKIE)}


@pytest.fixture(scope="module")
def uklady():
    return [U.wczytaj(n) for n in WSZYSTKIE]


@pytest.fixture(scope="module")
def rozpoznane(skany, uklady):
    """Rozpoznanie bez podanego numeru - tak, jak przy pierwszym uruchomieniu okna."""
    wyniki = {}
    for nazwa, (_, skan, _) in skany.items():
        with warnings.catch_warnings(record=True) as ostrz:
            warnings.simplefilter("always")
            wyr, info = plate.rozpoznaj_uklad(skan, uklady)
        wyniki[nazwa] = (wyr, info, [str(o.message) for o in ostrz])
    return wyniki


@pytest.mark.parametrize("nazwa", WSZYSTKIE)
def test_rozpoznaje_kazdy_z_osmiu_ukladow_bez_numeru(rozpoznane, skany, nazwa):
    wyr, info, _ = rozpoznane[nazwa]
    _, _, prawda = skany[nazwa]
    assert wyr.plytka == nazwa == info["wybrany"], info
    assert info["pewny"] is True, info
    assert wyr.jakosc["uklad_zgodny"] is True
    assert {f.gniazdo for f in wyr.fragmenty if f.status == "praca"} == {p.gniazdo for p in prawda.prace}
    wpisy = {k["uklad"]: k for k in info["kandydaci"]}
    assert set(wpisy) == set(WSZYSTKIE)
    rodzina = {n for n in WSZYSTKIE if n.removeprefix("okragla_") == nazwa.removeprefix("okragla_")}  # kwadrat i kolo: te same stozki
    assert {n for n, k in wpisy.items() if k["stozki_pasuja"]} == rodzina
    assert all(wpisy[n]["odrzucony"] == "stozki" for n in set(WSZYSTKIE) - rodzina)


@pytest.mark.parametrize("nazwa", WSZYSTKIE)
def test_wynik_jak_przy_ukladzie_wybranym_recznie(rozpoznane, skany, nazwa):
    """Rozpoznanie nie zmienia wyniku: macierz, numer i fragmenty takie same jak z ``wyrownaj`` z tym ukladem."""
    wyr, _, _ = rozpoznane[nazwa]
    uk, skan, _ = skany[nazwa]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        reczny = plate.wyrownaj(skan, uk)
    # ICP z Open3D liczy wielowatkowo: dwa przebiegi tego samego ``wyrownaj`` roznia sie o szum numeryczny rzedu 1e-15
    assert np.allclose(wyr.macierz, reczny.macierz, rtol=0.0, atol=1e-9)
    assert (wyr.numer, wyr.numer_zrodlo, wyr.bity) == (reczny.numer, reczny.numer_zrodlo, reczny.bity)
    assert [(f.gniazdo, f.status, f.liczba) for f in wyr.fragmenty] == [(f.gniazdo, f.status, f.liczba) for f in reczny.fragmenty]
    assert wyr.gniazda_puste == reczny.gniazda_puste and wyr.gniazda_podwojne == reczny.gniazda_podwojne


@pytest.mark.parametrize("nazwa", [n for n in WSZYSTKIE if n.startswith("okragla")])
def test_plytka_okragla_ma_numer_z_dolkow(rozpoznane, nazwa):
    wyr, info, _ = rozpoznane[nazwa]
    assert wyr.numer_zrodlo == "dolki" and wyr.numer in U.wczytaj(nazwa).numery
    wpis = next(k for k in info["kandydaci"] if k["uklad"] == nazwa)
    assert wpis["numer_z_dolkow_wazny"] is True


@pytest.mark.parametrize("nazwa", ["wieczorna_r54", "poranna_r54", "wieczorna", "poranna"])
def test_kwadrat_z_podanym_numerem(skany, uklady, nazwa):
    """Na kwadracie dolki kodu leza poza polem fi 100: numer podaje czlowiek i on tez wskazuje ksztalt (n1-n6 = kwadrat)."""
    uk, skan, _ = skany[nazwa]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wyr, info = plate.rozpoznaj_uklad(skan, uklady, numer=uk.numery[0], ciecie=False)
    assert wyr.plytka == nazwa and wyr.numer == uk.numery[0] and wyr.numer_zrodlo == "podany"
    assert info["pewny"] is True and info["powod"] == "numer_podany"


def test_numer_spoza_rozpoznanej_rodziny_jest_pomijany(skany, uklady):
    """Podany numer 8 (plytka okragla wieczorna) przy skanie plytki porannej: stozki rozstrzygaja, numer idzie do kosza z ostrzezeniem."""
    _, skan, _ = skany["poranna_r54"]
    with pytest.warns(UserWarning, match="nie nale"):
        wyr, info = plate.rozpoznaj_uklad(skan, uklady, numer=8, ciecie=False)
    assert wyr.plytka == "poranna_r54" and wyr.numer_zrodlo != "podany"


def test_zaden_uklad_nie_pasuje(skany, uklady):
    _, skan, _ = skany["poranna_r54"]
    tylko_wieczorne = [u for u in uklady if "wieczorna" in u.nazwa]
    with pytest.raises(plate.NierozpoznanyUklad) as blad:
        plate.rozpoznaj_uklad(skan, tylko_wieczorne)
    e = blad.value
    assert isinstance(e, plate.NiezgodnyUklad) and str(e).startswith("nie rozpoznano uk") and e.powod == "stozki"
    assert e.jakosc["uklad_zgodny"] is False and len(e.kandydaci) == len(tylko_wieczorne)
    assert all(k["odrzucony"] == "stozki" for k in e.kandydaci)
    with pytest.raises(ValueError):
        plate.rozpoznaj_uklad(skan, [])


# --- porownaj ---------------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def folder_projektow(korony, tmp_path_factory):
    d = tmp_path_factory.mktemp("projekty_auto")
    for i, p in enumerate(korony):
        shutil.copy(p, d / f"2026-11-02_p{i}-{['11', '14', '36'][i]}-crown_cad.stl")
    return d


@pytest.fixture(scope="module")
def wynik_auto(skany, folder_projektow, tmp_path_factory):
    """Skan starej plytki kwadratowej wieczornej (taka bedzie na pierwszym tescie skanera) przez ``porownaj`` bez wyboru ukladu."""
    d = tmp_path_factory.mktemp("skan_auto")
    _, skan, prawda = skany["wieczorna_r54"]
    p_stl, p_json = synth.zapisz(skan, prawda, d, "skan_stara_wieczorna")
    ust = UST.wczytaj_ustawienia()
    kontekst: dict = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wynik = PO.porownaj(p_stl, [folder_projektow], PO.AUTO, ust, None, None, kontekst=kontekst)
    return wynik, p_stl, p_json, ust, kontekst, prawda


def test_porownaj_auto_rozpoznaje_stara_plytke_i_dobiera_wspolczynnik(wynik_auto, folder_projektow):
    wynik, p_stl, _, ust, kontekst, prawda = wynik_auto
    assert wynik["plytka"] == "wieczorna_r54" and wynik["plytka_wybor"] == "auto" and wynik["uklad_zgodny"] is True
    assert wynik["uklad_auto"]["wybrany"] == "wieczorna_r54" and wynik["uklad_auto"]["pewny"] is True
    assert wynik["wspolczynnik"] == PO.wspolczynnik_domyslny("wieczorna_r54", ust)
    assert kontekst["uk"].nazwa == "wieczorna_r54" and kontekst["pula"].wspolczynnik == wynik["wspolczynnik"]
    assert {g["gniazdo"] for g in wynik["gniazda"]} == {p.gniazdo for p in prawda.prace}
    # to samo recznie: te same gniazda, ci sami kandydaci, ta sama macierz
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        reczny = PO.porownaj(p_stl, [folder_projektow], "wieczorna_r54", ust, None, None, pula=kontekst["pula"])
    assert reczny["plytka_wybor"] == "reczny" and reczny["uklad_auto"] is None
    assert np.allclose(reczny["macierz_skan_do_plytki"], wynik["macierz_skan_do_plytki"], rtol=0.0, atol=1e-9)
    klucz = lambda w: sorted((g["gniazdo"], g["status"], g["kandydaci"][0]["id"] if g["kandydaci"] else None) for g in w["gniazda"])  # noqa: E731
    assert klucz(reczny) == klucz(wynik)


def test_porownaj_auto_poranna_ma_wspolczynnik_jeden(skany, folder_projektow, tmp_path):
    _, skan, prawda = skany["okragla_poranna_r54"]
    p_stl, _ = synth.zapisz(skan, prawda, tmp_path, "skan_okragla_poranna")
    ust = UST.wczytaj_ustawienia()
    obca = match.Pula([folder_projektow], 1.22)  # pula z innym wspolczynnikiem nie moze byc uzyta przy wspolczynniku domyslnym
    kontekst: dict = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wynik = PO.porownaj(p_stl, [folder_projektow], PO.AUTO, ust, None, None, pula=obca, kontekst=kontekst, inspekcja=False)
    assert wynik["plytka"] == "okragla_poranna_r54" and wynik["wspolczynnik"] == 1.0 and wynik["numer_zrodlo"] == "dolki"
    assert kontekst["pula"] is not obca and kontekst["pula"].wspolczynnik == 1.0
    # wspolczynnik podany jawnie ma pierwszenstwo i wtedy podana pula jest uzyta bez zmian
    kontekst2: dict = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wynik2 = PO.porownaj(p_stl, [folder_projektow], PO.AUTO, ust, 1.22, None, pula=obca, kontekst=kontekst2, inspekcja=False)
    assert wynik2["wspolczynnik"] == 1.22 and kontekst2["pula"] is obca


def test_porownaj_auto_nie_rozpoznaje_gdy_brak_ukladu(skany, folder_projektow, tmp_path):
    _, skan, prawda = skany["poranna_r54"]
    p_stl, _ = synth.zapisz(skan, prawda, tmp_path, "skan_poranna_stara")
    ust = UST.wczytaj_ustawienia()
    tylko_wieczorne = {**ust, "plytki": {n: k for n, k in ust["plytki"].items() if "wieczorna" in n}}
    with pytest.warns(UserWarning, match="nie rozpoznano"):
        wynik = PO.porownaj(p_stl, [folder_projektow], PO.AUTO, tylko_wieczorne, None, None)
    assert wynik["uklad_zgodny"] is False and wynik["plytka"] == PO.AUTO and wynik["plytka_wybor"] == "auto"
    assert wynik["gniazda"] == [] and all(n == 0 for n in wynik["statusy_gniazd"].values())  # nic zielonego
    assert wynik["uklad_auto"]["wybrany"] is None and wynik["projekty"] is None and wynik["wspolczynnik"] is None
    assert wynik["uklad_komunikat"].startswith("nie rozpoznano uk")


def test_cli_domyslnie_auto(wynik_auto, folder_projektow, tmp_path, capsys):
    _, p_stl, p_json, _, _, _ = wynik_auto
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wynik = PO.main(["--skan", str(p_stl), "--projekty", str(folder_projektow), "--wyjscie", str(tmp_path), "--prawda", str(p_json), "--bez-inspekcji"])
    wyjscie = capsys.readouterr().out
    assert wynik["plytka"] == "wieczorna_r54" and wynik["plytka_wybor"] == "auto"
    assert wynik["metryki"]["uklad_rozpoznany_ok"] is True
    assert "rozpoznany automatycznie: wieczorna_r54" in wyjscie and "R54" in wyjscie
    assert (tmp_path / f"{p_stl.stem}_wynik.json").exists() and (tmp_path / f"{p_stl.stem}_mapa.png").exists()


# --- ustawienia: stary plik bez wierszy *_r54 -------------------------------------------------------
def test_stary_plik_ustawien_dostaje_uklady_wbudowane(tmp_path):
    """Lokalny ``ustawienia.toml`` sprzed R59 nie ma wierszy ``*_r54`` - program dopisuje uklady dostarczane z programem."""
    tekst = UST.PLIK_PRZYKLADU.read_text(encoding="utf-8")
    stary = "\n".join(linia for linia in tekst.splitlines() if not linia.split("=")[0].strip().endswith("_r54") and not linia.startswith("okragla_"))
    p = tmp_path / "ustawienia.toml"
    p.write_text(stary, encoding="utf-8")
    ust = UST.wczytaj_ustawienia(p)
    assert set(ust["plytki"]) == set(WSZYSTKIE)
    assert list(ust["plytki"])[:2] == ["wieczorna", "poranna"]  # kolejnosc z pliku, dopisane na koncu
    for n in WSZYSTKIE:
        assert (UST.katalog_plytki(ust, n) / "uklad.json").exists()
    assert not PO.brak_ukladow_poprzednich(ust)
    assert set(PO.uklady_z_ustawien(ust)) == set(WSZYSTKIE)
    # wpis z pliku ma pierwszenstwo przed wbudowanym
    d = {"plytki": {"wieczorna_r54": "inny/katalog"}}
    assert "wieczorna_r54" not in UST.uzupelnij_uklady_wbudowane(d) and d["plytki"]["wieczorna_r54"] == "inny/katalog"


def test_opis_ukladu():
    assert "R54" in PO.opis_ukladu("wieczorna_r54") and "kwadratowa" in PO.opis_ukladu("wieczorna_r54") and "wieczorna" in PO.opis_ukladu("wieczorna_r54")
    assert "R59" in PO.opis_ukladu("okragla_poranna") and "poranna" in PO.opis_ukladu("okragla_poranna") and "kwadratowa" not in PO.opis_ukladu("okragla_poranna")


# --- okno -------------------------------------------------------------------------------------------
def test_okno_domyslnie_rozpoznaje_automatycznie(wynik_auto, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QMessageBox

    from stanowisko import ui_test

    app = QApplication.instance() or QApplication([])
    wynik, _, _, ust, kontekst, _ = wynik_auto
    komunikaty = []
    monkeypatch.setattr(QMessageBox, "warning", lambda rodzic, tytul, tekst: komunikaty.append((tytul, tekst)))
    okno = ui_test.Okno(ust)
    assert okno.tryb_auto() and not okno.lista_plytek.isEnabled() and okno.uk is None
    assert okno.pole_wspolczynnik.text().startswith("auto")  # wspolczynnik domyslny dla rozpoznanej plytki
    assert [okno.lista_plytek.itemText(i) for i in range(okno.lista_plytek.count())] == list(ust["plytki"])
    # wynik rozpoznania: okno podpisuje plytke i rysuje mape rozpoznanego ukladu
    okno._klucz_puli = ("x", None)
    okno.gotowe(wynik, {}, kontekst["pula"])
    assert okno.uk is not None and okno.uk.nazwa == "wieczorna_r54" and okno.mapa.uk is okno.uk and not okno.mapa.niezgodny
    assert "wieczorna_r54" in okno.etykieta_plytki.text() and "R54" in okno.etykieta_plytki.text()
    assert okno.pule[("x", round(wynik["wspolczynnik"], 4))] is kontekst["pula"] and komunikaty == []
    assert okno.tabela.rowCount() == len(wynik["gniazda"])
    # nierozpoznana plytka: komunikat, zadnych kolorow
    brak = {**wynik, "uklad_zgodny": False, "uklad_komunikat": "nie rozpoznano ukladu plytki: test", "gniazda": [], "gniazda_podwojne": [],
            "statusy_gniazd": {s: 0 for s in PO.STATUSY_GNIAZDA}, "ubytki": 0, "uklad_auto": {"wybrany": None, "pewny": False, "powod": "stozki", "kandydaci": []}}
    okno.gotowe(brak, {}, None)
    assert len(komunikaty) == 1 and "Nie rozpoznano" in komunikaty[0][0] and okno.uk is None and "NIE ROZPOZNANO" in okno.etykieta_stanu.text()
    # wybor ukladu z listy (takze programowo) wylacza tryb automatyczny i przywraca wspolczynnik domyslny ukladu
    okno.lista_plytek.setCurrentText("okragla_poranna")
    assert not okno.tryb_auto() and okno.lista_plytek.isEnabled() and okno.uk.nazwa == "okragla_poranna"
    assert okno.pole_wspolczynnik.value() == pytest.approx(1.0) and okno.etykieta_plytki.text() == ""
    okno.pole_auto.setChecked(True)
    assert okno.tryb_auto() and okno.uk is None and okno.pole_wspolczynnik.text().startswith("auto")
    okno.close()
    app.processEvents()
