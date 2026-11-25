"""okno_instalatora - okno instalacji programu "Stanowisko" (E3-I1): Foldery -> Osoby -> Instalacja -> Gotowe.

Start z paczki: ``Instaluj.cmd`` -> ``python\\pythonw.exe -I -B program\\instalacja\\okno_instalatora.py --paczka <paczka>``.
Okno dziala na Pythonie z paczki i bibliotece Qt z katalogu ``okno/`` paczki (wycinek kol PySide6 i shiboken6 z paczki:
QtCore, QtGui, QtWidgets i wtyczka okien) - ZANIM powstanie srodowisko wersji. Logika (kontrole, polecenie instalatora, kody,
start programu) jest w ``kreator.py``; okno tylko ja pokazuje. Instalacja to ``instalator.py zainstaluj`` jako proces
potomny z ukryta konsola - te same kroki, kody wyjscia i dziennik co ``zainstaluj.cmd``.

Tryb bez okna (testy; parametry zamiast klikniec, ta sama logika)::

    okno_instalatora.py --bez-okna --folder-skanow X [--folder-projektow Y] [--katalog K] --osoba A [--osoba B ...]

Zrzuty 4 krokow (dane przykladowe, bez instalacji): ``okno_instalatora.py --zrzuty KATALOG``.
Wyglad wg makiety ``etap3/nowy_interfejs/makieta/Instalator.dc.html`` (kolory jak ``stanowisko/ui/motyw.py``).
"""
from __future__ import annotations

import argparse
import sys
import threading
from pathlib import Path


def _paczka_z_argumentow(argv: list[str]) -> Path:
    for i, a in enumerate(argv[:-1]):
        if a == "--paczka":
            return Path(argv[i + 1]).resolve()
    return Path(__file__).resolve().parent.parent.parent


if __name__ == "__main__":  # uruchomiony z paczki (python -I): katalog skryptu i biblioteka okna z paczki na sys.path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    if (_paczka_z_argumentow(sys.argv[1:]) / "okno").is_dir():
        sys.path.insert(0, str(_paczka_z_argumentow(sys.argv[1:]) / "okno"))

try:
    from instalacja import instalator as I
    from instalacja import kreator as K
    from instalacja import napisy_instalatora as N
except ImportError:  # pragma: no cover - droga z paczki
    import instalator as I  # type: ignore[no-redef]
    import kreator as K  # type: ignore[no-redef]
    import napisy_instalatora as N  # type: ignore[no-redef]

# --- wyglad (makieta Instalator.dc.html; wartosci jak stanowisko/ui/motyw.py) ---------------------------------------------
TLO, POWIERZCHNIA, WGLEBIENIE, AKCENT, NA_AKCENCIE = "#191919", "#303030", "#242424", "#338CED", "#0F1720"
AKCENT_TEKST, AKCENT_JASNY, AKCENT_FOKUS, LINIA, LINIA_TLA, OBWODKA = "#9CC9F9", "#4A9BF0", "#6FB0F5", "#3F3F3F", "#2B2B2B", "#4A4A4A"
OBWODKA_MOCNA, TEKST, TEKST_POMOCNICZY = "#6A6A6A", "#F2F2F2", "#B8B8B8"
POZIOMY = {"info": ("#1D2733", AKCENT), "ostrzezenie": ("#2B2616", "#C9A227"), "blad": ("#2E1C1D", "#D9575B"), "ok": ("#1D2733", AKCENT)}
OBWODKA_BRAKU = "#E2B93B"  # pole "nie wybrano" (makieta: folder projektow)
SZEROKOSC, WYSOKOSC = 900, 600

ARKUSZ = f"""
QWidget {{ background: {TLO}; color: {TEKST}; font-family: 'Segoe UI Variable Text', 'Segoe UI'; font-size: 14px; }}
QFrame#nawigacja {{ background: {POWIERZCHNIA}; border-right: 1px solid {LINIA}; }}
QFrame#nawigacja QLabel {{ background: transparent; }}
QFrame#pasek {{ border-top: 1px solid {LINIA_TLA}; }}
QLabel#tytul {{ font-size: 22px; font-weight: 600; }}
QLabel#nazwa {{ font-size: 18px; font-weight: 600; }}
QLabel#pomocniczy, QLabel#opis {{ color: {TEKST_POMOCNICZY}; font-size: 13px; }}
QLabel#etykieta {{ font-weight: 600; }}
QLineEdit, QListWidget, QPlainTextEdit {{ background: {WGLEBIENIE}; border: 1px solid {OBWODKA}; border-radius: 4px; padding: 0 12px;
    min-height: 42px; color: {TEKST}; selection-background-color: {AKCENT}; selection-color: {NA_AKCENCIE}; }}
QListWidget, QPlainTextEdit {{ padding: 6px; }}
QListWidget::item {{ min-height: 32px; }}
QListWidget::item:selected {{ background: #1D2733; border: 1px solid {AKCENT}; color: {TEKST}; }}
QLineEdit[brak="true"] {{ border: 1px solid {OBWODKA_BRAKU}; }}
QLineEdit:disabled {{ color: {TEKST_POMOCNICZY}; }}
QPushButton {{ min-height: 42px; padding: 0 16px; border: 1px solid {OBWODKA}; border-radius: 4px; background: {POWIERZCHNIA}; color: {TEKST}; }}
QPushButton:hover {{ background: #3A3A3A; }}
QPushButton:focus {{ border: 2px solid {AKCENT_FOKUS}; }}
QPushButton:disabled {{ color: #7A7A7A; border-color: {LINIA}; }}
QPushButton[rola="glowny"] {{ background: {AKCENT}; color: {NA_AKCENCIE}; border: 0; font-weight: 600; padding: 0 24px; }}
QPushButton[rola="glowny"]:hover {{ background: {AKCENT_JASNY}; }}
QPushButton[rola="glowny"]:disabled {{ background: #2A4A6E; color: #8FA3B8; }}
QPushButton[rola="wskazany"] {{ border: 1px solid {AKCENT}; color: {AKCENT_TEKST}; font-weight: 600; }}
QPushButton[rola="przezroczysty"] {{ background: transparent; }}
QProgressBar {{ background: {WGLEBIENIE}; border: 1px solid {OBWODKA}; border-radius: 4px; max-height: 8px; }}
QProgressBar::chunk {{ background: {AKCENT}; }}
"""


def zaladuj_qt():
    from PySide6 import QtCore, QtGui, QtWidgets  # noqa: PLC0415

    return QtCore, QtGui, QtWidgets


try:
    QtCore, QtGui, QtWidgets = zaladuj_qt()
    _BLAD_QT = None
except Exception as _e:  # noqa: BLE001 - brak biblioteki okna: komunikat systemowy (main), nie slad wyjatku
    QtCore = QtGui = QtWidgets = None
    _BLAD_QT = _e


def _okienko_systemowe(tekst: str) -> None:
    """Komunikat bez Qt (Windows: MessageBoxW) - gdy biblioteki okna nie da sie zaladowac."""
    try:
        import ctypes  # noqa: PLC0415

        ctypes.windll.user32.MessageBoxW(None, tekst, N.TYTUL_OKNA, 0x10)
    except Exception:  # noqa: BLE001
        print(tekst, file=sys.stderr)


if QtWidgets is not None:

    class _Sygnaly(QtCore.QObject):
        wiersz = QtCore.Signal(str)
        koniec = QtCore.Signal(int)

    class OknoInstalatora(QtWidgets.QWidget):
        """Kreator 4 krokow. ``uruchom`` = funkcja (polecenie, na_wiersz, przerwij) -> kod (testy podstawiaja atrape)."""

        def __init__(self, paczka: Path, *, katalog: str = I.KATALOG_DOMYSLNY, uruchom=None, python: Path | None = None,
                     skrot_katalog: Path | None = None, start_programu=None):
            super().__init__()
            self.paczka = Path(paczka)
            self.info = K.informacje_paczki(self.paczka)
            self.wybor = K.Wybor(katalog=katalog)
            self._uruchom = uruchom or K.uruchom_instalacje
            self._python = python
            self._skrot_katalog = skrot_katalog
            self._start = start_programu or K.uruchom_program
            self._przerwij = False
            self._watek: threading.Thread | None = None
            self.postep = K.Postep()
            self.kod: int | None = None
            self.krok = 0
            self.aktualizacja: dict | None = None
            self._sygnaly = _Sygnaly()
            self._sygnaly.wiersz.connect(self._wiersz)
            self._sygnaly.koniec.connect(self._koniec)
            self.setWindowTitle(N.TYTUL_OKNA)
            self.setStyleSheet(ARKUSZ)
            self.resize(SZEROKOSC, WYSOKOSC)
            self.setMinimumSize(SZEROKOSC, WYSOKOSC)
            uklad = QtWidgets.QHBoxLayout(self)
            uklad.setContentsMargins(0, 0, 0, 0)
            uklad.setSpacing(0)
            uklad.addWidget(self._nawigacja())
            prawa = QtWidgets.QVBoxLayout()
            prawa.setContentsMargins(0, 0, 0, 0)
            prawa.setSpacing(0)
            self.strony = QtWidgets.QStackedWidget()
            for budowa in (self._strona_folderow, self._strona_osob, self._strona_instalacji, self._strona_gotowe):
                self.strony.addWidget(budowa())
            prawa.addWidget(self.strony, 1)
            prawa.addWidget(self._pasek())
            uklad.addLayout(prawa, 1)
            self._odswiez_cel()
            self._pokaz(0)

        # --- budowa ------------------------------------------------------------------------------------------------------
        def _etykieta(self, tekst: str, nazwa: str = "", zawijaj: bool = True):
            e = QtWidgets.QLabel(tekst)
            if nazwa:
                e.setObjectName(nazwa)
            e.setWordWrap(zawijaj)
            return e

        def _nawigacja(self):
            ramka = QtWidgets.QFrame()
            ramka.setObjectName("nawigacja")
            ramka.setFixedWidth(240)
            u = QtWidgets.QVBoxLayout(ramka)
            u.setContentsMargins(24, 28, 24, 28)
            u.setSpacing(2)
            u.addWidget(self._etykieta(N.NAZWA, "nazwa"))
            u.addWidget(self._etykieta(N.PODTYTUL.format(wersja=self.info["wersja"]), "pomocniczy"))
            u.addSpacing(36)
            self._znaczniki = []
            for i, nazwa in enumerate(N.KROKI):
                wiersz = QtWidgets.QHBoxLayout()
                wiersz.setSpacing(12)
                kolko = QtWidgets.QLabel(str(i + 1))
                kolko.setFixedSize(26, 26)
                kolko.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                napis = QtWidgets.QLabel(nazwa)
                wiersz.addWidget(kolko)
                wiersz.addWidget(napis, 1)
                u.addLayout(wiersz)
                u.addSpacing(16)
                self._znaczniki.append((kolko, napis))
            u.addStretch(1)
            u.addWidget(self._etykieta(N.STOPKA_KROKOW, "pomocniczy"))
            return ramka

        def _strona(self, tytul: str, podtytul: str = ""):
            strona = QtWidgets.QWidget()
            u = QtWidgets.QVBoxLayout(strona)
            u.setContentsMargins(36, 32, 36, 12)
            u.setSpacing(6)
            t = self._etykieta(tytul, "tytul")
            u.addWidget(t)
            p = self._etykieta(podtytul, "pomocniczy")
            u.addWidget(p)
            u.addSpacing(14)
            return strona, u, t, p

        def _pole(self, u, etykieta: str, opis: str, przycisk: str):
            u.addWidget(self._etykieta(etykieta, "etykieta"))
            if opis:
                u.addWidget(self._etykieta(opis, "opis"))
            wiersz = QtWidgets.QHBoxLayout()
            wiersz.setSpacing(8)
            pole = QtWidgets.QLineEdit()
            pole.setAccessibleName(etykieta)
            b = QtWidgets.QPushButton(przycisk)
            b.setAccessibleName(f"{przycisk} {etykieta.lower()}")
            wiersz.addWidget(pole, 1)
            wiersz.addWidget(b)
            u.addLayout(wiersz)
            u.addSpacing(12)
            return pole, b

        def _komunikat(self):
            k = QtWidgets.QLabel()
            k.setWordWrap(True)
            k.setTextFormat(QtCore.Qt.TextFormat.PlainText)
            k.setVisible(False)
            return k

        def _ustaw_komunikat(self, etykieta, tekst: str, poziom: str = "blad") -> None:
            tlo, obwodka = POZIOMY[poziom]
            etykieta.setStyleSheet(f"background: {tlo}; border: 1px solid {obwodka}; border-radius: 4px; padding: 10px 12px;")
            etykieta.setText(tekst)
            etykieta.setVisible(bool(tekst))

        def _strona_folderow(self):
            strona, u, _, _ = self._strona(N.FOLDERY_TYTUL, N.FOLDERY_PODTYTUL)
            self.pole_skanow, b1 = self._pole(u, N.SKANY, N.SKANY_OPIS, N.WYBIERZ)
            self.pole_projektow, b2 = self._pole(u, N.PROJEKTY, N.PROJEKTY_OPIS, N.WYBIERZ)
            self.pole_celu, b3 = self._pole(u, N.CEL, "", N.ZMIEN)
            u.takeAt(u.count() - 1)  # bez odstepu pod polem miejsca: pod nim opis miejsca na dysku
            self.napis_miejsca = self._etykieta("", "opis")
            u.addWidget(self.napis_miejsca)
            u.addSpacing(10)
            for pole in (self.pole_skanow, self.pole_projektow):
                pole.setPlaceholderText(N.NIE_WYBRANO)
                pole.textChanged.connect(self._oznacz_puste)
            self.pole_celu.setText(self.wybor.katalog)
            self.pole_celu.editingFinished.connect(self._odswiez_cel)
            b1.clicked.connect(lambda: self._wybierz_folder(self.pole_skanow))
            b2.clicked.connect(lambda: self._wybierz_folder(self.pole_projektow))
            b3.clicked.connect(lambda: (self._wybierz_folder(self.pole_celu), self._odswiez_cel()))
            self._przyciski_folderow = (b1, b2)
            self.komunikat_folderow = self._komunikat()
            u.addWidget(self.komunikat_folderow)
            u.addStretch(1)
            self._oznacz_puste()
            return strona

        def _strona_osob(self):
            strona, u, _, self.podtytul_osob = self._strona(N.OSOBY_TYTUL, N.OSOBY_PODTYTUL)
            wiersz = QtWidgets.QHBoxLayout()
            wiersz.setSpacing(8)
            self.pole_osoby = QtWidgets.QLineEdit()
            self.pole_osoby.setPlaceholderText(N.OSOBA_POLE)
            self.pole_osoby.setAccessibleName(N.OSOBA_POLE)
            self.pole_osoby.returnPressed.connect(self.dodaj_osobe)
            self.przycisk_dodaj = QtWidgets.QPushButton(N.DODAJ)
            self.przycisk_dodaj.setProperty("rola", "wskazany")
            self.przycisk_dodaj.clicked.connect(self.dodaj_osobe)
            wiersz.addWidget(self.pole_osoby, 1)
            wiersz.addWidget(self.przycisk_dodaj)
            u.addLayout(wiersz)
            u.addSpacing(8)
            self.lista_osob = QtWidgets.QListWidget()
            self.lista_osob.setAccessibleName(N.KROKI[1])
            u.addWidget(self.lista_osob, 1)
            wiersz = QtWidgets.QHBoxLayout()
            self.przycisk_usun = QtWidgets.QPushButton(N.USUN)
            self.przycisk_usun.clicked.connect(self.usun_osobe)
            wiersz.addWidget(self.przycisk_usun)
            wiersz.addStretch(1)
            u.addLayout(wiersz)
            self.komunikat_osob = self._komunikat()
            u.addWidget(self.komunikat_osob)
            return strona

        def _strona_instalacji(self):
            strona, u, self.tytul_instalacji, self.opis_instalacji = self._strona(N.INSTALACJA_TYTUL, N.INSTALACJA_TRWA)
            siatka = QtWidgets.QGridLayout()
            siatka.setHorizontalSpacing(16)
            siatka.setVerticalSpacing(4)
            self._stany_krokow = []
            for i, nazwa in enumerate(N.KROKI_INSTALATORA):
                n = QtWidgets.QLabel(f"{i + 1}. {nazwa}")
                s = QtWidgets.QLabel("")
                s.setObjectName("pomocniczy")
                siatka.addWidget(n, i, 0)
                siatka.addWidget(s, i, 1)
                self._stany_krokow.append((n, s))
            siatka.setColumnStretch(2, 1)
            u.addLayout(siatka)
            u.addSpacing(8)
            self.pasek_postepu = QtWidgets.QProgressBar()
            self.pasek_postepu.setTextVisible(False)
            self.pasek_postepu.setRange(0, 9)
            u.addWidget(self.pasek_postepu)
            self.komunikat_instalacji = self._komunikat()
            u.addWidget(self.komunikat_instalacji)
            self.przycisk_szczegolow = QtWidgets.QPushButton(N.SZCZEGOLY)
            self.przycisk_szczegolow.setProperty("rola", "przezroczysty")
            self.przycisk_szczegolow.setCheckable(True)
            self.szczegoly = QtWidgets.QPlainTextEdit()
            self.szczegoly.setReadOnly(True)
            self.szczegoly.setVisible(False)
            self.przycisk_szczegolow.toggled.connect(self.szczegoly.setVisible)
            wiersz = QtWidgets.QHBoxLayout()
            wiersz.addWidget(self.przycisk_szczegolow)
            wiersz.addStretch(1)
            u.addLayout(wiersz)
            u.addWidget(self.szczegoly, 1)
            u.addStretch(0)
            return strona

        def _strona_gotowe(self):
            strona, u, _, self.opis_gotowe = self._strona(N.GOTOWE_TYTUL, "")
            self.opis_gotowe.setObjectName("")
            self.komunikat_ikon = self._komunikat()
            u.addWidget(self.komunikat_ikon)
            self.komunikat_ramek = self._komunikat()
            u.addWidget(self.komunikat_ramek)
            u.addSpacing(12)
            wiersz = QtWidgets.QHBoxLayout()
            wiersz.setSpacing(10)
            self.przycisk_uruchom = QtWidgets.QPushButton(N.URUCHOM_PROGRAM)
            self.przycisk_uruchom.setProperty("rola", "glowny")
            self.przycisk_uruchom.clicked.connect(lambda: self.uruchom_program("stanowisko"))
            self.przycisk_dnia = QtWidgets.QPushButton(N.URUCHOM_DZIEN_SKANERA)
            self.przycisk_dnia.clicked.connect(lambda: self.uruchom_program("dzien_skanera"))
            wiersz.addWidget(self.przycisk_uruchom)
            wiersz.addWidget(self.przycisk_dnia)
            wiersz.addStretch(1)
            u.addLayout(wiersz)
            self.komunikat_startu = self._komunikat()
            u.addWidget(self.komunikat_startu)
            u.addStretch(1)
            return strona

        def _pasek(self):
            ramka = QtWidgets.QFrame()
            ramka.setObjectName("pasek")
            u = QtWidgets.QHBoxLayout(ramka)
            u.setContentsMargins(36, 18, 36, 18)
            u.setSpacing(10)
            u.addStretch(1)
            self.przycisk_anuluj = QtWidgets.QPushButton(N.ANULUJ)
            self.przycisk_anuluj.setProperty("rola", "przezroczysty")
            self.przycisk_wstecz = QtWidgets.QPushButton(N.WSTECZ)
            self.przycisk_dalej = QtWidgets.QPushButton(N.DALEJ)
            self.przycisk_dalej.setProperty("rola", "glowny")
            self.przycisk_dalej.setDefault(True)
            self.przycisk_anuluj.clicked.connect(self.close)
            self.przycisk_wstecz.clicked.connect(self.wstecz)
            self.przycisk_dalej.clicked.connect(self.dalej)
            for b in (self.przycisk_anuluj, self.przycisk_wstecz, self.przycisk_dalej):
                u.addWidget(b)
            return ramka

        # --- zachowanie -------------------------------------------------------------------------------------------------
        def _wybierz_folder(self, pole) -> None:
            start = pole.text().strip() or str(Path.home())
            wybrany = QtWidgets.QFileDialog.getExistingDirectory(self, N.WYBOR_FOLDERU, start)
            if wybrany:
                pole.setText(str(Path(wybrany)))

        def _oznacz_puste(self) -> None:
            for pole in (self.pole_skanow, self.pole_projektow):
                pole.setProperty("brak", not pole.text().strip() and pole.isEnabled())
                pole.style().unpolish(pole)
                pole.style().polish(pole)

        def _odswiez_cel(self) -> None:
            """Miejsce instalacji zmienione: wolne miejsce i rozpoznanie istniejacej instalacji (aktualizacja)."""
            katalog = self.pole_celu.text().strip()
            potrzeba = self.info["potrzebne_mb"]
            wolne = K.wolne_mb(katalog) if katalog else None
            self.napis_miejsca.setText(N.MIEJSCE.format(potrzeba=K.tekst_mb(potrzeba), wolne=K.tekst_mb(wolne)) if wolne is not None
                                       else N.MIEJSCE_NIEZNANE.format(potrzeba=K.tekst_mb(potrzeba)))
            self.aktualizacja = K.istniejaca_instalacja(katalog) if katalog else None
            for pole, b in zip((self.pole_skanow, self.pole_projektow), self._przyciski_folderow):
                pole.setEnabled(self.aktualizacja is None)
                b.setEnabled(self.aktualizacja is None)
            if self.aktualizacja is not None:
                self.pole_skanow.setText(self.aktualizacja["folder_skanow"])
                self.pole_projektow.setText(self.aktualizacja["folder_projektow"])
                self._ustaw_komunikat(self.komunikat_folderow, N.AKTUALIZACJA.format(wersja=self.aktualizacja["wersja"]), "info")
            else:
                self._ustaw_komunikat(self.komunikat_folderow, "")
            self._oznacz_puste()

        def _pokaz(self, krok: int) -> None:
            self.krok = krok
            self.strony.setCurrentIndex(krok)
            for i, (kolko, napis) in enumerate(self._znaczniki):
                aktywny, zrobiony = i == krok, i < krok
                tlo = AKCENT if aktywny else ("transparent")
                obwodka = AKCENT if aktywny or zrobiony else OBWODKA_MOCNA
                kolor = NA_AKCENCIE if aktywny else (AKCENT_TEKST if zrobiony else TEKST_POMOCNICZY)
                kolko.setStyleSheet(f"border: 1px solid {obwodka}; border-radius: 13px; background: {tlo}; color: {kolor}; "
                                    "font-size: 13px; font-weight: 600;")
                napis.setStyleSheet(f"color: {TEKST if aktywny else TEKST_POMOCNICZY}; font-weight: {600 if aktywny else 400};")
            self.przycisk_wstecz.setVisible(krok in (1,))
            self.przycisk_anuluj.setVisible(krok in (0, 1))
            self.przycisk_dalej.setText({0: N.DALEJ, 1: N.INSTALUJ, 2: N.ZAMKNIJ, 3: N.ZAMKNIJ}[krok])
            self.przycisk_dalej.setEnabled(krok != 2)
            if krok == 1:
                self._pokaz_osoby()
            if krok == 3:
                self.przycisk_uruchom.setFocus()

        def _pokaz_osoby(self) -> None:
            akt = self.aktualizacja is not None
            if akt:
                self.lista_osob.clear()
                self.lista_osob.addItems(self.aktualizacja["osoby"])
            self.podtytul_osob.setText(N.OSOBY_AKTUALIZACJA if akt else N.OSOBY_PODTYTUL)
            for w in (self.pole_osoby, self.przycisk_dodaj, self.przycisk_usun):
                w.setEnabled(not akt)
            self._ustaw_komunikat(self.komunikat_osob, "")
            if not akt:
                self.pole_osoby.setFocus()

        def ustaw_wybor(self, wybor: K.Wybor) -> None:
            """Wypelnia pola okna (testy, zrzuty) - jak wpisanie recznie."""
            self.pole_skanow.setText(wybor.folder_skanow)
            self.pole_projektow.setText(wybor.folder_projektow)
            self.pole_celu.setText(wybor.katalog)
            self._odswiez_cel()
            if self.aktualizacja is None:
                self.lista_osob.clear()
                self.lista_osob.addItems(wybor.osoby)

        def biezacy_wybor(self) -> K.Wybor:
            osoby = [] if self.aktualizacja is not None else [self.lista_osob.item(i).text() for i in range(self.lista_osob.count())]
            return K.Wybor(self.pole_skanow.text().strip(), self.pole_projektow.text().strip(), self.pole_celu.text().strip(), osoby)

        def dodaj_osobe(self) -> bool:
            osoby = [self.lista_osob.item(i).text() for i in range(self.lista_osob.count())]
            blad = K.sprawdz_osobe(self.pole_osoby.text(), osoby)
            if blad:
                self._ustaw_komunikat(self.komunikat_osob, blad)
                return False
            self.lista_osob.addItem(self.pole_osoby.text().strip())
            self.pole_osoby.clear()
            self._ustaw_komunikat(self.komunikat_osob, "")
            return True

        def usun_osobe(self) -> None:
            wiersz = self.lista_osob.currentRow()
            if wiersz < 0 and self.lista_osob.count():
                wiersz = self.lista_osob.count() - 1
            if wiersz >= 0:
                self.lista_osob.takeItem(wiersz)

        def wstecz(self) -> None:
            if self.krok == 1:
                self._pokaz(0)

        def dalej(self) -> None:
            if self.krok == 0:
                self._odswiez_cel()
                bledy, uwagi = K.sprawdz_foldery(self.biezacy_wybor(), self.info["potrzebne_mb"])
                if bledy:
                    self._ustaw_komunikat(self.komunikat_folderow, "\n".join(bledy), "blad")
                    return
                if uwagi and not getattr(self, "_uwagi_pokazane", None) == uwagi:  # uwaga (folder projektow) - raz, potem dalej
                    self._uwagi_pokazane = uwagi
                    self._ustaw_komunikat(self.komunikat_folderow, "\n".join(uwagi), "ostrzezenie")
                    return
                self._pokaz(1)
            elif self.krok == 1:
                if self.pole_osoby.text().strip() and self.aktualizacja is None and not self.dodaj_osobe():
                    return
                bledy = [] if self.aktualizacja is not None else K.sprawdz_osoby(self.biezacy_wybor().osoby)
                if bledy:
                    self._ustaw_komunikat(self.komunikat_osob, "\n".join(bledy), "blad")
                    return
                self._pokaz(2)
                self.instaluj()
            elif self.krok == 2 and self.kod not in (None, 0):
                self.close()
            elif self.krok == 3:
                self.close()

        def polecenie(self) -> list[str]:
            polecenie = K.polecenie_instalacji(self.paczka, self.biezacy_wybor(), self.aktualizacja is not None, self._python)
            if self._skrot_katalog is not None:
                polecenie += ["--skrot-katalog", str(self._skrot_katalog)]
            return polecenie

        def instaluj(self) -> None:
            """Krok 3: instalator w osobnym watku (proces potomny); wiersze wracaja sygnalem do watku okna."""
            self.kod, self.postep, self._przerwij = None, K.Postep(), False
            self.szczegoly.clear()
            self.pasek_postepu.setValue(0)
            self.tytul_instalacji.setText(N.INSTALACJA_TYTUL)
            self.opis_instalacji.setText(N.INSTALACJA_TRWA)
            self._ustaw_komunikat(self.komunikat_instalacji, "")
            self.przycisk_dalej.setEnabled(False)
            self.przycisk_dalej.setText(N.ZAMKNIJ)
            for n, s in self._stany_krokow:
                s.setText("")
            polecenie = self.polecenie()

            def praca():
                try:
                    kod = self._uruchom(polecenie, self._sygnaly.wiersz.emit, lambda: self._przerwij)
                except OSError as e:
                    self._sygnaly.wiersz.emit("BLAD: " + N.NIE_URUCHOMIONO.format(blad=type(e).__name__))
                    kod = I.KOD_PACZKA
                self._sygnaly.koniec.emit(int(kod))

            self._watek = threading.Thread(target=praca, name="instalator", daemon=True)
            self._watek.start()

        def _wiersz(self, tekst: str) -> None:
            poprzedni = self.postep.krok
            self.postep.wiersz(tekst)
            self.szczegoly.appendPlainText(tekst)
            if self.postep.krok != poprzedni:
                for i, (_, s) in enumerate(self._stany_krokow):
                    s.setText(N.STAN_GOTOWE if i + 1 < self.postep.krok else (N.STAN_TRWA if i + 1 == self.postep.krok else ""))
                self.pasek_postepu.setValue(self.postep.krok - 1)

        def _koniec(self, kod: int) -> None:
            self.kod = kod
            self._watek = None
            if kod == 0:
                for _, s in self._stany_krokow:
                    s.setText(N.STAN_GOTOWE)
                self.pasek_postepu.setValue(9)
                self._pokaz_gotowe()
                return
            if self.postep.krok:
                self._stany_krokow[self.postep.krok - 1][1].setText(N.STAN_BLAD)
            self.tytul_instalacji.setText(N.INSTALACJA_BLAD_TYTUL)
            self.opis_instalacji.setText("")
            tekst = [K.zdanie_kodu(kod)] + self.postep.bledy[-2:] + [N.CO_ZROBIC.format(rada=r) for r in self.postep.rady[-1:]]
            tekst.append(N.DZIENNIK.format(plik=Path(self.pole_celu.text().strip()) / I.PLIK_DZIENNIKA))
            self._ustaw_komunikat(self.komunikat_instalacji, "\n".join(tekst), "ostrzezenie" if kod == I.KOD_WSTRZYMANA else "blad")
            self.przycisk_wstecz.setVisible(True)
            self.przycisk_wstecz.setText(N.SPROBUJ_PONOWNIE)
            try:
                self.przycisk_wstecz.clicked.disconnect()
            except (RuntimeError, TypeError):
                pass
            self.przycisk_wstecz.clicked.connect(self._ponow)
            self.przycisk_dalej.setEnabled(True)
            self.przycisk_dalej.setText(N.ZAMKNIJ)

        def _ponow(self) -> None:
            self.przycisk_wstecz.setText(N.WSTECZ)
            self.przycisk_wstecz.clicked.disconnect()
            self.przycisk_wstecz.clicked.connect(self.wstecz)
            self._odswiez_cel()
            self._pokaz(0)

        def _pokaz_gotowe(self) -> None:
            katalog = Path(self.pole_celu.text().strip())
            self.opis_gotowe.setText(N.GOTOWE_OPIS.format(wersja=self.info["wersja"], katalog=katalog))
            zalozone = [n for n, (ok, _) in self.postep.skroty.items() if ok]
            braki = [N.IKONA_BRAK.format(nazwa=n, plik=Path(p).name) for n, (ok, p) in self.postep.skroty.items() if not ok]
            tekst = ([N.IKONY_SA.format(ikony=", ".join(f"„{n}”" for n in zalozone))] if zalozone else []) + braki
            self._ustaw_komunikat(self.komunikat_ikon, "\n".join(tekst), "ostrzezenie" if braki else "info")
            self._ustaw_komunikat(self.komunikat_ramek, N.RAMKI_WYLACZONE if self.postep.ramki_wylaczone else "", "info")
            self._pokaz(3)

        def uruchom_program(self, cel: str) -> bool:
            katalog = Path(self.pole_celu.text().strip())
            ok = self._start(katalog, cel)
            if ok:
                self._ustaw_komunikat(self.komunikat_startu, N.URUCHAMIAM, "info")
                QtCore.QTimer.singleShot(1500, self.close)
            else:
                nazwa, skrypt = next((n, s) for n, c, s in I.SKROTY if c == cel)
                self._ustaw_komunikat(self.komunikat_startu, N.IKONA_BRAK.format(nazwa=nazwa, plik=skrypt), "blad")
            return ok

        def closeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
            if self._watek is not None and self._watek.is_alive():
                odp = QtWidgets.QMessageBox.question(self, N.TYTUL_OKNA, N.PRZERWANIE_PYTANIE)
                if odp != QtWidgets.QMessageBox.StandardButton.Yes:
                    zdarzenie.ignore()
                    return
                self._przerwij = True
            zdarzenie.accept()


def zrzuty(paczka: Path, katalog_zrzutow: Path) -> list[Path]:
    """Zrzuty 4 krokow okna z danymi przykladowymi (bez instalacji): instalator_1_foldery.png ... instalator_4_gotowe.png."""
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    katalog_zrzutow.mkdir(parents=True, exist_ok=True)
    wiersze = ["[1/9] Sumy SHA-256 paczki...", "[2/9] Python 3.12 z paczki...", "[3/9] Katalog instalacji C:\\Stanowisko...",
               "[4/9] Ustawienia...", "[5/9] Katalog wersji...", "      instalacja 73 pakietow z kol paczki (bez sieci) - to trwa kilka minut..."]
    okno = OknoInstalatora(paczka, katalog="C:\\Stanowisko", uruchom=lambda *_: 0, start_programu=lambda *_: True)
    okno.aktualizacja = None
    okno.pole_skanow.setText("C:\\Skany")
    okno.pole_projektow.setText("")
    okno._oznacz_puste()
    okno.show()
    pliki = []

    def zrzut(nazwa: str) -> None:
        app.processEvents()
        plik = katalog_zrzutow / nazwa
        okno.grab().save(str(plik))
        pliki.append(plik)

    zrzut("instalator_1_foldery.png")
    okno.lista_osob.addItems(["Anna Kowalska", "Piotr W."])
    okno._pokaz(1)
    zrzut("instalator_2_osoby.png")
    okno._pokaz(2)
    for w in wiersze:
        okno._wiersz(w)
    zrzut("instalator_3_instalacja.png")
    for w in ["SKROT ZALOZONY: Stanowisko | C:\\Users\\Public\\Desktop\\Stanowisko.lnk",
              "SKROT ZALOZONY: Dzie\u0144 skanera | C:\\Users\\Public\\Desktop\\Dzie\u0144 skanera.lnk"]:
        okno._wiersz(w)
    okno._koniec(0)
    zrzut("instalator_4_gotowe.png")
    okno.close()
    return pliki


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    p = argparse.ArgumentParser(prog="okno_instalatora", description='Okno instalatora programu "Stanowisko".')
    p.add_argument("--paczka", type=Path, default=Path(__file__).resolve().parent.parent.parent, help="katalog rozpakowanej paczki")
    p.add_argument("--katalog", default=I.KATALOG_DOMYSLNY, help="miejsce instalacji (domyslnie C:\\Stanowisko)")
    p.add_argument("--bez-okna", action="store_true", help="tryb bez okna: parametry zamiast klikniec (ta sama logika)")
    p.add_argument("--folder-skanow", default="")
    p.add_argument("--folder-projektow", default="")
    p.add_argument("--osoba", action="append", default=[])
    p.add_argument("--python", type=Path, default=None, help="(proby) Python instalatora, gdy paczka nie ma katalogu python")
    p.add_argument("--zrzuty", type=Path, default=None, help="zapisz zrzuty 4 krokow do katalogu (bez instalacji)")
    a = p.parse_args(argv)
    paczka = a.paczka.resolve()
    if a.bez_okna:
        for strumien in (sys.stdout, sys.stderr):
            if strumien is not None and hasattr(strumien, "reconfigure"):
                strumien.reconfigure(errors="replace")
        return K.main_bez_okna(paczka, K.Wybor(a.folder_skanow, a.folder_projektow, a.katalog, a.osoba), a.python)
    if QtWidgets is None:
        _okienko_systemowe(f"Nie mozna otworzyc okna instalatora ({type(_BLAD_QT).__name__}: {_BLAD_QT}).\n\n"
                           "Rozpakuj CALA paczke jeszcze raz albo zainstaluj z wiersza polecen: zainstaluj.cmd")
        return I.KOD_PYTHON
    if a.zrzuty is not None:
        print("\n".join(str(p) for p in zrzuty(paczka, a.zrzuty)))
        return 0
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    okno = OknoInstalatora(paczka, katalog=a.katalog, python=a.python)
    okno.show()
    app.exec()
    return okno.kod if okno.kod is not None else 0


if __name__ == "__main__":
    sys.exit(main())
