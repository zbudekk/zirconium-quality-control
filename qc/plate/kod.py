"""Numer plytki z dolkow kodu (bity A, B, C: n = A + 2B + 4C) na skanie wyrownanym."""

from __future__ import annotations

import numpy as np
import trimesh

from qc.uklad import DOLEK_D, DOLEK_GLEBOKOSC, Uklad, numer_z_kodu

PROMIEN_POMIARU = 0.6  # x d/2 wokol pozycji dolka
PROG_BITU = 0.5  # mediana z < -0,5 x glebokosc -> dolek obecny
ZAKRES_Z = (-2.0, 0.3)  # x glebokosc / mm nad wierzchem: bez dna plytki, kieszeni magnesow i prac


def bity_kodu(skan_wyrownany: trimesh.Trimesh, uklad: Uklad) -> set[str]:
    """Bity, dla ktorych w skanie (uklad plytki) jest dolek kodu."""
    v = np.asarray(skan_wyrownany.vertices, dtype=np.float64)
    bity = set()
    for bit, (x, y) in uklad.dolki_kodu.items():
        d, glebokosc = uklad.wymiary_dolkow.get(bit, (DOLEK_D, DOLEK_GLEBOKOSC))
        w_kole = np.hypot(v[:, 0] - x, v[:, 1] - y) <= PROMIEN_POMIARU * d / 2
        z = v[w_kole, 2]
        z = z[(z >= ZAKRES_Z[0] * glebokosc) & (z <= ZAKRES_Z[1])]
        if len(z) and float(np.median(z)) < -PROG_BITU * glebokosc:
            bity.add(bit)
    return bity


def numer_plytki(skan_wyrownany: trimesh.Trimesh, uklad: Uklad) -> int | None:
    """Numer plytki z dolkow kodu; None gdy kod 0 albo 7 albo numer spoza uklad.numery."""
    numer = numer_z_kodu(bity_kodu(skan_wyrownany, uklad))
    return numer if numer in uklad.numery else None
