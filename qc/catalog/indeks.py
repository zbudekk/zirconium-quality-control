"""Indeks folderow Cyrkon i Prywatne (folder zlecenia / pliki .stl) oraz pule kandydatow rano i wieczorem."""

import os
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from pathlib import Path

import trimesh

from . import cechy as modul_cechy
from . import nazwy

ZRODLA = ("cyrkon", "prywatne")
BEZ_CECH = dict(objetosc_mm3=None, pole_mm2=None, wym1_mm=None, wym2_mm=None, wym3_mm=None, d2=None)


@dataclass
class RaportIndeksu:
    nowe: int = 0
    zmienione: int = 0
    usuniete: int = 0
    bledy: int = 0
    bledne: list[str] = field(default_factory=list)  # pliki (foldery z "/" na koncu) nie wczytane


@dataclass(frozen=True)
class Wpis:
    projekt_id: int
    wspolczynnik: float = 1.0


class PulaWieczor(tuple):
    """Krotka (wpisy, brakujace) z atrybutami wpisy, brakujace, niejednoznaczne."""

    def __new__(cls, wpisy: list[Wpis], brakujace: int, niejednoznaczne: int):
        obiekt = super().__new__(cls, (wpisy, brakujace))
        obiekt.niejednoznaczne = niejednoznaczne
        return obiekt

    @property
    def wpisy(self) -> list[Wpis]:
        return self[0]

    @property
    def brakujace(self) -> int:
        return self[1]


def _ns(chwila: datetime) -> int:
    return int(chwila.timestamp() * 1e9)


def _data_pliku(mtime_ns: int) -> date:
    return datetime.fromtimestamp(mtime_ns / 1e9).date()


def _pula(ustawienia):
    if ustawienia is None:
        from qc.ustawienia import wczytaj

        ustawienia = wczytaj()
    return ustawienia.pula


def _pliki_stl(katalog: Path, raport: RaportIndeksu, nieczytelne: list[str]):
    """(sciezka wzgledna z "/", folder, nazwa, os.stat) dla katalog/<folder>/<plik>.stl.

    Folder, ktorego nie da sie odczytac, trafia do bledow i do `nieczytelne` (bez oznaczania usuniec).
    """
    with os.scandir(katalog) as foldery:
        for folder in foldery:
            if not folder.is_dir():
                continue
            try:
                with os.scandir(folder.path) as pliki:
                    wpisy = [(p.name, p.stat()) for p in pliki
                             if p.is_file() and p.name.lower().endswith(".stl")]
            except OSError:
                raport.bledy += 1
                raport.bledne.append(folder.name + "/")
                nieczytelne.append(folder.name + "/")
                continue
            for nazwa, st in wpisy:
                yield f"{folder.name}/{nazwa}", folder.name, nazwa, st


def _cechy_pliku(sciezka: Path) -> dict:
    siatka = trimesh.load(sciezka, file_type="stl", process=False)
    if not isinstance(siatka, trimesh.Trimesh) or len(siatka.faces) == 0:
        raise ValueError(f"plik nie zawiera siatki trojkatow: {type(siatka).__name__}")
    siatka.merge_vertices()  # STL ma osobne wierzcholki kazdego trojkata; bez scalenia brak bryly zamknietej
    c = modul_cechy.policz(siatka)
    return dict(objetosc_mm3=c.objetosc_mm3, pole_mm2=c.pole_mm2, wym1_mm=float(c.wymiary_mm[0]),
                wym2_mm=float(c.wymiary_mm[1]), wym3_mm=float(c.wymiary_mm[2]), d2=c.d2)


def skanuj(ustawienia, baza, teraz: datetime) -> RaportIndeksu:
    """Synchronizuje baze z folderami; cechy liczone tylko dla nowych i zmienionych (mtime_ns, rozmiar).

    Pliki starsze niz pula.usuwaj_po_dniach sa pomijane (nie wracaja po usun_starsze_niz). Plik, ktorego
    nie da sie wczytac, dostaje rekord bez cech i trafia do raport.bledne; ponowna proba po jego zmianie.
    Brak katalogu zrodla (np. niezsynchronizowany OneDrive) = zrodlo pominiete, bez oznaczania usuniec.
    """
    raport = RaportIndeksu()
    granica_ns = _ns(teraz - timedelta(days=ustawienia.pula.usuwaj_po_dniach))
    znane = {(r["zrodlo"], r["sciezka"]): r for r in baza.projekty(usuniete=True)}
    for zrodlo in ZRODLA:
        katalog = Path(getattr(ustawienia.sciezki, zrodlo))
        if not katalog.is_dir():
            continue
        widziane: set[str] = set()
        nieczytelne: list[str] = []
        for sciezka, folder, nazwa, st in _pliki_stl(katalog, raport, nieczytelne):
            widziane.add(sciezka)
            stary = znane.get((zrodlo, sciezka))
            klucz = (st.st_mtime_ns, st.st_size)
            if stary is not None and not stary["usuniety"] and (stary["mtime_ns"], stary["rozmiar"]) == klucz:
                continue
            if st.st_mtime_ns < granica_ns:
                continue
            try:
                wartosci = _cechy_pliku(katalog / folder / nazwa)
            except Exception:  # uszkodzony STL, plik zablokowany, brak pamieci - skan idzie dalej
                wartosci = BEZ_CECH
                raport.bledy += 1
                raport.bledne.append(sciezka)
            zlecenie = nazwy.rozbierz(folder)
            rekord = dict(zrodlo=zrodlo, sciezka=sciezka, folder=folder, kuweta=zlecenie.kuweta,
                          nazwisko=zlecenie.nazwisko, numer_zeba=nazwy.numer_zeba(nazwa),
                          mtime_ns=st.st_mtime_ns, rozmiar=st.st_size, zaindeksowano=teraz.isoformat(),
                          usuniety=0, **wartosci)
            if stary is None:
                baza.dodaj_projekt(rekord)
                raport.nowe += 1
            else:
                baza.zmien_projekt(stary["id"], rekord)
                raport.zmienione += 1
        zniknely = [r["id"] for (z, s), r in znane.items()
                    if z == zrodlo and not r["usuniety"] and s not in widziane
                    and not s.startswith(tuple(nieczytelne))]
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


def pula_rano(baza, teraz: datetime, dni: int | None = None, ustawienia=None) -> list[Wpis]:
    """Projekty z ostatnich `dni` dni roboczych (domyslnie pula.dni_rano) i z dzis; k = 1,0."""
    if dni is None:
        dni = _pula(ustawienia).dni_rano
    od = datetime.combine(poczatek_dni_roboczych(teraz.date(), dni), time())
    return [Wpis(r["id"]) for r in baza.projekty(od=od)]


def _sciezka_csv(plik: str) -> str:
    return plik.replace("\\", "/").strip("/").casefold()


def _pasuje_sciezka(sciezka_bazy: str, sciezka_csv: str) -> bool:
    """Koniec sciezki: "Folder/36.stl" z CSV pasuje do sciezki wzglednej (pelna sciezka z CSV tez)."""
    a = sciezka_bazy.casefold()
    return a == sciezka_csv or a.endswith("/" + sciezka_csv) or sciezka_csv.endswith("/" + a)


def pula_wieczor(baza, wspolczynniki, teraz: datetime, dni: int | None = None,
                 ustawienia=None) -> PulaWieczor:
    """Projekty z CSV z ostatnich `dni` dni kalendarzowych (dzis wlacznie, domyslnie pula.dni_wieczor).

    Plik z folderem ("Folder/36.stl", tez z "\\") = dopasowanie konca sciezki wzglednej. Sama nazwa pliku =
    kandydaci z mtime w oknie (+1 dzien zapasu). Przy kilku kandydatach wybierany najblizszy dacie z CSV
    i liczony w `niejednoznaczne`; brak kandydata = `brakujace`.
    """
    if dni is None:
        dni = _pula(ustawienia).dni_wieczor
    dzis = teraz.date()
    od = dzis - timedelta(days=dni - 1)
    od_mtime = od - timedelta(days=1)
    projekty = baza.projekty()
    wpisy, brakujace, niejednoznaczne = [], 0, 0
    for w in wspolczynniki:
        if not od <= w.data <= dzis:
            continue
        sciezka = _sciezka_csv(w.plik_stl)
        if "/" in sciezka:
            kandydaci = [r for r in projekty if _pasuje_sciezka(r["sciezka"], sciezka)]
        else:
            kandydaci = [r for r in projekty if r["sciezka"].rsplit("/", 1)[-1].casefold() == sciezka
                         and _data_pliku(r["mtime_ns"]) >= od_mtime]
        if not kandydaci:
            brakujace += 1
            continue
        if len(kandydaci) > 1:
            niejednoznaczne += 1
        wybrany = min(kandydaci, key=lambda r: (abs((_data_pliku(r["mtime_ns"]) - w.data).days),
                                                -r["mtime_ns"]))
        wpisy.append(Wpis(wybrany["id"], float(w.wspolczynnik)))
    return PulaWieczor(wpisy, brakujace, niejednoznaczne)
