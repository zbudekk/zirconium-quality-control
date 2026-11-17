"""inspect — ukruszenia brzegu pracy dwiema metodami, drgnięcie, poprawka ręczna.

Wejście: fragment skanu (punkty z normalnymi w układzie płytki, z ``plate``), projekt z puli
(``match.Projekt``: siatka × współczynnik brzegiem do góry, brzeg na z = 0) i transformacja
(projekt × w) → płytka z najlepszego kandydata ``match``, pokrycie z ``match``.

Metoda A — mapa odchyłek: odległość ze znakiem każdego punktu skanu od powierzchni projektu
(ujemna = pod powierzchnią, czyli brak materiału). Ubytek = plama punktów ≥ ``prog_glebokosci_mm``
pod powierzchnią, średnica ``srednica_min_mm…srednica_max_mm``, z ostrą krawędzią (w pierścieniu
``krawedz_pas_mm`` wokół plamy odchyłka wraca do ~0), w pasie ``pas_brzegu_mm`` od brzegu albo na
ostrej krawędzi projektu. Plama bez ostrej krawędzi i szersza niż ``poprawka_min_mm`` = poprawka
ręczna (osobny status); plama szersza niż ``srednica_max_mm`` = „sprawdź ułożenie”; plama na
granicy danych skanu (brak pierścienia) = „brak danych”, nigdy ubytek.

Metoda B — ciągłość linii brzegu: linia brzegu = gęsta próbka powierzchni projektu w pasie
0…``pas_brzegu_mm`` od brzegu (obwód z brzegiem włącznie; ostra krawędź brzegu nie da się wyciąć
z siatek exocad — zmierzone: 7 z 17 projektów ma < 5 mm ostrych krawędzi przy brzegu). Dla każdego
punktu linii: odległość do najbliższego punktu skanu. ≤ ``wciecie_min_mm`` = linia ciągła; większa
i najbliższy punkt skanu leży pod powierzchnią projektu = wcięcie (ukruszenie); większa, a skan leży
obok albo daleko = brak odcinka linii („brak danych”, nigdy ubytek). Odcinek wcięcia liczy się, gdy
≥ 50 % jego otoczenia na linii ma ciągły skan.

Drgnięcie (podwójna powierzchnia): udział komórek 1 mm, w których ≥ ``drgniecie_udzial_w_komorce``
punktów ma |odchyłkę| > ``drgniecie_odchylka_mm``; powyżej ``drgniecie_udzial_obszaru`` → „skan ponownie”
(odchyłki rozmyte na dużej części pracy, nie w jednej plamie).

Kolejność: drgnięcie → jakość dopasowania (pokrycie < ``[match] prog_akceptacji_pokrycie`` →
„popraw ułożenie”, ubytki nieliczone) → metoda A i B → decyzja: CZERWONE, gdy obie metody wskazują
to samo miejsce albo wcięcie brzegu ≥ ``wciecie_pewne_mm``; ŻÓŁTE „sprawdź”, gdy tylko jedna.
Progi wyłącznie w ``ustawienia.toml [inspect]``.

Pas brzegu od linii brzegu (P2, 15.11.2026; ``pas_brzegu_od`` = ``linia``): pas ``pas_brzegu_mm`` liczy się jako
odległość od linii krawędzi brzegu KAŻDEGO filaru projektu (moduł ``krawedz``: korona 1 pętla, most — pętla na filar,
korona implantowa — obwód powierzchni przylegania), a nie od płaszczyzny z = 0: metoda A przyjmuje plamę, której środek
leży ≤ pas od linii, metoda B próbkuje powierzchnię projektu ≤ pas od linii. Dla każdego filaru liczone jest, jaka część
jego linii została sprawdzona (linia projektu zweryfikowana ORAZ dane skanu przy linii); filar z udziałem
< ``brzeg_min_sprawdzony`` albo z odcinkiem bez sprawdzenia dłuższym niż ``brzeg_max_przerwa_mm`` (także: projekt bez
wyznaczonej linii) daje status ``nie_sprawdzono`` — gniazdo nie jest zielone; brak danych nigdy nie daje czerwonego.
``pas_brzegu_od`` = ``plaszczyzna`` zostawia sposób sprzed P2 (do porównań przed / po).

Tryb domyślny ``linia_i_plaszczyzna`` (16.11.2026, po pomiarze P2: przy samej linii 29 % prac całych dostawało
„nie sprawdzono” z powodu niepełnych linii projektu przy łącznikach mostów, a ubytki ścian przęseł i łączników wypadały
z kontroli): pas brzegu = suma pasa od linii każdego filaru i pasa sprzed P2 (z = 0 … −pas) — zasięg nigdy nie jest
mniejszy niż przed P2, a głęboki brzeg filarów dochodzi. „Nie sprawdzono” daje wtedy tylko brak danych SKANU przy linii
brzegu; niepewna linia projektu (nasze ograniczenie, nie skanu) trafia do uwag, a tam działa pas od płaszczyzny.
Projekt bez wyznaczonej linii = pas sprzed P2.
"""
from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass, field

import numpy as np
import open3d as o3d
import trimesh
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

from . import krawedz as KR
from . import match as M

STATUSY = ("ok", "ubytek", "sprawdz", "sprawdz_ulozenie", "poprawka", "skan_ponownie", "popraw_ulozenie", "nie_sprawdzono", "pominieto")
PAS_OD = ("linia_i_plaszczyzna", "linia", "plaszczyzna")  # [inspect] pas_brzegu_od: suma obu pasów (domyślnie), od linii brzegu każdego filaru (P2) albo, jak przed P2, od płaszczyzny z = 0
OTOCZENIE_STACJI_MM = 0.3  # stacja linii brzegu „ma dane”, gdy punkty próbki pasa w tym promieniu od niej mają powierzchnię skanu …
UDZIAL_DANYCH_STACJI = 0.5  # … co najmniej w takiej części
ODCINEK_MIN_MM = 0.2  # krótsze odcinki linii bez sprawdzenia nie są wypisywane w wyniku (liczą się do udziału)
ODCINKOW_MAX = 12  # najwyżej tyle najdłuższych odcinków bez sprawdzenia na filar w wyniku JSON
KAT_KRAWEDZI_DEG = 40.0  # ostra krawędź projektu (jak synth.strona_brzegu)
ODLEGLOSC_KRAWEDZI_MM = 0.5  # plama w tej odległości od ostrej krawędzi projektu liczy się jak w pasie brzegu
EPS_PLAMY_MM = 0.25  # łączenie punktów pod powierzchnią w plamę
KOMORKA_DRGNIECIA_MM = 1.0
GESTOSC_PROBKI_BRZEGU = 0.03  # mm: odstęp próbki powierzchni projektu w pasie brzegu (metoda B)
MIN_PUNKTOW_DRGNIECIA = 20  # komórka 1 mm liczy się do drgnięcia, gdy ma tyle punktów
UDZIAL_DRUGIEJ_STRONY = 0.2  # drgnięcie: rozmyte odchyłki całej pracy po obu stronach powierzchni (każdy znak ≥ tyle)
NAJWIEKSZA_PLAMA_DRGNIECIA = 0.6  # drgnięcie: największe zwarte skupisko rozmytych komórek ≤ tyle wszystkich (poprawka = jedna plama)


@dataclass
class Ubytek:
    x: float  # środek, układ płytki
    y: float
    z: float
    srednica_mm: float
    glebokosc_mm: float
    metoda: str  # A | B | A+B
    kolor: str  # czerwony | zolty
    punkty: int = 0
    odleglosc_od_brzegu_mm: float = 0.0  # odległość środka od linii brzegu najbliższego filaru (pas od płaszczyzny: od z = 0 projektu)
    wciecie_mm: float = 0.0  # metoda B: głębokość wcięcia linii brzegu
    na_krawedzi: bool = False
    filar: int = 0  # numer filaru (pętli linii brzegu), przy którym leży ubytek; 0 = nieznany (pas od płaszczyzny, brak linii)


@dataclass
class Plama:
    """Plama punktów pod powierzchnią (metoda A) z klasyfikacją."""
    x: float
    y: float
    z: float
    srednica_mm: float
    glebokosc_mm: float
    punkty: int
    ostra_krawedz: bool
    pierscien_punkty: int
    pierscien_mediana_mm: float
    odleglosc_od_brzegu_mm: float
    na_krawedzi: bool
    rodzaj: str  # ubytek | poprawka | sprawdz_ulozenie | brak_danych | lagodna | poza_pasem | za_mala
    filar: int = 0  # numer filaru najbliższej linii brzegu (0 = nieznany)


@dataclass
class Wciecie:
    """Wcięcie linii brzegu (metoda B)."""
    x: float
    y: float
    z: float
    szerokosc_mm: float
    wciecie_mm: float
    punkty: int
    otoczenie_z_danymi: float  # udział punktów linii w otoczeniu odcinka, gdzie skan jest ciągły
    rodzaj: str  # wciecie | brak_danych | za_male
    odleglosc_od_brzegu_mm: float = 0.0  # odległość środka od linii brzegu (pas od płaszczyzny: od z = 0 projektu)
    filar: int = 0  # numer filaru najbliższej linii brzegu (0 = nieznany)


@dataclass
class WynikInspekcji:
    gniazdo: int | None
    projekt: str
    status: str  # STATUSY
    pokrycie: float
    ubytki: list[Ubytek] = field(default_factory=list)
    plamy: list[Plama] = field(default_factory=list)
    wciecia: list[Wciecie] = field(default_factory=list)
    drgniecie: dict = field(default_factory=dict)
    linia_brzegu: dict = field(default_factory=dict)
    odchylki: dict = field(default_factory=dict)
    uwagi: list[str] = field(default_factory=list)
    czas_s: float = 0.0
    # P2: co z brzegu każdego filaru zostało sprawdzone (``ocena_brzegu``); {} = nie liczono (pas od płaszczyzny, drgnięcie, złe ułożenie)
    brzeg: dict = field(default_factory=dict)
    czas_linii_s: float = 0.0  # część ``czas_s`` zużyta na jednorazowe wyznaczenie linii brzegu projektu (0, gdy były w pamięci)
    # do podglądu (nie do JSON): punkty w układzie płytki i odchyłka każdego
    _P: np.ndarray | None = field(default=None, repr=False, compare=False)
    _d: np.ndarray | None = field(default=None, repr=False, compare=False)

    def json(self) -> dict:
        d = asdict(self)
        d.pop("_P", None)
        d.pop("_d", None)
        return d


# ----------------------------------------------------------------------------
# odchyłki
# ----------------------------------------------------------------------------
def transformacja_do_projektu(pr: M.Projekt, transformacja: np.ndarray) -> np.ndarray:
    """4×4 płytka → układ puli projektu (``transformacja``: (projekt × w) → płytka, z ``match``)."""
    return pr.T0 @ np.linalg.inv(np.asarray(transformacja, dtype=np.float64))


def odchylki(P_pula: np.ndarray, pr: M.Projekt) -> np.ndarray:
    """Odległość ze znakiem punktów (układ puli) od siatki projektu: < 0 = pod powierzchnią (w materiale)."""
    r = pr.scena.compute_closest_points(o3d.core.Tensor(np.ascontiguousarray(P_pula, dtype=np.float32)))
    C = r["points"].numpy().astype(np.float64)
    N = r["primitive_normals"].numpy().astype(np.float64)
    return np.einsum("ij,ij->i", P_pula - C, N)


def krawedzie_projektu(pr: M.Projekt) -> np.ndarray:
    """Środki ostrych krawędzi projektu (kąt między normalnymi > KAT_KRAWEDZI_DEG), układ puli; cache na projekcie."""
    if getattr(pr, "_krawedzie", None) is None:
        m = pr.siatka
        e = m.face_adjacency_edges[m.face_adjacency_angles > math.radians(KAT_KRAWEDZI_DEG)]
        pr._krawedzie = (m.vertices[e[:, 0]] + m.vertices[e[:, 1]]) / 2 if len(e) else np.zeros((0, 3))
    return pr._krawedzie


# ----------------------------------------------------------------------------
# linie brzegu projektu (P2)
# ----------------------------------------------------------------------------
@dataclass
class BrzegProjektu:
    """Linie krawędzi brzegu projektu w układzie puli: stacje linii O i I wszystkich filarów (pas brzegu = odległość od
    nich), stacje samej linii O (rachunek „co sprawdzono”) i próbka powierzchni projektu w pasie (metoda B)."""

    linie: KR.LinieProjektu
    X: np.ndarray  # (N, 3) stacje linii O i I
    filar: np.ndarray  # (N,) indeks filaru stacji na liście linie.filary
    drzewo: cKDTree | None  # None = projekt bez linii
    XO: np.ndarray  # (K, 3) stacje linii O
    filar_O: np.ndarray
    zweryf_O: np.ndarray  # stacja leży na zweryfikowanym przekroju linii projektu
    drzewo_O: cKDTree | None
    probki: dict = field(default_factory=dict)  # pas → (punkty, normalne, najbliższa stacja O, odległość do niej, odległość od linii)


_BRZEGI: dict[tuple, BrzegProjektu] = {}  # (klucz projektu, współczynnik) → linie w układzie puli; linie liczy raz moduł krawedz
_BRZEGI_MAX = 256


def brzeg_projektu(pr: M.Projekt) -> BrzegProjektu:
    """Linie brzegu projektu z puli (``krawedz.linie_siatki`` na siatce puli), pamiętane na projekt i współczynnik."""
    klucz = (KR.klucz_projektu(pr.id, pr.T0), round(float(pr.wspolczynnik), 9))
    b = _BRZEGI.get(klucz)
    if b is None:
        linie = KR.linie_siatki(pr.siatka, skala=pr.wspolczynnik, klucz=klucz[0])
        st, so = KR.stacje(linie, ("O", "I")), KR.stacje(linie, ("O",))
        b = BrzegProjektu(linie, st["X"], st["filar"], cKDTree(st["X"]) if len(st["X"]) else None,
                          so["X"], so["filar"], so["zweryf"], cKDTree(so["X"]) if len(so["X"]) else None)
        if len(_BRZEGI) >= _BRZEGI_MAX:
            _BRZEGI.pop(next(iter(_BRZEGI)))
        _BRZEGI[klucz] = b
    return b


# ----------------------------------------------------------------------------
# drgnięcie
# ----------------------------------------------------------------------------
def wykryj_drgniecie(P: np.ndarray, d: np.ndarray, ust_i: dict) -> dict:
    """Podwójna powierzchnia: odchyłki > ``drgniecie_odchylka_mm`` rozsiane po dużej części pracy.

    Komórki 1 mm z ≥ MIN_PUNKTOW_DRGNIECIA punktów; komórka „rozmyta”, gdy ≥ ``drgniecie_udzial_w_komorce``
    jej punktów ma |d| > próg. Drgnięcie, gdy rozmytych jest ≥ ``drgniecie_udzial_obszaru`` komórek I rozmyte
    odchyłki całej pracy leżą po obu stronach powierzchni (≥ UDZIAL_DRUGIEJ_STRONY każdego znaku: druga warstwa
    jest raz nad, raz pod projektem; ubytek i poprawka ręczna są tylko pod) ALBO rozmyte komórki są rozproszone
    (największe zwarte skupisko ≤ NAJWIEKSZA_PLAMA_DRGNIECIA wszystkich; poprawka to jedna plama, kopia po drgnięciu
    rozmywa komórki po całej pracy, nawet gdy ICP trzyma się warstwy głównej i odchyłki są jednostronne).
    Ubytek rozmywa 1–3 komórki, drgnięcie — połowę pracy.
    """
    if len(P) == 0:
        return {"wykryte": False, "udzial_obszaru": 0.0, "komorek": 0}
    ij = np.floor(P / KOMORKA_DRGNIECIA_MM).astype(np.int64)
    _, inv = np.unique(ij, axis=0, return_inverse=True)
    inv = inv.ravel()
    n = np.bincount(inv)
    nad = np.bincount(inv, weights=(d > ust_i["drgniecie_odchylka_mm"]).astype(float))
    pod = np.bincount(inv, weights=(d < -ust_i["drgniecie_odchylka_mm"]).astype(float))
    ok = n >= MIN_PUNKTOW_DRGNIECIA
    if not ok.any():
        return {"wykryte": False, "udzial_obszaru": 0.0, "komorek": 0}
    zle = nad + pod
    rozmyta = zle[ok] / n[ok] >= ust_i["drgniecie_udzial_w_komorce"]
    udzial = float(np.mean(rozmyta))
    # obie strony powierzchni liczone na całej pracy (ICP trzyma się warstwy głównej, więc w jednej komórce kopia
    # leży po jednej stronie, ale po całej pracy — po obu); ubytek i poprawka ręczna są wyłącznie pod
    n_nad, n_pod = float(nad[ok][rozmyta].sum()), float(pod[ok][rozmyta].sum())
    obie_strony = min(n_nad, n_pod) >= UDZIAL_DRUGIEJ_STRONY * (n_nad + n_pod) if (n_nad + n_pod) > 0 else False
    # rozproszenie: poprawka ręczna to JEDNA zwarta plama rozmytych komórek; drgnięcie rozmywa komórki po całej pracy
    # (gdy ICP trzyma się warstwy głównej, odchyłki kopii mogą być jednostronne — wtedy decyduje rozproszenie)
    kom = np.unique(ij, axis=0)[ok][rozmyta]
    najwieksza = 1.0
    if len(kom) > 1:
        kom = kom - kom.min(0)
        siatka = np.zeros(tuple(kom.max(0) + 1), dtype=bool)
        siatka[tuple(kom.T)] = True
        etyk, n_sk = ndimage.label(siatka, structure=np.ones((3, 3, 3)))
        najwieksza = float(np.bincount(etyk.ravel())[1:].max() / len(kom))
    rozproszone = najwieksza <= NAJWIEKSZA_PLAMA_DRGNIECIA
    return {"wykryte": bool(udzial >= ust_i["drgniecie_udzial_obszaru"] and (obie_strony or rozproszone)), "udzial_obszaru": round(udzial, 4),
            "komorek": int(ok.sum()), "udzial_nad": round(n_nad / max(1.0, n_nad + n_pod), 3), "najwieksza_plama": round(najwieksza, 3)}


# ----------------------------------------------------------------------------
# metoda A: plamy pod powierzchnią
# ----------------------------------------------------------------------------
def _skupiska(Q: np.ndarray, eps: float) -> np.ndarray:
    """Etykiety spójnych skupisk punktów (sąsiedztwo ≤ eps)."""
    if len(Q) == 0:
        return np.zeros(0, dtype=int)
    pary = cKDTree(Q).query_pairs(eps, output_type="ndarray")
    if len(pary) == 0:
        return np.arange(len(Q))
    A = coo_matrix((np.ones(len(pary)), (pary[:, 0], pary[:, 1])), shape=(len(Q), len(Q)))
    return connected_components(A, directed=False)[1]


def _rozmiar(Q: np.ndarray) -> float:
    """Największy rozmiar skupiska [mm]: rozpiętość 2…98 percentyla wzdłuż pierwszej osi głównej
    (pojedyncze punkty szumu doczepione do plamy nie wydłużają jej)."""
    if len(Q) < 2:
        return 0.0
    c = Q - Q.mean(0)
    _, _, vt = np.linalg.svd(c, full_matrices=False)
    r = c @ vt[0]
    lo, hi = np.percentile(r, [2, 98])
    return float(hi - lo)


def plamy_pod_powierzchnia(P_pula: np.ndarray, d: np.ndarray, pr: M.Projekt, ust_i: dict, brzeg: BrzegProjektu | None = None,
                           z_plaszczyzna: bool = False) -> list[Plama]:
    """Skupiska punktów ≥ prog pod powierzchnią z klasyfikacją (ubytek / poprawka / sprawdź ułożenie / brak danych / łagodna / poza pasem).

    ``brzeg`` (linie brzegu projektu): pas brzegu = odległość środka plamy od linii brzegu najbliższego filaru;
    None = sposób sprzed P2 (odległość od płaszczyzny z = 0 projektu). ``z_plaszczyzna`` (tryb ``linia_i_plaszczyzna``):
    odległość = mniejsza z obu, czyli pas = suma pasa od linii i pasa od płaszczyzny."""
    prog = ust_i["prog_glebokosci_mm"]
    rdzen = np.flatnonzero(d <= -prog)
    if len(rdzen) == 0:
        return []
    drzewo = cKDTree(P_pula)
    etyk = _skupiska(P_pula[rdzen], EPS_PLAMY_MM)
    krawedzie = krawedzie_projektu(pr)
    drzewo_kr = cKDTree(krawedzie) if len(krawedzie) else None
    plamy: list[Plama] = []
    for e in np.unique(etyk):
        idx = rdzen[etyk == e]
        if len(idx) < ust_i["min_punktow_plamy"]:
            continue
        Q = P_pula[idx]
        # pierścień krawedz_pas_mm wokół rdzenia (punkty spoza rdzenia): tu odchyłka ma wrócić do ~0
        sasiedzi = np.unique(np.concatenate([np.asarray(s, dtype=int) for s in drzewo.query_ball_point(Q, ust_i["krawedz_pas_mm"])]))
        w_rdzeniu = np.zeros(len(P_pula), dtype=bool)
        w_rdzeniu[idx] = True
        pierscien = sasiedzi[~w_rdzeniu[sasiedzi]]
        c = Q.mean(0)
        srednica = _rozmiar(Q)  # rozpiętość rdzenia (≥ prog pod powierzchnią): mniejsza niż średnica ubytku
        glebokosc = float(-d[idx].min())
        n_pier = int(len(pierscien))
        med_pier = float(np.median(np.abs(d[pierscien]))) if n_pier else math.inf
        ostra = n_pier >= ust_i["min_punktow_plamy"] and med_pier <= prog / 2
        filar = 0
        odl_plaszcz = float(max(0.0, -c[2]))
        if brzeg is None:
            odl_brzegu = odl_plaszcz
        elif brzeg.drzewo is None:
            # projekt bez linii brzegu: w trybie sumy pas sprzed P2, w trybie samej linii pasa nie ma (zostaje reguła ostrej krawędzi)
            odl_brzegu = odl_plaszcz if z_plaszczyzna else math.inf
        else:
            odl_brzegu, j = brzeg.drzewo.query(c)
            odl_brzegu, filar = float(odl_brzegu), int(brzeg.linie.filary[brzeg.filar[j]].nr)
            if z_plaszczyzna:
                odl_brzegu = min(odl_brzegu, odl_plaszcz)
        na_kraw = bool(drzewo_kr is not None and drzewo_kr.query(c)[0] <= ODLEGLOSC_KRAWEDZI_MM)
        if n_pier < ust_i["min_punktow_plamy"]:
            rodzaj = "brak_danych"
        elif srednica > ust_i["poprawka_min_mm"] and not ostra:
            rodzaj = "poprawka"
        elif srednica > ust_i["srednica_max_mm"]:
            rodzaj = "sprawdz_ulozenie"
        elif not ostra:
            rodzaj = "lagodna"
        elif srednica < ust_i["srednica_min_mm"] / 2:
            rodzaj = "za_mala"
        elif odl_brzegu > ust_i["pas_brzegu_mm"] and not na_kraw:
            rodzaj = "poza_pasem"
        else:
            rodzaj = "ubytek"
        plamy.append(Plama(*map(float, c), round(srednica, 3), round(glebokosc, 4), int(len(idx)), bool(ostra), n_pier,
                           round(med_pier, 4) if math.isfinite(med_pier) else -1.0, round(min(odl_brzegu, 999.0), 3), na_kraw, rodzaj, filar))
    return plamy


# ----------------------------------------------------------------------------
# metoda B: linia brzegu
# ----------------------------------------------------------------------------
def probka_brzegu(pr: M.Projekt, pas: float) -> tuple[np.ndarray, np.ndarray]:
    """Gęsta próbka powierzchni projektu (punkty + normalne, układ puli) w pasie brzegu z = 0 … −pas; cache na projekcie."""
    cache = getattr(pr, "_probka_brzegu", None)
    if cache is None or cache[0] != pas:
        m = pr.siatka
        zmax = m.vertices[m.faces, 2].max(axis=1)
        sel = np.flatnonzero(zmax > -(pas + 0.3))
        if len(sel) == 0:
            pr._probka_brzegu = (pas, np.zeros((0, 3)), np.zeros((0, 3)))
        else:
            sub = trimesh.Trimesh(m.vertices, m.faces[sel], process=False)
            ile = int(min(300000, max(2000, sub.area / GESTOSC_PROBKI_BRZEGU**2)))
            pts, fid = trimesh.sample.sample_surface(sub, ile, seed=0)
            pts, nrm = np.asarray(pts), np.asarray(sub.face_normals[fid])
            w = pts[:, 2] >= -pas
            pr._probka_brzegu = (pas, pts[w], nrm[w])
    return pr._probka_brzegu[1], pr._probka_brzegu[2]


def probka_od_linii(pr: M.Projekt, pas: float, brzeg: BrzegProjektu) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Gęsta próbka powierzchni projektu w pasie ``pas`` od linii brzegu wszystkich filarów (P2): punkty, normalne,
    numer najbliższej stacji linii O i odległość do niej, odległość od linii (O / I). Pamiętana w ``brzeg``."""
    cache = brzeg.probki.get(pas)
    if cache is None:
        puste = (np.zeros((0, 3)), np.zeros((0, 3)), np.zeros(0, dtype=np.int64), np.zeros(0), np.zeros(0))
        cache = puste
        if brzeg.drzewo is not None and brzeg.drzewo_O is not None:
            m = pr.siatka
            blisko = np.isfinite(brzeg.drzewo.query(m.vertices, distance_upper_bound=pas + 0.3)[0])
            sel = np.flatnonzero(blisko[m.faces].any(axis=1))
            if len(sel):
                sub = trimesh.Trimesh(m.vertices, m.faces[sel], process=False)
                ile = int(min(300000, max(2000, sub.area / GESTOSC_PROBKI_BRZEGU**2)))
                pts, fid = trimesh.sample.sample_surface(sub, ile, seed=0)
                pts, nrm = np.asarray(pts), np.asarray(sub.face_normals[fid])
                odl = brzeg.drzewo.query(pts)[0]
                w = odl <= pas
                odl_O, st_O = brzeg.drzewo_O.query(pts[w])
                cache = (pts[w], nrm[w], st_O.astype(np.int64), odl_O, odl[w])
        brzeg.probki[pas] = cache
    return cache


def probka_suma(pr: M.Projekt, pas: float, brzeg: BrzegProjektu) -> tuple[np.ndarray, np.ndarray, int]:
    """Próbka pasa w trybie ``linia_i_plaszczyzna``: najpierw cała próbka od linii (``probka_od_linii``, w tej kolejności),
    potem punkty pasa sprzed P2 (z = 0 … −pas) dalsze od każdej linii niż ``pas`` (bez podwójnych punktów: ta sama gęstość
    co w jednym pasie). Zwraca (punkty, normalne, liczba punktów części od linii). Pamiętana w ``brzeg``."""
    klucz = ("suma", pas)
    cache = brzeg.probki.get(klucz)
    if cache is None:
        L1, N1 = probka_od_linii(pr, pas, brzeg)[:2]
        L2, N2 = probka_brzegu(pr, pas)
        if brzeg.drzewo is not None and len(L2):
            zostaw = brzeg.drzewo.query(L2)[0] > pas
            L2, N2 = L2[zostaw], N2[zostaw]
        cache = (np.vstack([L1, L2]) if len(L2) else L1, np.vstack([N1, N2]) if len(L2) else N1, int(len(L1)))
        brzeg.probki[klucz] = cache
    return cache


BRAK_DANYCH_MM = 0.8  # metoda B: punkt linii bez wierzchołka skanu o zgodnej normalnej w tym promieniu = brak danych (0,5 odcinało rzadkie siatki: 16 % prac dobrze ułożonych miało linię < 90 %)
SASIADOW_LINII = 8  # metoda B: tylu najbliższych wierzchołków skanu przeglądanych w poszukiwaniu zgodnej normalnej
ZGODNOSC_NORMALNEJ = 0.2  # cos kąta normalna skanu · normalna linii brzegu
UDZIAL_POD = 0.7  # metoda B: wektor do wierzchołka skanu ma leżeć głównie wzdłuż normalnej (pod linią), nie bocznie


def linia_brzegu(P_pula: np.ndarray, N_pula: np.ndarray, pr: M.Projekt, ust_i: dict, brzeg: BrzegProjektu | None = None,
                 z_plaszczyzna: bool = False) -> tuple[list[Wciecie], dict]:
    """Metoda B (``_linia_brzegu``): wcięcia linii brzegu i liczniki; ``brzeg`` = pas od linii brzegu każdego filaru."""
    return _linia_brzegu(P_pula, N_pula, pr, ust_i, brzeg, z_plaszczyzna)[:2]


def _linia_brzegu(P_pula: np.ndarray, N_pula: np.ndarray, pr: M.Projekt, ust_i: dict, brzeg: BrzegProjektu | None = None,
                  z_plaszczyzna: bool = False):
    """Ciągłość linii brzegu: dla każdego punktu pasa brzegu projektu — czy skan ma tam powierzchnię.

    Pas brzegu: z ``brzeg`` — powierzchnia projektu ≤ ``pas_brzegu_mm`` od linii brzegu każdego filaru (P2), bez —
    z = 0 … −pas (sposób sprzed P2); ``z_plaszczyzna`` — suma obu (``probka_suma``: najpierw część od linii).
    Zwraca (wcięcia, liczniki, maska „punkt próbki ma powierzchnię skanu” albo None).

    Najbliższy wierzchołek skanu o zgodnej normalnej dalej niż BRAK_DANYCH_MM = brak odcinka linii (brak danych).
    Inaczej cofnięcie skanu = składowa wektora do tego wierzchołka wzdłuż normalnej linii do wnętrza materiału:
    ≥ ``wciecie_min_mm`` i wierzchołek leży głównie pod punktem linii (nie bocznie, jak na skraju dziury) = wcięcie
    (ukruszenie); inaczej linia ciągła (nie alarm).
    Wcięcia grupowane w odcinki; odcinek liczy się, gdy jego otoczenie na linii ma dane (≥ 50 %).
    Gdy linia jest ciągła w mniej niż ``linia_min_udzial`` swojej długości (praca bokiem / do góry nogami /
    zasłonięta), wcięcia stają się „brak danych”: ciągłości nie da się ocenić (plan 1a: podnosić próg
    pokrycia, nie próg ubytku).
    """
    pas, wmin = ust_i["pas_brzegu_mm"], ust_i["wciecie_min_mm"]
    if brzeg is None:
        L, NL = probka_brzegu(pr, pas)
    elif z_plaszczyzna:
        L, NL = probka_suma(pr, pas, brzeg)[:2]
    else:
        L, NL = probka_od_linii(pr, pas, brzeg)[:2]
    if len(L) == 0 or len(P_pula) == 0:
        return [], {"punktow_linii": 0, "brak_danych": 0, "udzial_brak_danych": 0.0, "wciec": 0, "uwaga": "projekt bez pasa brzegu"}, None
    # najbliższy wierzchołek skanu o normalnej zgodnej z linią (cienka ścianka: wierzchołek z drugiej strony
    # ścianki jest bliżej, ale to inna powierzchnia); brak takiego w promieniu BRAK_DANYCH_MM = brak danych
    kk = min(SASIADOW_LINII, len(P_pula))
    odl_k, naj_k = cKDTree(P_pula).query(L, k=kk, distance_upper_bound=BRAK_DANYCH_MM)
    if kk == 1:
        odl_k, naj_k = odl_k[:, None], naj_k[:, None]
    naj_k = np.where(np.isfinite(odl_k), naj_k, 0)
    zgodne = np.einsum("ijk,ik->ij", N_pula[naj_k], NL) > ZGODNOSC_NORMALNEJ
    zgodne &= np.isfinite(odl_k)
    ma = zgodne.any(axis=1)
    j = np.argmax(zgodne, axis=1)
    naj = naj_k[np.arange(len(L)), j]
    odl_w = np.where(ma, odl_k[np.arange(len(L)), j], np.inf)
    R = P_pula[naj] - L
    dl = np.linalg.norm(R, axis=1)
    pod = -np.einsum("ij,ij->i", R, NL)  # > 0: wierzchołek skanu pod powierzchnią projektu (w materiale), wzdłuż normalnej linii
    brak = ~ma
    # wcięcie: skan cofnięty o ≥ wmin wzdłuż normalnej i wierzchołek leży głównie POD punktem linii (nie obok —
    # na skraju dziury w skanie najbliższy wierzchołek jest przesunięty bocznie, a na wypukłej powierzchni
    # wypada pozornie „pod” płaszczyzną styczną)
    wciecie = ma & (pod >= wmin) & (pod >= UDZIAL_POD * dl)
    odl = pod
    daleko = brak | wciecie
    wciecia: list[Wciecie] = []
    idx_w = np.flatnonzero(wciecie)
    if len(idx_w):
        etyk = _skupiska(L[idx_w], EPS_PLAMY_MM)
        drzewo_L = cKDTree(L)
        for e in np.unique(etyk):
            idx = idx_w[etyk == e]
            Q = L[idx]
            szer = _rozmiar(Q)
            sas = np.unique(np.concatenate([np.asarray(s, dtype=int) for s in drzewo_L.query_ball_point(Q, ust_i["krawedz_pas_mm"])]))
            sas = sas[~np.isin(sas, idx)]
            udz = float(np.mean(~daleko[sas])) if len(sas) else 0.0
            if szer < ust_i["srednica_min_mm"] or len(idx) < ust_i["min_punktow_plamy"]:
                rodzaj = "za_male"
            elif udz < 0.5:
                rodzaj = "brak_danych"
            else:
                rodzaj = "wciecie"
            c = Q.mean(0)
            odl_brzegu, filar = float(max(0.0, -c[2])), 0  # bez linii (pas od płaszczyzny albo projekt bez linii w trybie sumy): od z = 0, filar nieznany
            if brzeg is not None and brzeg.drzewo is not None:
                odl_brzegu, j = brzeg.drzewo.query(c)
                filar = int(brzeg.linie.filary[brzeg.filar[j]].nr)
            wciecia.append(Wciecie(float(c[0]), float(c[1]), float(c[2]), round(szer, 3), round(float(odl[idx].max()), 4), int(len(idx)), round(udz, 3), rodzaj,
                                   float(odl_brzegu), filar))
    udzial_ciagly = float((~daleko).mean())
    uwaga = None
    if udzial_ciagly < ust_i["linia_min_udzial"]:  # większość linii brzegu bez danych (praca bokiem, do góry nogami, zasłonięta): ciągłości nie da się ocenić
        for w in wciecia:
            if w.rodzaj == "wciecie":
                w.rodzaj = "brak_danych"
        uwaga = f"linia brzegu widoczna w {udzial_ciagly:.0%} (< {ust_i['linia_min_udzial']:.0%}): metoda B pominięta"
    info = {"punktow_linii": int(len(L)), "brak_danych": int(brak.sum()), "udzial_brak_danych": round(float(brak.mean()), 4),
            "udzial_ciagly": round(udzial_ciagly, 4), "wciec": sum(1 for w in wciecia if w.rodzaj == "wciecie")}
    if uwaga:
        info["uwaga"] = uwaga
    return wciecia, info, ma


def _kryterium_brzegu(ok: np.ndarray, krok: float, ust_i: dict) -> tuple[bool, float, float]:
    """(czy filar sprawdzony, udział stacji sprawdzonych, najdłuższy odcinek bez sprawdzenia [mm]) dla maski stacji linii O."""
    udzial = float(ok.mean()) if len(ok) else 0.0
    przerwa = KR.najdluzsza_przerwa(ok) * krok if len(ok) else 0.0
    return bool(udzial >= ust_i["brzeg_min_sprawdzony"] and przerwa <= ust_i["brzeg_max_przerwa_mm"]), udzial, float(przerwa)


def _odcinki_bez_sprawdzenia(spr: np.ndarray, zw: np.ndarray, X: np.ndarray, krok: float, T_pula_do_plytki: np.ndarray | None) -> list[dict]:
    """Kołowe ciągi stacji bez sprawdzenia (≥ ODCINEK_MIN_MM), najdłuższe pierwsze: położenie wzdłuż linii O, długość,
    powód (``linia`` = linia projektu niezweryfikowana, ``dane`` = brak danych skanu przy linii), środek odcinka (układ płytki)."""
    n = len(spr)
    if n == 0 or spr.all():
        return []
    start = int(np.argmax(spr)) if spr.any() else 0  # obrót, żeby ciąg nie był rozcięty końcem tablicy
    kolej = (np.arange(n) + start) % n
    zle = ~spr[kolej]
    granice = np.flatnonzero(np.diff(np.concatenate([[False], zle, [False]]).astype(int)))
    odcinki = []
    for a, b in zip(granice[::2], granice[1::2]):
        idx = kolej[a:b]
        dl = len(idx) * krok
        if dl < ODCINEK_MIN_MM:
            continue
        sr = X[idx[len(idx) // 2]]
        if T_pula_do_plytki is not None:
            sr = T_pula_do_plytki[:3, :3] @ sr + T_pula_do_plytki[:3, 3]
        odcinki.append({"od_mm": round(float(idx[0] * krok), 2), "do_mm": round(float((idx[-1] + 1) * krok), 2), "dlugosc_mm": round(float(dl), 2),
                        "powod": "linia" if (~zw[idx]).mean() >= 0.5 else "dane", "srodek": [round(float(v), 3) for v in sr]})
    odcinki.sort(key=lambda o: -o["dlugosc_mm"])
    return odcinki[:ODCINKOW_MAX]


def ocena_brzegu(brzeg: BrzegProjektu, st_O: np.ndarray | None, odl_O: np.ndarray | None, ma_dane: np.ndarray | None, ust_i: dict,
                 T_pula_do_plytki: np.ndarray | None = None, tylko_dane: bool = False) -> dict:
    """Która część linii brzegu każdego filaru została sprawdzona (P2).

    Stacja linii O jest sprawdzona, gdy leży na zweryfikowanym przekroju linii projektu ORAZ co najmniej
    UDZIAL_DANYCH_STACJI punktów próbki pasa w promieniu OTOCZENIE_STACJI_MM od niej ma powierzchnię skanu
    (``ma_dane`` z metody B). Filar jest sprawdzony, gdy udział sprawdzonych stacji ≥ ``brzeg_min_sprawdzony`` i
    najdłuższy odcinek bez sprawdzenia ≤ ``brzeg_max_przerwa_mm``. Projekt bez linii = nic nie sprawdzono.
    Wynik (do JSON): ``sprawdzony``, ``nie_sprawdzono`` (numery filarów), ``opis`` i na filar: długość linii, udziały
    (linia pewna / z danymi / sprawdzona), najdłuższa przerwa, powody (``linia`` / ``dane``), odcinki bez sprawdzenia.

    ``tylko_dane`` (tryb ``linia_i_plaszczyzna``): stacja jest sprawdzona, gdy ma dane skanu — niepewna linia projektu nie
    blokuje (tam działa też pas od płaszczyzny) i trafia do ``uwagi_linii``; projekt bez linii = sprawdzony pasem sprzed P2.
    """
    linie = brzeg.linie
    if not linie.filary:
        uw = "linii brzegu projektu nie wyznaczono" + (f" ({'; '.join(linie.uwagi)})" if linie.uwagi else "")
        if tylko_dane:
            return {"sprawdzony": True, "stan_linii": "brak", "filarow": 0, "nie_sprawdzono": [], "filary": [], "opis": "",
                    "uwagi_linii": uw + " — pas brzegu od płaszczyzny (jak przed P2)"}
        return {"sprawdzony": False, "stan_linii": "brak", "filarow": 0, "nie_sprawdzono": [], "filary": [], "opis": uw}
    n = len(brzeg.XO)
    dane = np.zeros(n, dtype=bool)
    if st_O is not None and ma_dane is not None and len(st_O):
        blisko = odl_O <= OTOCZENIE_STACJI_MM
        wszystkie = np.bincount(st_O[blisko], minlength=n)
        z_danymi = np.bincount(st_O[blisko], weights=ma_dane[blisko].astype(float), minlength=n)
        dane = (wszystkie > 0) & (z_danymi >= UDZIAL_DANYCH_STACJI * wszystkie)
    filary, zle, opisy, uwagi_linii = [], [], [], []
    for i, f in enumerate(linie.filary):
        w = brzeg.filar_O == i
        zw, dn = brzeg.zweryf_O[w], dane[w]
        krok = f.linie["O"].krok
        spr = dn if tylko_dane else zw & dn
        ok, udzial, przerwa = _kryterium_brzegu(spr, krok, ust_i)
        ok_linia, udzial_linii, przerwa_linii = _kryterium_brzegu(zw, krok, ust_i)
        ok_dane, udzial_danych, _ = _kryterium_brzegu(dn, krok, ust_i)
        if tylko_dane:
            powody = [] if ok else ["dane"]
            if not ok_linia:
                uwagi_linii.append(f"filar {f.nr}: linia projektu niepewna (pewne {udzial_linii:.0%} długości, najdłuższy odcinek "
                                   f"niepewny {przerwa_linii:.1f} mm) — tam pas brzegu także od płaszczyzny")
        else:
            powody = [] if ok else ([p for p, dobrze in (("linia", ok_linia), ("dane", ok_dane)) if not dobrze] or ["linia", "dane"])
        filary.append({"nr": f.nr, "sprawdzony": ok, "dlugosc_mm": round(f.dlugosc, 2), "werdykt_linii": f.werdykt,
                       "udzial_linii_pewnej": round(udzial_linii, 4), "udzial_z_danymi": round(udzial_danych, 4), "udzial_sprawdzony": round(udzial, 4),
                       "najdl_przerwa_mm": round(przerwa, 2), "najdl_przerwa_linii_mm": round(przerwa_linii, 2), "powody": powody,
                       "odcinki": _odcinki_bez_sprawdzenia(spr, zw, brzeg.XO[w], krok, T_pula_do_plytki)})
        if not ok:
            zle.append(f.nr)
            co = {"linia": f"linia projektu niepewna (pewne {udzial_linii:.0%} długości, najdłuższy odcinek niepewny {przerwa_linii:.1f} mm)",
                  "dane": f"brak danych skanu przy linii (dane na {udzial_danych:.0%} długości)"}
            opisy.append(f"filar {f.nr}: sprawdzono {udzial:.0%} linii brzegu, najdłuższy odcinek bez sprawdzenia {przerwa:.1f} mm — "
                         + "; ".join(co[p] for p in powody))
    wynik = {"sprawdzony": not zle, "stan_linii": linie.stan, "filarow": len(filary), "nie_sprawdzono": zle, "filary": filary, "opis": "; ".join(opisy)}
    if tylko_dane:
        wynik["uwagi_linii"] = "; ".join(uwagi_linii)
    return wynik


# ----------------------------------------------------------------------------
# decyzja
# ----------------------------------------------------------------------------
def _do_plytki(T_pula_do_plytki: np.ndarray, p) -> tuple[float, float, float]:
    q = T_pula_do_plytki[:3, :3] @ np.asarray(p, dtype=float) + T_pula_do_plytki[:3, 3]
    return float(q[0]), float(q[1]), float(q[2])


def polacz(plamy: list[Plama], wciecia: list[Wciecie], T_pula_do_plytki: np.ndarray, ust_i: dict) -> list[Ubytek]:
    """Decyzja: A+B w tym samym miejscu → czerwone; samo B ≥ wciecie_pewne → czerwone; jedna metoda → żółte."""
    A = [p for p in plamy if p.rodzaj == "ubytek"]
    B = [w for w in wciecia if w.rodzaj == "wciecie"]
    uzyte = set()
    out: list[Ubytek] = []
    for p in A:
        para = None
        for j, w in enumerate(B):
            if j in uzyte:
                continue
            if math.dist((p.x, p.y, p.z), (w.x, w.y, w.z)) <= max(p.srednica_mm, w.szerokosc_mm) / 2 + 0.3:
                para = j
                break
        x, y, z = _do_plytki(T_pula_do_plytki, (p.x, p.y, p.z))
        if para is not None:
            uzyte.add(para)
            w = B[para]
            out.append(Ubytek(x, y, z, p.srednica_mm, p.glebokosc_mm, "A+B", "czerwony", p.punkty, p.odleglosc_od_brzegu_mm, w.wciecie_mm, p.na_krawedzi, p.filar))
        else:
            out.append(Ubytek(x, y, z, p.srednica_mm, p.glebokosc_mm, "A", "zolty", p.punkty, p.odleglosc_od_brzegu_mm, 0.0, p.na_krawedzi, p.filar))
    for j, w in enumerate(B):
        if j in uzyte:
            continue
        x, y, z = _do_plytki(T_pula_do_plytki, (w.x, w.y, w.z))
        kolor = "czerwony" if w.wciecie_mm >= ust_i["wciecie_pewne_mm"] else "zolty"
        out.append(Ubytek(x, y, z, w.szerokosc_mm, w.wciecie_mm, "B", kolor, w.punkty, w.odleglosc_od_brzegu_mm, w.wciecie_mm, False, w.filar))
    return out


def sprawdz(P: np.ndarray, N: np.ndarray, pr: M.Projekt, transformacja: np.ndarray, pokrycie: float, ust: dict, gniazdo: int | None = None) -> WynikInspekcji:
    """Pełna inspekcja fragmentu (punkty + normalne w układzie płytki) wobec projektu ``pr`` z transformacją z ``match``."""
    t0 = time.time()
    ui, um = ust["inspect"], ust["match"]
    T = transformacja_do_projektu(pr, transformacja)
    T_inv = np.linalg.inv(T)
    P_pula = P @ T[:3, :3].T + T[:3, 3]
    # po korekcie skali w match transformacja jest podobieństwem (obrót + przesunięcie + skala ≤ ±1 %): normalne bez skali
    N_pula = np.asarray(N, dtype=np.float64) @ (T[:3, :3] / M.skala_macierzy(T)).T
    d = odchylki(P_pula, pr)
    w = WynikInspekcji(gniazdo, pr.id, "ok", float(pokrycie), _P=P, _d=d)
    w.odchylki = {"punkty": int(len(P)), "udzial_pod": round(float(np.mean(d <= -ui["prog_glebokosci_mm"])), 4),
                  "udzial_nad": round(float(np.mean(d >= ui["prog_glebokosci_mm"])), 4), "rms_mm": round(float(np.sqrt(np.mean(d**2))), 4) if len(d) else 0.0,
                  "mediana_mm": round(float(np.median(d)), 4) if len(d) else 0.0}
    w.drgniecie = wykryj_drgniecie(P_pula, d, ui)
    if w.drgniecie["wykryte"]:
        w.status = "skan_ponownie"
        w.uwagi.append(f"podwójna powierzchnia: odchyłki rozmyte na {w.drgniecie['udzial_obszaru']:.0%} pracy — skan ponownie")
        w.czas_s = round(time.time() - t0, 3)
        return w
    brzeg = None
    suma = ui["pas_brzegu_od"] == "linia_i_plaszczyzna"
    if ui["pas_brzegu_od"] in ("linia", "linia_i_plaszczyzna"):  # P2: pas brzegu od linii brzegu każdego filaru (linie liczone raz na projekt)
        t_linii = time.time()
        brzeg = brzeg_projektu(pr)
        w.czas_linii_s = round(time.time() - t_linii, 3)  # > 0 tylko przy pierwszej inspekcji projektu w procesie
    if pokrycie < um["prog_akceptacji_pokrycie"]:
        # gładka poprawka ręczna obniża pokrycie tak samo jak złe ułożenie: jeśli po odjęciu jej punktów pokrycie
        # wraca nad próg, to poprawka (pomarańczowe), nie „popraw ułożenie”
        plamy = plamy_pod_powierzchnia(P_pula, d, pr, ui, brzeg, suma)
        w_poprawkach = sum(p.punkty for p in plamy if p.rodzaj == "poprawka")
        if not (w_poprawkach and len(P) and pokrycie + w_poprawkach / len(P) >= um["prog_akceptacji_pokrycie"]):
            w.status = "popraw_ulozenie"
            w.uwagi.append(f"pokrycie {pokrycie:.2f} < {um['prog_akceptacji_pokrycie']}: popraw ułożenie / skan ponownie, ubytki nieliczone")
            w.czas_s = round(time.time() - t0, 3)
            return w
        w.uwagi.append(f"pokrycie {pokrycie:.2f} obniżone przez gładką poprawkę ręczną ({w_poprawkach} punktów)")
        w.plamy = plamy
    else:
        w.plamy = plamy_pod_powierzchnia(P_pula, d, pr, ui, brzeg, suma)
    w.wciecia, w.linia_brzegu, ma_dane = _linia_brzegu(P_pula, N_pula, pr, ui, brzeg, suma)
    if brzeg is not None:
        _, _, st_O, odl_O, _ = probka_od_linii(pr, ui["pas_brzegu_mm"], brzeg)
        if ma_dane is not None and suma:
            ma_dane = ma_dane[:len(st_O)]  # probka_suma: najpierw część od linii, w tej samej kolejności
        w.brzeg = ocena_brzegu(brzeg, st_O, odl_O, ma_dane, ui, T_inv, tylko_dane=suma)
    w.ubytki = polacz(w.plamy, w.wciecia, T_inv, ui)
    for p in w.plamy:  # środki plam do układu płytki (do podglądu)
        p.x, p.y, p.z = _do_plytki(T_inv, (p.x, p.y, p.z))
    for v in w.wciecia:
        v.x, v.y, v.z = _do_plytki(T_inv, (v.x, v.y, v.z))
    if any(u.kolor == "czerwony" for u in w.ubytki):
        w.status = "ubytek"
    elif w.ubytki:
        w.status = "sprawdz"
    elif any(p.rodzaj == "poprawka" for p in w.plamy):
        w.status = "poprawka"
    elif any(p.rodzaj == "sprawdz_ulozenie" for p in w.plamy):
        w.status = "sprawdz_ulozenie"
    elif brzeg is not None and not w.brzeg["sprawdzony"]:
        w.status = "nie_sprawdzono"  # P2: brzegu któregoś filaru nie dało się sprawdzić — nigdy zielone, nigdy czerwone
    if brzeg is not None and not w.brzeg["sprawdzony"]:
        w.uwagi.append("brzeg nie sprawdzony: " + w.brzeg["opis"])
    if brzeg is not None and w.brzeg.get("uwagi_linii"):
        w.uwagi.append(w.brzeg["uwagi_linii"])
    n_bd = sum(1 for p in w.plamy if p.rodzaj == "brak_danych") + sum(1 for v in w.wciecia if v.rodzaj == "brak_danych")
    if n_bd:
        w.uwagi.append(f"{n_bd} miejsc bez danych skanu (nie liczone jako ubytek)")
    if w.linia_brzegu.get("uwaga"):
        w.uwagi.append(w.linia_brzegu["uwaga"])
    elif w.linia_brzegu.get("udzial_brak_danych", 0) > 0.2:
        w.uwagi.append(f"linia brzegu bez danych w {w.linia_brzegu['udzial_brak_danych']:.0%}")
    w.czas_s = round(time.time() - t0, 3)
    return w


# ----------------------------------------------------------------------------
# metryki na prawdzie
# ----------------------------------------------------------------------------
def dopasuj_do_prawdy(ubytki_prawdy: list, wykryte: list[dict], tolerancja: float = 0.3) -> dict:
    """Które ubytki z prawdy (synth.Ubytek: x, y, z, srednica, wykrywalny) mają wykrycie w promieniu srednica/2 + tolerancja;
    wykrycie bez żadnego ubytku prawdy (także niewykrywalnego / częściowo widocznego) w promieniu srednica/2 + 1 mm = fałszywe."""
    traf = {"A": [], "B": [], "A+B": [], "czerwony": [], "dowolny": []}
    for u in ubytki_prawdy:
        c = (u.x, u.y, u.z)
        bl = [w for w in wykryte if math.dist(c, (w["x"], w["y"], w["z"])) <= u.srednica / 2 + tolerancja]
        traf["A"].append(any(w["metoda"] in ("A", "A+B") for w in bl))
        traf["B"].append(any(w["metoda"] in ("B", "A+B") for w in bl))
        traf["A+B"].append(any(w["metoda"] == "A+B" for w in bl))
        traf["czerwony"].append(any(w["kolor"] == "czerwony" for w in bl))
        traf["dowolny"].append(bool(bl))
    falszywe = [w for w in wykryte if not any(math.dist((u.x, u.y, u.z), (w["x"], w["y"], w["z"])) <= u.srednica / 2 + 1.0 for u in ubytki_prawdy)]
    return {"trafione": traf, "falszywe": len(falszywe), "falszywe_czerwone": sum(1 for w in falszywe if w["kolor"] == "czerwony"),
            "falszywe_metoda": {m: sum(1 for w in falszywe if w["metoda"] == m) for m in ("A", "B", "A+B")}}


def klasa_polozenia(polozenie: str) -> str:
    """Klasa do metryk: ``krawedz`` (krawedz_srodek / krawedz_zewn / krawedz_wewn), ``sciana`` albo ``nieznane``."""
    if polozenie.startswith("krawedz"):
        return "krawedz"
    return "sciana" if polozenie == "sciana" else "nieznane"


def polozenie_ubytku_prawdy(u, pr: M.Projekt, transformacja: np.ndarray) -> tuple[str, float | None]:
    """Położenie ubytku z prawdy względem linii brzegu projektu — dla prawdy sprzed P4, która nie ma pola ``polozenie``.

    ``transformacja``: (projekt × w) → płytka z prawdy. Zwraca (``krawedz`` | ``sciana`` | ``nieznane``, odległość środka
    od linii O / I [mm]): krawędź, gdy kula ubytku (promień ``srednica`` / 2) sięga linii O / S / I któregoś filaru;
    projekt bez linii = ``nieznane``."""
    b = brzeg_projektu(pr)
    if b.drzewo is None:
        return "nieznane", None
    T = transformacja_do_projektu(pr, transformacja)
    p = T[:3, :3] @ np.array([u.x, u.y, u.z], dtype=np.float64) + T[:3, 3]
    odl = float(b.drzewo.query(p)[0])
    odl_s = min((float(np.linalg.norm(f.S - p, axis=1).min()) for f in b.linie.filary), default=math.inf)
    return ("krawedz" if min(odl, odl_s) <= u.srednica / 2 else "sciana"), round(odl, 4)
