"""dowody_lf.py - kontrola i naprawa plikow dowodow przed ``git add`` (uwaga 9 recenzji PR #44): ASCII + LF, bez duzych danych.

Po co: logi z przekierowania ``cmd >`` maja konce CRLF, a wyjscie narzedzi programu bywa ze znakami spoza ASCII - taki
dowod dodany do repo daje naruszenie w T13 (nowe pliki: ASCII, LF). Skrypt czyta katalog dowodow testu i:
  * bez ``--napraw``: wypisuje dla kazdego pliku tekstowego liczbe CR, bajtow NUL i bajtow spoza ASCII; kod 1, gdy sa,
  * z ``--napraw``: zamienia CRLF i samotne CR na LF, znaki spoza ASCII transliteruje (rozklad NFKD + l z kreska; czego sie
    nie da - na "?") i zapisuje plik; liczby zamian sa w wyniku (transliteracja zmienia tresc dowodu - dlatego jest liczona),
  * zawsze zglasza pliki, ktorych do repo dodawac nie wolno: STL, bazy, ZIP, zapisy ruchu, pliki > 1024 KB (kod 1).
Pliki o innych rozszerzeniach niz tekstowe sa wypisane jako "nieznane rozszerzenie" (kod 1) - dowod ma byc tekstem.

Uzycie:  PY -I <ODB>\\narzedzia\\dowody_lf.py --katalog <DOW> [--napraw] [--wynik <plik.txt>]
Kody: 0 = wszystkie pliki ASCII + LF i nic zakazanego; 1 = sa naruszenia (po ``--napraw``: te, ktorych nie dalo sie naprawic);
2 = blad uzycia.
"""
from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path

TEKST = {".txt", ".log", ".md", ".json", ".tsv", ".csv", ".toml", ".cmd", ".bat", ".ps1", ".py"}
CRLF = {".cmd", ".bat", ".ps1"}
ZAKAZANE = {".stl", ".sqlite", ".db", ".zip", ".bin", ".pkl", ".npz", ".npy", ".whl", ".xlsx", ".png", ".pdf"}
RECZNE = {0x142: "l", 0x141: "L", 0x2013: "-", 0x2014: "-", 0x201e: '"', 0x201d: '"', 0x2026: "...", 0xb7: "*"}
LIMIT_KB = 1024


def do_ascii(tekst: str) -> tuple[str, int]:
    wynik, nieznane = [], 0
    for znak in tekst:
        if ord(znak) < 128:
            wynik.append(znak)
        elif ord(znak) in RECZNE:
            wynik.append(RECZNE[ord(znak)])
        else:
            rozklad = "".join(c for c in unicodedata.normalize("NFKD", znak) if ord(c) < 128)
            if not rozklad:
                nieznane += 1
            wynik.append(rozklad or "?")
    return "".join(wynik), nieznane


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="dowody_lf.py", description="Kontrola (i z --napraw naprawa) plikow dowodow: ASCII + LF, bez duzych danych.")
    ap.add_argument("--katalog", type=Path, required=True, action="append", help="katalog dowodow (mozna powtarzac)")
    ap.add_argument("--napraw", action="store_true", help="zamien CRLF na LF i znaki spoza ASCII na ASCII (zapis w miejscu)")
    ap.add_argument("--wynik", type=Path, default=None, help="plik z wynikiem (ASCII, LF)")
    a = ap.parse_args(argv)
    linie, naruszen, plikow = [], 0, 0
    for katalog in a.katalog:
        if not katalog.is_dir():
            print(f"BLAD: brak katalogu {katalog}", file=sys.stderr)
            return 2
        for plik in sorted(q for q in katalog.rglob("*") if q.is_file()):
            if a.wynik is not None and plik.resolve() == a.wynik.resolve():
                continue
            plikow += 1
            nazwa, roz, kb = plik.relative_to(katalog).as_posix(), plik.suffix.lower(), plik.stat().st_size / 1024
            if roz in ZAKAZANE or kb > LIMIT_KB:
                naruszen += 1
                linie.append(f"ZAKAZANY  {nazwa}: {'rozszerzenie ' + roz if roz in ZAKAZANE else f'{kb:.0f} KB > {LIMIT_KB} KB'} - nie dodawac do repo")
                continue
            if roz not in TEKST:
                naruszen += 1
                linie.append(f"NIEZNANY  {nazwa}: rozszerzenie '{roz}' spoza listy tekstowych - nie sprawdzono")
                continue
            dane = plik.read_bytes()
            cr, nul, wysokie = dane.count(b"\r"), dane.count(b"\x00"), sum(1 for b in dane if b > 127)
            zle_konce = (dane.count(b"\n") - dane.count(b"\r\n") + (cr - dane.count(b"\r\n"))) if roz in CRLF else cr
            if not (zle_konce or nul or wysokie):
                linie.append(f"OK        {nazwa}")
                continue
            if not a.napraw or nul or roz in CRLF:
                naruszen += 1
                linie.append(f"NARUSZENIE {nazwa}: CR {cr}, NUL {nul}, bajtow spoza ASCII {wysokie}"
                             + (" (plik z bajtami NUL - np. UTF-16; napraw recznie)" if nul else "")
                             + (" (plik polecen ma miec CRLF - napraw recznie)" if roz in CRLF and not nul else ""))
                continue
            try:
                tekst = dane.decode("utf-8")
                kodowanie = "utf-8"
            except UnicodeDecodeError:
                tekst, kodowanie = dane.decode("cp1250", errors="replace"), "cp1250 (plik nie jest UTF-8)"
            tekst = tekst.replace("\r\n", "\n").replace("\r", "\n")
            tekst, nieznane = do_ascii(tekst)
            plik.write_bytes(tekst.encode("ascii"))
            linie.append(f"NAPRAWIONY {nazwa}: CR {cr} -> 0, bajtow spoza ASCII {wysokie} -> 0 (kodowanie {kodowanie}; znakow zamienionych na '?': {nieznane})")
    naglowek = f"dowody_lf.py: plikow {plikow}, naruszen {naruszen}{' (po naprawie)' if a.napraw else ''}"
    tekst = "\n".join([naglowek, *linie, f"WYNIK: {'ZAL (ASCII + LF, nic zakazanego)' if naruszen == 0 else f'FAIL ({naruszen} naruszen)'}"]) + "\n"
    print(tekst, end="")
    if a.wynik is not None:
        a.wynik.write_bytes(tekst.encode("ascii", errors="replace"))
    return 0 if naruszen == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
