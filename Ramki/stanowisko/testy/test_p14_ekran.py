"""E3-P14: poprawki ekranu przed testami koncowymi T7 / T14 (okno offscreen na ``AtrapaKontrolera``).

* poz. 9 / D8 - przyciski decyzji ekranu porannego ("To ten projekt", "Bez projektu", "Przypisz recznie", "Cofnij wybor",
  "Rozlozona", "Cofnij", "Zamknij piec", kolejnosc kuwet) i wieczornego ("Ukruszona", "OK", "Cofnij decyzje", "Nastepna",
  "Zamknij", odpowiedzi na pytanie, "Pokaz nowy wynik") widoczne w calosci BEZ PRZEWIJANIA przy oknie 1920 x 1080 (100 %),
  1600 x 900, 1536 x 864 (125 %) i 1280 x 720 (150 %);
* N2 - nowa plytka przy niedokonczonej poprzedniej: trwaly panel "Nowy wynik czeka" z tytulem komunikatu / pytania nowej
  plytki; mapa ogladanej plytki zostaje;
* N3 - "Zamknij piec" przy pracach nierozstrzygnietych: pytanie (ile, ktore plytki i gniazda), domyslnie powrot do
  rozstrzygania; po swiadomym zamknieciu prace nazwane w osobnej grupie;
* poz. 8 - nowy skan czekajacy na odpowiedz "ponowny skan?" nie jest "sprawdzony" i rozni sie napisem od poprzedniego skanu;
* poz. 6 - przycisk na pasku mowi, ze program czeka na plik skanu (nie "Skanuj");
* poz. 1-4, 7 - napisy.
Zrzuty do raportu: zmienna ``P14_ZRZUTY`` = katalog (poza repo).
"""
from __future__ import annotations

import datetime as dt
import os
from pathlib import Path

import pytest

import test_ui_rano as UR
import test_ui_wieczor as UW
from stanowisko import statusy as ST
from stanowisko.ui import napisy as N
from stanowisko.ui import napisy_rano as NR

ROZMIARY = ((1920, 1080), (1600, 900), (1536, 864), (1280, 720))  # 100 %, okno 1600 x 900, 125 %, 150 % ekranu 1920 x 1080
RANO_KANDYDACI = ("kandydat_1_wybierz", "kandydat_2_wybierz", "praca_rano_bez_projektu", "praca_rano_przypisz", "praca_rano_zamknij")
RANO_STALE = ("rano_potwierdz_kuwete", "rano_cofnij_kuwete", "przycisk_zamknij_piec", "kolejnosc_liczba", "kolejnosc_numer",
              "rano_strona_rozkladanie", "rano_strona_wynik", "przycisk_skanuj", "przycisk_przelacz_tryb")
WIECZOR_DECYZJE = ("przycisk_ukruszona", "przycisk_ok", "przycisk_cofnij", "przycisk_nastepna", "przycisk_zamknij_prace", "przycisk_skanuj",
                   "przycisk_przelacz_tryb", "przycisk_zapisz_liste")
WIECZOR_PYTANIE = ("odp_potwierdz_ponowny_skan", "odp_odrzuc_ponowny_skan")
PROJEKTY_2 = {1: 15, 2: 16, 3: 17, 4: 18}


@pytest.fixture(scope="module", autouse=True)
def _qt():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    if UW.FONTY_WINDOWS.is_dir():
        os.environ.setdefault("QT_QPA_FONTDIR", str(UW.FONTY_WINDOWS))
    import PySide6.QtCore  # noqa: F401
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    assert app.platformName() == "offscreen"
    UW.czcionka_ekranu()
    yield app


class Swiat:
    """Atrapy kontrolera i okna jednego testu (zamykane po tescie); ``wieczor()`` / ``rano()`` -> (kontroler, zegar)."""

    def __init__(self, katalog: Path):
        self.katalog = katalog
        self.kontrolery, self.ekrany_ = [], []

    def _atrapa(self, zegar):
        from stanowisko import kontroler_api as K

        k = K.AtrapaKontrolera(self.katalog / f"atrapa_{len(self.kontrolery)}", zegar=zegar)
        self.kontrolery.append(k)
        return k

    def wieczor(self):
        zegar = UW.Zegar()
        k = self._atrapa(zegar)
        k.wybierz_operatora("Technik A")
        return k, zegar

    def rano(self):
        zegar = UR.ZegarRano()
        k = self._atrapa(zegar)
        return k, zegar

    def ekran(self, k, rozmiar: tuple = (1920, 1080)):
        e = UR.Ekran(k, rozmiar)
        self.ekrany_.append(e)
        return e

    def koniec(self) -> None:
        for e in self.ekrany_:
            e.zamknij()
        for k in self.kontrolery:
            k.zamknij()


@pytest.fixture
def swiat(tmp_path):
    s = Swiat(tmp_path)
    yield s
    s.koniec()


def zrzut(e, nazwa: str) -> None:
    """PNG okna do katalogu ``P14_ZRZUTY`` (poza repo) - tylko gdy zmienna jest ustawiona."""
    katalog = os.environ.get("P14_ZRZUTY")
    if katalog:
        Path(katalog).mkdir(parents=True, exist_ok=True)
        if not e.okno.rano():
            e.po_ochronie()  # mapa wieczorna bez przygaszenia po zmianie zawartosci
        e.obraz().save(str(Path(katalog) / f"{nazwa}.png"), "PNG")


def ustaw_rozmiar(e, rozmiar: tuple) -> None:
    e.okno.resize(*rozmiar)
    for _ in range(4):
        e.zdarzenia()
        e.odczekaj(20)


def niewidoczne_w_calosci(e, nazwy) -> list:
    """Elementy z ``nazwy``, ktorych technik NIE widzi w calosci bez przewijania (brak, ukryty, uciety przez obszar przewijany
    albo okno) - z opisem, ile widac."""
    from PySide6.QtWidgets import QWidget

    okno, wynik = e.okno, []
    e.zdarzenia()
    for nazwa in nazwy:
        w = okno.findChild(QWidget, nazwa)
        if w is None or not w.isVisibleTo(okno):
            wynik.append(f"{nazwa}: nie ma na ekranie")
            continue
        caly, widac = UW._w_oknie(okno, w), UW._widoczny_wycinek(okno, w)
        if widac != caly:
            wynik.append(f"{nazwa}: widac {widac.width()}x{widac.height()} z {caly.width()}x{caly.height()} (dol przycisku {caly.bottom()}, "
                         f"dol widocznej czesci {widac.bottom()})")
    return wynik


def poranek_t14(k, zegar) -> tuple:
    """Piec jak w probie T14: plytka 4 (zolta praca w gniezdzie 3) i plytka 5; 4 kuwety."""
    from stanowisko import kontroler_api as K

    k.przelacz_tryb("rano")
    k.wybierz_operatora("Technik A")
    K.indeks_rano_sztuczny(k.sesja.baza, k.sesja.teraz())
    p4 = k.symuluj_skan_rano(4, {1: "pewna", 2: "pewna", 3: "zolta", 4: "pewna", 5: "pewna"}, projekty={1: 307, 2: 308, 3: (309, 320), 4: 311, 5: 312})
    zegar.przesun(1)
    p5 = k.symuluj_skan_rano(5, {1: "pewna", 2: "pewna", 3: "pewna"}, projekty={1: 310, 2: 313, 3: 314})
    return p4, p5


# ----------------------------------------------------------------------------
# poz. 9 / D8: przyciski decyzji widoczne bez przewijania w 4 rozmiarach okna
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("rozmiar", ROZMIARY, ids=lambda r: f"{r[0]}x{r[1]}")
def test_poz9_rano_to_ten_projekt_i_pozostale_przyciski_widoczne_bez_przewijania(swiat, rozmiar):
    """Proba P8 recenzenta (piec T14, zolta praca) i piec pokazowy (3 plytki x 23 prace, kilkanascie kuwet): po kliknieciu
    zoltego gniazda oba "To ten projekt", "Bez projektu", "Przypisz recznie" i "Zamknij" oraz przyciski rozkladania, "Zamknij
    piec" i kolejnosci sa widoczne w calosci; po wyborze kandydata - "Cofnij wybor"; praca nieznana i konflikt - "Bez projektu"
    i "Przypisz recznie"."""
    usterki = []
    k, zegar = swiat.rano()
    p4, _ = poranek_t14(k, zegar)
    e = swiat.ekran(k, rozmiar)
    e.klik_rano(p4, 3)
    ustaw_rozmiar(e, rozmiar)
    assert (e.okno.width(), e.okno.height()) == rozmiar and e.okno.rano()
    usterki += [f"T14 zolta: {u}" for u in niewidoczne_w_calosci(e, RANO_KANDYDACI + RANO_STALE)]
    zrzut(e, f"po_p8_rano_kandydaci_{rozmiar[0]}x{rozmiar[1]}")
    e.klik("kandydat_1_wybierz")
    usterki += [f"T14 po wyborze: {u}" for u in niewidoczne_w_calosci(e, ("praca_rano_cofnij", "praca_rano_zamknij") + RANO_STALE)]

    k2, _ = swiat.rano()
    skany = k2.scenariusz_poranny()
    e2 = swiat.ekran(k2, rozmiar)
    assert len(k2.stan().rano.kuwety) >= 8
    for opis, numer, gniazdo, nazwy in (("dwuznaczna", 4, 9, RANO_KANDYDACI), ("nieznana", 5, 22, ("praca_rano_bez_projektu", "praca_rano_przypisz")),
                                        ("konflikt", 5, 3, ("praca_rano_bez_projektu", "praca_rano_przypisz", "praca_rano_zamknij"))):
        e2.klik_rano(skany[numer], gniazdo)
        ustaw_rozmiar(e2, rozmiar)
        usterki += [f"piec pokazowy, {opis}: {u}" for u in niewidoczne_w_calosci(e2, nazwy + RANO_STALE)]
        if opis == "dwuznaczna":
            zrzut(e2, f"po_poz9_rano_piec_pokazowy_{rozmiar[0]}x{rozmiar[1]}")
    assert not usterki, f"okno {rozmiar[0]} x {rozmiar[1]}:\n" + "\n".join(usterki)


@pytest.mark.parametrize("rozmiar", ROZMIARY, ids=lambda r: f"{r[0]}x{r[1]}")
def test_poz9_wieczor_przyciski_decyzji_i_pytania_widoczne_bez_przewijania(swiat, rozmiar):
    """Wieczor w tych samych 4 rozmiarach: otwarta czerwona praca (decyzje), "Pokaz nowy wynik" przy nowej plytce i odpowiedzi
    na pytanie o ponowny skan."""
    k, zegar = swiat.wieczor()
    s1 = k.symuluj_skan("zwykla", numer=1)
    e = swiat.ekran(k, rozmiar)
    e.klik_gniazdo(2)
    zegar.przesun(1)
    k.symuluj_skan("do_powtorzenia", numer=2, projekty=PROJEKTY_2)
    ustaw_rozmiar(e, rozmiar)
    assert e.okno.pokazana_plytka() == s1 and not e.okno.rano()
    usterki = [f"otwarta praca: {u}" for u in niewidoczne_w_calosci(e, WIECZOR_DECYZJE + ("przycisk_nowa_plytka", "nowy_wynik_pokaz"))]
    zegar.przesun(2)
    s3 = k.symuluj_skan("czysta", numer=2, projekty=PROJEKTY_2)
    e.klik("nowy_wynik_pokaz")
    assert e.okno.pokazana_plytka() == s3
    ustaw_rozmiar(e, rozmiar)
    usterki += [f"pytanie: {u}" for u in niewidoczne_w_calosci(e, WIECZOR_PYTANIE + ("przycisk_skanuj",))]
    assert not usterki, f"okno {rozmiar[0]} x {rozmiar[1]}:\n" + "\n".join(usterki)


# ----------------------------------------------------------------------------
# N2: nowa plytka czeka i ma pytanie - trwaly sygnal, mapa zostaje
# ----------------------------------------------------------------------------
def test_n2_nowa_plytka_z_komunikatem_i_pytaniem_ma_trwaly_sygnal(swiat):
    """Proba P1 recenzenta: technik oglada plytke 1 (prace do obejrzenia), przychodzi plytka 2 "do ponownego skanu", potem jej
    ponowny skan z pytaniem. Ekran zostaje na plytce 1 (mapa bez zmian), a nad lista plytek i mapa stoi panel "Nowy wynik
    czeka" z numerem plytki i tytulem jej komunikatu / pytania - takze po 2,5 s (blysk paska trwa 1,5 s). Przycisk panelu
    pokazuje nowa plytke z pytaniem; panel znika."""
    from stanowisko.ui import czesci as C

    k, zegar = swiat.wieczor()
    s1 = k.symuluj_skan("zwykla", numer=1)
    e = swiat.ekran(k, (1920, 1080))
    assert e.okno.pokazana_plytka() == s1 and not e.jest("panel_nowy_wynik")
    podpisy = dict(e.mapa.podpisy())
    zegar.przesun(1)
    s2 = k.symuluj_skan("do_powtorzenia", numer=2, projekty=PROJEKTY_2)
    e.zdarzenia()
    assert e.okno.pokazana_plytka() == s1 and e.jest("panel_nowy_wynik"), e.tekst()
    tekst = e.tekst_elementu("panel_nowy_wynik")
    assert N.PLYTKA_NR.format(numer=2) in tekst and ST.KOMUNIKATY["skan_do_powtorzenia"].tytul in tekst
    assert not e.jest("komunikat_skan_do_powtorzenia")  # sam komunikat plytki 2 dopiero przy jej mapie
    e.odczekaj(C.BLYSK_MS + 1000)
    assert e.jest("panel_nowy_wynik") and e.okno.pokazana_plytka() == s1 and dict(e.mapa.podpisy()) == podpisy
    zrzut(e, "po_p1_po_skanie_plytki2_bez_przelaczenia")
    zegar.przesun(2)
    s3 = k.symuluj_skan("czysta", numer=2, projekty=PROJEKTY_2)
    e.zdarzenia()
    assert [q.skan_id for q in k.stan().pytania] == [s3] and e.okno.pokazana_plytka() == s1 and not e.jest("pytanie_ponowny_skan")
    tekst = e.tekst_elementu("panel_nowy_wynik")
    assert ST.PYTANIA["ponowny_skan"].tytul in tekst and N.PLYTKA_NR.format(numer=2) in tekst
    assert dict(e.mapa.podpisy()) == podpisy
    zrzut(e, "po_p1_po_3_skanie_bez_przelaczenia")
    e.klik_gniazdo(2)  # technik pracuje dalej na plytce 1: panel nie zabiera mu pracy i nie znika
    e.klik("przycisk_ukruszona")
    assert e.jest("panel_nowy_wynik") and e.okno.pokazana_plytka() == s1 and k.stan().plytka(s1).gniazdo(2).praca.decyzja == "ukruszona"
    e.klik("nowy_wynik_pokaz")
    assert e.okno.pokazana_plytka() == s3 and e.jest("pytanie_ponowny_skan")
    assert not e.jest("panel_nowy_wynik"), e.tekst_elementu("panel_nowy_wynik")  # poprzedni skan tej plytki (s2) tlumaczy pytanie
    assert s2 in e.plytki()


def test_n2_bez_nowej_plytki_i_po_samoczynnym_przelaczeniu_panelu_nie_ma(swiat):
    """Panel "Nowy wynik czeka" jest tylko wtedy, gdy ekran NIE przelaczyl sie na nowa plytke (regula A-P2 bez zmian)."""
    k, zegar = swiat.wieczor()
    s1 = k.symuluj_skan("czysta", numer=1)
    e = swiat.ekran(k, (1600, 900))
    zegar.przesun(1)
    s2 = k.symuluj_skan("zwykla", numer=2, projekty={g: 40 + g for g in range(1, 10)})
    e.zdarzenia()
    assert e.okno.pokazana_plytka() == s2 and not e.jest("panel_nowy_wynik") and s1 in e.plytki()


# ----------------------------------------------------------------------------
# N3: "Zamknij piec" przy pracach nierozstrzygnietych
# ----------------------------------------------------------------------------
def test_n3_zamknij_piec_pyta_o_prace_nierozstrzygniete_i_nazywa_je_po_zamknieciu(swiat):
    """Piec T14 z nierozstrzygnieta zolta praca (plytka 4, gniazdo 3): "Zamknij piec" NIE zamyka od razu - pytanie z liczba
    prac, plytka i gniazdem; pierwsza (domyslna) odpowiedz "Wroc do rozstrzygania" zostawia piec otwarty i otwiera te prace.
    "Zamknij piec mimo to" zamyka; strona wyniku nazywa prace nierozstrzygnieta (plytka, gniazdo) w osobnej grupie."""
    k, zegar = swiat.rano()
    p4, _ = poranek_t14(k, zegar)
    rano = k.stan().rano
    assert [(x.numer_plytki, x.gniazdo, x.klasa) for x in rano.nierozstrzygniete_prace] == [(4, 3, "dwuznaczna")]
    e = swiat.ekran(k, (1536, 864))
    zrzut(e, "po_p5_rano_scenariusz")
    e.klik("przycisk_zamknij_piec")
    assert k.stan().rano.otwarty and e.jest("pytanie_zamknij_mimo"), e.tekst()
    tekst = e.tekst_elementu("pytanie_zamknij_mimo")
    assert N.PLYTKA_NR.format(numer=4) in tekst and "gniazdo 3" in tekst and "1 " in tekst and "NIE" in tekst
    przyciski = [b.objectName() for b in e.w("pytanie_zamknij_mimo").findChildren(type(e.w("zamknij_mimo_wroc")))]
    assert przyciski == ["zamknij_mimo_wroc", "zamknij_mimo_tak"]  # domyslna (pierwsza, wyrozniona): powrot do rozstrzygania
    assert e.w("zamknij_mimo_wroc").property("rola") == "glowny" and e.w("zamknij_mimo_tak").property("rola") != "glowny"
    assert not niewidoczne_w_calosci(e, ("zamknij_mimo_wroc", "zamknij_mimo_tak"))
    zrzut(e, "po_n3_pytanie_przed_zamknieciem")
    e.klik("zamknij_mimo_wroc")
    assert k.stan().rano.otwarty and not e.jest("pytanie_zamknij_mimo")
    assert e.jest("kandydat_1_wybierz") and e.rano.pokazana_praca().praca_id == k.stan().rano.plytka(p4).gniazdo(3).praca.praca_id
    e.klik("przycisk_zamknij_piec")
    assert e.jest("pytanie_zamknij_mimo") and k.stan().rano.otwarty
    e.klik("zamknij_mimo_tak")
    rano = k.stan().rano
    assert not rano.otwarty and not e.jest("pytanie_zamknij_mimo") and e.w("rano_strona_wynik").isChecked()
    assert [(x.numer_plytki, x.gniazdo, x.klasa) for x in rano.nierozstrzygniete_prace] == [(4, 3, "dwuznaczna")]
    assert e.jest("rano_nierozstrzygniete")
    grupa = e.w("rano_nierozstrzygniete").text()
    assert N.PLYTKA_NR.format(numer=4) in grupa and "gniazdo 3" in grupa and "NIE" in grupa and ST.status_rano("dwuznaczna").napis in grupa
    kuwety = [w[0] for w in e.tabela("tabela_kompletne")] + [w[0] for w in e.tabela("tabela_braki")]
    assert len(kuwety) == len(set(kuwety))
    zrzut(e, "po_p5_rano_zamkniety_za_wczesnie")


def test_n3_bez_prac_nierozstrzygnietych_zamknij_piec_nie_pyta(swiat):
    k, zegar = swiat.rano()
    p4, _ = poranek_t14(k, zegar)
    e = swiat.ekran(k, (1920, 1080))
    e.klik_rano(p4, 3)
    e.klik("kandydat_1_wybierz")
    assert k.stan().rano.nierozstrzygniete_prace == ()
    e.klik("przycisk_zamknij_piec")
    assert not k.stan().rano.otwarty and not e.jest("pytanie_zamknij_mimo") and not e.jest("rano_nierozstrzygniete")


# ----------------------------------------------------------------------------
# poz. 8: nowy skan przed odpowiedzia na "ponowny skan?"
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("odpowiedz", ("odp_odrzuc_ponowny_skan", "odp_potwierdz_ponowny_skan"))
def test_poz8_nowy_skan_przed_odpowiedzia_nie_jest_sprawdzony_i_rozni_sie_od_poprzedniego(swiat, odpowiedz):
    """Proba P7 recenzenta: plytka 2 "do ponownego skanu", potem jej ponowny skan (same zielone). Do czasu odpowiedzi naglowek
    mapy i kafelek nowego skanu NIE mowia "sprawdzona" (napis "nowy skan - czeka na odpowiedz"), a kafelek poprzedniego skanu
    ma napis "poprzedni skan tej plytki". Po odpowiedzi nowy skan jest "sprawdzona", znacznik poprzedniego znika."""
    k, zegar = swiat.wieczor()
    s2 = k.symuluj_skan("do_powtorzenia", numer=2, projekty=PROJEKTY_2)
    e = swiat.ekran(k, (1920, 1080))
    zrzut(e, "po_p7_plytka2_popraw")
    zegar.przesun(2)
    s3 = k.symuluj_skan("czysta", numer=2, projekty=PROJEKTY_2)
    e.zdarzenia()
    assert e.okno.pokazana_plytka() == s3 and e.jest("pytanie_ponowny_skan")
    plytka2 = N.PLYTKA_NR.format(numer=2)
    assert e.w("mapa_naglowek").text() == N.MAPA_NAGLOWEK.format(plytka=plytka2, napis=N.PLYTKA_NOWY_SKAN)
    nowy, stary = e.tekst_elementu(f"plytka_{s3}"), e.tekst_elementu(f"plytka_{s2}")
    assert N.PLYTKA_SPRAWDZONA not in e.w("mapa_naglowek").text() and N.PLYTKA_SPRAWDZONA not in nowy
    assert N.PLYTKA_NOWY_SKAN in nowy and N.PLYTKA_POPRZEDNI_SKAN not in nowy
    assert N.PLYTKA_POPRZEDNI_SKAN in stary and N.PLYTKA_NOWY_SKAN not in stary
    zrzut(e, "po_p7_pytanie_przed_odpowiedzia")
    e.klik(odpowiedz)
    assert not e.jest("pytanie_ponowny_skan")
    assert e.w("mapa_naglowek").text() == N.MAPA_NAGLOWEK.format(plytka=plytka2, napis=N.PLYTKA_SPRAWDZONA)
    assert N.PLYTKA_NOWY_SKAN not in e.tekst_elementu(f"plytka_{s3}") and N.PLYTKA_POPRZEDNI_SKAN not in e.tekst(tylko_widoczne=True)
    zrzut(e, "po_p7_po_odpowiedzi_" + ("nie" if "odrzuc" in odpowiedz else "tak"))


# ----------------------------------------------------------------------------
# poz. 6: przycisk "program czeka na plik skanu"
# ----------------------------------------------------------------------------
def test_poz6_przycisk_skanu_mowi_co_robi_i_nie_wyglada_jak_start_skanu(swiat):
    """Przycisk na pasku nie zaczyna sie od "Skanuj" i nie jest przyciskiem glownym: mowi, ze program czeka na plik, a skan
    uruchamia sie w programie skanera; Spacja i klikniecie dzialaja jak dotad (jedno ``start_skanu``)."""
    from PySide6.QtCore import Qt

    k, _ = swiat.wieczor()
    e = swiat.ekran(k, (1600, 900))
    b = e.w("przycisk_skanuj")
    tekst = b.text()
    assert tekst == N.SKANUJ_ATRAPA and not tekst.lower().startswith("skanuj"), tekst
    assert "na plik skanu" in tekst and "programie skanera" in tekst and "Spacja" in tekst
    assert b.property("rola") != "glowny" and b.toolTip() == N.SKANUJ_ATRAPA_OPIS
    zrzut(e, "po_poz6_pasek_stanu")
    e.klawisz(Qt.Key.Key_Space)
    assert len(k.starty_skanu) == 1 and e.w("napis_skaner").text() == N.SKANER_CZEKA
    e.klik("przycisk_skanuj")
    assert len(k.starty_skanu) == 2


# ----------------------------------------------------------------------------
# poz. 1-4 i 7: napisy
# ----------------------------------------------------------------------------
def test_poz4_pusta_lista_z_godzina_zapisu_to_jedno_zdanie(swiat):
    k, _ = swiat.wieczor()
    k.symuluj_skan("czysta", numer=1)
    e = swiat.ekran(k, (1600, 900))
    assert k.stan().lista_zapisana and e.jest("lista_pusta") and e.jest("lista_zapisano")
    stopka = e.w("lista_pusta").text() + " " + e.w("lista_zapisano").text()
    assert stopka.count("Lista") == 1 and "19:00" in stopka and N.LISTA_PUSTA in stopka, stopka


def test_poz7_opis_zoltej_pracy_w_widoku_nie_kaze_klikac_gniazda(swiat):
    """Po kliknieciu gniazda widok pracy nie mowi juz "kliknij gniazdo" (legenda nadal tak): dla zoltej - "wybierz ponizej"."""
    k, zegar = swiat.rano()
    p4, _ = poranek_t14(k, zegar)
    e = swiat.ekran(k, (1920, 1080))
    e.klik_rano(p4, 3)
    opis = e.w("praca_rano_opis").text()
    assert "kliknij gniazdo" not in opis.lower() and ST.PRZYCISKI["wybierz_kandydata"] in opis, opis
    k2, _ = swiat.rano()
    skany = k2.scenariusz_poranny()
    e2 = swiat.ekran(k2, (1920, 1080))
    for numer, gniazdo in ((5, 22), (5, 3), (6, 2), (4, 1)):  # nieznana, konflikt, poprawka, pewna
        e2.klik_rano(skany[numer], gniazdo)
        assert "kliknij gniazdo" not in e2.w("praca_rano_opis").text().lower(), (numer, gniazdo, e2.w("praca_rano_opis").text())


def test_poz3_lista_brakow_wszystkie_piece_kolumna_stan_nieucieta(swiat):
    """"Lista brakow (wszystkie piece)": napis stanu ("nie wyszedl z pieca") miesci sie w kolumnie przy 1920 x 1080 i 1536 x 864."""
    from PySide6.QtWidgets import QStyle

    k, _ = swiat.rano()
    skany = k.scenariusz_poranny()
    k.przypisz_recznie(k.stan().rano.plytka(skany[6]).gniazdo(11).praca.praca_id, None)
    assert k.zamknij_piec(k.stan().rano.sesja_pieca_id).ok
    e = swiat.ekran(k, (1920, 1080))
    for rozmiar in ((1920, 1080), (1536, 864)):
        ustaw_rozmiar(e, rozmiar)
        e.klik("rano_strona_wynik")
        t = e.w("tabela_braki_biezace")
        wiersze = e.tabela("tabela_braki_biezace")
        assert wiersze and any(ST.STANY_PUNKTU["brak_po_piecu"] in w[2] for w in wiersze)
        # Qt ucina napis komorki ("..."), gdy jest szerszy niz kolumna bez marginesu ramki fokusu z obu stron
        margines = 2 * (t.style().pixelMetric(QStyle.PixelMetric.PM_FocusFrameHMargin, None, t) + 1)
        uciete = [(w[kol], t.fontMetrics().horizontalAdvance(w[kol]), t.columnWidth(kol)) for w in wiersze for kol in range(t.columnCount())
                  if t.fontMetrics().horizontalAdvance(w[kol]) + margines > t.columnWidth(kol)]
        assert not uciete, f"{rozmiar}: napisy szersze niz kolumna: {uciete}"
        if rozmiar == (1536, 864):
            zrzut(e, "po_poz3_lista_brakow_1536x864")


def test_poz1_poz2_teksty_excela_bez_oznaczen_programisty():
    """Panel Excela: tekst dla technika bez "regula N:", "(D2)", "[excel]" i nazw plikow ustawien (szczegoly zostaja w logu)."""
    for surowy in ("regula 2: nazwa w H zgodna z nazwa folderu - jeden wiersz 9", "regula 5: kilka wierszy z ta kuweta - wskaz wiersz",
                   "regula 4: pole B wiersza 12 juz zielone - nic do zapisania, tylko wpis w logu"):
        czysty = NR.dla_technika(surowy)
        assert "regula" not in czysty.lower() and czysty and czysty[0].isupper() and surowy.split(": ", 1)[1][1:] in czysty, czysty
    surowy = ("[excel] skoroszyt / arkusz nie sa wskazane w ustawieniach - program uzywa aktywnych: skoroszyt 'Zlecenia_atrapa.xlsx', arkusz "
              "'Arkusz1'; sprawdz przed pierwszym zatwierdzeniem i wpisz nazwy w ustawienia.toml (D2)")
    czysty = NR.dla_technika(surowy)
    assert "(D2)" not in czysty and "[excel]" not in czysty and "ustawienia.toml" not in czysty, czysty
    assert "Zlecenia_atrapa.xlsx" in czysty and "Arkusz1" in czysty
    assert NR.dla_technika("") == "" and NR.dla_technika("Zwykly tekst.") == "Zwykly tekst."
