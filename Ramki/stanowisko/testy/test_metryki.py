"""metryki.py i narzedzia/raport_metryk.py - raport metryk z bazy stanowiska (E3-A10).

Kryterium (plan etapu 3, 4.1, E3-A10): na bazie z sesji sztucznych o znanej prawdzie wartosci raportu = wartosci policzone
recznie (tabela ``OCZEKIWANE`` - kazdy wiersz osobnym testem ``test_oczekiwane[Xnn]``) dla: udzialu falszywych alarmow,
top-1 i top-2 wzgledem decyzji technika, udzialu prac nieznanych, czasu przy stanowisku, udzialu skanow powtorzonych i dni
bez awarii; raport (jedna strona) do 60 linii; w raporcie i w JSON 0 nazw folderow, plikow i osob.

Baza powstaje WYLACZNIE przez publiczne API: ``Sesja`` (wieczor), ``SesjaRano`` (poranek) i ``Baza.zdarzenie`` dla wpisow,
ktore w programie robi aplikacja (``program_start``, ``program_stop``, ``start_skanu``, ``silnik_nie_startuje`` - te same
nazwy i zrodla co ``aplikacja.py``). Zadnych wpisow SQL obok logiki. Schemat bazy bez zmian (wersja 1): raport czyta baze
tylko do odczytu, a metryka M2 (tabela testow wykrywalnosci) jest pominieta z dopiskiem "wymaga zmiany schematu".

Scenariusz (czas lokalny; doba robocza 06:00-06:00, zmiany 6 / 14 / 22; projekty P1-P8 w indeksie, P9 poza indeksem):

Doba 2026-11-16, zmiana 2 (wieczor):
  17:55 program_start (pierwszy w dzienniku - nie awaria)
  18:00 start_skanu; 18:01 W1 plytka 1 przyjety: g1 P1 zielony, g2 P2 czerwony, g3 P3 czerwony, g4 szary (bez kandydata),
        g5 P4 zielony; 18:03 "Ukruszona" g2; 18:04 "OK" g3 (falszywy alarm); 18:05 "ukruszona_niewykryta" g5 (tryb cienia)
  18:20 start_skanu; 18:21 W2 plytka 2 przyjety: g1 P6 zielony, g2 P7 czerwony; 18:22 "OK" g2
  18:23 start_skanu; 18:24 W3 plytka 2 (te same prace): g1 P6 zielony, g2 P7 czerwony; 18:25 potwierdzenie ponownego skanu
        (W2 -> zastapiony: jego "OK" przestaje sie liczyc); 18:26 "OK" W3 g2 (falszywy alarm)
  18:45 start_skanu; 18:46 W4 plytka poranna nr 4 w trybie wieczor -> plytka_nie_z_trybu
  18:47 start_skanu; 18:48 W5 analiza bez wyniku -> blad
  18:49 start_skanu; 18:50 W6 plytka 3: g1 P8 zielony, g2 szary, g3 P5 czerwony; 18:51 "Ukruszona" g3, 18:52 cofniecie
  19:30 program_stop
Doba 2026-11-17:
  06:50 program_start (po program_stop - nie awaria)
  06:58 start_skanu; 07:00 R1 plytka 4 (otwiera piec F1): g1 P1 zielony (pewna), g2 P2 zolty k1=P2 k2=P3 (dwuznaczna),
        g3 szary k1=P5 k2=P4 (dwuznaczna), g4 bez kandydata, g5 bez kandydata, g6 P7 zielony (pewna);
        07:02 wybor 1. kandydata g2 (P2); 07:03 wybor 2. kandydata g3 (P4); 07:04 przypisanie reczne g4 -> P6
  07:10 R2 plytka 5: g1 P8 zielony (pewna), g2 zolty k1=P3 (dwuznaczna, zostaje), g3 zielony k1=P9 spoza indeksu (nieznana)
  07:12 R3 analiza bez wyniku (blad); 07:13 pominiecie R3; 07:20 "Zamknij piec" F1
  09:00 R4 plytka 4 (piec F2): g1 P1 zielony (poprawka - punkt zamknal F1), g2 P5 zielony (pewna); 09:05 "Zamknij piec" F2
  22:50 program_start BEZ program_stop od 06:50 -> awaria (ostatni wpis dziennika przed startem: 09:05, doba 2026-11-17)
  23:10 start_skanu; 23:11 W7 plytka 1 (zmiana 3): g1 P1 zielony, g2 P3 czerwony; 23:14 "Ukruszona" g2
Doba 2026-11-18:
  00:30 program_stop (doba 2026-11-17); 07:25 program_start
  07:29 start_skanu; 07:30 R5 plytka 6 (piec F3, NIEZAMKNIETY): g1 P3 zielony
  18:58 start_skanu; 19:00 W8 plytka 2: g1 P6 czerwony, g2 P7 zielony; 19:03 "OK" g1 (falszywy alarm)
  19:09 start_skanu; 19:10 W9 plytka 3: g1 P8 "popraw ulozenie" -> do_powtorzenia (zostaje aktywny)
  19:30 silnik_nie_startuje -> awaria (doba 2026-11-18)

Rachunek reczny (okres 2026-11-16 .. 2026-11-18, tryb oba) - w kolumnie "jak" tabeli ``OCZEKIWANE``.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

from stanowisko import baza as B
from stanowisko import session as SE
from stanowisko import session_rano as SR

import raport_metryk  # noqa: E402 (katalog narzedzia dodaje conftest)
from stanowisko import metryki as M  # noqa: E402

STANOWISKO = Path(__file__).resolve().parent.parent
OSOBY = ["Kowalska Maria", "Zielinski Piotr"]
ZLECENIA = [  # (klucz, zrodlo, folder - fikcyjne nazwiska: nie moga trafic do raportu, kuweta)
    ("Z1", "cyrkon", "3263 Testowska Anna", "3263"),
    ("Z2", "cyrkon", "3270 Probny-Kowal Jan", "3270"),
    ("Z3", "prywatne", "#1234 Fikcyjna Ewa", "#1234"),
]
PROJEKTY = [  # (klucz, zlecenie, plik, zeby)
    ("P1", "Z1", "Testowska_11.stl", "11"), ("P2", "Z1", "Testowska_12.stl", "12"), ("P3", "Z1", "Testowska_21.stl", "21"),
    ("P4", "Z2", "Probny_36.stl", "36"), ("P5", "Z2", "Probny_46.stl", "46"),
    ("P6", "Z3", "Fikcyjna_14.stl", "14"), ("P7", "Z3", "Fikcyjna_15.stl", "15"), ("P8", "Z3", "Fikcyjna_16.stl", "16"),
]
ZAKAZANE = (["Testowska", "Probny", "Kowal", "Fikcyjna", "Nowakowa", "Teresa", ".stl", "C:/", "C:\\"] + OSOBY
            + [z[2] for z in ZLECENIA] + [p[2] for p in PROJEKTY])
OD, DO = "2026-11-16", "2026-11-18"


def sha16(klucz: str) -> str:
    return hashlib.sha256(f"qc-test-metryki/{klucz}".encode("ascii")).hexdigest()[:16]


class Zegar:
    """Zegar testu bez samoczynnego przesuwania: kazdy czas w bazie jest dokladnie ustawionym czasem (rachunek reczny)."""

    def __init__(self, start: str):
        self.t = dt.datetime.fromisoformat(start)

    def ustaw(self, czas: str) -> None:
        self.t = dt.datetime.fromisoformat(czas)

    def __call__(self) -> dt.datetime:
        return self.t


def status_match(kandydaci: list) -> tuple[str, float]:
    """Status dopasowania jak w ``match`` (progi z ustawienia.przyklad.toml): akceptacja 0,85, ostrzezenie 0,6, przewaga 0,1."""
    if not kandydaci:
        return "szary", 0.0
    p1 = kandydaci[0][1]
    p2 = kandydaci[1][1] if len(kandydaci) > 1 else 0.0
    pewnosc = round(p1 - p2, 4)
    if p1 >= 0.85 and pewnosc >= 0.1:
        return "zielony", pewnosc
    if p1 >= 0.6 and pewnosc >= 0.1:
        return "zolty", pewnosc
    return "szary", pewnosc


INSPEKCJA_GNIAZDA = {"ok": "zielony", "ubytek": "czerwony", "popraw_ulozenie": "zolty"}


def wynik(plytka: str, numer: int, gniazda: list, wieczor: bool) -> dict:
    """Wynik w formacie ``porownaj.porownaj`` (pola czytane przez ``session``). Gniazdo: (nr, [(projekt, pokrycie)...], inspekcja)."""
    wsp = 1.225 if wieczor else 1.0
    lista = []
    for nr, kand, ins in gniazda:
        k = [{"id": sha16(p), "pokrycie": pok, "rms_mm": 0.02, "metoda": "ransac"} for p, pok in kand]
        status, pewnosc = status_match(kand)
        inspekcja = None if status == "szary" else {
            "status": ins, "ubytki": [{"srednica_mm": 0.8, "glebokosc_mm": 0.1}] if ins == "ubytek" else [], "metoda": "plaszczyzna"}
        lista.append({"gniazdo": nr, "status_fragmentu": "praca", "punkty": 15000, "status": status, "pewnosc": pewnosc, "czas_s": 0.5,
                      "uwagi": [], "kandydaci": k, "inspekcja": inspekcja,
                      "status_gniazda": "szary" if status == "szary" else INSPEKCJA_GNIAZDA[ins],
                      "skala": {"wspolczynnik_puli": wsp, "poprawka_proc": 0.0} if k else None})
    return {"skan": f"Nowakowa Teresa plytka{numer}.stl", "plytka": plytka, "plytka_wybor": "auto", "uklad_zgodny": True,
            "wspolczynnik": wsp, "projekty": 8, "foldery_projektow": ["C:/Users/lab/OneDrive/Cyrkon/3263 Testowska Anna"], "numer": numer,
            "numer_zrodlo": "dolki", "gniazda": lista, "gniazda_podwojne": [], "poza_gniazdem": 0, "czas_s": {"razem": 30.0}}


class Budowa:
    """Baza scenariusza budowana przez publiczne API (``Sesja``, ``SesjaRano``, ``Baza.zdarzenie``)."""

    def __init__(self, katalog: Path, start: str = "2026-11-16T17:00:00"):
        self.zegar = Zegar(start)
        self.plik = katalog / "dane" / "stanowisko.sqlite"
        self.baza = B.otworz(self.plik, zegar=self.zegar)
        self.sesja = SE.Sesja(self.baza, operatorzy=OSOBY, katalog_wynikow=katalog / "dane" / "wyniki", zegar=self.zegar)
        self.sesja.wybierz_operatora(OSOBY[0])
        self.rano = SR.SesjaRano(self.sesja)
        self.projekt_id: dict[str, int] = {}
        self.n = 0

    def indeks(self) -> None:
        """Zlecenia i projekty (w programie wpisuje je indeks folderow - paczka A4, ``Baza.wstaw``)."""
        z_id = {}
        with self.baza.transakcja():
            for klucz, zrodlo, folder, kuweta in ZLECENIA:
                z_id[klucz] = self.baza.wstaw("zlecenia", zrodlo=zrodlo, folder=folder, folder_norm=folder.lower(), kuweta=kuweta,
                                              mtime=1794900000.0, dodano="2026-11-15T08:00:00")
            for klucz, zl, plik, zeby in PROJEKTY:
                self.projekt_id[klucz] = self.baza.wstaw("projekty", zlecenie_id=z_id[zl], plik=plik, sha16=sha16(klucz), zeby=zeby,
                                                         typ="korona", mtime_ns=1794900000000000000, rozmiar=300000,
                                                         zaindeksowano="2026-11-15T08:00:05")

    def o(self, czas: str) -> "Budowa":
        self.zegar.ustaw(czas)
        return self

    def zd(self, czas: str, zrodlo: str, typ: str, dane: dict | None = None) -> None:
        """Wpis dziennika tak, jak robi go aplikacja (``aplikacja.py``: program_start / program_stop / start_skanu / silnik_nie_startuje)."""
        self.baza.zdarzenie(zrodlo, typ, dane, czas=czas)

    def _zdarzenie_skanu(self, czas: str) -> dict:
        self.n += 1
        return {"plik": f"C:/Skany/{czas[:10]}/Nowakowa Teresa {self.n}.stl",
                "sha16": hashlib.sha256(f"skan/{self.n}".encode("ascii")).hexdigest()[:16], "rozmiar": 48000000, "czas_pliku": czas}

    def wieczor(self, czas: str, plytka: str, numer: int, gniazda: list) -> tuple[int, list[int]]:
        self.o(czas)
        skan = self.sesja.przyjmij_wynik(self._zdarzenie_skanu(czas), wynik(plytka, numer, gniazda, True), tryb="wieczor")
        return skan, self.prace(skan)

    def rano_skan(self, czas: str, numer: int, gniazda: list) -> tuple[int, list[int]]:
        self.o(czas)
        skan = self.rano.przyjmij_wynik(self._zdarzenie_skanu(czas), wynik("poranna", numer, gniazda, False))
        return skan, self.prace(skan)

    def prace(self, skan_id: int) -> list[int]:
        return [w["id"] for w in self.baza.wiersze("SELECT id FROM prace WHERE skan_id = ? ORDER BY id", (skan_id,))]


def zbuduj_scenariusz(katalog: Path) -> Path:
    """Caly scenariusz z naglowka modulu; zwraca plik bazy."""
    b = Budowa(katalog)
    b.indeks()
    s, r = b.sesja, b.rano
    # --- doba 2026-11-16, zmiana 2 ---
    b.zd("2026-11-16T17:55:00", "system", "program_start", {"wersja": "test", "wznowione": 0, "znane_pliki": 0})
    b.zd("2026-11-16T18:00:00", "ui", "start_skanu", {"udany": True})
    _, w1 = b.wieczor("2026-11-16T18:01:00", "wieczorna", 1, [
        (1, [("P1", 0.95)], "ok"), (2, [("P2", 0.93)], "ubytek"), (3, [("P3", 0.92)], "ubytek"), (4, [], "ok"), (5, [("P4", 0.95)], "ok")])
    b.o("2026-11-16T18:03:00"); s.ukruszona(w1[1])
    b.o("2026-11-16T18:04:00"); s.ok(w1[2])
    b.o("2026-11-16T18:05:00"); s.decyzja(w1[4], "ukruszona_niewykryta")
    b.zd("2026-11-16T18:20:00", "ui", "start_skanu", {"udany": True})
    _, w2 = b.wieczor("2026-11-16T18:21:00", "wieczorna", 2, [(1, [("P6", 0.95)], "ok"), (2, [("P7", 0.94)], "ubytek")])
    b.o("2026-11-16T18:22:00"); s.ok(w2[1])
    b.zd("2026-11-16T18:23:00", "ui", "start_skanu", {"udany": True})
    skan_w3, w3 = b.wieczor("2026-11-16T18:24:00", "wieczorna", 2, [(1, [("P6", 0.95)], "ok"), (2, [("P7", 0.94)], "ubytek")])
    b.o("2026-11-16T18:25:00"); s.zastap_skan(skan_w3)
    b.o("2026-11-16T18:26:00"); s.ok(w3[1])
    b.zd("2026-11-16T18:45:00", "ui", "start_skanu", {"udany": True})
    b.wieczor("2026-11-16T18:46:00", "poranna", 4, [(1, [("P8", 0.95)], "ok")])
    b.zd("2026-11-16T18:47:00", "ui", "start_skanu", {"udany": True})
    b.o("2026-11-16T18:48:00"); s.przyjmij_blad(b._zdarzenie_skanu("2026-11-16T18:48:00"), RuntimeError("analiza przerwana"))
    b.zd("2026-11-16T18:49:00", "ui", "start_skanu", {"udany": True})
    _, w6 = b.wieczor("2026-11-16T18:50:00", "wieczorna", 3, [(1, [("P8", 0.95)], "ok"), (2, [], "ok"), (3, [("P5", 0.90)], "ubytek")])
    b.o("2026-11-16T18:51:00"); s.ukruszona(w6[2])
    b.o("2026-11-16T18:52:00"); s.cofnij(w6[2])
    b.zd("2026-11-16T19:30:00", "system", "program_stop", {"niezakonczone": 0})
    # --- doba 2026-11-17: poranek ---
    b.zd("2026-11-17T06:50:00", "system", "program_start", {"wersja": "test", "wznowione": 0, "znane_pliki": 9})
    b.zd("2026-11-17T06:58:00", "ui", "start_skanu", {"udany": True})
    _, r1 = b.rano_skan("2026-11-17T07:00:00", 4, [
        (1, [("P1", 0.95)], "ok"), (2, [("P2", 0.75), ("P3", 0.60)], "ok"), (3, [("P5", 0.72), ("P4", 0.65)], "ok"),
        (4, [], "ok"), (5, [], "ok"), (6, [("P7", 0.95)], "ok")])
    b.o("2026-11-17T07:02:00"); r.wybierz_kandydata(r1[1], sha16("P2"))
    b.o("2026-11-17T07:03:00"); r.wybierz_kandydata(r1[2], sha16("P4"))
    b.o("2026-11-17T07:04:00"); r.przypisz_recznie(r1[3], b.projekt_id["P6"])
    b.rano_skan("2026-11-17T07:10:00", 5, [(1, [("P8", 0.95)], "ok"), (2, [("P3", 0.70)], "ok"), (3, [("P9", 0.95)], "ok")])
    b.o("2026-11-17T07:12:00"); skan_r3 = r.przyjmij_blad(b._zdarzenie_skanu("2026-11-17T07:12:00"), RuntimeError("analiza przerwana"))
    b.o("2026-11-17T07:13:00"); r.pomin_skan(skan_r3)
    b.o("2026-11-17T07:20:00"); r.zamknij_piec()
    b.rano_skan("2026-11-17T09:00:00", 4, [(1, [("P1", 0.95)], "ok"), (2, [("P5", 0.95)], "ok")])
    b.o("2026-11-17T09:05:00"); r.zamknij_piec()
    # --- doba 2026-11-17: restart bez zamkniecia, zmiana 3 ---
    b.zd("2026-11-17T22:50:00", "system", "program_start", {"wersja": "test", "wznowione": 0, "znane_pliki": 13})
    b.zd("2026-11-17T23:10:00", "ui", "start_skanu", {"udany": True})
    _, w7 = b.wieczor("2026-11-17T23:11:00", "wieczorna", 1, [(1, [("P1", 0.95)], "ok"), (2, [("P3", 0.93)], "ubytek")])
    b.o("2026-11-17T23:14:00"); s.ukruszona(w7[1])
    b.zd("2026-11-18T00:30:00", "system", "program_stop", {"niezakonczone": 0})
    # --- doba 2026-11-18 ---
    b.zd("2026-11-18T07:25:00", "system", "program_start", {"wersja": "test", "wznowione": 0, "znane_pliki": 14})
    b.zd("2026-11-18T07:29:00", "ui", "start_skanu", {"udany": True})
    b.rano_skan("2026-11-18T07:30:00", 6, [(1, [("P3", 0.95)], "ok")])
    b.zd("2026-11-18T18:58:00", "ui", "start_skanu", {"udany": True})
    _, w8 = b.wieczor("2026-11-18T19:00:00", "wieczorna", 2, [(1, [("P6", 0.93)], "ubytek"), (2, [("P7", 0.95)], "ok")])
    b.o("2026-11-18T19:03:00"); s.ok(w8[0])
    b.zd("2026-11-18T19:09:00", "ui", "start_skanu", {"udany": True})
    b.wieczor("2026-11-18T19:10:00", "wieczorna", 3, [(1, [("P8", 0.95)], "popraw_ulozenie")])
    b.zd("2026-11-18T19:30:00", "silnik", "silnik_nie_startuje", {"opis": "proces silnika nie wystartowal"})
    b.baza.zamknij()
    return b.plik


@pytest.fixture(scope="module")
def plik_bazy(tmp_path_factory) -> Path:
    return zbuduj_scenariusz(tmp_path_factory.mktemp("metryki"))


def policz(plik: Path, od: str = OD, do: str = DO, tryb: str = "oba") -> dict:
    with B.otworz(plik, tylko_odczyt=True) as baza:
        return M.policz(baza, od, do, tryb, teraz="2026-11-18T20:00:00")


@pytest.fixture(scope="module")
def raport(plik_bazy) -> dict:
    return policz(plik_bazy)


def pole(d: dict, sciezka: tuple):
    for k in sciezka:
        d = d[k]
    return d


# Tabela oczekiwan - rachunek reczny dla okresu 2026-11-16 .. 2026-11-18, tryb "oba". (id, sciezka, wartosc, jak policzono)
OCZEKIWANE = [
    # --- wieczor: zbior prac = prace skanow aktywnych (przyjety, do_powtorzenia) przyjetych w okresie, jak `prac` w stan_wieczoru
    ("W01", ("wieczor", "skany"), 9, "W1..W9"),
    ("W02", ("wieczor", "skany_aktywne"), 6, "W1, W3, W6, W7, W8 (przyjety) + W9 (do_powtorzenia); W2 zastapiony, W4 plytka nie z trybu, W5 blad"),
    ("W03", ("wieczor", "prace"), 15, "W1 5 + W3 2 + W6 3 + W7 2 + W8 2 + W9 1"),
    ("W04", ("wieczor", "czerwone"), 6, "W1 g2, g3; W3 g2; W6 g3; W7 g2; W8 g1 (W2 g2 - skan zastapiony - nie)"),
    ("W05", ("wieczor", "falszywe_alarmy"), 3, "czerwone z obowiazujacym OK: W1 g3, W3 g2, W8 g1 (OK na W2 g2 przepada z zastapieniem)"),
    ("W06", ("wieczor", "udzial_falszywych"), 3 / 15, "3 / 15 prac (PW: udzial w calosci prac)"),
    ("W07", ("wieczor", "czerwone_ukruszone"), 2, "W1 g2, W7 g2"),
    ("W08", ("wieczor", "czerwone_bez_decyzji"), 1, "W6 g3: Ukruszona cofnieta"),
    ("W09", ("wieczor", "niewykryte_cien"), 1, "W1 g5: zielony z ukruszona_niewykryta"),
    ("W10", ("wieczor", "wykrywalnosc_cien"), 2 / 3, "2 czerwone ukruszone / (2 + 1 niewykryta)"),
    ("W11", ("wieczor", "nieznane"), 2, "W1 g4, W6 g2 (szare, bez kandydata)"),
    ("W12", ("wieczor", "udzial_nieznanych"), 2 / 15, "2 / 15"),
    ("W13", ("wieczor", "powtorzone", "skany"), 9, "W1..W9"),
    ("W14", ("wieczor", "powtorzone", "powtorzone"), 4, "W2 zastapiony, W4 plytka_nie_z_trybu, W5 blad, W9 do_powtorzenia"),
    ("W15", ("wieczor", "powtorzone", "udzial"), 4 / 9, "4 / 9"),
    ("W16", ("wieczor", "powtorzone", "statusy"), {"zastapiony": 1, "plytka_nie_z_trybu": 1, "blad": 1, "do_powtorzenia": 1}, "jw."),
    ("W17", ("wieczor", "czas", "posiedzen"), 5, "16.11: 18:00-18:05, 18:20-18:26, 18:45-18:52; 17.11: 23:10-23:14; 18.11: 18:58-19:10"),
    ("W18", ("wieczor", "czas", "zmian"), 3, "(16.11, zmiana 2), (17.11, zmiana 3), (18.11, zmiana 2)"),
    ("W19", ("wieczor", "czas", "suma_min"), 34.0, "5 + 6 + 7 + 4 + 12"),
    ("W20", ("wieczor", "czas", "srednio_min"), 34 / 3, "34 / 3 zmiany"),
    ("W21", ("wieczor", "czas", "max_min"), 18.0, "16.11 zmiana 2: 5 + 6 + 7"),
    # --- rano: piece ZAMKNIETE z doba w okresie (F1, F2); prace skanow aktywnych i niepominietych (klasa ze stan_pieca)
    ("R01", ("rano", "piece"), 2, "F1, F2"),
    ("R02", ("rano", "piece_otwarte"), 1, "F3 (18.11) niezamkniety - poza metrykami klas"),
    ("R03", ("rano", "prace"), 11, "R1 6 + R2 3 + R4 2 (R3 blad - nieaktywny)"),
    ("R04", ("rano", "klasy"), {"pewna": 4, "przypisana": 3, "poprawka": 1, "dwuznaczna": 1, "nieznana": 2},
     "pewna R1 g1, g6, R2 g1, R4 g2; przypisana R1 g2, g3, g4; poprawka R4 g1; dwuznaczna R2 g2; nieznana R1 g5, R2 g3"),
    ("R05", ("rano", "z_prawda"), 8, "pewna + przypisana + poprawka (projekt po decyzjach technika)"),
    ("R06", ("rano", "top1"), 6, "projekt = 1. kandydat: 4 pewne, R1 g2, R4 g1 (R1 g3 = 2. kandydat, R1 g4 spoza kandydatow)"),
    ("R07", ("rano", "top2"), 7, "top-1 + R1 g3"),
    ("R08", ("rano", "udzial_top1"), 0.75, "6 / 8"),
    ("R09", ("rano", "udzial_top2"), 0.875, "7 / 8"),
    ("R10", ("rano", "nieznane"), 2, "R1 g5 (bez kandydata), R2 g3 (kandydat spoza indeksu)"),
    ("R11", ("rano", "udzial_nieznanych"), 2 / 11, "2 / 11"),
    ("R12", ("rano", "dwuznaczne"), 1, "R2 g2 nierozstrzygnieta do zamkniecia pieca"),
    ("R13", ("rano", "powtorzone", "skany"), 5, "R1..R5 (skany poranne przyjete w okresie)"),
    ("R14", ("rano", "powtorzone", "powtorzone"), 1, "R3 blad"),
    ("R15", ("rano", "powtorzone", "udzial"), 0.2, "1 / 5"),
    ("R16", ("rano", "czas", "posiedzen"), 3, "17.11 06:58-07:20, 09:00-09:05; 18.11 07:29-07:30"),
    ("R17", ("rano", "czas", "zmian"), 2, "(17.11, zmiana 1), (18.11, zmiana 1)"),
    ("R18", ("rano", "czas", "suma_min"), 28.0, "22 + 5 + 1"),
    ("R19", ("rano", "czas", "srednio_min"), 14.0, "28 / 2"),
    ("R20", ("rano", "czas", "max_min"), 27.0, "17.11 zmiana 1: 22 + 5"),
    ("R21", ("rano", "czas_pieca_min", "mediana"), 12.5, "F1 07:00-07:20 = 20, F2 09:00-09:05 = 5"),
    ("R22", ("rano", "czas_pieca_min", "max"), 20.0, "F1"),
    # --- stabilnosc (z dziennika, niezaleznie od trybu)
    ("S01", ("stabilnosc", "dni_pracy"), 3, "doby z wpisami dziennika: 16, 17, 18.11"),
    ("S02", ("stabilnosc", "dni_z_awaria"), 2, "17.11 (restart bez program_stop), 18.11 (silnik nie startuje)"),
    ("S03", ("stabilnosc", "awarie"), 2, "jw."),
    ("S04", ("stabilnosc", "restart_bez_zamkniecia"), 1, "program_start 17.11 22:50 po starcie 06:50 bez program_stop"),
    ("S05", ("stabilnosc", "silnik_nie_startuje"), 1, "18.11 19:30"),
    ("S06", ("stabilnosc", "najdluzsza_seria"), 1, "16.11"),
    ("S07", ("stabilnosc", "obecna_seria"), 0, "ostatnia doba (18.11) z awaria"),
    ("S08", ("stabilnosc", "doby_z_awaria"), ["2026-11-17", "2026-11-18"], "jw."),
    # --- ocena wzgledem progow odbioru (PW "Testy odbiorcze i kryteria")
    ("O01", ("ponizej_progu",), ["falszywe_alarmy", "top1", "top2", "nieznane_wieczor", "nieznane_rano", "powtorzone_wieczor",
                                 "powtorzone_rano", "dni_bez_awarii"], "czas wieczor 11,3 min <= 20 - jedyna metryka w progu"),
    ("O02", ("kod",), 3, "ponizej progu = kod 3"),
]


@pytest.mark.parametrize("sciezka, oczekiwane", [(w[1], w[2]) for w in OCZEKIWANE], ids=[w[0] for w in OCZEKIWANE])
def test_oczekiwane(raport, sciezka, oczekiwane):
    wartosc = pole(raport, sciezka)
    if isinstance(oczekiwane, float):
        assert wartosc == pytest.approx(oczekiwane, abs=1e-9)
    else:
        assert wartosc == oczekiwane


def test_wiersze_metryk_maja_wartosci_tabeli(raport):
    """Wiersze strony (tabela metryk) = wartosci z tabeli oczekiwan; M2 = "wymaga zmiany schematu", bez wartosci."""
    wiersze = {m["klucz"]: m for m in raport["metryki"]}
    oczekiwane = {"falszywe_alarmy": (3 / 15, 3, 15, "PONIZEJ"), "top1": (0.75, 6, 8, "PONIZEJ"), "top2": (0.875, 7, 8, "PONIZEJ"),
                  "nieznane_wieczor": (2 / 15, 2, 15, "PONIZEJ"), "nieznane_rano": (2 / 11, 2, 11, "PONIZEJ"),
                  "czas_wieczor": (34 / 3, None, None, "OK"), "powtorzone_wieczor": (4 / 9, 4, 9, "PONIZEJ"),
                  "powtorzone_rano": (0.2, 1, 5, "PONIZEJ"), "dni_bez_awarii": (1, None, None, "PONIZEJ")}
    for klucz, (wartosc, licznik, mianownik, ocena) in oczekiwane.items():
        m = wiersze[klucz]
        assert m["wartosc"] == pytest.approx(wartosc), klucz
        assert (m["licznik"], m["mianownik"], m["ocena"]) == (licznik, mianownik, ocena), klucz
    assert wiersze["m2"]["wartosc"] is None and wiersze["m2"]["ocena"] == "wymaga zmiany schematu"
    assert raport["m2"]["dostepne"] is False and "zmiany schematu" in raport["m2"]["powod"]


def test_strona_do_60_linii_z_liczbami_scenariusza(raport):
    linie = M.strona(raport)
    assert 0 < len(linie) <= 60
    tekst = "\n".join(linie)
    for fragment in ("3/15", "6/8", "7/8", "2/15", "2/11", "4/9", "1/5", "20.0%", "75.0%", "87.5%", "11.3 min", "wymaga zmiany schematu",
                     "2026-11-16 .. 2026-11-18", "kod 3"):
        assert fragment in tekst, fragment
    assert all(len(x) <= 140 for x in linie)
    assert tekst.isascii()


def test_dane_osobowe_0_nazw_w_raporcie_i_json(raport):
    """Kryterium: 0 nazw folderow, plikow i osob w raporcie (strona i JSON) - tylko liczby."""
    tekst = "\n".join(M.strona(raport)) + "\n" + json.dumps(raport, ensure_ascii=False)
    for slowo in ZAKAZANE:
        assert slowo not in tekst, slowo


def test_okres_zawezony(plik_bazy):
    """Okres 16..17.11: bez W8, W9, R5, F3 i awarii silnika z 18.11 (rachunek reczny jak w tabeli, bez dnia 18.11)."""
    w = policz(plik_bazy, "2026-11-16", "2026-11-17")
    assert w["okres"] == {"od": "2026-11-16", "do": "2026-11-17", "tryb": "oba", "doby": 2}
    ww = w["wieczor"]
    assert (ww["skany"], ww["prace"], ww["czerwone"], ww["falszywe_alarmy"], ww["nieznane"]) == (7, 12, 5, 2, 2)
    assert ww["udzial_falszywych"] == pytest.approx(2 / 12)
    assert (ww["powtorzone"]["powtorzone"], ww["powtorzone"]["skany"]) == (3, 7)
    assert (ww["czas"]["zmian"], ww["czas"]["suma_min"], ww["czas"]["max_min"]) == (2, 22.0, 18.0)
    wr = w["rano"]
    assert (wr["piece"], wr["piece_otwarte"], wr["prace"], wr["top1"], wr["top2"]) == (2, 0, 11, 6, 7)
    assert (wr["powtorzone"]["powtorzone"], wr["powtorzone"]["skany"]) == (1, 4)
    assert (wr["czas"]["zmian"], wr["czas"]["suma_min"]) == (1, 27.0)
    st = w["stabilnosc"]
    assert (st["dni_pracy"], st["dni_z_awaria"], st["najdluzsza_seria"], st["obecna_seria"]) == (2, 1, 1, 0)
    assert st["doby_z_awaria"] == ["2026-11-17"]


def test_jedna_doba(plik_bazy):
    """Doba 17.11: wieczor tylko W7 (zmiana 3), rano F1 i F2."""
    w = policz(plik_bazy, "2026-11-17", "2026-11-17")
    ww = w["wieczor"]
    assert (ww["skany"], ww["prace"], ww["czerwone"], ww["falszywe_alarmy"], ww["czerwone_ukruszone"]) == (1, 2, 1, 0, 1)
    assert ww["udzial_falszywych"] == 0.0
    assert (ww["czas"]["zmian"], ww["czas"]["suma_min"]) == (1, 4.0)
    assert (w["rano"]["piece"], w["rano"]["prace"]) == (2, 11)


@pytest.mark.parametrize("tryb, jest, nie_ma", [("wieczor", "wieczor", "rano"), ("rano", "rano", "wieczor")])
def test_tryb_wieczor_albo_rano(plik_bazy, tryb, jest, nie_ma):
    w = policz(plik_bazy, tryb=tryb)
    assert w["okres"]["tryb"] == tryb
    assert w[jest] is not None and w[nie_ma] is None
    klucze = {m["klucz"] for m in w["metryki"]}
    assert not any(k.endswith("_" + nie_ma) for k in klucze)
    assert ("top1" in klucze) == (tryb == "rano") and ("falszywe_alarmy" in klucze) == (tryb == "wieczor")
    assert "dni_bez_awarii" in klucze and "m2" in klucze  # stabilnosc i M2 niezaleznie od trybu
    assert w["stabilnosc"]["dni_pracy"] == 3
    assert len(M.strona(w)) <= 60


def test_pusta_baza(tmp_path):
    """Baza bez danych: kazda metryka "brak danych", kod 0, strona do 60 linii."""
    plik = tmp_path / "pusta.sqlite"
    B.otworz(plik).zamknij()
    w = policz(plik)
    assert w["wieczor"]["prace"] == 0 and w["wieczor"]["udzial_falszywych"] is None
    assert w["rano"]["piece"] == 0 and w["rano"]["udzial_top1"] is None
    assert w["stabilnosc"]["dni_pracy"] == 0
    assert all(m["ocena"] in ("brak danych", "wymaga zmiany schematu") for m in w["metryki"])
    assert w["kod"] == 0 and w["ponizej_progu"] == []
    assert len(M.strona(w)) <= 60
    json.dumps(w)


def test_posiedzenia_granica_przerwy():
    """Przerwa dluzsza niz ``przerwa_min`` konczy posiedzenie; rowna - nie."""
    t = ["2026-11-16T18:00:00", "2026-11-16T18:10:00", "2026-11-16T18:20:01", "2026-11-16T18:21:00"]
    assert M.posiedzenia(t, 10) == [("2026-11-16T18:00:00", "2026-11-16T18:10:00"), ("2026-11-16T18:20:01", "2026-11-16T18:21:00")]
    assert M.posiedzenia(list(reversed(t)), 10) == M.posiedzenia(t, 10)
    assert M.posiedzenia([], 10) == []
    assert M.posiedzenia(t, 15) == [("2026-11-16T18:00:00", "2026-11-16T18:21:00")]


def test_seria_dni_bez_awarii(tmp_path):
    """8 dni pracy (01-05, 07-09.11; 06.11 bez programu), awaria na 03.11: najdluzsza i obecna seria = 5 (04, 05, 07, 08, 09)."""
    plik = tmp_path / "stab.sqlite"
    with B.otworz(plik) as baza:
        for d in ("01", "02", "03", "04", "05", "07", "08", "09"):
            baza.zdarzenie("system", "program_start", {"wersja": "test"}, czas=f"2026-11-{d}T07:00:00")
            if d == "03":
                baza.zdarzenie("ui", "start_skanu", {"udany": True}, czas="2026-11-03T08:00:00")  # brak program_stop: restart 04.11 = awaria 03.11
            else:
                baza.zdarzenie("system", "program_stop", {"niezakonczone": 0}, czas=f"2026-11-{d}T15:00:00")
    w = policz(plik, "2026-11-01", "2026-11-09")
    st = w["stabilnosc"]
    assert (st["dni_pracy"], st["dni_z_awaria"], st["awarie"], st["najdluzsza_seria"], st["obecna_seria"]) == (8, 1, 1, 5, 5)
    assert st["doby_z_awaria"] == ["2026-11-03"]
    assert {m["klucz"]: m["ocena"] for m in w["metryki"]}["dni_bez_awarii"] == "OK"
    assert w["kod"] == 0


def test_ocena_progu():
    assert M.ocena(0.15, 0.15, "max") == "OK" and M.ocena(0.1501, 0.15, "max") == "PONIZEJ"
    assert M.ocena(0.85, 0.85, "min") == "OK" and M.ocena(0.8499, 0.85, "min") == "PONIZEJ"
    assert M.ocena(None, 0.85, "min") == "brak danych"


def test_bledne_parametry(plik_bazy):
    with B.otworz(plik_bazy, tylko_odczyt=True) as baza:
        with pytest.raises(ValueError):
            M.policz(baza, "2026-11-18", "2026-11-16")
        with pytest.raises(ValueError):
            M.policz(baza, "16.11.2026", "2026-11-18")
        with pytest.raises(ValueError):
            M.policz(baza, OD, DO, "poranek")


def test_raport_tylko_odczyt_i_schemat_bez_zmian(plik_bazy, raport):
    """Raport nie zmienia pliku bazy ani schematu (wersja 1, 11 tabel z planu 3.4) - zmiana modelu danych wymaga zgody wlasciciela."""
    przed = hashlib.sha256(plik_bazy.read_bytes()).hexdigest()
    policz(plik_bazy)
    assert raport_metryk.main(["--baza", str(plik_bazy), "--od", OD, "--do", DO]) == 3
    assert hashlib.sha256(plik_bazy.read_bytes()).hexdigest() == przed
    assert B.WERSJA_SCHEMATU == 1 and max(B.MIGRACJE) == 1 and len(B.TABELE) == 11
    with B.otworz(plik_bazy, tylko_odczyt=True) as baza:
        assert baza.wersja() == 1


def _uruchom(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        kod = raport_metryk.main(argv)
    return kod, out.getvalue(), err.getvalue()


def test_cli_jedno_polecenie_jedna_strona_i_json(plik_bazy, raport, tmp_path):
    """M1: jedno polecenie = jedna strona na stdout (do 60 linii) + JSON z tymi samymi polami; kod 3 = ponizej progu."""
    cel = tmp_path / "metryki.json"
    kod, out, err = _uruchom(["--baza", str(plik_bazy), "--od", OD, "--do", DO, "--tryb", "oba", "--json", str(cel),
                              "--ustawienia", str(STANOWISKO / "ustawienia.przyklad.toml")])
    assert kod == 3, err
    linie = out.rstrip("\n").split("\n")
    assert 0 < len(linie) <= 60
    assert "3/15" in out and "wymaga zmiany schematu" in out
    j = json.loads(cel.read_text(encoding="utf-8"))
    for w in OCZEKIWANE:
        if w[1][0] in ("wieczor", "rano", "stabilnosc"):
            wart = pole(j, w[1])
            assert wart == pytest.approx(w[2]) if isinstance(w[2], float) else wart == w[2], w[0]
    assert j["kod"] == 3
    for slowo in ZAKAZANE:
        assert slowo not in out and slowo not in cel.read_text(encoding="utf-8"), slowo


def test_cli_domyslny_okres_7_dob(plik_bazy):
    """Bez ``--od``: 7 dob konczacych sie na ``--do`` (dane sprzed 16.11 nie istnieja - wartosci jak w tabeli)."""
    kod, out, _ = _uruchom(["--baza", str(plik_bazy), "--do", DO])
    assert kod == 3
    assert "2026-11-12 .. 2026-11-18" in out


def test_cli_tryb_wieczor(plik_bazy):
    kod, out, _ = _uruchom(["--baza", str(plik_bazy), "--od", OD, "--do", DO, "--tryb", "wieczor"])
    assert kod == 3 and "top-1" not in out and "3/15" in out


@pytest.mark.parametrize("argv", [
    ["--od", "2026-11-18", "--do", "2026-11-16"],
    ["--od", "16.11.2026", "--do", DO],
    ["--tryb", "poranek"],
])
def test_cli_bledne_argumenty_kod_2(plik_bazy, argv):
    kod, out, err = _uruchom(["--baza", str(plik_bazy)] + argv)
    assert kod == 2 and err and not out


def test_cli_brak_bazy_kod_2(tmp_path):
    kod, out, err = _uruchom(["--baza", str(tmp_path / "nie_ma.sqlite"), "--od", OD, "--do", DO])
    assert kod == 2 and "brak pliku bazy" in err and not out
    assert not (tmp_path / "nie_ma.sqlite").exists()


def test_modul_nie_importuje_okna_ani_silnika():
    """Raport dziala w osobnym procesie bez Qt i bez silnika (tylko biblioteka standardowa + baza / session)."""
    import os
    import subprocess

    kod = ("import sys; import stanowisko.metryki, raport_metryk; "
           "zle = [m for m in ('PySide6', 'numpy', 'trimesh', 'open3d', 'stanowisko.silnik', 'stanowisko.aplikacja') if m in sys.modules]; "
           "print(','.join(zle)); sys.exit(1 if zle else 0)")
    r = subprocess.run([sys.executable, "-c", kod], cwd=STANOWISKO, capture_output=True, text=True,
                       env={**os.environ, "PYTHONPATH": f"{STANOWISKO}{os.pathsep}{STANOWISKO / 'narzedzia'}"})
    assert r.returncode == 0, r.stdout + r.stderr
