# Raport recenzenta PR #16 - runda 2 (recenzja przyrostowa)

Data: 2026-11-17. Recenzent: swieza subsesja, niezalezna od wykonawcow i koordynatora; werdyktu koordynatora nie znalem.
Stan recenzowany: HEAD `d7e1a55` galezi `e3/a1` (PR #16 "E3-A1: baza i sesja wieczorna"). Zakres: `git diff 3fdf76f..d7e1a55`
(15 plikow: kod, testy, opisy, raport wykonawcy, scalony raport rundy 1); kontekst: `git diff origin/przed-skanerem...origin/e3/a1`.
Zrodla: raport rundy 1 (`raport_recenzenta_PR16_runda1.md`, P1-P7, D1-D14), raport wykonawcy sekcja 7, `session.md`, `baza.md`, plan
etapu 3 (`origin/przed-skanerem`) sekcje 3.3, 3.4, 4.1, 6 (Z1), decyzje wlasciciela z 17.11 (`00_NADZOR_STAN.md` w `przed-skanerem`).
Metoda: przeczytane w calosci `baza.py`, `session.py` (stan HEAD), diff `import_decyzji.py`, `ustawienia.py`, `ustawienia.przyklad.toml`,
diff trzech plikow testow i `indeks.json`, oba opisy, raport sekcja 7; w `porownaj.py` / `match.py` / `plate.py` tylko budowa wyniku,
statusy fragmentow i nazwy ukladow.
Uruchomienia (tylko PC, `<PC-katalog>\e3\r16b`, kod z `git archive HEAD`, ustawienia = kopia wzoru PC, `run.cmd` z limitem 2 watkow;
1 moj proces python naraz; wolny RAM przed startem 15 GB i 13 GB): (1) wlasny skrypt `proby_r2.py` (biblioteka standardowa + pakiet
`stanowisko`, 9 prob, 18 s, katalogi tymczasowe usuniete); (2) jeden przebieg pytest trzech plikow paczki bez testu z prawdziwym
`porownaj` i bez testu `git ls-files` (moja kopia nie jest repozytorium): **116 passed, 2 deselected, 0 failed** (= 118 z raportu
wykonawcy). Log pelnego pytest wykonawcy odczytany: `e3\a1\pytest_11e1cb1.log` = 498 passed / 3 skipped / 0 failed; `d7e1a55` rozni sie
od `11e1cb1` tylko raportem. Na MSI nie uruchamiano pytest ani obliczen.

## 0. Werdykt

**do scalenia po poprawkach** - nowe uwagi: B 0 / P 2 / D 11.

Runda 2 zalatwia wszystkie siedem uwag P rundy 1 i wdraza osiem decyzji wlasciciela zgodnie z ich trescia; testy odtwarzaja scenariusze
z rundy 1 (import + "cofnij", praca skanu `niezgodny_uklad`, plik o starej dacie / polnoc, plytka 2 "zastepujaca" plytke 1, kolor
po decyzji). Losowe sekwencje decyzji, zastapien, dopuszczen i cofniec (60 x 40 krokow, 818 udanych operacji) nie znalazly zadnej
niespojnosci `stan_punktow`, kolorow ani "zielonego mimo decyzji / statusu". Zaden test rundy 1 nie zostal oslabiony.
Do poprawy przed scaleniem dwie nowe rzeczy, obie tanie: lista "do dofrezowania" moze pokazac ten sam zab dwa razy (P1) i poprawka D3
kasuje pliki wynikow innej bazy (P2).

## 1. Uwagi rundy 1 -> stan

| Uwaga | Stan | Jak sprawdzone |
|---|---|---|
| P1 NOT NULL ponad 3.4 | zalatwiona: zdjete z `frezowania.plik_w_raporcie`, `.data`, `.krazek`, `projekty.sha16`; zostaje 15 NOT NULL + 2 DEFAULT + 4 wyzwalacze, kazde z uzasadnieniem w `baza.OGRANICZENIA_PONAD_3_4`, `baza.md`, raporcie 7.3; test pilnuje dokladnej listy. Zadne nie blokuje zapisu z planu A4-A9 (sekcja "Schemat" nizej) | uruchomione (test), czytane |
| P2 `foldery_projektow` w pliku wyniku | zalatwiona dla sciezek bezwzglednych: `do_zapisu` usuwa pole (zostaje liczba) i wycina sciezki z kazdego tekstu; slownik silnika nietkniety | uruchomione (`test_p2_*`); test z prawdziwym `porownaj` - tylko wynik wykonawcy |
| P3 opis bledu w dzienniku | zalatwiona: `typ` + opis bez sciezek, do 500 znakow (przyciecie PO wycieciu); `Baza.zdarzenie` czysci kazdy wpis | uruchomione (`test_p3_*`); granice funkcji - nowe D5 |
| P4 punkt / lista rozjechane | zalatwiona: (a) skany importu `status = import`, zapytanie `inne` tylko po skanach aktywnych tego trybu; (b) decyzje tylko na skanie `przyjety` (16 z 16 prob odrzuconych) | uruchomione (testy + proba I: 0 naruszen punktow) |
| P5 co to jest wieczor | zalatwiona wg decyzji wlasciciela (doba 06:00-06:00 od chwili przyjecia, okno 60 min takze przez 06:00, lista biezaca) | uruchomione (testy, proby D, E) |
| P6 zastapienie bez kontroli i bez cofania | zalatwiona: (a) odmowa przy roznych numerach (gdy oba znane) albo rodzinach ukladu; (b) `cofnij_zastapienie` przywraca skan i decyzje. Luka przy nieznanym numerze - nowe D1 | uruchomione (testy, proby C, F) |
| P7 kolor bez decyzji | zalatwiona = decyzja 3 | uruchomione (test, proba I) |
| D1 baza zajeta | zalatwiona (`BladBazy`; test uzywa dwoch polaczen w jednym procesie) | czytane, test |
| D2 mnozenie kopii | czesciowo: identyczna kopia nie powstaje drugi raz; kopia nadal `shutil.copy2` (znane) | test |
| D3 osierocony plik wyniku | zalatwiona, ale poprawka wprowadza nowe **P2** | uruchomione (proba B) |
| D4 cykl punktu | opis poprawiony, zachowanie do A6 (znane) | czytane |
| D5 zgadywanie krazka | zalatwiona (2 wpisy = krazek pusty; dane testowe przeniesione na inny zab - zasadnie) | test |
| D6 brak `uklad_zgodny` | nie (do A2, znane) | czytane |
| D7 dublowanie importu | czesciowo - nowe D6 | uruchomione (proba H) |
| D8 komunikaty / zgodnosc decyzji | czesciowo: komunikaty bez nazw osob; reszta do A3 (znane) | test |
| D9 unikat `prace` z NULL | nie (znane) | czytane |
| D10 to samo zdarzenie dwa razy | nie (do A3, znane) | czytane |
| D11 tylko przez `otworz` | zalatwiona opisem | czytane |
| D12 jedna stala kolumn z nazwami | zalatwiona (`KOLUMNY_Z_NAZWAMI`, `zrzut(bez_nazw=True)`) | test |
| D13 skrot ustawien | zalatwiona (`[plytki]`, `[match]`, `[inspect]`) | test |
| D14 niescislosci raportu | zalatwiona; baza PR nadal `przed-skanerem` - nowe D11 | czytane |

## 2. Decyzje wlasciciela z 17.11 -> wdrozenie

| Nr | Decyzja | Ocena | Dowod |
|---|---|---|---|
| 1 | cofniecie = nowy wiersz `cofniecie` z id cofanej decyzji | wdrozone poprawnie (`cofnij`, `cofnij_dopuszczenie`; `cofnij_zastapienie` osobnym rodzajem) | test k2, proba I |
| 2 | lista operatorow wymagana; stary `ustawienia.toml` sie wczytuje; import z operatorem `import` | wdrozone poprawnie: kazda droga decyzji (o pracy, cofniecie, zastapienie, cofniecie zastapienia, numer plytki, dopuszczenie i jego cofniecie) wola `_operator`; przy pustej liscie 7 z 7 prob odrzuconych, skany nadal przyjmowane | testy (uruchomione), czytane `session.py:261-272, 409-438` |
| 3 | "Ukruszona" (takze niewykryta) = czerwona i liczona jako ukruszona; "OK" na czerwonej = `zatwierdzona_ok`; status w bazie bez zmian | wdrozone poprawnie (`_kolor`, liczniki po kolorze, licznik `decyzje`); "OK" na zielonej / zoltej / szarej tez daje `zatwierdzona_ok` - spojne | test p7, proba I: 0 przypadkow "ukruszona nie czerwona" i "zielony mimo decyzji" |
| 4 | nazwy folderow i plikow zlecen tylko w 4 tabelach | wdrozone poprawnie w bazie, pliku wyniku, liscie i dzienniku dla nazw podanych jako sciezka bezwzgledna; inne postacie przechodza - D5 | testy k8, p2, p3; proba G |
| 5 | 3 zmiany, doba 06:00 -> 06:00 nazwana data poczatku, od chwili przyjecia; numer zmiany z godziny, bez kolumny | wdrozone poprawnie (05:59:59 -> poprzednia doba, 06:00:00 -> nowa; zmiany 05:59 = 3, 06:00 = 1, 14:00 = 2, 22:00 = 3); uwagi D2 (doba pozycji listy z czasu decyzji) i D3 (czas lokalny bez strefy) | test p5, proby D, E |
| 6 | ta sama plytka (numer + rodzina) w 60 min = propozycja, takze przez 06:00; po godzinie nowy wsad; reczne zastapienie tylko tej samej plytki, cofalne | wdrozone poprawnie (59 i 60 min - propozycja, 61 - nie; z kodu: 60 min 30 s - nie); kwadrat i kolo jednej rodziny traktowane jako jedna (numery n1-n6 / n8-n9 sie nie powtarzaja - poprawne); uwagi D1, D3; skutek "nowego wsadu" dla listy - P1 | test p5, p6a, p6b; proby A, C, E |
| 7 | otwarte pozycje "do dofrezowania" nie znikaja na granicy doby | wdrozone poprawnie (lista biezaca); przez liste biezaca podwojna pozycja (P1) trwa takze miedzy dobami | test p5, proba A |
| 8 | blokada plytki niezgodnej z trybem; dopuszczenie swiadome, cofalne | wdrozone poprawnie: 6 z 6 ukladow, 0 kolorow, decyzje odrzucane, nic na listach i w `stan_punktow`, nie zastepuje i nie jest zastepowany, dopuszczenie z operatorem i wpisem w dzienniku; uwagi D4, D7 | testy blokady (9), proby F, I |
| K | wpis reczny na krazek bez pliku; sciezki puli poza plikami wynikow i dziennikiem; decyzje tylko na `przyjety` | wdrozone poprawnie | testy p1, p2, p4b |

## 3. Nowe uwagi (B = blokujaca, P = poprawic przed scaleniem, D = drobna / moze zostac jako znana)

Sciezki wzgledem `Ramki/stanowisko/`. "Proba X" = `proby_r2.py` na PC.

| Nr | Waga | Plik:linia | Scenariusz (wejscie -> zly wynik) | Sprawdzone | Oczekiwane |
|---|---|---|---|---|---|
| P1 | P | `stanowisko/session.py:816-819` (warunek pozycji), `707-710` (`_prace_skanow` nie czyta `stan_punktow.praca_id`), `867` (konflikt pomija prace "Ukruszona") | Pozycja listy = kazda praca z "Ukruszona" w skanie aktywnym, gdy punkt jej projektu ma stan `do_dofrezowania` - bez sprawdzenia, ze punkt wskazuje TE prace. Dwie aktywne prace tego samego projektu z "Ukruszona" -> ten sam zab dwa razy na liscie i w pliku CSV, a w `stan_punktow` jeden punkt. Drogi: (a) ta sama plytka z tymi samymi pracami zeskanowana ponownie po ponad 60 min (nowy wsad wg decyzji 6) i zab oznaczony na obu skanach - konflikt tego zeba NIE jest zglaszany, bo prace "Ukruszona" sa wylaczone z konfliktow; (b) zab dofrezowany nastepnego dnia znow ukruszony - pozycja z dnia 1 zostaje obok pozycji z dnia 2 (lista biezaca); (c) `cofnij_zastapienie`, gdy oba skany maja "Ukruszona" na tym zebie. Lista idzie do frezowania (Z6) - grozi podwojne dofrezowanie. Zasada 4 sekcji 3.4: lista to zapytanie po `stan_punktow`. W rundzie 1 to samo bylo mozliwe tylko w obrebie jednego wieczoru; lista biezaca przenosi to przez doby. | Uruchomieniem: proba A (a): 2 pozycje i 2 wiersze pliku / 1 punkt, konflikt = nie; (b): 2 pozycje z dob 17.11 i 18.11; proba I: 8 z 60 losowych sekwencji. | Pozycja z projektem tylko, gdy `stan_punktow.praca_id = prace.id` (jedna na punkt) + prace bez projektu jak dotad; test z przypadkami (a) i (b). |
| P2 | P | `stanowisko/session.py:389-391` (`_zapisz_wynik`, kasowanie `skan{id:06d}_*_wynik.json`) | Poprawka D3 kasuje KAZDY plik `skanNNNNNN_*_wynik.json` o numerze nowego skanu, zakladajac, ze to sierota tej samej bazy. Gdy baza powstaje od nowa przy tym samym `[sciezki] wyniki` (`baza.md` zaleca to po rundzie 2) albo zostanie przywrocona z kopii, numery skanow zaczynaja sie powtarzac i pierwszy nowy skan kasuje plik wyniku skanu ze starej bazy / skanu sprzed awarii. Plik wyniku to jedyne miejsce szczegolow ubytkow (zasada 3 sekcji 3.4), a wyniki maja byc trzymane bezterminowo (DW4). Kasowanie jest nieodwracalne. | Uruchomieniem: proba B1 (baza od nowa: plik wyniku skanu 1 starej bazy znika, zostaje 1 plik), B2 (baza przywrocona z kopii: plik skanu 2 sprzed przywrocenia znika). | Nie kasowac: przeniesc do podkatalogu albo dopisac przyrostek (`.sierota`), albo nazwa pliku wyniku z czescia unikalna (np. `sha16` skanu / czas przyjecia); test na oba przypadki. |
| D1 | D | `stanowisko/session.py:595` (`_niezgodnosc` - numer porownywany tylko, gdy oba znane), `640-649`, `538-551` (`podaj_numer_plytki`) | Plytki kwadratowe (n1-n6) maja dolki poza polem skanu, wiec wieczorem zwykle nie maja numeru. Zastapienie wskazane wprost miedzy dwoma skanami bez numeru tej samej rodziny jest przyjmowane, choc to rozne plytki; numery wpisane potem (1 i 2) tez sa przyjmowane i powiazanie zostaje. "Ukruszona" z pierwszej plytki znika z listy. Cofniecie istnieje, wiec szkoda jest odwracalna. | Uruchomieniem (proba C). | Zastapienie wprost przy braku numeru u ktoregos skanu: najpierw numer albo wyrazne ostrzezenie dla A3; `podaj_numer_plytki` odmawia numeru sprzecznego z `zastepuje_id`. |
| D2 | D | `stanowisko/session.py:820` (doba pozycji z czasu decyzji), `694-701`, `793` | Skan przyjety o 05:50 nalezy do doby 17.11, "Ukruszona" klikniete o 06:05 daje pozycje doby 18.11: widok 17.11 ma skan bez pozycji, widok 18.11 pozycje bez skanu (lista biezaca ma ja raz). Decyzja 5 mowi o chwili przyjecia skanu. Pokrewne: ponowny skan 05:50 / 06:10 bez potwierdzenia daje dwa aktywne skany w dwoch dobach - konflikt (liczony per doba) ich nie widzi. | Uruchomieniem (proba D); konflikt - czytane. | Doba pozycji = doba skanu albo zdanie w kontrakcie A3 ("widok doby filtruje po czasie decyzji"). |
| D3 | D | `stanowisko/session.py:222-223, 602-607`; `149-159` (`_czas_iso`) | Wszystkie czasy to lokalny czas bez strefy. Okno 60 min liczone z roznicy takich czasow: przy zmianie czasu jesienia skan 02:05 i skan 02:55 z drugiego przebiegu godziny 2 (110 min rzeczywistych) daje propozycje "ponowny skan"; skan 02:50 i 02:10 po cofnieciu zegara (20 min) - brak propozycji; wiosna 01:50 -> 03:10 (20 min) - brak. Tak samo przy zegarze cofnietym przez synchronizacje (ujemna roznica = brak propozycji). Zmiana 3 pracuje o tej porze; to tylko propozycja, raz w roku. `_czas_iso` przy czasie ze strefa ucina strefe bez przeliczenia (dzis `czas_pliku` to tylko informacja). | Uruchomieniem (proba E); `_czas_iso` czytane. | Okno liczyc z czasu bezwzglednego (np. `astimezone()` / znacznik epoki przy zapisie) albo zapisac granice w opisie; doba moze zostac lokalna. |
| D4 | D | `stanowisko/session.py:514-531` (`cofnij_dopuszczenie`), `483-485`, `509` | (a) Cofniecie dopuszczenia skanu, ktory wczesniej zastapil inny skan tej plytki: stary zostaje `zastapiony`, nowy wraca do blokady - zaden skan plytki nie jest aktywny, a `cofnij_zastapienie` odmawia z rada "najpierw cofnij pozniejsze zastapienie" (mylaca; trzeba ponownie dopuscic). (b) Ponowne dopuszczenie przywraca dawne decyzje bez nowego klikniecia (zamierzone, testowane). (c) Decyzje na skanie zablokowanym / zastapionym zostaja w `decyzje` jako niecofniete - metryki A10 musza filtrowac po statusie skanu. | Uruchomieniem (proba F); (b), (c) czytane i test wykonawcy. | (a) komunikat z wlasciwa rada albo odmowa cofniecia dopuszczenia, gdy skan ma `zastepuje_id`; (b) pytanie 1; (c) zdanie w `session.md` dla A10. |
| D5 | D | `stanowisko/baza.py:228-250` (`bez_sciezek`), `stanowisko/session.py:136-141` (`do_zapisu`) | Funkcja wycina tylko sciezki bezwzgledne (wykonawca to przyznaje). Przecieka (6 z 8 prob): sciezka wzgledna, `//serwer/...` (ukosniki), sciezka w cudzyslowie z apostrofem w nazwie folderu (koniec na apostrofie), `%USERPROFILE%\...`, sama nazwa folderu (np. tekst `KeyError`), sama nazwa pliku STL zlecenia. Nowe w `przed-skanerem` (nie w tym PR): `porownaj` wpisuje tresc wyjatku inspekcji do `inspekcja.blad` i `uwagi` - po scaleniu trafi do pliku wyniku przez `do_zapisu` z ta sama ochrona. | Uruchomieniem (proba G); `porownaj` czytane. | Kontrakt A2 / A3 jest w `session.md`; dodatkowo w `do_zapisu` i `przyjmij_blad` maskowac tez nazwy `*.stl` i sciezki wzgledne z separatorem, albo do pliku wyniku brac z wyjatku tylko typ. |
| D6 | D | `narzedzia/import_decyzji.py:89-97` | Odmowa dziala tylko, gdy plik nie zaczyna sie od ZADNEGO wczesniejszego importu. Plik, ktory zgadza sie z pierwszym importem (7 wierszy), ale zmienia wiersze dopisane drugim importem, jest przyjety: zmienione wiersze dochodza drugi raz (12 decyzji w bazie przy 10 wierszach pliku); tabela jest tylko do dopisywania. | Uruchomieniem (proba H). | Porownywac z OSTATNIM importem (plik musi byc jego przedluzeniem), inaczej odmowa / `--wymus`. |
| D7 | D | `stanowisko/session.py:105, 130-133, 275, 294` | Blokada przepuszcza (fail-open): uklad o nazwie spoza wzoru `_WZOR_UKLADU` (opcjonalnie `okragla_`, potem `wieczorna` albo `poranna`, opcjonalnie `_rNN`; np. nowy uklad dopisany w `[plytki]` pod inna nazwa) oraz `tryb` inny niz `wieczor` / `rano` (literowka w A3) - wtedy skan jest `przyjety`, a przy literowce dodatkowo niewidoczny w stanie wieczoru. Pierwsze opisane w `session.md`. | Czytane; test wykonawcy potwierdza `powod_nie_z_trybu("uklad_ktorego_program_nie_zna", "wieczor") is None`. | `przyjmij_wynik` odrzuca nieznany `tryb` (`BladSesji`); dla ukladu spoza wzoru co najmniej ostrzezenie w `stan_wieczoru`. |
| D8 | D | `stanowisko/ustawienia.py:242-246`; `stanowisko/session.py:193-199, 267-270` | Walidacja nowych kluczy jest poprawna (godziny 0-23, lista niepusta i scisle rosnaca, okno >= 0, typy bez `bool`; testy 9 przypadkow), ale nie wiaze `zmiany_start_godz[0]` z `granica_doby_godz`: np. 6 i [7, 15, 23] -> 06:30 to doba nowa, a zmiana 3. Osoba wpisana na liste z bialym znakiem na koncu nie da sie wybrac (strip tylko po stronie wyboru; komunikat "nie ma na liscie"). | Czytane. | Ostrzezenie albo blad przy `zmiany_start_godz[0] != granica_doby_godz`; strip nazw przy wczytaniu listy. |
| D9 | D | `stanowisko/baza.py:128` | Unikat `frezowania (plik_w_raporcie, krazek, data)` nie dziala dla wpisow recznych (plik NULL), wiec "raz na krazek" (K7) pilnuje tylko A4 (opisane w `baza.md`). Indeks czesciowy, np. `UNIQUE (krazek, data) WHERE plik_w_raporcie IS NULL`, jest tani teraz, po pierwszej bazie produkcyjnej to migracja. | Uruchomione (test wykonawcy `test_p1_wpis_reczny_*`), czytane. | Decyzja przed A4 (zmiana schematu = opis dla wlasciciela). |
| D10 | D | `stanowisko/session.py:629-654`, `779-780` | Potwierdzenie "ponowny skan" zdejmuje wszystkie "Ukruszona" starego skanu z listy (Z4: decyzje nie przechodza), a zab, ktory program uznal za zielony, znow jest zielony. `do_potwierdzenia` nie podaje, ile decyzji przestanie obowiazywac, wiec okno nie ma z czego ostrzec. | Czytane; test wykonawcy `test_k3_*`. | Kontrakt A3: w `do_potwierdzenia` liczba decyzji "Ukruszona" skanu zastepowanego i ostrzezenie przed potwierdzeniem. |
| D11 | D | raport wykonawcy 7.4.5; `opisy_modulow/session.md:63`; `opisy_modulow/README.md`, `ui.md`; galaz | (a) "Godziny zmian 2 i 3 to zalozenie koordynatora" - wlasciciel potwierdzil je 17.11 (`00_NADZOR_STAN.md`). (b) `opisy_modulow/README.md` i `ui.md` sa spoza listy 4.1 (pliki wspolne, sekcja 9); raport mowi "dozwolone w tej rundzie", zapisu zgody w repo nie znalazlem; zmiany sa male, innej otwartej galezi z tymi plikami na `origin` nie ma. (c) Galaz stoi na `a6cf3a4`, a `origin/przed-skanerem` ma od tego czasu 28 commitow w 23 plikach (m.in. `porownaj.py`); wspolnych plikow z PR brak, ale testy PR nie byly uruchamiane na polaczonym kodzie. | Czytane (`git diff --name-only`, `git log`). | Poprawic zdanie; potwierdzic zgode koordynatora w stanie paczki; przed scaleniem pytest na polaczeniu z biezacym `przed-skanerem`. |

## 4. Na co patrzylem i nie budzi zastrzezen

- **Logika czasu.** Granice 05:59:59 / 06:00:00 (doba), 59 / 60 / 61 min (okno, liczone wlacznie, ulamki minut sie licza), zmiany z godziny,
  przedzial doby jako porownanie tekstow ISO w jednym formacie (`teraz()` w `Sesja` i `Baza` - ten sam format, `zdarzenia` dostaja czas sesji).
  Dwa skany tej samej plytki w tej samej sekundzie: roznica 0 min = propozycja, kolejnosc po `id`. Data pliku skanu nie wplywa na dobe.
- **Zielone mimo decyzji / statusu.** Nie znalazlem drogi: skan nieaktywny (`zastapiony`, `niezgodny_uklad`, `plytka_nie_z_trybu`, `blad`,
  `import`) = brak koloru i poza licznikami, konfliktami i lista; "Ukruszona" = `czerwony` takze na zielonej; `do_powtorzenia` = zielony ->
  zolty; status przywracany po cofnieciu zastapienia / dopuszczeniu liczony z prac (`_status_z_prac`) jest rowny pierwotnemu dla wyniku
  z `porownaj` (fragmenty `podwojny` / `poza_gniazdem` zawsze sa w `gniazda[]`, `plate.py:545-555, 700-703`). Proba I: 0 naruszen.
- **Spojnosc `stan_punktow` po sekwencjach** (decyzja -> zastapienie -> cofniecie zastapienia -> cofniecie decyzji, w roznych kolejnosciach,
  takze z dopuszczeniem i jego cofnieciem): punkt zawsze wskazuje prace z obowiazujaca "Ukruszona" w skanie aktywnym, a bez takiej pracy
  nie jest `do_dofrezowania` (proba I + reczne przejscie 4 sekwencji). Jedyna niespojnosc to liczba pozycji listy (P1).
- **Schemat a paczki A4-A9.** 15 NOT NULL: zadne nie dotyczy kolumny, ktora A4 (indeks, CSV, wpis reczny), A5, A6, A8 (`zdarzenia` z
  potwierdzeniami ramki), A9 (`excel_zapisy` - bez ograniczen) czy A10 (nowa tabela) mialyby zostawiac puste. Wyzwalacze blokuja tylko
  `UPDATE` / `DELETE` w `decyzje` i `zdarzenia` - plan ich nie przewiduje. Unikat `frezowania` z NULL - D9.
- **`ustawienia.py`.** Nowe klucze `[sesja]` tylko opcjonalne (sekcja dalej w `SEKCJE_OPCJONALNE`), stary plik dostaje wartosci domyslne,
  lista domyslna kopiowana; zamrozona lista kluczy wymaganych bez zmian.
- **Testy rundy 1 nieoslabione.** Kazda usunieta asercja ma odpowiednik rowny albo mocniejszy; trzy zmiany zachowania wynikaja wprost z
  decyzji (pusta lista operatorow, ta sama plytka nastepnego dnia, skrot ustawien bez `[ramki]`); w `indeks.json` drugi wpis frezowania
  przeniesiony z zeba 14 na 24, zeby test k2 mial jeden wpis, a nowy test D5 dwa.
- **Higiena.** 15 plikow; nowe linie w plikach paczki ASCII, bez CR; znaki diakrytyczne tylko w plikach, ktore juz je mialy
  (`README.md`, `ui.md`, `ustawienia.py`, wzor ustawien); planu, `00_NADZOR_STAN.md` i plikow silnika nie ruszano; dane testowe fikcyjne.

## 5. Pytanie do wlasciciela

1. Plytka nie z trybu: technik ja swiadomie dopuscil, oznaczyl zab "Ukruszona", potem cofnal dopuszczenie i jeszcze raz dopuscil.
   Czy to "Ukruszona" ma wrocic samo (tak jest teraz), czy technik ma zaznaczyc zab od nowa? (Rzadki przypadek; obie odpowiedzi sa proste.)

## 6. Czego NIE sprawdzilem

- Pelnego pytest (zakaz; wynik wykonawcy z logu 498 / 3 / 0), testu z prawdziwym `porownaj` (Open3D, obciazenie PC) i testu `git ls-files`.
- Proby mutacyjnej wykonawcy (38 z 38).
- Kodu PR scalonego z biezacym `origin/przed-skanerem` (D11 c).
- Zmiany czasu na prawdziwym zegarze systemu - tylko podane recznie czasy lokalne (proba E).
- Dwoch procesow piszacych naraz, duzej bazy (czasy zapytan listy biezacej), dysku sieciowego / OneDrive.
- Prawdziwego `dane/decyzje.csv`, nazw plikow ze skanera (`skany.plik`, nazwa pliku wyniku - S5), kontraktow A2 / A3 (jeszcze ich nie ma).
- Plikow `testy/dane_sesji/wynik_*.json` wiersz po wierszu (tylko statusy gniazd i kandydaci).
