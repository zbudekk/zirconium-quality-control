"""Testy samokontroli programu (E3-A11s): stanowisko/samokontrola.py.

Kazde sprawdzenie w stanie OK i w stanie zlym (BLAD albo OSTRZEZENIE), kody wyjscia 0 / 1 / 2, format wierszy, --json,
--sumy (zgodne, plik zmieniony, brakujacy, nadmiarowy), swiezy katalog z ustawieniami ze wzoru, brak zmian w bazie
i ustawieniach, czas. Testy pisza tylko do tmp_path; siec = wylacznie 127.0.0.x (atrapa ramki w procesie testu).
Dane osobowe: nazwy folderow zlecen w testach sa fikcyjne i sluza temu, zeby pokazac, ze NIE trafiaja do wyjscia.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import socket
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest

STANOWISKO = Path(__file__).resolve().parent.parent
for _p in (STANOWISKO, STANOWISKO / "narzedzia"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import atrapa_ramki  # noqa: E402
from stanowisko import aplikacja as AP  # noqa: E402
from stanowisko import baza as B  # noqa: E402
from stanowisko import excel_com  # noqa: E402
from stanowisko import indicate as IND  # noqa: E402
from stanowisko import samokontrola as S  # noqa: E402
from stanowisko import ustawienia as UST  # noqa: E402

KODY = ("python", "pakiety", "moduly", "ustawienia", "operatorzy", "folder_skanera", "folder_cyrkon", "folder_prywatne",
        "folder_millbox", "dane_folder", "dane_miejsce", "dane_polozenie", "baza", "modele", "pula", "pamiec_puli",
        "ramka_wieczorna", "ramka_poranna", "excel", "egzemplarz", "sumy")
WIERSZ_OK = re.compile(r"OK [a-z0-9_]+: [^;\n]+")
WIERSZ_ZLY = re.compile(r"(OSTRZEZENIE|BLAD) [a-z0-9_]+: [^;\n]+; [^\n]+")
ZIELONA = re.compile(r"SAMOKONTROLA: ZIELONA \(ok (\d+), ostrzezenia (\d+)\)")
CZERWONA = re.compile(r"SAMOKONTROLA: CZERWONA \(ok (\d+), ostrzezenia (\d+), bledy (\d+)\)")
NAZWISKO = "Kowalczykowa"  # fikcyjne: nie moze trafic do wyjscia samokontroli


# ----------------------------------------------------------------------------- pomocnicze

def wolny_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def zmien(tekst: str, klucz: str, wartosc: str) -> str:
    """Podmienia wartosc klucza we wzorze ustawien (``wartosc`` w zapisie TOML); klucz musi byc we wzorze dokladnie raz."""
    nowy, ile = re.subn(rf"(?m)^({re.escape(klucz)}\s*=\s*)(\"[^\"\n]*\"|\[[^\]\n]*\]|[^\s#]+)", lambda m: m.group(1) + wartosc, tekst)
    assert ile == 1, (klucz, ile)
    return nowy


class Katalog:
    """Swiezy katalog stanowiska w tmp_path: ustawienia ze wzoru z folderami pracy i danymi w tmp_path."""

    def __init__(self, tmp_path: Path, foldery: bool = True):
        self.tmp = tmp_path
        self.plik = tmp_path / "ustawienia.toml"
        self.dane = tmp_path / "dane"
        self.foldery = {k: tmp_path / n for k, n in (("folder_eksportu_skanera", "Scandata"), ("folder_cyrkon", "Cyrkon"),
                                                     ("folder_prywatne", "Prywatne"), ("folder_millbox", "MillBox"))}
        if foldery:
            for f in self.foldery.values():
                f.mkdir()
        t = UST.PLIK_PRZYKLADU.read_text(encoding="utf-8")
        for k, f in self.foldery.items():
            t = zmien(t, k, f'"{f.as_posix()}"')
        for k, n in (("baza", "stanowisko.sqlite"), ("log_excel", "log_excel.csv"), ("wyniki", "wyniki"), ("podglady", "podglady"),
                     ("pula_cache", "pula_cache"), ("logi", "logi"), ("kalibracja_ramek", "kalibracja_ramek.json")):
            t = zmien(t, k, f'"{(self.dane / n).as_posix()}"')
        self.port = wolny_port()  # nic na nim nie slucha: ramki nieobecne bez wychodzenia poza 127.0.0.1
        t = zmien(t, "port", str(self.port))
        t = zmien(t, "wieczorna_host", '"127.0.0.1"')
        t = zmien(t, "poranna_host", '"127.0.0.2"')
        self.tekst = t
        self.zapisz()

    def zapisz(self, **zmiany: str) -> "Katalog":
        for k, v in zmiany.items():
            self.tekst = zmien(self.tekst, k, v)
        self.plik.write_text(self.tekst, encoding="utf-8")
        return self

    @property
    def ust(self) -> dict:
        return UST.wczytaj_ustawienia(self.plik)

    @property
    def baza(self) -> Path:
        return self.dane / "stanowisko.sqlite"

    def zaloz_baze(self) -> Path:
        B.otworz(self.baza).zamknij()
        return self.baza

    def wykonaj(self, **kw):
        kw.setdefault("bez_sieci", True)
        kw.setdefault("plik_ustawien", self.plik)
        return S.wykonaj(self.ust, **kw)


@pytest.fixture
def kat(tmp_path) -> Katalog:
    return Katalog(tmp_path)


@pytest.fixture(autouse=True)
def otoczenie(monkeypatch):
    """Stale otoczenie testow: bez zmiennych OneDrive*, Excel nieuruchomiony (atrapa klienta COM), moduly z DLL bez
    prawdziwego importu (osobny test laduje je naprawde)."""
    for k in list(os.environ):
        if k.upper().startswith("ONEDRIVE"):
            monkeypatch.delenv(k)
    monkeypatch.setattr(S, "_foldery_z_rejestru", lambda: [])
    monkeypatch.setattr(excel_com, "_win32com_client", lambda: KlientCom(dziala=False))
    monkeypatch.setattr(S, "_zaladuj", lambda moduly: {n: True for n in moduly})


class KlientCom:
    def __init__(self, dziala: bool):
        self.dziala = dziala

    def GetActiveObject(self, nazwa):  # noqa: N802 - nazwa COM
        assert nazwa == "Excel.Application"
        if not self.dziala:
            raise RuntimeError("Operation unavailable")
        return object()


def odcisk(katalog: Path) -> dict:
    """Wszystkie pliki i foldery pod ``katalog``: sciezka wzgledna -> SHA-256 tresci (folder: None)."""
    return {p.relative_to(katalog).as_posix(): (hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None)
            for p in sorted(katalog.rglob("*"))}


def program_tmp(tmp_path: Path) -> Path:
    """Maly "katalog programu" do testow sum."""
    k = tmp_path / "program"
    for rel, tresc in (("stanowisko/__init__.py", ""), ("stanowisko/a.py", "A = 1\n"), ("stanowisko/ui/b.py", "B = 2\n"),
                       ("modele_plytek/wieczorna/uklad.json", "{}"), ("ustawienia.przyklad.toml", "# wzor\n")):
        p = k / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(tresc.encode("ascii"))
    return k


def zapisz_sumy(k: Path, plik: Path | None = None, pomin: tuple = ()) -> Path:
    plik = plik or k / S.PLIK_SUM
    linie = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(k).as_posix()}"
             for p in sorted(k.rglob("*")) if p.is_file() and p != plik and p.relative_to(k).as_posix() not in pomin]
    plik.write_text("\n".join(linie) + "\n", encoding="ascii", newline="\n")
    return plik


def uruchom_main(capsys, *argumenty) -> tuple[int, str]:
    kod = S.main([str(a) for a in argumenty])
    wyjscie = capsys.readouterr()
    assert "Traceback" not in wyjscie.out + wyjscie.err
    return kod, wyjscie.out


# ----------------------------------------------------------------------------- kryterium 2 i 3: swiezy katalog, bez zmian

def test_swiezy_katalog_ze_wzoru_zero_bledow_ramki_ostrzezenie_kod_0(kat, capsys):
    kod, wyjscie = uruchom_main(capsys, "--ustawienia", kat.plik)  # z proba ramek: port 127.0.0.x, na ktorym nic nie slucha
    wiersze = wyjscie.splitlines()
    assert kod == 0, wyjscie
    assert [w.split()[1].rstrip(":") for w in wiersze[:-1]] == list(KODY)
    assert not [w for w in wiersze if w.startswith("BLAD")]
    for ramka in ("ramka_wieczorna", "ramka_poranna"):
        assert [w for w in wiersze if w.startswith(f"OSTRZEZENIE {ramka}: ")], wyjscie
    m = ZIELONA.fullmatch(wiersze[-1])
    assert m and int(m.group(1)) + int(m.group(2)) == len(KODY) and int(m.group(2)) >= 2
    assert [w for w in wiersze if w.startswith("OSTRZEZENIE baza: ") and "zostanie zalozona przy pierwszym starcie" in w]
    assert [w for w in wiersze if w.startswith("OSTRZEZENIE sumy: ") and "kopia robocza bez pliku sum" in w]


def test_wzor_bez_zmian_hostow_z_bez_sieci_ramki_pominiete_kod_0(kat, capsys):
    kat.zapisz(wieczorna_host='"ramka-w.local"', poranna_host='"ramka-p.local"', port="8765")  # jak we wzorze
    kod, wyjscie = uruchom_main(capsys, "--ustawienia", kat.plik, "--bez-sieci")
    assert kod == 0
    for ramka in ("ramka_wieczorna", "ramka_poranna"):
        assert re.search(rf"(?m)^OSTRZEZENIE {ramka}: .*pominieto", wyjscie), wyjscie


def test_samokontrola_nie_zmienia_bazy_ustawien_ani_folderow(kat, capsys):
    kat.zaloz_baze()
    (kat.dane / "pula_cache" / "projekty").mkdir(parents=True)
    (kat.foldery["folder_cyrkon"] / "a.stl").write_bytes(b"solid a\nendsolid a\n")
    przed, czasy = odcisk(kat.tmp), (kat.baza.stat().st_mtime_ns, kat.plik.stat().st_mtime_ns)
    kod, wyjscie = uruchom_main(capsys, "--ustawienia", kat.plik)
    assert kod == 0 and "OK baza: " in wyjscie and "OK dane_folder: " in wyjscie  # baza czytana, zapis w folderze danych sprawdzony
    assert odcisk(kat.tmp) == przed  # te same pliki, te same sumy, zadnego nowego pliku ani folderu (takze po probie zapisu)
    assert (kat.baza.stat().st_mtime_ns, kat.plik.stat().st_mtime_ns) == czasy


def test_samokontrola_nie_zaklada_bazy_ani_folderow(kat, capsys):
    przed = odcisk(kat.tmp)
    assert uruchom_main(capsys, "--ustawienia", kat.plik)[0] == 0
    assert odcisk(kat.tmp) == przed and not kat.dane.exists()


# ----------------------------------------------------------------------------- umowa: format, kody wyjscia, --json

def test_format_wierszy_i_podsumowania(kat, capsys):
    kat.zapisz(folder_cyrkon=f'"{(kat.tmp / "nie_ma").as_posix()}"')
    kod, wyjscie = uruchom_main(capsys, "--ustawienia", kat.plik, "--bez-sieci")
    wiersze = wyjscie.splitlines()
    assert kod == 1 and len(wiersze) == len(KODY) + 1
    for w in wiersze[:-1]:
        assert WIERSZ_OK.fullmatch(w) or WIERSZ_ZLY.fullmatch(w), w
        assert w.isascii()
    m = CZERWONA.fullmatch(wiersze[-1])
    poziomy = [w.split()[0] for w in wiersze[:-1]]
    assert m and tuple(int(x) for x in m.groups()) == (poziomy.count("OK"), poziomy.count("OSTRZEZENIE"), poziomy.count("BLAD"))
    assert poziomy.count("BLAD") >= 1 and [w for w in wiersze if w.startswith("BLAD folder_cyrkon: ")]


def test_wynik_jako_funkcja_pola_sprawdzen(kat):
    wynik = kat.wykonaj()
    assert [s.kod for s in wynik.sprawdzenia] == list(KODY) == [s.kod for s in wynik]
    for s in wynik.sprawdzenia:
        assert s.poziom in (S.OK, S.OSTRZEZENIE, S.BLAD) and s.opis and isinstance(s.rada, str)
        assert (s.poziom == S.OK) == (s.rada == ""), s  # rada jest zawsze i tylko przy ostrzezeniu albo bledzie
    assert wynik.bledy == 0 and wynik.zielona and wynik.kod_wyjscia == 0
    assert wynik.ok + wynik.ostrzezenia == len(KODY)
    assert wynik.sprawdzenie("baza").poziom == S.OSTRZEZENIE
    assert wynik.tekst().splitlines()[-1] == wynik.podsumowanie() == f"SAMOKONTROLA: ZIELONA (ok {wynik.ok}, ostrzezenia {wynik.ostrzezenia})"


def test_json_jeden_obiekt_to_samo_co_tekst(kat, capsys):
    kod_t, tekst = uruchom_main(capsys, "--ustawienia", kat.plik, "--bez-sieci")
    kod_j, surowe = uruchom_main(capsys, "--ustawienia", kat.plik, "--bez-sieci", "--json")
    d = json.loads(surowe)
    assert isinstance(d, dict) and kod_j == kod_t == d["kod_wyjscia"] == 0
    assert [f"{s['poziom']} {s['kod']}: {s['opis']}" + (f"; {s['rada']}" if s["rada"] else "") for s in d["sprawdzenia"]] == tekst.splitlines()[:-1]
    assert d["podsumowanie"] == tekst.splitlines()[-1] and d["samokontrola"] == "ZIELONA"
    assert (d["ok"], d["ostrzezenia"], d["bledy"]) == (sum(s["poziom"] == "OK" for s in d["sprawdzenia"]),
                                                      sum(s["poziom"] == "OSTRZEZENIE" for s in d["sprawdzenia"]), 0)
    assert set(d["sprawdzenia"][0]) == {"kod", "poziom", "opis", "rada"}


@pytest.mark.parametrize("json_", [False, True])
def test_kod_2_brak_pliku_ustawien(tmp_path, capsys, json_):
    kod, wyjscie = uruchom_main(capsys, "--ustawienia", tmp_path / "nie_ma.toml", *(["--json"] if json_ else []))
    assert kod == 2
    if json_:
        d = json.loads(wyjscie)
        assert d["kod_wyjscia"] == 2 and d["samokontrola"] == "NIEWYKONANA" and "brak pliku" in d["sprawdzenia"][0]["opis"]
    else:
        assert WIERSZ_ZLY.fullmatch(wyjscie.splitlines()[0]) and wyjscie.startswith("BLAD ustawienia: ")
        assert wyjscie.splitlines()[-1].startswith("SAMOKONTROLA: NIEWYKONANA")


@pytest.mark.parametrize("stare, nowe, fragment", [
    ('pewnosc_min = 0.1', 'pewnosc_min = "duza"', "pewnosc_min"),  # zly typ
    ('[match]', '[match', "TOML"),  # blad skladni
    ('port = ', 'portt = ', "port"),  # literowka w kluczu
])
def test_kod_2_bledny_plik_ustawien_komunikat_bez_sladu_wyjatku(kat, capsys, stare, nowe, fragment):
    assert stare in kat.tekst
    kat.plik.write_text(kat.tekst.replace(stare, nowe, 1), encoding="utf-8")
    kod, wyjscie = uruchom_main(capsys, "--ustawienia", kat.plik)
    assert kod == 2 and fragment in wyjscie and wyjscie.startswith("BLAD ustawienia: ")
    assert "SAMOKONTROLA: NIEWYKONANA" in wyjscie.splitlines()[-1]


def test_kod_2_nieznana_opcja(capsys):
    with pytest.raises(SystemExit) as e:
        S.main(["--nie-ma-takiej-opcji"])
    assert e.value.code == 2


def test_polecenie_modulu_w_osobnym_procesie(kat):
    """Umowa: ``python -m stanowisko.samokontrola`` - prawdziwy proces, prawdziwe moduly z DLL, kod wyjscia, czas (kryterium 4)."""
    polecenie = [sys.executable, "-m", "stanowisko.samokontrola", "--ustawienia", str(kat.plik), "--bez-sieci"]
    p = subprocess.run(polecenie + ["--json"], cwd=str(STANOWISKO), capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert p.returncode == 0 and "Traceback" not in p.stdout + p.stderr, p.stdout + p.stderr
    d = json.loads(p.stdout)
    poziomy = {s["kod"]: s["poziom"] for s in d["sprawdzenia"]}
    assert list(poziomy) == list(KODY) and d["samokontrola"] == "ZIELONA" and ZIELONA.fullmatch(d["podsumowanie"])
    assert poziomy["moduly"] in ("OK", "OSTRZEZENIE") and poziomy["pakiety"] in ("OK", "OSTRZEZENIE"), d  # OSTRZEZENIE: komputer bez pywin32
    assert d["czas_s"] < 20.0, d["czas_s"]  # pelna samokontrola z --bez-sieci, prawdziwy import PySide6 i Open3D
    p = subprocess.run([sys.executable, "-m", "stanowisko.samokontrola", "--ustawienia", str(kat.tmp / "nie_ma.toml")],
                       cwd=str(STANOWISKO), capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert p.returncode == 2 and p.stdout.startswith("BLAD ustawienia: ") and "Traceback" not in p.stdout + p.stderr


# ----------------------------------------------------------------------------- 1. Python i pakiety

def test_python_ok_i_zla_wersja(kat, monkeypatch):
    assert kat.wykonaj().sprawdzenie("python").poziom == S.OK
    monkeypatch.setattr(S, "_wersja_pythona", lambda: (3, 14, 0))
    s = kat.wykonaj().sprawdzenie("python")
    assert s.poziom == S.BLAD and "3.14" in s.opis and "3.12" in s.rada


def piny() -> dict:
    """Pakiety i wersje z requirements.txt programu (dla Windows): nazwa -> wersja."""
    wymagania = dict(S.czytaj_wymagania(STANOWISKO / "requirements.txt"))
    assert {"numpy", "open3d", "PySide6", "pytest", "pywin32"} <= set(wymagania) and len(wymagania) >= 12
    return wymagania


def test_pakiety_zgodne_z_requirements(kat, monkeypatch):
    wymagania = piny()
    monkeypatch.setattr(S, "_wersja_pakietu", lambda n: wymagania.get(n))
    s = kat.wykonaj().sprawdzenie("pakiety")
    assert s.poziom == S.OK and f"zgodne {len(wymagania) - 1} z {len(wymagania) - 1}" in s.opis  # bez pytest


def test_pakiety_prawdziwe_srodowisko_bez_bledu(kat):
    s = kat.wykonaj().sprawdzenie("pakiety")
    assert s.poziom in (S.OK, S.OSTRZEZENIE) and re.search(r"zgodne \d+ z \d+", s.opis), s


def test_pakiety_rozbieznosc_wersji_ostrzezenie_z_lista(kat, monkeypatch):
    wymagania = piny()
    monkeypatch.setattr(S, "_wersja_pakietu", lambda n: "0.0.1" if n == "trimesh" else wymagania.get(n))
    s = kat.wykonaj().sprawdzenie("pakiety")
    assert s.poziom == S.OSTRZEZENIE and f"trimesh 0.0.1 (wymagana {wymagania['trimesh']})" in s.opis
    assert f"zgodne {len(wymagania) - 2} z {len(wymagania) - 1}" in s.opis


def test_pakiety_brak_potrzebnego_blad_brak_pytest_bez_znaczenia_brak_dodatkowego_ostrzezenie(kat, monkeypatch):
    wymagania = piny()
    monkeypatch.setattr(S, "_wersja_pakietu", lambda n: None if n == "pytest" else wymagania.get(n))
    assert kat.wykonaj().sprawdzenie("pakiety").poziom == S.OK  # pytest nie jest wymagany na stanowisku
    for dodatkowy in S.PAKIETY_DODATKOWE:
        monkeypatch.setattr(S, "_wersja_pakietu", lambda n: None if n == dodatkowy else wymagania.get(n))
        s = kat.wykonaj().sprawdzenie("pakiety")
        assert s.poziom == S.OSTRZEZENIE and f"brak {dodatkowy}" in s.opis, dodatkowy
    assert set(S.PAKIETY_DODATKOWE) == {"pywin32", "rtree", "beautifulsoup4", "pypdf"}
    for potrzebny in set(wymagania) - set(S.PAKIETY_DODATKOWE) - {"pytest"}:
        monkeypatch.setattr(S, "_wersja_pakietu", lambda n: None if n in (potrzebny, "pywin32") else wymagania.get(n))
        wynik = kat.wykonaj()
        s = wynik.sprawdzenie("pakiety")
        assert s.poziom == S.BLAD and f"brak {potrzebny}" in s.opis and wynik.kod_wyjscia == 1, potrzebny


def test_pakiety_bez_requirements_ostrzezenie_a_brak_potrzebnego_nadal_blad(kat, tmp_path, monkeypatch):
    pusty = tmp_path / "program_bez_listy"
    pusty.mkdir()
    monkeypatch.setattr(S, "_wersja_pakietu", lambda n: "1.0")
    s = kat.wykonaj(korzen=pusty).sprawdzenie("pakiety")
    assert s.poziom == S.OSTRZEZENIE and "requirements.txt" in s.opis
    monkeypatch.setattr(S, "_wersja_pakietu", lambda n: None if n == "numpy" else "1.0")
    s = kat.wykonaj(korzen=pusty).sprawdzenie("pakiety")
    assert s.poziom == S.BLAD and "brak numpy" in s.opis
    assert set(S.PAKIETY_W_PRACY) == set(piny()) - set(S.PAKIETY_DODATKOWE) - {"pytest"}  # lista awaryjna = requirements.txt


# ----------------------------------------------------------------------------- 2. moduly z DLL

def test_moduly_prawdziwe_ladowanie_te_same_co_program(kat, monkeypatch):
    monkeypatch.undo()  # prawdziwy import (PySide6, Open3D, ...), jak w aplikacja.main
    wolane = []
    prawdziwe = AP.zaladuj_moduly_dll
    monkeypatch.setattr(AP, "zaladuj_moduly_dll", lambda moduly=AP.MODULY_DLL: wolane.append(tuple(moduly)) or prawdziwe(moduly))
    monkeypatch.setattr(excel_com, "_win32com_client", lambda: KlientCom(dziala=False))
    s = kat.wykonaj().sprawdzenie("moduly")
    ladowane = {n for grupa in wolane for n in grupa}
    assert set(AP.MODULY_DLL) | set(AP.MODULY_DLL_PULI) | {"PySide6.QtWidgets", "stanowisko.porownaj"} <= ladowane
    nieobowiazkowe = set(S.MODULY_NIEOBOWIAZKOWE)
    assert nieobowiazkowe == {"pythoncom", "win32com.client"}
    assert s.poziom in (S.OK, S.OSTRZEZENIE), s  # OSTRZEZENIE tylko, gdy na tym komputerze nie ma pywin32
    assert f"z {len(ladowane)}" in s.opis


def test_moduly_blad_importu_to_wynik_blad_a_nie_awaria(kat, monkeypatch):
    monkeypatch.setattr(S, "_zaladuj", lambda moduly: {n: ("ImportError: DLL load failed while importing pybind" if n == "open3d" else True) for n in moduly})
    s = kat.wykonaj().sprawdzenie("moduly")
    assert s.poziom == S.BLAD and "open3d" in s.opis and "DLL load failed" in s.opis

    def awaria(moduly):
        raise OSError("[WinError 126] nie znaleziono modulu")

    monkeypatch.setattr(S, "_zaladuj", awaria)
    wynik = kat.wykonaj()
    assert wynik.sprawdzenie("moduly").poziom == S.BLAD and len(wynik.sprawdzenia) == len(KODY)  # reszta sprawdzen wykonana


def test_moduly_brak_pywin32_tylko_ostrzezenie(kat, monkeypatch):
    monkeypatch.setattr(S, "_zaladuj", lambda moduly: {n: ("ModuleNotFoundError: No module named 'pythoncom'" if n in S.MODULY_NIEOBOWIAZKOWE else True)
                                                       for n in moduly})
    s = kat.wykonaj().sprawdzenie("moduly")
    assert s.poziom == S.OSTRZEZENIE and "pythoncom" in s.opis and "Excel" in s.rada


# ----------------------------------------------------------------------------- 3. ustawienia

def test_ustawienia_lista_kluczy_uzupelnionych_domyslnie(kat):
    s = kat.wykonaj().sprawdzenie("ustawienia")
    assert s.poziom == S.OK and "0 kluczy" in s.opis  # wzor ma wszystkie klucze
    t = kat.tekst
    for wiersz in ("pula_wpisow = false", "pamiec_puli_dni = 30", 'tryb = "pytaj"'):
        poczatek = t.index(wiersz)
        t = t[:poczatek] + t[t.index("\n", poczatek) + 1:]
    kat.plik.write_text(t, encoding="utf-8")
    s = kat.wykonaj().sprawdzenie("ustawienia")
    assert s.poziom == S.OK and "3 klucze" in s.opis  # informacja, nie blad
    for klucz in ("[silnik] pula_wpisow", "[silnik] pamiec_puli_dni", "[excel] tryb"):
        assert klucz in s.opis


def test_ustawienia_bez_pliku_wywolanie_z_programu(kat):
    s = S.wykonaj(kat.ust, bez_sieci=True).sprawdzenie("ustawienia")
    assert s.poziom == S.OK


def test_operatorzy_pusta_lista_ostrzezenie_wpisana_ok(kat):
    s = kat.wykonaj().sprawdzenie("operatorzy")
    assert s.poziom == S.OSTRZEZENIE and "[sesja] operatorzy" in s.rada
    s = kat.zapisz(operatorzy='["Technik A", "Technik B"]').wykonaj().sprawdzenie("operatorzy")
    assert s.poziom == S.OK and "2" in s.opis and "Technik" not in s.opis


# ----------------------------------------------------------------------------- 4. foldery pracy

@pytest.mark.parametrize("klucz, kod, poziom_braku", [
    ("folder_eksportu_skanera", "folder_skanera", "BLAD"), ("folder_cyrkon", "folder_cyrkon", "BLAD"),
    ("folder_prywatne", "folder_prywatne", "OSTRZEZENIE"), ("folder_millbox", "folder_millbox", "OSTRZEZENIE")])
def test_foldery_pracy_ok_i_brak(kat, klucz, kod, poziom_braku):
    s = kat.wykonaj().sprawdzenie(kod)
    assert s.poziom == S.OK and kat.foldery[klucz].as_posix() in s.opis.replace("\\", "/")
    kat.foldery[klucz].rmdir()
    wynik = kat.wykonaj()
    s = wynik.sprawdzenie(kod)
    assert s.poziom == poziom_braku and f"[sciezki] {klucz}" in s.rada
    assert wynik.kod_wyjscia == (1 if poziom_braku == "BLAD" else 0)
    kat.foldery[klucz].write_bytes(b"to plik, nie folder")
    assert kat.wykonaj().sprawdzenie(kod).poziom == poziom_braku


def test_foldery_puli_per_praca_brak_millbox_zatrzymuje_wieczor_blad_brak_prywatne_ostrzezenie(kat):
    kat.zapisz(pula_wpisow="true")
    kat.foldery["folder_millbox"].rmdir()
    kat.foldery["folder_prywatne"].rmdir()
    wynik = kat.wykonaj()
    s = wynik.sprawdzenie("folder_millbox")
    assert s.poziom == S.BLAD and S.PLIK_WSPOLCZYNNIKOW in s.opis and "[sciezki] folder_millbox" in s.rada and wynik.kod_wyjscia == 1
    assert wynik.sprawdzenie("folder_prywatne").poziom == S.OSTRZEZENIE
    kat.zapisz(pula_wpisow="false")
    wynik = kat.wykonaj()
    s = wynik.sprawdzenie("folder_millbox")
    assert s.poziom == S.OSTRZEZENIE and "pula_wpisow = false" in s.opis and wynik.kod_wyjscia == 0


def test_folder_nieczytelny_i_folder_bez_odpowiedzi(kat, monkeypatch):
    prawdziwy = S._czytaj_folder

    def odmowa(folder):
        if Path(folder) == kat.foldery["folder_cyrkon"]:
            raise PermissionError(13, "Odmowa dostepu", str(Path(folder) / f"{NAZWISKO} 3263"))
        return prawdziwy(folder)

    monkeypatch.setattr(S, "_czytaj_folder", odmowa)
    s = kat.wykonaj().sprawdzenie("folder_cyrkon")
    assert s.poziom == S.BLAD and "PermissionError" in s.opis and NAZWISKO not in s.opis + s.rada

    def wisi(folder):
        if Path(folder) == kat.foldery["folder_millbox"]:
            time.sleep(30)
        return prawdziwy(folder)

    monkeypatch.setattr(S, "_czytaj_folder", wisi)
    monkeypatch.setattr(S, "LIMIT_FOLDERU_S", 0.3)
    t = time.perf_counter()
    wynik = kat.wykonaj()
    assert time.perf_counter() - t < 5.0
    assert wynik.sprawdzenie("folder_millbox").poziom == S.OSTRZEZENIE and "nie odpowiada" in wynik.sprawdzenie("folder_millbox").opis
    assert wynik.sprawdzenie("folder_skanera").poziom == S.OK


# ----------------------------------------------------------------------------- 5. folder danych

def test_dane_folder_istnieje_zapis_ok_plik_probny_usuniety(kat):
    kat.dane.mkdir()
    s = kat.wykonaj().sprawdzenie("dane_folder")
    assert s.poziom == S.OK and "zapis mozliwy" in s.opis and list(kat.dane.iterdir()) == []


def test_dane_folder_brak_da_sie_utworzyc_ostrzezenie_nie_da_sie_blad(kat):
    s = kat.wykonaj().sprawdzenie("dane_folder")
    assert s.poziom == S.OSTRZEZENIE and "zostanie zalozony" in s.opis and not kat.dane.exists()
    kat.dane.write_bytes(b"plik w miejscu folderu danych")
    s = kat.wykonaj().sprawdzenie("dane_folder")
    assert s.poziom == S.BLAD and "[sciezki] baza" in s.rada


def test_dane_folder_bez_prawa_zapisu_blad(kat, monkeypatch):
    kat.dane.mkdir()

    def odmowa(folder):
        raise PermissionError(13, "Odmowa dostepu")

    monkeypatch.setattr(S, "_proba_zapisu", odmowa)
    s = kat.wykonaj().sprawdzenie("dane_folder")
    assert s.poziom == S.BLAD and "zapis" in s.opis and "PermissionError" in s.opis


@pytest.mark.parametrize("wolne_gb, poziom", [(250.0, "OK"), (S.MIEJSCE_OSTRZEZENIE_GB - 0.5, "OSTRZEZENIE"), (S.MIEJSCE_BLAD_GB - 0.2, "BLAD")])
def test_dane_miejsce_progi(kat, monkeypatch, wolne_gb, poziom):
    monkeypatch.setattr(S, "_wolne_miejsce", lambda folder: int(wolne_gb * 2**30))
    s = kat.wykonaj().sprawdzenie("dane_miejsce")
    assert s.poziom == poziom and f"{wolne_gb:.1f} GB" in s.opis
    assert 0 < S.MIEJSCE_BLAD_GB < S.MIEJSCE_OSTRZEZENIE_GB


def test_dane_miejsce_prawdziwy_dysk(kat):
    assert re.search(r"\d+\.\d GB", kat.wykonaj().sprawdzenie("dane_miejsce").opis)


def test_dane_polozenie_ok_poza_synchronizacja(kat):
    assert kat.wykonaj().sprawdzenie("dane_polozenie").poziom == S.OK


def test_dane_polozenie_w_onedrive_ze_zmiennej_blad(kat, monkeypatch):
    monkeypatch.setenv("OneDriveCommercial", str(kat.tmp))
    s = kat.wykonaj().sprawdzenie("dane_polozenie")
    assert s.poziom == S.BLAD and "OneDrive" in s.opis and "[sciezki] baza" in s.opis
    monkeypatch.setenv("OneDriveCommercial", str(kat.tmp / "inny_katalog"))
    assert kat.wykonaj().sprawdzenie("dane_polozenie").poziom == S.OK


@pytest.mark.parametrize("nazwa", ["OneDrive - Pracownia", "Pracownia - SharePoint"])
def test_dane_polozenie_nazwa_katalogu_synchronizowanego_blad(kat, nazwa):
    kat.zapisz(baza=f'"{(kat.tmp / nazwa / "dane" / "stanowisko.sqlite").as_posix()}"')
    s = kat.wykonaj().sprawdzenie("dane_polozenie")
    assert s.poziom == S.BLAD and "[sciezki] baza" in s.opis


def test_dane_polozenie_biblioteka_sharepoint_z_rejestru_blad(kat, monkeypatch):
    monkeypatch.setattr(S, "_foldery_z_rejestru", lambda: [str(kat.tmp / "inna"), str(kat.dane)])
    s = kat.wykonaj().sprawdzenie("dane_polozenie")
    assert s.poziom == S.BLAD and "[sciezki] baza" in s.opis


def test_dane_polozenie_inna_sciezka_danych_w_onedrive(kat, monkeypatch):
    monkeypatch.setenv("OneDrive", str(kat.tmp / "OD"))
    kat.zapisz(log_excel=f'"{(kat.tmp / "OD" / "dane" / "log_excel.csv").as_posix()}"')
    s = kat.wykonaj().sprawdzenie("dane_polozenie")
    assert s.poziom == S.BLAD and "[sciezki] log_excel" in s.opis and "[sciezki] baza" not in s.opis


def test_dane_polozenie_w_katalogu_wydania_ostrzezenie(kat, tmp_path):
    k = program_tmp(tmp_path)
    zapisz_sumy(k)  # katalog programu z plikiem sum = wersja zainstalowana z paczki
    kat.zapisz(baza=f'"{(k / "dane" / "stanowisko.sqlite").as_posix()}"')
    s = kat.wykonaj(korzen=k).sprawdzenie("dane_polozenie")
    assert s.poziom == S.OSTRZEZENIE and "katalogu programu" in s.opis


# ----------------------------------------------------------------------------- 6. baza

def test_baza_brak_pliku_ostrzezenie(kat):
    s = kat.wykonaj().sprawdzenie("baza")
    assert s.poziom == S.OSTRZEZENIE and "zostanie zalozona przy pierwszym starcie" in s.opis and not kat.baza.exists()


def test_baza_biezaca_ok(kat):
    kat.zaloz_baze()
    s = kat.wykonaj().sprawdzenie("baza")
    assert s.poziom == S.OK and f"wersja schematu {max(B.MIGRACJE)}" in s.opis and "quick_check ok" in s.opis


def test_baza_starsza_ostrzezenie_nowsza_blad(kat):
    kat.zaloz_baze()
    stara, nowa = max(B.MIGRACJE) - 1, max(B.MIGRACJE) + 1
    pol = sqlite3.connect(kat.baza)
    pol.execute(f"PRAGMA user_version = {stara}")
    pol.close()
    s = kat.wykonaj().sprawdzenie("baza")
    assert s.poziom == S.OSTRZEZENIE and "migracja z kopia przy starcie" in s.opis and f"wersja schematu {stara}" in s.opis
    pol = sqlite3.connect(kat.baza)
    pol.execute(f"PRAGMA user_version = {nowa}")
    pol.close()
    wynik = kat.wykonaj()
    s = wynik.sprawdzenie("baza")
    assert s.poziom == S.BLAD and f"wersja schematu {nowa}" in s.opis and wynik.kod_wyjscia == 1


def test_baza_plik_nie_jest_baza_blad(kat):
    kat.dane.mkdir()
    kat.baza.write_bytes(b"to nie jest baza SQLite " * 500)
    s = kat.wykonaj().sprawdzenie("baza")
    assert s.poziom == S.BLAD and "nie jest baza SQLite albo jest uszkodzony" in s.opis


def test_baza_uszkodzona_quick_check_blad(kat):
    kat.zaloz_baze()
    pol = sqlite3.connect(kat.baza)
    with pol:
        pol.executemany("INSERT INTO zdarzenia (czas, zrodlo, typ, dane) VALUES (?, 'system', 'test', ?)",
                        [("2026-11-20T10:00:00", "x" * 200) for _ in range(3000)])
    rozmiar_strony = pol.execute("PRAGMA page_size").fetchone()[0]
    pol.close()
    surowe = bytearray(kat.baza.read_bytes())
    assert len(surowe) > 40 * rozmiar_strony
    for strona in range(20, 30):  # zamazane strony danych w srodku pliku (naglowek i schemat zostaja)
        surowe[strona * rozmiar_strony:(strona + 1) * rozmiar_strony] = b"\xa5" * rozmiar_strony
    kat.baza.write_bytes(bytes(surowe))
    przed = hashlib.sha256(kat.baza.read_bytes()).hexdigest()
    s = kat.wykonaj().sprawdzenie("baza")
    assert s.poziom == S.BLAD and "quick_check" in s.opis and "kopi" in s.rada
    assert hashlib.sha256(kat.baza.read_bytes()).hexdigest() == przed  # samokontrola niczego nie naprawia


def test_baza_przerwany_zapis_goracy_dziennik_ostrzezenie_bez_zmiany_plikow(kat, tmp_path):
    """Kopia bazy zrobiona w trakcie duzej transakcji = stan po wylaczeniu pradu w czasie zapisu: baza + plik -journal.
    Program cofa taki zapis przy starcie; samokontrola (tylko odczyt) nie moze ani tego zglosic jako uszkodzenia, ani ruszyc plikow."""
    zrodlo = tmp_path / "zrodlo" / "stanowisko.sqlite"
    B.otworz(zrodlo).zamknij()
    pol = sqlite3.connect(zrodlo, isolation_level=None)
    pol.execute("PRAGMA cache_size = 5")
    pol.execute("BEGIN IMMEDIATE")
    pol.executemany("INSERT INTO zdarzenia (czas, zrodlo, typ, dane) VALUES ('2026-11-20T10:00:00', 'system', 'test', ?)",
                    [("x" * 500,) for _ in range(4000)])
    kat.dane.mkdir()
    for p in list(zrodlo.parent.iterdir()):
        (kat.dane / p.name).write_bytes(p.read_bytes())
    pol.execute("ROLLBACK")
    pol.close()
    assert sorted(p.name for p in kat.dane.iterdir()) == ["stanowisko.sqlite", "stanowisko.sqlite-journal"]
    kat.zapisz(pula_wpisow="true")
    przed = odcisk(kat.dane)
    wynik = kat.wykonaj()
    s = wynik.sprawdzenie("baza")
    assert s.poziom == S.OSTRZEZENIE and "niedokonczony zapis" in s.opis and "-journal" in s.rada, s
    assert wynik.sprawdzenie("pula").poziom == S.OSTRZEZENIE and "nie da sie teraz odczytac" in wynik.sprawdzenie("pula").opis
    assert odcisk(kat.dane) == przed and wynik.kod_wyjscia == 0
    B.otworz(kat.baza).zamknij()  # program przy starcie cofa przerwany zapis - baza jest potem w porzadku
    assert kat.wykonaj().sprawdzenie("baza").poziom == S.OK


def test_baza_quick_check_ograniczony_limitem_krotszym_niz_czekanie_programu(kat, monkeypatch):
    kat.zaloz_baze()
    pol = sqlite3.connect(kat.baza)
    with pol:
        pol.executemany("INSERT INTO zdarzenia (czas, zrodlo, typ, dane) VALUES ('2026-11-20T10:00:00', 'system', 'test', ?)",
                        [("x" * 200,) for _ in range(3000)])
    pol.close()
    assert kat.wykonaj().sprawdzenie("baza").poziom == S.OK
    monkeypatch.setattr(S, "LIMIT_QUICK_CHECK_S", -1.0)  # limit minal, zanim sprawdzanie sie zaczelo
    monkeypatch.setattr(S, "KROK_QUICK_CHECK", 50)
    s = kat.wykonaj().sprawdzenie("baza")
    assert s.poziom == S.OSTRZEZENIE and "quick_check nie zakonczyl sie" in s.opis and "spojnosci nie sprawdzono" in s.opis
    monkeypatch.undo()
    assert S.LIMIT_QUICK_CHECK_S * 1000 < B.CZEKAJ_NA_BLOKADE_MS  # samokontrola obok pracujacego programu nie blokuje jego zapisu za dlugo


def test_baza_pusty_plik_jak_brak(kat):
    kat.dane.mkdir()
    kat.baza.write_bytes(b"")
    s = kat.wykonaj().sprawdzenie("baza")
    assert s.poziom == S.OSTRZEZENIE and "zostanie zalozona przy pierwszym starcie" in s.opis


# ----------------------------------------------------------------------------- 7. modele plytek

def test_modele_ok_wszystkie_uklady_z_ustawien(kat):
    s = kat.wykonaj().sprawdzenie("modele")
    assert s.poziom == S.OK and f"{len(kat.ust['plytki'])} z {len(kat.ust['plytki'])}" in s.opis


@pytest.mark.parametrize("zepsucie, fragment", [("brak_katalogu", "brak katalogu"), ("brak_ukladu", "uklad.json"),
                                                ("zly_json", "uklad.json"), ("brak_stl", "plytka_n")])
def test_modele_zly_uklad_blad(kat, tmp_path, zepsucie, fragment):
    wzor = STANOWISKO / "modele_plytek" / "wieczorna"
    kopia = tmp_path / "modele" / "wieczorna"
    if zepsucie != "brak_katalogu":
        kopia.mkdir(parents=True)
        if zepsucie != "brak_ukladu":
            tresc = (wzor / "uklad.json").read_text(encoding="utf-8")
            (kopia / "uklad.json").write_text(tresc[: len(tresc) // 2] if zepsucie == "zly_json" else tresc, encoding="utf-8")
        if zepsucie != "brak_stl":
            (kopia / "plytka_n1.stl").write_bytes((wzor / "plytka_n1.stl").read_bytes())
    kat.zapisz(wieczorna=f'"{kopia.as_posix()}"')
    wynik = kat.wykonaj()
    s = wynik.sprawdzenie("modele")
    assert s.poziom == S.BLAD and "wieczorna" in s.opis and fragment in s.opis and wynik.kod_wyjscia == 1


# ----------------------------------------------------------------------------- 8. pula projektow i pamiec puli

def test_pula_z_folderu_pusta_ostrzezenie_niepusta_ok_licznik_bez_nazw(kat):
    s = kat.wykonaj().sprawdzenie("pula")
    assert s.poziom == S.OSTRZEZENIE and "0 plikow STL" in s.opis
    zlecenie = kat.foldery["folder_cyrkon"] / f"{NAZWISKO} Anna 3263"
    (zlecenie / "_stare").mkdir(parents=True)
    for p in (zlecenie / f"{NAZWISKO}_16_cad.stl", zlecenie / "drugi.STL", zlecenie / "_stare" / "pomijany.stl", zlecenie / "notatka.txt"):
        p.write_bytes(b"solid x\nendsolid x\n")
    wynik = kat.wykonaj()
    s = wynik.sprawdzenie("pula")
    assert s.poziom == S.OK and "2 pliki STL" in s.opis and "pula_wpisow = false" in s.opis
    assert AP.pliki_stl(kat.foldery["folder_cyrkon"]) == 2  # ta sama regula liczenia co w programie
    assert NAZWISKO not in wynik.tekst()


def test_pula_folder_wybrany_w_programie_bez_sciezki_w_wyjsciu(kat):
    kat.dane.mkdir()
    wybrany = kat.tmp / f"{NAZWISKO} probny"
    wybrany.mkdir()
    (wybrany / "a.stl").write_bytes(b"solid a\nendsolid a\n")
    (kat.dane / AP.PLIK_PULI).write_text(json.dumps({"folder": str(wybrany), "wspolczynnik": 1.22}), encoding="utf-8")
    wynik = kat.wykonaj()
    s = wynik.sprawdzenie("pula")
    assert s.poziom == S.OK and "1 plik STL" in s.opis and "wybrany w programie" in s.opis
    assert NAZWISKO not in wynik.tekst()
    assert S.PLIK_PULI == AP.PLIK_PULI and S.PLIK_WSPOLCZYNNIKOW == AP.PLIK_WSPOLCZYNNIKOW


def test_pula_wpisow_stan_z_indeksu_licznikami(kat):
    kat.zapisz(pula_wpisow="true")
    s = kat.wykonaj().sprawdzenie("pula")
    assert s.poziom == S.OSTRZEZENIE and "pula_wpisow = true" in s.opis and "indeks" in s.opis  # brak bazy: indeks powstanie przy starcie
    baza = B.otworz(kat.baza)
    with baza.transakcja():
        z = baza.wstaw("zlecenia", zrodlo="cyrkon", folder=f"{NAZWISKO} Anna 3263", kuweta="3263")
        for n in range(3):
            baza.wstaw("projekty", zlecenie_id=z, plik=f"{NAZWISKO}_{n}_cad.stl", sha16=f"{n:016x}")
        usuniete = baza.wstaw("zlecenia", zrodlo="cyrkon", folder=f"{NAZWISKO} Jan 3301", kuweta="3301", usuniety=1)
        baza.wstaw("projekty", zlecenie_id=usuniete, plik="stary_cad.stl", sha16="f" * 16, usuniety=1)
        baza.wstaw("frezowania", plik_w_raporcie=f"{NAZWISKO}_0_cad.stl", krazek="K1", wspolczynnik=1.2251, data="2026-11-20", zrodlo="csv")
    baza.zamknij()
    wynik = kat.wykonaj()
    s = wynik.sprawdzenie("pula")
    assert s.poziom == S.OSTRZEZENIE and "zlecen 1" in s.opis and "projektow 3" in s.opis and "frezowan 1" in s.opis
    assert S.PLIK_WSPOLCZYNNIKOW in s.opis  # brak pliku wspolczynnikow w folder_millbox = ostrzezenie
    (kat.foldery["folder_millbox"] / S.PLIK_WSPOLCZYNNIKOW).write_text("plik;krazek;wspolczynnik;data\n", encoding="utf-8")
    wynik = kat.wykonaj()
    s = wynik.sprawdzenie("pula")
    assert s.poziom == S.OK and "zlecen 1" in s.opis and "projektow 3" in s.opis
    assert NAZWISKO not in wynik.tekst()


def test_pamiec_puli_brak_ok_wpisy_policzone_plik_zamiast_folderu_ostrzezenie(kat):
    s = kat.wykonaj().sprawdzenie("pamiec_puli")
    assert s.poziom == S.OK and "0 wpisow" in s.opis
    projekty = kat.dane / "pula_cache" / "projekty"
    projekty.mkdir(parents=True)
    for n in range(3):
        (projekty / f"{n:016x}_1.225000_auto_e_abc.npz").write_bytes(b"x" * 1024)
    (projekty / "0000.123.tmp.npz").write_bytes(b"x")  # pozostalosc przerwanego zapisu - nie jest wpisem
    s = kat.wykonaj().sprawdzenie("pamiec_puli")
    assert s.poziom == S.OK and "3 wpisy" in s.opis
    kat.zapisz(pula_cache=f'"{kat.plik.as_posix()}"')  # sciezka wskazuje plik
    s = kat.wykonaj().sprawdzenie("pamiec_puli")
    assert s.poziom == S.OSTRZEZENIE and "[sciezki] pula_cache" in s.rada


# ----------------------------------------------------------------------------- 9. ramki

@pytest.fixture
def ramki(kat):
    """Atrapy ramek W (127.0.0.1) i P (127.0.0.2) na porcie z ustawien - program ramki z atrapa sprzetu w procesie testu."""
    programy = []

    def uruchom(role=("W", "P"), **konf):
        for rola in role:
            program, _ = atrapa_ramki.uruchom_atrape(rola, port=kat.port, host="127.0.0.1" if rola == "W" else "127.0.0.2", **konf)
            programy.append(program)
        return programy

    yield uruchom
    for p in programy:
        p.zatrzymaj()


def test_ramki_obecne_ok(kat, ramki):
    programy = ramki()
    przed = [p.stan(None) for p in programy]
    wynik = kat.wykonaj(bez_sieci=False)
    for kod, rola in (("ramka_wieczorna", "W"), ("ramka_poranna", "P")):
        s = wynik.sprawdzenie(kod)
        assert s.poziom == S.OK and f"rola {rola}" in s.opis, s
    po = [p.stan(None) for p in programy]
    for a, b in zip(przed, po):  # proba nie zmienia stanu ramki: brak kontaktu laptopa, brak zdarzen, ten sam plan
        assert {k: a[k] for k in ("wlasciciel", "nr_zdarzenia", "plan_id", "tryb")} == {k: b[k] for k in ("wlasciciel", "nr_zdarzenia", "plan_id", "tryb")}
    assert S.NAGLOWEK_KLUCZA == IND.NAGLOWEK_KLUCZA


def test_ramki_nieobecne_ostrzezenie_kod_0(kat):
    t = time.perf_counter()
    wynik = kat.wykonaj(bez_sieci=False)
    assert time.perf_counter() - t < 2 * S.LIMIT_RAMKI_S + 3.0
    for kod in ("ramka_wieczorna", "ramka_poranna"):
        s = wynik.sprawdzenie(kod)
        assert s.poziom == S.OSTRZEZENIE and "nieobecna" in s.opis and "bez ramek" in s.rada
    assert wynik.kod_wyjscia == 0


def test_ramki_bez_sieci_pominiete(kat, ramki):
    ramki()
    wynik = kat.wykonaj(bez_sieci=True)
    for kod in ("ramka_wieczorna", "ramka_poranna"):
        s = wynik.sprawdzenie(kod)
        assert s.poziom == S.OSTRZEZENIE and "pominieto" in s.opis


def test_ramki_zamienione_hosty_ostrzezenie(kat, ramki):
    ramki()
    kat.zapisz(wieczorna_host='"127.0.0.2"', poranna_host='"127.0.0.1"')
    wynik = kat.wykonaj(bez_sieci=False)
    s = wynik.sprawdzenie("ramka_wieczorna")
    assert s.poziom == S.OSTRZEZENIE and "rola P" in s.opis and "wieczorna_host" in s.rada


def test_ramki_zly_klucz_ostrzezenie_bez_klucza_w_wyjsciu(kat, ramki):
    klucz_ramki, klucz_laptopa = "K" * 24, "tajnyKluczLaptopa1234"
    ramki(role=("W",), klucz=klucz_ramki)
    kat.zapisz(klucz=f'"{klucz_laptopa}"')
    wynik = kat.wykonaj(bez_sieci=False)
    s = wynik.sprawdzenie("ramka_wieczorna")
    assert s.poziom == S.OSTRZEZENIE and "klucz" in s.opis and "[ramki] klucz" in s.rada
    assert klucz_laptopa not in wynik.tekst() and klucz_ramki not in wynik.tekst()
    kat.zapisz(klucz=f'"{klucz_ramki}"')
    wynik = kat.wykonaj(bez_sieci=False)
    assert wynik.sprawdzenie("ramka_wieczorna").poziom == S.OK and klucz_ramki not in json.dumps(wynik.do_slownika())


def test_ramki_proba_ograniczona_limitem(kat, monkeypatch):
    def wisi(host, port, klucz, limit_s):
        time.sleep(30)

    monkeypatch.setattr(S, "_zapytaj_ramke", wisi)
    t = time.perf_counter()
    wynik = kat.wykonaj(bez_sieci=False, limit_ramki_s=0.5)
    assert time.perf_counter() - t < 4.0  # obie ramki rownolegle, kazda najwyzej limit
    assert wynik.sprawdzenie("ramka_poranna").poziom == S.OSTRZEZENIE and "0.5 s" in wynik.sprawdzenie("ramka_poranna").opis
    assert 0 < S.LIMIT_RAMKI_S <= 5.0


# ----------------------------------------------------------------------------- 10. Excel

def test_excel_uruchomiony_ok_nieuruchomiony_ostrzezenie_brak_pywin32_ostrzezenie(kat, monkeypatch):
    s = kat.wykonaj().sprawdzenie("excel")
    assert s.poziom == S.OSTRZEZENIE and "nie jest uruchomiony" in s.opis
    monkeypatch.setattr(excel_com, "_win32com_client", lambda: KlientCom(dziala=True))
    assert kat.wykonaj().sprawdzenie("excel").poziom == S.OK

    def brak():
        raise ImportError("No module named 'win32com'")

    monkeypatch.setattr(excel_com, "_win32com_client", brak)
    s = kat.wykonaj().sprawdzenie("excel")
    assert s.poziom == S.OSTRZEZENIE and "pywin32" in s.opis


def test_excel_ostrzezenie_konfiguracji_logu_poza_dane(kat, monkeypatch):
    monkeypatch.setattr(excel_com, "_win32com_client", lambda: KlientCom(dziala=True))
    kat.zapisz(log_excel=f'"{(kat.tmp / "inne" / "log_excel.csv").as_posix()}"')
    s = kat.wykonaj().sprawdzenie("excel")
    assert s.poziom == S.OSTRZEZENIE and "log_excel" in s.opis


# ----------------------------------------------------------------------------- 11. drugi egzemplarz / zajeta baza

def test_egzemplarz_program_nie_dziala_ok_dziala_ostrzezenie_bez_bledu(kat):
    kat.zaloz_baze()
    assert kat.wykonaj().sprawdzenie("egzemplarz").poziom == S.OK  # brak pliku blokady
    blokada = AP.BlokadaStanowiska(kat.baza).zajmij()
    try:
        wynik = kat.wykonaj()
        s = wynik.sprawdzenie("egzemplarz")
        assert s.poziom == S.OSTRZEZENIE and "jest teraz uruchomiony" in s.opis and wynik.kod_wyjscia == 0
    finally:
        blokada.zwolnij()
    s = kat.wykonaj().sprawdzenie("egzemplarz")
    assert s.poziom == S.OK  # plik blokady zostal, ale nikt go nie trzyma
    AP.BlokadaStanowiska(kat.baza).zajmij().zwolnij()  # proba samokontroli nie zostawila blokady


def test_baza_zajeta_ostrzezenie_nie_blad(kat, monkeypatch):
    kat.zaloz_baze()
    monkeypatch.setattr(S, "CZEKAJ_NA_BAZE_MS", 200)
    pol = sqlite3.connect(kat.baza, isolation_level=None)
    pol.execute("BEGIN EXCLUSIVE")
    try:
        wynik = kat.wykonaj()
    finally:
        pol.execute("ROLLBACK")
        pol.close()
    s = wynik.sprawdzenie("baza")
    assert s.poziom == S.OSTRZEZENIE and "zajeta" in s.opis and wynik.kod_wyjscia == 0
    assert "zajeta" in wynik.sprawdzenie("egzemplarz").opis and wynik.sprawdzenie("egzemplarz").poziom == S.OSTRZEZENIE


# ----------------------------------------------------------------------------- 12. sumy plikow programu

def test_sumy_zgodne_n_z_n_z_pliku_w_katalogu_programu_i_z_opcji(kat, tmp_path):
    k = program_tmp(tmp_path)
    zapisz_sumy(k)
    s = kat.wykonaj(korzen=k).sprawdzenie("sumy")
    assert s.poziom == S.OK and "zgodne 5 z 5" in s.opis
    osobny = zapisz_sumy(k, plik=tmp_path / "sumy_z_paczki.sha256", pomin=(S.PLIK_SUM,))
    (k / S.PLIK_SUM).unlink()
    s = kat.wykonaj(korzen=k, sumy=osobny).sprawdzenie("sumy")
    assert s.poziom == S.OK and "zgodne 5 z 5" in s.opis
    (k / "stanowisko" / "__pycache__").mkdir()  # pliki tworzone przez Pythona i dane lokalne nie sa nadmiarowe
    (k / "stanowisko" / "__pycache__" / "a.cpython-312.pyc").write_bytes(b"\0")
    (k / "dane").mkdir()
    (k / "dane" / "stanowisko.sqlite").write_bytes(b"\0")
    (k / "ustawienia.toml").write_text("# lokalne\n", encoding="ascii")
    assert kat.wykonaj(korzen=k, sumy=osobny).sprawdzenie("sumy").poziom == S.OK


def test_sumy_bez_pliku_kopia_robocza_ostrzezenie(kat, tmp_path):
    s = kat.wykonaj(korzen=program_tmp(tmp_path)).sprawdzenie("sumy")
    assert s.poziom == S.OSTRZEZENIE and "kopia robocza bez pliku sum" in s.opis


def test_sumy_jeden_plik_zmieniony_blad(kat, tmp_path):
    k = program_tmp(tmp_path)
    zapisz_sumy(k)
    (k / "stanowisko" / "a.py").write_bytes(b"A = 2\n")
    wynik = kat.wykonaj(korzen=k)
    s = wynik.sprawdzenie("sumy")
    assert s.poziom == S.BLAD and "zgodne 4 z 5" in s.opis and "zmieniony stanowisko/a.py" in s.opis and wynik.kod_wyjscia == 1


def test_sumy_jeden_plik_brakujacy_blad(kat, tmp_path):
    k = program_tmp(tmp_path)
    zapisz_sumy(k)
    (k / "stanowisko" / "ui" / "b.py").unlink()
    s = kat.wykonaj(korzen=k).sprawdzenie("sumy")
    assert s.poziom == S.BLAD and "zgodne 4 z 5" in s.opis and "brak stanowisko/ui/b.py" in s.opis


@pytest.mark.parametrize("nadmiarowy", ["stanowisko/dodatkowy.py", "modele_plytek/wieczorna/plytka_n7.stl", "json.py", "numpy/__init__.py"])
def test_sumy_jeden_plik_nadmiarowy_blad(kat, tmp_path, nadmiarowy):
    """Ustalenie: plik nadmiarowy w strefie programu (katalogi z listy sum; w katalogu glownym pliki i pakiety, ktore Python
    zaladowalby zamiast wlasciwych) to BLAD - katalog nie jest wtedy rowny wydaniu i moze dzialac inaczej."""
    k = program_tmp(tmp_path)
    zapisz_sumy(k)
    (k / nadmiarowy).parent.mkdir(parents=True, exist_ok=True)
    (k / nadmiarowy).write_bytes(b"X = 1\n")
    s = kat.wykonaj(korzen=k).sprawdzenie("sumy")
    assert s.poziom == S.BLAD and "zgodne 5 z 5" in s.opis and f"nadmiarowy {nadmiarowy}" in s.opis


def test_sumy_lista_pierwszych_10_roznic(kat, tmp_path):
    k = program_tmp(tmp_path)
    for n in range(14):
        (k / "stanowisko" / f"m{n:02d}.py").write_bytes(b"X = 1\n")
    zapisz_sumy(k)
    for n in range(14):
        (k / "stanowisko" / f"m{n:02d}.py").write_bytes(b"X = 2\n")
    s = kat.wykonaj(korzen=k).sprawdzenie("sumy")
    assert s.poziom == S.BLAD and "zgodne 5 z 19" in s.opis and s.opis.count("zmieniony ") == 10 and "i 4 kolejne" in s.opis


@pytest.mark.parametrize("tresc, fragment", [
    ("", "pusty"), ("to nie jest plik sum\n", "wiersz 1"), ("0" * 64 + "  ../poza/katalogiem.py\n", "wiersz 1"),
    ("0" * 64 + "  C:/Windows/notepad.exe\n", "wiersz 1")])
def test_sumy_zly_plik_sum_blad(kat, tmp_path, tresc, fragment):
    k = program_tmp(tmp_path)
    (k / S.PLIK_SUM).write_text(tresc, encoding="ascii")
    s = kat.wykonaj(korzen=k).sprawdzenie("sumy")
    assert s.poziom == S.BLAD and fragment in s.opis


def test_sumy_opcja_wskazuje_brak_pliku_blad_kod_1(kat, capsys, tmp_path):
    kod, wyjscie = uruchom_main(capsys, "--ustawienia", kat.plik, "--bez-sieci", "--sumy", tmp_path / "nie_ma.sha256")
    assert kod == 1 and re.search(r"(?m)^BLAD sumy: ", wyjscie)


def test_sumy_format_sha256sum_tryb_binarny_i_konce_linii(kat, tmp_path):
    k = program_tmp(tmp_path)
    plik = zapisz_sumy(k)
    linie = plik.read_text(encoding="ascii").splitlines()
    plik.write_bytes(("\r\n".join(w.replace("  ", " *", 1) for w in linie) + "\r\n").encode("ascii"))  # "<suma> *<plik>", CRLF
    s = kat.wykonaj(korzen=k).sprawdzenie("sumy")
    assert s.poziom == S.OK and "zgodne 5 z 5" in s.opis


# ----------------------------------------------------------------------------- kryterium 4 i dane osobowe

def test_czas_pelnej_samokontroli_bez_sieci(kat, monkeypatch):
    monkeypatch.undo()  # prawdziwe moduly z DLL
    monkeypatch.setattr(excel_com, "_win32com_client", lambda: KlientCom(dziala=False))
    kat.zaloz_baze()
    wynik = kat.wykonaj()
    assert wynik.czas_s < 20.0 and wynik.do_slownika()["czas_s"] == round(wynik.czas_s, 1)


def test_wyjscie_bez_nazw_zlecen_takze_przy_bledach(kat, capsys):
    zlecenie = kat.foldery["folder_cyrkon"] / f"{NAZWISKO} Anna 3263"
    zlecenie.mkdir()
    (zlecenie / f"{NAZWISKO}_16_cad.stl").write_bytes(b"solid x\nendsolid x\n")
    skan = kat.foldery["folder_eksportu_skanera"] / f"{NAZWISKO}_skan.stl"
    skan.write_bytes(b"solid x\nendsolid x\n")
    for json_ in ((), ("--json",)):
        kod, wyjscie = uruchom_main(capsys, "--ustawienia", kat.plik, "--bez-sieci", *json_)
        assert kod == 0 and NAZWISKO not in wyjscie
