"""sonda_komunikaty.py - UZUPELNIENIE testu koncowego T7 (odpornosc): narzedzie POMIARU tresci komunikatow NA EKRANIE.

Co robi: uruchamia PRAWDZIWY program "Stanowisko" z instalacji z paczki (``stanowisko.aplikacja.main`` - ta sama funkcja,
ktora wola ``Stanowisko.cmd``; prawdziwy obserwator folderu, prawdziwy proces silnika, prawdziwe okno; wzor: sterowniki
odbioru ``t2_wieczor.py`` / ``t3_poranek.py``), wywoluje przypadek awarii SRODKAMI ZEWNETRZNYMI i co 150 ms zapisuje
WSZYSTKIE widoczne teksty paneli komunikatow, paska stanu i okienek (tekst, nazwa obiektu, ``isVisible()``, czy panel ma
widoczne piksele), a w chwili pojawienia sie nowego panelu robi zrzut okna PNG (``okno.grab().save``).

Uruchomienie (interpreterem i z katalogu programu instalacji; okno offscreen - odstepstwo O4 jak w T2 / T3):
    set QT_QPA_PLATFORM=offscreen
    <PC-katalog>\\t0\\odbior_t12\\Stanowisko\\Polecenie.cmd <ten plik> --przypadek <1-6> --powt <n> [--wariant <x>]
Dwa poziomy procesow: proces NADZORCY (ten plik bez ``--wewnatrz``: katalog przebiegu, plik ustawien, start i - w przypadku 2 -
zakonczenie procesu programu, atrapy ramek w wariancie 5d, odczyt bazy PO zamknieciu programu, podsumowanie) i proces
PROGRAMU (ten plik z ``--wewnatrz``: ``QApplication`` + zegar sondy + ``aplikacja.main()`` w jednym procesie, jak w T2).

Czego sonda NIE robi: niczego nie podmienia w programie (zadnych atrap silnika, ``setattr``, monkeypatch, wlasnych podklas),
nie wola polecen kontrolera, nie pisze do bazy programu (proces blokady robi ``BEGIN EXCLUSIVE`` / ``BEGIN IMMEDIATE`` i
``ROLLBACK`` - zadnego zapisu), nie zmienia plikow instalacji ani ``<K>\\ustawienia.toml`` (czyta go jako wzor).
Program dostaje WLASNY plik ustawien: kopia ``<K>\\ustawienia.toml`` z 11 sciezkami ``[sciezki]`` w podkatalogach
``uzup\\robocze\\`` (funkcja ``zloz_ustawienia`` sterownika T2) i - tylko w przypadkach 4 / 5 - z innym adresem ramek ``[ramki]``.

Awarie (srodki zewnetrzne):
  1  zabicie silnika: ``powershell Stop-Process -Id <pid> -Force`` w osobnym procesie; PID wg reguly planu (procesy Pythona
     bazowego ze ``StartTime`` do 5 s po posredniku srodowiska wersji = dokladnie 2, mlodszy = silnik) ORAZ zgodny z lancuchem
     rodzic-potomek (jedyny proces potomny ``multiprocessing`` procesu programu); oba odczyty sa w logu,
  2  zamkniecie programu: nadzorca konczy proces posrednika (``TerminateProcess`` = ``Stop-Process -Force``) w trakcie analizy
     2. skanu i uruchamia program ponownie na tych samych danych (wariant c: zwykle zamkniecie okna ``close()`` = krzyzyk),
  3  brak folderu projektow: ``os.rename`` folderu ``folder_cyrkon`` (przed startem - nadzorca; w trakcie pracy - sonda),
  4  brak sieci: adres ramek nieosiagalny (4a: nazwy ``ramka-w.local`` / ``ramka-p.local`` z ustawien instalacji - nazwa sie nie
     rozwiazuje; 4b: adresy 192.0.2.x - brak odpowiedzi); fizycznego odciecia sieci sonda NIE robi,
  5  brak ramki: 5a - adres 127.0.0.1 i port, pod ktorym nikt nie slucha; 5d - atrapy ramek programu
     (``narzedzia/atrapa_ramki.py``, osobne procesy) dzialaja przy starcie i sa konczone przez nadzorce w trakcie pracy,
  6  baza zajeta: osobny proces (ten plik z ``--blokada``) trzyma ``BEGIN EXCLUSIVE`` / ``IMMEDIATE`` na pliku bazy programu;
     decyzja technika = klikniecie ``przycisk_ukruszona`` (tak jak klika sterownik T2: po nazwach obiektow).

MIEJSCA, w ktorych sonda zaglada do wnetrza programu (tylko odczyt; czynnosci WYLACZNIE kliknieciami ``QTest.mouseClick``):
  a) okno: ``QApplication.topLevelWidgets()`` -> obiekt ``okno_wieczor``; wszystkie widzety klas ``PanelUwagi`` / ``PanelOsoby``
     (panele pytan i komunikatow; obszary ``pasek_bledow``, ``uwagi``, ``rano_pasek_bledow``, ``rano_uwagi``, ``lista_plytek``) -
     ich ``objectName()``, ``isVisible()``, ``visibleRegion()``, teksty ``QLabel`` i przyciskow; pasek stanu ``pasek_stanu``
     (etykiety ``napis_*`` i ich podpowiedz ``toolTip``); naglowek mapy ``mapa_naglowek``; nazwy kafelkow ``plytka_<id>``;
     ``okno.grab()`` (zrzut); inne widoczne okna najwyzszego poziomu (okienka dialogowe) - klasa, tytul, tekst,
  b) atrybut ``okno.k`` (kontroler przekazany oknu przez ``main``) i ``kontroler.stan()`` - tylko odczyt: ``wymaga_operatora``,
     ``pula.stan``, ``kolejka``, ``analiza`` (czy trwa), ``plytki`` (``skan_id``, ``status``, ``sha16``, gniazda: ``nr``, kolor
     i ``decyzja`` pracy, ``praca_id``), ``komunikaty`` (``rodzaj``, ``id``, ``poziom``, ``trwaly``) i ``pytania`` (``rodzaj``),
     ``do_dofrezowania_biezaca`` (liczba) - do sterowania scenariuszem i jako odczyt porownawczy obok tekstow ekranu
     (werdykt "komunikat widoczny" liczy sie WYLACZNIE z tekstow widzetow, nie ze stanu),
  c) ``okno.pokazana_plytka()``, ``okno.ochrona_aktywna()``, ``okno.mapa.przygaszona()``, ``okno.mapa.srodek_gniazda(nr)``
     (punkt klikniecia gniazda), ``okno.widok.praca_id`` (ktora prace pokazuje widok) - jak sterownik T2,
  d) ``multiprocessing.active_children()`` w procesie programu (PID procesu roboczego silnika - przypadek 1),
  e) PO zamknieciu programu: baza SQLite tylko do odczytu (``mode=ro``; tabele ``skany`` i ``zdarzenia`` - liczniki).
Klikniecia: ``osoba_0`` (wybor osoby), ``plytka_<id>``, mapa (gniazdo), ``przycisk_ukruszona``, ``komunikat_ponow_polecenie``
("Ponow teraz"), ``komunikat_odswiez_pule`` ("Odswiez pule" w komunikacie), ``przycisk_przelacz_tryb``, ``zamknij_komunikat``.

Ograniczenia: okno offscreen (bez prawdziwego ekranu; zrzut = to, co okno rysuje); program biegnie w procesie sondy (jak w
T2: modul glowny procesu to ten plik, proces silnika importuje go jako ``__mp_main__``); zegar sondy (150 ms) dziala w watku
okna; ``--zamknij-po`` jako bezpiecznik; czas "widoczny po" ma dokladnosc okresu zegara i przerw petli okna.
Wynik: ``robocze/<przebieg>/odczyty_<etap>.jsonl`` (kazda zmiana ekranu + znaczniki zdarzen), zrzuty ``robocze/zrzuty/``,
podsumowanie ``<przebieg>_podsumowanie.txt`` i kopia odczytow w katalogu tego pliku. Tylko numery, sha16 i teksty ekranu.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

TU = Path(__file__).resolve().parent
ROB = TU / "robocze"
ODB_NARZ = Path("<PC-katalog>/t0/repo/Ramki/etap3/odbior_koncowy/narzedzia")
K_UST = Path("<PC-katalog>/t0/odbior_t12/Stanowisko/ustawienia.toml")
OKRES_MS = 150
OBSZARY = ("pasek_bledow", "uwagi", "rano_pasek_bledow", "rano_uwagi", "lista_plytek", "pasek_stanu")
PL = str.maketrans({"\u0105": "a", "\u0107": "c", "\u0119": "e", "\u0142": "l", "\u0144": "n", "\u00f3": "o", "\u015b": "s", "\u017a": "z", "\u017c": "z", "\u0104": "A", "\u0106": "C",
                    "\u0118": "E", "\u0141": "L", "\u0143": "N", "\u00d3": "O", "\u015a": "S", "\u0179": "Z", "\u017b": "Z", "\u201e": '"', "\u201d": '"', "\u2014": "-", "\u2013": "-",
                    "\u2026": "...", "\u00b7": "|", "\u2192": "->", "\u2190": "<-", "\u00a0": " ", "\u2019": "'"})


def ascii_pl(tekst) -> str:
    return str(tekst).translate(PL).encode("ascii", "replace").decode("ascii")


def ps(polecenie: str, limit: float = 60.0) -> tuple:
    r = subprocess.run(["powershell", "-NoProfile", "-Command", polecenie], capture_output=True, text=True, timeout=limit,
                       stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout, r.stderr


def procesy_python() -> list:
    kod, out, _ = ps("Get-Process python -ErrorAction SilentlyContinue | Select-Object Id,@{n='Start';e={$_.StartTime.ToString('o')}},"
                     "@{n='Epoka';e={([DateTimeOffset]$_.StartTime).ToUnixTimeMilliseconds()}},Path | ConvertTo-Json -Compress")
    try:
        dane = json.loads(out) if out.strip() else []
    except ValueError:
        return []
    return dane if isinstance(dane, list) else [dane]


# --- proces blokady bazy (przypadek 6) ---------------------------------------------------------------------------------
def blokada(baza: str, tryb: str, sekundy: float, flaga: str) -> int:
    import sqlite3

    c = sqlite3.connect(baza, timeout=15.0, isolation_level=None)
    c.execute(f"BEGIN {tryb}")
    Path(flaga + ".start").write_text(repr(time.time()), encoding="ascii")
    time.sleep(sekundy)
    c.execute("ROLLBACK")
    c.close()
    Path(flaga + ".koniec").write_text(repr(time.time()), encoding="ascii")
    return 0


# --- proces programu ---------------------------------------------------------------------------------------------------
class Sonda:
    def __init__(self, a):
        self.a = a
        self.kat = Path(a.katalog)
        self.t0 = time.time()
        self.plik = open(self.kat / f"odczyty_{a.etap}.jsonl", "a", encoding="ascii")
        self.okno = self.k = None
        self.t_okna = None
        self.podpis = None
        self.t_zapisu = 0.0
        self.widziane: dict = {}
        self.zrzutow = 0
        self.koniec = False
        self.w_tyku = False
        self.bez_quit = False
        self.symulatory: list = []
        self.procesy: list = []
        self.gen = SCENARIUSZE[a.przypadek](self)

    # ---- zapis
    def zapisz(self, rek: dict) -> None:
        teraz = time.time()
        rek = {"t": round(teraz - self.t0, 3), "zegar": time.strftime("%H:%M:%S", time.localtime(teraz)) + f".{int(teraz * 1000) % 1000:03d}",
               "epoka": round(teraz, 3), **rek}
        self.plik.write(json.dumps(rek, ensure_ascii=True, default=str) + "\n")
        self.plik.flush()

    def znak(self, nazwa: str, **dane) -> None:
        self.zapisz({"zdarzenie": nazwa, **dane})

    # ---- okno
    def _znajdz_okno(self) -> None:
        from PySide6.QtWidgets import QApplication

        for w in QApplication.topLevelWidgets():
            if w.objectName() == "okno_wieczor" and hasattr(w, "k"):
                self.okno, self.k = w, w.k
                self.t_okna = time.time()
                self.znak("okno programu znalezione", widoczne=w.isVisible(), rozmiar=[w.width(), w.height()])
                return

    def _w(self, nazwa: str, w_panelu: str | None = None):
        from PySide6.QtWidgets import QWidget

        korzen = self.okno
        if w_panelu is not None:
            korzen = next((p for p in self._panele() if p.objectName() == w_panelu and p.isVisibleTo(self.okno)), None)
            if korzen is None:
                return None
        w = korzen.findChild(QWidget, nazwa)
        return w if w is not None and w.isVisibleTo(self.okno) else None

    def klik(self, nazwa: str, w_panelu: str | None = None) -> bool:
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest

        w = self._w(nazwa, w_panelu)
        if w is None or not w.isEnabled():
            return False
        self.znak("klik", obiekt=nazwa, panel=w_panelu, napis=ascii_pl(getattr(w, "text", lambda: "")()))
        QTest.mouseClick(w, Qt.MouseButton.LeftButton)
        return True

    def _panele(self) -> list:
        from PySide6.QtWidgets import QWidget

        return [w for w in self.okno.findChildren(QWidget) if type(w).__name__ in ("PanelUwagi", "PanelOsoby")]

    def _obszar(self, w) -> str:
        p = w.parentWidget()
        while p is not None:
            if p.objectName() in OBSZARY:
                return p.objectName()
            p = p.parentWidget()
        return ""

    def panel_widoczny(self, nazwa: str) -> bool:
        return any(p.objectName() == nazwa and p.isVisible() and not p.visibleRegion().isEmpty() for p in self._panele())

    def zrzut(self, nazwa: str) -> None:
        if self.okno is None or self.zrzutow >= 9:
            return
        self.zrzutow += 1
        cel = ROB / "zrzuty" / f"{self.kat.name}_e{self.a.etap}_{self.zrzutow:02d}_{nazwa}.png"
        ok = self.okno.grab().save(str(cel))
        self.znak("zrzut", plik=cel.name, zapisany=bool(ok))

    # ---- odczyt ekranu
    def odczyt(self, wymus: bool = False) -> None:
        from PySide6.QtWidgets import QAbstractButton, QApplication, QLabel, QMessageBox, QWidget

        rek: dict = {"okna": [], "panele": [], "pasek": {}, "kafelki": [], "naglowek_mapy": "", "stan": None}
        for w in QApplication.topLevelWidgets():
            if w.isVisible():
                rek["okna"].append({"klasa": type(w).__name__, "nazwa": w.objectName(), "tytul": w.windowTitle(),
                                    "tekst": (w.text() + " | " + w.informativeText()) if isinstance(w, QMessageBox) else ""})
        okno = self.okno
        nowe = []
        if okno is not None:
            for p in self._panele():
                widoczny = p.isVisible()
                piksele = widoczny and not p.visibleRegion().isEmpty()
                teksty = [e.text() for e in p.findChildren(QLabel) if e.isVisibleTo(p) and e.text()]
                przyciski = [[b.objectName(), b.text(), b.isEnabled()] for b in p.findChildren(QAbstractButton) if b.isVisibleTo(p)]
                if type(p).__name__ == "PanelOsoby":
                    przyciski = [[n, "(osoba)" if n.startswith("osoba_") else t, e] for n, t, e in przyciski]
                rek["panele"].append({"obszar": self._obszar(p), "panel": p.objectName(), "isVisible": widoczny, "piksele": piksele,
                                      "teksty": teksty, "przyciski": przyciski})
                klucz = (self._obszar(p), p.objectName(), teksty[0] if teksty else "")
                if piksele and klucz not in self.widziane:
                    self.widziane[klucz] = time.time()
                    nowe.append(p.objectName())
            for nazwa in ("uwagi_jeszcze", "rano_uwagi_jeszcze"):
                e = okno.findChild(QLabel, nazwa)
                if e is not None and e.isVisible():
                    rek["panele"].append({"obszar": self._obszar(e), "panel": nazwa, "isVisible": True, "piksele": not e.visibleRegion().isEmpty(),
                                          "teksty": [e.text()], "przyciski": []})
            pasek = okno.findChild(QWidget, "pasek_stanu")
            if pasek is not None:
                for e in pasek.findChildren(QLabel):
                    if e.objectName().startswith("napis_"):
                        rek["pasek"][e.objectName()] = {"tekst": e.text(), "isVisible": e.isVisible(), "podpowiedz": e.toolTip()}
                rek["pasek"]["przyciski"] = [[b.objectName(), b.text(), b.isEnabled()] for b in pasek.findChildren(QAbstractButton) if b.isVisible()]
            rek["kafelki"] = sorted(w.objectName() for w in okno.findChildren(QWidget)
                                    if type(w).__name__ == "KafelekPlytki" and w.isVisible())
            e = okno.findChild(QLabel, "mapa_naglowek")
            rek["naglowek_mapy"] = e.text() if e is not None and e.isVisible() else ""
            try:
                s = self.k.stan()
                rek["stan"] = {"tryb": s.tryb, "wymaga_operatora": s.wymaga_operatora, "pula": s.pula.stan,
                               "kolejka": [s.kolejka.razem, s.kolejka.w_toku, s.kolejka.czeka, s.kolejka.wstrzymane, s.kolejka.silnik_gotowy],
                               "analiza": s.analiza is not None,
                               "plytki": [[p.skan_id, p.status, p.sha16] for p in s.plytki],
                               "komunikaty": [[x.rodzaj, x.id, x.poziom, x.trwaly, x.skan_id] for x in s.komunikaty],
                               "pytania": [q.rodzaj for q in s.pytania], "do_dofrezowania": len(s.do_dofrezowania_biezaca)}
            except Exception as e:  # noqa: BLE001 - odczyt porownawczy nie moze przerwac sondy
                rek["stan"] = {"blad_odczytu": type(e).__name__}
        bez = json.loads(json.dumps(rek, default=str))
        bez["pasek"].pop("napis_analiza", None)
        podpis = json.dumps(bez, sort_keys=True)
        teraz = time.time()
        if podpis != self.podpis or wymus:
            self.podpis, self.t_zapisu = podpis, teraz
            self.zapisz({"ekran": rek})
        elif teraz - self.t_zapisu >= 2.0:
            self.t_zapisu = teraz
            self.zapisz({"bez_zmian": True})
        for nazwa in nowe:
            # od przebiegu p2_1 (04:57): poza przypadkami 4 / 5 bez zrzutow paneli tla (wybor osoby, ramka wieczorna) - byly juz 8 razy
            if self.a.przypadek in (4, 5) or nazwa not in ("panel_osoba", "komunikat_ramka_wieczorna_niedostepna"):
                self.zrzut(nazwa)

    # ---- zegar
    def tyk(self) -> None:
        if self.koniec or self.w_tyku:
            return
        self.w_tyku = True
        try:
            if self.okno is None:
                self._znajdz_okno()
            self.odczyt()
            try:
                next(self.gen)
            except StopIteration:
                self.zakoncz()
        except Exception as e:  # noqa: BLE001 - blad sondy = wpis i koniec
            self.znak("BLAD SONDY", blad=f"{type(e).__name__}: {e}", slad=traceback.format_exc()[-1500:])
            self.zakoncz()
        finally:
            self.w_tyku = False

    def zakoncz(self) -> None:
        from PySide6.QtWidgets import QApplication

        if self.koniec:
            return
        try:
            if self.okno is not None and not self.bez_quit:
                self.odczyt(wymus=True)
        except Exception:  # noqa: BLE001
            pass
        self.koniec = True
        self.znak("koniec scenariusza")
        if not self.bez_quit:
            QApplication.quit()

    # ---- klocki scenariuszy (generatory: kazdy ``yield`` oddaje petle okna do nastepnego tykniecia)
    def czekaj(self, warunek, limit: float, opis: str):
        t = time.time()
        while True:
            try:
                ok = bool(warunek())
            except Exception:  # noqa: BLE001
                ok = False
            if ok:
                self.znak("spelnione: " + opis, po_s=round(time.time() - t, 2))
                return True
            if time.time() - t > limit:
                self.znak("LIMIT: " + opis, po_s=limit)
                return False
            yield

    def pauza(self, s: float):
        t = time.time()
        while time.time() - t < s:
            yield

    def w_tle(self, funkcja) -> None:
        threading.Thread(target=funkcja, daemon=True).start()

    def stan(self):
        return self.k.stan()

    def start(self, wymagaj_puli: bool = True, limit_puli: float = 600.0):
        ok = yield from self.czekaj(lambda: self.okno is not None and self.okno.isVisible(), 180, "okno programu widoczne")
        if not ok:
            return False
        yield from self.pauza(1.0)
        if self.stan().wymaga_operatora:
            yield from self.czekaj(lambda: self.klik("osoba_0"), 20, "klikniecie osoba_0")
            yield from self.czekaj(lambda: not self.stan().wymaga_operatora, 10, "osoba wybrana")
        if wymagaj_puli:
            ok = yield from self.czekaj(lambda: self.stan().pula.stan == "gotowa" and self.stan().kolejka.silnik_gotowy, limit_puli,
                                        "pula gotowa i silnik gotowy")
        return ok

    def symulator(self, litera: str, nr: int) -> None:
        program = Path.cwd()
        log = open(self.kat / f"symulator_{nr}.log", "wb")
        p = subprocess.Popen([sys.executable, str(program / "narzedzia" / "symulator_skanera.py"), "--folder", str(self.kat / "eksport"),
                              "--zrodla", str(ROB / "skany" / f"{litera}.stl"), "--ile", "1", "--rownolegle", "1", "--seed", str(nr),
                              "--czas", "2.0", "3.0", "--wzor-nazwy", f"skan_s{nr}_" + "{nr:04d}.stl",
                              "--dziennik", str(self.kat / f"symulator_{nr}.json")],
                             cwd=str(program), stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
        self.symulatory.append(p)
        self.znak("start symulatora skanera", nr=nr, zrodlo=litera, pid=p.pid)

    def plytek(self, bez_bledu: bool = False) -> int:
        return sum(1 for p in self.stan().plytki if not bez_bledu or p.status != "blad")


def zabij_silnik(s: Sonda, wynik: dict) -> None:
    """Regula planu (T7 B3) + lancuch rodzic-potomek; zabicie w osobnym procesie powershell."""
    import multiprocessing

    try:
        dzieci = [p.pid for p in multiprocessing.active_children() if p.pid]
        wynik["active_children"] = dzieci
        lista = [x for x in procesy_python() if x.get("Epoka") is not None]
        ja, rodzic = os.getpid(), os.getppid()
        baza = os.path.normcase(getattr(sys, "_base_executable", sys.executable))
        wpis = {x["Id"]: x for x in lista}
        wynik["pid_programu"], wynik["pid_posrednika"] = ja, rodzic
        wynik["posrednik_na_liscie"] = rodzic in wpis
        t_r = wpis[rodzic]["Epoka"] / 1000.0 if rodzic in wpis else None
        bazowe = [x for x in lista if x.get("Path") and os.path.normcase(x["Path"]) == baza and t_r is not None
                  and 0.0 <= x["Epoka"] / 1000.0 - t_r <= 5.0]
        bazowe.sort(key=lambda x: x["Epoka"])
        wynik["regula_5s"] = [[x["Id"], round(x["Epoka"] / 1000.0 - t_r, 2)] for x in bazowe]
        wynik["regula_5s_ok"] = len(bazowe) == 2 and bazowe[0]["Id"] == ja and len(dzieci) == 1 and bazowe[1]["Id"] == dzieci[0]
        lancuch = (len(dzieci) == 1 and dzieci[0] in wpis and wpis[dzieci[0]].get("Path")
                   and os.path.normcase(wpis[dzieci[0]]["Path"]) == baza and ja in wpis and wpis[dzieci[0]]["Epoka"] >= wpis[ja]["Epoka"])
        wynik["lancuch_ok"] = bool(lancuch)
        if t_r is not None and len(dzieci) == 1 and dzieci[0] in wpis:
            wynik["silnik_start_po_posredniku_s"] = round(wpis[dzieci[0]]["Epoka"] / 1000.0 - t_r, 2)
        wynik["analiza_trwa_przed"] = s.stan().analiza is not None
        if not lancuch:
            wynik["zabity"], wynik["powod"] = False, "PID silnika nieustalony jednoznacznie - nie zabijam"
            return
        wynik["pid_silnika"] = dzieci[0]
        wynik["t_zabicia"] = time.time()
        kod, out, err = ps(f"Stop-Process -Id {dzieci[0]} -Force")
        wynik["t_po_zabiciu"] = time.time()
        wynik["zabity"], wynik["kod_stop_process"], wynik["stderr"] = kod == 0, kod, ascii_pl(err)[:300]
    except Exception as e:  # noqa: BLE001
        wynik["zabity"], wynik["powod"] = False, f"{type(e).__name__}: {e}"
    finally:
        wynik["koniec"] = True


def scen_1(s: Sonda):
    if not (yield from s.start()):
        return
    yield from s.pauza(4.0)
    s.symulator("a", 1)
    if not (yield from s.czekaj(lambda: s.stan().analiza is not None, 120, "analiza skanu 1 trwa")):
        return
    yield from s.pauza(5.0)
    wynik: dict = {}
    s.w_tle(lambda: zabij_silnik(s, wynik))
    yield from s.czekaj(lambda: "koniec" in wynik, 90, "procedura zabicia silnika")
    s.znak("AWARIA: zabicie silnika w trakcie analizy" if wynik.get("zabity") else "AWARIA NIEWYKONANA", **wynik)
    if not wynik.get("zabity"):
        return
    yield from s.czekaj(lambda: s.panel_widoczny("komunikat_blad_analizy"), 60, "komunikat blad_analizy na ekranie")
    yield from s.pauza(8.0)
    s.symulator("b", 2)  # dalsza praca: nastepny skan
    yield from s.czekaj(lambda: s.plytek(bez_bledu=True) >= 1, 300, "DALSZA PRACA: skan 2 ma plytke (status inny niz blad)")
    yield from s.pauza(5.0)


def scen_2(s: Sonda):
    if s.a.etap == 1:
        if not (yield from s.start()):
            return
        yield from s.pauza(3.0)
        s.symulator("a", 1)
        if not (yield from s.czekaj(lambda: s.plytek() >= 1 and s.stan().analiza is None, 300, "skan 1 ma plytke")):
            return
        yield from s.pauza(4.0)
        s.symulator("b", 2)
        if not (yield from s.czekaj(lambda: s.stan().analiza is not None, 120, "analiza skanu 2 trwa")):
            return
        yield from s.pauza(4.0)
        import multiprocessing

        pidy = {"program": os.getpid(), "posrednik": os.getppid(), "silnik": [p.pid for p in multiprocessing.active_children() if p.pid]}
        if s.a.wariant == "c":
            s.znak("AWARIA: zamkniecie okna programu (close) w trakcie analizy skanu 2", **pidy)
            from PySide6.QtCore import QTimer
            from PySide6.QtWidgets import QApplication

            s.bez_quit = True
            s.koniec = True
            QTimer.singleShot(30000, QApplication.quit)  # bezpiecznik, gdyby zamkniecie okna nie konczylo programu
            s.okno.close()
            return
        s.znak("AWARIA: prosba do nadzorcy o zakonczenie procesu programu w trakcie analizy skanu 2", **pidy)
        (s.kat / "ZABIJ.json").write_text(json.dumps(pidy), encoding="ascii")
        while True:
            yield
    ok = yield from s.czekaj(lambda: s.okno is not None and s.okno.isVisible(), 180, "okno programu widoczne (po ponownym starcie)")
    if not ok:
        return
    s.znak("PO RESTARCIE: stan przy pierwszym odczycie", plytek=s.plytek(), kafelki=len([1 for p in s.stan().plytki]))
    yield from s.pauza(1.0)
    if s.stan().wymaga_operatora:
        yield from s.czekaj(lambda: s.klik("osoba_0"), 20, "klikniecie osoba_0")
    yield from s.czekaj(lambda: s.panel_widoczny("komunikat_wznowiono"), 120, "komunikat wznowiono na ekranie")
    yield from s.czekaj(lambda: s.plytek() >= 2 and s.stan().analiza is None, 400, "DALSZA PRACA: skan 2 ma plytke po restarcie (2 plytki)")
    yield from s.pauza(5.0)


def scen_3(s: Sonda):
    cyrkon, schowany = ROB / "Cyrkon3", ROB / "Cyrkon3_x"
    if not (yield from s.start(wymagaj_puli=False)):
        return
    s.znak("3a: program wystartowal BEZ folderu projektow", folder_istnieje=cyrkon.exists())
    yield from s.pauza(8.0)
    s.zrzut("start_bez_folderu_bez_skanu")
    s.symulator("a", 1)
    yield from s.czekaj(lambda: s.panel_widoczny("komunikat_pula_brak_folderu"), 60, "komunikat pula_brak_folderu na ekranie (3a)")
    yield from s.pauza(4.0)
    os.rename(schowany, cyrkon)
    s.znak("folder projektow przywrocony")
    yield from s.pauza(1.0)
    if not (yield from s.czekaj(lambda: s.klik("komunikat_odswiez_pule", "komunikat_pula_brak_folderu"), 5, "klik 'Odswiez pule' w komunikacie")):
        yield from s.czekaj(lambda: s.klik("przycisk_odswiez_pule"), 5, "klik 'Odswiez pule' na pasku")
    if not (yield from s.czekaj(lambda: s.plytek() >= 1 and s.stan().analiza is None, 400, "DALSZA PRACA: skan 1 ma plytke po przywroceniu folderu")):
        return
    yield from s.pauza(4.0)
    blad = None
    for _ in range(20):
        try:
            os.rename(cyrkon, schowany)
            blad = None
            break
        except OSError as e:
            blad = f"{type(e).__name__} {e.winerror}"
            yield from s.pauza(0.5)
    if blad:
        s.znak("3b NIE ZMIERZONO: folderu nie dalo sie usunac w trakcie pracy", blad=blad)
        return
    s.znak("AWARIA 3b: folder projektow znika w trakcie pracy")
    yield from s.pauza(10.0)
    s.zrzut("3b_po_zniknieciu_bez_skanu")
    s.symulator("b", 2)
    yield from s.czekaj(lambda: s.panel_widoczny("komunikat_pula_brak_folderu") or s.plytek() >= 2, 150,
                        "3b: komunikat pula_brak_folderu ALBO skan 2 ma plytke")
    yield from s.pauza(6.0)
    s.zrzut("3b_po_skanie")
    os.rename(schowany, cyrkon)
    s.znak("folder projektow przywrocony (3b)")
    if s.panel_widoczny("komunikat_pula_brak_folderu"):
        yield from s.czekaj(lambda: s.klik("komunikat_odswiez_pule", "komunikat_pula_brak_folderu"), 5, "klik 'Odswiez pule' w komunikacie (3b)")
        yield from s.czekaj(lambda: s.plytek() >= 2 and s.stan().analiza is None, 400, "DALSZA PRACA 3b: skan 2 ma plytke")
    yield from s.pauza(4.0)


def scen_45(s: Sonda):
    if s.a.wariant == "d":  # atrapy ramek dzialaja przy starcie; nadzorca konczy je na prosbe
        if not (yield from s.start(wymagaj_puli=False)):
            return
        from PySide6.QtWidgets import QLabel

        def napis():
            return s.okno.findChild(QLabel, "napis_ramki")

        ok = yield from s.czekaj(lambda: napis() is not None and napis().isVisible() and napis().text().count("gotowa") >= 2, 60,
                                 "pasek: obie ramki 'gotowa'")
        s.zrzut("ramki_gotowe")
        yield from s.pauza(3.0)
        (s.kat / "WYLACZ_RAMKI.json").write_text("{}", encoding="ascii")
        yield from s.czekaj(lambda: (s.kat / "RAMKI_WYLACZONE.json").exists(), 30, "nadzorca zakonczyl atrapy ramek")
        s.znak("AWARIA: atrapy ramek zakonczone (ramka znika w trakcie pracy)", wczesniej_gotowe=ok)
        yield from s.czekaj(lambda: s.panel_widoczny("komunikat_ramka_wieczorna_niedostepna"), 90, "komunikat ramki wieczornej na ekranie")
        yield from s.pauza(5.0)
    else:
        if not (yield from s.start(wymagaj_puli=False)):
            return
        yield from s.czekaj(lambda: s.panel_widoczny("komunikat_ramka_wieczorna_niedostepna"), 60, "komunikat ramki wieczornej na ekranie")
        yield from s.pauza(6.0)
    s.klik("przycisk_przelacz_tryb")
    yield from s.czekaj(lambda: s.stan().tryb == "rano", 15, "tryb Poranek")
    yield from s.czekaj(lambda: s.panel_widoczny("komunikat_ramka_niedostepna"), 60, "komunikat ramki porannej na ekranie")
    yield from s.pauza(6.0)
    # dalsza praca (krotka kontrola): komunikat da sie zamknac, okno reaguje, powrot do trybu Wieczor, pula i silnik gotowe
    zamkniety = s.klik("zamknij_komunikat", "komunikat_ramka_niedostepna")
    yield from s.pauza(1.5)
    s.znak("DALSZA PRACA: 'Zamknij' w komunikacie ramki porannej", klikniety=zamkniety, komunikat_nadal=s.panel_widoczny("komunikat_ramka_niedostepna"))
    s.klik("przycisk_przelacz_tryb")
    yield from s.czekaj(lambda: s.stan().tryb == "wieczor", 15, "tryb Wieczor (powrot)")
    ok = yield from s.czekaj(lambda: s.stan().pula.stan == "gotowa" and s.stan().kolejka.silnik_gotowy, 600, "DALSZA PRACA: pula gotowa i silnik gotowy")
    if ok and s.a.skan:
        s.symulator("a", 1)
        yield from s.czekaj(lambda: s.plytek(bez_bledu=True) >= 1 and s.stan().analiza is None, 400, "DALSZA PRACA: skan przyjety przy braku ramek (plytka)")
    yield from s.pauza(4.0)


def scen_6(s: Sonda):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    if not (yield from s.start()):
        return
    yield from s.pauza(3.0)
    s.symulator("a", 1)
    if not (yield from s.czekaj(lambda: s.plytek() >= 1 and s.stan().analiza is None, 400, "skan 1 ma plytke")):
        return
    yield from s.pauza(3.0)
    p = s.stan().plytki[0]
    s.znak("plytka", skan_id=p.skan_id, status=p.status, gniazd_z_praca=sum(1 for g in p.gniazda if g.praca is not None),
           kolory=sorted({str(g.praca.kolor) for g in p.gniazda if g.praca is not None}))
    if s.okno.pokazana_plytka() != p.skan_id:
        s.klik(f"plytka_{p.skan_id}")
        yield from s.pauza(0.5)
    kandydaci = [g for g in p.gniazda if g.praca is not None and not g.praca.decyzja]
    cel = next((g for g in kandydaci if g.praca.kolor in ("czerwony", "zolty")), kandydaci[0] if kandydaci else None)
    if cel is None:
        s.znak("NIE ZMIERZONO: plytka bez pracy do decyzji")
        return
    praca_id = cel.praca.praca_id
    otwarta = False
    for _ in range(5):
        yield from s.czekaj(lambda: not s.okno.ochrona_aktywna() and not s.okno.mapa.przygaszona(), 10, "mapa bez ochrony")
        mapa = s.okno.mapa
        s.znak("klik gniazdo", gniazdo=cel.nr, kolor=cel.praca.kolor)
        QTest.mouseClick(mapa, Qt.MouseButton.LeftButton, pos=mapa.srodek_gniazda(cel.nr).toPoint())
        otwarta = yield from s.czekaj(lambda: getattr(s.okno.widok, "praca_id", None) == praca_id, 2, "widok pokazuje wybrana prace")
        if otwarta:
            break
    if not otwarta:
        s.znak("NIE ZMIERZONO: widok pracy nie otworzyl sie")
        return
    yield from s.pauza(1.0)
    flaga = str(s.kat / "blokada")
    tryb = "EXCLUSIVE" if s.a.powt % 2 == 1 else "IMMEDIATE"
    baza = str(s.kat / "dane" / "stanowisko.sqlite")
    pb = subprocess.Popen([sys.executable, "-I", str(Path(__file__).resolve()), "--blokada", baza, tryb, "16", flaga],
                          stdin=subprocess.DEVNULL, stdout=open(s.kat / "blokada.log", "wb"), stderr=subprocess.STDOUT)
    s.procesy.append(pb)
    if not (yield from s.czekaj(lambda: Path(flaga + ".start").exists(), 30, f"proces blokady trzyma BEGIN {tryb}")):
        return
    s.znak(f"AWARIA: baza zajeta przez osobny proces (BEGIN {tryb}, 16 s)", pid=pb.pid)
    yield from s.pauza(0.6)
    t = time.time()
    kl = s.klik("przycisk_ukruszona")
    s.znak("klikniecie 'Ukruszona' przy zajetej bazie - powrot z klikniecia", klikniety=kl, klik_trwal_s=round(time.time() - t, 2))
    yield from s.czekaj(lambda: s.panel_widoczny("komunikat_decyzja_niezapisana"), 20, "komunikat decyzja_niezapisana na ekranie")
    yield from s.pauza(2.5)
    t = time.time()
    kl = s.klik("komunikat_ponow_polecenie", "komunikat_decyzja_niezapisana")
    s.znak("'Ponow teraz' przy NADAL zajetej bazie - powrot z klikniecia", klikniety=kl, klik_trwal_s=round(time.time() - t, 2),
           blokada_trwa=not Path(flaga + ".koniec").exists())
    yield from s.pauza(2.0)
    s.znak("po 2 s od nieudanego ponowienia", komunikat_widoczny=s.panel_widoczny("komunikat_decyzja_niezapisana"))
    yield from s.czekaj(lambda: Path(flaga + ".koniec").exists(), 40, "proces blokady zwolnil baze")
    yield from s.pauza(1.0)
    t = time.time()
    kl = s.klik("komunikat_ponow_polecenie", "komunikat_decyzja_niezapisana")
    s.znak("'Ponow teraz' przy WOLNEJ bazie - powrot z klikniecia", klikniety=kl, klik_trwal_s=round(time.time() - t, 2))

    def decyzja():
        pr = s.stan().praca(praca_id)
        return pr.decyzja if pr is not None else None

    ok = yield from s.czekaj(lambda: decyzja() in ("ukruszona", "ukruszona_niewykryta") and not s.panel_widoczny("komunikat_decyzja_niezapisana"),
                             15, "DALSZA PRACA: decyzja zapisana po 'Ponow teraz' i komunikat zniknal")
    s.znak("stan po ponowieniu", decyzja=decyzja(), do_dofrezowania=len(s.stan().do_dofrezowania_biezaca),
           komunikat_widoczny=s.panel_widoczny("komunikat_decyzja_niezapisana"), ok=ok)
    yield from s.pauza(4.0)


SCENARIUSZE = {1: scen_1, 2: scen_2, 3: scen_3, 4: scen_45, 5: scen_45, 6: scen_6}


def wewnatrz(a) -> int:
    import multiprocessing

    program = Path.cwd()
    for p in (str(program / "narzedzia"), str(program)):
        if p not in sys.path:
            sys.path.insert(0, p)
    kat = Path(a.katalog)
    (kat / f"pid_{a.etap}.json").write_text(json.dumps({"program": os.getpid(), "posrednik": os.getppid()}), encoding="ascii")
    koniec = threading.Event()

    def straznik() -> None:
        if not koniec.wait(a.limit):
            for p in multiprocessing.active_children():
                p.kill()
            os._exit(3)

    threading.Thread(target=straznik, daemon=True).start()
    from PySide6 import QtCore, QtWidgets

    from stanowisko import aplikacja as AP

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    s = Sonda(a)
    s.znak("start procesu programu", platforma_qt=app.platformName(), python=sys.version.split()[0], katalog_programu=str(program.parent.name),
           przypadek=a.przypadek, wariant=a.wariant, powt=a.powt, etap=a.etap)
    zegar = QtCore.QTimer()
    zegar.setInterval(OKRES_MS)
    zegar.timeout.connect(s.tyk)
    zegar.start()
    kod = None
    try:
        kod = AP.main(["--ustawienia", str(kat / "ustawienia_t2.toml"), "--zamknij-po", str(a.limit - 30.0)])
    finally:
        zegar.stop()
        koniec.set()
        s.znak("program zakonczony", kod=kod)
        for p in s.symulatory + s.procesy:
            if p.poll() is None:
                p.terminate()
        for p in multiprocessing.active_children():
            p.kill()
        for p in multiprocessing.active_children():
            p.join(5.0)
        s.znak("procesy potomne po sprzataniu", zywe=[p.pid for p in multiprocessing.active_children()])
        s.plik.close()
    return int(kod or 0)


# --- nadzorca ------------------------------------------------------------------------------------------------------------
def ustaw_ramki(plik: Path, wieczorna: str, poranna: str, port: int) -> None:
    import re

    wynik, sekcja = [], ""
    for linia in plik.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*\[([^\]]+)\]", linia)
        if m:
            sekcja = m.group(1).strip()
        k = re.match(r"^\s*([A-Za-z0-9_]+)\s*=", linia)
        if sekcja == "ramki" and k and k.group(1) in ("wieczorna_host", "poranna_host", "port"):
            linia = {"wieczorna_host": f'wieczorna_host = "{wieczorna}"', "poranna_host": f'poranna_host = "{poranna}"', "port": f"port = {port}"}[k.group(1)]
        wynik.append(linia)
    plik.write_text("\n".join(wynik) + "\n", encoding="utf-8")


def odczyt_bazy(plik: Path) -> dict:
    import sqlite3

    if not plik.is_file():
        return {"brak_pliku": True}
    try:
        c = sqlite3.connect(f"file:{plik.as_posix()}?mode=ro", uri=True, timeout=5.0)
        try:
            return {"skany": dict(c.execute("SELECT status, count(*) FROM skany GROUP BY status").fetchall()),
                    "zdarzenia": dict(c.execute("SELECT typ, count(*) FROM zdarzenia GROUP BY typ").fetchall())}
        finally:
            c.close()
    except Exception as e:  # noqa: BLE001
        return {"blad": f"{type(e).__name__}: {e}"}


def podsumuj(kat: Path, wynik: dict) -> str:
    """Tekst ASCII: znaczniki zdarzen i KAZDY panel widziany na ekranie (pierwszy / ostatni odczyt, teksty, przyciski)."""
    w = [f"PRZEBIEG {kat.name}", json.dumps({k: v for k, v in wynik.items() if k != "etapy"}, ensure_ascii=True, default=str), ""]
    for plik in sorted(kat.glob("odczyty_*.jsonl")):
        w.append(f"== {plik.name}")
        panele: dict = {}
        paski: list = []
        okna: set = set()
        n = 0
        t_okna = None
        for linia in plik.read_text(encoding="ascii").splitlines():
            try:
                r = json.loads(linia)
            except ValueError:
                continue
            if "zdarzenie" in r:
                if r["zdarzenie"] == "okno programu znalezione":
                    t_okna = r["t"]
                reszta = {k: v for k, v in r.items() if k not in ("t", "zegar", "epoka", "zdarzenie", "slad")}
                w.append(f"  [{r['t']:8.2f} s {r['zegar']}] ZDARZENIE: {ascii_pl(r['zdarzenie'])} {ascii_pl(json.dumps(reszta, ensure_ascii=False)) if reszta else ''}")
                if "slad" in r:
                    w.append("      " + ascii_pl(r["slad"]).replace("\n", "\n      "))
            if "ekran" in r:
                n += 1
                e = r["ekran"]
                for o in e["okna"]:
                    okna.add((o["klasa"], o["nazwa"], ascii_pl(o["tytul"]), ascii_pl(o["tekst"])))
                for p in e["panele"]:
                    klucz = (p["obszar"], p["panel"], tuple(p["teksty"]), tuple(b[1] for b in p["przyciski"]))
                    x = panele.setdefault(klucz, {"pierwszy": r["t"], "zegar": r["zegar"], "ostatni": r["t"], "piksele": p["piksele"], "isVisible": p["isVisible"]})
                    x["ostatni"] = r["t"]
                    x["piksele"] = x["piksele"] or p["piksele"]
                pasek = {k: v["tekst"] for k, v in e["pasek"].items() if k != "przyciski" and k != "napis_analiza" and v.get("isVisible")}
                pod = e["pasek"].get("napis_ramki", {}).get("podpowiedz", "")
                opis = ascii_pl(json.dumps(pasek, ensure_ascii=False, sort_keys=True)) + (f" | podpowiedz ramek: {ascii_pl(pod)}" if pod else "")
                if not paski or paski[-1][1] != opis:
                    paski.append((r["t"], opis))
                stan = e.get("stan") or {}
                if stan.get("komunikaty") is not None:
                    w.append(f"  [{r['t']:8.2f} s {r['zegar']}] ekran: paneli {len(e['panele'])} ({', '.join(p['panel'] for p in e['panele'] if p['piksele'])}); "
                             f"kafelki {e['kafelki']}; stan: komunikaty {[x[0] for x in stan['komunikaty']]}, pytania {stan.get('pytania')}, "
                             f"plytki {stan.get('plytki')}, pula {stan.get('pula')}, kolejka {stan.get('kolejka')}, analiza {stan.get('analiza')}, tryb {stan.get('tryb')}")
        w.append(f"  odczytow ze zmiana ekranu: {n}; okno programu znalezione w t = {t_okna}")
        w.append("  OKNA najwyzszego poziomu widziane: " + "; ".join(str(o) for o in sorted(okna)))
        w.append("  PANELE widziane (obszar / panel / pierwszy odczyt / ostatni / mial widoczne piksele):")
        for (obszar, panel, teksty, przyciski), x in sorted(panele.items(), key=lambda kv: kv[1]["pierwszy"]):
            w.append(f"   - {obszar} / {panel}: pierwszy {x['pierwszy']:.2f} s ({x['zegar']}), ostatni {x['ostatni']:.2f} s, isVisible {x['isVisible']}, piksele {x['piksele']}")
            for t in teksty:
                w.append(f"        tekst: {ascii_pl(t)}")
            if przyciski:
                w.append(f"        przyciski: {' | '.join(ascii_pl(b) for b in przyciski)}")
        w.append("  PASEK STANU (zmiany):")
        for t, opis in paski:
            w.append(f"   [{t:8.2f} s] {opis}")
        w.append("")
    for plik in sorted(kat.glob("symulator_*.json")):
        try:
            d = json.loads(plik.read_text(encoding="utf-8"))
            for z in d.get("zapisy", []):
                w.append(f"symulator {plik.stem}: koniec zapisu epoka {z['koniec']:.3f} ({time.strftime('%H:%M:%S', time.localtime(z['koniec']))}), sha16 {z.get('sha16')}, rozmiar {z.get('rozmiar')}")
        except Exception as e:  # noqa: BLE001
            w.append(f"symulator {plik.stem}: blad odczytu dziennika {type(e).__name__}")
    return "\n".join(w) + "\n"


def nadzorca(a) -> int:
    sys.path.insert(0, str(ODB_NARZ))
    import t2_wieczor as T2  # tylko funkcja zloz_ustawienia (sterownik T2, tylko odczyt)

    nazwa = f"p{a.przypadek}{a.wariant}_{a.powt}"
    kat = ROB / nazwa
    if kat.exists():
        print(f"BLAD: katalog przebiegu {kat} juz istnieje")
        return 2
    for pod in ("dane", "eksport", "prywatne", "millbox"):
        (kat / pod).mkdir(parents=True)
    cyrkon, schowany = (ROB / "Cyrkon3", ROB / "Cyrkon3_x") if a.przypadek == 3 else (ROB / "Cyrkon", None)
    if a.przypadek == 3:
        if schowany.exists() and not cyrkon.exists():
            os.rename(schowany, cyrkon)
        cyrkon_do_ustawien = cyrkon
    else:
        cyrkon_do_ustawien = cyrkon
    (ROB / "pula_cache").mkdir(exist_ok=True)
    ust = T2.zloz_ustawienia(K_UST, kat, cyrkon_do_ustawien, ROB / "pula_cache")
    wynik: dict = {"przebieg": nazwa, "przypadek": a.przypadek, "wariant": a.wariant, "powt": a.powt, "start": time.strftime("%H:%M:%S"),
                   "ramki": "jak w ustawieniach instalacji (ramka-w.local / ramka-p.local : 8765)", "etapy": []}
    atrapy: list = []
    if a.przypadek == 4 and a.wariant == "b":
        ustaw_ramki(ust, "192.0.2.10", "192.0.2.11", 8765)
        wynik["ramki"] = "192.0.2.10 / 192.0.2.11 : 8765 (adresy dokumentacyjne TEST-NET-1 - brak odpowiedzi)"
    if a.przypadek == 5 and a.wariant in ("a", ""):
        ustaw_ramki(ust, "127.0.0.1", "127.0.0.1", 18799)
        wynik["ramki"] = "127.0.0.1 : 18799 - nikt nie slucha (polaczenie odrzucane)"
    if a.przypadek == 5 and a.wariant == "d":
        ustaw_ramki(ust, "127.0.0.2", "127.0.0.3", 18765)
        wynik["ramki"] = "atrapy ramek programu: W 127.0.0.2:18765, P 127.0.0.3:18765 (osobne procesy), konczone w trakcie pracy"
        for rola, host in (("W", "127.0.0.2"), ("P", "127.0.0.3")):
            p = subprocess.Popen([sys.executable, str(Path.cwd() / "narzedzia" / "atrapa_ramki.py"), "--rola", rola, "--port", "18765", "--host", host],
                                 stdin=subprocess.PIPE, stdout=open(kat / f"atrapa_{rola}.log", "wb"), stderr=subprocess.STDOUT)
            atrapy.append(p)
        time.sleep(3.0)
        wynik["atrapy_pid"] = [p.pid for p in atrapy]
        wynik["atrapy_zyja_przed_startem"] = [p.poll() is None for p in atrapy]
    if a.przypadek == 3:
        os.rename(cyrkon, schowany)  # brak folderu PRZED startem programu
        wynik["folder_cyrkon_przed_startem"] = "brak (zmieniona nazwa)"
    # platforma offscreen nie ma czcionek systemu (pierwsza proba p4a_1: kwadraty zamiast liter na zrzutach) - sonda podaje
    # katalog z kopia 5 czcionek systemowych (Segoe UI, Arial); to ustawienie srodowiska Qt, nie programu
    srod = dict(os.environ, QT_QPA_PLATFORM="offscreen", QT_QPA_FONTDIR=str(ROB / "czcionki"))

    def start(etap: int) -> subprocess.Popen:
        log = open(kat / f"proces_{etap}.log", "wb")
        return subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--wewnatrz", "--przypadek", str(a.przypadek), "--powt", str(a.powt),
                                 "--wariant", a.wariant, "--etap", str(etap), "--katalog", str(kat), "--limit", str(a.limit)] + (["--skan"] if a.skan else []),
                                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, env=srod)

    def czekaj(p: subprocess.Popen, etap: int) -> dict:
        t = time.time()
        e = {"etap": etap, "pid_posrednika": p.pid}
        while p.poll() is None:
            time.sleep(0.2)
            if (kat / "ZABIJ.json").exists() and "zabity" not in e:
                pidy = json.loads((kat / "ZABIJ.json").read_text(encoding="ascii"))
                e["zabity"] = time.strftime("%H:%M:%S")
                e["t_zabicia_epoka"] = round(time.time(), 3)
                p.kill()  # TerminateProcess na posredniku srodowiska wersji (= Stop-Process -Force)
                time.sleep(1.5)
                zywe = {x["Id"] for x in procesy_python()}
                e["pidy"] = pidy
                e["zywe_po_1_5_s"] = sorted(zywe & ({pidy["program"], pidy["posrednik"]} | set(pidy["silnik"])))
                (kat / "ZABIJ.json").rename(kat / "ZABIJ_wykonane.json")
            if (kat / "WYLACZ_RAMKI.json").exists() and not (kat / "RAMKI_WYLACZONE.json").exists():
                for x in atrapy:
                    x.kill()
                for x in atrapy:
                    x.wait(10)
                e["atrapy_zakonczone"] = time.strftime("%H:%M:%S")
                (kat / "RAMKI_WYLACZONE.json").write_text("{}", encoding="ascii")
            if time.time() - t > a.limit + 60:
                p.kill()
                e["PRZERWANO"] = "limit nadzorcy"
        e["kod"] = p.returncode
        e["czas_s"] = round(time.time() - t, 1)
        return e

    przed = {x["Id"] for x in procesy_python()}
    try:
        e1 = czekaj(start(1), 1)
        wynik["etapy"].append(e1)
        if a.przypadek == 2:
            wynik["baza_miedzy_etapami"] = odczyt_bazy(kat / "dane" / "stanowisko.sqlite")
            wynik["zadania_niezakonczone_json_miedzy_etapami"] = (kat / "dane" / "zadania_niezakonczone.json").exists()
            time.sleep(2.0)
            wynik["etapy"].append(czekaj(start(2), 2))
    finally:
        for x in atrapy:
            if x.poll() is None:
                x.kill()
        if a.przypadek == 3 and schowany.exists() and not cyrkon.exists():
            os.rename(schowany, cyrkon)
    time.sleep(1.0)
    wynik["baza_po"] = odczyt_bazy(kat / "dane" / "stanowisko.sqlite")
    wynik["zadania_niezakonczone_json_po"] = (kat / "dane" / "zadania_niezakonczone.json").exists()
    po = {x["Id"] for x in procesy_python()}
    wynik["procesy_python_nowe_po_przebiegu"] = sorted(po - przed - {os.getpid(), os.getppid()})
    wynik["koniec"] = time.strftime("%H:%M:%S")
    wynik["zrzuty"] = sorted(p.name for p in (ROB / "zrzuty").glob(f"{nazwa}_*.png"))
    (kat / "wynik.json").write_text(json.dumps(wynik, ensure_ascii=True, indent=1, default=str) + "\n", encoding="ascii")
    tekst = podsumuj(kat, wynik)
    (TU / f"{nazwa}_podsumowanie.txt").write_text(tekst, encoding="ascii", newline="\n")
    for plik in sorted(kat.glob("odczyty_*.jsonl")):
        shutil.copyfile(plik, TU / f"{nazwa}_{plik.name}")
    print(tekst[-6000:])
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--blokada":
        return blokada(sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5])
    ap = argparse.ArgumentParser()
    ap.add_argument("--przypadek", type=int, required=True, choices=sorted(SCENARIUSZE))
    ap.add_argument("--powt", type=int, default=1)
    ap.add_argument("--wariant", default="")
    ap.add_argument("--skan", action="store_true", help="przypadki 4 / 5: na koncu prawdziwy skan (dalsza praca)")
    ap.add_argument("--limit", type=float, default=900.0)
    ap.add_argument("--wewnatrz", action="store_true")
    ap.add_argument("--etap", type=int, default=1)
    ap.add_argument("--katalog", default=None)
    a = ap.parse_args()
    return wewnatrz(a) if a.wewnatrz else nadzorca(a)


if __name__ == "__main__":
    raise SystemExit(main())
