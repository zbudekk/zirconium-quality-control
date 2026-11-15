"""Straznik ukladu (R59): skan plytki, ktora nie pasuje do wybranego ukladu gniazd, nie moze dac zadnego wyniku z gniazdami.

Ten sam numer plytki ma dwa uklady (R59 i poprzedni ``*_r54``), wiec numer z dolkow ich nie rozroznia. Sprawdzane sa
obie warstwy straznika w ``plate``:
1. rozstaw stozkow znacznikow (uklady R59 i R54 maja stozki w innych miejscach) -> ``NiezgodnyUklad``, powod ``stozki``,
2. mapa wysokosci skanu z modelem STL w miejscach jednoznacznych -> ``NiezgodnyUklad``, powod ``gniazda``; te warstwe
   sprawdza uklad-hybryda (stozki jednego ukladu, gniazda i STL drugiego), bo w parze R59 / R54 pierwsza warstwa
   zatrzymuje skan wczesniej,
oraz ``porownaj`` (wynik bez gniazd, zadnego zielonego) i okno (komunikat). Liczniki na 240 skanach:
``narzedzia/straznik_R59.py`` i ``raporty/R59_2026-11-14.md``.
"""
from __future__ import annotations

import json
import os
import shutil
import warnings

import numpy as np
import pytest
import trimesh

from conftest import STANOWISKO
from stanowisko import match, plate, porownaj as PO, synth, uklad as U, ustawienia as UST

TYPY = ("wieczorna", "poranna", "okragla_wieczorna", "okragla_poranna")
KOMUNIKAT = "p\u0142ytka nie pasuje do wybranego uk\u0142adu"  # poczatek komunikatu NiezgodnyUklad


def _skan(nazwa: str, projekty, seed: int, prace: int | None = None):
    """Sztuczny skan plytki ``nazwa``: losowa poza skanera, pole fi 100, skala 1,22 / 1,0 jak dla typu plytki."""
    uk = U.wczytaj(nazwa)
    w = 1.0 if synth.poranna(nazwa) else 1.22
    op = synth.Opcje.z_toml(plytka=nazwa, prace_na_plytce=len(projekty) if prace is None else prace, wspolczynnik=(w, w),
                            ubytki_na_prace=(0, 0), poza_uklad=True, pole=100.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        skan, prawda = synth.generuj_plytke(uk, uk.numery[0], list(projekty), np.random.default_rng(seed), op, seed)
    return uk, skan, prawda


def _numer(uk: U.UkladPlytki) -> int | None:
    return uk.numery[0] if uk.shape == "square" else None  # kwadrat: dolki kodu poza polem fi 100


@pytest.fixture(scope="module")
def skany(korony):
    """Po jednym skanie z 3 atrapami dla kazdego z 8 ukladow."""
    return {n: _skan(n, korony, seed=41 + i) for i, n in enumerate(TYPY + tuple(t + "_r54" for t in TYPY))}


# --- warstwa 1: rozstaw stozkow ---------------------------------------------------------------
@pytest.mark.parametrize("typ", TYPY)
@pytest.mark.parametrize("kierunek", ["stara_plytka_nowy_uklad", "nowa_plytka_stary_uklad"])
def test_plytka_innego_ukladu_konczy_sie_niezgodny_uklad(skany, typ, kierunek):
    zeskanowany, wybrany = (typ + "_r54", typ) if kierunek == "stara_plytka_nowy_uklad" else (typ, typ + "_r54")
    _, skan, _ = skany[zeskanowany]
    uk_skanu, uk = U.wczytaj(zeskanowany), U.wczytaj(wybrany)
    with pytest.raises(plate.NiezgodnyUklad) as blad:
        plate.wyrownaj(skan, uk, numer=_numer(uk))
    e = blad.value
    assert isinstance(e, plate.BladWyrownania) and str(e).startswith(KOMUNIKAT) and wybrany in str(e)
    assert e.powod == "stozki" and e.macierz is None
    assert e.jakosc["uklad_zgodny"] is False and e.jakosc["uklad_powod"] == "stozki" and e.jakosc["znaczniki_reszta_mm"] > plate.RESZTA_ZNACZNIKOW_MAX
    assert e.jakosc["stozki_dopasowane"] >= 3  # skan jest dobry (3 stozki), tylko uklad inny
    assert e.jakosc["uklad_rozstaw_modelu_mm"] != e.jakosc["uklad_rozstaw_skanu_mm"]
    assert plate.stozki_pasuja(e.stozki, uk_skanu) and not plate.stozki_pasuja(e.stozki, uk)  # podpowiedz: do ktorego ukladu pasuje


@pytest.mark.parametrize("nazwa", TYPY + tuple(t + "_r54" for t in TYPY))
def test_plytka_zgodna_bez_falszywego_alarmu(skany, nazwa):
    uk, skan, prawda = skany[nazwa]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        w = plate.wyrownaj(skan, uk, numer=_numer(uk))
    j = w.jakosc
    assert j["uklad_zgodny"] is True and "uklad_powod" not in j
    assert j["uklad_dziura_w_pelnym_mm2"] == 0.0 and j["uklad_gniazdo_nad_pelnym_mm2"] < plate.PROG_GNIAZDO_NAD_PELNYM_MM2 / 5
    assert j["uklad_strefa_dna_mm2"] > 300 and j["uklad_strefa_wierzchu_mm2"] > 1500  # strefy pewne modelu widoczne w skanie
    assert {f.gniazdo for f in w.fragmenty if f.status == "praca"} == {p.gniazdo for p in prawda.prace}


# --- warstwa 2: gniazda (mapa wysokosci skanu z modelem) --------------------------------------
def _probka_modelu(uk: U.UkladPlytki, seed: int = 1) -> np.ndarray:
    """Punkty po powierzchni modelu STL plytki bez spodu = idealny skan pustej plytki w ukladzie plytki."""
    m = trimesh.load(uk.plik_stl(uk.numery[0]), force="mesh")
    m.update_faces(m.triangles_center[:, 2] > 0.5)
    P, _ = trimesh.sample.sample_surface(m, 1500000, seed=seed)
    return np.asarray(P)


@pytest.mark.parametrize("typ", TYPY)
def test_zgodnosc_ukladu_na_pustych_plytkach(typ):
    nowy, stary = U.wczytaj(typ), U.wczytaj(typ + "_r54")
    for skan_uk, drugi in ((nowy, stary), (stary, nowy)):
        P = _probka_modelu(skan_uk)
        zg = plate.zgodnosc_ukladu(P, skan_uk, skan_uk.plik_stl(skan_uk.numery[0]))
        assert zg["uklad_zgodny"] is True and zg["uklad_gniazdo_nad_pelnym_mm2"] == 0.0 and zg["uklad_dziura_w_pelnym_mm2"] == 0.0, (skan_uk.nazwa, zg)
        nz = plate.zgodnosc_ukladu(P, drugi, drugi.plik_stl(drugi.numery[0]))
        assert nz["uklad_zgodny"] is False, (skan_uk.nazwa, drugi.nazwa, nz)
        # obie miary z duzym zapasem ponad progami (zmierzone na pustych plytkach: >= 440 i >= 280 mm2)
        assert nz["uklad_gniazdo_nad_pelnym_mm2"] > 2 * plate.PROG_GNIAZDO_NAD_PELNYM_MM2 and nz["uklad_dziura_w_pelnym_mm2"] > 2 * plate.PROG_DZIURA_W_PELNYM_MM2
        # brak danych nie jest dowodem: maly wycinek skanu (kolo r 4 mm w srodku plytki) niczego nie rozstrzyga
        maly = plate.zgodnosc_ukladu(P[np.hypot(P[:, 0], P[:, 1]) < 4.0], drugi, drugi.plik_stl(drugi.numery[0]))
        assert maly["uklad_zgodny"] is True and maly["uklad_strefa_wierzchu_mm2"] + maly["uklad_strefa_dna_mm2"] < 60


def _hybryda(tmp_path, stozki_z: str, gniazda_z: str) -> U.UkladPlytki:
    """Uklad testowy: stozki znacznikow ukladu ``stozki_z``, gniazda i model STL ukladu ``gniazda_z`` (w tmp)."""
    kat = tmp_path / f"hybryda_{stozki_z}_{gniazda_z}"
    kat.mkdir()
    zr = STANOWISKO / "modele_plytek"
    d = json.loads((zr / gniazda_z / "uklad.json").read_text(encoding="utf-8"))
    d["markers"] = json.loads((zr / stozki_z / "uklad.json").read_text(encoding="utf-8"))["markers"]
    (kat / "uklad.json").write_text(json.dumps(d), encoding="utf-8")
    for p in (zr / gniazda_z).glob("plytka_n*.stl"):
        shutil.copy(p, kat / p.name)
    return U.wczytaj(f"hybryda_{stozki_z}_{gniazda_z}", kat)


@pytest.mark.parametrize("zeskanowany,wybrany", [("wieczorna", "wieczorna_r54"), ("wieczorna_r54", "wieczorna"), ("poranna", "poranna_r54"), ("poranna_r54", "poranna")])
def test_stozki_pasuja_ale_gniazda_inne(skany, tmp_path, zeskanowany, wybrany):
    """Gdyby dwa uklady mialy stozki w tych samych miejscach, skan wyrownalby sie - wtedy zatrzymuje go porownanie gniazd."""
    uk_skanu, skan, _ = skany[zeskanowany]
    hyb = _hybryda(tmp_path, zeskanowany, wybrany)
    with pytest.raises(plate.NiezgodnyUklad) as blad, warnings.catch_warnings():
        warnings.simplefilter("ignore")
        plate.wyrownaj(skan, hyb, numer=hyb.numery[0])
    e = blad.value
    assert str(e).startswith(KOMUNIKAT) and e.powod == "gniazda" and e.jakosc["uklad_zgodny"] is False
    assert e.macierz is not None and e.macierz.shape == (4, 4)  # wyrownanie po stozkach bylo, wyniku z gniazdami nie ma
    assert e.jakosc["znaczniki_reszta_mm"] < 0.05
    assert e.jakosc["uklad_gniazdo_nad_pelnym_mm2"] >= plate.PROG_GNIAZDO_NAD_PELNYM_MM2 or e.jakosc["uklad_dziura_w_pelnym_mm2"] >= plate.PROG_DZIURA_W_PELNYM_MM2
    assert plate.stozki_pasuja(e.stozki, uk_skanu)
    with warnings.catch_warnings():  # wylaczony straznik gniazd: stare zachowanie (wynik bez flagi) - tylko do diagnostyki
        warnings.simplefilter("ignore")
        w = plate.wyrownaj(skan, hyb, numer=hyb.numery[0], straznik=False, ciecie=False)
    assert "uklad_zgodny" not in w.jakosc


# --- porownaj i okno ----------------------------------------------------------------------------
@pytest.fixture(scope="module")
def folder_projektow(korony, tmp_path_factory):
    d = tmp_path_factory.mktemp("projekty_straznik")
    for i, p in enumerate(korony):
        shutil.copy(p, d / f"2026-11-02_p{i}-{['11', '14', '36'][i]}-crown_cad.stl")
    return d


@pytest.fixture(scope="module")
def wynik_niezgodny(skany, folder_projektow, tmp_path_factory):
    """Skan starej plytki okraglej wieczornej (R54) porownany z nowym ukladem ``okragla_wieczorna`` przez ``porownaj``."""
    d = tmp_path_factory.mktemp("skan_straznik")
    _, skan, prawda = skany["okragla_wieczorna_r54"]
    p_stl, p_json = synth.zapisz(skan, prawda, d, "skan_stara_plytka")
    ust = UST.wczytaj_ustawienia()
    pula = match.Pula([folder_projektow], 1.22)
    with pytest.warns(UserWarning, match="nie pasuje do wybranego"):
        wynik = PO.porownaj(p_stl, [folder_projektow], "okragla_wieczorna", ust, 1.22, None, pula=pula)
    return wynik, p_stl, p_json, ust, pula


def test_porownaj_niezgodny_uklad_zadnych_gniazd(wynik_niezgodny, tmp_path):
    wynik, p_stl, _, ust, _ = wynik_niezgodny
    assert wynik["uklad_zgodny"] is False and wynik["uklad_komunikat"].startswith(KOMUNIKAT)
    assert wynik["jakosc_wyrownania"]["uklad_zgodny"] is False and wynik["jakosc_wyrownania"]["uklad_powod"] == "stozki"
    assert wynik["gniazda"] == [] and wynik["gniazda_puste"] == [] and wynik["gniazda_podwojne"] == []
    assert set(wynik["statusy_gniazd"]) == set(PO.STATUSY_GNIAZDA) and all(n == 0 for n in wynik["statusy_gniazd"].values())  # nic zielonego
    assert wynik["numer"] is None and wynik["macierz_skan_do_plytki"] is None
    # podpowiedz: rozstaw stozkow pasuje do starego ukladu tego typu (kwadrat i okragla maja te same stozki), nie do nowych
    assert set(wynik["uklady_pasujace"]) == {"wieczorna_r54", "okragla_wieczorna_r54"}
    assert "okragla_wieczorna_r54" in wynik["uklad_komunikat"]
    json.dumps(wynik)  # wynik zapisywalny jak zwykly
    assert "NIE PASUJE" in PO.tabela(wynik) and "okragla_wieczorna_r54" in PO.tabela(wynik)
    png = PO.mapa_png(wynik, U.wczytaj("okragla_wieczorna"), tmp_path / "mapa.png")
    assert png.exists() and png.stat().st_size > 1000


def test_porownaj_zgodny_uklad_ma_flage(skany, folder_projektow, wynik_niezgodny, tmp_path):
    _, p_stl, _, ust, pula = wynik_niezgodny
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wynik = PO.porownaj(p_stl, [folder_projektow], "okragla_wieczorna_r54", ust, 1.22, None, pula=pula)
    assert wynik["uklad_zgodny"] is True and wynik["jakosc_wyrownania"]["uklad_zgodny"] is True
    assert len(wynik["gniazda"]) == 3 and wynik["numer"] == 8 and "uklad_komunikat" not in wynik


def test_cli_porownaj_niezgodny_zapisuje_wynik_bez_metryk(wynik_niezgodny, folder_projektow, tmp_path, capsys):
    _, p_stl, p_json, _, _ = wynik_niezgodny
    wynik = PO.main(["--skan", str(p_stl), "--projekty", str(folder_projektow), "--plytka", "okragla_wieczorna", "--wspolczynnik", "1.22",
                     "--prawda", str(p_json), "--wyjscie", str(tmp_path)])
    zapis = json.loads((tmp_path / f"{p_stl.stem}_wynik.json").read_text(encoding="utf-8"))
    assert zapis["uklad_zgodny"] is False and zapis["statusy_gniazd"]["zielony"] == 0 and "metryki" not in zapis
    assert any(o.startswith(KOMUNIKAT) for o in zapis["ostrzezenia"]) and wynik["uklad_zgodny"] is False
    assert (tmp_path / f"{p_stl.stem}_mapa.png").exists()
    wyjscie = capsys.readouterr().out
    assert "NIE PASUJE" in wyjscie and "UWAGA:" in wyjscie


def test_okno_lista_ukladow_i_komunikat_straznika(wynik_niezgodny, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QMessageBox

    from stanowisko import ui_test

    app = QApplication.instance() or QApplication([])
    wynik, _, _, ust, pula = wynik_niezgodny
    komunikaty = []
    monkeypatch.setattr(QMessageBox, "warning", lambda rodzic, tytul, tekst: komunikaty.append((tytul, tekst)))
    okno = ui_test.Okno(ust)
    nazwy = [okno.lista_plytek.itemText(i) for i in range(okno.lista_plytek.count())]
    assert nazwy == list(ust["plytki"]) and {"wieczorna", "wieczorna_r54", "okragla_poranna", "okragla_poranna_r54"} <= set(nazwy)
    okno.lista_plytek.setCurrentText("okragla_wieczorna")
    okno._klucz_puli = ("x", 1.22)
    okno.gotowe(wynik, {}, pula)
    assert len(komunikaty) == 1 and "okragla_wieczorna_r54" in komunikaty[0][1] and "nie pasuje" in komunikaty[0][0]
    assert "NIE PASUJE" in okno.etykieta_stanu.text()
    assert okno.mapa.niezgodny and okno.tabela.rowCount() == 0
    for g in okno.uk.sockets:  # zadnych kolorow statusu: wszystkie gniazda jak puste
        assert okno.mapa.kolor_gniazda(g.id).getRgb()[:3] == PO.KOLORY["pusty"]
    okno.close()
    app.processEvents()


# --- stary lokalny ustawienia.toml (bez ukladow *_r54): podpowiedz zamiast "nie pasuje do zadnego ukladu" -------
def _ustawienia_bez_r54(ust: dict) -> dict:
    """Ustawienia jak ze starego ``ustawienia.toml`` (sprzed R59): w ``[plytki]`` tylko uklady bez przyrostka ``_r54``."""
    return {**ust, "plytki": {n: k for n, k in ust["plytki"].items() if U.typ_plytki(n) == n}}


@pytest.fixture(scope="module")
def wynik_stare_ustawienia(wynik_niezgodny, folder_projektow):
    """Ten sam skan starej plytki okraglej wieczornej, ale ``[plytki]`` bez ukladow ``*_r54`` (pierwsze prawdziwe skany beda takie)."""
    _, p_stl, _, ust, pula = wynik_niezgodny
    stare = _ustawienia_bez_r54(ust)
    with pytest.warns(UserWarning, match="ustawienia.przyklad.toml"):
        wynik = PO.porownaj(p_stl, [folder_projektow], "okragla_wieczorna", stare, 1.22, None, pula=pula)
    return wynik, stare


def test_stary_plik_ustawien_podpowiada_brakujace_uklady_r54(wynik_niezgodny, wynik_stare_ustawienia, folder_projektow, skany, tmp_path):
    wynik_pelny, _, _, ust, pula = wynik_niezgodny
    wynik, stare = wynik_stare_ustawienia
    # ustawienia z ukladami _r54: jest nazwa pasujacego ukladu, podpowiedzi o brakujacych wierszach nie ma
    assert wynik_pelny["uklad_podpowiedz"] == "" and "ustawienia.przyklad.toml" not in wynik_pelny["uklad_komunikat"]
    assert not PO.brak_ukladow_poprzednich(ust)
    # stare ustawienia: zaden uklad nie pasuje, komunikat mowi, ktorych wierszy brakuje
    assert set(stare["plytki"]) == set(TYPY) and PO.brak_ukladow_poprzednich(stare)
    assert wynik["uklad_zgodny"] is False and wynik["uklady_pasujace"] == [] and wynik["gniazda"] == []
    assert all(n == 0 for n in wynik["statusy_gniazd"].values())
    assert wynik["uklad_podpowiedz"] == PO.PODPOWIEDZ_BRAK_R54 and wynik["uklad_komunikat"].startswith(KOMUNIKAT)
    for tekst in (wynik["uklad_komunikat"], PO.tabela(wynik)):
        assert "ustawienia.przyklad.toml" in tekst and "_r54" in tekst and "4 wiersze" in tekst
    json.dumps(wynik)
    assert PO.mapa_png(wynik, U.wczytaj("okragla_wieczorna"), tmp_path / "mapa.png").exists()
    # uklady _r54 sa w ustawieniach, ale zaden nie pasuje (plytka innego typu): to nie jest brak wierszy - bez podpowiedzi
    _, skan_p, prawda_p = skany["poranna_r54"]
    p2, _ = synth.zapisz(skan_p, prawda_p, tmp_path, "skan_poranna_stara")
    tylko_wieczorne = {**ust, "plytki": {n: k for n, k in ust["plytki"].items() if "wieczorna" in n}}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        inny = PO.porownaj(p2, [folder_projektow], "wieczorna", tylko_wieczorne, 1.22, 4, pula=pula)
    assert inny["uklad_zgodny"] is False and inny["uklady_pasujace"] == [] and inny["uklad_podpowiedz"] == ""
    assert "ustawienia.przyklad.toml" not in inny["uklad_komunikat"]


def test_okno_podpowiada_brak_ukladow_r54(wynik_niezgodny, wynik_stare_ustawienia, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QMessageBox

    from stanowisko import ui_test

    app = QApplication.instance() or QApplication([])
    pula = wynik_niezgodny[4]
    wynik, stare = wynik_stare_ustawienia
    komunikaty = []
    monkeypatch.setattr(QMessageBox, "warning", lambda rodzic, tytul, tekst: komunikaty.append((tytul, tekst)))
    okno = ui_test.Okno(stare)
    assert [okno.lista_plytek.itemText(i) for i in range(okno.lista_plytek.count())] == list(stare["plytki"])  # na liscie nie ma ukladow _r54
    okno.lista_plytek.setCurrentText("okragla_wieczorna")
    okno._klucz_puli = ("x", 1.22)
    okno.gotowe(wynik, {}, pula)
    assert len(komunikaty) == 1
    for slowo in ("ustawienia.przyklad.toml", "_r54", "4 wiersze", "uruchom okno ponownie"):
        assert slowo in komunikaty[0][1], slowo
    assert "NIE PASUJE" in okno.etykieta_stanu.text() and okno.mapa.niezgodny and okno.tabela.rowCount() == 0
    okno.close()
    app.processEvents()
