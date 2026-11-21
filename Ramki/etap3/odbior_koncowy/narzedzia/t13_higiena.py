"""T13 - higiena repozytorium: pliki zmienione od poczatku etapu 3 z kontrola.

Tylko odczyt repozytorium (polecenia ``git diff`` i ``git cat-file``); niczego nie zmienia.

Kontrole:
  1. sciezka: kazdy zmieniony plik musi pasowac do przedrostka z pliku listy (``t13_dozwolone.txt``);
     grupa ``E3`` = paczki etapu 3, inne grupy = prace spoza etapu 3 (liczone osobno), brak dopasowania = NARUSZENIE;
  2. nowe pliki tekstowe grupy E3: same bajty ASCII;
  3. konce linii nowych plikow tekstowych grupy E3: LF, a w ``.cmd`` / ``.bat`` / ``.ps1`` CRLF;
  4. brak STL (poza ``modele_plytek/``), brak plikow danych (rozszerzenia z ``DANE``) i plikow wiekszych niz ``--maks-kb``.

Odstepstwo O11 (decyzja koordynatora 20.11 nr 5): pliki z listy ``t13_wyjatki_ascii.txt`` (napisy ekranu po polsku ze znakami
diakrytycznymi - styl programu przyjety przez wlasciciela w paczkach A3 / A6) nie sa naruszeniem kontroli 2; sa wypisywane
OSOBNO ("nie-ASCII: napisy ekranu, odstepstwo O11") z liczba wierszy i bajtow nie-ASCII w kazdym. Kazdy INNY nowy plik ze
znakiem spoza ASCII jest nadal naruszeniem; pozostale kontrole (konce linii, dane, rozmiar) obejmuja takze pliki z listy.

Wynik: tabela licznikow i lista naruszen (sciezka + powod). Kod wyjscia 0 = brak naruszen w grupie E3 i brak plikow
poza listami, 1 = sa naruszenia, 2 = blad wywolania.

Przyklad:
  python t13_higiena.py --repo <PC-katalog>\\qc --od 2537f6f --do main --json C:\\...\\T13\\t13_wynik.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

POCZATEK_ETAPU_3 = "2537f6f"  # pierwszy commit pliku Ramki/plan_etap3_pelna_aplikacja_2026-11-16.md (16.11.2026 00:05)
CRLF = {".cmd", ".bat", ".ps1"}
DANE = {".stl", ".ply", ".obj", ".npz", ".npy", ".sqlite", ".db", ".zip", ".7z", ".whl", ".blend", ".xlsx", ".xlsm", ".csv"}
BINARNE_ZNANE = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico"}


def git(repo: Path, *argumenty: str, wejscie: bytes | None = None) -> bytes:
    wynik = subprocess.run(["git", "-C", str(repo), *argumenty], input=wejscie, capture_output=True)
    if wynik.returncode != 0:
        raise SystemExit(f"BLAD git {' '.join(argumenty[:3])}: {wynik.stderr.decode('utf-8', 'replace').strip()}")
    return wynik.stdout


def wczytaj_liste(plik: Path) -> list[tuple[str, str]]:
    lista = []
    for wiersz in plik.read_text(encoding="utf-8").splitlines():
        wiersz = wiersz.split("#", 1)[0].rstrip()
        if not wiersz.strip():
            continue
        grupa, _, przedrostek = wiersz.partition(" ")
        lista.append((przedrostek.strip(), grupa.strip()))
    return sorted(lista, key=lambda para: -len(para[0]))  # najdluzszy przedrostek wygrywa


def grupa_sciezki(sciezka: str, lista: list[tuple[str, str]]) -> str | None:
    for przedrostek, grupa in lista:
        if sciezka.startswith(przedrostek):
            return grupa
    return None


def zmienione(repo: Path, od: str, do: str) -> list[tuple[str, str]]:
    surowe = git(repo, "diff", "--name-status", "--no-renames", "-z", od, do).split(b"\0")
    pary = []
    for i in range(0, len(surowe) - 1, 2):
        pary.append((surowe[i].decode("ascii"), surowe[i + 1].decode("utf-8", "replace")))
    return pary


def tresci(repo: Path, do: str, sciezki: list[str]) -> dict[str, bytes]:
    """Tresc plikow z commita ``do`` jednym procesem ``git cat-file --batch``."""
    if not sciezki:
        return {}
    wejscie = "".join(f"{do}:{s}\n" for s in sciezki).encode("utf-8")
    dane = git(repo, "cat-file", "--batch", wejscie=wejscie)
    wynik, pozycja = {}, 0
    for sciezka in sciezki:
        koniec = dane.index(b"\n", pozycja)
        naglowek = dane[pozycja:koniec].split()
        pozycja = koniec + 1
        if naglowek[-1] == b"missing":
            wynik[sciezka] = b""
            continue
        rozmiar = int(naglowek[2])
        wynik[sciezka] = dane[pozycja:pozycja + rozmiar]
        pozycja += rozmiar + 1
    return wynik


def wczytaj_wyjatki(plik: Path | None) -> set[str]:
    """Sciezki plikow z napisami ekranu (odstepstwo O11); brak pliku listy = brak wyjatkow."""
    if plik is None or not plik.is_file():
        return set()
    return {w.split("#", 1)[0].strip() for w in plik.read_text(encoding="utf-8").splitlines() if w.split("#", 1)[0].strip()}


def wiersze_nie_ascii(tresc: bytes) -> int:
    return sum(1 for wiersz in tresc.split(b"\n") if any(bajt > 127 for bajt in wiersz))


def ocen_nowy(sciezka: str, tresc: bytes, maks_kb: int) -> list[str]:
    powody = []
    rozszerzenie = Path(sciezka).suffix.lower()
    if rozszerzenie == ".stl" and "/modele_plytek/" not in sciezka:
        powody.append("STL poza modele_plytek")
    elif rozszerzenie in DANE and rozszerzenie != ".stl":
        powody.append(f"plik danych ({rozszerzenie})")
    if len(tresc) > maks_kb * 1024:
        powody.append(f"duzy plik ({len(tresc) // 1024} KB > {maks_kb} KB)")
    if rozszerzenie in BINARNE_ZNANE or rozszerzenie in DANE:  # pliki danych ocenia regula wyzej (STL, plik danych)
        return powody
    if b"\0" in tresc[:8000]:  # uwaga 22 recenzji: plik tekstowy UTF-16 (bajty NUL) nie moze przejsc jako "binarny"
        powody.append(f"bajty NUL w pliku {rozszerzenie or 'bez rozszerzenia'} spoza listy binarnych (np. tekst UTF-16)")
        return powody
    nie_ascii = sum(1 for bajt in tresc if bajt > 127)
    if nie_ascii:
        powody.append(f"nie ASCII ({nie_ascii} bajtow)")
    crlf = tresc.count(b"\r\n")
    lf = tresc.count(b"\n") - crlf
    samotne_cr = tresc.count(b"\r") - crlf
    if samotne_cr:
        powody.append(f"konce linii: {samotne_cr} x samotne CR")
    if rozszerzenie in CRLF:
        if lf:
            powody.append(f"konce linii: {lf} x LF w pliku {rozszerzenie} (ma byc CRLF)")
    elif crlf:
        powody.append(f"konce linii: {crlf} x CRLF (ma byc LF)")
    return powody


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="T13: pliki zmienione od poczatku etapu 3 z kontrola sciezek, ASCII, koncow linii i danych")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="katalog repozytorium (domyslnie biezacy)")
    parser.add_argument("--od", default=POCZATEK_ETAPU_3, help=f"commit poczatku etapu (domyslnie {POCZATEK_ETAPU_3})")
    parser.add_argument("--do", default="main", help="commit koncowy (domyslnie main)")
    parser.add_argument("--dozwolone", type=Path, default=Path(__file__).with_name("t13_dozwolone.txt"), help="plik listy przedrostkow sciezek")
    parser.add_argument("--wyjatki-ascii", type=Path, default=Path(__file__).with_name("t13_wyjatki_ascii.txt"),
                        help="plik listy sciezek z napisami ekranu (odstepstwo O11: nie-ASCII raportowane osobno)")
    parser.add_argument("--maks-kb", type=int, default=1024, help="prog duzego pliku w KB (domyslnie 1024)")
    parser.add_argument("--json", type=Path, default=None, help="zapisz pelny wynik do pliku JSON")
    parser.add_argument("--pokaz", type=int, default=60, help="ile naruszen wypisac na ekran (domyslnie 60; wszystkie sa w --json)")
    args = parser.parse_args(argv)

    lista = wczytaj_liste(args.dozwolone)
    pary = zmienione(args.repo, args.od, args.do)
    nowe = [s for status, s in pary if status == "A"]
    zawartosc = tresci(args.repo, args.do, nowe)
    liczniki: dict[str, dict[str, int]] = {}
    naruszenia, poza_etapem, odstepstwo_ascii = [], [], []
    wyjatki = wczytaj_wyjatki(args.wyjatki_ascii)
    for status, sciezka in pary:
        grupa = grupa_sciezki(sciezka, lista)
        nazwa_grupy = grupa or "POZA_LISTAMI"
        licznik = liczniki.setdefault(nazwa_grupy, {"A": 0, "M": 0, "D": 0, "inne": 0})
        licznik[status if status in licznik else "inne"] += 1
        if grupa is None:
            naruszenia.append({"sciezka": sciezka, "status": status, "powod": "sciezka poza listami paczek"})
        if status != "A":
            continue
        for powod in ocen_nowy(sciezka, zawartosc.get(sciezka, b""), args.maks_kb):
            wpis = {"sciezka": sciezka, "status": status, "powod": powod, "grupa": nazwa_grupy}
            if grupa == "E3" and sciezka in wyjatki and powod.startswith("nie ASCII"):
                wpis["wierszy_nie_ascii"] = wiersze_nie_ascii(zawartosc.get(sciezka, b""))
                odstepstwo_ascii.append(wpis)
                continue
            (naruszenia if grupa in ("E3", None) else poza_etapem).append(wpis)
    nieuzyte = sorted(wyjatki - {w["sciezka"] for w in odstepstwo_ascii})

    hash_od = git(args.repo, "rev-parse", "--short", args.od).decode().strip()
    hash_do = git(args.repo, "rev-parse", "--short", args.do).decode().strip()
    print(f"T13 higiena repo: {hash_od}..{hash_do}, zmienionych plikow {len(pary)}, w tym nowych {len(nowe)}")
    print(f"{'grupa':<16}{'nowe':>6}{'zmien.':>8}{'usun.':>7}")
    for nazwa in sorted(liczniki):
        licznik = liczniki[nazwa]
        print(f"{nazwa:<16}{licznik['A']:>6}{licznik['M']:>8}{licznik['D']:>7}")
    print(f"NARUSZENIA (grupa E3 i sciezki poza listami): {len(naruszenia)}")
    for wpis in naruszenia[:args.pokaz]:
        print(f"  {wpis['status']} {wpis['sciezka'].encode('ascii', 'backslashreplace').decode()} -> {wpis['powod']}")
    if len(naruszenia) > args.pokaz:
        print(f"  ... i {len(naruszenia) - args.pokaz} dalszych (pelna lista w --json)")
    print(f"nie-ASCII: napisy ekranu, odstepstwo O11 (nie licza sie do naruszen): {len(odstepstwo_ascii)} plikow z {len(wyjatki)} na liscie")
    for wpis in odstepstwo_ascii:
        print(f"  {wpis['status']} {wpis['sciezka']} -> {wpis['wierszy_nie_ascii']} wierszy nie-ASCII ({wpis['powod'].split('(')[1].rstrip(')')})")
    for sciezka in nieuzyte:
        print(f"  (pozycja listy wyjatkow bez trafienia - plik nie jest nowy albo jest juz ASCII: {sciezka})")
    print(f"UWAGI w grupach spoza etapu 3 (nie licza sie do wyniku T13, do oceny koordynatora): {len(poza_etapem)}")
    powody: dict[str, int] = {}
    for wpis in poza_etapem:
        klucz = f"{wpis['grupa']}: {wpis['powod'].split(' (')[0].split(': ')[0]}"
        powody[klucz] = powody.get(klucz, 0) + 1
    for klucz in sorted(powody):
        print(f"  {klucz}: {powody[klucz]}")
    if args.json:
        args.json.write_text(json.dumps({"od": hash_od, "do": hash_do, "zmienionych": len(pary), "nowych": len(nowe), "liczniki": liczniki,
                                         "naruszenia": naruszenia, "odstepstwo_o11_napisy_ekranu": odstepstwo_ascii,
                                         "wyjatki_bez_trafienia": nieuzyte, "uwagi_poza_etapem": poza_etapem}, ensure_ascii=True, indent=1) + "\n",
                             encoding="ascii", newline="\n")
    print("WYNIK T13:", (f"ZAL z odstepstwem O11 (0 naruszen; {len(odstepstwo_ascii)} plikow napisow ekranu nie-ASCII)" if odstepstwo_ascii
                         else "ZAL (0 naruszen)") if not naruszenia else f"FAIL ({len(naruszenia)} naruszen)")
    return 0 if not naruszenia else 1


if __name__ == "__main__":
    sys.exit(main())
