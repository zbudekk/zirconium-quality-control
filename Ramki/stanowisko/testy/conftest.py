"""Wspólne fixture'y testów (część przeniesiona z sesje_2026-10-31/kod_a_stanowisko/testy_edge/conftest.py).

Testy nie piszą nic do ``dane/`` ani do plików projektu — tylko do tmp_path.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest
import trimesh

STANOWISKO = Path(__file__).resolve().parent.parent
RAMKI = STANOWISKO.parent
for p in (STANOWISKO, STANOWISKO / "narzedzia"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import atrapy_koron  # noqa: E402
from stanowisko import uklad as U  # noqa: E402


@pytest.fixture(scope="session")
def korony(tmp_path_factory) -> list[Path]:
    """Trzy małe atrapy (siekacz, przedtrzonowy, trzonowy)."""
    d = tmp_path_factory.mktemp("stl")
    rng = np.random.default_rng(3)
    pliki = []
    for i, t in enumerate(["siekacz", "przedtrzonowy", "trzonowy"]):
        W, L, H, g, amp = atrapy_koron.TYPY[t]
        m = atrapy_koron.korona(W, L, H, g, amp, n_theta=96, n_u=120, rng=rng)
        p = d / f"a{i}_{t}.stl"
        m.export(p)
        pliki.append(p)
    return pliki


@pytest.fixture
def korona_siekacz() -> trimesh.Trimesh:
    W, L, H, g, amp = atrapy_koron.TYPY["siekacz"]
    return atrapy_koron.korona(W, L, H, g, amp, n_theta=96, n_u=120, rng=np.random.default_rng(7))


@pytest.fixture
def uklad_tmp(tmp_path, monkeypatch):
    """Kopia katalogu modeli w tmp (uklad.json + puste pliki STL o nazwach plytka_n*.stl).

    Zwraca funkcję ``zrob(nazwa, zmien=None, pliki=("plytka_n1.stl",))``: ``zmien(dict)``
    zwraca nowy słownik JSON (albo None, gdy zmienia w miejscu); ``U.KATALOG_MODELI`` wskazuje na tmp.
    """
    root = tmp_path / "modele_plytek"
    monkeypatch.setattr(U, "KATALOG_MODELI", root)

    def zrob(nazwa="wieczorna", zmien=None, pliki=("plytka_n1.stl",), zrodlo="wieczorna"):
        kat = root / nazwa
        kat.mkdir(parents=True, exist_ok=True)
        d = json.loads((STANOWISKO / "modele_plytek" / zrodlo / "uklad.json").read_text(encoding="utf-8"))
        if zmien is not None:
            wynik = zmien(d)
            d = d if wynik is None else wynik
        (kat / "uklad.json").write_text(json.dumps(d), encoding="utf-8")
        for f in pliki:
            (kat / f).write_bytes(b"")
        return kat

    return zrob


def zapisz_ascii_stl(p: Path, trojkaty: list[list[tuple[float, float, float]]]) -> Path:
    linie = ["solid test"]
    for t in trojkaty:
        linie.append("facet normal 0 0 0\n  outer loop")
        for v in t:
            linie.append(f"    vertex {v[0]} {v[1]} {v[2]}")
        linie.append("  endloop\nendfacet")
    linie.append("endsolid test")
    p.write_text("\n".join(linie), encoding="ascii")
    return p
