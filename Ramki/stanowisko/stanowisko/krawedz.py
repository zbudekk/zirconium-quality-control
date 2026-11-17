"""krawedz - linie krawedzi brzegu kazdego filaru projektu (z siatki STL projektu).

Korona pojedyncza: 1 petla; most / praca wieloczlonowa: petla na kazdy filar (przesla nie maja brzegu);
korona implantowa bez lacznika: obwod powierzchni przylegania (styk z Ti-base, kanal sruby) - decyzja
wlasciciela 06.11.2026: liczy sie jako krawedz brzegu.

Wejscie: siatka projektu brzegiem do gory (os z = os wprowadzenia, wspolna dla calej pracy - eksport exocad),
czyli tak jak ``match.Projekt.siatka`` i praca w ``synth`` przed ulozeniem w gniezdzie.
Wyjscie: ``LinieProjektu`` - lista filarow, a dla kazdego: linia naroznika zewnetrznego plaskiej krawedzi (O),
wewnetrznego (I) i srodka plaskiej krawedzi lezacego NA powierzchni (S), ze znacznikiem ``zweryf`` na kazdej
stacji / przekroju oraz miarami wiarygodnosci. Gdy linii nie da sie wyznaczyc wiarygodnie, wynik mowi to jawnie
(``werdykt`` filaru: ``wiarygodna`` | ``czesciowa`` | ``niepewna``; brak filarow = ``stan`` ``brak``; filar z przyjeta
niecka, dla ktorego linii nie wyznaczono = numer w ``filary_bez_linii`` i ``stan`` ``czesciowe``) - modul
niczego nie zgaduje, a odcinki niezweryfikowane sa oznaczone, nie usuniete.

Metoda (przeniesiona z prototypu sesji testowej T9, 06.11.2026, bez zmiany konstrukcji i stalych):
1. mapa wysokosci z gory (promienie w dol, piksel 0,05 mm); filary = niecki mapy (wneka filaru albo kanal sruby)
   po wypelnieniu niecek od ramki obrazu ("priority flood"); przesla nie maja niecki;
2. obszar filaru = dzial wodny ze znacznikami (zalewanie Meyera): granica biegnie po grzbiecie brzegu;
3. przekroje promieniowe wokol srodka wneki co 0,5 st.; w kazdym naroznik zewnetrzny O i wewnetrzny I plaskiej
   krawedzi (lamana przekroju od wezla startowego w obie strony, do odchylenia normalnej o 25 st.);
   start wskazany na dwa niezalezne sposoby: wariant 1 - najwyzszy wezel przy granicy obszaru z dzialu wodnego,
   wariant 2 - wezel najblizszy koncowi sciany wneki, wariant 3 - przekroje, w ktorych 1 i 2 sa zgodne do 0,10 mm,
   a spory rozstrzyga gladka krzywa (odporny szereg Fouriera);
4. wybor wariantu na filar (przerwa linii O <= 5 st. i skok surowej linii O <= 0,6 mm; kolejnosc 3, 1, 2);
5. weryfikacja kazdego przekroju: przekroj udany, co najmniej dwa niezalezne wyznaczenia punktu O zgodne do
   0,10 mm (wariant 1, wariant 2, a dla pracy z jednym filarem takze linia "T3": os w srodku obrysu, start w
   najwyzszym wezle przekroju), szerokosc plaskiej krawedzi O-I 0,10-1,50 mm.

Stale ponizej sa w milimetrach pracy w skali odniesienia ``SKALA_ODNIESIENIA`` (projekt x 1,22 - warunki, w
ktorych metoda byla sprawdzana na 17 projektach). ``linie_siatki`` przelicza dowolna skale na skale odniesienia,
liczy linie raz na projekt (pamiec podreczna w module, opcjonalnie takze na dysku) i zwraca je w ukladzie siatki
wejsciowej. Modul nie zalezy od ``match`` ani od plikow spoza repozytorium.
"""
from __future__ import annotations

import heapq
import json
import math
import os
import time
import warnings
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import open3d as o3d
import trimesh
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

WERSJA = 1  # wersja algorytmu: zmiana konstrukcji albo stalych = nowy numer (klucz pamieci podrecznej na dysku)
SKALA_ODNIESIENIA = 1.22  # linie liczone na projekcie x 1,22 (praca zielona), wynik przeliczany na skale wywolania

# --- filary z mapy wysokosci ---------------------------------------------------------------------------
PIKSEL = 0.05  # mm: piksel mapy wysokosci z gory
ZAPAS_MAPY = 1.0  # mm: margines mapy wokol obrysu pracy
GLEB_RDZENIA = 0.3  # mm: piksel niecki = lezy o tyle pod poziomem wypelnienia
POLE_MIN = 2.0  # mm2: najmniejsza niecka filaru
GLEB_MAX_MIN = 1.0  # mm: niecka filaru ma gdzies co najmniej tyle glebokosci
# --- przekroje i narozniki (jak prototyp T3 / T9) -------------------------------------------------------
KROK_KATA_DEG = 0.5  # przekroje promieniowe (polplaszczyzny zawierajace os filaru) co tyle
R_MIN_PRZEKROJU = 0.2  # mm: odcinki przekroju blizej osi sa pomijane
COS_GORA = 0.64  # odcinek "plaskiej krawedzi": normalna 2D w granicach ok. 50 st. od +z
ANG_ROG_DEG = 25.0  # koniec plaskiej krawedzi: normalna odchylona o tyle od sredniej normalnej krawedzi
DL_SCIANY = 0.10  # mm: odcinek sciany za naroznikiem (normalna sciany, linie O2 / I2)
W_NZ, W_DZ = 0.7, 0.1  # linia W: najdalej do srodka punkt skierowany do gory (nz > 0,7) do 0,1 mm pod szczytem
DROGA_MAX = 2.0  # mm: najdluzsza droga po lamanej przekroju od wezla startowego
OKNO_STARTU = 0.6  # mm: wezel startowy przekroju w tym promieniu od grzbietu / konca sciany
ODST_GRZBIETU = 0.4  # mm: grzbiet dalej od gladkiej krzywej (Fourier rzedu 8) = zastapiony krzywa
ODST_O = 0.25  # mm: punkt O dalej od gladkiej krzywej (Fourier rzedu 16) = przekroj odrzucony
ZGODA_MM = 0.10  # mm: dwa wyznaczenia punktu O blizej niz tyle = zgodne
ZGODNYCH_MIN = 40  # wariant 3: mniej zgodnych przekrojow = wariant 1 bez potwierdzenia
MED_OKNO = 4  # filtr medianowy po przekrojach (+- tyle przekrojow)
ODST_MED = 0.15  # mm: przekroj odstajacy od mediany sasiadow o tyle = nieudany dla tej linii
KROK_STACJI = 0.05  # mm: stacje wzdluz linii
ZAPAS_PODSIATKI_R = 3.0  # mm: podsiatka filaru = trojkaty do tylu poza najwiekszym promieniem grzbietu
ZAPAS_PODSIATKI_Z = 4.0  # mm: ... i nie nizej niz tyle pod najnizszym punktem grzbietu (droga po przekroju <= 2,1 mm)
# --- wybor wariantu i weryfikacja ------------------------------------------------------------------------
PRZERWA_DOBRA_ST = 5.0  # wariant "dobry": najdluzsza przerwa linii O <= tyle stopni ...
SKOK_DOBRY_MM = 0.6  # ... i najwiekszy skok surowej linii O miedzy kolejnymi przekrojami <= tyle
SZER_MIN, SZER_MAX = 0.10, 1.50  # mm: dopuszczalna szerokosc plaskiej krawedzi O-I w zweryfikowanym przekroju
UDZIAL_WIARYGODNA = 0.9  # petla wiarygodna: >= tyle przekrojow zweryfikowanych ...
CIAG_WIARYGODNA_ST = 10.0  # ... i najdluzszy ciag niezweryfikowanych <= tyle stopni
UDZIAL_CZESCIOWA = 0.6  # petla czesciowa: >= tyle przekrojow zweryfikowanych; mniej = niepewna
WERDYKTY = ("wiarygodna", "czesciowa", "niepewna")
NAZWY_LINII = ("O", "I", "S")


# ----------------------------------------------------------------------------
# wynik
# ----------------------------------------------------------------------------
@dataclass
class Linia:
    """Zamknieta lamana ze stacjami co ok. ``KROK_STACJI`` (w skali odniesienia)."""

    X: np.ndarray  # (K, 3) punkty stacji
    zweryf: np.ndarray  # (K,) bool: stacja lezy na zweryfikowanym przekroju
    przekroj: np.ndarray  # (K,) float: numer przekroju (kata) stacji
    dlugosc: float  # dlugosc petli [mm]

    @property
    def krok(self) -> float:
        return self.dlugosc / max(1, len(self.X))


@dataclass
class Filar:
    """Jeden czlon pracy z brzegiem: linie O / I / S i miary wiarygodnosci."""

    nr: int
    srodek: tuple[float, float]  # (x, y) osi przekrojow = srodek wneki
    wariant: str  # 1 | 2 | 3 - wybrany sposob wskazania startu przekroju
    wybor_pewny: bool  # wybrany wariant spelnia kryterium "dobry"
    werdykt: str  # WERDYKTY
    udzial_zweryf: float  # udzial przekrojow zweryfikowanych
    najdl_ciag_st: float  # najdluzszy ciag przekrojow niezweryfikowanych [st.]
    najdl_przerwa_mm: float  # to samo wzdluz linii O [mm]
    linie: dict[str, Linia]  # "O", "I", "S"
    katy: np.ndarray  # (N,) katy przekrojow [rad]
    O: np.ndarray  # (N, 3) naroznik zewnetrzny w przekroju (po filtrze i interpolacji)
    I: np.ndarray  # (N, 3) naroznik wewnetrzny
    S: np.ndarray  # (N, 3) srodek plaskiej krawedzi zrzutowany na powierzchnie projektu
    udany: np.ndarray  # (N,) bool: przekroj wyznaczony (nie interpolowany)
    zweryf: np.ndarray  # (N,) bool: przekroj zweryfikowany
    kontrola: dict = field(default_factory=dict)  # miary pomocnicze (liczniki)

    @property
    def dlugosc(self) -> float:
        return self.linie["O"].dlugosc

    @property
    def z_min_max(self) -> tuple[float, float]:
        z = self.linie["O"].X[:, 2]
        return float(z.min()), float(z.max())


@dataclass
class LinieProjektu:
    filary: list[Filar]
    niecki: list[dict] = field(default_factory=list)
    uwagi: list[str] = field(default_factory=list)
    czas_s: float = 0.0
    skala: float = SKALA_ODNIESIENIA  # skala, w ktorej podane sa wspolrzedne (wzgledem pliku projektu)

    @property
    def filary_bez_linii(self) -> list[int]:
        """Numery filarow, ktorych niecka (wneka albo kanal sruby) zostala przyjeta, ale linii nie wyznaczono - nie ma
        ich na liscie ``filary`` (w ``uwagi`` jest wtedy wpis "linii nie wyznaczono"). Liczone z ``niecki``."""
        z_linia = {f.nr for f in self.filary}
        return sorted({int(d["filar"]) for d in self.niecki if d.get("przyjeta") and d.get("filar") is not None} - z_linia)

    @property
    def stan(self) -> str:
        """``wiarygodne`` (kazdy filar ma linie i jest wiarygodny) | ``czesciowe`` | ``brak`` (zadnego filaru z linia)."""
        if not self.filary:
            return "brak"
        return "wiarygodne" if all(f.werdykt == "wiarygodna" for f in self.filary) and not self.filary_bez_linii else "czesciowe"

    def przeksztalc(self, k: float, przesuniecie=(0.0, 0.0, 0.0)) -> LinieProjektu:
        """Kopia w ukladzie x' = k * x + przesuniecie (dlugosci x k)."""
        t = np.asarray(przesuniecie, dtype=np.float64)
        filary = []
        for f in self.filary:
            linie = {n: Linia(L.X * k + t, L.zweryf.copy(), L.przekroj.copy(), L.dlugosc * k) for n, L in f.linie.items()}
            filary.append(Filar(f.nr, (f.srodek[0] * k + t[0], f.srodek[1] * k + t[1]), f.wariant, f.wybor_pewny, f.werdykt, f.udzial_zweryf,
                                f.najdl_ciag_st, f.najdl_przerwa_mm * k, linie, f.katy.copy(), f.O * k + t, f.I * k + t, f.S * k + t,
                                f.udany.copy(), f.zweryf.copy(), dict(f.kontrola)))
        return LinieProjektu(filary, [dict(n) for n in self.niecki], list(self.uwagi), self.czas_s, self.skala * k)

    def opis(self) -> dict:
        """Liczniki do raportu / JSON (bez tablic)."""
        return {"stan": self.stan, "filarow": len(self.filary), "filary_bez_linii": self.filary_bez_linii, "uwagi": list(self.uwagi), "czas_s": self.czas_s,
                "filary": [{"nr": f.nr, "wariant": f.wariant, "wybor_pewny": f.wybor_pewny, "werdykt": f.werdykt,
                            "przekroje_zweryfikowane": int(f.zweryf.sum()), "przekroje": int(len(f.zweryf)),
                            "udzial_zweryf": round(f.udzial_zweryf, 4), "najdl_ciag_st": round(f.najdl_ciag_st, 1),
                            "najdl_przerwa_mm": round(f.najdl_przerwa_mm, 2), "dlugosc_O_mm": round(f.dlugosc, 2),
                            "dlugosc_O_zweryf_mm": round(float(f.linie["O"].zweryf.mean()) * f.dlugosc, 2),
                            "z_O_min_max": [round(v, 2) for v in f.z_min_max], "srodek": [round(v, 2) for v in f.srodek],
                            **f.kontrola} for f in self.filary]}


# ----------------------------------------------------------------------------
# mapa wysokosci, niecki, dzial wodny
# ----------------------------------------------------------------------------
def scena_siatki(m: trimesh.Trimesh) -> o3d.t.geometry.RaycastingScene:
    mo = o3d.t.geometry.TriangleMesh(o3d.core.Tensor(np.asarray(m.vertices, dtype=np.float32)), o3d.core.Tensor(np.asarray(m.faces, dtype=np.int32)))
    scena = o3d.t.geometry.RaycastingScene()
    scena.add_triangles(mo)
    return scena


def mapa_wysokosci(m: trimesh.Trimesh, scena, piksel: float = PIKSEL, zapas: float = ZAPAS_MAPY):
    """Mapa wysokosci z gory: (xs, ys, Z[iy, ix] - NaN bez trafienia, F[iy, ix] - numer trojkata albo -1)."""
    (x0, y0, _), (x1, y1, z1) = m.bounds
    xs = np.arange(x0 - zapas, x1 + zapas, piksel)
    ys = np.arange(y0 - zapas, y1 + zapas, piksel)
    X, Y = np.meshgrid(xs, ys)
    ray = np.zeros((X.size, 6), dtype=np.float32)
    ray[:, 0], ray[:, 1], ray[:, 2] = X.ravel(), Y.ravel(), z1 + 5.0
    ray[:, 5] = -1.0
    r = scena.cast_rays(o3d.core.Tensor(ray))
    t = r["t_hit"].numpy()
    fid = r["primitive_ids"].numpy().astype(np.int64)
    Z = np.where(np.isfinite(t), z1 + 5.0 - t, np.nan).reshape(X.shape)
    F = np.where(np.isfinite(t), fid, -1).reshape(X.shape)
    return xs, ys, Z, F


def wypelnij_niecki(Z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Wypelnienie niecek od ramki obrazu ("priority flood"); brak trafienia = bardzo nisko (tlo).

    Zwraca (mapa wypelniona, mapa z NaN zastapionym poziomem tla)."""
    H, W = Z.shape
    zlo = np.nanmin(Z) - 1.0
    Zf = np.where(np.isnan(Z), zlo, Z)
    flat = Zf.ravel().tolist()
    F = [0.0] * (H * W)
    done = bytearray(H * W)
    hp = []
    for iy in range(H):
        for ix in (0, W - 1):
            i = iy * W + ix
            if not done[i]:
                done[i] = 1
                F[i] = flat[i]
                hp.append((flat[i], i))
    for ix in range(W):
        for iy in (0, H - 1):
            i = iy * W + ix
            if not done[i]:
                done[i] = 1
                F[i] = flat[i]
                hp.append((flat[i], i))
    heapq.heapify(hp)
    pop, push = heapq.heappop, heapq.heappush
    while hp:
        v, i = pop(hp)
        iy, ix = divmod(i, W)
        if iy > 0:
            j = i - W
            if not done[j]:
                done[j] = 1
                f = flat[j] if flat[j] > v else v
                F[j] = f
                push(hp, (f, j))
        if iy < H - 1:
            j = i + W
            if not done[j]:
                done[j] = 1
                f = flat[j] if flat[j] > v else v
                F[j] = f
                push(hp, (f, j))
        if ix > 0:
            j = i - 1
            if not done[j]:
                done[j] = 1
                f = flat[j] if flat[j] > v else v
                F[j] = f
                push(hp, (f, j))
        if ix < W - 1:
            j = i + 1
            if not done[j]:
                done[j] = 1
                f = flat[j] if flat[j] > v else v
                F[j] = f
                push(hp, (f, j))
    return np.asarray(F, dtype=np.float64).reshape(H, W), Zf


_SASIEDZI8 = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))


def zalewanie_meyer(Zf: np.ndarray, znacz: np.ndarray) -> np.ndarray:
    """Dzial wodny przez zalewanie (Meyer): kolejka priorytetowa wg wysokosci piksela; piksel dostaje etykiete
    sasiada, ktory go pierwszy wstawil. (``scipy.ndimage.watershed_ift`` z kosztem "max na sciezce" daje remisy na
    scianach wneki powyzej poziomu przelewu i zalewal cala prace - odrzucone w T9.)"""
    H, W = Zf.shape
    flat = Zf.ravel().tolist()
    lab = znacz.ravel().astype(np.int64).tolist()
    wst = bytearray(1 if v > 0 else 0 for v in lab)
    hp = []
    licz = 0
    iy0, ix0 = np.nonzero(znacz > 0)
    for iy, ix in zip(iy0.tolist(), ix0.tolist()):  # tylko piksele na brzegu znacznika wstawiaja sasiadow
        e = lab[iy * W + ix]
        for dy, dx in _SASIEDZI8:
            jy, jx = iy + dy, ix + dx
            if 0 <= jy < H and 0 <= jx < W:
                j = jy * W + jx
                if not wst[j]:
                    wst[j] = 1
                    licz += 1
                    hp.append((flat[j], licz, j, e))
    heapq.heapify(hp)
    pop, push = heapq.heappop, heapq.heappush
    while hp:
        _, _, i, e = pop(hp)
        lab[i] = e
        iy, ix = divmod(i, W)
        for dy, dx in _SASIEDZI8:
            jy, jx = iy + dy, ix + dx
            if 0 <= jy < H and 0 <= jx < W:
                j = jy * W + jx
                if not wst[j]:
                    wst[j] = 1
                    licz += 1
                    push(hp, (flat[j], licz, j, e))
    return np.asarray(lab, dtype=np.int32).reshape(H, W)


def obszary_filarow(Z: np.ndarray, piksel: float = PIKSEL):
    """Znaczniki niecek i dzial wodny. Zwraca (etykiety: 0 tlo, 1..k filary; opis niecek; k; glebokosc niecek)."""
    Fw, Zf = wypelnij_niecki(Z)
    gl = Fw - Zf
    rdzen = gl > GLEB_RDZENIA
    lab, n = ndi.label(rdzen, structure=np.ones((3, 3)))
    niecki = []
    for k in range(1, n + 1):
        w = lab == k
        pole = float(w.sum()) * piksel**2
        gmax = float(gl[w].max())
        niecki.append({"etykieta": k, "pole_mm2": round(pole, 2), "gleb_max": round(gmax, 2),
                       "przyjeta": bool(pole >= POLE_MIN and gmax >= GLEB_MAX_MIN)})
    znacz = np.zeros(Z.shape, dtype=np.int32)
    nr = 0
    for d in niecki:
        if d["przyjeta"]:
            nr += 1
            znacz[lab == d["etykieta"]] = nr
            d["filar"] = nr
    if nr == 0:
        return np.zeros(Z.shape, dtype=np.int32), niecki, 0, gl
    brak = np.isnan(Z)  # tlo: brak trafienia polaczony z ramka obrazu
    lb, _ = ndi.label(brak)
    ramka = set(np.unique(np.concatenate([lb[0], lb[-1], lb[:, 0], lb[:, -1]])).tolist()) - {0}
    znacz[np.isin(lb, list(ramka))] = nr + 1
    ws = zalewanie_meyer(Zf, znacz)
    ws = np.where(ws == nr + 1, 0, ws)
    return ws, niecki, nr, gl


# ----------------------------------------------------------------------------
# grzbiet brzegu i koniec sciany wneki (dwa niezalezne wskazania startu przekroju)
# ----------------------------------------------------------------------------
def _promien(c, th: float, rr: np.ndarray, xs, ys, piksel: float, ksztalt):
    H, W = ksztalt
    x = c[0] + rr * math.cos(th)
    y = c[1] + rr * math.sin(th)
    ix = np.round((x - xs[0]) / piksel).astype(int)
    iy = np.round((y - ys[0]) / piksel).astype(int)
    ok = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
    return np.where(ok, ix, 0), np.where(ok, iy, 0), ok


def grzbiet(ws, k: int, xs, ys, Z, c, katy, rmax: float = 20.0, krok: float = 0.025, piksel: float = PIKSEL):
    """Wariant 1: dla kazdego kata promien wyjscia z obszaru filaru ``k`` i najwyzszy punkt mapy w +-0,3 mm wokol
    wyjscia (grzbiet brzegu); ``wej`` = liczba ponownych wejsc w obszar dalej na promieniu."""
    rr = np.arange(0.0, rmax, krok)
    rb = np.full(len(katy), np.nan)
    zb = np.full(len(katy), np.nan)
    wej = np.zeros(len(katy), dtype=int)
    for i, th in enumerate(katy):
        ix, iy, ok = _promien(c, th, rr, xs, ys, piksel, ws.shape)
        w = ok & (ws[iy, ix] == k)
        if not w[0]:
            continue
        j = int(np.argmin(w))  # pierwszy piksel poza obszarem
        if j == 0:
            continue
        rb[i] = rr[j]
        sl = slice(max(0, j - 12), min(len(rr), j + 12))
        zw = np.where(ok[sl], Z[iy[sl], ix[sl]], np.nan)
        zz = Z[iy[j - 1], ix[j - 1]] if ok[j - 1] else np.nan
        zb[i] = np.nanmax(zw) if np.isfinite(zw).any() else zz
        wej[i] = int((np.diff(w[j:].astype(int)) == 1).sum())
    return rb, zb, wej


def koniec_sciany(rd, xs, ys, Z, F, normalne, c, katy, rmax: float = 20.0, krok: float = 0.025, piksel: float = PIKSEL):
    """Wariant 2: od ostatniego piksela rdzenia niecki na promieniu idziemy na zewnatrz po scianie wneki (normalna
    skierowana do srodka filaru, n_r < -0,3) do pierwszego piksela skierowanego do gory (n_z > COS_GORA) = poczatek
    plaskiej krawedzi od strony wneki. Nie zalezy od tego, czy za brzegiem powierzchnia opada (lacznik moze sie
    wznosic); nie dziala w kanale sruby na wylot (brak sciany widocznej z gory)."""
    rr = np.arange(0.0, rmax, krok)
    rb = np.full(len(katy), np.nan)
    zb = np.full(len(katy), np.nan)
    for i, th in enumerate(katy):
        ix, iy, ok = _promien(c, th, rr, xs, ys, piksel, Z.shape)
        wr = ok & rd[iy, ix]
        if not wr.any():
            continue
        j0 = int(np.flatnonzero(wr)[-1])
        f = F[iy, ix]
        n = np.where((f >= 0)[:, None], normalne[np.maximum(f, 0)], np.nan)
        nr_ = n[:, 0] * math.cos(th) + n[:, 1] * math.sin(th)
        nz = n[:, 2]
        stop = ~ok | (f < 0)
        sciana = False
        for j in range(j0, len(rr)):
            if stop[j]:
                break
            if nr_[j] < -0.3:
                sciana = True
            elif sciana and nz[j] > COS_GORA:
                rb[i] = rr[j]
                zb[i] = Z[iy[j], ix[j]]
                break
    return rb, zb


def fourier_odporny(th: np.ndarray, y: np.ndarray, rzad: int, skala: float = 0.2, iteracje: int = 8) -> np.ndarray:
    """Odporne (wagi Cauchy'ego) dopasowanie szeregu Fouriera y(th); NaN pomijane. Za malo punktow = same NaN."""
    A = [np.ones_like(th)]
    for k in range(1, rzad + 1):
        A += [np.cos(k * th), np.sin(k * th)]
    A = np.stack(A, 1)
    ok = np.isfinite(y)
    if ok.sum() < 2 * rzad + 4:
        return np.full_like(th, np.nan)
    w = np.ones(int(ok.sum()))
    cf = None
    for _ in range(iteracje):
        sw = np.sqrt(w)[:, None]
        cf = np.linalg.lstsq(A[ok] * sw, y[ok] * sw[:, 0], rcond=None)[0]
        res = y[ok] - A[ok] @ cf
        w = 1.0 / (1.0 + (res / skala) ** 2)
    return A @ cf


def najdluzsza_przerwa(ok: np.ndarray) -> int:
    """Najdluzszy kolowy ciag False."""
    ok = np.asarray(ok, dtype=bool)
    if ok.all():
        return 0
    if not ok.any():
        return int(len(ok))
    o = np.roll(ok, -int(np.argmax(ok)))
    best = cur = 0
    for v in o.tolist():
        cur = 0 if v else cur + 1
        best = max(best, cur)
    return best


# ----------------------------------------------------------------------------
# przekroj i narozniki plaskiej krawedzi
# ----------------------------------------------------------------------------
class _Przekroj:
    """Przekroj siatki polplaszczyzna: odcinki 2D (r, z), normalne 2D, wezly i sasiedztwo odcinkow."""

    __slots__ = ("s2", "n2", "klucze", "inv", "dl", "tf", "_por", "_od", "_do")

    def __init__(self, s2: np.ndarray, n2: np.ndarray):
        self.s2, self.n2 = s2, n2
        self.klucze, inv = np.unique(np.round(s2.reshape(-1, 2), 5), axis=0, return_inverse=True)
        self.inv = inv.ravel().reshape(-1, 2)
        self.dl = np.linalg.norm(s2[:, 1] - s2[:, 0], axis=1)
        self.tf = n2[:, 1] > COS_GORA
        plaskie = self.inv.ravel()
        por = np.argsort(plaskie, kind="stable")
        self._por = (por // 2).astype(np.int64)  # numer odcinka
        wez = plaskie[por]
        nk = np.arange(len(self.klucze))
        self._od = np.searchsorted(wez, nk, side="left")
        self._do = np.searchsorted(wez, nk, side="right")

    def przy(self, wezel: int) -> list[int]:
        """Odcinki stykajace sie z wezlem (w kolejnosci numerow odcinkow)."""
        return self._por[self._od[wezel]:self._do[wezel]].tolist()


def _przekroj(sub: trimesh.Trimesh, th: float) -> _Przekroj | None:
    """Przekroj podsiatki (os filaru w poczatku ukladu) polplaszczyzna pod katem ``th``."""
    er = np.array([math.cos(th), math.sin(th), 0.0])
    npl = np.array([-math.sin(th), math.cos(th), 0.0])
    segs, fi = trimesh.intersections.mesh_plane(sub, npl, np.zeros(3), return_faces=True)
    if len(segs) == 0:
        return None
    R = segs @ er
    keep = R.min(1) > R_MIN_PRZEKROJU
    if keep.sum() < 4:
        return None
    s2 = np.stack([R, segs[:, :, 2]], -1)[keep]
    n3 = sub.face_normals[fi[keep]]
    n2 = np.stack([n3 @ er, n3[:, 2]], -1)
    n2 /= np.maximum(np.linalg.norm(n2, axis=1, keepdims=True), 1e-12)
    return _Przekroj(s2, n2)


def _naroza(p: _Przekroj, start: tuple[float, float, str] | None):
    """Plaska krawedz w przekroju: od wezla startowego idziemy po lamanej w obie strony, dopoki normalna odcinka nie
    odchyli sie o > ANG_ROG_DEG od sredniej normalnej przebytej krawedzi (naroznik = ostre zalamanie albo suma
    lagodnych). ``start`` None = najwyzszy wezel calego przekroju (linia "T3"); (rb, zb, tryb) = wezel odcinka "do
    gory" w promieniu OKNO_STARTU od (rb, zb): ``najwyzszy`` albo ``najblizszy``.

    Zwraca [O, I, (dwusieczna, kat) O, (...) I, W, O2, I2] w 2D (r, z) albo None; O = koniec o wiekszym r.
    """
    klucze, inv, dl, n2, tf = p.klucze, p.inv, p.dl, p.n2, p.tf
    if start is None:
        wezel0 = int(np.argmax(klucze[:, 1]))
    else:
        rb, zb, tryb = start
        wez_kand = np.unique(inv[tf].ravel()) if tf.any() else np.zeros(0, dtype=int)
        if len(wez_kand) == 0:
            return None
        kk = klucze[wez_kand]
        blisko = (np.abs(kk[:, 0] - rb) <= OKNO_STARTU) & (kk[:, 1] >= zb - OKNO_STARTU)
        if not blisko.any():
            return None
        if tryb == "najblizszy":
            wezel0 = int(wez_kand[blisko][np.argmin(np.hypot(kk[blisko, 0] - rb, kk[blisko, 1] - zb))])
        else:
            wezel0 = int(wez_kand[blisko][np.argmax(kk[blisko, 1])])
    ztop = float(klucze[wezel0, 1])
    kand = [i for i in p.przy(wezel0) if tf[i]]
    if not kand:
        return None
    gora = max(kand, key=lambda i: n2[i, 1])
    cosmax = math.cos(math.radians(ANG_ROG_DEG))

    def nastepny(cur: int, wezel: int):
        nast = [i for i in p.przy(wezel) if i != cur]
        return nast[0] if len(nast) == 1 else None

    def drugi(seg: int, wezel: int) -> int:
        return int(inv[seg, 1] if inv[seg, 0] == wezel else inv[seg, 0])

    konce = []
    for kier in (0, 1):
        ref = n2[gora] * max(dl[gora], 1e-4)
        cur, wezel, przeb = gora, int(inv[gora, kier]), 0.0
        while True:
            nxt = nastepny(cur, wezel)
            if nxt is None or przeb > DROGA_MAX:
                nxt = None
                break
            rn = ref / np.linalg.norm(ref)
            if float(n2[nxt] @ rn) < cosmax:
                break
            ref = ref + n2[nxt] * max(dl[nxt], 1e-4)
            przeb += dl[nxt]
            cur = nxt
            wezel = drugi(nxt, wezel)
        X = klucze[wezel]
        nt = ref / np.linalg.norm(ref)
        rog = None
        X2 = X
        if nxt is not None:
            sw, c2, w2, d2, s_ = np.zeros(2), cur, wezel, 0.0, nxt
            while s_ is not None and d2 < DL_SCIANY:
                sw += n2[s_] * max(dl[s_], 1e-4)
                d2 += dl[s_]
                w2 = drugi(s_, w2)
                c2 = s_
                s_ = nastepny(c2, w2)
            b = sw / max(np.linalg.norm(sw), 1e-12)
            bis = -(nt + b)
            bis /= max(np.linalg.norm(bis), 1e-9)
            alfa = math.pi - math.acos(float(np.clip(nt @ b, -1, 1)))
            rog = (bis, alfa)
            X2 = klucze[w2]
        # linia W w tym kierunku: najdalej do srodka punkt skierowany do gory do W_DZ pod szczytem
        cur, wezel, przeb, Wmin = gora, int(inv[gora, kier]), 0.0, klucze[int(inv[gora, kier])]
        while przeb < DROGA_MAX:
            nxt2 = nastepny(cur, wezel)
            if nxt2 is None or n2[nxt2, 1] <= W_NZ:
                break
            w_ = drugi(nxt2, wezel)
            if klucze[w_, 1] < ztop - W_DZ:
                break
            przeb += dl[nxt2]
            cur, wezel = nxt2, w_
            if klucze[w_, 0] < Wmin[0]:
                Wmin = klucze[w_]
        konce.append((X, rog, Wmin, X2))
    if konce[0][0][0] >= konce[1][0][0]:
        (O, rO, _, O2), (Iw, rI, W, I2) = konce
    else:
        (Iw, rI, W, I2), (O, rO, _, O2) = konce
    W = W if W[0] <= Iw[0] + 1e-9 else Iw
    return [O, Iw, rO, rI, W, O2, I2]


def _rekord(w) -> np.ndarray:
    """Wiersz tabeli przekrojow: rO zO rI zI bOr bOz bIr bIz aO aI - szer rW zW rO2 zO2 rI2 zI2."""
    rek = np.full(18, np.nan)
    O, Iw, iO, iI, W, O2, I2 = w
    rek[0:2], rek[2:4], rek[12:14], rek[14:16], rek[16:18] = O, Iw, W, O2, I2
    if iO is not None:
        rek[4:6], rek[8] = iO[0], iO[1]
    if iI is not None:
        rek[6:8], rek[9] = iI[0], iI[1]
    return rek


def _podsiatka(m: trimesh.Trimesh, c, promien: float, z_min: float) -> trimesh.Trimesh:
    """Trojkaty w promieniu ``promien`` od osi filaru i nie nizej niz ``z_min``; os filaru w poczatku ukladu."""
    cen = m.triangles_center
    sel = np.flatnonzero((np.hypot(cen[:, 0] - c[0], cen[:, 1] - c[1]) <= promien) & (cen[:, 2] >= z_min))
    V = m.vertices[m.faces[sel].ravel()].reshape(-1, 3) - np.array([c[0], c[1], 0.0])
    return trimesh.Trimesh(V, np.arange(len(sel) * 3).reshape(-1, 3), process=True)


def _med_kolowa(x: np.ndarray, k: int) -> np.ndarray:
    st = np.stack([np.roll(x, o) for o in range(-k, k + 1)], 0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nanmedian(st, axis=0)


_KOLUMNY = {"O": (0, 1, (4, 5, 8)), "I": (2, 3, (6, 7, 9)), "W": (12, 13, ()), "O2": (14, 15, ()), "I2": (16, 17, ())}


def zbuduj_linie(rek: np.ndarray, katy: np.ndarray, c) -> dict | None:
    """Z tabeli przekrojow: filtr medianowy, interpolacja nieudanych przekrojow, stacje co KROK_STACJI.

    Zwraca slownik linii (O, I, W, S, O2, I2: X, ok, przekroj, L) + ``_przekroje`` (tabela surowa i po interpolacji)
    albo None, gdy ktorejs linii nie da sie zbudowac (za malo udanych przekrojow)."""
    n = len(katy)
    ok0 = np.isfinite(rek[:, 0])
    oki = {}
    idx = np.arange(n)
    R2 = rek.copy()
    for nazwa, (ir, iz, inne) in _KOLUMNY.items():
        mr, mz = _med_kolowa(rek[:, ir], MED_OKNO), _med_kolowa(rek[:, iz], MED_OKNO)
        with np.errstate(invalid="ignore"):
            ok = ok0 & (np.hypot(rek[:, ir] - mr, rek[:, iz] - mz) <= ODST_MED)
        oki[nazwa] = ok
        for j in (ir, iz) + tuple(inne):
            dob = ok & np.isfinite(rek[:, j])
            if dob.sum() < 4:
                continue
            xp = np.concatenate([idx[dob] - n, idx[dob], idx[dob] + n])
            R2[:, j] = np.interp(idx, xp, np.tile(rek[dob, j], 3))
    er = np.stack([np.cos(katy), np.sin(katy), np.zeros_like(katy)], 1)
    ez = np.array([0.0, 0.0, 1.0])
    c3 = np.array([c[0], c[1], 0.0])
    punkty = {nazwa: c3 + er * R2[:, ir:ir + 1] + ez * R2[:, iz:iz + 1] for nazwa, (ir, iz, _) in _KOLUMNY.items()}
    punkty["S"] = (punkty["O"] + punkty["W"]) / 2
    oki["S"] = oki["O"] & oki["W"]
    out = {}
    for nazwa, X in punkty.items():
        if not np.isfinite(X).all():
            return None
        Xz = np.vstack([X, X[:1]])
        s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(Xz, axis=0), axis=1))])
        L = float(s[-1])
        K = max(8, int(round(L / KROK_STACJI)))
        sk = np.arange(K) * L / K
        Xk = np.stack([np.interp(sk, s, Xz[:, j]) for j in range(3)], 1)
        okk = np.interp(sk, s, np.concatenate([oki[nazwa], oki[nazwa][:1]]).astype(float)) > 0.5
        out[nazwa] = {"X": Xk, "ok": okk, "przekroj": np.interp(sk, s, np.arange(n + 1)), "L": L}
    out["_przekroje"] = {"rek": rek, "R2": R2, "ok": ok0, "punkty": punkty, "srodek": (float(c[0]), float(c[1])), "katy": katy}
    return out


def _surowe_O(L: dict) -> np.ndarray:
    """Surowe punkty O przekrojow (3D), NaN dla nieudanych."""
    pz = L["_przekroje"]
    rek, katy, c = pz["rek"], pz["katy"], pz["srodek"]
    return np.stack([c[0] + np.cos(katy) * rek[:, 0], c[1] + np.sin(katy) * rek[:, 0], rek[:, 1]], 1)


def _miary_wyboru(L: dict | None, n: int) -> tuple[float, float]:
    """(najdluzsza przerwa linii O [st.], najwiekszy skok surowej linii O miedzy kolejnymi udanymi przekrojami [mm])."""
    if L is None:
        return math.inf, math.inf
    ok = np.asarray(L["_przekroje"]["ok"])
    przerwa = najdluzsza_przerwa(ok) * 360.0 / n
    X = _surowe_O(L)[ok]
    if len(X) < 2:
        return przerwa, math.inf
    skok = np.linalg.norm(np.diff(np.vstack([X, X[:1]]), axis=0), axis=1)
    return przerwa, float(skok.max())


# ----------------------------------------------------------------------------
# calosc
# ----------------------------------------------------------------------------
def _warianty_filaru(m: trimesh.Trimesh, c, wskazania: dict, katy: np.ndarray) -> tuple[dict, dict]:
    """Tabele przekrojow wariantow 1, 2 i 3 dla jednego filaru; ``wskazania``: {"1": (rb, zb, tryb), "2": (...)}."""
    n = len(katy)
    przygot = {}
    for nazwa, (rb, zb, tryb) in wskazania.items():
        rbf, zbf = fourier_odporny(katy, rb, 8), fourier_odporny(katy, zb, 8)
        if not np.isfinite(rbf).all():
            przygot[nazwa] = None
            continue
        with np.errstate(invalid="ignore"):
            zly = ~np.isfinite(rb) | (np.abs(rb - rbf) > ODST_GRZBIETU)
        przygot[nazwa] = (np.where(zly, rbf, rb), np.where(zly, zbf, zb), tryb, int(zly.sum()))
    wazne = [v for v in przygot.values() if v is not None]
    rek = {nazwa: np.full((n, 18), np.nan) for nazwa in wskazania}
    licz = {f"grzbiet_poprawiony_{nazwa}": (v[3] if v is not None else n) for nazwa, v in przygot.items()}
    if wazne:
        promien = max(float(np.nanmax(v[0])) for v in wazne) + ZAPAS_PODSIATKI_R
        z_min = min(float(np.nanmin(v[1])) for v in wazne) - ZAPAS_PODSIATKI_Z
        sub = _podsiatka(m, c, promien, z_min)
        for i, th in enumerate(katy):
            p = _przekroj(sub, float(th)) if len(sub.faces) else None
            if p is None:
                continue
            for nazwa, v in przygot.items():
                if v is None or not np.isfinite(v[0][i]):
                    continue
                w = _naroza(p, (float(v[0][i]), float(v[1][i]), v[2]))
                if w is not None:
                    rek[nazwa][i] = _rekord(w)
    for nazwa in wskazania:  # punkt O odstajacy od gladkiej krzywej = przekroj odrzucony
        r = rek[nazwa]
        rof, zof = fourier_odporny(katy, r[:, 0], 16, 0.1), fourier_odporny(katy, r[:, 1], 16, 0.1)
        with np.errstate(invalid="ignore"):
            zly_o = np.isfinite(r[:, 0]) & ((np.abs(r[:, 0] - rof) > ODST_O) | (np.abs(r[:, 1] - zof) > ODST_O))
        r[zly_o] = np.nan
        licz[f"O_odrzucone_{nazwa}"] = int(zly_o.sum())
    # wariant 3: zgoda wariantow 1 i 2, spory rozstrzyga gladka krzywa
    rek1, rek2 = rek["1"], rek["2"]
    v1, v2 = np.isfinite(rek1[:, 0]), np.isfinite(rek2[:, 0])
    with np.errstate(invalid="ignore"):
        dd = np.hypot(rek1[:, 0] - rek2[:, 0], rek1[:, 1] - rek2[:, 1])
        zg = v1 & v2 & (dd <= ZGODA_MM)
    rek3 = np.full_like(rek1, np.nan)
    rek3[zg] = rek1[zg]
    rozstrz = 0
    if zg.sum() >= ZGODNYCH_MIN:
        rof, zof = fourier_odporny(katy, rek3[:, 0], 16, 0.1), fourier_odporny(katy, rek3[:, 1], 16, 0.1)
        for i in np.flatnonzero(~zg & (v1 | v2)):
            best, bd = None, ODST_O
            for rk in (rek1, rek2):
                if np.isfinite(rk[i, 0]):
                    d_ = math.hypot(rk[i, 0] - rof[i], rk[i, 1] - zof[i])
                    if d_ < bd:
                        best, bd = rk, d_
            if best is not None:
                rek3[i] = best[i]
                rozstrz += 1
    else:  # za malo zgodnych (np. brak wariantu 2 w koronie z kanalem sruby) - wariant 1 bez potwierdzenia
        rek3 = rek1.copy()
        rozstrz = -1
    rek["3"] = rek3
    licz.update({"przekroje_zgodne_1_2": int(zg.sum()), "spory_rozstrzygniete": int(rozstrz),
                 "wariant1_waznych": int(v1.sum()), "wariant2_waznych": int(v2.sum())})
    return rek, licz


def _linia_t3(m: trimesh.Trimesh, katy: np.ndarray, z_min: float) -> np.ndarray | None:
    """Stacje linii O wyznaczonej jak w prototypie T3: os w srodku obrysu pracy (poczatek ukladu), start w najwyzszym
    wezle przekroju. Trzecie, niezalezne wyznaczenie - tylko dla pracy z jednym filarem."""
    sub = _podsiatka(m, (0.0, 0.0), math.inf, z_min)
    rek = np.full((len(katy), 18), np.nan)
    for i, th in enumerate(katy):
        p = _przekroj(sub, float(th))
        if p is None:
            continue
        w = _naroza(p, None)
        if w is not None:
            rek[i] = _rekord(w)
    if np.isfinite(rek[:, 0]).sum() < 8:
        return None
    L = zbuduj_linie(rek, katy, (0.0, 0.0))
    return None if L is None else L["O"]["X"]


def _stacje_zweryf(L: dict, zweryf: np.ndarray) -> np.ndarray:
    return zweryf[np.round(L["przekroj"]).astype(int) % len(zweryf)]


def wyznacz(m: trimesh.Trimesh) -> LinieProjektu:
    """Linie krawedzi brzegu kazdego filaru siatki ``m`` (brzegiem do gory, w skali odniesienia, srodek obrysu xy
    w poczatku ukladu). Bez pamieci podrecznej - zwykle wolana przez ``linie_siatki``."""
    t0 = time.time()
    uwagi: list[str] = []
    scena = scena_siatki(m)
    xs, ys, Z, F = mapa_wysokosci(m, scena)
    if not np.isfinite(Z).any():
        return LinieProjektu([], [], ["pusta mapa wysokosci"], round(time.time() - t0, 2))
    ws, niecki, k, gl = obszary_filarow(Z)
    if k == 0:
        return LinieProjektu([], niecki, ["brak niecki filaru (wneki albo kanalu sruby): brzegu nie wyznaczono"], round(time.time() - t0, 2))
    katy = np.radians(np.arange(0.0, 360.0, KROK_KATA_DEG))
    n = len(katy)
    normalne = np.asarray(m.face_normals)
    surowe = []
    for nr in range(1, k + 1):
        w = ws == nr
        iy, ix = np.nonzero(w)
        c = np.array([xs[ix].mean(), ys[iy].mean()])
        rd = w & (gl > GLEB_RDZENIA)  # srodek: centroid rdzenia niecki (wneki), stabilniejszy niz obszar z polka
        if rd.sum() > 20:
            jy, jx = np.nonzero(rd)
            c = np.array([xs[jx].mean(), ys[jy].mean()])
        rb1, zb1, _ = grzbiet(ws, nr, xs, ys, Z, c, katy)
        rb2, zb2 = koniec_sciany(rd if rd.sum() > 20 else w, xs, ys, Z, F, normalne, c, katy)
        rek, licz = _warianty_filaru(m, c, {"1": (rb1, zb1, "najwyzszy"), "2": (rb2, zb2, "najblizszy")}, katy)
        # otwor na wylot widoczny z gory w niecce filaru (np. kanal sruby): czesc rdzenia niecki bez trafienia promienia
        licz["otwor_na_wylot"] = bool(rd.any() and np.isnan(Z[rd]).mean() > 0.05)
        kand = {nazwa: (zbuduj_linie(r, katy, c) if np.isfinite(r[:, 0]).sum() >= 8 else None) for nazwa, r in rek.items()}
        z_grzb = float(np.nanmin(zb1)) if np.isfinite(zb1).any() else float(np.nanmin(Z))
        surowe.append((nr, c, kand, licz, z_grzb))
    t3 = None
    if k == 1 and any(L is not None for L in surowe[0][2].values()):
        t3 = _linia_t3(m, katy, surowe[0][4] - ZAPAS_PODSIATKI_Z - DROGA_MAX)
    drzewo_t3 = cKDTree(t3) if t3 is not None else None
    filary: list[Filar] = []
    for nr, c, kand, licz, _ in surowe:
        miary = {nazwa: _miary_wyboru(L, n) for nazwa, L in kand.items()}
        kolejnosc = ("3", "1", "2")
        dobre = [nazwa for nazwa in kolejnosc if miary[nazwa][0] <= PRZERWA_DOBRA_ST and miary[nazwa][1] <= SKOK_DOBRY_MM]
        wyb = dobre[0] if dobre else min(kolejnosc, key=lambda nazwa: miary[nazwa][0] / PRZERWA_DOBRA_ST + miary[nazwa][1] / SKOK_DOBRY_MM)
        L = kand[wyb]
        if L is None:  # filar zostaje bez linii: nie ma go w ``filary``, jest w ``niecki`` (przyjeta) -> ``filary_bez_linii``
            uwagi.append(f"filar {nr}: za malo udanych przekrojow - linii nie wyznaczono")
            continue
        pz = L["_przekroje"]
        ok = np.asarray(pz["ok"])
        Xw = _surowe_O(L)
        zg = np.zeros(n, dtype=int)
        for nazwa in ("1", "2"):
            if kand[nazwa] is not None:
                with np.errstate(invalid="ignore"):
                    dd = np.linalg.norm(_surowe_O(kand[nazwa]) - Xw, axis=1)
                    zg += (np.isfinite(dd) & (dd <= ZGODA_MM)).astype(int)
        if drzewo_t3 is not None:
            dd = drzewo_t3.query(np.nan_to_num(Xw, nan=1e6))[0]
            zg += (np.isfinite(Xw[:, 0]) & (dd <= ZGODA_MM)).astype(int)
        with np.errstate(invalid="ignore"):
            szer = np.hypot(pz["rek"][:, 0] - pz["rek"][:, 2], pz["rek"][:, 1] - pz["rek"][:, 3])
            ksztalt = np.isfinite(szer) & (szer >= SZER_MIN) & (szer <= SZER_MAX)
        zgodny = zg >= 2
        zweryf = ok & zgodny & ksztalt
        udzial = float(zweryf.mean())
        ciag = najdluzsza_przerwa(zweryf) * 360.0 / n
        werdykt = "wiarygodna" if (udzial >= UDZIAL_WIARYGODNA and ciag <= CIAG_WIARYGODNA_ST) else ("czesciowa" if udzial >= UDZIAL_CZESCIOWA else "niepewna")
        O3, I3 = pz["punkty"]["O"], pz["punkty"]["I"]
        S3 = scena.compute_closest_points(o3d.core.Tensor(np.ascontiguousarray((O3 + I3) / 2, dtype=np.float32)))["points"].numpy().astype(np.float64)
        linie = {}
        for nazwa, (X, lz) in {"O": (L["O"]["X"], L["O"]), "I": (L["I"]["X"], L["I"])}.items():
            linie[nazwa] = Linia(X, _stacje_zweryf(lz, zweryf), lz["przekroj"], lz["L"])
        Sz = np.vstack([S3, S3[:1]])  # linia S: te same przekroje, stacje wzdluz lamanej srodkow
        s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(Sz, axis=0), axis=1))])
        Ks = max(8, int(round(float(s[-1]) / KROK_STACJI)))
        sk = np.arange(Ks) * float(s[-1]) / Ks
        prz = np.interp(sk, s, np.arange(n + 1))
        linie["S"] = Linia(np.stack([np.interp(sk, s, Sz[:, j]) for j in range(3)], 1), zweryf[np.round(prz).astype(int) % n], prz, float(s[-1]))
        przerwa_mm = najdluzsza_przerwa(linie["O"].zweryf) * linie["O"].krok
        kontrola = {**licz, "warianty_przerwa_skok": {nazwa: [round(a, 1) if math.isfinite(a) else None, round(b, 3) if math.isfinite(b) else None]
                                                     for nazwa, (a, b) in miary.items()},
                    "przekroje_udane": int(ok.sum()), "przekroje_zgodne_2_zrodla": int(zgodny.sum()), "przekroje_ksztalt_ok": int(ksztalt.sum()),
                    "szer_OI_mediana_mm": round(float(np.nanmedian(szer)), 3) if np.isfinite(szer).any() else None,
                    "zrodla_drugiej_opinii": ["wariant 1", "wariant 2"] + (["T3"] if drzewo_t3 is not None else [])}
        filary.append(Filar(nr, (float(c[0]), float(c[1])), wyb, bool(dobre), werdykt, udzial, ciag, float(przerwa_mm), linie,
                            katy.copy(), O3, I3, S3, ok.copy(), zweryf, kontrola))
    if not filary:
        uwagi.append("zaden filar nie ma linii brzegu")
    return LinieProjektu(filary, niecki, uwagi, round(time.time() - t0, 2))


# ----------------------------------------------------------------------------
# pamiec podreczna i przeliczenie skali
# ----------------------------------------------------------------------------
_PAMIEC: dict[str, LinieProjektu] = {}  # klucz projektu -> linie w skali odniesienia (srodek obrysu w 0)
_KATALOG: Path | None = None  # opcjonalna pamiec na dysku (wspolna dla procesow)
_PAMIEC_MAX = 512


def ustaw_katalog_pamieci(katalog: Path | str | None) -> None:
    """Wlacza (albo, dla None, wylacza) pamiec podreczna linii na dysku: jeden plik ``<klucz>_v<WERSJA>.npz`` na projekt.
    Domyslnie wylaczona - modul sam nie pisze niczego na dysk."""
    global _KATALOG
    _KATALOG = Path(katalog) if katalog is not None else None


def wyczysc_pamiec() -> None:
    _PAMIEC.clear()


def _plik_pamieci(klucz: str) -> Path | None:
    if _KATALOG is None or not klucz:
        return None
    bezp = "".join(ch for ch in str(klucz) if ch.isalnum() or ch in "-_")
    return _KATALOG / f"{bezp}_v{WERSJA}.npz" if bezp else None


def zapisz_npz(linie: LinieProjektu, plik: Path) -> None:
    """Zapis linii do jednego pliku (tablice + opis JSON); zapis przez plik tymczasowy, zeby drugi proces nie czytal polowy."""
    tab: dict[str, np.ndarray] = {}
    meta = {"wersja": WERSJA, "skala": linie.skala, "niecki": linie.niecki, "uwagi": linie.uwagi, "czas_s": linie.czas_s, "filary": []}
    for i, f in enumerate(linie.filary):
        meta["filary"].append({"nr": f.nr, "srodek": list(f.srodek), "wariant": f.wariant, "wybor_pewny": f.wybor_pewny, "werdykt": f.werdykt,
                               "udzial_zweryf": f.udzial_zweryf, "najdl_ciag_st": f.najdl_ciag_st, "najdl_przerwa_mm": f.najdl_przerwa_mm,
                               "kontrola": f.kontrola})
        for nazwa, L in f.linie.items():
            tab[f"f{i}_{nazwa}_X"], tab[f"f{i}_{nazwa}_zweryf"], tab[f"f{i}_{nazwa}_przekroj"] = L.X, L.zweryf, L.przekroj
            tab[f"f{i}_{nazwa}_L"] = np.array(L.dlugosc)
        for nazwa in ("katy", "O", "I", "S", "udany", "zweryf"):
            tab[f"f{i}_p_{nazwa}"] = getattr(f, nazwa)
    plik = Path(plik)
    plik.parent.mkdir(parents=True, exist_ok=True)
    tmp = plik.with_name(f"{plik.stem}.{os.getpid()}.tmp.npz")
    np.savez_compressed(tmp, meta=np.array(json.dumps(meta)), **tab)
    os.replace(tmp, plik)


def wczytaj_npz(plik: Path) -> LinieProjektu | None:
    """Odczyt pliku z ``zapisz_npz``; plik innej wersji albo uszkodzony = None."""
    try:
        with np.load(plik, allow_pickle=False) as d:
            meta = json.loads(str(d["meta"]))
            if meta.get("wersja") != WERSJA:
                return None
            filary = []
            for i, mf in enumerate(meta["filary"]):
                linie = {nazwa: Linia(d[f"f{i}_{nazwa}_X"], d[f"f{i}_{nazwa}_zweryf"], d[f"f{i}_{nazwa}_przekroj"], float(d[f"f{i}_{nazwa}_L"]))
                         for nazwa in NAZWY_LINII}
                filary.append(Filar(mf["nr"], tuple(mf["srodek"]), mf["wariant"], mf["wybor_pewny"], mf["werdykt"], mf["udzial_zweryf"],
                                    mf["najdl_ciag_st"], mf["najdl_przerwa_mm"], linie, d[f"f{i}_p_katy"], d[f"f{i}_p_O"], d[f"f{i}_p_I"],
                                    d[f"f{i}_p_S"], d[f"f{i}_p_udany"], d[f"f{i}_p_zweryf"], mf["kontrola"]))
            return LinieProjektu(filary, meta["niecki"], meta["uwagi"], meta["czas_s"], meta["skala"])
    except (OSError, KeyError, ValueError, EOFError, zipfile.BadZipFile):
        return None


def klucz_projektu(skrot: str, obrot=None) -> str:
    """Klucz pamieci podrecznej projektu: skrot SHA-256 pliku + znacznik orientacji. ``obrot`` = macierz, ktora ustawila
    plik brzegiem do gory (``synth.orientacja_brzegiem_do_gory`` albo ``match.Projekt.T0``): zwykly przypadek (plik z
    brzegiem na dole, obrot o 180 st.) nie zmienia klucza, plik wziety bez obrotu dostaje przyrostek ``_g`` - ten sam
    plik wczytany z wymuszona inna orientacja ma inna siatke, wiec i inne linie."""
    if obrot is None or np.asarray(obrot)[2, 2] < 0:
        return str(skrot)
    return f"{skrot}_g"


def srodek_ukladu(m: trimesh.Trimesh) -> np.ndarray:
    """Punkt odniesienia siatki: srodek obrysu xy i najwyzszy punkt (jak uklad puli w ``match.Projekt``)."""
    b = m.bounds
    return np.array([(b[0, 0] + b[1, 0]) / 2, (b[0, 1] + b[1, 1]) / 2, b[1, 2]])


def linie_siatki(siatka: trimesh.Trimesh, skala: float = 1.0, klucz: str | None = None) -> LinieProjektu:
    """Linie krawedzi brzegu siatki projektu brzegiem do gory, w jej wlasnym ukladzie wspolrzednych.

    ``skala``: ile razy siatka jest wieksza od pliku projektu (wspolczynnik skurczu; 1,0 = praca spieczona).
    ``klucz``: identyfikator projektu (skrot SHA-256 pliku) - z nim wynik jest liczony raz na projekt i trzymany w
    pamieci modulu (a po ``ustaw_katalog_pamieci`` takze na dysku), niezaleznie od skali i przesuniecia siatki.
    """
    if not (math.isfinite(skala) and skala > 0):
        raise ValueError(f"skala siatki musi byc > 0, jest {skala}")
    c = srodek_ukladu(siatka)
    k = SKALA_ODNIESIENIA / skala
    wz = _PAMIEC.get(klucz) if klucz else None
    plik = _plik_pamieci(klucz) if klucz else None
    zapisac = plik is not None and not plik.exists()  # takze wtedy, gdy linie sa juz w pamieci procesu, a pliku jeszcze nie ma
    if wz is None:
        if plik is not None and not zapisac:
            wz = wczytaj_npz(plik)
        if wz is None:
            wz = wyznacz(trimesh.Trimesh((np.asarray(siatka.vertices) - c) * k, np.asarray(siatka.faces), process=False))
            zapisac = plik is not None
        if len(_PAMIEC) >= _PAMIEC_MAX:
            _PAMIEC.pop(next(iter(_PAMIEC)))
        if klucz:
            _PAMIEC[klucz] = wz
    if zapisac:
        try:
            zapisz_npz(wz, plik)
        except OSError as e:  # pamiec na dysku jest tylko przyspieszeniem
            warnings.warn(f"nie zapisano linii brzegu do {plik.name}: {e}", stacklevel=2)
    return wz.przeksztalc(1.0 / k, c)


def stacje(linie: LinieProjektu, nazwy: tuple[str, ...] = ("O", "I")) -> dict:
    """Stacje wybranych linii wszystkich filarow w jednej tablicy (do drzewa odleglosci).

    Zwraca ``X`` (N, 3), ``filar`` (N,) - indeks filaru na liscie ``linie.filary``, ``linia`` (N,) - indeks nazwy,
    ``nr`` (N,) - numer stacji na swojej linii, ``zweryf`` (N,)."""
    X, fil, lin, nr, zw = [], [], [], [], []
    for i, f in enumerate(linie.filary):
        for j, nazwa in enumerate(nazwy):
            L = f.linie[nazwa]
            X.append(L.X)
            fil.append(np.full(len(L.X), i))
            lin.append(np.full(len(L.X), j))
            nr.append(np.arange(len(L.X)))
            zw.append(L.zweryf)
    if not X:
        return {"X": np.zeros((0, 3)), "filar": np.zeros(0, dtype=int), "linia": np.zeros(0, dtype=int), "nr": np.zeros(0, dtype=int),
                "zweryf": np.zeros(0, dtype=bool)}
    return {"X": np.vstack(X), "filar": np.concatenate(fil), "linia": np.concatenate(lin), "nr": np.concatenate(nr), "zweryf": np.concatenate(zw)}
