"""indicate - klient ramek swietlnych po stronie laptopa (E3-A8, czesc "indicate").

Ramka (program `ramka/`, atrapa `narzedzia/atrapa_ramki.py`) jest serwerem HTTP + JSON w sieci lokalnej; laptop ja
odpytuje (DW8). Kontrakt: `ramka/README.md`, "Protokol v1" i "Wymagania dla strony laptopa" (pkt 1-11). Budowa
i walidacja komunikatow: `ramka_protokol.py`. API dla programu (A12): `opisy_modulow/indicate.md`.

Jeden `KlientRamki` = jedna ramka (W albo P), dwa watki:
- odpytywanie: `GET /stan` przy pierwszym kontakcie (i po utracie zdarzen z dziennika ramki), potem w petli
  `GET /zdarzenia?od=<nr>&czekaj=<s>&start_id=<id>`; kursor (start_id, nr) przesuwany tylko po udanej odpowiedzi, wiec
  w jednym uruchomieniu kazde zdarzenie trafia do programu dokladnie raz i w kolejnosci - takze po zerwanej sieci
  i zgubionej odpowiedzi; po restarcie programu wraca historia biezacego startu ramki (`z_historii`), duplikaty usuwa
  program po `klucz_zdarzenia` = (start_id, nr); restart ramki (inny start_id) = kursor od zera, rano plan ponownie;
- polecenia: JEDNA szeregowa kolejka (`PUT /tryb`, `DELETE /plan`, `PUT /plan`); polecenie gaszace anuluje oczekujacy
  plan i ponowienie; plan budowany tuz przed wyslaniem, z `zdarzenia_do` = numer ostatniego ODEBRANEGO zdarzenia i po
  odebraniu zdarzenia wlasnego poprzedniego polecenia; klient HTTP bez automatycznych ponowien - ponowienie swiadome tylko
  po zgubionej odpowiedzi (ta sama tresc i wersja); polecenia gaszace ponawiane do skutku; po 409 `inny_laptop` plan
  dopiero po jawnym `wznow()`.
Start i stop: przy pierwszym kontakcie uruchomienia plan zastany na ramce, ktorego to uruchomienie nie ustawilo, jest
gaszony; `zatrzymaj()` (najwyzej 1 s) najpierw probuje wyslac oczekujace polecenie gaszace; watki sa daemon.
Ramka W pokazuje TYLKO wynik ostatniego skanu (Spacja / `znacznik()` / blad / zgaszenie = nowy skan, stary wynik nie
wraca; skan bez numeru albo zablokowany = ramka ciemna). Wynik ma znacznik skanu (start_id, numer ostatniego odebranego
zdarzenia, numer skanu); po odebraniu zdjecia plytki, wygasniecia planu, awarii sprzetu, utraty zdarzen albo restartu
ramki wynik nie jest juz wysylany (wymaganie 7) - takze przy ponowieniu po 409 zdarzenia_nieodebrane.
Ramka P: potwierdzenia z klawiatury stosuje sama ramka; laptop zapisuje je w swoim stanie (z `GET /stan` po starcie
i po utracie zdarzen) i wysyla nowa wersje planu tylko przy wlasnej zmianie (nowy plan z sesji, restart ramki,
`plan_wygasl`, `sprzet_dziala`, utracone zdarzenia), nigdy po zdarzeniu klawiatury.
W ruchu sieciowym tylko numery plytek, gniazd i kuwet (`ramka_protokol`); klucz ramki nie trafia do dziennika ruchu.
Tylko biblioteka standardowa (i pakiet `ramka` przez `ramka_protokol`).
"""
from __future__ import annotations

import collections
import copy
import http.client
import itertools
import json
import logging
import secrets
import socket
import threading
import time
from pathlib import Path
from typing import NamedTuple

from . import ramka_protokol as RP

log = logging.getLogger("stanowisko.indicate")

NAGLOWEK_KLUCZA = "X-Ramka-Klucz"
LIMIT_ZDARZEN = 500                 # zdarzen w jednej odpowiedzi (protokol: 1-500)
PLIK_ID_LAPTOPA = "ramki_laptop_id.txt"
PLIK_KALIBRACJI = "dane/kalibracja_ramek.json"
BLEDY_SIECI = (OSError, http.client.HTTPException)
WSTRZYMANIE_INNY_LAPTOP_S = 2.0     # ponowna proba, gdy ramke obsluguje drugi laptop
ZDARZENIA_KONCA_PLANU = ("plan_wygasl", "blad_sprzetu", "zgaszono", "plan_przyjety")
ZATRZYMANIE_S = 1.0                 # zatrzymaj(): najwyzej tyle (z proba wyslania oczekujacego polecenia gaszacego)
MAX_KOLEJKI_ZDARZEN = 10000         # zdarzenia czekajace na odbierz_zdarzenia() (nadmiar: licznik `przepelnienie`)
WYNIK_WYSLANY, WYNIK_BEZ_NUMERU, WYNIK_ZLA_PLYTKA = "wyslany", "bez_numeru", "zla_plytka"
WYNIK_BRAK_KALIBRACJI, WYNIK_NIEWAZNY = "brak_kalibracji", "niewazny"

# Komunikaty dla technika (kod `blad` w stan(); tekst ostateczny ustala okno - A12).
KOMUNIKATY = {
    "brak_polaczenia": "Brak polaczenia z ramka - sprawdz zasilanie ramki i siec stanowiska.",
    "zly_klucz": "Ramka odrzuca klucz - sprawdz [ramki] klucz w ustawieniach (ten sam co w ramce).",
    "inny_laptop": "Drugi laptop na stanowisku obsluguje te ramke - zamknij program na drugim laptopie.",
    "blad_sprzetu": "Awaria sprzetu ramki - gniazda zgaszone; ramka wroci sama, potem wyniki pojawia sie ponownie.",
    "plan_odrzucony": "Ramka odrzucila plan - gniazda zgaszone (inna wersja programu ramki?).",
    "plan_innej_ramki": "Adresy ramki wieczornej i porannej sa zamienione w ustawieniach.",
    "zla_rola": "Pod adresem tej ramki odpowiada ramka innego rodzaju - sprawdz adresy ramek w ustawieniach.",
    "zla_odpowiedz": "Ramka odpowiada niezgodnie z protokolem (inna wersja programu ramki?).",
    "polecenie_odrzucone": "Ramka odrzuca polecenie - program ponawia.",
    "brak_kalibracji": "Brak poprawnej kalibracji diod ramki - gniazda nie beda wskazywane.",
}


class Znacznik(NamedTuple):
    """Chwila skanu: start ramki, numer ostatniego zdarzenia odebranego przez laptop i numer skanu w tym uruchomieniu
    klienta (ramka W pokazuje tylko wynik OSTATNIEGO skanu - runda 2, B1)."""
    start_id: str | None
    nr: int
    skan: int = 0


def klucz_zdarzenia(z: dict) -> tuple:
    """Klucz unikalny zdarzenia ramki (start ramki, numer) - po nim program usuwa duplikaty (historia po restarcie)."""
    return (z["start_id"], z["nr"])


class _Wynik(NamedTuple):
    uklad: str
    kolory: dict
    znacznik: Znacznik


class _ZlyKlucz(Exception):
    pass


class _ZlaRola(Exception):
    pass


def _int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _rozbierz_odpowiedz(surowe: bytes) -> tuple:
    """(status, tresc) z surowej odpowiedzi HTTP. Odpowiedz urwana (bez naglowkow, tresc krotsza niz Content-Length) =
    `ConnectionError` (jak zerwana siec - zgubiona odpowiedz); zla linia statusu = `BladOdpowiedzi`."""
    glowa, sep, tresc = surowe.partition(b"\r\n\r\n")
    if not sep:
        raise ConnectionError("odpowiedz ramki urwana (bez naglowkow)")
    linie = glowa.split(b"\r\n")
    czesci = linie[0].split(b" ", 2)
    if len(czesci) < 2 or not czesci[0].startswith(b"HTTP/") or not czesci[1].isdigit():
        raise RP.BladOdpowiedzi("zla linia statusu odpowiedzi")
    dlugosc = None
    for linia in linie[1:]:
        nazwa, _, wartosc = linia.partition(b":")
        if nazwa.strip().lower() == b"content-length":
            if not wartosc.strip().isdigit():
                raise RP.BladOdpowiedzi("zly naglowek Content-Length")
            dlugosc = int(wartosc.strip())
    if dlugosc is not None:
        if len(tresc) < dlugosc:
            raise ConnectionError("odpowiedz ramki urwana (tresc krotsza niz Content-Length)")
        tresc = tresc[:dlugosc]
    return int(czesci[1]), tresc


class KlientRamki:
    """Klient jednej ramki. `rola` W (wieczorna) albo P (poranna); `host`, `port` = `[ramki]` ustawien.

    `laptop_id` - staly identyfikator programu laptopa (naglowek X-Laptop-Id, nigdy nazwa osoby); `kalibracja` - dane pliku
    kalibracji diod (None = gniazda nie beda wskazywane); `klucz` - wspolny klucz ramki (pusty = bez klucza);
    `odpytywanie_s` - najdluzsze czekanie w GET /zdarzenia (ramka i tak skraca); `wazny_s` - waznosc planu (domyslnie W 30 s,
    P 600 s); `przerwa_min_s` / `przerwa_max_s` - przerwy po bledzie sieci; `na_zdarzenie(zdarzenie)` - wolane w watku
    odpytywania dla kazdego nowego zdarzenia (to samo daje `odbierz_zdarzenia()`); `dziennik_ruchu(wpis)` - zapis ruchu
    (testy, K8; klucz zastapiony "***"); `kursor` - (start_id, nr) ostatniego zdarzenia zapisanego przez program: dostarczane
    sa tylko zdarzenia o wyzszych numerach tego startu; bez niego - cala historia biezacego startu ramki (runda 2, B3).
    Zdarzenia sprzed pierwszego kontaktu tego klienta maja `z_historii: True`; duplikaty usuwa program po `klucz_zdarzenia`."""

    def __init__(self, rola: str, host: str, port: int, *, laptop_id: str, kalibracja=None, klucz: str = "",
                 odpytywanie_s: float = 25.0, wazny_s=None, przerwa_min_s: float = 0.2, przerwa_max_s: float = 1.0,
                 limit_polaczenia_s: float = 5.0, na_zdarzenie=None, dziennik_ruchu=None, kursor=None, ostrzezenia=(),
                 zegar=time.perf_counter):
        if rola not in ("W", "P"):
            raise ValueError("rola: W albo P")
        if not (isinstance(laptop_id, str) and RP.WZOR_ID.fullmatch(laptop_id)):
            raise ValueError("laptop_id: 1-40 znakow [A-Za-z0-9._-]")
        if not isinstance(klucz, str) or (klucz and not RP.WZOR_KLUCZA.fullmatch(klucz)):
            raise ValueError("klucz: pusty albo 16-256 drukowalnych znakow ASCII bez odstepu")
        self.rola = rola
        self.host = host
        self.port = int(port)
        self.laptop_id = laptop_id
        self.kalibracja = kalibracja
        self._klucz = klucz
        self._odpytywanie_s = float(odpytywanie_s)
        self._wazny_s = float(wazny_s) if wazny_s else RP.WAZNY_S_ROLI[rola]
        self._przerwa_min = float(przerwa_min_s)
        self._przerwa_max = max(float(przerwa_max_s), self._przerwa_min)
        self._limit = float(limit_polaczenia_s)
        self._na_zdarzenie = na_zdarzenie
        self._dziennik = dziennik_ruchu
        self._kursor_programu = tuple(kursor) if kursor else None
        self._zegar = zegar
        self.przed_wyslaniem_planu = None   # hak testow: wolany tuz przed kazdym PUT /plan
        self._warunek = threading.Condition(threading.RLock())
        self._stop = threading.Event()      # nowy obiekt przy kazdym uruchom() - stary watek widzi swoj (ustawiony)
        self._stop.set()
        self._wznow = threading.Event()
        self._szybko = threading.Event()    # nastepne odpytanie bez czekania
        self._watki = []
        self._aktywne = set()               # polaczenia w toku - zamykane przy zatrzymaniu (watki sa daemon)
        self._nr_zadania = itertools.count(1)
        # stan ramki wg laptopa
        self._start_id = None
        self._kursor = 0
        self._pierwszy_kontakt = True       # pierwsza migawka tego uruchomienia klienta (B2: zastany plan gasic)
        self._prog_stanu = 0                # zdarzenia <= tego numeru sa juz w migawce GET /stan
        self._prog_dostarczenia = 0         # zdarzenia <= tego numeru nie sa dostarczane programowi
        self._prog_historii = 0             # zdarzenia <= tego numeru byly przed pierwszym kontaktem (`z_historii`)
        self._prog_utraty = 0               # utracone liczone powyzej tego numeru (pozycja programu)
        self._przepelnienie = 0             # zdarzenia odrzucone z pelnej kolejki programu
        self._potrzebna_migawka = True
        self._polaczona = False
        self._bledy_sieci = 0
        self._utracone = 0
        self._plytka = None
        self._tryb_ramki = None
        self._plan_ramki = None
        self._awaria = False
        self._blad = None
        self._kod_bledu = None
        self._ostrzezenia = list(ostrzezenia)
        if kalibracja is None:
            self._ostrzezenia.append(KOMUNIKATY["brak_kalibracji"])
        self._nr_odpytania = 0              # odpytania /zdarzenia rozpoczete
        self._odpytanie_zakonczone = 0      # numer ostatniego odpytania przetworzonego
        self._zdarzenia_wy = collections.deque(maxlen=MAX_KOLEJKI_ZDARZEN)
        # kolejka polecen
        self._gaszace = None                # najnowsze oczekujace polecenie gaszace (metoda, sciezka, tresc, tryb)
        self._gen_gaszace = 0
        self._plan_potrzebny = False
        self._cel = 0                       # licznik zmian tego, co ma byc na ramce
        self._min_kursor = None             # (start_id, nr): przed planem odebrac zdarzenia co najmniej do nr
        self._czekaj_na = None              # 409 zdarzenia_nieodebrane: (start_id, numer) - plan, gdy kursor go minie
        self._po_odmowie = False            # P-N1: po 409 zdarzenia_nieodebrane GET /stan (numer ostatniego zdarzenia)
        self._ponowienie = None             # PUT /plan bez odpowiedzi: ta sama tresc i wersja
        self._zablokowane = set()           # odciski tresci, ktorych nie wysylac (409 plan_zgaszony, odrzucone)
        self._wersje = {}                   # plan_id -> najwyzsza znana / uzyta wersja
        self._plan_przyjety = None          # (plan_id, wersja, odcisk, nr zdarzenia plan_przyjety, start_id)
        self._przyjete_wersje = set()       # (start_id, plan_id, wersja) przyjete w tym uruchomieniu (D2)
        self._wstrzymane_plany = False      # P2: po 409 inny_laptop plany dopiero po jawnym wznow()
        self._ostatni_tryb = None
        self._wstrzymanie_do = 0.0
        self._przerwa_polecen = self._przerwa_min
        self._pominiete = {}
        self._wyslane_plany = 0
        self._przyjete_plany = 0
        # ramka P
        self._rano_plan_id = None
        self._rano_baza = None
        self._rano_odcisk = None
        self._potw = {}                     # plan_id -> [[plytka, kuweta], ...] w kolejnosci potwierdzen
        self._wyb = {}                      # plan_id -> {"plytka": kuweta}
        # ramka W
        self._plan_id_w = f"{time.strftime('%Y-%m-%d')}-w-{secrets.token_hex(3)}"
        self._wyniki = {}                   # numer plytki -> _Wynik (najwyzej jeden: wynik ostatniego skanu)
        self._skan = 0                      # numer ostatniego skanu (Spacja, znacznik(), blad, zgas) - B1
        self._zdjecia = {}                  # numer plytki -> numer ostatniego zdarzenia zdjecia (biezacy start)
        self._uniewaznione_do = 0           # wyniki ze znacznikiem ponizej tego numeru sa niewazne

    # ------------------------------------------------------------------ start / stop

    @property
    def adres(self) -> tuple:
        return (self.host, self.port)

    @property
    def kursor(self) -> tuple:
        with self._warunek:
            return (self._start_id, self._kursor)

    def uruchom(self) -> None:
        """Startuje watki (daemon). Kazde uruchomienie ma wlasny sygnal stopu - watek poprzedniego uruchomienia, ktory
        jeszcze nie wyszedl z zadania sieciowego, konczy sie sam i nic juz nie zmienia."""
        with self._warunek:
            if self._watki:
                return
            stop = threading.Event()
            self._stop = stop
            self._pierwszy_kontakt = True
            self._potrzebna_migawka = True
        for nazwa, cel in (("odpytywanie", self._petla_odpytywania), ("polecenia", self._petla_polecen)):
            w = threading.Thread(target=cel, args=(stop,), name=f"indicate-{self.rola}-{nazwa}", daemon=True)
            self._watki.append(w)
            w.start()

    def zatrzymaj(self, timeout: float = ZATRZYMANIE_S) -> bool:
        """Zatrzymanie w czasie najwyzej `timeout` (domyslnie 1 s): najpierw proba wyslania oczekujacego polecenia
        gaszacego (np. `zgas()` tuz przed zamknieciem programu - B2), potem zamkniecie polaczen w toku; watki sa daemon.
        Zwraca False, gdy oczekujace zgaszenie NIE doszlo do ramki (ramka moze swiecic do konca waznosci planu - program
        moze o tym powiedziec technikowi), inaczej True."""
        koniec = time.monotonic() + timeout
        with self._warunek:
            stop = self._stop
            stop.set()
            pol = self._gaszace
            self._warunek.notify_all()
        self._wznow.set()
        self._przerwij_polaczenia()
        doszlo = [pol is None]
        if pol is not None:
            czas = min(0.6, koniec - time.monotonic() - 0.15)
            if czas > 0.05:
                # osobny watek daemon: tez rozwiazywanie nazwy hosta (np. ramka-p.local) nie przedluzy zamkniecia
                w = threading.Thread(target=self._wyslij_przy_zamykaniu, args=(pol, czas, doszlo), daemon=True,
                                     name=f"indicate-{self.rola}-zamykanie")
                w.start()
                w.join(czas + 0.1)
        self._przerwij_polaczenia()
        for w in self._watki:
            w.join(max(0.0, koniec - time.monotonic()))
        self._watki = []
        return bool(doszlo[0])

    def _wyslij_przy_zamykaniu(self, pol, czas: float, doszlo: list) -> None:
        metoda, sciezka, tresc_d, _ = pol
        try:
            st, _ = self._zadanie(metoda, sciezka, RP.koduj(tresc_d) if tresc_d is not None else None, timeout=czas,
                                  przy_zamykaniu=True)
            if st == 200:
                doszlo[0] = True
                with self._warunek:
                    if self._gaszace is pol:
                        self._gaszace = None
        except (RP.BladOdpowiedzi,) + BLEDY_SIECI:
            log.warning("ramka %s: polecenie gaszace przy zamykaniu nie doszlo", self.rola)

    def _przerwij_polaczenia(self) -> None:
        """Zamyka gniazda zadan w toku (na Windows `shutdown` nie przerywa `recv` w innym watku - gniazdo jest zamykane;
        klient nie uzywa `makefile`, wiec `close()` zamyka je od razu - bez prywatnego API)."""
        with self._warunek:
            gniazda = list(self._aktywne)
        for sock in gniazda:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                sock.close()
            except OSError:
                pass

    def wznow(self) -> None:
        """Jawna decyzja czlowieka po bledzie: 401 (zly klucz - np. po poprawieniu ustawien) albo `inny_laptop` (drugi
        laptop na stanowisku - P2). Bez tego klient nie ponawia: ani odpytywania przy zlym kluczu, ani planu po
        `inny_laptop` (polecenia gaszace ponawia zawsze - zgaszenie jest bezpieczne)."""
        with self._warunek:
            if self._blad in ("zly_klucz", "inny_laptop"):
                self._blad = None
            if self._wstrzymane_plany:
                self._wstrzymane_plany = False
                self._wstrzymanie_do = 0.0
                if self._rano_baza is not None or self._wazne_wyniki():
                    self._zlec_plan()
            self._warunek.notify_all()
        self._wznow.set()

    # ------------------------------------------------------------------ odczyt dla programu

    def stan(self) -> dict:
        with self._warunek:
            kod = self._blad or (None if self._polaczona else "brak_polaczenia")
            pid = self._rano_plan_id if self.rola == "P" else self._plan_id_w
            return {
                "rola": self.rola, "adres": self.adres, "polaczona": self._polaczona, "start_id": self._start_id,
                "kursor": self._kursor, "plytka": self._plytka, "tryb_ramki": self._tryb_ramki,
                "plan_ramki": self._plan_ramki, "plan_id": pid, "wersja": self._wersje.get(pid),
                "plan_przyjety": self._plan_przyjety is not None, "awaria": self._awaria,
                "oczekuje": self._gaszace is not None or self._plan_potrzebny, "blad": self._blad,
                "kod_bledu": self._kod_bledu, "komunikat": KOMUNIKATY.get(kod) if kod else None,
                "ostrzezenia": list(self._ostrzezenia), "potwierdzone": self._potwierdzone(),
                "wybrane": dict(self._wyb.get(self._rano_plan_id, {})), "utracone": self._utracone,
                "pominiete": copy.deepcopy(self._pominiete), "wyslane_plany": self._wyslane_plany,
                "przyjete_plany": self._przyjete_plany, "bledy_sieci": self._bledy_sieci,
                "wyniki": sorted(self._wyniki) if self.rola == "W" else [], "wstrzymane": self._wstrzymane_plany,
                "przepelnienie": self._przepelnienie,
            }

    def odbierz_zdarzenia(self) -> list:
        """Zdarzenia ramki od ostatniego wywolania, w kolejnosci: slownik zdarzenia z protokolu + `rola`, `start_id`,
        `z_historii` (True = zdarzenie sprzed pierwszego kontaktu tego uruchomienia klienta) i `nieaktualne` (True dla
        `zamknij_piec` z historii albo innego pieca niz biezacy plan klienta - NIE wykonywac, tylko dziennik; r3 B-N1).
        W jednym uruchomieniu kazde zdarzenie raz; po restarcie programu wraca historia biezacego startu ramki (powyzej
        `kursor`, jesli podany) - WYMAGANIE dla programu: zapis kazdego zdarzenia z kluczem unikalnym `klucz_zdarzenia(z)`."""
        with self._warunek:
            wynik = list(self._zdarzenia_wy)
            self._zdarzenia_wy.clear()
        return wynik

    def czekaj(self, warunek, timeout: float = 5.0) -> bool:
        """Czeka, az warunek(stan()) bedzie prawdziwy."""
        koniec = time.monotonic() + timeout
        with self._warunek:
            while True:
                if warunek(self.stan()):
                    return True
                pozostalo = koniec - time.monotonic()
                if pozostalo <= 0:
                    return False
                self._warunek.wait(min(pozostalo, 0.05))

    def potwierdzone(self) -> list:
        with self._warunek:
            return self._potwierdzone()

    def _potwierdzone(self) -> list:
        return [list(x) for x in self._potw.get(self._rano_plan_id, [])]

    def znacznik(self) -> Znacznik:
        """Ramka W: NOWY SKAN rozpoczety bez Spacji - dziala jak `skanowanie()` (P-N2: ramka gasi poprzedni wynik od razu,
        `PUT /tryb skanowanie`); to nie jest odczyt bez skutku. Ramka P: znacznik chwili (start ramki, kursor) bez skutku."""
        if self.rola == "W":
            return self.skanowanie()
        with self._warunek:
            return Znacznik(self._start_id, self._kursor, self._skan)

    def _nowy_skan(self) -> None:
        """Ramka W pokazuje tylko wynik ostatniego skanu (B1): nowy skan (albo blad / zgaszenie) uniewaznia poprzednie."""
        self._skan += 1
        self._wyniki.clear()

    # ------------------------------------------------------------------ polecenia: ramka P (rano)

    def ustaw_plan_rano(self, plan_plytek: dict, *, potwierdzone=None, wybrane=None) -> dict:
        """Plan sesji pieca z `SesjaRano.plan_plytek(...)` do ramki porannej. Nowy `plan_id` (nowy piec) = najpierw
        `DELETE /plan`. Ta sama tresc = nic nie wysyla. `potwierdzone` / `wybrane` - stan potwierdzen podany przez program
        (domyslnie stan laptopa: zdarzenia klawiatury i `GET /stan`). Zwraca `pominiete` (plytki i gniazda, ktore nie
        pojda do ramki: spoza rodziny P, bez kalibracji, kuwety odrzucone)."""
        if self.rola != "P":
            raise ValueError("ustaw_plan_rano: tylko ramka poranna (P)")
        if not isinstance(plan_plytek, dict):
            raise ValueError("ustaw_plan_rano: oczekiwano wyniku SesjaRano.plan_plytek")
        pid = plan_plytek.get("plan_id")
        if not (isinstance(pid, str) and RP.WZOR_ID.fullmatch(pid)):
            raise RP.BladProtokolu("zly_plan_id", "plan_id: [A-Za-z0-9._-]{1,40}")
        baza = {k: copy.deepcopy(plan_plytek.get(k)) for k in RP.POLA_PLANU_PLYTEK}
        odcisk = RP.odcisk(baza)
        with self._warunek:
            nowy = pid != self._rano_plan_id
            if nowy:
                if self._rano_plan_id is not None or self._plan_ramki not in (None, pid):
                    self._zlec_gaszace("DELETE", "/plan", None, None)   # nowy wsad pieca: najpierw zgas (D-N12)
                self._rano_plan_id = pid
                self._potw.setdefault(pid, [])
                self._wyb.setdefault(pid, {})
            if potwierdzone is not None:
                self._potw[pid] = [[int(p), k] for p, k in potwierdzone]
            if wybrane is not None:
                self._wyb[pid] = {str(p): k for p, k in wybrane.items()}
            if nowy or odcisk != self._rano_odcisk or potwierdzone is not None or wybrane is not None:
                self._rano_baza = baza
                self._rano_odcisk = odcisk
                self._zlec_plan()
            try:
                _, pom = RP.plan_rano(baza, self.kalibracja, wersja=0, start_id="0000", zdarzenia_do=0,
                                      potwierdzone=self._potw[pid], wybrane=self._wyb[pid])
            except RP.BladProtokolu:
                pom = {}
            self._pominiete = pom
            return copy.deepcopy(pom)

    def zgas(self) -> None:
        """`DELETE /plan`: zgas ramke (rano: "Zamknij piec" przyjete przez sesje, skan zablokowany wieczorem). Rano plan
        przestaje obowiazywac - pokazuje go dopiero kolejne `ustaw_plan_rano`."""
        with self._warunek:
            self._zlec_gaszace("DELETE", "/plan", None, None)
            if self.rola == "P":
                self._rano_baza = None
                self._rano_odcisk = None
            else:
                self._nowy_skan()

    # ------------------------------------------------------------------ polecenia: tryb i ramka W (wieczor)

    def tryb(self, stan: str) -> Znacznik:
        """`PUT /tryb` (gotowa, skanowanie, analiza, blad, test_led) - kazdy usuwa plan z ramki. Zwraca znacznik chwili
        polecenia (dla wyniku skanu). Rano plan przestaje obowiazywac (jak `zgas`). Ramka W: kazdy stan poza "analiza"
        zaczyna nowy skan - poprzedni wynik nie wroci (B1); "analiza" nalezy do biezacego skanu."""
        tresc = RP.tresc_trybu(stan)
        with self._warunek:
            if self.rola == "W" and (stan != "analiza" or self._ostatni_tryb != "skanowanie"):
                self._nowy_skan()   # "analiza" bez poprzedzajacej Spacji / znacznik() tez zaczyna nowy skan (r2 P-N2)
            z = Znacznik(self._start_id, self._kursor, self._skan)
            self._zlec_gaszace("PUT", "/tryb", tresc, stan)
            if self.rola == "P":
                self._rano_baza = None
                self._rano_odcisk = None
            return z

    def skanowanie(self) -> Znacznik:
        """Spacja: ramka W w stan "skanowanie"; poprzednie wyniki skasowane (ramka pokazuje tylko ostatni skan).
        Znacznik przekazac do `wynik` tego skanu."""
        return self.tryb("skanowanie")

    def analiza(self) -> Znacznik:
        return self.tryb("analiza")

    def blad(self) -> Znacznik:
        """Skan zablokowany / nieprzyjety / blad analizy: ramka w stan "blad" (gniazda ciemne, poprzedni wynik nie wroci)."""
        return self.tryb("blad")

    def wynik(self, numer_plytki, uklad: str, kolory: dict, znacznik: Znacznik) -> str:
        """Wynik OSTATNIEGO skanu plytki wieczornej: `kolory` = {gniazdo: kolor ramki albo None} (`ramka_protokol.
        kolor_ramki` ze statusu gniazda), `znacznik` z `skanowanie()` tego skanu (albo `znacznik()` z chwili skanu bez
        Spacji). Ramka W pokazuje tylko ten jeden wynik (B1). Zwraca "wyslany" (zlecony) albo powod, dla ktorego nie:
        "bez_numeru", "zla_plytka", "brak_kalibracji" - ramka ciemna; "niewazny" - po znaczniku byl nowszy skan, zdjecie tej
        plytki, wygasniecie planu, awaria, utrata zdarzen albo restart ramki (pokazac moze juz tylko NOWY skan)."""
        if self.rola != "W":
            raise ValueError("wynik: tylko ramka wieczorna (W)")
        if not isinstance(znacznik, Znacznik):
            raise TypeError("znacznik: wynik skanowanie() albo znacznik()")
        with self._warunek:
            powod = self._sprawdz_wynik(numer_plytki, uklad, kolory, znacznik)
            if powod == WYNIK_WYSLANY:
                self._wyniki = {numer_plytki: _Wynik(uklad, {int(g): c for g, c in kolory.items()}, znacznik)}
                self._zlec_plan()
            elif znacznik.skan == self._skan:
                # biezacy skan nie da sie pokazac (bez numeru, zablokowany, niewazny): ramka ciemna, nic starego nie wraca
                self._wyniki.clear()
                if (self._plan_przyjety is not None or self._plan_potrzebny
                        or self._ostatni_tryb in ("skanowanie", "analiza")):
                    self._zlec_gaszace("PUT", "/tryb", RP.tresc_trybu("gotowa"), "gotowa")
            return powod

    def _sprawdz_wynik(self, numer, uklad, kolory, znacznik) -> str:
        if numer is None:
            return WYNIK_BEZ_NUMERU
        if not _int(numer) or numer not in RP.RODZINY["W"]:
            return WYNIK_ZLA_PLYTKA
        kal = self.kalibracja
        gn = (kal or {}).get("ramki", {}).get("W", {}).get(uklad, {}).get("gniazda") if isinstance(uklad, str) else None
        if not gn or not isinstance(kolory, dict):
            return WYNIK_BRAK_KALIBRACJI
        for g, c in kolory.items():
            if isinstance(g, bool) or not (_int(g) or (isinstance(g, str) and g.isascii() and g.isdigit())):
                return WYNIK_BRAK_KALIBRACJI    # D13: klucz gniazda nie-liczba
            if c is not None and str(int(g)) not in gn:
                return WYNIK_BRAK_KALIBRACJI
        if not self._wynik_wazny(numer, znacznik):
            return WYNIK_NIEWAZNY
        return WYNIK_WYSLANY

    def _wynik_wazny(self, numer: int, z: Znacznik) -> bool:
        return (z.start_id is not None and z.start_id == self._start_id and z.skan == self._skan
                and z.nr >= self._uniewaznione_do and z.nr >= self._zdjecia.get(numer, 0))

    def _wazne_wyniki(self) -> dict:
        return {n: w for n, w in self._wyniki.items() if self._wynik_wazny(n, w.znacznik)}

    # ------------------------------------------------------------------ kolejka polecen (pod blokada)

    def _zlec_gaszace(self, metoda, sciezka, tresc, tryb) -> None:
        """Polecenie gaszace zastepuje oczekujace polecenia i anuluje oczekujacy plan i ponowienie (wymaganie 3)."""
        self._gaszace = (metoda, sciezka, tresc, tryb)
        self._gen_gaszace += 1
        self._plan_potrzebny = False
        self._ponowienie = None
        self._plan_przyjety = None
        self._ostatni_tryb = tryb
        self._wstrzymanie_do = 0.0
        self._warunek.notify_all()

    def _zlec_plan(self) -> None:
        self._plan_potrzebny = True
        self._cel += 1
        if self._blad == "plan_odrzucony":
            self._blad = None
        self._warunek.notify_all()

    # ------------------------------------------------------------------ HTTP

    def _zapisz(self, kierunek, nr, metoda, sciezka, status=None, naglowki=None, tresc=None, blad=None) -> None:
        if self._dziennik is None:
            return
        wpis = {"nr": nr, "kierunek": kierunek, "metoda": metoda, "sciezka": sciezka, "rola": self.rola,
                "t": round(time.monotonic(), 4)}
        if status is not None:
            wpis["status"] = status
        if naglowki is not None:
            wpis["naglowki"] = {k: ("***" if k == NAGLOWEK_KLUCZA else v) for k, v in naglowki.items()}
        if tresc is not None:
            wpis["tresc"] = bytes(tresc)
        if blad is not None:
            wpis["blad"] = blad
        try:
            self._dziennik(wpis)
        except Exception:  # noqa: BLE001 - dziennik testow nie moze zatrzymac klienta
            log.exception("dziennik ruchu")

    def _zadanie(self, metoda: str, sciezka: str, tresc: bytes | None = None, timeout: float | None = None,
                 przy_zamykaniu: bool = False, stop=None):
        """Jedno zadanie HTTP (nowe polaczenie, `Connection: close`, bez zadnych ponowien). Zwraca (status, JSON albo None).
        `stop` - sygnal uruchomienia watku (zatrzymany = brak zadania); `przy_zamykaniu` - polecenie gaszace z `zatrzymaj()`.
        Klient HTTP na zwyklym gniezdzie (bez `makefile`): `zatrzymaj()` zamyka gniazdo w toku od razu (P1, bez prywatnego
        API - recenzja r2 D-N2). Odpowiedz ramki: HTTP/1.0, `Content-Length`, zamkniecie polaczenia po odpowiedzi."""
        nr = next(self._nr_zadania)
        naglowki = {"Host": f"{self.host}:{self.port}", "X-Laptop-Id": self.laptop_id, "Connection": "close"}
        if self._klucz:
            naglowki[NAGLOWEK_KLUCZA] = self._klucz
        if tresc is not None:
            naglowki["Content-Type"] = "application/json"
            naglowki["Content-Length"] = str(len(tresc))
        self._zapisz("do_ramki", nr, metoda, sciezka, naglowki=naglowki, tresc=tresc)
        zatrzymany = stop if stop is not None else self._stop
        with self._warunek:
            if not przy_zamykaniu and zatrzymany.is_set():
                raise OSError("klient zatrzymany")
        sock = None
        try:
            sock = socket.create_connection((self.host, self.port), timeout=timeout or self._limit)
            with self._warunek:
                if not przy_zamykaniu and zatrzymany.is_set():
                    raise OSError("klient zatrzymany")
                self._aktywne.add(sock)
            glowa = f"{metoda} {sciezka} HTTP/1.1\r\n" + "".join(f"{k}: {v}\r\n" for k, v in naglowki.items()) + "\r\n"
            sock.sendall(glowa.encode("ascii") + (tresc or b""))
            surowe = bytearray()
            while True:
                b = sock.recv(65536)
                if not b:
                    break
                surowe += b
                if len(surowe) > RP.MAX_ODPOWIEDZI + 65536:
                    raise RP.BladOdpowiedzi("odpowiedz za duza")
            status, dane = _rozbierz_odpowiedz(bytes(surowe))
        except Exception as e:
            self._zapisz("blad", nr, metoda, sciezka, blad=type(e).__name__)
            raise
        finally:
            if sock is not None:
                with self._warunek:
                    self._aktywne.discard(sock)
                sock.close()
        self._zapisz("z_ramki", nr, metoda, sciezka, status=status, tresc=dane)
        if len(dane) > RP.MAX_ODPOWIEDZI:
            raise RP.BladOdpowiedzi("odpowiedz za duza")
        if not dane:
            return status, None
        try:
            return status, json.loads(dane.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            raise RP.BladOdpowiedzi("odpowiedz nie jest JSON") from None

    # ------------------------------------------------------------------ watek odpytywania

    def _petla_odpytywania(self, stop: threading.Event) -> None:
        przerwa = self._przerwa_min
        while not stop.is_set():
            with self._warunek:
                zly_klucz = self._blad == "zly_klucz"
            if zly_klucz:
                if self._wznow.wait(0.5):
                    self._wznow.clear()
                continue
            try:
                if self._potrzebna_migawka:
                    self._migawka(stop)
                wywolaj = self._odpytaj(stop)
                przerwa = self._przerwa_min
                for z in wywolaj:
                    self._wywolaj(z)
                continue
            except _ZlyKlucz:
                continue
            except _ZlaRola:
                stop.wait(self._przerwa_max * 5)
                continue
            except RP.BladOdpowiedzi:
                with self._warunek:
                    if not stop.is_set():
                        self._blad = "zla_odpowiedz"
                        self._polaczona = False
                        self._bledy_sieci += 1
                        self._warunek.notify_all()
            except BLEDY_SIECI:
                with self._warunek:
                    if not stop.is_set():
                        self._polaczona = False
                        self._bledy_sieci += 1
                        self._warunek.notify_all()
            if stop.wait(przerwa):
                break
            przerwa = min(przerwa * 2, self._przerwa_max)

    def _wywolaj(self, z: dict) -> None:
        if self._na_zdarzenie is None:
            return
        try:
            self._na_zdarzenie(dict(z))
        except Exception:  # noqa: BLE001 - blad programu nie zatrzymuje odbioru zdarzen
            log.exception("na_zdarzenie")

    def _ustaw_zly_klucz(self) -> None:
        with self._warunek:
            self._blad = "zly_klucz"
            self._polaczona = False
            self._wznow.clear()
            self._warunek.notify_all()
        log.error("ramka %s: 401 - zly klucz ramki w ustawieniach (klient nie ponawia do wznow())", self.rola)

    def _migawka(self, stop: threading.Event) -> None:
        st, d = self._zadanie("GET", "/stan", stop=stop)
        if st == 401:
            self._ustaw_zly_klucz()
            raise _ZlyKlucz()
        if st != 200:
            raise RP.BladOdpowiedzi(f"GET /stan: status {st}")
        d = RP.sprawdz_stan(d)
        with self._warunek:
            if stop.is_set():
                return
            if d["rola"] != self.rola:
                self._blad = "zla_rola"
                self._polaczona = False
                self._warunek.notify_all()
                raise _ZlaRola()
            self._zastosuj_migawke(d)

    def _zastosuj_migawke(self, d: dict) -> None:
        sid, n = d["start_id"], d["nr_zdarzenia"]
        if sid != self._start_id:
            pierwszy = self._start_id is None
            self._nowy_start(sid)
            if pierwszy:
                # B3: bez kursora programu - cala historia biezacego startu ramki (oznaczona z_historii); z kursorem -
                # tylko zdarzenia powyzej niego. Duplikaty usuwa program po klucz_zdarzenia (start_id, nr).
                kp = self._kursor_programu
                znany = kp is not None and kp[0] == sid
                self._prog_dostarczenia = int(kp[1]) if znany else 0
                self._prog_utraty = int(kp[1]) if znany else n
                self._prog_historii = n
        self._prog_stanu = max(self._prog_stanu, n)
        self._plytka = d.get("plytka")
        self._tryb_ramki = d.get("tryb")
        self._plan_ramki = d.get("plan_id")
        self._awaria = bool(d.get("blad_sprzetu"))
        pid = d.get("plan_id")
        if pid:
            if _int(d.get("plan_wersja")):
                self._wersje[pid] = max(self._wersje.get(pid, 0), d["plan_wersja"])
            if self.rola == "P":
                self._potw[pid] = [[int(p), k] for p, k in d.get("potwierdzone", [])]
                self._wyb[pid] = {str(p): k for p, k in d.get("wybrane", {}).items()}
        if self._pierwszy_kontakt:
            self._pierwszy_kontakt = False
            self._zgas_zastany_plan(d.get("plan_id"))
        self._potrzebna_migawka = False
        self._polaczona = True
        if self._blad in ("zla_odpowiedz", "zla_rola"):
            self._blad = None
        self._warunek.notify_all()

    def _zgas_zastany_plan(self, plan_ramki) -> None:
        """B2: pierwszy kontakt w tym uruchomieniu - plan na ramce, ktorego to uruchomienie nie ustawilo (poprzednie
        uruchomienie programu z tym samym X-Laptop-Id podtrzymywaloby go bez konca), jest gaszony. Rano ten sam piec podany
        przez program idzie ponownie z potwierdzeniami z migawki; wieczorem wynik sprzed restartu programu nie wraca."""
        if plan_ramki is None or self._gaszace is not None:
            return
        if self.rola == "P":
            if plan_ramki == self._rano_plan_id:
                return
            log.warning("ramka P: plan zastany na ramce (nie z tego uruchomienia) - gaszony")
            self._zlec_gaszace("DELETE", "/plan", None, None)
            if self._rano_baza is not None:
                self._zlec_plan()
        else:
            log.warning("ramka W: plan zastany na ramce (nie z tego uruchomienia) - gaszony")
            self._zlec_gaszace("PUT", "/tryb", RP.tresc_trybu("gotowa"), "gotowa")

    def _odpytaj(self, stop: threading.Event) -> list:
        with self._warunek:
            sid, od = self._start_id, self._kursor
            self._nr_odpytania += 1
            nr_odp = self._nr_odpytania
        czekaj = 0.0 if self._szybko.is_set() else self._odpytywanie_s
        self._szybko.clear()
        st, d = self._zadanie("GET", f"/zdarzenia?od={od}&czekaj={czekaj:g}&limit={LIMIT_ZDARZEN}&start_id={sid}",
                              timeout=czekaj + self._limit, stop=stop)
        if st == 401:
            self._ustaw_zly_klucz()
            raise _ZlyKlucz()
        if st != 200:
            raise RP.BladOdpowiedzi(f"GET /zdarzenia: status {st}")
        d = RP.sprawdz_zdarzenia(d)
        with self._warunek:
            if stop.is_set() or (self._start_id, self._kursor) != (sid, od):
                return []   # zatrzymany albo stan zmienil sie w miedzyczasie - odpowiedz pomijana, kursor bez zmian
            return self._przetworz(d, nr_odp)

    def _przetworz(self, d: dict, nr_odp: int) -> list:
        """Odpowiedz /zdarzenia (pod blokada): restart, utracone, zdarzenia > kursor - stan i dostarczenie programowi."""
        if d["restart"] or d["start_id"] != self._start_id:
            self._nowy_start(d["start_id"])
            log.warning("ramka %s wystartowala ponownie (start %s)", self.rola, d["start_id"])
        utracone = d.get("utracone") or 0
        utracone_do = d.get("utracone_do") or 0
        if utracone and utracone_do > self._prog_utraty:
            self._utracone += utracone       # D7: liczone wzgledem pozycji programu (kursor programu albo migawka)
        if utracone and utracone_do > self._prog_stanu:
            log.warning("ramka %s: %d zdarzen wypchnietych z dziennika ramki przed odebraniem", self.rola, utracone)
            if self.rola == "W":
                self._uniewaznione_do = max(self._uniewaznione_do, d.get("utracone_do") or 0)
                self._wyniki = self._wazne_wyniki()
            else:
                self._potrzebna_migawka = True      # stan potwierdzen z GET /stan, potem nowa wersja planu
                self._zablokowane.clear()
                if self._rano_baza is not None:
                    self._zlec_plan()
        nowe = []
        for z in d["zdarzenia"]:
            nr = z["nr"]
            if nr <= self._kursor:
                continue
            self._zastosuj(z, nr > self._prog_stanu)
            self._kursor = nr
            if nr > self._prog_dostarczenia:
                wy = dict(z)
                wy["rola"] = self.rola
                wy["start_id"] = self._start_id
                wy["z_historii"] = nr <= self._prog_historii
                # B-N1: "Zamknij piec" z historii albo innego pieca niz biezacy plan klienta - tylko do dziennika,
                # nie jako polecenie (spoznione zdarzenie nie zamyka nastepnego pieca)
                wy["nieaktualne"] = z["typ"] == "zamknij_piec" and (wy["z_historii"]
                                                                    or z.get("plan_id") != self._rano_plan_id)
                if len(self._zdarzenia_wy) == self._zdarzenia_wy.maxlen:
                    self._przepelnienie += 1     # D8: program nie odbiera (tylko na_zdarzenie) - najstarsze odpada
                self._zdarzenia_wy.append(wy)
                nowe.append(wy)
        self._polaczona = True
        if self._blad == "zla_odpowiedz":
            self._blad = None
        self._odpytanie_zakonczone = nr_odp
        self._warunek.notify_all()
        return nowe

    def _nowy_start(self, sid: str) -> None:
        """Nowy start ramki (pierwszy kontakt albo restart): kursor od zera, plan w RAM ramki zniknal."""
        restart = self._start_id is not None
        self._start_id = sid
        self._kursor = 0
        self._prog_stanu = 0
        self._prog_dostarczenia = 0
        self._prog_historii = 0
        self._prog_utraty = 0
        self._min_kursor = None
        self._czekaj_na = None
        self._ponowienie = None
        self._plan_ramki = None
        self._plan_przyjety = None
        self._awaria = False
        self._plytka = None
        self._tryb_ramki = "gotowa"
        self._zablokowane.clear()
        self._przyjete_wersje.clear()
        self._zdjecia.clear()
        self._uniewaznione_do = 0
        if not restart:
            return
        if self.rola == "W":
            self._wyniki.clear()        # wyniki sprzed restartu ramki nie wracaja (wymaganie 7 / 10)
            if self._gaszace is None and self._ostatni_tryb in ("skanowanie", "analiza", "blad"):
                self._gaszace = ("PUT", "/tryb", RP.tresc_trybu(self._ostatni_tryb), self._ostatni_tryb)
                self._gen_gaszace += 1
        elif self._rano_baza is not None:
            self._zlec_plan()           # rano: plan ponownie z nowym start_id i potwierdzeniami laptopa

    def _zastosuj(self, z: dict, stan: bool) -> None:
        """Jedno zdarzenie (pod blokada). `stan` False = zdarzenie juz zawarte w migawce GET /stan."""
        typ, nr = z["typ"], z["nr"]
        pp = self._plan_przyjety
        if typ in ZDARZENIA_KONCA_PLANU and pp is not None and nr > pp[3]:
            self._plan_przyjety = None   # zgaszony albo zastapiony po przyjeciu (zdarzenie pozniejsze niz przyjecie)
        if typ == "plan_przyjety":
            pid = z["plan_id"]
            self._wersje[pid] = max(self._wersje.get(pid, 0), z["wersja"])
            if stan:
                self._plan_ramki = pid
                self._tryb_ramki = "wynik"
            return
        if typ == "plytka" and self.rola == "W" and z["poprzednia"] > 0:
            p = z["poprzednia"]
            self._zdjecia[p] = max(self._zdjecia.get(p, 0), nr)   # wynik plytki p sprzed tego numeru - niewazny
            w = self._wyniki.get(p)
            if w is not None and not self._wynik_wazny(p, w.znacznik):
                del self._wyniki[p]
        if not stan:
            return
        if typ == "plytka":
            self._plytka = z["plytka"]
        elif typ in RP.ZDARZENIA_KUWET and self.rola == "P":
            self._zdarzenie_kuwety(typ, z["plan_id"], z["plytka"], z["kuweta"])
        elif typ == "plan_wygasl":
            self._plan_ramki = None
            if self._tryb_ramki == "wynik":
                self._tryb_ramki = "gotowa"
            if self.rola == "W":
                self._uniewaznione_do = max(self._uniewaznione_do, nr)   # wynik sprzed przerwy nie wraca
                self._wyniki.clear()
            elif self._rano_baza is not None and z.get("plan_id") == self._rano_plan_id:
                self._zablokowane.clear()
                self._zlec_plan()
        elif typ == "blad_sprzetu":
            self._awaria = True
            self._blad = "blad_sprzetu"         # D5: komunikat takze po zdarzeniu (nie tylko po 409)
            self._plan_ramki = None
            self._tryb_ramki = "gotowa"
            if self.rola == "W":
                self._uniewaznione_do = max(self._uniewaznione_do, nr)
                self._wyniki.clear()
        elif typ == "sprzet_dziala":
            self._awaria = False
            if self._blad == "blad_sprzetu":
                self._blad = None
            if self.rola == "P" and self._rano_baza is not None:
                self._zablokowane.clear()
                self._zlec_plan()
        elif typ == "zgaszono":
            self._plan_ramki = None
            przyczyna = z.get("przyczyna")
            if przyczyna == "tryb" and isinstance(z.get("stan"), str):
                self._tryb_ramki = z["stan"]
            elif przyczyna == "usuniecie" or self._tryb_ramki == "wynik":
                self._tryb_ramki = "gotowa"
            if (self.rola == "P" and przyczyna in ("usuniecie", "tryb") and self._rano_baza is not None
                    and self._gaszace is None and pp is not None and nr > pp[3]):
                # D10: przyjety plan pieca zgaszony nie z biezacego polecenia (np. spoznione ponowienie DELETE) - plan,
                # ktory program nadal chce pokazac, idzie ponownie (nowa wersja, ten sam stan potwierdzen)
                self._zlec_plan()

    def _zdarzenie_kuwety(self, typ: str, pid: str, p: int, k: str) -> None:
        """Potwierdzenia z klawiatury - lustro stanu ramki (ramka stosuje je sama; laptop nie wysyla po nich planu)."""
        potw = self._potw.setdefault(pid, [])
        wyb = self._wyb.setdefault(pid, {})
        if typ == "potwierdzenie":
            if [p, k] not in potw:
                potw.append([p, k])
            wyb.pop(str(p), None)
        elif typ == "cofniecie":
            for i in range(len(potw) - 1, -1, -1):
                if potw[i] == [p, k]:
                    del potw[i]
                    break
            wyb[str(p)] = k
        else:
            wyb[str(p)] = k

    # ------------------------------------------------------------------ watek polecen

    def _petla_polecen(self, stop: threading.Event) -> None:
        while not stop.is_set():
            with self._warunek:
                zadanie = self._wybierz()
                if zadanie is None:
                    czas = 0.2
                    pauza = self._wstrzymanie_do - self._zegar()
                    if pauza > 0:
                        czas = min(czas, pauza)
                    self._warunek.wait(max(czas, 0.005))
                    continue
            try:
                if zadanie[0] == "gaszace":
                    self._wykonaj_gaszace(zadanie[1], stop)
                else:
                    self._wykonaj_plan(stop)
            except Exception:  # noqa: BLE001 - watek polecen nie moze zginac
                if not stop.is_set():
                    log.exception("ramka %s: blad w kolejce polecen", self.rola)
                stop.wait(self._przerwa_max)

    def _wybierz(self):
        if self._blad in ("zly_klucz", "zla_rola"):
            return None
        if self._zegar() < self._wstrzymanie_do:
            return None
        if self._gaszace is not None:
            return ("gaszace", self._gaszace)
        if self._plan_potrzebny and not self._wstrzymane_plany and self._mozna_planowac():
            return ("plan", None)
        return None

    def _mozna_planowac(self) -> bool:
        if self._start_id is None or self._potrzebna_migawka or not self._polaczona or self._awaria:
            return False
        if self._kursor < self._prog_stanu:
            return False        # najpierw odebrac zdarzenia do numeru z migawki GET /stan
        mk = self._min_kursor
        if mk is not None and mk[0] == self._start_id and self._kursor < mk[1]:
            return False        # najpierw odebrac zdarzenie wlasnego polecenia (wymaganie 5)
        cn = self._czekaj_na
        if cn is not None and cn[0] == self._start_id and self._kursor <= cn[1]:
            self._szybko.set()
            return False        # po 409 zdarzenia_nieodebrane: najpierw zdarzenia nowsze niz odrzucony plan
        return True

    def _pauza_po_bledzie(self) -> None:
        self._wstrzymanie_do = self._zegar() + self._przerwa_polecen
        self._przerwa_polecen = min(self._przerwa_polecen * 2, self._przerwa_max)

    def _wykonaj_gaszace(self, pol, stop: threading.Event) -> None:
        metoda, sciezka, tresc_d, tryb = pol
        tresc = RP.koduj(tresc_d) if tresc_d is not None else None
        try:
            st, d = self._zadanie(metoda, sciezka, tresc, stop=stop)
        except (RP.BladOdpowiedzi,) + BLEDY_SIECI:
            with self._warunek:
                self._bledy_sieci += 1
                self._pauza_po_bledzie()   # polecenie gaszace zostaje w kolejce: ponawiane do skutku
            return
        with self._warunek:
            if stop.is_set():
                return
            if st == 200:
                try:
                    d = RP.sprawdz_odpowiedz_polecenia(d)
                except RP.BladOdpowiedzi:
                    self._blad = "zla_odpowiedz"
                    self._pauza_po_bledzie()
                    return
                if self._gaszace is pol:
                    self._gaszace = None
                self._min_kursor = (d["start_id"], d["nr_zdarzenia"])
                self._przerwa_polecen = self._przerwa_min
                if self._blad == "polecenie_odrzucone" or (self._blad == "inny_laptop" and not self._wstrzymane_plany):
                    self._blad = None
                self._warunek.notify_all()
                return
            if st == 401:
                self._ustaw_zly_klucz()
                return
            kod, _, _ = RP.blad_odpowiedzi(d)
            self._kod_bledu = kod
            if kod == "inny_laptop":
                # P2: drugi laptop - zgaszenie ponawiane (bezpieczne), plany dopiero po jawnym wznow()
                self._blad = "inny_laptop"
                self._wstrzymane_plany = True
                self._wstrzymanie_do = self._zegar() + WSTRZYMANIE_INNY_LAPTOP_S
            else:
                self._blad = "polecenie_odrzucone"
                self._pauza_po_bledzie()
            self._warunek.notify_all()

    def _zbuduj_plan(self):
        """(plan, odcisk tresci) z biezacego stanu albo None (nic do pokazania). Pod blokada."""
        try:
            if self.rola == "P":
                if self._rano_baza is None:
                    return None
                if self.kalibracja is None:
                    self._blad = "brak_kalibracji"
                    self._zgas_po_bledzie_budowy()
                    return None
                pid = self._rano_plan_id
                plan, pom = RP.plan_rano(self._rano_baza, self.kalibracja, wersja=0, start_id=self._start_id,
                                         zdarzenia_do=self._kursor, potwierdzone=self._potw.get(pid, []),
                                         wybrane=self._wyb.get(pid, {}), wazny_s=self._wazny_s)
            else:
                wazne = self._wazne_wyniki()
                self._wyniki = wazne
                if not wazne:
                    return None
                plan, pom = RP.plan_wieczor({n: (w.uklad, w.kolory) for n, w in wazne.items()}, self.kalibracja,
                                            plan_id=self._plan_id_w, wersja=0, start_id=self._start_id,
                                            zdarzenia_do=self._kursor, wazny_s=self._wazny_s)
                if not plan["plytki"]:
                    return None
        except RP.BladProtokolu as e:
            self._blad = "plan_odrzucony"
            self._kod_bledu = e.kod
            log.error("ramka %s: planu nie da sie zbudowac zgodnie z protokolem (%s)", self.rola, e.kod)
            if self.rola == "P":
                self._zgas_po_bledzie_budowy()
            return None
        self._pominiete = pom
        return plan, RP.odcisk_tresci(plan)

    def _zgas_po_bledzie_budowy(self) -> None:
        """D4: nowej wersji planu pieca nie da sie zbudowac - poprzednia wersja nie moze zostac na ramce (niepewnosc =
        ciemno). Pod blokada; plan programu zostaje i pojdzie po kolejnej zmianie."""
        if self._plan_ramki is not None and self._gaszace is None:
            self._zlec_gaszace("DELETE", "/plan", None, None)

    def _wykonaj_plan(self, stop: threading.Event) -> None:
        with self._warunek:
            if stop.is_set() or not self._plan_potrzebny or not self._mozna_planowac():
                return      # D3: stan mogl sie zmienic od wyboru zadania (migawka, awaria)
            cel, gen, sid = self._cel, self._gen_gaszace, self._start_id
            zb = self._zbuduj_plan()
            if zb is None:
                if self._cel == cel:
                    self._plan_potrzebny = False
                if (self.rola == "W" and self._gaszace is None and self._ostatni_tryb in ("skanowanie", "analiza")):
                    # wynik ostatniego skanu stal sie niewazny (np. zdjecie plytki odebrane po 409): ramka nie zostaje
                    # w stanie skanowania / analizy
                    self._zlec_gaszace("PUT", "/tryb", RP.tresc_trybu("gotowa"), "gotowa")
                self._warunek.notify_all()
                return
            plan, odcisk = zb
            if odcisk in self._zablokowane:
                self._plan_potrzebny = False
                return
            pon = self._ponowienie
            ponowienie = pon is not None and pon["start_id"] == sid and pon["odcisk"] == odcisk
            if ponowienie:
                plan_id, wersja, tresc = pon["plan_id"], pon["wersja"], pon["tresc"]   # po zgubionej odpowiedzi
                zdarzenia_do = pon["zdarzenia_do"]
            else:
                plan_id = plan["plan_id"]
                wersja = self._wersje.get(plan_id, 0) + 1
                self._wersje[plan_id] = wersja
                plan["wersja"] = wersja
                tresc = RP.koduj(plan)
                zdarzenia_do = plan["zdarzenia_do"]
            self._ponowienie = None
            self._wyslane_plany += 1
            hak = self.przed_wyslaniem_planu
        if hak is not None:
            hak()
        try:
            st, d = self._zadanie("PUT", "/plan", tresc, stop=stop)
        except (RP.BladOdpowiedzi,) + BLEDY_SIECI:
            with self._warunek:
                self._bledy_sieci += 1
                if self._gen_gaszace == gen and self._start_id == sid and not stop.is_set():
                    self._ponowienie = {"start_id": sid, "odcisk": odcisk, "plan_id": plan_id, "wersja": wersja,
                                        "tresc": tresc, "zdarzenia_do": zdarzenia_do}
                self._pauza_po_bledzie()
            return
        with self._warunek:
            if stop.is_set():
                return
            self._po_planie(st, d, plan_id, wersja, odcisk, cel, ponowienie, sid, zdarzenia_do)
            po_odmowie, self._po_odmowie = self._po_odmowie, False
        if po_odmowie:
            self._stan_po_odmowie(stop, sid)

    def _stan_po_odmowie(self, stop: threading.Event, sid) -> None:
        """P-N1: `GET /stan` zaraz po 409 zdarzenia_nieodebrane - plan dopiero, gdy kursor dojdzie do `nr_zdarzenia` ramki."""
        try:
            st, d = self._zadanie("GET", "/stan", stop=stop)
            if st != 200:
                return
            d = RP.sprawdz_stan(d)
        except (RP.BladOdpowiedzi,) + BLEDY_SIECI:
            return      # zostaje warunek przyblizony (dwa zdarzenia nowsze niz odrzucony plan)
        with self._warunek:
            if not stop.is_set() and d["start_id"] == sid == self._start_id:
                self._min_kursor = (sid, d["nr_zdarzenia"])
                self._czekaj_na = None
                self._szybko.set()
                self._warunek.notify_all()

    def _po_planie(self, st, d, plan_id, wersja, odcisk, cel, ponowienie=False, sid=None, zdarzenia_do=0) -> None:
        """Odpowiedz na PUT /plan (README, wymaganie 6). Pod blokada."""
        if st == 200:
            try:
                d = RP.sprawdz_odpowiedz_polecenia(d)
            except RP.BladOdpowiedzi:
                self._blad = "zla_odpowiedz"
                self._pauza_po_bledzie()
                return
            self._przyjete_plany += 1
            self._przyjete_wersje.add((d["start_id"], plan_id, wersja))
            self._plan_przyjety = (plan_id, wersja, odcisk, d["nr_zdarzenia"], d["start_id"])
            self._min_kursor = (d["start_id"], d["nr_zdarzenia"])
            if self._cel == cel:
                self._plan_potrzebny = False
            if self.rola == "W":
                self._ostatni_tryb = None
            self._przerwa_polecen = self._przerwa_min
            if self._blad in ("plan_odrzucony", "blad_sprzetu", "polecenie_odrzucone"):
                self._blad = None
            self._warunek.notify_all()
            return
        if st == 401:
            self._ustaw_zly_klucz()
            return
        kod, _, wersja_ramki = RP.blad_odpowiedzi(d)
        self._kod_bledu = kod
        if wersja_ramki is not None:
            self._wersje[plan_id] = max(self._wersje.get(plan_id, 0), wersja_ramki)
        if kod == "zdarzenia_nieodebrane":
            # P-N1: odpytac, przeliczyc (potwierdzenia, zdjete plytki), nowa wersja dopiero, gdy kursor dojdzie do numeru
            # ostatniego zdarzenia ramki PO odmowie (GET /stan zaraz po tej odpowiedzi - zawiera tez `zgaszono` odmowy):
            # jedno ponowienie na zdarzenie, bez czekania na nowe dlugie odpytanie. Gdyby GET /stan sie nie udal - co
            # najmniej dwa zdarzenia nowsze niz odrzucony plan (brakujace + `zgaszono` odmowy).
            self._czekaj_na = (sid, zdarzenia_do + 1)
            self._po_odmowie = True
            self._szybko.set()
        elif kod in ("plan_starszy", "konflikt_wersji"):
            pass                                 # nowa wersja powyzej wersji ramki
        elif kod == "plan_zgaszony" and not ponowienie and (sid, plan_id, wersja) not in self._przyjete_wersje:
            # D2: ramka zna zamknieta wersje z POPRZEDNIEGO uruchomienia programu (ten sam plan_id, ta sama tresc) -
            # nie nasz obraz zgaszony celowo: jak plan_starszy, nowa wersja powyzej wersja_ramki
            if wersja_ramki is None:
                self._wersje[plan_id] = max(self._wersje.get(plan_id, 0), wersja)
        elif kod == "plan_zgaszony":
            self._zablokowane.add(odcisk)        # nasz obraz zgaszony celowo: tej tresci nie wysylac w zadnej wersji
            if self._cel == cel:
                self._plan_potrzebny = False
        elif kod == "inny_start":
            self._potrzebna_migawka = True
        elif kod == "inny_laptop":
            # P2: drugi laptop - bez automatycznego ponawiania planu (cicha zamiana kuwet po 30 s ciszy wlasciciela);
            # komunikat trwa, plan dopiero po jawnym wznow()
            self._blad = "inny_laptop"
            self._wstrzymane_plany = True
        elif kod == "blad_sprzetu":
            self._potrzebna_migawka = True       # D1: stan awarii z GET /stan (zdarzenie sprzet_dziala moglo juz byc)
            self._blad = "blad_sprzetu"
        else:                                    # 400 / 411 / 413 / 500 / plan_innej_ramki: ramka zgaszona
            self._blad = "plan_innej_ramki" if kod == "plan_innej_ramki" else "plan_odrzucony"
            self._zablokowane.add(odcisk)
            if self._cel == cel:
                self._plan_potrzebny = False
            log.error("ramka %s odrzucila plan: %s %s", self.rola, st, kod)
        self._warunek.notify_all()


# ----------------------------------------------------------------------------- dwie ramki stanowiska

def wczytaj_kalibracje(sciezka, katalog_modeli) -> tuple:
    """(kalibracja albo None, ostrzezenia). Brak pliku = wartosci startowe z geometrii plytek (plik nie jest zapisywany);
    zly plik = None (gniazda ciemne - lepiej nic niz zle gniazdo). E3-O2: plikowi, w ktorym brakuje ukladow majacych
    kalibracje startowa (plik sprzed E3-O2 nie ma ukladow okraglych ramkowych), brakujace uklady sa DOPISYWANE z geometrii
    i plik jest zapisywany (kopia starego obok; wpisy istniejace, takze "zrodlo": "kalibracja", bez zmian) + ostrzezenie;
    pliku nie da sie zapisac = uklady dopisane tylko w pamieci programu + ostrzezenie."""
    sciezka = Path(sciezka)
    if not sciezka.exists():
        try:
            return RP.kalibracja_domyslna(katalog_modeli), [
                "Brak pliku kalibracji ramek - wartosci startowe z geometrii plytek (kalibracja na ramce: paczka C2)."]
        except Exception as e:  # noqa: BLE001
            return None, [f"Brak kalibracji ramek ({type(e).__name__}) - gniazda nie beda wskazywane."]
    try:
        kal = RP.wczytaj_kalibracje(sciezka)
    except ValueError as e:
        return None, [f"Zly plik kalibracji ramek ({e}) - gniazda nie beda wskazywane."]
    return _uzupelnij_kalibracje(kal, sciezka, katalog_modeli)


def _uzupelnij_kalibracje(kal: dict, sciezka: Path, katalog_modeli) -> tuple:
    """(kalibracja, ostrzezenia): poprawny plik kalibracji + uklady, ktorych w nim brakuje (E3-O2). Blad uzupelniania
    (np. brak katalogu modeli) nie odbiera kalibracji z pliku - zostaje, jak byla."""
    def lista(dopisane) -> str:
        return ", ".join(f"{u} (ramka {r})" for r, u in dopisane)

    try:
        dane, dopisane = RP.uzupelnij_kalibracje(sciezka, katalog_modeli)
    except OSError as e:
        try:
            dopisane = RP.uzupelnij_kalibracje_w_pamieci(kal, katalog_modeli)
        except Exception:  # noqa: BLE001
            log.exception("kalibracja ramek: brakujacych ukladow nie da sie dopisac")
            return kal, []
        if not dopisane:
            return kal, []
        log.warning("kalibracja ramek: pliku nie da sie zapisac (%s) - uklady dopisane tylko w pamieci", type(e).__name__)
        return kal, [f"Uklady {lista(dopisane)} maja wartosci startowe z geometrii plytek, ale plik kalibracji ramek nie zostal "
                     f"zapisany ({type(e).__name__}) - przed praca z tymi plytkami skalibruj diody na ramce."]
    except Exception:  # noqa: BLE001 - np. brak katalogu modeli: kalibracja z pliku zostaje
        log.exception("kalibracja ramek: brakujacych ukladow nie da sie dopisac")
        return kal, []
    if not dopisane:
        return dane, []
    log.warning("kalibracja ramek: do pliku dopisano uklady z geometrii: %s", lista(dopisane))
    return dane, [f"Do pliku kalibracji ramek dopisano uklady {lista(dopisane)} - wartosci startowe z geometrii plytek; przed "
                  f"praca z tymi plytkami skalibruj diody na ramce (kopia starego pliku: z koncowka {RP.KAL.PRZYROSTEK_KOPII})."]


def identyfikator_laptopa(katalog) -> str:
    """Staly, losowy identyfikator programu laptopa (X-Laptop-Id) w pliku lokalnym `ramki_laptop_id.txt`."""
    plik = Path(katalog) / PLIK_ID_LAPTOPA
    try:
        tekst = plik.read_text(encoding="ascii").strip()
        if RP.WZOR_ID.fullmatch(tekst):
            return tekst
    except (OSError, UnicodeDecodeError):
        pass
    lid = "lap-" + secrets.token_hex(8)
    try:
        plik.parent.mkdir(parents=True, exist_ok=True)
        plik.write_text(lid + "\n", encoding="ascii")
    except OSError:
        log.warning("nie da sie zapisac identyfikatora laptopa - identyfikator tylko na czas programu")
    return lid


def _zapisany_identyfikator(katalog, lid: str) -> bool:
    try:
        return (Path(katalog) / PLIK_ID_LAPTOPA).read_text(encoding="ascii").strip() == lid
    except (OSError, UnicodeDecodeError):
        return False


class Indicate:
    """Obie ramki stanowiska: `wieczorna` (W) i `poranna` (P) - klienci `KlientRamki`."""

    def __init__(self, wieczorna: KlientRamki | None = None, poranna: KlientRamki | None = None):
        self.wieczorna = wieczorna
        self.poranna = poranna

    @classmethod
    def z_ustawien(cls, ust: dict, *, korzen=None, katalog_danych=None, na_zdarzenie=None, dziennik_ruchu=None,
                   **kw) -> "Indicate":
        """Klienci z ustawien: `[ramki] port, wieczorna_host, poranna_host, klucz, odpytywanie_s`, `[sciezki]
        kalibracja_ramek` (wzgledna od katalogu programu). Identyfikator laptopa w `katalog_danych` (domyslnie `dane/`
        programu - niezaleznie od pliku kalibracji, D9). Nie uruchamia watkow (`uruchom()`)."""
        if korzen is None:
            from . import ustawienia
            korzen = ustawienia.KORZEN
        korzen = Path(korzen)
        r, s = ust["ramki"], ust["sciezki"]
        sciezka = Path(s.get("kalibracja_ramek") or PLIK_KALIBRACJI)
        if not sciezka.is_absolute():
            sciezka = korzen / sciezka
        kal, ostrzezenia = wczytaj_kalibracje(sciezka, korzen / "modele_plytek")
        katalog = Path(katalog_danych) if katalog_danych is not None else korzen / "dane"
        lid = identyfikator_laptopa(katalog)
        if not _zapisany_identyfikator(katalog, lid):
            # D-N3: identyfikator tylko na czas programu - szybki restart = ramka widzi "drugi laptop" przez 30 s
            ostrzezenia = list(ostrzezenia) + [
                "Identyfikator laptopa nie zostal zapisany w katalogu danych - po restarcie programu ramka moze przez "
                "30 s zglaszac drugi laptop na stanowisku."]

        def klient(rola, host):
            return KlientRamki(rola, host, r["port"], laptop_id=lid, kalibracja=kal, klucz=r.get("klucz", ""),
                               odpytywanie_s=r.get("odpytywanie_s", 25.0), na_zdarzenie=na_zdarzenie,
                               dziennik_ruchu=dziennik_ruchu, ostrzezenia=ostrzezenia, **kw)

        return cls(klient("W", r["wieczorna_host"]), klient("P", r["poranna_host"]))

    def klienci(self) -> list:
        return [k for k in (self.wieczorna, self.poranna) if k is not None]

    def uruchom(self) -> None:
        for k in self.klienci():
            k.uruchom()

    def zatrzymaj(self, timeout: float = ZATRZYMANIE_S) -> dict:
        """Obie ramki naraz (kazda z proba wyslania oczekujacego zgaszenia) - razem najwyzej ok. `timeout` (P1). Zwraca
        {rola: czy oczekujace zgaszenie doszlo (albo nie bylo potrzebne)} - False = ramka moze jeszcze swiecic (D-N4)."""
        wyniki = {k.rola: False for k in self.klienci()}

        def zatrzymaj_klienta(k):
            wyniki[k.rola] = k.zatrzymaj(timeout)

        watki = [threading.Thread(target=zatrzymaj_klienta, args=(k,), daemon=True) for k in self.klienci()]
        for w in watki:
            w.start()
        koniec = time.monotonic() + timeout + 0.1
        for w in watki:
            w.join(max(0.0, koniec - time.monotonic()))
        return dict(wyniki)

    def stan(self) -> dict:
        return {k.rola: k.stan() for k in self.klienci()}
