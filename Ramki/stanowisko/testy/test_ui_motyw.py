"""motyw (E3-U1a): jedno miejsce wygladu nowego okna - ``stanowisko/ui/motyw.py`` (``etap3/nowy_interfejs/SPEC.md`` p. 2).

  (1) kolory glowne ze specyfikacji (#338CED / #191919 / #303030 i pochodne),
  (2) kontrast co najmniej 4,5 : 1 dla KAZDEJ pary napis / tlo z motywu i dla napisu na kazdym kolorze statusu ze ``statusy``,
  (3) kolory statusow na ciemnym tle wg specyfikacji; w ``statusy.py`` zmienily sie TYLKO wartosci RGB ekranu (kolory diod
      ramki i napisy bez zmian),
  (4) uklady okna (progi 1500 x 860 i 1000), stale wysokosci,
  (5) arkusz: tylko kolory motywu, promienie 4 / 3 px, bez gradientow i cieni, czcionka z zapasem, wysokosci przyciskow nie
      w arkuszu; barwy nie sa wpisane w innych plikach nowego okna,
  (6) modul bez Qt na poziomie modulu.
Plik jest ASCII.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

STANOWISKO = Path(__file__).resolve().parent.parent
UI = STANOWISKO / "stanowisko" / "ui"
NOWE_PLIKI = ("czesci.py", "wieczor.py", "mapa.py", "okno.py", "obraz.py", "styl.py", "__init__.py")  # nowe okno; barwy tylko w motyw.py
HEX = re.compile(r"#[0-9a-fA-F]{6}\b")


# ----------------------------------------------------------------------------
# (1) kolory ze specyfikacji
# ----------------------------------------------------------------------------
def test_kolory_glowne_ze_specyfikacji():
    from stanowisko.ui import motyw as M

    assert (M.AKCENT, M.TLO, M.POWIERZCHNIA) == ("#338CED", "#191919", "#303030")  # trzy kolory wskazane przez wlasciciela
    assert M.WGLEBIENIE == "#242424" and M.NA_AKCENCIE == "#0F1720" and M.WYBOR_TLO == "#1D2733"
    assert (M.AKCENT_TEKST, M.AKCENT_FOKUS) == ("#9CC9F9", "#6FB0F5")
    assert (M.LINIA, M.LINIA_TLA, M.OBWODKA) == ("#3F3F3F", "#2B2B2B", "#4A4A4A")
    assert (M.TEKST, M.TEKST_POMOCNICZY, M.TEKST_PRZYGASZONY) == ("#F2F2F2", "#B8B8B8", "#9E9E9E")
    assert M.NA_STATUSIE == "#111111"
    assert M.POZIOMY["pytanie"] == (M.WYBOR_TLO, M.AKCENT)  # pytanie: tlo wybranej pozycji z obwodka akcentu
    assert M.CZCIONKI == ("Segoe UI Variable Text", "Segoe UI")
    assert (M.PROMIEN, M.PROMIEN_ZNACZNIKA, M.SIATKA, M.CEL_KLIKNIECIA) == (4, 3, (4, 8, 12, 16, 20), 44)
    assert (M.PX_POMOCNICZY, M.PX_TRESC, M.PX_PODSTAWOWY, M.PX_PRZYCISK_DECYZJI, M.PX_NUMER_PLYTKI, M.PX_NAGLOWEK_PLYTKI, M.PX_KUWETA) == (
        12, 13, 14, 15, 15, 20, 64)
    assert (M.WYSOKOSC_PASKA_GORNEGO, M.WYSOKOSC_PASKA_STANU) == (52, 32)


# ----------------------------------------------------------------------------
# (2) kontrast
# ----------------------------------------------------------------------------
def test_kontrast_wzor_wcag():
    from stanowisko.ui import motyw as M

    assert M.kontrast("#000000", "#FFFFFF") == pytest.approx(21.0)
    assert M.kontrast("#777777", "#777777") == pytest.approx(1.0)
    assert M.kontrast("#191919", "#F2F2F2") == M.kontrast("#F2F2F2", "#191919")
    assert M.kontrast("#767676", "#FFFFFF") == pytest.approx(4.54, abs=0.01)  # znana granica 4,5 : 1 na bialym


def test_kontrast_kazdej_pary_napis_tlo_z_motywu():
    """Kazda para napis / tlo uzywana w arkuszu i w rysowaniu ma kontrast co najmniej 4,5 : 1."""
    from stanowisko.ui import motyw as M

    assert M.KONTRAST_MIN == 4.5 and len(M.PARY_KONTRASTU) >= 24
    slabe = [(opis, napis, tlo, round(M.kontrast(napis, tlo), 2)) for opis, napis, tlo in M.PARY_KONTRASTU if M.kontrast(napis, tlo) < M.KONTRAST_MIN]
    assert not slabe, f"pary ponizej {M.KONTRAST_MIN} : 1: {slabe}"
    najslabsza = min(M.kontrast(napis, tlo) for _, napis, tlo in M.PARY_KONTRASTU)
    print(f"\n[motyw] par napis / tlo: {len(M.PARY_KONTRASTU)}, najmniejszy kontrast {najslabsza:.2f} : 1")
    # kazda rola napisu i kazde tlo z motywu sa w parach (nowe tlo albo napis w motywie = nowa para tutaj)
    napisy = {napis for _, napis, _ in M.PARY_KONTRASTU}
    tla = {tlo for _, _, tlo in M.PARY_KONTRASTU}
    assert {M.TEKST, M.TEKST_POMOCNICZY, M.TEKST_PRZYGASZONY, M.NA_AKCENCIE, M.AKCENT_TEKST, M.AKCENT_FOKUS} <= napisy
    assert {M.TLO, M.POWIERZCHNIA, M.WGLEBIENIE, M.WYBOR_TLO, M.SEGMENT, M.AKCENT, M.AKCENT_JASNY} | {t for t, _ in M.POZIOMY.values()} <= tla
    # tekst przygaszony tylko na tle okna, wglebieniu i tle wybranej pozycji (SPEC: nie na powierzchni #303030)
    assert {tlo for _, napis, tlo in M.PARY_KONTRASTU if napis == M.TEKST_PRZYGASZONY} == {M.TLO, M.WGLEBIENIE, M.WYBOR_TLO}


def test_napis_na_kazdym_kolorze_statusu():
    """Napis na kolorze statusu to zawsze #111111 (SPEC) i ma kontrast co najmniej 4,5 : 1 - dla KAZDEGO wiersza ``statusy``
    (wieczor i poranek); numer pustego gniazda (kolor plytki) jest jasny."""
    from stanowisko import statusy as ST
    from stanowisko.ui import motyw as M

    pary = M.pary_statusow()
    assert len(pary) == len(ST.STATUSY) + len(ST.STATUSY_RANO_WIERSZE) >= 27
    slabe = [(opis, napis, tlo, round(M.kontrast(napis, tlo), 2)) for opis, napis, tlo in pary if M.kontrast(napis, tlo) < M.KONTRAST_MIN]
    assert not slabe, f"napis na kolorze statusu ponizej {M.KONTRAST_MIN} : 1: {slabe}"
    for wiersz in tuple(ST.STATUSY.values()) + tuple(ST.STATUSY_RANO_WIERSZE.values()):
        if wiersz.klucz == "pusty":
            assert M.tekst_pustego(wiersz.hex) == M.TEKST_POMOCNICZY and wiersz.hex.upper() == M.WGLEBIENIE  # puste gniazdo = kolor plytki
        else:
            assert M.tekst_na(wiersz.hex) == M.NA_STATUSIE, wiersz.klucz
    assert M.tekst_na("#101010") == M.TEKST and M.tekst_pustego("#EDEDED") == M.NA_STATUSIE  # kolor spoza tabeli: napis czytelny, bez wyjatku


# ----------------------------------------------------------------------------
# (3) kolory statusow
# ----------------------------------------------------------------------------
KOLORY_SPEC = {"zielony": "#3FB46A", "czerwony": "#E5484D", "ukruszona": "#E5484D", "zolty": "#E2B93B", "zatwierdzona_ok": "#2BA89A",
               "szary": "#8C8C8C", "pomaranczowy": "#E8833A", "dofrezowany": "#F0B429", "podwojny": "#A678D9"}
# kolory diod ramki i napisy ze ``statusy.py`` sprzed paczki (main b856b9e) - paczka E3-U1a nie moze ich zmienic
DIODY_I_NAPISY = {
    "zielony": ("zielony", "OK"), "czerwony": ("czerwony", "UBYTEK"), "ukruszona": ("czerwony", "UKRUSZONA"),
    "zatwierdzona_ok": ("zielony", "OK \u2014 zatwierdzona"), "zolty": ("zolty", "sprawd\u017a"),
    "sprawdz_ulozenie": ("zolty", "sprawd\u017a u\u0142o\u017cenie"), "popraw_ulozenie": ("zolty", "popraw u\u0142o\u017cenie"),
    "skan_ponownie": ("zolty", "skan poruszony"), "skan_do_powtorzenia": ("zolty", "powt\u00f3rz skan"), "nie_sprawdzono": ("zolty", "nie sprawdzono"),
    "blad_inspekcji": ("zolty", "b\u0142\u0105d kontroli"), "szary": ("bialy", "bez projektu"), "pomaranczowy": ("zolty", "poprawiana r\u0119cznie"),
    "dofrezowany": ("bursztyn", "z\u0105b dofrezowany"), "nieznana_rano": ("bialy", "nieznana"), "pusty": (None, ""),
    "podwojny": ("zolty", "dwie prace"), "poza_gniazdem": (None, "poza gniazdem"), "czeka_na_numer": (None, "podaj nr p\u0142ytki"),
    "plytka_nie_z_trybu": (None, "zablokowana"), "nieaktywny": (None, "skan nieaktualny"), "nieznany": ("zolty", "sprawd\u017a"),
    "rano_pewna": ("zielony", "rozpoznana"), "rano_przypisana": ("zielony", "przypisana"), "rano_dwuznaczna": ("zolty", "wybierz"),
    "rano_konflikt": ("czerwony", "konflikt"), "rano_juz_rozpoznany": ("bursztyn", "z\u0105b ju\u017c rozpoznany"),
}


def test_kolory_statusow_na_ciemnym_tle_wg_specyfikacji():
    from stanowisko import statusy as ST

    wiersze = {**ST.STATUSY, **ST.STATUSY_RANO_WIERSZE}
    for klucz, kolor in KOLORY_SPEC.items():
        assert wiersze[klucz].hex.upper() == kolor, klucz
    # poranek: te same barwy co wieczorem dla tej samej klasy koloru
    assert wiersze["rano_pewna"].hex == wiersze["rano_przypisana"].hex == wiersze["zielony"].hex
    assert wiersze["rano_dwuznaczna"].hex == wiersze["zolty"].hex and wiersze["rano_konflikt"].hex == wiersze["czerwony"].hex
    assert wiersze["rano_juz_rozpoznany"].hex == wiersze["dofrezowany"].hex != wiersze["pomaranczowy"].hex  # Z9
    assert wiersze["zatwierdzona_ok"].hex != wiersze["zielony"].hex
    # statusy rozrozniane barwa w obrebie mapy: kolory roznych znaczen sa rozne
    rozne = ("zielony", "czerwony", "zolty", "zatwierdzona_ok", "szary", "pomaranczowy", "dofrezowany", "podwojny", "poza_gniazdem", "czeka_na_numer",
             "plytka_nie_z_trybu", "nieaktywny", "blad_inspekcji", "nieznana_rano", "pusty")
    assert len({wiersze[k].hex for k in rozne}) == len(rozne)


def test_statusy_zmienione_tylko_rgb_ekranu():
    """Kolory diod ramki (pole ``ramka``), napisy i zestaw wierszy ``statusy`` - jak przed paczka."""
    from stanowisko import statusy as ST

    wiersze = {**ST.STATUSY, **ST.STATUSY_RANO_WIERSZE}
    assert set(wiersze) == set(DIODY_I_NAPISY)
    for klucz, (dioda, napis) in DIODY_I_NAPISY.items():
        assert (wiersze[klucz].ramka, wiersze[klucz].napis) == (dioda, napis), klucz
    assert ST.STATUSY_ZIELONE == ("zielony",) and ST.status("cos_nowego").klucz == "nieznany"


# ----------------------------------------------------------------------------
# (4) uklady okna
# ----------------------------------------------------------------------------
def test_uklad_dla_progi_i_stale_wysokosci():
    from stanowisko.ui import motyw as M

    assert M.PROG_ZWARTEGO == (1500, 860) and M.MINIMUM_OKNA == (1240, 640)
    assert M.uklad_dla(1920, 1080) is M.UKLAD_WYSOKI and M.uklad_dla(1920, 1001) is M.UKLAD_WYSOKI
    assert M.uklad_dla(1536, 864) is M.UKLAD_ZWYKLY and M.uklad_dla(1600, 900) is M.UKLAD_ZWYKLY and M.uklad_dla(1500, 860) is M.UKLAD_ZWYKLY
    for rozmiar in ((1499, 1080), (1920, 859), (1536, 784), (1366, 768), (1280, 720), (1280, 642), M.MINIMUM_OKNA):
        assert M.uklad_dla(*rozmiar) is M.UKLAD_ZWARTY, rozmiar
    for u in (M.UKLAD_WYSOKI, M.UKLAD_ZWYKLY):
        assert (u.lewa, u.prawa, u.zwarty) == (280, 360, False) and 340 <= u.prawa <= 360
    z = M.UKLAD_ZWARTY
    assert (z.lewa, z.prawa, z.odstep, z.bok, z.zwarty) == (240, 320, 12, 12, True)  # SPEC: ponizej 1500 px kolumny 240 / 320, odstepy 12
    for u in (M.UKLAD_WYSOKI, M.UKLAD_ZWYKLY, M.UKLAD_ZWARTY):
        assert u.odstep in M.SIATKA and u.bok in M.SIATKA
        assert u.decyzja >= 48 and u.przycisk >= M.CEL_KLIKNIECIA
        assert u.lista == u.naglowek_listy + u.naglowek_tabeli + u.wiersze_listy * u.wiersz_tabeli + u.odstep and u.wiersze_listy >= 2
    # najmniejsze okno miesci stale czesci srodka i najmniejsza mape
    wolne = M.MINIMUM_OKNA[1] - M.WYSOKOSC_PASKA_GORNEGO - M.WYSOKOSC_PASKA_STANU
    assert z.strefa + z.naglowek + z.lista + z.mapa_min[1] + 12 <= wolne
    assert z.lewa + z.prawa + z.mapa_min[0] + z.boczny + z.odstep + 2 * z.bok <= M.MINIMUM_OKNA[0]


# ----------------------------------------------------------------------------
# (5) arkusz i barwy tylko w motywie
# ----------------------------------------------------------------------------
def kolory_motywu() -> set:
    from stanowisko.ui import motyw as M

    stale = {v.upper() for k, v in vars(M).items() if k.isupper() and isinstance(v, str) and HEX.fullmatch(v)}
    return stale | {x.upper() for para in M.POZIOMY.values() for x in para}


@pytest.mark.parametrize("uklad", ["UKLAD_WYSOKI", "UKLAD_ZWYKLY", "UKLAD_ZWARTY"])
def test_arkusz_tylko_kolory_motywu_bez_gradientow_i_cieni(uklad):
    from stanowisko.ui import motyw as M

    arkusz = M.arkusz(getattr(M, uklad))
    obce = {k.upper() for k in HEX.findall(arkusz)} - kolory_motywu()
    assert not obce, f"kolory spoza stalych motywu w arkuszu: {sorted(obce)}"
    for zakazane in ("gradient", "shadow", "rgba(", "image:", "url("):
        assert zakazane not in arkusz.lower(), zakazane
    promienie = {int(x) for x in re.findall(r"border(?:-[a-z]+)*-radius: (\d+)px", arkusz)}
    assert promienie <= {0, M.PROMIEN_ZNACZNIKA, M.PROMIEN} and M.PROMIEN in promienie  # promien 4 px, znaczniki 3 px (0 = srodek przelacznika)
    assert '"Segoe UI Variable Text", "Segoe UI"' in arkusz  # czcionka z zapasem
    grubosci = {int(x) for x in re.findall(r"border(?:-(?:top|bottom|left|right))?: (\d+)px", arkusz)}
    assert grubosci <= {1, 2}  # obwodki 1 px; 2 px tylko fokus klawiatury
    assert "border-left: " not in arkusz or "border-left: 1px" in arkusz  # bez kolorowych paskow z lewej strony kafelka


def test_arkusz_nie_ustawia_wysokosci_przyciskow():
    """Wlasciwosc ``min-height`` w regule przycisku nadpisywalaby ``setMinimumHeight`` przy kazdym odswiezeniu stylu (blad
    znaleziony w tej paczce: przyciski decyzji 36 px zamiast 52) - wysokosci przyciskow sa w kodzie (``motyw.WYSOKOSCI``)."""
    from stanowisko.ui import motyw as M

    arkusz = M.arkusz(M.UKLAD_WYSOKI)
    reguly = re.findall(r"^QPushButton[^{]*\{\{?[^}]*\}", arkusz, re.M)
    assert len(reguly) >= 30
    for regula in reguly:
        assert "min-height" not in regula and "max-height" not in regula and "min-width" not in regula, regula
    assert M.WYSOKOSCI["stan"] <= 24 and M.WYSOKOSCI["osoba"] >= 40 and M.WYSOKOSC_PRZYCISKU >= 36


@pytest.mark.parametrize("plik", NOWE_PLIKI)
def test_barwy_sa_tylko_w_motywie(plik):
    """Zaden plik nowego okna poza ``motyw.py`` nie wpisuje wlasnej barwy ``#rrggbb`` (pliki ekranu porannego - etap U1b)."""
    tekst = (UI / plik).read_text(encoding="utf-8")
    assert not HEX.findall(tekst), f"{plik}: barwy poza motywem: {sorted(set(HEX.findall(tekst)))}"


def test_bez_okien_modalnych_cieni_i_emoji_w_plikach_okna():
    """Wymagania techniczne SPEC: zadnych okien modalnych, cieni, gradientow, emoji - w kodzie i w napisach nowego okna."""
    for plik in ("czesci.py", "wieczor.py", "mapa.py", "okno.py", "motyw.py"):
        tekst = (UI / plik).read_text(encoding="utf-8")
        for zakazane in ("QDialog", "QMessageBox", "QInputDialog", ".exec(", "QMenu", "setModal", "ApplicationModal", "WindowModal",
                         "QGraphicsDropShadowEffect", "QLinearGradient", "QRadialGradient", "QConicalGradient", "qlineargradient"):
            assert zakazane not in tekst, (plik, zakazane)
    for plik in ("napisy.py", "motyw.py", "czesci.py", "wieczor.py", "okno.py", "mapa.py"):
        tekst = (UI / plik).read_text(encoding="utf-8")
        emoji = [z for z in tekst if ord(z) >= 0x1F000 or 0x2600 <= ord(z) <= 0x27BF or 0x2190 <= ord(z) <= 0x21FF]
        assert not emoji, (plik, sorted(set(emoji)))


# ----------------------------------------------------------------------------
# (6) modul bez Qt; czcionka do rysowania
# ----------------------------------------------------------------------------
def test_motyw_bez_qt_na_poziomie_modulu():
    kod = ("import sys; import stanowisko.ui.motyw as M; M.arkusz(M.UKLAD_ZWARTY); M.pary_statusow(); "
           "print(any(m.startswith('PySide6') for m in sys.modules))")
    wynik = subprocess.run([sys.executable, "-c", kod], capture_output=True, text=True, cwd=str(STANOWISKO), timeout=120)
    assert wynik.stdout.strip() == "False", wynik.stdout + wynik.stderr


def test_czcionka_do_rysowania_ma_rodzine_zapasowa():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QApplication

    from stanowisko.ui import motyw as M

    app = QApplication.instance() or QApplication([])
    assert app is not None
    f = M.czcionka(15, True)
    assert f.families() == list(M.CZCIONKI) and f.pixelSize() == 15 and f.weight() == QFont.Weight.DemiBold
    assert M.czcionka(3).pixelSize() == 7 and M.czcionka(13).weight() == QFont.Weight.Normal
