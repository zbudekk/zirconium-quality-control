"""Import decyzji technika z okna testowego (``dane/decyzje.csv``, pisze je ``ui_test.py``) do bazy stanowiska.

Uzycie (z katalogu stanowisko/):
    py -3.12 narzedzia/import_decyzji.py [--plik dane/decyzje.csv] [--baza dane/stanowisko.sqlite] [--wymus]

Kazdy wiersz pliku staje sie jednym wierszem tabeli ``decyzje`` (``rodzaj`` = ukruszona / ok, ``czas`` z pliku,
``operator`` = "import"). Do wiersza powstaja potrzebne rekordy: jeden skan na nazwe pliku skanu i jedna praca na pare
(skan, gniazdo) z identyfikatorem projektu (``sha16``), statusem programu i liczba ubytkow z pliku. Skany z importu maja
status ``import``, ``wersja_programu`` = "import decyzje.csv" i pusty ``tryb`` - nie sa aktywne i nie naleza do zadnej doby,
wiec nie zmieniaja list ani stanu zlecen i nie przyjmuja decyzji. Plik zly w ktorymkolwiek wierszu nie jest importowany wcale.
Ponowny import tego samego pliku nic nie dopisuje; gdy okno dopisalo nowe wiersze na koncu, importowane sa tylko one.
Plik, ktory NIE jest przedluzeniem wczesniejszego importu (zmieniony wczesniejszy wiersz, inny plik), jest odrzucany -
tabela ``decyzje`` jest tylko do dopisywania i dubli nie da sie usunac; swiadomy import calego takiego pliku: ``--wymus``.

Na stdout same liczby (bez nazw plikow skanow). Plik decyzji nie jest zmieniany ani usuwany.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from stanowisko import baza as B  # noqa: E402

KOLUMNY = ("czas", "skan", "gniazdo", "projekt", "zeby", "decyzja", "status_programu", "ubytkow")  # = ui_test.KOLUMNY_DECYZJI
DECYZJE = ("ukruszona", "ok")
ZNACZNIK = "import decyzje.csv"  # skany.wersja_programu rekordow z importu
STATUS_IMPORT = "import"  # skany.status: skan z okna testowego, nieaktywny dla sesji
OPERATOR_IMPORT = "import"  # decyzje.operator (decyzja wlasciciela z 17.11.2026)


class BladImportu(ValueError):
    """Plik decyzji ma zly naglowek albo zly wiersz; komunikat z numerem wiersza pliku."""


def wczytaj(plik: Path) -> list[dict]:
    """Wiersze pliku po sprawdzeniu (czas ISO, gniazdo i liczba ubytkow jako liczby, decyzja z listy)."""
    plik = Path(plik)
    with open(plik, newline="", encoding="utf-8-sig") as f:
        surowe = list(csv.reader(f, delimiter=";"))
    if not surowe or tuple(surowe[0]) != KOLUMNY:
        raise BladImportu(f"{plik.name}: zly naglowek - oczekiwano {';'.join(KOLUMNY)}")
    wiersze = []
    for nr, w in enumerate(surowe[1:], start=2):
        if not w or all(not x.strip() for x in w):
            continue

        def blad(co: str) -> BladImportu:
            return BladImportu(f"{plik.name}: wiersz {nr}: {co}")

        if len(w) != len(KOLUMNY):
            raise blad(f"{len(w)} kolumn zamiast {len(KOLUMNY)}")
        d = dict(zip(KOLUMNY, (x.strip() for x in w)))
        try:
            d["czas"] = dt.datetime.fromisoformat(d["czas"]).replace(microsecond=0).isoformat()
        except ValueError:
            raise blad(f"czas {d['czas']!r} nie jest data w formacie ISO") from None
        if not d["skan"]:
            raise blad("brak nazwy pliku skanu")
        for pole in ("gniazdo", "ubytkow"):
            try:
                d[pole] = int(d[pole] or 0) if pole == "ubytkow" else int(d[pole])
            except ValueError:
                raise blad(f"{pole} {d[pole]!r} nie jest liczba") from None
        if d["decyzja"] not in DECYZJE:
            raise blad(f"decyzja {d['decyzja']!r} (dozwolone: {', '.join(DECYZJE)})")
        d["surowy"] = ";".join(x.strip() for x in w)
        wiersze.append(d)
    return wiersze


def _skrot(wiersze: list[dict], n: int) -> str:
    return hashlib.sha256("\n".join(w["surowy"] for w in wiersze[:n]).encode("utf-8")).hexdigest()[:16]


def importuj(baza: B.Baza, plik: Path, wymus: bool = False) -> dict:
    """Importuje plik decyzji; zwraca liczniki: wiersze pliku, dopisane decyzje, nowe skany i prace, wiersze pominiete (zaimportowane wczesniej).

    Gdy w bazie jest juz import, a plik nie zaczyna sie od zadnego z wczesniej zaimportowanych - ``BladImportu``
    (chyba ze ``wymus``: wtedy caly plik jest dopisywany).
    """
    wiersze = wczytaj(plik)
    pominiete = 0
    wczesniejsze = baza.wiersze("SELECT dane FROM zdarzenia WHERE typ = 'import_decyzji'")
    for z in wczesniejsze:
        wczesniej = json.loads(z["dane"])
        n = int(wczesniej.get("wiersze", 0))
        if pominiete < n <= len(wiersze) and wczesniej.get("skrot") == _skrot(wiersze, n):
            pominiete = n  # poczatek pliku jest juz w bazie
    if wczesniejsze and pominiete == 0 and wiersze and not wymus:
        raise BladImportu(f"{Path(plik).name}: plik nie jest przedluzeniem wczesniejszego importu (w bazie sa juz decyzje z {len(wczesniejsze)} "
                          f"importu / importow) - dopisanie zdublowaloby decyzje, ktorych nie da sie usunac; swiadomy import calosci: --wymus")
    wynik = {"wiersze": len(wiersze), "decyzje": 0, "skany": 0, "prace": 0, "pominiete": pominiete}
    nowe = wiersze[pominiete:]
    if not nowe:
        return wynik
    with baza.transakcja():
        for w in nowe:
            skan = baza.wiersz("SELECT id FROM skany WHERE plik = ? AND wersja_programu = ?", (w["skan"], ZNACZNIK))
            if skan is None:
                skan_id = baza.wstaw("skany", plik=w["skan"], czas_analizy=w["czas"], status=STATUS_IMPORT, wersja_programu=ZNACZNIK)
                wynik["skany"] += 1
            else:
                skan_id = skan["id"]
            praca = baza.wiersz("SELECT id FROM prace WHERE skan_id = ? AND gniazdo = ? AND nr_fragmentu = 1", (skan_id, w["gniazdo"]))
            if praca is None:
                projekty = baza.wiersze("SELECT id FROM projekty WHERE sha16 = ? AND usuniety = 0 LIMIT 2", (w["projekt"],)) if w["projekt"] else []
                praca_id = baza.wstaw("prace", skan_id=skan_id, gniazdo=w["gniazdo"], nr_fragmentu=1, status_gniazda=w["status_programu"] or None,
                                      kandydat1_sha16=w["projekt"] or None, ubytki=w["ubytkow"],
                                      projekt_id=projekty[0]["id"] if len(projekty) == 1 else None)
                wynik["prace"] += 1
            else:
                praca_id = praca["id"]
            baza.wstaw("decyzje", praca_id=praca_id, rodzaj=w["decyzja"], operator=OPERATOR_IMPORT, czas=w["czas"])
            wynik["decyzje"] += 1
        baza.zdarzenie("system", "import_decyzji", {"wiersze": len(wiersze), "nowe": len(nowe), "skrot": _skrot(wiersze, len(wiersze))})
    return wynik


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--plik", type=Path, default=None, help="plik decyzji okna testowego (domyslnie dane/decyzje.csv w katalogu programu)")
    ap.add_argument("--baza", type=Path, default=None, help="plik bazy (domyslnie [sciezki] baza z ustawienia.toml)")
    ap.add_argument("--wymus", action="store_true", help="importuj caly plik, choc nie jest przedluzeniem wczesniejszego importu (dubluje decyzje)")
    a = ap.parse_args(argv)
    from stanowisko import ustawienia as UST

    plik = a.plik if a.plik is not None else UST.KORZEN / "dane" / "decyzje.csv"
    if not plik.exists():
        print(f"brak pliku decyzji: {plik}", file=sys.stderr)
        return 2
    try:
        sciezka = a.baza if a.baza is not None else B.sciezka_bazy(UST.wczytaj_ustawienia())
        with B.otworz(sciezka) as baza:
            r = importuj(baza, plik, wymus=a.wymus)
    except (BladImportu, B.BladBazy, UST.BladUstawien, FileNotFoundError) as e:
        print(f"import nieudany, niczego nie dopisano: {e}", file=sys.stderr)
        return 1
    print(f"{plik.name}: {r['wiersze']} wierszy w pliku, zaimportowano {r['decyzje']} decyzji ({r['skany']} nowych skanow, {r['prace']} nowych prac), "
          f"pominieto {r['pominiete']} wierszy zaimportowanych wczesniej; baza: {sciezka}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
