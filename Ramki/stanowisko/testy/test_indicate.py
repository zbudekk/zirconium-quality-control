"""Testy strony laptopa ramek (E3-A8, czesc "indicate"): stanowisko/indicate.py i stanowisko/ramka_protokol.py.

Kryteria planu etapu 3 (sekcja 4.1, E3-A8) po stronie laptopa - nazwy testow `test_k<n>_...`:
K1 plan plytki porannej (23 gniazda) -> zrzut matrycy 64 x 64 z atrapy: swieca dokladnie bloki z planu (piksel po pikselu),
K2 margines: numer kuwety i liczba prac, K5 utrata sieci: 5 potwierdzen bez sieci -> laptop dostaje dokladnie 5, w kolejnosci,
bez powtorek (100 powtorzen z losowymi przerwami), K6 restart ramki -> laptop sam wysyla plan ponownie do 5 s, K7 Spacja ->
zmiana stanu ramki W ponizej 1 s (dwa procesy), K8 zapis calego ruchu testow bez nazw folderow ani nazwisk (ostatni test
pliku). Wymaganie z recenzji PR #19 dla laptopa ("laptop widzial zdjecie plytki, a wysyla stary wynik") - testy `test_w<n>_...`.
Pozostale: poranek (nowy piec, "Zamknij piec", restart programu laptopa, aktualizacja planu), jedna kolejka polecen, klucz,
drugi laptop, ustawienia, plan z prawdziwej `SesjaRano.plan_plytek`, protokol (budowa i walidacja komunikatow).
Runda 2 (recenzja PR #28): `test_b1_*` (ramka W = tylko ostatni skan), `test_b2_*` (zgaszenie przy zamykaniu, zastany
plan gaszony), `test_b3_*` (historia po restarcie programu, klucz (start_id, nr)), `test_p1_*` (zatrzymaj < 1 s),
`test_p2_*` (drugi laptop bez automatycznego przejecia), `test_zmiana_pieca_*` (proba 6); K8 z wlasnym ruchem.

Atrapa ramki: `narzedzia/atrapa_ramki.py` w osobnym procesie (K1, K2, K5, K6, K7) albo w procesie testu
(`atrapa_ramki.uruchom_atrape`) - zawsze przez HTTP na 127.0.0.1. Dane osobowe: tylko fikcyjne nazwy, i tylko po to, zeby
pokazac, ze nie trafiaja do ruchu sieciowego. Progi czasowe sa progami kryteriow (5 s, 1 s); czekanie na stan ramki ma zapas
na zegar Windows (ok. 15,6 ms) i obciazenie maszyny.
"""
from __future__ import annotations

import ast
import collections
import http.client
import json
import random
import re
import secrets
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

STANOWISKO = Path(__file__).resolve().parent.parent
for _p in (STANOWISKO, STANOWISKO / "narzedzia"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import atrapa_ramki  # noqa: E402
from ramka import czcionka, kalibracja, obraz  # noqa: E402
from ramka import protokol as RPR  # noqa: E402
from stanowisko import indicate as IND  # noqa: E402
from stanowisko import ramka_protokol as RP  # noqa: E402
from stanowisko import statusy  # noqa: E402

MODELE = STANOWISKO / "modele_plytek"
NARZ = STANOWISKO / "narzedzia" / "atrapa_ramki.py"
LAPTOP = "lap-test-a8i"
CZARNY = (0, 0, 0)
PLAN_ID = "2026-11-18-p1"

# Fikcyjne nazwy (dane osobowe udawane): laptop zna je w swojej sesji, do ramki maja trafiac tylko numery.
NAZWISKA = ("Kowalczykowa", "Wisniewska", "Zielinski", "Lewandowski", "Dabrowski", "Szymanska")
FOLDERY = ("Kowalczykowa 3263 ZR", "Wisniewska3301KB", "J. Zielinski 0412", "Prywatne Lewandowski", "Dabrowski 3999 AB",
           "Szymanska 4100")
KLUCZE_TESTOW: set = set()

# ----------------------------------------------------------------------------- zapis ruchu (K8)

RUCH: list = []
_RUCH_BLOK = threading.Lock()


def _do_bajtow(wpis) -> bytes:
    if isinstance(wpis, (bytes, bytearray)):
        return bytes(wpis)
    tekst = {k: (v.decode("utf-8", "replace") if isinstance(v, (bytes, bytearray)) else v) for k, v in wpis.items()}
    return json.dumps(tekst, ensure_ascii=False, default=str).encode("utf-8")


def zapisz_ruch(wpis) -> None:
    with _RUCH_BLOK:
        RUCH.append(_do_bajtow(wpis))


class Dziennik:
    """Dziennik ruchu jednego klienta `indicate` (hak `dziennik_ruchu`): wpisy do asercji + wspolny zapis K8."""

    def __init__(self):
        self.wpisy = []
        self._blok = threading.Lock()

    def __call__(self, wpis: dict) -> None:
        with self._blok:
            self.wpisy.append(dict(wpis))
        zapisz_ruch(wpis)

    def zadania(self, metoda=None, sciezka=None) -> list:
        with self._blok:
            w = list(self.wpisy)
        return [x for x in w if x["kierunek"] == "do_ramki" and (metoda is None or x["metoda"] == metoda)
                and (sciezka is None or x["sciezka"].split("?")[0] == sciezka)]

    def liczba(self, metoda, sciezka) -> int:
        return len(self.zadania(metoda, sciezka))


# ----------------------------------------------------------------------------- pomocnicze

@pytest.fixture(scope="module")
def kal():
    return kalibracja.domyslna(MODELE)


@pytest.fixture
def sprzataj():
    lista = []
    yield lista
    for f in reversed(lista):
        try:
            f()
        except Exception:  # noqa: BLE001 - sprzatanie po tescie
            pass


def czekaj_na(warunek, timeout=3.0, krok=0.01) -> bool:
    koniec = time.perf_counter() + timeout
    while time.perf_counter() < koniec:
        try:
            if warunek():
                return True
        except (OSError, http.client.HTTPException):
            pass
        time.sleep(krok)
    return bool(warunek())


def wolny_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class Http:
    """Bezposrednie zadania testu do ramki (obserwacja i sterowanie atrapa) - ruch tez trafia do zapisu K8."""

    def __init__(self, port, klucz=None):
        self.port = port
        self.klucz = klucz

    def zadanie(self, metoda, sciezka, tresc=None, laptop=None, timeout=10.0):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=timeout)
        try:
            h = {}
            if laptop:
                h["X-Laptop-Id"] = laptop
            if self.klucz:
                h["X-Ramka-Klucz"] = self.klucz
            body = None
            if tresc is not None:
                body = json.dumps(tresc).encode("utf-8")
                h["Content-Type"] = "application/json"
            zapisz_ruch(f"{metoda} {sciezka} ".encode("ascii") + (body or b""))
            c.request(metoda, sciezka, body=body, headers=h)
            r = c.getresponse()
            dane = r.read()
            zapisz_ruch(dane)
            return r.status, (json.loads(dane.decode("utf-8")) if dane else None)
        finally:
            c.close()

    def stan(self) -> dict:
        st, odp = self.zadanie("GET", "/stan")
        assert st == 200, odp
        return odp

    def plytka(self, n: int) -> None:
        st, odp = self.zadanie("PUT", "/atrapa/plytka", {"plytka": n}, laptop="test-atrapa")
        assert st == 200, odp

    def klawisz(self, k: str) -> None:
        st, odp = self.zadanie("PUT", "/atrapa/klawisz", {"klawisz": k}, laptop="test-atrapa")
        assert st == 200, odp

    def klatka(self) -> obraz.Klatka:
        st, odp = self.zadanie("GET", "/atrapa/klatka")
        assert st == 200, odp
        return obraz.Klatka.z_hex(odp["piksele_hex"])


class AtrapaProces(Http):
    """Atrapa ramki jako OSOBNY PROCES (narzedzia/atrapa_ramki.py --sterowanie)."""

    def __init__(self, rola, port=0, klucz=None, katalog=None):
        args = [sys.executable, str(NARZ), "--rola", rola, "--port", str(port), "--sterowanie"]
        if klucz:
            plik = Path(katalog) / f"ramka_{secrets.token_hex(4)}.json"
            plik.write_text(json.dumps({"klucz": klucz}), encoding="ascii")
            args += ["--konfiguracja", str(plik)]
        self.p = None
        for _ in range(3):  # port po zabitym procesie bywa przez chwile zajety
            self.p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                      cwd=str(STANOWISKO), text=True)
            linia = self.p.stdout.readline()
            if linia.startswith("ATRAPA_RAMKI "):
                break
            self.p.wait(10)
            time.sleep(0.3)
        assert linia.startswith("ATRAPA_RAMKI "), linia
        self.t_start = time.perf_counter()
        pola = dict(x.split("=") for x in linia.split()[1:])
        super().__init__(int(pola["port"]), klucz)
        self.start_id = pola["start_id"]

    def zabij(self) -> None:
        self.p.kill()
        self.p.wait(10)

    def zakoncz(self) -> None:
        if self.p.poll() is not None:
            return
        try:
            self.p.stdin.close()
            self.p.wait(10)
        except (OSError, subprocess.TimeoutExpired):
            self.p.kill()
            self.p.wait(10)


def ramka_wewnatrz(rola, port=0, **konf):
    """Program ramki z atrapa sprzetu w procesie testu (HTTP na 127.0.0.1); zwraca (program, atrapa, port)."""
    program, atrapa = atrapa_ramki.uruchom_atrape(rola, port=port, sterowanie=True, **konf)
    return program, atrapa, program.serwer.server_address[1]


def klient(rola, port, kal_, **kw):
    """Klient `indicate` z dziennikiem ruchu; krotkie przerwy po bledzie sieci (testy), chyba ze podane."""
    d = Dziennik()
    kw.setdefault("przerwa_min_s", 0.05)
    kw.setdefault("przerwa_max_s", 0.25)
    kw.setdefault("laptop_id", LAPTOP)
    k = IND.KlientRamki(rola, "127.0.0.1", port, kalibracja=kal_, dziennik_ruchu=d, **kw)
    k.uruchom()
    return k, d


class Posrednik:
    """Posrednik TCP na 127.0.0.1 symulujacy siec: `awaria` (zerwanie od razu, zgubione odpowiedzi w locie),
    `p_zrywania` (zgubiona odpowiedz), zapis calego ruchu w obie strony (K8)."""

    def __init__(self, cel_port, ziarno=11):
        self.cel_port = cel_port
        self.awaria = False
        self.p_zrywania = 0.0
        self.zerwane = 0
        self._rng = random.Random(ziarno)
        self._gn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._gn.bind(("127.0.0.1", 0))
        self._gn.listen(64)
        self.port = self._gn.getsockname()[1]
        self._stop = False
        threading.Thread(target=self._petla, daemon=True).start()

    def _petla(self):
        while not self._stop:
            try:
                kl, _ = self._gn.accept()
            except OSError:
                return
            threading.Thread(target=self._obsluz, args=(kl,), daemon=True).start()

    def _obsluz(self, kl):
        try:
            if self.awaria:
                self.zerwane += 1
                kl.close()
                return
            zrywaj = self._rng.random() < self.p_zrywania
            up = socket.create_connection(("127.0.0.1", self.cel_port), timeout=60)
            kl.settimeout(60)

            def do_gory():
                try:
                    while True:
                        b = kl.recv(65536)
                        if not b:
                            break
                        zapisz_ruch(b)
                        up.sendall(b)
                except OSError:
                    pass

            threading.Thread(target=do_gory, daemon=True).start()
            odp = bytearray()
            try:
                while True:
                    b = up.recv(65536)
                    if not b:
                        break
                    odp.extend(b)
            except OSError:
                pass
            if zrywaj or self.awaria:
                self.zerwane += 1
            else:
                zapisz_ruch(bytes(odp))
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


def piksele(kal_, rola, uklad, kolory: dict) -> dict:
    """{(x, y): rgb} blokow gniazd z pliku kalibracji (niezaleznie od `indicate`)."""
    wynik = {}
    for gid, kolor in kolory.items():
        x, y, w, h = kal_["ramki"][rola][uklad]["gniazda"][str(gid)]
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                wynik[(xx, yy)] = obraz.KOLORY[kolor]
    return wynik


def roznice_plytki(klatka, oczekiwane) -> list:
    """Porownanie piksel po pikselu w CALYM obszarze plytki; lista pikseli roznych od oczekiwanych (reszta ciemna)."""
    x0, y0, w, h = obraz.OBSZAR_PLYTKI
    return [(x, y) for y in range(y0, y0 + h) for x in range(x0, x0 + w)
            if klatka.piksel(x, y) != oczekiwane.get((x, y), CZARNY)]


TEKST_OBSZAR = (obraz.TEKST_X0, obraz.TEKST_Y, obraz.TEKST_SZER, czcionka.WYS)
PRAWY_OBSZAR = (obraz.PRAWY_X, obraz.PRAWY_Y0, czcionka.SZER, 3 * obraz.PRAWY_KROK + czcionka.WYS)


def margines(klatka) -> dict:
    return {(x, y): klatka.piksel(x, y) for (x0, y0, w, h) in (TEKST_OBSZAR, PRAWY_OBSZAR)
            for y in range(y0, y0 + h) for x in range(x0, x0 + w)}


def margines_wzor(tekst, inne=()) -> dict:
    k = obraz.Klatka()
    obraz.rysuj_tekst_przod(k, tekst)
    obraz.rysuj_prawy(k, inne)
    return margines(k)


# Plan plytki porannej K1: 23 gniazda ukladu `poranna` (2..24; id 1 = rynienka), 5 kuwet + 2 prace bez kuwety.
KUWETY_K1 = [("3263", [2, 3, 4, 5, 6], "zielony", [4, 5]), ("3301", [7, 8, 9, 10, 11], "zielony", [4]),
             ("0412", [12, 13, 14, 15], "bursztyn", [4]), ("#1234", [16, 17, 18, 19], "zielony", [4]),
             ("3999", [20, 21, 22], "zielony", [4])]
BEZ_KUWETY_K1 = {23: "bialy", 24: "czerwony"}


def plan_plytek_k1(plan_id=PLAN_ID, braki=("5120",)) -> dict:
    """Plan w ksztalcie `SesjaRano.plan_plytek` (z polami pomocniczymi, ktorych ramka nie dostaje)."""
    gniazda = []
    for kuw, ids, kolor, _ in KUWETY_K1:
        gniazda += [{"id": i, "kolor": kolor, "kuweta": kuw} for i in ids]
    gniazda += [{"id": i, "kolor": k} for i, k in BEZ_KUWETY_K1.items()]
    gniazda.sort(key=lambda g: g["id"])
    return {"plan_id": plan_id, "tryb": "rano", "sesja_pieca_id": 1, "plytki": {"4": {"gniazda": gniazda}},
            "kuwety": [{"kuweta": k, "plytki": pl} for k, _, _, pl in KUWETY_K1], "braki": list(braki),
            "uklady": {"4": "poranna"}, "skany": {"4": 11}, "liczba_prac": {k: len(ids) for k, ids, _, _ in KUWETY_K1},
            "pominiete": {"bez_numeru": [], "poza_gniazdem": 0, "zdublowane_plytki": []}}


K5_KUWETY = ["5001", "5002", "5003", "5004", "5005", "5006"]


def plan_plytek_k5(plan_id="2026-11-18-p5") -> dict:
    return {"plan_id": plan_id, "tryb": "rano", "plytki": {"4": {"gniazda": [
        {"id": 2 + n, "kolor": "zielony", "kuweta": k} for n, k in enumerate(K5_KUWETY)]}},
        "kuwety": [{"kuweta": k, "plytki": [4]} for k in K5_KUWETY], "braki": [], "uklady": {"4": "poranna"}}


def kolory_wieczor(kal_, uklad="wieczorna", przesuniecie=0) -> dict:
    """Kolory gniazd plytki wieczornej z jednej tabeli statusow (statusy.py) - tak, jak mape widzi ekran."""
    cykl = ["zielony", "czerwony", "zolty", "szary", "zatwierdzona_ok", "pusty", "podwojny", "ukruszona", "popraw_ulozenie"]
    ids = sorted(int(i) for i in kal_["ramki"]["W"][uklad]["gniazda"])
    return {i: RP.kolor_ramki(cykl[(n + przesuniecie) % len(cykl)]) for n, i in enumerate(ids)}


def swiecace(kolory: dict) -> dict:
    return {i: c for i, c in kolory.items() if c is not None}


def czekaj_klatka(pobierz, oczekiwane, timeout=3.0) -> list:
    """Czeka, az obszar plytki bedzie rowny oczekiwanemu; zwraca ostatnia liste roznic ([] = zgodnie)."""
    ost = [None]

    def ok():
        ost[0] = roznice_plytki(pobierz(), oczekiwane)
        return ost[0] == []
    czekaj_na(ok, timeout, 0.02)
    return ost[0]


def odbierz_n(k, n, timeout=10.0) -> list:
    """Zdarzenia odebrane przez klienta, az bedzie ich co najmniej n (potem chwila na ewentualne nadmiarowe)."""
    nowe = []
    koniec = time.perf_counter() + timeout
    while time.perf_counter() < koniec and len(nowe) < n:
        nowe += k.odbierz_zdarzenia()
        time.sleep(0.005)
    time.sleep(0.05)
    nowe += k.odbierz_zdarzenia()
    return nowe


# ----------------------------------------------------------------------------- protokol (ramka_protokol.py)

def test_protokol_plan_rano_z_planu_plytek_przechodzi_walidacje_ramki(kal):
    pp = plan_plytek_k1()
    plan, pominiete = RP.plan_rano(pp, kal, wersja=3, start_id="a1b2c3d4", zdarzenia_do=57,
                                   potwierdzone=[[4, "3263"], [5, "3263"], [4, "9999"]], wybrane={"4": "0412", "6": "3301"})
    p = RPR.sprawdz_plan(plan, "P")  # walidacja programu ramki - plan przyjalby sie bez 400
    assert set(plan) == {"protokol", "plan_id", "wersja", "start_id", "zdarzenia_do", "wazny_s", "tryb", "plytki", "kuwety",
                         "potwierdzone", "wybrane", "braki"}
    assert (plan["wersja"], plan["start_id"], plan["zdarzenia_do"], plan["wazny_s"], plan["tryb"]) == (3, "a1b2c3d4", 57, 600.0, "rano")
    assert [g["id"] for g in plan["plytki"]["4"]["gniazda"]] == list(range(2, 25))
    for g in plan["plytki"]["4"]["gniazda"]:
        assert g["px"] == kal["ramki"]["P"]["poranna"]["gniazda"][str(g["id"])]
    assert [k.kuweta for k in p.kuwety] == ["3263", "3301", "0412", "#1234", "3999"]
    # potwierdzone / wybrane tylko dla plytek planu i kuwet z listy (inaczej ramka odrzucilaby caly plan 400)
    assert plan["potwierdzone"] == [[4, "3263"]] and plan["wybrane"] == {"4": "0412"}
    assert plan["braki"] == ["5120"] and pominiete["zla_plytka"] == [] and pominiete["brak_kalibracji"] == []
    assert RP.odcisk_tresci(plan) == RP.odcisk_tresci(dict(plan, wersja=9, start_id="ffff", zdarzenia_do=1))
    assert RP.odcisk_tresci(plan) != RP.odcisk_tresci(dict(plan, potwierdzone=[]))


def test_protokol_plan_rano_odrzuca_to_czego_ramka_nie_przyjmie(kal):
    """Nazwy zamiast numerow kuwet, plytka spoza rodziny ramki, uklad bez kalibracji (plytka okragla), zly kolor i pola
    pomocnicze: nic z tego nie idzie do ramki, plan dalej przechodzi walidacje ramki."""
    pp = plan_plytek_k1()
    pp["plytki"]["4"]["gniazda"][0]["kuweta"] = FOLDERY[0]       # gniazdo 2: nazwa folderu zamiast numeru
    pp["plytki"]["4"]["gniazda"][1]["kolor"] = "rozowy"          # gniazdo 3: kolor spoza protokolu
    pp["plytki"]["2"] = {"gniazda": [{"id": 1, "kolor": "zielony", "kuweta": "3263"}]}   # plytka wieczorna rano
    pp["plytki"]["5"] = {"gniazda": [{"id": 1, "kolor": "zielony", "kuweta": "3301"}]}
    pp["uklady"].update({"2": "wieczorna", "5": "okragla_poranna"})
    pp["kuwety"].append({"kuweta": FOLDERY[1], "plytki": [4]})
    pp["braki"] += [NAZWISKA[2], "0007"]
    pp["opisy"] = {"3263": FOLDERY[0]}                          # pole nieznane protokolowi
    plan, pominiete = RP.plan_rano(pp, kal, wersja=1, start_id="a1b2", zdarzenia_do=0)
    RPR.sprawdz_plan(plan, "P")
    tekst = json.dumps(plan)
    assert not any(n.lower() in tekst.lower() for n in NAZWISKA + FOLDERY)
    assert set(plan["plytki"]) == {"4"}
    assert pominiete["zla_plytka"] == [2] and pominiete["brak_kalibracji"] == [5]
    g = {x["id"]: x for x in plan["plytki"]["4"]["gniazda"]}
    assert g[2] == {"id": 2, "px": g[2]["px"], "kolor": "czerwony"}   # bez kuwety = "sprawdz" (jak session_rano)
    assert g[3]["kolor"] == "czerwony" and g[3]["kuweta"] == "3263"
    assert pominiete["kuweta_odrzucona"] == 1 and pominiete["zly_kolor"] == 1
    assert [k["kuweta"] for k in plan["kuwety"]] == ["3263", "3301", "0412", "#1234", "3999"]
    assert plan["braki"] == ["5120", "0007"]
    with pytest.raises(RP.BladProtokolu):
        RP.plan_rano(dict(pp, plan_id="Kowalczykowa 3263"), kal, wersja=1, start_id="a1b2", zdarzenia_do=0)


def test_protokol_plan_wieczor_bez_pol_porannych_kolory_z_tabeli_statusow(kal):
    kol = kolory_wieczor(kal)
    plan, pominiete = RP.plan_wieczor({2: ("wieczorna", kol)}, kal, plan_id="2026-11-18-w-ab12", wersja=1,
                                      start_id="a1b2c3d4", zdarzenia_do=4)
    RPR.sprawdz_plan(plan, "W")
    assert set(plan) == {"protokol", "plan_id", "wersja", "start_id", "zdarzenia_do", "wazny_s", "tryb", "plytki"}
    assert plan["tryb"] == "wieczor" and plan["wazny_s"] == 30.0
    gn = plan["plytki"]["2"]["gniazda"]
    assert all(set(g) == {"id", "px", "kolor"} for g in gn)
    assert {g["id"]: g["kolor"] for g in gn} == swiecace(kol)
    # jedna tabela statusow: kolor ramki = kolumna `ramka` w statusy.py (ekran i ramka bez wlasnych stalych)
    for klucz, wiersz in statusy.STATUSY.items():
        assert RP.kolor_ramki(klucz) == wiersz.ramka
    assert RP.kolor_ramki("status_z_przyszlosci") == statusy.status("status_z_przyszlosci").ramka
    assert RP.kolor_ramki("czeka_na_numer") is None and RP.kolor_ramki("szary") == "bialy"
    # plytka spoza rodziny ramki W i uklad bez kalibracji nie ida do planu
    plan2, pom2 = RP.plan_wieczor({5: ("poranna", {2: "zielony"}), 3: ("okragla_wieczorna", {1: "zielony"})}, kal,
                                  plan_id="w", wersja=2, start_id="a1b2", zdarzenia_do=0)
    assert plan2["plytki"] == {} and pom2["zla_plytka"] == [5] and pom2["brak_kalibracji"] == [3]


def test_protokol_walidacja_odpowiedzi_ramki():
    dobra = {"protokol": 1, "start_id": "a1b2c3d4", "restart": False, "od": 3, "nr_zdarzenia": 5, "najstarsze_zdarzenie": 1,
             "utracone": 0, "utracone_od": None, "utracone_do": None,
             "zdarzenia": [{"nr": 4, "typ": "plytka", "czas_s": 1.0, "plytka": 4, "poprzednia": 0},
                           {"nr": 5, "typ": "potwierdzenie", "czas_s": 1.5, "plan_id": "p", "plytka": 4, "kuweta": "3263"}]}
    assert RP.sprawdz_zdarzenia(dobra)["zdarzenia"][1]["kuweta"] == "3263"
    for zla in (None, [], {"protokol": 2}, dict(dobra, protokol=2), dict(dobra, start_id="Kowal czyk"),
                dict(dobra, zdarzenia={}), dict(dobra, zdarzenia=[{"typ": "plytka"}]),
                dict(dobra, zdarzenia=[{"nr": "4", "typ": "plytka"}]), dict(dobra, zdarzenia=[{"nr": 5, "typ": 7}]),
                dict(dobra, zdarzenia=[dobra["zdarzenia"][1], dobra["zdarzenia"][0]]),
                dict(dobra, utracone=-1), dict(dobra, restart="tak")):
        with pytest.raises(RP.BladOdpowiedzi):
            RP.sprawdz_zdarzenia(zla)
    stan = {"protokol": 1, "rola": "P", "start_id": "a1b2c3d4", "plytka": 4, "plytka_pewna": True, "tryb": "wynik",
            "plan_id": PLAN_ID, "plan_wersja": 2, "nr_zdarzenia": 9, "potwierdzone": [[4, "3263"]], "wybrane": {"4": "3301"},
            "blad_sprzetu": False}
    assert RP.sprawdz_stan(stan)["plan_wersja"] == 2
    for zla in (dict(stan, rola="X"), dict(stan, nr_zdarzenia=-1), dict(stan, potwierdzone=[[4]]), dict(stan, start_id=None)):
        with pytest.raises(RP.BladOdpowiedzi):
            RP.sprawdz_stan(zla)
    assert RP.tresc_trybu("skanowanie") == {"protokol": 1, "stan": "skanowanie"}
    with pytest.raises(RP.BladProtokolu):
        RP.tresc_trybu("wynik")  # stan wynik ustawia tylko przyjety plan


# ----------------------------------------------------------------------------- K1: matryca 64 x 64

def test_k1_plan_porannej_23_gniazda_matryca_piksel_po_pikselu(kal, sprzataj):
    """Atrapa ramki P jako osobny proces. Ramka poranna swieci gniazda biezacej kuwety i prace bez kuwety: po kolei
    (Enter) swieca wszystkie 23 gniazda planu, kazde w swoim kroku, reszta obszaru plytki ciemna - piksel po pikselu."""
    atr = AtrapaProces("P")
    sprzataj.append(atr.zakoncz)
    k, d = klient("P", atr.port, kal)
    sprzataj.append(k.zatrzymaj)
    k.ustaw_plan_rano(plan_plytek_k1())
    assert czekaj_na(lambda: atr.stan()["plan_id"] == PLAN_ID, 5.0), k.stan()
    atr.plytka(4)
    zapalone_w_krokach = []
    for kuw, ids, kolor, _ in KUWETY_K1:
        ocz = piksele(kal, "P", "poranna", {**{i: kolor for i in ids}, **BEZ_KUWETY_K1})
        assert czekaj_klatka(atr.klatka, ocz) == [], f"kuweta {kuw}"
        zapalone_w_krokach.append(set(ids))
        atr.klawisz("enter")
    assert czekaj_klatka(atr.klatka, piksele(kal, "P", "poranna", BEZ_KUWETY_K1)) == []
    wszystkie = set().union(*zapalone_w_krokach) | set(BEZ_KUWETY_K1)
    assert wszystkie == set(range(2, 25)) and len(wszystkie) == 23
    assert sum(len(s) for s in zapalone_w_krokach) == 21  # kazde gniazdo z kuweta zapalone w dokladnie jednym kroku
    # nowy piec: 23 prace bez kuwety (nieznane / sprawdz) - wszystkie 23 bloki naraz; najpierw DELETE /plan (nowy wsad)
    pp2 = plan_plytek_k1(plan_id="2026-11-18-p2", braki=())
    kolory2 = {i: ("bialy", "czerwony", "zolty")[i % 3] for i in range(2, 25)}
    pp2["plytki"]["4"]["gniazda"] = [{"id": i, "kolor": c} for i, c in kolory2.items()]
    pp2["kuwety"] = []
    k.ustaw_plan_rano(pp2)
    assert czekaj_na(lambda: atr.stan()["plan_id"] == "2026-11-18-p2", 5.0)
    assert czekaj_klatka(atr.klatka, piksele(kal, "P", "poranna", kolory2)) == []
    polecenia = [(w["metoda"], json.loads(w["tresc"])["plan_id"] if w["metoda"] == "PUT" else None)
                 for w in d.zadania() if w["sciezka"].split("?")[0] == "/plan"]
    assert polecenia.index(("DELETE", None)) == polecenia.index(("PUT", "2026-11-18-p2")) - 1
    assert atr.stan()["potwierdzone"] == []


# ----------------------------------------------------------------------------- K2: margines

def test_k2_margines_numer_kuwety_i_liczba_prac(kal, sprzataj):
    """Margines z przodu: "<kuweta> <liczba prac tej kuwety na lezacej plytce>", z prawej numery innych plytek kuwety;
    po rozlozeniu wszystkich kuwet - braki ("-5120"). Porownanie pikseli marginesu z napisem wzorcowym."""
    atr = AtrapaProces("P")
    sprzataj.append(atr.zakoncz)
    k, _ = klient("P", atr.port, kal)
    sprzataj.append(k.zatrzymaj)
    k.ustaw_plan_rano(plan_plytek_k1())
    assert czekaj_na(lambda: atr.stan()["plan_id"] == PLAN_ID, 5.0)
    atr.plytka(4)
    for kuw, ids, _, plytki in KUWETY_K1:
        wzor = margines_wzor(f"{kuw} {len(ids)}", [p for p in plytki if p != 4])
        assert czekaj_na(lambda w=wzor: margines(atr.klatka()) == w, 3.0, 0.02), kuw
        assert atr.stan()["kuweta"] == kuw
        atr.klawisz("enter")
    assert czekaj_na(lambda: margines(atr.klatka()) == margines_wzor("-5120"), 3.0, 0.02)
    assert czekaj_na(lambda: k.potwierdzone() == [[4, kuw] for kuw, _, _, _ in KUWETY_K1], 3.0)


# ----------------------------------------------------------------------------- K5: utrata sieci

def test_k5_utrata_sieci_5_potwierdzen_100_powtorzen(kal, sprzataj):
    """Ramka P w osobnym procesie, laptop przez posrednik TCP. W kazdym powtorzeniu siec pada, technik naciska 5 klawiszy
    (Enter x 5 albo Backspace x 5), przerwa losowa, siec wraca z 30 % zgubionych odpowiedzi. Laptop ma dostac dokladnie
    5 zdarzen, w kolejnosci, bez powtorek - i nie wysylac planu po zdarzeniach klawiatury."""
    atr = AtrapaProces("P")
    sprzataj.append(atr.zakoncz)
    proxy = Posrednik(atr.port, ziarno=5)
    sprzataj.append(proxy.zamknij)
    k, d = klient("P", proxy.port, kal, odpytywanie_s=2.0)
    sprzataj.append(k.zatrzymaj)
    k.ustaw_plan_rano(plan_plytek_k5())
    assert czekaj_na(lambda: atr.stan()["plan_id"] == "2026-11-18-p5", 5.0), k.stan()
    atr.plytka(4)
    assert czekaj_na(lambda: atr.stan()["plytka"] == 4 and atr.stan()["plytka_pewna"], 3.0)
    assert czekaj_na(lambda: k.kursor[1] == atr.stan()["nr_zdarzenia"], 5.0)
    k.odbierz_zdarzenia()
    put0 = d.liczba("PUT", "/plan")
    rng = random.Random(18)
    odebrane = []
    for rep in range(100):
        klawisz, typ, kolejnosc = (("enter", "potwierdzenie", K5_KUWETY[:5]) if rep % 2 == 0
                                   else ("backspace", "cofniecie", K5_KUWETY[:5][::-1]))
        proxy.p_zrywania = 0.0
        proxy.awaria = True
        n0 = atr.stan()["nr_zdarzenia"]
        for _ in range(5):
            atr.klawisz(klawisz)
            if rng.random() < 0.5:
                time.sleep(rng.uniform(0.0, 0.01))
        assert czekaj_na(lambda: atr.stan()["nr_zdarzenia"] >= n0 + 5, 5.0, 0.02), f"powtorzenie {rep}"
        time.sleep(rng.uniform(0.0, 0.15))
        proxy.awaria, proxy.p_zrywania = False, 0.3
        nowe = odbierz_n(k, 5)
        assert [(z["typ"], z["kuweta"]) for z in nowe] == [(typ, kk) for kk in kolejnosc], f"powtorzenie {rep}: {nowe}"
        assert all(z["rola"] == "P" and z["start_id"] == atr.start_id for z in nowe)
        odebrane += nowe
    nry = [z["nr"] for z in odebrane]
    assert len(odebrane) == 500 and nry == list(range(nry[0], nry[0] + 500)), "luka albo powtorka w zdarzeniach"
    assert d.liczba("PUT", "/plan") == put0, "laptop wyslal plan po zdarzeniach klawiatury"
    assert czekaj_na(lambda: k.potwierdzone() == [] and atr.stan()["potwierdzone"] == [], 3.0)
    bledy = k.stan()["bledy_sieci"]
    print(f"POMIAR K5: 100 powtorzen, zdarzen odebranych {len(odebrane)} z 500 (0 powtorek, 0 luk), "
          f"nieudanych zadan laptopa {bledy}, odpowiedzi zgubionych przez posrednik {proxy.zerwane}")
    assert bledy >= 100


# ----------------------------------------------------------------------------- K6: restart ramki

def test_k6_restart_ramki_laptop_wysyla_plan_ponownie_do_5_s(kal, sprzataj):
    """Ramka P w osobnym procesie zabijana i uruchamiana ponownie na tym samym porcie (3 razy). Laptop (przerwy po bledzie
    jak w programie: 0,2-1 s) sam wysyla plan z nowym start_id i potwierdzeniami z wlasnego stanu - do 5 s od startu ramki."""
    port = wolny_port()
    atr = AtrapaProces("P", port=port)
    sprzataj.append(lambda: atr.zakoncz())
    k, d = klient("P", port, kal, przerwa_min_s=0.2, przerwa_max_s=1.0)
    sprzataj.append(k.zatrzymaj)
    k.ustaw_plan_rano(plan_plytek_k1())
    assert czekaj_na(lambda: atr.stan()["plan_id"] == PLAN_ID, 5.0)
    atr.plytka(4)
    assert czekaj_na(lambda: atr.stan()["plytka"] == 4 and atr.stan()["plytka_pewna"], 3.0)
    atr.klawisz("enter")
    atr.klawisz("enter")
    potw = [[4, "3263"], [4, "3301"]]
    assert czekaj_na(lambda: k.potwierdzone() == potw, 5.0), k.stan()
    czasy, od_zabicia = [], []
    for _ in range(3):
        stary = atr.stan()["start_id"]
        t_zabicia = time.perf_counter()
        atr.zabij()
        atr = AtrapaProces("P", port=port)
        t0 = atr.t_start   # linia ATRAPA_RAMKI (port nasluchu otwarty chwile wczesniej)
        assert czekaj_na(lambda: atr.stan()["plan_id"] == PLAN_ID, 8.0, 0.02), k.stan()
        teraz = time.perf_counter()
        czasy.append(teraz - t0)
        od_zabicia.append(teraz - t_zabicia)   # gorne ograniczenie: razem z uruchomieniem nowego procesu ramki
        s = atr.stan()
        assert s["start_id"] != stary and s["potwierdzone"] == potw
    atr.plytka(4)
    ocz = piksele(kal, "P", "poranna", {**{i: "bursztyn" for i in KUWETY_K1[2][1]}, **BEZ_KUWETY_K1})
    assert czekaj_klatka(atr.klatka, ocz) == []
    print(f"POMIAR K6: 3 restarty ramki, plan ponownie po {', '.join(f'{c:.2f}' for c in czasy)} s od startu ramki, "
          f"{', '.join(f'{c:.2f}' for c in od_zabicia)} s od zabicia poprzedniego procesu ramki")
    assert max(od_zabicia) <= 5.0, od_zabicia


# ----------------------------------------------------------------------------- K7: Spacja -> stan ramki W

def test_k7_spacja_zmienia_stan_ramki_w_ponizej_1_s_dwa_procesy(kal, sprzataj):
    """Ramka W jako osobny proces, laptop = proces testu (klient indicate). 10 razy: plytka zdjeta, Spacja (skanowanie)
    -> stan ramki < 1 s, analiza, wynik -> po polozeniu plytki kolory gniazd rowne mapie (tabela statusow)."""
    atr = AtrapaProces("W")
    sprzataj.append(atr.zakoncz)
    k, d = klient("W", atr.port, kal)
    sprzataj.append(k.zatrzymaj)
    assert czekaj_na(lambda: k.stan()["polaczona"], 5.0)
    czasy = []
    for i in range(10):
        kol = kolory_wieczor(kal, przesuniecie=i)
        plytka = 2 + i % 2   # na zmiane 2 i 3: powrot A -> 0 -> A ramka ustala dopiero po 3 s (drgania czujnikow)
        atr.plytka(0)
        assert czekaj_na(lambda: atr.stan()["plytka"] == 0, 3.0)
        assert czekaj_na(lambda: k.kursor[1] == atr.stan()["nr_zdarzenia"], 3.0)
        t0 = time.perf_counter()
        z = k.skanowanie()
        assert czekaj_na(lambda: atr.stan()["tryb"] == "skanowanie", 3.0, 0.003)
        czasy.append(time.perf_counter() - t0)
        k.analiza()
        assert czekaj_na(lambda: atr.stan()["tryb"] == "analiza", 3.0)
        assert k.wynik(plytka, "wieczorna", kol, z) == "wyslany"
        atr.plytka(plytka)
        assert czekaj_klatka(atr.klatka, piksele(kal, "W", "wieczorna", swiecace(kol))) == [], f"cykl {i}"
    s = sorted(czasy)
    print(f"POMIAR K7: 10 Spacji, stan ramki W po: mediana {s[5] * 1000:.0f} ms, maks {s[-1] * 1000:.0f} ms")
    assert max(czasy) < 1.0, czasy
    assert d.liczba("PUT", "/tryb") == 20 and d.liczba("PUT", "/plan") >= 10


# ----------------------------------------------------------------------------- W: wymaganie z recenzji PR #19

def _wieczor(kal, sprzataj, **kw):
    program, atrapa, port = ramka_wewnatrz("W")
    sprzataj.append(program.zatrzymaj)
    k, d = klient("W", kw.pop("port_klienta", port), kal, **kw)
    sprzataj.append(k.zatrzymaj)
    assert czekaj_na(lambda: k.stan()["polaczona"], 5.0)
    return program, atrapa, port, k, d


def _odebral_wszystko(k, program, timeout=3.0) -> bool:
    return czekaj_na(lambda: k.kursor == (program.logika.start_id, program.logika.nr), timeout)


def test_w1_laptop_odebral_zdjecie_plytki_i_nie_wysyla_starego_wyniku(kal, sprzataj):
    program, atrapa, port, k, d = _wieczor(kal, sprzataj)
    kol = kolory_wieczor(kal)
    z = k.skanowanie()
    assert k.wynik(2, "wieczorna", kol, z) == "wyslany"
    atrapa.poloz_plytke(2)
    ocz = piksele(kal, "W", "wieczorna", swiecace(kol))
    assert atrapa.czekaj(lambda a: roznice_plytki(a.klatka, ocz) == [], 3.0)
    atrapa.poloz_plytke(0)                       # technik zdejmuje plytke (nowe prace)
    assert czekaj_na(lambda: program.logika.plytka == 0, 2.0)
    assert _odebral_wszystko(k, program)
    put = d.liczba("PUT", "/plan")
    kol2 = kolory_wieczor(kal, przesuniecie=3)   # np. decyzja technika zmienia kolor - ale to nadal stary skan
    assert k.wynik(2, "wieczorna", kol2, z) == "niewazny"
    atrapa.poloz_plytke(2)
    assert czekaj_na(lambda: program.logika.plytka == 2 and program.logika.plytka_pewna, 6.0)  # powrot A-0-A: po 3 s
    time.sleep(0.2)
    assert roznice_plytki(atrapa.klatka, {}) == [] and d.liczba("PUT", "/plan") == put
    assert program.logika.stan(program.zegar())["plytki_planu"] == []
    # nowy skan tej plytki (laptop odebral zdjecie przed Spacja) - wynik swieci
    atrapa.poloz_plytke(0)
    assert czekaj_na(lambda: program.logika.plytka == 0, 2.0)
    assert _odebral_wszystko(k, program)
    z2 = k.skanowanie()
    assert k.wynik(2, "wieczorna", kol2, z2) == "wyslany"
    atrapa.poloz_plytke(2)
    ocz2 = piksele(kal, "W", "wieczorna", swiecace(kol2))
    assert atrapa.czekaj(lambda a: roznice_plytki(a.klatka, ocz2) == [], 6.0)


def test_w2_po_wygasnieciu_planu_wynik_sprzed_przerwy_nie_wraca(kal, sprzataj):
    """Siec pada na dluzej niz waznosc planu W (tu 2 s): ramka gasi (plan_wygasl), technik zdejmuje i kladzie plytke.
    Po powrocie sieci laptop NIE wysyla wyniku sprzed przerwy."""
    program, atrapa, port = ramka_wewnatrz("W")
    sprzataj.append(program.zatrzymaj)
    proxy = Posrednik(port)
    sprzataj.append(proxy.zamknij)
    k, d = klient("W", proxy.port, kal, wazny_s=2.0, odpytywanie_s=0.5)
    sprzataj.append(k.zatrzymaj)
    assert czekaj_na(lambda: k.stan()["polaczona"], 5.0)
    kol = kolory_wieczor(kal)
    z = k.skanowanie()
    assert k.wynik(2, "wieczorna", kol, z) == "wyslany"
    atrapa.poloz_plytke(2)
    assert atrapa.czekaj(lambda a: roznice_plytki(a.klatka, piksele(kal, "W", "wieczorna", swiecace(kol))) == [], 3.0)
    put = d.liczba("PUT", "/plan")
    proxy.awaria = True
    assert czekaj_na(lambda: program.logika.plan is None, 6.0)
    atrapa.poloz_plytke(0)
    assert czekaj_na(lambda: program.logika.plytka == 0, 2.0)
    atrapa.poloz_plytke(2)
    assert czekaj_na(lambda: program.logika.plytka == 2, 6.0)   # powrot A -> 0 -> A ramka ustala po 3 s
    proxy.awaria = False
    assert _odebral_wszystko(k, program, 5.0)
    typy = [z_["typ"] for z_ in k.odbierz_zdarzenia()]
    assert "plan_wygasl" in typy
    time.sleep(0.7)
    assert d.liczba("PUT", "/plan") == put and program.logika.plan is None
    assert roznice_plytki(atrapa.klatka, {}) == []
    assert k.wynik(2, "wieczorna", kol, z) == "niewazny"


def test_w3_restart_ramki_w_laptop_nie_wznawia_wyniku(kal, sprzataj):
    program, atrapa, port, k, d = _wieczor(kal, sprzataj)
    kol = kolory_wieczor(kal)
    z = k.skanowanie()
    assert k.wynik(2, "wieczorna", kol, z) == "wyslany"
    atrapa.poloz_plytke(2)
    assert atrapa.czekaj(lambda a: roznice_plytki(a.klatka, piksele(kal, "W", "wieczorna", swiecace(kol))) == [], 3.0)
    stary = program.logika.start_id
    put = d.liczba("PUT", "/plan")
    program.zatrzymaj()
    program2, atrapa2, _ = ramka_wewnatrz("W", port=port)
    sprzataj.append(program2.zatrzymaj)
    atrapa2.poloz_plytke(2)
    assert czekaj_na(lambda: k.kursor[0] == program2.logika.start_id != stary, 5.0)
    time.sleep(0.7)
    assert d.liczba("PUT", "/plan") == put and program2.logika.plan is None
    assert atrapa2.czekaj(lambda a: roznice_plytki(a.klatka, {}) == [], 2.0)
    assert k.wynik(2, "wieczorna", kol, z) == "niewazny"   # skan sprzed restartu ramki


def test_w4_plan_sprzed_zdjecia_plytki_409_laptop_odbiera_i_nie_wysyla_starego_wyniku(kal, sprzataj):
    """Plan zbudowany przed zdjeciem plytki 2 (zdjecie miedzy zbudowaniem planu a jego przyjeciem): ramka 409
    zdarzenia_nieodebrane; laptop odbiera zdarzenia, widzi zdjecie - wynik plytki 2 juz nie idzie, ramka ciemna
    i w stanie "gotowa"; wynik poprzedniego skanu (plytka 1) tez nie wraca (ramka W = tylko ostatni skan, B1)."""
    program, atrapa, port, k, d = _wieczor(kal, sprzataj)
    kol1, kol2 = kolory_wieczor(kal), kolory_wieczor(kal, przesuniecie=2)
    z1 = k.skanowanie()
    assert k.wynik(1, "wieczorna", kol1, z1) == "wyslany"
    assert czekaj_na(lambda: program.logika.plan is not None and sorted(program.logika.plan.plytki) == [1], 3.0)
    z2 = k.skanowanie()
    assert czekaj_na(lambda: program.logika.tryb == "skanowanie", 3.0)
    wywolania = []

    def zdejmij_przed_wyslaniem():
        if not wywolania:
            atrapa.poloz_plytke(2)
            assert czekaj_na(lambda: program.logika.plytka == 2, 2.0)
            atrapa.poloz_plytke(0)
            assert czekaj_na(lambda: program.logika.plytka == 0, 2.0)
        wywolania.append(1)

    k.przed_wyslaniem_planu = zdejmij_przed_wyslaniem
    put = d.liczba("PUT", "/plan")
    assert k.wynik(2, "wieczorna", kol2, z2) == "wyslany"
    assert czekaj_na(lambda: wywolania and program.logika.tryb == "gotowa" and not k.stan()["oczekuje"], 5.0), (
        program.logika.tryb, program.logika.plan, {x: k.stan()[x] for x in ("oczekuje", "blad", "kod_bledu", "wyniki",
                                                                          "kursor", "plan_przyjety")},
        [(w["kierunek"], w["metoda"], w["sciezka"][:12], w.get("status")) for w in d.wpisy if w["metoda"] != "GET"],
        [(z["nr"], z["typ"]) for z in program.logika.zdarzenia])
    time.sleep(0.3)
    assert program.logika.plan is None and program.logika.tryb == "gotowa"
    plany = [json.loads(w["tresc"]) for w in d.zadania("PUT", "/plan")[put:]]
    assert [sorted(p["plytki"]) for p in plany] == [["2"]]   # jedna proba (409), potem nic - bez starego wyniku
    assert k.wynik(2, "wieczorna", kol2, z2) == "niewazny"
    atrapa.poloz_plytke(2)
    assert czekaj_na(lambda: program.logika.plytka == 2 and program.logika.plytka_pewna, 6.0)  # powrot A-0-A: po 3 s
    time.sleep(0.2)
    assert roznice_plytki(atrapa.klatka, {}) == []
    atrapa.poloz_plytke(1)
    assert czekaj_na(lambda: program.logika.plytka == 1 and program.logika.plytka_pewna, 3.0)
    time.sleep(0.2)
    assert roznice_plytki(atrapa.klatka, {}) == []   # wynik plytki 1 z poprzedniego skanu nie wraca


def test_w5_wynik_bez_numeru_albo_bez_kalibracji_nic_nie_zapala(kal, sprzataj):
    program, atrapa, port, k, d = _wieczor(kal, sprzataj)
    z = k.skanowanie()
    k.analiza()
    assert k.wynik(None, "wieczorna", kolory_wieczor(kal), z) == "bez_numeru"
    assert k.wynik(5, "poranna", {2: "zielony"}, z) == "zla_plytka"
    assert k.wynik(3, "okragla_wieczorna", {1: "zielony"}, z) == "brak_kalibracji"
    assert czekaj_na(lambda: program.logika.tryb == "gotowa", 3.0)   # pierscien nie zostaje w stanie "analiza"
    assert d.liczba("PUT", "/plan") == 0


def test_b1_ramka_w_tylko_ostatni_skan_skan_bez_numeru_ciemno(kal, sprzataj):
    """Runda 2, B1 (proba 1 A): plytka 1 zeskanowana (wynik na ramce), prace przelozone i ponowny skan bez numeru - stary
    wynik plytki 1 nie wraca (ani po skanie bez numeru, ani z kolejnym planem); ramka ciemna i "gotowa"."""
    program, atrapa, port, k, d = _wieczor(kal, sprzataj)
    kol = kolory_wieczor(kal)
    z1 = k.skanowanie()
    assert k.wynik(1, "wieczorna", kol, z1) == "wyslany"
    assert czekaj_na(lambda: program.logika.plan is not None, 3.0)
    put = d.liczba("PUT", "/plan")
    z2 = k.skanowanie()
    k.analiza()
    assert k.wynik(None, "wieczorna", kolory_wieczor(kal, przesuniecie=4), z2) == "bez_numeru"
    assert czekaj_na(lambda: program.logika.tryb == "gotowa" and not k.stan()["oczekuje"], 3.0)
    assert k.wynik(1, "wieczorna", kol, z1) == "niewazny"           # stary skan - nowszy skan juz byl
    time.sleep(0.3)
    assert program.logika.plan is None and d.liczba("PUT", "/plan") == put and k.stan()["wyniki"] == []
    atrapa.poloz_plytke(1)
    assert czekaj_na(lambda: program.logika.plytka == 1 and program.logika.plytka_pewna, 3.0)
    time.sleep(0.2)
    assert roznice_plytki(atrapa.klatka, {}) == []


def test_b1_ramka_w_blad_skanu_i_nowy_skan_bez_starego_wyniku(kal, sprzataj):
    """Runda 2, B1 (proba 1 B): wynik plytki 2, Spacja, skan zablokowany (`blad`), Spacja, wynik plytki 3 - plan
    zawiera TYLKO plytke 3."""
    program, atrapa, port, k, d = _wieczor(kal, sprzataj)
    z = k.skanowanie()
    assert k.wynik(2, "wieczorna", kolory_wieczor(kal), z) == "wyslany"
    assert czekaj_na(lambda: program.logika.plan is not None and sorted(program.logika.plan.plytki) == [2], 3.0)
    k.skanowanie()
    k.blad()
    z3 = k.skanowanie()
    assert k.wynik(3, "wieczorna", kolory_wieczor(kal, przesuniecie=1), z3) == "wyslany"
    assert czekaj_na(lambda: not k.stan()["oczekuje"] and program.logika.plan is not None
                     and sorted(program.logika.plan.plytki) == [3], 3.0), k.stan()
    time.sleep(0.3)
    assert sorted(program.logika.plan.plytki) == [3] and program.logika.tryb == "wynik"
    assert [sorted(json.loads(w["tresc"])["plytki"]) for w in d.zadania("PUT", "/plan")] == [["2"], ["3"]]


# ----------------------------------------------------------------------------- poranek

def _poranek(kal, sprzataj, **kw):
    program, atrapa, port = ramka_wewnatrz("P", **kw.pop("konf", {}))
    sprzataj.append(program.zatrzymaj)
    k, d = klient("P", port, kal, **kw)
    sprzataj.append(k.zatrzymaj)
    return program, atrapa, port, k, d


def test_poranek_zamknij_piec_zdarzenie_raz_potem_zgas(kal, sprzataj):
    program, atrapa, port, k, d = _poranek(kal, sprzataj)
    k.ustaw_plan_rano(plan_plytek_k1())
    assert czekaj_na(lambda: program.logika.plan is not None, 5.0)
    atrapa.poloz_plytke(4)
    assert czekaj_na(lambda: program.logika.plytka == 4 and program.logika.plytka_pewna, 2.0)
    atrapa.nacisnij("enter")
    atrapa.nacisnij("zamknij_piec")
    atrapa.nacisnij("enter")
    nowe = odbierz_n(k, 3)
    typy = [z["typ"] for z in nowe if z["typ"] in ("potwierdzenie", "zamknij_piec")]
    assert typy == ["potwierdzenie", "zamknij_piec"]
    zp = next(z for z in nowe if z["typ"] == "zamknij_piec")
    assert (zp["plan_id"], zp["plytka"]) == (PLAN_ID, 4)
    k.zgas()   # A12: sesja pieca zamknieta -> DELETE /plan
    assert czekaj_na(lambda: program.logika.plan is None and program.logika.tryb == "gotowa", 3.0)
    put = d.liczba("PUT", "/plan")
    time.sleep(0.5)
    assert d.liczba("PUT", "/plan") == put and program.logika.plan is None
    assert [z["typ"] for z in k.odbierz_zdarzenia()].count("zamknij_piec") == 0


def test_poranek_aktualizacja_planu_zachowuje_potwierdzenia_ta_sama_tresc_bez_wysylki(kal, sprzataj):
    program, atrapa, port, k, d = _poranek(kal, sprzataj)
    pp = plan_plytek_k1()
    k.ustaw_plan_rano(pp)
    assert czekaj_na(lambda: program.logika.plan is not None, 5.0)
    atrapa.poloz_plytke(4)
    assert czekaj_na(lambda: program.logika.plytka == 4 and program.logika.plytka_pewna, 2.0)
    atrapa.nacisnij("enter")
    atrapa.nacisnij("enter")
    potw = [[4, "3263"], [4, "3301"]]
    assert czekaj_na(lambda: k.potwierdzone() == potw, 3.0)
    wersja = program.logika.plan.wersja
    pp2 = plan_plytek_k1()
    pp2["plytki"]["5"] = {"gniazda": [{"id": 2, "kolor": "zielony", "kuweta": "3263"}]}
    pp2["uklady"]["5"] = "poranna"
    k.ustaw_plan_rano(pp2)
    assert czekaj_na(lambda: program.logika.plan.wersja > wersja and 5 in program.logika.plan.plytki, 3.0)
    s = program.logika.stan(program.zegar())
    assert s["potwierdzone"] == potw and s["kuweta"] == "0412"
    put = d.liczba("PUT", "/plan")
    k.ustaw_plan_rano(plan_plytek_k1() | {"plytki": pp2["plytki"], "uklady": pp2["uklady"]})
    time.sleep(0.5)
    assert d.liczba("PUT", "/plan") == put   # ta sama tresc - bez nowej wersji


def test_poranek_restart_programu_laptopa_przejmuje_stan_potwierdzen_z_ramki(kal, sprzataj):
    program, atrapa, port, k, d = _poranek(kal, sprzataj)
    k.ustaw_plan_rano(plan_plytek_k1())
    assert czekaj_na(lambda: program.logika.plan is not None, 5.0)
    atrapa.poloz_plytke(4)
    assert czekaj_na(lambda: program.logika.plytka == 4 and program.logika.plytka_pewna, 2.0)
    atrapa.nacisnij("enter")
    atrapa.nacisnij("enter")
    potw = [[4, "3263"], [4, "3301"]]
    assert czekaj_na(lambda: k.potwierdzone() == potw, 3.0)
    wersja = program.logika.plan.wersja
    k.zatrzymaj()
    k2, d2 = klient("P", port, kal)   # ten sam identyfikator laptopa, nowy program
    sprzataj.append(k2.zatrzymaj)
    k2.ustaw_plan_rano(plan_plytek_k1())
    assert czekaj_na(lambda: program.logika.plan is not None and program.logika.plan.wersja > wersja, 5.0), k2.stan()
    assert program.logika.stan(program.zegar())["potwierdzone"] == potw and k2.potwierdzone() == potw
    hist = [z for z in k2.odbierz_zdarzenia() if z["typ"] == "potwierdzenie"]
    assert [z["kuweta"] for z in hist] == ["3263", "3301"] and all(z["z_historii"] for z in hist)  # B3: historia oznaczona


def test_b3_restart_programu_historia_ramki_bez_utraty_i_bez_duplikatow(kal, sprzataj):
    """Runda 2, B3 (proba 4): potwierdzenie odebrane, program zatrzymany, technik potwierdza 2 kuwety, program startuje
    ponownie. Bez kursora: cala historia biezacego startu ramki (`z_historii`), po kluczu (start_id, nr) dokladnie
    2 nowe potwierdzenia, w kolejnosci. Z kursorem programu: tylko zdarzenia powyzej niego."""
    program, atrapa, port, k, d = _poranek(kal, sprzataj)
    k.ustaw_plan_rano(plan_plytek_k1())
    assert czekaj_na(lambda: program.logika.plan is not None, 5.0)
    atrapa.poloz_plytke(4)
    assert czekaj_na(lambda: program.logika.plytka == 4 and program.logika.plytka_pewna, 2.0)
    atrapa.nacisnij("enter")
    assert czekaj_na(lambda: k.potwierdzone() == [[4, "3263"]], 3.0)
    zapisane = {IND.klucz_zdarzenia(z) for z in k.odbierz_zdarzenia()}   # "baza" programu
    kursor = k.kursor
    k.zatrzymaj()
    atrapa.nacisnij("enter")
    atrapa.nacisnij("enter")
    assert czekaj_na(lambda: len(program.logika.stos.get(4, [])) == 3, 3.0)
    k2, _ = klient("P", port, kal)
    sprzataj.append(k2.zatrzymaj)
    assert czekaj_na(lambda: k2.kursor[0] == program.logika.start_id and k2.kursor[1] >= kursor[1] + 2, 5.0)
    hist = odbierz_n(k2, 1)
    assert all(z["z_historii"] for z in hist if z["nr"] <= kursor[1] + 2)
    nowe = [z for z in hist if IND.klucz_zdarzenia(z) not in zapisane]
    assert [(z["typ"], z["kuweta"]) for z in nowe if z["typ"] == "potwierdzenie"] == [("potwierdzenie", "3301"),
                                                                                      ("potwierdzenie", "0412")]
    assert len({IND.klucz_zdarzenia(z) for z in hist}) == len(hist)
    k3, _ = klient("P", port, kal, kursor=kursor)
    sprzataj.append(k3.zatrzymaj)
    assert czekaj_na(lambda: k3.kursor[1] >= kursor[1] + 2, 5.0)
    od_kursora = odbierz_n(k3, 2)
    assert [z["nr"] for z in od_kursora][:2] == [kursor[1] + 1, kursor[1] + 2] and all(z["nr"] > kursor[1] for z in od_kursora)
    assert [z["kuweta"] for z in od_kursora if z["typ"] == "potwierdzenie"][:2] == ["3301", "0412"]


def test_poranek_utracone_zdarzenia_stan_z_ramki(kal, sprzataj):
    """Dziennik ramki przepelniony, gdy laptop nie odpytywal (tu 5 zdarzen): laptop dostaje `utracone`, bierze stan
    potwierdzen z GET /stan i liczy utracone."""
    program, atrapa, port = ramka_wewnatrz("P")
    sprzataj.append(program.zatrzymaj)
    with program.warunek:
        program.logika.zdarzenia = collections.deque(program.logika.zdarzenia, maxlen=5)
    proxy = Posrednik(port)
    sprzataj.append(proxy.zamknij)
    k, d = klient("P", proxy.port, kal, odpytywanie_s=0.5)
    sprzataj.append(k.zatrzymaj)
    k.ustaw_plan_rano(plan_plytek_k5())
    assert czekaj_na(lambda: program.logika.plan is not None, 5.0)
    atrapa.poloz_plytke(4)
    assert czekaj_na(lambda: program.logika.plytka == 4 and program.logika.plytka_pewna, 2.0)
    assert _odebral_wszystko(k, program)
    proxy.awaria = True
    for _ in range(4):
        atrapa.nacisnij("enter")
    for _ in range(3):
        atrapa.nacisnij("backspace")
    for _ in range(3):
        atrapa.nacisnij("enter")
    assert czekaj_na(lambda: len(program.logika.stos.get(4, [])) == 4 and program.logika.nr >= 12, 3.0)
    proxy.awaria = False
    assert czekaj_na(lambda: k.stan()["utracone"] > 0, 5.0)
    potw = [[4, kk] for kk in K5_KUWETY[:4]]
    assert czekaj_na(lambda: k.potwierdzone() == potw, 5.0), k.stan()


# ----------------------------------------------------------------------------- kolejka polecen, klucz, drugi laptop

def test_jedna_kolejka_polecen_spacja_anuluje_oczekujacy_plan(kal, sprzataj):
    """Bez sieci: Spacja, wynik (plan czeka), Spacja ponownie. Po powrocie sieci ramka dostaje tylko PUT /tryb - stary
    wynik nie przychodzi pozniej z kolejki; polecenia ida szeregowo (zadne dwa naraz)."""
    program, atrapa, port = ramka_wewnatrz("W")
    sprzataj.append(program.zatrzymaj)
    proxy = Posrednik(port)
    sprzataj.append(proxy.zamknij)
    k, d = klient("W", proxy.port, kal)
    sprzataj.append(k.zatrzymaj)
    assert czekaj_na(lambda: k.stan()["polaczona"], 5.0)
    proxy.awaria = True
    z = k.skanowanie()
    assert k.wynik(2, "wieczorna", kolory_wieczor(kal), z) == "wyslany"
    time.sleep(0.3)
    k.skanowanie()
    proxy.awaria = False
    assert czekaj_na(lambda: program.logika.tryb == "skanowanie", 5.0)
    time.sleep(0.5)
    assert program.logika.plan is None and program.logika.tryb == "skanowanie"
    dotarly = [w for w in d.wpisy if w["kierunek"] == "z_ramki" and w["metoda"] == "PUT" and w["sciezka"] == "/plan"]
    assert dotarly == []
    # szeregowo: po kazdym poleceniu (PUT / DELETE) najpierw jego odpowiedz albo blad, potem nastepne polecenie
    otwarte = None
    for w in d.wpisy:
        if w["metoda"] in ("PUT", "DELETE"):
            if w["kierunek"] == "do_ramki":
                assert otwarte is None, "dwa polecenia do ramki naraz"
                otwarte = w["nr"]
            else:
                assert w["nr"] == otwarte
                otwarte = None


def test_zly_klucz_401_bez_petli_dobry_klucz_w_kazdym_zadaniu(kal, sprzataj):
    klucz = secrets.token_hex(24)
    KLUCZE_TESTOW.add(klucz)
    program, atrapa, port = ramka_wewnatrz("P", klucz=klucz)
    sprzataj.append(program.zatrzymaj)
    zly = secrets.token_hex(24)
    KLUCZE_TESTOW.add(zly)
    k, d = klient("P", port, kal, klucz=zly)
    sprzataj.append(k.zatrzymaj)
    k.ustaw_plan_rano(plan_plytek_k5())
    assert czekaj_na(lambda: k.stan()["blad"] == "zly_klucz", 3.0), k.stan()
    n = len(d.zadania())
    time.sleep(1.5)
    assert len(d.zadania()) <= n + 1 and program.logika.plan is None   # bez ponawiania w petli
    k2, d2 = klient("P", port, kal, klucz=klucz)
    sprzataj.append(k2.zatrzymaj)
    k2.ustaw_plan_rano(plan_plytek_k5())
    assert czekaj_na(lambda: program.logika.plan is not None, 5.0)
    assert all(w["naglowki"].get("X-Ramka-Klucz") == "***" for w in d2.zadania())  # w kazdym zadaniu, w dzienniku ukryty


def test_drugi_laptop_jasny_komunikat_plan_pierwszego_zostaje(kal, sprzataj):
    program, atrapa, port, k, d = _poranek(kal, sprzataj)
    k.ustaw_plan_rano(plan_plytek_k5())
    assert czekaj_na(lambda: program.logika.plan is not None, 5.0)
    k2, _ = klient("P", port, kal, laptop_id="lap-test-drugi")
    sprzataj.append(k2.zatrzymaj)
    k2.ustaw_plan_rano(plan_plytek_k1())
    assert czekaj_na(lambda: k2.stan()["blad"] == "inny_laptop", 5.0), k2.stan()
    assert "drugi laptop" in k2.stan()["komunikat"].lower()
    assert program.logika.plan.plan_id == "2026-11-18-p5"


def test_p2_inny_laptop_bez_automatycznego_przejecia_ramki_do_wznow(kal, sprzataj):
    """Runda 2, P2 (proba 5): drugi laptop B dostaje `inny_laptop`; wlasciciel A milknie dluzej niz limit lacznosci
    ramki (tu 2 s) - B NIE przejmuje ramki sam (plan B nie pojawia sie, komunikat zostaje); dopiero `wznow()` (decyzja
    czlowieka) wysyla plan B."""
    program, atrapa, port, k, d = _poranek(kal, sprzataj, konf={"limit_lacznosci_s": 2.0})
    k.ustaw_plan_rano(plan_plytek_k5())
    assert czekaj_na(lambda: program.logika.plan is not None, 5.0)
    kb, db = klient("P", port, kal, laptop_id="lap-test-b")
    sprzataj.append(kb.zatrzymaj)
    kb.ustaw_plan_rano(plan_plytek_k1(plan_id="2026-11-17-p3"))
    assert czekaj_na(lambda: kb.stan()["blad"] == "inny_laptop" and kb.stan()["wstrzymane"], 5.0), kb.stan()
    k.zatrzymaj()                     # wlasciciel milknie (uspienie, przerwa Wi-Fi, zamkniety program)
    time.sleep(4.0)
    assert program.logika.plan is None or program.logika.plan.plan_id != "2026-11-17-p3"
    s = kb.stan()
    assert s["blad"] == "inny_laptop" and s["wstrzymane"] and "drugi laptop" in s["komunikat"].lower()
    assert db.liczba("PUT", "/plan") <= 1          # najwyzej pierwsza, odrzucona proba - bez ponawiania
    kb.wznow()
    assert czekaj_na(lambda: program.logika.plan is not None and program.logika.plan.plan_id == "2026-11-17-p3", 3.0)
    assert kb.stan()["blad"] is None


def test_b2_zatrzymaj_wysyla_zgaszenie_a_nowe_uruchomienie_gasi_zastany_plan(kal, sprzataj):
    """Runda 2, B2 (proba 2): (a) `zgas()` tuz przed zamknieciem programu - `DELETE` wychodzi w `zatrzymaj()`, nawet gdy
    kolejka polecen go nie wyslala; (b) poprzednie uruchomienie zostawilo plan na ramce, nowe uruchomienie z tym samym
    identyfikatorem laptopa bez otwartego pieca - plan zgaszony przy pierwszym kontakcie; (c) to samo dla ramki W."""
    program, atrapa, port = ramka_wewnatrz("P")
    sprzataj.append(program.zatrzymaj)
    k, d = klient("P", port, kal)
    k.ustaw_plan_rano(plan_plytek_k5())
    assert czekaj_na(lambda: program.logika.plan is not None, 5.0)
    k._wybierz = lambda: None         # kolejka polecen nie wysle juz niczego (np. w przerwie po bledzie sieci)
    k.zgas()
    t0 = time.perf_counter()
    k.zatrzymaj()
    dt = time.perf_counter() - t0
    assert dt < 1.0 and program.logika.plan is None and d.liczba("DELETE", "/plan") == 1, dt
    k2, _ = klient("P", port, kal)
    k2.ustaw_plan_rano(plan_plytek_k5(plan_id="2026-11-18-p6"))
    assert czekaj_na(lambda: program.logika.plan is not None and program.logika.plan.plan_id == "2026-11-18-p6", 5.0)
    k2.zatrzymaj()                    # bez zgas(): plan zostaje na ramce (i bylby podtrzymywany tym samym X-Laptop-Id)
    assert program.logika.plan is not None
    k3, d3 = klient("P", port, kal)
    sprzataj.append(k3.zatrzymaj)
    assert czekaj_na(lambda: program.logika.plan is None, 3.0)
    assert d3.liczba("DELETE", "/plan") == 1 and d3.liczba("PUT", "/plan") == 0
    progw, atrw, portw = ramka_wewnatrz("W")
    sprzataj.append(progw.zatrzymaj)
    kw, _ = klient("W", portw, kal)
    assert czekaj_na(lambda: kw.stan()["polaczona"], 5.0)
    z = kw.skanowanie()
    assert kw.wynik(2, "wieczorna", kolory_wieczor(kal), z) == "wyslany"
    assert czekaj_na(lambda: progw.logika.plan is not None, 3.0)
    kw.zatrzymaj()
    kw2, dw2 = klient("W", portw, kal)
    sprzataj.append(kw2.zatrzymaj)
    assert czekaj_na(lambda: progw.logika.plan is None and progw.logika.tryb == "gotowa", 3.0)
    assert dw2.liczba("PUT", "/plan") == 0


def test_p1_zatrzymaj_ponizej_1_s_przy_wiszacym_odpytywaniu_i_wiszacej_ramce(kal, sprzataj):
    """Runda 2, P1 (proby 3, 3b): Windows - `shutdown` nie przerywa `recv`; `zatrzymaj()` ma trwac ponizej 1 s przy
    dlugim odpytywaniu w toku, przy ramce, ktora przyjmuje polaczenie i nie odpowiada (z oczekujacym zgaszeniem),
    i dla `Indicate` z dwiema takimi ramkami; watki sa daemon i koncza sie."""
    program, atrapa, port = ramka_wewnatrz("P")
    sprzataj.append(program.zatrzymaj)
    k, _ = klient("P", port, kal, odpytywanie_s=25.0)
    assert czekaj_na(lambda: k.stan()["polaczona"] and k.kursor[1] == program.logika.nr, 3.0)
    time.sleep(0.3)                   # dlugie odpytywanie w toku (ramka czeka do 10 s)
    watki = list(k._watki)
    t0 = time.perf_counter()
    k.zatrzymaj()
    czasy = [time.perf_counter() - t0]
    assert all(w.daemon for w in watki) and czekaj_na(lambda: not any(w.is_alive() for w in watki), 2.0)
    gluchy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # przyjmuje polaczenie (kolejka), nie odpowiada
    gluchy.bind(("127.0.0.1", 0))
    gluchy.listen(8)
    sprzataj.append(gluchy.close)
    port_g = gluchy.getsockname()[1]
    k2, _ = klient("P", port_g, kal)
    time.sleep(0.3)
    k2.zgas()
    t0 = time.perf_counter()
    k2.zatrzymaj()
    czasy.append(time.perf_counter() - t0)
    ind = IND.Indicate(klient("W", port_g, kal)[0], klient("P", port_g, kal)[0])
    time.sleep(0.3)
    ind.poranna.zgas()
    t0 = time.perf_counter()
    ind.zatrzymaj()
    czasy.append(time.perf_counter() - t0)
    print(f"POMIAR P1: zatrzymaj() {', '.join(f'{c:.3f}' for c in czasy)} s (odpytywanie w toku, gluchy host, Indicate)")
    assert max(czasy) < 1.0, czasy


def test_zmiana_pieca_w_trakcie_wysylki_planu(kal, sprzataj):
    """Recenzja PR #28, proba 6: nowy piec ustawiony w chwili wysylki planu poprzedniego - p1 przyjety, zgaszony
    (DELETE), potem p2; na ramce zostaje p2."""
    program, atrapa, port, k, d = _poranek(kal, sprzataj)
    raz = []

    def hak():
        if not raz:
            raz.append(1)
            k.ustaw_plan_rano(plan_plytek_k5(plan_id="2026-11-18-p2"))

    k.przed_wyslaniem_planu = hak
    k.ustaw_plan_rano(plan_plytek_k5(plan_id="2026-11-18-p1"))
    assert czekaj_na(lambda: program.logika.plan is not None and program.logika.plan.plan_id == "2026-11-18-p2", 5.0)
    time.sleep(0.3)
    assert program.logika.plan.plan_id == "2026-11-18-p2"
    with program.warunek:
        dz = [(z["typ"], z.get("plan_id"), z.get("przyczyna")) for z in program.logika.zdarzenia
              if z["typ"] in ("plan_przyjety", "zgaszono")]
    assert dz == [("plan_przyjety", "2026-11-18-p1", None), ("zgaszono", "2026-11-18-p1", "usuniecie"),
                  ("plan_przyjety", "2026-11-18-p2", None)]


# ----------------------------------------------------------------------------- ustawienia i plan z SesjaRano

def test_z_ustawien_hosty_klucz_kalibracja_i_staly_identyfikator_laptopa(tmp_path):
    from stanowisko import ustawienia as UST

    ust = UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU)
    ust["sciezki"]["kalibracja_ramek"] = (tmp_path / "kal" / "kalibracja_ramek.json").as_posix()
    dane = tmp_path / "dane"
    ind = IND.Indicate.z_ustawien(ust, katalog_danych=dane)
    assert ind.wieczorna.adres == (ust["ramki"]["wieczorna_host"], ust["ramki"]["port"])
    assert ind.poranna.adres == (ust["ramki"]["poranna_host"], ust["ramki"]["port"])
    assert ind.wieczorna.rola == "W" and ind.poranna.rola == "P"
    # brak pliku kalibracji: wartosci startowe z geometrii plytek + ostrzezenie (plik nie jest zapisywany)
    assert any("kalibrac" in o for o in ind.poranna.stan()["ostrzezenia"])
    assert not (tmp_path / "kal" / "kalibracja_ramek.json").exists()
    lid = ind.poranna.laptop_id
    assert RPR.WZOR_ID.fullmatch(lid) and lid == ind.wieczorna.laptop_id
    # staly dla instalacji: plik w katalogu danych programu, niezaleznie od miejsca pliku kalibracji (D9)
    assert (dane / IND.PLIK_ID_LAPTOPA).read_text(encoding="ascii").strip() == lid
    assert not (tmp_path / "kal" / IND.PLIK_ID_LAPTOPA).exists()
    assert IND.Indicate.z_ustawien(ust, katalog_danych=dane).poranna.laptop_id == lid
    # plik kalibracji jest - uzyty; zly plik - ramka bez planow (ciemno) i ostrzezenie, program dziala dalej
    kalibracja.zapisz(kalibracja.domyslna(MODELE), tmp_path / "kal" / "kalibracja_ramek.json")
    assert IND.Indicate.z_ustawien(ust, katalog_danych=dane).poranna.stan()["ostrzezenia"] == []
    (tmp_path / "kal" / "kalibracja_ramek.json").write_text("{}", encoding="ascii")
    ind3 = IND.Indicate.z_ustawien(ust, katalog_danych=dane)
    assert ind3.poranna.stan()["ostrzezenia"] and ind3.poranna.kalibracja is None


def test_plan_z_prawdziwej_sesji_rano_na_atrapie(kal, tmp_path, sprzataj):
    """`SesjaRano.plan_plytek` (A6) -> indicate -> atrapa ramki P: plan przyjety, plytki 4 i 5, obraz plytki 4 zgodny
    z planem (biezaca kuweta + prace bez kuwety)."""
    import test_session_rano as TSR

    st = TSR.Stanowisko(tmp_path)
    sprzataj.append(st.sesja.baza.zamknij)
    TSR.wypelnij_indeks(st.sesja.baza)
    st.skan(TSR.rano(4, "2026-11-18T07:00:00", [{"g": 2, "k": [["X11", 0.95]]}, {"g": 3, "k": [["X12", 0.95]]},
                                                {"g": 4, "k": [["Y21", 0.95]]}, {"g": 5, "k": [["Z31", 0.95]]},
                                                {"g": 6, "k": [["V36", 0.95]]}, {"g": 7, "k": []}]))
    st.skan(TSR.rano(5, "2026-11-18T07:02:00", [{"g": 2, "k": [["X13", 0.95]]}, {"g": 3, "k": [["Y22", 0.95]]},
                                                {"g": 4, "k": [["Q46", 0.95]]}]))
    pp = st.rano.plan_plytek()
    program, atrapa, port, k, d = _poranek(kal, sprzataj)
    assert k.ustaw_plan_rano(pp)["zla_plytka"] == []
    assert czekaj_na(lambda: program.logika.plan is not None and program.logika.plan.plan_id == pp["plan_id"], 5.0)
    assert sorted(program.logika.plan.plytki) == [4, 5]
    atrapa.poloz_plytke(4)
    pierwsza = pp["kuwety"][0]["kuweta"]
    gn = pp["plytki"]["4"]["gniazda"]
    kolory = {g["id"]: g["kolor"] for g in gn if g.get("kuweta") in (None, pierwsza)}
    ocz = piksele(kal, "P", pp["uklady"]["4"], kolory)
    assert atrapa.czekaj(lambda a: roznice_plytki(a.klatka, ocz) == [], 3.0)
    assert pierwsza == "3263" and {6, 7} <= set(kolory)


# ----------------------------------------------------------------------------- pliki

def test_pliki_indicate_ascii_tylko_biblioteka_standardowa():
    dozwolone_obce = {"stanowisko", "ramka"}
    for nazwa in ("indicate.py", "ramka_protokol.py"):
        sciezka = STANOWISKO / "stanowisko" / nazwa
        dane = sciezka.read_bytes()
        assert all(b < 128 for b in dane), nazwa
        drzewo = ast.parse(dane.decode("ascii"))
        for wezel in ast.walk(drzewo):
            if isinstance(wezel, ast.Import):
                moduly = [a.name.split(".")[0] for a in wezel.names]
            elif isinstance(wezel, ast.ImportFrom):
                moduly = [(wezel.module or "").split(".")[0]] if wezel.level == 0 else []
            else:
                continue
            for m in moduly:
                assert m in sys.stdlib_module_names or m in dozwolone_obce, (nazwa, m)


# ----------------------------------------------------------------------------- K8: caly ruch (ostatni test pliku)

def test_zz_k8_caly_ruch_sieciowy_testow_bez_nazw_folderow_i_nazwisk(kal, sprzataj):
    """Test ma WLASNY ruch (nie zalezy od kolejnosci ani od innych testow - D11): ramka P z kluczem przez posrednik TCP
    (surowe bajty), plan z nazwami w polach pomocniczych i w miejscu numerow kuwet (jak bledny plan z sesji), nowy piec
    (DELETE), ramka W (PUT /tryb). Sprawdzany jest caly zapis ruchu: ten test i wszystko, co zapisaly wczesniej
    uruchomione testy pliku (dzienniki klientow, posredniki TCP, zadania testow). Klucz moze wystapic w surowych bajtach
    tylko w naglowku X-Ramka-Klucz."""
    klucz = secrets.token_hex(24)
    KLUCZE_TESTOW.add(klucz)
    program, atrapa, port = ramka_wewnatrz("P", klucz=klucz)
    sprzataj.append(program.zatrzymaj)
    proxy = Posrednik(port)
    sprzataj.append(proxy.zamknij)
    k, d = klient("P", proxy.port, kal, klucz=klucz)
    sprzataj.append(k.zatrzymaj)
    pp = plan_plytek_k1()
    pp["plytki"]["4"]["gniazda"][0]["kuweta"] = FOLDERY[0]
    pp["kuwety"].append({"kuweta": FOLDERY[1], "plytki": [4]})
    pp["braki"] += [NAZWISKA[3]]
    pp["opisy"] = {k_: f for k_, f in zip(("3263", "3301", "0412", "#1234", "3999", "4100"), FOLDERY)}
    k.ustaw_plan_rano(pp)
    assert czekaj_na(lambda: program.logika.plan is not None, 5.0)
    k.ustaw_plan_rano(plan_plytek_k5(plan_id="2026-11-18-p9"))
    assert czekaj_na(lambda: program.logika.plan is not None and program.logika.plan.plan_id == "2026-11-18-p9", 5.0)
    progw, atrw, portw = ramka_wewnatrz("W")
    sprzataj.append(progw.zatrzymaj)
    kw, _ = klient("W", portw, kal)
    sprzataj.append(kw.zatrzymaj)
    assert czekaj_na(lambda: kw.stan()["polaczona"], 5.0)
    kw.skanowanie()
    assert czekaj_na(lambda: progw.logika.tryb == "skanowanie", 3.0)
    with _RUCH_BLOK:
        ruch = list(RUCH)
    calosc = b"\n".join(ruch).decode("utf-8", "replace").lower()
    rodzaje = set()
    for b in ruch:
        try:
            w = json.loads(b)
        except ValueError:
            continue
        if isinstance(w, dict) and w.get("kierunek") == "do_ramki":
            rodzaje.add((w["metoda"], w["sciezka"].split("?")[0]))
    assert {("GET", "/stan"), ("GET", "/zdarzenia"), ("PUT", "/plan"), ("PUT", "/tryb"), ("DELETE", "/plan")} <= rodzaje
    trafienia = [n for n in NAZWISKA + FOLDERY if n.lower() in calosc]
    poza_naglowkiem = [x for x in KLUCZE_TESTOW if calosc.count(x.lower()) != calosc.count("x-ramka-klucz: " + x.lower())]
    w_naglowku = calosc.count("x-ramka-klucz: " + klucz.lower())
    print(f"POMIAR K8: {len(ruch)} zapisow ruchu ({len(calosc)} znakow), trafien nazw {len(trafienia)}, kluczy poza "
          f"naglowkiem {len(poza_naglowkiem)} (klucz w naglowku surowych zadan: {w_naglowku} razy)")
    assert trafienia == [] and poza_naglowkiem == [] and w_naglowku > 0
    assert not re.search(r"\b[a-z]:\\", calosc) and "/users/" not in calosc
