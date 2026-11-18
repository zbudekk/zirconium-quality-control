"""match — który projekt STL to jest: identyfikacja fragmentu skanu w puli projektów.

Wejście: fragment (punkty z normalnymi w układzie płytki, z ``plate``), pula projektów
(folder(y) STL, współczynnik skurczu). Wyjście: ranking kandydatów z pokryciem
(udział punktów fragmentu w odległości ≤ ``[match] odleglosc_max_mm`` od projektu),
transformacją projekt → płytka i pewnością (różnica pokrycia 1. i 2. kandydata).

Kroki na parę fragment–kandydat:
1. filtr (cechy z katalogu × współczynnik): fragment nie wyższy niż projekt (+ tolerancja) i nie niższy niż
   `filtr_wysokosc_min_udzial` jego wysokości (dół pracy bywa schowany w gnieździe albo niewidoczny z góry);
   wymiary obrysu xy ± (`filtr_wymiar_mm` albo `filtr_wymiar_udzial`) i objętość otoczki wypukłej
   ± `filtr_objetosc_udzial` — wobec projektu PRZYCIĘTEGO do wysokości fragmentu (od brzegu w dół);
2. zgrubne dopasowanie: FPFH + RANSAC (Open3D) — a gdy pokrycie po nim jest słabe, przegląd obrotów
   wokół z co 30° od środków (prace leżą brzegiem do góry, więc różnią się głównie obrotem wokół z);
3. ICP punkt–płaszczyzna (progi 0,6 → 0,2 → 0,08 mm);
4. ocena: odległość każdego punktu fragmentu do siatki projektu (Open3D RaycastingScene) → pokrycie,
   RMS punktów w pokryciu, pokrycie odwrotne (punkty projektu blisko fragmentu).

Po rankingu — korekta skali ze skanu (decyzja właściciela 06.11.2026: współczynnik z puli + poprawka skali
wyznaczona ze skanu w oknie ± `korekta_skali_okno_proc`, ostrzeżenie powyżej `korekta_skali_ostrzezenie_proc`):
dla najlepszego kandydata dopasowanie podobieństwa (obrót + przesunięcie + JEDNA skala) na punktach skanu
POZA pasem brzegu (`korekta_skali_pas_brzegu_mm`; strefa przy krawędzi brzegu nie wpływa na skalę), a potem
pokrycie i transformacja liczone w skali skorygowanej. Transformacja kandydata po korekcie jest podobieństwem.

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
KROK_PROFILU = 0.5  # mm: co tyle głębokości (od brzegu w dół) liczone są cechy projektu przyciętego do wysokości fragmentu (filtr)
# korekta skali ze skanu — parametry estymatora (progi robocze: okno, ostrzeżenie, pas brzegu są w [match])
SKALA_VOXEL = 0.1  # mm: stała siatka uśredniania punktów skanu do estymacji skali
SKALA_ITERACJI = 30  # najwyżej tyle kroków Gaussa–Newtona na przejście
SKALA_ZBIEZNOSC = 1e-6  # koniec iteracji: zmiana skali poniżej tego (0,0001 %), obrotu < 1e-5 rad, przesunięcia < 5e-5 mm
SKALA_ODL_MAX = 0.5  # mm: punkt skanu dalej od projektu nie bierze udziału (inna powierzchnia, okruch)
SKALA_C_MIN = 0.03  # mm: dolna granica stałej Tukeya (c = 4,685 · 1,4826 · MAD reszt)
SKALA_OBSZAR_MM = 0.03  # mm: średnia reszta otoczenia punktu powyżej tego = obszar odbiegający od projektu (poprawka ręczna, ubytek) — wyłączony z 2. przejścia
SKALA_OBSZAR_PROMIEN = 0.3  # mm: promień otoczenia do średniej reszty
SKALA_OBSZAR_SASIADOW = 24  # najwyżej tylu sąsiadów w otoczeniu
SKALA_MIN_PUNKTOW = 300  # mniej punktów (po uśrednieniu, poza pasem brzegu, z wagą > 0) = skali nie wyznacza się
SKALA_GRANICA = 0.05  # |s − 1| powyżej tego w trakcie iteracji = dopasowanie rozbieżne (obcy projekt), przerwanie
SKALA_KANDYDATOW = 2  # najwyżej tylu kandydatów dostaje korektę skali (drugi tylko, gdy jego pokrycie jest blisko pierwszego)
SKALA_REMIS = 0.5  # drugi kandydat dostaje korektę, gdy jego pokrycie ≥ tyle × pokrycie pierwszego (ranking niepewny przy błędzie współczynnika)
SKALA_SPADEK_POKRYCIA = 0.02  # korekta, po której pokrycie spada o więcej niż tyle, nie jest stosowana
SKALA_DOKLADNOSC_PROC = 0.05  # dokładność estymaty skali (cel z testów T7, zmierzona: raport części A); poprawka do okno + tyle jest jeszcze stosowana


@dataclass
class KorektaSkali:
    """Korekta skali ze skanu dla kandydata (izotropowa; wariant C z testów T7, decyzja właściciela 06.11.2026).

    ``poprawka_proc`` > 0: skan (praca) jest większy niż projekt × współczynnik puli o tyle procent, czyli
    współczynnik tej pracy wynosi ``wspolczynnik_ze_skanu`` = współczynnik puli × (1 + poprawka / 100).
    """
    poprawka_proc: float | None = None  # None = nie wyznaczono (powód w ``powod``)
    zastosowana: bool = False  # czy pokrycie i transformacja kandydata są liczone w skali skorygowanej
    powod: str = ""  # dlaczego nie zastosowano ("" = zastosowana)
    ostrzezenie: bool = False  # |poprawka| > korekta_skali_ostrzezenie_proc (także poza oknem), o ile estymata nie jest niepewna
    niepewna: bool = False  # po korekcie pokrycie < prog_akceptacji_pokrycie: skan nie pasuje do projektu także w tej skali (drgnięcie, bokiem) — bez ostrzeżenia
    wspolczynnik_puli: float | None = None
    wspolczynnik_ze_skanu: float | None = None
    pokrycie_przed: float | None = None  # pokrycie kandydata przed korektą (skala z puli)
    pokrycie_po: float | None = None  # pokrycie w skali ze skanu (także gdy korekty nie zastosowano)
    punktow: int = 0  # punkty estymacji (uśrednione, poza pasem brzegu, poza obszarami odbiegającymi)
    punktow_w_pasie_brzegu: int = 0  # punkty wyłączone, bo leżą w pasie brzegu
    punktow_w_obszarach: int = 0  # punkty wyłączone jako obszar odbiegający od projektu
    iteracje: int = 0
    czas_s: float = 0.0


@dataclass
class Kandydat:
    id: str
    zeby: list[str]
    typ: str
    pokrycie: float = 0.0  # udział punktów fragmentu ≤ odleglosc_max od projektu
    rms_mm: float = math.inf  # RMS odległości punktów w pokryciu
    pokrycie_odwrotne: float = 0.0  # udział punktów projektu ≤ 2·odleglosc_max od fragmentu
    transformacja: list | None = None  # 4×4: (projekt × współczynnik) → układ płytki; po korekcie skali podobieństwo (skala = 1 + poprawka)
    metoda: str = ""  # ransac | obroty | filtr
    filtr_ok: bool = True
    powod_filtru: str = ""
    skala: KorektaSkali | None = None  # korekta skali ze skanu (tylko kandydaci, dla których ją liczono)


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

    @property
    def skala(self) -> KorektaSkali | None:
        """Korekta skali najlepszego kandydata (None: brak kandydata albo nie liczono)."""
        return self.kandydaci[0].skala if self.kandydaci else None


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
        self._profil: dict[int, tuple[list[float], float]] = {}  # cechy projektu przyciętego do głębokości k·KROK_PROFILU (filtr)

    def odleglosci(self, P: np.ndarray) -> np.ndarray:
        return self.scena.compute_distance(o3d.core.Tensor(np.ascontiguousarray(P, dtype=np.float32))).numpy()

    def cechy_do_glebokosci(self, glebokosc: float) -> tuple[list[float], float]:
        """(obrys xy [krótszy, dłuższy bok], objętość otoczki wypukłej) części projektu od brzegu (z = 0) do ``glebokosc`` mm w dół.

        Fragment skanu bywa niższy niż projekt (dół pracy schowany w gnieździe, widok tylko z góry) — jego obrys i otoczkę
        porównuje się wtedy z tą samą częścią projektu, nie z całym. Głębokość zaokrąglana w górę do ``KROK_PROFILU``;
        gdy sięga dna projektu — cechy całego projektu. Liczone na próbce powierzchni, zapamiętywane na projekcie.
        """
        k = max(1, math.ceil(glebokosc / KROK_PROFILU - 1e-9))
        if k * KROK_PROFILU >= self.wysokosc:
            return self.obrys_xy, self.hull
        if k not in self._profil:
            Q = np.asarray(self.chmura.points)
            Q = Q[Q[:, 2] >= -k * KROK_PROFILU]
            if len(Q) < 4:
                self._profil[k] = ([0.0, 0.0], 0.0)
            else:
                _, boki = trimesh.bounds.oriented_bounds_2D(Q[:, :2])
                try:
                    hull = float(trimesh.convex.convex_hull(Q).volume)
                except Exception:  # noqa: BLE001 — punkty w jednej płaszczyźnie (sam brzeg): otoczka bez objętości
                    hull = 0.0
                self._profil[k] = (sorted(float(b) for b in boki), hull)
        return self._profil[k]


class Pula:
    """Pula projektów. ``wspolczynnik`` — współczynnik skurczu wspólny dla puli; ``wspolczynniki`` (opcjonalnie)
    — współczynnik dla pojedynczych projektów: skrót projektu (``Projekt.id``) → współczynnik (np. z raportu MillBox
    każdej pracy); projekt bez wpisu dostaje współczynnik wspólny."""

    def __init__(self, foldery: list[Path] | Path, wspolczynnik: float, orientacja: str = "auto", wspolczynniki: dict[str, float] | None = None):
        foldery = [Path(f) for f in (foldery if isinstance(foldery, (list, tuple)) else [foldery])]
        t0 = time.time()
        self.projekty: dict[str, Projekt] = {}
        self.pominiete = 0
        for f in foldery:
            for p in S.pliki_projektow(f):
                w = wspolczynniki.get(S.skrot_pliku(p), wspolczynnik) if wspolczynniki else wspolczynnik
                try:
                    pr = Projekt(p, w, orientacja)
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
    """Czy wymiary i objętość fragmentu pasują do projektu (× współczynnik już w puli).

    Skan widzi pracę z góry i tylko tę część, która wystaje z gniazda, więc fragment bywa NIŻSZY niż projekt
    (testy T7: 82–92 % wysokości przy widoku z góry; T10: dolne 1,5 mm w gnieździe), ale nigdy istotnie wyższy.
    Dlatego: (1) wysokość — fragment nie wyższy niż projekt + tolerancja i nie niższy niż
    ``filtr_wysokosc_min_udzial`` wysokości projektu (albo projekt − tolerancja, jeśli to mniej: reguła sprzed zmiany
    nigdy nie jest zaostrzana); (2) obrys xy i objętość otoczki — wobec projektu przyciętego do wysokości fragmentu
    (``Projekt.cechy_do_glebokosci``), z tolerancjami jak dotąd. Przy fragmencie pełnej wysokości to stary filtr.
    """
    m = ust["match"]
    tol = lambda v: max(m["filtr_wymiar_mm"], m["filtr_wymiar_udzial"] * v)  # noqa: E731
    if fr.wysokosc - pr.wysokosc > tol(pr.wysokosc):
        return False, f"wysokość {fr.wysokosc:.1f} vs {pr.wysokosc:.1f} mm (fragment wyższy niż projekt)"
    if fr.wysokosc < min(pr.wysokosc - tol(pr.wysokosc), m["filtr_wysokosc_min_udzial"] * pr.wysokosc):
        return False, f"wysokość {fr.wysokosc:.1f} vs {pr.wysokosc:.1f} mm (widać mniej niż {m['filtr_wysokosc_min_udzial']:.0%} wysokości projektu)"
    obrys, hull = pr.cechy_do_glebokosci(fr.wysokosc)
    for nazwa, a, b in (("długość", fr.obrys_xy[1], obrys[1]), ("szerokość", fr.obrys_xy[0], obrys[0])):
        if abs(a - b) > tol(b):
            return False, f"{nazwa} {a:.1f} vs {b:.1f} mm"
    if hull > 0 and abs(fr.hull - hull) > m["filtr_objetosc_udzial"] * hull:
        return False, f"objętość otoczki {fr.hull:.0f} vs {hull:.0f} mm³"
    return True, ""


def skala_macierzy(T: np.ndarray) -> float:
    """Skala podobieństwa 4×4 (∛ wyznacznika części obrotowej); macierz sztywna → dokładnie 1,0."""
    det = float(np.linalg.det(np.asarray(T)[:3, :3]))
    return 1.0 if abs(det - 1.0) < 1e-9 else float(np.cbrt(det))


def _icp(zr: o3d.geometry.PointCloud, cel: o3d.geometry.PointCloud, T: np.ndarray, progi=(0.6, 0.2, 0.08), iteracje: int = 40) -> np.ndarray:
    est = o3d.pipelines.registration.TransformationEstimationPointToPlane()
    for prog in progi:
        w = o3d.pipelines.registration.registration_icp(zr, cel, prog, T, est, o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=iteracje))
        T = np.asarray(w.transformation)
    return T


def ocena(fr: FragmentDoDopasowania, pr: Projekt, T: np.ndarray, odl_max: float) -> tuple[float, float, float]:
    """(pokrycie, rms, pokrycie odwrotne) dla T: fragment → układ puli projektu.

    T może być podobieństwem (po korekcie skali): odległości liczone w układzie puli wracają do mm skanu (÷ skala)."""
    s = skala_macierzy(T)
    P = fr.P @ T[:3, :3].T + T[:3, 3]
    d = pr.odleglosci(P) / s
    w = d <= odl_max
    pok = float(w.mean())
    rms = float(np.sqrt(np.mean(d[w] ** 2))) if w.any() else math.inf
    dd, _ = cKDTree(P).query(np.asarray(pr.chmura.points)[::4], k=1, distance_upper_bound=2 * odl_max * s)
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


# ----------------------------------------------------------------------------
# korekta skali ze skanu
# ----------------------------------------------------------------------------
def _usrednij_w_siatce(P: np.ndarray, voxel: float) -> np.ndarray:
    """Średnie punktów w komórkach STAŁEJ siatki (początek w zerze układu, nie w rogu chmury jak w Open3D):
    wynik dla punktów jednej komórki nie zależy od reszty chmury, więc zmiana punktów pasa brzegu nie rusza pozostałych."""
    if len(P) == 0:
        return np.zeros((0, 3))
    k = np.floor(P / voxel).astype(np.int64) + (1 << 20)
    _, inv, n = np.unique((k[:, 0] << 42) | (k[:, 1] << 21) | k[:, 2], return_inverse=True, return_counts=True)
    inv = inv.ravel()
    return np.stack([np.bincount(inv, weights=P[:, i]) / n for i in range(3)], axis=1)


def _obrot_z_wektora(w: np.ndarray) -> np.ndarray:
    """Macierz obrotu 3×3 z wektora obrotu (wzór Rodriguesa)."""
    th = float(np.linalg.norm(w))
    if th < 1e-12:
        return np.eye(3)
    k = w / th
    K = np.array([[0.0, -k[2], k[1]], [k[2], 0.0, -k[0]], [-k[1], k[0], 0.0]])
    return np.eye(3) + math.sin(th) * K + (1 - math.cos(th)) * (K @ K)


def _reszty_do_projektu(X: np.ndarray, pr: Projekt) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Dla punktów w układzie puli: (odległość ze znakiem od płaszczyzny najbliższego trójkąta, jego normalna, odległość)."""
    cp = pr.scena.compute_closest_points(o3d.core.Tensor(np.ascontiguousarray(X, dtype=np.float32)))
    C = cp["points"].numpy().astype(np.float64)
    n = cp["primitive_normals"].numpy().astype(np.float64)
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    dv = X - C
    return np.einsum("ij,ij->i", dv, n), n, np.linalg.norm(dv, axis=1)


def _dopasuj_podobienstwo(Q: np.ndarray, pr: Projekt, R: np.ndarray, t: np.ndarray, s: float, aktywne: np.ndarray) -> dict:
    """Gauss–Newton dla x = s·R·q + t (q — punkty skanu wyśrodkowane): minimum Σ w·ρ², ρ = r / s, r = odległość
    punkt–płaszczyzna do najbliższego trójkąta projektu, wagi Tukeya (c = max(4,685 · 1,4826 · mediana |ρ|, SKALA_C_MIN)),
    7 parametrów. Punkty nieaktywne i dalsze niż SKALA_ODL_MAX mają wagę 0.

    Reszty liczone w mm SKANU (ρ = r / s), nie w układzie puli: skalowanie punktów skanu skaluje też ich szum, więc
    minimum Σ r² leży przy za małym s (obciążenie ≈ +σ² / średnia (n·u)², zmierzone +0,005…+0,05 % przy σ = 0,03 mm —
    to samo obciążenie „+0,01 %” miał prototyp T7). W ρ pochodna po skali nie zawiera szumu punktu."""
    it, n_wag, sigma = 0, 0, 0.0
    for it in range(1, SKALA_ITERACJI + 1):
        u = Q @ R.T
        r, n, odl = _reszty_do_projektu(s * u + t, pr)
        r, odl = r / s, odl / s
        blisko = aktywne & (odl < SKALA_ODL_MAX)
        if int(blisko.sum()) < SKALA_MIN_PUNKTOW:
            return {"ok": False, "powod": f"za mało punktów przy projekcie ({int(blisko.sum())} < {SKALA_MIN_PUNKTOW})", "iteracje": it}
        sigma = 1.4826 * float(np.median(np.abs(r[blisko])))
        c = max(4.685 * sigma, SKALA_C_MIN)
        w = np.where(blisko & (np.abs(r) < c), (1 - (r / c) ** 2) ** 2, 0.0)
        n_wag = int((w > 0).sum())
        J = np.empty((len(Q), 7))
        J[:, 0:3] = np.cross(u, n)
        J[:, 3:6] = n / s
        J[:, 6] = (np.einsum("ij,ij->i", n, u) - r) / s
        try:
            dx = np.linalg.solve(J.T @ (J * w[:, None]), -J.T @ (w * r))
        except np.linalg.LinAlgError:
            return {"ok": False, "powod": "układ równań osobliwy (za mało geometrii poza pasem brzegu)", "iteracje": it}
        R = _obrot_z_wektora(dx[0:3]) @ R
        t = t + dx[3:6]
        s = s + float(dx[6])
        if abs(s - 1.0) > SKALA_GRANICA:
            return {"ok": False, "powod": f"dopasowanie rozbieżne (skala {s:.3f})", "iteracje": it}
        if it >= 3 and abs(dx[6]) < SKALA_ZBIEZNOSC and np.abs(dx[0:3]).max() < 10 * SKALA_ZBIEZNOSC and np.abs(dx[3:6]).max() < 50 * SKALA_ZBIEZNOSC:
            break
    return {"ok": True, "powod": "", "R": R, "t": t, "s": s, "iteracje": it, "punktow": n_wag, "sigma_mm": sigma}


def skala_ze_skanu(P: np.ndarray, pr: Projekt, T: np.ndarray, pas_brzegu_mm: float) -> dict:
    """Izotropowa skala skanu względem projektu z puli: podobieństwo x = s·R·p + t (płytka → układ puli) dopasowane do
    siatki projektu, start z transformacji ``T`` (płytka → pula, z ``dopasuj_pare``).

    Metoda = wariant C z testów T7 (ICP punkt–płaszczyzna z wolną skalą, wagi odporne; błąd ≤ 0,05 % w 1008/1008
    dopasowań) z trzema zmianami: (1) punkty skanu w pasie brzegu — w układzie puli z > −``pas_brzegu_mm`` (brzeg na
    z = 0) — NIE biorą udziału (zastrzeżenie R2b z testów S1b: dopasowanie z wolną skalą przesuwa pas brzegu o
    0,01–0,03 mm, gdy strefa przy krawędzi odbiega od projektu; ukruszenie brzegu nie może zmieniać skali);
    (2) punkty uśredniane w stałej siatce SKALA_VOXEL, żeby zmiana punktów pasa nie zmieniała pozostałych;
    (3) reszty w mm skanu, nie w układzie puli (bez obciążenia skali szumem — ``_dopasuj_podobienstwo``).
    Dwa przejścia: po pierwszym reszty uśrednione po otoczeniu SKALA_OBSZAR_PROMIEN wyznaczają obszary odbiegające
    od projektu (gładka poprawka ręczna, ubytek poza pasem: |średnia| > max(SKALA_OBSZAR_MM, σ reszt)) — w drugim
    są pominięte (T7: bez tego poprawka ręczna przeciąga skalę do 0,09 %).

    Zwraca słownik: ``ok``, ``powod``, ``s`` (skala skan → projekt × współczynnik puli; < 1 = praca większa),
    ``T`` (4×4 podobieństwo płytka → pula), ``punktow``, ``punktow_w_pasie_brzegu``, ``punktow_w_obszarach``,
    ``iteracje``, ``sigma_mm`` (odporne σ reszt), ``czas_s``.
    """
    t0 = time.time()
    P = np.asarray(P, dtype=np.float64)
    T = np.asarray(T, dtype=np.float64)
    s = skala_macierzy(T)
    R, tt = T[:3, :3] / s, T[:3, 3].copy()
    wyn = {"ok": False, "powod": "", "s": None, "T": None, "punktow": 0, "punktow_w_pasie_brzegu": 0, "punktow_w_obszarach": 0, "iteracje": 0, "sigma_mm": None}
    for przejscie in (1, 2):
        poza_pasem = (s * (P @ R.T) + tt)[:, 2] <= -pas_brzegu_mm
        Qp = _usrednij_w_siatce(P[poza_pasem], SKALA_VOXEL)
        wyn["punktow_w_pasie_brzegu"] = int(len(P) - poza_pasem.sum())
        if len(Qp) < SKALA_MIN_PUNKTOW:
            wyn["powod"] = f"za mało punktów poza pasem brzegu ({len(Qp)} < {SKALA_MIN_PUNKTOW})"
            break
        c0 = Qp.mean(0)
        Q = Qp - c0
        t = s * (R @ c0) + tt  # położenie środka punktów w układzie puli
        aktywne = np.ones(len(Q), dtype=bool)
        if przejscie == 2:  # obszary odbiegające od projektu: średnia reszta otoczenia ponad próg
            r = _reszty_do_projektu(s * (Q @ R.T) + t, pr)[0] / s
            dd, ii = cKDTree(Qp).query(Qp, k=min(SKALA_OBSZAR_SASIADOW, len(Qp)), distance_upper_bound=SKALA_OBSZAR_PROMIEN)
            jest = np.isfinite(dd)
            sr = np.where(jest, r[np.where(jest, ii, 0)], 0.0).sum(axis=1) / np.maximum(jest.sum(axis=1), 1)
            aktywne = np.abs(sr) <= max(SKALA_OBSZAR_MM, wyn["sigma_mm"] or 0.0)
            wyn["punktow_w_obszarach"] = int((~aktywne).sum())
        d = _dopasuj_podobienstwo(Q, pr, R, t, s, aktywne)
        wyn["iteracje"] += d["iteracje"]
        if not d["ok"]:
            wyn["powod"] = d["powod"]
            break
        R, t, s = d["R"], d["t"], d["s"]
        tt = t - s * (R @ c0)
        wyn["punktow"], wyn["sigma_mm"] = d["punktow"], d["sigma_mm"]
    else:
        Ts = np.eye(4)
        Ts[:3, :3], Ts[:3, 3] = s * R, tt
        wyn.update(ok=True, s=float(s), T=Ts)
    wyn["czas_s"] = round(time.time() - t0, 3)
    return wyn


def koryguj_skale(P: np.ndarray, fr: FragmentDoDopasowania, k: Kandydat, pr: Projekt, m: dict, bez_korekty: str = "") -> None:
    """Korekta skali ze skanu dla kandydata ``k`` (wpis ``k.skala``): estymata skali poza pasem brzegu, a gdy poprawka
    mieści się w oknie ± ``korekta_skali_okno_proc`` i wolno ją stosować — pokrycie i transformacja ``k`` w skali skorygowanej.

    ``bez_korekty`` (niepusty powód, np. płytka poranna): poprawka jest tylko mierzona (z ostrzeżeniem), nie stosowana.
    Po korekcie poza poprawiana jest tak jak dotąd (ICP na wszystkich punktach fragmentu), przy ustalonej skali.
    Nie jest stosowana także wtedy, gdy pokrycie po korekcie < ``prog_ostrzezenia_pokrycie`` (praca nierozpoznana w żadnej
    skali — status i tak szary; pomiar R59: inaczej skorygowany obcy projekt wyprzedzał właściwy, nieskorygowany)
    albo spada o więcej niż SKALA_SPADEK_POKRYCIA.
    """
    kor = KorektaSkali(wspolczynnik_puli=pr.wspolczynnik, pokrycie_przed=k.pokrycie)
    k.skala = kor
    if not m["korekta_skali"]:
        kor.powod = "korekta wyłączona ([match] korekta_skali)"
        return
    t0 = time.time()
    est = skala_ze_skanu(P, pr, pr.T0 @ np.linalg.inv(np.asarray(k.transformacja, dtype=np.float64)), m["korekta_skali_pas_brzegu_mm"])
    kor.punktow, kor.punktow_w_pasie_brzegu, kor.punktow_w_obszarach, kor.iteracje = est["punktow"], est["punktow_w_pasie_brzegu"], est["punktow_w_obszarach"], est["iteracje"]
    if not est["ok"]:
        kor.powod = "skali nie wyznaczono: " + est["powod"]
        kor.czas_s = round(time.time() - t0, 3)
        return
    e = (1.0 / est["s"] - 1.0) * 100.0  # o tyle % skan jest większy niż projekt × współczynnik puli
    kor.poprawka_proc = round(e, 4)
    kor.wspolczynnik_ze_skanu = round(pr.wspolczynnik / est["s"], 6)
    Ts = _icp(fr.chmura, pr.chmura, est["T"], progi=(0.2, 0.08))  # sztywna poprawka pozy przy ustalonej skali (init niesie skalę)
    pok, rms, odwr = ocena(fr, pr, Ts, m["odleglosc_max_mm"])
    kor.pokrycie_po = round(pok, 4)
    # estymata jest wiarygodna, gdy w tej skali skan pasuje do projektu; inaczej (podwójna powierzchnia po drgnięciu, praca
    # bokiem, obcy projekt) liczba nie mówi nic o współczynniku i ostrzeżenia „sprawdź współczynnik” nie ma
    kor.niepewna = pok < m["prog_akceptacji_pokrycie"]
    kor.ostrzezenie = abs(e) > m["korekta_skali_ostrzezenie_proc"] and not kor.niepewna
    if abs(e) > m["korekta_skali_okno_proc"] + SKALA_DOKLADNOSC_PROC:  # błąd równy granicy okna nie może zależeć od szumu estymaty
        kor.powod = f"poprawka {e:+.2f} % poza oknem ±{m['korekta_skali_okno_proc']:g} %"
    elif bez_korekty:
        kor.powod = bez_korekty
    elif pok < m["prog_ostrzezenia_pokrycie"]:  # praca nierozpoznana także w tej skali: korekta niczego nie poprawia, a mogłaby przestawić ranking obcych projektów
        kor.powod = f"pokrycie po korekcie {pok:.2f} < prog_ostrzezenia_pokrycie: praca nierozpoznana"
    elif pok < k.pokrycie - SKALA_SPADEK_POKRYCIA:
        kor.powod = f"pokrycie po korekcie niższe ({pok:.2f} < {k.pokrycie:.2f})"
    else:
        k.pokrycie, k.rms_mm, k.pokrycie_odwrotne = pok, rms, odwr
        k.transformacja = (np.linalg.inv(Ts) @ pr.T0).tolist()  # (projekt × w) → płytka: podobieństwo o skali 1 + poprawka
        kor.zastosowana = True
    kor.czas_s = round(time.time() - t0, 3)


def dopasuj(P: np.ndarray, N: np.ndarray, pula: Pula, ust: dict, gniazdo: int | None = None, seed: int = 0, bez_korekty: str = "") -> WynikDopasowania:
    """Ranking projektów z puli dla fragmentu (punkty + normalne w układzie płytki).

    Po rankingu korekta skali ze skanu dla najlepszego kandydata (``Kandydat.skala``, ``WynikDopasowania.skala``);
    ``bez_korekty`` — niepusty powód, dla którego poprawki skali nie wolno stosować (płytka poranna: prace spieczone,
    współczynnik 1,0): poprawka jest wtedy tylko mierzona."""
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
    # korekta skali ze skanu: najlepszy kandydat, a drugi tylko gdy ranking jest niepewny (pokrycia blisko siebie, jak przy
    # błędzie współczynnika); obcy projekt dostaje skalę poza oknem i zostaje bez korekty (T7: 1,36–1,46 zamiast 1,22)
    for i, k in enumerate(list(kandydaci[:SKALA_KANDYDATOW])):
        if k.transformacja is not None and (i == 0 or k.pokrycie >= SKALA_REMIS * kandydaci[0].pokrycie):
            koryguj_skale(P, fr, k, pula.projekty[k.id], m, bez_korekty)
    kandydaci.sort(key=lambda k: (-k.pokrycie, k.rms_mm))
    sk = kandydaci[0].skala
    if sk is not None and sk.ostrzezenie:
        uwagi.append(f"skala: praca {'większa' if sk.poprawka_proc > 0 else 'mniejsza'} o {abs(sk.poprawka_proc):.2f} % niż projekt × współczynnik "
                     f"(próg ostrzeżenia {m['korekta_skali_ostrzezenie_proc']:g} %) — sprawdź współczynnik / krążek"
                     + ("" if sk.zastosowana else f"; korekty nie zastosowano: {sk.powod}"))
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
    """Różnica dwóch macierzy (projekt × w → płytka) na środku ciężkości projektu: przesunięcie [mm] i obrót [°].

    Macierze mogą być podobieństwami (transformacja po korekcie skali): obrót liczony po zdjęciu skali."""
    A, B = np.asarray(transformacja), np.asarray(prawda)
    E = A @ np.linalg.inv(B)
    kat = math.degrees(math.acos(min(1.0, max(-1.0, (np.trace(E[:3, :3]) / skala_macierzy(E) - 1) / 2))))
    c = np.append(siatka.centroid, 1.0)
    return {"przesuniecie_mm": float(np.linalg.norm((A @ c)[:3] - (B @ c)[:3])), "obrot_deg": kat}
