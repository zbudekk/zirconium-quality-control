"""E3-O3: przygotowanie wydania dla plytek okraglych ramkowych n1-n6 (R58, uklady ``okragla_ramkowa_*``).

Kryteria paczki (zlecenie 2 z 21.11.2026, plan ``Ramki/etap3/plan_plytki_okragle_n1-n6_2026-11-21.md`` sekcja 4 "E3-O3"):
  (3) samokontrola: "uklady plytek z [plytki]: poprawne 10 z 10"; brak katalogu modelu ramkowego = BLAD z nazwa ukladu -
      takze wtedy, gdy lokalny plik ustawien jest sprzed E3-O1 i ukladu ramkowego w ``[plytki]`` w ogole nie ma,
  (4) symulator skanera umie wygenerowac i podac skan plytki okraglej ramkowej (``synth.generuj_plytke`` bez zmian), nowy
      scenariusz T2 ``t2_scenariusz_okragle.json`` ma 10 pozycji, w tym 2 ramkowe z tabela prawdy; sterownik T2 bierze je
      z katalogu podanego opcja (zachowanie domyslne bez zmian),
  (5) metryki: nowa wartosc ``skany.uklad`` niczego nie zmienia w raporcie (baza z 2 skanami ramkowymi),
  (7) kontrola higieny T13: waski wyjatek dla 10 kopii bajtowych R58 - tylko gdy suma SHA-256 pliku zgadza sie z lista R58,
  (8) paczka wydania zawiera 38 plikow ``modele_plytek/**`` (lista plikow paczki i prawdziwy ZIP zbudowany narzedziem).

Testy pisza tylko do ``tmp_path``. Plik jest ASCII.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import warnings
import zipfile
from pathlib import Path

import pytest

import symulator_skanera as SY
import test_metryki as TM
import test_samokontrola as TS
import zbuduj_wydanie as ZW
from stanowisko import samokontrola as S
from stanowisko import ustawienia as UST

STANOWISKO = Path(__file__).resolve().parent.parent
RAMKI = STANOWISKO.parent
NARZEDZIA_ODBIORU = RAMKI / "etap3" / "odbior_koncowy" / "narzedzia"
LISTA_R58 = RAMKI / "wyniki_v2" / "raport" / "sha256_stl_po_R58.txt"
RAMKOWE = ("okragla_ramkowa_wieczorna", "okragla_ramkowa_poranna")
DECYZJA = "decyzja wlasciciela nr 1 z 21.11.2026"
# 10 kopii bajtowych R58 w modele_plytek: plik w repo -> nazwa na liscie sum R58
KOPIE_R58 = {
    **{f"Ramki/stanowisko/modele_plytek/okragla_ramkowa_wieczorna/plytka_n{n}.stl": f"stl/ramka_plytka_okragla_ramkowa_wieczorna_n{n}_v2.stl" for n in (1, 2, 3)},
    **{f"Ramki/stanowisko/modele_plytek/okragla_ramkowa_poranna/plytka_n{n}.stl": f"stl/ramka_plytka_okragla_ramkowa_poranna_n{n}_v2.stl" for n in (4, 5, 6)},
    "Ramki/stanowisko/modele_plytek/okragla_ramkowa_wieczorna/plytka_bazowa.stl": "stl/ramka_plytka_okragla_ramkowa_wieczorna_v2.stl",
    "Ramki/stanowisko/modele_plytek/okragla_ramkowa_poranna/plytka_bazowa.stl": "stl/ramka_plytka_okragla_ramkowa_poranna_v2.stl",
    "Ramki/stanowisko/modele_plytek/okragla_ramkowa_wieczorna/uklad.json": "json/uklad_gniazd_okragla_ramkowa_wieczorna.json",
    "Ramki/stanowisko/modele_plytek/okragla_ramkowa_poranna/uklad.json": "json/uklad_gniazd_okragla_ramkowa_poranna.json",
}


def suma(dane: bytes) -> str:
    return hashlib.sha256(dane).hexdigest()


def modul_odbioru(nazwa: str):
    """Narzedzie odbioru koncowego (``Ramki/etap3/odbior_koncowy/narzedzia/<nazwa>.py``) zaladowane jako modul."""
    spec = importlib.util.spec_from_file_location(f"odbior_{nazwa}", NARZEDZIA_ODBIORU / f"{nazwa}.py")
    modul = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = modul
    spec.loader.exec_module(modul)
    return modul


def lista_r58() -> dict:
    """Nazwa z listy R58 -> suma SHA-256."""
    return {w.split(" *", 1)[1].strip(): w.split(" *", 1)[0].strip() for w in LISTA_R58.read_text(encoding="ascii").splitlines() if " *" in w}


# ----------------------------------------------------------------------------
# (3) samokontrola: 10 ukladow, brak katalogu modelu ramkowego
# ----------------------------------------------------------------------------
@pytest.fixture
def otoczenie_samokontroli(monkeypatch):
    """Jak ``test_samokontrola.otoczenie``: rejestr bez OneDrive, Excel nieuruchomiony, moduly z DLL bez prawdziwego importu."""
    monkeypatch.setitem(sys.modules, "winreg", TS.AtrapaRejestru(None))
    monkeypatch.setattr(TS.excel_com, "_win32com_client", lambda: TS.KlientCom(dziala=False))
    monkeypatch.setattr(S, "_zaladuj", lambda moduly: {n: True for n in moduly})


def korzen_programu(tmp_path: Path, bez: tuple = ()) -> Path:
    """Katalog programu w tmp z modelami plytek (``uklad.json`` skopiowany, pliki STL puste - numery plytek program bierze
    z nazw plikow) dla wszystkich ukladow wbudowanych poza ``bez``."""
    korzen = tmp_path / "program"
    for nazwa in UST.UKLADY_WBUDOWANE:
        if nazwa in bez:
            continue
        zrodlo, cel = STANOWISKO / "modele_plytek" / nazwa, korzen / "modele_plytek" / nazwa
        cel.mkdir(parents=True)
        for p in zrodlo.iterdir():
            if p.name == "uklad.json":
                shutil.copy(p, cel / p.name)
            else:
                (cel / p.name).write_bytes(b"")
    return korzen


def ustawienia_sprzed_o1(kat: TS.Katalog, zostaw: tuple | None = None) -> None:
    """Lokalny plik ustawien bez wierszy ukladow ramkowych w ``[plytki]`` (plik sprzed E3-O1); ``zostaw`` = tylko te uklady."""
    wiersze = []
    for w in kat.tekst.splitlines():
        klucz = w.split("=")[0].strip()
        if klucz in RAMKOWE or (zostaw is not None and klucz in UST.UKLADY_WBUDOWANE and klucz not in zostaw):
            continue
        wiersze.append(w)
    kat.tekst = "\n".join(wiersze) + "\n"
    kat.zapisz()


def test_samokontrola_liczy_10_ukladow(tmp_path, otoczenie_samokontroli):
    kat = TS.Katalog(tmp_path)
    assert list(kat.ust["plytki"]) == list(UST.UKLADY_WBUDOWANE) and len(UST.UKLADY_WBUDOWANE) == 10
    assert set(RAMKOWE) <= set(kat.ust["plytki"])
    s = kat.wykonaj().sprawdzenie("modele")
    assert s.poziom == S.OK and s.opis.startswith("uklady plytek z [plytki]: poprawne 10 z 10")


@pytest.mark.parametrize("zostaw", [None, ("wieczorna", "poranna")])
def test_samokontrola_stary_plik_ustawien_dostaje_uklady_ramkowe(tmp_path, otoczenie_samokontroli, zostaw):
    """Plik ustawien sprzed E3-O1 (8 ukladow albo tylko 2 wymagane), program kompletny: uklady dopisuja sie same - 10 z 10."""
    kat = TS.Katalog(tmp_path)
    ustawienia_sprzed_o1(kat, zostaw)
    assert "okragla_ramkowa" not in kat.plik.read_text(encoding="utf-8")
    s = kat.wykonaj().sprawdzenie("modele")
    assert s.poziom == S.OK and s.opis.startswith("uklady plytek z [plytki]: poprawne 10 z 10")


@pytest.mark.parametrize("brak", RAMKOWE)
def test_samokontrola_brak_katalogu_modelu_ramkowego_mowi_ktory(tmp_path, otoczenie_samokontroli, monkeypatch, brak):
    """Plik ustawien ze wzoru (10 wierszy), w katalogu programu nie ma katalogu jednego modelu ramkowego."""
    korzen = korzen_programu(tmp_path, bez=(brak,))
    monkeypatch.setattr(UST, "KORZEN", korzen)
    kat = TS.Katalog(tmp_path)
    wynik = S.wykonaj(kat.ust, plik_ustawien=kat.plik, bez_sieci=True, korzen=korzen)
    s = wynik.sprawdzenie("modele")
    drugi = next(n for n in RAMKOWE if n != brak)
    assert s.poziom == S.BLAD and wynik.kod_wyjscia == 1
    assert "poprawne 9 z 10" in s.opis and f"{brak}: brak katalogu" in s.opis and f"{drugi}:" not in s.opis
    assert ";" not in s.opis and "modele_plytek" in s.rada


@pytest.mark.parametrize("bez", [RAMKOWE, RAMKOWE[:1], RAMKOWE[1:]])
def test_samokontrola_stary_plik_ustawien_i_brak_katalogu_modelu_ramkowego(tmp_path, otoczenie_samokontroli, monkeypatch, bez):
    """LUKA sprzed E3-O3: plik ustawien sprzed E3-O1 + niepelny katalog programu (brak katalogu modelu ramkowego). Program nie
    dopisuje wtedy ukladu do ``[plytki]`` i samokontrola byla zielona ("poprawne 8 z 8") - a plytek ramkowych program nie zna.
    Teraz: BLAD z nazwa brakujacego ukladu i jego katalogiem."""
    korzen = korzen_programu(tmp_path, bez=bez)
    monkeypatch.setattr(UST, "KORZEN", korzen)
    kat = TS.Katalog(tmp_path)
    ustawienia_sprzed_o1(kat)
    ust = kat.ust
    assert not set(bez) & set(ust["plytki"]) and len(ust["plytki"]) == 10 - len(bez)
    wynik = S.wykonaj(ust, plik_ustawien=kat.plik, bez_sieci=True, korzen=korzen)
    s = wynik.sprawdzenie("modele")
    assert s.poziom == S.BLAD and wynik.kod_wyjscia == 1
    assert f"poprawne {10 - len(bez)} z 10" in s.opis and ";" not in s.opis
    for nazwa in RAMKOWE:
        if nazwa in bez:
            assert f"{nazwa}: " in s.opis and f"modele_plytek/{nazwa}" in s.opis and "brak katalogu" in s.opis
        else:
            assert f"{nazwa}: " not in s.opis
    wiersz = next(w for w in wynik.tekst().splitlines() if w.startswith("BLAD modele:"))
    assert all(n in wiersz for n in bez)


def test_samokontrola_wlasny_uklad_w_ustawieniach_liczy_sie_dodatkowo(tmp_path, otoczenie_samokontroli):
    """Uklad dopisany recznie do ``[plytki]`` (inna nazwa, katalog modelu ramkowego): 11 z 11 - licznik to uklady z ustawien."""
    kat = TS.Katalog(tmp_path)
    kat.tekst = kat.tekst.replace('okragla_ramkowa_poranna = "modele_plytek/okragla_ramkowa_poranna"',
                                  'okragla_ramkowa_poranna = "modele_plytek/okragla_ramkowa_poranna"\nwlasna = "modele_plytek/okragla_ramkowa_poranna"')
    kat.zapisz()
    assert len(kat.ust["plytki"]) == 11
    s = kat.wykonaj().sprawdzenie("modele")
    assert s.poziom == S.OK and "poprawne 11 z 11" in s.opis


# ----------------------------------------------------------------------------
# (5) metryki: nowa wartosc skany.uklad
# ----------------------------------------------------------------------------
def _wieczor_dwa_skany(katalog: Path, uklad_w: str, uklad_p: str) -> TM.Budowa:
    """Dwa skany wieczorne z decyzjami i piec z dwiema plytkami porannymi; uklady wpisane do bazy = ``uklad_w`` / ``uklad_p``."""
    b = TM.Budowa(katalog)
    b.indeks()
    s, r = b.sesja, b.rano
    b.zd("2026-11-16T17:55:00", "system", "program_start", {"wersja": "test", "wznowione": 0, "znane_pliki": 0})
    b.zd("2026-11-16T18:00:00", "ui", "start_skanu", {"udany": True})
    skan1, w1 = b.wieczor("2026-11-16T18:01:00", "wieczorna", 1, [
        (1, [("P1", 0.95)], "ok"), (2, [("P2", 0.93)], "ubytek"), (3, [("P3", 0.92)], "ubytek"), (4, [], "ok")])
    b.o("2026-11-16T18:03:00"); s.ukruszona(w1[1])
    b.o("2026-11-16T18:04:00"); s.ok(w1[2])
    b.zd("2026-11-16T18:20:00", "ui", "start_skanu", {"udany": True})
    skan2, w2 = b.wieczor("2026-11-16T18:21:00", "wieczorna", 2, [(1, [("P6", 0.95)], "ok"), (2, [("P7", 0.94)], "ubytek")])
    b.o("2026-11-16T18:22:00"); s.ukruszona(w2[1])
    b.zd("2026-11-17T06:58:00", "ui", "start_skanu", {"udany": True})
    skan3, r1 = b.rano_skan("2026-11-17T07:00:00", 4, [(1, [("P1", 0.95)], "ok"), (2, [("P2", 0.75), ("P3", 0.60)], "ok"), (3, [], "ok")])
    b.o("2026-11-17T07:02:00"); r.wybierz_kandydata(r1[1], TM.sha16("P2"))
    skan4, _ = b.rano_skan("2026-11-17T07:10:00", 5, [(1, [("P8", 0.95)], "ok"), (2, [("P5", 0.95)], "ok")])
    b.o("2026-11-17T07:20:00"); r.zamknij_piec()
    b.zd("2026-11-17T08:00:00", "system", "program_stop", {"niezakonczone": 0})
    with b.baza.transakcja():
        for skan, uklad in ((skan1, uklad_w), (skan2, uklad_w), (skan3, uklad_p), (skan4, uklad_p)):
            b.baza.wykonaj("UPDATE skany SET uklad = ? WHERE id = ?", (uklad, skan))
    return b


def test_metryki_nie_zaleza_od_nazwy_ukladu_2_skany_ramkowe(tmp_path):
    """Ta sama historia zapisana raz jako plytki kwadratowe, raz jako okragle ramkowe (2 skany wieczorne + 2 poranne z tymi
    samymi pracami i decyzjami): raport metryk jest identyczny - ``metryki.py`` nie grupuje i nie filtruje po ``skany.uklad``."""
    from stanowisko import metryki as M

    wyniki = {}
    for klucz, (uw, up) in {"kwadrat": ("wieczorna", "poranna"), "ramkowe": RAMKOWE, "testowe": ("okragla_wieczorna", "okragla_poranna")}.items():
        b = _wieczor_dwa_skany(tmp_path / klucz, uw, up)
        uklady = [w["uklad"] for w in b.baza.wiersze("SELECT uklad FROM skany ORDER BY id")]
        assert uklady == [uw, uw, up, up]
        b.baza.zamknij()
        wyniki[klucz] = TM.policz(b.plik, "2026-11-16", "2026-11-17")
        strona = "\n".join(M.strona(wyniki[klucz]))
        assert "okragl" not in strona and "ramkow" not in strona  # raport nie wypisuje nazw ukladow
    assert wyniki["ramkowe"] == wyniki["kwadrat"] == wyniki["testowe"]
    w = wyniki["ramkowe"]
    assert w["wieczor"]["skany"] == w["wieczor"]["skany_aktywne"] == 2 and w["wieczor"]["prace"] == 6 and w["wieczor"]["czerwone"] == 3
    assert w["wieczor"]["powtorzone"]["powtorzone"] == 0 and w["rano"] is not None
    assert json.dumps(w, sort_keys=True, default=str).count("okragla") == 0


def test_metryki_skan_ramkowy_przyjety_przez_sesje_nie_psuje_raportu(tmp_path):
    """Skan z ukladem ramkowym przyjety zwykla droga (``Sesja.przyjmij_wynik``): raport liczy sie bez bledu, a skan jest w nim
    policzony dokladnie raz - jako przyjety albo (galaz bez E3-O2: sesja blokuje nieznany uklad) jako "plytka nie z trybu"."""
    from stanowisko import session as SE

    b = TM.Budowa(tmp_path)
    b.indeks()
    b.zd("2026-11-16T17:55:00", "system", "program_start", {"wersja": "test", "wznowione": 0, "znane_pliki": 0})
    for i, numer in enumerate((1, 2)):
        b.zd(f"2026-11-16T18:0{i}:00", "ui", "start_skanu", {"udany": True})
        b.wieczor(f"2026-11-16T18:0{i}:30", "okragla_ramkowa_wieczorna", numer, [(1, [("P1", 0.95)], "ok"), (2, [("P2", 0.93)], "ubytek")])
    statusy = [w["status"] for w in b.baza.wiersze("SELECT status FROM skany ORDER BY id")]
    b.baza.zamknij()
    assert len(statusy) == 2 and set(statusy) <= {SE.STATUS_PRZYJETY, SE.STATUS_PLYTKA_NIE_Z_TRYBU}
    wynik = TM.policz(b.plik, "2026-11-16", "2026-11-16", tryb="wieczor")
    tekst = json.dumps(wynik, sort_keys=True, default=str)
    assert "okragla" not in tekst
    w = wynik["wieczor"]
    assert w["skany"] == w["powtorzone"]["skany"] == 2
    assert w["skany_aktywne"] == statusy.count(SE.STATUS_PRZYJETY)
    assert w["powtorzone"]["statusy"].get(SE.STATUS_PLYTKA_NIE_Z_TRYBU, 0) == statusy.count(SE.STATUS_PLYTKA_NIE_Z_TRYBU)
    assert w["powtorzone"]["powtorzone"] == statusy.count(SE.STATUS_PLYTKA_NIE_Z_TRYBU)


# ----------------------------------------------------------------------------
# (7) T13: waski wyjatek dla 10 kopii bajtowych R58
# ----------------------------------------------------------------------------
def _git(repo: Path, *argumenty: str) -> str:
    wynik = subprocess.run(["git", "-C", str(repo), "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "-c", "core.autocrlf=false",
                            "-c", "commit.gpgsign=false", *argumenty], capture_output=True, text=True, check=True)
    return wynik.stdout.strip()


WZOR_STL = "Ramki/stanowisko/modele_plytek/okragla_ramkowa_wieczorna/plytka_n1.stl"
WZOR_JSON = "Ramki/stanowisko/modele_plytek/okragla_ramkowa_wieczorna/uklad.json"


@pytest.fixture
def repo_t13(tmp_path):
    """Male repozytorium: commit poczatkowy, potem commit z 2 kopiami bajtowymi R58 (STL 1,1 MB i ``uklad.json`` nie-ASCII
    z CRLF) i lista sum R58. Zwraca (repo, commit poczatkowy)."""
    repo = tmp_path / "repo"
    (repo / "Ramki" / "stanowisko").mkdir(parents=True)
    (repo / "Ramki" / "stanowisko" / "plik.py").write_bytes(b"x = 1\n")
    _git(tmp_path, "init", "-q", str(repo))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "poczatek")
    poczatek = _git(repo, "rev-parse", "HEAD")
    for rel in (WZOR_STL, WZOR_JSON):
        cel = repo / rel
        cel.parent.mkdir(parents=True, exist_ok=True)
        cel.write_bytes((RAMKI.parent / rel).read_bytes())
    lista = repo / "Ramki" / "wyniki_v2" / "raport" / "sha256_stl_po_R58.txt"
    lista.parent.mkdir(parents=True)
    lista.write_bytes(LISTA_R58.read_bytes())
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "kopie R58")
    return repo, poczatek


def _t13(repo: Path, od: str, tmp_path: Path, capsys, **opcje) -> tuple:
    t13 = modul_odbioru("t13_higiena")
    plik = tmp_path / "t13.json"
    argumenty = ["--repo", str(repo), "--od", od, "--do", "HEAD", "--json", str(plik)]
    for k, v in opcje.items():
        argumenty += [f"--{k}", str(v)]
    capsys.readouterr()
    kod = t13.main(argumenty)
    return kod, capsys.readouterr().out, json.loads(plik.read_text(encoding="ascii"))


def test_t13_lista_wyjatkow_to_dokladnie_10_kopii_r58_z_sumami():
    t13 = modul_odbioru("t13_higiena")
    kopie = t13.wczytaj_kopie(NARZEDZIA_ODBIORU / "t13_dozwolone.txt")
    r58 = lista_r58()
    assert set(kopie) == set(KOPIE_R58) and len(kopie) == 10
    for sciezka, (sha, nazwa) in kopie.items():
        assert nazwa == KOPIE_R58[sciezka] and sha == r58[nazwa] == suma((RAMKI.parent / sciezka).read_bytes()), sciezka
    # wiersze wyjatkow nie sa przedrostkami sciezek: lista grup zostaje taka sama jak przed paczka
    grupy = t13.wczytaj_liste(NARZEDZIA_ODBIORU / "t13_dozwolone.txt")
    assert not any(g == t13.GRUPA_KOPII for _, g in grupy) and ("Ramki/stanowisko/", "E3") in grupy


def test_t13_kopie_bajtowe_r58_to_odstepstwo_nie_naruszenie(repo_t13, tmp_path, capsys):
    repo, poczatek = repo_t13
    kod, wyjscie, wynik = _t13(repo, poczatek, tmp_path, capsys)
    assert kod == 0 and wynik["naruszenia"] == []
    odstepstwo = {w["sciezka"]: w for w in wynik["odstepstwo_kopie_r58"]}
    assert set(odstepstwo) == {WZOR_STL, WZOR_JSON}
    assert any(p.startswith("duzy plik") for p in odstepstwo[WZOR_STL]["powody"])
    assert any(p.startswith("nie ASCII") for p in odstepstwo[WZOR_JSON]["powody"]) and any("CRLF" in p for p in odstepstwo[WZOR_JSON]["powody"])
    assert wynik["decyzja_kopie_r58"] == DECYZJA
    assert DECYZJA in wyjscie and "kopie bajtowe R58" in wyjscie and WZOR_STL in wyjscie
    assert "WYNIK T13: ZAL" in wyjscie and "(0 naruszen" in wyjscie and DECYZJA in wyjscie.splitlines()[-1]


@pytest.mark.parametrize("plik, powod", [(WZOR_STL, "duzy plik"), (WZOR_JSON, "nie ASCII")])
def test_t13_plik_zmieniony_o_1_bajt_naruszenie_wraca(repo_t13, tmp_path, capsys, plik, powod):
    repo, poczatek = repo_t13
    dane = bytearray((repo / plik).read_bytes())
    dane[100] ^= 0x01  # jeden bajt (STL: naglowek; JSON: tekst opisu) - dlugosc pliku bez zmian
    (repo / plik).write_bytes(bytes(dane))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "zmiana o 1 bajt")
    kod, wyjscie, wynik = _t13(repo, poczatek, tmp_path, capsys)
    powody = [w["powod"] for w in wynik["naruszenia"] if w["sciezka"] == plik]
    assert kod == 1 and any(p.startswith(powod) for p in powody), powody
    assert any("kopia bajtowa R58" in p and "suma" in p for p in powody), powody  # wprost: suma inna niz na liscie
    assert plik not in {w["sciezka"] for w in wynik["odstepstwo_kopie_r58"]}
    drugi = WZOR_JSON if plik == WZOR_STL else WZOR_STL
    assert drugi in {w["sciezka"] for w in wynik["odstepstwo_kopie_r58"]}  # wyjatek drugiego pliku zostaje
    assert "WYNIK T13: FAIL" in wyjscie
    # ten sam plik zmieniony PO commicie poczatkowym kontroli (status "zmieniony", nie "nowy") tez jest naruszeniem
    kopie = _git(repo, "rev-parse", "HEAD~1")
    kod2, _, wynik2 = _t13(repo, kopie, tmp_path, capsys)
    assert kod2 == 1 and any(w["sciezka"] == plik and "kopia bajtowa R58" in w["powod"] for w in wynik2["naruszenia"])


def test_t13_wyjatek_wymaga_sumy_z_listy_r58(repo_t13, tmp_path, capsys):
    """Suma pliku zgodna z lista wyjatkow, ale lista sum R58 w repo mowi co innego (albo jej nie ma): wyjatek nie obowiazuje."""
    repo, poczatek = repo_t13
    lista = repo / "Ramki" / "wyniki_v2" / "raport" / "sha256_stl_po_R58.txt"
    tekst = lista.read_text(encoding="ascii")
    stara = lista_r58()[KOPIE_R58[WZOR_STL]]
    lista.write_bytes(tekst.replace(stara, "0" * 64).encode("ascii"))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "inna suma na liscie R58")
    kod, _, wynik = _t13(repo, poczatek, tmp_path, capsys)
    assert kod == 1 and any(w["sciezka"] == WZOR_STL and w["powod"].startswith("duzy plik") for w in wynik["naruszenia"])
    assert WZOR_JSON in {w["sciezka"] for w in wynik["odstepstwo_kopie_r58"]}
    _git(repo, "rm", "-q", "Ramki/wyniki_v2/raport/sha256_stl_po_R58.txt")
    _git(repo, "commit", "-q", "-m", "bez listy R58")
    kod, _, wynik = _t13(repo, poczatek, tmp_path, capsys)
    assert kod == 1 and wynik["odstepstwo_kopie_r58"] == []
    assert {w["sciezka"] for w in wynik["naruszenia"]} == {WZOR_STL, WZOR_JSON}


def test_t13_wyjatek_nie_obejmuje_innych_plikow(repo_t13, tmp_path, capsys):
    """Ten sam STL pod inna sciezka (poza lista 10 plikow) i inny duzy plik w katalogu modelu ramkowego: naruszenia."""
    repo, poczatek = repo_t13
    obok = "Ramki/stanowisko/modele_plytek/okragla_ramkowa_wieczorna/plytka_n7.stl"
    gdzie_indziej = "Ramki/stanowisko/modele_plytek/wieczorna/plytka_n9.stl"
    for rel in (obok, gdzie_indziej):
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_bytes((repo / WZOR_STL).read_bytes())
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "kopie pod innymi nazwami")
    kod, _, wynik = _t13(repo, poczatek, tmp_path, capsys)
    assert kod == 1 and {w["sciezka"] for w in wynik["naruszenia"]} == {obok, gdzie_indziej}
    assert {w["sciezka"] for w in wynik["odstepstwo_kopie_r58"]} == {WZOR_STL, WZOR_JSON}


# ----------------------------------------------------------------------------
# (8) paczka wydania: 38 plikow modele_plytek
# ----------------------------------------------------------------------------
def _kola_zastepcze(katalog: Path) -> Path:
    """Puste kola o nazwach zgodnych z listami zamrozonymi programu i testow (budowa wymaga kompletu kol; tresc kol nie jest
    przedmiotem tego testu - prawdziwe kola sa w paczce probnej z kroku ciezkiego)."""
    katalog.mkdir(parents=True, exist_ok=True)
    for lista in (ZW.LISTA_PROGRAMU, ZW.LISTA_TESTOW):
        for pakiet, wersja in ZW.wczytaj_liste((STANOWISKO / lista).read_bytes(), lista).items():
            with zipfile.ZipFile(katalog / f"{pakiet.replace('-', '_')}-{wersja}-py3-none-any.whl", "w") as z:
                z.writestr(f"{pakiet.replace('-', '_')}-{wersja}.dist-info/METADATA", f"Name: {pakiet}\nVersion: {wersja}\n")
    return katalog


def test_lista_plikow_paczki_ma_38_plikow_modeli():
    pliki, _, _, _ = ZW.pliki_z_gita(STANOWISKO)
    modele = sorted(n for n in pliki if n.startswith("modele_plytek/"))
    assert len(modele) == 38
    katalogi = {n.split("/")[1] for n in modele}
    assert katalogi == set(UST.UKLADY_WBUDOWANE) and len(katalogi) == 10
    r58 = lista_r58()
    for sciezka, nazwa in KOPIE_R58.items():
        rel = sciezka.removeprefix("Ramki/stanowisko/")
        assert rel in pliki and suma(pliki[rel]) == r58[nazwa], rel
    assert sum(1 for n in modele if n.split("/")[1] in RAMKOWE) == 10


def test_prawdziwy_zip_wydania_ma_38_plikow_modeli(tmp_path):
    """Paczka zbudowana narzedziem wydania z commita HEAD (kola zastepcze): 38 wpisow ``program/modele_plytek/`` w ZIP, kazdy
    z suma w ``SUMY_PROGRAMU.sha256`` (z tego pliku samokontrola sprawdza instalacje), kontrola wlasna paczki bez roznic."""
    wynik = ZW.zbuduj(tmp_path / "paczka", _kola_zastepcze(tmp_path / "kola"), wersja="0.0.0-proba-o3", lista_wydan=tmp_path / "brak_listy.txt")
    assert wynik["samokontrola"] is True and ZW.sprawdz_zip(wynik["plik"]) == []
    with zipfile.ZipFile(wynik["plik"]) as z:
        modele = sorted(n for n in z.namelist() if n.startswith("program/modele_plytek/"))
        sumy = dict(reversed(w.split("  ", 1)) for w in z.read("program/SUMY_PROGRAMU.sha256").decode("utf-8").splitlines() if w)
        r58 = lista_r58()
        for sciezka, nazwa in KOPIE_R58.items():
            rel = sciezka.removeprefix("Ramki/stanowisko/")
            assert suma(z.read(f"program/{rel}")) == r58[nazwa] == sumy[rel], rel
    assert len(modele) == 38
    assert sum(1 for n in sumy if n.startswith("modele_plytek/")) == 38
    assert sum(1 for n in modele if n.split("/")[2] in RAMKOWE) == 10


# ----------------------------------------------------------------------------
# (4) symulator: skan plytki okraglej ramkowej
# ----------------------------------------------------------------------------
@pytest.fixture(scope="module")
def skan_ramkowy(korony, tmp_path_factory):
    """Skan plytki okraglej ramkowej wieczornej nr 1 z 3 atrap, wygenerowany symulatorem (ziarno 5801)."""
    cel = tmp_path_factory.mktemp("ramkowe")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return cel, SY.generuj_skan_plytki(cel, "okragla_ramkowa_wieczorna", 1, 5801, korony, ubytki=(1, 1))


def test_symulator_generuje_skan_plytki_ramkowej_z_prawda(skan_ramkowy, korony):
    cel, opis = skan_ramkowy
    assert opis["skan"] == "skan_okragla_ramkowa_wieczorna_n1_s5801"
    stl, prawda_plik = cel / f"{opis['skan']}.stl", cel / f"{opis['skan']}.json"
    assert stl.is_file() and prawda_plik.is_file() and opis["sha16"] == SY.skrot16(stl.read_bytes())
    prawda = json.loads(prawda_plik.read_text(encoding="utf-8"))
    assert prawda["plytka"] == "okragla_ramkowa_wieczorna" and prawda["numer"] == 1 and prawda["seed"] == 5801
    assert prawda["pole_d"] == 100.0 and prawda["poza_skanu"] is not None  # jak skany odniesienia: pole fi 100, losowa poza
    tabela = opis["prawda"]
    assert tabela == SY.tabela_prawdy(prawda_plik)
    assert tabela["uklad"] == "okragla_ramkowa_wieczorna" and tabela["numer"] == 1 and tabela["prac"] == len(korony) == 3
    assert tabela["gniazda_ubytki"] == tabela["gniazda_prac"] and len(tabela["gniazda_prac"]) == 3 and tabela["drgniec"] == 0
    assert set(tabela) == {"uklad", "numer", "prac", "gniazda_prac", "gniazda_ubytki", "drgniec"}  # same liczby i nazwa ukladu


def test_symulator_skan_ramkowy_jest_powtarzalny_i_rozpoznawany(skan_ramkowy, korony, tmp_path):
    import trimesh

    from stanowisko import plate
    from stanowisko import porownaj as PO

    cel, opis = skan_ramkowy
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        drugi = SY.generuj_skan_plytki(tmp_path / "a", "okragla_ramkowa_wieczorna", 1, 5801, korony, ubytki=(1, 1))
        inny = SY.generuj_skan_plytki(tmp_path / "b", "okragla_ramkowa_wieczorna", 1, 5802, korony, ubytki=(0, 0))
        assert drugi["sha16"] == opis["sha16"] and drugi["prawda"] == opis["prawda"]  # te same ziarna = ten sam plik
        assert inny["sha16"] != opis["sha16"] and inny["prawda"]["gniazda_ubytki"] == [] and inny["prawda"]["prac"] == 3
        kandydaci = list(PO.uklady_z_ustawien(UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU)).values())
        assert len(kandydaci) == 10
        wyr, info = plate.rozpoznaj_uklad(trimesh.load(cel / f"{opis['skan']}.stl"), kandydaci, ciecie=False)
    assert info["wybrany"] == "okragla_ramkowa_wieczorna" and info["pewny"] and wyr.numer == 1
    with pytest.raises(FileExistsError):
        SY.generuj_skan_plytki(cel, "okragla_ramkowa_wieczorna", 1, 5801, korony, ubytki=(1, 1))  # istniejacego pliku nie nadpisuje


def test_symulator_podaje_wygenerowany_skan_ramkowy(korony, tmp_path, capsys):
    """Jedno polecenie: ``--generuj okragla_ramkowa_poranna:4:5901`` tworzy skan w katalogu generowanych i zapisuje go do
    folderu skanera w kawalkach, jak kazdy inny plik zrodlowy."""
    folder, gen, dziennik = tmp_path / "eksport", tmp_path / "gen", tmp_path / "dziennik.json"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        kod = SY.main(["--folder", str(folder), "--generuj", "okragla_ramkowa_poranna:4:5901:bez_ubytkow", "--katalog-generowanych", str(gen),
                       "--projekty", str(korony[0].parent), "--czas", "0.05", "0.1", "--kawalki", "3", "5", "--dziennik", str(dziennik)])
    assert kod == 0
    zrodlo = gen / "skan_okragla_ramkowa_poranna_n4_s5901.stl"
    assert zrodlo.is_file() and (gen / "skan_okragla_ramkowa_poranna_n4_s5901.json").is_file()
    zapisane = sorted(folder.glob("*.stl"))
    assert len(zapisane) == 1 and zapisane[0].read_bytes() == zrodlo.read_bytes()
    zapisy = json.loads(dziennik.read_text(encoding="utf-8"))["zapisy"]
    assert len(zapisy) == 1 and zapisy[0]["sha16"] == SY.skrot16(zrodlo.read_bytes())
    prawda = SY.tabela_prawdy(zrodlo.with_suffix(".json"))
    assert prawda["uklad"] == "okragla_ramkowa_poranna" and prawda["numer"] == 4 and prawda["gniazda_ubytki"] == []
    assert "skan_okragla_ramkowa_poranna_n4_s5901" in capsys.readouterr().out


@pytest.mark.parametrize("argumenty, fragment", [
    (["--generuj", "okragla_ramkowa_wieczorna:1:5801"], "--katalog-generowanych"),
    (["--generuj", "okragla_ramkowa_wieczorna:7:5801", "--katalog-generowanych", "G"], "numer"),
    (["--generuj", "nie_ma_takiego:1:5801", "--katalog-generowanych", "G"], "nie_ma_takiego"),
    (["--generuj", "okragla_ramkowa_wieczorna:1", "--katalog-generowanych", "G"], "UKLAD:NUMER:ZIARNO"),
    (["--tylko-generuj"], "--generuj"),
])
def test_symulator_bledne_opcje_generowania_kod_2(tmp_path, capsys, argumenty, fragment):
    argumenty = [str(tmp_path / "gen") if a == "G" else a for a in argumenty]
    with pytest.raises(SystemExit) as e:
        SY.main(["--folder", str(tmp_path / "eksport"), *argumenty])
    assert e.value.code == 2 and fragment in capsys.readouterr().err
    assert not (tmp_path / "eksport").exists() or not any((tmp_path / "eksport").iterdir())


# ----------------------------------------------------------------------------
# (4) scenariusz T2 z plytkami ramkowymi i sterownik T2
# ----------------------------------------------------------------------------
STARY_SCENARIUSZ = NARZEDZIA_ODBIORU / "t2_scenariusz.json"
NOWY_SCENARIUSZ = NARZEDZIA_ODBIORU / "t2_scenariusz_okragle.json"
SUMA_STAREGO_SCENARIUSZA = "700b84fb1c34620f6368bdb18dca99e99c7adee41860fcb5f4c32425baff2b90"


def test_scenariusz_t2_okragle_10_plytek_w_tym_2_ramkowe():
    stary, nowy = json.loads(STARY_SCENARIUSZ.read_text(encoding="utf-8")), json.loads(NOWY_SCENARIUSZ.read_text(encoding="ascii"))
    assert suma(STARY_SCENARIUSZ.read_bytes()) == SUMA_STAREGO_SCENARIUSZA  # stary scenariusz (wyniki nocy 20/21.11) bez zmian
    assert [p["nr"] for p in nowy["plytki"]] == list(range(1, 11)) and nowy["odpowiedzi"] == stary["odpowiedzi"]
    stare = {p["nr"]: p for p in stary["plytki"]}
    generowane = [p for p in nowy["plytki"] if p.get("zrodlo") == "generowane"]
    bez_zmian = [p for p in nowy["plytki"] if p.get("zrodlo") != "generowane"]
    assert len(generowane) == 2 and len(bez_zmian) == 8
    for p in bez_zmian:
        assert p == stare[p["nr"]], p["nr"]  # 8 pozycji przeniesionych bez zmian (ten sam plik, ta sama prawda)
    osma = next(p for p in nowy["plytki"] if p["nr"] == 8)
    assert osma["sha16"] == "247ee785f428396f" and osma["oczekiwany_status"] == "przyjety"  # znany FAIL T2 (e) zostaje w zestawie
    assert sorted(p["rodzaj"] for p in nowy["plytki"]) == sorted(p["rodzaj"] for p in stary["plytki"])  # 1 uciety, 1 przeskalowany
    z_ubytkiem = [p for p in generowane if p["prawda"]["gniazda_ubytki"]]
    bez_ubytku = [p for p in generowane if not p["prawda"]["gniazda_ubytki"]]
    assert len(z_ubytkiem) == 1 and len(bez_ubytku) == 1
    for p in generowane:
        g, prawda = p["generuj"], p["prawda"]
        assert g["uklad"] == prawda["uklad"] == "okragla_ramkowa_wieczorna" and g["numer"] == prawda["numer"] and g["numer"] in (1, 2, 3)
        assert p["skan"] == f"skan_{g['uklad']}_n{g['numer']}_s{g['ziarno']:04d}" and "katalog" not in p
        assert p["rodzaj"] == "skan" and p["oczekiwany_status"] == "przyjety" and p["decyzje"] == "ukruszona_wg_prawdy"
        assert prawda["drgniec"] == 0 and prawda["prac"] == len(prawda["gniazda_prac"]) >= 3
        assert set(prawda["gniazda_ubytki"]) <= set(prawda["gniazda_prac"]) <= set(range(1, 20))
        assert len(p["sha16"]) == 16 and int(p["sha16"], 16) >= 0
    assert generowane[0]["generuj"]["ziarno"] != generowane[1]["generuj"]["ziarno"]
    # sklad wg kryterium T2 zostaje: uklady R59 i R54, okragle testowe, 1 niezgodny, 1 drgniecie, 1 uciety, plytka nie z trybu
    statusy = sorted(p["oczekiwany_status"] for p in nowy["plytki"])
    assert statusy.count("niezgodny_uklad") == 1 and statusy.count("do_powtorzenia") == 1 and statusy.count("plik_odrzucony") == 1
    assert statusy.count("plytka_nie_z_trybu") == 1 and statusy.count("przyjety") == 6
    sklady = " | ".join(p["sklad"] for p in bez_zmian)
    assert "uklad R54, kwadratowa" in sklady and "uklad R54, okragla" in sklady and "uklad R59, okragla wieczorna" in sklady


def _scenariusz_z_jednym(opis: dict, **zmiany) -> dict:
    pozycja = {"nr": 1, "rodzaj": "skan", "zrodlo": "generowane", "skan": opis["skan"], "sha16": opis["sha16"],
               "generuj": {"uklad": "okragla_ramkowa_wieczorna", "numer": 1, "ziarno": 5801, "ubytki_na_prace": [1, 1]},
               "prawda": dict(opis["prawda"]), "sklad": "okragla ramkowa wieczorna", "oczekiwany_status": "przyjety",
               "decyzje": "ukruszona_wg_prawdy"}
    pozycja.update(zmiany)
    return {"wersja": 2, "odpowiedzi": {}, "plytki": [pozycja]}


def test_symulator_generuje_skany_ze_scenariusza_i_porownuje_z_tabela_prawdy(skan_ramkowy, korony, tmp_path, capsys):
    _, opis = skan_ramkowy
    plik = tmp_path / "scen.json"
    plik.write_text(json.dumps(_scenariusz_z_jednym(opis)), encoding="ascii")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        kod = SY.main(["--tylko-generuj", "--scenariusz", str(plik), "--katalog-generowanych", str(tmp_path / "gen"), "--projekty", str(korony[0].parent)])
    wyjscie = capsys.readouterr().out
    assert kod == 0 and "zgodne ze scenariuszem: 1 z 1" in wyjscie and opis["sha16"] in wyjscie
    assert SY.skrot16((tmp_path / "gen" / f"{opis['skan']}.stl").read_bytes()) == opis["sha16"]
    # drugie uruchomienie na tym samym katalogu: plik juz jest - sprawdzany, nie generowany od nowa
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert SY.main(["--tylko-generuj", "--scenariusz", str(plik), "--katalog-generowanych", str(tmp_path / "gen"), "--projekty", str(korony[0].parent)]) == 0
    assert "juz jest" in capsys.readouterr().out
    # inna tabela prawdy w scenariuszu (np. inna pula projektow niz ta, z ktorej liczono scenariusz): kod 1 i wiersz roznicy
    zla = dict(opis["prawda"], gniazda_ubytki=[])
    plik.write_text(json.dumps(_scenariusz_z_jednym(opis, prawda=zla, sha16="0" * 16)), encoding="ascii")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        kod = SY.main(["--tylko-generuj", "--scenariusz", str(plik), "--katalog-generowanych", str(tmp_path / "gen2"), "--projekty", str(korony[0].parent)])
    wyjscie = capsys.readouterr().out
    assert kod == 1 and "zgodne ze scenariuszem: 0 z 1" in wyjscie and "NIEZGODNE" in wyjscie


def test_sterownik_t2_bierze_skan_generowany_z_katalogu_podanego_opcja(skan_ramkowy, tmp_path):
    t2 = modul_odbioru("t2_wieczor")
    cel, opis = skan_ramkowy
    scen = _scenariusz_z_jednym(opis)
    pozycje, zrodla, uciety = t2.przygotuj_zestaw(scen, [1], tmp_path / "brak_dane_ref", tmp_path / "rob", SY.skrot16, dane_generowane=cel)
    assert uciety is False and zrodla == [cel / f"{opis['skan']}.stl"] and len(pozycje) == 1
    p = pozycje[0]
    assert p["uklad"] == "okragla_ramkowa_wieczorna" and p["numer"] == 1 and p["prac"] == 3 and p["sha16"] == opis["sha16"]
    assert p["gniazda_ubytki"] == p["do_dofrezowania"] == opis["prawda"]["gniazda_ubytki"] and p["drgniec"] == 0
    with pytest.raises(SystemExit, match="--dane-generowane"):  # scenariusz ze skanem generowanym, a opcji nie podano
        t2.przygotuj_zestaw(scen, [1], tmp_path / "brak_dane_ref", tmp_path / "rob", SY.skrot16)
    with pytest.raises(SystemExit, match="sha16"):  # inny plik pod ta sama nazwa
        t2.przygotuj_zestaw(_scenariusz_z_jednym(opis, sha16="0" * 16), [1], tmp_path / "x", tmp_path / "rob", SY.skrot16, dane_generowane=cel)
    with pytest.raises(SystemExit, match="tabela prawdy"):  # prawda pliku inna niz tabela prawdy scenariusza
        zla = dict(opis["prawda"], gniazda_ubytki=[])
        t2.przygotuj_zestaw(_scenariusz_z_jednym(opis, prawda=zla), [1], tmp_path / "x", tmp_path / "rob", SY.skrot16, dane_generowane=cel)


def test_sterownik_t2_zachowanie_domyslne_bez_zmian(skan_ramkowy, tmp_path):
    """Pozycja bez pola ``zrodlo`` (stary scenariusz): skan z ``<dane-ref>/<katalog>``, jak przed paczka - takze gdy podano
    ``dane_generowane``; opcja ``--dane-generowane`` ma wartosc domyslna None."""
    t2 = modul_odbioru("t2_wieczor")
    cel, opis = skan_ramkowy
    dane_ref = tmp_path / "dane_ref"
    (dane_ref / "zestaw").mkdir(parents=True)
    for rozszerzenie in (".stl", ".json"):
        shutil.copy(cel / f"{opis['skan']}{rozszerzenie}", dane_ref / "zestaw" / f"{opis['skan']}{rozszerzenie}")
    scen = {"plytki": [{"nr": 1, "rodzaj": "skan", "katalog": "zestaw", "skan": opis["skan"], "sha16": opis["sha16"], "sklad": "x",
                        "oczekiwany_status": "przyjety", "decyzje": "ukruszona_wg_prawdy"}]}
    for dodatkowe in ({}, {"dane_generowane": tmp_path / "nie_ma"}):
        pozycje, zrodla, _ = t2.przygotuj_zestaw(scen, [1], dane_ref, tmp_path / "rob", SY.skrot16, **dodatkowe)
        assert zrodla == [dane_ref / "zestaw" / f"{opis['skan']}.stl"] and pozycje[0]["uklad"] == "okragla_ramkowa_wieczorna"
    stary = json.loads(STARY_SCENARIUSZ.read_text(encoding="utf-8"))
    assert not any("zrodlo" in p for p in stary["plytki"])
    zrodlo = (NARZEDZIA_ODBIORU / "t2_wieczor.py").read_text(encoding="ascii")
    assert '"--dane-generowane", type=Path, default=None' in zrodlo
