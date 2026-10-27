"""Identyfikacja prac: fragment skanu -> projekt z puli (filtr cech, osie PCA / FPFH + RANSAC, ICP, ranking)."""

import numpy as np
import open3d as o3d
import trimesh

from qc.catalog.cechy import policz
from qc.match import dopasowanie as _d
from qc.match import filtr, ranking
from qc.match.filtr import WpisPuli
from qc.match.ranking import Kandydat, WynikDopasowania

__all__ = ["dopasuj", "WpisPuli", "Kandydat", "WynikDopasowania"]

PROBY_RANSAC = 2
WCZESNE_POKRYCIE = 0.97
WCZESNE_ODLEGLOSC = 2.0
MAX_HIPOTEZ = 5  # hipotezy oceniane pokryciem po 1. etapie ICP (pozy symetryczne maja podobny fitness)
KATY = 12  # przeglad obrotu wokol osi co 30 st.
ICP_NA_RAMKE = 4  # zgrubne ICP z 4 katow (co >= 90 st.) na kazda z 6 ramek (3 osie x 2 zwroty)
PROG_HIPOTEZY = 0.9  # kolejna hipoteza oceniana, gdy jej fitness >= 0,9 x najlepszej
PROG_ZGRUBNY = 0.7  # fitness zgrubny (0,25 mm od siatki) ponizej = odrzucony (zmierzone: wlasciwe >= 0,84)
PROG_WYRAZNOSCI = 0.05  # os PCA nieokreslona -> zgrubne FPFH + RANSAC
PUNKTY_OCENY = 4_000  # pokrycie hipotez (blad udzialu ok. 0,002 przy 0,99)
PUNKTY_POKRYCIA = 12_000  # pokrycie koncowe (blad udzialu ok. 0,001 przy 0,99)
ZIARNO = 0
DRUGI_ETAP_RANO = 2  # drugi etap: najwyzej tyle x max_kandydatow kolejnych wpisow
DRUGI_ETAP_WIECZOR = 1


class _Projekt:
    """Chmury projektu przeskalowanego o k; gesta probka (cel 2. etapu ICP) liczona dopiero, gdy potrzebna."""

    def __init__(self, wpis: WpisPuli, voxel: float):
        self.wpis = wpis
        self.rzadka = _d.probka_projektu(wpis.siatka, wpis.wspolczynnik, _d.PUNKTY_RZADKIE).voxel_down_sample(voxel)
        self.rzadka.normalize_normals()
        srodek, R, _ = _d.osie(np.asarray(self.rzadka.points))
        self.uklad = (srodek, R)
        self.fpfh: _d.ChmuraCech | None = None
        self._gesta = None

    @property
    def gesta(self) -> o3d.geometry.PointCloud:
        if self._gesta is None:
            self._gesta = _d.probka_projektu(self.wpis.siatka, self.wpis.wspolczynnik)
        return self._gesta


def _projekt(wpis: WpisPuli, voxel: float, pamiec: dict) -> _Projekt:
    klucz = (wpis.projekt_id, round(float(wpis.wspolczynnik), 6), voxel, id(wpis.siatka))
    if klucz not in pamiec:
        pamiec[klucz] = _Projekt(wpis, voxel)
    return pamiec[klucz]


def _podzbior(punkty: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    return punkty if len(punkty) <= n else punkty[rng.choice(len(punkty), n, replace=False)]


class _Fragment:
    """Dane fragmentu liczone raz na wywolanie dopasuj."""

    def __init__(self, fragment: trimesh.Trimesh, voxel: float):
        gladkie = _d.wygladz(np.asarray(fragment.vertices, dtype=np.float64), np.asarray(fragment.faces))
        probka = _podzbior(gladkie, PUNKTY_POKRYCIA, np.random.default_rng(ZIARNO))
        self.probka = probka
        self.do_oceny = probka[:PUNKTY_OCENY]
        self.pc = _d.chmura(gladkie)
        self.zgrubna = self.pc.voxel_down_sample(3 * voxel)
        self.gesta = self.pc.voxel_down_sample(_d.VOXEL_ICP_MM)
        self.uklady, self.wyraznosc = _d.uklady_osi(np.asarray(self.gesta.points))
        self.fpfh = None
        self.voxel = voxel


def _ocen_wpis(frag: _Fragment, wpis: WpisPuli, prog_min: float, prog_mm: float, pamiec: dict) -> Kandydat | None:
    """Najlepsza poza projektu wpisu wobec fragmentu: hipotezy PCA (awaryjnie RANSAC), ICP, pokrycie.

    None = odrzucony po zgrubnym wyrownaniu (fitness < PROG_ZGRUBNY przy wyraznej osi fragmentu).
    """
    proj = _projekt(wpis, frag.voxel, pamiec)
    scena = _d.scena(wpis.siatka)
    S = np.diag([float(wpis.wspolczynnik)] * 3 + [1.0])
    najlepszy = None  # (pokrycie oceny, rms, T fragment -> projekt)

    def ocen(T0):
        # 1. etap ICP (0,5 mm) na rzadkiej chmurze projektu wystarcza do wyboru hipotezy
        nonlocal najlepszy
        T_f2p, rms = _d.icp(frag.gesta, proj.rzadka, T0, etapy=_d.ETAPY_ICP_MM[:1])
        pokr = _d.pokrycie(frag.do_oceny, wpis.siatka, np.linalg.inv(T_f2p) @ S, prog_mm, scena)
        if najlepszy is None or (pokr, -rms) > (najlepszy[0], -najlepszy[1]):
            najlepszy = (pokr, rms, T_f2p)

    hipotezy = _d.hipotezy_pca(frag.zgrubna, frag.uklady, proj.rzadka, proj.uklad, katy=KATY,
                               scena_projektu=scena, skala=float(wpis.wspolczynnik), liczba_icp=ICP_NA_RAMKE)
    os_niepewna = frag.wyraznosc < PROG_WYRAZNOSCI
    if not os_niepewna and (not hipotezy or hipotezy[0][0] < PROG_ZGRUBNY):
        return None
    for fit, T0 in hipotezy[:MAX_HIPOTEZ]:
        if fit < PROG_HIPOTEZY * hipotezy[0][0]:
            break
        ocen(T0)
    if os_niepewna and (najlepszy is None or najlepszy[0] < prog_min):
        if frag.fpfh is None:
            frag.fpfh = _d.cechy_fpfh(frag.pc, frag.voxel)
        if proj.fpfh is None:
            proj.fpfh = _d.cechy_fpfh(proj.gesta, frag.voxel)
        for proba in range(PROBY_RANSAC):
            ocen(_d.zgrubne_z_cech(frag.fpfh, proj.fpfh, frag.voxel, ziarno=_d.ZIARNO_RANSAC + proba))
            if najlepszy[0] >= prog_min:
                break

    # 2. etap ICP (0,1 mm) na gestej probce tylko dla wybranej hipotezy
    T_f2p, rms = _d.icp(frag.gesta, proj.gesta, najlepszy[2], etapy=_d.ETAPY_ICP_MM[1:])
    T = np.linalg.inv(T_f2p) @ S
    pokr = _d.pokrycie(frag.probka, wpis.siatka, T, prog_mm, scena)
    return Kandydat(wpis.projekt_id, float(wpis.wspolczynnik), T, float(pokr), float(rms))


def dopasuj(fragment: trimesh.Trimesh, pula: list[WpisPuli], ustawienia, tryb: str = "wieczor",
            pamiec: dict | None = None) -> WynikDopasowania:
    """Kandydaci z puli dla fragmentu (malejaco po pokryciu) i pewnosc identyfikacji.

    pamiec: opcjonalny slownik wywolujacego na chmury projektow (klucz projekt_id + k); bez niego
    cache zyje tylko w obrebie jednego wywolania (brak stanu globalnego).
    Gdy zaden kandydat filtra nie osiaga min_pokrycie (rano: 0,97), drugi etap sprawdza kolejne
    wpisy puli wg odleglosci cech bez progow pasuje (niepelny skan i ubytki psuja wymiary PCA).
    """
    d = ustawienia.dopasowanie
    prog_min = ranking.min_pokrycie(ustawienia, tryb)
    pamiec = {} if pamiec is None else pamiec
    voxel = float(d.voxel_fpfh_mm)

    cechy_fragmentu = policz(fragment)
    lista = filtr.kandydaci_z_odlegloscia(cechy_fragmentu, pula, ustawienia)
    frag = None
    kandydaci = []
    for i, (odl_cech, wpis) in enumerate(lista):
        frag = frag or _Fragment(fragment, voxel)
        k = _ocen_wpis(frag, wpis, prog_min, d.odleglosc_mm, pamiec)
        if k is None:
            continue
        kandydaci.append(k)
        if (k.pokrycie >= WCZESNE_POKRYCIE and i + 1 < len(lista)
                and lista[i + 1][0] > WCZESNE_ODLEGLOSC * odl_cech):
            break

    najlepsze = max((k.pokrycie for k in kandydaci), default=0.0)
    if najlepsze < (WCZESNE_POKRYCIE if tryb == "rano" else prog_min):
        # drugi etap: kolejne wpisy wg odleglosci cech bez progow pasuje (niepelny skan, ubytki)
        sprawdzone = {id(w) for _, w in lista}
        dalsze = [w for _, w in filtr.wedlug_odleglosci(cechy_fragmentu, pula) if id(w) not in sprawdzone]
        for wpis in dalsze[:(DRUGI_ETAP_RANO if tryb == "rano" else DRUGI_ETAP_WIECZOR) * d.max_kandydatow]:
            frag = frag or _Fragment(fragment, voxel)
            k = _ocen_wpis(frag, wpis, prog_min, d.odleglosc_mm, pamiec)
            if k is None:
                continue
            kandydaci.append(k)
            if k.pokrycie >= WCZESNE_POKRYCIE:
                break
    wynik = ranking.wynik(kandydaci, ustawienia, tryb)
    wynik.kandydaci = wynik.kandydaci[:d.max_kandydatow]
    return wynik
