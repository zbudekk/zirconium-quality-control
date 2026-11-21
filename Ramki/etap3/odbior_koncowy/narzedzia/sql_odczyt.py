"""Zapytanie SELECT do bazy programu, tylko do odczytu - do liczenia liczb kryteriow (T2, T8, T11) "recznie".

Baza otwierana w trybie ``mode=ro``. Zapytania dotykajace tabel z nazwami folderow i plikow zlecen (``zlecenia``, ``projekty``,
``frezowania``, ``excel_zapisy`` - plan sekcja 3.4) sa odrzucane, chyba ze wynik to sama liczba (``SELECT count(...)``):
nazwy nie moga trafic do logu ani do dowodow.

Przyklad:
  PY -I sql_odczyt.py --baza <PC-katalog>\\t0\\k1\\dane\\stanowisko.sqlite "SELECT status, count(*) FROM skany GROUP BY status"
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

TABELE_Z_NAZWAMI = ("zlecenia", "projekty", "frezowania", "excel_zapisy")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SELECT do bazy programu (tylko odczyt, bez tabel z nazwami zlecen)")
    parser.add_argument("--baza", required=True, type=Path)
    parser.add_argument("zapytanie")
    args = parser.parse_args(argv)
    tekst = args.zapytanie.strip().rstrip(";")
    if not re.match(r"(?is)^\s*(select|with)\b", tekst) or ";" in tekst:
        print("BLAD: dozwolone jest jedno zapytanie SELECT")
        return 2
    sama_liczba = re.match(r"(?is)^\s*select\s+count\s*\([^)]*\)\s+from\b", tekst) is not None and " group by " not in tekst.lower()
    dotkniete = [t for t in TABELE_Z_NAZWAMI if re.search(rf"(?i)\b{t}\b", tekst)]
    # uwaga 21 recenzji: "SELECT count(*) FROM zlecenia UNION SELECT folder FROM zlecenia" wypisywalo nazwy - przy tabelach z
    # nazwami odrzucane jest kazde zlozenie zapytan i kazdy drugi SELECT (takze podzapytanie)
    zlozone = re.search(r"(?i)\b(union|intersect|except)\b", tekst) is not None or len(re.findall(r"(?i)\bselect\b", tekst)) > 1
    if dotkniete and (not sama_liczba or zlozone):
        print(f"BLAD: tabele z nazwami zlecen ({', '.join(dotkniete)}) - dozwolone tylko jedno SELECT count(...) bez GROUP BY, "
              "bez UNION / INTERSECT / EXCEPT i bez podzapytan")
        return 2
    if not args.baza.is_file():
        print("BLAD: nie ma pliku bazy")
        return 2
    baza = sqlite3.connect(f"file:{args.baza.as_posix()}?mode=ro", uri=True)
    try:
        kursor = baza.execute(tekst)
        print("\t".join(opis[0] for opis in kursor.description))
        wierszy = 0
        for wiersz in kursor:
            print("\t".join("" if pole is None else str(pole) for pole in wiersz))
            wierszy += 1
        print(f"-- wierszy: {wierszy}")
    except sqlite3.Error as e:
        print(f"BLAD: zapytanie odrzucone przez SQLite ({type(e).__name__}: {e})")
        return 2
    finally:
        baza.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
