# S2 - opisy modulow kontra kod: zawieszenia i czas (23.11.2026)

Zakres: opisy `stanowisko/opisy_modulow/` (silnik.md, aplikacja.md, scanner.md, baza.md, pula.md, pamiec_puli.md,
samokontrola.md, README.md) kontra kod `stanowisko/stanowisko/` (silnik.py, aplikacja.py, kontroler_api.py, scanner.py,
baza.py, pula.py, pamiec_puli.py, indeks.py, ustawienia.py, samokontrola.py) oraz `ustawienia.przyklad.toml`.
Temat: limity czasu, liczby procesow / watkow / prob, restart, awaria, blokady, zajeta baza, zajety plik, folder
niedostepny, zimny start, pamiec podreczna, zamykanie, co widzi technik.
Metoda: tylko czytanie plikow (Read / Grep). Nic nie uruchamiano. Numery linii z narzedzia Read.
Wagi nie oceniano. Pliki poza zakresem (statusy.py, indicate.py, excel.py, session.py) cytowane tylko jako odnosnik.
Pominiete jako niezwiazane z czasem / zawieszeniami: reguly danych (okna dat CSV, kuwety, dane osobowe, schemat).

Legenda statusu: ZGODNE / ROZJAZD / BRAK W KODZIE / NIE DA SIE USTALIC (pomiar, test albo kod poza zakresem).
Skroty: S = silnik.py, A = aplikacja.py, K = kontroler_api.py, SC = scanner.py, B = baza.py, PL = pula.py,
PP = pamiec_puli.py, I = indeks.py, U = ustawienia.py, SK = samokontrola.py, T = ustawienia.przyklad.toml.

## Podsumowanie liczb

| Opis | punktow | ZGODNE | ROZJAZD | BRAK W KODZIE | NIE DA SIE USTALIC |
|---|---|---|---|---|---|
| silnik.md | 69 | 61 | 1 | 0 | 7 |
| aplikacja.md | 49 | 42 | 4 | 0 | 3 |
| scanner.md | 30 | 26 | 1 | 0 | 3 |
| baza.md | 8 | 6 | 1 | 0 | 1 |
| pula.md | 3 | 2 | 1 | 0 | 0 |
| pamiec_puli.md | 14 | 8 | 3 | 2 | 1 |
| samokontrola.md | 18 | 14 | 1 | 0 | 3 |
| README.md | 3 | 3 | 0 | 0 | 0 |
| RAZEM | 194 | 162 | 12 | 2 | 18 |

---

## 1. silnik.md

| Nr | Opis (plik:linia) - cytat | Kod (plik:linia) | Status | Uwagi / co mowi kod |
|---|---|---|---|---|
| S1 | silnik.md:3 "kolejka zadan, jedna analiza naraz" | S:1199-1200, S:1606-1617 | ZGODNE | |
| S2 | silnik.md:4 "Open3D w watku pod Qt zawisa (okno testowe: 195 s bez wyniku" | - | NIE DA SIE USTALIC | pomiar historyczny (ui_test) |
| S3 | silnik.md:23 "`limit_zadania_s` (600)" | S:79, S:1219 | ZGODNE | w programie wartosc z [silnik] (A:536) |
| S4 | silnik.md:24 "`limit_startu_s` (180: od `Process.start()` do zgloszenia gotowosci" | S:80, S:1220, S:1508, S:1535, S:1594-1597 | ZGODNE | |
| S5 | silnik.md:24 "`pul_w_pamieci` (2)" | S:90, S:398-399, S:471-472 | ZGODNE | |
| S6 | silnik.md:27 "`czekaj_na_plik_s` (60: jak dlugo ponawiac kopiowanie zajetego pliku skanu)" | S:99, S:1221, S:640-642 | ZGODNE | |
| S7 | silnik.md:28 "`limit_uruchomienia_s` (30: limit samego `Process.start()`) i `proby_uruchomienia` (3)" | S:81-82, S:1222, S:1226, S:1418, S:1462 | ZGODNE | |
| S8 | silnik.md:30 "`na_zdarzenie` (wolanej w watku nadzorcy) albo do kolejki `Silnik.zdarzenia`" | S:1395-1403 | ZGODNE | |
| S9 | silnik.md:36 "`oczekiwanie na zwolnienie pliku skanu` z udzialem 0, gdy plik trzyma inny program" | S:102, S:1052, S:643-645 | ZGODNE | |
| S10 | silnik.md:38 rodzaje bledu `proces`, `limit_czasu`, `start`, `plik_niedostepny` "przez `czekaj_na_plik_s` ... POKAZAC technikowi, zlecic ponownie" | S:92, S:1747-1748, S:1677-1678, S:1762, S:641-642 | ZGODNE | |
| S11 | silnik.md:39 "`zatrzymany` ... wolane w watku, ktory wywolal `stop()`" | S:1301 | ZGODNE | |
| S12 | silnik.md:46-47 "Pliki tymczasowe `*.<pid>.tmp` po procesie zabitym w trakcie zapisu sa usuwane przy kolejnym zapisie" | S:594-606, S:993 | ZGODNE | |
| S13 | silnik.md:49-50 "watek nadzorcy ... proces roboczy (`spawn`, lacze `Pipe` - bez wspolnych kolejek, wiec zabity proces niczego nie blokuje)" | S:1232, S:1268, S:1501 | ZGODNE | |
| S14 | silnik.md:52 "Nadzorca wysyla zadania po jednym, w kolejnosci zlecen" | S:1606-1617 | ZGODNE | |
| S15 | silnik.md:52-53 "wyjatek analizy (takze `SystemExit` ...) = `blad` i nastepne zadanie w tym samym procesie" | S:1186-1187, S:1190-1193 | ZGODNE | |
| S16 | silnik.md:53-55 "proces zniknal ... albo przekroczyl `limit_zadania_s` = `blad` tego zadania, nowy proces, nastepne zadanie (bez ponawiania" | S:1669-1678, S:1739-1748, S:1573-1577 | ZGODNE | |
| S17 | silnik.md:55-56 "Proces, ktory nie umie wystartowac ... oddaje `blad` rodzaju `start` kolejnym zadaniom - jedna proba na zadanie, bez petli restartow" | S:1128-1133, S:1686-1689, S:1752-1762, S:1573-1576 | ZGODNE | "jedna proba" = jedna runda; przy wieszajacym sie `Process.start()` runda = do 3 prob (S:1418) |
| S18 | silnik.md:56-57 "Limit czasu nadzorca sprawdza takze przy kazdej wiadomosci z procesu" | S:1582-1585 | ZGODNE | |
| S19 | silnik.md:58-59 "`stop()` konczy proces i ZWRACA zadania niezakonczone ...; kolejne `stop()` zwraca []" | S:1271-1302, S:1283-1284 | ZGODNE | |
| S20 | silnik.md:61-62 "gdy `na_zdarzenie` blokuje sie dluzej niz `czekaj_s`" | S:1271, S:1289-1292 | ZGODNE | wartosc `czekaj_s` = 5,0 s nie podana w opisie (lista W KODZIE) |
| S21 | silnik.md:64-65 "Proces roboczy, ktory zaczal startowac, gdy `stop()` juz ruszyl (wolny start), jest od razu zabijany" | S:1533-1541 | ZGODNE | |
| S22 | silnik.md:68 "w programie ok. 5 KB, wiecej niz bufor lacza 4 KB" | - | NIE DA SIE USTALIC | biblioteka standardowa / pomiar |
| S23 | silnik.md:72-74 "`start()` biegnie w watku pomocniczym `silnik-start`, nadzorca czeka najwyzej `limit_uruchomienia_s` (30 s ...), a co 0,5 s sprawdza, czy potomek jeszcze zyje" | S:85, S:1458-1468 | ZGODNE | |
| S24 | silnik.md:75-77 "opis potomka do logu ..., zabicie potomka, anulowanie zawieszonego zapisu (`CancelSynchronousIo` ...), zamkniecie obu koncow `Pipe` i kolejna proba po 0,5 s" | S:904-943, S:1479-1490, S:1510-1521, S:83, S:1419 | ZGODNE | |
| S25 | silnik.md:80-82 "Watek, ktorego nie da sie odblokowac w 3 s ... zostaje porzucony: potomek ... jest zabijany od razu ..., a proces, ktorego `start()` skonczy sie mimo to - zaraz po nim" | S:84, S:929-942, S:761-768, S:1452-1456, S:1488-1489 | ZGODNE | |
| S26 | silnik.md:82-83 "Wyjatek z `start()` (np. blad `CreateProcess`) to tez nieudana proba" | S:1446-1449, S:1469-1471 | ZGODNE | |
| S27 | silnik.md:84-85 "Po `proby_uruchomienia` (3) nieudanych probach: `blad` rodzaju `start` pierwszego zadania z kolejki" | S:1427-1432, S:1752-1762 | ZGODNE | |
| S28 | silnik.md:85-87 "aplikacja zleca zadanie raz ponownie, potem pokazuje komunikat \"silnik nie startuje\" (A3) i wstrzymuje skany do ponownego startu programu" | A:74, A:1485-1494, A:1295-1296 | ZGODNE | powrot bez restartu mozliwy przez zdarzenie `gotowy` (A:1321-1328, `silnik_wrocil`) |
| S29 | silnik.md:87 "`stop()` w trakcie zawieszonego startu przerywa go od razu (bez czekania na limit)" | S:1419-1422, S:1462, S:1472-1473, S:1481 | ZGODNE | przerwanie trwa do CZEKAJ_NA_PRZERWANIE_S = 3 s (S:84) |
| S30 | silnik.md:87-88 "`stan()[\"nieudane_uruchomienia\"]` ...; `limit_startu_s` liczony jest teraz od poczatku `Process.start()`" | S:1388, S:1518, S:1508, S:1535 | ZGODNE | |
| S31 | silnik.md:95 "proces roboczy startuje z wlasna, niewidoczna konsola (`CREATE_NO_WINDOW`" | S:89, S:819-829 | ZGODNE | |
| S32 | silnik.md:107-109 "kazda nieudana proba zostawia w procesie okna 1 uchwyt" | - | NIE DA SIE USTALIC | biblioteka standardowa |
| S33 | silnik.md:111-112 "watek sprawdza co 0,5 s, czy zyje proces okna ..., i konczy proces roboczy od razu" | S:104, S:363-366, S:371-382, S:1106-1108 | ZGODNE | "zmierzone: 0,4 s" - pomiar |
| S34 | silnik.md:113 "wlasny limit zadania: `limit_zadania_s` + 30 s" | S:97, S:367-369 | ZGODNE | Straznik nie liczy czasu budowy puli w tle (S:1155, brak `poczatek_zadania`) |
| S35 | silnik.md:114-117 "obiekt zadania (Job Object) procesu okna z `KILL_ON_JOB_CLOSE`" | S:655-688 (683), S:691-718, S:743-760 | ZGODNE | |
| S36 | silnik.md:118-119 "`stan()[\"obiekt_zadania\"]` ...; gdy obiektu zadania nie da sie utworzyc albo przypisac, silnik dziala jak dotad (sam `Straznik`, ostrzezenie w logu)" | S:1387, S:1525-1532 | ZGODNE | |
| S37 | silnik.md:127-128 "ponawianie co 0,1 s, potem 2x, 4x ... rzadziej (najrzadziej co 2 s ...), po `czekaj_na_plik_s` blad `plik_niedostepny`" | S:100, S:640-647 | ZGODNE | pierwszy odstep 0,05 x 2^1 = 0,1 s |
| S38 | silnik.md:129-131 "Kopia jest usuwana po zadaniu; resztki ... usuwane przy starcie procesu roboczego i przed kazda kopia" | S:1061-1062, S:1142-1146, S:1047 | ZGODNE | |
| S39 | silnik.md:131 "Kopia powstaje tylko, gdy po niej zostanie 256 MB wolnego miejsca" | S:101, S:627-630 | ZGODNE | |
| S40 | silnik.md:132 "Koszt: 0,04-0,11 s na skan 46-55 MB" | - | NIE DA SIE USTALIC | pomiar |
| S41 | silnik.md:144-145 "budowana raz na (foldery, wspolczynnik, orientacja, lista plikow ...) - zmiana plikow w folderze = nowa pula przy nastepnym zadaniu" | S:502-521 | ZGODNE | lista plikow folderu liczona przy kazdym zadaniu (S:508-511) |
| S42 | silnik.md:146-147 "`pamiec_linii` dodaje zapis tych linii na dysk (przezywaja restart procesu i programu)" | S:1075-1084, S:1126, S:1161-1165 | ZGODNE | |
| S43 | silnik.md:149-151 "`lacznik_qt(silnik)` ... (zegar Qt oproznia kolejke `silnik.zdarzenia`)" | S:1774-1823 | ZGODNE | aplikacja nie uzywa `silnik.lacznik_qt`, tylko `kontroler_api.lacznik_qt` (A:1717) |
| S44 | silnik.md:169-171 "moduly PySide6 ... importowac W CALOSCI przy starcie programu - na poczatku `main()`, przed pierwszym uzyciem silnika" | A:1655, A:1667, A:1705-1706 | ZGODNE | |
| S45 | silnik.md:172-176 "Plik startowy ... NIE moze importowac Qt na poziomie modulu ...; `multiprocessing.freeze_support()` na poczatku `main()`" | A:39-66 (brak Qt), A:1652 | ZGODNE | |
| S46 | silnik.md:177-178 "silnik dodaje start procesu (jednorazowo, 2-4 s)" | - | NIE DA SIE USTALIC | pomiar |
| S47 | silnik.md:178-179 "Pierwsza plytka po starcie procesu (takze po awarii) placi za pule i linie brzegu" | S:1127, S:1548 | ZGODNE | |
| S48 | silnik.md:180 "Jedna analiza naraz i jeden proces (plan 3.8)" | S:1238, S:1573-1577 | ZGODNE | |
| S49 | silnik.md:181-182 "glowny modul chroniony `if __name__ == \"__main__\":`" | A:1729-1730 | ZGODNE | |
| S50 | silnik.md:185-189 "A3: (1) ... NAJPIERW `scanner.stop()`, POTEM `niezakonczone = silnik.stop()` ... zapisuje zwrocone zadania; (2) po starcie zleca je ponownie; (3) ... nadrabianie" | A:1516, A:1527, A:1549, A:549-555, A:551-559 | ZGODNE | nie w `closeEvent`, lecz w `zamknij()` (aboutToQuit i po `app.exec()`: A:1719, A:1725) |
| S51 | silnik.md:189-190 "`na_zdarzenie` nie moze czekac na watek wolajacy `stop()` (najprosciej `lacznik_qt`)" | A:535-540 (bez `na_zdarzenie`), A:1150 | ZGODNE | |
| S52 | silnik.md:191 "proces roboczy i tak konczy sie sam (obiekt zadania, `Straznik`)" | S:363-369, S:683 | ZGODNE | |
| S53 | silnik.md:194 "plik trwale bez uprawnien do odczytu = `plik_niedostepny` po 60 s" | S:99, S:640 | ZGODNE | w programie wartosc z [silnik] czekaj_na_plik_s (A:537) |
| S54 | silnik.md:196-197 "Bez Windows albo przy odmowie systemu zostaje sam `Straznik`" | S:696-697, S:750-751, S:1529-1532 | ZGODNE | |
| S55 | silnik.md:198 "`zadanie_id` liczy sie od 1 w kazdym obiekcie `Silnik` (po `stop()` trzeba utworzyc nowy)" | S:1244, S:1265-1266 | ZGODNE | |
| S56 | silnik.md:201-202 "Priorytet procesu roboczego jest zwykly" | S (grep: brak SetPriorityClass / nice) | ZGODNE | |
| S57 | silnik.md:203-204 "Proces roboczy, ktory zglasza gotowosc i ginie bez zadania, jest uruchamiany od nowa bez licznika" | S:1739-1750, S:1573-1577 | ZGODNE | |
| S58 | silnik.md:213-218, 226-227 WMI: "ok. 1 s na inicjalizacje, 0,1 s na polaczenie ... po ok. 5 s ... ok. 0,07-0,09 s" | - | NIE DA SIE USTALIC | stanowisko/__init__.py i biblioteka standardowa poza zakresem |
| S59 | silnik.md:263-265 "`Silnik.przygotuj_pule(opis)` (ostatnie wywolanie wygrywa ...) - nadzorca wysyla pule ..., gdy ten jest gotowy i wolny, PRZED kolejnym zadaniem z kolejki; zadanie trwajace konczy sie najpierw" | S:1374-1382, S:1592-1605, S:1619-1634 | ZGODNE | |
| S60 | silnik.md:266 "najczesciej co `ODSTEP_POSTEPU_PULI_S` = 0,25 s" | S:109, S:464-466 | ZGODNE | |
| S61 | silnik.md:268 "Proces bez postepu budowy dluzej niz `limit_zadania_s` = zabity" | S:110, S:1598-1602 | ROZJAZD | kod: limit = min(limit_zadania_s, LIMIT_BEZ_POSTEPU_PULI_S = 120 s) - przy domyslnych 120 s, nie 600 s (opis sam to poprawia w l. 291-292) |
| S62 | silnik.md:268-270 "smierc procesu w trakcie budowy = nowa proba po restarcie, po `PROBY_PRZYGOTOWANIA_PULI` (2) takich z rzedu koniec prob; wyjatek budowy (nie smierc) - bez ponawiania" | S:111, S:1636-1649, S:1720-1725, S:1744-1745 | ZGODNE | |
| S63 | silnik.md:270-271 "Po kazdym restarcie procesu roboczego (awaria, limit czasu) pula zadana buduje sie od nowa sama. `stan()[\"pula\"]`" | S:1548, S:1619-1634, S:1389-1391 | ZGODNE | po 2 przerwaniach z rzedu `_pula_zadana` = None (S:1644-1646) - juz nie |
| S64 | silnik.md:274-275 "30 s, petla okna max 61 ms; ... 0,14 s (4,3 s ...). Pula 400 wpisow zimna: ok. 5 min" | - | NIE DA SIE USTALIC | pomiar |
| S65 | silnik.md:277-279 "`Silnik(pamiec_puli_dni=N)` - przy PIERWSZYM starcie procesu roboczego ... `PamiecPuli.sprzataj(N)` ... `stan()[\"pamiec_puli_usuniete\"]`" | S:1507, S:1134-1140, S:1690-1693, S:1392 | ZGODNE | |
| S66 | silnik.md:289-290 "druga pula budowana w zadaniu, gdy nie byla przygotowana - przy zimnej puli porannej to minuty w limicie zadania" | S:497-500, S:1167, S:1669-1678 | ZGODNE | |
| S67 | silnik.md:291 "Zadanie, ktorego pula jest juz zbudowana w procesie, idzie przed budowa innej puli (D1)" | S:1626-1627 | ZGODNE | |
| S68 | silnik.md:291-292 "Budowa bez postepu: limit `min(limit_zadania_s, LIMIT_BEZ_POSTEPU_PULI_S = 120 s)`" | S:110, S:1599 | ZGODNE | |
| S69 | silnik.md:292 "Blad katalogu pamieci linii w petli zadan nie konczy procesu (D5)" | S:1161-1165 | ZGODNE | |

## 2. aplikacja.md

| Nr | Opis (plik:linia) - cytat | Kod (plik:linia) | Status | Uwagi / co mowi kod |
|---|---|---|---|---|
| A1 | aplikacja.md:22 komunikaty "`plik_zajety` (\"czeka na zwolnienie\"), `plik_niedostepny`, ... `folder_skanera_niedostepny`, `silnik_nie_startuje`, `baza_zajeta`" | A:1238, A:1481, A:1209, A:1492; statusy.py:336-349, 381 (poza zakresem) | ZGODNE | |
| A2 | aplikacja.md:27 "zegar lacznika co 30 ms wola `kontroler.przetworz()` (bez tego zdarzenia skanera i silnika czekaja w kolejkach)" | K:128, K:1167, K:1184-1190; A:1135-1167 | ZGODNE | |
| A3 | aplikacja.md:31 "`closeEvent` okna nie musi niczego robic: `main()` wola `kontroler.zamknij()` po wyjsciu z petli (i przez `aboutToQuit`)" | A:1719, A:1723-1725 | ZGODNE | |
| A4 | aplikacja.md:44 "`blad_zapisu` ... zostaje do udanego zapisu albo zamkniecia przez technika (wraca tylko z nowym takim skanem). `baza_zajeta` (id `baza_zajeta:wyniki`) znika sam po udanym zapisie" | K:3430-3438; A:1391, A:1404 | ZGODNE | |
| A5 | aplikacja.md:56 "`skanowanie_trwa` - od \"start skanu\" do pierwszego pliku, najwyzej `LIMIT_SKANOWANIA_S` = 180 s, albo plik skanera w zapisie" | K:180, K:1932-1950 | ZGODNE | |
| A6 | aplikacja.md:56 "`zajety` (`analiza_trwa` - skan w analizie, w kolejce albo wynik czeka na zapis" | K:1938, K:479-480; A:1081-1083 | ROZJAZD | kod: `analiza_trwa` gdy `kolejka.razem > 0`, a `razem` obejmuje tez `wstrzymane` = skany czekajace na pule (pusta / brak folderu), na sprawdzenie puli po bledzie i przy `silnik_nie_startuje` (A:1082) - "Zamknij piec" zablokowane takze wtedy (przy silnik_nie_startuje do restartu programu) |
| A7 | aplikacja.md:77-78 "`stan.ramki` ... czytany z klientow co `OKRES_STANU_RAMEK_S` (0,25 s) w `przetworz()`" | K:105, K:2255-2256, K:2271 | ZGODNE | |
| A8 | aplikacja.md:90-91 "pamiec ostatnich 4000 kluczy z dziennika" | K:107, K:2379-2384 | ZGODNE | |
| A9 | aplikacja.md:106-107 "\"Test LED\" ...; po 8,5 s plan pieca ponownie" | K:106, K:2990, K:2257-2261 | ZGODNE | |
| A10 | aplikacja.md:118-119 "`zamknij()` najpierw: `zgas()` obu ramek, `Indicate.zatrzymaj()` (najwyzej ok. 1 s; ...), `excel.rozlacz()`" | A:1511; K:2750-2772; indicate.py:1313-1326 (poza zakresem) | ZGODNE | |
| A11 | aplikacja.md:119-120 "Zdarzenia nieodebrane do chwili zamkniecia wracaja po starcie jako historia" | K:2379-2384 (tylko odsiew duplikatow) | NIE DA SIE USTALIC | zachowanie ramki / indicate poza zakresem |
| A12 | aplikacja.md:130-132 "P1: Excel po \"Zamknij piec\" odroczony ... kroki z zegara okna - propozycje (jeden odczyt arkusza), ... (po jednym na obieg)" | K:2832-2855, K:2233 | ZGODNE | odczyt COM idzie w watku okna bez limitu czasu (excel.py poza zakresem) |
| A13 | aplikacja.md:133 "P2: kazdy blad `plan_plytek` = ramka P zgaszona, ..., ponowienie co `OKRES_PONOWIENIA_PLANU_S`" | K:111, K:2265-2266, K:2605 | ZGODNE | wartosc 2,0 s nie w opisie (lista W KODZIE) |
| A14 | aplikacja.md:137-138 "przy starcie piece zamkniete w ostatnich `ZALEGLE_EXCELA_H` godzinach" | K:123, K:2817-2819 | ZGODNE | wartosc 48 h nie w opisie |
| A15 | aplikacja.md:141-142 "D2: zdarzenia ramek przy zajetej bazie czekaja na ponowienie (nie gina), blad ramek / Excela nie przerywa `przetworz`" | K:2245-2254, K:1438-1442; A:1173-1176 | ZGODNE | |
| A16 | aplikacja.md:143-144 "D7: komunikaty \"ramka nie odpowiada\" po `CZAS_NA_POLACZENIE_RAMEK_S`" | K:110, K:2131-2134, K:2262-2264 | ZGODNE | wartosc 2,0 s nie w opisie |
| A17 | aplikacja.md:152-153 "ponowienie co `OKRES_PONOWIENIA_ZDARZEN_S` (1 s), czekanie na baze przy ich zapisie `CZEKAJ_ZDARZENIA_MS` (150 ms zamiast 5 s" | K:112-113, K:2250-2253, K:2288-2312 | ZGODNE | |
| A18 | aplikacja.md:163 "`BlokadaStanowiska` ... ZANIM otworzy baze, log i folder skanera. Drugi egzemplarz: `ProgramJuzDziala` - ... kodem 3 ... Blokade trzyma system ...; `zamknij()` zwalnia ja na koncu" | A:258-307 (278: LK_NBLCK, bez czekania), A:453-454, A:1690-1695, A:79, A:1564 | ZGODNE | |
| A19 | aplikacja.md:164 "Start: baza i sesja ...; sprzatanie `dane/podglady` ...; silnik z `ust` ...; uklady plytek wczytane od razu ...; liczenie puli w tle; zadania z `dane/zadania_niezakonczone.json` zlecane ponownie; dopiero potem `Scanner(..., znane=...)`" | A:456-461, A:534-556, A:557-563 | ZGODNE | |
| A20 | aplikacja.md:165 "Samo zobaczenie pliku niczego trwale nie zapisuje, wiec awaria miedzy zdarzeniem a wynikiem nie gubi skanu" | A:1227-1229, A:1189-1196, A:551 | ROZJAZD | kod: przy zdarzeniu skanu najpierw wpis `nowy_skan` w dzienniku `zdarzenia` (A:1227-1228), dopiero potem `_nowy_skan` (A:1229); baza zajeta > 5 s = `BladBazy` lapany w `_bezpiecznie` (tylko log) - skan nie trafia do kolejki az do restartu (nadrabianie), bez komunikatu dla technika |
| A21 | aplikacja.md:168 "pozycja zostaje w pamieci ... zapisywana ponownie sama co `OKRES_KONTROLI_S`, potem 2x, 4x ... rzadziej (najrzadziej co 30 s), bez ponownej analizy, oraz na polecenie `ponow_zapis()` ... Zamkniecie z pozycja niezapisana: zadanie wraca do pliku zadan" | A:75-76, A:249-251, A:1144-1146, A:1375-1405, A:1453-1463, A:1543-1549 | ZGODNE | wartosc OKRES_KONTROLI_S = 1,0 s nie w opisie |
| A22 | aplikacja.md:169 "`proces` / `limit_czasu` -> `session.przyjmij_blad` ... + komunikat `blad_analizy`" | A:1503, A:1412-1434; K:3252-3256 | ZGODNE | |
| A23 | aplikacja.md:169 "`plik_niedostepny` -> komunikat i ponowne zlecenie `[silnik] ponow_plik_niedostepny` razy (3), potem skan `blad` z komunikatem `plik_niedostepny`" | A:476, A:1479-1484, A:1495, A:1503; K:3249-3251 | ZGODNE | |
| A24 | aplikacja.md:169 "`start` ... -> jedna ponowna proba, potem skany CZEKAJA z komunikatem `silnik_nie_startuje` (nie dostaja bledu, wracaja po restarcie programu)" | A:74, A:1485-1494, A:1295-1296 | ZGODNE | |
| A25 | aplikacja.md:170 "Liczba STL liczona w watku pomocniczym ... przy starcie, po \"Odswiez pule\", po kazdym nowym skanie, po kazdym wyniku i po kazdym bledzie analizy (P3; najwyzej jedno liczenie naraz - D4)" | A:671-701, A:548, A:1061, A:1275, A:1451, A:1016 | ROZJAZD | kod: blokada "jedno liczenie naraz" tylko dla cichego liczenia (A:680-682); liczenie glosne (start, "Odswiez pule", `ustaw_pule`) nie sprawdza `_liczenie_puli` i zawsze startuje nowy watek `pula-liczenie` (A:689-701) - przy wiszacym folderze sieciowym kazde klikniecie doklada watek |
| A26 | aplikacja.md:170 "Pula pusta albo bez folderu: skany czekaja (`kolejka.wstrzymane`, komunikat) do \"Odswiez pule\" - nie dostaja bledu analizy" | A:1295-1299, A:703-715, A:1018-1033 | ZGODNE | |
| A27 | aplikacja.md:172 "`zamknij()`: `scanner.stop()`, potem `silnik.stop()`; wyniki, ktore zdazyly przyjsc, sa przyjmowane; ostatnia proba zapisu ...; zadania ... -> `dane/zadania_niezakonczone.json` ...; na koncu zwolnienie blokady. Awaria bez `zamknij`: ... nadrabianie folderu" | A:1506-1567, A:563 | ZGODNE | czas zamykania - stale w liscie W KODZIE |
| A28 | aplikacja.md:174 "Wszystko w watku okna; ... `przetworz()` obsluguje je najwyzej 50 ms naraz. Blad obslugi jednego zdarzenia = wpis w logu i nastepne zdarzenie" | A:481, A:558-559, A:699, A:1135-1167, A:1189-1196; K:127 | ZGODNE | limit sprawdzany miedzy zdarzeniami (A:1166); jedno zdarzenie z zapisem do zajetej bazy trwa do 5 s; ponowienia `_do_zapisu` (A:1144-1146) przed petla, bez limitu |
| A29 | aplikacja.md:189 "Wartosci domyslne rowne domyslnym modulow `scanner` i `silnik` ... `pamiec_linii` od rundy 2 domyslnie `false` - jak w `silnik` (D11)" | U:190, T:122, S:1220/1227 | ROZJAZD | kod: `pamiec_linii` domyslnie True (U:190, T:122 "E3-A5i: domyslnie true"); modul silnik bez ustawien - wylaczona (`pamiec_linii=None`), wiec domyslne programu i modulu sie roznia |
| A30 | aplikacja.md:204 "folder sieciowy z tysiacami plikow jest listowany przy kazdym odswiezeniu (w tle) i przez silnik przy kazdym zadaniu" | A:395-400, A:694-701; S:508-511 | ZGODNE | |
| A31 | aplikacja.md:205 "Skan `blad` (takze `plik_niedostepny` po ponowieniach) jest \"znany\": po restarcie nie jest analizowany sam" | A:551, A:557-559 | ZGODNE | |
| A32 | aplikacja.md:206 "Wynik, ktory czekal na zapis ..., a program zostal zamkniety: zadanie wraca do pliku zadan i skan jest liczony od nowa po starcie" | A:1543-1549 | ZGODNE | |
| A33 | aplikacja.md:209 "Baza zajeta przez inny program blokuje watek okna do `czekaj_ms` (5 s) przy kazdym zapisie (D5, znane); ponowienia ... (najrzadziej co 30 s)" | B:45, B:317-325; A:456, A:1418, A:76 | ZGODNE | |
| A34 | aplikacja.md:218-221 "`aplikacja.stan_pliku` w watku pomocniczym `pula-plik-csv` co `OKRES_KONTROLI_S`, najwyzej jedno sprawdzenie naraz, wynik przez skrzynke - okno nie czeka na udzial sieciowy" | A:93-100, A:778-809, A:811-820, A:1168-1172 | ZGODNE | |
| A35 | aplikacja.md:222 "nieudane ponawiane po `PONOW_KATALOG_S` (60 s; runda 3 D8)" | A:90, A:784-790, A:826-828 | ZGODNE | |
| A36 | aplikacja.md:223 "Jeden watek indeksu naraz: zamowienie w trakcie = kolejne odswiezenie po biezacym" | A:727-731, A:836-839, A:716-718 | ZGODNE | (dotyczy pula_wpisow; dla puli z folderu patrz A25) |
| A37 | aplikacja.md:228-229 "Po odswiezeniu `silnik.przygotuj_pule(opis trybu)`, ZANIM skany wstrzymane pojda do silnika - regula zimnej puli" | A:841-845, A:903-917 | ZGODNE | |
| A38 | aplikacja.md:233-234 "`[silnik] pamiec_puli_dni` (30; 0 = nie) przekazane do silnika tylko z pula wpisow" | U:191; A:509, A:540 | ZGODNE | |
| A39 | aplikacja.md:241-243 "`main()` po utworzeniu `QApplication` wola `zaladuj_moduly_dll()` ... przed pierwszym procesem roboczym" | A:1664-1667, A:1687-1688, A:1705-1706 | ZGODNE | |
| A40 | aplikacja.md:244-246 "po `KNOWNDLLS_SPRAWDZ_PO_S` (5 i 30 s) wpis w logu ... - tylko log, bez wplywu na prace" | A:102, A:984-1006, A:1171 | ZGODNE | |
| A41 | aplikacja.md:248-249 "Zimna pula kilkuset wpisow ... = minuty czekania pierwszego skanu z postepem na pasku" | S:459-466; A:960-967 | NIE DA SIE USTALIC | pomiar |
| A42 | aplikacja.md:260-261 "`MODULY_DLL_PULI` ... - w `main()`, gdy `pula_wpisow`" | A:88, A:1687-1688 | ZGODNE | |
| A43 | aplikacja.md:265 "B1: zaden `os.stat` folderu MillBox / udzialow w watku okna" | A:775-776, A:741, A:801-808 | ZGODNE | w watku okna jest jednak I/O folderu skanera: `scanner.start()` -> `is_dir()` i listowanie (SC:344, SC:391-394, SC:401; A:562) oraz `_istnieje()` (A:164-168, A:1257, A:1281, A:1497) |
| A44 | aplikacja.md:278-281 "`ponow_polecenie(id komunikatu)` ... Odmowa przejsciowa (`KODY_DO_PONOWIENIA` ...): polecenie czeka dalej" | K:174-175, K:3570-3585 | ZGODNE | |
| A45 | aplikacja.md:284-285 "Program sam decyzji NIE ponawia ...; po restarcie programu lista do ponowienia jest pusta" | K:1301, K:3547-3568 | ZGODNE | |
| A46 | aplikacja.md:288-293 "`CZEKAJ_POLECENIA_MS` = 200 ..., odczyt stanu ... `CZEKAJ_STANU_MS` = 100. ... zegar okna ponawia odczyt co `OKRES_NADRABIANIA_STANU_S` = 1 s jedna proba bez czekania" | K:119-122, K:3482-3488, K:1340-1360, K:1378-1399, K:1446; A:1179 | ZGODNE | |
| A47 | aplikacja.md:293-294 "przed 14,7-14,9 s, po 0,65-0,68 s" | - | NIE DA SIE USTALIC | pomiar |
| A48 | aplikacja.md:294-296 "polecenia plytki ... czytaja tryb skanu POD ta oslona (`_polecenie_plytki`)" | K:3959 | ZGODNE | |
| A49 | aplikacja.md:298-299 "`Aplikacja.start_skanu` (Spacja): wpis `start_skanu` w dzienniku czeka na baze tak samo krotko; gdy baza jest zajeta, Spacja dziala ..., brakuje tylko wpisu dziennika (ostrzezenie w logu)" | A:1120-1124 | ZGODNE | |

## 3. scanner.md

| Nr | Opis (plik:linia) - cytat | Kod (plik:linia) | Status | Uwagi / co mowi kod |
|---|---|---|---|---|
| C1 | scanner.md:6 "Modul nie laduje numpy, trimesh, Open3D ani Qt (dziala w procesie okna, w zwyklym watku)" | SC:51-64, SC:346 | ZGODNE | |
| C2 | scanner.md:15 "`stabilizacja_ms` 300" | SC:69, SC:297, SC:595 | ZGODNE | |
| C3 | scanner.md:17 "`odrzuc_po_s` 5" | SC:73, SC:669, SC:685 | ZGODNE | |
| C4 | scanner.md:18 "`okres_s`, `przeglad_s` 0,05 i 2" | SC:74-75, SC:544-550, SC:556 | ZGODNE | bez kandydatow watek czeka min(przeglad_s, 0,5 s) (SC:547-549) |
| C5 | scanner.md:22 "`informuj_po_s`, `informuj_co_s` 10 i 60" | SC:80-81, SC:727-737 | ZGODNE | |
| C6 | scanner.md:23 "`odpytywanie` = bez biblioteki watchdog ..., sam przeglad co `przeglad_s`" | SC:291-293, SC:465, SC:470-473 | ZGODNE | |
| C7 | scanner.md:26-27 "Podpiecie do `ustawienia.toml` robi paczka A3 (proponowane klucze `[scanner]`: ...)" | A:556-561; U:122-129 | ZGODNE | czasy odrzuc_po_s, okres_s, przeglad_s, informuj_* nie sa kluczami ustawien (tylko stale) |
| C8 | scanner.md:35-36 "funkcji `na_skan` ... (wolanych w watku obserwatora) ...; odrzucenia sa tez w `Scanner.odrzucone` (ostatnie 1000)" | SC:746-753, SC:77, SC:305 | ZGODNE | |
| C9 | scanner.md:51-52 "niezaleznie co `przeglad_s` caly folder jest przegladany (zgubione powiadomienia, folder, ktory pojawil sie pozniej, watchdog, ktory nie wystartowal)" | SC:556, SC:567-569, SC:625-638 | ZGODNE | |
| C10 | scanner.md:53-55 "Koniec zapisu = ... (1) rozmiar i czas pliku bez zmian przez `stabilizacja_ms`; ... (3) zaden program nie trzyma pliku otwartego do zapisu" | SC:588-596, SC:693-695 | ZGODNE | |
| C11 | scanner.md:55-57 "Plik stabilny, ale zly, czeka `odrzuc_po_s` ... przed wpisem jeszcze raz sprawdzany rozmiar i czas" | SC:684-691 | ZGODNE | |
| C12 | scanner.md:63 "proby co `okres_s`, potem 2x, 4x ... rzadziej (najrzadziej co 2 s; dla pliku otwartego do zapisu co 0,25 s)" | SC:78-79, SC:729-730, SC:682, SC:694 | ROZJAZD | kod: pierwszy odstep = okres_s x 2^1 = 0,1 s (proby zaczyna od 1, SC:729-730), czyli 2x, 4x, 8x okres_s ... do 2 s / 0,25 s; "co okres_s" nie wystepuje (roznica 0,05 s) |
| C13 | scanner.md:63-64 "bez limitu liczby prob; po `informuj_po_s` (10 s) `Oczekiwanie` dla technika, powtarzane co `informuj_co_s` (60 s)" | SC:727-737 | ZGODNE | sprawdzane tylko przy probie (dokladnosc <= 2 s) |
| C14 | scanner.md:65-66 "Plik zajety nie trafia do plikow znanych: po zwolnieniu ... jedno zdarzenie; po restarcie programu wraca przez nadrabianie" | SC:723-726, SC:710 | ZGODNE | |
| C15 | scanner.md:66-67 "Trwaly brak uprawnien do pliku wyglada tak samo (`Oczekiwanie` co minute) - nic nie ginie po cichu" | SC:678-683, SC:731-737 | ZGODNE | |
| C16 | scanner.md:69-71 "Stan poczatkowy ustala PIERWSZY udany przeglad folderu - przy starcie albo pozniej, gdy folder ... pojawi sie po starcie" | SC:391-394, SC:636-638 | ZGODNE | |
| C17 | scanner.md:74-76 "Chwilowy blad listowania ... nie kasuje wiedzy o znanych plikach: ... zapominany dopiero, gdy `os.stat` mowi, ze go nie ma" | SC:653-664 | ZGODNE | |
| C18 | scanner.md:78-79 "Pliki zastane sa ustalane w `start()` (przed powrotem), a decyzja nadrabiania (wywolania `znane`) zapada w pierwszym obiegu watku obserwatora - nigdy w watku okna" | SC:344, SC:382-394, SC:557-558, SC:452-457 | ZGODNE | `start()` listuje caly folder w watku wolajacym (SC:401), aplikacja wola `start()` w watku okna (A:562) |
| C19 | scanner.md:80-81 "przeglad sprawdza, czy watek watchdog zyje i czy folder ma ten sam numer pliku - jesli nie, obserwator watchdog rusza od nowa" | SC:516-531, SC:634 | ZGODNE | |
| C20 | scanner.md:82-83 "`stop()`, ktory nie doczekal sie konca watku ..., zostawia watek widoczny w `dziala()`; ... `start()` nie uruchamia drugiego (D11)" | SC:349-360, SC:334-340, SC:598, SC:676, SC:705 | ZGODNE | `czekaj_s` = 5,0 s nie w opisie |
| C21 | scanner.md:86-88 "`znane` ... wolana wylacznie w watku obserwatora ...; wyjatek = plik \"nieznany\"" | SC:452-458 | ZGODNE | |
| C22 | scanner.md:98-100 "`ZnanePliki(wpisy)` - ... zbior niezmienny, wiec wywolanie jest bezpieczne z kazdego watku i nie dotyka bazy" | SC:218-234 | ZGODNE | |
| C23 | scanner.md:104-106 "`Zbieracz`: odpytuje co 1,5 s i potrzebuje 2 zgodnych odczytow (opoznienie 1,5-3 s ...) ... po 30 s" | - | NIE DA SIE USTALIC | dzien_skanera_rdzen poza zakresem |
| C24 | scanner.md:124-127 "nie zostalby rozpoznany na Windows inaczej niz po `stabilizacja_ms` (poza Windows `ktos_pisze` zawsze zwraca False" | - | NIE DA SIE USTALIC | `ktos_pisze` w dzien_skanera_rdzen poza zakresem |
| C25 | scanner.md:128-129 "`ktos_pisze` ... jest wolane dopiero dla pliku stabilnego" | SC:595-599, SC:669, SC:685, SC:693 | ZGODNE | |
| C26 | scanner.md:133-135 "A3 MA podac nadrabianie: `znane=ZnanePliki(<wiersze z bazy>)`" | A:551-559 | ZGODNE | |
| C27 | scanner.md:140 "Rozdzielczosc: zegar systemu (ok. 16 ms na Windows)" | - | NIE DA SIE USTALIC | system |
| C28 | scanner.md:141-142 "Folder niedostepny przy starcie albo znikajacy w trakcie nie jest bledem: obserwator czeka i wraca do pracy (`stan()[\"folder_dostepny\"]`)" | SC:391-394, SC:625-633, SC:377; A:1206-1210 | ZGODNE | technik widzi `folder_skanera_niedostepny` (kontrola co OKRES_KONTROLI_S) |
| C29 | scanner.md:143 "Funkcje zwrotne i `znane` sa wolane w watku obserwatora; okno Qt powinno w nich tylko emitowac sygnal albo wkladac do kolejki" | A:558-559 | ZGODNE | |
| C30 | scanner.md:145 "Caly folder z podfolderami jest listowany co `przeglad_s`" | SC:556, SC:641 | ZGODNE | |

## 4. baza.md

| Nr | Opis (plik:linia) - cytat | Kod (plik:linia) | Status | Uwagi / co mowi kod |
|---|---|---|---|---|
| B1 | baza.md:3 "Baze pisze jeden proces (proces okna przez `session`) ... `baza.otworz` - to ono wlacza klucze obce i czekanie na blokade" | B:317-325, B:396-397; A:456; PL:361 | ZGODNE | przy pula_wpisow drugie polaczenie piszace w tym samym procesie (watek pula-katalog: PL:361, I:241, I:298) |
| B2 | baza.md:8 "`otworz(plik, tylko_odczyt=False, czekaj_ms=5000)`" | B:45, B:396-397 | ZGODNE | |
| B3 | baza.md:10 "Baza zajeta przez inny program (blokada dluzej niz `czekaj_ms`): `BladBazy` \"baza jest zajeta przez inny program ... niczego nie zapisano\" - nie surowy blad SQLite" | B:496-504, B:531-536; B:334-338, B:427, B:381-393 | ROZJAZD | dla operacji `Baza` zgodne; przy `otworz` `_wersja` lapie kazdy `sqlite3.DatabaseError` (takze "database is locked" po 5 s) i zglasza "plik nie jest baza SQLite albo jest uszkodzony" (B:334-338); BEGIN IMMEDIATE migracji idzie wprost `pol.execute` -> "migracja ... nie powiodla sie" (B:384, B:389-393) |
| B4 | baza.md:45 "porownana bajt po bajcie przy kazdym otwarciu (blokami po 1 MB, bez pamieci podrecznej)" | B:346-363, B:366-370 | ZGODNE | |
| B5 | baza.md:50 "Tryb dziennika SQLite domyslny (jeden plik, bez plikow `-wal`); jeden proces piszacy. Kopia sprzed migracji ... przy zamknietym polaczeniu" | B:317-325 (brak PRAGMA journal_mode - grep), B:431-434 | ZGODNE | |
| B6 | baza.md:56 "`Baza.czekanie(ms)` ... najwyzej `ms` (`PRAGMA busy_timeout` ...), po bloku - takze po wyjatku - wraca poprzednie czekanie; bloki mozna zagniezdzac; `BladBazy` podaje czas" | B:478-494, B:502 | ZGODNE | |
| B7 | baza.md:56 "Uzywa tego kontroler dla polecen wywolanych kliknieciem i dla odczytu stanu w watku okna" | K:1333-1348, K:3483; A:1121 | ZGODNE | |
| B8 | baza.md:56 "100 ms -> 0,17 s ... / 0,46 s ...; 200 ms -> 0,30 s / 0,68 s; 400 ms -> 0,53 s / 0,96 s" | - | NIE DA SIE USTALIC | pomiar |

## 5. pula.md

| Nr | Opis (plik:linia) - cytat | Kod (plik:linia) | Status | Uwagi / co mowi kod |
|---|---|---|---|---|
| P1 | pula.md:22 "`KatalogPul.odswiez()` w watku roboczym (cechy nowego pliku to ok. 0,2 s; 17 plikow z PC: 3,5 s), obiekt utworzony w tym watku (wlasne polaczenie SQLite)" | A:739-761 (745); PL:361-365 | ZGODNE | czasy - pomiar |
| P2 | pula.md:55 "Folder, w ktorym od `usun_z_puli_po_dniach` dni nic sie nie zmienilo, nie jest czytany (archiwum) ani usuwany" | I:212-226, I:163-174 | ROZJAZD | kod: kazdy folder jest listowany (`_wpisy_folderu`: os.scandir, stat kazdego STL, liczenie STL w podfolderach - I:167-173) PRZED testem wieku (I:215, test I:221); pomijane jest tylko liczenie skrotu / cech i zapis. "ani usuwany" - zgodne (I:233-234) |
| P3 | pula.md:76 "D11 - kazdy przebieg listuje wszystkie foldery zrodla (takze archiwum; nie czyta ich plikow)" | I:202-203, I:212-216 | ZGODNE | tresci plikow archiwum nie czyta; liste plikow i stat - tak (patrz P2) |

## 6. pamiec_puli.md

| Nr | Opis (plik:linia) - cytat | Kod (plik:linia) | Status | Uwagi / co mowi kod |
|---|---|---|---|---|
| M1 | pamiec_puli.md:6-8 "0,1-0,3 s, profil glebokosci kolejne 0,2-0,5 s ... Z dysku: czesc lekka 1-2 ms, pelny projekt 12-21 ms" | - | NIE DA SIE USTALIC | pomiar |
| M2 | pamiec_puli.md:10-12 "`PamiecPuli(katalog=None, limit_ciezkich=64)`; `z_ustawien(ust)` = katalog `[sciezki] pula_cache` / `projekty` (... domyslnie `dane/pula_cache` ...). Bez katalogu = tylko pamiec procesu" | PP:41-42, PP:95-98, PP:105-107, PP:119-121; U:176 | ZGODNE | |
| M3 | pamiec_puli.md:32-33 "Plik zmieniony ... = inny wpis; Zmiana algorytmu albo bibliotek = inny odcisk = nowe wpisy; stare zostaja do `sprzataj`" | PP:57-76, PP:116-117 | ZGODNE | |
| M4 | pamiec_puli.md:34-35 "Wpis uszkodzony ... = liczony od nowa (licznik `bledy_odczytu`), bez wyjatku. Zapis atomowy (plik tymczasowy + `os.replace`)" | PP:188-190, PP:246-248, PP:265-269 | ZGODNE | |
| M5 | pamiec_puli.md:36-37 "`sprzataj(dni)`: usuwa wpisy nieuzywane od `dni` dni (kazdy odczyt odswieza czas pliku) i pozostalosci przerwanych zapisow starsze niz doba" | PP:285-299, PP:192, PP:279-283, PP:234-250, PP:145-148, PP:201-206 | ROZJAZD | kod: czas pliku odswieza tylko odczyt czesci lekkiej z dysku (PP:192); odczyt pelnego projektu z dysku (`_czytaj_ciezki`, PP:234-250) i trafienia w pamieci procesu (PP:145-148, PP:201-206) pliku nie dotykaja. Pozostalosci `.tmp` > doba - zgodne (PP:294) |
| M6 | pamiec_puli.md:37-38 "Kto i kiedy wola sprzatanie - do ustalenia przy integracji z aplikacja (propozycja: przy starcie, `dni` = `[match] usun_z_puli_po_dniach` + zapas)" | S:1134-1140, S:1507; A:509, A:540 | ROZJAZD | opis nieaktualny: wola proces roboczy silnika przy pierwszym starcie w obiekcie Silnik, dni = `[silnik] pamiec_puli_dni` (30), tylko przy `pula_wpisow = true` |
| M7 | pamiec_puli.md:53-55 "Czesc lekka nowego STL liczona jest w procesie, ktory buduje pule (... 0,9 s na wpis, 400 wpisow 361 s); ... lepiej budowac pule zaraz po odswiezeniu, przed pierwszym skanem" | S:459-466, S:1374-1382; A:842 | ZGODNE | budowa w tle przed skanami jest; liczby - pomiar |
| M8 | pamiec_puli.md:56 "Pelnych projektow w procesie najwyzej `limit_ciezkich` (64 ...); najdawniej uzyte wypadaja i wracaja z dysku" | PP:42, PP:252-256, PP:207-209 | ZGODNE | |
| M9 | pamiec_puli.md:57-58 "dzis nic poza testem nie wola `sprzataj`" | S:481-483, S:1136 | ROZJAZD | kod: `PamiecPul.sprzataj` -> `PamiecPuli.sprzataj` wolane w procesie roboczym przy starcie (S:1134-1140), parametr z A:540 |
| M10 | pamiec_puli.md:58 "a katalog nie ma limitu rozmiaru" | PP:285-299 | ZGODNE | |
| M11 | pamiec_puli.md:59 "Paczka ... musi: wolac `sprzataj(dni)` (przy starcie albo przy odswiezeniu puli)" | S:1134-1140, S:1507 | ZGODNE | |
| M12 | pamiec_puli.md:59-60 "ustalic limit rozmiaru katalogu (najstarsze `mtime` pierwsze)" | PP:285-299 | BRAK W KODZIE | `sprzataj` usuwa tylko po wieku; brak limitu rozmiaru |
| M13 | pamiec_puli.md:62-63 "pierwszy start po aktualizacji to zimna pula (ok. 0,9 s na wpis) - budowac ja w tle po aktualizacji programu" | S:1374-1382, S:1155-1160; A:842 | ZGODNE | |
| M14 | pamiec_puli.md:63-64 "a `sprzataj` wolac przy starcie i od razu usuwac pliki ze starym odciskiem" | PP:285-299, PP:116-117 | BRAK W KODZIE | odcisk jest w nazwie pliku, ale `sprzataj` go nie sprawdza - stare wpisy znikaja dopiero po `dni` (30) |

## 7. samokontrola.md

| Nr | Opis (plik:linia) - cytat | Kod (plik:linia) | Status | Uwagi / co mowi kod |
|---|---|---|---|---|
| K1 | samokontrola.md:43-45 "`wykonaj` nie rzuca wyjatku ... i nie wisi: ... sprawdzenie niezakonczone w swoim limicie czasu - BLAD (... ramki i Excel: OSTRZEZENIE), a pozostale sa wykonywane" | SK:1289-1330, SK:293-313, SK:103 | ZGODNE | |
| K2 | samokontrola.md:46-48 "wywolanie trwa do kilku sekund (ramki, foldery sieciowe) - wolac poza watkiem okna; kazde sprawdzenie dziala w watku pomocniczym, a watek, ktory nie skonczyl w limicie ..., zostaje w tle do konca procesu" | SK:293-313, SK:1311-1316 | ZGODNE | sprawdzenia ida po kolei; gorna granica = suma limitow (15 x 30 s + 120 s + 10 s + 5 s wstepnie = ok. 585 s); program samokontroli nie wola (brak wywolan w A i K) |
| K3 | samokontrola.md:59 "`folder_skanera` ... brak odpowiedzi w 5 s" | SK:106, SK:501-506, SK:532 | ZGODNE | |
| K4 | samokontrola.md:63 "`dane_folder` ... folder danych nie odpowiada w 5 s" | SK:1305-1307, SK:1343-1346 | ZGODNE | |
| K5 | samokontrola.md:66 "`baza` ... baza zajeta; ...; `quick_check` nie zmiescil sie w 4 s" | SK:110, SK:698-705, SK:753-763 | ZGODNE | |
| K6 | samokontrola.md:70 "`GET /stan` pod `[ramki] wieczorna_host`:`port`, limit 3 s" | SK:104, SK:1047, SK:1071 | ZGODNE | zewnetrzny limit 3,5 s (SK:1071) |
| K7 | samokontrola.md:73 "`egzemplarz` - czy program dziala teraz na tej bazie (blokada `<baza>.blokada`) i czy baza byla zajeta" | SK:784-813, SK:816-828 | ZGODNE | |
| K8 | samokontrola.md:76-78 "limit czasu sprawdzenia: 30 s, `moduly` 120 s, `excel` 10 s; ... `ramka_wieczorna`, `ramka_poranna` i `excel` maja po limicie OSTRZEZENIE" | SK:97-103, SK:1315, SK:1326-1329, SK:1333-1335 | ZGODNE | |
| K9 | samokontrola.md:79-80 "Gdy folder danych nie odpowiada w 5 s: `dane_folder` = BLAD, a `dane_miejsce`, `baza`, `pula`, `pamiec_puli`, `egzemplarz` = OSTRZEZENIE" | SK:1283, SK:1305-1313, SK:1343-1348 | ZGODNE | |
| K10 | samokontrola.md:146 "Folder sieciowy, ktory nie odpowiada w 5 s (`LIMIT_FOLDERU_S`), jest traktowany jak brak; cztery foldery sa sprawdzane rownolegle" | SK:106, SK:501-506, SK:293-313 | ZGODNE | |
| K11 | samokontrola.md:176-177 "`quick_check` ma limit 4 s - krotszy niz czekanie programu na baze (5 s), wiec samokontrola uruchomiona obok pracujacego programu nie powoduje w nim \"nie zapisano\"" | SK:110, SK:698-705; B:45; K:119, K:3483-3488, K:3560, K:113, K:2299 | ROZJAZD | 5 s dotyczy tylko zapisu wynikow / dziennika; polecenia okna czekaja 200 ms (K:119, K:3483), zdarzenia ramek 150 ms (K:113, K:2299) - decyzja kliknieta w czasie quick_check (do 4 s blokady odczytu) moze dostac odmowe `baza_zajeta` i komunikat "Decyzja NIE zostala zapisana" (K:3487-3488, K:3560) |
| K12 | samokontrola.md:181-183 "Jedyny zapis: plik probny ... (jedno `os.open` z nowa nazwa - bez `tempfile.mkstemp`, ktore ... ponawia probe 2^31 razy i wisi)" | SK:540-558 | ZGODNE | do PROBY_PLIKU_PROBNEGO = 3 nazw, tylko przy FileExistsError (SK:122, SK:546-551) |
| K13 | samokontrola.md:189-190 "proba zajmuje blokade pliku `<baza>.blokada` na ulamek milisekundy i od razu ja zwalnia" | SK:784-813 | ZGODNE | |
| K14 | samokontrola.md:205-212 "`LIMIT_SPRAWDZENIA_S` 30 s, `moduly` 120 s ..., `excel` 10 s ... `LIMIT_RAMKI_S` 3 s ..., `LIMIT_FOLDERU_S` 5 s ..., `LIMIT_LICZENIA_S` 5 s ..., `LIMIT_QUICK_CHECK_S` 4 s, `CZEKAJ_NA_BAZE_MS` 1000" | SK:97-112, SK:896-905, SK:964-973, SK:677-679 | ZGODNE | |
| K15 | samokontrola.md:213-215 "wisial ponad 2 godziny ... nie dala wyniku w 60 s ... caly proces 2,6 s" | - | NIE DA SIE USTALIC | pomiar |
| K16 | samokontrola.md:217-218 "`czas_s` 2,1-2,3 s ... z proba nieobecnych ramek 5,0 s" | - | NIE DA SIE USTALIC | pomiar |
| K17 | samokontrola.md:223 "prawdziwe polecenie ... w osobnym procesie ponizej 20 s" | - | NIE DA SIE USTALIC | test, nie uruchamiano |
| K18 | samokontrola.md:244-245 "Limit czasu sprawdzenia nie przerywa watku, tylko przestaje na niego czekac: w poleceniu konczy sie razem z procesem, a przy wywolaniu `wykonaj` z programu zostaje w tle" | SK:293-313 (SK:307 daemon=True) | ZGODNE | |

## 8. README.md (opisy_modulow)

| Nr | Opis (plik:linia) - cytat | Kod (plik:linia) | Status | Uwagi |
|---|---|---|---|---|
| R1 | README.md:19 scanner "nadrabianie po restarcie (`ZnanePliki`)" | SC:218-234, SC:431-458 | ZGODNE | |
| R2 | README.md:20 silnik "awaria = komunikat i nastepne zadanie" | S:1739-1750, S:1669-1678 | ZGODNE | "petla Qt bez zamrozenia" - test, nie uruchamiano |
| R3 | README.md:21 aplikacja "nadrabianie i wznowienie po restarcie ...; jeden egzemplarz na baze, zapis ponawiany przy bledzie dysku / bazy" | A:549-559, A:258-307, A:1375-1405 | ZGODNE | |

---

## USTAWIENIA CZASOWE

Walidacja: U:_waliduj (U:242-345). Typ: float przyjmuje int, nie bool (U:234-239); NaN / inf = blad (U:266-267).
"Brak klucza" w sekcjach [sesja], [scanner], [silnik], [ramki] odpowiednich kluczach [excel] = wartosc z DOMYSLNE_NOWYCH
(U:156-192, U:198-213); w [match] klucze wymagane (brak = BladUstawien "brak klucza", U:259-261).

| Klucz | Domyslnie T | Domyslnie U | Walidacja zakresu; 0 / ujemne / brak klucza | Uzycia w kodzie zakresu |
|---|---|---|---|---|
| [silnik] limit_zadania_s | 600.0 (T:120) | 600.0 (U:190) | U:341 > 0; 0 i ujemne = BladUstawien; brak = 600.0. Mala wartosc dopuszczona (np. 0,001 = kazde zadanie limit_czasu, budowa puli zabijana po min(x, 120 s)) | A:536 -> S:1219, S:1225, S:1504 -> S:1101, S:1107 (Straznik + 30 s, S:368), S:1599 (min z 120 s), S:1674, S:1678 |
| [silnik] czekaj_na_plik_s | 60.0 (T:121) | 60.0 (U:190) | U:342 >= 0; 0 dopuszczone = `plik_niedostepny` przy pierwszej nieudanej probie kopii, bez ponowien (S:640); ujemne = blad; brak = 60.0 | A:537 -> S:1221, S:1229, S:1504 -> S:1101, S:1178 -> S:1036, S:1052 -> S:609, S:640-641, S:647 |
| [silnik] ponow_plik_niedostepny | 3 (T:123) | 3 (U:190) | U:343 >= 0; 0 = bez ponowien (warunek A:1479 falszywy, skan `blad` od razu); ujemne = blad; brak = 3 | A:476, A:1479, A:1482 |
| [silnik] pamiec_linii | true (T:122) | True (U:190) - INNA niz domyslna modulu silnik (None = wylaczona, S:1220, S:1227) | tylko typ bool (U:263); brak = True | A:537 -> S:1227, S:1503 -> S:1100, S:1126, S:1161-1165 |
| [silnik] pamiec_puli_dni | 30 (T:125) | 30 (U:191) | U:344 >= 0; 0 = bez sprzatania (A:540 -> None); brak = 30. Dziala tylko przy pula_wpisow = true (A:540) - komentarz T:125 tego nie mowi | A:509, A:540 -> S:1223, S:1253, S:1507 -> S:1102, S:1134-1140, S:1692; SK:1021, SK:1033 |
| [scanner] stabilizacja_ms | 300 (T:112) | 300 (U:184) | U:336 >= 0; 0 dopuszczone (plik oceniany w kolejnym obiegu po ustaleniu podpisu, SC:588-596); brak = 300 | A:560 -> SC:288, SC:297, SC:595 |
| [scanner] obserwator | "watchdog" (T:117; komentarz: "przeglad folderu co 2 s") | "watchdog" (U:185) | U:340 tylko watchdog / odpytywanie; brak = watchdog | A:561 -> SC:291-293, SC:306, SC:465; okres przegladu PRZEGLAD_S = 2,0 s (SC:75) niekonfigurowalny |
| [ramki] odpytywanie_s | 25.0 (T:101) | 25.0 (U:181) | U:305 [0,5; 25]; poza = blad; brak = 25.0 | w zakresie tylko walidacja; poza zakresem: indicate.py:1301 |
| [excel] odswiez_co_min | 5.0 (T:93) | 5.0 (U:164) | U:320 > 0; brak = 5.0 | poza zakresem: excel.py:297 |
| [excel] maks_wiek_dni | 60 (T:94) | 60 (U:165) | U:321 >= 0; 0 = bez limitu; brak = 60 | poza zakresem: excel.py:297 |
| [sesja] przechowuj_skany_dni | 0 (T:105) | 0 (U:182) | U:325 >= 0; 0 = nie usuwac; brak = 0 | brak uzycia (U:115 PRZYSZLY) - tylko walidacja |
| [sesja] granica_doby_godz | 6 (T:106) | 6 (U:182) | U:326 0..23; U:330-331 musi = zmiany_start_godz[0]; brak = 6 | PL:365; poza zakresem: session.py:301, metryki.py:142 |
| [sesja] zmiany_start_godz | [6, 14, 22] (T:107) | [6, 14, 22] (U:182) | U:327-331 niepusta, rosnaca, 0..23, pierwsza = granica; brak = domyslna | poza zakresem: session.py:301, metryki.py:142 |
| [sesja] ponowny_skan_okno_min | 60 (T:108) | 60 (U:183) | U:332 > 0; brak = 60 | poza zakresem: session.py:302 |
| [match] pula_wieczor_dni | 2 (T:51) | brak domyslnej (klucz wymagany; stala PL:49 = 2 tylko dla argumentow funkcji) | U:60 tylko typ int; brak = BladUstawien; 0 / ujemne przechodza ustawienia, PL:124-125 ValueError -> w watku pula-katalog lapane (A:757-758) -> pula bez zmian, ponowienie co 60 s (A:828) | PL:363, PL:345, PL:373, PL:420, PL:428 |
| [match] pula_rano_dni_roboczych | 4 (T:52) | brak (wymagany; PL:50 = 4) | U:61 tylko typ int; brak = blad; ujemne -> PL:238-239 ValueError (jak wyzej); 0 dopuszczone | PL:364, PL:346, PL:424 |
| [match] usun_z_puli_po_dniach | 10 (T:53) | brak (wymagany; PL:51 = 10, I:44 = 10) | U:62 tylko typ int; brak = blad; BRAK kontroli zakresu - 0 i ujemne przyjete (I:193: granica >= teraz, kazdy folder "stary"; PL:242) | PL:364, PL:347, PL:380 -> I:178, I:193; PL:425 -> PL:242 |

Parametry czasu / liczby prob BEZ klucza w ustawieniach (tylko stale; aplikacja ich nie przekazuje - A:535-540, A:557-561):
scanner odrzuc_po_s 5 (SC:73), okres_s 0,05 (SC:74), przeglad_s 2 (SC:75), informuj_po_s 10 (SC:80), informuj_co_s 60 (SC:81);
silnik limit_startu_s 180 (S:80), limit_uruchomienia_s 30 (S:81), proby_uruchomienia 3 (S:82), pul_w_pamieci 2 (S:90);
pamiec_puli limit_ciezkich 64 (PP:42).

---

## W KODZIE, A NIE W OPISIE

| plik:linia | stala | do czego |
|---|---|---|
| S:91 | OKRES_S = 0.02 | co ile nadzorca zaglada do lacza z procesem (S:1582) |
| S:932 | watek.join(0.05) | petla przerywania zawieszonego `Process.start()` |
| S:950 | p.join(5.0) | zamkniecie procesu porzuconej proby startu |
| S:1271 | stop(czekaj_s=5.0) | czekanie `stop()` na watek nadzorcy (opis wymienia `czekaj_s` bez wartosci) |
| S:1372 | time.sleep(0.02) | petla `czekaj_na_pusta_kolejke` |
| S:1411 | time.sleep(0.2) | przerwa po wyjatku w kroku nadzorcy (opis l. 83 wspomina 0,2 s tylko jako stan sprzed E3-A2p) |
| S:1463 | w.join(0.05) | petla czekania na `Process.start()` |
| S:1540 | p.join(5.0) | po zabiciu procesu, gdy `stop()` ruszyl w trakcie startu |
| S:1554 | p.join(2.0) | grzeczne zamkniecie procesu roboczego (wiadomosc "koniec") |
| S:1559 | p.join(5.0) | po `kill()` procesu roboczego |
| S:1575 | time.sleep(0.05) | po nieudanym starcie, gdy kolejka pusta |
| S:1774, S:1802 | okres_ms = 30; range(200) | `silnik.lacznik_qt`: zegar i najwyzej 200 zdarzen na tykniecie (aplikacja uzywa kontroler_api.lacznik_qt) |
| A:75 | OKRES_KONTROLI_S = 1.0 | okres kontroli w `przetworz` (skaner, katalog, DLL) i pierwszy odstep ponowienia zapisu (opis podaje nazwe, nie wartosc) |
| A:147, A:152 | maks = 0x2000 | `uchwyty_knowndlls`: przeglad ok. 2047 uchwytow `NtQueryObject` przy starcie w watku okna (A:541) |
| A:326 | FiltrNazw.LIMIT = 4000 | ile nazw plikow pamieta filtr logu |
| A:1004 | 5.0 | ta sama smierc procesu w ciagu 5 s = jeden zestaw wpisow diagnostyki KnownDlls |
| A:1586 | maxBytes = 2 MB, backupCount = 5 | rotacja stanowisko.log |
| K:110 | CZAS_NA_POLACZENIE_RAMEK_S = 2.0 | opis podaje nazwe bez wartosci |
| K:111 | OKRES_PONOWIENIA_PLANU_S = 2.0 | opis podaje nazwe bez wartosci |
| K:123 | ZALEGLE_EXCELA_H = 48 | opis podaje nazwe bez wartosci |
| K:124 | ZALEGLE_EXCELA_PIECE = 5 | najwyzej tyle zaleglych piecow Excela przy starcie |
| K:129 | PAMIEC_ODRZUCEN_DNI = 2 | z ilu dni wstecz czytane odrzucone propozycje ponownego skanu |
| K:130 | LIMIT_KOMUNIKATOW = 50 | najwyzej tyle komunikatow ulotnych w pamieci (K:3404) |
| SC:349 | stop(czekaj_s=5.0) | czekanie na watek obserwatora (opis bez wartosci) |
| SC:512 | obs.join(2.0) | zatrzymanie watku watchdog |
| SC:547-549 | min(przeglad_s, 0.5) | odstep petli obserwatora bez kandydatow (0,5 s) |
| SC:550 | max(0.005, ...) | najkrotszy odstep petli obserwatora |
| PP:43 | LIMIT_LEKKICH = 4000 | czesci lekkich w pamieci procesu (PP:169-170) |
| SK:111 | KROK_QUICK_CHECK = 20000 | co tyle krokow SQLite sprawdzany limit 4 s |
| SK:122 | PROBY_PLIKU_PROBNEGO = 3 | proby nazw pliku probnego (opis: "jedno os.open") |
| SK:965 | LIMIT_LICZENIA_S + 1.0 | zewnetrzny limit liczenia STL puli (6 s) |
| SK:1071 | limit + 0.5 | zewnetrzny limit proby ramek (3,5 s) |

Czasy wynikowe (z polaczenia stalych, nieopisane jako calosc):
- silnik nie startuje (Process.start wisi): 2 rundy (A:74 + zadanie pierwotne) x 3 proby (S:82) x (do 30 s + do 3 s przerwania) + 0,5 s przerwy (S:81, S:83, S:84) = ok. 200 s do komunikatu `silnik_nie_startuje`; proces startuje, ale nie zglasza gotowosci: 2 x limit_startu_s 180 s (S:1594-1597, bez 3 prob) = ok. 360 s.
- plik skanu trwale zajety: (1 + 3 ponowienia) x czekaj_na_plik_s 60 s (A:476, A:1479; S:99) = ok. 240 s do skanu `blad`.
- zamkniecie programu w najgorszym razie: ramki ok. 1 s + scanner.stop 5 s + watchdog 2 s + silnik.stop 5 s + zamkniecie procesu 2 s + 5 s = ok. 20 s (A:1511-1527, SC:349, SC:512, S:1271, S:1554, S:1559).
- samokontrola: suma limitow ok. 585 s (patrz K2).
