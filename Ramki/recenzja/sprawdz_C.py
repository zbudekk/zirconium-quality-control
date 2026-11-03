# -*- coding: utf-8 -*-
"""
Skrypt RECENZENTA — etap B (wkładka, rama dyfuzora, blat, korpus W/P, złożenie w .blend).
Napisany niezależnie, bez czytania ramka_generator.py.
Uruchomienie:
  "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b -P recenzja/sprawdz_B.py -- --iter 3
Wyniki: recenzja/wyniki_B_iter<n>.json, recenzja/relief_*.png, recenzja/log_B_iter<n>.txt (przez tee)
"""
import bpy, bmesh, json, math, os, sys, zlib, struct, hashlib
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



# ================= MAŁE CZĘŚCI (etap C) =================
import csv, re, struct as _struct

def check_tulejka(name, S):
    lst = [S.probe((0, 0, 1.5), False), S.probe((3.5, 0, 1.5), False), S.probe((4.8, 0, 1.5), True), S.probe((5.5, 0, 2), True),
           S.probe((5.85, 0, 2), True), S.probe((6.0, 0, 2), False), S.probe((0, -5.85, 2.5), True), S.probe((0, 6.0, 2.5), False), S.probe((6.8, 0, 2), False), S.probe((6.8, 0, 0.5), True), S.probe((8, 0, 0.5), False),
           S.probe((-4.8, 0, 1.5), True), S.probe((0, 4.8, 1.5), True), S.probe((0, -6.8, 0.5), True), S.probe((0, 6.8, 2), False), S.probe((0, 0, 0.5), False)]
    bb = S.bb; dims = (bb[1] - bb[0], bb[3] - bb[2], bb[5] - bb[4])
    ok = all(e["ok"] for e in lst) and all(abs(dims[i] - (15, 15, 3)[i]) <= 0.1 for i in range(3))
    # średnice z promieni: otwór na Z 1,5; walec na Z 2; kołnierz na Z 0,5
    def width(z, outward):
        if outward:
            h1 = S.first_hit((-30, 0, z), (1, 0, 0)); h2 = S.first_hit((30, 0, z), (-1, 0, 0))
        else:
            h1 = S.first_hit((0, 0, z), (1, 0, 0)); h2 = S.first_hit((0, 0, z), (-1, 0, 0))
        return (h1 - h2).length if h1 and h2 else None
    d_hole = width(1.5, False); d_cyl = width(2.0, True); d_fl = width(0.5, True)
    d_cyl_y = width_y = None
    h1 = S.first_hit((0, -30, 2.0), (0, 1, 0)); h2 = S.first_hit((0, 30, 2.0), (0, -1, 0)); d_cyl_y = (h1 - h2).length if h1 and h2 else None
    ok = ok and d_hole is not None and abs(d_hole - 8.2) <= 0.05 and d_cyl is not None and abs(d_cyl - 11.85) <= 0.05 and d_cyl_y is not None and abs(d_cyl_y - 11.85) <= 0.05 and d_fl is not None and abs(d_fl - 15) <= 0.05
    rec("K-52b", name, "ZAL" if ok else "NIE", f"{sum(e['ok'] for e in lst)}/{len(lst)} sond; gabaryt {dims[0]:.3f} × {dims[1]:.3f} × {dims[2]:.3f} (15 × 15 × 3 ± 0,1); z promieni: otwór ø{d_hole:.3f} (8,2), walec ø{d_cyl:.3f} X / ø{d_cyl_y:.3f} Y (11,85 ± 0,05; R52), kołnierz ø{d_fl:.3f} (15)", "P", lst)

def check_podkladka(name, S, t):
    z = t / 2
    lst = [S.probe((0, 0, z), False), S.probe((1.5, 0, z), False), S.probe((3, 0, z), True), S.probe((4.7, 0, z), False),
           S.probe((-3, 0, z), True), S.probe((0, 3, z), True), S.probe((0, -1.5, z), False)]
    bb = S.bb; dims = (bb[1] - bb[0], bb[3] - bb[2], bb[5] - bb[4])
    ok = all(e["ok"] for e in lst) and all(abs(dims[i] - (9, 9, t)[i]) <= 0.05 for i in range(3))
    h1 = S.first_hit((0, 0, z), (1, 0, 0)); h2 = S.first_hit((0, 0, z), (-1, 0, 0)); d_hole = (h1 - h2).length if h1 and h2 else None
    rec("K-52c", name, "ZAL" if ok else "NIE", f"{sum(e['ok'] for e in lst)}/{len(lst)} sond; gabaryt {dims[0]:.3f} × {dims[1]:.3f} × {dims[2]:.3f} (9 × 9 × {t} ± 0,05); otwór z promieni ø{d_hole:.3f} (3,4)", "P", lst)

# ================= K-57: arkusz zamówienia =================
def pl(s):
    return float(str(s).replace(",", ".").replace("\u00a0", "").strip())

def check_k57(vols, dims_all):
    path = os.path.join(WYN, "arkusze", "arkusz_zamowienia.csv")
    if not os.path.exists(path):
        rec("K-57", "arkusz_zamowienia.csv", "NIE", "brak pliku", "P"); return
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig"), delimiter=";"))
    q = P("sterowanie", "quantities"); mats = P("sterowanie", "materials")
    rmin, rmax, dye, smooth = P("sterowanie", "cost_rate_min"), P("sterowanie", "cost_rate_max"), P("sterowanie", "cost_dye_factor"), P("sterowanie", "cost_smooth_factor")
    notes = []; ok = True
    if len(rows) != 15:
        ok = False; notes.append(f"wierszy {len(rows)} ≠ 15")
    seen = set(); nprint = 0; sum_vol = 0; sum_min = 0; sum_max = 0; sum_pmin = 0; sum_pmax = 0
    maxdv = 0; maxdg = 0; maxdc = 0
    for r in rows:
        f = r["plik STL"].strip(); key = f[:-4]; qkey = f.replace("_v2.stl", "")
        seen.add(qkey)
        if not os.path.exists(os.path.join(WYN, "stl", f)):
            ok = False; notes.append(f"{f}: brak pliku"); continue
        if key not in vols:
            ok = False; notes.append(f"{f}: brak mojego pomiaru"); continue
        v = pl(r["objętość [cm³]"]); dv = abs(v - vols[key]); maxdv = max(maxdv, dv)
        if dv > 0.01:
            ok = False; notes.append(f"{f}: objętość {v} vs {vols[key]:.3f}")
        g = [pl(x) for x in re.split(r"[×x]", r["gabaryt X × Y × Z [mm]"])]
        dg = max(abs(g[i] - dims_all[key][i]) for i in range(3)); maxdg = max(maxdg, dg)
        if dg > 0.1:
            ok = False; notes.append(f"{f}: gabaryt {g} vs {dims_all[key]}")
        n = int(r["ilość"])
        if q.get(qkey) != n:
            ok = False; notes.append(f"{f}: ilość {n} vs quantities {q.get(qkey)}")
        if mats.get(qkey) != r["materiał"].strip():
            ok = False; notes.append(f"{f}: materiał '{r['materiał']}' vs '{mats.get(qkey)}'")
        if "bazow" in r["część"] or qkey in ("ramka_plytka_wieczorna", "ramka_plytka_poranna"):
            ok = False; notes.append(f"{f}: wiersz bazowej płytki")
        drukarnia = r["materiał"].strip().startswith("PA12 drukarnia")
        if drukarnia:
            nprint += 1
            cmin = v * n * rmin; cmax = v * n * rmax
            graf = "grafit" in r["kolor"]
            pmin = cmin * (dye * smooth if graf else 1); pmax = cmax * (dye * smooth if graf else 1)
            got = [pl(r[c]) for c in ("koszt najtańszy min [zł]", "koszt najtańszy max [zł]", "koszt pokazowy min [zł]", "koszt pokazowy max [zł]")]
            dc = max(abs(got[0] - cmin), abs(got[1] - cmax), abs(got[2] - pmin), abs(got[3] - pmax)); maxdc = max(maxdc, dc)
            if dc > 0.01:
                ok = False; notes.append(f"{f}: koszt {got} vs wzór {[round(cmin, 2), round(cmax, 2), round(pmin, 2), round(pmax, 2)]}")
            sum_vol += v * n; sum_min += cmin; sum_max += cmax; sum_pmin += pmin; sum_pmax += pmax
        else:
            if any(r[c].strip() for c in ("koszt najtańszy min [zł]", "koszt najtańszy max [zł]", "koszt pokazowy min [zł]", "koszt pokazowy max [zł]")):
                ok = False; notes.append(f"{f}: druk własny z kosztem")
    if nprint != 10:
        ok = False; notes.append(f"pozycji drukarni {nprint} ≠ 10")
    missing = set(q) - seen
    if missing:
        ok = False; notes.append(f"brak w arkuszu: {missing}")
    md = open(os.path.join(WYN, "arkusze", "arkusz_zamowienia.md"), encoding="utf-8").read()
    if "STEP" not in md or "FreeCAD" not in md:
        ok = False; notes.append("brak uwagi STEP/FreeCAD w .md")
    # sumy w .md
    m = re.search(r"\|\s*10 pozycji × ilości\s*\|\s*([\d\s,\.]+)\s*\|\s*([\d\s]+)–([\d\s]+)\s*\|\s*([\d\s]+)–([\d\s]+)\s*\|", md)
    sums_ok = None
    if m:
        got = [pl(m.group(1)), pl(m.group(2)), pl(m.group(3)), pl(m.group(4)), pl(m.group(5))]
        exp_ = [sum_vol, sum_min, sum_max, sum_pmin, sum_pmax]
        sums_ok = abs(got[0] - exp_[0]) <= 0.05 and all(abs(got[i] - exp_[i]) <= 1.0 for i in range(1, 5))
        if not sums_ok:
            ok = False; notes.append(f"sumy .md {got} vs moje {[round(e, 2) for e in exp_]}")
    rec("K-57", "arkusz_zamowienia.csv/.md", "ZAL" if ok else "NIE",
        f"{len(rows)} wierszy ({nprint} drukarnia); max |Δobjętość| {maxdv:.4f} cm³, |Δgabaryt| {maxdg:.3f} mm, |Δkoszt| {maxdc:.3f} zł; ilości i materiały = parametry.json; "
        f"sumy drukarni: obj {sum_vol:.2f} cm³, najtańszy {sum_min:.0f}–{sum_max:.0f} zł, pokazowy {sum_pmin:.0f}–{sum_pmax:.0f} zł (zgodne z .md: {sums_ok}); STEP/FreeCAD: tak" + ("; BŁĘDY: " + "; ".join(notes) if notes else ""), "P")

# ================= K-60: rendery, raport, arkusz wymiarów, LICZONE =================
def png_size(p):
    with open(p, "rb") as f:
        head = f.read(24)
    return _struct.unpack(">II", head[16:24])

def check_k60():
    notes = []; ok = True
    for n in ("render_rozstrzelony.png", "render_zlozony.png", "render_plytki.png"):
        p = os.path.join(WYN, "render", n)
        if not os.path.exists(p):
            ok = False; notes.append(f"brak {n}"); continue
        w, h = png_size(p)
        notes.append(f"{n} {w}×{h}")
        if w < 1600 or h < 1200:
            ok = False
    rep = open(os.path.join(WYN, "raport", "raport_wykonawcy_C_iter1.md"), encoding="utf-8").read()
    sec3 = rep.split("## 3.")[1].split("## 4.")[0] if "## 3." in rep else ""
    expected = ["K‑01", "K‑02", "K‑03", "K‑04", "K‑04b"] + [f"K‑{i:02d}" for i in range(5, 19)] + ["K‑20", "K‑22", "K‑23", "K‑24", "K‑25"] + [f"K‑{i}" for i in range(27, 41)] + \
               [f"K‑{i}" for i in range(42, 48)] + ["K‑44b", "K‑49", "K‑52b", "K‑52c", "K‑53", "K‑54", "K‑55", "K‑56", "K‑57", "K‑58", "K‑59", "K‑60"]
    missing = [k for k in expected if not re.search(r"^\|\s*" + re.escape(k) + r"\s*\(", sec3, re.M)]
    if missing:
        ok = False; notes.append(f"brak w raporcie: {missing}")
    else:
        notes.append(f"raport: wszystkie {len(expected)} K‑xx etapów A+B+C obecne")
    wym = open(os.path.join(WYN, "arkusze", "arkusz_wymiarow.md"), encoding="utf-8").read()
    m = re.search(r"```json\s*(\{.*?\})\s*```", wym, re.S)
    if m:
        try:
            dump = json.loads(m.group(1))
            diff = []
            for sec, d in PAR.items():
                if sec == "_meta":
                    continue
                for k, v in d.items():
                    dv = dump.get(sec, {}).get(k)
                    if dv is None or dv.get("value") != v.get("value"):
                        diff.append(f"{sec}.{k}")
            extra = [f"{s}.{k}" for s, d in dump.items() if s != "_meta" for k in d if k not in PAR.get(s, {})]
            if diff or extra:
                ok = False; notes.append(f"zrzut parametry.json ≠ plik: różnią się {diff[:10]}, nadmiarowe {extra[:10]}")
            else:
                notes.append(f"zrzut parametry.json w arkusz_wymiarow.md zgodny ({sum(len(d) for s, d in dump.items() if s != '_meta')} kluczy)")
        except Exception as e:
            ok = False; notes.append(f"zrzut JSON nieparsowalny: {e}")
    else:
        # fallback: każdy klucz i wartość w tekście
        miss = [k for sec, d in PAR.items() if sec != "_meta" for k in d if k not in wym]
        if miss:
            ok = False; notes.append(f"brak kluczy w zrzucie: {miss[:10]}")
        else:
            notes.append("zrzut parametry.json: wszystkie klucze obecne (tekstowo)")
    flat = {k: v for s, d in PAR.items() if s != "_meta" for k, v in d.items()}
    V = lambda k: flat[k]["value"]
    calc = {"panel_pcb_z": V("floor_t") + V("pi_standoff_h") + V("pi_stack_h") + V("pi_clearance_top") + V("panel_bottom_parts_h"),
            "blat_top_z": V("panel_pcb_z") + V("panel_pcb_t") + V("panel_led_h") + V("led_gap") + V("diffuser_t"),
            "korpus_h": V("blat_top_z") - V("blat_t"), "panel_standoff_l": V("panel_pcb_z") - V("floor_t") - V("panel_pad_h"),
            "cover_inner_h": V("max_work_height") - V("socket_depth") + 4, "snap_pocket_z": V("korpus_h") - 7, "snap_hook_z": V("korpus_h") - 6.75,
            "blat_screw_z": V("korpus_h") - 4.6, "label_pos_z": V("korpus_h") - 8.6}
    bad = {k: (round(c, 3), V(k)) for k, c in calc.items() if abs(c - V(k)) > 0.01}
    if bad:
        ok = False; notes.append(f"LICZONE niezgodne: {bad}")
    else:
        notes.append("LICZONE 9/9 zgodne ze wzorami; " + ", ".join(f"{k} {V(k)}" for k in calc))
    for n in ("README.md", "do_v3.md"):
        if not os.path.exists(os.path.join(WYN, n)):
            ok = False; notes.append(f"brak {n}")
    rd = open(os.path.join(WYN, "README.md"), encoding="utf-8").read()
    if not re.search(r"^cd <PC>\\Desktop\\Ramki", rd, re.M):
        ok = False; notes.append("README: polecenie nie zaczyna się od cd")
    rec("K-60", "render/raport/arkusze", "ZAL" if ok else "NIE", "; ".join(notes) + "; treść renderu rozstrzelonego (lista §11) — ocena wizualna recenzenta w raporcie", "P")

# ================= main =================
def main():
    summary = {}
    small = [("ramka_tulejka_dc_v2", (15, 15, 3), 0.24, None), ("ramka_podkladka_panelu_05_v2", (9, 9, 0.5), 0.03, 0.5),
             ("ramka_podkladka_panelu_1_v2", (9, 9, 1.0), 0.05, 1.0), ("ramka_podkladka_panelu_2_v2", (9, 9, 2.0), 0.11, 2.0)]
    vols = {}; dims_all = {}
    for name, exp_bb, exp_vol, t in small:
        path = os.path.join(WYN, "stl", name + ".stl")
        if not os.path.exists(path):
            rec("K-01", name, "NIE", "brak pliku", "B"); continue
        obj = import_stl(path); weld(obj)
        raw = bbox([v.co for v in obj.data.vertices])
        cx = (raw[0] + raw[1]) / 2; cy = (raw[2] + raw[3]) / 2
        S = Solid.from_object(obj, Matrix.Translation(Vector((-cx, -cy, -raw[4]))), name)
        print(f"=== {name}: bbox surowy X[{raw[0]:.3f},{raw[1]:.3f}] Y[{raw[2]:.3f},{raw[3]:.3f}] Z[{raw[4]:.3f},{raw[5]:.3f}]")
        vol, dims = general_checks(name, obj, S, exp_bb, exp_vol)
        vols[name] = vol; dims_all[name] = dims
        summary[name] = {"bbox_surowy": [round(v, 3) for v in raw], "objetosc_cm3": round(vol, 4), "gabaryt": [round(v, 3) for v in dims],
                         "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest()}
        if t is None:
            check_tulejka(name, S)
        else:
            check_podkladka(name, S, t)
    # objętości i gabaryty pozostałych części z moich przebiegów A/B (ten sam zestaw plików: SHA sprawdzone)
    for fn in ("wyniki_A_iterC1.json", "wyniki_B_iterC1.json"):
        p = os.path.join(REC, fn)
        if os.path.exists(p):
            d = json.load(open(p, encoding="utf-8"))
            for k, v in d["pliki"].items():
                if "objetosc_cm3" in v:
                    vols[k] = v["objetosc_cm3"]; dims_all[k] = v["gabaryt"]
                    summary.setdefault(k, {})["sha256_z_przebiegu"] = v.get("sha256")
    # kontrola: SHA z przebiegów A/B = SHA plików teraz
    stale = [k for k, v in summary.items() if "sha256_z_przebiegu" in v and os.path.exists(os.path.join(WYN, "stl", k + ".stl"))
             and v["sha256_z_przebiegu"] != hashlib.sha256(open(os.path.join(WYN, "stl", k + ".stl"), "rb").read()).hexdigest()]
    canon = {}
    pc = os.path.join(REC, "wyniki_C_iter2_sha.json")
    if os.path.exists(pc):
        canon = {k.split("/")[-1][:-4]: v["trojkaty_rowne"] for k, v in json.load(open(pc, encoding="utf-8"))["kanonicznie_vs_powtorka"].items()}
    stale_canon = [k for k in stale if canon.get(k)]
    stale = [k for k in stale if not canon.get(k)]
    rec("INFO-sha", "stl", "ZAL" if not stale else "NIE", f"pliki zmierzone w przebiegach A/B (C1) zgodne z obecnymi STL: {'tak' if not stale else stale}; inne bajty, ale identyczne trójkąty (K-59 kanonicznie): {stale_canon}", "-")
    check_k57(vols, dims_all)
    check_k60()
    out = {"etap": "C", "iteracja": ITER, "blender": bpy.app.version_string, "pliki": summary, "wyniki": RESULTS}
    json.dump(out, open(os.path.join(REC, f"wyniki_C_iter{ITER}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    nie = [r for r in RESULTS if r["wynik"] == "NIE"]
    print(f"\n=== PODSUMOWANIE: {len(RESULTS)} sprawdzeń, NIE: {len(nie)}")
    for r in nie:
        print("  NIE", r["id"], r["plik"], r["wartosc"][:400])

main()
