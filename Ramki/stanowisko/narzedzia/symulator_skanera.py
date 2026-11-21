"""symulator_skanera - wrzuca sztuczne skany do folderu tak, jak robilby to program skanera (paczka E3-A2).

Po co: skanera jeszcze nie ma, a modul ``scanner`` (obserwacja folderu) i ``silnik`` (analiza w osobnym procesie) trzeba
zbudowac i zmierzyc. Symulator zapisuje pliki W KAWALKACH z przerwami (zapis trwa np. 1-5 s), kilka naraz albo co zadany
odstep, i dorzuca pliki zle: uciety, pusty, nie-STL, z niezgodnym naglowkiem, za krotki, STL tekstowy, inne rozszerzenie.
To NIE jest opis prawdziwego skanera: nazwy plikow (``--wzor-nazwy``), sposob zapisu (``--tryb``) i czasy sa parametrami.

Uzycie (z katalogu stanowisko/):
    py -3.12 narzedzia/symulator_skanera.py --folder FOLDER [--zrodla SKAN.stl|KATALOG ...] [--ile N] [--czas 1 5]
        [--kawalki 5 20] [--rownolegle 4] [--odstep 0] [--zle uciety pusty ...] [--seed 0] [--wzor-nazwy "skan_{nr:04d}.stl"]
        [--tryb wprost|dopisywanie|tymczasowy|wylaczny] [--dziennik PLIK.json]
        [--pomiar [--stabilizacja-ms 300] [--odrzuc-po 5]]                 obserwuj folder modulem scanner i policz opoznienia
        [--analiza --projekty FOLDER ... [--wyjscie FOLDER] [--ustawienia PLIK]]   dodatkowo analizuj kazdy skan silnikiem
        [--generuj UKLAD:NUMER:ZIARNO[:bez_ubytkow] ... --katalog-generowanych KATALOG [--projekty FOLDER ...]]
        [--scenariusz PLIK.json --katalog-generowanych KATALOG [--projekty FOLDER ...]] [--tylko-generuj]

Bez ``--zrodla`` symulator sam tworzy male poprawne pliki binarnego STL (losowe trojkaty - dobre do proby obserwatora,
nie do analizy). Z ``--pomiar`` wypisuje liczniki (zdarzen / zapisow, ile zdarzen przed koncem zapisu, mediana opoznienia,
odrzucenia z powodami) i konczy kodem 0 tylko wtedy, gdy kazdy dobry plik dal dokladnie jedno zdarzenie po koncu zapisu,
a kazdy zly - zero zdarzen i wpis z powodem. Z ``--analiza`` dochodza wyniki silnika (czas od konca zapisu do startu
analizy, czas plytki, statusy gniazd) i pliki ``<czas przyjecia>_<sha16>[_n]_wynik.json`` (bez nazwy skanu) w ``--wyjscie``.
``--tryb wylaczny`` (tylko Windows) zapisuje plik bez zgody na wspoldzielenie - obserwator czeka wtedy na zwolnienie pliku
(``Oczekiwanie`` po 10 s, liczone w ``--pomiar``). Na koncu zatrzymuje najpierw obserwator, potem silnik (kolejnosc jak
w oknie aplikacji: zadne zlecenie w trakcie ``Silnik.stop()``).

Skany plytek generowane (E3-O3; plytki okragle ramkowe n1-n6 nie maja jeszcze prawdziwych skanow ani skanow w danych
odniesienia): ``--generuj okragla_ramkowa_wieczorna:1:5801`` tworzy sztuczny skan plytki generatorem programu
(``synth.generuj_plytke`` - ten sam, ktorym powstaly dane odniesienia: pole fi 100 mm, losowa poza skanera, skala 1,22
wieczorem i 1,0 rano, bez drgniec; ``:bez_ubytkow`` = prace cale) w ``--katalog-generowanych`` (POZA repozytorium) jako
``skan_<uklad>_n<numer>_s<ziarno>.stl`` + ``.json`` (prawda generatora) i dopisuje go do plikow zrodlowych - symulator podaje
go potem jak kazdy inny skan. Prace: pliki STL z ``--projekty`` (kolejnosc alfabetyczna; ta sama pula i to samo ziarno = ten
sam plik bajt w bajt), a bez ``--projekty`` trzy atrapy koron. ``--scenariusz`` generuje pozycje scenariusza T2 z polem
``generuj`` (``Ramki/etap3/odbior_koncowy/narzedzia/t2_scenariusz_okragle.json``) i porownuje kazda z tabela prawdy i ``sha16``
scenariusza; ``--tylko-generuj`` konczy po generowaniu (``--folder`` nie jest wtedy potrzebny): kod 0 = wszystkie pozycje
zgodne ze scenariuszem, 1 = roznica (np. inna pula projektow niz ta, z ktorej liczono scenariusz). Plik, ktory juz jest w
katalogu, nie jest generowany od nowa - jest sprawdzany. Ustawienia generatora: ``--ustawienia`` albo wzor programu.

Funkcje dla testow: ``sztuczny_stl``, ``zly_plik``, ``zapisz_jak_skaner``, ``symuluj``, ``statystyki``,
``generuj_skan_plytki``, ``tabela_prawdy``, ``generuj_ze_scenariusza``.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import random
import statistics
import struct
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

RODZAJE_ZLYCH = ("uciety", "pusty", "nie_stl", "zly_naglowek", "za_krotki", "stl_tekstowy", "inne_rozszerzenie")
TRYBY = ("wprost", "dopisywanie", "tymczasowy", "wylaczny")
BLOK = 1024 * 1024


def skrot16(dane: bytes) -> str:
    return hashlib.sha256(dane).hexdigest()[:16]


def sztuczny_stl(trojkaty: int = 500, seed: int = 0) -> bytes:
    """Poprawny binarny STL z losowymi trojkatami (rozmiar = 84 + 50 x liczba trojkatow). Naglowek nie zaczyna sie od "solid"."""
    rng = random.Random(seed)
    cz = [f"sztuczny skan symulatora, seed {seed}".encode("ascii").ljust(80, b" ")[:80], struct.pack("<I", trojkaty)]
    for _ in range(trojkaty):
        x, y, z = rng.uniform(-50, 50), rng.uniform(-50, 50), rng.uniform(0, 10)
        w = [(x + rng.uniform(-0.2, 0.2), y + rng.uniform(-0.2, 0.2), z + rng.uniform(-0.2, 0.2)) for _ in range(3)]
        cz.append(struct.pack("<12fH", 0.0, 0.0, 1.0, *w[0], *w[1], *w[2], 0))
    return b"".join(cz)


def zly_plik(rodzaj: str, dobry: bytes) -> bytes:
    """Zawartosc pliku zlego danego rodzaju, zrobiona z poprawnego binarnego STL ``dobry``."""
    if rodzaj == "uciety":
        return dobry[: max(85, int(len(dobry) * 0.6))]
    if rodzaj == "pusty":
        return b""
    if rodzaj == "nie_stl":
        return b"To nie jest plik STL, tylko zwykly tekst zapisany z rozszerzeniem stl.\r\n" * 8
    if rodzaj == "zly_naglowek":
        n = struct.unpack("<I", dobry[80:84])[0]
        return dobry[:80] + struct.pack("<I", n + 7) + dobry[84:]
    if rodzaj == "za_krotki":
        return dobry[:40]
    if rodzaj == "stl_tekstowy":
        sciana = "facet normal 0 0 1\n outer loop\n  vertex 0 0 0\n  vertex 1 0 0\n  vertex 0 1 0\n endloop\nendfacet\n"
        return ("solid symulator\n" + sciana * 6 + "endsolid symulator\n").encode("ascii")
    if rodzaj == "inne_rozszerzenie":
        return dobry
    raise ValueError(f"rodzaj pliku zlego: {rodzaj!r} (dozwolone: {', '.join(RODZAJE_ZLYCH)})")


def _kawalki(zrodlo, ile: int):
    """Kolejne kawalki zawartosci (``bytes`` albo plik) - ``ile`` mniej wiecej rownych czesci."""
    if isinstance(zrodlo, (bytes, bytearray)):
        n = len(zrodlo)
        krok = max(1, -(-n // ile))
        for i in range(0, n, krok):
            yield bytes(zrodlo[i:i + krok])
        return
    n = os.stat(zrodlo).st_size
    krok = max(1, -(-n // ile))
    with open(zrodlo, "rb") as f:
        while True:
            blok = f.read(krok)
            if not blok:
                return
            yield blok


def otworz_wylacznie(plik, zapis: bool):
    """Windows: plik otwarty BEZ zgody na wspoldzielenie - dopoki uchwyt zyje, zaden inny program nie otworzy tego pliku
    nawet do odczytu (tak domyslnie otwieraja pliki np. ``File.Create`` / ``File.OpenWrite`` w .NET; tak tez moze trzymac
    plik podglad w programie skanera albo antywirus). ``zapis``: nowy plik do zapisu; inaczej istniejacy plik do odczytu."""
    if os.name != "nt":
        raise NotImplementedError("uchwyt wylaczny (bez wspoldzielenia) jest dostepny tylko na Windows")
    import ctypes
    import msvcrt
    from ctypes import wintypes

    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    k.CreateFileW.restype = wintypes.HANDLE
    uchwyt = k.CreateFileW(str(plik), 0x40000000 if zapis else 0x80000000, 0, None, 2 if zapis else 3, 0, None)  # GENERIC_WRITE / READ; CREATE_ALWAYS / OPEN_EXISTING
    if uchwyt is None or uchwyt == wintypes.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    return os.fdopen(msvcrt.open_osfhandle(uchwyt, (0 if zapis else os.O_RDONLY) | getattr(os, "O_BINARY", 0)), "wb" if zapis else "rb")


def zapisz_jak_skaner(zrodlo, cel, czas_s: float = 1.0, kawalki: int = 10, tryb: str = "wprost", trzymaj_s: float = 0.0) -> dict:
    """Zapisuje ``zrodlo`` (``bytes`` albo sciezka pliku) do ``cel`` w ``kawalki`` czesciach rozlozonych na ``czas_s`` sekund.

    ``tryb``: ``wprost`` - plik otwarty przez caly zapis; ``dopisywanie`` - plik zamykany po kazdym kawalku;
    ``tymczasowy`` - zapis do ``<cel>.tmp`` i zmiana nazwy na koncu; ``wylaczny`` - jak ``wprost``, ale plik otwarty bez zgody
    na wspoldzielenie (``otworz_wylacznie``; tylko Windows). ``trzymaj_s``: tyle po ostatnim kawalku plik jest
    jeszcze trzymany otwarty. Zwraca opis zapisu: ``plik``, ``start``, ``koniec`` (time.time() PO zamknieciu pliku), ``rozmiar``,
    ``sha16``, ``mtime_ns``.
    """
    if tryb not in TRYBY:
        raise ValueError(f"tryb: {tryb!r} (dozwolone: {', '.join(TRYBY)})")
    cel = Path(cel)
    cel.parent.mkdir(parents=True, exist_ok=True)
    kawalki = max(1, int(kawalki))
    przerwa = czas_s / (kawalki - 1) if kawalki > 1 else czas_s
    h = hashlib.sha256()
    rozmiar = 0
    t0 = time.time()
    czesci = _kawalki(zrodlo, kawalki)
    if tryb == "dopisywanie":
        for i, blok in enumerate(czesci):
            if i:
                time.sleep(przerwa)
            with open(cel, "ab" if i else "wb") as f:
                f.write(blok)
            h.update(blok)
            rozmiar += len(blok)
        if rozmiar == 0:
            cel.write_bytes(b"")
    else:
        roboczy = cel.with_name(cel.name + ".tmp") if tryb == "tymczasowy" else cel
        with (otworz_wylacznie(roboczy, zapis=True) if tryb == "wylaczny" else open(roboczy, "wb")) as f:
            if kawalki == 1:
                time.sleep(przerwa)
            for i, blok in enumerate(czesci):
                if i:
                    time.sleep(przerwa)
                f.write(blok)
                f.flush()
                h.update(blok)
                rozmiar += len(blok)
            if trzymaj_s > 0:
                time.sleep(trzymaj_s)
        if tryb == "tymczasowy":
            os.replace(roboczy, cel)
    koniec = time.time()
    return {"plik": str(cel), "start": t0, "koniec": koniec, "rozmiar": rozmiar, "sha16": h.hexdigest()[:16], "mtime_ns": os.stat(cel).st_mtime_ns}


def symuluj(folder, zrodla: list, ile: int | None = None, czas: tuple = (1.0, 5.0), kawalki: tuple = (5, 20), rownolegle: int = 4,
            odstep_s: float = 0.0, zle: tuple | list = (), seed: int = 0, wzor_nazwy: str = "skan_{nr:04d}.stl", tryb: str = "wprost",
            czasy: list | None = None) -> list[dict]:
    """Wrzuca do ``folder`` ``ile`` dobrych plikow (kolejno z ``zrodla``: ``bytes`` albo sciezki) i po jednym pliku zlym na
    kazdy wpis ``zle``. Do ``rownolegle`` zapisow naraz; ``odstep_s`` - przerwa miedzy rozpoczeciem kolejnych plikow.
    Czas zapisu pliku losowany z ``czas`` (albo ``czasy[i]`` dla i-tego dobrego pliku), liczba kawalkow z ``kawalki``.
    Zwraca liste opisow zapisow (jak ``zapisz_jak_skaner``) z polami ``nr``, ``rodzaj`` (``dobry`` albo rodzaj pliku zlego)
    i ``zrodlo``; kolejnosc listy = kolejnosc rozpoczynania zapisow.
    """
    if not zrodla:
        raise ValueError("symuluj: brak plikow zrodlowych")
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    ile = len(zrodla) if ile is None else ile
    plan = []
    for i in range(ile):
        z = zrodla[i % len(zrodla)]
        nazwa = wzor_nazwy.format(nr=i + 1, zrodlo=Path(z).stem if not isinstance(z, (bytes, bytearray)) else f"dane{i % len(zrodla)}")
        plan.append({"nr": i + 1, "rodzaj": "dobry", "zrodlo": i % len(zrodla), "dane": z, "cel": folder / nazwa,
                     "czas": float(czasy[i]) if czasy is not None else rng.uniform(*czas), "kawalki": rng.randint(*kawalki), "tryb": tryb})
    if zle:
        z0 = zrodla[0]
        dobry = bytes(z0) if isinstance(z0, (bytes, bytearray)) else Path(z0).read_bytes()
        for j, rodzaj in enumerate(zle):
            dane = zly_plik(rodzaj, dobry)
            nazwa = f"zly_{j + 1:02d}_{rodzaj}" + (".txt" if rodzaj == "inne_rozszerzenie" else ".stl")
            wpis = {"nr": ile + j + 1, "rodzaj": rodzaj, "zrodlo": 0, "dane": dane, "cel": folder / nazwa, "czas": rng.uniform(*czas),
                    "kawalki": rng.randint(*kawalki), "tryb": "wprost"}
            plan.insert(min(len(plan), (j + 1) * max(1, ile // (len(zle) + 1)) + j), wpis)  # zle pliki rozlozone miedzy dobrymi

    def jeden(p: dict) -> dict:
        w = zapisz_jak_skaner(p["dane"], p["cel"], p["czas"], p["kawalki"], p["tryb"])
        return {"nr": p["nr"], "rodzaj": p["rodzaj"], "zrodlo": p["zrodlo"], **w}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, rownolegle), thread_name_prefix="symulator") as pula:
        przyszle = []
        for i, p in enumerate(plan):
            if i and odstep_s > 0:
                time.sleep(odstep_s)
            przyszle.append(pula.submit(jeden, p))
        return [f.result() for f in przyszle]


def _klucz(sciezka) -> str:
    return os.path.normcase(os.path.abspath(str(sciezka)))


# ----------------------------------------------------------------------------
# skany plytek generowane (E3-O3): plytki okragle ramkowe i kazdy inny uklad z [plytki]
# ----------------------------------------------------------------------------
def tabela_prawdy(plik_json) -> dict:
    """Tabela prawdy skanu z pliku prawdy generatora - same liczby i nazwa ukladu (bez skrotow i nazw projektow): ``uklad``,
    ``numer``, ``prac``, ``gniazda_prac``, ``gniazda_ubytki`` (gniazda prac z co najmniej jednym ubytkiem), ``drgniec``."""
    d = json.loads(Path(plik_json).read_text(encoding="utf-8"))
    prace = d.get("prace") or []
    return {"uklad": d.get("plytka"), "numer": d.get("numer"), "prac": len(prace),
            "gniazda_prac": sorted(int(x["gniazdo"]) for x in prace if x.get("gniazdo") is not None),
            "gniazda_ubytki": sorted(int(x["gniazdo"]) for x in prace if x.get("ubytki") and x.get("gniazdo") is not None),
            "drgniec": sum(1 for x in prace if x.get("drgniecie"))}


def _ustawienia_generatora(plik=None) -> dict:
    from stanowisko import ustawienia as UST

    return UST.wczytaj_ustawienia(plik if plik is not None else UST.PLIK_PRZYKLADU)


def atrapy_koron_do(katalog) -> list:
    """Trzy atrapy koron (siekacz, przedtrzonowy, trzonowy) jak w testach programu - prace skanu generowanego bez puli projektow."""
    import numpy as np

    import atrapy_koron

    katalog = Path(katalog)
    katalog.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(3)
    pliki = []
    for i, typ in enumerate(("siekacz", "przedtrzonowy", "trzonowy")):
        W, L, H, g, amp = atrapy_koron.TYPY[typ]
        m = atrapy_koron.korona(W, L, H, g, amp, n_theta=96, n_u=120, rng=rng)
        plik = katalog / f"a{i}_{typ}.stl"
        m.export(plik)
        pliki.append(plik)
    return pliki


def nazwa_skanu(uklad: str, numer: int, ziarno: int) -> str:
    return f"skan_{uklad}_n{int(numer)}_s{int(ziarno):04d}"


def generuj_skan_plytki(cel, uklad: str, numer: int, ziarno: int, projekty: list, *, ubytki: tuple = (0, 2), prac: int | None = None,
                        pole: float = 100.0, ust: dict | None = None, nadpisz: bool = False) -> dict:
    """Sztuczny skan plytki ``uklad`` nr ``numer`` generatorem programu (``synth.generuj_plytke``; ``synth.py`` bez zmian):
    prace z plikow ``projekty`` (tyle, ile wejdzie, albo ``prac``), ``ubytki`` = zakres liczby ubytkow na prace, pole skanu
    fi ``pole`` mm, losowa poza skanera, skala 1,22 (plytka wieczorna) albo 1,0 (poranna), bez drgniec. Zapisuje
    ``<cel>/skan_<uklad>_n<numer>_s<ziarno>.stl`` i ``.json`` (prawda generatora). Te same argumenty, pliki projektow i
    ustawienia daja ten sam plik. Zwraca ``{"skan", "plik", "sha16", "prawda"}`` (``prawda`` = ``tabela_prawdy``)."""
    import warnings

    import numpy as np

    from stanowisko import synth
    from stanowisko import uklad as U
    from stanowisko import ustawienia as UST

    ust = ust if ust is not None else _ustawienia_generatora()
    if uklad not in ust["plytki"]:
        raise ValueError(f"uklad {uklad!r}: brak w [plytki] (sa: {', '.join(ust['plytki'])})")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        uk = U.wczytaj(uklad, UST.katalog_plytki(ust, uklad))
    if numer not in uk.numery:
        raise ValueError(f"numer {numer} nie jest numerem plytki ukladu {uklad} (sa: {', '.join(map(str, uk.numery))})")
    projekty = [Path(x) for x in projekty]
    if not projekty:
        raise ValueError("brak plikow projektow do ulozenia na plytce")
    cel, nazwa = Path(cel), nazwa_skanu(uklad, numer, ziarno)
    if not nadpisz:
        for istniejacy in (cel / f"{nazwa}.stl", cel / f"{nazwa}.json"):
            if istniejacy.exists():
                raise FileExistsError(f"{istniejacy.name} juz istnieje w katalogu skanow generowanych (nadpisz=True, zeby zastapic)")
    skala = 1.0 if synth.poranna(uklad) else 1.22
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        opcje = synth.Opcje.z_toml(ust, plytka=uklad, wspolczynnik=(skala, skala), ubytki_na_prace=(int(ubytki[0]), int(ubytki[1])),
                                   prace_na_plytce=prac, p_drgniecia=0.0, poza_uklad=True, pole=float(pole))
        skan, prawda = synth.generuj_plytke(uk, int(numer), projekty, np.random.default_rng(int(ziarno)), opcje, int(ziarno))
        p_stl, p_json = synth.zapisz(skan, prawda, cel, nazwa, nadpisz=nadpisz)
    return {"skan": nazwa, "plik": str(p_stl), "sha16": skrot16(p_stl.read_bytes()), "prawda": tabela_prawdy(p_json)}


def generuj_ze_scenariusza(scenariusz: dict, cel, projekty: list, ust: dict | None = None) -> list[dict]:
    """Generuje do ``cel`` skany pozycji scenariusza z polem ``generuj`` (``uklad``, ``numer``, ``ziarno``, opcjonalnie
    ``ubytki_na_prace`` [min, max], ``prac``, ``pole``) i porownuje kazdy z tabela prawdy (``prawda``) i ``sha16`` pozycji.
    Skan, ktory juz jest w ``cel``, nie jest generowany od nowa (``byl`` = True) - jest sprawdzany tak samo. Zwraca wpisy
    ``{"nr", "skan", "sha16", "prawda", "byl", "zgodna_prawda", "zgodne_sha16", "zgodne"}``."""
    cel, wyniki = Path(cel), []
    for poz in scenariusz.get("plytki") or []:
        g = poz.get("generuj")
        if not g:
            continue
        nazwa = nazwa_skanu(g["uklad"], g["numer"], g["ziarno"])
        if poz.get("skan") not in (None, nazwa):
            raise ValueError(f"scenariusz nr {poz.get('nr')}: pole skan ({poz['skan']}) inne niz nazwa z pola generuj ({nazwa})")
        p_stl, p_json = cel / f"{nazwa}.stl", cel / f"{nazwa}.json"
        byl = p_stl.is_file() and p_json.is_file()
        if byl:
            opis = {"skan": nazwa, "plik": str(p_stl), "sha16": skrot16(p_stl.read_bytes()), "prawda": tabela_prawdy(p_json)}
        else:
            opis = generuj_skan_plytki(cel, g["uklad"], int(g["numer"]), int(g["ziarno"]), projekty, ubytki=tuple(g.get("ubytki_na_prace", (0, 2))),
                                       prac=g.get("prac"), pole=float(g.get("pole", 100.0)), ust=ust)
        zgodna_prawda = poz.get("prawda") is None or dict(poz["prawda"]) == opis["prawda"]
        zgodne_sha16 = poz.get("sha16") is None or poz["sha16"] == opis["sha16"]
        wyniki.append({"nr": poz.get("nr"), **opis, "byl": byl, "zgodna_prawda": zgodna_prawda, "zgodne_sha16": zgodne_sha16,
                       "zgodne": zgodna_prawda and zgodne_sha16})
    return wyniki


def _wypisz_generowane(wyniki: list[dict], ze_scenariusza: bool) -> None:
    for w in wyniki:
        p = w["prawda"]
        stan = ""
        if ze_scenariusza:
            stan = " zgodny ze scenariuszem" if w["zgodne"] else (" NIEZGODNE ze scenariuszem:" + ("" if w["zgodna_prawda"] else " tabela prawdy")
                                                                  + ("" if w["zgodne_sha16"] else " sha16"))
        print(f"skan generowany{' nr ' + str(w['nr']) if w.get('nr') is not None else ''}: {w['skan']} sha16={w['sha16']} uklad={p['uklad']} "
              f"numer={p['numer']} prac={p['prac']} gniazda_prac={p['gniazda_prac']} gniazda_ubytki={p['gniazda_ubytki']} drgniec={p['drgniec']}"
              f"{' (plik juz jest - sprawdzony, nie generowany)' if w.get('byl') else ''}{stan}")
    if ze_scenariusza:
        print(f"skany generowane zgodne ze scenariuszem: {sum(1 for w in wyniki if w['zgodne'])} z {len(wyniki)}")


def _plan_generowania(ap, a) -> list[tuple]:
    """Lista (uklad, numer, ziarno, ubytki) z opcji ``--generuj``; bledy opcji = ``ap.error`` (kod 2) przed jakimkolwiek zapisem."""
    plan = []
    for wpis in a.generuj:
        cz = wpis.split(":")
        if len(cz) not in (3, 4) or not cz[1].isdigit() or not cz[2].isdigit() or (len(cz) == 4 and cz[3] != "bez_ubytkow"):
            ap.error(f"--generuj {wpis!r}: oczekiwano UKLAD:NUMER:ZIARNO albo UKLAD:NUMER:ZIARNO:bez_ubytkow")
        plan.append((cz[0], int(cz[1]), int(cz[2]), (0, 0) if len(cz) == 4 else (0, 2)))
    if (plan or a.scenariusz is not None) and a.katalog_generowanych is None:
        ap.error("--generuj i --scenariusz wymagaja --katalog-generowanych (katalog na skany generowane, poza repozytorium)")
    if a.tylko_generuj and not plan and a.scenariusz is None:
        ap.error("--tylko-generuj wymaga --generuj albo --scenariusz")
    if not plan:
        return plan
    try:
        ust = _ustawienia_generatora(a.ustawienia)
        from stanowisko import uklad as U
        from stanowisko import ustawienia as UST
    except Exception as e:  # noqa: BLE001 - zly plik ustawien to blad opcji
        ap.error(f"--ustawienia: {type(e).__name__}")
    for uklad, numer, _, _ in plan:
        if uklad not in ust["plytki"]:
            ap.error(f"--generuj: uklad {uklad!r} nie jest w [plytki] (sa: {', '.join(ust['plytki'])})")
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            numery = U.wczytaj(uklad, UST.katalog_plytki(ust, uklad)).numery
        if numer not in numery:
            ap.error(f"--generuj: numer {numer} nie jest numerem plytki ukladu {uklad} (sa: {', '.join(map(str, numery))})")
    return plan


def _generuj_z_opcji(a, plan: list[tuple]) -> tuple[list, bool]:
    """Wykonuje ``--generuj`` i ``--scenariusz``; zwraca (pliki STL do podania, czy wszystko zgodne ze scenariuszem)."""
    from stanowisko import synth

    ust = _ustawienia_generatora(a.ustawienia)
    projekty = [x for folder in a.projekty for x in synth.pliki_projektow(folder)] if a.projekty else atrapy_koron_do(a.katalog_generowanych / "atrapy")
    if not projekty:
        raise SystemExit("--projekty: nie znaleziono plikow .stl do ulozenia na plytkach generowanych")
    pliki, zgodne = [], True
    if a.scenariusz is not None:
        wyniki = generuj_ze_scenariusza(json.loads(a.scenariusz.read_text(encoding="utf-8")), a.katalog_generowanych, projekty, ust)
        _wypisz_generowane(wyniki, True)
        zgodne = all(w["zgodne"] for w in wyniki)
        pliki += [Path(w["plik"]) for w in wyniki]
    wyniki = []
    for uklad, numer, ziarno, ubytki in plan:
        nazwa = nazwa_skanu(uklad, numer, ziarno)
        p_stl, p_json = a.katalog_generowanych / f"{nazwa}.stl", a.katalog_generowanych / f"{nazwa}.json"
        if p_stl.is_file() and p_json.is_file():
            wyniki.append({"skan": nazwa, "plik": str(p_stl), "sha16": skrot16(p_stl.read_bytes()), "prawda": tabela_prawdy(p_json), "byl": True})
        else:
            wyniki.append(generuj_skan_plytki(a.katalog_generowanych, uklad, numer, ziarno, projekty, ubytki=ubytki, ust=ust))
    _wypisz_generowane(wyniki, False)
    return pliki + [Path(w["plik"]) for w in wyniki], zgodne


def statystyki(zapisy: list[dict], skany: list, odrzucone: list) -> dict:
    """Porownanie zapisow symulatora ze zdarzeniami obserwatora (``scanner.ZdarzenieSkanu``) i odrzuceniami (``scanner.Odrzucenie``)."""
    wolne = list(skany)
    opoznienia, bez_zdarzenia, przed_koncem, zly_skrot = [], [], 0, 0
    dobre = [z for z in zapisy if z["rodzaj"] == "dobry"]
    for z in sorted(dobre, key=lambda z: z["koniec"]):
        moje = [s for s in wolne if _klucz(s.plik) == _klucz(z["plik"])]
        if not moje:
            bez_zdarzenia.append(Path(z["plik"]).name)
            continue
        s = moje[0]
        wolne.remove(s)
        if (s.sha16, s.rozmiar) != (z["sha16"], z["rozmiar"]) or 84 + 50 * s.trojkaty != z["rozmiar"]:
            zly_skrot += 1
        if s.czas_zdarzenia < z["koniec"]:
            przed_koncem += 1
        opoznienia.append(s.czas_zdarzenia - z["koniec"])
    zle = [z for z in zapisy if z["rodzaj"] != "dobry"]
    powody = {_klucz(o.plik): o.powod for o in odrzucone}
    ze_zdarzeniem = [Path(z["plik"]).name for z in zle if any(_klucz(s.plik) == _klucz(z["plik"]) for s in skany)]
    opoznienia.sort()
    return {
        "dobrych": len(dobre), "zdarzen": len(skany), "bez_zdarzenia": bez_zdarzenia, "nadmiarowe": len(wolne) - len(ze_zdarzeniem),
        "przed_koncem": przed_koncem, "zly_skrot": zly_skrot,
        "opoznienie_mediana_s": statistics.median(opoznienia) if opoznienia else None,
        "opoznienie_p95_s": opoznienia[min(len(opoznienia) - 1, int(0.95 * len(opoznienia)))] if opoznienia else None,
        "opoznienie_max_s": opoznienia[-1] if opoznienia else None,
        "opoznienie_min_s": opoznienia[0] if opoznienia else None,
        "zlych": len(zle), "odrzucen": len(odrzucone),
        "powody_zlych": {Path(z["plik"]).name: powody.get(_klucz(z["plik"])) for z in zle},
        "zle_bez_powodu": [Path(z["plik"]).name for z in zle if _klucz(z["plik"]) not in powody],
        "zle_ze_zdarzeniem": ze_zdarzeniem,
    }


def _zrodla_z_argumentow(sciezki: list, ile: int | None, trojkaty: int, seed: int) -> list:
    if not sciezki:
        return [sztuczny_stl(trojkaty + 13 * i, seed=seed * 1000 + i) for i in range(ile or 10)]
    pliki = []
    for s in sciezki:
        p = Path(s)
        if p.is_dir():
            pliki += sorted(q for q in p.iterdir() if q.is_file() and q.suffix.lower() == ".stl")
        elif p.is_file():
            pliki.append(p)
        else:
            raise SystemExit(f"--zrodla: brak pliku albo katalogu {p}")
    if not pliki:
        raise SystemExit("--zrodla: nie znaleziono plikow .stl")
    return pliki


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--folder", type=Path, default=None, help="folder, do ktorego trafiaja pliki (jak folder eksportu skanera); "
                    "wymagany poza --tylko-generuj")
    ap.add_argument("--zrodla", nargs="*", default=[], help="pliki STL albo katalogi z plikami STL; brak = male pliki sztuczne")
    ap.add_argument("--ile", type=int, default=None, help="ile dobrych plikow zapisac (domyslnie: tyle, ile zrodel)")
    ap.add_argument("--czas", type=float, nargs=2, default=(1.0, 5.0), metavar=("MIN", "MAX"), help="czas zapisu jednego pliku, s")
    ap.add_argument("--kawalki", type=int, nargs=2, default=(5, 20), metavar=("MIN", "MAX"))
    ap.add_argument("--rownolegle", type=int, default=4, help="ile zapisow naraz")
    ap.add_argument("--odstep", type=float, default=0.0, help="przerwa miedzy rozpoczeciem kolejnych plikow, s")
    ap.add_argument("--zle", nargs="*", default=[], choices=RODZAJE_ZLYCH, help="pliki zle do dorzucenia (po jednym na wpis)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--trojkaty", type=int, default=2000, help="wielkosc plikow sztucznych (gdy brak --zrodla)")
    ap.add_argument("--wzor-nazwy", default="skan_{nr:04d}.stl", help="nazwa pliku: pola {nr} i {zrodlo}; moze zawierac podfolder")
    ap.add_argument("--tryb", choices=TRYBY, default="wprost")
    ap.add_argument("--dziennik", type=Path, default=None, help="zapisz opis zapisow i statystyki do pliku JSON")
    ap.add_argument("--pomiar", action="store_true", help="obserwuj folder modulem scanner i policz zdarzenia oraz opoznienia")
    ap.add_argument("--stabilizacja-ms", type=float, default=None, help="parametr obserwatora (domyslnie wartosc modulu scanner)")
    ap.add_argument("--odrzuc-po", type=float, default=None, help="parametr obserwatora: po ilu sekundach plik zly jest odrzucany")
    ap.add_argument("--czekaj", type=float, default=60.0, help="ile najdluzej czekac na zdarzenia po ostatnim zapisie, s")
    ap.add_argument("--analiza", action="store_true", help="analizuj kazdy zgloszony skan silnikiem (wymaga --projekty)")
    ap.add_argument("--projekty", type=Path, nargs="+", default=[], help="folder(y) puli projektow dla --analiza; takze prace skanow "
                    "generowanych (--generuj, --scenariusz; bez --projekty: 3 atrapy koron)")
    ap.add_argument("--wyjscie", type=Path, default=None, help="folder na <czas>_<sha16>[_n]_wynik.json z silnika (bez nazwy skanu)")
    ap.add_argument("--ustawienia", type=Path, default=None)
    ap.add_argument("--limit-analizy", type=float, default=3600.0, help="ile najdluzej czekac na wszystkie analizy, s")
    ap.add_argument("--generuj", nargs="*", default=[], metavar="UKLAD:NUMER:ZIARNO[:bez_ubytkow]",
                    help="wygeneruj sztuczny skan plytki (np. okragla_ramkowa_wieczorna:1:5801) i podaj go jak plik zrodlowy")
    ap.add_argument("--scenariusz", type=Path, default=None, help="scenariusz T2 (JSON): wygeneruj pozycje z polem 'generuj' i porownaj z tabela prawdy")
    ap.add_argument("--katalog-generowanych", type=Path, default=None, help="katalog na skany generowane i ich pliki prawdy (poza repozytorium)")
    ap.add_argument("--tylko-generuj", action="store_true", help="tylko wygeneruj skany (--generuj / --scenariusz) i zakoncz; bez --folder")
    a = ap.parse_args(argv)
    if a.analiza and not a.projekty:
        ap.error("--analiza wymaga --projekty")
    plan = _plan_generowania(ap, a)
    if a.folder is None and not a.tylko_generuj:
        ap.error("--folder jest wymagany (poza --tylko-generuj)")
    wygenerowane, zgodne = _generuj_z_opcji(a, plan) if (plan or a.scenariusz is not None) else ([], True)
    if a.tylko_generuj:
        return 0 if zgodne else 1
    if wygenerowane:
        a.zrodla = [*a.zrodla, *(str(x) for x in wygenerowane)]
    zrodla = _zrodla_z_argumentow(a.zrodla, a.ile, a.trojkaty, a.seed)
    obserwuj = a.pomiar or a.analiza
    skany, odrzucone, oczekiwania, zdarzenia_silnika = [], [], [], []
    zmiana = threading.Condition()
    sc = silnik = None
    if a.analiza:
        from stanowisko import silnik as SI

        def na_zdarzenie(z) -> None:
            with zmiana:
                zdarzenia_silnika.append(z)
                zmiana.notify_all()

        silnik = SI.Silnik(plik_ustawien=a.ustawienia, na_zdarzenie=na_zdarzenie)
        silnik.start()
        pula = SI.OpisPuli(foldery=tuple(str(p) for p in a.projekty))
    if obserwuj:
        from stanowisko import scanner as SC

        def na_skan(z) -> None:
            with zmiana:
                skany.append(z)
                zmiana.notify_all()
            if silnik is not None:
                silnik.zlec_skan(z, pula, wyjscie=a.wyjscie)

        def na_odrzucenie(o) -> None:
            with zmiana:
                odrzucone.append(o)
                zmiana.notify_all()

        parametry = {}
        if a.stabilizacja_ms is not None:
            parametry["stabilizacja_ms"] = a.stabilizacja_ms
        if a.odrzuc_po is not None:
            parametry["odrzuc_po_s"] = a.odrzuc_po
        a.folder.mkdir(parents=True, exist_ok=True)
        sc = SC.Scanner(a.folder, na_skan=na_skan, na_odrzucenie=na_odrzucenie, na_oczekiwanie=oczekiwania.append, **parametry)
        sc.start()
    kod = 0
    wynik: dict = {}
    try:
        zapisy = symuluj(a.folder, zrodla, a.ile, tuple(a.czas), tuple(a.kawalki), a.rownolegle, a.odstep, a.zle, a.seed, a.wzor_nazwy, a.tryb)
        wynik["zapisy"] = zapisy
        dobrych = sum(1 for z in zapisy if z["rodzaj"] == "dobry")
        print(f"zapisano plikow: {len(zapisy)} (dobrych {dobrych}, zlych {len(zapisy) - dobrych}) w {a.folder}")
        if sc is not None:
            limit = a.czekaj + sc.odrzuc_po_s
            with zmiana:
                zmiana.wait_for(lambda: len(skany) >= dobrych and len(odrzucone) >= len(zapisy) - dobrych, limit)
            time.sleep(min(1.0, sc.stabilizacja_s * 3))  # zdarzenia nadmiarowe, gdyby byly
            st = statystyki(zapisy, skany, odrzucone)
            wynik["statystyki"] = st
            wynik["zdarzenia"] = [{"plik": Path(z.plik).name, "sha16": z.sha16, "rozmiar": z.rozmiar, "trojkaty": z.trojkaty, "czas_zdarzenia": z.czas_zdarzenia,
                                   "nr": z.nr, "ponowny": z.ponowny, "duplikat": z.duplikat} for z in skany]
            wynik["odrzucone"] = [{"plik": Path(o.plik).name, "powod": o.powod, "opis": o.opis, "rozmiar": o.rozmiar} for o in odrzucone]
            wynik["oczekiwania"] = [{"plik": Path(o.plik).name, "od_s": o.od_s, "opis": o.opis} for o in list(oczekiwania)]
            if oczekiwania:
                print(f"informacji 'czeka na zwolnienie pliku': {len(oczekiwania)} (plikow {len({str(o.plik) for o in oczekiwania})})")
            print(f"zdarzen {st['zdarzen']} / {st['dobrych']}, przed koncem zapisu {st['przed_koncem']}, bez zdarzenia {len(st['bez_zdarzenia'])}, "
                  f"nadmiarowych {st['nadmiarowe']}, zly skrot {st['zly_skrot']}")
            if st["opoznienie_mediana_s"] is not None:
                print(f"opoznienie zdarzenia od konca zapisu: mediana {st['opoznienie_mediana_s']:.3f} s, p95 {st['opoznienie_p95_s']:.3f} s, "
                      f"min {st['opoznienie_min_s']:.3f} s, max {st['opoznienie_max_s']:.3f} s")
            print(f"pliki zle: {st['zlych']}, odrzucen z powodem {st['zlych'] - len(st['zle_bez_powodu'])} / {st['zlych']}, ze zdarzeniem {len(st['zle_ze_zdarzeniem'])}"
                  + "".join(f"\n  {n}: {p}" for n, p in st["powody_zlych"].items()))
            dobrze = (st["zdarzen"] == st["dobrych"] and not st["bez_zdarzenia"] and st["nadmiarowe"] == 0 and st["przed_koncem"] == 0 and st["zly_skrot"] == 0
                      and not st["zle_bez_powodu"] and not st["zle_ze_zdarzeniem"])
            kod = 0 if dobrze else 1
        if silnik is not None:
            with zmiana:
                zmiana.wait_for(lambda: sum(1 for z in zdarzenia_silnika if z.typ in ("wynik", "blad")) >= len(skany), a.limit_analizy)
            koniec_zapisu = {_klucz(z["plik"]): z["koniec"] for z in zapisy}
            analizy = []
            for z in [z for z in zdarzenia_silnika if z.typ in ("wynik", "blad")]:
                start = next((s.czas for s in zdarzenia_silnika if s.typ == "start" and s.zadanie_id == z.zadanie_id), None)
                kz = koniec_zapisu.get(_klucz(z.zadanie.skan))
                w = z.wynik or {}
                analizy.append({"plik": Path(z.zadanie.skan).name, "sha16": z.zadanie.skan_sha16, "typ": z.typ, "rodzaj": z.rodzaj, "blad": z.blad,
                                "start_od_konca_zapisu_s": round(start - kz, 3) if start is not None and kz is not None else None,
                                "wynik_od_konca_zapisu_s": round(z.czas - kz, 3) if kz is not None else None, "czas_s": z.czas_s,
                                "plytka": w.get("plytka"), "numer": w.get("numer"), "uklad_zgodny": w.get("uklad_zgodny"),
                                "gniazd": len(w.get("gniazda", [])), "statusy_gniazd": w.get("statusy_gniazd"), "ubytki": w.get("ubytki")})
                x = analizy[-1]
                print(f"analiza {x['plik']} sha16={x['sha16']}: {x['typ']}{' (' + x['rodzaj'] + ': ' + x['blad'] + ')' if z.typ == 'blad' else ''} "
                      f"plytka={x['plytka']} nr={x['numer']} gniazd={x['gniazd']} statusy={x['statusy_gniazd']} czas={x['czas_s']} s, "
                      f"start po {x['start_od_konca_zapisu_s']} s od konca zapisu, wynik po {x['wynik_od_konca_zapisu_s']} s")
            wynik["analizy"] = analizy
            if len(analizy) < len(skany):
                print(f"UWAGA: analiz {len(analizy)} / {len(skany)} w limicie {a.limit_analizy} s")
                kod = 1
            print(f"analizy: {sum(1 for x in analizy if x['typ'] == 'wynik')} wynikow, {sum(1 for x in analizy if x['typ'] == 'blad')} bledow / {len(skany)} skanow")
    finally:
        if sc is not None:
            sc.stop()
        if silnik is not None:
            silnik.stop()
    if a.dziennik is not None:
        a.dziennik.parent.mkdir(parents=True, exist_ok=True)
        a.dziennik.write_text(json.dumps(wynik, ensure_ascii=False, indent=1), encoding="utf-8")
        print(a.dziennik)
    return kod


if __name__ == "__main__":
    sys.exit(main())
