"""ui - okno programu "Stanowisko" (nowe okno: paczka E3-U1a, ``etap3/nowy_interfejs/SPEC.md``).

Wejscie: ``utworz_okno(kontroler, lacznik)`` - wolane z ``aplikacja.main()`` po zaimportowaniu Qt; zwraca okno Qt (jeszcze
niepokazane). Okno niczego samo nie liczy: pokazuje ``kontroler.stan()`` i wysyla polecenia kontrolera (kontrakt:
``kontroler_api``, opis: ``opisy_modulow/aplikacja.md``).

Ten plik nie importuje Qt na poziomie modulu (proces roboczy silnika importuje pakiet ``stanowisko``); PySide6 jest
ladowane w calosci dopiero w ``utworz_okno``. Moduly pakietu:

* ``motyw``   - JEDNO miejsce wygladu: kolory, czcionki, rozmiary, arkusz Qt (NIE kolory statusow - te sa tylko w ``statusy``); bez Qt,
* ``napisy``  - napisy okna, ktorych nie ma w ``statusy`` (etykiety, podpowiedzi); bez Qt,
* ``czesci``  - czesci wspolne: przycisk (takze ze skrotem w ramce), kafelek, tabela, znacznik i kropka statusu, strefa pytan
  i komunikatow o stalej wysokosci, pasek gorny z lista osob, pasek stanu z lista bledow programu,
* ``mapa``    - mapa plytki rysowana ze stanu (kwadrat z wycieciem, kolo ze scieciem, wszystkie uklady),
* ``wieczor`` - czesci trybu "Wieczor": plytki tej zmiany, panel obok mapy (legenda), kolumna "Praca", lista "Do dofrezowania",
* ``obraz``   - obraz odchylek pracy liczony w watku pomocniczym,
* ``okno``    - okno: szkielet obu trybow, wybor technika (plytka, gniazdo), klawisze, polecenia,
* tryb "Poranek" w dotychczasowym ukladzie (nowy uklad: etap U1b): ``ekran_rano`` (strona okna), ``mapa_rano``, ``kandydaci``,
  ``okno_excela``, ``napisy_rano``, ``styl`` (rozmiary i arkusz ekranu porannego z barwami ``motyw``).
"""
from __future__ import annotations


def utworz_okno(kontroler, lacznik):
    """Okno programu na kontrolerze ``kontroler`` (``Aplikacja`` albo ``AtrapaKontrolera``) i laczniku ``lacznik_qt``."""
    from PySide6 import QtCore, QtGui, QtWidgets  # noqa: F401, PLC0415 - Qt w calosci przy starcie okna, nigdy na poziomie modulu

    from .okno import OknoStanowiska  # noqa: PLC0415

    return OknoStanowiska(kontroler, lacznik)
