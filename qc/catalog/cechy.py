"""Cechy geometryczne siatki do wstepnego filtra kandydatow: objetosc, pole, wymiary PCA, rozklad D2."""

from dataclasses import dataclass, replace

import numpy as np
import trimesh

KOSZYKI = 64
PARY = 20_000
PUNKTY = 4_000
ZAKRES_D2 = 1.05  # x przekatna wymiarow


@dataclass(eq=False)
class Cechy:
    objetosc_mm3: float | None
    pole_mm2: float
    wymiary_mm: np.ndarray  # (3,) malejaco
    d2: np.ndarray  # (64,) suma 1

    def przeskaluj(self, k: float) -> "Cechy":
        """Cechy siatki przeskalowanej o k (d2 jest wzgledny wobec wymiarow, wiec bez zmian)."""
        return replace(self,
                       objetosc_mm3=None if self.objetosc_mm3 is None else self.objetosc_mm3 * k ** 3,
                       pole_mm2=self.pole_mm2 * k ** 2,
                       wymiary_mm=self.wymiary_mm * k,
                       d2=self.d2.copy())


def wymiary(punkty: np.ndarray) -> np.ndarray:
    """Rozpietosc punktow wzdluz osi glownych (PCA przez eigh), malejaco."""
    p = np.asarray(punkty, dtype=np.float64)
    p = p - p.mean(axis=0)
    _, osie = np.linalg.eigh(p.T @ p / len(p))
    rzuty = p @ osie
    return np.sort(rzuty.max(axis=0) - rzuty.min(axis=0))[::-1]


def policz(siatka: trimesh.Trimesh, ziarno: int = 0) -> Cechy:
    """Cechy siatki; objetosc tylko dla bryly zamknietej (is_watertight), inaczej None."""
    rng = np.random.default_rng(ziarno)
    wym = wymiary(siatka.vertices)
    punkty, _ = trimesh.sample.sample_surface(siatka, PUNKTY, seed=rng)
    a = rng.integers(0, len(punkty), PARY)
    b = rng.integers(0, len(punkty), PARY)
    odl = np.linalg.norm(punkty[a] - punkty[b], axis=1)
    hist, _ = np.histogram(odl, bins=KOSZYKI, range=(0.0, ZAKRES_D2 * float(np.linalg.norm(wym))))
    d2 = hist / max(hist.sum(), 1)
    objetosc = float(siatka.volume) if siatka.is_watertight else None
    return Cechy(objetosc_mm3=objetosc, pole_mm2=float(siatka.area), wymiary_mm=wym, d2=d2)


def odleglosc(a: Cechy, b: Cechy) -> float:
    """0,5 x L1(d2) + 0,5 x max wzgledna roznica wymiarow; 0 = identyczne."""
    l1 = float(np.abs(a.d2 - b.d2).sum())
    wzgledna = np.abs(a.wymiary_mm - b.wymiary_mm) / np.maximum(np.maximum(a.wymiary_mm, b.wymiary_mm), 1e-9)
    return 0.5 * l1 + 0.5 * float(wzgledna.max())


def pasuje(skan: Cechy, projekt: Cechy, k: float, ustawienia) -> bool:
    """Czy skan moze byc projektem przeskalowanym o k (objetosc pomijana, gdy ktorejs brak)."""
    d = ustawienia.dopasowanie
    oczekiwane = projekt.przeskaluj(k)
    if skan.objetosc_mm3 is not None and oczekiwane.objetosc_mm3 is not None:
        if abs(skan.objetosc_mm3 - oczekiwane.objetosc_mm3) > d.tolerancja_objetosci * oczekiwane.objetosc_mm3:
            return False
    return bool(np.all(np.abs(skan.wymiary_mm - oczekiwane.wymiary_mm) <= d.tolerancja_wymiarow_mm))
