# Raport recenzenta PR #18 - runda 2 (przyrostowa)

Data: 2026-11-17. Recenzent: swieza subsesja (Opus 5.5), niezalezna od wykonawcy, koordynatora i recenzenta rundy 1.
Stan recenzowany: HEAD `cee3b83` galezi `e3/a4` (PR #18 "E3-A4: katalog, pule, wspolczynniki"). Zakres przyrostu:
`git diff a1a5c84..cee3b83 -- Ramki/stanowisko` (9 plikow) + raport rundy 1 (`57d0b90`) = 10 plikow, +1 084 / -230.
Kontekst: cala paczka `git diff origin/e3/fala2-baza...origin/e3/a4`.
Metoda: czytanie w calosci `nazwy.py`, `indeks.py`, `wspolczynniki.py`, `pula.py` (HEAD), diffu trzech plikow testow,
`pula.md`, raportu wykonawcy (sekcja "Runda 2"), raportu recenzenta rundy 1; w `session.py` miejsca czytajace
`zlecenia.kuweta` i `frezowania` (`_projekt`, `_frezowanie`, `_prace_skanow`, `do_dofrezowania`, `zapisz_do_dofrezowania`);
`baza.py` (schemat `frezowania`, unikaty).
Uruchomienia na PC (`<PC-katalog>\e3\r18b`, kod z `git archive HEAD`, konto `<konto-PC>`, 1 proces python naraz, wolny RAM
15 GB): (1) `testy\test_nazwy.py`, `test_indeks.py`, `test_pula.py` - **156 passed** w 15,2 s (62 / 22 / 72 - zgodne
z raportem wykonawcy); (2) `scen_r2.py` - scenariusze S1-S9 na bazach tymczasowych z fikcyjnymi nazwami (`licz_cechy=False`,
pliki-atrapy z `drzewo_syntetyczne`); (3) `scen_do.py` - dane osobowe na nowych drogach (fikcyjne nazwisko); (4) `proba_r2.py` -
nazwy folderow `Prace_test` przez `nazwy.rozbierz` (tylko odczyt, same liczniki i zanonimizowane ksztalty). Katalogi tymczasowe
scenariuszy usuniete (skrypt to sprawdza). Na MSI nie uruchamiano pytest ani obliczen. Pelnego pytest nie uruchamialem.

## 0. Werdykt

**do scalenia po poprawkach** - nowe uwagi: B 0 / P 2 / D 7.

Runda 2 zalatwia P1, P2 i scenariusze rundy 1 dla P3 i P4; testy odtwarzaja S1, S3, S4, S5, S7, S9, S11 rundy 1 i
porownuja wynik ze swieza baza (P2). Zadnego testu nie oslabiono (dwie zmiany asercji to zmiany wymagan - pkt 3). Schemat,
`baza.py`, `session.py` bez zmian; dane osobowe czyste takze na nowych drogach (uruchomione). Dwie nowe uwagi P dotycza
mechanizmow wprowadzonych w tej rundzie i obie daja zla pule bez wyraznego sygnalu:
- **P5** - wpis reczny "najnowszy w +-7 dni" i rozstrzyganie sprzecznosci na caly krazek: przy oznaczeniu krazka uzytym
  ponownie (zalozenie decyzji 8) nowszy wpis po cichu zmienia wspolczynnik prac z wczesniejszej doby okna, a sprzecznosci
  piatek / poniedzialek nie da sie rozstrzygnac poprawnie - kazdy wybor daje jednej dobie zly wspolczynnik.
- **P6** - regula "dzien obecny w pliku = plik zrodlem prawdy" (decyzja 6) przy pliku czyszczonym codziennie o innej porze
  niz polnoc (3 zmiany): wiersze 3. zmiany sprzed czyszczenia z ta sama data kalendarza staja sie nieaktualne i wypadaja z puli;
  licznika nie ma ani w puli, ani w kontrakcie ekranu.
Obie to kilkanascie-kilkadziesiat linii + test, bez zmiany schematu. Zadna nie dziala przy typowej pracy z niepowtarzalnymi
oznaczeniami krazkow i plikiem narastajacym - dlatego P, nie B (P6 rosnie do B, jesli wlasciciel potwierdzi czyszczenie pliku
co dzien o 06:00).

## 1. Uwagi rundy 1 -> stan

| Nr | Stan | Dowod (test / scenariusz) | Uwagi |
|---|---|---|---|
| P1 | zalatwiona | `test_nazwy::test_p1_*` (12 + 8 + 1), `test_indeks::test_p1_*`; czytanie `nazwy.py:42-45, 74-101` | Daty z zakresami, zeby FDI po numerze, kilku kandydatow = "?a,b" + licznik w indeksie i puli porannej. Wszystkie przyklady (a) i (b) rundy 1 w testach. `Prace_test`: 15 / 15 jednoznacznych (pkt 4). Kuweta niejednoznaczna nie blokuje dopasowania (wpis zostaje w obu pulach; `session._projekt` szuka po `sha16`) - S8. Rzadki przypadek "glosny" -> D19. |
| P2 | zalatwiona | `test_p2_powiazanie_przeliczane_...` (S1 rundy 1 + swieza baza) | `pula_wieczorna` laczy w pamieci od nowa (zapisane powiazanie bez pierwszenstwa), `odswiez` przelicza okno (`powiazanie.zmienione`), `wczytaj_do_bazy` przelicza wiersze pliku. |
| P3 | zalatwiona (nowe P6, D15) | `test_p3_...` (krazek, nazwa pliku, powrot wiersza, dzien spoza pliku), zmieniony test ponownego wczytania | Wiersz nieaktualny wraca tym samym `id` (bez podwojnego wpisu - test + czytanie klucza `istniejace`). Nowe skutki reguly dnia: P6 (czyszczenie pliku w srodku daty), D15 (literowka daty na dzien bez innych wierszy). |
| P4 | czesciowo (nowe P5) | `test_p4_*` (3), S5, S1, S2 | (a) dwie wartosci CSV jednej doby, (b) CSV kontra wpis reczny, (c) wpis starszy niz 7 dni - z licznikami `sprzeczne_wspolczynniki`, `krazki_sprzeczne`, polem `krazki().sprzeczne` / `brakuje`: zrobione. Mechanizm waznosci i rozstrzygania daje nowe P5; ponowne otwarcie po kazdym dopisanym wierszu - D16. |
| D1 | zalatwiona | `test_decyzja7_...`, S9 | Decyzja 7. |
| D2 | zalatwiona (nowe D17) | `test_d2_*` (2), S6, S7 | Pusty katalog = nic nie oznaczone + ostrzezenie; stary folder wraca z tymi samymi `id` zlecenia i projektu (S7). Prawdziwe usuniecie nie jest blokowane na zawsze (najdalej do zestarzenia, S6) - skutki w D17. |
| D3 | zalatwiona | `test_d3_*` (2), `scen_do` (`stare_doindeksowane` = 1) | |
| D4 | zalatwiona | `test_d4_...`, `scen_do` (`po_samej_nazwie` = 1) | Folder zlecenia bez pliku nadal = brakujacy (nie zgaduje). |
| D5 | znana (opisana w `pula.md`) | - | |
| D6 | wymaganie dla A5 (opisane w `pula.md` pkt 3) | - | |
| D7 | czesciowo (nowe D14) | `test_d7_*` (2 + 4) | Srednik na koncu, pusta linia przed naglowkiem, data dalej niz 60 dni: zrobione. `17.11.26` / `2026/11/17` nadal odrzucane (glosno), zakres 1,0-1,6 ze stalych (POTRZEBUJE). Okno 60 dni w przeszlosc odrzuca caly plik narastajacy - D14. |
| D8 | zalatwiona | `test_d8_...` | |
| D9, D10, D11, D13 | znane (opisane w `pula.md`) | - | |
| D12 | zalatwiona | 41 nowych testow | Kryterium 6 nie rozszerzone o nowe drogi, ale nowe testy sprawdzaja wyniki, a `scen_do` - dziennik i kolumny (pkt 5). |

## 2. Decyzje robocze 1-8 -> wdrozenie

| Nr | Decyzja | Stan | Dowod |
|---|---|---|---|
| 1 | kuweta bez zer wiodacych | wdrozona poprawnie | `nazwy.KUWETA_BEZ_ZER`, `postac_numeru`; "0412 412" = jeden kandydat (test); `#0123` bez zmian (D10 znane) |
| 2 | STL w podfolderach pomijane, liczone | wdrozona poprawnie | `indeks._wpisy_folderu`, `pominiete_podfoldery` liczone przy kazdym przebiegu dla folderow biezacych; w kontrakcie ekranu (pula.md pkt 1); `Prace_test`: 0 |
| 3 | swieta jak dni robocze | wdrozona poprawnie | `DNI_WOLNE` puste, argument `wolne` w oknie wieczornym, puli porannej, `krazki`, `odswiez` (test z `wolne`); brak klucza ustawien (POTRZEBUJE) |
| 4 | Prywatne: 10 dni kalendarzowych | wdrozona poprawnie | `pula.py:250` (`od_prywatne` nie krotsze niz Cyrkon, nie dawniej niz limit); `test_decyzja4_...` |
| 5 | `operator` wymagany, w dzienniku | wdrozona poprawnie | brak argumentu = `TypeError`, pusty = odmowa, w `zdarzenia` (test + `scen_do`: typ `wspolczynnik_reczny`) |
| 6 | dla dob w biezacym CSV plik zrodlem prawdy | wdrozona zgodnie z trescia, z bledem skutku | `wspolczynniki.py:271, 301-304`; P6 (czyszczenie w srodku daty), D15 |
| 7 | okno wieczorne w dniach roboczych | wdrozona poprawnie | S9: pt 06:00 - nd 06:00 w sobote, pt - pon 06:00 w nd i pon 05:30, pt - wt 06:00 w pon 20:00, wt 08:00 bez piatku; sobota robocza: wiersze z soboty sa w puli soboty i poniedzialku (brak przelacznika "sobota robocza", ale skutkiem jest tylko szersze okno); okno ograniczone (najwyzej pt - wt) |
| 8 | wpis reczny wazny 7 dni; sprzecznosc = prace krazka bez wspolczynnika do rozstrzygniecia | wdrozona, z bledem mechanizmu | `wspolczynniki.py:386-391`, `pula.py:144-179`; P5 (S1, S2), D16 (S5) |

## 3. Testy - oslabienia, higiena

- Zmienione asercje rundy 1: (1) `test_wczytanie_csv_...` - bylo "9 wierszy `csv` po wczytaniu 3" (utrwalalo P3), jest
  `(wierszy, nieaktualne) == (3, 3)`, 6 aktualnych i dokladne `id` nieaktualnych (linie 5, 6, 10) - ostrzejsze; (2) "Testowski 12 zs
  4567": "12" -> "?12,4567" (P1b); (3) `wczytaj_csv(..., dzis=TERAZ.date())` (bez tego wynik zalezalby od daty uruchomienia) i
  `operator=` przy wpisach recznych. Zadnego testu nie usunieto (brak linii `-def` w diffie). Oslabien nie znalazlem.
- Testy czerwone przed poprawka: raport podaje 55 failed + 10 errors na `0338e3a` - nie odtwarzalem (pkt 6).
- Higiena: 10 plikow z listy (9 paczki + raport rundy 1), 0 plikow spoza `Ramki/stanowisko` i `Ramki/recenzja`;
  `baza.py`, `session.py`, ustawienia bez zmian; ASCII (0 znakow spoza ASCII) i LF (`git ls-files --eol`) w kazdym zmienionym pliku.

## 4. Nowe uwagi

Sciezki wzgledem `Ramki/stanowisko/`. S1-S9 = `scen_r2.py`, uruchomione na PC.

| Nr | Waga | Plik:linia | Scenariusz (wejscie -> zly wynik) | Sprawdzone | Oczekiwane |
|---|---|---|---|---|---|
| P5 | P | `stanowisko/wspolczynniki.py:386-391` (`reczny_dla`: najnowszy wpis z data odlegla o <= 7 dni w OBIE strony); `stanowisko/pula.py:153-164, 169-172` (`_ocen`: sprzecznosc wykrywana w grupie krazek + data, ale wylacza caly krazek; rozstrzygniecie daje jedna wartosc wszystkim grupom w konflikcie); `wspolczynniki.py:431-437` | Zalozenie decyzji 8: oznaczenia krazkow moga sie powtarzac. **S1 (po cichu):** pt 20.11 krazek K-1, wiersze CSV bez wartosci, wpis reczny 1,25. Pon 23.11 nowy krazek o tym samym oznaczeniu: wpis 1,30 -> odmowa "krazek K-1 ma juz wspolczynnik 1,2500 (wpis z 2026-11-20) - potwierdz zmiane"; operator potwierdza (`zmien=True`), bo to nowy krazek. Pula pon 20:00 (decyzja 7 - obejmuje piatek): praca z piatku dostaje **1,30** (frezowana krazkiem 1,25), `sprzeczne` = 0, `brakuje` = False - bez zadnego sygnalu. Odwrotnie: bez nowego wpisu prace nowego krazka z poniedzialku po cichu dostaja 1,25 z piatku (granica 7 dni - do wiedzy wlasciciela). **S2 (nie do rozstrzygniecia):** pt K-1 w CSV 1,2210; pon ten sam znak, wiersz bez wartosci + wpis reczny 1,25 -> K-1 sprzeczny, obie prace poza pula. Wpisanie 1,2500 do CSV dla poniedzialku NIE pomaga (grupa piatkowa nadal porownywana z wpisem z poniedzialku). Rozstrzygniecie 1,25 (`zmien=True`) -> praca z piatku dostaje 1,25 (CSV mowi 1,2210, zrodlo "reczny"); rozstrzygniecie 1,2210 -> praca z poniedzialku dostaje 1,2210. Kazdy wybor daje jednej dobie zla skale; okno wpisu pokazuje tylko `wspolczynniki_csv` i `wspolczynnik_reczny` i prosi o wybor jednej wartosci. | Uruchomione (S1, S2 w obu wariantach rozstrzygniecia) + czytanie. | Wpis reczny obowiazuje od swojej doby (z tolerancja jednej doby wstecz - "wpis wieczorem dzien po frezowaniu"), a pozniejszy wpis nie zastepuje wczesniejszego dla dob, ktore tamten juz pokrywal; wpis pozniejszy dla dob wczesniejszych tylko, gdy wczesniejszego nie ma i tylko dla wierszy bez wartosci w CSV. Sprzecznosc i rozstrzygniecie w grupie krazek + data (wylaczyc prace tej grupy, nie calego krazka; wpis rozstrzygajacy z data grupy). Testy na S1 i S2. Pytanie 8 rundy 1 (czy oznaczenia sie powtarzaja) nadal do wlasciciela - przy oznaczeniach niepowtarzalnych P5 nie wystepuje. |
| P6 | P | `stanowisko/wspolczynniki.py:271` (`dni` = daty obecne w pliku), `wspolczynniki.py:301-304` (oznaczanie `csv_nieaktualny`); `stanowisko/pula.py:202-204` (brak licznika w puli); `opisy_modulow/pula.md:22-23` (kontrakt ekranu bez `csv.nieaktualne`) | Data w CSV = data kalendarza (konwencja modulu i testow: "data kalendarza 3. zmiany"), zaklad pracuje na 3 zmiany, a `pula.md` przewiduje "plik czyszczony co dzien". Plik czyszczony o 06:00: wiersz 3. zmiany z 18.11 02:00 (wczytany o 05:00, w puli o 05:30) -> po czyszczeniu 1. zmiana wpisuje wiersz z 18.11 -> przy wczytaniu o 07:00 dzien 18.11 "jest w pliku", wiec wiersz nocny = `csv_nieaktualny` (`nieaktualne` = 1). Pula 18.11 20:00 nie ma tej pracy - przy skanie praca "bez projektu". Liczniki `pula_wieczorna` nie maja `nieaktualne`, kontrakt ekranu (pula.md pkt 1-2) nie kaze pokazywac `csv.nieaktualne` - dla technika cicho. Kazde czyszczenie pliku o innej porze niz polnoc gubi w ten sposob wiersze z dnia czyszczenia sprzed czyszczenia. | Uruchomione (S3) + czytanie. | Odroznic czyszczenie od poprawki, np.: wiersz uznawac za nieaktualny tylko, gdy w pliku zostaly wiersze tej samej daty wczytane WCZESNIEJ niz on (poprawka zostawia starsze wiersze dnia, czyszczenie - nie); albo decyzja wlasciciela o porze czyszczenia (tylko o polnocy / tylko wiersze sprzed wczoraj) zapisana w instrukcji CSV. W kazdym razie licznik `nieaktualne` w `pula_wieczorna().liczniki` i w kontrakcie ekranu. Test na S3. |
| D14 | D | `stanowisko/wspolczynniki.py:226-228` | Plik CSV narastajacy (nie czyszczony - drugi przewidziany sposob; ponowne wczytanie bez duplikatow) po 60 dniach od pierwszego wiersza: kazdy stary wiersz = blad linii, **caly plik odrzucony**, nowe wiersze nie wchodza do bazy (S4: "nic nie wczytano - linia 2: data dalej niz 60 dni od dzisiaj - sprawdz rok i miesiac", 0 wierszy). Glosno (`csv_blad`), ale komunikat wskazuje literowke, a nie stary wiersz, i blokuje caly dzien. | Uruchomione (S4). | Data w przeszlosci dalej niz okno: pominac z licznikiem "poza oknem" (nie blad); data w przyszlosci: blad jak dzis. Albo w instrukcji: plik trzeba czyscic co najmniej raz na 60 dni. |
| D15 | D | `stanowisko/wspolczynniki.py:301-302` | Literowka daty na dzien, ktorego plik poza nia nie zawiera (19.11 zamiast 18.11), poprawiona w pliku: dzien 19.11 znika z pliku, wiec stary wiersz zostaje `csv` -> w puli dwa wpisy tej samej pracy (18.11 i 19.11, ten sam krazek i wspolczynnik). Skala dobra; podwojny kandydat (D6) i wiersz "frezowania" z data, ktorej nie bylo. | Uruchomione (S3, czesc 2). | Znana granica reguly dnia do opisu w `pula.md`; ewentualnie ten sam plik + krazek z innym dniem w biezacym pliku traktowac jak poprawke. |
| D16 | D | `stanowisko/pula.py:161` (rozstrzygniecie porownywane z najnowszym `wczytano` wszystkich wierszy grupy), `pula.py:401-402` | Rozstrzygniecie (`zmien=True`, 1,2210) przy literowce zostawionej w CSV, potem dopisany wiersz tego krazka i doby z TA SAMA wartoscia 1,2210 -> sprzecznosc wraca, wszystkie 3 prace poza pula, trwale przy kolejnych wczytaniach (S5). Plik wypelniany w ciagu dnia = kazdy nowy wiersz krazka wymaga nowego rozstrzygniecia, dopoki ktos nie poprawi CSV. Zgodne z opisem ("dopisany po rozstrzygnieciu = nowa sprzecznosc"), ale uciazliwe. Przy tym `odswiez` zapisuje zdarzenie `sprzeczne_wspolczynniki` przy kazdym odswiezeniu, poki sprzecznosc trwa (odswiezenie po kazdym nowym pliku). Rzadkie: przy cofnieciu zegara (zmiana czasu jesienia) rozstrzygniecie z powtorzonej godziny ma `wczytano` wczesniejsze niz wiersze CSV - nie rozstrzyga do konca tej godziny. | Uruchomione (S5); zmiana czasu - czytane. | Nowy wiersz z wartoscia rowna rozstrzygnieciu nie otwiera sprzecznosci (porownywac z rozstrzygnieciem tylko wiersze o innej wartosci); zdarzenie tylko przy zmianie listy krazkow. |
| D17 | D | `stanowisko/indeks.py:233-239` (prog), `stanowisko/pula.py:251-253` (pula poranna), `pula.py:310-325` (`sciezki_plikow`) | Prawdziwe usuniecie wiecej niz polowy biezacych folderow zrodla (male "Prywatne": 2 z 3; tydzien gotowych prac wyniesiony z "Cyrkon"): usuniecia wstrzymane do zestarzenia folderow (S6: 17.11 i 22.11 wstrzymane z ostrzezeniem "sprawdz synchronizacje OneDrive", 26.11 oznaczone). W tym czasie pula poranna ma 2 wpisy z plikami, ktorych nie ma (`sciezki` -> 2 sciezki bez pliku), a `IndeksPlikow` moze laczyc z nimi wiersze CSV. Nie na zawsze (archiwum starsze niz 10 dni idzie bez progu). | Uruchomione (S6). | Wymaganie dla A5: brak pliku pod sciezka z `sciezki()` = wpis pominiety z licznikiem, nie blad wczytania; w ostrzezeniu tez mozliwosc "prawdziwe usuniecie" (ewentualnie przycisk potwierdzenia w A3). |
| D18 | D | poza PR: `stanowisko/session.py:810-814, 958, 981`; `opisy_modulow/pula.md:26` | (a) `session` (A1) pokazuje `zlecenia.kuweta` doslownie: kuweta "?46,3263" trafia do `stan_wieczoru`, listy "do dofrezowania" i pliku `do_dofrezowania_biezaca.csv` (S8: `['?46,3263', '14', 'K-1']`). Widac, ze niepewna, ale kontrakt (pula.md pkt 5) opisuje pokazywanie tylko dla ekranu porannego (A6). (b) Krazek na liscie "do dofrezowania" pochodzi z `prace.frezowanie_id`: praca dopasowana przed poprawka CSV (K-1 -> K-2) nadal pokazuje K-1 z wiersza `csv_nieaktualny` (S8). `_frezowanie` (wybor wpisu po `projekt_id`) jest bezpieczne - nieaktualny ma `projekt_id` NULL. | Uruchomione (S8) + czytanie. | Do kontraktu A3 / A6: kuweta "?a,b" wszedzie jak na ekranie porannym ("46 albo 3263 - sprawdz folder"), takze w pliku listy; krazek z wiersza `csv_nieaktualny` pokazywac jako niepewny (albo wpis zastepujacy ten sam plik i date). |
| D19 | D | `stanowisko/nazwy.py:42-43` | Numer kuwety 1-31 albo 1900-2099 z zebami dopisanymi lacznikiem, gdy pierwszy zab to 11 lub 12 (most 11-21 jest czesty): "Nazwisko 12-11-21", "Nazwisko 2012_11_21" sa poprawnymi datami -> wyciete -> brak kuwety. Glosno (`bez_kuwety`), rzadko (kuweta 4-cyfrowa spoza 1900-2099 dziala: "3263-11-21" -> 3263). | Czytane. | Opisac jako granice albo nie uznawac za date lancucha, ktorego 2. i 3. liczba to zeby FDI, gdy 1. liczba nie jest rokiem w poblizu biezacego. |
| D20 | D | poza PR: `stanowisko/baza.py:125` (komentarz `zrodlo`), `opisy_modulow/baza.md` | Nowe wartosci `frezowania.zrodlo` (`csv_nieaktualny`, `reczny_potwierdzony`) sa opisane tylko w `pula.md`; komentarz schematu wymienia 4 stare. Kolejna paczka czytajaca `frezowania` (A6, A9: "ile frezowan", "wpis reczny" po `zrodlo = 'reczny'`) policzy wiersz nieaktualny albo pominie potwierdzony. Dzis wszystkie miejsca czytajace (pula, wspolczynniki, session) sa poprawne. | Czytane (grep po `frezowania` i `zrodlo`). | Dopisac do `baza.md` (sekcja typow / statusow) przy najblizszej zmianie dokumentu; reguly: aktualne = `zrodlo != csv_nieaktualny`, reczne = `ZRODLA_RECZNE`. |

## 5. Sprawdzone bez zastrzezen

- **Nowe oznaczenia w istniejacych kolumnach.** `csv_nieaktualny` + `projekt_id` NULL: poza pulami, `krazki`, powiazaniem
  (`powiaz_frezowania`), `pliki_frezowan` (D3) i wyborem wpisu w `session._frezowanie`; wraca tym samym `id` (test P3);
  podwojny wpis przez powrot niemozliwy - klucz `istniejace` obejmuje wiersze nieaktualne. `reczny_potwierdzony`: czytany przez
  `ZRODLA_RECZNE` we wszystkich zapytaniach o wpisy reczne. Kuweta "?a,b": nie blokuje pul (S8, test P1), nie zgadza sie
  z zadnym numerem; zapis Excela (A9) jeszcze nie istnieje.
- **Okno w dniach roboczych** (S9, czytanie `okno_wieczoru`, `poczatek_dni_roboczych`): granica 06:00 w poniedzialek,
  niedziela, sobota, argument `wolne` (skonczona petla - zbior dat skonczony), okno najwyzej pt - wt.
- **D2:** prog liczy tylko foldery biezace (archiwum miesiaca wyniesione naraz = oznaczone bez ostrzezenia - czytanie);
  wracajacy folder dostaje te same `id` zlecenia i projektu (S7); pliki znikajace w istniejacym folderze (OneDrive z pustymi
  folderami) wracaja z tym samym `id` projektu (czytanie `_folder`).
- **P1 na prawdziwych nazwach** (`proba_r2.py`, `Prace_test`, tylko odczyt): 15 folderow z STL, wszystkie na glebokosci 1,
  17 plikow, 0 STL w podfolderach; wynik rozbioru: 13 jednoznacznych 4-cyfrowych, 2 jednoznaczne 3-cyfrowe, 0 niejednoznacznych,
  0 bez kuwety, 0 prywatnych; 0 nazw ze wzorem "liczba.liczba" (data bez roku / godzina). Ksztalty (L = litery, N4 = 4 cyfry;
  ciag znakow nieliterowych z kopii PC - znieksztalcone litery z ogonkami - zastapiony jednym "~"): "L N4 L" (5), "L N4L" (2),
  "L N4 L L", "L~L N3 L", "L L. N4 L", "L N3 L", "L~L N4 L" (2), "~L N4 LN1", "~L~L N4 L"; razem 15. 17 / 17 plikow z numerem zeba. Zgodne z raportem wykonawcy.
- **Dane osobowe** (`scen_do.py`, fikcyjne nazwisko w 5 folderach i 4 wierszach CSV, takze sciezka MillBox z nazwiskiem;
  drogi: kuweta niejednoznaczna, D3, D4, sprzecznosc, wiersz nieaktualny, D2 wstrzymane z ostrzezeniem, wpis reczny z operatorem
  i odmowa): wyniki `odswiez` x2, pule, `krazki`, komunikat odmowy - 0 trafien nazwiska; baza - 0 trafien poza
  `KOLUMNY_Z_NAZWAMI`; dziennik `pula`: `indeks`, `sprzeczne_wspolczynniki`, `wspolczynnik_reczny`, `wspolczynniki_csv` - same
  liczby, id, krazki, operator. `ostrzezenia` = nazwa zrodla + liczby. Krazek to nadal dowolny tekst (D13 znane).
- **Liczby wykonawcy, ktore dalo sie sprawdzic:** 156 testow paczki (62 / 22 / 72) - 156 passed; `Prace_test` - jak wyzej.

## 6. Czego NIE sprawdzilem

- Pelnego pytest (836 / 8 / 0 wg wykonawcy) i stanu czerwonego na `0338e3a` (55 failed + 10 errors) - nie uruchamialem.
- Prawdziwego "Cyrkon" na OneDrive, prawdziwego pliku CSV z frezarki (czy jest czyszczony i kiedy - od tego zalezy waga P6),
  nazw z MillBox; czy oznaczenia krazkow sie powtarzaja (od tego zalezy P5).
- Cech i miniatur (scenariusze z `licz_cechy=False`); czasu indeksu (D11 nie mierzony ponownie).
- Zmiany czasu (tylko czytanie), dwoch polaczen naraz (watek roboczy + okno) przy rozstrzyganiu sprzecznosci.
- Konsumentow kontraktu: A3 (ekran), A5 (silnik), A6 (poranek), A9 (Excel) nie istnieja; `session` tylko w zakresie S8.
- Nazw folderow ze znakami niedozwolonymi w UTF-8 (jak w rundzie 1).
