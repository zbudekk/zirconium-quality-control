"""napisy_rano - teksty ekranu porannego (E3-A7), ktorych nie ma w ``statusy`` (naglowki, podpisy pol, podpowiedzi).

Statusy prac, komunikaty, pytania i napisy przyciskow polecen sa WYLACZNIE w ``statusy`` (wiersze poranne ``rano_*``,
``nieznana_rano``, ``dofrezowany``; ``PRZYCISKI``; ``NAZWY_KOLEJNOSCI``; ``STANY_PUNKTU``). Teksty po polsku ze znakami
diakrytycznymi (czyta je osoba rozkladajaca piec); plik UTF-8, bez Qt. Do zatwierdzenia przez wlasciciela na bramce G2.
"""
from __future__ import annotations

# --- przelacznik trybu (pasek stanu) ----------------------------------------------------------------
PRZELACZ_NA = "→ {tryb}"
PRZELACZ_OPIS = "Przełącz program na tryb „{tryb}” — nowe skany trafią do tego trybu."

# --- naglowek pieca --------------------------------------------------------------------------------
PIEC_OTWARTY = "Piec {nr} · doba {doba} · otwarty od {godzina}"
PIEC_ZAMKNIETY = "Piec {nr} · doba {doba} · zamknięty o {godzina} ({osoba})"
PIEC_BRAK = "Jeszcze nie ma pieca — zeskanuj pierwszą płytkę poranną (piec otworzy się sam)."
PIEC_Z_WCZORAJ = "Ten piec jest otwarty od poprzedniej doby — zamknij go, jeśli już rozłożony."
PIEC_ZAMKNIETY_INFO = "Piec zamknięty — następny skan płytki porannej otworzy nowy piec."
BLOKADY_TYTUL = "„Zamknij piec” teraz niemożliwe:"
ZAMKNIJ_PIEC_SKROT = "Zamknij piec"
LICZNIK = "{napis}: {n}"

# --- plytki ---------------------------------------------------------------------------------------
PLYTKA_NR = "Płytka {numer}"
PLYTKA_BEZ_NUMERU = "Płytka bez numeru"
SKAN_Z = "skan z {godzina}"
PLYTKI_NIEAKTYWNE = "Skany, które się nie liczą: {lista}"
PLYTKA_NIEAKTYWNA = "{plytka} ({godzina}) — {napis}"
POZA_GNIAZDAMI = "Poza gniazdami: {n}"
MAPA_BEZ_GNIAZD = "Płytka {napis}."
ZMIEN_NUMER = "Zmień numer"
LEGENDA = "Na płytkach:"
ZAB_KROTKO = "z. {zab}"

# --- prawa kolumna: przelacznik stron ---------------------------------------------------------------
STRONA_ROZKLADANIE = "Rozkładanie kuwet"
STRONA_WYNIK = "Kompletne i braki"

# --- rozkladanie kuwet -----------------------------------------------------------------------------
KUWETY_TYTUL = "Kuwety do rozłożenia: {n}"
KUWETA_BIEZACA = "Kuweta {kuweta}"
KUWETA_BIEZACA_OPIS = "{prac} · {plytki}"
KUWETA_PRAC = "prac: {n}"
KUWETA_PLYTKI = "płytki: {lista}"
KUWETA_BRAK = "Wszystkie kuwety rozłożone — możesz zamknąć piec."
KUWETA_BRAK_PIECA = "Kuwety pojawią się po skanach płytek pieca."
BUFOR = "Wpisany numer kuwety: {bufor}▁  (Enter = wybierz, Backspace = popraw, Esc = wyczyść)"
KUWETY_PODPOWIEDZ = "Cyfry i Enter = wybór kuwety po numerze. Gniazda bieżącej kuwety są obwiedzione na płytkach."
POTWIERDZ_SKROT = "Rozłożona  [Enter]"
COFNIJ_SKROT = "Cofnij  [Backspace]"
KOLUMNY_KUWET = ("Kuweta", "Prac", "Płytki", "Stan")
KUWETA_STAN_ROZLOZONA = "rozłożona"
KUWETA_STAN_BIEZACA = "teraz"
KUWETA_STAN_BRAKI = "braki"
KUWETA_STAN_CZEKA = ""

# --- widok pracy porannej ---------------------------------------------------------------------------
PRACA_PUSTY_WIDOK = ("Kliknij gniazdo na płytce, żeby zobaczyć pracę.\n\nŻółte — wybierz właściwy projekt, białe — praca nieznana "
                     "(przymierz na modelach albo przypisz ręcznie), czerwone — konflikt.")
PRACA_TYTUL = "{plytka} — gniazdo {gniazdo}"
PRACA_TYTUL_POZA = "{plytka} — praca poza gniazdem"
KUWETA = "Kuweta"
ZAB = "Ząb"
TYP = "Typ"
BRAK_DANYCH = "—"
DECYZJA_ZAPISANA = "Decyzja: {decyzja} — {osoba}, {godzina}"
DECYZJE = {"wybor_kandydata": "wybór kandydata", "przypisanie_reczne": "przypisanie ręczne"}
BEZ_PROJEKTU_ZAPISANE = "bez projektu"
PRZYPISANIE_AUTO = "Przypisanie: program (dopasowanie pewne)."
KONFLIKT_Z = "Ten sam projekt jest też w: {miejsca}."
KONFLIKT_MIEJSCE = "{plytka}, gniazdo {gniazdo}"
POPRAWKA_INFO = "Ząb dofrezowany do zlecenia, które było już odhaczone — tylko wpis w logu, Excel bez zmian."
DOMYKA_DOFREZOWANIE = "Ten ząb był na liście „do dofrezowania” — po „Zamknij piec” zniknie z listy."
KUWETA_DO_SPRAWDZENIA = "Kuweta tego zlecenia jest niejednoznaczna — sprawdź numer na folderze zlecenia."
KANDYDACI_TYTUL = "Który to projekt?"
KANDYDAT_NR = "Kandydat {nr}"
KANDYDAT_POKRYCIE = "pasuje w {procent} %"
KANDYDAT_WYBRANY = "wybrany"
KANDYDAT_KILKA_ZLECEN = "ten plik jest w {n} zleceniach — przypisz ręcznie"
KANDYDAT_POZA_INDEKSEM = "projektu nie ma w puli — przypisz ręcznie"
MINIATURA_BRAK = "brak\nminiatury"
DECYZJE_NIEDOSTEPNE = "Decyzji nie można teraz zapisać — {powod}."
POWOD_PIEC_ZAMKNIETY = "piec jest zamknięty"
POWOD_SKAN = "płytka {napis}"
PRZYPISZ_TYTUL = "Przypisz ręcznie: wpisz numer kuwety"
PRZYPISZ_POKAZ = "Pokaż projekty"
PRZYPISZ_BRAK = "Nie ma projektów kuwety {kuweta} w puli porannej."
PRZYPISZ_PROJEKT = "Ząb {zab} · {typ} · {stan}"
ZAMKNIJ_SKROT = "Zamknij  [Esc]"

# --- kompletne i braki -----------------------------------------------------------------------------
WYNIK_TYTUL_OTWARTY = "Piec {nr} — stan prowizoryczny (do „Zamknij piec”)"
WYNIK_TYTUL_ZAMKNIETY = "Piec {nr} — zamknięty o {godzina} ({osoba})"
WYNIK_BRAK = "Jeszcze nie ma pieca."
KOMPLETNE_TYTUL = "Zlecenia kompletne — do odhaczenia w Excelu: {n}"
BRAKI_TYTUL = "Braki w tym piecu: {n}"
BRAKI_BIEZACE_TYTUL = "Lista braków (wszystkie piece): {n}"
POPRAWKI_TYTUL = "Ząb dofrezowany do zlecenia odhaczonego (tylko log): {lista}"
NIEROZSTRZYGNIETE = "Nierozstrzygnięte (nie liczą się): wybierz {dwuznaczne}, nieznane {nieznane}"
KOLUMNY_KOMPLETNE = ("Kuweta", "Punkty", "Uwagi")
KOLUMNY_BRAKI = ("Kuweta", "Brakuje", "Stan")
KOLUMNY_BRAKI_BIEZACE = ("Kuweta", "Brakuje", "Stan", "Piec")
UWAGA_DOFREZOWANY = "z dofrezowanym zębem"
PUNKTY = "{rozpoznane} z {punktow}"
LISTA_PUSTA = "—"
