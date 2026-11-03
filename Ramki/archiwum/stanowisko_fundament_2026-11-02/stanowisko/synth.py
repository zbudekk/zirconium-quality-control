"""Generator sztucznych skanów płytki (dane syntetyczne do strojenia bez skanera).

Z prawdziwych (albo atrapowych) projektów STL buduje „skan” całej płytki:
projekt powiększony o współczynnik skurczu, obrócony brzegiem do góry,
losowo ułożony w gnieździe, z wyciętymi ubytkami brzegu o znanym położeniu
i rozmiarze, z szumem pomiarowym, na siatce płytki z gniazdami. Obok STL
zapisuje JSON z prawdą (co, gdzie, jaki ubytek), na którym moduły plate,
match i inspect liczą swoje metryki.

Użycie (z katalogu stanowisko/):
    python -m stanowisko.synth --projekty dane/stl --plytka wieczorna --ile 3 --wyjscie dane/syntetyczne
"""
from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import trimesh

from . import uklad as U

TAN_SCIANKI = math.tan(math.radians(U.KAT_SCIANKI_DEG))
MAKS_UNIESIENIE = 1.5  # mm: o tyle praca może wisieć nad dnem gniazda (klin na ściance), więcej = za małe gniazdo


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


@dataclass
class PracaNaPlytce:
    gniazdo: int
    projekt: str  # nazwa pliku STL projektu
    wspolczynnik: float  # skala projekt → praca zielona (1.0 rano)
    transformacja: list  # 4×4: (projekt × wspolczynnik) → układ skanu
    ubytki: list[Ubytek] = field(default_factory=list)
    drgniecie: bool = False  # podwójna powierzchnia (praca przesunęła się w skanie)
    poza_gniazdem: bool = False


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


# ----------------------------------------------------------------------------
# operacje na pojedynczej pracy
# ----------------------------------------------------------------------------
def orientacja_brzegiem_do_gory(m: trimesh.Trimesh) -> np.ndarray:
    """Zwraca macierz 4×4 obracającą pracę tak, by brzeg (otwór) był na górze.

    Heurystyka: wnętrze korony to dodatkowa powierzchnia po stronie brzegu,
    więc środek ciężkości POWIERZCHNI leży bliżej brzegu niż środek obrysu.
    Jeśli brzeg jest na dole (jak w projektach z exocad), obracamy o 180° wokół x.
    """
    srodek_pow = (m.triangles_center * m.area_faces[:, None]).sum(0) / m.area
    srodek_obrysu = m.bounds.mean(0)
    if srodek_pow[2] < srodek_obrysu[2]:
        return trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0])
    return np.eye(4)


def wytnij_ubytek(
    m: trimesh.Trimesh, srednica: float, rng: np.random.Generator, pas_brzegu: float = 2.0
) -> tuple[trimesh.Trimesh, Ubytek]:
    """Wycina kulisty ubytek na brzegu pracy (brzeg = górny pas ``pas_brzegu`` mm).

    Praca musi być już obrócona brzegiem do góry. Siatka jest lokalnie zagęszczona
    do 0,05 mm, trójkąty w kuli usunięte, a w ich miejsce wstawiona „czasza”
    kuli leżąca pod pierwotną powierzchnią — tak wygląda miejsce bez materiału.
    """
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
    c = p + 0.3 * r * n  # środek kuli lekko na zewnątrz: głębokość ubytku 0,7 r

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
    return out, Ubytek(*map(float, p), srednica=float(srednica), glebokosc=float(0.7 * r))


def dodaj_szum(m: trimesh.Trimesh, sigma: float, rng: np.random.Generator) -> trimesh.Trimesh:
    """Szum pomiarowy: przesunięcie wierzchołków wzdłuż normalnych, N(0, sigma)."""
    if sigma <= 0:
        return m
    n = m.vertex_normals
    n = np.where(np.isfinite(n), n, 0.0)
    V = m.vertices + n * rng.normal(0, sigma, (len(m.vertices), 1))
    return trimesh.Trimesh(V, m.faces.copy(), process=False)


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


def osadz_w_gniezdzie(
    m: trimesh.Trimesh, g: U.Gniazdo, rng: np.random.Generator, luz_xy: float = 0.6
) -> np.ndarray | None:
    """Liczy macierz 4×4 układającą pracę (brzegiem do góry, środek xy w 0) w gnieździe.

    Losowy obrót wokół z, lekki przechył, przesunięcie w gnieździe, a wysokość
    tak, by praca oparła się o stożkową ściankę gniazda albo o jego dno.
    Zwraca None, gdy praca nie mieści się w gnieździe.
    """
    if g.okragle:
        jaw = rng.uniform(0, 2 * math.pi)
    else:  # most w rynience leży wzdłuż niej, ewentualnie odwrócony
        jaw = math.radians(g.angle + rng.choice([0.0, 180.0]) + rng.uniform(-1.0, 1.0))
    przechyl = math.radians(rng.uniform(0, 4.0))
    os_przech = np.array([math.cos(rng.uniform(0, 2 * math.pi)), math.sin(rng.uniform(0, 2 * math.pi)), 0])
    R = trimesh.transformations.rotation_matrix(jaw, [0, 0, 1])
    R = trimesh.transformations.rotation_matrix(przechyl, os_przech) @ R
    V = trimesh.transform_points(m.vertices, R)
    V -= [V[:, 0].mean(), V[:, 1].mean(), V[:, 2].min()]  # środek xy w 0, dno na z=0

    z_dno, z_top = g.z_dno, U.Z_TOP
    if g.okragle:
        rho = np.hypot(V[:, 0], V[:, 1])
        rb = g.promien_dolny()
        # najniższa szerokość pracy musi wejść w dno gniazda, inaczej nie mieści się
        if rho[V[:, 2] < 0.5].min(initial=np.inf) > g.promien_gorny:
            return None
        s = z_dno  # start: dno pracy na dnie gniazda
        for _ in range(20):
            z = V[:, 2] + s
            w_gn = z < z_top
            dop = rb + (z - z_dno) * TAN_SCIANKI
            nar = w_gn & (rho > dop)
            if not nar.any():
                break
            s = max(s, ((rho[nar] - rb) / TAN_SCIANKI - V[nar, 2] + z_dno).max())
        if s - z_dno > MAKS_UNIESIENIE:  # praca wisi na krawędzi zamiast siedzieć w gnieździe
            return None
        dx, dy = rng.uniform(-luz_xy, luz_xy, 2) * max(0.0, 1 - (s - z_dno) / g.depth)
    else:
        a = math.radians(g.angle)
        u = V[:, 0] * math.cos(a) + V[:, 1] * math.sin(a)
        v = -V[:, 0] * math.sin(a) + V[:, 1] * math.cos(a)
        if (u.max() - u.min()) > g.l - 1.0 or (v.max() - v.min()) > g.w - 0.4:
            return None
        s = z_dno
        dx = rng.uniform(-1, 1) * max(0.0, (g.l - (u.max() - u.min())) / 2 - 0.5)
        dy = rng.uniform(-1, 1) * max(0.0, (g.w - (v.max() - v.min())) / 2 - 0.5)
    T = trimesh.transformations.translation_matrix([g.x + dx, g.y + dy, s])
    Tc = trimesh.transformations.translation_matrix(
        [-trimesh.transform_points(m.vertices, R)[:, 0].mean(),
         -trimesh.transform_points(m.vertices, R)[:, 1].mean(),
         -trimesh.transform_points(m.vertices, R)[:, 2].min()]
    )
    return T @ Tc @ R


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
    blisko &= c[:, 2] > U.Z_TOP - 3.5  # tylko wierzch (nie kieszenie magnesów)
    Vs, Fs = trimesh.remesh.subdivide_to_size(V, F[blisko], max_edge=0.12)
    F = np.concatenate([F[~blisko], Fs + len(V)])
    V = np.concatenate([V, Vs])
    out = trimesh.Trimesh(V, F, process=False)
    out.merge_vertices()
    # skaner widzi płytkę od góry: spód i kieszenie magnesów usuwamy
    out.update_faces(out.triangles_center[:, 2] > 0.5)
    return dodaj_szum(out, sigma, rng)


# ----------------------------------------------------------------------------
# cała płytka
# ----------------------------------------------------------------------------
@dataclass
class Opcje:
    szum_sigma: float = 0.03
    wspolczynnik: tuple[float, float] = (1.20, 1.25)  # zakres skurczu (wieczór); rano (1.0, 1.0)
    ubytki_na_prace: tuple[int, int] = (0, 2)
    srednica_ubytku: tuple[float, float] = (0.2, 0.6)
    p_drgniecia: float = 0.0
    prace_na_plytce: int | None = None  # None = ile się zmieści z puli
    mosty: bool = True


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
    kolejnosc = list(rng.permutation(len(projekty)))
    limit = opcje.prace_na_plytce if opcje.prace_na_plytce is not None else len(projekty)

    for i in kolejnosc:
        if len(prace) >= limit:
            break
        plik = projekty[i]
        m = trimesh.load(plik, force="mesh")
        w = float(rng.uniform(*opcje.wspolczynnik))
        S = trimesh.transformations.scale_matrix(w)
        O = orientacja_brzegiem_do_gory(m)
        m2 = m.copy()
        m2.apply_transform(O @ S)

        szer = max(m2.extents[0], m2.extents[1])
        most = szer > 20.0
        kand = wolne_rynienki if most else sorted(wolne_okragle, key=lambda g: g.d_top)
        if most and not opcje.mosty:
            continue
        T = None
        g_wyb = None
        for g in kand:
            if g.okragle and g.d_top < szer * 0.55:  # za małe na pewno
                continue
            T = osadz_w_gniezdzie(m2, g, rng)
            if T is not None:
                g_wyb = g
                break
        if T is None:
            continue
        (wolne_rynienki if most else wolne_okragle).remove(g_wyb)

        m3 = m2.copy()
        m3.apply_transform(T)
        ubytki = []
        for _ in range(int(rng.integers(opcje.ubytki_na_prace[0], opcje.ubytki_na_prace[1] + 1))):
            m3, ub = wytnij_ubytek(m3, float(rng.uniform(*opcje.srednica_ubytku)), rng)
            ubytki.append(ub)
        drg = bool(rng.uniform() < opcje.p_drgniecia)
        m3 = dodaj_szum(m3, opcje.szum_sigma, rng)
        if drg:
            m3 = drgniecie(m3, rng)
        czesci.append(m3)
        prace.append(
            PracaNaPlytce(
                gniazdo=g_wyb.id,
                projekt=plik.name,
                wspolczynnik=w,
                transformacja=(T @ O).tolist(),
                ubytki=ubytki,
                drgniecie=drg,
            )
        )

    zajete = {p.gniazdo for p in prace}
    prawda = PrawdaPlytki(
        plytka=uk.nazwa,
        numer=numer,
        seed=seed,
        szum_sigma=opcje.szum_sigma,
        z_top=U.Z_TOP,
        prace=prace,
        gniazda_puste=[g.id for g in uk.sockets if g.id not in zajete],
    )
    return trimesh.util.concatenate(czesci), prawda


def zapisz(skan: trimesh.Trimesh, prawda: PrawdaPlytki, wyjscie: Path, nazwa: str) -> tuple[Path, Path]:
    wyjscie.mkdir(parents=True, exist_ok=True)
    p_stl = wyjscie / f"{nazwa}.stl"
    p_json = wyjscie / f"{nazwa}.json"
    skan.export(p_stl)
    prawda.plik_stl = p_stl.name
    p_json.write_text(json.dumps(asdict(prawda), ensure_ascii=False, indent=1), encoding="utf-8")
    return p_stl, p_json


def wczytaj_prawde(p_json: Path) -> PrawdaPlytki:
    d = json.loads(p_json.read_text(encoding="utf-8"))
    prace = [
        PracaNaPlytce(**{**p, "ubytki": [Ubytek(**u) for u in p["ubytki"]]}) for p in d.pop("prace")
    ]
    return PrawdaPlytki(prace=prace, **d)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--projekty", type=Path, default=Path("dane/stl"), help="folder z STL projektów")
    ap.add_argument("--plytka", choices=["wieczorna", "poranna"], default="wieczorna")
    ap.add_argument("--numer", type=int, default=None, help="numer płytki (domyślnie losowy z dostępnych)")
    ap.add_argument("--ile", type=int, default=1, help="ile płytek wygenerować")
    ap.add_argument("--prace", type=int, default=None, help="ile prac na płytce (domyślnie: ile wejdzie)")
    ap.add_argument("--szum", type=float, default=0.03)
    ap.add_argument("--ubytki", type=str, default="0-2", help="zakres ubytków na pracę, np. 0-2")
    ap.add_argument("--srednica", type=str, default="0.2-0.6", help="zakres średnic ubytków [mm]")
    ap.add_argument("--drgniecie", type=float, default=0.0, help="prawdopodobieństwo podwójnej powierzchni")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--wyjscie", type=Path, default=Path("dane/syntetyczne"))
    a = ap.parse_args()

    uk = U.wczytaj(a.plytka)
    projekty = sorted(a.projekty.glob("*.stl"))
    if not projekty:
        raise SystemExit(f"brak plików STL w {a.projekty}; uruchom narzedzia/atrapy_koron.py")
    u0, u1 = (int(x) for x in a.ubytki.split("-"))
    s0, s1 = (float(x) for x in a.srednica.split("-"))
    opcje = Opcje(
        szum_sigma=a.szum,
        wspolczynnik=(1.0, 1.0) if a.plytka == "poranna" else (1.20, 1.25),
        ubytki_na_prace=(u0, u1),
        srednica_ubytku=(s0, s1),
        p_drgniecia=a.drgniecie,
        prace_na_plytce=a.prace,
    )
    for k in range(a.ile):
        seed = a.seed + k
        rng = np.random.default_rng(seed)
        numer = a.numer if a.numer is not None else int(rng.choice(uk.numery))
        t0 = time.time()
        skan, prawda = generuj_plytke(uk, numer, projekty, rng, opcje, seed)
        nazwa = f"skan_{a.plytka}_n{numer}_s{seed:04d}"
        p_stl, _ = zapisz(skan, prawda, a.wyjscie, nazwa)
        n_ub = sum(len(p.ubytki) for p in prawda.prace)
        print(
            f"{p_stl.name}: prac {len(prawda.prace)}, ubytków {n_ub}, "
            f"trójkątów {len(skan.faces)}, {p_stl.stat().st_size / 1e6:.1f} MB, {time.time() - t0:.1f} s"
        )


if __name__ == "__main__":
    main()
