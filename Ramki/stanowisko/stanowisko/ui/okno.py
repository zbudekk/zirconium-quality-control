"""okno - okno trybu "Wieczor": sklada elementy ekranu, pokazuje ``kontroler.stan()`` i wysyla polecenia kontrolera.

Zasady (kontrakt ``kontroler_api`` / ``opisy_modulow/aplikacja.md``):
* okno NICZEGO nie liczy i nie siega do ``session`` / ``baza`` / ``scanner``; kolory i napisy statusow bierze ze stanu
  i ze ``statusy``; na ekranie nie ma sciezek ani nazw plikow (folder puli i skanera nie sa pokazywane);
* kazde polecenie idzie przez ``kontroler.wykonaj``; odmowa to ``Odpowiedz`` i komunikat w stanie - okno pokazuje go jak
  kazdy inny komunikat, nic nie rzuca;
* pytania i komunikaty sa panelami w oknie (nad mapa; prawa kolumna z przyciskami decyzji ma stale miejsce) - zadnych okien modalnych; stan o nizszej ``wersja`` niz pokazany jest pomijany;
* wszystko dzieje sie w watku okna poza obrazem odchylek (``obraz.WczytywaczObrazow``); odswiezenie po sygnale stanu
  przebudowuje tylko te czesci ekranu, ktorych dane sie zmienily;
* klawiatura nalezy do okna: Spacja = "start skanu" (raz na nacisniecie), U / O / C = decyzje przy otwartej pracy,
  N = nastepna praca do obejrzenia, Esc = zamknij widok pracy. Zaden przycisk nie przyjmuje klawiatury.

Wlasny stan okna to tylko wybor technika: pokazana plytka, wybrane gniazdo, filtr listy, otwarty panel numeru plytki
albo zmiany osoby oraz tekst ostatniej odmowy, ktorej nie ma w komunikatach stanu.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget

from .. import kontroler_api as K
from .. import statusy as ST
from . import napisy as N
from . import styl
from .czesci import (LOKALNE_NUMER_BEZ_ZMIAN, LOKALNE_ZAMKNIJ_ODPOWIEDZ, Legenda, ListaDofrezowania, ListaPlytek, PanelOsoby, PasekStanu, WidokPracy,
                     etykieta, godzina, nazwa_plytki, panel_komunikatu, panel_numeru, panel_odmowy, panel_pytania, przycisk, wyczysc)
from .mapa import MapaPlytki, geometria_ukladu
from .obraz import WczytywaczObrazow

SPRAWY_OSOBY = ("brak_operatora", "nowa_zmiana", "pusta_lista_operatorow", "osoba_spoza_listy")  # komunikaty pokazywane w panelu wyboru osoby
PANELI = 3  # tyle pytan i komunikatow naraz (pierwsze: pokazana plytka, potem ogolne od najnowszego); reszta czeka na zamkniecie


def otwarte(pozycje) -> list:
    """Pytania / komunikaty do pokazania: bez pozycji zamknietych przez technika (``ukryte=True``, kontrakt w wersji 2 - D6).
    ``stan.pytania`` i ``stan.komunikaty`` sa juz otwarte; filtr chroni ekran, gdyby pozycja ukryta jednak tam trafila."""
    return [x for x in pozycje if not x.ukryte]


class OknoWieczor(QWidget):
    def __init__(self, kontroler, lacznik):
        super().__init__()
        self.k = kontroler
        self.lacznik = lacznik
        self.setObjectName("okno_wieczor")
        self.setWindowTitle(N.TYTUL_OKNA)
        self.setStyleSheet(styl.ARKUSZ)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(1280, 760)
        self.resize(1600, 900)
        # wybor technika (jedyny wlasny stan okna)
        self._stan = None
        self._plytka_id: int | None = None
        self._gniazdo: int | None = None
        self._poza: int | None = None  # praca_id pracy poza gniazdem
        self._nr_pracy = 0
        self._lista_wszystkie = False
        self._zmiana_osoby = False
        self._pokaz_wczesniejsze = False
        self._podaj_numer = False  # otwarty panel recznego numeru plytki
        self._odmowa = ""  # tekst odmowy ostatniego polecenia, gdy kontroler nie dal go w komunikatach stanu
        self._znane: set = set()
        self._nieobejrzane: set = set()  # plytki, ktore przyszly, gdy technik ogladal prace
        self._pierwszy_stan = True
        self._nr_komunikatow: dict = {}
        self._obraz_dla: int | None = None
        self._bez_obrazu: set = set()
        self._sygnatury: dict = {}
        self._zamkniete = False
        self.wczytywacz = WczytywaczObrazow(self)
        self.wczytywacz.gotowy.connect(self._obraz_gotowy)
        self._zbuduj()
        lacznik.stan_zmieniony.connect(self._na_stan)
        lacznik.postep.connect(self._na_postep)
        lacznik.zamkniety.connect(self._na_zamkniety)
        self.pokaz_stan(kontroler.stan())

    # --- budowa ----------------------------------------------------------------------------------
    def _zbuduj(self) -> None:
        korzen = QVBoxLayout(self)
        korzen.setContentsMargins(10, 10, 10, 10)
        korzen.setSpacing(8)
        self.pasek = PasekStanu()
        self.pasek.skanuj.connect(self._start_skanu)
        self.pasek.odswiez_pule.connect(lambda: self._polecenie("odswiez_pule"))
        self.pasek.zmien_osobe.connect(self._przelacz_zmiane_osoby)
        korzen.addWidget(self.pasek)
        calosc = QHBoxLayout()
        calosc.setSpacing(10)
        korzen.addLayout(calosc, 1)
        lewa = QVBoxLayout()
        lewa.setSpacing(8)
        calosc.addLayout(lewa, 1)
        # wybor osoby, pytania i komunikaty: panele nad lista plytek i mapa; prawa kolumna (widok pracy z przyciskami decyzji
        # i lista) ma stale miejsce - przyciski nie przesuwaja sie, gdy przychodzi komunikat
        self._uwagi = QVBoxLayout()
        self._uwagi.setSpacing(6)
        lewa.addLayout(self._uwagi)
        srodek = QHBoxLayout()
        srodek.setSpacing(10)
        lewa.addLayout(srodek, 1)

        self.lista_plytek = ListaPlytek()
        self.lista_plytek.wybrano.connect(lambda skan_id: QTimer.singleShot(0, lambda: self._pokaz_plytke(skan_id)))
        self.lista_plytek.przelacz_wczesniejsze.connect(lambda: QTimer.singleShot(0, self._przelacz_wczesniejsze))
        self.lista_plytek.ponow_zapis.connect(lambda: QTimer.singleShot(0, lambda: self._polecenie("ponow_zapis")))
        srodek.addWidget(self.lista_plytek)

        kolumna = QFrame()
        kolumna.setProperty("rola", "panel")
        kolumna.setObjectName("kolumna_mapy")
        u = QVBoxLayout(kolumna)
        u.setContentsMargins(12, 8, 12, 8)
        u.setSpacing(6)
        wiersz = QHBoxLayout()
        wiersz.setSpacing(10)
        self.naglowek = etykieta("", "tytul", "mapa_naglowek")
        self.podnaglowek = etykieta("", "slaby", "mapa_godzina")
        wiersz.addWidget(self.naglowek)
        wiersz.addWidget(self.podnaglowek)
        wiersz.addStretch(1)
        self._akcje_plytki = QHBoxLayout()
        self._akcje_plytki.setSpacing(8)
        wiersz.addLayout(self._akcje_plytki)
        u.addLayout(wiersz)
        self.mapa = MapaPlytki()
        self.mapa.klik.connect(self._klik_gniazdo)
        u.addWidget(self.mapa, 1)
        self.poza = QWidget()
        self.poza.setObjectName("poza_gniazdem")
        self._poza_uklad = QHBoxLayout(self.poza)
        self._poza_uklad.setContentsMargins(0, 0, 0, 0)
        self._poza_uklad.setSpacing(8)
        u.addWidget(self.poza)
        self.legenda = Legenda()
        u.addWidget(self.legenda)
        srodek.addWidget(kolumna, 1)

        prawa = QWidget()
        prawa.setFixedWidth(styl.SZEROKOSC_PRAWEJ)
        u = QVBoxLayout(prawa)
        u.setContentsMargins(0, 0, 0, 0)
        u.setSpacing(10)
        self.widok = WidokPracy()
        self.widok.decyzja.connect(self._decyzja)
        self.widok.zamknij.connect(self._zamknij_prace)
        self.widok.nastepna.connect(self._idz_do_nastepnej)
        self.widok.inna_praca.connect(self._inna_praca)
        self.widok.setMinimumHeight(500)
        u.addWidget(self.widok, 9)
        self.lista = ListaDofrezowania()
        self.lista.filtr.connect(self._ustaw_filtr)
        self.lista.wybrano.connect(self._klik_pozycja)
        self.lista.zapisz.connect(self._zapisz_liste)
        u.addWidget(self.lista, 4)
        calosc.addWidget(prawa)

    # --- sygnaly kontrolera ----------------------------------------------------------------------
    def _na_stan(self, stan) -> None:
        self.pokaz_stan(stan)

    def _na_postep(self, _postep) -> None:
        """Postep analizy: zmienia sie tylko czesc "zywa" stanu - odswiezany jest sam pasek."""
        if self._zamkniete:
            return
        stan = self.k.stan()
        if self._stan is None or stan.wersja >= self._stan.wersja:
            if self._stan is not None and stan.plytki is not self._stan.plytki:
                self.pokaz_stan(stan)
            else:
                self._stan = stan
                self.pasek.ustaw(stan)

    def _na_zamkniety(self) -> None:
        self.setEnabled(False)

    def pokaz_stan(self, stan) -> None:
        """Pokazuje ``stan`` (``StanAplikacji``). Stan starszy niz pokazany jest pomijany (kontrakt: zagniezdzona petla okna)."""
        if stan is None or self._zamkniete or (self._stan is not None and stan.wersja < self._stan.wersja):
            return
        self._stan = stan
        for k in stan.komunikaty:  # kolejnosc pojawiania sie komunikatow (najnowsze na gorze)
            self._nr_komunikatow.setdefault(k.id, len(self._nr_komunikatow))
        self._wybierz_plytke(stan)
        self._odswiez()

    def pokazana_plytka(self) -> int | None:
        """``skan_id`` plytki, ktorej mapa jest na ekranie."""
        return self._plytka_id

    # --- wybor plytki i pracy ----------------------------------------------------------------------
    def _wybierz_plytke(self, stan) -> None:
        numery = [p.skan_id for p in stan.plytki]
        nowe = [i for i in numery if i not in self._znane]
        self._znane.update(numery)
        self._nieobejrzane &= set(numery)
        if self._plytka_id not in numery:
            self._plytka_id, self._gniazdo, self._poza, self._podaj_numer = None, None, None, False
        if nowe and not self._pierwszy_stan:
            if self._gniazdo is not None or self._poza is not None:
                self._nieobejrzane.update(nowe)  # technik oglada prace: nie zabieramy mu ekranu
            else:
                self._plytka_id, self._podaj_numer = nowe[-1], False
        self._pierwszy_stan = False
        if self._plytka_id is None and numery:
            self._plytka_id = stan.biezaca_plytka if stan.biezaca_plytka in numery else numery[-1]
        self._nieobejrzane.discard(self._plytka_id)
        if self._zmiana_osoby and stan.wymaga_operatora:
            self._zmiana_osoby = False

    def _plytka(self):
        return self._stan.plytka(self._plytka_id) if self._stan is not None and self._plytka_id is not None else None

    def _wybor(self):
        """(gniazdo, praca) wybrane przez technika wg biezacego stanu; (None, None), gdy nic nie jest wybrane albo zniknelo."""
        plytka = self._plytka()
        if plytka is None:
            return None, None
        if self._gniazdo is not None:
            g = plytka.gniazdo(self._gniazdo)
            if g is None:
                return None, None
            self._nr_pracy = min(self._nr_pracy, max(0, len(g.prace) - 1))
            return g, (g.prace[self._nr_pracy] if g.prace else None)
        if self._poza is not None:
            return None, next((p for p in plytka.poza_gniazdem if p.praca_id == self._poza), None)
        return None, None

    def _pokaz_plytke(self, skan_id: int, gniazdo: int | None = None, poza: int | None = None) -> None:
        if self._stan is None or self._stan.plytka(skan_id) is None:
            return
        self._plytka_id, self._gniazdo, self._poza, self._nr_pracy, self._podaj_numer = skan_id, gniazdo, poza, 0, False
        self._nieobejrzane.discard(skan_id)
        self._odswiez()

    def _klik_gniazdo(self, nr: int) -> None:
        self._gniazdo, self._poza, self._nr_pracy = nr, None, 0
        self._odswiez()

    def _klik_poza(self, praca_id: int) -> None:
        self._gniazdo, self._poza, self._nr_pracy = None, praca_id, 0
        self._odswiez()

    def _klik_pozycja(self, pozycja) -> None:
        """Klikniecie pozycji listy "do dofrezowania": pokazuje te prace, jesli jej plytka jest w stanie tej doby."""
        if self._stan is None or self._stan.plytka(pozycja.skan_id) is None:
            return
        skan_id, gniazdo = pozycja.skan_id, pozycja.gniazdo
        poza = pozycja.praca_id if gniazdo is None else None
        QTimer.singleShot(0, lambda: self._pokaz_plytke(skan_id, gniazdo, poza))

    def _zamknij_prace(self) -> None:
        if self._gniazdo is None and self._poza is None:
            return
        self._gniazdo, self._poza, self._nr_pracy = None, None, 0
        self._odswiez()

    def _inna_praca(self) -> None:
        g, _ = self._wybor()
        if g is not None and len(g.prace) > 1:
            self._nr_pracy = (self._nr_pracy + 1) % len(g.prace)
            self._odswiez()

    def _nastepna(self, plytka) -> int | None:
        """Numer nastepnego gniazda z praca do obejrzenia: bez decyzji, z dozwolona decyzja i ze statusem innym niz zielony."""
        if plytka is None:
            return None
        numery = [g.nr for g in plytka.gniazda
                  if g.nr != self._gniazdo and any(p.decyzja is None and "ukruszona" in p.dozwolone and p.status not in ST.STATUSY_ZIELONE
                                                   for p in g.prace)]
        if not numery:
            return None
        dalsze = [nr for nr in numery if self._gniazdo is None or nr > self._gniazdo]
        return (dalsze or numery)[0]

    def _idz_do_nastepnej(self) -> None:
        nr = self._nastepna(self._plytka())
        if nr is not None:
            self._klik_gniazdo(nr)

    def _ustaw_filtr(self, wszystkie: bool) -> None:
        self._lista_wszystkie = wszystkie
        self._odswiez()

    def _przelacz_wczesniejsze(self) -> None:
        self._pokaz_wczesniejsze = not self._pokaz_wczesniejsze
        self._odswiez()

    def _przelacz_zmiane_osoby(self) -> None:
        self._zmiana_osoby = not self._zmiana_osoby
        self._odswiez()

    # --- polecenia -------------------------------------------------------------------------------
    def _polecenie(self, nazwa: str, *argumenty):
        """Polecenie do kontrolera. Odmowa wraca jako ``Odpowiedz`` (nie wyjatek): zwykle jest tez komunikatem w stanie i ekran
        pokazuje go po odswiezeniu; gdy stan jej nie zawiera (np. ``zle_argumenty``), okno pokazuje tekst odpowiedzi samo."""
        if self._zamkniete or self._stan is None or self._stan.zamkniety:
            return None
        odpowiedz = self.k.wykonaj(nazwa, *argumenty)  # kontrakt: polecenia nie rzucaja wyjatkow (zle dane = odmowa ``zle_argumenty``)
        stan = self.k.stan()
        tekst = odpowiedz.tekst if not odpowiedz.ok else ""
        self._odmowa = tekst if tekst and all(k.tekst != tekst for k in otwarte(stan.komunikaty)) else ""
        if odpowiedz.ok and nazwa == "podaj_numer_plytki":
            self._podaj_numer = False
        if stan.wersja == self._stan.wersja:
            self._odswiez()  # polecenie bez nowego stanu (odmowa bez komunikatu): pokaz tekst odpowiedzi
        else:
            self.pokaz_stan(stan)
        return odpowiedz

    def _start_skanu(self) -> None:
        self._polecenie("start_skanu")

    def _decyzja(self, nazwa: str) -> None:
        if not self.widok.aktywny(nazwa):
            return
        _, praca = self._wybor()
        if praca is not None:
            self._polecenie(nazwa, praca.praca_id)

    def _wybrano_osobe(self, osoba: str) -> None:
        self._zmiana_osoby = False
        self._polecenie("wybierz_operatora", osoba)

    def _wyloguj(self) -> None:
        self._zmiana_osoby = False
        self._polecenie("wybierz_operatora", None)

    def _zapisz_liste(self) -> None:
        self._polecenie("zapisz_liste")  # czas zapisu wraca w stanie (``lista_zapisana``); odmowa = komunikat

    def _przelacz_numer(self) -> None:
        self._podaj_numer = not self._podaj_numer
        self._odswiez()

    # --- klawiatura ------------------------------------------------------------------------------
    def keyPressEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        klawisz = zdarzenie.key()
        if zdarzenie.isAutoRepeat():  # przytrzymany klawisz to jedno nacisniecie
            zdarzenie.accept()
            return
        if klawisz == Qt.Key.Key_Space:
            self._start_skanu()
        elif klawisz == Qt.Key.Key_U:
            self._decyzja("ukruszona")
        elif klawisz == Qt.Key.Key_O:
            self._decyzja("ok")
        elif klawisz == Qt.Key.Key_C:
            self._decyzja("cofnij")
        elif klawisz == Qt.Key.Key_N:
            self._idz_do_nastepnej()
        elif klawisz == Qt.Key.Key_Escape:
            if self._zmiana_osoby:
                self._przelacz_zmiane_osoby()
            else:
                self._zamknij_prace()
        else:
            super().keyPressEvent(zdarzenie)
            return
        zdarzenie.accept()

    def showEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        super().showEvent(zdarzenie)
        self.setFocus()

    def closeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        """Okno odlacza sie od lacznika i konczy watek obrazow; kontroler zamyka ``aplikacja.main()``."""
        if not self._zamkniete:
            self._zamkniete = True
            for sygnal, odbiorca in ((self.lacznik.stan_zmieniony, self._na_stan), (self.lacznik.postep, self._na_postep),
                                     (self.lacznik.zamkniety, self._na_zamkniety)):
                try:
                    sygnal.disconnect(odbiorca)
                except (RuntimeError, TypeError):
                    pass
            self.wczytywacz.zakoncz()
        super().closeEvent(zdarzenie)

    # --- odswiezanie -----------------------------------------------------------------------------
    def _zmienione(self, czesc: str, sygnatura) -> bool:
        if self._sygnatury.get(czesc) == sygnatura:
            return False
        self._sygnatury[czesc] = sygnatura
        return True

    def _odswiez(self) -> None:
        stan = self._stan
        if stan is None:
            return
        self.pasek.ustaw(stan)
        plytka = self._plytka()
        widoczne = [p for p in stan.plytki if self._pokaz_wczesniejsze or p.zmiana in (None, stan.zmiana) or p.skan_id == self._plytka_id]
        wczesniejszych = sum(1 for p in stan.plytki if p.zmiana not in (None, stan.zmiana))
        self.lista_plytek.ustaw(widoczne, self._plytka_id, self._nieobejrzane, {q.skan_id for q in otwarte(stan.pytania)}, wczesniejszych,
                                self._pokaz_wczesniejsze, stan.niezapisane)
        gniazdo, praca = self._wybor()
        if gniazdo is None and praca is None:
            self._gniazdo, self._poza = None, None
        geometria = geometria_ukladu(self.k, plytka.uklad) if plytka is not None and plytka.gniazda and (plytka.aktywna or plytka.prace) else None
        self.mapa.ustaw(plytka, geometria, self._gniazdo)
        self._odswiez_naglowek(stan, plytka)
        self.legenda.ustaw(plytka)
        self._odswiez_uwagi(stan, plytka)
        if gniazdo is None and praca is None:
            self.widok.wyczysc()
            self._obraz_dla = None
        else:
            self.widok.ustaw(stan, plytka, gniazdo, praca, self._nr_pracy, self._nastepna(plytka) is not None)
            self._odswiez_obraz(praca)
        self.lista.ustaw(stan.do_dofrezowania_biezaca if self._lista_wszystkie else stan.do_dofrezowania, self._lista_wszystkie,
                         stan.lista_zapisana)

    def _odswiez_naglowek(self, stan, plytka) -> None:
        if plytka is None:
            self.naglowek.setText("")
            self.podnaglowek.setText("")
        else:
            self.naglowek.setText(N.MAPA_NAGLOWEK.format(plytka=nazwa_plytki(plytka.numer), napis=plytka.napis))
            self.podnaglowek.setText(N.MAPA_GODZINA.format(godzina=godzina(plytka.czas)) if plytka.czas else "")
        # polecenia plytki ze stanu (``Plytka.dozwolone``); te, o ktore wlasnie pyta otwarte pytanie, sa tylko w panelu pytania
        pytane = {"brak_numeru_plytki": "podaj_numer_plytki", "plytka_nie_z_trybu": "dopusc_plytke"}
        w_pytaniach = {pytane.get(q.rodzaj) for q in otwarte(stan.pytania) if plytka is not None and q.skan_id == plytka.skan_id}
        akcje = tuple(a for a in ("podaj_numer_plytki", "dopusc_plytke", "cofnij_zastapienie", "cofnij_dopuszczenie")
                      if plytka is not None and a in plytka.dozwolone and a not in w_pytaniach and a in ST.PRZYCISKI)
        if self._zmienione("akcje", (plytka.skan_id if plytka else None, akcje, stan.operator)):
            wyczysc(self._akcje_plytki)
            for akcja in akcje:
                if akcja == "podaj_numer_plytki":  # numer wybiera sie w panelu z cyframi
                    b = przycisk(ST.PRZYCISKI[akcja], f"plytka_{akcja}", "lacze", self._przelacz_numer)
                else:
                    b = przycisk(ST.PRZYCISKI[akcja], f"plytka_{akcja}", "lacze", lambda a=akcja, s=plytka.skan_id: self._polecenie(a, s))
                    b.setEnabled(stan.operator is not None)
                self._akcje_plytki.addWidget(b)
        poza = plytka.poza_gniazdem if plytka is not None else ()
        if self._zmienione("poza", (poza, self._poza)):
            wyczysc(self._poza_uklad)
            if poza:
                self._poza_uklad.addWidget(etykieta(N.POZA_GNIAZDEM.format(n=len(poza)), "slaby"))
                for i, p in enumerate(poza):
                    b = przycisk(p.podpis, f"poza_{i}", None, lambda praca_id=p.praca_id: self._klik_poza(praca_id))
                    b.setStyleSheet(f"background: {p.rgb}; color: {styl.tekst_na(p.rgb)}; border: {'4' if p.praca_id == self._poza else '1'}px solid #101418; "
                                    "border-radius: 6px; padding: 4px 12px; font-size: 15px; font-weight: 700;")
                    self._poza_uklad.addWidget(b)
                self._poza_uklad.addStretch(1)
        self.poza.setVisible(bool(poza))

    def _odswiez_uwagi(self, stan, plytka) -> None:
        """Pod paskiem stanu, nad lista plytek i mapa: wybor osoby, tekst odmowy spoza stanu, reczny numer plytki, otwarte pytania
        pokazanej plytki (``stan.pytania``), jej komunikaty, komunikaty ogolne (bledy pierwsze, potem od najnowszego; jednakowe razem)."""
        pokaz_osobe = stan.wymaga_operatora or self._zmiana_osoby
        wszystkie = otwarte(stan.komunikaty)  # pozycje ukryte przez technika (``ukryte``) nie wracaja na ekran
        if not stan.operatorzy:
            teksty = [ST.tekst_komunikatu("pusta_lista_operatorow")[2]]
        elif stan.wymaga_operatora:
            teksty = [k.tekst for k in wszystkie if k.rodzaj == "nowa_zmiana"][-1:] + [ST.tekst_komunikatu("brak_operatora")[2]]
        else:
            teksty = []
        pytania = [q for q in otwarte(stan.pytania) if plytka is not None and q.skan_id == plytka.skan_id]
        komunikaty = [k for k in wszystkie if plytka is not None and k.skan_id == plytka.skan_id]
        numer = (plytka is not None and self._podaj_numer and "podaj_numer_plytki" in plytka.dozwolone
                 and not any(q.rodzaj == "brak_numeru_plytki" for q in pytania))
        ogolne = [k for k in wszystkie
                  if (k.skan_id is None or stan.plytka(k.skan_id) is None) and not (pokaz_osobe and k.rodzaj in SPRAWY_OSOBY)]
        # bledy przed reszta (np. trwaly blad zapisu nie chowa sie pod "i jeszcze n"), w kazdej grupie od najnowszego
        ogolne.sort(key=lambda k: (0 if k.poziom == ST.POZIOM_BLAD else 1, -self._nr_komunikatow.get(k.id, 0)))
        grupy: dict = {}  # jednakowe komunikaty (ten sam rodzaj i tekst) jako jeden panel z licznikiem
        for k in ogolne:
            grupy.setdefault((k.rodzaj, k.poziom, k.tytul, k.tekst), []).append(k)
        sygnatura = (pokaz_osobe, self._zmiana_osoby, stan.operator, stan.operatorzy, tuple(teksty), self._odmowa, numer,
                     plytka.skan_id if plytka else None, plytka.numer if plytka else None, plytka.typ if plytka else None,
                     tuple(pytania), tuple(komunikaty), tuple(ogolne))
        if not self._zmienione("uwagi", sygnatura):
            return
        wyczysc(self._uwagi)
        if pokaz_osobe:
            panel = PanelOsoby(stan.operatorzy, stan.operator, teksty, zmiana_osoby=not stan.wymaga_operatora)
            panel.wybrano.connect(self._wybrano_osobe)
            panel.bez_zmian.connect(self._przelacz_zmiane_osoby)
            panel.wyloguj.connect(self._wyloguj)
            self._uwagi.addWidget(panel)
        nazwa = nazwa_plytki(plytka.numer) if plytka is not None else ""
        budowa = []  # funkcje budujace panele, w kolejnosci waznosci
        if self._odmowa:
            budowa.append(lambda: panel_odmowy(self._odmowa))
        if numer:
            geometria = geometria_ukladu(self.k, plytka.uklad)
            numery = tuple(geometria.numery) if geometria is not None and geometria.numery else K.NUMERY_PLYTEK_ZAPASOWE
            brak = ST.tekst_komunikatu("brak_operatora" if stan.operatorzy else "pusta_lista_operatorow")[2]
            budowa.append(lambda: panel_numeru(plytka.skan_id, numery, plytka.numer, stan.operator is not None, brak, nazwa))
        budowa += [lambda q=q: panel_pytania(q, stan, plytka.typ, nazwa) for q in pytania]
        budowa += [lambda k=k: panel_komunikatu((k,), nazwa) for k in komunikaty]
        budowa += [lambda g=g: panel_komunikatu(tuple(g)) for g in grupy.values()]
        for zbuduj in budowa[:PANELI]:
            panel = zbuduj()
            panel.polecenie.connect(self._polecenie_panelu)
            self._uwagi.addWidget(panel)
        if len(budowa) > PANELI:
            self._uwagi.addWidget(etykieta(N.JESZCZE.format(n=len(budowa) - PANELI), "slaby", "uwagi_jeszcze"))

    def _polecenie_panelu(self, nazwa: str, argumenty: tuple) -> None:
        if nazwa == LOKALNE_NUMER_BEZ_ZMIAN:
            self._przelacz_numer()
        elif nazwa == LOKALNE_ZAMKNIJ_ODPOWIEDZ:
            self._odmowa = ""
            self._odswiez()
        elif nazwa == "zamknij_komunikat":  # panel jednakowych komunikatow zamyka je wszystkie
            for komunikat_id in argumenty:
                self._polecenie(nazwa, komunikat_id)
        else:
            self._polecenie(nazwa, *argumenty)

    # --- obraz odchylek --------------------------------------------------------------------------
    def _odswiez_obraz(self, praca) -> None:
        if praca is None:
            self._obraz_dla = None
            return
        if praca.praca_id == self._obraz_dla:
            return
        self._obraz_dla = praca.praca_id
        gotowy = self.wczytywacz.obraz(praca.praca_id)
        if gotowy is not None:
            self.widok.obraz.ustaw_obraz(gotowy)
            return
        szczegoly = None
        if praca.praca_id not in self._bez_obrazu and praca.gniazdo is not None:
            szczegoly = self.k.szczegoly_pracy(praca.praca_id)  # w watku okna: odczyt z pamieci kontrolera i jedno zapytanie do bazy
        if szczegoly is None or szczegoly.plik_podgladu is None:
            self._bez_obrazu.add(praca.praca_id)
            self.widok.obraz.ustaw_napis(N.OBRAZ_BRAK)
            return
        self.widok.obraz.ustaw_napis(N.OBRAZ_WCZYTYWANIE)
        self.wczytywacz.zlec(praca.praca_id, szczegoly.plik_podgladu, praca.gniazdo, szczegoly.ubytki)

    def _obraz_gotowy(self, klucz, obraz) -> None:
        if obraz is None:
            self._bez_obrazu.add(klucz)
        if self._zamkniete or klucz != self._obraz_dla or not self.widok.otwarty():
            return
        if obraz is None:
            self.widok.obraz.ustaw_napis(N.OBRAZ_BRAK)
        else:
            self.widok.obraz.ustaw_obraz(obraz)
