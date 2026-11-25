"""E3-I1: okno instalatora (``instalacja/okno_instalatora.py``) i jego logika (``instalacja/kreator.py``) - bez ekranu.

Okno: przejscie 4 krokow (Foldery -> Osoby -> Instalacja -> Gotowe) z atrapa instalatora, walidacje (brak folderu, brak
osoby, za malo miejsca), blad instalatora jako zdanie po polsku, aktualizacja (ustawienia z pliku, bez zmian). Logika:
zdanie dla KAZDEGO kodu instalatora, polecenie instalatora, tryb bez okna na prawdziwej malej paczce (prawdziwy instalator,
``python -m venv`` i pip z jednym kolem - jak ``test_zainstaluj_cmd_prawdziwe_srodowisko_i_skrypty``).
"""
from __future__ import annotations

import os
import sys
import time
import tomllib
from pathlib import Path

import pytest

from instalacja import instalator as I
from instalacja import kreator as K
from instalacja import napisy_instalatora as N
from test_zbuduj_wydanie import STANOWISKO, zbuduj_paczke

O = pytest.importorskip("instalacja.okno_instalatora")


@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def foldery(tmp_path) -> dict:
    (tmp_path / "Skany").mkdir()
    (tmp_path / "Projekty").mkdir()
    return {"skany": str(tmp_path / "Skany"), "projekty": str(tmp_path / "Projekty"), "katalog": str(tmp_path / "Stanowisko")}


WIERSZE_UDANE = ["[1/9] Sumy SHA-256 paczki (P)...", "      zgodne 10 z 10", "[2/9] Python 3.12 z paczki...", "[3/9] Katalog instalacji K...",
                 "[4/9] Ustawienia...", "      zalozono ustawienia.toml ze wzoru z wyborem z okna instalatora: foldery pracy, osoby: 2; "
                 "ramki wylaczone ([ramki] wlaczone = false)", "[5/9] Katalog wersji 1.0...", "[6/9] Kopia bazy...", "[7/9] Samokontrola wersji 1.0...",
                 "      SAMOKONTROLA: ZIELONA (ok 5, ostrzezenia 1)", "[8/9] Przelaczenie wersji biezacej...", "[9/9] Ikony na pulpicie...",
                 "SKROT ZALOZONY: Stanowisko | C:\\pulpit\\Stanowisko.lnk", "SKROT NIEUDANY: Dzie\u0144 skanera | C:\\K\\Dzien_skanera.cmd",
                 "INSTALACJA: GOTOWA - wersja biezaca 1.0 (poprzednia: brak). Uruchamianie: K\\Stanowisko.cmd"]


class AtrapaInstalatora:
    """Zamiast procesu instalatora: zapamietuje polecenie, podaje gotowe wiersze, zwraca kod."""

    def __init__(self, wiersze: list[str], kod: int):
        self.wiersze, self.kod, self.polecenia = wiersze, kod, []

    def __call__(self, polecenie, na_wiersz, przerwij):
        self.polecenia.append(polecenie)
        for w in self.wiersze:
            na_wiersz(w)
        return self.kod


def czekaj_na_koniec(app, okno, limit_s: float = 30) -> None:
    koniec = time.monotonic() + limit_s
    while okno.kod is None and time.monotonic() < koniec:
        app.processEvents()
        time.sleep(0.01)
    app.processEvents()
    assert okno.kod is not None, "instalacja nie skonczyla sie"


def okno_z_paczka(tmp_path, app, atrapa, **opcje):
    paczka = zbuduj_paczke(tmp_path, "1.0")
    okno = O.OknoInstalatora(paczka, uruchom=atrapa, start_programu=opcje.pop("start", lambda katalog, cel: True), **opcje)
    return okno, paczka


# ----------------------------------------------------------------------------------------------------------- kreator

def test_kazdy_kod_instalatora_ma_zdanie_po_polsku():
    kody = sorted({v for k, v in vars(I).items() if k.startswith("KOD_") and isinstance(v, int)})
    assert kody == list(range(12))  # 0..11: tabela kodow opisy_modulow/instalacja.md
    for kod in kody:
        zdanie = K.zdanie_kodu(kod)
        assert zdanie == N.ZDANIA_KODOW[kod] and zdanie.endswith(".") and len(zdanie) > 20, kod
    assert len(set(N.ZDANIA_KODOW.values())) == len(N.ZDANIA_KODOW)  # kazdy kod inne zdanie
    assert K.zdanie_kodu(77) == N.ZDANIE_NIEZNANEGO_KODU.format(kod=77) and "77" in K.zdanie_kodu(77)
    assert set(N.ZDANIA_KODOW) == set(kody)


def test_walidacja_folderow(tmp_path, foldery, monkeypatch):
    dobry = K.Wybor(foldery["skany"], foldery["projekty"], foldery["katalog"], ["A"])
    assert K.sprawdz_foldery(dobry, 100) == ([], [])
    assert K.sprawdz_foldery(K.Wybor("", "", foldery["katalog"]), 100)[0] == [N.BRAK_SKANOW]
    bledy, _ = K.sprawdz_foldery(K.Wybor(str(tmp_path / "nie_ma"), str(tmp_path / "nie_ma_tez"), foldery["katalog"]), 100)
    assert bledy == [N.SKANY_NIE_ISTNIEJE.format(sciezka=tmp_path / "nie_ma"), N.PROJEKTY_NIE_ISTNIEJE.format(sciezka=tmp_path / "nie_ma_tez")]
    bledy, uwagi = K.sprawdz_foldery(K.Wybor(foldery["skany"], "", foldery["katalog"]), 100)  # projekty niewybrane: uwaga, nie blad
    assert bledy == [] and uwagi == [N.PROJEKTY_PUSTE.format(sciezka=Path(foldery["katalog"]) / "dane" / "projekty")]
    for katalog, blad in (("", N.BRAK_CELU), ("Stanowisko", N.CEL_WZGLEDNY), ("C:Stanowisko", N.CEL_WZGLEDNY),
                          (str(tmp_path / "a;b"), N.CEL_SREDNIK)):
        assert K.sprawdz_foldery(K.Wybor(foldery["skany"], "", katalog), 100)[0] == [blad], katalog
    (tmp_path / "plik").write_text("x", encoding="ascii")
    assert K.sprawdz_foldery(K.Wybor(foldery["skany"], "", str(tmp_path / "plik")), 100)[0] == [N.CEL_PLIK.format(sciezka=tmp_path / "plik")]
    monkeypatch.setenv("OneDrive", str(tmp_path))
    assert K.sprawdz_foldery(dobry, 100)[0] == [N.CEL_SYNCHRONIZOWANY]
    monkeypatch.delenv("OneDrive")
    wolne = K.wolne_mb(foldery["katalog"])  # katalog jeszcze nie istnieje: dysk najblizszego istniejacego katalogu
    assert wolne is not None and wolne > 0
    bledy, _ = K.sprawdz_foldery(dobry, wolne + 10_000)
    assert len(bledy) == 1 and bledy[0].startswith("Za ma\u0142o miejsca na dysku: potrzeba ") and "GB" in bledy[0]


def test_walidacja_osob():
    assert K.sprawdz_osoby([]) == [N.BRAK_OSOB] and K.sprawdz_osoby(["  "]) == [N.BRAK_OSOB]
    assert K.sprawdz_osoby(["Anna", "\u0141ukasz \u017b."]) == []
    assert K.sprawdz_osobe("anna", ["Anna"]) == N.OSOBA_POWTORZONA.format(osoba="anna")
    assert K.sprawdz_osobe("", []) == N.OSOBA_PUSTA and K.sprawdz_osobe("a\tb", []) == N.OSOBA_ZNAKI
    assert K.sprawdz_osobe("x" * 41, []) == N.OSOBA_ZA_DLUGA.format(n=40) and K.sprawdz_osobe("x" * 40, []) is None


def test_postep_czyta_wiersze_instalatora():
    p = K.Postep()
    for w in WIERSZE_UDANE[:7]:
        p.wiersz(w)
    assert p.krok == 5 and p.ramki_wylaczone and p.bledy == [] and p.koncowy == ""
    for w in WIERSZE_UDANE[7:] + ["BLAD: cos", "CO ZROBIC: zrob to"]:
        p.wiersz(w)
    assert p.krok == 9 and p.koncowy.startswith("INSTALACJA: GOTOWA") and p.bledy == ["cos"] and p.rady == ["zrob to"]
    assert p.skroty == {"Stanowisko": (True, "C:\\pulpit\\Stanowisko.lnk"), "Dzie\u0144 skanera": (False, "C:\\K\\Dzien_skanera.cmd")}


def test_polecenie_instalacji(tmp_path, foldery):
    paczka = tmp_path / "paczka"
    (paczka / "program" / "instalacja").mkdir(parents=True)
    wybor = K.Wybor(foldery["skany"], "", foldery["katalog"], ["Anna", " ", "Piotr"])
    p = K.polecenie_instalacji(paczka, wybor, False, Path(sys.executable))
    assert p[1:7] == ["-I", "-B", "-X", "utf8", str(paczka / "program" / "instalacja" / "instalator.py"), "zainstaluj"]
    assert p[p.index("--python") + 1] == str(K.python_konsolowy(Path(sys.executable))) and "--python-z-paczki" not in p
    assert p[p.index("--folder-skanow") + 1] == foldery["skany"] and p[p.index("--folder-projektow") + 1] == ""
    assert [p[i + 1] for i, a in enumerate(p) if a == "--osoba"] == ["Anna", "Piotr"]
    assert {"--skrot", "--bez-sieci", "--bez-pauzy", "--ramki-wylaczone"} <= set(p)
    # paczka z Pythonem: instalator rusza Pythonem paczki (konsolowy python.exe - procesy potomne bez okien) i go kopiuje
    (paczka / "python").mkdir()
    (paczka / "python" / "python.exe").write_bytes(b"x")
    p = K.polecenie_instalacji(paczka, wybor, True, None, tmp_path / "pulpit")
    assert p[0] == str(paczka / "python" / "python.exe") and "--python-z-paczki" in p and "--python" not in p
    assert "--folder-skanow" not in p and "--osoba" not in p and "--ramki-wylaczone" not in p  # aktualizacja: ustawienia zostaja
    assert p[p.index("--skrot-katalog") + 1] == str(tmp_path / "pulpit")
    pythonw = tmp_path / "py" / "pythonw.exe"
    pythonw.parent.mkdir()
    pythonw.write_bytes(b"")
    (tmp_path / "py" / "python.exe").write_bytes(b"")
    assert K.python_konsolowy(pythonw) == tmp_path / "py" / "python.exe"


# ------------------------------------------------------------------------------------------------------------- okno

def test_okno_cztery_kroki(tmp_path, app, foldery):
    atrapa = AtrapaInstalatora(WIERSZE_UDANE, 0)
    starty = []
    okno, paczka = okno_z_paczka(tmp_path, app, atrapa, katalog=foldery["katalog"], skrot_katalog=tmp_path / "pulpit",
                                 start=lambda katalog, cel: starty.append((katalog, cel)) or True)
    assert okno.krok == 0 and okno.przycisk_dalej.text() == N.DALEJ and okno.pole_celu.text() == foldery["katalog"]
    assert okno.info["wersja"] == "1.0" and okno.info["potrzebne_mb"] > 0 and okno.napis_miejsca.text().startswith("Potrzeba ")
    okno.pole_skanow.setText(foldery["skany"])
    okno.pole_projektow.setText(foldery["projekty"])
    okno.dalej()
    assert okno.krok == 1 and okno.przycisk_dalej.text() == N.INSTALUJ and okno.przycisk_wstecz.isVisible() is not None
    for imie in ("Anna Kowalska", "Piotr W."):
        okno.pole_osoby.setText(imie)
        assert okno.dodaj_osobe()
    okno.pole_osoby.setText("Ktos do usuniecia")
    okno.dodaj_osobe()
    okno.lista_osob.setCurrentRow(2)
    okno.usun_osobe()
    assert [okno.lista_osob.item(i).text() for i in range(okno.lista_osob.count())] == ["Anna Kowalska", "Piotr W."]
    okno.dalej()  # Instaluj
    assert okno.krok == 2 and not okno.przycisk_dalej.isEnabled()
    czekaj_na_koniec(app, okno)
    assert okno.kod == 0 and okno.krok == 3
    polecenie = atrapa.polecenia[0]
    assert polecenie[polecenie.index("--folder-skanow") + 1] == foldery["skany"]
    assert polecenie[polecenie.index("--katalog") + 1] == foldery["katalog"]
    assert [polecenie[i + 1] for i, a in enumerate(polecenie) if a == "--osoba"] == ["Anna Kowalska", "Piotr W."]
    assert polecenie[polecenie.index("--skrot-katalog") + 1] == str(tmp_path / "pulpit")
    # krok 4: opis, ikony (zalozona i nieudana - wtedy plik do klikniecia), ramki wylaczone, start programu
    assert okno.opis_gotowe.text() == N.GOTOWE_OPIS.format(wersja="1.0", katalog=Path(foldery["katalog"]))
    assert N.IKONY_SA.format(ikony="\u201eStanowisko\u201d") in okno.komunikat_ikon.text()
    assert N.IKONA_BRAK.format(nazwa="Dzie\u0144 skanera", plik="Dzien_skanera.cmd") in okno.komunikat_ikon.text()
    assert okno.komunikat_ramek.text() == N.RAMKI_WYLACZONE
    assert okno.szczegoly.toPlainText().splitlines() == WIERSZE_UDANE
    assert [s.text() for _, s in okno._stany_krokow] == [N.STAN_GOTOWE] * 9
    assert okno.uruchom_program("stanowisko") and starty == [(Path(foldery["katalog"]), "stanowisko")]
    okno.close()


def test_okno_walidacje(tmp_path, app, foldery):
    atrapa = AtrapaInstalatora(WIERSZE_UDANE, 0)
    okno, _ = okno_z_paczka(tmp_path, app, atrapa, katalog=foldery["katalog"])
    okno.dalej()  # brak folderu skanow
    assert okno.krok == 0 and okno.komunikat_folderow.text() == N.BRAK_SKANOW and okno.komunikat_folderow.isVisibleTo(okno)
    okno.pole_skanow.setText(str(tmp_path / "nie_ma"))
    okno.dalej()
    assert okno.krok == 0 and okno.komunikat_folderow.text() == N.SKANY_NIE_ISTNIEJE.format(sciezka=tmp_path / "nie_ma")
    # za malo miejsca
    okno.pole_skanow.setText(foldery["skany"])
    okno.info["potrzebne_mb"] = K.wolne_mb(foldery["katalog"]) + 50_000
    okno.dalej()
    assert okno.krok == 0 and okno.komunikat_folderow.text().startswith("Za ma\u0142o miejsca na dysku")
    okno.info["potrzebne_mb"] = 1
    # folder projektow niewybrany: najpierw uwaga (zolta), drugie "Dalej" przechodzi
    okno.dalej()
    assert okno.krok == 0 and okno.komunikat_folderow.text().startswith("Nie wybrano folderu z projektami")
    assert okno.pole_projektow.property("brak") is True
    okno.dalej()
    assert okno.krok == 1
    # brak osoby
    okno.dalej()
    assert okno.krok == 1 and okno.komunikat_osob.text() == N.BRAK_OSOB and atrapa.polecenia == []
    okno.pole_osoby.setText("Anna")
    okno.dodaj_osobe()
    okno.pole_osoby.setText("ANNA")
    assert not okno.dodaj_osobe() and okno.komunikat_osob.text() == N.OSOBA_POWTORZONA.format(osoba="ANNA")
    okno.wstecz()
    assert okno.krok == 0
    okno.close()


def test_okno_blad_instalatora_po_polsku_i_ponowna_proba(tmp_path, app, foldery):
    wiersze = WIERSZE_UDANE[:7] + ["BLAD: za malo miejsca na dysku: potrzeba ok. 2000 MB, wolne 100 MB",
                                   "CO ZROBIC: Zwolnij miejsce albo wybierz inny dysk (/katalog) i uruchom zainstaluj.cmd ponownie.",
                                   "INSTALACJA: NIEUDANA (kod 6) - wersja biezaca bez zmian: brak"]
    atrapa = AtrapaInstalatora(wiersze, I.KOD_INSTALACJA)
    okno, _ = okno_z_paczka(tmp_path, app, atrapa, katalog=foldery["katalog"])
    okno.ustaw_wybor(K.Wybor(foldery["skany"], foldery["projekty"], foldery["katalog"], ["Anna"]))
    okno.dalej()
    okno.dalej()
    czekaj_na_koniec(app, okno)
    assert okno.kod == 6 and okno.krok == 2
    tekst = okno.komunikat_instalacji.text()
    assert tekst.startswith(N.ZDANIA_KODOW[6]) and "za malo miejsca na dysku" in tekst and "Co zrobi\u0107: Zwolnij miejsce" in tekst
    assert N.DZIENNIK.format(plik=Path(foldery["katalog"]) / I.PLIK_DZIENNIKA) in tekst
    assert okno.tytul_instalacji.text() == N.INSTALACJA_BLAD_TYTUL and okno._stany_krokow[4][1].text() == N.STAN_BLAD
    assert okno.przycisk_wstecz.text() == N.SPROBUJ_PONOWNIE and okno.przycisk_dalej.isEnabled()
    okno.przycisk_wstecz.click()
    assert okno.krok == 0 and okno.przycisk_wstecz.text() == N.WSTECZ
    okno.close()


def test_okno_aktualizacja_zostawia_ustawienia(tmp_path, app, foldery):
    katalog = Path(foldery["katalog"])
    katalog.mkdir()
    tekst = I.ustawienia_ze_wzoru((STANOWISKO / "ustawienia.przyklad.toml").read_bytes(), katalog,
                                  {("sciezki", "folder_eksportu_skanera"): "D:/Skany", ("sesja", "operatorzy"): ["Ola", "Jan"]})
    (katalog / "ustawienia.toml").write_bytes(tekst)
    (katalog / "wersja_biezaca.txt").write_text("0.3.3\r\n", encoding="ascii")
    atrapa = AtrapaInstalatora(WIERSZE_UDANE, 0)
    okno, _ = okno_z_paczka(tmp_path, app, atrapa, katalog=str(katalog))
    assert okno.aktualizacja is not None and okno.pole_skanow.text() == "D:/Skany" and not okno.pole_skanow.isEnabled()
    assert okno.komunikat_folderow.text() == N.AKTUALIZACJA.format(wersja="0.3.3")
    okno.dalej()
    assert okno.krok == 1 and [okno.lista_osob.item(i).text() for i in range(okno.lista_osob.count())] == ["Ola", "Jan"]
    assert not okno.pole_osoby.isEnabled() and okno.podtytul_osob.text() == N.OSOBY_AKTUALIZACJA
    okno.dalej()
    czekaj_na_koniec(app, okno)
    polecenie = atrapa.polecenia[0]
    assert "--folder-skanow" not in polecenie and "--osoba" not in polecenie and polecenie[polecenie.index("--katalog") + 1] == str(katalog)
    assert (katalog / "ustawienia.toml").read_bytes() == tekst
    okno.close()


def test_zrzuty_czterech_krokow(tmp_path, app):
    pliki = O.zrzuty(zbuduj_paczke(tmp_path, "1.0"), tmp_path / "zrzuty")
    assert [p.name for p in pliki] == ["instalator_1_foldery.png", "instalator_2_osoby.png", "instalator_3_instalacja.png",
                                       "instalator_4_gotowe.png"]
    from PySide6.QtGui import QImage

    for p in pliki:
        obraz = QImage(str(p))
        assert obraz.width() >= O.SZEROKOSC and obraz.height() >= O.WYSOKOSC, p.name


# -------------------------------------------------------------------------------------------- tryb bez okna (prawdziwy)

@pytest.mark.skipif(os.name != "nt", reason="instalacja z venv i skryptami .cmd: Windows")
def test_tryb_bez_okna_prawdziwa_instalacja(tmp_path, foldery, capsys):
    """Ta sama logika co okno, bez klikniec: prawdziwy instalator (proces), prawdziwy ``python -m venv`` i pip (jedno male
    kolo), ustawienia z wyboru, ikony w katalogu testu. Blad wyboru = kod 12 i nic nie powstaje."""
    paczka = zbuduj_paczke(tmp_path, "1.0")
    katalog = Path(foldery["katalog"])
    wypisane = []
    kod = K.main_bez_okna(paczka, K.Wybor("", "", str(katalog), []), wypisz=wypisane.append)
    assert kod == K.KOD_WYBOR == 12 and not katalog.exists()
    assert wypisane[-1] == N.ZDANIE_WYBORU.format(bledy=f"{N.BRAK_SKANOW} {N.BRAK_OSOB}")
    wypisane.clear()
    (tmp_path / "pulpit").mkdir()
    wybor = K.Wybor(foldery["skany"], "", str(katalog), ["Anna Kowalska", "\u0141ukasz"])
    kod = K.main_bez_okna(paczka, wybor, Path(sys.executable), wypisz=wypisane.append, skrot_katalog=tmp_path / "pulpit")
    assert kod == 0, "\n".join(wypisane)
    assert wypisane[-1] == "WYNIK: " + N.ZDANIA_KODOW[0] and any(w.startswith("INSTALACJA: GOTOWA - wersja biezaca 1.0") for w in wypisane)
    ust = tomllib.loads((katalog / "ustawienia.toml").read_text(encoding="utf-8"))
    assert ust["sciezki"]["folder_eksportu_skanera"] == Path(foldery["skany"]).as_posix()
    assert ust["sciezki"]["folder_cyrkon"] == (katalog.resolve() / "dane" / "projekty").as_posix()
    assert ust["sesja"]["operatorzy"] == ["Anna Kowalska", "\u0141ukasz"]
    assert sorted(p.name for p in (tmp_path / "pulpit").iterdir()) == ["Dzie\u0144 skanera.lnk", "Stanowisko.lnk"]
    assert (katalog / I.WZOR_STARTU).is_file() and K.polecenie_startu(katalog)[-1] == "stanowisko"
    # druga proba na tym samym katalogu = aktualizacja (ustawienia zostaja; foldery i osoby nie sa podawane)
    suma = (katalog / "ustawienia.toml").read_bytes()
    wypisane.clear()
    assert K.main_bez_okna(paczka, K.Wybor("", "", str(katalog), []), Path(sys.executable), wypisz=wypisane.append,
                           skrot_katalog=tmp_path / "pulpit") == 0
    assert wypisane[0] == N.AKTUALIZACJA.format(wersja="1.0") and (katalog / "ustawienia.toml").read_bytes() == suma
