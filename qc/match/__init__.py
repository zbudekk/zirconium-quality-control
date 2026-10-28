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

# Progi zalezne od danych sa w ustawieniach ([dopasowanie] prog_zgrubny, wczesne_pokrycie,
# prog_wyraznosci_osi); ponizej parametry algorytmu.
PROBY_RANSAC = 2
WCZESNE_ODLEGLOSC = 2.0
MAX_HIPOTEZ = 5  # hipotezy oceniane pokryciem po 1. etapie ICP (pozy symetryczne maja podobny fitness)
KATY = 12  # przeglad obrotu wokol osi co 30 st.
ICP_NA_RAMKE = 4  # zgrubne ICP z 4 katow (co >= 90 st.) na kazda z 6 ramek (3 osie x 2 zwroty)
PROG_HIPOTEZY = 0.9  # kolejna hipoteza oceniana, gdy jej fitness >= 0,9 x najlepszej
PUNKTY_OCENY = 4_000  # pokrycie hipotez (blad udzialu ok. 0,002 przy 0,99)
PUNKTY_POKRYCIA = 12_000  # pokrycie koncowe (blad udzialu ok. 0,001 przy 0,99)
ZIARNO = 0
DRUGI_ETAP_WIECZOR = 1  # wieczorem drugi etap najwyzej 1 x max_kandydatow wpisow; rano bez limitu


class _Projekt:
    """Chmury i scena projektu przeskalowanego o k; gesta probka liczona dopiero, gdy potrzebna."""

    def __init__(self, wpis: WpisPuli, voxel: float):
        self.siatka = wpis.siatka
        self.k = float(wpis.wspolczynnik)
        self.rzadka = _d.probka_projektu(self.siatka, self.k, _d.PUNKTY_RZADKIE).voxel_down_sample(voxel)
        self.rzadka.normalize_normals()
        self.promien = voxel
        srodek, R, _ = _d.osie(np.asarray(self.rzadka.points))
        self.uklad = (srodek, R)
        self.fpfh: _d.ChmuraCech | None = None
        self._gesta = None
        self._scena = None
        self._odleglosc = None

    @property
    def gesta(self) -> o3d.geometry.PointCloud:
        if self._gesta is None:
            self._gesta = _d.probka_projektu(self.siatka, self.k)
        return self._gesta

    @property
    def odleglosc(self) -> _d.OdlegloscOdChmury:
        """Szybka odleglosc od chmury rzadkiej (etap zgrubny, bez BVH siatki)."""
        if self._odleglosc is None:
            self._odleglosc = _d.OdlegloscOdChmury(self.rzadka, self.promien)
        return self._odleglosc

    @property
    def scena(self):
        if self._scena is None:
            self._scena = _d.scena(self.siatka)
        return self._scena


def _projekt(wpis: WpisPuli, voxel: float, pamiec: dict) -> _Projekt:
    """Dane projektu z pamieci; klucz (projekt_id, k, voxel) - pod jednym projekt_id ta sama siatka."""
    klucz = (wpis.projekt_id, round(float(wpis.wspolczynnik), 6), voxel)
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
        self.wpisy_ransac = 0
        self.voxel = voxel


def _skala(wpis) -> np.ndarray:
    return np.diag([float(wpis.wspolczynnik)] * 3 + [1.0])


def _dokoncz(frag: _Fragment, proj: _Projekt, wpis: WpisPuli, T_f2p: np.ndarray, prog_mm: float) -> Kandydat:
    """2. etap ICP (0,1 mm) na gestej probce projektu i pokrycie koncowe."""
    T_f2p, rms = _d.icp(frag.gesta, proj.gesta, T_f2p, etapy=_d.ETAPY_ICP_MM[1:])
    T = np.linalg.inv(T_f2p) @ _skala(wpis)
    pokr = _d.pokrycie(frag.probka, wpis.siatka, T, prog_mm, proj.scena)
    return Kandydat(wpis.projekt_id, float(wpis.wspolczynnik), T, float(pokr), float(rms))


def _ocen_wpis(frag: _Fragment, wpis: WpisPuli, prog_min: float, d, pamiec: dict) -> Kandydat | None:
    """Najlepsza poza projektu wpisu wobec fragmentu: hipotezy PCA albo RANSAC, ICP, pokrycie.

    None = odrzucony po zgrubnym wyrownaniu (fitness < prog_zgrubny przy wyraznej osi fragmentu).
    """
    proj = _projekt(wpis, frag.voxel, pamiec)
    S = _skala(wpis)
    najlepszy = None  # (pokrycie oceny, rms, T fragment -> projekt)

    def ocen(T0):
        # 1. etap ICP (0,5 mm) na rzadkiej chmurze projektu wystarcza do wyboru hipotezy
        nonlocal najlepszy
        T_f2p, rms = _d.icp(frag.gesta, proj.rzadka, T0, etapy=_d.ETAPY_ICP_MM[:1])
        pokr = _d.pokrycie(frag.do_oceny, wpis.siatka, np.linalg.inv(T_f2p) @ S, d.odleglosc_mm, proj.scena)
        if najlepszy is None or (pokr, -rms) > (najlepszy[0], -najlepszy[1]):
            najlepszy = (pokr, rms, T_f2p)

    if frag.wyraznosc < d.prog_wyraznosci_osi and frag.wpisy_ransac < d.max_kandydatow:
        # zabezpieczenie: os PCA fragmentu nieokreslona -> zgrubne FPFH + RANSAC (2 proby, rozne ziarna);
        # najwyzej max_kandydatow wpisow na wywolanie (rano drugi etap bez limitu), dalej PCA
        frag.wpisy_ransac += 1
        if frag.fpfh is None:
            frag.fpfh = _d.cechy_fpfh(frag.pc, frag.voxel)
        if proj.fpfh is None:
            proj.fpfh = _d.cechy_fpfh(proj.gesta, frag.voxel)
        for proba in range(PROBY_RANSAC):
            ocen(_d.zgrubne_z_cech(frag.fpfh, proj.fpfh, frag.voxel, ziarno=_d.ZIARNO_RANSAC + proba))
            if najlepszy[0] >= prog_min:
                break
    else:
        # zgrubne ICP raz; sito: fitness od chmury rzadkiej (bez BVH siatki) >= prog_sita,
        # potem fitness tych samych poz od siatki (scena) >= prog_zgrubny
        hipotezy = _d.hipotezy_pca(frag.zgrubna, frag.uklady, proj.rzadka, proj.uklad, katy=KATY,
                                   odleglosc=proj.odleglosc, liczba_icp=ICP_NA_RAMKE)
        if not hipotezy or hipotezy[0][0] < d.prog_sita:
            return None
        hipotezy = _d.przelicz_fitness(frag.zgrubna, hipotezy, _d.odleglosc_od_sceny(proj.scena, proj.k))
        if hipotezy[0][0] < d.prog_zgrubny:
            return None
        for fit, T0 in hipotezy[:MAX_HIPOTEZ]:
            if fit < PROG_HIPOTEZY * hipotezy[0][0]:
                break
            ocen(T0)
    return _dokoncz(frag, proj, wpis, najlepszy[2], d.odleglosc_mm)


def _obrot_180(frag: _Fragment, wpis: WpisPuli, top: Kandydat, d, pamiec: dict) -> Kandydat:
    """Kontrola pozy obroconej o 180 st. wokol osi wyroznionej projektu (korona prawie symetryczna).

    Poza obrocona (po ICP) zastepuje top-1 tylko przy pokryciu wiekszym o > margines_obrotu_180; rms nie
    rozstrzyga (zmierzone: zdominowane szumem). Pewnosci nie zmienia.
    """
    proj = _projekt(wpis, frag.voxel, pamiec)
    S = _skala(wpis)
    T_f2p = np.linalg.inv(top.T_projekt_do_fragmentu @ np.linalg.inv(S))
    srodek, R = proj.uklad
    os_ = R[:, 2]
    M = np.eye(4)
    M[:3, :3] = 2 * np.outer(os_, os_) - np.eye(3)
    M[:3, 3] = srodek - M[:3, :3] @ srodek
    T1, _ = _d.icp(frag.gesta, proj.rzadka, M @ T_f2p, etapy=_d.ETAPY_ICP_MM[:1])
    inny = _dokoncz(frag, proj, wpis, T1, d.odleglosc_mm)
    probne = np.asarray(frag.zgrubna.points)
    przesuniecie = np.max(np.linalg.norm(
        _d.przenies(probne, np.linalg.inv(inny.T_projekt_do_fragmentu))
        - _d.przenies(probne, np.linalg.inv(top.T_projekt_do_fragmentu)), axis=1))
    if przesuniecie < d.obrot_inna_poza_mm or inny.pokrycie - top.pokrycie <= d.margines_obrotu_180:
        return top
    return inny


def dopasuj(fragment: trimesh.Trimesh, pula: list[WpisPuli], ustawienia, tryb: str = "wieczor",
            pamiec: dict | None = None) -> WynikDopasowania:
    """Kandydaci z puli dla fragmentu (malejaco po pokryciu) i pewnosc identyfikacji.

    pamiec: opcjonalny slownik wywolujacego na dane projektow, klucz (projekt_id, k, voxel) - pod tym
    samym projekt_id musi byc ta sama siatka; bez niego pamiec zyje tylko w obrebie wywolania.
    Gdy zaden kandydat filtra nie osiaga min_pokrycie (rano: wczesne_pokrycie), drugi etap sprawdza
    kolejne wpisy puli wg odleglosci cech bez progow pasuje (niepelny skan i ubytki psuja wymiary PCA).
    """
    d = ustawienia.dopasowanie
    prog_min = ranking.min_pokrycie(ustawienia, tryb)
    pamiec = {} if pamiec is None else pamiec
    voxel = float(d.voxel_fpfh_mm)

    cechy_fragmentu = policz(fragment)
    lista = filtr.kandydaci_z_odlegloscia(cechy_fragmentu, pula, ustawienia)
    frag = None
    kandydaci, wpisy = [], {}
    for i, (odl_cech, wpis) in enumerate(lista):
        frag = frag or _Fragment(fragment, voxel)
        k = _ocen_wpis(frag, wpis, prog_min, d, pamiec)
        if k is None:
            continue
        kandydaci.append(k)
        wpisy[id(k)] = wpis
        if (k.pokrycie >= d.wczesne_pokrycie and i + 1 < len(lista)
                and lista[i + 1][0] > WCZESNE_ODLEGLOSC * odl_cech):
            break

    najlepsze = max((k.pokrycie for k in kandydaci), default=0.0)
    if najlepsze < (d.wczesne_pokrycie if tryb == "rano" else prog_min):
        # drugi etap: kolejne wpisy wg odleglosci cech bez progow pasuje (niepelny skan, ubytki);
        # rano bez limitu liczby - przerwanie dopiero po pokryciu >= wczesne_pokrycie
        sprawdzone = {id(w) for _, w in lista}
        dalsze = [w for _, w in filtr.wedlug_odleglosci(cechy_fragmentu, pula) if id(w) not in sprawdzone]
        if tryb != "rano":
            dalsze = dalsze[:DRUGI_ETAP_WIECZOR * d.max_kandydatow]
        for wpis in dalsze:
            frag = frag or _Fragment(fragment, voxel)
            k = _ocen_wpis(frag, wpis, prog_min, d, pamiec)
            if k is None:
                continue
            kandydaci.append(k)
            wpisy[id(k)] = wpis
            if k.pokrycie >= d.wczesne_pokrycie:
                break

    uporzadkowani = ranking.uporzadkuj(kandydaci)
    if tryb == "wieczor" and uporzadkowani and uporzadkowani[0].pokrycie >= prog_min:
        # tylko wieczorem (T idzie do inspect); rano liczy sie projekt, nie poza
        top = uporzadkowani[0]
        uporzadkowani[0] = _obrot_180(frag, wpisy[id(top)], top, d, pamiec)
    wynik = ranking.wynik(uporzadkowani, ustawienia, tryb)
    wynik.kandydaci = wynik.kandydaci[:d.max_kandydatow]
    return wynik
