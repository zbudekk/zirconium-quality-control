"""Wspolne fixtures testow na danych syntetycznych.

Importy modulow qc.syntetyka i open3d sa wewnatrz fixtures, zeby blad jednej czesci
nie blokowal zbierania testow pozostalych czesci.
"""

import os

# Jeden watek BLAS przed pierwszym importem numpy (pytest laduje conftest przed qc); patrz qc/__init__.py.
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np  # noqa: E402
import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "wolne: test trwajacy ponad 20 s")


@pytest.fixture
def ziarno():
    return 42


@pytest.fixture(scope="session")
def projekt_korony():
    from qc.syntetyka import prace

    return prace.korona(42)


@pytest.fixture(scope="session")
def projekt_mostu():
    from qc.syntetyka import prace

    return prace.most(42)


@pytest.fixture(scope="session")
def pula30():
    from qc.syntetyka import prace

    return prace.pula_projektow(30, 1)


@pytest.fixture
def skan(ziarno):
    """Fabryka: skan(projekt, **kw) -> (Trimesh, PrawdaPracy)."""
    from qc.syntetyka import skan as modul_skan

    def _skan(projekt, **kw):
        kw.setdefault("ziarno", ziarno)
        return modul_skan.skan_pracy(projekt, **kw)

    return _skan


def odleglosci_ze_znakiem(a, b):
    """Odleglosc ze znakiem wierzcholkow a (Trimesh albo tablica (N,3)) od powierzchni b.

    Ujemna = pod powierzchnia b (wewnatrz bryly) = brak materialu.
    """
    import open3d as o3d

    punkty = np.asarray(getattr(a, "vertices", a), dtype=np.float32)
    scena = o3d.t.geometry.RaycastingScene()
    scena.add_triangles(
        o3d.core.Tensor(np.asarray(b.vertices, dtype=np.float32)),
        o3d.core.Tensor(np.asarray(b.faces, dtype=np.uint32)),
    )
    wynik = scena.compute_signed_distance(o3d.core.Tensor(punkty))
    return wynik.numpy().astype(np.float64)


@pytest.fixture
def odleglosci():
    """Fabryka: odleglosci(a, b) -> np.ndarray odleglosci ze znakiem wierzcholkow a od b."""
    return odleglosci_ze_znakiem
