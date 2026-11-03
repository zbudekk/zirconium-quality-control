# -*- coding: utf-8 -*-
"""
Skrypt RECENZENTA — R54 (płytki po przeliczeniu układu gniazd do koła socket_zone_r 47).
Pochodna recenzja/sprawdz_A.py (etap A), dostosowana do protokołu po R54:
  K-05 (a) liczby z ev_rows/mo_rows, (c) warunek koła, (e) ścianki po przekątnej;
  K-09 sondy z `markers` JSON + kontrola odwrotna dawnych rogów; K-12 kieszenie z `magnet_pockets` JSON (= rogi ±42);
  K-16 promień znacznika ≤ 44,5, znacznik–gniazdo ≥ 3, znacznik–dołek ≥ 1,5, znacznik–kieszeń (XY) ≥ 1,5.
Dodatkowo (recenzent, poza protokołem): K-05x JSON == ev_rows/mo_rows co do pozycji; K-06x mapa wierzchu (każdy punkt
wierzchu płytki poza oczekiwanymi cechami musi być na Z = 0; każdy punkt w cesze poniżej 0) — wykrywa brakujące i nadmiarowe wycięcia.
Napisany bez czytania ramka_generator.py.
Uruchomienie:
  "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b -P recenzja/sprawdz_R54.py -- --iter 1
Wyniki: recenzja/wyniki_R54_iter<n>.json, recenzja/relief_R54_<plik>.png, recenzja/wierzch_R54_<plik>.png
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
    if "--wyniki" in a:
        WYN = a[a.index("--wyniki") + 1]

PAR = json.load(open(os.path.join(ROOT, "parametry.json"), encoding="utf-8"))
def P(sec, key):
    return PAR[sec][key]["value"]

# ---------- parametry oczekiwane (z parametry.json / planu v2) ----------
PLATE = P("plytka", "plate_size")                 # 96
PT = P("plytka", "plate_thickness")               # 8
SOCK_DEPTH = P("plytka", "socket_depth")          # 4
ANG = math.radians(P("plytka", "socket_wall_angle"))  # 15°
HOLE_D = P("plytka", "socket_hole_d")             # 3
DIMPLE_X = P("plytka", "code_dimple_x")           # -45.0
DIMPLE_Y0 = P("plytka", "code_dimple_y0")         # -36
DIMPLE_P = P("plytka", "code_dimple_pitch")       # 3
DIMPLE_D = P("plytka", "code_dimple_d")           # 2
DIMPLE_DEPTH = P("plytka", "code_dimple_depth")   # 1
MARK_OFF = P("plytka", "marker_offset")           # 6 -> kieszenie magnesów ±42
MARK_D = P("plytka", "marker_cone_d")             # 5
MARK_DEPTH = P("plytka", "marker_cone_depth")     # 3
NOTCH = P("plytka", "notch_size")                 # 5
MAG_D = P("plytka", "magnet_pocket_d")            # 5.2
MAG_DEPTH = P("plytka", "magnet_pocket_depth")    # 2.2
REL_H = P("plytka", "number_relief_h")            # 0.6
NUM_X = P("plytka", "number_pos_x"); NUM_Y = P("plytka", "number_pos_y")
GROOVE_W = P("plytka", "cover_groove_w"); GROOVE_DEPTH = P("plytka", "cover_groove_depth"); GROOVE_Z = P("plytka", "cover_groove_z")
ZONE_R = P("plytka", "socket_zone_r")             # 47 (R54)
ZONE_SQ = P("plytka", "socket_zone") / 2          # 45
WALL_MIN = P("plytka", "socket_wall_min")         # 3
MARKER_POS = {"wieczorna": P("plytka", "ev_marker_pos"), "poranna": P("plytka", "mo_marker_pos")}
ROWS = {"wieczorna": P("plytka", "ev_rows"), "poranna": P("plytka", "mo_rows")}
HALF = PLATE / 2  # 48
MC = HALF - MARK_OFF  # 42 — kieszenie magnesów (rogi)
BITS = {"A": DIMPLE_Y0, "B": DIMPLE_Y0 + DIMPLE_P, "C": DIMPLE_Y0 + 2 * DIMPLE_P}
NUM_BITS = {1: "A", 2: "B", 3: "AB", 4: "C", 5: "AC", 6: "BC"}

FILES = {
    "ramka_plytka_wieczorna_v2": ("wieczorna", 0),
    "ramka_plytka_wieczorna_n1_v2": ("wieczorna", 1),
    "ramka_plytka_wieczorna_n2_v2": ("wieczorna", 2),
    "ramka_plytka_wieczorna_n3_v2": ("wieczorna", 3),
    "ramka_plytka_poranna_v2": ("poranna", 0),
    "ramka_plytka_poranna_n4_v2": ("poranna", 4),
    "ramka_plytka_poranna_n5_v2": ("poranna", 5),
    "ramka_plytka_poranna_n6_v2": ("poranna", 6),
}
VOL_EXP = {"wieczorna": 62.0, "poranna": 61.0}  # tabela 1 protokołu (± 30 %)

RESULTS = []
def rec(kid, plik, wynik, wartosc, waga, sondy=None, uwaga=""):
    RESULTS.append({"id": kid, "plik": plik, "wynik": wynik, "wartosc": wartosc, "waga": waga,
                    "sondy": sondy or [], "uwaga": uwaga})
    print(f"[{wynik}] {kid} {plik}: {wartosc} {uwaga}")

# ---------- narzędzia ----------
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
    """Siatka w układzie montażowym + BVH + sondy (parzystość przecięć w 3 kierunkach)."""
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
        """Cięciwa pustki przez punkt p wzdłuż osi: odległość między pierwszymi trafieniami w +axis i −axis."""
        d = Vector(axis).normalized()
        h1 = self.bvh.ray_cast(Vector(p), d, half); h2 = self.bvh.ray_cast(Vector(p), -d, half)
        return None if (h1[0] is None or h2[0] is None) else (h1[0] - h2[0]).length

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
    """img: lista wierszy, każdy wiersz lista (r,g,b)."""
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
    bm.free()
    return bad_edges, loose

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
    be, lv = manifold_check(obj)
    so = self_overlap(solid)
    rec("K-03", name, "ZAL" if (be == 0 and lv == 0 and so == 0) else "NIE",
        f"krawędzie niemanifold {be}, luźne wierzchołki {lv}, samoprzecięcia {so}", "B")
    nc = components(obj)
    rec("K-04", name, "ZAL" if nc == 1 else "NIE", f"składowych {nc}", "B")
    vol = volume(solid)
    ok = vol > 0 and abs(vol - exp_vol) <= 0.3 * exp_vol
    rec("K-04b", name, "ZAL" if ok else "NIE", f"objętość {vol:.3f} cm³ (oczek. {exp_vol} ± 30 %)", "B")
    return vol, dims

# ---------- geometria obrysów ----------
def outline_seg(s):
    """Obrys górny jako odcinek osi + promień: okrąg → punkt; stadion → odcinek x ± (l−w)/2."""
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
    """Min. odległość między obrysami górnymi w XY (okrąg/stadion); dla szachownicy = odległość środków − promienie."""
    a0, a1, ra = outline_seg(s1); b0, b1, rb = outline_seg(s2)
    cands = [pt_seg(a0, b0, b1), pt_seg(a1, b0, b1), pt_seg(b0, a0, a1), pt_seg(b1, a0, a1)]
    return min(cands) - ra - rb

def dist_point_outline(sock, px, py):
    a0, a1, r = outline_seg(sock)
    return pt_seg(Vector((px, py)), a0, a1) - r

# ---------- K-05 (+ K-05x: JSON == ev_rows/mo_rows) ----------
def check_json(plate, data, name):
    s = data["sockets"]
    rounds = [x for x in s if x["type"] == "round"]; troughs = [x for x in s if x["type"] == "trough"]
    rows_par = ROWS[plate]
    exp_round = sum(len(r["x"]) for r in rows_par if r["type"] == "round")
    exp_trough = sum(len(r["x"]) for r in rows_par if r["type"] == "trough")
    notes = []
    ok_a = (len(rounds), len(troughs)) == (exp_round, exp_trough)
    notes.append(f"(a) round/trough {len(rounds)}/{len(troughs)} (oczek. z {'ev' if plate == 'wieczorna' else 'mo'}_rows {exp_round}/{exp_trough})")
    # (b) symetria rzędów
    rows = {}
    for x in s:
        rows.setdefault(round(x["y"], 2), []).append(x)
    ok_b = True
    for y, lst in rows.items():
        xs = sorted(v["x"] for v in lst)
        if any(abs(xs[i] + xs[-1 - i]) > 0.01 for i in range(len(xs))):
            ok_b = False; notes.append(f"(b) rząd y={y} niesymetryczny: {xs}")
    notes.append(f"(b) {len(rows)} rzędów symetrycznych: {ok_b}")
    # (c) kwadrat ±45 ORAZ koło socket_zone_r
    ok_c = True; max_sq = 0; max_r = 0; max_r_id = None
    for x in s:
        a0, a1, r = outline_seg(x)
        x0, x1, y0, y1 = min(a0.x, a1.x) - r, max(a0.x, a1.x) + r, x["y"] - r, x["y"] + r
        max_sq = max(max_sq, abs(x0), abs(x1), abs(y0), abs(y1))
        if x0 < -ZONE_SQ - 1e-6 or x1 > ZONE_SQ + 1e-6 or y0 < -ZONE_SQ - 1e-6 or y1 > ZONE_SQ + 1e-6:
            ok_c = False; notes.append(f"(c) id {x['id']} poza kwadratem ±{ZONE_SQ}: [{x0},{x1}]×[{y0},{y1}]")
        for end in (a0, a1):
            rr = math.hypot(end.x, end.y) + r
            if rr > max_r:
                max_r = rr; max_r_id = x["id"]
            if rr > ZONE_R + 1e-6:
                ok_c = False; notes.append(f"(c) id {x['id']} poza kołem r {ZONE_R}: {rr:.3f}")
    notes.append(f"(c) max |x|+r / |y|+r = {max_sq:.3f} ≤ {ZONE_SQ}; max promień obrysu {max_r:.3f} (id {max_r_id}) ≤ {ZONE_R}")
    # (d) narożniki: żaden punkt obrysu z |x|>35 ∧ |y|>35
    ok_d = True
    for x in s:
        a0, a1, r = outline_seg(x)
        for sx in (-1, 1):
            for sy in (-1, 1):
                # najbliższy punkt odcinka osi do kwadratu narożnego [35,48]×[35,48] (z przeniesieniem znaku)
                corner_min = Vector((sx * 35, sy * 35))
                # punkt obrysu najdalej w kierunku narożnika: sprawdź czy istnieje punkt osi + r przekraczający 35 w obu osiach
                for end in (a0, a1):
                    far = end + Vector((sx, sy)).normalized() * r
                    if (far.x * sx > 35 + 1e-6) and (far.y * sy > 35 + 1e-6):
                        ok_d = False; notes.append(f"(d) id {x['id']} wchodzi w narożnik ({sx},{sy})")
                    # także skrajne punkty osiowe: (end.x ± r, end.y) i (end.x, end.y ± r) nie mogą być w narożniku
                    for q in (Vector((end.x + sx * r, end.y)), Vector((end.x, end.y + sy * r))):
                        if (q.x * sx > 35 + 1e-6) and (q.y * sy > 35 + 1e-6):
                            ok_d = False; notes.append(f"(d) id {x['id']} wchodzi w narożnik ({sx},{sy}) [oś]")
    # (e) ścianki ≥ 3 (po przekątnej dla szachownicy)
    mind = 1e9; pair = None; pairs3 = []
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            d = dist_outlines(s[i], s[j])
            if d < mind:
                mind = d; pair = (s[i]["id"], s[j]["id"])
            if d < WALL_MIN + 0.02:
                pairs3.append((s[i]["id"], s[j]["id"], round(d, 3)))
    ok_e = mind >= WALL_MIN - 0.005
    notes.append(f"(e) min ścianka {mind:.3f} (para {pair}); par ze ścianką ≤ 3,02: {len(pairs3)}")
    # (f) d_bottom
    ok_f = True
    for x in rounds:
        exp_db = x["d_top"] - 2 * SOCK_DEPTH * math.tan(ANG)
        if abs(x["d_bottom"] - exp_db) > 0.01:
            ok_f = False; notes.append(f"(f) id {x['id']} d_bottom {x['d_bottom']} oczek. {exp_db:.3f}")
    notes.append(f"(f) d_bottom = d_top − {2 * SOCK_DEPTH * math.tan(ANG):.3f}: {ok_f}")
    # (g) id
    ids = [x["id"] for x in s]
    ok_g = ids == list(range(1, len(s) + 1))
    order = sorted(s, key=lambda v: (round(v["y"], 2), -v["x"]))
    if [v["id"] for v in order] != ids:
        ok_g = False; notes.append("(g) kolejność id ≠ rzędami od przodu, malejące x")
    notes.append(f"(g) id 1…{len(s)} ciągłe, rzędami od przodu, malejące x: {ok_g}")
    ok = ok_a and ok_b and ok_c and ok_d and ok_e and ok_f and ok_g
    rec("K-05", name, "ZAL" if ok else "NIE", "; ".join(notes), "B",
        uwaga=f"max_promien={max_r:.3f}; min_scianka={mind:.3f}")
    # K-05x: JSON == rzędy z parametry.json (pozycje i wymiary), + markers/magnet_pockets/dimples/notch
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
    mp = {m["corner"]: (m["x"], m["y"], m["d"], m["depth"]) for m in data["magnet_pockets"]}
    mp_exp = {"A": (-MC, -MC, MAG_D, MAG_DEPTH), "B": (-MC, MC, MAG_D, MAG_DEPTH), "C": (MC, MC, MAG_D, MAG_DEPTH)}
    if mp != mp_exp:
        xs.append(f"magnet_pockets {mp} ≠ rogi {mp_exp}")
    cd = {m["bit"]: (m["x"], m["y"]) for m in data["code_dimples"]}
    if cd != {b: (DIMPLE_X, y) for b, y in BITS.items()}:
        xs.append(f"code_dimples {cd}")
    nt = data["notch"]
    if (nt["x_min"], nt["x_max"], nt["y_min"], nt["y_max"]) != (HALF - NOTCH, HALF, -HALF, -HALF + NOTCH):
        xs.append(f"notch {nt}")
    holes = [(t["hole_count"], t["hole_pitch"]) for t in troughs]
    pitch_exp = P("plytka", "ev_trough_hole_pitch") if plate == "wieczorna" else P("plytka", "mo_trough_hole_pitch")
    if any(h != (4, pitch_exp) for h in holes):
        xs.append(f"rynienki otwory {holes} ≠ (4, {pitch_exp})")
    okx = (exp_set == got_set) and not xs
    rec("K-05x", name, "ZAL" if okx else "NIE",
        f"gniazda JSON == {'ev' if plate == 'wieczorna' else 'mo'}_rows (pozycje, średnice, l×w): {exp_set == got_set} "
        f"(brak w JSON {sorted(exp_set - got_set)}, nadmiar {sorted(got_set - exp_set)}); markers = *_marker_pos, kieszenie = rogi ±{MC}, dołki, wycięcie, otwory rynienek: "
        + ("zgodne" if not xs else "; ".join(xs)), "B", uwaga="sprawdzenie recenzenta (poza protokołem)")
    return ok

# ---------- K-16 ----------
def check_k16(plate, data, name):
    s = data["sockets"]
    notes = []; ok = True; vals = {}
    markers = {m["corner"]: (m["x"], m["y"], m["d"] / 2) for m in data["markers"]}
    pockets = {m["corner"]: (m["x"], m["y"], m["d"] / 2) for m in data["magnet_pockets"]}
    # gniazdo–dołek ≥ 3
    mind = 1e9; who = None
    for sock in s:
        for b, y in BITS.items():
            d = dist_point_outline(sock, DIMPLE_X, y) - DIMPLE_D / 2
            if d < mind:
                mind = d; who = (sock["id"], b)
    notes.append(f"gniazdo–dołek min {mind:.2f} ({who}) ≥ 3"); ok &= mind >= WALL_MIN; vals["gniazdo_dolek"] = round(mind, 3)
    # [R54] znaczniki: promień ≤ socket_zone_r − d/2; znacznik–gniazdo ≥ 3; znacznik–dołek ≥ 1,5; znacznik–kieszeń (XY) ≥ 1,5
    for c, (mx, my, mr) in markers.items():
        rad = math.hypot(mx, my)
        dmin = 1e9; wid = None
        for sock in s:
            d = dist_point_outline(sock, mx, my) - mr
            if d < dmin:
                dmin = d; wid = sock["id"]
        ddim = min(math.hypot(mx - DIMPLE_X, my - y) - mr - DIMPLE_D / 2 for y in BITS.values())
        dpock = min(math.hypot(mx - px, my - py) - mr - pr for (px, py, pr) in pockets.values())
        ok_m = rad <= ZONE_R - mr + 1e-6 and dmin >= WALL_MIN - 0.005 and ddim >= 1.5 and dpock >= 1.5
        ok &= ok_m
        notes.append(f"znacznik {c} ({mx}, {my}): promień {rad:.2f} ≤ {ZONE_R - mr}; gniazdo min {dmin:.2f} (id {wid}) ≥ 3; dołek {ddim:.2f} ≥ 1,5; kieszeń XY {dpock:.2f} ≥ 1,5 → {'ok' if ok_m else 'NIE'}")
        vals[f"znacznik_{c}"] = {"promien": round(rad, 3), "gniazdo": round(dmin, 3), "gniazdo_id": wid, "dolek": round(ddim, 3), "kieszen_xy": round(dpock, 3)}
    # gniazdo–kieszeń magnesu (XY) i gniazdo–wycięcie D, gniazdo–relief ≥ 1,5 (cechy narożne)
    mind2 = 1e9; who2 = None
    for sock in s:
        for c, (px, py, pr) in pockets.items():
            d = dist_point_outline(sock, px, py) - pr
            if d < mind2:
                mind2 = d; who2 = (sock["id"], f"kieszeń {c}")
        a0, a1, r = outline_seg(sock)
        for (rx0, rx1, ry0, ry1, nm) in ((HALF - NOTCH, HALF, -HALF, -HALF + NOTCH, "wycięcie D"), (36, 43, -48, -41, "relief numeru")):
            for end in (a0, a1):
                cx = max(rx0, min(rx1, end.x)); cy = max(ry0, min(ry1, end.y))
                d = math.hypot(end.x - cx, end.y - cy) - r
                if d < mind2:
                    mind2 = d; who2 = (sock["id"], nm)
    notes.append(f"gniazdo–cecha narożna (kieszeń magnesu XY / wycięcie D / relief) min {mind2:.2f} ({who2}) ≥ 1,5"); ok &= mind2 >= 1.5
    vals["gniazdo_cecha_narozna"] = round(mind2, 3)
    # kieszeń magnesu–krawędź ≥ 1,5; dołek–krawędź
    d_pe = min(HALF - max(abs(px), abs(py)) - pr for (px, py, pr) in pockets.values())
    d_edge = HALF - (abs(DIMPLE_X) + DIMPLE_D / 2)
    notes.append(f"kieszeń magnesu–krawędź {d_pe:.2f} ≥ 1,5; dołek–krawędź {d_edge:.2f}")
    ok &= d_pe >= 1.5 and d_edge >= 1.5
    dg = math.hypot((HALF - GROOVE_DEPTH) - (abs(DIMPLE_X) + DIMPLE_D / 2), (GROOVE_Z - GROOVE_W / 2) - DIMPLE_DEPTH)
    notes.append(f"dołek–rowek pokrywki {dg:.2f} (R47: 1,3 przyjęte, D)")
    rec("K-16", name, "ZAL" if ok else "NIE", "; ".join(notes), "B", uwaga=json.dumps(vals, ensure_ascii=False))

# ---------- mapa wierzchu (K-06x, recenzent) ----------
def expected_top(plate, data, n, x, y):
    """Co powinno być na wierzchu w (x, y): 'top' (Z=0), 'cavity' (Z<0), 'none' (brak materiału), 'skip' (strefa niepewna)."""
    # poza obrysem płytki / R1 narożniki / faza 0,5
    if abs(x) > HALF - 0.6 or abs(y) > HALF - 0.6:
        return "skip"
    # wycięcie D
    nt = data["notch"]
    if nt["x_min"] - 0.3 <= x <= nt["x_max"] + 0.3 and nt["y_min"] - 0.3 <= y <= nt["y_max"] + 0.3:
        return "skip" if (abs(x - nt["x_min"]) < 0.3 or abs(y - nt["y_max"]) < 0.3) else "none"
    # relief numeru
    if n != 0 and 36 - 0.5 <= x <= 43 + 0.5 and -48 <= y <= -41 + 0.5:
        return "skip"
    # dołki kodu
    for b, yy in BITS.items():
        d = math.hypot(x - DIMPLE_X, y - yy)
        if d <= DIMPLE_D / 2 + 0.3:
            if n == 0 or b in NUM_BITS[n]:
                return "cavity" if d <= DIMPLE_D / 2 - 0.3 else "skip"
            return "top" if d > DIMPLE_D / 2 + 0.3 else "skip"
    # znaczniki
    for m in data["markers"]:
        d = math.hypot(x - m["x"], y - m["y"])
        if d <= m["d"] / 2 + 0.3:
            return "cavity" if d <= m["d"] / 2 - 0.3 else "skip"
    # gniazda (z otworami ø3 przelotowymi: promień z góry nie trafia → None)
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

def check_topmap(name, plate, n, solid, data, step=0.5):
    bad = []; cnt = {"top": 0, "cavity": 0, "none": 0, "skip": 0}
    x0 = -HALF; nx = int(round(PLATE / step)) + 1
    img = []
    for j in range(nx):
        y = HALF - j * step
        row = []
        for i in range(nx):
            x = x0 + i * step
            e = expected_top(plate, data, n, x, y)
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
            if not okp:
                col = (255, 0, 0)
                bad.append((round(x, 2), round(y, 2), e, None if z is None else round(z, 3)))
            row.append(col)
        img.append(row)
    write_png_rgb(os.path.join(REC, f"wierzch_R54_{name}.png"), [[px for px in r for _ in range(2)] for r in img for _ in range(2)])
    rec("K-06x", name, "ZAL" if not bad else "NIE",
        f"mapa wierzchu krok {step}: punktów top {cnt['top']}, w cechach {cnt['cavity']}, bez materiału {cnt['none']}, pominiętych (krawędzie cech) {cnt['skip']}; "
        f"niezgodnych {len(bad)}" + (f": {bad[:12]}" if bad else ""), "B", uwaga="sprawdzenie recenzenta (poza protokołem): brak nadmiarowych i brakujących wycięć na wierzchu")

# ---------- płytka: sondy ----------
def check_plate(name, plate, n, solid, data):
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
    # K-07 (3 gniazda każdego rozmiaru) + cięciwa na Z −2 dla każdego rozmiaru
    lst = []; chords = {}
    bysize = {}
    for r in rounds:
        bysize.setdefault(r["d_top"], []).append(r)
    for d, lst_r in sorted(bysize.items()):
        for r in lst_r[:3]:
            rr = (d - 2 * 2 * math.tan(ANG)) / 2
            lst += [solid.probe((r["x"] + rr - 0.15, r["y"], -2), False, f"ø{d}"), solid.probe((r["x"] + rr + 0.15, r["y"], -2), True, f"ø{d}")]
        r0 = lst_r[0]
        chords[d] = (round(solid.chord((r0["x"], r0["y"], -2), (1, 0, 0)), 3), round(d - 4 * math.tan(ANG), 3),
                     round(solid.chord((r0["x"], r0["y"], -0.05), (1, 0, 0)), 3), round(solid.chord((r0["x"], r0["y"], -6), (1, 0, 0)), 3))
    probes_result("K-07", name, lst, "B", uwaga=f"cięciwy X (zmierzona na Z −2, oczek. d − 2·2·tan15°, na Z −0,05, otwór na Z −6): {chords}")
    # K-08
    lst = []
    for t in troughs:
        x, y, l, w, pitch = t["x"], t["y"], t["l"], t["w"], t["hole_pitch"]
        tg = f"id{t['id']}"
        lst += [solid.probe((x, y, -2), False, tg), solid.probe((x + l / 2 - 1, y, -2), False, tg), solid.probe((x - l / 2 + 1, y, -2), False, tg),
                solid.probe((x + l / 2 - 0.5, y + w / 2 - 0.5, -2), True, tg), solid.probe((x + l / 2 + 1.6, y, -2), True, tg)]
        for k in (-1.5, -0.5, 0.5, 1.5):
            lst.append(solid.probe((x + k * pitch, y, -6), False, tg))
        lst.append(solid.probe((x, y, -6), True, tg))
    probes_result("K-08", name, lst, "B", uwaga=f"{len(troughs)} rynienki × 10 sond")
    # K-09 [R54]: pozycje z markers JSON + kontrola odwrotna dawnych rogów
    lst = []
    for m in data["markers"]:
        x, y = m["x"], m["y"]; tg = f"znacznik {m['corner']}"
        lst += [solid.probe((x, y, -1), False, tg), solid.probe((x, y, -3.3), True, tg),
                solid.probe((x + 1.5, y, -1), False, tg), solid.probe((x + 2.7, y, -1), True, tg)]
    for (x, y) in ((-MC, -MC), (-MC, MC), (MC, MC)):
        lst.append(solid.probe((x, y, -1), True, "dawny róg"))
    probes_result("K-09", name, lst, "B", uwaga="3 znaczniki × 4 sondy + 3 dawne rogi W BRYLE")
    # K-10
    lst = [solid.probe((45.5, -45.0, -4), False), solid.probe((45.5, -45.0, -7.9), False),
           solid.probe((41.5, -45.0, -4), True), solid.probe((45.5, -41.5, -4), True)]
    probes_result("K-10", name, lst, "B")
    # K-11
    lst = []
    if n == 0:
        for b, y in BITS.items():
            lst += [solid.probe((DIMPLE_X, y, -0.5), False, b), solid.probe((DIMPLE_X, y, -1.3), True, b)]
    else:
        bits = NUM_BITS[n]
        for b, y in BITS.items():
            lst.append(solid.probe((DIMPLE_X, y, -0.5), b not in bits, b))
            if b in bits:
                lst.append(solid.probe((DIMPLE_X, y, -1.3), True, b))
    probes_result("K-11", name, lst, "B", uwaga=f"n={n} bity {NUM_BITS.get(n, 'ABC (baza)')}")
    # K-12: kieszenie z magnet_pockets JSON (muszą być rogi ±42 — K-05x)
    lst = []
    for m in data["magnet_pockets"]:
        x, y = m["x"], m["y"]; tg = f"kieszeń {m['corner']}"
        lst += [solid.probe((x, y, -7), False, tg), solid.probe((x, y, -5.6), True, tg),
                solid.probe((x + 2.45, y, -7), False, tg), solid.probe((x + 2.8, y, -7), True, tg)]
    lst.append(solid.probe((MC, -MC, -7), True, "D bez kieszeni"))
    probes_result("K-12", name, lst, "B")
    # K-13: mapa wysokości x 36..43, y -48..-41
    hm = solid.heightmap(36, 43, -48, -41, 0.1)
    zs = [z for row in hm for z in row if z is not None]
    zmax = max(zs) if zs else None
    exp = 0.0 if n == 0 else REL_H
    tol = 0.02 if n == 0 else 0.05
    ok = zmax is not None and abs(zmax - exp) <= tol
    png = os.path.join(REC, f"relief_R54_{name}.png")
    write_png(png, hm, -0.2, 0.7, 6)
    pts = [(36 + i * 0.1, -41 - j * 0.1) for j, row in enumerate(hm) for i, z in enumerate(row) if z is not None and z > 0.3]
    cen = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)) if pts else None
    rec("K-13", name, "ZAL" if ok else "NIE",
        f"max Z w obszarze {zmax:.3f} (oczek. {exp} ± {tol}); środek reliefu {cen and (round(cen[0], 2), round(cen[1], 2))}; "
        f"pikseli reliefu {len(pts)}; PNG {os.path.basename(png)} — treść cyfry do odczytu przez recenzenta", "B")
    # K-14
    lst = []
    for (x, y) in ((47.5, 0), (-47.5, 0), (0, 47.5), (0, -47.5)):
        sx = 1 if x > 0 else (-1 if x < 0 else 0); sy = 1 if y > 0 else (-1 if y < 0 else 0)
        lst += [solid.probe((x, y, -2), False), solid.probe((x - 0.6 * sx, y - 0.6 * sy, -2), True),
                solid.probe((x, y, -0.8), True), solid.probe((x, y, -3.2), True)]
    probes_result("K-14", name, lst, "B")
    # K-15
    lst = [solid.probe((47.8, 47.8, -4), False), solid.probe((47.9, 0, -0.05), False), solid.probe((47.9, 0, -1), True)]
    probes_result("K-15", name, lst, "D")
    # K-06x mapa wierzchu
    check_topmap(name, plate, n, solid, data)

# ---------- K-58 ----------
def check_k58():
    path = os.path.join(WYN, "arkusze", "kody_plytek.md")
    if not os.path.exists(path):
        rec("K-58", "kody_plytek.md", "NIE", "brak pliku", "P"); return
    txt = open(path, encoding="utf-8").read()
    notes = []; ok = True
    for n, bits in NUM_BITS.items():
        typ = "wieczorna" if n <= 3 else "poranna"
        m = re.search(rf"^\|\s*{n}\s*\|\s*(\w+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|", txt, re.M)
        if not m:
            ok = False; notes.append(f"brak wiersza n={n}"); continue
        t, mag, dim, fn = m.group(1).strip(), m.group(2), m.group(3), m.group(4)
        mag_bits = "".join(sorted(re.findall(r"\b([ABC])\b", mag))); dim_bits = "".join(sorted(re.findall(r"\b([ABC])\b", dim)))
        row_ok = (t == typ and mag_bits == bits and dim_bits == bits and f"_n{n}_" in fn)
        if not row_ok:
            ok = False; notes.append(f"n={n}: typ {t}, magnesy {mag_bits}, dołki {dim_bits}, plik {fn.strip()} (oczek. {typ}, {bits})")
    low = txt.lower()
    has = all(w in low for w in ("biegun", "jednakow")) and re.search(r"\bS\b", txt) is not None
    if not has:
        ok = False; notes.append("brak instrukcji bieguna (biegun / S / jednakowy)")
    notes.append(f"6 wierszy n→typ→magnesy→dołki→plik zgodne z D11/K-11; instrukcja bieguna (biegun/S/jednakowy): {has}; x dołków −45 w tekście: {'-45' in txt}")
    rec("K-58", "kody_plytek.md", "ZAL" if ok else "NIE", "; ".join(notes), "P")

# ---------- główna pętla ----------
def main():
    layouts = {}
    for plate in ("wieczorna", "poranna"):
        p = os.path.join(WYN, "json", f"uklad_gniazd_{plate}.json")
        layouts[plate] = json.load(open(p, encoding="utf-8"))
        check_json(plate, layouts[plate], f"uklad_gniazd_{plate}.json")
        check_k16(plate, layouts[plate], f"uklad_gniazd_{plate}.json")
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
        exp_bb = (PLATE, PLATE, PT if n == 0 else PT + REL_H)
        solid = Solid(obj, M)
        print(f"=== {name}: bbox surowy X[{raw_bb[0]:.3f},{raw_bb[1]:.3f}] Y[{raw_bb[2]:.3f},{raw_bb[3]:.3f}] Z[{raw_bb[4]:.3f},{raw_bb[5]:.3f}]")
        vol, dims = general_checks(name, obj, solid, exp_bb, VOL_EXP[plate])
        summary[name] = {"bbox_surowy": [round(v, 3) for v in raw_bb], "objetosc_cm3": round(vol, 4), "gabaryt": [round(v, 3) for v in dims],
                         "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest(), "rozmiar_B": os.path.getsize(path)}
        check_plate(name, plate, n, solid, layouts[plate])
    check_k58()
    out = {"etap": "R54", "iteracja": ITER, "blender": bpy.app.version_string, "wyniki_v2": WYN, "pliki": summary, "wyniki": RESULTS}
    json.dump(out, open(os.path.join(REC, f"wyniki_R54_iter{ITER}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    nie = [r for r in RESULTS if r["wynik"] == "NIE"]
    print(f"\n=== PODSUMOWANIE: {len(RESULTS)} sprawdzeń, NIE: {len(nie)}; sond łącznie {sum(len(r['sondy']) for r in RESULTS)}")
    for r in nie:
        print("  NIE", r["id"], r["plik"], r["wartosc"][:300])

main()
