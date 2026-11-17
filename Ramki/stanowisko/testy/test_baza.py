"""baza.py (E3-A1): plik SQLite wg planu etapu 3, sekcja 3.4 - schemat, migracje z kopia, zrzut stanu.

Kryteria odbioru E3-A1 sprawdzane tutaj: 5 (zrzut po zamknieciu i otwarciu - poziom bazy), 7 (migracja 0 -> 1
z kopia pliku; baza nowsza niz program = odmowa) i 8 (nazwa folderu zlecenia tylko w `zlecenia` i `excel_zapisy`).
Dane w pelni sztuczne; testy pisza tylko do tmp_path.
"""
from __future__ import annotations

import sqlite3

import pytest

from stanowisko import baza as B
from stanowisko import ustawienia as UST

# Kolumny przepisane z tabeli w sekcji 3.4 planu (kolejnosc jak w planie). Zmiana schematu = migracja z opisem dla wlasciciela.
SCHEMAT_3_4 = {
    "zlecenia": ["id", "zrodlo", "folder", "folder_norm", "kuweta", "mtime", "dodano", "usuniety"],
    "projekty": ["id", "zlecenie_id", "plik", "sha16", "zeby", "typ", "mtime_ns", "rozmiar", "zaindeksowano", "usuniety"],
    "cechy_stl": ["sha16", "trojkaty", "szczelny", "objetosc_mm3", "hull_mm3", "pole_mm2", "obrys_a_mm", "obrys_b_mm", "wysokosc_mm",
                  "miniatura", "wersja_cech", "policzono"],
    "frezowania": ["id", "projekt_id", "plik_w_raporcie", "krazek", "wspolczynnik", "data", "zrodlo", "raport_plik", "wczytano"],
    "skany": ["id", "plik", "sha16", "rozmiar", "czas_pliku", "czas_analizy", "czas_s", "tryb", "uklad", "uklad_zrodlo", "uklad_zgodny",
              "numer_plytki", "numer_zrodlo", "sesja_pieca_id", "status", "zastepuje_id", "wynik_json", "wersja_programu", "skrot_ustawien"],
    "prace": ["id", "skan_id", "gniazdo", "nr_fragmentu", "status_fragmentu", "status_match", "status_inspekcji", "status_gniazda",
              "kandydat1_sha16", "kandydat1_pokrycie", "kandydat2_sha16", "kandydat2_pokrycie", "pewnosc", "frezowanie_id", "wspolczynnik",
              "korekta_skali", "ubytki", "ubytek_max_mm", "projekt_id"],
    "decyzje": ["id", "praca_id", "skan_id", "rodzaj", "wartosc", "operator", "czas"],
    "sesje_pieca": ["id", "data", "nr_w_dniu", "otwarto", "zamknieto", "zamknal"],
    "stan_punktow": ["projekt_id", "stan", "praca_id", "sesja_pieca_id", "czas"],
    "excel_zapisy": ["id", "czas", "sesja_pieca_id", "zlecenie_id", "kuweta", "folder", "numer_zlecenia_b", "arkusz", "wiersz", "regula",
                     "wynik", "tryb", "operator"],
    "zdarzenia": ["id", "czas", "zrodlo", "typ", "skan_id", "dane"],
}


def _kolumny(pol: sqlite3.Connection, tabela: str) -> list[str]:
    return [w[1] for w in pol.execute(f"PRAGMA table_info({tabela})")]


def _tabele(pol: sqlite3.Connection) -> set[str]:
    return {w[0] for w in pol.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'")}


def _wersja_pliku(plik) -> int:
    pol = sqlite3.connect(plik)
    try:
        return pol.execute("PRAGMA user_version").fetchone()[0]
    finally:
        pol.close()


@pytest.fixture
def baza(tmp_path):
    b = B.otworz(tmp_path / "dane" / "stanowisko.sqlite")
    yield b
    b.zamknij()


def _zlecenie_i_projekt(b: B.Baza, folder: str = "3263 Testowa Anna", sha16: str = "24b22d4d000947e0") -> tuple[int, int]:
    z = b.wstaw("zlecenia", zrodlo="cyrkon", folder=folder, folder_norm=folder.lower(), kuweta=folder.split()[0], usuniety=0)
    p = b.wstaw("projekty", zlecenie_id=z, plik="2026-11-16_testowa_anna-11-crown_cad.stl", sha16=sha16, zeby="11", typ="korona", usuniety=0)
    return z, p


# --- schemat ------------------------------------------------------------------------------
def test_nowa_baza_ma_schemat_z_sekcji_3_4(baza):
    assert B.WERSJA_SCHEMATU == 1 == max(B.MIGRACJE)
    assert baza.wersja() == 1 and _wersja_pliku(baza.plik) == 1
    assert baza.plik.exists() and baza.kopia_przed_migracja is None  # nowy plik: nie ma czego kopiowac
    assert _tabele(baza.polaczenie) == set(SCHEMAT_3_4) == set(B.TABELE)
    assert len(B.TABELE) == 11
    for tabela, kolumny in SCHEMAT_3_4.items():
        assert _kolumny(baza.polaczenie, tabela) == kolumny, tabela


def test_indeksy_i_unikaty_z_sekcji_3_4(baza):
    indeksy = {}
    for tabela in SCHEMAT_3_4:
        for _, nazwa, unikat, *_ in baza.polaczenie.execute(f"PRAGMA index_list({tabela})"):
            kol = tuple(w[2] for w in baza.polaczenie.execute(f"PRAGMA index_info({nazwa})"))
            indeksy.setdefault(tabela, set()).add((kol, bool(unikat)))
    assert (("zrodlo", "folder"), True) in indeksy["zlecenia"] and (("kuweta",), False) in indeksy["zlecenia"]
    assert (("zlecenie_id", "plik"), True) in indeksy["projekty"] and (("sha16",), False) in indeksy["projekty"]
    assert (("plik_w_raporcie", "krazek", "data"), True) in indeksy["frezowania"]
    assert (("skan_id", "gniazdo", "nr_fragmentu"), True) in indeksy["prace"]
    z, p = _zlecenie_i_projekt(baza)
    with pytest.raises(sqlite3.IntegrityError):
        baza.wstaw("zlecenia", zrodlo="cyrkon", folder="3263 Testowa Anna", usuniety=0)
    with pytest.raises(sqlite3.IntegrityError):
        baza.wstaw("projekty", zlecenie_id=z, plik="2026-11-16_testowa_anna-11-crown_cad.stl", sha16="ffff000000000000", usuniety=0)
    baza.wstaw("zlecenia", zrodlo="prywatne", folder="3263 Testowa Anna", usuniety=0)  # inne zrodlo: osobne zlecenie


def test_k8_nazwy_folderow_i_plikow_zlecen_tylko_w_czterech_tabelach(baza):
    """Kryterium 8 po decyzji wlasciciela 4 (17.11): nazwy folderow i plikow zlecen (dane osobowe) wolno trzymac w czterech
    tabelach; jedna stala `KOLUMNY_Z_NAZWAMI` dla testow i przyszlej kopii bazy bez nazw (D12)."""
    assert B.KOLUMNY_Z_NAZWAMI == {"zlecenia": ("folder", "folder_norm"), "projekty": ("plik",),
                                   "frezowania": ("plik_w_raporcie", "raport_plik"), "excel_zapisy": ("folder",)}
    assert B.TABELE_Z_NAZWAMI == ("zlecenia", "projekty", "frezowania", "excel_zapisy")
    for tabela, kolumny in B.KOLUMNY_Z_NAZWAMI.items():
        assert set(kolumny) <= set(_kolumny(baza.polaczenie, tabela)), tabela
    z_folderem = {t for t in B.TABELE if any("folder" in k for k in _kolumny(baza.polaczenie, t))}
    assert z_folderem == {"zlecenia", "excel_zapisy"}
    # poza czterema tabelami: zadnej kolumny na nazwe zlecenia / pacjenta; jedyny "plik" to plik skanu ze skanera (`skany.plik`)
    for t in set(B.TABELE) - set(B.TABELE_Z_NAZWAMI):
        kolumny = _kolumny(baza.polaczenie, t)
        assert not [k for k in kolumny if k in ("nazwa", "nazwisko", "pacjent", "zlecenie", "sciezka")], t
        assert [k for k in kolumny if "plik" in k] == (["plik", "czas_pliku"] if t == "skany" else []), t
    # zrzut bez nazw: kolumny z nazwami puste, reszta bez zmian
    z, p = _zlecenie_i_projekt(baza)
    baza.wstaw("frezowania", projekt_id=p, plik_w_raporcie="2026-11-16_testowa_anna-11-crown_cad.stl", krazek="K-1101", data="2026-11-17",
               raport_plik="raport_testowa.html")
    baza.wstaw("excel_zapisy", zlecenie_id=z, kuweta="3263", folder="3263 Testowa Anna", wynik="tylko_log")
    pelny, bez = baza.zrzut(), baza.zrzut(bez_nazw=True)
    assert pelny["zlecenia"][0]["folder"] == "3263 Testowa Anna" and pelny["projekty"][0]["plik"].startswith("2026-11-16_testowa")
    assert "testowa" not in repr(bez).lower() and "anna" not in repr(bez).lower()
    assert (bez["zlecenia"][0]["folder"], bez["zlecenia"][0]["kuweta"], bez["projekty"][0]["sha16"], bez["frezowania"][0]["krazek"],
            bez["excel_zapisy"][0]["kuweta"]) == (None, "3263", "24b22d4d000947e0", "K-1101", "3263")


def test_statusy_sa_tekstem_bez_listy_zamknietej(baza):
    """Zasada 2 sekcji 3.4: nowy status (P2 dodal "nie_sprawdzono", kolejne paczki dodadza nastepne) nie wymaga migracji."""
    s = baza.wstaw("skany", plik="skan_x.stl", sha16="00aa00aa00aa00aa", status="status_ktorego_dzis_nie_ma", tryb="wieczor")
    p = baza.wstaw("prace", skan_id=s, gniazdo=4, nr_fragmentu=1, status_match="zielony", status_inspekcji="nowy_status_b4",
                   status_gniazda="fioletowy")
    assert baza.wiersz("SELECT status_inspekcji, status_gniazda FROM prace WHERE id = ?", (p,)) == {
        "status_inspekcji": "nowy_status_b4", "status_gniazda": "fioletowy"}
    assert baza.wiersz("SELECT status FROM skany WHERE id = ?", (s,))["status"] == "status_ktorego_dzis_nie_ma"


def test_klucze_obce_sa_pilnowane(baza):
    with pytest.raises(sqlite3.IntegrityError):
        baza.wstaw("prace", skan_id=999, gniazdo=1, nr_fragmentu=1)
    with pytest.raises(sqlite3.IntegrityError):
        baza.wstaw("projekty", zlecenie_id=999, plik="a.stl", sha16="00aa00aa00aa00aa", usuniety=0)
    s = baza.wstaw("skany", plik="skan_x.stl", status="przyjety")
    baza.wstaw("prace", skan_id=s, gniazdo=1, nr_fragmentu=1)
    with pytest.raises(sqlite3.IntegrityError):
        baza.wstaw("prace", skan_id=s, gniazdo=1, nr_fragmentu=1)  # unikat (skan, gniazdo, fragment)
    baza.wstaw("prace", skan_id=s, gniazdo=1, nr_fragmentu=2)  # druga praca w tym samym gniezdzie


def test_decyzje_i_zdarzenia_tylko_dopisywanie(baza):
    s = baza.wstaw("skany", plik="skan_x.stl", status="przyjety")
    d = baza.wstaw("decyzje", skan_id=s, rodzaj="powtorz_skan", czas="2026-11-17T19:00:00")
    z = baza.zdarzenie("system", "proba", {"liczba": 3}, skan_id=s)
    for sql in ("UPDATE decyzje SET rodzaj = 'ok' WHERE id = ?", "DELETE FROM decyzje WHERE id = ?"):
        with pytest.raises(sqlite3.DatabaseError, match="tylko dopisywanie"):
            baza.wykonaj(sql, (d,))
    for sql in ("UPDATE zdarzenia SET typ = 'inny' WHERE id = ?", "DELETE FROM zdarzenia WHERE id = ?"):
        with pytest.raises(sqlite3.DatabaseError, match="tylko dopisywanie"):
            baza.wykonaj(sql, (z,))
    assert baza.wiersz("SELECT rodzaj FROM decyzje WHERE id = ?", (d,))["rodzaj"] == "powtorz_skan"
    zd = baza.wiersz("SELECT * FROM zdarzenia WHERE id = ?", (z,))
    assert (zd["zrodlo"], zd["typ"], zd["skan_id"], zd["dane"]) == ("system", "proba", s, '{"liczba": 3}') and zd["czas"]


def test_wstaw_odrzuca_nieznana_tabele_i_kolumne(baza):
    with pytest.raises(B.BladBazy, match="nieznana tabela"):
        baza.wstaw("sqlite_master", name="x")
    with pytest.raises(B.BladBazy, match=r"skany: nieznana kolumna.*folder"):
        baza.wstaw("skany", plik="skan_x.stl", status="przyjety", folder="3263 Testowa Anna")


def test_transakcja_wycofuje_calosc_po_bledzie(baza):
    with pytest.raises(sqlite3.IntegrityError):
        with baza.transakcja():
            s = baza.wstaw("skany", plik="skan_x.stl", status="przyjety")
            baza.wstaw("prace", skan_id=s, gniazdo=1, nr_fragmentu=1)
            baza.wstaw("prace", skan_id=s, gniazdo=1, nr_fragmentu=1)
    assert baza.wiersz("SELECT count(*) AS n FROM skany")["n"] == 0 and baza.wiersz("SELECT count(*) AS n FROM prace")["n"] == 0
    with baza.transakcja():
        with baza.transakcja():  # zagniezdzenie: jedna transakcja
            baza.wstaw("skany", plik="skan_y.stl", status="przyjety")
    assert baza.wiersz("SELECT count(*) AS n FROM skany")["n"] == 1


# --- kryterium 5: stan po zamknieciu i otwarciu -----------------------------------------------
def test_k5_zrzut_po_zamknieciu_i_otwarciu_jest_identyczny(tmp_path):
    plik = tmp_path / "stanowisko.sqlite"
    b = B.otworz(plik)
    z, p = _zlecenie_i_projekt(b)
    b.wstaw("cechy_stl", sha16="24b22d4d000947e0", trojkaty=1200, szczelny=1, objetosc_mm3=310.5, miniatura=b"\x89PNG\x00\x01", wersja_cech=1)
    f = b.wstaw("frezowania", projekt_id=p, plik_w_raporcie="2026-11-16_testowa_anna-11-crown_cad.stl", krazek="K-1101", wspolczynnik=1.2251,
                data="2026-11-17", zrodlo="csv")
    s = b.wstaw("skany", plik="skan_x.stl", sha16="00aa00aa00aa00aa", rozmiar=48000000, tryb="wieczor", uklad="wieczorna", uklad_zgodny=1,
                numer_plytki=1, numer_zrodlo="podany", status="przyjety", czas_pliku="2026-11-17T19:02:11")
    pr = b.wstaw("prace", skan_id=s, gniazdo=2, nr_fragmentu=1, status_match="zielony", status_inspekcji="ubytek", status_gniazda="czerwony",
                 kandydat1_sha16="24b22d4d000947e0", kandydat1_pokrycie=0.91, pewnosc=0.75, frezowanie_id=f, ubytki=1, ubytek_max_mm=0.62, projekt_id=p)
    b.wstaw("decyzje", praca_id=pr, rodzaj="ukruszona", operator="Technik A", czas="2026-11-17T19:05:00")
    b.wstaw("stan_punktow", projekt_id=p, stan="do_dofrezowania", praca_id=pr, czas="2026-11-17T19:05:00")
    b.zdarzenie("silnik", "skan_przyjety", {"prace": 1}, skan_id=s)
    przed = b.zrzut()
    assert set(przed) == set(B.TABELE)
    assert [len(przed[t]) for t in ("zlecenia", "projekty", "cechy_stl", "frezowania", "skany", "prace", "decyzje", "stan_punktow", "zdarzenia")] == [1] * 9
    assert przed["cechy_stl"][0]["miniatura"] == b"\x89PNG\x00\x01" and przed["prace"][0]["ubytek_max_mm"] == 0.62
    b.zamknij()
    b2 = B.otworz(plik)
    assert b2.kopia_przed_migracja is None  # ta sama wersja: bez migracji i bez kopii
    assert b2.zrzut() == przed
    assert b2.zrzut(["decyzje"]) == {"decyzje": przed["decyzje"]}
    b2.zamknij()
    assert sorted(x.name for x in tmp_path.iterdir()) == ["stanowisko.sqlite"]  # zadnych plikow obok bazy


# --- kryterium 7: migracje --------------------------------------------------------------------
def test_k7_migracja_0_do_1_robi_kopie_pliku(tmp_path):
    plik = tmp_path / "stanowisko.sqlite"
    pol = sqlite3.connect(plik)  # plik bazy w wersji 0 (sprzed programu), z danymi, ktore maja przetrwac
    pol.execute("CREATE TABLE notatka (tresc TEXT)")
    pol.execute("INSERT INTO notatka VALUES ('sprzed migracji')")
    pol.commit()
    pol.close()
    assert _wersja_pliku(plik) == 0
    przed = plik.read_bytes()
    b = B.otworz(plik)
    try:
        assert b.wersja() == 1 and b.zmigrowano == (0, 1)
        kopia = b.kopia_przed_migracja
        assert kopia is not None and kopia.parent == plik.parent and kopia != plik
        assert "kopia_v0" in kopia.name and kopia.suffix == ".sqlite"  # *.sqlite jest w .gitignore
        assert kopia.read_bytes() == przed and _wersja_pliku(kopia) == 0
        assert set(SCHEMAT_3_4) <= _tabele(b.polaczenie)
        assert b.wiersz("SELECT tresc FROM notatka")["tresc"] == "sprzed migracji"
        zd = b.wiersze("SELECT zrodlo, typ, dane FROM zdarzenia")
        assert len(zd) == 1 and (zd[0]["zrodlo"], zd[0]["typ"]) == ("system", "migracja") and kopia.name in zd[0]["dane"]
    finally:
        b.zamknij()
    b2 = B.otworz(plik)  # drugie otwarcie: nic do migracji, nowej kopii nie ma
    assert b2.kopia_przed_migracja is None and b2.zmigrowano is None
    b2.zamknij()
    assert len(list(tmp_path.glob("*kopia*"))) == 1


def test_k7_migracje_ida_w_przod_wersja_po_wersji(tmp_path, monkeypatch):
    plik = tmp_path / "stanowisko.sqlite"
    b = B.otworz(plik)
    b.wstaw("skany", plik="skan_x.stl", status="przyjety")
    b.zamknij()
    monkeypatch.setitem(B.MIGRACJE, 2, ("ALTER TABLE zdarzenia ADD COLUMN probna TEXT",))
    monkeypatch.setitem(B.MIGRACJE, 3, ("CREATE TABLE probna_tabela (a INTEGER)", "INSERT INTO probna_tabela VALUES (7)"))
    b = B.otworz(plik)
    try:
        assert b.wersja() == 3 and b.zmigrowano == (1, 3)
        assert "kopia_v1" in b.kopia_przed_migracja.name and _wersja_pliku(b.kopia_przed_migracja) == 1
        assert "probna" in _kolumny(b.polaczenie, "zdarzenia") and b.wiersz("SELECT a FROM probna_tabela")["a"] == 7
        assert b.wiersz("SELECT count(*) AS n FROM skany")["n"] == 1  # dane zostaly
    finally:
        b.zamknij()


def test_k7_baza_nowsza_niz_program_odmowa(tmp_path):
    plik = tmp_path / "stanowisko.sqlite"
    B.otworz(plik).zamknij()
    pol = sqlite3.connect(plik)
    pol.execute("PRAGMA user_version = 7")
    pol.close()
    przed = plik.read_bytes()
    with pytest.raises(B.BladBazy, match=r"stanowisko\.sqlite.*wersji 7.*obsluguje.*1.*zaktualizuj program"):
        B.otworz(plik)
    assert plik.read_bytes() == przed and _wersja_pliku(plik) == 7  # pliku nie ruszono
    assert sorted(x.name for x in tmp_path.iterdir()) == ["stanowisko.sqlite"]  # bez kopii i bez plikow tymczasowych


def test_k7_nieudana_migracja_zostawia_baze_w_starej_wersji(tmp_path, monkeypatch):
    plik = tmp_path / "stanowisko.sqlite"
    B.otworz(plik).zamknij()
    monkeypatch.setitem(B.MIGRACJE, 2, ("CREATE TABLE probna_tabela (a INTEGER)", "TO NIE JEST POLECENIE SQL"))
    with pytest.raises(B.BladBazy, match=r"migracja do wersji 2 nie powiodla sie.*kopia"):
        B.otworz(plik)
    assert _wersja_pliku(plik) == 1
    pol = sqlite3.connect(plik)
    assert "probna_tabela" not in _tabele(pol)  # migracja jest jedna transakcja: albo cala, albo wcale
    pol.close()
    assert len(list(tmp_path.glob("*kopia_v1*"))) == 1


def test_plik_ktory_nie_jest_baza(tmp_path):
    plik = tmp_path / "stanowisko.sqlite"
    plik.write_bytes(b"to nie jest plik SQLite, tylko tekst" * 40)
    with pytest.raises(B.BladBazy, match=r"stanowisko\.sqlite.*nie jest baza SQLite"):
        B.otworz(plik)
    assert plik.read_bytes().startswith(b"to nie jest plik SQLite")


# --- kopia, odczyt, sciezka ---------------------------------------------------------------------
def test_kopia_bazy_na_zyczenie(baza, tmp_path):
    baza.wstaw("skany", plik="skan_x.stl", status="przyjety")
    cel = baza.kopia(tmp_path / "kopie" / "kopia_reczna.sqlite")
    assert cel.exists() and _wersja_pliku(cel) == 1
    k = B.otworz(cel, tylko_odczyt=True)
    assert k.zrzut() == baza.zrzut()
    k.zamknij()
    with pytest.raises(B.BladBazy, match="juz istnieje"):
        baza.kopia(cel)


def test_otwarcie_tylko_do_odczytu(tmp_path):
    plik = tmp_path / "stanowisko.sqlite"
    with pytest.raises(B.BladBazy, match="brak pliku bazy"):
        B.otworz(plik, tylko_odczyt=True)
    assert not plik.exists()
    b = B.otworz(plik)
    b.wstaw("skany", plik="skan_x.stl", status="przyjety")
    b.zamknij()
    o = B.otworz(plik, tylko_odczyt=True)
    assert o.wiersz("SELECT count(*) AS n FROM skany")["n"] == 1
    with pytest.raises(sqlite3.OperationalError):
        o.wstaw("skany", plik="skan_y.stl", status="przyjety")
    o.zamknij()
    pol = sqlite3.connect(plik)
    pol.execute("PRAGMA user_version = 0")
    pol.close()
    with pytest.raises(B.BladBazy, match="wymaga migracji"):  # odczyt nie migruje
        B.otworz(plik, tylko_odczyt=True)


def test_sciezka_bazy_z_ustawien(tmp_path):
    assert B.sciezka_bazy({"sciezki": {"baza": "dane/stanowisko.sqlite"}}) == UST.KORZEN / "dane" / "stanowisko.sqlite"
    bezwzgledna = (tmp_path / "x" / "baza.sqlite").as_posix()
    assert B.sciezka_bazy({"sciezki": {"baza": bezwzgledna}}) == tmp_path / "x" / "baza.sqlite"
    assert B.sciezka_bazy(UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU)).name == "stanowisko.sqlite"


def test_modul_bazy_tylko_biblioteka_standardowa():
    """Baza nie moze wciagac numpy / Open3D / Qt (proces okna, narzedzia, raport metryk)."""
    import ast
    from pathlib import Path

    drzewo = ast.parse(Path(B.__file__).read_text(encoding="utf-8"))
    importy = {a.name.split(".")[0] for w in ast.walk(drzewo) if isinstance(w, ast.Import) for a in w.names}
    importy |= {w.module.split(".")[0] for w in ast.walk(drzewo) if isinstance(w, ast.ImportFrom) and w.level == 0 and w.module}
    assert importy <= {"__future__", "contextlib", "datetime", "filecmp", "json", "pathlib", "re", "shutil", "sqlite3", "typing"}, importy


# --- runda 2 (recenzja PR #16): P1 - schemat a sekcja 3.4 ------------------------------------------
# Ograniczenia, ktorych sekcja 3.4 planu nie podaje, a schemat je ma (kazde z uzasadnieniem w `baza.OGRANICZENIA_PONAD_3_4`
# i w `opisy_modulow/baza.md`). Dopisanie nowego wymaga zmiany tej listy - czyli swiadomej decyzji.
NOT_NULL_PONAD_3_4 = {
    "zlecenia": ["zrodlo", "folder", "usuniety"],
    "projekty": ["zlecenie_id", "plik", "usuniety"],
    "skany": ["status"],
    "prace": ["skan_id", "nr_fragmentu"],
    "decyzje": ["rodzaj", "czas"],
    "stan_punktow": ["stan"],
    "zdarzenia": ["czas", "zrodlo", "typ"],
}
DOMYSLNE_PONAD_3_4 = {("zlecenia", "usuniety"): "0", ("projekty", "usuniety"): "0"}


def test_p1_ograniczenia_ponad_sekcje_3_4_to_dokladnie_lista_z_opisu(baza):
    not_null, domyslne = {}, {}
    for tabela in B.TABELE:
        for _, kolumna, _typ, wymagana, domyslna, _pk in baza.polaczenie.execute(f"PRAGMA table_info({tabela})"):
            if wymagana:
                not_null.setdefault(tabela, []).append(kolumna)
            if domyslna is not None:
                domyslne[(tabela, kolumna)] = domyslna
    assert not_null == NOT_NULL_PONAD_3_4 and sum(len(k) for k in not_null.values()) == 15
    assert domyslne == DOMYSLNE_PONAD_3_4
    assert "frezowania" not in not_null and "sha16" not in not_null["projekty"]  # nic, co blokowaloby zapis przewidziany planem (K7, A4)
    opisane = {f"{t}.{k}" for t, kolumny in NOT_NULL_PONAD_3_4.items() for k in kolumny}
    assert set(B.OGRANICZENIA_PONAD_3_4) == opisane and all(len(u) > 20 for u in B.OGRANICZENIA_PONAD_3_4.values())  # kazde z uzasadnieniem
    wyzwalacze = [w[0] for w in baza.polaczenie.execute("SELECT name FROM sqlite_master WHERE type = 'trigger' ORDER BY name")]
    assert wyzwalacze == ["decyzje_bez_usuwania", "decyzje_bez_zmiany", "zdarzenia_bez_usuwania", "zdarzenia_bez_zmiany"]


def test_p1_wpis_reczny_wspolczynnika_na_krazek_bez_pliku_i_daty(baza):
    """K7: wspolczynnik wpisany recznie raz na krazek to wiersz `frezowania` bez pliku STL (i bez daty); `zrodlo` = reczny."""
    f = baza.wstaw("frezowania", krazek="K-2001", wspolczynnik=1.2244, zrodlo="reczny", wczytano="2026-11-17T15:00:00")
    w = baza.wiersz("SELECT * FROM frezowania WHERE id = ?", (f,))
    assert (w["projekt_id"], w["plik_w_raporcie"], w["data"], w["raport_plik"], w["krazek"], w["zrodlo"]) == (None, None, None, None, "K-2001", "reczny")
    baza.wstaw("frezowania", krazek="K-2001", wspolczynnik=1.2244, data="2026-11-17", zrodlo="reczny")  # z data, bez pliku
    baza.wstaw("frezowania", wspolczynnik=1.22, zrodlo="reczny")  # nawet bez krazka (raport bez identyfikatora krazka)
    # unikat (plik_w_raporcie, krazek, data) dziala tylko dla wierszy z wszystkimi trzema wartosciami: w SQLite pusta wartosc
    # (NULL) jest rozna od kazdej innej, wiec drugi identyczny wpis reczny NIE jest odrzucany - pilnuje tego piszacy (A4)
    baza.wstaw("frezowania", krazek="K-2001", wspolczynnik=1.2250, zrodlo="reczny")
    assert baza.wiersz("SELECT count(*) AS n FROM frezowania WHERE krazek = 'K-2001' AND plik_w_raporcie IS NULL AND data IS NULL")["n"] == 2
    baza.wstaw("frezowania", plik_w_raporcie="a-11-crown_cad.stl", krazek="K-2001", data="2026-11-17")
    with pytest.raises(sqlite3.IntegrityError):
        baza.wstaw("frezowania", plik_w_raporcie="a-11-crown_cad.stl", krazek="K-2001", data="2026-11-17")
    # punkt pracy zaindeksowany, zanim dalo sie policzyc skrot pliku (plik chwilowo niedostepny): bez sha16
    z = baza.wstaw("zlecenia", zrodlo="cyrkon", folder="3301 Przykladowy Jan")
    p = baza.wstaw("projekty", zlecenie_id=z, plik="2026-11-16_przykladowy_jan-36-crown_cad.stl")
    assert baza.wiersz("SELECT sha16, usuniety FROM projekty WHERE id = ?", (p,)) == {"sha16": None, "usuniety": 0}


# --- runda 2: uwagi drobne D1, D2 -------------------------------------------------------------------
def test_d1_baza_zajeta_przez_inny_proces_daje_czytelny_komunikat(tmp_path):
    plik = tmp_path / "stanowisko.sqlite"
    b = B.otworz(plik, czekaj_ms=150)
    obcy = sqlite3.connect(plik, isolation_level=None)  # drugi program trzyma blokade zapisu
    try:
        obcy.execute("BEGIN IMMEDIATE")
        with pytest.raises(B.BladBazy, match=r"stanowisko\.sqlite.*zajeta przez inny program.*niczego nie zapisano"):
            with b.transakcja():
                b.wstaw("skany", plik="skan_x.stl", status="przyjety")
        assert not b.polaczenie.in_transaction
        with pytest.raises(B.BladBazy, match="zajeta przez inny program"):
            b.wstaw("skany", plik="skan_x.stl", status="przyjety")  # takze pojedynczy zapis poza transakcja
        assert b.wiersz("SELECT count(*) AS n FROM skany")["n"] == 0  # odczyt w czasie cudzej transakcji dziala
        obcy.execute("ROLLBACK")
        with b.transakcja():  # po zwolnieniu blokady ta sama operacja przechodzi
            b.wstaw("skany", plik="skan_x.stl", status="przyjety")
        assert b.wiersz("SELECT count(*) AS n FROM skany")["n"] == 1
    finally:
        obcy.close()
        b.zamknij()


def test_d2_kolejne_nieudane_migracje_nie_mnoza_kopii_pliku(tmp_path, monkeypatch):
    plik = tmp_path / "stanowisko.sqlite"
    b = B.otworz(plik)
    b.wstaw("skany", plik="skan_x.stl", status="przyjety")
    b.zamknij()
    monkeypatch.setitem(B.MIGRACJE, 2, ("CREATE TABLE probna_tabela (a INTEGER)", "TO NIE JEST POLECENIE SQL"))
    for _ in range(3):  # trzy uruchomienia programu z migracja, ktora sie nie udaje
        with pytest.raises(B.BladBazy, match="migracja do wersji 2 nie powiodla sie"):
            B.otworz(plik)
    kopie = list(tmp_path.glob("*kopia_v1*"))
    assert len(kopie) == 1 and kopie[0].read_bytes() == plik.read_bytes() and _wersja_pliku(plik) == 1
    pol = sqlite3.connect(plik)  # baza zmienila sie miedzy probami: nowa kopia (stara zostaje)
    pol.execute("INSERT INTO skany (plik, status) VALUES ('skan_y.stl', 'przyjety')")
    pol.commit()
    pol.close()
    with pytest.raises(B.BladBazy):
        B.otworz(plik)
    assert len(list(tmp_path.glob("*kopia_v1*"))) == 2


# --- runda 3 (recenzja przyrostowa PR #16): D5 - sciezki w tekstach -------------------------------------
@pytest.mark.parametrize("tekst,oczekiwane", [
    # sciezki bezwzgledne: dysk, zasob sieciowy w obu zapisach, zmienne srodowiskowe, katalog domowy
    ("brak pliku C:\\Cyrkon\\9911 Zmyslony Nazwiskowski\\a.stl - pomijam", "brak pliku <sciezka>"),
    ("zasob \\\\serwer\\Cyrkon\\9911 Zmyslony\\a.stl", "zasob <sciezka>"),
    ("zasob //serwer/Cyrkon/9911 Zmyslony Nazwiskowski/a.stl niedostepny", "zasob <sciezka>"),
    ("%USERPROFILE%\\OneDrive\\Cyrkon\\9911 Zmyslony Nazwiskowski", "<sciezka>"),
    ("kopia do $HOME/Cyrkon/9911 x/a.stl oraz ~/Cyrkon/9911 y", "kopia do <sciezka>"),
    # sciezka w cudzyslowie albo apostrofach konczy sie na zamykajacym znaku; apostrof w nazwie folderu nie wypuszcza reszty
    ("[Errno 2] No such file or directory: 'C:\\\\Cyrkon\\\\9911 Zmyslony\\\\a.stl'", "[Errno 2] No such file or directory: '<sciezka>'"),
    ('plik "C:\\Cyrkon\\9911 O\'Nazwiskowski\\a.stl" uszkodzony', 'plik "<sciezka>" uszkodzony'),
    ("plik 'C:\\Cyrkon\\9911 O'Nazwiskowski\\a.stl' uszkodzony", "plik '<sciezka>'<sciezka>' uszkodzony"),
    # sciezki wzgledne z separatorem: od poprzedniego ogranicznika (dwukropek, przecinek, nawias, cudzyslow) albo od poczatku wiersza
    ("blad: Cyrkon\\9911 Zmyslony Nazwiskowski\\a.stl", "blad: <sciezka>"),
    ("brak pliku 9911 Zmyslony Nazwiskowski\\a.stl - pomijam", "<sciezka>"),
    ("otwieram '9911 Zmyslony Nazwiskowski\\a.stl' do odczytu", "otwieram '<sciezka>' do odczytu"),
    ("zapis dane/wyniki/9911 Zmyslony/a.json gotowy", "<sciezka>"),
    ("wczytano (Cyrkon/9911 Zmyslony Nazwiskowski/a.stl)", "wczytano (<sciezka>"),
    ("lista, 9911 Zmyslony Nazwiskowski/a.stl", "lista, <sciezka>"),
    ("wiersz 1 bez sciezki\nblad: x\\y\\z.stl\nwiersz 3", "wiersz 1 bez sciezki\nblad: <sciezka>\nwiersz 3"),
    # runda 4 (D3): w apostrofach / cudzyslowie separator wystarczy (takze sciezka wzgledna bez rozszerzenia); folder z ukosnikiem
    # na koncu; sciezka od \ albo / na poczatku slowa; nazwa pliku z rozszerzeniem po ukosniku
    ("KeyError: 'Cyrkon/9911 Zmyslony Nazwiskowski'", "KeyError: '<sciezka>'"),
    ('NotADirectoryError: "Cyrkon\\9911 Zmyslony" (folder)', 'NotADirectoryError: "<sciezka>" (folder)'),
    ("brak folderu Cyrkon/9911 Zmyslony Nazwiskowski/ - pomijam", "<sciezka>"),
    ("brak pliku \\Cyrkon\\9911 Zmyslony Nazwiskowski\\a.stl", "brak pliku <sciezka>"),
    ("brak pliku /9911_Zmyslony_Nazwiskowski.stl", "brak pliku <sciezka>"),
    ("zakres 0.91/0.95, plik: 9911 Zmyslony Nazwiskowski/2026-11-16_zmyslony-11-crown_cad.stl", "zakres 0.91/0.95, plik: <sciezka>"),
])
def test_d5r3_bez_sciezek_wycina_sciezki_bezwzgledne_i_wzgledne(tekst, oczekiwane):
    wynik = B.bez_sciezek(tekst)
    assert wynik == oczekiwane
    assert "Zmyslony" not in wynik and "Nazwiskowski" not in wynik and "9911" not in wynik
    assert B.bez_sciezek(wynik) == wynik  # powtorne czyszczenie nic nie zmienia


@pytest.mark.parametrize("tekst", [
    "pokrycie 0.91 / pewnosc 0.75; A/B; 19:02:11; skala: -0.4 %",
    "korony 3/5, tempo 12 km/h, zakres 0.91/0.95, data 17/11, typ N/A",
    "blad inspekcji: ValueError: za malo punktow (inspect.py:120 sprawdz)",
    "dolki kodu poza skanem (3 z 3 niewidocznych) - podaj numer plytki (--numer)",
    "plytka wieczorna, kwadratowa, nowy uklad gniazd (R59); rozstaw stozkow pasuje do ukladu: wieczorna_r54",
    "filar 1: sprawdzono 69% linii brzegu, najdluzszy odcinek bez sprawdzenia 6.7 mm",
    "<sciezka>",
    # runda 4 (D3): przyklady recenzenta rundy 3 - zwykly tekst z ukosnikami (daty, ulamki, a/b/c, zwrot z nazwa pliku) zostaje
    "pas 0.15 / 0.20 mm",
    "pas 0.15/0.20 mm, prog 0.25 mm",
    "pokrycie 0.85 < 0.9: popraw ulozenie / skan ponownie, ubytki nieliczone",
    "skala o 0.50 % - sprawdz wspolczynnik / krazek",
    "filar 2: sprawdzono 61% linii brzegu, najdluzszy odcinek bez sprawdzenia 1.4 mm",
    "ValueError: shape (3,)/(4,) mismatch",
    "Uwaga: skan z 17/11/2026 ma drgniecie",
    "skan z 17/11/2026 godz. 18:05 - drgniecie",
    "2026/11/17 18:05 skan",
    "korony 3/5 i 4/5 gotowe",
    "data 17/11 i 18/11",
    "wartosci 1/2/3 mm",
    "statusy zielony/zolty/czerwony: 3/4/1",
    "tryb linia/plaszczyzna wg ustawienia.toml",
    "patrz https://example.org/a/b",
    "tempo 12 km/h, zakres 0.91/0.95 i 0.85/0.90 wg ustawienia.toml",
    "data 17/11/2026, korony 3/5 i 4/5, statusy 3/4/1",
])
def test_d5r3_bez_sciezek_nie_rusza_zwyklych_tekstow(tekst):
    assert B.bez_sciezek(tekst) == tekst


def test_d5r3_znana_granica_sama_nazwa_bez_separatora():
    """Nazwa folderu albo pliku zlecenia podana bez separatora sciezki NIE jest rozpoznawana - to wymaganie dla wywolujacego
    (A2 / A3: w tekstach przekazywanych do `session` i do dziennika nie podawac nazw zlecen)."""
    tekst = "KeyError: '9911 Zmyslony Nazwiskowski'; plik 2026-11-16_nazwiskowski-11-crown_cad.stl"
    assert B.bez_sciezek(tekst) == tekst
