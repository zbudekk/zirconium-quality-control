"""Układ płytki z gniazdami: wczytanie pliku ``modele_plytek/<nazwa>/uklad.json``.

Jeden wspólny opis płytki dla modułów plate, synth, indicate i ui.
Współrzędne w pliku układu: początek w środku GÓRNEJ powierzchni płytki,
x w prawo, y do tyłu (od użytkownika). W STL płytki ta sama płaszczyzna
leży na z = ``Z_TOP`` (grubość płytki), spód na z = 0.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

KATALOG_MODELI = Path(__file__).resolve().parent.parent / "modele_plytek"
Z_TOP = 8.0  # z górnej powierzchni płytki w STL (= grubość płytki)
KAT_SCIANKI_DEG = 15.0  # kąt ścianki stożka gniazda od pionu


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

    @property
    def okragle(self) -> bool:
        return self.typ == "round"

    @property
    def z_dno(self) -> float:
        """z dna gniazda w układzie STL."""
        return Z_TOP - self.depth

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

    def zawiera(self, x: float, y: float, margines: float = 0.0) -> bool:
        """Czy punkt (x, y) leży nad otworem gniazda (plus margines)."""
        dx, dy = x - self.x, y - self.y
        if self.okragle:
            return math.hypot(dx, dy) <= self.d_top / 2 + margines
        a = math.radians(self.angle)
        u = dx * math.cos(a) + dy * math.sin(a)
        v = -dx * math.sin(a) + dy * math.cos(a)
        return abs(u) <= self.l / 2 + margines and abs(v) <= self.w / 2 + margines


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

    def gniazdo(self, id_: int) -> Gniazdo:
        for g in self.sockets:
            if g.id == id_:
                return g
        raise KeyError(f"brak gniazda {id_} w układzie {self.nazwa}")

    def gniazda_okragle(self) -> list[Gniazdo]:
        return [g for g in self.sockets if g.okragle]

    def rynienki(self) -> list[Gniazdo]:
        return [g for g in self.sockets if not g.okragle]

    def najblizsze_gniazdo(self, x: float, y: float) -> Gniazdo:
        return min(self.sockets, key=lambda g: math.hypot(g.x - x, g.y - y))

    def plik_stl(self, numer: int) -> Path:
        p = self.katalog / f"plytka_n{numer}.stl"
        if not p.exists():
            raise FileNotFoundError(f"brak modelu płytki nr {numer}: {p}")
        return p

    @staticmethod
    def numer_z_bitow(a: bool, b: bool, c: bool) -> int:
        """Kod płytki: n = A + 2·B + 4·C (kody_plytek.md)."""
        return int(a) + 2 * int(b) + 4 * int(c)

    @staticmethod
    def bity_z_numeru(n: int) -> tuple[bool, bool, bool]:
        return bool(n & 1), bool(n & 2), bool(n & 4)


def wczytaj(nazwa: str) -> UkladPlytki:
    """Wczytuje układ ``wieczorna`` lub ``poranna`` z katalogu modeli."""
    katalog = KATALOG_MODELI / nazwa
    plik = katalog / "uklad.json"
    if not plik.exists():
        raise FileNotFoundError(f"brak pliku układu: {plik}")
    d = json.loads(plik.read_text(encoding="utf-8"))
    sockets = []
    for s in d["sockets"]:
        sockets.append(
            Gniazdo(
                id=int(s["id"]),
                typ=s["type"],
                x=float(s["x"]),
                y=float(s["y"]),
                depth=float(s["depth"]),
                d_top=s.get("d_top"),
                d_bottom=s.get("d_bottom"),
                l=s.get("l"),
                w=s.get("w"),
                angle=float(s.get("angle", 0.0)),
            )
        )
    numery = sorted(
        int(p.stem.split("_n")[1]) for p in katalog.glob("plytka_n*.stl")
    )
    return UkladPlytki(
        nazwa=d["plate"],
        size=float(d["size"]),
        thickness=float(d["thickness"]),
        markers=[Znacznik(**m) for m in d["markers"]],
        notch=d["notch"],
        code_dimples=[Dolek(**c) for c in d["code_dimples"]],
        sockets=sockets,
        katalog=katalog,
        numery=numery,
    )
