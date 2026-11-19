"""E3-A5i runda 3 - poprawki po recenzji PR #32 runda 2 (B1, D1, D6, D8). Dane FIKCYJNE, tylko tmp_path."""
from __future__ import annotations

import datetime as dt
import os
import shutil
import threading
import time
from pathlib import Path

import pytest

import test_kontroler_api as TK
import test_pula_aplikacja as T1
import test_pula_aplikacja_r2 as T2
from stanowisko import session as SE

atrapy_puli = T1.atrapy_puli


def test_r3_b1_stan_pliku_wspolczynnikow_poza_watkiem_okna(atrapy_puli, tmp_path, monkeypatch):
    """B1: ``folder_millbox`` na udziale sieciowym - ``os.stat`` stoi sekundy. Stan pliku wspolczynnikow sprawdza watek pomocniczy;
    atrapa ``stan_pliku`` blokujaca 5 s: petla ``przetworz`` bez przerwy > 200 ms, zadne wywolanie w watku okna."""
    from stanowisko import aplikacja as AP

    drzewo, millbox = atrapy_puli[0].parents[2], tmp_path / "millbox"
    T1.zapisz_csv(millbox, [(p.name, "K-120", 1.20, dt.date.today().isoformat()) for p in atrapy_puli[:2]])
    wywolania, prawdziwy = [], AP.stan_pliku

    def wolny(plik):
        wywolania.append(threading.current_thread().name)
        time.sleep(5.0)
        return prawdziwy(plik)

    monkeypatch.setattr(AP, "stan_pliku", wolny)
    k = AP.Aplikacja(T1.ustawienia_puli(tmp_path, drzewo, millbox), funkcja_analizy=T1.FUNKCJA_Z_PULA, parametry_scannera=TK.PARAMETRY_SCANNERA)
    try:
        k.start()
        przerwa, ostatni, koniec = 0.0, time.perf_counter(), time.monotonic() + 16.0
        while time.monotonic() < koniec:
            k.przetworz()
            teraz = time.perf_counter()
            przerwa, ostatni = max(przerwa, teraz - ostatni), teraz
            time.sleep(0.01)
        print(f"\n[B1] najdluzsza przerwa petli przetworz {przerwa * 1000:.0f} ms, wywolania stan_pliku: {wywolania}")
        assert "pula-plik-csv" in wywolania and "MainThread" not in wywolania and set(wywolania) <= {"pula-katalog", "pula-plik-csv"}
        assert przerwa < 0.2
        assert k.stan().pula.stan == "gotowa"
    finally:
        k.zamknij()


def test_r3_d8_nieudane_odswiezenie_ponawiane(atrapy_puli, tmp_path, monkeypatch):
    """D8: odswiezenie katalogu zakonczone bledem nie zapisuje stanu doby / pliku i jest ponawiane po ``PONOW_KATALOG_S``."""
    from stanowisko import aplikacja as AP
    from stanowisko import pula as PL

    drzewo, millbox = atrapy_puli[0].parents[2], tmp_path / "millbox"
    T1.zapisz_csv(millbox, [(p.name, "K-120", 1.20, dt.date.today().isoformat()) for p in atrapy_puli[:2]])
    monkeypatch.setattr(AP, "PONOW_KATALOG_S", 0.5)
    prawdziwe, licznik = PL.KatalogPul.odswiez, []

    def odswiez(self, teraz=None):
        licznik.append(1)
        if len(licznik) == 1:
            raise OSError("udzial sieciowy niedostepny (proba)")
        return prawdziwe(self, teraz)

    monkeypatch.setattr(PL.KatalogPul, "odswiez", odswiez)
    k = AP.Aplikacja(T1.ustawienia_puli(tmp_path, drzewo, millbox), funkcja_analizy=T1.FUNKCJA_Z_PULA, parametry_scannera=TK.PARAMETRY_SCANNERA)
    try:
        k.start()
        T1.czekaj(k, lambda: licznik and not k._liczenie_puli, "pierwsze (nieudane) odswiezenie", 60)
        assert k._doba_katalogu is None and k.stan().pula.stan == "brak_folderu"
        T1.czekaj(k, lambda: k.stan().pula.stan == "gotowa", "ponowione odswiezenie", 60)
        assert k.odswiezenia_katalogu == ["glosne", "ponowienie"] and k._doba_katalogu is not None and k._csv_katalogu is not None
    finally:
        k.zamknij()


def test_r3_d1_plytka_drugiego_typu_z_pusta_pula_ostrzezenie_przy_plytce(atrapy_puli, tmp_path):
    """D1: plytka poranna dopuszczona wieczorem, a pula poranna pusta - komunikat przy plytce (nie ciche prace szare)."""
    from stanowisko import aplikacja as AP

    drzewo, millbox = tmp_path / "drzewo", tmp_path / "millbox"
    dawno = time.time() - 30 * 86400  # zlecenia sprzed 30 dni: pula poranna pusta, wieczorna z pliku wspolczynnikow (foldery stare)
    for i, p in enumerate(atrapy_puli[:2]):
        cel = drzewo / "Cyrkon" / f"Zmyslony {3500 + i} zs" / p.name
        cel.parent.mkdir(parents=True)
        shutil.copy(p, cel)
        os.utime(cel, (dawno, dawno))
        os.utime(cel.parent, (dawno, dawno))
    (drzewo / "Prywatne").mkdir()
    T1.zapisz_csv(millbox, [(p.name, "K-120", 1.20, dt.date.today().isoformat()) for p in atrapy_puli[:2]])
    (tmp_path / "eksport").mkdir()
    k = AP.Aplikacja(T1.ustawienia_puli(tmp_path, drzewo, millbox), funkcja_analizy=T1.FUNKCJA_Z_PULA, parametry_scannera=TK.PARAMETRY_SCANNERA)
    try:
        k.start()
        T1.czekaj(k, lambda: k.stan().pula.stan == "gotowa", "pula wieczorna", 120)
        assert k._pule_wpisow[SE.TRYB_WIECZOR][0] and not k._pule_wpisow[SE.TRYB_RANO][0]
        (tmp_path / "eksport" / "poranna.stl").write_bytes(TK.plik_skanu({"uklad": "poranna", "numer": 4, "gniazda": {1: "zielony"}}))
        T1.czekaj(k, lambda: bool(k.stan().plytki), "wynik plytki porannej", 120)
        p = k.stan().plytki[0]
        kom = [x for x in k.stan().komunikaty if x.rodzaj == "pula_plytki_pusta"]  # komunikat z skan_id plytki
        assert kom and kom[0].skan_id == p.skan_id and "poranna" in kom[0].tekst
    finally:
        k.zamknij()


def test_r3_d6_cofnij_wpis_z_id_decyzji(tmp_path):
    """D6: ``cofnij_wpis`` z id cofanego wyboru - podwojne klikniecie nie cofa dwoch wyborow."""
    baza, (p1, p2), (f1, f2) = T2._baza_dwa_zlecenia(tmp_path)
    try:
        s = SE.Sesja(baza, operatorzy=["Technik A"])
        s.wybierz_operatora("Technik A")
        wpisy = [{"frezowanie_id": f1, "projekt_id": p1, "krazek": "K-1", "wspolczynnik": 1.2},
                 {"frezowanie_id": f2, "projekt_id": p2, "krazek": "K-2", "wspolczynnik": 1.2}]
        skan_id = s.przyjmij_wynik({"plik": "C:/Skany/s.stl", "sha16": "1" * 16},
                                   T1._wynik([T1._gniazdo(3, "a" * 16, projekt_id=None, frezowanie_id=None, wpisy=wpisy)]))
        praca = baza.wiersz("SELECT * FROM prace WHERE skan_id = ?", (skan_id,))
        s.wybierz_wpis(praca["id"], f1)
        d2 = s.wybierz_wpis(praca["id"], f2)
        s.cofnij_wpis(praca["id"], decyzja_id=d2)
        with pytest.raises(SE.BladSesji):
            s.cofnij_wpis(praca["id"], decyzja_id=d2)  # drugie klikniecie: obowiazuje juz K-1 - odmowa
        assert baza.wiersz("SELECT frezowanie_id FROM prace WHERE id = ?", (praca["id"],))["frezowanie_id"] == f1
        assert s.stan_wieczoru()["skany"][0]["prace"][0]["wybor_wpisu"]["wartosc"] == str(f1)
    finally:
        baza.zamknij()
