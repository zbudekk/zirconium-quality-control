"""instalacja/instalator.py (E3-A11i): instalacja, aktualizacja, powrot - na malej sztucznej paczce w tmp_path, bez sieci.

Srodowisko wirtualne i pip zastepuje ``SrodowiskoAtrapa`` (poza jednym krotkim testem z prawdziwym ``python -m venv``);
samokontrola to atrapa wg umowy A11s, uruchamiana naprawde jako proces (``python -m stanowisko.samokontrola``).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tomllib
import types
from pathlib import Path

import pytest

from instalacja import instalator as I
from stanowisko import ustawienia as UST
from test_zbuduj_wydanie import STANOWISKO, zbuduj_paczke

PYTHON = Path(sys.executable)


class SrodowiskoAtrapa(I.Srodowisko):
    """Zamiast venv i pip: katalog z plikiem ``pakiety.json``; interpreter wersji = interpreter testow."""

    def __init__(self):
        self.instalacje, self.blad_pip = 0, None

    def utworz(self, python, venv):
        venv.mkdir(parents=True)
        (venv / "pakiety.json").write_text("{}", encoding="ascii")

    def python(self, venv):
        return PYTHON

    def instaluj(self, venv, katalogi_kol, lista, dziennik_pip):
        if self.blad_pip is not None:
            raise self.blad_pip
        self.instalacje += 1
        pakiety = json.loads((venv / "pakiety.json").read_text(encoding="ascii"))
        for nazwa, wersja in I.wczytaj_liste_zamrozona(lista).items():
            assert any(list(Path(k).glob(f"{nazwa}-{wersja}-*.whl")) for k in katalogi_kol), f"brak kola {nazwa}"
            pakiety[nazwa] = wersja
        (venv / "pakiety.json").write_text(json.dumps(pakiety), encoding="ascii")

    def pakiety(self, venv):
        try:
            return dict(json.loads((venv / "pakiety.json").read_text(encoding="ascii")), pip="25.0.1")
        except OSError as e:
            raise I.BladInstalacji(I.KOD_INSTALACJA, "brak srodowiska") from e


class Stanowisko:
    """Katalog instalacji w tmp z gotowymi ustawieniami (foldery pracy istnieja) i licznikiem instalacji pakietow."""

    def __init__(self, tmp: Path):
        self.tmp, self.katalog, self.srodowisko = tmp, tmp / "Stanowisko", SrodowiskoAtrapa()
        self.zegar_n = 0

    def zegar(self) -> dt.datetime:
        self.zegar_n += 1
        return dt.datetime(2026, 11, 20, 12, 0, 0) + dt.timedelta(seconds=self.zegar_n)

    def ustawienia_gotowe(self) -> Path:
        """Ustawienia jak po pierwszej instalacji i uzupelnieniu folderow pracy przez osobe instalujaca."""
        self.katalog.mkdir(parents=True, exist_ok=True)
        tekst = I.ustawienia_ze_wzoru((STANOWISKO / "ustawienia.przyklad.toml").read_bytes(), self.katalog).decode("utf-8")
        for klucz, wzor in (("skaner", "C:/Aidite/Scandata"), ("cyrkon", "C:/sciezka/do/OneDrive/Cyrkon")):
            (self.tmp / "foldery" / klucz).mkdir(parents=True, exist_ok=True)
            assert wzor in tekst
            tekst = tekst.replace(wzor, (self.tmp / "foldery" / klucz).as_posix())
        (self.katalog / "ustawienia.toml").write_bytes(tekst.encode("utf-8"))
        return self.katalog / "ustawienia.toml"

    def zainstaluj(self, paczka: Path, **opcje) -> int:
        return I.zainstaluj(paczka, self.katalog, PYTHON, srodowisko=self.srodowisko, zegar=self.zegar, bez_sieci=True, **opcje)

    def wroc(self, **opcje) -> int:
        return I.wroc(self.katalog, srodowisko=self.srodowisko, zegar=self.zegar, **opcje)

    @property
    def biezaca(self):
        return I.czytaj_wskaznik(self.katalog, I.PLIK_BIEZACEJ)

    @property
    def poprzednia(self):
        return I.czytaj_wskaznik(self.katalog, I.PLIK_POPRZEDNIEJ)

    @property
    def baza(self) -> Path:
        return self.katalog / "dane" / "stanowisko.sqlite"

    def zaloz_baze(self, schemat: int = 1, wiersze: int = 3) -> Path:
        self.baza.parent.mkdir(parents=True, exist_ok=True)
        pol = sqlite3.connect(self.baza)
        pol.execute("CREATE TABLE IF NOT EXISTS skany (id INTEGER PRIMARY KEY, opis TEXT)")
        pol.executemany("INSERT INTO skany (opis) VALUES (?)", [(f"skan {i}",) for i in range(wiersze)])
        pol.execute(f"PRAGMA user_version = {schemat}")
        pol.commit()
        pol.close()
        return self.baza

    def dziennik(self) -> str:
        return (self.katalog / I.PLIK_DZIENNIKA).read_text(encoding="utf-8")


def sha(plik: Path) -> str:
    return hashlib.sha256(plik.read_bytes()).hexdigest()


def liczba_skanow(plik: Path) -> int:
    pol = sqlite3.connect(plik)
    try:
        return pol.execute("SELECT count(*) FROM skany").fetchone()[0]
    finally:
        pol.close()


@pytest.fixture
def st(tmp_path) -> Stanowisko:
    return Stanowisko(tmp_path)


@pytest.fixture
def zainstalowane(st, tmp_path) -> Stanowisko:
    """Stanowisko z zainstalowana wersja 1.0, baza (schemat 1, 3 skany) i plikiem danych."""
    st.ustawienia_gotowe()
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "1.0")) == 0
    st.zaloz_baze()
    (st.katalog / "dane" / "wyniki").mkdir()
    (st.katalog / "dane" / "wyniki" / "skan_wynik.json").write_text('{"gniazda": []}', encoding="ascii")
    return st


# ------------------------------------------------------------------------------------------------ czysta instalacja

def test_czysta_instalacja_najpierw_czerwona_po_poprawce_ustawien_zielona(st, tmp_path, capsys):
    paczka = zbuduj_paczke(tmp_path, "1.0")
    # 1. pierwsza proba: ustawienia ze wzoru, foldery pracy nie istnieja -> samokontrola czerwona -> wersja NIE jest biezaca
    assert st.zainstaluj(paczka) == I.KOD_SAMOKONTROLA_CZERWONA
    wyjscie = capsys.readouterr().out
    assert "BLAD folder_cyrkon: folder nie istnieje" in wyjscie and "SAMOKONTROLA: CZERWONA" in wyjscie
    assert "INSTALACJA: NIEUDANA (kod 1) - wersja biezaca bez zmian: brak" in wyjscie and "CO ZROBIC:" in wyjscie
    assert st.biezaca is None and not (st.katalog / "Stanowisko.cmd").exists()
    assert I.stan_wersji(st.katalog, "1.0") == "zainstalowana" and st.srodowisko.instalacje == 1
    # ustawienia ze wzoru: sciezki danych bezwzgledne w katalogu instalacji (poza katalogiem wersji), plik poprawny dla programu
    ust = UST.wczytaj_ustawienia(st.katalog / "ustawienia.toml")
    korzen = st.katalog.resolve().as_posix()
    assert ust["sciezki"]["baza"] == f"{korzen}/dane/stanowisko.sqlite" and ust["sciezki"]["logi"] == f"{korzen}/dane/logi"
    assert all(Path(v).is_absolute() and "wersje" not in Path(v).parts for v in ust["sciezki"].values())
    # 2. osoba instalujaca poprawia foldery i uruchamia to samo polecenie: bez ponownej instalacji pakietow, wersja biezaca
    plik = st.ustawienia_gotowe()
    suma = sha(plik)
    assert st.zainstaluj(paczka) == 0
    wyjscie = capsys.readouterr().out
    assert "jest juz zainstalowana i zgodna z paczka" in wyjscie and "SAMOKONTROLA: ZIELONA" in wyjscie
    assert "OK sumy: zgodne" in wyjscie and "INSTALACJA: GOTOWA - wersja biezaca 1.0" in wyjscie
    assert st.biezaca == "1.0" and st.poprzednia is None and st.srodowisko.instalacje == 1 and sha(plik) == suma
    assert (st.katalog / "wersja_biezaca.txt").read_bytes() == b"1.0\r\n"
    for nazwa in I.WZORY_SKRYPTOW:  # skrypty uruchamiajace w katalogu instalacji, z CRLF
        tresc = (st.katalog / nazwa).read_bytes()
        assert tresc == (STANOWISKO / "instalacja" / "wzory" / nazwa).read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    wersja = st.katalog / "wersje" / "1.0"
    assert (wersja / "program" / "stanowisko" / "samokontrola.py").is_file() and (wersja / "wydanie.json").is_file()
    assert not (wersja / I.ZNACZNIK_NIEDOKONCZONEJ).exists()
    assert not list((wersja / "program").rglob("__pycache__"))  # katalog programu zostaje zgodny z sumami
    zapis = json.loads((wersja / "instalacja.json").read_text(encoding="ascii"))
    assert zapis["wersja"] == "1.0" and zapis["schemat_bazy"] == 1 and zapis["pakiety"] == 1 and zapis["testy"] is False
    dziennik = st.dziennik()
    for fragment in ("zainstaluj 1.0", "sumy paczki zgodne", "samokontrola: BLAD folder_cyrkon", "SAMOKONTROLA: CZERWONA",
                     "samokontrola: kod wyjscia 1", "SAMOKONTROLA: ZIELONA", "samokontrola: kod wyjscia 0", "INSTALACJA: GOTOWA"):
        assert fragment in dziennik, fragment
    assert "folder nie istnieje" not in dziennik  # do dziennika trafia poziom i kod sprawdzenia, bez opisu ze sciezkami


def test_ustawienia_ze_wzoru_zmieniaja_tylko_sciezki_wzgledne(tmp_path):
    wzor = (STANOWISKO / "ustawienia.przyklad.toml").read_bytes()
    wynik = I.ustawienia_ze_wzoru(wzor, tmp_path / "Kat alog")
    stare, nowe = wzor.decode("utf-8").splitlines(), wynik.decode("utf-8").splitlines()
    assert len(stare) == len(nowe)
    zmienione = [(s, n) for s, n in zip(stare, nowe) if s != n]
    przed, po = tomllib.loads(wzor.decode("utf-8")), tomllib.loads(wynik.decode("utf-8"))
    wzgledne = sorted(k for k, v in przed["sciezki"].items() if not Path(v).is_absolute())
    assert wzgledne == ["baza", "kalibracja_ramek", "log_excel", "logi", "podglady", "pula_cache", "wyniki"]
    assert len(zmienione) == len(wzgledne)
    korzen = (tmp_path / "Kat alog").resolve().as_posix()
    assert all(po["sciezki"][k] == f"{korzen}/{przed['sciezki'][k]}" for k in wzgledne)
    assert {k: v for k, v in po["sciezki"].items() if k not in wzgledne} == {k: v for k, v in przed["sciezki"].items() if k not in wzgledne}
    assert {s: v for s, v in po.items() if s != "sciezki"} == {s: v for s, v in przed.items() if s != "sciezki"}  # [plytki] zostaja wzgledne
    plik = tmp_path / "ustawienia.toml"
    plik.write_bytes(wynik)
    UST.wczytaj_ustawienia(plik)  # program przyjmuje taki plik (ukosniki /, wszystkie klucze)


# ------------------------------------------------------------------------------------------- bledy przed instalacja

def test_zepsuty_plik_w_paczce_zatrzymuje_przed_jakakolwiek_zmiana(st, tmp_path, capsys):
    paczka = zbuduj_paczke(tmp_path, "1.0")
    kolo = next((paczka / "kola").glob("*.whl"))
    kolo.write_bytes(kolo.read_bytes()[:-1] + b"X")
    assert st.zainstaluj(paczka) == I.KOD_PACZKA
    wyjscie = capsys.readouterr().out
    assert "sumy SHA-256 paczki niezgodne: 1 z" in wyjscie and "zmieniony plik kola/pakiecik-1.0-py3-none-any.whl" in wyjscie
    assert "Niczego nie zmieniono" in wyjscie and not st.katalog.exists()
    (paczka / "wydanie.json").unlink()
    assert st.zainstaluj(paczka) == I.KOD_PACZKA and "brak pliku wydanie.json" in capsys.readouterr().out
    (paczka / "SHA256SUMS").unlink()
    assert st.zainstaluj(paczka) == I.KOD_PACZKA and not st.katalog.exists()


def test_zepsuty_plik_przy_aktualizacji_nie_rusza_wersji_biezacej(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    paczka = zbuduj_paczke(tmp_path, "2.0")
    (paczka / "program" / "stanowisko" / "baza.py").write_text("zepsute\n", encoding="ascii")
    przed = {p: sha(p) for p in st.katalog.rglob("*") if p.is_file() and p.name != I.PLIK_DZIENNIKA}
    assert st.zainstaluj(paczka) == I.KOD_PACZKA
    assert "INSTALACJA: NIEUDANA (kod 3) - wersja biezaca bez zmian: 1.0" in capsys.readouterr().out
    assert "sumy SHA-256 paczki niezgodne" in st.dziennik()  # przy aktualizacji nieudana proba zostaje w dzienniku
    assert {p: sha(p) for p in st.katalog.rglob("*") if p.is_file() and p.name != I.PLIK_DZIENNIKA} == przed
    assert st.biezaca == "1.0" and I.stan_wersji(st.katalog, "2.0") == "brak"


def test_paczka_bez_samokontroli_to_blad_wydania(st, tmp_path, capsys):
    paczka = zbuduj_paczke(tmp_path, "1.0", samokontrola=False)
    assert st.zainstaluj(paczka) == I.KOD_PACZKA
    assert "blad wydania: paczka nie zawiera modulu samokontroli" in capsys.readouterr().out and not st.katalog.exists()


def test_brak_albo_zla_wersja_pythona(st, tmp_path, capsys, monkeypatch):
    paczka = zbuduj_paczke(tmp_path, "1.0")
    assert I.zainstaluj(paczka, st.katalog, tmp_path / "nie_ma" / "python.exe", srodowisko=st.srodowisko) == I.KOD_PYTHON
    wyjscie = capsys.readouterr().out
    assert "nie mozna uruchomic Pythona" in wyjscie and "/python" in wyjscie and not st.katalog.exists()
    prawdziwe = I.uruchom
    for odpowiedz, fragment in (("3.11.9 64", "zla wersja Pythona"), ("3.14.0 64", "zla wersja Pythona"), ("3.12.10 32", "(32-bit)")):
        def falszywe(polecenie, **kw):
            if "-c" in polecenie and "struct" in polecenie[polecenie.index("-c") + 1]:
                return subprocess.CompletedProcess(polecenie, 0, odpowiedz + "\n", "")
            return prawdziwe(polecenie, **kw)

        monkeypatch.setattr(I, "uruchom", falszywe)
        assert st.zainstaluj(paczka) == I.KOD_PYTHON
        wyjscie = capsys.readouterr().out
        assert fragment in wyjscie and "a program wymaga 3.12 (64-bit)" in wyjscie and not st.katalog.exists()
    monkeypatch.setattr(I, "uruchom", prawdziwe)
    assert I.sprawdz_pythona(PYTHON, "%d.%d" % sys.version_info[:2]).startswith("%d.%d." % sys.version_info[:2])


def test_katalog_w_folderze_synchronizowanym(st, tmp_path, capsys, monkeypatch):
    paczka = zbuduj_paczke(tmp_path, "1.0")
    monkeypatch.setenv("OneDriveCommercial", str(tmp_path / "Firma"))
    assert I.zainstaluj(paczka, tmp_path / "Firma" / "Stanowisko", PYTHON, srodowisko=st.srodowisko) == I.KOD_INSTALACJA
    wyjscie = capsys.readouterr().out.lower()  # Windows podaje nazwy zmiennych wielkimi literami
    assert "folderze synchronizowanym (zmienna onedrivecommercial)" in wyjscie and not (tmp_path / "Firma").exists()
    assert I.katalog_synchronizowany(tmp_path / "OneDrive - Firma" / "Stanowisko") is not None
    assert I.katalog_synchronizowany(st.katalog) is None


def test_sciezki_wzgledne_w_istniejacych_ustawieniach_zatrzymuja_instalacje(st, tmp_path, capsys):
    """Plik ze starej instalacji (kopia folderu): ``baza = "dane/..."`` trafilaby do katalogu wersji i znikla przy aktualizacji."""
    st.katalog.mkdir()
    shutil.copyfile(STANOWISKO / "ustawienia.przyklad.toml", st.katalog / "ustawienia.toml")
    suma = sha(st.katalog / "ustawienia.toml")
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "1.0")) == I.KOD_USTAWIENIA
    wyjscie = capsys.readouterr().out
    assert "sciezki wzgledne w [sciezki] (baza, kalibracja_ramek, log_excel, logi, podglady, pula_cache, wyniki)" in wyjscie
    assert f'baza = "{st.katalog.resolve().as_posix()}/dane/stanowisko.sqlite"' in wyjscie
    assert sha(st.katalog / "ustawienia.toml") == suma and I.stan_wersji(st.katalog, "1.0") == "brak" and st.srodowisko.instalacje == 0
    (st.katalog / "ustawienia.toml").write_text("[sciezki\n", encoding="ascii")  # blad skladni: komunikat programu, kod 7
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "1.1")) == I.KOD_USTAWIENIA
    assert "plik ustawien nie przechodzi kontroli tej wersji programu: ustawienia.toml" in capsys.readouterr().out


# ---------------------------------------------------------------------------------------- aktualizacja i powrot

def test_aktualizacja_zachowuje_ustawienia_i_dane_robi_kopie_bazy_i_przelacza(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    ustawienia, wynik = st.katalog / "ustawienia.toml", st.katalog / "dane" / "wyniki" / "skan_wynik.json"
    przed = {p: p.read_bytes() for p in (ustawienia, st.baza, wynik)}
    wersja_1 = {p: sha(p) for p in (st.katalog / "wersje" / "1.0").rglob("*") if p.is_file()}
    capsys.readouterr()
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0")) == 0
    wyjscie = capsys.readouterr().out
    assert {p: p.read_bytes() for p in przed} == przed  # ustawienia, baza i dane bajt w bajt
    assert st.biezaca == "2.0" and st.poprzednia == "1.0"
    kopie = list((st.katalog / "dane" / "kopie").glob("*.sqlite"))
    assert len(kopie) == 1 and kopie[0].name.startswith("stanowisko_przed_2.0_20261120_12")
    assert kopie[0].name.endswith("_v1.sqlite") and liczba_skanow(kopie[0]) == 3 and I.wersja_schematu(kopie[0]) == 1
    assert f"kopia bazy: kopie/{kopie[0].name}" in wyjscie and "INSTALACJA: GOTOWA - wersja biezaca 2.0 (poprzednia: 1.0)" in wyjscie
    assert "istniejacy ustawienia.toml zostaje bez zmian" in wyjscie
    assert {p: sha(p) for p in (st.katalog / "wersje" / "1.0").rglob("*") if p.is_file()} == wersja_1  # stara wersja nietknieta
    assert (st.katalog / "wersje" / "2.0" / "program" / "WERSJA").read_text(encoding="ascii") == "2.0\n"


def test_powrot_bez_zmiany_schematu_nie_rusza_bazy(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0")) == 0
    przed = {p: p.read_bytes() for p in (st.katalog / "ustawienia.toml", st.baza)}
    kopie = sorted(p.name for p in (st.katalog / "dane" / "kopie").iterdir())
    capsys.readouterr()
    assert st.wroc() == 0
    wyjscie = capsys.readouterr().out
    assert st.biezaca == "1.0" and st.poprzednia == "2.0"
    assert "schemat zgodny - baza zostaje bez zmian" in wyjscie and "POWROT: GOTOWY - wersja biezaca 1.0" in wyjscie
    assert "SAMOKONTROLA: ZIELONA" in wyjscie
    assert {p: p.read_bytes() for p in przed} == przed and sorted(p.name for p in (st.katalog / "dane" / "kopie").iterdir()) == kopie
    assert st.wroc() == 0 and st.biezaca == "2.0" and st.poprzednia == "1.0"  # ponowny powrot = z powrotem do nowszej
    assert "wroc 1.0 -> 2.0" in st.dziennik() and "wroc 2.0 -> 1.0" in st.dziennik()


def test_powrot_po_migracji_wymaga_zgody_i_przywraca_kopie(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0", migracje="{1: (), 2: ()}")) == 0
    kopia = next((st.katalog / "dane" / "kopie").glob("*_przed_2.0_*_v1.sqlite"))
    st.zaloz_baze(schemat=2, wiersze=2)  # program 2.0 zmigrowal baze i dopisal 2 skany
    baza_v2 = st.baza.read_bytes()
    capsys.readouterr()
    # bez zgody: wykrycie PRZED przelaczeniem, ostrzezenie z licznikami, nic nie zmienione
    assert st.wroc() == I.KOD_BAZA_NOWSZA
    wyjscie = capsys.readouterr().out
    assert st.biezaca == "2.0" and st.poprzednia == "1.0" and st.baza.read_bytes() == baza_v2
    assert "Baza: schemat 2; wersja 1.0 obsluguje schemat do 1" in wyjscie and "wersja 1.0 tej bazy NIE otworzy" in wyjscie
    assert f"Kopia sprzed aktualizacji: {kopia.name}" in wyjscie and "zniknie wszystko, co zapisano po tej chwili: 2 wpisow w 1 tabelach" in wyjscie
    assert "tabela skany: 3 w kopii, 5 teraz (+2)" in wyjscie and "/przywroc-kopie" in wyjscie and "POWROT: NIEUDANA (kod 8)" in wyjscie
    # ze zgoda: kopia v1 wraca, baza v2 odlozona (nie skasowana), wersja 1.0 biezaca
    assert st.wroc(przywroc=True) == 0
    wyjscie = capsys.readouterr().out
    assert st.biezaca == "1.0" and st.poprzednia == "2.0"
    assert I.wersja_schematu(st.baza) == 1 and liczba_skanow(st.baza) == 3
    odlozone = list((st.katalog / "dane" / "kopie").glob("stanowisko_odlozona_v2_*.sqlite"))
    assert len(odlozone) == 1 and odlozone[0].read_bytes() == baza_v2 and liczba_skanow(odlozone[0]) == 5
    assert kopia.is_file() and f"przywrocono kopie {kopia.name}" in wyjscie and f"kopie/{odlozone[0].name}" in wyjscie


def test_powrot_po_migracji_bez_kopii_niczego_nie_zmienia(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0", migracje="{1: (), 2: ()}")) == 0
    shutil.rmtree(st.katalog / "dane" / "kopie")
    st.zaloz_baze(schemat=2, wiersze=1)
    baza = st.baza.read_bytes()
    assert st.wroc(przywroc=True) == I.KOD_BAZA_NOWSZA
    assert "nie ma kopii bazy o schemacie do 1" in capsys.readouterr().out
    assert st.biezaca == "2.0" and st.baza.read_bytes() == baza
    # kopia zrobiona przez sam program przed migracja (baza.py: <baza>.kopia_v1_<czas>.sqlite) tez sie nadaje
    kopia_programu = st.baza.with_name("stanowisko.kopia_v1_20261120_130000.sqlite")
    pol = sqlite3.connect(kopia_programu)
    pol.execute("CREATE TABLE skany (id INTEGER PRIMARY KEY, opis TEXT)")
    pol.execute("PRAGMA user_version = 1")
    pol.commit()
    pol.close()
    assert st.wroc(przywroc=True) == 0 and st.biezaca == "1.0" and I.wersja_schematu(st.baza) == 1


def test_powrot_bez_poprzedniej_wersji(zainstalowane, st, capsys):
    assert zainstalowane.wroc() == I.KOD_BRAK_WERSJI
    assert "nie ma poprzedniej wersji" in capsys.readouterr().out and zainstalowane.biezaca == "1.0"
    assert I.wroc(zainstalowane.tmp / "pusty", srodowisko=st.srodowisko) == I.KOD_BRAK_WERSJI


# ------------------------------------------------------------------------- bledy w trakcie: wersja biezaca nietknieta

@pytest.mark.parametrize("kod_modulu, kod_instalatora, fragment", [
    (1, I.KOD_SAMOKONTROLA_CZERWONA, "samokontrola wersji 2.0 zglosila bledy - wersja biezaca zostaje 1.0"),
    (2, I.KOD_SAMOKONTROLA_NIEWYKONANA, "samokontroli wersji 2.0 nie dalo sie wykonac (kod 2) - wersja biezaca zostaje 1.0"),
])
def test_samokontrola_nowej_wersji_z_bledem_nie_przelacza(zainstalowane, tmp_path, capsys, kod_modulu, kod_instalatora, fragment):
    st = zainstalowane
    skrypty = {n: (st.katalog / n).read_bytes() for n in I.WZORY_SKRYPTOW}
    capsys.readouterr()
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0", kod_samokontroli=kod_modulu)) == kod_instalatora
    wyjscie = capsys.readouterr().out
    assert fragment in wyjscie and f"INSTALACJA: NIEUDANA (kod {kod_instalatora}) - wersja biezaca bez zmian: 1.0" in wyjscie
    assert st.biezaca == "1.0" and st.poprzednia is None
    assert {n: (st.katalog / n).read_bytes() for n in I.WZORY_SKRYPTOW} == skrypty
    assert I.stan_wersji(st.katalog, "2.0") == "zainstalowana"  # gotowa do ponownej proby, ale nie biezaca
    assert st.wroc() == I.KOD_BRAK_WERSJI  # nieudana aktualizacja nie zostaje "poprzednia"


def test_program_uruchomiony_podczas_aktualizacji_i_powrotu(zainstalowane, tmp_path, capsys):
    """Blokade trzyma prawdziwa ``aplikacja.BlokadaStanowiska`` - ten sam plik ``<baza>.blokada``, co w dzialajacym programie."""
    from stanowisko import aplikacja

    st = zainstalowane
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0")) == 0
    paczka_3 = zbuduj_paczke(tmp_path, "3.0")
    instalacje = st.srodowisko.instalacje
    blokada = aplikacja.BlokadaStanowiska(st.baza).zajmij()
    try:
        capsys.readouterr()
        assert st.zainstaluj(paczka_3) == I.KOD_PROGRAM_DZIALA
        wyjscie = capsys.readouterr().out
        assert 'program "Stanowisko" jest uruchomiony' in wyjscie and "Zamknij program" in wyjscie
        assert st.biezaca == "2.0" and I.stan_wersji(st.katalog, "3.0") == "brak" and st.srodowisko.instalacje == instalacje
        assert st.wroc() == I.KOD_PROGRAM_DZIALA and st.biezaca == "2.0" and st.poprzednia == "1.0"
    finally:
        blokada.zwolnij()
    assert st.zainstaluj(paczka_3) == 0 and st.biezaca == "3.0" and st.poprzednia == "2.0"
    with I.BlokadaProgramu(st.baza):  # i odwrotnie: w czasie przelaczania programu nie da sie uruchomic
        with pytest.raises(aplikacja.ProgramJuzDziala):
            aplikacja.BlokadaStanowiska(st.baza).zajmij()
    aplikacja.BlokadaStanowiska(st.baza).zajmij().zwolnij()


def test_brak_miejsca_na_dysku(zainstalowane, tmp_path, capsys, monkeypatch):
    st = zainstalowane
    paczka = zbuduj_paczke(tmp_path, "2.0")
    capsys.readouterr()
    assert st.zainstaluj(paczka, min_wolne_mb=10**9) == I.KOD_INSTALACJA
    assert "za malo miejsca na dysku: potrzeba ok. 1000000000 MB" in capsys.readouterr().out
    monkeypatch.setattr(I.shutil, "disk_usage", lambda _: types.SimpleNamespace(total=10**12, used=10**12 - 10**6, free=10**6))
    assert st.zainstaluj(paczka) == I.KOD_INSTALACJA
    wyjscie = capsys.readouterr().out
    assert f"za malo miejsca na dysku: potrzeba ok. {I.ZAPAS_MB} MB, wolne 0 MB" in wyjscie and "Wersja biezaca bez zmian" in wyjscie
    assert st.biezaca == "1.0" and I.stan_wersji(st.katalog, "2.0") == "brak" and st.srodowisko.instalacje == 1


@pytest.mark.parametrize("blad", [I.BladInstalacji(I.KOD_INSTALACJA, "pip zakonczyl sie bledem (kod 1): No space left on device", "rada"),
                                  KeyboardInterrupt(), OSError(28, "No space left on device")])
def test_przerwany_pip_zostawia_znacznik_a_nastepna_proba_sprzata(zainstalowane, tmp_path, capsys, blad):
    st = zainstalowane
    paczka = zbuduj_paczke(tmp_path, "2.0")
    przed = {p: p.read_bytes() for p in (st.katalog / "ustawienia.toml", st.baza, st.katalog / "wersja_biezaca.txt")}
    st.srodowisko.blad_pip = blad
    capsys.readouterr()
    assert st.zainstaluj(paczka) == I.KOD_INSTALACJA
    wyjscie = capsys.readouterr().out
    assert "INSTALACJA: NIEUDANA (kod 6) - wersja biezaca bez zmian: 1.0" in wyjscie
    assert st.biezaca == "1.0" and st.poprzednia is None and {p: p.read_bytes() for p in przed} == przed
    assert I.stan_wersji(st.katalog, "2.0") == "niedokonczona" and (st.katalog / "wersje" / "2.0" / I.ZNACZNIK_NIEDOKONCZONEJ).is_file()
    assert [w["stan"] for w in I.lista_wersji(st.katalog)] == ["zainstalowana", "niedokonczona"]
    st.srodowisko.blad_pip = None
    assert st.zainstaluj(paczka) == 0
    wyjscie = capsys.readouterr().out
    assert "usunieto niedokonczona instalacje wersji 2.0" in wyjscie and st.biezaca == "2.0" and st.poprzednia == "1.0"
    assert I.stan_wersji(st.katalog, "2.0") == "zainstalowana"


# -------------------------------------------------------------------------------- ponowna instalacja, naprawa, wersje

def test_ponowna_instalacja_tej_samej_wersji_jest_bezpieczna(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    paczka = zbuduj_paczke(tmp_path / "ponownie", "1.0")
    przed = {p: p.read_bytes() for p in (st.katalog / "ustawienia.toml", st.baza)}
    capsys.readouterr()
    assert st.zainstaluj(paczka) == 0
    wyjscie = capsys.readouterr().out
    assert "jest juz zainstalowana i zgodna z paczka" in wyjscie and "kopia bazy niepotrzebna" in wyjscie
    assert st.srodowisko.instalacje == 1 and st.biezaca == "1.0" and st.poprzednia is None and {p: p.read_bytes() for p in przed} == przed
    assert not (st.katalog / "dane" / "kopie").exists()
    # uszkodzony plik programu -> naprawa: wersja zalozona od nowa, dane bez zmian
    (st.katalog / "wersje" / "1.0" / "program" / "stanowisko" / "aplikacja.py").write_text("uszkodzony\n", encoding="ascii")
    assert st.zainstaluj(paczka) == 0
    wyjscie = capsys.readouterr().out
    assert "pliki programu niezgodne z sumami (1) - naprawa" in wyjscie and st.srodowisko.instalacje == 2
    assert {p: p.read_bytes() for p in przed} == przed and st.biezaca == "1.0"
    assert I.sprawdz_sumy(st.katalog / "wersje" / "1.0" / "program", I.wczytaj_sumy(st.katalog / "wersje" / "1.0" / "program" / I.PLIK_SUM_PROGRAMU)) == []


def test_zestaw_testowy_tylko_na_zadanie(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    pakiety = json.loads((st.katalog / "wersje" / "1.0" / "venv" / "pakiety.json").read_text(encoding="ascii"))
    assert pakiety == {"pakiecik": "1.0"}  # domyslnie bez zestawu testowego
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0"), testy=True) == 0
    assert "zestaw testowy (pytest): 1 pakietow" in capsys.readouterr().out
    pakiety = json.loads((st.katalog / "wersje" / "2.0" / "venv" / "pakiety.json").read_text(encoding="ascii"))
    assert pakiety == {"pakiecik": "1.0", "testowy": "2.0"}
    assert json.loads((st.katalog / "wersje" / "2.0" / "instalacja.json").read_text(encoding="ascii"))["testy"] is True
    # /testy na wersji juz zainstalowanej: sam zestaw testowy, bez zakladania wersji od nowa
    assert st.wroc() == 0 and st.biezaca == "1.0"
    instalacje = st.srodowisko.instalacje
    assert st.zainstaluj(zbuduj_paczke(tmp_path / "ponownie", "1.0"), testy=True) == 0
    assert "dokladam zestaw testowy" in capsys.readouterr().out and st.srodowisko.instalacje == instalacje + 1
    assert json.loads((st.katalog / "wersje" / "1.0" / "venv" / "pakiety.json").read_text(encoding="ascii")) == pakiety
    zapis = json.loads((st.katalog / "wersje" / "1.0" / "instalacja.json").read_text(encoding="ascii"))
    assert zapis["testy"] is True and zapis["pakiety"] == 2 and zapis["wersja"] == "1.0"
    assert st.zainstaluj(zbuduj_paczke(tmp_path / "trzeci", "1.0")) == 0 and st.srodowisko.instalacje == instalacje + 1  # bez /testy: zgodna
    assert I.porownaj_pakiety({"pakiecik": "1.1", "obcy": "3", "pip": "25"}, {"pakiecik": "1.0", "drugi": "2"}) == [
        "brak drugi==2", "pakiecik: jest 1.1, ma byc 1.0", "nadmiarowy obcy==3"]


def test_lista_wersji_i_usuwanie(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0")) == 0 and st.zainstaluj(zbuduj_paczke(tmp_path, "3.0")) == 0
    capsys.readouterr()
    assert I.wersje(st.katalog) == 0
    wiersze = capsys.readouterr().out.splitlines()
    assert [w.split()[0] for w in wiersze] == ["1.0", "2.0", "3.0"]
    assert "BIEZACA" in wiersze[2] and "poprzednia" in wiersze[1] and "BIEZACA" not in wiersze[0] and "poprzednia" not in wiersze[0]
    for wersja in ("3.0", "2.0", "9.9"):  # biezaca, poprzednia, nieistniejaca
        assert I.wersje(st.katalog, usun=wersja) == I.KOD_BRAK_WERSJI
    assert sorted(p.name for p in (st.katalog / "wersje").iterdir()) == ["1.0", "2.0", "3.0"]
    przed = {p: p.read_bytes() for p in (st.katalog / "ustawienia.toml", st.baza)}
    assert I.wersje(st.katalog, usun="1.0") == 0
    assert sorted(p.name for p in (st.katalog / "wersje").iterdir()) == ["2.0", "3.0"] and {p: p.read_bytes() for p in przed} == przed
    assert st.biezaca == "3.0" and st.poprzednia == "2.0"


# -------------------------------------------------------------------------------------------------------- drobne

def test_sumy_odrzucaja_sciezki_poza_katalog(tmp_path):
    for wiersz in ("0" * 64 + "  ../poza.txt", "0" * 64 + "  /bezwzgledna", "0" * 64 + "  C:/dysk.txt", "krotka  plik.txt", "0" * 64 + " plik.txt"):
        (tmp_path / "SUMY").write_text(wiersz + "\n", encoding="ascii")
        with pytest.raises(I.BladInstalacji):
            I.wczytaj_sumy(tmp_path / "SUMY")
    (tmp_path / "SUMY").write_text("a" * 64 + "  kat/plik.txt\n" + "b" * 64 + " *inny.bin\n\n", encoding="ascii")
    assert I.wczytaj_sumy(tmp_path / "SUMY") == {"kat/plik.txt": "a" * 64, "inny.bin": "b" * 64}


def test_dziennik_bez_katalogu_profilu(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", r"C:\Users\Jan Kowalski")
    assert I.bez_profilu(r"python c:\users\jan kowalski\AppData\python.exe i C:/Users/Jan Kowalski/x") == \
        r"python %USERPROFILE%\AppData\python.exe i %USERPROFILE%/x"
    dziennik = I.Dziennik(tmp_path, "proba", lambda: dt.datetime(2026, 11, 20, 8, 5, 1))
    dziennik.wpis("START C:\\Users\\Jan Kowalski\\Stanowisko\ndrugi wiersz")
    assert (tmp_path / I.PLIK_DZIENNIKA).read_bytes() == (b"2026-11-20 08:05:01 | proba | START %USERPROFILE%\\Stanowisko\r\n"
                                                         b"2026-11-20 08:05:01 | proba | drugi wiersz\r\n")


def test_opcje_w_stylu_windows_i_wskaznik(tmp_path):
    assert I._normalizuj_argumenty(["zainstaluj", "/katalog", "C:\\X", "/Python", "p.exe", "/testy", "/bez-pauzy", "/nieznana", "C:/a"]) == \
        ["zainstaluj", "--katalog", "C:\\X", "--python", "p.exe", "--testy", "--bez-pauzy", "/nieznana", "C:/a"]
    assert I.czytaj_wskaznik(tmp_path, I.PLIK_BIEZACEJ) is None
    for tresc, wynik in ((b"1.0\r\n", "1.0"), (b"  2.0-rc1 \n", "2.0-rc1"), (b"", None), (b"..\\..\\x", None), (b"\xff\xfe", None)):
        (tmp_path / I.PLIK_BIEZACEJ).write_bytes(tresc)
        assert I.czytaj_wskaznik(tmp_path, I.PLIK_BIEZACEJ) == wynik
    assert I.main(["wersje", "/katalog", str(tmp_path)]) == 0
    assert I.main(["wroc", "/katalog", str(tmp_path), "/przywroc-kopie", "/bez-pauzy"]) == I.KOD_BRAK_WERSJI


def test_skrot_nie_zatrzymuje_instalacji(tmp_path):
    """Skrot zaklada PowerShell (WScript.Shell); gdy polityka komputera na to nie pozwala, wynik to None, nie wyjatek."""
    (tmp_path / "pulpit").mkdir()
    skrot = I.utworz_skrot(tmp_path / "Stanowisko", tmp_path / "pulpit")
    assert skrot is None or (skrot == tmp_path / "pulpit" / "Stanowisko.lnk" and skrot.is_file())
    assert [p.name for p in (tmp_path / "pulpit").iterdir()] == ([] if skrot is None else ["Stanowisko.lnk"])


# --------------------------------------------------------------- prawdziwe srodowisko wirtualne i skrypty .cmd (Windows)

@pytest.mark.skipif(os.name != "nt", reason="skrypty .cmd dzialaja tylko w Windows")
def test_zainstaluj_cmd_prawdziwe_srodowisko_i_skrypty(st, tmp_path):
    """Jedyny test z prawdziwym ``python -m venv`` i pip (jedno male kolo, bez sieci): zainstaluj.cmd -> Stanowisko.cmd -> Wersje.cmd."""
    paczka = Path(shutil.move(zbuduj_paczke(tmp_path, "1.0"), tmp_path / "Paczka ze spacja"))  # sciezki ze spacjami: paczka i katalog
    st.katalog = tmp_path / "Katalog ze spacja" / "Stanowisko"
    st.ustawienia_gotowe()
    srodowisko = {k: v for k, v in os.environ.items() if k.upper() not in ("PYTHONPATH", "STANOWISKO_PYTHON")}

    def cmd(*polecenie) -> subprocess.CompletedProcess:
        # cmd /s /c "<calosc>": zewnetrzne cudzyslowy zdejmuje cmd, wiec sciezki ze spacjami tez dzialaja
        return subprocess.run('cmd /s /c "' + subprocess.list2cmdline(list(map(str, polecenie))) + '"', capture_output=True, text=True,
                              encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, env=srodowisko, timeout=600)

    # zly Python wskazany wprost: stop z kodem 4, zanim cokolwiek powstanie
    wynik = cmd(paczka / "zainstaluj.cmd", "/katalog", st.katalog, "/python", tmp_path / "nie_ma" / "python.exe")
    assert wynik.returncode == I.KOD_PYTHON and "brak Pythona - opcja /python wskazuje plik, ktorego nie ma" in wynik.stdout
    assert not (st.katalog / "wersje").exists()
    wynik = cmd(paczka / "zainstaluj.cmd", "/katalog", st.katalog, "/python", sys.executable, "/bez-sieci", "/testy")
    assert wynik.returncode == 0, wynik.stdout + wynik.stderr
    assert "pakiety zgodne z lista zamrozona: 2 z 2" in wynik.stdout and "INSTALACJA: GOTOWA - wersja biezaca 1.0" in wynik.stdout
    venv = st.katalog / "wersje" / "1.0" / "venv"
    assert (venv / "Scripts" / "python.exe").is_file() and (st.katalog / "wersje" / "1.0" / "pip.log").is_file()
    wynik = cmd(st.katalog / "Stanowisko.cmd", "--atrapa", "--zamknij-po", "1")
    assert wynik.returncode == 0 and "STANOWISKO wersja=1.0 atrapa=True ustawienia=True" in wynik.stdout, wynik.stdout + wynik.stderr
    wynik = cmd(st.katalog / "Polecenie.cmd", "-c", "import sys, pakiecik, testowy; print(sys.prefix); print(sys.path)")
    assert wynik.returncode == 0 and str(venv).lower() in wynik.stdout.splitlines()[0].lower(), wynik.stdout + wynik.stderr
    bazowe = str(Path(sys.base_prefix) / "Lib" / "site-packages").replace("\\", "\\\\")
    assert bazowe.lower() not in wynik.stdout.lower()  # srodowisko wersji nie widzi pakietow interpretera bazowego
    wynik = cmd(st.katalog / "Samokontrola.cmd", "--bez-sieci")
    assert wynik.returncode == 0 and "SAMOKONTROLA: ZIELONA" in wynik.stdout and "OK sumy: zgodne" in wynik.stdout
    wynik = cmd(st.katalog / "Wersje.cmd", "/bez-pauzy")
    assert wynik.returncode == 0 and wynik.stdout.split()[0] == "1.0" and "BIEZACA" in wynik.stdout
    wynik = cmd(st.katalog / "Wroc_do_poprzedniej.cmd", "/bez-pauzy")
    assert wynik.returncode == I.KOD_BRAK_WERSJI and "nie ma poprzedniej wersji" in wynik.stdout
    assert not list((st.katalog / "wersje" / "1.0" / "program").rglob("__pycache__"))
