# -*- coding: utf-8 -*-
"""
Skrypt RECENZENTA — etap B (wkładka, rama dyfuzora, blat, korpus W/P, złożenie w .blend).
Napisany niezależnie, bez czytania ramka_generator.py.
Uruchomienie:
  "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b -P recenzja/sprawdz_B.py -- --iter 2
Wyniki: recenzja/wyniki_B_iter<n>.json, recenzja/relief_*.png, recenzja/log_B_iter<n>.txt (przez tee)
"""
import bpy, bmesh, json, math, os, sys, zlib, struct, hashlib
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

ROOT = r"<PC>\Desktop\Ramki"
WYN = os.path.join(ROOT, "wyniki_v2")
REC = os.path.join(ROOT, "recenzja")
ITER = 2
if "--" in sys.argv:
    a = sys.argv[sys.argv.index("--") + 1:]
    if "--iter" in a:
        ITER = int(a[a.index("--iter") + 1])

PAR = json.load(open(os.path.join(ROOT, "parametry.json"), encoding="utf-8"))
def P(sec, key):
    return PAR[sec][key]["value"]

RESULTS = []
def rec(kid, plik, wynik, wartosc, waga, sondy=None, uwaga=""):
    RESULTS.append({"id": kid, "plik": plik, "wynik": wynik, "wartosc": wartosc, "waga": waga,
                    "sondy": sondy or [], "uwaga": uwaga})
    print(f"[{wynik}] {kid} {plik}: {wartosc} {uwaga}")

# ---------- narzędzia (jak w sprawdz_A.py) ----------
def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def import_stl(path):
    clear_scene()
    bpy.ops.wm.stl_import(filepath=path)
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    assert len(objs) == 1
    return objs[0]

def weld(obj, dist=1e-5):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bm.to_mesh(obj.data); bm.free(); obj.data.update()

def bbox(verts):
    xs = [v.x for v in verts]; ys = [v.y for v in verts]; zs = [v.z for v in verts]
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))

class Solid:
    def __init__(self, verts, tris, name=""):
        self.name = name
        self.verts = verts; self.tris = tris
        self.bvh = BVHTree.FromPolygons(verts, tris, all_triangles=True, epsilon=0.0)
        self.bb = bbox(verts)
        self.dirs = [Vector((1.0, 0.00071, 0.00137)).normalized(),
                     Vector((0.00083, 1.0, 0.00119)).normalized(),
                     Vector((0.00097, 0.00061, 1.0)).normalized()]
        self.diag = (Vector((self.bb[1], self.bb[3], self.bb[5])) - Vector((self.bb[0], self.bb[2], self.bb[4]))).length + 10

    @classmethod
    def from_object(cls, obj, matrix, name=""):
        me = obj.data
        verts = [matrix @ v.co for v in me.vertices]
        me.calc_loop_triangles()
        tris = [tuple(t.vertices) for t in me.loop_triangles]
        return cls(verts, tris, name)

    def count_hits(self, p, d):
        n = 0; o = Vector(p); last = None
        for _ in range(500):
            hit = self.bvh.ray_cast(o, d, self.diag)
            if hit[0] is None:
                break
            loc = hit[0]
            if last is None or (loc - last).length > 1e-5:
                n += 1
            last = loc
            o = loc + d * 1e-4
        return n

    def inside3(self, p):
        return [self.count_hits(p, d) % 2 == 1 for d in self.dirs]

    def nearest(self, p):
        loc, nrm, idx, dist = self.bvh.find_nearest(Vector(p))
        return loc, nrm, dist

    def probe(self, p, expect_in, tag=""):
        p = Vector(p)
        r = self.inside3(p)
        loc, nrm, dist = self.nearest(p)
        e = {"p": [round(c, 3) for c in p], "oczek": "W" if expect_in else "POZA",
             "r3": ["W" if x else "P" for x in r], "d_sciana": round(dist, 3) if dist is not None else None}
        if tag:
            e["tag"] = tag
        if r.count(True) in (0, 3):
            e["wynik"] = "W" if r[0] else "POZA"
        else:
            if nrm is None or nrm.length == 0:
                nrm = Vector((0, 0, 1))
            p2 = p + (-nrm if expect_in else nrm) * 0.1
            r2 = self.inside3(p2)
            e["niestabilna"] = True; e["p_przes"] = [round(c, 3) for c in p2]; e["r3_przes"] = ["W" if x else "P" for x in r2]
            e["wynik"] = ("W" if r2[0] else "POZA") if r2.count(True) in (0, 3) else "NIESTABILNA"
        e["ok"] = (e["wynik"] == e["oczek"])
        return e

    def first_hit(self, origin, direction):
        hit = self.bvh.ray_cast(Vector(origin), Vector(direction).normalized(), self.diag)
        return None if hit[0] is None else hit[0]

    def top_z(self, x, y, down=True, zstart=None):
        if zstart is None:
            zstart = self.bb[5] + 5 if down else self.bb[4] - 5
        h = self.first_hit((x, y, zstart), (0, 0, -1 if down else 1))
        return None if h is None else h.z

    def heightmap(self, x0, x1, y0, y1, step=0.25):
        nx = int(round((x1 - x0) / step)) + 1; ny = int(round((y1 - y0) / step)) + 1
        return [[self.top_z(x0 + i * step, y1 - j * step) for i in range(nx)] for j in range(ny)]

    def depthmap_y(self, x0, x1, z0, z1, step=0.25, ystart=-110):
        """Mapa 'głębokości' promieniami wzdłuż +Y (dla reliefu na przedniej ściance): wartość = y pierwszego trafienia."""
        nx = int(round((x1 - x0) / step)) + 1; nz = int(round((z1 - z0) / step)) + 1
        out = []
        for j in range(nz):
            z = z1 - j * step; row = []
            for i in range(nx):
                h = self.first_hit((x0 + i * step, ystart, z), (0, 1, 0))
                row.append(None if h is None else h.y)
            out.append(row)
        return out

def write_png(path, hm, vmin, vmax, k=1, invert=False):
    rows = []
    for row in hm:
        r = []
        for z in row:
            r.extend([z] * k)
        for _ in range(k):
            rows.append(r)
    h = len(rows); w = len(rows[0])
    raw = bytearray()
    for row in rows:
        raw.append(0)
        for z in row:
            if z is None:
                raw.append(0)
            else:
                t = (z - vmin) / (vmax - vmin) if vmax > vmin else 0
                if invert:
                    t = 1 - t
                raw.append(max(0, min(255, int(40 + 215 * t))))
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0)) \
          + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    open(path, "wb").write(png)

def manifold_check(obj):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bad = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    loose = sum(1 for v in bm.verts if len(v.link_edges) == 0)
    bm.free()
    return bad, loose

def self_overlap(solid):
    pairs = solid.bvh.overlap(solid.bvh)
    n = 0
    for a, b in pairs:
        if a == b or set(solid.tris[a]) & set(solid.tris[b]):
            continue
        n += 1
    return n // 2

def components(obj):
    me = obj.data; n = len(me.vertices); parent = list(range(n))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for e in me.edges:
        ra, rb = find(e.vertices[0]), find(e.vertices[1])
        if ra != rb:
            parent[ra] = rb
    return len({find(i) for i in range(n)})

def volume(solid):
    v = 0.0; V = solid.verts
    for a, b, c in solid.tris:
        v += V[a].dot(V[b].cross(V[c]))
    return v / 6.0 / 1000.0

def probes_result(kid, plik, lst, waga, uwaga=""):
    nbad = sum(1 for e in lst if not e["ok"])
    bad = [f"{e['p']}→{e['wynik']}≠{e['oczek']}" for e in lst if not e["ok"]][:6]
    rec(kid, plik, "ZAL" if nbad == 0 else "NIE", f"{len(lst) - nbad}/{len(lst)} sond zgodnych" + (f"; niezgodne: {bad}" if bad else ""), waga, lst, uwaga)
    return nbad == 0

def general_checks(name, obj, solid, exp_bb, exp_vol):
    ntri = len(solid.tris)
    nan = any(math.isnan(v.x) or math.isnan(v.y) or math.isnan(v.z) for v in solid.verts)
    rec("K-01", name, "ZAL" if (ntri > 100 and not nan) else "NIE", f"trójkątów {ntri}, NaN {nan}", "B")
    bb = solid.bb; dims = (bb[1] - bb[0], bb[3] - bb[2], bb[5] - bb[4])
    ok = all(abs(dims[i] - exp_bb[i]) <= 0.1 for i in range(3))
    rec("K-02", name, "ZAL" if ok else "NIE",
        f"gabaryt {dims[0]:.3f} × {dims[1]:.3f} × {dims[2]:.3f} (oczek. {exp_bb[0]} × {exp_bb[1]} × {exp_bb[2]}); bbox montażowy "
        f"X[{bb[0]:.3f},{bb[1]:.3f}] Y[{bb[2]:.3f},{bb[3]:.3f}] Z[{bb[4]:.3f},{bb[5]:.3f}]", "B")
    be, lv = manifold_check(obj); so = self_overlap(solid)
    rec("K-03", name, "ZAL" if (be == 0 and lv == 0 and so == 0) else "NIE", f"krawędzie niemanifold {be}, luźne wierzchołki {lv}, samoprzecięcia {so}", "B")
    nc = components(obj)
    rec("K-04", name, "ZAL" if nc == 1 else "NIE", f"składowych {nc}", "B")
    vol = volume(solid)
    rec("K-04b", name, "ZAL" if (vol > 0 and abs(vol - exp_vol) <= 0.3 * exp_vol) else "NIE", f"objętość {vol:.3f} cm³ (oczek. {exp_vol} ± 30 %)", "B")
    return vol, dims

# ================= WKŁADKA =================
def check_wkladka(name, S):
    lst = [S.probe((48.1, 0, 3), False), S.probe((48.5, 0, 3), True), S.probe((52.5, 0, 3), False),
           S.probe((48.5, 0, 5.9), False), S.probe((49.5, 0, 5.9), True), S.probe((0, 0, 3), False)]
    # dodatkowo pozostałe boki
    for (x, y) in ((-48.1, 0), (0, 48.1)):
        lst.append(S.probe((x, y, 3), False))
    for (x, y) in ((-48.5, 0), (0, 48.5)):
        lst.append(S.probe((x, y, 3), True))
    probes_result("K-23", name, lst, "B")
    lst = [S.probe((-38, -38, 1.5), True), S.probe((-38, -38, 3), False), S.probe((38, 38, 1.5), True), S.probe((-38, 38, 1.5), True),
           S.probe((38, -38, 1.5), True), S.probe((-30, -30, 1.5), False), S.probe((-35.5, -35.5, 1.5), False)]
    probes_result("K-24", name, lst, "B")
    lst = [S.probe((-42, -42, 1.5), False), S.probe((-42, 42, 1.5), False), S.probe((42, 42, 1.5), False), S.probe((42, -42, 1.5), True),
           S.probe((-45, -45, 0.5), False), S.probe((-45, -45, 1.8), True), S.probe((-50, -50, 0.7), False), S.probe((-50, -50, 2.2), True)]
    # analogicznie B i C (kanały po przekątnych)
    for (sx, sy) in ((-1, 1), (1, 1)):
        lst += [S.probe((sx * 45, sy * 45, 0.5), False), S.probe((sx * 45, sy * 45, 1.8), True), S.probe((sx * 50, sy * 50, 0.7), False), S.probe((sx * 50, sy * 50, 2.2), True)]
    probes_result("K-25", name, lst, "B")
    lst = [S.probe((45.6, -45.6, 5), True), S.probe((45.6, -45.6, 8), False), S.probe((45.6, -45.6, 7.2), True), S.probe((48.05, -45.6, 5), False)]
    probes_result("K-27", name, lst, "B")
    lst = [S.probe((0, -50.3, 3), False), S.probe((0, -50.3, 0.3), False), S.probe((20, -50.3, 3), True), S.probe((-20, -50.3, 3), True)]
    probes_result("K-28", name, lst, "B")
    lst = []
    for sx in (1, -1):
        lst += [S.probe((sx * 58, 80, 1.5), True), S.probe((sx * 58, 80, 4), False),
                S.probe((sx * 47, 55, 1.5), True), S.probe((sx * 47, 55, 3.5), False), S.probe((sx * 62, 55, 1.5), True), S.probe((sx * 62, 50, 1.5), False),
                S.probe((sx * 47, 59, 1.5), False), S.probe((sx * 56, 55, 0.5), False), S.probe((sx * 56, 55, 2), True), S.probe((sx * 48, 50.5, 0.5), False),
                S.probe((sx * 58, 93.5, -2), True), S.probe((sx * 58, 93.5, -3.8), False), S.probe((sx * 58, 86, 1.5), False), S.probe((sx * 58, 89, 1.5), True),
                S.probe((sx * 64, 70, 0.5), False), S.probe((sx * 64, 70, 2), True), S.probe((sx * 64, 89, 0.5), False),
                S.probe((sx * 58, 95.5, 1.5), True), S.probe((sx * 58, 96.5, 1.5), False)]
    probes_result("K-29", name, lst, "B")
    lst = [S.probe((51.5, 0, 0.7), False), S.probe((51.5, 0, 2.5), True), S.probe((-51.5, 0, 0.7), False), S.probe((0, 51.5, 0.7), False), S.probe((20, -51.5, 0.7), True)]
    probes_result("K-30", name, lst, "P")
    # K-31: strzałki
    hm = S.heightmap(-40, 40, -52.3, -48.3, 0.1)
    def region_max(x0, x1, y0, y1):
        vals = []
        for j, row in enumerate(hm):
            y = -48.3 - j * 0.1
            if y0 - 1e-6 <= y <= y1 + 1e-6:
                for i, z in enumerate(row):
                    x = -40 + i * 0.1
                    if x0 - 1e-6 <= x <= x1 + 1e-6 and z is not None:
                        vals.append(z)
        return max(vals) if vals else None
    m1 = region_max(-34, -30, -52.3, -50.0); m2 = region_max(30, 34, -52.3, -50.0); m3 = region_max(-40, 40, -50.0, -48.3)
    # pas pod kołnierzem pokrywki: wyłączyć fazę (y > -49.3 daje < 6)
    ok = all(m is not None for m in (m1, m2, m3)) and abs(m1 - 6.6) <= 0.05 and abs(m2 - 6.6) <= 0.05 and abs(m3 - 6.0) <= 0.05
    write_png(os.path.join(REC, f"relief_{name}_strzalki.png"), hm, 5.5, 6.7, 3)
    rec("K-31", name, "ZAL" if ok else "NIE", f"max Z lewa strzałka {m1}, prawa {m2} (oczek. 6,6 ± 0,05); pas y −50,0…−48,3 max {m3} (oczek. 6,0); PNG relief_{name}_strzalki.png", "P")
    # K-32: otwór z promieni
    w = {}
    for nm, o, d in (("X", (0, 0, 3), Vector((1, 0, 0))), ("Y", (20, 0, 3), Vector((0, 1, 0)))):
        h1 = S.first_hit(o, d); h2 = S.first_hit(o, -d)
        w[nm] = (h1 - h2).length if h1 and h2 else None
    ok = all(v is not None and abs(v - 96.6) <= 0.2 for v in w.values())
    rec("K-32", name, "ZAL" if ok else "NIE", f"otwór z promieni X {w['X']:.3f}, Y {w['Y']:.3f} (oczek. 96,6 ± 0,2); część złożeniowa → K-53", "B")

# ================= RAMA =================
def check_rama(name, S):
    lst = [S.probe((82, 0, 7), True), S.probe((79, 0, 7), False), S.probe((86, 0, 7), False), S.probe((82, 0, 3), False),
           S.probe((90, 90, 2), False), S.probe((92.5, 90, 2), True), S.probe((92.5, 90, 4.5), False), S.probe((83, 83, 2), True),
           S.probe((83, 83, 7), True), S.probe((93, 93, 2), False), S.probe((82, 92, 2), True), S.probe((0, 0, 7), False),
           S.probe((82, 0, 10.1), False), S.probe((82, 0, 2), False)]
    for (sx, sy) in ((-1, 1), (-1, -1), (1, -1)):
        lst += [S.probe((sx * 90, sy * 90, 2), False), S.probe((sx * 92.5, sy * 90, 2), True), S.probe((sx * 83, sy * 83, 2), True), S.probe((sx * 83, sy * 83, 7), True)]
    probes_result("K-48", name, lst, "B")
    w = {}
    for nm, d in (("X", Vector((1, 0, 0))), ("Y", Vector((0, 1, 0)))):
        h1 = S.first_hit((0, 0, 7), d); h2 = S.first_hit((0, 0, 7), -d)
        w[nm] = (h1 - h2).length if h1 and h2 else None
    return w

# ================= BLAT =================
def check_blat(name, S, do_rec=True):
    lst = [S.probe((80.5, 0, -1), False), S.probe((80.5, 0, -3), True), S.probe((81.5, 0, -1), True), S.probe((0, 0, -3), False),
           S.probe((78, 0, -3), False), S.probe((80.9, 80.9, -1), True)]
    ok45 = probes_result("K-45", name, lst, "B") if do_rec else all(e["ok"] for e in lst)
    lst = [S.probe((96.0, 0, -9), True), S.probe((94, 0, -9), False), S.probe((97.8, 20, -9), False), S.probe((97.8, 0, -9.75), True),
           S.probe((97.8, 20, -9.75), False), S.probe((97.8, 0, -12.5), False), S.probe((0, -97.8, -9.75), False), S.probe((50, -97.8, -9.75), True),
           S.probe((-50, 97.8, -9.75), True), S.probe((50, 97.8, -9.75), False), S.probe((-97.8, 0, -9.75), True),
           S.probe((96.0, 4.5, -9), False), S.probe((96.0, 7, -9), True), S.probe((96.0, 4.5, -4.5), True)]
    ok46 = probes_result("K-46", name, lst, "B") if do_rec else all(e["ok"] for e in lst)
    lst = []
    for sx in (1, -1):
        lst += [S.probe((sx * 75, 93, -8.6), False), S.probe((sx * 75, 89.6, -8.6), True), S.probe((sx * 75, 88, -8.6), False),
                S.probe((sx * 75, 93, -6), True), S.probe((sx * 75, 93, -12), True), S.probe((sx * 78, 92, -8.6), True), S.probe((sx * 70, 96.0, -9), True),
                S.probe((sx * 58, 93.5, -2), False), S.probe((sx * 58, 93.5, -4.2), False), S.probe((sx * 58, 86, -1), False), S.probe((sx * 58, 86, -3), True),
                S.probe((sx * 66, 90, -2), False), S.probe((sx * 66, 90, -3.95), False), S.probe((sx * 66, 90, -4.3), False)]
    for (sx, sy) in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        lst += [S.probe((sx * 90, sy * 90, -6), False), S.probe((sx * 92.5, sy * 90, -6), True), S.probe((sx * 92.5, sy * 90, -10.5), False)]
    lst.append(S.probe((84, 0, -7), False))
    # grubość dna otworu kołka promieniem
    extra = []
    for sx in (1, -1):
        zt = S.top_z(sx * 58, 93.5, down=True); zb = S.top_z(sx * 58, 93.5, down=False)
        extra.append((zt, zb))
    floor_ok = all(zt is not None and zb is not None and abs(zt + 3.8) <= 0.05 and abs(zb + 4.0) <= 0.05 for zt, zb in extra)
    ok47 = all(e["ok"] for e in lst) and floor_ok
    if do_rec:
        rec("K-47", name, "ZAL" if ok47 else "NIE", f"{sum(1 for e in lst if e['ok'])}/{len(lst)} sond zgodnych; dno otworów kołków (z góry, z dołu): {[(round(a, 3), round(b, 3)) for a, b in extra]} (oczek. −3,8 / −4,0)", "B", lst)
    return ok45 and ok46 and ok47, ok47

# ================= KORPUS =================
def check_korpus(name, S):
    lst = [S.probe((0, 0, 1.5), True), S.probe((0, 0, 10), False), S.probe((98.75, 0, 20), True), S.probe((96, 0, 20), False), S.probe((0, 98.75, 20), True),
           S.probe((99, 99, 20), False), S.probe((0, 0, 54.5), False), S.probe((98.75, 0, 54.4), True), S.probe((98.75, 0, 54.7), False)]
    probes_result("K-34", name, lst, "B")
    lst = [S.probe((60, 60, 1.5), False), S.probe((-60, 60, 1.5), False), S.probe((62.5, 60, 0.5), False), S.probe((62.5, 60, 2.5), True),
           S.probe((-91, 0, 1.5), False), S.probe((-91, 7.5, 1.5), False), S.probe((-91, 9, 1.5), True), S.probe((-60, 10, 1.5), False), S.probe((-60, 13, 1.5), True),
           S.probe((60, -60, 1.5), False), S.probe((-60, -60, 1.5), False), S.probe((-60, -10, 1.5), False)]
    probes_result("K-35", name, lst, "B")
    lst = [S.probe((62, 60, 3.5), True), S.probe((62, 60, 4.5), False), S.probe((62, -60, 3.5), True), S.probe((-85.5, -24.5, 6), True), S.probe((-88.5, -24.5, 6), False),
           S.probe((-88.5, -24.5, 8.5), False), S.probe((-27.5, 24.5, 6), True), S.probe((23, 75, 6), True), S.probe((20, 75, 6), False), S.probe((-17, 75, 6), True),
           S.probe((-88.5, 24.5, 6), False), S.probe((-30.5, -24.5, 6), False), S.probe((-30.5, 24.5, 6), False), S.probe((-20, 75, 6), False)]
    probes_result("K-36", name, lst, "B")
    lst = [S.probe((-63, 98.75, 8), False), S.probe((-63, 98.75, 6.2), True), S.probe((-63, 98.75, 9.8), True), S.probe((-63, 101, 9.6), True), S.probe((-63, 101, 7.4), False),
           S.probe((-54, 98.75, 8), True), S.probe((98.75, -45, 8), False), S.probe((-98.75, 45, 8), False), S.probe((101, 45, 9.6), True), S.probe((0, -98.75, 8), True)]
    for x in (-45, -27, -9, 9, 27, 45, 63):
        lst.append(S.probe((x, 98.75, 8), False))
    for y in (-27, -9, 9, 27, 45):
        lst.append(S.probe((98.75, y, 8), False))
    for y in (-45, -27, -9, 9, 27):
        lst.append(S.probe((-98.75, y, 8), False))
    probes_result("K-37", name, lst, "B")
    lst = [S.probe((-60, 90, 26), False), S.probe((-60, 99, 15), False), S.probe((-60, 99, 13), True), S.probe((-43, 99, 26), False), S.probe((-40.5, 99, 26), True),
           S.probe((-60, 79, 30), False), S.probe((-60, 79, 37.5), True), S.probe((-79, 85, 26), True), S.probe((-81, 85, 26), False),
           S.probe((-60, 85, 13), True), S.probe((-60, 85, 10), False), S.probe((-60, 85, 39), True), S.probe((-60, 85, 41), False),
           S.probe((-77, 99, 26), False), S.probe((-79.5, 99, 26), True), S.probe((-60, 99, 37), False), S.probe((-60, 99, 39), True)]
    probes_result("K-38", name, lst, "B")
    lst = [S.probe((60, 98.75, 24), False), S.probe((60, 98.75, 29), True), S.probe((49, 98.75, 24), False), S.probe((71, 98.75, 24), False),
           S.probe((75, 98.75, 50), False), S.probe((-75, 98.75, 50), False), S.probe((75, 98.75, 47), True), S.probe((60, 98.75, 19), True),
           S.probe((53.5, 98.75, 24), False), S.probe((66.5, 98.75, 24), False), S.probe((51.5, 98.75, 24), True)]
    probes_result("K-39", name, lst, "B")
    # K-40
    lst = [S.probe((30, -98.75, 22), True), S.probe((-70, -98.75, 38), True), S.probe((-82, -98.75, 38), True), S.probe((-58, -98.75, 38), True),
           S.probe((0, -98.75, 20), True), S.probe((60, -98.75, 30), True), S.probe((-60, -98.75, 30), True)]
    bad = []; nray = 0; yvals = []
    for xi in range(-95, 96, 5):
        for zi in range(5, 53, 5):
            h = S.first_hit((xi, -110, zi), (0, 1, 0)); nray += 1
            if h is None or not (-100.6 - 0.01 <= h.y <= -100.0 + 0.01):
                bad.append((xi, zi, None if h is None else round(h.y, 3)))
            else:
                yvals.append(h.y)
    ok = all(e["ok"] for e in lst) and not bad
    rec("K-40", name, "ZAL" if ok else "NIE", f"{sum(e['ok'] for e in lst)}/{len(lst)} sond; siatka {nray} promieni: trafienia y ∈ [{min(yvals):.3f}, {max(yvals):.3f}], poza zakresem: {bad[:8]}", "B", lst)
    lst = [S.probe((98.0, 0, 48.8), False), S.probe((98.0, 4.5, 48.8), False), S.probe((98.0, 6, 48.8), True), S.probe((98.0, 0, 47), True), S.probe((98.0, 0, 50.6), True),
           S.probe((98.9, 0, 48.8), True), S.probe((-98.0, 0, 48.8), False), S.probe((50, -98.0, 48.8), False), S.probe((0, -98.0, 48.8), True),
           S.probe((-50, 98.0, 48.8), False), S.probe((50, 98.0, 48.8), True)]
    probes_result("K-42", name, lst, "B")
    # K-43: mapa głębokości przedniej ścianki
    dm = S.depthmap_y(-60, 60, 38, 54, 0.2)
    def region_min(x0, x1, z0, z1):
        vals = []
        for j, row in enumerate(dm):
            z = 54 - j * 0.2
            if z0 - 1e-6 <= z <= z1 + 1e-6:
                for i, y in enumerate(row):
                    x = -60 + i * 0.2
                    if x0 - 1e-6 <= x <= x1 + 1e-6 and y is not None:
                        vals.append(y)
        return min(vals) if vals else None
    miny_label = region_min(-45, 45, 41, 51)
    dm2 = S.depthmap_y(-45, 45, 30, 36, 1.0)
    vals2 = [y for row in dm2 for y in row if y is not None]
    miny_blank = min(vals2) if vals2 else None
    write_png(os.path.join(REC, f"relief_{name}_napis.png"), dm, -100.65, -99.95, 2, invert=True)
    ok = miny_label is not None and abs(miny_label + 100.6) <= 0.05 and miny_blank is not None and abs(miny_blank + 100.0) <= 0.05
    rec("K-43", name, "ZAL" if ok else "NIE", f"min Y w x[−45,45] Z[41,51]: {miny_label:.3f} (oczek. −100,6); w Z[30,36]: {miny_blank:.3f} (oczek. −100,0); PNG relief_{name}_napis.png (treść do odczytu)", "B")
    # K-44
    lst = [S.probe((75, 75, 6), True), S.probe((75, 75, 10), False), S.probe((72, 78, 6), False), S.probe((88, 88, 0.2), False), S.probe((88, 88, 0.8), True), S.probe((99.9, 0, 0.3), False),
           S.probe((66, 66, 6), True), S.probe((-75, -75, 6), True), S.probe((-88, -88, 0.2), False), S.probe((88, -88, 0.2), False), S.probe((-88, 88, 0.2), False)]
    probes_result("K-44", name, lst, "P")
    # wnętrze korpusu z promieni (do K-49)
    w = {}
    for nm, d in (("X", Vector((1, 0, 0))), ("Y", Vector((0, 1, 0)))):
        h1 = S.first_hit((0, 0, 20), d); h2 = S.first_hit((0, 0, 20), -d)
        w[nm] = (h1 - h2).length if h1 and h2 else None
    return w

# ================= .blend =================
def vertex_normals(verts, tris):
    nrm = [Vector((0, 0, 0)) for _ in verts]
    for a, b, c in tris:
        n = (verts[b] - verts[a]).cross(verts[c] - verts[a])
        nrm[a] += n; nrm[b] += n; nrm[c] += n
    return [n.normalized() if n.length > 0 else Vector((0, 0, 1)) for n in nrm]

def shrunk_bvh(S, d=0.05):
    nrm = vertex_normals(S.verts, S.tris)
    verts = [v - n * d for v, n in zip(S.verts, nrm)]
    return BVHTree.FromPolygons(verts, S.tris, all_triangles=True, epsilon=0.0)

def check_blend(blend_path):
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    sol = {}
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        S = Solid.from_object(o, o.matrix_world, o.name)
        sol[o.name] = S
    cols = {c.name: [o.name for o in c.objects] for c in bpy.data.collections}
    # zestaw złożony = obiekty, których bbox mieści się w |x|,|y| ≤ 150
    assembled = [n for n, S in sol.items() if max(abs(S.bb[0]), abs(S.bb[1]), abs(S.bb[2]), abs(S.bb[3])) <= 150]
    offset = [n for n in sol if n not in assembled]
    mind_off = min((min(abs(sol[n].bb[0]), abs(sol[n].bb[1]), abs(sol[n].bb[2]), abs(sol[n].bb[3])) for n in offset), default=None)
    rec("INFO-blend", "ramka_v2.blend", "ZAL", f"kolekcje {cols}; zestaw złożony ({len(assembled)}): {sorted(assembled)}; odsunięte ({len(offset)}): {sorted(offset)}; najmniejsza |współrzędna| odsuniętych {mind_off}", "-")
    # K-53
    shr = {n: shrunk_bvh(sol[n]) for n in assembled}
    pairs = []; bad = []
    names = sorted(assembled)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            # szybki test bbox
            A, B = sol[a].bb, sol[b].bb
            if A[1] < B[0] or B[1] < A[0] or A[3] < B[2] or B[3] < A[2] or A[5] < B[4] or B[5] < A[4]:
                continue
            n = len(shr[a].overlap(shr[b]))
            pairs.append((a, b, n))
            if n:
                bad.append((a, b, n))
    rec("K-53", "ramka_v2.blend", "ZAL" if not bad else "NIE", f"par z nakładającym się bbox: {len(pairs)}; par z przecięciem: {len(bad)}: {bad}", "B",
        [{"para": f"{a}–{b}", "przeciec": n, "ok": n == 0} for a, b, n in pairs])
    # K-54
    def topz(n, x, y):
        return sol[n].top_z(x, y) if n in sol else None
    vals = {"blat (90,0)": (topz("blat", 90, 0), 58.6), "dyfuzor (0,70)": (topz("proxy_dyfuzor", 0, 70), 58.6), "wkladka (0,50.3)": (topz("wkladka", 0, 50.3), 64.6),
            "wkladka max Z": (sol["wkladka"].bb[5], 66.1), "plytka n1 (0,-46.5)": (topz("plytka_wieczorna_n1", 0, -46.5), 69.1),
            "plytka n1 relief (39.5,-44.5)": (topz("plytka_wieczorna_n1", 39.5, -44.5), 69.7), "pokrywka (40,40)": (topz("pokrywka", 40, 40), 85.1),
            "pokrywka max Z": (sol["pokrywka"].bb[5], 85.7), "pokrywka min Z": (sol["pokrywka"].bb[4], 65.1), "proxy_pi_bonnet max Z": (sol["proxy_pi_bonnet"].bb[5], 34.0),
            "proxy_panel min Z": (sol["proxy_panel"].bb[4], 37.0), "proxy_panel max Z (PCB)": (sol["proxy_panel"].bb[5], 50.6),
            "proxy_panel PCB spód (wierzchołek z=49 obecny)": (49.0 if any(abs(v.z - 49.0) < 1e-3 for v in sol["proxy_panel"].verts) else None, 49.0),
            "stopki min Z": (min(sol[n].bb[4] for n in sol if n.startswith("proxy_stopka")), -4.0), "stopki max Z": (max(sol[n].bb[5] for n in sol if n.startswith("proxy_stopka")), 0.0),
            "blat max Z": (sol["blat"].bb[5], 58.6), "blat min Z": (sol["blat"].bb[4], 44.6), "korpus_W max Z": (sol["korpus_W"].bb[5], 54.6), "korpus_W min Z": (sol["korpus_W"].bb[4], 0.0),
            "rama max Z": (sol["rama_dyfuzora"].bb[5], 54.6), "rama min Z": (sol["rama_dyfuzora"].bb[4], 44.6), "wkladka min Z (kołki)": (sol["wkladka"].bb[4], 55.1),
            "plytka n1 min Z": (sol["plytka_wieczorna_n1"].bb[4], 61.1)}
    bad = {k: (round(v, 3) if v is not None else None, e) for k, (v, e) in vals.items() if v is None or abs(v - e) > 0.05}
    rec("K-54", "ramka_v2.blend", "ZAL" if not bad else "NIE", "; ".join(f"{k} {round(v, 3) if v is not None else None}/{e}" for k, (v, e) in vals.items()) + (f"; NIEZGODNE: {bad}" if bad else ""), "B")
    # K-33
    wk = sol["wkladka"]
    zmin_ex_pins = min(v.z for v in wk.verts if v.z > 56.0)
    dyf_top = sol["proxy_dyfuzor"].bb[5]
    pin_in = [sol["blat"].probe((sx * 58, 93.5, 57.0), False) for sx in (1, -1)] + [wk.probe((sx * 58, 93.5, 56.5), True) for sx in (1, -1)]
    ok = abs(zmin_ex_pins - 58.6) <= 0.02 and abs(dyf_top - 58.6) <= 0.02 and all(e["ok"] for e in pin_in)
    rec("K-33", "ramka_v2.blend", "ZAL" if ok else "NIE", f"min Z wkładki poza kołkami {zmin_ex_pins:.3f} (58,6 ± 0,02); wierzch dyfuzora {dyf_top:.3f}; kołki w otworach blatu: {sum(e['ok'] for e in pin_in)}/4; przecięcia wkładka–blat/–dyfuzor: patrz K-53", "B", pin_in)
    # K-44b
    k = sol["korpus_W"]; pi = sol["proxy_pi_bonnet"]; wt = sol["proxy_wtyk_bonnet"]; pn = sol["proxy_panel"]
    n1 = len(shr["korpus_W"].overlap(shr["proxy_pi_bonnet"])); n2 = len(shr["korpus_W"].overlap(shr["proxy_wtyk_bonnet"]))
    n3 = len(shr["proxy_panel"].overlap(shr["proxy_pi_bonnet"])); n4 = len(shr["proxy_panel"].overlap(shr["proxy_wtyk_bonnet"]))
    luz = pn.bb[4] - max(pi.bb[5], wt.bb[5])
    rec("K-44b", "ramka_v2.blend", "ZAL" if (n1 == n2 == n3 == n4 == 0 and luz >= 3 - 1e-6) else "NIE",
        f"przecięcia korpus–Pi {n1}, korpus–wtyk {n2}, panel–Pi {n3}, panel–wtyk {n4}; luz Z {luz:.3f} (≥ 3); Pi bbox X[{pi.bb[0]:.1f},{pi.bb[1]:.1f}] Y[{pi.bb[2]:.1f},{pi.bb[3]:.1f}] Z[{pi.bb[4]:.1f},{pi.bb[5]:.1f}]; wtyk X[{wt.bb[0]:.1f},{wt.bb[1]:.1f}] Y[{wt.bb[2]:.1f},{wt.bb[3]:.1f}] Z[{wt.bb[4]:.1f},{wt.bb[5]:.1f}]", "B")
    # K-55
    mg = sol["proxy_magnes_A"]; hl = sol["proxy_hall_A"]
    gap = mg.bb[4] - hl.bb[5]
    rec("K-55", "ramka_v2.blend", "ZAL" if abs(gap - 1.2) <= 0.05 else "NIE", f"spód magnesu A {mg.bb[4]:.3f} − wierzch Halla A {hl.bb[5]:.3f} = {gap:.3f} (1,2 ± 0,05); +0,5 = {gap + 0.5:.2f} ≤ 4", "B")
    # K-56
    yf = wk.first_hit((30, -100, 62), (0, 1, 0)); xr = wk.first_hit((100, 0, 62), (-1, 0, 0))
    front = -yf.y if yf else None; right = xr.x if xr else None
    strip_f = 80 - front if front else None; strip_r = 80 - right if right else None
    viol = []
    for n in assembled:
        if n in ("proxy_dyfuzor", "proxy_panel"):
            continue
        S = sol[n]
        if S.bb[5] <= 58.65:
            continue
        for xi in range(-79, 80, 2):
            for yi in range(-79, -52, 2):
                if yi > -52.3 - 0.1:
                    continue
                z = S.top_z(xi, yi)
                if z is not None and z > 58.65:
                    viol.append((n, "przód", xi, yi, round(z, 2))); break
        for xi in range(53, 80, 2):
            for yi in range(-79, 52, 2):  # prawy pas w zasięgu Y ramy (−52,3…52,3); tylne narożniki y > 52,3 = strefa uszu (D12)
                z = S.top_z(xi, yi)
                if z is not None and z > 58.65:
                    viol.append((n, "prawy", xi, yi, round(z, 2))); break
    px = math.floor(min(strip_f, strip_r) / 2.5 + 1e-6) if strip_f and strip_r else None
    ok = strip_f is not None and abs(strip_f - 27.7) <= 0.1 and abs(strip_r - 27.7) <= 0.1 and px == 11 and not viol
    rec("K-56", "ramka_v2.blend", "ZAL" if ok else "NIE", f"krawędź wkładki przód y={-front if front else None}, prawa x={right}; pas przedni {strip_f}, prawy {strip_r} (27,7); pikseli {px} (11); obiekty nad pasami: {viol[:6]}", "B")
    # K-49 złożeniowe
    rama = sol["rama_dyfuzora"]; blat = sol["blat"]
    tabs_top = max(v.z for v in rama.verts if v.z < 50)
    boss_bot = min(v.z for v in blat.verts if math.hypot(abs(v.x) - 90, abs(v.y) - 90) <= 4.1)
    n_rb = len(shr["rama_dyfuzora"].overlap(shr["blat"])); n_rp = len(shr["rama_dyfuzora"].overlap(shr["proxy_panel"])); n_bk = len(shr["blat"].overlap(shr["korpus_W"]))
    return {"tabs_top": tabs_top, "boss_bot": boss_bot, "n_rb": n_rb, "n_rp": n_rp, "n_bk": n_bk,
            "panel_w": sol["proxy_panel"].bb[1] - sol["proxy_panel"].bb[0], "dyf_w": sol["proxy_dyfuzor"].bb[1] - sol["proxy_dyfuzor"].bb[0]}

# ================= main =================
def main():
    summary = {}
    files = ["ramka_wkladka_v2", "ramka_rama_dyfuzora_v2", "ramka_blat_v2", "ramka_korpus_W_v2", "ramka_korpus_P_v2"]
    exp = {"ramka_wkladka_v2": ((130, 148.3, 11.0), 16), "ramka_rama_dyfuzora_v2": ((188, 188, 10), 20), "ramka_blat_v2": ((200, 200, 14), 85),
           "ramka_korpus_W_v2": ((204, 202.6, 54.6), 215), "ramka_korpus_P_v2": ((204, 202.6, 54.6), 215)}
    meas = {}
    for name in files:
        path = os.path.join(WYN, "stl", name + ".stl")
        if not os.path.exists(path):
            rec("K-01", name, "NIE", "brak pliku", "B"); continue
        obj = import_stl(path); weld(obj)
        raw = bbox([v.co for v in obj.data.vertices])
        cx = (raw[0] + raw[1]) / 2; cy = (raw[2] + raw[3]) / 2
        if name == "ramka_wkladka_v2":
            M = Matrix.Translation(Vector((-cx, -(raw[2] + 52.3), -(raw[4] + 3.5))))
        elif name == "ramka_rama_dyfuzora_v2":
            M = Matrix.Translation(Vector((-cx, -cy, -raw[4])))
        elif name == "ramka_blat_v2":
            M = Matrix.Rotation(math.pi, 4, "X") @ Matrix.Translation(Vector((-cx, -cy, -raw[4])))
        else:
            zs0 = [v.co for v in obj.data.vertices if v.co.z < raw[4] + 0.01]
            b0 = bbox(zs0); cy0 = (b0[2] + b0[3]) / 2
            M = Matrix.Translation(Vector((-cx, -cy0, -raw[4])))
        S = Solid.from_object(obj, M, name)
        print(f"=== {name}: bbox surowy X[{raw[0]:.3f},{raw[1]:.3f}] Y[{raw[2]:.3f},{raw[3]:.3f}] Z[{raw[4]:.3f},{raw[5]:.3f}]")
        vol, dims = general_checks(name, obj, S, exp[name][0], exp[name][1])
        summary[name] = {"bbox_surowy": [round(v, 3) for v in raw], "objetosc_cm3": round(vol, 4), "gabaryt": [round(v, 3) for v in dims],
                         "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest()}
        if name == "ramka_wkladka_v2":
            check_wkladka(name, S)
        elif name == "ramka_rama_dyfuzora_v2":
            meas["rama"] = check_rama(name, S)
        elif name == "ramka_blat_v2":
            ok_all, ok47 = check_blat(name, S)
            if not ok47:
                S2 = Solid.from_object(obj, Matrix.Rotation(math.pi, 4, "Z") @ M, name + "_Rz180")
                ok2, ok47b = check_blat(name + "_Rz180", S2, do_rec=False)
                rec("K-02", name, "NIE" if ok47b else "ZAL", f"test rozpoznawczy osi eksportu: K-47 po dodatkowym obrocie Rz180: {'ZAL → zła oś eksportu (część nieodbita)' if ok47b else 'NIE → błąd geometrii, nie orientacji'}", "B")
            w = {}
            # szerokość ZEWNĘTRZNA kołnierza: promienie z zewnątrz (y/x = 20, poza haczykami i nacięciami), Z −9
            for nm, o1, d in (("X", (-150, 20, -9), Vector((1, 0, 0))), ("Y", (20, -150, -9), Vector((0, 1, 0)))):
                o2 = (150, 20, -9) if nm == "X" else (20, 150, -9)
                h1 = S.first_hit(o1, d); h2 = S.first_hit(o2, -d)
                w[nm] = (h1 - h2).length if h1 and h2 else None
            meas["blat_kolnierz"] = w
            wp = {}
            for nm, d in (("X", Vector((1, 0, 0))), ("Y", Vector((0, 1, 0)))):
                h1 = S.first_hit((0, 0, -1), d); h2 = S.first_hit((0, 0, -1), -d)
                wp[nm] = (h1 - h2).length if h1 and h2 else None
            meas["blat_kieszen"] = wp
        else:
            meas[name] = check_korpus(name, S)
    # K-43 różnice W/P
    shaW = summary.get("ramka_korpus_W_v2", {}).get("sha256"); shaP = summary.get("ramka_korpus_P_v2", {}).get("sha256")
    vW = summary.get("ramka_korpus_W_v2", {}).get("objetosc_cm3"); vP = summary.get("ramka_korpus_P_v2", {}).get("objetosc_cm3")
    if shaW and shaP:
        dv = vW - vP
        rec("K-43", "korpus W vs P", "ZAL" if (shaW != shaP and dv != 0 and abs(dv) < 0.5) else "NIE", f"SHA różne: {shaW != shaP}; objętość W − P = {dv:.4f} cm³ (≠ 0, < 0,5)", "B")
    # .blend
    bl = os.path.join(WYN, "ramka_v2.blend")
    if os.path.exists(bl):
        summary["ramka_v2.blend"] = {"sha256": hashlib.sha256(open(bl, "rb").read()).hexdigest()}
        m = check_blend(bl)
        kW = meas.get("ramka_korpus_W_v2", {}); bk = meas.get("blat_kolnierz", {}); bp = meas.get("blat_kieszen", {}); rm = meas.get("rama", {})
        luz_bk = [(kW.get(a) - bk.get(a)) / 2 if kW.get(a) and bk.get(a) else None for a in ("X", "Y")]
        luz_rp = (rm.get("X") - m["panel_w"]) / 2 if rm.get("X") else None
        luz_dk = (bp.get("X") - m["dyf_w"]) / 2 if bp.get("X") else None
        ok = all(l is not None and abs(l - 0.5) <= 0.1 for l in luz_bk) and luz_rp is not None and abs(luz_rp - 0.5) <= 0.1 and luz_dk is not None and abs(luz_dk - 1.0) <= 0.1 \
             and abs(m["tabs_top"] - 48.6) <= 0.05 and abs(m["boss_bot"] - 48.6) <= 0.05 and m["n_rb"] == 0 and m["n_rp"] == 0 and m["n_bk"] == 0
        rec("K-49", "blat/korpus/rama", "ZAL" if ok else "NIE",
            f"wnętrze korpusu X {kW.get('X'):.3f} Y {kW.get('Y'):.3f}; kołnierz blatu X {bk.get('X'):.3f} Y {bk.get('Y'):.3f} → luz/stronę {[round(l, 3) for l in luz_bk]} (0,5); "
            f"rama wewn. {rm.get('X'):.3f} vs panel {m['panel_w']:.3f} → {luz_rp:.3f} (0,5); kieszeń {bp.get('X'):.3f} vs dyfuzor {m['dyf_w']:.3f} → {luz_dk:.3f} (1,0); "
            f"wierzch łap ramy {m['tabs_top']:.3f} = spód bossów blatu {m['boss_bot']:.3f} (48,6); przecięcia rama–blat {m['n_rb']}, rama–panel {m['n_rp']}, blat–korpus {m['n_bk']}", "B")
    out = {"etap": "B", "iteracja": ITER, "blender": bpy.app.version_string, "pliki": summary, "wyniki": RESULTS}
    json.dump(out, open(os.path.join(REC, f"wyniki_B_iter{ITER}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    nie = [r for r in RESULTS if r["wynik"] == "NIE"]
    print(f"\n=== PODSUMOWANIE: {len(RESULTS)} sprawdzeń, NIE: {len(nie)}")
    for r in nie:
        print("  NIE", r["id"], r["plik"], r["wartosc"][:200])

main()
