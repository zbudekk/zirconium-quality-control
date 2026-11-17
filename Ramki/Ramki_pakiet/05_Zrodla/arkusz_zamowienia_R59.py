#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R59-D (14.11.2026): arkusz zamowienia dla pakietu R59 = arkusz z generatora (wyniki_v2/arkusze, 15 pozycji, K-57)
+ 2 plytki okragle n8 / n9 w nowym ukladzie gniazd (R59). Wzor: narzedzia/arkusz_zamowienia_R57.py.
Plikow w wyniki_v2/ nie zmienia - pisze tylko do katalogu docelowego.

Roznica wobec R57: objetosci i gabaryty plytek okraglych NIE sa wpisane w skrypcie. Sa czytane z tabeli
"2. Pliki wytworzone" raportu generatora (domyslnie wyniki_v2/raport/raport_wykonawcy_R59_iter2.md). Skrypt sprawdza:
  1. objetosc kazdego pliku z arkusza generatora = objetosc tego pliku w raporcie (arkusz i raport z jednego przebiegu),
  2. SHA-256 i objetosc 12 plikow plytek w raporcie = tabela w R59_wdrozenie_zmiany.md (pliki przyjete przez recenzje),
  3. SHA-256 plikow STL lezacych w wyniki_v2/stl = raport (w repo STL nie ma; brak pliku = pominiete z komunikatem).
Niezgodnosc = blad, pliki wynikowe nie powstaja.

Ilosci: plytki kwadratowe i reszta z arkusza generatora (parametry.json -> quantities, bez zmian - decyzja D6);
plytki okragle po 1 szt. jak w R57 (klucza quantities dla nich nie ma). Stawki z parametry.json.
Liczby gniazd w opisie licza sie z ev_rows / mo_rows w parametry.json.
Teksty z polskimi znakami sa zapisane sekwencjami unicode (ukosnik + u + 4 cyfry), zeby ten plik zostal w ASCII.

Uruchomienie (z folderu Ramki):
    python narzedzia/arkusz_zamowienia_R59.py <katalog_docelowy>
        [--nazwa arkusz_zamowienia]      nazwa plikow wynikowych bez rozszerzenia (.csv i .md)
        [--raport <plik.md>]             inny raport generatora
        [--porownaj <stary_arkusz.csv>]  wypisz roznice objetosci i sum wobec starszego arkusza (tylko na ekran)
Przyklady:
    do pakietu, jak w R57:  python narzedzia/arkusz_zamowienia_R59.py Ramki_pakiet/02_Druk_drukarnia_PA12
    wynik w repo (R59-D):   python narzedzia/arkusz_zamowienia_R59.py . --nazwa R59_arkusz_zamowienia
Potrzebny tylko Python 3 z biblioteka standardowa.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "wyniki_v2" / "arkusze"
STL = ROOT / "wyniki_v2" / "stl"
RAPORT = ROOT / "wyniki_v2" / "raport" / "raport_wykonawcy_R59_iter2.md"
WDROZENIE = ROOT / "R59_wdrozenie_zmiany.md"
P = json.loads((ROOT / "parametry.json").read_text(encoding="utf-8"))

X = "\u00d7"        # znak mnozenia
FI = "\u00f8"       # znak srednicy
MYSLNIK = "\u2013"  # polpauza w zakresach
PAUZA = "\u2014"
ILE_OKRAGLYCH = 1   # sztuk kazdej plytki okraglej (jak w R57; quantities ich nie zawiera)


def par(k):
    for sekcja in P.values():
        if isinstance(sekcja, dict) and k in sekcja:
            return sekcja[k]["value"]
    return P[k]["value"]


RMIN, RMAX = par("cost_rate_min"), par("cost_rate_max")


def pl(x, n=2):
    return f"{x:.{n}f}".replace(".", ",")


def g(x):
    return f"{x:g}".replace(".", ",")


def zl(x):
    return str(int(x + 0.5))


def num(s):
    return float(s.replace(",", "."))


def blad(tekst):
    sys.exit("BLAD: " + tekst)


def czytaj_raport(sciezka):
    """Tabela sekcji 2 raportu generatora -> {plik: (sha, [x, y, z], objetosc)}."""
    wz = re.compile(r"^\| `stl/([A-Za-z0-9_]+\.stl)` \| \d+ \| `([0-9a-f]{64})` \| ([^|]+) \| ([0-9.]+) \|")
    wynik = {}
    for linia in sciezka.read_text(encoding="utf-8").splitlines():
        m = wz.match(linia)
        if m:
            gab = [float(t) for t in m.group(3).split(X)]
            wynik[m.group(1)] = (m.group(2), gab, float(m.group(4)))
    return wynik


def czytaj_wdrozenie(sciezka):
    """Tabela SHA w R59_wdrozenie_zmiany.md -> {plik: (sha, objetosc)} dla plikow plytek."""
    wz = re.compile(r"^\| `(ramka_plytka_[a-z0-9_]+\.stl)`[^|]*\| ([0-9a-f]{64}) \| ([0-9,]+) \|")
    wynik = {}
    for linia in sciezka.read_text(encoding="utf-8").splitlines():
        m = wz.match(linia)
        if m:
            wynik[m.group(1)] = (m.group(2), num(m.group(3)))
    return wynik


def opis_ukladu(klucz):
    """Liczby gniazd z rzedow w parametry.json: (gniazd, rynienek, tekst do arkusza)."""
    okragle, rynienki = {}, []
    for rzad in par(klucz):
        if rzad["type"] == "trough":
            rynienki += [(rzad["l"], rzad["w"])] * len(rzad["x"])
        else:
            okragle[rzad["d"]] = okragle.get(rzad["d"], 0) + len(rzad["x"])
    n = sum(okragle.values())
    czesci = ", ".join(f"{ile} {X} {FI}{g(d)}" for d, ile in sorted(okragle.items()))
    ryn = " i ".join(f"{g(l)} {X} {g(w)}" for l, w in sorted(set(rynienki)))
    slowo = "rynienka" if len(rynienki) == 1 else "rynienki"
    gniazd = "gniazda" if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14) else "gniazd"
    return n, len(rynienki), f"{n} {gniazd} ({czesci}) + {len(rynienki)} {slowo} {ryn}"


def sumy_drukarni(wiersze):
    """Suma pozycji z materialem 'PA12 drukarnia...' (koszty w arkuszu = za cala ilosc)."""
    s = dict(n=0, szt=0, v=0.0, a=0.0, b=0.0, c=0.0, d=0.0)
    for f in wiersze:
        if len(f) < 13 or not f[4].startswith("PA12 drukarnia"):
            continue
        q = int(f[2])
        s["n"] += 1
        s["szt"] += q
        s["v"] += q * num(f[7])
        s["a"] += num(f[9])
        s["b"] += num(f[10])
        s["c"] += num(f[11])
        s["d"] += num(f[12])
    return s


def main():
    ap = argparse.ArgumentParser(description="Arkusz zamowienia R59: arkusz generatora + plytki okragle n8 / n9")
    ap.add_argument("katalog", nargs="?", default=".")
    ap.add_argument("--nazwa", default="arkusz_zamowienia")
    ap.add_argument("--raport", default=str(RAPORT))
    ap.add_argument("--porownaj", default="")
    args = ap.parse_args()
    dst = Path(args.katalog)
    raport_p = Path(args.raport)
    if dst.resolve() == SRC.resolve() and args.nazwa == "arkusz_zamowienia":
        blad("katalog docelowy to wyniki_v2/arkusze - nadpisalbym arkusz generatora; podaj inny katalog albo --nazwa")

    # --- zrodla: raport generatora, tabela wdrozenia, arkusz generatora
    rap = czytaj_raport(raport_p)
    if not rap:
        blad(f"w raporcie {raport_p.name} nie ma tabeli plikow STL")
    wdr = czytaj_wdrozenie(WDROZENIE)
    if len(wdr) != 12:
        blad(f"R59_wdrozenie_zmiany.md: oczekiwane 12 plikow plytek w tabeli SHA, jest {len(wdr)}")
    for plik, (sha, v) in sorted(wdr.items()):
        if plik not in rap:
            blad(f"{plik}: jest w R59_wdrozenie_zmiany.md, brak w raporcie {raport_p.name}")
        if rap[plik][0] != sha:
            blad(f"{plik}: SHA-256 w raporcie {rap[plik][0][:12]}... inne niz w R59_wdrozenie_zmiany.md {sha[:12]}...")
        if abs(rap[plik][2] - v) > 0.005:
            blad(f"{plik}: objetosc w raporcie {rap[plik][2]} inna niz w R59_wdrozenie_zmiany.md {v}")
    print(f"zrodlo objetosci: {raport_p.name}; SHA-256 i objetosc 12 z 12 plikow plytek = R59_wdrozenie_zmiany.md")

    sprawdzone, brak = 0, 0
    for plik, (sha, _gab, _v) in sorted(rap.items()):
        p = STL / plik
        if not p.exists():
            brak += 1
            continue
        if hashlib.sha256(p.read_bytes()).hexdigest() != sha:
            blad(f"{plik}: SHA-256 pliku w wyniki_v2/stl inne niz w raporcie {raport_p.name}")
        sprawdzone += 1
    print(f"pliki STL w wyniki_v2/stl: SHA-256 = raport {sprawdzone} z {sprawdzone}; brak pliku (pominiete) {brak}")

    raw = (SRC / "arkusz_zamowienia.csv").read_bytes().decode("utf-8-sig")
    lines = raw.split("\r\n")
    for k, l in enumerate(lines[1:], 2):
        f = l.split(";")
        if len(f) < 9:
            continue
        if f[0] not in rap:
            blad(f"arkusz generatora, wiersz {k}: {f[0]} nie wystepuje w raporcie {raport_p.name}")
        if abs(num(f[7]) - rap[f[0]][2]) > 0.005:
            blad(f"arkusz generatora, wiersz {k}: {f[0]} objetosc {f[7]} inna niz w raporcie {rap[f[0]][2]}")
    n_gen = sum(1 for l in lines[1:] if l.count(";") >= 8)
    print(f"arkusz generatora: objetosc {n_gen} z {n_gen} pozycji = raport")

    # --- plytki okragle: nazwy z numerow w parametry.json, objetosc i gabaryt z raportu
    numery = par("plate_numbers_round")
    ciecie = g(par("round_flat_w"))
    okragle = []
    for typ in ("wieczorna", "poranna"):
        for nr in numery[typ]:
            plik = f"ramka_plytka_okragla_{typ}_n{nr}_v2.stl"
            if plik not in rap:
                blad(f"{plik}: brak w raporcie {raport_p.name}")
            _sha, gab, v = rap[plik]
            czesc = f"p\u0142ytka okr\u0105g\u0142a {typ} n{nr}"
            okragle.append((plik, czesc, v, f" {X} ".join(pl(t, 1) for t in gab), typ))
    uwaga = (f"R59: uk\u0142ad gniazd jak p\u0142ytka kwadratowa tego typu, \u015bci\u0119cie orientacyjne "
             f"(ci\u0119ciwa {ciecie}) nie wyg\u0142adza\u0107, tylko do skanera {PAUZA} nie pasuje do wk\u0142adki ramki (R58)")
    if ";" in uwaga:
        blad("srednik w tekscie uwagi zepsulby CSV")

    # --- CSV (UTF-8 z BOM, CRLF, separator ;): pola opisowe plytek okraglych skopiowane z wiersza plytki n6
    i = max(k for k, l in enumerate(lines) if l.startswith("ramka_plytka_poranna_n6_v2.stl;"))
    wz = lines[i].split(";")
    nowe = []
    for plik, czesc, v, gab, _typ in okragle:
        a, b = round(v * ILE_OKRAGLYCH * RMIN, 2), round(v * ILE_OKRAGLYCH * RMAX, 2)
        nowe.append(";".join([plik, czesc, str(ILE_OKRAGLYCH)] + wz[3:7] + [pl(v), gab, pl(a), pl(b), pl(a), pl(b), uwaga]))
    przed = sumy_drukarni(l.split(";") for l in lines[1:])
    lines[i + 1:i + 1] = nowe
    po = sumy_drukarni(l.split(";") for l in lines[1:])

    def grupa(prefiks):
        return sumy_drukarni(l.split(";") for l in lines[1:] if l.startswith(prefiks))

    grupy = [
        ("p\u0142ytki wieczorne n1" + MYSLNIK + "n3 (kwadratowe)", grupa("ramka_plytka_wieczorna_n")),
        ("p\u0142ytki poranne n4" + MYSLNIK + "n6 (kwadratowe)", grupa("ramka_plytka_poranna_n")),
        ("p\u0142ytki okr\u0105g\u0142e n8 i n9", grupa("ramka_plytka_okragla_")),
    ]

    # --- MD
    md = (SRC / "arkusz_zamowienia.md").read_text(encoding="utf-8")
    m = re.search(r"^\| `ramka_plytka_poranna_n6_v2\.stl`.*$", md, re.M)
    if not m:
        blad("brak wiersza n6 w arkusz_zamowienia.md")
    kom = [c.strip() for c in m.group(0).strip().strip("|").split("|")]
    rows = []
    for plik, czesc, v, gab, _typ in okragle:
        a, b = zl(v * ILE_OKRAGLYCH * RMIN), zl(v * ILE_OKRAGLYCH * RMAX)
        rows.append(f"| `{plik}` | {czesc} | {ILE_OKRAGLYCH} | " + " | ".join(kom[3:7]) +
                    f" | {pl(v)} | {gab} | {a}{MYSLNIK}{b} | {a}{MYSLNIK}{b} | {uwaga} |")
    md = md[:m.end()] + "\n" + "\n".join(rows) + md[m.end():]

    stary = "15 pozycji: 10 do drukarni, 5 druku w\u0142asnego (bez p\u0142ytek bazowych, Z28)."
    if stary not in md:
        blad("arkusz_zamowienia.md: brak zdania o liczbie pozycji (zmienil sie tekst generatora?)")
    md = md.replace(stary, f"{n_gen + len(okragle)} pozycji: {po['n']} do drukarni (w tym {len(okragle)} p\u0142ytki "
                           f"okr\u0105g\u0142e n8 / n9 dopisane skryptem `narzedzia/arkusz_zamowienia_R59.py`; ich "
                           f"obj\u0119to\u015bci i gabaryty z raportu generatora `{raport_p.name}`), "
                           f"{n_gen - przed['n']} druku w\u0142asnego (bez p\u0142ytek bazowych, Z28).")
    if args.nazwa != "arkusz_zamowienia":
        # zdanie "Ten sam arkusz w ...csv" ma wskazywac plik zapisany obok
        md = md.replace("`arkusz_zamowienia.csv`", f"`{args.nazwa}.csv`", 1)
    m = re.search(r"^\| 10 pozycji \u00d7 ilo\u015bci \|.*$", md, re.M)
    if not m:
        blad("brak wiersza sum w arkusz_zamowienia.md")
    md = md[:m.end()] + (f"\n| {po['n']} pozycji {X} ilo\u015bci (z p\u0142ytkami okr\u0105g\u0142ymi n8, n9) | "
                         f"{pl(po['v'])} | {zl(po['a'])}{MYSLNIK}{zl(po['b'])} | "
                         f"{zl(po['c'])}{MYSLNIK}{zl(po['d'])} |") + md[m.end():]

    _nw, _rw, opis_w = opis_ukladu("ev_rows")
    _np, _rp, opis_p = opis_ukladu("mo_rows")
    sekcja = [
        "## P\u0142ytki w uk\u0142adzie R59 (dopisane skryptem `narzedzia/arkusz_zamowienia_R59.py`)",
        "",
        f"- Uk\u0142ad gniazd (z `parametry.json`, rz\u0119dy `ev_rows` / `mo_rows`): p\u0142ytka wieczorna {opis_w}; "
        f"p\u0142ytka poranna {opis_p}. P\u0142ytka okr\u0105g\u0142a ma te same gniazda co kwadratowa tego samego typu.",
        f"- P\u0142ytki okr\u0105g\u0142e n8 (wieczorna) i n9 (poranna): {FI}{g(par('plate_round_d'))} {X} 8 (8,6 z cyfr\u0105), po "
        f"{ILE_OKRAGLYCH} szt. jak w R57; obj\u0119to\u015bci z siatek wg raportu generatora `{raport_p.name}`; "
        f"bia\u0142e {PAUZA} bez mno\u017cnik\u00f3w; tylko do skanera (bez kieszeni magnes\u00f3w, nie pasuj\u0105 do wk\u0142adki ramki).",
        "- Ilo\u015bci bez zmian (decyzja w\u0142a\u015bciciela D6: \u201eokr\u0105g\u0142e raczej\u201d; co i ile zam\u00f3wi\u0107, "
        "rozstrzyga w\u0142a\u015bciciel po odbiorze). Wiersz sum \u201e10 pozycji\u201d = bez p\u0142ytek okr\u0105g\u0142ych.",
        "- Pliki p\u0142ytek z poprzedniego uk\u0142adu (R54 / R57) maj\u0105 te same nazwy i numery, ale inne sumy SHA\u2011256. "
        "Do zam\u00f3wienia tylko pliki o sumach z `R59_wdrozenie_zmiany.md`.",
        "",
        "| Grupa | Szt. | Obj\u0119to\u015b\u0107 [cm\u00b3] | Najta\u0144szy [z\u0142] | Pokazowy [z\u0142] |",
        "|---|---|---|---|---|",
    ]
    for nazwa, s in grupy:
        sekcja.append(f"| {nazwa} | {s['szt']} | {pl(s['v'])} | {zl(s['a'])}{MYSLNIK}{zl(s['b'])} | "
                      f"{zl(s['c'])}{MYSLNIK}{zl(s['d'])} |")
    kotwica = "\n## Uwaga dla CNC"
    if kotwica not in md:
        blad("arkusz_zamowienia.md: brak sekcji 'Uwaga dla CNC'")
    md = md.replace(kotwica, "\n" + "\n".join(sekcja) + "\n" + kotwica, 1)

    # --- zapis
    dst.mkdir(parents=True, exist_ok=True)
    (dst / (args.nazwa + ".csv")).write_bytes(("\ufeff" + "\r\n".join(lines)).encode("utf-8"))
    (dst / (args.nazwa + ".md")).write_text(md, encoding="utf-8", newline="\n")

    print(f"arkusz R59: {len(lines) - 1} wierszy CSV -> {args.nazwa}.csv, {args.nazwa}.md")
    for plik, _czesc, v, gab, typ in okragle:
        print(f"  okragla {typ}: {plik} {pl(v)} cm3, gabaryt {gab.replace(X, 'x')}, "
              f"{zl(v * RMIN)}-{zl(v * RMAX)} zl/szt.")
    for (_nazwa, s), etyk in zip(grupy, ("wieczorne n1-n3", "poranne n4-n6", "okragle n8 + n9")):
        print(f"  plytki {etyk}: {s['szt']} szt., {pl(s['v'])} cm3, {zl(s['a'])}-{zl(s['b'])} zl")
    for etyk, s in (("bez plytek okraglych", przed), ("z plytkami okraglymi", po)):
        print(f"  drukarnia {etyk}: {s['n']} pozycji, {s['szt']} szt., {pl(s['v'])} cm3, "
              f"najtanszy {zl(s['a'])}-{zl(s['b'])} zl, pokazowy {zl(s['c'])}-{zl(s['d'])} zl")

    # --- porownanie ze starszym arkuszem (tylko na ekran)
    if args.porownaj:
        stare = Path(args.porownaj).read_bytes().decode("utf-8-sig").split("\r\n")
        sw = {l.split(";")[0]: l.split(";") for l in stare[1:] if l.count(";") >= 8}
        print(f"porownanie z {Path(args.porownaj).name} (objetosc cm3: stara -> nowa):")
        for l in lines[1:]:
            f = l.split(";")
            if len(f) < 9:
                continue
            if f[0] not in sw:
                print(f"  {f[0]}: brak w starym arkuszu -> {f[7]}")
            elif sw[f[0]][7] != f[7]:
                print(f"  {f[0]}: {sw[f[0]][7]} -> {f[7]} ({num(f[7]) - num(sw[f[0]][7]):+.2f})")
        s0 = sumy_drukarni(sw.values())
        print(f"  drukarnia razem: {s0['n']} pozycji {pl(s0['v'])} cm3, najtanszy {zl(s0['a'])}-{zl(s0['b'])} zl, "
              f"pokazowy {zl(s0['c'])}-{zl(s0['d'])} zl -> {po['n']} pozycji {pl(po['v'])} cm3, "
              f"najtanszy {zl(po['a'])}-{zl(po['b'])} zl, pokazowy {zl(po['c'])}-{zl(po['d'])} zl")


if __name__ == "__main__":
    main()
