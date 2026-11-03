# -*- coding: utf-8 -*-
"""
Skrypt RECENZENTA — R57 (płytki OKRĄGŁE ø100 do testu skanera: bazowe + n8 / n9).
Pochodna recenzja/sprawdz_R54.py (te same narzędzia: import STL, BVH, sondy parzystości przecięć w 3 kierunkach).
Zakres: K-01…K-04b, K-05 (a–h) + K-05x, K-06, K-07, K-08 (koniec zaokrąglony: sonda 45° z protokołu + łuk końca z siatki),
K-09 (+ kontrola odwrotna dawnych rogów i dawnych dołków oraz dołków DRUGIEGO typu), K-11 (4 bity z JSON), K-13 (cyfra w kole),
K-16 (okrąg + ścięcie), K-61 a–f, K-62, K-63, K-06x (mapa wierzchu w kole z obrysami z JSON), ścianki do krawędzi Z SIATKI
(sondy promieniowe przez końce obrysów), objętość/bbox vs raport, SHA-256 (4 STL + 2 JSON + 15 plików R56).
Napisany bez czytania ramka_generator.py.
Uruchomienie:
  "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b -P recenzja/sprawdz_R57.py -- --iter 1
Wyniki: recenzja/wyniki_R57_iter<n>.json, recenzja/relief_R57_<plik>.png, recenzja/wierzch_R57_<plik>.png
"""
import bpy, bmesh, json, math, os, sys, zlib, struct, re, hashlib
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

ROOT = r"<PC>\Desktop\Ramki"
WYN = os.path.join(ROOT, "wyniki_v2")
REC = os.path.join(ROOT, "recenzja")
ITER = "1"
if "--" in sys.argv:
    a = sys.argv[sys.argv.index("--") + 1:]
    if "--iter" in a:
        ITER = a[a.index("--iter") + 1]

PAR = json.load(open(os.path.join(ROOT, "parametry.json"), encoding="utf-8"))
def P(sec, key):
    return PAR[sec][key]["value"]

# ---------- parametry oczekiwane (parametry.json / plan v2 4.1a / protokół §3a) ----------
PT = P("plytka", "plate_thickness")               # 8
SOCK_DEPTH = P("plytka", "socket_depth")          # 4
ANG = math.radians(P("plytka", "socket_wall_angle"))  # 15°
TAN = math.tan(ANG)
HOLE_D = P("plytka", "socket_hole_d")             # 3
DIMPLE_D = P("plytka", "code_dimple_d")           # 2
DIMPLE_DEPTH = P("plytka", "code_dimple_depth")   # 1
MARK_D = P("plytka", "marker_cone_d")             # 5
MARK_DEPTH = P("plytka", "marker_cone_depth")     # 3
REL_H = P("plytka", "number_relief_h")            # 0.6
TEXT_H = P("plytka", "number_text_h")             # 5
ZONE_R = P("plytka", "socket_zone_r")             # 47
WALL_MIN = P("plytka", "socket_wall_min")         # 3
CHAMF = P("plytka", "plate_top_chamfer")          # 0.5
RD = P("plytka", "plate_round_d")                 # 100
R = RD / 2                                        # 50
FLAT_W = P("plytka", "round_flat_w")              # 16
FLAT_DMIN = P("plytka", "round_flat_depth_min")   # 0.6
FLAT_ANG = math.radians(P("plytka", "round_flat_angle"))  # −45°
FLAT_DIST = math.sqrt(R * R - (FLAT_W / 2) ** 2)  # 49.3559
FLAT_DEPTH = R - FLAT_DIST                        # 0.644
FLAT_N = Vector((math.cos(FLAT_ANG), math.sin(FLAT_ANG)))  # normalna ścięcia (od środka na zewnątrz)
FLAT_HALF_ANG = math.degrees(math.asin((FLAT_W / 2) / R))  # 9.21°
DIMPLES_R = P("plytka", "code_dimples_round")
NUMPOS_R = P("plytka", "number_pos_round")
NUMS_R = P("plytka", "plate_numbers_round")
MARKER_POS = {"wieczorna": P("plytka", "ev_marker_pos"), "poranna": P("plytka", "mo_marker_pos")}
ROWS = {"wieczorna": P("plytka", "ev_rows"), "poranna": P("plytka", "mo_rows")}
OLD_DIMPLE_X = P("plytka", "code_dimple_x"); OLD_DIMPLE_Y0 = P("plytka", "code_dimple_y0"); OLD_DIMPLE_P = P("plytka", "code_dimple_pitch")
OLD_BIT_D = P("plytka", "code_bit_d_pos")
OLD_MC = P("plytka", "plate_size") / 2 - P("plytka", "marker_offset")  # 42 — dawne rogi (kieszenie / stożki)
NUM_BITS = {8: "D", 9: "AD"}   # n = A + 2B + 4C + 8D
BITS_ALL = "ABCD"

FILES = {
    "ramka_plytka_okragla_wieczorna_v2": ("wieczorna", 0),
    "ramka_plytka_okragla_wieczorna_n8_v2": ("wieczorna", 8),
    "ramka_plytka_okragla_poranna_v2": ("poranna", 0),
    "ramka_plytka_okragla_poranna_n9_v2": ("poranna", 9),
}
VOL_EXP = {"wieczorna": 49.0, "poranna": 51.0}  # tabela 1 protokołu (± 30 %)
# deklaracje wykonawcy (raport R57 iter2, sekcja 2 / 7.1) — porównanie po pomiarze
DECL = {
    "ramka_plytka_okragla_wieczorna_v2": ("3ca8178262f7f1f253480ca1d49adbbccf2db3648647814ec2390311e5553ace", 48.99, (100.0, 100.0, 8.0)),
    "ramka_plytka_okragla_wieczorna_n8_v2": ("c4c8a18d0b83fd2a2903f5d782188a8de4827ee07c55dca9df7bd0d8e4a37d32", 49.01, (100.0, 100.0, 8.6)),
    "ramka_plytka_okragla_poranna_v2": ("713aef6c0cef1dc2fc3b3809ce3756557b41b0cc4268c85166e985f18f74e0dd", 50.55, (100.0, 100.0, 8.0)),
    "ramka_plytka_okragla_poranna_n9_v2": ("a87bc6c5f8f0323bc202e5ebfeab6be6d7c8432beba6aafe4a8372d70666e2be", 50.56, (100.0, 100.0, 8.6)),
}
DECL_JSON = {
    "uklad_gniazd_okragla_wieczorna.json": "260f807c630211dcd3c1b552cded03838d1367156c856fc51f3a3f7ec12f0743",
    "uklad_gniazd_okragla_poranna.json": "5adcc977dd9b456e5261d1e2225bc386def23a165d79de124b5733fb9ef43d53",
}

RESULTS = []
def rec(kid, plik, wynik, wartosc, waga, sondy=None, uwaga=""):
    RESULTS.append({"id": kid, "plik": plik, "wynik": wynik, "wartosc": wartosc, "waga": waga,
                    "sondy": sondy or [], "uwaga": uwaga})
    print(f"[{wynik}] {kid} {plik}: {wartosc} {uwaga}")

# ---------- narzędzia (jak R54) ----------
def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def import_stl(path):
    clear_scene()
    bpy.ops.wm.stl_import(filepath=path)
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    assert len(objs) == 1, f"import dał {len(objs)} obiektów"
    return objs[0]

def weld(obj, dist=1e-5):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bm.to_mesh(obj.data); bm.free(); obj.data.update()

def bbox(verts):
    xs = [v.x for v in verts]; ys = [v.y for v in verts]; zs = [v.z for v in verts]
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))

class Solid:
    def __init__(self, obj, matrix):
        self.obj = obj
        me = obj.data
        self.verts = [matrix @ v.co for v in me.vertices]
        me.calc_loop_triangles()
        self.tris = [tuple(t.vertices) for t in me.loop_triangles]
        self.bvh = BVHTree.FromPolygons(self.verts, self.tris, all_triangles=True, epsilon=0.0)
        self.bb = bbox(self.verts)
        self.dirs = [Vector((1.0, 0.00071, 0.00137)).normalized(),
                     Vector((0.00083, 1.0, 0.00119)).normalized(),
                     Vector((0.00097, 0.00061, 1.0)).normalized()]
        self.diag = (Vector((self.bb[1], self.bb[3], self.bb[5])) - Vector((self.bb[0], self.bb[2], self.bb[4]))).length + 10

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
        entry = {"p": [round(c, 3) for c in p], "oczek": "W" if expect_in else "POZA",
                 "r3": ["W" if x else "P" for x in r], "d_sciana": round(dist, 3)}
        if tag:
            entry["tag"] = tag
        if r.count(True) in (0, 3):
            entry["wynik"] = "W" if r[0] else "POZA"
        else:
            if nrm is None or nrm.length == 0:
                nrm = Vector((0, 0, 1))
            p2 = p + (-nrm if expect_in else nrm) * 0.1
            r2 = self.inside3(p2)
            entry["niestabilna"] = True
            entry["p_przes"] = [round(c, 3) for c in p2]
            entry["r3_przes"] = ["W" if x else "P" for x in r2]
            entry["wynik"] = ("W" if r2[0] else "POZA") if r2.count(True) in (0, 3) else "NIESTABILNA"
        entry["ok"] = (entry["wynik"] == entry["oczek"])
        return entry

    def top_z(self, x, y, zstart=None, down=True):
        if zstart is None:
            zstart = self.bb[5] + 5 if down else self.bb[4] - 5
        d = Vector((0, 0, -1 if down else 1))
        hit = self.bvh.ray_cast(Vector((x, y, zstart)), d, self.diag)
        return None if hit[0] is None else hit[0].z

    def heightmap(self, x0, x1, y0, y1, step=0.25):
        nx = int(round((x1 - x0) / step)) + 1; ny = int(round((y1 - y0) / step)) + 1
        hm = []
        for j in range(ny):
            y = y1 - j * step
            hm.append([self.top_z(x0 + i * step, y) for i in range(nx)])
        return hm

    def chord(self, p, axis, half=60.0):
        d = Vector(axis).normalized()
        h1 = self.bvh.ray_cast(Vector(p), d, half); h2 = self.bvh.ray_cast(Vector(p), -d, half)
        return None if (h1[0] is None or h2[0] is None) else (h1[0] - h2[0]).length

    def radial_hit(self, ang_deg, z, start_r=None, offset=0.0):
        """Promień z zewnątrz (start_r od osi, przesunięty prostopadle o offset) do osi; zwraca odległość trafienia od osi
        mierzoną wzdłuż kierunku (rzut na kierunek), None gdy brak."""
        if start_r is None:
            start_r = R + 5
        a = math.radians(ang_deg)
        u = Vector((math.cos(a), math.sin(a), 0.0)); v = Vector((-math.sin(a), math.cos(a), 0.0))
        o = u * start_r + v * offset + Vector((0, 0, z))
        hit = self.bvh.ray_cast(o, -u, start_r + 5)
        if hit[0] is None:
            return None
        return hit[0].dot(u)

    def hits_along(self, o, d, maxd):
        """Wszystkie trafienia wzdłuż promienia (odległości od o)."""
        out = []; o = Vector(o); d = Vector(d).normalized(); last = None; acc = 0.0
        for _ in range(200):
            hit = self.bvh.ray_cast(o, d, maxd - acc)
            if hit[0] is None:
                break
            seg = (hit[0] - o).length
            if last is None or seg > 1e-5:
                out.append(acc + seg)
            acc += seg + 1e-4; o = hit[0] + d * 1e-4; last = hit[0]
            if acc >= maxd:
                break
        return out

def write_png(path, hm, zmin, zmax, k=1):
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
                t = (z - zmin) / (zmax - zmin) if zmax > zmin else 0
                raw.append(max(0, min(255, int(40 + 215 * t))))
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0)) \
          + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    open(path, "wb").write(png)

def write_png_rgb(path, img):
    h = len(img); w = len(img[0])
    raw = bytearray()
    for row in img:
        raw.append(0)
        for (r, g, b) in row:
            raw += bytes((r, g, b))
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) \
          + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    open(path, "wb").write(png)

def manifold_check(obj):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bad_edges = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    loose = sum(1 for v in bm.verts if len(v.link_edges) == 0)
    degen = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    # spójność orientacji: każda krawędź ma 2 ściany o przeciwnych kierunkach obiegu
    flipped = 0
    for e in bm.edges:
        if len(e.link_faces) == 2:
            f1, f2 = e.link_faces
            def dirn(f, e):
                vs = [l.vert for l in f.loops]
                i = vs.index(e.verts[0]); j = vs.index(e.verts[1])
                return (j - i) % len(vs) == 1
            if dirn(f1, e) == dirn(f2, e):
                flipped += 1
    bm.free()
    return bad_edges, loose, degen, flipped

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
    return v / 6.0 / 1000.0  # cm³

def probes_result(kid, plik, lst, waga, uwaga=""):
    nbad = sum(1 for e in lst if not e["ok"])
    bad = [f"{e.get('tag', '')}{e['p']}→{e['wynik']}≠{e['oczek']}" for e in lst if not e["ok"]][:8]
    rec(kid, plik, "ZAL" if nbad == 0 else "NIE", f"{len(lst) - nbad}/{len(lst)} sond zgodnych" + (f"; niezgodne: {bad}" if bad else ""), waga, lst, uwaga)
    return nbad == 0

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

# ---------- K-01…K-04b ----------
def general_checks(name, obj, solid, exp_bb, exp_vol):
    ntri = len(solid.tris)
    nan = any(math.isnan(v.x) or math.isnan(v.y) or math.isnan(v.z) for v in solid.verts)
    rec("K-01", name, "ZAL" if (ntri > 100 and not nan) else "NIE", f"trójkątów {ntri}, NaN {nan}", "B")
    bb = solid.bb
    dims = (bb[1] - bb[0], bb[3] - bb[2], bb[5] - bb[4])
    ok = all(abs(dims[i] - exp_bb[i]) <= 0.1 for i in range(3))
    rec("K-02", name, "ZAL" if ok else "NIE",
        f"gabaryt {dims[0]:.3f} × {dims[1]:.3f} × {dims[2]:.3f} (oczek. {exp_bb[0]} × {exp_bb[1]} × {exp_bb[2]}); "
        f"bbox montażowy X[{bb[0]:.3f},{bb[1]:.3f}] Y[{bb[2]:.3f},{bb[3]:.3f}] Z[{bb[4]:.3f},{bb[5]:.3f}]", "B")
    be, lv, dg, fl = manifold_check(obj)
    so = self_overlap(solid)
    rec("K-03", name, "ZAL" if (be == 0 and lv == 0 and so == 0 and dg == 0 and fl == 0) else "NIE",
        f"krawędzie niemanifold {be}, luźne wierzchołki {lv}, samoprzecięcia {so}, zdegenerowane trójkąty (pole < 1e-9) {dg}, krawędzie o niespójnej orientacji ścian {fl}", "B")
    nc = components(obj)
    rec("K-04", name, "ZAL" if nc == 1 else "NIE", f"składowych {nc}", "B")
    vol = volume(solid)
    ok = vol > 0 and abs(vol - exp_vol) <= 0.3 * exp_vol
    rec("K-04b", name, "ZAL" if ok else "NIE", f"objętość {vol:.3f} cm³ (> 0 → normalne na zewnątrz; oczek. {exp_vol} ± 30 %)", "B")
    return vol, dims

# ---------- geometria obrysów ----------
def outline_seg(s):
    if s["type"] == "round":
        c = Vector((s["x"], s["y"])); return c, c, s["d_top"] / 2
    half = (s["l"] - s["w"]) / 2
    return Vector((s["x"] - half, s["y"])), Vector((s["x"] + half, s["y"])), s["w"] / 2

def pt_seg(p, q0, q1):
    d = q1 - q0
    if d.length < 1e-9:
        return (p - q0).length
    t = max(0.0, min(1.0, (p - q0).dot(d) / d.length_squared))
    return (p - (q0 + d * t)).length

def dist_outlines(s1, s2):
    a0, a1, ra = outline_seg(s1); b0, b1, rb = outline_seg(s2)
    cands = [pt_seg(a0, b0, b1), pt_seg(a1, b0, b1), pt_seg(b0, a0, a1), pt_seg(b1, a0, a1)]
    return min(cands) - ra - rb

def dist_point_outline(sock, px, py):
    a0, a1, r = outline_seg(sock)
    return pt_seg(Vector((px, py)), a0, a1) - r

def edge_dist(px, py, r=0.0):
    """Odległość obrysu (środek, promień r) do krawędzi płytki: min(ściana pionowa okręgu, płaszczyzna ścięcia)."""
    d_circ = R - math.hypot(px, py) - r
    d_flat = FLAT_DIST - (px * FLAT_N.x + py * FLAT_N.y) - r
    return min(d_circ, d_flat), d_circ, d_flat

def outline_edge_dist(sock):
    a0, a1, r = outline_seg(sock)
    return min(edge_dist(e.x, e.y, r)[0] for e in (a0, a1))

def outline_flat_dist(sock):
    a0, a1, r = outline_seg(sock)
    return min(edge_dist(e.x, e.y, r)[2] for e in (a0, a1))

def outline_max_radius(sock):
    a0, a1, r = outline_seg(sock)
    return max(math.hypot(e.x, e.y) for e in (a0, a1)) + r

# ---------- K-05 (a–h) + K-05x ----------
def check_json(plate, data, name, square):
    s = data["sockets"]
    rounds = [x for x in s if x["type"] == "round"]; troughs = [x for x in s if x["type"] == "trough"]
    rows_par = ROWS[plate]
    exp_round = sum(len(r["x"]) for r in rows_par if r["type"] == "round")
    exp_trough = sum(len(r["x"]) for r in rows_par if r["type"] == "trough")
    notes = []
    ok_a = (len(rounds), len(troughs)) == (exp_round, exp_trough)
    notes.append(f"(a) round/trough {len(rounds)}/{len(troughs)} (oczek. z {'ev' if plate == 'wieczorna' else 'mo'}_rows {exp_round}/{exp_trough})")
    rows = {}
    for x in s:
        rows.setdefault(round(x["y"], 2), []).append(x)
    ok_b = True
    for y, lst in rows.items():
        xs = sorted(v["x"] for v in lst)
        if any(abs(xs[i] + xs[-1 - i]) > 0.01 for i in range(len(xs))):
            ok_b = False; notes.append(f"(b) rząd y={y} niesymetryczny: {xs}")
    notes.append(f"(b) {len(rows)} rzędów symetrycznych: {ok_b}")
    ok_c = True; max_r = 0; max_r_id = None
    for x in s:
        rr = outline_max_radius(x)
        if rr > max_r:
            max_r = rr; max_r_id = x["id"]
        if rr > ZONE_R + 1e-6:
            ok_c = False; notes.append(f"(c) id {x['id']} poza kołem r {ZONE_R}: {rr:.3f}")
    notes.append(f"(c) max promień obrysu górnego {max_r:.3f} (id {max_r_id}) ≤ {ZONE_R}")
    mind = 1e9; pair = None; pairs3 = []
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            d = dist_outlines(s[i], s[j])
            if d < mind:
                mind = d; pair = (s[i]["id"], s[j]["id"])
            if d < WALL_MIN + 0.02:
                pairs3.append((s[i]["id"], s[j]["id"], round(d, 3)))
    ok_e = mind >= WALL_MIN - 0.005
    notes.append(f"(e) min ścianka między obrysami {mind:.3f} (para {pair}); par ze ścianką ≤ 3,02: {len(pairs3)}")
    ok_f = True
    for x in rounds:
        exp_db = x["d_top"] - 2 * SOCK_DEPTH * TAN
        if abs(x["d_bottom"] - exp_db) > 0.01:
            ok_f = False; notes.append(f"(f) id {x['id']} d_bottom {x['d_bottom']} oczek. {exp_db:.3f}")
    notes.append(f"(f) d_bottom = d_top − {2 * SOCK_DEPTH * TAN:.3f}: {ok_f}")
    ids = [x["id"] for x in s]
    ok_g = ids == list(range(1, len(s) + 1))
    order = sorted(s, key=lambda v: (round(v["y"], 2), -v["x"]))
    if [v["id"] for v in order] != ids:
        ok_g = False; notes.append("(g) kolejność id ≠ rzędami od przodu, malejące x")
    notes.append(f"(g) id 1…{len(s)} ciągłe: {ok_g}")
    # (h) sockets identyczne z JSON kwadratu tego typu (wszystkie pola)
    ok_h = (s == square["sockets"])
    diffs = []
    if not ok_h:
        for a_, b_ in zip(s, square["sockets"]):
            if a_ != b_:
                diffs.append((a_.get("id"), {k: (a_.get(k), b_.get(k)) for k in set(a_) | set(b_) if a_.get(k) != b_.get(k)}))
    notes.append(f"(h) sockets identyczne z JSON kwadratu ({len(s)} vs {len(square['sockets'])}): {ok_h}" + (f" różnice {diffs[:5]}" if diffs else ""))
    ok_mk = (data["markers"] == square["markers"])
    notes.append(f"(h) markers identyczne z kwadratem: {ok_mk}")
    ok = ok_a and ok_b and ok_c and ok_e and ok_f and ok_g and ok_h and ok_mk
    rec("K-05", name, "ZAL" if ok else "NIE", "; ".join(notes), "B", uwaga=f"max_promien={max_r:.3f}; min_scianka={mind:.3f}")
    # K-05x: JSON == rzędy z parametry.json + markers = *_marker_pos + code_dimples = code_dimples_round + number_relief = number_pos_round + flat + brak kieszeni/notch
    exp_set = set(); got_set = set()
    for r in rows_par:
        for xx in r["x"]:
            if r["type"] == "round":
                exp_set.add(("round", round(xx, 3), round(r["y"], 3), round(r["d"], 3), None))
            else:
                exp_set.add(("trough", round(xx, 3), round(r["y"], 3), round(r["l"], 3), round(r["w"], 3)))
    for x in s:
        if x["type"] == "round":
            got_set.add(("round", round(x["x"], 3), round(x["y"], 3), round(x["d_top"], 3), None))
        else:
            got_set.add(("trough", round(x["x"], 3), round(x["y"], 3), round(x["l"], 3), round(x["w"], 3)))
    xs = []
    mk = {m["corner"]: (m["x"], m["y"], m["d"], m["depth"]) for m in data["markers"]}
    mk_exp = {k: (v[0], v[1], MARK_D, MARK_DEPTH) for k, v in MARKER_POS[plate].items()}
    if mk != mk_exp:
        xs.append(f"markers {mk} ≠ parametry {mk_exp}")
    cd = {m["bit"]: (m["x"], m["y"], m["d"], m["depth"]) for m in data["code_dimples"]}
    cd_exp = {b: (v[0], v[1], DIMPLE_D, DIMPLE_DEPTH) for b, v in DIMPLES_R[plate].items()}
    if cd != cd_exp:
        xs.append(f"code_dimples {cd} ≠ code_dimples_round {cd_exp}")
    if [m["bit"] for m in data["code_dimples"]] != list(BITS_ALL):
        xs.append("kolejność bitów ≠ A,B,C,D")
    nr = data.get("number_relief")
    nr_exp = NUMPOS_R[plate]
    if nr is None or (nr["x"], nr["y"], nr["text_h"], nr["relief_h"]) != (nr_exp[0], nr_exp[1], TEXT_H, REL_H):
        xs.append(f"number_relief {nr} ≠ number_pos_round {nr_exp} / {TEXT_H} / {REL_H}")
    fl = data.get("flat") or {}
    if (fl.get("angle_deg"), fl.get("chord_w")) != (math.degrees(FLAT_ANG), FLAT_W) or abs(fl.get("dist", 0) - FLAT_DIST) > 0.001:
        xs.append(f"flat {fl} ≠ ({math.degrees(FLAT_ANG)}, {FLAT_W}, {FLAT_DIST:.4f})")
    if data.get("shape") != "round" or data.get("d") != RD or data.get("size") != RD or data.get("thickness") != PT:
        xs.append(f"shape/d/size/thickness {data.get('shape')}/{data.get('d')}/{data.get('size')}/{data.get('thickness')}")
    if data.get("magnet_pockets") != [] or data.get("notch") is not None:
        xs.append(f"magnet_pockets {data.get('magnet_pockets')} / notch {data.get('notch')} — mają być puste")
    holes = [(t["hole_count"], t["hole_pitch"]) for t in troughs]
    pitch_exp = P("plytka", "ev_trough_hole_pitch") if plate == "wieczorna" else P("plytka", "mo_trough_hole_pitch")
    if any(h != (4, pitch_exp) for h in holes):
        xs.append(f"rynienki otwory {holes} ≠ (4, {pitch_exp})")
    okx = (exp_set == got_set) and not xs
    rec("K-05x", name, "ZAL" if okx else "NIE",
        f"gniazda JSON == {'ev' if plate == 'wieczorna' else 'mo'}_rows: {exp_set == got_set} (brak {sorted(exp_set - got_set)}, nadmiar {sorted(got_set - exp_set)}); "
        f"markers = *_marker_pos, code_dimples = code_dimples_round (A,B,C,D), number_relief = number_pos_round, flat (−45°, 16, {FLAT_DIST:.4f}), shape round ø{RD} × {PT}, bez kieszeni/notch, otwory rynienek: "
        + ("zgodne" if not xs else "; ".join(xs)), "B", uwaga="sprawdzenie recenzenta (poza protokołem)")
    return ok

# ---------- K-16 / K-62 / K-61f z JSON ----------
def check_k16_k62_k61f(plate, data, name):
    s = data["sockets"]
    notes = []; ok = True; vals = {}
    markers = {m["corner"]: (m["x"], m["y"], m["d"] / 2) for m in data["markers"]}
    dimples = {m["bit"]: (m["x"], m["y"], m["d"] / 2) for m in data["code_dimples"]}
    # gniazdo/rynienka – krawędź (ściana pionowa) ≥ 1,5 i do początku fazy (R − 0,5) ≥ 1,5
    mind = 1e9; who = None; mind_ch = 1e9
    for sock in s:
        d = outline_edge_dist(sock)
        if d < mind:
            mind = d; who = sock["id"]
        mind_ch = min(mind_ch, d - CHAMF if d == R - outline_max_radius(sock) else d)  # faza tylko na okręgu; przy ścięciu brak fazy? (sprawdzane w STL)
    d_ch = R - CHAMF - max(outline_max_radius(x) for x in s)
    notes.append(f"gniazdo/rynienka–krawędź (ściana pionowa okręgu lub ścięcie) min {mind:.2f} (id {who}) ≥ 1,5; do początku fazy (R − 0,5) min {d_ch:.2f} ≥ 1,5")
    ok &= mind >= 1.5 and d_ch >= 1.5
    vals["gniazdo_krawedz"] = round(mind, 3); vals["gniazdo_krawedz_id"] = who; vals["gniazdo_poczatek_fazy"] = round(d_ch, 3)
    # znaczniki
    for c, (mx, my, mr) in markers.items():
        rad = math.hypot(mx, my)
        dmin = 1e9; wid = None
        for sock in s:
            d = dist_point_outline(sock, mx, my) - mr
            if d < dmin:
                dmin = d; wid = sock["id"]
        ddim = min(math.hypot(mx - dx, my - dy) - mr - dr for (dx, dy, dr) in dimples.values())
        de, dcirc, dflat = edge_dist(mx, my, mr)
        ok_m = rad <= ZONE_R - mr + 1e-6 and dmin >= WALL_MIN - 0.005 and ddim >= 1.5 and de >= 1.5
        ok &= ok_m
        notes.append(f"znacznik {c} ({mx}, {my}): promień {rad:.2f} ≤ {ZONE_R - mr}; gniazdo min {dmin:.2f} (id {wid}) ≥ 3; dołek {ddim:.2f} ≥ 1,5; krawędź {de:.2f} (okrąg {dcirc:.2f}, ścięcie {dflat:.2f}) ≥ 1,5 → {'ok' if ok_m else 'NIE'}")
        vals[f"znacznik_{c}"] = {"promien": round(rad, 3), "gniazdo": round(dmin, 3), "gniazdo_id": wid, "dolek": round(ddim, 3), "krawedz": round(de, 3)}
    # K-62: dołki: promień ≤ 44; do gniazd ≥ 3; do stożków ≥ 1,5; do krawędzi ≥ 1,5
    ok62 = True; n62 = []; v62 = {}
    for b, (dx, dy, dr) in dimples.items():
        rad = math.hypot(dx, dy)
        dmin = 1e9; wid = None
        for sock in s:
            d = dist_point_outline(sock, dx, dy) - dr
            if d < dmin:
                dmin = d; wid = sock["id"]
        dmk = min(math.hypot(dx - mx, dy - my) - dr - mr for (mx, my, mr) in markers.values())
        de, dcirc, dflat = edge_dist(dx, dy, dr)
        okb = rad <= ZONE_R - WALL_MIN + 1e-6 and dmin >= WALL_MIN - 0.005 and dmk >= 1.5 and de >= 1.5
        ok62 &= okb
        n62.append(f"{b} ({dx}, {dy}): promień {rad:.2f} ≤ {ZONE_R - WALL_MIN}; gniazdo {dmin:.2f} (id {wid}) ≥ 3; stożek {dmk:.2f} ≥ 1,5; krawędź {de:.2f} (okrąg {dcirc:.2f}, ścięcie {dflat:.2f}) ≥ 1,5 → {'ok' if okb else 'NIE'}")
        v62[b] = {"promien": round(rad, 3), "gniazdo": round(dmin, 3), "gniazdo_id": wid, "stozek": round(dmk, 3), "krawedz": round(de, 3)}
    rec("K-62", name, "ZAL" if ok62 else "NIE", "; ".join(n62), "B", uwaga=json.dumps(v62, ensure_ascii=False))
    # K-61f: ścianka od płaszczyzny ścięcia do obrysów (gniazda/rynienki oba końce, dołki, stożki) ≥ 3
    cands = []
    for sock in s:
        cands.append((outline_flat_dist(sock), f"gniazdo id {sock['id']}"))
    for b, (dx, dy, dr) in dimples.items():
        cands.append((edge_dist(dx, dy, dr)[2], f"dołek {b}"))
    for c, (mx, my, mr) in markers.items():
        cands.append((edge_dist(mx, my, mr)[2], f"stożek {c}"))
    nr = data.get("number_relief")
    d_num = None
    if nr:
        d_num = FLAT_DIST - (nr["x"] * FLAT_N.x + nr["y"] * FLAT_N.y)   # do środka cyfry (obrys z siatki w K-13)
    fmin, fwho = min(cands)
    rec("K-61f", name, "ZAL" if fmin >= WALL_MIN - 0.005 else "NIE",
        f"ścianka płaszczyzna ścięcia → obrysy min {fmin:.2f} ({fwho}) ≥ 3; środek cyfry → ścięcie {d_num and round(d_num, 2)} (obrys cyfry z siatki: K-13)", "B",
        uwaga=json.dumps({"min": round(fmin, 3), "kto": fwho, "top5": [(round(d, 2), w) for d, w in sorted(cands)[:5]]}, ensure_ascii=False))
    vals["sciecie_obrysy_min"] = round(fmin, 3); vals["sciecie_obrysy_kto"] = fwho
    rec("K-16", name, "ZAL" if ok else "NIE", "; ".join(notes), "B", uwaga=json.dumps(vals, ensure_ascii=False))
    return vals

# ---------- mapa wierzchu (K-06x) w kole ----------
def expected_top(plate, data, n, x, y, bits):
    rho = math.hypot(x, y)
    proj = x * FLAT_N.x + y * FLAT_N.y
    if rho > R + 0.3 or proj > FLAT_DIST + 0.3:
        return "none"
    if rho > R - CHAMF - 0.3 or proj > FLAT_DIST - 0.3:
        return "skip"
    nr = data.get("number_relief")
    if n != 0 and nr and abs(x - nr["x"]) <= 4.0 and abs(y - nr["y"]) <= 4.0:
        return "skip"
    for m in data["code_dimples"]:
        d = math.hypot(x - m["x"], y - m["y"])
        if d <= m["d"] / 2 + 0.3:
            if m["bit"] in bits:
                return "cavity" if d <= m["d"] / 2 - 0.3 else "skip"
            return "top" if d > m["d"] / 2 + 0.3 else "skip"
    for m in data["markers"]:
        d = math.hypot(x - m["x"], y - m["y"])
        if d <= m["d"] / 2 + 0.3:
            return "cavity" if d <= m["d"] / 2 - 0.3 else "skip"
    for sck in data["sockets"]:
        d = dist_point_outline(sck, x, y)
        if d <= 0.3:
            if sck["type"] == "round":
                axes = [(sck["x"], sck["y"])]
            else:
                axes = [(sck["x"] + k * sck["hole_pitch"], sck["y"]) for k in (-1.5, -0.5, 0.5, 1.5)]
            dh = min(math.hypot(x - ax, y - ay) for (ax, ay) in axes)
            if dh <= HOLE_D / 2 + 0.3:
                return "none" if dh <= HOLE_D / 2 - 0.3 else "skip"
            return "cavity" if d <= -0.3 else "skip"
    return "top"

def check_topmap(name, plate, n, solid, data, bits, step=0.5):
    bad = []; cnt = {"top": 0, "cavity": 0, "none": 0, "skip": 0}
    x0 = -R - 1; nx = int(round((2 * R + 2) / step)) + 1
    img = []
    for j in range(nx):
        y = R + 1 - j * step
        row = []
        for i in range(nx):
            x = x0 + i * step
            e = expected_top(plate, data, n, x, y, bits)
            cnt[e] += 1
            z = solid.top_z(x, y)
            okp = True
            if e == "top":
                okp = z is not None and abs(z) <= 0.02
            elif e == "cavity":
                okp = z is not None and z < -0.1
            elif e == "none":
                okp = z is None
            col = (60, 60, 60) if z is None else (int(120 + 130 * max(0, min(1, (z + 4) / 4.6))),) * 3
            if e == "skip":
                col = (col[0] // 2 + 30, col[1] // 2 + 30, col[2] // 2 + 60)
            # obrysy z JSON: gniazda zielone, dołki/stożki cyjan, krawędź (okrąg i ścięcie) niebieska, cyfra żółta
            on_outline = any(abs(dist_point_outline(s_, x, y)) <= 0.26 for s_ in data["sockets"])
            on_feat = any(abs(math.hypot(x - m["x"], y - m["y"]) - m["d"] / 2) <= 0.26 for m in data["markers"] + data["code_dimples"])
            rho = math.hypot(x, y); proj = x * FLAT_N.x + y * FLAT_N.y
            on_edge = (abs(rho - R) <= 0.26 and proj <= FLAT_DIST) or (abs(proj - FLAT_DIST) <= 0.26 and rho <= R)
            if on_outline:
                col = (0, 200, 0)
            elif on_feat:
                col = (0, 200, 200)
            elif on_edge:
                col = (60, 60, 255)
            elif z is not None and z > 0.3:
                col = (255, 220, 0)
            if not okp:
                col = (255, 0, 0)
                bad.append((round(x, 2), round(y, 2), e, None if z is None else round(z, 3)))
            row.append(col)
        img.append(row)
    write_png_rgb(os.path.join(REC, f"wierzch_R57_{name}.png"), [[px for px in r for _ in range(2)] for r in img for _ in range(2)])
    rec("K-06x", name, "ZAL" if not bad else "NIE",
        f"mapa wierzchu krok {step} w kole: punktów top {cnt['top']}, w cechach {cnt['cavity']}, bez materiału {cnt['none']}, pominiętych (krawędzie cech) {cnt['skip']}; "
        f"niezgodnych {len(bad)}" + (f": {bad[:12]}" if bad else ""), "B",
        uwaga="sprawdzenie recenzenta (poza protokołem): brak nadmiarowych i brakujących wycięć na wierzchu; PNG z obrysami z JSON")

# ---------- K-61 a–e, K-63 z siatki ----------
def check_round_body(name, solid, n, data):
    # (a) promień z sond promieniowych co 10° na Z −4 i −7,5, bez sektora ścięcia (± FLAT_HALF_ANG + 2°); dodatkowo co 1° (gęsto)
    flat_c = math.degrees(FLAT_ANG)
    def in_flat(a, margin):
        d = (a - flat_c + 180) % 360 - 180
        return abs(d) <= FLAT_HALF_ANG + margin
    vals = []; bad = []
    for z in (-4.0, -7.5, -1.0, -6.0):
        for a in range(0, 360, 1):
            if in_flat(a, 2.0):
                continue
            h = solid.radial_hit(a, z)
            vals.append((a, z, h))
            if h is None or abs(h - R) > 0.05:
                bad.append((a, z, h))
    hs = [v[2] for v in vals if v[2] is not None]
    rec("K-61a", name, "ZAL" if not bad else "NIE",
        f"promień z {len(vals)} sond promieniowych (co 1°, Z −1/−4/−6/−7,5, poza sektorem ścięcia ±{FLAT_HALF_ANG + 2:.1f}°): min {min(hs):.3f}, max {max(hs):.3f} (oczek. {R} ± 0,05); niezgodnych {len(bad)}" + (f" {bad[:6]}" if bad else ""), "B",
        uwaga=f"ø = {2 * min(hs):.3f}…{2 * max(hs):.3f}")
    r_meas_max = max(hs)
    # (b) ścięcie: na kierunku −45° odległość = FLAT_DIST ± 0,05 na kilku Z i wzdłuż cięciwy (offset ±7); 3° za krawędzią sektora = R
    lst = []; bad = []
    for z in (-0.7, -1.0, -4.0, -7.5, -7.9):
        for off in (-7.0, -5.0, -3.0, 0.0, 3.0, 5.0, 7.0):
            h = solid.radial_hit(flat_c, z, offset=off)
            lst.append({"z": z, "offset": off, "d": None if h is None else round(h, 4)})
            if h is None or abs(h - FLAT_DIST) > 0.05:
                bad.append((z, off, h))
    edge = []
    for a in (flat_c - FLAT_HALF_ANG - 3, flat_c + FLAT_HALF_ANG + 3):
        for z in (-4.0, -7.5):
            h = solid.radial_hit(a, z)
            edge.append((round(a, 2), z, None if h is None else round(h, 4)))
            if h is None or abs(h - R) > 0.05:
                bad.append(("3° za sektorem", a, z, h))
    # cięciwa z siatki: na Z −4 szukaj przejścia płaszczyzna → okrąg (bisekcja po offsecie)
    def is_plane(off, z=-4.0):
        h = solid.radial_hit(flat_c, z, offset=off)
        return h is not None and abs(h - FLAT_DIST) <= 0.001   # poza cięciwą okrąg oddala się o 0,16 mm/mm → przejście ostre
    chords = {}
    for z in (-4.0, -7.5, -1.0):
        ends = []
        for sgn in (-1, 1):
            lo, hi = 0.0, 12.0   # lo: na płaszczyźnie, hi: na okręgu
            for _ in range(30):
                mid = (lo + hi) / 2
                if is_plane(sgn * mid, z):
                    lo = mid
                else:
                    hi = mid
            ends.append(sgn * (lo + hi) / 2)
        chords[z] = round(ends[1] - ends[0], 3)
    # cięciwa z wierzchołków ściany ścięcia: wierzchołki z |rzut na normalną − FLAT_DIST| < 1e-3, rozpiętość wzdłuż cięciwy
    tvec = Vector((-FLAT_N.y, FLAT_N.x))
    onp = [v for v in solid.verts if abs(v.x * FLAT_N.x + v.y * FLAT_N.y - FLAT_DIST) < 1e-3]
    ts = [v.x * tvec.x + v.y * tvec.y for v in onp]
    zs_ = [v.z for v in onp]
    chords["wierzcholki"] = round(max(ts) - min(ts), 3) if ts else None
    chords["z_sciany_sciecia"] = (round(min(zs_), 3), round(max(zs_), 3)) if zs_ else None
    chord_ok = all(abs(c - FLAT_W) <= 0.1 for k, c in chords.items() if k != "z_sciany_sciecia" and c is not None)
    # głębokość ścięcia z STL = max promień (a) − odległość płaszczyzny (b)
    d_flat_meas = [e["d"] for e in lst if e["d"] is not None and e["offset"] == 0.0]
    depth = r_meas_max - min(d_flat_meas) if d_flat_meas else None
    rec("K-61b", name, "ZAL" if (not bad and chord_ok) else "NIE",
        f"ścięcie na {flat_c}°: odległość płaszczyzny {min(e['d'] for e in lst if e['d']):.4f}…{max(e['d'] for e in lst if e['d']):.4f} z {len(lst)} sond (Z −0,7…−7,9, wzdłuż cięciwy ±7; oczek. {FLAT_DIST:.4f} ± 0,05); "
        f"3° za sektorem: {edge} (oczek. {R} ± 0,05); cięciwa z siatki {chords} (oczek. {FLAT_W} ± 0,1); niezgodnych {len(bad)}" + (f" {bad[:6]}" if bad else ""), "B",
        sondy=lst, uwaga=f"glebokosc={depth and round(depth, 4)}")
    rec("K-61e", name, "ZAL" if (depth is not None and depth >= FLAT_DMIN) else "NIE",
        f"głębokość ścięcia z siatki {depth and round(depth, 4)} (max promień {r_meas_max:.4f} − płaszczyzna {min(d_flat_meas):.4f}) ≥ {FLAT_DMIN}", "B")
    # (c) faza / krawędź na kierunku 90° + profil fazy (r(z) na 90° i 0°, 180°)
    lst = [solid.probe((0, R - 0.1, -0.05), False, "faza"), solid.probe((0, R - 0.6, -0.15), True, "pod fazą"),
           solid.probe((0, R - 0.1, -1), True, "ściana"), solid.probe((0, R - 0.1, -7.9), True, "ściana dół"), solid.probe((0, R + 0.1, -4), False, "poza")]
    prof = {}
    for a in (90, 0, 180, 270):
        prof[a] = [(z, None if (h := solid.radial_hit(a, z)) is None else round(h, 3)) for z in (-0.05, -0.15, -0.25, -0.35, -0.45, -0.55, -0.7)]
    # oczekiwany profil fazy 0,5 × 45°: r(z) = R − (CHAMF − |z|) dla |z| < CHAMF
    prof_bad = []
    for a, pts in prof.items():
        for z, h in pts:
            exp = R - max(0.0, CHAMF - abs(z))
            if h is None or abs(h - exp) > 0.05:
                prof_bad.append((a, z, h, round(exp, 3)))
    okc = all(e["ok"] for e in lst) and not prof_bad
    rec("K-61c", name, "ZAL" if okc else "NIE",
        f"{sum(e['ok'] for e in lst)}/{len(lst)} sond fazy/krawędzi zgodnych; profil fazy r(z) na 0/90/180/270°: {prof[90]} (oczek. R − (0,5 − |z|), 45° jak kwadrat); niezgodnych w profilu {len(prof_bad)}" + (f" {prof_bad[:6]}" if prof_bad else ""), "B", sondy=lst)
    # faza wzdłuż ścięcia? sprawdź r na kierunku −45° przy Z −0,05 i −0,3 (informacyjnie: czy ścięcie ma fazę)
    fz = [(z, None if (h := solid.radial_hit(flat_c, z)) is None else round(h, 3)) for z in (-0.05, -0.3, -0.5, -0.7)]
    rec("K-61c2", name, "ZAL", f"profil przy ścięciu na {flat_c}°: {fz} (płaszczyzna {FLAT_DIST:.3f}; informacyjnie — czy krawędź ścięcia ma fazę)", "D")
    # (d) bbox
    bb = solid.bb
    okd = abs(bb[0] + R) <= 0.01 and abs(bb[1] - R) <= 0.01 and abs(bb[2] + R) <= 0.01 and abs(bb[3] - R) <= 0.01 and abs(bb[4] + PT) <= 0.01 \
          and abs(bb[5] - (0.0 if n == 0 else REL_H)) <= 0.02
    rec("K-61d", name, "ZAL" if okd else "NIE", f"bbox X[{bb[0]:.3f},{bb[1]:.3f}] Y[{bb[2]:.3f},{bb[3]:.3f}] Z[{bb[4]:.3f},{bb[5]:.3f}] (oczek. ±{R} ± 0,01, Z min −{PT}, Z max {0.0 if n == 0 else REL_H})", "B")
    # K-63: ściany n_z < −0,9 na Z = −8 ± 0,01; sondy W na promieniu 45,5 co 30° od 15° na Z −7 i −7,9; dawny rowek (R − 0,5, −2) na 0/90/180°
    me = solid.obj.data
    low = []; nlow = 0
    for t in me.loop_triangles:
        a_, b_, c_ = (solid.verts[i] for i in t.vertices)
        nrm = (b_ - a_).cross(c_ - a_)
        if nrm.length < 1e-12:
            continue
        nrm.normalize()
        if nrm.z < -0.9:
            nlow += 1
            for v in (a_, b_, c_):
                if abs(v.z + PT) > 0.01:
                    low.append(round(v.z, 3))
    lst = []
    for k in range(12):
        a = math.radians(15 + 30 * k)
        for z in (-7.0, -7.9):
            lst.append(solid.probe((45.5 * math.cos(a), 45.5 * math.sin(a), z), True, f"spód {15 + 30 * k}°"))
    for a in (0, 90, 180):
        ar = math.radians(a)
        lst.append(solid.probe(((R - 0.5) * math.cos(ar), (R - 0.5) * math.sin(ar), -2), True, f"dawny rowek {a}°"))
    # spód płaski: mapa Z od dołu co 2 mm w kole r 48
    axes = []
    for sk in data["sockets"]:
        if sk["type"] == "round":
            axes.append((sk["x"], sk["y"]))
        else:
            axes += [(sk["x"] + k * sk["hole_pitch"], sk["y"]) for k in (-1.5, -0.5, 0.5, 1.5)]
    def in_hole(x, y):
        return any(math.hypot(x - ax, y - ay) <= HOLE_D / 2 + 0.3 for ax, ay in axes)
    zb = []
    for x in range(-48, 49, 2):
        for y in range(-48, 49, 2):
            if math.hypot(x, y) <= 48 and not in_hole(x, y):
                z = solid.top_z(x, y, zstart=-PT - 5, down=False)
                zb.append(z)
    zb_bad = [z for z in zb if z is None or abs(z + PT) > 0.01]
    ok63 = (not low) and all(e["ok"] for e in lst) and not zb_bad
    rec("K-63", name, "ZAL" if ok63 else "NIE",
        f"ścian z n_z < −0,9: {nlow}, wierzchołków tych ścian poza Z −8 ± 0,01: {len(low)}{(' ' + str(sorted(set(low))[:8])) if low else ''}; "
        f"{sum(e['ok'] for e in lst)}/{len(lst)} sond spodu/rowka W BRYLE; mapa spodu od dołu ({len(zb)} promieni w kole r 48, poza otworami ø3): poza −8 ± 0,01: {len(zb_bad)}", "B", sondy=lst)
    return r_meas_max, depth

# ---------- gniazda, rynienki, znaczniki, dołki, cyfra ----------
def check_plate(name, plate, n, solid, data, bits, other):
    s = data["sockets"]
    rounds = [x for x in s if x["type"] == "round"]; troughs = [x for x in s if x["type"] == "trough"]
    # K-06
    lst = []
    for r in rounds:
        x, y, d = r["x"], r["y"], r["d_top"]
        t = f"id{r['id']}"
        lst += [solid.probe((x, y, -2), False, t), solid.probe((x, y, -3.9), False, t), solid.probe((x, y, -6), False, t),
                solid.probe((x + 2.0, y, -6), True, t), solid.probe((x + d / 2 + 1.6, y, -2), True, t)]
    probes_result("K-06", name, lst, "B", uwaga=f"{len(rounds)} gniazd okrągłych × 5 sond")
    # K-07: 3 gniazda każdego rozmiaru + cięciwy (Z −2, −0,05, −3,9 dno, otwór −6) dla KAŻDEGO gniazda
    lst = []; chords = {}; bad_ch = []
    bysize = {}
    for r in rounds:
        bysize.setdefault(r["d_top"], []).append(r)
    for d, lst_r in sorted(bysize.items()):
        for r in lst_r[:3]:
            rr = (d - 2 * 2 * TAN) / 2
            lst += [solid.probe((r["x"] + rr - 0.15, r["y"], -2), False, f"ø{d}"), solid.probe((r["x"] + rr + 0.15, r["y"], -2), True, f"ø{d}")]
        r0 = lst_r[0]
        chords[d] = (round(solid.chord((r0["x"], r0["y"], -2), (1, 0, 0)), 3), round(d - 4 * TAN, 3),
                     round(solid.chord((r0["x"], r0["y"], -0.05), (1, 0, 0)), 3), round(solid.chord((r0["x"], r0["y"], -3.9), (1, 0, 0)), 3), round(d - 2 * 3.9 * TAN, 3),
                     round(solid.chord((r0["x"], r0["y"], -6), (1, 0, 0)), 3))
    for r in rounds:
        for z, exp in ((-2.0, r["d_top"] - 4 * TAN), (-0.05, r["d_top"] - 0.1 * TAN), (-3.9, r["d_top"] - 7.8 * TAN), (-6.0, HOLE_D)):
            for ax in ((1, 0, 0), (0, 1, 0)):
                c = solid.chord((r["x"], r["y"], z), ax)
                if c is None or abs(c - exp) > 0.1:
                    bad_ch.append((r["id"], z, ax, c, round(exp, 3)))
    # dno gniazda na Z −4: promień z góry w (x + 2, y) trafia na −4 ± 0,02
    bad_floor = []
    for r in rounds:
        z = solid.top_z(r["x"] + 2.0, r["y"])
        if z is None or abs(z + SOCK_DEPTH) > 0.02:
            bad_floor.append((r["id"], z))
    ok7 = all(e["ok"] for e in lst) and not bad_ch and not bad_floor
    rec("K-07", name, "ZAL" if ok7 else "NIE",
        f"{sum(e['ok'] for e in lst)}/{len(lst)} sond stożka 15° zgodnych; cięciwy X i Y wszystkich {len(rounds)} gniazd na Z −2/−0,05/−3,9/−6 vs d − 2·|z|·tan15° i ø3 (± 0,1): niezgodnych {len(bad_ch)}" + (f" {bad_ch[:6]}" if bad_ch else "") +
        f"; dno na Z −4 ± 0,02: niezgodnych {len(bad_floor)}" + (f" {bad_floor[:6]}" if bad_floor else ""), "B", sondy=lst,
        uwaga=f"cięciwy pierwszego gniazda każdego ø (Z −2 zmierz./oczek., Z −0,05, Z −3,9 zmierz./oczek., otwór Z −6): {chords}")
    # K-08: rynienki (protokół) + sonda 45° [R57] + narożnik prostokąta (przy ø100 leży w płytce: promień 48,5–48,6 < 50 → W BRYLE) + łuk końca z siatki
    lst = []; arc_bad = []; arc_vals = []
    for t in troughs:
        x, y, l, w, pitch = t["x"], t["y"], t["l"], t["w"], t["hole_pitch"]
        tg = f"id{t['id']}"
        lst += [solid.probe((x, y, -2), False, tg), solid.probe((x + l / 2 - 1, y, -2), False, tg), solid.probe((x - l / 2 + 1, y, -2), False, tg),
                solid.probe((x + l / 2 + 1.6, y, -2), True, tg), solid.probe((x - l / 2 - 1.6, y, -2), True, tg)]
        u = (w / 2 + 0.6) / math.sqrt(2)
        for sx in (1, -1):
            for sy in (1, -1):
                lst.append(solid.probe((x + sx * ((l - w) / 2 + u), y + sy * u, -2), True, tg + " 45°"))
                cx, cy = x + sx * (l / 2 - 0.5), y + sy * (w / 2 - 0.5)
                if math.hypot(cx, cy) <= R - 1.0:
                    lst.append(solid.probe((cx, cy, -2), True, tg + " narożnik prostokąta"))
        for k in (-1.5, -0.5, 0.5, 1.5):
            lst.append(solid.probe((x + k * pitch, y, -6), False, tg))
        lst.append(solid.probe((x, y, -6), True, tg))
        # łuk końca z siatki: w płaszczyźnie Z −2 promień końca = w/2 − 2·tan15°; sondy co 15° wokół środka półokręgu, r ± 0,3
        rz = w / 2 - 2 * TAN
        for sx in (1, -1):
            ex = x + sx * (l - w) / 2
            for ang in (0, 15, 30, 45, 60, 75):
                for sy in (1, -1):
                    a = math.radians(ang)
                    px, py = ex + sx * (rz - 0.3) * math.cos(a), y + sy * (rz - 0.3) * math.sin(a)
                    qx, qy = ex + sx * (rz + 0.3) * math.cos(a), y + sy * (rz + 0.3) * math.sin(a)
                    e1 = solid.probe((px, py, -2), False, tg + f" łuk {sx}/{sy} {ang}° wewn."); e2 = solid.probe((qx, qy, -2), True, tg + f" łuk {sx}/{sy} {ang}° zewn.")
                    lst += [e1, e2]
            # promień łuku z siatki: trafienie promienia od środka półokręgu na 45°, Z −2 i Z −0,05
            for z, expr in ((-2.0, rz), (-0.05, w / 2 - 0.05 * TAN)):
                d_ = Vector((sx * math.cos(math.radians(45)), math.sin(math.radians(45)), 0))
                h = solid.bvh.ray_cast(Vector((ex, y, z)), d_, 20)
                rm = None if h[0] is None else (h[0] - Vector((ex, y, z))).length
                arc_vals.append((t["id"], sx, z, None if rm is None else round(rm, 3), round(expr, 3)))
                if rm is None or abs(rm - expr) > 0.1:
                    arc_bad.append((t["id"], sx, z, rm, round(expr, 3)))
    ok8 = all(e["ok"] for e in lst) and not arc_bad
    rec("K-08", name, "ZAL" if ok8 else "NIE",
        f"{sum(e['ok'] for e in lst)}/{len(lst)} sond rynienek zgodnych ({len(troughs)} rynienki: środek, końce, +1,6 za końcem, 4 × sonda 45° [R57], narożniki prostokąta w płytce W BRYLE, 4 otwory ø3, między otworami, łuk końca r ± 0,3 co 15°); "
        f"promień łuku końca z siatki na 45° (Z −2 → w/2 − 2·tan15°, Z −0,05 → w/2): {arc_vals}; niezgodnych {len(arc_bad)}", "B", sondy=lst,
        uwaga="koniec rynienki = półokrąg o promieniu w/2 (stadion), nie prostokąt")
    # K-09: znaczniki + kontrola odwrotna (dawne rogi ±42 i dawne dołki (−45, −36…−27) — poza obrysem ø100 → POZA; dołki DRUGIEGO typu → W BRYLE)
    lst = []
    for m in data["markers"]:
        x, y = m["x"], m["y"]; tg = f"znacznik {m['corner']}"
        lst += [solid.probe((x, y, -1), False, tg), solid.probe((x, y, -3.3), True, tg),
                solid.probe((x + 1.5, y, -1), False, tg), solid.probe((x + 2.7, y, -1), True, tg),
                solid.probe((x, y + 1.5, -1), False, tg), solid.probe((x, y + 2.7, -1), True, tg)]
    rev = []
    for (x, y) in ((-OLD_MC, -OLD_MC), (-OLD_MC, OLD_MC), (OLD_MC, OLD_MC), (OLD_MC, -OLD_MC)):
        rev.append(((x, y, -1), f"dawny róg (promień {math.hypot(x, y):.1f} > {R})"))
    for k in range(3):
        rev.append(((OLD_DIMPLE_X, OLD_DIMPLE_Y0 + k * OLD_DIMPLE_P, -0.5), f"dawny dołek (promień {math.hypot(OLD_DIMPLE_X, OLD_DIMPLE_Y0 + k * OLD_DIMPLE_P):.1f})"))
    rev.append(((OLD_BIT_D[0], OLD_BIT_D[1], -0.5), f"dawny dołek D (promień {math.hypot(*OLD_BIT_D):.1f})"))
    for p, tg in rev:
        inside_plate = math.hypot(p[0], p[1]) <= R - 0.3 and (p[0] * FLAT_N.x + p[1] * FLAT_N.y) <= FLAT_DIST - 0.3
        lst.append(solid.probe(p, inside_plate, tg + (" W" if inside_plate else " poza obrysem → POZA")))
    # dołki drugiego typu (kontrola odwrotna per typ): pełna bryła na Z −0,5, o ile ≥ 0,5 od obrysów
    for b, (dx, dy) in DIMPLES_R[other].items():
        dmin = min(dist_point_outline(sk, dx, dy) for sk in s)
        dmk = min(math.hypot(dx - m["x"], dy - m["y"]) - m["d"] / 2 for m in data["markers"])
        nr = data.get("number_relief")
        near_num = nr is not None and n != 0 and abs(dx - nr["x"]) < 4 and abs(dy - nr["y"]) < 4
        if dmin >= 0.5 and dmk >= 0.5 and not near_num:
            lst.append(solid.probe((dx, dy, -0.5), True, f"dołek {b} typu {other} ({dx}, {dy}) → brak dołka W BRYLE"))
    probes_result("K-09", name, lst, "B", uwaga="3 znaczniki × 6 sond + kontrola odwrotna: 4 dawne rogi, 4 dawne dołki (poza obrysem ø100 → POZA), dołki drugiego typu W BRYLE")
    # K-11: dołki z JSON code_dimples wg bitów + promień dołka (cięciwa na Z −0,5 i −0,1) + dno na −1
    lst = []; dchords = []
    for m in data["code_dimples"]:
        b, x, y = m["bit"], m["x"], m["y"]
        present = b in bits
        lst.append(solid.probe((x, y, -0.5), not present, b))
        if present:
            lst.append(solid.probe((x, y, -1.3), True, b))
            zf = solid.top_z(x, y)
            dchords.append((b, round(solid.chord((x, y, -0.5), (1, 0, 0)), 3), round(solid.chord((x, y, -0.1), (1, 0, 0)), 3), None if zf is None else round(zf, 3)))
        else:
            lst.append(solid.probe((x, y, -0.1), True, b + " brak"))
    rec_ok = all(e["ok"] for e in lst)
    rec("K-11", name, "ZAL" if rec_ok else "NIE",
        f"{sum(e['ok'] for e in lst)}/{len(lst)} sond zgodnych; n={n} bity obecne {bits or 'ABCD (baza)'}; (bit, cięciwa X na Z −0,5, na Z −0,1, Z dna) = {dchords} (oczek. ø{DIMPLE_D}, dno −{DIMPLE_DEPTH})", "B", sondy=lst)
    # K-13: relief cyfry w kole: obszar number_relief ± 4 (krok 0,1); max Z; obrys reliefu: promień ≤ 47, odstęp od gniazd/dołków/stożków/ścięcia
    nr = data.get("number_relief")
    if nr is None:
        hm_all = solid.heightmap(-R, R, -R, R, 1.0)
        zm = max(z for row in hm_all for z in row if z is not None)
        rec("K-13", name, "ZAL" if abs(zm) <= 0.02 else "NIE", f"number_relief null → max Z całej płytki {zm:.3f} (oczek. 0 ± 0,02)", "B")
    else:
        cx, cy = nr["x"], nr["y"]
        x0, x1, y0, y1 = cx - 4, cx + 4, cy - 4, cy + 4
        hm = solid.heightmap(x0, x1, y0, y1, 0.1)
        zs = [z for row in hm for z in row if z is not None]
        zmax = max(zs) if zs else None
        exp = 0.0 if n == 0 else REL_H
        tol = 0.02 if n == 0 else 0.05
        ok = zmax is not None and abs(zmax - exp) <= tol
        png = os.path.join(REC, f"relief_R57_{name}.png")
        write_png(png, hm, -0.2, 0.7, 6)
        pts = [(x0 + i * 0.1, y1 - j * 0.1) for j, row in enumerate(hm) for i, z in enumerate(row) if z is not None and z > 0.3]
        info = ""
        if pts:
            cen = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
            xs_ = [p[0] for p in pts]; ys_ = [p[1] for p in pts]
            rmax = max(math.hypot(p[0], p[1]) for p in pts)
            # odstępy obrysu reliefu (piksele z > 0,3) do obrysów gniazd, dołków, stożków, płaszczyzny ścięcia, krawędzi
            d_sock = min(dist_point_outline(sk, p[0], p[1]) for p in pts for sk in s)
            d_dim = min(math.hypot(p[0] - m["x"], p[1] - m["y"]) - m["d"] / 2 for p in pts for m in data["code_dimples"])
            d_mk = min(math.hypot(p[0] - m["x"], p[1] - m["y"]) - m["d"] / 2 for p in pts for m in data["markers"])
            d_fl = min(FLAT_DIST - (p[0] * FLAT_N.x + p[1] * FLAT_N.y) for p in pts)
            d_ed = min(R - CHAMF - math.hypot(p[0], p[1]) for p in pts)
            # wysokość reliefu: min Z nad obszarem pikseli (czy relief jest pełny 0,6) i max Z całej płytki poza obszarem cyfry
            zrel = [z for row in hm for z in row if z is not None and z > 0.3]
            info = (f"; obrys cyfry: {min(xs_):.1f}…{max(xs_):.1f} × {min(ys_):.1f}…{max(ys_):.1f} (wys. {max(ys_) - min(ys_):.1f}, szer. {max(xs_) - min(xs_):.1f}), środek ({cen[0]:.2f}, {cen[1]:.2f}), "
                    f"max promień obrysu {rmax:.2f} ≤ 47; odstęp do gniazd {d_sock:.2f}, dołków {d_dim:.2f}, stożków {d_mk:.2f}, ścięcia {d_fl:.2f}, początku fazy {d_ed:.2f}; Z reliefu {min(zrel):.3f}…{max(zrel):.3f}")
            ok = ok and rmax <= ZONE_R and d_sock > 0 and d_dim > 0 and d_mk > 0 and d_fl > 0 and d_ed > 0
            if n == 0:
                ok = False
        # max Z całej płytki poza obszarem cyfry = 0
        hm_all = solid.heightmap(-R, R, -R, R, 1.0)
        zo = [z for j, row in enumerate(hm_all) for i, z in enumerate(row) if z is not None and not (x0 <= -R + i * 1.0 <= x1 and y0 <= R - j * 1.0 <= y1)]
        zo_max = max(zo)
        ok = ok and abs(zo_max) <= 0.02
        rec("K-13", name, "ZAL" if ok else "NIE",
            f"max Z w obszarze cyfry ({cx}, {cy}) ± 4: {zmax:.3f} (oczek. {exp} ± {tol}); pikseli reliefu {len(pts)}{info}; max Z poza obszarem cyfry {zo_max:.3f} (oczek. 0 ± 0,02); PNG {os.path.basename(png)} — treść cyfry do odczytu przez recenzenta", "B")
    # ścianki do krawędzi Z SIATKI: promień przez każdy koniec obrysu (gniazda, rynienki, stożki, dołki) od zewnątrz; grubość materiału = odległość 1. trafienia (ściana płytki) − 2. (ściana cechy)
    walls = []
    feats = []
    for sk in s:
        a0, a1, r = outline_seg(sk)
        for e in (a0, a1):
            feats.append((f"gniazdo id {sk['id']}", e.x, e.y, r))
    for m in data["markers"]:
        feats.append((f"stożek {m['corner']}", m["x"], m["y"], m["d"] / 2))
    for m in data["code_dimples"]:
        if m["bit"] in bits:
            feats.append((f"dołek {m['bit']}", m["x"], m["y"], m["d"] / 2))
    skipped = []
    for (tg, fx, fy, fr) in feats:
        ang = math.degrees(math.atan2(fy, fx)); rho = math.hypot(fx, fy)
        for z in (-0.6, -0.05):
            # kierunek radialny przez środek cechy od zewnątrz: 1. trafienie = ściana płytki (okrąg/faza/ścięcie), 2. = ściana cechy;
            # 2. trafienie musi leżeć na obrysie TEJ cechy (ρ + r − |z|·tan15° dla gniazd ± 0,1), inaczej promień trafił po drodze w inną cechę → pomijane
            a = math.radians(ang)
            u = Vector((math.cos(a), math.sin(a), 0)); o = u * (R + 5) + Vector((0, 0, z))
            hits = solid.hits_along(o, -u, R + 5 + 3)
            if len(hits) >= 2:
                r1 = R + 5 - hits[0]; r2 = R + 5 - hits[1]
                if tg.startswith("gniazdo"):
                    exp2 = rho + fr - abs(z) * TAN
                    if abs(r2 - exp2) > 0.1:
                        skipped.append((tg, round(ang, 1), z, round(r2, 3), round(exp2, 3))); continue
                wall = hits[1] - hits[0]
                walls.append((tg, round(ang, 1), z, round(r1, 3), round(r2, 3), round(wall, 3)))
    g_walls = [w for w in walls if w[0].startswith("gniazdo")]
    wmin06 = min((w for w in g_walls if w[2] == -0.6), key=lambda w: w[5])
    wmin005 = min((w for w in g_walls if w[2] == -0.05), key=lambda w: w[5])
    # oczekiwane z JSON: ściana pionowa: R − ρ_max (na Z −0,6 ścianka siatki = R − ρ_max + 0,6·tan15°); początek fazy (R − 0,5): na Z −0,05 pierwsze trafienie = faza r = R − 0,45
    rho_max = max(outline_max_radius(x) for x in s)
    w_wall = wmin06[5] - 0.6 * TAN
    w_ch = wmin005[5] - 0.05 - 0.05 * TAN
    rec("K-16s", name, "ZAL" if (w_wall >= 1.5 - 0.02 and w_ch >= 1.5 - 0.02) else "NIE",
        f"ścianka z siatki (promień przez koniec obrysu od zewnątrz; 1. trafienie ściana płytki, 2. ściana cechy): na Z −0,6 min {wmin06[5]} ({wmin06[0]}, {wmin06[1]}°, trafienia {wmin06[3]}/{wmin06[4]}) → do obrysu górnego {w_wall:.3f} (JSON R − ρ_max = {R - rho_max:.3f}) ≥ 1,5; "
        f"na Z −0,05 (1. trafienie = faza) min {wmin005[5]} ({wmin005[0]}, trafienia {wmin005[3]}/{wmin005[4]}) → obrys górny–początek fazy {w_ch:.3f} (JSON R − 0,5 − ρ_max = {R - CHAMF - rho_max:.3f}) ≥ 1,5; promieni pominiętych (inna cecha po drodze) {len(skipped)}", "B",
        uwaga=json.dumps({"min_z-0.6": wmin06, "min_z-0.05": wmin005, "stozki_dolki_z-0.6": [w for w in walls if not w[0].startswith("gniazdo") and w[2] == -0.6], "pominiete": skipped[:10]}, ensure_ascii=False))
    # K-06x mapa wierzchu
    check_topmap(name, plate, n, solid, data, bits)

# ---------- SHA ----------
def check_sha():
    notes = []; ok = True
    for name, (sh, vol, bb) in DECL.items():
        p = os.path.join(WYN, "stl", name + ".stl")
        s_ = sha(p) if os.path.exists(p) else None
        if s_ != sh:
            ok = False; notes.append(f"{name}: {s_} ≠ raport {sh}")
    for name, sh in DECL_JSON.items():
        p = os.path.join(WYN, "json", name)
        s_ = sha(p) if os.path.exists(p) else None
        if s_ != sh:
            ok = False; notes.append(f"{name}: {s_} ≠ raport {sh}")
    # plik sha256_stl_po_R57_iter2.txt
    txt = open(os.path.join(WYN, "raport", "sha256_stl_po_R57_iter2.txt"), encoding="utf-8").read()
    listed = {fn: sh for sh, fn in re.findall(r"([0-9a-f]{64}) \*?(\S+)", txt)}
    n_ok = 0; n_bad = []
    for fn, sh in listed.items():
        p = os.path.join(WYN, "stl", fn)
        if os.path.exists(p) and sha(p) == sh:
            n_ok += 1
        else:
            n_bad.append(fn)
    rec("SHA", "4 STL + 2 JSON", "ZAL" if ok and not n_bad else "NIE",
        f"4 STL + 2 JSON = raport wykonawcy §2/§7.1: {ok}" + (f" ({notes})" if notes else "") + f"; sha256_stl_po_R57_iter2.txt: {n_ok}/{len(listed)} zgodnych" + (f" niezgodne {n_bad}" if n_bad else ""), "P")
    # 15 plików R56
    txt = open(os.path.join(ROOT, "Ramki_pakiet", "SHA256SUMS_2026-11-01_R56.txt"), encoding="utf-8").read()
    r56 = {}
    for sh, path in re.findall(r"([0-9a-f]{64}) \*?(\S+)", txt):
        if path.endswith(".stl"):
            fn = os.path.basename(path).replace("_TEST_SKANERA", "")
            r56.setdefault(fn, set()).add(sh)
    bad = []; good = 0
    for fn, shs in sorted(r56.items()):
        p = os.path.join(WYN, "stl", fn)
        s_ = sha(p) if os.path.exists(p) else None
        if len(shs) == 1 and s_ in shs:
            good += 1
        else:
            bad.append((fn, s_, shs))
    rec("K-59s", "15 plików R56", "ZAL" if not bad else "NIE", f"{good}/{len(r56)} plików z SHA256SUMS_2026-11-01_R56.txt bajtowo identycznych w wyniki_v2/stl" + (f"; różne: {bad}" if bad else ""), "B",
        uwaga="kontrola niezależna recenzenta (K-59 [R57]: 15 plików R56 bez zmian)")

# ---------- główna pętla ----------
def main():
    check_sha()
    layouts = {}; squares = {}; k16 = {}
    for plate in ("wieczorna", "poranna"):
        squares[plate] = json.load(open(os.path.join(WYN, "json", f"uklad_gniazd_{plate}.json"), encoding="utf-8"))
        p = os.path.join(WYN, "json", f"uklad_gniazd_okragla_{plate}.json")
        layouts[plate] = json.load(open(p, encoding="utf-8"))
        nm = f"uklad_gniazd_okragla_{plate}.json"
        check_json(plate, layouts[plate], nm, squares[plate])
        k16[plate] = check_k16_k62_k61f(plate, layouts[plate], nm)
    summary = {}
    for name, (plate, n) in FILES.items():
        path = os.path.join(WYN, "stl", name + ".stl")
        if not os.path.exists(path):
            rec("K-01", name, "NIE", "brak pliku", "B"); continue
        obj = import_stl(path)
        weld(obj)
        raw_bb = bbox([v.co for v in obj.data.vertices])
        cx = (raw_bb[0] + raw_bb[1]) / 2; cy = (raw_bb[2] + raw_bb[3]) / 2
        M = Matrix.Translation(Vector((-cx, -cy, -(raw_bb[4] + PT))))   # tabela 1: spód Z=0 → wierzch na 0, środek XY na 0
        exp_bb = (RD, RD, PT if n == 0 else PT + REL_H)
        solid = Solid(obj, M)
        print(f"=== {name}: bbox surowy X[{raw_bb[0]:.3f},{raw_bb[1]:.3f}] Y[{raw_bb[2]:.3f},{raw_bb[3]:.3f}] Z[{raw_bb[4]:.3f},{raw_bb[5]:.3f}]")
        vol, dims = general_checks(name, obj, solid, exp_bb, VOL_EXP[plate])
        # dopasowanie środka: środek okręgu z trafień promieniowych na 0/90/180/270° (kontrola, że środek bbox = oś walca)
        hx = (solid.radial_hit(0, -4), solid.radial_hit(180, -4)); hy = (solid.radial_hit(90, -4), solid.radial_hit(270, -4))
        rec("K-02c", name, "ZAL" if all(h is not None and abs(h - R) <= 0.01 for h in hx + hy) else "NIE",
            f"oś walca vs środek bbox: trafienia na 0/180/90/270° = {[h and round(h, 4) for h in hx + hy]} (oczek. {R} ± 0,01)", "B")
        decl = DECL[name]
        dv = vol - decl[1]
        rec("OBJ", name, "ZAL" if abs(dv) <= 0.01 + 0.005 and all(abs(dims[i] - decl[2][i]) <= 0.01 for i in range(3)) else "NIE",
            f"objętość z siatki {vol:.3f} cm³ vs raport {decl[1]} (Δ {dv:+.3f}, tol. ± 0,01 + zaokrąglenie); gabaryt {dims[0]:.3f} × {dims[1]:.3f} × {dims[2]:.3f} vs raport {decl[2]}", "P")
        bits = BITS_ALL if n == 0 else NUM_BITS[n]
        other = "poranna" if plate == "wieczorna" else "wieczorna"
        rmax, depth = check_round_body(name, solid, n, layouts[plate])
        check_plate(name, plate, n, solid, layouts[plate], bits, other)
        summary[name] = {"bbox_surowy": [round(v, 3) for v in raw_bb], "objetosc_cm3": round(vol, 4), "gabaryt": [round(v, 3) for v in dims],
                         "sha256": sha(path), "rozmiar_B": os.path.getsize(path), "promien_max_siatka": round(rmax, 4), "glebokosc_sciecia": depth and round(depth, 4),
                         "bity": bits, "k16_json": k16[plate]}
    out = {"etap": "R57", "iteracja": ITER, "blender": bpy.app.version_string, "wyniki_v2": WYN, "pliki": summary, "wyniki": RESULTS}
    json.dump(out, open(os.path.join(REC, f"wyniki_R57_iter{ITER}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    nie = [r for r in RESULTS if r["wynik"] == "NIE"]
    print(f"\n=== PODSUMOWANIE: {len(RESULTS)} sprawdzeń, NIE: {len(nie)}; sond punktowych łącznie {sum(len(r['sondy']) for r in RESULTS)}")
    for r in nie:
        print("  NIE", r["id"], r["plik"], r["wartosc"][:400])

main()
