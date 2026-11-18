"""Logika ramki niezalezna od sprzetu i sieci: stan, plan, dziennik zdarzen, reguly "co swieci".

Wszystkie metody przyjmuja czas `teraz` (sekundy, zegar monotoniczny) - testy podaja czas
sztuczny, program podaje `time.perf_counter()`. Klasa nie ma watkow ani blokad: wolajacy
(program.ProgramRamki) trzyma blokade.

Reguly "co swieci" (I1-I13; szczegoly w README.md):
- gniazda swieca tylko w stanie "wynik", przy waznym planie i plytce o numerze z planu;
- gniazdo przypisane do kuwety swieci tylko, gdy to biezaca kuweta i nie jest potwierdzona
  na tej plytce; gniazdo bez kuwety (nieznana praca, "sprawdz", wynik wieczorny) swieci zawsze;
- plan traci waznosc, gdy laptop-wlasciciel planu nie odezwie sie przez `wazny_s` sekund:
  plan jest usuwany (zdarzenie plan_wygasl) i nic nie swieci;
- plytka bez planu, stan blad / skanowanie / analiza / gotowa = zadne gniazdo nie swieci.
"""
from __future__ import annotations

import secrets
from collections import deque
from itertools import islice

from . import WERSJA, obraz, protokol
from .protokol import BladProtokolu

TYPY_STANU_PLANU = ("potwierdzenie", "cofniecie", "kuweta_wybrana")
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
        self.tryb = "gotowa"
        self.tryb_od = teraz
        self.plan = None
        self.plan_laptop = None
        self.plan_czas = teraz
        self.potwierdzone = set()
        self.stos = {}
        self.wybrane = {}
        self.wpisywane = ""
        self.komunikat = ""
        self.komunikat_do = 0.0
        self.wlasciciel = None
        self.kontakty = {}
        self.wersje = {}
        self.ostatnie_stanu_planu = {}
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
        if typ in TYPY_STANU_PLANU:
            self.ostatnie_stanu_planu[pola.get("plan_id")] = self.nr
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
        return any(teraz - t <= self.limit_lacznosci_s for t in self.kontakty.values())

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
            x = min(x, self.plan.wazny_s)
        return max(0.5, x / 3.0)

    # ------------------------------------------------------------------ plan

    def _plan_wazny(self, teraz: float) -> bool:
        if self.plan is None:
            return False
        t = self.kontakty.get(self.plan_laptop)
        return t is not None and teraz - t <= self.plan.wazny_s

    def _wyczysc_stan_planu(self) -> None:
        self.plan = None
        self.plan_laptop = None
        self.potwierdzone = set()
        self.stos = {}
        self.wybrane = {}
        self.wpisywane = ""
        self.komunikat = ""

    def tick(self, teraz: float) -> None:
        """Uplyw czasu: wygasniecie planu po utracie lacznosci z laptopem, koniec test_led."""
        if self.plan is not None and not self._plan_wazny(teraz):
            plan_id = self.plan.plan_id
            self._wyczysc_stan_planu()
            self._dodaj("plan_wygasl", teraz, plan_id=plan_id)
        if self.tryb == "test_led" and teraz - self.tryb_od >= CZAS_TEST_LED_S:
            self.tryb = "gotowa"
            self.tryb_od = teraz
            self.zmiana += 1

    def _zapamietaj_wersje(self, plan) -> None:
        self.wersje.pop(plan.plan_id, None)
        self.wersje[plan.plan_id] = (plan.wersja, plan.odcisk)
        while len(self.wersje) > MAX_WERSJI:
            del self.wersje[next(iter(self.wersje))]

    def przyjmij_plan(self, dane, laptop_id, teraz: float) -> dict:
        """PUT /plan. Zwraca odpowiedz (wynik przyjety / powtorzony) albo zglasza BladProtokolu."""
        self.kontakt(laptop_id, teraz)
        self.tick(teraz)
        plan = protokol.sprawdz_plan(dane, self.rola, self.rodzina)
        if not laptop_id:
            raise BladProtokolu(400, "brak_laptopa", "naglowek X-Laptop-Id jest wymagany")
        if plan.start_id != self.start_id:
            raise BladProtokolu(409, "inny_start", "plan dla innego startu ramki - odczytaj GET /stan")
        if plan.zdarzenia_do > self.nr:
            raise BladProtokolu(400, "zle_pole", "plan.zdarzenia_do: wieksze niz numer ostatniego zdarzenia")
        self._sprawdz_wlasciciela(laptop_id, teraz)
        poprzednia = self.wersje.get(plan.plan_id)
        if poprzednia is not None:
            wersja, odcisk = poprzednia
            if plan.wersja < wersja:
                raise BladProtokolu(409, "plan_starszy", "ramka ma nowsza wersje tego planu")
            if plan.wersja == wersja:
                if plan.odcisk != odcisk:
                    raise BladProtokolu(409, "konflikt_wersji", "ta sama wersja planu z inna trescia")
                if self.plan is not None and self.plan.plan_id == plan.plan_id:
                    self.wlasciciel = laptop_id
                    return self._odpowiedz_planu("powtorzony")
        if plan.zdarzenia_do < self.ostatnie_stanu_planu.get(plan.plan_id, 0):
            raise BladProtokolu(409, "zdarzenia_nieodebrane",
                                "ramka ma zdarzenia tego planu, ktorych laptop nie odebral - odpytaj /zdarzenia")
        self._wyczysc_stan_planu()
        self.plan = plan
        self.plan_laptop = laptop_id
        self.plan_czas = teraz
        self.potwierdzone = set(plan.potwierdzone)
        for p, k in plan.potwierdzone:
            self.stos.setdefault(p, []).append(k)
        self.wybrane = dict(plan.wybrane)
        self._zapamietaj_wersje(plan)
        self.wlasciciel = laptop_id
        self.tryb = "wynik"
        self.tryb_od = teraz
        self.zmiana += 1
        return self._odpowiedz_planu("przyjety")

    def _odpowiedz_planu(self, wynik: str) -> dict:
        return {"protokol": protokol.PROTOKOL, "wynik": wynik, "plan_id": self.plan.plan_id,
                "wersja": self.plan.wersja, "start_id": self.start_id, "nr_zdarzenia": self.nr}

    def usun_plan(self, laptop_id, teraz: float, plan_id=None) -> dict:
        """DELETE /plan = zgas: brak planu, stan gotowa."""
        self.kontakt(laptop_id, teraz)
        self.tick(teraz)
        self._sprawdz_wlasciciela(laptop_id, teraz)
        if self.plan is None:
            wynik = "brak_planu"
        elif plan_id is not None and plan_id != self.plan.plan_id:
            raise BladProtokolu(409, "inny_plan", "ramka ma inny plan niz wskazany")
        else:
            self._wyczysc_stan_planu()
            wynik = "usuniety"
        self.wlasciciel = laptop_id
        self.tryb = "gotowa"
        self.tryb_od = teraz
        self.zmiana += 1
        return {"protokol": protokol.PROTOKOL, "wynik": wynik, "start_id": self.start_id, "nr_zdarzenia": self.nr}

    def ustaw_tryb(self, dane, laptop_id, teraz: float) -> dict:
        """PUT /tryb: gotowa / skanowanie / analiza / wynik / blad / test_led."""
        self.kontakt(laptop_id, teraz)
        self.tick(teraz)
        stan = protokol.sprawdz_tryb(dane)
        self._sprawdz_wlasciciela(laptop_id, teraz)
        self.wlasciciel = laptop_id
        if stan != self.tryb:
            self.tryb_od = teraz
        self.tryb = stan
        self.zmiana += 1
        return {"protokol": protokol.PROTOKOL, "wynik": "przyjety", "stan": stan, "start_id": self.start_id,
                "nr_zdarzenia": self.nr}

    # ------------------------------------------------------------------ plytka i klawiatura

    def ustaw_plytke(self, n: int, teraz: float) -> None:
        """Ustalony (po odbijaniu) numer plytki z czujnikow Halla: 0 = brak plytki."""
        n = int(n)
        if n == self.plytka:
            return
        stara = self.plytka
        self.plytka = n
        if self.plan is not None and stara in self.plan.plytki and self.plan.plytki[stara].usun_po_zdjeciu:
            del self.plan.plytki[stara]
        self.wpisywane = ""
        self.komunikat = ""
        self._dodaj("plytka", teraz, plytka=n, poprzednia=stara)

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
        p = self.plytka
        if self.plan is None or p not in self.plan.plytki:
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

    def klawisz(self, k: str, teraz: float) -> None:
        """Klawisz klawiatury ramki porannej (enter, backspace, 0-9, zamknij_piec)."""
        self.tick(teraz)
        if self.rola != "P" or k not in protokol.KLAWISZE:
            return
        p = self.plytka
        if k == "zamknij_piec":
            self.wpisywane = ""
            self._dodaj("zamknij_piec", teraz, plan_id=self._plan_id(), plytka=p)
            return
        if self.plan is None or p not in self.plan.plytki or self.tryb != "wynik" or not self._plan_wazny(teraz):
            return
        if k.isdigit():
            if len(self.wpisywane) < MAX_WPISYWANYCH:
                self.wpisywane += k
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
            pozostalo = round(plan.wazny_s - (teraz - self.kontakty[self.plan_laptop]), 3)
        return {
            "protokol": protokol.PROTOKOL, "rola": self.rola, "program": self.program,
            "start_id": self.start_id, "czas_s": round(teraz - self.t0, 3), "plytka": self.plytka,
            "tryb": self.tryb, "plan_id": plan.plan_id if plan else None,
            "plan_wersja": plan.wersja if plan else None, "plan_wazny_s": plan.wazny_s if plan else None,
            "plan_pozostalo_s": pozostalo, "plytki_planu": sorted(plan.plytki) if plan else [],
            "laptop": self.wlasciciel, "kuweta": self.biezaca_kuweta() if plan else None,
            "wpisywane": self.wpisywane, "nr_zdarzenia": self.nr,
            "najstarsze_zdarzenie": self.najstarsze_zdarzenie(), "lacznosc": self.lacznosc(teraz),
            "temp_c": self.temp_c,
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
        p = self.plytka
        ma_plan_plytki = wazny and p in self.plan.plytki
        tekst, inne = "", []
        if self.tryb == "blad":
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
                if g.kuweta is None or (g.kuweta == biezaca and (p, g.kuweta) not in self.potwierdzone):
                    x, y, w, h = g.px
                    k.blok(x, y, w, h, obraz.KOLORY[g.kolor])
            if self.rola == "P":
                tekst, inne = self._tekst_przod_rano(p, teraz)
            else:
                tekst = str(p)
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
