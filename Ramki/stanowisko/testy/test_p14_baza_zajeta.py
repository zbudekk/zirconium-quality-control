"""E3-P14, N1: decyzja technika przy bazie zajetej przez inny program (test koncowy T7 "baza zajeta").

Inny program trzyma baze stanowiska (drugie polaczenie SQLite, ``BEGIN EXCLUSIVE`` - nie da sie ani pisac, ani czytac).
Wymagane:
(a) polecenie technika (decyzja "Ukruszona" / "OK", cofniecie, wybor kandydata, "Rozlozona", "Zamknij piec") nie ginie po
    cichu: odmowa ``baza_zajeta`` + komunikat TRWALY ``decyzja_niezapisana`` / ``polecenie_niezapisane``, ktory mowi wprost
    "NIE", nazywa polecenie i ma przycisk "Ponow teraz" (polecenie ``ponow_polecenie(id komunikatu)``) ponawiajacy DOKLADNIE
    to polecenie; komunikat znika dopiero po udanym zapisie tej decyzji albo po swiadomej rezygnacji;
(b) okno nie stoi: polecenie przy zajetej bazie wraca w ciagu ``LIMIT_ODPOWIEDZI_S`` (przed poprawka ok. 15 s).
Pomiar czasu wg wzorca E3-T0p (``pomiar_czasu``): kryterium na czasie sciennym; pomiar jest powtarzany tylko wtedy, gdy
przekroczenie wyjasnia przestoj calego procesu albo dysku (PC wspoldzielony), najwyzej 2 razy, z ostrzezeniem.
"""
from __future__ import annotations

import os
import sqlite3
import time

import pytest

import test_ui_wieczor as UW
from stanowisko import baza as B
from stanowisko import statusy as ST

LIMIT_ODPOWIEDZI_S = 1.0  # zlecenie E3-P14: "okno odpowiada w ciagu 1 s"
NIEZAPISANE = ("decyzja_niezapisana", "polecenie_niezapisane")


@pytest.fixture(scope="module", autouse=True)
def _qt():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    if UW.FONTY_WINDOWS.is_dir():
        os.environ.setdefault("QT_QPA_FONTDIR", str(UW.FONTY_WINDOWS))
    import PySide6.QtCore  # noqa: F401
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    UW.czcionka_ekranu()
    yield app


@pytest.fixture
def zegar():
    return UW.Zegar()


def nowa_atrapa(katalog, zegar):
    from stanowisko import kontroler_api as K

    return K.AtrapaKontrolera(katalog, zegar=zegar)


@pytest.fixture
def atrapa(tmp_path, zegar):
    k = nowa_atrapa(tmp_path / "atrapa", zegar)
    yield k
    k.zamknij()


class ObcyProgram:
    """Drugie polaczenie z plikiem bazy: ``zajmij()`` = ``BEGIN EXCLUSIVE`` (inny program trzyma baze), ``zwolnij()``."""

    def __init__(self, kontroler):
        self.pol = sqlite3.connect(str(kontroler.sesja.baza.plik), timeout=0.1, isolation_level=None)
        self.zajeta = False

    def zajmij(self) -> None:
        self.pol.execute("BEGIN EXCLUSIVE")
        self.zajeta = True

    def zwolnij(self) -> None:
        if self.zajeta:
            self.pol.execute("ROLLBACK")
            self.zajeta = False

    def zamknij(self) -> None:
        self.zwolnij()
        self.pol.close()


@pytest.fixture
def obcy(atrapa):
    o = ObcyProgram(atrapa)
    yield o
    o.zamknij()


def niezapisane(kontroler) -> list:
    return [k for k in kontroler.stan().komunikaty if k.rodzaj in NIEZAPISANE]


def decyzja_pracy(kontroler, praca_id: int):
    return kontroler.sesja.baza.wiersz("SELECT count(*) AS n FROM decyzje WHERE praca_id = ?", (praca_id,))["n"]


# ----------------------------------------------------------------------------
# baza: czekanie na blokade na czas bloku
# ----------------------------------------------------------------------------
def test_n1_baza_czekanie_skraca_czekanie_na_blokade_i_przywraca(tmp_path):
    """``Baza.czekanie(ms)``: w bloku zapis przy bazie trzymanej przez inne polaczenie konczy sie ``BladBazy`` po ok. ``ms``
    (nie po 5 s) z prawdziwym czasem w komunikacie; po bloku wraca czekanie polaczenia (takze po wyjatku i przy zagniezdzeniu)."""
    with B.otworz(tmp_path / "s.sqlite") as baza:
        domyslne = baza.czekaj_ms
        assert domyslne == B.CZEKAJ_NA_BLOKADE_MS == 5000
        obce = sqlite3.connect(str(baza.plik), timeout=0.1, isolation_level=None)
        try:
            obce.execute("BEGIN IMMEDIATE")
            t0 = time.perf_counter()
            with pytest.raises(B.BladBazy) as blad:
                with baza.czekanie(200):
                    assert baza.czekaj_ms == 200
                    with baza.czekanie(100):
                        assert baza.czekaj_ms == 100
                    assert baza.czekaj_ms == 200
                    baza.zdarzenie("test", "zapis", {"a": 1})
            czas = time.perf_counter() - t0
            assert "zajeta" in str(blad.value) and "0.2 s" in str(blad.value) and "niczego nie zapisano" in str(blad.value)
            assert czas < 2.5, f"czekanie 200 ms trwalo {czas:.2f} s"
            assert baza.czekaj_ms == domyslne
            assert baza.polaczenie.execute("PRAGMA busy_timeout").fetchone()[0] == domyslne
            obce.execute("ROLLBACK")
            with baza.czekanie(200):
                baza.zdarzenie("test", "zapis", {"a": 2})  # po zwolnieniu ta sama operacja przechodzi
            assert [w["typ"] for w in baza.wiersze("SELECT typ FROM zdarzenia WHERE zrodlo = 'test'")] == ["zapis"]
        finally:
            obce.close()


# ----------------------------------------------------------------------------
# (a) decyzja nie ginie po cichu - kontroler
# ----------------------------------------------------------------------------
def test_n1_decyzja_przy_zajetej_bazie_zostaje_do_ponowienia(atrapa, obcy):
    """"Ukruszona" przy zajetej bazie: odmowa ``baza_zajeta``, komunikat trwaly "decyzja NIE zostala zapisana" z nazwa decyzji,
    plytka i gniazdem; decyzji nie ma w bazie. Udane polecenie dla INNEJ pracy komunikatu nie zdejmuje. ``ponow_polecenie`` po
    zwolnieniu bazy zapisuje te decyzje i komunikat znika."""
    atrapa.wybierz_operatora("Technik A")
    skan = atrapa.symuluj_skan("zwykla", numer=1)
    plytka = atrapa.stan().plytka(skan)
    p2, p9 = plytka.gniazdo(2).praca.praca_id, plytka.gniazdo(9).praca.praca_id
    obcy.zajmij()
    odp = atrapa.wykonaj("ukruszona", p2)
    assert not odp.ok and odp.kod == "baza_zajeta"
    czekajace = niezapisane(atrapa)
    assert len(czekajace) == 1, [(k.rodzaj, k.tekst) for k in atrapa.stan().komunikaty]
    k = czekajace[0]
    assert k.rodzaj == "decyzja_niezapisana" and k.trwaly and k.poziom == ST.POZIOM_BLAD
    assert "NIE" in k.tytul + k.tekst and ST.PRZYCISKI["ukruszona"] in k.tekst and "gniazdo 2" in k.tekst and odp.tekst == k.tekst
    obcy.zwolnij()
    assert decyzja_pracy(atrapa, p2) == 0 and atrapa.stan().praca(p2).decyzja is None
    assert atrapa.wykonaj("ok", p9).ok  # inna praca: decyzja zapisana, komunikat o pracy z gniazda 2 ZOSTAJE
    assert [x.id for x in niezapisane(atrapa)] == [k.id] and atrapa.stan().praca(p2).decyzja is None
    atrapa.przetworz()
    assert [x.id for x in niezapisane(atrapa)] == [k.id]
    odp = atrapa.wykonaj("ponow_polecenie", k.id)
    assert odp.ok, odp
    stan = atrapa.stan()
    assert stan.praca(p2).decyzja == "ukruszona" and not niezapisane(atrapa) and len(stan.do_dofrezowania) == 1
    assert decyzja_pracy(atrapa, p2) == 1  # jedna decyzja, nie dwie
    assert not atrapa.wykonaj("ponow_polecenie", k.id).ok  # nic juz nie czeka: odmowa, bez drugiego zapisu
    assert decyzja_pracy(atrapa, p2) == 1


def test_n1_ponowna_decyzja_technika_zdejmuje_komunikat_a_rezygnacja_nie_zapisuje(atrapa, obcy):
    """Technik zamiast "Ponow teraz" klika decyzje jeszcze raz (po zwolnieniu bazy): zapis i komunikat znika. Druga nieudana
    proba dla tej samej pracy nie mnozy komunikatow. Rezygnacja ("zamknij_komunikat") = komunikat znika, decyzji nie ma."""
    atrapa.wybierz_operatora("Technik A")
    skan = atrapa.symuluj_skan("zwykla", numer=1)
    plytka = atrapa.stan().plytka(skan)
    p2, p3 = plytka.gniazdo(2).praca.praca_id, plytka.gniazdo(3).praca.praca_id
    obcy.zajmij()
    assert not atrapa.wykonaj("ukruszona", p2).ok
    assert not atrapa.wykonaj("ok", p2).ok  # zmienil zdanie, baza nadal zajeta: jeden komunikat, o ostatniej decyzji
    assert not atrapa.wykonaj("ok", p3).ok
    czekajace = niezapisane(atrapa)
    assert len(czekajace) == 2 and ST.PRZYCISKI["ok"] in czekajace[0].tekst and "gniazdo 2" in czekajace[0].tekst
    ponowione = atrapa.wykonaj("ponow_polecenie", czekajace[0].id)  # baza nadal zajeta: decyzja dalej czeka
    assert not ponowione.ok and ponowione.kod == "baza_zajeta" and len(niezapisane(atrapa)) == 2
    obcy.zwolnij()
    assert atrapa.wykonaj("ok", p2).ok
    czekajace = niezapisane(atrapa)
    assert len(czekajace) == 1 and "gniazdo 3" in czekajace[0].tekst and atrapa.stan().praca(p2).decyzja == "ok"
    assert atrapa.wykonaj("zamknij_komunikat", czekajace[0].id).ok  # rezygnacja
    assert not niezapisane(atrapa) and atrapa.stan().praca(p3).decyzja is None and decyzja_pracy(atrapa, p3) == 0
    assert not atrapa.wykonaj("ponow_polecenie", czekajace[0].id).ok and decyzja_pracy(atrapa, p3) == 0


# ----------------------------------------------------------------------------
# (b) inne zapisy wywolywane kliknieciem: czas i brak cichej utraty (tabela w raporcie)
# ----------------------------------------------------------------------------
def _wieczor(k) -> dict:
    k.wybierz_operatora("Technik A")
    skan = k.symuluj_skan("zwykla", numer=1)
    plytka = k.stan().plytka(skan)
    p2, p9 = plytka.gniazdo(2).praca.praca_id, plytka.gniazdo(9).praca.praca_id
    assert k.ok(p9).ok
    return {"ukruszona": ("ukruszona", (p2,)), "ok": ("ok", (p2,)), "cofnij": ("cofnij", (p9,))}


def _rano(k) -> dict:
    skany = k.scenariusz_poranny()
    rano = k.stan().rano
    konflikt = rano.plytka(skany[6]).gniazdo(11).praca.praca_id
    assert k.przypisz_recznie(konflikt, None).ok  # konflikt rozstrzygniety: "Zamknij piec" dozwolone
    rano = k.stan().rano
    zolta = rano.plytka(skany[4]).gniazdo(9).praca
    assert "zamknij_piec" in rano.dozwolone and rano.kuweta_biezaca
    return {"wybierz_kandydata": ("wybierz_kandydata", (zolta.praca_id, zolta.kandydaci[0].sha16)),
            "przypisz_recznie": ("przypisz_recznie", (zolta.praca_id,)),
            "potwierdz_kuwete": ("potwierdz_kuwete", (rano.kuweta_biezaca,)),
            "zamknij_piec": ("zamknij_piec", (rano.sesja_pieca_id,))}


POLECENIA_KLIKANE = (("wieczor", "ukruszona"), ("wieczor", "ok"), ("wieczor", "cofnij"), ("rano", "wybierz_kandydata"),
                     ("rano", "przypisz_recznie"), ("rano", "potwierdz_kuwete"), ("rano", "zamknij_piec"))


@pytest.mark.parametrize("pora,polecenie", POLECENIA_KLIKANE)
def test_n1_polecenie_klikane_przy_zajetej_bazie_wraca_w_limicie_i_daje_sie_ponowic(tmp_path, zegar, pora, polecenie):
    """Kazde polecenie zapisujace, ktore technik wywoluje kliknieciem: przy zajetej bazie wraca w ``LIMIT_ODPOWIEDZI_S`` z odmowa
    ``baza_zajeta`` i komunikatem do ponowienia; ``przetworz`` (zegar okna) tez nie stoi; po zwolnieniu bazy "Ponow teraz"
    wykonuje polecenie (ten sam skutek w bazie, co polecenie wykonane od razu)."""
    import pomiar_czasu as PC

    def proba(nr: int) -> tuple:
        k = nowa_atrapa(tmp_path / f"{pora}_{polecenie}_{nr}", zegar)
        obcy = None
        try:
            nazwa, argumenty = (_wieczor if pora == "wieczor" else _rano)(k)[polecenie]
            dziennik = k.sesja.baza.wiersz("SELECT count(*) AS n FROM zdarzenia")["n"]
            decyzji = k.sesja.baza.wiersz("SELECT count(*) AS n FROM decyzje")["n"]
            obcy = ObcyProgram(k)
            obcy.zajmij()
            with PC.PomiarOdporny(dysk=tmp_path) as pw:
                t0 = time.perf_counter()
                odp = k.wykonaj(nazwa, *argumenty)
                t1 = time.perf_counter()
                k.przetworz()
                t2 = time.perf_counter()
            czas, tykniecie = t1 - t0, t2 - t1
            opis = (f"{polecenie}: odpowiedz po {czas * 1000:.0f} ms, przetworz {tykniecie * 1000:.0f} ms (limit {LIMIT_ODPOWIEDZI_S * 1000:.0f} ms); "
                    f"przestoj procesu {pw.przestoj(t0, t2) * 1000:.0f} ms, dysku {pw.przestoj_dysku(t0, t2) * 1000:.0f} ms")
            if max(czas, tykniecie) > LIMIT_ODPOWIEDZI_S:
                if max(pw.wlasny(t0, t1), pw.wlasny(t1, t2)) <= LIMIT_ODPOWIEDZI_S:
                    return PC.POWTORZ_PROCES, opis
                if max(czas, tykniecie) - pw.przestoj_dysku(t0, t2) <= LIMIT_ODPOWIEDZI_S:
                    return PC.POWTORZ_DYSK, opis
                return PC.BLAD, opis
            assert not odp.ok and odp.kod == "baza_zajeta", odp
            czekajace = niezapisane(k)
            assert len(czekajace) == 1 and czekajace[0].trwaly and "NIE" in czekajace[0].tytul + czekajace[0].tekst, k.stan().komunikaty
            obcy.zwolnij()
            assert k.sesja.baza.wiersz("SELECT count(*) AS n FROM zdarzenia")["n"] == dziennik  # nic nie zapisane
            assert k.sesja.baza.wiersz("SELECT count(*) AS n FROM decyzje")["n"] == decyzji
            ponowione = k.wykonaj("ponow_polecenie", czekajace[0].id)
            assert ponowione.ok, ponowione
            assert not niezapisane(k)
            assert (k.sesja.baza.wiersz("SELECT count(*) AS n FROM zdarzenia")["n"] + k.sesja.baza.wiersz("SELECT count(*) AS n FROM decyzje")["n"]
                    > dziennik + decyzji)
            if polecenie == "zamknij_piec":
                assert not k.stan().rano.otwarty
            return PC.OK, opis
        finally:
            if obcy is not None:
                obcy.zamknij()
            k.zamknij()

    powtorki = PC.Powtorki()
    while True:
        ocena, opis = proba(len(powtorki.historia) + 1)
        print(f"\n[N1 {pora}] proba {len(powtorki.historia) + 1}: {ocena}; {opis}")
        if not powtorki.dalej(ocena, opis):
            break
    powtorki.ostrzez(f"N1 {polecenie}", ocena)
    assert ocena == PC.OK, f"N1 {polecenie}: {powtorki.opis()}"


# ----------------------------------------------------------------------------
# okno: klikniecie "Ukruszona" przy zajetej bazie
# ----------------------------------------------------------------------------
def test_n1_okno_odpowiada_w_limicie_i_pokazuje_decyzje_do_ponowienia(tmp_path, zegar):
    """Okno (offscreen), proba P2 recenzenta: klikniecie "Ukruszona", gdy inny program trzyma baze. Okno wraca w
    ``LIMIT_ODPOWIEDZI_S`` (bylo ok. 15 s), na pasku bledow jest komunikat "Decyzja NIE zostala zapisana" z przyciskiem
    "Ponow teraz", gniazdo NIE ma podpisu decyzji; po zwolnieniu bazy "Ponow teraz" zapisuje decyzje: podpis gniazda, lista
    "do dofrezowania" i znikniecie komunikatu."""
    import pomiar_czasu as PC
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    def proba(nr: int) -> tuple:
        k = nowa_atrapa(tmp_path / f"okno_{nr}", zegar)
        obcy, e = None, None
        try:
            k.wybierz_operatora("Technik A")
            skan = k.symuluj_skan("zwykla", numer=1)
            e = UW.Ekran(k)
            e.klik_gniazdo(2)
            przed = e.mapa.podpisy()[2]
            przycisk = e.w("przycisk_ukruszona")
            assert przycisk.isEnabled() and przed != ST.STATUSY["ukruszona"].napis
            obcy = ObcyProgram(k)
            obcy.zajmij()
            with PC.PomiarOdporny(dysk=tmp_path) as pw:
                t0 = time.perf_counter()
                QTest.mouseClick(przycisk, Qt.MouseButton.LeftButton)
                t1 = time.perf_counter()
                e.odczekaj(150)  # kilka tykniec zegara okna przy zajetej bazie
                t2 = time.perf_counter()
            czas, dalej = t1 - t0, (t2 - t1) - 0.150
            opis = (f"klikniecie przy zajetej bazie: {czas * 1000:.0f} ms, kolejne 150 ms pracy okna wydluzone o {dalej * 1000:.0f} ms "
                    f"(limit {LIMIT_ODPOWIEDZI_S * 1000:.0f} ms); przestoj procesu {pw.przestoj(t0, t2) * 1000:.0f} ms, "
                    f"dysku {pw.przestoj_dysku(t0, t2) * 1000:.0f} ms")
            if max(czas, dalej) > LIMIT_ODPOWIEDZI_S:
                if max(pw.wlasny(t0, t1), pw.wlasny(t1, t2) - 0.150) <= LIMIT_ODPOWIEDZI_S:
                    return PC.POWTORZ_PROCES, opis
                if max(czas, dalej) - pw.przestoj_dysku(t0, t2) <= LIMIT_ODPOWIEDZI_S:
                    return PC.POWTORZ_DYSK, opis
                return PC.BLAD, opis
            assert e.jest("komunikat_decyzja_niezapisana") and e.jest("komunikat_ponow_polecenie"), e.tekst()
            tekst = e.tekst_elementu("komunikat_decyzja_niezapisana")
            assert "NIE" in tekst and ST.PRZYCISKI["ukruszona"] in tekst and "gniazdo 2" in tekst
            assert e.w("komunikat_ponow_polecenie").text() == ST.PRZYCISKI["ponow_polecenie"]
            assert not e.jest("komunikat_odpowiedz")  # jeden komunikat, nie dwa
            assert e.mapa.podpisy()[2] == przed and k.stan().praca(k.stan().plytka(skan).gniazdo(2).praca.praca_id).decyzja is None
            obcy.zwolnij()
            e.odczekaj(1500)  # program sam decyzji NIE zapisuje - czeka na technika
            assert e.jest("komunikat_decyzja_niezapisana") and e.mapa.podpisy()[2] == przed
            e.klik("komunikat_ponow_polecenie")
            e.czekaj(lambda: not e.jest("komunikat_decyzja_niezapisana"), 5.0, "znikniecie komunikatu po ponowieniu")
            assert e.mapa.podpisy()[2] == ST.STATUSY["ukruszona"].napis
            assert k.stan().plytka(skan).gniazdo(2).praca.decyzja == "ukruszona" and len(e.lista()) == 1
            return PC.OK, opis
        finally:
            if e is not None:
                e.zamknij()
            if obcy is not None:
                obcy.zamknij()
            k.zamknij()

    powtorki = PC.Powtorki()
    while True:
        ocena, opis = proba(len(powtorki.historia) + 1)
        print(f"\n[N1 okno] proba {len(powtorki.historia) + 1}: {ocena}; {opis}")
        if not powtorki.dalej(ocena, opis):
            break
    powtorki.ostrzez("N1 okno", ocena)
    assert ocena == PC.OK, f"N1 okno: {powtorki.opis()}"
