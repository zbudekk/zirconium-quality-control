# Raport recenzenta PR #16 - runda 1

Data: 2026-11-17. Recenzent: swieza subsesja (Fable 5.2), niezalezna od wykonawcow i koordynatora; werdyktu
koordynatora nie znalem.
Stan recenzowany: HEAD `3fdf76f` galezi `e3/a1`, PR #16 "E3-A1: baza i sesja wieczorna" (`e3/a1` -> `przed-skanerem`),
zakres `git diff origin/przed-skanerem...origin/e3/a1` (22 pliki, +7 935 / -5, wszystko pod `Ramki/stanowisko/`).
Zrodlo wymagan: `Ramki/plan_etap3_pelna_aplikacja_2026-11-16.md` sekcje 3.3, 3.4, 3.7, 3.8, 4.1, 6, 9, 11.1; decyzje G0
wlasciciela z 17.11 (DW1-DW12 wg zalecen, DW2, DW3).
Metoda: przeczytane w calosci `baza.py`, `session.py`, `import_decyzji.py`, diff `ustawienia.py` /
`ustawienia.przyklad.toml` / `test_ustawienia.py`, `test_baza.py`, `test_session_wieczor.py`, oba opisy modulow, raport
wykonawcy; z danych testowych naglowki plikow i `indeks.json` (pliki `wynik_*.json` wyrywkowo); w `porownaj.py` i
`match.py` tylko budowa slownika wyniku. Uruchomienia na PC (`<PC-katalog>\e3\r16`, kod z `git archive HEAD`, wolny RAM
16 GB i 15 GB przed startem): (1) wlasny skrypt `proby.py` - 12 prob na `baza` i `session`, tylko biblioteka standardowa,
ok. 20 s; (2) jeden przebieg `pytest` trzech plikow paczki bez testu z prawdziwym `porownaj`. Pelnego pytest nie
powtarzalem (log wykonawcy `e3\a1\pytest_d60e388.log`: 463 passed, 3 skipped). Na MSI nie uruchamiano pytest ani
obliczen. Uwaga do limitu "1 proces python": proby 1 i 2 z natury wymagaly procesu potomnego (zabicie w polowie
transakcji, drugi proces trzymajacy blokade, 2 procesy otwierajace nowa baze) - w tych chwilach byly 2-3 procesy
python, kazdy przez ulamek sekundy do 9 s, bez obliczen (czekanie na blokade).

## 0. Werdykt

**do scalenia po poprawkach** - B 0 / P 7 / D 14.

Fundament jest porzadny: 11 tabel i wszystkie kolumny, unikaty i indeksy zgadzaja sie z sekcja 3.4 co do nazwy
i kolejnosci; transakcje sa jawne i calosciowe (zabicie procesu w polowie przyjecia skanu zostawia baze spojna - proba 1);
klucze obce wlaczone na kazdym polaczeniu modulu; migracja jest jedna transakcja z kopia pliku; baza nowsza niz program
jest odrzucana bez dotkniecia pliku; testy kryteriow sprawdzaja prawdziwa logike (bez atrap zastepujacych kod).
Nie znalazlem sciezki, ktora przy wyniku z prawdziwego `porownaj` pokazalaby jako zielona prace ze skanu
`niezgodny_uklad`, `do_powtorzenia`, `zastapiony` albo `blad`.
Poprawki przed scaleniem dotycza trzech rzeczy: (a) ograniczen `NOT NULL` dolozonych ponad sekcje 3.4 bez zgloszenia
(P1), (b) dwoch drog, ktorymi nazwa folderu zlecenia moze trafic poza dwie dozwolone tabele (P2, P3), (c) czterech
miejsc, w ktorych stan albo lista moga sie rozjechac z decyzjami technika (P4-P7). Zadna nie wymaga przebudowy;
P1 jest tania tylko teraz (po scaleniu to migracja z przebudowa tabeli).

## 1. Uwagi (B = blokujaca, P = poprawic przed scaleniem, D = drobna / moze zostac jako znana)

Sciezki wzgledem `Ramki/stanowisko/`. "Proba N" = `proby.py` uruchomiony na PC.

| Nr | Waga | Plik:linia | Scenariusz (wejscie -> zly wynik) | Sprawdzone | Oczekiwane |
|---|---|---|---|---|---|
| P1 | P | `stanowisko/baza.py:47-48, 53, 58-60, 66, 85-86, 88, 115, 122, 124, 145, 148, 151, 171-173` | Schemat ma 19 ograniczen `NOT NULL` i 2 wartosci domyslne, ktorych sekcja 3.4 nie podaje, a raport wykonawcy i `baza.md` pisza "kolumny dokladnie wg 3.4" / "schemat bez zmian" (plan 11.1: nie wolno zmieniac schematu wzgledem 3.4 bez pytania). Jedno z nich koliduje z wymaganiem K7: wpis reczny wspolczynnika "raz na krazek" nie ma pliku STL -> `INSERT` do `frezowania` bez `plik_w_raporcie` konczy sie `IntegrityError: NOT NULL constraint failed: frezowania.plik_w_raporcie` (tak samo bez `data`). SQLite nie zdejmie `NOT NULL` bez przebudowy tabeli, wiec po scaleniu to migracja do wersji 2 z opisem dla wlasciciela. | Uruchomieniem (proba 10) i czytaniem. | Albo zdjac `NOT NULL` z `frezowania.plik_w_raporcie` i `frezowania.data` teraz, albo jawna decyzja wlasciciela, jak A4 zapisze wpis reczny (np. pusty tekst). Pozostale ograniczenia wypisac w raporcie i `baza.md` jako dodatek do 3.4 (lista w sekcji 2). |
| P2 | P | `stanowisko/session.py:259-264` (`_zapisz_wynik`), zrodlo pola: `stanowisko/porownaj.py:246, 268`; test: `testy/test_session_wieczor.py:438-471, 618` | Wynik `porownaj` ma pole `foldery_projektow` = pelne sciezki folderow, z ktorych zbudowano pule. `przyjmij_wynik` zapisuje wynik w calosci do `[sciezki] wyniki`. Gdy silnik (A2 / A5) poda foldery zlecen, nazwy folderow z nazwiskami laduja w kazdym pliku `skanNNNNNN_*_wynik.json` - wbrew zasadzie 1 sekcji 3.4 ("pliki wynikow uzywaja `sha16`") i DW2. Test kryterium 8 tego nie widzi, bo w danych testowych pole ma neutralna sciezke; test na prawdziwym `porownaj` wrecz wymaga, zeby plik byl rowny wynikowi (linia 618). To samo dotyczy tekstow `gniazda[].uwagi`. | Uruchomieniem (proba 5: wynik z dwoma folderami zlecen -> obie nazwy w pliku wyniku). | `_zapisz_wynik` usuwa albo zastepuje `foldery_projektow` (np. liczba folderow) przed zapisem; test k8 z folderem zlecenia w tym polu. Alternatywa: kontrakt 3.8 mowi wprost, ze silnik tego pola nie wypelnia - ale wtedy i tak potrzebny test. |
| P3 | P | `stanowisko/session.py:204-215` (`przyjmij_blad`) | `opis` awarii analizy idzie bez zmian do `zdarzenia.dane`. Typowy opis to tekst wyjatku, np. brak pliku projektu z pelna sciezka folderu zlecenia -> nazwa folderu w dzienniku, ktory ma byc "JSON bez nazwisk"; tabela jest tylko do dopisywania (wyzwalacze), wiec wpisu nie da sie potem usunac zwyklym poleceniem. | Uruchomieniem (proba 5: opis ze sciezka zlecenia -> nazwa folderu w `zdarzenia.dane`). | Do dziennika typ bledu i krotki kod, a pelny tekst najwyzej do pliku w `dane/` poza baza; albo maskowanie sciezek. Co najmniej ostrzezenie w docstringu i kontrakcie dla A2 / A3 + test. |
| P4 | P | `stanowisko/session.py:352-358` (`_praca_do_decyzji`), `404-430` (`_odswiez_punkt`, zapytanie `inne` 421-423); `narzedzia/import_decyzji.py:94, 107` | `stan_punktow` moze dostac `do_dofrezowania`, ktorego nie ma na liscie wieczoru, dwiema drogami. (a) Decyzje z okna testowego: import zaklada skany ze statusem `przyjety` i przypisuje `projekt_id` z indeksu; wieczorem technik klika "Ukruszona" i "cofnij" na pracy tego samego projektu -> zapytanie `inne` (bez ograniczenia do trybu i wieczoru) znajduje prace z importu i punkt ZOSTAJE w `do_dofrezowania`, wskazujac prace z okna testowego; lista wieczoru jest pusta. Opis importu mowi "nie zmieniaja list ani stanu zlecen". (b) Decyzja jest przyjmowana na pracy skanu o dowolnym statusie poza `zastapiony`: praca skanu `niezgodny_uklad` -> "Ukruszona" -> punkt `do_dofrezowania`, lista pusta (dzis prawdziwy `porownaj` zwraca przy niezgodnym ukladzie 0 gniazd, wiec (b) wymaga wyniku z innego zrodla). Wedlug zasady 4 sekcji 3.4 lista brakow rano to zapytanie po `stan_punktow`. | Uruchomieniem (proby 11 i 3). | `inne` tylko po skanach z trybem (albo bez znacznika importu); import ze statusem innym niz aktywny; `_praca_do_decyzji` dopuszcza tylko skany aktywne. |
| P5 | P | `stanowisko/session.py:183, 218-219, 439-440` (wieczor = data z czasu pliku), `477, 525` (domyslnie "dzis") | Przynaleznosc skanu do wieczoru wynika z daty modyfikacji pliku skanu, a `stan_wieczoru()` i `do_dofrezowania()` bez daty biora dzien z zegara programu. (a) Plik z inna data niz dzis (kopia z zachowana data - tak dziala `shutil.copy2`, wiec moze tak robic symulator z A2; zegar; ponowna analiza pliku z wczoraj) -> skan przyjety, ale ekran dzisiejszego wieczoru go nie pokazuje, a "Ukruszona" na nim nie trafia na dzisiejsza liste. (b) Polnoc: skan o 23:59 i ponowny skan tej samej plytki o 00:00 nie sa "tym samym wieczorem" - brak propozycji zastapienia, `zastap_skan` wprost odmawia; po polnocy `stan_wieczoru()` jest pusty. | Uruchomieniem (proba 7). | Decyzja projektowa przed A2 / A3: wieczor liczony od czasu przyjecia (`czas_analizy`) albo jawny identyfikator sesji wieczoru; co najmniej zapis w kontrakcie `ZdarzenieSkanu` i test z plikiem o starej dacie. |
| P6 | P | `stanowisko/session.py:380-401` (`_zastap`; warunki dla podanego `poprzedni_id`: 390-395), `369-378` | Zastapienie skanu jest nieodwracalne i nie sprawdza plytki. (a) `zastap_skan(skan, poprzedni_id)` przyjmuje dowolny wczesniejszy aktywny skan wieczoru: skan plytki 2 "zastapil" skan plytki 1, pozycja "Ukruszona" z plytki 1 zniknela z listy. (b) Droga zwykla: dwie rozne plytki z tym samym odczytanym numerem (blad odczytu dolkow; plytka uzyta drugi raz - przypadek opisany w `session.md`) -> program sam proponuje zastapienie -> jedno klikniecie -> decyzje pierwszej plytki przestaja sie liczyc. `cofnij` obsluguje tylko decyzje o pracy; dla `powtorz_skan` nie ma cofniecia, zostaje ponowne skanowanie plytki. | Uruchomieniem (proba 9, przypadek a); (b) czytaniem. | Odmowa, gdy oba skany maja numer plytki i numery sa rozne; cofniecie zastapienia (kolejny wiersz `cofniecie` wskazujacy decyzje `powtorz_skan`) albo decyzja wlasciciela, ze brak cofniecia jest akceptowany (pytanie 5). |
| P7 | P | `stanowisko/session.py:462-468` (`_kolor`), `491-497` (liczniki) | `kolor` pracy i `liczniki` nie uwzgledniaja decyzji technika. Praca zielona oznaczona `ukruszona_niewykryta` (albo `ukruszona`) nadal ma `kolor = "zielony"` i jest liczona w `liczniki["zielony"]`; praca czerwona po "OK" zostaje czerwona. `session.md` nazywa `kolor` "obowiazujacym na mapie", a z tego pola skorzysta ekran (A3) i ramka wieczorna ("czerwone i zielone", I6). Skutek mozliwy bez zmiany kodu A1: zielona dioda pod praca, ktora technik uznal za ukruszona. | Uruchomieniem (proba 4: liczniki przed i po decyzjach identyczne, gniazdo 1 zielone z decyzja `ukruszona`). | Rozstrzygnac teraz, bo to kontrakt dla A3 i A8: albo decyzja zmienia `kolor` (ukruszona -> czerwony, ok -> zielony albo osobny), albo opis mowi wprost "kolor = ocena programu, odbiorca laczy go z polem `decyzja`", a `liczniki` dostaja osobne zliczenie decyzji. |
| D1 | D | `stanowisko/baza.py:334` (`BEGIN IMMEDIATE`), `207` | Baza zajeta przez drugi proces: decyzja czeka 5,5 s i konczy sie surowym `sqlite3.OperationalError: database is locked` (nie `BladSesji` / `BladBazy`); transakcja nie zostaje otwarta, po zwolnieniu blokady ta sama decyzja przechodzi. Odczyt stanu w czasie cudzej transakcji dziala od razu. Wykonawca opisal to w `baza.md` jako zadanie okna (A3). | Uruchomieniem (proba 2). | A3: zlapac i pokazac komunikat z tabeli "co robic" (T7). |
| D2 | D | `stanowisko/baza.py:283-287`, `223-231` | Nieudana migracja istniejacego pliku (np. plik w wersji 0, ktory ma juz tabele `projekty`) robi kopie pliku przy KAZDYM uruchomieniu: 3 starty = 3 kopie. Kopia powstaje przez `shutil.copy2` po zamknieciu polaczenia, a nie mechanizmem kopii SQLite (ktory modul ma w `Baza.kopia`), wiec przy drugim procesie piszacym moglaby byc niespojna. | Uruchomieniem (proba 8); druga czesc czytaniem. | Nie robic kopii, gdy istnieje identyczna z poprzedniej proby; kopia przez `backup`. |
| D3 | D | `stanowisko/session.py:194-195, 263`; `baza.py:101` (klucz bez `AUTOINCREMENT`) | Zabicie procesu po zapisie pliku wyniku, przed `COMMIT`: baza spojna (skanu nie ma, `integrity_check` ok), ale plik `skan000002_*_wynik.json` zostaje, a nastepny skan dostaje ten sam numer 2 -> dwa pliki z przedrostkiem `skan000002_` rozniace sie tylko nazwa skanu. | Uruchomieniem (proba 1). | Zapis pliku po `COMMIT` (z dopisaniem sciezki w drugiej malej transakcji) albo sprzatanie plikow bez wiersza przy starcie. |
| D4 | D | `stanowisko/session.py:415-417, 432-436` (docstring 407-409) | "Ukruszona" nadpisuje punkt w kazdym stanie (`rozpoznany`, `zamkniety_recznie`, `brak_po_piecu`) i zeruje `sesja_pieca_id`; cofniecie nie przywraca poprzedniego stanu, tylko `oczekuje`. Docstring mowi "punktow w innych stanach nie rusza" - to prawda tylko dla galezi cofania. W A1 innych stanow nikt nie zapisuje; wykonawca zglosil to jako "do potwierdzenia w A6". | Uruchomieniem (proba 6). | Rozstrzygnac w A6, zanim poranek zacznie pisac do tej tabeli; poprawic docstring. |
| D5 | D | `stanowisko/session.py:249-257` (256) | Gdy wynik nie wskazuje wpisu frezowania (dzis nigdy nie wskazuje), praca dostaje NAJNOWSZY wpis projektu. Zab dofrezowany na innym krazku (K4: dwie wersje) -> na liscie "do dofrezowania" moze stac krazek nie tej wersji, ktora lezy na plytce. | Uruchomieniem (proba 12: projekt z dwoma krazkami -> wybrany nowszy) i czytaniem. | Do A5 (pula ze wspolczynnikiem per praca); do tego czasu przy wiecej niz jednym wpisie raczej puste pole niz zgadywanie. |
| D6 | D | `stanowisko/session.py:174-180` | Wynik bez klucza `uklad_zgodny` (albo z `null` - straznik ukladu wylaczony) jest przyjmowany jako `przyjety` z zielonymi pracami. Dla wyniku z biezacego `porownaj` klucz jest zawsze. | Uruchomieniem (proba 12). | Zostawic albo traktowac brak klucza jako blad kontraktu - do decyzji przy A2. |
| D7 | D | `narzedzia/import_decyzji.py:81-90` | Ochrona przed dublowaniem dziala tylko, gdy stary plik jest poczatkiem nowego. Plik z poprawionym pierwszym wierszem -> ponowny import dopisuje wszystkie 7 decyzji drugi raz (14 w bazie); tabela jest tylko do dopisywania, wiec zostaja. | Uruchomieniem (proba 11). | Ostrzezenie i odmowa, gdy w bazie jest juz import, a plik nie jest jego przedluzeniem (z przelacznikiem wymuszenia). |
| D8 | D | `stanowisko/session.py:279-301`, `331-338`, `155, 158` | Brak kontroli zgodnosci decyzji ze stanem: `ukruszona` na pracy zielonej i `ukruszona_niewykryta` na czerwonej sa przyjmowane (metryka "program nie zauwazyl" bedzie zalezec od tego, ktory przycisk okno wywola); numer plytki bez gornej granicy (przyjmie 999). Komunikaty `BladSesji` o operatorze zawieraja liste imion osob z ustawien - trafia do logow, jesli okno je zapisuje. | Czesciowo uruchomieniem (proba 4), reszta czytaniem. | Do ustalenia w A3; nazwy osob poza komunikatem wyjatku. |
| D9 | D | `stanowisko/baza.py:140` | Unikat (`skan_id`, `gniazdo`, `nr_fragmentu`) nie obejmuje prac poza gniazdem: dla `gniazdo` = NULL SQLite przyjmuje dwa identyczne wiersze. To wlasnosc schematu z planu; `session` numeruje fragmenty sam, wiec dzis bez skutku. | Uruchomieniem (proba 10). | Wiedziec; ewentualnie indeks po `COALESCE(gniazdo, -1)` przy najblizszej migracji. |
| D10 | D | `stanowisko/session.py:162-202` | To samo zdarzenie skanu przyjete dwa razy (np. restart miedzy `COMMIT` a potwierdzeniem zadania w A2 / A3): drugi skan z tymi samymi pracami, liczniki podwojone (10 prac zamiast 5), 4 "konflikty", wpis `konflikt_projektu` w dzienniku - az technik potwierdzi zastapienie. Program to pokazuje (`do_potwierdzenia`), wiec nic nie ginie. | Uruchomieniem (proba 9). | A3: ten sam `sha16` pliku z tego samego wieczoru zastepowac bez pytania albo nie przyjmowac drugi raz. |
| D11 | D | `stanowisko/baza.py:200-208` | Klucze obce i (posrednio) spojnosc pilnuje `PRAGMA foreign_keys` ustawiane tylko przez `baza._polacz`. Obce polaczenie (`sqlite3.connect` w narzedziu, przegladarka bazy) wstawia wiersz `prace` z nieistniejacym skanem. | Uruchomieniem (proba 10). | Zasada w `baza.md`: do bazy tylko przez `baza.otworz`; okresowo `PRAGMA foreign_key_check` (samokontrola A11). |
| D12 | D | `testy/test_baza.py:95-104`; `stanowisko/baza.py:30` | Test kryterium 8 w `test_baza.py` sprawdza NAZWY kolumn (czy zawieraja "folder"), nie dane; wlasciwy test danych jest w `test_session_wieczor.py:438` i ma luki opisane w P2 i P3. Stala `TABELE_Z_NAZWA_FOLDERU` nie obejmuje trzech kolumn z nazwami plikow zlecen (pytanie 2). | Czytaniem. | Po decyzji wlasciciela (pytanie 2) jedna stala "kolumny z danymi osobowymi" uzywana przez test i przyszle narzedzie kopii dla programistow. |
| D13 | D | `stanowisko/session.py:66-68` | `skrot_ustawien` liczy sie z calych ustawien, wiec zmienia sie po zmianie sciezki, hosta ramki albo listy operatorow - nie tylko progow; opis kolumny ("przy jakich progach liczono skan") obiecuje wiecej. | Czytaniem (test `test_sesja_z_ustawien` potwierdza: zmiana portu zmienia skrot). | Skrot z sekcji `[match]`, `[inspect]`, `[plytki]` albo poprawic opis. |
| D14 | D | `raporty/E3-A1_2026-11-17.md` pkt 1 i 5; PR | Niescislosci raportu: "kolumny wg 3.4 ... schemat bez zmian" (patrz P1); galaz i PR sa oparte na `przed-skanerem`, nie na `origin/main` (plan sekcja 9) - wykonawca pisze to w opisie PR. Liczby testow potwierdzone: log 463 / 3 / 0 dla `d60e388`; `3fdf76f` rozni sie od `d60e388` tylko plikiem raportu. | Odczyt logu na PC, `git diff --stat d60e388 3fdf76f`. | Poprawic zdanie o schemacie; baza PR do zmiany po scaleniu #13. |

## 2. Schemat 3.4 vs kod (`baza.py:44-178`)

Tabele (11), nazwy i kolejnosc kolumn, klucze glowne, klucze obce, 4 unikaty i 2 indeksy: **zgodne z sekcja 3.4, 0 roznic
w nazwach** (porownane kolumna po kolumnie; pilnuje tego tez `test_nowa_baza_ma_schemat_z_sekcji_3_4`).
`zdarzenia.skan_id` bez klucza obcego - tak jak w planie ("`skan_id` albo NULL", bez FK). Roznice = rzeczy, ktorych plan
nie podaje, a kod dodaje:

| Tabela | Sekcja 3.4 | Kod | Ocena |
|---|---|---|---|
| `zlecenia` | bez informacji o wymagalnosci | `zrodlo`, `folder` NOT NULL; `usuniety` NOT NULL DEFAULT 0 | rozsadne; zglosic |
| `projekty` | jw. | `zlecenie_id`, `plik`, `sha16` NOT NULL; `usuniety` NOT NULL DEFAULT 0 | rozsadne; zglosic |
| `cechy_stl` | - | bez dodatkow | zgodne |
| `frezowania` | wiersz raportu, CSV albo "wpis reczny" | `plik_w_raporcie`, `krazek`, `data` NOT NULL | **P1**: koliduje z wpisem recznym na krazek (K7) |
| `skany` | - | `status` NOT NULL | rozsadne; zglosic |
| `prace` | `gniazdo` moze byc puste (praca poza gniazdem - wynika z formatu wyniku) | `skan_id`, `nr_fragmentu` NOT NULL; unikat nie dziala dla `gniazdo` NULL | D9 |
| `decyzje` | "tylko dopisywanie" | `rodzaj`, `czas` NOT NULL; wyzwalacze blokujace UPDATE i DELETE | zgodne z intencja; skutek: wpisu nie da sie usunac ani poprawic (P3, D7), a migracja zmieniajaca te tabele musi najpierw zdjac wyzwalacze |
| `sesje_pieca` | - | bez dodatkow (w kodzie przed `skany`, bo `skany` ma do niej klucz obcy) | zgodne |
| `stan_punktow` | `projekt_id` PK i FK | `stan` NOT NULL | rozsadne; zglosic |
| `excel_zapisy` | - | bez dodatkow | zgodne |
| `zdarzenia` | "tylko dopisywanie" | `czas`, `zrodlo`, `typ` NOT NULL; wyzwalacze jw. | jw.; dziennika nie da sie skracac (retencja) bez migracji |
| caly plik | typow kolumn plan nie podaje | czasy TEXT ISO lokalne do sekundy, flagi INTEGER 0 / 1, `kuweta` i `zeby` TEXT, `miniatura` BLOB; `id` bez AUTOINCREMENT; tryb dziennika domyslny (`delete`), `synchronous` pelne | opisane w `baza.md`; AUTOINCREMENT - patrz D3 |
| rodzaje decyzji | lista 8 rodzajow | dodatkowy rodzaj `cofniecie` (schemat tego nie ogranicza - kolumna jest tekstem) | pytanie 1 |

## 3. Pytania do wlasciciela

1. **Cofniecie decyzji** jako wiersz `rodzaj = cofniecie`, `wartosc` = id cofanej decyzji (nie ma go na liscie w 3.4):
   TAK / inaczej? Moim zdaniem TAK - jest zgodne z "tylko dopisywanie", dziala poprawnie w probach (kolejnosc
   ukruszona -> ok -> cofnij -> cofnij), nie zmienia schematu.
2. **Nazwy plikow zlecen** (`projekty.plik`, `frezowania.plik_w_raporcie`, `frezowania.raport_plik`): nazwy plikow STL
   zawieraja nazwisko, a DW2 mowi o dwoch tabelach. Zostaja (wtedy DW2 trzeba rozszerzyc o te 3 kolumny, a kopia dla
   programistow musi je wycinac) czy maja zniknac / byc zastapione? `plik_w_raporcie` jest czescia unikatu, wiec
   decyzja przed A4 - pozniej to przebudowa tabeli.
3. **Wpis reczny wspolczynnika na krazek (K7)**: jak ma wygladac w `frezowania` - wiersz bez pliku (wtedy zdjac
   `NOT NULL`, P1) czy inaczej?
4. **Co jest "wieczorem"** (P5): data pliku skanu (jak teraz), data przyjecia skanu przez program, czy jawnie otwierana
   sesja wieczoru? Od tego zalezy, co technik zobaczy po polnocy i przy pliku z inna data.
5. **Pomylkowe potwierdzenie "to ponowny skan"** (P6): czy brak cofniecia jest akceptowany (ratunek = zeskanowac
   plytke jeszcze raz), czy zastapienie ma dac sie cofnac?
6. **Kolor a decyzja** (P7): czy praca oznaczona "Ukruszona" ma na mapie i ramce zmieniac kolor (i nie liczyc sie
   jako zielona), a "OK" na czerwonej - gasic czerwien?
7. **Pusta lista operatorow** (pytanie wykonawcy): dzis decyzje dzialaja z pusta kolumna `operator`. Zalecam: baza
   przyjmuje, ale okno (A3) przy pustej liscie pokazuje stale ostrzezenie - inaczej "kto zatwierdzil" (SE12, DW3)
   przepada po cichu na starym pliku ustawien.
8. **"0 prac zielonych" w skanie do powtorzenia** (pytanie wykonawcy): w bazie `prace.status_gniazda` zostaje
   `zielony`, a zolty jest tylko w `stan_wieczoru`. Akceptowalne, jesli kazdy odbiorca (metryki A10, poranek) czyta
   kolor przez `session`, nie wprost z tabeli - potwierdzic.
9. `przechowuj_skany_dni = 0` (nie usuwac) - zgodne z DW4 na tryb cienia i bezpieczne (kodu usuwajacego jeszcze nie
   ma); bez pytania, tylko do wiadomosci. `przyjmij_blad`, `podaj_numer_plytki`, `ukruszona_niewykryta` - bezpieczne
   jako fundament po uwagach P3 i D8.

## 4. Co sprawdzilem i nie budzi zastrzezen

- **Transakcje i awarie.** Przyjecie skanu, decyzja, cofniecie, zastapienie, import: kazde w jednej transakcji
  `BEGIN IMMEDIATE`; wyjatek w srodku = `ROLLBACK` (takze blad zapisu pliku wyniku - proba 12: 0 skanow, brak otwartej
  transakcji). Zabicie procesu w polowie przyjecia skanu: po restarcie 1 skan i 5 prac sprzed awarii,
  `integrity_check` ok, `foreign_key_check` pusty; odczyt w trybie tylko do odczytu przy pozostawionym pliku
  dziennika dziala (proba 1).
- **Dwa procesy.** Odczyt w czasie cudzej transakcji bez czekania; zapis czeka 5 s i konczy sie wyjatkiem bez
  uszkodzenia stanu (D1). Dwa procesy otwierajace naraz nowy plik: oba koncza z wersja 1, jeden plik (proba 2).
- **Migracje.** DDL i `user_version` w jednej transakcji; nieudana migracja zostawia stara wersje (test + proba 8);
  kopia sprzed migracji bajt w bajt (test). Baza nowsza: `BladBazy`, plik bajtowo bez zmian, bez plikow obok (test).
  Plik niebedacy baza: `BladBazy`, plik bez zmian.
- **Zielone mimo zlego skanu.** `niezgodny_uklad`, `blad`, `zastapiony`: `kolor` = brak, prace poza licznikami
  i listami; `do_powtorzenia`: zielone -> zolte; decyzje skanu zastapionego nie licza sie do listy ani do
  `stan_punktow`, nowych decyzji na nim nie mozna podjac. Nazwy statusow w `session.py` (`skan_ponownie`,
  `popraw_ulozenie`, `podwojny`, `poza_gniazdem`, `gniazda_podwojne`) zgadzaja sie z `porownaj.py`. Konflikt tego
  samego `sha16` jest zglaszany, ale NIE zmienia koloru prac (kryterium 6 wymaga tylko zgloszenia) - do wiedzy A3.
- **Cofanie.** Ukruszona -> OK -> cofnij -> cofnij daje kolejno: ok, ukruszona, brak; cofniecie bez decyzji = odmowa.
- **Odtworzenie po restarcie.** Caly stan w bazie; w pamieci tylko wybrany operator (po restarcie trzeba go wybrac
  ponownie - przy niepustej liscie decyzja bez wyboru jest odrzucana).
- **Testy kryteriow 1-10.** Sprawdzaja dane w bazie i wynik funkcji, nie wlasne zalozenia; jedyne `monkeypatch` to
  dopisanie przyszlych wersji do `MIGRACJE` (uprawnione). Kryterium 4 jest spelnione na poziomie `stan_wieczoru`
  (pytanie 8). Luki: P2, P3 (kryterium 8), D12.
- **`test_ustawienia.py`.** Jedna asercja starego testu zmieniona z rownosci zbioru sekcji na "wymagane <= sekcje <=
  wymagane + opcjonalne" (linia 107) - konieczne, bo lokalny plik moze nie miec `[sesja]`; sekcje wymagane nadal
  musza byc wszystkie. Nie uwazam tego za oslabienie. Zamrozona lista kluczy wymaganych (`WYMAGANE_PRZED_ETAPEM_3`)
  pilnuje, ze nie doszedl zaden klucz wymagany.
- **`ustawienia.py`.** Sekcja opcjonalna jest zakladana tylko, gdy WSZYSTKIE jej klucze maja wartosc domyslna (dzis
  wylacznie `[sesja]`); stare sekcje przechodza te sama walidacje co przed zmiana (brak sekcji, nieznany klucz, typ);
  `[sesja]` z literowka w kluczu albo w nazwie sekcji = blad (test). Lista domyslna kopiowana, nie wspoldzielona.
- **Higiena.** 22 pliki, wszystkie z listy paczki (4.1); 19 nowych plikow: 0 znakow spoza ASCII, 0 znakow CR; brak
  sekretow w diffie; dane testowe z jawnie fikcyjnymi nazwami zlecen; plik listy "do dofrezowania" zawiera tylko
  kuwete, zeby, krazek, plytke, gniazdo i `sha16`.
- **pytest (PC, 1 przebieg):** `test_baza.py`, `test_ustawienia.py`, `test_session_wieczor.py` bez testu z prawdziwym
  `porownaj`: 81 passed, 1 deselected, 1 failed - `test_repo_nie_sledzi_danych_ani_ustawien_maszyny` wola
  `git ls-files`, a moja kopia z `git archive` nie jest repozytorium (blad srodowiska recenzenta, nie kodu).

## 5. Liczniki

- Uwagi: B 0, P 7, D 14. Sprawdzone uruchomieniem: P1-P7 (P6 w czesci), D1-D7, D9-D11; czytaniem: D8 (czesc), D12-D14.
- Schemat: 11 z 11 tabel i 0 roznic w nazwach / kolejnosci kolumn; 19 ograniczen NOT NULL i 2 DEFAULT ponad plan;
  4 wyzwalacze.
- Proby wlasne: 12 (wszystkie zakonczone, katalogi tymczasowe usuniete). Testy paczki: 81 passed + 1 nie do
  uruchomienia w mojej kopii + 1 pominiety celowo, z 83.

## 6. Czego NIE sprawdzilem

- Pelnego `pytest` (zakaz - PC byl przeciazony) ani testu `test_wynik_prawdziwego_porownaj_wchodzi_do_bazy`
  (wymaga Open3D i liczenia); zgodnosc kluczy wyniku z `porownaj.py` sprawdzona tylko czytaniem.
- Proby mutacyjnej wykonawcy (23 z 23) - nie powtarzana.
- Plikow `testy/dane_sesji/wynik_*.json` wiersz po wierszu (ok. 5 600 linii) - tylko naglowki, statusy gniazd jednego
  pliku i przeszukanie pod katem sciezek folderow.
- Zachowania na dysku sieciowym / w folderze OneDrive, przy braku miejsca na dysku, przy uszkodzonym pliku bazy
  innym niz "nie jest baza", przy bardzo duzej bazie (czasy zapytan - brak indeksu po dacie skanu).
- Prawdziwego `dane/decyzje.csv` z okna testowego (nie mam; wykonawca tez nie mial).
- Czy nazwa pliku skanu ze skanera (`skany.plik`, nazwa pliku wyniku) moze zawierac dane osobowe - zalezy od
  eksportu programu skanera (S5, pierwszy dzien skanera).
- Wspolpracy z A2 / A3 (klasa `ZdarzenieSkanu`, okno) - jeszcze nie istnieja; uwagi P2, P3, P5, P7 sa o kontrakcie
  dla nich.
- Kopii bazy dla programistow bez kolumn z nazwami (narzedzia nie ma - poza zakresem A1).
