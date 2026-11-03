"""Niezależne pomiary siatek STL (trimesh, promienie) — DESIGN A, 31.10.2026.
Uruchomienie: PYTHONUTF8=1 py -3.12 -I pomiar_stl.py
Wynik: pomiary_stl.md + pomiary_stl.json w tym folderze. Niczego nie zapisuje poza tym folderem.
Układy: korpus = globalny D3 (dno Z 0, przód −Y). Blat i pokrywka: STL wierzchem w dół (wierzch na Z 0).
Wkładka: kołki ustalające w dół (końce kołków Z 0, spód ramy Z 3,5). Płytki: spód Z 0, wierzch Z 8.
Tulejka: kołnierz na Z 0…1. Podkładki: płasko.
"""
import os, json, math
import numpy as np
import trimesh
from trimesh.ray.ray_triangle import RayMeshIntersector

BASE = r"<PC>\Desktop\Ramki\wyniki_v2\stl"
OUT = os.path.dirname(os.path.abspath(__file__))
TOL = 0.05

_cache = {}
def mesh(name):
    if name not in _cache:
        m = trimesh.load(os.path.join(BASE, name + ".stl"), force="mesh")
        m.ray = RayMeshIntersector(m)
        _cache[name] = m
    return _cache[name]

AX = {"X": np.array([1.0, 0, 0]), "Y": np.array([0, 1.0, 0]), "Z": np.array([0, 0, 1.0]),
      "D": np.array([1.0, 1.0, 0]) / math.sqrt(2),      # przekątna (+x,+y)
      "N": np.array([1.0, -1.0, 0]) / math.sqrt(2)}     # prostopadle do przekątnej

def first_hit(m, origin, direction):
    origin = np.asarray(origin, float); direction = np.asarray(direction, float)
    loc, idx_ray, idx_tri = m.ray.intersects_location([origin], [direction], multiple_hits=True)
    if len(loc) == 0:
        return None
    d = np.linalg.norm(loc - origin, axis=1)
    d = d[d > 1e-6]
    return float(d.min()) if len(d) else None

def chord(m, p, axis):
    """szerokość pustki (lub materiału) przez punkt p wzdłuż osi: suma odległości do pierwszych trafień w obie strony"""
    a = AX[axis]
    dp, dm = first_hit(m, p, a), first_hit(m, p, -a)
    if dp is None or dm is None:
        return None
    return dp + dm

def surf(m, p, axis, sign):
    """współrzędna (wzdłuż osi) pierwszej powierzchni trafionej z punktu p w kierunku sign*axis; zwraca rzut na oś"""
    a = AX[axis] * sign
    d = first_hit(m, p, a)
    if d is None:
        return None
    hit = np.asarray(p, float) + a * d
    return float(np.dot(hit, AX[axis]))

rows = []   # (plik, cecha, metoda, zmierzone, nominał, źródło nominału)
def add(plik, cecha, metoda, val, nom, src=""):
    rows.append({"plik": plik, "cecha": cecha, "metoda": metoda,
                 "zmierzone": None if val is None else round(val, 3), "nominal": nom, "zrodlo": src})

def bbox(name):
    m = mesh(name); b = m.bounds
    return b[0], b[1], b[1] - b[0], m.volume / 1000.0, m.is_watertight

# ---------------------------------------------------------------- KORPUS
for K in ("ramka_korpus_W_v2", "ramka_korpus_P_v2"):
    m = mesh(K); lo, hi, sz, vol, wt = bbox(K)
    add(K, "gabaryt X / Y / Z (bbox)", "bbox", sz[0], 200, "box_outer"); add(K, "gabaryt Y z napisem", "bbox", sz[1], 200.6, "+label_relief_h 0,6")
    add(K, "wysokość korpusu", "bbox Z", sz[2], 59.6, "korpus_h"); add(K, "objętość [cm³]", "mesh", vol, None, "arkusz 233,66/233,63")
    add(K, "wnętrze X (y 20, Z 30)", "cięciwa", chord(m, (0, 20, 30), "X"), 195, "box_outer-2·wall_t")
    add(K, "wnętrze Y (x 20, Z 30)", "cięciwa", chord(m, (20, 0, 30), "Y"), 195, "")
    add(K, "ściana prawa grubość (98,75, 20, 30)", "cięciwa w materiale", chord(m, (98.75, 20, 30), "X"), 2.5, "wall_t")
    add(K, "ściana przednia grubość (20, −98,75, 30)", "cięciwa w materiale", chord(m, (20, -98.75, 30), "Y"), 2.5, "wall_t")
    add(K, "ściana tylna grubość (20, 98,75, 45)", "cięciwa w materiale", chord(m, (20, 98.75, 45), "Y"), 2.5, "wall_t")
    add(K, "dno grubość (20, −20, 1,5)", "cięciwa w materiale", chord(m, (20, -20, 1.5), "Z"), 3.0, "floor_t")
    add(K, "wierzch ściany Z (98,75, 20)", "trafienie −Z", surf(m, (98.75, 20, 200), "Z", -1), 59.6, "korpus_h")
    add(K, "naroże pionowe R5: x lica przy y=−99", "trafienie −X", surf(m, (150, -99, 30), "X", -1), 95 + math.sqrt(25 - 16), "box_corner_r 5 → 98,0")
    add(K, "dolna krawędź R3: z lica przy x=99,5", "trafienie +Z", surf(m, (99.5, 20, -10), "Z", +1), 3 - math.sqrt(9 - 2.5**2), "box_edge_r 3 → 1,34")
    # stadiony i rowki panelu
    add(K, "stadion panelu (60,60): wierzch Z", "trafienie −Z", surf(m, (63, 57, 20), "Z", -1), 4.0, "floor_t+panel_pad_h (sonda 4,24 od osi rowka)")
    add(K, "stadion szerokość prostopadle do przekątnej: lico z zewnątrz (z (66,54,3,5) w −N)", "trafienie −N", first_hit(m, (66, 54, 3.5), -AX["N"]), (6*math.sqrt(2)) - 4.5, "odl. 8,49 od osi − 4,5 = 3,99")
    add(K, "rowek panelu szer. (60,60, Z 1,5) prostopadle do przekątnej", "cięciwa N", chord(m, (60, 60, 1.5), "N"), 3.4, "panel_slot_w")
    add(K, "rowek panelu długość wzdłuż przekątnej (60,60, Z 1,5)", "cięciwa D", chord(m, (60, 60, 1.5), "D"), 10 * math.sqrt(2) + 3.4, "(55→65)·√2 + 3,4 = 17,54")
    add(K, "rowek panelu przelotowy przez dno i stadion: trafienie +Z z (60,60,−5)", "trafienie +Z", surf(m, (60, 60, -5), "Z", +1), None, "brak = przelot (wkręt M3 przechodzi przez dno i stadion do dystansu)")
    add(K, "rowek: półdługość od (60,60,3,5) w +D (koniec rowka R1,7)", "trafienie +D", first_hit(m, (60, 60, 3.5), AX["D"]), 5 * math.sqrt(2) + 1.7, "5·√2 + 1,7 = 8,77")
    add(K, "stadion: koniec od zewnątrz (z (80,80,3,5) w −D)", "trafienie −D", first_hit(m, (80, 80, 3.5), -AX["D"]), (80 - 65) * math.sqrt(2) - 4.5, "koniec stadionu 65 + R4,5 → 16,71")
    # bossy Pi
    add(K, "boss Pi (−46,5,−24,5): wierzch Z", "trafienie −Z", surf(m, (-43.5, -24.5, 20), "Z", -1), 8.0, "floor_t+pi_standoff_h")
    add(K, "boss Pi: otwór ø (Z 7)", "cięciwa X", chord(m, (-46.5, -24.5, 7), "X"), 2.1, "insert_hole_m25")
    add(K, "boss Pi: dno otworu Z", "trafienie −Z", surf(m, (-46.5, -24.5, 7), "Z", -1), 3.0, "8 − insert_depth_m25 5")
    add(K, "boss Pi: lico zewn. x (z (−30,−24,5,6) w −X)", "trafienie −X", surf(m, (-30, -24.5, 6), "X", -1), -42.5, "ø8 → −46,5+4")
    add(K, "boss Pi (11,5, 24,5): wierzch Z", "trafienie −Z", surf(m, (14.5, 24.5, 20), "Z", -1), 8.0, "")
    # wentylacja
    add(K, "wlot w dnie (−8,−10): X", "cięciwa", chord(m, (-8, -10, 1.5), "X"), 30, "floor_vent_l")
    add(K, "wlot w dnie (−8,−10): Y", "cięciwa", chord(m, (-8, -10, 1.5), "Y"), 4, "floor_vent_w")
    add(K, "szczelina tylna (−54, Z 8): X", "cięciwa", chord(m, (-54, 98.75, 8), "X"), 12, "vent_slot_w")
    add(K, "szczelina tylna (−54, Z 8): Z", "cięciwa", chord(m, (-54, 98.75, 8), "Z"), 3, "vent_slot_h")
    add(K, "szczelina boczna prawa (y 36, Z 8): Y", "cięciwa", chord(m, (98.75, 36, 8), "Y"), 12, "")
    add(K, "szczelina boczna lewa (y −36, Z 8): Z", "cięciwa", chord(m, (-98.75, -36, 8), "Z"), 3, "")
    # kieszeń DC
    add(K, "okno DC (−67,5, Z 26): X", "cięciwa", chord(m, (-67.5, 98.75, 26), "X"), 51, "dc_pocket_w")
    add(K, "okno DC: Z", "cięciwa", chord(m, (-67.5, 98.75, 26), "Z"), 24, "dc_pocket_h")
    add(K, "okno DC: dolna krawędź Z", "trafienie −Z", surf(m, (-67.5, 98.75, 26), "Z", -1), 14, "dc_pocket_z0")
    add(K, "skrzynka DC wnętrze X (y 87,75, Z 16)", "cięciwa", chord(m, (-67.5, 87.75, 16), "X"), 53.5, "−95,5…−42")
    add(K, "skrzynka DC: ściana przednia w świetle y", "trafienie −Y z zewnątrz", surf(m, (-67.5, 110, 16), "Y", -1), 80, "100 − dc_pocket_depth 22 + wall 2")
    add(K, "skrzynka DC: sufit Z (z wnętrza)", "trafienie +Z", surf(m, (-67.5, 88, 26), "Z", +1), 38, "40 − 2")
    add(K, "skrzynka DC: dno Z (z wnętrza)", "trafienie −Z", surf(m, (-67.5, 88, 26), "Z", -1), 14, "12 + 2")
    add(K, "otwór DC ø (Y) w prawej ścianie skrzynki (x −41)", "cięciwa", chord(m, (-41, 89, 30), "Y"), 12, "dc_hole_d")
    add(K, "otwór DC ø (Z)", "cięciwa", chord(m, (-41, 89, 30), "Z"), 12, "dc_hole_d")
    add(K, "prawa ściana skrzynki grubość (−41, 81, 30)", "cięciwa w materiale X", chord(m, (-41, 81, 30), "X"), 2.0, "dc_pocket_wall")
    add(K, "ścianka otwór DC – wierzch prawej ściany skrzynki (−41, 89, 37)", "cięciwa w materiale Z", chord(m, (-41, 89, 37), "Z"), 4.0, "otwór do Z 36, wierzch skrzynki Z 40 → 4,0")
    add(K, "skrzynka: lewa ściana (= ściana korpusu) grubość (−96,5, 88, 26)", "cięciwa w materiale X", chord(m, (-96.5, 88, 26), "X"), 4.5, "2,5 + 2")
    # USB
    add(K, "okno USB (60, Z 24): X", "cięciwa", chord(m, (60, 98.75, 24), "X"), 16, "usb_cut_w")
    add(K, "okno USB: Z", "cięciwa", chord(m, (60, 98.75, 24), "Z"), 9, "usb_cut_h")
    add(K, "rowek flanszy USB prawy (72,75): X", "cięciwa", chord(m, (72.75, 98.75, 24), "X"), 5.7, "(14−11,5)+3,2")
    add(K, "rowek flanszy USB prawy: Z", "cięciwa", chord(m, (72.75, 98.75, 24), "Z"), 3.2, "usb_slot_w")
    add(K, "ścianka okno USB – rowek (68,95)", "cięciwa w materiale X", chord(m, (68.95, 98.75, 24), "X"), 1.9, "52−50,1")
    # kieszenie zatrzasków (4)
    for nm, p, axc in (("prawa (98, 0)", (98, 0, 53.8), "Y"), ("lewa (−98, 0)", (-98, 0, 53.8), "Y"),
                       ("przednia (50, −98)", (50, -98, 53.8), "X"), ("tylna (−50, 98)", (-50, 98, 53.8), "X")):
        add(K, f"kieszeń zatrzasku {nm}: szerokość", "cięciwa", chord(m, p, axc), 10, "snap_pocket_w")
        add(K, f"kieszeń zatrzasku {nm}: wysokość Z", "cięciwa", chord(m, p, "Z"), 2.5, "snap_pocket_h")
        add(K, f"kieszeń zatrzasku {nm}: dolna krawędź Z", "trafienie −Z", surf(m, p, "Z", -1), 52.6, "snap_pocket_z")
        add(K, f"kieszeń zatrzasku {nm}: górna krawędź Z", "trafienie +Z", surf(m, p, "Z", +1), 55.1, "52,6+2,5")
    add(K, "kieszeń prawa: dno x (z (80,0,53,8) +X)", "trafienie +X", surf(m, (80, 0, 53.8), "X", +1), 98.5, "97,5 + snap_pocket_depth 1,0")
    add(K, "kieszeń przednia: dno y", "trafienie −Y", surf(m, (50, -80, 53.8), "Y", -1), -98.5, "")
    add(K, "ściana za kieszenią prawą (99,25, 0, 53,85)", "cięciwa w materiale X", chord(m, (99.25, 0, 53.85), "X"), 1.5, "2,5 − 1,0")
    # wkręty blatu
    add(K, "otwór wkrętu blatu (75, Z 55): ø w ścianie (y 98,2)", "cięciwa X", chord(m, (75, 98.2, 55), "X"), 3.2, "blat_screw_hole_d")
    add(K, "otwór wkrętu blatu: ø przy licu zewn. (y 99,9)", "cięciwa X", chord(m, (75, 99.9, 55), "X"), 6.3 - 2 * 0.1, "pogłębienie ø6,3/90° → 6,1 na y 99,9")
    add(K, "otwór wkrętu blatu (−75, Z 55): ø w ścianie", "cięciwa X", chord(m, (-75, 98.2, 55), "X"), 3.2, "")
    add(K, "otwór wkrętu blatu: ø pionowo (Z) przy y 98,2", "cięciwa Z", chord(m, (75, 98.2, 55), "Z"), 3.2, "")
    # napis
    add(K, "napis: lico reliefu min y (bbox)", "bbox", lo[1], -100.6, "label_relief_h 0,6")
    zs = [surf(m, (x, -150, 51), "Y", +1) for x in np.arange(-55, 55.01, 0.5)]
    zs = [z for z in zs if z is not None]
    add(K, "napis: najdalszy punkt reliefu y (skan x −55…55 co 0,5, Z 51)", "trafienie +Y", min(zs) if zs else None, -100.6, "")
    # zasięg napisu w Z
    zz = []
    for z in np.arange(44, 58, 0.25):
        ys = [surf(m, (x, -150, z), "Y", +1) for x in np.arange(-55, 55.01, 1.0)]
        ys = [y for y in ys if y is not None]
        if ys and min(ys) < -100.05:
            zz.append(z)
    add(K, "napis: zakres Z reliefu (skan)", "skan", (max(zz) - min(zz)) if zz else None, 8.0, f"label_text_h 8 (Z {min(zz) if zz else None}…{max(zz) if zz else None})")

# W vs P: identyczność poza przednią ścianą
mw, mp = mesh("ramka_korpus_W_v2"), mesh("ramka_korpus_P_v2")
vw = {tuple(np.round(v, 4)) for v in mw.vertices if v[1] > -99.9}
vp = {tuple(np.round(v, 4)) for v in mp.vertices if v[1] > -99.9}
add("korpus W vs P", "wierzchołki poza przednią ścianą (y > −99,9): różnica zbiorów", "zbiory", float(len(vw ^ vp)), 0, "R33: różnica tylko napisem")

# ---------------------------------------------------------------- BLAT (wierzch na Z 0, kołnierz do Z 14)
B = "ramka_blat_v2"; m = mesh(B); lo, hi, sz, vol, wt = bbox(B)
add(B, "gabaryt X / Y", "bbox", sz[0], 200, "box_outer"); add(B, "gabaryt Z", "bbox", sz[2], 14, "blat_t+blat_skirt_h")
add(B, "objętość [cm³]", "mesh", vol, None, "arkusz 72,57")
add(B, "wierzch blatu: Z lica (99, 0)", "trafienie +Z z −10", surf(m, (97, 0, -10), "Z", +1), 0.0, "STL wierzchem w dół (sonda 3 od krawędzi R1,5)")
add(B, "płyta grubość (99, 0, 2)", "cięciwa w materiale Z", chord(m, (97, 0, 2), "Z"), 4.0, "blat_t")
add(B, "płyta grubość (90, 90, 2) — bez bossa ramy", "cięciwa w materiale Z", chord(m, (90, 90, 2), "Z"), 4.0, "R50‑U1")
add(B, "kieszeń dyfuzora X (y 20, Z 1)", "cięciwa", chord(m, (0, 20, 1), "X"), 162, "diffuser_pocket")
add(B, "kieszeń dyfuzora głębokość: półka Z (z (80, 0, −10) +Z)", "trafienie +Z", surf(m, (80, 0, -10), "Z", +1), 2.0, "diffuser_t")
add(B, "kieszeń dyfuzora: naroże ostre — x lica przy y 80,8", "trafienie +X", surf(m, (0, 80.8, 1), "X", +1), 81.0, "diffuser_pocket_r 0")
add(B, "okno przelotowe X (y 20, Z 3)", "cięciwa", chord(m, (0, 20, 3), "X"), 158, "window_through")
add(B, "kołnierz zewn. x (z (150,20,9) −X)", "trafienie −X", surf(m, (150, 20, 9), "X", -1), 97.0, "194/2")
add(B, "kołnierz zewn. y (z (20,150,9) −Y)", "trafienie −Y", surf(m, (20, 150, 9), "Y", -1), 97.0, "")
add(B, "kołnierz wewn. X (cięciwa 0,20,9)", "cięciwa", chord(m, (0, 20, 9), "X"), 190, "2·95")
add(B, "kołnierz grubość (96, 20, 9)", "cięciwa w materiale X", chord(m, (96, 20, 9), "X"), 2.0, "blat_skirt_t")
add(B, "kołnierz: dolna krawędź Z (96,20)", "trafienie −Z z 30", surf(m, (96, 20, 30), "Z", -1), 14.0, "")
add(B, "kołnierz naroże R4,5: x lica przy y 96", "trafienie −X", surf(m, (150, 96, 9), "X", -1), 92.5 + math.sqrt(4.5**2 - 3.5**2), "→ 95,33")
add(B, "górna krawędź R1,5: z lica przy x 99,5", "trafienie +Z", surf(m, (99.5, 20, -10), "Z", +1), 1.5 - math.sqrt(1.5**2 - 1.0**2), "blat_top_edge_r → 0,38")
for nm, p, ax_in, sgn in (("prawy (y 0)", (110, 0, 9.75), "X", -1), ("lewy", (-110, 0, 9.75), "X", +1),
                          ("przedni (x 50; STL +Y)", (50, 110, 9.75), "Y", -1), ("tylny (x −50; STL −Y)", (-50, -110, 9.75), "Y", +1)):
    v = surf(m, p, ax_in, sgn)
    add(B, f"haczyk {nm}: czubek", f"trafienie {ax_in}", abs(v) if v is not None else None, 98.3, "97,0 + snap_hook_h 1,3")
add(B, "haczyk prawy: szerokość (y) na czubku", "cięciwa w materiale Y (98, 0, 9.75)", chord(m, (98, 0, 9.75), "Y"), 8.0, "snap_hook_w")
add(B, "nacięcie obok haczyka (96, 4,5, 10): szer. Y", "cięciwa", chord(m, (96, 4.5, 10), "Y"), 1.0, "snap_notch_w")
add(B, "nacięcie: górny koniec Z (z (96,4,5,13) −Z... = pierwsze trafienie w górę)", "trafienie −Z (w kierunku wierzchu)", surf(m, (96, 4.5, 13), "Z", -1), 5.0, "snap_hook_arm_l 9 → lokalnie −5")
add(B, "ramię haczyka grubość (96,8, 0, 13)", "cięciwa w materiale X", chord(m, (96.8, 0, 13), "X"), 1.5, "snap_hook_t")
prof = []
for z in np.arange(8.0, 12.01, 0.05):
    x = surf(m, (110, 0, z), "X", -1)
    prof.append((round(float(z), 2), None if x is None else round(x, 3)))
# słupki
add(B, "słupek (75, y 89,2…95,2): otwór ø (Z 8,6)", "cięciwa X (75, 94, 8.6)", chord(m, (75, -94, 8.6), "X"), 2.5, "insert_hole_m3 (STL y −94)")
add(B, "słupek: otwór ø pionowo", "cięciwa Z", chord(m, (75, -94, 8.6), "Z"), 2.5, "")
add(B, "słupek: dno otworu y", "trafienie −Y", surf(m, (75, -94, 8.6), "Y", +1), -91.0, "97 − blat_post_hole_depth 6 (STL −91)")
add(B, "słupek: wylot otworu y (+Y)", "trafienie +Y", surf(m, (75, -94, 8.6), "Y", -1), None, "otwarty na zewnątrz (brak trafienia = przelot)")
add(B, "słupek: szerokość X (y 92, Z 10)", "cięciwa w materiale X", chord(m, (75, -92, 10), "X"), 8.0, "blat_post_w")
add(B, "słupek: przednie lico y (z (75,80,10) +Y)", "trafienie +Y", surf(m, (75, -80, 10), "Y", -1), -89.2, "blat_post_y0 (STL −89,2)")
add(B, "słupek: dno pod otworem (75, 90,1, 8,6)", "cięciwa w materiale Y", chord(m, (75, -90.1, 8.6), "Y"), 1.8, "91,0 − 89,2")
add(B, "słupek −75: otwór ø", "cięciwa X", chord(m, (-75, -94, 8.6), "X"), 2.5, "")
# wkładka ↔ blat
add(B, "otwór kołka (58, 93,5): ø", "cięciwa X (Z 2)", chord(m, (58, -93.5, 2), "X"), 3.3, "blat_pin_hole_d (STL y −93,5)")
add(B, "otwór kołka: dno Z", "trafienie +Z z (58,93,5,1)", surf(m, (58, -93.5, 1), "Z", +1), 3.8, "blat_pin_hole_depth")
add(B, "otwór kołka −58: ø", "cięciwa X", chord(m, (-58, -93.5, 2), "X"), 3.3, "")
add(B, "kieszeń magnesu (58, 86): ø", "cięciwa X (Z 1)", chord(m, (58, -86, 1), "X"), 5.4, "blat_magnet_pocket_d")
add(B, "kieszeń magnesu: dno Z", "trafienie +Z", surf(m, (58, -86, 1), "Z", +1), 2.3, "blat_magnet_pocket_depth")
add(B, "szczelina kabla (66, 90): X", "cięciwa", chord(m, (66, -90, 2), "X"), 4, "wire_slot_w")
add(B, "szczelina kabla: Y", "cięciwa", chord(m, (66, -90, 2), "Y"), 8, "wire_slot_l")
add(B, "szczelina kabla: przelot (trafienie z (66,90,−5) +Z)", "trafienie +Z", surf(m, (66, -90, -5), "Z", +1), None, "brak trafienia = przelot przez płytę")

# ---------------------------------------------------------------- WKŁADKA (końce kołków Z 0, spód ramy Z 3,5)
Wk = "ramka_wkladka_v2"; m = mesh(Wk); lo, hi, sz, vol, wt = bbox(Wk)
add(Wk, "gabaryt X / Y / Z", "bbox", sz[0], 130, "2·65"); add(Wk, "gabaryt Y", "bbox", sz[1], 148.3, "−52,3…96"); add(Wk, "gabaryt Z", "bbox", sz[2], 11.0, "3,5 + 6 + 1,5 kołek")
add(Wk, "objętość [cm³]", "mesh", vol, None, "arkusz 12,41")
add(Wk, "rama zewn. X (y 0, Z 6,5)", "zewn. (trafienia z ±150)", (surf(m, (150, 0, 6.5), "X", -1) or 0) - (surf(m, (-150, 0, 6.5), "X", +1) or 0), 104.6, "96,6 + 2·4")
add(Wk, "otwór X (0,0,6,5)", "cięciwa", chord(m, (0, 0, 6.5), "X"), 96.6, "insert_opening")
add(Wk, "otwór Y (20,0,6,5)", "cięciwa", chord(m, (20, 0, 6.5), "Y"), 96.6, "")
add(Wk, "otwór: naroże ostre, x lica przy y 48,1", "trafienie +X", surf(m, (0, 48.1, 6.5), "X", +1), 48.3, "insert_opening_r 0")
add(Wk, "spód ramy Z (−40, −50,3)", "trafienie +Z z −10", surf(m, (-40, -50.3, -10), "Z", +1), 3.5, "kołki 3,5 w dół")
add(Wk, "wierzch ramy Z", "trafienie −Z z 20", surf(m, (-40, -50.3, 20), "Z", -1), 9.5, "3,5 + insert_h 6")
add(Wk, "rama szerokość (y −50,3): Y", "cięciwa w materiale", chord(m, (-40, -50.3, 6.5), "Y"), 4.0, "insert_wall_w")
add(Wk, "faza otworu 1×45°: z lica przy x 48,8", "trafienie −Z z 20", surf(m, (48.8, 0, 20), "Z", -1), 9.0, "insert_chamfer 1 → 9,5 − 0,5")
add(Wk, "półka A (−38,−38): wierzch Z", "trafienie −Z", surf(m, (-38, -38, 20), "Z", -1), 6.0, "3,5 + insert_shelf_h 2,5")
add(Wk, "półka A grubość", "cięciwa w materiale Z (−38,−38,4,5)", chord(m, (-38, -38, 4.5), "Z"), 2.5, "insert_shelf_h")
add(Wk, "półka A: bok (x lica od środka)", "trafienie −X z (0,−38,5)", surf(m, (0, -38, 5), "X", -1), -36.3, "48,3 − 12")
add(Wk, "kieszeń Halla A (−42,−42): X", "cięciwa", chord(m, (-42, -42, 4.5), "X"), 5.0, "hall_pocket_w")
add(Wk, "kieszeń Halla A: Y", "cięciwa", chord(m, (-42, -42, 4.5), "Y"), 5.5, "hall_pocket_l")
add(Wk, "kieszeń Halla A: przelot (z (−42,−42,−5) +Z)", "trafienie +Z", surf(m, (-42, -42, -5), "Z", +1), None, "brak = przelot")
add(Wk, "kanał pod półką A (−45,−45, Z 3,5…4,5)? szer. prostopadle do przekątnej", "cięciwa N (−45,−45,4)", chord(m, (-45, -45, 4), "N"), 2.5, "hall_lead_channel_w")
add(Wk, "kanał pod półką A: sufit Z (z (−45,−45,0) +Z)", "trafienie +Z", surf(m, (-45, -45, 0), "Z", +1), 4.5, "3,5 + 1,0")
add(Wk, "przelot w ściance A (−50,−50): sufit Z", "trafienie +Z", surf(m, (-50, -50, 0), "Z", +1), 5.0, "3,5 + hall_wall_pass_h 1,5")
add(Wk, "półka nad kanałem A (−45,−45, Z 5,25)", "cięciwa w materiale Z", chord(m, (-45, -45, 5.25), "Z"), 1.5, "2,5 − 1,0")
add(Wk, "kołek orientacyjny (45,6,−45,6): X", "cięciwa w materiale X (Z 8)", chord(m, (45.6, -45.6, 8), "X"), 4.4, "orient_post")
add(Wk, "kołek orientacyjny: Y", "cięciwa w materiale Y", chord(m, (45.6, -45.6, 8), "Y"), 4.4, "")
add(Wk, "kołek orientacyjny: szczyt Z", "trafienie −Z z 20", surf(m, (45.6, -45.6, 20), "Z", -1), 11.0, "6 + orient_post_h 5")
add(Wk, "kołek orientacyjny: lico zewn. x (z (0,−45,6,8) +X)", "trafienie +X", surf(m, (0, -45.6, 8), "X", +1), 48.3 - 0.5 - 4.4, "ściana 48,3 − gap 0,5 − 4,4 = 43,4")
add(Wk, "kołek orientacyjny: faza — szczyt przy x 43,6", "trafienie −Z", surf(m, (43.6, -45.6, 20), "Z", -1), 11.0 - (1 - 0.2), "orient_post_chamfer 1 → 10,2")
add(Wk, "wycięcie palcowe (0,−50,3, 6,5): X", "cięciwa", chord(m, (0, -50.3, 6.5), "X"), 30, "finger_cut_w")
add(Wk, "rowek kablowy prawy: dno x (z (57,3,0,4,25) −X)", "trafienie −X", surf(m, (57.3, 0, 4.25), "X", -1), 49.8, "52,3 − wire_rabbet_w 2,5")
add(Wk, "rowek kablowy prawy: sufit Z (z (51,05,0,0) +Z)", "trafienie +Z", surf(m, (51.05, 0, 0), "Z", +1), 5.0, "3,5 + wire_rabbet 1,5")
add(Wk, "rowek kablowy tylny: dno y (z (0,57,3,4,25) −Y)", "trafienie −Y", surf(m, (0, 57.3, 4.25), "Y", -1), 49.8, "")
add(Wk, "rowek kablowy lewy: dno x", "trafienie +X z (−57,3,0,4,25)", surf(m, (-57.3, 0, 4.25), "X", +1), -49.8, "")
add(Wk, "rowek kablowy przedni (nie ma): sufit Z (0? z (−30,−51,05,0) +Z)", "trafienie +Z", surf(m, (-30, -51.05, 0), "Z", +1), 3.5, "przód bez rowka → spód ramy 3,5")
add(Wk, "ścianka rowek–otwór (49,05, 0, 4,25)", "cięciwa w materiale X", chord(m, (49.05, 0, 4.25), "X"), 1.5, "49,8 − 48,3")
add(Wk, "ucho prawe (58, 80): wierzch Z", "trafienie −Z z 20", surf(m, (58, 80, 20), "Z", -1), 6.5, "3,5 + tab_t 3")
add(Wk, "ucho prawe: szerokość X (y 80, Z 5)", "cięciwa w materiale X", chord(m, (58, 80, 5), "X"), 14, "tab_w")
add(Wk, "ucho prawe: koniec y (z (58,150,5) −Y)", "trafienie −Y", surf(m, (58, 150, 5), "Y", -1), 96, "tab_end_y")
add(Wk, "kołek ustalający (58, 93,5): ø (Z 1,5)", "cięciwa X", chord(m, (58, 93.5, 1.5), "X"), 3.0, "tab_pin_d")
add(Wk, "kołek ustalający: ø przy końcu (Z 0,25)", "cięciwa X", chord(m, (58, 93.5, 0.25), "X"), 2.0 + 0.5, "stożek ø3→ø2 na 0,5: na Z 0,25 ≈ 2,5")
add(Wk, "kołek ustalający: koniec Z", "trafienie +Z z −5", surf(m, (58, 93.5, -5), "Z", +1), 0.0, "tab_pin_h 3,5 pod spodem")
add(Wk, "kołek ustalający −58: ø", "cięciwa X", chord(m, (-58, 93.5, 1.5), "X"), 3.0, "")
add(Wk, "otwór magnesu ucha (58, 86): ø", "cięciwa X (Z 5)", chord(m, (58, 86, 5), "X"), 5.4, "tab_magnet_hole_d")
add(Wk, "otwór magnesu: przelot", "trafienie +Z z (58,86,−5)", surf(m, (58, 86, -5), "Z", +1), None, "brak = przelot")
add(Wk, "kanał pod uchem (64, 70): ścianka wewn. x (z (64,70,4) −X)", "trafienie −X", surf(m, (64, 70, 4), "X", -1), 63.0, "kanał 63…65 = otwarty na zewnętrznej krawędzi ucha")
add(Wk, "kanał pod uchem: otwarty w +X (z (64,70,4) +X)", "trafienie +X", surf(m, (64, 70, 4), "X", +1), None, "brak = kanał otwarty bokiem (rabbet)")
add(Wk, "kanał pod uchem: sufit Z (z (64,70,0) +Z)", "trafienie +Z", surf(m, (64, 70, 0), "Z", +1), 3.5 + 1.2, "tab_cable_channel_h 1,2 → 4,7")
add(Wk, "nasada L: koniec y części wewn. (x 48, z (48,70,5) −Y)", "trafienie −Y", surf(m, (48, 70, 5), "Y", -1), 58.0, "tab_root_y1")
add(Wk, "nasada L: brak materiału poza ramą dla x 60, y 50 (z (60,50,5) +Z)", "trafienie +Z z (60,50,−5)", surf(m, (60, 50, -5), "Z", +1), None, "brak = prawy pas odsłonięty (K‑56)")
add(Wk, "nasada L: lico y części zewn. (x 60, z (60,0,5) +Y)", "trafienie +Y", surf(m, (60, 0, 5), "Y", +1), 52.3, "x 52,3…65 od y 52,3")
add(Wk, "strzałka ▼ (32, −51,15): szczyt Z", "trafienie −Z z 20", surf(m, (32, -51.15, 20), "Z", -1), 9.5 + 0.6, "relief 0,6 na wierzchu ramy → 10,1")
add(Wk, "strzałka ▼ (−32, −51,15): szczyt Z", "trafienie −Z z 20", surf(m, (-32, -51.15, 20), "Z", -1), 10.1, "")

# ---------------------------------------------------------------- POKRYWKA (wierzch na Z 0, kołnierz do Z 20)
P = "ramka_pokrywka_v2"; m = mesh(P); lo, hi, sz, vol, wt = bbox(P)
add(P, "gabaryt X", "bbox", sz[0], 99.6, "96,6 + 2·1,5"); add(P, "gabaryt Z", "bbox", sz[2], 20.0, "14 + 2 + 4"); add(P, "objętość [cm³]", "mesh", vol, None, "arkusz 30,06")
add(P, "wierzch: Z lica z zewnątrz (15,0)", "trafienie +Z z −10", surf(m, (15, 0, -10), "Z", +1), 0.0, "wierzchem w dół")
add(P, "wierzch grubość (15,0,1)", "cięciwa w materiale Z", chord(m, (15, 0, 1), "Z"), 2.0, "cover_top_t")
add(P, "wnęka X (0,20,10)", "cięciwa", chord(m, (0, 20, 10), "X"), 96.6, "plate_size + 2·cover_clearance")
add(P, "wnęka Y (20,0,10)", "cięciwa", chord(m, (20, 0, 10), "Y"), 96.6, "")
add(P, "wnęka: naroże — x lica przy y 48,1", "trafienie +X", surf(m, (0, 48.1, 10), "X", +1), 46.8 + math.sqrt(1.5**2 - 1.3**2), "naroże wnęki R1,5 (= R3 − 1,5) → 47,55")
add(P, "kołnierz grubość (49,05, 20, 10)", "cięciwa w materiale X", chord(m, (49.05, 20, 10), "X"), 1.5, "cover_skirt_t")
add(P, "kołnierz grubość za garbem (49,05, 0, 18)", "cięciwa w materiale X", chord(m, (49.05, 0, 18), "X"), 2.2, "1,5 + garb 0,7")
add(P, "garb prawy (y 0): czubek x (z (0,0,18) +X)", "trafienie +X", surf(m, (0, 0, 18), "X", +1), 47.6, "48,3 − cover_snap_bump 0,7")
add(P, "garb przedni (x 25): czubek y", "trafienie −Y z (25,0,18)", surf(m, (25, 0, 18), "Y", +1), 47.6, "cover_snap_front_x 25 (przód = STL +Y po obrocie)")
add(P, "garb tylny (x −25): czubek y", "trafienie +Y z (−25,0,18)", surf(m, (-25, 0, 18), "Y", -1), -47.6, "")
add(P, "garb lewy (y 0): czubek x", "trafienie −X z (0,0,18)", surf(m, (0, 0, 18), "X", -1), -47.6, "")
add(P, "garb prawy: szerokość Y (cięciwa w materiale przy x 47,8, Z 18)", "cięciwa w materiale Y", chord(m, (47.8, 0, 18), "Y"), 10.0, "cover_snap_w")
bump = []
for z in np.arange(16.5, 19.51, 0.05):
    x = surf(m, (0, 0, z), "X", +1)
    bump.append((round(float(z), 2), None if x is None else round(x, 3)))
add(P, "wycięcie palcowe przód (y −49,05, Z 19): X", "cięciwa", chord(m, (0, -49.05, 19), "X"), 30, "cover_finger_w")
add(P, "wycięcie palcowe przód: górna krawędź Z (z (0,−49,05,10) +Z)", "trafienie +Z", surf(m, (0, -49.05, 10), "Z", +1), 17.0, "20 − cover_finger_h 3")
add(P, "wycięcie palcowe tył (y 49,05, Z 19): X", "cięciwa", chord(m, (0, 49.05, 19), "X"), 30, "")
add(P, "naroże R3: x lica przy y −49,0", "trafienie −X z (150,−49,10)", surf(m, (150, -49, 10), "X", -1), 46.8 + math.sqrt(9 - 2.2**2), "cover_corner_r 3 → 48,84")
add(P, "dolna krawędź kołnierza Z (49,05, 20)", "trafienie −Z z 30", surf(m, (49.05, 20, 30), "Z", -1), 20.0, "")

# ---------------------------------------------------------------- TULEJKA, PODKŁADKI
T = "ramka_tulejka_dc_v2"; m = mesh(T); lo, hi, sz, vol, wt = bbox(T)
add(T, "kołnierz ø (bbox X)", "bbox", sz[0], 15, "dc_bush_flange_d (tesselacja)")
add(T, "walec: promień zewn. (z (10,0,2) −X)", "trafienie −X", surf(m, (10, 0, 2), "X", -1), 5.925, "dc_bush_outer_d 11,85 / 2")
add(T, "walec: promień zewn. w −X", "trafienie +X z (−10,0,2)", surf(m, (-10, 0, 2), "X", +1), -5.925, "")
add(T, "walec: promień zewn. (Y)", "trafienie −Y z (0,10,2)", surf(m, (0, 10, 2), "Y", -1), 5.925, "")
add(T, "otwór ø (0,0,1)", "cięciwa X", chord(m, (0, 0, 1), "X"), 8.2, "dc_bush_inner_d")
add(T, "otwór ø (0,0,2,5)", "cięciwa Y", chord(m, (0, 0, 2.5), "Y"), 8.2, "")
add(T, "wysokość całkowita", "bbox Z", sz[2], 3.0, "dc_bush_t 2 + flange_t 1")
add(T, "kołnierz grubość (6,7, 0, 0,5)", "cięciwa w materiale Z", chord(m, (6.7, 0, 0.5), "Z"), 1.0, "dc_bush_flange_t")
add(T, "ścianka walca (5, 0, 2)", "cięciwa w materiale X", chord(m, (5, 0, 2), "X"), (11.85 - 8.2) / 2, "1,825")
for S, t in (("ramka_podkladka_panelu_05_v2", 0.5), ("ramka_podkladka_panelu_1_v2", 1.0), ("ramka_podkladka_panelu_2_v2", 2.0)):
    m = mesh(S); lo, hi, sz, vol, wt = bbox(S)
    add(S, "ø zewn. (bbox X)", "bbox", sz[0], 9, "panel_shim_d"); add(S, "otwór ø", "cięciwa X (0,0,t/2)", chord(m, (0, 0, t / 2), "X"), 3.4, "panel_shim_hole_d")
    add(S, "grubość", "bbox Z", sz[2], t, "panel_shim_t")

# ---------------------------------------------------------------- PŁYTKA n1 (tylko interfejs; spód Z 0, wierzch Z 8)
Pl = "ramka_plytka_wieczorna_n1_v2"; m = mesh(Pl); lo, hi, sz, vol, wt = bbox(Pl)
add(Pl, "bok X / Y", "bbox", sz[0], 96, "plate_size"); add(Pl, "grubość z reliefem cyfry", "bbox Z", sz[2], 8.6, "8 + number_relief_h 0,6")
add(Pl, "grubość płytki (0, −46,5, 4)", "cięciwa w materiale Z", chord(m, (0, -46.5, 4), "Z"), 8.0, "plate_thickness")
add(Pl, "wycięcie D: otwarte na zewnątrz (z (45,5,−45,5,4) +X)", "trafienie +X", surf(m, (45.5, -45.5, 4), "X", +1), None, "brak = wycięcie narożne otwarte")
add(Pl, "wycięcie D: lico y od środka (z (45,5,0,4) −Y)", "trafienie −Y", surf(m, (45.5, 0, 4), "Y", -1), -43.0, "notch y −48…−43")
add(Pl, "wycięcie D: lico x od środka (z (0,−45,5,4) +X)", "trafienie +X", surf(m, (0, -45.5, 4), "X", +1), 43.0, "")
add(Pl, "rowek pokrywki: dno x (z (60,20,6) −X)", "trafienie −X", surf(m, (60, 20, 6), "X", -1), 47.2, "48 − cover_groove_depth 0,8")
grv = []
for z in np.arange(5.0, 7.01, 0.05):
    x = surf(m, (60, 20, z), "X", -1); grv.append((round(float(z), 2), None if x is None else round(x, 3)))
add(Pl, "kieszeń magnesu A (−42,−42): ø", "cięciwa X (Z 1)", chord(m, (-42, -42, 1), "X"), 5.2, "magnet_pocket_d")
add(Pl, "kieszeń magnesu A: sufit Z", "trafienie +Z z (−42,−42,−5)", surf(m, (-42, -42, -5), "Z", +1), 2.2, "magnet_pocket_depth")
add(Pl, "faza górna 0,5: z lica przy x 47,8", "trafienie −Z z 20", surf(m, (47.8, 20, 20), "Z", -1), 8 - 0.3, "plate_top_chamfer → 7,7")
add(Pl, "krawędź pionowa R1: x lica przy y −47,5", "trafienie −X z (150,−47,5,4)", surf(m, (150, 47.5, 4), "X", -1), 47 + math.sqrt(1 - 0.25), "plate_edge_r → 47,87 (róg C, bez wycięcia)")
add(Pl, "stożek znacznika A: dno Z", "trafienie −Z z (−42,−42,20)", surf(m, (-42, -42, 20), "Z", -1), 5.0, "8 − marker_cone_depth 3")

# ---------------------------------------------------------------- PASOWANIA (z wartości zmierzonych)
def g(plik, frag):
    for r in rows:
        if r["plik"] == plik and frag in r["cecha"] and r["zmierzone"] is not None:
            return r["zmierzone"]
    return None
KW, BL, WK, PK, PL, TU = "ramka_korpus_W_v2", "ramka_blat_v2", "ramka_wkladka_v2", "ramka_pokrywka_v2", "ramka_plytka_wieczorna_n1_v2", "ramka_tulejka_dc_v2"
fits = []
def fit(para, rach, val, nom, regula):
    fits.append({"para": para, "rachunek": rach, "zmierzone": None if val is None else round(val, 3), "nominal": nom, "regula": regula})
hz = [(z, x) for z, x in prof if x is not None and x > 97.05]
hv = [(z, x) for z, x in prof if x is not None and x > 98.25]
hook_lo, hook_hi = (63.6 - max(z for z, _ in hz), 63.6 - min(z for z, _ in hz)) if hz else (None, None)
fit("blat kołnierz ↔ korpus wnętrze (na stronę)", "(195 − 2·97,0)/2", (g(KW, "wnętrze X") - 2 * g(BL, "kołnierz zewn. x")) / 2, 0.5, "R48: 0,3 + SLS ±0,3/200 → 0,5")
fit("haczyk blatu: zahaczenie w kieszeni", "czubek 98,3 − ściana wewn. 97,5", g(BL, "haczyk prawy (y 0): czubek") - g(KW, "wnętrze X") / 2, 0.8, "zatrzask (R48)")
fit("haczyk blatu: luz do dna kieszeni", "dno 98,5 − czubek 98,3", g(KW, "kieszeń prawa: dno x") - g(BL, "haczyk prawy (y 0): czubek"), 0.2, "zatrzask")
fit("haczyk blatu: dół rampy występu Z globalnie (profil, x > 97,05)", "63,6 − Z_STL", hook_lo, 52.85, f"snap_hook_z; góra występu {hook_hi}; lico pionowe (x > 98,25) Z {63.6 - max(z for z, _ in hv):.2f}…{63.6 - min(z for z, _ in hv):.2f} = zahaczenie pionowe 1,0 + rampa 1,0 (U6 trzeciego oka)")
fit("haczyk blatu: luz pod występem", "52,85 − kieszeń dolna 52,6", (hook_lo - g(KW, "kieszeń zatrzasku prawa (98, 0): dolna krawędź Z")) if hook_lo else None, 0.25, "R47")
fit("haczyk blatu: luz nad występem", "kieszeń górna 55,1 − 54,85", (g(KW, "kieszeń zatrzasku prawa (98, 0): górna krawędź Z") - hook_hi) if hook_hi else None, 0.25, "R47")
fit("haczyk 8 w kieszeni 10 (na stronę)", "(10 − 8)/2", (g(KW, "kieszeń zatrzasku prawa (98, 0): szerokość") - g(BL, "haczyk prawy: szerokość")) / 2, 1.0, "ruchome")
fit("kołek wkładki ø3 w otworze blatu ø3,3 (na stronę)", "(3,3 − 3,0)/2", (g(BL, "otwór kołka (58, 93,5): ø") - g(WK, "kołek ustalający (58, 93,5): ø")) / 2, 0.15, "wciskane 0,1–0,15 (4.8)")
fit("kołek wkładki: luz osiowy", "głębokość 3,8 − długość 3,5", g(BL, "otwór kołka: dno Z") - (g(WK, "spód ramy Z") - g(WK, "kołek ustalający: koniec Z")), 0.3, "R8")
fit("magnes ø5 w kieszeni blatu ø5,4 (na stronę)", "(5,4 − 5)/2", (g(BL, "kieszeń magnesu (58, 86): ø") - 5) / 2, 0.2, "magnesy 0,1–0,2 (klejone)")
fit("magnes ø5 w otworze ucha ø5,4 (na stronę)", "(5,4 − 5)/2", (g(WK, "otwór magnesu ucha (58, 86): ø") - 5) / 2, 0.2, "")
fit("magnes ø5 × 2 w kieszeni płytki ø5,2 × 2,2", "(5,2 − 5)/2; cofnięcie 2,2 − 2", (g(PL, "kieszeń magnesu A (−42,−42): ø") - 5) / 2, 0.1, f"cofnięcie {round(g(PL, 'kieszeń magnesu A: sufit Z') - 2, 2)}")
fit("płytka 96 w otworze wkładki 96,6 (na stronę)", "(96,6 − 96)/2", (g(WK, "otwór X (0,0,6,5)") - g(PL, "bok X / Y")) / 2, 0.3, "ruchome 0,2–0,3")
fit("płytka 96 we wnęce pokrywki 96,6 (na stronę)", "(96,6 − 96)/2", (g(PK, "wnęka X (0,20,10)") - g(PL, "bok X / Y")) / 2, 0.3, "ruchome 0,2–0,3")
fit("kołek orientacyjny 4,4 w wycięciu 5 (luz po stronie otwartej, płytka wycentrowana)", "lico kołka 43,4 − lico wycięcia 43,0", g(WK, "kołek orientacyjny: lico zewn. x") - g(PL, "wycięcie D: lico x od środka"), 0.4, "4.11/R52 U2: 0,4")
fit("garb pokrywki: zahaczenie w rowku płytki", "bok płytki 48,0 − czubek 47,6", g(PL, "bok X / Y") / 2 - g(PK, "garb prawy (y 0): czubek x"), 0.4, "zatrzask")
fit("garb pokrywki: luz do dna rowka", "czubek 47,6 − dno 47,2", g(PK, "garb prawy (y 0): czubek x") - g(PL, "rowek pokrywki: dno x"), 0.4, "zatrzask")
gz = [z for z, x in bump if x is not None and x < 48.25]
rz = [z for z, x in grv if x is not None and x < 47.95]
fit("garb pokrywki: wysokość Z (profil, x < 48,25)", "zakres Z STL", (max(gz) - min(gz) + 0.05) if gz else None, 0.8, f"cover_snap_hgt; Z {min(gz) if gz else None}…{max(gz) if gz else None}")
fit("rowek płytki: wysokość Z (profil, x < 47,95)", "zakres Z STL", (max(rz) - min(rz) + 0.05) if rz else None, 1.0, f"cover_groove_w; Z {min(rz) if rz else None}…{max(rz) if rz else None} (wierzch 8 → 2 pod wierzchem = 6,0)")
fit("tulejka ø11,85 w otworze korpusu ø12 (na stronę)", "(12 − 2·5,925)/2", (g(KW, "otwór DC ø (Y)") - 2 * g(TU, "walec: promień zewn. (z (10,0,2) −X)")) / 2, 0.075, "wciskane 0,1–0,15 (R52: 0,075 w żywicy bez skurczu)")
fit("gwint gniazda ø8 w tulejce ø8,2 (na stronę)", "(8,2 − 8)/2", (g(TU, "otwór ø (0,0,1)") - 8) / 2, 0.1, "R50‑3")
fit("tulejka: długość walca 2 vs ściana skrzynki 2", "3 − 1 vs 2,0", (g(TU, "wysokość całkowita") - g(TU, "kołnierz grubość")) - g(KW, "prawa ściana skrzynki grubość"), 0.0, "walec kończy się w licu ściany (nakrętka dociska ścianę)")
fit("podkładka: otwór 3,4 vs M3 (na stronę)", "(3,4 − 3)/2", (g("ramka_podkladka_panelu_1_v2", "otwór ø") - 3) / 2, 0.2, "ø zewn. 9 = stadion 9")
fit("dyfuzor 160 × 2 w kieszeni 162 × 2 (na stronę)", "(162 − 160)/2", (g(BL, "kieszeń dyfuzora X") - 160) / 2, 1.0, f"licowanie: głębokość {g(BL, 'kieszeń dyfuzora głębokość')} − 2 = {round(g(BL, 'kieszeń dyfuzora głębokość') - 2, 2)}")
fit("czujnik Halla TO‑92 (4 × 5 × 1,5 proxy) w kieszeni 5,0 × 5,5: luz łączny X", "5,0 − 4", g(WK, "kieszeń Halla A (−42,−42): X") - 4.0, 1.0, "Y: " + str(round(g(WK, "kieszeń Halla A: Y") - 5.0, 2)))
kh = g(KW, "wysokość korpusu"); bt = g(BL, "płyta grubość (99"); sh = g(WK, "półka A (−38,−38): wierzch Z") - g(WK, "spód ramy Z"); ih = g(WK, "wierzch ramy Z") - g(WK, "spód ramy Z"); pt = g(PL, "grubość płytki")
fit("łańcuch: wierzch blatu = korpus_h + blat_t", "59,6 + 4", kh + bt, 63.6, "blat_top_z")
fit("łańcuch: półki wkładki", "63,6 + 2,5", kh + bt + sh, 66.1, "D4")
fit("łańcuch: wierzch ramy wkładki", "63,6 + 6", kh + bt + ih, 69.6, "D4")
fit("łańcuch: wierzch płytki", "66,1 + 8", kh + bt + sh + pt, 74.1, "D4")
cov_bot = kh + bt + sh + pt - (g(PK, "gabaryt Z") - g(PK, "wierzch grubość") - 14)
fit("pokrywka: dół kołnierza nad ramą wkładki", "74,1 − (20 − 2 − 14) = 70,1 vs rama 69,6", cov_bot - (kh + bt + ih), 0.5, "4.11 bez styku")
fit("pokrywka: prześwit nad płytką", "wnęka 18 − kołnierz pod wierzch 4", (g(PK, "gabaryt Z") - g(PK, "wierzch grubość")) - 4, 14.0, "cover_inner_h")
fit("panel: stadion 4,0 + dystans 50 = spód PCB", "4 + 50", g(KW, "stadion panelu (60,60): wierzch Z") + 50, 54.0, "panel_pcb_z")
fit("Pi: boss 8 + stos 26 = szczyt stosu", "8 + 26", g(KW, "boss Pi (−46,5,−24,5): wierzch Z") + 26, 34.0, "zapas do strefy złączy 42 − 34 = 8")
fit("wkręt blatu M3×8: zapas do dna otworu słupka", "koniec wkrętu 100 − 8 = 92; dno 91", (100 - 8) - 91.0, 1.0, "gwint w PA12 97 → 92 = 5,0")
fit("wkręt Pi M2,5×6: zapas do dna otworu bossa", "otwór 5 − (6 − 1,6)", (g(KW, "boss Pi (−46,5,−24,5): wierzch Z") - g(KW, "boss Pi: dno otworu Z")) - 4.4, 0.6, "")

# ---------------------------------------------------------------- ZAPIS
md = ["# Pomiary STL — DESIGN A (31.10.2026)", "",
      "Skrypt: `pomiar_stl.py` (trimesh 5.2, promienie na siatkach; cięciwa = suma odległości do pierwszych trafień w obie strony; trafienie = współrzędna pierwszej powierzchni). Tolerancja porównania 0,05 mm. Niezależnie od generatora i trzeciego oka (inne punkty sond).", "",
      "## 1. Gabaryty, objętości, szczelność", "", "| Plik | min | max | rozmiar | objętość [cm³] | szczelna |", "|---|---|---|---|---|---|"]
names = ["ramka_korpus_W_v2", "ramka_korpus_P_v2", "ramka_blat_v2", "ramka_wkladka_v2", "ramka_pokrywka_v2", "ramka_tulejka_dc_v2",
         "ramka_podkladka_panelu_05_v2", "ramka_podkladka_panelu_1_v2", "ramka_podkladka_panelu_2_v2", "ramka_plytka_wieczorna_n1_v2", "ramka_plytka_poranna_n4_v2"]
for n in names:
    lo, hi, sz, vol, wt = bbox(n)
    md.append(f"| `{n}` | {np.round(lo,2).tolist()} | {np.round(hi,2).tolist()} | {np.round(sz,2).tolist()} | {vol:.2f} | {wt} |")
md += ["", "## 2. Wymiary (zmierzone vs nominał z `parametry.json` / planu)", "", "| Plik | Cecha | Metoda | Zmierzone | Nominał | Δ | OK | Źródło nominału |", "|---|---|---|---|---|---|---|---|"]
nbad = 0
for r in rows:
    z, n = r["zmierzone"], r["nominal"]
    if n is None or z is None:
        d, ok = "", "—" if n is None else ("brak trafienia" if z is None else "")
        if n is None and z is None: ok = "— (przelot ✓)" if "przelot" in r["zrodlo"] else "—"
    else:
        d = round(z - n, 3); ok = "✓" if abs(d) <= TOL else "**✗**"
        if ok != "✓": nbad += 1
    md.append(f"| `{r['plik']}` | {r['cecha']} | {r['metoda']} | {z} | {n} | {d} | {ok} | {r['zrodlo']} |")
md += ["", f"Różnic > {TOL} mm: **{nbad}**.", "",
       "## 3. Profil haczyka blatu (prawy, y 0): x czubka w funkcji Z lokalnego STL (wierzch blatu Z 0; globalnie Z_g = 63,6 − Z)", "",
       "| Z STL | x | Z globalne |", "|---|---|---|"]
for z, x in prof:
    md.append(f"| {z} | {x} | {round(63.6 - z, 2)} |")
md += ["", "## 4. Profil garbu pokrywki (prawy, y 0): x czubka w funkcji Z STL (wierzch Z 0; garb nominalnie Z 17,6…18,4, czubek 47,6)", "", "| Z STL | x |", "|---|---|"]
for z, x in bump:
    md.append(f"| {z} | {x} |")
md += ["", "## 5. Profil rowka pokrywki w płytce n1 (bok +X, y 20): x dna w funkcji Z STL (wierzch Z 8; rowek nominalnie Z 5,5…6,5, dno 47,2)", "", "| Z STL | x |", "|---|---|"]
for z, x in grv:
    md.append(f"| {z} | {x} |")

md += ["", "## 6. Pasowania policzone z wartości zmierzonych", "", "| Para | Rachunek | Zmierzone | Nominał | Δ | OK | Reguła |", "|---|---|---|---|---|---|---|"]
for f in fits:
    z, n = f["zmierzone"], f["nominal"]
    d = "" if (z is None or n is None) else round(z - n, 3)
    ok = "—" if d == "" else ("✓" if abs(d) <= TOL else "**✗**")
    md.append(f"| {f['para']} | {f['rachunek']} | {z} | {n} | {d} | {ok} | {f['regula']} |")
open(os.path.join(OUT, "pomiary_stl.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
json.dump({"rows": rows, "fits": fits, "profil_haczyka": prof, "profil_garbu": bump, "profil_rowka_plytki": grv}, open(os.path.join(OUT, "pomiary_stl.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"wierszy: {len(rows)}, poza tolerancją: {nbad}")
for r in rows:
    z, n = r["zmierzone"], r["nominal"]
    if z is not None and n is not None and abs(z - n) > TOL:
        print("  ✗", r["plik"], "|", r["cecha"], "|", z, "vs", n)
    if z is None:
        print("  (brak trafienia)", r["plik"], "|", r["cecha"], "|", r["zrodlo"])
