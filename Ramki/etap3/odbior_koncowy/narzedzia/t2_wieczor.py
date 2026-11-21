"""t2_wieczor.py - sterownik testu koncowego T2 (wieczor od poczatku do konca): narzedzie POMIARU, nie test jednostkowy.

Co robi: uruchamia PRAWDZIWY program "Stanowisko" (``stanowisko.aplikacja.main`` - ta sama funkcja, ktora wola
``Stanowisko.cmd`` przez ``python -m stanowisko.aplikacja``; prawdziwy obserwator folderu, prawdziwy proces silnika, prawdziwe
okno), podaje pliki symulatorem skanera programu (``narzedzia/symulator_skanera.py`` jako osobny proces: ``--rownolegle 1``,
``--odstep``, ``--zle uciety``) wg pliku scenariusza z tabela prawdy (``t2_scenariusz.json``), wykonuje decyzje technika
KLIKNIECIAMI w oknie (po nazwach obiektow) i mierzy liczby kryterium T2. Wynik: ``<roboczy>/t2_wynik.json`` i tabela
``t2_wynik.txt`` (takze na stdout) - tylko ``sha16`` plikow skanow, numery plytek i gniazd, bez nazw plikow.

Uruchomienie (z KATALOGU PROGRAMU, interpreterem programu):
    instalacja z paczki (jedna linia; ``Polecenie.cmd`` robi ``cd`` do katalogu programu wersji i uruchamia python wersji):
        set QT_QPA_PLATFORM=offscreen
        <K>\\Polecenie.cmd <ODB>\\narzedzia\\t2_wieczor.py --ustawienia-wzor <K>\\ustawienia.toml --roboczy <ROB>\\t2
            --projekty <folder_cyrkon>                                   (10 plikow co 60 s, ok. 11-13 min, limit 30 min)
    proba z kopii repo (PC): cd /d <REPO>\\Ramki\\stanowisko && <PC-katalog>\\koordynator\\narz\\py.cmd <ODB>\\narzedzia\\t2_wieczor.py ...
    proba skrocona:       ... --odstep 5 --wybierz 2,4,5,7     (albo --plytki 3 = trzy pierwsze pozycje scenariusza)
    Katalog ``--roboczy`` musi byc nowy albo pusty. W srodowisku programu nie ma ``psutil`` - procesy potomne sterownik sledzi
    wtedy przez ``multiprocessing.active_children()`` (proces roboczy silnika) i uchwyt symulatora.

Czego sterownik NIE robi: nie podmienia i nie lata niczego w programie (zadnych atrap silnika, zadnego monkeypatch), nie
zmienia plikow programu ani danych odniesienia. Program dostaje wlasny plik ustawien w katalogu roboczym: kopia pliku
``--ustawienia-wzor`` z podmienionymi sciezkami w ``[sciezki]`` (baza, logi, wyniki, podglady, pamiec puli, folder eksportu
skanera - wszystko w ``--roboczy``; ``folder_cyrkon`` = ``--projekty``) i - tylko gdy lista jest pusta - ``[sesja] operatorzy``
= ["Technik A"]. Reszta ustawien (progi, uklady plytek, silnik, ramki, Excel) zostaje jak we wzorze.

ODSTEPSTWA od drogi ``Stanowisko.cmd`` (wszystkie):
  1. program biegnie w procesie sterownika: ``QApplication`` tworzy sterownik tuz przed ``main()`` (``main`` bierze istniejaca
     instancje - tak jest napisany), modul glowny procesu to ten plik, a nie ``stanowisko.aplikacja`` (proces roboczy silnika
     importuje ten plik jako ``__mp_main__``; plik nie importuje Qt na poziomie modulu),
  2. program dostaje opcje ``--zamknij-po <limit>`` (bezpiecznik) i jest zamykany przez ``QApplication.quit()`` po pomiarze,
  3. okno moze byc ``offscreen`` (``QT_QPA_PLATFORM=offscreen``) - wynik podaje platforme Qt,
  4. w watku okna dodatkowo dziala zegar sterownika (co 20 ms: odczyt ``kontroler.stan()`` i ewentualne klikniecie) - jego
     wlasny czas jest mierzony i podany w wyniku (``sterownik_tyk_max_ms``, ``sterownik_tyk_max_co``); wlicza sie do przerw
     petli. ``QTest.mouseClick`` przetwarza zdarzenia okna w srodku klikniecia: zegar tyka wtedy dalej (tykniecia
     "w srodku klikniecia" mierza przerwy, scenariusza nie prowadza), wiec dlugie tykniecie sterownika nie musi byc przerwa
     petli - przerwa jest zawsze odstepem dwoch kolejnych tykniec.

MIEJSCA, w ktorych sterownik zaglada do wnetrza programu (tylko odczyt, obiekty publiczne):
  a) okno: ``QApplication.topLevelWidgets()`` -> obiekt o nazwie ``okno_wieczor``; jego atrybut ``k`` (kontroler - ten sam
     obiekt, ktory ``main`` przekazal oknu), ``mapa.srodek_gniazda(nr)`` (punkt klikniecia gniazda), ``pokazana_plytka()``,
     ``ochrona_aktywna()`` / ``mapa.przygaszona()`` (mapa przygaszona po zmianie - klikniecia sa wtedy pomijane, technik tez
     czeka), ``mapa.grab()`` + ``mapa.punkt_probny(nr)`` (kolor gniazda z obrazu), ``widok.praca_id`` (ktora prace pokazuje widok),
  b) stan: ``kontroler.stan()`` (``StanAplikacji``: ``plytki``, ``analiza`` = ``Postep`` z polami ``sha16`` i ``od``,
     ``kolejka``, ``pula``, ``pytania``, ``komunikaty``, ``do_dofrezowania_biezaca``, ``wymaga_operatora``),
  c) po zamknieciu programu: baza SQLite otwarta tylko do odczytu (tabele ``skany`` i ``zdarzenia`` - bez tabel z nazwami)
     i log programu ``logi/stanowisko.log`` (wiersze WARNING / ERROR trafiaja do pliku w katalogu roboczym, do wyniku tylko
     liczniki wg slow kluczowych).
Decyzje i odpowiedzi ida WYLACZNIE kliknieciami (``QTest.mouseClick``) w obiekty: ``osoba_0`` (wybor osoby), kafelek
``plytka_<skan_id>`` (wybor plytki), mapa (gniazdo), ``przycisk_ukruszona``, ``przycisk_ok``, ``odp_odrzuc_ponowny_skan`` /
``odp_potwierdz_ponowny_skan``, ``odp_podaj_numer_plytki_<n>`` (odpowiedz na pytanie "Podaj numer plytki" - numer z prawdy; na
plytkach kwadratowych program numeru nie odczytuje - raport R59: dolki poza polem skanu). Polecen kontrolera sterownik nie wola.

Co jest mierzone i jak:
  * obsluzone zgodnie z prawda n z N: dla kazdego pliku oczekiwany status / uklad / numer z tabeli prawdy wobec stanu programu
    (plik uciety: brak plytki + zdarzenie ``plik_odrzucony`` w bazie; numer = odczytany przez program ALBO podany przez
    technika na pytanie programu - zrodlo numeru jest w wyniku przy kazdej plytce i w polu ``numery_plytek``; plytka nie z
    trybu: program o numer nie pyta - numer porownywany tylko, gdy go odczytal; niezgodny uklad: bez ukladu i numeru),
  * start analizy od zapisu: ``analiza.od`` (czas zdarzenia "start" procesu silnika, zegar ``time.time()``) minus ``koniec``
    zapisu pliku z dziennika symulatora (``time.time()`` po zamknieciu pliku). To pomiar DOSLOWNY, o ile sterownik zobaczyl
    analize tej plytki w ktoryms z odczytow co 20 ms; inaczej "NIE ZMIERZONO". Kryterium (< 1 s) jest liczone dla WSZYSTKICH
    plikow dobrych; plik zapisany, gdy poprzednia plytka jest jeszcze liczona (pole ``kolejka_przy_zapisie`` > 0), czeka w
    kolejce silnika - takie wartosci sa dodatkowo wskazane w polu ``czekaly_w_kolejce`` (przyczyna, nie wylaczenie z kryterium;
    w probie skroconej z odstepem krotszym niz czas analizy sa nieuniknione),
  * czas do mapy: chwila, w ktorej plytka pierwszy raz jest w ``stan().plytki`` (odczyt co 20 ms w watku okna = GORNE
    OGRANICZENIE z dokladnoscia do okresu zegara i przerw petli) minus ``koniec`` zapisu; mediana, maksimum, pierwsza plytka
    osobno (pula zimna) z licznikami "do 40 s: n z m"; obok ``czas_s`` analizy podany przez program i - gdy okno samo
    pokazalo mape tej plytki (``okno.pokazana_plytka()``, bez klikniecia sterownika w kafelek) - chwila pokazania (``w_oknie``;
    okno nie przelacza mapy, gdy technik oglada inna plytke: wtedy "NIE ZMIERZONO"),
  * przerwy petli okna: zegar Qt co 20 ms w watku okna; przerwa = odstep kolejnych tykniec; maksimum i liczba > 200 ms
    (od pierwszego tykniecia w ``app.exec()`` do tykniecia zamykajacego; start programu przed pokazaniem okna i samo
    zamykanie programu NIE sa mierzone - czas tykniecia zamykajacego jest podany osobno),
  * kolory prac: po pojawieniu sie plytki przyjetej sterownik wybiera jej kafelek i - gdy mapa nie jest chroniona - czyta
    kolor KAZDEJ pracy Z OBRAZU mapy (``mapa.grab()``, piksel w ``mapa.punkt_probny(nr)``; klasa koloru wg tabeli
    ``statusy.STATUSY``) - PRZED jakimkolwiek kliknieciem w te plytke; odczyt jest w wyniku dla kazdej pracy,
  * decyzje technika (decyzja koordynatora nr 1 po recenzji): sterownik nasladuje technika, ktory oglada tylko to, co program
    mu wskazal - "Ukruszona" klika WYLACZNIE na pracach z ubytkiem wg prawdy pokazanych na czerwono albo zolto; praca z
    ubytkiem wg prawdy pokazana na zielono (albo inaczej) = PRZEOCZONA przez program: sterownik jej nie klika, pozycji nie
    ma wtedy na liscie programu i werdykt "lista = prawda" to FAIL z licznikiem; praca cala wg prawdy pokazana na czerwono
    = falszywy alarm: sterownik klika "OK" (licznik osobno, listy nie psuje); prac zoltych calych wg prawdy sterownik nie
    klika (liczy je),
  * ochrona klikniec mapy (A-P2 i E3-P15: mapa przygaszona ok. 800 ms po zmianie zawartosci albo komunikatow nad mapa):
    sterownik czeka na jej zdjecie; przed kliknieciem decyzji sprawdza, ze widok pracy (``okno.widok.praca_id``) pokazuje
    wlasnie te prace; klikniecie bez skutku ponawia od klikniecia gniazda (liczba ponowien i czekan w wyniku),
  * lista "do dofrezowania": ``do_dofrezowania_biezaca`` wobec WSZYSTKICH prac z ubytkiem w prawdzie plytek przyjetych
    (rowna / roznice) - prawda nie zalezy od tego, co sterownik kliknal.
Zdarzenia srodowiska (proces silnika ginie, restart silnika, blad analizy, przekroczony limit) sa wynikiem: pola
``zdarzenia_srodowiska`` i ``przerwano``; sterownik ma limit czasu (``--limit``) i straznika w osobnym watku, ktory po
``limit + 120 s`` zapisuje wynik czesciowy, konczy procesy potomne i wychodzi kodem 3.

Kody wyjscia: 0 = pomiar wykonany w calosci (werdykty kryterium sa w pliku wyniku; wiersz laczny "T2 LACZNIE"), 1 = tylko z
opcja ``--wymagaj-zal``: pomiar wykonany, ale "T2 LACZNIE" nie jest ZAL, 2 = blad przygotowania / opcji,
3 = PRZERWANO: limit czasu, 4 = program zakonczyl sie bledem albo sterownik napotkal wyjatek.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sqlite3
import statistics
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path

TU = Path(__file__).resolve().parent
PROG_PRZERWY_MS = 200.0
OKRES_MS = 20
SLOWA_SRODOWISKA = ("0xC0000005", "c000070a", "0xC0000142", "KnownDlls", "proces roboczy", "proces silnika", "nieudana",
                    "limit", "nie wystartowal", "przerwana", "Traceback")
KLUCZE_SCIEZEK = {"folder_eksportu_skanera": "eksport", "folder_prywatne": "prywatne", "folder_millbox": "millbox",
                  "baza": "dane/stanowisko.sqlite", "log_excel": "dane/log_excel.csv", "wyniki": "dane/wyniki",
                  "podglady": "dane/podglady", "pula_cache": "dane/pula_cache", "logi": "dane/logi",
                  "kalibracja_ramek": "dane/kalibracja_ramek.json"}


# --- przygotowanie -------------------------------------------------------------------------------
def zloz_ustawienia(wzor: Path, roboczy: Path, projekty: Path, pula_cache: Path | None) -> Path:
    """Kopia pliku ustawien z podmienionymi sciezkami ``[sciezki]`` (i operatorem, gdy lista pusta); zwraca nowy plik."""
    import tomllib

    tekst = wzor.read_text(encoding="utf-8")
    stare = tomllib.loads(tekst)
    cele = {k: (roboczy / v).as_posix() for k, v in KLUCZE_SCIEZEK.items()}
    cele["folder_cyrkon"] = projekty.as_posix()
    if pula_cache is not None:
        cele["pula_cache"] = pula_cache.as_posix()
    brak_osob = not (stare.get("sesja") or {}).get("operatorzy")
    wynik, sekcja, zrobione = [], "", set()

    def dopisz_brakujace() -> None:
        if sekcja == "sciezki":
            wynik.extend(f'{k} = "{v}"' for k, v in cele.items() if k not in zrobione)
            zrobione.update(cele)
        if sekcja == "sesja" and brak_osob and "operatorzy" not in zrobione:
            wynik.append('operatorzy = ["Technik A"]')
            zrobione.add("operatorzy")

    for linia in tekst.splitlines():
        m = re.match(r"^\s*\[([^\]]+)\]", linia)
        if m:
            dopisz_brakujace()
            sekcja = m.group(1).strip()
            wynik.append(linia)
            continue
        k = re.match(r"^\s*([A-Za-z0-9_]+)\s*=", linia)
        if k and sekcja == "sciezki" and k.group(1) in cele:
            wynik.append(f'{k.group(1)} = "{cele[k.group(1)]}"')
            zrobione.add(k.group(1))
        elif k and sekcja == "sesja" and k.group(1) == "operatorzy" and brak_osob:
            wynik.append('operatorzy = ["Technik A"]')
            zrobione.add("operatorzy")
        else:
            wynik.append(linia)
    dopisz_brakujace()
    if brak_osob and "operatorzy" not in zrobione:
        wynik += ["", "[sesja]", 'operatorzy = ["Technik A"]']
    plik = roboczy / "ustawienia_t2.toml"
    plik.write_text("\n".join(wynik) + "\n", encoding="utf-8")
    nowe = tomllib.loads(plik.read_text(encoding="utf-8"))
    for k, v in cele.items():
        if nowe["sciezki"].get(k) != v:
            raise SystemExit(f"ustawienia: nie udalo sie podmienic [sciezki] {k}")
    if not nowe.get("sesja", {}).get("operatorzy"):
        raise SystemExit("ustawienia: pusta lista [sesja] operatorzy")
    return plik


def przeskaluj_stl(zrodlo: Path, cel: Path, skala_xy: float) -> None:
    """Binarny STL ze wspolrzednymi X i Y wierzcholkow pomnozonymi przez ``skala_xy`` (plik pochodny w katalogu roboczym)."""
    import numpy as np

    dane = zrodlo.read_bytes()
    n = struct.unpack("<I", dane[80:84])[0]
    typ = np.dtype([("n", "<f4", (3,)), ("v", "<f4", (3, 3)), ("a", "<u2")])
    if len(dane) != 84 + n * typ.itemsize:
        raise SystemExit("skan_przeskalowany: plik zrodlowy nie jest binarnym STL")
    t = np.frombuffer(dane, dtype=typ, count=n, offset=84).copy()
    t["v"][:, :, 0] *= skala_xy
    t["v"][:, :, 1] *= skala_xy
    cel.parent.mkdir(parents=True, exist_ok=True)
    cel.write_bytes(dane[:84] + t.tobytes())


def przygotuj_zestaw(scen: dict, wybrane: list, dane_ref: Path, roboczy: Path, skrot16) -> tuple:
    """Zwraca (pozycje tabeli prawdy, lista plikow zrodlowych dobrych w kolejnosci, czy jest plik uciety)."""
    pozycje, zrodla, uciety = [], [], False
    for p in scen["plytki"]:
        if p["nr"] not in wybrane:
            continue
        w = {"nr": p["nr"], "rodzaj": p["rodzaj"], "sklad": p.get("sklad", ""), "oczekiwany_status": p["oczekiwany_status"],
             "decyzje": p.get("decyzje", "brak")}
        if p["rodzaj"] == "uciety":
            uciety = True
            pozycje.append(w)
            continue
        skan = dane_ref / p["katalog"] / (p["skan"] + ".stl")
        prawda_plik = dane_ref / p["katalog"] / (p["skan"] + ".json")
        if not skan.is_file() or not prawda_plik.is_file():
            raise SystemExit(f"scenariusz nr {p['nr']}: brak skanu albo pliku prawdy w {p['katalog']}")
        prawda = json.loads(prawda_plik.read_text(encoding="utf-8"))
        sha_zrodla = skrot16(skan.read_bytes())
        if p.get("sha16") and p["sha16"] != sha_zrodla:
            raise SystemExit(f"scenariusz nr {p['nr']}: sha16 pliku w danych odniesienia ({sha_zrodla}) inne niz w scenariuszu ({p['sha16']})")
        prace = prawda.get("prace") or []
        if p["rodzaj"] == "skan_przeskalowany":
            plik = roboczy / "zrodla" / f"pochodny_{p['nr']:02d}.stl"
            przeskaluj_stl(skan, plik, float(p["skala_xy"]))
        else:
            plik = skan
        w.update(uklad=prawda.get("plytka"), numer=prawda.get("numer"), prac=len(prace),
                 drgniec=sum(1 for x in prace if x.get("drgniecie")),
                 gniazda_ubytki=sorted(int(x["gniazdo"]) for x in prace if x.get("ubytki") and x.get("gniazdo") is not None),
                 gniazda_prac=sorted(int(x["gniazdo"]) for x in prace if x.get("gniazdo") is not None),
                 sha16=skrot16(plik.read_bytes()) if plik != skan else sha_zrodla, sha16_zrodla=sha_zrodla,
                 rozmiar_mb=round(plik.stat().st_size / 1e6, 1))
        if w["oczekiwany_status"] == "przyjety" and w["drgniec"]:
            raise SystemExit(f"scenariusz nr {p['nr']}: oczekiwany 'przyjety', a prawda ma prace z drgnieciem")
        w["do_dofrezowania"] = w["gniazda_ubytki"] if w["decyzje"] == "ukruszona_wg_prawdy" else []
        pozycje.append(w)
        zrodla.append(plik)
    if not zrodla:
        raise SystemExit("zestaw bez dobrego pliku")
    return pozycje, zrodla, uciety


# --- sterownik w watku okna ----------------------------------------------------------------------
class Sterownik:
    """Zegar w watku okna: przerwy petli, odczyt stanu, klikniecia wg tabeli prawdy, start symulatora, koniec pomiaru."""

    def __init__(self, a, pozycje: list, polecenie_symulatora: list, katalog_programu: Path, scen: dict):
        self.a, self.pozycje, self.polecenie, self.katalog_programu, self.scen = a, pozycje, polecenie_symulatora, katalog_programu, scen
        self.dobre = {p["sha16"]: p for p in pozycje if p["rodzaj"] != "uciety"}
        self.t0 = time.time()
        self.ostatni = None
        self.przerwy: list = []  # (ms, sekunda od startu, co sterownik robil w poprzednim tyknieciu)
        self.przerwa_max_ms, self.tykniec, self.tyk_max_ms = 0.0, 0, 0.0
        self.okno = self.k = None
        self.symulator: subprocess.Popen | None = None
        self.t_gotowe = self.t_symulator = self.t_symulator_koniec = self.t_koniec_plytek = None
        self.starty: dict = {}  # sha16 -> (analiza.od, chwila odczytu)
        self.mapy: dict = {}  # sha16 -> chwila pierwszego odczytu plytki w stanie
        self.mapy_okno: dict = {}  # sha16 -> chwila, w ktorej okno pierwszy raz pokazywalo mape tej plytki (samo, bez klikniecia kafelka)
        self.kafelki_klikniete: set = set()  # skan_id kafelkow kliknietych przez sterownik
        self.numery_podane: dict = {}  # sha16 -> numer plytki podany kliknieciem na pytanie brak_numeru_plytki
        self.numery_programu: dict = {}  # sha16 -> numer odczytany przez program ze skanu (None = nie odczytal)
        self.skan_id: dict = {}  # sha16 -> skan_id
        self.kolejka_probki: list = []  # (czas, kolejka.razem)
        self.komunikaty: dict = {}  # rodzaj -> [pierwszy raz (s od startu), ile odczytow nowych id]
        self.komunikaty_id: set = set()
        self.pytania: dict = {}  # id -> (rodzaj, skan_id, s od startu)
        self.zadania: collections.deque = collections.deque()
        self.decyzje: list = []
        self.odpowiedzi: list = []
        self.czekaj_do = 0.0
        self.ostatnia_czynnosc = ""
        self.przerwano: str | None = None
        self.blad: str | None = None
        self.koncowy: dict | None = None
        self.zakonczono = False
        self.osoba_kliknieta = 0.0
        self.pytanie_klik: dict = {}
        self.pytanie_od: dict = {}
        self.pytania_porzucone: set = set()
        self.w_tyku = False
        self.tykniec_zagniezdzonych = 0
        self.tyk_max_co = ""
        self.tyk_koniec_ms: float | None = None
        self.t_pusta: float | None = None  # od kiedy kolejka jest nieprzerwanie pusta i nic nie jest liczone
        self.kolory_ekranu: dict = {}  # sha16 -> {gniazdo: {piksel, klasa, status, klasa_stanu}} - odczyt z obrazu mapy PRZED kliknieciami
        self.klasy_hex: dict | None = None  # kolor ekranu #rrggbb -> zbior klas koloru (tabela statusow programu)
        self.przeglady: list = []  # plytki, ktorych mapy sterownik obejrzal (albo nie zdolal)

    # ---- pomocnicze: tylko nazwy obiektow okna
    def _w(self, nazwa: str):
        from PySide6.QtWidgets import QWidget

        w = self.okno.findChild(QWidget, nazwa)
        return w if w is not None and w.isVisibleTo(self.okno) else None

    def _klik(self, nazwa: str) -> bool:
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest

        w = self._w(nazwa)
        if w is None or not w.isEnabled():
            return False
        QTest.mouseClick(w, Qt.MouseButton.LeftButton)
        self.ostatnia_czynnosc = f"klik {re.sub(r'[0-9]+', 'N', nazwa)}"
        return True

    def _znajdz_okno(self) -> None:
        from PySide6.QtWidgets import QApplication

        for w in QApplication.topLevelWidgets():
            if w.objectName() == "okno_wieczor" and hasattr(w, "k"):
                self.okno, self.k = w, w.k
                return

    # ---- tykniecie
    def tyk(self) -> None:
        if self.zakonczono:
            return
        teraz = time.perf_counter()
        if self.ostatni is not None:
            ms = (teraz - self.ostatni) * 1000.0
            self.przerwa_max_ms = max(self.przerwa_max_ms, ms)
            if ms > PROG_PRZERWY_MS:
                self.przerwy.append((round(ms, 1), round(time.time() - self.t0, 2), self.ostatnia_czynnosc))
        self.ostatni = teraz
        self.tykniec += 1
        if self.w_tyku:  # tykniecie w srodku klikniecia (QTest.mouseClick przetwarza zdarzenia okna): tylko pomiar przerwy
            self.tykniec_zagniezdzonych += 1
            return
        self.w_tyku = True
        self.ostatnia_czynnosc = ""
        try:
            self._krok()
        except Exception as e:  # noqa: BLE001 - blad sterownika = wynik "blad", program zamykany
            self.blad = f"{type(e).__name__}: {e}"
            self._koniec()
        finally:
            self.w_tyku = False
        ms = (time.perf_counter() - teraz) * 1000.0
        if self.zakonczono:
            self.tyk_koniec_ms = ms  # ostatnie tykniecie: stan koncowy + zamkniecie programu (poza pomiarem przerw)
        elif ms > self.tyk_max_ms:
            self.tyk_max_ms, self.tyk_max_co = ms, self.ostatnia_czynnosc or "odczyt stanu"

    def _krok(self) -> None:
        czas = time.time()
        if czas - self.t0 > self.a.limit:
            self.przerwano = f"PRZERWANO: limit {self.a.limit:.0f} s"
            self._koniec()
            return
        if self.okno is None:
            self._znajdz_okno()
            if self.okno is None:
                return
        s = self.k.stan()
        self._zapisz_stan(s, czas)
        if s.wymaga_operatora:
            if czas - self.osoba_kliknieta > 2.0 and self._klik("osoba_0"):
                self.osoba_kliknieta = czas
            return
        if self.t_gotowe is None:
            if s.pula.stan == "gotowa" and s.kolejka.silnik_gotowy:
                self.t_gotowe = czas
            elif czas - self.t0 > self.a.czekaj_na_start:
                self.przerwano = (f"PRZERWANO: program nie byl gotowy po {self.a.czekaj_na_start:.0f} s "
                                  f"(pula: {s.pula.stan}, silnik gotowy: {s.kolejka.silnik_gotowy})")
                self._koniec()
            return
        if self.symulator is None:
            self.symulator = subprocess.Popen(self.polecenie, cwd=str(self.katalog_programu), stdin=subprocess.DEVNULL,
                                              stdout=open(Path(self.a.roboczy) / "t2_symulator.log", "wb"), stderr=subprocess.STDOUT)
            self.t_symulator = czas
            self.ostatnia_czynnosc = "start symulatora"
            return
        if self.t_symulator_koniec is None and self.symulator.poll() is not None:
            self.t_symulator_koniec = czas
        if not self._pytania(s, czas):
            self._decyzje(s, czas)
        if s.kolejka.razem == 0 and s.analiza is None:
            self.t_pusta = self.t_pusta if self.t_pusta is not None else czas
        else:
            self.t_pusta = None
        # koniec: symulator skonczyl, wszystkie dobre pliki maja plytke, kolejka pusta, decyzje wykonane, odrzucenie widziane
        if self.t_symulator_koniec is None or self.zadania:
            return
        if len(self.mapy) >= len(self.dobre) and s.kolejka.razem == 0:
            if self.t_koniec_plytek is None:
                self.t_koniec_plytek = czas
            ma_uciety = any(p["rodzaj"] == "uciety" for p in self.pozycje)
            if (not ma_uciety or "plik_odrzucony" in self.komunikaty or czas - self.t_symulator_koniec > self.a.czekaj_odrzucenie) \
                    and czas - self.t_koniec_plytek > 3.0:
                self._koniec()
        elif self.t_pusta is not None and czas - self.t_pusta > 60.0 and czas - self.t_symulator_koniec > 60.0:
            self._koniec()  # brakujace plytki (np. blad analizy) zostana wykazane jako BRAK PLYTKI

    def _zapisz_stan(self, s, czas: float) -> None:
        an = s.analiza
        if an is not None and an.sha16 and an.sha16 not in self.starty:
            self.starty[an.sha16] = (float(an.od), czas)
        for p in s.plytki:
            if p.sha16 and p.sha16 not in self.mapy:
                self.mapy[p.sha16] = czas
                self.skan_id[p.sha16] = p.skan_id
                self.numery_programu[p.sha16] = p.numer  # numer w chwili pojawienia sie plytki = odczytany przez program (albo None)
                poz = self.dobre.get(p.sha16)
                if poz is not None and poz["decyzje"] == "ukruszona_wg_prawdy" and p.status == "przyjety":
                    self.zadania.append({"sha16": p.sha16, "skan_id": p.skan_id, "nr": poz["nr"], "gniazdo": None, "rodzaj": "przeglad",
                                         "krok": "plytka", "od": czas})
        if self.okno is not None and len(self.mapy_okno) < len(self.mapy):
            pokazana = self.okno.pokazana_plytka()
            for sha, sid in self.skan_id.items():
                if sid == pokazana and sha not in self.mapy_okno and sid not in self.kafelki_klikniete:
                    self.mapy_okno[sha] = czas
        if not self.kolejka_probki or self.kolejka_probki[-1][1] != s.kolejka.razem:
            self.kolejka_probki.append((czas, s.kolejka.razem))
        for kom in s.komunikaty:
            if kom.id not in self.komunikaty_id:
                self.komunikaty_id.add(kom.id)
                self.komunikaty.setdefault(kom.rodzaj, [round(czas - self.t0, 2), 0])[1] += 1
        for q in s.pytania:
            if q.id not in self.pytania:
                self.pytania[q.id] = (q.rodzaj, q.skan_id, round(czas - self.t0, 2))

    def _pytania(self, s, czas: float) -> bool:
        """Odpowiedz na pytanie "to ponowny skan?" wg scenariusza. True = pytanie czeka (decyzje "Ukruszona" stoja)."""
        odp = (self.scen.get("odpowiedzi") or {}).get("ponowny_skan")
        numer_z_prawdy = (self.scen.get("odpowiedzi") or {}).get("brak_numeru_plytki") == "numer_z_prawdy"
        if self.zadania and self.zadania[0]["krok"] != "plytka":
            return False
        for q in s.pytania:  # najpierw numer plytki (program nie odczytal go ze skanu), potem "to ponowny skan?"
            if q.rodzaj != "brak_numeru_plytki" or not numer_z_prawdy or q.id in self.pytania_porzucone:
                continue
            sha = next((h for h, sid in self.skan_id.items() if sid == q.skan_id), None)
            poz = self.dobre.get(sha)
            if poz is None or poz.get("numer") is None:
                self.pytania_porzucone.add(q.id)
                continue
            pierwszy = self.pytanie_od.setdefault(q.id, czas)
            if czas - pierwszy > 30.0:
                self.pytania_porzucone.add(q.id)
                self.odpowiedzi.append({"pytanie": "brak_numeru_plytki", "odpowiedz": f"NIEUDZIELONA: przycisk numeru {poz['numer']} niedostepny przez 30 s",
                                        "skan_id": q.skan_id, "s_od_startu": round(czas - self.t0, 2)})
                continue
            if czas - self.pytanie_klik.get(q.id, 0.0) < 0.3:
                return True
            self.pytanie_klik[q.id] = czas
            if self._klik(f"odp_podaj_numer_plytki_{poz['numer']}"):
                self.pytania_porzucone.add(q.id)
                self.numery_podane[sha] = poz["numer"]
                self.odpowiedzi.append({"pytanie": "brak_numeru_plytki", "odpowiedz": f"numer {poz['numer']}", "skan_id": q.skan_id,
                                        "s_od_startu": round(czas - self.t0, 2)})
            elif self.okno.pokazana_plytka() != q.skan_id:
                self.kafelki_klikniete.add(q.skan_id)
                self._klik(f"plytka_{q.skan_id}")
            return True
        if odp not in ("odrzuc", "potwierdz"):
            return False
        for q in s.pytania:
            if q.rodzaj != "ponowny_skan" or q.id in self.pytania_porzucone:
                continue
            pierwszy = self.pytanie_od.setdefault(q.id, czas)
            if czas - pierwszy > 30.0:
                self.pytania_porzucone.add(q.id)
                self.odpowiedzi.append({"pytanie": "ponowny_skan", "odpowiedz": "NIEUDZIELONA: przycisk odpowiedzi niedostepny przez 30 s",
                                        "skan_id": q.skan_id, "s_od_startu": round(czas - self.t0, 2)})
                continue
            if czas - self.pytanie_klik.get(q.id, 0.0) < 0.3:
                return True
            self.pytanie_klik[q.id] = czas
            if self._klik(f"odp_{odp}_ponowny_skan"):
                self.pytania_porzucone.add(q.id)
                self.odpowiedzi.append({"pytanie": "ponowny_skan", "odpowiedz": odp, "skan_id": q.skan_id, "s_od_startu": round(czas - self.t0, 2)})
            elif self.okno.pokazana_plytka() != q.skan_id:
                self.kafelki_klikniete.add(q.skan_id)
                self._klik(f"plytka_{q.skan_id}")
            return True
        return False

    def _kolory_z_ekranu(self, p) -> dict:
        """Kolor kazdego gniazda z praca odczytany Z OBRAZU mapy (piksel w ``mapa.punkt_probny``) i klasa koloru tego piksela wg
        tabeli statusow programu (``statusy.STATUSY``: kolor ekranu -> klasa). Obok, tylko do porownania: status i klasa ze stanu."""
        if self.klasy_hex is None:
            from stanowisko import statusy as ST

            self.klasy_hex = {}
            for st in ST.STATUSY.values():
                self.klasy_hex.setdefault(st.hex.lower(), set()).add(st.kolor)
        mapa = self.okno.mapa
        obraz = mapa.grab().toImage()
        wynik = {}
        for g in p.gniazda:
            if g.praca is None:
                continue
            piksel = obraz.pixelColor(mapa.punkt_probny(g.nr).toPoint()).name().lower()
            klasy = self.klasy_hex.get(piksel, set())
            klasa = next(iter(klasy)) if len(klasy) == 1 else None
            wynik[g.nr] = {"piksel": piksel, "klasa": klasa if klasa is not None else f"inny ({g.status})", "status": g.status,
                           "klasa_stanu": g.kolor}
        return wynik

    def _przeglad(self, z: dict, p, czas: float) -> None:
        """Technik oglada mape plytki: sterownik czyta kolory z ekranu i dopiero z nich uklada klikniecia. "Ukruszona" tylko na
        pracach z ubytkiem wg prawdy pokazanych na CZERWONO albo ZOLTO; praca z ubytkiem pokazana inaczej (zielona) NIE jest
        klikana (przeoczona przez program - zostaje jako brak na liscie); praca cala wg prawdy pokazana na czerwono = falszywy
        alarm: klikniecie "OK"."""
        z.setdefault("start", czas)
        wpis = {"nr": z["nr"], "sha16": z["sha16"], "s_od_startu": round(czas - self.t0, 2)}
        if p is None or czas - z["start"] > self.a.limit_decyzji:
            self.przeglady.append({**wpis, "wynik": "NIEWYKONANY: plytki nie ma w stanie" if p is None else
                                   f"NIEWYKONANY: limit {self.a.limit_decyzji:.0f} s (mapa niedostepna albo chroniona)"})
            self.zadania.popleft()
            return
        if self.okno.pokazana_plytka() != z["skan_id"]:
            self.kafelki_klikniete.add(z["skan_id"])
            self._klik(f"plytka_{z['skan_id']}")
            self.czekaj_do = czas + 0.1
            return
        if self.okno.ochrona_aktywna() or self.okno.mapa.przygaszona():
            if not z.get("w_ochronie"):
                z["w_ochronie"], z["czekan"] = True, z.get("czekan", 0) + 1
            return
        kolory = self._kolory_z_ekranu(p)
        self.kolory_ekranu[z["sha16"]] = kolory
        poz = self.dobre[z["sha16"]]
        nowe = []
        for g in sorted(set(kolory) | set(poz["gniazda_ubytki"])):
            ubytek, k = g in poz["gniazda_ubytki"], kolory.get(g)
            baza = {"sha16": z["sha16"], "skan_id": z["skan_id"], "nr": z["nr"], "gniazdo": g, "kolor": k["klasa"] if k else None}
            if k is None:
                self.decyzje.append({"nr": z["nr"], "sha16": z["sha16"], "gniazdo": g, "rodzaj": "ukruszona", "kolor_przed": None,
                                     "wynik": "NIEWYKONANA: program nie ma pracy w tym gniezdzie", "decyzja": None, "ponowien": 0,
                                     "czekan_na_ochrone": 0, "czas_s": 0.0})
            elif ubytek and k["klasa"] in ("czerwony", "zolty"):
                nowe.append({**baza, "rodzaj": "ukruszona", "krok": "gniazdo"})
            elif ubytek:
                self.decyzje.append({"nr": z["nr"], "sha16": z["sha16"], "gniazdo": g, "rodzaj": "ukruszona", "kolor_przed": k["klasa"],
                                     "wynik": f"POMINIETA: praca z ubytkiem wg prawdy pokazana przez program jako {k['klasa']} - technik "
                                              "jej nie oglada (przeoczona przez program)", "decyzja": None, "ponowien": 0,
                                     "czekan_na_ochrone": 0, "czas_s": 0.0})
            elif k["klasa"] == "czerwony":
                nowe.append({**baza, "rodzaj": "ok", "krok": "gniazdo"})
        self.przeglady.append({**wpis, "wynik": "obejrzana", "prac_na_mapie": len(kolory), "czekan_na_ochrone": z.get("czekan", 0),
                               "klikniec_zaplanowanych": len(nowe)})
        self.zadania.popleft()
        self.zadania.extendleft(reversed(nowe))
        self.ostatnia_czynnosc = "odczyt kolorow mapy"

    def _decyzje(self, s, czas: float) -> None:
        """Jedna czynnosc na tykniecie: kafelek plytki -> odczyt kolorow mapy (przeglad) -> gniazdo na mapie -> sprawdzenie, ze
        widok pracy pokazuje te prace -> "Ukruszona" / "OK" -> sprawdzenie w stanie. Gdy mapa jest chroniona (przygaszona po
        zmianie zawartosci albo po zmianie komunikatow nad mapa - E3-P15), sterownik czeka na zdjecie ochrony; klikniecie, ktore
        nie dalo skutku (widok pokazuje inna prace / decyzja nie weszla), jest PONAWIANE od klikniecia gniazda - liczba ponowien
        i czekan jest w wyniku przy kazdej decyzji."""
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest

        if not self.zadania or czas < self.czekaj_do:
            return
        z = self.zadania[0]
        p = s.plytka(z["skan_id"])
        if z["rodzaj"] == "przeglad":
            return self._przeglad(z, p, czas)
        ukr = ("ukruszona", "ukruszona_niewykryta")

        def zamknij(wynik: str, decyzja: str | None = None) -> None:
            self.decyzje.append({"nr": z["nr"], "sha16": z["sha16"], "gniazdo": z["gniazdo"], "rodzaj": z["rodzaj"], "kolor_przed": z["kolor"],
                                 "wynik": wynik, "decyzja": decyzja, "ponowien": z.get("ponowien", 0),
                                 "czekan_na_ochrone": z.get("czekan", 0), "czas_s": round(czas - z.get("start", czas), 2)})
            self.zadania.popleft()

        z.setdefault("start", czas)
        g = p.gniazdo(z["gniazdo"]) if p is not None else None
        praca = g.praca if g is not None else None
        if p is None or praca is None:
            return zamknij("NIEWYKONANA: program nie ma pracy w tym gniezdzie")
        zrobione = praca.decyzja in ukr if z["rodzaj"] == "ukruszona" else bool(praca.decyzja) and praca.decyzja not in ukr
        if zrobione:
            return zamknij("wykonana" if "klik" in z else "juz oznaczona", praca.decyzja)
        if czas - z["start"] > self.a.limit_decyzji:
            return zamknij(f"NIEWYKONANA: limit {self.a.limit_decyzji:.0f} s w kroku {z['krok']}", praca.decyzja)
        if self.okno.pokazana_plytka() != z["skan_id"]:
            self.kafelki_klikniete.add(z["skan_id"])
            self._klik(f"plytka_{z['skan_id']}")
            z["krok"] = "gniazdo"
            self.czekaj_do = czas + 0.1
            return
        if self.okno.ochrona_aktywna() or self.okno.mapa.przygaszona():  # mapa chroniona: technik czeka, klikniecie byloby pominiete
            if not z.get("w_ochronie"):
                z["w_ochronie"], z["czekan"] = True, z.get("czekan", 0) + 1
            return
        z["w_ochronie"] = False
        if z["krok"] == "gniazdo":
            mapa = self.okno.mapa
            QTest.mouseClick(mapa, Qt.MouseButton.LeftButton, pos=mapa.srodek_gniazda(z["gniazdo"]).toPoint())
            self.ostatnia_czynnosc = "klik gniazdo"
            z["krok"], z["klik_gniazda"] = "przycisk", czas
            self.czekaj_do = czas + 0.05
            return
        if z["krok"] == "przycisk":
            if getattr(self.okno.widok, "praca_id", None) != praca.praca_id:  # klikniecie gniazda nie otworzylo tej pracy: ponow
                if czas - z["klik_gniazda"] > 0.3:
                    z["ponowien"], z["krok"] = z.get("ponowien", 0) + 1, "gniazdo"
                return
            if self._klik(f"przycisk_{z['rodzaj']}"):
                z["krok"], z["klik"] = "sprawdz", czas
            elif czas - z["klik_gniazda"] > 2.0:
                z["ponowien"], z["krok"] = z.get("ponowien", 0) + 1, "gniazdo"
            self.czekaj_do = czas + 0.05
            return
        if z["krok"] == "sprawdz" and czas - z["klik"] > 1.0:  # decyzja nie weszla w 1 s: ponow od klikniecia gniazda
            z["ponowien"], z["krok"] = z.get("ponowien", 0) + 1, "gniazdo"

    def _koniec(self) -> None:
        from PySide6.QtWidgets import QApplication

        if self.zakonczono:
            return
        self.zakonczono = True
        try:
            if self.k is not None:
                s = self.k.stan()
                self.koncowy = {
                    "plytki": [{"sha16": p.sha16, "skan_id": p.skan_id, "status": p.status, "uklad": p.uklad, "numer": p.numer,
                                "zielonych": p.zielonych, "prac": len(p.prace), "czas_s": p.czas_s, "aktywna": p.aktywna,
                                "liczniki": dict(p.liczniki), "pytania": sorted({q.rodzaj for q in p.pytania}),
                                "komunikaty": sorted({x.rodzaj for x in p.komunikaty})} for p in s.plytki],
                    "do_dofrezowania": [{"skan_id": x.skan_id, "numer_plytki": x.numer_plytki, "gniazdo": x.gniazdo, "decyzja": x.decyzja}
                                        for x in s.do_dofrezowania_biezaca],
                    "kolejka": s.kolejka.razem, "pula": s.pula.stan, "pula_stl": s.pula.liczba_stl,
                    "komunikaty_otwarte": sorted({x.rodzaj for x in s.komunikaty}), "pytania_otwarte": sorted({q.rodzaj for q in s.pytania})}
        except Exception as e:  # noqa: BLE001
            self.blad = self.blad or f"odczyt stanu koncowego: {type(e).__name__}: {e}"
        QApplication.quit()


# --- wynik ---------------------------------------------------------------------------------------
def odczyt_bazy(plik: Path) -> dict:
    if not plik.is_file():
        return {"blad": "brak pliku bazy"}
    try:
        b = sqlite3.connect(f"file:{plik.as_posix()}?mode=ro", uri=True, timeout=5.0)
        b.row_factory = sqlite3.Row
        try:
            skany = [dict(w) for w in b.execute("SELECT id, status, uklad, uklad_zrodlo, uklad_zgodny, czas_pliku, czas_analizy, czas_s FROM skany ORDER BY id")]
            zdarzenia = {f"{w['zrodlo']}/{w['typ']}": w["n"] for w in b.execute("SELECT zrodlo, typ, count(*) AS n FROM zdarzenia GROUP BY zrodlo, typ")}
        finally:
            b.close()
        return {"skany": skany, "zdarzenia": zdarzenia}
    except sqlite3.Error as e:
        return {"blad": f"{type(e).__name__}: {e}"}


def odczyt_logu(katalog_logow: Path, cel: Path) -> dict:
    """Wiersze WARNING / ERROR logu programu -> plik w katalogu roboczym; do wyniku tylko liczniki."""
    liczniki = {"WARNING": 0, "ERROR": 0, "slowa": {}}
    wiersze = []
    for plik in sorted(katalog_logow.glob("*.log*")) if katalog_logow.is_dir() else []:
        for linia in plik.read_text(encoding="utf-8", errors="replace").splitlines():
            poziom = "ERROR" if (" ERROR " in linia or "CRITICAL" in linia) else "WARNING" if " WARNING " in linia else None
            trafione = [sl for sl in SLOWA_SRODOWISKA if sl.lower() in linia.lower()]
            if poziom:
                liczniki[poziom] += 1
            if poziom or trafione:
                wiersze.append(f"{plik.name}: {linia}")
                for sl in trafione:
                    liczniki["slowa"][sl] = liczniki["slowa"].get(sl, 0) + 1
    cel.write_text("\n".join(wiersze) + "\n", encoding="utf-8")
    liczniki["plik"] = cel.name
    return liczniki


def policz(a, pozycje: list, st: Sterownik | None, roboczy: Path, dodatki: dict) -> dict:
    dziennik_plik = roboczy / "t2_symulator.json"
    zapisy = []
    if dziennik_plik.is_file():
        try:
            zapisy = json.loads(dziennik_plik.read_text(encoding="utf-8")).get("zapisy") or []
        except (ValueError, OSError):
            zapisy = []
    zapis_wg_sha = {z.get("sha16"): z for z in zapisy}
    baza = odczyt_bazy(roboczy / "dane" / "stanowisko.sqlite")
    koncowy = (st.koncowy if st else None) or {}
    plytki = {p["sha16"]: p for p in koncowy.get("plytki", [])}
    skan_sha = {p["skan_id"]: p["sha16"] for p in koncowy.get("plytki", [])}
    wiersze, czasy_mapy, czasy_startu, czasy_w_kolejce, czasy_okna = [], [], [], [], []
    kolejnosc = {z.get("sha16"): i + 1 for i, z in enumerate(zapisy)}
    odrzucone = (baza.get("zdarzenia") or {}).get("scanner/plik_odrzucony", 0)
    ucietych_zapisanych = sum(1 for z in zapisy if z.get("rodzaj") == "uciety")
    for poz in pozycje:
        w = {"nr": poz["nr"], "sklad": poz["sklad"], "oczekiwany_status": poz["oczekiwany_status"]}
        if poz["rodzaj"] == "uciety":
            zap = next((z for z in zapisy if z.get("rodzaj") == "uciety"), None)
            w.update(sha16=zap.get("sha16") if zap else None, kolejnosc=kolejnosc.get(zap.get("sha16")) if zap else None,
                     faktyczny_status="plik_odrzucony" if odrzucone else "brak zdarzenia plik_odrzucony",
                     plytka_w_stanie=bool(zap and zap.get("sha16") in plytki), zdarzen_plik_odrzucony=odrzucone,
                     komunikat_plik_odrzucony=bool(st and "plik_odrzucony" in st.komunikaty))
            w["zgodne"] = bool(zap) and odrzucone == ucietych_zapisanych == 1 and not w["plytka_w_stanie"]
            wiersze.append(w)
            continue
        p = plytki.get(poz["sha16"])
        zap = zapis_wg_sha.get(poz["sha16"])
        w.update(sha16=poz["sha16"], kolejnosc=kolejnosc.get(poz["sha16"]), oczekiwany_uklad=poz["uklad"], oczekiwany_numer=poz["numer"],
                 prac_prawda=poz["prac"], faktyczny_status=p["status"] if p else "BRAK PLYTKI", faktyczny_uklad=p["uklad"] if p else None,
                 faktyczny_numer=p["numer"] if p else None, prac_program=p["prac"] if p else None, zielonych=p["zielonych"] if p else None,
                 pytania=p["pytania"] if p else [], czas_s_programu=p["czas_s"] if p else None)
        odczytany = st.numery_programu.get(poz["sha16"]) if st else None
        podany = st.numery_podane.get(poz["sha16"]) if st else None
        w["numer_zrodlo"] = ("odczytany przez program" if odczytany is not None else "podany przez technika na pytanie programu" if podany is not None
                             else "brak (program nie odczytal i nie pytal albo odpowiedz nieudzielona)")
        zgodne = p is not None and p["status"] == poz["oczekiwany_status"]
        if zgodne and poz["oczekiwany_status"] != "niezgodny_uklad":
            zgodne = p["uklad"] == poz["uklad"]
            if poz["oczekiwany_status"] == "plytka_nie_z_trybu" and p["numer"] is None:
                pass  # plytka zablokowana: program nie pyta o numer, dopoki technik nie rozstrzygnie pytania o tryb
            else:
                zgodne = zgodne and p["numer"] == poz["numer"]
        if zgodne and poz["oczekiwany_status"] == "przyjety":
            zgodne = p["prac"] == poz["prac"]  # uwaga 12 recenzji: liczba prac programu = liczba prac w prawdzie
        if zgodne and poz["oczekiwany_status"] != "przyjety":
            zgodne = p["zielonych"] == 0
        if zgodne and poz["oczekiwany_status"] == "plytka_nie_z_trybu":
            zgodne = "plytka_nie_z_trybu" in p["pytania"] or any(q[0] == "plytka_nie_z_trybu" for q in st.pytania.values())
        w["zgodne"] = bool(zgodne)
        if zap and st:
            koniec = float(zap["koniec"])
            if poz["sha16"] in st.starty:
                w["start_analizy_od_zapisu_s"] = round(st.starty[poz["sha16"]][0] - koniec, 3)
            else:
                w["start_analizy_od_zapisu_s"] = "NIE ZMIERZONO: sterownik nie zobaczyl analizy tej plytki w stanie programu"
            w["kolejka_przy_zapisie"] = next((n for t, n in reversed(st.kolejka_probki) if t <= koniec), 0)
            if isinstance(w["start_analizy_od_zapisu_s"], float):
                czasy_startu.append(w["start_analizy_od_zapisu_s"])
                if w["kolejka_przy_zapisie"] != 0:
                    czasy_w_kolejce.append(w["start_analizy_od_zapisu_s"])
            if poz["sha16"] in st.mapy:
                w["mapa_od_zapisu_s"] = round(st.mapy[poz["sha16"]] - koniec, 2)
                czasy_mapy.append((kolejnosc.get(poz["sha16"], 0), w["mapa_od_zapisu_s"]))
            if poz["sha16"] in st.mapy_okno:
                w["mapa_w_oknie_od_zapisu_s"] = round(st.mapy_okno[poz["sha16"]] - koniec, 2)
                czasy_okna.append(w["mapa_w_oknie_od_zapisu_s"])
            elif poz["sha16"] in st.mapy:
                w["mapa_w_oknie_od_zapisu_s"] = "NIE ZMIERZONO: okno nie pokazalo tej plytki samo (pokazywalo inna) przed kliknieciem sterownika"
        if st and poz["sha16"] in st.kolory_ekranu:
            kol = st.kolory_ekranu[poz["sha16"]]
            w["kolory_prac_z_ekranu"] = {str(g): {**k, "ubytek_wg_prawdy": g in poz["gniazda_ubytki"]} for g, k in sorted(kol.items())}
        wiersze.append(w)
    kolory = {"ubytki_wg_prawdy": {"czerwony": 0, "zolty": 0, "zielony": 0, "inny": 0, "brak_pracy_w_programie": 0, "plytka_nieobejrzana": 0, "z": 0},
              "cale_wg_prawdy": {"czerwony": 0, "zolty": 0, "zielony": 0, "inny": 0, "z": 0}, "ekran_inny_niz_stan": 0, "prac_odczytanych": 0}
    for poz in pozycje:
        if poz["rodzaj"] == "uciety" or poz["decyzje"] != "ukruszona_wg_prawdy":
            continue
        kol = st.kolory_ekranu.get(poz["sha16"]) if st else None
        for g in poz["gniazda_ubytki"]:
            kolory["ubytki_wg_prawdy"]["z"] += 1
            if kol is None:
                kolory["ubytki_wg_prawdy"]["plytka_nieobejrzana"] += 1
            elif g not in kol:
                kolory["ubytki_wg_prawdy"]["brak_pracy_w_programie"] += 1
            else:
                kolory["ubytki_wg_prawdy"][kol[g]["klasa"] if kol[g]["klasa"] in ("czerwony", "zolty", "zielony") else "inny"] += 1
        for g, k in (kol or {}).items():
            kolory["prac_odczytanych"] += 1
            kolory["ekran_inny_niz_stan"] += 0 if k["klasa"] == k["klasa_stanu"] else 1
            if g not in poz["gniazda_ubytki"]:
                kolory["cale_wg_prawdy"]["z"] += 1
                kolory["cale_wg_prawdy"][k["klasa"] if k["klasa"] in ("czerwony", "zolty", "zielony") else "inny"] += 1
    decyzje = st.decyzje if st else []
    zrobione = ("wykonana", "juz oznaczona")
    klikniecia = {"ukruszona": [sum(1 for d in decyzje if d["rodzaj"] == "ukruszona" and d["wynik"] in zrobione),
                                sum(1 for d in decyzje if d["rodzaj"] == "ukruszona")],
                  "ok_falszywy_alarm": [sum(1 for d in decyzje if d["rodzaj"] == "ok" and d["wynik"] in zrobione),
                                        sum(1 for d in decyzje if d["rodzaj"] == "ok")],
                  "pominiete_przeoczone": sum(1 for d in decyzje if d["wynik"].startswith("POMINIETA")),
                  "ponowien": sum(d.get("ponowien", 0) for d in decyzje),
                  "czekan_na_ochrone_mapy": sum(d.get("czekan_na_ochrone", 0) for d in decyzje) + sum(x.get("czekan_na_ochrone", 0) for x in (st.przeglady if st else []))}
    oczekiwana = sorted((poz["sha16"], g) for poz in pozycje if poz["rodzaj"] != "uciety" for g in poz["do_dofrezowania"])
    faktyczna = sorted((skan_sha.get(x["skan_id"], f"skan_id {x['skan_id']}"), x["gniazdo"]) for x in koncowy.get("do_dofrezowania", []))
    przerwy = st.przerwy if st else []
    czasy_mapy.sort()
    same_mapy = [c for _, c in czasy_mapy]
    zgodnych = sum(1 for w in wiersze if w["zgodne"])
    pomiar_caly = bool(st and st.koncowy is not None and not st.przerwano and not st.blad)
    lista_rowna = oczekiwana == faktyczna
    wynik = {
        "narzedzie": "t2_wieczor.py", "data": time.strftime("%Y-%m-%d %H:%M:%S"), "przerwano": st.przerwano if st else "sterownik nie wystartowal",
        "blad_sterownika": st.blad if st else None, "pomiar_caly": pomiar_caly, **dodatki,
        "obsluzone_zgodnie_z_prawda": {"zgodnych": zgodnych, "z": len(wiersze)},
        "start_analizy_od_zapisu_s": {"zmierzonych": len(czasy_startu), "z": len([p for p in pozycje if p["rodzaj"] != "uciety"]),
                                      "max": max(czasy_startu) if czasy_startu else None, "wartosci": czasy_startu,
                                      "ponizej_1_s": sum(1 for c in czasy_startu if c < 1.0),
                                      "czekaly_w_kolejce": czasy_w_kolejce,
                                      "uwaga": "kryterium liczone dla WSZYSTKICH plikow dobrych; pole czekaly_w_kolejce = wartosci plikow zapisanych, "
                                               "gdy program liczyl jeszcze poprzednia plytke (przyczyna, nie wylaczenie z kryterium); przy --odstep "
                                               "krotszym niz czas analizy (proba skrocona) takie pliki sa nieuniknione",
                                      "zrodlo": "analiza.od stanu programu (zdarzenie 'start' silnika) minus koniec zapisu z dziennika symulatora"},
        "mapa_od_zapisu_s": {"zmierzonych": len(same_mapy), "mediana": round(statistics.median(same_mapy), 2) if same_mapy else None,
                             "max": max(same_mapy) if same_mapy else None, "pierwsza_plytka": same_mapy[0] if same_mapy else None,
                             "kolejne": same_mapy[1:], "zrodlo": "pierwszy odczyt plytki w stan().plytki (co 20 ms) minus koniec zapisu - gorne ograniczenie",
                             "do_40_s": {"pierwsza_plytka_pula_zimna": [sum(1 for c in same_mapy[:1] if c <= 40.0), len(same_mapy[:1])],
                                         "kolejne_pula_ciepla": [sum(1 for c in same_mapy[1:] if c <= 40.0), len(same_mapy[1:])]},
                             "w_oknie": {"zmierzonych": len(czasy_okna), "mediana": round(statistics.median(czasy_okna), 2) if czasy_okna else None,
                                         "max": max(czasy_okna) if czasy_okna else None,
                                         "zrodlo": "pierwsze tykniecie (co 20 ms), w ktorym okno.pokazana_plytka() = ta plytka, bez klikniecia "
                                                   "sterownika w kafelek, minus koniec zapisu - gorne ograniczenie; gdy okno nie przelaczy mapy "
                                                   "samo (technik oglada inna plytke) - NIE ZMIERZONO"}},
        "petla_okna": {"tykniec": st.tykniec if st else 0, "okres_ms": OKRES_MS, "prog_ms": PROG_PRZERWY_MS, "najdluzsza_przerwa_ms": round(st.przerwa_max_ms, 1) if st else None,
                       "przekroczen": len(przerwy), "przekroczenia": przerwy[:50], "sterownik_tyk_max_ms": round(st.tyk_max_ms, 1) if st else None,
                       "sterownik_tyk_max_co": st.tyk_max_co if st else None, "tykniec_w_srodku_klikniecia": st.tykniec_zagniezdzonych if st else 0,
                       "tykniecie_zamykajace_ms": round(st.tyk_koniec_ms, 1) if st and st.tyk_koniec_ms is not None else None,
                       "uwaga": "tykniecie zamykajace (odczyt stanu koncowego i QApplication.quit() - zamkniecie okien programu) konczy pomiar: "
                                "po nim nie ma kolejnego tykniecia, jego czas nie jest przerwa petli w trakcie pracy"},
        "lista_do_dofrezowania": {"rowna": lista_rowna, "oczekiwanych": len(oczekiwana), "w_programie": len(faktyczna),
                                  "brakuje_w_programie": [list(x) for x in oczekiwana if x not in faktyczna],
                                  "nadmiarowe_w_programie": [list(x) for x in faktyczna if x not in oczekiwana]},
        "kolory_prac": kolory, "klikniecia": klikniecia, "przeglady_map": st.przeglady if st else [],
        "decyzje": st.decyzje if st else [], "odpowiedzi_na_pytania": st.odpowiedzi if st else [],
        "pytania_programu": sorted([list(v) for v in st.pytania.values()], key=lambda x: x[2]) if st else [],
        "komunikaty_programu": st.komunikaty if st else {}, "plytki": wiersze, "stan_koncowy": {k: v for k, v in koncowy.items() if k != "plytki"},
        "baza": baza, "zapisy_symulatora": [{k: z.get(k) for k in ("nr", "rodzaj", "sha16", "rozmiar", "start", "koniec")} for z in zapisy],
        "zdarzenia_srodowiska": {"log": odczyt_logu(roboczy / "dane" / "logi", roboczy / "t2_log_ostrzezenia.txt"),
                                 "plytki_ze_statusem_blad": sum(1 for p in koncowy.get("plytki", []) if p["status"] == "blad"),
                                 "komunikaty_bledow": {k: v for k, v in (st.komunikaty if st else {}).items()
                                                       if k in ("blad_analizy", "silnik", "silnik_nie_startuje", "blad_zapisu", "limit_czasu")}},
    }
    nz = "NIE ZMIERZONO"
    dobre = [x for x in wiersze if "numer_zrodlo" in x]
    wynik["numery_plytek"] = {"odczytane_przez_program": sum(1 for x in dobre if x["numer_zrodlo"].startswith("odczytany")),
                              "podane_przez_technika": sum(1 for x in dobre if x["numer_zrodlo"].startswith("podany")),
                              "brak": sum(1 for x in dobre if x["numer_zrodlo"].startswith("brak")), "z": len(dobre),
                              "uwaga": "na plytkach kwadratowych dolki numeru sa poza polem skanu (raport R59: numer trzeba podac) - program pyta "
                                       "'Podaj numer plytki', sterownik klika numer z prawdy; plytka nie z trybu i niezgodny uklad: bez pytania o numer"}
    wynik["werdykty"] = {
        "10 z 10 zgodnie z prawda": nz if not pomiar_caly else f"{'ZAL' if zgodnych == len(wiersze) else 'FAIL'} ({zgodnych} z {len(wiersze)})",
        "start analizy < 1 s": nz if not czasy_startu else (
            f"FAIL ({sum(1 for c in czasy_startu if c < 1.0)} z {wynik['start_analizy_od_zapisu_s']['z']} ponizej 1 s; "
            f"w kolejce za poprzednia plytka czekalo {len(czasy_w_kolejce)})" if max(czasy_startu) >= 1.0
            else "ZAL" if len(czasy_startu) == wynik["start_analizy_od_zapisu_s"]["z"]
            else f"FAIL ({len(czasy_startu)} z {wynik['start_analizy_od_zapisu_s']['z']} ponizej 1 s; reszta {nz})"),
        "mapa do 40 s (mediana)": nz if not same_mapy else (
            f"{nz} (pomiar przerwany; czesciowo: mediana {statistics.median(same_mapy):.2f} s z {len(same_mapy)} plytek)" if not pomiar_caly
            else "ZAL" if statistics.median(same_mapy) <= 40.0 else "FAIL"),
        "okno bez przerw > 200 ms": nz if not st or st.tykniec == 0 else (
            f"{nz} (pomiar przerwany; czesciowo: przekroczen {len(przerwy)})" if not pomiar_caly else "ZAL" if not przerwy else "FAIL"),
    }
    u = kolory["ubytki_wg_prawdy"]
    przeoczone = u["z"] - u["czerwony"] - u["zolty"]
    wynik["werdykty"]["lista do dofrezowania = prawda"] = nz if not pomiar_caly else (
        f"{'ZAL' if lista_rowna else 'FAIL'} (lista = prawda: {'TAK' if lista_rowna else 'NIE'}; ubytki wg prawdy {u['z']}: program pokazal "
        f"czerwone {u['czerwony']}, zolte {u['zolty']}, zielone (przeoczone) {u['zielony']}, inne / brak pracy / nieobejrzane "
        f"{u['inny'] + u['brak_pracy_w_programie'] + u['plytka_nieobejrzana']}; nieklikniete przez technika {przeoczone} z {u['z']}; "
        f"falszywe alarmy - cale wg prawdy na czerwono: {kolory['cale_wg_prawdy']['czerwony']} z {kolory['cale_wg_prawdy']['z']})")
    czesci = list(wynik["werdykty"].values())
    wynik["werdykty"]["T2 LACZNIE"] = ("ZAL" if all(c.startswith("ZAL") for c in czesci) else "FAIL" if any(c.startswith("FAIL") for c in czesci)
                                       else nz) + f" ({sum(1 for c in czesci if c.startswith('ZAL'))} z {len(czesci)} kryteriow ZAL, " \
        f"{sum(1 for c in czesci if c.startswith('FAIL'))} FAIL, {sum(1 for c in czesci if c.startswith(nz))} {nz})"
    return wynik


def tabela(w: dict) -> str:
    linie = [f"T2 wieczor - wynik sterownika ({w['data']}); platforma Qt: {w.get('platforma_qt')}; plikow: {len(w['plytki'])}; odstep {w.get('odstep_s')} s",
             f"przerwano: {w['przerwano'] or 'nie'}; blad sterownika: {w['blad_sterownika'] or 'brak'}; kod programu: {w.get('kod_programu')}",
             *(["UWAGA: PROBA SKROCONA (kryterium: 10 plikow co 60 s) - liczby i werdykty NIE sa wynikiem odbioru"]
               if len(w["plytki"]) != 10 or w.get("odstep_s") != 60.0 else []), "",
             f"{'nr':>3} {'kol':>3} {'sha16':16} {'oczekiwany':19} {'faktyczny':19} {'uklad':22} {'num':>3} {'prac':>9} {'start[s]':>9} {'mapa[s]':>8} zgodne"]
    for p in w["plytki"]:
        start = p.get("start_analizy_od_zapisu_s")
        linie.append(f"{p['nr']:>3} {str(p.get('kolejnosc') or '-'):>3} {str(p.get('sha16') or '-'):16} {p['oczekiwany_status']:19} {str(p['faktyczny_status']):19} "
                     f"{str(p.get('faktyczny_uklad') or '-'):22} {str(p.get('faktyczny_numer') if p.get('faktyczny_numer') is not None else '-'):>3} "
                     f"{str(p.get('prac_program', '-')) + '/' + str(p.get('prac_prawda', '-')):>9} "
                     f"{(f'{start:.3f}' if isinstance(start, float) else '-' if start is None else 'NZ'):>9} {str(p.get('mapa_od_zapisu_s', '-')):>8} {'TAK' if p['zgodne'] else 'NIE'}")
    o, s, m, pe, li = (w["obsluzone_zgodnie_z_prawda"], w["start_analizy_od_zapisu_s"], w["mapa_od_zapisu_s"], w["petla_okna"], w["lista_do_dofrezowania"])
    kl, ko = w["klikniecia"], w["kolory_prac"]
    linie += ["", "kolory prac odczytane z ekranu PRZED kliknieciami (piksel mapy -> klasa koloru); U = praca z ubytkiem wg prawdy, C = cala wg prawdy",
              f"{'nr':>3} {'sha16':16} {'prac':>4} {'U czerw':>7} {'U zolte':>7} {'U ziel':>6} {'U inne':>6} {'C czerw':>7} {'C zolte':>7} {'C ziel':>6} {'C inne':>6}"]
    for p in w["plytki"]:
        kp = p.get("kolory_prac_z_ekranu")
        if kp is None:
            continue
        def ile(ubytek, klasa):
            return sum(1 for k in kp.values() if k["ubytek_wg_prawdy"] == ubytek and (
                k["klasa"] == klasa if klasa else k["klasa"] not in ("czerwony", "zolty", "zielony")))
        linie.append(f"{p['nr']:>3} {str(p.get('sha16')):16} {len(kp):>4} {ile(True, 'czerwony'):>7} {ile(True, 'zolty'):>7} {ile(True, 'zielony'):>6} "
                     f"{ile(True, None):>6} {ile(False, 'czerwony'):>7} {ile(False, 'zolty'):>7} {ile(False, 'zielony'):>6} {ile(False, None):>6}")
    ku, kc = ko["ubytki_wg_prawdy"], ko["cale_wg_prawdy"]
    linie += [f"ubytki wg prawdy ({ku['z']}): czerwonych {ku['czerwony']}, zoltych {ku['zolty']}, zielonych (przeoczonych) {ku['zielony']}, innych "
              f"{ku['inny']}, bez pracy w programie {ku['brak_pracy_w_programie']}, na plytce nieobejrzanej {ku['plytka_nieobejrzana']}",
              f"prace cale wg prawdy ({kc['z']}): czerwonych (falszywe alarmy) {kc['czerwony']}, zoltych {kc['zolty']}, zielonych {kc['zielony']}, "
              f"innych {kc['inny']}; kolor z ekranu inny niz klasa w stanie programu: {ko['ekran_inny_niz_stan']} z {ko['prac_odczytanych']} prac"]
    linie += ["", f"obsluzone zgodnie z prawda: {o['zgodnych']} z {o['z']}",
              f"start analizy od zapisu (pomiar doslowny): ponizej 1 s {s['ponizej_1_s']} z {s['z']} plikow dobrych (zmierzono {s['zmierzonych']}), "
              f"max {s['max']} s, wartosci {s['wartosci']}; w tym pliki zapisane, gdy program liczyl poprzednia plytke: {s['czekaly_w_kolejce']}",
              f"mapa od zapisu (plytka w stanie programu, gorne ograniczenie): mediana {m['mediana']} s, max {m['max']} s, pierwsza plytka "
              f"(pula zimna) {m['pierwsza_plytka']} s, kolejne {m['kolejne']}; do 40 s: pierwsza {m['do_40_s']['pierwsza_plytka_pula_zimna'][0]} z "
              f"{m['do_40_s']['pierwsza_plytka_pula_zimna'][1]}, kolejne {m['do_40_s']['kolejne_pula_ciepla'][0]} z {m['do_40_s']['kolejne_pula_ciepla'][1]}",
              f"mapa w oknie od zapisu (okno samo pokazalo plytke, gorne ograniczenie): zmierzono {m['w_oknie']['zmierzonych']} z {m['zmierzonych']}, "
              f"mediana {m['w_oknie']['mediana']} s, max {m['w_oknie']['max']} s",
              f"petla okna: najdluzsza przerwa {pe['najdluzsza_przerwa_ms']} ms, przekroczen progu {pe['prog_ms']:.0f} ms: {pe['przekroczen']} "
              f"(tykniec {pe['tykniec']}, w tym {pe['tykniec_w_srodku_klikniecia']} w srodku klikniecia; najdluzsze tykniecie sterownika "
              f"w trakcie pomiaru {pe['sterownik_tyk_max_ms']} ms: {pe['sterownik_tyk_max_co']}; tykniecie zamykajace program, poza pomiarem: "
              f"{pe['tykniecie_zamykajace_ms']} ms)",
              f"lista do dofrezowania: {'rowna prawdzie' if li['rowna'] else 'ROZNA'} (oczekiwanych {li['oczekiwanych']}, w programie {li['w_programie']}, "
              f"brakuje {len(li['brakuje_w_programie'])}, nadmiarowych {len(li['nadmiarowe_w_programie'])})",
              f"decyzje technika (klikniecia tylko na pracach pokazanych na czerwono / zolto): 'Ukruszona' wykonanych {kl['ukruszona'][0]} z "
              f"{kl['ukruszona'][1]} zaplanowanych, 'OK' na falszywym alarmie {kl['ok_falszywy_alarm'][0]} z {kl['ok_falszywy_alarm'][1]}, prace z ubytkiem "
              f"NIEKLIKNIETE (program pokazal je inaczej niz czerwono / zolto) {kl['pominiete_przeoczone']}; ponowien klikniec {kl['ponowien']}, "
              f"czekan na zdjecie ochrony mapy {kl['czekan_na_ochrone_mapy']}; "
              f"odpowiedzi na pytania: {len(w['odpowiedzi_na_pytania'])}; pytania programu: {[x[0] for x in w['pytania_programu']]}",
              f"numery plytek: odczytane przez program {w['numery_plytek']['odczytane_przez_program']}, podane przez technika na pytanie programu "
              f"{w['numery_plytek']['podane_przez_technika']}, brak {w['numery_plytek']['brak']} (z {w['numery_plytek']['z']} plikow dobrych)",
              f"zdarzenia srodowiska: log WARNING {w['zdarzenia_srodowiska']['log']['WARNING']}, ERROR {w['zdarzenia_srodowiska']['log']['ERROR']}, "
              f"slowa {w['zdarzenia_srodowiska']['log']['slowa']}; plytki ze statusem blad: {w['zdarzenia_srodowiska']['plytki_ze_statusem_blad']}; "
              f"komunikaty bledow: {w['zdarzenia_srodowiska']['komunikaty_bledow']}",
              f"procesy potomne po sprzataniu: {w.get('procesy_po_sprzataniu')}", "", "werdykty:"]
    linie += [f"  {k}: {v}" for k, v in w["werdykty"].items()]
    return "\n".join(linie) + "\n"


# --- procesy -------------------------------------------------------------------------------------
def potomne() -> list:
    try:
        import psutil

        return [p for p in psutil.Process().children(recursive=True)]
    except Exception:  # noqa: BLE001 - brak psutil (srodowisko programu go nie ma) albo blad odczytu
        return []


def potomne_pid(symulator=None) -> list:
    """PID-y zywych procesow potomnych: z psutil (cale drzewo) albo - bez psutil - procesy ``multiprocessing`` (proces roboczy
    silnika programu) i symulator."""
    import multiprocessing

    pidy = {p.pid for p in potomne()} | {p.pid for p in multiprocessing.active_children() if p.pid}
    if symulator is not None and symulator.poll() is None:
        pidy.add(symulator.pid)
    return sorted(pidy)


def sprzatnij(symulator: subprocess.Popen | None) -> list:
    """Konczy symulator i wszystkie procesy potomne sterownika (silnik); zwraca PID-y, ktore mimo to zostaly."""
    if symulator is not None and symulator.poll() is None:
        symulator.terminate()
        try:
            symulator.wait(5.0)
        except subprocess.TimeoutExpired:
            symulator.kill()
    zywe = potomne()
    for p in zywe:
        try:
            p.terminate()
        except Exception:  # noqa: BLE001
            pass
    try:
        import psutil

        _, zostaly = psutil.wait_procs(zywe, timeout=5.0)
        for p in zostaly:
            try:
                p.kill()
            except Exception:  # noqa: BLE001
                pass
        _, zostaly = psutil.wait_procs(zostaly, timeout=5.0)
        return [p.pid for p in zostaly]
    except ImportError:
        import multiprocessing

        for p in multiprocessing.active_children():
            p.kill()
        for p in multiprocessing.active_children():
            p.join(5.0)
        return [p.pid for p in multiprocessing.active_children()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="t2_wieczor.py", description="Sterownik testu koncowego T2: prawdziwy program + symulator skanera + "
                                 "decyzje technika wg tabeli prawdy; mierzy liczby kryterium T2. Uruchamiac z katalogu programu interpreterem programu.")
    ap.add_argument("--roboczy", type=Path, required=True, help="katalog roboczy poza repo (nowy albo pusty): baza, logi, folder eksportu, wynik")
    ap.add_argument("--projekty", type=Path, required=True, help="folder puli projektow STL (jako [sciezki] folder_cyrkon; tylko odczyt)")
    ap.add_argument("--dane-ref", type=Path, default=Path("<PC-katalog>/app/dane_ref"), help="katalog danych odniesienia (podkatalogi ze scenariusza)")
    ap.add_argument("--scenariusz", type=Path, default=TU / "t2_scenariusz.json", help="tabela prawdy (domyslnie t2_scenariusz.json obok sterownika)")
    ap.add_argument("--ustawienia-wzor", type=Path, default=None, help="plik ustawien do skopiowania (domyslnie ustawienia.toml w katalogu programu, "
                    "a gdy go nie ma - ustawienia.przyklad.toml)")
    ap.add_argument("--program", type=Path, default=Path.cwd(), help="katalog programu (z pakietem stanowisko i narzedzia/); domyslnie katalog biezacy")
    ap.add_argument("--odstep", type=float, default=60.0, help="przerwa miedzy rozpoczeciem kolejnych plikow, s (kryterium: 60)")
    ap.add_argument("--plytki", type=int, default=10, help="ile pierwszych pozycji scenariusza podac (kryterium: 10)")
    ap.add_argument("--wybierz", default=None, help="numery pozycji scenariusza po przecinku, np. 1,5,7 (zamiast --plytki)")
    ap.add_argument("--czas-zapisu", type=float, nargs=2, default=(2.0, 4.0), metavar=("MIN", "MAX"), help="czas zapisu jednego pliku przez symulator, s")
    ap.add_argument("--limit", type=float, default=None, help="limit czasu calosci, s (domyslnie plikow x odstep + 1200); po nim wynik 'PRZERWANO: limit', kod 3")
    ap.add_argument("--czekaj-na-start", type=float, default=600.0, help="ile najdluzej czekac na gotowa pule i silnik przed pierwszym plikiem, s")
    ap.add_argument("--czekaj-odrzucenie", type=float, default=60.0, help="ile najdluzej czekac po ostatnim zapisie na odrzucenie pliku ucietego, s")
    ap.add_argument("--limit-decyzji", type=float, default=60.0, help="limit czasu jednej decyzji 'Ukruszona' (od wybrania plytki), s")
    ap.add_argument("--pula-cache", type=Path, default=None, help="istniejaca pamiec linii brzegu (domyslnie pusta w katalogu roboczym = pula zimna)")
    ap.add_argument("--seed", type=int, default=1, help="ziarno symulatora (czasy zapisu)")
    ap.add_argument("--wymagaj-zal", action="store_true", help="kod wyjscia 1, gdy pomiar wykonany, ale wiersz 'T2 LACZNIE' nie jest ZAL")
    a = ap.parse_args(argv)

    program = a.program.resolve()
    if not (program / "stanowisko" / "aplikacja.py").is_file() or not (program / "narzedzia" / "symulator_skanera.py").is_file():
        print(f"BLAD: {program} nie jest katalogiem programu (brak stanowisko/aplikacja.py albo narzedzia/symulator_skanera.py)", file=sys.stderr)
        return 2
    for p in (str(program / "narzedzia"), str(program)):
        if p not in sys.path:
            sys.path.insert(0, p)
    os.chdir(program)
    roboczy = a.roboczy.resolve()
    if roboczy.exists() and any(roboczy.iterdir()):
        print(f"BLAD: katalog roboczy {roboczy} nie jest pusty - podaj nowy (stara baza zmienilaby wynik)", file=sys.stderr)
        return 2
    for pod in ("dane", "eksport", "prywatne", "millbox", "zrodla"):
        (roboczy / pod).mkdir(parents=True, exist_ok=True)
    a.roboczy = roboczy
    try:
        scen = json.loads(a.scenariusz.read_text(encoding="utf-8"))
        numery = [p["nr"] for p in scen["plytki"]]
        wybrane = [int(x) for x in a.wybierz.split(",")] if a.wybierz else numery[: max(1, a.plytki)]
        if any(n not in numery for n in wybrane):
            raise SystemExit(f"--wybierz: numery spoza scenariusza ({numery})")
        wzor = a.ustawienia_wzor or (program / "ustawienia.toml" if (program / "ustawienia.toml").is_file() else program / "ustawienia.przyklad.toml")
        if not a.projekty.is_dir() or not wzor.is_file():
            raise SystemExit("brak folderu --projekty albo pliku ustawien wzorcowych")
        import symulator_skanera as SY  # narzedzie programu: tylko skrot16 (ten sam skrot, ktorym program oznacza skan)

        ustawienia = zloz_ustawienia(wzor, roboczy, a.projekty.resolve(), a.pula_cache)
        pozycje, zrodla, uciety = przygotuj_zestaw(scen, wybrane, a.dane_ref, roboczy, SY.skrot16)
    except SystemExit as e:
        print(f"BLAD przygotowania: {e}", file=sys.stderr)
        return 2
    plikow = len(zrodla) + (1 if uciety else 0)
    if a.limit is None:
        a.limit = plikow * a.odstep + 1200.0
    polecenie = [sys.executable, str(program / "narzedzia" / "symulator_skanera.py"), "--folder", str(roboczy / "eksport"), "--zrodla",
                 *[str(z) for z in zrodla], "--ile", str(len(zrodla)), "--odstep", str(a.odstep), "--rownolegle", "1", "--seed", str(a.seed),
                 "--czas", str(a.czas_zapisu[0]), str(a.czas_zapisu[1]), "--dziennik", str(roboczy / "t2_symulator.json")] + (["--zle", "uciety"] if uciety else [])
    (roboczy / "t2_pid.txt").write_text(f"sterownik {os.getpid()}\n", encoding="ascii")
    dodatki = {"odstep_s": a.odstep, "plikow": plikow, "limit_s": a.limit, "katalog_programu": program.name, "python": sys.version.split()[0],
               "scenariusz": a.scenariusz.name, "wybrane": wybrane, "pula_cache": "podana (ciepla)" if a.pula_cache else "pusta (zimna)"}
    st: Sterownik | None = None
    koniec = threading.Event()

    def zapisz(wynik: dict) -> None:
        (roboczy / "t2_wynik.json").write_text(json.dumps(wynik, ensure_ascii=True, indent=1, default=str) + "\n", encoding="ascii")
        tekst = tabela(wynik)
        (roboczy / "t2_wynik.txt").write_text(tekst, encoding="ascii", errors="replace")
        print(tekst)

    def straznik() -> None:  # osobny watek: PID-y procesow potomnych do pliku; po limit + 120 s wynik czesciowy i wyjscie
        znane: set = set()
        while not koniec.wait(5.0):
            for pid in potomne_pid(st.symulator if st is not None else None):
                if pid not in znane:
                    znane.add(pid)
                    with open(roboczy / "t2_pid.txt", "a", encoding="ascii") as f:
                        f.write(f"potomny {pid}\n")
            if st is not None and time.time() - st.t0 > a.limit + 120.0:
                st.przerwano = f"PRZERWANO: limit {a.limit:.0f} s + 120 s - petla okna nie odpowiada (zawieszenie)"
                try:
                    dodatki["procesy_po_sprzataniu"] = sprzatnij(st.symulator)
                    zapisz(policz(a, pozycje, st, roboczy, dodatki))
                finally:
                    os._exit(3)

    kod_programu: int | None = None
    wyjatek: str | None = None
    try:
        from PySide6 import QtCore, QtWidgets

        from stanowisko import aplikacja as AP

        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
        dodatki["platforma_qt"] = app.platformName()
        st = Sterownik(a, pozycje, polecenie, program, scen)
        threading.Thread(target=straznik, name="t2-straznik", daemon=True).start()
        zegar = QtCore.QTimer()
        zegar.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
        zegar.setInterval(OKRES_MS)
        zegar.timeout.connect(st.tyk)
        zegar.start()  # tyka dopiero w app.exec() wewnatrz main() programu
        kod_programu = AP.main(["--ustawienia", str(ustawienia), "--zamknij-po", str(a.limit + 60.0)])
        zegar.stop()
        if not st.zakonczono and not st.przerwano:
            st.przerwano = f"PRZERWANO: program zakonczyl sie sam (kod {kod_programu}) przed koncem pomiaru"
    except BaseException as e:  # noqa: BLE001 - wynik ma powstac takze po bledzie
        wyjatek = f"{type(e).__name__}: {e}"
    finally:
        koniec.set()
        dodatki["procesy_po_sprzataniu"] = sprzatnij(st.symulator if st else None)
    dodatki["kod_programu"] = kod_programu
    if st is not None and wyjatek:
        st.blad = st.blad or wyjatek
    wynik = policz(a, pozycje, st, roboczy, dodatki)
    if st is None:
        wynik["blad_sterownika"] = wyjatek
    zapisz(wynik)
    if st is not None and st.przerwano and "limit" in st.przerwano:
        return 3
    if st is None or st.blad or st.przerwano or kod_programu != 0:
        return 4
    if a.wymagaj_zal and not wynik["werdykty"]["T2 LACZNIE"].startswith("ZAL"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
