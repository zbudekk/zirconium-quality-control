"""Narzedzie "test LED" dla pliku kalibracji: zapala kolejno blok kazdego gniazda (z numerem
gniazda na marginesie) albo wszystkie bloki naraz (sasiednie gniazda w roznych kolorach).

Na ramce: zatrzymac usluge ramki (matryca obsluguje jeden program), potem np.
  python -m ramka.test_led --kalibracja kalibracja_ramek.json --rola P --uklad poranna --sprzet rpi
Operator patrzy z gory: kazde gniazdo swieci przez otwor w dnie, sasiednie ciemne (PR 9 krok 13).
Na atrapie (bez elektroniki) narzedzie sprawdza tylko plik i liczy wyswietlone klatki.
Szybki test samej matrycy z laptopa (bez kalibracji): PUT /tryb {"stan": "test_led"}.
"""
from __future__ import annotations

import argparse
import sys
import time

from . import kalibracja, obraz

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


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m ramka.test_led", description="Test LED wg pliku kalibracji.")
    p.add_argument("--kalibracja", required=True)
    p.add_argument("--rola", choices=("W", "P"), required=True)
    p.add_argument("--uklad", required=True)
    p.add_argument("--sprzet", choices=("atrapa", "rpi"), default="atrapa")
    p.add_argument("--czas", type=float, default=0.7, help="sekundy na gniazdo")
    p.add_argument("--wszystkie", action="store_true", help="wszystkie gniazda naraz (10 s)")
    a = p.parse_args(argv)
    try:
        kal = kalibracja.wczytaj(a.kalibracja)
        _bloki(kal, a.rola, a.uklad)
    except kalibracja.BladKalibracji as e:
        print(f"blad: {e}", file=sys.stderr)
        return 1
    except KeyError:
        print("blad: brak ukladu w kalibracji tej ramki", file=sys.stderr)
        return 1
    if a.sprzet == "rpi":
        from .sprzet_rpi import SprzetRpi
        sprzet = SprzetRpi(rola=a.rola, z_klawiatura=False)
    else:
        from .sprzet_atrapa import SprzetAtrapa
        sprzet = SprzetAtrapa()
    try:
        if a.wszystkie:
            sprzet.pokaz(klatka_wszystkich(kal, a.rola, a.uklad))
            time.sleep(10.0 if a.sprzet == "rpi" else 0.0)
            n = len(_bloki(kal, a.rola, a.uklad))
        else:
            n = uruchom_test(sprzet, kal, a.rola, a.uklad, a.czas if a.sprzet == "rpi" else 0.0)
    finally:
        sprzet.zamknij()
    print(f"test LED: {n} gniazd ukladu {a.uklad} (ramka {a.rola})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
