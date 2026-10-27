"""Porownanie wyniku inspekcji z prawda syntetycznego skanu: wykryte / pominiete / falszywe."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

RODZAJ_LICZONY = "ukruszenie"


@dataclass
class Porownanie:
    wykryte: int
    pominiete: int
    falszywe: int
    pary: list = field(default_factory=list)  # (Ubytek wykryty, UbytekPrawda)


def porownaj(wynik, prawda, T_prawdy, tolerancja_mm: float = 0.5) -> Porownanie:
    """Przypisanie zachlanne po rosnacej odleglosci srodkow, jeden do jednego.

    Srodki prawdy (uklad projektu bez skali) przenoszone przez T_prawdy do ukladu fragmentu.
    """
    prawdy = [u for u in prawda.ubytki if u.rodzaj == RODZAJ_LICZONY]
    wykryte = list(wynik.ubytki)
    pary = []
    if prawdy and wykryte:
        T = np.asarray(T_prawdy, dtype=np.float64).reshape(4, 4)
        sp = np.array([u.srodek for u in prawdy], dtype=np.float64) @ T[:3, :3].T + T[:3, 3]
        sw = np.array([np.asarray(u.srodek, dtype=np.float64) for u in wykryte])
        odl = np.linalg.norm(sw[:, None, :] - sp[None, :, :], axis=2)
        wolne_w = np.ones(len(wykryte), dtype=bool)
        wolne_p = np.ones(len(prawdy), dtype=bool)
        for k in np.argsort(odl, axis=None, kind="stable"):
            i, j = divmod(int(k), len(prawdy))
            if odl[i, j] > tolerancja_mm:
                break
            if wolne_w[i] and wolne_p[j]:
                wolne_w[i] = wolne_p[j] = False
                pary.append((wykryte[i], prawdy[j]))
    return Porownanie(wykryte=len(pary), pominiete=len(prawdy) - len(pary),
                      falszywe=len(wykryte) - len(pary), pary=pary)
