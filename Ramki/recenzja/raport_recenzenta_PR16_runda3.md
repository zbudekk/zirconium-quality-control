# Raport recenzenta PR #16 - runda 3 (recenzja przyrostowa + test koncowy)

Data: 2026-11-17. Recenzent: swieza subsesja, niezalezna od wykonawcow i koordynatora; werdyktu koordynatora nie znalem.
Stan recenzowany: HEAD `adbf4ca` galezi `e3/a1` (PR #16 "E3-A1: baza i sesja wieczorna"). Przyrost: `git diff d7e1a55..adbf4ca`
ograniczony do plikow paczki (`stanowisko/baza.py`, `stanowisko/session.py`, `stanowisko/ustawienia.py`, `narzedzia/import_decyzji.py`,
`testy/test_baza.py`, `testy/test_session_wieczor.py`, `testy/test_ustawienia.py`, `opisy_modulow/baza.md`, `opisy_modulow/session.md`;
dodatkowo przeczytany raport wykonawcy sekcja 8 i jedna linia w `ustawienia.przyklad.toml`). Zmian ze scalenia `przed-skanerem` (`59eb7e2`) nie recenzowalem.
Zrodla: raport rundy 2 (`raport_recenzenta_PR16_runda2.md`, P1, P2, D1-D11), raport wykonawcy `raporty/E3-A1_2026-11-17.md` sekcja 8, `session.md`.
Metoda: przeczytane w calosci `session.py` (stan HEAD), diff `baza.py`, `ustawienia.py`, `import_decyzji.py`, diff trzech plikow testow
(kazda usunieta asercja), oba opisy; w silniku (`inspect.py`, `krawedz.py`, `match.py`, `porownaj.py`) tylko szablony tekstow `uwagi` / `opis` / `blad`.
Uruchomienia (tylko PC, konto zadan, katalog `<PC-katalog>\e3\r16c`, kod z `git archive HEAD`, ustawienia = kopia wzoru PC, `run.cmd` z limitem
2 watkow; zawsze 1 moj proces python; wolny RAM przed kazdym startem 16-17 GB):
(1) `proby_r3.py` - wlasne proby do czesci A (9 scenariuszy + 15 tekstow `bez_sciezek`), log `proby_r3.log`;
(2) `test_koncowy.py` - test koncowy (czesc B), log `test_koncowy.log`, wynik 8 z 8;
(3) jeden przebieg pytest trzech plikow paczki bez testu z prawdziwym `porownaj`: **154 passed, 1 failed, 2 deselected** - jedyny blad to
`test_repo_nie_sledzi_danych_ani_ustawien_maszyny` (`git ls-files` w kopii, ktora nie jest repozytorium; srodowisko, nie kod); 154 + 1 + 2 = 157 = liczba z raportu wykonawcy.
Log pelnego pytest wykonawcy odczytany: `e3\a1\pytest_9870c2a.log` = 568 passed / 3 skipped / 0 failed (kod po scaleniu); `adbf4ca` rozni sie od `9870c2a` tylko raportem.
Na MSI nie uruchamiano pytest ani obliczen (git, czytanie plikow; jedno wywolanie python wylacznie do wyswietlenia formatu `testy/dane_sesji/wynik_plytka1.json`).

## 0. Werdykt

**do scalenia po poprawkach** - nowe uwagi: B 0 / P 1 / D 5.

Runda 3 zalatwia oba P rundy 2 i osiem z jedenastu D (D1, D2, D4, D6, D7, D8, D10, D11; przy D6 skutek uboczny - nowe D4), D5 czesciowo
(nadmierne wycinanie - nowe D3), D3 i D9 swiadomie zostaja jako znane. Dla trybu `wieczor`
lista "do dofrezowania" ma teraz zawsze jedna pozycje na punkt: 4 wlasne sekwencje (Ukruszona x2 + cofniecie kazdej, OK, zastapienia i ich cofniecia)
nie znalazly ani podwojnej pozycji, ani zeba, ktory znika z listy. Test koncowy: 8 z 8 punktow. Zaden test rund 1-2 nie zostal oslabiony.
Do poprawy przed scaleniem jedna rzecz, tania: zab moze zniknac z listy, gdy ten sam projekt dostanie "Ukruszona" na skanie w trybie `rano`
(nowe P1 - dzis nie ma jeszcze wywolujacego z trybem `rano`, ale API go przyjmuje, a runda 3 zrobila z tej drogi znikniecie juz po jednym kliknieciu).

## 1. Uwagi rundy 2 -> stan

| Uwaga | Stan | Jak sprawdzone |
|---|---|---|
| P1 podwojna pozycja listy | zalatwiona dla trybu `wieczor`: pozycja projektu tylko dla pracy wskazanej przez `stan_punktow` (`session.py:936`), reszta w `powtorzenia`, wpis `ukruszona_powtorzona`, `na_liscie`, `pozycja_projektu`. Droga przez tryb `rano` - nowe **P1** | uruchomione: proby P1-1..P1-4 (tabela w pkt 4), test koncowy pkt 2 i 7, testy `test_p1r3_*` |
| P2 kasowanie plikow wynikow | zalatwiona: w `session.py` i `baza.py` nie ma `unlink` / `remove` / `rmtree` / `rename`; zapis `open(cel, "x")` (O_EXCL, atomowo - odporne na wyscig, inny blad niz `FileExistsError` wycofuje skan); zajeta nazwa -> `_2`; `osierocone_wyniki()` tylko wypisuje. Nadpisywany jest tylko plik listy CSV (`zapisz_do_dofrezowania`, zamierzone). Nazwa skanu w nazwie pliku - nowe D1, D2 | uruchomione: proba P2 (ta sama sekunda i `sha16` -> `..._2_wynik.json`, oba pliki zostaja), testy `test_p2r3_*`; czytane |
| D1 zastapienie bez numeru | zalatwiona: zastapienie wprost bez numeru u ktoregos skanu = odmowa "najpierw podaj numer" (wyjatek: ten sam plik); `podaj_numer_plytki` odrzuca numer sprzeczny z powiazaniem (po obu stronach) | uruchomione (proba D1: odmowa zastapienia, odmowa numeru 4 przy powiazaniu z plytka 3), test |
| D2 doba pozycji z czasu decyzji | zalatwiona: `doba` i `zmiana` pozycji z `skany.czas_analizy` (`miejsce()`, `session.py:928-931`) | czytane, test `test_d2r3_*` (w moim przebiegu zielony) |
| D3 czas lokalny bez strefy | znana, opisana (docstring `_w_oknie_ponownego_skanu`, `session.md` "Czas (D3)") - bez zmian w kodzie | czytane |
| D4 cofniecie dopuszczenia skanu, ktory zastapil inny | zalatwiona: odmowa z wlasciwa rada "najpierw cofnij zastapienie"; zdanie dla A10 w `session.md` | czytane, test |
| D5 `bez_sciezek` | czesciowo: wycina teraz sciezki wzgledne z separatorem, `//serwer`, `%ZMIENNA%\`, `$HOME/`, `~/`, apostrof w nazwie; `inspekcja.blad` i `uwagi` czyszczone w pliku wyniku. Znana granica (sama nazwa bez separatora) opisana jako wymaganie A2 / A3. Wycina "z zapasem" takze zwykle teksty - nowe **D3** | uruchomione (15 tekstow, pkt 3 nizej), test koncowy pkt 8 |
| D6 import nie z ostatniego | zalatwiona (plik musi byc przedluzeniem OSTATNIEGO importu); skutek uboczny przy ponownym imporcie starszego pliku - nowe **D4** | uruchomione (proba D6) |
| D7 blokada przepuszcza nieznane | zalatwiona: uklad spoza wzoru -> `plytka_nie_z_trybu` (dopuszczalny swiadomie), nieznany `tryb` -> `BladSesji` (takze w `przyjmij_blad`). Wszystkie 8 ukladow wbudowanych (`UKLADY_WBUDOWANE`) i 8 nazw z `[plytki]` wzoru PC pasuja do wzoru - blokada nie zatrzyma prawdziwej plytki | czytane, test `test_d7r3_*` |
| D8 walidacja `[sesja]` | zalatwiona: zmiana 1 = granica doby, okno > 0, nazwy osob przyciete, niepuste i rozne (ustawienia i konstruktor `Sesja`). Okno 0 ("nigdy nie proponuj") nie bylo potrzebne zadnej decyzji (wlasciciel: 60 min), minimum 1 min wystarcza do wylaczenia w praktyce; "zmiana 1 = granica doby" nie blokuje rozsadnego ukladu zmian (zawsze mozna zaczac zmiane 1 o granicy) | uruchomione (proba D8: 3 z 3 odmowy), testy |
| D9 unikat `frezowania` z NULL | znana: wymaganie dla A4 i decyzja przed A4 zapisane w `baza.md` | czytane |
| D10 potwierdzenie zdejmuje decyzje bez ostrzezenia | zalatwiona: `do_potwierdzenia` podaje `liczba_decyzji`, `liczba_ukruszonych`, `decyzje` skanu zastepowanego | czytane, test |
| D11 niescislosci, baza PR | zalatwiona: zdanie o godzinach zmian poprawione; testy na kodzie scalonym z `przed-skanerem` (log 568 / 3 / 0 odczytany); zgoda na `README.md` / `ui.md` opisana w raporcie 8.1 | czytane, log |

Twierdzenia raportu wykonawcy (sekcja 8) - sprawdzone: 8.1 wszystkie wiersze poza zastrzezeniami nizej; 8.2 liczby plikow paczki (157) i pelny pytest (log).
Zastrzezenia: 8.1 P1 "1600 krokow, 0 rozbieznosci" dotyczy tylko trybu `wieczor` (losowa proba nie uzywa `rano` - nowe P1); 8.3.1 "pozycja wskazuje
NAJNOWSZA prace" nie zawsze (nowe D5); 8.3.4 "dla tekstow prawdziwego `porownaj` nic nie jest zmieniane" - zgodne z szablonami tekstow silnika,
samego testu z `porownaj` nie uruchamialem. Proby mutacyjnej (25 z 25) nie sprawdzalem.

## 2. Nowe uwagi (B = blokujaca, P = poprawic przed scaleniem, D = drobna / moze zostac jako znana)

Sciezki wzgledem `Ramki/stanowisko/`. "Proba X" = `proby_r3.py` na PC.

| Nr | Waga | Plik:linia | Scenariusz (wejscie -> zly wynik) | Sprawdzone | Oczekiwane |
|---|---|---|---|---|---|
| P1 | P | `stanowisko/session.py:647-660` (`_praca_do_decyzji` - brak warunku na tryb), `757-760` (galaz "Ukruszona" w `_odswiez_punkt` bez trybu), `764-766` (szukanie innej ukruszonej pracy tylko w trybie cofanej), `918-922` i `936` (lista: tylko `wieczor` i tylko praca wskazana przez punkt) | Zab znika z listy "do dofrezowania", choc ma obowiazujaca "Ukruszona". Wieczorem praca p1 (projekt X) dostaje "Ukruszona" -> lista [p1]. Skan w trybie `rano` (plytka poranna, status `przyjety` - API to przyjmuje) z praca p2 tego samego projektu dostaje "Ukruszona": punkt X przechodzi na p2, lista (tylko `wieczor`) pomija p2, a p1 pomija, bo punkt na nia nie wskazuje -> **lista pusta**. Cofniecie decyzji na p2: punkt szuka innej ukruszonej pracy tylko w trybie `rano` -> `oczekuje` -> lista pusta trwale, mimo ze p1 nadal ma "Ukruszona". W rundzie 2 pierwszy krok nie chowal zeba (warunek byl tylko na stan punktu), runda 3 zrobila z tego znikniecie po jednym kliknieciu. `session.md` mowi, ze skany poranne "nie wchodza do stanu wieczoru ani list" - wplywaja jednak na liste. Dzis nikt nie wola `session` z trybem `rano` (poranek = A6), ale `sprawdz_tryb` jawnie go dopuszcza, a skutek (chipniety zab nie trafia do dofrezowania) jest grozniejszy niz podwojna pozycja z rundy 2. | Uruchomieniem (proba P1-5): po "Ukruszona" p1 `[(1, [])]`, punkt `('do_dofrezowania', 1)`; po "Ukruszona" p_rano `[]`, punkt `('do_dofrezowania', 2)`; po cofnieciu `[]`, punkt `('oczekuje', None)`; decyzje p1: `['ukruszona']`. | Do A6: decyzje o pracach tylko skanow `tryb = wieczor` (`_praca_do_decyzji`: `BladSesji` "decyzje poranne dojda w A6") albo `_odswiez_punkt` nie rusza punktu dla innego trybu; test z sekwencja P1-5. Alternatywnie (decyzja koordynatora): D z twardym wymaganiem dla A6 w `session.md`. |
| D1 | D | `stanowisko/session.py:414-416` (`rdzen` = nazwa pliku skanu w nazwie pliku wyniku), `325` (`skany.plik` = pelna sciezka), `875` (`stan_wieczoru.skany[].plik`) | Nazwa skanu w nazwie pliku wyniku (pytanie koordynatora): nazwa jest brana doslownie, tylko znaki zakazane w Windows (`<>:"/\|?*`, sterujace) zamieniane na `_`. Gdy skaner nazywa pliki wg zlecenia (S5 planu otwarte: "kazdy skan wymaga zlecenia"), np. `D:/Skaner/9911 Fikcyjny Pacjent/Fikcyjny Pacjent <gora>?.stl`, nazwisko trafia do nazwy pliku wyniku, do `skany.plik` (z folderem) i do `stan_wieczoru`. Nie jest to nowe w rundzie 3 (runda 2 miala `skanNNNNNN_<nazwa>`, `skany.plik` od rundy 1; `baza.md` zapisuje to jako "do sprawdzenia w pierwszym dniu skanera"), ale po P2 nazwa skanu nie jest juz potrzebna do unikalnosci - wystarcza czas + `sha16`. | Uruchomieniem (proba P2): plik `20261117_180000_000000000000c00c_Fikcyjny Pacjent _gora___wynik.json`, `skany.plik` i `stan_wieczoru` z pelna sciezka. | Usunac nazwe skanu z nazwy pliku wyniku (albo skrocic do bezpiecznego rdzenia, gdy S5 potwierdzi brak danych osobowych); rozstrzygnac `skany.plik` przy S5 / A2. |
| D2 | D | `stanowisko/session.py:414-426` | Bardzo dluga nazwa pliku skanu: nazwa pliku wyniku = 44 znaki + nazwa skanu; przy nazwie skanu > 211 znakow skladnik przekracza 255 znakow NTFS -> `OSError [Errno 22]`, wyjatek wychodzi z `przyjmij_wynik`, transakcja wycofana - skanu nie ma w bazie wcale (nawet jako `blad`). Dluga sciezka (> 260 znakow) na PC dziala. Malo prawdopodobne, ale skutek to zgubiony skan. | Uruchomieniem (proba P2): nazwa 150 i 205 znakow - przyjete (nazwa pliku 194 / 249 znakow, sciezka 253 / 308); 215 i 240 - `OSError`, skanow przybylo 0. | Ta sama poprawka co D1 (bez nazwy skanu albo przyciecie np. do 60 znakow). |
| D3 | D | `stanowisko/baza.py:233` (`_SCIEZKA_WZGLEDNA`: "dwa ukosniki" i "ukosnik + rozszerzenie" z dowolnymi slowami i spacjami pomiedzy), `258-263` (poczatek cofany do ogranicznika albo poczatku wiersza), `267-270` (koniec = koniec wiersza) | Pytanie koordynatora D5: liczby z ukosnikiem i spacjami sa bezpieczne, ale data z rokiem, dwa ulamki bez przecinka i trzy czlony z ukosnikami wycinaja caly wiersz (albo wszystko od ostatniego dwukropka / przecinka / nawiasu). Dzisiejsze szablony `uwagi` / `opis` / `blad` silnika takich ukladow nie maja (sprawdzone grepem), wiec dotyczy tresci wyjatkow i przyszlych komunikatow; w dzienniku `zdarzenia` znieksztalcenie jest nieodwracalne (tylko dopisywanie). Danych nie ujawnia - blad jest "w bezpieczna strone". Przyklady wejscie -> wyjscie ponizej tabeli. | Uruchomieniem (15 tekstow, `proby_r3.log`). | Dopisac do opisu granicy (`baza.md`, docstring): "data d/m/rrrr, dwa ulamki bez przecinka i a/b/c zostana wyciete"; ewentualnie wymagac litery w ktoryms czlonie wzglednej sciezki z dwoma ukosnikami. |
| D4 | D | `narzedzia/import_decyzji.py:89-97`; docstring `11-13`, pomoc `--wymus` `129` | Skutek uboczny D6: ponowny import STARSZEGO pliku, ktory jest w calosci w bazie (np. kopia `decyzje.csv` sprzed dopisania wierszy), konczy sie odmowa "nie jest przedluzeniem ostatniego importu ... swiadomy import calosci: --wymus". W rundzie 2 to bylo "nic nowego". Kto poslucha rady, dubluje wszystkie wiersze (tabela tylko do dopisywania). Docstring modulu nadal mowi "przedluzeniem wczesniejszego importu". | Uruchomieniem (proba D6): import a.csv (3) -> 3, b.csv (5) -> 2, ponownie a.csv -> odmowa; z `--wymus` decyzji 5 -> 8. | Plik rowny ktoremus wczesniejszemu importowi (ta sama liczba wierszy i skrot) = "juz zaimportowany", 0 dopisanych, bez rady `--wymus`; poprawic docstring. |
| D5 | D | `stanowisko/session.py:563` (`cofnij_zastapienie`), `582` (`dopusc_plytke`), `609-612`, `757-760` | Po cofnieciu zastapienia (albo ponownym dopuszczeniu) punkt przechodzi na prace PRZYWROCONEGO, starszego skanu, choc nowsza "Ukruszona" jest na innym skanie - wbrew raportowi 8.3.1 ("pozycja wskazuje NAJNOWSZA prace") i docstringowi `do_dofrezowania` ("ostatnio oznaczona"). Nadal jedna pozycja i ten sam zab (kuweta, zeby, krazek), ale plytka / gniazdo / doba pozycji pokazuja starszy skan, a przy skanach z dwoch dob pozycja moze przejsc do widoku poprzedniej doby. | Uruchomieniem (proba P1-4): "Ukruszona" p1 (15:00) i p2 (17:05, nowsza); zastapienie skanu p1 skanem p2 i cofniecie -> `[(1, [2])]` (pozycja p1, p2 w `powtorzenia`). | `_przelicz_punkty_skanu(aktywny=True)` wybiera najnowsza obowiazujaca "Ukruszona" projektu zamiast nadpisywac; albo poprawic opis i raport. |

Przyklady D3 (`baza.bez_sciezek`, uruchomione):

| Wejscie | Wyjscie |
|---|---|
| `pas 0.15 / 0.20 mm` | bez zmian |
| `pas 0.15/0.20 mm, prog 0.25 mm` | bez zmian |
| `pokrycie 0.85 < 0.9: popraw ulozenie / skan ponownie, ubytki nieliczone` (szablon `inspect`) | bez zmian |
| `skala o 0.50 % - sprawdz wspolczynnik / krazek` (szablon `match`) | bez zmian |
| `filar 2: sprawdzono 61% linii brzegu, najdluzszy odcinek bez sprawdzenia 1.4 mm` (szablon `inspect`) | bez zmian |
| `ValueError: shape (3,)/(4,) mismatch` | bez zmian |
| `Uwaga: skan z 17/11/2026 ma drgniecie` | `Uwaga: <sciezka>` |
| `skan z 17/11/2026 godz. 18:05 - drgniecie` | `<sciezka>` |
| `2026/11/17 18:05 skan` | `<sciezka>` |
| `korony 3/5 i 4/5 gotowe` | `<sciezka>` |
| `data 17/11 i 18/11` | `<sciezka>` |
| `wartosci 1/2/3 mm` | `<sciezka>` |
| `statusy zielony/zolty/czerwony: 3/4/1` | `<sciezka>` |
| `tryb linia/plaszczyzna wg ustawienia.toml` | `<sciezka>` |
| `patrz https://example.org/a/b` | `patrz http<sciezka>` (kosmetyka: "s:/" uznane za dysk) |

## 3. Test koncowy koordynatora (czesc B) - 8 z 8 zaliczonych

Skrypt wlasny `<PC-katalog>\e3\r16c\test_koncowy.py` (zalacznik A, 98 linii; biblioteka standardowa + `stanowisko.baza`, `stanowisko.session`;
format wyniku tylko odczytany z `testy/dane_sesji/wynik_plytka1.json`, danych i testow wykonawcy nie uzywa). Baza i wyniki w katalogu tymczasowym
(usuniety na koncu). Indeks: 1 zlecenie (folder `9911 Testowski_Jan`), 9 projektow, 9 wpisow frezowania (nazwy tylko w 3 tabelach z nazwami).
Wyniki plytek: sciezka puli `C:/Pula/Cyrkon/9911 Testowski_Jan` w `foldery_projektow`, w `uwagi` wyniku i gniazd (bezwzgledna), w `inspekcja.uwagi`
(wzgledna `Cyrkon\9911 Testowski_Jan\n.stl`), w `inspekcja.blad` (w apostrofach) i w tekscie bledu `przyjmij_blad`. Log: `test_koncowy.log`.

| Pkt | Co | Wynik |
|---|---|---|
| 1 | 3 plytki (nr 1, 2, 3; `wieczorna`, `wieczorna`, `okragla_wieczorna`; tryb `wieczor`; 3 + 4 + 2 gniazda), operatorzy na liscie; 2 x "Ukruszona" (rozni operatorzy), 1 x "OK", 1 cofniecie (drugiej "Ukruszona"); zrzut (stan wieczoru, lista, `skany`, `prace`, `decyzje`, `stan_punktow`) -> zamkniecie -> nowe `otworz` + nowa `Sesja` -> zrzut | ZALICZONY: 631 pol przed / 631 po, 0 roznic; 4 decyzje; `stan_punktow` = [(1, do_dofrezowania, praca 1), (5, oczekuje, None)] |
| 2 | liczniki: prace w bazie = gniazda w plikach wynikow; lista = oczekiwane pozycje | ZALICZONY: 9 prac = 9 gniazd w 3 plikach; lista = 1 pozycja (praca 1, kuweta 9911, zab 11, krazek K1) = oczekiwana |
| 3 | decyzja bez operatora (sesja po ponownym otwarciu, nikt nie wybrany), z osoba spoza listy, przy pustej liscie | ZALICZONY: 3 z 3 odmow `BladSesji`, 0 nowych wierszy `decyzje` |
| 4 | plytka poranna (`poranna`, 2 gniazda zielone) w trybie `wieczor` | ZALICZONY: status `plytka_nie_z_trybu`, 0 zielonych, liczniki puste, decyzja "OK" odrzucona |
| 5 | ta sama plytka po 59 min / inna po 61 min | ZALICZONY: 59 min - propozycja jest; 61 min - brak (nowy wsad) |
| 6 | skan 05:55 (doba 17.11) + powtorka 06:05 (doba 18.11) | ZALICZONY: propozycja [(skan 10, poprzedni 9)] mimo zmiany doby |
| 7 | na koncu (17 prac z 10 plikow + 1 skan `blad`) liczniki i lista ponownie | ZALICZONY: 17 prac = 17 gniazd; lista nadal [praca 1] |
| 8 | "testowski" (bez wielkosci liter): 7 tabel poza `zlecenia`, `projekty`, `frezowania`, `excel_zapisy` (47 wierszy, takze `zdarzenia`), 10 plikow katalogu wynikow (nazwy i tresc) + plik listy CSV, wszystkie teksty zwrocone przez `session` (zrzuty, stan obu dob, listy, konflikty, `pozycja_projektu`, `osierocone_wyniki`, `sciezka_wyniku`, 4 komunikaty `BladSesji`) | ZALICZONY: 0 / 0 / 0 wystapien; kontrola: 19 wystapien w tabelach z nazwami (dane wejsciowe naprawde zawieraly igle), 61 znacznikow `<sciezka>` w plikach wynikow i 1 w dzienniku |

Uwaga do pkt 8: test obejmuje nazwe podana jako sciezka (tak, jak chcial koordynator). Sama nazwa bez separatora przechodzi - to opisana znana granica (wymaganie dla A2 / A3).

## 4. Proby do czesci A (P1) - wszystkie uruchomione, `proby_r3.log`

Ta sama plytka 7 zeskanowana dwa razy (15:00 i 17:00 = nowy wsad), projekt X w gniezdzie 1 obu skanow: praca p1 i p2, "Ukruszona" na obu.

| Sekwencja | Lista (pozycja, powtorzenia) | Ocena |
|---|---|---|
| 2 x Ukruszona -> cofnij p2 | [(p2, [p1])] -> [(p1, [])] | dobrze (pozycja wraca na p1) |
| 2 x Ukruszona -> cofnij p1 | [(p2, [])] | dobrze |
| 2 x Ukruszona -> OK p1 -> OK p2 | [(p2, [])] -> [] | dobrze |
| zastapienie skanu p2 ponownym skanem (17:30) -> cofniecie | [(p1, [])] -> [(p2, [p1])] | dobrze |
| zastapienie skanu p1 skanem p2 -> cofniecie | [(p2, [])] -> [(p1, [p2])] | jedna pozycja, ale na starszej pracy (D5) |
| Ukruszona p1 (wieczor) -> Ukruszona p_rano (tryb `rano`) -> cofnij p_rano | [(p1, [])] -> [] -> [] | zab znika (P1) |

## 5. Na co patrzylem i nie budzi zastrzezen

- **Niezmiennik listy w trybie `wieczor`.** Punkt zmieniaja tylko `_odswiez_punkt` (decyzja, cofniecie) i `_przelicz_punkty_skanu` (zastapienie, cofniecie
  zastapienia, dopuszczenie, cofniecie dopuszczenia); kazda zmiana statusu skanu jest wykonana PRZED przeliczeniem, wiec szukanie "innej ukruszonej pracy"
  nie widzi skanu, ktory wlasnie przestal byc aktywny. Import nie rusza `stan_punktow`. Nie znalazlem drogi do znikniecia ani podwojenia poza P1 / D5.
- **Plik wyniku (P2).** Nazwa niezalezna od numeracji bazy, `open(..., "x")`, petla tylko na `FileExistsError`; sciezka w `skany.wynik_json` wzgledna
  od folderu bazy i tak samo rozwiazywana w `osierocone_wyniki` (bez falszywych sierot). Sieroty po zabitym procesie i po starej bazie zostaja.
- **Walidacja (D8).** `ustawienia.py` przycina nazwy przed walidacja, wiec `["A", "A "]` daje blad unikalnosci; konstruktor `Sesja` sprawdza to samo.
- **Testy rund 1-2 nieoslabione.** Usuniete asercje: kazde `do_potwierdzenia == [...]` zamienione na `potw(...) == [...]` (te same pola; nowe pola sprawdza
  `test_d10r3_*`); w `test_p5_*` "dwie pozycje" -> "jedna pozycja + `powtorzenia`" (= P1); okno 0 -> okno 1 i granica 0 / [7, 19] -> 7 / [7, 19] (= D8);
  przypadki "nieznany uklad / tryb = brak powodu" usuniete, bo D7 odwraca zachowanie (nowy test sprawdza odwrotnosc); `test_d3_*` zastapiony
  mocniejszym `test_p2r3_*` (pliki starej bazy i bazy z kopii zostaja).
- **Higiena.** Runda 3 zmienia 11 plikow, wszystkie z listy paczki; dodane linie bez CR; znaki diakrytyczne tylko w plikach, ktore juz je mialy
  (`ustawienia.py`, `test_ustawienia.py`, `ustawienia.przyklad.toml`); dane testowe fikcyjne.

## 6. Czego NIE sprawdzilem

- Pelnego pytest (zakaz; log wykonawcy 568 / 3 / 0), testu z prawdziwym `porownaj` (Open3D) i testow `git ls-files` (kopia nie jest repozytorium).
- Proby mutacyjnej wykonawcy (25 z 25) ani jego losowej proby poza tym, ze przeszla w moim przebiegu.
- Zmiany czasu na prawdziwym zegarze, dwoch procesow piszacych naraz, duzej bazy (czas listy biezacej), dysku sieciowego / OneDrive.
- Prawdziwych nazw plikow ze skanera (S5), prawdziwego `decyzje.csv`, kontraktow A2 / A3 i logiki poranka A6 (P1 dotyczy wlasnie styku z A6).
- Rzeczywistego wyscigu dwoch zapisow tego samego pliku wyniku (tylko odczyt kodu: `open(..., "x")` jest atomowe).

## Zalacznik A. `test_koncowy.py` (na PC: `<PC-katalog>\e3\r16c\test_koncowy.py`, uruchomienie `run.cmd test_koncowy.py`)

```python
"""Test koncowy PR #16 (recenzent, runda 3): wlasny skrypt, biblioteka standardowa + stanowisko.baza / stanowisko.session."""
import datetime as dt, json, shutil, tempfile
from pathlib import Path
from stanowisko import baza as B, session as SE

IGLA, OSOBY, DATA = "testowski", ["Osoba X", "Osoba Y"], "2026-11-17"
PULA = "C:/Pula/Cyrkon/9911 Testowski_Jan"
WYN = []

def punkt(nr, ok, opis): WYN.append((nr, ok)); print(f"PUNKT {nr}: {'ZALICZONY' if ok else 'NIEZALICZONY'} - {opis}")

class Zegar:
    def __init__(s, t): s.ustaw(t)
    def ustaw(s, t): s.t = dt.datetime.fromisoformat(t)
    def __call__(s): return s.t

def wynik(numer, uklad, prace):  # prace: (gniazdo, sha16 projektu, status_gniazda)
    g = [{"gniazdo": n, "status_fragmentu": "praca", "status": "zielony", "pewnosc": 0.8, "uwagi": [f"pula {PULA}/{n}.stl niedostepna"],
          "kandydaci": [{"id": p, "pokrycie": 0.9, "zeby": ["11"]}], "status_gniazda": st,
          "inspekcja": {"status": "ok" if st == "zielony" else "ubytki", "pokrycie": 0.9, "ubytki": [] if st == "zielony" else [{"srednica_mm": 0.6}],
                        "uwagi": [f"blad: Cyrkon\\9911 Testowski_Jan\\{n}.stl"], "blad": f"FileNotFoundError: brak '{PULA}\\{n}.stl'"}} for n, p, st in prace]
    return {"skan": f"plytka_{numer}.stl", "plytka": uklad, "plytka_wybor": "auto", "uklad_zgodny": True, "numer": numer, "numer_zrodlo": "dolki",
            "foldery_projektow": [PULA], "czas_s": {"razem": 10.0}, "uwagi": [f"pula: {PULA}"], "gniazda": g}

def przyjmij(s, z, czas, numer, uklad, prace, tryb="wieczor"):
    z.ustaw(czas); n = len(s.baza.wiersze("SELECT id FROM skany")) + 1
    return s.przyjmij_wynik({"plik": f"D:/Skaner/eksport/plytka_{numer}_{n}.stl", "sha16": f"{0xa000 + n:016x}", "rozmiar": 1000 + n,
                             "czas_pliku": czas}, wynik(numer, uklad, prace), tryb=tryb)

def praca(s, skan, g): return s.baza.wiersz("SELECT id FROM prace WHERE skan_id = ? AND gniazdo = ?", (skan, g))["id"]

def plaskie(o, p=""):
    if isinstance(o, dict): return [x for k, v in o.items() for x in plaskie(v, f"{p}/{k}")]
    if isinstance(o, list): return [x for i, v in enumerate(o) for x in plaskie(v, f"{p}[{i}]")]
    return [(p, o)]

def zrzut(s): return {"stan": s.stan_wieczoru(DATA), "lista": s.do_dofrezowania(), **s.baza.zrzut(["skany", "prace", "decyzje", "stan_punktow"])}

kat = Path(tempfile.mkdtemp(prefix="r16c_")); plik, wyn = kat / "stanowisko.sqlite", kat / "wyniki"
z = Zegar(f"{DATA}T17:00:00"); teksty = []
s = SE.Sesja(B.otworz(plik, zegar=z), operatorzy=OSOBY, katalog_wynikow=wyn, zegar=z)
with s.baza.transakcja():  # indeks: nazwa folderu i pliku zlecenia tylko w tabelach z nazwami
    zl = s.baza.wstaw("zlecenia", zrodlo="cyrkon", folder="9911 Testowski_Jan", kuweta="9911")
    for i in range(1, 10):
        pr = s.baza.wstaw("projekty", zlecenie_id=zl, plik=f"Testowski_Jan_{i}.stl", sha16=f"{i:016x}", zeby=str(10 + i))
        s.baza.wstaw("frezowania", projekt_id=pr, plik_w_raporcie=f"Testowski_Jan_{i}.stl", krazek=f"K{i}", data=DATA)
P = lambda i: f"{i:016x}"
s1 = przyjmij(s, z, f"{DATA}T18:00:00", 1, "wieczorna", [(1, P(1), "czerwony"), (2, P(2), "zielony"), (3, P(3), "zielony")])
s2 = przyjmij(s, z, f"{DATA}T18:10:00", 2, "wieczorna", [(1, P(4), "zielony"), (2, P(5), "czerwony"), (3, P(6), "zielony"), (4, P(7), "zielony")])
s3 = przyjmij(s, z, f"{DATA}T18:20:00", 3, "okragla_wieczorna", [(1, P(8), "czerwony"), (2, P(9), "zielony")])
s.wybierz_operatora("Osoba X"); z.ustaw(f"{DATA}T18:30:00")
A, Bp, C = praca(s, s1, 1), praca(s, s2, 2), praca(s, s3, 1)
s.ukruszona(A); s.ukruszona(Bp, operator="Osoba Y"); s.ok(C); s.cofnij(Bp)
przed = zrzut(s); s.baza.zamknij()
s = SE.Sesja(B.otworz(plik, zegar=z), operatorzy=OSOBY, katalog_wynikow=wyn, zegar=z)
po = zrzut(s); a, b = dict(plaskie(przed)), dict(plaskie(po))
rozne = [k for k in a.keys() | b.keys() if a.get(k, "<brak>") != b.get(k, "<brak>")]
punkt(1, not rozne and len(a) > 300, f"zrzut przed / po ponownym otwarciu: pol {len(a)} / {len(b)}, roznic {len(rozne)}; decyzje {len(przed['decyzje'])}, "
      f"punkty {[(w['projekt_id'], w['stan'], w['praca_id']) for w in po['stan_punktow']]}")
gniazd = sum(len(json.loads(f.read_text(encoding="utf-8"))["gniazda"]) for f in wyn.glob("*_wynik.json"))
prac = s.baza.wiersz("SELECT count(*) AS n FROM prace")["n"]; lista = s.do_dofrezowania(); teksty += [przed, po, lista]
punkt(2, prac == gniazd == 9 and [(x["praca_id"], x["kuweta"], x["zeby"], x["krazek"]) for x in lista] == [(A, "9911", "11", "K1")],
      f"prac w bazie {prac}, gniazd w {len(list(wyn.glob('*_wynik.json')))} plikach {gniazd}; lista {[(x['praca_id'], x['zeby'], x['krazek']) for x in lista]} (oczekiwana [{A}])")
n_dec = len(s.baza.wiersze("SELECT id FROM decyzje")); odm = []
for f in (lambda: s.ukruszona(praca(s, s2, 1)), lambda: s.ukruszona(praca(s, s2, 1), operator="Ktos Spoza Listy"),
          lambda: SE.Sesja(s.baza, operatorzy=[], zegar=z).ok(praca(s, s2, 1))):
    try: f(); odm.append(False)
    except SE.BladSesji as e: odm.append(True); teksty.append(str(e))
punkt(3, all(odm) and len(s.baza.wiersze("SELECT id FROM decyzje")) == n_dec, f"decyzja bez operatora / spoza listy / pusta lista: odmowy {sum(odm)} z 3, nowych decyzji 0")
sr = przyjmij(s, z, f"{DATA}T19:00:00", 7, "poranna", [(1, P(2), "zielony"), (2, P(3), "zielony")])
st = [x for x in s.stan_wieczoru(DATA)["skany"] if x["id"] == sr][0]
try: s.ok(praca(s, sr, 1), operator="Osoba X"); odrz = False
except SE.BladSesji as e: odrz = True; teksty.append(str(e))
zielone = sum(1 for p in st["prace"] if p["kolor"] == "zielony")
punkt(4, st["status"] == "plytka_nie_z_trybu" and zielone == 0 and st["liczniki"] == {} and odrz, f"plytka poranna w trybie wieczor: status {st['status']}, zielonych {zielone}, decyzja odrzucona {odrz}")
s4a = przyjmij(s, z, f"{DATA}T20:00:00", 4, "wieczorna", [(1, "e" * 16, "zielony")]); s4b = przyjmij(s, z, f"{DATA}T20:59:00", 4, "wieczorna", [(1, "e" * 16, "zielony")])
s5a = przyjmij(s, z, f"{DATA}T21:00:00", 5, "wieczorna", [(1, "f" * 16, "zielony")]); s5b = przyjmij(s, z, f"{DATA}T22:01:00", 5, "wieczorna", [(1, "f" * 16, "zielony")])
pot = {(x["skan_id"], x["poprzedni_id"]) for x in s.stan_wieczoru(DATA)["do_potwierdzenia"]}
punkt(5, (s4b, s4a) in pot and not any(k[0] == s5b for k in pot), f"59 min: propozycja {(s4b, s4a) in pot}; 61 min: propozycja {any(k[0] == s5b for k in pot)} (oczekiwane: tak / nie)")
s6a = przyjmij(s, z, "2026-11-18T05:55:00", 6, "wieczorna", [(1, "d" * 16, "zielony")]); s6b = przyjmij(s, z, "2026-11-18T06:05:00", 6, "wieczorna", [(1, "d" * 16, "zielony")])
st18 = s.stan_wieczoru("2026-11-18"); pot18 = [(x["skan_id"], x["poprzedni_id"]) for x in st18["do_potwierdzenia"]]; teksty.append(st18)
punkt(6, pot18 == [(s6b, s6a)] and s.doba(s.baza.wiersz("SELECT czas_analizy FROM skany WHERE id = ?", (s6a,))["czas_analizy"]) == DATA,
      f"05:55 (doba {DATA}) i 06:05 (doba 2026-11-18): propozycje {pot18}")
z.ustaw("2026-11-18T06:10:00"); s.przyjmij_blad({"plik": "D:/Skaner/eksport/plytka_8.stl", "sha16": "b" * 16}, OSError(f"nie mozna otworzyc '{PULA}/x.stl'"))
gniazd = sum(len(json.loads(f.read_text(encoding="utf-8"))["gniazda"]) for f in wyn.glob("*_wynik.json")); prac = s.baza.wiersz("SELECT count(*) AS n FROM prace")["n"]
lista2 = s.do_dofrezowania(); csv_l = s.zapisz_do_dofrezowania(katalog=kat / "listy")
teksty += [s.stan_wieczoru(DATA), lista2, s.konflikty(DATA), s.pozycja_projektu(A), [str(p) for p in s.osierocone_wyniki()], str(s.sciezka_wyniku(s1))]
punkt(7, prac == gniazd and [x["praca_id"] for x in lista2] == [A], f"na koniec: prac {prac} = gniazd {gniazd}; lista {[x['praca_id'] for x in lista2]}")
zr = s.baza.zrzut(); poza = {t: sum(str(v).lower().count(IGLA) for w in zr[t] for v in w.values()) for t in B.TABELE if t not in B.TABELE_Z_NAZWAMI}
w_nazwach = sum(str(v).lower().count(IGLA) for t in B.TABELE_Z_NAZWAMI for w in zr[t] for v in w.values())
pliki = sum(f.name.lower().count(IGLA) + f.read_text(encoding="utf-8").lower().count(IGLA) for f in list(wyn.iterdir()) + [csv_l])
ses = json.dumps(teksty, ensure_ascii=False, default=str).lower().count(IGLA)
znaczniki = (sum(f.read_text(encoding="utf-8").count(B.ZNACZNIK_SCIEZKI) for f in wyn.glob("*_wynik.json")), sum(str(w["dane"]).count(B.ZNACZNIK_SCIEZKI) for w in zr["zdarzenia"]))
punkt(8, sum(poza.values()) == 0 and pliki == 0 and ses == 0 and w_nazwach > 0 and all(znaczniki),
      f"'{IGLA}': tabele poza 4 z nazwami {sum(poza.values())} ({len(poza)} tabel, wierszy {sum(len(zr[t]) for t in poza)}), pliki wynikow + lista {pliki} "
      f"({len(list(wyn.iterdir()))} plikow), teksty session {ses}; kontrola: w 4 tabelach z nazwami {w_nazwach}, znacznikow <sciezka> w plikach / dzienniku {znaczniki}")
s.baza.zamknij(); shutil.rmtree(kat)
print(f"WYNIK: {sum(ok for _, ok in WYN)} z {len(WYN)} punktow zaliczonych")
```

Wynik (`test_koncowy.log`):

```
PUNKT 1: ZALICZONY - zrzut przed / po ponownym otwarciu: pol 631 / 631, roznic 0; decyzje 4, punkty [(1, 'do_dofrezowania', 1), (5, 'oczekuje', None)]
PUNKT 2: ZALICZONY - prac w bazie 9, gniazd w 3 plikach 9; lista [(1, '11', 'K1')] (oczekiwana [1])
PUNKT 3: ZALICZONY - decyzja bez operatora / spoza listy / pusta lista: odmowy 3 z 3, nowych decyzji 0
PUNKT 4: ZALICZONY - plytka poranna w trybie wieczor: status plytka_nie_z_trybu, zielonych 0, decyzja odrzucona True
PUNKT 5: ZALICZONY - 59 min: propozycja True; 61 min: propozycja False (oczekiwane: tak / nie)
PUNKT 6: ZALICZONY - 05:55 (doba 2026-11-17) i 06:05 (doba 2026-11-18): propozycje [(10, 9)]
PUNKT 7: ZALICZONY - na koniec: prac 17 = gniazd 17; lista [1]
PUNKT 8: ZALICZONY - 'testowski': tabele poza 4 z nazwami 0 (7 tabel, wierszy 47), pliki wynikow + lista 0 (10 plikow), teksty session 0; kontrola: w 4 tabelach z nazwami 19, znacznikow <sciezka> w plikach / dzienniku (61, 1)
WYNIK: 8 z 8 punktow zaliczonych
```

Skrypt prob do czesci A: `<PC-katalog>\e3\r16c\proby_r3.py` (111 linii, log `proby_r3.log`) - zostawiony na PC, nie wklejony.
