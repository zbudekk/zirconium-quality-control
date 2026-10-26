"""Mapa odchylek fragmentu skanu od projektu (odleglosc ze znakiem, open3d)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import open3d as o3d

# brzeg projektu = pierscien |z| < PAS_Z_BRZEGU_MM w ukladzie projektu
PAS_Z_BRZEGU_MM = 0.3


@dataclass
class Mapa:
    """Odchylki wierzcholkow fragmentu od projektu (uklad fragmentu)."""

    punkty: np.ndarray  # (N, 3)
    odleglosci: np.ndarray  # (N,) ujemna = pod powierzchnia projektu = brak materialu
    normalne_projektu: np.ndarray  # (N, 3) normalna najblizszego trojkata projektu
    przy_brzegu: np.ndarray  # (N,) bool: w pasie ubytki.pas_brzegu_mm od krzywej brzegu
    sciany: np.ndarray | None = None  # (M, 3) sciany fragmentu: sasiedztwo do wygladzania i skladowych


def _przeksztalc(punkty: np.ndarray, T: np.ndarray) -> np.ndarray:
    T = np.asarray(T, dtype=np.float64).reshape(4, 4)
    return punkty @ T[:3, :3].T + T[:3, 3]


def _tensor(a, typ) -> o3d.core.Tensor:
    return o3d.core.Tensor(np.ascontiguousarray(a, dtype=typ))


def odleglosc_od_zbioru(punkty: np.ndarray, zbior: np.ndarray) -> np.ndarray:
    """Odleglosc kazdego punktu od najblizszego punktu zbioru (open3d nns)."""
    if len(zbior) == 0:
        return np.full(len(punkty), np.inf)
    nns = o3d.core.nns.NearestNeighborSearch(_tensor(zbior, np.float32))
    nns.knn_index()
    _, odl2 = nns.knn_search(_tensor(punkty, np.float32), 1)
    return np.sqrt(odl2.numpy()[:, 0].astype(np.float64))


def mapa_odchylek(fragment, projekt, T_projekt_do_fragmentu, ustawienia) -> Mapa:
    """Odleglosc ze znakiem wierzcholkow fragmentu od powierzchni projektu przeniesionego przez T.

    Znak z normalnej najblizszego trojkata (jedna sciezka dla siatek zamknietych i otwartych:
    mosty, skany z dziurami).
    """
    punkty = np.asarray(fragment.vertices, dtype=np.float64)
    v_proj = np.asarray(projekt.vertices, dtype=np.float64)
    v_po_T = _przeksztalc(v_proj, T_projekt_do_fragmentu)
    sciany = np.asarray(projekt.faces, dtype=np.int64)

    scena = o3d.t.geometry.RaycastingScene()
    scena.add_triangles(_tensor(v_po_T, np.float32), _tensor(sciany, np.uint32))
    wynik = scena.compute_closest_points(_tensor(punkty, np.float32))
    najblizsze = wynik["points"].numpy().astype(np.float64)
    trojkaty = wynik["primitive_ids"].numpy().astype(np.int64)

    a, b, c = (v_po_T[sciany[trojkaty, i]] for i in range(3))
    normalne = np.cross(b - a, c - a)
    normalne /= np.linalg.norm(normalne, axis=1, keepdims=True) + 1e-15
    roznica = punkty - najblizsze
    odl = np.linalg.norm(roznica, axis=1)
    znak = np.where(np.einsum("ij,ij->i", roznica, normalne) < 0.0, -1.0, 1.0)

    brzeg = v_po_T[np.abs(v_proj[:, 2]) < PAS_Z_BRZEGU_MM]
    przy_brzegu = odleglosc_od_zbioru(punkty, brzeg) <= float(ustawienia.ubytki.pas_brzegu_mm)

    return Mapa(punkty=punkty, odleglosci=znak * odl, normalne_projektu=normalne, przy_brzegu=przy_brzegu,
                sciany=np.asarray(fragment.faces, dtype=np.int64))
