"""Wspolne narzedzia open3d: globalny seed generatora losowego pod blokada (plate, match)."""

import threading
from contextlib import contextmanager

import open3d as o3d

BLOKADA_SEED = threading.Lock()  # open3d.utility.random.seed jest globalny dla procesu


@contextmanager
def ziarno(n: int):
    """Ustawia seed open3d i trzyma blokade do konca bloku (RANSAC open3d powtarzalny i bezpieczny dla watkow)."""
    with BLOKADA_SEED:
        o3d.utility.random.seed(int(n))
        yield
