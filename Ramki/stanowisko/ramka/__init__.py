"""Program ramki swietlnej stanowiska kontroli cyrkonii (Raspberry Pi albo atrapa sprzetu).

Ramka = serwer HTTP + JSON (biblioteka standardowa Pythona) w sieci lokalnej; laptop odpytuje
ramke (decyzja wlasciciela DW8 = a). Laptop wysyla gotowe bloki pikseli dla plytki o danym
numerze (DW9 = TAK), ramka nie zna ukladow gniazd. Opis i specyfikacja protokolu: README.md.

Zgodnosc: kod w tym pakiecie nie uzywa skladni ani modulow nowszych niz Python 3.11
(Raspberry Pi OS). Poza `sprzet_rpi.py` importuje tylko biblioteke standardowa.
"""

WERSJA = "0.1.0"
PROTOKOL = 1
