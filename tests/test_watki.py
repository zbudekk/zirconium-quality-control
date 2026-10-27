"""Testy pracy wielowatkowej: jeden watek BLAS po imporcie qc, inspekcja rownolegle z wyrownaniem plytki.

Wielowatkowy OpenBLAS (mnozenia `@` w numpy) wolany z watku Pythona rownolegle z open3d (OpenMP) w
innym watku dawal access violation. Pakiet qc przy imporcie ustawia jeden watek BLAS (qc.ogranicz_blas).
"""

import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest

from qc.ustawienia import katalog_repo, wczytaj

# Kod podprocesu: liczba watkow OpenBLAS z biblioteki numpy przez ctypes ("brak" gdy niedostepna).
_KOD_LICZBY_WATKOW = r"""
import ctypes, glob, os, sys
import numpy
baza = os.path.dirname(numpy.__file__)
wzorce = [os.path.join(baza, "..", "numpy.libs", "*openblas*"), os.path.join(baza, ".libs", "*openblas*"),
          os.path.join(baza, "..", "numpy.libs", "*.so*"), os.path.join(baza, ".libs", "*.so*")]
nazwy = ["scipy_openblas_get_num_threads64_", "scipy_openblas_get_num_threads", "openblas_get_num_threads64_",
         "openblas_get_num_threads"]
wynik = "brak"
for wzorzec in wzorce:
    for sciezka in glob.glob(wzorzec):
        try:
            biblioteka = ctypes.CDLL(sciezka)
        except OSError:
            continue
        for nazwa in nazwy:
            funkcja = getattr(biblioteka, nazwa, None)
            if funkcja is not None:
                wynik = str(funkcja())
                break
        if wynik != "brak":
            break
    if wynik != "brak":
        break
print("WATKI", wynik)
print("ENV", os.environ.get("OPENBLAS_NUM_THREADS"))
"""


def _podproces(przed):
    env = {k: v for k, v in os.environ.items() if k not in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")}
    kod = przed + "\n" + _KOD_LICZBY_WATKOW
    wynik = subprocess.run([sys.executable, "-c", kod], cwd=katalog_repo(), env=env, capture_output=True,
                           text=True, timeout=120)
    assert wynik.returncode == 0, wynik.stderr
    linie = dict(linia.split(" ", 1) for linia in wynik.stdout.splitlines() if " " in linia)
    return linie["WATKI"], linie["ENV"], wynik.stdout


def test_blas_ograniczony():
    """Import qc przed numpy: zmienna srodowiska i biblioteka OpenBLAS ustawione na 1 watek."""
    watki, env, wyjscie = _podproces("import qc")
    assert env == "1", wyjscie
    if watki != "brak":
        assert watki == "1", wyjscie


def test_blas_ograniczony_po_numpy():
    """numpy zaimportowane przed qc: ogranicz_blas() ustawia 1 watek przez ctypes."""
    watki, _, wyjscie = _podproces("import numpy\nimport qc\nassert qc.ogranicz_blas() in (True, False)")
    if watki == "brak":
        pytest.skip("funkcja openblas_get_num_threads niedostepna na tej platformie")
    assert watki == "1", wyjscie


def test_watki_inspect_rownolegle(pula30):
    """4 watki x 3 inspekcje rownolegle z wyrownaniem plytki 6+1 w 2 watkach: bez wyjatku, wyniki jak sekwencyjnie."""
    import qc.inspect as inspect
    import qc.plate as plate
    from qc import uklad as modul_ukladu
    from qc.syntetyka import plytka, prace
    from qc.syntetyka import skan as modul_skan

    ustawienia = wczytaj()
    rng = np.random.default_rng(7)
    zadania = []
    for i, ind in enumerate(rng.choice(len(pula30), size=12, replace=False)):
        projekt = pula30[int(ind)].siatka
        fragment, prawda = modul_skan.skan_pracy(projekt, ziarno=7000 + i, ubytki=2)
        zadania.append((fragment, projekt, prawda.T_projekt_do_skanu))

    wieczorna = modul_ukladu.wczytaj(katalog_repo() / "modele" / "uklad_gniazd_wieczorna.json")
    pula = list(pula30) + [prace.Projekt(id="most-01", rodzaj="most", siatka=prace.most(1, 4, 0.1))]
    rozm = plytka.rozmiesc(wieczorna, pula, 6, 1, ziarno=21)
    siatka_plytki, _ = plytka.skan_plytki(wieczorna, 2, rozm, ziarno=21, szum_mm=0.02, T_plytki="losowa")

    def inspekcja(z):
        w = inspect.sprawdz(*z, ustawienia)
        return (repr(w.ubytki), repr(w.poprawki), repr(w.inne), w.drgniecie, np.asarray(w.mapa).copy())

    def wyrownanie():
        return plate.wyrownaj(siatka_plytki, wieczorna, ustawienia).T_skan_do_plytki.copy()

    sekw_insp = [inspekcja(z) for z in zadania]
    sekw_wyr = wyrownanie()

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=6) as wykonawca:
        przyszle_wyr = [wykonawca.submit(lambda: [wyrownanie() for _ in range(3)]) for _ in range(2)]
        przyszle_insp = [wykonawca.submit(lambda k=k: [inspekcja(z) for z in zadania[3 * k:3 * k + 3]])
                         for k in range(4)]
        rown_wyr = [T for p in przyszle_wyr for T in p.result()]
        rown_insp = [w for p in przyszle_insp for w in p.result()]
    czas = time.perf_counter() - start

    for T in rown_wyr:
        np.testing.assert_allclose(T, sekw_wyr, atol=1e-9)
    assert len(rown_insp) == len(sekw_insp)
    for a, b in zip(rown_insp, sekw_insp):
        assert a[:4] == b[:4]
        np.testing.assert_array_equal(a[4], b[4])
    print(f"czas rownolegle: {czas:.1f} s")
