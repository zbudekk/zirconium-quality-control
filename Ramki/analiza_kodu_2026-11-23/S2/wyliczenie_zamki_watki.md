# S2 - wyliczenie: zamki, watki, procesy, sygnaly Qt, praca w watku okna

Zakres: stanowisko/stanowisko/{silnik, aplikacja, kontroler_api, scanner, baza, pula, pamiec_puli, indeks, ustawienia,
samokontrola, __init__}.py. Pliki ui/*.py czytane wylacznie wyrywkowo, zeby ustalic watek wywolania (okno.py 120-199,
505-579, 880-924; obraz.py 75-148; czesci.py 535-569; grep w ekran_rano.py, kandydaci.py, okno_excela.py).
Wyliczenie, bez oceny wagi. Numery linii z narzedzia Read. "poza zakresem" = metoda z pliku spoza listy (session,
session_rano, indicate, excel, wspolczynniki, uklad) - jej wnetrza nie wyliczano.

---------------------------------------------------------------------------------------------------------------------

## 1. ZAMKI (utworzenia)

| # | plik:linia utworzenia | nazwa atrybutu | typ | co chroni (wg komentarza / kodu) |
|---|---|---|---|---|
| 1 | silnik.py:652 | `_ZAMEK_OBIEKTU` (modul) | threading.Lock | utworzenie jednego na proces obiektu zadania Windows `_OBIEKT_ZADANIA` (651, 700-703) |
| 2 | silnik.py:723 | `_ZAMEK_WINAPI` (modul) | threading.Lock | jednorazowa podmiana `popen_spawn_win32._winapi` na `_WinapiZFlagami` (839-848) |
| 3 | silnik.py:736 | `ProbaStartu.zamek` | threading.Lock | stan jednej proby Process.start(): `pid`, `uchwyt`, `w_obiekcie_zadania`, `blad_obiektu`, `porzucona` (728, 737-741); wspolny dla watku silnik-start i nadzorcy |
| 4 | silnik.py:1234 | `Silnik._zamek` | threading.Lock | `_kolejka`, `_po_stopie`/`_zatrzymany`, `_lista_zebrana`, `_biezace`, `_zglaszane`, zamiana `_proces`/`_lacze`/`_gotowy`, pula w tle `_pula_zadana`/`_pula_w_toku`/`_pula_gotowa`/`_pula_proby` (D-N3, D-N4, D3; komentarze 1328, 1545, 1606) |
| 5 | silnik.py:1235 | `Silnik._stop` | threading.Event | flaga zatrzymania watku silnik-nadzorca (petla 1406) |
| 6 | silnik.py:1440 | `zamek` (lokalny w `_start_z_limitem`) | threading.Lock | slownik `stan` ("blad" / "uruchomiony" / "porzucony") miedzy watkiem silnik-start a nadzorca |
| 7 | aplikacja.py:331 | `FiltrNazw._zamek` | threading.Lock | `_znane` (OrderedDict nazwa pliku -> sha16, do 4000 wpisow, 326, 330); filtr jest jeden na proces (`FILTR_NAZW` 392) i dziala w kazdym watku, ktory loguje |
| 8 | aplikacja.py:273 (open), 278 / 282 (lock) | `BlokadaStanowiska._fd` (plik `<baza>.blokada`, 265) | plik-blokada: msvcrt.locking LK_NBLCK (Windows) / fcntl.flock LOCK_EX\|LOCK_NB | jeden egzemplarz programu na plik bazy (B1, 259-261); trzymana przez caly czas pracy procesu |
| 9 | scanner.py:310 | `Scanner._zamek_watchdog` | threading.Lock | `_watchdog` (Observer) - start / stop obserwatora watchdog (460-514) |
| 10 | scanner.py:312 | `Scanner._budzik` | threading.Event | pobudka watku obserwatora (zdarzenia watchdog 481/492, stop 354) |
| 11 | scanner.py:313 | `Scanner._stop` | threading.Event | flaga zatrzymania watku obserwatora |
| 12 | scanner.py:315 | `Scanner._zamek_watku` | threading.Lock | start / koniec watku: `_watek`, `_watek_konczy`, `_stop.clear()` (D11, 334-347, 534-539) |
| 13 | baza.py:512 | `Baza.transakcja()` -> `BEGIN IMMEDIATE` | blokada pliku SQLite (RESERVED do COMMIT) | atomowosc zapisu ("calosc albo nic", 508); czekanie na cudza blokade = `PRAGMA busy_timeout` (324; domyslnie `CZEKAJ_NA_BLOKADE_MS` = 5000, 45; zmieniane przez `Baza.czekanie` 479-489 i kontroler_api.py:2299) |
| 14 | baza.py:384 | `_migruj` -> `BEGIN IMMEDIATE` | blokada pliku SQLite | migracja schematu (jedna transakcja na wersje) |
| 15 | samokontrola.py:798 / 807 | sonda `_blokada_trzymana` na pliku `<baza>.blokada` | msvcrt.locking LK_NBLCK / flock LOCK_NB, zwalniana od razu (802 / 810) | sprawdzenie, czy program dziala; zamka nie trzyma |

Obiekty pokrewne (nie zamki, ale z wewnetrzna synchronizacja albo wspoldzielone miedzy watkami):

| plik:linia | nazwa | typ | uwaga |
|---|---|---|---|
| silnik.py:722 | `_PROBA_STARTU` | threading.local | dane watku silnik-start; nie zamek |
| silnik.py:1231 | `Silnik.zdarzenia` | queue.Queue (bez limitu) | nadzorca -> watek okna (put 1398, get_nowait aplikacja.py:1150, 1533) |
| aplikacja.py:481 | `Aplikacja._skrzynka` | queue.Queue (bez limitu) | watki scanner / pula-* -> watek okna |
| scanner.py:304 | `Scanner.zdarzenia` | queue.Queue (bez limitu) | uzywana tylko bez funkcji zwrotnych (748); Aplikacja podaje funkcje |
| scanner.py:311 | `Scanner._zmiany` | collections.deque | watek watchdog (append 480-489) -> watek scanner (popleft 560); bez zamka |
| ustawienia.py:369 | `domyslne()` | functools.lru_cache(maxsize=1) | brak jawnego zamka |
| kontroler_api.py | - | - | brak jakiegokolwiek zamka (kontrakt: wszystko w watku okna, 20-23) |
| pula.py, pamiec_puli.py, indeks.py, ustawienia.py, __init__.py | - | - | brak zamkow watkow (indeks.py: transakcje SQLite 241, 298 - w tabeli 2d) |

---------------------------------------------------------------------------------------------------------------------

## 2. UZYCIA ZAMKOW

Wszystkie wejscia to `with x:` - acquire BEZ limitu czasu (zadnego `acquire(timeout=...)` w zakresie).

### 2a. Zamki watkow (Lock)

| # | plik:linia | funkcja (watek) | timeout | wywolania pod zamkiem, ktore moga trwac / blokowac |
|---|---|---|---|---|
| 1 | silnik.py:1282 | `Silnik.stop` (watek okna: aplikacja.py:1527) | nie | tylko flagi 1283-1285 |
| 2 | silnik.py:1294 | `Silnik.stop` (watek okna) | nie | `list(self._kolejka)` 1296, `clear` 1297 - krotkie |
| 3 | silnik.py:1328 | `Silnik.zlec` (watek okna: aplikacja.py:1301) | nie | `dataclasses.replace` 1330/1338, `deque.append` 1332/1338, `raise SilnikZatrzymany` 1333/1335 - krotkie |
| 4 | silnik.py:1349 | `Silnik.anuluj` (watek okna: aplikacja.py:1032, 1288) | nie | przeglad i `remove` z deque 1350-1352 - O(dlugosc kolejki) |
| 5 | silnik.py:1366 | `Silnik.czekaj_na_pusta_kolejke` (nie wolana w pakiecie - grep) | nie | odczyt 1367; `time.sleep(0.02)` 1372 POZA zamkiem |
| 6 | silnik.py:1380 | `Silnik.przygotuj_pule` (watek okna: aplikacja.py:908, 917) | nie | porownanie dataclass `opis != self._pula_zadana` 1381 (krotka `wpisy`, slownik `sciezki` - CPU proporcjonalne do liczby wpisow) |
| 7 | silnik.py:1533 | `Silnik._proba_uruchomienia` (nadzorca) | nie | przypisania 1535-1537; `p.kill`/`p.join(5.0)` 1539-1540 POZA zamkiem |
| 8 | silnik.py:1545 | `Silnik._zamknij_proces` (nadzorca: 1596, 1601, 1676, 1687, 1743; watek okna przez stop 1300) | nie | tylko zamiana 1546-1548; `lacze.send` 1553, `p.join(2.0)` 1554, `p.kill` 1558, `p.join(5.0)` 1559, `p.close` 1562, `lacze.close` 1567 - POZA zamkiem |
| 9 | silnik.py:1606 | `Silnik._krok` (nadzorca) | nie | `popleft` 1609; `_zglos` 1613 i `lacze.send` 1615 POZA zamkiem |
| 10 | silnik.py:1622 | `Silnik._wyslij_pule` (nadzorca) | nie | porownania OpisPuli `opis == self._pula_gotowa` 1624, `self._kolejka[0].pula == self._pula_gotowa` 1626 (CPU); `_zglos` 1629, `lacze.send` 1631 POZA zamkiem |
| 11 | silnik.py:1639 | `Silnik._pula_przerwana` (nadzorca) | nie | porownanie `self._pula_zadana == opis` 1644; `LOG.warning` 1647, `_zglos` 1648 POZA zamkiem |
| 12 | silnik.py:1655 | `Silnik._zakoncz` (nadzorca) | nie | `LOG.info` 1657 POD zamkiem (tylko po stop()): filtr loggera `FiltrNazw.filter` (aplikacja.py:365-389, bierze `FiltrNazw._zamek` 353/358) + uchwyt pliku logu RotatingFileHandler (zamek uchwytu logging + zapis pliku, aplikacja.py:1586) |
| 13 | silnik.py:1664 | `Silnik._zakoncz` finally (nadzorca) | nie | przypisania 1665-1667; `_zglos` 1662 (callback / queue.put) jest MIEDZY 1655 a 1664, poza zamkiem |
| 14 | silnik.py:1720 | `Silnik._odbierz_pule` (nadzorca) | nie | porownanie `self._pula_zadana == opis` 1724; `_zglos` 1732/1736 POZA zamkiem |
| 15 | silnik.py:1756 | `Silnik._nieudany_start_procesu` (nadzorca) | nie | `popleft` 1759; `LOG.error` 1754 PRZED zamkiem; `_zglos` 1762 POZA zamkiem |
| 16 | silnik.py:1764 | `Silnik._nieudany_start_procesu` finally (nadzorca) | nie | przypisanie 1765 |
| 17 | silnik.py:752 | `ProbaStartu.po_utworzeniu` (watek silnik-start, wewnatrz `CreateProcess` z `p.start()` 1445 -> 835) | nie | `_winapi.GetCurrentProcess` 757, `_winapi.DuplicateHandle` 758 (wywolania systemu, krotkie); `_dolacz_do_obiektu_zadania` 749 PRZED zamkiem; `TerminateProcess`/`CloseHandle` 762-767 PO zamku |
| 18 | silnik.py:773 | `ProbaStartu.porzuc` (nadzorca: 910, 1483) | nie | przypisanie 774 |
| 19 | silnik.py:780 | `ProbaStartu.kod_wyjscia` (nadzorca: 1466) | nie | odczyt 781; `GetExitCodeProcess` 787 PO zamku |
| 20 | silnik.py:794 | `ProbaStartu.zamknij_uchwyt` (nadzorca: 1470, 1484) | nie | zamiana 795; `CloseHandle` 800 PO zamku |
| 21 | silnik.py:700 | `_dolacz_do_obiektu_zadania` (watek silnik-start: 749; nadzorca: 1528) | nie | `_utworz_obiekt_zadania()` 702 -> `CreateJobObjectW` 679, `SetInformationJobObject` 684 (ctypes, raz na proces); `OpenProcess`/`AssignProcessToJobObject` 710-717 PO zamku |
| 22 | silnik.py:845 | `_winapi_z_flagami` (nadzorca: 1496) | nie | `isinstance` + przypisanie 846-847; import 843 PRZED zamkiem |
| 23 | silnik.py:1447 | `cel` w `_start_z_limitem` (watek silnik-start) | nie | f-string 1448 |
| 24 | silnik.py:1452 | `cel` w `_start_z_limitem` (watek silnik-start) | nie | odczyt/zapis slownika 1453-1454; `_zamknij_porzucony(p)` 1456 (kill, join 5.0, close 949-951) PO zamku |
| 25 | silnik.py:1485 | `_start_z_limitem` finally (nadzorca) | nie | odczyt/zapis slownika 1486-1487; `_zamknij_porzucony` 1489 PO zamku |
| 26 | aplikacja.py:337 | `FiltrNazw.zapamietaj` (watek okna: 554, 1226; kazdy watek logujacy: 377) | nie | operacje na OrderedDict 338-343 (do 4000) - krotkie |
| 27 | aplikacja.py:353 | `FiltrNazw._argument` (kazdy watek logujacy) | nie | `dict.get` + `Path(...).name` 354 |
| 28 | aplikacja.py:358 | `FiltrNazw.oczysc` (kazdy watek logujacy) | nie | `sorted(...)` do 4000 pozycji 359 (CPU); zamiany i `B.bez_sciezek` 360-363 PO zamku |
| 29 | scanner.py:335 | `Scanner.start` (watek okna: aplikacja.py:562) | nie | `self._stop.clear()` 336 (wewn. zamek Event); `_uruchom_watchdog()` 339/345 -> `_zamek_watchdog` 461 (zagniezdzenie) -> `folder.is_dir()` 465, import watchdog 468-469, `Observer()` 495, `obs.schedule` 496, `obs.start()` 498, `os.stat` 503, `LOG.warning` 471/500; `przygotuj()` 344 -> `folder.is_dir()` 391, `_uruchom_watchdog()` 393, `_ustal_zastane` 394 -> `pliki_w_folderze(self.folder)` 401 (listowanie calego folderu skanera, rekurencyjnie; dysk sieciowy - bez limitu); `threading.Thread(...)` 346, `.start()` 347 |
| 30 | scanner.py:536 | `Scanner._petla` (watek scanner) | nie | `_stop.is_set()` 537, przypisanie 538 |
| 31 | scanner.py:461 | `Scanner._uruchom_watchdog` (watek okna: 339, 345, 393 pod `_zamek_watku`; watek scanner: 531, 635) | nie | `folder.is_dir()` 465, `from watchdog...` 468-469, `LOG.warning` 471/500 (-> FiltrNazw._zamek), `Observer()` 495, `obs.schedule(...)` 496, `obs.start()` 498, `_identyfikator` -> `os.stat` 503/254 - wszystko na folderze skanera (udzial sieciowy = moze stac) |
| 32 | scanner.py:507 | `Scanner._zatrzymaj_watchdog` (watek okna: stop 360; watek scanner: 530, 631) | nie | tylko zamiana 508; `obs.stop()` 511 i `obs.join(2.0)` 512 PO zamku. UWAGA: wejscie z watku okna (360) czeka bez limitu, jesli watek scanner trzyma zamek w 461 (465/495-498/503 na niedostepnym folderze) |

### 2b. Zdarzenia (Event)

| # | plik:linia | funkcja (watek) | timeout | uwagi |
|---|---|---|---|---|
| 33 | silnik.py:1286 | `Silnik.stop` - `self._stop.set()` (watek okna) | - | potem `w.join(czekaj_s)` 1289 (domyslnie 5.0) |
| 34 | silnik.py:1419 | `Silnik._uruchom_proces` - `self._stop.wait(0.5)` (nadzorca) | tak, `ODSTEP_PROB_URUCHOMIENIA_S` = 0.5 (83) | `is_set()` (bez czekania): 1406, 1421, 1427, 1462, 1472, 1516 |
| 35 | scanner.py:550 | `Scanner._petla` - `self._budzik.wait(...)` (watek scanner) | tak, `max(0.005, czekaj)` <= 0.5 s (545-549) | `clear()` 551 |
| 36 | scanner.py:354 / 481 / 492 | `_budzik.set()` (watek okna w stop; watek watchdog w `on_any_event`) | - | - |
| 37 | scanner.py:336 | `Scanner.start` - `self._stop.clear()` POD `_zamek_watku` (watek okna) | - | wewnetrzny zamek Event, trywialny |
| 38 | scanner.py:353 | `Scanner.stop` - `self._stop.set()` (watek okna) | - | potem `w.join(czekaj_s)` 357 (domyslnie 5.0); `is_set()` 537, 598, 676, 705 |

### 2c. Plik-blokada

| # | plik:linia | funkcja (watek) | timeout | uwagi |
|---|---|---|---|---|
| 39 | aplikacja.py:278 / 282 | `BlokadaStanowiska.zajmij` (watek glowny = watek okna: 454 w `__init__`, 1692 w `main`) | nieblokujace (LK_NBLCK / LOCK_NB) - od razu `ProgramJuzDziala` 285 | trzymana do `zwolnij`: 1564 (zamknij), 1714 (blad startu), 458 / 465 (blad konstruktora) |
| 40 | aplikacja.py:303 | `BlokadaStanowiska.zwolnij` | - | `os.lseek` 302, `LK_UNLCK` 303, `os.close` 307 |
| 41 | samokontrola.py:798 / 807 | `_blokada_trzymana` (watek samokontrola-*) | nieblokujace | zwolnienie od razu 802 / 810; w tej chwili `zajmij` programu dostalby `ProgramJuzDziala` (bez czekania) |

### 2d. Transakcje SQLite (BEGIN IMMEDIATE, czekanie = busy_timeout polaczenia)

| # | plik:linia | funkcja (watek, polaczenie) | timeout | wywolania pod transakcja |
|---|---|---|---|---|
| 42 | baza.py:512 | `Baza.transakcja` (kazdy) | busy_timeout polaczenia (domyslnie 5000 ms) | to, co w bloku `with` wolajacego; COMMIT 515 tez moze czekac |
| 43 | baza.py:384 | `_migruj` (watek okna przy `B.otworz` w aplikacja.py:456) | 5000 ms | DDL `MIGRACJE` 385-387; wczesniej poza transakcja `shutil.copy2` 377 (kopia calego pliku bazy) i porownanie plikow 355-363 |
| 44 | aplikacja.py:1418 | `Aplikacja._zapis_w_bazie` (watek okna, polaczenie sesji) | 5000 ms - BEZ `_czekanie_okna` (wolane z przetworz 1146/1155, ponow_zapis 1458, zamknij 1537/1539) | `_skan_z_wynikiem` SELECT 1419/1244; `baza.zdarzenie` 1421, 1434; `self.rano.przyjmij_wynik` 1424 / `self.sesja.przyjmij_wynik` 1426 / `przyjmij_blad` 1430, 1432 (poza zakresem); `_zapisz_podglad` 1427 (INSERT kontroler_api.py:2101). Ramka (1436-1440) PO transakcji |
| 45 | kontroler_api.py:2346 | `_zdarzenia_ramki.zapisz_serie` (watek okna; busy 150 ms z 2250/2299) | 150 ms (`CZEKAJ_ZDARZENIA_MS` 113) | `_zdarzenie_ramki` 2349 -> `self.rano.otwarty_piec()` 2457, `_kuweta_z_ramki` 2462 -> `k.potwierdzone()` 2426 (metoda klienta ramki - indicate, poza zakresem) i `_rozlozone` SELECT 1654; zagniezdzona transakcja 2464 (dolacza do zewnetrznej, 509-511); `_klucz_zapisany` SELECT LIKE 2398; `_wpisz_zdarzenie_ramki` 2402 |
| 46 | kontroler_api.py:2464 | `_zdarzenie_ramki` (watek okna) | 150 ms (z 2250) | `_klucz_zapisany` 2465, `_wpisz_zdarzenie_ramki` 2467 |
| 47 | kontroler_api.py:2491 | `_zamknij_piec_z_ramki` (watek okna) | 150 ms (z 2250) | `_klucz_zapisany` 2492; `_zajety()` 2498-2499 (`scanner.stan()` przez `_stan_zywy`); `self.rano.zamknij_piec(...)` 2502 (poza zakresem); `_wpisz_zdarzenie_ramki` 2506. `self.rano.otwarty_piec()` 2490 tuz przed |
| 48 | kontroler_api.py:2514 | `_zamknij_piec_z_ramki` po bledzie (watek okna) | 150 ms | `_klucz_zapisany` 2515, `_wpisz_zdarzenie_ramki` 2516 |
| 49 | kontroler_api.py:4302 | `indeks_rano_sztuczny` (atrapa, watek okna) | 5000 ms | `wstaw` x N 4305-4309, `miniatura_sztuczna` 4312 (CPU, PNG 64x64) |
| 50 | kontroler_api.py:4352 | `indeks_sztuczny` (atrapa, watek okna) | 5000 ms | `wstaw` x 3N 4354-4359 |
| 51 | indeks.py:241 | `indeksuj` (watek pula-katalog, wlasne polaczenie z pula.py:361) | 5000 ms | 2 x UPDATE 242-243 |
| 52 | indeks.py:298 | `_folder` (watek pula-katalog, wlasne polaczenie) | 5000 ms | INSERT/UPDATE 300-324; odczyt pliku 273 i cechy siatki 280-282 PRZED transakcja (komentarz 252) |

---------------------------------------------------------------------------------------------------------------------

## 3. ZAGNIEZDZENIA (pod jednym zamkiem drugi; do 2 poziomow wywolan, logging liczony jako wywolanie)

| # | zamek zewnetrzny (plik:linia wejscia) | droga | zamek wewnetrzny (plik:linia wejscia) |
|---|---|---|---|
| 1 | `Scanner._zamek_watku` scanner.py:335 | `_uruchom_watchdog()` 339 | `Scanner._zamek_watchdog` scanner.py:461 |
| 2 | `Scanner._zamek_watku` scanner.py:335 | `przygotuj()` 344 -> `_uruchom_watchdog()` 393 | `Scanner._zamek_watchdog` scanner.py:461 |
| 3 | `Scanner._zamek_watku` scanner.py:335 | `_uruchom_watchdog()` 345 | `Scanner._zamek_watchdog` scanner.py:461 |
| 4 | `Scanner._zamek_watchdog` scanner.py:461 | `LOG.warning` 471 / 500 -> filtr loggera "stanowisko.scanner" (aplikacja.py:314, 1584) -> `FiltrNazw.filter` 365 -> `_argument` / `oczysc` | `FiltrNazw._zamek` aplikacja.py:353 / 358 |
| 5 | `Scanner._zamek_watku` scanner.py:335 | jak #4, przez 339/345/393 -> 461 -> 471/500 (3 poziomy) | `FiltrNazw._zamek` aplikacja.py:353 / 358 |
| 6 | `Silnik._zamek` silnik.py:1655 | `LOG.info` 1657 -> filtr loggera "stanowisko.silnik" -> `FiltrNazw.filter` 365 -> `_argument` 378 / `oczysc` 379 | `FiltrNazw._zamek` aplikacja.py:353 / 358 |
| 7 | `Silnik._zamek` silnik.py:1655 | `LOG.info` 1657 -> uchwyt RotatingFileHandler (aplikacja.py:1586-1589) `emit` | zamek uchwytu logging (biblioteka standardowa; zapis pliku logu) |
| 8 | `Scanner._zamek_watku` scanner.py:335 | `self._stop.clear()` 336 | wewnetrzny Condition `Scanner._stop` (biblioteka standardowa, trywialny) |
| 9 | transakcja SQLite kontroler_api.py:2346 | `_zdarzenie_ramki` 2349 -> `_kuweta_z_ramki` 2462 -> `k.potwierdzone()` 2426 | zamki klienta ramki (indicate.py - poza zakresem, nieustalone) |
| 10 | transakcja SQLite kontroler_api.py:2491 | `self.rano.zamknij_piec` 2502 | session_rano (poza zakresem; w zakresie brak zamkow watkow) |

Sprawdzone i NIE zagniezdzone: `_dolacz_do_obiektu_zadania` (bierze `_ZAMEK_OBIEKTU` 700) wolane w silnik.py:749 PRZED
`with self.zamek` 752 (kolejno, nie w sobie); `_winapi_z_flagami` (`_ZAMEK_WINAPI` 845) wolane w 1496 bez zadnego zamka;
`_przerwij_start` 1481 i finally 1483-1487 biora `ProbaStartu.zamek` i lokalny `zamek` po kolei; pod `FiltrNazw._zamek`
(337, 353, 358) tylko operacje na slowniku; zadne `_zglos` / `na_zdarzenie` (1401) nie jest wolane pod `Silnik._zamek`;
`Scanner._wyslij` (callback 751) wolane bez zamka.

Lista par (A -> B):
- `Scanner._zamek_watku` -> `Scanner._zamek_watchdog`
- `Scanner._zamek_watku` -> `FiltrNazw._zamek`
- `Scanner._zamek_watchdog` -> `FiltrNazw._zamek`
- `Silnik._zamek` -> `FiltrNazw._zamek`
- `Silnik._zamek` -> zamek uchwytu pliku logu (logging)
- `Scanner._zamek_watku` -> `Scanner._stop` (wewnetrzny Condition)
- (SQLite RESERVED -> klient ramki indicate; SQLite RESERVED -> session_rano - poza zakresem)

Kolejnosc odwrotna (B -> A): NIE ZNALEZIONO w zakresie. Pod `FiltrNazw._zamek` nie jest brany zaden inny zamek; pod
`_zamek_watchdog` nie jest brany `_zamek_watku`; w logging `Handler.handle` wola filtr przed wzieciem zamka uchwytu, a
`emit` RotatingFileHandler nie wola kodu programu.

Czekania krzyzowe miedzy watkami (nie zagniezdzenia, dla kompletu): watek okna `Silnik.stop` czeka na nadzorce
(`join(5.0)` 1289), nadzorca na watek okna nie czeka (`na_zdarzenie` = None w Aplikacji -> `queue.put` 1398 bez limitu
rozmiaru); watek okna `Scanner.stop` czeka na watek scanner (`join(5.0)` 357), watek scanner oddaje zdarzenia przez
`_skrzynka.put` (aplikacja.py:558-559) bez czekania; potem watek okna bierze `_zamek_watchdog` (360 -> 507) bez limitu.

---------------------------------------------------------------------------------------------------------------------

## 4. WATKI I ZEGARY

| # | plik:linia | nazwa / cel (target / slot) | daemon | kto i gdzie konczy |
|---|---|---|---|---|
| 1 | silnik.py:380 | "silnik-straznik" (w PROCESIE ROBOCZYM), `petla` 372 -> `Straznik.sprawdz` 363 + `time.sleep(okres_s)` 378 | tak | nigdy (`while True` 373); ginie z procesem roboczym (sam konczy proces `_zakoncz_proces` 324-341 kody 91/92) |
| 2 | silnik.py:1268 | "silnik-nadzorca", `Silnik._petla` 1405 | tak | `Silnik.stop`: `_stop.set()` 1286 + `w.join(czekaj_s)` 1289 (domyslnie 5.0 s); po limicie zostawiony z wpisem w logu 1290-1292 |
| 3 | silnik.py:1458 | "silnik-start", `cel` 1442 -> `p.start()` 1445 | tak | sam po `p.start()`; nadzorca `w.join(0.05)` w petli do `limit_uruchomienia_s` (30 s, 81) 1462-1463, potem `_przerwij_start` 1481: `CancelSynchronousIo` 931 + `watek.join(0.05)` do `CZEKAJ_NA_PRZERWANIE_S` = 3 s (84, 929-932); dalej zyje = porzucony (940-942) |
| 4 | silnik.py:1796 | QTimer `LacznikQt._zegar`, interwal `okres_ms` (domyslnie 30, 1774 / 1797), slot `oproznij` 1801 | - | `zatrzymaj()` 1819-1820; funkcja `silnik.lacznik_qt` wolana tylko w testach (grep: testy/test_silnik.py:1921) |
| 5 | aplikacja.py:701 | "pula-liczenie", `licz` 694 -> `pliki_stl(folder)` 696 (rglob 399) | tak | nikt (bez join, bez flagi stop); wynik `_skrzynka.put` 699; najwyzej jeden naraz (`_liczenie_puli` 680, 692) |
| 6 | aplikacja.py:761 | "pula-katalog", `licz` 739 -> `KatalogPul.z_ustawien` 745 (wlasne polaczenie z baza), `kp.odswiez` 747 (indeks, CSV, powiazanie), pule 749-750, `kp.zamknij` 752 | tak | nikt (bez join, bez flagi stop); wynik `_skrzynka.put` 759; jeden naraz (`_liczenie_puli` 727, 736) |
| 7 | aplikacja.py:808 | "pula-plik-csv", `sprawdz` 801 -> `stan_pliku` -> `os.stat` 97 | tak | nikt; wynik `_skrzynka.put` 806; jeden naraz (`_csv_w_toku` 797-798, zerowane 814) |
| 8 | aplikacja.py:1722 | `QTimer.singleShot(zamknij_po * 1000, app.quit)` (opcja `--zamknij-po`) | - | jednorazowy |
| 9 | kontroler_api.py:1184 | QTimer `LacznikKontrolera._zegar`, interwal `OKRES_LACZNIKA_MS` = 30 ms (128, 1185), slot `_tyk` 1189 -> `kontroler.przetworz()` 1190 | - | `zatrzymaj()` 1204-1206 (wolane aplikacja.py:1724 po `app.exec`) |
| 10 | scanner.py:346 | "scanner", `Scanner._petla` 534 | tak | `Scanner.stop`: `_stop.set` 353, `_budzik.set` 354, `w.join(czekaj_s)` 357 (domyslnie 5.0); po limicie watek zostaje (`_watek` nie zerowany 358-359), konczy sie sam przy nastepnym sprawdzeniu 536-539 |
| 11 | scanner.py:495 | watchdog `Observer()` (watek biblioteki + emitery), `Odbiornik.on_any_event` 477 | tak (497) | `_zatrzymaj_watchdog`: `obs.stop()` 511 + `obs.join(2.0)` 512 |
| 12 | samokontrola.py:307 | "samokontrola-<klucz>", `uruchom` 299 -> funkcja sprawdzenia | tak | `w.join(max(0, koniec - teraz))` 312 z lacznym limitem (`LIMIT_SPRAWDZENIA_S` 30 s 97, moduly 120 s 98, excel 10 s 100, folder 5 s 106, liczenie puli 5+1 s 964-965, ramki limit+0.5 s 1071); po limicie watek zostaje w tle do konca procesu (295-296) |

Brak w zakresie: QThread, QThreadPool / QRunnable, threading.Timer, ThreadPoolExecutor. (Poza zakresem, informacyjnie:
QThreadPool w ui/obraz.py:108 wola `kontroler_api.wczytaj_podglad` w watku pomocniczym - obraz.py:132.)

---------------------------------------------------------------------------------------------------------------------

## 5. PROCESY

| # | plik:linia | cel | daemon | jak konczony | potoki po smierci procesu |
|---|---|---|---|---|---|
| 1 | silnik.py:1232 | `multiprocessing.get_context("spawn")` | - | - | - |
| 2 | silnik.py:1501 | `self._ctx.Pipe()` -> `rodzic`, `dziecko` (duplex) | - | - | po udanym starcie `dziecko.close()` 1522 w procesie okna (smierc robotnika = EOF); nieudany start: oba konce zamykane 1511-1515; stop w trakcie startu: `rodzic.close()` 1541; `_zamknij_proces` `lacze.close()` 1565-1569 |
| 3 | silnik.py:1502 | `self._ctx.Process(target=_robotnik 1100, name="silnik-analiza", daemon=True, args=(dziecko, ...))`; start `p.start()` 1445 w watku silnik-start, limit 30 s (81, 1462), do 3 prob (82, 1418) | tak | grzecznie: `lacze.send(("koniec",))` 1553 + `p.join(2.0)` 1554; potem `p.kill()` 1558 + `p.join(5.0)` 1559 + `p.close()` 1562 (`_zamknij_proces` 1544-1570); porzucony start: `_zamknij_porzucony` kill / `join(5.0)` / close 949-951; `_winapi.TerminateProcess` 916 (przerwany start); stop w trakcie startu: `p.kill()` 1539 + `p.join(5.0)` 1540; przekroczenie limitu zadania 600 s (79) `_sprawdz_limit` 1669-1678; brak gotowosci po 180 s (80) 1595-1597; budowa puli bez postepu `min(limit_zadania_s, 120 s)` 1599-1602; sam: Straznik (rodzic zniknal / limit + 30 s, 363-369, 104-106); Windows Job Object `KILL_ON_JOB_CLOSE` 683 (dolaczenie 749 / 1528) | nadzorca: `lacze.poll(OKRES_S)` 1582 / `recv()` 1583 -> `EOFError`/`OSError` 1586 -> `_po_smierci_procesu` 1587 / 1739 -> `_zamknij_proces`; `p.is_alive()` False 1590-1591 -> to samo. Robotnik: `recv` `EOFError`/`OSError` -> return 1150-1152; `send` `OSError` -> return 1159, 1190-1193. Zawieszony zapis danych startowych do lacza (bpo-33929, 44-47): `CancelSynchronousIo` 895-901 / 931. `lacze.send` nadzorcy 1553 / 1615 / 1631 bez limitu czasu (Pipe Windows - zapis z czekaniem, gdy bufor pelny) |
| 4 | silnik.py:1106 | `multiprocessing.parent_process()` w robotniku (dla Straznika 1107) | - | - | - |
| 5 | aplikacja.py:1652 | `multiprocessing.freeze_support()` | - | - | - |

subprocess / multiprocessing.Queue / multiprocessing.Lock / Event: BRAK w zakresie.

---------------------------------------------------------------------------------------------------------------------

## 6. SYGNALY Qt I PRZEJSCIA MIEDZY WATKAMI

BlockingQueuedConnection: BRAK (grep calego pakietu stanowisko/stanowisko, takze ui/ - zero wystapien).
Jawne QueuedConnection / DirectConnection: BRAK. QMetaObject.invokeMethod: BRAK. QTimer.singleShot(0, ...): BRAK w zakresie
(w ui: okno.py:181-183, 446 - poza zakresem).

### 6a. Definicje Signal

| # | plik:linia | sygnal |
|---|---|---|
| 1 | kontroler_api.py:1174 | `stan_zmieniony = Signal(object)` |
| 2 | kontroler_api.py:1175 | `postep = Signal(object)` |
| 3 | kontroler_api.py:1176 | `komunikat = Signal(object)` |
| 4 | kontroler_api.py:1177 | `pytanie = Signal(object)` |
| 5 | kontroler_api.py:1178 | `zamkniety = Signal()` |
| 6 | silnik.py:1786 | `gotowy = Signal()` |
| 7 | silnik.py:1787 | `start = Signal(int)` |
| 8 | silnik.py:1788 | `postep = Signal(int, str, float)` |
| 9 | silnik.py:1789 | `wynik = Signal(int, object)` |
| 10 | silnik.py:1790 | `blad = Signal(int, str, str)` |
| 11 | silnik.py:1791 | `zdarzenie = Signal(object)` |

### 6b. connect

| # | plik:linia | polaczenie | typ |
|---|---|---|---|
| 12 | kontroler_api.py:1186 | `QTimer.timeout -> LacznikKontrolera._tyk` | domyslny (Auto; ten sam watek okna) |
| 13 | silnik.py:1798 | `QTimer.timeout -> LacznikQt.oproznij` | domyslny |
| 14 | aplikacja.py:1629 | `lacznik.stan_zmieniony -> OknoZastepcze.pokaz` | domyslny |
| 15 | aplikacja.py:1719 | `app.aboutToQuit -> kontroler.zamknij` | domyslny (funkcja Pythona, wywolanie w watku okna) |

### 6c. emit

| # | plik:linia | emit | watek |
|---|---|---|---|
| 16 | kontroler_api.py:1194 | `stan_zmieniony.emit` | okna (z `_powiadom` 1315-1325, wolanego wylacznie z metod kontrolera) |
| 17 | kontroler_api.py:1196 | `postep.emit` | okna |
| 18 | kontroler_api.py:1198 | `komunikat.emit` | okna |
| 19 | kontroler_api.py:1200 | `pytanie.emit` | okna |
| 20 | kontroler_api.py:1202 | `zamkniety.emit` | okna (z `_powiadom("zamkniety")` aplikacja.py:1566, kontroler_api.py:4578) |
| 21 | silnik.py:1807 | `zdarzenie.emit` | okna (QTimer) |
| 22 | silnik.py:1809 | `gotowy.emit` | okna |
| 23 | silnik.py:1811 | `start.emit` | okna |
| 24 | silnik.py:1813 | `postep.emit` | okna |
| 25 | silnik.py:1815 | `wynik.emit` | okna |
| 26 | silnik.py:1817 | `blad.emit` | okna |

Emit z watku innego niz okna w zakresie: BRAK. (Poza zakresem: ui/obraz.py:95 emit z QRunnable, polaczenie domyslne.)
Polaczenie Auto w tym samym watku = wywolanie bezposrednie: sloty okna wykonuja sie wewnatrz `_powiadom`, czyli wewnatrz
`przetworz` / polecenia kontrolera.

### 6d. QTimer.singleShot

| # | plik:linia | wywolanie |
|---|---|---|
| 27 | aplikacja.py:1722 | `QtCore.QTimer.singleShot(int(args.zamknij_po * 1000), app.quit)` |

### 6e. Przejscia miedzy watkami bez Qt (kolejki / lacze)

| # | plik:linia (nadawca, watek) | odbiorca (plik:linia, watek) | mechanizm |
|---|---|---|---|
| 28 | silnik.py:1398 `self.zdarzenia.put(z)` (nadzorca; takze watek wolajacy stop() 1301) | aplikacja.py:1150 `get_nowait` (okna, przetworz), 1533 (okna, zamknij) | queue.Queue |
| 29 | silnik.py:1401 `self.na_zdarzenie(z)` | funkcja zwrotna w watku nadzorcy; w Aplikacji nieuzywana (Silnik bez `na_zdarzenie`, 535-540) | callback |
| 30 | aplikacja.py:558-559 lambdy `self._skrzynka.put(("skan"/"odrzucenie"/"oczekiwanie", ...))` wolane z scanner.py:751 (watek scanner) | aplikacja.py:1157 (okna), 1521 (okna, zamknij) | queue.Queue |
| 31 | aplikacja.py:699 (pula-liczenie) | aplikacja.py:1157 -> `_pula_policzona` 1215 | queue.Queue |
| 32 | aplikacja.py:759 (pula-katalog) | aplikacja.py:1157 -> `_pula_wpisow_policzona` 1220 | queue.Queue |
| 33 | aplikacja.py:806 (pula-plik-csv) | aplikacja.py:1157 -> `_stan_csv` 1218 | queue.Queue |
| 34 | silnik.py:1045, 1091, 1097, 1130, 1140, 1147, 1191 `lacze.send` (proces roboczy) | silnik.py:1582-1583 `poll` / `recv` (nadzorca) | multiprocessing Pipe |

---------------------------------------------------------------------------------------------------------------------

## 7. CO DZIALA W WATKU OKNA (kontroler_api.py i aplikacja.py)

Watek: wszystkie polecenia ida z ui przez `okno._polecenie` (ui/okno.py:511-536) -> `self.k.wykonaj` (okno.py:519) ->
`Kontroler.wykonaj` (kontroler_api.py:1142-1152); ui/ekran_rano.py:977-979 i ui/okno_excela.py:138-140 przekazuja do
`okno._polecenie`. Wywolania z obslugi przyciskow / klawiszy (sloty Qt w watku okna) albo QTimer. Kontrakt watku:
kontroler_api.py:20-23. Limity: `_czekanie_okna(ms)` (1333-1338 -> baza.py:479-494) ogranicza TYLKO czekanie na blokade
SQLite (busy_timeout); pliki, siec, COM, CPU nie maja limitu w zakresie. Bez `_czekanie_okna` obowiazuje 5000 ms.

### 7a. aplikacja.py

| # | plik:linia metody | skad wolana | operacje blokujace (plik:linia) | limit czasu |
|---|---|---|---|---|
| A1 | aplikacja.py:449 `Aplikacja.__init__` | aplikacja.py:1705 (main, przed app.exec) | blokada pliku 454 (nieblokujaca); `B.otworz` 456 (sqlite + ewent. kopia bazy `shutil.copy2` baza.py:377 i migracja 384); `SE.Sesja.z_ustawien` 461 (poza zakresem); `super().__init__` 462 -> `_wczytaj_tryb` SELECT kontroler_api.py:1624, `_wczytaj_odrzucone` SELECT 1388; `_wczytaj_pule` odczyt pliku 662 | sqlite 5000 ms; kopia pliku bez limitu |
| A2 | aplikacja.py:528 `start` | aplikacja.py:1706 (main) | `mkdir` 533; `_sprzatnij_podglady` 534 -> SELECT zdarzen 607, `iterdir` 613, `unlink` 616; `uchwyty_knowndlls` 541 -> 152 (2047 x `NtQueryObject` 137); `_uklad` 547 -> kontroler_api.py:1465 `U.wczytaj` (plik + numpy); `_wczytaj_zadania` 549 -> 640; SELECT wszystkich skanow 551; `_nowy_skan` 555 (SQL 1244, `_istnieje` 1257); `scanner.start()` 562 -> scanner.py:401 listowanie folderu POD zamkiem, 495-498 watchdog; `zdarzenie` 564; `_podlacz_ramki_i_excel` 569 -> `utworz_ramki` 577/414 (poza zakresem), `self.stan()` 583, `podlacz_ramki` 584 (kontroler_api.py:2067, 2071, 2074 `ramki.uruchom()`), `utworz_excel` 589, `podlacz_excel` 595 (2093 -> SELECT 2820, `rano.wynik_pieca` 2822, SELECT 2829); `_odswiez` 570 | sqlite 5000 ms (poza `_odswiez` 100 ms); listowanie folderow, NtQueryObject, ramki - brak |
| A3 | aplikacja.py:1135 `przetworz` | QTimer kontroler_api.py:1184-1190 (co 30 ms) | ponowienia `_zapisz` 1146 -> 1383 -> transakcja 1418 (BEGIN IMMEDIATE); `_zdarzenie_silnika` 1155 -> `_przyjmij_wynik` 1368 / `_zapisz_blad` 1373 -> 1418; `z.zdarzenie()` 1417 -> 224 -> 209 -> `Path.is_file()` 166 (sciezka skanu w folderze skanera; komentarz 94-95: `os.stat` na niedostepnym hoscie ok. 21 s); `_ramka_w_analiza` 1342 -> `k.analiza()` kontroler_api.py:2651; `_ramka_w_blad` 1440 -> `k.blad()` 2667; `_blad_analizy` 1497 `_istnieje`, `zdarzenie` 1476/1493/1498; `_zdarzenie_puli` 950 `zdarzenie`; `_zdarzenie_skrzynki` 1162 -> `zdarzenie` 1227/1234, `_nowy_skan` 1229 (SELECT 1244, `_istnieje` 1257, `_przejmij_przemianowany` 1281 `_istnieje`, `_ramka_w_nowy_skan` 1272 -> `k.znacznik()` 2636, `silnik.zlec` 1301 pod `Silnik._zamek`), `_pula_wpisow_policzona` -> `silnik.stan()` 910 / `przygotuj_pule` 917 (porownanie OpisPuli pod zamkiem), SQL 849, `_rozstrzygnij_sprawdzenia` 1023/1025; `_kontrola_dll` 1171 -> `silnik.stan()` 989 (`p.is_alive()` silnik.py:1319), `knowndlls_otwarty` 996; `_przetworz_ramki` 1174 (= K34); `_odswiez` 1178 (= K4) | `limit_s` = 0.05 s (kontroler_api.py:127) liczy tylko petle zdarzen (1166) - pojedyncze zdarzenie bez limitu; sqlite 5000 ms w `_zapisz` i `zdarzenie`; plik / ramka / COM - brak |
| A4 | aplikacja.py:1112 `start_skanu` | ui/okno.py:539 (pasek 146, Spacja); aplikacja.py:1644 | `scanner.start_skanu()` 1116 -> akcja scanner.py:368 (atrapa - natychmiast); `zdarzenie` 1122 pod `_czekanie_okna(200)` 1121; `_ramka_w_spacja` 1127 -> `k.skanowanie()` kontroler_api.py:2624; `_odswiez` 1129 / `_odswiez_zywe` 1131 | sqlite 200 ms (1121) / 100 ms; ramka - brak |
| A5 | aplikacja.py:1035 `ustaw_pule` | watek okna przez okno.py:519; bezposredniego wywolania w ui nie znaleziono (tylko lista czesci.py:31) | `mkdir` 1046, `write_text` 1047 (plik w folderze danych); `zdarzenie` 1051 BEZ `_czekanie_okna`; `odswiez_pule` 1053 | sqlite 5000 ms |
| A6 | aplikacja.py:1055 `odswiez_pule` | ui/okno.py:147 | `_policz_pule` 1061 (watek 701 albo 761); `_odswiez` 1062 | 100 ms (sqlite) |
| A7 | aplikacja.py:973 `przelacz_tryb` | ui/okno.py:287 | `super().przelacz_tryb` 977 -> kontroler_api.py:3745 `_polecenie` (`zdarzenie` 3741); `_odswiez_katalog` 979 (watek); `_odswiez` 981 | 200 ms / 100 ms (sqlite) |
| A8 | aplikacja.py:1453 `ponow_zapis` | ui/okno.py:183 (`QTimer.singleShot(0)` -> `_polecenie`) | `_zapisz` 1458 dla kazdej pozycji -> transakcja 1418 (nie przez `_polecenie`, BEZ `_czekanie_okna`); `_odswiez` 1459 | 5000 ms na kazda pozycje |
| A9 | aplikacja.py:1506 `zamknij` | aplikacja.py:1719 (`aboutToQuit`), 1725 (po app.exec) | `_zamknij_ramki_excel` 1511 -> `k.zgas()` kontroler_api.py:2756, `ramki.zatrzymaj()` 2760, `excel.rozlacz()` 2769; `scanner.stop()` 1516 -> scanner.py:357 `join(5.0)`, 360 -> 507 zamek bez limitu, 512 `join(2.0)`; `_zdarzenie_skrzynki` 1525 (SQL); `silnik.stop()` 1527 -> silnik.py:1289 `join(5.0)`, 1553 `send`, 1554 `join(2.0)`, 1559 `join(5.0)`; `_zdarzenie_silnika` 1537 i `_zapisz` 1539 (transakcja 1418); `_zapisz_zadania` 1549 (plik 655-657); `zdarzenie` 1554; `_zbuduj` 1555 (bez `_czekanie_okna`); `baza.zamknij` 1562 | joiny: 5 + 2 (scanner) + 5 + 2 + 5 (silnik); sqlite 5000 ms na operacje; zamek 507 i ramki/Excel - brak |
| A10 | aplikacja.py:1642 `OknoZastepcze.keyPressEvent` | zdarzenie klawiatury Qt; okno zastepcze tylko gdy brak pakietu ui (1611-1613) | `kontroler.start_skanu()` 1644 (= A4) | jak A4 |

### 7b. kontroler_api.py

| # | plik:linia metody | skad wolana | operacje blokujace (plik:linia) | limit czasu |
|---|---|---|---|---|
| K1 | kontroler_api.py:1328 `stan` | ui/okno.py:132, 297, 520, 896 | `_zbuduj` 1330 tylko przy pierwszym wywolaniu (bez `_czekanie_okna`); zwykle stan z pamieci | 5000 ms przy pierwszym |
| K2 | kontroler_api.py:1142 `wykonaj` | ui/okno.py:519 | `inspect.signature` 1149; polecenie 1152 | wg polecenia |
| K3 | kontroler_api.py:1435 `KontrolerSesji.przetworz` (Atrapa 4429; w Aplikacji nadpisane A3) | QTimer 1190 | `_przetworz_ramki` 1439 (= K34); `_odswiez` 1444 | jak K4 |
| K4 | kontroler_api.py:3465 `_polecenie` (wspolne dla polecen) + `_odswiez` 1340 | z polecen K5-K16, K24-K30 | funkcja polecenia pod `_czekanie_okna(CZEKAJ_POLECENIA_MS)` 3483-3484; `_odswiez` 3502 -> `_czekanie_okna(CZEKAJ_STANU_MS)` 1347 -> `_zbuduj` 1348/1494: `sesja.stan_wieczoru()` 1495 (poza zakresem), `_zapisz_liste_po_zmianie` 1500 -> `sesja.zapisz_do_dofrezowania` 3124 (zapis pliku CSV), `_plytka` 1509 -> `_inspekcje` 3183 -> `_wynik_skanu` 1479 (odczyt JSON wyniku), `_uklad` 3193 -> 1465, `_rodzaj_bledu` SELECT 3332, `_przyczyna_bledu` SELECT 3312, `_numer_z_dolkow` 3226 -> 1479; tryb rano `_stan_rano` 1523 -> `rano.piece()` 1965, `_braki_biezace` 1966 -> `rano.braki()` 1898 (cala historia zlecen), `rano.otwarty_piec()` 1968, `rano.stan_pieca` 1972 / 1908, `rano.wynik_pieca` 1908, SELECT 2009, `_miniatury` 2013 -> 1637, `_rozlozone` 2022 -> 1654, `_z_przeniesienia` 2032 -> 1915, SELECT 2035; `_po_odswiezeniu` 1363 -> `_synchronizuj_ramke_p` (2590 `rano.plan_plytek`, 2593 SELECT, 2594 `k.ustaw_plan_rano`) i `_synchronizuj_ramke_w` (2694 `k.blad()`, 2716 `k.wynik(...)`) | sqlite: 200 ms (`CZEKAJ_POLECENIA_MS` 119) i 100 ms (`CZEKAJ_STANU_MS` 120); komentarz 116-118: realnie 0,17-0,96 s; pliki / CPU / ramki - brak |
| K5 | kontroler_api.py:3614 `ukruszona` | ui/okno.py:548 | SELECT 3616; `sesja.decyzja` 3618 (poza zakresem); K4 | 200 / 100 ms (sqlite) |
| K6 | kontroler_api.py:3622 `ok`, 3625 `cofnij`, 3628 `wybierz_wpis`, 3631 `cofnij_wpis` | ui/okno.py:548, 555, 562 | `sesja.ok/cofnij/wybierz_wpis/cofnij_wpis` (poza zakresem); K4 | 200 / 100 ms |
| K7 | kontroler_api.py:3662 `potwierdz_ponowny_skan`, 3677 `cofnij_zastapienie`, 3680 `dopusc_plytke`, 3683 `cofnij_dopuszczenie` | ui/okno.py:766, 905; ui/ekran_rano.py:775 | `_polecenie_plytki` 3648 -> `_sesja_skanu` SELECT 3638, metoda sesji 3656 (poza zakresem); K4 | 200 / 100 ms |
| K8 | kontroler_api.py:3665 `odrzuc_ponowny_skan` | ui/okno.py:905 | `_plytka_dowolna` 3667 (pamiec), `zdarzenie` 3670; K4 | 200 / 100 ms |
| K9 | kontroler_api.py:3686 `podaj_numer_plytki` | ui/okno.py:766, 905; ui/ekran_rano.py:775 | SELECT pod `_czekanie_okna` 3703-3704; `_odswiez` 3713; `rano.podaj_numer_plytki` 3719 / `sesja.podaj_numer_plytki` 3721 (poza zakresem); K4 | 200 / 100 ms |
| K10 | kontroler_api.py:3730 `przelacz_tryb` | ui/okno.py:287 (w Aplikacji przez A7) | `zdarzenie` 3741; K4 | 200 / 100 ms |
| K11 | kontroler_api.py:3747 `wybierz_kandydata`, 3755 `przypisz_recznie`, 3759 `cofnij_przypisanie` | ui/ekran_rano.py:608 (sygnal widoku -> `_polecenie`) | `rano.*` 3752 / 3757 / 3761 (poza zakresem); K4 | 200 / 100 ms |
| K12 | kontroler_api.py:3780 `zamknij_piec` | ui/ekran_rano.py:846, 857 | `_zajety` 3786 (pamiec); `rano.zamknij_piec` 3791 (poza zakresem); `_po_zamknieciu_pieca` 3792 -> `k.stan()` 2784, `_zgas_ramke_p` 2786 -> `k.zgas()` 2562; K4 | 200 / 100 ms (sqlite); ramka - brak |
| K13 | kontroler_api.py:3797 `zamknij_piec_i_przenies`, 3815 `cofnij_przeniesienie`, 3825 `otworz_piec_ponownie` | ui/ekran_rano.py:900; ui/okno.py:905 (przyciski pytan) | `rano.*` 3809 / 3819 / 3828 (poza zakresem); `_po_zamknieciu_pieca` 3810; `_wyczysc_excel_otwartego` 3820 / 3829 -> SELECT 2945; K4 | 200 / 100 ms |
| K14 | kontroler_api.py:3834 `pomin_skan`, 3837 `cofnij_pominiecie`, 3840 `zamknij_brak_recznie`, 3848 `cofnij_zamkniecie_reczne` | ui/ekran_rano.py:775, 363, 379 | `rano.*` (poza zakresem); K4 | 200 / 100 ms |
| K15 | kontroler_api.py:3851 `ustaw_kolejnosc`, 3874 `wybierz_kuwete` | wybierz_kuwete: ui/ekran_rano.py:1062; ustaw_kolejnosc: watek okna, miejsce w ui nieustalone (brak bezposredniego wywolania w grep; tylko przez `_polecenie(nazwa, ...)`) | pamiec; `self.stan()` 3869; K4 (`_odswiez`) | 100 ms |
| K16 | kontroler_api.py:3899 `potwierdz_kuwete`, 3924 `cofnij_kuwete` | ui/ekran_rano.py:984, 990 | `stan()` 3908 / 3932; `zdarzenie` 3917 / 3943; `_rozlozone` 3918 / 3939 -> SELECT 1654 (pierwszy raz); K4 | 200 / 100 ms |
| K17 | kontroler_api.py:3588 `wybierz_operatora` | ui/okno.py:566, 570 | `sesja.wybierz_operatora` 3603 (poza zakresem); `_odswiez` 3596 / 3611 (nie przez `_polecenie`) | 100 ms (sqlite w `_odswiez`) |
| K18 | kontroler_api.py:3973 `zamknij_pytanie`, 3984 `zamknij_komunikat` | ui/okno.py:893, 903, 905 | `_odswiez` 3981 / 3992 | 100 ms |
| K19 | kontroler_api.py:3995 `zapisz_liste` | ui/okno.py:573 | `_odswiez` 4003 (zapis CSV 3124); dla doby: `sesja.zapisz_do_dofrezowania` 4013 (plik + SQL) BEZ `_czekanie_okna`; `_odswiez` 4017 | 100 ms; dla doby 5000 ms |
| K20 | kontroler_api.py:3570 `ponow_polecenie` | ui/okno.py:905 (przycisk "Ponow teraz") | `getattr(self, nazwa)(*argumenty)` 3582 - ponowione polecenie; `_odswiez` 3584 | jak polecenie |
| K21 | kontroler_api.py:3950 `projekty_kuwety` | ui/ekran_rano.py:607 -> ui/kandydaci.py:314 (wpisywanie kuwety) | SELECT 3960-3964 i `_miniatury` 3965 -> 1637 pod `_czekanie_okna` 3959 | 200 ms |
| K22 | kontroler_api.py:4062 `szczegoly_pracy` | ui/okno.py:921 (otwarcie pracy) | pod `_czekanie_okna` 4069: `_inspekcje` 4070 -> `_wynik_skanu` 1479 (odczyt pliku JSON), `_plik_podgladu` 4071 -> SELECT 4088, `is_file` 4093 | 200 ms tylko sqlite; plik - brak |
| K23 | kontroler_api.py:3092 `excel_szczegoly` | ui/okno_excela.py:261 | pamiec; `self.excel.konf.kolor` 3100 (poza zakresem) | - |
| K24 | kontroler_api.py:2983 `test_led` | ui/okno.py:150 | `k.tryb("test_led")` 2989 (indicate); `_odczytaj_ramki` 2993 -> `k.stan()` 2115; K4 | 200 / 100 ms; ramka - brak |
| K25 | kontroler_api.py:2998 `przejmij_ramke` | ui/okno.py:151 | `k.wznow()` 3008 (indicate); `zdarzenie` 3009; K4 | 200 / 100 ms; ramka - brak |
| K26 | kontroler_api.py:3014 `excel_zatwierdz` | ui/okno_excela.py:198, 200 | `self.excel.zatwierdz(...)` 3022 (Excel COM - zapis koloru; poza zakresem); K4 | 200 ms tylko sqlite; COM - brak w zakresie |
| K27 | kontroler_api.py:3029 `excel_pomin` | ui/okno_excela.py:207 | `self.excel.pomin(...)` 3035 (poza zakresem); K4 | jw. |
| K28 | kontroler_api.py:3054 `excel_odswiez` | ui/okno_excela.py:128 | `_excel_krok_piec` 3062 -> `rano.wynik_pieca` 2874, `_excel_zalatwione` SELECT 2829, SELECT 2880, `ex.propozycje(...)` 2888 (Excel COM - odczyt arkusza), `ex.zapisz_cien_bez_odczytu` 2904; K4 | 200 ms tylko sqlite; COM - brak |
| K29 | kontroler_api.py:3071 `excel_pokaz` | ui/ekran_rano.py:374, 454; ui/okno_excela.py:246 | `_excel_pokaz_piec` 3079 -> `_excel_krok_piec` 3048 (jak K28); K4 | jw. |
| K30 | kontroler_api.py:3083 `excel_zamknij` | ui/okno_excela.py:129 | pamiec; K4 | 100 ms |
| K31 | kontroler_api.py:2058 `podlacz_ramki` | aplikacja.py:584 (start) | `_odczytaj_ramki` 2067 -> `k.stan()` 2115; `_odswiez` 2071; `ramki.uruchom()` 2074 (indicate) | ramka - brak |
| K32 | kontroler_api.py:2078 `podlacz_excel` | aplikacja.py:595 (start) | `_excel_przelicz_zalegle` 2093 -> SELECT 2820, `rano.wynik_pieca` 2822, SELECT 2829; `_odswiez` 2097 | sqlite 5000 ms (poza `_odswiez`) |
| K33 | kontroler_api.py:1158 `wczytaj_podglad` | ui/obraz.py:132 w `_Zadanie.run` (QRunnable, obraz.py:83-86) | `SI.wczytaj_podglad` -> `np.load` silnik.py:960 | NIE w watku okna (watek QThreadPool) |
| K34 | kontroler_api.py:2228 `_przetworz_ramki` (prywatna, ale zegar okna) | aplikacja.py:1174 (A3), kontroler_api.py:1439 (K3) | `_przetworz_excel` 2233 -> `_excel_krok_piec` 2840 (COM 2888 / 2904), `excel.zaloguj_poprawki` 2918, `excel.zaloguj_juz_odhaczone` 2927, `excel.rozlacz` 2859, `_odswiez` 2854; `k.odbierz_zdarzenia()` 2241 (indicate); zapis zdarzen pod `_krotkie_czekanie_na_baze` 2250-2251 -> transakcje 2346 / 2464 / 2491 (w 2491 `rano.zamknij_piec` 2502); `_synchronizuj_ramke_p` 2268 (2590, 2593, 2594); `_odczytaj_ramki` 2271 -> `k.stan()` 2115 co `OKRES_STANU_RAMEK_S` = 0,25 s (105); `_odswiez` 2282 / `_odswiez_zywe` 2284 | sqlite 150 ms (zdarzenia ramek), 100 ms (`_odswiez`); jeden krok Excela na obieg (2832-2837), sam krok COM bez limitu; ramka - brak |
| K35 | kontroler_api.py:4366 `AtrapaKontrolera` (tryb `--atrapa`, aplikacja.py:1676) | ui jak wyzej; `scenariusz_pokazowy` / `scenariusz_poranny` aplikacja.py:1678-1680 | `B.otworz` 4388, `indeks_sztuczny` 4411 (transakcja 4352), `symuluj_*` -> `sesja.przyjmij_wynik` 4645 / `rano.*` 4643, `_sztuczny_podglad` 4703 (`np.savez`), `zamknij` 4577 (`shutil.rmtree`) | sqlite 5000 ms |

---------------------------------------------------------------------------------------------------------------------

## Liczba linii i potwierdzenie przeczytania

| plik | linii (grep "^") | przeczytany |
|---|---|---|
| silnik.py | 1823 | w calosci: 1-827, 828-1327, 1328-1823 |
| aplikacja.py | 1730 | w calosci: 1-600, 600-1099, 1100-1599, 1600-1730 |
| kontroler_api.py | 4756 | w calosci: 1-450, 450-999, 1000-1549, 1550-2098, 2099-2598, 2599-3097, 3098-3597, 3598-4047, 4048-4497, 4498-4756 |
| scanner.py | 753 | w calosci |
| baza.py | 586 | w calosci |
| pula.py | 442 | w calosci |
| pamiec_puli.py | 299 | w calosci |
| indeks.py | 395 | w calosci |
| ustawienia.py | 379 | w calosci |
| samokontrola.py | 1432 | w calosci: 1-500, 500-999, 1000-1432 |
| __init__.py | 29 | w calosci |

Zakresy pominiete: brak. Pliki ui/*.py czytane tylko we wskazanych fragmentach (naglowek), wylacznie dla ustalenia watku.
