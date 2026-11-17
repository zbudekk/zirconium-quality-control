"""indeks.py (E3-A4): indeks folderow "Cyrkon" i "Prywatne" -> tabele `zlecenia`, `projekty`, `cechy_stl`.

Kryteria planu etapu 3 (sekcja 4.1, E3-A4) sprawdzane tutaj: 1 (kuweta poprawna w 40 z 40 po indeksowaniu drzewa),
2 (liczba nowych = liczba plikow STL; drugi przebieg 0 nowych i cechy tylko dla nowych i zmienionych; plik usuniety =
`usuniety`; brak calego katalogu zrodla = zrodlo pominiete bez oznaczania usuniec). Drzewo w tmp_path, nazwy FIKCYJNE,
pliki STL = male atrapy koron (`narzedzia/drzewo_syntetyczne.py`).
"""
from __future__ import annotations

import datetime as dt
import json
import shutil

import numpy as np
import pytest
import trimesh

import drzewo_syntetyczne as D
from stanowisko import baza as B
from stanowisko import indeks as I
from stanowisko import katalog as K
from stanowisko import synth as S

TERAZ = dt.datetime(2026, 11, 17, 10, 0)  # wtorek
WCZORAJ = TERAZ - dt.timedelta(days=1)


@pytest.fixture
def baza(tmp_path):
    b = B.otworz(tmp_path / "dane" / "stanowisko.sqlite")
    yield b
    b.zamknij()


@pytest.fixture(scope="module")
def drzewo40(tmp_path_factory):
    """Wzorcowe drzewo 40 zlecen (budowane raz); kazdy test dostaje wlasna kopie."""
    cel = tmp_path_factory.mktemp("drzewo40")
    prawda = D.zbuduj(cel, zlecen=40, seed=1, kiedy=WCZORAJ)
    return cel, prawda


@pytest.fixture
def drzewo(drzewo40, tmp_path):
    zrodlo, prawda = drzewo40
    cel = tmp_path / "drzewo"
    shutil.copytree(zrodlo, cel)  # copytree zachowuje czasy plikow
    return cel, prawda


def zrodla(cel):
    return {"cyrkon": cel / "Cyrkon", "prywatne": cel / "Prywatne"}


def liczba(b, tabela, warunek="1"):
    return b.wiersz(f"SELECT count(*) AS n FROM {tabela} WHERE {warunek}")["n"]


def test_kryterium1_kuweta_poprawna_w_40_z_40_po_indeksowaniu(baza, drzewo):
    cel, prawda = drzewo
    r = I.indeksuj(baza, zrodla(cel), TERAZ)
    assert r.zlecen == 40 and r.zlecenia_nowe == 40 and r.bledy == 0
    w_bazie = {(w["zrodlo"], w["folder"]): w["kuweta"] for w in baza.wiersze("SELECT zrodlo, folder, kuweta FROM zlecenia")}
    trafione = sum(w_bazie.get((z.zrodlo, z.folder)) == z.kuweta for z in prawda)
    assert trafione == 40
    assert {z.wzor for z in prawda} == set(range(10))


def test_kryterium2_nowe_rowne_liczbie_plikow_drugi_przebieg_zero(baza, drzewo):
    cel, prawda = drzewo
    plikow = sum(len(z.pliki) for z in prawda)
    r = I.indeksuj(baza, zrodla(cel), TERAZ)
    assert r.nowe == plikow and r.zmienione == 0 and r.usuniete == 0
    assert liczba(baza, "projekty") == plikow
    skroty = {S.skrot_pliku(p) for p in cel.rglob("*.stl")}
    assert len(skroty) == plikow  # kazdy plik ma inna zawartosc
    assert r.cechy_policzone == plikow and liczba(baza, "cechy_stl") == plikow
    assert {w["sha16"] for w in baza.wiersze("SELECT sha16 FROM projekty")} == skroty
    r2 = I.indeksuj(baza, zrodla(cel), TERAZ)
    assert (r2.nowe, r2.zmienione, r2.usuniete, r2.cechy_policzone, r2.zlecenia_nowe) == (0, 0, 0, 0, 0)
    assert r2.bez_zmian == plikow


def test_kryterium2_cechy_tylko_dla_zmienionych_i_plik_usuniety(baza, drzewo):
    cel, prawda = drzewo
    I.indeksuj(baza, zrodla(cel), TERAZ)
    z0, z1 = prawda[0], prawda[1]
    zmieniany = cel / "Cyrkon" / z0.folder / z0.pliki[0]
    stary_sha = S.skrot_pliku(zmieniany)
    D.zapisz_stl(D.atrapa(np.random.default_rng(99)), zmieniany, TERAZ - dt.timedelta(hours=1))
    usuwany = cel / "Cyrkon" / z1.folder / z1.pliki[0]
    usuwany.unlink()
    r = I.indeksuj(baza, zrodla(cel), TERAZ)
    assert (r.nowe, r.zmienione, r.usuniete, r.cechy_policzone) == (0, 1, 1, 1)
    w = baza.wiersz("SELECT p.* FROM projekty p JOIN zlecenia z ON z.id = p.zlecenie_id WHERE z.folder = ? AND p.plik = ?",
                    (z0.folder, z0.pliki[0]))
    assert w["sha16"] == S.skrot_pliku(zmieniany) != stary_sha and w["usuniety"] == 0
    assert w["mtime_ns"] == zmieniany.stat().st_mtime_ns and w["rozmiar"] == zmieniany.stat().st_size
    u = baza.wiersz("SELECT p.usuniety FROM projekty p JOIN zlecenia z ON z.id = p.zlecenie_id WHERE z.folder = ? AND p.plik = ?",
                    (z1.folder, z1.pliki[0]))
    assert u["usuniety"] == 1
    r = I.indeksuj(baza, zrodla(cel), TERAZ)
    assert (r.nowe, r.zmienione, r.usuniete, r.cechy_policzone) == (0, 0, 0, 0)


def test_kryterium2_folder_usuniety_oznacza_zlecenie_i_projekty(baza, drzewo):
    cel, prawda = drzewo
    I.indeksuj(baza, zrodla(cel), TERAZ)
    z = prawda[2]
    shutil.rmtree(cel / "Cyrkon" / z.folder)
    r = I.indeksuj(baza, zrodla(cel), TERAZ)
    assert r.zlecenia_usuniete == 1 and r.usuniete == len(z.pliki)
    zl = baza.wiersz("SELECT * FROM zlecenia WHERE folder = ?", (z.folder,))
    assert zl["usuniety"] == 1
    assert liczba(baza, "projekty", f"zlecenie_id = {zl['id']} AND usuniety = 0") == 0


def test_kryterium2_brak_katalogu_zrodla_bez_oznaczania_usuniec(baza, drzewo):
    cel, prawda = drzewo
    I.indeksuj(baza, zrodla(cel), TERAZ)
    prywatnych = sum(len(z.pliki) for z in prawda if z.zrodlo == "prywatne")
    assert prywatnych > 0
    (cel / "Prywatne").rename(cel / "Prywatne_niezsynchronizowane")
    r = I.indeksuj(baza, zrodla(cel), TERAZ)
    assert r.zrodla == {"cyrkon": "ok", "prywatne": "brak katalogu"}
    assert (r.usuniete, r.zlecenia_usuniete) == (0, 0)
    assert liczba(baza, "projekty p JOIN zlecenia z ON z.id = p.zlecenie_id", "z.zrodlo = 'prywatne' AND p.usuniety = 0") == prywatnych
    # zrodlo podane jako None (brak klucza w ustawieniach) tez jest pominiete
    r = I.indeksuj(baza, {"cyrkon": cel / "Cyrkon", "prywatne": None}, TERAZ)
    assert r.zrodla["prywatne"] == "brak katalogu" and r.usuniete == 0


def test_plik_przywrocony_i_ten_sam_plik_w_innym_folderze_bez_liczenia_cech(baza, drzewo):
    cel, prawda = drzewo
    I.indeksuj(baza, zrodla(cel), TERAZ)
    z = prawda[0]
    zrodlowy = cel / "Cyrkon" / z.folder / z.pliki[0]
    kopia = cel / "Cyrkon" / "Probna 9999 kopia" / "zab 11.stl"
    kopia.parent.mkdir()
    shutil.copy2(zrodlowy, kopia)
    r = I.indeksuj(baza, zrodla(cel), TERAZ)
    assert (r.nowe, r.cechy_policzone, r.cechy_z_pamieci, r.zlecenia_nowe) == (1, 0, 1, 1)
    assert liczba(baza, "projekty", f"sha16 = '{S.skrot_pliku(zrodlowy)}'") == 2


def test_cechy_rowne_katalogowi_i_miniatura_png(baza, drzewo):
    cel, prawda = drzewo
    I.indeksuj(baza, zrodla(cel), TERAZ)
    z = next(z for z in prawda if z.pliki[0].endswith("_cad.stl"))
    plik = cel / ("Cyrkon" if z.zrodlo == "cyrkon" else "Prywatne") / z.folder / z.pliki[0]
    c = baza.wiersz("SELECT * FROM cechy_stl WHERE sha16 = ?", (S.skrot_pliku(plik),))
    oczek = K.cechy(S.wczytaj_projekt(plik), plik.name)
    assert c["trojkaty"] == oczek.trojkaty and c["szczelny"] == int(oczek.szczelna)
    for kol, wart in (("objetosc_mm3", oczek.objetosc_mm3), ("hull_mm3", oczek.hull_mm3), ("pole_mm2", oczek.pole_mm2),
                      ("obrys_a_mm", oczek.obrys_xy_mm[0]), ("obrys_b_mm", oczek.obrys_xy_mm[1]), ("wysokosc_mm", oczek.wysokosc_mm)):
        assert c[kol] == pytest.approx(wart, rel=1e-6), kol
    assert c["wersja_cech"] == I.WERSJA_CECH and c["policzono"] == TERAZ.isoformat()
    assert bytes(c["miniatura"][:8]) == b"\x89PNG\r\n\x1a\n"
    p = baza.wiersz("SELECT * FROM projekty WHERE sha16 = ?", (S.skrot_pliku(plik),))
    zeby, typ = K.typ_i_zeby_z_nazwy(plik.name)[1], K.typ_i_zeby_z_nazwy(plik.name)[0]
    assert p["zeby"] == "-".join(zeby) and p["typ"] == typ and p["zaindeksowano"] == TERAZ.isoformat()


def test_zapis_zlecenia_folder_doslownie_norm_i_czas(baza, drzewo):
    cel, prawda = drzewo
    I.indeksuj(baza, zrodla(cel), TERAZ)
    nfd = next(z for z in prawda if z.wzor == 8)
    w = baza.wiersz("SELECT * FROM zlecenia WHERE folder = ?", (nfd.folder,))
    assert w is not None, "folder zapisany doslownie (NFD), zeby dalo sie zbudowac sciezke"
    assert w["folder_norm"] == w["folder_norm"].lower() and w["kuweta"] == nfd.kuweta
    assert w["mtime"] == pytest.approx(WCZORAJ.timestamp(), abs=1.0)
    assert w["dodano"] == TERAZ.isoformat() and w["usuniety"] == 0
    pryw = next(z for z in prawda if z.zrodlo == "prywatne")
    assert baza.wiersz("SELECT zrodlo, kuweta FROM zlecenia WHERE folder = ?", (pryw.folder,)) == {"zrodlo": "prywatne", "kuweta": pryw.kuweta}


def test_stary_folder_pomijany_i_nie_oznaczany_jako_usuniety(baza, tmp_path):
    cel = tmp_path / "d"
    rng = np.random.default_rng(3)
    D.zapisz_stl(D.atrapa(rng), cel / "Cyrkon" / "Testowski 101 stary" / "zab 11.stl", TERAZ - dt.timedelta(days=11))
    D.zapisz_stl(D.atrapa(rng), cel / "Cyrkon" / "Testowski 102 prawie" / "zab 12.stl", TERAZ - dt.timedelta(days=9, hours=12))
    D.zapisz_stl(D.atrapa(rng), cel / "Cyrkon" / "Testowski 103 nowy" / "zab 14.stl", TERAZ - dt.timedelta(hours=1))
    r = I.indeksuj(baza, {"cyrkon": cel / "Cyrkon"}, TERAZ, usun_po_dniach=10)
    assert (r.nowe, r.pominiete_stare) == (2, 1)
    assert {w["kuweta"] for w in baza.wiersze("SELECT kuweta FROM zlecenia")} == {"102", "103"}
    # dzien pozniej "102" ma 10,5 dnia: nie jest indeksowany od nowa ani oznaczany jako usuniety
    r = I.indeksuj(baza, {"cyrkon": cel / "Cyrkon"}, TERAZ + dt.timedelta(days=1), usun_po_dniach=10)
    assert (r.nowe, r.zmienione, r.usuniete, r.zlecenia_usuniete, r.pominiete_stare) == (0, 0, 0, 0, 2)
    assert liczba(baza, "projekty", "usuniety = 1") == 0


def test_bledny_stl_bez_cech_ponowna_proba_i_poprawka(baza, tmp_path):
    cel = tmp_path / "d"
    rng = np.random.default_rng(4)
    D.zapisz_stl(D.atrapa(rng), cel / "Cyrkon" / "Testowski 201" / "zab 11.stl", WCZORAJ)
    zly = cel / "Cyrkon" / "Testowski 202" / "zab 12.stl"
    zly.parent.mkdir(parents=True)
    zly.write_bytes(np.random.default_rng(7).integers(0, 256, 3000, dtype=np.uint8).tobytes())
    D.ustaw_czas(zly, WCZORAJ)
    r = I.indeksuj(baza, {"cyrkon": cel / "Cyrkon"}, TERAZ)
    assert (r.nowe, r.bledy, r.cechy_policzone) == (2, 1, 1)
    p = baza.wiersz("SELECT * FROM projekty WHERE plik = 'zab 12.stl'")
    assert p["sha16"] == S.skrot_pliku(zly) and r.bledne_projekty == [p["id"]]
    assert liczba(baza, "cechy_stl", f"sha16 = '{p['sha16']}'") == 0
    r = I.indeksuj(baza, {"cyrkon": cel / "Cyrkon"}, TERAZ)  # bez cech = ponowna proba (np. plik byl zablokowany)
    assert (r.nowe, r.zmienione, r.bledy) == (0, 0, 1)
    D.zapisz_stl(D.atrapa(rng), zly, TERAZ - dt.timedelta(hours=1))
    r = I.indeksuj(baza, {"cyrkon": cel / "Cyrkon"}, TERAZ)
    assert (r.zmienione, r.bledy, r.cechy_policzone) == (1, 0, 1)


def test_plik_zablokowany_bez_skrotu_i_ponowna_proba(baza, tmp_path, monkeypatch):
    cel = tmp_path / "d"
    D.zapisz_stl(D.atrapa(np.random.default_rng(5)), cel / "Cyrkon" / "Testowski 301" / "zab 11.stl", WCZORAJ)
    oryginal = I._czytaj_plik

    def zablokowany(p):
        raise PermissionError(13, "plik zablokowany przez inny proces", str(p))

    monkeypatch.setattr(I, "_czytaj_plik", zablokowany)
    r = I.indeksuj(baza, {"cyrkon": cel / "Cyrkon"}, TERAZ)
    assert (r.nowe, r.bledy) == (1, 1)
    assert baza.wiersz("SELECT sha16 FROM projekty")["sha16"] is None
    monkeypatch.setattr(I, "_czytaj_plik", oryginal)
    r = I.indeksuj(baza, {"cyrkon": cel / "Cyrkon"}, TERAZ)
    assert (r.nowe, r.zmienione, r.bledy, r.cechy_policzone) == (0, 0, 0, 1)
    assert baza.wiersz("SELECT sha16 FROM projekty")["sha16"] is not None


def test_wielkosc_liter_pliki_inne_foldery_specjalne_i_podfoldery(baza, tmp_path):
    cel = tmp_path / "d"
    rng = np.random.default_rng(6)
    D.zapisz_stl(D.atrapa(rng), cel / "Cyrkon" / "Testowski 401" / "21.STL", WCZORAJ)
    D.zapisz_stl(D.atrapa(rng), cel / "Cyrkon" / "Testowski 402" / "22.Stl", WCZORAJ)
    (cel / "Cyrkon" / "Testowski 402" / "opis.txt").write_text("nie stl", encoding="utf-8")
    D.zapisz_stl(D.atrapa(rng), cel / "Cyrkon" / "Testowski 402" / "skany" / "23.stl", WCZORAJ)  # podfolder: nie punkt pracy
    D.zapisz_stl(D.atrapa(rng), cel / "Cyrkon" / "_pobrane" / "24.stl", WCZORAJ)
    D.zapisz_stl(D.atrapa(rng), cel / "Cyrkon" / "Testowski 403" / "~$tymczasowy.stl", WCZORAJ)
    (cel / "Cyrkon" / "luzny.stl").write_bytes(b"")  # plik w katalogu zrodla, poza folderem zlecenia
    r = I.indeksuj(baza, {"cyrkon": cel / "Cyrkon"}, TERAZ)
    assert r.nowe == 2 and r.pominiete_podfoldery == 1
    assert {w["zeby"] for w in baza.wiersze("SELECT zeby FROM projekty")} == {"21", "22"}
    assert liczba(baza, "zlecenia") == 3  # _pobrane pominiety; folder bez STL tez jest zleceniem (kuweta znana)


def test_folder_bez_kuwety_liczony_i_zapisany(baza, tmp_path):
    cel = tmp_path / "d"
    D.zapisz_stl(D.atrapa(np.random.default_rng(8)), cel / "Cyrkon" / "Testowski bez numeru" / "zab 11.stl", WCZORAJ)
    r = I.indeksuj(baza, {"cyrkon": cel / "Cyrkon"}, TERAZ)
    assert (r.nowe, r.bez_kuwety) == (1, 1)
    assert baza.wiersz("SELECT kuweta FROM zlecenia")["kuweta"] is None


def test_zmiana_nazwy_folderu_nowe_zlecenie_cechy_z_pamieci(baza, drzewo):
    cel, prawda = drzewo
    I.indeksuj(baza, zrodla(cel), TERAZ)
    z = prawda[0]
    (cel / "Cyrkon" / z.folder).rename(cel / "Cyrkon" / (z.folder + " poprawione"))
    r = I.indeksuj(baza, zrodla(cel), TERAZ)
    assert (r.zlecenia_nowe, r.zlecenia_usuniete, r.nowe, r.usuniete, r.cechy_policzone) == (1, 1, len(z.pliki), len(z.pliki), 0)


def test_bez_liczenia_cech(baza, drzewo):
    cel, prawda = drzewo
    r = I.indeksuj(baza, zrodla(cel), TERAZ, licz_cechy=False)
    assert r.nowe == sum(len(z.pliki) for z in prawda) and r.cechy_policzone == 0 and liczba(baza, "cechy_stl") == 0
    assert liczba(baza, "projekty", "sha16 IS NULL") == 0
    r = I.indeksuj(baza, zrodla(cel), TERAZ)  # pozniej z cechami: liczone dla wszystkich bez cech, bez nowych
    assert (r.nowe, r.zmienione, r.cechy_policzone) == (0, 0, sum(len(z.pliki) for z in prawda))


def test_zdarzenie_indeksu_w_dzienniku_same_liczby(baza, drzewo):
    cel, _ = drzewo
    r = I.indeksuj(baza, zrodla(cel), TERAZ)
    z = baza.wiersze("SELECT * FROM zdarzenia WHERE zrodlo = 'pula' AND typ = 'indeks'")
    assert len(z) == 1
    import json
    dane = json.loads(z[0]["dane"])
    assert dane["nowe"] == r.nowe and dane["zlecen"] == 40
    assert r.do_slownika()["nowe"] == r.nowe


def test_zrodla_z_ustawien_sciezki_wzgledne_od_katalogu_programu():
    from stanowisko import ustawienia as UST
    ust = {"sciezki": {"folder_cyrkon": "C:/OneDrive/Cyrkon", "folder_prywatne": "dane/Prywatne"}}
    z = I.zrodla_z_ustawien(ust)
    assert z["cyrkon"].as_posix() == "C:/OneDrive/Cyrkon"
    assert z["prywatne"] == UST.KORZEN / "dane" / "Prywatne"


# --- runda 2 recenzji PR #18 ------------------------------------------------------------------------------------------
def test_p1_niejednoznaczna_kuweta_w_indeksie_i_licznikach(baza, tmp_path):
    from stanowisko import pula as P
    cel = tmp_path / "d"
    rng = np.random.default_rng(11)
    D.zapisz_stl(D.atrapa(rng), cel / "Cyrkon" / "Testowski 46 3263" / "zab 11.stl", WCZORAJ)  # dwa numery
    D.zapisz_stl(D.atrapa(rng), cel / "Cyrkon" / "Probna 3263_16_11_2026" / "zab 12.stl", WCZORAJ)  # numer + data
    D.zapisz_stl(D.atrapa(rng), cel / "Cyrkon" / "Fikcyjny bez numeru" / "zab 14.stl", WCZORAJ)
    r = I.indeksuj(baza, {"cyrkon": cel / "Cyrkon"}, TERAZ, licz_cechy=False)
    assert (r.kuweta_niejednoznaczna, r.bez_kuwety) == (1, 1)
    assert sorted(w["kuweta"] or "-" for w in baza.wiersze("SELECT kuweta FROM zlecenia")) == ["-", "3263", "?46,3263"]
    p = P.pula_poranna(baza, TERAZ)
    assert (p.liczniki["kuweta_niejednoznaczna"], p.liczniki["bez_kuwety"]) == (1, 1)
    assert "Testowski" not in json.dumps(r.do_slownika()) + json.dumps(p.do_slownika())


def test_d2_pusty_katalog_zrodla_bez_oznaczania_usuniec_i_ostrzezenie(baza, drzewo, tmp_path):
    cel, prawda = drzewo
    I.indeksuj(baza, zrodla(cel), TERAZ)
    cyrkon = [z for z in prawda if z.zrodlo == "cyrkon"]
    schowek = tmp_path / "schowek"
    shutil.move(str(cel / "Cyrkon"), str(schowek))
    (cel / "Cyrkon").mkdir()  # katalog jest, ale pusty (OneDrive w trakcie synchronizacji)
    r = I.indeksuj(baza, zrodla(cel), TERAZ)
    assert r.zrodla["cyrkon"] == "ok" and (r.zlecenia_usuniete, r.usuniete) == (0, 0)
    assert r.wstrzymane_usuniecia == len(cyrkon) and len(r.ostrzezenia) == 1 and "cyrkon" in r.ostrzezenia[0]
    assert liczba(baza, "zlecenia", "usuniety = 1") == 0
    assert all(z.folder not in json.dumps(r.do_slownika()) for z in prawda)
    # wiecej niz polowa folderow naraz: tez nic; jeden z wielu: oznaczony
    (cel / "Cyrkon").rmdir()
    shutil.move(str(schowek), str(cel / "Cyrkon"))
    for z in cyrkon[: len(cyrkon) // 2 + 1]:
        shutil.move(str(cel / "Cyrkon" / z.folder), str(tmp_path / z.folder))
    r = I.indeksuj(baza, zrodla(cel), TERAZ)
    assert r.zlecenia_usuniete == 0 and r.wstrzymane_usuniecia == len(cyrkon) // 2 + 1
    for z in cyrkon[: len(cyrkon) // 2 + 1]:
        shutil.move(str(tmp_path / z.folder), str(cel / "Cyrkon" / z.folder))
    shutil.rmtree(cel / "Cyrkon" / cyrkon[0].folder)
    r = I.indeksuj(baza, zrodla(cel), TERAZ)
    assert (r.zlecenia_usuniete, r.wstrzymane_usuniecia, r.ostrzezenia) == (1, 0, [])


def test_d2_stary_folder_oznaczony_jako_usuniety_wraca_do_indeksu(baza, tmp_path):
    cel = tmp_path / "d"
    rng = np.random.default_rng(12)
    D.zapisz_stl(D.atrapa(rng), cel / "Cyrkon" / "Testowski 501" / "zab 11.stl", WCZORAJ)
    D.zapisz_stl(D.atrapa(rng), cel / "Cyrkon" / "Testowski 502" / "zab 12.stl", WCZORAJ)
    I.indeksuj(baza, {"cyrkon": cel / "Cyrkon"}, TERAZ)
    shutil.move(str(cel / "Cyrkon" / "Testowski 502"), str(tmp_path / "502"))
    r = I.indeksuj(baza, {"cyrkon": cel / "Cyrkon"}, TERAZ)
    assert (r.zlecenia_usuniete, r.usuniete) == (1, 1)
    shutil.move(str(tmp_path / "502"), str(cel / "Cyrkon" / "Testowski 502"))  # wraca po 2 tygodniach (folder ma juz > 10 dni)
    r = I.indeksuj(baza, {"cyrkon": cel / "Cyrkon"}, TERAZ + dt.timedelta(days=14))
    assert (r.stare_doindeksowane, r.zlecenia_nowe, r.pominiete_stare) == (1, 1, 1)
    assert liczba(baza, "zlecenia", "usuniety = 1") == 0 and liczba(baza, "projekty", "usuniety = 1") == 0


def test_d3_stary_folder_z_wymaganym_plikiem_doindeksowany(baza, tmp_path):
    cel = tmp_path / "d"
    rng = np.random.default_rng(13)
    D.zapisz_stl(D.atrapa(rng), cel / "Cyrkon" / "Testowski 601 stary" / "Zab 21.STL", TERAZ - dt.timedelta(days=20))
    D.zapisz_stl(D.atrapa(rng), cel / "Cyrkon" / "Testowski 602 stary" / "zab 22.stl", TERAZ - dt.timedelta(days=20))
    r = I.indeksuj(baza, {"cyrkon": cel / "Cyrkon"}, TERAZ, wymagane={"zab 21.stl"})
    assert (r.nowe, r.stare_doindeksowane, r.pominiete_stare) == (1, 1, 1)
    assert [w["kuweta"] for w in baza.wiersze("SELECT kuweta FROM zlecenia")] == ["601"]


def test_siatka_z_bajtow_jak_wczytaj_projekt(drzewo):
    cel, prawda = drzewo
    plik = next(cel.rglob("*.stl"))
    m1 = I.siatka_z_bajtow(plik.read_bytes())
    m2 = S.wczytaj_projekt(plik)
    assert isinstance(m1, trimesh.Trimesh) and len(m1.faces) == len(m2.faces)
    assert np.allclose(m1.vertices, m2.vertices)
    with pytest.raises(ValueError):
        I.siatka_z_bajtow(b"to nie jest STL")
