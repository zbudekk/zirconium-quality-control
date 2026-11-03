"""Niezależny pomiar STL (trimesh). Tylko odczyt; wynik na stdout."""
import sys, json, math
import numpy as np
import trimesh

STL = r"<PC>\Desktop\Ramki\wyniki_v2\stl"
files = ["ramka_korpus_W_v2", "ramka_korpus_P_v2", "ramka_blat_v2", "ramka_wkladka_v2",
         "ramka_plytka_wieczorna_n1_v2", "ramka_plytka_poranna_n4_v2", "ramka_pokrywka_v2",
         "ramka_tulejka_dc_v2", "ramka_podkladka_panelu_1_v2"]
M = {}
print("plik | bbox X×Y×Z | obj cm3 | watertight | tris")
for f in files:
    m = trimesh.load(f"{STL}\\{f}.stl", force="mesh")
    M[f] = m
    e = m.extents
    print(f"{f} | {e[0]:.3f}×{e[1]:.3f}×{e[2]:.3f} | {m.volume/1000:.2f} | {m.is_watertight} | {len(m.faces)}")

def chord(m, origin, direction):
    """Cięciwa w materiale/otworze: odległość między pierwszymi dwoma trafieniami promienia."""
    o = np.array([origin]); d = np.array([direction], float)
    loc, idx, _ = m.ray.intersects_location(o, d, multiple_hits=True)
    if len(loc) < 2:
        return None
    t = np.sort(np.linalg.norm(loc - o, axis=1))
    return t

k = M["ramka_korpus_W_v2"]
# korpus: układ STL = globalny D3 (dno Z=0), środek XY = środek obrysu
c = k.bounds.mean(axis=0); cx = c[0]; cy = (k.bounds[0][1] + 0.3 + k.bounds[1][1]) / 2  # napis +0,6 w -Y
print("korpus środek szacowany", round(cx, 3), round(cy, 3))
# wnętrze: promień od środka w +X na Z 30 -> pierwsze trafienie = ściana wewn.
for name, d in [("+X", [1, 0, 0]), ("-X", [-1, 0, 0]), ("+Y", [0, 1, 0]), ("-Y", [0, -1, 0])]:
    t = chord(k, [cx, cy, 30], d)
    print(f"korpus ściana {name}: wewn. {t[0]:.3f}, zewn. {t[1]:.3f}, ścianka {t[1]-t[0]:.3f}")
# dno
t = chord(k, [cx + 64, cy + 54, -5], [0, 0, 1]); print("korpus dno grubość:", round(t[1] - t[0], 3))
# otwór DC ø12 w ścianie x=-40..-42, oś (y 89, Z 30): cięciwa w Y przez oś
t = chord(k, [cx - 41, cy + 60, 30], [0, 1, 0]); print("otwór DC: trafienia Y od 60:", np.round(t[:4], 3))
# kieszeń zatrzasku lewej ściany y=0: Z 52,6..55,1, głębokość 1,0 -> cięciwa w X na Z 53,85
t = chord(k, [cx - 90, cy, 53.85], [-1, 0, 0]); print("kieszeń zatrzasku L: ścianka za kieszenią", np.round(t[:2], 3), "->", round(t[1]-t[0], 3))
# wysokość korpusu
print("korpus wysokość max Z:", round(k.bounds[1][2], 3))
# boss Pi (-46.5,-24.5): cięciwa Z
t = chord(k, [cx - 46.5 + 3.5, cy - 24.5, -1], [0, 0, 1]); print("boss Pi wierzch (Z):", np.round(t[:2], 3))
t = chord(k, [cx - 46.5, cy - 24.5, -1], [0, 0, 1]); print("otwór bossa Pi (Z trafienia):", np.round(t[:4], 3))
# stadion panelu (60,60): wierzch
t = chord(k, [cx + 62.5, cy + 57.5, -1], [0, 0, 1]); print("stadion obok rowka (62.5,57.5) Z trafienia:", np.round(t[:4], 3))
# rowek: szerokość prostopadle do przekątnej w (60,60)
dd = np.array([1, -1, 0]) / math.sqrt(2)
t = chord(k, [cx + 60 - 10 * dd[0], cy + 60 - 10 * dd[1], 1.5], dd); print("rowek panelu cięciwa:", np.round(t[:2], 3), "szer.", round(t[1]-t[0], 3))
# szczeliny wentylacyjne tył x=-54, Z 8: cięciwa Z przez ścianę y=+99
t = chord(k, [cx - 54, cy + 99, 0.5], [0, 0, 1]); print("szczelina tył Z:", np.round(t[:4], 3))
# okno USB 16×9 w (60, Z24)
t = chord(k, [cx + 40, cy + 99, 24], [1, 0, 0]); print("okno USB X:", np.round(t[:6], 3))

b = M["ramka_blat_v2"]
cb = b.bounds.mean(axis=0)
# kołnierz zewn. 194: cięciwa w X na wysokości kołnierza (STL wierzchem w dół: wierzch Z=0, kołnierz do Z 14)
t = chord(b, [cb[0] - 110, cb[1] + 30, 9], [1, 0, 0]); print("blat kołnierz X trafienia:", np.round(t, 3))
t = chord(b, [cb[0] - 110, cb[1], 12.5], [1, 0, 0]); print("blat haczyk (y=0) Z lok 12,5 X trafienia:", np.round(t, 3))
print("blat wys:", round(b.extents[2], 3))

w = M["ramka_wkladka_v2"]
cw = w.bounds.mean(axis=0)
# środek otworu: y_min+52,3 (uszy w +Y), x środek obrysu
ox = cw[0]; oy = w.bounds[0][1] + 52.3
t = chord(w, [ox - 70, oy, 3.5 + 4.5], [1, 0, 0]); print("wkładka otwór X trafienia:", np.round(t, 3))
t = chord(w, [ox, oy - 70, 3.5 + 4.5], [0, 1, 0]); print("wkładka otwór Y trafienia:", np.round(t, 3))

p = M["ramka_plytka_wieczorna_n1_v2"]
cp = p.bounds.mean(axis=0)
print("płytka bok:", np.round(p.extents, 3))
t = chord(p, [cp[0] - 42, cp[1] - 42, -1], [0, 0, 1]); print("stożek A: Z trafienia od dołu:", np.round(t, 3))
t = chord(p, [cp[0] - 45, cp[1] - 36, 9], [0, 0, -1]); print("dołek A: Z od góry:", np.round(t, 3))

tu = M["ramka_tulejka_dc_v2"]; ct = tu.bounds.mean(axis=0)
t = chord(tu, [ct[0] - 10, ct[1], 2.5], [1, 0, 0]); print("tulejka walec X trafienia:", np.round(t, 3), "ø zewn.", round(t[-1]-t[0], 3), "ø wewn.", round(t[2]-t[1], 3))

# przekątna płytki (pole skanowania przy obrocie)
print("przekątna płytki:", round(96 * math.sqrt(2), 2))
# pole szczelin
print("wylot 10×12×3 =", 10 * 12 * 3, "mm²; wlot 2×30×4 =", 2 * 30 * 4, "mm²")
