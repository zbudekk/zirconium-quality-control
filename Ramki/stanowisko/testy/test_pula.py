"""pula.py i wspolczynniki.py (E3-A4): pula poranna, pula wieczorna, wspolczynniki z pliku CSV i wpis reczny na krazek.

Kryteria planu etapu 3 (sekcja 4.1, E3-A4) sprawdzane tutaj: 3 (pula poranna: tabela 10 dat, piatek obejmuje weekend;
zlecenia starsze niz 10 dni poza pula), 4 (pula wieczorna z CSV i wpisow recznych: STL z dzis i wczoraj, ten sam STL
z dwoma wspolczynnikami = 2 wpisy, STL z CSV spoza indeksu = licznik "brakujace"), 5 (bledny CSV = komunikat z numerem
linii), 6 (0 nazw folderow i plikow zlecen poza czterema tabelami: dziennik, wyjatki, wyniki funkcji puli, logi).
Decyzje wlasciciela 17.11.2026: DW6 = (c) CSV `plik;krazek;wspolczynnik;data` oraz wpis reczny raz na krazek; doba
robocza 06:00-06:00 ("dzis" / "wczoraj" puli liczone w dobach, nie w datach kalendarza). Dane FIKCYJNE, tylko tmp_path.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import json
import logging
import re
import traceback
from pathlib import Path

import numpy as np
import pytest

import drzewo_syntetyczne as D
from stanowisko import baza as B
from stanowisko import indeks as I
from stanowisko import pula as P
from stanowisko import session as SE
from stanowisko import synth as S
from stanowisko import ustawienia as UST
from stanowisko import wspolczynniki as W

STANOWISKO = Path(__file__).resolve().parent.parent
TERAZ = dt.datetime(2026, 11, 17, 20, 0)  # wtorek, 2. zmiana; doba robocza 17.11
NAGLOWEK = "plik;krazek;wspolczynnik;data"
OPERATOR = "Technik A"  # decyzja robocza 5: kto wpisal wspolczynnik reczny (dziennik)

PLIK_A = "2026-11-16_testowski-14-crown_cad.stl"
PLIK_B = "2026-11-16_testowski-15-crown_cad.stl"
PLIK_C = "2026-11-16_probna-36-crown_cad.stl"
PLIK_F = "2026-11-16_zmyslona-11-crown_cad.stl"
FOLDERY = {  # (zrodlo, folder) -> {plik: czas modyfikacji}
    ("Cyrkon", "Testowski 3263 zs"): {PLIK_A: dt.datetime(2026, 11, 16, 12), PLIK_B: dt.datetime(2026, 11, 16, 12)},
    ("Cyrkon", "Probna 3301 kor"): {PLIK_C: dt.datetime(2026, 11, 16, 13)},
    ("Cyrkon", "Fikcyjny 0412"): {"zab 46.stl": dt.datetime(2026, 11, 16, 12)},
    ("Cyrkon", "Atrapowicz 512 Jan"): {"zab 46.stl": dt.datetime(2026, 11, 10, 12)},
    ("Prywatne", "#1234 Zmyslona"): {PLIK_F: dt.datetime(2026, 11, 16, 14)},
}
CSV_WIECZOR = [
    f"{PLIK_A};K-1;1,2210;2026-11-17",                           # linia 2: dzis
    f"{PLIK_A};K-2;1,2480;2026-11-17",                           # linia 3: ten sam STL, drugi krazek
    f"{PLIK_B};K-3;;2026-11-16",                                 # linia 4: wczoraj, wspolczynnik z wpisu recznego
    f"{PLIK_C};K-4;;2026-11-17",                                 # linia 5: bez wspolczynnika i bez wpisu recznego
    "2026-11-16_brakujacy-21-crown_cad.stl;K-1;1,2210;2026-11-17",  # linia 6: STL spoza indeksu
    f"{PLIK_F};K-1;1,2210;2026-11-15",                           # linia 7: przedwczoraj (poza pula)
    "Fikcyjny 0412\\zab 46.stl;K-5;1,2300;2026-11-18",           # linia 8: z folderem; data kalendarza 3. zmiany
    "zab 46.stl;K-5;1,2350;2026-11-19",                          # linia 9: jutro (poza pula)
    "zab 46.stl;K-6;1,2400;17.11.2026",                          # linia 10: sama nazwa, dwa pliki w indeksie
]


def zapisz_csv(p: Path, wiersze: list[str], naglowek: str | None = NAGLOWEK, kodowanie: str = "utf-8") -> Path:
    tekst = "\n".join(([naglowek] if naglowek is not None else []) + wiersze) + "\n"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(tekst.encode(kodowanie))
    return p


def zbuduj_foldery(cel: Path, foldery: dict, seed: int = 0) -> None:
    rng = np.random.default_rng(seed)
    for (zrodlo, folder), pliki in foldery.items():
        for plik, kiedy in pliki.items():
            D.zapisz_stl(D.atrapa(rng), cel / zrodlo / folder / plik, kiedy)
        D.ustaw_czas(cel / zrodlo / folder, max(pliki.values()))


def zrodla(cel: Path) -> dict:
    return {"cyrkon": cel / "Cyrkon", "prywatne": cel / "Prywatne"}


def sha(cel: Path, zrodlo: str, folder: str, plik: str) -> str:
    return S.skrot_pliku(cel / zrodlo / folder / plik)


@pytest.fixture
def baza(tmp_path):
    b = B.otworz(tmp_path / "dane" / "stanowisko.sqlite")
    yield b
    b.zamknij()


@pytest.fixture
def wieczor(tmp_path, baza):
    """Indeks 5 zlecen, CSV z 9 wierszami i wpis reczny K-3 = 1,235."""
    cel = tmp_path / "drzewo"
    zbuduj_foldery(cel, FOLDERY)
    I.indeksuj(baza, zrodla(cel), TERAZ)
    csv = zapisz_csv(tmp_path / "millbox" / "wspolczynniki.csv", CSV_WIECZOR)
    W.wczytaj_do_bazy(baza, csv, teraz=TERAZ)
    W.wpisz_reczny(baza, " k-3 ", 1.235, operator=OPERATOR, teraz=TERAZ)
    return cel, csv


def wpisy(pula: P.Pula, cel: Path) -> list[tuple]:
    """(plik, wspolczynnik, krazek, zrodlo wspolczynnika) - plik odtworzony w tescie ze skrotu (w puli nazw nie ma)."""
    po_skrocie = {}
    for (zrodlo, folder), pliki in FOLDERY.items():
        for plik in pliki:
            po_skrocie[sha(cel, zrodlo, folder, plik)] = f"{folder}/{plik}"
    return sorted((po_skrocie[w.sha16], round(w.wspolczynnik, 4), w.krazek, w.zrodlo_wspolczynnika) for w in pula.wpisy)


# --- doba robocza i dni robocze ------------------------------------------------------------------------------------
@pytest.mark.parametrize("czas, doba", [
    ("2026-11-17T06:00:00", "2026-11-17"), ("2026-11-17T05:59:59", "2026-11-16"), ("2026-11-17T23:59:00", "2026-11-17"),
    ("2026-11-18T03:00:00", "2026-11-17"), ("2026-11-18T06:01:00", "2026-11-18"), ("2026-11-21T12:00:00", "2026-11-21"),
])
def test_doba_robocza_taka_sama_jak_w_sesji(baza, czas, doba):
    chwila = dt.datetime.fromisoformat(czas)
    assert P.doba_robocza(chwila, 6).isoformat() == doba == SE.Sesja(baza, granica_doby_godz=6).doba(chwila)
    assert P.doba_robocza(chwila, 0) == chwila.date()


@pytest.mark.parametrize("dzien, dni, poczatek", [
    ("2026-11-16", 4, "2026-11-10"), ("2026-11-19", 4, "2026-11-13"), ("2026-11-20", 4, "2026-11-16"),
    ("2026-11-21", 4, "2026-11-17"), ("2026-11-22", 1, "2026-11-20"), ("2026-11-18", 0, "2026-11-18"),
])
def test_poczatek_dni_roboczych_weekend_nalezy_do_piatku(dzien, dni, poczatek):
    assert P.poczatek_dni_roboczych(dt.date.fromisoformat(dzien), dni).isoformat() == poczatek


# --- kryterium 3: pula poranna ---------------------------------------------------------------------------------------
TABELA_RANO = [  # (teraz, pierwsza chwila w puli) - policzone recznie: 4 dni robocze wstecz od doby, sobota i niedziela sie nie licza
    ("2026-11-16T08:00", "2026-11-10T06:00"),  # pon: pt, czw, sr, wt
    ("2026-11-17T08:00", "2026-11-11T06:00"),  # wt
    ("2026-11-18T08:00", "2026-11-12T06:00"),  # sr
    ("2026-11-19T08:00", "2026-11-13T06:00"),  # czw: od piatku - weekend 14-15.11 w puli
    ("2026-11-20T08:00", "2026-11-16T06:00"),  # pt: od poniedzialku - weekend 14-15.11 poza pula
    ("2026-11-21T10:00", "2026-11-17T06:00"),  # sobota
    ("2026-11-22T10:00", "2026-11-17T06:00"),  # niedziela
    ("2026-11-23T08:00", "2026-11-17T06:00"),  # pon: pt, czw, sr, wt
    ("2026-11-24T05:30", "2026-11-17T06:00"),  # wt przed 6:00 = jeszcze doba poniedzialku
    ("2026-11-25T06:00", "2026-11-19T06:00"),  # sr punkt 6:00 = juz doba srody
]


@pytest.fixture(scope="module")
def drzewo_dni(tmp_path_factory):
    """75 zlecen: po jednym z 05:59, 06:01 i 12:00 kazdego dnia 1-25.11.2026 (+ jedno prywatne 20.11); kuweta = numer zlecenia."""
    cel = tmp_path_factory.mktemp("dni")
    czasy, foldery, nr = {}, {}, 0
    for dzien in range(1, 26):
        for godz, minuta in ((5, 59), (6, 1), (12, 0)):
            nr += 1
            kiedy = dt.datetime(2026, 11, dzien, godz, minuta)
            foldery[("Cyrkon", f"Testowski {nr} d{dzien:02d}")] = {f"zab {11 + nr % 7}.stl": kiedy}
            czasy[str(nr)] = kiedy
    foldery[("Prywatne", "#7777 Zmyslona")] = {"zab 21.stl": dt.datetime(2026, 11, 20, 12)}
    czasy["#7777"] = dt.datetime(2026, 11, 20, 12)
    zbuduj_foldery(cel, foldery, seed=1)
    return cel, czasy


@pytest.fixture
def baza_dni(drzewo_dni, baza):
    cel, czasy = drzewo_dni
    I.indeksuj(baza, zrodla(cel), dt.datetime(2026, 11, 25, 13, 0), usun_po_dniach=60, licz_cechy=False)
    return baza, czasy


def kuwety(pula: P.Pula) -> set[str]:
    return {w.kuweta for w in pula.wpisy}


def test_kryterium3_pula_poranna_tabela_10_dat_zgodna_w_10_z_10(baza_dni):
    b, czasy = baza_dni
    zgodne = 0
    for teraz, pierwsza in TABELA_RANO:
        p = P.pula_poranna(b, dt.datetime.fromisoformat(teraz), dni_robocze=4, usun_po_dniach=10, granica_doby_godz=6)
        oczekiwane = {k for k, kiedy in czasy.items() if kiedy >= dt.datetime.fromisoformat(pierwsza)}
        zgodne += kuwety(p) == oczekiwane
        assert kuwety(p) == oczekiwane, teraz
        assert all(w.wspolczynnik == 1.0 and w.krazek is None and w.frezowanie_id is None and w.zrodlo_wspolczynnika == "rano"
                   for w in p.wpisy)
    assert zgodne == 10 == len(TABELA_RANO)


def test_kryterium3_zlecenia_starsze_niz_10_dni_poza_pula(baza_dni):
    b, czasy = baza_dni
    teraz = dt.datetime(2026, 11, 25, 8, 0)
    p = P.pula_poranna(b, teraz, dni_robocze=10, usun_po_dniach=10)  # 10 dni roboczych siegaloby 11.11; limit 10 dni = 15.11 08:00
    assert kuwety(p) == {k for k, kiedy in czasy.items() if kiedy >= teraz - dt.timedelta(days=10)}
    assert min(czasy[k] for k in kuwety(p)) == dt.datetime(2026, 11, 15, 12, 0)
    p = P.pula_poranna(b, teraz, dni_robocze=10, usun_po_dniach=30)
    assert min(czasy[k] for k in kuwety(p)) == dt.datetime(2026, 11, 11, 6, 1)
    assert p.od == "2026-11-11T06:00:00"


def test_pula_poranna_bez_usunietych_liczniki_i_kolejnosc(baza_dni):
    b, czasy = baza_dni
    teraz = dt.datetime(2026, 11, 20, 8, 0)
    p1 = P.pula_poranna(b, teraz)
    b.wykonaj("UPDATE zlecenia SET usuniety = 1 WHERE kuweta = '50'")  # 50 = 17.11 06:01
    p2 = P.pula_poranna(b, teraz)
    assert kuwety(p1) - kuwety(p2) == {"50"}
    assert p2.liczniki["zlecen"] == len(kuwety(p2)) and p2.liczniki["wpisow"] == len(p2.wpisy)
    assert p2.liczniki["bez_cech"] == len(p2.wpisy)  # indeks bez cech (licz_cechy=False)
    assert [w.projekt_id for w in p2.wpisy] == sorted(w.projekt_id for w in p2.wpisy)
    assert p2.tryb == "rano" and p2.doba == "2026-11-20"


# --- kryterium 4: pula wieczorna -------------------------------------------------------------------------------------
OCZEKIWANA_17 = [
    ("Fikcyjny 0412/zab 46.stl", 1.23, "K-5", "csv"),
    ("Fikcyjny 0412/zab 46.stl", 1.24, "K-6", "csv"),
    (f"Testowski 3263 zs/{PLIK_A}", 1.221, "K-1", "csv"),
    (f"Testowski 3263 zs/{PLIK_A}", 1.248, "K-2", "csv"),
    (f"Testowski 3263 zs/{PLIK_B}", 1.235, "K-3", "reczny"),
]


def test_kryterium4_pula_wieczorna_z_csv_i_wpisow_recznych(baza, wieczor):
    cel, _ = wieczor
    p = P.pula_wieczorna(baza, TERAZ, dni=2, granica_doby_godz=6)
    assert wpisy(p, cel) == OCZEKIWANA_17
    assert (p.liczniki["brakujace"], p.liczniki["niejednoznaczne"], p.liczniki["bez_wspolczynnika"]) == (1, 1, 1)
    assert p.liczniki["krazki_bez_wspolczynnika"] == ["K-4"]
    assert p.liczniki["wierszy"] == 7 and p.liczniki["wpisow"] == 5
    a = [w for w in p.wpisy if w.sha16 == sha(cel, "Cyrkon", "Testowski 3263 zs", PLIK_A)]
    assert len(a) == 2 and len({w.frezowanie_id for w in a}) == 2  # ten sam STL z dwoma wspolczynnikami = 2 wpisy
    assert {w.kuweta for w in a} == {"3263"} and {w.zeby for w in a} == {"14"}
    assert p.tryb == "wieczor" and p.doba == "2026-11-17" and (p.od, p.do) == ("2026-11-16T06:00:00", "2026-11-18T06:00:00")


def test_kryterium4_dzis_i_wczoraj_w_dobach_roboczych_nie_w_datach(baza, wieczor):
    cel, _ = wieczor
    # 18.11 03:00 = 3. zmiana doby 17.11: pula ta sama co o 20:00 (wiersz z 16.11 nadal "wczoraj")
    assert wpisy(P.pula_wieczorna(baza, dt.datetime(2026, 11, 18, 3, 0)), cel) == OCZEKIWANA_17
    # 18.11 08:00 = doba 18.11: wiersz z 16.11 wypada, wiersz z 19.11 (sama nazwa, blizej Fikcyjny) wchodzi
    p = P.pula_wieczorna(baza, dt.datetime(2026, 11, 18, 8, 0))
    assert wpisy(p, cel) == sorted([("Fikcyjny 0412/zab 46.stl", 1.23, "K-5", "csv"), ("Fikcyjny 0412/zab 46.stl", 1.24, "K-6", "csv"),
                                    ("Fikcyjny 0412/zab 46.stl", 1.235, "K-5", "csv"), (f"Testowski 3263 zs/{PLIK_A}", 1.221, "K-1", "csv"),
                                    (f"Testowski 3263 zs/{PLIK_A}", 1.248, "K-2", "csv")])
    assert p.liczniki["niejednoznaczne"] == 2
    # jeden dzien: tylko doba 17.11 (data kalendarza 17 i 18)
    assert ("Testowski 3263 zs/" + PLIK_B, 1.235, "K-3", "reczny") not in wpisy(P.pula_wieczorna(baza, TERAZ, dni=1), cel)


def test_pula_wieczorna_wspolczynnik_awaryjny_dla_krazka_bez_wspolczynnika(baza, wieczor):
    cel, _ = wieczor
    p = P.pula_wieczorna(baza, TERAZ, wspolczynnik_awaryjny=1.22)
    assert ("Probna 3301 kor/" + PLIK_C, 1.22, "K-4", "awaryjny") in wpisy(p, cel)
    assert p.liczniki["bez_wspolczynnika"] == 0 and p.liczniki["krazki_bez_wspolczynnika"] == []


def test_csv_wczytany_przed_indeksem_pula_i_powiazanie_pozniej(tmp_path, baza):
    csv = zapisz_csv(tmp_path / "w.csv", CSV_WIECZOR)
    r = W.wczytaj_do_bazy(baza, csv, teraz=TERAZ)
    assert (r.nowe, r.powiazane, r.brakujace) == (9, 0, 9)
    cel = tmp_path / "drzewo"
    zbuduj_foldery(cel, FOLDERY)
    I.indeksuj(baza, zrodla(cel), TERAZ)
    W.wpisz_reczny(baza, "K-3", 1.235, operator=OPERATOR, teraz=TERAZ)
    assert wpisy(P.pula_wieczorna(baza, TERAZ), cel) == OCZEKIWANA_17  # powiazanie w pamieci, bez zapisu
    assert baza.wiersz("SELECT count(*) AS n FROM frezowania WHERE projekt_id IS NOT NULL")["n"] == 0
    pw = W.powiaz_frezowania(baza)
    assert (pw.powiazane, pw.brakujace, pw.niejednoznaczne) == (8, 1, 2)
    assert baza.wiersz("SELECT count(*) AS n FROM frezowania WHERE projekt_id IS NOT NULL")["n"] == 8
    assert wpisy(P.pula_wieczorna(baza, TERAZ), cel) == OCZEKIWANA_17


def test_projekt_usuniety_z_indeksu_szukany_ponownie_po_nazwie(baza, wieczor, tmp_path):
    cel, _ = wieczor
    stary = cel / "Cyrkon" / "Testowski 3263 zs"
    stary.rename(cel / "Cyrkon" / "Testowski 3263 zs poprawka")
    I.indeksuj(baza, zrodla(cel), TERAZ)
    p = P.pula_wieczorna(baza, TERAZ)
    a = [w for w in p.wpisy if w.krazek in ("K-1", "K-2")]
    assert len(a) == 2 and all(baza.wiersz("SELECT usuniety FROM projekty WHERE id = ?", (w.projekt_id,))["usuniety"] == 0 for w in a)


# --- wczytanie CSV ---------------------------------------------------------------------------------------------------
def test_wczytanie_csv_powiazanie_i_ponowne_wczytanie_bez_duplikatow(baza, wieczor, tmp_path):
    cel, csv = wieczor
    f = baza.wiersze("SELECT * FROM frezowania WHERE zrodlo = 'csv' ORDER BY id")
    assert len(f) == 9 and {w["raport_plik"] for w in f} == {"wspolczynniki.csv"}
    assert all(w["wczytano"] == TERAZ.isoformat() for w in f)
    po_linii = {i + 2: w for i, w in enumerate(f)}
    assert po_linii[4]["wspolczynnik"] is None and po_linii[4]["krazek"] == "K-3"
    assert po_linii[10]["data"] == "2026-11-17"  # 17.11.2026 -> postac ISO
    assert po_linii[6]["projekt_id"] is None  # spoza indeksu
    fikcyjny = baza.wiersz("SELECT p.id FROM projekty p JOIN zlecenia z ON z.id = p.zlecenie_id WHERE z.folder = 'Fikcyjny 0412'")["id"]
    assert po_linii[8]["projekt_id"] == fikcyjny == po_linii[10]["projekt_id"]  # z folderem: dokladnie; sama nazwa: blizej daty
    r = W.wczytaj_do_bazy(baza, csv, teraz=TERAZ)
    assert (r.wierszy, r.nowe, r.zmienione, r.bez_zmian) == (9, 0, 0, 9)
    zmieniony = CSV_WIECZOR.copy()
    zmieniony[0] = f"{PLIK_A};K-1;1,2220;2026-11-17"  # poprawiony wspolczynnik tego samego wiersza (plik, krazek, data)
    r = W.wczytaj_do_bazy(baza, zapisz_csv(csv, zmieniony), teraz=TERAZ)
    assert (r.nowe, r.zmienione, r.bez_zmian) == (0, 1, 8)
    assert baza.wiersz("SELECT wspolczynnik FROM frezowania WHERE id = ?", (po_linii[2]["id"],))["wspolczynnik"] == pytest.approx(1.222)
    # runda 2 (P3, pytanie 6 - zmiana wymagania): dla dni obecnych w pliku plik jest zrodlem prawdy. Plik ma dni 16 i 17.11:
    # wiersze tych dni, ktorych w pliku juz nie ma (linie 5, 6, 10), sa nieaktualne (w bazie zostaja, oznaczone); dni 15, 18
    # i 19.11 (nieobecne w pliku - plik czyszczony codziennie) zostaja aktualne.
    r = W.wczytaj_do_bazy(baza, zapisz_csv(csv, zmieniony[:3]), teraz=TERAZ)
    assert (r.wierszy, r.nieaktualne) == (3, 3)
    assert baza.wiersz("SELECT count(*) AS n FROM frezowania WHERE zrodlo = 'csv'")["n"] == 6
    nieaktualne = baza.wiersze("SELECT id FROM frezowania WHERE zrodlo = ? ORDER BY id", (W.ZRODLO_CSV_NIEAKTUALNY,))
    assert [w["id"] for w in nieaktualne] == [po_linii[n]["id"] for n in (5, 6, 10)]


@pytest.mark.parametrize("kodowanie, bom", [("utf-8", False), ("utf-8", True), ("cp1250", False)])
def test_csv_kodowanie_bom_crlf_puste_linie_spacje(tmp_path, kodowanie, bom):
    tekst = (f"{NAGLOWEK}\r\n\r\n \u017b\u00f3\u0142ty.stl ; k-1 ; 1.2210 ; 2026-11-17 \r\nzab 46.stl;;1,23;17.11.2026\r\n\r\n")
    dane = tekst.encode(kodowanie)
    p = tmp_path / "w.csv"
    p.write_bytes((b"\xef\xbb\xbf" if bom else b"") + dane)
    w = W.wczytaj_csv(p, dzis=TERAZ.date())
    assert [(x.linia, x.plik, x.krazek, x.wspolczynnik, x.data.isoformat()) for x in w] == [
        (3, "\u017b\u00f3\u0142ty.stl", "K-1", pytest.approx(1.221), "2026-11-17"), (4, "zab 46.stl", None, pytest.approx(1.23), "2026-11-17")]


@pytest.mark.parametrize("wiersze, naglowek, linie, fragment", [
    ([f"{PLIK_A};K-1;1,22;2026-11-17"], "plik,krazek,wspolczynnik,data", [1], "srednik"),
    ([f"{PLIK_A};K-1;1,22;2026-11-17"], None, [1], "naglowka"),
    ([], "", [1], "naglowka"),
    ([f"{PLIK_A};K-1;1,22;2026-11-17", f"{PLIK_B};K-1;1,22"], NAGLOWEK, [3], "4 pola"),
    ([f"{PLIK_A};K-1;1,22;2026-11-17", f"{PLIK_B};K-1;1,22;2026-11-17", f"{PLIK_C};K-1;1,2x;2026-11-17"], NAGLOWEK, [4], "liczba"),
    ([f"{PLIK_A};K-1;12,2;2026-11-17"], NAGLOWEK, [2], "zakres"),
    ([f"{PLIK_A};K-1;0;2026-11-17"], NAGLOWEK, [2], "zakres"),
    ([f"{PLIK_A};K-1;nan;2026-11-17"], NAGLOWEK, [2], "liczba"),
    ([f"{PLIK_A};K-1;1,22;2026-11-17"] * 3 + [f"{PLIK_B};K-1;1,22;27 listopada"], NAGLOWEK, [5], "data"),
    ([f"{PLIK_A};K-1;1,22;2026-02-30"], NAGLOWEK, [2], "data"),
    ([" ;K-1;1,22;2026-11-17"], NAGLOWEK, [2], "plik"),
    ([f"{PLIK_A};;;2026-11-17"], NAGLOWEK, [2], "krazek"),
    ([f"{PLIK_A};K-1;1,22;2026-11-17", f"{PLIK_B};K-1;1,22;2026-11-17", f"{PLIK_A};k-1;1,25;2026-11-17"], NAGLOWEK, [4], "linii 2"),
    ([f"{PLIK_A};K-1;1,2x;2026-11-17", f"{PLIK_B};K-1;1,22;2026-11-17", f"{PLIK_C};K-1;1,22;2026-11-17", "x.stl;K-1"],
     NAGLOWEK, [2, 5], "2 bledne"),
])
def test_kryterium5_bledny_csv_komunikat_z_numerem_linii_i_nic_nie_wczytano(tmp_path, baza, wiersze, naglowek, linie, fragment):
    p = zapisz_csv(tmp_path / "zly.csv", wiersze, naglowek)
    with pytest.raises(W.BladWspolczynnikow) as e:
        W.wczytaj_do_bazy(baza, p, teraz=TERAZ)
    tekst = str(e.value)
    assert e.value.linie == linie
    for n in linie:
        assert re.search(rf"\blinia {n}\b", tekst), tekst
    assert fragment in tekst
    assert baza.wiersz("SELECT count(*) AS n FROM frezowania")["n"] == 0
    for nazwa in (PLIK_A, PLIK_B, PLIK_C, "x.stl", "zly.csv"):
        assert nazwa not in tekst  # komunikat bez nazw plikow (nazwiska)


def test_csv_brak_pliku_komunikat_bez_sciezki(tmp_path, baza):
    with pytest.raises(W.BladWspolczynnikow) as e:
        W.wczytaj_do_bazy(baza, tmp_path / "Testowski" / "brak.csv", teraz=TERAZ)
    assert "Testowski" not in str(e.value) and "brak" in str(e.value)


# --- wpis reczny raz na krazek (K7) ----------------------------------------------------------------------------------
def test_wpis_reczny_raz_na_krazek(baza):
    i1 = W.wpisz_reczny(baza, "K-7", 1.23, operator=OPERATOR, teraz=TERAZ)
    w = baza.wiersz("SELECT * FROM frezowania WHERE id = ?", (i1,))
    assert (w["plik_w_raporcie"], w["projekt_id"], w["krazek"], w["zrodlo"], w["data"], w["raport_plik"]) == (
        None, None, "K-7", "reczny", "2026-11-17", None)
    assert w["wspolczynnik"] == pytest.approx(1.23) and w["wczytano"] == TERAZ.isoformat()
    assert W.wpisz_reczny(baza, " k-7 ", 1.23, operator=OPERATOR, teraz=TERAZ) == i1  # to samo drugi raz: bez nowego wiersza
    with pytest.raises(W.BladWspolczynnikow) as e:
        W.wpisz_reczny(baza, "K-7", 1.25, operator=OPERATOR, teraz=TERAZ)  # inna wartosc bez potwierdzenia: odmowa
    assert "K-7" in str(e.value) and "1,2300" in str(e.value)
    assert baza.wiersz("SELECT wspolczynnik FROM frezowania WHERE id = ?", (i1,))["wspolczynnik"] == pytest.approx(1.23)
    assert W.wpisz_reczny(baza, "K-7", 1.25, operator=OPERATOR, teraz=TERAZ, zmien=True) == i1  # potwierdzona zmiana: ten sam wiersz
    assert baza.wiersz("SELECT wspolczynnik FROM frezowania WHERE id = ?", (i1,))["wspolczynnik"] == pytest.approx(1.25)
    pozniej = TERAZ + dt.timedelta(days=2)
    assert W.wpisz_reczny(baza, "K-7", 1.25, operator=OPERATOR, teraz=pozniej) == i1  # ta sama wartosc innego dnia: nic nowego
    i2 = W.wpisz_reczny(baza, "K-7", 1.26, operator=OPERATOR, teraz=pozniej, zmien=True)  # zmiana innego dnia: nowy wiersz (historia)
    assert i2 != i1
    assert W.wspolczynnik_krazka(baza, "k-7")["wspolczynnik"] == pytest.approx(1.26)
    assert baza.wiersz("SELECT count(*) AS n FROM frezowania WHERE krazek = 'K-7'")["n"] == 2
    assert baza.wiersz("SELECT count(*) AS n FROM frezowania WHERE krazek = 'K-7' AND data = '2026-11-17'")["n"] == 1
    zd = baza.wiersze("SELECT dane FROM zdarzenia WHERE zrodlo = 'pula' AND typ = 'wspolczynnik_reczny'")
    assert len(zd) == 3


@pytest.mark.parametrize("krazek, wsp", [("", 1.23), ("   ", 1.23), ("K-1", 2.5), ("K-1", 0.0), ("K-1", float("nan")), ("K-1", "1,2x"),
                                         (None, 1.23), ("K-1", None)])
def test_wpis_reczny_zle_dane_odmowa(baza, krazek, wsp):
    with pytest.raises(W.BladWspolczynnikow):
        W.wpisz_reczny(baza, krazek, wsp, operator=OPERATOR, teraz=TERAZ)
    assert baza.wiersz("SELECT count(*) AS n FROM frezowania")["n"] == 0


def test_wpis_reczny_tekst_z_okna_z_przecinkiem_i_data_podana(baza):
    i = W.wpisz_reczny(baza, "K-8", " 1,2345 ", data="2026-11-16", operator=OPERATOR, teraz=TERAZ)
    w = baza.wiersz("SELECT wspolczynnik, data FROM frezowania WHERE id = ?", (i,))
    assert w["wspolczynnik"] == pytest.approx(1.2345) and w["data"] == "2026-11-16"


def test_wpis_reczny_na_3_zmianie_nalezy_do_doby_i_najnowszy_wygrywa_w_puli(baza, wieczor):
    cel, _ = wieczor
    i = W.wpisz_reczny(baza, "K-4", 1.241, operator=OPERATOR, teraz=dt.datetime(2026, 11, 18, 2, 0))
    assert baza.wiersz("SELECT data FROM frezowania WHERE id = ?", (i,))["data"] == "2026-11-17"
    p = P.pula_wieczorna(baza, TERAZ)
    assert ("Probna 3301 kor/" + PLIK_C, 1.241, "K-4", "reczny") in wpisy(p, cel)
    W.wpisz_reczny(baza, "K-3", 1.239, operator=OPERATOR, teraz=TERAZ + dt.timedelta(days=1), zmien=True)
    assert ("Testowski 3263 zs/" + PLIK_B, 1.239, "K-3", "reczny") in wpisy(P.pula_wieczorna(baza, TERAZ), cel)


def test_krazki_dnia_lista_do_wpisu_recznego(baza, wieczor):
    W.wpisz_reczny(baza, "K-9", 1.22, operator=OPERATOR, teraz=TERAZ)  # krazek z wpisem, bez plikow w CSV
    k = {x["krazek"]: x for x in P.krazki(baza, TERAZ)}
    assert set(k) == {"K-1", "K-2", "K-3", "K-4", "K-5", "K-6", "K-9"}
    assert (k["K-1"]["plikow"], k["K-1"]["wspolczynniki_csv"], k["K-1"]["brakuje"]) == (2, [1.221], False)
    assert (k["K-3"]["plikow_bez_wspolczynnika"], k["K-3"]["wspolczynnik_reczny"], k["K-3"]["brakuje"]) == (1, 1.235, False)
    assert (k["K-4"]["plikow_bez_wspolczynnika"], k["K-4"]["wspolczynnik_reczny"], k["K-4"]["brakuje"]) == (1, None, True)
    assert (k["K-9"]["plikow"], k["K-9"]["wspolczynnik_reczny"]) == (0, 1.22)
    assert [x["krazek"] for x in P.krazki(baza, TERAZ) if x["brakuje"]] == ["K-4"]


# --- sciezki do wczytania, ustawienia i kontrakt z session ----------------------------------------------------------
def test_sciezki_plikow_wpisow_tylko_do_wczytania_siatki(baza, wieczor):
    cel, _ = wieczor
    p = P.pula_wieczorna(baza, TERAZ)
    s = P.sciezki_plikow(baza, p.wpisy, zrodla(cel))
    assert set(s) == {w.projekt_id for w in p.wpisy}
    for w in p.wpisy:
        assert s[w.projekt_id].is_file() and S.skrot_pliku(s[w.projekt_id]) == w.sha16
    assert P.sciezki_plikow(baza, p.wpisy, {"cyrkon": None, "prywatne": None}) == {}


def test_wspolczynniki_jednoznaczne_dla_obecnego_silnika(baza, wieczor):
    cel, _ = wieczor
    p = P.pula_wieczorna(baza, TERAZ)
    jedn = p.wspolczynniki()
    b_sha = sha(cel, "Cyrkon", "Testowski 3263 zs", PLIK_B)
    a_sha = sha(cel, "Cyrkon", "Testowski 3263 zs", PLIK_A)
    assert jedn[b_sha] == pytest.approx(1.235) and a_sha not in jedn  # A ma dwa rozne wspolczynniki
    assert p.liczniki["sha16_z_kilkoma_wspolczynnikami"] == 2  # A i Fikcyjny


def ustawienia_tmp(tmp_path: Path, cel: Path, millbox: Path) -> dict:
    tekst = (STANOWISKO / "ustawienia.przyklad.toml").read_text(encoding="utf-8")
    for klucz, wartosc in (("folder_cyrkon", cel / "Cyrkon"), ("folder_prywatne", cel / "Prywatne"), ("folder_millbox", millbox),
                           ("baza", tmp_path / "dane" / "z_ustawien.sqlite")):
        tekst, n = re.subn(rf"(?m)^{klucz}\s*=.*$", f'{klucz} = "{Path(wartosc).as_posix()}"', tekst, count=1)
        assert n == 1, klucz
    plik = tmp_path / "ustawienia.toml"
    plik.write_text(tekst, encoding="utf-8")
    return UST.wczytaj_ustawienia(plik)


def test_katalog_pul_z_ustawien_odswiez_i_pule(tmp_path):
    cel = tmp_path / "drzewo"
    zbuduj_foldery(cel, FOLDERY)
    millbox = tmp_path / "millbox"
    zapisz_csv(millbox / "wspolczynniki.csv", CSV_WIECZOR)
    ust = ustawienia_tmp(tmp_path, cel, millbox)
    kat = P.KatalogPul.z_ustawien(ust)
    try:
        assert (kat.dni_wieczor, kat.dni_rano, kat.usun_po_dniach, kat.granica_doby_godz) == (2, 4, 10, 6)
        o = kat.odswiez(TERAZ)
        assert o["indeks"]["nowe"] == 6 and o["csv"]["nowe"] == 9 and o["csv_plik"] == "jest"
        kat.wpisz_wspolczynnik("K-3", 1.235, operator=OPERATOR, teraz=TERAZ)
        assert wpisy(kat.pula_wieczorna(TERAZ), cel) == OCZEKIWANA_17
        assert len(kat.pula_poranna(TERAZ).wpisy) == 5  # zlecenie z 10.11 poza 4 dniami roboczymi
        assert [x["krazek"] for x in kat.krazki(TERAZ) if x["brakuje"]] == ["K-4"]
        assert set(kat.sciezki(kat.pula_wieczorna(TERAZ).wpisy).values()) <= set(cel.rglob("*.stl"))
        (millbox / "wspolczynniki.csv").unlink()
        o = kat.odswiez(TERAZ)  # brak pliku CSV to nie blad (DW6: CSV albo wpis reczny)
        assert o["csv_plik"] == "brak" and o["csv"] is None
        zapisz_csv(millbox / "wspolczynniki.csv", ["x.stl;K-1;1,2x;2026-11-17"])
        o = kat.odswiez(TERAZ)  # zly CSV: indeks odswiezony, blad CSV w wyniku (z numerem linii), bez wyjatku
        assert o["csv_plik"] == "blad" and "linia 2" in o["csv_blad"] and o["indeks"] is not None
    finally:
        kat.zamknij()


def test_kontrakt_session_frezowanie_id_z_wpisu_daje_krazek_na_liscie(tmp_path, baza, wieczor):
    cel, _ = wieczor
    p = P.pula_wieczorna(baza, TERAZ)
    wpis = next(w for w in p.wpisy if w.krazek == "K-2")
    dane = Path(__file__).resolve().parent / "dane_sesji"
    wynik = json.loads((dane / "wynik_plytka1.json").read_text(encoding="ascii"))
    zdarzenie = json.loads((dane / "zdarzenia.json").read_text(encoding="ascii"))["wynik_plytka1"]
    g = wynik["gniazda"][0]
    g["kandydaci"][0]["id"] = wpis.sha16
    g["kandydaci"][0]["frezowanie_id"] = wpis.frezowanie_id
    s = SE.Sesja(baza, operatorzy=["Technik A"], katalog_wynikow=tmp_path / "wyniki", zegar=lambda: dt.datetime(2026, 11, 17, 20, 30))
    s.wybierz_operatora("Technik A")
    skan_id = s.przyjmij_wynik(zdarzenie, wynik)
    praca_id = baza.wiersz("SELECT id FROM prace WHERE skan_id = ? AND gniazdo = ?", (skan_id, g["gniazdo"]))["id"]
    s.ukruszona(praca_id)
    poz = [x for x in s.do_dofrezowania() if x["sha16"] == wpis.sha16]
    assert [(x["kuweta"], x["zeby"], x["krazek"]) for x in poz] == [("3263", "14", "K-2")]


# --- kryterium 6: zero nazw folderow i plikow zlecen poza czterema tabelami -------------------------------------------
NAZWISKO = "Testowski"


def _teksty_wyjatku(e: BaseException) -> list[str]:
    return [str(e), repr(e), "".join(traceback.format_exception(e))]


def test_kryterium6_zero_nazwisk_poza_czterema_tabelami(tmp_path, baza, caplog, capsys, recwarn, monkeypatch):
    caplog.set_level(logging.DEBUG)
    cel = tmp_path / "drzewo"
    t = dt.datetime(2026, 11, 16, 12)
    zbuduj_foldery(cel, {
        ("Cyrkon", f"{NAZWISKO} 3263 zs"): {f"2026-11-16_{NAZWISKO.lower()}-14-crown_cad.stl": t, f"{NAZWISKO} 15.stl": t},
        ("Cyrkon", f"{NAZWISKO} J.3301"): {f"2026-11-16_{NAZWISKO.lower()}-36-crown_cad.stl": t},
        ("Cyrkon", f"{NAZWISKO} bez numeru"): {f"{NAZWISKO} 46.stl": t},
        ("Prywatne", f"#1234 {NAZWISKO}"): {f"2026-11-16_{NAZWISKO.lower()}-11-crown_cad.stl": t},
    })
    zly = cel / "Cyrkon" / f"{NAZWISKO} 3263 zs" / f"2026-11-16_{NAZWISKO.lower()}-12-crown_cad.stl"
    zly.write_bytes(b"solid zly\nto nie jest siatka\n")
    D.zapisz_stl(D.atrapa(np.random.default_rng(1)), cel / "Cyrkon" / f"{NAZWISKO} 3263 zs" / NAZWISKO / "21.stl", t)
    teksty, wyjatki = [], []
    oryginal = I._wpisy_folderu

    def zepsuty_folder(sciezka):
        if "J.3301" in str(sciezka):
            raise PermissionError(13, "odmowa dostepu", str(sciezka))
        return oryginal(sciezka)

    monkeypatch.setattr(I, "_wpisy_folderu", zepsuty_folder)
    r = I.indeksuj(baza, zrodla(cel), TERAZ)
    assert r.bledy == 2  # zly STL i folder bez dostepu
    monkeypatch.setattr(I, "_wpisy_folderu", oryginal)
    r2 = I.indeksuj(baza, zrodla(cel), TERAZ)
    teksty += [repr(r), json.dumps(r.do_slownika()), repr(r2), json.dumps(r2.do_slownika())]

    plik_csv = tmp_path / "millbox" / "wspolczynniki.csv"
    zapisz_csv(plik_csv, [f"2026-11-16_{NAZWISKO.lower()}-14-crown_cad.stl;K-1;1,22;2026-11-17",
                          f"{NAZWISKO} 3263 zs/{NAZWISKO} 15.stl;K-2;;2026-11-17",
                          f"2026-11-16_{NAZWISKO.lower()}-99-crown_cad.stl;K-1;1,22;2026-11-17"])
    rc = W.wczytaj_do_bazy(baza, plik_csv, teraz=TERAZ)
    teksty += [repr(rc), json.dumps(rc.do_slownika()), repr(W.powiaz_frezowania(baza))]
    for wiersze in ([f"{NAZWISKO} 15.stl;K-1;1,2x;2026-11-17"], [f"{NAZWISKO} 15.stl;K-1;1,22;2026-13-01"],
                    [f"{NAZWISKO} 15.stl;K-1"], [f"{NAZWISKO} 15.stl;;;2026-11-17"],
                    [f"{NAZWISKO} 15.stl;K-1;1,22;2026-11-17", f"{NAZWISKO} 15.stl;K-1;1,25;2026-11-17"]):
        with pytest.raises(W.BladWspolczynnikow) as e:
            W.wczytaj_do_bazy(baza, zapisz_csv(tmp_path / NAZWISKO / f"{NAZWISKO}.csv", wiersze), teraz=TERAZ)
        wyjatki.append(e.value)
    with pytest.raises(W.BladWspolczynnikow) as e:
        W.wczytaj_do_bazy(baza, tmp_path / NAZWISKO / "brak.csv", teraz=TERAZ)
    wyjatki.append(e.value)
    W.wpisz_reczny(baza, "K-2", 1.23, operator=OPERATOR, teraz=TERAZ)
    with pytest.raises(W.BladWspolczynnikow) as e:
        W.wpisz_reczny(baza, "K-2", 1.24, operator=OPERATOR, teraz=TERAZ)
    wyjatki.append(e.value)

    pw, pp, kr = P.pula_wieczorna(baza, TERAZ), P.pula_poranna(baza, TERAZ), P.krazki(baza, TERAZ)
    assert len(pw.wpisy) == 2 and len(pp.wpisy) >= 3  # dane naprawde przeszly przez pule
    kat = P.KatalogPul(baza, zrodla(cel), plik_csv=plik_csv)
    o = kat.odswiez(TERAZ)
    zapisz_csv(plik_csv, [f"{NAZWISKO} 15.stl;K-1;1,2x;2026-11-17"])
    o2 = kat.odswiez(TERAZ)
    teksty += [repr(pw), json.dumps(pw.do_slownika()), repr(pp), json.dumps(pp.do_slownika()), json.dumps(kr),
               json.dumps(o, default=str), json.dumps(o2, default=str), repr([dataclasses.asdict(w) for w in pw.wpisy + pp.wpisy])]
    for e in wyjatki:
        teksty += _teksty_wyjatku(e)
    teksty += [rec.getMessage() for rec in caplog.records] + [str(w.message) for w in recwarn]
    wyjscie = capsys.readouterr()
    teksty += [wyjscie.out, wyjscie.err]
    trafienia = [x for x in teksty if NAZWISKO.casefold() in x.casefold()]
    assert trafienia == []

    # baza: nazwisko tylko w kolumnach z nazwami czterech tabel (KOLUMNY_Z_NAZWAMI), dziennik bez nazwisk
    for tabela in B.TABELE:
        dozwolone = B.KOLUMNY_Z_NAZWAMI.get(tabela, ())
        for w in baza.wiersze(f"SELECT * FROM {tabela}"):
            for kol, wart in w.items():
                if kol not in dozwolone and isinstance(wart, (str, bytes)):
                    tekst = wart.decode("latin-1") if isinstance(wart, bytes) else wart
                    assert NAZWISKO.casefold() not in tekst.casefold(), (tabela, kol)
    assert baza.wiersz("SELECT count(*) AS n FROM zdarzenia WHERE zrodlo = 'pula'")["n"] >= 5
    # kontrola: dane testowe naprawde mialy nazwisko w dozwolonych kolumnach
    assert baza.wiersz("SELECT count(*) AS n FROM zlecenia WHERE folder LIKE ?", (f"%{NAZWISKO}%",))["n"] == 4
    assert baza.wiersz("SELECT count(*) AS n FROM frezowania WHERE plik_w_raporcie LIKE ?", (f"%{NAZWISKO}%",))["n"] == 3


# --- runda 2 recenzji PR #18: P2, P3, P4, D3, D4, D7, D8 i decyzje robocze 4, 5, 7 ------------------------------------
def klucze(pula: P.Pula) -> list[tuple]:
    return sorted((w.sha16, round(w.wspolczynnik, 4), w.krazek, w.zrodlo_wspolczynnika) for w in pula.wpisy)


def zaindeksuj(baza, cel: Path, foldery: dict, seed: int = 0, usun_po_dniach: int = 10) -> None:
    zbuduj_foldery(cel, foldery, seed)
    I.indeksuj(baza, zrodla(cel), TERAZ, usun_po_dniach=usun_po_dniach, licz_cechy=False)


def id_projektu(baza, folder: str) -> int:
    return baza.wiersz("SELECT p.id FROM projekty p JOIN zlecenia z ON z.id = p.zlecenie_id WHERE z.folder = ?", (folder,))["id"]


def test_p2_powiazanie_przeliczane_gdy_wlasciwy_plik_pozniej_w_indeksie(tmp_path, baza):
    """S1 recenzji: wiersz z sama nazwa pliku wczytany, gdy w indeksie byl tylko plik o tej nazwie w starszym folderze;
    wlasciwy folder pojawia sie pozniej (opoznienie OneDrive). Po odswiezeniu pula wskazuje nowy folder - jak na swiezej bazie."""
    cel = tmp_path / "drzewo"
    zbuduj_foldery(cel, {("Cyrkon", "Atrapowicz 512 Jan"): {"zab 46.stl": dt.datetime(2026, 11, 10, 12)}}, seed=0)
    csv = zapisz_csv(tmp_path / "millbox" / "wspolczynniki.csv", ["zab 46.stl;K-6;1,2400;2026-11-17"])
    kat = P.KatalogPul(baza, zrodla(cel), plik_csv=csv, licz_cechy=False)
    kat.odswiez(TERAZ)
    assert baza.wiersz("SELECT projekt_id FROM frezowania")["projekt_id"] == id_projektu(baza, "Atrapowicz 512 Jan")
    zbuduj_foldery(cel, {("Cyrkon", "Fikcyjny 0412"): {"zab 46.stl": dt.datetime(2026, 11, 16, 12)}}, seed=1)
    o = kat.odswiez(TERAZ)
    p = kat.pula_wieczorna(TERAZ)
    assert [w.sha16 for w in p.wpisy] == [sha(cel, "Cyrkon", "Fikcyjny 0412", "zab 46.stl")]
    assert baza.wiersz("SELECT projekt_id FROM frezowania")["projekt_id"] == id_projektu(baza, "Fikcyjny 0412")
    assert o["powiazanie"]["zmienione"] == 1
    b2 = B.otworz(tmp_path / "dane2" / "swieza.sqlite")  # swieza baza, ten sam stan folderow i pliku CSV
    try:
        k2 = P.KatalogPul(b2, zrodla(cel), plik_csv=csv, licz_cechy=False)
        k2.odswiez(TERAZ)
        assert klucze(k2.pula_wieczorna(TERAZ)) == klucze(p)
    finally:
        b2.zamknij()


def test_p3_poprawka_wiersza_w_csv_usuwa_stary_wiersz_z_puli(tmp_path, baza):
    cel = tmp_path / "drzewo"
    zaindeksuj(baza, cel, FOLDERY)
    a, c = sha(cel, "Cyrkon", "Testowski 3263 zs", PLIK_A), sha(cel, "Cyrkon", "Probna 3301 kor", PLIK_C)
    csv = tmp_path / "millbox" / "wspolczynniki.csv"
    W.wczytaj_do_bazy(baza, zapisz_csv(csv, [f"{PLIK_A};K-1;1,2500;2026-11-17", f"{PLIK_B};K-3;1,2300;2026-11-16"]), teraz=TERAZ)
    # literowka w krazku poprawiona w pliku (zmienia sie klucz plik + krazek + data): stary wiersz wypada z puli
    r = W.wczytaj_do_bazy(baza, zapisz_csv(csv, [f"{PLIK_A};K-2;1,2000;2026-11-17", f"{PLIK_B};K-3;1,2300;2026-11-16"]), teraz=TERAZ)
    assert (r.nowe, r.nieaktualne, r.bez_zmian) == (1, 1, 1)
    p = P.pula_wieczorna(baza, TERAZ)
    assert [(round(w.wspolczynnik, 4), w.krazek) for w in p.wpisy if w.sha16 == a] == [(1.2, "K-2")]
    assert p.wspolczynniki()[a] == pytest.approx(1.2)
    assert [x["krazek"] for x in P.krazki(baza, TERAZ)] == ["K-2", "K-3"]
    stary = baza.wiersz("SELECT * FROM frezowania WHERE krazek = 'K-1'")
    assert stary["zrodlo"] == W.ZRODLO_CSV_NIEAKTUALNY and stary["projekt_id"] is None  # w bazie zostaje, oznaczony
    # pomylka nazwy pliku (b zamiast c) poprawiona: w puli tylko plik naprawde frezowany
    r = W.wczytaj_do_bazy(baza, zapisz_csv(csv, [f"{PLIK_A};K-2;1,2000;2026-11-17", f"{PLIK_C};K-3;1,2300;2026-11-16"]), teraz=TERAZ)
    assert (r.nowe, r.nieaktualne) == (1, 1)
    assert P.pula_wieczorna(baza, TERAZ).sha16() == {a, c}
    # wiersz wraca do pliku: ten sam wiersz bazy znow aktualny
    r = W.wczytaj_do_bazy(baza, zapisz_csv(csv, [f"{PLIK_A};K-1;1,2500;2026-11-17", f"{PLIK_C};K-3;1,2300;2026-11-16"]), teraz=TERAZ)
    assert (r.nowe, r.przywrocone, r.nieaktualne) == (0, 1, 1)
    assert baza.wiersz("SELECT zrodlo, projekt_id FROM frezowania WHERE id = ?", (stary["id"],)) == {
        "zrodlo": "csv", "projekt_id": id_projektu(baza, "Testowski 3263 zs")}
    # dni nieobecne w pliku (plik wyczyszczony rano) zostaja
    r = W.wczytaj_do_bazy(baza, zapisz_csv(csv, [f"{PLIK_C};K-4;1,2100;2026-11-18"]), teraz=TERAZ)
    assert r.nieaktualne == 0
    assert klucze(P.pula_wieczorna(baza, TERAZ)) == sorted([(a, 1.25, "K-1", "csv"), (c, 1.23, "K-3", "csv"), (c, 1.21, "K-4", "csv")])


def test_p4_dwa_rozne_wspolczynniki_krazka_tej_samej_doby_sprzeczne(tmp_path, baza):
    cel = tmp_path / "drzewo"
    zaindeksuj(baza, cel, FOLDERY)
    csv = zapisz_csv(tmp_path / "millbox" / "wspolczynniki.csv",
                     [f"{PLIK_A};K-1;1,2210;2026-11-17", f"{PLIK_B};K-1;1,2120;2026-11-17", f"{PLIK_C};K-2;1,2300;2026-11-17"])
    W.wczytaj_do_bazy(baza, csv, teraz=TERAZ)
    p = P.pula_wieczorna(baza, TERAZ)
    assert [w.krazek for w in p.wpisy] == ["K-2"]  # prace K-1 nie dostaja zadnego z dwoch wspolczynnikow
    assert (p.liczniki["sprzeczne_wspolczynniki"], p.liczniki["krazki_sprzeczne"]) == (2, ["K-1"])
    k = {x["krazek"]: x for x in P.krazki(baza, TERAZ)}
    assert (k["K-1"]["sprzeczne"], k["K-2"]["sprzeczne"], k["K-1"]["wspolczynniki_csv"]) == (True, False, [1.212, 1.221])
    o = P.KatalogPul(baza, zrodla(cel), plik_csv=csv, licz_cechy=False).odswiez(TERAZ)
    assert (o["sprzeczne_wspolczynniki"], o["krazki_sprzeczne"]) == (2, ["K-1"])
    assert "Testowski" not in json.dumps(o, default=str)
    # czlowiek rozstrzyga wpisem recznym z potwierdzeniem (zmien=True): obie prace dostaja ten wspolczynnik
    W.wpisz_reczny(baza, "K-1", "1,2210", zmien=True, operator=OPERATOR, teraz=TERAZ)
    p = P.pula_wieczorna(baza, TERAZ)
    assert sorted((w.krazek, round(w.wspolczynnik, 4), w.zrodlo_wspolczynnika) for w in p.wpisy) == [
        ("K-1", 1.221, "reczny"), ("K-1", 1.221, "reczny"), ("K-2", 1.23, "csv")]
    assert (p.liczniki["sprzeczne_wspolczynniki"], p.liczniki["krazki_sprzeczne"]) == (0, [])
    # wiersz CSV zmieniony PO rozstrzygnieciu = nowa informacja, znow sprzeczne
    pozniej = TERAZ + dt.timedelta(minutes=10)
    W.wczytaj_do_bazy(baza, zapisz_csv(csv, [f"{PLIK_A};K-1;1,2210;2026-11-17", f"{PLIK_B};K-1;1,2150;2026-11-17",
                                             f"{PLIK_C};K-2;1,2300;2026-11-17"]), teraz=pozniej)
    assert P.pula_wieczorna(baza, pozniej).liczniki["krazki_sprzeczne"] == ["K-1"]


def test_p4_csv_kontra_wpis_reczny_sprzeczne_az_do_potwierdzenia(tmp_path, baza):
    cel = tmp_path / "drzewo"
    zaindeksuj(baza, cel, FOLDERY)
    csv = zapisz_csv(tmp_path / "millbox" / "wspolczynniki.csv",
                     [f"{PLIK_A};K-1;1,2210;2026-11-17", f"{PLIK_B};K-1;;2026-11-16", f"{PLIK_C};K-2;1,2300;2026-11-17"])
    W.wczytaj_do_bazy(baza, csv, teraz=TERAZ)
    W.wpisz_reczny(baza, "K-1", 1.25, operator=OPERATOR, teraz=TERAZ)  # inny niz w CSV (S7 recenzji: wczesniej po cichu CSV)
    p = P.pula_wieczorna(baza, TERAZ)
    assert [w.krazek for w in p.wpisy] == ["K-2"]  # obie prace krazka bez wspolczynnika (takze ta z pustym polem w CSV)
    assert (p.liczniki["sprzeczne_wspolczynniki"], p.liczniki["krazki_sprzeczne"], p.liczniki["bez_wspolczynnika"]) == (2, ["K-1"], 0)
    W.wpisz_reczny(baza, "K-1", 1.25, operator=OPERATOR, teraz=TERAZ)  # ta sama wartosc bez potwierdzenia nic nie rozstrzyga
    assert P.pula_wieczorna(baza, TERAZ).liczniki["krazki_sprzeczne"] == ["K-1"]
    assert P.pula_wieczorna(baza, TERAZ, wspolczynnik_awaryjny=1.22).liczniki["krazki_sprzeczne"] == ["K-1"]
    W.wpisz_reczny(baza, "K-1", 1.25, zmien=True, operator=OPERATOR, teraz=TERAZ + dt.timedelta(minutes=5))
    p = P.pula_wieczorna(baza, TERAZ)
    assert sorted((w.krazek, round(w.wspolczynnik, 4), w.zrodlo_wspolczynnika) for w in p.wpisy) == [
        ("K-1", 1.25, "reczny"), ("K-1", 1.25, "reczny"), ("K-2", 1.23, "csv")]
    assert p.liczniki["krazki_sprzeczne"] == []


def test_p4_wpis_reczny_starszy_niz_wazny_dni_nie_obowiazuje(tmp_path, baza):
    cel = tmp_path / "drzewo"
    zaindeksuj(baza, cel, FOLDERY)
    W.wczytaj_do_bazy(baza, zapisz_csv(tmp_path / "w.csv", [f"{PLIK_B};K-3;;2026-11-16"]), teraz=TERAZ)
    W.wpisz_reczny(baza, "K-3", 1.235, operator=OPERATOR, teraz=dt.datetime(2026, 9, 1, 10))  # wpis sprzed 2,5 miesiaca
    p = P.pula_wieczorna(baza, TERAZ)
    assert (len(p.wpisy), p.liczniki["bez_wspolczynnika"], p.liczniki["krazki_bez_wspolczynnika"]) == (0, 1, ["K-3"])
    k = P.krazki(baza, TERAZ)[0]
    assert (k["krazek"], k["brakuje"], k["wspolczynnik_reczny"], k["data_recznego"]) == ("K-3", True, 1.235, "2026-09-01")
    # nowy wpis (stary juz nie obowiazuje - inna wartosc bez potwierdzenia przyjeta): 7 dni przed frezowaniem obowiazuje
    W.wpisz_reczny(baza, "K-3", 1.24, operator=OPERATOR, teraz=dt.datetime(2026, 11, 9, 10))
    assert klucze(P.pula_wieczorna(baza, TERAZ)) == [(sha(cel, "Cyrkon", "Testowski 3263 zs", PLIK_B), 1.24, "K-3", "reczny")]
    assert P.krazki(baza, TERAZ)[0]["brakuje"] is False
    assert P.pula_wieczorna(baza, TERAZ, wazny_dni=6).liczniki["bez_wspolczynnika"] == 1
    assert P.krazki(baza, TERAZ, wazny_dni=6)[0]["brakuje"] is True


def test_d3_swieza_baza_stary_folder_z_wiersza_csv_w_oknie_doindeksowany(tmp_path, baza):
    cel = tmp_path / "drzewo"
    zbuduj_foldery(cel, {("Cyrkon", "Atrapowicz 512 Jan"): {"zab 46.stl": dt.datetime(2026, 11, 1, 12)},  # 16 dni
                         ("Cyrkon", "Probna 3301 kor"): {PLIK_C: dt.datetime(2026, 11, 16, 13)},
                         ("Cyrkon", "Wzorcowy 77 stary"): {"zab 47.stl": dt.datetime(2026, 11, 1, 12)}})
    csv = zapisz_csv(tmp_path / "millbox" / "wspolczynniki.csv",
                     ["zab 46.stl;K-6;1,2400;2026-11-17", f"{PLIK_C};K-4;1,2300;2026-11-17"])  # dofrezowanie starej pracy
    kat = P.KatalogPul(baza, zrodla(cel), plik_csv=csv, licz_cechy=False)
    o = kat.odswiez(TERAZ)
    p = kat.pula_wieczorna(TERAZ)
    assert (p.liczniki["brakujace"], len(p.wpisy)) == (0, 2)
    assert (o["indeks"]["stare_doindeksowane"], o["indeks"]["pominiete_stare"]) == (1, 1)  # "Wzorcowy" nadal nieczytany


def test_d4_sciezka_z_obcym_folderem_dopasowana_po_samej_nazwie(tmp_path, baza):
    cel = tmp_path / "drzewo"
    zaindeksuj(baza, cel, FOLDERY)
    W.wczytaj_do_bazy(baza, zapisz_csv(tmp_path / "w.csv", [f"C:\\MillBox\\Jobs\\{PLIK_C};K-4;1,2300;2026-11-17",
                                                            f"Testowski 3263 zs\\{PLIK_C};K-5;1,2300;2026-11-17"]), teraz=TERAZ)
    p = P.pula_wieczorna(baza, TERAZ)
    # folder spoza zlecen (MillBox) = proba po nazwie; folder zlecenia, w ktorym pliku nie ma = brakujacy (nie zgadujemy)
    assert klucze(p) == [(sha(cel, "Cyrkon", "Probna 3301 kor", PLIK_C), 1.23, "K-4", "csv")]
    assert (p.liczniki["po_samej_nazwie"], p.liczniki["brakujace"]) == (1, 1)


def test_d7_srednik_na_koncu_wiersza_i_pusta_linia_przed_naglowkiem(tmp_path):
    p = tmp_path / "w.csv"
    p.write_bytes((f"\r\n;;\r\n{NAGLOWEK};\r\n{PLIK_A};K-1;1,2210;2026-11-17;\r\n{PLIK_B};K-2;1,2300;2026-11-16;;\r\n").encode("utf-8"))
    assert [(x.linia, x.krazek) for x in W.wczytaj_csv(p, dzis=TERAZ.date())] == [(4, "K-1"), (5, "K-2")]
    zapisz_csv(p, [f"{PLIK_A};K-1;1,2210;2026-11-17;x"])  # piate pole z trescia nadal jest bledem
    with pytest.raises(W.BladWspolczynnikow) as e:
        W.wczytaj_csv(p, dzis=TERAZ.date())
    assert e.value.linie == [2] and "4 pola" in str(e.value)


@pytest.mark.parametrize("data", ["2025-11-17", "2027-11-17", "17.01.2027", "2026-09-17"])
def test_d7_data_dalej_niz_60_dni_od_dzis_to_blad_linii(tmp_path, baza, data):
    p = zapisz_csv(tmp_path / "w.csv", [f"{PLIK_A};K-1;1,22;2026-11-17", f"{PLIK_B};K-1;1,22;2026-09-18", f"{PLIK_C};K-1;1,22;{data}"])
    with pytest.raises(W.BladWspolczynnikow) as e:
        W.wczytaj_do_bazy(baza, p, teraz=TERAZ)
    assert e.value.linie == [4] and "60 dni" in str(e.value)
    assert baza.wiersz("SELECT count(*) AS n FROM frezowania")["n"] == 0


def test_d8_wpis_reczny_z_data_wsteczna_odmowa(baza):
    W.wpisz_reczny(baza, "K-7", 1.24, data="2026-11-18", operator=OPERATOR, teraz=TERAZ)
    with pytest.raises(W.BladWspolczynnikow) as e:
        W.wpisz_reczny(baza, "K-7", 1.26, data="2026-11-10", zmien=True, operator=OPERATOR, teraz=TERAZ)
    assert "K-7" in str(e.value) and "2026-11-18" in str(e.value)
    assert baza.wiersz("SELECT count(*) AS n FROM frezowania WHERE krazek = 'K-7'")["n"] == 1
    assert W.wspolczynnik_krazka(baza, "K-7")["wspolczynnik"] == pytest.approx(1.24)


def test_decyzja4_prywatne_z_ostatnich_10_dni_kalendarzowych(tmp_path, baza):
    cel = tmp_path / "drzewo"
    zaindeksuj(baza, cel, {("Cyrkon", "Testowski 701"): {"zab 11.stl": dt.datetime(2026, 11, 10, 12)},
                           ("Prywatne", "#702 Probna"): {"zab 12.stl": dt.datetime(2026, 11, 10, 12)},
                           ("Prywatne", "#703 Probna"): {"zab 13.stl": dt.datetime(2026, 11, 6, 12)}}, usun_po_dniach=30)
    # 4 dni robocze od doby 17.11 = od 11.11 06:00: Cyrkon z 10.11 poza pula; Prywatne z 10.11 w 10 dniach, z 06.11 poza
    assert kuwety(P.pula_poranna(baza, TERAZ)) == {"#702"}
    assert kuwety(P.pula_poranna(baza, TERAZ, dni_prywatne=4)) == set()


def test_decyzja5_operator_wpisu_recznego_wymagany_i_w_dzienniku(baza):
    with pytest.raises(TypeError):
        W.wpisz_reczny(baza, "K-1", 1.23, teraz=TERAZ)  # bez operatora
    for zly in ("", "   ", None):
        with pytest.raises(W.BladWspolczynnikow):
            W.wpisz_reczny(baza, "K-1", 1.23, operator=zly, teraz=TERAZ)
    assert baza.wiersz("SELECT count(*) AS n FROM frezowania")["n"] == 0
    W.wpisz_reczny(baza, "K-1", 1.23, operator=" Technik  A ", teraz=TERAZ)
    zd = json.loads(baza.wiersz("SELECT dane FROM zdarzenia WHERE typ = 'wspolczynnik_reczny'")["dane"])
    assert (zd["operator"], zd["krazek"], zd["zmien"]) == ("Technik A", "K-1", False)


def test_decyzja7_okno_wieczorne_liczone_w_dniach_roboczych(tmp_path, baza):
    cel = tmp_path / "drzewo"
    zaindeksuj(baza, cel, FOLDERY)
    W.wczytaj_do_bazy(baza, zapisz_csv(tmp_path / "w.csv", [f"{PLIK_A};K-1;1,2210;2026-11-20"]), teraz=dt.datetime(2026, 11, 20, 20))
    chwile = ("2026-11-20T20:00", "2026-11-21T10:00", "2026-11-22T20:00", "2026-11-23T07:00", "2026-11-23T20:00", "2026-11-24T08:00")
    assert [len(P.pula_wieczorna(baza, dt.datetime.fromisoformat(t), dni=2).wpisy) for t in chwile] == [1, 1, 1, 1, 1, 0]
    p = P.pula_wieczorna(baza, dt.datetime(2026, 11, 23, 20), dni=2)  # poniedzialek: piatek w puli, weekend nie zuzywa okna
    assert (p.od, p.do) == ("2026-11-20T06:00:00", "2026-11-24T06:00:00")
    assert [x["krazek"] for x in P.krazki(baza, dt.datetime(2026, 11, 23, 20), dni=2)] == ["K-1"]
    # dzien wolny w tygodniu (gdyby wlasciciel podal kalendarz swiat - decyzja 3: dzis pusty): tez nie zuzywa okna
    assert len(P.pula_wieczorna(baza, dt.datetime(2026, 11, 24, 20), dni=2, wolne={dt.date(2026, 11, 23)}).wpisy) == 1
