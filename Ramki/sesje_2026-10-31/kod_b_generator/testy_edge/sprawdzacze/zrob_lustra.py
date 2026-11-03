# -*- coding: utf-8 -*-
"""
Audyt skryptów sprawdzających — generator luster testowych w scratchpadzie.
NIE dotyka projektu: czyta z <PC>\\Desktop\\Ramki (tylko odczyt), pisze wyłącznie do SP.

Tworzy:
  SP/lustro_A_uszk        — 8 płytek z różnymi uszkodzeniami (brak, 0 B, 0 trójkątów, NaN, ASCII, zły licznik, obcięty)
  SP/lustro_A_obciety1    — pierwsza płytka w kolejności FILES_A obcięta (test: czy JSON z wynikami powstaje po padzie)
  SP/lustro_C_uszk        — tulejka obcięta, podkładka_05 zły licznik, podkładka_1 ASCII, podkładka_2 0 trójkątów
  SP/lustro_C_k57         — arkusz_zamowienia.md bez wiersza sum „10 pozycji × ilości”
  SP/lustro_C_bezraportu  — bez wyniki_v2/raport/raport_wykonawcy_C_iter1.md
  SP/lustro_3oko_16       — 16 STL (bez ramka_podkladka_panelu_2_v2.stl)
  SP/lustro_sha           — kopie STL dla testu kanonicznego: −0,0 w normalnych, odwrócone nawinięcie, ASCII, obcięty
oraz kopie skryptów recenzji z ROOT/REC/OUT_DIR przekierowanymi na dane lustro (SP/skrypty_<lustro>/).

Uruchomienie (Python Blendera lub py -3.12):  python -I zrob_lustra.py
"""
import os, shutil, struct, math, sys

SRC = r"<PC>\Desktop\Ramki"
SP = r"<PC>\AppData\Local\Temp\claude\C--Users-<uzytkownik>-Desktop-Ramki\6066cedd-3612-4f95-9068-ea0e40643981\scratchpad\audyt_sprawdzacze"
STL_SRC = os.path.join(SRC, "wyniki_v2", "stl")

def read_stl(p):
    d = open(p, "rb").read()
    n = struct.unpack("<I", d[80:84])[0]
    recs = [d[84 + 50 * i: 84 + 50 * i + 50] for i in range(n)]
    return d[:80], recs

def write_stl(p, header, recs, count=None):
    with open(p, "wb") as f:
        f.write(header[:80].ljust(80, b"\0"))
        f.write(struct.pack("<I", len(recs) if count is None else count))
        for r in recs:
            f.write(r)

def to_ascii(p_in, p_out):
    header, recs = read_stl(p_in)
    with open(p_out, "w", encoding="ascii") as f:
        f.write("solid audyt\n")
        for r in recs:
            v = struct.unpack("<12f", r[:48])
            f.write("  facet normal %.6e %.6e %.6e\n    outer loop\n" % v[0:3])
            for k in (3, 6, 9):
                f.write("      vertex %.6e %.6e %.6e\n" % v[k:k + 3])
            f.write("    endloop\n  endfacet\n")
        f.write("endsolid audyt\n")

def nan_vertex(p_in, p_out):
    header, recs = read_stl(p_in)
    r = bytearray(recs[100]); r[12:16] = struct.pack("<f", float("nan")); recs[100] = bytes(r)
    write_stl(p_out, header, recs)

def truncate(p_in, p_out, frac=0.5):
    d = open(p_in, "rb").read()
    open(p_out, "wb").write(d[: int(len(d) * frac)])

def bad_count(p_in, p_out, extra=1000):
    header, recs = read_stl(p_in)
    write_stl(p_out, header, recs, count=len(recs) + extra)

def flip_zero_normals(p_in, p_out):
    """każde 0.0 w normalnej -> -0.0 (znany efekt z ramka_wkladka_v2.stl)"""
    header, recs = read_stl(p_in)
    out = []
    for r in recs:
        v = list(struct.unpack("<12f", r[:48]))
        for k in range(3):
            if v[k] == 0.0:
                v[k] = -0.0 if math.copysign(1, v[k]) > 0 else 0.0
        out.append(struct.pack("<12f", *v) + r[48:])
    write_stl(p_out, header, out)

def flip_winding(p_in, p_out, every=1):
    """odwraca kolejność wierzchołków (nawinięcie) w każdym trójkącie — normalna zostaje jak była"""
    header, recs = read_stl(p_in)
    out = []
    for i, r in enumerate(recs):
        v = struct.unpack("<12f", r[:48])
        if i % every == 0:
            v = v[0:3] + v[6:9] + v[3:6] + v[9:12]
        out.append(struct.pack("<12f", *v) + r[48:])
    write_stl(p_out, header, out)

def copytree_min(dst, stl_names, extra_dirs=("json", "arkusze", "raport", "render"), blend=False):
    os.makedirs(os.path.join(dst, "wyniki_v2", "stl"), exist_ok=True)
    for n in stl_names:
        shutil.copy(os.path.join(STL_SRC, n), os.path.join(dst, "wyniki_v2", "stl", n))
    for d in extra_dirs:
        shutil.copytree(os.path.join(SRC, "wyniki_v2", d), os.path.join(dst, "wyniki_v2", d), dirs_exist_ok=True)
    for f in ("README.md", "do_v3.md"):
        shutil.copy(os.path.join(SRC, "wyniki_v2", f), os.path.join(dst, "wyniki_v2", f))
    if blend:
        shutil.copy(os.path.join(SRC, "wyniki_v2", "ramka_v2.blend"), os.path.join(dst, "wyniki_v2", "ramka_v2.blend"))
    shutil.copy(os.path.join(SRC, "parametry.json"), os.path.join(dst, "parametry.json"))
    os.makedirs(os.path.join(dst, "recenzja"), exist_ok=True)
    for f in ("wyniki_A_iterC1.json", "wyniki_B_iterC1.json", "wyniki_C_iter2_sha.json"):
        shutil.copy(os.path.join(SRC, "recenzja", f), os.path.join(dst, "recenzja", f))

def script_copy(name, lustro, wyjscia):
    """kopia skryptu recenzji z przekierowanymi ścieżkami (ROOT -> lustro, REC/OUT -> wyjscia)"""
    src = os.path.join(SRC, "recenzja_koncowa" if name == "trzecie_oko" else "recenzja", name + ".py")
    s = open(src, encoding="utf-8").read().replace(r"<PC>\Desktop\Ramki", lustro)
    repl = {
        "sprawdz_A": [('REC = os.path.join(ROOT, "recenzja")', 'REC = r"%s"' % wyjscia)],
        "sprawdz_B": [('REC = os.path.join(ROOT, "recenzja")', 'REC = r"%s"' % wyjscia)],
        "sprawdz_C": [('REC = os.path.join(ROOT, "recenzja")', 'REC = r"%s"' % wyjscia)],
        "sprawdz_C2_sha": [('os.path.join(R, "recenzja", "wyniki_C_iter2_sha.json")', 'os.path.join(r"%s", "wyniki_C_iter2_sha.json")' % wyjscia)],
        "sprawdz_K59": [(lustro + r"\recenzja\wyniki_C_iter1_K59.json", wyjscia + r"\wyniki_C_iter1_K59.json")],
        "trzecie_oko": [('OUT_DIR = os.path.join(ROOT, "recenzja_koncowa")', 'OUT_DIR = r"%s"' % wyjscia)],
    }[name]
    for a, b in repl:
        assert a in s, (name, a)
        s = s.replace(a, b)
    os.makedirs(os.path.dirname(wyjscia) if False else wyjscia, exist_ok=True)
    out = os.path.join(os.path.dirname(wyjscia), "skrypt_" + name + ".py")
    open(out, "w", encoding="utf-8").write(s)
    # sprawdz_C czyta wyniki_A/B_iterC1.json i wyniki_C_iter2_sha.json z REC
    for f in ("wyniki_A_iterC1.json", "wyniki_B_iterC1.json", "wyniki_C_iter2_sha.json"):
        shutil.copy(os.path.join(SRC, "recenzja", f), os.path.join(wyjscia, f))
    return out

ALL = sorted(f for f in os.listdir(STL_SRC) if f.endswith(".stl"))
PLATES = [f for f in ALL if f.startswith("ramka_plytka")]
OTHER = [f for f in ALL if f not in PLATES]

def main():
    os.makedirs(SP, exist_ok=True)
    # --- lustro_A_uszk ------------------------------------------------------------------
    L = os.path.join(SP, "lustro_A_uszk"); shutil.rmtree(L, ignore_errors=True)
    copytree_min(L, ["ramka_plytka_wieczorna_v2.stl", "ramka_plytka_wieczorna_n1_v2.stl"], extra_dirs=("json", "arkusze"))
    S = os.path.join(L, "wyniki_v2", "stl")
    # n2: brak pliku (nie kopiujemy)
    truncate(os.path.join(STL_SRC, "ramka_plytka_wieczorna_n3_v2.stl"), os.path.join(S, "ramka_plytka_wieczorna_n3_v2.stl"))
    open(os.path.join(S, "ramka_plytka_poranna_v2.stl"), "wb").close()                       # 0 B
    write_stl(os.path.join(S, "ramka_plytka_poranna_n4_v2.stl"), b"audyt 0 tri", [])           # 0 trójkątów
    nan_vertex(os.path.join(STL_SRC, "ramka_plytka_poranna_n5_v2.stl"), os.path.join(S, "ramka_plytka_poranna_n5_v2.stl"))
    to_ascii(os.path.join(STL_SRC, "ramka_plytka_poranna_n6_v2.stl"), os.path.join(S, "ramka_plytka_poranna_n6_v2.stl"))
    bad_count(os.path.join(STL_SRC, "ramka_pokrywka_v2.stl"), os.path.join(S, "ramka_pokrywka_v2.stl"))
    script_copy("sprawdz_A", L, os.path.join(L, "wyjscia"))
    # --- lustro_A_obciety1: pierwszy plik w FILES_A obcięty ---------------------------------
    L = os.path.join(SP, "lustro_A_obciety1"); shutil.rmtree(L, ignore_errors=True)
    copytree_min(L, PLATES, extra_dirs=("json", "arkusze"))
    truncate(os.path.join(STL_SRC, "ramka_plytka_wieczorna_v2.stl"), os.path.join(L, "wyniki_v2", "stl", "ramka_plytka_wieczorna_v2.stl"))
    script_copy("sprawdz_A", L, os.path.join(L, "wyjscia"))
    # --- lustro_C_uszk ----------------------------------------------------------------------
    L = os.path.join(SP, "lustro_C_uszk"); shutil.rmtree(L, ignore_errors=True)
    copytree_min(L, [f for f in ALL if "tulejka" not in f and "podkladka" not in f])
    S = os.path.join(L, "wyniki_v2", "stl")
    truncate(os.path.join(STL_SRC, "ramka_tulejka_dc_v2.stl"), os.path.join(S, "ramka_tulejka_dc_v2.stl"))
    bad_count(os.path.join(STL_SRC, "ramka_podkladka_panelu_05_v2.stl"), os.path.join(S, "ramka_podkladka_panelu_05_v2.stl"))
    to_ascii(os.path.join(STL_SRC, "ramka_podkladka_panelu_1_v2.stl"), os.path.join(S, "ramka_podkladka_panelu_1_v2.stl"))
    write_stl(os.path.join(S, "ramka_podkladka_panelu_2_v2.stl"), b"audyt 0 tri", [])
    script_copy("sprawdz_C", L, os.path.join(L, "wyjscia"))
    # --- lustro_C_k57: .md bez wiersza sum --------------------------------------------------
    L = os.path.join(SP, "lustro_C_k57"); shutil.rmtree(L, ignore_errors=True)
    copytree_min(L, ALL)
    p = os.path.join(L, "wyniki_v2", "arkusze", "arkusz_zamowienia.md")
    md = open(p, encoding="utf-8").read()
    lines = [ln for ln in md.splitlines() if "10 pozycji × ilości" not in ln]
    assert len(lines) < len(md.splitlines()), "nie znaleziono wiersza sum"
    open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    script_copy("sprawdz_C", L, os.path.join(L, "wyjscia"))
    # --- lustro_C_bezraportu ----------------------------------------------------------------
    L = os.path.join(SP, "lustro_C_bezraportu"); shutil.rmtree(L, ignore_errors=True)
    copytree_min(L, ALL)
    os.remove(os.path.join(L, "wyniki_v2", "raport", "raport_wykonawcy_C_iter1.md"))
    script_copy("sprawdz_C", L, os.path.join(L, "wyjscia"))
    # --- lustro_3oko_16 ---------------------------------------------------------------------
    L = os.path.join(SP, "lustro_3oko_16"); shutil.rmtree(L, ignore_errors=True)
    copytree_min(L, [f for f in ALL if f != "ramka_podkladka_panelu_2_v2.stl"], extra_dirs=("json",), blend=True)
    script_copy("trzecie_oko", L, os.path.join(L, "wyjscia"))
    # --- lustro_sha: warianty do testu kanonicznego -----------------------------------------
    L = os.path.join(SP, "lustro_sha"); shutil.rmtree(L, ignore_errors=True); os.makedirs(L)
    w = os.path.join(STL_SRC, "ramka_wkladka_v2.stl")
    shutil.copy(w, os.path.join(L, "wkladka_orig.stl"))
    flip_zero_normals(w, os.path.join(L, "wkladka_minus_zero.stl"))
    flip_winding(w, os.path.join(L, "wkladka_odwrocone_nawiniecie.stl"))
    to_ascii(w, os.path.join(L, "wkladka_ascii.stl"))
    truncate(w, os.path.join(L, "wkladka_obcieta.stl"))
    bad_count(w, os.path.join(L, "wkladka_zly_licznik.stl"))
    print("lustra gotowe w", SP)

if __name__ == "__main__":
    main()
