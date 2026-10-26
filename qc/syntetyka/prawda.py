"""Prawda o syntetycznych skanach: co i gdzie zostalo wprowadzone (JSON, wersja 1)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

WERSJA = 1


@dataclass
class UbytekPrawda:
    """Ubytek wprowadzony do skanu; srodek w ukladzie projektu (bez skali)."""

    srodek: list[float]
    srednica_mm: float
    glebokosc_mm: float
    rodzaj: str = "ukruszenie"  # "ukruszenie" | "poprawka"
    przy_brzegu: bool = True

    def do_dict(self) -> dict:
        return {
            "srodek": [float(x) for x in self.srodek],
            "srednica_mm": float(self.srednica_mm),
            "glebokosc_mm": float(self.glebokosc_mm),
            "rodzaj": self.rodzaj,
            "przy_brzegu": bool(self.przy_brzegu),
        }

    @classmethod
    def z_dict(cls, d: dict) -> "UbytekPrawda":
        return cls(
            srodek=[float(x) for x in d["srodek"]],
            srednica_mm=float(d["srednica_mm"]),
            glebokosc_mm=float(d["glebokosc_mm"]),
            rodzaj=d.get("rodzaj", "ukruszenie"),
            przy_brzegu=bool(d.get("przy_brzegu", True)),
        )


@dataclass
class PrawdaPracy:
    """Prawda o jednej pracy w skanie."""

    id: str
    wspolczynnik: float
    T_projekt_do_skanu: np.ndarray
    zakres_scian: list[int]
    gniazdo: int | None = None
    stan: str = "praca"
    drgniecie: bool = False
    pokrycie: float = 1.0
    ubytki: list[UbytekPrawda] = field(default_factory=list)

    def __post_init__(self):
        self.T_projekt_do_skanu = np.asarray(self.T_projekt_do_skanu, dtype=np.float64).reshape(4, 4)

    def do_dict(self) -> dict:
        return {
            "id": self.id,
            "gniazdo": self.gniazdo,
            "wspolczynnik": float(self.wspolczynnik),
            "T_projekt_do_skanu": self.T_projekt_do_skanu.tolist(),
            "zakres_scian": [int(x) for x in self.zakres_scian],
            "stan": self.stan,
            "drgniecie": bool(self.drgniecie),
            "pokrycie": float(self.pokrycie),
            "ubytki": [u.do_dict() for u in self.ubytki],
        }

    @classmethod
    def z_dict(cls, d: dict) -> "PrawdaPracy":
        return cls(
            id=d["id"],
            gniazdo=d.get("gniazdo"),
            wspolczynnik=float(d["wspolczynnik"]),
            T_projekt_do_skanu=np.asarray(d["T_projekt_do_skanu"], dtype=np.float64),
            zakres_scian=[int(x) for x in d["zakres_scian"]],
            stan=d.get("stan", "praca"),
            drgniecie=bool(d.get("drgniecie", False)),
            pokrycie=float(d.get("pokrycie", 1.0)),
            ubytki=[UbytekPrawda.z_dict(u) for u in d.get("ubytki", [])],
        )


@dataclass
class Prawda:
    """Prawda o calym skanie (plytka albo pojedyncze prace)."""

    ziarno: int
    szum_mm: float
    gestosc_mm: float
    plytka: dict | None = None
    prace: list[PrawdaPracy] = field(default_factory=list)
    wersja: int = WERSJA

    def do_dict(self) -> dict:
        return {
            "wersja": int(self.wersja),
            "ziarno": int(self.ziarno),
            "szum_mm": float(self.szum_mm),
            "gestosc_mm": float(self.gestosc_mm),
            "plytka": self.plytka,
            "prace": [p.do_dict() for p in self.prace],
        }

    @classmethod
    def z_dict(cls, d: dict) -> "Prawda":
        if int(d.get("wersja", 0)) != WERSJA:
            raise ValueError(f"nieobslugiwana wersja prawdy: {d.get('wersja')}")
        return cls(
            wersja=int(d["wersja"]),
            ziarno=int(d["ziarno"]),
            szum_mm=float(d["szum_mm"]),
            gestosc_mm=float(d["gestosc_mm"]),
            plytka=d.get("plytka"),
            prace=[PrawdaPracy.z_dict(p) for p in d.get("prace", [])],
        )

    def do_json(self, sciezka) -> None:
        Path(sciezka).write_text(json.dumps(self.do_dict(), indent=1), encoding="utf-8")

    @classmethod
    def z_json(cls, sciezka) -> "Prawda":
        return cls.z_dict(json.loads(Path(sciezka).read_text(encoding="utf-8")))
