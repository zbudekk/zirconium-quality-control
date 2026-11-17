"""Protokol ramka <-> laptop, wersja 1: stale, limity i walidacja tresci zadan.

Specyfikacja (kontrakt dla strony laptopa) jest w README.md, rozdzial "Protokol v1".
Zasada danych osobowych (I7): walidacja jest scisla - nieznane pola sa odrzucane, a numery
kuwet musza byc cyframi (opcjonalnie z "#"), wiec nazwa folderu ani nazwisko nie przejda.
Komunikaty bledow nigdy nie powtarzaja wartosci z zadania (tylko sciezke pola).
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, field

from . import obraz

PROTOKOL = 1

# ---------------------------------------------------------------- DECYZJE ROBOCZE (17.11.2026)
# Wartosci przyjete przez koordynatora do decyzji wlasciciela - zmieniac TYLKO tutaj (opis: README,
# "Decyzje robocze"). Ramka trzyma plan bez kontaktu z laptopem najwyzej tyle sekund (twarda granica
# ramki; wieksze `wazny_s` z planu jest przycinane).
MAX_WAZNY_S_ROLI = {"W": 30.0, "P": 600.0}
# "Zamknij piec" w dwoch krokach: klawisz, potem Enter w ciagu tylu sekund.
CZAS_POTWIERDZENIA_ZAMKNIECIA_S = 5.0
# Wynik plytki kasowany przy jej zdjeciu z ramki (wieczor: zawsze; rano: plytki wracaja na ramke).
KASUJ_PO_ZDJECIU_ROLI = {"W": True, "P": False}
# Wpisywane cyfry (wybor kuwety) kasowane po tylu sekundach od ostatniego klawisza (D3).
CZAS_WPISYWANIA_S = 10.0
# Wyglad marginesu (napisy "3263 3", "PIEC?", prawy margines) - roboczy, ocena na zlozonej ramce (G2).
# ----------------------------------------------------------------

STANY = ("gotowa", "skanowanie", "analiza", "wynik", "blad", "test_led")  # stany ramki w GET /stan
# Stany ustawiane przez PUT /tryb - bez "wynik": stan wynik ustawia wylacznie przyjety plan (P2).
STANY_TRYBU = ("gotowa", "skanowanie", "analiza", "blad", "test_led")
KOLORY_GNIAZD = tuple(obraz.KOLORY)
TRYBY_PLANU = ("rano", "wieczor")
TRYB_ROLI = {"W": "wieczor", "P": "rano"}
RODZINY = {"W": (1, 2, 3), "P": (4, 5, 6)}  # numery plytek ramki (plan_ramki_v2 D11)
KOLEJNOSCI = ("liczba", "numer", "reczna")
KLAWISZE =("enter", "backspace", "zamknij_piec") + tuple("0123456789")
POLA_TYLKO_RANO = ("kuwety", "potwierdzone", "wybrane", "braki")  # plus "kuweta" przy gniezdzie
# Odrzucenia, ktore NIE gasza obrazu: polecenie starsze niz obraz, nie od wlasciciela albo nie
# do tej ramki / tego startu. Kazde inne odrzucenie PUT /plan i PUT /tryb od wlasciciela gasi (P5).
KODY_BEZ_ZMIANY_OBRAZU = frozenset({
    "inny_laptop", "inny_start", "plan_starszy", "plan_zgaszony", "zdarzenia_nieodebrane",
    "blad_sprzetu", "brak_laptopa", "zly_laptop"})

MAX_TRESC = 65536            # bajtow w tresci zadania
MAX_TRESC_ODCZYT = 1048576   # tyle najwyzej czytamy i wyrzucamy przy zbyt duzej tresci
MAX_PLYTKA = 7
MAX_ID_GNIAZDA = 64
MAX_GNIAZD_PLYTKI = 48
MAX_PIKSELI_PLYTKI = 800
MAX_BOK_BLOKU = 24
MAX_KUWET = 200
MAX_BRAKOW = 100
MAX_WAZNY_S = 3600.0
MIN_WAZNY_S = 1.0
CZEKAJ_MAX_S = 25.0
LIMIT_ZDARZEN_MAX = 500

WZOR_KUWETY = re.compile(r"^#?[0-9]{1,6}$")
WZOR_ID = re.compile(r"^[A-Za-z0-9._-]{1,40}$")
WZOR_START = re.compile(r"^[0-9a-f]{4,32}$")
WZOR_UKLADU = re.compile(r"^[a-z0-9_]{1,40}$")
WZOR_KLUCZA = re.compile(r"^[\x21-\x7e]{16,256}$")  # wspolny klucz (P6): drukowalne ASCII bez odstepu


def cyfry(tekst) -> bool:
    """Napis z samych cyfr ASCII (isdigit() przyjmuje tez np. cyfre arabska 4 - D4)."""
    return isinstance(tekst, str) and tekst.isascii() and tekst.isdigit()


class BladProtokolu(Exception):
    """Blad zadania: status HTTP, kod (staly napis) i opis bez danych z zadania."""

    def __init__(self, status: int, kod: str, opis: str = ""):
        super().__init__(f"{status} {kod}: {opis}")
        self.status = status
        self.kod = kod
        self.opis = opis

    def jako_json(self) -> dict:
        return {"protokol": PROTOKOL, "blad": {"kod": self.kod, "opis": self.opis}}


@dataclass
class Gniazdo:
    id: int
    px: tuple
    kolor: str
    kuweta: object = None


@dataclass
class PlanPlytki:
    uklad: str
    gniazda: list


@dataclass
class Kuweta:
    kuweta: str
    prac: int
    plytki: tuple


@dataclass
class Plan:
    plan_id: str
    wersja: int
    start_id: str
    zdarzenia_do: int
    wazny_s: float
    tryb: str
    kolejnosc: object
    plytki: dict
    kuwety: list
    potwierdzone: list
    wybrane: dict
    braki: list
    odcisk: str
    kolejnosc_kuwet: dict = field(default_factory=dict)


def _blad(kod: str, opis: str, status: int = 400):
    raise BladProtokolu(status, kod, opis)


def _obiekt(d, sciezka: str, wymagane, opcjonalne=()):
    if not isinstance(d, dict):
        _blad("zle_pole", f"{sciezka}: oczekiwano obiektu JSON")
    dozwolone = set(wymagane) | set(opcjonalne)
    nieznane = [k for k in d if k not in dozwolone]
    if nieznane:
        _blad("nieznane_pole", f"{sciezka}: nieznane pola ({len(nieznane)})")
    for k in wymagane:
        if k not in d:
            _blad("brak_pola", f"{sciezka}.{k}: brak pola")


def _calkowita(v, sciezka: str, lo: int, hi: int, kod: str = "zle_pole") -> int:
    if isinstance(v, bool) or not isinstance(v, int) or not (lo <= v <= hi):
        _blad(kod, f"{sciezka}: oczekiwano liczby calkowitej {lo}..{hi}")
    return v


def _liczba(v, sciezka: str, lo: float, hi: float) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or not (lo <= v <= hi):
        _blad("zle_pole", f"{sciezka}: oczekiwano liczby {lo:g}..{hi:g}")
    return float(v)


def _napis(v, sciezka: str, wzor, kod: str = "zle_pole") -> str:
    if not isinstance(v, str) or not wzor.match(v):
        _blad(kod, f"{sciezka}: niedozwolony napis")
    return v


def _lista(v, sciezka: str, maks: int, kod_dlugosci: str = "zle_pole") -> list:
    if not isinstance(v, list):
        _blad("zle_pole", f"{sciezka}: oczekiwano listy")
    if len(v) > maks:
        _blad(kod_dlugosci, f"{sciezka}: za dlugo (maks. {maks})")
    return v


def _numer_plytki(klucz, sciezka: str) -> int:
    if cyfry(klucz) and len(klucz) <= 2:
        n = int(klucz)
    elif isinstance(klucz, int) and not isinstance(klucz, bool):
        n = klucz
    else:
        _blad("zla_plytka", f"{sciezka}: numer plytki 1..{MAX_PLYTKA}")
    if not (1 <= n <= MAX_PLYTKA):
        _blad("zla_plytka", f"{sciezka}: numer plytki 1..{MAX_PLYTKA}")
    return n


def odcisk_planu(d: dict) -> str:
    """Odcisk tresci planu bez pol transportowych (start_id, zdarzenia_do)."""
    tresc = {k: v for k, v in d.items() if k not in ("start_id", "zdarzenia_do")}
    return hashlib.sha256(json.dumps(tresc, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _sprawdz_gniazda(lista, sciezka: str, rano: bool = True) -> list:
    _lista(lista, sciezka, MAX_GNIAZD_PLYTKI, "za_duzo_gniazd")
    wynik = []
    ids = set()
    zajete = set()
    pikseli = 0
    for n, g in enumerate(lista):
        sg = f"{sciezka}[{n}]"
        _obiekt(g, sg, ("id", "px", "kolor"), ("kuweta",))
        gid = _calkowita(g["id"], sg + ".id", 1, MAX_ID_GNIAZDA, "nieznane_gniazdo")
        if gid in ids:
            _blad("nieznane_gniazdo", f"{sg}.id: powtorzone id gniazda")
        ids.add(gid)
        px = g["px"]
        if not isinstance(px, list) or len(px) != 4:
            _blad("zle_pole", f"{sg}.px: oczekiwano [x, y, szerokosc, wysokosc]")
        x = _calkowita(px[0], sg + ".px[0]", 0, obraz.SZEROKOSC - 1, "px_poza_plytka")
        y = _calkowita(px[1], sg + ".px[1]", 0, obraz.WYSOKOSC - 1, "px_poza_plytka")
        w = _calkowita(px[2], sg + ".px[2]", 1, MAX_BOK_BLOKU)
        h = _calkowita(px[3], sg + ".px[3]", 1, MAX_BOK_BLOKU)
        if not obraz.w_obszarze_plytki(x, y, w, h):
            _blad("px_poza_plytka", f"{sg}.px: blok poza obszarem plytki")
        if not isinstance(g["kolor"], str) or g["kolor"] not in obraz.KOLORY:
            _blad("zly_kolor", f"{sg}.kolor: nieznany kolor")
        kuw = g.get("kuweta")
        if kuw is not None and not rano:
            # B1: regula "swieci tylko biezaca kuweta" jest wylacznie poranna - plan wieczorny z kuweta
            # przy gniezdzie to blad laptopa, odrzucany (i gaszacy obraz), nie cicho pomijany
            _blad("pole_tylko_rano", f"{sg}.kuweta: kuweta przy gniezdzie tylko w planie rano")
        if kuw is not None:
            _napis(kuw, sg + ".kuweta", WZOR_KUWETY, "zla_kuweta")
        pikseli += w * h
        if pikseli > MAX_PIKSELI_PLYTKI:
            _blad("za_duzo_pikseli", f"{sciezka}: ponad {MAX_PIKSELI_PLYTKI} pikseli na plytke")
        blok = {(xx, yy) for yy in range(y, y + h) for xx in range(x, x + w)}
        if blok & zajete:
            _blad("px_nakladanie", f"{sg}.px: blok naklada sie na inne gniazdo")
        zajete |= blok
        wynik.append(Gniazdo(gid, (x, y, w, h), g["kolor"], kuw))
    return wynik


def sprawdz_plan(d, rola: str, rodzina=None) -> Plan:
    """Waliduje tresc PUT /plan; zwraca Plan albo zglasza BladProtokolu (400 / 409)."""
    if not isinstance(d, dict):
        _blad("zly_json", "tresc nie jest obiektem JSON")
    _obiekt(d, "plan", ("protokol", "plan_id", "wersja", "start_id", "zdarzenia_do", "wazny_s", "tryb", "plytki"),
            ("kolejnosc", "kuwety", "potwierdzone", "wybrane", "braki"))
    if d["protokol"] != PROTOKOL or isinstance(d["protokol"], bool):
        _blad("zly_protokol", f"plan.protokol: obslugiwana wersja {PROTOKOL}")
    plan_id = _napis(d["plan_id"], "plan.plan_id", WZOR_ID)
    wersja = _calkowita(d["wersja"], "plan.wersja", 0, 10 ** 9)
    start_id = _napis(d["start_id"], "plan.start_id", WZOR_START)
    zdarzenia_do = _calkowita(d["zdarzenia_do"], "plan.zdarzenia_do", 0, 10 ** 12)
    wazny_s = _liczba(d["wazny_s"], "plan.wazny_s", MIN_WAZNY_S, MAX_WAZNY_S)
    tryb = d["tryb"]
    if tryb not in TRYBY_PLANU:
        _blad("zle_pole", "plan.tryb: rano albo wieczor")
    if tryb != TRYB_ROLI[rola]:
        _blad("plan_innej_ramki", f"plan.tryb: ta ramka przyjmuje plany '{TRYB_ROLI[rola]}'", 409)
    rano = tryb == "rano"
    if not rano:
        for pole in POLA_TYLKO_RANO:
            if pole in d:
                _blad("pole_tylko_rano", f"plan.{pole}: pole tylko w planie rano")
    kolejnosc = d.get("kolejnosc")
    if kolejnosc is not None and kolejnosc not in KOLEJNOSCI:
        _blad("zle_pole", "plan.kolejnosc: liczba, numer albo reczna")
    rodzina = tuple(rodzina) if rodzina else RODZINY[rola]

    plytki_d = d["plytki"]
    if not isinstance(plytki_d, dict):
        _blad("zle_pole", "plan.plytki: oczekiwano obiektu")
    if len(plytki_d) > MAX_PLYTKA:
        _blad("zla_plytka", "plan.plytki: za duzo plytek")
    plytki = {}
    for klucz, wpis in plytki_d.items():
        n = _numer_plytki(klucz, "plan.plytki")
        sp = f"plan.plytki.{n}"
        if n not in rodzina:
            _blad("zla_plytka", f"{sp}: plytka spoza rodziny tej ramki {list(rodzina)}")
        if n in plytki:
            _blad("zla_plytka", f"{sp}: powtorzona plytka")
        _obiekt(wpis, sp, ("uklad", "gniazda"))
        uklad = _napis(wpis["uklad"], sp + ".uklad", WZOR_UKLADU)
        plytki[n] = PlanPlytki(uklad, _sprawdz_gniazda(wpis["gniazda"], sp + ".gniazda", rano))

    kuwety = []
    znane = {}
    for n, k in enumerate(_lista(d.get("kuwety", []), "plan.kuwety", MAX_KUWET)):
        sk = f"plan.kuwety[{n}]"
        _obiekt(k, sk, ("kuweta",), ("prac", "plytki"))
        nazwa = _napis(k["kuweta"], sk + ".kuweta", WZOR_KUWETY, "zla_kuweta")
        if nazwa in znane:
            _blad("zle_pole", f"{sk}.kuweta: powtorzona kuweta")
        prac = _calkowita(k.get("prac", 0), sk + ".prac", 0, 999)
        pl = _lista(k.get("plytki", []), sk + ".plytki", MAX_PLYTKA)
        pl_n = tuple(_calkowita(p, sk + ".plytki", 1, MAX_PLYTKA, "zla_plytka") for p in pl)
        znane[nazwa] = n
        kuwety.append(Kuweta(nazwa, prac, pl_n))

    for n, wpis in plytki.items():
        for i, g in enumerate(wpis.gniazda):
            if g.kuweta is not None and g.kuweta not in znane:
                _blad("nieznana_kuweta", f"plan.plytki.{n}.gniazda[{i}].kuweta: kuweta spoza listy kuwet")

    potwierdzone = []
    widziane = set()
    for i, para in enumerate(_lista(d.get("potwierdzone", []), "plan.potwierdzone", MAX_KUWET * MAX_PLYTKA)):
        sp = f"plan.potwierdzone[{i}]"
        if not isinstance(para, list) or len(para) != 2:
            _blad("zle_pole", f"{sp}: oczekiwano [plytka, kuweta]")
        p = _calkowita(para[0], sp + "[0]", 1, MAX_PLYTKA, "zla_plytka")
        k = _napis(para[1], sp + "[1]", WZOR_KUWETY, "zla_kuweta")
        if p not in plytki:
            _blad("zla_plytka", f"{sp}: plytka spoza planu")
        if k not in znane:
            _blad("nieznana_kuweta", f"{sp}: kuweta spoza listy kuwet")
        if (p, k) in widziane:
            _blad("zle_pole", f"{sp}: powtorzone potwierdzenie")
        widziane.add((p, k))
        potwierdzone.append((p, k))

    wybrane_d = d.get("wybrane", {})
    if not isinstance(wybrane_d, dict):
        _blad("zle_pole", "plan.wybrane: oczekiwano obiektu")
    wybrane = {}
    for klucz, k in wybrane_d.items():
        p = _numer_plytki(klucz, "plan.wybrane")
        if p not in plytki:
            _blad("zla_plytka", f"plan.wybrane.{p}: plytka spoza planu")
        k = _napis(k, f"plan.wybrane.{p}", WZOR_KUWETY, "zla_kuweta")
        if k not in znane:
            _blad("nieznana_kuweta", f"plan.wybrane.{p}: kuweta spoza listy kuwet")
        wybrane[p] = k

    braki = [_napis(b, f"plan.braki[{i}]", WZOR_KUWETY, "zla_kuweta")
             for i, b in enumerate(_lista(d.get("braki", []), "plan.braki", MAX_BRAKOW))]

    return Plan(plan_id=plan_id, wersja=wersja, start_id=start_id, zdarzenia_do=zdarzenia_do, wazny_s=wazny_s,
                tryb=tryb, kolejnosc=kolejnosc, plytki=plytki, kuwety=kuwety, potwierdzone=potwierdzone,
                wybrane=wybrane, braki=braki, odcisk=odcisk_planu(d), kolejnosc_kuwet=znane)


def sprawdz_tryb(d) -> str:
    """Tresc PUT /tryb: {"protokol": 1, "stan": "..."}; stan "wynik" nie istnieje w PUT /tryb (P2)."""
    if not isinstance(d, dict):
        _blad("zly_json", "tresc nie jest obiektem JSON")
    _obiekt(d, "tryb", ("protokol", "stan"))
    if d["protokol"] != PROTOKOL or isinstance(d["protokol"], bool):
        _blad("zly_protokol", f"tryb.protokol: obslugiwana wersja {PROTOKOL}")
    if not isinstance(d["stan"], str) or d["stan"] not in STANY_TRYBU:
        _blad("zly_stan", "tryb.stan: " + ", ".join(STANY_TRYBU) + " (stan wynik ustawia tylko przyjety plan)")
    return d["stan"]


def sprawdz_klucz(klucz) -> str:
    """Wspolny klucz z konfiguracji ramki (P6): pusty = bez klucza."""
    if not isinstance(klucz, str) or (klucz and not WZOR_KLUCZA.match(klucz)):
        raise ValueError("konfiguracja: klucz = 16-256 drukowalnych znakow ASCII bez odstepu")
    return klucz


def sprawdz_id_laptopa(wartosc) -> str:
    if not isinstance(wartosc, str) or not WZOR_ID.match(wartosc):
        _blad("zly_laptop", "naglowek X-Laptop-Id: 1-40 znakow [A-Za-z0-9._-]")
    return wartosc
