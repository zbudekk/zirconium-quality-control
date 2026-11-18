"""ui - ekran trybu "Wieczor" programu "Stanowisko" (paczka E3-A3b).

Wejscie: ``utworz_okno(kontroler, lacznik)`` - wolane z ``aplikacja.main()`` po zaimportowaniu Qt; zwraca okno Qt (jeszcze
niepokazane). Okno niczego samo nie liczy: pokazuje ``kontroler.stan()`` i wysyla polecenia kontrolera (kontrakt:
``kontroler_api``, opis: ``opisy_modulow/ui_wieczor.md``).

Ten plik nie importuje Qt na poziomie modulu (proces roboczy silnika importuje pakiet ``stanowisko``); PySide6 jest
ladowane w calosci dopiero w ``utworz_okno``. Moduly pakietu:

* ``napisy`` - napisy ekranu, ktorych nie ma w ``statusy`` (etykiety, podpowiedzi); bez Qt,
* ``styl``   - czcionki, rozmiary i kolory obramowan (NIE kolory statusow - te sa tylko w ``statusy``),
* ``mapa``   - mapa plytki rysowana ze stanu,
* ``obraz``  - obraz odchylek pracy liczony w watku pomocniczym,
* ``czesci`` - pasek stanu, panele pytan i komunikatow, lista plytek, widok pracy, lista "do dofrezowania",
* ``okno``   - okno wieczorne: sklada czesci, trzyma wybor technika (plytka, gniazdo), obsluguje klawisze.
"""
from __future__ import annotations


def utworz_okno(kontroler, lacznik):
    """Okno wieczorne na kontrolerze ``kontroler`` (``Aplikacja`` albo ``AtrapaKontrolera``) i laczniku ``lacznik_qt``."""
    from PySide6 import QtCore, QtGui, QtWidgets  # noqa: F401, PLC0415 - Qt w calosci przy starcie okna, nigdy na poziomie modulu

    from .okno import OknoWieczor  # noqa: PLC0415

    return OknoWieczor(kontroler, lacznik)
