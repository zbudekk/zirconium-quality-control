#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R57‑C (2.11.2026): arkusz zamówienia dla pakietu R57 = arkusz z generatora (wyniki_v2/arkusze, 15 pozycji, K‑57)
+ 2 płytki okrągłe n8 / n9 (drugi wariant do testu skanera). Plików w wyniki_v2/ nie zmienia — pisze tylko do katalogu docelowego.
Objętości i gabaryty z siatek (raport wykonawcy R57 iter2 §7.1, recenzja R57‑B iter1: 49,009 / 50,561 cm³), stawki z parametry.json.

Uruchomienie (z folderu Ramki):  py -3 narzedzia/arkusz_zamowienia_R57.py <katalog_docelowy>
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "wyniki_v2" / "arkusze"
P = json.loads((ROOT / "parametry.json").read_text(encoding="utf-8"))


def par(k):
    for sekcja in P.values():
        if isinstance(sekcja, dict) and k in sekcja:
            return sekcja[k]["value"]
    return P[k]["value"]


RMIN, RMAX = par("cost_rate_min"), par("cost_rate_max")
D = par("plate_round_d")

OKRAGLE = [  # plik, część, objętość z siatki [cm³]
    ("ramka_plytka_okragla_wieczorna_n8_v2.stl", "płytka okrągła wieczorna n8 (R57, test skanera)", 49.009),
    ("ramka_plytka_okragla_poranna_n9_v2.stl", "płytka okrągła poranna n9 (R57, test skanera)", 50.561),
]
UWAGA = "R57: drugi wariant do testu skanera, ścięcie orientacyjne (cięciwa 16) nie wygładzać, nie pasuje do wkładki ramki (R58)"


def pl(x, n=2):
    return f"{x:.{n}f}".replace(".", ",")


def zl(x):
    return str(int(x + 0.5))


def main(dst):
    dst = Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    gab = f"{pl(D, 1)} × {pl(D, 1)} × 8,6"

    # CSV (UTF‑8 z BOM, CRLF, separator ;)
    raw = (SRC / "arkusz_zamowienia.csv").read_bytes().decode("utf-8-sig")
    lines = raw.split("\r\n")
    i = max(k for k, l in enumerate(lines) if l.startswith("ramka_plytka_poranna_n6_v2.stl;"))
    nowe = []
    for plik, czesc, v in OKRAGLE:
        a, b = round(v * RMIN, 2), round(v * RMAX, 2)
        nowe.append(";".join([plik, czesc, "1", "MJF/SLS (D2)", "PA12 drukarnia", "biały (naturalny)",
                              "mat, bez wygładzania wierzchu", pl(v), gab, pl(a), pl(b), pl(a), pl(b), UWAGA]))
    lines[i + 1:i + 1] = nowe
    (dst / "arkusz_zamowienia.csv").write_bytes(("﻿" + "\r\n".join(lines)).encode("utf-8"))

    # sumy drukarni z CSV (objętość × ilość; koszty w CSV już za całą ilość)
    s = dict(v=0.0, a=0.0, b=0.0, c=0.0, d=0.0, n=0)
    for l in lines[1:]:
        f = l.split(";")
        if len(f) < 13 or not f[4].startswith("PA12 drukarnia"):
            continue
        q = int(f[2])
        num = lambda x: float(x.replace(",", "."))
        s["n"] += 1
        s["v"] += q * num(f[7])
        s["a"] += num(f[9]); s["b"] += num(f[10]); s["c"] += num(f[11]); s["d"] += num(f[12])  # koszty w arkuszu = za całą ilość

    # MD
    md = (SRC / "arkusz_zamowienia.md").read_text(encoding="utf-8")
    rows = []
    for plik, czesc, v in OKRAGLE:
        a, b = zl(v * RMIN), zl(v * RMAX)
        rows.append(f"| `{plik}` | {czesc} | 1 | MJF/SLS (D2) | PA12 drukarnia | biały (naturalny) | mat, bez wygładzania wierzchu | "
                    f"{pl(v)} | {gab} | {a}–{b} | {a}–{b} | {UWAGA} |")
    m = re.search(r"^\| `ramka_plytka_poranna_n6_v2\.stl`.*$", md, re.M)
    assert m, "brak wiersza n6 w arkusz_zamowienia.md"
    md = md[:m.end()] + "\n" + "\n".join(rows) + md[m.end():]
    stary = "15 pozycji: 10 do drukarni, 5 druku własnego (bez płytek bazowych, Z28)."
    assert stary in md
    md = md.replace(stary, "17 pozycji: 12 do drukarni (w tym 2 płytki okrągłe n8 / n9 dopisane w R57‑C skryptem "
                           "`narzedzia/arkusz_zamowienia_R57.py`), 5 druku własnego (bez płytek bazowych, Z28).")
    m = re.search(r"^\| 10 pozycji × ilości \|.*$", md, re.M)
    assert m, "brak wiersza sum"
    md = md[:m.start()] + (f"| {s['n']} pozycji × ilości (z płytkami okrągłymi n8, n9) | {pl(s['v'])} | "
                           f"{zl(s['a'])}–{zl(s['b'])} | {zl(s['c'])}–{zl(s['d'])} |") + md[m.end():]
    md = md.replace("- Płytki wieczorne n1–n3 liczone do drukarni (R55: bez alternatywy żywicznej).",
                    "- Płytki wieczorne n1–n3 liczone do drukarni (R55: bez alternatywy żywicznej).\n"
                    f"- R57: płytki okrągłe n8 (wieczorna) i n9 (poranna), ø{D} × 8 (8,6 z cyfrą), objętości z siatek "
                    "49,01 / 50,56 cm³ (raport wykonawcy R57 iter2 §7.1, recenzja R57‑B), białe — bez mnożników; "
                    "tylko do skanera (bez kieszeni magnesów, nie pasują do wkładki ramki).")
    (dst / "arkusz_zamowienia.md").write_text(md, encoding="utf-8", newline="\n")
    print(f"arkusz R57: {len(lines) - 1} wierszy CSV; drukarnia {s['n']} pozycji, {pl(s['v'])} cm³, "
          f"najtańszy {zl(s['a'])}–{zl(s['b'])} zł, pokazowy {zl(s['c'])}–{zl(s['d'])} zł")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
