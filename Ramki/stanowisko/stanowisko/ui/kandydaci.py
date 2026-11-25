"""kandydaci - kolumna "Praca" trybu porannego (E3-A7; nowy uklad E3-U1b wg makiety ``Rano.dc.html``): dane pracy ze stanu,
"Ktory to projekt?" z kandydatami (miniatura, kuweta, zab, typ, pokrycie, "To ten projekt") i przypisanie reczne.

``WidokPracyRano.ustaw(stan, plytka, gniazdo, praca, otwarty_piec)`` pokazuje ``kontroler_api.PracaRano``; wybor osoby wychodzi
sygnalem ``polecenie(nazwa, argumenty)`` (``wybierz_kandydata``, ``przypisz_recznie``, ``cofnij_przypisanie``) - widok sam nie
wola kontrolera poza zapytaniem ``projekty_kuwety`` (lista projektow zlecenia do przypisania recznego, przez funkcje ``projekty``
podana przy budowie). Kolory i napisy statusow - ze stanu i ``statusy``; wyglad - ``motyw``; pozostale napisy - ``napisy_rano``.
Miniatury dekoduje ekran (funkcja ``obraz(sha16, dane)`` -> ``QImage``). Decyzja idzie zawsze do pracy, ktorej dane widok
pokazuje (``praca_id``). Uklad: u gory (przewijane) - naglowek pracy, status, dane projektu, kandydaci, przypisanie reczne;
na STALYM miejscu na dole kolumny - "Przypisz recznie", "Bez projektu", "Cofnij wybor".
"""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QScrollArea, QSizePolicy, QStackedLayout, QVBoxLayout, QWidget

from .. import statusy as ST
from . import motyw
from . import napisy_rano as NR
from .czesci import etykieta, godzina, guzik, wyczysc, znaczek

MINIATURA_PX = 64


def nazwa_plytki(numer) -> str:
    return NR.PLYTKA_NR.format(numer=numer) if numer is not None else NR.PLYTKA_BEZ_NUMERU


def przypisanie_programu(praca) -> bool:
    """S3-16: napis "Przypisanie: program (dopasowanie pewne)" tylko przy pracy przypisanej przez program BEZ konfliktu (ten sam
    projekt w innym gniezdzie = dopasowanie nie jest pewne)."""
    return praca.decyzja is None and praca.przypisanie == "auto" and praca.klasa != "konflikt" and not praca.konflikt_z


class PoleKuwety(QLineEdit):
    """Pole numeru kuwety do przypisania recznego: Enter jest JAWNIE przyjety przez pole (``returnPressed`` = szukaj) i nie
    dochodzi do okna, gdzie oznaczalby "kuweta rozlozona" (recenzja PR #26, D2 - nie zalezy od przebudowy widoku)."""

    def keyPressEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        super().keyPressEvent(zdarzenie)
        if zdarzenie.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            zdarzenie.accept()


class Miniatura(QLabel):
    """Miniatura projektu (PNG z indeksu) w ramce ``px``; bez miniatury - napis."""

    def __init__(self, nazwa: str, px: int = MINIATURA_PX):
        super().__init__()
        self.setObjectName(nazwa)
        self.setFixedSize(px + 4, px + 4)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(motyw.styl_miniatury())
        self.sha16: str | None = None
        self._px = px

    def ustaw(self, sha16: str | None, obraz) -> None:
        self.sha16 = sha16 if obraz is not None else None
        if obraz is None:
            self.setPixmap(QPixmap())
            self.setText(NR.MINIATURA_BRAK)
            return
        self.setText("")
        self.setPixmap(QPixmap.fromImage(obraz).scaled(QSize(self._px, self._px), Qt.AspectRatioMode.KeepAspectRatio,
                                                         Qt.TransformationMode.SmoothTransformation))


class KartaKandydata(QFrame):
    """Jeden kandydat pracy dwuznacznej (makieta): miniatura, "Kuweta n · zab", typ, "pasuje w x %", przycisk "To ten projekt"
    (albo znacznik "wybrany", albo powod, dla ktorego nie da sie go wybrac)."""

    wybrano = Signal(str)

    def __init__(self, nr: int, kandydat, obraz, przypisany: bool, aktywny: bool, u: motyw.Uklad):
        super().__init__()
        self.setObjectName(f"kandydat_{nr}")
        self.setProperty("rola", "kafelek")
        self.setProperty("wybrany", "true" if przypisany else "false")
        calosc = QVBoxLayout(self)
        calosc.setContentsMargins(*((10, 8, 10, 8) if u.zwarty else (12, 12, 12, 12)))
        calosc.setSpacing(8 if u.zwarty else 10)
        uklad = QHBoxLayout()
        uklad.setSpacing(10 if u.zwarty else 12)
        calosc.addLayout(uklad)
        self.miniatura = Miniatura(f"kandydat_{nr}_miniatura", motyw.MINIATURA_KANDYDATA_ZWARTY if u.zwarty else motyw.MINIATURA_KANDYDATA)
        self.miniatura.ustaw(kandydat.sha16, obraz)
        uklad.addWidget(self.miniatura, 0, Qt.AlignmentFlag.AlignTop)
        kolumna = QVBoxLayout()
        kolumna.setSpacing(2)
        naglowek = NR.KUWETA + " " + (kandydat.kuweta or NR.BRAK_DANYCH)
        if kandydat.zeby:
            naglowek += NR.KROPKA + f"{NR.ZAB.lower()} {kandydat.zeby}"
        kolumna.addWidget(etykieta(naglowek, "wyrozniony", f"kandydat_{nr}_kuweta", zawijaj=True))
        kolumna.addWidget(etykieta(kandydat.typ or NR.BRAK_DANYCH, "tresc", f"kandydat_{nr}_zab", zawijaj=True))
        opis = NR.KANDYDAT_NR.format(nr=nr)
        if kandydat.pokrycie is not None:
            opis += NR.KROPKA + NR.KANDYDAT_POKRYCIE.format(procent=round(100 * kandydat.pokrycie))
        kolumna.addWidget(etykieta(opis, "tresc", f"kandydat_{nr}_naglowek", zawijaj=True))
        kolumna.addStretch(1)
        uklad.addLayout(kolumna, 1)
        if przypisany:
            calosc.addWidget(etykieta(NR.KANDYDAT_WYBRANY, "znaczek_nowa", f"kandydat_{nr}_wybrany"), 0, Qt.AlignmentFlag.AlignLeft)
        elif kandydat.projekt_id is None:
            powod = NR.KANDYDAT_POZA_INDEKSEM if kandydat.zlecen == 0 else NR.KANDYDAT_KILKA_ZLECEN.format(n=kandydat.zlecen)
            calosc.addWidget(etykieta(powod, "tresc", f"kandydat_{nr}_powod", zawijaj=True))
        else:
            b = guzik(ST.PRZYCISKI["wybierz_kandydata"], f"kandydat_{nr}_wybierz", "akcent", lambda: self.wybrano.emit(kandydat.sha16),
                      motyw.CEL_KLIKNIECIA)
            b.setEnabled(aktywny)
            calosc.addWidget(b)


class WidokPracyRano(QFrame):
    """Widok pracy porannej po kliknieciu gniazda (kolumna "Praca"). ``praca_id`` - praca, ktorej dane sa pokazane (do niej ida
    decyzje)."""

    polecenie = Signal(str, tuple)
    zamknij = Signal()

    def __init__(self, projekty, obraz):
        super().__init__()
        self.setObjectName("ramka_pracy_rano")
        self._projekty = projekty
        self._obraz = obraz
        self.praca_id: int | None = None
        self._uklad = motyw.UKLAD_WYSOKI
        self._sygnatura = None
        self._przypisanie = False
        self._fokus = False
        self._kuweta_szukana: str | None = None
        self._wyniki: tuple = ()
        self._stos = QStackedLayout(self)
        self._pusty = etykieta(NR.PRACA_PUSTY_WIDOK, "tresc", "praca_rano_pusty", zawijaj=True)
        self._pusty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pusty.setContentsMargins(20, 14, 20, 14)
        self._pusty.setMinimumSize(10, 10)
        self._pusty.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self._stos.addWidget(self._pusty)
        strona = QWidget()
        strona.setObjectName("praca_rano_strona")
        su = QVBoxLayout(strona)
        su.setContentsMargins(0, 0, 0, 0)
        su.setSpacing(0)
        self._przewijanie = QScrollArea()
        self._przewijanie.setObjectName("praca_rano_przewijanie")
        self._przewijanie.setWidgetResizable(True)
        self._przewijanie.setFrameShape(QFrame.Shape.NoFrame)
        self._przewijanie.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._przewijanie.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._wnetrze = QWidget()
        self._wnetrze.setObjectName("praca_rano_wnetrze")
        self._wnetrze.setStyleSheet("QWidget#praca_rano_wnetrze { background: transparent; }")
        self._u = QVBoxLayout(self._wnetrze)
        self._przewijanie.setWidget(self._wnetrze)
        self._przewijanie.viewport().setAutoFillBackground(False)
        su.addWidget(self._przewijanie, 1)
        self._dol = QWidget()
        self._dol.setObjectName("praca_rano_decyzje")
        self._du = QVBoxLayout(self._dol)
        self._du.setSpacing(8)
        su.addWidget(self._dol)
        self._stos.addWidget(strona)
        self.ustaw_uklad(motyw.UKLAD_WYSOKI)

    def ustaw_uklad(self, u: motyw.Uklad) -> None:
        self._uklad = u
        bok = 12 if u.zwarty else 16
        self._u.setContentsMargins(bok, bok, bok, bok)
        self._u.setSpacing(8 if u.zwarty else 10)
        self._du.setContentsMargins(bok, 8, bok, bok)
        self._sygnatura = None

    def otwarty(self) -> bool:
        return self._stos.currentIndex() == 1

    def wyczysc(self) -> None:
        self._stos.setCurrentIndex(0)
        self.praca_id = None
        self._sygnatura = None
        self._przypisanie, self._kuweta_szukana, self._wyniki = False, None, ()

    # --- budowa widoku -------------------------------------------------------------------------------------------------
    def ustaw(self, stan, plytka, gniazdo, praca, otwarty_piec: bool) -> None:
        if praca is None or praca.praca_id != self.praca_id:
            self._przypisanie, self._kuweta_szukana, self._wyniki = False, None, ()
        self.praca_id = praca.praca_id if praca is not None else None
        self._stos.setCurrentIndex(1)
        sygnatura = (plytka.skan_id, plytka.numer, plytka.napis, gniazdo, praca, stan.operator, stan.operatorzy, otwarty_piec, self._przypisanie,
                     self._kuweta_szukana, self._wyniki, self._uklad)
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        wyczysc(self._u)
        wyczysc(self._du)
        u = self._u
        nazwa = nazwa_plytki(plytka.numer)
        wiersz = QHBoxLayout()
        wiersz.setSpacing(8)
        wiersz.addWidget(etykieta(NR.PRACA_TYTUL.format(plytka=nazwa, gniazdo=gniazdo.nr) if gniazdo is not None else NR.PRACA_TYTUL_POZA.format(plytka=nazwa),
                                  "tytul_pracy", "praca_rano_tytul", zawijaj=True), 1)
        wiersz.addWidget(guzik(NR.ZAMKNIJ_SKROT, "praca_rano_zamknij", "lacze", self.zamknij.emit), 0, Qt.AlignmentFlag.AlignTop)
        u.addLayout(wiersz)
        zrodlo = praca if praca is not None else gniazdo
        if zrodlo is None:
            u.addStretch(1)
            self._dol.setVisible(False)
            return
        wiersz = QHBoxLayout()
        wiersz.setSpacing(10)
        status = znaczek(ST.status(zrodlo.status).napis, zrodlo.rgb, "praca_rano_status", motyw.PX_PODSTAWOWY)
        status.setMinimumHeight(28)
        wiersz.addWidget(status, 0, Qt.AlignmentFlag.AlignTop)
        # E3-P14 (poz. 7): gniazdo jest juz klikniete - opis w widoku mowi, co zrobic TERAZ (legenda zostaje przy "kliknij gniazdo")
        opis = NR.OPIS_W_WIDOKU.get(zrodlo.status, "").format(wybierz=ST.PRZYCISKI["wybierz_kandydata"]) or ST.status(zrodlo.status).opis
        wiersz.addWidget(etykieta(opis, "tresc", "praca_rano_opis", zawijaj=True), 1)
        u.addLayout(wiersz)
        if praca is None:
            u.addStretch(1)
            self._dol.setVisible(False)
            return
        # dane przypisanego projektu: miniatura, kuweta, zab, typ. E3-P14 (poz. 9): praca BEZ projektu (dwuznaczna, nieznana) nie ma
        # czego pokazac - puste pola "Kuweta -, Zab -, Typ -" zabieraly miejsce i spychaly "To ten projekt" poza widok
        if praca.projekt_id is not None or praca.kuweta or praca.zeby or praca.typ or praca.miniatura:
            wiersz = QHBoxLayout()
            wiersz.setSpacing(12)
            mini = Miniatura("praca_rano_miniatura", motyw.MINIATURA_KANDYDATA_ZWARTY if self._uklad.zwarty else MINIATURA_PX)
            mini.ustaw(praca.sha16, self._obraz(praca.sha16, praca.miniatura) if praca.miniatura else None)
            wiersz.addWidget(mini, 0, Qt.AlignmentFlag.AlignTop)
            dane = QVBoxLayout()
            dane.setSpacing(2)
            for klucz, podpis, wartosc in (("kuweta", NR.KUWETA, praca.kuweta), ("zab", NR.ZAB, praca.zeby), ("typ", NR.TYP, praca.typ)):
                linia = QHBoxLayout()
                linia.setSpacing(8)
                linia.addWidget(etykieta(podpis, "tresc"))
                linia.addWidget(etykieta(wartosc or NR.BRAK_DANYCH, "wyrozniony", f"praca_rano_{klucz}"))
                linia.addStretch(1)
                dane.addLayout(linia)
            wiersz.addLayout(dane, 1)
            u.addLayout(wiersz)
        if praca.decyzja is not None:
            opis = NR.DECYZJE.get(praca.decyzja, praca.decyzja)
            if praca.decyzja == "przypisanie_reczne" and praca.projekt_id is None:
                opis += f" ({NR.BEZ_PROJEKTU_ZAPISANE})"
            u.addWidget(etykieta(NR.DECYZJA_ZAPISANA.format(decyzja=opis, osoba=praca.operator or NR.BRAK_DANYCH, godzina=godzina(praca.czas_decyzji)),
                                 "tresc", "praca_rano_decyzja", zawijaj=True))
        elif przypisanie_programu(praca):  # S3-16: nie przy konflikcie
            u.addWidget(etykieta(NR.PRZYPISANIE_AUTO, "tresc", "praca_rano_decyzja", zawijaj=True))
        if praca.konflikt_z:
            miejsca = ", ".join(NR.KONFLIKT_MIEJSCE.format(plytka=nazwa_plytki(n), gniazdo=g if g is not None else NR.BRAK_DANYCH) for n, g in praca.konflikt_z)
            u.addWidget(etykieta(NR.KONFLIKT_Z.format(miejsca=miejsca), "uwaga", "praca_rano_konflikt", zawijaj=True))
        if praca.klasa == "poprawka":  # Z9 / A6 D2: "zlecenie juz odhaczone" tylko, gdy naprawde odhaczone (P5)
            u.addWidget(etykieta(NR.POPRAWKA_INFO if praca.zlecenie_odhaczone else NR.JUZ_ROZPOZNANY_INFO, "informacja", "praca_rano_poprawka",
                                 zawijaj=True))
        if praca.domyka_dofrezowanie:
            u.addWidget(etykieta(NR.DOMYKA_DOFREZOWANIE, "informacja", "praca_rano_dofrezowanie", zawijaj=True))
        if praca.kuweta_do_sprawdzenia:
            u.addWidget(etykieta(NR.KUWETA_DO_SPRAWDZENIA, "uwaga", "praca_rano_kuweta_sprawdz", zawijaj=True))
        jest_osoba = stan.operator is not None
        if not praca.dozwolone:
            powod = NR.POWOD_PIEC_ZAMKNIETY if not otwarty_piec else NR.POWOD_SKAN.format(napis=plytka.napis)
            u.addWidget(etykieta(NR.DECYZJE_NIEDOSTEPNE.format(powod=powod), "uwaga", "praca_rano_wyjasnienie", zawijaj=True))
        elif not jest_osoba:
            u.addWidget(etykieta(ST.tekst_komunikatu("brak_operatora" if stan.operatorzy else "pusta_lista_operatorow")[2], "uwaga",
                                 "praca_rano_wyjasnienie", zawijaj=True))
        # kandydaci (praca dwuznaczna, konflikt, korekta przypisania) - jeden pod drugim (makieta)
        if praca.kandydaci and praca.klasa in ("dwuznaczna", "konflikt", "nieznana") or (praca.kandydaci and praca.decyzja is not None):
            u.addWidget(etykieta(NR.KANDYDACI_TYTUL, "naglowek", "praca_rano_kandydaci_tytul"))
            for i, k in enumerate(praca.kandydaci[:2], start=1):
                karta = KartaKandydata(i, k, self._obraz(k.sha16, k.miniatura) if k.miniatura else None,
                                       przypisany=k.projekt_id is not None and k.projekt_id == praca.projekt_id,
                                       aktywny=jest_osoba and "wybierz_kandydata" in praca.dozwolone, u=self._uklad)
                karta.wybrano.connect(lambda sha, p=praca.praca_id: self.polecenie.emit("wybierz_kandydata", (p, sha)))
                u.addWidget(karta)
        if self._przypisanie and "przypisz_recznie" in praca.dozwolone and jest_osoba:
            self._dodaj_przypisanie(praca)
        u.addStretch(1)
        # decyzje na stalym miejscu na dole kolumny
        rzad = QHBoxLayout()
        rzad.setSpacing(8)
        if "przypisz_recznie" in praca.dozwolone:
            b = guzik(ST.PRZYCISKI["przypisz_recznie"], "praca_rano_przypisz", None, self._przelacz_przypisanie, motyw.CEL_KLIKNIECIA)
            b.setCheckable(True)
            b.setChecked(self._przypisanie)
            b.setEnabled(jest_osoba)
            rzad.addWidget(b, 1)
            b = guzik(ST.PRZYCISK_BEZ_PROJEKTU, "praca_rano_bez_projektu", None, lambda p=praca.praca_id: self.polecenie.emit("przypisz_recznie", (p,)),
                      motyw.CEL_KLIKNIECIA)
            b.setEnabled(jest_osoba and not (praca.decyzja == "przypisanie_reczne" and praca.projekt_id is None))
            rzad.addWidget(b, 1)
        if rzad.count():
            self._du.addLayout(rzad)
        if "cofnij_przypisanie" in praca.dozwolone:
            b = guzik(ST.PRZYCISKI["cofnij_przypisanie"], "praca_rano_cofnij", None,
                      lambda p=praca.praca_id, d=praca.decyzja_id: self.polecenie.emit("cofnij_przypisanie", (p, d) if d is not None else (p,)),
                      motyw.CEL_KLIKNIECIA)
            b.setEnabled(jest_osoba)
            self._du.addWidget(b)
        self._dol.setVisible(self._du.count() > 0)

    def _dodaj_przypisanie(self, praca) -> None:
        self._u.addWidget(etykieta(NR.PRZYPISZ_TYTUL, "naglowek", "praca_rano_przypisz_tytul", zawijaj=True))
        wiersz = QHBoxLayout()
        wiersz.setSpacing(8)
        pole = PoleKuwety()
        pole.setObjectName("praca_rano_przypisz_kuweta")
        pole.setMaxLength(8)
        pole.setText(self._kuweta_szukana or "")
        pole.setMinimumHeight(motyw.CEL_KLIKNIECIA)
        pole.returnPressed.connect(lambda: self._szukaj(pole.text(), fokus=True))
        wiersz.addWidget(pole, 1)
        wiersz.addWidget(guzik(NR.PRZYPISZ_POKAZ, "praca_rano_przypisz_pokaz", None, lambda: self._szukaj(pole.text()), motyw.CEL_KLIKNIECIA))
        self._u.addLayout(wiersz)
        self._pole = pole
        if self._fokus:  # Enter w polu: po przebudowie fokus w nowym polu (poprawiany numer nie trafia do numeru kuwety ekranu)
            self._fokus = False
            pole.setFocus(Qt.FocusReason.OtherFocusReason)
        if self._kuweta_szukana is not None and not self._wyniki:
            self._u.addWidget(etykieta(NR.PRZYPISZ_BRAK.format(kuweta=self._kuweta_szukana), "tresc", "praca_rano_przypisz_brak", zawijaj=True))
        for projekt in self._wyniki:
            linia = QHBoxLayout()
            linia.setSpacing(8)
            mini = Miniatura(f"projekt_{projekt.projekt_id}_miniatura", 40)
            mini.ustaw(projekt.sha16, self._obraz(projekt.sha16, projekt.miniatura) if projekt.miniatura else None)
            linia.addWidget(mini)
            napis = NR.PRZYPISZ_PROJEKT.format(zab=projekt.zeby or NR.BRAK_DANYCH, typ=projekt.typ or NR.BRAK_DANYCH,
                                               stan=ST.STANY_PUNKTU.get(projekt.stan, projekt.stan or ""))
            b = guzik(f"{NR.KUWETA} {projekt.kuweta}{NR.KROPKA}{napis}", f"projekt_{projekt.projekt_id}", "lacze",
                      lambda pid=projekt.projekt_id, p=praca.praca_id: self.polecenie.emit("przypisz_recznie", (p, pid)))
            b.setEnabled(projekt.projekt_id != praca.projekt_id)
            linia.addWidget(b, 1)
            self._u.addLayout(linia)

    def _przelacz_przypisanie(self) -> None:
        self._przypisanie = not self._przypisanie
        self._sygnatura = None
        self.odswiez_sam()

    def _szukaj(self, tekst: str, fokus: bool = False) -> None:
        self._fokus = fokus
        tekst = (tekst or "").strip()
        self._kuweta_szukana = tekst or None
        self._wyniki = tuple(self._projekty(tekst)) if tekst else ()
        self._sygnatura = None
        self.odswiez_sam()

    def odswiez_sam(self) -> None:
        """Przebudowa po zmianie wlasnego stanu widoku (panel przypisania) - ekran poda ostatni stan."""
        if self._na_zmiane is not None:
            self._na_zmiane()

    _na_zmiane = None

    def po_zmianie(self, funkcja) -> None:
        self._na_zmiane = funkcja

    def szukaj(self, kuweta: str) -> None:
        """Przypisanie reczne: projekty kuwety ``kuweta`` (to samo, co wpisanie numeru w pole i "Pokaz projekty")."""
        self._przypisanie = True
        self._szukaj(kuweta)
