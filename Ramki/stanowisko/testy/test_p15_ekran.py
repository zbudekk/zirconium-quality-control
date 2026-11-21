"""E3-P15 p. 1: komunikat ogolny, ktory przychodzi w trakcie ogladania plytki, nie moze podstawic innego gniazda pod kursor.

Komunikat ogolny (bez ``skan_id``, np. "Ten sam projekt w dwoch gniazdach") staje NAD lista plytek i mapa - mapa ogladanej
plytki przesuwa sie i maleje (99 / 75 px). Wariant paczki: geometria moze sie zmienic, ale wtedy dziala ta sama ochrona
klikniec co po zmianie zawartosci mapy (A-P2, ``okno.OCHRONA_MS``): mapa przygaszona, klikniecia mapy i skroty decyzji
pomijane - klikniecie w stary srodek gniazda nie otwiera innego gniazda. Okno offscreen na ``AtrapaKontrolera``.
Zrzuty do raportu: zmienna ``P15_ZRZUTY`` = katalog (poza repo).
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

import test_p14_ekran as P14
from stanowisko.ui import okno as OKNO

_qt = P14._qt  # ta sama aplikacja Qt offscreen i czcionka ekranu
swiat = P14.swiat
DLUGO_MS = 600_000  # ochrona nie konczy sie sama w trakcie serii klikniec testu (test nie zalezy od obciazenia PC)


def zrzut(e, nazwa: str) -> None:
    katalog = os.environ.get("P15_ZRZUTY")
    if katalog:
        Path(katalog).mkdir(parents=True, exist_ok=True)
        e.zdarzenia()
        e.okno.grab().toImage().save(str(Path(katalog) / f"{nazwa}.png"), "PNG")


def koniec_ochrony(e) -> None:
    """Ochrona konczy sie teraz (jak po ``OCHRONA_MS``); nastepna znowu trwa ``DLUGO_MS``."""
    if e.okno.ochrona_aktywna():
        e.okno._ochrona.start(1)
        e.po_ochronie()
    e.okno._ochrona.setInterval(DLUGO_MS)
    assert not e.mapa.przygaszona()


def ogolne(k) -> list:
    return [x for x in k.stan().komunikaty if x.skan_id is None and not x.ukryte]


def kliki_w_stare_srodki(e, stare: dict) -> list:
    """Klikniecie w stary srodek kazdego z 19 gniazd (punkt okna): lista (gniazdo celowane, gniazdo otwarte) dla INNYCH gniazd."""
    inne = []
    for nr, punkt in stare.items():
        P14._klik_w_punkt(e, punkt)
        otwarte = e.okno._gniazdo
        if otwarte is not None and otwarte != nr:
            inne.append((nr, otwarte))
        if otwarte is not None:
            e.okno._zamknij_prace()
            e.zdarzenia()
    return inne


def sprawdz_krok(e, przed: tuple, co: str, zrzut_ochrony: str = "") -> tuple:
    """Po zmianie komunikatow ogolnych w tle: geometria bez zmian ALBO ochrona klikniec; 0 z 19 klikniec w stare srodki
    otwiera inne gniazdo. Zwraca nowa geometrie (po koncu ochrony)."""
    e.odczekaj(60)
    ochrona = e.okno.ochrona_aktywna()
    po = P14._geometria_mapy(e)
    ruszone = [nr for nr in przed[1] if po[1][nr] != przed[1][nr]]
    if ruszone or po[0] != przed[0]:
        assert ochrona and e.mapa.przygaszona(), (f"{co}: mapa {przed[0]} -> {po[0]}, srodek zmienia {len(ruszone)} z 19 gniazd, "
                                                  "a ochrona klikniec jest nieaktywna")
    inne = kliki_w_stare_srodki(e, przed[1])
    assert not inne, f"{co}: klikniecie w stary srodek otwiera INNE gniazdo {len(inne)} z 19: {inne}"
    assert not e.jest("widok_pracy") or not ruszone
    if zrzut_ochrony:
        zrzut(e, zrzut_ochrony)  # mapa przygaszona: tak wyglada ekran przez ``OCHRONA_MS`` po dojsciu komunikatu
    koniec_ochrony(e)
    return P14._geometria_mapy(e)


@pytest.mark.parametrize("rozmiar", P14.ROZMIARY, ids=lambda r: f"{r[0]}x{r[1]}")
def test_p15_komunikat_ogolny_w_tle_nie_podstawia_innego_gniazda_pod_kursor(swiat, rozmiar):
    """Technik oglada plytke 1 i siega po gniazdo. W tle: dochodzi komunikat ogolny (konflikt projektu z nowej plytki),
    dochodzi drugi (plik zajety), oba znikaja. Za kazdym razem: mapa stoi w miejscu albo ochrona klikniec jest aktywna i
    zadne z 19 klikniec w stare srodki gniazd nie otwiera innego gniazda; komunikat widac w calosci; po koncu ochrony
    klikniecie gniazda dziala."""
    k, zegar = swiat.wieczor()
    s1 = k.symuluj_skan("zwykla", numer=1)
    e = swiat.ekran(k, rozmiar)
    e.po_ochronie()
    assert e.okno._ochrona.interval() == OKNO.OCHRONA_MS == 800
    e.okno._ochrona.setInterval(DLUGO_MS)
    r = f"{rozmiar[0]}x{rozmiar[1]}"
    g = P14._geometria_mapy(e)
    assert len(g[1]) == 19 and not ogolne(k)
    zrzut(e, f"p15_bez_komunikatu_{r}")

    zegar.przesun(2)
    k.symuluj_skan("do_powtorzenia", numer=5, projekty={1: 41, 2: 42})
    assert [x.rodzaj for x in ogolne(k)] == ["konflikt_projektu"]
    g = sprawdz_krok(e, g, "doszedl 1. komunikat ogolny", f"p15_ochrona_{r}")
    assert e.okno.pokazana_plytka() == s1 and not P14.niewidoczne_w_calosci(e, ("komunikat_konflikt_projektu",))
    zrzut(e, f"p15_po_1_komunikacie_{r}")

    zegar.przesun(2)
    k.symuluj_komunikat("plik_zajety")
    assert sorted(x.rodzaj for x in ogolne(k)) == ["konflikt_projektu", "plik_zajety"]
    g = sprawdz_krok(e, g, "doszedl 2. komunikat ogolny")
    assert not P14.niewidoczne_w_calosci(e, ("komunikat_konflikt_projektu", "komunikat_plik_zajety"))
    zrzut(e, f"p15_po_2_komunikacie_{r}")

    for kom in ogolne(k):  # znikaja w tle (kontroler), nie kliknieciem technika
        k.zamknij_komunikat(kom.id)
    assert not ogolne(k)
    g = sprawdz_krok(e, g, "komunikaty ogolne zniknely")
    assert not e.jest("komunikat_konflikt_projektu") and not e.jest("komunikat_plik_zajety")
    zrzut(e, f"p15_po_zniknieciu_{r}")

    P14._klik_w_punkt(e, g[1][9])  # po koncu ochrony mapa przyjmuje klikniecia: nowy srodek gniazda 9 otwiera gniazdo 9
    assert e.okno._gniazdo == 9 and e.jest("widok_pracy") and e.okno.pokazana_plytka() == s1


def test_p15_ochrona_po_komunikacie_ogolnym_konczy_sie_sama_i_pomija_skroty_decyzji(swiat):
    """Ochrona po dojsciu komunikatu ogolnego to ta sama ochrona A-P2: przy otwartej pracy skrot decyzji ("U") nacisniety tuz
    po przesunieciu mapy nic nie wysyla; po ``OCHRONA_MS`` ochrona konczy sie sama i decyzja dziala."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    k, zegar = swiat.wieczor()
    s1 = k.symuluj_skan("zwykla", numer=1)
    e = swiat.ekran(k, (1536, 864))
    e.klik_gniazdo(9)
    praca = e.okno._praca_widoku
    assert praca is not None
    przed = [(g.nr, g.status) for g in k.stan().plytka(s1).gniazda]
    k.symuluj_komunikat("plik_zajety")
    e.odczekaj(40)
    assert e.okno.ochrona_aktywna() and e.mapa.przygaszona()
    QTest.keyClick(e.okno, Qt.Key.Key_U)
    e.zdarzenia()
    assert [(g.nr, g.status) for g in k.stan().plytka(s1).gniazda] == przed  # skrot pominiety
    e.po_ochronie()  # konczy sie sama (800 ms)
    assert not e.mapa.przygaszona() and e.okno._praca_widoku == praca and e.okno._gniazdo == 9


def test_p15_zmiana_samego_tekstu_i_wlasne_zamkniecie_komunikatu_nie_przygaszaja_mapy(swiat):
    """Ochrona wlacza sie tylko, gdy panele nad mapa zmieniaja wysokosc w tle. Komunikat "plik zajety (od 12 s)" odswiezany co
    sekunde (ten sam panel, inny tekst) NIE przygasza mapy - inaczej mapa bylaby nieczynna przez caly czas skanowania.
    Komunikat zamkniety przez technika (jego wlasne klikniecie) tez nie - jak dotad."""
    k, zegar = swiat.wieczor()
    k.symuluj_skan("zwykla", numer=1)
    e = swiat.ekran(k, (1600, 900))
    def plik_zajety(od_s: int) -> None:  # jak ``Aplikacja``: ten sam identyfikator komunikatu, tekst z nowa liczba sekund
        k._komunikat("plik_zajety", id_="plik_zajety:skaner", od_s=od_s)
        k._odswiez()

    plik_zajety(12)
    e.odczekaj(40)
    assert e.okno.ochrona_aktywna()
    e.po_ochronie()
    g = P14._geometria_mapy(e)
    tekst = e.tekst_elementu("komunikat_plik_zajety")
    for od_s in (13, 14, 15):
        plik_zajety(od_s)
        e.odczekaj(40)
        assert len(ogolne(k)) == 1 and not e.okno.ochrona_aktywna() and not e.mapa.przygaszona()
    assert e.tekst_elementu("komunikat_plik_zajety") != tekst and "15" in e.tekst_elementu("komunikat_plik_zajety")
    assert P14._geometria_mapy(e) == g
    przycisk = e.w("komunikat_plik_zajety").findChild(type(e.w("przycisk_skanuj")), "zamknij_komunikat")
    P14._klik_w_punkt(e, przycisk.mapTo(e.okno, przycisk.rect().center()))
    e.odczekaj(40)
    assert not ogolne(k) and not e.jest("komunikat_plik_zajety") and not e.okno.ochrona_aktywna()
    assert P14._geometria_mapy(e) != g  # mapa wrocila na miejsce po decyzji technika - bez przygaszenia


def test_p15_komunikat_ogolny_bez_gniazd_na_mapie_nie_wlacza_ochrony(swiat):
    """Regula A-P2 zostaje: gdy mapa nie ma gniazd do klikniecia (nie ma jeszcze zadnej plytki), nie ma czego chronic -
    komunikat ogolny z tla nie przygasza mapy i niczego nie blokuje."""
    k, zegar = swiat.wieczor()
    e = swiat.ekran(k, (1600, 900))
    assert e.okno.pokazana_plytka() is None and not e.mapa.numery()
    k.symuluj_komunikat("plik_zajety")
    e.odczekaj(40)
    assert e.jest("komunikat_plik_zajety") and not e.okno.ochrona_aktywna() and not e.mapa.przygaszona()
