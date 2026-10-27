"""Uklad gniazd plytki: wczytanie pliku `uklad_gniazd_<typ>.json` ramki i walidacja (jak kontrola K-05).

Uklad plytki: srodek gornej powierzchni, X w prawo, Y do tylu (przod = -Y), Z w gore; wierzch Z = 0.
Format pliku jest formatem ramki (klucze angielskie); nieznane klucze sa ignorowane.
Kod numeru plytki: n = A + 2B + 4C (bit = magnes/dolek obecny); 0 = brak plytki, 7 = rezerwa.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

NUMERY = {"wieczorna": [1, 2, 3], "poranna": [4, 5, 6]}
BITY = {"A": 1, "B": 2, "C": 4}
WYMAGANE = ("plate", "size", "thickness", "markers", "notch", "code_dimples", "sockets")

# stale planu uzywane, gdy plik nie ma klucza
DOLEK_D, DOLEK_GLEBOKOSC = 2.0, 1.0
KIESZEN_D, KIESZEN_GLEBOKOSC = 5.2, 2.2
RELIEF_H = 0.6

# walidacja K-05
POLE_MAX = 45.0
NAROZNIK_OD = 35.0
MIN_ODSTEP = 3.0
TOL_SYMETRII = 0.01
TOL_D_DOL = 0.01
KAT_SCIANKI_DEG = 15.0


class BladUkladu(Exception):
    """Bledny plik ukladu gniazd (brak klucza albo niespelniony warunek K-05)."""


@dataclass
class Gniazdo:
    nr: int
    rodzaj: str  # "stozek" | "rynienka"
    xy: tuple[float, float]
    glebokosc: float
    otwor_d: float
    d_gora: float | None = None
    d_dol: float | None = None
    dlugosc: float | None = None
    szerokosc: float | None = None
    kat: float | None = None
    rozstaw_otworow: float | None = None
    liczba_otworow: int | None = None

    def os_rynienki(self) -> tuple[tuple[float, float], tuple[float, float], float]:
        """Os obrysu gornego: odcinek (p, q) i promien (kolo = odcinek zerowy)."""
        if self.rodzaj == "stozek":
            return self.xy, self.xy, self.d_gora / 2
        pol = (self.dlugosc - self.szerokosc) / 2
        a = math.radians(self.kat or 0.0)
        dx, dy = pol * math.cos(a), pol * math.sin(a)
        x, y = self.xy
        return (x - dx, y - dy), (x + dx, y + dy), self.szerokosc / 2

    def srodki_otworow(self) -> list[tuple[float, float]]:
        if self.rodzaj == "stozek":
            return [self.xy]
        a = math.radians(self.kat or 0.0)
        n = int(self.liczba_otworow or 0)
        x, y = self.xy
        wynik = []
        for i in range(n):
            s = (i - (n - 1) / 2) * float(self.rozstaw_otworow or 0.0)
            wynik.append((x + s * math.cos(a), y + s * math.sin(a)))
        return wynik


@dataclass
class Uklad:
    nazwa: str
    numery: list[int]
    rozmiar: float
    grubosc: float
    gniazda: list[Gniazdo]
    znaczniki: dict[str, tuple[float, float, float, float]]  # naroznik -> (x, y, d, glebokosc)
    wyciecie: tuple[float, float, float, float]  # (x_min, x_max, y_min, y_max)
    dolki_kodu: dict[str, tuple[float, float]]  # bit -> (x, y)
    kieszenie_magnesow: dict[str, tuple[float, float, float, float]]  # naroznik -> (x, y, d, glebokosc)
    relief_numeru: tuple[float, float, float, float] | None  # (x, y, wysokosc_tekstu, wysokosc_reliefu)
    leds: dict = field(default_factory=dict)
    wymiary_dolkow: dict[str, tuple[float, float]] = field(default_factory=dict)  # bit -> (d, glebokosc)
    plik: Path | None = None

    def gniazdo(self, nr: int) -> Gniazdo:
        for g in self.gniazda:
            if g.nr == nr:
                return g
        raise KeyError(f"uklad {self.nazwa} nie ma gniazda {nr}")

    def gniazdo_dla_xy(self, x: float, y: float, margines: float = 0.0) -> int | None:
        """Numer gniazda, w ktorego obrysie gornym (+ margines) lezy punkt; None = poza gniazdami."""
        for g in self.gniazda:
            p, q, r = g.os_rynienki()
            if _punkt_odcinek((x, y), p, q) <= r + margines:
                return g.nr
        return None


# --- kod numeru ---------------------------------------------------------------


def kod_numeru(n: int) -> set[str]:
    """Bity (dolki/magnesy) plytki o numerze n: n = A + 2B + 4C."""
    if not 1 <= int(n) <= 6:
        raise ValueError(f"numer plytki poza zakresem 1-6: {n}")
    return {b for b, w in BITY.items() if int(n) & w}


def numer_z_kodu(bity) -> int | None:
    """Numer plytki z zestawu bitow; 0 (brak plytki) i 7 (rezerwa) -> None."""
    n = sum(BITY[b] for b in set(bity))
    return n if 1 <= n <= 6 else None


# --- geometria ------------------------------------------------------------------


def _punkt_odcinek(pt, p, q) -> float:
    vx, vy = q[0] - p[0], q[1] - p[1]
    dl2 = vx * vx + vy * vy
    t = 0.0 if dl2 == 0 else max(0.0, min(1.0, ((pt[0] - p[0]) * vx + (pt[1] - p[1]) * vy) / dl2))
    return math.hypot(pt[0] - p[0] - t * vx, pt[1] - p[1] - t * vy)


def _odstep(a: Gniazdo, b: Gniazdo) -> float:
    """Najmniejsza odleglosc obrysow gornych (kolo/stadion); odcinki osi sie nie przecinaja."""
    p1, q1, r1 = a.os_rynienki()
    p2, q2, r2 = b.os_rynienki()
    d = min(_punkt_odcinek(p1, p2, q2), _punkt_odcinek(q1, p2, q2),
            _punkt_odcinek(p2, p1, q1), _punkt_odcinek(q2, p1, q1))
    return d - r1 - r2


def _w_narozniku(g: Gniazdo) -> bool:
    """Czy obrys gorny wchodzi w kwadrat narozny (|x| > 35 i |y| > 35)."""
    p, q, r = g.os_rynienki()
    for x, y in (p, q):
        dx = max(0.0, NAROZNIK_OD - abs(x))
        dy = max(0.0, NAROZNIK_OD - abs(y))
        if math.hypot(dx, dy) < r - 1e-9:
            return True
    return False


# --- wczytanie ------------------------------------------------------------------


def _klucz(d: dict, klucz: str, gdzie: str):
    if klucz not in d:
        raise BladUkladu(f"{gdzie}: brak klucza '{klucz}'")
    return d[klucz]


def _gniazdo(s: dict) -> Gniazdo:
    gdzie = f"sockets id={s.get('id')}"
    nr = int(_klucz(s, "id", "sockets"))
    typ = _klucz(s, "type", gdzie)
    xy = (float(_klucz(s, "x", gdzie)), float(_klucz(s, "y", gdzie)))
    glebokosc = float(_klucz(s, "depth", gdzie))
    otwor = float(_klucz(s, "hole_d", gdzie))
    if typ == "round":
        return Gniazdo(nr, "stozek", xy, glebokosc, otwor, d_gora=float(_klucz(s, "d_top", gdzie)),
                       d_dol=float(_klucz(s, "d_bottom", gdzie)))
    if typ == "trough":
        return Gniazdo(nr, "rynienka", xy, glebokosc, otwor, dlugosc=float(_klucz(s, "l", gdzie)),
                       szerokosc=float(_klucz(s, "w", gdzie)), kat=float(s.get("angle", 0.0)),
                       rozstaw_otworow=float(_klucz(s, "hole_pitch", gdzie)),
                       liczba_otworow=int(_klucz(s, "hole_count", gdzie)))
    raise BladUkladu(f"{gdzie}: nieznany type '{typ}'")


def _waliduj(gniazda: list[Gniazdo]) -> None:
    if [g.nr for g in gniazda] != list(range(1, len(gniazda) + 1)):
        raise BladUkladu("id gniazd nie sa ciagle 1..N w kolejnosci pliku")
    rzedy: dict[float, list[Gniazdo]] = {}
    for g in gniazda:
        rzedy.setdefault(round(g.xy[1], 2), []).append(g)
    kolejnosc = [g.nr for y in sorted(rzedy) for g in sorted(rzedy[y], key=lambda g: -g.xy[0])]
    if kolejnosc != list(range(1, len(gniazda) + 1)):
        raise BladUkladu("id gniazd nie ida rzedami od przodu (rosnace y), w rzedzie malejace x")
    tan15 = math.tan(math.radians(KAT_SCIANKI_DEG))
    for g in gniazda:
        if g.rodzaj == "stozek":
            oczekiwane = g.d_gora - 2 * g.glebokosc * tan15
            if abs(g.d_dol - oczekiwane) > TOL_D_DOL:
                raise BladUkladu(f"gniazdo {g.nr}: d_bottom {g.d_dol} zamiast {oczekiwane:.2f} (scianki 15 st.)")
        p, q, r = g.os_rynienki()
        for x, y in (p, q):
            if abs(x) + r > POLE_MAX + 1e-9 or abs(y) + r > POLE_MAX + 1e-9:
                raise BladUkladu(f"gniazdo {g.nr}: obrys poza polem [-{POLE_MAX:g}, {POLE_MAX:g}]^2")
        if _w_narozniku(g):
            raise BladUkladu(f"gniazdo {g.nr}: obrys w kwadracie naroznym (|x| > 35 i |y| > 35)")
    for y, rzad in rzedy.items():
        xs = sorted(g.xy[0] for g in rzad)
        if any(abs(a + b) > TOL_SYMETRII for a, b in zip(xs, reversed(xs))):
            raise BladUkladu(f"rzad gniazd y={y}: brak symetrii wzgledem x = 0")
    for i, a in enumerate(gniazda):
        for b in gniazda[i + 1:]:
            d = _odstep(a, b)
            if d < MIN_ODSTEP - 1e-6:
                raise BladUkladu(f"gniazda {a.nr} i {b.nr}: odstep obrysow {d:.2f} < {MIN_ODSTEP:g} mm")


def z_dict(d: dict, plik: Path | None = None) -> Uklad:
    """Uklad ze slownika w formacie ramki (walidacja K-05)."""
    for klucz in WYMAGANE:
        _klucz(d, klucz, "uklad")
    nazwa = str(d["plate"])
    if nazwa not in NUMERY:
        raise BladUkladu(f"nieznana plate '{nazwa}' (oczekiwano {', '.join(NUMERY)})")
    znaczniki = {}
    for m in d["markers"]:
        znaczniki[str(_klucz(m, "corner", "markers"))] = (
            float(_klucz(m, "x", "markers")), float(_klucz(m, "y", "markers")),
            float(_klucz(m, "d", "markers")), float(_klucz(m, "depth", "markers")))
    if set(znaczniki) != {"A", "B", "C"}:
        raise BladUkladu(f"markers: oczekiwano naroznikow A, B, C, jest {sorted(znaczniki)}")
    n = d["notch"]
    wyciecie = tuple(float(_klucz(n, k, "notch")) for k in ("x_min", "x_max", "y_min", "y_max"))
    dolki, wymiary = {}, {}
    for c in d["code_dimples"]:
        bit = str(_klucz(c, "bit", "code_dimples"))
        dolki[bit] = (float(_klucz(c, "x", "code_dimples")), float(_klucz(c, "y", "code_dimples")))
        wymiary[bit] = (float(c.get("d", DOLEK_D)), float(c.get("depth", DOLEK_GLEBOKOSC)))
    if set(dolki) != set(BITY):
        raise BladUkladu(f"code_dimples: oczekiwano bitow A, B, C, jest {sorted(dolki)}")
    kieszenie = {}
    for k in d.get("magnet_pockets", []):
        kieszenie[str(_klucz(k, "corner", "magnet_pockets"))] = (
            float(_klucz(k, "x", "magnet_pockets")), float(_klucz(k, "y", "magnet_pockets")),
            float(k.get("d", KIESZEN_D)), float(k.get("depth", KIESZEN_GLEBOKOSC)))
    relief = None
    if "number_relief" in d:
        r = d["number_relief"]
        relief = (float(_klucz(r, "x", "number_relief")), float(_klucz(r, "y", "number_relief")),
                  float(r.get("text_h", 5.0)), float(r.get("relief_h", RELIEF_H)))
    if not isinstance(d["sockets"], list) or not d["sockets"]:
        raise BladUkladu("sockets: pusta lista gniazd")
    gniazda = [_gniazdo(s) for s in d["sockets"]]
    _waliduj(gniazda)
    return Uklad(nazwa=nazwa, numery=list(NUMERY[nazwa]), rozmiar=float(d["size"]),
                 grubosc=float(d["thickness"]), gniazda=gniazda, znaczniki=znaczniki, wyciecie=wyciecie,
                 dolki_kodu=dolki, kieszenie_magnesow=kieszenie, relief_numeru=relief,
                 leds=d.get("leds") or {}, wymiary_dolkow=wymiary, plik=plik)


def wczytaj(sciezka) -> Uklad:
    """Wczytuje i waliduje plik ukladu gniazd ramki (UTF-8)."""
    plik = Path(sciezka)
    try:
        dane = json.loads(plik.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise BladUkladu(f"nie mozna wczytac ukladu {plik}: {e}") from e
    if not isinstance(dane, dict):
        raise BladUkladu(f"{plik}: oczekiwano obiektu JSON")
    return z_dict(dane, plik)
