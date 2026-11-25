"""napisy - teksty okna (paski, tryb wieczorny), ktorych nie ma w ``statusy`` (etykiety pol, naglowki, podpowiedzi).

Statusy prac i plytek, komunikaty, pytania i napisy przyciskow polecen sa WYLACZNIE w ``statusy`` - tutaj ich nie ma.
Wyjatek: napis stanu obejrzenia plytki ("do obejrzenia: n" / "sprawdzona"), ktory ekran wylicza z decyzji w stanie
(``czesci.stan_obejrzenia``) - to nie jest status skanu. Teksty sa po polsku ze znakami diakrytycznymi (czyta je technik);
plik UTF-8, bez Qt. Wszystkie do zatwierdzenia przez wlasciciela na pokazie G1 (lista w raporcie paczki).
E3-U1a (nowe okno): napisy, ktore technik znal ze starego okna, zostaja bez zmian wszedzie tam, gdzie zostala funkcja
(instrukcje i dokumenty dnia sprzetu je cytuja); nowe czesci okna maja nowe stale oznaczone "E3-U1a".
"""
from __future__ import annotations

TYTUL_OKNA = "Stanowisko — kontrola prac przed piecem"

# --- pasek gorny i pasek stanu --------------------------------------------------------------------
NAZWA_PROGRAMU = "Stanowisko"  # E3-U1a: nazwa programu na pasku gornym
TRYB_GRUPA = "Tryb pracy"  # E3-U1a: opis przelacznika Wieczor / Poranek dla czytnikow ekranu
WERSJA = "wersja {wersja}"  # E3-U1a: wersja programu na pasku stanu
DOBA_I_ZMIANA = "{doba} · zmiana {zmiana}"
OSOBA = "Osoba"
OSOBA_BRAK = "nie wybrano"
ZMIEN_OSOBE = "Zmień"
PULA = "Folder projektów"
SKANER = "Folder skanera"
SKANER_GOTOWY = "dostępny"
SKANER_CZEKA = "czekam na plik skanu…"
SKANER_ZAJETY = "plik skanu zajęty — czekam"
SKANER_BRAK_FOLDERU = "niedostępny"
SKANER_NIE_DZIALA = "nie jest obserwowany"
ANALIZA = "Analiza"
ANALIZA_BRAK = "nic nie czeka"
ANALIZA_TRWA = "trwa: {procent} %"
ANALIZA_CZEKA = "skany czekają"
PODPIS_POLA = "{podpis}:"
KOLEJKA = "skany w kolejce: {n}"
WSTRZYMANE_PULA = "czekają na projekty: {n}"
WSTRZYMANE_ANALIZA = "czekają na analizę: {n}"
WSTRZYMANE_ZAPIS = "czekają na zapis: {n}"
ODSTEP_KOLEJKI = " · "
# start skanu jest atrapa do dnia skanera (B2): skan uruchamia technik w programie skanera, program czeka na plik.
# E3-P14 (poz. 6): przycisk nie zaczyna sie od "Skanuj" i nie jest przyciskiem glownym - mowi, co robi Spacja (program czeka na plik)
# E3-U1a: jeden wiersz na pasku gornym (skrot w ramce); "skanujesz w programie skanera" mowi podpowiedz SKANUJ_ATRAPA_OPIS
SKANUJ_ATRAPA = "Czekam na plik skanu  [Spacja]"
SKANUJ_ATRAPA_OPIS = "Program sam nie uruchamia skanera. Uruchom skan w programie skanera — program przyjmie plik skanu sam."
NOWA_PLYTKA = "Pokaż nowy wynik:\n{plytka}"
NOWE_PLYTKI = "Pokaż nowe wyniki ({n}):\n{plytka}"
# E3-P14 (N2): trwaly panel nad lista plytek i mapa, gdy wynik nowej plytki czeka, a ekran zostal na ogladanej plytce
NOWY_WYNIK_TYTUL = "Nowy wynik czeka: {plytki}"
NOWE_WYNIKI_TYTUL = "Nowe wyniki czekają ({n}): {plytki}"
NOWY_WYNIK_SPRAWY = "{plytka} (skan z {godzina}): {sprawy}."
NOWY_WYNIK_PYTANIE = "pytanie „{tytul}”"
NOWY_WYNIK_KOMUNIKAT = "„{tytul}”"
NOWY_WYNIK_RADA = "Ekran został na oglądanej płytce. Dokończ ją albo kliknij „Pokaż nowy wynik”."
NOWY_WYNIK_POKAZ = "Pokaż nowy wynik"

# --- pasek bledow programu (A-P3) ----------------------------------------------------------------
BLEDY_PROGRAMU = "Błędy programu: {n}"
# E3-U1a: licznik bledow jest przyciskiem na pasku stanu - rozwija liste bledow nad paskiem
BLEDY_OPIS = "Pokaż albo ukryj listę błędów programu"
BLEDY_ROZWINIETE = "lista błędów jest rozwinięta"
BLEDY_ZWINIETE = "lista błędów jest zwinięta"

# --- wybor osoby -----------------------------------------------------------------------------------
KTO_PRACUJE = "Kto teraz pracuje?"
ZMIANA_OSOBY = "Zmiana osoby"
ZOSTAW_OSOBE = "Bez zmian"

# --- lista plytek ----------------------------------------------------------------------------------
PLYTKI_ZMIANY = "Płytki tej zmiany"
PLYTKI_BRAK = "Jeszcze nie ma skanów.\nUłóż prace na płytce, włóż ją do skanera i uruchom skan w programie skanera."
PLYTKA_NR = "Płytka {numer}"
PLYTKA_BEZ_NUMERU = "Płytka bez numeru"
PLYTKA_NOWA = "NOWA"
PLYTKA_PYTANIE = "czeka na odpowiedź"
PLYTKA_KOMUNIKAT = "ma komunikat"
PLYTKA_BEZ_PRAC = "brak prac"
PLYTKA_DO_OBEJRZENIA = "do obejrzenia: {n}"
PLYTKA_SPRAWDZONA = "sprawdzona"
# E3-P14 (poz. 8): do odpowiedzi na "Ponowny skan tej samej plytki?" nowy skan nie jest "sprawdzony", a poprzedni ma znacznik
PLYTKA_NOWY_SKAN = "nowy skan, czeka na odpowiedź"
PLYTKA_POPRZEDNI_SKAN = "poprzedni skan"  # krotko: kafelek w ukladzie zwartym ma 180 punktow szerokosci
PLYTKA_DOPUSZCZONA = "{jaka} — dopuszczona świadomie"
PRAC = "prac: {n}"
LICZNIK = "{napis} {n}"  # E3-U1a: licznik prac na kafelku plytki - kropka w kolorze statusu, napis statusu i liczba
WCZESNIEJSZE_POKAZ = "Pokaż wcześniejsze zmiany ({n})"
WCZESNIEJSZE_UKRYJ = "Ukryj wcześniejsze zmiany"
ZMIANA_NR = "zmiana {zmiana}"
LICZNIK_OPIS = "{napis}: {n}"

# --- mapa ------------------------------------------------------------------------------------------
MAPA_BRAK_PLYTKI = "Tu pojawi się mapa płytki po pierwszym skanie."
MAPA_GODZINA = "skan z {godzina}"
KROPKA = " · "  # E3-U1a: odstep czesci opisu skanu pod numerem plytki ("skan z 19:05 · przeanalizowana · do obejrzenia: 3")
# E3-U1a (S3-14): w czasie analizy nowego skanu mapa na ekranie jest mapa POPRZEDNIEJ plytki - oznaczona i przygaszona
MAPA_POPRZEDNIA = "POPRZEDNIA PŁYTKA — wynik nowego skanu nie jest jeszcze gotowy"
MAPA_PRZOD = "PRZÓD PŁYTKI"
MAPA_BEZ_GNIAZD = "Płytka {napis}."
LEGENDA = "Na tej płytce"
LEGENDA_PUSTE = "Puste gniazdo"  # E3-U1a: pozycja legendy z obwodka przerywana
POZA_GNIAZDEM = "Poza gniazdami: {n}"
# E3-U1a: strefa pytan i komunikatow o stalej wysokosci - jedna pozycja naraz, reszta w liczniku
JESZCZE_KROTKO = "i jeszcze {n}"
JESZCZE_OPIS = "Pokaż następne pytanie albo komunikat"
STREFA_PUSTA = "Brak pytań i komunikatów."
TYTUL_ZE_SKANEM = "{tytul} — skan z {godzina}"  # S3-3: tytul panelu plytki bez numeru wskazuje skan godzina
PLYTKA_ZE_SKANEM = "{plytka}, skan z {godzina}"  # S3-3: plytka w tytule pytania / komunikatu - numer i godzina skanu
UWAGA_PLYTKI = "{plytka}: {tytul}"
KILKA_RAZY = "{tytul}  ({n} razy)"
NUMER_PLYTKI_TEKST = "Wybierz numer wybity na płytce."
ZMIEN_NUMER = "Zmień numer"
ZMIEN_NUMER_TYTUL = "zmień numer płytki"
KONFLIKT_MIEJSCA = "Gniazda: {miejsca}."
KONFLIKT_MIEJSCE = "{plytka}, gniazdo {gniazdo}"
KONFLIKT_GODZINA = " ({godzina})"
KONFLIKT_I = " i "
KONFLIKT_ODSTEP = "; "
KONFLIKT_DALEJ = "; …"

# --- widok pracy -----------------------------------------------------------------------------------
PRACA_PUSTY_WIDOK = "Kliknij gniazdo na mapie, żeby obejrzeć pracę.\n\nCzerwone i żółte prace weź do ręki, obejrzyj i wybierz „Ukruszona” albo „OK”."
PRACA_TYTUL = "{plytka} — gniazdo {gniazdo}"
PRACA_TYTUL_POZA = "{plytka} — praca poza gniazdem"
PRACA_Z_DWOCH = "praca {nr} z {ile}"
KUWETA = "Kuweta"
ZAB = "Ząb"
KRAZEK = "Krążek"
# E3-A5i: wynik puli per praca nie rozstrzygnal krazka (ten sam STL z ta sama wartoscia na kilku krazkach) - wybiera technik
KRAZEK_DO_WYBORU = "Krazek do wyboru:"
KRAZEK_WYBRANY = "{krazek} (wybrany)"
KRAZEK_PODPOWIEDZ = "wspolczynnik {wspolczynnik} - kliknij, jesli praca pochodzi z tego krazka"
KRAZEK_COFNIJ = "Cofnij wybor krazka"
BRAK_DANYCH = "—"
NAJWIEKSZY_UBYTEK = "Największy ubytek: {mm} mm"
LICZBA_UBYTKOW = "Liczba ubytków: {n}"
BEZ_UBYTKOW = "Program nie wskazał ubytku."  # E3-U1a (S3-4): tylko gdy kontrola pracy byla i dala wynik "ok"
NIE_SPRAWDZIL = "Tej pracy program nie sprawdził."  # E3-U1a (S3-4): "nie sprawdzono", "błąd kontroli", "bez projektu"
BRAK_DECYZJI = "Brak decyzji dla tej pracy"  # E3-U1a: nad przyciskami decyzji, gdy praca nie ma decyzji
OBRAZ_WCZYTYWANIE = "Wczytuję obraz pracy…"
OBRAZ_BRAK = "Brak obrazu tej pracy."
OBRAZ_OPIS = "Widok z góry: czerwone = brakuje materiału, niebieskie = nadmiar, kółko = ubytek."
DECYZJA_ZAPISANA = "Decyzja: {decyzja} — {osoba}, {godzina}"
DECYZJA_NIEWYKRYTA = "{decyzja} (program tego nie wykrył)"
DECYZJE_NIEDOSTEPNE = "Decyzji nie można teraz zapisać — płytka {napis}."
SKROT = "{napis}  [{klawisz}]"
ZAMKNIJ_PRACE = "Zamknij  [Esc]"
NASTEPNA = "Następna  [N]"
NASTEPNA_OPIS = "Następna praca do obejrzenia na tej płytce"

# --- informacje ekranu (panel z przyciskiem "Zamknij"; nie sa komunikatami kontrolera) -------------
INFORMACJA = "Informacja"
PRACA_ZNIKNELA = "Pokazanej pracy nie ma już w stanie programu (nowa doba robocza albo skan nie jest już liczony) — widok pracy zamknięto."
PRACA_ZMIENIONA = "Dane w tym gnieździe zmieniły się — widok pracy zamknięto, żeby decyzja nie trafiła do innej pracy. Kliknij gniazdo ponownie."
POZYCJA_Z_INNEJ_DOBY = "Ta praca jest z doby {doba} (zmiana {zmiana}) — jej płytki nie ma na mapie tej doby."

# --- lista "do dofrezowania" -----------------------------------------------------------------------
LISTA_TYTUL = "Do dofrezowania: {n}"
LISTA_TA_DOBA = "Ta doba"
LISTA_WSZYSTKIE = "Wszystkie otwarte"
LISTA_PUSTA = "Lista jest pusta."
KOLUMNY_LISTY = ("Kuweta", "Ząb", "Krążek", "Płytka", "Gniazdo", "Doba", "Zmiana")
POWTORZONY = "oznaczony {n} razy"
LISTA_PLIK = "Zapisano do pliku o {godzina}"  # E3-P14 (poz. 4): obok "Lista jest pusta." bylo "Lista zapisana ..." - dwa razy "Lista"

# --- rady do pytan (uzupelnienie tekstu pytania ze ``statusy``; patrz POTRZEBUJE w raporcie) --------
RADA_PLYTKA_PORANNA = "Przełóż prace na płytkę wieczorną i zeskanuj ponownie."
RADA_PLYTKA_WIECZORNA = "Przełóż prace na płytkę poranną i zeskanuj ponownie."
RADA_PLYTKA_NIEZNANA = "Przełóż prace na właściwą płytkę i zeskanuj ponownie."

# --- skroty klawiszowe -----------------------------------------------------------------------------
KLAWISZ_UKRUSZONA = "U"
KLAWISZ_OK = "O"
KLAWISZ_COFNIJ = "C"
