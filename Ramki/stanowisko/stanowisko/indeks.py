"""indeks - indeks folderow zlecen "Cyrkon" i "Prywatne" w bazie: tabele ``zlecenia``, ``projekty``, ``cechy_stl`` (E3-A4).

Struktura (K1, plan wdrozenia v2 "Dane i integracje"): ``<zrodlo>/<folder zlecenia>/*.stl``. Folder = zlecenie (kuweta
z nazwy folderu - ``nazwy``), kazdy plik STL bezposrednio w folderze = punkt pracy (``projekty``: plik, ``sha16`` = 16 znakow
SHA-256 zawartosci, zeby i typ z nazwy, ``mtime_ns``, rozmiar). STL w podfolderach nie sa punktami pracy (liczone
w ``pominiete_podfoldery``); foldery ``_*`` i ``.*`` sa pomijane. Przeniesione z wczesniejszej linii ``qc/catalog/indeks.py``
(H): klucz zmiany pliku (mtime_ns, rozmiar), cechy tylko dla nowych i zmienionych, plik zniknal = ``usuniety = 1``, brak
calego katalogu zrodla (OneDrive niezsynchronizowany) = zrodlo pominiete bez oznaczania usuniec, folder nieczytelny = blad
bez oznaczania usuniec, foldery starsze niz ``usun_z_puli_po_dniach`` pomijane (archiwum "Cyrkon" nie jest czytane co dzien).
Nowe wzgledem H: cechy (``cechy_stl``) kluczowane skrotem pliku - ten sam plik w innym folderze nie jest liczony drugi raz;
plik bez skrotu albo bez cech (zablokowany, uszkodzony) jest probowany przy kazdym przebiegu; siatka wczytywana z bajtow
(skrot i cechy z tej samej tresci; biblioteki nie widza nazwy pliku); zapis kazdego folderu w krotkiej transakcji
(cechy liczone przed nia - baza nie jest blokowana na czas liczenia).

DANE OSOBOWE (DW2 po decyzji z 17.11.2026): nazwa folderu trafia tylko do ``zlecenia.folder`` / ``folder_norm`` (doslownie,
takze w postaci NFD - inaczej nie dalo sie zbudowac sciezki), nazwa pliku do ``projekty.plik``. Raport, dziennik
(``zdarzenia``) i bledy podaja tylko liczby i identyfikatory wierszy; wyjatki odczytu (z sciezka) sa zamieniane na liczniki,
ostrzezenia bibliotek przy wczytywaniu siatki sa wyciszane. Opis: ``opisy_modulow/pula.md``.
"""
from __future__ import annotations

import collections
import datetime as dt
import hashlib
import io
import os
import time
import warnings
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import baza as B
from . import nazwy as N

ZRODLA = ("cyrkon", "prywatne")
KLUCZE_ZRODEL = {"cyrkon": "folder_cyrkon", "prywatne": "folder_prywatne"}  # [sciezki] w ustawienia.toml
WERSJA_CECH = 1  # podniesienie = cechy liczone od nowa dla kazdego pliku przy nastepnym przebiegu
USUN_PO_DNIACH = 10  # [match] usun_z_puli_po_dniach
MINIATURA_PX = 64
_KOLUMNY_CECH = ("trojkaty", "szczelny", "objetosc_mm3", "hull_mm3", "pole_mm2", "obrys_a_mm", "obrys_b_mm", "wysokosc_mm")


@dataclass
class RaportIndeksu:
    """Wynik przebiegu indeksu - same liczby i identyfikatory wierszy (bez nazw)."""
    zrodla: dict = field(default_factory=dict)  # zrodlo -> "ok" / "brak katalogu" / "blad odczytu"
    zlecen: int = 0  # foldery zlecen przejrzane w tym przebiegu (bez starych)
    zlecenia_nowe: int = 0
    zlecenia_usuniete: int = 0
    bez_kuwety: int = 0
    pominiete_stare: int = 0  # foldery starsze niz usun_po_dniach (nie czytane, nie usuwane)
    nowe: int = 0
    zmienione: int = 0
    usuniete: int = 0
    bez_zmian: int = 0
    cechy_policzone: int = 0
    cechy_z_pamieci: int = 0  # plik nowy albo zmieniony, ale jego zawartosc ma juz cechy w bazie
    bledy: int = 0
    bledne_projekty: list = field(default_factory=list)  # id wierszy ``projekty`` bez skrotu albo bez cech po bledzie
    pominiete_podfoldery: int = 0  # pliki STL w podfolderach folderow zlecen (nie sa punktami pracy)
    czas_s: float = 0.0

    def do_slownika(self) -> dict:
        return asdict(self)


def zrodla_z_ustawien(ust: dict) -> dict[str, Path]:
    """Katalogi zrodel z ``[sciezki] folder_cyrkon`` i ``folder_prywatne`` (wzgledne liczone od katalogu programu)."""
    return {zrodlo: B.sciezka_z_ustawien(ust, klucz) for zrodlo, klucz in KLUCZE_ZRODEL.items()}


def _czytaj_plik(p: str | Path) -> bytes:
    return Path(p).read_bytes()


def skrot(dane: bytes) -> str:
    """Identyfikator projektu: 16 znakow SHA-256 zawartosci (jak ``synth.skrot_pliku``)."""
    return hashlib.sha256(dane).hexdigest()[:16]


def siatka_z_bajtow(dane: bytes):
    """Siatka STL z bajtow - te same kontrole co ``synth.wczytaj_projekt`` (trojkaty, liczby skonczone, pole > 0), ale bez
    nazwy pliku w ostrzezeniach i wyjatkach. Zly plik = ``ValueError`` z opisem bez nazwy."""
    import numpy as np
    import trimesh

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            m = trimesh.load(io.BytesIO(dane), file_type="stl", force="mesh", process=False)
        except Exception as e:  # noqa: BLE001 - kazdy blad odczytu = plik bez siatki
            raise ValueError(f"nie da sie wczytac siatki ({type(e).__name__})") from None
        if not isinstance(m, trimesh.Trimesh) or len(m.faces) == 0:
            raise ValueError("brak trojkatow")
        if not np.isfinite(m.vertices).all():
            raise ValueError("NaN albo nieskonczonosc we wierzcholkach")
        if not m.area > 0:
            raise ValueError("zerowa powierzchnia")
        m.process()
    return m


def cechy_siatki(m, nazwa: str) -> dict:
    """Kolumny ``cechy_stl`` (bez ``sha16``, miniatury i czasu) - te same wartosci co ``katalog.cechy`` (pola ``Projekt``)."""
    from . import katalog as K

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        c = K.cechy(m, nazwa)
    return {"trojkaty": int(c.trojkaty), "szczelny": int(bool(c.szczelna)), "objetosc_mm3": float(c.objetosc_mm3),
            "hull_mm3": float(c.hull_mm3), "pole_mm2": float(c.pole_mm2), "obrys_a_mm": float(c.obrys_xy_mm[0]),
            "obrys_b_mm": float(c.obrys_xy_mm[1]), "wysokosc_mm": float(c.wysokosc_mm)}


def miniatura_png(m, nazwa: str = "", px: int = MINIATURA_PX) -> bytes | None:
    """Miniatura projektu (PNG ``px`` x ``px``, skala szarosci): widok od strony zujacej (brzeg z dala od patrzacego), jasniej =
    blizej. Bez biblioteki Pillow (``requirements.txt``) - None."""
    try:
        import numpy as np
        import trimesh
        from PIL import Image

        from . import synth as S
    except ImportError:
        return None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        O = S.orientacja_brzegiem_do_gory(m, "auto", nazwa)
    V = trimesh.transform_points(np.asarray(m.vertices), O)  # brzeg na gorze: strona zujaca na dole (najmniejsze z)
    xy = V[:, :2] - V[:, :2].min(axis=0)
    zakres = float(xy.max()) or 1.0
    xy += (zakres - xy.max(axis=0)) / 2  # wysrodkowanie krotszego boku
    ij = np.clip(np.round(xy / zakres * (px - 1)).astype(int), 0, px - 1)
    wys = V[:, 2].max() - V[:, 2] + 1e-6  # strona zujaca = najwieksza wartosc
    obraz = np.zeros((px, px))
    np.maximum.at(obraz, (px - 1 - ij[:, 1], ij[:, 0]), wys)
    zajete = obraz > 0
    obraz[zajete] = 40 + 215 * obraz[zajete] / obraz.max()
    bufor = io.BytesIO()
    Image.fromarray(obraz.astype(np.uint8), "L").save(bufor, format="PNG", optimize=True)
    return bufor.getvalue()


def _policz_stl(katalog: str) -> int:
    n = 0
    for _, _, pliki in os.walk(katalog, onerror=lambda e: None):
        n += sum(p.lower().endswith(".stl") for p in pliki)
    return n


def _wpisy_folderu(sciezka: str) -> tuple[list[tuple[str, int, int]], int]:
    """(pliki STL bezposrednio w folderze jako (nazwa, mtime_ns, rozmiar), liczba STL w podfolderach). ``OSError`` przechodzi
    dalej (folder nieczytelny - wywolujacy liczy blad, nie oznacza usuniec)."""
    pliki, w_podfolderach = [], 0
    with os.scandir(sciezka) as wpisy:
        for p in wpisy:
            if p.is_dir():
                w_podfolderach += _policz_stl(p.path)
            elif p.is_file() and p.name.lower().endswith(".stl") and not p.name.startswith((".", "~")):
                st = p.stat()
                pliki.append((p.name, st.st_mtime_ns, st.st_size))
    return sorted(pliki), w_podfolderach


def indeksuj(baza: B.Baza, zrodla: dict[str, str | Path | None], teraz: dt.datetime | None = None, *,
             usun_po_dniach: int = USUN_PO_DNIACH, licz_cechy: bool = True, miniatury: bool = True) -> RaportIndeksu:
    """Synchronizuje tabele indeksu z folderami ``zrodla`` (zrodlo -> katalog, np. ``zrodla_z_ustawien(ust)``).

    ``teraz`` (czas zapisu i granica wieku folderow, domyslnie teraz); ``usun_po_dniach``: folder, w ktorym od tylu dni nic
    sie nie zmienilo (folder i pliki STL), nie jest czytany ani oznaczany jako usuniety; ``licz_cechy=False``: same skroty
    (cechy policzy nastepny przebieg z ``licz_cechy=True``). Trwa: cechy nowego pliku to ok. 0,1-1 s - w programie wolac
    w watku roboczym z wlasnym polaczeniem z baza. Wpis w dzienniku: ``pula / indeks`` z liczbami.
    """
    teraz = teraz or dt.datetime.now()
    t0 = time.perf_counter()
    r = RaportIndeksu()
    granica = teraz.timestamp() - usun_po_dniach * 86400
    czas = teraz.replace(microsecond=0).isoformat()
    cechy_znane = {w["sha16"]: w["wersja_cech"] or 0 for w in baza.wiersze("SELECT sha16, wersja_cech FROM cechy_stl")}
    for zrodlo, katalog in zrodla.items():
        if katalog is None or not Path(katalog).is_dir():
            r.zrodla[zrodlo] = "brak katalogu"
            continue
        try:
            with os.scandir(katalog) as wpisy:
                foldery = sorted((e for e in wpisy if e.is_dir() and not e.name.startswith(("_", "."))), key=lambda e: e.name)
        except OSError:
            r.zrodla[zrodlo] = "blad odczytu"
            r.bledy += 1
            continue
        r.zrodla[zrodlo] = "ok"
        znane = {w["folder"]: w for w in baza.wiersze("SELECT * FROM zlecenia WHERE zrodlo = ?", (zrodlo,))}
        widziane = set()
        for e in foldery:
            widziane.add(e.name)  # takze folder nieczytelny i stary: nie jest usuniety
            try:
                pliki, w_podfolderach = _wpisy_folderu(e.path)
                zmieniono = max([e.stat().st_mtime] + [m / 1e9 for _, m, _ in pliki])
            except OSError:
                r.bledy += 1
                continue
            if zmieniono < granica:
                r.pominiete_stare += 1
                continue
            r.zlecen += 1
            r.pominiete_podfoldery += w_podfolderach
            _folder(baza, r, zrodlo, Path(e.path), e.name, znane.get(e.name), pliki, zmieniono, czas, cechy_znane, licz_cechy, miniatury)
        for folder, w in znane.items():
            if folder not in widziane and not w["usuniety"]:
                with baza.transakcja():
                    r.usuniete += baza.wykonaj("UPDATE projekty SET usuniety = 1 WHERE zlecenie_id = ? AND usuniety = 0", (w["id"],)).rowcount
                    baza.wykonaj("UPDATE zlecenia SET usuniety = 1 WHERE id = ?", (w["id"],))
                r.zlecenia_usuniete += 1
    r.czas_s = round(time.perf_counter() - t0, 2)
    baza.zdarzenie("pula", "indeks", r.do_slownika())
    return r


def _folder(baza: B.Baza, r: RaportIndeksu, zrodlo: str, sciezka: Path, nazwa: str, zl: dict | None, pliki: list, zmieniono: float,
            czas: str, cechy_znane: dict, licz_cechy: bool, miniatury: bool) -> None:
    """Jeden folder zlecenia: najpierw odczyt i cechy (bez blokady bazy), potem zapis w krotkiej transakcji."""
    info = N.rozbierz(nazwa)
    if info.kuweta is None:
        r.bez_kuwety += 1
    znane = {w["plik"]: w for w in baza.wiersze("SELECT * FROM projekty WHERE zlecenie_id = ?", (zl["id"],))} if zl else {}
    do_zapisu = []  # (plik, mtime_ns, rozmiar, stary, sha16, cechy, blad)
    for plik, mtime_ns, rozmiar in pliki:
        stary = znane.get(plik)
        bez_zmian = stary is not None and not stary["usuniety"] and stary["mtime_ns"] == mtime_ns and stary["rozmiar"] == rozmiar
        brak_cech = stary is not None and (stary["sha16"] is None or (licz_cechy and cechy_znane.get(stary["sha16"], -1) < WERSJA_CECH))
        if bez_zmian:
            r.bez_zmian += 1
            if not brak_cech:
                continue
        elif stary is None:
            r.nowe += 1
        else:
            r.zmienione += 1
        sha16, cechy, blad = None, None, False
        try:
            dane = _czytaj_plik(sciezka / plik)
        except OSError:
            blad = True
        else:
            sha16 = skrot(dane)
            if licz_cechy and cechy_znane.get(sha16, -1) < WERSJA_CECH:
                try:
                    m = siatka_z_bajtow(dane)
                    cechy = cechy_siatki(m, plik)
                    cechy["miniatura"] = miniatura_png(m, plik) if miniatury else None
                except Exception:  # noqa: BLE001 - uszkodzony STL, brak pamieci: plik zostaje bez cech, przebieg idzie dalej
                    blad = True
                else:
                    cechy_znane[sha16] = WERSJA_CECH
                    r.cechy_policzone += 1
            elif not bez_zmian:
                r.cechy_z_pamieci += licz_cechy
        r.bledy += blad
        do_zapisu.append((plik, mtime_ns, rozmiar, stary, sha16, cechy, blad))
    obecne = {p for p, _, _ in pliki}
    znikniete = [w["id"] for p, w in znane.items() if p not in obecne and not w["usuniety"]]
    zlecenie_bez_zmian = (zl is not None and not zl["usuniety"] and zl["kuweta"] == info.kuweta and zl["folder_norm"] == info.folder_norm
                          and zl["mtime"] is not None and abs(zl["mtime"] - zmieniono) < 1e-6)
    if zlecenie_bez_zmian and not do_zapisu and not znikniete:
        return
    with baza.transakcja():
        if zl is None:
            zid = baza.wstaw("zlecenia", zrodlo=zrodlo, folder=nazwa, folder_norm=info.folder_norm, kuweta=info.kuweta, mtime=zmieniono,
                             dodano=czas, usuniety=0)
            r.zlecenia_nowe += 1
        else:
            zid = zl["id"]
            baza.wykonaj("UPDATE zlecenia SET folder_norm = ?, kuweta = ?, mtime = ?, usuniety = 0 WHERE id = ?",
                         (info.folder_norm, info.kuweta, zmieniono, zid))
            r.zlecenia_nowe += bool(zl["usuniety"])
        for plik, mtime_ns, rozmiar, stary, sha16, cechy, blad in do_zapisu:
            zeby, typ = N.zeby_i_typ(plik)
            if stary is None:
                pid = baza.wstaw("projekty", zlecenie_id=zid, plik=plik, sha16=sha16, zeby=zeby, typ=typ, mtime_ns=mtime_ns, rozmiar=rozmiar,
                                 zaindeksowano=czas, usuniety=0)
            else:
                pid = stary["id"]
                baza.wykonaj("UPDATE projekty SET sha16 = ?, zeby = ?, typ = ?, mtime_ns = ?, rozmiar = ?, zaindeksowano = ?, usuniety = 0 "
                             "WHERE id = ?", (sha16, zeby, typ, mtime_ns, rozmiar, czas, pid))
            if cechy is not None:
                baza.wykonaj(f"INSERT OR REPLACE INTO cechy_stl (sha16, {', '.join(_KOLUMNY_CECH)}, miniatura, wersja_cech, policzono) "
                             f"VALUES (?, {', '.join('?' * len(_KOLUMNY_CECH))}, ?, ?, ?)",
                             (sha16, *(cechy[k] for k in _KOLUMNY_CECH), cechy["miniatura"], WERSJA_CECH, czas))
            if blad:
                r.bledne_projekty.append(pid)
        for pid in znikniete:
            baza.wykonaj("UPDATE projekty SET usuniety = 1 WHERE id = ?", (pid,))
        r.usuniete += len(znikniete)


class IndeksPlikow:
    """Pliki indeksu w pamieci do laczenia nazw z raportow i CSV z punktami pracy (projekty i zlecenia nieusuniete).

    ``znajdz(plik, data)`` -> (wiersz albo None, liczba kandydatow). Nazwa z folderem ("Folder/plik.stl", takze z ``\\``
    i z dluzsza sciezka) = dopasowanie konca sciezki ``folder/plik``; sama nazwa pliku = wszystkie pliki o tej nazwie.
    Porownanie bez wielkosci liter, w postaci NFC. Kilku kandydatow: plik o dacie modyfikacji najblizszej ``data``
    (potem nowszy) - jak w H (``pula_wieczor``); wywolujacy liczy to jako "niejednoznaczne". Wiersz zawiera nazwy (pola
    ``plik``, ``folder``) - nie do logow ani wynikow.
    """

    def __init__(self, baza: B.Baza):
        self.po_id: dict[int, dict] = {}
        self.po_nazwie: dict[str, list[dict]] = collections.defaultdict(list)
        for w in baza.wiersze("SELECT p.id, p.plik, p.sha16, p.zeby, p.typ, p.mtime_ns, p.zlecenie_id, z.folder, z.kuweta, z.zrodlo "
                              "FROM projekty p JOIN zlecenia z ON z.id = p.zlecenie_id WHERE p.usuniety = 0 AND z.usuniety = 0 ORDER BY p.id"):
            self.po_id[w["id"]] = w
            self.po_nazwie[N.klucz_pliku(w["plik"])].append(w)

    def kandydaci(self, plik: str) -> list[dict]:
        k = N.klucz_pliku(plik)
        if "/" not in k:
            return list(self.po_nazwie.get(k, ()))
        nazwa = k.rsplit("/", 1)[1]
        wynik = []
        for w in self.po_nazwie.get(nazwa, ()):
            pelna = N.klucz_pliku(f"{w['folder']}/{w['plik']}")
            if pelna == k or pelna.endswith("/" + k) or k.endswith("/" + pelna):
                wynik.append(w)
        return wynik

    def znajdz(self, plik: str, data: dt.date | None = None) -> tuple[dict | None, int]:
        kandydaci = self.kandydaci(plik)
        if not kandydaci:
            return None, 0
        if len(kandydaci) == 1 or data is None:
            return (kandydaci[0] if len(kandydaci) == 1 else max(kandydaci, key=lambda w: (w["mtime_ns"] or 0, w["id"]))), len(kandydaci)

        def odleglosc(w: dict) -> tuple:
            dzien = dt.datetime.fromtimestamp((w["mtime_ns"] or 0) / 1e9).date()
            return abs((dzien - data).days), -(w["mtime_ns"] or 0), w["id"]

        return min(kandydaci, key=odleglosc), len(kandydaci)
