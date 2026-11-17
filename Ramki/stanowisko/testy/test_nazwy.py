"""nazwy.py (E3-A4): nazwa folderu zlecenia -> numer kuwety, normalizacja nazw, zeby i typ z nazwy pliku STL.

Kryterium 1 planu etapu 3 (sekcja 4.1, E3-A4): kuweta poprawna w 40 z 40 zlecen drzewa syntetycznego (wzory nazw
z planu). Regula z planu wdrozenia v2 ("Dane i integracje"): numer kuwety = ciag 1-4 cyfr, zera wiodace
normalizowane (3 = 03 = 003); "#1234" = zlecenie prywatne. Wszystkie nazwy sa FIKCYJNE.
"""
from __future__ import annotations

import unicodedata

import numpy as np
import pytest

import drzewo_syntetyczne as D
from stanowisko import nazwy as N


@pytest.mark.parametrize("folder, kuweta, prywatne", [
    ("Testowski 3263 zs", "3263", False),
    ("Testowski 1784PG", "1784", False),          # kod sklejony z numerem
    ("Testowski 1784 PG", "1784", False),
    ("Testowski J. 3263 zs", "3263", False),      # inicjal z kropka przed numerem
    ("Testowski J.3263", "3263", False),
    ("Testowski 0041", "41", False),              # zera wiodace
    ("03 Probna", "3", False),
    ("3263 Testowa Anna", "3263", False),         # numer na poczatku (dane A1)
    ("Testowski_88_zs", "88", False),
    ("  Testowski   0912  ", "912", False),
    ("Nowak-Testowa 7", "7", False),
    ("Testowski 12 zs 4567", "12", False),        # pierwszy numer
    ("Testowski 12345 3263", "3263", False),      # liczba 5-cyfrowa to nie kuweta
    ("Testowski 3263 ZS1", "3263", False),
    ("PG1784 Testowski", None, False),            # litery przed cyframi: to nie numer kuwety
    ("Testowski", None, False),
    ("Testowski 12345", None, False),
    ("#1234", "#1234", True),
    ("#1234 Testowski", "#1234", True),
    ("# 1234 Testowski", "#1234", True),
    ("Testowski #0123", "#0123", True),           # numer zlecenia prywatnego bez zmian (to nie kuweta)
    ("2026-11-16 Testowski 3263", "3263", False),  # data w nazwie nie jest kuweta
    ("16.11.2026 Testowski 3263 zs", "3263", False),
    ("Testowski 3263 2026_11_16", "3263", False),
])
def test_kuweta_z_nazwy_folderu(folder, kuweta, prywatne):
    z = N.rozbierz(folder)
    assert z.kuweta == kuweta
    assert z.prywatne is prywatne
    assert N.kuweta(folder) == kuweta


def test_kryterium1_kuweta_w_40_z_40_wzorow_drzewa():
    rng = np.random.default_rng(5)
    duze = rng.permutation(np.arange(1000, 10000))
    male = rng.permutation(np.arange(1, 1000))
    trafione, wzory = 0, set()
    for i in range(40):
        wzor = i % D.WZOROW
        numer = int(male[i]) if wzor in (4, 7) else int(duze[i])
        _, folder, oczekiwana = D.nazwa_folderu(wzor, numer, D.NAZWISKA[i % len(D.NAZWISKA)], rng)
        trafione += N.rozbierz(folder).kuweta == oczekiwana
        wzory.add(wzor)
    assert (trafione, len(wzory)) == (40, 10)


def test_nazwy_nfd_i_nfc_daja_te_sama_kuwete_i_normalizacje():
    nfd = unicodedata.normalize("NFD", "Wi\u015bniewska 003 Zs")
    nfc = unicodedata.normalize("NFC", nfd)
    assert nfd != nfc
    assert N.rozbierz(nfd).kuweta == N.rozbierz(nfc).kuweta == "3"
    assert N.znormalizuj(nfd) == N.znormalizuj(nfc) == "wi\u015bniewska 3 zs"


def test_znormalizuj():
    zn = N.znormalizuj
    assert zn("  Testowski   0041 ZS ") == "testowski 41 zs"
    assert zn("Testowski 1784PG") == zn("Testowski 1784 PG") == "testowski 1784 pg"
    assert zn("007 Probna") == "7 probna"
    assert zn("0") == "0"
    assert zn("#0123 Testowski") == "#123 testowski"


def test_rozbierz_zwraca_tylko_kuwete_i_normalizacje_bez_nazwiska():
    z = N.rozbierz("Testowski 3263 zs")
    assert z.folder_norm == "testowski 3263 zs"
    assert not hasattr(z, "nazwisko")


@pytest.mark.parametrize("plik, zeby, typ", [
    ("2026-11-16_testowski-14-crown_cad.stl", "14", "korona"),
    ("2026-11-16_testowski-24-25-26-bridge_cad.stl", "24-25-26", "most"),
    ("2026-11-02_testowski-2026-11-02_testowski-11-12-waxup_slm_cad.stl", "11-12", "waxup"),
    ("2026-11-16_testowski-46-tooth_without_abutment_cad.stl", "46", "bez_lacznika"),
    ("zab 46.stl", "46", "nieznany"),
    ("Testowski_3263_47.stl", "47", "nieznany"),
    ("11.STL", "11", "nieznany"),
    ("3263.stl", None, "nieznany"),
    ("korona.stl", None, "nieznany"),
    ("19.stl", None, "nieznany"),
    ("136.stl", None, "nieznany"),
])
def test_zeby_i_typ_z_nazwy_pliku(plik, zeby, typ):
    assert N.zeby_i_typ(plik) == (zeby, typ)


def test_klucz_pliku_do_porownan():
    assert N.klucz_pliku("  Testowski 3263\\Zab 46.STL ") == "testowski 3263/zab 46.stl"
    nfd = unicodedata.normalize("NFD", "\u017b\u00f3\u0142ty.stl")
    assert N.klucz_pliku(nfd) == N.klucz_pliku(unicodedata.normalize("NFC", nfd))
    assert N.klucz_pliku("/a/b.stl/") == "a/b.stl"


def test_normalizuj_krazek():
    assert N.normalizuj_krazek(" k-1101 ") == "K-1101"
    assert N.normalizuj_krazek("b 2311  05") == "B 2311 05"
    assert N.normalizuj_krazek("") is None
    assert N.normalizuj_krazek(None) is None
