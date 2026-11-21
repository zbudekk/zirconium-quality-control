"""Narzedzie "test LED" dla pliku kalibracji: zapala kolejno blok kazdego gniazda (z numerem
gniazda na marginesie) albo wszystkie bloki naraz (sasiednie gniazda w roznych kolorach).

Na ramce: zatrzymac usluge ramki (matryca obsluguje jeden program), potem np.
  python -m ramka.test_led --kalibracja kalibracja_ramek.json --uklad poranna --konfiguracja /etc/ramka/ramka.json
Plik konfiguracji ramki (`--konfiguracja`, ten sam co w `python -m ramka`) daje role, rodzaj sprzetu i ustawienia
matrycy (`obrot`, `lustro`, `jasnosc`, `piny_halla`, `mapowanie`, `spowolnienie_gpio`); `--rola` i `--sprzet` z wiersza
polecen maja pierwszenstwo przed plikiem. Bez pliku: wartosci domyslne z kodu (`program.Konfiguracja`), sprzet = atrapa.
Kody wyjscia: 0 = test pokazany, 1 = zly plik kalibracji / konfiguracji albo brak ukladu, 2 = sprzet niedostepny
(np. brak biblioteki matrycy) albo zla skladnia polecenia.
Operator patrzy z gory: kazde gniazdo swieci przez otwor w dnie, sasiednie ciemne (PR 9 krok 13).
Na atrapie (bez elektroniki) narzedzie sprawdza tylko plik i liczy wyswietlone klatki.
Szybki test samej matrycy z laptopa (bez kalibracji): PUT /tryb {"stan": "test_led"}.
"""
from __future__ import annotations

import argparse
import sys
import time

from . import kalibracja, obraz, program
from .sprzet import BladSprzetu

KOLORY_NAPRZEMIENNE = ("zielony", "czerwony", "niebieski", "zolty")


def _bloki(kal: dict, rola: str, uklad: str) -> list:
    gn = kal["ramki"][rola][uklad]["gniazda"]
    return [(int(g), gn[g]) for g in sorted(gn, key=int)]


def klatka_gniazda(blok, nr: int, kolor: str = "bialy") -> obraz.Klatka:
    k = obraz.Klatka()
    x, y, w, h = blok
    k.blok(x, y, w, h, obraz.KOLORY[kolor])
    obraz.rysuj_tekst_przod(k, str(nr))
    return k


def klatka_wszystkich(kal: dict, rola: str, uklad: str) -> obraz.Klatka:
    k = obraz.Klatka()
    for i, (_, (x, y, w, h)) in enumerate(_bloki(kal, rola, uklad)):
        k.blok(x, y, w, h, obraz.KOLORY[KOLORY_NAPRZEMIENNE[i % len(KOLORY_NAPRZEMIENNE)]])
    return k


def uruchom_test(sprzet, kal: dict, rola: str, uklad: str, czas_s: float = 0.7, sen=time.sleep) -> int:
    """Pokazuje kolejno kazde gniazdo; zwraca liczbe pokazanych gniazd. Na koniec gasi matryce."""
    n = 0
    for nr, blok in _bloki(kal, rola, uklad):
        sprzet.pokaz(klatka_gniazda(blok, nr))
        n += 1
        sen(czas_s)
    sprzet.pokaz(obraz.Klatka())
    return n


def utworz_sprzet(konf):
    """Sprzet testu z konfiguracji ramki: te same pola co `program.utworz_sprzet`, ale bez watku klawiatury."""
    if konf.sprzet == "rpi":
        from . import sprzet_rpi
        return sprzet_rpi.SprzetRpi(rola=konf.rola, piny_halla=konf.piny_halla, jasnosc=konf.jasnosc, obrot=konf.obrot,
                                    lustro=konf.lustro, mapowanie=konf.mapowanie, spowolnienie_gpio=konf.spowolnienie_gpio,
                                    klawisz_zamknij_piec=konf.klawisz_zamknij_piec, z_klawiatura=False)
    from .sprzet_atrapa import SprzetAtrapa
    return SprzetAtrapa()


def parser_polecen() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m ramka.test_led", description="Test LED wg pliku kalibracji.")
    p.add_argument("--kalibracja", required=True)
    p.add_argument("--rola", choices=("W", "P"), help="domyslnie z pliku konfiguracji ramki")
    p.add_argument("--uklad", required=True)
    p.add_argument("--sprzet", choices=("atrapa", "rpi"), help="domyslnie z pliku konfiguracji, bez pliku atrapa")
    p.add_argument("--konfiguracja", help="plik JSON z ustawieniami ramki - ten sam co w python -m ramka "
                                          "(na ramce /etc/ramka/ramka.json): rola, sprzet, obrot, lustro, jasnosc, piny")
    p.add_argument("--czas", type=float, default=0.7, help="sekundy na gniazdo")
    p.add_argument("--wszystkie", action="store_true", help="wszystkie gniazda naraz (10 s)")
    return p


def main(argv=None) -> int:
    p = parser_polecen()
    a = p.parse_args(argv)
    if not a.rola and not a.konfiguracja:
        p.error("podaj --rola W|P albo --konfiguracja (plik ramki z polem rola)")
    try:
        konf = program.wczytaj_konfiguracje(a.konfiguracja) if a.konfiguracja else program.Konfiguracja()
    except (OSError, ValueError, TypeError) as e:
        opis = str(e) if str(e).startswith("konfiguracja") else f"{type(e).__name__}: {e}"
        print(f"blad: konfiguracja ramki ({a.konfiguracja}) - {opis}", file=sys.stderr)
        return 1
    if a.rola:
        konf.rola = a.rola
    if a.sprzet:
        konf.sprzet = a.sprzet
    try:
        kal = kalibracja.wczytaj(a.kalibracja)
        _bloki(kal, konf.rola, a.uklad)
    except kalibracja.BladKalibracji as e:
        print(f"blad: {e}", file=sys.stderr)
        return 1
    except KeyError:
        print("blad: brak ukladu w kalibracji tej ramki", file=sys.stderr)
        return 1
    na_ramce = konf.sprzet == "rpi"
    if na_ramce and not a.konfiguracja:
        print("uwaga: bez --konfiguracja matryca dostaje ustawienia domyslne (obrot 0, bez lustra, jasnosc 60); "
              "na ramce podaj ten sam plik co usluga: --konfiguracja /etc/ramka/ramka.json", file=sys.stderr)
    try:
        sprzet = utworz_sprzet(konf)
    except BladSprzetu as e:
        print(f"blad: sprzet niedostepny: {e}", file=sys.stderr)
        return 2
    try:
        if a.wszystkie:
            sprzet.pokaz(klatka_wszystkich(kal, konf.rola, a.uklad))
            time.sleep(10.0 if na_ramce else 0.0)
            n = len(_bloki(kal, konf.rola, a.uklad))
        else:
            n = uruchom_test(sprzet, kal, konf.rola, a.uklad, a.czas if na_ramce else 0.0)
    finally:
        sprzet.zamknij()
    print(f"test LED: {n} gniazd ukladu {a.uklad} (ramka {konf.rola})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
