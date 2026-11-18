"""Generator sztucznych skanów płytki (dane syntetyczne do strojenia bez skanera).

Z prawdziwych (albo atrapowych) projektów STL buduje „skan” całej płytki:
projekt powiększony o współczynnik skurczu, obrócony brzegiem do góry,
losowo ułożony w gnieździe, z wyciętymi ubytkami brzegu o znanym położeniu
i rozmiarze, z szumem pomiarowym, na siatce płytki z gniazdami. Obok STL
zapisuje JSON z prawdą (co, gdzie, jaki ubytek), na którym moduły plate,
match i inspect liczą swoje metryki. Projekt jest w prawdzie zapisany jako
skrót SHA-256 pliku (bez nazwy); mapowanie skrót → nazwa trafia do osobnego
pliku ``mapa_projektow.json`` w katalogu nad wyjściem (domyślnie ``dane/``).

Progi i zakresy (szum, skurcz, średnice ubytków, pas brzegu, próg głębokości)
czyta z ``ustawienia.toml`` (sekcje ``[synth]`` i ``[inspect]``).

Użycie (z katalogu stanowisko/):
    py -3.12 -m stanowisko.synth --projekty dane/stl --plytka wieczorna --ile 3 --wyjscie dane/syntetyczne
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import time
import warnings
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

import numpy as np
import open3d as o3d
import trimesh
from scipy.spatial import ConvexHull, cKDTree

from . import krawedz as KR
from . import uklad as U
from . import ustawienia as UST

TAN_SCIANKI = math.tan(math.radians(U.KAT_SCIANKI_DEG))
MAKS_UNIESIENIE = 1.5  # mm: o tyle praca może wisieć nad dnem gniazda (klin na ściance), więcej = za małe gniazdo
TOLERANCJA_PRZENIKANIA = 1e-6  # mm: osadzenie z większym wejściem w ściankę to błąd programu
WSPOLCZYNNIK_PORANNA = (1.0, 1.0)  # rano prace są już spieczone: skala 1 z definicji, to nie próg do strojenia
GLEBOKOSC_UBYTKU = 0.7  # głębokość ubytku = 0,7·r (środek kuli 0,3·r nad powierzchnią)
WERSJE_UBYTKOW = (1, 2)  # 1 = generator sprzed P4 (czasza pod płaszczyzną styczną — tylko do odtwarzania starych zestawów), 2 = czasza w materiale
POLOZENIA_UKRUSZEN = ("srodek", "zewn", "wewn", "sciana")  # K6: środek płaskiej krawędzi brzegu, narożnik zewnętrzny / wewnętrzny, ściana w pasie brzegu
KLASY_POLOZENIA = {"srodek": "krawedz_srodek", "zewn": "krawedz_zewn", "wewn": "krawedz_wewn", "sciana": "sciana"}  # → Ubytek.polozenie
ODSTEP_UKRUSZEN_MM = 2.0  # K6: środki ubytków tej samej pracy leżą co najmniej o tyle od siebie (plus ich promienie)
SCIANA_OD_KRAWEDZI_MM = 0.15  # K6 „sciana”: kula nie dochodzi do płaskiej krawędzi brzegu bliżej niż na tyle
PUNKTOW_POMIARU_KULI = 4000  # gęsta siatka punktów kuli do pomiaru rzeczywistej głębokości ubytku
PROB_UKRUSZENIA = 60  # K6: tyle losowań miejsca, zanim ukruszenie zostanie pominięte
ORIENTACJE = ("auto", "brzeg_dol", "brzeg_gora")
ULOZENIA = ("dobrze", "bokiem", "do_gory_nogami")
NORMALNA_NIEWIDOCZNA = -0.15  # praca bokiem: trójkąty z normalną z poniżej tego nie są widziane z góry
WZOR_EXOCAD = re.compile(r"_cad\.stl$", re.IGNORECASE)
PROG_MOSTU_MM = 20.0  # praca szersza niż to idzie do rynienki


# ----------------------------------------------------------------------------
# prawda (ground truth)
# ----------------------------------------------------------------------------
@dataclass
class Ubytek:
    x: float
    y: float
    z: float  # środek ubytku na powierzchni, układ skanu (STL płytki)
    srednica: float
    glebokosc: float
    wykrywalny: bool = True  # False: płytszy niż [inspect] prog_glebokosci_mm, średnica poza zakresem [inspect] albo niewidoczny
    widoczny: bool = True  # False: powierzchnia ubytku usunięta ze skanu (--pokrycie, praca bokiem)
    # pola od P4 (15.11.2026); w prawdzie starszych zestawów ich nie ma — zostają wartości domyślne („nieznane”)
    polozenie: str = ""  # klasa położenia: krawedz_srodek | krawedz_zewn | krawedz_wewn | sciana; "" = nieznana
    glebokosc_rzeczywista: float | None = None  # zmierzona: największa odległość nowej powierzchni pod pierwotną powierzchnią pracy [mm]
    filar: int = 0  # numer filaru (pętli brzegu) najbliższej linii; 0 = nieznany / brak linii
    odleglosc_od_linii: float | None = None  # odległość środka (x, y, z) od linii krawędzi brzegu O / I [mm]
    celowy: bool = False  # True: ukruszenie K6 postawione celowo (środek kuli NA powierzchni, rozmiar = promień = srednica / 2)


@dataclass
class Poprawka:
    """Gładka poprawka ręczna: zagłębienie o profilu (1 − (ρ/R)²)², średnica 2R > [inspect] poprawka_min_mm."""
    x: float
    y: float
    z: float
    srednica: float
    glebokosc: float


@dataclass
class PracaNaPlytce:
    gniazdo: int
    projekt: str  # skrót SHA-256 pliku STL projektu (16 znaków hex); nazwa pliku tylko w mapa_projektow.json
    wspolczynnik: float  # skala projekt → praca zielona (1.0 rano)
    transformacja: list  # 4×4: (projekt × wspolczynnik) → układ skanu
    ubytki: list[Ubytek] = field(default_factory=list)
    drgniecie: bool = False  # podwójna powierzchnia (praca przesunęła się w skanie)
    poza_gniazdem: bool = False
    ulozenie: str = "dobrze"  # dobrze | bokiem | do_gory_nogami (P3a: --bokiem)
    pokrycie: float = 1.0  # udział powierzchni pracy, który został w skanie (P3a: --pokrycie, praca bokiem)
    poprawki: list[Poprawka] = field(default_factory=list)  # gładkie poprawki ręczne (P3a: --poprawka)
    ukruszenia_pominiete: int = 0  # K6: ile zamówionych ukruszeń celowych nie dało się postawić (brak zweryfikowanej linii / miejsca)


@dataclass
class PrawdaPlytki:
    plytka: str
    numer: int
    seed: int
    szum_sigma: float
    z_top: float
    prace: list[PracaNaPlytce]
    gniazda_puste: list[int]
    plik_stl: str = ""
    poza_skanu: list | None = None  # 4×4: układ płytki → układ skanu (None = skan w układzie płytki)
    pole_d: float | None = None  # średnica pola skanowania [mm], gdy skan przycięto (None = cała płytka)
    pole_srodek: list | None = None  # (x, y) środka pola w układzie płytki
    pominiete: list[str] = field(default_factory=list)  # skróty projektów, które nie zmieściły się w żadnym wolnym gnieździe


def skrot_pliku(p: Path) -> str:
    """Identyfikator projektu w prawdzie: pierwsze 16 znaków SHA-256 zawartości pliku."""
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


def pliki_projektow(folder: Path) -> list[Path]:
    """Pliki STL projektów: w folderze i podfolderach (zlecenia), z pominięciem folderów ``_*`` (np. ``_pobrane``)."""
    folder = Path(folder)
    return sorted(
        p for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() == ".stl" and not any(cz.startswith("_") for cz in p.relative_to(folder).parts[:-1])
    )


def wczytaj_projekt(plik: Path) -> trimesh.Trimesh | None:
    """Wczytuje STL projektu; zły plik (pusty, NaN, zerowa powierzchnia) → None z ostrzeżeniem."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)  # trimesh/numpy przy pustych plikach
            m = trimesh.load(plik, force="mesh", process=False)  # process=True cicho usuwa NaN — najpierw sprawdzamy
    except Exception as e:  # noqa: BLE001 — każdy błąd odczytu = pomijamy plik
        powod = f"nie da się wczytać ({type(e).__name__})"
    else:
        if not isinstance(m, trimesh.Trimesh) or len(m.faces) == 0:
            powod = "brak trójkątów"
        elif not np.isfinite(m.vertices).all():
            powod = "NaN/nieskończoność we wierzchołkach"
        elif not m.area > 0:
            powod = "zerowa powierzchnia"
        else:
            m.process()  # scalenie wierzchołków jak przy zwykłym trimesh.load
            return m
    warnings.warn(f"pomijam projekt {plik.name}: {powod}", stacklevel=2)
    return None


# ----------------------------------------------------------------------------
# operacje na pojedynczej pracy
# ----------------------------------------------------------------------------
def strona_brzegu(m: trimesh.Trimesh, kat_deg: float = 40.0, pas: float = 0.2) -> tuple[float, float]:
    """Długość krawędzi „brzegowych” w dolnym i górnym pasie ``pas``·wysokości [mm].

    Brzeg korony to ostra krawędź (kąt między normalnymi sąsiednich trójkątów > ``kat_deg``:
    ściana zewnętrzna ↔ stopień ↔ ściana wewnętrzna) albo — w siatce nieszczelnej — krawędź
    otwarta. Po stronie żującej takich krawędzi prawie nie ma (kanał śruby: ~6 mm obwodu).
    """
    e = m.face_adjacency_edges[m.face_adjacency_angles > math.radians(kat_deg)]
    otwarte = m.edges[trimesh.grouping.group_rows(m.edges_sorted, require_count=1)]
    e = np.vstack([e, otwarte]) if len(otwarte) else e
    if len(e) == 0:
        return 0.0, 0.0
    v = m.vertices
    dl = np.linalg.norm(v[e[:, 0]] - v[e[:, 1]], axis=1)
    zc = (v[e[:, 0], 2] + v[e[:, 1], 2]) / 2
    z0, z1 = m.bounds[:, 2]
    h = z1 - z0
    return float(dl[zc < z0 + pas * h].sum()), float(dl[zc > z1 - pas * h].sum())


def brzeg_z_heurystyki(m: trimesh.Trimesh) -> str:
    """``dol`` | ``gora`` | ``niejasny`` — po której stronie pliku jest brzeg wg ``strona_brzegu``."""
    dol, gora = strona_brzegu(m)
    if max(dol, gora) < 1.0 or max(dol, gora) < 1.5 * min(dol, gora):
        return "niejasny"
    return "dol" if dol > gora else "gora"


def plik_exocad(nazwa: str) -> bool:
    """Eksport z exocad (``…_cad.stl``): praca w układzie osi wprowadzenia, brzeg na dole."""
    return WZOR_EXOCAD.search(str(nazwa)) is not None


def orientacja_brzegiem_do_gory(m: trimesh.Trimesh, orientacja: str = "auto", nazwa: str = "") -> np.ndarray:
    """Zwraca macierz 4×4 obracającą pracę tak, by brzeg (otwór) był na górze.

    ``orientacja``: ``brzeg_dol`` — projekt ma brzeg na dole (obrót o 180° wokół x);
    ``brzeg_gora`` — bez obrotu; ``auto`` — plik exocad (``…_cad.stl``, poznany po ``nazwa``)
    ma brzeg na dole z konwencji eksportu (sprawdzone 2.11.2026 rzutem z góry i z dołu na 17/17
    projektach z pulpitu: korony górne i dolne, mosty, waxupy, prace bez łącznika), inne pliki —
    heurystyka ``strona_brzegu`` (ostre/otwarte krawędzie w dolnym vs górnym pasie 20 % wysokości;
    29/30 na pulpicie + atrapach, myli się na pochylonym moście z przęsłem niżej niż brzegi).
    Gdy heurystyka jest niejednoznaczna, zakłada brzeg na dole i ostrzega.
    """
    if orientacja not in ORIENTACJE:
        raise ValueError(f"orientacja {orientacja!r}: dopuszczalne {', '.join(ORIENTACJE)}")
    obrot = trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0])
    if orientacja == "brzeg_dol":
        return obrot
    if orientacja == "brzeg_gora":
        return np.eye(4)
    if plik_exocad(nazwa):
        return obrot
    brzeg = brzeg_z_heurystyki(m)
    if brzeg == "niejasny":
        dol, gora = strona_brzegu(m)
        warnings.warn(
            f"orientacja pracy niejednoznaczna (krawędzie brzegu: dół {dol:.1f} mm, góra {gora:.1f} mm); "
            "zakładam brzeg na dole — podaj --orientacja", stacklevel=2
        )
        return obrot
    return obrot if brzeg == "dol" else np.eye(4)


def _wytnij_ubytek_v1(
    m: trimesh.Trimesh, srednica: float, rng: np.random.Generator, pas_brzegu: float | None = None
) -> tuple[trimesh.Trimesh, Ubytek]:
    """Generator ubytków sprzed P4 (``wersja_ubytkow`` = 1) — ZOSTAWIONY BEZ ZMIAN wyłącznie po to, żeby dało się
    odtworzyć bajt w bajt zestawy wygenerowane przed 15.11.2026 (zestawy odniesienia R59 / r54, mapa seed 7001).

    Błąd tej wersji (testy krawędzi T5, 06.11.2026): wstawiana jest połowa kuli pod płaszczyzną styczną w wierzchołku,
    a nie część kuli leżąca w materiale — na krawędzi i na cienkiej ściance część czaszy wisi w powietrzu, a część
    materiału w kuli zostaje bez powierzchni. Nowe zestawy generuje ``wytnij_ubytek`` (wersja 2).

    ``pas_brzegu`` None = ``[inspect] pas_brzegu_mm`` z ustawień. Praca musi być już obrócona brzegiem do góry.
    Siatka jest lokalnie zagęszczona do 0,05 mm, trójkąty w kuli usunięte, a w ich miejsce wstawiona „czasza” kuli.
    """
    if not (math.isfinite(srednica) and srednica > 0):
        raise ValueError(f"średnica ubytku musi być > 0 mm, jest {srednica}")
    if pas_brzegu is None:
        pas_brzegu = UST.domyslne()["inspect"]["pas_brzegu_mm"]
    r = srednica / 2
    z_max = m.bounds[1, 2]
    kand = np.flatnonzero(m.vertices[:, 2] > z_max - pas_brzegu)
    if len(kand) == 0:
        kand = np.arange(len(m.vertices))
    iv = int(rng.choice(kand))
    p = m.vertices[iv].copy()
    n = m.vertex_normals[iv].copy()
    if not np.isfinite(n).all() or np.linalg.norm(n) < 0.5:
        n = np.array([0, 0, 1.0])
    n /= np.linalg.norm(n)
    c = p + (1 - GLEBOKOSC_UBYTKU) * r * n  # środek kuli lekko na zewnątrz: głębokość ubytku 0,7 r

    # lokalne zagęszczenie wokół ubytku
    V, F = m.vertices.copy(), m.faces.copy()
    odl = np.linalg.norm(m.triangles_center - c, axis=1)
    blisko = odl < 1.6 * r + 0.3
    if blisko.any():
        Vs, Fs = trimesh.remesh.subdivide_to_size(V, F[blisko], max_edge=min(0.05, r / 3))
        F = np.concatenate([F[~blisko], Fs + len(V)])
        V = np.concatenate([V, Vs])
    # usuń trójkąty, których dowolny wierzchołek jest w kuli
    w_kuli = np.linalg.norm(V - c, axis=1) < r
    F = F[~w_kuli[F].any(axis=1)]
    # czasza kuli pod powierzchnią
    kula = trimesh.creation.icosphere(subdivisions=4, radius=r)
    kula.apply_translation(c)
    pod = ((kula.triangles_center - p) @ n) < 0
    kula.update_faces(pod)
    kula.invert()  # normalne do wnętrza kuli = na zewnątrz materiału
    V = np.concatenate([V, kula.vertices])
    F = np.concatenate([F, kula.faces + (len(V) - len(kula.vertices))])
    out = trimesh.Trimesh(V, F, process=False)
    out.merge_vertices()
    out.update_faces(out.nondegenerate_faces())
    out.remove_unreferenced_vertices()
    return out, Ubytek(*map(float, p), srednica=float(srednica), glebokosc=float(GLEBOKOSC_UBYTKU * r))


class Material:
    """Materiał pracy do wycinania ubytków: pierwotna powierzchnia (przed ubytkami) i lista już wyciętych kul.

    ``funkcja(Q)`` < 0 = punkt leży w materiale, który jeszcze jest (pod pierwotną powierzchnią i poza wyciętymi
    kulami). Znak odległości od powierzchni: siatka szczelna — ``compute_signed_distance`` Open3D (parzystość
    przecięć promienia); nieszczelna — normalna najbliższego trójkąta (jak ``inspect.odchylki``; przy bardzo ostrych
    krawędziach znak bywa błędny — ograniczenie opisane w ``opisy_modulow/synth.md``).
    """

    def __init__(self, m: trimesh.Trimesh):
        self.scena = KR.scena_siatki(m)
        self.szczelna = bool(m.is_watertight)
        self.kule: list[tuple[np.ndarray, float]] = []

    def najblizszy(self, Q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """(najbliższy punkt pierwotnej powierzchni, odległość) dla każdego punktu ``Q``."""
        r = self.scena.compute_closest_points(o3d.core.Tensor(np.ascontiguousarray(np.atleast_2d(Q), dtype=np.float32)))
        C = r["points"].numpy().astype(np.float64)
        return C, np.linalg.norm(np.atleast_2d(Q) - C, axis=1)

    def od_powierzchni(self, Q: np.ndarray) -> np.ndarray:
        """Odległość ze znakiem od pierwotnej powierzchni pracy: < 0 = w materiale."""
        t = o3d.core.Tensor(np.ascontiguousarray(Q, dtype=np.float32))
        if self.szczelna:
            return self.scena.compute_signed_distance(t).numpy().astype(np.float64)
        r = self.scena.compute_closest_points(t)
        R = Q - r["points"].numpy().astype(np.float64)
        znak = np.sign(np.einsum("ij,ij->i", R, r["primitive_normals"].numpy().astype(np.float64)))
        return znak * np.linalg.norm(R, axis=1)

    def funkcja(self, Q: np.ndarray) -> np.ndarray:
        g = self.od_powierzchni(Q)
        for c, r in self.kule:
            g = np.maximum(g, r - np.linalg.norm(Q - c, axis=1))
        return g


def _punkty_kuli(n: int) -> np.ndarray:
    """``n`` prawie równomiernych kierunków na sferze jednostkowej (spirala Fibonacciego)."""
    i = np.arange(n) + 0.5
    z = 1 - 2 * i / n
    fi = i * math.pi * (3 - math.sqrt(5))
    s = np.sqrt(1 - z * z)
    return np.c_[s * np.cos(fi), s * np.sin(fi), z]


def _przytnij(V: np.ndarray, F: np.ndarray, g, rzut=None, iteracje: int = 10) -> tuple[np.ndarray, np.ndarray]:
    """Część siatki, w której ``g(punkt)`` < 0. Trójkąty przecięte granicą g = 0 są dzielone: punkt przecięcia każdej
    krawędzi szukany bisekcją i brany po stronie g < 0 (zostająca część nigdy nie wychodzi poza granicę);
    ``rzut`` — opcjonalne dociągnięcie punktów bisekcji na powierzchnię, po której biegnie krawędź (np. na sferę).
    Zwraca (wierzchołki + nowe punkty, trójkąty)."""
    ins = np.asarray(g(V)) < 0
    k = ins[F].sum(axis=1)
    cale = F[k == 3]
    miesz = F[(k == 1) | (k == 2)]
    if len(miesz) == 0:
        return V, cale
    flag = ins[miesz]
    jeden = flag.sum(axis=1) == 1  # jeden wierzchołek po stronie g < 0 (inaczej: jeden po stronie g >= 0)
    odm = np.where(jeden[:, None], flag, ~flag).argmax(axis=1)  # kolumna wierzchołka „odmiennego”
    T = np.take_along_axis(miesz, (odm[:, None] + np.arange(3)) % 3, axis=1)  # (a, b, c): a odmienny, kolejność cykliczna zachowana
    a, b, c = T.T
    e_in = np.concatenate([np.where(jeden, a, b), np.where(jeden, a, c)])  # krawędzie a–b i a–c jako (g < 0, g >= 0)
    e_out = np.concatenate([np.where(jeden, b, a), np.where(jeden, c, a)])
    _, pierwszy, odw = np.unique(e_in.astype(np.int64) * len(V) + e_out, return_index=True, return_inverse=True)
    lo, hi = V[e_in[pierwszy]].astype(np.float64).copy(), V[e_out[pierwszy]].astype(np.float64).copy()
    for _ in range(iteracje):
        mid = (lo + hi) / 2 if rzut is None else rzut((lo + hi) / 2)
        w = np.asarray(g(mid)) < 0
        lo[w] = mid[w]
        hi[~w] = mid[~w]
    X = lo
    odw = odw.ravel()
    xab, xac = len(V) + odw[: len(T)], len(V) + odw[len(T):]
    nowe = [np.c_[a, xab, xac][jeden], np.c_[xab, b, c][~jeden], np.c_[xab, c, xac][~jeden]]
    return np.vstack([V, X]), np.vstack([cale, *nowe])


def _wytnij_kule(m: trimesh.Trimesh, material: Material, c: np.ndarray, r: float, odstep: float) -> tuple[trimesh.Trimesh, dict] | None:
    """Usuwa z pracy materiał w kuli (c, r): powierzchnia pracy przycięta dokładnie na sferze, w jej miejsce część
    sfery leżąca W materiale (przycięta na pierwotnej powierzchni i na wcześniej wyciętych kulach) — nic nie wisi w
    powietrzu i żaden materiał w kuli nie zostaje bez powierzchni. Punkty nowej powierzchni mają gęstość skanu:
    jeden na ``odstep``² mm². Dopisuje kulę do ``material.kule``. Zwraca (siatka, pomiar) albo None, gdy kula nie
    sięga materiału.

    pomiar: ``glebokosc`` = największa odległość nowej powierzchni pod PIERWOTNĄ powierzchnią pracy [mm],
    ``udzial_kuli_w_materiale`` (udział pola sfery, który stał się nową powierzchnią), ``punktow_czaszy``.
    """
    Pd = c + r * _punkty_kuli(PUNKTOW_POMIARU_KULI)
    w = material.funkcja(Pd) < 0
    if not w.any():
        return None
    glebokosc = float(max(0.0, -material.od_powierzchni(Pd[w]).min()))
    V, F = m.vertices.copy(), m.faces.copy()
    blisko = np.linalg.norm(m.triangles_center - c, axis=1) < 1.6 * r + 0.3
    if blisko.any():  # lokalne zagęszczenie wokół ubytku do gęstości skanu
        Vs, Fs = trimesh.remesh.subdivide_to_size(V, F[blisko], max_edge=odstep)
        F = np.concatenate([F[~blisko], Fs + len(V)])
        V = np.concatenate([V, Vs])
    V, F = _przytnij(V, F, lambda Q: r - np.linalg.norm(Q - c, axis=1))  # zostaje część powierzchni poza kulą
    Uk = _punkty_kuli(max(24, int(round(4 * math.pi * r * r / odstep**2))))
    Vk, Fk = _przytnij(c + r * Uk, ConvexHull(Uk).simplices, material.funkcja,
                       rzut=lambda X: c + r * (X - c) / np.maximum(np.linalg.norm(X - c, axis=1, keepdims=True), 1e-12))
    if len(Fk):  # normalne czaszy do środka kuli = na zewnątrz materiału
        tr = Vk[Fk]
        nrm = np.cross(tr[:, 1] - tr[:, 0], tr[:, 2] - tr[:, 0])
        zle = np.einsum("ij,ij->i", nrm, tr.mean(axis=1) - c) > 0
        Fk[zle] = Fk[zle][:, ::-1]
    out = trimesh.Trimesh(np.concatenate([V, Vk]), np.concatenate([F, Fk + len(V)]), process=False)
    out.merge_vertices()
    out.update_faces(out.nondegenerate_faces())
    out.remove_unreferenced_vertices()
    material.kule.append((np.asarray(c, dtype=np.float64).copy(), float(r)))
    return out, {"glebokosc": glebokosc, "udzial_kuli_w_materiale": float(w.mean()), "punktow_czaszy": int(len(np.unique(Fk)))}


def _stacje_pewne(linie: KR.LinieProjektu | None) -> np.ndarray:
    """Zweryfikowane stacje linii O i I wszystkich filarów (N×3); bez linii — pusta tablica."""
    if linie is None or not linie.filary:
        return np.zeros((0, 3))
    st = KR.stacje(linie)
    return st["X"][st["zweryf"]]


def polozenie_wzgledem_brzegu(linie: KR.LinieProjektu | None, p: np.ndarray, r: float) -> tuple[str, int, float | None]:
    """Klasa położenia ubytku o promieniu ``r`` i środku ``p`` na powierzchni: (klasa, numer filaru, odległość od linii
    O / I). Kula sięgająca płaskiej krawędzi brzegu (odległość od najbliższej z linii O / S / I ≤ r) = krawędź, klasa
    wg najbliższej linii (O → ``krawedz_zewn``, S → ``krawedz_srodek``, I → ``krawedz_wewn``); inaczej ``sciana``.
    Bez linii: ("", 0, None)."""
    if linie is None or not linie.filary:
        return "", 0, None
    naj = (math.inf, "", 0)
    odl_linii = math.inf
    for f in linie.filary:
        for nazwa, klasa in (("O", "krawedz_zewn"), ("S", "krawedz_srodek"), ("I", "krawedz_wewn")):
            d = float(cKDTree(f.linie[nazwa].X).query(p)[0])
            if d < naj[0]:
                naj = (d, klasa, f.nr)
            if nazwa != "S":
                odl_linii = min(odl_linii, d)
    return (naj[1] if naj[0] <= r else "sciana"), naj[2], round(odl_linii, 4)


def wytnij_ubytek(
    m: trimesh.Trimesh, srednica: float, rng: np.random.Generator, pas_brzegu: float | None = None, *,
    linie: KR.LinieProjektu | None = None, material: Material | None = None, odstep: float | None = None, wersja: int = 2,
) -> tuple[trimesh.Trimesh, Ubytek]:
    """Wycina kulisty ubytek w losowym miejscu pasa brzegu pracy (praca już obrócona brzegiem do góry).

    Miejsce = losowy wierzchołek siatki w pasie ``pas_brzegu`` (None = ``[inspect] pas_brzegu_mm``): z liniami
    krawędzi brzegu (``linie`` z ``krawedz.linie_siatki``) pas liczy się od zweryfikowanych odcinków linii każdego
    filaru — tak jak szuka inspect; bez linii to górny pas ``pas_brzegu`` mm pracy. Środek kuli leży 0,3·r nad
    powierzchnią (głębokość nominalna 0,7·r). Materiał w kuli jest usuwany, a w jego miejsce wchodzi część sfery
    leżąca w materiale (``_wytnij_kule``); w prawdzie: klasa położenia względem brzegu i zmierzona głębokość.
    ``material`` — wspólny dla kolejnych ubytków tej samej pracy (None = nowy z ``m``); ``odstep`` — gęstość punktów
    nowej powierzchni (None = ``[synth] odstep_ubytku_mm``); ``wersja`` = 1 → generator sprzed P4 (``_wytnij_ubytek_v1``).
    """
    if not (math.isfinite(srednica) and srednica > 0):
        raise ValueError(f"średnica ubytku musi być > 0 mm, jest {srednica}")
    if wersja not in WERSJE_UBYTKOW:
        raise ValueError(f"wersja generatora ubytków {wersja!r}: dopuszczalne {WERSJE_UBYTKOW}")
    if wersja == 1:
        return _wytnij_ubytek_v1(m, srednica, rng, pas_brzegu)
    if pas_brzegu is None:
        pas_brzegu = UST.domyslne()["inspect"]["pas_brzegu_mm"]
    if odstep is None:
        odstep = UST.domyslne()["synth"]["odstep_ubytku_mm"]
    if material is None:
        material = Material(m)
    r = srednica / 2
    pewne = _stacje_pewne(linie)
    if len(pewne):
        kand = np.flatnonzero(np.isfinite(cKDTree(pewne).query(m.vertices, distance_upper_bound=pas_brzegu)[0]))
    else:
        kand = np.flatnonzero(m.vertices[:, 2] > m.bounds[1, 2] - pas_brzegu)
    if len(kand) == 0:
        kand = np.arange(len(m.vertices))
    for _ in range(PROB_UKRUSZENIA):
        iv = int(rng.choice(kand))
        p = m.vertices[iv].copy()
        n = m.vertex_normals[iv].copy()
        if not np.isfinite(n).all() or np.linalg.norm(n) < 0.5:
            n = np.array([0, 0, 1.0])
        n /= np.linalg.norm(n)
        wynik = _wytnij_kule(m, material, p + (1 - GLEBOKOSC_UBYTKU) * r * n, r, odstep)  # środek kuli lekko na zewnątrz
        if wynik is not None:
            break
    else:
        raise RuntimeError("nie znaleziono miejsca na ubytek (kula nie sięga materiału)")
    klasa, filar, odl = polozenie_wzgledem_brzegu(linie, p, r)
    return wynik[0], Ubytek(*map(float, p), srednica=float(srednica), glebokosc=float(GLEBOKOSC_UBYTKU * r), polozenie=klasa,
                            glebokosc_rzeczywista=round(wynik[1]["glebokosc"], 4), filar=filar, odleglosc_od_linii=odl)


def wytnij_ukruszenie(
    m: trimesh.Trimesh, linie: KR.LinieProjektu | None, polozenie: str, rozmiar: float, rng: np.random.Generator, *,
    material: Material | None = None, pas_brzegu: float | None = None, odstep: float | None = None,
) -> tuple[trimesh.Trimesh, Ubytek | None]:
    """K6: ukruszenie postawione celowo na krawędzi brzegu (albo, dla porównania, na ścianie w pasie brzegu).

    ``rozmiar`` = promień kuli, której środek leży DOKŁADNIE NA powierzchni projektu (nie pod nią — błąd testów fali 1:
    środek pod powierzchnią dawał ukruszenie głębsze niż nominalne). ``polozenie``:
    ``srodek`` — środek płaskiej krawędzi (wgryz o głębokości = rozmiar i szerokości 2 × rozmiar),
    ``zewn`` / ``wewn`` — narożnik zewnętrzny / wewnętrzny płaskiej krawędzi (odprysk o boku ≈ rozmiar; największa
    głębokość pod powierzchnią ≈ rozmiar · sin(kąt narożnika / 2)), ``sciana`` — wierzchołek siatki w pasie brzegu
    dalej niż rozmiar + SCIANA_OD_KRAWEDZI_MM od linii O / S / I. Miejsca krawędziowe tylko na ZWERYFIKOWANYCH
    przekrojach linii (losowy filar, potem losowy przekrój), co najmniej ODSTEP_UKRUSZEN_MM od innych ubytków pracy.
    W prawdzie: ``srednica`` = 2 × rozmiar, ``glebokosc`` = rozmiar (nominalna), ``glebokosc_rzeczywista`` — zmierzona
    na wyciętej geometrii, ``polozenie``, ``filar``, ``celowy`` = True. Brak miejsca (brak linii, zajęte) → (m, None).
    """
    if polozenie not in POLOZENIA_UKRUSZEN:
        raise ValueError(f"położenie ukruszenia {polozenie!r}: dopuszczalne {', '.join(POLOZENIA_UKRUSZEN)}")
    if not (math.isfinite(rozmiar) and rozmiar > 0):
        raise ValueError(f"rozmiar ukruszenia musi być > 0 mm, jest {rozmiar}")
    if pas_brzegu is None:
        pas_brzegu = UST.domyslne()["inspect"]["pas_brzegu_mm"]
    if odstep is None:
        odstep = UST.domyslne()["synth"]["odstep_ubytku_mm"]
    if material is None:
        material = Material(m)
    filary = [f for f in (linie.filary if linie is not None else []) if f.zweryf.any()]
    if not filary:
        return m, None

    def wolne(p: np.ndarray) -> bool:
        return all(np.linalg.norm(p - c) >= ODSTEP_UKRUSZEN_MM + rozmiar + r for c, r in material.kule)

    kand_sciany = None
    for _ in range(PROB_UKRUSZENIA):
        f = filary[int(rng.integers(len(filary)))]
        if polozenie == "sciana":
            if kand_sciany is None:  # wierzchołki pierwotnej powierzchni w pasie, z dala od płaskiej krawędzi
                V = m.vertices
                pewne = _stacje_pewne(linie)
                wszystkie = KR.stacje(linie, KR.NAZWY_LINII)["X"]
                w_pasie = np.isfinite(cKDTree(pewne).query(V, distance_upper_bound=max(pas_brzegu - rozmiar, 0.0))[0])
                daleko = ~np.isfinite(cKDTree(wszystkie).query(V, distance_upper_bound=rozmiar + SCIANA_OD_KRAWEDZI_MM)[0])
                kand_sciany = np.flatnonzero(w_pasie & daleko)
                if len(kand_sciany):
                    kand_sciany = kand_sciany[material.najblizszy(V[kand_sciany])[1] < 1e-4]
            if len(kand_sciany) == 0:
                return m, None
            p0 = m.vertices[int(rng.choice(kand_sciany))]
        else:
            i = int(rng.choice(np.flatnonzero(f.zweryf)))
            p0 = {"srodek": f.S, "zewn": f.O, "wewn": f.I}[polozenie][i]
        q, odl = material.najblizszy(p0)
        if odl[0] > 0.02 or not wolne(q[0]):  # punkt linii poza powierzchnią albo za blisko innego ubytku
            continue
        wynik = _wytnij_kule(m, material, q[0], rozmiar, odstep)
        if wynik is None:
            continue
        p = q[0]
        _, filar, odl_linii = polozenie_wzgledem_brzegu(linie, p, rozmiar)
        return wynik[0], Ubytek(*map(float, p), srednica=float(2 * rozmiar), glebokosc=float(rozmiar), polozenie=KLASY_POLOZENIA[polozenie],
                                glebokosc_rzeczywista=round(wynik[1]["glebokosc"], 4), filar=(filar if polozenie == "sciana" else f.nr),
                                odleglosc_od_linii=odl_linii, celowy=True)
    return m, None


def dodaj_szum(m: trimesh.Trimesh, sigma: float, rng: np.random.Generator) -> trimesh.Trimesh:
    """Szum pomiarowy: przesunięcie wierzchołków wzdłuż normalnych, N(0, sigma)."""
    if not (math.isfinite(sigma) and sigma >= 0):
        raise ValueError(f"sigma szumu musi być >= 0 mm, jest {sigma}")
    if sigma == 0:
        return m
    n = m.vertex_normals
    n = np.where(np.isfinite(n), n, 0.0)
    V = m.vertices + n * rng.normal(0, sigma, (len(m.vertices), 1))
    return trimesh.Trimesh(V, m.faces.copy(), process=False)


def poprawka_reczna(m: trimesh.Trimesh, rng: np.random.Generator, promien: tuple[float, float] = (1.5, 3.0), glebokosc: tuple[float, float] = (0.15, 0.4)) -> tuple[trimesh.Trimesh, Poprawka]:
    """Gładkie zagłębienie (poprawka ręczna, np. doszlifowany kontakt): wierzchołki w promieniu R od losowego
    punktu przesunięte do wnętrza wzdłuż normalnych o g·(1 − (ρ/R)²)² — bez ostrej krawędzi, szersze niż ubytek."""
    R = float(rng.uniform(*promien))
    g = float(rng.uniform(*glebokosc))
    iv = int(rng.integers(len(m.vertices)))
    p = m.vertices[iv].copy()
    V, F = m.vertices.copy(), m.faces.copy()
    odl = np.linalg.norm(m.triangles_center - p, axis=1)
    blisko = odl < R + 0.3
    if blisko.any():  # zagęszczenie, żeby profil był gładki także na rzadkiej siatce
        Vs, Fs = trimesh.remesh.subdivide_to_size(V, F[blisko], max_edge=0.15)
        F = np.concatenate([F[~blisko], Fs + len(V)])
        V = np.concatenate([V, Vs])
    out = trimesh.Trimesh(V, F, process=False)
    out.merge_vertices()
    rho = np.linalg.norm(out.vertices - p, axis=1)
    w = np.clip(1 - (rho / R) ** 2, 0, None) ** 2
    n = out.vertex_normals
    n = np.where(np.isfinite(n), n, 0.0)
    V2 = out.vertices - n * (g * w)[:, None]
    return trimesh.Trimesh(V2, out.faces.copy(), process=False), Poprawka(*map(float, p), srednica=2 * R, glebokosc=g)


def obrot_bokiem(rng: np.random.Generator) -> tuple[np.ndarray, str]:
    """Macierz 4×4 kładąca pracę bokiem (obrót 90° ± 20° wokół losowej osi poziomej) albo do góry nogami (180°)."""
    if rng.uniform() < 1 / 3:
        kat, ulozenie = math.pi, "do_gory_nogami"
    else:
        kat, ulozenie = math.radians(90 + rng.uniform(-20, 20)), "bokiem"
    t = rng.uniform(0, 2 * math.pi)
    return trimesh.transformations.rotation_matrix(kat, [math.cos(t), math.sin(t), 0.0]), ulozenie


def widok_z_gory(m: trimesh.Trimesh, prog: float = NORMALNA_NIEWIDOCZNA) -> trimesh.Trimesh:
    """Usuwa trójkąty skierowane w dół (normalna z < prog): skaner patrzy z góry."""
    out = m.copy()
    out.update_faces(out.face_normals[:, 2] >= prog)
    out.remove_unreferenced_vertices()
    return out


def usun_plamy(m: trimesh.Trimesh, udzial: float, rng: np.random.Generator, ile_plam: int | None = None) -> tuple[trimesh.Trimesh, float]:
    """Usuwa ``udzial`` powierzchni pracy w 2–4 okrągłych plamach (zasłonięcia, przezierna cyrkonia).

    Każda plama: losowy trójkąt jako środek, promień dobrany bisekcją tak, by plama zabrała swoją część
    docelowej powierzchni. Zwraca siatkę i faktyczny udział powierzchni, który został.
    """
    if not (0 <= udzial < 1):
        raise ValueError(f"udział usuwany musi być z [0, 1), jest {udzial}")
    A0 = float(m.area)
    out = m.copy()
    k = int(ile_plam if ile_plam is not None else rng.integers(2, 5))
    cel = A0 * udzial / k
    for _ in range(k):
        if len(out.faces) == 0:
            break
        c = out.triangles_center
        pola = out.area_faces
        srodek = c[int(rng.integers(len(c)))]
        odl = np.linalg.norm(c - srodek, axis=1)
        lo, hi = 0.0, float(odl.max()) + 1e-6
        for _ in range(40):
            r = (lo + hi) / 2
            if pola[odl < r].sum() < cel:
                lo = r
            else:
                hi = r
        out.update_faces(odl >= hi)
    out.remove_unreferenced_vertices()
    return out, float(out.area / A0) if A0 > 0 else 0.0


def ubytek_widoczny(m: trimesh.Trimesh, u: Ubytek, srodek_kuli: np.ndarray | None = None) -> bool:
    """Czy po usunięciu części powierzchni w skanie została powierzchnia ubytku.

    Generator w wersji 2 podaje środek kuli ubytku (``srodek_kuli``, układ siatki ``m``): ubytek jest widoczny, gdy
    ≥ 3 wierzchołki leżą na jego sferze (± 0,01 mm) — nowa powierzchnia albo jej obrys. Bez środka kuli (wersja 1):
    ≥ 3 wierzchołki w promieniu 0,5·r od środka z prawdy — reguła sprzed P4, zostawiona bez zmian (uwaga: czasza
    wersji 1 leży ≥ 0,7·r od tego środka, więc reguła odrzuca prawie każdy ubytek o r > 0,086 mm; opis w synth.md)."""
    if srodek_kuli is not None:
        return bool((np.abs(np.linalg.norm(m.vertices - srodek_kuli, axis=1) - u.srednica / 2) < 0.01).sum() >= 3)
    c = np.array([u.x, u.y, u.z])
    r = max(0.5 * u.srednica / 2, 0.06)
    return bool((np.linalg.norm(m.vertices - c, axis=1) < r).sum() >= 3)


def drgniecie(m: trimesh.Trimesh, rng: np.random.Generator) -> trimesh.Trimesh:
    """Podwójna powierzchnia: kopia części siatki przesunięta o 0,08–0,15 mm."""
    k = rng.uniform(0.08, 0.15)
    kier = rng.normal(size=3)
    kier[2] *= 0.2
    kier = kier / np.linalg.norm(kier) * k
    kopia = m.copy()
    # losowa „połowa” siatki: trójkąty po jednej stronie losowej płaszczyzny
    norm = rng.normal(size=3)
    strona = ((kopia.triangles_center - kopia.centroid) @ norm) > 0
    kopia.update_faces(strona)
    kopia.apply_translation(kier)
    return trimesh.util.concatenate([m, kopia])


def _stadion(u: np.ndarray, v: np.ndarray, g: U.Gniazdo) -> np.ndarray:
    """Odległość punktów (u, v) w układzie rynienki od jej obrysu na wierzchu (stadion); ujemna = wewnątrz."""
    return np.hypot(np.maximum(np.abs(u) - (g.l - g.w) / 2, 0.0), v) - g.w / 2


def przenikanie(V: np.ndarray, g: U.Gniazdo) -> float:
    """Największe wejście wierzchołków ``V`` (układ skanu) w dno lub ściankę gniazda [mm]; 0 = brak.

    Ścianka: stożek 15° (gniazdo okrągłe) albo skośna ścianka rynienki o obrysie
    stadionu (półokrągłe końce), od dna ``z_dno`` do wierzchu ``z_top``. Punkty nad wierzchem płytki nie są liczone.
    """
    z = V[:, 2]
    pod_dnem = float(np.maximum(g.z_dno - z, 0).max(initial=0.0))
    w = z < g.z_top
    dx, dy, zw = V[w, 0] - g.x, V[w, 1] - g.y, z[w]
    if g.okragle:
        boki = np.hypot(dx, dy) - (g.promien_dolny() + (zw - g.z_dno) * TAN_SCIANKI)
    else:
        a = math.radians(g.angle)
        u = dx * math.cos(a) + dy * math.sin(a)
        v = -dx * math.sin(a) + dy * math.cos(a)
        zwezenie = (g.z_top - zw) * TAN_SCIANKI  # o tyle ścianka na wysokości z jest węższa niż otwór
        boki = _stadion(u, v, g) + zwezenie  # obrys rynienki to stadion (półokrągłe końce), nie prostokąt
    return max(pod_dnem, float(np.maximum(boki, 0).max(initial=0.0)))


def _uniesienie(V: np.ndarray, g: U.Gniazdo, ox: float, oy: float) -> float:
    """Najniższe z dna pracy (``V``: środek xy w 0, dno na z=0) przesuniętej o (ox, oy) od środka gniazda,
    przy którym żaden wierzchołek pod wierzchem płytki nie wchodzi w ściankę ani dno."""
    x, y = V[:, 0] + ox, V[:, 1] + oy
    if g.okragle:
        wystaje = np.hypot(x, y) - g.promien_dolny()  # o tyle punkt wychodzi poza obrys dna
    else:
        a = math.radians(g.angle)
        u = x * math.cos(a) + y * math.sin(a)
        v = -x * math.sin(a) + y * math.cos(a)
        wystaje = _stadion(u, v, g) + g.depth * TAN_SCIANKI  # o tyle punkt wychodzi poza obrys dna (stadion)
    # punkt wystający poza dno o e > 0 może leżeć najniżej na z = z_dno + e / tan(15°)
    s_min = g.z_dno + np.maximum(wystaje, 0) / TAN_SCIANKI - V[:, 2]
    s = g.z_dno
    for _ in range(20):  # punkty, które po uniesieniu są nad wierzchem płytki, nie podpierają pracy
        nar = (V[:, 2] + s < g.z_top) & (s_min > s)
        if not nar.any():
            return s
        s = float(s_min[nar].max())
    return s


def szerokosc_pracy(m: trimesh.Trimesh) -> float:
    """Dłuższy bok prostokąta obrysu xy o najmniejszym polu [mm] (most: > PROG_MOSTU_MM)."""
    _, boki = trimesh.bounds.oriented_bounds_2D(m.vertices[:, :2])
    return float(max(boki))


def kandydaci_gniazd(m: trimesh.Trimesh, okragle: list[U.Gniazdo], rynienki: list[U.Gniazdo]) -> list[U.Gniazdo]:
    """Gniazda do sprawdzenia dla pracy brzegiem do góry: most → tylko rynienki; korona → okrągłe od najmniejszego
    (pomijając na pewno za małe), a gdy żadne nie pasuje — rynienki (np. 3-punktowy waxup przedni 18 mm)."""
    szer = szerokosc_pracy(m)
    if szer > PROG_MOSTU_MM:
        return list(rynienki)
    return [g for g in sorted(okragle, key=lambda g: g.d_top) if g.d_top >= szer * 0.55] + list(rynienki)


def os_glowna_deg(xy: np.ndarray) -> float:
    """Kąt (od +x, w stopniach) osi głównej PCA punktów xy — wzdłuż niej leży most."""
    c = xy - xy.mean(0)
    w, v = np.linalg.eigh(c.T @ c)
    return math.degrees(math.atan2(v[1, -1], v[0, -1]))


def osadz_w_gniezdzie(
    m: trimesh.Trimesh, g: U.Gniazdo, rng: np.random.Generator, luz_xy: float = 0.6
) -> np.ndarray | None:
    """Liczy macierz 4×4 układającą pracę (brzegiem do góry, środek xy w 0) w gnieździe.

    Losowy obrót wokół z, lekki przechył, przesunięcie w gnieździe, a wysokość
    tak, by praca oparła się o skośną ściankę gniazda (stożek albo ścianki
    rynienki) albo o jego dno. Przesunięcie jest losowane przed liczeniem
    uniesienia, więc praca nigdy nie wchodzi w ściankę (B1, B1b); wynik jest
    sprawdzany funkcją ``przenikanie``. Zwraca None, gdy praca nie mieści się w gnieździe.
    """
    if g.okragle:
        jaw = rng.uniform(0, 2 * math.pi)
    else:  # most w rynience leży wzdłuż niej (oś główna obrysu xy wzdłuż rynienki), ewentualnie odwrócony
        jaw = math.radians(g.angle - os_glowna_deg(m.vertices[:, :2]) + rng.choice([0.0, 180.0]) + rng.uniform(-1.0, 1.0))
    przechyl = math.radians(rng.uniform(0, 4.0))
    os_przech = np.array([math.cos(rng.uniform(0, 2 * math.pi)), math.sin(rng.uniform(0, 2 * math.pi)), 0])
    R = trimesh.transformations.rotation_matrix(jaw, [0, 0, 1])
    R = trimesh.transformations.rotation_matrix(przechyl, os_przech) @ R
    V0 = trimesh.transform_points(m.vertices, R)
    c = np.array([V0[:, 0].mean(), V0[:, 1].mean(), V0[:, 2].min()])
    V = V0 - c  # środek xy w 0, dno na z=0
    los = rng.uniform(-1, 1, 2)  # przesunięcie w gnieździe, losowane PRZED uniesieniem

    if g.okragle:
        rho = np.hypot(V[:, 0], V[:, 1])
        # najniższa szerokość pracy musi wejść w dno gniazda, inaczej nie mieści się
        if rho[V[:, 2] < 0.5].min(initial=np.inf) > g.promien_gorny:
            return None
        s0 = _uniesienie(V, g, 0.0, 0.0)
        luz = luz_xy * max(0.0, 1 - (s0 - g.z_dno) / g.depth)  # praca oparta o ściankę ma mniej luzu
        ox, oy = los * luz
    else:
        a = math.radians(g.angle)
        u = V[:, 0] * math.cos(a) + V[:, 1] * math.sin(a)
        v = -V[:, 0] * math.sin(a) + V[:, 1] * math.cos(a)
        if (u.max() - u.min()) > g.l - 1.0 or (v.max() - v.min()) > g.w - 0.4:
            return None
        s0 = _uniesienie(V, g, 0.0, 0.0)
        du = los[0] * max(0.0, (g.l - (u.max() - u.min())) / 2 - 0.5)
        dv = los[1] * max(0.0, (g.w - (v.max() - v.min())) / 2 - 0.5)
        ox, oy = du * math.cos(a) - dv * math.sin(a), du * math.sin(a) + dv * math.cos(a)  # z układu rynienki do xy
    if s0 - g.z_dno > MAKS_UNIESIENIE:  # praca wisi na krawędzi zamiast siedzieć w gnieździe
        return None
    s = _uniesienie(V, g, ox, oy)
    if s - g.z_dno > MAKS_UNIESIENIE:  # przesunięta zaklinowałaby się wysoko: zostaje na środku
        ox = oy = 0.0
        s = s0
    T = trimesh.transformations.translation_matrix([g.x + ox - c[0], g.y + oy - c[1], s - c[2]]) @ R
    pr = przenikanie(trimesh.transform_points(m.vertices, T), g)
    if pr > TOLERANCJA_PRZENIKANIA:
        raise AssertionError(f"osadzenie w gnieździe {g.id} przenika ściankę/dno o {pr:.6f} mm")
    return T


# ----------------------------------------------------------------------------
# płytka
# ----------------------------------------------------------------------------
def siatka_plytki(uk: U.UkladPlytki, numer: int, sigma: float, rng: np.random.Generator) -> trimesh.Trimesh:
    """STL płytki z zagęszczonymi znacznikami i dołkami kodu, z szumem."""
    m = trimesh.load(uk.plik_stl(numer), force="mesh")
    V, F = m.vertices.copy(), m.faces.copy()
    c = m.triangles_center
    blisko = np.zeros(len(F), dtype=bool)
    for z in uk.markers:
        blisko |= np.hypot(c[:, 0] - z.x, c[:, 1] - z.y) < z.d / 2 + 1.5
    for d in uk.code_dimples:
        blisko |= np.hypot(c[:, 0] - d.x, c[:, 1] - d.y) < d.d / 2 + 1.0
    blisko &= c[:, 2] > uk.thickness - 3.5  # tylko wierzch (nie kieszenie magnesów)
    Vs, Fs = trimesh.remesh.subdivide_to_size(V, F[blisko], max_edge=0.12)
    F = np.concatenate([F[~blisko], Fs + len(V)])
    V = np.concatenate([V, Vs])
    out = trimesh.Trimesh(V, F, process=False)
    out.merge_vertices()
    # skaner widzi płytkę od góry: spód usuwamy (ścianki kieszeni magnesów zostają — S8)
    out.update_faces(out.triangles_center[:, 2] > 0.5)
    return dodaj_szum(out, sigma, rng)


# ----------------------------------------------------------------------------
# cała płytka
# ----------------------------------------------------------------------------
def poranna(plytka: str) -> bool:
    """Czy płytka jest poranna (prace spieczone, skala 1): ``poranna`` i ``okragla_poranna``, także w układzie ``*_r54``."""
    return U.typ_plytki(plytka).endswith("poranna")


def _z_ustawien(ust: dict, plytka: str) -> dict:
    s, i = ust["synth"], ust["inspect"]
    return {
        "szum_sigma": s["szum_sigma_mm"],
        "wspolczynnik": WSPOLCZYNNIK_PORANNA if poranna(plytka) else (s["wspolczynnik_min"], s["wspolczynnik_max"]),
        "srednica_ubytku": (i["srednica_min_mm"], i["srednica_max_mm"]),
        "srednica_wykrywalna": (i["srednica_min_mm"], i["srednica_max_mm"]),
        "pas_brzegu": i["pas_brzegu_mm"],
        "prog_glebokosci": i["prog_glebokosci_mm"],
        "odstep_ubytku": s["odstep_ubytku_mm"],
        "krawedz_rozmiar": (s["krawedz_rozmiar_min_mm"], s["krawedz_rozmiar_max_mm"]),
    }


@dataclass
class Opcje:
    """Parametry generatora. Pole ``None`` = wartość z ``ustawienia.toml`` (płytka wieczorna; patrz ``z_toml``)."""

    szum_sigma: float | None = None  # [synth] szum_sigma_mm
    wspolczynnik: tuple[float, float] | None = None  # [synth] wspolczynnik_min/max; rano WSPOLCZYNNIK_PORANNA
    ubytki_na_prace: tuple[int, int] = (0, 2)
    srednica_ubytku: tuple[float, float] | None = None  # [inspect] srednica_min/max_mm
    srednica_wykrywalna: tuple[float, float] | None = None  # [inspect] srednica_min/max_mm (do pola wykrywalny)
    pas_brzegu: float | None = None  # [inspect] pas_brzegu_mm
    prog_glebokosci: float | None = None  # [inspect] prog_glebokosci_mm
    p_drgniecia: float = 0.0
    prace_na_plytce: int | None = None  # None = ile się zmieści z puli
    mosty: bool = True
    orientacja: str = "auto"  # auto | brzeg_dol | brzeg_gora (orientacja_brzegiem_do_gory)
    poza_uklad: bool = False  # losowe położenie całego skanu (obrót wokół z, przechył ≤ 3°, przesunięcie) — prawda: poza_skanu
    pole: float | None = None  # średnica pola skanowania: skan przycięty do koła (środek ± 1,5 mm od środka płytki)
    p_bokiem: float = 0.0  # P3a: prawdopodobieństwo, że praca leży bokiem / do góry nogami (widziana z góry: spód usunięty)
    p_pokrycie: float = 0.0  # P3a: prawdopodobieństwo usunięcia części powierzchni skanu pracy (plamy)
    pokrycie_usuwane: tuple[float, float] = (0.3, 0.6)  # P3a: udział powierzchni usuwany przy --pokrycie
    p_poprawki: float = 0.0  # P3a: prawdopodobieństwo gładkiej poprawki ręcznej na pracy
    wersja_ubytkow: int = 2  # P4: 2 = czasza ubytku w materiale; 1 = generator sprzed P4 (odtwarzanie starych zestawów bajt w bajt)
    odstep_ubytku: float | None = None  # P4: [synth] odstep_ubytku_mm — gęstość punktów nowej powierzchni ubytku i jej otoczenia
    krawedz_na_prace: tuple[int, int] = (0, 0)  # K6: ile ukruszeń celowych (na krawędzi brzegu) na pracę
    krawedz_rozmiar: tuple[float, float] | None = None  # K6: zakres rozmiaru (promień kuli) — [synth] krawedz_rozmiar_min/max_mm
    krawedz_rozmiary: tuple[float, ...] | None = None  # K6: lista rozmiarów zamiast zakresu (np. 0.08, 0.10, 0.15)
    krawedz_polozenia: tuple[str, ...] = ("srodek", "zewn", "wewn")  # K6: losowane położenia (POLOZENIA_UKRUSZEN)

    def __post_init__(self) -> None:
        if self._niepelne():
            for k, v in _z_ustawien(UST.domyslne(), "wieczorna").items():
                if getattr(self, k) is None:
                    setattr(self, k, v)
        self._waliduj()

    def _niepelne(self) -> bool:
        return None in (self.szum_sigma, self.wspolczynnik, self.srednica_ubytku, self.srednica_wykrywalna,
                        self.pas_brzegu, self.prog_glebokosci, self.odstep_ubytku, self.krawedz_rozmiar)

    @classmethod
    def z_toml(cls, ust: dict | None = None, plytka: str = "wieczorna", **nadpisania) -> Opcje:
        """Opcje z ustawień dla płytki ``plytka``; ``nadpisania`` różne od None mają pierwszeństwo."""
        wart = _z_ustawien(UST.domyslne() if ust is None else ust, plytka)
        wart.update({k: v for k, v in nadpisania.items() if v is not None})
        return cls(**wart)

    def _waliduj(self) -> None:
        def zakres(nazwa: str, typ, dodatni: bool) -> tuple:
            v = getattr(self, nazwa)
            try:
                a, b = (typ(x) for x in v)
            except (TypeError, ValueError):
                raise ValueError(f"Opcje.{nazwa}: oczekiwano pary (min, max), jest {v!r}") from None
            if not (math.isfinite(a) and math.isfinite(b) and (a > 0 if dodatni else a >= 0) and a <= b):
                raise ValueError(f"Opcje.{nazwa}: musi być {'0 <' if dodatni else '0 ≤'} min ≤ max, jest {v!r}")
            if typ is int and any(float(x) != int(x) for x in v):
                raise ValueError(f"Opcje.{nazwa}: liczby całkowite, jest {v!r}")
            return a, b

        self.wspolczynnik = zakres("wspolczynnik", float, True)
        self.ubytki_na_prace = zakres("ubytki_na_prace", int, False)
        self.srednica_ubytku = zakres("srednica_ubytku", float, True)
        self.srednica_wykrywalna = zakres("srednica_wykrywalna", float, True)
        self.pokrycie_usuwane = zakres("pokrycie_usuwane", float, False)
        if self.pokrycie_usuwane[1] >= 1:
            raise ValueError(f"Opcje.pokrycie_usuwane: udział usuwany musi być < 1, jest {self.pokrycie_usuwane!r}")
        self.krawedz_na_prace = zakres("krawedz_na_prace", int, False)
        self.krawedz_rozmiar = zakres("krawedz_rozmiar", float, True)
        if self.krawedz_rozmiary is not None:
            try:
                self.krawedz_rozmiary = tuple(float(x) for x in self.krawedz_rozmiary)
            except (TypeError, ValueError):
                raise ValueError(f"Opcje.krawedz_rozmiary: oczekiwano listy liczb, jest {self.krawedz_rozmiary!r}") from None
            if not self.krawedz_rozmiary or not all(math.isfinite(x) and x > 0 for x in self.krawedz_rozmiary):
                raise ValueError(f"Opcje.krawedz_rozmiary: niepusta lista rozmiarów > 0 mm, jest {self.krawedz_rozmiary!r}")
        self.krawedz_polozenia = tuple(self.krawedz_polozenia) if not isinstance(self.krawedz_polozenia, str) else (self.krawedz_polozenia,)
        if not self.krawedz_polozenia or any(p not in POLOZENIA_UKRUSZEN for p in self.krawedz_polozenia):
            raise ValueError(f"Opcje.krawedz_polozenia: {self.krawedz_polozenia!r} — dopuszczalne {', '.join(POLOZENIA_UKRUSZEN)}")
        if self.wersja_ubytkow not in WERSJE_UBYTKOW:
            raise ValueError(f"Opcje.wersja_ubytkow: {self.wersja_ubytkow!r} — dopuszczalne {WERSJE_UBYTKOW}")
        if self.wersja_ubytkow == 1 and self.krawedz_na_prace[1] > 0:
            raise ValueError("Opcje.krawedz_na_prace: ukruszenia celowe (K6) wymagają wersja_ubytkow = 2")
        for nazwa, ok in (
            ("szum_sigma", lambda v: v >= 0),
            ("pas_brzegu", lambda v: v > 0),
            ("odstep_ubytku", lambda v: v > 0),
            ("prog_glebokosci", lambda v: v >= 0),
            ("p_drgniecia", lambda v: 0 <= v <= 1),
            ("p_bokiem", lambda v: 0 <= v <= 1),
            ("p_pokrycie", lambda v: 0 <= v <= 1),
            ("p_poprawki", lambda v: 0 <= v <= 1),
        ):
            v = getattr(self, nazwa)
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or not ok(v):
                raise ValueError(f"Opcje.{nazwa}: niedozwolona wartość {v!r}")
        if self.prace_na_plytce is not None and not (isinstance(self.prace_na_plytce, int) and self.prace_na_plytce >= 0):
            raise ValueError(f"Opcje.prace_na_plytce: None albo liczba ≥ 0, jest {self.prace_na_plytce!r}")
        if self.orientacja not in ORIENTACJE:
            raise ValueError(f"Opcje.orientacja: {self.orientacja!r} — dopuszczalne {', '.join(ORIENTACJE)}")
        if self.pole is not None and not (isinstance(self.pole, (int, float)) and math.isfinite(self.pole) and self.pole > 0):
            raise ValueError(f"Opcje.pole: None albo średnica > 0, jest {self.pole!r}")

    def wykrywalny(self, srednica: float, glebokosc: float) -> bool:
        """Czy ubytek mieści się w specyfikacji detektora ([inspect]): dość głęboki i w zakresie średnic."""
        s0, s1 = self.srednica_wykrywalna
        return bool(glebokosc >= self.prog_glebokosci and s0 <= srednica <= s1)


def generuj_plytke(
    uk: U.UkladPlytki,
    numer: int,
    projekty: list[Path],
    rng: np.random.Generator,
    opcje: Opcje,
    seed: int,
) -> tuple[trimesh.Trimesh, PrawdaPlytki]:
    czesci = [siatka_plytki(uk, numer, opcje.szum_sigma, rng)]
    wolne_okragle = uk.gniazda_okragle()
    wolne_rynienki = uk.rynienki()
    prace: list[PracaNaPlytce] = []
    pominiete: list[str] = []
    kolejnosc = list(rng.permutation(len(projekty)))
    limit = opcje.prace_na_plytce if opcje.prace_na_plytce is not None else len(projekty)

    for i in kolejnosc:
        if len(prace) >= limit:
            break
        plik = projekty[i]
        m = wczytaj_projekt(plik)
        if m is None:
            continue
        w = float(rng.uniform(*opcje.wspolczynnik))
        S = trimesh.transformations.scale_matrix(w)
        O = orientacja_brzegiem_do_gory(m, opcje.orientacja, plik.name)
        m2 = m.copy()
        m2.apply_transform(O @ S)

        most = szerokosc_pracy(m2) > PROG_MOSTU_MM
        if most and not opcje.mosty:
            continue
        # ubytki i poprawki na pracy brzegiem do góry (pas brzegu liczony od brzegu, nie od wierzchu w gnieździe)
        ubytki_lok: list[Ubytek] = []
        n_ubytkow = int(rng.integers(opcje.ubytki_na_prace[0], opcje.ubytki_na_prace[1] + 1))
        linie = material = None
        if opcje.wersja_ubytkow != 1 and (n_ubytkow > 0 or opcje.krawedz_na_prace[1] > 0):
            # linie krawędzi brzegu każdego filaru (raz na projekt, pamięć w module krawedz) i materiał przed ubytkami
            linie = KR.linie_siatki(m2, skala=w, klucz=KR.klucz_projektu(skrot_pliku(plik), O))
            material = Material(m2)
        for _ in range(n_ubytkow):
            m2, ub = wytnij_ubytek(m2, float(rng.uniform(*opcje.srednica_ubytku)), rng, opcje.pas_brzegu, linie=linie, material=material,
                                   odstep=opcje.odstep_ubytku, wersja=opcje.wersja_ubytkow)
            ub.wykrywalny = opcje.wykrywalny(ub.srednica, ub.glebokosc)
            ubytki_lok.append(ub)
        pominiete_k6 = 0
        if opcje.krawedz_na_prace[1] > 0:  # K6: ukruszenia celowe na krawędzi brzegu (losowania tylko, gdy zamówione)
            for _ in range(int(rng.integers(opcje.krawedz_na_prace[0], opcje.krawedz_na_prace[1] + 1))):
                gdzie = str(rng.choice(opcje.krawedz_polozenia))
                rozmiar = float(rng.choice(opcje.krawedz_rozmiary)) if opcje.krawedz_rozmiary else float(rng.uniform(*opcje.krawedz_rozmiar))
                m2, ub = wytnij_ukruszenie(m2, linie, gdzie, rozmiar, rng, material=material, pas_brzegu=opcje.pas_brzegu, odstep=opcje.odstep_ubytku)
                if ub is None:
                    pominiete_k6 += 1
                    continue
                ub.wykrywalny = opcje.wykrywalny(ub.srednica, ub.glebokosc)
                ubytki_lok.append(ub)
        poprawki_lok: list[Poprawka] = []
        if rng.uniform() < opcje.p_poprawki:
            m2, pop = poprawka_reczna(m2, rng)
            poprawki_lok.append(pop)
        R = np.eye(4)
        ulozenie = "dobrze"
        if rng.uniform() < opcje.p_bokiem:
            R, ulozenie = obrot_bokiem(rng)
            m2.apply_transform(R)
        T = None
        g_wyb = None
        for g in kandydaci_gniazd(m2, wolne_okragle, wolne_rynienki):
            T = osadz_w_gniezdzie(m2, g, rng)
            if T is not None:
                g_wyb = g
                break
        if T is None:
            pominiete.append(skrot_pliku(plik))
            continue
        (wolne_rynienki if not g_wyb.okragle else wolne_okragle).remove(g_wyb)

        m3 = m2.copy()
        m3.apply_transform(T)
        TR = T @ R
        ubytki = []
        for ub in ubytki_lok:
            x, y, z = trimesh.transform_points([[ub.x, ub.y, ub.z]], TR)[0]
            ubytki.append(replace(ub, x=float(x), y=float(y), z=float(z)))
        poprawki = []
        for pop in poprawki_lok:
            x, y, z = trimesh.transform_points([[pop.x, pop.y, pop.z]], TR)[0]
            poprawki.append(Poprawka(float(x), float(y), float(z), pop.srednica, pop.glebokosc))
        pokrycie = 1.0
        A_cala = float(m3.area)
        if ulozenie != "dobrze":  # praca bokiem: skaner widzi ją tylko z góry
            m3 = widok_z_gory(m3)
            pokrycie = float(m3.area / A_cala) if A_cala > 0 else 0.0
        if rng.uniform() < opcje.p_pokrycie:
            m3, zostalo = usun_plamy(m3, float(rng.uniform(*opcje.pokrycie_usuwane)), rng)
            pokrycie *= zostalo
        if pokrycie < 1.0:
            # wersja 2: środki kul ubytków (material.kule, w kolejności ubytków) przeniesione do układu skanu
            srodki = trimesh.transform_points([c for c, _ in material.kule], TR) if material is not None and material.kule else None
            for j, ub in enumerate(ubytki):
                ub.widoczny = ubytek_widoczny(m3, ub, None if srodki is None else srodki[j])
                ub.wykrywalny = ub.wykrywalny and ub.widoczny
        drg = bool(rng.uniform() < opcje.p_drgniecia)
        m3 = dodaj_szum(m3, opcje.szum_sigma, rng)
        if drg:
            m3 = drgniecie(m3, rng)
        czesci.append(m3)
        prace.append(
            PracaNaPlytce(
                gniazdo=g_wyb.id,
                projekt=skrot_pliku(plik),
                wspolczynnik=w,
                transformacja=(TR @ O).tolist(),  # (projekt × w) → skan: orientacja brzegiem do góry, obrót bokiem, osadzenie
                ubytki=ubytki,
                drgniecie=drg,
                ulozenie=ulozenie,
                pokrycie=round(pokrycie, 4),
                poprawki=poprawki,
                ukruszenia_pominiete=pominiete_k6,
            )
        )

    zajete = {p.gniazdo for p in prace}
    prawda = PrawdaPlytki(
        plytka=uk.nazwa,
        numer=numer,
        seed=seed,
        szum_sigma=opcje.szum_sigma,
        z_top=uk.thickness,
        prace=prace,
        gniazda_puste=[g.id for g in uk.sockets if g.id not in zajete],
        pominiete=pominiete,
    )
    if pominiete:
        warnings.warn(
            f"płytka {uk.nazwa} nr {numer} seed {seed}: {len(pominiete)} projektów nie zmieściło się w żadnym wolnym gnieździe: "
            + ", ".join(pominiete), stacklevel=2
        )
    skan = trimesh.util.concatenate(czesci)
    if opcje.pole is not None:  # pole skanowania: koło o średnicy ``pole`` prawie w środku płytki
        sr = rng.uniform(-1.5, 1.5, 2)
        skan = przytnij_do_kola(skan, sr, opcje.pole / 2)
        skan.remove_unreferenced_vertices()
        prawda.pole_d = float(opcje.pole)
        prawda.pole_srodek = [float(sr[0]), float(sr[1])]
    if opcje.poza_uklad:  # skaner ma własny układ: płytka leży gdzieś, obrócona, lekko przechylona
        P = losowa_poza_skanu(rng)
        skan.apply_transform(P)
        prawda.poza_skanu = P.tolist()
    return skan, prawda


def przytnij_do_kola(m: trimesh.Trimesh, srodek, promien: float, krok: float = 0.4) -> trimesh.Trimesh:
    """Zostawia część siatki w kole (pole skanowania): trójkąty przecinające okrąg są najpierw
    zagęszczone do ``krok`` mm, potem zostają te ze środkiem w kole (brzeg z dokładnością ~krok/2;
    duże trójkąty płaskiego wierzchu nie wystają poza pole)."""
    V, F = m.vertices, m.faces
    w = np.hypot(V[:, 0] - srodek[0], V[:, 1] - srodek[1]) <= promien
    wf = w[F]
    cale = wf.all(axis=1)
    przec = wf.any(axis=1) & ~cale
    czesci = [F[cale]]
    Vn = V
    if przec.any():
        Vs, Fs = trimesh.remesh.subdivide_to_size(V, F[przec], max_edge=krok)
        c = Vs[Fs].mean(axis=1)
        Fs = Fs[np.hypot(c[:, 0] - srodek[0], c[:, 1] - srodek[1]) <= promien]
        czesci.append(Fs + len(V))
        Vn = np.vstack([V, Vs])
    out = trimesh.Trimesh(Vn, np.vstack(czesci), process=False)
    out.merge_vertices()
    out.remove_unreferenced_vertices()
    return out


def losowa_poza_skanu(rng: np.random.Generator) -> np.ndarray:
    """Macierz 4×4 układ płytki → układ skanu: obrót wokół z 0…360°, przechył 0…3°, przesunięcie ±20 mm (z ±5)."""
    R = trimesh.transformations.rotation_matrix(rng.uniform(0, 2 * math.pi), [0, 0, 1])
    t = rng.uniform(0, 2 * math.pi)
    P = trimesh.transformations.rotation_matrix(math.radians(rng.uniform(0, 3.0)), [math.cos(t), math.sin(t), 0])
    T = trimesh.transformations.translation_matrix([rng.uniform(-20, 20), rng.uniform(-20, 20), rng.uniform(-5, 5)])
    return T @ P @ R


def zapisz(
    skan: trimesh.Trimesh, prawda: PrawdaPlytki, wyjscie: Path, nazwa: str, nadpisz: bool = False
) -> tuple[Path, Path]:
    p_stl = wyjscie / f"{nazwa}.stl"
    p_json = wyjscie / f"{nazwa}.json"
    if not nadpisz:
        for p in (p_stl, p_json):
            if p.exists():
                raise FileExistsError(f"{p} już istnieje (nadpisz=True / --nadpisz, żeby zastąpić)")
    wyjscie.mkdir(parents=True, exist_ok=True)
    skan.export(p_stl)
    prawda.plik_stl = p_stl.name
    p_json.write_text(json.dumps(asdict(prawda), ensure_ascii=False, indent=1), encoding="utf-8")
    return p_stl, p_json


def dopisz_mape_projektow(plik: Path, projekty: list[Path]) -> dict[str, str]:
    """Dopisuje do ``plik`` (JSON) mapowanie skrót → nazwa pliku projektu (bez katalogu)."""
    mapa = json.loads(plik.read_text(encoding="utf-8")) if plik.exists() else {}
    mapa.update({skrot_pliku(p): p.name for p in projekty})
    plik.parent.mkdir(parents=True, exist_ok=True)
    plik.write_text(json.dumps(mapa, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    return mapa


def wczytaj_prawde(p_json: Path) -> PrawdaPlytki:
    d = json.loads(p_json.read_text(encoding="utf-8"))
    prace = [
        PracaNaPlytce(**{**p, "ubytki": [Ubytek(**u) for u in p["ubytki"]], "poprawki": [Poprawka(**q) for q in p.get("poprawki", [])]})
        for p in d.pop("prace")
    ]
    return PrawdaPlytki(prace=prace, **d)


# ----------------------------------------------------------------------------
# wiersz poleceń
# ----------------------------------------------------------------------------
def _liczba(typ, minimum: float | None = None, maksimum: float | None = None, dodatnia: bool = False):
    def parsuj(s: str):
        try:
            v = typ(s)
        except ValueError:
            raise argparse.ArgumentTypeError(f"oczekiwano liczby, jest {s!r}") from None
        if not math.isfinite(v) or (dodatnia and v <= 0) or (minimum is not None and v < minimum) or (
            maksimum is not None and v > maksimum
        ):
            granice = "> 0" if dodatnia else f"z przedziału [{minimum}, {'∞' if maksimum is None else maksimum}]"
            raise argparse.ArgumentTypeError(f"wartość {s!r} musi być {granice}")
        return v

    return parsuj


def _zakres(typ, dodatni: bool):
    def parsuj(s: str) -> tuple:
        try:
            a, b = (typ(x) for x in s.split("-"))
        except ValueError:
            raise argparse.ArgumentTypeError(f"oczekiwano zakresu MIN-MAX, np. {'0.2-0.6' if typ is float else '0-2'}; jest {s!r}") from None
        if not (math.isfinite(a) and math.isfinite(b) and (a > 0 if dodatni else a >= 0) and a <= b):
            raise argparse.ArgumentTypeError(f"zakres {s!r}: musi być {'0 <' if dodatni else '0 ≤'} MIN ≤ MAX")
        return a, b

    return parsuj


def _lista(typ):
    def parsuj(s: str) -> tuple:
        try:
            v = tuple(typ(x.strip()) for x in s.split(","))
        except ValueError:
            raise argparse.ArgumentTypeError(f"oczekiwano listy rozdzielonej przecinkami; jest {s!r}") from None
        if not v or any(x == "" for x in v):
            raise argparse.ArgumentTypeError(f"pusta pozycja na liście {s!r}")
        return v

    return parsuj


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ustawienia", type=Path, default=None, help="plik ustawień (domyślnie ustawienia.toml programu)")
    ap.add_argument("--projekty", type=Path, default=Path("dane/stl"), help="folder z STL projektów")
    ap.add_argument("--plytka", default="wieczorna", help="układ płytki z [plytki] w ustawieniach (wieczorna, poranna, okragla_…; stary układ: …_r54)")
    ap.add_argument("--numer", type=int, default=None, help="numer płytki (domyślnie losowy z dostępnych)")
    ap.add_argument("--ile", type=_liczba(int, minimum=0), default=1, help="ile płytek wygenerować")
    ap.add_argument("--prace", type=_liczba(int, minimum=0), default=None, help="ile prac na płytce (domyślnie: ile wejdzie)")
    ap.add_argument("--szum", type=_liczba(float, minimum=0), default=None, help="σ szumu [mm] (domyślnie [synth] szum_sigma_mm)")
    ap.add_argument("--ubytki", type=_zakres(int, False), default=(0, 2), help="zakres ubytków na pracę, np. 0-2")
    ap.add_argument("--srednica", type=_zakres(float, True), default=None,
                    help="zakres średnic ubytków [mm] (domyślnie [inspect] srednica_min_mm-srednica_max_mm)")
    ap.add_argument("--drgniecie", type=_liczba(float, 0, 1), default=0.0, help="prawdopodobieństwo podwójnej powierzchni")
    ap.add_argument("--wspolczynnik", type=_liczba(float, dodatnia=True), default=None,
                    help="stały współczynnik skurczu (domyślnie: wieczorna losowo z [synth], poranna 1,0)")
    ap.add_argument("--orientacja", choices=ORIENTACJE, default="auto", help="gdzie projekt ma brzeg (auto: heurystyka krawędzi)")
    ap.add_argument("--poza-uklad", action="store_true", help="skan w losowym układzie skanera (prawda: poza_skanu)")
    ap.add_argument("--pole", type=_liczba(float, dodatnia=True), default=None, help="średnica pola skanowania [mm]: skan przycięty do koła")
    ap.add_argument("--bokiem", type=_liczba(float, 0, 1), default=0.0, help="P3a: prawdopodobieństwo pracy bokiem / do góry nogami (widzianej z góry)")
    ap.add_argument("--pokrycie", type=_liczba(float, 0, 1), default=0.0, help="P3a: prawdopodobieństwo usunięcia części powierzchni skanu pracy")
    ap.add_argument("--pokrycie-zakres", type=_zakres(float, False), default=(0.3, 0.6), help="udział usuwanej powierzchni przy --pokrycie, np. 0.3-0.6")
    ap.add_argument("--poprawka", type=_liczba(float, 0, 1), default=0.0, help="P3a: prawdopodobieństwo gładkiej poprawki ręcznej na pracy")
    ap.add_argument("--wersja-ubytkow", type=int, choices=WERSJE_UBYTKOW, default=2,
                    help="generator ubytków: 2 = czasza w materiale (domyślnie), 1 = sprzed P4, do odtwarzania starych zestawów bajt w bajt")
    ap.add_argument("--odstep-ubytku", type=_liczba(float, dodatnia=True), default=None,
                    help="odstęp punktów nowej powierzchni ubytku [mm] (domyślnie [synth] odstep_ubytku_mm)")
    ap.add_argument("--krawedz", type=_zakres(int, False), default=(0, 0),
                    help="K6: zakres liczby ukruszeń celowych na krawędzi brzegu na pracę, np. 1-2 (domyślnie 0-0)")
    ap.add_argument("--krawedz-rozmiar", type=_zakres(float, True), default=None,
                    help="K6: zakres rozmiaru ukruszenia = promienia kuli o środku na powierzchni [mm] "
                         "(domyślnie [synth] krawedz_rozmiar_min_mm-krawedz_rozmiar_max_mm)")
    ap.add_argument("--krawedz-rozmiary", type=_lista(float), default=None, help="K6: lista rozmiarów zamiast zakresu, np. 0.08,0.10,0.15,0.20,0.30,0.40")
    ap.add_argument("--krawedz-polozenie", type=_lista(str), default=("srodek", "zewn", "wewn"),
                    help=f"K6: losowane położenia, lista z: {', '.join(POLOZENIA_UKRUSZEN)} (domyślnie srodek,zewn,wewn)")
    ap.add_argument("--pamiec-linii", type=Path, default=None,
                    help="katalog pamięci podręcznej linii krawędzi brzegu na dysku (domyślnie tylko w pamięci procesu)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--wyjscie", type=Path, default=Path("dane/syntetyczne"))
    ap.add_argument("--mapa", type=Path, default=None,
                    help="plik mapowania skrót → nazwa projektu (domyślnie <wyjscie>/../mapa_projektow.json)")
    ap.add_argument("--nadpisz", action="store_true", help="zastąp istniejące skan_*.stl/.json")
    a = ap.parse_args()

    ust = UST.wczytaj_ustawienia(a.ustawienia)
    if a.plytka not in ust["plytki"]:
        ap.error(f"--plytka {a.plytka!r}: brak w [plytki] (są: {', '.join(ust['plytki'])})")
    uk = U.wczytaj(a.plytka, UST.katalog_plytki(ust, a.plytka))
    projekty = pliki_projektow(a.projekty)
    if not projekty:
        raise SystemExit(f"brak plików STL w {a.projekty}; uruchom narzedzia/atrapy_koron.py")
    try:
        opcje = Opcje.z_toml(
            ust,
            a.plytka,
            szum_sigma=a.szum,
            ubytki_na_prace=a.ubytki,
            srednica_ubytku=a.srednica,
            p_drgniecia=a.drgniecie,
            prace_na_plytce=a.prace,
            wspolczynnik=(a.wspolczynnik, a.wspolczynnik) if a.wspolczynnik is not None else None,
            orientacja=a.orientacja,
            poza_uklad=a.poza_uklad,
            pole=a.pole,
            p_bokiem=a.bokiem,
            p_pokrycie=a.pokrycie,
            pokrycie_usuwane=a.pokrycie_zakres,
            p_poprawki=a.poprawka,
            wersja_ubytkow=a.wersja_ubytkow,
            odstep_ubytku=a.odstep_ubytku,
            krawedz_na_prace=a.krawedz,
            krawedz_rozmiar=a.krawedz_rozmiar,
            krawedz_rozmiary=a.krawedz_rozmiary,
            krawedz_polozenia=a.krawedz_polozenie,
        )
    except ValueError as e:
        ap.error(str(e))
    if a.pamiec_linii is not None:
        KR.ustaw_katalog_pamieci(a.pamiec_linii)
    if a.ile > 0:
        dopisz_mape_projektow(a.mapa if a.mapa is not None else a.wyjscie.resolve().parent / "mapa_projektow.json", projekty)
    for k in range(a.ile):
        seed = a.seed + k
        rng = np.random.default_rng(seed)
        numer = a.numer if a.numer is not None else int(rng.choice(uk.numery))
        nazwa = f"skan_{a.plytka}_n{numer}_s{seed:04d}"
        if not a.nadpisz and any((a.wyjscie / f"{nazwa}{e}").exists() for e in (".stl", ".json")):
            raise SystemExit(f"{a.wyjscie / nazwa}.stl/.json już istnieje; dodaj --nadpisz albo zmień --seed")
        t0 = time.time()
        skan, prawda = generuj_plytke(uk, numer, projekty, rng, opcje, seed)
        p_stl, _ = zapisz(skan, prawda, a.wyjscie, nazwa, nadpisz=a.nadpisz)
        n_ub = sum(len(p.ubytki) for p in prawda.prace)
        n_wyk = sum(u.wykrywalny for p in prawda.prace for u in p.ubytki)
        n_bok = sum(p.ulozenie != "dobrze" for p in prawda.prace)
        n_pok = sum(p.pokrycie < 1.0 for p in prawda.prace)
        n_pop = sum(len(p.poprawki) for p in prawda.prace)
        n_k6 = sum(u.celowy for p in prawda.prace for u in p.ubytki)
        n_k6_pom = sum(p.ukruszenia_pominiete for p in prawda.prace)
        print(
            f"{p_stl.name}: prac {len(prawda.prace)} (pominiętych {len(prawda.pominiete)}), ubytków {n_ub} (wykrywalnych {n_wyk}"
            + (f", celowych na krawędzi {n_k6}, niepostawionych {n_k6_pom}" if opcje.krawedz_na_prace[1] > 0 else "") + "), "
            f"bokiem {n_bok}, częściowych {n_pok}, poprawek {n_pop}, "
            f"trójkątów {len(skan.faces)}, {p_stl.stat().st_size / 1e6:.1f} MB, {time.time() - t0:.1f} s"
        )
    if a.pamiec_linii is not None:
        KR.ustaw_katalog_pamieci(None)


if __name__ == "__main__":
    main()
