"""pamiec_puli - pamiec podreczna projektow puli per praca (E3-A5): projekt STL x wspolczynnik na dysku i w procesie.

Po co: pula wieczorna ma kilkaset wpisow (projekt x wspolczynnik krazka), a budowa ``match.Projekt`` z pliku STL to ok.
0,2-0,4 s (wczytanie, orientacja, 40 tys. punktow, FPFH, scena promieni). ``match.Pula.z_wpisow`` potrzebuje dla kazdej
geometrii tylko czesci lekkiej (``match.ProjektLekki``: cechy filtra z profilem glebokosci, chmura 0,3 mm do rankingu
wstepnego); pelny projekt powstaje dopiero dla kandydatow po filtrze i rankingu. Obie czesci sa liczone raz i zapisane na
dysk (jeden plik ``.npz`` na geometrie), wiec po starcie programu pula wczytuje sie w sekundy, a pelne projekty kandydatow
w milisekundy.

Klucz wpisu: skrot SHA-256 ZAWARTOSCI pliku (16 znakow, jak ``synth.skrot_pliku``) + wspolczynnik (6 miejsc) + orientacja
(argument i znacznik: ``e`` = nazwa exocad, brzeg na dole z konwencji eksportu; ``h`` = heurystyka z siatki) + odcisk
algorytmu (``odcisk()``: wersja formatu, stale match wplywajace na dane, wersje open3d i trimesh). Uniewaznianie: inna
zawartosc pliku = inny skrot = inny wpis (plik zmieniony po indeksowaniu nie dostanie starych danych); zmiana algorytmu
albo bibliotek = inny odcisk; plik pamieci uszkodzony albo niezgodny z kluczem = liczony od nowa (licznik
``bledy_odczytu``); ``sprzataj(dni)`` usuwa wpisy nieuzywane od ``dni`` dni (uzycie odswieza czas pliku).

Dane osobowe: w pamieci na dysku sa tylko skrot, liczby i cechy z nazwy pliku (zeby, typ pracy) - bez nazwy pliku, folderu
i sciezki. Sciezka do pliku STL jest tylko w pamieci procesu (``ProjektLekki.zrodlo``) - do zbudowania pelnego projektu,
gdy nie ma go na dysku. Katalog: ``[sciezki] pula_cache`` / ``projekty`` (``z_ustawien``); bez katalogu = tylko pamiec procesu.
"""
from __future__ import annotations

import collections
import hashlib
import json
import os
import time
import warnings
import zipfile
from pathlib import Path

import numpy as np

from . import match as M
from . import synth as S
from . import ustawienia as UST

WERSJA = 1  # format pliku pamieci; zmiana tresci = nowy numer
PODKATALOG = "projekty"  # w [sciezki] pula_cache (obok linii brzegu z krawedz)
LIMIT_CIEZKICH = 64  # pelnych projektow trzymanych w procesie (ok. 10-30 MB kazdy); najdawniej uzyte wypadaja (zostaja na dysku)
LIMIT_LEKKICH = 4000  # czesci lekkich w procesie (ok. 0,1-0,3 MB kazda)
POLA_LEKKIE = ("l_profil", "l_pts", "l_nrm")


def odcisk() -> str:
    """Odcisk algorytmu: zmiana stalych match wplywajacych na dane pamieci albo wersji bibliotek = nowe wpisy (stare nieuzywane)."""
    import open3d as o3d
    import trimesh

    dane = {"wersja": WERSJA, "punkty": M.PUNKTY_KANDYDATA, "voxel_fpfh": M.VOXEL_FPFH, "voxel_zgrubne": M.VOXEL_ZGRUBNE, "krok_profilu": M.KROK_PROFILU,
            "voxel_wstepny": M.WSTEPNY_VOXEL_PROJEKTU, "open3d": o3d.__version__, "trimesh": trimesh.__version__}
    return hashlib.sha256(json.dumps(dane, sort_keys=True).encode("ascii")).hexdigest()[:8]


def znacznik_orientacji(plik: Path, orientacja: str) -> str:
    """Orientacja geometrii w kluczu: podana wprost albo (``auto``) ``e`` dla nazwy exocad i ``h`` dla heurystyki z siatki."""
    return orientacja if orientacja != "auto" else ("e" if S.plik_exocad(Path(plik).name) else "h")


def z_ustawien(ust: dict, limit_ciezkich: int = LIMIT_CIEZKICH) -> PamiecPuli:
    """Pamiec w ``[sciezki] pula_cache`` / ``projekty`` (sciezka wzgledna liczona od katalogu programu)."""
    p = Path(ust["sciezki"]["pula_cache"])
    return PamiecPuli((p if p.is_absolute() else UST.KORZEN / p) / PODKATALOG, limit_ciezkich=limit_ciezkich)


class PamiecPuli:
    """Czesci lekkie i pelne projekty puli: w procesie (pelne - najwyzej ``limit_ciezkich``, najdawniej uzyte wypadaja) i na
    dysku w ``katalog`` (None = bez dysku). ``statystyka``: liczniki trafien i liczenia (do raportu i ekranu)."""

    def __init__(self, katalog: Path | str | None = None, limit_ciezkich: int = LIMIT_CIEZKICH):
        self.katalog = Path(katalog) if katalog is not None else None
        self.limit_ciezkich = max(1, int(limit_ciezkich))
        self.odcisk = odcisk()
        self._lekkie: collections.OrderedDict[str, M.ProjektLekki] = collections.OrderedDict()
        self._ciezkie: collections.OrderedDict[str, M.Projekt] = collections.OrderedDict()
        self._skroty: dict[tuple, str] = {}
        self.statystyka = {"lekkie_z_pamieci": 0, "lekkie_z_dysku": 0, "lekkie_policzone": 0, "ciezkie_z_pamieci": 0, "ciezkie_z_dysku": 0,
                           "ciezkie_z_pliku": 0, "bledy_odczytu": 0, "bledy_zapisu": 0, "czas_liczenia_s": 0.0, "czas_odczytu_s": 0.0}

    # --- klucze i pliki ---------------------------------------------------------------------------------------------
    def klucz(self, sha16: str, wspolczynnik: float, orientacja: str, znacznik: str) -> str:
        return f"{sha16}_{M.tekst_wspolczynnika(wspolczynnik)}_{orientacja}_{znacznik}_{self.odcisk}"

    def _plik(self, klucz: str) -> Path | None:
        if self.katalog is None:
            return None
        bezp = "".join(ch for ch in klucz if ch.isalnum() or ch in "-_.")
        return self.katalog / f"{bezp}.npz"

    def pliki(self) -> list[Path]:
        """Pliki pamieci na dysku (bez plikow tymczasowych zapisu)."""
        if self.katalog is None or not self.katalog.is_dir():
            return []
        return sorted(p for p in self.katalog.glob("*.npz") if ".tmp" not in p.name)

    def skrot(self, plik: Path) -> str:
        """Skrot zawartosci pliku (16 znakow SHA-256); w procesie zapamietany po (sciezka, rozmiar, czas zmiany)."""
        st = os.stat(plik)
        k = (str(plik), st.st_size, st.st_mtime_ns)
        if k not in self._skroty:
            self._skroty[k] = S.skrot_pliku(plik)
        return self._skroty[k]

    # --- czesc lekka ------------------------------------------------------------------------------------------------
    def lekki(self, plik: Path, sha16: str, wspolczynnik: float, orientacja: str = "auto") -> M.ProjektLekki:
        """Czesc lekka geometrii (plik o skrocie ``sha16``, ``wspolczynnik``, ``orientacja``): z procesu, z dysku albo
        policzona z pliku (wtedy zapisana na dysk razem z pelnym projektem). ``ValueError`` = pliku nie da sie wczytac."""
        znak = znacznik_orientacji(plik, orientacja)
        kl = self.klucz(sha16, wspolczynnik, orientacja, znak)
        lk = self._lekkie.get(kl)
        if lk is not None:
            self._lekkie.move_to_end(kl)
            self.statystyka["lekkie_z_pamieci"] += 1
        else:
            lk = self._czytaj_lekki(kl, sha16, wspolczynnik)
            if lk is not None:
                self.statystyka["lekkie_z_dysku"] += 1
            else:
                t0 = time.time()
                pr = M.Projekt(plik, wspolczynnik, orientacja)
                lk = pr.lekki()
                lk.klucz_pamieci = kl
                self.statystyka["lekkie_policzone"] += 1
                self.statystyka["czas_liczenia_s"] = round(self.statystyka["czas_liczenia_s"] + time.time() - t0, 3)
                if pr.id != sha16:  # plik zmienil sie miedzy skrotem a wczytaniem: geometria z biezacej zawartosci, bez zapisu
                    lk.klucz_pamieci = self.klucz(pr.id, wspolczynnik, orientacja, znak)
                    lk.zrodlo = (Path(plik), orientacja)
                    self._wstaw_ciezki(lk.klucz_pamieci, pr)
                    return lk
                self._zapisz(kl, pr, lk)
                if self.katalog is None:  # bez dysku pelny projekt zostaje w procesie (z dyskiem - wczytany, gdy bedzie kandydatem)
                    self._wstaw_ciezki(kl, pr)
            self._lekkie[kl] = lk
            while len(self._lekkie) > LIMIT_LEKKICH:
                self._lekkie.popitem(last=False)
        lk.zrodlo = (Path(plik), orientacja)
        return lk

    def _czytaj_lekki(self, kl: str, sha16: str, wspolczynnik: float) -> M.ProjektLekki | None:
        plik = self._plik(kl)
        if plik is None or not plik.is_file():
            return None
        t0 = time.time()
        try:
            with np.load(plik, allow_pickle=False) as d:
                opis = json.loads(str(d["meta"]))
                if opis.get("klucz") != kl or opis.get("id") != sha16 or abs(float(opis.get("wspolczynnik", -1)) - round(float(wspolczynnik), 6)) > 1e-9:
                    raise ValueError("wpis pamieci niezgodny z kluczem")
                prof, pts, nrm = (np.array(d[n], dtype=np.float64) for n in POLA_LEKKIE)
        except (OSError, KeyError, ValueError, EOFError, zipfile.BadZipFile):
            self.statystyka["bledy_odczytu"] += 1
            return None
        lk = M.ProjektLekki(opis["id"], float(opis["wspolczynnik"]), [float(v) for v in opis["obrys_xy"]], float(opis["wysokosc"]), float(opis["hull"]),
                            prof.reshape(-1, 3), pts, nrm, opis["cechy"].get("zeby", []), opis["cechy"].get("typ", ""))
        lk.klucz_pamieci = kl
        self._dotknij(plik)
        self.statystyka["czas_odczytu_s"] = round(self.statystyka["czas_odczytu_s"] + time.time() - t0, 3)
        return lk

    # --- pelny projekt ----------------------------------------------------------------------------------------------
    def projekt(self, lk: M.ProjektLekki) -> M.Projekt:
        """Pelny projekt geometrii: z procesu, z dysku albo z pliku STL (``lk.zrodlo``). ``ValueError``: pliku nie da sie wczytac
        albo jego zawartosc zmienila sie od zbudowania puli (inny skrot)."""
        kl = lk.klucz_pamieci
        pr = self._ciezkie.get(kl)
        if pr is not None:
            self._ciezkie.move_to_end(kl)
            self.statystyka["ciezkie_z_pamieci"] += 1
            return pr
        pr = self._czytaj_ciezki(kl, lk)
        if pr is not None:
            self.statystyka["ciezkie_z_dysku"] += 1
        else:
            if lk.zrodlo is None:
                raise ValueError(f"projekt {lk.id}: brak pliku do wczytania")
            plik, orientacja = lk.zrodlo
            t0 = time.time()
            pr = M.Projekt(plik, lk.wspolczynnik, orientacja)
            self.statystyka["czas_liczenia_s"] = round(self.statystyka["czas_liczenia_s"] + time.time() - t0, 3)
            if pr.id != lk.id:
                raise ValueError(f"projekt {lk.id}: plik zmienil sie od zbudowania puli (teraz {pr.id})")
            self.statystyka["ciezkie_z_pliku"] += 1
            p = self._plik(kl)
            if p is not None and not p.is_file():
                self._zapisz(kl, pr, lk)
        if not pr._profil:  # profil filtra z czesci lekkiej (te same liczby) - filtr w dopasuj_pare nie liczy otoczek drugi raz
            pr._profil = {k: ([float(a), float(b)], float(h)) for k, (a, b, h) in enumerate(lk.profil, start=1)}
        self._wstaw_ciezki(kl, pr)
        return pr

    def _czytaj_ciezki(self, kl: str, lk: M.ProjektLekki) -> M.Projekt | None:
        plik = self._plik(kl)
        if plik is None or not plik.is_file():
            return None
        t0 = time.time()
        try:
            with np.load(plik, allow_pickle=False) as d:
                opis = json.loads(str(d["meta"]))
                if opis.get("klucz") != kl or opis.get("id") != lk.id:
                    raise ValueError("wpis pamieci niezgodny z kluczem")
                tab = {n: d[n] for n in ("V", "F", "T0", "pts", "nrm", "fpfh_pts", "fpfh_nrm", "fpfh")}
        except (OSError, KeyError, ValueError, EOFError, zipfile.BadZipFile):
            self.statystyka["bledy_odczytu"] += 1
            return None
        pr = M.Projekt.z_tablic(tab, opis, lk.zrodlo[0] if lk.zrodlo else None)
        self.statystyka["czas_odczytu_s"] = round(self.statystyka["czas_odczytu_s"] + time.time() - t0, 3)
        return pr

    def _wstaw_ciezki(self, kl: str, pr: M.Projekt) -> None:
        self._ciezkie[kl] = pr
        self._ciezkie.move_to_end(kl)
        while len(self._ciezkie) > self.limit_ciezkich:
            self._ciezkie.popitem(last=False)

    # --- zapis i sprzatanie -----------------------------------------------------------------------------------------
    def _zapisz(self, kl: str, pr: M.Projekt, lk: M.ProjektLekki) -> None:
        plik = self._plik(kl)
        if plik is None:
            return
        tab, opis = pr.do_tablic()
        opis.update(klucz=kl, wersja=WERSJA, odcisk=self.odcisk)
        tmp = plik.with_name(f"{plik.stem}.{os.getpid()}.tmp.npz")
        try:
            plik.parent.mkdir(parents=True, exist_ok=True)
            np.savez(tmp, meta=np.array(json.dumps(opis)), l_profil=lk.profil, l_pts=lk.punkty, l_nrm=lk.normalne, **tab)
            os.replace(tmp, plik)
        except OSError as e:  # pamiec na dysku jest tylko przyspieszeniem (pelny dysk, plik zajety przez inny proces)
            self.statystyka["bledy_zapisu"] += 1
            warnings.warn(f"pamiec puli: nie zapisano wpisu {plik.name}: {type(e).__name__}", stacklevel=3)
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass

    @staticmethod
    def _dotknij(plik: Path) -> None:
        try:
            os.utime(plik)
        except OSError:
            pass

    def sprzataj(self, dni: float, teraz: float | None = None) -> int:
        """Usuwa z dysku wpisy nieuzywane od ``dni`` dni (i pozostalosci przerwanych zapisow starsze niz doba); zwraca liczbe usunietych plikow."""
        if self.katalog is None or not self.katalog.is_dir():
            return 0
        teraz = time.time() if teraz is None else teraz
        n = 0
        for p in self.katalog.glob("*.npz"):
            try:
                wiek = teraz - p.stat().st_mtime
                if wiek > dni * 86400 or (".tmp" in p.name and wiek > 86400):
                    p.unlink()
                    n += ".tmp" not in p.name
            except OSError:
                continue
        return n
