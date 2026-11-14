# -*- coding: utf-8 -*-
"""
Recenzent R59 - pkt 8.1 (normalne): kontrola pliku binarnego STL 12 plytek bez Blendera (python + numpy):
rozmiar pliku = 84 + 50 * n, bajty atrybutow = 0, normalne ZAPISANE w pliku zgodne z kolejnoscia wierzcholkow
(iloczyn skalarny z normalna policzona z wierzcholkow > 0,999), brak trojkatow o zerowym polu, objetosc ze wzoru
dywergencji (wprost z float32 pliku) i gabaryt. Uruchomienie: python sprawdz_R59_normalne.py
"""
import os
import sys

import numpy as np

TU = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(os.path.dirname(TU), "Ramki", "wyniki_v2", "stl")
PLYTKI = ["ramka_plytka_wieczorna_v2", "ramka_plytka_wieczorna_n1_v2", "ramka_plytka_wieczorna_n2_v2",
          "ramka_plytka_wieczorna_n3_v2", "ramka_plytka_poranna_v2", "ramka_plytka_poranna_n4_v2",
          "ramka_plytka_poranna_n5_v2", "ramka_plytka_poranna_n6_v2", "ramka_plytka_okragla_wieczorna_v2",
          "ramka_plytka_okragla_wieczorna_n8_v2", "ramka_plytka_okragla_poranna_v2", "ramka_plytka_okragla_poranna_n9_v2"]
DT = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])


def main():
    nie = 0
    for p in PLYTKI:
        sc = os.path.join(STL, p + ".stl")
        with open(sc, "rb") as f:
            nagl = f.read(80)
            n = int(np.frombuffer(f.read(4), dtype="<u4")[0])
            d = np.frombuffer(f.read(), dtype=DT)
        rozm = os.path.getsize(sc)
        v = d["v"].astype(np.float64)
        nn = d["n"].astype(np.float64)
        c = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0])
        pole = np.linalg.norm(c, axis=1) / 2.0
        cu = c / np.maximum(np.linalg.norm(c, axis=1)[:, None], 1e-30)
        dl = np.linalg.norm(nn, axis=1)
        zg = np.einsum("ij,ij->i", cu, nn / np.maximum(dl[:, None], 1e-30))
        zle_n = int((zg < 0.999).sum())
        zero_n = int((dl < 0.5).sum())
        zero_p = int((pole < 1e-9).sum())
        obj = float(np.einsum("ij,ij->i", v[:, 0], np.cross(v[:, 1], v[:, 2])).sum() / 6000.0)
        lo = v.reshape(-1, 3).min(axis=0)
        hi = v.reshape(-1, 3).max(axis=0)
        ok = rozm == 84 + 50 * n and len(d) == n and int(d["a"].max()) == 0 and zle_n == 0 and zero_n == 0 and zero_p == 0 and \
            not np.isnan(v).any() and obj > 0
        nie += 0 if ok else 1
        print("[%s] %s: trojkatow %d, rozmiar %d (= 84 + 50 n: %s), atrybuty max %d, normalne zapisane niezgodne z wierzcholkami: %d,"
              " normalne zerowe: %d, trojkaty o zerowym polu: %d, min zgodnosc %.6f, objetosc %.4f cm3, gabaryt %s...%s, naglowek: %r" % (
                  "ZAL" if ok else "NIE", p, n, rozm, rozm == 84 + 50 * n, int(d["a"].max()), zle_n, zero_n, zero_p, float(zg.min()), obj,
                  np.round(lo, 4).tolist(), np.round(hi, 4).tolist(), nagl[:40].rstrip(b"\x00 ")))
    print("NORMALNE KONIEC: plikow %d, NIE %d" % (len(PLYTKI), nie))
    return 0 if nie == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
