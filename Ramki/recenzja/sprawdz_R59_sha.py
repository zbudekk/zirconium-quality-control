# -*- coding: utf-8 -*-
"""
Recenzent R59 - pkt 8.6: sumy SHA-256 (python, bez pakietow dodatkowych).
Wartosci oczekiwane sa PARSOWANE z dokumentow (kopia z git HEAD w ref/): R59_wdrozenie_zmiany.md (12 STL + 4 JSON),
Ramki_pakiet/SHA256SUMS_2026-11-02_R57.txt (9 plikow nieplytkowych, stary uklad), raport wykonawcy R59 iter2.
Uruchomienie: python sprawdz_R59_sha.py   (katalog <PC-katalog>/r59/recenzja; wynik: wyniki/sha_R59.json)
"""
import hashlib
import json
import os
import re
import sys

TU = os.path.dirname(os.path.abspath(__file__))
BAZA = os.path.join(os.path.dirname(TU), "Ramki")
REF = os.path.join(TU, "ref", "Ramki")
WYN = os.path.join(TU, "wyniki")
ARCH = os.path.join(BAZA, "archiwum", "wyniki_v2_przed_R59_2026-11-14")
PLYTKI = ["ramka_plytka_wieczorna_v2", "ramka_plytka_wieczorna_n1_v2", "ramka_plytka_wieczorna_n2_v2",
          "ramka_plytka_wieczorna_n3_v2", "ramka_plytka_poranna_v2", "ramka_plytka_poranna_n4_v2",
          "ramka_plytka_poranna_n5_v2", "ramka_plytka_poranna_n6_v2", "ramka_plytka_okragla_wieczorna_v2",
          "ramka_plytka_okragla_wieczorna_n8_v2", "ramka_plytka_okragla_poranna_v2", "ramka_plytka_okragla_poranna_n9_v2"]
INNE = ["ramka_korpus_W_v2", "ramka_korpus_P_v2", "ramka_blat_v2", "ramka_wkladka_v2", "ramka_pokrywka_v2",
        "ramka_tulejka_dc_v2", "ramka_podkladka_panelu_05_v2", "ramka_podkladka_panelu_1_v2", "ramka_podkladka_panelu_2_v2"]
JSONY = ["uklad_gniazd_wieczorna.json", "uklad_gniazd_poranna.json", "uklad_gniazd_okragla_wieczorna.json",
         "uklad_gniazd_okragla_poranna.json"]
PAR_OCZEK = "8434aafe1584bdd5e8cb88776566e5c697fd48dac8bc02685b02b3d70d32f3b2"   # zlecenie koordynatora (worktree HEAD)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def czytaj(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def sumy_z_tabeli_md(tekst):
    """wiersze tabeli: | `nazwa` ... | [jedna kolumna, np. rozmiar |] <64 hex> | ... -> {nazwa: sha}"""
    out = {}
    for m in re.finditer(r"\|\s*`([^`|]+)`[^|]*\|(?:[^|`]*\|)?\s*`?([0-9a-f]{64})`?\s*\|", tekst):
        out[os.path.basename(m.group(1))] = m.group(2)
    return out


def sumy_z_listy(tekst):
    """linie '<64 hex> *sciezka' albo '<64 hex>  sciezka' -> {basename: [sha, ...]}"""
    out = {}
    for m in re.finditer(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$", tekst, re.M):
        out.setdefault(os.path.basename(m.group(2).replace("\\", "/")), []).append(m.group(1).lower())
    return out


def main():
    os.makedirs(WYN, exist_ok=True)
    wyn = {"sprawdzenia": []}
    nie = 0

    def spr(nazwa, lista):
        nonlocal nie
        zg = sum(1 for e in lista if e[1] == e[2])
        ok = zg == len(lista) and len(lista) > 0
        nie += 0 if ok else 1
        wyn["sprawdzenia"].append({"nazwa": nazwa, "zgodne": zg, "z": len(lista), "ok": ok,
                                   "roznice": [e for e in lista if e[1] != e[2]]})
        print("[%s] %s: %d / %d zgodnych" % ("ZAL" if ok else "NIE", nazwa, zg, len(lista)))
        for e in lista:
            if e[1] != e[2]:
                print("     ROZNICA %s: jest %s, oczekiwane %s" % e)

    stl = dict((n, sha(os.path.join(BAZA, "wyniki_v2", "stl", n + ".stl"))) for n in PLYTKI + INNE)
    js = dict((n, sha(os.path.join(BAZA, "wyniki_v2", "json", n))) for n in JSONY)
    wyn["pc_stl"] = stl
    wyn["pc_json"] = js
    ile_stl = len([f for f in os.listdir(os.path.join(BAZA, "wyniki_v2", "stl")) if f.lower().endswith(".stl")])
    print("plikow STL w wyniki_v2/stl na PC: %d" % ile_stl)
    wyn["pc_stl_liczba"] = ile_stl
    # 1. dokument wdrozenia R59
    d59 = sumy_z_tabeli_md(czytaj(os.path.join(REF, "R59_wdrozenie_zmiany.md")))
    spr("12 STL plytek = R59_wdrozenie_zmiany.md", [(n, stl[n], d59.get(n + ".stl")) for n in PLYTKI])
    spr("4 JSON ukladu = R59_wdrozenie_zmiany.md", [(n, js[n], d59.get(n)) for n in JSONY])
    # 2. raport wykonawcy (sekcja 2)
    rw = sumy_z_tabeli_md(czytaj(os.path.join(REF, "wyniki_v2", "raport", "raport_wykonawcy_R59_iter2.md")))
    spr("21 STL + 4 JSON = raport wykonawcy R59 iter2 sekcja 2",
        [(n, stl[n], rw.get(n + ".stl")) for n in PLYTKI + INNE] + [(n, js[n], rw.get(n)) for n in JSONY])
    # 3. pliki nieplytkowe = pakiet R57
    s57 = sumy_z_listy(czytaj(os.path.join(REF, "Ramki_pakiet", "SHA256SUMS_2026-11-02_R57.txt")))
    spr("9 plikow nieplytkowych = SHA256SUMS R57", [(n, stl[n], (s57.get(n + ".stl") or [None])[0]) for n in INNE])
    # 4. parametry.json i JSON ukladu: PC = git HEAD (ref)
    p_pc = sha(os.path.join(BAZA, "parametry.json"))
    p_ref = sha(os.path.join(REF, "parametry.json"))
    wyn["parametry"] = {"pc": p_pc, "ref_git_HEAD": p_ref, "oczekiwane": PAR_OCZEK}
    spr("parametry.json: PC = git HEAD = 8434aafe...", [("PC", p_pc, PAR_OCZEK), ("git HEAD", p_ref, PAR_OCZEK)])
    spr("4 JSON ukladu: PC = git HEAD", [(n, js[n], sha(os.path.join(REF, "wyniki_v2", "json", n))) for n in JSONY])
    # 5. archiwum starego ukladu (zrodlo kontroli odwrotnej)
    lista = sumy_z_listy(czytaj(os.path.join(ARCH, "sha256_stl_przed_R59.txt")))
    ast = dict((n, sha(os.path.join(ARCH, "stl", n + ".stl"))) for n in PLYTKI + INNE)
    spr("archiwum: 21 starych STL = sha256_stl_przed_R59.txt", [(n, ast[n], (lista.get(n + ".stl") or [None])[0]) for n in PLYTKI + INNE])
    wpak = [n for n in PLYTKI if n + ".stl" in s57]
    spr("archiwum: stare STL plytek = SHA256SUMS R57 (pliki obecne w pakiecie: %d)" % len(wpak),
        [(n, ast[n], s57[n + ".stl"][0]) for n in wpak])
    aj = dict((n, sha(os.path.join(ARCH, "json", n))) for n in JSONY)
    spr("archiwum: 4 stare JSON = SHA256SUMS R57", [(n, aj[n], (s57.get(n) or [None])[0]) for n in JSONY])
    ps = sha(os.path.join(BAZA, "archiwum", "parametry_przed_R59_2026-11-14.json"))
    spr("archiwum: parametry_przed_R59 = SHA256SUMS R57 (parametry.json) = git HEAD (ref)",
        [("PC", ps, (s57.get("parametry.json") or [None])[0]),
         ("ref", sha(os.path.join(REF, "archiwum", "parametry_przed_R59_2026-11-14.json")), ps)])
    wyn["archiwum_stl"] = ast
    # 6. nowe plytki rozne od starych i miedzy soba
    zm = [(n, "zmieniony" if stl[n] != ast[n] else "BEZ ZMIAN", "zmieniony") for n in PLYTKI]
    spr("12 plikow plytek ma inne SHA niz przed R59", zm)
    spr("12 plikow plytek: SHA parami rozne", [("liczba roznych", len(set(stl[n] for n in PLYTKI)), 12)])
    spr("9 plikow nieplytkowych: SHA = archiwum sprzed R59", [(n, stl[n], ast[n]) for n in INNE])
    wyn["nie"] = nie
    with open(os.path.join(WYN, "sha_R59.json"), "w", encoding="utf-8") as f:
        json.dump(wyn, f, indent=1)
    print("SHA KONIEC: sprawdzen %d, NIE %d" % (len(wyn["sprawdzenia"]), nie))
    for n in PLYTKI + INNE:
        print("%s  %s.stl" % (stl[n], n))
    for n in JSONY:
        print("%s  %s" % (js[n], n))
    return 0 if nie == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
