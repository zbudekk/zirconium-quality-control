"""Rzut z góry skanu płytki jako PNG (mapa wysokości), do szybkiej kontroli wzrokowej.

Użycie (z katalogu stanowisko/):
    py -3.12 narzedzia/rzut_z_gory.py dane/syntetyczne/skan_wieczorna_n2_s0001.stl [--px 0.1] [--prawda]
Z opcją --prawda nanosi numery zajętych gniazd (w środku gniazda z uklad.json płytki)
i krzyżyki w miejscach ubytków z JSON obok STL.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from stanowisko import uklad as U  # noqa: E402


def mapa_wysokosci(m: trimesh.Trimesh, px: float) -> tuple[np.ndarray, np.ndarray]:
    """Zwraca (siatka z_max, [xmin, ymin]) — każdemu pikselowi najwyższy wierzchołek."""
    if not (math.isfinite(px) and px > 0):
        raise ValueError(f"px (mm na piksel) musi być > 0, jest {px}")
    pts = m.vertices
    if len(pts) == 0:
        raise ValueError("siatka pusta: brak wierzchołków")
    if not np.isfinite(pts).all():
        raise ValueError("siatka zawiera NaN/nieskończoność we wierzchołkach")
    xy0 = pts[:, :2].min(0)
    ij = np.floor((pts[:, :2] - xy0) / px).astype(int)
    w, h = ij.max(0) + 1
    Z = np.full((h, w), -np.inf)
    np.maximum.at(Z, (ij[:, 1], ij[:, 0]), pts[:, 2])
    Z[np.isinf(Z)] = np.nan
    return Z, xy0


def render(p_stl: Path, px: float, prawda: bool) -> Path:
    if not (math.isfinite(px) and px > 0):
        raise ValueError(f"px (mm na piksel) musi być > 0, jest {px}")
    m = trimesh.load(p_stl, force="mesh")
    Z, xy0 = mapa_wysokosci(m, px)
    zz = Z[~np.isnan(Z)]
    z0, z1 = np.percentile(zz, 1), np.percentile(zz, 99.5)
    img = np.clip((Z - z0) / max(z1 - z0, 1e-6), 0, 1)
    img = np.where(np.isnan(Z), 0.0, img)
    rgb = np.stack([img * 255, img * 220 + 20, img * 180 + 40], -1).astype(np.uint8)
    im = Image.fromarray(rgb[::-1])  # y do góry na obrazku = y "do tyłu" płytki
    d = ImageDraw.Draw(im)
    h = im.height

    def pix(x, y):
        return (x - xy0[0]) / px, h - (y - xy0[1]) / px

    p_json = p_stl.with_suffix(".json")
    if prawda and p_json.exists():
        pr = json.loads(p_json.read_text(encoding="utf-8"))
        uk = U.wczytaj(pr["plytka"])
        for w in pr["prace"]:
            for u in w["ubytki"]:
                x, y = pix(u["x"], u["y"])
                r = 6
                d.line([x - r, y - r, x + r, y + r], fill=(255, 0, 0), width=2)
                d.line([x - r, y + r, x + r, y - r], fill=(255, 0, 0), width=2)
            g = uk.gniazdo(w["gniazdo"])  # translacja z prawdy zawiera centrowanie projektu, nie środek pracy
            x, y = pix(g.x, g.y)
            d.text((x - 6, y - 6), str(w["gniazdo"]), fill=(0, 90, 255))
    out = p_stl.with_suffix(".png")
    im.save(out)
    return out


def _dodatnia(s: str) -> float:
    try:
        v = float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"oczekiwano liczby, jest {s!r}") from None
    if not (math.isfinite(v) and v > 0):
        raise argparse.ArgumentTypeError(f"--px musi być > 0, jest {s!r}")
    return v


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stl", type=Path, nargs="+")
    ap.add_argument("--px", type=_dodatnia, default=0.1, help="mm na piksel (> 0)")
    ap.add_argument("--prawda", action="store_true")
    a = ap.parse_args()
    for p in a.stl:
        print(render(p, a.px, a.prawda))


if __name__ == "__main__":
    main()
