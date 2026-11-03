# KOPIA R53: wyniki do skrypty/wyniki/, transformacja y_min + 52,4 (rama po R53)
# -*- coding: utf-8 -*-
"""Sprawdzenie dodatkowe (poza protokołem): ciągłość kanałów przewodów Halla w spodzie wkładki.
Mapa spodu promieniami z dołu (siatka 0,25 mm): komórka 'kanał' = pierwsze trafienie na Z w [0,9; 1,7] (kanał 1,0 / przelot 1,2–1,5 nad płaszczyzną spodu Z=0).
BFS po komórkach kanału od kieszeni Halla A/B/C do wylotu kanału ucha (±64, 89). Zapis PNG mapy spodu."""
import bpy, os, sys, math, zlib, struct, json
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
sys.path.insert(0, r"<PC>\Desktop\Ramki\recenzja")
ROOT = r"<PC>\Desktop\Ramki"; REC = os.path.join(ROOT, "sesje_2026-10-31", "poprawki_pasowan", "skrypty", "wyniki")   # R53: kopia
path = os.path.join(ROOT, "wyniki_v2", "stl", "ramka_wkladka_v2.stl")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=path)
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
raw = [v.co for v in obj.data.vertices]
xs = [v.x for v in raw]; ys = [v.y for v in raw]; zs = [v.z for v in raw]
M = Matrix.Translation(Vector((-(min(xs) + max(xs)) / 2, -(min(ys) + 52.4), -(min(zs) + 3.5))))
verts = [M @ v for v in raw]
obj.data.calc_loop_triangles()
tris = [tuple(t.vertices) for t in obj.data.loop_triangles]
bvh = BVHTree.FromPolygons(verts, tris, all_triangles=True)
step = 0.25
x0, x1, y0, y1 = -66, 66, -54, 97
nx = int(round((x1 - x0) / step)) + 1; ny = int(round((y1 - y0) / step)) + 1
grid = []
for j in range(ny):
    y = y0 + j * step; row = []
    for i in range(nx):
        x = x0 + i * step
        hit = bvh.ray_cast(Vector((x, y, -10)), Vector((0, 0, 1)), 50)
        row.append(None if hit[0] is None else hit[0].z)
    grid.append(row)
def cell(x, y):
    return int(round((x - x0) / step)), int(round((y - y0) / step))
def is_chan(i, j):
    z = grid[j][i]
    return z is not None and 0.9 <= z <= 1.7
from collections import deque
def bfs(start, goal):
    si, sj = cell(*start); gi, gj = cell(*goal)
    # start: najbliższa komórka kanału w promieniu 2 mm
    seeds = [(si + di, sj + dj) for di in range(-8, 9) for dj in range(-8, 9) if 0 <= si + di < nx and 0 <= sj + dj < ny and is_chan(si + di, sj + dj)]
    goals = {(gi + di, gj + dj) for di in range(-8, 9) for dj in range(-8, 9)}
    seen = set(seeds); q = deque(seeds); n = 0
    while q:
        i, j = q.popleft(); n += 1
        if (i, j) in goals:
            return True, n, len(seeds)
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = i + di, j + dj
            if 0 <= a < nx and 0 <= b < ny and (a, b) not in seen and is_chan(a, b):
                seen.add((a, b)); q.append((a, b))
    return False, n, len(seeds)
res = {}
for nm, start, goal in (("C", (44, 44), (64, 89)), ("B", (-44, 44), (-64, 89)), ("A", (-44, -44), (-64, 89))):
    ok, n, ns = bfs(start, goal)
    res[nm] = {"ciagly": ok, "komorek_kanalu_odwiedzonych": n, "komorek_startowych": ns}
    print(f"KANAL {nm}: ciągły={ok}, odwiedzone komórki {n}, start {ns}")
# głębokość kanału na trasie (min/max z trafień w komórkach odwiedzonych nie zapisujemy; prosta statystyka)
vals = [z for row in grid for z in row if z is not None and 0.9 <= z <= 1.7]
print("KANAL stat: komórek kanałowych", len(vals), "z min", round(min(vals), 3), "max", round(max(vals), 3))
# PNG: 0 (brak trafienia) czarny; z 0 = ciemny; kanał jasny; półki (2,5) i góra inne
def write_png(p, rows, vmin, vmax):
    h = len(rows); w = len(rows[0]); raw = bytearray()
    for row in rows:
        raw.append(0)
        for z in row:
            raw.append(0 if z is None else max(0, min(255, int(40 + 215 * (z - vmin) / (vmax - vmin)))))
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    open(p, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))
write_png(os.path.join(REC, "spod_wkladki_kanaly.png"), list(reversed(grid)), -0.2, 3.0)
json.dump(res, open(os.path.join(REC, "wyniki_B_iter2_kanaly.json"), "w", encoding="utf-8"), indent=1)
