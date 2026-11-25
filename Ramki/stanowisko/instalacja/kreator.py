"""kreator - logika okna instalatora (E3-I1), wspolna dla okna (``okno_instalatora.py``) i trybu bez okna (testy).

Tylko biblioteka standardowa (okno startuje z Pythona paczki, ZANIM powstanie srodowisko wersji). Kolejnosc jak w oknie:

1. ``Wybor`` (foldery, miejsce instalacji, osoby) i ``informacje_paczki`` (wersja, potrzebne miejsce);
2. ``sprawdz_foldery`` / ``sprawdz_osoby`` - zdania bledow po polsku (``napisy_instalatora``); pusta lista = wolno dalej;
3. ``polecenie_instalacji`` - wiersz polecen ``instalator.py zainstaluj`` (ta sama droga co ``zainstaluj.cmd``: kody wyjscia,
   dziennik, wersje, powrot - bez zmian); ``uruchom_instalacje`` uruchamia go z ukryta konsola i podaje wiersze wyjscia;
   ``Postep`` czyta z nich krok ``[n/9]``, ``BLAD:`` / ``CO ZROBIC:``, ikony (``SKROT ...``) i wiersz koncowy;
4. ``zdanie_kodu`` - kod wyjscia instalatora jako zdanie; ``uruchom_program`` - start programu bez konsoli (starter ikon).

Tryb bez okna: ``okno_instalatora.py --bez-okna --folder-skanow X [--folder-projektow Y] [--katalog K] --osoba A [--osoba B]``.
"""
from __future__ import annotations

import dataclasses
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

try:  # pakiet ``instalacja`` (testy) albo katalog skryptu na sys.path (okno uruchomione z paczki: python -I okno_instalatora.py)
    from instalacja import instalator as I
    from instalacja import napisy_instalatora as N
except ImportError:  # pragma: no cover - droga okna z paczki
    import instalator as I  # type: ignore[no-redef]
    import napisy_instalatora as N  # type: ignore[no-redef]

KOD_WYBOR = 12          # tryb bez okna: wybor nie przechodzi kontroli (zdanie bledu na ekranie) - nic nie zmieniono
DLUGOSC_OSOBY = 40
CREATE_NO_WINDOW = 0x08000000
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200


@dataclasses.dataclass
class Wybor:
    """Wybor osoby instalujacej (krok 1 i 2 okna)."""
    folder_skanow: str = ""
    folder_projektow: str = ""
    katalog: str = I.KATALOG_DOMYSLNY
    osoby: list[str] = dataclasses.field(default_factory=list)


def tekst_mb(mb: int | None) -> str:
    if mb is None:
        return "?"
    return f"{mb / 1024:.1f} GB".replace(".", ",") if mb >= 1024 else f"{mb} MB"


def informacje_paczki(paczka: Path) -> dict:
    """{wersja, potrzebne_mb (nowa wersja + Python), python_w_paczce, blad}. Bez liczenia sum (to robi instalator w kroku 1)."""
    info = {"wersja": "?", "potrzebne_mb": None, "python_w_paczce": (paczka / I.KATALOG_PYTHONA / "python.exe").is_file(), "blad": None}
    try:
        info["wersja"] = json.loads((paczka / I.PLIK_WYDANIA).read_text(encoding="utf-8"))["wersja"]
        sumy = I.wczytaj_sumy(paczka / I.PLIK_SUM_PACZKI)
        bajty_kol, _ = I.rozmiary_kol(sorted((paczka / "kola").glob("*.whl")))
        info["potrzebne_mb"] = I.potrzebne_miejsce_mb(paczka, sumy, bajty_kol) + I.bajty_pythona(paczka, sumy) // 2**20
    except (OSError, ValueError, KeyError, TypeError, I.BladInstalacji) as e:
        info["blad"] = f"{type(e).__name__}: {e}"
    return info


def wolne_mb(katalog: str | Path) -> int | None:
    """Wolne miejsce (MB) na dysku miejsca instalacji - najblizszy istniejacy katalog nadrzedny; None, gdy dysku nie ma."""
    p = Path(katalog)
    for kandydat in [p, *p.parents]:
        if kandydat.is_dir():
            try:
                return I.shutil.disk_usage(kandydat).free // 2**20
            except OSError:
                return None
    return None


def istniejaca_instalacja(katalog: str | Path) -> dict | None:
    """Gdy w ``katalog`` jest juz plik ustawien: {wersja, folder_skanow, folder_projektow, osoby, blad} - okno pokazuje je
    i nie zmienia (aktualizacja zostawia ustawienia bajt w bajt). Brak pliku = None."""
    k = Path(katalog)
    plik = k / I.PLIK_USTAWIEN
    if not k.is_absolute() or not plik.is_file():
        return None
    wynik = {"wersja": I.czytaj_wskaznik(k, I.PLIK_BIEZACEJ) or "niedoko\u0144czona", "folder_skanow": "", "folder_projektow": "", "osoby": [],
             "blad": None}
    try:
        ust = tomllib.loads(plik.read_text(encoding="utf-8"))
        wynik["folder_skanow"] = str(ust.get("sciezki", {}).get("folder_eksportu_skanera", ""))
        wynik["folder_projektow"] = str(ust.get("sciezki", {}).get("folder_cyrkon", ""))
        wynik["osoby"] = [str(o) for o in ust.get("sesja", {}).get("operatorzy", [])]
    except (OSError, ValueError, AttributeError) as e:
        wynik["blad"] = type(e).__name__
    return wynik


def domyslny_folder_projektow(katalog: str | Path) -> Path:
    return Path(katalog) / I.FOLDER_PROJEKTOW_DOMYSLNY


def sprawdz_foldery(wybor: Wybor, potrzebne: int | None) -> tuple[list[str], list[str]]:
    """Krok 1: (bledy, uwagi). Bledy zatrzymuja przejscie dalej; uwagi (np. brak folderu projektow) tylko informuja.
    Przy aktualizacji (w miejscu instalacji jest juz plik ustawien) foldery nie sa sprawdzane - zostaja z ustawien."""
    bledy, uwagi = [], []
    katalog = wybor.katalog.strip()
    if not katalog:
        bledy.append(N.BRAK_CELU)
    elif not re.match(r"[A-Za-z]:[\\/]", katalog) and not katalog.startswith("\\\\"):
        bledy.append(N.CEL_WZGLEDNY)
    else:
        k = Path(katalog)
        if not Path(k.anchor).exists():
            bledy.append(N.CEL_DYSK.format(sciezka=k.anchor))
        elif k.exists() and not k.is_dir():
            bledy.append(N.CEL_PLIK.format(sciezka=k))
        elif ";" in katalog:
            bledy.append(N.CEL_SREDNIK)
        elif I.katalog_synchronizowany(k):
            bledy.append(N.CEL_SYNCHRONIZOWANY)
        else:
            wolne = wolne_mb(k)
            if potrzebne is not None and wolne is not None and wolne < potrzebne:
                bledy.append(N.ZA_MALO_MIEJSCA.format(potrzeba=tekst_mb(potrzebne), wolne=tekst_mb(wolne)))
    if not bledy and istniejaca_instalacja(katalog) is not None:
        return bledy, uwagi
    skany = wybor.folder_skanow.strip()
    if not skany:
        bledy.append(N.BRAK_SKANOW)
    elif not Path(skany).is_dir():
        bledy.append(N.SKANY_NIE_ISTNIEJE.format(sciezka=skany))
    projekty = wybor.folder_projektow.strip()
    if projekty and not Path(projekty).is_dir():
        bledy.append(N.PROJEKTY_NIE_ISTNIEJE.format(sciezka=projekty))
    elif not projekty and katalog:
        uwagi.append(N.PROJEKTY_PUSTE.format(sciezka=domyslny_folder_projektow(katalog)))
    return bledy, uwagi


def sprawdz_osobe(osoba: str, osoby: list[str]) -> str | None:
    """Zdanie bledu dla dodawanej osoby albo None (wolno dodac)."""
    o = osoba.strip()
    if not o:
        return N.OSOBA_PUSTA
    if re.search(r"[\x00-\x1f\x7f]", o):
        return N.OSOBA_ZNAKI
    if len(o) > DLUGOSC_OSOBY:
        return N.OSOBA_ZA_DLUGA.format(n=DLUGOSC_OSOBY)
    if o.casefold() in {x.strip().casefold() for x in osoby}:
        return N.OSOBA_POWTORZONA.format(osoba=o)
    return None


def sprawdz_osoby(osoby: list[str]) -> list[str]:
    """Krok 2: co najmniej jedna osoba; kazda poprawna i bez powtorzen."""
    if not [o for o in osoby if o.strip()]:
        return [N.BRAK_OSOB]
    bledy = []
    for i, o in enumerate(osoby):
        blad = sprawdz_osobe(o, osoby[:i])
        if blad:
            bledy.append(blad)
    return bledy


def python_konsolowy(python: Path) -> Path:
    """``python.exe`` obok ``pythonw.exe`` (instalator uruchamiany jest z ukryta konsola: procesy potomne - venv, pip,
    samokontrola - dziedzicza ja i nie otwieraja wlasnych okien)."""
    if python.name.lower() == "pythonw.exe" and python.with_name("python.exe").is_file():
        return python.with_name("python.exe")
    return python


def polecenie_instalacji(paczka: Path, wybor: Wybor, aktualizacja: bool, python: Path | None = None,
                         skrot_katalog: Path | None = None) -> list[str]:
    """Wiersz polecen instalatora dla wyboru z okna. Paczka z Pythonem: ``--python-z-paczki`` (instalator kopiuje Pythona do
    katalogu instalacji); bez niego (proby) - ``--python`` = ``python``. Zawsze: ikony na pulpicie, samokontrola bez proby
    polaczenia z ramkami (ramki wylaczone), bez pauzy. Przy aktualizacji foldery i osoby nie sa podawane (ustawienia zostaja)."""
    z_paczki = (paczka / I.KATALOG_PYTHONA / "python.exe").is_file()
    interpreter = paczka / I.KATALOG_PYTHONA / "python.exe" if z_paczki else python_konsolowy(Path(python or sys.executable))
    polecenie = [str(interpreter), "-I", "-B", "-X", "utf8", str(paczka / "program" / "instalacja" / "instalator.py"), "zainstaluj",
                 "--paczka", str(paczka), "--katalog", wybor.katalog.strip()]
    polecenie += ["--python-z-paczki"] if z_paczki else ["--python", str(interpreter)]
    polecenie += ["--skrot", "--bez-sieci", "--bez-pauzy"] + (["--skrot-katalog", str(skrot_katalog)] if skrot_katalog else [])
    if not aktualizacja:
        polecenie += ["--folder-skanow", wybor.folder_skanow.strip(), "--folder-projektow", wybor.folder_projektow.strip(),
                      "--ramki-wylaczone"]
        for osoba in wybor.osoby:
            if osoba.strip():
                polecenie += ["--osoba", osoba.strip()]
    return polecenie


def srodowisko_instalatora() -> dict:
    env = {k: v for k, v in os.environ.items() if k.upper() not in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "VIRTUAL_ENV")}
    env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    return env


def uruchom_instalacje(polecenie: list[str], na_wiersz, przerwij=None) -> int:
    """Uruchamia instalator (ukryta konsola) i podaje kazdy wiersz wyjscia do ``na_wiersz``; zwraca kod wyjscia.
    ``przerwij`` (funkcja bez argumentow -> bool) sprawdzana po kazdym wierszu: True = zakoncz proces instalatora (jak
    zamkniete okno konsoli: instalator sprzata przy nastepnym uruchomieniu, wersja biezaca bez zmian)."""
    proces = subprocess.Popen(polecenie, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=srodowisko_instalatora(),
                              creationflags=CREATE_NO_WINDOW if os.name == "nt" else 0, text=True, encoding="utf-8", errors="replace")
    assert proces.stdout is not None
    for wiersz in proces.stdout:
        na_wiersz(wiersz.rstrip("\r\n"))
        if przerwij is not None and przerwij():
            proces.kill()
            break
    return proces.wait()


class Postep:
    """Stan instalacji z wierszy wyjscia instalatora: krok (1..9), wiersze ``BLAD:`` / ``CO ZROBIC:``, ikony, wiersz koncowy."""

    def __init__(self):
        self.krok = 0
        self.bledy: list[str] = []
        self.rady: list[str] = []
        self.skroty: dict[str, tuple[bool, str]] = {}  # nazwa -> (zalozony, plik skrotu albo plik do klikniecia)
        self.koncowy = ""
        self.ramki_wylaczone = False
        self.wiersze: list[str] = []

    def wiersz(self, tekst: str) -> None:
        self.wiersze.append(tekst)
        t = tekst.strip()
        m = re.match(r"\[(\d)/9\]", t)
        if m:
            self.krok = int(m.group(1))
        elif t.startswith("BLAD:"):
            self.bledy.append(t[len("BLAD:"):].strip())
        elif t.startswith("CO ZROBIC:"):
            self.rady.append(t[len("CO ZROBIC:"):].strip())
        elif t.startswith(("SKROT ZALOZONY:", "SKROT NIEUDANY:")):
            nazwa, _, plik = t.split(":", 1)[1].partition("|")
            self.skroty[nazwa.strip()] = (t.startswith("SKROT ZALOZONY:"), plik.strip())
        elif t.startswith(("INSTALACJA:", "POWROT:")):
            self.koncowy = t
        if "ramki wylaczone ([ramki] wlaczone = false)" in t:
            self.ramki_wylaczone = True


def zdanie_kodu(kod: int) -> str:
    return N.ZDANIA_KODOW.get(kod, N.ZDANIE_NIEZNANEGO_KODU.format(kod=kod))


def python_startu(katalog: Path) -> Path | None:
    """``pythonw.exe`` interpretera bazowego wersji biezacej (kopia z paczki w katalogu instalacji albo Python systemu)."""
    home = I.python_bazowy_wersji(katalog, I.czytaj_wskaznik(katalog, I.PLIK_BIEZACEJ))
    return home / "pythonw.exe" if home and (home / "pythonw.exe").is_file() else None


def polecenie_startu(katalog: Path, cel: str = "stanowisko") -> list[str] | None:
    """Ten sam start co ikona na pulpicie: ``pythonw.exe -I -B <KATALOG>/start_bez_konsoli.pyw <cel>``; None, gdy sie nie da."""
    pythonw = python_startu(katalog)
    if pythonw is None or not (katalog / I.WZOR_STARTU).is_file():
        return None
    return [str(pythonw), "-I", "-B", str(katalog / I.WZOR_STARTU), cel]


def uruchom_program(katalog: Path, cel: str = "stanowisko") -> bool:
    """Start programu niezalezny od okna instalatora (okno mozna zamknac, pendrive wyjac). False = nie da sie (brak startera)."""
    polecenie = polecenie_startu(katalog, cel)
    if polecenie is None:
        return False
    flagi = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    subprocess.Popen(polecenie, cwd=str(katalog), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     creationflags=flagi, close_fds=True, env=srodowisko_instalatora())
    return True


def main_bez_okna(paczka: Path, wybor: Wybor, python: Path | None = None, wypisz=print, skrot_katalog: Path | None = None) -> int:
    """Tryb bez okna (testy): te same kontrole i to samo polecenie, co okno; zdania na ekranie. Kod = kod instalatora albo 12."""
    info = informacje_paczki(paczka)
    aktualizacja = istniejaca_instalacja(wybor.katalog) is not None
    bledy, uwagi = sprawdz_foldery(wybor, info["potrzebne_mb"])
    if not aktualizacja:
        bledy += sprawdz_osoby(wybor.osoby)
    for uwaga in uwagi:
        wypisz("UWAGA: " + uwaga)
    if bledy:
        wypisz(N.ZDANIE_WYBORU.format(bledy=" ".join(bledy)))
        return KOD_WYBOR
    if aktualizacja:
        wypisz(N.AKTUALIZACJA.format(wersja=istniejaca_instalacja(wybor.katalog)["wersja"]))
    postep = Postep()

    def na_wiersz(tekst: str) -> None:
        postep.wiersz(tekst)
        wypisz(tekst)

    kod = uruchom_instalacje(polecenie_instalacji(paczka, wybor, aktualizacja, python, skrot_katalog), na_wiersz)
    wypisz("WYNIK: " + zdanie_kodu(kod))
    for nazwa, (zalozony, plik) in postep.skroty.items():
        if not zalozony:
            wypisz("UWAGA: " + N.IKONA_BRAK.format(nazwa=nazwa, plik=Path(plik).name))
    return kod
