# Raport recenzenta - PR #55 (E3-O2), runda 2 (recenzja przyrostowa)

Data: 21.11.2026 (15:54-16:17). Zakres: commity po 2c79335 na galezi `e3/o2`, HEAD = 7ebb5cd: 86b7a33 (scalenie `main`
1fce3fe - zmiany wniesione przez `main` nie sa przedmiotem recenzji), d021bb6 (kod i testy B1, P1, D), 5dd850b (opisy),
commity raportu, 7ebb5cd (latka testu k4 spoza paczki). Metoda: przeglad `git diff 86b7a33 7ebb5cd` (10 plikow) i
`git diff main...e3/o2` (18 plikow), wlasne proby w kopii `<PC-katalog>\qc-wt\rec-o2` (detached 7ebb5cd), raport
wykonawcy (sekcja 19) czytany po wlasnych probach. Pliki robocze: `<PC-katalog>\koordynator\robocze\rec-o2\`
(`proby_r2.py`, `okno_r2.py`, `wstrzyk_r2.ps1`, logi `*_r2*.log`, zrzuty `zrzuty\r2_*.png`). Uruchomiono: testy paczki
(56), test k4 5 razy, 24 proby kontrolera z 2 atrapami ramek, 3 scenariusze okna offscreen 1536 x 864 (6 zrzutow,
5 obejrzanych), 8 wstrzykniec, 3 pliki testow O3 / O4 / ponownego skanu. Pelnego pytest nie powtarzano (wynik na 7ebb5cd
sprawdza koordynator w logu; liczby 2494 / 9 / 2 i 2495 / 9 / 1 na 5dd850b - wg wykonawcy, niesprawdzone przeze mnie).

STAN: ZAKONCZONY.

## 0. Werdykt i liczby

WERDYKT: do scalenia po poprawkach (B 0, P 3, D 3 nowe + D4 z rundy 1 bez zmian) - z zastrzezeniem do B1 (nizej).

- **B1: zamknieta W BRZMIENIU ZLECENIA RUNDY 2 (wariant z pytaniem o ponowny skan), ale skutecznosc poprawki jest duzo
  wezsza, niz zakladalo zlecenie i moj raport rundy 1.** Program zadaje pytanie "Ponowny skan tej samej plytki?" tylko
  wtedy, gdy oba skany maja TE SAME PRACE (co najmniej 50 % wspolnych projektow), gdy w ktoryms skanie rozpoznano mniej
  niz 3 projekty albo gdy to ten sam plik (`session.py:957-970`). Dwie ROZNE plytki o jednym numerze maja zwykle rozne
  prace - wtedy pytania NIE ma i ramka W dalej swieci wynik nowego skanu pod plytka lezaca: proby X1 (okragla "n3
  odczytana jako 2" z innymi pracami) i X1b (kwadrat n2 z innymi pracami): 120 swiecacych pikseli wyniku drugiego skanu
  pod plytka lezaca, 0 pytan, 0 komunikatow - tak samo jak przed runda 2. **Blad jest moj:** proby G1 / H1 rundy 1 uzywaly
  skanow sztucznych z tymi samymi numerami projektow (atrapa: projekt = numer gniazda), wiec pytanie sie pojawialo;
  opisalem je jako "plytke z innymi pracami". Decyzja koordynatora "warianty BEZ pytania = mechanizm zastany, lista
  wlasciciela" obejmuje ten przypadek co do litery (na `main` to samo dla kwadratow - proba H3), ale zapadla na
  podstawie blednego opisu: wariant bez pytania to nie tylko R59 + R54 i numer wpisany z bledem, lecz takze oba
  scenariusze B1 (kwadrat nN + okragla nN; okragla z dolkiem odczytanym jako N), gdy plytki niosa rozne prace i po co
  najmniej 3 rozpoznane projekty. Wg miary rundy 1 ("wynik innej plytki na ramce = B") to nadal B; wg decyzji rundy 2 -
  lista wlasciciela. Rozstrzyga koordynator; ja licze to jako P2 (opis, test, lista wlasciciela - nizej), bo poprawka
  w kodzie wymaga twardszej reguly ramki (sekcja 5 p. 1), ktorej zlecenie rundy 2 zakazalo.
- P1 rundy 1: zamknieta.
- Nowe P: P2 (zakres B1 - opis i test mowia wiecej, niz program robi), P3 (tekst komunikatu `dwa_skany_numeru` nie
  zna przypadku "ta sama plytka, NOWY wsad" i pcha do "Tak, to ponowny skan" = zastapienie skanu poprzedniego wsadu),
  P4 (komunikat `dwa_skany_numeru` zostaje na ekranie po "Zmien numer", gdy pytania juz nie ma).
- Latka testu k4 (7ebb5cd): do przyjecia.
- Scalenie `main`: niczego nie zgubilo; zakres plikow zachowany; D1, D2, D3, D5 rundy 1 zamkniete, D4 bez zmian
  (decyzja wlasciciela).

## 0a. Uwagi rundy 1: zamknieta / otwarta + dowod

| Uwaga | Stan | Dowod (moje proby na 7ebb5cd) |
|---|---|---|
| B1 | zamknieta w wariancie Z pytaniem; wariant BEZ pytania szerszy niz opisano (P2) | G1 (okragla n2 lezy i swieci, skan kwadratu n2, te same projekty): do odpowiedzi 0 swiecacych pikseli (bylo: 9 gniazd wyniku nowego skanu), 1 pytanie, 1 komunikat `dwa_skany_numeru`; po "Tak, to ponowny skan" swieci wynik nowego skanu (120 px, stary skan `zastapiony`). H1 (okragla odczytana jako 2, te same projekty): do odpowiedzi 0 px; "Nie, to nowy wsad" po zdjeciu plytki: 0 px, takze po ponownym polozeniu plytki nr 2 (odpowiedz ramki `niewazny`); "Nie" BEZ zdjecia plytki: pod plytka lezaca swieci wynik ostatniego skanu (120 px) - mechanizm zastany, utrwalony testem. X6 / X7 (kwadrat z numerem wpisanym recznie, te same prace): po wpisaniu numeru 0 px + pytanie + komunikat. Rano (G2): 51 px -> 0 px, `zdublowane_plytki` [4], blokada "Zamknij piec" - bezpiecznie jak dotad. ALE X1 / X1b (inne prace, 8 i 4 rozpoznane projekty, 0 wspolnych): 0 pytan, 0 komunikatow, 120 px wyniku drugiego skanu pod plytka lezaca. Wstrzykniecie J1 (cofniecie B1): 4 testy paczki padaja. |
| P1 | zamknieta | P1a (kwadrat bez numeru + plytka 4 na ramce P), P1b (okragla ramkowa z nieczytelnymi dolkami + plytka 5): komunikat `plytka_czeka_na_numer`, 0 komunikatow z rada "Zeskanuj" / "Zmien numer", 0 px; po podaniu numeru komunikat znika i ramka swieci (51 px). P1c (DWA skany bez numeru): ten sam tekst; po numerze dla 1. skanu plytka 4 swieci, dla plytki 5 komunikat z "ramka ma dla tego pieca tylko plytki: 4". P1d (plytka o numerze, ktory juz jest w planie, + skan bez numeru): 0 komunikatow, 51 px. P1f (skan bez numeru POMINIETY): wraca `plytka_bez_skanu` ("Zeskanuj") - slusznie. Po "Pozniej" w pytaniu o numer kafelek plytki ma przycisk "Podaj numer plytki" (zrzut `r2_r1b`), rada z komunikatu daje sie wykonac. Wstrzykniecie J4: 2 testy padaja. Drobiazgi tekstu: D7. |
| D1 | zamknieta | test `test_r2_d1_...` (zapis przerwany w polowie -> plik bajtowo bez zmian, 0 plikow obok); wstrzykniecie wykonawcy R2-W7 = moje I6b z rundy 1 - wg wykonawcy wykryte (`wstrzykniecia_r2_wynik.txt`: 1 failed), nie powtarzalem |
| D2 | zamknieta | 2 testy `test_r2_d2_*` (w 56 passed); R2-W9, R2-W10 = moje I7, I8 - wg wykonawcy wykryte, nie powtarzalem |
| D3 | zamknieta | `ramka/kalibracja.py:196-227`: kopia powstaje po udanym zapisie pliku tymczasowego, po nieudanej podmianie jest usuwana, kopia wczesniejsza zostaje; moje wstrzykniecie J5 (kopia nieusuwana): 1 failed (`test_r2_d3_...`) |
| D4 | bez zmian (do decyzji wlasciciela) | kod nie zmieniony; opis w raporcie wykonawcy 19.5 p. 4 poprawiony ("kwadratu nie dotyczy" tylko dla pola o100) |
| D5 | zamknieta | `opisy_modulow/aplikacja.md`: 18 wierszy dodanych (sekcja "kontrakt w wersji 6" na koncu) + znak konca ostatniego wiersza; nic poza wpisem |

## 1. Uwagi rundy 2

| Nr | Waga | Plik:linia | Scenariusz -> co sie dzieje | Propozycja |
|---|---|---|---|---|
| P2 | P (wg miary rundy 1: B - decyzja koordynatora, patrz sekcja 0) | `stanowisko/kontroler_api.py:2703` + `:2714-2726` (wstrzymanie tylko przy otwartym pytaniu), `stanowisko/session.py:957-970` (kiedy pytanie powstaje); test `testy/test_okragle_ramka.py:914` (`test_r2_b1_okragla_n3_odczytana_jako_2_...`), raport wykonawcy 19.2, 19.5 p. 1, 19.6 p. 1 i 7, `opisy_modulow/indicate.md:215-223` | Wieczor. Plytka okragla nr 2 lezy na ramce W i swieci. Technik skanuje INNA plytke, ktorej skan dostaje numer 2 (okragla nr 3 z zaslonietym dolkiem albo kwadrat nr 2), z INNYMI pracami - po co najmniej 3 rozpoznane projekty w kazdym skanie, mniej niz polowa wspolnych. Program nie zadaje pytania o ponowny skan (to dla niego "nowy wsad"), wiec poprawka B1 nie dziala: pod plytka lezaca zapala sie wynik nowego skanu (X1, X1b: 120 px, 0 pytan, 0 komunikatow). Testy `test_r2_b1_*` i moje proby G1 / H1 rundy 1 tego nie widza, bo skan sztuczny bierze projekt = numer gniazda (te same projekty w obu skanach = pytanie). Raport i opis modulu przedstawiaja oba scenariusze B1 jako wstrzymane ("i program pyta"), a liste wariantow bez pytania ograniczaja do R59 + R54 i numeru wpisanego z bledem. Poprawka chroni naprawde tylko: ponowny skan tych samych prac, skany z mniej niz 3 rozpoznanymi projektami i ten sam plik. | (1) Test utrwalajacy stan faktyczny (jak `..._mechanizm_zastany`): okragla nr 2 lezy, skan okraglej z `numer_z_dolkow=2` i `projekty` innymi niz w 1. skanie -> 0 pytan, co swieci. (2) Raport 19.2 / 19.5 p. 1 / 19.6 p. 1 i 7 oraz `indicate.md`: napisac wprost, kiedy pytanie powstaje i ze dwie rozne plytki z roznymi pracami NIE sa wstrzymywane (takze okragla z dolkiem odczytanym jako N i para kwadrat + okragla). (3) Koordynator: swiadoma decyzja, czy ten wariant zostaje na liscie wlasciciela z zasada pracy na 28-29.11 (zdejmij plytke z ramki W przed skanem nastepnej), czy blokuje paczke do czasu twardszej reguly. |
| P3 | P | `stanowisko/statusy.py:471-475` (tekst `dwa_skany_numeru`) | Wieczor, codzienna praca z malym wsadem: plytka nr 2 z 2 pracami zeskanowana, potem NOWY wsad (2 inne prace) na tej samej plytce nr 2; technik zdejmuje plytke do skanu, skanuje, kladzie na ramce. Mniej niz 3 rozpoznane projekty = program pyta "Ponowny skan tej samej plytki? ... Czy to ponowny skan tych samych prac?" i (nowosc rundy 2) ramka jest ciemna + komunikat (proba X1c: 0 px, pytanie, `dwa_skany_numeru`). Komunikat zna dwa przypadki: "Jesli to ta sama plytka zeskanowana drugi raz - kliknij Tak, to ponowny skan" i "Jesli to dwie rozne plytki - najpierw zdejmij z ramki ... potem Nie". Tu plytka JEST ta sama i JEST zeskanowana drugi raz, tylko z nowym wsadem - komunikat prowadzi do "Tak, to ponowny skan", czyli do zastapienia skanu poprzedniego wsadu (jego prace i decyzje przestaja sie liczyc). Wlasciwa odpowiedz to "Nie, to nowy wsad" BEZ zdejmowania plytki - wtedy ramka swieci dobrze (X1c: 18 px = 2 gniazda nowego wsadu). Pytanie nad komunikatem mowi poprawnie o "tych samych pracach", komunikat pod nim przestawia kryterium na "te sama plytke". | Tekst wg kryterium pytania, 3 przypadki: te same prace zeskanowane drugi raz -> "Tak, to ponowny skan" (ramka zaswieci); nowe prace na tej samej plytce -> "Nie, to nowy wsad" (ramka zaswieci); na ramce lezy INNA plytka niz ta z ostatniego skanu -> najpierw ja zdejmij, potem "Nie, to nowy wsad". Test: tekst zawiera wszystkie 3 rady. |
| P4 | P (waska sciezka, poprawka 1-2 wiersze) | `stanowisko/kontroler_api.py:2707-2711` (`if obraz == wyslane: return` przed zapisem `self._w_wynik`), skutek w `:2197-2207` | Pytanie o ponowny skan otwarte, plytka nr 2 lezy na ramce, komunikat `dwa_skany_numeru` na ekranie. Technik widzi, ze zeskanowana plytka to nr 3 (dolek zle odczytany), i poprawia numer skanu przyciskiem "Zmien numer" na 3 (droga z 19.5 p. 2 raportu wykonawcy). Pytanie znika (numery rozne), skan dostaje komunikat (c) `numer_niezgodny`, ramka zostaje ciemna - dobrze. Ale obraz dla ramki sie nie zmienil (numer None przed i po, te same kolory), wiec `_w_wynik` zostaje ze starym "numerem wstrzymanym" 2: komunikat "Dwa skany z numerem plytki 2 - ramka czeka na odpowiedz ... dopoki nie odpowiesz na pytanie o ponowny skan" ZOSTAJE na ekranie, choc pytania juz nie ma (proba X5: `pytania` [], komunikaty `dwa_skany_numeru` + `numer_niezgodny`; okno - zrzut `r2_w2c`). Z tej samej przyczyny po polozeniu na ramce plytki nr 3 (tej ze skanu, juz z poprawionym numerem) pojawia sie komunikat (b) "Na ramce wieczornej lezy plytka nr 3, a ostatni skan to plytka nr 2 - ramka nie swieci. Poloz na ramce plytke nr 2" - rada falszywa (proba X5b). Stan nie mija po zdjeciu plytki: po ponownym polozeniu plytki nr 2 komunikat o dwoch skanach wraca (X5b); mija dopiero po nastepnym skanie. Ramka przez caly czas ciemna (0 px) - zlego wyniku nie ma, mylace sa komunikaty. Sprzeczne z "przyjete domyslnie" p. 4 raportu wykonawcy (jeden komunikat (c)). | Aktualizowac `_w_wynik[3]` takze wtedy, gdy obraz sie nie zmienil (albo wlaczyc `wstrzymany` do porownywanego obrazu); test: pytanie otwarte + plytka na ramce -> "Zmien numer" na inny -> 0 komunikatow `dwa_skany_numeru`. |
| D6 | D | `stanowisko/kontroler_api.py:2721`, `:2724` | Dwie galezie `_czeka_na_ponowny_skan` bez testu: wstrzykniecie J2 (poprzedni skan spoza stanu doby nie wstrzymuje) - 6 passed; J9 (pytanie ukryte nie wstrzymuje) - 6 passed. Zachowanie kodu poprawne (proba X2: pytanie ukryte przez `zamknij_pytanie` -> 0 px, komunikat zostaje; okno nie ma przycisku ukrywajacego to pytanie). | Po jednym tescie albo zostawic. |
| D7 | D | `stanowisko/statusy.py:465-469` (tekst `plytka_czeka_na_numer`), `kontroler_api.py:2218` | Tekst jest warunkowy i prawdziwy ("jesli to skan tej plytki, wybierz numer N"), ale gdy skan bez numeru nalezy do INNEJ plytki, znika rada "Zeskanuj plytke nr N": P1c (plytka 6 nieskanowana, skan bez numeru to plytka 5), P1f (skan bez numeru to okragla TESTOWA - jej pytanie ma tylko przycisk "9", a komunikat radzi "wybierz numer 6"). Przy 2 skanach bez numeru tekst mowi "jest skan" (liczba pojedyncza). | Dopisac drugie zdanie: "jesli tej plytki jeszcze nie skanowano - zeskanuj ja"; `bez_numeru` liczyc tylko dla plytek ramki (`na_ramce`). |
| D8 | D | `testy/test_aplikacja_rano.py:867`, `:881` (latka 7ebb5cd) | `if ... moze_zastapic is not None` - gdyby pytanie przestalo sie pojawiac, test nadal by przeszedl (nie odpowiadalby, ramka swiecilaby od razu). Dane testu sa stale: pytanie jest przy skanach i = 3, i = 4 i przy ostatnim skanie plytki 2. | Mozna zaostrzyc: `assert (moze_zastapic is not None) == (i >= 3)`; nie jest to konieczne - obecnosc pytania pilnuja `test_ponowny_skan.py` i testy paczki. |

## 2. Wlasne proby

| Nr | Polecenie / proba | Wynik |
|---|---|---|
| 1 | `py.cmd -m pytest -q -p no:cacheprovider testy\test_okragle_sesja.py testy\test_okragle_ramka.py` (log `p1_testy_paczki_r2.log`) | 56 passed w 50,9 s (kod 0) |
| 2 | Test k4 z latka, 5 osobnych przebiegow (`testy_r2.cmd`, logi `k4_r2_1..5.log`) | 5 z 5 passed; Spacja -> stan ramki W: maks 37 / 40 / 32 / 30 / 56 ms (prog 1000 ms); kolory W = mapa w 95 gniazdach w kazdym przebiegu |
| 3 | `proby_r2.py` - kontroler `AtrapaKontrolera` + prawdziwi klienci ramek + 2 atrapy ramek, 24 proby (log `proby_r2.log`) | B1 z pytaniem: G1, H1 (3 warianty odpowiedzi), X6, X7 - do odpowiedzi 0 px w 6 z 6; po "Tak" 120 px wyniku nowego skanu (G1, H1_tak); po "Nie" bez zdjecia plytki 120 px wyniku ostatniego skanu pod plytka lezaca; po zdjeciu i "Nie" 0 px (takze po polozeniu plytki nr 2 i plytki nr 3). B1 bez pytania: X1, X1b (inne prace) - 120 px pod plytka lezaca, 0 pytan, 0 komunikatow; H2 (R59 + R54), H3 (numer wpisany z bledem, 27 px) - jak w rundzie 1, runda 2 ich nie pogorszyla ani nie poprawila; X4 ("Tak", potem "cofnij zastapienie") - oba skany aktywne, 0 pytan, 120 px wyniku ostatniego skanu (mechanizm zastany). Zwykla praca: X1d (nowy wsad 9 prac na tej samej plytce) - 0 pytan, ramka swieci od razu (120 px) jak przed runda 2; X1c (maly wsad, 2 prace) - pytanie, 0 px do odpowiedzi, po "Nie" 18 px (uwaga P3). X2: pytanie ukryte przez API -> nadal 0 px, komunikat zostaje; komunikat zamkniety przez technika wraca po ponownym polozeniu plytki. X3: trzeci skan (plytka 3) przy otwartym pytaniu -> komunikat (b) dla plytki 2 na ramce, po polozeniu plytki 3 swieci jej wynik; stare pytanie mozna zamknac odpowiedzia bez wplywu na ramke. X5, X5b: "Zmien numer" przy otwartym pytaniu -> komunikat o dwoch skanach zostaje bez pytania, przy plytce nr 3 falszywy komunikat (b) (uwaga P4). Rano: G2 bezpiecznie (51 -> 0 px); P1a-P1g - tabela 0a. |
| 4 | `okno_r2.py` - okno offscreen 1536 x 864, `QT_QPA_FONTDIR=C:\Windows\Fonts` (log `okno_r2.log`; zrzuty `zrzuty\r2_w1`, `r2_w2`, `r2_w2b`, `r2_w2c`, `r2_r1`, `r2_r1b`; obejrzane 5, `r2_w2b` tylko pomiar) | `dwa_skany_numeru`: zolty panel 966 x 132 px (4 wiersze), pod pytaniem z przyciskami "Tak, to ponowny skan" / "Nie, to nowy wsad" i komunikatem "Praca niesprawdzona" - 3 panele, mapa 19 gniazd, legenda i "Zmien numer" widoczne w calosci; kafelek nowego skanu ma znak "czeka na odpowiedz". Gdy technik oglada INNA plytke z pracami do obejrzenia (`r2_w2`): okno zostaje na niej, pytania z przyciskami NIE ma na ekranie, komunikat jest; panel "Nowy wynik czeka: Plytka 2 ... pytanie Ponowny skan tej samej plytki? ... kliknij Pokaz nowy wynik" mowi, jak dojsc do pytania - nie jest to slepa uliczka. `plytka_czeka_na_numer`: panel 966 x 90 px (2 wiersze) pod pytaniem "Podaj numer plytki" (4 / 5 / 6 / Pozniej); po "Pozniej" kafelek "Plytka bez numeru" ma przycisk "Podaj numer plytki". Tekst obu komunikatow czytelny, bez obciec. |
| 5 | Wstrzykniecia (`wstrzyk_r2.ps1`, log `wstrzykniecia_rec_r2.log`; kazde cofniete `git checkout`, po kazdym 0 plikow zmienionych) - 8 | Wykryte 6: J1 (B1 cofniete: ramka swieci mimo pytania - 4 testy paczki failed; test k4 z latka PRZECHODZI - nie jest od tego), J6 (ramka ciemna takze po "Nie" - 2 testy paczki + test k4 failed: k4 nadal pilnuje wyniku na ramce po odpowiedzi), J3 (komunikat `dwa_skany_numeru` dla kazdej plytki - 3 failed), J4 (P1: `plytka_czeka_na_numer` takze bez skanu bez numeru - 2 failed), J5 (D3: kopia zostaje po nieudanej podmianie - 1 failed), J7 (tekst B1 bez rady "najpierw zdejmij" - 1 failed). NIE wykryte 2: J2, J9 (uwaga D6). |
| 6 | Zgodnosc z O3 / O4: `git diff --numstat 1fce3fe 7ebb5cd`, `git diff --stat 1fce3fe 86b7a33`, rodzice 86b7a33; `py.cmd -m pytest -q testy\test_okragle_ekran.py testy\test_o4_test_led.py testy\test_ponowny_skan.py` (log `zgodnosc_o3_o4_r2.log`) | `main` 1fce3fe wobec HEAD: 18 plikow = 17 plikow paczki O2 + `test_aplikacja_rano.py` (4 wiersze dodane, 0 usunietych); commit scalenia ma rodzicow 2c79335 i 1fce3fe i rozni sie od `main` tylko 15 plikami O2 rundy 1 - scalenie niczego z `main` nie zgubilo. Testy 3 plikow na drzewie scalonym: 112 passed w 25,8 s (kod 0) |
| 7 | Bajty 8 plikow rundy 2 z obiektow git (`git cat-file blob 7ebb5cd:<plik>`), `git diff --check 86b7a33 7ebb5cd` | 0 bajtow nie-ASCII i 0 CR w 8 z 8 (`test_okragle_ramka.py`, `kontroler_api.py`, `kalibracja.py`, `aplikacja.md`, `indicate.md`, `ramka/README.md`, raport, `test_aplikacja_rano.py`); `diff --check`: 1 wpis - `README.md:23` (plik istniejacy w CRLF, znak CR liczony jako odstep na koncu; styl pliku bez zmian); `statusy.py`: polskie znaki jak dotad, LF |

## 3. Punkty zlecenia rundy 2

| Nr | Punkt (`o2-r2.md`) | Ocena |
|---|---|---|
| 1 | Scalenie `main` 1fce3fe | potwierdzone wlasna proba (proba 6): 0 zgubionych zmian, 0 plikow spoza paczki poza latka k4 |
| 2 | B1: ramka ciemna do odpowiedzi + komunikat; testy z atrapa; rano bezpiecznie; zwykla praca bez nowych komunikatow; warianty bez pytania bez zmian i na liscie wlasciciela | potwierdzone wlasna proba w brzmieniu zlecenia (proby 3, 4, 5); zastrzezenia: P2 (test "okragla n3 odczytana jako 2" uzywa tych samych projektow co plytka nr 2 - dla innych prac pytania nie ma i nic nie jest wstrzymane; lista wariantow bez pytania niepelna), P3 (tekst komunikatu), P4 (komunikat po "Zmien numer") |
| 3 | P1: brak rady "Zeskanuj" przy skanie bez numeru | potwierdzone wlasna proba (P1a-P1g, J4, zrzuty `r2_r1`, `r2_r1b`); drobiazgi D7 |
| 4 | D: testy atomowosci i 2 warunkow, kopia przy pliku tylko do odczytu, wpis kontraktu 6, README:23 | potwierdzone: D3 wlasna proba (J5), D1 / D2 przegladem testow + wynik wykonawcy, D5 i README przegladem diffu (README: 1 wiersz, `aplikacja.md`: sam wpis) |
| 5 | "Po recznej poprawce numeru ramka zostaje ciemna" zostaje + opis dla dokumentu dnia sprzetu | potwierdzone przegladem (raport 19.5 p. 2; kod bez zmian) i proba X5 (ramka ciemna, komunikat (c)); skutek uboczny w tej drodze: P4 |
| 6 | Pelny pytest 0 failed | wg wykonawcy na 5dd850b: NIE spelnione (2494 / 9 / 2 i 2495 / 9 / 1 - niesprawdzone przeze mnie); przyczyna 1. testu usunieta latka 7ebb5cd (u mnie k4 5 z 5 passed), 2. test (`test_pamiec_linii_na_dysku`) poza paczka i poza kodem rundy 2 - nie badalem; wynik na 7ebb5cd sprawdza koordynator |

### Skutek uboczny B1 w zwyklej pracy

- Kiedy ramka W czeka na odpowiedz: tylko gdy program pyta o ponowny skan. Nowy wsad na tej samej plytce z co najmniej
  3 rozpoznanymi projektami w obu skanach i mniej niz polowa wspolnych = bez pytania, ramka swieci od razu jak przed
  runda 2 (X1d: 120 px). Ponowny skan tych samych prac i maly / slabo rozpoznany wsad (mniej niz 3 projekty) = pytanie
  i ciemna ramka do odpowiedzi (X1c).
- Czy pytanie i tak wymagalo odpowiedzi: tak - do odpowiedzi oba skany sa aktywne (obie plytki na liscie zmiany,
  kafelek nowego skanu ze znakiem "czeka na odpowiedz"), wiec te same prace sa w stanie zmiany dwa razy.
  Zmiana rundy 2: przed nia ramka swiecila mimo otwartego pytania, teraz dopiero po odpowiedzi (wykonawca opisal to
  uczciwie w 19.2 i 19.10).
- Slepa uliczka (ciemna ramka bez pytania na ekranie): nie znalazlem trwalej. Okno nie ma przycisku ukrywajacego
  pytanie o ponowny skan; gdy technik oglada inna plytke, panel "Nowy wynik czeka" prowadzi do pytania (zrzut
  `r2_w2`); komunikat pojawia sie tylko, gdy plytka o tym numerze lezy na ramce. Wyjatek przejsciowy: P4.
  Po odpowiedzi "Tak" / "Nie" plytka zdjeta z ramki PO starcie skanu zostaje ciemna (zasada ramki sprzed paczki,
  `KlientRamki._wynik_wazny`; proby H1_nie_po_zdjeciu, X6: odpowiedz `niewazny`, 0 px, 0 komunikatow) - mechanizm
  zastany, ale komunikat obiecuje "kliknij Tak ..., ramka zaswieci"; do obserwacji na sprzecie (sekcja 5 p. 3).
- "Nie, to nowy wsad" bez zdjecia plytki: to jest ta sama wada co B1 (wynik ostatniego skanu pod plytka z poprzedniego
  skanu, 120 px), dostepna po swiadomej odpowiedzi technika wbrew radzie komunikatu. Komunikat mowi "najpierw zdejmij
  z ramki te, ktora lezy, potem kliknij Nie" - kolejnosc jest podana jasno (pilnuje jej test i wstrzykniecie J7), ale
  program jej nie wymusza. Nie licze tego jako nowej uwagi: stan utrwalony testem, opisany w 19.2 i 19.6 p. 7.
- Kryterium K4 (ramka W ponizej 1 s po Spacji): czas mierzony od Spacji do stanu "skanowanie" na atrapie ramki, PRZED
  przyjeciem wyniku skanu - latka i poprawka B1 nie dotykaja mierzonego odcinka (5 przebiegow: 30-56 ms).

### Ocena latki testu k4 (commit 7ebb5cd): do przyjecia

- Zmiana: 4 wiersze dodane w 2 miejscach (`testy/test_aplikacja_rano.py:867-868`, `:881-882`), 0 usunietych, 0
  zmienionych asercji; plik spoza listy paczki - dopuszczony decyzja koordynatora.
- To dopasowanie scenariusza do nowego zachowania: test skanuje plytki 1, 2, 3, 1, 2 i jeszcze raz 2; drugi skan plytki
  o danym numerze ma pytanie o ponowny skan (te same projekty atrapy), a po B1 ramka czeka na odpowiedz. Test odpowiada
  "Nie, to nowy wsad" i dalej sprawdza to samo co przedtem: wynik na ramce w 5 s, tylko ostatni skan w planie, kolory
  ramki = kolory mapy (95 gniazd), kolor po decyzji, ciemna ramka po skanie zablokowanym, czasy.
- `if ... moze_zastapic is not None` nie wylacza sprawdzen: asercje po warunku wykonuja sie zawsze. Wstrzykniecie J6
  (ramka ciemna takze po odpowiedzi) - test k4 pada, czyli nadal pilnuje, ze wynik dochodzi do ramki. Wstrzykniecie J1
  (cofniecie B1) - test k4 przechodzi: nie maskuje to niczego, bo wstrzymania pilnuja 4 testy paczki. Warunek mozna
  zamienic na asercje obecnosci pytania (D8) - niekonieczne.

## 4. Zakres plikow i zasady

- `git diff --numstat 86b7a33 7ebb5cd`: 10 plikow - `kontroler_api.py` (49 / 8), `statusy.py` (12 / 0),
  `ramka/kalibracja.py` (17 / 6), `testy/test_okragle_ramka.py` (314 / 1), `opisy_modulow/indicate.md` (15 / 1),
  `ramka/README.md` (2 / 0), raport (273 / 5) - z listy paczki; `opisy_modulow/aplikacja.md` (18 / 1: sam wpis
  kontraktu 6 + znak konca ostatniego wiersza), `Ramki/stanowisko/README.md` (1 / 1: wiersz 23) - dopuszczone w tej
  rundzie i w dopuszczonym zakresie; `testy/test_aplikacja_rano.py` (4 / 0) - latka dopuszczona decyzja koordynatora.
- Nietykalne (`match.py`, `inspect.py`, `plate.py`, `synth.py`, `uklad.py`, `modele_plytek/**`), `aplikacja.py`,
  `ui/**`, schemat bazy, `session*.py`, `indicate.py`, `ramka_protokol.py`: 0 zmian w rundzie 2.
- Nowe tresci ASCII + LF (proba 7); 0 plikow binarnych; danych osobowych nie znaleziono (dane sztuczne).
- Kontrakt: 2 nowe rodzaje komunikatow dopisane do wersji 6 (addytywnie), okno pokazuje je bez zmian w `ui/**`
  (zrzuty); wpis w `opisy_modulow/aplikacja.md` jest.
- Raport wykonawcy (sekcja 19): rzetelny co do zmian zachowania (19.2 wiersz "na ramce nic nie lezy", 19.10 skutek
  w zwyklej pracy, niespelnione "0 failed", odstepstwo od "test przed kodem"); nieprawdziwe przez pominiecie jest
  przedstawienie zakresu B1 (P2) - zrodlem jest moj opis z rundy 1, nie zla wola wykonawcy.
- Moja kopia: `git -C qc-wt\rec-o2 status --short` pusty, HEAD 7ebb5cd; w worktree wykonawcy niczego nie uruchamialem.
  Procesy python o 16:14 (`Get-Process python`, lancuch rodzicow): 6 procesow, 0 moich - PID 19448 (pelny pytest
  koordynatora, tor 1, start 15:51:51), 28256, 6428, 7032, 39844 (tory 3 i 4, `odbior2`, start 16:05:38), 12560 (znany,
  bez czasu startu). Kazda moja proba byla jednym procesem i skonczyla sie przed nastepna.

## 5. Do decyzji wlasciciela

Lista wykonawcy (19.6, 8 pozycji) zawiera 6 pozycji z mojego raportu rundy 1 + warianty bez pytania + odstepstwo
2 asercji; jest uczciwa, ale NIEPELNA w pozycjach 1 i 7 (P2). Lista po rundzie 2 - moja wersja:

1. **Dwie plytki o tym samym numerze w jednej zmianie wieczornej - ramka W rozpoznaje plytke tylko po numerze.**
   Program wstrzymuje ramke tylko wtedy, gdy pyta o ponowny skan (te same prace albo mniej niz 3 rozpoznane projekty).
   Dwie rozne plytki z roznymi pracami NIE sa wstrzymywane: plytka lezaca na ramce w czasie skanu drugiej dostaje jej
   wynik, bez pytania i bez komunikatu. Dotyczy: kwadrat R59 + R54 (H2), numer wpisany z bledem (H3), kwadrat + okragla
   o tym samym numerze (X1b), okragla z dolkiem odczytanym jako numer plytki lezacej na ramce (X1), "cofnij
   zastapienie" (X4), odpowiedz "Nie, to nowy wsad" bez zdjecia plytki. Na dni 28-29.11 potrzebna zasada pracy:
   przed skanem nastepnej plytki zdejmij poprzednia z ramki W - albo zgoda na twardsza regule w programie (ramka
   ciemna i komunikat, gdy plytka o numerze wyniku lezala na ramce juz w chwili startu skanu; wymaga zmiany programu
   ramki / `indicate` i sprawdzenia na sprzecie, kiedy naprawde zaczyna sie skan).
2. Numer poprawiony recznie a dolki: ramka zostaje ciemna (decyzja koordynatora na runde 2); propozycja "swiecic, gdy
   numer podany = numer z magnesow ramki" albo przycisk potwierdzenia - bez zmian wobec rundy 1.
3. Ponowny skan tych samych prac: od rundy 2 ramka W swieci dopiero po odpowiedzi "Tak, to ponowny skan"; plytka zdjeta
   z ramki po starcie skanu zostaje ciemna takze po odpowiedzi (zasada ramki sprzed paczki). Ocenic na sprzecie, czy
   technik nie odbiera tego jako awarii ramki.
4. Komunikat (b) wieczorem w zwyklej pracy (poprzednia plytka zostaje na ramce w czasie skanu nastepnej) - prawdziwy,
   znika sam; ocenic uciazliwosc na sprzecie.
5. Komunikat (c) i ciemna ramka takze dla kwadratow, gdy skan obejmie ich dolki (D4) - zostawic czy ograniczyc do
   plytek okraglych.
6. Kalibracja ukladow okraglych z geometrii: ostrzezenie tylko przy 1. starcie; czy potrzebne trwale przypomnienie.
7. Brzmienie komunikatow: 4 z rundy 1, 3 przyczyny bledu analizy, 2 z rundy 2 - do akceptacji po poprawce P3
   (`dwa_skany_numeru`) i ewentualnie D7 (`plytka_czeka_na_numer`).
8. Odstepstwo z rundy 1 (2 zmienione asercje przez pole `ramkowa`) - do przyjecia.
