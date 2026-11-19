"""Pula per praca w programie "Stanowisko" (E3-A5i): KatalogPul -> wpisy z wspolczynnikami -> silnik (``OpisPuli.wpisy``,
``PamiecPul`` z ``match.Pula.z_wpisow`` i ``pamiec_puli``) -> sesja (przypisanie z ``kandydaci[0].projekt_id`` /
``frezowanie_id``, wybor krazka przez technika) -> stan okna (licznik puli, postep budowy).

Kryteria paczki E3-A5i:
1. prawdziwa ``Aplikacja`` + prawdziwy ``porownaj`` z puli wpisow (dane sztuczne: krazki 1,20 / 1,25, ten sam STL na obu):
   prace przypisane do wlasciwego frezowania w 100 %, wynik niejednoznaczny pokazany do wyboru, wybor zapisany z osoba
   (``test_k1_*``);
2. zimna pula: skany w trakcie budowy czekaja w kolejce silnika (regula E3-A5i), petla okna bez przerw > 200 ms (``test_k2_k3_*``);
3. restart z ciepla pamiecia: pula gotowa < 5 s (``test_k2_k3_*``);
4. ``PamiecPuli.sprzataj(dni)`` przy starcie usuwa tylko wpisy nieuzywane dluzej niz N dni (``test_k4_*``);
5. zolty z ratunku (uwaga "ratunek:") nie zamyka zlecenia rano bez potwierdzenia technika (``test_k5_*``).
Do tego: diagnostyka uchwytu ``\\KnownDlls`` po smierci procesu roboczego (recenzja PR #31 D1), moduly z DLL ladowane przy
starcie programu (A2p POTRZEBUJE 4, PR #31 D2), czyszczenie nazw plikow puli wpisow w procesie roboczym (P3 recenzji PR #25).

Dane FIKCYJNE (atrapy, zmyslone nazwy), tylko tmp_path.
"""
from __future__ import annotations

import ast
import datetime as dt
import hashlib
import json
import logging
import os
import shutil
import sqlite3
import time
import warnings
from pathlib import Path

import numpy as np
import pytest

import atrapy_koron
import test_kontroler_api as TK
from stanowisko import baza as B
from stanowisko import session as SE
from stanowisko import session_rano as SR

STANOWISKO = Path(__file__).resolve().parent.parent
FUNKCJA_Z_PULA = "test_pula_aplikacja:analiza_z_pula"
NAZWISKA = ("Testowski", "Probna", "Atrapowa", "Zmyslony")  # fikcyjne nazwiska w nazwach folderow i plikow - nie moga wyjsc poza baze
PROG_PRZERWY_S = 0.2


# ----------------------------------------------------------------------------
# pomocnicze
# ----------------------------------------------------------------------------
def analiza_z_pula(skan, foldery, plytka, ust, wspolczynnik=None, numer=None, *reszta, postep=None, **kw):
    """Udaje ``porownaj.porownaj`` z pula per praca: bierze pule z ``pula_dla`` silnika (``PamiecPul``) i oddaje sztuczny wynik
    (``kontroler_api.sztuczny_wynik``) z liczbami puli - test widzi, ze analiza dostala pule wpisow, ile wpisow i jak dlugo
    budowala sie pula w zadaniu (po przygotowaniu w tle: z pamieci procesu)."""
    from stanowisko import kontroler_api as K

    opis = TK.opis_z_pliku(skan)
    t0 = time.monotonic()
    pula = kw["pula_dla"](1.22)
    czas_puli = time.monotonic() - t0
    if postep is not None:
        postep("identyfikacja i inspekcja gniazd (match + inspect)", 0.5)
    wynik = K.sztuczny_wynik(opis.get("uklad", "wieczorna"), opis.get("numer") if numer is None else numer,
                             {int(k): v for k, v in (opis.get("gniazda") or {}).items()}, skan=Path(skan).name)
    wynik["wspolczynnik"] = None
    wynik["foldery_projektow"] = [str(f) for f in foldery]
    wynik["pula_wpisy"] = pula.opis() if getattr(pula, "per_praca", False) else None
    wynik["test_pula"] = {"per_praca": bool(getattr(pula, "per_praca", False)), "geometrii": len(pula), "czas_w_zadaniu_s": round(czas_puli, 3)}
    return wynik


def ustawienia_puli(tmp_path: Path, drzewo: Path, millbox: Path) -> dict:
    ust = TK.ustawienia_probne(tmp_path)
    ust["sciezki"]["folder_cyrkon"] = (drzewo / "Cyrkon").as_posix()
    ust["sciezki"]["folder_prywatne"] = (drzewo / "Prywatne").as_posix()
    ust["sciezki"]["folder_millbox"] = millbox.as_posix()
    ust["silnik"]["pula_wpisow"] = True
    ust["silnik"]["pamiec_linii"] = True
    return ust


def zapisz_csv(millbox: Path, wiersze: list[tuple]) -> Path:
    """Plik wspolczynnikow ``plik;krazek;wspolczynnik;data`` (decyzja wlasciciela DW6) w folderze MillBox."""
    millbox.mkdir(parents=True, exist_ok=True)
    csv = millbox / "wspolczynniki.csv"
    csv.write_text("plik;krazek;wspolczynnik;data\n" + "".join(f"{p};{k};{str(w).replace('.', ',')};{d}\n" for p, k, w, d in wiersze),
                   encoding="utf-8")
    return csv


def czekaj(k, warunek, co: str, limit_s: float = 300.0, krok=None) -> None:
    koniec = time.monotonic() + limit_s
    while not warunek():
        k.przetworz()
        if krok is not None:
            krok()
        assert time.monotonic() < koniec, f"nie doczekalem sie: {co}; pula: {k.stan().pula}; komunikaty: {[x.tekst for x in k.stan().komunikaty]}"
        time.sleep(0.02)


def frezowania(baza: B.Baza) -> list[dict]:
    return baza.wiersze("SELECT f.id, f.krazek, f.wspolczynnik, p.sha16, p.id AS projekt_id FROM frezowania f JOIN projekty p ON p.id = f.projekt_id")


# ----------------------------------------------------------------------------
# silnik: opis puli z wpisami, czyszczenie nazw
# ----------------------------------------------------------------------------
def test_opis_puli_z_wpisami_bez_sciezek_w_repr_i_zgodny_wstecz():
    from stanowisko import silnik as SI

    stary = SI.OpisPuli(foldery=("C:/pula",), wspolczynnik=1.22)
    assert not stary.per_praca and stary.wpisy == () and stary.sciezki is None
    sciezki = {7: Path("C:/Cyrkon/Testowski 3263 zs/2026-11-18_testowski-11-crown_cad.stl")}
    opis = SI.OpisPuli(wpisy=({"sha16": "a" * 16, "wspolczynnik": 1.2, "krazek": "K-1", "frezowanie_id": 3, "projekt_id": 7},), sciezki=sciezki,
                       korzenie=("C:/Cyrkon",))
    assert opis.per_praca and opis.foldery == ()
    assert "Testowski" not in repr(opis) and "testowski" not in repr(SI.ZadanieAnalizy(skan=Path("x.stl"), pula=opis))
    assert opis == SI.OpisPuli(wpisy=opis.wpisy, sciezki=dict(sciezki), korzenie=("C:/Cyrkon",))  # porownanie: ta sama pula = bez ponownej budowy


def test_czysciciel_nazw_puli_wpisow_pliki_foldery_i_sciezki(tmp_path):
    """P3 recenzji PR #25: proces roboczy z pula wpisow czysci teksty z nazw plikow puli, nazw folderow zlecen i pelnych sciezek
    pod zrodlami - bez przegladania drzewa "Cyrkon" (lista plikow z ``OpisPuli.sciezki``)."""
    from stanowisko import silnik as SI

    korzen = tmp_path / "Cyrkon"
    plik = korzen / "Testowski 3263 zs" / "2026-11-18_testowski-11-crown_cad.stl"
    plik.parent.mkdir(parents=True)
    plik.write_bytes(b"solid x\nendsolid x\n")
    sha = hashlib.sha256(plik.read_bytes()).hexdigest()[:16]
    cz = SI.CzyscicielNazw((), pliki=[plik], korzenie=[korzen])
    tekst = cz(f"pomijam projekt {plik.name}; {plik.stem} zle; folder Testowski 3263 zs; sciezka {plik}")
    assert "testowski" not in tekst.lower() and f"<projekt {sha}>" in tekst and SI.ZNACZNIK_PULI in tekst
    wynik = cz.oczysc({"status": "zielony", "uwagi": [f"zob. {plik.name}"], "skan": "skan.stl"})
    assert wynik["status"] == "zielony" and "testowski" not in json.dumps(wynik).lower()


# ----------------------------------------------------------------------------
# sesja: przypisanie z kandydata (nie po sha16), wybor krazka
# ----------------------------------------------------------------------------
def _baza_z_projektami(tmp_path: Path):
    """Dwa zlecenia z TYM SAMYM plikiem (ten sam sha16 w dwoch folderach) + trzeci projekt; frezowania na krazkach."""
    baza = B.otworz(tmp_path / "dane" / "stanowisko.sqlite")
    with baza.transakcja():
        z1 = baza.wstaw("zlecenia", zrodlo="cyrkon", folder="Testowski 3263 zs", folder_norm="testowski 3263 zs", kuweta="3263", mtime=1.0, dodano="2026-11-18T08:00:00")
        z2 = baza.wstaw("zlecenia", zrodlo="cyrkon", folder="Probna 3301 kor", folder_norm="probna 3301 kor", kuweta="3301", mtime=1.0, dodano="2026-11-18T08:00:00")
        p1 = baza.wstaw("projekty", zlecenie_id=z1, plik="a-11-crown_cad.stl", sha16="a" * 16, zeby="11", typ="crown", zaindeksowano="2026-11-18T08:00:00")
        p2 = baza.wstaw("projekty", zlecenie_id=z2, plik="a-11-crown_cad.stl", sha16="a" * 16, zeby="11", typ="crown", zaindeksowano="2026-11-18T08:00:00")
        p3 = baza.wstaw("projekty", zlecenie_id=z2, plik="b-14-crown_cad.stl", sha16="b" * 16, zeby="14", typ="crown", zaindeksowano="2026-11-18T08:00:00")
        f = {}
        for nazwa, pid, krazek, w in (("f1", p2, "K-120", 1.20), ("f2", p3, "K-120", 1.20), ("f3", p3, "K-120B", 1.20), ("f4", p3, "K-125", 1.25)):
            f[nazwa] = baza.wstaw("frezowania", projekt_id=pid, plik_w_raporcie="x.stl", krazek=krazek, wspolczynnik=w, data=f"2026-11-18_{nazwa}",
                                  zrodlo="csv", wczytano="2026-11-18T08:00:00")
    return baza, (p1, p2, p3), f


def _gniazdo(nr: int, sha: str, status: str = "zielony", **kandydat) -> dict:
    uwagi = list(kandydat.pop("_uwagi", []))
    k = {"id": sha, "zeby": ["11"], "typ": "crown", "pokrycie": 0.93 if status == "zielony" else 0.78, "rms_mm": 0.02, "metoda": "ransac", **kandydat}
    return {"gniazdo": nr, "status_fragmentu": "praca", "status": status, "pewnosc": 0.5, "czas_s": 0.5, "uwagi": uwagi,
            "kandydaci": [k], "inspekcja": {"status": "ok", "ubytki": []}, "status_gniazda": status, "skala": {"wspolczynnik_puli": 1.2, "poprawka_proc": 0.0}}


def _wynik(gniazda: list, uklad: str = "wieczorna", numer: int = 1) -> dict:
    zajete = {g["gniazdo"] for g in gniazda}
    return {"skan": "skan.stl", "plytka": uklad, "plytka_wybor": "auto", "uklad_zgodny": True, "wspolczynnik": None, "numer": numer,
            "numer_zrodlo": "dolki", "gniazda": gniazda, "gniazda_puste": [i for i in range(1, 25) if i not in zajete], "gniazda_podwojne": [],
            "poza_gniazdem": 0, "czas_s": {"razem": 20.0}}


def test_session_przypisanie_z_kandydata_projekt_id_nie_po_sha16(tmp_path):
    """E3-A5i: wynik puli per praca niesie ``projekt_id`` i ``frezowanie_id`` wpisu - praca dostaje TEN projekt, takze gdy ten sam
    plik (sha16) lezy w dwoch zleceniach (szukanie po sha16 nie daje przypisania). Pula z folderu (bez ``wpisy``) - jak dotad."""
    baza, (p1, p2, p3), f = _baza_z_projektami(tmp_path)
    try:
        s = SE.Sesja(baza, operatorzy=["Technik A"])
        wpis2 = {"frezowanie_id": f["f1"], "projekt_id": p2, "krazek": "K-120", "wspolczynnik": 1.2}
        wpis3 = {"frezowanie_id": f["f4"], "projekt_id": p3, "krazek": "K-125", "wspolczynnik": 1.25}
        g = [_gniazdo(1, "a" * 16, projekt_id=p2, frezowanie_id=f["f1"], krazek="K-120", wpisy=[wpis2]),
             _gniazdo(2, "b" * 16, projekt_id=p3, frezowanie_id=f["f4"], krazek="K-125", wpisy=[wpis3]),
             _gniazdo(3, "a" * 16)]  # pula z folderu: bez wpisow - sha16 w dwoch zleceniach = bez przypisania (jak dotad)
        skan_id = s.przyjmij_wynik({"plik": "C:/Skany/skan.stl", "sha16": "1" * 16}, _wynik(g))
        prace = {p["gniazdo"]: p for p in baza.wiersze("SELECT * FROM prace WHERE skan_id = ?", (skan_id,))}
        assert (prace[1]["projekt_id"], prace[1]["frezowanie_id"]) == (p2, f["f1"])
        assert (prace[2]["projekt_id"], prace[2]["frezowanie_id"]) == (p3, f["f4"])
        assert (prace[3]["projekt_id"], prace[3]["frezowanie_id"]) == (None, None)
        st = s.stan_wieczoru()
        praca2 = next(x for x in st["skany"][0]["prace"] if x["gniazdo"] == 2)
        assert praca2["krazek"] == "K-125" and praca2["wpisy_do_wyboru"] == [] and praca2["propozycja"] is False
    finally:
        baza.zamknij()


def test_session_niejednoznaczny_krazek_do_wyboru_i_wybor_zapisany_z_osoba(tmp_path):
    """Ten sam STL z tym samym wspolczynnikiem na dwoch krazkach: ``frezowanie_id`` puste, oba wpisy w stanie do wyboru;
    ``wybierz_wpis`` (osoba z listy) zapisuje decyzje ``wybor_wpisu`` i krazek pracy; wpis spoza listy / bez osoby = odmowa."""
    baza, (p1, p2, p3), f = _baza_z_projektami(tmp_path)
    try:
        s = SE.Sesja(baza, operatorzy=["Technik A", "Technik B"])
        wpisy = [{"frezowanie_id": f["f2"], "projekt_id": p3, "krazek": "K-120", "wspolczynnik": 1.2},
                 {"frezowanie_id": f["f3"], "projekt_id": p3, "krazek": "K-120B", "wspolczynnik": 1.2}]
        g = [_gniazdo(5, "b" * 16, projekt_id=p3, frezowanie_id=None, krazek=None, wpisy=wpisy,
                      _uwagi=["ten sam projekt w 2 wpisach puli o tym samym wspolczynniku - krazek albo zlecenie do wskazania"])]
        skan_id = s.przyjmij_wynik({"plik": "C:/Skany/skan.stl", "sha16": "2" * 16}, _wynik(g))
        praca = baza.wiersz("SELECT * FROM prace WHERE skan_id = ?", (skan_id,))
        assert praca["projekt_id"] == p3 and praca["frezowanie_id"] is None
        x = s.stan_wieczoru()["skany"][0]["prace"][0]
        assert [(w["frezowanie_id"], w["krazek"]) for w in x["wpisy_do_wyboru"]] == [(f["f2"], "K-120"), (f["f3"], "K-120B")]
        assert x["krazek"] is None and x["wybor_wpisu"] is None
        with pytest.raises(SE.BladSesji):
            s.wybierz_wpis(praca["id"], f["f3"])  # nikt nie jest wybrany
        s.wybierz_operatora("Technik B")
        with pytest.raises(SE.BladSesji):
            s.wybierz_wpis(praca["id"], f["f4"])  # krazek spoza wpisow tej pracy
        d = s.wybierz_wpis(praca["id"], f["f3"])
        dec = baza.wiersz("SELECT * FROM decyzje WHERE id = ?", (d,))
        assert (dec["rodzaj"], dec["wartosc"], dec["operator"], dec["praca_id"]) == ("wybor_wpisu", str(f["f3"]), "Technik B", praca["id"])
        assert baza.wiersz("SELECT frezowanie_id, projekt_id FROM prace WHERE id = ?", (praca["id"],)) == {"frezowanie_id": f["f3"], "projekt_id": p3}
        x = s.stan_wieczoru()["skany"][0]["prace"][0]
        assert x["krazek"] == "K-120B" and x["wybor_wpisu"]["operator"] == "Technik B" and x["kolor"] == "zielony" and x["decyzja"] is None
        assert len(x["wpisy_do_wyboru"]) == 2  # wybor mozna zmienic
        s.wybierz_wpis(praca["id"], f["f2"])
        assert baza.wiersz("SELECT frezowanie_id FROM prace WHERE id = ?", (praca["id"],))["frezowanie_id"] == f["f2"]
    finally:
        baza.zamknij()


def test_kontroler_wybierz_wpis_dozwolone_i_zle_argumenty(tmp_path):
    """Polecenie okna ``wybierz_wpis(praca_id, frezowanie_id)``: ``Praca.wpisy_do_wyboru`` + ``dozwolone``; zle argumenty = odmowa."""
    from stanowisko import kontroler_api as K

    assert "wybierz_wpis" in K.POLECENIA
    a = K.AtrapaKontrolera()
    try:
        baza = a.sesja.baza
        with baza.transakcja():
            z = baza.wstaw("zlecenia", zrodlo="cyrkon", folder="Zmyslony 3400 x", folder_norm="zmyslony 3400 x", kuweta="3400", mtime=1.0, dodano="2026-11-18T08:00:00")
            p = baza.wstaw("projekty", zlecenie_id=z, plik="c.stl", sha16="c" * 16, zeby="36", typ="crown", zaindeksowano="2026-11-18T08:00:00")
            f1 = baza.wstaw("frezowania", projekt_id=p, plik_w_raporcie="c.stl", krazek="K-1", wspolczynnik=1.22, data="2026-11-18", zrodlo="csv")
            f2 = baza.wstaw("frezowania", projekt_id=p, plik_w_raporcie="c.stl", krazek="K-2", wspolczynnik=1.22, data="2026-11-17", zrodlo="csv")
        wpisy = [{"frezowanie_id": f1, "projekt_id": p, "krazek": "K-1", "wspolczynnik": 1.22},
                 {"frezowanie_id": f2, "projekt_id": p, "krazek": "K-2", "wspolczynnik": 1.22}]
        a.sesja.przyjmij_wynik({"plik": "C:/Skany/s.stl", "sha16": "3" * 16},
                               _wynik([_gniazdo(2, "c" * 16, projekt_id=p, frezowanie_id=None, krazek=None, wpisy=wpisy)]))
        a._odswiez()
        praca = a.stan().plytki[-1].gniazdo(2).praca
        assert [(w.frezowanie_id, w.krazek) for w in praca.wpisy_do_wyboru] == [(f1, "K-1"), (f2, "K-2")] and "wybierz_wpis" in praca.dozwolone
        assert not a.wybierz_wpis(praca.praca_id, f1)  # bez osoby
        assert a.wybierz_operatora("Technik A")
        for zle in (("x", f1), (praca.praca_id, None), (praca.praca_id, True), (praca.praca_id,)):
            odp = a.wykonaj("wybierz_wpis", *zle)
            assert not odp and odp.kod, zle
        odp = a.wybierz_wpis(praca.praca_id, f2)
        assert odp, odp.tekst
        praca = a.stan().plytki[-1].gniazdo(2).praca
        assert praca.krazek == "K-2" and [w.wybrany for w in praca.wpisy_do_wyboru] == [False, True]
    finally:
        a.zamknij()


# ----------------------------------------------------------------------------
# kryterium 5: zolty z ratunku rano = propozycja, nie zamyka zlecenia bez potwierdzenia
# ----------------------------------------------------------------------------
def test_k5_zolty_z_ratunku_nie_zamyka_zlecenia_rano_bez_potwierdzenia(tmp_path):
    """Recenzja PR #25 r3 D1: rano praca zolta z uwaga "ratunek: ..." (praca bokiem uratowana pelnym dopasowaniem - mozliwy zly
    projekt) nie dostaje przypisania automatycznego: zlecenie nie jest kompletne po "Zamknij piec", dopoki technik nie potwierdzi
    kandydata (praca dwuznaczna). Praca zielona tego samego skanu domyka swoje zlecenie."""
    zegar_t = [dt.datetime(2026, 11, 19, 8, 0)]

    def zegar():
        zegar_t[0] += dt.timedelta(seconds=5)
        return zegar_t[0]

    baza = B.otworz(tmp_path / "dane" / "stanowisko.sqlite", zegar=zegar)
    try:
        with baza.transakcja():
            zr = baza.wstaw("zlecenia", zrodlo="cyrkon", folder="Testowski 3263 zs", folder_norm="testowski 3263 zs", kuweta="3263", mtime=1.0, dodano="2026-11-18T08:00:00")
            zz = baza.wstaw("zlecenia", zrodlo="cyrkon", folder="Probna 3301 kor", folder_norm="probna 3301 kor", kuweta="3301", mtime=1.0, dodano="2026-11-18T08:00:00")
            baza.wstaw("projekty", zlecenie_id=zr, plik="r.stl", sha16="d" * 16, zeby="11", typ="crown", zaindeksowano="2026-11-18T08:00:00")
            baza.wstaw("projekty", zlecenie_id=zz, plik="z.stl", sha16="e" * 16, zeby="14", typ="crown", zaindeksowano="2026-11-18T08:00:00")
        s = SE.Sesja(baza, operatorzy=["Technik A"], zegar=zegar)
        rano = SR.SesjaRano(s)
        ratunek = ["ratunek: pelne dopasowanie 8 kandydatow wg deskryptorow FPFH (praca nierozpoznana albo niepewna)"]
        g = [_gniazdo(1, "d" * 16, status="zolty", _uwagi=ratunek), _gniazdo(2, "e" * 16, status="zielony")]
        for x in g:
            x["skala"]["wspolczynnik_puli"] = 1.0
        skan_id = rano.przyjmij_wynik({"plik": "C:/Skany/rano.stl", "sha16": "4" * 16}, _wynik(g, uklad="poranna", numer=4))
        prace = {p["gniazdo"]: p for p in baza.wiersze("SELECT * FROM prace WHERE skan_id = ?", (skan_id,))}
        assert prace[1]["projekt_id"] is None and prace[2]["projekt_id"] is not None  # propozycja z ratunku - bez przypisania automatycznego
        stan = rano.stan_pieca()
        klasy = {p["gniazdo"]: p for sk in stan["skany"] for p in sk["prace"]}
        assert klasy[1]["klasa"] == SR.KLASA_DWUZNACZNA and not klasy[1]["liczona"] and klasy[2]["liczona"]
        assert s.stan_wieczoru(s.doba())["skany"] == []  # skan poranny nie trafia do wieczoru
        assert s._przypisania_skanow([skan_id])[1] == {prace[1]["id"]}  # propozycja z ratunku zapisana (stan, ekran)
        wynik = rano.zamknij_piec("Technik A")
        kuwety = {z["kuweta"] for z in wynik["kompletne"]}
        assert "3263" not in kuwety and "3301" in kuwety  # zolty z ratunku bez potwierdzenia nie zamyka zlecenia
        rano.otworz_piec_ponownie(stan["sesja_pieca_id"], "Technik A")
        rano.wybierz_kandydata(prace[1]["id"], "d" * 16, "Technik A")  # technik potwierdza propozycje
        wynik = rano.zamknij_piec("Technik A")
        assert {"3263", "3301"} <= {z["kuweta"] for z in wynik["kompletne"]}
    finally:
        baza.zamknij()


def test_rano_przypisanie_z_wpisu_puli_nie_po_sha16(tmp_path):
    """E3-A5i: rano (pula poranna per praca) praca zielona dostaje projekt WPISU PULI z wyniku, takze gdy ten sam plik (sha16)
    lezy jeszcze w innym zleceniu (spoza puli porannej) - szukanie po sha16 dawaloby prace dwuznaczna."""
    baza, (p1, p2, p3), f = _baza_z_projektami(tmp_path)
    try:
        s = SE.Sesja(baza, operatorzy=["Technik A"])
        rano = SR.SesjaRano(s)
        wpis = {"frezowanie_id": None, "projekt_id": p2, "krazek": None, "wspolczynnik": 1.0}
        g = [_gniazdo(1, "a" * 16, projekt_id=p2, frezowanie_id=None, wpisy=[wpis]), _gniazdo(2, "a" * 16)]  # 2: pula z folderu
        for x in g:
            x["skala"]["wspolczynnik_puli"] = 1.0
        skan_id = rano.przyjmij_wynik({"plik": "C:/Skany/rano2.stl", "sha16": "6" * 16}, _wynik(g, uklad="poranna", numer=5))
        prace = {p["gniazdo"]: p for p in baza.wiersze("SELECT * FROM prace WHERE skan_id = ?", (skan_id,))}
        assert prace[1]["projekt_id"] == p2 and prace[2]["projekt_id"] is None
        klasy = {p["gniazdo"]: p["klasa"] for sk in rano.stan_pieca()["skany"] for p in sk["prace"]}
        assert klasy[1] == SR.KLASA_PEWNA and klasy[2] == SR.KLASA_DWUZNACZNA
    finally:
        baza.zamknij()


def test_propozycja_z_ratunku_wieczorem_oznaczona_w_stanie(tmp_path):
    """Wieczorem zolty z ratunku zostaje przypisany (lista "do dofrezowania" zna kuwete), ale stan i ekran oznaczaja go jako
    propozycje (``Praca.propozycja``)."""
    from stanowisko import kontroler_api as K

    a = K.AtrapaKontrolera()
    try:
        baza = a.sesja.baza
        with baza.transakcja():
            z = baza.wstaw("zlecenia", zrodlo="cyrkon", folder="Zmyslony 3400 x", folder_norm="zmyslony 3400 x", kuweta="3400", mtime=1.0, dodano="2026-11-18T08:00:00")
            p = baza.wstaw("projekty", zlecenie_id=z, plik="c.stl", sha16="f" * 16, zeby="36", typ="crown", zaindeksowano="2026-11-18T08:00:00")
        g = _gniazdo(3, "f" * 16, status="zolty", _uwagi=["ratunek: pelne dopasowanie 4 kandydatow wg deskryptorow FPFH (praca nierozpoznana albo niepewna)"])
        a.sesja.przyjmij_wynik({"plik": "C:/Skany/s2.stl", "sha16": "5" * 16}, _wynik([g]))
        a._odswiez()
        praca = a.stan().plytki[-1].gniazdo(3).praca
        assert praca.propozycja and praca.kuweta == "3400" and baza.wiersz("SELECT projekt_id FROM prace WHERE id = ?", (praca.praca_id,))["projekt_id"] == p
    finally:
        a.zamknij()


# ----------------------------------------------------------------------------
# silnik: przygotowanie puli wpisow w tle (regula zimnej puli), sprzatanie pamieci
# ----------------------------------------------------------------------------
@pytest.fixture(scope="module")
def atrapy_puli(tmp_path_factory) -> list[Path]:
    """24 rozne atrapy koron (inne wymiary = inny skrot zawartosci) w 12 folderach zlecen o fikcyjnych nazwach."""
    d = tmp_path_factory.mktemp("atrapy_puli")
    rng = np.random.default_rng(31)
    pliki = []
    for i in range(24):
        t = ("siekacz", "przedtrzonowy", "trzonowy")[i % 3]
        W, L, H, g, amp = atrapy_koron.TYPY[t]
        sk = rng.uniform(0.9, 1.1, 3)
        m = atrapy_koron.korona(W * sk[0], L * sk[1], H * sk[2], g, amp, n_theta=48, n_u=40, rng=rng)
        p = d / "Cyrkon" / f"{NAZWISKA[i % 4]} {3200 + i // 2} zs" / f"2026-11-18_{NAZWISKA[i % 4].lower()}{i}-{(11, 14, 36)[i % 3]}-crown_cad.stl"
        p.parent.mkdir(parents=True, exist_ok=True)
        m.export(p)
        pliki.append(p)
    return pliki


def test_silnik_przygotowanie_puli_wpisow_postep_i_zadania_czekaja(atrapy_puli, tmp_path):
    """Regula zimnej puli (E3-A5i): ``przygotuj_pule`` buduje pule wpisow w procesie roboczym przed zadaniami; postep
    (``ZdarzenieSilnika`` ``pula``: start / budowa / gotowa) z liczbami gotowe / razem; zadanie zlecone w trakcie budowy rusza
    PO zakonczeniu budowy i dostaje gotowa pule z pamieci procesu (bez ponownego liczenia)."""
    from stanowisko import silnik as SI

    ust = TK.ustawienia_probne(tmp_path)
    wpisy = tuple({"sha16": hashlib.sha256(p.read_bytes()).hexdigest()[:16], "wspolczynnik": 1.2 + 0.01 * (i % 3), "krazek": f"K-{i % 3}",
                   "frezowanie_id": 100 + i, "projekt_id": 1 + i} for i, p in enumerate(atrapy_puli[:12]))
    opis = SI.OpisPuli(wpisy=wpisy, sciezki={1 + i: p for i, p in enumerate(atrapy_puli[:12])}, korzenie=(str(atrapy_puli[0].parents[1]),))
    zdarzenia = []
    with SI.Silnik(ust, funkcja=FUNKCJA_Z_PULA, na_zdarzenie=zdarzenia.append, plik_logu=tmp_path / "silnik.log") as s:
        s.przygotuj_pule(opis)
        plik = tmp_path / "skan_1.stl"
        plik.write_bytes(TK.plik_skanu({"gniazda": {1: "zielony"}, "numer": 1}))
        t0 = time.monotonic()
        while not any(z.typ == "pula" and z.etap == "budowa" for z in zdarzenia):
            assert time.monotonic() - t0 < 120, [z.typ for z in zdarzenia]
            time.sleep(0.02)
        nr = s.zlec(SI.ZadanieAnalizy(skan=plik, pula=opis))
        while not any(z.typ in ("wynik", "blad") for z in zdarzenia):
            assert time.monotonic() - t0 < 300, [(z.typ, z.etap) for z in zdarzenia]
            time.sleep(0.05)
        stan = s.stan()
    typy = [(z.typ, z.etap) for z in zdarzenia if z.typ in ("pula", "start", "wynik", "blad")]
    gotowa = typy.index(("pula", "gotowa"))
    assert typy[0] == ("pula", "start") and typy.index(("start", "")) > gotowa, typy  # zadanie ruszylo po zbudowaniu puli
    postep = [z.wynik for z in zdarzenia if z.typ == "pula" and z.etap == "budowa"]
    assert postep and postep[-1]["razem"] == 12 and all(0 <= p["gotowe"] <= p["razem"] for p in postep)
    info = next(z.wynik for z in zdarzenia if z.typ == "pula" and z.etap == "gotowa")
    assert info["wpisow"] == 12 and info["geometrii"] == 12 and info["czas_s"] >= 0
    w = next(z for z in zdarzenia if z.typ == "wynik").wynik
    assert w["zadanie_id"] == nr and w["test_pula"]["per_praca"] and w["test_pula"]["geometrii"] == 12
    assert w["test_pula"]["czas_w_zadaniu_s"] < 1.0  # pula z pamieci procesu (przygotowana w tle), nie budowana od nowa
    assert stan["pula"]["gotowa"] and not stan["pula"]["w_toku"]
    assert len(list((tmp_path / "dane" / "pula_cache" / "projekty").glob("*.npz"))) == 12  # pamiec puli na dysku ([sciezki] pula_cache)
    assert "testowski" not in (tmp_path / "silnik.log").read_text(encoding="utf-8", errors="replace").lower()


def test_k4_sprzataj_przy_starcie_usuwa_tylko_stare_nieuzywane(atrapy_puli, tmp_path):
    """Kryterium 4: program przy starcie (proces roboczy silnika) wola ``PamiecPuli.sprzataj([silnik] pamiec_puli_dni)`` -
    znikaja tylko wpisy nieuzywane dluzej niz N dni; nowsze zostaja. Bez klucza (0) - nic nie jest usuwane."""
    from stanowisko import aplikacja as AP

    drzewo, millbox = atrapy_puli[0].parents[2], tmp_path / "millbox"
    zapisz_csv(millbox, [])
    ust = ustawienia_puli(tmp_path, drzewo, millbox)
    ust["silnik"]["pamiec_puli_dni"] = 30
    katalog = tmp_path / "dane" / "pula_cache" / "projekty"
    katalog.mkdir(parents=True)
    teraz = time.time()
    wiek = {"stary_40d": 40, "stary_31d": 31, "nowy_29d": 29, "nowy_1d": 1}
    for nazwa, dni in wiek.items():
        p = katalog / f"{'0' * 16}_1.2_auto_h_{nazwa}.npz"
        p.write_bytes(b"x")
        os.utime(p, (teraz - dni * 86400, teraz - dni * 86400))
    k = AP.Aplikacja(ust, funkcja_analizy=FUNKCJA_Z_PULA, parametry_scannera=TK.PARAMETRY_SCANNERA)
    try:
        k.start()
        czekaj(k, lambda: k.silnik.stan().get("pamiec_puli_usuniete") is not None, "sprzatanie pamieci puli przy starcie", 180)
        assert k.silnik.stan()["pamiec_puli_usuniete"] == 2
    finally:
        k.zamknij()
    zostaly = sorted(p.name.split("_")[-1][:-4] for p in katalog.glob("*.npz"))
    assert zostaly == ["1d", "29d"]


# ----------------------------------------------------------------------------
# kryteria 2 i 3: zimna pula przez aplikacje, petla okna, restart z ciepla pamiecia
# ----------------------------------------------------------------------------
def test_k2_k3_zimna_pula_skany_czekaja_bez_zawieszenia_okna_i_restart_z_ciepla_pamiecia(atrapy_puli, tmp_path):
    """Kryterium 2: pula 24 wpisow budowana od zera (pusta pamiec) po starcie programu; skany zapisane w trakcie budowy czekaja
    w kolejce silnika i ruszaja po zbudowaniu puli (regula E3-A5i), pasek pokazuje postep budowy (gotowe / razem), petla Qt bez
    przerw > 200 ms. Kryterium 3: restart programu z ciepla pamiecia (pliki ``.npz`` puli na dysku) - pula gotowa w < 5 s."""
    from PySide6.QtCore import QEventLoop, QTimer
    from PySide6.QtWidgets import QApplication

    from stanowisko import aplikacja as AP
    from stanowisko import kontroler_api as K

    app = QApplication.instance() or QApplication([])
    assert app.platformName() == "offscreen"
    drzewo, millbox = atrapy_puli[0].parents[2], tmp_path / "millbox"
    dzis = dt.date.today().isoformat()
    zapisz_csv(millbox, [(p.name, f"K-{120 + 5 * (i % 2)}", 1.20 + 0.05 * (i % 2), dzis) for i, p in enumerate(atrapy_puli)])
    ust = ustawienia_puli(tmp_path, drzewo, millbox)
    (tmp_path / "eksport").mkdir()

    k = AP.Aplikacja(ust, funkcja_analizy=FUNKCJA_Z_PULA, parametry_scannera=TK.PARAMETRY_SCANNERA)
    try:
        k.start()
        assert k.wybierz_operatora("Technik A")
        lacznik = K.lacznik_qt(k, okres_ms=30)
        petla = QEventLoop()
        pomiar = {"ostatni": time.perf_counter(), "przerwa": 0.0, "tykniec": 0, "budowa": [], "starty_przed_gotowa": 0, "zapisane": 0,
                  "napisy": set()}

        def tyk():
            teraz = time.perf_counter()
            pomiar["przerwa"] = max(pomiar["przerwa"], teraz - pomiar["ostatni"])
            pomiar["ostatni"] = teraz
            pomiar["tykniec"] += 1
            s = k.stan()
            p = s.pula
            if p.budowa_razem:
                pomiar["budowa"].append((p.budowa_gotowe, p.budowa_razem))
                pomiar["napisy"].add(p.napis)
                if pomiar["zapisane"] < 3 and p.budowa_gotowe < p.budowa_razem and len(pomiar["budowa"]) % 20 == 1:
                    pomiar["zapisane"] += 1  # skany zapisane W TRAKCIE budowy puli
                    (tmp_path / "eksport" / f"skan_{pomiar['zapisane']}.stl").write_bytes(
                        TK.plik_skanu({"gniazda": {1: "zielony", 2: "czerwony"}, "numer": pomiar["zapisane"]}))
            if s.analiza is not None and (p.budowa_razem is None or p.budowa_gotowe < p.budowa_razem):
                pomiar["starty_przed_gotowa"] += 1
            if len(s.plytki) == 3 and s.kolejka.razem == 0:
                petla.quit()

        zegar = QTimer()
        zegar.setInterval(10)
        zegar.timeout.connect(tyk)
        QTimer.singleShot(400_000, petla.quit)
        zegar.start()
        t0 = time.perf_counter()
        petla.exec()
        czas = time.perf_counter() - t0
        zegar.stop()
        lacznik.zatrzymaj()
        s = k.stan()
        print(f"\n[kryterium 2] zimna pula 24 wpisow + 3 skany w {czas:.1f} s; najdluzsza przerwa petli Qt {pomiar['przerwa'] * 1000:.0f} ms; "
              f"odczytow postepu budowy {len(pomiar['budowa'])}; napis {sorted(pomiar['napisy'])[:2]}")
        assert pomiar["zapisane"] == 3, "skany mialy byc zapisane w trakcie budowy puli"
        assert len(s.plytki) == 3 and all(p.status == "przyjety" for p in s.plytki)
        assert pomiar["starty_przed_gotowa"] == 0  # regula: analiza czeka na pule wpisow
        assert len({g for g, _ in pomiar["budowa"]}) >= 3 and pomiar["budowa"][-1][1] == 24  # postep widoczny na pasku
        assert pomiar["przerwa"] <= PROG_PRZERWY_S
        assert s.pula.wpisy == 24 and s.pula.stan == "gotowa" and s.pula.zrodlo == "wpisy"
        assert all(not any(n.lower() in napis.lower() for n in NAZWISKA) for napis in pomiar["napisy"])
        wyniki = [json.loads(k.sesja.sciezka_wyniku(p.skan_id).read_text(encoding="utf-8")) for p in s.plytki]
        assert all(w["test_pula"]["per_praca"] and w["test_pula"]["geometrii"] == 24 for w in wyniki)
    finally:
        k.zamknij()
    pliki_pamieci = list((tmp_path / "dane" / "pula_cache" / "projekty").glob("*.npz"))
    assert len(pliki_pamieci) == 24

    k2 = AP.Aplikacja(ust, funkcja_analizy=FUNKCJA_Z_PULA, parametry_scannera=TK.PARAMETRY_SCANNERA)  # restart: pamiec ciepla
    try:
        t0 = time.monotonic()
        k2.start()
        czekaj(k2, lambda: k2.stan().pula.stan == "gotowa" and k2.stan().pula.budowa_razem and k2.stan().pula.budowa_gotowe == 24
               and k2.stan().pula.czas_budowy_s is not None, "pula po restarcie", 120)
        sciana = time.monotonic() - t0
        budowa = k2.stan().pula.czas_budowy_s
        print(f"\n[kryterium 3] restart z ciepla pamiecia: budowa puli {budowa:.2f} s (od zlecenia do gotowej), od startu programu {sciana:.1f} s")
        assert budowa < 5.0
    finally:
        k2.zamknij()


# ----------------------------------------------------------------------------
# kryterium 1: prawdziwa aplikacja + prawdziwy porownaj z puli wpisow
# ----------------------------------------------------------------------------
def test_k1_prawdziwa_analiza_pula_wpisow_wlasciwe_frezowanie_i_wybor_krazka(korony, tmp_path):
    """Kryterium 1: plytka sztuczna z pracami z dwoch krazkow (1,20 i 1,25), kazdy STL na obu krazkach, jeden STL dodatkowo na
    trzecim krazku o tej samej wartosci (1,20) - prace przypisane do wlasciwego frezowania w 100 %, praca niejednoznaczna z oboma
    wpisami do wyboru (stan okna), wybor technika zapisany z osoba; nazwy folderow nie wychodza poza baze."""
    import symulator_skanera as SY
    import metryki_pula as MP

    from stanowisko import aplikacja as AP
    from stanowisko import synth
    from stanowisko import uklad as U

    drzewo, millbox = tmp_path / "drzewo", tmp_path / "millbox"
    foldery = ("Testowski 3263 zs", "Probna 3301 kor", "Atrapowa 3400 x")
    pliki = []
    for i, (p, folder) in enumerate(zip(korony, foldery)):
        cel = drzewo / "Cyrkon" / folder / f"2026-11-18_{folder.split()[0].lower()}-{['11', '14', '36'][i]}-crown_cad.stl"
        cel.parent.mkdir(parents=True)
        shutil.copy(p, cel)
        pliki.append(cel)
    uk = U.wczytaj("okragla_wieczorna")
    op = synth.Opcje.z_toml(plytka=uk.nazwa, prace_na_plytce=3, p_drgniecia=0.0, wspolczynnik=(1.20, 1.25), poza_uklad=True, wersja_ubytkow=1)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        skan, prawda = synth.generuj_plytke(uk, uk.numery[0], pliki, MP.LosowanieKrazkow(np.random.default_rng(22), (1.20, 1.25), kolejno=True), op, 22)
    plik_skanu, _ = synth.zapisz(skan, prawda, tmp_path / "skany", "skan_okragla_wieczorna")
    sha_pliku = {hashlib.sha256(p.read_bytes()).hexdigest()[:16]: p for p in pliki}
    niejednoznaczna = next(x for x in prawda.prace if abs(x.wspolczynnik - 1.20) < 1e-9)
    dzis = dt.date.today().isoformat()
    wiersze = [(p.name, k, w, dzis) for p in pliki for k, w in (("K-120", 1.20), ("K-125", 1.25))]
    wiersze.append((sha_pliku[niejednoznaczna.projekt].name, "K-120B", 1.20, dzis))  # ten sam STL, ta sama wartosc, drugi krazek
    zapisz_csv(millbox, wiersze)
    ust = ustawienia_puli(tmp_path, drzewo, millbox)
    (tmp_path / "eksport").mkdir()
    k = AP.Aplikacja(ust, parametry_scannera=TK.PARAMETRY_SCANNERA)  # prawdziwa funkcja analizy: stanowisko.porownaj:porownaj
    try:
        k.start()
        assert k.wybierz_operatora("Technik A")
        czekaj(k, lambda: k.stan().pula.stan == "gotowa" and k.stan().pula.wpisy == 7, "pula wpisow", 300)
        SY.zapisz_jak_skaner(plik_skanu, tmp_path / "eksport" / "eksport_plytki.stl", czas_s=1.0, kawalki=8)
        czekaj(k, lambda: bool(k.stan().plytki), "wynik analizy", 900)
        s = k.stan()
        p = s.plytki[0]
        assert p.status == "przyjety", (p.status, [x.tekst for x in s.komunikaty])
        baza = k.sesja.baza
        fr = {(x["sha16"], x["krazek"]): x["id"] for x in frezowania(baza)}
        prace = {x["gniazdo"]: x for x in baza.wiersze("SELECT * FROM prace WHERE skan_id = ?", (p.skan_id,))}
        dobrze = 0
        for x in prawda.prace:
            praca = prace[x.gniazdo]
            if x is niejednoznaczna:
                assert praca["frezowanie_id"] is None and praca["projekt_id"] is not None
                widok = p.gniazdo(x.gniazdo).praca
                assert sorted(w.krazek for w in widok.wpisy_do_wyboru) == ["K-120", "K-120B"] and "wybierz_wpis" in widok.dozwolone
                odp = k.wybierz_wpis(widok.praca_id, fr[(x.projekt, "K-120B")])
                assert odp, odp.tekst
                dec = baza.wiersz("SELECT * FROM decyzje WHERE praca_id = ? AND rodzaj = 'wybor_wpisu'", (widok.praca_id,))
                assert dec["operator"] == "Technik A" and dec["wartosc"] == str(fr[(x.projekt, "K-120B")])
                assert k.stan().plytki[0].gniazdo(x.gniazdo).praca.krazek == "K-120B"
            else:
                krazek = "K-120" if abs(x.wspolczynnik - 1.20) < 1e-9 else "K-125"
                assert praca["frezowanie_id"] == fr[(x.projekt, krazek)], (x.gniazdo, krazek, praca["frezowanie_id"])
                dobrze += 1
        print(f"\n[kryterium 1] prace przypisane do wlasciwego frezowania: {dobrze} / {len(prawda.prace) - 1} (+1 niejednoznaczna do wyboru)")
        wynik_txt = k.sesja.sciezka_wyniku(p.skan_id).read_text(encoding="utf-8").lower()
        assert not any(n.lower() in wynik_txt for n in NAZWISKA)
    finally:
        k.zamknij()
    log = "".join(f.read_text(encoding="utf-8", errors="replace") for f in (tmp_path / "dane" / "logi").glob("*.log")).lower()
    assert not any(n.lower() in log for n in NAZWISKA)


# ----------------------------------------------------------------------------
# start programu: moduly z DLL i diagnostyka \KnownDlls (recenzja PR #31 D1, D2)
# ----------------------------------------------------------------------------
def test_main_laduje_moduly_z_dll_przed_silnikiem():
    """A2p POTRZEBUJE 4 / PR #31 D2: ``main()`` laduje moduly z DLL uzywane pozniej (numpy, sqlite3, trimesh, PIL ...) zaraz po Qt,
    przed utworzeniem ``Aplikacja`` (a wiec przed pierwszym uzyciem silnika)."""
    from stanowisko import aplikacja as AP

    wynik = AP.zaladuj_moduly_dll()
    assert wynik["numpy"] is True and wynik["sqlite3"] is True and wynik["trimesh"] is True
    drzewo = ast.parse((STANOWISKO / "stanowisko" / "aplikacja.py").read_text(encoding="utf-8"))
    main = next(n for n in drzewo.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    wywolania = [(w.lineno, getattr(w.func, "id", getattr(w.func, "attr", ""))) for w in ast.walk(main) if isinstance(w, ast.Call)]
    linia_modulow = min(n for n, nazwa in wywolania if nazwa == "zaladuj_moduly_dll")
    linia_aplikacji = min(n for n, nazwa in wywolania if nazwa == "Aplikacja")
    assert linia_modulow < linia_aplikacji


@pytest.mark.skipif(os.name != "nt", reason="uchwyty obiektow Windows")
def test_knowndlls_uchwyt_sprawdzany_po_smierci_procesu_roboczego(tmp_path, caplog, monkeypatch):
    """PR #31 D1: po smierci procesu roboczego program zapisuje w logu, czy uchwyt ``\\KnownDlls`` procesu okna jest nadal otwarty
    (dane diagnostyczne z laptopa stanowiska); tylko wpis w logu - praca idzie dalej."""
    from stanowisko import aplikacja as AP

    uchwyty = AP.uchwyty_knowndlls()
    assert uchwyty and all(isinstance(h, int) and h > 0 for h in uchwyty)
    monkeypatch.setattr(AP, "KNOWNDLLS_SPRAWDZ_PO_S", (0.3,))
    TK.pula_probna(tmp_path)
    (tmp_path / "eksport").mkdir()
    caplog.set_level(logging.INFO, logger="stanowisko.aplikacja")
    k = AP.Aplikacja(TK.ustawienia_probne(tmp_path), funkcja_analizy=TK.FUNKCJA_SZTUCZNA, parametry_scannera=TK.PARAMETRY_SCANNERA)
    try:
        k.start()
        czekaj(k, lambda: k.silnik.pid is not None, "proces roboczy", 120)
        (tmp_path / "eksport" / "zabij.stl").write_bytes(TK.plik_skanu({"gniazda": {1: "zielony"}, "numer": 1, "zabij": True}))
        czekaj(k, lambda: any("KnownDlls" in r.getMessage() for r in caplog.records), "wpis diagnostyki KnownDlls", 120)
        (tmp_path / "eksport" / "dalej.stl").write_bytes(TK.plik_skanu({"gniazda": {1: "zielony"}, "numer": 2}))
        czekaj(k, lambda: any(p.numer == 2 for p in k.stan().plytki), "dalsza praca po smierci procesu", 120)
    finally:
        k.zamknij()
    wpis = next(r.getMessage() for r in caplog.records if "KnownDlls" in r.getMessage())
    assert "otwarty" in wpis or "zniknal" in wpis


# ----------------------------------------------------------------------------
# ekran: licznik puli i postep budowy, wybor krazka
# ----------------------------------------------------------------------------
def test_ui_pasek_postep_budowy_puli_i_wybor_krazka():
    from PySide6.QtWidgets import QApplication

    from stanowisko import kontroler_api as K
    from stanowisko.ui import czesci as C

    app = QApplication.instance() or QApplication([])
    assert app.platformName() == "offscreen"
    a = K.AtrapaKontrolera()
    try:
        a.symuluj_skan("zwykla", numer=1)
        stan = a.stan()
        pasek = C.PasekStanu()
        pula = K.Pula(stan="gotowa", zrodlo="wpisy", wpisy=40, budowa_gotowe=10, budowa_razem=40, napis="wpisow puli: 40 - buduje: 10 z 40")
        pasek.ustaw(__import__("dataclasses").replace(stan, pula=pula))
        assert pasek.postep_puli.isVisibleTo(pasek) and (pasek.postep_puli.minimum(), pasek.postep_puli.maximum()) == (0, 40)
        assert pasek.postep_puli.value() == 10 and "10 z 40" in pasek.pula.text()
        widok = C.WidokPracy()
        plytka = stan.plytki[0]
        gniazdo = next(g for g in plytka.gniazda if g.prace)
        praca = __import__("dataclasses").replace(gniazdo.prace[0], dozwolone=("ukruszona", "ok", "wybierz_wpis"),
                                                  wpisy_do_wyboru=(K.WpisDoWyboru(frezowanie_id=11, krazek="K-120", wspolczynnik=1.2),
                                                                   K.WpisDoWyboru(frezowanie_id=12, krazek="K-120B", wspolczynnik=1.2)))
        wybrane = []
        widok.wybor_wpisu.connect(wybrane.append)
        widok.ustaw(__import__("dataclasses").replace(stan, operator="Technik A"), plytka, gniazdo, praca, 0, False)
        przyciski = widok.przyciski_wpisow()
        assert [b.text() for b in przyciski] == ["K-120", "K-120B"] and all(b.isEnabled() for b in przyciski)
        przyciski[1].click()
        assert wybrane == [12]
    finally:
        a.zamknij()
