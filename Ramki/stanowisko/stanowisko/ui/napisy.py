"""napisy - teksty ekranu wieczornego, ktorych nie ma w ``statusy`` (etykiety pol, naglowki, podpowiedzi).

Statusy prac i plytek, komunikaty, pytania i napisy przyciskow polecen sa WYLACZNIE w ``statusy`` - tutaj ich nie ma.
Teksty sa po polsku ze znakami diakrytycznymi (czyta je technik); plik UTF-8, bez Qt. Wszystkie do zatwierdzenia przez
wlasciciela na pokazie G1 (lista w raporcie paczki).
"""
from __future__ import annotations

TYTUL_OKNA = "Stanowisko — kontrola prac przed piecem"

# --- pasek stanu ---------------------------------------------------------------------------------
TRYB = "Tryb"
DOBA = "Doba robocza"
DOBA_I_ZMIANA = "{doba} · zmiana {zmiana}"
OSOBA = "Osoba"
OSOBA_BRAK = "nie wybrano"
ZMIEN_OSOBE = "Zmień"
PULA = "Projekty w puli"
SKANER = "Skaner"
SKANER_GOTOWY = "gotowy"
SKANER_CZEKA = "czekam na skan…"
SKANER_ZAJETY = "plik skanu zajęty — czekam"
SKANER_BRAK_FOLDERU = "brak folderu skanera"
SKANER_NIE_DZIALA = "nie działa"
ANALIZA = "Analiza"
ANALIZA_BRAK = "nic nie czeka"
ANALIZA_TRWA = "trwa: {procent} %"
ANALIZA_CZEKA = "skany czekają"
KOLEJKA = "w kolejce: {n}"
WSTRZYMANE_PULA = "czekają na projekty w puli: {n}"
WSTRZYMANE_ANALIZA = "czekają na uruchomienie analizy: {n}"
WSTRZYMANE_ZAPIS = "czekają na zapis: {n}"

# --- wybor osoby -----------------------------------------------------------------------------------
KTO_PRACUJE = "Kto teraz pracuje?"
ZMIANA_OSOBY = "Zmiana osoby"
ZOSTAW_OSOBE = "Bez zmian"

# --- lista plytek ----------------------------------------------------------------------------------
PLYTKI_ZMIANY = "Płytki tej zmiany"
PLYTKI_BRAK = "Jeszcze nie ma skanów.\nUłóż prace na płytce, włóż ją do skanera i naciśnij Spację."
PLYTKA_NR = "Płytka {numer}"
PLYTKA_BEZ_NUMERU = "Płytka ?"
PLYTKA_NOWA = "NOWA"
PLYTKA_PYTANIE = "czeka na odpowiedź"
PLYTKA_BEZ_PRAC = "brak prac"
PRAC = "prac: {n}"
WCZESNIEJSZE_POKAZ = "Pokaż wcześniejsze zmiany ({n})"
WCZESNIEJSZE_UKRYJ = "Ukryj wcześniejsze zmiany"
ZMIANA_NR = "zmiana {zmiana}"

# --- mapa ------------------------------------------------------------------------------------------
MAPA_BRAK_PLYTKI = "Tu pojawi się mapa płytki po pierwszym skanie."
MAPA_NAGLOWEK = "{plytka} — {napis}"
MAPA_GODZINA = "skan z {godzina}"
MAPA_PRZOD = "PRZÓD PŁYTKI"
MAPA_BEZ_GNIAZD = "Płytka {napis}."
LEGENDA = "Na tej płytce:"
ODSTEP = "   ·   "
POZA_GNIAZDEM = "Poza gniazdami: {n}"
JESZCZE = "… i jeszcze {n} (zamknij powyższe, żeby zobaczyć)"
UWAGA_PLYTKI = "{plytka}: {tytul}"
KILKA_RAZY = "{tytul}  ({n} razy)"
NUMER_PLYTKI_TEKST = "Wybierz numer wybity na płytce."

# --- widok pracy -----------------------------------------------------------------------------------
PRACA_PUSTY_WIDOK = "Kliknij gniazdo na mapie, żeby obejrzeć pracę.\n\nCzerwone i żółte prace weź do ręki, obejrzyj i wybierz „Ukruszona” albo „OK”."
PRACA_TYTUL = "Gniazdo {gniazdo}"
PRACA_TYTUL_POZA = "Praca poza gniazdem"
PRACA_Z_DWOCH = "praca {nr} z {ile}"
KUWETA = "Kuweta"
ZAB = "Ząb"
KRAZEK = "Krążek"
BRAK_DANYCH = "—"
NAJWIEKSZY_UBYTEK = "Największy ubytek: {mm} mm"
LICZBA_UBYTKOW = "Liczba ubytków: {n}"
BEZ_UBYTKOW = "Program nie wskazał ubytku."
OBRAZ_WCZYTYWANIE = "Wczytuję obraz pracy…"
OBRAZ_BRAK = "Brak obrazu tej pracy."
OBRAZ_OPIS = "Widok z góry: czerwone = brakuje materiału, niebieskie = nadmiar, kółko = ubytek."
DECYZJA_ZAPISANA = "Decyzja: {decyzja} — {osoba}, {godzina}"
DECYZJA_NIEWYKRYTA = "{decyzja} (program jej nie wskazał)"
DECYZJE_NIEDOSTEPNE = "Decyzji nie można teraz zapisać — płytka {napis}."
SKROT = "{napis}  [{klawisz}]"
ZAMKNIJ_PRACE = "Zamknij  [Esc]"
NASTEPNA = "Następna  [N]"
NASTEPNA_OPIS = "Następna praca do obejrzenia na tej płytce"

# --- lista "do dofrezowania" -----------------------------------------------------------------------
LISTA_TYTUL = "Do dofrezowania: {n}"
LISTA_TA_DOBA = "Ta doba"
LISTA_WSZYSTKIE = "Wszystkie otwarte"
LISTA_PUSTA = "Lista jest pusta."
KOLUMNY_LISTY = ("Kuweta", "Ząb", "Krążek", "Płytka", "Gniazdo", "Doba", "Zmiana")
POWTORZONY = "oznaczony {n} razy"
LISTA_PLIK = "plik listy zapisany o {godzina}"

# --- rady do pytan (uzupelnienie tekstu pytania ze ``statusy``; patrz POTRZEBUJE w raporcie) --------
RADA_PLYTKA_PORANNA = "To płytka poranna — przełóż prace na płytkę wieczorną i zeskanuj ponownie."
RADA_PLYTKA_WIECZORNA = "To płytka wieczorna — przełóż prace na płytkę poranną i zeskanuj ponownie."
RADA_PLYTKA_NIEZNANA = "Przełóż prace na właściwą płytkę i zeskanuj ponownie."

# --- skroty klawiszowe -----------------------------------------------------------------------------
KLAWISZ_UKRUSZONA = "U"
KLAWISZ_OK = "O"
KLAWISZ_COFNIJ = "C"
