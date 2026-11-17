"""Testy programu ramki (E3-A8, czesc "ramka") - atrapa sprzetu, bez elektroniki.

Kryteria z planu etapu 3 (sekcja 4.1, E3-A8) dotyczace programu ramki: K1-K9 (nazwy testow
`test_k<n>_...`) oraz dodatkowe przypadki z prompta paczki: wygasniecie planu po utracie
lacznosci, zmiana plytki w trakcie, plytka bez planu, powtorzony / spozniony plan, zdarzenia
klawiatury bez gubienia i bez powtorek, zle dane, dwa laptopy naraz, restart programu ramki.

Serwer testowy slucha WYLACZNIE na 127.0.0.1 (losowy wolny port). Klient laptopa w testach to
maly klient z biblioteki standardowej (nie modul `indicate` - ten pisze inny wykonawca).
Dane osobowe: w testach sa tylko fikcyjne nazwy folderow i tylko po to, zeby pokazac, ze nie
trafiaja do ruchu sieciowego ani do logow ramki.
"""
from __future__ import annotations

import ast
import hashlib
import http.client
import json
import logging
import random
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

STANOWISKO = Path(__file__).resolve().parent.parent
if str(STANOWISKO) not in sys.path:
    sys.path.insert(0, str(STANOWISKO))

from ramka import czcionka, kalibracja, obraz, protokol, sprzet_rpi, test_led  # noqa: E402
from ramka.logika import LogikaRamki  # noqa: E402
from ramka.program import Konfiguracja, ProgramRamki  # noqa: E402
from ramka.sprzet import BladSprzetu, Odbijanie  # noqa: E402
from ramka.sprzet_atrapa import SprzetAtrapa  # noqa: E402

MODELE = STANOWISKO / "modele_plytek"
LAPTOP = "lap-test-1"
CZARNY = (0, 0, 0)
BLEDY_SIECI = (OSError, http.client.HTTPException)

# Fikcyjne nazwy folderow zlecen (dane osobowe udawane) - laptop zna je w swojej sesji,
# ale do ramki maja trafiac tylko numery kuwet.
FOLDERY = {
    "3263": "Kowalczykowa 3263 ZR",
    "3301": "Wisniewska3301KB",
    "0412": "J. Zielinski 0412",
    "#1234": "Prywatne Lewandowski",
    "3999": "Dabrowski 3999 AB",
    "4100": "Szymanska 4100",
}
NAZWISKA = ("Kowalczykowa", "Wisniewska", "Zielinski", "Lewandowski", "Dabrowski", "Szymanska")


# ----------------------------------------------------------------------------- pomocnicze

@pytest.fixture(scope="module")
def kal():
    return kalibracja.domyslna(MODELE)


def gniazda(kal_, rola, uklad, przypisanie):
    """przypisanie: {id: (kolor, kuweta albo None)} -> lista gniazd planu (jak liczy laptop)."""
    return kalibracja.gniazda_planu(
        kal_, rola, uklad, {i: {"kolor": k, "kuweta": kw} for i, (k, kw) in przypisanie.items()})


def plan_rano(kal_, logika_or_none=None, *, plan_id="2026-11-17-p1", wersja=1, start_id="0000",
              zdarzenia_do=0, wazny_s=600.0, potwierdzone=None, braki=("5120",)):
    """Plan porannej sesji pieca: plytki 4 i 5 (uklad poranna), kolejnosc kuwet z listy."""
    p4 = {1: ("bialy", None), 2: ("zielony", "3263"), 3: ("zielony", "3263"), 4: ("zielony", "3263"),
          5: ("zielony", "3301"), 6: ("zielony", "3301"), 7: ("bursztyn", "0412"),
          8: ("zielony", "#1234"), 9: ("zielony", "3999"), 10: ("czerwony", None)}
    p5 = {13: ("zielony", "3263"), 14: ("zielony", "3263"), 15: ("zielony", "4100"), 20: ("bialy", None)}
    if logika_or_none is not None:
        start_id = logika_or_none.start_id
        zdarzenia_do = logika_or_none.nr
    return {
        "protokol": 1, "plan_id": plan_id, "wersja": wersja, "start_id": start_id,
        "zdarzenia_do": zdarzenia_do, "wazny_s": wazny_s, "tryb": "rano", "kolejnosc": "liczba",
        "plytki": {"4": {"uklad": "poranna", "gniazda": gniazda(kal_, "P", "poranna", p4)},
                   "5": {"uklad": "poranna", "gniazda": gniazda(kal_, "P", "poranna", p5)}},
        "kuwety": [{"kuweta": "3263", "prac": 5, "plytki": [4, 5]},
                   {"kuweta": "3301", "prac": 2, "plytki": [4]},
                   {"kuweta": "0412", "prac": 1, "plytki": [4]},
                   {"kuweta": "#1234", "prac": 1, "plytki": [4]},
                   {"kuweta": "3999", "prac": 1, "plytki": [4]},
                   {"kuweta": "4100", "prac": 1, "plytki": [5]}],
        "potwierdzone": list(potwierdzone or []),
        "braki": list(braki),
    }


def plan_wieczor(kal_, logika_or_none=None, *, plytka=2, plan_id="2026-11-17-w", wersja=1,
                 start_id="0000", zdarzenia_do=0, wazny_s=30.0, uklad="wieczorna", kolory=None):
    """Plan ramki wieczornej: wszystkie gniazda plytki z kolorami (bez kuwet)."""
    ids = sorted(kal_["ramki"]["W"][uklad]["gniazda"], key=int)
    kol = kolory or ["zielony", "czerwony", "zolty", "szary"]
    przyp = {int(i): (kol[n % len(kol)], None) for n, i in enumerate(ids)}
    if logika_or_none is not None:
        start_id = logika_or_none.start_id
        zdarzenia_do = logika_or_none.nr
    return {"protokol": 1, "plan_id": plan_id, "wersja": wersja, "start_id": start_id,
            "zdarzenia_do": zdarzenia_do, "wazny_s": wazny_s, "tryb": "wieczor",
            "plytki": {str(plytka): {"uklad": uklad, "gniazda": gniazda(kal_, "W", uklad, przyp)}}}


def oczekiwane_piksele(plan, plytka, swiecace_ids):
    """{(x, y): rgb} dla gniazd planu o podanych id (bloki px z planu)."""
    wynik = {}
    for g in plan["plytki"][str(plytka)]["gniazda"]:
        if g["id"] in swiecace_ids:
            x, y, w, h = g["px"]
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    wynik[(xx, yy)] = obraz.KOLORY[g["kolor"]]
    return wynik


def piksele_plytki(klatka):
    """Zapalone piksele w obszarze plytki (bez marginesu)."""
    x0, y0, w, h = obraz.OBSZAR_PLYTKI
    return {(x, y): klatka.piksel(x, y) for y in range(y0, y0 + h) for x in range(x0, x0 + w)
            if klatka.piksel(x, y) != CZARNY}


def porownaj_obszar_plytki(klatka, oczekiwane):
    """Porownanie piksel po pikselu w calym obszarze plytki; zwraca liste roznic."""
    x0, y0, w, h = obraz.OBSZAR_PLYTKI
    roznice = []
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if klatka.piksel(x, y) != oczekiwane.get((x, y), CZARNY):
                roznice.append((x, y))
    return roznice


def tekst_ref(tekst, x0, y0, rgb):
    pix = {}
    x = x0
    for z in tekst:
        for dy, wiersz in enumerate(czcionka.glif(z)):
            for dx, c in enumerate(wiersz):
                if c == "#":
                    pix[(x + dx, y0 + dy)] = rgb
        x += czcionka.SZER + czcionka.ODSTEP
    return pix


def x_tekstu_przod(tekst):
    w = len(tekst) * (czcionka.SZER + czcionka.ODSTEP) - czcionka.ODSTEP
    return obraz.TEKST_X0 + (obraz.TEKST_SZER - w) // 2


def region(klatka, x0, y0, w, h):
    return {(x, y): klatka.piksel(x, y) for y in range(y0, y0 + h) for x in range(x0, x0 + w)
            if klatka.piksel(x, y) != CZARNY}


def tekst_przod(klatka):
    return region(klatka, obraz.TEKST_X0, obraz.TEKST_Y, obraz.TEKST_SZER, czcionka.WYS)


def logika_z_planem(kal_, plan_fn=plan_rano, rola="P", plytka=4, **kw):
    log = LogikaRamki(rola, teraz=0.0)
    log.kontakt(LAPTOP, 0.0)
    odp = log.przyjmij_plan(plan_fn(kal_, log, **kw), LAPTOP, 0.0)
    assert odp["wynik"] == "przyjety"
    if plytka:
        log.ustaw_plytke(plytka, 0.1)
    return log


def uruchom(rola, **kw):
    atrapa = kw.pop("sprzet", None) or SprzetAtrapa()
    konf = Konfiguracja(rola=rola, host="127.0.0.1", port=kw.pop("port", 0), **kw)
    prog = ProgramRamki(konf, sprzet=atrapa)
    _, port = prog.uruchom()
    return prog, atrapa, port


@pytest.fixture
def ramka_p():
    prog, atrapa, port = uruchom("P")
    yield prog, atrapa, port
    prog.zatrzymaj()


@pytest.fixture
def ramka_w():
    prog, atrapa, port = uruchom("W")
    yield prog, atrapa, port
    prog.zatrzymaj()


class Laptop:
    """Minimalny klient laptopa (biblioteka standardowa): odpytywanie z kursorem zdarzen."""

    def __init__(self, port, laptop_id=LAPTOP, host="127.0.0.1"):
        self.host, self.port, self.id = host, port, laptop_id
        self.od = 0
        self.start_id = None
        self.zdarzenia = []

    def zadanie(self, metoda, sciezka, tresc=None, naglowki=None, timeout=15.0, surowa=None):
        c = http.client.HTTPConnection(self.host, self.port, timeout=timeout)
        try:
            h = {"X-Laptop-Id": self.id} if self.id else {}
            h.update(naglowki or {})
            body = surowa
            if tresc is not None:
                body = json.dumps(tresc).encode("utf-8")
                h["Content-Type"] = "application/json"
            c.request(metoda, sciezka, body=body, headers=h)
            r = c.getresponse()
            dane = r.read()
            return r.status, (json.loads(dane.decode("utf-8")) if dane else None)
        finally:
            c.close()

    def stan(self):
        st, odp = self.zadanie("GET", "/stan")
        assert st == 200
        self.start_id = odp["start_id"]
        return odp

    def odpytaj(self, czekaj=0.0, limit=None):
        q = f"/zdarzenia?od={self.od}&czekaj={czekaj}"
        if self.start_id:
            q += f"&start_id={self.start_id}"
        if limit:
            q += f"&limit={limit}"
        st, odp = self.zadanie("GET", q, timeout=czekaj + 15.0)
        assert st == 200, odp
        if odp.get("restart") or odp["start_id"] != self.start_id:
            self.start_id = odp["start_id"]
            self.od = 0
        nowe = odp["zdarzenia"]
        if nowe:
            self.od = nowe[-1]["nr"]
        self.zdarzenia.extend(nowe)
        return nowe

    def dobierz(self):
        while self.odpytaj(0.0):
            pass

    def wyslij_plan(self, plan):
        plan = dict(plan)
        plan["start_id"] = self.start_id
        plan["zdarzenia_do"] = self.od
        return self.zadanie("PUT", "/plan", plan)


class Posrednik:
    """Posrednik TCP na 127.0.0.1 symulujacy siec: awaria (zerwanie od razu), gubienie odpowiedzi,
    zapis calego ruchu w obie strony."""

    def __init__(self, cel_port):
        self.cel_port = cel_port
        self.awaria = False
        self.p_zrywania = 0.0
        self.zapis = bytearray()
        self._blok = threading.Lock()
        self._rng = random.Random(11)
        self._gn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._gn.bind(("127.0.0.1", 0))
        self._gn.listen(32)
        self.port = self._gn.getsockname()[1]
        self._stop = False
        self._w = threading.Thread(target=self._petla, daemon=True)
        self._w.start()

    def _petla(self):
        while not self._stop:
            try:
                kl, _ = self._gn.accept()
            except OSError:
                return
            threading.Thread(target=self._obsluz, args=(kl,), daemon=True).start()

    def _zapisz(self, b):
        with self._blok:
            self.zapis.extend(b)

    def _obsluz(self, kl):
        try:
            if self.awaria:
                kl.close()
                return
            zrywaj = self._rng.random() < self.p_zrywania
            up = socket.create_connection(("127.0.0.1", self.cel_port), timeout=30)
            kl.settimeout(30)

            def do_gory():
                try:
                    while True:
                        b = kl.recv(65536)
                        if not b:
                            break
                        self._zapisz(b)
                        up.sendall(b)
                except OSError:
                    pass

            t = threading.Thread(target=do_gory, daemon=True)
            t.start()
            odp = bytearray()
            try:
                while True:
                    b = up.recv(65536)
                    if not b:
                        break
                    odp.extend(b)
            except OSError:
                pass
            if not zrywaj and not self.awaria:
                self._zapisz(bytes(odp))
                kl.sendall(bytes(odp))
            up.close()
            kl.close()
        except OSError:
            try:
                kl.close()
            except OSError:
                pass

    def zamknij(self):
        self._stop = True
        self._gn.close()


def czekaj_na(warunek, timeout=3.0, krok=0.003):
    koniec = time.monotonic() + timeout
    while time.monotonic() < koniec:
        if warunek():
            return True
        time.sleep(krok)
    return warunek()


# ----------------------------------------------------------------------------- K1: matryca 64 x 64

def test_k1_plan_porannej_24_gniazda_piksel_po_pikselu(kal):
    """Plan plytki porannej - wszystkie 24 id ukladu `poranna` (23 gniazda + rynienka)."""
    ids = sorted(int(i) for i in kal["ramki"]["P"]["poranna"]["gniazda"])
    assert len(ids) == 24
    przyp = {}
    for i in ids:
        if i == 1:
            przyp[i] = ("bialy", None)
        elif i in (2, 3, 4, 5):
            przyp[i] = ("zielony", "3263")
        elif i == 6:
            przyp[i] = ("czerwony", None)
        elif i == 7:
            przyp[i] = ("bursztyn", "3263")
        else:
            przyp[i] = ("zielony", "3301" if i % 2 else "3302")
    log = LogikaRamki("P", teraz=0.0)
    log.kontakt(LAPTOP, 0.0)
    plan = {"protokol": 1, "plan_id": "k1", "wersja": 1, "start_id": log.start_id, "zdarzenia_do": log.nr,
            "wazny_s": 600, "tryb": "rano",
            "plytki": {"4": {"uklad": "poranna", "gniazda": gniazda(kal, "P", "poranna", przyp)}},
            "kuwety": [{"kuweta": "3263", "prac": 5, "plytki": [4]},
                       {"kuweta": "3301", "prac": 9, "plytki": [4]},
                       {"kuweta": "3302", "prac": 8, "plytki": [4]}]}
    assert log.przyjmij_plan(plan, LAPTOP, 0.0)["wynik"] == "przyjety"
    log.ustaw_plytke(4, 0.1)
    k = log.obraz(0.2)
    assert (k.szerokosc, k.wysokosc) == (64, 64)
    swieci = {1, 2, 3, 4, 5, 6, 7}
    assert porownaj_obszar_plytki(k, oczekiwane_piksele(plan, 4, swieci)) == []
    # Enter: kuweta 3263 potwierdzona -> swieci nastepna (3301) + nieznana + czerwona
    log.klawisz("enter", 0.3)
    k2 = log.obraz(0.4)
    swieci2 = {1, 6} | {i for i in ids if i >= 8 and i % 2}
    assert porownaj_obszar_plytki(k2, oczekiwane_piksele(plan, 4, swieci2)) == []


def test_k1_plan_wieczorny_wszystkie_bloki_reszta_ciemna(kal):
    log = logika_z_planem(kal, plan_wieczor, rola="W", plytka=2)
    plan = plan_wieczor(kal, log)
    k = log.obraz(0.2)
    ids = {g["id"] for g in plan["plytki"]["2"]["gniazda"]}
    assert len(ids) == 19
    assert porownaj_obszar_plytki(k, oczekiwane_piksele(plan, 2, ids)) == []
    # poza obszarem plytki swieci tylko margines (pierscien, tekst, ikona) - nic z kolorow gniazd
    x0, y0, w, h = obraz.OBSZAR_PLYTKI
    for (x, y) in k.zapalone():
        assert not (x0 <= x < x0 + w and y0 <= y < y0 + h) or (x, y) in oczekiwane_piksele(plan, 2, ids)


def test_k1_przez_siec_i_atrape(kal, ramka_p):
    prog, atrapa, port = ramka_p
    lap = Laptop(port)
    lap.stan()
    lap.dobierz()
    st, odp = lap.wyslij_plan(plan_rano(kal))
    assert st == 200 and odp["wynik"] == "przyjety", odp
    atrapa.poloz_plytke(4)
    plan = plan_rano(kal)
    ocz = oczekiwane_piksele(plan, 4, {1, 2, 3, 4, 10})
    assert atrapa.czekaj(lambda a: a.klatka is not None and porownaj_obszar_plytki(a.klatka, ocz) == [], 2.0)


# ----------------------------------------------------------------------------- K2: margines

def test_k2_margines_numer_kuwety_i_liczba_prac(kal):
    log = logika_z_planem(kal)
    k = log.obraz(0.2)
    tekst = "3263 3"  # kuweta 3263, 3 prace na tej plytce (gniazda 2, 3, 4)
    ocz = tekst_ref(tekst, x_tekstu_przod(tekst), obraz.TEKST_Y, obraz.KOLOR_TEKSTU)
    assert tekst_przod(k) == ocz
    # kuweta lezy tez na plytce 5 -> prawy margines pokazuje "5"
    prawy = region(k, obraz.PRAWY_X, obraz.PRAWY_Y0, czcionka.SZER, czcionka.WYS)
    assert prawy == tekst_ref("5", obraz.PRAWY_X, obraz.PRAWY_Y0, obraz.KOLOR_TEKSTU)


def test_k2_wpisywane_cyfry_i_nieznana_kuweta(kal):
    log = logika_z_planem(kal)
    log.klawisz("3", 1.0)
    log.klawisz("2", 1.1)
    t = "32_"
    assert tekst_przod(log.obraz(1.2)) == tekst_ref(t, x_tekstu_przod(t), obraz.TEKST_Y, obraz.KOLOR_TEKSTU)
    log.klawisz("backspace", 1.3)
    log.klawisz("backspace", 1.4)
    for c in "7777":
        log.klawisz(c, 1.5)
    log.klawisz("enter", 1.6)
    t2 = "?7777"
    assert tekst_przod(log.obraz(1.7)) == tekst_ref(t2, x_tekstu_przod(t2), obraz.TEKST_Y, obraz.KOLOR_TEKSTU)
    # po czasie komunikatu wraca biezaca kuweta
    t3 = "3263 3"
    assert tekst_przod(log.obraz(9.0)) == tekst_ref(t3, x_tekstu_przod(t3), obraz.TEKST_Y, obraz.KOLOR_TEKSTU)


def test_k2_czcionka_cyfry_rozne_i_rozmiar():
    wzory = set()
    for z in "0123456789":
        g = czcionka.glif(z)
        assert len(g) == czcionka.WYS and all(len(w) == czcionka.SZER for w in g)
        wzory.add(g)
    assert len(wzory) == 10
    for z in "#-?_ BRAKOLD":
        assert czcionka.glif(z)


def test_k2_brak_kuwet_na_plytce_pokazuje_ok_albo_braki(kal):
    log = logika_z_planem(kal, braki=())
    for _ in range(5):
        log.klawisz("enter", 1.0)
    assert log.biezaca_kuweta() is None
    assert tekst_przod(log.obraz(1.1)) == tekst_ref("OK", x_tekstu_przod("OK"), obraz.TEKST_Y, obraz.KOLOR_TEKSTU)
    log2 = logika_z_planem(kal)  # braki ["5120"]
    for _ in range(5):
        log2.klawisz("enter", 1.0)
    t = "-5120"
    assert tekst_przod(log2.obraz(1.1)) == tekst_ref(t, x_tekstu_przod(t), obraz.TEKST_Y, obraz.KOLOR_TEKSTU)


# ----------------------------------------------------------------------------- K3: klawiatura

def typy_kuwety(zdarzenia):
    return [(z["typ"], z.get("kuweta")) for z in zdarzenia
            if z["typ"] in ("potwierdzenie", "cofniecie", "kuweta_wybrana", "kuweta_nieznana", "zamknij_piec")]


def test_k3_sekwencja_klawiszy_daje_dokladna_liste_zdarzen(kal):
    log = logika_z_planem(kal)
    start = log.nr
    for k in ["enter", "enter", "enter", "backspace", "3", "9", "9", "9", "enter"]:
        log.klawisz(k, 1.0)
    zd, utracone = log.zdarzenia_od(start)
    assert utracone == 0
    assert typy_kuwety(zd) == [("potwierdzenie", "3263"), ("potwierdzenie", "3301"), ("potwierdzenie", "0412"),
                               ("cofniecie", "0412"), ("kuweta_wybrana", "3999")]
    assert all(z["plan_id"] == "2026-11-17-p1" and z["plytka"] == 4 for z in zd)
    assert [z["nr"] for z in zd] == list(range(start + 1, start + 6))
    assert log.biezaca_kuweta() == "3999"
    log.klawisz("enter", 1.1)
    log.klawisz("zamknij_piec", 1.2)
    zd2, _ = log.zdarzenia_od(start + 5)
    assert typy_kuwety(zd2) == [("potwierdzenie", "3999"), ("zamknij_piec", None)]


def test_k3_wpisany_numer_dopasowanie_prywatne_zera_i_inna_plytka(kal):
    log = logika_z_planem(kal)
    start = log.nr
    for k in ["1", "2", "3", "4", "enter", "4", "1", "2", "enter", "4", "1", "0", "0", "enter"]:
        log.klawisz(k, 1.0)
    zd, _ = log.zdarzenia_od(start)
    assert typy_kuwety(zd) == [("kuweta_wybrana", "#1234"), ("kuweta_wybrana", "0412"), ("kuweta_wybrana", "4100")]
    # 4100 lezy tylko na plytce 5: na plytce 4 nic z niej nie swieci, prawy margines pokazuje 5
    k = log.obraz(1.1)
    plan = plan_rano(kal, log)
    assert porownaj_obszar_plytki(k, oczekiwane_piksele(plan, 4, {1, 10})) == []
    assert region(k, obraz.PRAWY_X, obraz.PRAWY_Y0, czcionka.SZER, czcionka.WYS) == \
        tekst_ref("5", obraz.PRAWY_X, obraz.PRAWY_Y0, obraz.KOLOR_TEKSTU)
    # Enter na kuwecie spoza plytki: brak potwierdzenia, powrot do kolejnosci
    n = log.nr
    log.klawisz("enter", 1.2)
    assert log.nr == n and log.biezaca_kuweta() == "3263"


def test_k3_klawisze_bez_planu_albo_bez_plytki_i_w_ramce_wieczornej(kal):
    log = LogikaRamki("P", teraz=0.0)
    n = log.nr
    for k in ["enter", "backspace", "1", "enter"]:
        log.klawisz(k, 0.5)
    assert log.nr == n
    log.klawisz("zamknij_piec", 0.6)
    zd, _ = log.zdarzenia_od(n)
    assert [(z["typ"], z["plan_id"]) for z in zd] == [("zamknij_piec", None)]
    w = LogikaRamki("W", teraz=0.0)
    n = w.nr
    for k in ["enter", "zamknij_piec", "5"]:
        w.klawisz(k, 0.1)
    assert w.nr == n


def test_k3_przez_siec_z_atrapa_klawiatury(kal, ramka_p):
    prog, atrapa, port = ramka_p
    lap = Laptop(port)
    lap.stan()
    atrapa.poloz_plytke(4)
    assert czekaj_na(lambda: prog.logika.plytka == 4)
    lap.dobierz()
    st, odp = lap.wyslij_plan(plan_rano(kal))
    assert st == 200, odp
    start = lap.od
    for k in ["enter", "enter", "enter", "backspace", "3", "9", "9", "9", "enter"]:
        atrapa.nacisnij(k)
    assert czekaj_na(lambda: prog.logika.nr >= start + 5)
    lap.dobierz()
    zd = [z for z in lap.zdarzenia if z["nr"] > start]
    assert typy_kuwety(zd) == [("potwierdzenie", "3263"), ("potwierdzenie", "3301"), ("potwierdzenie", "0412"),
                               ("cofniecie", "0412"), ("kuweta_wybrana", "3999")]


# ----------------------------------------------------------------------------- K4: zmiana plytki

def test_k4_zmiana_plytki_4_0_5_ponizej_100_ms_i_zdarzenia(kal, ramka_p):
    prog, atrapa, port = ramka_p
    lap = Laptop(port)
    lap.stan()
    p4 = {i: ("zielony", None) for i in range(1, 13)}
    p5 = {i: ("czerwony", None) for i in range(13, 25)}
    plan = {"protokol": 1, "plan_id": "k4", "wersja": 1, "wazny_s": 600, "tryb": "rano",
            "plytki": {"4": {"uklad": "poranna", "gniazda": gniazda(kal, "P", "poranna", p4)},
                       "5": {"uklad": "poranna", "gniazda": gniazda(kal, "P", "poranna", p5)}}}
    lap.dobierz()
    st, odp = lap.wyslij_plan(plan)
    assert st == 200, odp
    o4 = oczekiwane_piksele(plan, 4, set(p4))
    o5 = oczekiwane_piksele(plan, 5, set(p5))
    n0 = prog.logika.nr
    czasy = []
    for _ in range(10):
        for n, ocz in ((4, o4), (0, {}), (5, o5), (0, {})):
            t0 = time.monotonic()
            atrapa.poloz_plytke(n)
            ok = atrapa.czekaj(lambda a, o=ocz: a.klatka is not None and porownaj_obszar_plytki(a.klatka, o) == [], 2.0)
            czasy.append(time.monotonic() - t0)
            assert ok, f"plytka {n}: brak wlasciwego obrazu"
    assert max(czasy) < 0.100, f"najdluzsze przelaczenie {max(czasy) * 1000:.0f} ms"
    zd, _ = prog.logika.zdarzenia_od(n0)
    assert [z["plytka"] for z in zd if z["typ"] == "plytka"] == [4, 0, 5, 0] * 10
    # stary plan nie swieci pod nowa plytka: klatka wyswietlana 100 ms po polozeniu plytki 5
    # (ostatnia wyslana do matrycy do tej chwili) nie ma pikseli planu plytki 4
    assert len(atrapa.zmiany_plytki) == 40
    sprawdzone = 0
    for c, n in atrapa.zmiany_plytki:
        if n != 5:
            continue
        klatki_do = [k for czas, _, k in atrapa.historia if czas <= c + 0.100]
        assert klatki_do
        assert not (set(piksele_plytki(klatki_do[-1])) & set(o4)), "plan plytki 4 swieci pod plytka 5"
        assert porownaj_obszar_plytki(klatki_do[-1], o5) == []
        sprawdzone += 1
    assert sprawdzone == 10


def test_zmiana_plytki_w_logice_od_razu_bez_starego_planu(kal):
    log = logika_z_planem(kal)
    plan = plan_rano(kal, log)
    assert porownaj_obszar_plytki(log.obraz(0.2), oczekiwane_piksele(plan, 4, {1, 2, 3, 4, 10})) == []
    log.ustaw_plytke(5, 0.3)
    assert porownaj_obszar_plytki(log.obraz(0.3), oczekiwane_piksele(plan, 5, {13, 14, 20})) == []
    log.ustaw_plytke(0, 0.4)
    assert piksele_plytki(log.obraz(0.4)) == {}


def test_plytka_bez_planu_pokazuje_brak_planu(kal):
    log = logika_z_planem(kal, plytka=6)
    k = log.obraz(0.2)
    assert piksele_plytki(k) == {}
    t = "6 BRAK"
    assert tekst_przod(k) == tekst_ref(t, x_tekstu_przod(t), obraz.TEKST_Y, obraz.KOLOR_TEKSTU)
    assert k.piksel(32, 0) == obraz.KOLORY_STANU["brak_planu"]
    # ramka bez zadnego planu
    log2 = LogikaRamki("P", teraz=0.0)
    log2.kontakt(LAPTOP, 0.0)
    log2.ustaw_plytke(4, 0.1)
    k2 = log2.obraz(0.2)
    assert piksele_plytki(k2) == {}
    assert tekst_przod(k2) == tekst_ref("4 BRAK", x_tekstu_przod("4 BRAK"), obraz.TEKST_Y, obraz.KOLOR_TEKSTU)


def test_usun_po_zdjeciu_plytka_nie_wraca_ze_starym_planem(kal):
    log = LogikaRamki("W", teraz=0.0)
    log.kontakt(LAPTOP, 0.0)
    plan = plan_wieczor(kal, log)
    plan["plytki"]["2"]["usun_po_zdjeciu"] = True
    log.przyjmij_plan(plan, LAPTOP, 0.0)
    log.ustaw_plytke(2, 0.1)
    assert len(piksele_plytki(log.obraz(0.2))) > 0
    log.ustaw_plytke(0, 0.3)
    log.ustaw_plytke(2, 0.4)
    assert piksele_plytki(log.obraz(0.5)) == {}
    assert log.stan(0.5)["plytki_planu"] == []


# ----------------------------------------------------------------------------- brak planu / zgas / tryby

def test_zgas_delete_i_blokada_skanu_nic_nie_swieci(kal, ramka_w):
    prog, atrapa, port = ramka_w
    lap = Laptop(port)
    lap.stan()
    lap.dobierz()
    atrapa.poloz_plytke(2)
    assert lap.wyslij_plan(plan_wieczor(kal))[0] == 200
    assert atrapa.czekaj(lambda a: a.klatka is not None and len(piksele_plytki(a.klatka)) > 0, 2.0)
    # skan zablokowany (plytka niezgodna z trybem): laptop wysyla stan "blad" -> zero gniazd
    st, odp = lap.zadanie("PUT", "/tryb", {"protokol": 1, "stan": "blad"})
    assert st == 200, odp
    assert atrapa.czekaj(lambda a: piksele_plytki(a.klatka) == {}, 2.0)
    t = "BLAD"
    assert atrapa.czekaj(lambda a: tekst_przod(a.klatka) == tekst_ref(t, x_tekstu_przod(t), obraz.TEKST_Y,
                                                                      obraz.KOLOR_TEKSTU), 2.0)
    # wynik ponownie, potem DELETE /plan = zgas
    assert lap.zadanie("PUT", "/tryb", {"protokol": 1, "stan": "wynik"})[0] == 200
    assert atrapa.czekaj(lambda a: len(piksele_plytki(a.klatka)) > 0, 2.0)
    st, odp = lap.zadanie("DELETE", "/plan?plan_id=2026-11-17-w")
    assert st == 200 and odp["wynik"] == "usuniety"
    assert atrapa.czekaj(lambda a: piksele_plytki(a.klatka) == {}, 2.0)
    st, odp = lap.zadanie("DELETE", "/plan")
    assert st == 200 and odp["wynik"] == "brak_planu"
    assert lap.stan()["plan_id"] is None


def test_skanowanie_i_analiza_gasza_gniazda_plan_zostaje(kal):
    log = logika_z_planem(kal, plan_wieczor, rola="W", plytka=2)
    assert len(piksele_plytki(log.obraz(0.2))) > 0
    for stan, kolor in (("skanowanie", "zolty"), ("analiza", "fioletowy"), ("gotowa", "niebieski")):
        log.ustaw_tryb({"protokol": 1, "stan": stan}, LAPTOP, 0.3)
        k = log.obraz(0.3)
        assert piksele_plytki(k) == {}
        assert k.piksel(32, 0) == obraz.KOLORY_STANU[stan], stan
    assert log.stan(0.3)["plan_id"] == "2026-11-17-w"


def test_tryb_test_led_cala_matryca(kal):
    log = LogikaRamki("W", teraz=0.0)
    log.kontakt(LAPTOP, 0.0)
    log.ustaw_tryb({"protokol": 1, "stan": "test_led"}, LAPTOP, 10.0)
    kolory = []
    for t in (10.1, 11.1, 12.1, 13.1):
        k = log.obraz(t)
        z = k.zapalone()
        assert len(z) == 64 * 64
        assert len(set(z.values())) == 1
        kolory.append(next(iter(z.values())))
    assert len(set(kolory)) == 4


# ----------------------------------------------------------------------------- K5: utrata sieci

def plan_k5(kal_, wersja):
    kuw = ["5001", "5002", "5003", "5004", "5005", "5006"]
    przyp = {2 + n: ("zielony", k) for n, k in enumerate(kuw)}
    return {"protokol": 1, "plan_id": "k5", "wersja": wersja, "wazny_s": 3600, "tryb": "rano",
            "plytki": {"4": {"uklad": "poranna", "gniazda": gniazda(kal_, "P", "poranna", przyp)}},
            "kuwety": [{"kuweta": k, "prac": 1, "plytki": [4]} for k in kuw]}


def test_k5_utrata_sieci_5_potwierdzen_100_powtorzen(kal, ramka_p):
    prog, atrapa, port = ramka_p
    proxy = Posrednik(port)
    lap = Laptop(proxy.port)
    rng = random.Random(5)
    try:
        lap.stan()
        atrapa.poloz_plytke(4)
        assert czekaj_na(lambda: prog.logika.plytka == 4)
        nieudane_odpytania = 0
        for rep in range(100):
            proxy.awaria, proxy.p_zrywania = False, 0.0
            lap.dobierz()
            st, odp = lap.wyslij_plan(plan_k5(kal, rep + 1))
            assert st == 200, odp
            proxy.awaria = True
            n0 = prog.logika.nr
            for _ in range(5):
                atrapa.nacisnij("enter")
            assert czekaj_na(lambda: prog.logika.nr >= n0 + 5)
            for _ in range(rng.randint(1, 3)):
                with pytest.raises(BLEDY_SIECI):
                    lap.odpytaj(0.0)
                nieudane_odpytania += 1
            time.sleep(rng.uniform(0.0, 0.02))
            proxy.awaria, proxy.p_zrywania = False, 0.3
            przed = len(lap.zdarzenia)
            for _ in range(300):
                if len(lap.zdarzenia) - przed >= 5:
                    break
                try:
                    lap.odpytaj(rng.choice([0.0, 0.05]))
                except BLEDY_SIECI:
                    nieudane_odpytania += 1
            nowe = lap.zdarzenia[przed:]
            assert [(z["typ"], z["kuweta"]) for z in nowe] == \
                [("potwierdzenie", k) for k in ["5001", "5002", "5003", "5004", "5005"]], f"powtorzenie {rep}"
        nry = [z["nr"] for z in lap.zdarzenia]
        assert nry == list(range(1, len(nry) + 1)), "luka albo powtorka w numeracji zdarzen"
        assert nieudane_odpytania >= 100
    finally:
        proxy.zamknij()


# ----------------------------------------------------------------------------- K6: restart ramki

def test_k6_restart_ramki_laptop_wysyla_plan_ponownie_do_5_s(kal):
    prog, atrapa, port = uruchom("P")
    stop = threading.Event()
    lap = Laptop(port)
    wyslane = []

    def petla_laptopa():
        znany = None
        while not stop.is_set():
            try:
                if lap.start_id is None:
                    lap.stan()
                lap.odpytaj(0.3)
                if lap.start_id != znany:
                    st, _ = lap.wyslij_plan(plan_rano(kal, wersja=len(wyslane) + 1))
                    if st == 200:
                        znany = lap.start_id
                        wyslane.append(time.monotonic())
            except BLEDY_SIECI:
                time.sleep(0.05)

    w = threading.Thread(target=petla_laptopa, daemon=True)
    w.start()
    prog2 = None
    try:
        assert czekaj_na(lambda: prog.logika.plan is not None, 5.0)
        stary_start = prog.logika.start_id
        t0 = time.monotonic()
        prog.zatrzymaj()
        prog2, _, _ = uruchom("P", port=port, sprzet=atrapa)
        assert prog2.logika.start_id != stary_start
        assert czekaj_na(lambda: prog2.logika.plan is not None, 6.0)
        dt = time.monotonic() - t0
        assert dt < 5.0, f"plan po restarcie po {dt:.2f} s"
    finally:
        stop.set()
        w.join(5)
        if prog2:
            prog2.zatrzymaj()


def test_restart_programu_nowy_start_id_i_zdarzenia_od_poczatku(kal):
    prog, atrapa, port = uruchom("P")
    lap = Laptop(port)
    try:
        lap.stan()
        lap.dobierz()
        assert lap.wyslij_plan(plan_rano(kal))[0] == 200
        atrapa.poloz_plytke(4)
        assert czekaj_na(lambda: prog.logika.plytka == 4)
        lap.dobierz()
        stary = lap.start_id
        prog.zatrzymaj()
        prog, _, _ = uruchom("P", port=port, sprzet=atrapa)
        assert czekaj_na(lambda: prog.logika.plytka == 4)
        # plan z poprzedniego startu -> 409 inny_start; plan po restarcie jest pusty (RAM)
        st, odp = lap.wyslij_plan(plan_rano(kal, wersja=2))
        assert st == 409 and odp["blad"]["kod"] == "inny_start"
        assert lap.zadanie("GET", "/stan")[1]["plan_id"] is None
        # odpytanie ze starym start_id -> zdarzenia od poczatku nowego startu
        st, odp = lap.zadanie("GET", f"/zdarzenia?od={lap.od}&start_id={stary}")
        assert st == 200 and odp["restart"] is True and odp["start_id"] != stary
        assert odp["zdarzenia"][0]["nr"] == 1 and odp["zdarzenia"][0]["typ"] == "start"
        assert [z["typ"] for z in odp["zdarzenia"]][:2] == ["start", "plytka"]
    finally:
        prog.zatrzymaj()


# ----------------------------------------------------------------------------- K7: Spacja -> stan ramki W

def test_k7_spacja_zmienia_stan_ramki_w_ponizej_1_s_dwa_procesy(tmp_path):
    """Ramka W jako osobny proces (narzedzia/atrapa_ramki.py), laptop = proces testu."""
    narz = STANOWISKO / "narzedzia" / "atrapa_ramki.py"
    err = open(tmp_path / "atrapa_stderr.txt", "w", encoding="utf-8")
    p = subprocess.Popen([sys.executable, str(narz), "--rola", "W", "--port", "0", "--sterowanie"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=err,
                         cwd=str(STANOWISKO), text=True)
    try:
        linia = p.stdout.readline()
        assert linia.startswith("ATRAPA_RAMKI "), linia + (tmp_path / "atrapa_stderr.txt").read_text()
        port = int(dict(x.split("=") for x in linia.split()[1:])["port"])
        lap = Laptop(port)
        lap.stan()
        czasy = []

        def kolor_pierscienia():
            st, odp = lap.zadanie("GET", "/atrapa/klatka")
            assert st == 200
            k = obraz.Klatka.z_hex(odp["piksele_hex"])
            return k.piksel(32, 0)

        for i in range(10):
            stan = "skanowanie" if i % 2 == 0 else "gotowa"
            t0 = time.monotonic()
            st, odp = lap.zadanie("PUT", "/tryb", {"protokol": 1, "stan": stan})
            assert st == 200, odp
            assert czekaj_na(lambda s=stan: kolor_pierscienia() == obraz.KOLORY_STANU[s], 2.0, 0.005)
            czasy.append(time.monotonic() - t0)
        assert max(czasy) < 1.0, f"najdluzej {max(czasy):.3f} s"
    finally:
        try:
            p.stdin.close()
        except OSError:
            pass
        try:
            p.wait(10)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait(5)
        err.close()
    assert p.returncode == 0


# ----------------------------------------------------------------------------- K8: dane osobowe

DOZWOLONE_SLOWA = set(protokol.KOLORY_GNIAZD) | set(protokol.STANY) | {
    "rano", "wieczor", "liczba", "numer", "reczna", "P", "W", "przyjety", "powtorzony", "usuniety",
    "brak_planu", "poranna", "wieczorna", "start", "plytka", "potwierdzenie", "cofniecie",
    "kuweta_wybrana", "kuweta_nieznana", "zamknij_piec", "plan_wygasl", LAPTOP}


def _napisy(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from _napisy(v)
    elif isinstance(o, list):
        for v in o:
            yield from _napisy(v)


def test_k8_ruch_sieciowy_testow_bez_nazw_folderow(kal, ramka_p, caplog):
    caplog.set_level(logging.DEBUG)
    prog, atrapa, port = ramka_p
    proxy = Posrednik(port)
    try:
        lap = Laptop(proxy.port)
        # laptop zna nazwy folderow (FOLDERY), ale plan buduje z numerow kuwet
        assert set(FOLDERY) >= {k["kuweta"] for k in plan_rano(kal)["kuwety"]}
        lap.stan()
        lap.dobierz()
        assert lap.wyslij_plan(plan_rano(kal))[0] == 200
        atrapa.poloz_plytke(4)
        assert czekaj_na(lambda: prog.logika.plytka == 4)
        for k in ["enter", "1", "2", "3", "4", "enter", "backspace", "zamknij_piec"]:
            atrapa.nacisnij(k)
        assert czekaj_na(lambda: prog.logika.nr >= 6)
        lap.dobierz()
        lap.zadanie("PUT", "/tryb", {"protokol": 1, "stan": "gotowa"})
        lap.zadanie("DELETE", "/plan")
        lap.zadanie("GET", "/stan")
    finally:
        proxy.zamknij()
    ruch = bytes(proxy.zapis).decode("utf-8", "replace")
    assert len(ruch) > 1000
    for nazwa in list(FOLDERY.values()) + list(NAZWISKA):
        assert nazwa.lower() not in ruch.lower()
    # kazdy napis w JSON w obie strony: numer kuwety, identyfikator albo slowo protokolu
    import re
    wzor_ok = re.compile(r"^(#?[0-9]{1,6}|[0-9a-f]{4,32}|[A-Za-z0-9._-]{1,40}|0\.1\.[0-9]+|)$")
    for kawalek in re.findall(r"\{.*\}", ruch):
        try:
            dane = json.loads(kawalek)
        except ValueError:
            continue
        for s in _napisy(dane):
            if s in DOZWOLONE_SLOWA:
                continue
            assert wzor_ok.match(s) and not any(n.lower() in s.lower() for n in NAZWISKA), s
    logi = caplog.text
    for nazwa in NAZWISKA:
        assert nazwa.lower() not in logi.lower()


def test_k8_ramka_odrzuca_nazwy_i_nie_powtarza_ich_w_odpowiedzi_ani_logu(kal, ramka_p, caplog):
    caplog.set_level(logging.DEBUG)
    prog, atrapa, port = ramka_p
    lap = Laptop(port)
    lap.stan()
    plan = plan_rano(kal)
    plan["kuwety"][0]["kuweta"] = FOLDERY["3263"]
    st, odp = lap.wyslij_plan(plan)
    assert st == 400 and odp["blad"]["kod"] == "zla_kuweta"
    plan2 = plan_rano(kal)
    plan2["folder"] = FOLDERY["3301"]
    st2, odp2 = lap.wyslij_plan(plan2)
    assert st2 == 400 and odp2["blad"]["kod"] == "nieznane_pole"
    plan3 = plan_rano(kal)
    plan3[FOLDERY["0412"]] = 1
    st3, odp3 = lap.wyslij_plan(plan3)
    assert st3 == 400 and odp3["blad"]["kod"] == "nieznane_pole"
    st4, odp4 = lap.zadanie("GET", "/" + "Lewandowski")
    assert st4 == 404
    tekst = json.dumps([odp, odp2, odp3, odp4]) + caplog.text
    for nazwa in NAZWISKA:
        assert nazwa.lower() not in tekst.lower()


# ----------------------------------------------------------------------------- K9: tylko biblioteka standardowa

def test_k9_ramka_w_trybie_atrapy_importuje_tylko_biblioteke_standardowa():
    skrypt = (
        "import sys\n"
        f"sys.path.insert(0, {str(STANOWISKO)!r})\n"
        "import json, http.client\n"
        "from ramka import czcionka, obraz, protokol, logika, sprzet, sprzet_atrapa, serwer, program, "
        "kalibracja, test_led\n"
        "import ramka.__main__\n"
        "from ramka.program import Konfiguracja, ProgramRamki\n"
        "p = ProgramRamki(Konfiguracja(rola='P', host='127.0.0.1', port=0), sprzet=sprzet_atrapa.SprzetAtrapa())\n"
        "h, port = p.uruchom()\n"
        "c = http.client.HTTPConnection('127.0.0.1', port, timeout=10)\n"
        "c.request('GET', '/stan'); assert c.getresponse().status == 200\n"
        "p.zatrzymaj()\n"
        "std = set(sys.stdlib_module_names) | {'ramka', '__main__', '__mp_main__'}\n"
        "obce = sorted({m.split('.')[0] for m in sys.modules} - std)\n"
        "print('OBCE=' + ','.join(obce))\n"
        "assert 'ramka.sprzet_rpi' not in sys.modules\n"
    )
    r = subprocess.run([sys.executable, "-I", "-S", "-c", skrypt], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    assert "OBCE=\n" in r.stdout or r.stdout.strip() == "OBCE=", r.stdout


# ----------------------------------------------------------------------------- wygasniecie planu

def test_wygasniecie_planu_po_utracie_lacznosci(kal):
    log = logika_z_planem(kal, plan_wieczor, rola="W", plytka=2, wazny_s=10.0)
    log.tick(9.0)
    assert len(piksele_plytki(log.obraz(9.0))) > 0
    log.kontakt(LAPTOP, 8.0)
    log.tick(17.5)
    assert log.plan is not None, "kontakt w 8 s przedluza waznosc do 18 s"
    n = log.nr
    log.tick(18.5)
    assert log.plan is None
    k = log.obraz(18.5)
    assert piksele_plytki(k) == {}
    assert tekst_przod(k) == tekst_ref("2 BRAK", x_tekstu_przod("2 BRAK"), obraz.TEKST_Y, obraz.KOLOR_TEKSTU)
    zd, _ = log.zdarzenia_od(n)
    assert [(z["typ"], z["plan_id"]) for z in zd] == [("plan_wygasl", "2026-11-17-w")]


def test_ramka_poranna_bez_sieci_trzyma_plan_do_limitu(kal):
    """I1: bez sieci ramka poranna trzyma plan (wazny_s z planu), pokazujac brak lacznosci."""
    log = logika_z_planem(kal, wazny_s=600.0)
    k = log.obraz(100.0)  # 100 s bez kontaktu, limit lacznosci 30 s
    assert log.plan is not None
    plan = plan_rano(kal, log)
    assert porownaj_obszar_plytki(k, oczekiwane_piksele(plan, 4, {1, 2, 3, 4, 10})) == []
    assert log.stan(100.0)["lacznosc"] is False
    ikona = obraz.IKONA
    assert k.piksel(ikona[0], ikona[1]) == obraz.KOLORY_STANU["brak_lacznosci"]
    pierscienie = {log.obraz(100.0 + d).piksel(32, 0) for d in (0.0, 0.5)}
    assert pierscienie == {obraz.KOLORY_STANU["brak_lacznosci"], CZARNY}  # miganie
    log.tick(601.0)
    assert log.plan is None


def test_wygasniecie_przez_siec_z_atrapa(kal, ramka_w):
    prog, atrapa, port = ramka_w
    lap = Laptop(port)
    lap.stan()
    lap.dobierz()
    atrapa.poloz_plytke(2)
    assert lap.wyslij_plan(plan_wieczor(kal, wazny_s=1.0))[0] == 200
    assert atrapa.czekaj(lambda a: a.klatka is not None and len(piksele_plytki(a.klatka)) > 0, 2.0)
    assert atrapa.czekaj(lambda a: piksele_plytki(a.klatka) == {}, 3.0)
    odp = lap.stan()
    assert odp["plan_id"] is None
    lap.dobierz()
    assert "plan_wygasl" in [z["typ"] for z in lap.zdarzenia]


# ----------------------------------------------------------------------------- powtorzony / spozniony plan

def test_powtorzony_spozniony_i_nieaktualny_plan(kal):
    log = logika_z_planem(kal)
    log.klawisz("enter", 1.0)  # potwierdzenie 3263 na plytce 4
    n_po = log.nr
    # ten sam plan (ta sama wersja i tresc) -> powtorzony, stan bez zmian
    p1 = plan_rano(kal, log)
    p1["zdarzenia_do"] = 0
    odp = log.przyjmij_plan(p1, LAPTOP, 1.1)
    assert odp["wynik"] == "powtorzony"
    assert log.biezaca_kuweta() == "3301"
    # nowa wersja oparta na nieodebranych zdarzeniach -> 409
    p2 = plan_rano(kal, log, wersja=2)
    p2["zdarzenia_do"] = n_po - 1
    with pytest.raises(protokol.BladProtokolu) as e:
        log.przyjmij_plan(p2, LAPTOP, 1.2)
    assert (e.value.status, e.value.kod) == (409, "zdarzenia_nieodebrane")
    # nowa wersja z potwierdzeniem odebranym -> przyjeta
    p3 = plan_rano(kal, log, wersja=2, potwierdzone=[[4, "3263"]])
    assert log.przyjmij_plan(p3, LAPTOP, 1.3)["wynik"] == "przyjety"
    assert log.biezaca_kuweta() == "3301"
    # spozniony plan (starsza wersja) -> 409 plan_starszy
    with pytest.raises(protokol.BladProtokolu) as e:
        log.przyjmij_plan(plan_rano(kal, log, wersja=1), LAPTOP, 1.4)
    assert (e.value.status, e.value.kod) == (409, "plan_starszy")
    # ta sama wersja, inna tresc -> 409 konflikt_wersji
    p4 = plan_rano(kal, log, wersja=2, potwierdzone=[[4, "3263"]], braki=("9999",))
    with pytest.raises(protokol.BladProtokolu) as e:
        log.przyjmij_plan(p4, LAPTOP, 1.5)
    assert (e.value.status, e.value.kod) == (409, "konflikt_wersji")
    # zly start_id -> 409 inny_start
    p5 = plan_rano(kal, log, wersja=3)
    p5["start_id"] = "deadbeef"
    with pytest.raises(protokol.BladProtokolu) as e:
        log.przyjmij_plan(p5, LAPTOP, 1.6)
    assert (e.value.status, e.value.kod) == (409, "inny_start")
    # Backspace po przywroceniu planu cofa potwierdzenie z listy `potwierdzone`
    log.klawisz("backspace", 1.7)
    assert log.biezaca_kuweta() == "3263"


def test_spozniony_plan_po_wygasnieciu_i_spozniony_delete(kal):
    log = logika_z_planem(kal, wazny_s=5.0)
    log.przyjmij_plan(plan_rano(kal, log, wersja=2, wazny_s=5.0), LAPTOP, 1.0)
    log.tick(10.0)
    assert log.plan is None
    log.kontakt(LAPTOP, 10.0)
    with pytest.raises(protokol.BladProtokolu) as e:
        log.przyjmij_plan(plan_rano(kal, log, wersja=1), LAPTOP, 10.0)
    assert e.value.kod == "plan_starszy"
    log.przyjmij_plan(plan_rano(kal, log, wersja=3), LAPTOP, 10.1)
    with pytest.raises(protokol.BladProtokolu) as e:
        log.usun_plan(LAPTOP, 10.2, plan_id="inny-plan")
    assert (e.value.status, e.value.kod) == (409, "inny_plan")
    assert log.plan is not None


def test_powtorzone_zadania_przez_siec(kal, ramka_p):
    prog, atrapa, port = ramka_p
    lap = Laptop(port)
    lap.stan()
    lap.dobierz()
    plan = plan_rano(kal)
    assert lap.wyslij_plan(plan)[1]["wynik"] == "przyjety"
    for _ in range(3):
        st, odp = lap.wyslij_plan(plan)
        assert st == 200 and odp["wynik"] == "powtorzony"
    for _ in range(2):
        assert lap.zadanie("PUT", "/tryb", {"protokol": 1, "stan": "wynik"})[0] == 200
    assert lap.zadanie("DELETE", "/plan")[1]["wynik"] == "usuniety"
    assert lap.zadanie("DELETE", "/plan")[1]["wynik"] == "brak_planu"


# ----------------------------------------------------------------------------- zdarzenia bez gubienia

def test_zdarzenia_klawiatury_bez_gubienia_i_powtorek_dwa_klienty_rownolegle(kal, ramka_p):
    prog, atrapa, port = ramka_p
    lap = Laptop(port)
    lap.stan()
    atrapa.poloz_plytke(4)
    assert czekaj_na(lambda: prog.logika.plytka == 4)
    lap.dobierz()
    assert lap.wyslij_plan(plan_rano(kal))[0] == 200
    start = lap.od
    N = 300
    koniec = threading.Event()
    wyniki = {}

    def klient(nazwa, seed):
        rng = random.Random(seed)
        k = Laptop(port, laptop_id=nazwa)
        k.start_id = lap.start_id
        k.od = start
        while not koniec.is_set() or k.od < start + N:
            k.odpytaj(rng.choice([0.0, 0.05, 0.3]), limit=rng.randint(1, 7))
            if k.od >= start + N:
                break
        wyniki[nazwa] = list(k.zdarzenia)

    watki = [threading.Thread(target=klient, args=(f"lap-r{i}", i), daemon=True) for i in range(2)]
    for w in watki:
        w.start()
    rng = random.Random(1)
    for i in range(N):
        atrapa.nacisnij("enter" if i % 2 == 0 else "backspace")
        if rng.random() < 0.2:
            time.sleep(0.002)
    assert czekaj_na(lambda: prog.logika.nr >= start + N, 10.0)
    koniec.set()
    for w in watki:
        w.join(30)
    assert sorted(wyniki) == ["lap-r0", "lap-r1"]
    for nazwa, zd in wyniki.items():
        assert [z["nr"] for z in zd] == list(range(start + 1, start + N + 1)), nazwa
        assert [z["typ"] for z in zd] == ["potwierdzenie", "cofniecie"] * (N // 2), nazwa


def test_dziennik_zdarzen_przepelnienie_zglasza_utracone():
    log = LogikaRamki("P", teraz=0.0, max_zdarzen=10)
    for i in range(30):
        log.ustaw_plytke(4 if i % 2 == 0 else 0, float(i))
    zd, utracone = log.zdarzenia_od(0)
    assert utracone == 21 and [z["nr"] for z in zd] == list(range(22, 32))


# ----------------------------------------------------------------------------- zle dane

def test_zle_dane_w_zadaniu(kal, ramka_p):
    prog, atrapa, port = ramka_p
    lap = Laptop(port)
    lap.stan()

    def kod(st_odp):
        st, odp = st_odp
        return st, (odp or {}).get("blad", {}).get("kod")

    def plan_z(zmien):
        p = plan_rano(kal)
        p["start_id"], p["zdarzenia_do"] = lap.start_id, 0
        zmien(p)
        return p

    def g4(p):
        return p["plytki"]["4"]["gniazda"]

    przypadki = [
        ("zly JSON", lambda: lap.zadanie("PUT", "/plan", surowa=b"{\"protokol\": 1,,}"), (400, "zly_json")),
        ("nie obiekt", lambda: lap.zadanie("PUT", "/plan", surowa=b"[1,2]"), (400, "zly_json")),
        ("nie UTF-8", lambda: lap.zadanie("PUT", "/plan", surowa=b"\xff\xfe{"), (400, "zly_json")),
        ("za duza tresc", lambda: lap.zadanie("PUT", "/plan", surowa=b" " * 100000), (413, "za_duza_tresc")),
        ("gleboki JSON", lambda: lap.zadanie("PUT", "/plan", surowa=b"[" * 30000 + b"]" * 30000), (400, "zly_json")),
        ("nieznane gniazdo 0", lambda: lap.zadanie("PUT", "/plan", plan_z(lambda p: g4(p)[0].update(id=0))),
         (400, "nieznane_gniazdo")),
        ("nieznane gniazdo 99", lambda: lap.zadanie("PUT", "/plan", plan_z(lambda p: g4(p)[0].update(id=99))),
         (400, "nieznane_gniazdo")),
        ("gniazdo tekst", lambda: lap.zadanie("PUT", "/plan", plan_z(lambda p: g4(p)[0].update(id="13"))),
         (400, "nieznane_gniazdo")),
        ("gniazdo powtorzone", lambda: lap.zadanie("PUT", "/plan", plan_z(lambda p: g4(p)[1].update(id=g4(p)[0]["id"]))),
         (400, "nieznane_gniazdo")),
        ("za duzo pikseli", lambda: lap.zadanie("PUT", "/plan", plan_z(lambda p: p["plytki"]["4"].update(gniazda=[
            {"id": i + 1, "px": [12 + 8 * (i % 5), 12 + 8 * (i // 5), 8, 8], "kolor": "bialy"} for i in range(25)]))),
         (400, "za_duzo_pikseli")),
        ("za duzo gniazd", lambda: lap.zadanie("PUT", "/plan", plan_z(lambda p: p["plytki"]["4"].update(gniazda=[
            {"id": i + 1, "px": [12 + (i % 40), 12 + 2 * (i // 40), 1, 1], "kolor": "bialy"} for i in range(60)]))),
         (400, "za_duzo_gniazd")),
        ("blok poza plytka", lambda: lap.zadanie("PUT", "/plan", plan_z(lambda p: g4(p)[0].update(px=[0, 0, 3, 3]))),
         (400, "px_poza_plytka")),
        ("blok nakladany", lambda: lap.zadanie("PUT", "/plan", plan_z(lambda p: g4(p)[1].update(px=list(g4(p)[0]["px"])))),
         (400, "px_nakladanie")),
        ("zly kolor", lambda: lap.zadanie("PUT", "/plan", plan_z(lambda p: g4(p)[0].update(kolor="rozowy"))),
         (400, "zly_kolor")),
        ("kuweta spoza listy", lambda: lap.zadanie("PUT", "/plan", plan_z(lambda p: g4(p)[0].update(kuweta="7777"))),
         (400, "nieznana_kuweta")),
        ("plytka 9", lambda: lap.zadanie("PUT", "/plan", plan_z(lambda p: p["plytki"].update({"9": p["plytki"]["5"]}))),
         (400, "zla_plytka")),
        ("plytka wieczorna w ramce P", lambda: lap.zadanie("PUT", "/plan", plan_z(
            lambda p: p["plytki"].update({"2": p["plytki"].pop("5")}))), (400, "zla_plytka")),
        ("plan wieczorny do ramki P", lambda: lap.zadanie("PUT", "/plan", plan_z(lambda p: p.update(tryb="wieczor"))),
         (409, "plan_innej_ramki")),
        ("brak pola", lambda: lap.zadanie("PUT", "/plan", plan_z(lambda p: p.pop("wazny_s"))), (400, "brak_pola")),
        ("zly protokol", lambda: lap.zadanie("PUT", "/plan", plan_z(lambda p: p.update(protokol=2))), (400, "zly_protokol")),
        ("wazny_s 0", lambda: lap.zadanie("PUT", "/plan", plan_z(lambda p: p.update(wazny_s=0))), (400, "zle_pole")),
        ("bez Content-Length", lambda: _bez_dlugosci(port), (411, "brak_dlugosci")),
        ("brak X-Laptop-Id", lambda: Laptop(port, laptop_id=None).zadanie("PUT", "/tryb", {"protokol": 1, "stan": "gotowa"}),
         (400, "brak_laptopa")),
        ("zly X-Laptop-Id", lambda: lap.zadanie("PUT", "/tryb", {"protokol": 1, "stan": "gotowa"},
                                                 naglowki={"X-Laptop-Id": "a b"}), (400, "zly_laptop")),
        ("zly stan", lambda: lap.zadanie("PUT", "/tryb", {"protokol": 1, "stan": "spi"}), (400, "zly_stan")),
        ("zly parametr od", lambda: lap.zadanie("GET", "/zdarzenia?od=-x"), (400, "zly_parametr")),
        ("nieznany zasob", lambda: lap.zadanie("GET", "/nie-ma"), (404, "nieznany_zasob")),
        ("zla metoda", lambda: lap.zadanie("POST", "/plan", {"a": 1}), (405, "zla_metoda")),
        ("atrapa bez zgody", lambda: lap.zadanie("GET", "/atrapa/klatka"), (404, "nieznany_zasob")),
    ]
    wyniki = [(nazwa, kod(f())) for nazwa, f, _ in przypadki]
    assert wyniki == [(nazwa, ocz) for nazwa, _, ocz in przypadki]
    # ramka dziala dalej i nie przyjela zadnego z tych planow
    odp = lap.stan()
    assert odp["plan_id"] is None
    lap.dobierz()
    assert lap.wyslij_plan(plan_rano(kal))[0] == 200


def _bez_dlugosci(port):
    s = socket.create_connection(("127.0.0.1", port), timeout=10)
    try:
        s.sendall(b"PUT /plan HTTP/1.0\r\nX-Laptop-Id: lap-test-1\r\n\r\n")
        dane = b""
        while True:
            b = s.recv(65536)
            if not b:
                break
            dane += b
    finally:
        s.close()
    glowa, _, tresc = dane.partition(b"\r\n\r\n")
    return int(glowa.split()[1]), json.loads(tresc.decode("utf-8"))


# ----------------------------------------------------------------------------- dwa laptopy

def test_dwa_laptopy_naraz(kal):
    prog, atrapa, port = uruchom("P", limit_lacznosci_s=1.0)
    try:
        a = Laptop(port, laptop_id="lap-a")
        b = Laptop(port, laptop_id="lap-b")
        a.stan()
        b.stan()
        a.dobierz()
        b.dobierz()
        assert a.wyslij_plan(plan_rano(kal, plan_id="plan-a", wazny_s=600))[0] == 200
        st, odp = b.wyslij_plan(plan_rano(kal, plan_id="plan-b"))
        assert st == 409 and odp["blad"]["kod"] == "inny_laptop"
        assert b.zadanie("PUT", "/tryb", {"protokol": 1, "stan": "gotowa"})[1]["blad"]["kod"] == "inny_laptop"
        assert b.zadanie("DELETE", "/plan")[1]["blad"]["kod"] == "inny_laptop"
        # odczyt wolno obu; zdarzenia dostaja obaj
        atrapa.poloz_plytke(4)
        assert czekaj_na(lambda: prog.logika.plytka == 4)
        a.dobierz()
        b.dobierz()
        assert [z["nr"] for z in a.zdarzenia] == [z["nr"] for z in b.zdarzenia]
        assert b.stan()["laptop"] == "lap-a"
        # laptop A milknie dluzej niz limit lacznosci -> B przejmuje ramke (plan A nadal wazny 600 s)
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            st, odp = b.wyslij_plan(plan_rano(kal, plan_id="plan-b"))
            if st == 200:
                break
            b.dobierz()
            time.sleep(0.1)
        assert st == 200, odp
        assert prog.logika.plan.plan_id == "plan-b"
        st, odp = a.wyslij_plan(plan_rano(kal, plan_id="plan-a", wersja=2))
        assert st == 409 and odp["blad"]["kod"] == "inny_laptop"
    finally:
        prog.zatrzymaj()


# ----------------------------------------------------------------------------- odbijanie czujnikow

def test_odbijanie_czujnikow_krotkie_zaklocenie_ignorowane():
    o = Odbijanie(0.03, poczatkowa=0)
    assert o.podaj(4, 0.000) is None
    assert o.podaj(4, 0.010) is None
    assert o.podaj(1, 0.015) is None  # zaklocenie: jeden magnes chwilowo nie dziala
    assert o.podaj(4, 0.020) is None
    assert o.podaj(4, 0.040) is None
    assert o.podaj(4, 0.051) == 4
    assert o.podaj(4, 0.060) is None
    assert o.podaj(0, 0.070) is None
    assert o.podaj(0, 0.101) == 0


# ----------------------------------------------------------------------------- kalibracja i test LED

def test_kalibracja_domyslna_z_ukladow_waliduje_sie_i_nie_zmienia_ukladow():
    przed = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in MODELE.glob("*/uklad.json")}
    kal_ = kalibracja.domyslna(MODELE)
    po = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in MODELE.glob("*/uklad.json")}
    assert przed == po
    kalibracja.sprawdz(kal_)
    ramki = kal_["ramki"]
    assert sorted(ramki["W"]) == ["wieczorna", "wieczorna_r54"]
    assert sorted(ramki["P"]) == ["poranna", "poranna_r54"]
    liczby = {(r, u): len(v["gniazda"]) for r in ramki for u, v in ramki[r].items()}
    assert liczby == {("W", "wieczorna"): 19, ("W", "wieczorna_r54"): 20, ("P", "poranna"): 24,
                      ("P", "poranna_r54"): 33}
    # rynienka szersza niz gniazdo okragle; gniazdo okragle = blok 3 x 3
    assert kalibracja.blok(kal_, "P", "poranna", 1)[2] > 3
    assert kalibracja.blok(kal_, "P", "poranna", 2)[2:] == [3, 3]
    # srodek gniazda 23 porannej (x 0, y 37,05 mm) lezy w bloku
    x, y, w, h = kalibracja.blok(kal_, "P", "poranna", 23)
    assert x <= 32 < x + w and y <= 32 - 37.05 / 2.5 < y + h


def test_kalibracja_zle_pliki(tmp_path):
    dobra = kalibracja.domyslna(MODELE)
    p = tmp_path / "kalibracja_ramek.json"
    kalibracja.zapisz(dobra, p)
    assert kalibracja.wczytaj(p) == dobra
    assert p.read_bytes().isascii()

    def zla(zmien):
        d = json.loads(json.dumps(dobra))
        zmien(d)
        with pytest.raises(kalibracja.BladKalibracji):
            kalibracja.sprawdz(d)

    zla(lambda d: d.update(wersja=2))
    zla(lambda d: d["ramki"].update(X={}))
    zla(lambda d: d["ramki"]["P"]["poranna"]["gniazda"].update({"2": [0, 0, 3, 3]}))
    zla(lambda d: d["ramki"]["P"]["poranna"]["gniazda"].update({"3": d["ramki"]["P"]["poranna"]["gniazda"]["2"]}))
    zla(lambda d: d["ramki"]["P"]["poranna"]["gniazda"].update({"x": [20, 20, 3, 3]}))
    zla(lambda d: d["ramki"]["P"]["poranna"]["gniazda"].update({"2": [20, 20, 3]}))
    zla(lambda d: d["ramki"]["P"]["poranna"].update(nieznane=1))
    (tmp_path / "zly.json").write_text("{", encoding="ascii")
    with pytest.raises(kalibracja.BladKalibracji):
        kalibracja.wczytaj(tmp_path / "zly.json")
    with pytest.raises(KeyError):
        kalibracja.blok(dobra, "P", "poranna", 99)


def test_kalibracja_narzedzie_wiersza_polecen(tmp_path):
    wyj = tmp_path / "kal.json"
    assert kalibracja.main(["--domyslna", "--modele", str(MODELE), "--wyjscie", str(wyj)]) == 0
    assert kalibracja.main(["--sprawdz", str(wyj)]) == 0
    (tmp_path / "zly.json").write_text("{\"wersja\": 1}", encoding="ascii")
    assert kalibracja.main(["--sprawdz", str(tmp_path / "zly.json")]) != 0


def test_test_led_na_atrapie_kazde_gniazdo_osobno(kal):
    atrapa = SprzetAtrapa()
    n = test_led.uruchom_test(atrapa, kal, "P", "poranna", czas_s=0.0, sen=lambda s: None)
    assert n == 24
    klatki = [k for _, _, k in atrapa.historia]
    assert len(klatki) >= 24
    gniazda_kal = kal["ramki"]["P"]["poranna"]["gniazda"]
    for (gid, blok), k in zip(sorted(gniazda_kal.items(), key=lambda t: int(t[0])), klatki):
        x, y, w, h = blok
        assert set(piksele_plytki(k)) == {(xx, yy) for yy in range(y, y + h) for xx in range(x, x + w)}, gid
    wszystkie = test_led.klatka_wszystkich(kal, "P", "poranna")
    assert len(piksele_plytki(wszystkie)) == sum(b[2] * b[3] for b in gniazda_kal.values())


# ----------------------------------------------------------------------------- sprzet_rpi bez sprzetu

def test_sprzet_rpi_funkcje_czyste_i_brak_bibliotek_na_pc():
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                # magnes obecny = stan niski (A3144, otwarty kolektor z podciaganiem)
                n = sprzet_rpi.numer_z_poziomow([1 - a, 1 - b, 1 - c])
                assert n == a + 2 * b + 4 * c
    m = sprzet_rpi.MAPA_KLAWISZY
    assert sprzet_rpi.klawisz_z_nazwy("KEY_KPENTER", m) == "enter"
    assert sprzet_rpi.klawisz_z_nazwy(["KEY_ENTER"], m) == "enter"
    assert sprzet_rpi.klawisz_z_nazwy("KEY_BACKSPACE", m) == "backspace"
    assert sprzet_rpi.klawisz_z_nazwy("KEY_KP7", m) == "7"
    assert sprzet_rpi.klawisz_z_nazwy("KEY_KPASTERISK", m) == "zamknij_piec"
    assert sprzet_rpi.klawisz_z_nazwy("KEY_VOLUMEUP", m) is None
    assert sprzet_rpi.przeksztalc(0, 0, 0, False) == (0, 0)
    assert sprzet_rpi.przeksztalc(0, 0, 90, False) == (63, 0)
    assert sprzet_rpi.przeksztalc(0, 0, 180, False) == (63, 63)
    assert sprzet_rpi.przeksztalc(0, 0, 270, False) == (0, 63)
    assert sprzet_rpi.przeksztalc(5, 7, 0, True) == (58, 7)
    with pytest.raises(BladSprzetu):
        sprzet_rpi.SprzetRpi(rola="P")


# ----------------------------------------------------------------------------- pliki: Python 3.11, ASCII, LF

def _pliki_paczki():
    pliki = sorted((STANOWISKO / "ramka").rglob("*"))
    pliki = [p for p in pliki if p.is_file() and "__pycache__" not in p.parts]
    return pliki + [STANOWISKO / "narzedzia" / "atrapa_ramki.py", Path(__file__)]


def test_pliki_ramki_skladnia_python_311_ascii_lf():
    pliki = _pliki_paczki()
    assert any(p.name == "README.md" for p in pliki)
    for p in pliki:
        b = p.read_bytes()
        assert b.isascii(), p.name
        assert b"\r" not in b, p.name
        if p.suffix == ".py":
            ast.parse(b.decode("ascii"), filename=str(p), feature_version=(3, 11))


def test_logi_serwera_bez_tresci_zadan(kal, ramka_p, caplog):
    caplog.set_level(logging.DEBUG)
    prog, atrapa, port = ramka_p
    lap = Laptop(port)
    lap.stan()
    lap.dobierz()
    lap.wyslij_plan(plan_rano(kal))
    assert "PUT" in caplog.text and "/plan" in caplog.text
    assert "3263" not in caplog.text and "gniazda" not in caplog.text
