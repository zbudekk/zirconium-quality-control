"""Drzewo syntetyczne folderow zlecen (E3-A4): ``<zrodlo>/<folder zlecenia>/*.stl`` o FIKCYJNYCH nazwach.

Dane testowe katalogu (indeks, pule): kazde zlecenie ma wymyslone nazwisko, numer kuwety znany z budowy (prawda) i 1-2
male pliki STL (atrapy koron o roznych wymiarach, wiec kazdy plik ma inny skrot ``sha16``). Wzory nazw folderow
(plan etapu 3, sekcja 4.1 E3-A4, oraz maski prawdziwych nazw sprawdzone 17.11.2026 bez odczytu nazw: "L D4 L",
"L D4L", "L L. D4 L", "L D3 L", "L D4 L L", "L D4 LD1"):

  0 ``Nazwisko 3263 zs``        numer + kod literowy        5 ``3263 Nazwisko Imie``     numer na poczatku
  1 ``Nazwisko 1784PG``         kod sklejony z numerem       6 ``Nazwisko_88_zs``         podkreslniki
  2 ``Nazwisko J. 3263 zs``     inicjal z kropka             7 ``Nazwisko 512 Imie``      numer 1-3 cyfry
  3 ``Nazwisko J.3263``         inicjal sklejony z numerem   8 ``Nazwisko (NFD) 3263 ZS1`` litery w postaci NFD (OneDrive)
  4 ``Nazwisko 0412``           zera wiodace (kuweta 412)    9 ``#1234 Nazwisko``         zrodlo "prywatne", kuweta #1234

Pliki STL: nazwy w stylu exocad (``2026-11-16_nazwisko-14-crown_cad.stl``, most ``-24-25-26-bridge_cad.stl``) albo
proste (``zab 46.stl``). Na ekran narzedzie wypisuje tylko liczby - zadnych nazw.

Uzycie (z katalogu stanowisko/):
    py -3.12 narzedzia/drzewo_syntetyczne.py --cel dane/drzewo_testowe [--zlecen 40] [--seed 0] [--data 2026-11-16T12:00]
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

import atrapy_koron

NAZWISKA = ("Testowski", "Przykladowa", "Fikcyjny", "Zmyslona", "Atrapowicz", "Probna", "Wzorcowy", "Nowak-Testowa")
NAZWISKA_NFD = (unicodedata.normalize("NFD", "Wi\u015bniewska"), unicodedata.normalize("NFD", "\u017b\u00f3\u0142towski"))
IMIONA = ("Jan", "Anna", "Piotr", "Ewa", "Maria")
INICJALY = ("J", "A", "P", "E")
KODY = ("zs", "kor", "PG", "AB", "ZS1")
ZEBY = ("11", "12", "14", "16", "21", "24", "26", "36", "37", "45", "46")
WZOROW = 10


@dataclass
class ZlecenieTestowe:
    """Jedno zlecenie drzewa: zrodlo, nazwa folderu (fikcyjna), oczekiwana kuweta i nazwy plikow STL."""
    zrodlo: str
    folder: str
    kuweta: str
    wzor: int
    pliki: list[str] = field(default_factory=list)


def nazwa_folderu(wzor: int, numer: int, nazwisko: str, rng: np.random.Generator) -> tuple[str, str, str]:
    """(zrodlo, nazwa folderu, oczekiwana kuweta) dla wzoru 0-9; ``numer`` = numer kuwety (1-9999, wzory 4 i 7: < 1000)."""
    kod = KODY[int(rng.integers(len(KODY)))]
    imie = IMIONA[int(rng.integers(len(IMIONA)))]
    inicjal = INICJALY[int(rng.integers(len(INICJALY)))]
    k = str(numer)
    if wzor == 0:
        return "cyrkon", f"{nazwisko} {k} {kod}", k
    if wzor == 1:
        return "cyrkon", f"{nazwisko} {k}{kod.upper()}", k
    if wzor == 2:
        return "cyrkon", f"{nazwisko} {inicjal}. {k} {kod}", k
    if wzor == 3:
        return "cyrkon", f"{nazwisko} {inicjal}.{k}", k
    if wzor == 4:
        return "cyrkon", f"{nazwisko} {numer:04d}", k
    if wzor == 5:
        return "cyrkon", f"{k} {nazwisko} {imie}", k
    if wzor == 6:
        return "cyrkon", f"{nazwisko}_{k}_{kod}", k
    if wzor == 7:
        return "cyrkon", f"{nazwisko} {k} {imie}", k
    if wzor == 8:
        return "cyrkon", f"{NAZWISKA_NFD[int(rng.integers(len(NAZWISKA_NFD)))]} {k} {kod.upper()}", k
    if wzor == 9:
        return "prywatne", f"#{k} {nazwisko}", f"#{k}"
    raise ValueError(f"wzor {wzor}: dopuszczalne 0-{WZOROW - 1}")


def nazwa_pliku(nazwisko: str, nr: int, rng: np.random.Generator, data: str = "2026-11-16") -> str:
    """Nazwa pliku STL: exocad (korona albo most) albo prosta ``zab NN.stl``."""
    rodzaj = int(rng.integers(3))
    zab = ZEBY[(nr + int(rng.integers(len(ZEBY)))) % len(ZEBY)]
    baza = nazwisko.lower().replace(" ", "_")
    if rodzaj == 0:
        return f"{data}_{baza}-{zab}-crown_cad.stl"
    if rodzaj == 1:
        z = int(zab)
        return f"{data}_{baza}-{z}-{z + 1}-{z + 2}-bridge_cad.stl" if z % 10 <= 5 else f"{data}_{baza}-{z}-crown_cad.stl"
    return f"zab {zab}.stl"


def atrapa(rng: np.random.Generator):
    """Mala atrapa korony (ok. 800 trojkatow) o losowych wymiarach - kazde wywolanie daje inna zawartosc pliku."""
    W, L, H, g, amp = atrapy_koron.TYPY[("siekacz", "przedtrzonowy", "trzonowy")[int(rng.integers(3))]]
    sk = rng.uniform(0.9, 1.1, 3)
    return atrapy_koron.korona(W * sk[0], L * sk[1], H * sk[2], g, amp, n_theta=24, n_u=18, rng=rng)


def ustaw_czas(p: Path, kiedy: dt.datetime) -> None:
    ns = int(kiedy.timestamp() * 1e9)
    os.utime(p, ns=(ns, ns))


def zapisz_stl(m, plik: Path, kiedy: dt.datetime | None = None) -> Path:
    plik.parent.mkdir(parents=True, exist_ok=True)
    m.export(plik)
    if kiedy is not None:
        ustaw_czas(plik, kiedy)
        ustaw_czas(plik.parent, kiedy)
    return plik


def zbuduj(cel: Path, zlecen: int = 40, seed: int = 0, kiedy=None) -> list[ZlecenieTestowe]:
    """Buduje drzewo ``cel/Cyrkon/...`` i ``cel/Prywatne/...``; zwraca prawde (zlecenia z oczekiwana kuweta).

    ``kiedy``: czas modyfikacji plikow i folderow - ``datetime``, funkcja ``i -> datetime`` albo None (czas zapisu).
    Wzory nazw ida po kolei (zlecenie i ma wzor i % 10); numery kuwet sa rozne, wzory 4 i 7 maja numer < 1000.
    """
    cel = Path(cel)
    rng = np.random.default_rng(seed)
    duze = rng.permutation(np.arange(1000, 10000))
    male = rng.permutation(np.arange(1, 1000))
    prawda = []
    for i in range(zlecen):
        wzor = i % WZOROW
        numer = int(male[i]) if wzor in (4, 7) else int(duze[i])
        nazwisko = NAZWISKA[i % len(NAZWISKA)]
        zrodlo, folder, kuweta = nazwa_folderu(wzor, numer, nazwisko, rng)
        z = ZlecenieTestowe(zrodlo=zrodlo, folder=folder, kuweta=kuweta, wzor=wzor)
        chwila = kiedy(i) if callable(kiedy) else kiedy
        katalog = cel / ("Cyrkon" if zrodlo == "cyrkon" else "Prywatne") / folder
        for nr in range(1 + int(rng.integers(2))):
            nazwa = nazwa_pliku(nazwisko, nr, rng)
            while nazwa in z.pliki:
                nazwa = nazwa_pliku(nazwisko, nr + 1, rng)
            zapisz_stl(atrapa(rng), katalog / nazwa, chwila)
            z.pliki.append(nazwa)
        if chwila is not None:
            ustaw_czas(katalog, chwila)
        prawda.append(z)
    return prawda


def main() -> None:
    ap = argparse.ArgumentParser(description="Drzewo syntetyczne folderow zlecen (fikcyjne nazwy, male pliki STL).")
    ap.add_argument("--cel", type=Path, required=True, help="katalog, w ktorym powstana Cyrkon/ i Prywatne/")
    ap.add_argument("--zlecen", type=int, default=40)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--data", type=dt.datetime.fromisoformat, default=None, help="czas modyfikacji plikow (RRRR-MM-DDTGG:MM)")
    a = ap.parse_args()
    if a.zlecen < 0:
        ap.error("--zlecen musi byc >= 0")
    prawda = zbuduj(a.cel, a.zlecen, a.seed, a.data)
    print(f"zlecen: {len(prawda)} (prywatnych: {sum(z.zrodlo == 'prywatne' for z in prawda)}), "
          f"plikow STL: {sum(len(z.pliki) for z in prawda)}")


if __name__ == "__main__":
    main()
