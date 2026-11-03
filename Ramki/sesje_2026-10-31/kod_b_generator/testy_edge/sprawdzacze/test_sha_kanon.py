# -*- coding: utf-8 -*-
"""
Test funkcji read_stl() z recenzja/sprawdz_C2_sha.py i sprawdz_K59.py (porównanie kanoniczne, K‑59)
na wariantach z SP/lustro_sha (wygenerowanych przez zrob_lustra.py). Czysty Python (py -3.12 -I lub Python Blendera).
Nie pisze nic do projektu.
"""
import os, struct, hashlib, traceback

SP = r"<PC>\AppData\Local\Temp\claude\C--Users-<uzytkownik>-Desktop-Ramki\6066cedd-3612-4f95-9068-ea0e40643981\scratchpad\audyt_sprawdzacze"
L = os.path.join(SP, "lustro_sha")

# --- dosłowna kopia read_stl z sprawdz_K59.py (linie 5–19) ---
def read_stl(p):
    d = open(p, "rb").read()
    n = struct.unpack("<I", d[80:84])[0]
    tris = []; vol = 0.0; xs = []; ys = []; zs = []
    for i in range(n):
        o = 84 + 50 * i
        v = struct.unpack("<12f", d[o:o + 48])
        a, b, c = v[3:6], v[6:9], v[9:12]
        for q in (a, b, c):
            xs.append(q[0]); ys.append(q[1]); zs.append(q[2])
        vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
        key = tuple(sorted(tuple(round(x, 5) for x in q) for q in (a, b, c)))
        tris.append(key)
    tris.sort()
    return n, tris, vol / 1000.0, (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

base = read_stl(os.path.join(L, "wkladka_orig.stl"))
print("ORYGINAŁ: n=%d obj=%.4f gab=%s" % (base[0], base[2], [round(x, 3) for x in base[3]]))
for nm in ("wkladka_minus_zero.stl", "wkladka_odwrocone_nawiniecie.stl", "wkladka_ascii.stl", "wkladka_obcieta.stl", "wkladka_zly_licznik.stl"):
    p = os.path.join(L, nm)
    print("\n==", nm, "| SHA równe oryginałowi:", sha(p) == sha(os.path.join(L, "wkladka_orig.stl")), "| rozmiar", os.path.getsize(p))
    try:
        n, tris, vol, gab = read_stl(p)
        same = tris == base[1]
        diff = len(set(tris) ^ set(base[1]))
        print("   read_stl OK: n=%d TRI=%s różnych=%d obj=%.4f (oryg %.4f) gab=%s" % (n, same, diff, vol, base[2], [round(x, 3) for x in gab]))
        print("   -> fallback K-59 (|Δobj| ≤ 0,001, |Δgab| ≤ 0,01):", abs(vol - base[2]) <= 0.001 and all(abs(gab[i] - base[3][i]) <= 0.01 for i in range(3)))
    except Exception as e:
        print("   read_stl PADA:", type(e).__name__, str(e)[:120])
