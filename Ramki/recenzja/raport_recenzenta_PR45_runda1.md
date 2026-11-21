# Raport recenzenta PR #45 (E3-P15) - runda 1

Data: 21.11.2026. Zakres: `git -C <PC-katalog>\qc diff main...origin/e3/p15`, HEAD `43a88cc`, `main` `bcd0678`; 9 plikow,
+508 / -4 (8 commitow). Zlecenie (miara): `zlecenia\p15.md`.

Metoda: najpierw wlasny przeglad diffu i kodu wokol zmiany (`ui/okno.py`, `ui/czesci.py` `ObszarPaneli`, `ui/mapa.py`,
`kontroler_api.py`, `baza.py`), potem wlasne proby na oknie offscreen (`AtrapaKontrolera`) w kopii `qc-wt\rec-p15` (galaz) i
w klonie glownym `<PC-katalog>\qc` (`main`, tylko uruchamianie, bez zapisu), testy paczki 5 x, 5 wstrzykniec, proba dwoch
kandydatow poprawki; raport wykonawcy przeczytany na koncu. Pliki robocze, logi i zrzuty: `<PC-katalog>\koordynator\robocze\rec-p15\`
(`proba.py` - tryby A, A2, B1, B2, B3, C; `proba_d.py`; `porownaj.py`; `wstrz.sh`). Kopia `rec-p15` po probach czysta
(`git status --short` pusty), klon glowny i `integ` nietkniete. Pelnego pytest nie uruchamialem. Najwyzej 2 procesy python naraz.

Oznaczenia: [W] = wlasna proba, liczba z mojego pomiaru; "wg wykonawcy" = niesprawdzone przeze mnie.

## 0. Werdykt i liczby

**Do scalenia po poprawkach.** B 0, P 2, D 4.

Cel glowny dla komunikatow z tla jest osiagniety: 1064 klikniec w stare srodki gniazd, 0 otwarc innego gniazda, 0 polecen;
zwykly wieczor bez komunikatow ogolnych: wlaczen ochrony `main` 9, galaz 9; uklad ekranu identyczny co do piksela (16 z 16
zrzutow, 0 roznych pikseli). Do poprawy sa dwie rzeczy w tych samych 6 wierszach `ui/okno.py`: ochrona wlacza sie takze wtedy,
gdy mapa sie NIE ruszyla (P1), i nie wlacza sie, gdy komunikat przesuwajacy mape jest skutkiem polecenia technika (P2). Oba
zachowania wykonawca opisal w raporcie jako "przyjete domyslnie" (sekcja 10), bez liczb i bez testu. Jedna poprawka zamyka obie -
kandydat sprawdzony w mojej kopii (sekcja 2, proby 13-14).

Nie nadaje wagi B: zadna decyzja nie zostala zapisana na innej pracy niz kliknieta (0 polecen w 1064 kliknieciach), mapa nie
zostaje zablokowana na stale (koniec ochrony 816-828 ms po ostatniej zmianie), zwykla praca bez komunikatow nie traci klikniec
(9 = 9, 0 zjedzonych z 30). P1 lezy na granicy miary koordynatora "ochrona wlaczana bez zmiany geometrii": dzieje sie tylko przy
zdarzeniu komunikatu (dojscie / zmiana wysokosci / znikniecie), nie przy odswiezaniu stalego komunikatu (0 wlaczen), strata to
najwyzej 800 ms widocznego przygaszenia na zdarzenie - stad P, nie B.

## 1. Uwagi

| Nr | Waga | Plik:linia | Scenariusz -> co sie dzieje | Propozycja |
|---|---|---|---|---|
| P1 | P | `stanowisko/ui/okno.py:329-334` (+ `:852`, `:866`) | Okno 1600 x 900, 1536 x 864 albo 1280 x 720; technik oglada plytke, ktora ma wlasny komunikat (np. "Praca niesprawdzona") albo nad mapa jest juz inny panel. W tle dochodzi / zmienia wysokosc / znika kolejny komunikat. Obszar `uwagi` jest wtedy ograniczony i przewijany - mapa NIE zmienia miejsca ani rozmiaru (y 343 -> 343, wys. 476 -> 476), a ochrona i tak sie wlacza: mapa przygasa na 800 ms i pomija prawowite klikniecia gniazd, Enter, U / O / C. [W] proba A: ochrona wlaczona w 56 z 56 zdarzen z tla, mapa ruszyla sie w 16 - **40 wlaczen bez zmiany geometrii** (po 12 w trzech mniejszych oknach, 4 przy 1920 x 1080: zmiana dlugosci tekstu przy 3 panelach). Na `main` w tych zdarzeniach ochrony nie ma i nie jest potrzebna (mapa stoi). Przyczyna: warunek porownuje `sizeHint()` obszarow paneli (`_wys_paneli`), a nie to, co technik ma pod kursorem. Zaden test tego nie pilnuje (wstrzykniecie W2 "ochrona zawsze" wykrywa tylko test zmiany samego tekstu). | Warunek od prostokata mapy: przed `self._odswiez()` zapamietac `QRect(self.mapa.mapTo(self, QPoint(0, 0)), self.mapa.size())`, po nim `self._calosc.activate()` (uklad policzony od razu, w tym samym wywolaniu) i start ochrony tylko, gdy prostokat jest inny; `_wys_paneli` i wiersze 852 / 866 staja sie zbedne. Gotowy diff: `robocze\rec-p15\kandydat_poprawki.diff` (5 wierszy +, 3 -). [W] na kandydacie: ochrona bez ruchu mapy 0 z 40, ochrona przy ruchu 16 z 16, inne gniazdo 0 z 1064, `test_p15_ekran.py` 7 passed, zwykly wieczor 9 wlaczen. Test do dopisania: 1536 x 864, plytka z wlasnym komunikatem + 1 komunikat ogolny, dochodzi drugi -> prostokat mapy bez zmian, ochrona nieaktywna, klik w srodek gniazda 9 otwiera gniazdo 9. |
| P2 | P | `stanowisko/ui/okno.py:332` (`not self._w_poleceniu`) | Technik klika "Ukruszona" (prawa kolumna), a zapis samoczynny listy sie nie udaje (np. plik listy otwarty w Excelu, dysk): w odpowiedzi na JEGO polecenie dochodzi komunikat ogolny `lista_nie_zapisana`, mapa zjezdza o 93-117 px, ochrona nieaktywna. Nastepny ruch technika to klik kolejnego gniazda - trafia w inne. [W] proba B3D, klik w stare srodki 19 gniazd zaraz po decyzji: inne gniazdo otwarte w 0 / 4 / 7 / 5 z 19 (1920 x 1080 / 1600 x 900 / 1536 x 864 / 1280 x 720) = **16 z 76**, tak samo na `main` (16 z 76). To ta sama klasa bledu, dla ktorej paczka powstala; zlecenie mowi o "DOWOLNYM komunikacie ogolnym" (dojscie), a kryterium 1 o 0 otwarc innego gniazda. Dotyczy kazdej odmowy, ktora stawia panel nad mapa w trakcie polecenia. Wykonawca: "przyjete domyslnie ... jak w A-P2" - ale A-P2 zwalnia z ochrony zmiane ZAWARTOSCI mapy po wlasnej decyzji (geometria stoi), nie skok mapy. | W trakcie polecenia wlaczac ochrone tylko wtedy, gdy panele nad mapa UROSLY (kolumna mapy zjechala w dol: `self.kolumna.y()` po `activate()` wieksze niz przed); komunikat zamkniety przez technika (kolumna idzie w gore) i decyzja bez komunikatu zostaja bez przygaszenia. Gotowy diff obu poprawek razem: `robocze\rec-p15\kandydat_poprawki_p1_p2.diff` (6 wierszy +, 3 -). [W] na kandydacie: B3D inne gniazdo 0 z 76 (ochrona aktywna 4 z 4), zwykly wieczor 9 wlaczen i 30 z 30 decyzji, wlasne zamkniecie komunikatu / grupy 0 wlaczen, proba A jak w P1, `test_p15_ekran.py` 7 passed, `test_p14_ekran.py` 33 passed, `test_ui_wieczor.py` 89 passed. Test do dopisania: zepsuty `zapisz_do_dofrezowania`, klik "Ukruszona" -> ochrona aktywna, 0 z 19 klikniec w stare srodki otwiera inne gniazdo. Gdyby wlasciciel wolal zostawic to poza paczka: minimum to wpis w sekcji "czego nie zrobiono" z liczba 16 z 76 i osobne zadanie. |
| D1 | D | `stanowisko/ui/okno.py:182` (kafelki), panele `uwagi` / naglowek mapy | Ograniczenie zgloszone przez wykonawce ("nie mierzono") - zmierzone: z 860 starych miejsc przyciskow / kafelkow po zdarzeniu z tla 144 zmienia miejsce, w 18 lezy INNY element klikalny: 10 x kafelek -> inny kafelek plytki, 4 x "Zmien numer" -> "Zamknij" komunikatu (komunikat zamkniety bez przeczytania), 4 x odwrotnie; w probie z pytaniem o numer plytki 4 x kafelek -> "Ponow zapis". Skutek trafienia w inny kafelek: pokazana inna plytka (naglowek ja nazywa, mapa przygasa przez A-P2, zadna decyzja sie nie zapisuje). Przyciski decyzji i lista (prawa kolumna): 0 z 6 zmienia miejsce, przy otwartej pracy decyzja kliknieta mysza w czasie ochrony idzie do pracy z widoku. Tak samo na `main`. Oceniam jako D (nie P): brak zapisu na innej pracy, skutek widoczny i odwracalny. | Bez poprawki w tej paczce; do decyzji wlasciciela p. 2. |
| D2 | D | `stanowisko/ui/okno.py:52` (`OCHRONA_MS`) | Granica ochrony [W]: klik w stary srodek 700-761 ms po komunikacie - pominiety 20 z 20; 851-916 ms po komunikacie - przyjety: przy 1536 x 864 inne gniazdo otwarte w 2 z 5 (2 x 5 prob), przy 1280 x 720 w 0 z 5. To cecha wariantu "ochrona" (ta sama co w A-P2), nie blad. | Do decyzji wlasciciela p. 1. |
| D3 | D | `stanowisko/ui/okno.py:333` | Seria zmian wysokosci paneli co 300 ms (10 zmian) trzyma mape przygaszona bez przerwy 3633-3685 ms; konczy sie 816-828 ms po ostatniej. Zrodla takiej serii w programie nie znalazlem (odswiezanie "plik zajety od n s" nie zmienia wysokosci - 0 wlaczen), wiec bez skutku w praktyce. | Nic; po poprawce P1 dotyczy tylko zmian, ktore naprawde ruszaja mape. |
| D4 | D | `stanowisko/kontroler_api.py:2992` | Udany zapis samoczynny pliku listy BIEZACEJ usuwa `odmowa:lista_nie_zapisana` takze wtedy, gdy odmowa dotyczyla zapisu listy innej doby (inny plik, `zapisz_liste(doba)`) - ten sam identyfikator. Ekran nie wola `zapisz_liste` z doba (`ui/okno.py:564`, `ui/czesci.py:809` - bez argumentu), wiec technik tego nie zobaczy. | Nic teraz; gdy ekran dostanie zapis listy wybranej doby - osobny identyfikator odmowy. |

## 2. Wlasne proby

Wszystkie w `<PC-katalog>\koordynator\robocze\rec-p15\`; uruchamiane przez `narz\py.cmd` z katalogu `Ramki\stanowisko` danego drzewa.

| Nr | Polecenie / skrypt | Wynik |
|---|---|---|
| 1 | `proba.py <rec-p15> A` (log `a_galaz.log`): 4 rozmiary x praca zamknieta / otwarta x 7 zdarzen z tla (dojscie konfliktu projektu, drugi, trzeci, dluzszy tekst, krotszy tekst, znikniecie jednego, znikniecie wszystkich); po kazdym 19 prawdziwych klikniec w stare srodki gniazd w czasie ochrony (najdluzej 157 ms od zdarzenia) | 56 zdarzen, 1064 klikniec: inne gniazdo 0, polecen do kontrolera 0, innych skutkow (inna plytka, zamkniety komunikat) 0. Mapa ruszyla sie w 16 zdarzeniach (19 z 19 gniazd, przesuniecia 52-99 px), ochrona aktywna w 16 z 16; ochrona aktywna takze w 40 zdarzeniach BEZ ruchu mapy (P1). Stare miejsca 860 przyciskow / kafelkow: 144 ruszone, 18 z innym elementem klikalnym (D1) |
| 2 | `proba.py <rec-p15> A2` (log `A2_galaz.log`), 1536 x 864 i 1280 x 720, praca otwarta, dochodzi komunikat | Przyciski decyzji 0 z 6 zmienia miejsce (x 2 rozmiary). Klawisze U, O, C, Enter (2 rodzaje) w czasie ochrony: 0 polecen. Dwuklik w 3 stare srodki: gniazdo bez zmian, 0 polecen. Klik mysza "Ukruszona" w czasie ochrony: 1 polecenie na pracy z widoku (ta sama praca). Granica: 700 / 750 ms pominiete 20 z 20; 850 / 900 ms przyjete, inne gniazdo 4 z 10 przy 1536 x 864, 0 z 10 przy 1280 x 720 |
| 3 | `proba.py A2`, czesc "A2Q": plytka bez numeru (pytanie z przyciskami) + blad zapisu / silnik nie startuje / plik zajety, 4 rozmiary | 12 krokow, 172 stare miejsca elementow klikalnych: inny element w 4 (kafelek plytki -> "Ponow zapis"); przyciski pytania o numer nie trafiaja w inny przycisk (0) |
| 4 | `proba.py <drzewo> B1` na `main` (`b1_main.log`) i galezi (`B1_galaz.log`): 1600 x 900, 10 plytek (9 dochodzi w trakcie), po 3 odswiezenia z tla na plytke, 30 decyzji kliknieciami, "Pokaz nowy wynik", 3 x "Zapisz liste" | `main`: wlaczen ochrony 9 (okresow 9), decyzji zapisanych 30, klikniec gniazd zjedzonych 0. Galaz: 9 (9), 30, 0. Roznica 0 |
| 5 | `proba.py <drzewo> B2` (`B2_main.log`, `B2_galaz.log`): komunikat staly kazdego z 56 rodzajow `statusy.KOMUNIKATY` x 2 rozmiary; 10 odswiezen bez zmiany, 5 x ten sam tekst od nowa, 5 x inna liczba w tekscie | Galaz: 112 przypadkow, wlaczen ochrony 0 / 0 / 0 przy 0 ruchach mapy. `main`: 0 / 0 / 0. Dodatkowo 8 komunikatow naraz (obszary przewijane), 20 odswiezen "plik zajety od n s" x 4 rozmiary: 0 wlaczen, 0 ruchow (obie wersje) |
| 6 | `proba.py <drzewo> B3` (`B3_main.log`, `B3_galaz.log`) | Galaz: seria 10 zmian co 300 ms - ochrona ciagla 3633 / 3685 ms (2 przebiegi), koniec 828 / 822 ms po ostatniej, potem mapa nieprzygaszona i klik gniazda 9 otwiera 9. Technik zamyka pojedynczy komunikat: 0 wlaczen; zamyka grupe 2 jednakowych (mapa y 319 -> 244): 0 wlaczen (`main` tak samo). Okno zamkniete w czasie ochrony: zegar nieaktywny; komunikat po zamknieciu okna: bez wyjatku, zegar nieaktywny |
| 7 | `proba.py B3`, czesc "B3D": decyzja technika przy zepsutym zapisie listy, 4 rozmiary, `main` i galaz | Obie wersje: mapa y 244 -> 340 / 244 -> 340 / 244 -> 361 / 179 -> 272, ochrona 0 z 4, inne gniazdo 0 / 4 / 7 / 5 z 19 (P2) |
| 8 | `proba.py <drzewo> C` + `porownaj.py`: zrzuty okna bez komunikatu, z otwarta praca, z 1 komunikatem, z 2 komunikatami x 4 rozmiary, `main` wobec galezi | 16 z 16 par: 0 roznych pikseli. Galaz dodatkowo 4 zrzuty mapy przygaszonej. Obejrzane narzedziem Read 4: `3_przygaszona_1536x864` (mapa wyraznie przygaszona, reszta ekranu bez zmian, oba panele czytelne), `5_z_dwoma_1280x720` (drugi panel uwag przewijany - stan z `main`), `4_z_komunikatem_1920x1080`, `1_bez_komunikatu_1600x900` |
| 9 | `proba_d.py <rec-p15>` (`d_galaz.log`) | `lista_nie_zapisana`: po nieudanym recznym zapisie 2 komunikaty; po decyzji przy NADAL zepsutym zapisie zostaja oba; po drugim nieudanym recznym zostaja; po udanym samoczynnym 0 (plik 3 wiersze, `lista_zapisana` ustawione); po kolejnym nieudanym recznym wracaja, po udanym recznym 0. `Baza.kolumny` przy bazie zajetej: `BladBazy` "zajeta" 11 z 11 tabel, `wstaw` przy pustej pamieci kolumn `BladBazy`; po zwolnieniu 11 z 11 odczytow; w transakcji odczyt dziala; `WERSJA_SCHEMATU` 1, `MIGRACJE` 1 |
| 10 | Testy paczki 5 x, dwa procesy python rownolegle (`testy5.log`) | `test_p15_ekran.py`: 5 z 5 przebiegow zielonych (7 passed, 5,7-6,2 s); `test_p15_drobne.py`: 5 z 5 (4 passed, 1,4-1,5 s) |
| 11 | Pliki testow dotknietych modulow, po jednym (drugi proces python w tle) | `test_ui_wieczor.py` 89 passed (91 s), `test_p14_ekran.py` 33 passed (31 s), `test_ui_rano.py` 32 passed (38 s), `test_kontroler_api.py` 92 passed (35 s), `test_baza.py` 70 passed (1,4 s) |
| 12 | `wstrz.sh` (`wstrz.log`): 5 wstrzykniec w kopii, po kazdym oba pliki testow paczki, plik przywracany | 5 z 5 wykrytych: W1 ochrona nie wlacza sie przy zmaleniu / zniknieciu paneli - 4 failed; W2 ochrona przy kazdym stanie z tla - 1 failed; W3 czas ochrony 0 ms - 6 failed; W4 odmowa `lista_nie_zapisana` usuwana takze po nieudanym zapisie - 2 failed; W5 `Baza.kolumny` bez opakowania - 1 failed. Dodatkowo cofniecie wiersza punktu 2: `test_p15_drobne.py` 1 failed, 3 passed |
| 13 | Kandydat poprawki P1 (`kandydat_poprawki.diff`) w kopii: `proba.py A`, `B1`, `test_p15_ekran.py` | Ochrona bez ruchu mapy 0 (bylo 40), przy ruchu 16 z 16, inne gniazdo 0 z 1064; zwykly wieczor 9 wlaczen; 7 passed |
| 14 | Kandydat P1 + P2 (`kandydat_poprawki_p1_p2.diff`, log `kandydat2.log`): `proba.py B3`, `B1`, `A`, 3 pliki testow | B3D inne gniazdo 0 z 76, ochrona 4 z 4; wlasne zamkniecie komunikatu i grupy 0 wlaczen; zwykly wieczor 9 wlaczen, 30 decyzji, 0 zjedzonych; proba A: 0 / 16 z 16 / 0 z 1064; `test_p15_ekran.py` 7 passed, `test_p14_ekran.py` 33 passed, `test_ui_wieczor.py` 89 passed. Kopia przywrocona |
| 15 | `test_instrukcje.py` na `qc-wt\integ` (`f5c3e01` = `main` bcd0678 + p15 43a88cc) | 36 passed (19 s) |

Nie zmierzono: prawdziwy ekran z mysza i prawdziwy kontroler `Aplikacja` (wszystko na oknie offscreen i atrapie); `test_p14_baza_zajeta.py`
i `test_aplikacja.py` (wg wykonawcy 27 passed i 28 passed + 1 skipped); kontrola `t13_higiena.py` (wg wykonawcy 0 naruszen; moja
kontrola bajtow nizej).

## 3. Kryteria zlecenia

| Nr | Kryterium | Ocena |
|---|---|---|
| 1 | Punkt 1, wariant "ochrona klikniec": 0 decyzji / otwarc innego gniazda w probie klikniec w stare punkty, 4 rozmiary; zrzuty obejrzane; komunikat widoczny; uklad bez komunikatow bez zmian | Dla komunikatow z tla **potwierdzone wlasna proba** (0 z 1064; uklad 0 roznych pikseli w 16 zrzutach). **Niespelnione** dla komunikatu, ktory dochodzi jako skutek polecenia technika (16 z 76, P2). Skutek uboczny: 40 z 56 wlaczen ochrony bez ruchu mapy (P1) |
| 2 | Punkty 2-4: test kazdego, bez poprawki pada | **Potwierdzone wlasna proba**: p. 2 - cofniecie wiersza: 1 failed; p. 3 - W5: 1 failed; p. 4 - przeglad testu (czyta bajty pliku) + `kandydaci.py` 0 bajtow spoza ASCII |
| 3 | Testy dotknietych modulow po jednym pliku | **Potwierdzone wlasna proba** dla 5 plikow + 2 nowych (sekcja 2, proby 10-11); 2 pliki wg wykonawcy, niesprawdzone |
| 4 | Pelny pytest 0 failed | **Potwierdzone przegladem** logu: `robocze\p15\pytest_e2240d1.log` konczy sie "2167 passed, 9 skipped, 1 warning in 1544.53s", `pytest_e2240d1.kod`: `KOD_WYJSCIA=0`, `ciezkie.log`: START 00:09:19, KONIEC 00:35:08 kod 0; `git diff --stat e2240d1 43a88cc`: 1 plik (raport) |
| 5 | Raport z lista "czego nie zrobiono" i wstrzyknieciami (min. 4) | **Potwierdzone przegladem**: sekcje 8 (9 wstrzykniec) i 11; ograniczenia P1 i P2 sa w sekcji 10 jako "przyjete domyslnie", bez liczb |

Punkty 2-4 kodu: `Baza.kolumny` idzie przez `_wykonaj` (opakowuje tylko blad "baza zajeta", inne bledy SQLite bez zmian); wywolania
`kolumny` sa dwa, oba w `baza.py` (`wstaw` :540, `zrzut` :566) - `wstaw` i tak rzucal `BladBazy` z `INSERT`, wiec wywolujacy sa na
to gotowi; miejsca lapiace sam `sqlite3.Error` (`samokontrola.py:752`, `:980`) uzywaja wlasnych polaczen, nie `Baza`. Ekran poranny:
`_odswiez` w trybie porannym wraca przed panelami, `_mapa_podpis` jest zerowany przy zmianie trybu - nowy warunek sie tam nie
wlacza (przeglad + `test_ui_rano.py` 32 passed).

## 4. Zakres plikow i zasady

- Zakres: 9 z 9 plikow na liscie zlecenia (`ui/okno.py`, `ui/kandydaci.py` - 1 wiersz komentarza, `kontroler_api.py` +1,
  `baza.py` - tylko `Baza.kolumny`, 2 nowe testy, 2 opisy modulow, raport). Zaden istniejacy test nie zmieniony.
- Zakaz napisow: `git diff main...origin/e3/p15 -- .../statusy.py ".../ui/napisy*.py"` pusty (0 wierszy); `test_instrukcje.py` na
  `main` + p15: 36 passed.
- Nietykalne, `instrukcje/**`, `Ramki/etap3/**`, `instalacja/**`, `README.md`: bez zmian. Schemat: `WERSJA_SCHEMATU`, `MIGRACJE`
  nie wystepuja w diffie.
- ASCII / LF: w dodanych wierszach calego diffu 0 znakow spoza ASCII; CR w 5 sprawdzonych plikach (2 testy, raport,
  `kandydaci.py`, `okno.py`): 0.
- Dane osobowe: raport, testy i commity - tylko dane sztuczne ("Technik A", numery plytek atrapy); nazw zlecen brak.
- Commity: 8, przedrostek "E3-P15", stopka `Co-Authored-By` w 8 z 8; duzych danych brak.

## 5. Do decyzji wlasciciela

1. Wariant "ochrona" zostawia skok mapy o 52-117 px przy kazdym komunikacie nad mapa i chroni tylko przez 800 ms (po 851-916 ms
   klik w stare miejsce trafil w inne gniazdo w 4 z 10 prob przy 1536 x 864). Czy po wydaniu przeniesc komunikaty tak, zeby
   mapa nie zmieniala miejsca (wariant "stala geometria" - przebudowa ukladu, nowe zrzuty instrukcji).
2. Kafelki plytek i przyciski paneli nad mapa przesuwaja sie razem z mapa i nie sa chronione (18 z 860 starych miejsc pod
   innym elementem; skutek: inna plytka na ekranie albo zamkniety nieprzeczytany komunikat, bez zapisu decyzji). Czy objac je
   ta sama ochrona, czy zostawic do wariantu "stala geometria".
3. P2: czy ochrona po komunikacie bedacym skutkiem polecenia technika ma wejsc do tej paczki (proponuje: tak, 1 warunek wiecej,
   sprawdzony), czy jako osobne zadanie po wydaniu.

WERDYKT: do scalenia po poprawkach (B 0, P 2, D 4)
