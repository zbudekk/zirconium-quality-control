# -*- coding: utf-8 -*-
"""
Recenzent R59 - K-59 (powtarzalnosc, dodatkowo do planu sekcja 8): porownanie plikow z czystego przebiegu generatora
(recenzja/powtorka/Ramki: ramka_generator.py, parametry.json, plan_ramki_v2.md, protokol_weryfikacji_v2.md z git HEAD,
BEZ wyniki_v2 - JSON ukladu odtwarzane z ev_rows / mo_rows) z plikami oddanymi do recenzji (r59/Ramki/wyniki_v2).
SHA-256; przy roznicy SHA porownanie kanoniczne (posortowane trojkaty, wierzcholki do 1e-5), objetosc, gabaryt.
Uruchomienie: python sprawdz_R59_K59.py   (po przebiegu generatora w powtorka/Ramki)
"""
import glob
import hashlib
import json
import os
import struct
import sys

TU = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(os.path.dirname(TU), "Ramki", "wyniki_v2")
B = os.path.join(TU, "powtorka", "Ramki", "wyniki_v2")


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def czytaj_stl(p):
    with open(p, "rb") as f:
        d = f.read()
    n = struct.unpack("<I", d[80:84])[0]
    tris = []
    vol = 0.0
    for i in range(n):
        o = 84 + 50 * i
        v = struct.unpack("<12f", d[o:o + 48])
        a, b, c = v[3:6], v[6:9], v[9:12]
        vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
        tris.append(tuple(sorted(tuple(round(x, 5) + 0.0 for x in q) for q in (a, b, c))))
    tris.sort()
    return n, tris, vol / 1000.0


def main():
    pliki = sorted(os.path.basename(p) for p in glob.glob(os.path.join(A, "stl", "*.stl")))
    pb = sorted(os.path.basename(p) for p in glob.glob(os.path.join(B, "stl", "*.stl")))
    print("STL oddane: %d, w powtorce: %d, brakuje %s, nadmiar %s" % (len(pliki), len(pb), sorted(set(pliki) - set(pb)), sorted(set(pb) - set(pliki))))
    out = {}
    n_sha = n_kan = 0
    for f in pliki:
        fa = os.path.join(A, "stl", f)
        fb = os.path.join(B, "stl", f)
        if not os.path.isfile(fb):
            print("BRAK w powtorce: %s" % f)
            out[f] = "BRAK"
            continue
        ha, hb = sha(fa), sha(fb)
        e = {"sha_rowne": ha == hb, "sha_oddany": ha, "sha_powtorka": hb}
        if ha == hb:
            n_sha += 1
            n_kan += 1
        else:
            na, ta, va = czytaj_stl(fa)
            nb, tb, vb = czytaj_stl(fb)
            e.update({"trojkatow": [na, nb], "kanonicznie_rowne": ta == tb, "roznych_trojkatow": len(set(ta) ^ set(tb)),
                      "objetosc": [round(va, 4), round(vb, 4)]})
            n_kan += 1 if ta == tb else 0
        out[f] = e
        print("%s %s%s" % ("SHA=" if ha == hb else "SHA!=", f, "" if ha == hb else " " + json.dumps(e)))
    nj = 0
    js = sorted(os.path.basename(p) for p in glob.glob(os.path.join(A, "json", "*.json")))
    for f in js:
        fb = os.path.join(B, "json", f)
        r = os.path.isfile(fb) and sha(os.path.join(A, "json", f)) == sha(fb)
        nj += 1 if r else 0
        out[f] = {"sha_rowne": r}
        print("%s %s" % ("SHA=" if r else "SHA!=", f))
    print("K-59: STL bajtowo identyczne %d / %d, kanonicznie identyczne %d / %d; JSON ukladu identyczne %d / %d" % (
        n_sha, len(pliki), n_kan, len(pliki), nj, len(js)))
    with open(os.path.join(TU, "wyniki", "K59_R59.json"), "w", encoding="utf-8") as fo:
        json.dump(out, fo, indent=1)
    return 0 if (n_kan == len(pliki) and nj == len(js)) else 1


if __name__ == "__main__":
    sys.exit(main())
