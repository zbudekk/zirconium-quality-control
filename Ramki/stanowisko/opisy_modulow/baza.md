# baza - plik SQLite stanowiska (E3-A1, 17.11.2026; po rundach 2 i 3 recenzji PR #16)

**Co robi.** Zaklada i otwiera lokalna baze programu (`stanowisko/baza.py`): schemat z planu etapu 3, sekcja 3.4 (11 tabel, jeden plik - decyzje wlasciciela DW1 i DW2 z 17.11.2026), migracje schematu z kopia pliku, zrzut stanu i kopia na zyczenie. Tylko biblioteka standardowa (`sqlite3`), zadnych nowych zaleznosci. Baze pisze jeden proces (proces okna przez `session`); narzedzia i raporty otwieraja ja do odczytu. **Do bazy wchodzi sie tylko przez `baza.otworz`** - to ono wlacza klucze obce i czekanie na blokade; polaczenie otwarte inaczej (`sqlite3.connect` w narzedziu, przegladarka bazy) nie pilnuje kluczy obcych.

**Wejscie.** Sciezka pliku: `[sciezki] baza` z `ustawienia.toml` (domyslnie `dane/stanowisko.sqlite`; sciezka wzgledna liczona od katalogu programu - `baza.sciezka_bazy(ust)`). Plik lezy poza repozytorium (`dane/` i `*.sqlite` sa w `.gitignore`) i ma lezec poza OneDrive.

**Wyjscie / API.**
- `otworz(plik, tylko_odczyt=False, czekaj_ms=5000)` -> `Baza`. Nowy plik: zalozenie schematu. Plik starszy: kopia pliku, potem migracja. Plik nowszy niz program, plik niebedacy baza, nieudana migracja: `BladBazy` z komunikatem dla czlowieka, plik bez zmian. `tylko_odczyt=True`: nic nie zaklada i nie migruje.
- `Baza`: `wstaw(tabela, **kolumny)` (nazwy sprawdzane ze schematem), `wiersze(sql, parametry)`, `wiersz(...)`, `wykonaj(...)`, `transakcja()` (calosc albo nic; zagniezdzona nalezy do zewnetrznej), `zdarzenie(zrodlo, typ, dane, skan_id)` (dziennik; wycina sciezki z tekstow), `zrzut(tabele=None, bez_nazw=False)` (tabela -> wiersze), `kopia(cel)` (spojna kopia przy otwartym polaczeniu), `wersja()`, `zamknij()`; pola `plik`, `kopia_przed_migracja`, `zmigrowano`.
- Baza zajeta przez inny program (blokada dluzej niz `czekaj_ms`): `BladBazy` "baza jest zajeta przez inny program ... niczego nie zapisano" - nie surowy blad SQLite; po zwolnieniu blokady ta sama operacja przechodzi.
- `bez_sciezek(tekst)`, `oczysc(dane)`: zastepuja sciezki bezwzgledne znacznikiem `<sciezka>` (patrz "Dane osobowe").
- Stale: `TABELE` (11 nazw), `KOLUMNY_Z_NAZWAMI` / `TABELE_Z_NAZWAMI`, `OGRANICZENIA_PONAD_3_4`, `MIGRACJE`, `WERSJA_SCHEMATU` (= 1).

**Tabele.** `zlecenia` (folder zlecenia, kuweta), `projekty` (plik STL zlecenia = punkt pracy, `sha16`), `cechy_stl`, `frezowania` (krazek, wspolczynnik), `skany`, `prace` (jedno gniazdo jednego skanu), `decyzje` (tylko dopisywanie), `sesje_pieca`, `stan_punktow`, `excel_zapisy`, `zdarzenia` (dziennik, tylko dopisywanie). E3-A1 wypelnia `skany`, `prace`, `decyzje`, `stan_punktow` (czesc wieczorna) i `zdarzenia`; pozostale tabele sa zalozone dla kolejnych paczek (indeks A4, pula A5, poranek A6, Excel A9).

**Schemat a sekcja 3.4 planu.** Zgodne z planem: 11 tabel, nazwy i kolejnosc kolumn, klucze glowne i obce, 4 unikaty, 2 indeksy (`zlecenia.kuweta`, `projekty.sha16`). `zdarzenia.skan_id` bez klucza obcego - jak w planie. PONAD plan (plan tego nie podaje; decyzja koordynatora po recenzji PR #16: zostaja, kazde z uzasadnieniem; lista jest tez w kodzie - `OGRANICZENIA_PONAD_3_4` - i w tescie `test_p1_ograniczenia_ponad_sekcje_3_4...`):

| Ograniczenie | Uzasadnienie (jedno zdanie) |
|---|---|
| `zlecenia.zrodlo` NOT NULL | czesc unikatu (zrodlo, folder): przy pustej wartosci SQLite nie pilnowalby unikatu zlecenia |
| `zlecenia.folder` NOT NULL | czesc unikatu: zlecenie to folder, bez nazwy folderu wiersz nic nie znaczy |
| `zlecenia.usuniety` NOT NULL DEFAULT 0 | flaga 0 / 1: zapytania filtruja `usuniety = 0`, pusta wartosc gubilaby zlecenie; piszacy moze ja pominac |
| `projekty.zlecenie_id` NOT NULL | czesc unikatu (zlecenie_id, plik): punkt pracy zawsze nalezy do zlecenia |
| `projekty.plik` NOT NULL | czesc unikatu: punkt pracy to plik STL w folderze zlecenia |
| `projekty.usuniety` NOT NULL DEFAULT 0 | flaga 0 / 1: `session` szuka punktu po `sha16` wsrod `usuniety = 0` |
| `skany.status` NOT NULL | logika wieczoru wybiera skany po statusie; skan bez statusu znikalby ze stanu po cichu |
| `prace.skan_id` NOT NULL | praca istnieje tylko jako gniazdo konkretnego skanu (klucz obcy i czesc unikatu) |
| `prace.nr_fragmentu` NOT NULL | czesc unikatu (skan_id, gniazdo, nr_fragmentu): rozroznia dwie prace w jednym gniezdzie |
| `decyzje.rodzaj` NOT NULL | wiersz dziennika decyzji bez rodzaju nie daje sie zinterpretowac ani cofnac |
| `decyzje.czas` NOT NULL | kolejnosc i metryki licza sie z czasu decyzji; braku nie da sie uzupelnic (tylko dopisywanie) |
| `stan_punktow.stan` NOT NULL | tabela istnieje po to, zeby trzymac stan punktu; listy to zapytania po tej kolumnie |
| `zdarzenia.czas`, `.zrodlo`, `.typ` NOT NULL | wpis dziennika bez czasu, nadawcy i typu jest bezuzyteczny dla metryk; wszystkie trzy wpisuje zawsze `Baza.zdarzenie` |
| 4 wyzwalacze na `decyzje` i `zdarzenia` | "tylko dopisywanie" z planu: `UPDATE` i `DELETE` koncza sie bledem |

Razem 15 NOT NULL i 2 DEFAULT. Zdjete w rundzie 2 (blokowalyby zapis przewidziany planem): `frezowania.plik_w_raporcie`, `frezowania.data`, `frezowania.krazek` (wpis reczny wspolczynnika na krazek, K7: wiersz bez pliku, `zrodlo` = `reczny`; raport bez daty albo bez identyfikatora krazka) i `projekty.sha16` (plik zaindeksowany, zanim dalo sie policzyc skrot). Skutki ograniczen, o ktorych trzeba pamietac:
- Unikat `frezowania (plik_w_raporcie, krazek, data)` dziala tylko dla wierszy, ktore maja wszystkie trzy wartosci: w SQLite pusta wartosc (NULL) jest rozna od kazdej innej, wiec drugi identyczny wpis reczny (bez pliku albo bez daty) NIE jest odrzucany. Przed dopisaniem wpisu recznego piszacy (A4) musi sam sprawdzic, czy juz jest. To samo dotyczy unikatu `prace` dla pracy poza gniazdem (`gniazdo` puste) - `session` numeruje fragmenty sam.
- Wyzwalacze: wpisu w `decyzje` i `zdarzenia` nie da sie poprawic ani usunac (takze dziennika nie da sie skracac); migracja zmieniajaca te tabele musi najpierw zdjac wyzwalacze.
- Typy kolumn (plan ich nie podaje): czasy jako tekst ISO czasu lokalnego do sekundy (`2026-11-17T19:02:11`), flagi 0 / 1, `zeby` jako tekst `26-27`, `kuweta` jako tekst, `miniatura` jako BLOB, statusy i rodzaje jako tekst bez listy zamknietej (nowy status nie wymaga migracji; w rundzie 2 doszly statusy skanu `import` i `plytka_nie_z_trybu` oraz rodzaje decyzji `cofniecie`, `cofnij_zastapienie`). Klucze `id` bez AUTOINCREMENT.

**Dane osobowe (DW2 po decyzji wlasciciela z 17.11.2026).** Nazwy folderow i plikow zlecen (z nazwiskami) wolno trzymac w CZTERECH tabelach i nigdzie indziej: `zlecenia.folder`, `zlecenia.folder_norm`, `projekty.plik`, `frezowania.plik_w_raporcie`, `frezowania.raport_plik`, `excel_zapisy.folder` (stala `KOLUMNY_Z_NAZWAMI`). Nie wolno ich trzymac w `skany`, `prace`, `decyzje`, `zdarzenia`, plikach wynikow, liscie "do dofrezowania", logach ani komunikatach wyjatkow.
- `Baza.zdarzenie` wycina sciezki z kazdego tekstu w `dane` (`bez_sciezek`, rozszerzone w rundzie 3 - D5): bezwzgledne (dysk, zasob sieciowy `\\serwer` i `//serwer`, zmienne srodowiskowe `%USERPROFILE%\`, `$HOME/`, katalog domowy) i wzgledne z separatorem (`a\b`, `a/b/c`, `a/plik.stl`). Nazwy folderow maja spacje, wiec funkcja wycina z zapasem: sciezka w cudzyslowie albo apostrofach konczy sie na zamykajacym znaku, inna - na koncu wiersza; sciezka wzgledna zaczyna sie od poprzedniego ogranicznika (`: ; , = ( [ {`, cudzyslow) albo od poczatku wiersza. Pojedyncze `A/B`, `km/h`, `0.91/0.95` sciezka nie sa. ZNANA GRANICA = wymaganie dla wywolujacego (A2, A3): sama nazwa folderu albo pliku zlecenia bez separatora nie jest rozpoznawana - nie wolno jej wkladac do dziennika ani do tekstow dla `session`.
- `Baza.zrzut()` zwraca tez kolumny z nazwami; do logow, raportow i dla programistow tylko `zrzut(bez_nazw=True)` (te kolumny puste). Narzedzia robiacego kopie pliku bazy bez nazw jeszcze nie ma.
- `skany.plik` to plik skanu ze skanera, nie plik zlecenia (czy nazwa ze skanera moze zawierac dane osobowe - do sprawdzenia w pierwszym dniu skanera).

**Migracje.** Wersja schematu = `PRAGMA user_version`. Nowa wersja: dopisac `MIGRACJE[n] = (polecenia SQL...)` i podniesc `WERSJA_SCHEMATU`; przejscie idzie wersja po wersji, kazda w jednej transakcji (blad = baza zostaje w poprzedniej wersji). Przed migracja istniejacego pliku powstaje kopia `<nazwa>.kopia_v<stara wersja>_<RRRRMMDD_GGMMSS>.sqlite` obok bazy, a w `zdarzenia` wpis `system / migracja`; gdy identyczna kopia tej wersji juz jest (poprzednia proba sie nie udala), nie powstaje nastepna. Kazda zmiana schematu to zmiana modelu danych: najpierw opis dla wlasciciela (plan, DW1). Bazy produkcyjnej jeszcze nie ma, wiec poprawki rundy 2 zmienily definicje wersji 1 bez migracji - baze zalozona kodem sprzed rundy 2 (proby na PC) trzeba zalozyc od nowa.

**Kryterium "dziala".** `testy/test_baza.py` (45 testow, w tym 23 przypadki `bez_sciezek`: 15 sciezek wycinanych, 7 zwyklych tekstow bez zmian, 1 znana granica): 11 tabel i kolumny rowne tabeli z sekcji 3.4, indeksy i unikaty, klucze obce, `decyzje` i `zdarzenia` nie daja sie zmienic ani usunac, statusy przyjmuja dowolny tekst, zrzut po zamknieciu i otwarciu identyczny (kryterium 5), migracja 0 -> 1 i 1 -> 3 z kopia pliku, baza nowsza niz program = odmowa bez zmiany pliku, nieudana migracja cofnieta w calosci i bez mnozenia kopii (kryterium 7, D2), nazwy tylko w czterech tabelach i zrzut bez nazw (kryterium 8), lista ograniczen ponad 3.4 i wpis reczny frezowania (P1), baza zajeta (D1).

**Zalozenia i granice.**
- Tryb dziennika SQLite domyslny (jeden plik, bez plikow `-wal`); jeden proces piszacy. Kopia sprzed migracji to kopia pliku (`shutil.copy2`) zrobiona przy zamknietym polaczeniu - przy drugim procesie piszacym w tej samej chwili moglaby byc niespojna (kopia na zyczenie `Baza.kopia` uzywa mechanizmu SQLite).
- Wymaganie dla A4 (D9 rundy 3): "raz na krazek" dla wpisu recznego (K7) nie jest pilnowane przez baze (unikat nie dziala przy pustym `plik_w_raporcie`) - A4 sprawdza sama przed dopisaniem. Indeks czesciowy, np. unikat (`krazek`, `data`) dla wierszy bez pliku, bylby zmiana schematu: tani przed pierwsza baza produkcyjna, potem migracja - do decyzji wlasciciela przed A4.
- Poza kluczem glownym i unikatami sa tylko indeksy wymienione w planie; brak indeksu po czasie skanu - przy obecnej skali (kilkaset wierszy dziennie) wystarcza, do zmierzenia w A10.
- Klucze obce pilnuje tylko polaczenie z `baza.otworz`; okresowe `PRAGMA foreign_key_check` to zadanie samokontroli (A11).
- Nie ma jeszcze: usuwania starych skanow (DW4; klucz `[sesja] przechowuj_skany_dni` jest tylko zapisany), cyklicznej kopii zapasowej (A11), tabeli `testy_wykrywalnosci` (A10, migracja do wersji 2), kontroli, czy plik bazy nie lezy w folderze OneDrive (A11), narzedzia kopii bazy bez nazw.
