"""qc.plate - plytka: wyrownanie skanu do ukladu plytki, numer z dolkow kodu, ciecie na fragmenty gniazd."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import trimesh

from .ciecie import Fragment, potnij
from .kod import numer_plytki
from .wyrownanie import BladPlytki, Wyrownanie, wyrownaj

__all__ = ["wyrownaj", "numer_plytki", "potnij", "analizuj", "Fragment", "Wyrownanie", "WynikPlytki",
           "BladPlytki"]


@dataclass
class WynikPlytki:
    numer: int | None
    wyrownanie: Wyrownanie
    fragmenty: list[Fragment] = field(default_factory=list)
    skan_wyrownany: trimesh.Trimesh | None = None


def analizuj(skan: trimesh.Trimesh, uklad, ustawienia) -> WynikPlytki:
    """Wyrownanie -> skan w ukladzie plytki -> numer -> ciecie."""
    w = wyrownaj(skan, uklad, ustawienia)
    T = np.asarray(w.T_skan_do_plytki, dtype=np.float64)
    v = np.asarray(skan.vertices, dtype=np.float64) @ T[:3, :3].T + T[:3, 3]
    wyrownany = trimesh.Trimesh(v, np.asarray(skan.faces), process=False)
    numer = numer_plytki(wyrownany, uklad)
    fragmenty = potnij(wyrownany, uklad, ustawienia, numer=numer)
    return WynikPlytki(numer=numer, wyrownanie=w, fragmenty=fragmenty, skan_wyrownany=wyrownany)
