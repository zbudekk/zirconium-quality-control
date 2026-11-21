"""Kalibracja diod: ktory blok pikseli matrycy lezy pod ktorym gniazdem, dla kazdej ramki i ukladu.

Plik lokalny (decyzja DW9; plan etapu 3, 3.6): domyslnie `dane/kalibracja_ramek.json` na
laptopie stanowiska. Pliki `modele_plytek/*/uklad.json` zostaja bajtowo bez zmian (fakt 9) -
kalibracja ich nie zapisuje, tylko czyta geometrie, zeby policzyc wartosci startowe.
Laptop (indicate) liczy z tego pliku pole `px` gniazd w planie; ramka ukladow nie zna.

Format (wersja 1):
  {"wersja": 1,
   "matryca": {"szerokosc": 64, "wysokosc": 64, "raster_mm": 2.5},
   "ramki": {"W": {"wieczorna": {"zrodlo": "geometria", "gniazda": {"1": [x, y, w, h], ...}}, ...},
             "P": {"poranna": {...}, "poranna_r54": {...}, "okragla_ramkowa_poranna": {...}}}}
x, y = lewy gorny piksel bloku (uklad klatki z obraz.py), w, h = rozmiar. Kazdy blok w obszarze
plytki, bloki jednego ukladu sie nie nakladaja. "zrodlo": "geometria" (policzone z uklad.json)
albo "kalibracja" (sprawdzone na ramce, PR 9 krok 13 - paczka C2).

Uklady na ramkach (E3-O2): kwadratowe `wieczorna` / `poranna` (R59 i R54) oraz okragle ramkowe
`okragla_ramkowa_wieczorna` (plytki n1-n3, ramka W) i `okragla_ramkowa_poranna` (n4-n6, ramka P) -
R58: te same gniazda i srodek co kwadrat R59, wiec wartosci startowe sa rowne wartosciom kwadratu.
Plytki okragle testowe n8 / n9 (`okragla_wieczorna`, `okragla_poranna`) na ramce nie leza - bez wpisu.
Plik sprzed E3-O2 (bez ukladow ramkowych) uzupelnia `uzupelnij`: dopisuje TYLKO brakujace uklady
(z geometrii), istniejacych wpisow - takze "kalibracja" - nie rusza.

Wiersz polecen:
  python -m ramka.kalibracja --domyslna --modele modele_plytek --wyjscie dane/kalibracja_ramek.json
  python -m ramka.kalibracja --sprawdz dane/kalibracja_ramek.json
  python -m ramka.kalibracja --uzupelnij dane/kalibracja_ramek.json --modele modele_plytek
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path

from . import obraz

WERSJA_PLIKU = 1
ROLE_UKLADOW = {"wieczorna": "W", "poranna": "P"}  # pole "plate" w uklad.json -> ramka (plytki kwadratowe)
# E3-O2: plytki okragle ramkowe n1-n6 (R58; pole "plate" = nazwa ukladu, "shape" = "round") -> ramka
ROLE_UKLADOW_RAMKOWYCH = {"okragla_ramkowa_wieczorna": "W", "okragla_ramkowa_poranna": "P"}
PRZYROSTEK_KOPII = ".przed_uzupelnieniem"  # kopia pliku kalibracji sprzed dopisania ukladow (`uzupelnij_plik`)
BOK_GNIAZDA = 3            # blok 3 x 3 pod gniazdem okraglym (plan_ramki_v2 9 krok 13)
WYSOKOSC_RYNIENKI = 3
WZOR_UKLADU = re.compile(r"[a-z0-9_]{1,40}")  # tylko fullmatch (D-N9: koncowe "\n" odrzucane)
ZRODLA = ("geometria", "kalibracja")


class BladKalibracji(ValueError):
    """Zly plik kalibracji; komunikat zawiera sciezke pola."""


def blok_z_mm(x_mm: float, y_mm: float, w: int, h: int) -> list:
    """Blok w x h pikseli o srodku w punkcie plytki (mm, uklad z uklad.json: x w prawo, y do tylu)."""
    kol = obraz.SZEROKOSC / 2 + x_mm / obraz.RASTER_MM
    wie = obraz.WYSOKOSC / 2 - y_mm / obraz.RASTER_MM
    return [int(math.floor(kol - w / 2 + 0.5)), int(math.floor(wie - h / 2 + 0.5)), w, h]


def domyslna_dla_ukladu(uklad: dict) -> dict:
    """{"id": [x, y, w, h]} z geometrii gniazd uklad.json (wartosci startowe przed kalibracja)."""
    wynik = {}
    for g in uklad["sockets"]:
        if g.get("type") == "trough":
            n = int(g.get("hole_count", 1))
            rozpietosc = (n - 1) * float(g.get("hole_pitch", 0)) + float(g.get("hole_d", 3))
            dlugi = int(math.ceil(rozpietosc / obraz.RASTER_MM - 1e-9))
            kat = float(g.get("angle", 0)) % 180
            w, h = (dlugi, WYSOKOSC_RYNIENKI) if kat < 45 or kat > 135 else (WYSOKOSC_RYNIENKI, dlugi)
        else:
            w = h = BOK_GNIAZDA
        wynik[str(int(g["id"]))] = blok_z_mm(float(g["x"]), float(g["y"]), w, h)
    return wynik


def rola_ukladu(uklad: dict):
    """Ramka ("W" / "P"), na ktorej lezy plytka o tym `uklad.json`, albo None (plytka okragla testowa n8 / n9, uklad
    nieznany): kwadrat `wieczorna` / `poranna` albo okragla ramkowa `okragla_ramkowa_*` (E3-O2)."""
    ksztalt = uklad.get("shape", "square")
    if ksztalt == "square":
        return ROLE_UKLADOW.get(uklad.get("plate"))
    if ksztalt == "round":
        return ROLE_UKLADOW_RAMKOWYCH.get(uklad.get("plate"))
    return None


def domyslna(katalog_modeli) -> dict:
    """Kalibracja startowa z geometrii dla ukladow lezacych na ramkach: kwadratowych i okraglych ramkowych (`rola_ukladu`;
    plytki okragle testowe n8 / n9 nie pasuja do wkladki ramki)."""
    ramki = {"W": {}, "P": {}}
    for plik in sorted(Path(katalog_modeli).glob("*/uklad.json")):
        uklad = json.loads(plik.read_text(encoding="utf-8"))
        rola = rola_ukladu(uklad)
        if rola is None:
            continue
        ramki[rola][plik.parent.name] = {"zrodlo": "geometria", "gniazda": domyslna_dla_ukladu(uklad)}
    dane = {"wersja": WERSJA_PLIKU,
            "matryca": {"szerokosc": obraz.SZEROKOSC, "wysokosc": obraz.WYSOKOSC, "raster_mm": obraz.RASTER_MM},
            "ramki": ramki}
    sprawdz(dane)
    return dane


def _blad(sciezka: str, opis: str):
    raise BladKalibracji(f"{sciezka}: {opis}")


def sprawdz(dane) -> dict:
    """Walidacja pliku kalibracji; zwraca dane albo zglasza BladKalibracji."""
    if not isinstance(dane, dict):
        _blad("kalibracja", "oczekiwano obiektu JSON")
    if set(dane) - {"wersja", "matryca", "ramki"}:
        _blad("kalibracja", "nieznane klucze")
    if dane.get("wersja") != WERSJA_PLIKU or isinstance(dane.get("wersja"), bool):
        _blad("kalibracja.wersja", f"obslugiwana wersja {WERSJA_PLIKU}")
    m = dane.get("matryca")
    if m != {"szerokosc": obraz.SZEROKOSC, "wysokosc": obraz.WYSOKOSC, "raster_mm": obraz.RASTER_MM}:
        _blad("kalibracja.matryca", "oczekiwano matrycy 64 x 64, raster 2,5 mm")
    ramki = dane.get("ramki")
    if not isinstance(ramki, dict) or not ramki:
        _blad("kalibracja.ramki", "oczekiwano obiektu z ramkami W i P")
    for rola, uklady in ramki.items():
        sr = f"kalibracja.ramki.{rola}" if rola in ("W", "P") else "kalibracja.ramki"
        if rola not in ("W", "P"):
            _blad(sr, "ramka W albo P")
        if not isinstance(uklady, dict):
            _blad(sr, "oczekiwano obiektu ukladow")
        for nazwa, wpis in uklady.items():
            if not isinstance(nazwa, str) or not WZOR_UKLADU.fullmatch(nazwa):
                _blad(sr, "niedozwolona nazwa ukladu")
            su = f"{sr}.{nazwa}"
            if not isinstance(wpis, dict) or set(wpis) - {"zrodlo", "gniazda"} or "gniazda" not in wpis:
                _blad(su, "oczekiwano {\"zrodlo\", \"gniazda\"}")
            if wpis.get("zrodlo", "geometria") not in ZRODLA:
                _blad(su + ".zrodlo", "geometria albo kalibracja")
            gn = wpis["gniazda"]
            if not isinstance(gn, dict) or not gn:
                _blad(su + ".gniazda", "oczekiwano niepustego obiektu")
            zajete = {}
            for gid, blok in gn.items():
                sg = f"{su}.gniazda.{gid}" if isinstance(gid, str) and gid.isdigit() else su + ".gniazda"
                if not (isinstance(gid, str) and gid.isdigit() and 1 <= int(gid) <= 64):
                    _blad(sg, "id gniazda 1..64")
                if (not isinstance(blok, list) or len(blok) != 4
                        or any(isinstance(v, bool) or not isinstance(v, int) for v in blok)):
                    _blad(sg, "oczekiwano [x, y, szerokosc, wysokosc] (liczby calkowite)")
                x, y, w, h = blok
                if not (1 <= w <= 24 and 1 <= h <= 24):
                    _blad(sg, "rozmiar bloku 1..24")
                if not obraz.w_obszarze_plytki(x, y, w, h):
                    _blad(sg, "blok poza obszarem plytki")
                for yy in range(y, y + h):
                    for xx in range(x, x + w):
                        if (xx, yy) in zajete:
                            _blad(sg, f"blok naklada sie na gniazdo {zajete[(xx, yy)]}")
                        zajete[(xx, yy)] = gid
    return dane


def wczytaj(sciezka) -> dict:
    try:
        dane = json.loads(Path(sciezka).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as e:
        raise BladKalibracji(f"kalibracja: nie da sie odczytac pliku ({type(e).__name__})") from None
    return sprawdz(dane)


def zapisz(dane, sciezka) -> None:
    sprawdz(dane)
    tekst = json.dumps(dane, ensure_ascii=True, indent=1, sort_keys=True) + "\n"
    Path(sciezka).parent.mkdir(parents=True, exist_ok=True)
    with open(sciezka, "w", encoding="ascii", newline="\n") as f:
        f.write(tekst)


def uzupelnij(dane: dict, katalog_modeli) -> list:
    """Dopisuje do `dane` (w miejscu) uklady, ktore maja kalibracje startowa (`domyslna`), a ktorych w `dane` nie ma - np.
    uklady okragle ramkowe w pliku sprzed E3-O2. Istniejacych wpisow (takze "zrodlo": "kalibracja") NIE zmienia. Zwraca
    liste dopisanych [(rola, uklad), ...] (pusta = nic do dopisania)."""
    sprawdz(dane)
    wzor = domyslna(katalog_modeli)
    dopisane = []
    for rola in ("W", "P"):
        for nazwa in sorted(wzor["ramki"][rola]):
            if nazwa not in dane["ramki"].get(rola, {}):
                dane["ramki"].setdefault(rola, {})[nazwa] = wzor["ramki"][rola][nazwa]
                dopisane.append((rola, nazwa))
    if dopisane:
        sprawdz(dane)
    return dopisane


def uzupelnij_plik(sciezka, katalog_modeli) -> tuple:
    """Plik kalibracji uzupelniony o brakujace uklady (`uzupelnij`): zwraca (dane, dopisane). Gdy cos dopisano: kopia
    starego pliku obok (`<nazwa>.przed_uzupelnieniem`, istniejacej kopii nie nadpisuje), potem zapis przez plik tymczasowy
    i podmiane (plik nigdy nie zostaje w polowie zapisany). Nic do dopisania = pliku nie rusza. Zly plik = BladKalibracji;
    blad zapisu = OSError (wolajacy moze wtedy uzupelnic dane w pamieci przez `uzupelnij`)."""
    sciezka = Path(sciezka)
    dane = wczytaj(sciezka)
    dopisane = uzupelnij(dane, katalog_modeli)
    if dopisane:
        kopia = sciezka.with_name(sciezka.name + PRZYROSTEK_KOPII)
        if not kopia.exists():
            kopia.write_bytes(sciezka.read_bytes())
        tymczasowy = sciezka.with_name(sciezka.name + ".tmp")
        try:
            zapisz(dane, tymczasowy)
            os.replace(tymczasowy, sciezka)
        finally:
            try:
                tymczasowy.unlink()
            except OSError:
                pass
    return dane, dopisane


def blok(kal: dict, rola: str, uklad: str, gniazdo) -> list:
    """[x, y, w, h] gniazda; KeyError, gdy ramka, uklad albo gniazdo nie ma kalibracji."""
    return list(kal["ramki"][rola][uklad]["gniazda"][str(int(gniazdo))])


def gniazda_planu(kal: dict, rola: str, uklad: str, przypisanie: dict) -> list:
    """Pomoc dla laptopa: {id: {"kolor": ..., "kuweta": ... albo None}} -> lista gniazd planu (z px)."""
    wynik = []
    for gid in sorted(przypisanie, key=int):
        wpis = przypisanie[gid]
        g = {"id": int(gid), "px": blok(kal, rola, uklad, gid), "kolor": wpis["kolor"]}
        if wpis.get("kuweta") is not None:
            g["kuweta"] = wpis["kuweta"]
        wynik.append(g)
    return wynik


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m ramka.kalibracja", description="Plik kalibracji diod ramek.")
    p.add_argument("--domyslna", action="store_true", help="policz kalibracje startowa z uklad.json")
    p.add_argument("--modele", help="katalog modele_plytek (tylko odczyt)")
    p.add_argument("--wyjscie", help="plik wynikowy (np. dane/kalibracja_ramek.json)")
    p.add_argument("--sprawdz", help="sprawdz plik kalibracji")
    p.add_argument("--uzupelnij", help="dopisz do pliku kalibracji brakujace uklady z geometrii (wymaga --modele)")
    a = p.parse_args(argv)
    try:
        if a.uzupelnij:
            if not a.modele:
                print("blad: --uzupelnij wymaga --modele", file=sys.stderr)
                return 2
            try:
                _, dopisane = uzupelnij_plik(a.uzupelnij, a.modele)
            except OSError as e:
                print(f"blad: pliku nie da sie zapisac ({type(e).__name__})", file=sys.stderr)
                return 1
            if dopisane:
                print(f"dopisano do {a.uzupelnij} (z geometrii): " + ", ".join(f"{r}: {u}" for r, u in dopisane))
            else:
                print(f"{a.uzupelnij}: nic do dopisania")
            return 0
        if a.domyslna:
            if not a.modele or not a.wyjscie:
                print("blad: --domyslna wymaga --modele i --wyjscie", file=sys.stderr)
                return 2
            dane = domyslna(a.modele)
            zapisz(dane, a.wyjscie)
            n = {r: {u: len(v["gniazda"]) for u, v in uk.items()} for r, uk in dane["ramki"].items()}
            print(f"zapisano {a.wyjscie}: {json.dumps(n, sort_keys=True)}")
            return 0
        if a.sprawdz:
            dane = wczytaj(a.sprawdz)
            n = sum(len(v["gniazda"]) for uk in dane["ramki"].values() for v in uk.values())
            print(f"kalibracja poprawna: {n} gniazd")
            return 0
    except BladKalibracji as e:
        print(f"blad: {e}", file=sys.stderr)
        return 1
    p.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
