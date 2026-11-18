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

Pula per praca (E3-A5, ``Pula.z_wpisow``): wpis puli = projekt STL x wspolczynnik swojego krazka (+ krazek, frezowanie_id,
projekt_id); ten sam STL z dwoma wspolczynnikami = dwie geometrie, wynik wskazuje wpis. Lekka czesc kazdej geometrii (cechy
filtra z profilem glebokosci, chmura 0,3 mm do rankingu wstepnego) jest w pamieci procesu i na dysku (``pamiec_puli``);
pelny ``Projekt`` (siatka, FPFH, scena promieni) powstaje tylko dla kandydatow, ktorzy przeszli filtr i ranking wstepny
(``ocena_wstepna``: przeglad obrotow + krotkie ICP punkt-plaszczyzna na ok. 300 punktach). Pula z folderu (dotychczasowe
wywolanie) dziala bez zmian - bez rankingu wstepnego.
"""
from __future__ import annotations

import collections.abc
import dataclasses
import math
import time
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import open3d as o3d
import trimesh
from scipy.spatial import ConvexHull, QhullError, cKDTree

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
# pula per praca (E3-A5): ranking wstepny i wybor wpisu wsrod wariantow tego samego STL (parametry robocze, nie progi [match])
WSTEPNY_PELNYCH = 4  # najwyzej tylu kandydatow po filtrze dostaje pelne dopasowanie (FPFH + RANSAC + ICP) w jednej turze
WSTEPNY_MARGINES = 0.15  # do pelnego dopasowania ida kandydaci z oceną wstepna >= najlepsza - tyle (i najwyzej WSTEPNY_PELNYCH)
WSTEPNY_TUR = 3  # gdy najlepszy po pelnym dopasowaniu ma pokrycie < prog_ostrzezenia_pokrycie: kolejna tura (nastepni z rankingu), najwyzej tyle tur
WSTEPNY_PUNKTOW = 300  # punkty fragmentu do oceny wstepnej (z chmury 0,5 mm, wybor staly)
WSTEPNY_VOXEL_PROJEKTU = 0.3  # mm: chmura projektu do oceny wstepnej (punkty + normalne; czesc lekka, na dysku)
WSTEPNY_OBROTOW = 8  # hipotezy obrotu wokol z (co 45 st., jak zgrubne_obroty); KAZDA dostaje krotkie ICP (przeglad bez ICP mylil obrot - pomiar E3-A5)
WSTEPNY_PUNKTOW_PRZEGLADU = 100  # punkty fragmentu w ICP wszystkich hipotez (co 3. z WSTEPNY_PUNKTOW)
WSTEPNY_ICP_PRZEGLADU = (1.0, 1.0, 0.6, 0.4)  # mm: odrzucanie par w krokach ICP wszystkich hipotez
WSTEPNY_OBROTOW_ICP = 2  # najlepsze hipotezy po przegladzie: dalsze ICP na WSTEPNY_PUNKTOW punktach
WSTEPNY_ICP_ODL = (0.6, 0.4, 0.25, 0.25, 0.25)  # mm: odrzucanie par w krokach dalszego ICP
WSTEPNY_ODL_SASIADA = 0.35  # mm: punkt liczy sie do oceny, gdy najblizszy punkt chmury projektu jest blizej niz tyle ...
WSTEPNY_PROG_MM = 0.1  # mm: ... i odleglosc od plaszczyzny stycznej projektu jest nie wieksza niz tyle
WARIANT_REMIS_POKRYCIA = 0.02  # warianty tego samego STL o pokryciach blizej niz tyle: rozstrzyga estymata skali (albo sa nierozroznialne)
UWAGA_RATUNEK = "żaden projekt nie przeszedł filtru wymiarów — dopasowano wszystkie"


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
    # E3-A5 (pula per praca): ``klucz`` = klucz geometrii w ``Pula.projekty`` (pula z folderu: = id); ``wspolczynnik`` geometrii;
    # ``wpisy`` = wpisy puli zgodne z wynikiem ({frezowanie_id, projekt_id, krazek, wspolczynnik}); ``frezowanie_id``, ``projekt_id``
    # i ``krazek`` tylko, gdy wszystkie wpisy z ``wpisy`` maja te sama wartosc (inaczej None - program nie zgaduje krazka ani zlecenia)
    klucz: str = ""
    wspolczynnik: float | None = None
    krazek: str | None = None
    frezowanie_id: int | None = None
    projekt_id: int | None = None
    wpisy: list = field(default_factory=list)
    pokrycie_wstepne: float | None = None  # ocena wstepna (pula per praca, gdy liczona); ``metoda = wstepny`` = bez pelnego dopasowania

    def __post_init__(self) -> None:
        if not self.klucz:
            self.klucz = self.id


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
        self._zbuduj_scene()
        self.drzewo = cKDTree(pts)
        self._profil: dict[int, tuple[list[float], float]] = {}  # cechy projektu przyciętego do głębokości k·KROK_PROFILU (filtr)

    def _zbuduj_scene(self) -> None:
        m2 = self.siatka
        mo = o3d.t.geometry.TriangleMesh(o3d.core.Tensor(np.asarray(m2.vertices, dtype=np.float32)), o3d.core.Tensor(np.asarray(m2.faces, dtype=np.int32)))
        self.scena = o3d.t.geometry.RaycastingScene()
        self.scena.add_triangles(mo)

    # --- pamiec podreczna (E3-A5): zapis i odtworzenie bez wczytywania pliku STL ---------------------------------------
    def do_tablic(self) -> tuple[dict, dict]:
        """(tablice, opis) - wszystko, z czego ``z_tablic`` odtwarza ten sam projekt bez pliku STL (bez sciezki i nazwy pliku)."""
        tab = {
            "V": np.asarray(self.siatka.vertices, dtype=np.float64), "F": np.asarray(self.siatka.faces, dtype=np.int64),
            "T0": np.asarray(self.T0, dtype=np.float64),
            "pts": np.asarray(self.chmura.points), "nrm": np.asarray(self.chmura.normals),
            "fpfh_pts": np.asarray(self.chmura_fpfh.points), "fpfh_nrm": np.asarray(self.chmura_fpfh.normals),
            "fpfh": np.asarray(self.fpfh.data),
        }
        opis = {"id": self.id, "wspolczynnik": float(self.wspolczynnik), "obrys_xy": [float(v) for v in self.obrys_xy],
                "wysokosc": float(self.wysokosc), "hull": float(self.hull), "cechy": dataclasses.asdict(self.cechy)}
        return tab, opis

    @classmethod
    def z_tablic(cls, tab, opis: dict, plik: Path | None = None) -> Projekt:
        """Projekt z tablic ``do_tablic`` (pamiec podreczna na dysku): te same punkty, cechy FPFH, siatka i transformacja."""
        pr = cls.__new__(cls)
        pr.plik = Path(plik) if plik is not None else None
        pr.id = opis["id"]
        pr.cechy = K.Projekt(**opis["cechy"])
        pr.cechy.id = pr.id
        pr.T0 = np.array(tab["T0"], dtype=np.float64)
        pr.siatka = trimesh.Trimesh(np.array(tab["V"], dtype=np.float64), np.array(tab["F"], dtype=np.int64), process=False)
        pr.wspolczynnik = float(opis["wspolczynnik"])
        pr.obrys_xy = [float(v) for v in opis["obrys_xy"]]
        pr.wysokosc = float(opis["wysokosc"])
        pr.hull = float(opis["hull"])
        pts = np.array(tab["pts"], dtype=np.float64)
        pr.chmura = _chmura(pts, np.array(tab["nrm"], dtype=np.float64))
        pr.chmura_fpfh = _chmura(np.array(tab["fpfh_pts"], dtype=np.float64), np.array(tab["fpfh_nrm"], dtype=np.float64))
        f = o3d.pipelines.registration.Feature()
        f.data = np.array(tab["fpfh"], dtype=np.float64)
        pr.fpfh = f
        pr.chmura_zgrubna = pr.chmura.voxel_down_sample(VOXEL_ZGRUBNE)
        pr._zbuduj_scene()
        pr.drzewo = cKDTree(pts)
        pr._profil = {}
        return pr

    def lekki(self) -> ProjektLekki:
        """Lekka czesc projektu (E3-A5): cechy filtra z profilem glebokosci dla kazdego kroku KROK_PROFILU (te same liczby co
        ``cechy_do_glebokosci``) i chmura WSTEPNY_VOXEL_PROJEKTU z normalnymi do oceny wstepnej.

        Profil liczony przyrostowo: otoczka czesci od brzegu do glebokosci k = otoczka (wierzcholki otoczki dla k - 1
        + punkty nowej warstwy) - ta sama otoczka i ten sam obrys co z wszystkich punktow (objetosc z qhull wprost, bez
        budowy siatki trimesh; roznica wzgledem ``cechy_do_glebokosci`` na poziomie bledu zaokraglen)."""
        Q = np.asarray(self.chmura.points)
        z = Q[:, 2]
        profil = []
        H = np.zeros((0, 3))
        k = 1
        while k * KROK_PROFILU < self.wysokosc:
            dol = -k * KROK_PROFILU
            nowe = Q[z >= dol] if k == 1 else Q[(z >= dol) & (z < -(k - 1) * KROK_PROFILU)]
            P = np.vstack([H, nowe])
            if int((z >= dol).sum()) < 4:
                profil.append((0.0, 0.0, 0.0))
                H = P
            else:
                _, boki = trimesh.bounds.oriented_bounds_2D(P[:, :2])
                try:
                    otoczka = ConvexHull(P)
                    hull, H = float(otoczka.volume), P[otoczka.vertices]
                except (QhullError, ValueError):  # punkty w jednej płaszczyźnie: otoczka bez objętości (jak cechy_do_glebokosci)
                    hull, H = 0.0, P
                a, b = sorted(float(v) for v in boki)
                profil.append((a, b, hull))
            k += 1
        pc = self.chmura.voxel_down_sample(WSTEPNY_VOXEL_PROJEKTU)
        N = np.asarray(pc.normals)
        N = N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
        return ProjektLekki(self.id, float(self.wspolczynnik), [float(v) for v in self.obrys_xy], float(self.wysokosc), float(self.hull),
                            np.asarray(profil, dtype=np.float64).reshape(-1, 3), np.asarray(pc.points, dtype=np.float64), N,
                            list(self.cechy.zeby), self.cechy.typ)

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


class ProjektLekki:
    """Lekka czesc projektu puli (E3-A5): cechy filtra wymiarow (obrys, wysokosc, otoczka i profil glebokosci) i chmura
    WSTEPNY_VOXEL_PROJEKTU z normalnymi do oceny wstepnej - w ukladzie puli (projekt x wspolczynnik, brzeg na z = 0).
    Wystarcza do ``filtr`` i ``ocena_wstepna``; pelny ``Projekt`` buduje ``pamiec_puli`` tylko dla kandydatow."""

    __slots__ = ("id", "wspolczynnik", "obrys_xy", "wysokosc", "hull", "profil", "punkty", "normalne", "zeby", "typ", "klucz_pamieci", "zrodlo", "_drzewo")

    def __init__(self, id: str, wspolczynnik: float, obrys_xy: list, wysokosc: float, hull: float, profil: np.ndarray, punkty: np.ndarray,
                 normalne: np.ndarray, zeby: list | None = None, typ: str = ""):
        self.id, self.wspolczynnik, self.obrys_xy, self.wysokosc, self.hull = id, wspolczynnik, obrys_xy, wysokosc, hull
        self.profil, self.punkty, self.normalne = profil, punkty, normalne
        self.zeby, self.typ = list(zeby or []), typ
        self.klucz_pamieci = ""  # nazwa wpisu w pamieci podrecznej (pamiec_puli)
        self.zrodlo: tuple | None = None  # (plik, orientacja) do zbudowania pelnego projektu - tylko w pamieci procesu (sciezka = dane osobowe)
        self._drzewo = None

    @property
    def drzewo(self) -> cKDTree:
        if self._drzewo is None:
            self._drzewo = cKDTree(self.punkty)
        return self._drzewo

    def cechy_do_glebokosci(self, glebokosc: float) -> tuple[list[float], float]:
        """Jak ``Projekt.cechy_do_glebokosci`` (z profilu policzonego raz dla kazdego kroku KROK_PROFILU)."""
        k = max(1, math.ceil(glebokosc / KROK_PROFILU - 1e-9))
        if k * KROK_PROFILU >= self.wysokosc or k > len(self.profil):
            return self.obrys_xy, self.hull
        a, b, h = self.profil[k - 1]
        return [float(a), float(b)], float(h)


def tekst_wspolczynnika(w: float) -> str:
    """Wspolczynnik w kluczu geometrii puli: 6 miejsc po przecinku bez zer na koncu (1,2 -> "1.2", 1,2215 -> "1.2215")."""
    return f"{round(float(w), 6):.6f}".rstrip("0").rstrip(".")


def _pole(o, nazwa: str, domyslne=None):
    """Pole wpisu puli: obiekt (``pula.Wpis``) albo slownik."""
    if isinstance(o, dict):
        return o.get(nazwa, domyslne)
    return getattr(o, nazwa, domyslne)


class _ProjektyPuli(collections.abc.Mapping):
    """``Pula.projekty`` puli per praca: klucz geometrii -> pelny ``Projekt`` budowany przy pierwszym uzyciu (pamiec_puli)."""

    def __init__(self, pula: Pula):
        self._pula = pula

    def __getitem__(self, klucz: str) -> Projekt:
        return self._pula.pamiec.projekt(self._pula.lekkie[klucz])

    def __iter__(self):
        return iter(self._pula.lekkie)

    def __len__(self) -> int:
        return len(self._pula.lekkie)

    def __contains__(self, klucz) -> bool:
        return klucz in self._pula.lekkie


class Pula:
    """Pula projektów. ``wspolczynnik`` — współczynnik skurczu wspólny dla puli; ``wspolczynniki`` (opcjonalnie)
    — współczynnik dla pojedynczych projektów: skrót projektu (``Projekt.id``) → współczynnik (np. z raportu MillBox
    każdej pracy); projekt bez wpisu dostaje współczynnik wspólny.

    Pula per praca (E3-A5): ``Pula.z_wpisow(wpisy, sciezki)`` - wpis = projekt x wspolczynnik krazka (``pula.Wpis`` z A4)."""

    per_praca = False  # pula z wpisow (z_wpisow); pula z folderu: False
    ranking_wstepny = False

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

    @classmethod
    def z_wpisow(cls, wpisy, sciezki: dict | None = None, orientacja: str = "auto", pamiec=None, wspolczynnik_domyslny: float | None = None,
                 ranking_wstepny: bool = True) -> Pula:
        """Pula per praca z wpisow puli dnia (``pula.Wpis`` z A4 albo slowniki z tymi polami): ``sha16``, ``wspolczynnik``,
        ``krazek``, ``frezowanie_id``, ``projekt_id``; plik STL z ``sciezki[projekt_id]`` (``KatalogPul.sciezki``) albo z pola
        ``plik`` wpisu.

        Geometria = (skrot ZAWARTOSCI pliku, wspolczynnik, orientacja): ten sam STL z dwoma wspolczynnikami = dwie geometrie
        (klucz ``<sha16>@<wspolczynnik>``), ten sam STL z tym samym wspolczynnikiem w kilku wpisach (dwa krazki o tej samej
        wartosci; rano ten sam plik w dwoch zleceniach) = jedna geometria z kilkoma wpisami (``wpisy_geometrii``). Klucz
        geometrii to samo ``sha16``, gdy STL ma w puli jeden wspolczynnik. Wpis bez wspolczynnika (i bez
        ``wspolczynnik_domyslny``), bez sciezki albo z plikiem, ktorego nie ma (folder usuniety - D17 recenzji A4), jest
        pominiety z licznikiem, nie blad. Skrot liczony z biezacej zawartosci pliku: inny niz ``sha16`` wpisu = licznik
        ``plik_zmieniony`` (geometria z biezacej zawartosci). ``pamiec`` = ``pamiec_puli.PamiecPuli`` (domyslnie bez dysku).
        """
        from . import pamiec_puli as PP

        t0 = time.time()
        pula = cls.__new__(cls)
        pula.per_praca = True
        pula.ranking_wstepny = bool(ranking_wstepny)
        pula.wspolczynnik = None
        pula.orientacja = orientacja
        pula.pamiec = pamiec if pamiec is not None else PP.PamiecPuli(None)
        pula.lekkie: dict[str, ProjektLekki] = {}
        pula.wpisy_geometrii: dict[str, list[dict]] = {}
        pula.opisy: dict[str, tuple[list, str]] = {}  # klucz -> (zeby, typ) z nazwy pliku tego wpisu
        lz = {"wpisow": 0, "geometrii": 0, "stl": 0, "bez_wspolczynnika": 0, "bez_sciezki": 0, "brak_pliku": 0, "plik_zmieniony": 0, "pominiete": 0,
              "geometrie_z_kilkoma_wpisami": 0, "stl_z_kilkoma_wspolczynnikami": 0}
        grupy: dict[tuple, dict] = {}
        for w in wpisy:
            lz["wpisow"] += 1
            wsp = _pole(w, "wspolczynnik")
            wsp = wspolczynnik_domyslny if wsp is None else wsp
            if wsp is None:
                lz["bez_wspolczynnika"] += 1
                continue
            pid = _pole(w, "projekt_id")
            plik = sciezki.get(pid) if sciezki and pid in sciezki else (_pole(w, "plik") or _pole(w, "sciezka"))
            if plik is None:
                lz["bez_sciezki"] += 1
                continue
            plik = Path(plik)
            if not plik.is_file():
                lz["brak_pliku"] += 1
                continue
            try:
                sha = pula.pamiec.skrot(plik)
            except OSError:
                lz["brak_pliku"] += 1
                continue
            if _pole(w, "sha16") and _pole(w, "sha16") != sha:
                lz["plik_zmieniony"] += 1
            znak = orientacja if orientacja != "auto" else ("e" if S.plik_exocad(plik.name) else "h")  # exocad: brzeg na dole z nazwy
            g = grupy.setdefault((sha, round(float(wsp), 6), znak), {"plik": plik, "wpisy": []})
            g["wpisy"].append({"frezowanie_id": _pole(w, "frezowanie_id"), "projekt_id": pid, "krazek": _pole(w, "krazek"), "wspolczynnik": round(float(wsp), 6)})
        sha_ile = collections.Counter(k[0] for k in grupy)
        sha_w_ile = collections.Counter(k[:2] for k in grupy)
        for (sha, wsp, znak), g in grupy.items():
            kl = sha if sha_ile[sha] == 1 else f"{sha}@{tekst_wspolczynnika(wsp)}" + (f"#{znak}" if sha_w_ile[(sha, wsp)] > 1 else "")
            try:
                lk = pula.pamiec.lekki(g["plik"], sha, wsp, orientacja)
            except ValueError:  # plik nie do wczytania (pusty, NaN, zerowa powierzchnia) - jak Pula z folderu
                lz["pominiete"] += len(g["wpisy"])
                continue
            pula.lekkie[kl] = lk
            pula.wpisy_geometrii[kl] = g["wpisy"]
            typ, zeby = K.typ_i_zeby_z_nazwy(g["plik"].name)
            pula.opisy[kl] = (zeby, typ)
            lz["geometrie_z_kilkoma_wpisami"] += len(g["wpisy"]) > 1
        lz["geometrii"] = len(pula.lekkie)
        lz["stl"] = len({lk.id for lk in pula.lekkie.values()})
        lz["stl_z_kilkoma_wspolczynnikami"] = sum(1 for n in collections.Counter(lk.id for lk in pula.lekkie.values()).values() if n > 1)
        pula.liczniki = lz
        pula.pominiete = lz["pominiete"]
        pula.projekty = _ProjektyPuli(pula)
        pula.czas_s = round(time.time() - t0, 2)
        return pula

    def opis(self) -> dict:
        """Liczby puli per praca do wyniku i na ekran (bez nazw plikow i sciezek)."""
        if not self.per_praca:
            return {"per_praca": False, "projekty": len(self), "wspolczynnik": self.wspolczynnik, "czas_s": self.czas_s}
        return {"per_praca": True, **self.liczniki, "czas_s": self.czas_s, "pamiec": dict(self.pamiec.statystyka)}


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
    wstepne: np.ndarray | None = None  # punkty do oceny wstepnej (pula per praca), wzgledem srodka c; liczone przy pierwszym uzyciu

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
    k = Kandydat(id=pr.id, zeby=pr.cechy.zeby, typ=pr.cechy.typ, wspolczynnik=pr.wspolczynnik)
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
# ranking wstepny (pula per praca, E3-A5)
# ----------------------------------------------------------------------------
def _punkty_wstepne(fr: FragmentDoDopasowania) -> np.ndarray:
    """Najwyzej WSTEPNY_PUNKTOW punktow chmury 0,5 mm fragmentu (wybor staly), wzgledem srodka c (jak przeglad obrotow)."""
    if fr.wstepne is None:
        X = np.asarray(fr.chmura_zgrubna.points, dtype=np.float64)
        if len(X) > WSTEPNY_PUNKTOW:
            X = X[np.sort(np.random.default_rng(0).choice(len(X), WSTEPNY_PUNKTOW, replace=False))]
        fr.wstepne = X - fr.c
    return fr.wstepne


def _obrot_z(a: float) -> np.ndarray:
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def _obroty_z_wektorow(W: np.ndarray) -> np.ndarray:
    """Macierze obrotu (K, 3, 3) z wektorow obrotu (K, 3) - wzor Rodriguesa, wsadowo."""
    th = np.linalg.norm(W, axis=1)
    k = W / np.maximum(th, 1e-12)[:, None]
    Kx = np.zeros((len(W), 3, 3))
    Kx[:, 0, 1], Kx[:, 0, 2], Kx[:, 1, 0], Kx[:, 1, 2], Kx[:, 2, 0], Kx[:, 2, 1] = -k[:, 2], k[:, 1], k[:, 2], -k[:, 0], -k[:, 1], k[:, 0]
    s, c = np.sin(th)[:, None, None], (1 - np.cos(th))[:, None, None]
    return np.eye(3)[None] + s * Kx + c * (Kx @ Kx)


def _icp_wstepne(X: np.ndarray, R: np.ndarray, t: np.ndarray, lk: ProjektLekki, odleglosci) -> tuple[np.ndarray, np.ndarray]:
    """Krotkie ICP punkt-plaszczyzna (Gauss-Newton, 6 parametrow) WSADOWO dla K hipotez (R: K x 3 x 3, t: K x 3) do chmury
    lekkiej projektu; w kroku j pary dalsze niz ``odleglosci[j]`` odrzucane; hipoteza z < 12 parami stoi w miejscu."""
    drzewo, Q, Nq = lk.drzewo, lk.punkty, lk.normalne
    K, n = len(R), len(X)
    for odl in odleglosci:
        Y = np.einsum("kij,nj->kni", R, X) + t[:, None, :]
        d, i = drzewo.query(Y.reshape(-1, 3), distance_upper_bound=odl)
        w = np.isfinite(d).reshape(K, n)
        i = np.where(np.isfinite(d), i, 0).reshape(K, n)
        nq = Nq[i]
        r = np.einsum("kni,kni->kn", Y - Q[i], nq) * w
        J = np.concatenate([np.cross(Y, nq), nq], axis=2) * w[..., None]
        A = np.einsum("kni,knj->kij", J, J) + 1e-9 * np.eye(6)[None]
        dx = np.linalg.solve(A, -np.einsum("kni,kn->ki", J, r)[..., None])[..., 0]
        dx[w.sum(axis=1) < 12] = 0.0
        dR = _obroty_z_wektorow(dx[:, :3])
        R, t = dR @ R, np.einsum("kij,kj->ki", dR, t) + dx[:, 3:]
    return R, t


def _wynik_wstepny(X: np.ndarray, R: np.ndarray, t: np.ndarray, lk: ProjektLekki) -> np.ndarray:
    """Dla K hipotez: udzial punktow X z punktem projektu blizej niz WSTEPNY_ODL_SASIADA i odlegloscia od plaszczyzny
    stycznej projektu najwyzej WSTEPNY_PROG_MM."""
    K, n = len(R), len(X)
    Y = np.einsum("kij,nj->kni", R, X) + t[:, None, :]
    d, i = lk.drzewo.query(Y.reshape(-1, 3), distance_upper_bound=WSTEPNY_ODL_SASIADA)
    w = np.isfinite(d).reshape(K, n)
    i = np.where(np.isfinite(d), i, 0).reshape(K, n)
    r = np.abs(np.einsum("kni,kni->kn", Y - lk.punkty[i], lk.normalne[i]))
    return ((r <= WSTEPNY_PROG_MM) & w).mean(axis=1)


def ocena_wstepna(fr: FragmentDoDopasowania, lk: ProjektLekki) -> float:
    """Szybka ocena pary fragment-projekt (kilka ms) do rankingu przed pelnym dopasowaniem w puli per praca.

    Srodki na siebie (jak ``zgrubne_obroty``: xy srodek obrysu, z brzeg), WSTEPNY_OBROTOW hipotez obrotu wokol z, kazda
    z krotkim ICP punkt-plaszczyzna na WSTEPNY_PUNKTOW_PRZEGLADU punktach (wsadowo), dalsze ICP dla WSTEPNY_OBROTOW_ICP
    najlepszych na WSTEPNY_PUNKTOW punktach; wynik = najlepszy udzial punktow fragmentu, ktore maja punkt projektu blizej
    niz WSTEPNY_ODL_SASIADA i leza najwyzej WSTEPNY_PROG_MM od jego plaszczyzny stycznej (0-1). Tylko do kolejnosci
    kandydatow - o wyniku dopasowania decyduje pelne ``dopasuj_pare`` (pokrycie przy odleglosc_max_mm)."""
    X = _punkty_wstepne(fr)
    if len(X) < 12 or len(lk.punkty) < 12:
        return 0.0
    Xp = X[:: max(1, len(X) // WSTEPNY_PUNKTOW_PRZEGLADU)]
    R = np.stack([_obrot_z(2 * math.pi * j / WSTEPNY_OBROTOW) for j in range(WSTEPNY_OBROTOW)])
    t = np.zeros((WSTEPNY_OBROTOW, 3))
    R, t = _icp_wstepne(Xp, R, t, lk, WSTEPNY_ICP_PRZEGLADU)
    naj = np.argsort(-_wynik_wstepny(Xp, R, t, lk), kind="stable")[:WSTEPNY_OBROTOW_ICP]
    R, t = _icp_wstepne(X, R[naj], t[naj], lk, WSTEPNY_ICP_ODL)
    return float(_wynik_wstepny(X, R, t, lk).max())


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


# ----------------------------------------------------------------------------
# pula per praca (E3-A5): kandydaci z wpisow, ranking wstepny, wybor wpisu
# ----------------------------------------------------------------------------
def _wpisy_kandydata(k: Kandydat, wpisy: list[dict]) -> None:
    """``k.wpisy`` = wpisy zgodne z wynikiem; ``frezowanie_id`` / ``projekt_id`` / ``krazek`` tylko, gdy wszystkie wpisy sie zgadzaja."""
    k.wpisy = [dict(w) for w in wpisy]
    for pole in ("frezowanie_id", "projekt_id", "krazek"):
        wart = {w.get(pole) for w in k.wpisy}
        setattr(k, pole, next(iter(wart)) if len(wart) == 1 else None)


def _kandydat_puli(pula: Pula, kl: str, k: Kandydat | None = None, **pola) -> Kandydat:
    lk = pula.lekkie[kl]
    zeby, typ = pula.opisy.get(kl, (lk.zeby, lk.typ))
    if k is None:
        k = Kandydat(id=lk.id, zeby=list(zeby), typ=typ, **pola)
    else:
        k.zeby, k.typ = list(zeby), typ
    k.klucz, k.wspolczynnik = kl, lk.wspolczynnik
    _wpisy_kandydata(k, pula.wpisy_geometrii.get(kl, []))
    return k


def _pelne_dopasowanie(fr: FragmentDoDopasowania, pula: Pula, kl: str, ust: dict, seed: int, uwagi: list[str]) -> Kandydat:
    try:
        pr = pula.projekty[kl]
    except (ValueError, OSError) as e:  # plik zmieniony albo usuniety po zbudowaniu puli (i brak w pamieci na dysku)
        uwagi.append(f"projekt {pula.lekkie[kl].id} pominiety: nie da sie go wczytac ({type(e).__name__})")
        return _kandydat_puli(pula, kl, metoda="blad")
    return _kandydat_puli(pula, kl, k=dopasuj_pare(fr, pr, ust, seed))


def _kandydaci_per_praca(fr: FragmentDoDopasowania, pula: Pula, ust: dict, seed: int, uwagi: list[str]) -> list[Kandydat]:
    """Filtr wymiarow na czesci lekkiej kazdej geometrii; gdy po filtrze zostaje wiecej niz WSTEPNY_PELNYCH - ranking
    wstepny (``ocena_wstepna``) i pelne dopasowanie tylko najlepszych (ocena >= najlepsza - WSTEPNY_MARGINES, najwyzej
    WSTEPNY_PELNYCH); gdy najlepszy z nich ma pokrycie < prog_ostrzezenia_pokrycie - kolejna tura z rankingu (najwyzej
    WSTEPNY_TUR tur). Pozostali: ``metoda = wstepny``, pokrycie 0 (jak odrzuceni filtrem). Ratunek (nikt nie przeszedl
    filtru) idzie ta sama droga po calej puli."""
    m = ust["match"]
    lekkie = pula.lekkie
    wyn_filtru = {kl: filtr(fr, lk, ust) for kl, lk in lekkie.items()}
    zbior = [kl for kl, (ok, _) in wyn_filtru.items() if ok]
    ust_pary = ust
    if not zbior:
        uwagi.append(UWAGA_RATUNEK)
        zbior = list(lekkie)
        ust_pary = {**ust, "match": {**m, "filtr_wymiar_mm": 1e9, "filtr_objetosc_udzial": 1e9}}
    w_zbiorze = set(zbior)
    kandydaci = {kl: _kandydat_puli(pula, kl, filtr_ok=False, powod_filtru=powod, metoda="filtr")
                 for kl, (_, powod) in wyn_filtru.items() if kl not in w_zbiorze}
    wstepne: dict[str, float] = {}
    if pula.ranking_wstepny and len(zbior) > WSTEPNY_PELNYCH:
        wstepne = {kl: ocena_wstepna(fr, lekkie[kl]) for kl in zbior}
        kolejka = sorted(zbior, key=lambda kl: (-wstepne[kl], kl))
        tura = [kl for kl in kolejka[:WSTEPNY_PELNYCH] if wstepne[kl] >= wstepne[kolejka[0]] - WSTEPNY_MARGINES]
    else:
        kolejka, tura = list(zbior), list(zbior)
    w_turze = set(tura)
    reszta = [kl for kl in kolejka if kl not in w_turze]
    for nr in range(1, WSTEPNY_TUR + 1):
        for kl in tura:
            kandydaci[kl] = _pelne_dopasowanie(fr, pula, kl, ust_pary, seed, uwagi)
        najl = max((kandydaci[kl].pokrycie for kl in zbior if kl in kandydaci), default=0.0)
        if najl >= m["prog_ostrzezenia_pokrycie"] or not reszta or nr == WSTEPNY_TUR:
            break
        tura, reszta = reszta[:WSTEPNY_PELNYCH], reszta[WSTEPNY_PELNYCH:]
    for kl in reszta:
        kandydaci[kl] = _kandydat_puli(pula, kl, metoda="wstepny")
    for kl, w in wstepne.items():
        kandydaci[kl].pokrycie_wstepne = round(w, 4)
    return [kandydaci[kl] for kl in lekkie if kl in kandydaci]


def _wybierz_wariant(P: np.ndarray, fr: FragmentDoDopasowania, kandydaci: list[Kandydat], pula: Pula, m: dict, bez_korekty: str,
                     uwagi: list[str]) -> None:
    """Ten sam STL w puli z kilkoma wspolczynnikami (krazkami): wpis = wariant o wspolczynniku najblizszym estymacie ze skanu
    (``KorektaSkali.wspolczynnik_ze_skanu``), o ile jego pokrycie nie jest nizsze niz najlepszego o wiecej niz
    WARIANT_REMIS_POKRYCIA. Warianty blizej siebie niz dokladnosc estymaty (SKALA_DOKLADNOSC_PROC) albo - bez estymaty -
    o pokryciach blizej niz WARIANT_REMIS_POKRYCIA sa nierozroznialne: ich wpisy ida razem do ``wpisy`` najlepszego
    kandydata, a ``frezowanie_id`` / ``krazek`` zostaja puste (program nie zgaduje)."""
    k1 = kandydaci[0]
    if k1.transformacja is None:
        return
    grupa = [k for k in kandydaci if k.id == k1.id and k.transformacja is not None]
    najl, rowne = k1, []
    if len(grupa) > 1:
        est = next((k.skala.wspolczynnik_ze_skanu for k in grupa
                    if k.skala is not None and k.skala.wspolczynnik_ze_skanu is not None and not k.skala.niepewna), None)
        if est is not None:
            odl = {k.klucz: abs(est / k.wspolczynnik - 1.0) * 100.0 for k in grupa}
            grupa.sort(key=lambda k: (odl[k.klucz], -k.pokrycie))
            if grupa[0] is not k1:
                if grupa[0].skala is None:
                    koryguj_skale(P, fr, grupa[0], pula.projekty[grupa[0].klucz], m, bez_korekty)
                if grupa[0].pokrycie >= k1.pokrycie - WARIANT_REMIS_POKRYCIA:
                    najl = grupa[0]
                    kandydaci.remove(najl)
                    kandydaci.insert(0, najl)
            rowne = [k for k in grupa if k is not najl and abs(odl[k.klucz] - odl[najl.klucz]) < SKALA_DOKLADNOSC_PROC]
        else:
            rowne = [k for k in grupa if k is not k1 and k.pokrycie >= k1.pokrycie - WARIANT_REMIS_POKRYCIA]
    if rowne:
        _wpisy_kandydata(najl, najl.wpisy + [w for k in rowne for w in k.wpisy])
        uwagi.append(f"ten sam projekt w puli z {len(rowne) + 1} wspolczynnikami blizszymi niz dokladnosc estymaty skali - wpisu (krazka) nie rozstrzygnieto")
    elif len(najl.wpisy) > 1:
        uwagi.append(f"ten sam projekt w {len(najl.wpisy)} wpisach puli o tym samym wspolczynniku - krazek albo zlecenie do wskazania")


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
    per_praca = getattr(pula, "per_praca", False)
    if per_praca:
        kandydaci = _kandydaci_per_praca(fr, pula, ust, seed, uwagi)
    else:
        kandydaci = [dopasuj_pare(fr, pr, ust, seed) for pr in pula.projekty.values()]
        if not any(k.filtr_ok for k in kandydaci):
            uwagi.append(UWAGA_RATUNEK)
            for k, pr in zip(kandydaci, pula.projekty.values()):
                k.filtr_ok = True
                kk = dopasuj_pare(fr, pr, {**ust, "match": {**m, "filtr_wymiar_mm": 1e9, "filtr_objetosc_udzial": 1e9}}, seed)
                k.pokrycie, k.rms_mm, k.pokrycie_odwrotne, k.transformacja, k.metoda = kk.pokrycie, kk.rms_mm, kk.pokrycie_odwrotne, kk.transformacja, kk.metoda
    kandydaci.sort(key=lambda k: (-k.pokrycie, k.rms_mm))
    # korekta skali ze skanu: najlepszy kandydat, a drugi tylko gdy ranking jest niepewny (pokrycia blisko siebie, jak przy
    # błędzie współczynnika); obcy projekt dostaje skalę poza oknem i zostaje bez korekty (T7: 1,36–1,46 zamiast 1,22)
    for i, k in enumerate(list(kandydaci[:SKALA_KANDYDATOW])):
        if k.transformacja is not None and (i == 0 or k.pokrycie >= SKALA_REMIS * kandydaci[0].pokrycie):
            koryguj_skale(P, fr, k, pula.projekty[k.klucz], m, bez_korekty)
    kandydaci.sort(key=lambda k: (-k.pokrycie, k.rms_mm))
    if per_praca:
        _wybierz_wariant(P, fr, kandydaci, pula, m, bez_korekty, uwagi)
    sk = kandydaci[0].skala
    if sk is not None and sk.ostrzezenie:
        uwagi.append(f"skala: praca {'większa' if sk.poprawka_proc > 0 else 'mniejsza'} o {abs(sk.poprawka_proc):.2f} % niż projekt × współczynnik "
                     f"(próg ostrzeżenia {m['korekta_skali_ostrzezenie_proc']:g} %) — sprawdź współczynnik / krążek"
                     + ("" if sk.zastosowana else f"; korekty nie zastosowano: {sk.powod}"))
    p1 = kandydaci[0].pokrycie
    if per_praca:  # pewnosc wzgledem innego projektu: wariant tego samego STL (inny krazek) nie jest konkurentem
        p2 = max((k.pokrycie for k in kandydaci[1:] if k.id != kandydaci[0].id), default=0.0)
    else:
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
