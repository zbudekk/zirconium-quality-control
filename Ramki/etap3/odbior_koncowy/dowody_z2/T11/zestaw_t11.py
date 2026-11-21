# Zestawienie liczb kryterium T11 czesc B (tylko odczyt; pomocnik wykonawcy testow, nie narzedzie planu).
# Uzycie: python.exe -I zestaw_t11.py <stanowisko.sqlite> <t11_symulator.json> <katalog skanow 1> [<katalog skanow 2> ...]
# Prawda: sha16 = pierwsze 16 znakow SHA-256 pliku STL, uklad = pole "plytka" pliku .json obok skanu.
import glob
import hashlib
import json
import os
import sqlite3
import sys


def sha16(sciezka):
    h = hashlib.sha256()
    with open(sciezka, "rb") as f:
        while True:
            b = f.read(1 << 22)
            if not b:
                break
            h.update(b)
    return h.hexdigest()[:16]


def main():
    baza, dziennik, katalogi = sys.argv[1], sys.argv[2], sys.argv[3:]
    prawda = {}
    for k in katalogi:
        for stl in sorted(glob.glob(os.path.join(k, "*.stl"))):
            with open(os.path.splitext(stl)[0] + ".json", encoding="utf-8") as f:
                prawda[sha16(stl)] = (json.load(f).get("plytka"), os.path.basename(stl))
    print("plikow prawdy (STL + json): %d" % len(prawda))
    with open(dziennik, encoding="utf-8") as f:
        zapisy = json.load(f)["zapisy"]
    dobre = [z for z in zapisy if z.get("rodzaj") == "dobry"]
    sha_dz = [z["sha16"] for z in dobre]
    print("dziennik symulatora: zapisow %d, dobrych %d, roznych sha16 %d, sha16 spoza prawdy %d"
          % (len(zapisy), len(dobre), len(set(sha_dz)), len([s for s in sha_dz if s not in prawda])))
    m = len(dobre)
    con = sqlite3.connect("file:" + baza.replace("\\", "/") + "?mode=ro", uri=True)
    wiersze = con.execute(
        "SELECT s.id, s.sha16, s.status, s.uklad, s.uklad_zrodlo, s.uklad_zgodny, "
        "sum(p.status_gniazda='zielony') FROM skany s LEFT JOIN prace p ON p.skan_id = s.id "
        "GROUP BY s.id ORDER BY s.id").fetchall()
    con.close()
    po_sha = {}
    for w in wiersze:
        po_sha.setdefault(w[1], []).append(w)
    print("wierszy w skany: %d (roznych sha16 %d)" % (len(wiersze), len(po_sha)))
    w_bazie = rozp = auto = niepusty = 0
    zly_n = zly_ziel = 0
    statusy = {}
    for nr, s in enumerate(sha_dz, 1):
        ww = po_sha.get(s)
        pr = prawda.get(s, (None, "?"))
        if not ww:
            print("BRAK WIERSZA w skany (NIE ZMIERZONO): nr %d sha16 %s prawda %s" % (nr, s, pr[0]))
            continue
        w = ww[-1]
        w_bazie += 1
        statusy[w[2]] = statusy.get(w[2], 0) + 1
        if w[3]:
            niepusty += 1
        if w[3] == pr[0]:
            rozp += 1
        else:
            print("UKLAD INNY NIZ PRAWDA: nr %d sha16 %s baza %r prawda %r status %s (%s)" % (nr, s, w[3], pr[0], w[2], pr[1]))
        if w[4] == "auto":
            auto += 1
        if w[2] == "niezgodny_uklad" or w[5] == 0:
            zly_n += 1
            zly_ziel += int(w[6] or 0)
            print("ZLY UKLAD: nr %d sha16 %s status %s uklad_zgodny %r zielonych %r" % (nr, s, w[2], w[5], w[6]))
    print("(n) skany z dziennika z wierszem w skany: %d z %d" % (w_bazie, m))
    print("(a) UKLAD ROZPOZNANY (skany.uklad = plytka z prawdy): %d z %d; uklad_zrodlo = auto: %d z %d" % (rozp, m, auto, m))
    print("(b) ZIELONE PRZY ZLYM UKLADZIE: %d (skanow niezgodny_uklad albo uklad_zgodny = 0: %d)" % (zly_ziel, zly_n))
    print("(c) skany.uklad NIEPUSTY: %d z %d" % (niepusty, m))
    print("statusy skanow: %s" % json.dumps(statusy, sort_keys=True))
    print("punkt odniesienia (noc): 40 z 40, auto 40 z 40, zielone 0 (0 skanow), niepusty 40 z 40")


if __name__ == "__main__":
    main()
