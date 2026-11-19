#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R58 (19.11.2026): arkusz zamowienia kompletu okraglego do ramki.

Zrodla (nic nie jest wpisane w skrypcie):
  - ilosci i materialy: parametry.json -> quantities_r58 / materials_r58; stawki: cost_rate_min / max, mnozniki,
  - objetosci, gabaryty i SHA-256 plikow R58: tabela "2. Pliki wytworzone" raportu generatora na plikach oddanych
    (domyslnie wyniki_v2/raport/raport_wykonawcy_R58_SPRAWDZ_iter3.md),
  - czesci ramki bez zmian (korpus W, korpus P, blat): R59_arkusz_zamowienia.csv.
Kontrole (niezgodnosc = blad, pliki nie powstaja):
  1. SHA-256 w raporcie = wyniki_v2/raport/sha256_stl_po_R58.txt,
  2. SHA-256 pliku w wyniki_v2/stl (gdy lezy na dysku) = raport,
  3. kazda pozycja quantities_r58 ma wiersz w raporcie i material w materials_r58.

Uruchomienie (z folderu Ramki):
    python narzedzia/arkusz_zamowienia_R58.py <katalog_docelowy> [--nazwa R58_arkusz_zamowienia] [--raport <plik.md>]
Tylko biblioteka standardowa. Wynik w ASCII (bez znakow diakrytycznych), CSV: separator ';', przecinek dziesietny.
"""
import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STL = ROOT / "wyniki_v2" / "stl"
RAPORT = ROOT / "wyniki_v2" / "raport" / "raport_wykonawcy_R58_SPRAWDZ_iter3.md"
SUMY = ROOT / "wyniki_v2" / "raport" / "sha256_stl_po_R58.txt"
R59_CSV = ROOT / "R59_arkusz_zamowienia.csv"
P = json.loads((ROOT / "parametry.json").read_text(encoding="utf-8"))
GR = chr(96)   # grawis (znacznik kodu w Markdown)

# pozycje R59, ktore wchodza do kompletu okraglego bez zmian / ktore komplet okragly zastepuje
R59_BEZ_ZMIAN = ("ramka_korpus_W_v2.stl", "ramka_korpus_P_v2.stl", "ramka_blat_v2.stl")
R59_ZASTAPIONE = ("ramka_plytka_wieczorna_n1_v2.stl", "ramka_plytka_wieczorna_n2_v2.stl", "ramka_plytka_wieczorna_n3_v2.stl",
                  "ramka_plytka_poranna_n4_v2.stl", "ramka_plytka_poranna_n5_v2.stl", "ramka_plytka_poranna_n6_v2.stl",
                  "ramka_wkladka_v2.stl", "ramka_pokrywka_v2.stl")


def par(k):
    for sekcja in P.values():
        if isinstance(sekcja, dict) and k in sekcja:
            return sekcja[k]["value"]
    raise SystemExit("BLAD: brak klucza %s w parametry.json" % k)


def pl(x, n=2):
    return ("%.*f" % (n, x)).replace(".", ",")


def zl(a, b):
    return "%d-%d" % (round(a), round(b))


def kod(t):
    return GR + t + GR


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def wczytaj_raport(sciezka):
    """nazwa pliku STL -> (sha, (x, y, z), objetosc cm3) z tabeli '2. Pliki wytworzone'."""
    wynik = {}
    for linia in sciezka.read_text(encoding="utf-8").splitlines():
        pola = [p.strip().strip(GR) for p in linia.split("|")]
        if len(pola) < 7 or not pola[1].startswith("stl/"):
            continue
        liczby = re.findall(r"\d+\.\d+", pola[4])
        if len(liczby) != 3 or not re.fullmatch(r"[0-9a-f]{64}", pola[3]):
            raise SystemExit("BLAD: nieczytelny wiersz raportu: %s" % linia[:80])
        wynik[pola[1][4:]] = (pola[3], tuple(float(x) for x in liczby), float(pola[5]))
    return wynik


def wczytaj_sumy(sciezka):
    wynik = {}
    for linia in sciezka.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([0-9a-f]{64}) \*stl/(\S+)$", linia.strip())
        if m:
            wynik[m.group(2)] = m.group(1)
    return wynik


def opis(rdzen):
    m = re.match(r"ramka_plytka_okragla_ramkowa_(wieczorna|poranna)_n(\d)$", rdzen)
    if m:
        return "plytka okragla ramkowa %s n%s" % (m.group(1), m.group(2))
    return {"ramka_wkladka_okragla": "wkladka okragla gniazda plytki", "ramka_pokrywka_okragla": "pokrywka okragla plytki"}[rdzen]


def uwagi(rdzen):
    if rdzen.startswith("ramka_plytka"):
        return ("R58: lezy na ramce (3 kieszenie magnesow od spodu, rowek pokrywki, rowek klucza); "
                "sciecia orientacyjnego i rowkow nie wygladzac; nie pasuje do wkladki kwadratowej")
    if rdzen == "ramka_wkladka_okragla":
        return "R58: zamiast ramka_wkladka_v2.stl; 2 do ramek + 1 zapas; scianka w osiach 2,0 mm - nie szlifowac"
    return "R58: druk wlasny wierzchem w dol; sile zatrzasku sprawdzic na pierwszej sztuce"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cel")
    ap.add_argument("--nazwa", default="R58_arkusz_zamowienia")
    ap.add_argument("--raport", default=str(RAPORT))
    a = ap.parse_args()
    raport = wczytaj_raport(Path(a.raport))
    sumy = wczytaj_sumy(SUMY)
    il, mat = par("quantities_r58"), par("materials_r58")
    rmin, rmax = par("cost_rate_min"), par("cost_rate_max")
    dye, smooth = par("cost_dye_factor"), par("cost_smooth_factor")
    bledy = []
    wiersze = []
    for rdzen in il:
        plik = rdzen + "_v2.stl"
        if plik not in raport:
            bledy.append("brak %s w raporcie %s" % (plik, a.raport))
            continue
        if rdzen not in mat:
            bledy.append("brak materialu dla %s" % rdzen)
            continue
        sha, gab, obj = raport[plik]
        if sumy.get(plik) != sha:
            bledy.append("%s: SHA raportu %s != %s (%s)" % (plik, sha[:8], str(sumy.get(plik))[:8], SUMY.name))
        na_dysku = STL / plik
        stan = "brak pliku na dysku - pominiete"
        if na_dysku.exists():
            s = sha256(na_dysku)
            stan = "zgodny"
            if s != sha:
                bledy.append("%s: SHA pliku na dysku %s != raport %s" % (plik, s[:8], sha[:8]))
        drukarnia = mat[rdzen].startswith("PA12 drukarnia")
        wiersze.append({"plik": plik, "czesc": opis(rdzen), "szt": il[rdzen], "mat": mat[rdzen], "obj": obj, "gab": gab, "sha": sha,
                        "drukarnia": drukarnia, "kmin": obj * il[rdzen] * rmin if drukarnia else None,
                        "kmax": obj * il[rdzen] * rmax if drukarnia else None, "uwagi": uwagi(rdzen), "dysk": stan})
    r59 = {}
    with open(R59_CSV, encoding="utf-8-sig", newline="") as f:
        for w in csv.reader(f, delimiter=";"):
            r59[w[0]] = w
    for n in R59_BEZ_ZMIAN + R59_ZASTAPIONE:
        if n not in r59:
            bledy.append("brak %s w %s" % (n, R59_CSV.name))
    if bledy:
        for b in bledy:
            print("BLAD: " + b)
        return 1

    def liczba(t):
        return float(t.replace(",", ".")) if t else 0.0

    def r59_wiersz(n):
        w = r59[n]
        return {"plik": n, "szt": int(w[2]), "obj": liczba(w[7]), "gab": w[8].replace(chr(215), "x"),
                "nmin": liczba(w[9]), "nmax": liczba(w[10]), "pmin": liczba(w[11]), "pmax": liczba(w[12])}

    bez = [r59_wiersz(n) for n in R59_BEZ_ZMIAN]
    zast = [r59_wiersz(n) for n in R59_ZASTAPIONE]
    dr = [w for w in wiersze if w["drukarnia"]]
    wl = [w for w in wiersze if not w["drukarnia"]]
    obj_r58 = sum(w["obj"] * w["szt"] for w in dr)
    kmin_r58, kmax_r58 = sum(w["kmin"] for w in dr), sum(w["kmax"] for w in dr)
    obj_bez = sum(w["obj"] * w["szt"] for w in bez)
    obj_zast = sum(w["obj"] * w["szt"] for w in zast if w["nmin"])
    L = []
    L.append("# Arkusz zamowienia R58 - komplet okragly do ramki (19.11.2026)")
    L.append("")
    L.append("Wygenerowany przez %s. Objetosci, gabaryty (orientacja druku) i sumy SHA-256 z raportu generatora "
             "%s (pomiar na plikach oddanych); ilosci i materialy z %s -> %s / %s. "
             "Ten sam arkusz w %s (separator ;, przecinek dziesietny)." % (
                 kod("narzedzia/arkusz_zamowienia_R58.py"), kod(Path(a.raport).name), kod("parametry.json"),
                 kod("quantities_r58"), kod("materials_r58"), kod(a.nazwa + ".csv")))
    L.append("")
    L.append("Decyzje wlasciciela 19.11.2026: pelny komplet okragly (plytki + wkladka + pokrywka), numery n1-n3 wieczorne i n4-n6 poranne, "
             "srednica 100 mm (pole skanowania niezmierzone - ryzyko przyjete). Korpusy i blaty ramek bez zmian (pliki R59).")
    L.append("")
    L.append("## A. Nowe pliki do drukarni (PA12, bialy naturalny, mat, bez wygladzania)")
    L.append("")
    L.append("| Plik STL | Czesc | Szt. | Obj. [cm3] | Gabaryt X x Y x Z [mm] | Koszt [zl] | SHA-256 | Uwagi |")
    L.append("|---|---|---|---|---|---|---|---|")
    for w in dr:
        L.append("| %s | %s | %d | %s | %s x %s x %s | %s | %s | %s |" % (
            kod(w["plik"]), w["czesc"], w["szt"], pl(w["obj"]), pl(w["gab"][0], 1), pl(w["gab"][1], 1), pl(w["gab"][2], 1),
            zl(w["kmin"], w["kmax"]), kod(w["sha"]), w["uwagi"]))
    L.append("")
    L.append("Razem nowe pliki: %d pozycji, %d sztuk, %s cm3, %s zl (stawka %s-%s zl/cm3, czesci biale bez mnoznikow)." % (
        len(dr), sum(w["szt"] for w in dr), pl(obj_r58), zl(kmin_r58, kmax_r58), pl(rmin), pl(rmax)))
    L.append("")
    L.append("## B. Druk wlasny (PETG FDM, bez kosztu drukarni)")
    L.append("")
    L.append("| Plik STL | Czesc | Szt. | Obj. [cm3] | Gabaryt X x Y x Z [mm] | SHA-256 | Uwagi |")
    L.append("|---|---|---|---|---|---|---|")
    for w in wl:
        L.append("| %s | %s | %d | %s | %s x %s x %s | %s | %s |" % (
            kod(w["plik"]), w["czesc"], w["szt"], pl(w["obj"]), pl(w["gab"][0], 1), pl(w["gab"][1], 1), pl(w["gab"][2], 1),
            kod(w["sha"]), w["uwagi"]))
    L.append("")
    L.append("Male czesci druku wlasnego z pakietu R59 (tulejka DC, podkladki panelu) bez zmian.")
    L.append("")
    L.append("## C. Czesci ramki bez zmian - pliki z pakietu R59 (sumy w %s)" % kod("SHA256SUMS_2026-11-16_R59.txt"))
    L.append("")
    L.append("| Plik STL | Szt. | Obj. [cm3] | Gabaryt [mm] | Najtanszy [zl] | Pokazowy [zl] |")
    L.append("|---|---|---|---|---|---|")
    for w in bez:
        L.append("| %s | %d | %s | %s | %s | %s |" % (kod(w["plik"]), w["szt"], pl(w["obj"]), w["gab"], zl(w["nmin"], w["nmax"]), zl(w["pmin"], w["pmax"])))
    nmin, nmax = sum(w["nmin"] for w in bez), sum(w["nmax"] for w in bez)
    pmin, pmax = sum(w["pmin"] for w in bez), sum(w["pmax"] for w in bez)
    L.append("")
    L.append("## D. Pozycje pakietu R59, ktorych w wariancie okraglym NIE zamawiamy")
    L.append("")
    L.append("| Plik STL | Szt. | Powod |")
    L.append("|---|---|---|")
    for w in zast:
        powod = "zastapiona plytka okragla ramkowa o tym samym numerze" if "plytka" in w["plik"] else (
            "zastapiona przez " + kod("ramka_wkladka_okragla_v2.stl") if "wkladka" in w["plik"]
            else "zastapiona przez " + kod("ramka_pokrywka_okragla_v2.stl") + " (druk wlasny)")
        L.append("| %s | %d | %s |" % (kod(w["plik"]), w["szt"], powod))
    L.append("")
    L.append("Plytki okragle n8 i n9 (bez magnesow) zostaja plytkami testowymi tylko do skanera - zamowienie wedlug uznania; na ramce nie dzialaja "
             "(ramka odczyta 0 i 1).")
    L.append("")
    L.append("## Sumy - drukarnia")
    L.append("")
    L.append("| Zakres | Objetosc [cm3] | Najtanszy [zl] | Pokazowy [zl] |")
    L.append("|---|---|---|---|")
    L.append("| A. nowe pliki R58 (6 plytek + 3 wkladki) | %s | %s | %s |" % (pl(obj_r58), zl(kmin_r58, kmax_r58), zl(kmin_r58, kmax_r58)))
    L.append("| C. korpus W + korpus P + 2 blaty (R59) | %s | %s | %s |" % (pl(obj_bez), zl(nmin, nmax), zl(pmin, pmax)))
    L.append("| **Komplet okragly A + C** | **%s** | **%s** | **%s** |" % (
        pl(obj_r58 + obj_bez), zl(kmin_r58 + nmin, kmax_r58 + nmax), zl(kmin_r58 + pmin, kmax_r58 + pmax)))
    zmin, zmax = sum(w["nmin"] for w in zast), sum(w["nmax"] for w in zast)
    L.append("| dla porownania: pozycje D z drukarni (6 plytek kwadratowych + 3 wkladki) | %s | %s | %s |" % (pl(obj_zast), zl(zmin, zmax), zl(zmin, zmax)))
    L.append("")
    L.append("Wariant pokazowy: korpusy i blaty barwione na grafit i wygladzane (x %s x %s); czesci biale bez mnoznikow." % (pl(dye), pl(smooth)))
    L.append("")
    L.append("## Czego wymagac od drukarni i co sprawdzic przy odbiorze")
    L.append("")
    L.append("- Plytki: sciecia orientacyjnego, rowka na obwodzie i rowka od spodu nie wygladzac ani nie zalewac; orientacja druku gniazdami do gory.")
    L.append("- Plytka: 3 kieszenie od spodu - magnes 5 x 2 mm ma wejsc (kieszen 5,2 x 2,2); rowek klucza od spodu przy scieciu ma szerokosc 3,6.")
    L.append("- Wkladka: plytka wchodzi tylko scieciem do sciecia i opada na kolek (kolek 3,0 w rowku 3,6); luz na srednicy 0,8.")
    L.append("- Wkladka: 3 kieszenie czujnikow 5,0 x 5,5 i kanaly przewodow od spodu maja byc drozne (odpylone).")
    L.append("- Zamawiac wylacznie pliki o sumach SHA-256 z tabel A i B.")
    L.append("")
    cel = Path(a.cel)
    cel.mkdir(parents=True, exist_ok=True)
    (cel / (a.nazwa + ".md")).write_text("\n".join(L), encoding="ascii", newline="\n")
    with open(cel / (a.nazwa + ".csv"), "w", encoding="ascii", newline="") as f:
        wr = csv.writer(f, delimiter=";", lineterminator="\n")
        wr.writerow(["plik STL", "czesc", "ilosc", "material", "objetosc [cm3]", "gabaryt X x Y x Z [mm]", "koszt min [zl]", "koszt max [zl]", "SHA-256", "uwagi"])
        for w in wiersze:
            wr.writerow([w["plik"], w["czesc"], w["szt"], w["mat"].replace(chr(322), "l"), pl(w["obj"]),
                         "%s x %s x %s" % tuple(pl(g, 1) for g in w["gab"]),
                         pl(w["kmin"]) if w["drukarnia"] else "", pl(w["kmax"]) if w["drukarnia"] else "", w["sha"], w["uwagi"]])
    for w in wiersze:
        print("%-55s %2d szt. %6.2f cm3  plik: %s" % (w["plik"], w["szt"], w["obj"], w["dysk"]))
    print("drukarnia R58: %.2f cm3, %s zl; komplet okragly A + C: %.2f cm3, %s zl (pokazowy %s zl)" % (
        obj_r58, zl(kmin_r58, kmax_r58), obj_r58 + obj_bez, zl(kmin_r58 + nmin, kmax_r58 + nmax), zl(kmin_r58 + pmin, kmax_r58 + pmax)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
