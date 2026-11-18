"""Raport metryk stanowiska z bazy programu: jedno polecenie = jedna strona (M1, plan etapu 3; E3-A10).

Uzycie (z katalogu stanowisko/):
    py -3.12 narzedzia/raport_metryk.py [--od RRRR-MM-DD] [--do RRRR-MM-DD] [--tryb wieczor|rano|oba]
                                        [--baza plik] [--ustawienia plik] [--json plik]

Okres = doby robocze od .. do (wlacznie; doba od [sesja] granica_doby_godz do tej samej godziny nastepnego dnia). Bez --do:
biezaca doba; bez --od: 7 dob konczacych sie na --do. Tryb: wieczor, rano albo oba (domyslnie). Baza: --baza albo
[sciezki] baza z ustawienia.toml; otwierana TYLKO DO ODCZYTU (raport niczego nie zmienia i nie migruje). Doba, zmiany
i prog pracy dwuznacznej: z ustawienia.toml (--ustawienia albo plik domyslny; samo --baza bez pliku ustawien = wartosci
domyslne 6:00, zmiany 6/14/22, prog 0,6).

Na stdout strona do 60 linii (same liczby - bez nazw folderow, plikow i osob); --json: te same pola w pliku JSON.
Kod wyjscia: 0 - kazda metryka z danymi w progu odbioru; 3 - co najmniej jedna ponizej progu; 2 - blad (argumenty,
ustawienia, baza). Definicje metryk: opisy_modulow/metryki.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from stanowisko import baza as B  # noqa: E402
from stanowisko import metryki as M  # noqa: E402
from stanowisko import ustawienia as UST  # noqa: E402


def _blad(tekst: str) -> int:
    print(f"raport metryk nieudany: {tekst}", file=sys.stderr)
    return M.KOD_BLAD


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--od", default=None, help="pierwsza doba okresu RRRR-MM-DD (domyslnie 6 dob przed --do)")
    ap.add_argument("--do", default=None, help="ostatnia doba okresu RRRR-MM-DD (domyslnie biezaca doba robocza)")
    ap.add_argument("--tryb", default=M.TRYB_OBA, help="wieczor, rano albo oba (domyslnie oba)")
    ap.add_argument("--baza", type=Path, default=None, help="plik bazy (domyslnie [sciezki] baza z ustawienia.toml)")
    ap.add_argument("--ustawienia", type=Path, default=None, help="plik ustawien (domyslnie ustawienia.toml w katalogu programu)")
    ap.add_argument("--json", type=Path, default=None, help="zapisz wynik (te same pola co strona) do pliku JSON")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:  # zly argument: argparse wypisal juz uzycie na stderr
        return M.KOD_BLAD if e.code else 0
    if a.tryb not in M.TRYBY:
        return _blad(f"tryb {a.tryb!r} - dozwolone: {', '.join(M.TRYBY)}")
    try:
        if a.ustawienia is not None or a.baza is None:
            ust = UST.wczytaj_ustawienia(a.ustawienia)
        else:
            try:
                ust = UST.wczytaj_ustawienia()
            except FileNotFoundError:
                ust = None  # samo --baza bez pliku ustawien: domyslna doba, zmiany i prog
    except (UST.BladUstawien, FileNotFoundError, KeyError, TypeError) as e:
        return _blad(f"ustawienia: {e}")
    parametry = M.parametry_z_ustawien(ust)
    do = a.do or M.biezaca_doba(parametry["granica_doby_godz"])
    try:
        od = a.od or (dt.date.fromisoformat(do) - dt.timedelta(days=M.OKRES_DOMYSLNY_DOB - 1)).isoformat()
        M.sprawdz_okres(od, do)
    except ValueError as e:
        return _blad(str(e) if "okres" in str(e) else f"okres: daty dob w postaci RRRR-MM-DD (jest od={a.od!r}, do={a.do!r})")
    sciezka = a.baza if a.baza is not None else B.sciezka_bazy(ust)
    try:
        with B.otworz(sciezka, tylko_odczyt=True) as baza:
            wynik = M.policz(baza, od, do, a.tryb, **parametry)
    except (B.BladBazy, ValueError) as e:
        return _blad(str(e))
    print("\n".join(M.strona(wynik)))
    if a.json is not None:
        try:
            a.json.parent.mkdir(parents=True, exist_ok=True)
            a.json.write_text(json.dumps(wynik, ensure_ascii=True, indent=1), encoding="utf-8")
        except OSError as e:
            return _blad(f"zapis JSON ({type(e).__name__}): {a.json}")
    return wynik["kod"]


if __name__ == "__main__":
    raise SystemExit(main())
