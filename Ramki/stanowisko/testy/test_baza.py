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


def test_k8_nazwa_folderu_tylko_w_zlecenia_i_excel_zapisy(baza):
    """Kryterium 8: kolumny z nazwa folderu zlecenia (dane osobowe) ma tylko `zlecenia` i `excel_zapisy`."""
    assert set(B.TABELE_Z_NAZWA_FOLDERU) == {"zlecenia", "excel_zapisy"}
    z_folderem = {t for t in B.TABELE if any("folder" in k for k in _kolumny(baza.polaczenie, t))}
    assert z_folderem == {"zlecenia", "excel_zapisy"}
    assert [k for k in _kolumny(baza.polaczenie, "zlecenia") if "folder" in k] == ["folder", "folder_norm"]
    assert [k for k in _kolumny(baza.polaczenie, "excel_zapisy") if "folder" in k] == ["folder"]
    # zadna inna tabela nie ma kolumny, ktora z nazwy mialaby trzymac nazwe zlecenia / pacjenta
    for t in set(B.TABELE) - {"zlecenia", "excel_zapisy"}:
        assert not [k for k in _kolumny(baza.polaczenie, t) if k in ("nazwa", "nazwisko", "pacjent", "zlecenie", "sciezka")], t


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
    assert importy <= {"__future__", "contextlib", "datetime", "json", "pathlib", "shutil", "sqlite3", "typing"}, importy
