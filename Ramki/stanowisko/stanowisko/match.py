"""match — który projekt STL to jest: identyfikacja fragmentu skanu w puli projektów.

Wejście: fragment (punkty z normalnymi w układzie płytki, z ``plate``), pula projektów
(folder(y) STL, współczynnik skurczu). Wyjście: ranking kandydatów z pokryciem
(udział punktów fragmentu w odległości ≤ ``[match] odleglosc_max_mm`` od projektu),
transformacją projekt → płytka i pewnością (różnica pokrycia 1. i 2. kandydata).

Kroki na parę fragment–kandydat:
1. filtr (cechy z katalogu × współczynnik): wymiary obrysu xy i wysokość ± (`filtr_wymiar_mm` albo
   `filtr_wymiar_udzial`), objętość otoczki wypukłej ± `filtr_objetosc_udzial`;
2. zgrubne dopasowanie: FPFH + RANSAC (Open3D) — a gdy pokrycie po nim jest słabe, przegląd obrotów
   wokół z co 30° od środków (prace leżą brzegiem do góry, więc różnią się głównie obrotem wokół z);
3. ICP punkt–płaszczyzna (progi 0,6 → 0,2 → 0,08 mm);
4. ocena: odległość każdego punktu fragmentu do siatki projektu (Open3D RaycastingScene) → pokrycie,
   RMS punktów w pokryciu, pokrycie odwrotne (punkty projektu blisko fragmentu).

Progi w ``ustawienia.toml`` [match]; nic nie jest strojone w kodzie.
"""
from __future__ import annotations

import math
import time
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import open3d as o3d
import trimesh
from scipy.spatial import cKDTree

from . import katalog as K
from . import synth as S

VOXEL_FPFH = 0.4  # mm: siatka do cech FPFH (korona 6–12 mm → 1–3 tys. punktów)
VOXEL_ICP = 0.15  # mm: punkty fragmentu do ICP i oceny
VOXEL_ZGRUBNE = 0.5  # mm: chmury do przeglądu obrotów (szybkie ICP)
PUNKTY_KANDYDATA = 40000  # próbka z siatki projektu (ICP cel)
KROK_OBROTU_DEG = 45.0
KANDYDATOW_OBROTU = 4  # najwyżej tyle obrotów zgrubnych (remisujących) dostaje pełne ICP i dokładne pokrycie
REMIS_OBROTU = 0.02  # obroty o pokryciu zgrubnym w tej odległości od najlepszego liczą się jako remis
STATUSY = ("zielony", "zolty", "szary")


@dataclass
class Kandydat:
    id: str
    zeby: list[str]
    typ: str
    pokrycie: float = 0.0  # udział punktów fragmentu ≤ odleglosc_max od projektu
    rms_mm: float = math.inf  # RMS odległości punktów w pokryciu
    pokrycie_odwrotne: float = 0.0  # udział punktów projektu ≤ 2·odleglosc_max od fragmentu
    transformacja: list | None = None  # 4×4: (projekt × współczynnik) → układ płytki
    metoda: str = ""  # ransac | obroty | filtr
    filtr_ok: bool = True
    powod_filtru: str = ""


@dataclass
class WynikDopasowania:
    gniazdo: int | None
    kandydaci: list[Kandydat]  # posortowani malejąco po pokryciu
    pewnosc: float  # pokrycie 1. − pokrycie 2.
    status: str  # zielony | zolty | szary
    czas_s: float
    liczba_punktow: int
    uwagi: list[str] = field(default_factory=list)

    @property
    def najlepszy(self) -> Kandydat | None:
        return self.kandydaci[0] if self.kandydaci else None


# ----------------------------------------------------------------------------
# pula projektów
# ----------------------------------------------------------------------------
def _chmura(P, N=None) -> o3d.geometry.PointCloud:
    pc = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.ascontiguousarray(P, dtype=np.float64)))
    if N is not None:
        pc.normals = o3d.utility.Vector3dVector(np.ascontiguousarray(N, dtype=np.float64))
    return pc


def _fpfh(pc: o3d.geometry.PointCloud, voxel: float) -> tuple[o3d.geometry.PointCloud, o3d.pipelines.registration.Feature]:
    pd = pc.voxel_down_sample(voxel)
    if not pd.has_normals():
        pd.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=voxel * 2, max_nn=30))
    f = o3d.pipelines.registration.compute_fpfh_feature(pd, o3d.geometry.KDTreeSearchParamHybrid(radius=voxel * 5, max_nn=100))
    return pd, f


class Projekt:
    """Projekt w puli: siatka × współczynnik, brzegiem do góry, wyśrodkowana (xy: środek obrysu, z: brzeg na 0)."""

    def __init__(self, plik: Path, wspolczynnik: float, orientacja: str = "auto", seed: int = 0):
        self.plik = Path(plik)
        self.id = S.skrot_pliku(self.plik)
        m = S.wczytaj_projekt(self.plik)
        if m is None:
            raise ValueError(f"nie da się wczytać projektu {self.id}")
        self.cechy = K.cechy(m, self.plik.name)
        self.cechy.id = self.id
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            O = S.orientacja_brzegiem_do_gory(m, orientacja, self.plik.name)
        m2 = m.copy()
        m2.apply_transform(O @ trimesh.transformations.scale_matrix(wspolczynnik))
        c = np.array([m2.bounds[:, 0].mean(), m2.bounds[:, 1].mean(), m2.bounds[1, 2]])
        self.T0 = trimesh.transformations.translation_matrix(-c) @ O  # (projekt × w) → układ puli
        m2.apply_translation(-c)
        self.siatka = m2
        self.wspolczynnik = wspolczynnik
        _, boki = trimesh.bounds.oriented_bounds_2D(m2.vertices[:, :2])
        self.obrys_xy = sorted(float(b) for b in boki)
        self.wysokosc = float(m2.extents[2])
        self.hull = float(m2.convex_hull.volume)
        pts, fid = trimesh.sample.sample_surface(m2, PUNKTY_KANDYDATA, seed=seed)
        self.chmura = _chmura(pts, m2.face_normals[fid])
        self.chmura_fpfh, self.fpfh = _fpfh(self.chmura, VOXEL_FPFH)
        self.chmura_zgrubna = self.chmura.voxel_down_sample(VOXEL_ZGRUBNE)
        mo = o3d.t.geometry.TriangleMesh(o3d.core.Tensor(np.asarray(m2.vertices, dtype=np.float32)), o3d.core.Tensor(np.asarray(m2.faces, dtype=np.int32)))
        self.scena = o3d.t.geometry.RaycastingScene()
        self.scena.add_triangles(mo)
        self.drzewo = cKDTree(pts)

    def odleglosci(self, P: np.ndarray) -> np.ndarray:
        return self.scena.compute_distance(o3d.core.Tensor(np.ascontiguousarray(P, dtype=np.float32))).numpy()


class Pula:
    def __init__(self, foldery: list[Path] | Path, wspolczynnik: float, orientacja: str = "auto"):
        foldery = [Path(f) for f in (foldery if isinstance(foldery, (list, tuple)) else [foldery])]
        t0 = time.time()
        self.projekty: dict[str, Projekt] = {}
        self.pominiete = 0
        for f in foldery:
            for p in S.pliki_projektow(f):
                try:
                    pr = Projekt(p, wspolczynnik, orientacja)
                except ValueError:
                    self.pominiete += 1
                    continue
                self.projekty[pr.id] = pr
        self.wspolczynnik = wspolczynnik
        self.czas_s = round(time.time() - t0, 2)

    def __len__(self) -> int:
        return len(self.projekty)


# ----------------------------------------------------------------------------
# fragment
# ----------------------------------------------------------------------------
@dataclass
class FragmentDoDopasowania:
    P: np.ndarray  # punkty po voxelizacji 0,15 (układ płytki)
    N: np.ndarray
    c: np.ndarray  # środek (xy środek obrysu, z brzeg) — jak w Projekt
    obrys_xy: list[float]
    wysokosc: float
    hull: float
    chmura: o3d.geometry.PointCloud
    chmura_fpfh: o3d.geometry.PointCloud
    fpfh: o3d.pipelines.registration.Feature
    chmura_zgrubna: o3d.geometry.PointCloud

    @classmethod
    def z_punktow(cls, P: np.ndarray, N: np.ndarray) -> FragmentDoDopasowania:
        pc = _chmura(P, N).voxel_down_sample(VOXEL_ICP)
        Pd, Nd = np.asarray(pc.points), np.asarray(pc.normals)
        nrm = np.linalg.norm(Nd, axis=1, keepdims=True)
        Nd = np.where(nrm > 1e-9, Nd / np.maximum(nrm, 1e-9), 0.0)
        pc.normals = o3d.utility.Vector3dVector(Nd)
        lo, hi = Pd.min(0), Pd.max(0)
        c = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, hi[2]])
        _, boki = trimesh.bounds.oriented_bounds_2D(Pd[:, :2])
        hull = float(trimesh.convex.convex_hull(Pd).volume) if len(Pd) >= 4 else 0.0
        pd, f = _fpfh(pc, VOXEL_FPFH)
        return cls(Pd, Nd, c, sorted(float(b) for b in boki), float(hi[2] - lo[2]), hull, pc, pd, f, pc.voxel_down_sample(VOXEL_ZGRUBNE))


# ----------------------------------------------------------------------------
# dopasowanie pary
# ----------------------------------------------------------------------------
def filtr(fr: FragmentDoDopasowania, pr: Projekt, ust: dict) -> tuple[bool, str]:
    """Czy wymiary i objętość fragmentu pasują do projektu (× współczynnik już w puli)."""
    m = ust["match"]
    tol = lambda v: max(m["filtr_wymiar_mm"], m["filtr_wymiar_udzial"] * v)  # noqa: E731
    for nazwa, a, b in (("długość", fr.obrys_xy[1], pr.obrys_xy[1]), ("szerokość", fr.obrys_xy[0], pr.obrys_xy[0]), ("wysokość", fr.wysokosc, pr.wysokosc)):
        if abs(a - b) > tol(b):
            return False, f"{nazwa} {a:.1f} vs {b:.1f} mm"
    if pr.hull > 0 and abs(fr.hull - pr.hull) > m["filtr_objetosc_udzial"] * pr.hull:
        return False, f"objętość otoczki {fr.hull:.0f} vs {pr.hull:.0f} mm³"
    return True, ""


def _icp(zr: o3d.geometry.PointCloud, cel: o3d.geometry.PointCloud, T: np.ndarray, progi=(0.6, 0.2, 0.08), iteracje: int = 40) -> np.ndarray:
    est = o3d.pipelines.registration.TransformationEstimationPointToPlane()
    for prog in progi:
        w = o3d.pipelines.registration.registration_icp(zr, cel, prog, T, est, o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=iteracje))
        T = np.asarray(w.transformation)
    return T


def ocena(fr: FragmentDoDopasowania, pr: Projekt, T: np.ndarray, odl_max: float) -> tuple[float, float, float]:
    """(pokrycie, rms, pokrycie odwrotne) dla T: fragment → układ puli projektu."""
    P = fr.P @ T[:3, :3].T + T[:3, 3]
    d = pr.odleglosci(P)
    w = d <= odl_max
    pok = float(w.mean())
    rms = float(np.sqrt(np.mean(d[w] ** 2))) if w.any() else math.inf
    dd, _ = cKDTree(P).query(np.asarray(pr.chmura.points)[::4], k=1, distance_upper_bound=2 * odl_max)
    return pok, rms, float(np.isfinite(dd).mean())


def zgrubne_ransac(fr: FragmentDoDopasowania, pr: Projekt, seed: int = 0) -> np.ndarray | None:
    o3d.utility.random.seed(seed)
    dist = VOXEL_FPFH * 1.5
    w = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        fr.chmura_fpfh, pr.chmura_fpfh, fr.fpfh, pr.fpfh, True, dist,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False), 4,
        [o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(0.9), o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(dist)],
        o3d.pipelines.registration.RANSACConvergenceCriteria(100000, 0.999),
    )
    if w.fitness < 0.2:
        return None
    return np.asarray(w.transformation)


def zgrubne_obroty(fr: FragmentDoDopasowania, pr: Projekt, odl_max: float, krok_deg: float = KROK_OBROTU_DEG) -> tuple[np.ndarray, float]:
    """Środki na siebie (xy środek obrysu, z brzeg), obrót wokół z co ``krok_deg``, krótkie ICP na chmurach
    0,5 mm, ocena pokryciem przy 4·odl_max na chmurze zgrubnej; obroty remisujące z najlepszym (REMIS_OBROTU, najwyżej
    KANDYDATOW_OBROTU) dostają pełne ICP i dokładne pokrycie (korona prawie okrągła: przy 0,2 mm wszystkie obroty dają
    0,998, a przy 0,05 mm 0° → 0,90, 180° → 0,53 — P3a, seedy 21/27/29 na atrapach). Zwraca najlepszą transformację i jej pokrycie."""
    kandydaci: list[tuple[float, np.ndarray]] = []
    Pz = np.asarray(fr.chmura_zgrubna.points)
    for k in range(int(round(360 / krok_deg))):
        a = math.radians(k * krok_deg)
        R = trimesh.transformations.rotation_matrix(a, [0, 0, 1])
        T = R @ trimesh.transformations.translation_matrix(-fr.c)  # fragment → środek → obrót (pula ma środek w 0)
        T = _icp(fr.chmura_zgrubna, pr.chmura_zgrubna, T, progi=(1.0, 0.4), iteracje=12)
        d = pr.odleglosci(Pz @ T[:3, :3].T + T[:3, 3])
        kandydaci.append((float((d <= 4 * odl_max).mean()), T))
    prog = max(kt[0] for kt in kandydaci) - REMIS_OBROTU  # remis: obroty prawie równe zgrubnie (korona prawie okrągła) — rozstrzyga dokładne pokrycie
    remis = [kt for kt in kandydaci if kt[0] >= prog]  # w kolejności kątów
    if len(remis) > KANDYDATOW_OBROTU:  # równomiernie po kącie, nie „pierwsze z brzegu” (różnice 1e-4 ustawiałyby same złe obroty)
        remis = [remis[int(round(i * len(remis) / KANDYDATOW_OBROTU))] for i in range(KANDYDATOW_OBROTU)]
    najl, najl_pok = None, -1.0
    for _, T0 in remis:
        T = _icp(fr.chmura, pr.chmura, T0)
        pok, _, _ = ocena(fr, pr, T, odl_max)
        if pok > najl_pok:
            najl, najl_pok = T, pok
    return najl, najl_pok


def dopasuj_pare(fr: FragmentDoDopasowania, pr: Projekt, ust: dict, seed: int = 0) -> Kandydat:
    m = ust["match"]
    odl_max = m["odleglosc_max_mm"]
    k = Kandydat(id=pr.id, zeby=pr.cechy.zeby, typ=pr.cechy.typ)
    ok, powod = filtr(fr, pr, ust)
    if not ok:
        k.filtr_ok, k.powod_filtru, k.metoda = False, powod, "filtr"
        return k
    najl: tuple[float, np.ndarray, str] | None = None
    T0 = zgrubne_ransac(fr, pr, seed)
    if T0 is not None:
        T = _icp(fr.chmura, pr.chmura, T0)
        pok, _, _ = ocena(fr, pr, T, odl_max)
        najl = (pok, T, "ransac")
    if najl is None or najl[0] < m["prog_akceptacji_pokrycie"]:
        T0, _ = zgrubne_obroty(fr, pr, odl_max)
        T = _icp(fr.chmura, pr.chmura, T0)
        pok, _, _ = ocena(fr, pr, T, odl_max)
        if najl is None or pok > najl[0]:
            najl = (pok, T, "obroty")
    pok, T, metoda = najl
    k.pokrycie, k.rms_mm, k.pokrycie_odwrotne = ocena(fr, pr, T, odl_max)
    k.metoda = metoda
    # T: fragment (płytka) → pula; projekt (× w) → płytka = T⁻¹ · T0_projektu
    k.transformacja = (np.linalg.inv(T) @ pr.T0).tolist()
    return k


def dopasuj(P: np.ndarray, N: np.ndarray, pula: Pula, ust: dict, gniazdo: int | None = None, seed: int = 0) -> WynikDopasowania:
    """Ranking projektów z puli dla fragmentu (punkty + normalne w układzie płytki)."""
    t0 = time.time()
    m = ust["match"]
    uwagi: list[str] = []
    if len(P) < 50 or len(pula) == 0:
        return WynikDopasowania(gniazdo, [], 0.0, "szary", 0.0, int(len(P)), ["za mało punktów" if len(P) < 50 else "pusta pula"])
    fr = FragmentDoDopasowania.z_punktow(P, N)
    kandydaci = [dopasuj_pare(fr, pr, ust, seed) for pr in pula.projekty.values()]
    if not any(k.filtr_ok for k in kandydaci):
        uwagi.append("żaden projekt nie przeszedł filtru wymiarów — dopasowano wszystkie")
        for k, pr in zip(kandydaci, pula.projekty.values()):
            k.filtr_ok = True
            kk = dopasuj_pare(fr, pr, {**ust, "match": {**m, "filtr_wymiar_mm": 1e9, "filtr_objetosc_udzial": 1e9}}, seed)
            k.pokrycie, k.rms_mm, k.pokrycie_odwrotne, k.transformacja, k.metoda = kk.pokrycie, kk.rms_mm, kk.pokrycie_odwrotne, kk.transformacja, kk.metoda
    kandydaci.sort(key=lambda k: (-k.pokrycie, k.rms_mm))
    p1 = kandydaci[0].pokrycie
    p2 = kandydaci[1].pokrycie if len(kandydaci) > 1 else 0.0
    pewnosc = p1 - p2
    if p1 >= m["prog_akceptacji_pokrycie"] and pewnosc >= m["pewnosc_min"]:
        status = "zielony"
    elif p1 >= m["prog_ostrzezenia_pokrycie"] and pewnosc >= m["pewnosc_min"]:
        status = "zolty"
    else:
        status = "szary"
    return WynikDopasowania(gniazdo, kandydaci, pewnosc, status, round(time.time() - t0, 2), int(len(P)), uwagi)


def blad_pozy(transformacja: np.ndarray, prawda: np.ndarray, siatka: trimesh.Trimesh) -> dict:
    """Różnica dwóch macierzy (projekt × w → płytka) na środku ciężkości projektu: przesunięcie [mm] i obrót [°]."""
    A, B = np.asarray(transformacja), np.asarray(prawda)
    E = A @ np.linalg.inv(B)
    kat = math.degrees(math.acos(min(1.0, max(-1.0, (np.trace(E[:3, :3]) - 1) / 2))))
    c = np.append(siatka.centroid, 1.0)
    return {"przesuniecie_mm": float(np.linalg.norm((A @ c)[:3] - (B @ c)[:3])), "obrot_deg": kat}
