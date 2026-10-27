"""Wiersz polecen generatora syntetycznych danych.

    python -m qc.syntetyka wzorce [--katalog tests/dane/wzorce]
    python -m qc.syntetyka plytka --uklad wieczorna --numer 2 --korony 6 --mosty 1 --ziarno 7 \
        --szum 0.02 --wyjscie <katalog>

Zapis do tests/dane jest odrzucany (kod 2), poza `wzorce --katalog tests/dane/wzorce`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

KORZEN = Path(__file__).resolve().parent.parent.parent
DANE_TESTOWE = KORZEN / "tests" / "dane"
KATALOG_WZORCOW = DANE_TESTOWE / "wzorce"


def _w_danych_testowych(sciezka: Path) -> bool:
    p = sciezka.resolve()
    return p == DANE_TESTOWE.resolve() or DANE_TESTOWE.resolve() in p.parents


def _wzorce(arg) -> int:
    from qc.syntetyka import prace

    katalog = Path(arg.katalog)
    if _w_danych_testowych(katalog) and katalog.resolve() != KATALOG_WZORCOW.resolve():
        print(f"odmowa zapisu do {katalog}: w tests/dane dozwolony tylko {KATALOG_WZORCOW}", file=sys.stderr)
        return 2
    katalog.mkdir(parents=True, exist_ok=True)
    # te same przepisy co prace.zapisz_dane_testowe (krok 0,8 / 1,0 tylko do regresji)
    wzorce = {
        "korona-wzorzec": prace.przepis(1, "trzonowiec", 0.8),
        "most-wzorzec": prace.przepis_mostu(1, 3, 1.0),
    }
    for nazwa, prz in wzorce.items():
        opis = {"przepis": prz, "uwaga": "gruby krok tylko do regresji"}
        (katalog / f"{nazwa}.json").write_text(json.dumps(opis, indent=1), encoding="utf-8")
        prace.z_przepisu(prz).export(katalog / f"{nazwa}.stl", file_type="stl")
        print(f"zapisano {katalog / nazwa}.json/.stl")
    return 0


def _plytka(arg) -> int:
    wyjscie = Path(arg.wyjscie)
    if _w_danych_testowych(wyjscie):
        print(f"odmowa zapisu do {wyjscie}: tests/dane tylko na wzorce", file=sys.stderr)
        return 2
    from qc import uklad as modul_ukladu
    from qc.syntetyka import plytka, prace
    from qc.ustawienia import wczytaj

    uklad = modul_ukladu.wczytaj(getattr(wczytaj().plytki, arg.uklad))
    pula = prace.pula_projektow(30, 1, krok_mm=arg.krok)
    if arg.mosty:
        pula += [prace.Projekt(id=f"most-{i + 1:02d}", rodzaj="most",
                               siatka=prace.most(arg.ziarno + i, 4 if i % 2 == 0 else 3, arg.krok))
                 for i in range(max(2, arg.mosty))]
    try:
        rozm = plytka.rozmiesc(uklad, pula, arg.korony, arg.mosty, arg.ziarno)
        siatka, pr = plytka.skan_plytki(uklad, arg.numer, rozm, arg.ziarno, szum_mm=arg.szum,
                                        T_plytki="losowa" if arg.losowa else None)
    except ValueError as e:
        print(f"blad: {e}", file=sys.stderr)
        return 2
    wyjscie.mkdir(parents=True, exist_ok=True)
    siatka.export(wyjscie / "skan.stl", file_type="stl")
    pr.do_json(wyjscie / "prawda.json")
    print(f"zapisano {wyjscie / 'skan.stl'} ({len(siatka.faces)} scian) i prawda.json")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m qc.syntetyka", description="Syntetyczne dane testowe qc")
    pod = parser.add_subparsers(dest="polecenie", required=True)

    w = pod.add_parser("wzorce", help="wzorce regresyjne (STL + JSON)")
    w.add_argument("--katalog", default=str(KATALOG_WZORCOW), help="katalog wyjsciowy wzorcow")

    p = pod.add_parser("plytka", help="syntetyczny skan plytki z pracami i prawda")
    p.add_argument("--uklad", choices=["wieczorna", "poranna"], required=True)
    p.add_argument("--numer", type=int, default=None, help="numer plytki 1-6 (brak = plik bazowy)")
    p.add_argument("--korony", type=int, default=6)
    p.add_argument("--mosty", type=int, default=0)
    p.add_argument("--ziarno", type=int, default=1)
    p.add_argument("--szum", type=float, default=0.02, help="szum skanera prac, mm")
    p.add_argument("--krok", type=float, default=0.1, help="krok siatki projektow, mm")
    p.add_argument("--losowa", action="store_true", help="losowe polozenie plytki w skanerze")
    p.add_argument("--wyjscie", required=True, help="katalog na skan.stl i prawda.json")

    arg = parser.parse_args(argv)
    return _wzorce(arg) if arg.polecenie == "wzorce" else _plytka(arg)


if __name__ == "__main__":
    sys.exit(main())
