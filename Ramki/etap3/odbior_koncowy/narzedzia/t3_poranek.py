"""t3_poranek.py - sterownik testu koncowego T3 (scenariusz SE10 przez ekran): narzedzie POMIARU, nie test jednostkowy.

Cel (plan etapu 3, T3): "Scenariusz SE10 z A6 przez ekran: 3 piece, dofrezowany zab, poprawka, dwuznaczna, nieznana - listy
kompletnych i brakow zgodne z tabela oczekiwan w 100 % wierszy". Sterownik przeprowadza TEN SAM scenariusz, co
``testy/test_session_rano.py::_scenariusz`` (te same dane ``testy/dane_sesji/rano/se10.json``, ta sama tabela ``TABELA_SE10``,
te same 32 wiersze R01-R32 liczone tymi samymi funkcjami pomocniczymi testu), ale kazda czynnosc technika wykonuje
kliknieciem albo klawiszem w OKNIE programu (po nazwach obiektow), a nie wywolaniem metody sesji.

Uzycie (zawsze z KATALOGU PROGRAMU - tego, w ktorym lezy pakiet ``stanowisko`` - interpreterem programu):
  proba z kopii repozytorium (PC):
    cd /d <REPO>\\Ramki\\stanowisko
    <PC-katalog>\\koordynator\\narz\\py.cmd <ODB>\\narzedzia\\t3_poranek.py --wyjscie <ROB>\\t3_proba1
  instalacja z paczki wydania (po ``zainstaluj.cmd /testy`` - potrzebny pytest; w paczce nie ma katalogu ``testy``):
    set QT_QPA_PLATFORM=offscreen
    <K>\\Polecenie.cmd <ODB>\\narzedzia\\t3_poranek.py --testy <ST>\\testy --wyjscie <ROB>\\t3
  (<K> = katalog instalacji z ``Polecenie.cmd`` - robi ``cd`` do katalogu programu wersji i uruchamia python srodowiska wersji;
  <ODB> = katalog ``Ramki\\etap3\\odbior_koncowy``; <ST> = ``<REPO>\\Ramki\\stanowisko``; <ROB> = katalog roboczy poza
  programem). Katalog ``--wyjscie`` musi byc nowy albo pusty (sterownik nie kasuje danych poprzedniej proby).
  Opcje: ``--help``, ``--testy``, ``--wyjscie``, ``--limit-s`` (domyslnie 600), ``--wymagaj-100``, ``--ustawienia-wzor``, ``--ekran``.

Wynik: ``<wyjscie>/t3_wynik.json`` (wiersze: nr, opis, oczekiwane, faktyczne, zgodny, ekran; liczniki; czas; wersja programu;
interpreter; platforma Qt; lista czynnosci) i ``<wyjscie>/t3_wynik.txt`` (tabela 32 wierszy PASS / FAIL + podsumowanie).
Liczba "n z 32" jest liczona z tego, co POKAZUJE ekran: wiersz, ktorego wartosc z API sesji jest zgodna, ale odczyt ekranu to
"nie" albo "nie odczytano", ma wynik "FAIL (ekran)" i NIE liczy sie do n (liczba wg samego API jest podana obok).
Dwa ostatnie wiersze stdout: "SE10 przez ekran: n z 32 wierszy zgodnych ...; listy kompletnych i brakow z ekranu: m z k" oraz
"WERDYKT T3: ZAL / ZAL z odstepstwem O5 / FAIL (n z 32; ekran: tak a, czesciowo b, nie dotyczy c, nie d, nie odczytano e)".
W wyniku i na stdout sa tylko numery kuwet, zeby i skroty sha16 - zadnych nazw folderow ani plikow zlecen.

Kody wyjscia: 0 = scenariusz doszedl do konca i plik wyniku zapisany (takze gdy n < 32 - liczba jest w pliku i w ostatnim
wierszu stdout); 1 = tylko z ``--wymagaj-100``: scenariusz doszedl do konca, ale n < 32 (takze przez "FAIL (ekran)"); 2 = blad sterownika, scenariusz
przerwany (wiersze niepoliczone = "nie policzono" z powodem) albo limit czasu (wynik czesciowy zapisuje watek-straznik).

Co jest PRAWDZIWE:
  * kontroler programu ``stanowisko.aplikacja.Aplikacja(ust, zegar=..., ramki=False, excel=False)`` + ``start()`` (silnik
    i obserwator folderu eksportu dzialaja, ale nic nie analizuja - folder eksportu jest pusty), ``Sesja`` / ``SesjaRano``,
    baza SQLite, pliki wynikow skanow, dziennik;
  * okno programu: ``aplikacja.utworz_okno(kontroler, kontroler_api.lacznik_qt(kontroler))`` - jak w ``aplikacja.main()``;
  * czynnosci technika - WSZYSTKIE kliknieciem / klawiszem (``QTest``) w obiekty okna: ``osoba_0`` (wybor osoby),
    ``przycisk_przelacz_tryb`` (wieczor <-> poranek), kafelek ``plytka_<id>`` + gniazdo mapy + ``przycisk_ukruszona`` (R01),
    gniazdo mapy porannej + ``kandydat_<i>_wybierz`` (R06), ``praca_rano_przypisz`` + numer kuwety wpisany klawiszami w pole
    ``praca_rano_przypisz_kuweta`` + Enter + ``projekt_<id>`` (R07, R10), ``odp_potwierdz_ponowny_skan`` (R09),
    ``praca_rano_bez_projektu`` (R20), ``przycisk_zamknij_piec`` (+ ``zamknij_mimo_tak``, gdy okno pyta - ``pytanie_zamknij_mimo``),
    ``rano_strona_wynik`` / ``rano_strona_rozkladanie`` (odczyt list);
  * restart programu (R18, R26, R31): zamkniecie okna i ``kontroler.zamknij()``, nowa ``Aplikacja`` + ``start()`` i nowe okno
    na tej samej bazie; osoba po restarcie wybierana ponownie kliknieciem (program jej nie pamieta).
Co jest SZTUCZNE:
  * wyniki skanow (SE10 nie ma plikow STL): budowane funkcjami testu ``wynik_skanu`` / ``zdarzenie`` i podawane ta sama
    funkcja sesji, ktora kontroler wola po analizie (``Aplikacja._zapis_w_bazie``): ``kontroler.rano.przyjmij_wynik(zdarzenie,
    wynik)`` dla skanu porannego, ``kontroler.sesja.przyjmij_wynik(zdarzenie, wynik, "wieczor")`` dla wieczornego, w jednej
    transakcji bazy, z polem ``skan`` = sha16 skanu (jak ``Aplikacja._wynik_do_sesji``); bez pliku podgladu;
  * zegar: staly, ustawiany przez sterownik na czasy scenariusza (17-19.11.2026) i przesuwany o 1 s przy kazdej czynnosci
    sterownika (zegar testu SE10 dodaje 1 s przy kazdym wywolaniu - z zywym oknem bylby niepowtarzalny);
  * indeks zlecen: ``wypelnij_indeks`` z testu wpisuje zlecenia i projekty SE10 do bazy (w programie robi to indeks folderow);
    ``[silnik] pula_wpisow = false``, foldery zlecen puste - program niczego nie indeksuje i nie nadpisuje;
  * osoby: ``[sesja] operatorzy = ["Technik A", "Technik B"]`` w pliku ``ustawienia_t3.toml`` (kopia ``ustawienia.przyklad.toml``
    programu z sekcja ``[sciezki]`` przestawiona na podkatalogi ``--wyjscie``).

Gdzie sterownik zaglada do wnetrza programu:
  1. ``kontroler._po_skanie(tryb)`` i ``kontroler._odswiez()`` - skladniki prywatne kontrolera wolane po podaniu sztucznego
     wyniku (to samo robi ``Aplikacja._zapis_w_bazie`` / petla kontrolera po prawdziwej analizie); innej, publicznej drogi
     podania wyniku bez pliku STL program nie ma;
  2. ``kontroler.sesja.baza`` - ``transakcja()`` wokol podania wyniku (jak w programie), ``wypelnij_indeks`` (INSERT zlecen
     i projektow - opisane wyzej jako sztuczne); poza tym baza tylko SELECT (funkcje pomocnicze testu);
  3. odczyt wartosci wierszy: publiczne API sesji przez ``kontroler.sesja`` i ``kontroler.rano`` (``stan_pieca``, ``wynik_pieca``,
     ``braki``, ``piece``, ``plan_plytek``, ``otwarty_piec``, ``do_dofrezowania``) - tak samo jak test; ``kontroler.stan()``
     (publiczny) do sprawdzenia trybu i osoby;
  4. okno: ``okno.mapa.srodek_gniazda(nr)``, ``okno.pokazana_plytka()``, ``okno.ochrona_aktywna()``, ``okno.ekran_rano.mapy()``,
     ``okno.ekran_rano.ochrona_aktywna()`` (punkt klikniecia gniazda i czekanie na koniec przygaszenia mapy - technik tez
     czeka) oraz ``ui.ekran_rano.teksty_tabeli`` (odczyt tabel ``tabela_kompletne``, ``tabela_braki``, ``tabela_braki_biezace``).
  Kodu programu sterownik nie zmienia i nie podmienia (zadnego monkeypatch).

Wiersze "Zamknij piec odmawia" (R08, R19): test wola ``zamknij_piec()`` i oczekuje wyjatku. Na ekranie odmowa = przycisk
``przycisk_zamknij_piec`` widoczny i NIEAKTYWNY (powod w napisie ``rano_blokady``) - wiersz liczony jako odmowa = True, zrodlo
zapisane w wyniku. Gdyby przycisk byl aktywny, sterownik by go kliknal i policzyl odmowe po tym, czy piec zostal otwarty.

Pytanie okna przed "Zamknij piec" (paczka P14): sterownik klika ``przycisk_zamknij_piec``; gdy okno pokaze
``pytanie_zamknij_mimo``, odpowiada ``zamknij_mimo_tak``. Zlecenie oczekiwalo pytania przy piecu 2 (1 praca nieznana). Okno
pyta jednak tylko o prace dwuznaczne / nieznane BEZ decyzji (``StanRano.nierozstrzygniete_prace``), a praca nieznana pieca 2
ma decyzje "bez projektu" (R20) - dla sesji jest nadal nierozstrzygnieta (R22: nieznane 1), dla okna nie. Sterownik niczego
tu nie nagina: zapisuje w wyniku ``pytania_zamkniecia`` (oczekiwane wg zlecenia / bylo) i wiersz UWAGA.

Kolumna "ekran" (wiersze z listami kompletnych / brakow: R11, R14, R15, R17, R21, R22, R28, R29, R30, R31): kuwety i zeby
odczytane z tabel okna wobec oczekiwanych: tak / nie / nie odczytano / czesciowo / nie dotyczy (z powodem).
Licznik "m z k": m = wiersze "tak", k = 10 minus "nie dotyczy".

Wiersz R32 (dane osobowe): liczony funkcja testu ``nazwy_nie_wychodza`` na 7 tabelach bazy, plikach katalogu ``<wyjscie>/dane``
(sa tam tylko pliki wynikow skanow - baza, blokada i pliki kontrolera leza w ``<wyjscie>/baza``, logi w ``<wyjscie>/logi``)
i wynikach API; dodatkowo sterownik sprawdza te same slowa w logach programu i plikach obok bazy (pole ``dodatkowo``).

Odstepstwa:
  * okno ``offscreen`` (``QT_QPA_PLATFORM=offscreen``; sterownik ustawia je sam, gdy zmienna nie jest ustawiona i nie podano
    ``--ekran``) - platforma Qt jest w wyniku;
  * program biegnie w procesie sterownika (modul glowny = ten plik; proces roboczy silnika importuje go jako ``__mp_main__`` -
    plik nie importuje Qt ani testow na poziomie modulu); ramki i Excel wylaczone (``ramki=False, excel=False``);
  * rozmiar okna 1920 x 1001 (jak testy ekranu porannego).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import re
import sys
import threading
import time
import traceback
from pathlib import Path

sys.dont_write_bytecode = True
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

OSOBA = "Technik A"
OPERATORZY = ["Technik A", "Technik B"]
ROZMIAR_OKNA = (1920, 1001)
WIERSZE_LIST = ("R11", "R14", "R15", "R17", "R21", "R22", "R28", "R29", "R30", "R31")
PYTANIE_OCZEKIWANE = {1: False, 2: True, 3: False}  # czy okno ma zapytac przed "Zamknij piec" (piec 2: 1 praca nieznana)
SCIEZKI = {"folder_eksportu_skanera": "eksport", "folder_cyrkon": "cyrkon", "folder_prywatne": "prywatne",
           "folder_millbox": "millbox", "baza": "baza/stanowisko.sqlite", "log_excel": "baza/log_excel.csv",
           "wyniki": "dane/wyniki", "podglady": "podglady", "pula_cache": "pula_cache", "logi": "logi",
           "kalibracja_ramek": "baza/kalibracja_ramek.json"}
PLIK_JSON, PLIK_TXT = "t3_wynik.json", "t3_wynik.txt"


class BladSterownika(RuntimeError):
    pass


class Zegar:
    """Zegar staly: ``ustaw`` przestawia czas na czas scenariusza, ``krok`` dodaje 1 s (raz na czynnosc sterownika)."""

    def __init__(self, start: str):
        self.teraz = dt.datetime.fromisoformat(start)

    def __call__(self) -> dt.datetime:
        return self.teraz

    def ustaw(self, czas: str) -> None:
        self.teraz = dt.datetime.fromisoformat(czas)

    def krok(self) -> None:
        self.teraz += dt.timedelta(seconds=1)


# --- przygotowanie -------------------------------------------------------------------------------
def zloz_ustawienia(wzor: Path, wyjscie: Path) -> Path:
    """Kopia pliku ustawien programu: ``[sciezki]`` -> podkatalogi ``wyjscie``, osoby, ``pula_wpisow = false``."""
    import tomllib

    cele = {"sciezki": {k: json.dumps((wyjscie / v).as_posix()) for k, v in SCIEZKI.items()},
            "sesja": {"operatorzy": json.dumps(OPERATORZY)}, "silnik": {"pula_wpisow": "false"}}
    linie: list = []
    zrobione: set = set()
    sekcja = None

    def domknij() -> None:
        for k, v in cele.get(sekcja, {}).items():
            if (sekcja, k) not in zrobione:
                linie.append(f"{k} = {v}")
                zrobione.add((sekcja, k))

    for linia in wzor.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*\[([^\]\[]+)\]", linia)
        if m:
            domknij()
            sekcja = m.group(1).strip()
            linie.append(linia)
            continue
        k = re.match(r"^\s*([A-Za-z0-9_]+)\s*=", linia)
        if k and k.group(1) in cele.get(sekcja, {}):
            linie.append(f"{k.group(1)} = {cele[sekcja][k.group(1)]}")
            zrobione.add((sekcja, k.group(1)))
        else:
            linie.append(linia)
    domknij()
    for s in cele:
        if not any(z[0] == s for z in zrobione):
            linie.append(f"[{s}]")
            sekcja = s
            domknij()
    plik = wyjscie / "ustawienia_t3.toml"
    plik.write_text("\n".join(linie) + "\n", encoding="utf-8", newline="\n")
    nowe = tomllib.loads(plik.read_text(encoding="utf-8"))
    for k, v in SCIEZKI.items():
        if nowe["sciezki"].get(k) != (wyjscie / v).as_posix():
            raise BladSterownika(f"ustawienia: nie udalo sie przestawic [sciezki] {k}")
    if nowe["sesja"]["operatorzy"] != OPERATORZY or nowe["silnik"]["pula_wpisow"] is not False:
        raise BladSterownika("ustawienia: nie udalo sie ustawic osob albo pula_wpisow")
    for nazwa in ("eksport", "cyrkon", "prywatne", "millbox", "baza", "dane", "logi", "podglady", "pula_cache"):
        (wyjscie / nazwa).mkdir(parents=True, exist_ok=True)
    return plik


def zabij_potomne() -> int:
    """Procesy potomne (proces roboczy silnika programu) - koniec; zwraca liczbe procesow, ktore jeszcze zyly."""
    import multiprocessing

    ile = 0
    for p in multiprocessing.active_children():
        ile += 1
        try:
            p.kill()
            p.join(5)
        except Exception:  # noqa: BLE001 - sprzatanie musi dojsc do konca
            pass
    return ile


# --- okno: klikniecia i odczyt po nazwach obiektow -------------------------------------------------
class Ekran:
    """Okno programu na kontrolerze ``k`` (jak w ``aplikacja.main``), sterowane mysza i klawiatura przez ``QTest``."""

    def __init__(self, kontroler, zegar: Zegar, czynnosci: list):
        from PySide6.QtTest import QTest

        from stanowisko import aplikacja as A
        from stanowisko import kontroler_api as K

        self.k, self.zegar, self.czynnosci = kontroler, zegar, czynnosci
        self.lacznik = K.lacznik_qt(kontroler)
        self.okno = A.utworz_okno(kontroler, self.lacznik)
        self.okno.resize(*ROZMIAR_OKNA)
        self.okno.show()
        QTest.qWaitForWindowExposed(self.okno)
        self.odczekaj(60)

    def zamknij(self) -> None:
        from PySide6.QtCore import QCoreApplication, QEvent

        self.okno.close()
        self.lacznik.zatrzymaj()
        self.odczekaj(5)
        self.okno.deleteLater()
        self.lacznik.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    def zdarzenia(self) -> None:
        from PySide6.QtWidgets import QApplication

        QApplication.sendPostedEvents()
        QApplication.processEvents()

    def odczekaj(self, ms: int = 30) -> None:
        from PySide6.QtTest import QTest

        QTest.qWait(ms)

    def czekaj(self, warunek, limit_s: float = 15.0, co: str = "") -> None:
        koniec = time.monotonic() + limit_s
        while not warunek():
            if time.monotonic() >= koniec:
                raise BladSterownika(f"nie doczekalem sie: {co}")
            self.odczekaj(10)

    def znajdz(self, nazwa: str):
        from PySide6.QtWidgets import QWidget

        # ta sama nazwa bywa na stronie wieczornej i porannej okna (np. osoba_0): liczy sie obiekt widoczny
        wszystkie = self.okno.findChildren(QWidget, nazwa)
        return next((x for x in wszystkie if x.isVisibleTo(self.okno)), wszystkie[0] if wszystkie else None)

    def w(self, nazwa: str):
        w = self.znajdz(nazwa)
        if w is None:
            raise BladSterownika(f"na ekranie nie ma elementu {nazwa!r}")
        return w

    def jest(self, nazwa: str) -> bool:
        self.zdarzenia()
        w = self.znajdz(nazwa)
        return w is not None and w.isVisibleTo(self.okno)

    def aktywny(self, nazwa: str) -> bool:
        return self.jest(nazwa) and self.w(nazwa).isEnabled()

    def tekst(self, nazwa: str) -> str | None:
        return self.w(nazwa).text() if self.jest(nazwa) else None

    def _zapisz(self, co: str) -> None:
        self.zegar.krok()
        self.czynnosci.append({"czas_scenariusza": self.zegar.teraz.isoformat(), "czynnosc": co})

    def klik(self, nazwa: str) -> None:
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest

        self.zdarzenia()
        w = self.w(nazwa)
        if not w.isVisibleTo(self.okno):
            raise BladSterownika(f"element {nazwa!r} nie jest widoczny")
        if not w.isEnabled():
            raise BladSterownika(f"element {nazwa!r} jest nieaktywny")
        self._zapisz(f"klik {nazwa}")
        QTest.mouseClick(w, Qt.MouseButton.LeftButton)
        self.odczekaj(15)

    def klik_gniazdo_wieczor(self, nr: int) -> None:
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest

        self.zdarzenia()
        self.czekaj(lambda: not self.okno.ochrona_aktywna(), 5.0, "koniec przygaszenia mapy")
        self._zapisz(f"klik mapa wieczorna gniazdo {nr}")
        QTest.mouseClick(self.okno.mapa, Qt.MouseButton.LeftButton, pos=self.okno.mapa.srodek_gniazda(nr).toPoint())
        self.odczekaj(15)

    def mapy_rano(self) -> dict:
        self.zdarzenia()
        return self.okno.ekran_rano.mapy()

    def klik_gniazdo_rano(self, skan_id: int, nr: int) -> None:
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest

        self.czekaj(lambda: skan_id in self.mapy_rano(), 10.0, f"mapa plytki skanu {skan_id}")
        self.czekaj(lambda: not self.okno.ekran_rano.ochrona_aktywna(), 5.0, "koniec przygaszenia map porannych")
        mapa = self.mapy_rano()[skan_id]
        self._zapisz(f"klik mapa poranna skan {skan_id} gniazdo {nr}")
        QTest.mouseClick(mapa, Qt.MouseButton.LeftButton, pos=mapa.srodek_gniazda(nr).toPoint())
        self.odczekaj(15)

    def wpisz_w_pole(self, nazwa: str, tekst: str) -> None:
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest

        pole = self.w(nazwa)
        self._zapisz(f"klik {nazwa} + klawisze {tekst!r} + Enter")
        QTest.mouseClick(pole, Qt.MouseButton.LeftButton)
        QTest.keyClicks(pole, tekst)
        QTest.keyClick(pole, Qt.Key.Key_Return)
        self.odczekaj(30)

    def tabela(self, nazwa: str) -> list | None:
        """Wiersze tabeli okna jako listy napisow; None = tabeli nie ma albo jej strona nie jest pokazana."""
        from stanowisko.ui.ekran_rano import teksty_tabeli

        self.zdarzenia()
        t = self.znajdz(nazwa)
        if t is None or not t.isVisibleTo(self.okno):
            return None
        return teksty_tabeli(t)


# --- przebieg scenariusza --------------------------------------------------------------------------
class Przebieg:
    """Program (kontroler + okno) na bazie w ``wyjscie`` i czynnosci scenariusza SE10."""

    def __init__(self, T, plik_ustawien: Path, wyjscie: Path, zegar: Zegar, raport: dict):
        self.T, self.plik_ustawien, self.wyjscie, self.zegar, self.raport = T, plik_ustawien, wyjscie, zegar, raport
        self.k = None
        self.e: Ekran | None = None
        self.logi_gotowe = False

    # test nazywa to ``st``: sesja, sesja poranna i SELECT-y pomocnicze (metody klasy ``Stanowisko`` testu)
    @property
    def sesja(self):
        return self.k.sesja

    @property
    def rano(self):
        return self.k.rano

    @property
    def katalog(self) -> Path:
        return self.wyjscie

    def praca(self, skan_id: int, gniazdo: int) -> int:
        return self.T.Stanowisko.praca(self, skan_id, gniazdo)

    def projekt_id(self, klucz: str) -> int:
        return self.T.Stanowisko.projekt_id(self, klucz)

    def stan_punktu(self, klucz: str):
        return self.T.Stanowisko.stan_punktu(self, klucz)

    def skan_wiersz(self, skan_id: int) -> dict:
        return self.T.Stanowisko.skan_wiersz(self, skan_id)

    def liczba(self, sql: str, parametry: tuple = ()) -> int:
        return self.T.Stanowisko.liczba(self, sql, parametry)

    # --- program
    def otworz(self) -> None:
        from stanowisko import aplikacja as A
        from stanowisko import ustawienia as UST

        ust = UST.wczytaj_ustawienia(self.plik_ustawien)
        if not self.logi_gotowe:
            A.konfiguruj_logi(ust)
            self.logi_gotowe = True
        self.k = A.Aplikacja(ust, zegar=self.zegar, ramki=False, excel=False)
        self.k.start()
        self.e = Ekran(self.k, self.zegar, self.raport["czynnosci"])
        self.raport["starty_programu"] += 1

    def zamknij(self) -> None:
        e, k = self.e, self.k
        self.e = self.k = None
        try:
            if e is not None:
                e.zamknij()
        finally:
            if k is not None:
                k.zamknij()

    def restart(self) -> None:
        self.raport["czynnosci"].append({"czas_scenariusza": self.zegar.teraz.isoformat(),
                                         "czynnosc": "restart programu (okno i kontroler zamkniete, nowe na tej samej bazie)"})
        self.zamknij()
        self.otworz()

    # --- czynnosci technika (klikniecia)
    def osoba(self) -> None:
        e = self.e
        e.odczekaj(40)
        s = self.k.stan()
        if s.operator == OSOBA and not s.wymaga_operatora:
            return
        e.czekaj(lambda: e.jest("osoba_0"), 10.0, "panel wyboru osoby")
        if e.w("osoba_0").text() != OSOBA:
            raise BladSterownika("przycisk osoba_0 nie jest pierwsza osoba z listy")
        e.klik("osoba_0")
        e.czekaj(lambda: self.k.stan().operator == OSOBA and not self.k.stan().wymaga_operatora, 5.0, "osoba wybrana")

    def tryb(self, tryb: str) -> None:
        e = self.e
        e.odczekaj(40)
        if self.k.stan().tryb != tryb:
            e.klik("przycisk_przelacz_tryb")
            e.czekaj(lambda: self.k.stan().tryb == tryb, 5.0, f"tryb {tryb}")
        e.czekaj(lambda: e.okno.rano() == (tryb == "rano"), 5.0, f"strona okna trybu {tryb}")

    def skan(self, klucz: str) -> int:
        """Sztuczny wynik skanu do programu - droga kontrolera po analizie (naglowek pliku: co sztuczne, miejsca prywatne)."""
        T, k = self.T, self.k
        spec = T.SKANY[klucz]
        self.zegar.ustaw(spec["czas"])
        tryb = "rano" if spec["tryb"] == "rano" else "wieczor"
        if k.stan().tryb != tryb:
            raise BladSterownika(f"skan {klucz}: program w trybie {k.stan().tryb}, scenariusz wymaga {tryb}")
        zdarzenie = T.zdarzenie(spec)
        wynik = {**T.wynik_skanu(spec), "skan": zdarzenie["sha16"]}
        with k.sesja.baza.transakcja():
            if tryb == "rano":
                skan_id = k.rano.przyjmij_wynik(zdarzenie, wynik)
            else:
                skan_id = k.sesja.przyjmij_wynik(zdarzenie, wynik, tryb)
        k._po_skanie(tryb)
        k._odswiez()
        self.raport["podane_wyniki"].append({"skan": klucz, "tryb": tryb, "skan_id": skan_id, "sha16_skanu": zdarzenie["sha16"],
                                             "czas_scenariusza": spec["czas"]})
        self.e.odczekaj(80)
        return skan_id

    def ukruszona(self, skan_id: int, gniazdo: int) -> None:
        e = self.e
        self.osoba()
        e.czekaj(lambda: e.jest(f"plytka_{skan_id}"), 10.0, "kafelek plytki wieczornej")
        if e.okno.pokazana_plytka() != skan_id:
            e.klik(f"plytka_{skan_id}")
        e.czekaj(lambda: e.okno.pokazana_plytka() == skan_id, 5.0, "plytka wieczorna na ekranie")
        e.klik_gniazdo_wieczor(gniazdo)
        e.czekaj(lambda: e.aktywny("przycisk_ukruszona"), 5.0, "przycisk Ukruszona aktywny")
        e.klik("przycisk_ukruszona")

    def wybierz_kandydata(self, skan_id: int, gniazdo: int, klucz: str) -> dict:
        e, T = self.e, self.T
        self.osoba()
        kuweta = next(z["kuweta"] for z in T.SCEN["zlecenia"] if z["klucz"] == T.PROJ[klucz]["zlecenie"])
        e.klik_gniazdo_rano(skan_id, gniazdo)
        e.czekaj(lambda: e.jest("kandydat_1"), 5.0, "kandydaci pracy dwuznacznej")
        widoczni = {}
        for i in range(1, 9):
            if e.jest(f"kandydat_{i}"):
                widoczni[i] = (e.tekst(f"kandydat_{i}_kuweta") or "", e.tekst(f"kandydat_{i}_zab") or "")
        wybor = [i for i, (kuw, _) in widoczni.items() if kuw.split() and kuw.split()[-1] == kuweta]
        if len(wybor) != 1:
            raise BladSterownika(f"kandydat z kuweta {kuweta}: na ekranie {len(wybor)} (kandydatow {len(widoczni)})")
        e.klik(f"kandydat_{wybor[0]}_wybierz")
        return {"kandydaci_na_ekranie": [list(v) for v in widoczni.values()], "wybrany_nr": wybor[0]}

    def przypisz(self, skan_id: int, gniazdo: int, klucz: str) -> None:
        e, T = self.e, self.T
        self.osoba()
        kuweta = next(z["kuweta"] for z in T.SCEN["zlecenia"] if z["klucz"] == T.PROJ[klucz]["zlecenie"])
        pid = self.projekt_id(klucz)
        e.klik_gniazdo_rano(skan_id, gniazdo)
        e.czekaj(lambda: e.jest("praca_rano_przypisz"), 5.0, "przycisk przypisania recznego")
        e.klik("praca_rano_przypisz")
        e.czekaj(lambda: e.jest("praca_rano_przypisz_kuweta"), 5.0, "pole numeru kuwety")
        e.wpisz_w_pole("praca_rano_przypisz_kuweta", kuweta)
        if not e.jest(f"projekt_{pid}") and e.jest("praca_rano_przypisz_pokaz"):
            e.klik("praca_rano_przypisz_pokaz")
        e.czekaj(lambda: e.jest(f"projekt_{pid}"), 5.0, "projekty kuwety na ekranie")
        e.klik(f"projekt_{pid}")

    def bez_projektu(self, skan_id: int, gniazdo: int) -> None:
        e = self.e
        self.osoba()
        e.klik_gniazdo_rano(skan_id, gniazdo)
        e.czekaj(lambda: e.jest("praca_rano_bez_projektu"), 5.0, "przycisk 'bez projektu'")
        e.klik("praca_rano_bez_projektu")

    def zastap(self) -> None:
        e = self.e
        self.osoba()
        e.czekaj(lambda: e.jest("odp_potwierdz_ponowny_skan"), 5.0, "pytanie o ponowny skan")
        e.klik("odp_potwierdz_ponowny_skan")

    def strona(self, nazwa: str) -> None:
        e = self.e
        if e.jest(nazwa) and e.w(nazwa).isEnabled():
            e.klik(nazwa)

    def odmowa_zamkniecia(self) -> tuple:
        """(odmowa, opis zrodla) - jak odmowe "Zamknij piec" widac na ekranie."""
        e = self.e
        e.odczekaj(60)
        if not e.jest("przycisk_zamknij_piec"):
            self.strona("rano_strona_rozkladanie")
        jest, aktywny = e.jest("przycisk_zamknij_piec"), e.aktywny("przycisk_zamknij_piec")
        opis = {"przycisk_zamknij_piec": "nieaktywny" if jest and not aktywny else "aktywny" if jest else "niewidoczny",
                "rano_blokady": e.tekst("rano_blokady"), "blokady_w_stanie_pieca": len(self.rano.stan_pieca()["blokady"])}
        if jest and not aktywny:
            opis["zrodlo"] = "ekran: przycisk widoczny i nieaktywny (nie da sie kliknac), powod w napisie rano_blokady"
            return True, opis
        if not jest:
            opis["zrodlo"] = "ekran: przycisku nie ma - odmowy nie da sie odczytac"
            return None, opis
        piec = self.rano.otwarty_piec()
        e.klik("przycisk_zamknij_piec")
        e.odczekaj(100)
        if e.jest("pytanie_zamknij_mimo"):
            e.klik("zamknij_mimo_wroc")
            opis["zrodlo"] = "ekran: przycisk aktywny, okno zapytalo o zamkniecie mimo prac nierozstrzygnietych (to nie odmowa)"
            return False, opis
        po = self.rano.otwarty_piec()
        opis["zrodlo"] = "ekran: przycisk aktywny i klikniety; odmowa = piec nadal otwarty"
        return po is not None and piec is not None and po["id"] == piec["id"], opis

    def zamknij_piec(self, nr: int) -> tuple:
        """Klikniecie "Zamknij piec" (+ odpowiedz na pytanie okna). Zwraca (wynik pieca z API, odczyt ekranu)."""
        e = self.e
        self.osoba()
        piec = self.rano.otwarty_piec()
        if piec is None:
            raise BladSterownika(f"piec {nr}: nie ma otwartego pieca")
        if not e.jest("przycisk_zamknij_piec"):
            self.strona("rano_strona_rozkladanie")
        e.czekaj(lambda: e.aktywny("przycisk_zamknij_piec"), 10.0, f"piec {nr}: przycisk Zamknij piec aktywny")
        wg_sesji = dict(self.rano.stan_pieca()["nierozstrzygniete"])
        stan_rano = self.k.stan().rano
        bez_decyzji = len(getattr(stan_rano, "nierozstrzygniete_prace", ()) or ()) if stan_rano is not None else None
        e.klik("przycisk_zamknij_piec")
        e.odczekaj(150)
        pytanie = e.jest("pytanie_zamknij_mimo")
        if pytanie:
            e.klik("zamknij_mimo_tak")
        self.raport["pytania_zamkniecia"][str(nr)] = {
            "oczekiwane_wg_zlecenia": PYTANIE_OCZEKIWANE[nr], "bylo": pytanie, "zgodne": pytanie == PYTANIE_OCZEKIWANE[nr],
            "nierozstrzygniete_wg_sesji": wg_sesji, "prace_bez_decyzji_wg_stanu_okna": bez_decyzji}
        if pytanie != PYTANIE_OCZEKIWANE[nr]:
            self.raport["uwagi"].append(
                f"piec {nr}: pytanie okna przed 'Zamknij piec' - oczekiwane wg zlecenia: {'tak' if PYTANIE_OCZEKIWANE[nr] else 'nie'}, "
                f"bylo: {'tak' if pytanie else 'nie'}; nierozstrzygniete wg sesji: {json.dumps(wg_sesji)}, prace bez decyzji wg stanu okna "
                f"(StanRano.nierozstrzygniete_prace - o nie pyta okno): {bez_decyzji}. Okno pyta tylko o prace dwuznaczne / nieznane "
                "BEZ decyzji; praca z decyzja 'bez projektu' jest dla sesji nadal nieznana, ale okno o nia nie pyta")
        e.czekaj(lambda: self.rano.wynik_pieca(piec["id"]) is not None, 10.0, f"piec {nr} zamkniety")
        e.czekaj(lambda: e.tabela("tabela_kompletne") is not None, 5.0, f"piec {nr}: strona kompletnych i brakow")
        e.odczekaj(80)
        return self.rano.wynik_pieca(piec["id"]), self.odczyt_list()

    def odczyt_list(self) -> dict:
        e = self.e
        e.odczekaj(60)
        d = {n: e.tabela(n) for n in ("tabela_kompletne", "tabela_braki", "tabela_braki_biezace")}
        for n in ("rano_wynik_tytul", "rano_nierozstrzygniete", "rano_poprawki"):
            d[n] = e.tekst(n)
        return d


# --- porownanie ekranu z tabela oczekiwan ----------------------------------------------------------
def kuwety_ekranu(tab) -> list | None:
    return None if tab is None else [w[0] for w in tab]


def braki_ekranu(tab) -> list | None:
    return None if tab is None else [(w[0], w[1]) for w in tab]


def braki_oczekiwane(braki: list) -> list:
    return [(kuweta, ", ".join(zab for zab, _ in zeby)) for kuweta, zeby in braki]


def poprawki_na_ekranie(napis, poprawki: list) -> bool:
    """Czy napis poprawek z ekranu zawiera KAZDA oczekiwana poprawke: numer kuwety i kazdy zab jako cale liczby (nie podciagi)."""
    if napis is None or not poprawki:
        return False
    liczby = set(re.findall(r"[0-9]+", str(napis)))
    for poprawka in poprawki:
        wymagane = set(re.findall(r"[0-9]+", str(poprawka[0]))) | set(re.findall(r"[0-9]+", str(poprawka[1])))
        if not wymagane or not wymagane <= liczby:
            return False
    return True


def ocen(odczyty: list, zgodne: bool, opis: str) -> dict:
    """Wpis kolumny "ekran": ``odczyty`` - wartosci odczytane z okna (None = nie odczytano)."""
    if any(o is None for o in odczyty):
        return {"ekran": "nie odczytano", "opis": opis, "odczyt": odczyty}
    return {"ekran": "tak" if zgodne else "nie", "opis": opis, "odczyt": odczyty}


def scenariusz(p: Przebieg, w: dict, ek: dict, zrodla: dict) -> None:
    """SE10 krok po kroku jak ``test_session_rano._scenariusz``; czynnosci technika = klikniecia w oknie."""
    T, z = p.T, p.zegar
    ocz = {nr: o for nr, _, o in T.TABELA_SE10}
    # dzien 1 (17.11) wieczor
    p.otworz()
    T.wypelnij_indeks(p.sesja.baza)
    p.tryb("wieczor")
    p.osoba()
    w1 = p.skan("w1")
    p.skan("w2")
    z.ustaw("2026-11-17T19:30:00")
    p.ukruszona(w1, 4)
    w["R01"] = T.lista_dofrez(p.sesja)
    w["R02"] = p.stan_punktu("X13")[0]
    zrodla["R01"] = "klik: osoba_0, plytka_<id>, gniazdo 4 mapy, przycisk_ukruszona"
    # dzien 2 (18.11), piec 1
    z.ustaw("2026-11-18T06:59:00")
    p.tryb("rano")
    a = p.skan("p1_4")
    r = p.rano
    stan = r.stan_pieca()
    w["R03"] = (r.otwarty_piec()["data"], r.otwarty_piec()["nr_w_dniu"], stan["otwarty"], stan["plan_id"])
    b = p.skan("p1_5")
    stan = r.stan_pieca()
    w["R04"] = {4: T.klasy(stan, a), 5: T.klasy(stan, b)}
    p22 = T.praca_stanu(stan, b, 2)
    w["R05"] = [(pr["kuweta"], pr["zeby"]) for k in p22["kandydaci"] for pr in k["projekty"]]
    z.ustaw("2026-11-18T07:08:00")
    info = p.wybierz_kandydata(b, 2, "Y22")
    zrodla["R05"] = f"dodatkowo ekran: kandydatow na ekranie {len(info['kandydaci_na_ekranie'])}"
    x = T.praca_stanu(r.stan_pieca(), b, 2)
    w["R06"] = (x["klasa"], x["kolor"], x["kuweta"], p.liczba("decyzje WHERE rodzaj = 'wybor_kandydata'"))
    zrodla["R06"] = f"klik: gniazdo 2 mapy porannej, kandydat_{info['wybrany_nr']}_wybierz (kandydat z kuweta scenariusza)"
    p.przypisz(b, 3, "Z31")
    x = T.praca_stanu(r.stan_pieca(), b, 3)
    w["R07"] = (x["klasa"], x["kolor"], x["kuweta"], x["zeby"])
    zrodla["R07"] = "klik: gniazdo 3, praca_rano_przypisz, numer kuwety klawiszami + Enter, projekt_<id>"
    c = p.skan("p1_5_ponownie")
    stan = r.stan_pieca()
    propozycje = [{k: q[k] for k in ("skan_id", "poprzedni_id", "numer_plytki")} for q in stan["do_potwierdzenia"]]
    odmowa, opis = p.odmowa_zamkniecia()
    w["R08"] = (propozycje == [{"skan_id": c, "poprzedni_id": b, "numer_plytki": 5}],
                [(k["kuweta"], k["zeby"]) for k in stan["konflikty"]], odmowa)
    zrodla["R08"] = opis
    z.ustaw("2026-11-18T07:14:00")
    p.zastap()
    stan = r.stan_pieca()
    w["R09"] = (p.skan_wiersz(b)["status"], len(stan["konflikty"]), T.klasy(stan, c)[3])
    zrodla["R09"] = "klik: odp_potwierdz_ponowny_skan"
    p.przypisz(c, 3, "Z31")
    stan = r.stan_pieca()
    w["R10"] = T.klasy(stan, c)[3]
    zrodla["R10"] = "klik: gniazdo 3 nowego skanu, praca_rano_przypisz, numer kuwety + Enter, projekt_<id>"
    w["R11"] = (T.kuwety(stan["kompletne"]), T.braki_skrot(stan["braki"]))
    p.strona("rano_strona_wynik")
    o = p.odczyt_list()
    p.strona("rano_strona_rozkladanie")
    kk, bb = kuwety_ekranu(o["tabela_kompletne"]), braki_ekranu(o["tabela_braki"])
    ek["R11"] = ocen([kk, bb], kk == ocz["R11"][0] and bb == braki_oczekiwane(ocz["R11"][1]),
                     "strona 'Kompletne i braki' pieca otwartego: tabela_kompletne (kuwety), tabela_braki (kuweta, zeby)")
    plan = r.plan_plytek()
    w["R12"] = T.skrot_planu(plan)
    w["R13"] = T.waliduj_plan(plan)
    z.ustaw("2026-11-18T07:30:00")
    wynik1, o = p.zamknij_piec(1)
    w["R14"] = T.kuwety(wynik1["kompletne"])
    w["R15"] = T.braki_skrot(wynik1["braki"])
    kk, bb = kuwety_ekranu(o["tabela_kompletne"]), braki_ekranu(o["tabela_braki"])
    ek["R14"] = ocen([kk], kk == ocz["R14"], "po 'Zamknij piec' 1: tabela_kompletne (kuwety)")
    ek["R15"] = ocen([bb], bb == braki_oczekiwane(ocz["R15"]), "po 'Zamknij piec' 1: tabela_braki (kuweta, zeby)")
    w["R16"] = {k: p.stan_punktu(k) for k in T.PROJ}
    w["R17"] = (T.lista_dofrez(p.sesja), T.lista_zgodna_ze_stanem_punktow(p.sesja))
    bz = braki_ekranu(o["tabela_braki_biezace"])
    ek["R17"] = {"ekran": "nie dotyczy", "odczyt": [bz],
                 "opis": "listy 'do dofrezowania' ekran poranny nie pokazuje (jest na ekranie wieczornym - tabela_dofrezowania); "
                         "posrednio: zab jest w tabela_braki_biezace: " + ("tak" if bz is not None and ("3263", "13") in bz else "nie")}
    # restart programu miedzy piecami
    przed = T.migawka(p)
    p.restart()
    r = p.rano
    w["R18"] = T.migawka(p) == przed and r.otwarty_piec() is None
    zrodla["R18"] = f"restart; tryb po restarcie: {p.k.stan().tryb}"
    p.tryb("rano")
    # dzien 2, piec 2
    z.ustaw("2026-11-18T09:29:00")
    p.osoba()
    p.skan("p2_4")
    e_ = p.skan("p2_6")
    stan = r.stan_pieca()
    odmowa, opis = p.odmowa_zamkniecia()
    w["R19"] = ([(k["kuweta"], k["zeby"], sorted(m["numer_plytki"] for m in k["miejsca"])) for k in stan["konflikty"]], odmowa)
    zrodla["R19"] = opis
    z.ustaw("2026-11-18T09:40:00")
    p.bez_projektu(e_, 3)
    stan = r.stan_pieca()
    x = T.praca_stanu(stan, e_, 3)
    w["R20"] = (x["klasa"], x["status"], x["kolor_ramki"], len(stan["konflikty"]))
    zrodla["R20"] = "klik: gniazdo 3 plytki 6, praca_rano_bez_projektu"
    z.ustaw("2026-11-18T09:45:00")
    wynik2, o = p.zamknij_piec(2)
    w["R21"] = T.kuwety(wynik2["kompletne"])
    w["R22"] = (T.braki_skrot(r.braki()), wynik2["nierozstrzygniete"])
    kk, bz, nier = kuwety_ekranu(o["tabela_kompletne"]), braki_ekranu(o["tabela_braki_biezace"]), o["rano_nierozstrzygniete"]
    ek["R21"] = ocen([kk], kk == ocz["R21"], "po 'Zamknij piec' 2: tabela_kompletne (kuwety)")
    ek["R22"] = ocen([bz], bz == braki_oczekiwane(ocz["R22"][0]),
                     "po 'Zamknij piec' 2: tabela_braki_biezace (kuweta, zeby); druga czesc wiersza (1 praca nieznana "
                     "nierozstrzygnieta) - napis rano_nierozstrzygniete z liczba (1): "
                     + ("jest" if nier is not None and "(1)" in nier else
                        "BRAK - ekran nazywa nierozstrzygnietymi tylko prace bez decyzji, a ta ma decyzje 'bez projektu'; "
                        "ta czesc wiersza tylko z API"))
    # dzien 2 wieczor: dofrezowany zab X13 przechodzi przez skan wieczorny
    z.ustaw("2026-11-18T19:59:00")
    p.tryb("wieczor")
    p.skan("w3")
    w["R23"] = (T.lista_dofrez(p.sesja), p.stan_punktu("X13")[0])
    # dzien 3 (19.11), piec 3
    z.ustaw("2026-11-19T06:59:00")
    p.tryb("rano")
    f = p.skan("p3_4")
    stan = r.stan_pieca()
    x13, y21 = T.praca_stanu(stan, f, 2), T.praca_stanu(stan, f, 3)
    w["R24"] = (x13["klasa"], x13["domyka_dofrezowanie"], x13["sha16"])
    w["R25"] = (y21["klasa"], y21["kolor"], y21["zlecenie_odhaczone"], y21["liczona"])
    piec_przed = r.otwarty_piec()
    p.restart()
    r = p.rano
    w["R26"] = r.stan_pieca() == stan and r.otwarty_piec() == piec_przed
    zrodla["R26"] = f"restart; tryb po restarcie: {p.k.stan().tryb}"
    p.tryb("rano")
    w["R27"] = T.skrot_planu(r.plan_plytek())
    z.ustaw("2026-11-19T07:20:00")
    wynik3, o = p.zamknij_piec(3)
    w["R28"] = T.kuwety(wynik3["kompletne"])
    w["R29"] = ([(q["kuweta"], q["zeby"], q["zlecenie_odhaczone"]) for q in wynik3["poprawki"]],
                p.liczba("zdarzenia WHERE typ = 'poprawka_rano'"), "3301" in T.kuwety(wynik3["kompletne"]))
    w["R30"] = (T.braki_skrot(r.braki()), T.lista_dofrez(p.sesja), p.stan_punktu("X13"))
    kk, bz, pop = kuwety_ekranu(o["tabela_kompletne"]), braki_ekranu(o["tabela_braki_biezace"]), o["rano_poprawki"]
    ek["R28"] = ocen([kk], kk == ocz["R28"], "po 'Zamknij piec' 3: tabela_kompletne (kuwety)")
    # uwaga 19 recenzji: porownanie z wartosciami tabeli oczekiwan (cale liczby, nie podciagi napisu; braki z tabeli)
    ek["R29"] = ocen([kk, pop], poprawki_na_ekranie(pop, ocz["R29"][0]) and kk is not None
                     and all(str(q[0]) not in kk for q in ocz["R29"][0]),
                     "po 'Zamknij piec' 3: napis rano_poprawki zawiera kuwete i zeby KAZDEJ oczekiwanej poprawki (cale liczby); "
                     "kuwety poprawki nie ma w tabela_kompletne")
    ek["R30"] = ocen([bz], bz == braki_oczekiwane(ocz["R30"][0]),
                     "po 'Zamknij piec' 3: tabela_braki_biezace = oczekiwane braki (puste; listy 'do dofrezowania' ekran poranny "
                     "nie pokazuje - ta czesc wiersza tylko z API)")
    p.restart()
    r = p.rano
    w["R31"] = [T.skrot_wyniku(r.wynik_pieca(i)) for i in (1, 2, 3)]
    p.tryb("rano")
    p.strona("rano_strona_wynik")
    o = p.odczyt_list()
    if o["tabela_kompletne"] is None:
        p.strona("rano_strona_ostatni")
        o = {"tabela_kompletne": p.e.tabela("ostatni_tabela_kompletne"), "tabela_braki": p.e.tabela("ostatni_tabela_braki"),
             "rano_poprawki": p.e.tekst("ostatni_rano_poprawki"), "rano_wynik_tytul": p.e.tekst("ostatni_rano_wynik_tytul")}
    kk, bb, pop = kuwety_ekranu(o["tabela_kompletne"]), braki_ekranu(o["tabela_braki"]), o["rano_poprawki"]
    piec3 = ocz["R31"][2]
    zgodny3 = kk == piec3[1] and bb == braki_oczekiwane(piec3[2]) and poprawki_na_ekranie(pop, ocz["R29"][0])
    ek["R31"] = ocen([kk, bb, pop], zgodny3, "po restarcie ekran pokazuje tylko ostatni zamkniety piec (3): tabela_kompletne, "
                                             "tabela_braki, rano_poprawki; piecow 1 i 2 (poprzednia doba) ekran nie pokazuje")
    if ek["R31"]["ekran"] == "tak":
        ek["R31"]["ekran"] = "czesciowo"
        ek["R31"]["opis"] += " - piec 3 zgodny, piece 1 i 2 tylko z API"
    api = ([wynik1, wynik2, wynik3, r.braki(), r.piece(T.DOBA2), r.piece("2026-11-19")]
           + [r.stan_pieca(i) for i in (1, 2, 3)] + [plan])
    czyste, pliki = T.nazwy_nie_wychodza(p, api)
    w["R32"] = czyste and pliki == 9  # 9 plikow wynikow skanow (3 wieczorne + 6 porannych)
    zrodla["R32"] = {"czyste": czyste, "plikow_w_dane": pliki}


def nazwy_poza_dane(T, wyjscie: Path) -> dict:
    """Dodatek do R32: slowa z nazw zlecen w logach programu i plikach obok bazy (poza plikiem bazy)."""
    pliki = [q for kat in ("logi", "baza", "podglady") for q in (wyjscie / kat).rglob("*")
             if q.is_file() and not q.name.startswith("stanowisko.sqlite")]
    trafione = 0
    for q in pliki:
        try:
            tekst = q.read_text(encoding="utf-8", errors="replace").lower()
        except OSError:
            continue
        if any(sl in tekst for sl in T.SLOWA):
            trafione += 1
    return {"plikow_sprawdzonych": len(pliki), "plikow_z_nazwami": trafione}


# --- wynik -----------------------------------------------------------------------------------------
def zbuduj_wynik(T, w: dict, ek: dict, zrodla: dict, raport: dict) -> dict:
    blad = raport.get("przerwano")
    wiersze = []
    for nr, opis, oczekiwane in T.TABELA_SE10:
        policzony = nr in w
        zgodny = (w[nr] == oczekiwane) if policzony else None
        e = ek.get(nr) if nr in WIERSZE_LIST else None
        if nr in WIERSZE_LIST and e is None:
            e = {"ekran": "nie odczytano", "opis": "scenariusz przerwany przed odczytem", "odczyt": None}
        # P3 recenzji: wiersz liczy sie jako zgodny tylko wtedy, gdy zgadza sie takze to, co POKAZUJE ekran - odczyt ekranu
        # "nie" albo "nie odczytano" daje wynik "FAIL (ekran)", choc wartosc z API sesji jest zgodna
        ekran_zly = bool(e) and e["ekran"] in ("nie", "nie odczytano")
        wiersze.append({"nr": nr, "opis": opis, "oczekiwane": oczekiwane, "faktyczne": w.get(nr) if policzony else None,
                        "zgodny": zgodny, "zgodny_wg_api": zgodny,
                        "wynik": "nie policzono" if not policzony else "FAIL" if not zgodny else "FAIL (ekran)" if ekran_zly else "PASS",
                        "powod": None if policzony else f"scenariusz przerwany: {blad}",
                        "ekran": e["ekran"] if e else "-", "ekran_opis": e["opis"] if e else None,
                        "ekran_odczyt": e["odczyt"] if e else None, "zrodlo": zrodla.get(nr)})
    n = sum(1 for x in wiersze if x["wynik"] == "PASS")
    stany = [x["ekran"] for x in wiersze if x["nr"] in WIERSZE_LIST]
    m, k = stany.count("tak"), len(stany) - stany.count("nie dotyczy")
    raport = dict(raport)
    raport["liczniki"] = {"wierszy": len(wiersze), "zgodnych": n, "niezgodnych": sum(1 for x in wiersze if x["wynik"].startswith("FAIL")),
                          "zgodnych_wg_api": sum(1 for x in wiersze if x["zgodny"]),
                          "niezgodnych_tylko_ekran": sum(1 for x in wiersze if x["wynik"] == "FAIL (ekran)"),
                          "nie_policzono": sum(1 for x in wiersze if x["zgodny"] is None),
                          "listy_z_ekranu": {s: stany.count(s) for s in ("tak", "nie", "nie odczytano", "czesciowo", "nie dotyczy")},
                          "listy_z_ekranu_tak": m, "listy_z_ekranu_z": k}
    ls = raport["liczniki"]["listy_z_ekranu"]
    werdykt = "FAIL" if n < len(wiersze) or blad else "ZAL z odstepstwem O5" if ls["czesciowo"] or ls["nie dotyczy"] else "ZAL"
    raport["werdykt"] = werdykt
    raport["podsumowanie"] = (f"SE10 przez ekran: {n} z {len(wiersze)} wierszy zgodnych (wiersz z odczytem ekranu 'nie' / 'nie odczytano' "
                              f"= niezgodny); wg samego API sesji {raport['liczniki']['zgodnych_wg_api']} z {len(wiersze)}; "
                              f"listy kompletnych i brakow z ekranu: {m} z {k}" + chr(10) +
                              f"WERDYKT T3: {werdykt} ({n} z {len(wiersze)}; ekran: tak {ls['tak']}, czesciowo {ls['czesciowo']}, "
                              f"nie dotyczy {ls['nie dotyczy']}, nie {ls['nie']}, nie odczytano {ls['nie odczytano']})")
    raport["wiersze"] = wiersze
    return raport


def zapisz_wynik(T, wyjscie: Path, w: dict, ek: dict, zrodla: dict, raport: dict) -> dict:
    wynik = zbuduj_wynik(T, dict(w), dict(ek), dict(zrodla), raport)
    tekst_json = json.dumps(wynik, indent=1, ensure_ascii=True, default=str)
    linie = [f"T3 - SE10 przez ekran (t3_poranek.py); program {wynik.get('wersja_programu')}; Qt {wynik.get('platforma_qt')}; "
             f"czas {wynik.get('czas_s')} s", "", f"{'nr':<4} {'wynik':<13} {'ekran':<14} opis"]
    for x in wynik["wiersze"]:
        linie.append(f"{x['nr']:<4} {x['wynik']:<13} {x['ekran']:<14} {x['opis']}")
    for x in wynik["wiersze"]:
        if x["wynik"] == "FAIL (ekran)":
            linie.append(f"  {x['nr']} FAIL (ekran): wartosc z API zgodna, ekran pokazuje co innego - {x['ekran_opis']}; odczyt: "
                         f"{json.dumps(x['ekran_odczyt'], default=str)}")
        elif x["wynik"] == "FAIL":
            linie += [f"  {x['nr']} oczekiwane: {json.dumps(x['oczekiwane'], default=str)}",
                      f"  {x['nr']} faktyczne:  {json.dumps(x['faktyczne'], default=str)}"]
        elif x["wynik"] == "nie policzono":
            linie.append(f"  {x['nr']} nie policzono: {x['powod']}")
    linie.append("")
    for x in wynik["wiersze"]:
        if x["ekran"] != "-":
            linie.append(f"  ekran {x['nr']}: {x['ekran']} - {x['ekran_opis']}")
    for nr_pieca, q in sorted((wynik.get("pytania_zamkniecia") or {}).items()):
        linie.append(f"  pytanie okna przed 'Zamknij piec' {nr_pieca}: oczekiwane wg zlecenia {'tak' if q['oczekiwane_wg_zlecenia'] else 'nie'}, "
                     f"bylo {'tak' if q['bylo'] else 'nie'}")
    for u in wynik.get("uwagi") or []:
        linie.append(f"  UWAGA: {u}")
    if wynik.get("przerwano"):
        linie.append(f"PRZERWANO: {wynik['przerwano']}")
    linie += ["", wynik["podsumowanie"]]
    tekst_txt = "\n".join(linie) + "\n"
    slowa = sorted(getattr(T, "SLOWA", []), key=len, reverse=True)
    usuniete = 0
    for sl in slowa:  # bezpiecznik: w wyniku nie moze byc slow z nazw zlecen (tylko kuwety, zeby, sha16)
        wzor = re.compile(re.escape(sl), re.IGNORECASE)
        tekst_json, a = wzor.subn("[NAZWA]", tekst_json)
        tekst_txt, b = wzor.subn("[NAZWA]", tekst_txt)
        usuniete += a + b
    if usuniete:
        tekst_txt += f"UWAGA: z wyniku usunieto {usuniete} wystapien slow z nazw zlecen\n"
    wyjscie.mkdir(parents=True, exist_ok=True)
    (wyjscie / PLIK_JSON).write_text(tekst_json + "\n", encoding="ascii", errors="backslashreplace", newline="\n")
    (wyjscie / PLIK_TXT).write_text(tekst_txt, encoding="ascii", errors="backslashreplace", newline="\n")
    wynik["_tekst"] = tekst_txt
    return wynik


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="t3_poranek.py", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Sterownik testu koncowego T3: scenariusz SE10 (32 wiersze tabeli oczekiwan) przez okno programu 'Stanowisko'.",
        epilog="Uruchamiaj z katalogu programu (z pakietem 'stanowisko') interpreterem programu.\n"
               "Kody wyjscia: 0 = scenariusz do konca i wynik zapisany; 1 = --wymagaj-100 i n < 32; 2 = blad / przerwany / limit czasu.")
    parser.add_argument("--testy", type=Path, default=Path("testy"),
                        help="katalog testow programu z test_session_rano.py i dane_sesji/rano/se10.json (domyslnie: testy w biezacym katalogu)")
    parser.add_argument("--wyjscie", type=Path, required=True, help="nowy / pusty katalog na baze, logi i t3_wynik.json / t3_wynik.txt")
    parser.add_argument("--limit-s", type=float, default=600.0, help="limit czasu calosci w sekundach (domyslnie 600); po nim kod 2")
    parser.add_argument("--wymagaj-100", action="store_true", help="kod wyjscia 1, gdy zgodnych wierszy jest mniej niz 32")
    parser.add_argument("--ustawienia-wzor", type=Path, default=None,
                        help="plik ustawien - wzor (domyslnie ustawienia.przyklad.toml w katalogu programu)")
    parser.add_argument("--ekran", action="store_true", help="nie ustawiaj QT_QPA_PLATFORM=offscreen (okno na prawdziwym ekranie)")
    args = parser.parse_args(argv)

    t0 = time.monotonic()
    program = Path.cwd()
    if not (program / "stanowisko" / "aplikacja.py").is_file():
        print(f"BLAD: biezacy katalog nie jest katalogiem programu (brak stanowisko/aplikacja.py): {program}", file=sys.stderr)
        return 2
    testy = args.testy.resolve()
    if not (testy / "test_session_rano.py").is_file():
        print(f"BLAD: w katalogu --testy nie ma test_session_rano.py: {testy}", file=sys.stderr)
        return 2
    wyjscie = args.wyjscie.resolve()
    if (wyjscie / "baza").exists() or (wyjscie / "dane").exists():
        print(f"BLAD: katalog --wyjscie zawiera dane poprzedniej proby (podaj nowy katalog): {wyjscie}", file=sys.stderr)
        return 2
    wzor = args.ustawienia_wzor or (program / "ustawienia.przyklad.toml")
    if not wzor.is_file():
        print(f"BLAD: brak pliku ustawien - wzoru: {wzor}", file=sys.stderr)
        return 2
    for sciezka in (str(testy), str(program)):
        if sciezka not in sys.path:
            sys.path.insert(0, sciezka)
    try:
        import pytest  # noqa: F401 - potrzebny modulowi testu
    except ImportError:
        print("BLAD: w tym interpreterze nie ma pytest (instalacja z paczki: zainstaluj.cmd /testy)", file=sys.stderr)
        return 2
    try:
        import test_session_rano as T
    except Exception as e:  # noqa: BLE001
        print(f"BLAD: nie da sie zaimportowac test_session_rano z {testy}: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    if len(T.TABELA_SE10) != 32:
        print(f"BLAD: TABELA_SE10 ma {len(T.TABELA_SE10)} wierszy, oczekiwane 32", file=sys.stderr)
        return 2
    if not args.ekran:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    fonty = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    if os.environ.get("QT_QPA_PLATFORM") == "offscreen" and fonty.is_dir():
        os.environ.setdefault("QT_QPA_FONTDIR", str(fonty))

    wyjscie.mkdir(parents=True, exist_ok=True)
    wersja = (program / "WERSJA").read_text(encoding="utf-8").strip() if (program / "WERSJA").is_file() else None
    raport = {"narzedzie": "t3_poranek.py", "scenariusz": "SE10 (test_session_rano.TABELA_SE10) przez okno programu",
              "wersja_programu": wersja, "interpreter": sys.executable, "python": platform.python_version(),
              "system": platform.platform(), "platforma_qt": None, "kontroler": "stanowisko.aplikacja.Aplikacja (ramki=False, excel=False)",
              "limit_s": args.limit_s, "czas_s": None, "przerwano": None, "starty_programu": 0, "pytania_zamkniecia": {},
              "podane_wyniki": [], "czynnosci": [], "uwagi": [], "dodatkowo": {}}
    w: dict = {}
    ek: dict = {}
    zrodla: dict = {}
    koniec = threading.Event()

    def straznik() -> None:
        if koniec.wait(args.limit_s):
            return
        raport["przerwano"] = f"limit czasu {args.limit_s:.0f} s"
        raport["czas_s"] = round(time.monotonic() - t0, 1)
        try:
            wynik = zapisz_wynik(T, wyjscie, w, ek, zrodla, raport)
            print(f"PRZERWANO: limit czasu {args.limit_s:.0f} s; wynik czesciowy zapisany", flush=True)
            print(wynik["podsumowanie"], flush=True)
        finally:
            zabij_potomne()
            os._exit(2)

    threading.Thread(target=straznik, name="t3-straznik", daemon=True).start()
    przebieg = None
    try:
        from PySide6 import QtCore, QtGui, QtWidgets  # noqa: F401 - Qt w calosci przed silnikiem (jak aplikacja.main)

        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
        raport["platforma_qt"] = app.platformName()
        from stanowisko import aplikacja as A

        A.zaladuj_moduly_dll()
        plik_ustawien = zloz_ustawienia(wzor, wyjscie)
        przebieg = Przebieg(T, plik_ustawien, wyjscie, Zegar("2026-11-17T18:00:00"), raport)
        scenariusz(przebieg, w, ek, zrodla)
    except Exception as e:  # noqa: BLE001 - wiersze niepoliczone dostaja "nie policzono" z powodem
        raport["przerwano"] = f"{type(e).__name__}: {e}"
        raport["slad"] = traceback.format_exc().splitlines()[-12:]
    finally:
        try:
            if przebieg is not None:
                przebieg.zamknij()
        except Exception as e:  # noqa: BLE001
            raport["dodatkowo"]["blad_zamykania"] = f"{type(e).__name__}: {e}"
        raport["dodatkowo"]["procesy_potomne_zabite_na_koncu"] = zabij_potomne()
    try:
        raport["dodatkowo"]["nazwy_poza_dane"] = nazwy_poza_dane(T, wyjscie)
    except Exception as e:  # noqa: BLE001
        raport["dodatkowo"]["nazwy_poza_dane"] = f"nie sprawdzono: {type(e).__name__}"
    raport["czas_s"] = round(time.monotonic() - t0, 1)
    wynik = zapisz_wynik(T, wyjscie, w, ek, zrodla, raport)
    koniec.set()
    print(wynik["_tekst"], end="")
    n = wynik["liczniki"]["zgodnych"]
    if raport["przerwano"]:
        kod = 2
    elif args.wymagaj_100 and n < len(T.TABELA_SE10):
        kod = 1
    else:
        kod = 0
    print(f"kod wyjscia {kod}; wynik: {PLIK_JSON}, {PLIK_TXT} w katalogu --wyjscie")
    print(wynik["podsumowanie"], flush=True)

    def twardy_koniec() -> None:  # watki programu (obserwator, liczenie puli) nie moga zatrzymac wyjscia z procesu
        time.sleep(20)
        zabij_potomne()
        os._exit(kod)

    threading.Thread(target=twardy_koniec, name="t3-koniec", daemon=True).start()
    return kod


if __name__ == "__main__":
    raise SystemExit(main())
