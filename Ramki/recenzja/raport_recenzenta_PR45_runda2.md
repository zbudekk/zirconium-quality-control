# Raport recenzenta PR #45 (E3-P15) - runda 2 (recenzja przyrostowa)

Data: 21.11.2026. Zakres rundy: `git -C <PC-katalog>\qc diff 43a88cc..origin/e3/p15` (commity kodu / testow `b9964cb`, `47b94c4`,
`0bc605a`, `091e591`; potem 2 commity samego raportu), HEAD `d3b3ea7`, `main` `62ef6f5`. Calosc paczki
`git diff origin/main...origin/e3/p15`: 11 plikow, +846 / -7. Miara: `zlecenia\p15.md` + `zlecenia\p15-r2.md`.

Metoda: najpierw wlasny przeglad diffu rundy i kodu wokol zmiany (`ui/okno.py` `pokaz_stan` / `_polecenie` / `_odswiez`, uklad
strony wieczornej, `ui/czesci.py` `ObszarPaneli`, `aplikacja.py` `BlokadaStanowiska` i `main`), potem wlasne proby na oknie offscreen
(`AtrapaKontrolera`, 4 rozmiary okna) w kopii `qc-wt\rec-p15` (detached `d3b3ea7`) i w klonie glownym `<PC-katalog>\qc` (`main`
`62ef6f5`, tylko uruchamianie), testy paczki 5 x, wstrzykniecia, pomiar blokady interpreterem bazowym i interpreterem srodowiska
wersji (`t0\proba\Stanowisko\Polecenie.cmd`, wersja 0.3.1; kod programu i testow z kopii `rec-p15`); raport wykonawcy (sekcja 14)
przeczytany na koncu. Pliki robocze i logi: `<PC-katalog>\koordynator\robocze\rec-p15\runda2\` (`proba_r2.py` - tryby S, T, X;
`pomiar_b1.py`; `wstrz_r2.py`; `lancuch1-8.sh`; proby rundy 1 uzyte ponownie: `..\proba.py` tryby A, B1, B2, B3, C). Po probach
`git status --short` kopii `rec-p15` i klonu glownego pusty (`status_po.log`). Pelnego pytest nie uruchamialem. Najwyzej 2 procesy
python naraz (+ procesy potomne testow).

Oznaczenia: [W] = wlasna proba, liczba z mojego pomiaru; "wg wykonawcy" = niesprawdzone przeze mnie.

## 0. Werdykt i liczby

**Do scalenia.** B 0, P 0, D 6 (D1-D4 z rundy 1 odlozone - bez zmian wobec `main`; D5, D6 nowe, bez poprawki w tej paczce).

Obie uwagi P rundy 1 sa zamkniete wlasnym pomiarem: ochrona wlacza sie dokladnie wtedy, gdy mapa zmienia miejsce (falszywe
wlaczenia 0 z 40 w scenariuszu rundy 1 i 0 z 194 w szerszej probie; przy ruchu 16 z 16 i 54 z 54), a komunikat po poleceniu
technika jest chroniony (inne gniazdo 0 z 76; w szerszej probie 4 polecen 0 z 380, na `main` 51 z 380). Bledow wprowadzonych
runda 2 nie znalazlem: porownanie prostokata mapy jest liczone po ulozeniu ukladu w tym samym wywolaniu (ochrona aktywna od razu,
bez obiegu petli okna: 54 z 54), koszt `activate()` jest niemierzalny w sumie odswiezenia (8,29 ms wobec 8,41 ms na `main`),
zwykly wieczor 9 = 9 wlaczen i 0 zjedzonych klikniec, zrzuty 16 z 16 identyczne co do piksela. `test_b1` nie zostal oslabiony
(4 wstrzykniecia z blokada, ktora zostaje, wykryte obydwoma interpreterami).

## 1. Uwagi

### 1.1 Uwagi rundy 1

| Nr | Waga | Stan | Dowod |
|---|---|---|---|
| P1 | P | **zamknieta** | `stanowisko/ui/okno.py:331-339`: miara to prostokat mapy w oknie przed `_odswiez()` i po nim, po `self._calosc.activate()`; pole `_wys_paneli` usuniete (0 wystapien w kodzie). [W] proba A (ten sam scenariusz co w rundzie 1, 56 zdarzen z tla): mapa bez ruchu w 40 - ochrona **0 z 40** (runda 1: 40 z 40); mapa ruszona w 16 - ochrona **16 z 16**; klik w stare srodki: inne gniazdo **0 z 1064**, polecen 0, innych skutkow 0. [W] proba S (szersza, 248 zdarzen): falszywe 0 z 194, przy ruchu 54 z 54. [W] proba B2: komunikat staly odswiezany z tla, 112 przypadkow + 80 odswiezen przy 8 komunikatach: 0 wlaczen. Test `test_p15_r2_p1_ochrona_wlacza_sie_tylko_gdy_mapa_zmienia_miejsce` (4 rozmiary) pada po wstrzyknieciu W1 (4 failed) |
| P2 | P | **zamknieta** | `okno.py:337`: w trakcie polecenia ochrona, gdy kolumna mapy zjechala w dol (`po[1] > przed[1]`). [W] proba B3D (klik "Ukruszona" -> nieudany zapis listy -> `lista_nie_zapisana`): mapa y 244 -> 340 / 244 -> 340 / 244 -> 361 / 179 -> 272, ochrona **4 z 4**, inne gniazdo **0 z 76** (runda 1 i `main`: 16 z 76). [W] proba X (inne polecenia: reczny "Zapisz liste" nieudany przy pracy zamknietej i otwartej, "Skanuj" z nieudanym startem, decyzja bez wybranej osoby; 4 rozmiary): mapa zjechala w 16 przypadkach, ochrona **16 z 16**, inne gniazdo **0 z 380**; `main`: ochrona 0 z 16, inne gniazdo 51 z 380. Wlasne zamkniecie komunikatu przez technika (pojedynczy i grupa 2 jednakowych, mapa y 319 -> 244): **0 wlaczen**; zwykla decyzja: 0 wlaczen ponad `main` (9 = 9). Testy P2 padaja po W2 (4 failed) i W5 (2 failed) |
| D1 | D | otwarta, odlozona - bezpiecznie | Kafelki plytek i przyciski paneli nad mapa przesuwaja sie z mapa bez ochrony. [W] liczby jak w rundzie 1 i na `main` (860 starych miejsc: 144 ruszone, 18 z innym elementem klikalnym); bez zapisu decyzji na innej pracy. Do decyzji wlasciciela p. 2 |
| D2 | D | otwarta, odlozona - bezpiecznie | Granica 800 ms to cecha wariantu "ochrona" (ta sama stala `OCHRONA_MS` co w A-P2); runda 2 jej nie zmienia. Do decyzji wlasciciela p. 1 |
| D3 | D | otwarta, zawezona | Po P1 seria trzyma mape przygaszona tylko przy zmianach, ktore naprawde ruszaja mape. [W] seria 10 zmian co 300 ms: ochrona ciagla 3652 ms, koniec 813 ms po ostatniej, potem klik gniazda 9 otwiera 9 |
| D4 | D | otwarta, odlozona - bezpiecznie | `kontroler_api.py` bez zmian w rundzie 2; ekran nadal nie wola zapisu listy z doba |

### 1.2 Nowe uwagi rundy 2

| Nr | Waga | Plik:linia | Scenariusz -> co sie dzieje | Propozycja |
|---|---|---|---|---|
| D5 | D | `stanowisko/ui/okno.py:335` | Jeden `self._calosc.activate()` uklada strone wieczorna (panele, lista plytek, kolumna mapy), ale nie uklad WEWNATRZ kolumny mapy, gdy sama kolumna nie zmienia miejsca ani rozmiaru (np. naglowek plytki zawiniety do 2 wierszy, przycisk akcji plytki dochodzi z tla): taki ruch mapy jest ukladany w nastepnym obiegu petli i ochrony z P15 nie wlacza. Tak samo na `main`; poza celem paczki (komunikaty nad mapa); wykonawca opisal to w sekcji 14.2 jako ograniczenie. Przegladem nie znalazlem zdarzenia z tla, ktore zmienia naglowek pokazanej plytki bez zmiany stanu jej gniazd (ta wlacza ochrone A-P2). Nie zmierzono. W probie S (zdarzenia komunikatow) ruchu bez ochrony: 0 z 54 | Nic w tej paczce. Gdyby wlasciciel wybral wariant "stala geometria" (p. 5.1) - sprawa znika |
| D6 | D | `raporty/E3-A6_2026-11-18.md:94`, `:107` | Po usunieciu CR w wierszach zostaje znak sterujacy BEL (bajt 0x07): tekst czyta sie "e3" + BEL + "64" (dawna sciezka katalogu z ukosnikami wstecznymi). Zakres rundy to "tylko usuniecie CR" - wykonane doslownie ([W] 16 420 -> 16 419 B, poza CR plik identyczny). Wykonawca zglosil to w "POTRZEBUJE" | Koordynator: odtworzenie nazwy katalogu w 2 wierszach przy okazji (poza ta paczka) |

Bez uwag B i P - poprawek przed scaleniem nie ma.

## 2. Wlasne proby

Uruchamiane przez `narz\py.cmd` z katalogu `Ramki\stanowisko` danego drzewa (galaz = kopia `rec-p15` `d3b3ea7`; `main` = klon glowny
`62ef6f5`); interpreter srodowiska wersji przez `Polecenie.cmd` (kod z kopii `rec-p15`: `conftest.py` / skrypt wstawia ja na poczatek
`sys.path`, w logu `pomiar_b1_wersja.log` wypisane `kod programu: ...\rec-p15\...\aplikacja.py`).

| Nr | Polecenie / skrypt (log w `runda2\`) | Wynik |
|---|---|---|
| 1 | `proba.py <galaz> A` (`A_galaz.log`): 4 rozmiary x praca zamknieta / otwarta x 7 zdarzen z tla, po kazdym 19 klikniec w stare srodki | 56 zdarzen: bez ruchu mapy 40 - ochrona 0; z ruchem 16 - ochrona 16; 1064 klikniec: inne gniazdo 0, polecen 0, innych skutkow 0 |
| 2 | `proba.py <galaz> B3` (`B3_galaz.log`) | B3D: ochrona 4 z 4, inne gniazdo 0 z 76 (0 / 0 / 0 / 0 z 19). Technik zamyka pojedynczy komunikat: 0 wlaczen; grupe 2 jednakowych: 0 wlaczen. Seria 10 zmian co 300 ms: 3652 ms ciagle, koniec 813 ms po ostatniej. Okno zamkniete w czasie ochrony: zegar nieaktywny; komunikat po zamknieciu okna: bez wyjatku |
| 3 | `proba_r2.py <drzewo> X` (`X_main.log`, `X_galaz.log`): 5 polecen technika x 4 rozmiary, po kazdym 19 klikniec w stare srodki | Galaz: 20 przypadkow, mapa zjechala w 16, ochrona 16 z 16 (aktywna juz przy powrocie z klikniecia), inne gniazdo 0 z 380. `main`: ochrona 0 z 16, inne gniazdo 51 z 380. 4 przypadki "Skanuj przy niedostepnym skanerze" nie daly komunikatu (moja proba nie odtworzyla stanu) - mapa bez ruchu, 0 wlaczen |
| 4 | `proba_r2.py <galaz> S` (`S_galaz.log`): 31 zdarzen z tla (pasek bledow programu x 4, komunikat plytki pokazanej / innej, konflikt projektu, 6 komunikatow ogolnych dochodzi i znika, zmiany dlugosci tekstu, "plik zajety od n s", samo odswiezenie) x 4 rozmiary x praca zamknieta / otwarta; stan ZARAZ po zdarzeniu (bez obiegu petli okna) wobec stanu ustalonego po 60 ms | 248 zdarzen: ruch mapy (ustalony) 54 - ochrona aktywna od razu **54 z 54**, ruch bez ochrony 0; bez ruchu 194 - falszywe wlaczenia **0**. Uklad ustalal sie w wiecej niz jednym obiegu w 6 zdarzeniach (prostokat od razu inny niz ustalony) - we wszystkich 6 ochrona juz aktywna. Klik bez obiegu petli w 3 stare srodki: inne gniazdo 0 z 744; po ustaleniu: 0 z 4712 |
| 5 | `proba.py <drzewo> B1` (`B1_main.log`, `B1_galaz.log`): zwykly wieczor, 10 plytek, 30 decyzji, odswiezenia z tla, 3 x "Zapisz liste" | `main`: wlaczen ochrony 9 (okresow 9), decyzji 30, klikniec zjedzonych 0. Galaz: 9 (9), 30, 0 |
| 6 | `proba.py <galaz> B2` (`B2_galaz.log`): komunikat staly kazdego z 56 rodzajow x 2 rozmiary | 112 przypadkow: odswiezenie bez zmiany 0 wlaczen, ten sam tekst od nowa 0, inna liczba w tekscie 0 przy 0 ruchach mapy; 8 komunikatow naraz x 4 rozmiary, 20 odswiezen "plik zajety od n s": 0 wlaczen, 0 ruchow |
| 7 | `proba.py <drzewo> C` + `porownaj_r2.py` (`porownaj.log`; zrzuty `..\zrzuty\r2_main`, `r2_galaz`) | **16 z 16** par `main` / galaz: 0 roznych pikseli. Galaz dodatkowo 4 zrzuty mapy przygaszonej; obejrzany narzedziem Read `3_przygaszona_1280x720.png` (mapa przygaszona, oba panele i kolumna plytek czytelne) |
| 8 | `proba_r2.py <drzewo> T` (`T_main.log`, `T_main2.log`, `T_galaz.log`, `T_galaz2.log`): czas odswiezenia ekranu, mediana z 200, po 2 przebiegi, 1920 x 1080 i 1280 x 720 | Wywolanie + obieg petli okna, `main` / galaz: samo odswiezenie 1,24 / 1,24 ms; zmiana tekstu komunikatu 3,71 / 3,77 ms; komunikat dochodzi / znika 8,41 / 8,29 ms (1920 x 1080) i 7,93 / 7,75 ms (1280 x 720). Samo wywolanie rosnie (2,68 -> 3,84 ms), obieg petli maleje o tyle samo - uklad jest liczony raz, tylko wczesniej. Maksimum 13,1 / 13,5 ms |
| 9 | Testy petli okna z progiem 0,2 s, po 5 razy (`petla5.log`, `petla_f.log`, `petla_f_obc.log`) | `test_ui_wieczor.py -k test_6` (2 testy): 5 z 5; `test_ramka.py -k test_k4` (3 testy): 5 z 5; `test_aplikacja_rano.py` `test_k3_excel_pytaj...` 5 z 5, `test_k4_spacja...` 5 z 5; `test_aplikacja.py -k test_f_petla`: seria 1 (rownolegle z testami paczki) **4 z 5** - 1 nieudany w przebiegu 1; seria 2 (sam) 5 z 5; seria 3 (w tle `test_p15_ekran.py`) 6 z 6. `main`: 5 z 5 (1 zaliczony dopiero w 2. pomiarze: przerwa 229 ms, przestoj dysku 193 ms) i 6 z 6. Powodu nieudanego przebiegu nie zapisalem (tylko wiersz podsumowania). Ten test nie buduje okna (kontroler + `lacznik_qt`), a runda 2 zmienia tylko `ui/okno.py` - nie wiaze go ze zmiana paczki; to test czasowy spoza paczki czuly na obciazenie PC |
| 10 | `pomiar_b1.py` 10 x bazowym i 10 x interpreterem srodowiska wersji (`pomiar_b1_bazowy.log`, `pomiar_b1_wersja.log`) | Bazowy: blokada wolna przy pierwszej probie 10 z 10 (0,21-0,55 ms po `wait()`). Srodowisko wersji (`wersje\0.3.1\venv\Scripts\python.exe`): pierwsza proba nieudana 10 z 10, blokada wolna po **0,78-1,34 ms** (7-11 prob zajecia), zwolniona 10 z 10. Wiersz "SUMA ... > 0,3 ms" w logu bazowym to zly licznik mojego skryptu - miara jest pole "od razu" |
| 11 | `test_b1_blokada_znika_razem_z_procesem` po zmianie (`b1_test.log`) | Srodowisko wersji 3 z 3 passed, bazowy 3 z 3 passed (ok. 2 s) |
| 12 | Wstrzykniecia w test b1 (`wstrz_r2.py`, `wstrz.log`, `powod_B1a.log`, `powod_B1c.log`), kazde bazowym i srodowiskiem wersji | W3 limit = 0: srodowisko wersji 3 z 3 failed, bazowy passed (blokada wolna od razu - zgodne z pomiarem). B1a proces programu nie ginie (nikt go nie zabija, sam konczy po 12 s): failed / failed, "blokada nie zniknela w 2.0 s po koncu procesu programu". B1b inny proces trzyma blokade 8 s: failed / failed. B1c inny proces trzyma 3 s (znika po czasie dluzszym niz limit): failed / failed, ten sam komunikat. B1d inny proces trzyma 1 s (krocej niz limit): passed / passed |
| 13 | Wstrzykniecia w `ui/okno.py` (`wstrz.log`), po kazdym `test_p15_ekran.py`, plik przywracany | W1 ochrona od zmiany `sizeHint` paneli zamiast od ruchu mapy: 4 failed (test P1 x 4 rozmiary). W2 brak ochrony po poleceniu: 4 failed (test P2 x 4). W4 porownanie przed ulozeniem ukladu (bez `activate()`): 7 failed. W5 po poleceniu ochrona przy kazdym ruchu (takze wlasne zamkniecie): 2 failed. W6 `po = przed`: 14 failed. Wymagane 4 (W1, W2, W3, W4): **4 z 4**; wszystkich 10 z 10 (z B1a-B1c; B1d to proba kontrolna) |
| 14 | Testy paczki 5 x, drugi proces python w tle (`testy5.log`) | `test_p15_ekran.py`: 5 z 5 (16 passed, 19,3-27,9 s); `test_p15_drobne.py`: 5 z 5 (5 passed, 1,4-1,5 s) |
| 15 | Pliki testow dotknietych modulow po jednym (`moduly.log`) | `test_ui_wieczor.py` 89 passed (80 s); `test_p14_ekran.py` 33 passed (28 s); `test_ui_rano.py` 32 passed (36 s); `test_aplikacja.py` 28 passed, 1 skipped (58 s); `test_instrukcje.py` 36 passed (18 s) |
| 16 | Start interpretera srodowiska wersji (`start_wersja.log`, 3 pomiary: `Polecenie.cmd -c ...`, bez importow programu) | 135-171 ms od polecenia do konca procesu |

Nie zmierzono: prawdziwy ekran z mysza i prawdziwy kontroler `Aplikacja` (wszystko na oknie offscreen i atrapie); ruch mapy wewnatrz
kolumny mapy (D5); kontrola `t13_higiena.py` (wg wykonawcy 0 naruszen, niesprawdzone - moja kontrola bajtow w sekcji 4); 20 powtorek
`test_b1` (wg wykonawcy 20 z 20 w obu srodowiskach; moje 3 z 3 + pomiar 10 x). Potkniecie wlasne: pierwsza seria `test_aplikacja_rano`
k3 / k4 nie uruchomila testow (blad cudzyslowu w moim skrypcie, "no tests ran") - powtorzona poprawnie (wiersz 9).

### 2.1 Odpowiedzi na pytania zlecenia recenzji

- **B(1) chwila porownania.** `przed` to prostokat mapy z ekranu (uklad ustalony przez poprzedni obieg petli), `po` jest liczone po
  `_calosc.activate()` w tym samym wywolaniu `pokaz_stan`, w ktorym startuje ochrona. Nie ma chwili, w ktorej mapa juz stoi w nowym
  miejscu, a ochrona jeszcze nie dziala: przed wywolaniem widgety stoja w starych miejscach (klik trafia w stare gniazdo), po nim
  ochrona jest aktywna ([W] aktywna od razu 54 z 54; klik bez obiegu petli 0 z 744 w inne gniazdo). Uklad w wielu obiegach (pasek
  przewijania paneli) wystapil 6 razy na 248 - zawsze z ochrona wlaczona juz w pierwszym; przypadku "pierwszy obieg bez ruchu,
  ruch dopiero w nastepnym" nie bylo (0 z 194). Wersja `091e591` jest rownowazna mojemu kandydatowi z rundy 1 (ten tez mial jedno
  `activate()` po odswiezeniu); usuniete wobec `b9964cb` `_kolumna_uklad.activate()` dotyczy tylko D5.
- **B(2) koszt i inne ekrany.** `activate()` jest wolane tylko, gdy poprzednia mapa miala gniazda do klikniecia; rano `_mapa_podpis`
  jest None (zerowany przy zmianie trybu, `_odswiez` wraca przed mapa) - na ekranie porannym nie jest wolane wcale (przeglad +
  `test_ui_rano.py` 32 passed, k3 / k4 5 z 5). Czas: wiersz 8.
- **C program przy szybkim restarcie.** `BlokadaStanowiska.zajmij()` nie czeka i nie ponawia (`aplikacja.py:268-288`, `main`
  `:1690-1695` - od razu komunikat "program juz dziala", kod 3). Zwloka 0,78-1,34 ms wystepuje tylko, gdy zabity zostaje proces
  posredniczacy venv (wlasciwy interpreter ginie chwile po nim); przy zwyklej awarii interpreter ginie sam i blokada znika z nim.
  Nowy egzemplarz nie zdazy siegnac po blokade w tym czasie: sam start interpretera srodowiska wersji trwa 135-171 ms (wiersz 16),
  a przed blokada sa jeszcze importy i ladowanie modulow. Falszywe "program juz dziala" przy szybkim restarcie: nierealne.
- **D test CR.** `test_p15_r2_raport_e3_a6_bez_samotnego_znaku_cr` czyta JEDEN plik (`raporty/E3-A6_2026-11-18.md`) i szuka CR poza
  koncem wiersza - nie pada na inne raporty (na galezi 2 istniejace raporty maja CRLF: 104 i 24 bajty CR) ani na nowe pliki przyszlych
  paczek, nie pada tez przy CRLF z `autocrlf`. Nie jest za szeroki. Testy i `raporty/` nie wchodza do paczki wydania (katalog
  `wersje\<wersja>\program` ich nie ma), wiec test dziala tylko z repo - jak `test_p15_kandydaci_py_same_bajty_ascii`.

## 3. Kryteria zlecenia (runda 2, `p15-r2.md`)

| Nr | Kryterium | Ocena |
|---|---|---|
| 1 | Sekcja "Runda 2"; proby recenzenta po poprawce: falszywe wlaczenia 0 z n, przy ruchu n z n, klik po poleceniu 0 z 76, zwykly wieczor jak `main` | **Potwierdzone wlasna proba**: 0 z 40, 16 z 16, 0 z 76, 9 = 9 (wiersze 1, 2, 5); sekcja 14 raportu wykonawcy - przegladem, liczby zgodne z moimi |
| 2 | Uklad ekranu identyczny co do piksela z `main` (16 zrzutow) | **Potwierdzone wlasna proba**: 16 z 16, 0 roznych pikseli, wobec `main` `62ef6f5` (wiersz 7) |
| 3 | `test_b1`: 20 z 20 w srodowisku wersji i 20 z 20 bazowym; wstrzykniecie wykryte | **Potwierdzone wlasna proba** co do diagnozy, limitu i wstrzykniec (wiersze 10-12: 0,78-1,34 ms; 3 z 3 + 3 z 3; W3, B1a, B1b, B1c wykryte); liczba 20 z 20 wg wykonawcy, niesprawdzone. Wymaganie nie oslabione: test pada, gdy blokada zostaje i gdy znika po czasie dluzszym niz limit |
| 4 | Pelny pytest interpreterem bazowym 0 failed | **Potwierdzone przegladem** logu: `robocze\p15\pytest_r2_091e591.log` konczy sie "2213 passed, 9 skipped, 1 warning in 1575.70s (0:26:15)"; `ciezkie.log`: START 01:45:38, KONIEC 02:11:58, kod -1073740791 (po wierszu podsumowania - nie oceniam); `git diff --stat 091e591 d3b3ea7`: 1 plik (raport) |
| 5 | Wstrzykniecia rundy 2: min. 4 | **Potwierdzone wlasna proba**: moje 4 z 4 (wiersze 12-13); wykonawcy 8 z 8 - przegladem |

Punkty zlecenia rundy 2: p. 1 (P1) i p. 2 (P2) - zamkniete (sekcja 1.1); p. 3 (`test_b1`) - diagnoza potwierdzona, limit 2 s to ok.
1500 x najdluzszy pomiar, a blokada, ktora zostaje, konczy test po 2 s; p. 4 (CR) - usuniety 1 bajt, test pilnuje; p. 5 (D1-D4) -
odlozone z uzasadnieniem, bezpiecznie (zadna nie jest gorsza niz na `main`).

## 4. Zakres plikow i zasady

- Zakres: 11 z 11 plikow na liscie `p15.md` + rozszerzenie `p15-r2.md`: 9 plikow rundy 1 oraz `testy/test_aplikacja.py` (+14 / -1,
  2 fragmenty: stala `B1_LIMIT_ZWOLNIENIA_BLOKADY_S` i tresc `test_b1_blokada_znika_razem_z_procesem` - zaden inny test nie zmieniony)
  i `raporty/E3-A6_2026-11-18.md` (1 bajt). `testy/test_instrukcje.py` w `43a88cc..HEAD` pochodzi ze scalenia `main`, nie z paczki.
- Zakaz napisow: `git diff origin/main...origin/e3/p15 -- .../statusy.py ".../ui/napisy*.py"` - 0 wierszy; `test_instrukcje.py` 36 passed.
- Nietykalne, `instrukcje/**`, `Ramki/etap3/**`, `instalacja/**`, `README.md`: 0 plikow w diffie. Schemat: `WERSJA_SCHEMATU` / `MIGRACJE`
  tylko w wierszu kontekstu `opisy_modulow/baza.md`, bez zmian w kodzie. W testach 0 nowych `skip` / `xfail`.
- ASCII / LF: w dodanych wierszach calego diffu 0 znakow spoza ASCII; bajtow CR w 11 plikach paczki: 0.
- Dane osobowe: testy i raport - dane sztuczne ("Technik A", numery plytek atrapy). Duzych danych brak.
- Commity: 14 (bez scalen), przedrostek "E3-P15"; stopka `Co-Authored-By` w 6 z 6 commitow rundy 2.

## 5. Do decyzji wlasciciela

1. (bez zmian z rundy 1) Wariant "ochrona" zostawia skok mapy przy kazdym komunikacie nad mapa i chroni 800 ms. Czy po wydaniu
   przeniesc komunikaty tak, zeby mapa nie zmieniala miejsca ("stala geometria" - przebudowa ukladu, nowe zrzuty instrukcji).
2. (bez zmian z rundy 1) Kafelki plytek i przyciski paneli nad mapa przesuwaja sie razem z mapa i nie sa chronione (18 z 860
   starych miejsc pod innym elementem; bez zapisu decyzji). Objac ochrona czy zostawic do wariantu "stala geometria".
3. Po P2 mapa przygasa na 800 ms takze po poleceniu technika, ktore skonczylo sie komunikatem nad mapa (nieudany zapis listy,
   nieudany start skanu, brak wybranej osoby) - to zamierzony skutek poprawki; zwykla decyzja i wlasne zamkniecie komunikatu
   mapy nie przygaszaja.

Do koordynatora (nie uwaga do paczki): `test_aplikacja.py::test_f_petla_qt_bez_przerw_podczas_analizy_10_plytek` padl raz na 16
moich przebiegow na galezi (pod obciazeniem; `main` 11 z 11, w tym 1 zaliczony w 2. pomiarze) - przy testach koncowych na obciazonym
PC moze wymagac powtorki wg zasady z `wspolne.md`.

WERDYKT: do scalenia (B 0, P 0, D 6)
