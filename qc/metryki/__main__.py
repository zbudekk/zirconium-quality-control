"""python -m qc.metryki [--szybko | --pelne] [--ziarno N] [--wyjscie plik.json] [--ustawienia plik.toml]

Jedna strona metryk (<= 60 linii) na stdout, opcjonalnie JSON; kod wyjscia 0 albo 3 (ponizej progu odbiorczego).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from qc.metryki import KLASY, PROGI_ODBIORCZE, ocen, policz
from qc.ustawienia import BladUstawien, wczytaj


def _tabela(naglowek: list[str], wiersze: list[list]) -> list[str]:
    tekst = [[str(x) for x in w] for w in [naglowek] + wiersze]
    szer = [max(len(w[i]) for w in tekst) for i in range(len(naglowek))]
    linie = ["  ".join(x.ljust(szer[0]) if i == 0 else x.rjust(szer[i]) for i, x in enumerate(w)) for w in tekst]
    return [linie[0], "-" * len(linie[0])] + linie[1:]


def _p(x: float) -> str:
    return f"{100 * x:.1f}%"


def strona(w: dict) -> list[str]:
    """Strona tekstowa z tabelami plytka / identyfikacja / ubytki / czasy."""
    kod, zle = ocen(w)
    pl, ub, cz = w["plytka"], w["ubytki"], w["czasy"]
    linie = [f"qc.metryki  wersja {w['wersja']}  tryb {w['tryb']}  ziarno {w['ziarno']}", ""]

    n = pl["numery"]
    linie.append(f"PLYTKA ({pl['plytki']} plytek)  wyrownanie: blad max {pl['blad_wyrownania_max_mm']:.4f} mm, "
                 f"sredni {pl['blad_wyrownania_sredni_mm']:.4f} mm")
    linie.append(f"numery: OK {n['ok']}  zle {n['zle']}  None {n['brak']};  gniazda zgodne "
                 f"{pl['gniazda_zgodne']}/{pl['gniazda']}")
    linie += _tabela(["fragmenty", "wynik", "prawda"],
                     [[s, v["wynik"], v["prawda"]] for s, v in pl["fragmenty"].items()])
    for b in pl["bledy"][:2]:
        linie.append(f"blad: {b}")
    linie.append("")

    linie.append("IDENTYFIKACJA")
    wiersze = []
    for t in ("wieczor", "rano", "razem"):
        x = w["identyfikacja"][t]
        wiersze.append([t, x["prace"], x["fragmenty"], _p(x["udzial_top1"]), _p(x["udzial_top2"]), x["pewny"],
                        x["dwuznaczny"], x["brak"], x["falszywe_pewny"], x["powtorzone"]])
    linie += _tabela(["tryb", "prace", "frag.", "top-1", "top-2", "pewny", "dwuzn.", "brak", "fals.pewny", "powt."],
                     wiersze)
    linie.append("mianownik top-1 = prace 'praca' z prawdy (brak fragmentu = 'brak') + fragmenty bez pracy; "
                 "powt. = kopie projektu")
    linie.append(f"fragmenty 'praca' bez pracy w prawdzie: {w['identyfikacja']['razem']['fragmenty_bez_prawdy']} "
                 "(nietrafione w top-1)")
    podw = w["identyfikacja"]["podwojne"]
    if podw["fragmenty"]:
        linie.append(f"podwojne: {podw['fragmenty']}, top-1 jedna z prac gniazda: {podw['top1_ktorakolwiek']}")
    linie.append("")

    linie.append(f"UBYTKI (inspekcja: {ub['sprawdzone_fragmenty']} prac wieczornych 'pewny', rano "
                 f"{ub['sprawdzone_rano']}; ukruszen bez inspekcji {ub['ubytki_bez_inspekcji']})")
    bez = ub["ubytki_bez_inspekcji_klasy"]
    wiersze = [[f"srednica {n}", ub["klasy"][n]["wykryte"], ub["klasy"][n]["pominiete"], ub["klasy"][n]["falszywe"],
                bez[n], _p(ub["klasy"][n]["udzial_wykrytych"])] for n, _, _ in KLASY]
    wiersze += [[f"sigma {s}", v["wykryte"], v["pominiete"], v["falszywe"], "-", _p(v["udzial_wykrytych"])]
                for s, v in ub["sigma"].items()]
    linie += _tabela(["klasa", "wykryte", "pominiete", "falszywe", "bez insp.", "% wykr."], wiersze)
    linie.append(f"wykryte (>= 0,3 mm), bez inspekcji = niewykryte: {_p(ub['udzial_wykrytych_od_0_3_wszystkie'])} "
                 f"(prog);  na pracach zidentyfikowanych: {_p(ub['udzial_wykrytych_od_0_3'])}")
    linie.append(f"prace z falszywym alarmem: {ub['prace_z_falszywym_alarmem']} "
                 f"({_p(ub['udzial_prac_z_falszywym_alarmem'])})")
    linie.append("")

    linie.append(f"CZASY: na plytke {cz['na_plytke_s']:.1f} s, na fragment {cz['na_fragment_s']:.2f} s, "
                 f"calosc {cz['calosc_s']:.0f} s")
    linie.append("")
    linie.append("PROGI ODBIORCZE (sekcja 14): top-1 >= {top1:.2f}, wykryte (>= 0,3 mm) >= {wykryte_od_0_3:.2f}, "
                 "prace z falszywym alarmem <= {prace_z_falszywym_alarmem:.2f}".format(**PROGI_ODBIORCZE))
    linie.append("WYNIK: " + ("ODBIOR ZALICZONY (kod 0)" if kod == 0 else
                              f"PONIZEJ PROGU: {', '.join(zle)} (kod {kod})"))
    return linie


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m qc.metryki", description="Metryki odbiorcze qc: jedna strona.")
    tryb = parser.add_mutually_exclusive_group()
    tryb.add_argument("--szybko", action="store_const", const="szybko", dest="tryb", help="3 plytki, ok. 20 ubytkow")
    tryb.add_argument("--pelne", action="store_const", const="pelne", dest="tryb", help="6 plytek (domyslnie)")
    parser.add_argument("--ziarno", type=int, default=1)
    parser.add_argument("--wyjscie", type=Path, help="plik JSON z tymi samymi polami")
    parser.add_argument("--ustawienia", type=Path, help="plik ustawien TOML")
    a = parser.parse_args(argv)
    try:
        u = wczytaj(a.ustawienia)
    except BladUstawien as e:
        print(f"blad ustawien: {e}", file=sys.stderr)
        return 2
    w = policz(u, a.tryb or "pelne", a.ziarno)
    print("\n".join(strona(w)))
    if a.wyjscie:
        a.wyjscie.parent.mkdir(parents=True, exist_ok=True)
        a.wyjscie.write_text(json.dumps(w, indent=1, ensure_ascii=True), encoding="utf-8")
    return ocen(w)[0]


if __name__ == "__main__":
    sys.exit(main())
