"""Układ płytki z gniazdami: wczytanie pliku ``modele_plytek/<nazwa>/uklad.json``.

Jeden wspólny opis płytki dla modułów plate, synth, indicate i ui.
Współrzędne w pliku układu: początek w środku GÓRNEJ powierzchni płytki,
x w prawo, y do tyłu (od użytkownika). W STL płytki ta sama płaszczyzna
leży na z = ``thickness`` (grubość płytki z ``uklad.json``), spód na z = 0.

Plik jest sprawdzany przy wczytaniu (wymagane klucze, typy gniazd, gniazda
w obrysie płytki); błąd mówi, który plik i które gniazdo jest złe.
"""
from __future__ import annotations

import json
import math
import re
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

KATALOG_MODELI = Path(__file__).resolve().parent.parent / "modele_plytek"  # = [plytki] w ustawienia.toml (test_ustawienia)
Z_TOP = 8.0  # domyślne z górnej powierzchni płytki w STL; w układzie z pliku obowiązuje ``thickness``
KAT_SCIANKI_DEG = 15.0  # kąt ścianki stożka gniazda od pionu
TYPY_GNIAZD = ("round", "trough")
BITY_KODU = ("A", "B", "C", "D")  # n = A + 2·B + 4·C + 8·D; D opcjonalny (płytki n8, n9…)
WZOR_PLIKU_PLYTKI = re.compile(r"plytka_n(\d+)\.stl")
PLIK_PLYTKI_BAZOWEJ = "plytka_bazowa.stl"  # model bez numeru (wzorzec z dołkami wszystkich bitów), nie jest płytką do skanu


class BladUkladu(ValueError):
    """Zły plik ``uklad.json``; komunikat zaczyna się od ścieżki pliku."""


@dataclass(frozen=True)
class Gniazdo:
    id: int
    typ: str  # "round" | "trough"
    x: float
    y: float
    depth: float
    d_top: float | None = None
    d_bottom: float | None = None
    l: float | None = None
    w: float | None = None
    angle: float = 0.0
    z_top: float = Z_TOP  # z wierzchu płytki (thickness z uklad.json)

    @property
    def okragle(self) -> bool:
        return self.typ == "round"

    @property
    def z_dno(self) -> float:
        """z dna gniazda w układzie STL."""
        return self.z_top - self.depth

    @property
    def promien_gorny(self) -> float:
        """Promień koła wpisanego w otwór gniazda na wierzchu płytki."""
        if self.okragle:
            return self.d_top / 2
        return min(self.l, self.w) / 2

    def promien_dolny(self) -> float:
        if self.okragle:
            return self.d_bottom / 2
        return min(self.l, self.w) / 2 - self.depth * math.tan(math.radians(KAT_SCIANKI_DEG))

    def _uv(self, x: float, y: float) -> tuple[float, float]:
        """Współrzędne punktu w układzie rynienki (u wzdłuż, v w poprzek)."""
        dx, dy = x - self.x, y - self.y
        a = math.radians(self.angle)
        return dx * math.cos(a) + dy * math.sin(a), -dx * math.sin(a) + dy * math.cos(a)

    def _odleglosc_stadion(self, u: float, v: float) -> float:
        """Odległość od obrysu rynienki (stadion: odcinek l − w wzdłuż u, promień w/2); ujemna = wewnątrz."""
        return math.hypot(max(abs(u) - (self.l - self.w) / 2, 0.0), v) - self.w / 2

    def zawiera(self, x: float, y: float, margines: float = 0.0) -> bool:
        """Czy punkt (x, y) leży nad otworem gniazda (plus margines)."""
        return self.odleglosc_do_obrysu(x, y) <= margines

    def odleglosc_do_obrysu(self, x: float, y: float) -> float:
        """Odległość punktu od obrysu otworu na wierzchu płytki; ujemna = wewnątrz.

        Gniazdo okrągłe: ``hypot − r``. Rynienka: obrys to stadion — prostokąt (l − w) × w
        z półokręgami o promieniu w/2 na końcach (tak jest w STL płytki; D4 z recenzji R57).
        """
        if self.okragle:
            return math.hypot(x - self.x, y - self.y) - self.d_top / 2
        return self._odleglosc_stadion(*self._uv(x, y))

    def obrys(self, n: int = 72) -> list[tuple[float, float]]:
        """Punkty obrysu otworu na wierzchu płytki (do rysowania i sprawdzania „w obrysie płytki”)."""
        if self.okragle:
            r = self.d_top / 2
            return [(self.x + r * math.cos(t), self.y + r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, n, endpoint=False)]
        a = math.radians(self.angle)
        h, r = (self.l - self.w) / 2, self.w / 2
        pts = []
        for k in range(n):
            t = 2 * math.pi * k / n
            u = (h if math.cos(t) >= 0 else -h) + r * math.cos(t)
            v = r * math.sin(t)
            pts.append((self.x + u * math.cos(a) - v * math.sin(a), self.y + u * math.sin(a) + v * math.cos(a)))
        return pts


@dataclass(frozen=True)
class Znacznik:
    corner: str
    x: float
    y: float
    d: float
    depth: float


@dataclass(frozen=True)
class Dolek:
    bit: str
    x: float
    y: float
    d: float
    depth: float


@dataclass
class UkladPlytki:
    nazwa: str
    size: float
    thickness: float
    markers: list[Znacznik]
    notch: dict
    code_dimples: list[Dolek]
    sockets: list[Gniazdo]
    katalog: Path
    numery: list[int] = field(default_factory=list)
    shape: str = "square"  # "square" (size × size) | "round" (średnica d)
    d: float | None = None
    flat: dict = field(default_factory=dict)  # ścięcie orientacyjne płytki okrągłej (corner, angle_deg, chord_w, dist)

    def gniazdo(self, id_: int) -> Gniazdo:
        for g in self.sockets:
            if g.id == id_:
                return g
        raise KeyError(f"brak gniazda {id_} w układzie {self.nazwa}")

    def gniazda_okragle(self) -> list[Gniazdo]:
        return [g for g in self.sockets if g.okragle]

    def rynienki(self) -> list[Gniazdo]:
        return [g for g in self.sockets if not g.okragle]

    def najblizsze_gniazdo(self, x: float, y: float, margines: float = 0.0) -> Gniazdo | None:
        """Gniazdo, nad którym leży punkt (z marginesem), albo None poza wszystkimi.

        Gdy punkt leży nad kilkoma gniazdami (duży margines), wygrywa to, którego
        obrys jest najdalej od punktu do wewnątrz (najmniejsza odległość do obrysu).
        """
        zaw = [g for g in self.sockets if g.zawiera(x, y, margines)]
        if not zaw:
            return None
        return min(zaw, key=lambda g: g.odleglosc_do_obrysu(x, y))

    def plik_stl(self, numer: int) -> Path:
        p = self.katalog / f"plytka_n{numer}.stl"
        if not p.exists():
            raise FileNotFoundError(f"brak modelu płytki nr {numer}: {p}")
        return p

    @property
    def liczba_bitow(self) -> int:
        return len(self.code_dimples)

    @staticmethod
    def numer_z_bitow(a: bool, b: bool, c: bool, d: bool = False) -> int:
        """Kod płytki: n = A + 2·B + 4·C + 8·D (kody_plytek.md; D opcjonalny)."""
        for nazwa, bit in zip(BITY_KODU, (a, b, c, d)):
            if bit not in (0, 1):  # True/False i 0/1; 2 albo "1" to błąd wywołującego
                raise ValueError(f"bit {nazwa} musi być bool/0/1, jest {bit!r}")
        return int(a) + 2 * int(b) + 4 * int(c) + 8 * int(d)

    @staticmethod
    def bity_z_numeru(n: int, liczba_bitow: int = 3) -> tuple[bool, ...]:
        """Bity (A, B, C[, D]) numeru płytki; ``liczba_bitow`` = liczba dołków kodu (3 lub 4)."""
        if liczba_bitow not in (3, 4):
            raise ValueError(f"liczba bitów kodu 3 albo 4, jest {liczba_bitow}")
        if isinstance(n, bool) or not isinstance(n, int) or not 0 <= n < 2**liczba_bitow:
            raise ValueError(f"numer płytki {n!r} poza zakresem 0…{2**liczba_bitow - 1} ({liczba_bitow} bity)")
        return tuple(bool(n & (1 << k)) for k in range(liczba_bitow))


# ----------------------------------------------------------------------------
# wczytanie i walidacja
# ----------------------------------------------------------------------------
def _liczba(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _waliduj(d, plik: Path) -> None:
    def blad(co: str) -> BladUkladu:
        return BladUkladu(f"plik {plik}: {co}")

    if not isinstance(d, dict):
        raise blad("oczekiwano obiektu JSON")
    for k in ("plate", "thickness", "markers", "code_dimples", "sockets"):  # notch opcjonalny (płytka okrągła)
        if k not in d:
            raise blad(f"brak klucza {k!r}")
    shape = d.get("shape", "square")
    if shape not in ("square", "round"):
        raise blad(f"shape {shape!r} — dopuszczalne 'square' albo 'round'")
    wym = "size" if shape == "square" else "d"
    if not _liczba(d.get(wym)) or d[wym] <= 0:
        raise blad(f"płytka {shape}: brak albo zły {wym!r}")
    if not _liczba(d["thickness"]) or d["thickness"] <= 0:
        raise blad("thickness musi być liczbą > 0")
    pol = d[wym] / 2
    flat = d.get("flat")
    if flat is not None:
        if shape != "round":
            raise blad("flat (ścięcie orientacyjne) tylko dla shape 'round'")
        for k in ("angle_deg", "chord_w", "dist"):
            if not _liczba(flat.get(k)):
                raise blad(f"flat: brak albo zły {k!r}")
        if not 0 < flat["dist"] < pol or flat["chord_w"] <= 0:
            raise blad(f"flat: dist {flat['dist']} musi być w (0, {pol}), chord_w > 0")

    def w_obrysie(x: float, y: float) -> bool:
        if shape == "square":
            return abs(x) <= pol + 1e-9 and abs(y) <= pol + 1e-9
        return math.hypot(x, y) <= pol + 1e-9

    for lista, wymagane in (("markers", ("corner", "x", "y", "d", "depth")), ("code_dimples", ("bit", "x", "y", "d", "depth"))):
        if not isinstance(d[lista], list):
            raise blad(f"{lista} musi być listą")
        for i, e in enumerate(d[lista], 1):
            for k in wymagane:
                if k not in e:
                    raise blad(f"{lista}[{i}]: brak {k}")
                if k not in ("corner", "bit") and not _liczba(e[k]):
                    raise blad(f"{lista}[{i}]: {k} musi być liczbą, jest {e[k]!r}")
    bity = [e["bit"] for e in d["code_dimples"]]
    if bity not in (list(BITY_KODU[:3]), list(BITY_KODU)):
        raise blad(f"code_dimples: bity {bity} — oczekiwano A, B, C (opcjonalnie D) w tej kolejności")

    if not isinstance(d["sockets"], list) or not d["sockets"]:
        raise blad("sockets: co najmniej jedno gniazdo")
    tan = math.tan(math.radians(KAT_SCIANKI_DEG))
    ids = set()
    for s in d["sockets"]:
        nr = s.get("id", "?")
        for k in ("id", "type", "x", "y", "depth"):
            if k not in s:
                raise blad(f"gniazdo {nr}: brak {k}")
        if s["type"] not in TYPY_GNIAZD:
            raise blad(f"gniazdo {nr}: type {s['type']!r} — dopuszczalne {', '.join(TYPY_GNIAZD)}")
        pola = ("x", "y", "depth") + (("d_top", "d_bottom") if s["type"] == "round" else ("l", "w"))
        for k in pola:
            if k not in s:
                raise blad(f"gniazdo {nr}: brak {k}")
            if not _liczba(s[k]):
                raise blad(f"gniazdo {nr}: {k} musi być liczbą, jest {s[k]!r}")
        if not isinstance(s["id"], int) or isinstance(s["id"], bool) or s["id"] in ids:
            raise blad(f"gniazdo {nr}: id musi być unikalną liczbą całkowitą")
        ids.add(s["id"])
        if not 0 < s["depth"] <= d["thickness"]:
            raise blad(f"gniazdo {nr}: depth {s['depth']} poza (0, thickness={d['thickness']}]")
        x, y = s["x"], s["y"]
        if s["type"] == "round":
            r = s["d_top"] / 2
            if not 0 < s["d_bottom"] <= s["d_top"]:
                raise blad(f"gniazdo {nr}: d_bottom {s['d_bottom']} poza (0, d_top={s['d_top']}]")
            if abs(s["d_bottom"] - (s["d_top"] - 2 * s["depth"] * tan)) > 0.01:
                raise blad(f"gniazdo {nr}: d_bottom {s['d_bottom']} niezgodne z kątem ścianki {KAT_SCIANKI_DEG}°")
            punkty = [(x + r * math.cos(t), y + r * math.sin(t)) for t in [k * math.pi / 18 for k in range(36)]]
        else:
            if s["l"] <= 0 or s["w"] <= 0 or min(s["l"], s["w"]) / 2 <= s["depth"] * tan:
                raise blad(f"gniazdo {nr}: l/w za małe na ściankę {KAT_SCIANKI_DEG}° przy depth {s['depth']}")
            punkty = Gniazdo(nr, "trough", x, y, s["depth"], l=s["l"], w=s["w"], angle=float(s.get("angle", 0.0))).obrys(72)
        if not all(w_obrysie(px, py) for px, py in punkty):
            raise blad(f"gniazdo {nr}: wychodzi poza obrys płytki ({shape} {wym}={d[wym]})")


def _numery_plytek(katalog: Path, liczba_bitow: int, plik: Path) -> list[int]:
    numery = []
    for p in katalog.iterdir():
        dop = WZOR_PLIKU_PLYTKI.fullmatch(p.name)
        if dop is None:
            if p.name == PLIK_PLYTKI_BAZOWEJ:
                continue
            if p.suffix.lower() == ".stl":
                warnings.warn(f"{katalog}: pomijam plik {p.name} (nazwa inna niż plytka_n<numer>.stl)", stacklevel=3)
            continue
        n = int(dop.group(1))
        if not 1 <= n < 2**liczba_bitow:
            raise BladUkladu(f"plik {plik}: płytka {p.name} — numer {n} poza 1…{2**liczba_bitow - 1} ({liczba_bitow} dołki kodu)")
        numery.append(n)
    return sorted(numery)


def wczytaj(nazwa: str, katalog: Path | None = None) -> UkladPlytki:
    """Wczytuje układ ``nazwa`` (np. ``wieczorna``) z ``katalog`` (domyślnie ``KATALOG_MODELI/nazwa``)."""
    katalog = Path(katalog) if katalog is not None else KATALOG_MODELI / nazwa
    plik = katalog / "uklad.json"
    if not plik.exists():
        raise FileNotFoundError(f"brak pliku układu: {plik}")
    try:
        d = json.loads(plik.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise BladUkladu(f"plik {plik}: błąd składni JSON: {e}") from e
    _waliduj(d, plik)
    shape = d.get("shape", "square")
    size = float(d["size"]) if "size" in d else float(d["d"])
    thickness = float(d["thickness"])
    sockets = [
        Gniazdo(
            id=s["id"],
            typ=s["type"],
            x=float(s["x"]),
            y=float(s["y"]),
            depth=float(s["depth"]),
            d_top=s.get("d_top"),
            d_bottom=s.get("d_bottom"),
            l=s.get("l"),
            w=s.get("w"),
            angle=float(s.get("angle", 0.0)),
            z_top=thickness,
        )
        for s in d["sockets"]
    ]
    dolki = [Dolek(c["bit"], c["x"], c["y"], c["d"], c["depth"]) for c in d["code_dimples"]]
    return UkladPlytki(
        nazwa=d["plate"],
        size=size,
        thickness=thickness,
        markers=[Znacznik(m["corner"], m["x"], m["y"], m["d"], m["depth"]) for m in d["markers"]],
        notch=d.get("notch", {}),
        code_dimples=dolki,
        sockets=sockets,
        katalog=katalog,
        numery=_numery_plytek(katalog, len(dolki), plik),
        shape=shape,
        d=float(d["d"]) if shape == "round" else None,
        flat=dict(d.get("flat", {})),
    )
