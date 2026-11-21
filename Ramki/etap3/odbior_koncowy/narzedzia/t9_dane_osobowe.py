"""T9 - dane osobowe: szukanie nazw folderow zlecen (i nazw plikow projektow) w repo, logach, wynikach i zapisie ruchu.

ZASADA: lista nazw istnieje tylko w pamieci tego procesu. Skrypt NIGDY nie wypisuje nazwy ani fragmentu pliku z
trafieniem - tylko liczby trafien i ``sha16`` nazwy (pierwsze 16 znakow SHA-256 nazwy w UTF-8, jak w programie).
Sciezka pliku, ktora sama zawiera szukana nazwe, jest wypisywana jako ``<sciezka sha16=...>``.

Skad nazwy (mozna laczyc):
  --nazwy-z KATALOG   nazwy podfolderow KATALOGU (folder "Cyrkon" / "Prywatne" / pula testowa) i nazwy plikow STL w nich;
  --baza PLIK         tabele ``zlecenia.folder`` i ``projekty.plik`` bazy programu (otwierana tylko do odczytu).

Gdzie szukac (mozna laczyc):
  --repo KATALOG      pliki sledzone przez git (tresc i sciezki) oraz opisy commitow ``--od..HEAD``;
  --cel SCIEZKA       plik albo katalog (rekurencyjnie): logi, pliki wynikow, zapis ruchu do ramki;
  --dozwolone WZOR    fragment sciezki, w ktorym nazwy WOLNO trzymac (np. stanowisko.sqlite, log_excel.csv) - trafienia
                      tam sa liczone osobno i nie psuja wyniku.

Szukane sa: cala nazwa (kryterium T9) oraz czlony nazwy (slowa z litera, co najmniej ``--min-czlon`` znakow) - trafienia
czlonow sa liczone osobno "do wyjasnienia" (czlon moze byc zwyklym slowem). Kodowania: UTF-8, UTF-16 LE, cp1250; bez
rozrozniania wielkosci liter ASCII. Pliki spakowane (zip, npz) nie sa rozpakowywane - liczone jako "nieprzeszukane".

Kod wyjscia: 0 = 0 trafien calych nazw poza miejscami dozwolonymi, 1 = sa trafienia, 2 = blad wywolania / brak nazw.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

SPAKOWANE = {".zip", ".npz", ".7z", ".whl", ".gz", ".xlsx", ".xlsm", ".docx", ".pdf", ".png", ".jpg"}
MAKS_MB = 300


def sha16(tekst: str) -> str:
    return hashlib.sha256(tekst.encode("utf-8")).hexdigest()[:16]


def nazwy_z_katalogu(katalog: Path) -> set[str]:
    nazwy = set()
    for pozycja in katalog.iterdir():
        if pozycja.is_dir():
            nazwy.add(pozycja.name)
            for plik in pozycja.rglob("*"):
                if plik.is_file() and plik.suffix.lower() == ".stl":
                    nazwy.add(plik.stem)
    return nazwy


def nazwy_z_bazy(plik: Path) -> set[str]:
    nazwy = set()
    baza = sqlite3.connect(f"file:{plik.as_posix()}?mode=ro", uri=True)
    try:
        for zapytanie in ("SELECT folder FROM zlecenia", "SELECT plik FROM projekty"):
            try:
                for (wartosc,) in baza.execute(zapytanie):
                    if wartosc:
                        nazwy.add(Path(str(wartosc)).stem if zapytanie.endswith("projekty") else str(wartosc))
            except sqlite3.Error:
                pass
    finally:
        baza.close()
    return nazwy


def czlony(nazwa: str, min_znakow: int) -> set[str]:
    return {c for c in re.split(r"[\s_\-.,;()\[\]]+", nazwa) if len(c) >= min_znakow and re.search(r"[^\W\d_]", c)}


def wzorzec(teksty: set[str]) -> tuple[re.Pattern[bytes] | None, dict[bytes, str]]:
    """Jeden wzorzec bajtowy dla wszystkich tekstow w 3 kodowaniach; slownik bajty (male litery) -> tekst."""
    slownik: dict[bytes, str] = {}
    for tekst in teksty:
        for kodowanie in ("utf-8", "utf-16-le", "cp1250"):
            try:
                slownik.setdefault(tekst.lower().encode(kodowanie), tekst)
            except UnicodeEncodeError:
                pass
    if not slownik:
        return None, slownik
    czesci = sorted(slownik, key=len, reverse=True)
    return re.compile(b"|".join(re.escape(c) for c in czesci)), slownik


def szukaj(dane: bytes, wz: re.Pattern[bytes] | None, slownik: dict[bytes, str]) -> dict[str, int]:
    trafienia: dict[str, int] = {}
    if wz is None:
        return trafienia
    for dopasowanie in wz.finditer(dane.lower()):
        tekst = slownik[dopasowanie.group(0)]
        trafienia[tekst] = trafienia.get(tekst, 0) + 1
    return trafienia


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="T9: liczba trafien nazw folderow zlecen (wypisuje tylko liczby i sha16)")
    parser.add_argument("--nazwy-z", type=Path, action="append", default=[], metavar="KATALOG")
    parser.add_argument("--baza", type=Path, action="append", default=[], metavar="PLIK")
    parser.add_argument("--repo", type=Path, action="append", default=[], metavar="KATALOG")
    parser.add_argument("--od", default="2537f6f", help="opisy commitow od tego commita (domyslnie poczatek etapu 3)")
    parser.add_argument("--cel", type=Path, action="append", default=[], metavar="SCIEZKA")
    parser.add_argument("--dozwolone", action="append", default=[], metavar="WZOR")
    parser.add_argument("--min-nazwa", type=int, default=4, help="najkrotsza szukana cala nazwa (krotsze sa liczone jako pominiete)")
    parser.add_argument("--min-czlon", type=int, default=5, help="najkrotszy szukany czlon nazwy; 0 = bez czlonow")
    parser.add_argument("--json", type=Path, default=None, help="zapisz wynik (liczby i sha16, bez nazw) do pliku JSON")
    args = parser.parse_args(argv)

    nazwy: set[str] = set()
    for katalog in args.nazwy_z:
        nazwy |= nazwy_z_katalogu(katalog)
    for plik in args.baza:
        nazwy |= nazwy_z_bazy(plik)
    krotkie = {n for n in nazwy if len(n) < args.min_nazwa}
    nazwy -= krotkie
    if not nazwy:
        print("BLAD: brak nazw do szukania (podaj --nazwy-z albo --baza)")
        return 2
    slowa: set[str] = set()
    if args.min_czlon:
        for nazwa in nazwy:
            slowa |= czlony(nazwa, args.min_czlon)
        slowa -= nazwy
    wz_nazw, slownik_nazw = wzorzec(nazwy)
    wz_slow, slownik_slow = wzorzec(slowa)

    def ukryj(sciezka: str) -> str:
        return f"<sciezka sha16={sha16(sciezka)}>" if szukaj(sciezka.encode("utf-8"), wz_nazw, slownik_nazw) else sciezka

    pliki: list[tuple[str, Path | None, bytes | None]] = []  # (opis, plik, dane gotowe)
    for repo in args.repo:
        lista = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"], capture_output=True, check=True).stdout.split(b"\0")
        for surowa in lista:
            if surowa:
                wzgledna = surowa.decode("utf-8", "replace")
                pliki.append((f"repo:{wzgledna}", repo / wzgledna, None))
        opisy = subprocess.run(["git", "-C", str(repo), "log", "--format=%B%n%an", f"{args.od}..HEAD"], capture_output=True, check=True).stdout
        pliki.append((f"repo:<opisy commitow {args.od}..HEAD>", None, opisy))
        pliki.append(("repo:<lista sciezek sledzonych>", None, b"\n".join(lista)))
    for cel in args.cel:
        if cel.is_dir():
            for plik in sorted(cel.rglob("*")):
                if plik.is_file():
                    pliki.append((str(plik), plik, None))
        elif cel.is_file():
            pliki.append((str(cel), cel, None))
        else:
            print(f"BLAD: nie ma celu {ukryj(str(cel))}")
            return 2

    wynik = {"nazw": len(nazwy), "nazw_pominietych_krotkich": len(krotkie), "czlonow": len(slowa), "plikow": 0, "nieprzeszukane": [],
             "trafienia": [], "trafienia_dozwolone": [], "czlony_do_wyjasnienia": []}
    for opis, plik, dane in pliki:
        dozwolony = any(wzor.lower() in opis.lower().replace("\\", "/") for wzor in (w.replace("\\", "/") for w in args.dozwolone))
        if dane is None:
            assert plik is not None
            if plik.suffix.lower() in SPAKOWANE or not plik.exists() or plik.stat().st_size > MAKS_MB * 1024 * 1024:
                wynik["nieprzeszukane"].append(ukryj(opis))
                sciezkowe = szukaj(opis.encode("utf-8"), wz_nazw, slownik_nazw)
                if sciezkowe and not dozwolony:
                    wynik["trafienia"].append({"gdzie": ukryj(opis), "w_sciezce": True, "nazwy": {sha16(n): k for n, k in sciezkowe.items()}})
                continue
            dane = plik.read_bytes()
        wynik["plikow"] += 1
        calosc = dane + b"\n" + opis.encode("utf-8")
        trafione = szukaj(calosc, wz_nazw, slownik_nazw)
        if trafione:
            wpis = {"gdzie": ukryj(opis), "nazwy": {sha16(n): k for n, k in sorted(trafione.items(), key=lambda p: sha16(p[0]))}}
            wynik["trafienia_dozwolone" if dozwolony else "trafienia"].append(wpis)
        elif not dozwolony:
            slowne = szukaj(calosc, wz_slow, slownik_slow)
            if slowne:
                wynik["czlony_do_wyjasnienia"].append({"gdzie": ukryj(opis), "czlony": {sha16(n): k for n, k in sorted(slowne.items(), key=lambda p: sha16(p[0]))}})

    def suma(lista: list[dict], pole: str) -> int:
        return sum(sum(wpis[pole].values()) for wpis in lista)

    print(f"T9 dane osobowe: szukanych nazw {wynik['nazw']} (pominietych krotszych niz {args.min_nazwa} znaki: {wynik['nazw_pominietych_krotkich']}), "
          f"czlonow {wynik['czlonow']}; przeszukanych plikow {wynik['plikow']}, nieprzeszukanych (spakowane / za duze) {len(wynik['nieprzeszukane'])}")
    print(f"TRAFIENIA calych nazw poza miejscami dozwolonymi: {suma(wynik['trafienia'], 'nazwy')} w {len(wynik['trafienia'])} plikach")
    for wpis in wynik["trafienia"][:40]:
        print(f"  {wpis['gdzie']}: " + ", ".join(f"{skrot} x{ile}" for skrot, ile in wpis["nazwy"].items()))
    print(f"Trafienia w miejscach dozwolonych: {suma(wynik['trafienia_dozwolone'], 'nazwy')} w {len(wynik['trafienia_dozwolone'])} plikach")
    print(f"Czlony nazw do wyjasnienia (bez calej nazwy): {suma(wynik['czlony_do_wyjasnienia'], 'czlony')} w {len(wynik['czlony_do_wyjasnienia'])} plikach")
    for wpis in wynik["czlony_do_wyjasnienia"][:40]:
        print(f"  {wpis['gdzie']}: " + ", ".join(f"{skrot} x{ile}" for skrot, ile in wpis["czlony"].items()))
    if args.json:
        args.json.write_text(json.dumps(wynik, ensure_ascii=True, indent=1) + "\n", encoding="ascii", newline="\n")
    zaliczony = not wynik["trafienia"]
    print("WYNIK T9 (cale nazwy):", "ZAL (0 trafien)" if zaliczony else "FAIL")
    return 0 if zaliczony else 1


if __name__ == "__main__":
    sys.exit(main())
