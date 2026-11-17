"""Logika ramki niezalezna od sprzetu i sieci: stan, plan, dziennik zdarzen, reguly "co swieci".

Wszystkie metody przyjmuja czas `teraz` (sekundy, zegar monotoniczny) - testy podaja czas
sztuczny, program podaje `time.perf_counter()`. Klasa nie ma watkow ani blokad: wolajacy
(program.ProgramRamki) trzyma blokade.

Reguly "co swieci" (I1-I13; szczegoly w README.md, "Zasady bezpieczenstwa wskazan"):
- gniazda swieca tylko w stanie "wynik" (= jest przyjety, wazny plan), pod plytka o numerze
  z planu, gdy odczyt czujnikow jest ustalony (pewny) i sprzet dziala;
- ramka wieczorna swieci WSZYSTKIE gniazda planu plytki; ramka poranna: gniazdo przypisane do
  kuwety swieci tylko, gdy to biezaca kuweta i nie jest potwierdzona na tej plytce, gniazdo bez
  kuwety (nieznana praca, "sprawdz") swieci zawsze;
- zgaszenie jest ostateczne: DELETE /plan, kazdy PUT /tryb, odrzucone polecenie od wlasciciela i awaria
  sprzetu usuwaja plan z pamieci i zamykaja wersje ostatnio przyjetego planu, takze juz wygaslego
  (ten sam albo starszy plan = 409);
- plan traci waznosc, gdy laptop-wlasciciel planu nie odezwie sie przez `wazny_s` sekund (najwyzej
  granica roli): plan jest usuwany (zdarzenie plan_wygasl), stan wraca do `gotowa`, nic nie swieci;
- ramka wieczorna kasuje wynik plytki, gdy plytke zdjeto (ta sama plytka moze wrocic z nowymi pracami);
- runda 3: kazde zdarzenie, ktore gasi albo uniewaznia obraz, ma numer w dzienniku (plytka, plan_wygasl,
  blad_sprzetu, start, zgaszono - DELETE / PUT /tryb / odrzucenie od wlasciciela, plan_przyjety), a plan
  jest przyjmowany TYLKO z `zdarzenia_do` rownym numerowi ostatniego zdarzenia ramki - laptop potwierdza,
  ze odebral wszystko, co ramka zglosila (inaczej 409 zdarzenia_nieodebrane, ciemno).
"""
from __future__ import annotations

import secrets
from collections import deque
from itertools import islice

from . import WERSJA, obraz, protokol
from .protokol import BladProtokolu

MAX_KONTAKTOW = 16
MAX_WERSJI = 64
MAX_WPISYWANYCH = 6
CZAS_TEST_LED_S = 8.0  # test_led konczy sie sam (2 cykle kolorow) - nie zostaje przy zerwanej sieci


class LogikaRamki:
    def __init__(self, rola: str, *, start_id=None, teraz: float = 0.0, limit_lacznosci_s: float = 30.0,
                 max_zdarzen: int = 2000, czas_komunikatu_s: float = 3.0, rodzina=None, program: str = WERSJA):
        if rola not in ("W", "P"):
            raise ValueError("rola: W albo P")
        self.rola = rola
        self.start_id = start_id or secrets.token_hex(4)
        self.program = program
        self.t0 = teraz
        self.limit_lacznosci_s = float(limit_lacznosci_s)
        self.czas_komunikatu_s = float(czas_komunikatu_s)
        self.rodzina = tuple(rodzina) if rodzina else protokol.RODZINY[rola]
        self.plytka = 0
        self.plytka_pewna = True    # False = odczyt czujnikow inny niz ustalony / nieustalony (P7)
        self.tryb = "gotowa"
        self.tryb_od = teraz
        self.plan = None
        self.plan_laptop = None
        self.plan_czas = teraz
        self.plan_wazny_s = None    # wazny_s planu przyciete do granicy roli
        self.ostatni_plan_id = None  # ostatnio przyjety plan - zgaszenie zamyka jego wersje takze po wygasnieciu
        self.zgaszenie = float("-inf")  # czas ostatniego polecenia gaszacego (P1)
        self.awaria = False         # wyjatek w petli sprzetu, do pierwszego udanego obiegu (P4)
        self.potwierdzone = set()
        self.stos = {}
        self.wybrane = {}
        self.wpisywane = ""
        self.wpisywane_od = teraz
        self.komunikat = ""
        self.komunikat_do = 0.0
        self.pytanie_do = None      # "Zamknij piec": czeka na Enter do tej chwili
        self.pytanie_wygaslo = False  # D-N5: pytanie minelo bez Entera - pierwszy klawisz tylko to kasuje
        self.wlasciciel = None
        self.kontakty = {}
        self.wersje = {}
        self.zdarzenia = deque(maxlen=max_zdarzen)
        self.nr = 0
        self.zmiana = 0
        self.temp_c = None
        self._dodaj("start", teraz, rola=rola, program=program)

    # ------------------------------------------------------------------ dziennik zdarzen

    def _dodaj(self, typ: str, teraz: float, **pola) -> dict:
        self.nr += 1
        z = {"nr": self.nr, "typ": typ, "czas_s": round(teraz - self.t0, 3)}
        z.update(pola)
        self.zdarzenia.append(z)
        self.zmiana += 1
        return z

    def najstarsze_zdarzenie(self) -> int:
        return self.zdarzenia[0]["nr"] if self.zdarzenia else self.nr + 1

    def zdarzenia_od(self, od: int, limit: int = 100):
        """Zdarzenia o numerach > od (najwyzej `limit`) i liczba utraconych (wypchnietych z dziennika)."""
        od = max(0, int(od))
        najstarszy = self.najstarsze_zdarzenie()
        utracone = max(0, najstarszy - 1 - od)
        poczatek = max(0, od + 1 - najstarszy)
        return [dict(z) for z in islice(self.zdarzenia, poczatek, poczatek + max(0, limit))], utracone

    # ------------------------------------------------------------------ laczonosc i wlasnosc

    def kontakt(self, laptop_id, teraz: float) -> None:
        if not laptop_id:
            return
        if laptop_id not in self.kontakty and len(self.kontakty) >= MAX_KONTAKTOW:
            kandydaci = [x for x in self.kontakty if x not in (self.wlasciciel, self.plan_laptop)]
            if kandydaci:
                del self.kontakty[min(kandydaci, key=self.kontakty.get)]
        self.kontakty[laptop_id] = teraz

    def lacznosc(self, teraz: float) -> bool:
        """D-N4: kontakt laptopa-wlasciciela (planu, a bez planu - ostatniego polecenia) w limicie lacznosci;
        bez wlasciciela - kontakt dowolnego laptopa. Kontakt zapisuja tylko zadania z poprawnym kluczem
        (serwer odpowiada 401 przed czymkolwiek)."""
        wl = self.plan_laptop if self.plan is not None else self.wlasciciel
        if wl is None:
            return any(teraz - t <= self.limit_lacznosci_s for t in self.kontakty.values())
        return self._aktywny(wl, teraz)

    def _aktywny(self, laptop_id, teraz: float) -> bool:
        t = self.kontakty.get(laptop_id)
        return t is not None and teraz - t <= self.limit_lacznosci_s

    def _sprawdz_wlasciciela(self, laptop_id, teraz: float) -> None:
        if not laptop_id:
            raise BladProtokolu(400, "brak_laptopa", "naglowek X-Laptop-Id jest wymagany")
        wl = self.wlasciciel
        if wl is not None and wl != laptop_id and self._aktywny(wl, teraz):
            raise BladProtokolu(409, "inny_laptop", "ramke obsluguje inny laptop")

    def limit_odpytywania(self) -> float:
        """Najdluzsze czekanie w GET /zdarzenia - laptop odzywa sie dosc czesto dla waznosci planu."""
        x = self.limit_lacznosci_s
        if self.plan is not None:
            x = min(x, self.plan_wazny_s)
        return max(0.5, x / 3.0)

    # ------------------------------------------------------------------ plan

    def _plan_wazny(self, teraz: float) -> bool:
        if self.plan is None:
            return False
        t = self.kontakty.get(self.plan_laptop)
        return t is not None and teraz - t <= self.plan_wazny_s

    def _wyczysc_stan_planu(self) -> None:
        self.plan = None
        self.plan_laptop = None
        self.plan_wazny_s = None
        self.potwierdzone = set()
        self.stos = {}
        self.wybrane = {}
        self.wpisywane = ""
        self.komunikat = ""
        self.pytanie_do = None
        self.pytanie_wygaslo = False

    def tick(self, teraz: float) -> None:
        """Uplyw czasu: wygasniecie planu po utracie lacznosci z laptopem (stan wraca do gotowa - D-N3),
        koniec test_led, koniec pytania "Zamknij piec", wygasniecie wpisywanych cyfr."""
        if self.plan is not None and not self._plan_wazny(teraz):
            plan_id = self.plan.plan_id
            self._wyczysc_stan_planu()
            if self.tryb == "wynik":
                self.tryb = "gotowa"
                self.tryb_od = teraz
            self._dodaj("plan_wygasl", teraz, plan_id=plan_id)
        if self.tryb == "test_led" and teraz - self.tryb_od >= CZAS_TEST_LED_S:
            self.tryb = "gotowa"
            self.tryb_od = teraz
            self.zmiana += 1
        if self.pytanie_do is not None and teraz >= self.pytanie_do:
            self.pytanie_do = None
            self.pytanie_wygaslo = True
            self.zmiana += 1
        if self.wpisywane and teraz - self.wpisywane_od >= protokol.CZAS_WPISYWANIA_S:
            self.wpisywane = ""
            self.zmiana += 1

    def _zapamietaj_wersje(self, plan) -> None:
        self.wersje.pop(plan.plan_id, None)
        self.wersje[plan.plan_id] = {"wersja": plan.wersja, "odcisk": plan.odcisk, "zamknieta": False}
        while len(self.wersje) > MAX_WERSJI:
            del self.wersje[next(iter(self.wersje))]

    def _zamknij_wersje(self, plan_id) -> None:
        """Wersja planu zgaszona: ten sam plan (ta sama albo starsza wersja) nie zapali sie ponownie."""
        w = self.wersje.get(plan_id)
        if w is not None:
            w["zamknieta"] = True

    def _zgas(self, teraz: float, tryb=None, przyczyna=None, **pola) -> None:
        """Wspolne zgaszenie (DELETE, PUT /tryb, odrzucone polecenie wlasciciela, awaria sprzetu): plan
        usuniety z pamieci, wersja OSTATNIO PRZYJETEGO planu zamknieta takze wtedy, gdy plan juz wygasl
        (P-N2), PUT /plan odebrany przed ta chwila odrzucany (P1). `tryb` None = stan bez zmian, tylko
        `wynik` -> `gotowa`. `przyczyna` = zdarzenie zgaszono w dzienniku (runda 3: plan zbudowany przed
        nim ma za male zdarzenia_do); awaria ma wlasne zdarzenie blad_sprzetu."""
        plan_id = self._plan_id()
        if self.ostatni_plan_id is not None:
            self._zamknij_wersje(self.ostatni_plan_id)
        self._wyczysc_stan_planu()
        self.zgaszenie = teraz
        if tryb is None:
            tryb = "gotowa" if self.tryb == "wynik" else self.tryb
        if tryb != self.tryb:
            self.tryb_od = teraz
        self.tryb = tryb
        self.zmiana += 1
        if przyczyna is not None:
            self._dodaj("zgaszono", teraz, przyczyna=przyczyna, plan_id=plan_id, **pola)

    def _po_odrzuceniu(self, laptop_id, blad: BladProtokolu, teraz: float) -> None:
        """P5, D-N6: odrzucone polecenie od wlasciciela (albo laptopa, ktory moglby nim zostac) gasi obraz -
        poza odrzuceniami polecen starszych niz obraz tego samego planu, nie od wlasciciela albo nie do tej
        ramki. Zgaszenie = zdarzenie zgaszono (przyczyna odrzucenie, kod) i `blad.zgaszono` w odpowiedzi.
        Kazdy blad rozpatrywany raz (`obsluzony`: serwer nie gasi drugi raz po logice)."""
        if blad.obsluzony:
            return
        blad.obsluzony = True
        if not laptop_id or blad.kod in protokol.KODY_BEZ_ZMIANY_OBRAZU:
            return
        wl = self.wlasciciel
        if wl is not None and wl != laptop_id and self._aktywny(wl, teraz):
            return
        self._zgas(teraz, None, "odrzucenie", kod=blad.kod)
        blad.zgaszono = True

    def odrzucenie(self, laptop_id, blad: BladProtokolu, teraz: float) -> None:
        """Odrzucenie polecenia przez serwer poza logika (zly JSON, 411, 413, zly parametr, 404 / 405, 500)."""
        self.tick(teraz)
        self._po_odrzuceniu(laptop_id, blad, teraz)

    def przyjmij_plan(self, dane, laptop_id, teraz: float, t_odbioru=None) -> dict:
        """PUT /plan. Zwraca odpowiedz (wynik przyjety / powtorzony) albo zglasza BladProtokolu.
        `t_odbioru` = chwila przyjecia polaczenia z zadaniem (serwer); None = teraz."""
        self.tick(teraz)  # najpierw uplyw czasu: plan po terminie wygasa przed kontaktem (D1)
        self.kontakt(laptop_id, teraz)
        try:
            return self._przyjmij_plan(dane, laptop_id, teraz, t_odbioru)
        except BladProtokolu as b:
            self._po_odrzuceniu(laptop_id, b, teraz)
            raise

    def _przyjmij_plan(self, dane, laptop_id, teraz: float, t_odbioru) -> dict:
        plan = protokol.sprawdz_plan(dane, self.rola, self.rodzina)
        if not laptop_id:
            raise BladProtokolu(400, "brak_laptopa", "naglowek X-Laptop-Id jest wymagany")
        if plan.start_id != self.start_id:
            raise BladProtokolu(409, "inny_start", "plan dla innego startu ramki - odczytaj GET /stan")
        if plan.zdarzenia_do > self.nr:
            raise BladProtokolu(400, "zle_pole", "plan.zdarzenia_do: wieksze niz numer ostatniego zdarzenia")
        self._sprawdz_wlasciciela(laptop_id, teraz)
        if self.awaria:
            raise BladProtokolu(409, "blad_sprzetu", "awaria sprzetu ramki - czekaj na zdarzenie sprzet_dziala")
        poprzednia = self.wersje.get(plan.plan_id)
        # D-N8: najwyzsza wersja tego planu znana ramce (laptop po restarcie wie, od czego zaczac)
        znana = {"wersja_ramki": poprzednia["wersja"]} if poprzednia is not None else {}
        if t_odbioru is not None and t_odbioru < self.zgaszenie:
            raise BladProtokolu(409, "plan_zgaszony", "plan odebrany przed poleceniem zgaszenia - tej tresci nie "
                                "wysylac ponownie", **znana)
        if poprzednia is not None:
            if plan.wersja < poprzednia["wersja"]:
                raise BladProtokolu(409, "plan_starszy", "ramka ma nowsza wersje tego planu", **znana)
            if plan.wersja == poprzednia["wersja"]:
                if plan.odcisk != poprzednia["odcisk"]:
                    raise BladProtokolu(409, "konflikt_wersji", "ta sama wersja planu z inna trescia", **znana)
                if poprzednia["zamknieta"]:
                    raise BladProtokolu(409, "plan_zgaszony", "ta wersja planu zostala zgaszona - tej tresci nie "
                                        "wysylac ponownie", **znana)
                if self.plan is not None and self.plan.plan_id == plan.plan_id:
                    self.wlasciciel = laptop_id
                    return self._odpowiedz_planu("powtorzony")
        if plan.zdarzenia_do != self.nr:
            # runda 3: laptop nie odebral wszystkich zdarzen ramki (zdjecie plytki, zgaszenie, wygasniecie,
            # restart, przyjecie innego planu ...) - plan zbudowany na starszym stanie nie zapali sie
            raise BladProtokolu(409, "zdarzenia_nieodebrane",
                                "ramka ma zdarzenia, ktorych laptop nie odebral - odpytaj /zdarzenia, plan z "
                                "zdarzenia_do = numer ostatniego odebranego zdarzenia")
        self._wyczysc_stan_planu()
        self.plan = plan
        self.plan_laptop = laptop_id
        self.plan_czas = teraz
        self.plan_wazny_s = min(plan.wazny_s, protokol.MAX_WAZNY_S_ROLI[self.rola])
        self.potwierdzone = set(plan.potwierdzone)
        for p, k in plan.potwierdzone:
            self.stos.setdefault(p, []).append(k)
        self.wybrane = dict(plan.wybrane)
        self._zapamietaj_wersje(plan)
        self.ostatni_plan_id = plan.plan_id
        self.wlasciciel = laptop_id
        if self.tryb != "wynik":
            self.tryb_od = teraz
        self.tryb = "wynik"
        self.zmiana += 1
        # nowy obraz zastepuje poprzedni: plan zbudowany przed tym przyjeciem (np. spozniony PUT innego
        # plan_id - D-N2) ma za male zdarzenia_do
        self._dodaj("plan_przyjety", teraz, plan_id=plan.plan_id, wersja=plan.wersja)
        return self._odpowiedz_planu("przyjety")

    def _odpowiedz_planu(self, wynik: str) -> dict:
        return {"protokol": protokol.PROTOKOL, "wynik": wynik, "plan_id": self.plan.plan_id,
                "wersja": self.plan.wersja, "wazny_s": self.plan_wazny_s, "start_id": self.start_id,
                "nr_zdarzenia": self.nr}

    def usun_plan(self, laptop_id, teraz: float, plan_id=None) -> dict:
        """DELETE /plan = zgas: brak planu, stan gotowa, wersja planu zamknieta, zdarzenie zgaszono
        (zawsze, takze bez planu w pamieci; `nr_zdarzenia` w odpowiedzi = jego numer)."""
        self.tick(teraz)
        self.kontakt(laptop_id, teraz)
        self._sprawdz_wlasciciela(laptop_id, teraz)
        if self.plan is not None and plan_id is not None and plan_id != self.plan.plan_id:
            raise BladProtokolu(409, "inny_plan", "ramka ma inny plan niz wskazany")
        wynik = "usuniety" if self.plan is not None else "brak_planu"
        if plan_id is not None:
            self._zamknij_wersje(plan_id)
        self._zgas(teraz, "gotowa", "usuniecie")
        self.wlasciciel = laptop_id
        return {"protokol": protokol.PROTOKOL, "wynik": wynik, "start_id": self.start_id, "nr_zdarzenia": self.nr}

    def ustaw_tryb(self, dane, laptop_id, teraz: float) -> dict:
        """PUT /tryb: gotowa / skanowanie / analiza / blad / test_led. Kazdy usuwa plan (P2) i daje zdarzenie
        zgaszono (przyczyna tryb, stan); `nr_zdarzenia` w odpowiedzi = jego numer."""
        self.tick(teraz)
        self.kontakt(laptop_id, teraz)
        try:
            stan = protokol.sprawdz_tryb(dane)
            self._sprawdz_wlasciciela(laptop_id, teraz)
        except BladProtokolu as b:
            self._po_odrzuceniu(laptop_id, b, teraz)
            raise
        self._zgas(teraz, stan, "tryb", stan=stan)
        self.wlasciciel = laptop_id
        return {"protokol": protokol.PROTOKOL, "wynik": "przyjety", "stan": stan, "start_id": self.start_id,
                "nr_zdarzenia": self.nr}

    # ------------------------------------------------------------------ sprzet: awaria

    def awaria_sprzetu(self, teraz: float) -> None:
        """P4: wyjatek w petli sprzetu - zgaszenie jak po DELETE, plytka nieznana, zdarzenie blad_sprzetu
        (raz na awarie). Plany sa odrzucane (409 blad_sprzetu) do koniec_awarii (program: po
        `powrot_sprzetu_s` obiegow bez wyjatku - D-N7)."""
        if self.awaria:
            return
        self.awaria = True
        self._zgas(teraz, "gotowa")
        self._dodaj("blad_sprzetu", teraz)
        self.ustaw_plytke(0, teraz)

    def koniec_awarii(self, teraz: float) -> None:
        if not self.awaria:
            return
        self.awaria = False
        self.zmiana += 1
        self._dodaj("sprzet_dziala", teraz)

    # ------------------------------------------------------------------ plytka i klawiatura

    def ustaw_plytke(self, n: int, teraz: float) -> None:
        """Ustalony (po odbijaniu) numer plytki z czujnikow Halla: 0 = brak plytki (albo odczyt
        niepewny dluzej niz czas odbijania). Ramka wieczorna kasuje wtedy wynik poprzedniej plytki (P3)."""
        n = int(n)
        self.ustaw_pewnosc(True, teraz)
        if n == self.plytka:
            return
        stara = self.plytka
        self.plytka = n
        if protokol.KASUJ_PO_ZDJECIU_ROLI[self.rola] and self.plan is not None and stara in self.plan.plytki:
            del self.plan.plytki[stara]
            self._zamknij_wersje(self.plan.plan_id)  # ponowny PUT tej wersji nie przywroci wpisu
        self.wpisywane = ""
        self.komunikat = ""
        self.pytanie_wygaslo = False
        self._dodaj("plytka", teraz, plytka=n, poprzednia=stara)

    def ustaw_pewnosc(self, pewna: bool, teraz: float) -> None:
        """P7: False = surowy odczyt rozny od ustalonego albo jeszcze nieustalony - gniazda nie swieca."""
        pewna = bool(pewna)
        if pewna != self.plytka_pewna:
            self.plytka_pewna = pewna
            self.zmiana += 1

    def _plytka_widoczna(self) -> int:
        """Plytka, dla ktorej wolno swiecic: ustalona i pewna; inaczej 0 (jak brak plytki)."""
        return self.plytka if self.plytka_pewna and not self.awaria else 0

    def _plan_id(self):
        return self.plan.plan_id if self.plan is not None else None

    def _kuwety_na_plytce(self, p: int) -> dict:
        """{kuweta: liczba gniazd} na plytce p."""
        wynik = {}
        if self.plan is None or p not in self.plan.plytki:
            return wynik
        for g in self.plan.plytki[p].gniazda:
            if g.kuweta is not None:
                wynik[g.kuweta] = wynik.get(g.kuweta, 0) + 1
        return wynik

    def biezaca_kuweta(self):
        """Biezaca kuweta lezacej (pewnej) plytki - tylko rano; ramka wieczorna nie zna kuwet (B1)."""
        p = self._plytka_widoczna()
        if self.rola != "P" or self.plan is None or p not in self.plan.plytki:
            return None
        if p in self.wybrane:
            return self.wybrane[p]
        na = self._kuwety_na_plytce(p)
        for k in self.plan.kuwety:
            if k.kuweta in na and (p, k.kuweta) not in self.potwierdzone:
                return k.kuweta
        return None

    def _znajdz_kuwete(self, tekst: str):
        nazwy = [k.kuweta for k in self.plan.kuwety]
        if tekst in nazwy:
            return tekst
        if "#" + tekst in nazwy:
            return "#" + tekst
        try:
            liczba = int(tekst)
        except ValueError:
            return None
        zwykle = [k for k in nazwy if not k.startswith("#") and int(k) == liczba]
        if zwykle:
            return zwykle[0]
        prywatne = [k for k in nazwy if k.startswith("#") and int(k[1:]) == liczba]
        return prywatne[0] if prywatne else None

    def _plan_aktywny(self, teraz: float) -> bool:
        return self.plan is not None and self.tryb == "wynik" and self._plan_wazny(teraz) and not self.awaria

    def klawisz(self, k: str, teraz: float) -> None:
        """Klawisz klawiatury ramki porannej (enter, backspace, 0-9, zamknij_piec)."""
        self.tick(teraz)
        if self.rola != "P" or k not in protokol.KLAWISZE:
            return
        if self.pytanie_wygaslo:
            # D-N5: pytanie "PIEC?" minelo bez Entera - pierwszy klawisz po uplywie czasu tylko kasuje stan `*`
            # (Enter spozniony o chwile nie zamyka pieca i nie potwierdza biezacej kuwety)
            self.pytanie_wygaslo = False
            self.zmiana += 1
            return
        p = self._plytka_widoczna()
        if self.pytanie_do is not None:
            # "Zamknij piec", krok 2: Enter potwierdza; kazdy inny klawisz tylko anuluje pytanie
            self.pytanie_do = None
            self.zmiana += 1
            if k == "enter" and self._plan_aktywny(teraz) and p != 0:
                self._dodaj("zamknij_piec", teraz, plan_id=self._plan_id(), plytka=p)
            return
        if k == "zamknij_piec":
            # krok 1: pytanie na marginesie; bez planu i bez (pewnej) plytki klawisz nic nie robi (D-N5)
            if self._plan_aktywny(teraz) and p != 0:
                self.wpisywane = ""
                self.komunikat = ""
                self.pytanie_do = teraz + protokol.CZAS_POTWIERDZENIA_ZAMKNIECIA_S
                self.zmiana += 1
            return
        if not self._plan_aktywny(teraz) or p not in self.plan.plytki:
            return
        if k.isdigit():
            if len(self.wpisywane) < MAX_WPISYWANYCH:
                self.wpisywane += k
                self.wpisywane_od = teraz
                self.komunikat = ""
                self.zmiana += 1
            return
        if k == "backspace":
            if self.wpisywane:
                self.wpisywane = self.wpisywane[:-1]
                self.zmiana += 1
                return
            stos = self.stos.get(p)
            if stos:
                kuw = stos.pop()
                self.potwierdzone.discard((p, kuw))
                self.wybrane[p] = kuw
                self._dodaj("cofniecie", teraz, plan_id=self._plan_id(), plytka=p, kuweta=kuw)
            return
        # enter
        if self.wpisywane:
            tekst = self.wpisywane
            self.wpisywane = ""
            kuw = self._znajdz_kuwete(tekst)
            if kuw is None:
                self.komunikat = "?" + tekst
                self.komunikat_do = teraz + self.czas_komunikatu_s
                self._dodaj("kuweta_nieznana", teraz, plan_id=self._plan_id(), plytka=p, wpisano=tekst)
            else:
                self.komunikat = ""
                self.wybrane[p] = kuw
                self._dodaj("kuweta_wybrana", teraz, plan_id=self._plan_id(), plytka=p, kuweta=kuw)
            return
        kuw = self.biezaca_kuweta()
        if kuw is None:
            return
        if (p, kuw) not in self.potwierdzone and self._kuwety_na_plytce(p).get(kuw):
            self.potwierdzone.add((p, kuw))
            self.stos.setdefault(p, []).append(kuw)
            self.wybrane.pop(p, None)
            self._dodaj("potwierdzenie", teraz, plan_id=self._plan_id(), plytka=p, kuweta=kuw)
        else:
            self.wybrane.pop(p, None)
            self.zmiana += 1

    # ------------------------------------------------------------------ stan i obraz

    def stan(self, teraz: float) -> dict:
        wazny = self._plan_wazny(teraz)
        plan = self.plan if wazny else None
        pozostalo = None
        if plan is not None:
            pozostalo = round(self.plan_wazny_s - (teraz - self.kontakty[self.plan_laptop]), 3)
        wl = self.wlasciciel
        return {
            "protokol": protokol.PROTOKOL, "rola": self.rola, "program": self.program,
            "start_id": self.start_id, "czas_s": round(teraz - self.t0, 3), "plytka": self.plytka,
            "plytka_pewna": self.plytka_pewna, "tryb": self.tryb, "plan_id": plan.plan_id if plan else None,
            "plan_wersja": plan.wersja if plan else None, "plan_wazny_s": self.plan_wazny_s if plan else None,
            "plan_pozostalo_s": pozostalo, "plytki_planu": sorted(plan.plytki) if plan else [],
            # P6: bez identyfikatora laptopa-wlasciciela - tylko czy ramke obsluguje teraz jakis laptop
            "wlasciciel": wl is not None and self._aktywny(wl, teraz),
            "kuweta": self.biezaca_kuweta() if plan else None,
            # D2: stan potwierdzen z ramki (laptop odtwarza go po utracie zdarzen z dziennika)
            "potwierdzone": [[p, k] for p in sorted(self.stos) for k in self.stos[p]] if plan else [],
            "wybrane": {str(p): k for p, k in sorted(self.wybrane.items())} if plan else {},
            "wpisywane": self.wpisywane, "nr_zdarzenia": self.nr,
            "najstarsze_zdarzenie": self.najstarsze_zdarzenie(), "lacznosc": self.lacznosc(teraz),
            "blad_sprzetu": self.awaria, "temp_c": self.temp_c,
        }

    def _tekst_przod_rano(self, p: int, teraz: float):
        """Napis z przodu i numery innych plytek dla ramki porannej w stanie wynik."""
        if self.wpisywane:
            return self.wpisywane + "_", []
        if self.komunikat and teraz < self.komunikat_do:
            return self.komunikat, []
        kuw = self.biezaca_kuweta()
        if kuw is None:
            if self.plan.braki:
                i = int(max(0.0, teraz - self.plan_czas) // 2.0) % len(self.plan.braki)
                return "-" + self.plan.braki[i], []
            return "OK", []
        liczba = self._kuwety_na_plytce(p).get(kuw, 0) if (p, kuw) not in self.potwierdzone else 0
        inne = []
        for k in self.plan.kuwety:
            if k.kuweta == kuw:
                inne = [n for n in k.plytki if n != p]
        return (f"{kuw} {liczba}" if liczba else kuw), inne

    def obraz(self, teraz: float) -> obraz.Klatka:
        """Klatka 64 x 64 wynikajaca ze stanu (bez zmiany stanu)."""
        k = obraz.Klatka()
        if self.tryb == "test_led" and teraz - self.tryb_od < CZAS_TEST_LED_S:
            faza = int(max(0.0, teraz - self.tryb_od) // 1.0) % len(obraz.KOLORY_TEST_LED)
            k.wypelnij(obraz.KOLORY_TEST_LED[faza])
            return k
        lacznosc = self.lacznosc(teraz)
        wazny = self._plan_wazny(teraz)
        p = self._plytka_widoczna()  # odczyt niepewny (P7) albo awaria (P4) = jak brak plytki
        ma_plan_plytki = wazny and p in self.plan.plytki
        tekst, inne = "", []
        if self.awaria or self.tryb == "blad":
            stan_k = "blad"
            tekst = "BLAD"
        elif self.tryb in ("skanowanie", "analiza"):
            stan_k = self.tryb
        elif p == 0:
            stan_k = "gotowa"
        elif not ma_plan_plytki:
            stan_k = "brak_planu"
            tekst = f"{p} BRAK"
        elif self.tryb != "wynik":
            stan_k = "gotowa"
        else:
            stan_k = "wynik"
            biezaca = self.biezaca_kuweta()
            for g in self.plan.plytki[p].gniazda:
                # B1: ramka wieczorna swieci wszystkie gniazda planu (regula kuwet tylko rano)
                if self.rola == "W" or g.kuweta is None or \
                        (g.kuweta == biezaca and (p, g.kuweta) not in self.potwierdzone):
                    x, y, w, h = g.px
                    k.blok(x, y, w, h, obraz.KOLORY[g.kolor])
            if self.rola == "P":
                tekst, inne = self._tekst_przod_rano(p, teraz)
            else:
                tekst = str(p)
        if self.pytanie_do is not None and teraz < self.pytanie_do and not self.awaria:
            tekst, inne = "PIEC?", []  # "Zamknij piec": czeka na Enter
        if lacznosc:
            obraz.rysuj_pierscien(k, obraz.KOLORY_STANU[stan_k])
            obraz.rysuj_ikone(k, obraz.KOLORY_STANU["lacznosc"])
        else:
            if int(teraz * 2.0) % 2 == 0:
                obraz.rysuj_pierscien(k, obraz.KOLORY_STANU["brak_lacznosci"])
            obraz.rysuj_ikone(k, obraz.KOLORY_STANU["brak_lacznosci"])
        obraz.rysuj_tekst_przod(k, tekst)
        obraz.rysuj_prawy(k, inne)
        return k
