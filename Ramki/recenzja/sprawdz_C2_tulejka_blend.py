# -*- coding: utf-8 -*-
"""C iter2: położenie tulejki DC w .blend względem otworu ø12 korpusu W i gniazda DC (luz promieniowy, styk kołnierza)."""
import bpy, bmesh, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath=r"<PC>\Desktop\Ramki\wyniki_v2\ramka_v2.blend")
def world(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); bmesh.ops.triangulate(bm, faces=bm.faces)
    vs = [v.co.copy() for v in bm.verts]; fs = [[v.index for v in f.verts] for f in bm.faces]; bm.free(); return vs, fs
objs = {o.name: o for o in bpy.data.objects if o.type == "MESH"}
tn = [n for n in objs if "tulejka" in n.lower()]; print("tulejka:", tn)
t = objs[tn[0]]; tv, tf = world(t)
bb = [min(v.x for v in tv), max(v.x for v in tv), min(v.y for v in tv), max(v.y for v in tv), min(v.z for v in tv), max(v.z for v in tv)]
print("tulejka bbox", [round(b, 3) for b in bb])
# oś tulejki: najdłuższy wymiar najmniejszy -> oś; tu spodziewana oś X (ściana prawa/lewa)
dims = (bb[1]-bb[0], bb[3]-bb[2], bb[5]-bb[4]); ax = dims.index(min(dims)); print("oś tulejki:", "XYZ"[ax], "długość", round(dims[ax], 3))
cy = ((bb[2]+bb[3])/2, (bb[4]+bb[5])/2) if ax == 0 else None
kW = objs["korpus_W"] if "korpus_W" in objs else objs[[n for n in objs if "korpus_W" in n][0]]
kv, kf = world(kW); bvhK = BVHTree.FromPolygons(kv, kf)
gd = [n for n in objs if "gniazdo_dc" in n]; print("gniazdo:", gd)
gv, gf = world(objs[gd[0]]); bvhG = BVHTree.FromPolygons(gv, gf)
out = {"tulejka": tn[0], "bbox": [round(b, 3) for b in bb], "os": "XYZ"[ax]}
# promień walca i kołnierza w świecie: wierzchołki wg odległości od osi
def r_of(v): 
    if ax == 0: return math.hypot(v.y - cy[0], v.z - cy[1])
rs = sorted(set(round(r_of(v), 3) for v in tv)); print("promienie wierzchołków:", rs[:3], "...", rs[-3:])
# grupy: ~4.1 (otwór), ~5.925 (walec), ~7.5 (kołnierz)
cyl = [v for v in tv if abs(r_of(v) - 5.925) < 0.02]; fl = [v for v in tv if abs(r_of(v) - 7.5) < 0.02]
xs_c = sorted(set(round(v.x, 3) for v in cyl)); xs_f = sorted(set(round(v.x, 3) for v in fl)); print("walec x:", xs_c, "kołnierz x:", xs_f)
out["walec_x"] = xs_c; out["kolnierz_x"] = xs_f
# luz promieniowy: dla wierzchołków walca odległość do korpusu (ściana z otworem ø12) -> oczekiwane ≈ 0,075
dK = [bvhK.find_nearest(v)[3] for v in cyl]; print("walec→korpus: min %.4f max %.4f (n=%d)" % (min(dK), max(dK), len(cyl)))
out["walec_do_korpusu"] = (round(min(dK), 4), round(max(dK), 4))
# promień otworu w ścianie korpusu: promienie z osi w płaszczyźnie środka walca
xm = (xs_c[0] + xs_c[-1]) / 2; hits = []
for k in range(72):
    a = 2*math.pi*k/72; d = Vector((0, math.cos(a), math.sin(a)))
    h = bvhK.ray_cast(Vector((xm, cy[0], cy[1])), d, 20)
    if h[0]: hits.append((h[0] - Vector((xm, cy[0], cy[1]))).length)
print("otwór korpusu: r min %.4f max %.4f -> ø %.3f" % (min(hits), max(hits), 2*sum(hits)/len(hits))); out["otwor_korpusu_d"] = round(2*sum(hits)/len(hits), 4)
# kołnierz: odległość do korpusu (styk z licem ściany) i do gniazda
dF = [bvhK.find_nearest(v)[3] for v in fl]; print("kołnierz→korpus: min %.4f" % min(dF)); out["kolnierz_do_korpusu_min"] = round(min(dF), 4)
dG = [bvhG.find_nearest(v)[3] for v in tv]; print("tulejka→gniazdo: min %.4f" % min(dG)); out["tulejka_do_gniazda_min"] = round(min(dG), 4)
# ściana korpusu w osi tulejki: promień wzdłuż osi od zewnątrz
o = Vector((bb[1] + 30, cy[0], cy[1] + 6.5)); h = bvhK.ray_cast(o, Vector((-1, 0, 0)), 100); print("lico zewn. ściany (nad otworem) x =", round(h[0].x, 3) if h[0] else None)
h2 = bvhK.ray_cast(Vector((bb[0] - 30, cy[0], cy[1] + 6.5)), Vector((1, 0, 0)), 100); print("lico wewn. ściany x =", round(h2[0].x, 3) if h2[0] else None)
out["sciana_x"] = [round(h2[0].x, 3) if h2[0] else None, round(h[0].x, 3) if h[0] else None]
json.dump(out, open(r"<PC>\Desktop\Ramki\recenzja\wyniki_C_iter2_tulejka_blend.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
