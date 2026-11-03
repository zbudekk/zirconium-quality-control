"""Atrapy koron: syntetyczne, szczelne siatki o kształcie zbliżonym do korony.

Zastępują prawdziwe projekty STL z folderu „Cyrkon”, dopóki ich nie ma.
Korona ma zewnętrzną powierzchnię (kopuła z guzkami), wnętrze (ubytek
protetyczny) i brzeg (pierścień na z = 0). Orientacja jak w typowym
projekcie: brzeg na dole, powierzchnia żująca na górze.

Użycie:
    python narzedzia/atrapy_koron.py --wyjscie dane/stl --ile 12 --seed 1
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import trimesh

TYPY = {
    # nazwa: (szerokość W, długość L, wysokość H, liczba guzków, amplituda guzków)
    "siekacz": (6.5, 5.0, 10.0, 1, 0.04),
    "kiel": (7.0, 6.5, 10.5, 1, 0.08),
    "przedtrzonowy": (8.0, 7.0, 8.0, 2, 0.10),
    "trzonowy": (10.5, 11.0, 7.5, 4, 0.12),
}


def korona(
    W: float,
    L: float,
    H: float,
    guzki: int = 4,
    amp_guzkow: float = 0.1,
    scianka: float = 0.6,
    grubosc_zujaca: float = 1.0,
    n_theta: int = 160,
    n_u: int = 200,
    rng: np.random.Generator | None = None,
) -> trimesh.Trimesh:
    """Buduje szczelną koronę jako siatkę o topologii torusa (profil zamknięty)."""
    rng = rng or np.random.default_rng(0)
    f1, f2, f3 = rng.uniform(0, 2 * np.pi, 3)
    a2, a3 = rng.uniform(0.02, 0.06), rng.uniform(0.01, 0.04)

    theta = np.linspace(0, 2 * np.pi, n_theta, endpoint=False)
    # promień obrysu: elipsa W × L z łagodną nieregularnością
    R = (W * L) / (2 * np.sqrt((L * np.cos(theta)) ** 2 + (W * np.sin(theta)) ** 2))
    R = R * (1 + a2 * np.cos(2 * theta + f1) + a3 * np.cos(3 * theta + f2))

    u = np.linspace(0, 1, n_u, endpoint=False)
    verts = np.empty((n_u, n_theta, 3))
    for i, ui in enumerate(u):
        if ui < 0.5:  # zewnątrz: od brzegu (s=0) do szczytu (s=1)
            s = 2 * ui
            rad = R * (1 + 0.10 * np.sin(np.pi * s)) * np.cos(np.pi * s / 2)
            z = H * np.sin(np.pi * s / 2)
            z = z + H * amp_guzkow * np.cos(guzki * theta + f3) * s**2
        else:  # wnętrze: od szczytu (s=1) w dół do brzegu (s=0)
            s = 2 - 2 * ui
            Ri = np.maximum(R - scianka, 0.5)
            rad = Ri * np.cos(np.pi * s / 2) * (1 + 0.05 * np.sin(np.pi * s))
            z = (H - grubosc_zujaca) * np.sin(np.pi * s / 2)
        verts[i, :, 0] = rad * np.cos(theta)
        verts[i, :, 1] = rad * np.sin(theta)
        verts[i, :, 2] = z

    V = verts.reshape(-1, 3)
    idx = np.arange(n_u * n_theta).reshape(n_u, n_theta)
    i0 = idx
    i1 = np.roll(idx, -1, axis=0)  # następny wiersz profilu (periodycznie)
    j1 = np.roll(np.arange(n_theta), -1)
    a, b, c, d = i0, i0[:, j1], i1[:, j1], i1
    F = np.concatenate(
        [np.stack([a, b, c], -1).reshape(-1, 3), np.stack([a, c, d], -1).reshape(-1, 3)]
    )
    m = trimesh.Trimesh(V, F, process=False)
    m.merge_vertices()
    m.update_faces(m.nondegenerate_faces())
    m.fix_normals()
    return m


def most(rng: np.random.Generator, punkty: int = 4) -> trimesh.Trimesh:
    """Most: korony w rzędzie wzdłuż x połączone łącznikami (siatka złożona)."""
    czesci = []
    x = 0.0
    typy = ["przedtrzonowy", "przedtrzonowy", "trzonowy", "trzonowy"][:punkty]
    poprzedni = None
    for t in typy:
        W, L, H, g, amp = TYPY[t]
        k = korona(W, L, H, g, amp, rng=rng)
        k.apply_translation([x + L / 2, 0, 0])
        if poprzedni is not None:
            lacznik = trimesh.creation.box([2.0, 3.0, 3.0])
            lacznik.apply_translation([x, 0, H * 0.45])
            czesci.append(lacznik)
        czesci.append(k)
        poprzedni = k
        x += L + 0.4
    return trimesh.util.concatenate(czesci)


def generuj(wyjscie: Path, ile: int, seed: int, mosty: int = 1) -> list[Path]:
    rng = np.random.default_rng(seed)
    wyjscie.mkdir(parents=True, exist_ok=True)
    pliki = []
    nazwy = list(TYPY)
    for i in range(ile):
        t = nazwy[i % len(nazwy)]
        W, L, H, g, amp = TYPY[t]
        sk = rng.uniform(0.92, 1.08, 3)
        m = korona(W * sk[0], L * sk[1], H * sk[2], g, amp, rng=rng)
        zab = {"siekacz": 11, "kiel": 13, "przedtrzonowy": 14, "trzonowy": 16}[t] + (i % 2) * 20
        p = wyjscie / f"atrapa_{i + 1:02d}_{t}_{zab}.stl"
        m.export(p)
        pliki.append(p)
    for j in range(mosty):
        m = most(rng)
        p = wyjscie / f"atrapa_most_{j + 1:02d}_4pkt.stl"
        m.export(p)
        pliki.append(p)
    return pliki


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--wyjscie", type=Path, default=Path("dane/stl"))
    ap.add_argument("--ile", type=int, default=12)
    ap.add_argument("--mosty", type=int, default=1)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    for p in generuj(a.wyjscie, a.ile, a.seed, a.mosty):
        print(p)


if __name__ == "__main__":
    main()
