"""Indeks folderow Cyrkon i Prywatne (folder zlecenia / pliki .stl) oraz pule kandydatow rano i wieczorem."""

import os
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path, PurePath

import trimesh

from . import cechy as modul_cechy
from . import nazwy

ZRODLA = ("cyrkon", "prywatne")


@dataclass
class RaportIndeksu:
    nowe: int = 0
    zmienione: int = 0
    usuniete: int = 0


@dataclass(frozen=True)
class Wpis:
    projekt_id: int
    wspolczynnik: float = 1.0


def _pliki_stl(katalog: Path):
    """(sciezka wzgledna z "/", folder, nazwa, os.stat) dla katalog/<folder>/<plik>.stl."""
    with os.scandir(katalog) as foldery:
        for folder in foldery:
            if not folder.is_dir():
                continue
            with os.scandir(folder.path) as pliki:
                for plik in pliki:
                    if plik.is_file() and plik.name.lower().endswith(".stl"):
                        yield f"{folder.name}/{plik.name}", folder.name, plik.name, plik.stat()


def _cechy_pliku(sciezka: Path) -> dict:
    siatka = trimesh.load(sciezka, file_type="stl", process=False)
    siatka.merge_vertices()  # STL ma osobne wierzcholki kazdego trojkata; bez scalenia brak bryly zamknietej
    c = modul_cechy.policz(siatka)
    return dict(objetosc_mm3=c.objetosc_mm3, pole_mm2=c.pole_mm2, wym1_mm=float(c.wymiary_mm[0]),
                wym2_mm=float(c.wymiary_mm[1]), wym3_mm=float(c.wymiary_mm[2]), d2=c.d2)


def skanuj(ustawienia, baza, teraz: datetime) -> RaportIndeksu:
    """Synchronizuje baze z folderami; cechy liczone tylko dla nowych i zmienionych (mtime_ns, rozmiar).

    Brak katalogu zrodla (np. niezsynchronizowany OneDrive) = zrodlo pominiete, bez oznaczania usuniec.
    """
    raport = RaportIndeksu()
    znane = {r["sciezka"]: r for r in baza.projekty(usuniete=True)}
    for zrodlo in ZRODLA:
        katalog = Path(getattr(ustawienia.sciezki, zrodlo))
        if not katalog.is_dir():
            continue
        widziane = set()
        for sciezka, folder, nazwa, st in _pliki_stl(katalog):
            widziane.add(sciezka)
            stary = znane.get(sciezka)
            if stary is not None and stary["zrodlo"] == zrodlo and not stary["usuniety"] \
                    and (stary["mtime_ns"], stary["rozmiar"]) == (st.st_mtime_ns, st.st_size):
                continue
            zlecenie = nazwy.rozbierz(folder)
            rekord = dict(zrodlo=zrodlo, sciezka=sciezka, folder=folder, kuweta=zlecenie.kuweta,
                          nazwisko=zlecenie.nazwisko, numer_zeba=nazwy.numer_zeba(nazwa),
                          mtime_ns=st.st_mtime_ns, rozmiar=st.st_size, zaindeksowano=teraz.isoformat(),
                          usuniety=0, **_cechy_pliku(katalog / folder / nazwa))
            if stary is None:
                baza.dodaj_projekt(rekord)
                raport.nowe += 1
            else:
                baza.zmien_projekt(stary["id"], rekord)
                raport.zmienione += 1
        zniknely = [r["id"] for s, r in znane.items()
                    if r["zrodlo"] == zrodlo and not r["usuniety"] and s not in widziane]
        baza.oznacz_usuniete(zniknely)
        raport.usuniete += len(zniknely)
    return raport


def poczatek_dni_roboczych(dzis: date, dni: int) -> date:
    """Data `dni` dni roboczych przed dzis (sb/nd sie nie licza; weekend nalezy do piatku)."""
    d = dzis
    while dni > 0:
        d -= timedelta(days=1)
        if d.weekday() < 5:
            dni -= 1
    return d


def pula_rano(baza, teraz: datetime, dni: int | None = None) -> list[Wpis]:
    """Projekty z ostatnich `dni` dni roboczych (domyslnie pula.dni_rano) i z dzis; k = 1,0."""
    if dni is None:
        from qc.ustawienia import wczytaj

        dni = wczytaj().pula.dni_rano
    od = datetime.combine(poczatek_dni_roboczych(teraz.date(), dni), time())
    return [Wpis(r["id"]) for r in baza.projekty(od=od)]


def _klucz_pliku(nazwa: str) -> str:
    return PurePath(nazwa.replace("\\", "/")).name.casefold()


def pula_wieczor(baza, wspolczynniki, teraz: datetime, dni: int = 2) -> tuple[list[Wpis], int]:
    """Projekty z CSV z ostatnich `dni` dni kalendarzowych (dzis wlacznie) z k z CSV.

    STL z CSV szukany po nazwie pliku (bez wielkosci liter); przy kilku trafieniach najnowszy.
    Zwraca (wpisy, liczba STL z CSV nieobecnych w bazie).
    """
    od = teraz.date() - timedelta(days=dni - 1)
    po_nazwie: dict[str, dict] = {}
    for r in baza.projekty():
        klucz = _klucz_pliku(r["sciezka"])
        if klucz not in po_nazwie or r["mtime_ns"] > po_nazwie[klucz]["mtime_ns"]:
            po_nazwie[klucz] = r
    wpisy, brakujace = [], 0
    for w in wspolczynniki:
        if not od <= w.data <= teraz.date():
            continue
        r = po_nazwie.get(_klucz_pliku(w.plik_stl))
        if r is None:
            brakujace += 1
        else:
            wpisy.append(Wpis(r["id"], float(w.wspolczynnik)))
    return wpisy, brakujace
