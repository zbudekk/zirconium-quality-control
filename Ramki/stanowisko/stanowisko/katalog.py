"""Katalog projektów STL: cechy każdego pliku bez jego nazwy (nazwy niosą nazwiska pacjentów).

Identyfikator projektu = pierwsze 16 znaków SHA‑256 zawartości pliku (``synth.skrot_pliku``),
ten sam, który generator zapisuje w prawdzie. Do katalogu (``dane/katalog.json``) trafiają
tylko: identyfikator, numery zębów z nazwy pliku, typ pracy, objętość, wymiary, liczba
trójkątów, szczelność, strona brzegu, w jakie gniazdo wchodzi. Mapowanie identyfikator → ścieżka
pliku leży osobno w ``dane/mapa_sciezek.json`` (poza repozytorium) i służy tylko modułowi
match do wczytania siatki.

Nazwy plików z exocad: ``<data>_<zlecenie/pacjent>-<ząb>[-<ząb>…]-<typ>_cad.stl``,
typ ∈ crown | bridge | waxup | waxup_slm | tooth_without_abutment.
"""
from __future__ import annotations

import json
import re
import time
import warnings
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import trimesh

from . import synth as S
from . import uklad as U

WZOR_NAZWY = re.compile(r"-(\d{2}(?:-\d{2})*)-(crown|bridge|waxup|tooth_without_abutment)(?:_slm)?(?:_cad)?\.stl$", re.IGNORECASE)
TYPY = {"crown": "korona", "bridge": "most", "waxup": "waxup", "tooth_without_abutment": "bez_lacznika"}
TYP_NIEZNANY = "nieznany"
WERSJA_KATALOGU = 1


@dataclass
class Projekt:
    id: str  # 16 znaków SHA-256 pliku
    zeby: list[str]  # numery zębów z nazwy (FDI), [] gdy nazwa nie pasuje do wzoru exocad
    typ: str  # korona | most | waxup | bez_lacznika | nieznany
    trojkaty: int
    szczelna: bool
    objetosc_mm3: float  # z siatki (dla nieszczelnej: przybliżona, znak może być ujemny → wartość bezwzględna)
    pole_mm2: float
    bbox_mm: list[float]  # wymiary prostopadłościanu w układzie pliku (x, y, z)
    obrys_xy_mm: list[float]  # prostokąt obrysu xy o najmniejszym polu (krótszy, dłuższy bok) po obrocie brzegiem do góry
    wysokosc_mm: float
    hull_mm3: float  # objętość otoczki wypukłej (cecha do filtru match; mierzalna też na częściowym skanie)
    brzeg: str  # dol | gora | niejasny — gdzie w pliku jest brzeg wg heurystyki krawędzi (synth.brzeg_z_heurystyki)
    krawedzie_brzegu_mm: list[float]  # długość krawędzi brzegu w dolnym i górnym pasie
    exocad: bool = False  # plik ``…_cad.stl``: orientacja z konwencji eksportu (brzeg na dole), nie z heurystyki
    gniazdo: dict = field(default_factory=dict)  # płytka → opis gniazda, w które projekt wchodzi (None = nie mieści się)


def typ_i_zeby_z_nazwy(nazwa: str) -> tuple[str, list[str]]:
    """Typ pracy i numery zębów z nazwy pliku exocad; (nieznany, []) gdy wzór nie pasuje."""
    m = WZOR_NAZWY.search(nazwa)
    if m is None:
        return TYP_NIEZNANY, []
    return TYPY[m.group(2).lower()], m.group(1).split("-")


def cechy(m: trimesh.Trimesh, nazwa: str = "") -> Projekt:
    """Cechy siatki projektu (bez ścieżki); ``id`` uzupełnia wywołujący."""
    typ, zeby = typ_i_zeby_z_nazwy(nazwa)
    dol, gora = S.strona_brzegu(m)
    brzeg = S.brzeg_z_heurystyki(m)
    m2 = m.copy()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # niejasna heurystyka: katalog zapisuje „niejasny”, nie ostrzega
        m2.apply_transform(S.orientacja_brzegiem_do_gory(m, "auto", nazwa))
    _, boki = trimesh.bounds.oriented_bounds_2D(m2.vertices[:, :2])
    return Projekt(
        id="",
        zeby=zeby,
        typ=typ,
        trojkaty=int(len(m.faces)),
        szczelna=bool(m.is_watertight),
        objetosc_mm3=float(abs(m.volume)),
        pole_mm2=float(m.area),
        bbox_mm=[float(v) for v in m.extents],
        obrys_xy_mm=[float(v) for v in sorted(boki)],
        wysokosc_mm=float(m2.extents[2]),
        hull_mm3=float(m.convex_hull.volume),
        brzeg=brzeg,
        krawedzie_brzegu_mm=[round(dol, 2), round(gora, 2)],
        exocad=S.plik_exocad(nazwa),
    )


def gniazdo_dla(m: trimesh.Trimesh, uk: U.UkladPlytki, wspolczynnik: float, orientacja: str = "auto", nazwa: str = "") -> dict | None:
    """W jakie gniazdo płytki ``uk`` wchodzi projekt × ``wspolczynnik`` (ta sama procedura co generator, seed 0).

    Zwraca ``{"typ": "round"|"trough", "d_top"|"l": …}`` najmniejszego pasującego gniazda albo None z powodem.
    """
    m2 = m.copy()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        O = S.orientacja_brzegiem_do_gory(m, orientacja, nazwa)
    m2.apply_transform(O @ trimesh.transformations.scale_matrix(wspolczynnik))
    widziane = set()
    for g in S.kandydaci_gniazd(m2, uk.gniazda_okragle(), uk.rynienki()):
        klucz = (g.typ, g.d_top if g.okragle else (g.l, g.w))
        if klucz in widziane:
            continue
        widziane.add(klucz)
        if S.osadz_w_gniezdzie(m2, g, np.random.default_rng(0)) is not None:
            return {"typ": g.typ, "d_top": g.d_top} if g.okragle else {"typ": g.typ, "l": g.l, "w": g.w}
    _, boki = trimesh.bounds.oriented_bounds_2D(m2.vertices[:, :2])
    return {"typ": None, "powod": f"praca {boki.max():.1f} × {boki.min():.1f} mm (×{wspolczynnik}) nie mieści się w żadnym gnieździe"}


def zbuduj(folder: Path, plytki: dict[str, tuple[U.UkladPlytki, float]] | None = None, orientacja: str = "auto") -> tuple[dict, dict[str, str]]:
    """Katalog folderu projektów: (``katalog`` do JSON, ``mapa`` id → ścieżka).

    ``plytki``: nazwa → (układ, współczynnik) — dla każdej sprawdza, w jakie gniazdo projekt wchodzi.
    """
    folder = Path(folder)
    t0 = time.time()
    projekty, mapa, pominiete = [], {}, []
    for p in S.pliki_projektow(folder):
        m = S.wczytaj_projekt(p)
        if m is None:
            pominiete.append(str(p.relative_to(folder)))
            continue
        c = cechy(m, p.name)
        c.id = S.skrot_pliku(p)
        for nazwa, (uk, w) in (plytki or {}).items():
            c.gniazdo[nazwa] = gniazdo_dla(m, uk, w, orientacja, p.name)
        projekty.append(c)
        mapa[c.id] = str(p.resolve())
    katalog = {
        "wersja": WERSJA_KATALOGU,
        "liczba": len(projekty),
        "czas_s": round(time.time() - t0, 1),
        "plytki": {n: w for n, (_, w) in (plytki or {}).items()},
        "pominiete": len(pominiete),  # liczba, bez nazw
        "projekty": [asdict(c) for c in projekty],
    }
    return katalog, mapa


def wczytaj(plik: Path) -> dict[str, Projekt]:
    """Katalog z JSON jako słownik id → Projekt."""
    d = json.loads(Path(plik).read_text(encoding="utf-8"))
    return {e["id"]: Projekt(**e) for e in d["projekty"]}


def zapisz(katalog: dict, mapa: dict[str, str], plik_katalogu: Path, plik_mapy: Path) -> None:
    plik_katalogu = Path(plik_katalogu)
    plik_mapy = Path(plik_mapy)
    plik_katalogu.parent.mkdir(parents=True, exist_ok=True)
    plik_mapy.parent.mkdir(parents=True, exist_ok=True)
    plik_katalogu.write_text(json.dumps(katalog, ensure_ascii=False, indent=1), encoding="utf-8")
    plik_mapy.write_text(json.dumps(mapa, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")


def streszczenie(katalog: dict) -> str:
    """Tabela tekstowa katalogu (bez nazw plików)."""
    w = ["id               typ           zęby          tri     szcz  obj[mm³]  obrys xy [mm]   h[mm]  brzeg(heur.) exocad  " + "  ".join(katalog.get("plytki", {}))]
    for e in katalog["projekty"]:
        gn = []
        for n in katalog.get("plytki", {}):
            g = e["gniazdo"].get(n)
            gn.append("—" if g is None or g.get("typ") is None else (f"ø{g['d_top']}" if g["typ"] == "round" else f"ryn{g['l']:.0f}"))
        w.append(
            f"{e['id']} {e['typ']:13s} {'-'.join(e['zeby']):13s} {e['trojkaty']:6d}  {'tak' if e['szczelna'] else 'NIE':4s} "
            f"{e['objetosc_mm3']:8.1f}  {e['obrys_xy_mm'][1]:5.1f} × {e['obrys_xy_mm'][0]:4.1f}  {e['wysokosc_mm']:5.1f}  {e['brzeg']:12s} {'tak' if e['exocad'] else 'nie':6s}  "
            + "  ".join(f"{g:>{max(len(n), 5)}}" for g, n in zip(gn, katalog.get("plytki", {})))
        )
    return "\n".join(w)
