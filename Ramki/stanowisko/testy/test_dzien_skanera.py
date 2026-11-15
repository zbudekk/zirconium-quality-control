"""dzien_skanera: sesja i manifest (zapis po kazdej akcji, wznowienie po "awarii"), obserwacja folderu na katalogach
tymczasowych (nowy plik, plik rosnacy, zmieniony, podfoldery, typy inne niz STL), kopiowanie bez zmiany oryginalu, SHA,
pominiecie kroku z powodem, raport i ZIP, --sprawdz (takze uszkodzony plik), szybka kontrola na malym sztucznym skanie
i na pliku, ktory nie jest plytka, okno bez ekranu (QT_QPA_PLATFORM=offscreen). Testy pisza tylko do tmp_path."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
import warnings
import zipfile
from pathlib import Path

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QMimeData, QPointF, Qt, QUrl  # noqa: E402
from PySide6.QtGui import QDropEvent  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from stanowisko import dzien_skanera as DS, dzien_skanera_rdzen as R, synth, uklad as U, ustawienia as UST  # noqa: E402

WINDOWS = os.name == "nt"


# ----------------------------------------------------------------------------
# pomocnicze
# ----------------------------------------------------------------------------
def stl_binarny(n: int, ziarno: int = 0) -> bytes:
    """Poprawny binarny STL z ``n`` losowymi trojkatami (to nie jest plytka - do testow kopiowania)."""
    rng = np.random.default_rng(ziarno)
    return b"test".ljust(80, b" ") + int(n).to_bytes(4, "little") + rng.integers(0, 255, 50 * n, dtype=np.uint8).tobytes()


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def na_dysku(sesja: R.Sesja) -> dict:
    return json.loads((sesja.folder / R.PLIK_MANIFESTU).read_text(encoding="utf-8"))


def stan_folderu(folder: Path) -> dict:
    """Nazwy, rozmiary, czasy i sumy wszystkich plikow - do sprawdzenia, ze oryginaly sie nie zmienily."""
    return {p.relative_to(folder).as_posix(): (p.stat().st_size, p.stat().st_mtime_ns, sha(p)) for p in sorted(folder.rglob("*")) if p.is_file()}


class Zegar:
    def __init__(self):
        self.t = 1000.0

    def __call__(self) -> float:
        return self.t


@pytest.fixture
def srodowisko(tmp_path):
    """Folder eksportu skanera z jednym plikiem zastanym, nowa sesja w tmp i zbieracz bez kontroli (obiegi wolane recznie)."""
    eksport = tmp_path / "Scandata"
    eksport.mkdir()
    (eksport / "stary_sprzed_sesji.stl").write_bytes(stl_binarny(5, 99))
    sesja = R.Sesja.nowa(tmp_path / "sesje", foldery=[eksport])
    zegar = Zegar()
    zb = R.Zbieracz(sesja, None, None, "brak", zegar=zegar)
    return eksport, sesja, zb, zegar


def obiegi(zb: R.Zbieracz, ile: int = 3) -> None:
    for _ in range(ile):
        zb.obieg()


def zdarzenia(zb: R.Zbieracz) -> list[dict]:
    wynik = []
    while not zb.zdarzenia.empty():
        wynik.append(zb.zdarzenia.get_nowait())
    return wynik


# ----------------------------------------------------------------------------
# kroki z pliku danych
# ----------------------------------------------------------------------------
def test_kroki_z_pliku_maja_wymagane_minimum():
    kroki, pola = R.wczytaj_kroki()
    idy = [k.id for k in kroki]
    assert len(idy) == len(set(idy))
    for wymagany in ("ustawienia", "pusta", "prace_cale", "powtorka", "inny_eksport", "ukruszone", "potracona", "bokiem", "druga_plytka", "kopia_folderu"):
        assert wymagany in idy, wymagany
    k = {x.id: x for x in kroki}
    assert k["pusta"].kontrola == "plytka_pusta" and k["pusta"].rodzaj_plikow == "siatka" and k["pusta"].ile_plikow == 1 and k["pusta"].wymagany
    assert k["powtorka"].kontrola == "powtorka" and k["powtorka"].porownaj_z == "prace_cale"
    assert k["ustawienia"].rodzaj_plikow == "obraz" and k["kopia_folderu"].kontrola == "kopia_folderu" and idy[-1] == "kopia_folderu"
    assert not k["inny_eksport"].wymagany and not k["potracona"].wymagany and not k["druga_plytka"].wymagany
    assert "czas_skanu" in k["prace_cale"].pola and "gniazda_ukruszone" in k["ukruszone"].wymagane_pola
    assert {"numer_plytki", "wspolczynnik", "gniazda_ukruszone"} <= set(pola) and all(p["etykieta"] for p in pola.values())
    assert all(len(x.instrukcja) > 80 for x in kroki)


@pytest.mark.parametrize("tresc,blad", [
    ('[[krok]]\nid = "a"\ntytul = "A"\ninstrukcja = "x"\n[[krok]]\nid = "a"\ntytul = "B"\ninstrukcja = "y"\n', "powtorzone"),
    ('[[krok]]\nid = "a"\ntytul = "A"\ninstrukcja = "x"\nkontrola = "cos"\n', "kontrola"),
    ('[[krok]]\nid = "a"\ntytul = "A"\ninstrukcja = "x"\nporownaj_z = "b"\n', "porownaj_z"),
    ('[[krok]]\nid = "a"\ntytul = "A"\ninstrukcja = "x"\npola = ["nie_ma"]\n', "definicji"),
    ('[[krok]]\nid = "Zle Id"\ntytul = "A"\ninstrukcja = "x"\n', "id tylko"),
    ("wersja = 1\n", "brak krokow"),
])
def test_zly_plik_krokow_daje_czytelny_blad(tmp_path, tresc, blad):
    p = tmp_path / "kroki.toml"
    p.write_text(tresc, encoding="utf-8")
    with pytest.raises(R.BladKrokow, match=blad):
        R.wczytaj_kroki(p)


# ----------------------------------------------------------------------------
# sesja i manifest
# ----------------------------------------------------------------------------
def test_sesja_zapis_po_kazdej_akcji_i_wznowienie_po_awarii(tmp_path):
    s = R.Sesja.nowa(tmp_path / "sesje", foldery=[tmp_path / "eksport"])
    assert s.folder.parent == tmp_path / "sesje" and len(s.folder.name) == 15  # RRRR-MM-DD_GGMM
    m = na_dysku(s)
    assert m["format"] == R.FORMAT_MANIFESTU and m["biezacy_krok"] == "start" and m["foldery"][0]["etykieta"] == "eksport"
    s.ustaw_notatke("start", "notatka z ąę")
    assert na_dysku(s)["kroki"]["start"]["notatka"] == "notatka z ąę"
    s.ustaw_pole("pusta", "numer_plytki", "1")
    assert na_dysku(s)["kroki"]["pusta"]["pola"] == {"numer_plytki": "1"}
    assert s.zakoncz_krok("start") == "ustawienia"
    m = na_dysku(s)
    assert m["kroki"]["start"]["stan"] == "zrobiony" and m["biezacy_krok"] == "ustawienia" and m["kroki"]["ustawienia"]["rozpoczeto"]
    assert s.pomin_krok("ustawienia", "program skanera nie chciał się uruchomić") == "pytania"
    m = na_dysku(s)
    assert m["kroki"]["ustawienia"]["stan"] == "pominiety" and m["kroki"]["ustawienia"]["powod"] == "program skanera nie chciał się uruchomić"
    s.ustaw_auto_zrzut(True)
    s.stoper_start("pusta")
    assert na_dysku(s)["kroki"]["pusta"]["stoper_start"]
    assert s.stoper_stop("pusta") >= 0 and len(na_dysku(s)["kroki"]["pusta"]["stoper"]) == 1
    w = s.dodaj_plik("pytania", "reczny", "kroki/k03_pytania/reczne/a.txt", 3, "ab" * 32)
    assert na_dysku(s)["pliki"][0]["id"] == w["id"] == 1
    # "awaria": obiekt porzucony bez zamykania; wznowienie czyta wszystko z dysku
    s2 = R.Sesja.wznow(s.folder)
    assert s2.m["kroki"] == s.m["kroki"] and s2.m["pliki"] == s.m["pliki"] and s2.biezacy == "pytania" and s2.m["auto_zrzut"] is True
    assert s2.m["zdarzenia"][-1]["co"] == "wznowienie sesji"
    assert [x["nazwa"] for x in R.Sesja.lista(tmp_path / "sesje")] == [s.folder.name]
    # dwie sesje w tej samej minucie nie nadpisuja sie
    s3 = R.Sesja.nowa(tmp_path / "sesje")
    assert s3.folder != s.folder and (s.folder / R.PLIK_MANIFESTU).exists()


def test_wznowienie_z_kopii_gdy_manifest_uszkodzony(tmp_path):
    s = R.Sesja.nowa(tmp_path / "sesje")
    s.ustaw_notatke("start", "pierwsza")
    s.ustaw_notatke("start", "druga")
    (s.folder / R.PLIK_MANIFESTU).write_bytes(b'{"format": "dzien_skanera/1", "kroki": {"st')  # zapis przerwany w polowie
    s2 = R.Sesja.wznow(s.folder)
    assert s2.m["kroki"]["start"]["notatka"] == "pierwsza"  # stan sprzed ostatniej akcji
    assert "nieczytelny" in (s.folder / R.PLIK_LOGU).read_text(encoding="utf-8")
    (s.folder / R.PLIK_MANIFESTU).unlink()
    (s.folder / (R.PLIK_MANIFESTU + ".bak")).unlink()
    with pytest.raises(FileNotFoundError):
        R.Sesja.wznow(s.folder)


def test_sesja_nie_pisze_poza_swoim_folderem(tmp_path):
    s = R.Sesja.nowa(tmp_path / "sesje")
    with pytest.raises(ValueError, match="poza folderem sesji"):
        s.sciezka("../obok.txt")
    with pytest.raises(ValueError, match="poza folderem sesji"):
        s.sciezka("kroki/../../obok.txt")
    assert s.sciezka("kroki/k01_start/pliki/a.stl").parent.parent.parent.parent == s.folder


def test_kompletnosc_i_pominiecie_z_powodem(tmp_path):
    s = R.Sesja.nowa(tmp_path / "sesje")
    oceny = {o["id"]: o for o in s.kompletnosc()}
    assert oceny["start"]["stan"] == "w_toku" and oceny["pusta"]["stan"] == "czeka"
    braki, pominiete = s.braki()
    assert len(braki) == sum(1 for k in s.kroki if k.wymagany) and not pominiete
    s.zakoncz_krok("start")
    s.pomin_krok("pusta", "nie mam pustej płytki")
    s.dodaj_plik("prace_cale", "obserwacja", "kroki/k06_prace_cale/pliki/Scandata/a.stl", 10, "00" * 32)
    oceny = {o["id"]: o for o in s.kompletnosc()}
    assert oceny["start"]["stan"] == "zrobiony" and oceny["pusta"]["stan"] == "pominiety" and oceny["pusta"]["powod"] == "nie mam pustej płytki"
    assert oceny["prace_cale"]["stan"] == "niepelny" and any("Współczynnik" in b for b in oceny["prace_cale"]["braki"])  # plik jest, pol brak
    for pole, wart in (("numer_plytki", "1"), ("wspolczynnik", "1.2234"), ("czas_skanu", "160 s")):
        s.ustaw_pole("prace_cale", pole, wart)
    assert {o["id"]: o for o in s.kompletnosc()}["prace_cale"]["stan"] == "zrobiony"
    braki, pominiete = s.braki()
    assert len(pominiete) == 1 and "nie mam pustej płytki" in pominiete[0] and not any("pusta" in b.lower() and "skan 1" in b.lower() for b in braki)
    s.przywroc_krok("pusta")
    assert {o["id"]: o for o in s.kompletnosc()}["pusta"]["stan"] == "czeka" and na_dysku(s)["kroki"]["pusta"]["stan"] == "czeka"


# ----------------------------------------------------------------------------
# kopiowanie
# ----------------------------------------------------------------------------
def test_kopiowanie_strumieniowe_z_postepem_bez_zmiany_oryginalu(tmp_path):
    zrodlo = tmp_path / "duzy.stl"
    dane = np.random.default_rng(1).integers(0, 255, 21 * 1024 * 1024, dtype=np.uint8).tobytes()
    zrodlo.write_bytes(dane)
    przed = (zrodlo.stat().st_size, zrodlo.stat().st_mtime_ns)
    postep = []
    wyn = R.kopiuj_plik(zrodlo, tmp_path / "cel" / "gleboko" / "duzy.stl", postep=lambda n, r: postep.append((n, r)))
    cel = tmp_path / "cel" / "gleboko" / "duzy.stl"
    assert wyn["sha256"] == hashlib.sha256(dane).hexdigest() == sha(cel) and wyn["rozmiar"] == len(dane)
    assert len(postep) >= 5 and postep[-1] == (len(dane), len(dane)) and [p[0] for p in postep] == sorted(p[0] for p in postep)  # bloki po 4 MB
    assert (zrodlo.stat().st_size, zrodlo.stat().st_mtime_ns) == przed and zrodlo.read_bytes() == dane
    assert cel.stat().st_mtime_ns == przed[1] and not list(cel.parent.glob("*.czesc"))


def test_brak_miejsca_komunikat_przed_kopiowaniem(tmp_path):
    zrodlo = tmp_path / "a.stl"
    zrodlo.write_bytes(stl_binarny(100))
    with pytest.raises(R.BrakMiejsca, match="Brak miejsca na dysku") as e:
        R.kopiuj_plik(zrodlo, tmp_path / "cel" / "a.stl", wolne=lambda folder: 1000)
    assert e.value.wolne == 1000 and e.value.potrzeba == zrodlo.stat().st_size
    assert not (tmp_path / "cel").exists()  # nic nie zostalo zapisane


def test_zbieracz_przy_braku_miejsca_ponawia(srodowisko):
    eksport, sesja, zb, _ = srodowisko
    zb.wolne = lambda folder: 1000
    (eksport / "skan.stl").write_bytes(stl_binarny(50))
    obiegi(zb)
    z = zdarzenia(zb)
    assert not sesja.m["pliki"] and [x for x in z if x["typ"] == "brak_miejsca"] and "Zwolnij miejsce" in [x for x in z if x["typ"] == "brak_miejsca"][0]["tekst"]
    zb.wolne = R.wolne_miejsce  # miejsce sie znalazlo: plik kopiuje sie sam
    obiegi(zb, 2)
    assert [Path(w["cel"]).name for w in sesja.m["pliki"]] == ["skan.stl"]


@pytest.mark.skipif(not WINDOWS, reason="tryby wspoldzielenia plikow Windows")
def test_windows_nie_blokuje_programu_skanera_i_czeka_na_koniec_zapisu(tmp_path):
    p = tmp_path / "skan.stl"
    p.write_bytes(stl_binarny(10))
    assert R.ktos_pisze(p) is False
    with open(p, "ab"):
        assert R.ktos_pisze(p) is True  # ktos trzyma plik otwarty do zapisu
    assert R.ktos_pisze(p) is False
    with R.otworz_zrodlo(p) as f:  # nasze czytanie nie przeszkadza w zapisie, zmianie nazwy ani usunieciu
        assert f.read(4) == b"test"
        with open(p, "ab") as g:
            g.write(b"x")
        os.replace(p, tmp_path / "inna_nazwa.stl")
    assert (tmp_path / "inna_nazwa.stl").exists() and not p.exists()


def test_stl_binarny_kompletny(tmp_path):
    caly, uciety, tekstowy = tmp_path / "a.stl", tmp_path / "b.stl", tmp_path / "c.stl"
    caly.write_bytes(stl_binarny(7))
    uciety.write_bytes(stl_binarny(7)[:-100])
    tekstowy.write_text("solid x\nfacet normal 0 0 0\n outer loop\n  vertex 0 0 0\n  vertex 1 0 0\n  vertex 0 1 0\n endloop\nendfacet\nendsolid x\n" * 3, encoding="ascii")
    assert R.stl_binarny_kompletny(caly) is True and R.stl_binarny_kompletny(uciety) is False and R.stl_binarny_kompletny(tekstowy) is None


# ----------------------------------------------------------------------------
# obserwacja folderu
# ----------------------------------------------------------------------------
def test_obserwacja_nowe_pliki_podfoldery_i_inne_typy(srodowisko):
    eksport, sesja, zb, _ = srodowisko
    pliki = {"skan.stl": stl_binarny(40, 1), "zlecenie A/dane/chmura.ply": b"ply\nformat ascii 1.0\n", "zlecenie A/model.obj": b"v 0 0 0\n",
             "zlecenie A/TEST1.dentalProject": b"<xml/>", "obrazy/kamera_01.png": b"\x89PNG....", "bez_rozszerzenia": b"cokolwiek"}
    for rel, tresc in pliki.items():
        (eksport / rel).parent.mkdir(parents=True, exist_ok=True)
        (eksport / rel).write_bytes(tresc)
    przed = stan_folderu(eksport)
    zb.obieg()
    assert not sesja.m["pliki"]  # pierwszy odczyt: jeszcze nie wiadomo, czy rozmiar jest staly
    obiegi(zb, 2)
    wpisy = {w["wzgledna"]: w for w in sesja.m["pliki"]}
    assert set(wpisy) == set(pliki)  # plik zastany (sprzed sesji) nie jest kopiowany
    for rel, tresc in pliki.items():
        w = wpisy[rel]
        assert w["cel"] == f"kroki/k01_start/pliki/Scandata/{rel}" and w["krok"] == "start" and w["rodzaj"] == "obserwacja" and w["folder"] == "Scandata"
        kopia = sesja.folder / w["cel"]
        assert kopia.read_bytes() == tresc and w["sha256"] == hashlib.sha256(tresc).hexdigest() and w["rozmiar"] == len(tresc) and w["skopiowano"] and w["mtime"]
    assert stan_folderu(eksport) == przed  # oryginaly bez zmian: nic nie przeniesione, nie skasowane, nie dotkniete
    assert na_dysku(sesja)["pliki"] == sesja.m["pliki"]  # manifest na dysku po kazdej kopii
    assert sorted(z["wpis"]["wzgledna"] for z in zdarzenia(zb) if z["typ"] == "nowy_plik") == sorted(pliki)
    obiegi(zb, 3)
    assert len(sesja.m["pliki"]) == len(pliki)  # nic nie kopiuje sie drugi raz


def test_plik_rosnacy_jest_kopiowany_dopiero_po_ustabilizowaniu(srodowisko):
    eksport, sesja, zb, _ = srodowisko
    p = eksport / "duzy_eksport.bin"
    p.write_bytes(b"a" * 1000)
    zb.obieg()
    for _ in range(4):  # program skanera dopisuje miedzy odczytami: rozmiar ciagle inny
        with open(p, "ab") as f:
            f.write(b"b" * 1000)
        zb.obieg()
        assert not sesja.m["pliki"]
    zb.obieg()
    assert len(sesja.m["pliki"]) == 1 and sesja.m["pliki"][0]["rozmiar"] == 5000 and (sesja.folder / sesja.m["pliki"][0]["cel"]).read_bytes() == p.read_bytes()


@pytest.mark.skipif(not WINDOWS, reason="wykrywanie otwartego zapisu tylko na Windows")
def test_plik_otwarty_do_zapisu_czeka(srodowisko):
    eksport, sesja, zb, _ = srodowisko
    p = eksport / "pisany.stl"
    with open(p, "wb") as f:
        f.write(stl_binarny(30))
        f.flush()
        obiegi(zb, 4)
        assert not sesja.m["pliki"]  # rozmiar staly, ale program skanera nie zamknal jeszcze pliku
    obiegi(zb, 3)
    assert len(sesja.m["pliki"]) == 1


def test_niepelny_stl_czeka_a_po_czasie_jest_kopiowany_z_uwaga(srodowisko):
    eksport, sesja, zb, zegar = srodowisko
    p = eksport / "uciety.stl"
    p.write_bytes(stl_binarny(100)[:2000])
    obiegi(zb, 4)
    assert not sesja.m["pliki"]  # naglowek obiecuje 100 trojkatow: czekamy na reszte
    p.write_bytes(stl_binarny(100))
    obiegi(zb, 3)
    assert len(sesja.m["pliki"]) == 1 and not sesja.m["pliki"][0]["uwagi"]
    q = eksport / "uciety_na_zawsze.stl"
    q.write_bytes(stl_binarny(100)[:2000])
    obiegi(zb, 3)
    assert len(sesja.m["pliki"]) == 1
    zegar.t += R.CZEKAJ_NA_PELNY_STL_S + 1  # lepiej skopiowac za duzo niz za malo
    zb.obieg()
    assert len(sesja.m["pliki"]) == 2 and "niepelny" in " ".join(sesja.m["pliki"][1]["uwagi"])


def test_plik_zmieniony_daje_nowa_wersje_a_ta_sama_tresc_nie(srodowisko):
    eksport, sesja, zb, _ = srodowisko
    p = eksport / "eksport.stl"
    p.write_bytes(stl_binarny(20, 1))
    obiegi(zb)
    p.write_bytes(stl_binarny(25, 2))  # program skanera nadpisal plik nowym skanem
    obiegi(zb)
    assert [w["cel"] for w in sesja.m["pliki"]] == ["kroki/k01_start/pliki/Scandata/eksport.stl", "kroki/k01_start/pliki/Scandata/eksport__zmiana2.stl"]
    assert (sesja.folder / sesja.m["pliki"][0]["cel"]).read_bytes() == stl_binarny(20, 1)  # pierwsza wersja zostala
    assert (sesja.folder / sesja.m["pliki"][1]["cel"]).read_bytes() == stl_binarny(25, 2) and "zmieniona wersja" in sesja.m["pliki"][1]["uwagi"][0]
    st = p.stat()
    os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns + 5_000_000_000))  # zmienil sie tylko czas pliku, tresc ta sama
    obiegi(zb)
    assert len(sesja.m["pliki"]) == 2 and not list((sesja.folder / "kroki").rglob("*zmiana3*"))
    sesja.zakoncz_krok("start")  # w nastepnym kroku zmieniony plik trafia do folderu tego kroku pod zwykla nazwa
    p.write_bytes(stl_binarny(30, 3))
    obiegi(zb)
    assert sesja.m["pliki"][2]["cel"] == "kroki/k02_ustawienia/pliki/Scandata/eksport.stl" and sesja.m["pliki"][2]["krok"] == "ustawienia"


def test_limit_wersji_jednego_pliku_w_kroku(srodowisko, monkeypatch):
    eksport, sesja, zb, _ = srodowisko
    monkeypatch.setattr(R, "LIMIT_WERSJI", 2)
    p = eksport / "baza.db"
    for i in range(4):
        p.write_bytes(b"wersja %d" % i * (i + 1))
        obiegi(zb)
    assert len(sesja.m["pliki"]) == 2 and any("zmienia się raz po raz" in z.get("tekst", "") for z in zdarzenia(zb))
    sesja.zakoncz_krok("start")
    p.write_bytes(b"ostatnia")
    obiegi(zb)
    assert len(sesja.m["pliki"]) == 3 and sesja.m["pliki"][2]["krok"] == "ustawienia"


def test_wznowienie_kopiuje_pliki_ktore_pojawily_sie_w_przerwie(srodowisko):
    eksport, sesja, zb, _ = srodowisko
    (eksport / "a.stl").write_bytes(stl_binarny(10, 1))
    obiegi(zb)
    assert len(sesja.m["pliki"]) == 1
    # program zamkniety (awaria); w tym czasie skaner zapisal kolejny plik
    (eksport / "b.stl").write_bytes(stl_binarny(11, 2))
    sesja2 = R.Sesja.wznow(sesja.folder)
    zb2 = R.Zbieracz(sesja2, None, None, "brak")
    obiegi(zb2)
    assert [w["wzgledna"] for w in sesja2.m["pliki"]] == ["a.stl", "b.stl"]  # a nie drugi raz, b skopiowany, zastany nadal nie
    assert "program byl zamkniety" in " ".join(sesja2.m["pliki"][1]["uwagi"])
    # brak pliku stanu obserwatora: odtworzenie z manifestu, plik zastany tez zostaje skopiowany (lepiej za duzo)
    for nazwa in (R.PLIK_OBSERWATORA, R.PLIK_OBSERWATORA + ".bak"):
        (sesja.folder / nazwa).unlink(missing_ok=True)
    zb3 = R.Zbieracz(R.Sesja.wznow(sesja.folder), None, None, "brak")
    obiegi(zb3)
    assert sorted(w["wzgledna"] for w in zb3.sesja.m["pliki"]) == ["a.stl", "b.stl", "stary_sprzed_sesji.stl"]


def test_folder_ktory_powstaje_pozniej_i_dodanie_folderu(tmp_path):
    sesja = R.Sesja.nowa(tmp_path / "sesje", foldery=[tmp_path / "jeszcze_nie_ma"])
    zb = R.Zbieracz(sesja, None, None, "brak")
    zb.obieg()
    assert any("nie istnieje" in z.get("tekst", "") for z in zdarzenia(zb))
    (tmp_path / "jeszcze_nie_ma").mkdir()
    (tmp_path / "jeszcze_nie_ma" / "pierwszy.stl").write_bytes(stl_binarny(3))
    obiegi(zb)
    assert [w["wzgledna"] for w in sesja.m["pliki"]] == ["pierwszy.stl"]
    inny = tmp_path / "inny dysk" / "Export"
    inny.mkdir(parents=True)
    (inny / "juz_byl.stl").write_bytes(stl_binarny(4))
    zb.dodaj_folder(inny, skopiuj_istniejace=True)  # czlowiek znalazl folder po fakcie: pliki, ktore juz w nim sa, tez sa potrzebne
    obiegi(zb)
    assert sorted(w["cel"] for w in sesja.m["pliki"])[0].endswith("pliki/Export/juz_byl.stl") and len(sesja.m["foldery"]) == 2
    drugi = tmp_path / "Export"
    drugi.mkdir()
    (drugi / "stary.stl").write_bytes(stl_binarny(5))
    zb.dodaj_folder(drugi)  # bez kopiowania istniejacych; etykieta nie moze sie powtorzyc
    obiegi(zb)
    assert sesja.m["foldery"][2]["etykieta"] == "Export_2" and len(sesja.m["pliki"]) == 2
    (drugi / "nowy.stl").write_bytes(stl_binarny(6))
    obiegi(zb)
    assert sesja.m["pliki"][-1]["cel"].endswith("pliki/Export_2/nowy.stl")


def test_folder_sesji_wewnatrz_obserwowanego_nie_kopiuje_sam_siebie(tmp_path):
    eksport = tmp_path / "wszystko"
    sesja = R.Sesja.nowa(eksport / "dzien_skanera", foldery=[eksport])
    zb = R.Zbieracz(sesja, None, None, "brak")
    (eksport / "skan.stl").write_bytes(stl_binarny(8))
    obiegi(zb, 6)
    assert [w["wzgledna"] for w in sesja.m["pliki"]] == ["skan.stl"]


def test_reczne_dodanie_pliku_i_folderu(srodowisko, tmp_path):
    eksport, sesja, zb, _ = srodowisko
    gdzie_indziej = tmp_path / "Pulpit"
    (gdzie_indziej / "eksport reczny" / "pod").mkdir(parents=True)
    (gdzie_indziej / "pojedynczy.stl").write_bytes(stl_binarny(9))
    (gdzie_indziej / "eksport reczny" / "a.stl").write_bytes(stl_binarny(10))
    (gdzie_indziej / "eksport reczny" / "pod" / "notatka.txt").write_text("x", encoding="utf-8")
    przed = stan_folderu(gdzie_indziej)
    zb.dodaj_recznie([gdzie_indziej / "pojedynczy.stl", gdzie_indziej / "eksport reczny"])
    zb.obieg()
    cele = sorted(w["cel"] for w in sesja.m["pliki"])
    assert cele == ["kroki/k01_start/reczne/eksport_reczny/a.stl", "kroki/k01_start/reczne/eksport_reczny/pod/notatka.txt", "kroki/k01_start/reczne/pojedynczy.stl"]
    assert all(w["rodzaj"] == "reczny" and (sesja.folder / w["cel"]).exists() for w in sesja.m["pliki"]) and stan_folderu(gdzie_indziej) == przed
    zb.dodaj_recznie([gdzie_indziej / "pojedynczy.stl"])  # ten sam plik drugi raz: osobna kopia, nic nie jest nadpisywane
    zb.obieg()
    assert sesja.m["pliki"][-1]["cel"] == "kroki/k01_start/reczne/pojedynczy__2.stl"
    zb.wolne = lambda folder: 10
    zb.dodaj_recznie([gdzie_indziej / "eksport reczny"])
    zb.obieg()
    assert len(sesja.m["pliki"]) == 4 and any(z["typ"] == "brak_miejsca" for z in zdarzenia(zb))  # komunikat przed kopiowaniem partii


def test_kopia_calego_folderu_na_koniec(srodowisko):
    eksport, sesja, zb, _ = srodowisko
    (eksport / "zlecenia" / "TEST1").mkdir(parents=True)
    (eksport / "zlecenia" / "TEST1" / "skan.stl").write_bytes(stl_binarny(12))
    obiegi(zb)
    sesja.ustaw_biezacy("kopia_folderu")
    zb.kopia_calych_folderow()
    zb.obieg()
    kopie = sorted(w["cel"] for w in sesja.m["pliki"] if w["rodzaj"] == "kopia_folderu")
    assert kopie == ["kroki/k14_kopia_folderu/kopia_folderu/Scandata/stary_sprzed_sesji.stl", "kroki/k14_kopia_folderu/kopia_folderu/Scandata/zlecenia/TEST1/skan.stl"]
    assert {o["id"]: o for o in sesja.kompletnosc()}["kopia_folderu"]["stan"] == "zrobiony"


def test_przeniesienie_pliku_do_innego_kroku(srodowisko):
    eksport, sesja, zb, _ = srodowisko
    (eksport / "skan.stl").write_bytes(stl_binarny(13))
    obiegi(zb)
    w = sesja.przenies_plik(sesja.m["pliki"][0]["id"], "pusta")
    assert w["krok"] == "pusta" and w["cel"] == "kroki/k05_pusta/pliki/Scandata/skan.stl" and (sesja.folder / w["cel"]).exists()
    assert not (sesja.folder / "kroki/k01_start/pliki/Scandata/skan.stl").exists() and (eksport / "skan.stl").exists()
    assert na_dysku(sesja)["pliki"][0]["krok"] == "pusta" and na_dysku(sesja)["zdarzenia"][-1]["co"].startswith("plik przeniesiony")


def test_zrzut_ekranu_i_zrzut_automatyczny(srodowisko):
    from PIL import Image

    eksport, sesja, zb, zegar = srodowisko
    zb.grab = lambda: Image.new("RGB", (320, 200), (10, 120, 200))
    zb.zrzut("reczny")
    zb.obieg()
    w = sesja.m["pliki"][0]
    assert w["rodzaj"] == "zrzut" and w["cel"].startswith("kroki/k01_start/zrzuty/zrzut_") and w["cel"].endswith(".png")
    assert Image.open(sesja.folder / w["cel"]).size == (320, 200) and w["sha256"] == sha(sesja.folder / w["cel"])
    sesja.ustaw_auto_zrzut(True)
    (eksport / "a.stl").write_bytes(stl_binarny(3))
    (eksport / "b.stl").write_bytes(stl_binarny(4))
    obiegi(zb)
    assert [w["rodzaj"] for w in sesja.m["pliki"]].count("zrzut") == 2  # jeden automatyczny na serie plikow (nie czesciej niz co 10 s)
    zegar.t += 60
    (eksport / "c.stl").write_bytes(stl_binarny(5))
    obiegi(zb)
    assert [w["rodzaj"] for w in sesja.m["pliki"]].count("zrzut") == 3

    def zepsuty():
        raise OSError("brak pulpitu")

    zb.grab = zepsuty  # nieudany zrzut nie zatrzymuje zbierania
    zb.zrzut("reczny")
    (eksport / "d.stl").write_bytes(stl_binarny(6))
    obiegi(zb)
    assert Path(sesja.m["pliki"][-1]["cel"]).name == "d.stl" and any(z["typ"] == "blad" and "Zrzut ekranu nie udał się" in z["tekst"] for z in zdarzenia(zb))


def test_watek_zbieracza_i_wyjatek_w_obiegu_nie_zatrzymuje_zbierania(srodowisko, monkeypatch):
    eksport, sesja, zb, _ = srodowisko
    zb.zegar = time.monotonic
    monkeypatch.setattr(R, "OKRES_ODPYTYWANIA_S", 0.05)
    prawdziwy, licznik = zb._odpytaj_foldery, {"n": 0}

    def psuje_sie_raz():
        licznik["n"] += 1
        if licznik["n"] == 2:
            raise RuntimeError("awaria w obiegu")
        prawdziwy()

    zb._odpytaj_foldery = psuje_sie_raz
    zb.start()
    try:
        (eksport / "w_watku.stl").write_bytes(stl_binarny(7))
        for _ in range(200):
            if sesja.m["pliki"]:
                break
            time.sleep(0.05)
    finally:
        zb.stop()
    assert [w["wzgledna"] for w in sesja.m["pliki"]] == ["w_watku.stl"]
    assert "awaria w obiegu" in (sesja.folder / R.PLIK_LOGU).read_text(encoding="utf-8") and any(z["typ"] == "blad" for z in zdarzenia(zb))


def test_szukanie_swiezych_plikow_skanow(tmp_path):
    (tmp_path / "a" / "b").mkdir(parents=True)
    (tmp_path / "stare").mkdir()
    (tmp_path / "a" / "b" / "nowy.stl").write_bytes(b"x")
    (tmp_path / "a" / "b" / "nowy2.PLY").write_bytes(b"xy")
    (tmp_path / "a" / "tekst.txt").write_bytes(b"x")
    stary = tmp_path / "stare" / "dawny.stl"
    stary.write_bytes(b"x")
    os.utime(stary, (time.time() - 86400, time.time() - 86400))
    wynik = R.szukaj_nowych_siatek([tmp_path])
    assert [(Path(w["folder"]).name, w["plikow"], w["bajtow"]) for w in wynik] == [("b", 2, 3)]
    assert R.szukaj_nowych_siatek([tmp_path], pomijaj=(tmp_path / "a",)) == []


# ----------------------------------------------------------------------------
# raport, sumy, ZIP, --sprawdz
# ----------------------------------------------------------------------------
def sesja_z_plikami(tmp_path) -> tuple[R.Sesja, R.Zbieracz, Path]:
    eksport = tmp_path / "Scandata"
    eksport.mkdir()
    sesja = R.Sesja.nowa(tmp_path / "sesje", foldery=[eksport])
    zb = R.Zbieracz(sesja, None, None, "brak")
    sesja.zakoncz_krok("start")
    sesja.pomin_krok("ustawienia", "nie znalazłem ustawień")
    sesja.ustaw_biezacy("pusta")
    sesja.ustaw_pole("pusta", "numer_plytki", "1")
    sesja.ustaw_notatke("pusta", "płytka nr 1, stara\ndruga linia")
    (eksport / "pusta.stl").write_bytes(stl_binarny(2000, 1))
    (eksport / "obraz.png").write_bytes(b"\x89PNG" + bytes(500))
    obiegi(zb)
    sesja.ustaw_biezacy("prace_cale")
    (eksport / "prace.stl").write_bytes(stl_binarny(3000, 2))
    (eksport / "2026-11-16_Kowalski-11-crown_cad.stl").write_bytes(stl_binarny(10, 3))  # projekt z nazwiskiem: nie moze trafic do paczki
    obiegi(zb)
    return sesja, zb, eksport


def test_zakoncz_i_spakuj_raport_sumy_zip_i_sprawdz(tmp_path):
    sesja, zb, _ = sesja_z_plikami(tmp_path)
    postep = []
    wynik = R.spakuj(sesja, postep=lambda z, r, co: postep.append((z, r, co)))
    assert wynik["braki"] and any("Skan 2" in b for b in wynik["braki"]) and len(wynik["pominiete_kroki"]) == 1  # ostrzezenie, bez blokady
    assert len(wynik["czesci"]) == 1 and postep and postep[-1][0] == postep[-1][1]
    raport = (sesja.folder / R.PLIK_RAPORTU).read_text(encoding="utf-8")
    for fragment in ("## Braki wymaganych krokow", "nie znalazłem ustawień", "płytka nr 1, stara", "kroki/k05_pusta/pliki/Scandata/pusta.stl", "Numer płytki: 1", "## Kompletnosc"):
        assert fragment in raport, fragment
    assert "Kowalski" not in raport and "projekt_pominiety_" in raport  # nazwa projektu (nazwisko) nie trafia do raportu
    sumy = dict(reversed(linia.split("  ", 1)) for linia in (sesja.folder / R.PLIK_SUM).read_text(encoding="utf-8").splitlines())
    assert sumy["kroki/k05_pusta/pliki/Scandata/pusta.stl"] == hashlib.sha256(stl_binarny(2000, 1)).hexdigest()
    assert {R.PLIK_MANIFESTU, R.PLIK_RAPORTU, R.PLIK_LOGU} <= set(sumy) and not any("_cad.stl" in k for k in sumy)
    zip_ = Path(wynik["czesci"][0]["sciezka"])
    assert zip_.parent == sesja.folder / R.KATALOG_PACZKI and zip_.name == f"dzien_skanera_{sesja.m['nazwa']}.zip"
    with zipfile.ZipFile(zip_) as zf:
        nazwy = zf.namelist()
        assert all(n.startswith(sesja.m["nazwa"] + "/") for n in nazwy) and not any("_cad.stl" in n or "Kowalski" in n for n in nazwy)  # bez projektow i nazwisk
        assert f"{sesja.m['nazwa']}/kroki/k06_prace_cale/pliki/Scandata/prace.stl" in nazwy and f"{sesja.m['nazwa']}/{R.PLIK_SUM}" in nazwy
        assert zf.read(f"{sesja.m['nazwa']}/kroki/k05_pusta/pliki/Scandata/pusta.stl") == stl_binarny(2000, 1)
        for nazwa in nazwy:  # takze manifest, log i raport w paczce sa bez nazwiska
            if nazwa.endswith((".json", ".txt", ".md")):
                assert b"Kowalski" not in zf.read(nazwa), nazwa
        m_zip = json.loads(zf.read(f"{sesja.m['nazwa']}/{R.PLIK_MANIFESTU}"))
        assert [w.get("pominiety_w_paczce", False) for w in m_zip["pliki"]].count(True) == 1 and len(m_zip["pliki"]) == len(sesja.m["pliki"])
    assert wynik["pominiete_w_paczce"] == ["kroki/k06_prace_cale/pliki/Scandata/2026-11-16_Kowalski-11-crown_cad.stl"]
    assert (sesja.folder / wynik["pominiete_w_paczce"][0]).exists()  # w folderze sesji plik zostaje
    assert "Kowalski" in (sesja.folder / R.PLIK_MANIFESTU).read_text(encoding="utf-8")  # manifest lokalny bez zmian
    assert na_dysku(sesja)["zakonczono"] and (sesja.folder / R.KATALOG_PACZKI / "paczka.json").exists()
    # sprawdzenie: folder i zip - sumy zgodne, ale braki wymaganych krokow => kod 3
    for cel in (sesja.folder, zip_):
        kod, linie = R.sprawdz(cel)
        tekst = "\n".join(linie)
        assert kod == 3 and "WYNIK: sumy zgodne, ale sa braki krokow" in tekst and "KOMPLETNOSC: BRAKI" in tekst and "BLAD" not in tekst, tekst
    assert DS.main(["--sprawdz", str(zip_)]) == 3 and R.main(["--sprawdz", str(sesja.folder)]) == 3


def test_sprawdz_wykrywa_uszkodzony_i_brakujacy_plik(tmp_path):
    sesja, zb, _ = sesja_z_plikami(tmp_path)
    wynik = R.spakuj(sesja)
    zip_ = Path(wynik["czesci"][0]["sciezka"])
    # uszkodzony plik w folderze sesji (jeden bajt)
    ofiara = sesja.folder / "kroki/k05_pusta/pliki/Scandata/pusta.stl"
    dane = bytearray(ofiara.read_bytes())
    dane[5000] ^= 0xFF
    ofiara.write_bytes(bytes(dane))
    kod, linie = R.sprawdz(sesja.folder)
    assert kod == 1 and any("zla suma pliku kroki/k05_pusta/pliki/Scandata/pusta.stl" in x for x in linie) and "BLAD INTEGRALNOSCI" in linie[-1]
    (sesja.folder / "kroki/k05_pusta/pliki/Scandata/obraz.png").unlink()
    kod, linie = R.sprawdz(sesja.folder)
    assert kod == 1 and any("brak pliku kroki/k05_pusta/pliki/Scandata/obraz.png" in x for x in linie)
    # uszkodzone archiwum (bajty w srodku danych)
    kopia = tmp_path / "uszkodzony" / zip_.name
    kopia.parent.mkdir()
    b = bytearray(zip_.read_bytes())
    for i in range(len(b) // 2, len(b) // 2 + 64):
        b[i] ^= 0xFF
    kopia.write_bytes(bytes(b))
    kod, linie = R.sprawdz(kopia)
    assert kod == 1 and any(x.startswith("BLAD") for x in linie), linie
    assert R.sprawdz(tmp_path / "nie_ma_takiego")[0] == 2
    pusty = tmp_path / "pusty_folder"
    pusty.mkdir()
    assert R.sprawdz(pusty)[0] == 2


def test_archiwum_dzielone_i_brak_czesci(tmp_path):
    sesja, zb, _ = sesja_z_plikami(tmp_path)
    wynik = R.spakuj(sesja, limit=120_000)  # pliki 100 kB i 150 kB: kazdy w swojej czesci
    assert len(wynik["czesci"]) >= 2 and all(Path(c["sciezka"]).name.startswith(f"dzien_skanera_{sesja.m['nazwa']}_cz") for c in wynik["czesci"])
    czesci = [Path(c["sciezka"]) for c in wynik["czesci"]]
    for c in czesci:
        with zipfile.ZipFile(c) as zf:  # kazda czesc jest samodzielnym archiwum z manifestem i sumami
            assert f"{sesja.m['nazwa']}/{R.PLIK_MANIFESTU}" in zf.namelist() and f"{sesja.m['nazwa']}/{R.PLIK_SUM}" in zf.namelist() and zf.testzip() is None
    assert R.sprawdz(czesci[0])[0] == 3 and R.sprawdz(czesci[-1])[0] == 3  # wskazanie dowolnej czesci sprawdza wszystkie
    kod, linie = R.sprawdz(sesja.folder / R.KATALOG_PACZKI)
    assert kod == 3, linie
    wyslane = tmp_path / "odebrane"
    wyslane.mkdir()
    for c in czesci[:-1]:
        shutil.copy(c, wyslane / c.name)
    kod, linie = R.sprawdz(wyslane / czesci[0].name)
    assert kod == 1 and any("brakuje czesci archiwum" in x for x in linie)
    # ponowne spakowanie w jednej czesci usuwa stare czesci (wytwor programu), sesja zmieniona po spakowaniu jest oznaczona
    sesja.ustaw_notatke("pusta", "dopisane po spakowaniu")
    assert na_dysku(sesja)["zmieniono_po_spakowaniu"] is True and not (sesja.folder / R.PLIK_SUM).exists() and (sesja.folder / R.PLIK_SUM_NIEAKTUALNYCH).exists()
    assert R.sprawdz(sesja.folder)[0] == 1  # sumy nieaktualne: trzeba spakowac ponownie
    wynik2 = R.spakuj(sesja)
    assert len(wynik2["czesci"]) == 1 and sorted(p.name for p in (sesja.folder / R.KATALOG_PACZKI).glob("*.zip")) == [Path(wynik2["czesci"][0]["sciezka"]).name]
    assert R.sprawdz(sesja.folder)[0] == 3 and "dopisane po spakowaniu" in (sesja.folder / R.PLIK_RAPORTU).read_text(encoding="utf-8")


def test_sprawdz_komplet_daje_kod_zero(tmp_path):
    """Sesja ze wszystkimi wymaganymi krokami (pliki i pola) => kod 0."""
    eksport = tmp_path / "Scandata"
    eksport.mkdir()
    sesja = R.Sesja.nowa(tmp_path / "sesje", foldery=[eksport])
    zb = R.Zbieracz(sesja, None, None, "brak")
    for i, k in enumerate(sesja.kroki):
        if not k.wymagany:
            continue
        sesja.ustaw_biezacy(k.id)
        for p in k.wymagane_pola:
            sesja.ustaw_pole(k.id, p, "wpisane")
        roz = {"siatka": ".stl", "obraz": ".png", "dowolny": ".dat"}.get(k.rodzaj_plikow)
        for j in range(k.ile_plikow):
            (eksport / f"plik_{i}_{j}{roz}").write_bytes(stl_binarny(3 + i + j))
        obiegi(zb)
        sesja.zakoncz_krok(k.id)
    assert sesja.braki() == ([], [])
    wynik = R.spakuj(sesja)
    assert not wynik["braki"]
    for cel in (sesja.folder, Path(wynik["czesci"][0]["sciezka"])):
        kod, linie = R.sprawdz(cel)
        assert kod == 0 and linie[-1] == "WYNIK: sumy zgodne, komplet" and "KOMPLETNOSC: pelna (wszystkie wymagane kroki zrobione)" in linie, linie


# ----------------------------------------------------------------------------
# szybka kontrola skanu
# ----------------------------------------------------------------------------
def _skan(uk: U.UkladPlytki, numer: int, projekty, seed: int, **opcje):
    rng = np.random.default_rng(seed)
    op = synth.Opcje.z_toml(plytka=uk.nazwa, prace_na_plytce=len(projekty), **opcje)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return synth.generuj_plytke(uk, numer, list(projekty), rng, op, seed)


@pytest.fixture(scope="module")
def ust():
    return UST.wczytaj_ustawienia()


@pytest.fixture(scope="module")
def skany(korony, tmp_path_factory):
    """Male sztuczne skany starych plytek (uklad R54): okragla n8 z 3 pracami, ta sama z innym szumem (powtorka bez ruszania),
    okragla pusta, okragla z innym ukladem prac, kwadrat n1 w polu o srednicy 100 (dolki poza skanem)."""
    d = tmp_path_factory.mktemp("skany_dnia")
    uk = U.wczytaj("okragla_wieczorna_r54")
    skan, prawda = _skan(uk, 8, korony, seed=11, poza_uklad=True, pole=100.0, p_drgniecia=0.0, ubytki_na_prace=(0, 0))
    skan.export(d / "okragla_prace.stl")
    powt = synth.dodaj_szum(skan, 0.005, np.random.default_rng(5))  # drugi skan tej samej plytki: te same prace, inny szum
    powt.export(d / "okragla_powtorka.stl")
    pusta, _ = _skan(uk, 8, [], seed=12, poza_uklad=True, pole=100.0)
    pusta.export(d / "okragla_pusta.stl")
    inny, prawda_inna = _skan(uk, 8, korony[:2], seed=31, poza_uklad=True, pole=100.0, p_drgniecia=0.0, ubytki_na_prace=(0, 0))
    inny.export(d / "okragla_inne_prace.stl")
    kw, _ = _skan(U.wczytaj("wieczorna_r54"), 1, korony[:2], seed=5, poza_uklad=True, pole=100.0, p_drgniecia=0.0)
    kw.export(d / "kwadrat_prace.stl")
    shutil.copy(korony[0], d / "sama_korona.stl")
    return d, prawda, prawda_inna


@pytest.fixture(scope="module")
def wyniki(skany, ust):
    d, _, _ = skany
    return {p.stem: R.kontrola_pliku(p, ust) for p in sorted(d.glob("*.stl"))}


def test_kontrola_rozpoznaje_cala_plytke_uklad_numer_i_prace(skany, wyniki):
    _, prawda, _ = skany
    w = wyniki["okragla_prace"]
    p = w["plytka"]
    assert w["werdykt"] == "zielony" and w["tytul"] == "Skan dobry", (w["uwagi"], w["informacje"])
    assert p["cala"] and p["uklad"] == "okragla_wieczorna_r54" and p["numer"] == 8 and p["numer_zrodlo"] == "dolki"
    assert p["prace"] == 3 and p["gniazda_zajete"] == sorted(x.gniazdo for x in prawda.prace) and p["stozki_dopasowane"] >= 3
    assert 0.0 < p["plaszczyzna_rms_mm"] < 0.06 and p["odstep_wierzch_mm"] and p["odstep_prace_mm"]
    assert w["trojkaty"] > 1000 and len(w["obrys_mm"]) == 3 and 90 < w["obrys_mm"][0] < 110 and w["odstep_mm"] > 0 and w["format"] == "STL binarny"
    assert any(x["uklad"] == "okragla_wieczorna_r54" and x["wynik"] == "ok" for x in w["proby"])
    assert any("numer płytki z dołków: 8" in x for x in w["informacje"]) and any("szum na płaskiej części" in x for x in w["informacje"])
    json.dumps(w)  # wynik jest czystym JSON-em
    pusta = wyniki["okragla_pusta"]["plytka"]
    assert pusta["cala"] and pusta["prace"] == 0 and pusta["uklad"] == "okragla_wieczorna_r54" and wyniki["okragla_pusta"]["werdykt"] == "zielony"


def test_kontrola_kwadratu_w_polu_skanera_bez_numeru(wyniki):
    w = wyniki["kwadrat_prace"]
    p = w["plytka"]
    assert p["cala"] and p["uklad"] == "wieczorna_r54" and p["numer"] is None and p["numer_zrodlo"] == "nieznany" and p["prace"] == 2
    assert w["werdykt"] == "zielony" and any("wpisz numer płytki" in x for x in w["informacje"])


def test_kontrola_pliku_ktory_nie_jest_plytka(tmp_path, skany, wyniki, ust):
    w = wyniki["sama_korona"]
    assert w["werdykt"] == "czerwony" and w["plytka"]["cala"] is False and w["zrob_tak"] and w["trojkaty"] > 0
    skrot = R.ocen_w_kroku(None, w)
    assert skrot["tekst"].startswith("TEN SKAN SIĘ NIE NADA, bo ") and "ZRÓB TAK: " in skrot["tekst"] and "niczego nie kasuj" in skrot["tekst"]
    d, _, _ = skany
    uciety = tmp_path / "uciety.stl"
    uciety.write_bytes((d / "okragla_pusta.stl").read_bytes()[:50_000])
    w = R.kontrola_pliku(uciety, ust)
    assert w["werdykt"] == "czerwony" and w["blad_kod"] == "niepelny_stl" and "ucięty" in w["uwagi"][0]
    smiec = tmp_path / "smiec.stl"
    smiec.write_text("to nie jest plik STL\n" * 20, encoding="utf-8")
    w = R.kontrola_pliku(smiec, ust)
    assert w["werdykt"] == "czerwony" and w["blad_kod"] in ("nieczytelny", "bez_trojkatow", "niepelny_stl")
    w = R.kontrola_pliku(tmp_path / "nie_ma.stl", ust)  # nawet brak pliku nie rzuca wyjatku
    assert w["blad_kod"] == "wyjatek" and w["werdykt"] == "zolty"
    w = R.kontrola_pliku(d / "okragla_pusta.stl", None)  # brak ustawien: plik policzony, plytka niesprawdzona
    assert w["trojkaty"] > 0 and w["blad_kod"] == "brak_ustawien" and w["werdykt"] == "zolty"


def test_oczekiwania_kroku_i_porownanie_powtorki(wyniki):
    kroki = {k.id: k for k in R.wczytaj_kroki()[0]}
    prace, powt, pusta, inne = wyniki["okragla_prace"], wyniki["okragla_powtorka"], wyniki["okragla_pusta"], wyniki["okragla_inne_prace"]
    # pusta plytka z pracami / plytka z pracami bez prac
    s = R.ocen_w_kroku(kroki["pusta"], prace)
    assert s["werdykt"] == "zolty" and "PUSTA" in s["tekst"]
    assert R.ocen_w_kroku(kroki["pusta"], pusta)["werdykt"] == "zielony"
    s = R.ocen_w_kroku(kroki["prace_cale"], pusta)
    assert s["werdykt"] == "zolty" and "nie widzi na płytce żadnej pracy" in s["tekst"]
    assert R.ocen_w_kroku(kroki["prace_cale"], prace)["werdykt"] == "zielony"
    # powtorka bez ruszania: ten sam uklad prac
    s = R.ocen_w_kroku(kroki["powtorka"], powt, prace, "sha-b", "sha-a")
    por = s["porownanie"]
    assert s["werdykt"] == "zielony" and por["porownywalne"] and por["ten_sam_uklad"] and not por["tylko_w_odniesieniu"] and not por["tylko_w_nowym"]
    assert len(por["wspolne_gniazda"]) == 3 and por["przesuniecie_max_mm"] < 0.1 and por["ruch_plytki_mm"] < 0.1 and por["obrot_plytki_deg"] < 0.1
    assert any("ten sam układ prac" in x for x in s["informacje"])
    # ten sam plik zamiast drugiego skanu
    s = R.ocen_w_kroku(kroki["powtorka"], prace, prace, "sha-a", "sha-a")
    assert s["werdykt"] == "czerwony" and "TEN SAM plik" in s["tekst"] and "zeskanuj płytkę jeszcze raz" in s["tekst"]
    # inne prace niz w skanie odniesienia
    s = R.ocen_w_kroku(kroki["powtorka"], inne, prace, "sha-c", "sha-a")
    assert s["werdykt"] == "zolty" and "inne gniazda zajęte" in s["tekst"]
    # brak skanu odniesienia: tylko informacja
    s = R.ocen_w_kroku(kroki["powtorka"], powt, None)
    assert s["werdykt"] == "zielony" and any("nie ma jeszcze skanu odniesienia" in x for x in s["informacje"])
    # krok "ukruszone": ta sama plytka, zmiana gniazd jest informacja, nie uwaga
    s = R.ocen_w_kroku(kroki["ukruszone"], inne, prace, "sha-c", "sha-a")
    assert s["werdykt"] == "zielony" and any("zmiana w gniazdach" in x for x in s["informacje"])


def test_zbieracz_kontroluje_skan_i_porownuje_z_poprzednim(tmp_path, skany, ust):
    d, _, _ = skany
    eksport = tmp_path / "Scandata"
    eksport.mkdir()
    sesja = R.Sesja.nowa(tmp_path / "sesje", foldery=[eksport])
    zb = R.Zbieracz(sesja, ust, UST.PLIK_USTAWIEN, "w_procesie")
    sesja.ustaw_biezacy("prace_cale")
    shutil.copy(d / "okragla_prace.stl", eksport / "skan_1.stl")
    obiegi(zb)
    sesja.zakoncz_krok("prace_cale")
    assert sesja.biezacy == "powtorka"
    shutil.copy(d / "okragla_powtorka.stl", eksport / "skan_2.stl")
    shutil.copy(d / "sama_korona.stl", eksport / "nie_plytka.stl")
    obiegi(zb, 4)
    w = {Path(x["cel"]).name: x for x in sesja.m["pliki"]}
    assert w["skan_1.stl"]["kontrola"]["werdykt"] == "zielony" and w["skan_1.stl"]["kontrola"]["uklad"] == "okragla_wieczorna_r54" and w["skan_1.stl"]["kontrola"]["prace"] == 3
    k2 = w["skan_2.stl"]["kontrola"]
    assert k2["werdykt"] == "zielony" and k2["porownanie"]["z_plikiem"] == "skan_1.stl" and k2["porownanie"]["przesuniecie_max_mm"] < 0.1
    assert w["nie_plytka.stl"]["kontrola"]["werdykt"] == "czerwony"
    assert (sesja.folder / "kontrole" / f"k{w['skan_1.stl']['id']:04d}.json").exists() and na_dysku(sesja)["pliki"][0]["kontrola"]["werdykt"] == "zielony"
    typy = [z["typ"] for z in zdarzenia(zb)]
    assert typy.count("kontrola") == 3 and typy.count("kontrola_start") == 3
    # awaria kontroli nie zatrzymuje zbierania
    zb.ust = {"plytki": {"nie_ma_takiej": "modele_plytek/nie_ma"}}
    shutil.copy(d / "okragla_pusta.stl", eksport / "skan_3.stl")
    (eksport / "po_awarii.txt").write_text("x", encoding="utf-8")
    obiegi(zb, 4)
    nazwy = [Path(x["cel"]).name for x in sesja.m["pliki"]]
    assert "skan_3.stl" in nazwy and "po_awarii.txt" in nazwy and sesja.m["pliki"][nazwy.index("skan_3.stl")]["kontrola"]["werdykt"] in ("czerwony", "zolty")
    raport = R.raport_md(sesja)
    assert "## Wyniki kontroli skanow" in raport and "okragla_wieczorna_r54" in raport and "skan_2.stl" in raport


def test_kontrola_w_osobnym_procesie(tmp_path, skany, ust):
    """Tryb domyslny okna: kazdy skan sprawdza osobny proces Pythona; zbieracz tylko czeka na wynik."""
    d, _, _ = skany
    eksport = tmp_path / "Scandata"
    eksport.mkdir()
    sesja = R.Sesja.nowa(tmp_path / "sesje", foldery=[eksport])
    zb = R.Zbieracz(sesja, ust, UST.PLIK_USTAWIEN, "proces")
    sesja.ustaw_biezacy("pusta")
    shutil.copy(d / "okragla_pusta.stl", eksport / "pusta.stl")
    try:
        for _ in range(900):
            zb.obieg()
            if sesja.m["pliki"] and sesja.m["pliki"][0]["kontrola"]:
                break
            time.sleep(0.2)
    finally:
        zb.stop()
    k = sesja.m["pliki"][0]["kontrola"]
    assert k and k["werdykt"] == "zielony" and k["cala_plytka"] and k["uklad"] == "okragla_wieczorna_r54" and k["numer"] == 8 and k["prace"] == 0, k
    assert not zb.kontrola_w_toku()


# ----------------------------------------------------------------------------
# okno (offscreen)
# ----------------------------------------------------------------------------
@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def okno(app, tmp_path):
    from PIL import Image

    eksport = tmp_path / "Scandata"
    eksport.mkdir()
    sesja = R.Sesja.nowa(tmp_path / "sesje", foldery=[eksport])
    o = DS.Okno(sesja, None, None, "brak", autostart=False, grab=lambda: Image.new("RGB", (64, 48), (0, 0, 0)))
    o.otwieraj_foldery = False
    o.opoznienie_zrzutu_s = 0
    o.komunikaty, o.odpowiedz_tak, o.odpowiedz_tekst = [], True, "bo to test"
    o._komunikat = lambda tytul, tekst: o.komunikaty.append((tytul, tekst))
    o._pytaj_tak_nie = lambda *a, **k: o.odpowiedz_tak
    o._pytaj_tekst = lambda *a, **k: o.odpowiedz_tekst
    o.show()
    yield o, eksport
    o.close()


def takty(o: DS.Okno, obiegow: int = 3) -> None:
    for _ in range(obiegow):
        o.zbieracz.obieg()
    o._takt()


def test_okno_start_kroki_i_przyciski(okno):
    o, eksport = okno
    s = o.sesja
    assert o.lista_krokow.count() == len(s.kroki) and "Krok 1 z" in o.etykieta_tytulu.text() and "Zanim zaczniesz" in o.etykieta_tytulu.text()
    assert "Pięć zasad" in o.pole_instrukcji.toPlainText() and "Obserwuję" in o.etykieta_folderow.text() and str(eksport) in o.etykieta_folderow.text()
    assert "Brakuje (kroki wymagane)" in o.etykieta_kompletnosci.text() and o.lista_krokow.item(0).text().startswith("●")
    assert not o.przycisk_kopia.isVisible() and not o.ramka_stopera.isVisible()
    # notatka zapisuje sie sama; "Krok zrobiony - dalej" przechodzi do nastepnego
    o.pole_notatki.setPlainText("zrzut próbny działa")
    QTest.mouseClick(o.przycisk_zrzut, Qt.LeftButton)
    takty(o, 1)
    assert [w["rodzaj"] for w in s.m["pliki"]] == ["zrzut"] and o.tabela.rowCount() == 1 and "Zrzut ekranu zapisany" in o.etykieta_oceny.text()
    QTest.mouseClick(o.przycisk_dalej, Qt.LeftButton)
    assert s.biezacy == "ustawienia" and na_dysku(s)["biezacy_krok"] == "ustawienia"
    assert na_dysku(s)["kroki"]["start"]["notatka"] == "zrzut próbny działa" and na_dysku(s)["kroki"]["start"]["stan"] == "zrobiony"
    assert "Krok 2 z" in o.etykieta_tytulu.text() and o.lista_krokow.item(0).text().startswith("✔") and o.tabela.rowCount() == 0
    # pola kroku; brak zrzutow => pytanie "przejsc mimo to?" (odpowiedz Nie zostawia w kroku)
    assert set(o.pola) == {"wersja_programu", "folder_zapisu"}
    o.pola["folder_zapisu"].setText("C:/Aidite/Scandata")
    o.odpowiedz_tak = False
    QTest.mouseClick(o.przycisk_dalej, Qt.LeftButton)
    assert s.biezacy == "ustawienia" and na_dysku(s)["kroki"]["ustawienia"]["pola"]["folder_zapisu"] == "C:/Aidite/Scandata"
    # "Nie udalo sie / pomijam, bo ..." zapisuje powod i nie blokuje
    QTest.mouseClick(o.przycisk_pomin, Qt.LeftButton)
    assert na_dysku(s)["kroki"]["ustawienia"]["stan"] == "pominiety" and na_dysku(s)["kroki"]["ustawienia"]["powod"] == "bo to test" and s.biezacy == "pytania"
    assert o.lista_krokow.item(1).text().startswith("✖")
    # klik w krok na liscie = nowe pliki trafiaja do tego kroku; stoper zapisuje czas
    o.lista_krokow.setCurrentRow(s.numer_kroku("prace_cale") - 1)
    assert s.biezacy == "prace_cale" and o.ramka_stopera.isVisible() and "czas_skanu" in o.pola
    QTest.mouseClick(o.przycisk_stoper_start, Qt.LeftButton)
    QTest.mouseClick(o.przycisk_stoper_stop, Qt.LeftButton)
    assert len(na_dysku(s)["kroki"]["prace_cale"]["stoper"]) == 1 and o.pola["czas_skanu"].text().endswith(" s")
    # cofniecie pominiecia
    o.lista_krokow.setCurrentRow(1)
    QTest.mouseClick(o.przycisk_przywroc, Qt.LeftButton)
    assert na_dysku(s)["kroki"]["ustawienia"]["stan"] == "czeka"


def test_okno_zbiera_pliki_przeciaganie_i_pakowanie(okno, tmp_path):
    o, eksport = okno
    s = o.sesja
    o.lista_krokow.setCurrentRow(s.numer_kroku("pusta") - 1)
    (eksport / "TEST1").mkdir()
    (eksport / "TEST1" / "skan_pusta.stl").write_bytes(stl_binarny(500))
    takty(o)
    assert o.tabela.rowCount() == 1 and o.tabela.item(0, 1).text() == "skan_pusta.stl" and o.tabela.item(0, 4).text() == "skopiowany"
    assert "skan_pusta.stl" in o.etykieta_oceny.text() and o.kolor_oceny == "zielony" and "[1/1]" in o.lista_krokow.item(s.numer_kroku("pusta") - 1).text()
    assert "w sesji 1 plików" in o.etykieta_stanu.text()
    # przeciagniecie pliku na okno
    obcy = tmp_path / "Pulpit" / "eksport z innego miejsca.stl"
    obcy.parent.mkdir()
    obcy.write_bytes(stl_binarny(20))
    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(str(obcy))])
    o.dropEvent(QDropEvent(QPointF(20, 20), Qt.CopyAction, mime, Qt.LeftButton, Qt.NoModifier))
    takty(o, 1)
    assert o.tabela.rowCount() == 2 and s.m["pliki"][-1]["rodzaj"] == "reczny" and obcy.exists()
    # przeniesienie pliku do innego kroku
    o.tabela.selectRow(1)
    o._pytaj_wybor = lambda tytul, tekst, pozycje: pozycje[s.numer_kroku("druga_plytka") - 1]
    QTest.mouseClick(o.przycisk_przenies, Qt.LeftButton)
    assert s.m["pliki"][-1]["krok"] == "druga_plytka" and o.tabela.rowCount() == 1
    # kopia calego folderu w ostatnim kroku
    o.lista_krokow.setCurrentRow(s.numer_kroku("kopia_folderu") - 1)
    assert o.przycisk_kopia.isVisible()
    QTest.mouseClick(o.przycisk_kopia, Qt.LeftButton)
    takty(o, 1)
    assert [w["rodzaj"] for w in s.m["pliki"]].count("kopia_folderu") == 1
    # "Zakoncz i spakuj": ostrzezenie o brakach (odpowiedz Nie = nic sie nie dzieje), potem paczka mimo brakow
    o.odpowiedz_tak = False
    QTest.mouseClick(o.przycisk_spakuj, Qt.LeftButton)
    takty(o, 1)
    assert o.wynik_paczki is None and not (s.folder / R.KATALOG_PACZKI).exists()
    o.odpowiedz_tak = True
    QTest.mouseClick(o.przycisk_spakuj, Qt.LeftButton)
    assert not o.przycisk_spakuj.isEnabled()
    takty(o, 1)
    assert o.przycisk_spakuj.isEnabled() and o.wynik_paczki and o.wynik_paczki["braki"] and Path(o.wynik_paczki["czesci"][0]["sciezka"]).exists()
    assert o.komunikaty and "BRAKI wymaganych kroków" in o.komunikaty[-1][1] and "Spakowano" in o.etykieta_kompletnosci.text()
    assert R.sprawdz(s.folder)[0] == 3


def test_okno_wyjatek_nie_zamyka_okna_i_trafia_do_logu(okno):
    o, _ = okno

    def awaria(*a, **k):
        raise RuntimeError("celowa awaria w obsłudze przycisku")

    o.sesja.zakoncz_krok = awaria
    QTest.mouseClick(o.przycisk_dalej, Qt.LeftButton)
    assert o.isVisible() and "celowa awaria" in (o.sesja.folder / R.PLIK_LOGU).read_text(encoding="utf-8")
    assert "Błąd programu" in o.lista_komunikatow.item(o.lista_komunikatow.count() - 1).text()
    o.zbieracz.zdarzenia.put({"typ": "nieznany_typ"})
    o.zbieracz.zdarzenia.put({"typ": "kontrola"})  # zdarzenie bez wymaganych pol: blad obslugi nie zatrzymuje zegara
    o._takt()
    assert o.isVisible() and o.zegar.isActive()


def test_okno_brak_miejsca_pokazuje_alarm(okno):
    o, eksport = okno
    o.zbieracz.wolne = lambda folder: 5
    (eksport / "skan.stl").write_bytes(stl_binarny(100))
    takty(o)
    assert not o.etykieta_alarmu.isHidden() and "Brak miejsca na dysku" in o.etykieta_alarmu.text() and not o.sesja.m["pliki"]
    o.zbieracz.wolne = R.wolne_miejsce
    takty(o, 2)
    assert o.etykieta_alarmu.isHidden() and len(o.sesja.m["pliki"]) == 1


def test_wybor_sesji_wznawia_niedokonczona(tmp_path):
    class A:
        sesja, nowa, dane, folder = None, False, tmp_path / "sesje", [str(tmp_path / "eksport")]

    s1 = DS.wybierz_sesje(A, None)
    s1.ustaw_notatke("start", "z pierwszego uruchomienia")
    s2 = DS.wybierz_sesje(A, None)  # ponowne uruchomienie po awarii: ta sama sesja
    assert s2.folder == s1.folder and s2.m["kroki"]["start"]["notatka"] == "z pierwszego uruchomienia" and s2.m["foldery"][0]["etykieta"] == "eksport"
    assert DS.wybierz_sesje(A, None, pytaj=lambda tytul, tekst: False).folder != s1.folder  # czlowiek wybral nowa sesje
    A.nowa = True
    assert DS.wybierz_sesje(A, None).folder not in (s1.folder,)


def test_okno_z_kontrola_w_tle_na_sztucznym_skanie(app, tmp_path, skany, ust):
    """Okno z watkiem zbieracza i kontrola w osobnym procesie: skan wrzucony do folderu eksportu dostaje ocene, okno zyje."""
    d, _, _ = skany
    eksport = tmp_path / "Scandata"
    eksport.mkdir()
    sesja = R.Sesja.nowa(tmp_path / "sesje", foldery=[eksport])
    sesja.ustaw_biezacy("pusta")
    o = DS.Okno(sesja, ust, UST.PLIK_USTAWIEN, "proces")
    o.otwieraj_foldery = False
    o.show()
    try:
        shutil.copy(d / "okragla_pusta.stl", eksport / "pusta_n8.stl")
        widziano_sprawdzanie = False
        for _ in range(1800):
            QTest.qWait(100)
            widziano_sprawdzanie |= "Sprawdzam" in o.etykieta_oceny.text()
            if sesja.m["pliki"] and sesja.m["pliki"][0]["kontrola"] and o.kolor_oceny != "szary":
                break
        k = sesja.m["pliki"][0]["kontrola"]
        assert k and k["werdykt"] == "zielony" and k["uklad"] == "okragla_wieczorna_r54", k
        assert widziano_sprawdzanie and o.kolor_oceny == "zielony" and "SKAN DOBRY" in o.etykieta_oceny.text() and "Skan dobry" in o.tabela.item(0, 4).text()
    finally:
        o.close()
    assert not o.zbieracz._watek.is_alive()
