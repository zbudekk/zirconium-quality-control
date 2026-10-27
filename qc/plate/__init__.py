"""qc.plate - plytka: wyrownanie skanu do ukladu plytki, numer z dolkow kodu, ciecie na fragmenty gniazd."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import trimesh

from .ciecie import Fragment, potnij
from .kod import numer_plytki, odczytaj_kod
from .wyrownanie import BladPlytki, Wyrownanie, przenies, wyrownaj

__all__ = ["wyrownaj", "numer_plytki", "potnij", "analizuj", "Fragment", "Wyrownanie", "WynikPlytki",
           "BladPlytki"]


@dataclass
class WynikPlytki:
    numer: int | None
    wyrownanie: Wyrownanie
    fragmenty: list[Fragment] = field(default_factory=list)
    skan_wyrownany: trimesh.Trimesh | None = None
    uwagi: list[str] = field(default_factory=list)  # np. przyczyna numeru None


def analizuj(skan: trimesh.Trimesh, uklad, ustawienia) -> WynikPlytki:
    """Wyrownanie -> skan w ukladzie plytki -> numer -> ciecie."""
    w = wyrownaj(skan, uklad, ustawienia)
    T = np.asarray(w.T_skan_do_plytki, dtype=np.float64)
    v = przenies(skan.vertices, T)
    wyrownany = trimesh.Trimesh(v, np.asarray(skan.faces), process=False)
    numer, uwagi = odczytaj_kod(wyrownany, uklad)
    fragmenty = potnij(wyrownany, uklad, ustawienia)
    return WynikPlytki(numer=numer, wyrownanie=w, fragmenty=fragmenty, skan_wyrownany=wyrownany,
                       uwagi=uwagi)
