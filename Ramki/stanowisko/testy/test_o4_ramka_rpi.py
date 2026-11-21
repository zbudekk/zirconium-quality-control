"""E3-O4 punkt 4: pliki instalacji programu ramki na Raspberry Pi (`ramka/rpi/`) i instrukcja - zgodnosc z kodem.

Niczego z `ramka/rpi/` nie da sie uruchomic na komputerze PC (brak Raspberry Pi, systemd, matrycy). Testy sprawdzaja to,
co sie da: konce linii i ASCII, skladnie skryptow (`bash -n`, gdy jest bash), ze wzor konfiguracji przyjmuje program
ramki na atrapie, ze opcje z pliku uslugi i z polecen instrukcji istnieja w programie, ze fragmenty Pythona wpisane
w skrypty dzialaja (uruchomione osobno, na plikach w `tmp_path` i na atrapie ramki na 127.0.0.1) oraz ze katalog trafia
do paczki wydania bez zmiany bajtow.
"""
from __future__ import annotations

import ast
import http.client
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import fields
from pathlib import Path

import pytest

STANOWISKO = Path(__file__).resolve().parent.parent
if str(STANOWISKO) not in sys.path:
    sys.path.insert(0, str(STANOWISKO))
if str(STANOWISKO / "narzedzia") not in sys.path:
    sys.path.insert(0, str(STANOWISKO / "narzedzia"))

import zbuduj_wydanie  # noqa: E402
from ramka import WERSJA, protokol, test_led  # noqa: E402
from ramka import program as program_ramki  # noqa: E402
from ramka.program import Konfiguracja, ProgramRamki  # noqa: E402
from ramka.sprzet_atrapa import SprzetAtrapa  # noqa: E402

RPI = STANOWISKO / "ramka" / "rpi"
SKRYPTY = ("zainstaluj_ramke.sh", "sprawdz_ramke.sh")
PLIKI = SKRYPTY + ("ramka.service", "ramka.json.wzor")
INSTRUKCJA = STANOWISKO / "instrukcje" / "ramka_raspberry_pi.md"
ZNACZNIK = "[NIE SPRAWDZONE BEZ SPRZETU]"
KATALOG_NA_RAMCE, KONFIGURACJA_NA_RAMCE = "/opt/ramka", "/etc/ramka/ramka.json"
POLA_SPRZETU = ("port", "piny_halla", "jasnosc", "obrot", "lustro", "mapowanie", "spowolnienie_gpio", "klawisz_zamknij_piec")
GIT_BASH = Path(r"C:\Program Files\Git\bin\bash.exe")


def _tekst(nazwa: str) -> str:
    return (RPI / nazwa).read_bytes().decode("ascii")


def _wzor() -> dict:
    return json.loads(_tekst("ramka.json.wzor"))


def _klucz_wzoru() -> str:
    """Klucz zastepczy wpisany w skrypt instalacji (KLUCZ_WZORU="...")."""
    m = re.search(r'^KLUCZ_WZORU="([^"]+)"$', _tekst("zainstaluj_ramke.sh"), re.M)
    assert m, "zainstaluj_ramke.sh: brak wiersza KLUCZ_WZORU=\"...\""
    return m.group(1)


def _python_ze_skryptu(nazwa: str, znacznik: str) -> str:
    """Fragment Pythona wpisany w skrypt jako dokument w miejscu: <<'ZNACZNIK' ... ZNACZNIK."""
    m = re.search(r"<<'" + znacznik + r"'\n(.*?)\n" + znacznik + r"\n", _tekst(nazwa), re.S)
    assert m, f"{nazwa}: brak fragmentu {znacznik}"
    ast.parse(m.group(1), feature_version=(3, 11))  # Raspberry Pi OS Bookworm = Python 3.11
    return m.group(1)


def _uruchom_python(kod: str, *argumenty) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-c", kod, *[str(a) for a in argumenty]], capture_output=True, text=True, timeout=120)


# ----------------------------------------------------------------------------- pliki

def test_katalog_rpi_ma_komplet_plikow_ascii_lf():
    assert sorted(p.name for p in RPI.iterdir() if p.is_file()) == sorted(PLIKI)
    for plik in [RPI / n for n in PLIKI] + [INSTRUKCJA]:
        dane = plik.read_bytes()
        assert dane.isascii(), plik.name
        assert b"\r" not in dane and dane.endswith(b"\n"), plik.name
    for nazwa in SKRYPTY:
        tekst = _tekst(nazwa)
        assert tekst.startswith("#!/bin/bash\n"), nazwa
        assert ZNACZNIK in tekst, nazwa
        assert re.search(r"echo .*NIE SPRAWDZONE BEZ SPRZETU", tekst), f"{nazwa}: znacznik takze na ekranie"


def test_skrypty_skladnia_bash_n():
    bash = str(GIT_BASH) if GIT_BASH.is_file() else (None if os.name == "nt" else shutil.which("bash"))
    if bash is None:
        pytest.skip("nie sprawdzono - brak bash (Git Bash) na tym komputerze")
    for nazwa in SKRYPTY:
        r = subprocess.run([bash, "-n", str(RPI / nazwa)], capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, f"{nazwa}: {r.stderr}"


def test_skrypty_pomoc_zla_opcja_i_odmowa_bez_administratora():
    """Jedyna czesc skryptow, ktora da sie uruchomic poza Raspberry Pi: rozbior opcji i odmowa pracy bez `sudo`."""
    bash = str(GIT_BASH) if GIT_BASH.is_file() else (None if os.name == "nt" else shutil.which("bash"))
    if bash is None:
        pytest.skip("nie sprawdzono - brak bash (Git Bash) na tym komputerze")

    def uruchom(nazwa, *opcje):
        return subprocess.run([bash, str(RPI / nazwa), *opcje], capture_output=True, text=True, timeout=60)

    administrator = subprocess.run([bash, "-c", "id -u"], capture_output=True, text=True, timeout=60).stdout.strip() == "0"
    for nazwa, kod_zlej_opcji in (("zainstaluj_ramke.sh", 1), ("sprawdz_ramke.sh", 2)):
        r = uruchom(nazwa, "--help")
        assert r.returncode == 0 and "Uzycie: sudo bash " + nazwa in r.stdout and INSTRUKCJA.name in r.stdout, (nazwa, r.stderr)
        r = uruchom(nazwa, "--nie-ma-takiej")
        assert r.returncode == kod_zlej_opcji and "nieznana opcja" in r.stderr and r.stdout == "", (nazwa, r.stdout)
        if not administrator:  # zwykly uzytkownik: skrypt niczego nie rusza i mowi, jak go uruchomic
            r = uruchom(nazwa)
            assert r.returncode == kod_zlej_opcji and "sudo bash " + nazwa in r.stderr, (nazwa, r.stdout, r.stderr)
    for opcja in ("--rola", "--klucz"):
        r = uruchom("zainstaluj_ramke.sh", opcja)
        assert r.returncode == 1 and f"po {opcja} podaj" in r.stderr, opcja


ATRAPY_POLECEN = {  # polecenia systemu Raspberry Pi, ktorych na komputerze z testami nie ma albo nie wolno ruszac
    "id": 'echo 0\n',
    "chown": 'exit 0\n',
    "sleep": 'exit 0\n',
    "stat": 'echo "600 root"\n',
    "install": 'cp "${@: -2:1}" "${@: -1}"\n',
    "hostname": 'if [ "${1:-}" = "-I" ]; then echo "192.0.2.10 "; else echo "ramka-w"; fi\n',
    "systemctl": 'echo "$*" >> "$(dirname "$0")/systemctl.log"\ncase "$1" in\n    is-enabled) echo enabled ;;\n    is-active) echo active ;;\nesac\nexit 0\n',
}


def test_skrypty_w_piaskownicy_kopia_konfiguracja_usluga_i_ponowne_uruchomienie(tmp_path):
    """Proba calego przebiegu obu skryptow poza Raspberry Pi (NIE zastepuje proby na sprzecie): kopie skryptow ze
    sciezkami /opt, /etc i /usr/bin/python3 przepisanymi do `tmp_path`, polecenia systemu (id, systemctl, chown,
    install, hostname, stat, sleep) zastapione atrapami, biblioteki sprzetu - pustymi modulami. Sprawdza logike:
    brak bibliotek = kod 3 i usluga nie wlaczona; kopia programu; plik konfiguracji z wzoru; drugi przebieg nie
    zmienia pliku konfiguracji i wlacza usluge; klucz nie trafia na ekran."""
    bash = str(GIT_BASH) if GIT_BASH.is_file() else (None if os.name == "nt" else shutil.which("bash"))
    if bash is None:
        pytest.skip("nie sprawdzono - brak bash (Git Bash) na tym komputerze")

    def w_bashu(polecenie, argument) -> str:
        r = subprocess.run([bash, "-c", polecenie, "_", str(argument)], capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr
        return r.stdout.strip()

    korzen, atrapy, biblioteki, zrodlo = tmp_path / "korzen", tmp_path / "atrapy", tmp_path / "biblioteki", tmp_path / "zrodlo" / "ramka"
    for katalog in (korzen / "etc" / "systemd" / "system", atrapy, biblioteki):
        katalog.mkdir(parents=True)
    for nazwa, tresc in ATRAPY_POLECEN.items():
        (atrapy / nazwa).write_bytes(("#!/bin/bash\n" + tresc).encode("ascii"))
    shutil.copytree(STANOWISKO / "ramka", zrodlo, ignore=shutil.ignore_patterns("__pycache__"))
    korzen_b, atrapy_b = w_bashu('cd "$1" && pwd', korzen), w_bashu('cd "$1" && pwd', atrapy)
    python_b = w_bashu('cygpath -u "$1"', sys.executable) if os.name == "nt" else sys.executable
    for nazwa in SKRYPTY:
        tekst = _tekst(nazwa)
        for stare, nowe in (('KATALOG_PROGRAMU="/opt/ramka"', f'KATALOG_PROGRAMU="{korzen_b}/opt/ramka"'),
                            ('PLIK_KONFIGURACJI="/etc/ramka/ramka.json"', f'PLIK_KONFIGURACJI="{korzen_b}/etc/ramka/ramka.json"'),
                            ('PLIK_USLUGI="/etc/systemd/system/ramka.service"', f'PLIK_USLUGI="{korzen_b}/etc/systemd/system/ramka.service"'),
                            ('PYTHON="/usr/bin/python3"', f'PYTHON="{python_b}"'),
                            ("\nset -u\n", f'\nset -u\nPATH="{atrapy_b}:$PATH"\n')):
            assert tekst.count(stare) == 1, (nazwa, stare)
            tekst = tekst.replace(stare, nowe)
        (zrodlo / "rpi" / nazwa).write_bytes(tekst.encode("ascii"))
    program, konfiguracja = korzen / "opt" / "ramka" / "ramka", korzen / "etc" / "ramka" / "ramka.json"
    usluga, dziennik = korzen / "etc" / "systemd" / "system" / "ramka.service", atrapy / "systemctl.log"

    def uruchom(nazwa, *opcje, z_bibliotekami):
        srodowisko = {k: v for k, v in os.environ.items() if k.upper() != "PYTHONPATH"}
        srodowisko["PYTHONDONTWRITEBYTECODE"] = "1"
        if z_bibliotekami:
            srodowisko["PYTHONPATH"] = str(biblioteki)
        return subprocess.run([bash, str(zrodlo / "rpi" / nazwa), *opcje], capture_output=True, text=True, timeout=300, env=srodowisko)

    # 1. bez bibliotek sprzetu, bez uslugi: program i konfiguracja sa, kod 3, systemd nietkniety
    r = uruchom("zainstaluj_ramke.sh", "--rola", "P", "--bez-uslugi", z_bibliotekami=False)
    assert r.returncode == 3, (r.stdout, r.stderr)
    assert "BRAK: rgbmatrix" in r.stdout and "kod 3" in r.stdout and "POMIN usluga" in r.stdout
    assert (program / "__main__.py").is_file() and sorted(p.name for p in (program / "rpi").iterdir()) == sorted(PLIKI)
    assert not list(program.rglob("__pycache__")) and not usluga.exists() and not dziennik.exists()
    dane = json.loads(konfiguracja.read_text(encoding="ascii"))
    assert dane["rola"] == "P" and len(dane["klucz"]) == 48 and dane["klucz"] != _klucz_wzoru()
    assert program_ramki.wczytaj_konfiguracje(konfiguracja).sprzet == "rpi"
    assert "rola P, sprzet rpi, adres nasluchu 0.0.0.0, port 8765, klucz jest (48 znakow)" in r.stdout
    assert dane["klucz"] not in r.stdout + r.stderr
    # 2. z bibliotekami, pelna instalacja (rola z nazwy komputera): plik konfiguracji BEZ ZMIAN, usluga zapisana i wlaczona
    for modul in ("rgbmatrix", "gpiozero", "evdev"):
        (biblioteki / f"{modul}.py").write_bytes(b"")
    (program / "stary_plik.py").write_bytes(b"# zostal po poprzedniej wersji\n")
    przed = konfiguracja.read_bytes()
    r = uruchom("zainstaluj_ramke.sh", z_bibliotekami=True)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert konfiguracja.read_bytes() == przed and "zostaje BEZ ZMIAN" in r.stdout
    assert not (program / "stary_plik.py").exists()  # kopia programu jest zastepowana, nie nakladana
    assert not (program.parent / "ramka.nowy").exists() and not (program.parent / "ramka.stary").exists()
    assert usluga.read_bytes() == (RPI / "ramka.service").read_bytes()
    assert dziennik.read_text(encoding="ascii").splitlines()[:3] == ["daemon-reload", "enable ramka.service", "restart ramka.service"]
    for wiersz in ("OK    gpiozero", "OK    evdev", "OK    rgbmatrix", "OK    program", "OK    konfiguracja", "OK    autostart", "OK    usluga",
                   "OK    adres IP"):
        assert wiersz in r.stdout, (wiersz, r.stdout)
    assert f"program ramki {WERSJA} w " in r.stdout and dane["klucz"] not in r.stdout + r.stderr
    # 3. sama kontrola: sa wiersze BRAK (na tym komputerze nie ma config.txt Raspberry Pi) = kod 1 i rada po strzalce
    r = uruchom("sprawdz_ramke.sh", z_bibliotekami=True)
    assert r.returncode == 1, (r.stdout, r.stderr)
    assert "BRAK  config.txt" in r.stdout and "-> " in r.stdout and "WYNIK: wierszy BRAK:" in r.stdout
    # 4. bez pliku konfiguracji i bez roli (nazwa komputera inna niz ramka-w / ramka-p): blad, pliku nie ma
    konfiguracja.unlink()
    (atrapy / "hostname").write_bytes(b"#!/bin/bash\necho raspberrypi\n")
    r = uruchom("zainstaluj_ramke.sh", "--bez-uslugi", z_bibliotekami=True)
    assert r.returncode == 1 and "nie wiem, ktora to ramka" in r.stderr and not konfiguracja.exists()
    r = uruchom("zainstaluj_ramke.sh", "--bez-uslugi", "--rola", "w", "--klucz", dane["klucz"], z_bibliotekami=True)
    assert r.returncode == 0, (r.stdout, r.stderr)
    nowe = json.loads(konfiguracja.read_text(encoding="ascii"))
    assert nowe["rola"] == "W" and nowe["klucz"] == dane["klucz"] and dane["klucz"] not in r.stdout + r.stderr


def test_te_same_sciezki_i_klucz_zastepczy_we_wszystkich_plikach():
    klucz = _klucz_wzoru()
    assert _wzor()["klucz"] == klucz
    protokol.sprawdz_klucz(klucz)  # wzor musi dac sie wczytac programem; skrypty odrzucaja ten klucz na ramce
    for nazwa in SKRYPTY:
        tekst = _tekst(nazwa)
        assert f'KATALOG_PROGRAMU="{KATALOG_NA_RAMCE}"' in tekst, nazwa
        assert f'PLIK_KONFIGURACJI="{KONFIGURACJA_NA_RAMCE}"' in tekst, nazwa
        assert f'KLUCZ_WZORU="{klucz}"' in tekst, nazwa
        assert 'PLIK_USLUGI="/etc/systemd/system/ramka.service"' in tekst, nazwa
        for pakiet in ("rgbmatrix", "gpiozero", "evdev"):
            assert pakiet in tekst, (nazwa, pakiet)
    instalacja = _tekst("zainstaluj_ramke.sh")
    for nazwa in ("ramka.service", "ramka.json.wzor", "sprawdz_ramke.sh"):
        assert nazwa in instalacja, nazwa
    # nazwy pakietow systemu takie, jak podaje sam program w komunikacie o braku biblioteki
    sprzet = (STANOWISKO / "ramka" / "sprzet_rpi.py").read_text(encoding="ascii")
    for pakiet in ("python3-gpiozero", "python3-evdev"):
        assert pakiet in sprzet and pakiet in instalacja and pakiet in _tekst("sprawdz_ramke.sh"), pakiet
    # skrypt instalacji nie kompiluje biblioteki matrycy i nie instaluje pakietow
    for zakazane in ("make ", "git clone", "apt install -y", "apt-get install", "pip install"):
        polecenia = [w for w in instalacja.splitlines() if not w.lstrip().startswith(("#", "echo", "info", "blad", "brak", "rada"))]
        assert not any(zakazane in w for w in polecenia), zakazane


# ----------------------------------------------------------------------------- wzor konfiguracji

def test_wzor_konfiguracji_pola_i_wartosci_domyslne_z_kodu():
    wzor = _wzor()
    znane = {f.name for f in fields(Konfiguracja)}
    assert set(wzor) <= znane
    assert {"rola", "host", "klucz", "sprzet"} | set(POLA_SPRZETU) == set(wzor)
    domyslna = Konfiguracja()
    for pole in POLA_SPRZETU:
        wartosc = tuple(wzor[pole]) if isinstance(wzor[pole], list) else wzor[pole]
        assert wartosc == getattr(domyslna, pole), pole
    assert wzor["sprzet"] == "rpi" and wzor["rola"] in ("W", "P")
    # adres nasluchu widoczny z laptopa: nie 127.0.0.1 (domyslny w kodzie, takze na Raspberry Pi)
    assert wzor["host"] not in ("127.0.0.1", "localhost", "")


def test_wzor_konfiguracji_przyjmuje_program_ramki_na_atrapie():
    konf = program_ramki.konfiguracja_z_argumentow(program_ramki.parsuj_argumenty(
        ["--konfiguracja", str(RPI / "ramka.json.wzor"), "--sprzet", "atrapa", "--host", "127.0.0.1", "--port", "0"]))
    assert konf.klucz == _klucz_wzoru() and konf.piny_halla == (19, 25, 8)
    prog = ProgramRamki(konf, sprzet=SprzetAtrapa())
    _, port = prog.uruchom()
    try:
        for naglowki, status in (({"X-Ramka-Klucz": konf.klucz}, 200), ({}, 401)):
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
            c.request("GET", "/stan", headers=naglowki)
            odp = c.getresponse()
            tresc = odp.read()
            c.close()
            assert odp.status == status
        assert json.loads(tresc or b"{}") == {}  # 401 bez tresci
    finally:
        prog.zatrzymaj()


def test_skrypt_instalacji_tworzy_konfiguracje_z_wzoru(tmp_path):
    """Fragment PY_KONFIGURACJA: rola i klucz wpisane, reszta ze wzoru, istniejacego pliku nie nadpisuje."""
    kod = _python_ze_skryptu("zainstaluj_ramke.sh", "PY_KONFIGURACJA")
    wzor, klucz_wzoru = RPI / "ramka.json.wzor", _klucz_wzoru()
    cel = tmp_path / "ramka.json"
    r = _uruchom_python(kod, wzor, cel, "W", klucz_wzoru, "")
    assert r.returncode == 0, r.stderr
    dane = json.loads(cel.read_text(encoding="ascii"))
    assert dane["rola"] == "W" and dane["klucz"] != klucz_wzoru and len(dane["klucz"]) == 48
    assert dane["klucz"] not in r.stdout + r.stderr  # klucza nie ma na ekranie
    assert {k: v for k, v in dane.items() if k not in ("rola", "klucz")} == {k: v for k, v in _wzor().items() if k not in ("rola", "klucz")}
    konf = program_ramki.wczytaj_konfiguracje(cel)
    assert (konf.rola, konf.sprzet, konf.host) == ("W", "rpi", _wzor()["host"])
    # drugi raz: plik istnieje - blad, tresc bez zmian
    przed = cel.read_bytes()
    r2 = _uruchom_python(kod, wzor, cel, "P", klucz_wzoru, "")
    assert r2.returncode != 0 and cel.read_bytes() == przed
    # klucz podany (druga ramka dostaje ten sam klucz co pierwsza) i klucz zly
    cel2 = tmp_path / "ramka_p.json"
    assert _uruchom_python(kod, wzor, cel2, "P", klucz_wzoru, dane["klucz"]).returncode == 0
    assert json.loads(cel2.read_text(encoding="ascii"))["klucz"] == dane["klucz"]
    for zly in ("krotki", klucz_wzoru, "ze spacja w srodku 1234567890"):
        cel3 = tmp_path / "ramka_zla.json"
        r3 = _uruchom_python(kod, wzor, cel3, "P", klucz_wzoru, zly)
        assert r3.returncode != 0 and not cel3.exists(), zly
    # wzor z innym kluczem zastepczym niz w skrypcie = niezgodne pliki, nic nie powstaje
    assert _uruchom_python(kod, wzor, tmp_path / "x.json", "P", "inny-klucz-zastepczy-123", "").returncode != 0
    assert not (tmp_path / "x.json").exists()


def test_skrypt_sprawdzajacy_ocenia_konfiguracje(tmp_path):
    """Fragment PY_SPRAWDZ_KONFIGURACJE: kod 0 = dobra; wiersz 1 opis (bez klucza), wiersz 2 rada, wiersz 3 host i port."""
    kod = _python_ze_skryptu("sprawdz_ramke.sh", "PY_SPRAWDZ_KONFIGURACJE")
    klucz_wzoru = _klucz_wzoru()
    dobra = dict(_wzor(), rola="W", klucz="a1b2c3d4e5f6a7b8c9d0e1f2")
    przypadki = {"dobra": (dobra, 0), "klucz_zastepczy": (dict(dobra, klucz=klucz_wzoru), 1), "bez_klucza": (dict(dobra, klucz=""), 1),
                 "tylko_lokalnie": (dict(dobra, host="127.0.0.1"), 1), "nieznane_pole": (dict(dobra, obroty=90), 1)}
    for nazwa, (dane, oczekiwany) in przypadki.items():
        plik = tmp_path / f"{nazwa}.json"
        plik.write_text(json.dumps(dane), encoding="ascii")
        r = _uruchom_python(kod, plik, STANOWISKO, klucz_wzoru)
        wiersze = r.stdout.splitlines()
        assert r.returncode == oczekiwany, (nazwa, r.stdout, r.stderr)
        assert len(wiersze) == 3 and "Traceback" not in r.stderr, (nazwa, r.stdout, r.stderr)
        assert dobra["klucz"] not in r.stdout, nazwa
        if oczekiwany:
            assert wiersze[1].strip(), f"{nazwa}: brak rady, co zrobic"
    assert wiersze is not None
    r = _uruchom_python(kod, tmp_path / "dobra.json", STANOWISKO, klucz_wzoru)
    assert r.stdout.splitlines()[2] == f"{dobra['host']} {dobra['port']}" and "rola W" in r.stdout.splitlines()[0]
    r = _uruchom_python(kod, tmp_path / "nie_ma.json", STANOWISKO, klucz_wzoru)
    assert r.returncode == 1 and len(r.stdout.splitlines()) == 3 and "Traceback" not in r.stderr


def test_skrypt_sprawdzajacy_pyta_program_o_stan(tmp_path):
    """Fragment PY_STAN: pyta dzialajacy program ramki (atrapa na 127.0.0.1) o /stan z kluczem z pliku konfiguracji."""
    kod = _python_ze_skryptu("sprawdz_ramke.sh", "PY_STAN")
    klucz = "a1b2c3d4e5f6a7b8c9d0e1f2"
    prog = ProgramRamki(Konfiguracja(rola="W", host="127.0.0.1", port=0, klucz=klucz), sprzet=SprzetAtrapa())
    _, port = prog.uruchom()
    try:
        plik = tmp_path / "ramka.json"
        # "0.0.0.0" w pliku = wszystkie adresy: skrypt pyta wtedy 127.0.0.1
        for host in ("0.0.0.0", "127.0.0.1"):
            plik.write_text(json.dumps({"rola": "W", "host": host, "port": port, "klucz": klucz}), encoding="ascii")
            r = _uruchom_python(kod, plik)
            assert r.returncode == 0, (r.stdout, r.stderr)
            assert f"rola W" in r.stdout and WERSJA in r.stdout and klucz not in r.stdout
        zly = tmp_path / "zly_klucz.json"
        zly.write_text(json.dumps({"rola": "W", "host": "127.0.0.1", "port": port, "klucz": "inny-klucz-0123456789"}), encoding="ascii")
        r = _uruchom_python(kod, zly)
        assert r.returncode == 1 and "401" in r.stdout and "Traceback" not in r.stderr
    finally:
        prog.zatrzymaj()
    r = _uruchom_python(kod, plik)  # program zatrzymany: nikt nie slucha na porcie
    assert r.returncode == 1 and r.stdout.strip() and "Traceback" not in r.stderr


# ----------------------------------------------------------------------------- usluga systemd

def _usluga() -> dict:
    pola = {}
    for wiersz in _tekst("ramka.service").splitlines():
        if "=" in wiersz and not wiersz.startswith("#"):
            nazwa, wartosc = wiersz.split("=", 1)
            pola.setdefault(nazwa.strip(), []).append(wartosc.strip())
    return pola


def test_usluga_opcje_programu_istnieja_w_help(capsys):
    usluga = _usluga()
    polecenie = shlex.split(usluga["ExecStart"][0])
    assert polecenie[:3] == ["/usr/bin/python3", "-m", "ramka"]
    argumenty = polecenie[3:]
    with pytest.raises(SystemExit):
        program_ramki.parsuj_argumenty(["--help"])
    pomoc = capsys.readouterr().out
    opcje = [a for a in argumenty if a.startswith("--")]
    assert opcje and all(re.search(r"(?<![\w-])" + re.escape(o) + r"(?![\w-])", pomoc) for o in opcje), opcje
    a = program_ramki.parsuj_argumenty(argumenty)  # nieznana opcja albo zla wartosc = SystemExit
    assert a.konfiguracja == KONFIGURACJA_NA_RAMCE and a.sprzet == "rpi"
    assert a.host is None and a.port is None and a.rola is None  # adres, port i rola tylko z pliku konfiguracji
    # katalog roboczy = katalog nad pakietem ramka (python -m ramka), uzytkownik i ponowny start wg README programu ramki
    assert usluga["WorkingDirectory"] == [KATALOG_NA_RAMCE]
    assert usluga["User"] == ["root"] and usluga["Restart"] == ["always"] and usluga["RestartSec"] == ["2"]
    assert usluga["After"] == ["network-online.target"] and usluga["Wants"] == ["network-online.target"]
    assert usluga["StartLimitIntervalSec"] == ["0"] and usluga["WantedBy"] == ["multi-user.target"]


# ----------------------------------------------------------------------------- instrukcja

def _kroki_instrukcji() -> dict:
    tekst = INSTRUKCJA.read_bytes().decode("ascii")
    czesci = re.split(r"^## (Krok \d+[^\n]*)\n", tekst, flags=re.M)
    return dict(zip(czesci[1::2], czesci[2::2]))


def test_instrukcja_kazdy_krok_ma_znacznik_niesprawdzone():
    kroki = _kroki_instrukcji()
    assert len(kroki) >= 10
    assert [int(re.match(r"Krok (\d+)", k).group(1)) for k in kroki] == list(range(1, len(kroki) + 1))
    bez = [k for k, tresc in kroki.items() if ZNACZNIK not in k + tresc]
    assert bez == []
    # runda 2 (uwaga D5): sekcje koncowe z twierdzeniami nie do sprawdzenia na PC tez maja znacznik w naglowku
    naglowki = re.findall(r"^## ([^\n]*)$", INSTRUKCJA.read_bytes().decode("ascii"), flags=re.M)
    for sekcja in ("Zmiana pliku konfiguracji", "Typowe bledy"):
        pasujace = [n for n in naglowki if n.startswith(sekcja)]
        assert len(pasujace) == 1 and ZNACZNIK in pasujace[0], sekcja


def test_instrukcja_obejmuje_wymagane_tematy_i_nazwy_z_kodu():
    tekst = INSTRUKCJA.read_bytes().decode("ascii")
    domyslna = Konfiguracja()
    for napis in PLIKI + ("ramka-w", "ramka-p", "config.txt", "cmdline.txt", "dtparam=audio=off", "dtparam=spi=off", "isolcpus=3",
                          "python3-gpiozero", "python3-evdev", "rpi-rgb-led-matrix", "scp ", "pendrive", "Wi-Fi", "ssh ",
                          KATALOG_NA_RAMCE, KONFIGURACJA_NA_RAMCE, f":{domyslna.port}/stan", "X-Ramka-Klucz", "systemctl",
                          "journalctl", "--sprzet rpi", "ramka.test_led", "obrot", "lustro", "jasnosc", "Samokontrola.cmd"):
        assert napis in tekst, napis
    # nazwy pol ustawien laptopa, do ktorych instrukcja odsyla, istnieja we wzorze ustawien programu
    ustawienia = (STANOWISKO / "ustawienia.przyklad.toml").read_text(encoding="utf-8")
    sekcja = ustawienia[ustawienia.index("[ramki]"):ustawienia.index("[sesja]")]
    for pole in ("wieczorna_host", "poranna_host", "klucz", "port"):
        assert re.search(rf"^{pole} = ", sekcja, re.M) and f"`{pole}`" in tekst, pole
    # nazwy ukladow w przykladach test_led istnieja w modelach plytek
    for uklad in re.findall(r"--uklad (\w+)", tekst):
        assert (STANOWISKO / "modele_plytek" / uklad / "uklad.json").is_file(), uklad


def test_instrukcja_polecenia_programu_maja_istniejace_opcje():
    """Kazde `python3 -m ramka ...` i `python3 -m ramka.test_led ...` z instrukcji przechodzi przez prawdziwy rozbior opcji."""
    tekst = INSTRUKCJA.read_bytes().decode("ascii")
    polecenia = re.findall(r"^(?:sudo )?python3 -m (ramka(?:\.\w+)?) (.+)$", tekst, re.M)
    moduly = {m for m, _ in polecenia}
    assert {"ramka", "ramka.test_led"} <= moduly and moduly <= {"ramka", "ramka.test_led", "ramka.kalibracja"}
    for modul, reszta in polecenia:
        argumenty = shlex.split(reszta)
        if modul == "ramka":
            a = program_ramki.parsuj_argumenty(argumenty)
            assert a.sprzet == "rpi" and a.konfiguracja == KONFIGURACJA_NA_RAMCE, reszta
        elif modul == "ramka.test_led":
            a = test_led.parser_polecen().parse_args(argumenty)
            assert a.konfiguracja == KONFIGURACJA_NA_RAMCE and a.kalibracja and a.uklad, reszta
    # polecenia skryptow: tylko opcje, ktore skrypt zna
    opcje_instalacji = set(re.findall(r"^\s+(--[a-z-]+)\)", _tekst("zainstaluj_ramke.sh"), re.M))
    assert {"--rola", "--klucz", "--bez-uslugi"} <= opcje_instalacji
    uzyte = re.findall(r"^sudo bash (\w+\.sh)(.*)$", tekst, re.M)
    assert {n for n, _ in uzyte} == set(SKRYPTY)
    for nazwa, reszta in uzyte:
        znane = set(re.findall(r"^\s+(--[a-z-]+)\)", _tekst(nazwa), re.M))
        assert set(re.findall(r"(--[a-z-]+)", reszta)) <= znane, (nazwa, reszta)


# ----------------------------------------------------------------------------- paczka wydania

def test_katalog_rpi_i_instrukcja_trafiaja_do_paczki_bez_zmiany_bajtow(tmp_path):
    """Regula wyboru plikow paczki (`zbuduj_wydanie`) bierze `ramka/rpi/*` i instrukcje; skrypty .sh zostaja z LF."""
    nazwy = [f"ramka/rpi/{n}" for n in PLIKI] + ["instrukcje/ramka_raspberry_pi.md"]
    for nazwa in nazwy:
        assert zbuduj_wydanie._nalezy(nazwa), nazwa
        assert not nazwa.lower().endswith(zbuduj_wydanie.SKRYPTY_CRLF), nazwa  # tych plikow budowa nie zamienia na CRLF
    shutil.copytree(STANOWISKO / "ramka", tmp_path / "ramka", ignore=shutil.ignore_patterns("__pycache__"))
    (tmp_path / "instrukcje").mkdir()
    shutil.copyfile(INSTRUKCJA, tmp_path / "instrukcje" / INSTRUKCJA.name)
    pliki = zbuduj_wydanie.pliki_z_katalogu(tmp_path)
    for nazwa in nazwy:
        assert pliki[nazwa] == (STANOWISKO / nazwa).read_bytes(), nazwa
    assert sum(1 for n in pliki if n.startswith("ramka/rpi/")) == len(PLIKI)


# ----------------------------------------------------------------------------- runda 2 (uwagi D recenzji PR #52)

def test_d2_plik_z_kluczem_ma_prawa_600_w_skrypcie_instalacji():
    """Uwaga D2: plik konfiguracji z kluczem ma byc czytelny tylko dla root. Na PC nie da sie tego sprawdzic przebiegiem
    (Git Bash na NTFS nie zmienia praw: plik po ``chmod 600`` dalej pokazuje 644), wiec test pilnuje tresci skryptu:
    ``chmod 600`` dla pliku zastanego i nowego, ``umask 077`` wokol tworzenia, ``0o600`` przy otwarciu z ``O_EXCL``."""
    skrypt = (RPI / "zainstaluj_ramke.sh").read_bytes().decode("ascii")
    wiersze = [w.strip() for w in skrypt.splitlines()]
    assert wiersze.count('chmod 600 "$PLIK_KONFIGURACJI"') == 2
    assert sum(w.startswith("if ! (umask 077 && ") and '"$PLIK_KONFIGURACJI"' in w for w in wiersze) == 1
    assert sum("os.O_EXCL, 0o600)" in w for w in wiersze) == 1
    assert not re.search(r"chmod\s+(?:[0-7]*[1-7][0-7]|[0-7]*[1-7])\s+\"\$PLIK_KONFIGURACJI\"", skrypt)  # zadnych praw dla grupy / innych
    assert "0o644" not in skrypt and "umask 022" not in skrypt
    # kontrola na ramce: sprawdz_ramke.sh ma wiersz o prawach pliku (na sprzecie to on zlapie zle prawa)
    assert "600" in (RPI / "sprawdz_ramke.sh").read_bytes().decode("ascii")


def test_d3_instrukcja_podaje_poczatek_odpowiedzi_stan_tak_jak_wysyla_go_program():
    """Uwaga D3: krok 9 kaze porownac poczatek odpowiedzi ``/stan`` - ma byc znak w znak taki, jaki wysyla program."""
    konf = program_ramki.konfiguracja_z_argumentow(program_ramki.parsuj_argumenty(
        ["--konfiguracja", str(RPI / "ramka.json.wzor"), "--sprzet", "atrapa", "--host", "127.0.0.1", "--port", "0"]))
    prog = ProgramRamki(konf, sprzet=SprzetAtrapa())
    _, port = prog.uruchom()
    try:
        c = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
        c.request("GET", "/stan", headers={"X-Ramka-Klucz": konf.klucz})
        tresc = c.getresponse().read().decode("utf-8")
        c.close()
    finally:
        prog.zatrzymaj()
    poczatek = '{"protokol":' + str(json.loads(tresc)["protokol"])
    assert tresc.startswith(poczatek)
    tekst = INSTRUKCJA.read_bytes().decode("ascii")
    assert f"`{poczatek}`" in tekst and '{"protokol": ' not in tekst


def test_d4_d6_instrukcja_ostrzega_o_karcie_zastanej_i_o_kluczu_w_historii():
    kroki = _kroki_instrukcji()
    krok1 = next(tresc for k, tresc in kroki.items() if k.startswith("Krok 1."))
    assert "NIE nadpisuj" in krok1 and krok1.index("NIE nadpisuj") < krok1.index("Raspberry Pi Imager")  # przed pierwszym punktem
    assert "NOWEJ karcie" in krok1
    krok7 = next(tresc for k, tresc in kroki.items() if k.startswith("Krok 7."))
    assert krok7.index("--klucz KLUCZ") < krok7.index(".bash_history") < krok7.index("history -c")
