"""zrzuty_okna - zrzuty nowego okna programu "Stanowisko" (paczka E3-U1a) z danych sztucznych, bez ekranu.

Okno jest prawdziwe (``stanowisko.ui.utworz_okno``), dane wylacznie sztuczne (``kontroler_api.AtrapaKontrolera`` - te same,
ktore pokazuje ``py -3.12 -m stanowisko.aplikacja --atrapa``: fikcyjne kuwety, osoby "Technik A" / "Technik B"), zegar jest
staly - to samo polecenie daje te same obrazki. Skrypt steruje oknem jak technik (klikniecia) i zapisuje caly ekran jako PNG
w kazdym rozmiarze z ``ROZMIARY`` (1920 x 1080 i 1536 x 864 - laptop stanowiska przy skalowaniu 100 % i 125 %).

Uzycie (z katalogu stanowisko/):
    py -3.12 narzedzia/zrzuty_okna.py                      komplet do ../etap3/nowy_interfejs/zrzuty/
    py -3.12 narzedzia/zrzuty_okna.py --wyjscie KATALOG    komplet do innego katalogu
    py -3.12 narzedzia/zrzuty_okna.py --tylko wieczor_praca_czerwona --rozmiar 1280x720
    py -3.12 narzedzia/zrzuty_okna.py --lista              nazwy i opisy zrzutow

Wlasciciel oglada obrazki na telefonie; po zmianie wygladu okna: uruchom ponownie i OBEJRZYJ kazdy PNG.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
import tempfile
from pathlib import Path

STANOWISKO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STANOWISKO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import zrzuty_instrukcji as Z  # noqa: E402 - ``Ekran``, staly zegar i licznik czasu; bez Qt na poziomie modulu

KATALOG_DOMYSLNY = STANOWISKO.parent / "etap3" / "nowy_interfejs" / "zrzuty"
ROZMIARY = ((1920, 1080), (1536, 864))
WIECZOR = dt.datetime(2026, 11, 23, 20, 25, 0)  # poniedzialek, zmiana 2
OSOBA = "Technik A"
UKLAD = "okragla_ramkowa_wieczorna"  # plytka okragla ramkowa R58 (19 gniazd) - jak na makiecie i na testach sprzetu
# plytka 1: obejrzana do konca; plytka 2: ogladana (czerwone 3 i 7, zolte 11, szare 15); projekty atrapy 1-30
PLYTKA_1 = {n: "zielony" for n in range(1, 14)} | {2: "czerwony", 9: "zolty"}
PLYTKA_2 = {n: "zielony" for n in range(1, 18)} | {3: "czerwony", 7: "czerwony", 11: "zolty", 15: "szary"}
PROJEKTY_2 = {n: 13 + n for n in range(1, 18)}


def _wieczor(katalog: Path, *, osoba: bool = True):
    """Wieczor z dwiema plytkami: nr 1 sprawdzona (jedna "Ukruszona", jedna "OK"), nr 2 z pracami do obejrzenia."""
    k, zegar = Z._atrapa(katalog, WIECZOR)
    k.wybierz_operatora(OSOBA)
    zegar.przesun(2)
    pierwsza = k.symuluj_skan("zwykla", numer=1, uklad=UKLAD, gniazda=PLYTKA_1)
    plytka = k.stan().plytka(pierwsza)
    zegar.przesun(3)
    k.ukruszona(plytka.gniazdo(2).praca.praca_id)
    k.ok(plytka.gniazdo(9).praca.praca_id)
    zegar.przesun(20)
    druga = k.symuluj_skan("zwykla", numer=2, uklad=UKLAD, gniazda=PLYTKA_2, projekty=PROJEKTY_2)
    zegar.przesun(2)
    if not osoba:
        k.wybierz_operatora(None)
    return k, zegar, (pierwsza, druga)


def _otworz_prace(e, gniazdo: int) -> None:
    """Klik w gniazdo i czekanie, az kolumna "Praca" pokaze obraz odchylek (obraz wczytuje watek pomocniczy)."""
    from stanowisko.ui import napisy as N

    e.klik_gniazdo(gniazdo)
    e.czekaj(lambda: e.jest("widok_pracy") and N.OBRAZ_WCZYTYWANIE not in e.teksty(), 10.0, "widok pracy z obrazem odchylek")


def scena_praca_czerwona(katalog: Path, rozmiar: tuple):
    k, _, _ = _wieczor(katalog)
    e = Z.Ekran(k, rozmiar)
    _otworz_prace(e, 7)
    return e, k


def scena_pytanie_ponowny_skan(katalog: Path, rozmiar: tuple):
    k, zegar, (_, druga) = _wieczor(katalog)
    plytka = k.stan().plytka(druga)
    k.ukruszona(plytka.gniazdo(3).praca.praca_id)
    k.ok(plytka.gniazdo(11).praca.praca_id)
    e = Z.Ekran(k, rozmiar)
    zegar.przesun(9)
    k.symuluj_skan("zwykla", numer=2, uklad=UKLAD, gniazda=PLYTKA_2 | {7: "zielony"}, projekty=PROJEKTY_2)
    e.czekaj(lambda: e.jest("przycisk_nowa_plytka"), 5.0, "nowy wynik czeka")
    e.klik("przycisk_nowa_plytka")
    e.czekaj(lambda: e.jest("pytanie_ponowny_skan"), 5.0, "pytanie o ponowny skan")
    return e, k


def scena_bez_osoby(katalog: Path, rozmiar: tuple):
    k, _, _ = _wieczor(katalog, osoba=False)
    e = Z.Ekran(k, rozmiar)
    e.czekaj(lambda: e.jest("panel_osoba"), 5.0, "lista osob")
    _otworz_prace(e, 3)
    return e, k


def scena_analiza_nowego_skanu(katalog: Path, rozmiar: tuple):
    k, _, _ = _wieczor(katalog)
    e = Z.Ekran(k, rozmiar)
    k.start_skanu()
    k.symuluj_postep(udzial=0.4, czeka=1)
    e.czekaj(lambda: e.okno.mapa.poprzednia(), 5.0, "mapa oznaczona jako poprzednia plytka")
    return e, k


def scena_bledy_programu(katalog: Path, rozmiar: tuple):
    k, _, _ = _wieczor(katalog)
    e = Z.Ekran(k, rozmiar)
    _otworz_prace(e, 7)
    k.symuluj_blad_zapisu(1)
    k.symuluj_skaner(dostepny=False)
    e.czekaj(lambda: e.jest("lista_bledow"), 5.0, "lista bledow programu")
    return e, k


# nazwa -> (scena, opis: co ma byc widac)
ZRZUTY = {
    "wieczor_praca_czerwona": (scena_praca_czerwona, "wieczor: plytka 2 na mapie, otwarta praca czerwona (gniazdo 7) z obrazem odchylek i decyzjami"),
    "wieczor_pytanie_ponowny_skan": (scena_pytanie_ponowny_skan, 'wieczor: pytanie "Ponowny skan tej samej plytki?" w strefie pytan nad mapa'),
    "wieczor_bez_osoby": (scena_bez_osoby, "wieczor bez wybranej osoby: lista osob pod paskiem gornym, decyzje nieaktywne z wyjasnieniem"),
    "wieczor_analiza_nowego_skanu": (scena_analiza_nowego_skanu, 'wieczor w czasie analizy nowego skanu: mapa oznaczona "POPRZEDNIA PLYTKA"'),
    "wieczor_bledy_programu": (scena_bledy_programu, "wieczor: licznik bledow na pasku stanu i rozwinieta lista bledow programu"),
}
PODSTAWOWE = ("wieczor_praca_czerwona", "wieczor_pytanie_ponowny_skan", "wieczor_bez_osoby")  # w kazdym rozmiarze z ROZMIARY


def zrob(nazwa: str, rozmiar: tuple, katalog_wyjscia: Path) -> Path:
    """Buduje scene ``nazwa`` w oknie ``rozmiar`` i zapisuje ``<nazwa>_<szer>x<wys>.png``; zwraca plik."""
    scena, _ = ZRZUTY[nazwa]
    with tempfile.TemporaryDirectory(prefix="qc_zrzuty_") as tmp, Z.staly_licznik_czasu():
        e, k = scena(Path(tmp), rozmiar)
        try:
            # obraz spokojnego ekranu: po ochronie strefy pytan / listy bledow (przygaszenie 800 ms) i po blysku paska gornego
            e.czekaj(lambda: not e.okno.ochrona_nakladek_aktywna() and e.okno.pasek_gorny.property("blysk") != "true", 5.0, "spokojny ekran")
            obraz = e.obraz()
            katalog_wyjscia.mkdir(parents=True, exist_ok=True)
            plik = katalog_wyjscia / f"{nazwa}_{rozmiar[0]}x{rozmiar[1]}.png"
            if not obraz.save(str(plik), "PNG", 0):
                raise RuntimeError(f"nie zapisano {plik.name}")
        finally:
            e.zamknij()
            k.zamknij()
    return plik


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Zrzuty nowego okna programu "Stanowisko" (dane sztuczne, bez ekranu).')
    parser.add_argument("--wyjscie", type=Path, default=KATALOG_DOMYSLNY, help="katalog na PNG (domyslnie etap3/nowy_interfejs/zrzuty)")
    parser.add_argument("--tylko", nargs="+", metavar="NAZWA", help="tylko te zrzuty")
    parser.add_argument("--rozmiar", nargs="+", metavar="SZERxWYS", help="rozmiary okna, np. 1920x1080 1280x720 (domyslnie 1920x1080 i 1536x864)")
    parser.add_argument("--lista", action="store_true", help="wypisz nazwy i opisy zrzutow")
    args = parser.parse_args(argv)
    if args.lista:
        for nazwa, (_, opis) in ZRZUTY.items():
            print(f"{nazwa} - {opis}")
        return 0
    nazwy = args.tylko or list(ZRZUTY)
    nieznane = [n for n in nazwy if n not in ZRZUTY]
    if nieznane:
        print(f"BLAD: nieznany zrzut: {', '.join(nieznane)} (znane: {', '.join(ZRZUTY)})", file=sys.stderr)
        return 2
    try:
        rozmiary = [tuple(int(x) for x in r.lower().split("x")) for r in args.rozmiar] if args.rozmiar else None
        if rozmiary is not None and any(len(r) != 2 for r in rozmiary):
            raise ValueError
    except ValueError:
        print("BLAD: rozmiar podaj jako SZERxWYS, np. 1536x864", file=sys.stderr)
        return 2
    Z.przygotuj_qt()
    razem = 0
    for nazwa in nazwy:
        for rozmiar in rozmiary or (ROZMIARY if nazwa in PODSTAWOWE else ROZMIARY[1:]):
            plik = zrob(nazwa, rozmiar, args.wyjscie)
            razem += 1
            print(f"{plik.name}: {plik.stat().st_size} B - {ZRZUTY[nazwa][1]}")
    print(f"zrzutow: {razem}, katalog: {args.wyjscie}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
