"""instalator - instalacja, aktualizacja i powrot do poprzedniej wersji programu "Stanowisko" (E3-A11i, wariant B).

Uruchamiany z rozpakowanej paczki wydania przez ``zainstaluj.cmd`` (albo wprost: ``python -I instalator.py zainstaluj ...``)
i z katalogu instalacji przez ``Wroc_do_poprzedniej.cmd`` / ``Wersje.cmd``. Tylko biblioteka standardowa Pythona 3.12.

Uklad katalogu instalacji ``<KATALOG>`` (domyslnie ``C:\\Stanowisko``)::

    Stanowisko.cmd, Samokontrola.cmd, Wroc_do_poprzedniej.cmd, Wersje.cmd, Polecenie.cmd   skrypty uruchamiajace (wzory)
    ustawienia.toml          ustawienia tej maszyny - POZA katalogiem wersji, przy aktualizacji nietkniete
    dane\\                    baza, wyniki, logi, kopie bazy (dane\\kopie\\) - POZA katalogiem wersji
    wersja_biezaca.txt       wskaznik wersji biezacej (plik tekstowy, jeden wiersz; nie dowiazanie)
    wersja_poprzednia.txt    wersja, do ktorej wraca Wroc_do_poprzedniej.cmd
    dziennik_instalacji.txt  data, wersja, kroki, wynik samokontroli (bez danych osobowych)
    wersje\\<wersja>\\program\\   pliki programu z paczki (z SUMY_PROGRAMU.sha256)
    wersje\\<wersja>\\venv\\      wlasne srodowisko wirtualne tej wersji (pakiety tylko z kol paczki, pip --no-index)
    wersje\\<wersja>\\NIEDOKONCZONA.txt   znacznik instalacji w toku / przerwanej (sprzatana przy nastepnej probie)

Kolejnosc instalacji i kody wyjscia: ``opisy_modulow/instalacja.md``.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import traceback
import zipfile
from pathlib import Path

KOD_OK = 0
KOD_SAMOKONTROLA_CZERWONA = 1      # samokontrola nowej wersji: co najmniej jeden BLAD (wersja zainstalowana, NIE przelaczona)
KOD_SAMOKONTROLA_NIEWYKONANA = 2   # samokontroli nie dalo sie wykonac (kod 2 modulu albo inny nieznany kod)
KOD_PACZKA = 3                     # paczka: zle sumy, brak plikow, blad wydania (np. brak modulu samokontroli)
KOD_PYTHON = 4                     # brak Pythona 3.12 / zla wersja
KOD_PROGRAM_DZIALA = 5             # program "Stanowisko" jest uruchomiony - zamknij program
KOD_INSTALACJA = 6                 # katalog, miejsce na dysku, venv, pip, przerwanie
KOD_USTAWIENIA = 7                 # ustawienia.toml: blad albo sciezki wzgledne (dane trafilyby do katalogu wersji)
KOD_BAZA_NOWSZA = 8                # powrot: baza ma nowszy schemat niz poprzednia wersja - potrzebne /przywroc-kopie
KOD_BRAK_WERSJI = 9                # powrot / usuwanie: brak wersji, do ktorej mozna sie odwolac

KATALOG_DOMYSLNY = "C:\\Stanowisko"
PLIK_BIEZACEJ = "wersja_biezaca.txt"
PLIK_POPRZEDNIEJ = "wersja_poprzednia.txt"
PLIK_DZIENNIKA = "dziennik_instalacji.txt"
PLIK_USTAWIEN = "ustawienia.toml"
KATALOG_WERSJI = "wersje"
ZNACZNIK_NIEDOKONCZONEJ = "NIEDOKONCZONA.txt"
PLIK_INSTALACJI = "instalacja.json"
PLIK_SUM_PACZKI = "SHA256SUMS"
PLIK_SUM_PROGRAMU = "SUMY_PROGRAMU.sha256"
PLIK_WYDANIA = "wydanie.json"
LISTA_PROGRAMU = "instalacja/zamrozone.txt"          # wzgledem katalogu programu
LISTA_TESTOW = "instalacja/zamrozone_testy.txt"
MODUL_SAMOKONTROLI = "stanowisko/samokontrola.py"
WZORY_SKRYPTOW = ("Stanowisko.cmd", "Samokontrola.cmd", "Wroc_do_poprzedniej.cmd", "Wersje.cmd", "Polecenie.cmd")
WZOR_WERSJI = re.compile(r"[0-9A-Za-z][0-9A-Za-z._-]{0,31}")
# Zapas miejsca: pliki kol po rozpakowaniu x ZAPAS_PYC (pip dopisuje pliki .pyc) + program + ZAPAS_MB.
ZAPAS_PYC = 1.3
ZAPAS_MB = 300
LIMIT_SCIEZKI = 259                # Windows bez dlugich sciezek: najdluzsza sciezka pliku
LIMIT_SAMOKONTROLI_S = 600
PAKIETY_SRODOWISKA = ("pip",)      # zaklada je sam ``python -m venv`` (ensurepip); nie naleza do listy zamrozonej

_WIERSZ_SUM = re.compile(r"([0-9a-f]{64}) [ *](.+)")
_OPCJE_UKOSNIK = ("katalog", "python", "paczka", "testy", "skrot", "skrot-katalog", "bez-sieci", "bez-pauzy", "przywroc-kopie",
                  "min-wolne-mb", "usun")


class BladInstalacji(Exception):
    """Blad z komunikatem dla osoby instalujacej: ``opis`` (co sie stalo) i ``rada`` (co zrobic)."""

    def __init__(self, kod: int, opis: str, rada: str = ""):
        super().__init__(opis)
        self.kod, self.opis, self.rada = kod, opis, rada


# ---------------------------------------------------------------------------------------------------------- narzedzia

def sha256_pliku(plik: Path) -> str:
    h = hashlib.sha256()
    with open(plik, "rb") as f:
        for kawalek in iter(lambda: f.read(1 << 20), b""):
            h.update(kawalek)
    return h.hexdigest()


def wczytaj_sumy(plik: Path) -> dict[str, str]:
    """Plik w formacie ``sha256sum`` -> {sciezka wzgledna z ukosnikami /: suma}. Zly wiersz albo sciezka poza katalog = blad."""
    sumy: dict[str, str] = {}
    for nr, wiersz in enumerate(plik.read_text(encoding="utf-8").splitlines(), 1):
        if not wiersz.strip():
            continue
        m = _WIERSZ_SUM.fullmatch(wiersz)
        nazwa = m.group(2).replace("\\", "/") if m else ""
        if not m or nazwa.startswith("/") or ":" in nazwa or ".." in nazwa.split("/") or nazwa in sumy:
            raise BladInstalacji(KOD_PACZKA, f"{plik.name}: wiersz {nr} nie jest poprawnym wpisem sumy SHA-256",
                                 "Paczka jest uszkodzona - pobierz ja i rozpakuj ponownie.")
        sumy[nazwa] = m.group(1)
    return sumy


def sprawdz_sumy(katalog: Path, sumy: dict[str, str]) -> list[str]:
    """Liczy sumy plikow ``katalog/<nazwa>``; zwraca liste roznic (``brak pliku X`` / ``zmieniony plik X``)."""
    roznice = []
    for nazwa, oczekiwana in sumy.items():
        p = katalog / nazwa
        if not p.is_file():
            roznice.append(f"brak pliku {nazwa}")
        elif sha256_pliku(p) != oczekiwana:
            roznice.append(f"zmieniony plik {nazwa}")
    return roznice


def bez_profilu(tekst: str) -> str:
    """Zastepuje katalog profilu uzytkownika (zawiera nazwe konta) napisem %USERPROFILE% - do dziennika."""
    for zmienna in ("USERPROFILE", "HOME"):
        profil = os.environ.get(zmienna, "")
        if len(profil) > 3:
            tekst = re.sub(re.escape(profil), lambda _: "%USERPROFILE%", tekst, flags=re.IGNORECASE)
            tekst = re.sub(re.escape(profil.replace("\\", "/")), lambda _: "%USERPROFILE%", tekst, flags=re.IGNORECASE)
    return tekst


def normalizuj_nazwe(nazwa: str) -> str:
    """Nazwa pakietu pip w postaci porownywalnej (PEP 503)."""
    return re.sub(r"[-_.]+", "-", nazwa).lower()


def wczytaj_liste_zamrozona(plik: Path) -> dict[str, str]:
    """``nazwa==wersja`` w kazdym wierszu (komentarze # i puste wiersze pomijane) -> {nazwa znormalizowana: wersja}."""
    pakiety: dict[str, str] = {}
    for nr, wiersz in enumerate(plik.read_text(encoding="utf-8").splitlines(), 1):
        wiersz = wiersz.split("#", 1)[0].strip()
        if not wiersz:
            continue
        m = re.fullmatch(r"([A-Za-z0-9][A-Za-z0-9._-]*)==([A-Za-z0-9][A-Za-z0-9._+!-]*)", wiersz)
        if not m:
            raise BladInstalacji(KOD_PACZKA, f"{plik.name}: wiersz {nr} nie ma postaci nazwa==wersja",
                                 "Blad wydania - zglos budujacemu paczke.")
        pakiety[normalizuj_nazwe(m.group(1))] = m.group(2)
    return pakiety


def zapisz_atomowo(plik: Path, dane: bytes) -> None:
    """Zapis przez plik tymczasowy obok i ``os.replace`` - czytajacy widzi stara albo nowa tresc, nigdy polowe."""
    tymczasowy = plik.with_name(plik.name + ".nowy")
    with open(tymczasowy, "wb") as f:
        f.write(dane)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tymczasowy, plik)


def czytaj_wskaznik(katalog: Path, nazwa: str) -> str | None:
    """Wersja z pliku wskaznika; brak pliku, pusty albo zla tresc = None."""
    try:
        tekst = (katalog / nazwa).read_text(encoding="ascii").strip()
    except (OSError, UnicodeDecodeError):
        return None
    return tekst if WZOR_WERSJI.fullmatch(tekst) else None


def usun_katalog(katalog: Path) -> None:
    def popraw(funkcja, sciezka, _blad):  # plik tylko do odczytu: zdejmij atrybut i powtorz
        os.chmod(sciezka, 0o700)
        funkcja(sciezka)

    try:
        shutil.rmtree(katalog, onexc=popraw) if sys.version_info >= (3, 12) else shutil.rmtree(katalog, onerror=popraw)
    except OSError as e:
        raise BladInstalacji(KOD_INSTALACJA, f"nie mozna usunac katalogu {katalog} ({type(e).__name__}: {e.strerror or e})",
                             "Zamknij programy, ktore maja otwarte pliki z tego katalogu, i uruchom polecenie ponownie.") from e


def uruchom(polecenie: list, *, cwd: Path | None = None, env: dict | None = None, limit_s: float | None = None,
            przechwyc: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run([str(c) for c in polecenie], cwd=str(cwd) if cwd else None, env=env, timeout=limit_s,
                          stdin=subprocess.DEVNULL, capture_output=przechwyc, text=True, encoding="utf-8", errors="replace")


def srodowisko_procesu() -> dict:
    """Zmienne dla procesow programu uruchamianych przez instalator - te same, co w skryptach ``*.cmd``: bez PYTHONPATH,
    bez zapisu __pycache__ (katalog programu zostaje zgodny z ``SUMY_PROGRAMU.sha256``), UTF-8."""
    env = {k: v for k, v in os.environ.items() if k.upper() not in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "VIRTUAL_ENV")}
    env.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1")
    return env


class Dziennik:
    """Wiersze ``data godzina | operacja | tekst`` dopisywane do ``<KATALOG>/dziennik_instalacji.txt`` (gdy katalog jest)."""

    def __init__(self, katalog: Path, operacja: str, zegar=dt.datetime.now):
        self.katalog, self.operacja, self.zegar = katalog, operacja, zegar

    def wpis(self, tekst: str) -> None:
        if not self.katalog.is_dir():
            return
        try:
            with open(self.katalog / PLIK_DZIENNIKA, "a", encoding="utf-8", newline="\r\n") as f:
                for wiersz in bez_profilu(tekst).splitlines() or [""]:
                    f.write(f"{self.zegar():%Y-%m-%d %H:%M:%S} | {self.operacja} | {wiersz}\n")
        except OSError:
            pass  # dziennik nie moze zatrzymac instalacji

    def krok(self, tekst: str) -> None:
        print(tekst, flush=True)
        self.wpis(tekst)


# ------------------------------------------------------------------------------------------------- paczka i Python

def sprawdz_paczke(paczka: Path) -> tuple[dict, dict[str, str]]:
    """Krok 1: sumy kazdego pliku paczki. Zwraca (wydanie, sumy). Niezgodnosc = blad, zanim cokolwiek zostanie zmienione."""
    plik_sum = paczka / PLIK_SUM_PACZKI
    if not plik_sum.is_file():
        raise BladInstalacji(KOD_PACZKA, f"w katalogu paczki nie ma pliku {PLIK_SUM_PACZKI}",
                             "Rozpakuj CALA paczke wydania (wszystkie pliki) i uruchom zainstaluj.cmd z rozpakowanego katalogu.")
    sumy = wczytaj_sumy(plik_sum)
    roznice = sprawdz_sumy(paczka, sumy)
    if roznice:
        raise BladInstalacji(KOD_PACZKA, f"sumy SHA-256 paczki niezgodne: {len(roznice)} z {len(sumy)} plikow ("
                             + "; ".join(roznice[:10]) + ("; ..." if len(roznice) > 10 else "") + ")",
                             "Paczka jest uszkodzona albo zmieniona - pobierz ja i rozpakuj ponownie. Niczego nie zmieniono.")
    wymagane = (PLIK_WYDANIA, "program/" + PLIK_SUM_PROGRAMU, "program/" + LISTA_PROGRAMU, "program/ustawienia.przyklad.toml")
    brak = [n for n in wymagane if n not in sumy]
    if brak:
        raise BladInstalacji(KOD_PACZKA, "blad wydania: w paczce brakuje " + ", ".join(brak), "Zglos budujacemu paczke.")
    if "program/" + MODUL_SAMOKONTROLI not in sumy:
        raise BladInstalacji(KOD_PACZKA, "blad wydania: paczka nie zawiera modulu samokontroli (stanowisko/samokontrola.py)",
                             "Tej paczki nie da sie zainstalowac - zglos budujacemu paczke. Niczego nie zmieniono.")
    try:
        wydanie = json.loads((paczka / PLIK_WYDANIA).read_text(encoding="utf-8"))
        wersja = wydanie["wersja"]
        wydanie["python"], wydanie["commit"]
    except (ValueError, KeyError, TypeError) as e:
        raise BladInstalacji(KOD_PACZKA, f"blad wydania: {PLIK_WYDANIA} nieczytelny ({type(e).__name__})", "Zglos budujacemu paczke.") from e
    if not isinstance(wersja, str) or not WZOR_WERSJI.fullmatch(wersja):
        raise BladInstalacji(KOD_PACZKA, f"blad wydania: niepoprawny numer wersji {wersja!r}", "Zglos budujacemu paczke.")
    return wydanie, sumy


def sprawdz_pythona(python: Path, wymagana: str = "3.12") -> str:
    """Krok 2: interpreter istnieje, ma wersje ``wymagana`` (np. 3.12), 64 bity i modul venv. Zwraca pelna wersje."""
    rada = (f"Zainstaluj Pythona {wymagana} (64-bit) z python.org albo wskaz go: zainstaluj.cmd /python <sciezka>\\python.exe "
            "(albo zmienna STANOWISKO_PYTHON). Niczego nie zmieniono.")
    kod = "import sys, struct, venv, ensurepip; print('%d.%d.%d %d' % (sys.version_info[:3] + (struct.calcsize('P') * 8,)))"
    try:
        wynik = uruchom([python, "-I", "-c", kod], limit_s=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise BladInstalacji(KOD_PYTHON, f"nie mozna uruchomic Pythona: {python} ({type(e).__name__})", rada) from e
    m = re.fullmatch(r"(\d+\.\d+)\.(\d+) (\d+)", wynik.stdout.strip())
    if wynik.returncode != 0 or not m:
        raise BladInstalacji(KOD_PYTHON, f"{python} nie jest dzialajacym Pythonem z modulem venv (kod {wynik.returncode})", rada)
    if m.group(1) != wymagana or m.group(3) != "64":
        raise BladInstalacji(KOD_PYTHON, f"zla wersja Pythona: {python} to {m.group(1)}.{m.group(2)} ({m.group(3)}-bit), "
                             f"a program wymaga {wymagana} (64-bit)", rada)
    return f"{m.group(1)}.{m.group(2)}"


def katalog_synchronizowany(katalog: Path) -> str | None:
    """Nazwa powodu, gdy katalog lezy w folderze synchronizowanym (OneDrive / SharePoint); inaczej None."""
    pelny = str(katalog.resolve()).lower()
    for zmienna, wartosc in os.environ.items():
        if zmienna.lower().startswith("onedrive") and wartosc and (pelny + os.sep).startswith(wartosc.lower().rstrip("\\/") + os.sep):
            return f"zmienna {zmienna}"
    for czesc in katalog.resolve().parts:
        if czesc.lower().startswith(("onedrive", "sharepoint")):
            return f"katalog {czesc!r} w sciezce"
    return None


def rozmiary_kol(kola: list[Path]) -> tuple[int, int]:
    """(bajty po rozpakowaniu, dlugosc najdluzszej sciezki wzglednej wobec katalogu venv - z zapasem na plik .pyc)."""
    bajty, najdluzsza = 0, 0
    for kolo in kola:
        with zipfile.ZipFile(kolo) as z:
            for wpis in z.infolist():
                bajty += wpis.file_size
                m = re.match(r"[^/]+\.data/(purelib|platlib|data|scripts|headers)/(.*)", wpis.filename)
                if m and m.group(1) == "data":
                    wzgledna = m.group(2)
                elif m and m.group(1) == "scripts":
                    wzgledna = "Scripts/" + m.group(2)
                else:
                    wzgledna = "Lib/site-packages/" + (m.group(2) if m else wpis.filename)
                dlugosc = len(wzgledna) + (len("__pycache__/") + len(".cpython-312.pyc") - 3 if wzgledna.endswith(".py") else 0)
                najdluzsza = max(najdluzsza, dlugosc)
    return bajty, najdluzsza


# ------------------------------------------------------------------------------------- srodowisko wirtualne wersji

class Srodowisko:
    """Operacje na srodowisku wirtualnym wersji (``python -m venv`` + pip bez sieci). Testy podstawiaja atrape."""

    def utworz(self, python: Path, venv: Path) -> None:
        # --copies: pliki, nie dowiazania (na PC dowiazania cudzego konta daja blad 448)
        wynik = uruchom([python, "-I", "-m", "venv", "--copies", venv], limit_s=600)
        if wynik.returncode != 0 or not self.python(venv).is_file():
            raise BladInstalacji(KOD_INSTALACJA, f"nie udalo sie zalozyc srodowiska wirtualnego (kod {wynik.returncode}): "
                                 + (wynik.stderr or wynik.stdout).strip()[-400:],
                                 "Sprawdz miejsce na dysku i prawa zapisu w katalogu instalacji, potem uruchom zainstaluj.cmd ponownie.")
        proba = uruchom([self.python(venv), "-I", "-c", "import sys; print(sys.prefix != sys.base_prefix)"], limit_s=120)
        if proba.returncode != 0 or proba.stdout.strip() != "True":
            raise BladInstalacji(KOD_INSTALACJA, f"srodowisko wirtualne nie startuje (kod {proba.returncode}): "
                                 + (proba.stderr or proba.stdout).strip()[-400:],
                                 "Zglos ten komunikat; wersja biezaca programu zostala bez zmian.")

    def python(self, venv: Path) -> Path:
        return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

    def instaluj(self, venv: Path, katalogi_kol: list[Path], lista: Path, dziennik_pip: Path) -> None:
        polecenie = [self.python(venv), "-I", "-m", "pip", "install", "--isolated", "--no-index", "--only-binary=:all:",
                     "--disable-pip-version-check", "--no-warn-script-location", "--no-cache-dir", "--log", dziennik_pip]
        for k in katalogi_kol:
            polecenie += ["--find-links", k]
        wynik = uruchom(polecenie + ["-r", lista], limit_s=3600)
        if wynik.returncode != 0:
            raise BladInstalacji(KOD_INSTALACJA, f"pip zakonczyl sie bledem (kod {wynik.returncode}): "
                                 + " ".join((wynik.stderr or wynik.stdout).strip().splitlines()[-3:])[-600:],
                                 f"Szczegoly: {dziennik_pip}. Sprawdz miejsce na dysku i uruchom zainstaluj.cmd ponownie - "
                                 "niedokonczona wersja zostanie usunieta i zalozona od nowa; gdy blad wraca, paczka jest niekompletna "
                                 "(zglos budujacemu). Wersja biezaca bez zmian.")

    def pakiety(self, venv: Path) -> dict[str, str]:
        wynik = uruchom([self.python(venv), "-I", "-m", "pip", "list", "--isolated", "--format=json", "--disable-pip-version-check"],
                        limit_s=300)
        try:
            return {normalizuj_nazwe(p["name"]): p["version"] for p in json.loads(wynik.stdout)}
        except (ValueError, KeyError, TypeError) as e:
            raise BladInstalacji(KOD_INSTALACJA, f"pip list nie zwrocil listy pakietow (kod {wynik.returncode})",
                                 "Uruchom zainstaluj.cmd ponownie.") from e


def porownaj_pakiety(zainstalowane: dict[str, str], oczekiwane: dict[str, str]) -> list[str]:
    """Roznice miedzy pakietami srodowiska a lista zamrozona (pakiety zakladane przez venv pomijane); [] = zgodne n z n."""
    roznice = []
    for nazwa, wersja in sorted(oczekiwane.items()):
        if nazwa not in zainstalowane:
            roznice.append(f"brak {nazwa}=={wersja}")
        elif zainstalowane[nazwa] != wersja:
            roznice.append(f"{nazwa}: jest {zainstalowane[nazwa]}, ma byc {wersja}")
    for nazwa in sorted(set(zainstalowane) - set(oczekiwane) - set(PAKIETY_SRODOWISKA)):
        roznice.append(f"nadmiarowy {nazwa}=={zainstalowane[nazwa]}")
    return roznice


# ------------------------------------------------------------------------------------------ ustawienia, baza, blokada

_ZAPYTANIE_PROGRAMU = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
wynik = {}
try:
    from stanowisko import baza, ustawienia
    wynik["schemat"] = int(max(baza.MIGRACJE))
    if len(sys.argv) > 2:
        try:
            ust = ustawienia.wczytaj_ustawienia(sys.argv[2])
            wynik["sciezki"] = dict(ust["sciezki"])
            wynik["baza"] = str(baza.sciezka_bazy(ust))
        except (FileNotFoundError, ustawienia.BladUstawien) as e:
            wynik["blad_ustawien"] = str(e)
except Exception as e:
    wynik["blad_programu"] = "%s: %s" % (type(e).__name__, e)
print(json.dumps(wynik))
"""


def zapytaj_program(python: Path, program: Path, ustawienia: Path | None = None) -> dict:
    """Pyta kod programu (jego ``ustawienia`` i ``baza`` - tylko biblioteka standardowa): wersja schematu bazy obslugiwana
    przez program, ``[sciezki]`` po uzupelnieniu wartosci domyslnych i plik bazy. Niczego nie zapisuje (``-B``)."""
    try:
        wynik = uruchom([python, "-I", "-B", "-X", "utf8", "-c", _ZAPYTANIE_PROGRAMU, program] + ([ustawienia] if ustawienia else []),
                        limit_s=120)
        dane = json.loads(wynik.stdout.strip().splitlines()[-1])
    except (OSError, subprocess.TimeoutExpired, ValueError, IndexError) as e:
        raise BladInstalacji(KOD_PACZKA, f"nie mozna zapytac programu o ustawienia i schemat bazy ({type(e).__name__})",
                             "Blad wydania albo uszkodzona instalacja - zglos ten komunikat.") from e
    if "blad_programu" in dane:
        raise BladInstalacji(KOD_PACZKA, f"modulow programu nie da sie wczytac ({dane['blad_programu']})",
                             "Blad wydania albo uszkodzona instalacja - zglos ten komunikat.")
    return dane


def _wzgledna(wartosc: str) -> bool:
    return not (re.match(r"[A-Za-z]:[\\/]", wartosc) or wartosc.startswith(("/", "\\")))


def ustawienia_ze_wzoru(wzor: bytes, katalog: Path) -> bytes:
    """Wzor ``ustawienia.przyklad.toml`` z kazda WZGLEDNA sciezka sekcji ``[sciezki]`` (``dane/...``) zamieniona na
    bezwzgledna w katalogu instalacji - dane leza wtedy poza katalogiem wersji. Reszta pliku bez zmian (komentarze tez)."""
    korzen = katalog.resolve().as_posix().rstrip("/")
    wiersze, w_sciezkach = [], False
    for wiersz in wzor.decode("utf-8").splitlines(keepends=True):
        sekcja = re.match(r"\s*\[([^\]]+)\]", wiersz)
        if sekcja:
            w_sciezkach = sekcja.group(1).strip() == "sciezki"
        elif w_sciezkach:
            m = re.match(r'(\s*[A-Za-z0-9_]+\s*=\s*")([^"]*)(".*)', wiersz, flags=re.DOTALL)
            if m and m.group(2) and _wzgledna(m.group(2)):
                wiersz = f"{m.group(1)}{korzen}/{m.group(2)}{m.group(3)}"
        wiersze.append(wiersz)
    return "".join(wiersze).encode("utf-8")


def sprawdz_sciezki(dane: dict, katalog: Path) -> Path:
    """Odpowiedz ``zapytaj_program`` -> plik bazy. Blad ustawien albo sciezka wzgledna w ``[sciezki]`` = stop."""
    plik = katalog / PLIK_USTAWIEN
    if "blad_ustawien" in dane:
        raise BladInstalacji(KOD_USTAWIENIA, f"plik ustawien nie przechodzi kontroli tej wersji programu: {dane['blad_ustawien']}",
                             f"Popraw {plik} (wzor: ustawienia.przyklad.toml w katalogu programu) i uruchom polecenie ponownie.")
    wzgledne = sorted(k for k, v in dane["sciezki"].items() if isinstance(v, str) and _wzgledna(v))
    if wzgledne:
        korzen = katalog.resolve().as_posix().rstrip("/")
        wzor = "; ".join(f'{k} = "{korzen}/{dane["sciezki"][k]}"' for k in wzgledne)
        raise BladInstalacji(KOD_USTAWIENIA, "ustawienia.toml: sciezki wzgledne w [sciezki] (" + ", ".join(wzgledne) + ") - program "
                             "liczy je od katalogu WERSJI, wiec dane zniknelyby przy aktualizacji",
                             f"Wpisz w {plik} w sekcji [sciezki] sciezki bezwzgledne, np.: {wzor} (istniejace dane przenies tam "
                             "recznie), potem uruchom polecenie ponownie.")
    return Path(dane["baza"])


def _blokuj(fd: int, zajmij: bool) -> None:
    if os.name == "nt":
        import msvcrt  # noqa: PLC0415

        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_NBLCK if zajmij else msvcrt.LK_UNLCK, 1)
    else:
        import fcntl  # noqa: PLC0415

        fcntl.flock(fd, (fcntl.LOCK_EX | fcntl.LOCK_NB) if zajmij else fcntl.LOCK_UN)


class BlokadaProgramu:
    """Ten sam plik blokady, ktory trzyma dzialajacy program (``aplikacja.BlokadaStanowiska``: ``<baza>.blokada``).

    ``with BlokadaProgramu(plik_bazy):`` - gdy program dziala, rzuca ``BladInstalacji`` ("zamknij program"); w srodku bloku
    programu nie da sie uruchomic. Gdy katalogu bazy jeszcze nie ma (pierwsza instalacja), niczego nie zaklada."""

    def __init__(self, plik_bazy: Path):
        self.plik = plik_bazy.with_name(plik_bazy.name + ".blokada")
        self._fd: int | None = None

    def __enter__(self) -> "BlokadaProgramu":
        if not self.plik.parent.is_dir():
            return self
        try:
            fd = os.open(self.plik, os.O_RDWR | os.O_CREAT, 0o644)
        except OSError as e:
            raise BladInstalacji(KOD_INSTALACJA, f"nie mozna otworzyc pliku blokady programu ({type(e).__name__})",
                                 "Sprawdz prawa zapisu w folderze danych programu.") from e
        try:
            _blokuj(fd, True)
        except OSError:
            os.close(fd)
            raise BladInstalacji(KOD_PROGRAM_DZIALA, 'program "Stanowisko" jest uruchomiony',
                                 "Zamknij program i uruchom polecenie ponownie. Wersja biezaca bez zmian.") from None
        self._fd = fd
        return self

    def __exit__(self, *_) -> None:
        fd, self._fd = self._fd, None
        if fd is not None:
            try:
                _blokuj(fd, False)
            except OSError:
                pass
            finally:
                os.close(fd)


def wersja_schematu(plik_bazy: Path) -> int | None:
    """``PRAGMA user_version`` pliku bazy otwartego tylko do odczytu; None, gdy pliku nie ma albo nie jest baza SQLite."""
    if not plik_bazy.is_file() or plik_bazy.stat().st_size == 0:
        return None
    try:
        pol = sqlite3.connect(f"{plik_bazy.resolve().as_uri()}?mode=ro", uri=True)
        try:
            return int(pol.execute("PRAGMA user_version").fetchone()[0])
        finally:
            pol.close()
    except sqlite3.Error:
        return None


def liczniki_tabel(plik_bazy: Path) -> dict[str, int]:
    """{tabela: liczba wierszy} - same liczniki, bez tresci (do ostrzezenia przed przywroceniem kopii)."""
    pol = sqlite3.connect(f"{plik_bazy.resolve().as_uri()}?mode=ro", uri=True)
    try:
        tabele = [w[0] for w in pol.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        return {t: int(pol.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]) for t in tabele}
    finally:
        pol.close()


def kopia_bazy(plik_bazy: Path, wersja: str, teraz: dt.datetime) -> Path | None:
    """Kopia pliku bazy przed pierwszym uruchomieniem wersji ``wersja``: ``<katalog bazy>/kopie/<baza>_przed_<wersja>_
    <data>_<godzina>_v<schemat>.sqlite`` (mechanizm kopii SQLite - spojna takze z plikiem -wal). Brak bazy = None."""
    schemat = wersja_schematu(plik_bazy)
    if not plik_bazy.is_file() or plik_bazy.stat().st_size == 0:
        return None
    katalog = plik_bazy.parent / "kopie"
    katalog.mkdir(parents=True, exist_ok=True)
    rdzen = f"{plik_bazy.stem}_przed_{wersja}_{teraz:%Y%m%d_%H%M%S}_v{schemat if schemat is not None else 'x'}"
    cel, n = katalog / f"{rdzen}.sqlite", 1
    while cel.exists():
        n += 1
        cel = katalog / f"{rdzen}_{n}.sqlite"
    tymczasowy = cel.with_name(cel.name + ".nowy")
    try:
        if schemat is None:
            raise sqlite3.DatabaseError("plik nie jest baza SQLite")
        zrodlo = sqlite3.connect(f"{plik_bazy.resolve().as_uri()}?mode=ro", uri=True)
        try:
            docelowa = sqlite3.connect(tymczasowy)
            try:
                zrodlo.backup(docelowa)
            finally:
                docelowa.close()
        finally:
            zrodlo.close()
    except sqlite3.Error:
        shutil.copy2(plik_bazy, tymczasowy)  # plik uszkodzony albo nie-SQLite: kopia bajtowa (lepsza niz zadna)
    suma = sha256_pliku(tymczasowy)
    for istniejaca in sorted(katalog.glob(f"{plik_bazy.stem}_przed_{wersja}_*.sqlite"), reverse=True):
        if istniejaca.stat().st_size == tymczasowy.stat().st_size and sha256_pliku(istniejaca) == suma:
            tymczasowy.unlink()  # powtorzona proba instalacji tej samej wersji przy niezmienionej bazie: jedna kopia wystarczy
            return istniejaca
    os.replace(tymczasowy, cel)
    return cel


def znajdz_kopie(plik_bazy: Path, wersja_biezaca: str, schemat_max: int) -> Path | None:
    """Kopia do przywrocenia przy powrocie: najpierw zrobiona przed instalacja wersji biezacej, potem inne kopie instalatora,
    na koncu kopie programu sprzed migracji (``<baza>.kopia_v*``) - pierwsza o schemacie nie nowszym niz ``schemat_max``."""
    kopie = plik_bazy.parent / "kopie"
    kandydaci = sorted(kopie.glob(f"{plik_bazy.stem}_przed_{wersja_biezaca}_*.sqlite"), reverse=True)
    kandydaci += sorted((p for p in kopie.glob(f"{plik_bazy.stem}_przed_*.sqlite") if p not in kandydaci),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    kandydaci += sorted(plik_bazy.parent.glob(f"{plik_bazy.stem}.kopia_v*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
    for kandydat in kandydaci:
        schemat = wersja_schematu(kandydat)
        if schemat is not None and schemat <= schemat_max:
            return kandydat
    return None


def opis_strat(plik_bazy: Path, kopia: Path) -> list[str]:
    """Wiersze ostrzezenia: ile wpisow przybylo w bazie od zrobienia kopii (liczniki tabel) i od kiedy."""
    teraz, dawniej = liczniki_tabel(plik_bazy), liczniki_tabel(kopia)
    przyrosty = {t: n - dawniej.get(t, 0) for t, n in teraz.items() if n != dawniej.get(t, 0)}
    czas = dt.datetime.fromtimestamp(kopia.stat().st_mtime)
    wiersze = [f"Kopia sprzed aktualizacji: {kopia.name} z {czas:%Y-%m-%d %H:%M} (schemat {wersja_schematu(kopia)}).",
               f"Po przywroceniu z bazy roboczej zniknie wszystko, co zapisano po tej chwili: {sum(max(0, v) for v in przyrosty.values())} "
               f"wpisow w {sum(1 for v in przyrosty.values() if v > 0)} tabelach."]
    wiersze += [f"  tabela {t}: {dawniej.get(t, 0)} w kopii, {teraz[t]} teraz ({v:+d})" for t, v in sorted(przyrosty.items())]
    return wiersze


def przywroc_kopie(plik_bazy: Path, kopia: Path, schemat: int, teraz: dt.datetime) -> Path:
    """Odklada biezaca baze (z plikami -wal / -shm / -journal) do ``kopie/`` i wstawia w jej miejsce ``kopia``. Nic nie kasuje."""
    katalog = plik_bazy.parent / "kopie"
    katalog.mkdir(parents=True, exist_ok=True)
    rdzen = f"{plik_bazy.stem}_odlozona_v{schemat}_{teraz:%Y%m%d_%H%M%S}"
    odlozona, n = katalog / f"{rdzen}.sqlite", 1
    while odlozona.exists():
        n += 1
        odlozona = katalog / f"{rdzen}_{n}.sqlite"
    tymczasowy = plik_bazy.with_name(plik_bazy.name + ".nowy")
    shutil.copy2(kopia, tymczasowy)  # najpierw gotowa kopia obok, dopiero potem ruszamy baze
    os.replace(plik_bazy, odlozona)
    for przyrostek in ("-wal", "-shm", "-journal"):
        dodatkowy = plik_bazy.with_name(plik_bazy.name + przyrostek)
        if dodatkowy.exists():
            os.replace(dodatkowy, odlozona.with_name(odlozona.name + przyrostek))
    os.replace(tymczasowy, plik_bazy)
    return odlozona


# --------------------------------------------------------------------------------------------------- katalog wersji

def katalog_wersji(katalog: Path, wersja: str) -> Path:
    return katalog / KATALOG_WERSJI / wersja


def stan_wersji(katalog: Path, wersja: str) -> str:
    """``brak`` / ``niedokonczona`` (znacznik albo brak zapisu instalacji) / ``zainstalowana``."""
    kw = katalog_wersji(katalog, wersja)
    if not kw.exists():
        return "brak"
    if (kw / ZNACZNIK_NIEDOKONCZONEJ).exists() or not (kw / PLIK_INSTALACJI).is_file():
        return "niedokonczona"
    return "zainstalowana"


def lista_wersji(katalog: Path) -> list[dict]:
    biezaca, poprzednia = czytaj_wskaznik(katalog, PLIK_BIEZACEJ), czytaj_wskaznik(katalog, PLIK_POPRZEDNIEJ)
    wersje = []
    for kw in sorted((katalog / KATALOG_WERSJI).iterdir()) if (katalog / KATALOG_WERSJI).is_dir() else []:
        if not kw.is_dir():
            continue
        try:
            zapis = json.loads((kw / PLIK_INSTALACJI).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            zapis = {}
        wersje.append({"wersja": kw.name, "stan": stan_wersji(katalog, kw.name), "biezaca": kw.name == biezaca,
                       "poprzednia": kw.name == poprzednia, "zainstalowano": zapis.get("zainstalowano", "?"),
                       "commit": zapis.get("commit", "?"), "schemat_bazy": zapis.get("schemat_bazy")})
    return wersje


def przelacz(katalog: Path, nowa: str) -> str | None:
    """Przelacza wskaznik wersji biezacej na ``nowa`` (zapis atomowy); dotychczasowa biezaca staje sie poprzednia."""
    biezaca = czytaj_wskaznik(katalog, PLIK_BIEZACEJ)
    if biezaca == nowa:
        return czytaj_wskaznik(katalog, PLIK_POPRZEDNIEJ)
    if biezaca is not None:
        zapisz_atomowo(katalog / PLIK_POPRZEDNIEJ, (biezaca + "\r\n").encode("ascii"))
    zapisz_atomowo(katalog / PLIK_BIEZACEJ, (nowa + "\r\n").encode("ascii"))
    return biezaca


def zapisz_skrypty(program: Path, katalog: Path) -> int:
    """Kopiuje wzory skryptow uruchamiajacych z ``program/instalacja/wzory`` do katalogu instalacji; zwraca liczbe zmienionych."""
    zmienione = 0
    for nazwa in WZORY_SKRYPTOW:
        tresc = (program / "instalacja" / "wzory" / nazwa).read_bytes()
        cel = katalog / nazwa
        if not cel.is_file() or cel.read_bytes() != tresc:
            zapisz_atomowo(cel, tresc)
            zmienione += 1
    return zmienione


def utworz_skrot(katalog: Path, gdzie: Path | None) -> Path | None:
    """Skrot ``Stanowisko.lnk`` do ``<KATALOG>/Stanowisko.cmd`` na pulpicie (albo w ``gdzie``); None, gdy sie nie udalo."""
    skrypt = ("$k = $env:STANOWISKO_SKROT_KATALOG; if (-not $k) { $k = [Environment]::GetFolderPath('Desktop') }; "
              "$p = Join-Path $k 'Stanowisko.lnk'; $s = (New-Object -ComObject WScript.Shell).CreateShortcut($p); "
              "$s.TargetPath = $env:STANOWISKO_SKROT_CEL; $s.WorkingDirectory = $env:STANOWISKO_SKROT_ROBOCZY; "
              "$s.Description = 'Stanowisko kontroli cyrkonii'; $s.Save(); Write-Output $p")
    env = dict(os.environ, STANOWISKO_SKROT_KATALOG=str(gdzie) if gdzie else "", STANOWISKO_SKROT_CEL=str(katalog / "Stanowisko.cmd"),
               STANOWISKO_SKROT_ROBOCZY=str(katalog))
    try:
        wynik = uruchom(["powershell", "-NoProfile", "-NonInteractive", "-Command", skrypt], env=env, limit_s=120)
    except (OSError, subprocess.TimeoutExpired):
        return None
    sciezka = Path(wynik.stdout.strip().splitlines()[-1]) if wynik.returncode == 0 and wynik.stdout.strip() else None
    return sciezka if sciezka is not None and sciezka.is_file() else None


def uruchom_samokontrole(python: Path, program: Path, ustawienia: Path, bez_sieci: bool) -> tuple[int, str]:
    """Samokontrola wersji wg umowy A11s: ``python -m stanowisko.samokontrola --ustawienia PLIK --sumy PLIK [--bez-sieci]``.
    Zwraca (kod wyjscia, wyjscie tekstowe). Brak modulu w katalogu programu = blad wydania."""
    if not (program / MODUL_SAMOKONTROLI).is_file():
        raise BladInstalacji(KOD_PACZKA, "blad wydania: w katalogu programu nie ma modulu samokontroli (stanowisko/samokontrola.py)",
                             "Zglos budujacemu paczke; wersja biezaca bez zmian.")
    polecenie = [python, "-B", "-X", "utf8", "-m", "stanowisko.samokontrola", "--ustawienia", ustawienia,
                 "--sumy", program / PLIK_SUM_PROGRAMU] + (["--bez-sieci"] if bez_sieci else [])
    try:
        wynik = uruchom(polecenie, cwd=program, env=srodowisko_procesu(), limit_s=LIMIT_SAMOKONTROLI_S)
    except subprocess.TimeoutExpired:
        return KOD_SAMOKONTROLA_NIEWYKONANA, f"samokontrola nie skonczyla sie w {LIMIT_SAMOKONTROLI_S} s"
    except OSError as e:
        return KOD_SAMOKONTROLA_NIEWYKONANA, f"samokontroli nie dalo sie uruchomic ({type(e).__name__})"
    return wynik.returncode, (wynik.stdout + ("\n" + wynik.stderr if wynik.stderr.strip() else "")).strip()


def streszczenie_samokontroli(wyjscie: str) -> list[str]:
    """Do dziennika: poziom i kod kazdego wiersza OSTRZEZENIE / BLAD (bez opisu - moze zawierac sciezki) i wiersz koncowy."""
    wiersze = []
    for wiersz in wyjscie.splitlines():
        m = re.match(r"(OSTRZEZENIE|BLAD) ([^:\s]+):", wiersz)
        if m:
            wiersze.append(f"samokontrola: {m.group(1)} {m.group(2)}")
        elif wiersz.startswith("SAMOKONTROLA:"):
            wiersze.append(wiersz.strip())
    return wiersze


# ------------------------------------------------------------------------------------------------------ instalacja

def _instaluj_wersje(paczka: Path, sumy: dict[str, str], wydanie: dict, katalog: Path, python: Path, testy: bool,
                     srodowisko: Srodowisko, dziennik: Dziennik, teraz: dt.datetime, wersja_pythona: str, schemat: int) -> None:
    """Zaklada katalog wersji od zera: znacznik, pliki programu, venv, pakiety z kol paczki, kontrola wersji pakietow."""
    wersja = wydanie["wersja"]
    kw = katalog_wersji(katalog, wersja)
    kw.mkdir(parents=True)
    (kw / ZNACZNIK_NIEDOKONCZONEJ).write_text(f"Instalacja wersji {wersja} rozpoczeta {teraz:%Y-%m-%d %H:%M:%S} i niedokonczona.\r\n"
                                              "Katalog zostanie usuniety przy nastepnym uruchomieniu zainstaluj.cmd.\r\n", encoding="ascii")
    pliki = sorted(n for n in sumy if n.startswith("program/"))
    for nazwa in pliki:
        cel = kw / nazwa
        cel.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(paczka / nazwa, cel)
    shutil.copyfile(paczka / PLIK_WYDANIA, kw / PLIK_WYDANIA)
    program = kw / "program"
    roznice = sprawdz_sumy(program, wczytaj_sumy(program / PLIK_SUM_PROGRAMU))
    if roznice:
        raise BladInstalacji(KOD_INSTALACJA, f"pliki programu po skopiowaniu niezgodne z {PLIK_SUM_PROGRAMU}: " + "; ".join(roznice[:10]),
                             "Sprawdz dysk i uruchom zainstaluj.cmd ponownie.")
    dziennik.krok(f"      program: skopiowano {len(pliki)} plikow, sumy zgodne")
    venv = kw / "venv"
    srodowisko.utworz(python, venv)
    dziennik.krok("      srodowisko wirtualne zalozone i startuje")
    oczekiwane = wczytaj_liste_zamrozona(program / LISTA_PROGRAMU)
    dziennik.krok(f"      instalacja {len(oczekiwane)} pakietow z kol paczki (bez sieci) - to trwa kilka minut...")
    srodowisko.instaluj(venv, [paczka / "kola"], program / LISTA_PROGRAMU, kw / "pip.log")
    if testy:
        oczekiwane.update(_instaluj_testy(paczka, program, venv, kw, srodowisko, dziennik))
    roznice = porownaj_pakiety(srodowisko.pakiety(venv), oczekiwane)
    if roznice:
        raise BladInstalacji(KOD_INSTALACJA, "pakiety srodowiska niezgodne z lista zamrozona: " + "; ".join(roznice[:10]),
                             "Uruchom zainstaluj.cmd ponownie; gdy blad wraca - blad wydania, zglos budujacemu paczke.")
    dziennik.krok(f"      pakiety zgodne z lista zamrozona: {len(oczekiwane)} z {len(oczekiwane)}")
    zapis = {"wersja": wersja, "commit": wydanie.get("commit"), "zainstalowano": f"{teraz:%Y-%m-%d %H:%M:%S}", "python": wersja_pythona,
             "pakiety": len(oczekiwane), "testy": bool(testy), "schemat_bazy": schemat,
             "sha256_wydania": sha256_pliku(kw / PLIK_WYDANIA)}
    (kw / PLIK_INSTALACJI).write_text(json.dumps(zapis, indent=1, sort_keys=True) + "\n", encoding="ascii")
    (kw / ZNACZNIK_NIEDOKONCZONEJ).unlink()


def _instaluj_testy(paczka: Path, program: Path, venv: Path, kw: Path, srodowisko: Srodowisko, dziennik: Dziennik) -> dict[str, str]:
    lista = program / LISTA_TESTOW
    if not lista.is_file() or not (paczka / "kola_testy").is_dir():
        raise BladInstalacji(KOD_PACZKA, "paczka nie zawiera zestawu testowego (kola_testy, zamrozone_testy.txt)",
                             "Uruchom zainstaluj.cmd bez /testy albo popros o paczke z zestawem testowym.")
    pakiety = wczytaj_liste_zamrozona(lista)
    srodowisko.instaluj(venv, [paczka / "kola", paczka / "kola_testy"], lista, kw / "pip_testy.log")
    dziennik.krok(f"      zestaw testowy (pytest): {len(pakiety)} pakietow - tylko na zadanie /testy")
    return pakiety


BRAK_TESTOW = "brak zestawu testowego"


def _doinstaluj_testy(paczka: Path, katalog: Path, wersja: str, srodowisko: Srodowisko, dziennik: Dziennik) -> None:
    """``/testy`` na wersji juz zainstalowanej: doklada sam zestaw testowy (bez zakladania wersji od nowa) i sprawdza pakiety."""
    kw = katalog_wersji(katalog, wersja)
    program, venv = kw / "program", kw / "venv"
    oczekiwane = wczytaj_liste_zamrozona(program / LISTA_PROGRAMU)
    oczekiwane.update(_instaluj_testy(paczka, program, venv, kw, srodowisko, dziennik))
    roznice = porownaj_pakiety(srodowisko.pakiety(venv), oczekiwane)
    if roznice:
        raise BladInstalacji(KOD_INSTALACJA, "pakiety srodowiska niezgodne z lista zamrozona: " + "; ".join(roznice[:10]),
                             "Usun te wersje (Wersje.cmd /usun) albo uruchom zainstaluj.cmd ponownie.")
    zapis = json.loads((kw / PLIK_INSTALACJI).read_text(encoding="ascii"))
    zapis.update(pakiety=len(oczekiwane), testy=True)
    zapisz_atomowo(kw / PLIK_INSTALACJI, (json.dumps(zapis, indent=1, sort_keys=True) + "\n").encode("ascii"))
    dziennik.krok(f"      pakiety zgodne z lista zamrozona: {len(oczekiwane)} z {len(oczekiwane)}")


def _zgodna_z_paczka(paczka: Path, katalog: Path, wersja: str, testy: bool, srodowisko: Srodowisko) -> tuple[bool, str]:
    """Czy zainstalowana wersja jest ta sama budowa co paczka i jest cala: (True, "") albo (False, powod)."""
    kw = katalog_wersji(katalog, wersja)
    if not (kw / PLIK_WYDANIA).is_file() or (kw / PLIK_WYDANIA).read_bytes() != (paczka / PLIK_WYDANIA).read_bytes():
        return False, "inna budowa o tym samym numerze wersji"
    program = kw / "program"
    if not (program / PLIK_SUM_PROGRAMU).is_file() or (program / PLIK_SUM_PROGRAMU).read_bytes() != (paczka / "program" / PLIK_SUM_PROGRAMU).read_bytes():
        return False, "brak albo zmieniony plik sum programu"
    roznice = sprawdz_sumy(program, wczytaj_sumy(program / PLIK_SUM_PROGRAMU))
    if roznice:
        return False, f"pliki programu niezgodne z sumami ({len(roznice)})"
    venv = kw / "venv"
    if not srodowisko.python(venv).is_file():
        return False, "brak srodowiska wirtualnego"
    try:
        zainstalowane = srodowisko.pakiety(venv)
        oczekiwane = wczytaj_liste_zamrozona(program / LISTA_PROGRAMU)
        z_testami = dict(oczekiwane, **(wczytaj_liste_zamrozona(program / LISTA_TESTOW) if (program / LISTA_TESTOW).is_file() else {}))
    except (BladInstalacji, OSError, subprocess.TimeoutExpired):
        return False, "srodowisko wirtualne nie odpowiada"
    if porownaj_pakiety(zainstalowane, z_testami) == []:
        return True, ""
    if porownaj_pakiety(zainstalowane, oczekiwane) == []:
        return (False, BRAK_TESTOW) if testy else (True, "")
    return False, "pakiety srodowiska niezgodne z lista zamrozona"


def zainstaluj(paczka: Path, katalog: Path, python: Path, *, testy: bool = False, skrot: bool = False, skrot_katalog: Path | None = None,
               bez_sieci: bool = False, min_wolne_mb: int | None = None, srodowisko: Srodowisko | None = None,
               zegar=dt.datetime.now) -> int:
    """Instalacja albo aktualizacja z rozpakowanej paczki. Zwraca kod wyjscia (0 = wersja z paczki jest wersja biezaca)."""
    srodowisko = srodowisko or Srodowisko()
    paczka, katalog = paczka.resolve(), katalog.resolve()
    dziennik = Dziennik(katalog, "zainstaluj", zegar)  # wpisy trafiaja do pliku dopiero, gdy katalog instalacji istnieje
    try:
        print(f"[1/9] Sumy SHA-256 paczki ({paczka})...", flush=True)
        wydanie, sumy = sprawdz_paczke(paczka)
        wersja = wydanie["wersja"]
        dziennik.operacja = f"zainstaluj {wersja}"
        print(f"      zgodne {len(sumy)} z {len(sumy)}; wersja {wersja}, commit {str(wydanie.get('commit'))[:12]}", flush=True)

        print(f"[2/9] Python {wydanie['python']}...", flush=True)
        wersja_pythona = sprawdz_pythona(python, str(wydanie["python"]))
        print(f"      {python}: {wersja_pythona}", flush=True)

        print(f"[3/9] Katalog instalacji {katalog}...", flush=True)
        powod = katalog_synchronizowany(katalog)
        if powod:
            raise BladInstalacji(KOD_INSTALACJA, f"katalog instalacji lezy w folderze synchronizowanym ({powod})",
                                 "Wybierz katalog poza OneDrive / SharePoint, np. zainstaluj.cmd /katalog C:\\Stanowisko.")
        kola = sorted((paczka / "kola").glob("*.whl")) + (sorted((paczka / "kola_testy").glob("*.whl")) if testy else [])
        bajty_kol, najdluzsza = rozmiary_kol(kola)
        korzen_venv = katalog_wersji(katalog, wersja) / "venv"
        if os.name == "nt" and len(str(korzen_venv)) + 1 + najdluzsza > LIMIT_SCIEZKI:
            raise BladInstalacji(KOD_INSTALACJA, f"sciezka katalogu instalacji jest za dluga ({len(str(katalog))} znakow; pliki pakietow "
                                 f"przekroczylyby {LIMIT_SCIEZKI} znakow)", "Wybierz krotszy katalog, np. zainstaluj.cmd /katalog C:\\Stanowisko.")
        try:
            katalog.mkdir(parents=True, exist_ok=True)
            (katalog / KATALOG_WERSJI).mkdir(exist_ok=True)
            proba = katalog / ".proba_zapisu"
            proba.write_bytes(b"")
            proba.unlink()
        except OSError as e:
            raise BladInstalacji(KOD_INSTALACJA, f"nie mozna pisac w katalogu instalacji ({type(e).__name__})",
                                 "Wybierz katalog, w ktorym to konto moze zapisywac: zainstaluj.cmd /katalog <KATALOG>.") from e
        dziennik.wpis(f"START: paczka wersja {wersja}, commit {wydanie.get('commit')}, sumy paczki zgodne {len(sumy)} z {len(sumy)}, "
                      f"Python {wersja_pythona}")
        biezaca = czytaj_wskaznik(katalog, PLIK_BIEZACEJ)
        dziennik.krok(f"      wersja biezaca: {biezaca or 'brak (pierwsza instalacja)'}")
        for w in lista_wersji(katalog):  # sprzatanie po przerwanych probach
            if w["stan"] == "niedokonczona" and not w["biezaca"]:
                usun_katalog(katalog_wersji(katalog, w["wersja"]))
                dziennik.krok(f"      usunieto niedokonczona instalacje wersji {w['wersja']}")

        print("[4/9] Ustawienia...", flush=True)
        plik_ustawien = katalog / PLIK_USTAWIEN
        if not plik_ustawien.exists():
            zapisz_atomowo(plik_ustawien, ustawienia_ze_wzoru((paczka / "program" / "ustawienia.przyklad.toml").read_bytes(), katalog))
            (katalog / "dane").mkdir(exist_ok=True)
            dziennik.krok(f"      zalozono {plik_ustawien.name} ze wzoru (sciezki danych: {katalog.as_posix()}/dane/...) - UZUPELNIJ foldery "
                          "pracy w [sciezki] i osoby w [sesja] operatorzy")
            suma_ustawien = None
        else:
            suma_ustawien = sha256_pliku(plik_ustawien)
            dziennik.krok(f"      istniejacy {plik_ustawien.name} zostaje bez zmian (SHA-256 {suma_ustawien[:16]}...)")
        odpowiedz = zapytaj_program(python, paczka / "program", plik_ustawien)
        plik_bazy = sprawdz_sciezki(odpowiedz, katalog)
        with BlokadaProgramu(plik_bazy):
            pass  # program dziala = stop juz teraz, przed dluga instalacja pakietow

        print(f"[5/9] Katalog wersji {wersja}...", flush=True)
        stan = stan_wersji(katalog, wersja)
        if stan == "zainstalowana":
            zgodna, powod = _zgodna_z_paczka(paczka, katalog, wersja, testy, srodowisko)
            if zgodna:
                dziennik.krok(f"      wersja {wersja} jest juz zainstalowana i zgodna z paczka - pliki bez zmian")
            elif powod == BRAK_TESTOW:
                dziennik.krok(f"      wersja {wersja} jest juz zainstalowana i zgodna z paczka - dokladam zestaw testowy")
                _doinstaluj_testy(paczka, katalog, wersja, srodowisko, dziennik)
            else:
                dziennik.krok(f"      wersja {wersja} jest zainstalowana, ale: {powod} - naprawa (instalacja od nowa)")
                stan = "do_naprawy"
        if stan != "zainstalowana":
            if stan != "brak":
                with BlokadaProgramu(plik_bazy):  # naprawa wersji biezacej tylko przy zamknietym programie
                    usun_katalog(katalog_wersji(katalog, wersja))
            potrzeba = int(bajty_kol * ZAPAS_PYC + sum((paczka / n).stat().st_size for n in sumy if n.startswith("program/"))) // 2**20 + ZAPAS_MB
            potrzeba = potrzeba if min_wolne_mb is None else min_wolne_mb
            wolne = shutil.disk_usage(katalog).free // 2**20
            if wolne < potrzeba:
                raise BladInstalacji(KOD_INSTALACJA, f"za malo miejsca na dysku: potrzeba ok. {potrzeba} MB, wolne {wolne} MB",
                                     "Zwolnij miejsce albo wybierz inny dysk (/katalog) i uruchom zainstaluj.cmd ponownie. "
                                     "Wersja biezaca bez zmian.")
            dziennik.krok(f"      miejsce na dysku: potrzeba ok. {potrzeba} MB, wolne {wolne} MB")
            _instaluj_wersje(paczka, sumy, wydanie, katalog, python, testy, srodowisko, dziennik, zegar(), wersja_pythona,
                             int(odpowiedz["schemat"]))
        kw = katalog_wersji(katalog, wersja)
        program, python_wersji = kw / "program", srodowisko.python(kw / "venv")

        print("[6/9] Kopia bazy...", flush=True)
        if wersja == biezaca:
            dziennik.krok("      ta sama wersja co biezaca - kopia bazy niepotrzebna")
        else:
            with BlokadaProgramu(plik_bazy):
                kopia = kopia_bazy(plik_bazy, wersja, zegar())
            dziennik.krok(f"      kopia bazy: kopie/{kopia.name} (schemat bazy {wersja_schematu(kopia)}, program {wersja}: {odpowiedz['schemat']})"
                          if kopia else "      bazy jeszcze nie ma - program zalozy ja przy pierwszym uruchomieniu")

        print(f"[7/9] Samokontrola wersji {wersja}...", flush=True)
        kod, wyjscie = uruchom_samokontrole(python_wersji, program, plik_ustawien, bez_sieci)
        print("\n".join("      " + w for w in wyjscie.splitlines()), flush=True)
        for wiersz in streszczenie_samokontroli(wyjscie):
            dziennik.wpis(wiersz)
        dziennik.wpis(f"samokontrola: kod wyjscia {kod}")
        if suma_ustawien is not None and sha256_pliku(plik_ustawien) != suma_ustawien:
            raise BladInstalacji(KOD_INSTALACJA, f"{plik_ustawien.name} zmienil sie w trakcie instalacji", "Zglos ten komunikat.")
        if kod != 0:
            zostaje = f"wersja biezaca zostaje {biezaca}" if biezaca else "wersji biezacej nadal nie ma"
            if kod == 1:
                raise BladInstalacji(KOD_SAMOKONTROLA_CZERWONA, f"samokontrola wersji {wersja} zglosila bledy - {zostaje}",
                                     f"Popraw to, co wskazuja wiersze BLAD powyzej (zwykle foldery w {plik_ustawien}), i uruchom "
                                     "zainstaluj.cmd ponownie - pakiety nie beda instalowane drugi raz.")
            raise BladInstalacji(KOD_SAMOKONTROLA_NIEWYKONANA, f"samokontroli wersji {wersja} nie dalo sie wykonac (kod {kod}) - {zostaje}",
                                 f"Popraw przyczyne podana powyzej (zwykle plik {plik_ustawien}) i uruchom zainstaluj.cmd ponownie.")

        print("[8/9] Przelaczenie wersji biezacej...", flush=True)
        with BlokadaProgramu(plik_bazy):
            zapisz_skrypty(program, katalog)
            poprzednia = przelacz(katalog, wersja)
        dziennik.krok(f"      wersja biezaca: {wersja}; poprzednia: {poprzednia or 'brak'}")

        print("[9/9] Skrot na pulpicie...", flush=True)
        if skrot:
            plik_skrotu = utworz_skrot(katalog, skrot_katalog)
            dziennik.krok("      skrot Stanowisko.lnk zalozony" if plik_skrotu else
                          "      OSTRZEZENIE: skrotu nie udalo sie zalozyc - uruchamiaj Stanowisko.cmd z katalogu instalacji")
        else:
            print("      pominiety (opcja /skrot zaklada skrot Stanowisko na pulpicie)", flush=True)
        dziennik.krok(f"INSTALACJA: GOTOWA - wersja biezaca {wersja} (poprzednia: {poprzednia or 'brak'}). Uruchamianie: {katalog / 'Stanowisko.cmd'}")
        return KOD_OK
    except BladInstalacji as e:
        return _zglos(dziennik, "INSTALACJA", e)
    except KeyboardInterrupt:
        return _zglos(dziennik, "INSTALACJA", BladInstalacji(KOD_INSTALACJA, "instalacja przerwana",
                      "Uruchom zainstaluj.cmd ponownie - niedokonczona wersja zostanie usunieta. Wersja biezaca bez zmian."))
    except Exception as e:  # noqa: BLE001 - kazdy blad = komunikat dla czlowieka, slad do dziennika
        dziennik.wpis(traceback.format_exc())
        return _zglos(dziennik, "INSTALACJA", BladInstalacji(KOD_INSTALACJA, f"nieoczekiwany blad instalatora ({type(e).__name__}: {e})",
                      "Uruchom zainstaluj.cmd ponownie; gdy blad wraca, zglos go razem z plikiem dziennik_instalacji.txt."))


def _zglos(dziennik: Dziennik, operacja: str, e: BladInstalacji) -> int:
    dziennik.krok(f"BLAD: {e.opis}")
    if e.rada:
        dziennik.krok(f"CO ZROBIC: {e.rada}")
    biezaca = czytaj_wskaznik(dziennik.katalog, PLIK_BIEZACEJ)
    dziennik.krok(f"{operacja}: NIEUDANA (kod {e.kod}) - wersja biezaca bez zmian: {biezaca or 'brak'}")
    return e.kod


# ----------------------------------------------------------------------------------------- powrot, lista, usuwanie

def wroc(katalog: Path, *, przywroc: bool = False, srodowisko: Srodowisko | None = None, zegar=dt.datetime.now) -> int:
    """Powrot do poprzedniej wersji: przelacza wskaznik; gdy baza ma schemat nowszy niz obsluguje poprzednia wersja,
    wymaga jawnego ``przywroc`` (opcja /przywroc-kopie) i wtedy wstawia kopie sprzed aktualizacji, a biezaca baze odklada."""
    srodowisko = srodowisko or Srodowisko()
    katalog = katalog.resolve()
    dziennik = Dziennik(katalog, "wroc", zegar)
    try:
        biezaca, poprzednia = czytaj_wskaznik(katalog, PLIK_BIEZACEJ), czytaj_wskaznik(katalog, PLIK_POPRZEDNIEJ)
        if biezaca is None:
            raise BladInstalacji(KOD_BRAK_WERSJI, f"w {katalog} nie ma zainstalowanej wersji biezacej", "Uruchom zainstaluj.cmd z paczki wydania.")
        if poprzednia is None or poprzednia == biezaca or stan_wersji(katalog, poprzednia) != "zainstalowana":
            raise BladInstalacji(KOD_BRAK_WERSJI, f"nie ma poprzedniej wersji, do ktorej mozna wrocic (biezaca: {biezaca})",
                                 "Zainstaluj potrzebna wersje z jej paczki wydania (zainstaluj.cmd).")
        dziennik.operacja = f"wroc {biezaca} -> {poprzednia}"
        dziennik.krok(f"[1/4] Powrot z wersji {biezaca} do {poprzednia}...")
        kw = katalog_wersji(katalog, poprzednia)
        program, python_wersji = kw / "program", srodowisko.python(kw / "venv")
        plik_ustawien = katalog / PLIK_USTAWIEN
        suma_ustawien = sha256_pliku(plik_ustawien) if plik_ustawien.is_file() else None
        odpowiedz = zapytaj_program(python_wersji, program, plik_ustawien)
        if "blad_ustawien" in odpowiedz:
            raise BladInstalacji(KOD_USTAWIENIA, f"wersja {poprzednia} nie przyjmuje obecnego pliku ustawien: {odpowiedz['blad_ustawien']}",
                                 f"Usun albo zakomentuj w {plik_ustawien} wskazany klucz (dodany dla nowszej wersji) i uruchom "
                                 "Wroc_do_poprzedniej.cmd ponownie. Wersja biezaca bez zmian.")
        plik_bazy = sprawdz_sciezki(odpowiedz, katalog)
        schemat_programu = int(odpowiedz["schemat"])
        with BlokadaProgramu(plik_bazy):
            schemat_bazy = wersja_schematu(plik_bazy)
            dziennik.krok(f"[2/4] Baza: schemat {schemat_bazy if schemat_bazy is not None else 'brak pliku'}; wersja {poprzednia} "
                          f"obsluguje schemat do {schemat_programu}")
            if schemat_bazy is not None and schemat_bazy > schemat_programu:
                kopia = znajdz_kopie(plik_bazy, biezaca, schemat_programu)
                print(f"      UWAGA: wersja {biezaca} zmienila schemat bazy - wersja {poprzednia} tej bazy NIE otworzy.", flush=True)
                if kopia is None:
                    raise BladInstalacji(KOD_BAZA_NOWSZA, f"baza ma schemat {schemat_bazy}, a nie ma kopii bazy o schemacie do "
                                         f"{schemat_programu} (szukano w {plik_bazy.parent / 'kopie'})",
                                         f"Powrot do {poprzednia} bez kopii nie jest mozliwy - zostan przy wersji {biezaca} albo zglos "
                                         "sprawe. Niczego nie zmieniono.")
                for wiersz in opis_strat(plik_bazy, kopia):
                    dziennik.krok("      " + wiersz)
                if not przywroc:
                    raise BladInstalacji(KOD_BAZA_NOWSZA, f"powrot do {poprzednia} wymaga przywrocenia kopii bazy sprzed aktualizacji",
                                         "Jesli zgadzasz sie na utrate wpisow wymienionych powyzej, uruchom: Wroc_do_poprzedniej.cmd "
                                         "/przywroc-kopie (biezaca baza zostanie odlozona do dane\\kopie, nie skasowana). Niczego nie zmieniono.")
                odlozona = przywroc_kopie(plik_bazy, kopia, schemat_bazy, zegar())
                dziennik.krok(f"      przywrocono kopie {kopia.name}; dotychczasowa baza odlozona jako kopie/{odlozona.name}")
            else:
                dziennik.krok("      schemat zgodny - baza zostaje bez zmian")
            dziennik.krok("[3/4] Przelaczenie wersji biezacej...")
            przelacz(katalog, poprzednia)
        if suma_ustawien is not None and sha256_pliku(plik_ustawien) != suma_ustawien:
            raise BladInstalacji(KOD_INSTALACJA, f"{plik_ustawien.name} zmienil sie w trakcie powrotu", "Zglos ten komunikat.")
        dziennik.krok(f"[4/4] Samokontrola wersji {poprzednia} (informacyjnie)...")
        try:
            kod, wyjscie = uruchom_samokontrole(python_wersji, program, plik_ustawien, True)
            print("\n".join("      " + w for w in wyjscie.splitlines()), flush=True)
            for wiersz in streszczenie_samokontroli(wyjscie):
                dziennik.wpis(wiersz)
            if kod != 0:
                dziennik.krok(f"      OSTRZEZENIE: samokontrola wersji {poprzednia} zakonczyla sie kodem {kod} - popraw wskazane sprawy")
        except BladInstalacji as e:
            dziennik.krok(f"      OSTRZEZENIE: {e.opis}")
        dziennik.krok(f"POWROT: GOTOWY - wersja biezaca {poprzednia} (poprzednia: {biezaca}). Ponowne Wroc_do_poprzedniej.cmd wraca do {biezaca}.")
        return KOD_OK
    except BladInstalacji as e:
        return _zglos(dziennik, "POWROT", e)
    except Exception as e:  # noqa: BLE001
        dziennik.wpis(traceback.format_exc())
        return _zglos(dziennik, "POWROT", BladInstalacji(KOD_INSTALACJA, f"nieoczekiwany blad ({type(e).__name__}: {e})",
                      "Zglos ten komunikat razem z plikiem dziennik_instalacji.txt."))


def wersje(katalog: Path, usun: str | None = None, zegar=dt.datetime.now) -> int:
    """Lista zainstalowanych wersji albo usuniecie wskazanej (nie biezacej i nie poprzedniej)."""
    katalog = katalog.resolve()
    dziennik = Dziennik(katalog, "wersje", zegar)
    try:
        lista = lista_wersji(katalog)
        if usun is not None:
            wpis = next((w for w in lista if w["wersja"] == usun), None)
            if wpis is None:
                raise BladInstalacji(KOD_BRAK_WERSJI, f"nie ma zainstalowanej wersji {usun!r}", "Lista wersji: Wersje.cmd")
            if wpis["biezaca"] or wpis["poprzednia"]:
                raise BladInstalacji(KOD_BRAK_WERSJI, f"wersja {usun} jest {'biezaca' if wpis['biezaca'] else 'poprzednia'} - nie usuwam",
                                     "Usunac mozna tylko wersje, ktora nie jest ani biezaca, ani poprzednia.")
            usun_katalog(katalog_wersji(katalog, usun))
            dziennik.krok(f"WERSJE: usunieto wersje {usun} (ustawienia i dane bez zmian)")
            return KOD_OK
        if not lista:
            print(f"W {katalog} nie ma zainstalowanych wersji.")
        for w in lista:
            znaczniki = [n for n, jest in (("BIEZACA", w["biezaca"]), ("poprzednia", w["poprzednia"]),
                                           ("NIEDOKONCZONA", w["stan"] != "zainstalowana")) if jest]
            print(f"{w['wersja']:<16} zainstalowano {w['zainstalowano']:<19} commit {str(w['commit'])[:12]:<12} "
                  f"schemat bazy {w['schemat_bazy']}  {' '.join(znaczniki)}")
        return KOD_OK
    except BladInstalacji as e:
        return _zglos(dziennik, "WERSJE", e)


# ------------------------------------------------------------------------------------------------------------ main

def _normalizuj_argumenty(argv: list[str]) -> list[str]:
    """Opcje w stylu Windows (``/katalog X``) -> ``--katalog X``; pozostale argumenty bez zmian."""
    return ["--" + a[1:].lower() if a.startswith("/") and a[1:].lower() in _OPCJE_UKOSNIK else a for a in argv]


def main(argv: list[str] | None = None) -> int:
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(prog="instalator", description='Instalacja, aktualizacja i powrot wersji programu "Stanowisko".')
    polecenia = parser.add_subparsers(dest="polecenie", required=True)
    p = polecenia.add_parser("zainstaluj", help="instalacja / aktualizacja z rozpakowanej paczki wydania")
    p.add_argument("--paczka", type=Path, default=Path(__file__).resolve().parent.parent.parent, help="katalog rozpakowanej paczki")
    p.add_argument("--katalog", type=Path, default=Path(KATALOG_DOMYSLNY), help=f"katalog instalacji (domyslnie {KATALOG_DOMYSLNY})")
    p.add_argument("--python", type=Path, default=Path(sys.executable), help="python.exe 3.12, z ktorego powstaje srodowisko wersji")
    p.add_argument("--testy", action="store_true", help="doinstaluj zestaw testowy (pytest) - tylko odbior koncowy")
    p.add_argument("--skrot", action="store_true", help="zaloz skrot Stanowisko na pulpicie")
    p.add_argument("--skrot-katalog", type=Path, default=None, help="katalog skrotu zamiast pulpitu")
    p.add_argument("--bez-sieci", action="store_true", help="samokontrola bez proby polaczenia z ramkami")
    p.add_argument("--min-wolne-mb", type=int, default=None, help="wymagane wolne miejsce w MB (domyslnie liczone z paczki)")
    p.add_argument("--bez-pauzy", action="store_true", help="(dla zainstaluj.cmd) nie czekaj na klawisz na koncu")
    p = polecenia.add_parser("wroc", help="powrot do poprzedniej wersji")
    p.add_argument("--katalog", type=Path, required=True)
    p.add_argument("--przywroc-kopie", action="store_true", help="zgoda na przywrocenie kopii bazy sprzed aktualizacji")
    p.add_argument("--bez-pauzy", action="store_true")
    p = polecenia.add_parser("wersje", help="lista wersji / usuniecie wskazanej")
    p.add_argument("--katalog", type=Path, required=True)
    p.add_argument("--usun", default=None, metavar="WERSJA", help="usun wersje (nie biezaca i nie poprzednia)")
    p.add_argument("--bez-pauzy", action="store_true")
    args = parser.parse_args(_normalizuj_argumenty(list(sys.argv[1:] if argv is None else argv)))
    if args.polecenie == "zainstaluj":
        return zainstaluj(args.paczka, args.katalog, args.python, testy=args.testy, skrot=args.skrot, skrot_katalog=args.skrot_katalog,
                          bez_sieci=args.bez_sieci, min_wolne_mb=args.min_wolne_mb)
    if args.polecenie == "wroc":
        return wroc(args.katalog, przywroc=args.przywroc_kopie)
    return wersje(args.katalog, args.usun)


if __name__ == "__main__":
    raise SystemExit(main())
