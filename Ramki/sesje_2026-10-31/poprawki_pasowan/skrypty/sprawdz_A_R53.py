# KOPIA R53 (31.10.2026) — oryginał: recenzja/sprawdz_A.py (nietknięty). Zmiany w kopii: (1) wyniki zapisywane do
# sesje_2026-10-31/poprawki_pasowan/skrypty/wyniki/ zamiast recenzja/; (2) oczekiwania zależne od geometrii R53: brak (płytki i pokrywka bez zmian)
# -*- coding: utf-8 -*-
"""
Skrypt RECENZENTA — etap A (płytki, pokrywka, JSON, kody_plytek.md).
Napisany niezależnie, bez czytania ramka_generator.py.
Uruchomienie:
  "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b -P recenzja/sprawdz_A.py -- --iter 1
Wyniki: recenzja/wyniki_A_iter<n>.json, recenzja/relief_<plik>.png
"""
import bpy, bmesh, json, math, os, sys, zlib, struct, re, hashlib
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

ROOT = r"<PC>\Desktop\Ramki"
WYN = os.path.join(ROOT, "wyniki_v2")
REC = os.path.join(ROOT, "sesje_2026-10-31", "poprawki_pasowan", "skrypty", "wyniki")   # R53: kopia
ITER = 1
if "--" in sys.argv:
    a = sys.argv[sys.argv.index("--") + 1:]
    if "--iter" in a:
        ITER = a[a.index("--iter") + 1]

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
MARK_OFF = P("plytka", "marker_offset")           # 6 -> ±42
MARK_D = P("plytka", "marker_cone_d")             # 5
MARK_DEPTH = P("plytka", "marker_cone_depth")     # 3
NOTCH = P("plytka", "notch_size")                 # 5
MAG_D = P("plytka", "magnet_pocket_d")            # 5.2
MAG_DEPTH = P("plytka", "magnet_pocket_depth")    # 2.2
REL_H = P("plytka", "number_relief_h")            # 0.6
NUM_X = P("plytka", "number_pos_x"); NUM_Y = P("plytka", "number_pos_y")
GROOVE_W = P("plytka", "cover_groove_w"); GROOVE_DEPTH = P("plytka", "cover_groove_depth"); GROOVE_Z = P("plytka", "cover_groove_z")
EV_PITCH = P("plytka", "ev_trough_hole_pitch"); MO_PITCH = P("plytka", "mo_trough_hole_pitch")
COV_IN = P("plytka", "socket_zone") + 2 * P("pokrywka", "cover_clearance") + 6  # nieużywane
COVER_OUT = PLATE + 2 * P("pokrywka", "cover_clearance") + 2 * P("pokrywka", "cover_skirt_t")  # 99.6
COVER_H = P("pokrywka", "cover_inner_h") + P("pokrywka", "cover_top_t") + P("pokrywka", "cover_skirt_below")  # 20
COVER_LABEL_REL = 0.6
HALF = PLATE / 2  # 48
MC = HALF - MARK_OFF  # 42
BITS = {"A": DIMPLE_Y0, "B": DIMPLE_Y0 + DIMPLE_P, "C": DIMPLE_Y0 + 2 * DIMPLE_P}
NUM_BITS = {1: "A", 2: "B", 3: "AB", 4: "C", 5: "AC", 6: "BC"}

FILES_A = {
    "ramka_plytka_wieczorna_v2": ("plate", "wieczorna", 0),
    "ramka_plytka_wieczorna_n1_v2": ("plate", "wieczorna", 1),
    "ramka_plytka_wieczorna_n2_v2": ("plate", "wieczorna", 2),
    "ramka_plytka_wieczorna_n3_v2": ("plate", "wieczorna", 3),
    "ramka_plytka_poranna_v2": ("plate", "poranna", 0),
    "ramka_plytka_poranna_n4_v2": ("plate", "poranna", 4),
    "ramka_plytka_poranna_n5_v2": ("plate", "poranna", 5),
    "ramka_plytka_poranna_n6_v2": ("plate", "poranna", 6),
    "ramka_pokrywka_v2": ("cover", None, None),
}
VOL_EXP = {"wieczorna": 62.0, "poranna": 61.0, "cover": 30.0}  # tabela 1 (pokrywka 30 wg komunikatu właściciela)

RESULTS = []   # lista wyników K-xx
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
    """Siatka w układzie montażowym + BVH + sondy."""
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
        n = 0; o = Vector(p); last = None; total = 0.0
        for _ in range(500):
            hit = self.bvh.ray_cast(o, d, self.diag)
            if hit[0] is None:
                break
            loc, nrm, idx, dist = hit
            total += dist
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

    def probe(self, p, expect_in):
        """Zwraca dict z wynikiem sondy (ok, 3 wyniki, odległość od ściany, ew. przesunięcie)."""
        p = Vector(p)
        r = self.inside3(p)
        loc, nrm, dist = self.nearest(p)
        entry = {"p": [round(c, 3) for c in p], "oczek": "W" if expect_in else "POZA",
                 "r3": ["W" if x else "P" for x in r], "d_sciana": round(dist, 3)}
        if r.count(True) in (0, 3):
            entry["wynik"] = "W" if r[0] else "POZA"
        else:
            # niestabilna → przesunięcie 0,1 mm w głąb oczekiwanego obszaru
            if nrm is None or nrm.length == 0:
                nrm = Vector((0, 0, 1))
            p2 = p + (-nrm if expect_in else nrm) * 0.1
            r2 = self.inside3(p2)
            entry["niestabilna"] = True
            entry["p_przes"] = [round(c, 3) for c in p2]
            entry["r3_przes"] = ["W" if x else "P" for x in r2]
            if r2.count(True) in (0, 3):
                entry["wynik"] = "W" if r2[0] else "POZA"
            else:
                entry["wynik"] = "NIESTABILNA"
        entry["ok"] = (entry["wynik"] == entry["oczek"])
        return entry

    def top_z(self, x, y, zstart=None, down=True):
        """Pierwsze trafienie promienia z góry (down) albo z dołu."""
        if zstart is None:
            zstart = self.bb[5] + 5 if down else self.bb[4] - 5
        d = Vector((0, 0, -1 if down else 1))
        hit = self.bvh.ray_cast(Vector((x, y, zstart)), d, self.diag)
        return None if hit[0] is None else hit[0].z

    def heightmap(self, x0, x1, y0, y1, step=0.25):
        nx = int(round((x1 - x0) / step)) + 1; ny = int(round((y1 - y0) / step)) + 1
        hm = []
        for j in range(ny):
            y = y1 - j * step  # wiersz 0 = góra obrazu = max y
            row = []
            for i in range(nx):
                x = x0 + i * step
                z = self.top_z(x, y)
                row.append(z)
            hm.append(row)
        return hm

def write_png(path, hm, zmin, zmax):
    """Szary PNG z mapy wysokości (None = czarny)."""
    h = len(hm); w = len(hm[0])
    raw = bytearray()
    for row in hm:
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

def upscale_png(path, hm, zmin, zmax, k=4):
    big = []
    for row in hm:
        r = []
        for z in row:
            r.extend([z] * k)
        for _ in range(k):
            big.append(r)
    write_png(path, big, zmin, zmax)

def manifold_check(obj):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bad_edges = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    loose = sum(1 for v in bm.verts if len(v.link_edges) == 0)
    bm.free()
    return bad_edges, loose

def self_overlap(solid):
    pairs = solid.bvh.overlap(solid.bvh)
    tris = solid.tris
    n = 0
    for a, b in pairs:
        if a == b:
            continue
        if set(tris[a]) & set(tris[b]):
            continue
        n += 1
    return n // 2

def components(obj):
    me = obj.data
    n = len(me.vertices)
    parent = list(range(n))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for e in me.edges:
        a, b = e.vertices
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    return len({find(i) for i in range(n)})

def volume(solid):
    v = 0.0
    V = solid.verts
    for a, b, c in solid.tris:
        v += V[a].dot(V[b].cross(V[c]))
    return v / 6.0 / 1000.0  # cm³

def probes_result(kid, plik, lst, waga, uwaga=""):
    ok = all(e["ok"] for e in lst)
    nbad = sum(1 for e in lst if not e["ok"])
    rec(kid, plik, "ZAL" if ok else "NIE", f"{len(lst) - nbad}/{len(lst)} sond zgodnych", waga, lst, uwaga)
    return ok

# ---------- sprawdzenia ogólne K-01…K-04b ----------
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

# ---------- K-05: JSON ----------
def dist_outlines(s1, s2):
    """Min. odległość między obrysami górnymi (okrąg/stadion) — w XY."""
    def seg(s):
        if s["type"] == "round":
            return (Vector((s["x"], s["y"])), Vector((s["x"], s["y"])), s["d_top"] / 2)
        half = (s["l"] - s["w"]) / 2
        return (Vector((s["x"] - half, s["y"])), Vector((s["x"] + half, s["y"])), s["w"] / 2)
    a0, a1, ra = seg(s1); b0, b1, rb = seg(s2)
    # odległość odcinek–odcinek w 2D (próbkowanie + dokładne dla punkt–odcinek)
    def pt_seg(p, q0, q1):
        d = q1 - q0
        if d.length < 1e-9:
            return (p - q0).length
        t = max(0, min(1, (p - q0).dot(d) / d.length_squared))
        return (p - (q0 + d * t)).length
    cands = [pt_seg(a0, b0, b1), pt_seg(a1, b0, b1), pt_seg(b0, a0, a1), pt_seg(b1, a0, a1)]
    # równoległe odcinki poziome: wystarczą końce
    return min(cands) - ra - rb

def check_json(plate, data, name):
    s = data["sockets"]
    rounds = [x for x in s if x["type"] == "round"]; troughs = [x for x in s if x["type"] == "trough"]
    exp = {"wieczorna": (24, 2), "poranna": (35, 2)}[plate]
    notes = []
    ok_a = (len(rounds), len(troughs)) == exp
    notes.append(f"(a) round/trough {len(rounds)}/{len(troughs)} oczek. {exp}")
    # (b) symetria rzędów
    rows = {}
    for x in s:
        rows.setdefault(round(x["y"], 2), []).append(x)
    ok_b = True
    for y, lst in rows.items():
        xs = sorted(v["x"] for v in lst)
        if any(abs(xs[i] + xs[-1 - i]) > 0.01 for i in range(len(xs))):
            ok_b = False; notes.append(f"(b) rząd y={y} niesymetryczny: {xs}")
    # (c),(d) strefa i narożniki
    ok_c = ok_d = True
    for x in s:
        if x["type"] == "round":
            r = x["d_top"] / 2; x0, x1, y0, y1 = x["x"] - r, x["x"] + r, x["y"] - r, x["y"] + r
        else:
            x0, x1, y0, y1 = x["x"] - x["l"] / 2, x["x"] + x["l"] / 2, x["y"] - x["w"] / 2, x["y"] + x["w"] / 2
        if x0 < -45 - 1e-6 or x1 > 45 + 1e-6 or y0 < -45 - 1e-6 or y1 > 45 + 1e-6:
            ok_c = False; notes.append(f"(c) id {x['id']} poza strefą: [{x0},{x1}]×[{y0},{y1}]")
        # narożnik: fragment obrysu z |x|>35 i |y|>35 jednocześnie
        cx = max(abs(x0), abs(x1)); cy = max(abs(y0), abs(y1))
        if cx > 35 + 1e-6 and cy > 35 + 1e-6:
            # dokładniej: czy obrys ma punkt z |x|>35 i |y|>35
            if x["type"] == "round":
                # najbliższy punkt okręgu do narożnika (±35..±48)
                sx = 1 if x["x"] > 0 else -1; sy = 1 if x["y"] > 0 else -1
                corner = Vector((sx * 35, sy * 35))
                # punkt okręgu najdalej w kierunku narożnika
                c = Vector((x["x"], x["y"])); dirv = Vector((sx, sy)).normalized()
                far = c + dirv * r
                if abs(far.x) > 35 + 1e-6 and abs(far.y) > 35 + 1e-6:
                    ok_d = False; notes.append(f"(d) id {x['id']} wchodzi w narożnik")
            else:
                ok_d = False; notes.append(f"(d) id {x['id']} (rynienka) wchodzi w narożnik")
    # (e) ścianki ≥ 3
    mind = 1e9; pair = None
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            d = dist_outlines(s[i], s[j])
            if d < mind:
                mind = d; pair = (s[i]["id"], s[j]["id"])
    ok_e = mind >= 3.0 - 0.005
    notes.append(f"(e) min ścianka {mind:.3f} (para {pair})")
    # (f) d_bottom
    ok_f = True
    for x in rounds:
        exp_db = x["d_top"] - 2 * SOCK_DEPTH * math.tan(ANG)
        if abs(x["d_bottom"] - exp_db) > 0.01:
            ok_f = False; notes.append(f"(f) id {x['id']} d_bottom {x['d_bottom']} oczek. {exp_db:.3f}")
    # (g) id
    ids = [x["id"] for x in s]
    ok_g = ids == list(range(1, len(s) + 1))
    order = sorted(s, key=lambda v: (round(v["y"], 2), -v["x"]))
    if [v["id"] for v in order] != ids:
        ok_g = False; notes.append("(g) kolejność id ≠ rzędami od przodu, malejące x")
    ok = ok_a and ok_b and ok_c and ok_d and ok_e and ok_f and ok_g
    rec("K-05", name, "ZAL" if ok else "NIE", "; ".join(notes), "B")
    return ok

# ---------- K-16: rachunek ścianek ----------
def check_k16(plate, data, name):
    s = data["sockets"]
    feats = []  # (nazwa, x, y, r) cechy narożne jako okręgi; wycięcie jako kwadrat
    for b, y in BITS.items():
        feats.append((f"dołek {b}", DIMPLE_X, y, DIMPLE_D / 2))
    for c, (x, y) in {"A": (-MC, -MC), "B": (-MC, MC), "C": (MC, MC)}.items():
        feats.append((f"znacznik {c}", x, y, MARK_D / 2))
        feats.append((f"kieszeń magnesu {c}", x, y, MAG_D / 2))
    def d_to_outline(sock, px, py):
        if sock["type"] == "round":
            return math.hypot(sock["x"] - px, sock["y"] - py) - sock["d_top"] / 2
        half = (sock["l"] - sock["w"]) / 2
        cx = max(sock["x"] - half, min(sock["x"] + half, px))
        return math.hypot(cx - px, sock["y"] - py) - sock["w"] / 2
    notes = []; ok = True
    # gniazdo–dołek ≥ 3
    mind = 1e9; who = None
    for sock in s:
        for b, y in BITS.items():
            d = d_to_outline(sock, DIMPLE_X, y) - DIMPLE_D / 2
            if d < mind:
                mind = d; who = (sock["id"], b)
    notes.append(f"gniazdo–dołek min {mind:.2f} ({who})"); ok &= mind >= 3.0
    # gniazdo–cecha narożna ≥ 1,5 (wszystkie cechy)
    mind2 = 1e9; who2 = None
    for sock in s:
        for nm, x, y, r in feats:
            d = d_to_outline(sock, x, y) - r
            if d < mind2:
                mind2 = d; who2 = (sock["id"], nm)
        # wycięcie D: kwadrat x 43..48, y -48..-43
        if sock["type"] == "round":
            cx = max(43, min(48, sock["x"])); cy = max(-48, min(-43, sock["y"]))
            d = math.hypot(sock["x"] - cx, sock["y"] - cy) - sock["d_top"] / 2
        else:
            d = 99
        if d < mind2:
            mind2 = d; who2 = (sock["id"], "wycięcie D")
        # relief numeru: prostokąt x 36..43, y -48..-41
        if sock["type"] == "round":
            cx = max(36, min(43, sock["x"])); cy = max(-48, min(-41, sock["y"]))
            d = math.hypot(sock["x"] - cx, sock["y"] - cy) - sock["d_top"] / 2
            if d < mind2:
                mind2 = d; who2 = (sock["id"], "relief numeru")
    notes.append(f"gniazdo–cecha narożna min {mind2:.2f} ({who2})"); ok &= mind2 >= 1.5
    # cechy narożne między sobą i do krawędzi (rachunek 4.11)
    d_edge = HALF - (abs(DIMPLE_X) + DIMPLE_D / 2)
    d_mark = math.hypot(DIMPLE_X + MC, BITS["A"] + MC) - MARK_D / 2 - DIMPLE_D / 2
    notes.append(f"dołek–krawędź {d_edge:.2f}; dołek A–znacznik A {d_mark:.2f}")
    ok &= d_edge >= 1.5 and d_mark >= 1.5
    d_groove = math.hypot(abs(DIMPLE_X) + DIMPLE_D / 2 - (HALF - GROOVE_DEPTH), 0) if False else None
    # dołek a rowek pokrywki: w rzucie 47.2 - 46.0 = 1.2; po skosie do krawędzi rowka (Z -1.5) od dna dołka (Z -1): sqrt(1.2²+0.5²)
    dg = math.hypot((HALF - GROOVE_DEPTH) - (abs(DIMPLE_X) + DIMPLE_D / 2), (GROOVE_Z - GROOVE_W / 2) - DIMPLE_DEPTH)
    notes.append(f"dołek–rowek pokrywki {dg:.2f} (R47: 1,3 przyjęte, D)")
    rec("K-16", name, "ZAL" if ok else "NIE", "; ".join(notes), "B")

# ---------- płytka: sondy ----------
def check_plate(name, plate, n, solid, data):
    s = data["sockets"]
    rounds = [x for x in s if x["type"] == "round"]; troughs = [x for x in s if x["type"] == "trough"]
    # K-06
    lst = []
    for r in rounds:
        x, y, d = r["x"], r["y"], r["d_top"]
        lst += [solid.probe((x, y, -2), False), solid.probe((x, y, -3.9), False), solid.probe((x, y, -6), False),
                solid.probe((x + 2.0, y, -6), True), solid.probe((x + d / 2 + 1.6, y, -2), True)]
    probes_result("K-06", name, lst, "B")
    # K-07
    lst = []
    bysize = {}
    for r in rounds:
        bysize.setdefault(r["d_top"], []).append(r)
    for d, lst_r in bysize.items():
        for r in lst_r[:3]:
            rr = (d - 2 * 2 * math.tan(ANG)) / 2  # promień na Z = -2
            lst += [solid.probe((r["x"] + rr - 0.15, r["y"], -2), False), solid.probe((r["x"] + rr + 0.15, r["y"], -2), True)]
    probes_result("K-07", name, lst, "B", uwaga=f"promień na Z=-2: d/2-{2*math.tan(ANG):.3f}")
    # K-08
    lst = []
    for t in troughs:
        x, y, l, w, pitch = t["x"], t["y"], t["l"], t["w"], t["hole_pitch"]
        lst += [solid.probe((x, y, -2), False), solid.probe((x + l / 2 - 1, y, -2), False), solid.probe((x - l / 2 + 1, y, -2), False),
                solid.probe((x + l / 2 - 0.5, y + w / 2 - 0.5, -2), True), solid.probe((x + l / 2 + 1.6, y, -2), True)]
        for k in (-1.5, -0.5, 0.5, 1.5):
            lst.append(solid.probe((x + k * pitch, y, -6), False))
        lst.append(solid.probe((x, y, -6), True))
    probes_result("K-08", name, lst, "B")
    # K-09
    lst = []
    for (x, y) in ((-MC, -MC), (-MC, MC), (MC, MC)):
        lst += [solid.probe((x, y, -1), False), solid.probe((x, y, -3.3), True),
                solid.probe((x + 1.5, y, -1), False), solid.probe((x + 2.7, y, -1), True)]
    probes_result("K-09", name, lst, "B")
    # K-10
    lst = [solid.probe((45.5, -45.0, -4), False), solid.probe((45.5, -45.0, -7.9), False),
           solid.probe((41.5, -45.0, -4), True), solid.probe((45.5, -41.5, -4), True)]
    probes_result("K-10", name, lst, "B")
    # K-11
    lst = []
    if n == 0:
        for b, y in BITS.items():
            lst += [solid.probe((DIMPLE_X, y, -0.5), False), solid.probe((DIMPLE_X, y, -1.3), True)]
    else:
        bits = NUM_BITS[n]
        for b, y in BITS.items():
            lst.append(solid.probe((DIMPLE_X, y, -0.5), b not in bits))
            if b in bits:
                lst.append(solid.probe((DIMPLE_X, y, -1.3), True))
    probes_result("K-11", name, lst, "B", uwaga=f"n={n} bity {NUM_BITS.get(n, 'ABC (baza)')}")
    # K-12
    lst = []
    for (x, y) in ((-MC, -MC), (-MC, MC), (MC, MC)):
        lst += [solid.probe((x, y, -7), False), solid.probe((x, y, -5.6), True),
                solid.probe((x + 2.45, y, -7), False), solid.probe((x + 2.8, y, -7), True)]
    lst.append(solid.probe((MC, -MC, -7), True))
    probes_result("K-12", name, lst, "B")
    # K-13: mapa wysokości x 36..43, y -48..-41
    hm = solid.heightmap(36, 43, -48, -41, 0.1)
    zs = [z for row in hm for z in row if z is not None]
    zmax = max(zs) if zs else None
    exp = 0.0 if n == 0 else REL_H
    tol = 0.02 if n == 0 else 0.05
    ok = zmax is not None and abs(zmax - exp) <= tol
    png = os.path.join(REC, f"relief_{name}.png")
    upscale_png(png, hm, -0.2, 0.7, 6)
    # szerszy rzut z całym narożnikiem D (x 30..48, y -48..-30) do oceny położenia cyfry
    hm2 = solid.heightmap(30, 48, -48, -30, 0.1)
    upscale_png(os.path.join(REC, f"relief_{name}_naroznik.png"), hm2, -0.2, 0.7, 4)
    # środek masy reliefu (gdzie z > 0.3)
    pts = [(36 + i * 0.1, -41 - j * 0.1) for j, row in enumerate(hm) for i, z in enumerate(row) if z is not None and z > 0.3]
    cen = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)) if pts else None
    rec("K-13", name, "ZAL" if ok else "NIE",
        f"max Z w obszarze {zmax:.3f} (oczek. {exp} ± {tol}); środek reliefu {cen and (round(cen[0], 2), round(cen[1], 2))}; "
        f"pikseli reliefu {len(pts)}; PNG {os.path.basename(png)} — treść do odczytu przez recenzenta", "B")
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

# ---------- pokrywka ----------
def check_cover(name, solid):
    lst = [solid.probe((0, 0, -1), True), solid.probe((0, 0, -2.5), False), solid.probe((48.1, 0, -10), False),
           solid.probe((48.5, 0, -10), True), solid.probe((50, 0, -10), False), solid.probe((0, 0, -19.9), False)]
    ok17 = probes_result("K-17", name, lst, "B")
    lst = [solid.probe((47.8, 0, -18), True), solid.probe((47.8, 20, -18), False), solid.probe((-47.8, 0, -18), True),
           solid.probe((25, -47.8, -18), True), solid.probe((0, -47.8, -18), False), solid.probe((-25, 47.8, -18), True),
           solid.probe((25, 47.8, -18), False), solid.probe((47.8, 0, -16.5), False)]
    probes_result("K-18", name, lst, "B")
    lst = [solid.probe((15, 0, -1), False), solid.probe((15, 30, -1), False), solid.probe((-15, -30, -1), False), solid.probe((0, 0, -1), True)]
    # dodatkowo wszystkie 6 otworów
    for x in (-15, 15):
        for y in (-30, 0, 30):
            lst.append(solid.probe((x, y, -1), False))
    probes_result("K-19", name, lst, "P")
    lst = [solid.probe((0, -49, -19), False), solid.probe((20, -49, -19), True), solid.probe((0, 49, -19), False), solid.probe((0, -49, -16), True)]
    probes_result("K-20", name, lst, "P")
    # K-21
    hm = solid.heightmap(-12, 12, -4, 4, 0.1)
    zs = [z for row in hm for z in row if z is not None]
    zmax = max(zs); zmin_ = min(zs)
    ok = abs(zmax - 0.6) <= 0.05
    png = os.path.join(REC, f"relief_{name}.png")
    upscale_png(png, hm, -0.2, 0.7, 5)
    hm2 = solid.heightmap(-30, 30, -15, 15, 0.2)
    upscale_png(os.path.join(REC, f"relief_{name}_szeroki.png"), hm2, -0.2, 0.7, 3)
    rec("K-21", name, "ZAL" if ok else "NIE", f"max Z {zmax:.3f} (oczek. 0,6 ± 0,05), min Z w obszarze {zmin_:.3f}; PNG {os.path.basename(png)}", "D")
    # K-22: wnęka z sond 48,1 POZA / 48,5 W na 4 bokach → 96,6 ± 0,2; dokładny pomiar promieniem poziomym
    lst = []
    for (x, y) in ((48.1, 0), (-48.1, 0), (0, 48.1), (0, -48.1)):
        lst.append(solid.probe((x, y, -10), False))
    for (x, y) in ((48.5, 0), (-48.5, 0), (0, 48.5), (0, -48.5)):
        lst.append(solid.probe((x, y, -10), True))
    # pomiar promieniem: od środka w +X/-X/+Y/-Y na Z=-10 → pierwsza ściana
    widths = {}
    for nm, d in (("X", Vector((1, 0, 0))), ("Y", Vector((0, 1, 0)))):
        h1 = solid.bvh.ray_cast(Vector((0, 0, -10)), d, 100); h2 = solid.bvh.ray_cast(Vector((0, 0, -10)), -d, 100)
        widths[nm] = (h1[0] - h2[0]).length if h1[0] and h2[0] else None
    ok = all(e["ok"] for e in lst) and all(w is not None and abs(w - 96.6) <= 0.2 for w in widths.values())
    rec("K-22", name, "ZAL" if ok else "NIE",
        f"wnęka z promieni X {widths['X']:.3f}, Y {widths['Y']:.3f} (oczek. 96,6 ± 0,2); część złożeniowa (K-53) N/D w etapie A", "B", lst)

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
    notes.append(f"x dołków w tekście: {'-45' in txt}")
    rec("K-58", "kody_plytek.md", "ZAL" if ok else "NIE", "; ".join(notes) or "tabela n→magnesy→dołki zgodna z D11/K-11; instrukcja bieguna obecna", "P")

# ---------- główna pętla ----------
def main():
    layouts = {}
    for plate in ("wieczorna", "poranna"):
        p = os.path.join(WYN, "json", f"uklad_gniazd_{plate}.json")
        layouts[plate] = json.load(open(p, encoding="utf-8"))
        check_json(plate, layouts[plate], f"uklad_gniazd_{plate}.json")
        check_k16(plate, layouts[plate], f"uklad_gniazd_{plate}.json")
    summary = {}
    if "--" in sys.argv and "--bez-pokrywki" in sys.argv[sys.argv.index("--") + 1:]:
        FILES_A.pop("ramka_pokrywka_v2", None)
    for name, (kind, plate, n) in FILES_A.items():
        path = os.path.join(WYN, "stl", name + ".stl")
        if not os.path.exists(path):
            rec("K-01", name, "NIE", "brak pliku", "B"); continue
        obj = import_stl(path)
        weld(obj)
        raw_bb = bbox([v.co for v in obj.data.vertices])
        cx = (raw_bb[0] + raw_bb[1]) / 2; cy = (raw_bb[2] + raw_bb[3]) / 2
        if kind == "plate":
            M = Matrix.Translation(Vector((-cx, -cy, -(raw_bb[4] + PT))))
            exp_bb = (PLATE, PLATE, PT if n == 0 else PT + REL_H)
            exp_vol = VOL_EXP[plate]
        else:
            R = Matrix.Rotation(math.pi, 4, "X")
            tmp = Solid(obj, Matrix.Translation(Vector((-cx, -cy, 0))) @ R if False else R @ Matrix.Translation(Vector((-cx, -cy, 0))))
            zt = [tmp.top_z(40, 40), tmp.top_z(-40, -40), tmp.top_z(40, -40), tmp.top_z(-40, 40)]
            zflat = sum(zt) / len(zt)
            M = Matrix.Translation(Vector((0, 0, -zflat))) @ R @ Matrix.Translation(Vector((-cx, -cy, 0)))
            exp_bb = (COVER_OUT, COVER_OUT, COVER_H + COVER_LABEL_REL)
            exp_vol = VOL_EXP["cover"]
        solid = Solid(obj, M)
        print(f"=== {name}: bbox surowy X[{raw_bb[0]:.3f},{raw_bb[1]:.3f}] Y[{raw_bb[2]:.3f},{raw_bb[3]:.3f}] Z[{raw_bb[4]:.3f},{raw_bb[5]:.3f}]")
        vol, dims = general_checks(name, obj, solid, exp_bb, exp_vol)
        summary[name] = {"bbox_surowy": [round(v, 3) for v in raw_bb], "objetosc_cm3": round(vol, 3), "gabaryt": [round(v, 3) for v in dims],
                         "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest()}
        if kind == "plate":
            check_plate(name, plate, n, solid, layouts[plate])
        else:
            summary[name]["z_wierzch_plaski_po_obrocie"] = round(zflat, 4)
            check_cover(name, solid)
    check_k58()
    out = {"etap": "A", "iteracja": ITER, "blender": bpy.app.version_string, "pliki": summary, "wyniki": RESULTS}
    json.dump(out, open(os.path.join(REC, f"wyniki_A_iter{ITER}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    nie = [r for r in RESULTS if r["wynik"] == "NIE"]
    print(f"\n=== PODSUMOWANIE: {len(RESULTS)} sprawdzeń, NIE: {len(nie)}")
    for r in nie:
        print("  NIE", r["id"], r["plik"], r["wartosc"][:120])

main()
