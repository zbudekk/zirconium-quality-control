"""qc - stanowisko kontroli koron i mostow z cyrkonii."""

# Jeden watek BLAS. Wielowatkowy OpenBLAS (mnozenia `@` w numpy) wolany z watku Pythona rownolegle z
# open3d (OpenMP) w innym watku dawal access violation; z OPENBLAS_NUM_THREADS=1 crash znika. Program
# rownolegli sam (watki per praca), wiec BLAS nie musi. OMP_NUM_THREADS celowo bez zmian: steruje open3d.
# Zmienne dzialaja tylko, gdy ustawione przed pierwszym importem numpy; inaczej ogranicz_blas() przez ctypes.
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import ctypes  # noqa: E402
import glob  # noqa: E402
import sys  # noqa: E402

__version__ = "0.1.0"

_NAZWY_USTAW = ("scipy_openblas_set_num_threads64_", "scipy_openblas_set_num_threads",
                "openblas_set_num_threads64_", "openblas_set_num_threads")


def ogranicz_blas() -> bool:
    """Ustawia 1 watek OpenBLAS w bibliotece juz zaladowanego numpy (ctypes).

    True = ustawiono; False = numpy jeszcze nie zaladowane (wystarcza zmienne srodowiska) albo
    biblioteka/funkcja niedostepna na platformie.
    """
    numpy = sys.modules.get("numpy")
    if numpy is None or not getattr(numpy, "__file__", None):
        return False
    baza = os.path.dirname(numpy.__file__)
    sciezki = []
    for wzorzec in (os.path.join(baza, os.pardir, "numpy.libs", "*openblas*"),
                    os.path.join(baza, ".libs", "*openblas*")):
        sciezki += glob.glob(wzorzec)
    for sciezka in sciezki:
        try:
            biblioteka = ctypes.CDLL(sciezka)
        except OSError:
            continue
        for nazwa in _NAZWY_USTAW:
            funkcja = getattr(biblioteka, nazwa, None)
            if funkcja is not None:
                funkcja(1)
                return True
    return False


ogranicz_blas()
