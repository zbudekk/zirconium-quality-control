# -*- coding: utf-8 -*-
"""
trzecie_oko.py l.105–145: dopasowanie STL → obiekt .blend przez 7 kandydatów obrotu + KD‑drzewo.
Test: dla każdego STL wypisz maxd WSZYSTKICH kandydatów — czy dla części symetrycznych kilku kandydatów daje maxd ≈ 0
(wybór zależy wtedy od kolejności słownika, a tabela A pokazuje „typ” dowolny z równoważnych).
Dodatkowo: czy lustrzane odbicie (skala −1 w X; nie ma go w kandydatach) zostałoby wykryte (maxd > 1e-3).

  "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b -P test_transformacje.py
"""
import bpy, os, math
from mathutils import Vector, Matrix, kdtree

SP = r"<PC>\AppData\Local\Temp\claude\C--Users-<uzytkownik>-Desktop-Ramki\6066cedd-3612-4f95-9068-ea0e40643981\scratchpad\audyt_sprawdzacze"
STL_DIR = os.path.join(SP, "lustro", "wyniki_v2", "stl"); BLEND = os.path.join(SP, "lustro", "wyniki_v2", "ramka_v2.blend")
BLEND_NAME = {"ramka_blat_v2.stl": "blat", "ramka_korpus_W_v2.stl": "korpus_W", "ramka_wkladka_v2.stl": "wkladka", "ramka_pokrywka_v2.stl": "pokrywka",
              "ramka_tulejka_dc_v2.stl": "tulejka_dc", "ramka_podkladka_panelu_1_v2.stl": "podkladka_panelu_1", "ramka_plytka_wieczorna_n1_v2.stl": "plytka_wieczorna_n1"}
ROT_CANDS = {"przesuniecie": Matrix.Identity(3), "obrot_180_X": Matrix.Rotation(math.pi, 3, "X"), "obrot_180_Y": Matrix.Rotation(math.pi, 3, "Y"),
             "obrot_+90_Y": Matrix.Rotation(math.pi / 2, 3, "Y"), "obrot_-90_Y": Matrix.Rotation(-math.pi / 2, 3, "Y"), "obrot_+90_X": Matrix.Rotation(math.pi / 2, 3, "X"),
             "obrot_-90_X": Matrix.Rotation(-math.pi / 2, 3, "X"), "LUSTRO_X (nie w kandydatach)": Matrix.Scale(-1, 3, Vector((1, 0, 0))), "obrot_180_Z (nie w kandydatach)": Matrix.Rotation(math.pi, 3, "Z")}
def bbox(verts):
    xs = [v.x for v in verts]; ys = [v.y for v in verts]; zs = [v.z for v in verts]
    return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))
bpy.ops.wm.open_mainfile(filepath=BLEND)
BOBJ = {o.name: [o.matrix_world @ v.co for v in o.data.vertices] for o in bpy.data.objects if o.type == "MESH"}
for f, bname in BLEND_NAME.items():
    bpy.ops.wm.stl_import(filepath=os.path.join(STL_DIR, f)); o = bpy.context.selected_objects[0]
    verts = [v.co.copy() for v in o.data.vertices]; bpy.data.objects.remove(o)
    bverts = BOBJ[bname]; kd = kdtree.KDTree(len(bverts))
    for i, v in enumerate(bverts): kd.insert(v, i)
    kd.balance()
    res = []
    for rn, R in ROT_CANDS.items():
        rv = [R @ v for v in verts]; mn, mx = bbox(rv); bmn, bmx = bbox(bverts); t = (bmn + bmx) / 2 - (mn + mx) / 2
        res.append((max(kd.find(v + t)[2] for v in rv), rn))
    res.sort()
    print("[TEST] %-34s " % f + " | ".join("%s=%.1e" % (rn, d) for d, rn in res[:4]) + "  | lustroX=%.1e" % [d for d, rn in res if rn.startswith("LUSTRO")][0])
print("[TEST] KONIEC")
