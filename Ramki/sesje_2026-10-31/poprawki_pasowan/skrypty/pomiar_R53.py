"""Niezależny pomiar pasowań R53 ze ZNAKIEM luzu (trimesh, promienie) — sesja POPRAWKI PASOWAŃ, 31.10.2026.
Uruchomienie: PYTHONUTF8=1 py -3.12 -I pomiar_R53.py <katalog_stl> <wynik.json>
Luz = (współrzędna pierwszej powierzchni części B w kierunku +e) − (współrzędna pierwszej powierzchni części A w kierunku −e),
mierzone z JEDNEGO punktu leżącego w szczelinie; dodatni = szczelina, ujemny = przenikanie/wcisk. Nie używa abs().
Układ złożeniowy D3 (korpus: dno Z 0, przód −Y). Transformacje z orientacji druku: blat obrót 180° wokół X + Z 63,6;
wkładka: końce kołków Z 0 → spód ramy na 63,6, środek XY = środek otworu; płytka n1: spód 66,1; tulejka: oś X w (y 89, Z 30),
kołnierz na licu x −42 (tylko średnice)."""
import sys, os, json, math
import numpy as np
import trimesh
from trimesh.ray.ray_triangle import RayMeshIntersector

STL = sys.argv[1]
OUT = sys.argv[2]
PAR = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "parametry.json")
P = {}
for g, sub in json.load(open(PAR, encoding="utf-8")).items():
    if g.startswith("_"):
        continue
    for k, v in sub.items():
        P[k] = v["value"]
ZT = 63.6  # blat_top_z (zamrożone R50-1)

def load(name, M=None):
    m = trimesh.load(os.path.join(STL, name + ".stl"), force="mesh")
    if M is not None:
        m.apply_transform(M)
    m.ray = RayMeshIntersector(m)
    return m

def T(dx, dy, dz):
    M = np.eye(4); M[:3, 3] = [dx, dy, dz]; return M

def rotX180():
    M = np.eye(4); M[1, 1] = -1; M[2, 2] = -1; return M

AX = {"X": np.array([1.0, 0, 0]), "Y": np.array([0, 1.0, 0]), "Z": np.array([0, 0, 1.0])}

def first(m, p, d):
    """odległość do pierwszej powierzchni z punktu p w kierunku d (None = brak)"""
    loc, _, _ = m.ray.intersects_location([np.asarray(p, float)], [np.asarray(d, float)], multiple_hits=True)
    if len(loc) == 0:
        return None
    dd = np.linalg.norm(loc - np.asarray(p, float), axis=1)
    dd = dd[dd > 1e-6]
    return float(dd.min()) if len(dd) else None

def coord(m, p, axis, sgn):
    """współrzędna (wzdłuż osi) pierwszej powierzchni z p w kierunku sgn*axis"""
    d = first(m, p, AX[axis] * sgn)
    return None if d is None else float(np.dot(np.asarray(p, float), AX[axis]) + sgn * d)

def chord(m, p, axis):
    a, b = first(m, p, AX[axis]), first(m, p, -AX[axis])
    return None if a is None or b is None else a + b

def gap(mA, mB, p, axis, sgn=1):
    """luz ze znakiem między A (w kierunku −sgn·axis od p) a B (w kierunku +sgn·axis): B − A"""
    a = coord(mA, p, axis, -sgn); b = coord(mB, p, axis, sgn)
    return None if a is None or b is None else sgn * (b - a)

rows = []
def add(pas, przed_nom, po_nom, val, kier, uwaga=""):
    rows.append({"pasowanie": pas, "nominal_przed": przed_nom, "nominal_po": po_nom, "zmierzone": None if val is None else round(val, 3), "kierunek": kier, "uwaga": uwaga})

# ---------------------------------------------------------------- wczytanie
K = load("ramka_korpus_W_v2")
KP = load("ramka_korpus_P_v2")
BL = load("ramka_blat_v2", T(0, 0, ZT) @ rotX180())          # wierzch na 63,6, kołnierz do 49,6
wk_raw = trimesh.load(os.path.join(STL, "ramka_wkladka_v2.stl"), force="mesh")
b = wk_raw.bounds
# środek X: środek obrysu ramy (uszy symetryczne, więc = środek bbox); środek Y: y_min + (otwór/2 + 4)
zw = P["insert_opening"] / 2 + P["insert_wall_w"]
WK = load("ramka_wkladka_v2", T(-(b[0][0] + b[1][0]) / 2, -(b[0][1] + zw), ZT - P["tab_pin_h"] - b[0][2]))
# spód ramy w STL na Z = b0z + 3,5 (kołki 3,5); ma trafić na 63,6 → końce kołków na 60,1
pl_raw = trimesh.load(os.path.join(STL, "ramka_plytka_wieczorna_n1_v2.stl"), force="mesh")
pb = pl_raw.bounds
PL = load("ramka_plytka_wieczorna_n1_v2", T(-(pb[0][0] + pb[1][0]) / 2, -(pb[0][1] + pb[1][1]) / 2, ZT + P["insert_shelf_h"] - pb[0][2]))
TU = load("ramka_tulejka_dc_v2")

info = {"blat_bbox": BL.bounds.tolist(), "wkladka_bbox": WK.bounds.tolist(), "plytka_bbox": PL.bounds.tolist(),
        "watertight": {n: bool(m.is_watertight) for n, m in (("korpus_W", K), ("korpus_P", KP), ("blat", BL), ("wkladka", WK), ("plytka_n1", PL), ("tulejka", TU))}}

# ---------------------------------------------------------------- T1 kołnierz blatu – ściana korpusu
zk = ZT - P["blat_t"] - 5.0   # 54,6: środek wysokości kołnierza
for KK, kn in ((K, "W"), (KP, "P")):
    for (nm, p, ax, sg) in (("prawa", (97.15, 30, zk), "X", 1), ("lewa", (-97.15, 30, zk), "X", -1), ("przednia", (30, -97.15, zk), "Y", -1), ("tylna (x 30)", (30, 97.15, zk), "Y", 1), ("tylna (x −30)", (-30, 97.15, zk), "Y", 1)):
        add("T1 kołnierz blatu – ściana korpusu %s, %s" % (kn, nm), 0.5, P["blat_skirt_clearance"], gap(BL, KK, p, ax, sg), ax, "z punktu w szczelinie (lico kołnierza → ściana wewn.)")

# ---------------------------------------------------------------- T2/T3 haczyki
so = P["box_outer"] / 2 - P["wall_t"] - P["blat_skirt_clearance"]   # 96,8
wall_in = P["box_outer"] / 2 - P["wall_t"]                          # 97,5
zh = P["snap_hook_z"] + P["snap_hook_hgt"] * 0.75                   # 54,35: płaska część występu
hooks = (("prawy", "X", 1, "Y", P["snap_side_y"]), ("lewy", "X", -1, "Y", P["snap_side_y"]), ("przedni", "Y", -1, "X", P["snap_front_x"]), ("tylny", "Y", 1, "X", P["snap_rear_x"]))
def pt(ax, sg, r, along_val, z):
    return (sg * r, along_val, z) if ax == "X" else (along_val, sg * r, z)
for KK, kn in ((K, "W"), (KP, "P")):
    for (nm, ax, sg, along, at) in hooks:
        tip = coord(BL, pt(ax, sg, 110, at, zh), ax, -sg)                   # czubek haczyka (od zewnątrz)
        wall = coord(KK, pt(ax, sg, 90, at, P["snap_pocket_z"] - 1.0), ax, sg)   # ściana wewn. pod kieszenią
        add("T2 haczyk %s: zahaczenie (czubek − ściana wewn.) korpus %s" % (nm, kn), 0.8, P["snap_hook_h"] - P["blat_skirt_clearance"], None if None in (tip, wall) else sg * (tip - wall), ax, "czubek %.3f, ściana %.3f" % (abs(tip), abs(wall)))
        # luz czubek – dno kieszeni: z punktu między czubkiem (98,3) a dnem (98,8)
        luz_dno = P["blat_skirt_clearance"] + P["snap_pocket_depth"] - P["snap_hook_h"]
        pg = pt(ax, sg, (abs(tip) + luz_dno / 2) if tip is not None else 98.55, at, zh)   # punkt w połowie nominalnej szczeliny
        add("T2 haczyk %s: luz czubek – dno kieszeni, korpus %s" % (nm, kn), 0.2, P["blat_skirt_clearance"] + P["snap_pocket_depth"] - P["snap_hook_h"], gap(BL, KK, pg, ax, sg), ax, "punkt w szczelinie za czubkiem")
        # luz nad występem: z punktu w kieszeni nad haczykiem
        luz_nad = P["snap_pocket_z"] + P["snap_pocket_h"] - P["snap_hook_z"] - P["snap_hook_hgt"]
        pz = pt(ax, sg, so + 1.1, at, P["snap_pocket_z"] + P["snap_pocket_h"] - luz_nad / 2)   # punkt w połowie nominalnej szczeliny nad haczykiem
        add("T3 haczyk %s: luz nad występem (sufit kieszeni − górna krawędź), korpus %s" % (nm, kn), 0.25, P["snap_pocket_z"] + P["snap_pocket_h"] - P["snap_hook_z"] - P["snap_hook_hgt"], gap(BL, KK, pz, "Z", 1), "Z", "punkt (%.2f) w kieszeni nad haczykiem" % pz[2])
        # luz pod występem: profil haczyka promieniami poziomymi co 0,01 → start rampy (x > so + 0,02)
        zs = [round(P["snap_pocket_z"] - 1.0 + 0.01 * i, 2) for i in range(0, int(3.0 / 0.01) + 1)]
        prof = [(z, coord(BL, pt(ax, sg, 110, at, z), ax, -sg)) for z in zs]
        out_ = [z for z, x_ in prof if x_ is not None and abs(x_) > so + 0.02]
        z_start = min(out_) if out_ else None; z_top = max(out_) if out_ else None
        floor = coord(KK, pt(ax, sg, so + 1.1, at, zh), "Z", -1)
        ceil = coord(KK, pt(ax, sg, so + 1.1, at, zh), "Z", 1)
        add("T3 haczyk %s: luz pod występem (start rampy − dno kieszeni), korpus %s" % (nm, kn), 0.25, P["snap_hook_z"] - P["snap_pocket_z"], None if None in (z_start, floor) else z_start - floor, "Z", "start rampy Z %s, górna krawędź %s, dno kieszeni %s, sufit %s" % (z_start, z_top, None if floor is None else round(floor, 3), None if ceil is None else round(ceil, 3)))
        # luz boczny: cięciwa kieszeni wzdłuż 'along' vs cięciwa haczyka
        pk = chord(KK, pt(ax, sg, wall_in + 0.5, at, zh), along)
        hk = chord(BL, pt(ax, sg, so + 0.8, at, zh), along)
        add("T3c haczyk %s: luz boczny (kieszeń − haczyk)/2, korpus %s" % (nm, kn), 1.0, (P["snap_pocket_w"] - P["snap_hook_w"]) / 2, None if None in (pk, hk) else (pk - hk) / 2, along, "kieszeń %s, haczyk %s" % (None if pk is None else round(pk, 3), None if hk is None else round(hk, 3)))
    # ściana za kieszenią (prawa, y = 0)
    add("T2b ściana korpusu %s za kieszenią zatrzasku (prawa)" % kn, 1.5, P["wall_t"] - P["snap_pocket_depth"], chord(KK, (wall_in + P["snap_pocket_depth"] + 0.6, 0, zh), "X"), "X", "cięciwa w materiale")
    add("T2b ściana korpusu %s za kieszenią zatrzasku (przednia, x 50)" % kn, 1.5, P["wall_t"] - P["snap_pocket_depth"], chord(KK, (50, -(wall_in + P["snap_pocket_depth"] + 0.6), zh), "Y"), "Y", "cięciwa w materiale (bez reliefu: relief na zewnątrz)")

# ---------------------------------------------------------------- T4 wkręty tylne
for KK, kn in ((K, "W"), (KP, "P")):
    for sx in (-1, 1):
        x = sx * P["blat_screw_pitch"] / 2; z = P["blat_screw_z"]
        add("T4 otwór wkrętu blatu x=%g: ø w ścianie (X), korpus %s" % (x, kn), 3.2, P["blat_screw_hole_d"], chord(KK, (x, 98.2, z), "X"), "X")
        add("T4 otwór wkrętu blatu x=%g: ø w ścianie (Z), korpus %s" % (x, kn), 3.2, P["blat_screw_hole_d"], chord(KK, (x, 98.2, z), "Z"), "Z")
        add("T4 otwór wkrętu blatu x=%g: ø przy licu (pogłębienie), korpus %s" % (x, kn), 6.1, 6.1, chord(KK, (x, 99.9, z), "X"), "X", "stożek 90° ø6,3 → 6,1 na y 99,9 (bez zmian)")
        cx_k = (coord(KK, (x, 98.2, z), "X", 1) + coord(KK, (x, 98.2, z), "X", -1)) / 2
        cz_k = (coord(KK, (x, 98.2, z), "Z", 1) + coord(KK, (x, 98.2, z), "Z", -1)) / 2
        cx_b = (coord(BL, (x, 94, z), "X", 1) + coord(BL, (x, 94, z), "X", -1)) / 2
        cz_b = (coord(BL, (x, 94, z), "Z", 1) + coord(BL, (x, 94, z), "Z", -1)) / 2
        add("T4 współosiowość otwór ściany – otwór słupka x=%g, korpus %s" % (x, kn), 0.0, 0.0, math.hypot(cx_k - cx_b, cz_k - cz_b), "XZ", "środki: ściana (%.3f, %.3f), słupek (%.3f, %.3f)" % (cx_k, cz_k, cx_b, cz_b))
for sx in (-1, 1):
    x = sx * P["blat_screw_pitch"] / 2; z = P["blat_screw_z"]
    add("T4 otwór słupka x=%g: ø (blat)" % x, 2.5, P["insert_hole_m3"], chord(BL, (x, 94, z), "X"), "X")
    dno = coord(BL, (x, 94, z), "Y", -1)
    add("T4 otwór słupka x=%g: dno (y)" % x, 91.0, so - P["blat_post_hole_depth"], dno, "Y")
    add("T4 dno słupka x=%g pod otworem (materiał)" % x, 1.8, so - P["blat_post_hole_depth"] - P["blat_post_y0"], chord(BL, (x, P["blat_post_y0"] + 0.3, z), "Y"), "Y", "cięciwa w materiale 89,2…dno")
    add("T4 wkręt M3×8 x=%g: gwint w słupku (lico − (100 − 8))" % x, 5.0, so - 92.0, None if dno is None else (coord(BL, (x + 2.0, 120, z), "Y", -1) - 92.0), "Y", "lico kołnierza (promień obok otworu, x+2) − koniec wkrętu 100 − 8")

# ---------------------------------------------------------------- T5 kołek wkładki w blacie
for sx in (-1, 1):
    x, y = sx * P["tab_pos_x"], P["tab_pin_y"]; z = ZT - 2.0
    r_mid = (P["tab_pin_d"] + P["blat_pin_hole_d"]) / 4
    for (d_, off, sg) in (("X", (r_mid, 0), 1), ("X", (-r_mid, 0), -1), ("Y", (0, r_mid), 1), ("Y", (0, -r_mid), -1)):
        add("T5 kołek wkładki x=%g w otworze blatu: luz promieniowy %s%s" % (x, "+" if sg > 0 else "−", d_), 0.15, (P["blat_pin_hole_d"] - P["tab_pin_d"]) / 2, gap(WK, BL, (x + off[0], y + off[1], z), d_, sg), d_, "z punktu w szczelinie (kołek → ściana otworu)")
    add("T5 otwór kołka x=%g: ø (blat)" % x, 3.3, P["blat_pin_hole_d"], chord(BL, (x, y, z), "X"), "X")
    add("T5 kołek x=%g: ø (wkładka)" % x, 3.0, P["tab_pin_d"], chord(WK, (x, y, z), "X"), "X")
    tip = coord(WK, (x, y, ZT - 10), "Z", 1); bot = coord(BL, (x, y, ZT - 0.5), "Z", -1)
    add("T5 kołek x=%g: luz osiowy (koniec kołka − dno otworu)" % x, 0.3, P["blat_pin_hole_depth"] - P["tab_pin_h"], None if None in (tip, bot) else tip - bot, "Z")

# ---------------------------------------------------------------- T6 płytka we wkładce
c = P["plate_size"] / 2 + (P["insert_opening"] - P["plate_size"]) / 4   # punkt w szczelinie
zp = ZT + P["insert_shelf_h"] + 2.0
for (nm, p, ax, sg) in (("prawa y=20", (c, 20, zp), "X", 1), ("prawa y=−30", (c, -30, zp), "X", 1), ("lewa y=20", (-c, 20, zp), "X", -1), ("tylna x=20", (20, c, zp), "Y", 1), ("przednia x=30", (30, -c, zp), "Y", -1), ("przednia x=−30", (-30, -c, zp), "Y", -1)):
    add("T6 płytka n1 – wkładka: %s" % nm, 0.3, (P["insert_opening"] - P["plate_size"]) / 2, gap(PL, WK, p, ax, sg), ax, "z punktu w szczelinie (bok płytki → ściana otworu)")
add("T6 otwór wkładki X (cięciwa)", 96.6, P["insert_opening"], chord(WK, (0, 0, zp), "X"), "X")
add("T6 otwór wkładki Y (cięciwa, x 20)", 96.6, P["insert_opening"], chord(WK, (20, 0, zp), "Y"), "Y")
add("T6 rama wkładki zewn. X", 104.6, P["insert_opening"] + 2 * P["insert_wall_w"], (coord(WK, (150, 0, zp), "X", -1) - coord(WK, (-150, 0, zp), "X", 1)), "X")
add("T6 gabaryt wkładki Y (bbox)", 148.3, zw + P["tab_end_y"], float(WK.bounds[1][1] - WK.bounds[0][1]), "Y")
add("T6 płytka n1 bok X (promienie z zewnątrz)", 96.0, P["plate_size"], coord(PL, (150, 20, zp), "X", -1) - coord(PL, (-150, 20, zp), "X", 1), "X", "interfejs płytki bez zmian")
# kołek orientacyjny – wycięcie D (płytka wycentrowana): luz po stronie otwartej
pc = P["insert_opening"] / 2 - P["orient_post_gap"] - P["orient_post"] / 2
post_in = coord(WK, (pc - 5, -pc, zp), "X", 1)              # wewn. lico kołka (od środka)
notch = coord(PL, (pc - 5, -pc, zp), "X", 1)                # lico wycięcia płytki
add("T6 kołek orientacyjny – wycięcie płytki (x, strona otwarta)", 0.4, pc - P["orient_post"] / 2 - (P["plate_size"] / 2 - P["notch_size"]), None if None in (post_in, notch) else post_in - notch, "X", "lico kołka %s − lico wycięcia %s" % (post_in, notch))
add("T6 kołek orientacyjny – ściana otworu (x)", 0.5, P["orient_post_gap"], gap(WK, WK, (P["insert_opening"] / 2 - P["orient_post_gap"] / 2, -pc, zp), "X", 1), "X", "szczelina kołek–rama")
add("T6 margines matrycy: krawędź ramy → krawędź panelu (80)", 27.7, P["panel_size"] / 2 - zw, P["panel_size"] / 2 - coord(WK, (150, 0, zp), "X", -1), "X")

# ---------------------------------------------------------------- T12 rowek panelu
N = np.array([1.0, -1.0, 0]) / math.sqrt(2)
for KK, kn in ((K, "W"), (KP, "P")):
    a, b2 = first(KK, (60, 60, 1.5), N), first(KK, (60, 60, 1.5), -N)
    add("T12 rowek panelu (60,60): szerokość prostopadle do przekątnej, korpus %s" % kn, 3.4, P["panel_slot_w"], None if None in (a, b2) else a + b2, "N")
    add("T12 rowek panelu: cięciwa wzdłuż X (= szer·√2), korpus %s" % kn, 4.808, P["panel_slot_w"] * math.sqrt(2), chord(KK, (60, 60, 1.5), "X"), "X")

# ---------------------------------------------------------------- T7 tulejka (bez zmian, celowo wciskowe)
tb = TU.bounds
walec_d = None
# walec: cięciwa w Z między kołnierzem a końcem (Z 1…3), przez oś (środek bbox)
cxy = ((tb[0][0] + tb[1][0]) / 2, (tb[0][1] + tb[1][1]) / 2)
a = coord(TU, (cxy[0] + 20, cxy[1], 2.0), "X", -1); b2 = coord(TU, (cxy[0] - 20, cxy[1], 2.0), "X", 1)
walec_d = None if None in (a, b2) else a - b2
hole = chord(K, (-41, P["dc_pos_y"], P["dc_pos_z"]), "Y")
add("T7 tulejka DC: ø walca (STL)", 11.85, P["dc_bush_outer_d"], walec_d, "X")
add("T7 otwór DC ø w korpusie W (Y)", 12.0, P["dc_hole_d"], hole, "Y")
add("T7 tulejka w otworze: luz/stronę (ujemny = wcisk)", 0.075, (P["dc_hole_d"] - P["dc_bush_outer_d"]) / 2, None if None in (hole, walec_d) else (hole - walec_d) / 2, "Y", "CELOWO WCISKOWE (R52/R53): wartość dodatnia = luz nominalny 0,075 wg definicji 4.8 „wciskane” (średnica tulejki mniejsza o 0,15; realny wcisk powstaje przez skurcz żywicy i mniejszy otwór MJF) — druk własny po pomiarze otworu")

# ---------------------------------------------------------------- łańcuch wysokości (kontrola, bez zmian)
add("łańcuch: wierzch ściany korpusu W", 59.6, P["korpus_h"], coord(K, (98.75, 20, 200), "Z", -1), "Z")
add("łańcuch: wierzch blatu (90, 0)", 63.6, ZT, coord(BL, (90, 0, 200), "Z", -1), "Z")
add("łańcuch: spód blatu na wierzchu ściany (styk)", 0.0, 0.0, coord(BL, (98.75, 30, 55), "Z", 1) - coord(K, (98.75, 30, 55), "Z", 1), "Z", "promienie +Z z wnętrza: spód blatu − wierzch ściany")
add("łańcuch: wierzch ramy wkładki (0, 50,3)", 69.6, ZT + P["insert_h"], coord(WK, (0, 50.3, 200), "Z", -1), "Z")
add("łańcuch: wierzch płytki n1 (0, −46,5)", 74.1, ZT + P["insert_shelf_h"] + P["plate_thickness"], coord(PL, (0, -46.5, 200), "Z", -1), "Z")

json.dump({"info": info, "rows": rows}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("OK", len(rows), "pomiarow ->", OUT)
for r in rows:
    print("%-80s przed %-7s po %-7s zm %s" % (r["pasowanie"][:80], r["nominal_przed"], round(r["nominal_po"], 3) if isinstance(r["nominal_po"], float) else r["nominal_po"], r["zmierzone"]))
