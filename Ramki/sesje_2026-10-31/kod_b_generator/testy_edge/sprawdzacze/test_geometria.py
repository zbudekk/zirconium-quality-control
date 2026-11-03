# -*- coding: utf-8 -*-
"""
Testy geometryczne funkcji pomiarowych skryptów sprawdzających (Blender -b -P).
Każdy test: kopia (dosłowna) funkcji z audytowanego skryptu + syntetyczne lub realne wejście + obserwowany wynik.
Czyta z lustra w scratchpadzie (kopia wyniki_v2), pisze tylko log na stdout. Nie dotyka projektu.

  "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b -P test_geometria.py

T1  trzecie_oko.gap()/chord(): brak znaku — dwa pudełka z PRZENIKANIEM 0,2 dają luz +0,2
T2  sprawdz_*.Solid.probe(): sonda leżąca dokładnie na ścianie zalicza i „W”, i „POZA” (przesunięcie 0,1 w stronę oczekiwaną)
T3  sprawdz_C2_tulejka_blend: find_nearest()[3] bez znaku — tulejka przeskalowana do ø12,15 (wcisk 0,075/stronę) daje „luz 0,075”
T4  sprawdz_B K-53 (skurcz 0,05 + BVHTree.overlap): tulejka ø12,00 / 12,10 / 12,15 / 12,30 w otworze ø12 korpusu_W — od kiedy wykrywa przenikanie
T5  trzecie_oko.overlap(): bryła całkowicie zanurzona w drugiej (bez przecięć trójkątów) → 0 par, wnikanie 0
T6  trzecie_oko: tulejka 11,85 w otworze 12 — pary trójkątów i wnikanie (czy sagitta daje fałszywy styk)
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

SP = r"<PC>\AppData\Local\Temp\claude\C--Users-<uzytkownik>-Desktop-Ramki\6066cedd-3612-4f95-9068-ea0e40643981\scratchpad\audyt_sprawdzacze"
BLEND = os.path.join(SP, "lustro", "wyniki_v2", "ramka_v2.blend")
STL_TUL = os.path.join(SP, "lustro", "wyniki_v2", "stl", "ramka_tulejka_dc_v2.stl")

def P(*a):
    print("[TEST]", *a)

# ------------------------------------------------------------------ kopie funkcji z trzecie_oko.py (l. 162–262)
class Part:
    def __init__(self, name, verts, polys):
        self.name = name; self.verts = verts; self.polys = polys
        self.bvh = BVHTree.FromPolygons(verts, polys, all_triangles=False)
AX = {"X": Vector((1, 0, 0)), "Y": Vector((0, 1, 0)), "Z": Vector((0, 0, 1)), "-X": Vector((-1, 0, 0)), "-Y": Vector((0, -1, 0)), "-Z": Vector((0, 0, -1))}
def vec(d): return AX[d] if isinstance(d, str) else Vector(d).normalized()
def hit(part, p, d, maxd=1e6):
    loc, nrm, idx, dist = part.bvh.ray_cast(Vector(p), vec(d), maxd)
    return (loc, nrm, dist) if loc is not None else (None, None, None)
def chord(part, p, d):
    a = hit(part, p, d)[2]; b = hit(part, p, -vec(d))[2]
    return None if (a is None or b is None) else a + b
def gap(partA, partB, p, d):
    a = hit(partA, p, d)[2]; b = hit(partB, p, -vec(d))[2]
    return None if (a is None or b is None) else a + b
def box(name, x0, x1, y0, y1, z0, z1):
    vs = [Vector((x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    ps = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
    return Part(name, vs, ps)

# ------------------------------------------------------------------ kopia Solid.probe z sprawdz_B.py (l. 52–109)
class Solid:
    def __init__(self, verts, tris, name=""):
        self.name = name; self.verts = verts; self.tris = tris
        self.bvh = BVHTree.FromPolygons(verts, tris, all_triangles=True, epsilon=0.0)
        xs = [v.x for v in verts]; ys = [v.y for v in verts]; zs = [v.z for v in verts]
        self.bb = (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))
        self.dirs = [Vector((1.0, 0.00071, 0.00137)).normalized(), Vector((0.00083, 1.0, 0.00119)).normalized(), Vector((0.00097, 0.00061, 1.0)).normalized()]
        self.diag = (Vector((self.bb[1], self.bb[3], self.bb[5])) - Vector((self.bb[0], self.bb[2], self.bb[4]))).length + 10
    def count_hits(self, p, d):
        n = 0; o = Vector(p); last = None
        for _ in range(500):
            h = self.bvh.ray_cast(o, d, self.diag)
            if h[0] is None: break
            loc = h[0]
            if last is None or (loc - last).length > 1e-5: n += 1
            last = loc; o = loc + d * 1e-4
        return n
    def inside3(self, p): return [self.count_hits(p, d) % 2 == 1 for d in self.dirs]
    def probe(self, p, expect_in):
        p = Vector(p); r = self.inside3(p)
        loc, nrm, idx, dist = self.bvh.find_nearest(p)
        e = {"p": [round(c, 3) for c in p], "oczek": "W" if expect_in else "POZA", "r3": ["W" if x else "P" for x in r], "d_sciana": round(dist, 3)}
        if r.count(True) in (0, 3):
            e["wynik"] = "W" if r[0] else "POZA"
        else:
            if nrm is None or nrm.length == 0: nrm = Vector((0, 0, 1))
            p2 = p + (-nrm if expect_in else nrm) * 0.1
            r2 = self.inside3(p2)
            e["niestabilna"] = True; e["r3_przes"] = ["W" if x else "P" for x in r2]
            e["wynik"] = ("W" if r2[0] else "POZA") if r2.count(True) in (0, 3) else "NIESTABILNA"
        e["ok"] = (e["wynik"] == e["oczek"])
        return e
def box_solid(x0, x1, y0, y1, z0, z1, name):
    V = [Vector((x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    T = [(0, 2, 1), (1, 2, 3), (4, 5, 6), (5, 7, 6), (0, 1, 4), (1, 5, 4), (2, 6, 3), (3, 6, 7), (0, 4, 2), (2, 4, 6), (1, 3, 5), (3, 7, 5)]
    return Solid(V, T, name)
# kopia shrunk_bvh z sprawdz_B.py (l. 426–435)
def vertex_normals(verts, tris):
    nrm = [Vector((0, 0, 0)) for _ in verts]
    for a, b, c in tris:
        n = (verts[b] - verts[a]).cross(verts[c] - verts[a]); nrm[a] += n; nrm[b] += n; nrm[c] += n
    return [n.normalized() if n.length > 0 else Vector((0, 0, 1)) for n in nrm]
def shrunk_bvh(S, d=0.05):
    nrm = vertex_normals(S.verts, S.tris)
    return BVHTree.FromPolygons([v - n * d for v, n in zip(S.verts, nrm)], S.tris, all_triangles=True, epsilon=0.0)

# kopie inside_depth/penetration/overlap z trzecie_oko.py (l. 1050–1158, bez crossing — tylko wnikanie wierzchołkowe)
PARITY_DIRS = [Vector((0.3117, 0.5273, 0.7903)).normalized(), Vector((-0.6131, 0.2927, -0.7338)).normalized()]
def inside_parity(part, p, d):
    o = Vector(p); n = 0; last = None
    for _ in range(64):
        loc, nrm, idx, dist = part.bvh.ray_cast(o, d)
        if loc is None: break
        if dist > 1e-4 and not (idx == last and dist < 2e-3): n += 1
        last = idx; o = loc + d * 1e-3
    return n % 2 == 1
def inside_depth(part, p):
    loc, nrm, idx, dist = part.bvh.find_nearest(Vector(p))
    if loc is None or dist <= 1e-4: return 0.0
    if (Vector(p) - loc).dot(nrm) >= 0: return 0.0
    if not (inside_parity(part, p, PARITY_DIRS[0]) or inside_parity(part, p, PARITY_DIRS[1])): return 0.0
    return dist
def penetration(A, B, pairs):
    ia = set(); ib = set()
    for (i, j) in pairs: ia.update(A.polys[i]); ib.update(B.polys[j])
    best = 0.0
    for vi in ia: best = max(best, inside_depth(B, A.verts[vi]))
    for vi in ib: best = max(best, inside_depth(A, B.verts[vi]))
    return best
def overlap(A, B):
    pairs = A.bvh.overlap(B.bvh)
    return (0, 0.0) if not pairs else (len(pairs), penetration(A, B, pairs))

# ================================================================== T1
P("T1 gap()/chord() bez znaku: A = x∈[0,10], B = x∈[9.8,20] (PRZENIKANIE 0,2 mm), p=(9.9,5,5) w strefie wspólnej")
A = box("A", 0, 10, 0, 10, 0, 10); B = box("B", 9.8, 20, 0, 10, 0, 10)
g = gap(A, B, (9.9, 5, 5), "X")
P("   gap(A,B,p,'X') =", None if g is None else round(g, 3), "→ luz zgłoszony jako DODATNI; przy planie 0,2 ± 0,05 fit() dałoby OK (zmierz = plan)")
B2 = box("B2", 10.2, 20, 0, 10, 0, 10)
P("   kontrola: ta sama para z realnym luzem 0,2 (B2 x∈[10.2,20]): gap(B2, A, (10.1,5,5), 'X') =", round(gap(B2, A, (10.1, 5, 5), "X"), 3), "→ nieodróżnialne od przenikania 0,2")
P("   chord(A, p wewnątrz, 'X') =", round(chord(A, (5, 5, 5), "X"), 3), "; chord(A, p NA ZEWNĄTRZ (12,5,5), 'X') =", chord(A, (12, 5, 5), "X"), "(None = brak trafienia w −X; ok)")

# ================================================================== T2
P("T2 probe(): sonda dokładnie na ścianie pudełka x∈[0,10] — punkt (10, 5, 5)")
S = box_solid(0, 10, 0, 10, 0, 10, "S")
e_w = S.probe((10.0, 5, 5), True); e_p = S.probe((10.0, 5, 5), False)
P("   oczek W   :", e_w["wynik"], "ok=", e_w["ok"], "r3=", e_w["r3"], "niestabilna=", e_w.get("niestabilna"), "d_sciana=", e_w["d_sciana"])
P("   oczek POZA:", e_p["wynik"], "ok=", e_p["ok"], "r3=", e_p["r3"], "niestabilna=", e_p.get("niestabilna"))
e3 = S.probe((10.05, 5, 5), True)
P("   punkt 0,05 POZA materiałem, oczek W:", e3["wynik"], "ok=", e3["ok"], "r3=", e3["r3"], "(jednomyślne → brak przesunięcia → poprawnie NIE)")
e4 = S.probe((5, 5, 5), True); P("   kontrola: środek pudełka oczek W:", e4["wynik"], e4["ok"])

# ================================================================== T3/T4/T6: realna tulejka i korpus_W z .blend
bpy.ops.wm.open_mainfile(filepath=BLEND)
def world(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); bmesh.ops.triangulate(bm, faces=bm.faces)
    vs = [v.co.copy() for v in bm.verts]; fs = [tuple(v.index for v in f.verts) for f in bm.faces]; bm.free(); return vs, fs
objs = {o.name: o for o in bpy.data.objects if o.type == "MESH"}
kv, kf = world(objs["korpus_W"]); K_S = Solid(kv, kf, "korpus_W"); K_P = Part("korpus_W", kv, [list(f) for f in kf]); bvhK = K_S.bvh
tv0, tf = world(objs["tulejka_dc"])
cy = (89.0, 30.0)   # oś tulejki (y, z) wg .blend
def r_of(v): return math.hypot(v.y - cy[0], v.z - cy[1])
def scaled_tulejka(d_outer):
    """tulejka z walcem przeskalowanym promieniowo do ø d_outer (tylko wierzchołki walca r≈5,925; otwór i kołnierz bez zmian)"""
    k = (d_outer / 2) / 5.925
    out = []
    for v in tv0:
        r = r_of(v)
        if abs(r - 5.925) < 0.02:
            out.append(Vector((v.x, cy[0] + (v.y - cy[0]) * k, cy[1] + (v.z - cy[1]) * k)))
        else:
            out.append(v.copy())
    return out

P("T3 sprawdz_C2_tulejka_blend l.32: luz = find_nearest(v)[3] dla wierzchołków walca (bez znaku)")
for d_out in (11.85, 12.00, 12.15, 12.30):
    tv = scaled_tulejka(d_out)
    cyl = [v for v in tv if abs(r_of(v) - d_out / 2) < 0.02]
    dK = [bvhK.find_nearest(v)[3] for v in cyl]
    P("   tulejka ø%.2f w otworze ø12 (luz geometryczny %+.3f/stronę): walec→korpus min %.4f max %.4f (n=%d)" % (d_out, (12 - d_out) / 2, min(dK), max(dK), len(cyl)))
P("   uwaga: w oryginale filtr `abs(r_of(v) - 5.925) < 0.02` (l.28) — dla ø12,15 lista `cyl` byłaby PUSTA → min() pada (ValueError), zamiast raportować wcisk")

P("T4 sprawdz_B K-53: skurcz 0,05 na wierzchołek + BVHTree.overlap; tulejka przeskalowana vs korpus_W (.blend)")
shrK = shrunk_bvh(K_S)
for d_out in (11.85, 12.00, 12.08, 12.10, 12.15, 12.20, 12.30):
    T_S = Solid(scaled_tulejka(d_out), kf and tf, "tulejka")
    n_shr = len(shrK.overlap(shrunk_bvh(T_S)))
    n_raw = len(bvhK.overlap(T_S.bvh))
    P("   ø%.2f (luz %+.3f/stronę): par po skurczu = %d  (bez skurczu = %d)  → K-53: %s" % (d_out, (12 - d_out) / 2, n_shr, n_raw, "ZAL" if n_shr == 0 else "NIE"))

P("T6 trzecie_oko.overlap(): tulejka ø11,85 (plik) vs korpus_W — pary i wnikanie wierzchołkowe (EPS_PEN 0,05)")
for d_out in (11.85, 12.00, 12.08, 12.15):
    T_P = Part("tulejka", scaled_tulejka(d_out), [list(f) for f in tf])
    n, pen = overlap(T_P, K_P)
    P("   ø%.2f: par trójkątów %d, wnikanie max %.4f → %s" % (d_out, n, pen, "styk/OK" if pen <= 0.05 else "PRZECIECIE"))

# ================================================================== T5
P("T5 trzecie_oko.overlap(): bryła całkowicie wewnątrz drugiej (pudełko 2×2×2 w pudełku 10×10×10)")
big = box("big", 0, 10, 0, 10, 0, 10); small = box("small", 4, 6, 4, 6, 4, 6)
n, pen = overlap(small, big)
P("   par trójkątów =", n, "wnikanie =", pen, "→ brak przecięć trójkątów = brak wykrycia (werdykt OK)")
sm_S = box_solid(4, 6, 4, 6, 4, 6, "small"); bg_S = box_solid(0, 10, 0, 10, 0, 10, "big")
P("   to samo w K-53 (sprawdz_B, po skurczu): par =", len(shrunk_bvh(bg_S).overlap(shrunk_bvh(sm_S))))
P("KONIEC")
