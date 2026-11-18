"""excel_com - warstwa COM do Excela otwartego na laptopie stanowiska (pywin32) dla modulu ``excel`` (E3-A9).

STAN: napisana, w paczce E3-A9 NIEURUCHAMIANA na prawdziwym Excelu (testy: atrapa obiektow COM w ``testy/test_excel.py``).
Pierwsze uruchomienie na kopii pliku produkcyjnego = paczka D2 (komputer z Excelem i sesja interaktywna - COM nie dziala
[usunieto w kopii: opis dostepu ssh]

Zasady (plan wdrozenia "Excel produkcyjny", X1, X2): program podlacza sie do Excela JUZ OTWARTEGO (``GetActiveObject``) -
nigdy nie otwiera pliku drugi raz (``Workbooks.Open``), nie tworzy skoroszytu, nie zapisuje (``Save``, ``SaveAs``,
``SaveCopyAs``), nie zamyka; zapisuje Autozapis Excela. Jedyny zapis: ``Interior.Color`` jednej komorki
(``ArkuszCom.ustaw_wypelnienie``) - JEDNA proba: odrzucone wywolanie = ``BladCom``; ponowienie robi ``excel.Excel.zatwierdz``
jako caly krok ze swiezym odczytem i kontrola wiersza (runda 2 recenzji PR #27, B1 - ponowienie tutaj omijaloby kontrole).
Odczyt: ``Range.Value`` calego zakresu naraz (jedno wywolanie COM), kolor - komorka po komorce tylko dla kandydatow.
Nazwa i pelna sciezka skoroszytu oraz nazwa arkusza czytane na zywo (``Zapisz jako`` zmienia je na tym samym obiekcie - P2).
pywin32 importowany dopiero w ``polacz`` - modul importuje sie na kazdym komputerze (testy na PC bez Excela).
"""
from __future__ import annotations

from typing import Any

XL_BRAK_WYPELNIENIA = -4142  # xlColorIndexNone: komorka bez wypelnienia (Interior.Color podaje wtedy biel 16777215)


class BladCom(RuntimeError):
    """Excel niedostepny albo odmowa COM; komunikat dla czlowieka (bez nazw zlecen)."""


def rgb_na_kolor(rgb) -> int:
    """(R, G, B) -> liczba koloru COM (R + 256 G + 65536 B); (198, 239, 206) -> 13561798."""
    r, g, b = (int(c) for c in rgb)
    return r + 256 * g + 65536 * b


def kolor_na_rgb(kolor) -> tuple[int, int, int]:
    """Liczba koloru COM -> (R, G, B)."""
    k = int(kolor)
    return k & 0xFF, (k >> 8) & 0xFF, (k >> 16) & 0xFF


def _win32com_client():
    import win32com.client  # pywin32 - tylko na komputerze z Excelem (requirements laptopa stanowiska)

    return win32com.client


def polacz(skoroszyt: str = "", arkusz: str = "", aplikacja: Any = None) -> "ArkuszCom":
    """Arkusz w Excelu juz otwartym: ``skoroszyt`` - nazwa albo jej fragment (bez wielkosci liter; "" = aktywny),
    ``arkusz`` - nazwa arkusza ("" = aktywny). ``aplikacja``: obiekt Excel.Application (testy: atrapa)."""
    if aplikacja is None:
        try:
            klient = _win32com_client()
        except ImportError as e:
            raise BladCom("brak pakietu pywin32 - polaczenie z Excelem dziala tylko na laptopie z Excelem i pywin32") from e
        try:
            aplikacja = klient.GetActiveObject("Excel.Application")
        except Exception as e:
            raise BladCom("Excel nie jest uruchomiony - otworz plik zlecen w Excelu (z Autozapisem) i sprobuj ponownie") from e
    wb = _skoroszyt(aplikacja, skoroszyt)
    return ArkuszCom(aplikacja, wb, _arkusz(wb, arkusz))


def _skoroszyt(aplikacja: Any, wzor: str) -> Any:
    if not wzor:
        wb = aplikacja.ActiveWorkbook
        if wb is None:
            raise BladCom("w Excelu nie ma otwartego skoroszytu - otworz plik zlecen")
        return wb
    w = wzor.casefold()
    otwarte = list(aplikacja.Workbooks)
    pasujace = [wb for wb in otwarte if str(wb.Name).casefold() == w] or [wb for wb in otwarte if w in str(wb.Name).casefold()]
    if len(pasujace) != 1:
        ile = "zaden" if not pasujace else f"{len(pasujace)}"
        raise BladCom(f"[excel] skoroszyt: {ile} z {len(otwarte)} otwartych skoroszytow nie pasuje jednoznacznie do ustawienia - "
                      f"popraw [excel] skoroszyt albo otworz plik zlecen")
    return pasujace[0]


def _arkusz(wb: Any, nazwa: str) -> Any:
    if not nazwa:
        return wb.ActiveSheet
    try:
        return wb.Worksheets(nazwa)
    except Exception as e:
        raise BladCom("[excel] arkusz: w skoroszycie nie ma arkusza o tej nazwie - popraw ustawienie") from e


class ArkuszCom:
    """Interfejs ``excel.ZrodloArkusza`` nad arkuszem Excela (COM)."""

    def __init__(self, aplikacja: Any, skoroszyt: Any, arkusz: Any):
        self._app, self._wb, self._ws = aplikacja, skoroszyt, arkusz

    def _arkusz(self) -> Any:
        if self._ws is None:
            raise BladCom("polaczenie z Excelem zwolnione - polacz ponownie")
        return self._ws

    @property
    def nazwa(self) -> str:
        return str(self._arkusz().Name)

    @property
    def skoroszyt(self) -> str:
        return str(self._wb.Name) if self._wb is not None else ""

    @property
    def sciezka(self) -> str:
        return str(getattr(self._wb, "FullName", "")) if self._wb is not None else ""

    def zwolnij(self) -> None:
        """Zwalnia referencje do obiektow COM (Application, Workbook, Worksheet) - zamkniecie programu, blad COM (D2)."""
        self._ws = self._wb = self._app = None

    def _ostatni_wiersz(self) -> int:
        uzyty = self._arkusz().UsedRange
        return int(uzyty.Row) + int(uzyty.Rows.Count) - 1

    def _zakres(self, w1: int, k1: int, w2: int, k2: int) -> list[tuple]:
        ws = self._arkusz()
        v = ws.Range(ws.Cells(w1, k1), ws.Cells(w2, k2)).Value
        if not isinstance(v, tuple):  # jedna komorka: sama wartosc
            return [(v,)]
        return [tuple(r) for r in v]

    def odczytaj(self, pierwszy_wiersz: int, ostatnia_kolumna: int) -> list[tuple]:
        ostatni = self._ostatni_wiersz()
        if ostatni < pierwszy_wiersz:
            return []
        return self._zakres(pierwszy_wiersz, 1, ostatni, ostatnia_kolumna)

    def wiersz(self, nr: int, ostatnia_kolumna: int) -> tuple:
        return self._zakres(nr, 1, nr, ostatnia_kolumna)[0]

    def wypelnienie(self, nr: int, kolumna: int) -> tuple[int, int, int] | None:
        wnetrze = self._arkusz().Cells(nr, kolumna).Interior
        if int(wnetrze.ColorIndex) == XL_BRAK_WYPELNIENIA:
            return None
        return kolor_na_rgb(wnetrze.Color)

    def ustaw_wypelnienie(self, nr: int, kolumna: int, rgb) -> None:
        """Jedna proba zapisu koloru; odrzucenie (Excel zajety: edycja komorki, zmiany wspoledytora) = ``BladCom``."""
        try:
            self._arkusz().Cells(nr, kolumna).Interior.Color = rgb_na_kolor(rgb)
        except BladCom:
            raise
        except Exception as e:
            raise BladCom(f"Excel odrzucil zapis koloru (zajety - np. edycja komorki albo zmiany wspoledytora): {type(e).__name__}") from e
