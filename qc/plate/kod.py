"""Numer plytki z dolkow kodu (bity A, B, C: n = A + 2B + 4C) na skanie wyrownanym."""

from __future__ import annotations

import numpy as np
import trimesh

from qc.uklad import DOLEK_D, DOLEK_GLEBOKOSC, Uklad, numer_z_kodu

PROMIEN_POMIARU = 0.6  # x d/2 wokol pozycji dolka
PROG_BITU = 0.5  # mediana z < -0,5 x glebokosc -> dolek obecny
ZAKRES_Z = (-2.0, 0.3)  # x glebokosc / mm nad wierzchem: bez dna plytki, kieszeni magnesow i prac
MIN_PUNKTOW = 5  # w kole pomiaru i w pierscieniu; mniej = brak danych
PIERSCIEN_MM = (0.3, 0.9)  # pierscien wierzchu: r w (d/2 + 0,3; d/2 + 0,9) (dolki co 3 mm)
MAX_ODCHYLKA_PIERSCIENIA = 0.25  # x glebokosc: mediana |z| pierscienia (plaska okolica)


def wierzcholki_scian(siatka: trimesh.Trimesh) -> np.ndarray:
    """Wierzcholki uzywane przez sciany (bez pozostalosci po usunietych scianach)."""
    v = np.asarray(siatka.vertices, dtype=np.float64)
    uzyte = np.zeros(len(v), dtype=bool)
    uzyte[np.asarray(siatka.faces, dtype=np.int64).ravel()] = True
    return v[uzyte]


def odczytaj_kod(skan_wyrownany: trimesh.Trimesh, uklad: Uklad) -> tuple[int | None, list[str]]:
    """(numer albo None, uwagi). Bit bez danych (dolek zakryty, brak punktow) = numer None z uwaga."""
    v = wierzcholki_scian(skan_wyrownany)
    bity, uwagi = set(), []
    for bit, (x, y) in sorted(uklad.dolki_kodu.items()):
        d, glebokosc = uklad.wymiary_dolkow.get(bit, (DOLEK_D, DOLEK_GLEBOKOSC))
        r = np.hypot(v[:, 0] - x, v[:, 1] - y)
        z_ok = (v[:, 2] >= ZAKRES_Z[0] * glebokosc) & (v[:, 2] <= ZAKRES_Z[1])
        z = v[(r <= PROMIEN_POMIARU * d / 2) & z_ok, 2]
        pierscien = v[(r > d / 2 + PIERSCIEN_MM[0]) & (r < d / 2 + PIERSCIEN_MM[1]) & z_ok, 2]
        if len(z) < MIN_PUNKTOW:
            uwagi.append(f"dolek kodu {bit}: brak danych ({len(z)} punktow w kole)")
            continue
        if len(pierscien) < MIN_PUNKTOW or np.median(np.abs(pierscien)) > MAX_ODCHYLKA_PIERSCIENIA * glebokosc:
            uwagi.append(f"dolek kodu {bit}: okolica nieplaska albo bez danych ({len(pierscien)} punktow)")
            continue
        if float(np.median(z)) < -PROG_BITU * glebokosc:
            bity.add(bit)
    if uwagi:
        return None, uwagi
    numer = numer_z_kodu(bity)
    if numer is None:
        return None, [f"kod plytki {''.join(sorted(bity)) or '-'}: brak numeru (0 albo 7)"]
    if numer not in uklad.numery:
        return None, [f"kod plytki: numer {numer} spoza ukladu {uklad.nazwa} {uklad.numery}"]
    return numer, []


def numer_plytki(skan_wyrownany: trimesh.Trimesh, uklad: Uklad) -> int | None:
    """Numer plytki z dolkow kodu; None gdy kod 0 albo 7, numer spoza uklad.numery albo dolek bez danych."""
    return odczytaj_kod(skan_wyrownany, uklad)[0]
