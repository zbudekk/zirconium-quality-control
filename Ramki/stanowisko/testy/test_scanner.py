"""scanner (E3-A2): obserwacja folderu eksportu skanera, koniec zapisu, walidacja STL, duplikaty.

Kryteria odbioru z planu etapu 3 (sekcja 4.1, E3-A2), ktore sprawdza ten plik:
  1. 100 zapisow w kawalkach trwajacych 1-5 s: 100 zdarzen, 0 przed koncem zapisu, mediana opoznienia < 1 s,
  2. plik uciety, pusty, nie-STL albo z niezgodnym naglowkiem: 0 zdarzen i wpis z powodem,
  3. ten sam plik zapisany ponownie pod ta sama nazwa = nowe zdarzenie; ta sama zawartosc pod inna nazwa = flaga "duplikat",
  4. 20 plikow naraz: zdarzenia w kolejnosci zapisu, zadnego zgubionego (czesc silnika: test_silnik.py).

Progi czasu. Kryterium 1 mowi "mediana ponizej 1 s". Zestaw pytest biegnie na komputerze, na ktorym rownolegle licza
inne sesje, wiec domyslny prog w tescie jest luzniejszy (PROG_MEDIANY_S = 2,0 s); prog z kryterium (1,0 s) wlacza
zmienna srodowiskowa E3A2_SCISLE=1. Zmierzona mediana jest wypisywana (pytest -s) i podana w raporcie paczki.
Liczniki (100 z 100, 0 przed koncem zapisu) sa sprawdzane zawsze dokladnie.
"""
from __future__ import annotations

import os
import queue
import statistics
import threading
import time
from pathlib import Path

import pytest

import symulator_skanera as SY
from stanowisko import scanner as SC
from stanowisko.dzien_skanera_rdzen import stl_binarny_kompletny

SCISLE = os.environ.get("E3A2_SCISLE") == "1"
PROG_MEDIANY_S = 1.0 if SCISLE else 2.0  # kryterium 1: 1,0 s; domyslnie tolerancja na obciazony komputer
SZYBKO = dict(stabilizacja_ms=150, odrzuc_po_s=0.6, okres_s=0.03, przeglad_s=0.5)  # parametry skrocone: testy logiki, nie czasu


class Zbior:
    """Odbiornik zdarzen obserwatora (wywolywany w watku obserwatora)."""

    def __init__(self):
        self.skany: list[SC.ZdarzenieSkanu] = []
        self.odrzucone: list[SC.Odrzucenie] = []
        self.oczekiwania: list = []  # SC.Oczekiwanie: plik zajety przez inny program
        self._zmiana = threading.Condition()

    def oczekiwanie(self, o) -> None:
        with self._zmiana:
            self.oczekiwania.append(o)
            self._zmiana.notify_all()

    def skan(self, z) -> None:
        with self._zmiana:
            self.skany.append(z)
            self._zmiana.notify_all()

    def odrzucenie(self, o) -> None:
        with self._zmiana:
            self.odrzucone.append(o)
            self._zmiana.notify_all()

    def czekaj(self, warunek, limit_s: float = 20.0) -> bool:
        with self._zmiana:
            return self._zmiana.wait_for(warunek, limit_s)


@pytest.fixture
def obserwator(tmp_path):
    """Funkcja ``start(**parametry) -> (Scanner, Zbior, folder)``; obserwatory sa zatrzymywane po tescie."""
    uruchomione = []

    def start(folder: Path | None = None, **parametry):
        folder = folder if folder is not None else tmp_path / "eksport"
        if parametry.pop("utworz", True):
            folder.mkdir(parents=True, exist_ok=True)
        zb = Zbior()
        sc = SC.Scanner(folder, na_skan=zb.skan, na_odrzucenie=zb.odrzucenie, na_oczekiwanie=zb.oczekiwanie, **{**SZYBKO, **parametry})
        sc.start()
        uruchomione.append(sc)
        return sc, zb, folder

    yield start
    for sc in uruchomione:
        sc.stop()


# ----------------------------------------------------------------------------
# walidacja pliku (S2)
# ----------------------------------------------------------------------------
def test_sprawdz_stl_powody(tmp_path):
    dobry = SY.sztuczny_stl(40, seed=1)
    przypadki = {
        "dobry.stl": (dobry, None),
        "pusty.stl": (b"", "pusty"),
        "krotki.stl": (dobry[:50], "za_krotki"),
        "uciety.stl": (dobry[: len(dobry) // 2], "rozmiar_niezgodny"),
        "nadmiar.stl": (dobry + b"\0" * 10, "rozmiar_niezgodny"),
        "zly_naglowek.stl": (SY.zly_plik("zly_naglowek", dobry), "rozmiar_niezgodny"),
        "smieci.stl": (SY.zly_plik("nie_stl", dobry), "rozmiar_niezgodny"),
        "tekstowy.stl": (SY.zly_plik("stl_tekstowy", dobry), "stl_tekstowy"),
        "zero.stl": (SY.sztuczny_stl(0), "za_malo_trojkatow"),
    }
    for nazwa, (dane, powod) in przypadki.items():
        p = tmp_path / nazwa
        p.write_bytes(dane)
        w = SC.sprawdz_stl(p)
        assert w.powod == powod, (nazwa, w)
        assert w.rozmiar == len(dane)
        if powod is None:
            assert w.trojkaty == 40 and len(dane) == 84 + 50 * 40
        else:
            assert w.opis, nazwa  # powod zawsze z opisem dla czlowieka
        # zgodnosc z kontrola kompletnosci z "Dnia skanera" (ten sam wzor 84 + 50 x liczba trojkatow)
        kompletny = stl_binarny_kompletny(p)
        if powod in (None, "za_malo_trojkatow"):
            assert kompletny is True, nazwa
        else:
            assert kompletny is not True, nazwa
    assert SC.sprawdz_stl(tmp_path / "brak.stl").powod == "blad_odczytu"
    # progi z konstruktora: liczba trojkatow i rozmiar
    assert SC.sprawdz_stl(tmp_path / "dobry.stl", min_trojkatow=41).powod == "za_malo_trojkatow"
    assert SC.sprawdz_stl(tmp_path / "dobry.stl", min_rozmiar_mb=1.0).powod == "za_maly"
    assert set(przypadki[k][1] for k in przypadki if przypadki[k][1]) <= set(SC.POWODY)


# ----------------------------------------------------------------------------
# kryterium 1: 100 zapisow w kawalkach, 1-5 s kazdy
# ----------------------------------------------------------------------------
def test_100_zapisow_w_kawalkach(tmp_path, obserwator):
    """Kryterium 1 (S1) na parametrach DOMYSLNYCH obserwatora: 100 z 100 zdarzen, 0 przed koncem zapisu, mediana opoznienia."""
    sc, zb, folder = obserwator(stabilizacja_ms=SC.STABILIZACJA_MS, odrzuc_po_s=SC.ODRZUC_PO_S, okres_s=SC.OKRES_S, przeglad_s=SC.PRZEGLAD_S)
    zrodla = [SY.sztuczny_stl(400 + 37 * i, seed=i) for i in range(100)]  # 100 roznych zawartosci, 20-205 kB
    zapisy = SY.symuluj(folder, zrodla, ile=100, czas=(1.0, 5.0), kawalki=(5, 20), rownolegle=25, seed=11)
    assert len(zapisy) == 100
    assert zb.czekaj(lambda: len(zb.skany) >= 100, 30.0), f"zdarzen {len(zb.skany)} ze 100"
    time.sleep(1.0)  # zadnych zdarzen nadmiarowych
    st = SY.statystyki(zapisy, zb.skany, zb.odrzucone)
    print(f"\n[kryterium 1] zdarzen {st['zdarzen']} / {st['dobrych']}, przed koncem zapisu {st['przed_koncem']}, "
          f"opoznienie mediana {st['opoznienie_mediana_s']:.3f} s, p95 {st['opoznienie_p95_s']:.3f} s, max {st['opoznienie_max_s']:.3f} s "
          f"(prog testu {PROG_MEDIANY_S} s, kryterium 1,0 s)")
    assert st["zdarzen"] == 100 and st["dobrych"] == 100 and st["bez_zdarzenia"] == [] and st["nadmiarowe"] == 0
    assert st["przed_koncem"] == 0
    assert st["zly_skrot"] == 0  # sha16, rozmiar i liczba trojkatow zdarzenia = zapisany plik
    assert st["odrzucen"] == 0
    assert st["opoznienie_mediana_s"] < PROG_MEDIANY_S
    assert len({z.nr for z in zb.skany}) == 100 and [z.nr for z in zb.skany] == sorted(z.nr for z in zb.skany)


# ----------------------------------------------------------------------------
# kryterium 2: pliki zle
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("rodzaj, powod", [
    ("uciety", "rozmiar_niezgodny"),
    ("pusty", "pusty"),
    ("nie_stl", "rozmiar_niezgodny"),
    ("zly_naglowek", "rozmiar_niezgodny"),
    ("za_krotki", "za_krotki"),
    ("stl_tekstowy", "stl_tekstowy"),
    ("inne_rozszerzenie", "poza_wzorcem"),
])
def test_plik_zly_bez_zdarzenia_z_powodem(obserwator, rodzaj, powod):
    """Kryterium 2 (S2): 0 zdarzen i wpis z powodem; dobry plik zapisany potem nadal daje zdarzenie."""
    sc, zb, folder = obserwator()
    dobry = SY.sztuczny_stl(300, seed=5)
    zapisy = SY.symuluj(folder, [dobry], ile=1, czas=(0.3, 0.3), kawalki=(4, 4), zle=[rodzaj], seed=2)
    zly = [z for z in zapisy if z["rodzaj"] == rodzaj]
    assert len(zly) == 1 and len(zapisy) == 2
    assert zb.czekaj(lambda: len(zb.odrzucone) >= 1 and len(zb.skany) >= 1, 15.0), (zb.skany, zb.odrzucone)
    time.sleep(0.5)
    assert [o.powod for o in zb.odrzucone] == [powod]
    o = zb.odrzucone[0]
    assert Path(o.plik) == Path(zly[0]["plik"]) and o.opis and o.rozmiar == zly[0]["rozmiar"]
    assert [Path(z.plik) for z in zb.skany] == [Path(z["plik"]) for z in zapisy if z["rodzaj"] == "dobry"]
    assert list(sc.odrzucone)[-1].powod == powod  # wpis zostaje tez w dzienniku obserwatora
    assert sc.stan()["odrzucen"] == 1 and sc.stan()["zdarzen"] == 1


def test_plik_w_trakcie_zapisu_nie_jest_odrzucany_za_wczesnie(tmp_path):
    """Logika czasu na sztucznym zegarze (bez watkow): plik niepelny czeka ``odrzuc_po_s``; po dopisaniu reszty jest zdarzenie."""
    folder = tmp_path / "eksport"
    folder.mkdir()
    zegar = [1000.0]
    zb = Zbior()
    sc = SC.Scanner(folder, na_skan=zb.skan, na_odrzucenie=zb.odrzucenie, stabilizacja_ms=300, odrzuc_po_s=5.0, przeglad_s=0.0,
                    obserwator="odpytywanie", zegar=lambda: zegar[0])
    sc.przygotuj()  # stan poczatkowy bez watku
    dane = SY.sztuczny_stl(100, seed=3)
    p = folder / "a.stl"
    p.write_bytes(dane[:2000])
    for _ in range(3):
        sc.obieg()
        zegar[0] += 0.2
    assert zb.skany == [] and zb.odrzucone == []  # stabilny, ale niepelny: jeszcze nie odrzucony
    zegar[0] += 4.0
    sc.obieg()
    assert zb.odrzucone == []  # 4,6 s bez zmian < 5 s
    zegar[0] += 1.0
    sc.obieg()
    assert [o.powod for o in zb.odrzucone] == ["rozmiar_niezgodny"] and zb.skany == []
    # odrzucenie nie jest ostateczne: plik dopisany do konca daje zdarzenie
    p.write_bytes(dane)
    sc.obieg()
    assert zb.skany == []  # dopiero co zmieniony
    zegar[0] += 0.31
    sc.obieg()
    assert len(zb.skany) == 1 and zb.skany[0].trojkaty == 100 and zb.skany[0].rozmiar == len(dane)
    assert zb.skany[0].sha16 == SY.skrot16(dane)


# ----------------------------------------------------------------------------
# kryterium 3: ponowny zapis i duplikat
# ----------------------------------------------------------------------------
def test_ponowny_zapis_i_duplikat(obserwator):
    sc, zb, folder = obserwator()
    a, b = SY.sztuczny_stl(200, seed=1), SY.sztuczny_stl(200, seed=2)
    SY.zapisz_jak_skaner(a, folder / "p1.stl", czas_s=0.2, kawalki=3)
    assert zb.czekaj(lambda: len(zb.skany) == 1)
    z1 = zb.skany[0]
    assert (z1.ponowny, z1.duplikat, z1.duplikat_z) == (False, False, None)
    # ten sam plik (ta sama zawartosc) zapisany ponownie pod ta sama nazwa = nowe zdarzenie
    time.sleep(0.05)
    SY.zapisz_jak_skaner(a, folder / "p1.stl", czas_s=0.2, kawalki=3)
    assert zb.czekaj(lambda: len(zb.skany) == 2)
    z2 = zb.skany[1]
    assert Path(z2.plik) == Path(z1.plik) and z2.sha16 == z1.sha16 and z2.ponowny is True and z2.duplikat is False and z2.nr == z1.nr + 1
    # ta sama nazwa, inna zawartosc = nowe zdarzenie z nowym skrotem
    SY.zapisz_jak_skaner(b, folder / "p1.stl", czas_s=0.2, kawalki=3)
    assert zb.czekaj(lambda: len(zb.skany) == 3)
    z3 = zb.skany[2]
    assert z3.ponowny is True and z3.duplikat is False and z3.sha16 == SY.skrot16(b) != z1.sha16
    # ta sama zawartosc pod inna nazwa = zdarzenie z flaga "duplikat" i wskazaniem pierwszego pliku
    SY.zapisz_jak_skaner(a, folder / "p2.stl", czas_s=0.2, kawalki=3)
    assert zb.czekaj(lambda: len(zb.skany) == 4)
    z4 = zb.skany[3]
    assert z4.duplikat is True and z4.ponowny is False and z4.sha16 == z1.sha16 and Path(z4.duplikat_z) == Path(z1.plik)
    time.sleep(0.6)
    assert len(zb.skany) == 4 and zb.odrzucone == []  # odczyt pliku przez obserwatora nie wywoluje kolejnych zdarzen


# ----------------------------------------------------------------------------
# kryterium 4 (czesc obserwatora): 20 plikow naraz
# ----------------------------------------------------------------------------
def kolejnosc_wg_czasu_pliku(zdarzenia, luz_s: float = 0.1) -> bool:
    """Czy zdarzenia ida w kolejnosci czasu zapisu plikow. Test nie zaklada, w jakiej kolejnosci symulator SKONCZYL zapisy
    (to zalezy od obciazenia komputera - uwaga D9 recenzji), tylko porownuje kolejnosc zdarzen z czasami plikow; pliki
    zakonczone w odstepie mniejszym niz ``luz_s`` (dwa obiegi obserwatora) moga byc zgloszone w dowolnej kolejnosci."""
    czasy = [z.mtime_ns / 1e9 for z in zdarzenia]
    return all(a <= b + luz_s for a, b in zip(czasy, czasy[1:]))


def test_20_plikow_naraz_w_kolejnosci_zapisu(obserwator):
    sc, zb, folder = obserwator()
    zrodla = [SY.sztuczny_stl(300 + i, seed=100 + i) for i in range(20)]
    # 20 zapisow rozpoczetych jednoczesnie; plan: koncza sie co 0,3 s w kolejnosci INNEJ niz kolejnosc nazw
    kolejnosc = [(7 * i) % 20 for i in range(20)]
    czasy = [0.0] * 20
    for miejsce, nr in enumerate(kolejnosc):
        czasy[nr] = 0.6 + 0.3 * miejsce
    zapisy = SY.symuluj(folder, zrodla, ile=20, czasy=czasy, kawalki=(6, 6), rownolegle=20, seed=4)
    assert zb.czekaj(lambda: len(zb.skany) >= 20, 60.0), len(zb.skany)
    time.sleep(0.5)
    assert len(zb.skany) == 20 and zb.odrzucone == []  # zadnego zgubionego, zadnego nadmiarowego
    assert sorted(Path(z.plik).name for z in zb.skany) == sorted(Path(z["plik"]).name for z in zapisy)
    assert {z.sha16 for z in zb.skany} == {z["sha16"] for z in zapisy}
    assert kolejnosc_wg_czasu_pliku(zb.skany), [(Path(z.plik).name, z.mtime_ns) for z in zb.skany]
    assert [Path(z.plik).name for z in zb.skany] != sorted(Path(z.plik).name for z in zb.skany)  # kolejnosc zapisu, nie nazw


# ----------------------------------------------------------------------------
# sposoby zapisu
# ----------------------------------------------------------------------------
@pytest.mark.skipif(os.name != "nt", reason="blokada zapisu (dzien_skanera_rdzen.ktos_pisze) dziala tylko na Windows; poza Windows decyduje sama stabilizacja")
def test_uchwyt_trzymany_po_ostatnim_kawalku(obserwator):
    """Program zapisal caly plik (rozmiar zgodny z naglowkiem), ale jeszcze trzyma go otwartego: zdarzenie dopiero po zamknieciu."""
    sc, zb, folder = obserwator()
    wynik = {}
    w = threading.Thread(target=lambda: wynik.update(SY.zapisz_jak_skaner(SY.sztuczny_stl(500, seed=9), folder / "t.stl", czas_s=0.2, kawalki=4, trzymaj_s=1.5)))
    w.start()
    time.sleep(1.2)  # caly plik jest na dysku od ok. 1 s (stabilizacja 0,15 s dawno minela), uchwyt nadal otwarty
    assert zb.skany == []
    w.join()
    assert zb.czekaj(lambda: len(zb.skany) == 1)
    assert zb.skany[0].czas_zdarzenia >= wynik["koniec"]


@pytest.mark.parametrize("tryb", ["dopisywanie", "tymczasowy"])
def test_inne_sposoby_zapisu(obserwator, tryb):
    """Zapis z zamykaniem pliku po kazdym kawalku oraz zapis do pliku tymczasowego ze zmiana nazwy: jedno zdarzenie po koncu."""
    sc, zb, folder = obserwator()
    dane = SY.sztuczny_stl(800, seed=6)
    wynik = SY.zapisz_jak_skaner(dane, folder / "x.stl", czas_s=1.5, kawalki=5, tryb=tryb)
    assert zb.czekaj(lambda: len(zb.skany) >= 1)
    time.sleep(0.8)
    assert len(zb.skany) == 1 and zb.skany[0].sha16 == SY.skrot16(dane)
    assert zb.skany[0].czas_zdarzenia >= wynik["koniec"]
    assert [o.powod for o in zb.odrzucone if Path(o.plik).suffix.lower() == ".stl"] == []


def test_podfolder_i_wzorzec(obserwator):
    """Struktura folderu zlecenia nie jest zakladana: pliki w podfolderach sa widziane, wzorzec nazwy jest parametrem."""
    sc, zb, folder = obserwator(wzorzec_pliku="plytka_*.STL")
    dane = SY.sztuczny_stl(100, seed=1)
    (folder / "zlecenie_1" / "wynik").mkdir(parents=True)
    SY.zapisz_jak_skaner(dane, folder / "zlecenie_1" / "wynik" / "Plytka_A.stl", czas_s=0.1, kawalki=2)
    SY.zapisz_jak_skaner(SY.sztuczny_stl(100, seed=2), folder / "zlecenie_1" / "inny.stl", czas_s=0.1, kawalki=2)
    assert zb.czekaj(lambda: len(zb.skany) >= 1 and len(zb.odrzucone) >= 1)
    time.sleep(0.4)
    assert [Path(z.plik).name for z in zb.skany] == ["Plytka_A.stl"]  # wzorzec bez rozrozniania wielkosci liter
    assert [(Path(o.plik).name, o.powod) for o in zb.odrzucone] == [("inny.stl", "poza_wzorcem")]


def test_bez_podfolderow(obserwator):
    sc, zb, folder = obserwator(rekurencyjnie=False)
    (folder / "pod").mkdir()
    SY.zapisz_jak_skaner(SY.sztuczny_stl(100, seed=1), folder / "pod" / "a.stl", czas_s=0.1, kawalki=2)
    SY.zapisz_jak_skaner(SY.sztuczny_stl(100, seed=2), folder / "b.stl", czas_s=0.1, kawalki=2)
    assert zb.czekaj(lambda: len(zb.skany) >= 1)
    time.sleep(0.8)
    assert [Path(z.plik).name for z in zb.skany] == ["b.stl"] and zb.odrzucone == []


# ----------------------------------------------------------------------------
# start, pliki zastane, tryb odpytywania, brak folderu
# ----------------------------------------------------------------------------
def test_pliki_zastane(tmp_path, obserwator):
    folder = tmp_path / "eksport"
    folder.mkdir()
    stary = SY.sztuczny_stl(100, seed=1)
    (folder / "stary.stl").write_bytes(stary)
    sc, zb, _ = obserwator(folder)
    SY.zapisz_jak_skaner(SY.sztuczny_stl(100, seed=2), folder / "nowy.stl", czas_s=0.1, kawalki=2)
    assert zb.czekaj(lambda: len(zb.skany) >= 1)
    time.sleep(0.8)
    assert [Path(z.plik).name for z in zb.skany] == ["nowy.stl"]  # plik zastany przy starcie nie jest nowym skanem
    # plik zastany zapisany ponownie jest juz zdarzeniem (pierwszym dla tej sciezki)
    SY.zapisz_jak_skaner(stary, folder / "stary.stl", czas_s=0.1, kawalki=2)
    assert zb.czekaj(lambda: len(zb.skany) >= 2)
    assert Path(zb.skany[1].plik).name == "stary.stl" and zb.skany[1].ponowny is False
    sc.stop()
    # z ``zglos_zastane`` pliki obecne przy starcie sa zglaszane (w kolejnosci czasu pliku)
    sc2, zb2, _ = obserwator(folder, zglos_zastane=True)
    assert zb2.czekaj(lambda: len(zb2.skany) >= 2)
    assert sorted(Path(z.plik).name for z in zb2.skany) == ["nowy.stl", "stary.stl"]
    assert [z.czas_pliku for z in zb2.skany] == sorted(z.czas_pliku for z in zb2.skany)


def test_tryb_odpytywania_bez_watchdog(obserwator):
    sc, zb, folder = obserwator(obserwator="odpytywanie", przeglad_s=0.1)
    assert sc.stan()["obserwator"] == "odpytywanie"
    dane = SY.sztuczny_stl(300, seed=8)
    wynik = SY.zapisz_jak_skaner(dane, folder / "o.stl", czas_s=0.6, kawalki=6)
    assert zb.czekaj(lambda: len(zb.skany) >= 1)
    time.sleep(0.5)
    assert len(zb.skany) == 1 and zb.skany[0].sha16 == SY.skrot16(dane) and zb.skany[0].czas_zdarzenia >= wynik["koniec"]


def test_folder_powstaje_pozniej(tmp_path, obserwator):
    folder = tmp_path / "jeszcze_nie_ma" / "eksport"
    sc, zb, _ = obserwator(folder, utworz=False)
    time.sleep(0.4)
    assert sc.dziala() and sc.stan()["folder_dostepny"] is False
    folder.mkdir(parents=True)
    time.sleep(0.8)
    SY.zapisz_jak_skaner(SY.sztuczny_stl(100, seed=1), folder / "a.stl", czas_s=0.2, kawalki=2)
    assert zb.czekaj(lambda: len(zb.skany) >= 1)
    assert sc.stan()["folder_dostepny"] is True


def test_watchdog_jest_uzywany_domyslnie(obserwator):
    """Paczka zamawia obserwacje przez watchdog; odpytywanie jest tylko siatka bezpieczenstwa."""
    sc, zb, folder = obserwator(przeglad_s=3600.0)  # przeglad okresowy praktycznie wylaczony: zdarzenie musi przyjsc z watchdog
    assert sc.stan()["obserwator"] == "watchdog"
    SY.zapisz_jak_skaner(SY.sztuczny_stl(100, seed=1), folder / "w.stl", czas_s=0.3, kawalki=3)
    assert zb.czekaj(lambda: len(zb.skany) >= 1, 10.0)


def test_kolejka_gdy_brak_funkcji_zwrotnych(tmp_path):
    folder = tmp_path / "eksport"
    folder.mkdir()
    sc = SC.Scanner(folder, **SZYBKO)
    sc.start()
    try:
        SY.zapisz_jak_skaner(SY.sztuczny_stl(100, seed=1), folder / "a.stl", czas_s=0.1, kawalki=2)
        (folder / "b.stl").write_bytes(b"")
        odebrane = [sc.zdarzenia.get(timeout=10.0), sc.zdarzenia.get(timeout=10.0)]
    finally:
        sc.stop()
    assert sorted(type(x).__name__ for x in odebrane) == ["Odrzucenie", "ZdarzenieSkanu"]
    with pytest.raises(queue.Empty):
        sc.zdarzenia.get_nowait()
    assert not sc.dziala()


def test_blad_w_funkcji_zwrotnej_nie_zatrzymuje_obserwatora(tmp_path):
    folder = tmp_path / "eksport"
    folder.mkdir()
    odebrane = []

    def na_skan(z):
        odebrane.append(z)
        if len(odebrane) == 1:
            raise RuntimeError("blad odbiorcy")

    sc = SC.Scanner(folder, na_skan=na_skan, **SZYBKO)
    sc.start()
    try:
        SY.zapisz_jak_skaner(SY.sztuczny_stl(100, seed=1), folder / "a.stl", czas_s=0.1, kawalki=2)
        SY.zapisz_jak_skaner(SY.sztuczny_stl(100, seed=2), folder / "b.stl", czas_s=0.1, kawalki=2)
        t0 = time.time()
        while len(odebrane) < 2 and time.time() - t0 < 10:
            time.sleep(0.05)
    finally:
        sc.stop()
    assert [Path(z.plik).name for z in odebrane] == ["a.stl", "b.stl"]


# ----------------------------------------------------------------------------
# akcja "start skanu" (DW5) - tylko interfejs z atrapa
# ----------------------------------------------------------------------------
def test_start_skanu_atrapa(tmp_path):
    folder = tmp_path / "eksport"
    folder.mkdir()
    sc = SC.Scanner(folder)
    assert isinstance(sc.akcja_startu, SC.AtrapaStartuSkanu)  # domyslnie atrapa: zadnego klikania w programie skanera
    assert sc.start_skanu() is True and sc.start_skanu() is True
    assert len(sc.akcja_startu.wywolania) == 2
    wlasna = []
    sc2 = SC.Scanner(folder, start_skanu=lambda: wlasna.append(1) or False)
    assert sc2.start_skanu() is False and wlasna == [1]

    def zepsuta():
        raise OSError("okno skanera nieznalezione")

    assert SC.Scanner(folder, start_skanu=zepsuta).start_skanu() is False  # wyjatek akcji = False, nie awaria programu


# ----------------------------------------------------------------------------
# runda 2 recenzji PR #17: B1 (plik zajety), P2 (nadrabianie po restarcie), P3 (pliki zastane), D1 (folder odtworzony)
# ----------------------------------------------------------------------------
WINDOWS = pytest.mark.skipif(os.name != "nt", reason="uchwyt wylaczny (plik otwarty bez zgody na wspoldzielenie) istnieje tylko na Windows")


def _reczny(folder: Path, zegar: list, **parametry):
    """Obserwator bez watku i bez watchdog, na sztucznym zegarze: test sam wola ``obieg()``."""
    zb = Zbior()
    sc = SC.Scanner(folder, na_skan=zb.skan, na_odrzucenie=zb.odrzucenie, na_oczekiwanie=zb.oczekiwanie, obserwator="odpytywanie", przeglad_s=0.0,
                    zegar=lambda: zegar[0], **parametry)
    sc.przygotuj()
    return sc, zb


def _obiegi(sc, zegar: list, ile: int, krok_s: float = 0.1) -> None:
    for _ in range(ile):
        sc.obieg()
        zegar[0] += krok_s


@WINDOWS
def test_plik_trzymany_wylacznie_4_s_daje_zdarzenie_po_zwolnieniu(obserwator):
    """B1, proby ``a`` i ``b4`` recenzenta na parametrach DOMYSLNYCH: (a) program zapisuje caly plik i trzyma go wylacznie
    jeszcze 4 s; (b) plik gotowy, potem inny program trzyma go wylacznie do ODCZYTU 4 s. Kazdy daje dokladnie 1 zdarzenie
    po zwolnieniu, zadnego odrzucenia (przed poprawka: ``blad_odczytu`` po 2,8 s i 0 zdarzen juz na zawsze)."""
    sc, zb, folder = obserwator(stabilizacja_ms=SC.STABILIZACJA_MS, odrzuc_po_s=SC.ODRZUC_PO_S, okres_s=SC.OKRES_S, przeglad_s=SC.PRZEGLAD_S)
    dane_a, dane_b = SY.sztuczny_stl(4000, seed=1), SY.sztuczny_stl(4000, seed=2)
    zapis = {}
    w = threading.Thread(target=lambda: zapis.update(SY.zapisz_jak_skaner(dane_a, folder / "a.stl", czas_s=0.2, kawalki=3, tryb="wylaczny", trzymaj_s=4.0)))
    w.start()
    (folder / "b.stl").write_bytes(dane_b)
    uchwyt = SY.otworz_wylacznie(folder / "b.stl", zapis=False)
    time.sleep(4.0)
    assert zb.skany == [] and zb.odrzucone == []  # plik zajety to nie odrzucenie
    zwolnienie_b = time.time()
    uchwyt.close()
    w.join()
    assert zb.czekaj(lambda: len(zb.skany) >= 2, 15.0), (zb.skany, zb.odrzucone)
    time.sleep(2 * SC.PRZEGLAD_S + 0.5)  # dwa pelne przeglady folderu: nic nadmiarowego
    zd = {Path(z.plik).name: z for z in zb.skany}
    assert sorted(zd) == ["a.stl", "b.stl"] and len(zb.skany) == 2 and zb.odrzucone == []
    assert zd["a.stl"].sha16 == SY.skrot16(dane_a) and zd["b.stl"].sha16 == SY.skrot16(dane_b)
    assert zd["a.stl"].czas_zdarzenia >= zapis["koniec"] and zd["b.stl"].czas_zdarzenia >= zwolnienie_b
    assert sc.stan()["zajete"] == 0


@WINDOWS
@pytest.mark.parametrize("wariant", ["zapis", "odczyt"])
def test_plik_trzymany_wylacznie_30_s_czeka_bez_limitu(tmp_path, wariant):
    """B1: 30 s (sztuczny zegar, prawdziwy uchwyt wylaczny) - zero odrzucen, informacja "czeka na zwolnienie pliku" po 10 s
    (powtarzana rzadko), po zwolnieniu dokladnie 1 zdarzenie."""
    folder = tmp_path / "eksport"
    folder.mkdir()
    zegar = [5000.0]
    sc, zb = _reczny(folder, zegar)
    dane = SY.sztuczny_stl(600, seed=7)
    p = folder / "zajety.stl"
    if wariant == "zapis":
        uchwyt = SY.otworz_wylacznie(p, zapis=True)
        uchwyt.write(dane)
        uchwyt.flush()
    else:
        p.write_bytes(dane)
        uchwyt = SY.otworz_wylacznie(p, zapis=False)
    try:
        _obiegi(sc, zegar, 95)  # 9,5 s
        assert zb.oczekiwania == [] and zb.skany == [] and zb.odrzucone == []
        _obiegi(sc, zegar, 205)  # razem 30 s
        assert zb.skany == [] and zb.odrzucone == []
        assert len(zb.oczekiwania) == 1  # jedna informacja po 10 s, nastepna dopiero po minucie
        o = zb.oczekiwania[0]
        assert Path(o.plik) == p and 10.0 <= o.od_s < 13.0 and o.opis
        assert sc.stan()["zajete"] == 1 and sc.stan()["czeka"] == 1
        _obiegi(sc, zegar, 450)  # do 75 s: druga informacja
        assert len(zb.oczekiwania) == 2 and zb.skany == [] and zb.odrzucone == []
    finally:
        uchwyt.close()
    _obiegi(sc, zegar, 40)  # 4 s po zwolnieniu (odstep ponawiania najwyzej 2 s)
    assert len(zb.skany) == 1 and zb.skany[0].sha16 == SY.skrot16(dane) and zb.skany[0].trojkaty == 600
    _obiegi(sc, zegar, 40)
    assert len(zb.skany) == 1 and zb.odrzucone == [] and sc.stan()["zajete"] == 0


def test_nadrabianie_po_restarcie_od_czasu(tmp_path, obserwator):
    """P2 (a): ``zglos_zastane_od`` - po starcie zgloszone sa tylko pliki nowsze niz podany czas (np. czas pliku ostatniego
    skanu zapisanego w bazie), z flaga ``zastany``, w kolejnosci czasu pliku; starsze sa zastane; nowe ida zwykla droga."""
    folder = tmp_path / "eksport"
    folder.mkdir()
    teraz = time.time()
    for nazwa, wiek_s in (("stary1.stl", 7200), ("stary2.stl", 3600), ("nowszy2.stl", 60), ("nowszy1.stl", 600)):
        p = folder / nazwa
        p.write_bytes(SY.sztuczny_stl(100, seed=wiek_s))
        os.utime(p, (teraz - wiek_s, teraz - wiek_s))
    sc, zb, _ = obserwator(folder, zglos_zastane_od=teraz - 1800)
    assert zb.czekaj(lambda: len(zb.skany) >= 2)
    time.sleep(0.8)
    assert [(Path(z.plik).name, z.zastany, z.ponowny) for z in zb.skany] == [("nowszy1.stl", True, False), ("nowszy2.stl", True, False)]
    SY.zapisz_jak_skaner(SY.sztuczny_stl(100, seed=1), folder / "biezacy.stl", czas_s=0.1, kawalki=2)
    assert zb.czekaj(lambda: len(zb.skany) >= 3)
    assert Path(zb.skany[2].plik).name == "biezacy.stl" and zb.skany[2].zastany is False and zb.odrzucone == []


def test_nadrabianie_po_restarcie_funkcja_znane(tmp_path, obserwator, monkeypatch):
    """P2 (a): ``znane(sciezka, rozmiar, mtime_ns)`` - aplikacja odpowiada z bazy, czy plik byl juz przyjety; nieznane sa
    zglaszane z flaga ``zastany``. Skrot liczony tylko dla plikow zglaszanych (nie dla calej historii folderu). Tak tez
    wraca po restarcie plik, ktory przed zamknieciem programu byl zajety albo czekal w kolejce (B1, P2)."""
    folder = tmp_path / "eksport"
    (folder / "zlec").mkdir(parents=True)
    pliki = {"a.stl": folder / "a.stl", "b.stl": folder / "b.stl", "c.stl": folder / "zlec" / "c.stl"}
    for i, p in enumerate(pliki.values()):
        p.write_bytes(SY.sztuczny_stl(100 + i, seed=i))
        os.utime(p, (time.time() - 100 + i, time.time() - 100 + i))
    pytania, liczone = [], []
    prawdziwy = SC.skrot16_pliku
    monkeypatch.setattr(SC, "skrot16_pliku", lambda plik: (liczone.append(Path(plik).name), prawdziwy(plik))[1])

    def znane(sciezka, rozmiar, mtime_ns) -> bool:
        pytania.append((Path(sciezka).name, rozmiar, mtime_ns))
        return Path(sciezka).name == "a.stl"

    sc, zb, _ = obserwator(folder, znane=znane)
    assert zb.czekaj(lambda: len(zb.skany) >= 2)
    time.sleep(0.8)
    assert [(Path(z.plik).name, z.zastany) for z in zb.skany] == [("b.stl", True), ("c.stl", True)]
    assert sorted(liczone) == ["b.stl", "c.stl"]  # plik znany nie jest nawet czytany
    assert sorted(pytania) == sorted((n, p.stat().st_size, p.stat().st_mtime_ns) for n, p in pliki.items())
    sc.stop()
    # obie reguly naraz: plik musi byc nowszy niz czas ORAZ nieznany
    sc2, zb2, _ = obserwator(folder, znane=lambda *a: False, zglos_zastane_od=pliki["b.stl"].stat().st_mtime_ns / 1e9)
    assert zb2.czekaj(lambda: len(zb2.skany) >= 1)
    time.sleep(0.8)
    assert [Path(z.plik).name for z in zb2.skany] == ["c.stl"]


def test_folder_z_historia_pojawia_sie_po_starcie(tmp_path, obserwator):
    """P3 (a), proba ``e2`` recenzenta: folderu nie ma przy starcie programu, pojawia sie pozniej z 3 starymi plikami -
    przy ``zglos_zastane=False`` to nie sa nowe skany; plik zapisany potem jest."""
    stare = tmp_path / "stare"
    stare.mkdir()
    for i in range(3):
        (stare / f"stary{i}.stl").write_bytes(SY.sztuczny_stl(100 + i, seed=i))
    time.sleep(0.1)
    folder = tmp_path / "eksport"
    sc, zb, _ = obserwator(folder, utworz=False)
    time.sleep(0.7)
    os.rename(stare, folder)
    time.sleep(2.0)
    assert zb.skany == [] and zb.odrzucone == [] and sc.stan()["folder_dostepny"] is True
    SY.zapisz_jak_skaner(SY.sztuczny_stl(100, seed=9), folder / "nowy.stl", czas_s=0.2, kawalki=2)
    assert zb.czekaj(lambda: len(zb.skany) >= 1)
    time.sleep(0.8)
    assert [(Path(z.plik).name, z.zastany) for z in zb.skany] == [("nowy.stl", False)]


def test_blad_listowania_nie_zglasza_plikow_zastanych(tmp_path, monkeypatch):
    """P3 (b), proba ``e3`` recenzenta: chwilowy blad listowania folderu albo podfolderu nie kasuje wiedzy o plikach
    zastanych - po powrocie nie sa zglaszane jako nowe. Plik naprawde usuniety i zapisany znowu jest nowym skanem."""
    folder = tmp_path / "eksport"
    (folder / "zlec1").mkdir(parents=True)
    for i in range(3):
        (folder / "zlec1" / f"stary{i}.stl").write_bytes(SY.sztuczny_stl(100 + i, seed=i))
    time.sleep(0.05)
    zegar = [100.0]
    sc, zb = _reczny(folder, zegar)
    _obiegi(sc, zegar, 5)
    prawdziwa = SC.pliki_w_folderze

    def pusta_lista(korzen, pomijaj=(), niedostepne=None):  # jak w probie recenzenta: lista pusta, bledu nie widac
        return iter(())

    def podfolder_niedostepny(korzen, pomijaj=(), niedostepne=None):
        if niedostepne is not None:
            niedostepne.append(str(Path(korzen) / "zlec1"))
        return iter(())

    def folder_niedostepny(korzen, pomijaj=(), niedostepne=None):
        if niedostepne is not None:
            niedostepne.append(str(korzen))
        return iter(())

    for udawana in (pusta_lista, podfolder_niedostepny, folder_niedostepny):
        monkeypatch.setattr(SC, "pliki_w_folderze", udawana)
        _obiegi(sc, zegar, 3)
        monkeypatch.setattr(SC, "pliki_w_folderze", prawdziwa)
        _obiegi(sc, zegar, 10)
        assert zb.skany == [] and zb.odrzucone == [], udawana.__name__
    p = folder / "zlec1" / "stary0.stl"
    st, dane = p.stat(), p.read_bytes()
    p.unlink()
    _obiegi(sc, zegar, 3)
    p.write_bytes(dane)
    os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns))  # ten sam rozmiar i czas co plik zastany
    _obiegi(sc, zegar, 10)
    assert [Path(z.plik).name for z in zb.skany] == ["stary0.stl"]


def test_podfolder_niedostepny_przy_starcie(tmp_path, monkeypatch):
    """P3: podfolderu nie dalo sie wylistowac przy ustalaniu plikow zastanych - gdy staje sie dostepny, jego stare pliki
    nadal sa zastane, a nie nowe."""
    folder = tmp_path / "eksport"
    (folder / "zlec1").mkdir(parents=True)
    for i in range(2):
        (folder / "zlec1" / f"stary{i}.stl").write_bytes(SY.sztuczny_stl(100 + i, seed=i))
    (folder / "widoczny.stl").write_bytes(SY.sztuczny_stl(50, seed=5))
    time.sleep(0.05)
    prawdziwa = SC.pliki_w_folderze

    def bez_podfolderu(korzen, pomijaj=(), niedostepne=None):
        if niedostepne is not None:
            niedostepne.append(str(Path(korzen) / "zlec1"))
        return (w for w in prawdziwa(korzen, pomijaj) if not w[0].startswith("zlec1/"))

    monkeypatch.setattr(SC, "pliki_w_folderze", bez_podfolderu)
    zegar = [100.0]
    sc, zb = _reczny(folder, zegar)
    _obiegi(sc, zegar, 5)
    monkeypatch.setattr(SC, "pliki_w_folderze", prawdziwa)
    _obiegi(sc, zegar, 10)
    assert zb.skany == [] and zb.odrzucone == []
    (folder / "zlec1" / "nowy.stl").write_bytes(SY.sztuczny_stl(70, seed=6))
    _obiegi(sc, zegar, 10)
    assert [Path(z.plik).name for z in zb.skany] == ["nowy.stl"]


def test_folder_usuniety_i_odtworzony_watchdog_dziala_dalej(obserwator):
    """D1, proba ``e6`` recenzenta: po usunieciu i odtworzeniu folderu obserwator watchdog jest uruchamiany od nowa -
    zdarzenie znow przychodzi z powiadomienia, a nie dopiero z przegladu folderu."""
    import shutil

    sc, zb, folder = obserwator(przeglad_s=0.3)
    SY.zapisz_jak_skaner(SY.sztuczny_stl(100, seed=1), folder / "a.stl", czas_s=0.1, kawalki=2)
    assert zb.czekaj(lambda: len(zb.skany) >= 1)
    startow = sc.stan()["startow_watchdog"]
    shutil.rmtree(folder, ignore_errors=True)
    t0 = time.time()
    while time.time() - t0 < 15:  # katalog z otwartym uchwytem obserwatora znika dopiero po jego zamknieciu
        try:
            folder.mkdir()
            break
        except OSError:
            time.sleep(0.1)
    assert folder.is_dir()
    t0 = time.time()
    while sc.stan()["startow_watchdog"] <= startow and time.time() - t0 < 15:
        time.sleep(0.05)
    assert sc.stan()["startow_watchdog"] > startow and sc.stan()["obserwator"] == "watchdog"
    time.sleep(0.5)
    sc.przeglad_s = 3600.0  # od teraz bez przegladu okresowego: zdarzenie musi przyjsc z watchdog
    time.sleep(0.5)
    SY.zapisz_jak_skaner(SY.sztuczny_stl(100, seed=2), folder / "b.stl", czas_s=0.1, kawalki=2)
    assert zb.czekaj(lambda: len(zb.skany) >= 2, 10.0)
    assert Path(zb.skany[1].plik).name == "b.stl"


def test_stop_nie_gubi_watku_liczacego(tmp_path, monkeypatch):
    """D11 (a): gdy ``stop()`` nie doczeka sie konca watku (liczenie skrotu duzego pliku), kolejny ``start()`` nie uruchamia
    drugiego watku na tym samym stanie."""
    folder = tmp_path / "eksport"
    folder.mkdir()
    wolny = threading.Event()
    prawdziwy = SC.skrot16_pliku
    monkeypatch.setattr(SC, "skrot16_pliku", lambda plik: (wolny.wait(5.0), prawdziwy(plik))[1])
    zb = Zbior()
    sc = SC.Scanner(folder, na_skan=zb.skan, **SZYBKO)
    sc.start()
    try:
        SY.zapisz_jak_skaner(SY.sztuczny_stl(100, seed=1), folder / "a.stl", czas_s=0.1, kawalki=2)
        time.sleep(1.0)  # watek stoi w liczeniu skrotu
        sc.stop(czekaj_s=0.2)
        assert sc.dziala()  # watek jeszcze zyje - stop() tego nie ukrywa
        sc.start()
        assert sum(1 for t in threading.enumerate() if t.name == "scanner") == 1
    finally:
        wolny.set()
        sc.stop()
    assert not sc.dziala()


# ----------------------------------------------------------------------------
# symulator: wiersz polecen z pomiarem
# ----------------------------------------------------------------------------
def test_symulator_wiersz_polecen_z_pomiarem(tmp_path, capsys):
    dziennik = tmp_path / "dziennik.json"
    kod = SY.main(["--folder", str(tmp_path / "eksport"), "--ile", "6", "--czas", "0.3", "0.8", "--rownolegle", "3", "--zle", "uciety", "pusty",
                   "--seed", "5", "--pomiar", "--odrzuc-po", "0.6", "--dziennik", str(dziennik)])
    wyjscie = capsys.readouterr().out
    assert kod == 0, wyjscie
    import json

    d = json.loads(dziennik.read_text(encoding="utf-8"))
    st = d["statystyki"]
    assert st["dobrych"] == 6 and st["zdarzen"] == 6 and st["przed_koncem"] == 0 and st["zlych"] == 2 and st["odrzucen"] == 2
    assert st["zle_bez_powodu"] == [] and st["zle_ze_zdarzeniem"] == []
    assert sorted(z["rodzaj"] for z in d["zapisy"]) == ["dobry"] * 6 + ["pusty", "uciety"]
    assert "6 / 6" in wyjscie
    assert statistics.median([z["koniec"] - z["start"] for z in d["zapisy"] if z["rodzaj"] == "dobry"]) >= 0.3
