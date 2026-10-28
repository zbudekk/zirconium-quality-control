"""Wstepny filtr kandydatow: cechy fragmentu vs cechy projektow z puli (przeskalowane o k wpisu)."""

from dataclasses import dataclass

import trimesh

from qc.catalog.cechy import Cechy, odleglosc, pasuje


@dataclass(eq=False)
class WpisPuli:
    projekt_id: str
    siatka: trimesh.Trimesh
    cechy: Cechy | None  # None = plik uszkodzony, wpis pomijany
    wspolczynnik: float


def kandydaci(cechy_fragmentu: Cechy, pula: list[WpisPuli], ustawienia) -> list[WpisPuli]:
    """Wpisy, ktore moga byc fragmentem; rosnaco po odleglosci cech, najwyzej max_kandydatow."""
    return [w for _, w in kandydaci_z_odlegloscia(cechy_fragmentu, pula, ustawienia)]


def kandydaci_z_odlegloscia(cechy_fragmentu: Cechy, pula: list[WpisPuli],
                            ustawienia) -> list[tuple[float, WpisPuli]]:
    """Jak kandydaci, ale z odlegloscia cech (do wczesnego wyjscia w dopasuj)."""
    wyniki = [(d, w) for d, w in wedlug_odleglosci(cechy_fragmentu, pula)
              if pasuje(cechy_fragmentu, w.cechy, w.wspolczynnik, ustawienia)]
    return wyniki[:ustawienia.dopasowanie.max_kandydatow]


def wedlug_odleglosci(cechy_fragmentu: Cechy, pula: list[WpisPuli]) -> list[tuple[float, WpisPuli]]:
    """Wszystkie wpisy z cechami rosnaco po odleglosci cech (bez progow pasuje; rowne - kolejnosc puli)."""
    wyniki = []
    for i, wpis in enumerate(pula):
        if wpis.cechy is None:
            continue
        wyniki.append((odleglosc(cechy_fragmentu, wpis.cechy.przeskaluj(wpis.wspolczynnik)), i, wpis))
    wyniki.sort(key=lambda x: (x[0], x[1]))
    return [(d, w) for d, _, w in wyniki]
