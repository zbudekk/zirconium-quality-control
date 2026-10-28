"""Dopasowanie fragmentu do projektu: zgrubne (osie PCA + przeglad katow + ICP; FPFH + RANSAC),
ICP point-to-plane (dokladne), pokrycie.

Konwencja: wszystkie T zwracane przez funkcje publiczne prowadza z ukladu projektu do ukladu fragmentu.
zgrubne/dokladne pracuja na chmurze projektu juz przeskalowanej o k (T sztywne, mm);
pokrycie przyjmuje T ze skala (projekt w ukladzie CAD -> fragment).
Rejestracja liczona jest fragment -> projekt (fragment bywa niepelny, projekt jest pelny) i odwracana.
"""

from dataclasses import dataclass

import numpy as np
import open3d as o3d
import trimesh

from qc.open3d_wspolne import ziarno as ziarno_open3d

reg = o3d.pipelines.registration

PUNKTY_PROJEKTU = 20_000
PUNKTY_RZADKIE = 6_000  # probka do chmury voxel_fpfh_mm (przeglad katow, 1. etap ICP)
ZIARNO_PROBKI = 0
ZIARNO_RANSAC = 1
VOXEL_ICP_MM = 0.4
ETAPY_ICP_MM = (0.5, 0.1)
PRZESUNIECIA_OSI = (0.0, -0.05, 0.05, -0.1, 0.1, -0.15, 0.15, -0.2, 0.2, -0.25, 0.25)  # x dlugosc projektu wzdluz osi


@dataclass(eq=False)
class ChmuraCech:
    """Chmura po voxel_down_sample z normalnymi i FPFH."""

    chmura: o3d.geometry.PointCloud
    fpfh: reg.Feature


def chmura(punkty: np.ndarray, normalne: np.ndarray | None = None) -> o3d.geometry.PointCloud:
    pc = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.asarray(punkty, dtype=np.float64)))
    if normalne is not None:
        pc.normals = o3d.utility.Vector3dVector(np.asarray(normalne, dtype=np.float64))
    return pc


def cechy_fpfh(pc: o3d.geometry.PointCloud, voxel: float) -> ChmuraCech:
    """voxel_down_sample, normalne (promien 2 x voxel, 30 sasiadow), FPFH (promien 5 x voxel)."""
    rzadka = pc.voxel_down_sample(voxel)
    rzadka.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=2 * voxel, max_nn=30))
    fpfh = reg.compute_fpfh_feature(rzadka, o3d.geometry.KDTreeSearchParamHybrid(radius=5 * voxel, max_nn=100))
    return ChmuraCech(rzadka, fpfh)


def probka_projektu(siatka: trimesh.Trimesh, k: float, liczba: int = PUNKTY_PROJEKTU) -> o3d.geometry.PointCloud:
    """Probka powierzchni projektu przeskalowanego o k (losowanie wazone polem, stale ziarno), normalne scian.

    Wlasne losowanie w numpy: trimesh.sample.sample_surface trwa 20-30 ms na siatce 150 tys. scian.
    """
    v = np.asarray(siatka.vertices, dtype=np.float64)
    f = np.asarray(siatka.faces, dtype=np.int64)
    v0 = v[f[:, 0]]
    a = v[f[:, 1]] - v0
    b = v[f[:, 2]] - v0
    iloczyn = np.cross(a, b)
    pole = np.linalg.norm(iloczyn, axis=1)
    rng = np.random.default_rng(ZIARNO_PROBKI)
    skumulowane = np.cumsum(pole)
    sciany = np.minimum(np.searchsorted(skumulowane, rng.random(liczba) * skumulowane[-1]), len(f) - 1)
    u, w = rng.random(liczba), rng.random(liczba)
    poza = u + w > 1.0
    u[poza], w[poza] = 1.0 - u[poza], 1.0 - w[poza]
    punkty = v0[sciany] + a[sciany] * u[:, None] + b[sciany] * w[:, None]
    n = iloczyn[sciany] / np.maximum(pole[sciany], 1e-12)[:, None]
    return chmura(punkty * k, n)


def _odwroc(T: np.ndarray) -> np.ndarray:
    return np.linalg.inv(np.asarray(T, dtype=np.float64))


def zgrubne_z_cech(fragment: ChmuraCech, projekt: ChmuraCech, voxel: float,
                   ziarno: int = ZIARNO_RANSAC) -> np.ndarray:
    """RANSAC na korespondencjach FPFH; zwraca T fragment -> projekt (sztywne)."""
    odl = 1.5 * voxel
    with ziarno_open3d(ziarno):  # seed open3d jest globalny - blokada wspolna z qc.plate
        wynik = reg.registration_ransac_based_on_feature_matching(
            fragment.chmura, projekt.chmura, fragment.fpfh, projekt.fpfh, True, odl,
            reg.TransformationEstimationPointToPoint(False), 3,
            [reg.CorrespondenceCheckerBasedOnEdgeLength(0.9), reg.CorrespondenceCheckerBasedOnDistance(odl)],
            reg.RANSACConvergenceCriteria(100_000, 0.999))
    return np.asarray(wynik.transformation, dtype=np.float64)


def icp(fragment_pc: o3d.geometry.PointCloud, projekt_pc: o3d.geometry.PointCloud,
        T_f2p: np.ndarray, etapy=ETAPY_ICP_MM,
        projekt_rzadki: o3d.geometry.PointCloud | None = None) -> tuple[np.ndarray, float]:
    """ICP point-to-plane fragment -> projekt (projekt z normalnymi) w kolejnych etapach odleglosci.

    projekt_rzadki (opcjonalnie, z normalnymi): cel pierwszego etapu - szybciej, dokladnosc daje ostatni.
    """
    T = np.asarray(T_f2p, dtype=np.float64)
    rms = float("inf")
    for nr, max_odl in enumerate(etapy):
        cel = projekt_rzadki if nr == 0 and projekt_rzadki is not None and len(etapy) > 1 else projekt_pc
        wynik = reg.registration_icp(fragment_pc, cel, max_odl, T,
                                     reg.TransformationEstimationPointToPlane(),
                                     reg.ICPConvergenceCriteria(max_iteration=30))
        T = np.asarray(wynik.transformation, dtype=np.float64)
        rms = float(wynik.inlier_rmse) if wynik.fitness > 0 else float("inf")
    return T, rms


def zgrubne(fragment_pc: o3d.geometry.PointCloud, projekt_pc: o3d.geometry.PointCloud,
            voxel: float) -> np.ndarray:
    """FPFH + RANSAC; T projekt -> fragment (4x4, sztywne)."""
    return _odwroc(zgrubne_z_cech(cechy_fpfh(fragment_pc, voxel), cechy_fpfh(projekt_pc, voxel), voxel))


def dokladne(fragment_pc: o3d.geometry.PointCloud, projekt_pc: o3d.geometry.PointCloud,
             T0: np.ndarray, max_odleglosc: float) -> tuple[np.ndarray, float]:
    """ICP point-to-plane od T0 (projekt -> fragment); zwraca (T projekt -> fragment, rms w mm)."""
    if not projekt_pc.has_normals():
        projekt_pc = o3d.geometry.PointCloud(projekt_pc)
        projekt_pc.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=2 * max_odleglosc, max_nn=30))
    T, rms = icp(fragment_pc, projekt_pc, _odwroc(T0), etapy=(max_odleglosc,))
    return _odwroc(T), rms


def scena(siatka: trimesh.Trimesh) -> o3d.t.geometry.RaycastingScene:
    s = o3d.t.geometry.RaycastingScene()
    s.add_triangles(o3d.core.Tensor(np.asarray(siatka.vertices, dtype=np.float32)),
                    o3d.core.Tensor(np.asarray(siatka.faces, dtype=np.uint32)))
    return s


def pokrycie(fragment: trimesh.Trimesh | np.ndarray, projekt: trimesh.Trimesh, T: np.ndarray, prog_mm: float,
             scena_projektu: o3d.t.geometry.RaycastingScene | None = None) -> float:
    """Udzial wierzcholkow fragmentu (Trimesh albo tablica (N, 3)) w odleglosci <= prog od projektu po T.

    T ze skala (projekt w ukladzie CAD -> fragment); projekt potrzebny tylko, gdy brak sceny.

    Wierzcholki przenoszone sa do ukladu CAD przez T^-1, a odleglosc mnozona przez skale T,
    dzieki czemu scena projektu nie zalezy od k i moze byc uzyta ponownie.
    """
    T = np.asarray(T, dtype=np.float64)
    skala = float(np.cbrt(abs(np.linalg.det(T[:3, :3]))))
    wierzcholki = np.asarray(getattr(fragment, "vertices", fragment), dtype=np.float64)
    if skala <= 0 or len(wierzcholki) == 0:
        return 0.0
    odwr = np.linalg.inv(T)
    p = wierzcholki @ odwr[:3, :3].T + odwr[:3, 3]
    s = scena_projektu if scena_projektu is not None else scena(projekt)
    d = s.compute_distance(o3d.core.Tensor(p.astype(np.float32))).numpy() * skala
    return float(np.mean(d <= prog_mm))


# --- wyrownanie osi glownych (PCA) i przeglad katow ----------------------------


def wygladz(v: np.ndarray, f: np.ndarray) -> np.ndarray:
    """Jeden krok usredniania z sasiadami (pierscien wierzcholka) - tlumi szum skanera ok. 2,5 x."""
    v = np.asarray(v, dtype=np.float64)
    f = np.asarray(f, dtype=np.int64)
    if len(f) == 0:
        return v.copy()
    e = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    e = np.concatenate([e, e[:, ::-1]])
    suma = np.empty_like(v)
    for os_ in range(3):
        suma[:, os_] = np.bincount(e[:, 0], weights=v[e[:, 1], os_], minlength=len(v))
    liczba = np.bincount(e[:, 0], minlength=len(v)).astype(np.float64)
    return (v + suma) / (1.0 + liczba)[:, None]


def uklady_osi(punkty: np.ndarray) -> tuple[list[tuple[np.ndarray, np.ndarray]], float]:
    """Ramki (srodek, R) z kolejnymi osiami glownymi jako os z, od najbardziej wyroznionej; i jej wyraznosc.

    Dla korony os wyrozniona to os wprowadzenia (bryla prawie obrotowa), dla mostu os dluga.
    wyraznosc = najmniejsza roznica wartosci wlasnych tej osi od pozostalych / najwieksza wartosc
    wlasna (0 = os nieokreslona). Niepelny skan potrafi zamienic osie - stad ramki dla wszystkich osi.
    """
    p = np.asarray(punkty, dtype=np.float64)
    srodek = p.mean(axis=0)
    w, V = np.linalg.eigh(np.cov((p - srodek).T))
    roznice = [min(abs(w[i] - w[j]) for j in range(3) if j != i) / max(w.max(), 1e-12) for i in range(3)]
    ramki = []
    for i in sorted(range(3), key=lambda i: -roznice[i]):
        a = V[:, i]
        b = V[:, (i + 1) % 3]
        b = b - a * (a @ b)
        b /= np.linalg.norm(b)
        ramki.append((srodek, np.column_stack([np.cross(b, a), b, a])))
    return ramki, float(max(roznice))


def osie(punkty: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """(srodek, R, wyraznosc) dla osi najbardziej wyroznionej (kolumna 3 R), patrz uklady_osi."""
    ramki, wyraznosc = uklady_osi(punkty)
    return ramki[0][0], ramki[0][1], wyraznosc


def _obrot_z(kat: float) -> np.ndarray:
    c, s = np.cos(kat), np.sin(kat)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


class OdlegloscOdChmury:
    """Odleglosc punktow od powierzchni przyblizonej chmura z normalnymi (punkt-plaszczyzna do najblizszego).

    Szybka (NNS open3d, bez BVH siatki) - do etapu zgrubnego; punkt dalej niz promien od najblizszego
    punktu chmury dostaje odleglosc euklidesowa.
    """

    def __init__(self, chmura_pc: o3d.geometry.PointCloud, promien: float):
        self.punkty = np.asarray(chmura_pc.points, dtype=np.float64)
        self.normalne = np.asarray(chmura_pc.normals, dtype=np.float64)
        self.promien = promien
        self.nns = o3d.core.nns.NearestNeighborSearch(o3d.core.Tensor(self.punkty.astype(np.float32)))
        self.nns.knn_index()

    def __call__(self, punkty: np.ndarray) -> np.ndarray:
        idx, _ = self.nns.knn_search(o3d.core.Tensor(np.asarray(punkty, dtype=np.float32)), 1)
        idx = idx.numpy()[:, 0]
        roznica = np.asarray(punkty, dtype=np.float64) - self.punkty[idx]
        e = np.linalg.norm(roznica, axis=1)
        plaszczyzna = np.abs(np.einsum("ij,ij->i", roznica, self.normalne[idx]))
        return np.where(e <= self.promien, plaszczyzna, e)


def odleglosc_od_sceny(scena_projektu, skala: float):
    """Odleglosc od siatki CAD (scena RaycastingScene) punktow w ukladzie projektu przeskalowanego o skala."""
    def odleglosc(punkty: np.ndarray) -> np.ndarray:
        p = (np.asarray(punkty, dtype=np.float64) / skala).astype(np.float32)
        return scena_projektu.compute_distance(o3d.core.Tensor(p)).numpy().astype(np.float64) * skala
    return odleglosc


def _odleglosci_poz(punkty: np.ndarray, pozy: list[np.ndarray], odleglosc) -> np.ndarray:
    """Srednia odleglosc (obcieta do 1 mm) punktow fragmentu od projektu dla kazdej pozy; jedno zapytanie."""
    d = odleglosc(np.concatenate([punkty @ T[:3, :3].T + T[:3, 3] for T in pozy]))
    return np.minimum(d, 1.0).reshape(len(pozy), len(punkty)).mean(axis=1)


def hipotezy_pca(fragment_pc: o3d.geometry.PointCloud, uklady_fragmentu, projekt_pc: o3d.geometry.PointCloud,
                 uklad_projektu, katy: int = 8, max_odleglosc: float = 1.5, prog_oceny: float = 0.25,
                 odleglosc=None, liczba_icp: int = 2,
                 przesuniecia=PRZESUNIECIA_OSI) -> list[tuple[float, np.ndarray]]:
    """Odrebne pozy fragment -> projekt po zgrubnym ICP z ustawien osi (2 zwroty x katy obrotu wokol osi).

    przesuniecia: ulamki dlugosci projektu wzdluz osi wyroznionej dodawane do dopasowania srodkow
    (tylko przy szeregowaniu z odleglosc, pierwsze = 0): niepelny skan mostu przesuwa srodek o kilka mm;
    kazdy wybrany kat startuje ICP z najlepszego przesuniecia i, gdy lezy ono dalej niz polowa
    max_odleglosc, takze z przesuniecia 0.

    uklady_fragmentu: lista ramek (srodek, R) - os z kazdej ramki ustawiana na os wyrozniona projektu.
    odleglosc(punkty w ukladzie projektu przeskalowanego) -> odleglosci od powierzchni projektu
    (OdlegloscOdChmury albo odleglosc_od_sceny): pozy poczatkowe sa szeregowane po sredniej odleglosci
    i zgrubny ICP dostaje tylko liczba_icp katow z kazdej ramki i zwrotu (najlepsze, wzajemnie odlegle
    >= 90 st.), a fitness = udzial punktow <= prog_oceny; bez niej ICP startuje z kazdej pozy, fitness
    od chmury projektu (evaluate_registration).
    Zwraca [(fitness, T)] malejaco; pozy rozniace sie < 0,5 mm sa scalane.
    """
    cp, Rp = uklad_projektu
    punkty = np.asarray(fragment_pc.points)
    probne = punkty[:: max(1, len(punkty) // 50)]
    os_p = Rp[:, 2]
    rzut = np.asarray(projekt_pc.points) @ os_p
    dlugosc = float(rzut.max() - rzut.min()) if len(rzut) else 0.0
    przes = list(przesuniecia) if odleglosc is not None else [0.0]
    pozy = []  # kolejnosc: ramka x zwrot, kat, przesuniecie
    for (cf, Rf), zwrot in [(u, z) for u in uklady_fragmentu for z in (1.0, -1.0)]:
        Rfz = Rf * np.array([zwrot, 1.0, zwrot])  # obrot o 180 st. wokol osi y ramki
        for k in range(katy):
            R = Rp @ _obrot_z(2 * np.pi * k / katy) @ Rfz.T
            for u in przes:
                T = np.eye(4)
                T[:3, :3] = R
                T[:3, 3] = cp + u * dlugosc * os_p - R @ cf
                pozy.append(T)
    if odleglosc is not None and katy > liczba_icp:
        # w kazdej ramce i zwrocie liczba_icp katow: kolejno najlepszy, odlegly >= 90 st. od wybranych
        # (korona bywa prawie symetryczna o 180 st. - sasiednie katy zbiegaja do tej samej pozy)
        oceny = _odleglosci_poz(probne, pozy, odleglosc).reshape(-1, katy, len(przes))
        najlepsze_przes = oceny.argmin(axis=2)
        oceny = oceny.min(axis=2)
        odstep = max(1, katy // 4)
        wybrane = []
        for g, rzad in enumerate(oceny):
            ramka = []
            for k in np.argsort(rzad, kind="stable"):
                if all(min(abs(int(k) - j), katy - abs(int(k) - j)) >= odstep for j in ramka):
                    ramka.append(int(k))
                if len(ramka) == liczba_icp:
                    break
            for k in ramka:
                # najlepsze przesuniecie i takze start bez przesuniecia (indeks 0), gdy najlepsze lezy
                # dalej niz polowa zasiegu ICP: przy moscie najlepsze przesuniecie bywa poza obrocona
                # o 180 st., a wlasciwa startuje z 0; przy koronie (kilka mm) to ten sam start
                u = int(najlepsze_przes[g, k])
                indeksy = [u] if abs(przes[u]) * dlugosc <= max_odleglosc / 2 else sorted({u, 0})
                wybrane += [pozy[(g * katy + k) * len(przes) + i] for i in indeksy]
        pozy = wybrane
    po_icp = []
    for T in pozy:
        r = reg.registration_icp(fragment_pc, projekt_pc, max_odleglosc, T,
                                 reg.TransformationEstimationPointToPlane(),
                                 reg.ICPConvergenceCriteria(max_iteration=15))
        po_icp.append(np.asarray(r.transformation, dtype=np.float64))
    if odleglosc is not None:
        # fitness = udzial punktow fragmentu <= prog_oceny od powierzchni projektu
        d = odleglosc(np.concatenate([punkty @ T[:3, :3].T + T[:3, 3] for T in po_icp]))
        fitness = (d.reshape(len(po_icp), len(punkty)) <= prog_oceny).mean(axis=1)
    else:
        fitness = [reg.evaluate_registration(fragment_pc, projekt_pc, prog_oceny, T).fitness for T in po_icp]
    return _odrebne(sorted(zip((float(f) for f in fitness), po_icp), key=lambda x: -x[0]), probne)


def przelicz_fitness(fragment_pc: o3d.geometry.PointCloud, hipotezy: list[tuple[float, np.ndarray]], odleglosc,
                     prog_oceny: float = 0.25) -> list[tuple[float, np.ndarray]]:
    """Fitness tych samych poz (bez ICP) wzgledem innej odleglosci (np. od siatki zamiast od chmury)."""
    if not hipotezy:
        return []
    punkty = np.asarray(fragment_pc.points)
    d = odleglosc(np.concatenate([punkty @ T[:3, :3].T + T[:3, 3] for _, T in hipotezy]))
    fitness = (d.reshape(len(hipotezy), len(punkty)) <= prog_oceny).mean(axis=1)
    return sorted(((float(f), T) for f, (_, T) in zip(fitness, hipotezy)), key=lambda x: -x[0])


def _odrebne(wyniki: list[tuple[float, np.ndarray]], probne: np.ndarray) -> list[tuple[float, np.ndarray]]:
    """Scala pozy rozniace sie < 0,5 mm (max przesuniecie punktow probnych), zostawia najlepsza."""
    odrebne = []
    for fit, T in wyniki:
        p = probne @ T[:3, :3].T + T[:3, 3]
        if all(np.max(np.linalg.norm(p - q, axis=1)) > 0.5 for _, _, q in odrebne):
            odrebne.append((fit, T, p))
    return [(fit, T) for fit, T, _ in odrebne]


def przenies(punkty: np.ndarray, T: np.ndarray) -> np.ndarray:
    """Punkty (N, 3) po transformacji 4x4."""
    T = np.asarray(T, dtype=np.float64)
    return np.asarray(punkty, dtype=np.float64) @ T[:3, :3].T + T[:3, 3]
