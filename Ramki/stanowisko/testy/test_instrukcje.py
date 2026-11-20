"""test_instrukcje - instrukcje dla technika i zestaw proby T14 zgodne z programem (paczka E3-A11d).

Umowa zapisu instrukcji (``narzedzia/instrukcje_html.py``): tekst w cudzyslowie prostym to DOSLOWNY napis programu,
tekst w odwrotnych apostrofach to nazwa pliku albo wiersz z okna polecen. Testy:
  (1) kazdy cytat istnieje w kodzie programu, a zmiana napisu w programie jest wykrywana (napisy kluczowe sa porownywane
      wprost ze stalymi ``statusy`` / ``napisy``),
  (2) tabela "co robic, gdy nie dziala" ma wiersz na kazda sytuacje ze zlecenia; samokontrola wg umowy E3-A11s,
  (3) kazdy obrazek wskazany w instrukcji jest na liscie skryptu zrzutow i jest wpisany w strone do druku,
  (4) strony do druku sa aktualne (ten sam wynik skladania), pliki sa w ASCII z koncami linii LF,
  (5) objetosc jednej strony (liczba slow i obrazkow nie wieksza niz zmierzona przy druku na jedna strone A4),
  (6) scenariusz proby T14: dane zgodne z atrapa kontrolera i arkuszem obserwacji; przebieg 11 zadan na oknie programu
      bez ekranu (``symulator_t14.py --sprawdz`` w osobnym procesie).
Testy niczego nie zapisuja poza ``tmp_path`` i nie uzywaja internetu.
"""
from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

STANOWISKO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STANOWISKO / "narzedzia"))

import instrukcje_html as H  # noqa: E402
import zrzuty_instrukcji as Z  # noqa: E402 - bez Qt na poziomie modulu

INSTRUKCJE = ("wieczor", "poranek", "co_robic_gdy_nie_dziala")
DOKUMENTY = INSTRUKCJE + ("t14_jedna_strona", "t14_arkusz_obserwacji")
T14 = H.T14
NAZWY_Z_UMOWY = ("Stanowisko.cmd", "Samokontrola.cmd", "Wroc_do_poprzedniej.cmd")  # zlecenie E3-A11i: pliki w katalogu programu
# zlecenie E3-A11s, sekcja "Umowa": poziomy wierszy i ostatni wiersz samokontroli
SAMOKONTROLA_Z_UMOWY = ("OK", "OSTRZEZENIE", "BLAD", "SAMOKONTROLA: ZIELONA", "SAMOKONTROLA: CZERWONA")
# liczba slow (bez obrazkow i wierszy ukladu strony) i obrazkow, przy ktorych druk z .html dal 1 strone A4 (20.11.2026,
# Chrome bez okna, ``instrukcje_html.py --pdf``); wiecej tresci = trzeba zmierzyc druk ponownie i podniesc limit swiadomie
LIMITY_STRONY = {"wieczor": (535, 5), "poranek": (535, 4), "co_robic_gdy_nie_dziala": (1000, 0), "t14_jedna_strona": (230, 4),
                 "t14_arkusz_obserwacji": (450, 0)}
MIN_CYTATOW = {"wieczor": 25, "poranek": 25, "co_robic_gdy_nie_dziala": 40, "t14_jedna_strona": 12, "t14_arkusz_obserwacji": 2}
KOD_ZNIKNIECIA_PROCESU = 0xC0000142  # znane zjawisko PC (raporty/E3-A2p_2026-11-18.md): proces potomny nie startuje


def md(nazwa: str) -> str:
    return H.DOKUMENTY[nazwa][0].read_text(encoding="ascii")


@pytest.fixture(scope="module")
def indeks() -> H.Indeks:
    return H.Indeks()


# ----------------------------------------------------------------------------
# (1) cytaty = napisy programu
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("nazwa", DOKUMENTY)
def test_kazdy_cytat_istnieje_w_programie(nazwa, indeks):
    cytaty = H.cytaty(md(nazwa))
    brak = [c for c in cytaty if indeks.znajdz(c) is None]
    assert not brak, f"{nazwa}: cytatow, ktorych nie ma w kodzie programu: {len(brak)} z {len(cytaty)}: {brak}"
    assert len(cytaty) >= MIN_CYTATOW[nazwa], f"{nazwa}: tylko {len(cytaty)} cytatow - czy napisy programu sa nadal w cudzyslowie prostym?"


def test_zmiana_napisu_w_programie_jest_wykrywana(indeks):
    """Ten sam zestaw napisow programu z jednym napisem zmienionym: cytat z instrukcji przestaje byc znajdowany."""
    from stanowisko import statusy as ST
    from stanowisko.ui import napisy_rano as NR

    for stary, nowy, dokument in (("Zamknij piec", "Zakoncz piec", "poranek"), ("Ukruszona", "Uszkodzona", "wieczor"),
                                  (ST.KOMUNIKATY["baza_zajeta"].tytul, "Baza zablokowana", "co_robic_gdy_nie_dziala"),
                                  (NR.BRAKI_TYTUL, "Brakuje w piecu: {n}", "poranek")):
        zmienione = H.Indeks([(napis.replace(stary, nowy), plik) for napis, plik in indeks.napisy])
        brak = H.brakujace_cytaty(md(dokument), zmienione)
        assert any(H.ascii_napis(stary).split("{")[0].strip() in c for c in brak), (stary, brak)
        assert not H.brakujace_cytaty(md(dokument), indeks)


def test_wyszukiwanie_cytatu_reguly(indeks):
    """Napis rowny, wzor z polem, fragment z trzema kropkami; wzor z samych pol i napis, ktorego nie ma - nie pasuja."""
    from stanowisko import statusy as ST
    from stanowisko.ui import napisy as N

    assert indeks.znajdz("Odswiez pule")[0] == ST.PRZYCISKI["odswiez_pule"]  # pisownia z ekranu (polskie znaki)
    assert indeks.znajdz("Do dofrezowania: 7")[0] == N.LISTA_TYTUL.format(n=7)
    assert indeks.znajdz("sprawdz")[0] == ST.STATUSY["zolty"].napis
    assert indeks.znajdz("czekam na plik skanu...")[0] == N.SKANER_CZEKA
    fragment = indeks.znajdz("... juz dziala na tym komputerze ...")
    assert fragment is not None and fragment[1] == "aplikacja.py" and fragment[0].startswith("... ") and fragment[0].endswith(" ...")
    assert indeks.znajdz("Wpisany numer kuwety: ...") is not None
    assert indeks.znajdz("juz dziala na tym komputerze") is None  # fragment bez kropek nie jest calym napisem
    for brak in ("Tego napisu nie ma w programie", "Zamknij pieca", "3221: 4", "Ala: kot"):
        assert indeks.znajdz(brak) is None, brak


def test_kluczowe_napisy_instrukcji_sa_stalymi_programu():
    """Najwazniejsze przyciski i tytuly komunikatow: instrukcja cytuje DOKLADNIE stala programu - zmiana stalej w ``statusy`` /
    ``napisy`` bez zmiany instrukcji konczy sie bledem (takze wtedy, gdy stary napis zostal gdzie indziej w kodzie)."""
    from stanowisko import statusy as ST
    from stanowisko.ui import napisy as N
    from stanowisko.ui import napisy_rano as NR

    p, k, q, s = ST.PRZYCISKI, ST.KOMUNIKATY, ST.PYTANIA, ST.STATUSY
    kluczowe = {
        "wieczor": [N.KTO_PRACUJE, p["ukruszona"], p["ok"], p["cofnij"], p["odswiez_pule"], p["zapisz_liste"], p["potwierdz_ponowny_skan"],
                    p["odrzuc_ponowny_skan"], k["skan_do_powtorzenia"].tytul, q["ponowny_skan"].tytul, s["zielony"].napis, s["czerwony"].napis,
                    s["zolty"].napis, s["szary"].napis, s["pomaranczowy"].napis, s["popraw_ulozenie"].napis, s["skan_ponownie"].napis,
                    s["ukruszona"].napis, s["zatwierdzona_ok"].napis, N.PLYTKA_SPRAWDZONA, ST.NAZWY_TRYBOW["wieczor"]],
        "poranek": [ST.NAZWY_TRYBOW["rano"], N.KTO_PRACUJE, p["zamknij_piec"], p["wybierz_kandydata"], p["przypisz_recznie"],
                    p["cofnij_przypisanie"], ST.PRZYCISK_BEZ_PROJEKTU, NR.KANDYDACI_TYTUL, NR.STRONA_ROZKLADANIE, NR.STRONA_WYNIK,
                    NR.EXCEL_POKAZ, NR.EXCEL_POMIN, NR.EXCEL_POZNIEJ, NR.PRZYPISZ_POKAZ, ST.NAZWY_KOLEJNOSCI["liczba"],
                    ST.NAZWY_KOLEJNOSCI["numer"], ST.status_rano("dwuznaczna").napis, ST.status_rano("nieznana").napis,
                    ST.status_rano("konflikt").napis, ST.status_rano("poprawka").napis, k["ramka_niedostepna"].tytul],
        "co_robic_gdy_nie_dziala": [k[x].tytul for x in (
            "blad_analizy", "silnik_nie_startuje", "wznowiono", "pula_brak_folderu", "pula_pusta", "ramka_wieczorna_niedostepna",
            "ramka_niedostepna", "baza_zajeta", "blad_zapisu", "plik_odrzucony", "skan_do_powtorzenia", "niezgodny_uklad",
            "folder_skanera_niedostepny", "plik_zajety", "plik_niedostepny", "excel_niedostepny", "excel_blad", "pusta_lista_operatorow",
            "analiza_trwa")] + [q["plytka_nie_z_trybu"].tytul, q["brak_numeru_plytki"].tytul, p["ponow_zapis"], p["pomin_skan"],
                                ST.PRZYCISK_ZESKANUJE_WLASCIWA, NR.TEST_LED, NR.STRONA_OSTATNI, ST.POWODY_ODRZUCENIA["za_krotki"],
                                ST.POWODY_BLEDU_ANALIZY["proces"], ST.NAPISY_NIEZAPISANE["baza_zajeta"], ST.NAPISY_NIEZAPISANE["blad_zapisu"],
                                ST.STANY_PULI["brak_folderu"], ST.STANY_PULI["pusta"], N.SKANER_CZEKA],
        "t14_jedna_strona": [N.KTO_PRACUJE, p["ukruszona"], p["ok"], p["cofnij"], p["potwierdz_ponowny_skan"], p["zamknij_piec"],
                             p["wybierz_kandydata"], k["skan_do_powtorzenia"].tytul, s["popraw_ulozenie"].napis],
    }
    for nazwa, stale in kluczowe.items():
        cytaty = set(H.cytaty(md(nazwa)))
        brak = [napis for napis in stale if H.ascii_napis(napis) not in cytaty]
        assert not brak, f"{nazwa}: instrukcja nie cytuje napisu programu: {brak}"


# ----------------------------------------------------------------------------
# (2) tabela "co robic, gdy nie dziala"
# ----------------------------------------------------------------------------
def wiersze_tabeli(tekst: str) -> list[list[str]]:
    wiersze = [[k.strip() for k in w.strip().strip("|").split("|")] for w in tekst.splitlines() if w.startswith("|")]
    return [w for w in wiersze[1:] if not all(re.fullmatch(r":?-+:?", k) for k in w)]


def test_tabela_co_robic_ma_wiersz_na_kazda_sytuacje():
    wiersze = wiersze_tabeli(md("co_robic_gdy_nie_dziala"))
    assert len(wiersze) == 22
    assert all(len(w) == 4 and all(w) for w in wiersze), [w for w in wiersze if len(w) != 4 or not all(w)]
    sytuacje = {  # sytuacja ze zlecenia (T7 i dalsze) -> tekst, ktory musi byc w kolumnie "Co widzisz"
        "silnik padl w trakcie analizy": '"Analiza skanu nie powiodla sie"', "analiza nie startuje": '"Analiza nie dziala"',
        "program zamkniety w polowie wieczoru": "Program zamknal sie w polowie pracy", "brak folderu Cyrkon": '"Brak folderu projektow"',
        "brak sieci": "Brak sieci", "brak ramki": '"Ramka wieczorna nie odpowiada"', "baza zajeta": '"Baza jest zajeta"',
        "drugi egzemplarz programu": "juz dziala na tym komputerze", "plytka nie z trybu": '"Plytka nie z tego trybu"',
        "skan uciety": '"plik uciety"', "drgniecie": '"skan jest poruszony', "pusta pula": '"Brak projektow w puli"',
        "bledy samokontroli": "`SAMOKONTROLA: CZERWONA`", "Excel niedostepny": '"Excel nie jest podlaczony"',
        "program nie startuje": "Program nie startuje"}
    pierwsza = [w[0] for w in wiersze]
    brak = [nazwa for nazwa, tekst in sytuacje.items() if not any(tekst in k for k in pierwsza)]
    assert not brak, f"brak wiersza tabeli dla sytuacji: {brak}"


def test_samokontrola_i_nazwy_plikow_wg_umowy():
    """Teksty w odwrotnych apostrofach: pliki z umowy E3-A11i i wiersze samokontroli z umowy E3-A11s (bez zgadywania kodow
    sprawdzen). Gdy modul samokontroli juz jest w programie - slowa z instrukcji musza w nim wystepowac."""
    slowa = set()
    for nazwa in INSTRUKCJE:
        for kod in re.findall(r"`([^`\n]*)`", md(nazwa)):
            assert kod in NAZWY_Z_UMOWY or kod in SAMOKONTROLA_Z_UMOWY, f"{nazwa}: `{kod}` nie jest nazwa z umowy A11i / A11s"
            if kod in SAMOKONTROLA_Z_UMOWY:
                slowa.update(re.findall(r"[A-Z]+", kod))
    assert {"SAMOKONTROLA", "CZERWONA", "ZIELONA", "BLAD", "OSTRZEZENIE"} <= slowa
    modul = STANOWISKO / "stanowisko" / "samokontrola.py"
    if modul.is_file():  # po scaleniu z E3-A11s
        zrodlo = modul.read_text(encoding="utf-8")
        assert not [s for s in sorted(slowa) if s not in zrodlo], "samokontrola.py nie zawiera slow cytowanych w instrukcji"


# ----------------------------------------------------------------------------
# (3) obrazki, (4) strony do druku i pliki, (5) jedna strona
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("nazwa", DOKUMENTY)
def test_obrazki_z_instrukcji_sa_na_liscie_zrzutow_i_w_stronie_do_druku(nazwa):
    plik_md = H.DOKUMENTY[nazwa][0]
    wskazane = H.obrazki(md(nazwa))
    strona = plik_md.with_suffix(".html").read_text(encoding="ascii")
    wpisane = dict(re.findall(r'<img data-plik="([^"]+)"[^>]*? src="data:image/png;base64,([A-Za-z0-9+/=]+)"', strona))
    for sciezka in wskazane:
        plik = Path(sciezka)
        assert plik.parent.as_posix() == "obrazki" and plik.suffix == ".png" and plik.stem in Z.ZRZUTY, sciezka
        assert plik.name in wpisane, f"{nazwa}: obrazka {plik.name} nie ma w stronie do druku"
        dane = base64.b64decode(wpisane[plik.name])
        assert dane[:8] == b"\x89PNG\r\n\x1a\n" and len(dane) > 2000, plik.name
        if nazwa.startswith("t14_"):  # obrazki proby T14 sa w repozytorium
            assert (plik_md.parent / sciezka).is_file(), sciezka
            assert (plik_md.parent / sciezka).read_bytes() == dane, f"{sciezka}: plik rozni sie od obrazka wpisanego w strone"
    assert len(wskazane) == LIMITY_STRONY[nazwa][1]


def test_kazdy_zrzut_jest_uzyty_i_zestaw_t14_jest_kompletny():
    uzyte = {Path(s).stem for nazwa in DOKUMENTY for s in H.obrazki(md(nazwa))}
    assert uzyte == set(Z.ZRZUTY), (uzyte ^ set(Z.ZRZUTY))
    assert {Path(s).stem for s in H.obrazki(md("t14_jedna_strona"))} == set(Z.T14_OBRAZKI)
    assert {p.stem for p in (T14 / "obrazki").glob("*.png")} == set(Z.T14_OBRAZKI)
    assert all(opis and scena.__name__ == f"scena_{nazwa}" for nazwa, (scena, _, opis) in Z.ZRZUTY.items())


@pytest.mark.parametrize("nazwa", DOKUMENTY)
def test_strona_do_druku_jest_aktualna(nazwa, indeks):
    """Skladanie ``.md`` daje dokladnie zapisana strone ``.html`` (obrazki z dysku albo - gdy ich nie ma - ze strony)."""
    plik_html, strona, zrodla = H.zloz_dokument(nazwa, indeks)
    assert all(zrodla.values())
    assert plik_html.read_text(encoding="ascii") == strona, f"{plik_html.name} nieaktualny: uruchom narzedzia/instrukcje_html.py"
    assert "&#8222;" in strona and "<img" in strona or nazwa in ("co_robic_gdy_nie_dziala", "t14_arkusz_obserwacji")


def test_pliki_ascii_lf_i_rozmiar_w_repo():
    pliki = [p for nazwa in DOKUMENTY for p in (H.DOKUMENTY[nazwa][0], H.DOKUMENTY[nazwa][0].with_suffix(".html"))]
    pliki += [T14 / "README.md", T14 / "scenariusz_symulatora.md", T14 / "scenariusz_t14.json", T14 / "symulator_t14.py",
              STANOWISKO / "narzedzia" / "instrukcje_html.py", STANOWISKO / "narzedzia" / "zrzuty_instrukcji.py", Path(__file__)]
    for plik in pliki:
        dane = plik.read_bytes()
        assert dane.isascii(), f"{plik.name}: znaki spoza ASCII"
        assert b"\r" not in dane, f"{plik.name}: konce linii CRLF"
    rozmiar = sum(p.stat().st_size for p in pliki) + sum(p.stat().st_size for p in (T14 / "obrazki").glob("*.png"))
    assert rozmiar < 3_200_000, f"instrukcje i zestaw T14 zajmuja {rozmiar} B (zlecenie: lacznie do ok. 3 MB)"


@pytest.mark.parametrize("nazwa", DOKUMENTY)
def test_objetosc_jednej_strony(nazwa):
    """Druku test nie mierzy (przegladarka poza testami); pilnuje, zeby tresc nie urosla ponad zmierzona objetosc 1 strony A4."""
    tekst = "\n".join(w for w in md(nazwa).splitlines() if not w.strip().startswith("<!--"))
    tekst = re.sub(r"\|[-|]+\|", " ", H.WZOR_OBRAZKA.sub(" ", tekst))
    slow = len(tekst.split())
    assert slow <= LIMITY_STRONY[nazwa][0], f"{nazwa}: {slow} slow (limit {LIMITY_STRONY[nazwa][0]}) - zmierz druk: instrukcje_html.py --pdf"
    assert sum(1 for w in md(nazwa).splitlines() if w.startswith("# ")) == 1


# ----------------------------------------------------------------------------
# (6) zestaw proby T14
# ----------------------------------------------------------------------------
def scenariusz() -> dict:
    sys.path.insert(0, str(T14))
    import symulator_t14 as S

    return S.wczytaj_scenariusz(T14 / "scenariusz_t14.json")


def test_arkusz_obserwacji_ma_11_zadan_planu_i_liczby_scenariusza():
    wiersze = wiersze_tabeli(md("t14_arkusz_obserwacji").split("## Podsumowanie")[0])
    assert [w[0] for w in wiersze] == ["W1", "W2", "W3", "W4", "W5", "R1", "R2", "R3", "R4", "R5", "R6"]
    assert all(len(w) == 7 and w[1] and w[2] and not any(w[3:]) for w in wiersze)  # pola obserwatora puste
    tekst = md("t14_arkusz_obserwacji")
    assert "11 z 11 zadan wykonanych, 0 interwencji obserwatora" in tekst and "z 11." in tekst
    s = scenariusz()
    w, r = s["wieczor"]["oczekiwane"], s["rano"]["oczekiwane"]
    zad = {x[0]: x[1] + " " + x[2] for x in wiersze}
    assert all(str(nr) in zad["W2"] for nr in w["do_obejrzenia"])
    assert r["kuweta_do_znalezienia"] in zad["R5"] and all(kuweta in zad["R6"] for kuweta in r["braki"])
    assert f"gniazdo {r['zolte']} plytki {r['plytka_z_zoltym']}" in zad["R2"]


def test_scenariusz_t14_na_atrapie_kontrolera(tmp_path):
    """Skany scenariusza podane atrapie kontrolera (bez okna): stan programu = pole ``oczekiwane`` scenariusza."""
    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    s = scenariusz()
    surowy = json.loads((T14 / "scenariusz_t14.json").read_text(encoding="ascii"))
    assert len(surowy["wieczor"]["skany"]) >= 3 and len(surowy["rano"]["skany"]) >= 2
    w, ocz = s["wieczor"]["skany"], s["wieczor"]["oczekiwane"]
    assert all(x["rodzaj"] in K.RODZAJE_SKANOW_ATRAPY and set(x["gniazda"].values()) <= set(K.RODZAJE_PRAC) for x in w)
    k = K.AtrapaKontrolera(tmp_path / "wieczor")
    try:
        k.wybierz_operatora(k.sesja.operatorzy[0])
        skan1 = k.symuluj_skan(w[0]["rodzaj"], numer=w[0]["numer"], gniazda=w[0]["gniazda"], projekty=w[0]["projekty"])
        p1 = k.stan().plytka(skan1)
        czerwone = sorted(g.nr for g in p1.gniazda if g.prace and g.status == "czerwony")
        inne = sorted(g.nr for g in p1.gniazda if g.prace and g.status != "zielony")
        assert czerwone == ocz["czerwone"] and inne == ocz["do_obejrzenia"]
        assert k.ukruszona(p1.gniazdo(czerwone[0]).praca.praca_id) and k.ok(p1.gniazdo(czerwone[1]).praca.praca_id)
        skan2 = k.symuluj_skan(w[1]["rodzaj"], numer=w[1]["numer"], gniazda=w[1]["gniazda"], projekty=w[1]["projekty"])
        p2 = k.stan().plytka(skan2)
        assert p2.status == "do_powtorzenia" and p2.numer == ocz["plytka_do_poprawienia"]
        assert p2.gniazdo(ocz["popraw_ulozenie"]).status == "popraw_ulozenie"
        assert any(x.rodzaj == "skan_do_powtorzenia" for x in k.stan().komunikaty)
        skan3 = k.symuluj_skan(w[2]["rodzaj"], numer=w[2]["numer"], gniazda=w[2]["gniazda"], projekty=w[2]["projekty"])
        pytania = [q for q in k.stan().pytania if q.rodzaj == "ponowny_skan"]
        assert len(pytania) == 1 and k.potwierdz_ponowny_skan(skan3)
        p3 = k.stan().plytka(skan3)
        assert {g.status for g in p3.gniazda if g.prace} == {"zielony"} and not [q for q in k.stan().pytania if q.rodzaj == "ponowny_skan"]
        assert len(k.stan().do_dofrezowania_biezaca) == 1 and not k.stan().konflikty
    finally:
        k.zamknij()
    r, ocz = s["rano"]["skany"], s["rano"]["oczekiwane"]
    assert all(set(x["gniazda"].values()) <= set(K.RODZAJE_PRAC_RANO) for x in r)
    k = K.AtrapaKontrolera(tmp_path / "rano")
    try:
        k.przelacz_tryb(K.TRYB_RANO)
        k.wybierz_operatora(k.sesja.operatorzy[0])
        skany = [k.symuluj_skan_rano(x["numer"], x["gniazda"], projekty=x["projekty"]) for x in r[:2]]
        stan = k.stan().rano
        plytka = next(p for p in stan.plytki if p.skan_id == skany[0])
        zolte = [g.nr for g in plytka.gniazda if g.prace and g.prace[0].klasa == "dwuznaczna"]
        assert plytka.numer == ocz["plytka_z_zoltym"] and zolte == [ocz["zolte"]]
        praca = plytka.gniazdo(ocz["zolte"]).prace[0]
        assert len(praca.kandydaci) == 2 and k.wybierz_kandydata(praca.praca_id, praca.kandydaci[0].sha16)
        assert ocz["kuweta_do_znalezienia"] in [x.kuweta for x in k.stan().rano.kuwety] and k.wybierz_kuwete(ocz["kuweta_do_znalezienia"])
        assert k.stan().rano.kuweta_biezaca == ocz["kuweta_do_znalezienia"]
        assert k.zamknij_piec(k.stan().rano.sesja_pieca_id)
        stan = k.stan().rano
        assert [z.kuweta for z in stan.kompletne] == ocz["kompletne"] and [z.kuweta for z in stan.braki] == ocz["braki"]
        assert ST.KOMUNIKATY["excel_niedostepny"].tytul in [x.tytul for x in k.stan().komunikaty]  # bez Excela: komunikat, praca dalej
    finally:
        k.zamknij()


def test_symulator_t14_przebieg_11_zadan_na_oknie_programu_bez_ekranu(tmp_path):
    """``symulator_t14.py --sprawdz`` w osobnym procesie: okno programu, Spacja -> skan ze scenariusza, 11 zadan T14 sterowaniem
    ze skryptu; wynik czytany z ekranu. Zjawisko 0xC0000142 (proces potomny nie startuje) = ponowienie proby."""
    polecenie = [sys.executable, str(T14 / "symulator_t14.py"), "--sprawdz", "--program", str(STANOWISKO), "--dziennik", str(tmp_path / "t14.log")]
    for _ in range(3):
        wynik = subprocess.run(polecenie, capture_output=True, text=True, cwd=str(tmp_path), timeout=300,
                               env={**os.environ, "QT_QPA_PLATFORM": "offscreen", "PYTHONUTF8": "1"})
        if wynik.returncode & 0xFFFFFFFF != KOD_ZNIKNIECIA_PROCESU:
            break
    assert wynik.returncode == 0, wynik.stdout + wynik.stderr
    assert "SPRAWDZENIE T14 BEZ EKRANU: zgodne 18 z 18 krokow" in wynik.stdout and "NIEZGODNE" not in wynik.stdout
    assert "Traceback" not in wynik.stderr, wynik.stderr
    assert (tmp_path / "t14.log").read_bytes().isascii()


@pytest.mark.parametrize("plik", ["README.md", "scenariusz_symulatora.md"])
def test_cytaty_w_opisie_proby_t14(plik, indeks):
    """Opis proby dla prowadzacego: napisy z ekranu w cudzyslowie prostym tez musza istniec w programie."""
    tekst = (T14 / plik).read_text(encoding="ascii")
    assert not H.brakujace_cytaty(tekst, indeks)
    if plik == "scenariusz_symulatora.md":
        assert len(H.cytaty(tekst)) >= 20 and "zgodne 18 z 18 krokow" in tekst
