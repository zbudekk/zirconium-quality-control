# -*- coding: utf-8 -*-
"""
TRZECIE OKO — niezależna weryfikacja końcowa (bramka G4b) plików STL ramek świetlnych v2.

Uruchomienie:
  "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b -P recenzja_koncowa/trzecie_oko.py

Metoda (niezależna od generatora i protokołu):
  * STL wczytane z wyniki_v2/stl/ (orientacja druku); transformacja do układu złożeniowego D3
    ustalona przez dopasowanie wierzchołków do obiektów w wyniki_v2/ramka_v2.blend (kandydaci:
    przesunięcie, obrót 180° wokół X, obrót 180° wokół Y) i zweryfikowana KD‑drzewem (max odległość
    wierzchołek–wierzchołek) oraz bounding boxami wobec D3/D4.
  * Pomiary: promienie (BVHTree.ray_cast) na siatkach w układzie złożeniowym — cięciwy otworów,
    gabaryty zewnętrzne, cięciwy w materiale (ścianki), luzy = suma odległości z punktu w szczelinie
    do obu części w przeciwnych kierunkach.
  * Montaż: BVHTree.overlap + głębokość wnikania (wierzchołki jednej części wewnątrz drugiej, test
    normalną najbliższego punktu) na każdym kroku drogi wsuwania (krok 0,1 mm).
Wyniki: recenzja_koncowa/trzecie_oko_wyniki.json, recenzja_koncowa/tabele_auto.md, log na stdout.
"""
import bpy, bmesh, json, os, sys, math, time
from mathutils import Vector, Matrix, kdtree
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri

ROOT = r"<PC>\Desktop\Ramki"
STL_DIR = os.path.join(ROOT, "wyniki_v2", "stl")
BLEND = os.path.join(ROOT, "wyniki_v2", "ramka_v2.blend")
OUT_DIR = os.path.join(ROOT, "recenzja_koncowa")
TOL_DIM = 0.05
EPS_PEN = 0.05   # głębokość wnikania traktowana jako styk (sagitta tesselacji walca ø12 przy 32 segmentach = 0,029)

T0 = time.time()
def log(*a):
    print("[3oko %6.1fs]" % (time.time() - T0), *a)

# --------------------------------------------------------------------------- parametry
with open(os.path.join(ROOT, "parametry.json"), encoding="utf-8") as f:
    PRM_RAW = json.load(f)
P = {}
for g, sub in PRM_RAW.items():
    if g == "_meta":
        continue
    for k, v in sub.items():
        P[k] = v["value"] if isinstance(v, dict) and "value" in v else v
log("parametry.json: %d kluczy" % len(P))
with open(os.path.join(ROOT, "wyniki_v2", "json", "uklad_gniazd_wieczorna.json"), encoding="utf-8") as f:
    JSON_EV = json.load(f)
with open(os.path.join(ROOT, "wyniki_v2", "json", "uklad_gniazd_poranna.json"), encoding="utf-8") as f:
    JSON_MO = json.load(f)

# pochodne z D4 (liczone niezależnie z parametrów)
Z_FLOOR_TOP = P["floor_t"]
Z_PI_PCB = P["floor_t"] + P["pi_standoff_h"]
Z_PI_TOP = Z_PI_PCB + P["pi_stack_h"]
Z_PANEL_PARTS = Z_PI_TOP + P["pi_clearance_top"]
Z_PANEL_PCB = Z_PANEL_PARTS + P["panel_bottom_parts_h"]
Z_LED = Z_PANEL_PCB + P["panel_pcb_t"] + P["panel_led_h"]
Z_DIFF_BOT = Z_LED + P["led_gap"]
Z_BLAT_TOP = Z_DIFF_BOT + P["diffuser_t"]
Z_KORPUS_H = Z_BLAT_TOP - P["blat_t"]
Z_SHELF = Z_BLAT_TOP + P["insert_shelf_h"]
Z_INSERT_TOP = Z_BLAT_TOP + P["insert_h"]
Z_PLATE_TOP = Z_SHELF + P["plate_thickness"]
Z_COVER_TOP = Z_PLATE_TOP + P["cover_inner_h"] + P["cover_top_t"]
Z_COVER_BOT = Z_PLATE_TOP - P["cover_skirt_below"]
log("D4 niezależnie: panel_pcb_z=%g blat_top_z=%g korpus_h=%g (json: %g %g %g)" % (
    Z_PANEL_PCB, Z_BLAT_TOP, Z_KORPUS_H, P["panel_pcb_z"], P["blat_top_z"], P["korpus_h"]))

# --------------------------------------------------------------------------- wczytanie
bpy.ops.wm.open_mainfile(filepath=BLEND)
BLEND_OBJ = {}
for o in bpy.data.objects:
    if o.type == "MESH":
        m = o.matrix_world
        BLEND_OBJ[o.name] = [m @ v.co for v in o.data.vertices], [list(p.vertices) for p in o.data.polygons]

def bbox(verts):
    xs = [v.x for v in verts]; ys = [v.y for v in verts]; zs = [v.z for v in verts]
    return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))

STL_FILES = sorted(f for f in os.listdir(STL_DIR) if f.endswith(".stl"))
assert len(STL_FILES) == 17, STL_FILES
STL = {}   # nazwa -> dict(verts_local, polys)
for f in STL_FILES:
    bpy.ops.wm.stl_import(filepath=os.path.join(STL_DIR, f))
    o = bpy.context.selected_objects[0]
    verts = [v.co.copy() for v in o.data.vertices]
    polys = [list(p.vertices) for p in o.data.polygons]
    STL[f] = {"verts": verts, "polys": polys, "nverts": len(verts), "nfaces": len(polys)}
    bpy.data.objects.remove(o)
log("wczytano %d STL" % len(STL))

BLEND_NAME = {
    "ramka_blat_v2.stl": "blat", "ramka_korpus_W_v2.stl": "korpus_W", "ramka_korpus_P_v2.stl": "korpus_P",
    "ramka_wkladka_v2.stl": "wkladka", "ramka_pokrywka_v2.stl": "pokrywka", "ramka_tulejka_dc_v2.stl": "tulejka_dc",
    "ramka_podkladka_panelu_05_v2.stl": "podkladka_panelu_05", "ramka_podkladka_panelu_1_v2.stl": "podkladka_panelu_1",
    "ramka_podkladka_panelu_2_v2.stl": "podkladka_panelu_2",
    "ramka_plytka_wieczorna_v2.stl": "plytka_wieczorna", "ramka_plytka_wieczorna_n1_v2.stl": "plytka_wieczorna_n1",
    "ramka_plytka_wieczorna_n2_v2.stl": "plytka_wieczorna_n2", "ramka_plytka_wieczorna_n3_v2.stl": "plytka_wieczorna_n3",
    "ramka_plytka_poranna_v2.stl": "plytka_poranna", "ramka_plytka_poranna_n4_v2.stl": "plytka_poranna_n4",
    "ramka_plytka_poranna_n5_v2.stl": "plytka_poranna_n5", "ramka_plytka_poranna_n6_v2.stl": "plytka_poranna_n6",
}

# --------------------------------------------------------------------------- transformacje STL -> .blend
ROT_CANDS = {
    "przesuniecie": Matrix.Identity(3),
    "obrot_180_X": Matrix.Rotation(math.pi, 3, "X"),
    "obrot_180_Y": Matrix.Rotation(math.pi, 3, "Y"),
    "obrot_+90_Y": Matrix.Rotation(math.pi / 2, 3, "Y"),
    "obrot_-90_Y": Matrix.Rotation(-math.pi / 2, 3, "Y"),
    "obrot_+90_X": Matrix.Rotation(math.pi / 2, 3, "X"),
    "obrot_-90_X": Matrix.Rotation(-math.pi / 2, 3, "X"),
}
TRANSFORM = {}   # stl -> (nazwa, Matrix 4x4)
RES = {"transformacje": [], "pasowania": [], "wymiary": [], "scianki": [], "montaz": [], "uwagi": [], "blokujace": []}

def kd_of(verts):
    kd = kdtree.KDTree(len(verts))
    for i, v in enumerate(verts):
        kd.insert(v, i)
    kd.balance()
    return kd

for f, d in STL.items():
    bname = BLEND_NAME[f]
    bverts, bpolys = BLEND_OBJ[bname]
    kd = kd_of(bverts)
    best = None
    for rn, R in ROT_CANDS.items():
        rv = [R @ v for v in d["verts"]]
        mn, mx = bbox(rv); bmn, bmx = bbox(bverts)
        t = (bmn + bmx) / 2 - (mn + mx) / 2
        tv = [v + t for v in rv]
        maxd = max(kd.find(v)[2] for v in tv)
        if best is None or maxd < best[0]:
            best = (maxd, rn, R, t)
    maxd, rn, R, t = best
    M = Matrix.Translation(t) @ R.to_4x4()
    TRANSFORM[f] = (rn, M, maxd)
    same_n = (d["nverts"] == len(bverts) and d["nfaces"] == len(bpolys))
    RES["transformacje"].append({"stl": f, "obiekt_blend": bname, "typ": rn, "t": [round(c, 4) for c in t],
                                 "max_odleglosc_wierzcholkow": round(maxd, 6), "liczba_wierzch_zgodna": same_n})
    log("transformacja %-36s %-13s t=(%.3f,%.3f,%.3f) maxd=%.2e verts/faces zgodne=%s" % (f, rn, t.x, t.y, t.z, maxd, same_n))
    if maxd > 1e-3:
        RES["blokujace"].append({"gdzie": f, "opis": "STL nie odpowiada obiektowi w .blend (max odl. %.4f)" % maxd})

# korpus_P: w .blend przesunięty o +260 X; do złożenia używam transformacji korpusu W (identyczność)
# płytki: wszystkie w złożeniu na pozycji n1 (ta sama orientacja lokalna, ten sam gabaryt)
M_PLATE = TRANSFORM["ramka_plytka_wieczorna_n1_v2.stl"][1]
M_KORPUS = TRANSFORM["ramka_korpus_W_v2.stl"][1]

def world_mesh(f):
    rn, M, _ = TRANSFORM[f]
    if f.startswith("ramka_plytka"):
        M = M_PLATE
    if f.startswith("ramka_korpus"):
        M = M_KORPUS
    if f.startswith("ramka_podkladka"):
        M = Matrix.Identity(4)  # podkładki poza złożeniem (w .blend odsunięte); mierzone lokalnie
    return [M @ v for v in STL[f]["verts"]], STL[f]["polys"]

class Part:
    def __init__(self, name, verts, polys):
        self.name = name
        self.verts = verts
        self.polys = polys
        self.tris = [[(pl[0], pl[k], pl[k + 1]) for k in range(1, len(pl) - 1)] for pl in polys]
        self.bvh = BVHTree.FromPolygons(verts, polys, all_triangles=False)
        self.mn, self.mx = bbox(verts)
    def moved(self, dv):
        return Part(self.name, [v + dv for v in self.verts], self.polys)

PARTS = {}
for f in STL_FILES:
    v, p = world_mesh(f)
    PARTS[f] = Part(f, v, p)
    mn, mx = PARTS[f].mn, PARTS[f].mx
    log("złożenie %-36s bbox (%.2f,%.2f,%.2f)-(%.2f,%.2f,%.2f)" % (f, mn.x, mn.y, mn.z, mx.x, mx.y, mx.z))
PROXY = {}
for n, (v, p) in BLEND_OBJ.items():
    if n.startswith("proxy_"):
        PROXY[n] = Part(n, v, p)
# odbiornik USB w .blend stoi przy korpusie P (+260 X) -> do złożenia przy korpusie na origin
PROXY["proxy_odbiornik_usb"] = PROXY["proxy_odbiornik_usb"].moved(Vector((-260, 0, 0)))

# weryfikacja położeń wobec D3/D4
def chk_bbox(name, part, exp_min, exp_max, what):
    ok = True
    for i, (a, b) in enumerate(zip(part.mn, exp_min)):
        if b is not None and abs(a - b) > TOL_DIM: ok = False
    for i, (a, b) in enumerate(zip(part.mx, exp_max)):
        if b is not None and abs(a - b) > TOL_DIM: ok = False
    RES["transformacje"].append({"stl": name, "sprawdzenie_D3D4": what, "bbox_min": [round(c, 3) for c in part.mn],
                                 "bbox_max": [round(c, 3) for c in part.mx], "ok": ok})
    if not ok:
        RES["blokujace"].append({"gdzie": name, "opis": "bbox w złożeniu niezgodny z D3/D4: %s; jest %s..%s" % (what, [round(c, 3) for c in part.mn], [round(c, 3) for c in part.mx])})
    log("D3/D4 %-30s %s -> %s" % (name, what, "OK" if ok else "NIEZGODNE"))

chk_bbox("korpus_W", PARTS["ramka_korpus_W_v2.stl"], (-100, -100 - P["label_relief_h"], 0), (100, 100, Z_KORPUS_H), "korpus 200x200, dno Z0, wierzch korpus_h, napis 0,6 na przodzie")
chk_bbox("korpus_P", PARTS["ramka_korpus_P_v2.stl"], (-100, -100 - P["label_relief_h"], 0), (100, 100, Z_KORPUS_H), "korpus P jak W")
chk_bbox("blat", PARTS["ramka_blat_v2.stl"], (-100, -100, Z_KORPUS_H - P["blat_skirt_h"]), (100, 100, Z_BLAT_TOP), "blat wierzch blat_top_z, kołnierz 10 w dół")
chk_bbox("wkladka", PARTS["ramka_wkladka_v2.stl"], (-65, -52.3, Z_BLAT_TOP - P["tab_pin_h"]), (65, P["tab_end_y"], Z_BLAT_TOP + P["insert_shelf_h"] + P["orient_post_h"]), "wkładka: spód ramy na blat_top_z, kołki 3,5 w dół, kołek orient. do 71,1")
chk_bbox("plytka_n1", PARTS["ramka_plytka_wieczorna_n1_v2.stl"], (-48, -48, Z_SHELF), (48, 48, Z_PLATE_TOP + P["number_relief_h"]), "płytka: spód na półce 66,1, wierzch 74,1 + relief 0,6")
chk_bbox("pokrywka", PARTS["ramka_pokrywka_v2.stl"], (-49.8, -49.8, Z_COVER_BOT), (49.8, 49.8, Z_COVER_TOP), "pokrywka: wierzch 90,1, dół kołnierza 70,1")
chk_bbox("tulejka", PARTS["ramka_tulejka_dc_v2.stl"], (P["dc_pos_x"] - P["dc_pocket_wall"] - P["dc_bush_flange_t"], P["dc_pos_y"] - 7.5, P["dc_pos_z"] - 7.5), (P["dc_pos_x"], P["dc_pos_y"] + 7.5, P["dc_pos_z"] + 7.5), "tulejka: kołnierz na licu x=-42 od strony kieszeni, walec w ścianie -42..-40")

# --------------------------------------------------------------------------- prymitywy pomiarowe
AX = {"X": Vector((1, 0, 0)), "Y": Vector((0, 1, 0)), "Z": Vector((0, 0, 1)),
      "-X": Vector((-1, 0, 0)), "-Y": Vector((0, -1, 0)), "-Z": Vector((0, 0, -1))}
def vec(d):
    return AX[d] if isinstance(d, str) else Vector(d).normalized()

def hit(part, p, d, maxd=1e6):
    loc, nrm, idx, dist = part.bvh.ray_cast(Vector(p), vec(d), maxd)
    return (loc, nrm, dist) if loc is not None else (None, None, None)

def surf(part, p, d):
    """współrzędna pierwszego trafienia wzdłuż osi d (skalar wzdłuż tej osi) albo None"""
    loc, nrm, dist = hit(part, p, d)
    if loc is None:
        return None
    dv = vec(d)
    return loc.dot(dv) * 1.0

def coord(part, p, d):
    """pierwsze trafienie jako współrzędna osi (np. 'X' -> loc.x)"""
    loc, nrm, dist = hit(part, p, d)
    if loc is None:
        return None
    dv = vec(d)
    ax = [abs(c) for c in dv]
    i = ax.index(max(ax))
    return loc[i]

def chord(part, p, d):
    """cięciwa: suma odległości do powierzchni w +d i -d z punktu p (w otworze lub w materiale)"""
    a = hit(part, p, d)[2]; b = hit(part, p, -vec(d))[2]
    if a is None or b is None:
        return None
    return a + b

def inside(part, p):
    """czy punkt jest wewnątrz materiału (normalna najbliższego punktu)"""
    loc, nrm, idx, dist = part.bvh.find_nearest(Vector(p))
    if loc is None:
        return False
    return (Vector(p) - loc).dot(nrm) < 0

def gap(partA, partB, p, d):
    """luz: z punktu p w szczelinie: odległość do A wzdłuż +d plus do B wzdłuż -d"""
    a = hit(partA, p, d)[2]; b = hit(partB, p, -vec(d))[2]
    if a is None or b is None:
        return None
    return a + b

def outer(part, p, d, L=400):
    """gabaryt zewnętrzny wzdłuż osi d przez punkt p: promienie z zewnątrz z obu stron"""
    dv = vec(d)
    a = hit(part, Vector(p) + dv * L, -dv)[2]; b = hit(part, Vector(p) - dv * L, dv)[2]
    if a is None or b is None:
        return None
    return 2 * L - a - b

# --------------------------------------------------------------------------- rejestracja wyników
def fit(para, miejsce, plan, zmierz, regula, uwaga="", tol=TOL_DIM, blok_poza_regula=None):
    """blok_poza_regula: (lo, hi) zakres dopuszczalny reguły 4.8 albo None"""
    plan = round(plan, 3)
    if zmierz is None:
        werdykt = "BRAK POMIARU"
    else:
        werdykt = "OK" if abs(zmierz - plan) <= tol else "ROZNICA"
        if blok_poza_regula is not None and not (blok_poza_regula[0] - 0.01 <= zmierz <= blok_poza_regula[1] + 0.01):
            werdykt += " / POZA REGULA 4.8"
    RES["pasowania"].append({"para": para, "miejsce": miejsce, "luz_plan": plan, "luz_zmierzony": None if zmierz is None else round(zmierz, 3),
                             "regula": regula, "werdykt": werdykt, "uwaga": uwaga})
    if werdykt != "OK":
        RES["blokujace"].append({"gdzie": para + " / " + miejsce, "opis": "luz plan %s, zmierzony %s (%s) %s" % (plan, None if zmierz is None else round(zmierz, 3), regula, uwaga), "typ": "pasowanie", "werdykt": werdykt})
    log("PAS %-34s %-42s plan=%-7s zm=%-8s %s" % (para, miejsce, plan, "None" if zmierz is None else "%.3f" % zmierz, werdykt))
    return zmierz

def dim(stl, wymiar, param, oczek, zmierz, metoda="", tol=TOL_DIM):
    if zmierz is None:
        w = "BRAK POMIARU"; roz = None
    else:
        roz = zmierz - oczek
        w = "OK" if abs(roz) <= tol else "ROZNICA"
    RES["wymiary"].append({"stl": stl, "wymiar": wymiar, "parametr": param, "oczekiwane": oczek, "zmierzone": None if zmierz is None else round(zmierz, 3),
                           "roznica": None if roz is None else round(roz, 3), "metoda": metoda, "werdykt": w})
    if w != "OK":
        RES["blokujace"].append({"gdzie": stl + " / " + wymiar, "opis": "oczekiwane %s (%s), zmierzone %s, metoda %s" % (oczek, param, zmierz, metoda), "typ": "wymiar"})
    if w != "OK":
        log("DIM %-30s %-44s oczek=%-8s zm=%-8s %s" % (stl[:30], wymiar[:44], oczek, zmierz, w))
    return zmierz

def wall(stl, miejsce, oczek, zmierz, punkt, min_req=1.5, uwaga=""):
    if zmierz is None:
        w = "BRAK POMIARU"
    else:
        w = "OK" if abs(zmierz - oczek) <= TOL_DIM else "ROZNICA"
        if zmierz < min_req - 0.01:
            w += " / < %g" % min_req
    RES["scianki"].append({"stl": stl, "miejsce": miejsce, "oczekiwane": oczek, "zmierzone": None if zmierz is None else round(zmierz, 3), "punkt": [round(c, 2) for c in punkt], "min": min_req, "werdykt": w, "uwaga": uwaga})
    if w != "OK":
        RES["blokujace"].append({"gdzie": stl + " / ścianka " + miejsce, "opis": "oczekiwane %s, zmierzone %s w %s %s" % (oczek, zmierz, [round(c, 2) for c in punkt], uwaga), "typ": "scianka"})
    log("WALL %-28s %-50s oczek=%-5s zm=%-7s %s" % (stl[:28], miejsce[:50], oczek, "None" if zmierz is None else "%.3f" % zmierz, w))

def uwaga(txt):
    RES["uwagi"].append(txt)
    log("UWAGA:", txt)

# --------------------------------------------------------------------------- części w złożeniu
KORPUS_W = PARTS["ramka_korpus_W_v2.stl"]; KORPUS_P = PARTS["ramka_korpus_P_v2.stl"]
BLAT = PARTS["ramka_blat_v2.stl"]; WK = PARTS["ramka_wkladka_v2.stl"]; POK = PARTS["ramka_pokrywka_v2.stl"]
TUL = PARTS["ramka_tulejka_dc_v2.stl"]
PLATES = [f for f in STL_FILES if f.startswith("ramka_plytka")]
PL1 = PARTS["ramka_plytka_wieczorna_n1_v2.stl"]
DYF = PROXY["proxy_dyfuzor"]; PANEL = PROXY["proxy_panel"]; PI = PROXY["proxy_pi_bonnet"]
DYST = [PROXY["proxy_dystans_%d" % i] for i in (1, 2, 3, 4)]
HALL = {k: PROXY["proxy_hall_" + k] for k in "ABC"}
MAG_A = PROXY["proxy_magnes_A"]; GDC = PROXY["proxy_gniazdo_dc"]; GUSB = PROXY["proxy_gniazdo_usb"]
WTYK_B = PROXY["proxy_wtyk_bonnet"]; ODB = PROXY["proxy_odbiornik_usb"]

# =========================================================================== 1. KARTA PASOWAŃ
log("=== 1. KARTA PASOWAŃ")
R_RUCH = (0.2, 0.3); R_WCISK = (0.1, 0.15); R_MAG = (0.1, 0.2)
zp = Z_PLATE_TOP; zs = Z_SHELF
c_in = P["insert_opening"] / 2; c_pl = P["plate_size"] / 2
luz_pl = (P["insert_opening"] - P["plate_size"]) / 2

# 1a płytka–wkładka: otwór 96,6 vs 96,0 — dla wszystkich 8 płytek, 3 punkty na bok
for f in PLATES:
    PL = PARTS[f]
    short = f.replace("ramka_plytka_", "").replace("_v2.stl", "")
    vals = []
    for y in (-30, 0, 30):
        vals.append(("lewy y=%g" % y, gap(WK, PL, (-(c_pl + luz_pl / 2), y, zs + 2.0), "-X")))
        vals.append(("prawy y=%g" % y, gap(WK, PL, ((c_pl + luz_pl / 2), y, zs + 2.0), "X")))
    for x in (-30, 30, -40, 40):
        vals.append(("przód x=%g" % x, gap(WK, PL, (x, -(c_pl + luz_pl / 2), zs + 2.0), "-Y")))
    for x in (-30, 0, 30):
        vals.append(("tył x=%g" % x, gap(WK, PL, (x, (c_pl + luz_pl / 2), zs + 2.0), "Y")))
    for nm, v in vals:
        fit("płytka %s – wkładka (otwór 96,6/96,0)" % short, nm, luz_pl, v, "ruchome 0,2–0,3", blok_poza_regula=R_RUCH)
    # półki: spód płytki vs wierzch półki (4 narożniki)
    for (x, y) in ((-38, -38), (-38, 38), (38, 38), (38, -38)):
        zb = coord(PL, (x, y, zs - 1.0), "Z")       # spód płytki od dołu
        zt = coord(WK, (x, y, zs + 10), "-Z")       # wierzch półki od góry
        fit("płytka %s – półka wkładki (styk Z)" % short, "narożnik (%g,%g)" % (x, y), 0.0, None if (zb is None or zt is None) else zb - zt, "styk (D5)")
    # kołek orientacyjny 4,4 w wycięciu 5
    kx0 = c_in - P["orient_post_gap"] - P["orient_post"]    # 43,4
    ky0 = -(c_in - P["orient_post_gap"] - P["orient_post"])  # -43,4
    nx = P["plate_size"] / 2 - P["notch_size"]                # 43
    luz_k_geo = round(kx0 - nx, 3)                              # 0,4 wg 4.6.4 + 4.1
    for z in (zs + 1.0, zs + 3.0):
        gx = gap(WK, PL, (nx + (kx0 - nx) / 2, -45.6, z), "X")
        gy = gap(WK, PL, (45.6, -nx - (kx0 - nx) / 2, z), "-Y")
        fit("płytka %s – kołek orient. 4,4 w wycięciu 5" % short, "X, Z=%g" % z, luz_k_geo, gx, "ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4)", uwaga="plan 4.11 podaje 0,3 (kołek + 2·0,3 = 5,0); z 4.6.4 (kołek 0,5 od ściany otworu) i 4.1 (płytka 0,3 od ściany) wynika 0,4 przy płytce wycentrowanej; 0,1…0,7 w zakresie luzu płytki", tol=TOL_DIM)
        fit("płytka %s – kołek orient. 4,4 w wycięciu 5" % short, "Y, Z=%g" % z, luz_k_geo, gy, "ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4)", tol=TOL_DIM)
    # kołek: luz do ścian otworu wkładki 0,5 (kołek vs własna rama) — wymiar, nie pasowanie; górna krawędź kołka pod pokrywką
    # czujniki Halla (proxy) pod spodem płytki: szczelina 1,0
    for k, (cx_, cy_) in (("A", (-42, -42)), ("B", (-42, 42)), ("C", (42, 42))):
        H = HALL[k]
        qx, qy = cx_ - math.copysign(1.7, cx_), cy_ - math.copysign(2.3, cy_)   # w obrysie czujnika 4×5, poza kieszenią magnesu ø5,2
        ht = coord(H, (qx, qy, 80), "-Z")
        pb = coord(PL, (qx, qy, zs - 0.5), "Z")
        fit("płytka %s – czujnik Halla %s (proxy)" % (short, k), "szczelina Z: spód płytki − wierzch czujnika w (%g,%g)" % (qx, qy), 1.0, None if (ht is None or pb is None) else pb - ht, "D5: 1,0")
        if f == "ramka_plytka_wieczorna_n1_v2.stl" and k == "A":
            mbot = coord(MAG_A, (-42, -42, 60), "Z")
            fit("płytka n1 – magnes A – czujnik Halla A (proxy)", "spód magnesu − wierzch czujnika", 1.2, None if (ht is None or mbot is None) else mbot - coord(H, (-42, -42, 80), "-Z"), "D5: 0,2 + 1,0 = 1,2 (≤ 4)")
    # magnes A (proxy) w kieszeni płytki ø5,2
    if f == "ramka_plytka_wieczorna_n1_v2.stl":
        for d_ in ("X", "Y"):
            g = gap(PL, MAG_A, (-42 + (2.5 + 0.05) * (1 if d_ == "X" else 0), -42 + (2.5 + 0.05) * (1 if d_ == "Y" else 0), zs + 1.0), d_)
            fit("płytka n1 – magnes A ø5 w kieszeni ø5,2", "luz promieniowy %s" % d_, (P["magnet_pocket_d"] - P["magnet_d"]) / 2, g, "magnesy 0,1–0,2 (klejone)", blok_poza_regula=R_MAG)
        mt = coord(MAG_A, (-42, -42, 80), "-Z"); pc = coord(PL, (-42, -42, zs + 1.0), "Z")
        fit("płytka n1 – magnes A: sufit kieszeni", "Z", 0.0, None if (mt is None or pc is None) else pc - mt, "magnes dosunięty do dna kieszeni")
        mb = coord(MAG_A, (-42, -42, 60), "Z")
        fit("płytka n1 – magnes A: cofnięcie w kieszeni", "Z (spód magnesu − spód płytki)", P["magnet_pocket_depth"] - P["magnet_h"], None if mb is None else mb - zs, "D5: 0,2")

# 1b wkładka–blat: kołki ø3 w ø3,3 ślepych, magnesy ø5,4, uszy, rama na dyfuzorze
for sx in (-1, 1):
    px, py = sx * P["tab_pos_x"], P["tab_pin_y"]
    r_mid = (P["tab_pin_d"] + P["blat_pin_hole_d"]) / 4
    for z in (Z_BLAT_TOP - 1.0, Z_BLAT_TOP - 2.5):
        for d_, off in (("X", (r_mid, 0)), ("-X", (-r_mid, 0)), ("Y", (0, r_mid)), ("-Y", (0, -r_mid))):
            g = gap(BLAT, WK, (px + off[0], py + off[1], z), d_)
            fit("wkładka – blat: kołek ø3 w otworze ø3,3", "kołek x=%g, %s, Z=%g" % (px, d_, round(z, 2)), (P["blat_pin_hole_d"] - P["tab_pin_d"]) / 2, g, "wciskane 0,1–0,15", blok_poza_regula=R_WCISK)
    # koniec kołka vs dno otworu
    tip = coord(WK, (px, py, Z_BLAT_TOP - 10), "Z"); bot = coord(BLAT, (px, py, Z_BLAT_TOP - 0.5), "-Z")
    fit("wkładka – blat: kołek: koniec vs dno otworu ślepego", "kołek x=%g" % px, P["blat_pin_hole_depth"] - P["tab_pin_h"], None if (tip is None or bot is None) else tip - bot, "luz osiowy (R8: 3,8 − 3,5)")
    # stożek kołka: ø2 na końcu
    dtip = chord(WK, (px, py, Z_BLAT_TOP - P["tab_pin_h"] + 0.02), "X")
    dim("ramka_wkladka_v2.stl", "kołek ustalający x=%g: ø na końcu stożka" % px, "tab_pin_chamfer (ø3→ø2)", 2.0 + 0.02 * 2, dtip, "cięciwa 0,02 nad końcem", tol=0.08)
    # magnesy: otwór ucha ø5,4 i kieszeń blatu ø5,4 — współosiowość i luz dla magnesu ø5
    mx_, my_ = sx * P["tab_pos_x"], P["tab_magnet_y"]
    cxw = chord(WK, (mx_, my_, Z_BLAT_TOP + 1.5), "X"); cyw = chord(WK, (mx_, my_, Z_BLAT_TOP + 1.5), "Y")
    cxb = chord(BLAT, (mx_, my_, Z_BLAT_TOP - 1.0), "X"); cyb = chord(BLAT, (mx_, my_, Z_BLAT_TOP - 1.0), "Y")
    fit("wkładka – magnes ø5 w otworze ucha ø5,4", "x=%g, promieniowo" % mx_, (P["tab_magnet_hole_d"] - P["magnet_d"]) / 2, None if cxw is None else (cxw - P["magnet_d"]) / 2, "magnesy 0,1–0,2 (klejone)", blok_poza_regula=R_MAG)
    fit("blat – magnes ø5 w kieszeni ø5,4", "x=%g, promieniowo" % mx_, (P["blat_magnet_pocket_d"] - P["magnet_d"]) / 2, None if cxb is None else (cxb - P["magnet_d"]) / 2, "magnesy 0,1–0,2 (klejone)", blok_poza_regula=R_MAG)
    # środki otworów
    def center(part, p, d_):
        a = hit(part, p, d_)[2]; b = hit(part, p, "-" + d_ if not d_.startswith("-") else d_[1:])[2]
        if a is None or b is None: return None
        return Vector(p)[0 if d_ == "X" else 1] + (a - b) / 2
    cw = (center(WK, (mx_, my_, Z_BLAT_TOP + 1.5), "X"), center(WK, (mx_, my_, Z_BLAT_TOP + 1.5), "Y"))
    cb = (center(BLAT, (mx_, my_, Z_BLAT_TOP - 1.0), "X"), center(BLAT, (mx_, my_, Z_BLAT_TOP - 1.0), "Y"))
    if None not in cw and None not in cb:
        fit("wkładka – blat: współosiowość otworu magnesu i kieszeni", "x=%g (odległość środków XY)" % mx_, 0.0, math.hypot(cw[0] - cb[0], cw[1] - cb[1]), "współosiowe")
    # uszy na blacie / na dyfuzorze
    for (x, y, what, other) in ((sx * 56, 70, "ucho na dyfuzorze (y=70)", DYF), (sx * 56, 82.5, "ucho na blacie (y=82,5)", BLAT), (sx * 61, 92, "ucho na blacie (y=92)", BLAT)):
        eb = coord(WK, (x, y, Z_BLAT_TOP - 0.5), "Z"); ot = coord(other, (x, y, Z_BLAT_TOP + 10), "-Z")
        fit("wkładka – blat/dyfuzor: ucho leży płasko", "x=%g: %s" % (x, what), 0.0, None if (eb is None or ot is None) else eb - ot, "styk (R30)")
# rama na dyfuzorze (punkty poza rowkiem kablowym i wycięciem palcowym)
for (x, y) in ((30, -50.3), (-30, -50.3), (0, 49.0), (-49.0, 0), (49.0, 0), (-49.0, 30)):
    fb = coord(WK, (x, y, Z_BLAT_TOP - 0.5), "Z"); dt = coord(DYF, (x, y, Z_BLAT_TOP + 10), "-Z")
    fit("wkładka – dyfuzor: spód ramy na dyfuzorze", "(%g,%g)" % (x, y), 0.0, None if (fb is None or dt is None) else fb - dt, "styk (R30)")
# kołnierz pokrywki nad ramą wkładki
for (x, y) in ((30, -49.5), (-30, 49.5), (49.5, 20)):
    cb_ = coord(POK, (x, y, Z_COVER_BOT - 2), "Z"); wt = coord(WK, (x, y, Z_COVER_BOT + 1), "-Z")
    fit("pokrywka – wkładka: kołnierz nad ramą", "(%g,%g)" % (x, y), Z_COVER_BOT - Z_INSERT_TOP, None if (cb_ is None or wt is None) else cb_ - wt, "bez styku (4.11)")
# strzałki wkładki vs kołnierz pokrywki: najwyższy punkt reliefu strzałki vs dół kołnierza
arr_top = max([coord(WK, (x, -51.15, 80), "-Z") or 0 for x in (-32, 32)])
fit("pokrywka – wkładka: strzałki ▼ pod kołnierzem (XY rozłączne)", "szczyt strzałki Z vs dół kołnierza", Z_INSERT_TOP + P["number_relief_h"], arr_top, "4.11: relief do 70,2 na y −50…−52,3; kołnierz y −48,3…−49,8", tol=0.05)

# 1c dyfuzor–kieszeń blatu
for (p, d_) in (((80.5, 0, Z_BLAT_TOP - 1), "X"), ((-80.5, 0, Z_BLAT_TOP - 1), "-X"), ((0, 80.5, Z_BLAT_TOP - 1), "Y"), ((0, -80.5, Z_BLAT_TOP - 1), "-Y"), ((80.5, 50, Z_BLAT_TOP - 1), "X"), ((-50, -80.5, Z_BLAT_TOP - 1), "-Y")):
    fit("dyfuzor 160 – kieszeń blatu 162", "%s w %s" % (d_, p[:2]), (P["diffuser_pocket"] - P["diffuser_size"]) / 2, gap(BLAT, DYF, p, d_), "luz 1,0 (D13)")
for (x, y) in ((79.5, 0), (0, 79.5), (-79.5, 40)):
    db = coord(DYF, (x, y, Z_DIFF_BOT - 1), "Z"); pf = coord(BLAT, (x, y, Z_BLAT_TOP + 1), "-Z")
    fit("dyfuzor – półka kieszeni blatu (styk Z)", "(%g,%g)" % (x, y), 0.0, None if (db is None or pf is None) else db - pf, "styk; półka 2 mm (79…81)")
dt_ = coord(DYF, (40, 40, 80), "-Z"); bt_ = coord(BLAT, (90, 40, 80), "-Z")
fit("dyfuzor – blat: licowanie wierzchu", "Z", 0.0, None if (dt_ is None or bt_ is None) else dt_ - bt_, "licowany (R30)")

# 1d blat–korpus
for K, kn in ((KORPUS_W, "W"), (KORPUS_P, "P")):
    zc = Z_KORPUS_H - 5
    xs_ = 100 - P["wall_t"] - P["blat_skirt_clearance"] / 2  # 97,25
    for (p, d_) in (((xs_, 30, zc), "X"), ((xs_, -60, zc), "X"), ((xs_, 60, zc), "X"), ((-xs_, 30, zc), "-X"), ((-xs_, -60, zc), "-X"),
                    ((30, -xs_, zc), "-Y"), ((-30, -xs_, zc), "-Y"), ((80, -xs_, zc), "-Y"), ((30, xs_, zc), "Y"), ((-70, xs_, zc), "Y"), ((85, xs_, zc), "Y")):
        fit("blat – korpus %s: kołnierz 194,0 w 195" % kn, "%s w (%g,%g,%g)" % (d_, p[0], p[1], round(p[2], 1)), P["blat_skirt_clearance"], gap(K, BLAT, p, d_), "ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48)")
    # haczyki: prawy (x+, y=0), lewy, przedni (x=+50, y−), tylny (x=−50, y+)
    hz0 = Z_KORPUS_H - 6.75; hz1 = hz0 + P["snap_hook_hgt"]; pz0 = Z_KORPUS_H - 7; pz1 = pz0 + P["snap_pocket_h"]
    zm = (hz0 + hz1) / 2
    wall_in = 100 - P["wall_t"]  # 97,5
    for (nm, ax, sgn, along, at) in (("prawy", "X", 1, "Y", P["snap_side_y"]), ("lewy", "X", -1, "Y", P["snap_side_y"]), ("przedni", "Y", -1, "X", P["snap_front_x"]), ("tylny", "Y", 1, "X", P["snap_rear_x"])):
        def pt(r, z, t=at):
            return (sgn * r, t, z) if ax == "X" else (t, sgn * r, z)
        d_out = ("" if sgn > 0 else "-") + ax
        d_in = ("-" if sgn > 0 else "") + ax
        tip = coord(BLAT, pt(110, zm), d_in)            # czubek haczyka od zewnątrz (abs)
        wall_face = coord(K, pt(90, pz0 - 1.5), d_out)   # ściana wewn. poniżej kieszeni
        pocket_bot = coord(K, pt(wall_in + 0.5, zm), d_out)
        if None not in (tip, wall_face):
            fit("blat – korpus %s: haczyk %s — zahaczenie" % (kn, nm), "czubek %.3f − ściana wewn. %.3f" % (abs(tip), abs(wall_face)), P["snap_hook_h"] - P["blat_skirt_clearance"], abs(tip) - abs(wall_face), "zatrzask (R48: 0,8)")
        if None not in (tip, pocket_bot):
            fit("blat – korpus %s: haczyk %s — luz do dna kieszeni" % (kn, nm), "dno %.3f − czubek %.3f" % (abs(pocket_bot), abs(tip)), P["snap_pocket_depth"] - (P["snap_hook_h"] - P["blat_skirt_clearance"]), abs(pocket_bot) - abs(tip), "zatrzask (0,2)")
        # profil występu (promienie poziome co 0,01 w Z): start rampy, czubek, górna krawędź
        zs_list = [round(pz0 - 1.0 + 0.01 * i, 2) for i in range(0, int((pz1 + 1.0 - (pz0 - 1.0)) / 0.01) + 1)]
        prof = [(z, coord(BLAT, pt(110, z), d_in)) for z in zs_list]
        prof = [(z, None if x_ is None else abs(x_)) for z, x_ in prof]
        out_ = [z for z, x_ in prof if x_ is not None and x_ > 97.0 + 0.02]
        tipz = [z for z, x_ in prof if x_ is not None and x_ >= (97.0 + P["snap_hook_h"]) - 0.01]
        z_start = min(out_) if out_ else None; z_top = max(out_) if out_ else None; z_tip0 = min(tipz) if tipz else None
        pk_bot = coord(K, pt(wall_in + 0.5, zm), "-Z"); pk_top = coord(K, pt(wall_in + 0.5, zm), "Z")
        fit("blat – korpus %s: haczyk %s — luz pod występem (Z)" % (kn, nm), "start rampy %.2f − dno kieszeni %.2f" % (z_start or 0, pk_bot or 0), hz0 - pz0, None if None in (z_start, pk_bot) else z_start - pk_bot, "zatrzask (R47: 0,25)", tol=0.06)
        fit("blat – korpus %s: haczyk %s — luz nad występem (Z)" % (kn, nm), "sufit kieszeni %.2f − górna krawędź występu %.2f" % (pk_top or 0, z_top or 0), pz1 - hz1, None if None in (z_top, pk_top) else pk_top - z_top, "zatrzask (R47: 0,25)", tol=0.06)
        if kn == "W":
            dim("ramka_blat_v2.stl", "haczyk %s: dolna krawędź występu (start rampy) Z" % nm, "snap_hook_z", hz0, z_start, "profil promieniami co 0,01", tol=0.06)
            dim("ramka_blat_v2.stl", "haczyk %s: górna krawędź występu Z" % nm, "snap_hook_z + snap_hook_hgt", hz1, z_top, "profil promieniami co 0,01", tol=0.06)
            dim("ramka_blat_v2.stl", "haczyk %s: wysokość występu (z rampą)" % nm, "snap_hook_hgt", P["snap_hook_hgt"], None if None in (z_start, z_top) else z_top - z_start + 0.01, "profil", tol=0.06)
            dim("ramka_blat_v2.stl", "haczyk %s: rampa naprowadzająca (wysokość od startu do pełnego występu)" % nm, "4.4.2 „rampa od dołu” (bez liczby)", 1.0, None if None in (z_start, z_tip0) else z_tip0 - z_start, "profil; informacyjnie", tol=0.1)
            RES.setdefault("profil_haczyka", {})[nm] = [(z, x_) for z, x_ in prof[::10]]
        # szerokość kieszeni vs haczyk (wzdłuż 'along')
        pk = chord(K, pt(wall_in + 0.5, zm), along); hk = chord(BLAT, pt(abs(wall_face) + 0.4, zm), along)
        fit("blat – korpus %s: haczyk %s — szerokość 8 w kieszeni 10" % (kn, nm), "luz wzdłuż %s na stronę" % along, (P["snap_pocket_w"] - P["snap_hook_w"]) / 2, None if (pk is None or hk is None) else (pk - hk) / 2, "ruchome (1,0/stronę z planu)")
    # blat leży na wierzchu korpusu
    for (x, y) in ((98.75, 30), (-98.75, -30), (30, 98.75), (30, -98.75)):
        bu = coord(BLAT, (x, y, Z_KORPUS_H - 3), "Z"); kt = coord(K, (x, y, Z_KORPUS_H + 10), "-Z")
        fit("blat – korpus %s: spód blatu na wierzchu ściany" % kn, "(%g,%g)" % (x, y), 0.0, None if (bu is None or kt is None) else bu - kt, "styk")
    # wkręty tylne: otwór ø3,2 w ścianie vs otwór ø2,5 w słupku — współosiowość
    for sx in (-1, 1):
        x = sx * P["blat_screw_pitch"] / 2; z = Z_KORPUS_H - 4.6
        def cen(part, p, d_):
            a = hit(part, p, d_)[2]; b = hit(part, p, "-" + d_)[2]
            return None if (a is None or b is None) else Vector(p)[{"X": 0, "Z": 2}[d_]] + (a - b) / 2
        pw = (x, 98.0, z); pp = (x, 94.0, z)
        cw = (cen(K, pw, "X"), cen(K, pw, "Z")); cp = (cen(BLAT, pp, "X"), cen(BLAT, pp, "Z"))
        if None not in cw and None not in cp:
            fit("blat – korpus %s: wkręt x=%g — współosiowość otworów" % (kn, x), "ściana ø3,2 vs słupek ø2,5 (XZ)", 0.0, math.hypot(cw[0] - cp[0], cw[1] - cp[1]), "współosiowe (R7)")
        fit("blat – korpus %s: wkręt x=%g — ø w ścianie" % (kn, x), "cięciwa X", P["blat_screw_hole_d"], chord(K, pw, "X"), "przelot M3")
        fit("blat – korpus %s: wkręt x=%g — ø w słupku" % (kn, x), "cięciwa X", P["insert_hole_m3"], chord(BLAT, pp, "X"), "gwint formowany (R49)")
        # lico słupka (kołnierz zewn. 97,0) vs ściana 97,5
        fit("blat – korpus %s: lico słupka/kołnierza vs ściana" % kn, "x=%g, Y" % x, P["blat_skirt_clearance"], gap(K, BLAT, (x + 2.5, 97.25, z), "Y"), "0,5 (R48)")
    # PCB panelu vs spód blatu przy oknie
    pt_ = coord(PANEL, (79.5, 0, 70), "-Z"); bu_ = coord(BLAT, (79.5, 0, 56), "Z")
    fit("panel (proxy) – spód blatu przy oknie", "(79,5, 0)", Z_KORPUS_H - (Z_PANEL_PCB + P["panel_pcb_t"]), None if None in (pt_, bu_) else bu_ - pt_, "≥ 2 (K‑49)")

# 1e dystanse – stadiony / rowki; panel – dystanse
for i, (sx, sy) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1))):
    D = DYST[i]; cx, cy = sx * 60, sy * 60
    # punkt poza rowkiem (prostopadle do przekątnej) ale pod dystansem: przesunięcie (sx*1.5, -sy*1.5)
    px, py = cx + sx * 1.5, cy - sy * 1.5
    for K, kn in ((KORPUS_W, "W"), (KORPUS_P, "P")):
        padt = coord(K, (px, py, 30), "-Z"); dbot = coord(D, (px, py, 0.5), "Z")
        fit("dystans %d – stadion korpusu %s (styk Z)" % (i + 1, kn), "(%g,%g)" % (px, py), 0.0, None if None in (padt, dbot) else dbot - padt, "styk (R5, R50‑2)")
        fit("dystans %d – stadion korpusu %s: wierzch stadionu" % (i + 1, kn), "Z", P["floor_t"] + P["panel_pad_h"], padt, "3 + 1 = 4")
        # rowek 3,4 pod osią dystansu: cięciwa prostopadle do przekątnej w (cx,cy, 1.5)
        perp = Vector((-sx, sy, 0)).normalized()
        fit("dystans %d – rowek w dnie korpusu %s (szer. prostopadle do przekątnej)" % (i + 1, kn), "(%g,%g, Z 1,5)" % (cx, cy), P["panel_slot_w"], chord(K, (cx, cy, 1.5), perp), "rowek 3,4 (R50‑2)")
        diag = Vector((sx, sy, 0)).normalized()
        L_exp = (P["panel_slot_pitch_max"] - P["panel_slot_pitch_min"]) / 2 * math.sqrt(2) + P["panel_slot_w"]
        fit("dystans %d – rowek w dnie korpusu %s (długość wzdłuż przekątnej)" % (i + 1, kn), "(%g,%g, Z 1,5)" % (cx, cy), L_exp, chord(K, (cx, cy, 1.5), diag), "od (±55,±55) do (±65,±65) + 3,4")
        # rowek przelotowy: promień z góry w osi nie trafia w nic (dno przecięte)
        thr = hit(K, (cx, cy, 2.9), "-Z")[2]
        fit("dystans %d – rowek przelotowy przez dno korpusu %s" % (i + 1, kn), "promień −Z w osi z Z 2,9", 0.0, 0.0 if thr is None else 1.0, "0 = przelot (R50‑U20, bez pogłębienia)")
    # panel na dystansie
    ptop = coord(D, (px, py, 70), "-Z"); pb = coord(PANEL, (px, py, 50), "Z")
    fit("panel (proxy) – dystans %d (styk Z)" % (i + 1), "(%g,%g)" % (px, py), 0.0, None if None in (ptop, pb) else pb - ptop, "styk (R50‑7)")
    fit("panel (proxy) – dystans %d: wierzch dystansu" % (i + 1), "Z", Z_PANEL_PCB, ptop, "panel_pcb_z 54")
    fit("dystans %d: ø bryły zastępczej" % (i + 1), "cięciwa X w Z 30", P["standoff_d"], outer(D, (cx, cy, 30), "X", 20), "6,4 (sześciokąt 5,5)")
# stadion: wymiary mierzone z zewnątrz w Z 3,5
for K, kn in ((KORPUS_W, "W"), (KORPUS_P, "P")):
    for (sx, sy) in ((-1, -1), (1, 1)):
        cx, cy = sx * 60, sy * 60
        perp = Vector((-sx, sy, 0)).normalized(); diag = Vector((sx, sy, 0)).normalized()
        a = hit(K, Vector((cx, cy, 3.5)) + perp * 20, -perp)[2]; b = hit(K, Vector((cx, cy, 3.5)) - perp * 20, perp)[2]
        dim("ramka_korpus_%s_v2.stl" % kn, "stadion panelu (%g,%g): szerokość" % (cx, cy), "panel_pad_d", P["panel_pad_d"], None if None in (a, b) else 40 - a - b, "promienie z zewnątrz prostopadle do przekątnej, Z 3,5")
        a = hit(K, Vector((cx, cy, 3.5)) + diag * 20, -diag)[2]; b = hit(K, Vector((cx, cy, 3.5)) - diag * 20, diag)[2]
        dim("ramka_korpus_%s_v2.stl" % kn, "stadion panelu (%g,%g): długość" % (cx, cy), "panel_slot_pitch + panel_pad_d", 10 * math.sqrt(2) + P["panel_pad_d"], None if None in (a, b) else 40 - a - b, "promienie z zewnątrz wzdłuż przekątnej, Z 3,5")

# 1f Pi – bossy
for K, kn in ((KORPUS_W, "W"), (KORPUS_P, "P")):
    for (bx, by) in ((-46.5, -24.5), (11.5, -24.5), (-46.5, 24.5), (11.5, 24.5)):
        bt = coord(K, (bx + 2.5, by, 30), "-Z"); pb = coord(PI, (bx + 2.5, by, 1), "Z")
        fit("Pi (proxy) – boss korpusu %s (%g,%g): styk Z" % (kn, bx, by), "wierzch bossa vs spód PCB", 0.0, None if None in (bt, pb) else pb - bt, "styk")
        fit("Pi – boss korpusu %s (%g,%g): wierzch bossa" % (kn, bx, by), "Z", Z_PI_PCB, bt, "3 + 5 = 8")
        fit("Pi – boss korpusu %s (%g,%g): otwór ø" % (kn, bx, by), "cięciwa X w Z 6", P["insert_hole_m25"], chord(K, (bx, by, 6), "X"), "ø2,1 pod M2,5 formowany")
        hb = coord(K, (bx, by, 7.5), "-Z")
        fit("Pi – boss korpusu %s (%g,%g): głębokość otworu" % (kn, bx, by), "od wierzchu bossa", P["insert_depth_m25"], None if None in (hb, bt) else bt - hb, "5")
        fit("Pi – boss korpusu %s (%g,%g): ø bossa" % (kn, bx, by), "promienie z zewnątrz X w Z 6", P["pi_boss_d"], outer(K, (bx, by, 6), "X", 7), "ø8 (R48)")
    # otwory Pi (58 x 49 od narożnika 3,5) vs bossy: pozycje
    exp = [(P["pi_pos_x"] + P["pi_hole_edge"] + i * P["pi_hole_pitch_l"], P["pi_pos_y"] + P["pi_hole_edge"] + j * P["pi_hole_pitch_w"]) for i in (0, 1) for j in (0, 1)]
    for (ex, ey) in exp:
        a = hit(K, (ex, ey, 6), "X")[2]; b = hit(K, (ex, ey, 6), "-X")[2]; c = hit(K, (ex, ey, 6), "Y")[2]; d = hit(K, (ex, ey, 6), "-Y")[2]
        if None not in (a, b, c, d):
            fit("Pi – boss korpusu %s: oś otworu vs otwór Pi (%g,%g)" % (kn, ex, ey), "odległość środków XY", 0.0, math.hypot((a - b) / 2, (c - d) / 2), "współosiowe (R50‑6)")

# 1g gniazdo DC ø12 w prawej ścianie skrzynki; tulejka
for K, kn in ((KORPUS_W, "W"), (KORPUS_P, "P")):
    pc = (P["dc_pos_x"] - P["dc_pocket_wall"] / 2, P["dc_pos_y"], P["dc_pos_z"])
    dY = chord(K, pc, "Y"); dZ = chord(K, pc, "Z")
    fit("gniazdo DC – otwór ø12 w ścianie skrzynki (korpus %s)" % kn, "cięciwa Y", P["dc_hole_d"], dY, "ø12 (R50‑3)")
    fit("gniazdo DC – otwór ø12 w ścianie skrzynki (korpus %s)" % kn, "cięciwa Z", P["dc_hole_d"], dZ, "ø12 (R50‑3)")
    a = hit(K, pc, "Y")[2]; b = hit(K, pc, "-Y")[2]; c = hit(K, pc, "Z")[2]; d = hit(K, pc, "-Z")[2]
    if None not in (a, b, c, d):
        fit("gniazdo DC – oś otworu (korpus %s)" % kn, "środek vs (y 89, Z 30)", 0.0, math.hypot((a - b) / 2, (c - d) / 2), "oś (y 89, Z 30) wzdłuż X")
    wx = chord(K, (P["dc_pos_x"] - 1, P["dc_pos_y"] - 7.5 - 0.5, P["dc_pos_z"]), "X")
    wall("ramka_korpus_%s_v2.stl" % kn, "ścianka skrzynki DC z otworem ø12 (x −42…−40)", P["dc_pocket_wall"], wx, (P["dc_pos_x"] - 1, P["dc_pos_y"] - 8, P["dc_pos_z"]))
    # tulejka: walec ø12 w otworze ø12 (luz 0), kołnierz ø15 x 1 na licu x=-42
    bo = outer(TUL, (-41, P["dc_pos_y"], P["dc_pos_z"]), "Y", 20)
    fit("tulejka DC – otwór ø12 (korpus %s)" % kn, "(ø otworu − ø walca)/2", (P["dc_hole_d"] - P["dc_bush_outer_d"]) / 2, None if None in (dY, bo) else (dY - bo) / 2, "wciskane 0,1–0,15 (opis dc_bush_outer_d: „pasowanie wciskane 0,1”)", blok_poza_regula=R_WCISK, uwaga="dc_bush_outer_d = dc_hole_d = 12 → luz 0,0 z definicji parametrów")
    ff = coord(TUL, (-42.5, P["dc_pos_y"] + 7, P["dc_pos_z"]), "X"); wf = coord(K, (-60, P["dc_pos_y"] + 7, P["dc_pos_z"]), "X")
    fit("tulejka DC – kołnierz na licu ściany skrzynki (korpus %s)" % kn, "x kołnierza vs lico −42", 0.0, None if None in (ff, wf) else wf - ff, "styk (R50‑3)")
    # przelot ø8,2 (dla gniazda ø8) i proxy gniazda: nakrętka od wewnątrz
    fit("tulejka DC – otwór ø8,2 dla gwintu gniazda ø8", "cięciwa Y", (P["dc_bush_inner_d"] - 8) / 2, None if chord(TUL, (-41, P["dc_pos_y"], P["dc_pos_z"]), "Y") is None else (chord(TUL, (-41, P["dc_pos_y"], P["dc_pos_z"]), "Y") - 8) / 2, "0,1 (R50‑3)")
    nut_face = coord(GDC, (-80, P["dc_pos_y"] + 7, P["dc_pos_z"]), "X"); wall_in_face = coord(K, (-30, P["dc_pos_y"] + 7, P["dc_pos_z"]), "-X")
    fit("gniazdo DC (proxy) – nakrętka na ścianie od wnętrza (korpus %s)" % kn, "x nakrętki vs lico −40", 0.0, None if None in (nut_face, wall_in_face) else nut_face - wall_in_face, "styk (R50‑3)")
    # ścianka skrzynki nad otworem (Z 36 -> sufit wewn. 38)
    wall("ramka_korpus_%s_v2.stl" % kn, "prawa ściana skrzynki nad otworem ø12: materiał od góry otworu (Z 36) do wierzchu skrzynki (Z 40); do sufitu wewn. 38 zostaje 2", 4.0, chord(K, (P["dc_pos_x"] - 1, P["dc_pos_y"], P["dc_pos_z"] + 6 + 1.0), "Z"), (P["dc_pos_x"] - 1, P["dc_pos_y"], 37.0), uwaga="4.11: „Z 24…36 → 2 do sufitu wewn.”")
    dim("ramka_korpus_%s_v2.stl" % kn, "skrzynka DC: sufit wewnętrzny Z", "dc_pocket: 40 − 2", 38.0, coord(K, (P["dc_pocket_x_window"], 90, 26), "Z"), "promień +Z w świetle")
    # okno 51 x 24 i wnętrze skrzynki
    dim("ramka_korpus_%s_v2.stl" % kn, "kieszeń DC: okno X", "dc_pocket_w", P["dc_pocket_w"], chord(K, (P["dc_pocket_x_window"], 98.75, P["dc_pocket_z0"] + 12), "X"), "cięciwa X w ścianie tylnej")
    dim("ramka_korpus_%s_v2.stl" % kn, "kieszeń DC: okno Z", "dc_pocket_h", P["dc_pocket_h"], chord(K, (P["dc_pocket_x_window"], 98.75, P["dc_pocket_z0"] + 12), "Z"), "cięciwa Z w ścianie tylnej")
    dim("ramka_korpus_%s_v2.stl" % kn, "kieszeń DC: dolna krawędź okna Z", "dc_pocket_z0", P["dc_pocket_z0"], coord(K, (P["dc_pocket_x_window"], 98.75, P["dc_pocket_z0"] + 12), "-Z"), "promień −Z")
    dim("ramka_korpus_%s_v2.stl" % kn, "kieszeń DC: dno w świetle (y)", "100 − dc_pocket_depth", 100 - P["dc_pocket_depth"] + P["dc_pocket_wall"], coord(K, (P["dc_pocket_x_window"], 110, 26), "-Y"), "promień −Y przez okno (plan: skrzynka do y 78, w świetle 20 → 80)")
    dim("ramka_korpus_%s_v2.stl" % kn, "kieszeń DC: wnętrze X (ściana lewa skrzynki → prawa)", "4.11: −95,5…−42", 53.5, chord(K, (P["dc_pocket_x_window"], 96, 20), "X"), "cięciwa X w świetle (poza otworem ø12)")
    dim("ramka_korpus_%s_v2.stl" % kn, "kieszeń DC: wnętrze Z (dno → sufit)", "dc_pocket: 14…38", 24.0, chord(K, (P["dc_pocket_x_window"], 88, 26), "Z"), "cięciwa Z w świetle")
    # wtyki: proxy wtyk kątowy (26 od lica gniazda) i prosty (40 + 12) — lico gniazda = −42 − kołnierz tulejki 1 − flansza gniazda 2 = −45
    face_x = P["dc_pos_x"] - P["dc_pocket_wall"] - P["dc_bush_flange_t"] - 2.0
    left_in = coord(K, (-80, P["dc_pos_y"], P["dc_pos_z"]), "-X")
    fit("wtyk DC kątowy 26 – lewa ściana skrzynki (korpus %s)" % kn, "zapas X: lico gniazda −45 − 26 vs ściana", 27.5 - 3.0, None if left_in is None else (face_x - 26) - left_in, "4.11: 27,5 od lica −42 (tu lico −45: kołnierz tulejki 1 + flansza gniazda 2)")
    fit("wtyk DC prosty 40 + zagięcie 12 – lewa ściana skrzynki (korpus %s)" % kn, "zapas X liczony jak w 4.11 (od lica −42)", 1.5, None if left_in is None else (P["dc_pos_x"] - P["dc_pocket_wall"] - 52) - left_in, "4.11: −94 > −95,5 (1,5)")
    fit("wtyk DC prosty 40 + zagięcie 12 – lewa ściana skrzynki (korpus %s)" % kn, "zapas X od realnego lica gniazda −45 (kołnierz tulejki 1 + flansza gniazda 2) — INFORMACYJNIE", -1.5, None if left_in is None else (face_x - 52) - left_in, "informacyjnie; nie w 4.11", uwaga="wtyk prosty 40 mieści się tylko przy kablu zagiętym ciaśniej niż 12 (albo bez tulejki / cieńszej flanszy); rekomendowany wtyk kątowy (plan 5)")
    fit("wtyk ø11 w świetle okna (korpus %s): Z" % kn, "Z 24,5…35,5 w oknie 14…38", 24.5 - P["dc_pocket_z0"], (P["dc_pos_z"] - 5.5) - (coord(K, (P["dc_pocket_x_window"], 98.75, 26), "-Z") or 0), "4.11")

# 1h USB: okno 16 x 9 + rowki
for K, kn in ((KORPUS_W, "W"), (KORPUS_P, "P")):
    ux, uz = P["usb_pos_x"], P["usb_pos_z"]
    dim("ramka_korpus_%s_v2.stl" % kn, "okno USB X", "usb_cut_w", P["usb_cut_w"], chord(K, (ux, 98.75, uz), "X"), "cięciwa X")
    dim("ramka_korpus_%s_v2.stl" % kn, "okno USB Z", "usb_cut_h", P["usb_cut_h"], chord(K, (ux, 98.75, uz), "Z"), "cięciwa Z")
    for s in (-1, 1):
        sx0 = ux + s * (P["usb_slot_pitch_min"] / 2); sx1 = ux + s * (P["usb_slot_pitch_max"] / 2)
        smid = (sx0 + sx1) / 2
        L_slot = abs(sx1 - sx0) + P["usb_slot_w"]
        dim("ramka_korpus_%s_v2.stl" % kn, "rowek flanszy USB %s: długość X" % ("prawy" if s > 0 else "lewy"), "usb_slot_pitch_min/max + usb_slot_w", L_slot, chord(K, (smid, 98.75, uz), "X"), "cięciwa X")
        dim("ramka_korpus_%s_v2.stl" % kn, "rowek flanszy USB %s: wysokość Z" % ("prawy" if s > 0 else "lewy"), "usb_slot_w", P["usb_slot_w"], chord(K, (smid, 98.75, uz), "Z"), "cięciwa Z")
        # ścianka okno–rowek
        inner_end = ux + s * (P["usb_slot_pitch_min"] / 2 - P["usb_slot_w"] / 2)   # 50,1 / 69,9
        win_edge = ux + s * P["usb_cut_w"] / 2                                         # 52 / 68
        wall("ramka_korpus_%s_v2.stl" % kn, "ścianka okno USB – rowek %s" % ("prawy" if s > 0 else "lewy"), abs(win_edge - inner_end), chord(K, ((inner_end + win_edge) / 2, 98.75, uz), "X"), ((inner_end + win_edge) / 2, 98.75, uz))
    gb = PROXY["proxy_gniazdo_usb"]
    gbr = coord(gb, (ux, 120, uz), "-Y"); kin = coord(K, (ux, 50, 35), "Y")
    fit("gniazdo USB (proxy 16×20×14) – ściana korpusu %s" % kn, "tył bryły vs lico wewn. ściany (Y)", 0.0, None if None in (gbr, kin) else kin - gbr, "styk")
    fit("gniazdo USB (proxy) – dystans (60,60)", "odstęp Y (sześciokąt, tol 0,3)", 77.5 - 63.2, gap(gb, DYST[3], (60 + 1.0, 70, 24), "Y"), "4.11: ≥ 8,8", tol=0.3)

# 1i pokrywka–płytka (wszystkie 8 płytek)
for f in PLATES:
    PL = PARTS[f]; short = f.replace("ramka_plytka_", "").replace("_v2.stl", "")
    gz = zp - 0.9  # 73,2: nad rowkiem (72,6), pod fazą (73,6)
    gz2 = Z_COVER_BOT + 0.4  # 70,5: pod rowkiem (71,6)
    for (p, d_) in (((48.15, 20, gz), "X"), ((48.15, -30, gz2), "X"), ((-48.15, 20, gz), "-X"), ((-48.15, -30, gz2), "-X"), ((20, 48.15, gz), "Y"), ((-20, 48.15, gz2), "Y"), ((20, -48.15, gz), "-Y"), ((40, -48.15, gz2), "-Y")):
        fit("pokrywka – płytka %s: wnęka 96,6/96,0" % short, "%s w (%g,%g,%g)" % (d_, p[0], p[1], round(p[2], 1)), P["cover_clearance"], gap(POK, PL, p, d_), "ruchome 0,2–0,3", blok_poza_regula=R_RUCH)
    zg = zp - P["cover_groove_z"]  # 72,1
    for (nm, p_in, d_out, p_tip, p_edge) in (("prawy (y=0)", (47.4, 0, zg), "X", (0, 0, zg), (60, 0, gz)), ("lewy (y=0)", (-47.4, 0, zg), "-X", (0, 0, zg), (-60, 0, gz)),
                                                ("przedni (x=+25)", (25, -47.4, zg), "-Y", (25, 0, zg), (25, -60, gz)), ("tylny (x=−25)", (-25, 47.4, zg), "Y", (-25, 0, zg), (-25, 60, gz))):
        gbot = gap(POK, PL, p_in, d_out)
        fit("pokrywka – płytka %s: garb %s — luz do dna rowka" % (short, nm), "wzdłuż %s" % d_out, P["cover_groove_depth"] - P["cover_snap_bump"] + P["cover_clearance"], gbot, "zatrzask (0,4)")
        tip = coord(POK, p_tip, d_out); edge = coord(PL, p_edge, "-" + d_out if not d_out.startswith("-") else d_out[1:])
        fit("pokrywka – płytka %s: garb %s — zahaczenie" % (short, nm), "czubek garbu vs bok płytki", P["cover_snap_bump"] - P["cover_clearance"], None if None in (tip, edge) else abs(edge) - abs(tip), "zatrzask (0,4)")
        # luz Z garbu w rowku: garb 0,8 w rowku 1,0 — punkt 0,02 przed bokiem płytki (czubek półokrągły R 0,4: pełna wysokość dopiero od x 48,0)
        lat = 0 if d_out in ("X", "-X") else 1
        pz = list(p_in); pz[lat] = math.copysign(47.98, p_in[lat]); pz[2] = zg + P["cover_groove_w"] / 2 - 0.05
        gzt = gap(PL, POK, tuple(pz), "Z")
        pz[2] = zg - P["cover_groove_w"] / 2 + 0.05
        gzb = gap(POK, PL, tuple(pz), "Z")
        fit("pokrywka – płytka %s: garb %s — luz Z nad garbem" % (short, nm), "rowek 1,0 / garb 0,8", (P["cover_groove_w"] - P["cover_snap_hgt"]) / 2, gzt, "zatrzask (0,1)")
        fit("pokrywka – płytka %s: garb %s — luz Z pod garbem" % (short, nm), "rowek 1,0 / garb 0,8", (P["cover_groove_w"] - P["cover_snap_hgt"]) / 2, gzb, "zatrzask (0,1)")
    ct = coord(POK, (-46.5, 0, zp + 1), "Z"); ptop = coord(PL, (-46.5, 0, zp + 20), "-Z")
    fit("pokrywka – płytka %s: prześwit nad płytką" % short, "spód wierzchu pokrywki − wierzch płytki (−46,5, 0)", P["cover_inner_h"], None if None in (ct, ptop) else ct - ptop, "14 (D8)")

# 1j stos Pi+Bonnet (+taśma) vs spód strefy złączy panelu
pit = coord(PI, (0, 0, 40), "-Z"); pbot = coord(PANEL, (0, 0, 36), "Z")
fit("stos Pi+Bonnet (proxy) – spód elementów panelu", "(0,0) Z", P["pi_clearance_top"], None if None in (pit, pbot) else pbot - pit, "D4/R50‑1: ≥ 8; z taśmą HUB75 (+5) zostaje 3")
fit("stos Pi+Bonnet: szczyt", "Z", Z_PI_TOP, pit, "8 + 26 = 34")
# wtyk Bonnetu (proxy, −X) vs lewa ściana
fit("wtyk DC Bonnetu (−X, proxy) – lewa ściana korpusu W", "X", 97.5 - 90, gap(WTYK_B, KORPUS_W, (-93.75, 22, 28), "X"), "D10/R50‑6: 7,5")
# odbiornik USB vs korpus P i dystans
fit("odbiornik USB (proxy, korpus P) – prawa ściana", "X", 97.5 - 54, gap(KORPUS_P, ODB, (75, 0, 11), "X"), "4.11: do 62 vs 97,5")
# podkładki panelu: krążek ø9 z otworem ø3,4
for f in ("ramka_podkladka_panelu_05_v2.stl", "ramka_podkladka_panelu_1_v2.stl", "ramka_podkladka_panelu_2_v2.stl"):
    S = PARTS[f]; t = {"05": 0.5, "1": 1.0, "2": 2.0}[f.split("_")[3]]
    fit("podkładka %s – wkręt M3 w otworze ø3,4" % f.split("_")[3], "luz promieniowy", (P["panel_shim_hole_d"] - 3.0) / 2, (chord(S, (0, 0, t / 2), "X") - 3.0) / 2, "0,2")
    fit("podkładka %s – dystans ø6,4 / stadion 9" % f.split("_")[3], "ø zewn.", P["panel_shim_d"], outer(S, (0, 0, t / 2), "X", 10), "9 = szerokość stadionu")

# =========================================================================== 2. ZRZUT WYMIARÓW
log("=== 2. ZRZUT WYMIARÓW")
for f in STL_FILES:
    d = STL[f]; mn, mx = bbox(d["verts"])
    RES.setdefault("gabaryty", []).append({"stl": f, "gabaryt": [round(mx.x - mn.x, 3), round(mx.y - mn.y, 3), round(mx.z - mn.z, 3)], "min": [round(c, 3) for c in mn], "max": [round(c, 3) for c in mx], "wierzcholki": d["nverts"], "trojkaty": d["nfaces"]})

tan15 = math.tan(math.radians(P["socket_wall_angle"]))
for f in PLATES:
    PL = PARTS[f]; short = f.replace("ramka_", "").replace("_v2.stl", "")
    ev = "wieczorna" in f
    J = JSON_EV if ev else JSON_MO
    mn, mx = bbox(STL[f]["verts"])
    numbered = "_n" in f
    n = int(f.split("_n")[1][0]) if numbered else None
    dim(f, "gabaryt X", "plate_size", P["plate_size"], mx.x - mn.x, "bbox")
    dim(f, "gabaryt Y", "plate_size", P["plate_size"], mx.y - mn.y, "bbox")
    dim(f, "gabaryt Z", "plate_thickness (+ relief 0,6 w n)", P["plate_thickness"] + (P["number_relief_h"] if numbered else 0), mx.z - mn.z, "bbox")
    dim(f, "bok X (promienie)", "plate_size", P["plate_size"], outer(PL, (0, 20, zp - 4), "X"), "promienie z zewnątrz")
    dim(f, "bok Y (promienie)", "plate_size", P["plate_size"], outer(PL, (20, 0, zp - 4), "Y"), "promienie z zewnątrz")
    dim(f, "grubość (poza reliefem)", "plate_thickness", P["plate_thickness"], outer(PL, (0, -46.5, zp - 4), "Z"), "promienie z zewnątrz")
    dim(f, "wycięcie D: x od", "notch_size (48−5)", 48 - P["notch_size"], coord(PL, (47, -45.5, zp - 4), "-X"), "promień −X w wycięciu")
    dim(f, "wycięcie D: y do", "notch_size", -(48 - P["notch_size"]), coord(PL, (45.5, -47, zp - 4), "Y"), "promień +Y w wycięciu")
    thr = hit(PL, (45.5, -45.5, zp + 1), "-Z")[2]
    dim(f, "wycięcie D przelotowe", "4.1", 0.0, 0.0 if thr is None else 1.0, "promień −Z: 0 = przelot")
    for m in J["markers"]:
        zc = zp - 0.05
        dim(f, "stożek znacznika %s: ø 0,05 pod wierzchem" % m["corner"], "marker_cone_d", P["marker_cone_d"] - 2 * 0.05 * (P["marker_cone_d"] / 2) / P["marker_cone_depth"], chord(PL, (m["x"], m["y"], zc), "X"), "cięciwa X (stożek ø5 × 3 → 4,917)")
        tipz = coord(PL, (m["x"], m["y"], zp + 1), "-Z")
        dim(f, "stożek znacznika %s: głębokość" % m["corner"], "marker_cone_depth", P["marker_cone_depth"], None if tipz is None else zp - tipz, "promień −Z w osi", tol=0.1)
    for m in J["magnet_pockets"]:
        dim(f, "kieszeń magnesu %s: ø" % m["corner"], "magnet_pocket_d", P["magnet_pocket_d"], chord(PL, (m["x"], m["y"], zs + 1.0), "X"), "cięciwa X")
        cz = coord(PL, (m["x"], m["y"], zs + 1.0), "Z")
        dim(f, "kieszeń magnesu %s: głębokość" % m["corner"], "magnet_pocket_depth", P["magnet_pocket_depth"], None if cz is None else cz - zs, "promień +Z do sufitu")
        # materiał między sufitem kieszeni a wierzchołkiem stożka
        tipz = coord(PL, (m["x"], m["y"], zp + 1), "-Z")
        if cz is not None and tipz is not None:
            wall(f, "materiał stożek %s – kieszeń magnesu (Z4: 2,8)" % m["corner"], P["plate_thickness"] - P["marker_cone_depth"] - P["magnet_pocket_depth"], tipz - cz, (m["x"], m["y"], (tipz + cz) / 2))
    # dołki kodu: obecne wg numeru
    for i, dmp in enumerate(J["code_dimples"]):
        bit = 1 << i
        expected = True if not numbered else bool(n & bit)
        zt = coord(PL, (dmp["x"], dmp["y"], zp + 1), "-Z")
        depth = None if zt is None else zp - zt
        dim(f, "dołek kodu %s (%g,%g): głębokość (%s)" % (dmp["bit"], dmp["x"], dmp["y"], "oczekiwany" if expected else "brak"), "code_dimple_depth / D11", P["code_dimple_depth"] if expected else 0.0, depth, "promień −Z w osi dołka")
        if expected:
            dim(f, "dołek kodu %s: ø" % dmp["bit"], "code_dimple_d", P["code_dimple_d"], chord(PL, (dmp["x"], dmp["y"], zp - 0.5), "X"), "cięciwa X")
    # rowek pokrywki: dno x 47,2; wysokość 1,0; środek 2 pod wierzchem
    for (p, d_, exp_) in (((60, 20, zp - 2), "-X", 48 - P["cover_groove_depth"]), ((-60, 20, zp - 2), "X", -(48 - P["cover_groove_depth"])), ((20, 60, zp - 2), "-Y", 48 - P["cover_groove_depth"]), ((20, -60, zp - 2), "Y", -(48 - P["cover_groove_depth"]))):
        dim(f, "rowek pokrywki: dno (%s)" % d_, "cover_groove_depth", exp_, coord(PL, p, d_), "promień poziomy w Z −2")
    gzc = chord(PL, (47.6, 20, zp - 2), "Z")
    dim(f, "rowek pokrywki: wysokość", "cover_groove_w", P["cover_groove_w"], gzc, "cięciwa Z w rowku")
    gt = coord(PL, (47.6, 20, zp - 2), "Z")
    dim(f, "rowek pokrywki: górna krawędź pod wierzchem", "cover_groove_z − w/2", P["cover_groove_z"] - P["cover_groove_w"] / 2, None if gt is None else zp - gt, "promień +Z w rowku")
    # faza górna 0,5 i R1 pionowy
    dim(f, "faza górnej krawędzi: x boku na Z −0,25", "plate_top_chamfer", 48 - 0.25, coord(PL, (60, 20, zp - 0.25), "-X"), "promień −X 0,25 pod wierzchem (faza 0,5 × 45°)")
    diag = Vector((1, 1, 0)).normalized()
    cp = hit(PL, Vector((48, 48, zp - 4)) + diag * 5, -diag)[0]
    dim(f, "R pionowej krawędzi (naroże B/C): punkt na przekątnej", "plate_edge_r", 48 - P["plate_edge_r"] + P["plate_edge_r"] / math.sqrt(2), None if cp is None else cp.x, "promień wzdłuż przekątnej narożnika w Z −4", tol=0.05)
    # gniazda z JSON: każde: przelot ø3, dno Z −4, ø na wierzchu, rynienki: długość/szerokość i 4 otwory
    bad = 0; cnt_r = 0; cnt_t = 0
    for s in J["sockets"]:
        x, y = s["x"], s["y"]
        if s["type"] == "round":
            cnt_r += 1
            thr = hit(PL, (x, y, zp + 1), "-Z")[2]
            top_d = chord(PL, (x, y, zp - 0.05), "X")
            exp_top = s["d_top"] - 2 * 0.05 * tan15
            r_fl = s["d_bottom"] / 2 - 0.3
            fl = coord(PL, (x + r_fl, y, zp + 1), "-Z")
            hole = chord(PL, (x, y, zp - 6), "X")
            ok = (thr is None) and top_d is not None and abs(top_d - exp_top) <= TOL_DIM and fl is not None and abs((zp - fl) - s["depth"]) <= TOL_DIM and hole is not None and abs(hole - s["hole_d"]) <= TOL_DIM
            if not ok:
                bad += 1
                dim(f, "gniazdo id %d (%g,%g): przelot/ø góra/dno/otwór" % (s["id"], x, y), "JSON", 0, 1, "przelot=%s ø_góra=%s (oczek %.3f) dno=%s otwór=%s" % (thr is None, top_d, exp_top, None if fl is None else round(zp - fl, 3), hole))
        else:
            cnt_t += 1
            L = chord(PL, (x, y, zp - 0.05), "X"); W = chord(PL, (x, y, zp - 0.05), "Y")
            dim(f, "rynienka id %d: długość na wierzchu" % s["id"], "ev/mo_trough_l", s["l"] - 2 * 0.05 * tan15, L, "cięciwa X 0,05 pod wierzchem")
            dim(f, "rynienka id %d: szerokość na wierzchu" % s["id"], "ev/mo_trough_w", s["w"] - 2 * 0.05 * tan15, W, "cięciwa Y 0,05 pod wierzchem")
            fl = coord(PL, (x + 5, y + s["w"] / 2 - 2.5, zp + 1), "-Z")
            dim(f, "rynienka id %d: głębokość" % s["id"], "socket_depth", s["depth"], None if fl is None else zp - fl, "promień −Z")
            holes_ok = 0
            for k in range(s["hole_count"]):
                hx = x + (k - (s["hole_count"] - 1) / 2) * s["hole_pitch"]
                thr = hit(PL, (hx, y, zp + 1), "-Z")[2]
                hd = chord(PL, (hx, y, zp - 6), "X")
                if thr is None and hd is not None and abs(hd - s["hole_d"]) <= TOL_DIM:
                    holes_ok += 1
            dim(f, "rynienka id %d: otwory ø3 przelotowe w rozstawie %g" % (s["id"], s["hole_pitch"]), "trough_hole_count", s["hole_count"], holes_ok, "promienie −Z + cięciwy")
    dim(f, "gniazda okrągłe wg JSON: liczba zgodnych", "D6 (%d)" % cnt_r, cnt_r, cnt_r - bad, "wszystkie: przelot ø3, ø wierzchu, dno −4")
    exp_cnt = 24 if ev else 35
    dim(f, "gniazda okrągłe: liczba w JSON", "D6", exp_cnt, cnt_r, "JSON")
    dim(f, "rynienki: liczba w JSON", "D6", 2, cnt_t, "JSON")
    # JSON vs parametry (ev_rows/mo_rows)
    rows = P["ev_rows"] if ev else P["mo_rows"]
    exp_pos = set()
    for r in rows:
        for x in r["x"]:
            exp_pos.add((round(x, 3), round(r["y"], 3), r["type"], r.get("d", r.get("l"))))
    got = set((round(s["x"], 3), round(s["y"], 3), s["type"], s.get("d_top", s.get("l"))) for s in J["sockets"])
    dim(f, "JSON gniazd = parametry ev/mo_rows", "ev_rows/mo_rows", 0, len(exp_pos ^ got), "różnica zbiorów pozycji/typów/średnic")
    # relief numeru
    if numbered:
        zr = max([coord(PL, (P["number_pos_x"] + dx, P["number_pos_y"] + dy, zp + 5), "-Z") or 0 for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)])
        dim(f, "relief cyfry %d: wysokość nad wierzchem" % n, "number_relief_h", P["number_relief_h"], zr - zp, "max trafień −Z w polu 4×4 wokół (39,5, −44,5)")
        # obrys cyfry: skan
        xs_ = []; ys_ = []
        for dx in [i * 0.25 for i in range(-20, 21)]:
            for dy in [i * 0.25 for i in range(-16, 17)]:
                z_ = coord(PL, (P["number_pos_x"] + dx, P["number_pos_y"] + dy, zp + 5), "-Z")
                if z_ is not None and z_ > zp + 0.3:
                    xs_.append(P["number_pos_x"] + dx); ys_.append(P["number_pos_y"] + dy)
        if ys_:
            dim(f, "relief cyfry %d: wysokość znaku (Y)" % n, "number_text_h", P["number_text_h"], max(ys_) - min(ys_) + 0.25, "skan 0,25 mm", tol=0.3)
            dim(f, "relief cyfry %d: środek Y" % n, "number_pos_y", P["number_pos_y"], (max(ys_) + min(ys_)) / 2, "skan 0,25 mm", tol=0.3)
            dim(f, "relief cyfry %d: środek X" % n, "number_pos_x", P["number_pos_x"], (max(xs_) + min(xs_)) / 2, "skan 0,25 mm", tol=0.6)
            RES.setdefault("relief_cyfry", {})[f] = {"x": [min(xs_), max(xs_)], "y": [min(ys_), max(ys_)]}
    else:
        dim(f, "plik bazowy: brak reliefu (Z max = 8,0)", "4.1 (R4)", 0.0, mx.z - P["plate_thickness"], "bbox")
    # ścianka dołek kodu – rowek pokrywki (R47: 1,3 po przekątnej) i dołek – krawędź 2,0
    if (not numbered) or (n & 1):
        e = coord(PL, (-60, -36, zp - 0.6), "X")   # lewa krawędź płytki −48 (pod fazą 0,5)
        dd = coord(PL, (-45, -36, zp - 0.6), "-X")  # ściana dołka −46
        if None not in (e, dd):
            wall(f, "dołek kodu A – krawędź płytki (2,0; R3)", 2.0, dd - e, (-47, -36, zp - 0.5), min_req=1.5)
        # po przekątnej do rowka: dołek dno Z −1 przy x −46; rowek górna krawędź Z −1,5 przy x −47,2
        dz_ = coord(PL, (-45, -36, zp + 1), "-Z"); gx_ = coord(PL, (-60, -36, zp - 2), "X"); gt_ = coord(PL, (gx_ - 0.3, -36, zp - 2), "Z") if gx_ is not None else None
        if None not in (dz_, gx_, gt_, dd):
            wall(f, "dołek kodu A – rowek pokrywki po przekątnej (R47: 1,3 lokalnie, dopuszczone)", 1.3, math.hypot(dd - gx_, dz_ - gt_), (-46.6, -36, zp - 1.25), min_req=1.3, uwaga="R47(10): nie ścianka nośna; do_v3 #1")
    # ścianka między dołkami ø2 w rozstawie 3 (1,0; do_v3 #2)
    pairs_d = {None: [(-36, -33), (-33, -30)], 3: [(-36, -33)], 6: [(-33, -30)]}.get(n if numbered else None, [])
    for (ya, yb) in pairs_d:
        a_ = coord(PL, (-45, ya, zp - 0.6), "Y"); b_ = coord(PL, (-45, yb, zp - 0.6), "-Y")
        if None not in (a_, b_):
            wall(f, "ścianka między dołkami kodu y %g/%g (do_v3 #2: 1,0; głębokość 1, nie nośna)" % (ya, yb), P["code_dimple_pitch"] - P["code_dimple_d"], b_ - a_, (-45, (ya + yb) / 2, zp - 0.6), min_req=1.0, uwaga="do_v3 #2; dopuszczone w recenzji A")

# pokrywka
f = "ramka_pokrywka_v2.stl"; mn, mx = bbox(STL[f]["verts"])
exp_c = P["plate_size"] + 2 * P["cover_clearance"] + 2 * P["cover_skirt_t"]
dim(f, "gabaryt X", "plate_size + 2·cover_clearance + 2·cover_skirt_t", exp_c, mx.x - mn.x, "bbox")
dim(f, "gabaryt Y", "j.w.", exp_c, mx.y - mn.y, "bbox")
dim(f, "gabaryt Z", "cover_inner_h + cover_top_t + cover_skirt_below", P["cover_inner_h"] + P["cover_top_t"] + P["cover_skirt_below"], mx.z - mn.z, "bbox")
dim(f, "wnęka X", "plate_size + 2·cover_clearance", P["plate_size"] + 2 * P["cover_clearance"], chord(POK, (0, 20, Z_COVER_BOT + 5), "X"), "cięciwa X")
dim(f, "wnęka Y", "j.w.", P["plate_size"] + 2 * P["cover_clearance"], chord(POK, (20, 0, Z_COVER_BOT + 5), "Y"), "cięciwa Y")
dim(f, "grubość wierzchu", "cover_top_t", P["cover_top_t"], chord(POK, (15, 15, Z_COVER_TOP - 1), "Z"), "cięciwa Z w materiale")
wall(f, "kołnierz pokrywki (grubość)", P["cover_skirt_t"], chord(POK, (49.05, 20, Z_COVER_BOT + 5), "X"), (49.05, 20, Z_COVER_BOT + 5))
wall(f, "kołnierz pokrywki przy garbie (grubość za garbem)", P["cover_skirt_t"], chord(POK, (49.05, 0, Z_COVER_TOP - 10), "X"), (49.05, 0, Z_COVER_TOP - 10))
dim(f, "wierzch płaski (bez reliefu, R50‑U14)", "4.2", Z_COVER_TOP, coord(POK, (0, 0, Z_COVER_TOP + 5), "-Z"), "promień −Z")
dim(f, "wierzch pełny (bez otworów, R50‑U17)", "4.2", 1.0, 0.0 if hit(POK, (15, 0, Z_COVER_TOP + 5), "-Z")[2] is None else 1.0, "promień −Z w dawnym otworze: 1 = materiał")
zg = Z_COVER_TOP + P["cover_snap_z"]
for (nm, p, d_) in (("prawy", (0, 0, zg), "X"), ("lewy", (0, 0, zg), "-X"), ("przedni", (25, 0, zg), "-Y"), ("tylny", (-25, 0, zg), "Y")):
    dim(f, "garb %s: czubek" % nm, "48,3 − cover_snap_bump", 48.3 - P["cover_snap_bump"], abs(coord(POK, p, d_)), "promień poziomy w Z garbu")
    along = "Y" if d_ in ("X", "-X") else "X"
    q = list(p); q[0 if along == "X" else 1] = (q[0 if along == "X" else 1])
    tipp = hit(POK, p, d_)[0]
    if tipp is not None:
        inn = tipp + vec(d_) * 0.5
        dim(f, "garb %s: szerokość" % nm, "cover_snap_w", P["cover_snap_w"], chord(POK, inn, along), "cięciwa 0,5 za czubkiem (w korpusie garbu)", tol=0.3)
        dim(f, "garb %s: wysokość Z" % nm, "cover_snap_hgt", P["cover_snap_hgt"], chord(POK, inn, "Z"), "cięciwa Z 0,5 za czubkiem", tol=0.1)
        zc_ = hit(POK, inn, "Z")[0].z; zd_ = hit(POK, inn, "-Z")[0].z
        dim(f, "garb %s: środek Z (lokalnie −18)" % nm, "cover_snap_z", zg, (zc_ + zd_) / 2, "środek cięciwy Z", tol=0.1)
for (nm, y) in (("przedni", -49.05), ("tylny", 49.05)):
    dim(f, "wycięcie palcowe %s: szerokość" % nm, "cover_finger_w", P["cover_finger_w"], chord(POK, (0, y, Z_COVER_BOT + 1), "X"), "cięciwa X")
    dim(f, "wycięcie palcowe %s: wysokość" % nm, "cover_finger_h", P["cover_finger_h"], (coord(POK, (0, y, Z_COVER_BOT - 1), "Z") or 0) - Z_COVER_BOT, "promień +Z od dołu")
diag = Vector((1, 1, 0)).normalized()
cp = hit(POK, Vector((49.8, 49.8, Z_COVER_TOP - 10)) + diag * 5, -diag)[0]
dim(f, "R pionowej krawędzi 3: punkt na przekątnej", "cover_corner_r", 49.8 - 3 + 3 / math.sqrt(2), None if cp is None else cp.x, "promień wzdłuż przekątnej")

# wkładka
f = "ramka_wkladka_v2.stl"; mn, mx = bbox(STL[f]["verts"]); zb = Z_BLAT_TOP
dim(f, "gabaryt X", "2·65 (uszy)", 130.0, mx.x - mn.x, "bbox")
dim(f, "gabaryt Y", "52,3 + tab_end_y", 52.3 + P["tab_end_y"], mx.y - mn.y, "bbox")
dim(f, "gabaryt Z", "tab_pin_h + insert_shelf_h + orient_post_h", P["tab_pin_h"] + P["insert_shelf_h"] + P["orient_post_h"], mx.z - mn.z, "bbox")
dim(f, "rama zewn. X", "insert_opening + 2·insert_wall_w", P["insert_opening"] + 2 * P["insert_wall_w"], outer(WK, (0, 0, zb + 4), "X", 60), "promienie z zewnątrz")
dim(f, "rama zewn. Y (x=20)", "j.w.", P["insert_opening"] + 2 * P["insert_wall_w"], outer(WK, (20, 0, zb + 4), "Y", 60), "promienie z zewnątrz")
dim(f, "otwór X", "insert_opening", P["insert_opening"], chord(WK, (0, 0, zb + 4), "X"), "cięciwa X")
dim(f, "otwór Y (x=20)", "insert_opening", P["insert_opening"], chord(WK, (20, 0, zb + 4), "Y"), "cięciwa Y")
dim(f, "otwór: naroże ostre (x przy y=48,1)", "insert_opening_r 0", P["insert_opening"] / 2, coord(WK, (0, 48.1, zb + 4), "X"), "promień +X")
dim(f, "wysokość ramy", "insert_h", P["insert_h"], outer(WK, (-40, -50.3, zb + 3), "Z", 20), "promienie z zewnątrz")
dim(f, "faza górnej krawędzi wewn. 1×45°: x na Z 6−0,5", "insert_chamfer", P["insert_opening"] / 2 + 0.5, coord(WK, (0, 20, zb + P["insert_h"] - 0.5), "X"), "promień +X 0,5 pod wierzchem")
for (nm, x, y) in (("A", -38, -38), ("B", -38, 38), ("C", 38, 38), ("D", 38, -38)):
    dim(f, "półka %s: wierzch Z" % nm, "insert_shelf_h", zb + P["insert_shelf_h"], coord(WK, (x, y, zb + 10), "-Z"), "promień −Z")
    dim(f, "półka %s: grubość" % nm, "insert_shelf_h", P["insert_shelf_h"], outer(WK, (x, y, zb + 1), "Z", 20), "promienie z zewnątrz")
    dim(f, "półka %s: zasięg 12 od ściany otworu" % nm, "insert_shelf", P["insert_opening"] / 2 - P["insert_shelf"], abs(coord(WK, (0, y, zb + 1.5), "-X" if x < 0 else "X") or 0), "promień poziomy od x=0 do krawędzi półki")
for (nm, x, y) in (("A", -42, -42), ("B", -42, 42), ("C", 42, 42)):
    dim(f, "kieszeń Halla %s: X" % nm, "hall_pocket_w", P["hall_pocket_w"], chord(WK, (x, y, zb + 1.5), "X"), "cięciwa X")
    dim(f, "kieszeń Halla %s: Y" % nm, "hall_pocket_l", P["hall_pocket_l"], chord(WK, (x, y, zb + 1.5), "Y"), "cięciwa Y")
    thr = hit(WK, (x, y, zb + 4), "-Z")[2]
    dim(f, "kieszeń Halla %s: przelotowa" % nm, "D5", 0.0, 0.0 if thr is None else 1.0, "promień −Z: 0 = przelot")
    # kanał pod półką 2,5 x 1,0 po przekątnej do ściany: punkt między kieszenią a ścianką ramy
    sx, sy = (-1 if x < 0 else 1), (-1 if y < 0 else 1)
    q = (x + sx * 4.0, y + sy * 4.0, zb + 0.5)
    dim(f, "kanał Halla %s pod półką: wysokość" % nm, "hall_lead_channel_h", P["hall_lead_channel_h"], (coord(WK, q, "Z") or 0) - zb, "promień +Z z Z 0,5 (sufit kanału)")
    wall(f, "półka %s nad kanałem (2,5 − 1,0)" % nm, P["insert_shelf_h"] - P["hall_lead_channel_h"], chord(WK, (q[0], q[1], zb + 1.75), "Z"), (q[0], q[1], zb + 1.75))
    perp = Vector((-sy, sx, 0)).normalized()
    dim(f, "kanał Halla %s pod półką: szerokość" % nm, "hall_lead_channel_w", P["hall_lead_channel_w"], chord(WK, q, perp), "cięciwa prostopadła do przekątnej", tol=0.1)
    # przelot w ściance ramy 2,5 x 1,5 po przekątnej (−48,3..−52,3)
    q2 = (x + sx * 8.3, y + sy * 8.3, zb + 0.75)
    dim(f, "przelot w ściance ramy %s: wysokość" % nm, "hall_wall_pass_h", P["hall_wall_pass_h"], (coord(WK, q2, "Z") or 0) - zb, "promień +Z (sufit przelotu)")
    hdiag = hit(WK, (x + sx * 5.5, y + sy * 5.5, zb + 0.75), Vector((sx, sy, 0)).normalized())[2]
    dim(f, "przelot w ściance ramy %s: otwarty po przekątnej przez całą ściankę (promień z (%g,%g) ku narożnikowi; do narożnika zewn. 6,8)" % (nm, x + sx * 5.5, y + sy * 5.5), "R50‑U9 (jedna bryła ciągła)", 0.0, 0.0 if (hdiag is None or hdiag > 6.7) else 1.0, "0 = brak trafienia w ściankę przed narożnikiem zewn. (za nim w B i C leży nasada ucha)")
# kołek orientacyjny
kx = P["insert_opening"] / 2 - P["orient_post_gap"] - P["orient_post"] / 2
dim(f, "kołek orientacyjny: X", "orient_post", P["orient_post"], outer(WK, (kx, -kx, zb + 5), "X", 2.5), "promienie z odległości 2,5 w Z 5")
dim(f, "kołek orientacyjny: Y", "orient_post", P["orient_post"], outer(WK, (kx, -kx, zb + 5), "Y", 2.5), "promienie z odległości 2,5 w Z 5")
dim(f, "kołek orientacyjny: szczyt Z", "insert_shelf_h + orient_post_h", zb + P["insert_shelf_h"] + P["orient_post_h"], coord(WK, (kx, -kx, zb + 20), "-Z"), "promień −Z")
dim(f, "kołek orientacyjny: luz do ściany otworu (x)", "orient_post_gap", P["orient_post_gap"], chord(WK, (P["insert_opening"] / 2 - 0.25, -kx, zb + 4), "X"), "cięciwa X w szczelinie")
dim(f, "kołek orientacyjny: faza 1 na szczycie (X na Z szczyt−0,5)", "orient_post_chamfer", P["orient_post"] - 2 * 0.5, outer(WK, (kx, -kx, zb + P["insert_shelf_h"] + P["orient_post_h"] - 0.5), "X", 2.5), "promienie z zewnątrz 0,5 pod szczytem")
dim(f, "wycięcie palcowe X", "finger_cut_w", P["finger_cut_w"], chord(WK, (0, -50.3, zb + 3), "X"), "cięciwa X w ścianie przedniej")
dim(f, "wycięcie palcowe: pełna wysokość", "4.6.5", 0.0, 0.0 if hit(WK, (0, -50.3, zb + 10), "-Z")[2] is None else 1.0, "promień −Z: 0 = brak materiału")
for (nm, p, d_, expv) in (("prawy", (57.3, 0, zb + 0.75), "-X", 52.3 - P["wire_rabbet_w"]), ("lewy", (-57.3, 0, zb + 0.75), "X", -(52.3 - P["wire_rabbet_w"])), ("tylny", (0, 57.3, zb + 0.75), "-Y", 52.3 - P["wire_rabbet_w"])):
    dim(f, "rowek kablowy %s: dno" % nm, "52,3 − wire_rabbet_w", expv, coord(WK, p, d_), "promień poziomy w Z 0,75")
    q = list(p); q[0 if d_ in ("X", "-X") else 1] = (51.05 if expv > 0 else -51.05)
    dim(f, "rowek kablowy %s: sufit" % nm, "wire_rabbet", zb + P["wire_rabbet"], coord(WK, (q[0], q[1], zb - 5), "Z"), "promień +Z od dołu")
wall(f, "ścianka rowek kablowy – otwór (52,3 − 2,5 − 48,3)", P["insert_wall_w"] - P["wire_rabbet_w"], chord(WK, (49.05, 0, zb + 0.75), "X"), (49.05, 0, zb + 0.75))
wall(f, "ścianka rowek kablowy – otwór (tył)", P["insert_wall_w"] - P["wire_rabbet_w"], chord(WK, (0, 49.05, zb + 0.75), "Y"), (0, 49.05, zb + 0.75))
wall(f, "rama nad rowkiem kablowym (6 − 1,5)", P["insert_h"] - P["wire_rabbet"], chord(WK, (51.05, 0, zb + 3.75), "Z"), (51.05, 0, zb + 3.75))
dim(f, "brak materiału poza ramą dla y<52,3 (prawy pas, K‑56)", "R51(3)", 0.0, 0.0 if hit(WK, (58, 50, zb + 10), "-Z")[2] is None else 1.0, "promień −Z w (58,50): 0 = nic")
dim(f, "nasada L: x 44…52,3 od y 48,8 (materiał w (48,49.5))", "tab_root_*", 1.0, 0.0 if hit(WK, (48, 49.5, zb + 10), "-Z")[2] is None else 1.0, "promień −Z: 1 = materiał")
dim(f, "nasada L: materiał w (56, 55) (x 52,3…65 od y 52,3)", "tab_root_x_out", 1.0, 0.0 if hit(WK, (56, 55, zb + 10), "-Z")[2] is None else 1.0, "promień −Z: 1 = materiał")
dim(f, "nasada L: brak materiału w (56, 51) (poza obrysem ramy dla y < 52,3)", "tab_root_x_out", 0.0, 0.0 if hit(WK, (56, 51, zb + 10), "-Z")[2] is None else 1.0, "promień −Z: 0 = nic")
dim(f, "nasada L: materiał w (46, 50) (x 44…52,3 od y 48,8 — w obrysie ramy)", "tab_root_x_in", 1.0, 0.0 if (hit(WK, (46, 50, zb + 0.5), "-Z")[2] is None and hit(WK, (46, 50, zb + 0.5), "Z")[2] is None) else 1.0, "promienie ±Z z Z 0,5: 1 = materiał")
for sx in (-1, 1):
    dim(f, "ucho x=%g: szerokość X" % (sx * 58), "tab_w", P["tab_w"], outer(WK, (sx * 58, 80, zb + 1.5), "X", 10), "promienie z zewnątrz")
    dim(f, "ucho x=%g: koniec Y" % (sx * 58), "tab_end_y", P["tab_end_y"], coord(WK, (sx * 58, 120, zb + 1.5), "-Y"), "promień −Y")
    dim(f, "ucho x=%g: grubość" % (sx * 58), "tab_t", P["tab_t"], outer(WK, (sx * 58, 80, zb + 1.5), "Z", 10), "promienie z zewnątrz")
    dim(f, "kołek ustalający x=%g: ø" % (sx * 58), "tab_pin_d", P["tab_pin_d"], chord(WK, (sx * 58, 93.5, zb - 1.5), "X") if False else outer(WK, (sx * 58, 93.5, zb - 1.5), "X", 4), "promienie z zewnątrz")
    dim(f, "kołek ustalający x=%g: koniec Z" % (sx * 58), "tab_pin_h", zb - P["tab_pin_h"], coord(WK, (sx * 58, 93.5, zb - 10), "Z"), "promień +Z od dołu")
    dim(f, "otwór magnesu ucha x=%g: ø" % (sx * 58), "tab_magnet_hole_d", P["tab_magnet_hole_d"], chord(WK, (sx * 58, 86, zb + 1.5), "X"), "cięciwa X")
    dim(f, "otwór magnesu ucha x=%g: przelotowy" % (sx * 58), "D12", 0.0, 0.0 if hit(WK, (sx * 58, 86, zb + 2.9), "-Z")[2] is None else 1.0, "promień −Z: 0 = przelot")
    dim(f, "kanał kablowy ucha x=%g: wysokość" % (sx * 64), "tab_cable_channel_h", P["tab_cable_channel_h"], (coord(WK, (sx * 64, 75, zb - 1), "Z") or 0) - zb, "promień +Z od dołu")
    dim(f, "kanał kablowy ucha x=%g: szerokość (od krawędzi ucha 65 do ścianki kanału)" % (sx * 64), "tab_cable_channel_w", P["tab_cable_channel_w"], None if coord(WK, (sx * 64, 75, zb + 0.5), "-X" if sx > 0 else "X") is None else 65 - abs(coord(WK, (sx * 64, 75, zb + 0.5), "-X" if sx > 0 else "X")), "promień do ścianki kanału; kanał otwarty na krawędzi ucha")
    dim(f, "kanał kablowy ucha x=%g: wylot na krawędzi ucha (y 90)" % (sx * 64), "wire_slot_y", 1.0, 0.0 if hit(WK, (sx * 64.9, 90, zb + 0.5), "X" if sx > 0 else "-X")[2] is None else 1.0, "promień do krawędzi 65: 0 = otwarty")
arr = []
for x in (-32, 32):
    zt = max([coord(WK, (x + dx, -51.15 + dy, zb + 20), "-Z") or 0 for dx in (-1, -0.5, 0, 0.5, 1) for dy in (-0.5, 0, 0.5)])
    arr.append(zt)
    dim(f, "strzałka ▼ x=%g: relief nad ramą" % x, "number_relief_h", P["number_relief_h"], zt - (zb + P["insert_h"]), "max trafień −Z w polu wokół środka")

# blat
f = "ramka_blat_v2.stl"; mn, mx = bbox(STL[f]["verts"]); zt_ = Z_BLAT_TOP
dim(f, "gabaryt X", "box_outer", 200.0, mx.x - mn.x, "bbox"); dim(f, "gabaryt Y", "box_outer", 200.0, mx.y - mn.y, "bbox")
dim(f, "gabaryt Z", "blat_t + blat_skirt_h", P["blat_t"] + P["blat_skirt_h"], mx.z - mn.z, "bbox")
dim(f, "grubość płyty", "blat_t", P["blat_t"], outer(BLAT, (90, 0, zt_ - 2), "Z", 20), "promienie z zewnątrz")
dim(f, "spód płyty płaski (R50‑U1, (90,90))", "blat_t", zt_ - P["blat_t"], coord(BLAT, (90, 90, zt_ - 20), "Z"), "promień +Z od dołu")
dim(f, "kieszeń dyfuzora X", "diffuser_pocket", P["diffuser_pocket"], chord(BLAT, (0, 20, zt_ - 1), "X"), "cięciwa X")
dim(f, "kieszeń dyfuzora Y", "diffuser_pocket", P["diffuser_pocket"], chord(BLAT, (20, 0, zt_ - 1), "Y"), "cięciwa Y")
dim(f, "kieszeń dyfuzora: głębokość", "diffuser_t", P["diffuser_t"], zt_ - (coord(BLAT, (80, 0, zt_ + 1), "-Z") or 0), "promień −Z na półce")
dim(f, "kieszeń dyfuzora: naroże ostre", "diffuser_pocket_r 0", P["diffuser_pocket"] / 2, coord(BLAT, (0, 80.8, zt_ - 1), "X"), "promień +X przy y 80,8")
dim(f, "okno X", "window_through", P["window_through"], chord(BLAT, (0, 20, zt_ - 3), "X"), "cięciwa X")
dim(f, "okno Y", "window_through", P["window_through"], chord(BLAT, (20, 0, zt_ - 3), "Y"), "cięciwa Y")
dim(f, "kołnierz zewn. X", "195 − 2·blat_skirt_clearance", 195 - 2 * P["blat_skirt_clearance"], outer(BLAT, (0, 30, zt_ - 9), "X"), "promienie z zewnątrz")
dim(f, "kołnierz zewn. Y", "j.w.", 195 - 2 * P["blat_skirt_clearance"], outer(BLAT, (30, 0, zt_ - 9), "Y"), "promienie z zewnątrz")
wall(f, "kołnierz blatu (grubość)", P["blat_skirt_t"], chord(BLAT, (96, 30, zt_ - 9), "X"), (96, 30, zt_ - 9))
wall(f, "kołnierz blatu (grubość, tył)", P["blat_skirt_t"], chord(BLAT, (30, 96, zt_ - 9), "Y"), (30, 96, zt_ - 9))
dim(f, "kołnierz: wysokość całkowita", "blat_t + blat_skirt_h", P["blat_t"] + P["blat_skirt_h"], outer(BLAT, (96, 30, zt_ - 9), "Z", 20), "promienie z zewnątrz")
for (nm, p, d_, along, at) in (("prawy", (110, 0, Z_KORPUS_H - 5.75), "-X", "Y", 0), ("lewy", (-110, 0, Z_KORPUS_H - 5.75), "X", "Y", 0), ("przedni", (50, -110, Z_KORPUS_H - 5.75), "Y", "X", 50), ("tylny", (-50, 110, Z_KORPUS_H - 5.75), "-Y", "X", -50)):
    tipc = coord(BLAT, p, d_)
    dim(f, "haczyk %s: czubek" % nm, "97,0 + snap_hook_h", 97.0 + P["snap_hook_h"], None if tipc is None else abs(tipc), "promień poziomy w środku występu")
    tp = hit(BLAT, p, d_)[0]
    if tp is not None:
        inn = tp + vec(d_) * 0.3
        dim(f, "haczyk %s: szerokość" % nm, "snap_hook_w", P["snap_hook_w"], chord(BLAT, inn, along), "cięciwa 0,3 za czubkiem", tol=0.1)
        zc_ = hit(BLAT, inn, "Z")[0].z; zd_ = hit(BLAT, inn, "-Z")[0].z
        RES.setdefault("haczyk_lico", {})[nm] = round(zc_ - zd_, 3)   # informacyjnie: wysokość pionowego lica czubka 0,3 za czubkiem (rampa zajmuje dolne ~1,0)
    # ramię 1,5 (grubość ramienia poniżej występu) i nacięcia 1 mm od dołu kołnierza do lokalnie −5 (Z 58,6)
    q = list(p); q[2] = Z_KORPUS_H - 9.0
    arm_in = hit(BLAT, q, d_)[0]
    if arm_in is not None:
        wall(f, "ramię haczyka %s (grubość poniżej występu, Z 50,6)" % nm, P["snap_hook_t"], chord(BLAT, arm_in + vec(d_) * 0.2, d_), tuple(arm_in + vec(d_) * 0.2))
    # nacięcie: promień wzdłuż d_ na pozycji along = at ± 4,5 powinien przejść przez kołnierz (brak trafienia w kołnierz 95..97)
    for s in (-1, 1):
        qq = list(p); qq[0 if along == "X" else 1] = at + s * (P["snap_hook_w"] / 2 + P["snap_notch_w"] / 2); qq[2] = Z_KORPUS_H - 9.0
        h_ = hit(BLAT, qq, d_)[2]
        dim(f, "nacięcie przy haczyku %s (%s=%g): przelot przez kołnierz w Z 50,6" % (nm, along, qq[0 if along == "X" else 1]), "snap_notch_w", 0.0, 0.0 if (h_ is None or h_ > 20) else 1.0, "promień poziomy: 0 = brak kołnierza (nacięcie)")
        qq[2] = Z_BLAT_TOP - 5 + 0.5  # lokalnie −4,5: nad końcem nacięcia (−5) → materiał (nasada 1 mm pod płytą)
        h2 = hit(BLAT, qq, d_)[2]
        dim(f, "nacięcie przy haczyku %s (%s=%g): koniec nacięcia (materiał w Z %.1f, lokalnie −4,5)" % (nm, along, qq[0 if along == "X" else 1], qq[2]), "snap_hook_arm_l 9 (−14…−5)", 1.0, 0.0 if (h2 is None or h2 > 20) else 1.0, "promień poziomy: 1 = materiał")
        qq[2] = Z_BLAT_TOP - 5 - 0.3  # lokalnie −5,3: w nacięciu
        h3 = hit(BLAT, qq, d_)[2]
        dim(f, "nacięcie przy haczyku %s (%s=%g): jeszcze nacięcie w Z %.1f (lokalnie −5,3)" % (nm, along, qq[0 if along == "X" else 1], qq[2]), "snap_hook_arm_l 9", 0.0, 0.0 if (h3 is None or h3 > 20) else 1.0, "promień poziomy: 0 = nacięcie")
for sx in (-1, 1):
    x = sx * 75
    dim(f, "słupek x=%g: X zakres (71…79)" % x, "blat_post_w", P["blat_post_w"], outer(BLAT, (x, 92, Z_KORPUS_H - 7), "X", 6), "promienie z zewnątrz")
    dim(f, "słupek x=%g: przednie lico y" % x, "blat_post_y0", P["blat_post_y0"], coord(BLAT, (x, 70, Z_KORPUS_H - 7), "Y"), "promień +Y")
    dim(f, "słupek x=%g: dół Z (lokalnie −14)" % x, "blat_skirt_h", Z_KORPUS_H - P["blat_skirt_h"], coord(BLAT, (x, 92, 30), "Z"), "promień +Z od dołu")
    dim(f, "otwór słupka x=%g: ø" % x, "insert_hole_m3", P["insert_hole_m3"], chord(BLAT, (x, 94, Z_KORPUS_H - 4.6), "X"), "cięciwa X")
    dim(f, "otwór słupka x=%g: ø (Z)" % x, "insert_hole_m3", P["insert_hole_m3"], chord(BLAT, (x, 94, Z_KORPUS_H - 4.6), "Z"), "cięciwa Z")
    hb_ = coord(BLAT, (x, 94, Z_KORPUS_H - 4.6), "-Y")
    dim(f, "otwór słupka x=%g: dno (y)" % x, "97,0 − blat_post_hole_depth", 97.0 - P["blat_post_hole_depth"], hb_, "promień −Y")
    wall(f, "dno pod otworem słupka x=%g (91,0 − 89,2)" % x, 1.8, None if hb_ is None else hb_ - (coord(BLAT, (x, 70, Z_KORPUS_H - 4.6), "Y") or 0), (x, 90.1, Z_KORPUS_H - 4.6))
    dim(f, "otwór słupka x=%g: otwarty na licu kołnierza 97,0" % x, "R49a", 0.0, 0.0 if (hit(BLAT, (x, 94, Z_KORPUS_H - 4.6), "Y")[2] is None) else 1.0, "promień +Y: 0 = wychodzi na zewnątrz")
    dim(f, "otwór kołka x=%g: ø" % (sx * 58), "blat_pin_hole_d", P["blat_pin_hole_d"], chord(BLAT, (sx * 58, 93.5, zt_ - 2), "X"), "cięciwa X")
    dim(f, "otwór kołka x=%g: dno Z (ślepy)" % (sx * 58), "blat_pin_hole_depth", zt_ - P["blat_pin_hole_depth"], coord(BLAT, (sx * 58, 93.5, zt_ - 1), "-Z"), "promień −Z")
    wall(f, "dno blatu pod otworem kołka x=%g (4 − 3,8 = 0,2; R8 dopuszczone lokalnie)" % (sx * 58), P["blat_t"] - P["blat_pin_hole_depth"], chord(BLAT, (sx * 58, 93.5, zt_ - P["blat_pin_hole_depth"] - 0.1), "Z"), (sx * 58, 93.5, zt_ - 3.9), min_req=0.2, uwaga="R8/4.11: nie ścianka nośna, może przebić się na wylot")
    dim(f, "kieszeń magnesu x=%g: ø" % (sx * 58), "blat_magnet_pocket_d", P["blat_magnet_pocket_d"], chord(BLAT, (sx * 58, 86, zt_ - 1), "X"), "cięciwa X")
    dim(f, "kieszeń magnesu x=%g: głębokość" % (sx * 58), "blat_magnet_pocket_depth", P["blat_magnet_pocket_depth"], zt_ - (coord(BLAT, (sx * 58, 86, zt_ - 1), "-Z") or 0), "promień −Z")
    dim(f, "szczelina kabla x=%g: X" % (sx * 66), "wire_slot_w", P["wire_slot_w"], chord(BLAT, (sx * 66, 90, zt_ - 2), "X"), "cięciwa X")
    dim(f, "szczelina kabla x=%g: Y" % (sx * 66), "wire_slot_l", P["wire_slot_l"], chord(BLAT, (sx * 66, 90, zt_ - 2), "Y"), "cięciwa Y")
    dim(f, "szczelina kabla x=%g: przelotowa" % (sx * 66), "D12", 0.0, 0.0 if hit(BLAT, (sx * 66, 90, zt_ + 1), "-Z")[2] is None else 1.0, "promień −Z: 0 = przelot")
diag = Vector((1, 1, 0)).normalized()
cp = hit(BLAT, Vector((100, 100, zt_ - 2)) + diag * 5, -diag)[0]
dim(f, "R 5 pionowej krawędzi: punkt na przekątnej", "blat_corner_r", 100 - 5 + 5 / math.sqrt(2), None if cp is None else cp.x, "promień wzdłuż przekątnej")
dim(f, "R 1,5 górnej krawędzi: x boku na Z wierzch−0,2", "blat_top_edge_r", 100 - 1.5 + math.sqrt(1.5 ** 2 - 1.3 ** 2), coord(BLAT, (120, 30, zt_ - 0.2), "-X"), "promień −X 0,2 pod wierzchem", tol=0.05)
cpk = hit(BLAT, Vector((97, 97, zt_ - 9)) + diag * 5, -diag)[0]
dim(f, "kołnierz: R 4,5 naroża zewn.", "R50‑U15 (4,5)", 97 - 4.5 + 4.5 / math.sqrt(2), None if cpk is None else cpk.x, "promień wzdłuż przekątnej", tol=0.05)

# korpus W i P
for K, kn in ((KORPUS_W, "W"), (KORPUS_P, "P")):
    f = "ramka_korpus_%s_v2.stl" % kn; mn, mx = bbox(STL[f]["verts"])
    dim(f, "gabaryt X", "box_outer", P["box_outer"], mx.x - mn.x, "bbox")
    dim(f, "gabaryt Y (z napisem 0,6)", "box_outer + label_relief_h", P["box_outer"] + P["label_relief_h"], mx.y - mn.y, "bbox")
    dim(f, "gabaryt Z", "korpus_h", Z_KORPUS_H, mx.z - mn.z, "bbox")
    dim(f, "bok X", "box_outer", P["box_outer"], outer(K, (0, 20, 20), "X"), "promienie z zewnątrz")
    dim(f, "bok Y (poza napisem)", "box_outer", P["box_outer"], outer(K, (80, 0, 20), "Y"), "promienie z zewnątrz")
    dim(f, "wnętrze X", "box_outer − 2·wall_t", P["box_outer"] - 2 * P["wall_t"], chord(K, (0, 20, 20), "X"), "cięciwa X")
    dim(f, "wnętrze Y", "j.w.", P["box_outer"] - 2 * P["wall_t"], chord(K, (20, 0, 20), "Y"), "cięciwa Y")
    dim(f, "wierzch ściany Z", "korpus_h", Z_KORPUS_H, coord(K, (98.75, 20, 200), "-Z"), "promień −Z")
    dim(f, "dno: grubość", "floor_t", P["floor_t"], outer(K, (20, -20, 1), "Z", 10), "promienie z zewnątrz")
    for (nm, p, d_) in (("prawa", (98.75, 20, 30), "X"), ("lewa", (-98.75, -40, 30), "X"), ("przednia (poza napisem)", (80, -98.75, 30), "Y"), ("tylna", (20, 98.75, 30), "Y"), ("prawa za kieszenią zatrzasku", (99.25, 0, Z_KORPUS_H - 5.75), "X"), ("przednia za kieszenią zatrzasku", (50, -99.25, Z_KORPUS_H - 5.75), "Y"), ("tylna za kieszenią zatrzasku", (-50, 99.25, Z_KORPUS_H - 5.75), "Y"), ("lewa za kieszenią zatrzasku", (-99.25, 0, Z_KORPUS_H - 5.75), "X"), ("tylna między szczelinami (x=0)", (0, 98.75, 8), "Y"), ("prawa nad szczeliną y=0 (Z 10)", (98.75, 0, 10), "X"), ("tylna pod skrzynką DC (Z 11)", (-67.5, 98.75, 11), "Y"), ("tylna między oknem DC a narożnikiem (x=−95)", (-95, 98.75, 26), "Y"), ("tylna między oknem USB a rowkiem", (51.05, 98.75, 24), "X")):
        exp_ = P["wall_t"] - (P["snap_pocket_depth"] if "za kieszenią" in nm else 0)
        if "między oknem USB" in nm:
            exp_ = 1.9
        wall(f, "ściana korpusu %s" % nm, exp_, chord(K, p, d_), p)
    wall(f, "dno obok rowka panelu i poza stadionem ((64,54))", P["floor_t"], chord(K, (64, 54, 1.5), "Z"), (64, 54, 1.5))
    wall(f, "dno między wlotami (y=0, x=−8)", P["floor_t"], chord(K, (-8, 0, 1.5), "Z"), (-8, 0, 1.5))
    wall(f, "dno skrzynki DC (Z 12…14)", P["dc_pocket_wall"], chord(K, (-67.5, 88, 13), "Z"), (-67.5, 88, 13))
    wall(f, "sufit skrzynki DC (Z 38…40)", P["dc_pocket_wall"], chord(K, (-67.5, 88, 39), "Z"), (-67.5, 88, 39))
    wall(f, "przednia ściana skrzynki DC (y 78…80)", P["dc_pocket_wall"], chord(K, (-67.5, 79, 26), "Y"), (-67.5, 79, 26))
    wall(f, "lewa ściana skrzynki DC (x −97,5…−95,5; w ścianie korpusu łącznie 4,5)", P["wall_t"] + P["dc_pocket_wall"], chord(K, (-96.5, 88, 26), "X"), (-96.5, 88, 26))
    wall(f, "ścianka bossa Pi (ø8 − ø2,1)/2", (P["pi_boss_d"] - P["insert_hole_m25"]) / 2, chord(K, (-46.5 + (P["insert_hole_m25"] + P["pi_boss_d"]) / 4, -24.5, 6), "X"), (-46.5 + 2.525, -24.5, 6))
    diag = Vector((1, 1, 0)).normalized()
    cp = hit(K, Vector((100, 100, 30)) + diag * 10, -diag)[0]
    dim(f, "R 5 pionowej krawędzi: punkt na przekątnej", "box_corner_r", 100 - 5 + 5 / math.sqrt(2), None if cp is None else cp.x, "promień wzdłuż przekątnej")
    dim(f, "R 3 dolnej krawędzi: x boku na Z 0,2", "box_edge_r", 100 - 3 + math.sqrt(3 ** 2 - 2.8 ** 2), coord(K, (120, 20, 0.2), "-X"), "promień −X 0,2 nad dnem")
    # szczeliny wentylacyjne
    for x in P["vent_slots_rear_x"]:
        dim(f, "szczelina tylna x=%g: X" % x, "vent_slot_w", P["vent_slot_w"], chord(K, (x, 98.75, P["vent_slot_z"]), "X"), "cięciwa X")
        dim(f, "szczelina tylna x=%g: Z" % x, "vent_slot_h", P["vent_slot_h"], chord(K, (x, 98.75, P["vent_slot_z"]), "Z"), "cięciwa Z")
    for y in P["vent_slots_side_y"]:
        for sx in (-1, 1):
            dim(f, "szczelina boczna x=%s y=%g: Y" % ("+" if sx > 0 else "−", y), "vent_slot_w", P["vent_slot_w"], chord(K, (sx * 98.75, y, P["vent_slot_z"]), "Y"), "cięciwa Y")
            dim(f, "szczelina boczna x=%s y=%g: Z" % ("+" if sx > 0 else "−", y), "vent_slot_h", P["vent_slot_h"], chord(K, (sx * 98.75, y, P["vent_slot_z"]), "Z"), "cięciwa Z")
    for y in P["floor_vent_y"]:
        dim(f, "wlot w dnie y=%g: X" % y, "floor_vent_l", P["floor_vent_l"], chord(K, (P["floor_vent_x"], y, 1.5), "X"), "cięciwa X")
        dim(f, "wlot w dnie y=%g: Y" % y, "floor_vent_w", P["floor_vent_w"], chord(K, (P["floor_vent_x"], y, 1.5), "Y"), "cięciwa Y")
    # kieszenie zatrzasków
    for (nm, p, along, d_) in (("prawa", (98.0, 0, Z_KORPUS_H - 5.75), "Y", "X"), ("lewa", (-98.0, 0, Z_KORPUS_H - 5.75), "Y", "-X"), ("przednia", (50, -98.0, Z_KORPUS_H - 5.75), "X", "-Y"), ("tylna", (-50, 98.0, Z_KORPUS_H - 5.75), "X", "Y")):
        dim(f, "kieszeń zatrzasku %s: szerokość" % nm, "snap_pocket_w", P["snap_pocket_w"], chord(K, p, along), "cięciwa")
        dim(f, "kieszeń zatrzasku %s: wysokość" % nm, "snap_pocket_h", P["snap_pocket_h"], chord(K, p, "Z"), "cięciwa Z")
        dim(f, "kieszeń zatrzasku %s: dolna krawędź Z" % nm, "snap_pocket_z", Z_KORPUS_H - 7, coord(K, p, "-Z"), "promień −Z")
        dim(f, "kieszeń zatrzasku %s: dno" % nm, "97,5 + snap_pocket_depth", 97.5 + P["snap_pocket_depth"], abs(coord(K, p, d_)), "promień poziomy")
    # wkręty blatu: ø3,2 i pogłębienie ø6,3/90°
    for sx in (-1, 1):
        x = sx * 75
        dim(f, "otwór wkrętu blatu x=%g: ø" % x, "blat_screw_hole_d", P["blat_screw_hole_d"], chord(K, (x, 97.8, Z_KORPUS_H - 4.6), "X"), "cięciwa X")
        dim(f, "pogłębienie stożkowe x=%g: ø 0,1 pod licem" % x, "blat_screw_csink_d", P["blat_screw_csink_d"] - 0.2, chord(K, (x, 99.9, Z_KORPUS_H - 4.6), "X"), "cięciwa X (90° → −0,2)")
    # napis: zasięg X i wysokość liter
    xs_ = []; zs_ = []
    for xx in [i * 0.5 for i in range(-140, 141)]:
        for zz in (Z_KORPUS_H - 8.6 - 3.5, Z_KORPUS_H - 8.6, Z_KORPUS_H - 8.6 + 3.5):
            yy = coord(K, (xx, -150, zz), "Y")
            if yy is not None and yy < -100.05:
                xs_.append(xx)
    for zz in [i * 0.1 for i in range(int((Z_KORPUS_H - 8.6 - 6) * 10), int((Z_KORPUS_H - 8.6 + 6) * 10))]:
        for xx in [i * 1.0 for i in range(-60, 61)]:
            yy = coord(K, (xx, -150, zz), "Y")
            if yy is not None and yy < -100.05:
                zs_.append(zz); break
    if xs_ and zs_:
        dim(f, "napis: wysokość liter (Z)", "label_text_h", P["label_text_h"], max(zs_) - min(zs_) + 0.1, "skan 0,1 mm", tol=0.3)
        dim(f, "napis: środek Z", "label_pos_z", Z_KORPUS_H - 8.6, (max(zs_) + min(zs_)) / 2, "skan 0,1 mm", tol=0.3)
        dim(f, "napis: środek X", "0", 0.0, (max(xs_) + min(xs_)) / 2, "skan 0,5 mm", tol=1.0)
        RES.setdefault("napis", {})[kn] = {"x": [min(xs_), max(xs_)], "z": [min(zs_), max(zs_)], "szerokosc": max(xs_) - min(xs_) + 0.5}
        dim(f, "napis: relief", "label_relief_h", P["label_relief_h"], -100 - min([coord(K, (xx, -150, Z_KORPUS_H - 8.6), "Y") for xx in xs_ if coord(K, (xx, -150, Z_KORPUS_H - 8.6), "Y") is not None] + [0]), "min Y trafień", tol=0.05)
    dim(f, "przednia ściana gładka (Z28): brak otworów (skan Z 10…50, x −90…90)", "D15", 0, sum(1 for xx in range(-90, 91, 5) for zz in range(10, 51, 5) if hit(K, (xx, -150, zz), "Y")[2] is None), "liczba promieni +Y bez trafienia")
# korpus W vs P: geometria poza napisem identyczna
vw = set((round(v.x, 4), round(v.y, 4), round(v.z, 4)) for v in KORPUS_W.verts if v.y > -99.9)
vp = set((round(v.x, 4), round(v.y, 4), round(v.z, 4)) for v in KORPUS_P.verts if v.y > -99.9)
RES["korpus_WP_roznica_wierzcholkow"] = len(vw ^ vp)
if len(vw ^ vp):
    uwaga("korpus W i P: %d wierzchołków różni się poza przednią ścianą (y > −99,9) — różnica tesselacji po unii z napisem; geometria sprawdzana osobno sondami dla W i P" % len(vw ^ vp))

# tulejka
f = "ramka_tulejka_dc_v2.stl"; mn, mx = bbox(STL[f]["verts"])
dim(f, "gabaryt X/Y (kołnierz ø15)", "dc_bush_flange_d", P["dc_bush_flange_d"], mx.x - mn.x, "bbox", tol=0.05)
dim(f, "gabaryt Z", "dc_bush_t + dc_bush_flange_t", P["dc_bush_t"] + P["dc_bush_flange_t"], mx.z - mn.z, "bbox")
dim(f, "walec ø zewn.", "dc_bush_outer_d", P["dc_bush_outer_d"], outer(TUL, (-41, 89, 30), "Y", 20), "promienie z zewnątrz (w złożeniu, oś X)")
dim(f, "otwór ø", "dc_bush_inner_d", P["dc_bush_inner_d"], chord(TUL, (-41, 89, 30), "Y"), "cięciwa")
dim(f, "kołnierz: grubość", "dc_bush_flange_t", P["dc_bush_flange_t"], outer(TUL, (-42.5, 89 + 6.75, 30), "X", 5), "promienie z zewnątrz")
dim(f, "walec: długość", "dc_bush_t", P["dc_bush_t"], (coord(TUL, (-36, 89 + 5.5, 30), "-X") or 0) - (coord(TUL, (-36, 89 + 6.75, 30), "-X") or 0), "koniec walca (−40) − lico kołnierza od strony ściany (−42)")
wall(f, "ścianka tulejki (12 − 8,2)/2", (P["dc_bush_outer_d"] - P["dc_bush_inner_d"]) / 2, chord(TUL, (-41, 89 + 5.05, 30), "Y"), (-41, 94.05, 30), min_req=1.5, uwaga="druk własny (żywica/PETG); dopuszczone < 1,5? — reguła 4.8 dotyczy PA12 SLS")
# podkładki
for f in ("ramka_podkladka_panelu_05_v2.stl", "ramka_podkladka_panelu_1_v2.stl", "ramka_podkladka_panelu_2_v2.stl"):
    S = PARTS[f]; t = {"05": 0.5, "1": 1.0, "2": 2.0}[f.split("_")[3]]; mn, mx = bbox(STL[f]["verts"])
    dim(f, "gabaryt X", "panel_shim_d", P["panel_shim_d"], mx.x - mn.x, "bbox")
    dim(f, "gabaryt Y", "panel_shim_d", P["panel_shim_d"], mx.y - mn.y, "bbox")
    dim(f, "gabaryt Z", "panel_shim_t", t, mx.z - mn.z, "bbox")
    dim(f, "ø zewn.", "panel_shim_d", P["panel_shim_d"], outer(S, (0, 0, t / 2), "X", 10), "promienie z zewnątrz")
    dim(f, "otwór ø", "panel_shim_hole_d", P["panel_shim_hole_d"], chord(S, (0, 0, t / 2), "X"), "cięciwa X")
    dim(f, "otwór ø (Y)", "panel_shim_hole_d", P["panel_shim_hole_d"], chord(S, (0, 0, t / 2), "Y"), "cięciwa Y")
    dim(f, "grubość", "panel_shim_t", t, outer(S, (3.1, 0, t / 2), "Z", 5), "promienie z zewnątrz")

# =========================================================================== 3. SYMULACJA MONTAŻU
log("=== 3. SYMULACJA MONTAŻU")
PARITY_DIRS = [Vector((0.3117, 0.5273, 0.7903)).normalized(), Vector((-0.6131, 0.2927, -0.7338)).normalized()]
def inside_parity(part, p, d):
    """punkt wewnątrz zamkniętej siatki: nieparzysta liczba trafień promienia w kierunku d"""
    o = Vector(p); n = 0; last = None
    for _ in range(64):
        loc, nrm, idx, dist = part.bvh.ray_cast(o, d)
        if loc is None:
            break
        if dist > 1e-4 and not (idx == last and dist < 2e-3):
            n += 1
        last = idx
        o = loc + d * 1e-3
    return n % 2 == 1

def inside_depth(part, p):
    """głębokość wnikania punktu p w część (0 = na zewnątrz lub styk). Test łączony: normalna najbliższego punktu
    (zawodna przy wierzchołkach leżących w płaszczyźnie odległej ściany) ORAZ parzystość promienia w 2 kierunkach
    (zawodna przy stycznych/zbieżnych ścianach brył zastępczych) — wnikanie uznane tylko, gdy oba testy je potwierdzają."""
    loc, nrm, idx, dist = part.bvh.find_nearest(Vector(p))
    if loc is None or dist <= 1e-4:
        return 0.0
    if (Vector(p) - loc).dot(nrm) >= 0:
        return 0.0
    if not (inside_parity(part, p, PARITY_DIRS[0]) or inside_parity(part, p, PARITY_DIRS[1])):
        return 0.0
    return dist

LAST_PEN = {}
def penetration(A, B, pairs):
    """max głębokość wnikania między A i B: wierzchołki przecinających się trójkątów A wewnątrz B (parzystość) i odwrotnie; głębokość = odległość do najbliższej powierzchni"""
    ia = set(); ib = set()
    for (i, j) in pairs:
        ia.update(A.polys[i]); ib.update(B.polys[j])
    best = 0.0; where = None
    for vi in ia:
        p = A.verts[vi]
        dist = inside_depth(B, p)
        if dist > best:
            best = dist; where = (A.name, tuple(round(c, 3) for c in p))
    for vi in ib:
        p = B.verts[vi]
        dist = inside_depth(A, p)
        if dist > best:
            best = dist; where = (B.name, tuple(round(c, 3) for c in p))
    LAST_PEN[(A.name, B.name)] = where
    return best

def _pt_on_edge(q, a, b, tol=2e-3):
    d = b - a; L2 = d.length_squared
    if L2 < 1e-12:
        return (q - a).length < tol
    t = max(0.0, min(1.0, (q - a).dot(d) / L2))
    return (q - (a + d * t)).length < tol

def tri_pair_class(ta, tb):
    """klasyfikacja pary trójkątów ze wspólnymi punktami: ('styk', 0) albo ('przeciecie', zanurzenie)"""
    na = (ta[1] - ta[0]).cross(ta[2] - ta[0]); nb = (tb[1] - tb[0]).cross(tb[2] - tb[0])
    if na.length < 1e-12 or nb.length < 1e-12:
        return "styk", 0.0
    na.normalize(); nb.normalize()
    if na.cross(nb).length < 1e-4:
        return "styk", 0.0          # współpłaszczyznowe (styk powierzchniowy)
    pts = []
    for (t1, t2) in ((ta, tb), (tb, ta)):
        for k in range(3):
            p0 = t1[k]; p1 = t1[(k + 1) % 3]; d = p1 - p0; L = d.length
            if L < 1e-9:
                continue
            h = intersect_ray_tri(t2[0], t2[1], t2[2], d / L, p0, True)
            if h is not None:
                t = (h - p0).dot(d) / (L * L)
                if -1e-6 <= t <= 1 + 1e-6:
                    pts.append(h)
    uniq = []
    for q in pts:
        if all((q - u).length > 1e-4 for u in uniq):
            uniq.append(q)
    if len(uniq) < 2:
        return "styk", 0.0          # styk punktowy
    s0, s1 = uniq[0], uniq[1]
    for t in (ta, tb):
        for k in range(3):
            if _pt_on_edge(s0, t[k], t[(k + 1) % 3]) and _pt_on_edge(s1, t[k], t[(k + 1) % 3]):
                return "styk", 0.0  # odcinek leży na krawędzi jednego z trójkątów (styk krawędziowy)
    def dip(t, n, o):
        ds = [(v - o).dot(n) for v in t]
        pos = max([x for x in ds if x > 0] + [0.0]); neg = max([-x for x in ds if x < 0] + [0.0])
        return min(pos, neg)
    return "przeciecie", max(dip(ta, nb, tb[0]), dip(tb, na, ta[0]))

def crossing(A, B, pairs):
    """liczba par transwersalnych i max zanurzenie trójkąta w płaszczyźnie drugiego"""
    n = 0; dmax = 0.0
    for (i, j) in pairs:
        for ta in A.tris[i]:
            for tb in B.tris[j]:
                c, d = tri_pair_class([A.verts[k] for k in ta], [B.verts[k] for k in tb])
                if c == "przeciecie":
                    n += 1; dmax = max(dmax, d)
    return n, dmax

def overlap(A, B):
    """(liczba par, wnikanie wierzchołkowe, pary, liczba par transwersalnych, zanurzenie)"""
    pairs = A.bvh.overlap(B.bvh)
    if not pairs:
        return 0, 0.0, [], 0, 0.0
    pen = penetration(A, B, pairs)
    nc, dmax = crossing(A, B, pairs)
    return len(pairs), pen, pairs, nc, dmax

def in_hook_zone(v):
    """czy punkt blatu leży w strefie haczyków (poza obrysem kołnierza 97,0)"""
    return (abs(v.x) > 96.9 and abs(v.y) < 6) or (abs(v.y) > 96.9 and (abs(v.x - 50) < 6 or abs(v.x + 50) < 6))

def in_bump_zone(v):
    """strefa garbów pokrywki (współrzędne końcowe): wewnętrzna strona kołnierza na wysokości rowka płytki"""
    return (max(abs(v.x), abs(v.y)) > 47.5) and (Z_PLATE_TOP - 2.7 <= v.z <= Z_PLATE_TOP - 1.3)

def sweep(name, moving, statics, dv_start, steps=200, hook_ok=False, extra_note="", bump_ok=False, info=False):
    """droga wsuwania: część 'moving' od pozycji +dv_start do końcowej po prostej; co krok test overlap/pen."""
    first_hit = None; max_pen = 0.0; hook_pen = 0.0; hook_z = None; detail = []
    dv_start = Vector(dv_start)
    for k in range(steps + 1):
        tfrac = 1.0 - k / steps
        dv = dv_start * tfrac
        M = moving.moved(dv)
        pen_here = 0.0; hook_here = 0.0; who = []
        for S in statics:
            n, pen, pairs, nc, dmax = overlap(M, S)
            pen_eff = max(pen, dmax if nc else 0.0)
            if n and pen_eff > EPS_PEN:
                if (hook_ok and S.name.startswith("ramka_korpus") and moving.name.startswith("ramka_blat")) or (bump_ok and S.name.startswith("ramka_plytka") and moving.name.startswith("ramka_pokrywka")):
                    ia = set()
                    for (i, j) in pairs: ia.update(M.polys[i])
                    zone = in_hook_zone if hook_ok else in_bump_zone
                    allhook = all(zone(M.verts[vi] - dv) for vi in ia)
                    if allhook:
                        if pen > hook_here:
                            hook_here = pen; RES.setdefault("ugiecie_gdzie", {})[name] = (round(dv.length, 2), LAST_PEN.get((M.name, S.name)))
                        if hook_z is None: hook_z = round(dv.z, 2)
                        continue
                pen_here = max(pen_here, pen_eff); who.append("%s(wierzch. %.3f, transw. %d par, zanurz. %.3f)" % (S.name.replace("ramka_", "").replace("_v2.stl", ""), pen, nc, dmax))
        hook_pen = max(hook_pen, hook_here)
        if pen_here > EPS_PEN:
            max_pen = max(max_pen, pen_here)
            if first_hit is None:
                first_hit = (round(dv.length, 2), who)
            detail.append((round(dv.length, 2), who))
    # pozycja końcowa: styk/przecięcie
    final = []
    for S in statics:
        n, pen, pairs, nc, dmax = overlap(moving, S)
        if n:
            pen_eff = max(pen, dmax if nc else 0.0)
            final.append((S.name.replace("ramka_", "").replace("_v2.stl", ""), n, round(pen_eff, 3), LAST_PEN.get((moving.name, S.name)) if pen > EPS_PEN else ("transwersalnie %d par" % nc if pen_eff > EPS_PEN else None)))
    flex_lim = P["snap_hook_h"] if hook_ok else ((P["cover_snap_bump"] - P["cover_clearance"] + 0.05) if bump_ok else None)
    rec = {"krok": name, "droga_od": [round(c, 2) for c in dv_start], "pierwsze_przeciecie_na_drodze": first_hit, "max_wnikanie_na_drodze": round(max_pen, 3),
           "ugiecie_haczyka": round(hook_pen, 3) if (hook_ok or bump_ok) else None, "haczyk_pierwszy_kontakt_dz": hook_z, "pozycja_koncowa_kontakty": final,
           "werdykt": ("OK" if (first_hit is None and all(p <= EPS_PEN for (_, _, p, _w) in final)) else "PRZECIECIE") + ((" (ugięcie %s %.2f ≤ %.2f)" % ("haczyka" if hook_ok else "garbu", hook_pen, flex_lim)) if (hook_ok or bump_ok) and hook_pen > 0 else ""), "uwaga": extra_note, "informacyjnie": info}
    if (hook_ok or bump_ok) and hook_pen > flex_lim + 1e-6:
        rec["werdykt"] = "PRZECIECIE (ugięcie %.2f > %.2f)" % (hook_pen, flex_lim)
    if info and rec["werdykt"].startswith("PRZECIECIE"):
        rec["werdykt"] = "INFORMACYJNIE: " + rec["werdykt"]
    RES["montaz"].append(rec)
    if rec["werdykt"].startswith("PRZECIECIE"):
        RES["blokujace"].append({"gdzie": "montaż / " + name, "opis": "pierwsze przecięcie %s, max wnikanie %.3f, końcowo %s" % (first_hit, max_pen, final), "typ": "montaz"})
    log("MONT %-60s %s | pierwsze=%s maxpen=%.3f | końcowo=%s" % (name[:60], rec["werdykt"], first_hit, max_pen, final))
    return rec

def box(name, x0, x1, y0, y1, z0, z1):
    vs = [Vector((x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    ps = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
    return Part(name, vs, ps)

def cyl(name, axis, c, r, a0, a1, n=48):
    """walec wzdłuż osi 'X' lub 'Y' lub 'Z', środek przekroju c (2 współrzędne pozostałe), od a0 do a1"""
    vs = []; ps = []
    for a in (a0, a1):
        for i in range(n):
            t = 2 * math.pi * i / n
            if axis == "X": vs.append(Vector((a, c[0] + r * math.cos(t), c[1] + r * math.sin(t))))
            elif axis == "Y": vs.append(Vector((c[0] + r * math.cos(t), a, c[1] + r * math.sin(t))))
            else: vs.append(Vector((c[0] + r * math.cos(t), c[1] + r * math.sin(t), a)))
    for i in range(n):
        j = (i + 1) % n
        ps.append([i, j, n + j, n + i])
    ps.append(list(range(n))[::-1]); ps.append(list(range(n, 2 * n)))
    return Part(name, vs, ps)

for K, kn in ((KORPUS_W, "W"), (KORPUS_P, "P")):
    pre = "korpus %s: " % kn
    # K1 Pi na bossy
    sweep(pre + "Pi+Bonnet (proxy) na bossy (z góry 20)", PI, [K], (0, 0, 20))
    # K2 dystanse na stadiony (każdy osobno), K3 panel na dystanse
    for i, D in enumerate(DYST):
        sweep(pre + "dystans %d na stadion (z góry 20)" % (i + 1), D, [K, PI], (0, 0, 20))
    sweep(pre + "panel (proxy) na dystanse (z góry 20)", PANEL, [K, PI] + DYST + [WTYK_B], (0, 0, 20))
    # K4 dyfuzor w kieszeni blatu (blat w pozycji, bez korpusu)
    if kn == "W":
        sweep("dyfuzor (proxy) w kieszeń blatu (z góry 20)", DYF, [BLAT], (0, 0, 20))
    # K5 blat (+dyfuzor) na korpus z haczykami
    blat_grp = Part("ramka_blat_v2.stl", BLAT.verts, BLAT.polys)
    rec = sweep(pre + "blat na korpus (haczyki; z góry 20)", blat_grp, [K, PANEL, PI] + DYST + [WTYK_B, GDC, GUSB, TUL], (0, 0, 20), hook_ok=True)
    sweep(pre + "dyfuzor (w blacie) opuszczany razem z blatem", DYF, [K, PANEL, PI] + DYST, (0, 0, 20))
    # K6/K7 czujniki Halla do kieszeni wkładki (z góry) oraz wkładka(+czujniki) na kołki
    if kn == "W":
        for k_ in "ABC":
            sweep("czujnik Halla %s (proxy) w kieszeń półki wkładki (z góry 20)" % k_, HALL[k_], [WK], (0, 0, 20))
        sweep("wkładka na kołki blatu (z góry 20)", WK, [BLAT, DYF, K, PANEL] + DYST, (0, 0, 20))
        for k_ in "ABC":
            sweep("czujnik Halla %s (w wkładce) opuszczany z wkładką" % k_, HALL[k_], [BLAT, DYF], (0, 0, 20))
        # K8 magnesy: ø5 x 2 w otworze ucha (z góry) i w kieszeni blatu (z góry; przed wkładką) — bryły własne
        for sx in (-1, 1):
            mag_b = cyl("magnes_blat_x%d" % (sx * 58), "Z", (sx * 58, 86), 2.5, Z_BLAT_TOP - 2.3, Z_BLAT_TOP - 0.3)
            sweep("magnes ø5×2 w kieszeń blatu x=%g (z góry 20)" % (sx * 58), mag_b, [BLAT], (0, 0, 20))
            mag_u = cyl("magnes_ucho_x%d" % (sx * 58), "Z", (sx * 58, 86), 2.5, Z_BLAT_TOP + 0.5, Z_BLAT_TOP + 2.5)
            sweep("magnes ø5×2 w otwór ucha wkładki x=%g (z góry 20; wkładka na blacie z magnesem blatu)" % (sx * 58), mag_u, [WK, BLAT, mag_b], (0, 0, 20))
        # K9 płytki (każdy plik) na wkładkę + czujniki + magnes A
        for f in PLATES:
            PL = PARTS[f]; short = f.replace("ramka_plytka_", "").replace("_v2.stl", "")
            sweep("płytka %s na wkładkę/kołek orientacyjny (z góry 20)" % short, PL, [WK, BLAT, DYF] + [HALL[k_] for k_ in "ABC"], (0, 0, 20))
        sweep("magnes A (proxy) w kieszeni płytki n1 — z płytką", MAG_A, [WK, BLAT, DYF] + [HALL[k_] for k_ in "ABC"], (0, 0, 20))
        # K10 pokrywka na płytkę
        for f in PLATES:
            PL = PARTS[f]; short = f.replace("ramka_plytka_", "").replace("_v2.stl", "")
            sweep("pokrywka na płytkę %s (z góry 20)" % short, POK, [PL, WK, BLAT], (0, 0, 20), bump_ok=True, extra_note="garby 0,7 przechodzą przez bok płytki (luz 0,3): dopuszczalne ugięcie kołnierza 0,4 (zatrzask), nie na końcu drogi")
    # K11 tulejka w otwór ø12 (od strony kieszeni, +X 20)
    sweep(pre + "tulejka DC w otwór ściany skrzynki (od kieszeni, +X 20)", TUL, [K], (-20, 0, 0), extra_note="luz 0 → oczekiwany styk walca z otworem (wnikanie ≤ sagitta tesselacji)")
    # K12 gniazdo DC: własna bryła — flansza ø14×2 + gwint ø8×7, od strony kieszeni wzdłuż +X; potem nakrętka proxy od wnętrza wzdłuż −X
    face_x = P["dc_pos_x"] - P["dc_pocket_wall"] - P["dc_bush_flange_t"]
    socket_my = Part("gniazdo_DC_wlasne", *(lambda a, b: (a.verts + b.verts, a.polys + [[i + len(a.verts) for i in p] for p in b.polys]))(
        cyl("fl", "X", (P["dc_pos_y"], P["dc_pos_z"]), 7.0, face_x - 2.0, face_x), cyl("th", "X", (P["dc_pos_y"], P["dc_pos_z"]), 4.0, face_x, face_x + 1 + 2 + 4)))
    sweep(pre + "gniazdo DC (flansza ø14 + gwint ø8) przez tulejkę (od kieszeni, +X 20)", socket_my, [K, TUL], (-20, 0, 0))
    sweep(pre + "nakrętka+korpus gniazda DC (proxy) od wnętrza (−X 20)", GDC, [K, TUL, PANEL, PI] + DYST, (20, 0, 0))
    # wejście gniazda do kieszeni przez okno (z tyłu, −Y 30) — przy x o 20 w lewo od pozycji końcowej
    sweep(pre + "gniazdo DC przez okno kieszeni (z tyłu, −Y 30; x −20)", socket_my.moved(Vector((-20, 0, 0))), [K], (0, 30, 0))
    # K13 wtyki
    plug_k = Part("wtyk_katowy", *(lambda a, b: (a.verts + b.verts, a.polys + [[i + len(a.verts) for i in p] for p in b.polys]))(
        cyl("b", "X", (P["dc_pos_y"], P["dc_pos_z"]), 5.5, face_x - 2 - 26, face_x - 2), box("c", face_x - 2 - 26, face_x - 2 - 15, P["dc_pos_y"], 110, P["dc_pos_z"] - 5.5, P["dc_pos_z"] + 5.5)))
    sweep(pre + "wtyk kątowy (26 + kabel ku +Y przez okno): wsuwanie na gniazdo (+X 12)", plug_k, [K, TUL, socket_my], (-12, 0, 0))
    sweep(pre + "wtyk kątowy: wejście przez okno (z tyłu, −Y 30; x −12)", plug_k.moved(Vector((-12, 0, 0))), [K, TUL, socket_my], (0, 30, 0))
    plug_p = Part("wtyk_prosty", *(lambda a, b: (a.verts + b.verts, a.polys + [[i + len(a.verts) for i in p] for p in b.polys]))(
        cyl("b", "X", (P["dc_pos_y"], P["dc_pos_z"]), 5.5, face_x - 2 - 40, face_x - 2), cyl("c", "X", (P["dc_pos_y"], P["dc_pos_z"]), 3.0, face_x - 2 - 52, face_x - 2 - 40)))
    sweep(pre + "wtyk prosty 40 + kabel 12 w osi: pozycja końcowa i wsuwanie (+X 12) — INFORMACYJNIE", plug_p, [K, TUL, socket_my], (-12, 0, 0), info=True, extra_note="4.11 liczy od lica −42 (zapas 1,5); tu lico gniazda −45 (kołnierz tulejki 1 + flansza gniazda 2) → kabel w osi wchodzi 1,5 w lewą ścianę skrzynki; kabel realnie zagina się wcześniej; rekomendowany wtyk kątowy")
    # K14 USB: od wnętrza +Y
    sweep(pre + "gniazdo USB (proxy, korpus 16×20×14) od wnętrza (+Y 20) — INFORMACYJNIE", GUSB, [K, PANEL] + DYST, (0, -20, 0), info=True, extra_note="droga 20 mm po prostej przecina dystans (60,60) stojący 14,3 przed bryłą; realnie wystarczy ≤ 8 mm ruchu (następny wiersz)")
    sweep(pre + "gniazdo USB (proxy) od wnętrza (+Y 8)", GUSB, [K, PANEL] + DYST, (0, -8, 0))
    # K15 wtyk Bonnetu w 3 kierunkach: pozycja i wsuwanie na gniazdo Bonnetu wzdłuż osi
    plug_mX = WTYK_B
    plug_mY = box("wtyk_bonnet_-Y", -45, -35, -68, -28, 23, 34)
    plug_pY = box("wtyk_bonnet_+Y", -45, -35, 28, 68, 23, 34)
    sweep(pre + "wtyk DC Bonnetu −X (proxy): wsuwanie na gniazdo (+X 7)", plug_mX, [K, PANEL] + DYST + [GDC, GUSB], (-7, 0, 0), extra_note="zapas do ściany 7,5 (D10) → wsuwanie ≤ 7 po prostej; dłuższa droga wymaga wpięcia wtyku przed przykręceniem Pi")
    sweep(pre + "wtyk DC Bonnetu −X (proxy): wsuwanie (+X 20) — INFORMACYJNIE", plug_mX, [K], (-20, 0, 0), info=True, extra_note="20 mm po prostej przecina lewą ścianę (zapas 7,5, D10)")
    sweep(pre + "wtyk DC Bonnetu −Y (x −45…−35, y −68…−28): wsuwanie (+Y 20)", plug_mY, [K, PANEL] + DYST + [GDC, GUSB], (0, -20, 0))
    sweep(pre + "wtyk DC Bonnetu +Y (x −45…−35, y 28…68): wsuwanie (−Y 9; skrzynka DC 10 za wtykiem)", plug_pY, [K, PANEL] + DYST + [GDC, GUSB], (0, 9, 0))
    sweep(pre + "wtyk DC Bonnetu +Y: wsuwanie (−Y 20) — INFORMACYJNIE", plug_pY, [K], (0, 20, 0), info=True, extra_note="20 mm po prostej przecina skrzynkę DC (zapas 10, 4.11)")
    if kn == "P":
        sweep(pre + "odbiornik USB (proxy) w port Pi (−X 20)", ODB, [K, PANEL] + DYST + [GUSB], (20, 0, 0))
    # stan złożony: wszystkie pary statyczne (styk dopuszczalny)
    statics = {"korpus": K, "blat": BLAT, "wkladka": WK, "plytka_n1": PL1, "pokrywka": POK, "tulejka": TUL, "dyfuzor": DYF, "panel": PANEL, "pi": PI, "wtyk_bonnet": WTYK_B, "gniazdo_dc": GDC, "gniazdo_usb": GUSB, "hall_A": HALL["A"], "hall_B": HALL["B"], "hall_C": HALL["C"], "magnes_A": MAG_A, "dystans_1": DYST[0], "dystans_2": DYST[1], "dystans_3": DYST[2], "dystans_4": DYST[3]}
    if kn == "P":
        statics["odbiornik"] = ODB
    names = list(statics)
    pairs_rep = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            A, B = statics[names[i]], statics[names[j]]
            n, pen, _, nc, dmax = overlap(A, B)
            if n:
                pen = max(pen, dmax if nc else 0.0)
                pairs_rep.append((names[i], names[j], n, round(pen, 3), LAST_PEN.get((A.name, B.name)) if pen > EPS_PEN else None))
                if pen > EPS_PEN:
                    RES["blokujace"].append({"gdzie": "złożenie %s: %s – %s" % (kn, names[i], names[j]), "opis": "przecięcie w pozycji złożonej, wnikanie %.3f (%d par trójkątów)" % (pen, n), "typ": "montaz"})
    RES["montaz"].append({"krok": "korpus %s: złożenie końcowe — pary ze wspólnymi trójkątami (styk = wnikanie ≤ 0,05)" % kn, "pary": pairs_rep, "werdykt": "OK" if all(p <= EPS_PEN for (_, _, _, p, _w) in pairs_rep) else "PRZECIECIE"})
    log("ZLOZENIE %s: pary stykowe/przecięcia: %s" % (kn, pairs_rep))

# =========================================================================== ZAPIS
blok = [b for b in RES["blokujace"]]
RES["podsumowanie"] = {"blokujace_surowe": len(blok), "pasowania": len(RES["pasowania"]), "wymiary": len(RES["wymiary"]), "scianki": len(RES["scianki"]), "montaz": len(RES["montaz"])}
with open(os.path.join(OUT_DIR, "trzecie_oko_wyniki.json"), "w", encoding="utf-8") as fo:
    json.dump(RES, fo, ensure_ascii=False, indent=1, default=str)

def fmt(v):
    if v is None: return "—"
    if isinstance(v, float): return ("%.3f" % v).replace(".", ",")
    return str(v)
L = []
L.append("## Tabela A. Transformacje STL → złożenie (D3)\n")
L.append("| STL | obiekt .blend | typ | przesunięcie (x, y, z) | max odległość wierzchołków | liczba wierzchołków/trójkątów zgodna |")
L.append("|---|---|---|---|---|---|")
for t in RES["transformacje"]:
    if "typ" in t:
        L.append("| `%s` | %s | %s | %s | %.1e | %s |" % (t["stl"], t["obiekt_blend"], t["typ"], tuple(t["t"]), t["max_odleglosc_wierzcholkow"], "tak" if t["liczba_wierzch_zgodna"] else "NIE"))
L.append("\n| część | sprawdzenie D3/D4 | bbox min | bbox max | ok |\n|---|---|---|---|---|")
for t in RES["transformacje"]:
    if "sprawdzenie_D3D4" in t:
        L.append("| %s | %s | %s | %s | %s |" % (t["stl"], t["sprawdzenie_D3D4"], t["bbox_min"], t["bbox_max"], "✓" if t["ok"] else "✗"))
L.append("\n## Tabela B. Karta pasowań (luzy z siatek STL i brył zastępczych)\n")
L.append("| Para | Miejsce / punkt | Luz z planu | Luz zmierzony | Reguła 4.8 / źródło | Werdykt | Uwaga |")
L.append("|---|---|---|---|---|---|---|")
for r in RES["pasowania"]:
    L.append("| %s | %s | %s | %s | %s | %s | %s |" % (r["para"], r["miejsce"], fmt(r["luz_plan"]), fmt(r["luz_zmierzony"]), r["regula"], r["werdykt"], r["uwaga"]))
L.append("\n## Tabela C. Gabaryty STL (orientacja druku, bbox)\n")
L.append("| STL | X × Y × Z | min | max | wierzchołki | trójkąty |\n|---|---|---|---|---|---|")
for g in RES["gabaryty"]:
    L.append("| `%s` | %s × %s × %s | %s | %s | %d | %d |" % (g["stl"], fmt(g["gabaryt"][0]), fmt(g["gabaryt"][1]), fmt(g["gabaryt"][2]), g["min"], g["max"], g["wierzcholki"], g["trojkaty"]))
L.append("\n## Tabela D. Wymiary (układ złożeniowy D3; tolerancja 0,05)\n")
L.append("| STL | Wymiar | Parametr | Oczekiwane | Zmierzone | Różnica | Metoda | Werdykt |")
L.append("|---|---|---|---|---|---|---|---|")
for r in RES["wymiary"]:
    L.append("| `%s` | %s | %s | %s | %s | %s | %s | %s |" % (r["stl"], r["wymiar"], r["parametr"], fmt(r["oczekiwane"]), fmt(r["zmierzone"]), fmt(r["roznica"]), r["metoda"], r["werdykt"]))
L.append("\n## Tabela E. Ścianki minimalne\n")
L.append("| STL | Miejsce | Oczekiwane | Zmierzone | Punkt | Min. | Werdykt | Uwaga |\n|---|---|---|---|---|---|---|---|")
for r in RES["scianki"]:
    L.append("| `%s` | %s | %s | %s | %s | %s | %s | %s |" % (r["stl"], r["miejsce"], fmt(r["oczekiwane"]), fmt(r["zmierzone"]), r["punkt"], r["min"], r["werdykt"], r["uwaga"]))
L.append("\n## Tabela F. Symulacja montażu (BVHTree.overlap + głębokość wnikania; krok 0,1 mm)\n")
L.append("| Krok | Droga od | Pierwsze przecięcie na drodze (odległość od pozycji końcowej, co) | Max wnikanie na drodze | Ugięcie haczyka / pierwszy kontakt (dz) | Pozycja końcowa: kontakty (część, pary trójkątów, wnikanie) | Werdykt | Uwaga |")
L.append("|---|---|---|---|---|---|---|---|")
for r in RES["montaz"]:
    if "pary" in r:
        L.append("| %s | — | — | — | — | %s | %s | |" % (r["krok"], r["pary"], r["werdykt"]))
    else:
        L.append("| %s | %s | %s | %s | %s / %s | %s | %s | %s |" % (r["krok"], r["droga_od"], r["pierwsze_przeciecie_na_drodze"], fmt(r["max_wnikanie_na_drodze"]), fmt(r["ugiecie_haczyka"]), r["haczyk_pierwszy_kontakt_dz"], r["pozycja_koncowa_kontakty"], r["werdykt"], r["uwaga"]))
if "profil_haczyka" in RES:
    L.append("\n## Profil haczyków blatu (czubek w funkcji Z, promienie poziome; rampa od dołu)\n")
    for nm, prof in RES["profil_haczyka"].items():
        L.append("- %s: " % nm + ", ".join("Z %.2f→%s" % (z, fmt(x)) for z, x in prof))
with open(os.path.join(OUT_DIR, "tabele_auto.md"), "w", encoding="utf-8") as fo:
    fo.write("\n".join(L))

log("=== BLOKUJĄCE (surowe, przed oceną): %d" % len(blok))
for b in blok:
    log("  -", b)
log("KONIEC; pasowania=%d wymiary=%d scianki=%d montaz=%d" % (len(RES["pasowania"]), len(RES["wymiary"]), len(RES["scianki"]), len(RES["montaz"])))
