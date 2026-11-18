"""Program ramki: petla sprzetu (czujniki, klawiatura, matryca) + serwer HTTP + logika.

Uruchomienie (szczegoly w README.md):
  python -m ramka --rola P --sprzet atrapa                 # bez elektroniki, 127.0.0.1:8765
  python -m ramka --sprzet rpi --konfiguracja /etc/ramka/ramka.json   # Raspberry Pi (host i klucz z pliku)
Petla co `okres_s` (10 ms): odczyt czujnikow z odbijaniem (gaszenie od razu, zapalanie po
ustaleniu - P7), klawisze, uplyw czasu (waznosc planu), nowa klatka na matryce tylko przy zmianie.
Zadanie HTTP zmieniajace stan budzi petle od razu (stan ramki po Spacji na laptopie ponizej 1 s - I6).
Kazdy wyjatek w obiegu petli (czujniki, klawiatura, matryca, logika) = awaria sprzetu: matryca od
razu bez gniazd, plan usuniety, zdarzenie blad_sprzetu (P4); sprzet_dziala dopiero po `powrot_sprzetu_s`
udanych obiegow bez wyjatku (D-N7: awaria przerywana nie daje pary zdarzen co sekunde).
"""
from __future__ import annotations

import argparse
import json
import logging
import signal
import threading
import time
from dataclasses import dataclass, fields
from pathlib import Path

from . import WERSJA, obraz, protokol
from .logika import LogikaRamki
from .protokol import BladProtokolu
from .sprzet import BladSprzetu, Odbijanie

log = logging.getLogger("ramka.program")


@dataclass
class Konfiguracja:
    rola: str = "P"                      # W = ramka wieczorna, P = ramka poranna (klawiatura)
    host: str = "127.0.0.1"              # adres nasluchu; inny (np. adres ramki w sieci) TYLKO z konfiguracji
    port: int = 8765                     # [ramki] port w ustawieniach stanowiska
    klucz: str = ""                      # wspolny klucz X-Ramka-Klucz (P6) - tylko w pliku lokalnym, nie w repo
    sprzet: str = "atrapa"               # atrapa albo rpi
    okres_s: float = 0.01                # okres petli sprzetu
    stabilnosc_s: float = 0.03           # odbijanie czujnikow Halla
    odstep_drgan_s: float = 3.0          # powrot do poprzedniego numeru plytki najwczesniej po tylu s (drgania)
    powrot_sprzetu_s: float = 3.0        # sprzet_dziala po tylu s udanych obiegow od ostatniego wyjatku
    limit_lacznosci_s: float = 30.0      # po tylu sekundach ciszy laptop uznany za nieobecny
    rodzina: tuple = ()                  # numery plytek ramki; puste = W: 1-3, P: 4-6
    sterowanie_atrapy: bool = False      # zasoby /atrapa/* (tylko atrapa)
    piny_halla: tuple = (19, 25, 8)      # BCM: A, B, C (plan_ramki_v2 8.2)
    jasnosc: int = 60                    # procent (rpi-rgb-led-matrix)
    obrot: int = 0                       # 0 / 90 / 180 / 270 - ustawia C1 na sprzecie
    lustro: bool = False
    mapowanie: str = "adafruit-hat-pwm"  # plan_ramki_v2 8.1
    spowolnienie_gpio: int = 4           # --led-slowdown-gpio (Pi 4)
    klawisz_zamknij_piec: str = "KEY_KPASTERISK"


def wczytaj_konfiguracje(sciezka) -> Konfiguracja:
    """Plik JSON z kluczami jak pola Konfiguracja (nieznany klucz = blad)."""
    dane = json.loads(Path(sciezka).read_text(encoding="utf-8"))
    if not isinstance(dane, dict):
        raise ValueError("konfiguracja: oczekiwano obiektu JSON")
    znane = {f.name for f in fields(Konfiguracja)}
    nieznane = sorted(set(dane) - znane)
    if nieznane:
        raise ValueError("konfiguracja: nieznane klucze " + ", ".join(nieznane))
    for k in ("rodzina", "piny_halla"):
        if k in dane:
            dane[k] = tuple(dane[k])
    if "klucz" in dane:
        protokol.sprawdz_klucz(dane["klucz"])
    return Konfiguracja(**dane)


def utworz_sprzet(konf: Konfiguracja):
    if konf.sprzet == "atrapa":
        from .sprzet_atrapa import SprzetAtrapa
        return SprzetAtrapa()
    if konf.sprzet == "rpi":
        from .sprzet_rpi import SprzetRpi
        return SprzetRpi(rola=konf.rola, piny_halla=konf.piny_halla, jasnosc=konf.jasnosc, obrot=konf.obrot,
                         lustro=konf.lustro, mapowanie=konf.mapowanie, spowolnienie_gpio=konf.spowolnienie_gpio,
                         klawisz_zamknij_piec=konf.klawisz_zamknij_piec)
    raise BladSprzetu("sprzet: atrapa albo rpi")


class ProgramRamki:
    def __init__(self, konf: Konfiguracja, sprzet=None, zegar=time.perf_counter, start_id=None):
        if konf.rola not in ("W", "P"):
            raise ValueError("rola: W albo P")
        if konf.sterowanie_atrapy and konf.sprzet != "atrapa" and sprzet is None:
            raise ValueError("sterowanie atrapy tylko z atrapa sprzetu")
        protokol.sprawdz_klucz(konf.klucz)
        self.konf = konf
        self.zegar = zegar
        self.sprzet = sprzet if sprzet is not None else utworz_sprzet(konf)
        self.logika = LogikaRamki(konf.rola, start_id=start_id, teraz=zegar(),
                                  limit_lacznosci_s=konf.limit_lacznosci_s, rodzina=konf.rodzina or None,
                                  program=WERSJA)
        self.odbijanie = self._nowe_odbijanie()
        self._awaria_t = float("-inf")  # chwila ostatniego wyjatku w obiegu petli (D-N7)
        self.warunek = threading.Condition(threading.RLock())
        self._pokazana = None
        self._zmiana_pokazana = -1
        self._ostatni_obraz = float("-inf")
        self._stop = threading.Event()
        self._budzik = threading.Event()
        self._watek = None
        self._watek_serwera = None
        self.serwer = None
        self.zamykanie = False

    # ------------------------------------------------------------ petla sprzetu

    def _nowe_odbijanie(self) -> Odbijanie:
        return Odbijanie(self.konf.stabilnosc_s, odstep_powrotu_s=self.konf.odstep_drgan_s)

    def krok(self, teraz=None) -> bool:
        """Jedna iteracja petli: czujniki, klawisze, czas, obraz. False = awaria sprzetu (P4):
        wyjatek nie wychodzi z krok(), matryca gasnie od razu, plan usuniety, zdarzenie blad_sprzetu."""
        teraz = self.zegar() if teraz is None else teraz
        try:
            self._krok(teraz)
        except Exception:  # noqa: BLE001 - kazdy wyjatek obiegu = awaria, ramka ciemna
            if not self.logika.awaria:
                log.exception("blad w petli sprzetu - matryca wygaszona")
            self._awaria(teraz)
            return False
        if self.logika.awaria and teraz - self._awaria_t >= self.konf.powrot_sprzetu_s:
            # D-N7: caly obieg (odczyt, logika, matryca) bez wyjatku przez powrot_sprzetu_s od ostatniego bledu -
            # awaria przerywana nie daje pary blad_sprzetu / sprzet_dziala w kazdej sekundzie
            with self.warunek:
                self.logika.koniec_awarii(teraz)
                self.warunek.notify_all()
            log.warning("sprzet ramki znow dziala (plan trzeba wyslac ponownie)")
        return True

    def _krok(self, teraz) -> None:
        surowa = self.sprzet.odczytaj_plytke()
        klawisze = self.sprzet.pobierz_klawisze()
        temp = self.sprzet.temperatura()
        klatka = None
        with self.warunek:
            nr_przed = self.logika.nr
            zmiana = self.odbijanie.podaj(surowa, teraz)
            if zmiana is not None:
                self.logika.ustaw_plytke(zmiana, teraz)
            self.logika.ustaw_pewnosc(self.odbijanie.pewna, teraz)
            for k in klawisze:
                self.logika.klawisz(k, teraz)
            self.logika.tick(teraz)
            self.logika.temp_c = temp
            if self.logika.zmiana != self._zmiana_pokazana or teraz - self._ostatni_obraz >= 0.1:
                klatka = self.logika.obraz(teraz)
                self._zmiana_pokazana = self.logika.zmiana
                self._ostatni_obraz = teraz
            if self.logika.nr != nr_przed:
                self.warunek.notify_all()
        if klatka is not None and klatka != self._pokazana:
            self._pokazana = None  # gdy pokaz() sie nie uda, nastepny obieg wysle klatke ponownie
            self.sprzet.pokaz(klatka)
            self._pokazana = klatka

    def _awaria(self, teraz) -> None:
        """Awaria w petli: stan logiki jak po DELETE + blad_sprzetu, klatka awaryjna (bez gniazd),
        a gdy matryca tez zawodzi - wygaszenie calej matrycy. Brak "ostatniej klatki"."""
        klatka = obraz.Klatka()
        self._awaria_t = teraz
        with self.warunek:
            try:
                self.logika.awaria_sprzetu(teraz)
                klatka = self.logika.obraz(teraz)
            except Exception:  # noqa: BLE001
                log.exception("blad logiki przy awarii - matryca czarna")
            self.odbijanie = self._nowe_odbijanie()  # plytka od nowa po powrocie sprzetu
            self._zmiana_pokazana = -1
            self._ostatni_obraz = float("-inf")
            self.warunek.notify_all()
        self._pokazana = None
        try:
            self.sprzet.pokaz(klatka)
            self._pokazana = klatka
        except Exception:  # noqa: BLE001
            log.exception("matryca nie przyjela klatki awaryjnej - wygaszenie")
            try:
                self.sprzet.wygas()
            except Exception:  # noqa: BLE001
                log.exception("wygaszenie matrycy nie powiodlo sie")

    def _petla(self) -> None:
        while not self._stop.is_set():
            try:
                if not self.krok():
                    self._stop.wait(0.5)
            except Exception:  # noqa: BLE001 - ostatnia ochrona petli
                log.exception("blad w petli sprzetu")
                self._stop.wait(0.5)
            self._budzik.wait(self.konf.okres_s)
            self._budzik.clear()

    def _po_zmianie(self) -> None:
        self.warunek.notify_all()
        self._budzik.set()

    # ------------------------------------------------------------ obsluga zadan (serwer)

    def stan(self, laptop) -> dict:
        with self.warunek:
            teraz = self.zegar()
            nr = self.logika.nr
            self.logika.tick(teraz)  # D1: uplyw czasu przed kontaktem
            self.logika.kontakt(laptop, teraz)
            if self.logika.nr != nr:
                self._po_zmianie()
            return self.logika.stan(teraz)

    def zdarzenia(self, laptop, od: int, czekaj: float, limit: int, start_id) -> dict:
        with self.warunek:
            teraz = self.zegar()
            nr = self.logika.nr
            self.logika.tick(teraz)
            # D1: kontakt tylko na poczatku zadania (klient, ktory zniknal w trakcie czekania, nie
            # przedluza waznosci planu)
            self.logika.kontakt(laptop, teraz)
            if self.logika.nr != nr:
                self._po_zmianie()
            restart = start_id is not None and start_id != self.logika.start_id
            if restart:
                od = 0
            czekaj = min(czekaj, protokol.CZEKAJ_MAX_S, self.logika.limit_odpytywania())
            koniec = teraz + czekaj
            # czeka tylko, gdy kursor laptopa jest aktualny i nie ma nic nowego (od > nr: odpowiedz od razu)
            while self.logika.nr == od and not self.zamykanie:
                pozostalo = koniec - self.zegar()
                if pozostalo <= 0:
                    break
                self.warunek.wait(pozostalo)
            zd, utracone = self.logika.zdarzenia_od(od, limit)
            # D2: jawny zakres numerow wypchnietych z dziennika (zamiast cichej luki)
            return {"protokol": protokol.PROTOKOL, "start_id": self.logika.start_id, "restart": restart,
                    "od": od, "zdarzenia": zd, "nr_zdarzenia": self.logika.nr,
                    "najstarsze_zdarzenie": self.logika.najstarsze_zdarzenie(), "utracone": utracone,
                    "utracone_od": od + 1 if utracone else None, "utracone_do": od + utracone if utracone else None}

    def plan(self, laptop, dane, t_odbioru=None) -> dict:
        with self.warunek:
            try:
                return self.logika.przyjmij_plan(dane, laptop, self.zegar(), t_odbioru=t_odbioru)
            finally:
                self._po_zmianie()

    def odrzucenie(self, laptop, blad) -> None:
        """Serwer odrzucil polecenie (zly JSON, 411, 413, zly parametr, 404 / 405, 500) - P5, D-N6.
        Blad juz rozpatrzony przez logike (`obsluzony`) nie gasi drugi raz."""
        with self.warunek:
            try:
                self.logika.odrzucenie(laptop, blad, self.zegar())
            finally:
                self._po_zmianie()

    def usun_plan(self, laptop, plan_id) -> dict:
        with self.warunek:
            try:
                return self.logika.usun_plan(laptop, self.zegar(), plan_id=plan_id)
            finally:
                self._po_zmianie()

    def tryb(self, laptop, dane) -> dict:
        with self.warunek:
            try:
                return self.logika.ustaw_tryb(dane, laptop, self.zegar())
            finally:
                self._po_zmianie()

    # ------------------------------------------------------------ sterowanie atrapa (tylko testy)

    def atrapa_klatka(self) -> dict:
        k = self._pokazana
        return {"protokol": protokol.PROTOKOL, "szerokosc": 64, "wysokosc": 64,
                "piksele_hex": k.do_hex() if k is not None else "00" * (64 * 64 * 3)}

    def atrapa_plytka(self, dane) -> dict:
        if not isinstance(dane, dict) or set(dane) != {"plytka"} or dane["plytka"] not in range(8) \
                or isinstance(dane["plytka"], bool):
            raise BladProtokolu(400, "zle_pole", "atrapa: {\"plytka\": 0..7}")
        self.sprzet.poloz_plytke(dane["plytka"])
        self._budzik.set()
        return {"protokol": protokol.PROTOKOL, "wynik": "przyjety"}

    def atrapa_klawisz(self, dane) -> dict:
        if not isinstance(dane, dict) or set(dane) != {"klawisz"} or dane["klawisz"] not in protokol.KLAWISZE:
            raise BladProtokolu(400, "zle_pole", "atrapa: {\"klawisz\": nazwa}")
        self.sprzet.nacisnij(dane["klawisz"])
        self._budzik.set()
        return {"protokol": protokol.PROTOKOL, "wynik": "przyjety"}

    # ------------------------------------------------------------ start i stop

    def uruchom(self):
        """Startuje serwer i petle sprzetu; zwraca (host, port) - port 0 = losowy wolny."""
        from .serwer import SerwerRamki

        self.serwer = SerwerRamki((self.konf.host, self.konf.port), self)
        self._watek_serwera = threading.Thread(target=self.serwer.serve_forever, kwargs={"poll_interval": 0.1},
                                               name="ramka-serwer", daemon=True)
        self._watek = threading.Thread(target=self._petla, name="ramka-petla", daemon=True)
        self._watek.start()
        self._watek_serwera.start()
        host, port = self.serwer.server_address[:2]
        log.info("ramka %s (program %s) slucha na %s:%d, start_id %s, sprzet %s", self.konf.rola, WERSJA,
                 host, port, self.logika.start_id, self.konf.sprzet)
        return host, port

    def zatrzymaj(self) -> None:
        self._stop.set()
        self._budzik.set()
        with self.warunek:
            self.zamykanie = True
            self.warunek.notify_all()
        if self.serwer is not None:
            self.serwer.shutdown()
            self.serwer.server_close()
        for w in (self._watek, self._watek_serwera):
            if w is not None:
                w.join(5)
        try:
            self.sprzet.zamknij()
        except Exception:  # noqa: BLE001
            log.exception("blad przy zamykaniu sprzetu")


def parsuj_argumenty(argv=None):
    p = argparse.ArgumentParser(prog="python -m ramka", description="Program ramki swietlnej (W albo P).")
    p.add_argument("--rola", choices=("W", "P"), help="W = wieczorna, P = poranna")
    p.add_argument("--sprzet", choices=("atrapa", "rpi"), help="domyslnie atrapa")
    p.add_argument("--host", help="adres nasluchu (domyslnie 127.0.0.1; adres w sieci - w pliku konfiguracji)")
    p.add_argument("--port", type=int, help="port (domyslnie 8765)")
    p.add_argument("--konfiguracja", help="lokalny plik JSON z ustawieniami ramki (host, klucz) - poza repo")
    p.add_argument("--sterowanie-atrapy", action="store_true", help="zasoby /atrapa/* (tylko atrapa)")
    p.add_argument("--gadatliwie", action="store_true", help="logi DEBUG")
    return p.parse_args(argv)


def konfiguracja_z_argumentow(a) -> Konfiguracja:
    """Konfiguracja z pliku i wiersza polecen. Adres nasluchu: --host, potem "host" z pliku, inaczej
    127.0.0.1 (takze dla sprzetu rpi - P6: ramka nie slucha w sieci, jesli konfiguracja tego nie mowi)."""
    konf = wczytaj_konfiguracje(a.konfiguracja) if a.konfiguracja else Konfiguracja()
    if a.rola:
        konf.rola = a.rola
    if a.sprzet:
        konf.sprzet = a.sprzet
    if a.port is not None:
        konf.port = a.port
    if a.host:
        konf.host = a.host
    if a.sterowanie_atrapy:
        if konf.sprzet != "atrapa":
            raise SystemExit("--sterowanie-atrapy tylko z --sprzet atrapa")
        konf.sterowanie_atrapy = True
    return konf


def main(argv=None) -> int:
    a = parsuj_argumenty(argv)
    logging.basicConfig(level=logging.DEBUG if a.gadatliwie else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    konf = konfiguracja_z_argumentow(a)
    if konf.sprzet == "rpi" and konf.host in ("127.0.0.1", "localhost"):
        log.warning("ramka slucha tylko na %s - adres w sieci ustaw jako \"host\" w pliku konfiguracji", konf.host)
    if not konf.klucz and konf.host not in ("127.0.0.1", "localhost"):
        log.warning("brak klucza (X-Ramka-Klucz): uzywac tylko w sieci, w ktorej sa wylacznie laptop i ramki")
    try:
        program = ProgramRamki(konf)
    except BladSprzetu as e:
        log.error("sprzet niedostepny: %s", e)
        return 2
    koniec = threading.Event()

    def zatrzymaj(*_):
        koniec.set()

    signal.signal(signal.SIGINT, zatrzymaj)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, zatrzymaj)
    program.uruchom()
    try:
        while not koniec.wait(0.5):
            pass
    finally:
        program.zatrzymaj()
    return 0
