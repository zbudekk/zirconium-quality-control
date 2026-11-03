# -*- coding: utf-8 -*-
"""
Zachowanie toru importu sprawdz_A/B/C (import_stl → weld → bbox → Solid → general_checks) na uszkodzonych STL
z SP/lustro_A_uszk (zrob_lustra.py), KAŻDY plik osobno w try/except — żeby zobaczyć typ wyjątku per uszkodzenie,
bez zatrzymywania całości (sam sprawdz_A.py zatrzymuje się na pierwszym wyjątku).

  "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b -P test_import_uszkodzone.py
"""
import bpy, bmesh, math, os, sys, traceback
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

SP = r"<PC>\AppData\Local\Temp\claude\C--Users-<uzytkownik>-Desktop-Ramki\6066cedd-3612-4f95-9068-ea0e40643981\scratchpad\audyt_sprawdzacze"
STL = os.path.join(SP, "lustro_A_uszk", "wyniki_v2", "stl")

# --- dosłowne kopie z sprawdz_A.py (l. 76–93, 95–108, 206–245, 254–273) ---
def clear_scene(): bpy.ops.wm.read_factory_settings(use_empty=True)
def import_stl(path):
    clear_scene()
    bpy.ops.wm.stl_import(filepath=path)
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    assert len(objs) == 1, f"import dał {len(objs)} obiektów"
    return objs[0]
def weld(obj, dist=1e-5):
    bm = bmesh.new(); bm.from_mesh(obj.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist); bm.to_mesh(obj.data); bm.free(); obj.data.update()
def bbox(verts):
    xs = [v.x for v in verts]; ys = [v.y for v in verts]; zs = [v.z for v in verts]
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))
class Solid:
    def __init__(self, obj, matrix):
        me = obj.data; self.verts = [matrix @ v.co for v in me.vertices]; me.calc_loop_triangles()
        self.tris = [tuple(t.vertices) for t in me.loop_triangles]
        self.bvh = BVHTree.FromPolygons(self.verts, self.tris, all_triangles=True, epsilon=0.0); self.bb = bbox(self.verts)
def manifold_check(obj):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bad = sum(1 for e in bm.edges if len(e.link_faces) != 2); loose = sum(1 for v in bm.verts if len(v.link_edges) == 0); bm.free(); return bad, loose
def self_overlap(solid):
    n = 0
    for a, b in solid.bvh.overlap(solid.bvh):
        if a == b or set(solid.tris[a]) & set(solid.tris[b]): continue
        n += 1
    return n // 2
def components(obj):
    me = obj.data; n = len(me.vertices); parent = list(range(n))
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for e in me.edges:
        ra, rb = find(e.vertices[0]), find(e.vertices[1])
        if ra != rb: parent[ra] = rb
    return len({find(i) for i in range(n)})
def volume(solid):
    v = 0.0; V = solid.verts
    for a, b, c in solid.tris: v += V[a].dot(V[b].cross(V[c]))
    return v / 6.0 / 1000.0
def general_checks(name, obj, solid, exp_bb, exp_vol):
    out = {}
    ntri = len(solid.tris); nan = any(math.isnan(v.x) or math.isnan(v.y) or math.isnan(v.z) for v in solid.verts)
    out["K-01"] = ("ZAL" if (ntri > 100 and not nan) else "NIE", f"trójkątów {ntri}, NaN {nan}")
    bb = solid.bb; dims = (bb[1] - bb[0], bb[3] - bb[2], bb[5] - bb[4])
    out["K-02"] = ("ZAL" if all(abs(dims[i] - exp_bb[i]) <= 0.1 for i in range(3)) else "NIE", "gabaryt %s" % ([round(d, 3) for d in dims],))
    be, lv = manifold_check(obj); so = self_overlap(solid)
    out["K-03"] = ("ZAL" if (be == 0 and lv == 0 and so == 0) else "NIE", f"niemanifold {be}, luźne {lv}, samoprzecięcia {so}")
    nc = components(obj); out["K-04"] = ("ZAL" if nc == 1 else "NIE", f"składowych {nc}")
    vol = volume(solid); out["K-04b"] = ("ZAL" if (vol > 0 and abs(vol - exp_vol) <= 0.3 * exp_vol) else "NIE", f"objętość {vol:.3f}")
    return out

CASES = [("ramka_plytka_wieczorna_n2_v2.stl", "BRAK PLIKU"), ("ramka_plytka_wieczorna_n3_v2.stl", "OBCIĘTY do 50 %"),
         ("ramka_plytka_poranna_v2.stl", "0 BAJTÓW"), ("ramka_plytka_poranna_n4_v2.stl", "0 TRÓJKĄTÓW (poprawny nagłówek)"),
         ("ramka_plytka_poranna_n5_v2.stl", "NaN w jednym wierzchołku"), ("ramka_plytka_poranna_n6_v2.stl", "ASCII STL"),
         ("ramka_pokrywka_v2.stl", "ZŁY LICZNIK (+1000 w nagłówku)"), ("ramka_plytka_wieczorna_n1_v2.stl", "POPRAWNY (kontrola)")]
for name, what in CASES:
    path = os.path.join(STL, name)
    print("\n=== %s — %s" % (name, what))
    if not os.path.exists(path):
        print("   sprawdz_A l.585: os.path.exists → False → rec K-01 NIE 'brak pliku'; continue  [OK: raportuje B]"); continue
    try:
        obj = import_stl(path)
        print("   import OK: wierzchołków %d, ścian %d" % (len(obj.data.vertices), len(obj.data.polygons)))
        weld(obj)
        raw = bbox([v.co for v in obj.data.vertices])
        M = Matrix.Translation(Vector((-(raw[0] + raw[1]) / 2, -(raw[2] + raw[3]) / 2, -(raw[4] + 8))))
        S = Solid(obj, M)
        res = general_checks(name, obj, S, (96, 96, 8.6), 60.0)
        for k, (w, txt) in res.items(): print("   [%s] %s: %s" % (w, k, txt))
    except Exception as e:
        print("   PADA na etapie importu/kontroli: %s: %s" % (type(e).__name__, str(e).strip().splitlines()[-1][:200]))
        print("   → w sprawdz_A.py main() nie ma try/except: skrypt kończy się tu, wyniki_A_iter*.json NIE powstaje, poprzednie K-xx przepadają")
print("\nKONIEC")
