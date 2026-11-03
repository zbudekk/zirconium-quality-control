"""podglad3d — okno Open3D z mapą odchyłek jednej pracy (uruchamiane jako osobny proces z okna ``ui_test``).

Użycie: ``py -3.12 -m stanowisko.podglad3d <plik.npz>`` — plik z ``P`` (punkty N×3, układ płytki), ``d``
(odchyłka każdego punktu, mm; < 0 = pod powierzchnią projektu) i ``ubytki`` (K×4: x, y, z, średnica).
Kolory: szary = w tolerancji, czerwony = pod powierzchnią (brak materiału), niebieski = nad; ubytki jako
czarne kółka. Osobny proces, bo okno GL Open3D i pętla Qt w jednym procesie na Windows blokują się
nawzajem; podgląd 3D w samym Qt (QOpenGLWidget) to osobny moduł na później.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np


def kolory_odchylek(d: np.ndarray, prog: float) -> np.ndarray:
    """RGB w [0, 1]: szary w ±prog, liniowo do czerwonego (−) / niebieskiego (+) przy 3·prog."""
    k = np.full((len(d), 3), 0.75)
    u = np.clip(np.abs(d) / (3 * prog), 0, 1)
    pod = d < -prog
    nad = d > prog
    k[pod] = np.c_[0.75 + 0.25 * u[pod], 0.75 - 0.6 * u[pod], 0.75 - 0.6 * u[pod]]
    k[nad] = np.c_[0.75 - 0.6 * u[nad], 0.75 - 0.5 * u[nad], 0.75 + 0.25 * u[nad]]
    return k


def pokaz(plik: Path, prog: float = 0.08) -> None:
    import open3d as o3d

    z = np.load(plik)
    P, d = z["P"], z["d"]
    pc = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(P))
    pc.colors = o3d.utility.Vector3dVector(kolory_odchylek(d, prog))
    geom = [pc]
    for x, y, zz, sr in z["ubytki"]:
        s = o3d.geometry.TriangleMesh.create_sphere(radius=max(0.15, sr / 2), resolution=12)
        s.translate([x, y, zz])
        s.paint_uniform_color([0, 0, 0])
        geom.append(o3d.geometry.LineSet.create_from_triangle_mesh(s))
    o3d.visualization.draw_geometries(geom, window_name=f"odchyłki {plik.stem} (czerwone = brak materiału)", width=900, height=700)


if __name__ == "__main__":
    pokaz(Path(sys.argv[1]), float(sys.argv[2]) if len(sys.argv) > 2 else 0.08)
