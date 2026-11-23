# Wyliczenie miejsc czekania - "Stanowisko kontroli cyrkonii" (S2)

Data: 2026-11-23. Katalog: `<PC-katalog>\qc-wt\analiza-s2\Ramki\stanowisko\stanowisko\`.
Zakres: silnik.py, aplikacja.py, kontroler_api.py, scanner.py, baza.py, pula.py, pamiec_puli.py, indeks.py,
ustawienia.py, samokontrola.py, __init__.py. Tylko wyliczenie (bez oceny wagi). Numery linii z narzedzia Read,
sprawdzone dodatkowo przez Grep.

Skroty watkow / procesow (z kodu):
* "okno" = glowny watek procesu okna (watek Qt): `aplikacja.main()` (1651-1726), `Aplikacja.start/zamknij`, zegar
  `kontroler_api.lacznik_qt` (QTimer co 30 ms -> `kontroler.przetworz()`, kontroler_api.py:1184-1190) i polecenia okna
  (kontroler_api.py:20-23 "Kontroler zyje w watku okna").
* "nadzorca" = watek `silnik-nadzorca` (silnik.py:1268) w procesie okna.
* "silnik-start" = watek `silnik-start` (silnik.py:1458) w procesie okna.
* "potomny" = proces roboczy silnika `silnik-analiza` (silnik.py:1502), glowny watek = `_robotnik`; watek `silnik-straznik`
  (silnik.py:380) w tym procesie.
* "scanner" = watek `scanner` (scanner.py:346).
* "pula-liczenie" / "pula-katalog" / "pula-plik-csv" = watki z aplikacja.py:701 / 761 / 808.
* "samokontrola" = osobny program `python -m stanowisko.samokontrola`; "samokontrola-<kod>" = watki z samokontrola.py:307.

W tabelach znak `|` w kodzie zapisany jako `\|`.

---------------------------------------------------------------------------------------------------------------------

## A. Czekanie na watki i procesy (`.join(`, `.wait(`, `.communicate(`, `.result(`, `as_completed`)

| plik:linia | funkcja | fragment | limit czasu | po uplywie limitu | watek / proces |
|---|---|---|---|---|---|
| silnik.py:932 | `_przerwij_start` | `watek.join(0.05)` | tak: 0.05 s (literal); petla 929 do `czekaj_s` = `CZEKAJ_NA_PRZERWANIE_S` = 3.0 (stala, podana w 1481) | ponowienie w petli (z `_anuluj_zapis`); po 3 s watek zostawiony, dopisek do opisu (940-942) | nadzorca (z `_start_z_limitem` 1481) |
| silnik.py:950 | `_zamknij_porzucony` | `p.join(5.0)` | tak: 5.0 s (literal) | nic: dalej `p.close()`; wyjatki polykane (952) | silnik-start (1456) albo nadzorca (1489) |
| silnik.py:1289 | `Silnik.stop` | `w.join(czekaj_s)` | tak: `czekaj_s` = 5.0 (domyslny argument; aplikacja.py:1527 wola `stop()` bez argumentu) | `LOG.warning`, dalej zebranie listy i `_zamknij_proces` | okno (Aplikacja.zamknij 1527) |
| silnik.py:1419 | `Silnik._uruchom_proces` | `if proba > 1 and self._stop.wait(ODSTEP_PROB_URUCHOMIENIA_S):` | tak: 0.5 s (stala `ODSTEP_PROB_URUCHOMIENIA_S`) | nastepna proba uruchomienia (True = stop -> return) | nadzorca |
| silnik.py:1463 | `Silnik._start_z_limitem` | `w.join(0.05)` | tak: 0.05 s; petla 1462 do `limit_uruchomienia_s` = `LIMIT_URUCHOMIENIA_S` = 30.0 (stala, parametr Silnik) | ponowienie w petli; po 30 s / smierci potomka / stop -> `_przerwij_start` | nadzorca |
| silnik.py:1540 | `Silnik._proba_uruchomienia` | `p.join(5.0)` | tak: 5.0 s (literal) | nic: `rodzic.close()`, return None | nadzorca |
| silnik.py:1554 | `Silnik._zamknij_proces` | `p.join(2.0)` | tak: 2.0 s (literal), po `lacze.send(("koniec",))` | dalej `p.kill()`, gdy zyje (1557-1558) | okno (ze `stop()` 1300) albo nadzorca (1596, 1601, 1676, 1687, 1743) |
| silnik.py:1559 | `Silnik._zamknij_proces` | `p.join(5.0)` | tak: 5.0 s (literal) | nic: `kod = p.exitcode` (moze byc None), `p.close()` (ValueError polykany) | jw. |
| scanner.py:357 | `Scanner.stop` | `w.join(czekaj_s)` | tak: `czekaj_s` = 5.0 (domyslny; aplikacja.py:1516 bez argumentu) | watek zostaje (`self._watek` nie czyszczony), dalej `_zatrzymaj_watchdog` | okno (Aplikacja.zamknij 1516) |
| scanner.py:512 | `Scanner._zatrzymaj_watchdog` | `obs.join(2.0)` | tak: 2.0 s (literal) | nic (wyjatki polykane, 513-514) | okno (ze `stop()` 360) albo scanner (`_przeglad` 631, `_sprawdz_watchdog` 530) |
| scanner.py:550 | `Scanner._petla` | `self._budzik.wait(max(0.005, czekaj))` | tak: `okres_s` = `OKRES_S` = 0.05 gdy sa kandydaci, inaczej `min(przeglad_s, 0.5)` = 0.5 (`PRZEGLAD_S` = 2.0) | nastepny obieg petli 535 | scanner |
| samokontrola.py:312 | `_z_limitem` | `w.join(max(0.0, koniec - time.monotonic()))` | tak: wspolny termin `limit_s` (argument): 5 s `LIMIT_FOLDERU_S` (506, 999, 1307), 6 s `LIMIT_LICZENIA_S + 1.0` (964), `limit + 0.5` = 3.5 s ramki (1071), 30 s `LIMIT_SPRAWDZENIA_S` / 120 s `LIMIT_MODULOW_S` / 10 s `LIMIT_EXCELA_S` (1316) | wynik `("limit", None)`; watek zostaje w tle (daemon) | wolajacy: glowny watek samokontroli (1307, 1316) albo samokontrola-<kod> (zagniezdzone 506, 964, 999, 1071) |

Brak w zakresie: `.communicate(`, `.result(`, `as_completed`, `QThread.wait`, `QWaitCondition`, `subprocess.wait`.
(`.acquire(` i `with <zamek>:` pominiete zgodnie z poleceniem.)

---------------------------------------------------------------------------------------------------------------------

## B. Kolejki i potoki

### B1. recv / send / poll / get

| plik:linia | funkcja | fragment | limit czasu | po uplywie limitu | watek / proces |
|---|---|---|---|---|---|
| silnik.py:1045 | `_wykonaj.postep` | `lacze.send(("postep", zadanie.zadanie_id, str(etap), float(udzial)))` | nie | - | potomny (glowny watek, wolane z funkcji analizy) |
| silnik.py:1091 | `_przygotuj_pule` (lambda postepu) | `info = pamiec.przygotuj(opis, lambda gotowe, razem: lacze.send(("pula_postep", int(gotowe), int(razem))))` | nie | - | potomny |
| silnik.py:1097 | `_przygotuj_pule` | `lacze.send(odpowiedz)` | nie | - | potomny |
| silnik.py:1130 | `_robotnik` | `lacze.send(("blad_startu", f"{type(e).__name__}: {e}", traceback.format_exc()))` | nie | - | potomny |
| silnik.py:1140 | `_robotnik` | `lacze.send(("sprzatanie", usuniete))` | nie | - | potomny |
| silnik.py:1147 | `_robotnik` | `lacze.send(("gotowy", os.getpid()))` | nie | - | potomny |
| silnik.py:1150 | `_robotnik` | `wiadomosc = lacze.recv()` | nie | (EOFError / OSError -> return 1152) | potomny |
| silnik.py:1191 | `_robotnik` | `lacze.send(odpowiedz)` | nie | (OSError -> return) | potomny |
| silnik.py:1501 | `Silnik._proba_uruchomienia` | `rodzic, dziecko = self._ctx.Pipe()` | (utworzenie lacza, domyslnie duplex) | - | nadzorca |
| silnik.py:1553 | `Silnik._zamknij_proces` | `lacze.send(("koniec",))` | nie (po nim `p.join(2.0)`) | - | okno (stop) albo nadzorca |
| silnik.py:1582 | `Silnik._krok` | `if lacze.poll(OKRES_S):` | tak: 0.02 s (stala `OKRES_S`) | False -> kontrola stanu procesu i limitow (1589-1617), powrot do `_petla` | nadzorca |
| silnik.py:1583 | `Silnik._krok` | `self._odbierz(lacze.recv())` | nie (wolane tylko po `poll` True) | - | nadzorca |
| silnik.py:1615 | `Silnik._krok` | `lacze.send(("zadanie", zadanie))` | nie | (OSError -> `_po_smierci_procesu`) | nadzorca |
| silnik.py:1631 | `Silnik._wyslij_pule` | `lacze.send(("pula", opis))` | nie | (OSError -> `_po_smierci_procesu`) | nadzorca |
| silnik.py:1804 | `LacznikQt.oproznij` | `z = self.silnik.zdarzenia.get_nowait()` | nieblokujace (0 s) | `queue.Empty` -> return | okno (QTimer); aplikacja tego lacznika nie uzywa (uzywa kontroler_api.lacznik_qt, aplikacja.py:1717) |
| aplikacja.py:1150 | `Aplikacja.przetworz` | `e = self.silnik.zdarzenia.get_nowait()` | nieblokujace | `queue.Empty` -> pass | okno |
| aplikacja.py:1157 | `Aplikacja.przetworz` | `rodzaj, dane = self._skrzynka.get_nowait()` | nieblokujace | `queue.Empty` -> pass | okno |
| aplikacja.py:1521 | `Aplikacja.zamknij` | `rodzaj, dane = self._skrzynka.get_nowait()` | nieblokujace | `queue.Empty` -> break | okno |
| aplikacja.py:1533 | `Aplikacja.zamknij` | `e = self.silnik.zdarzenia.get_nowait()` | nieblokujace | `queue.Empty` -> break | okno |

### B2. Kolejki BEZ ograniczenia rozmiaru i ich `put` (dla kompletnosci; `put` nie blokuje)

| plik:linia | funkcja | fragment | watek |
|---|---|---|---|
| silnik.py:1231 | `Silnik.__init__` | `self.zdarzenia: queue.Queue = queue.Queue()` | okno (tworzenie) |
| silnik.py:1398 | `Silnik._zglos` | `self.zdarzenia.put(z)` | nadzorca; okno dla "zatrzymany" (1301) |
| scanner.py:304 | `Scanner.__init__` | `self.zdarzenia: queue.Queue = queue.Queue()` | okno (tworzenie) |
| scanner.py:748 | `Scanner._wyslij` | `self.zdarzenia.put(obiekt)` | scanner (tylko bez funkcji zwrotnych; aplikacja podaje funkcje) |
| aplikacja.py:481 | `Aplikacja.__init__` | `self._skrzynka: queue.Queue = queue.Queue()` | okno (tworzenie) |
| aplikacja.py:558 | `Aplikacja.start` (lambdy) | `na_skan=lambda z: self._skrzynka.put(("skan", z)), na_odrzucenie=lambda o: self._skrzynka.put(("odrzucenie", o)),` | scanner |
| aplikacja.py:559 | `Aplikacja.start` (lambda) | `na_oczekiwanie=lambda o: self._skrzynka.put(("oczekiwanie", o)), ...` | scanner |
| aplikacja.py:699 | `_policz_pule.licz` | `self._skrzynka.put(wynik)` | pula-liczenie |
| aplikacja.py:759 | `_odswiez_katalog.licz` | `self._skrzynka.put(wynik)` | pula-katalog |
| aplikacja.py:806 | `_kontrola_katalogu.sprawdz` | `self._skrzynka.put(("csv_stan", (nr, stan)))` | pula-plik-csv |

Brak w zakresie: `put` na kolejce z `maxsize`, `multiprocessing.connection.wait`, `recv_bytes`, czytanie stdout/stderr
procesu potomnego. Proces potomny przekierowuje wlasne stdout/stderr do pliku logu (silnik.py:1111-1115) albo do
`os.devnull` (1119); proces okna ich nie czyta.

---------------------------------------------------------------------------------------------------------------------

## C. Petle czekajace (while / for z ponowieniami, z sleep / wait / poll / get / zegarem)

| plik:linia | funkcja | petla | czekanie / zegar w srodku | warunek wyjscia | gorna granica czasu / obrotow | watek / proces |
|---|---|---|---|---|---|---|
| silnik.py:373 | `Straznik.uruchom.petla` | `while True:` | `time.sleep(okres_s)` 378 (`OKRES_STRAZNIKA_S` = 0.5); zegar w `sprawdz` 368 | brak wyjscia z petli; `sprawdz()` konczy proces (kod 91 / 92) | brak (petla bez konca z zalozenia) | potomny, watek silnik-straznik |
| silnik.py:459 | `PamiecPul.pula_wpisow` | `for nr, (plik, wsp) in enumerate(pliki, start=1):` | `time.monotonic()` 464-465 (tylko rzadszy postep, `ODSTEP_POSTEPU_PULI_S` = 0.25) | koniec listy plikow | obroty = liczba plikow puli; brak limitu czasu w petli (nadzorca zabija proces po `min(limit_zadania_s, LIMIT_BEZ_POSTEPU_PULI_S=120)` bez postepu, 1598-1602) | potomny |
| silnik.py:617 | `_kopiuj_skan` | `while True:` | `time.monotonic()` 616 / 640, `time.sleep(...)` 647 | return po udanej kopii 638; FileNotFoundError 621; OSError (miejsce) 629; `PlikNiedostepny` po `czekaj_s` 641 | tak: `czekaj_s` = ust `[silnik] czekaj_na_plik_s` (domyslnie 60.0; stala `CZEKAJ_NA_PLIK_S`) - sprawdzane MIEDZY probami; pojedyncza proba (otwarcie + kopia 619-636) bez limitu | potomny |
| silnik.py:929 | `_przerwij_start` | `while watek.is_alive() and time.monotonic() - t0 < czekaj_s:` | `watek.join(0.05)` 932 | watek zakonczony albo czas | tak: `czekaj_s` = 3.0 | nadzorca |
| silnik.py:1148 | `_robotnik` | `while True:` | `lacze.recv()` 1150 (bez limitu) | "koniec" 1153, EOFError/OSError 1151, KeyboardInterrupt 1180, OSError przy send 1192 | brak w petli (Straznik konczy proces po zniknieciu procesu okna i po `limit_zadania_s + ZAPAS_LIMITU_S`) | potomny, glowny watek |
| silnik.py:1365 | `Silnik.czekaj_na_pusta_kolejke` | `while True:` | `time.monotonic()` 1370, `time.sleep(0.02)` 1372 | kolejka pusta albo czas | tak: `limit_s` (argument) | nie wiadomo (brak wywolania w zakresie) |
| silnik.py:1406 | `Silnik._petla` | `while not self._stop.is_set():` | `_krok`: `lacze.poll(0.02)` 1582, `time.sleep(0.05)` 1575; `time.sleep(0.2)` 1411 po wyjatku; zegar w `_krok`: `limit_startu_s` (180, 1595), budowa puli (1599-1600), `_sprawdz_limit` (`limit_zadania_s`, 1674) | `_stop` ustawione przez `stop()` | brak granicy calkowitej (petla glowna); pojedynczy obrot bez limitu, gdy stoi `send` / `recv` / `_zglos` | nadzorca |
| silnik.py:1418 | `Silnik._uruchom_proces` | `for proba in range(1, self.proby_uruchomienia + 1):` | `self._stop.wait(0.5)` 1419 | udana proba, stop, koniec prob | tak: `proby_uruchomienia` = `PROBY_URUCHOMIENIA` = 3; kazda proba do ok. 30 s + 3 s przerwania + `p.join(5.0)` | nadzorca |
| silnik.py:1462 | `Silnik._start_z_limitem` | `while w.is_alive() and not self._stop.is_set() and time.monotonic() - t0 < self.limit_uruchomienia_s:` | `w.join(0.05)` 1463, kod wyjscia potomka co `SPRAWDZ_POTOMKA_S` = 0.5 | watek skonczyl, stop, czas, potomek zginal (1467) | tak: `limit_uruchomienia_s` = 30.0 | nadzorca |
| silnik.py:1802 | `LacznikQt.oproznij` | `for _ in range(200):` | `get_nowait` 1804 | `queue.Empty` | tak: 200 obrotow | okno (nieuzywane przez aplikacje) |
| scanner.py:535 | `Scanner._petla` | `while True:` | `obieg()`, `self._budzik.wait(...)` 550 (<= 0.5 s) | `_stop` ustawione (sprawdzane pod `_zamek_watku` 536-539) | brak (petla glowna); pojedynczy obieg bez limitu | scanner |
| scanner.py:573 | `Scanner.obieg` | `for k, kand in list(self._kandydaci.items()):` | zegar `teraz` (555) vs `kand["nastepna"]` 593 i `stabilizacja_s` 595 | koniec listy | obroty = liczba kandydatow; ponowienia pliku zajetego w kolejnych obiegach BEZ limitu liczby prob (z zalozenia, opis 17-21 i 723-726) | scanner |
| aplikacja.py:1144 | `Aplikacja.przetworz` | `for d in [x for x in self._do_zapisu if x.nastepna <= t0]:` | zegar `t0` (1139), `odstep_ponowienia` | koniec listy | obroty = pozycje "nie zapisano"; brak limitu czasu (kazdy `_zapisz` = transakcja z `busy_timeout` polaczenia, domyslnie 5000 ms); liczba ponowien w czasie bez limitu | okno |
| aplikacja.py:1147 | `Aplikacja.przetworz` | `while True:` | `get_nowait` x2, `time.monotonic()` 1166 | obie kolejki puste albo `time.monotonic() - t0 > limit_s` | tak (miekka): `limit_s` = `K.LIMIT_PRZETWARZANIA_S` = 0.05, sprawdzany po kazdym zdarzeniu; pojedyncza obsluga bez limitu | okno |
| aplikacja.py:1457 | `Aplikacja.ponow_zapis` | `for d in list(self._do_zapisu):` | `_zapisz` (transakcja) | koniec listy | obroty = pozycje; brak limitu czasu | okno |
| aplikacja.py:1519 | `Aplikacja.zamknij` | `while True:` | `self._skrzynka.get_nowait()` | `queue.Empty` | brak granicy czasu i obrotow (do oproznienia kolejki) | okno |
| aplikacja.py:1531 | `Aplikacja.zamknij` | `while True:` | `self.silnik.zdarzenia.get_nowait()` | `queue.Empty` | jw. | okno |
| aplikacja.py:1538 | `Aplikacja.zamknij` | `for d in list(self._do_zapisu):` | `_zapisz` (transakcja) | koniec listy | obroty = pozycje; brak limitu czasu | okno |
| samokontrola.py:311 | `_z_limitem` | `for w in watki:` | `w.join(max(0.0, koniec - time.monotonic()))` | koniec listy | tak: lacznie `limit_s` | wolajacy |
| samokontrola.py:900 | `_licz_stl` | `for _, podfoldery, pliki in os.walk(folder):` | `time.monotonic()` 898 / 903 | koniec `os.walk` albo czas | tak: `LIMIT_LICZENIA_S` = 5.0 sprawdzany po kazdym katalogu (pojedynczy krok `os.walk` bez limitu; calosc pod `_z_limitem` 964, 6 s) | samokontrola-pula |
| samokontrola.py:1311 | `wykonaj` | `for kody, funkcja in SPRAWDZENIA:` | `_z_limitem(...)` 1316, `time.monotonic()` 1300 / 1330 | koniec listy (17 pozycji) | tak: kazdy obrot do `limit_sprawdzenia`: 30 s (`LIMIT_SPRAWDZENIA_S`), moduly 120 s, excel 10 s | glowny watek samokontroli |

### C2. Ponowienia rozlozone w czasie (nie petla - wywolywane z petli nadrzednej albo zegara okna)

| plik:linia | funkcja | fragment | odstep / limit liczby prob | watek |
|---|---|---|---|---|
| aplikacja.py:1145 | `przetworz` | `d.nastepna = t0 + odstep_ponowienia(d.proby + 1)` | odstep 1 s, 2x ... do `ODSTEP_ZAPISU_MAX_S` = 30 s (249-251); liczba prob bez limitu | okno |
| aplikacja.py:785 | `_kontrola_katalogu` | `if time.monotonic() < self._ponow_katalog_po:` | `PONOW_KATALOG_S` = 60 s (828); bez limitu prob | okno |
| aplikacja.py:1479 | `_blad_analizy` | `if e.rodzaj == "plik_niedostepny" and z.proby < self.ponow_plik_niedostepny:` | limit: ust `[silnik] ponow_plik_niedostepny` (domyslnie 3) | okno |
| aplikacja.py:1486 | `_blad_analizy` | `if z.proby_startu < PROBY_STARTU_SILNIKA and not self._silnik_nie_startuje:` | limit: `PROBY_STARTU_SILNIKA` = 1 | okno |
| kontroler_api.py:2245 | `_przetworz_ramki` | `if self._zdarzenia_ponow and teraz < self._zdarzenia_ponow_od:` | `OKRES_PONOWIENIA_ZDARZEN_S` = 1.0 (2253); bez limitu prob | okno |
| kontroler_api.py:2265 | `_przetworz_ramki` | `if self._plan_p_ponow and teraz >= self._plan_p_ponow_od and self._stan is not None:` | `OKRES_PONOWIENIA_PLANU_S` = 2.0; bez limitu prob | okno |
| kontroler_api.py:1396 | `_nadrob_stan` | `if not self._stan_zalegly or self._zamkniety or time.monotonic() < self._stan_ponow_od:` | `OKRES_NADRABIANIA_STANU_S` = 1.0, czekanie `CZEKAJ_NADRABIANIA_MS` = 0; bez limitu prob | okno |
| scanner.py:730 | `Scanner._zajety` | `kand["nastepna"] = teraz + min(odstep_max_s, self.okres_s * 2 ** min(kand["proby"], 16))` | do `ODSTEP_ZAJETY_MAX_S` = 2.0 / `ODSTEP_PISZE_MAX_S` = 0.25; bez limitu prob | scanner |
| silnik.py:1574 | `Silnik._krok` | `if self._nieudany_start is not None and not self._kolejka:` | kolejny start dopiero przy zadaniu w kolejce; bez limitu prob | nadzorca |
| silnik.py:1644 | `Silnik._pula_przerwana` | `koniec = self._pula_proby >= PROBY_PRZYGOTOWANIA_PULI and self._pula_zadana == opis` | limit: `PROBY_PRZYGOTOWANIA_PULI` = 2 | nadzorca |

---------------------------------------------------------------------------------------------------------------------

## D. time.sleep / QThread.msleep / QEventLoop.exec / processEvents

| plik:linia | funkcja | fragment | czas | watek / proces |
|---|---|---|---|---|
| silnik.py:378 | `Straznik.uruchom.petla` | `time.sleep(okres_s)` | `OKRES_STRAZNIKA_S` = 0.5 s | potomny, silnik-straznik |
| silnik.py:647 | `_kopiuj_skan` | `time.sleep(min(ODSTEP_KOPII_MAX_S, 0.05 * 2 ** min(proba, 16), max(0.0, czekaj_s - (time.monotonic() - t0)) + 0.01))` | do 2.0 s (`ODSTEP_KOPII_MAX_S`) | potomny |
| silnik.py:1372 | `Silnik.czekaj_na_pusta_kolejke` | `time.sleep(0.02)` | 0.02 s | nie wiadomo |
| silnik.py:1411 | `Silnik._petla` | `time.sleep(0.2)` | 0.2 s (po wyjatku w `_krok`) | nadzorca |
| silnik.py:1575 | `Silnik._krok` | `time.sleep(0.05)  # po nieudanym starcie ...` | 0.05 s | nadzorca |
| aplikacja.py:1723 | `main` | `kod = app.exec()` | brak (glowna petla Qt do `quit`) | okno (glowny watek) |
| aplikacja.py:1671 | `main.pokaz_blad` | `QtWidgets.QMessageBox.critical(None, "Stanowisko", tekst)` | brak (okno modalne z wlasna petla zdarzen, czeka na czlowieka; pokrewne `exec`, spoza scislej listy) | glowny watek, przed `app.exec` |

Brak w zakresie: `QThread.msleep`, `QEventLoop.exec`, `processEvents`.

---------------------------------------------------------------------------------------------------------------------

## E. sqlite

### E1. `sqlite3.connect(`

| plik:linia | funkcja | fragment | timeout | isolation_level | check_same_thread | watek |
|---|---|---|---|---|---|---|
| baza.py:319 | `_polacz` (tylko_odczyt) | `pol = sqlite3.connect(f"{plik.resolve().as_uri()}?mode=ro", uri=True, isolation_level=None)` | nie podany (domyslny sqlite3 = 5.0 s); potem `PRAGMA busy_timeout = czekaj_ms` (domyslnie `CZEKAJ_NA_BLOKADE_MS` = 5000) | None (autocommit) | nie podany (domyslnie True) | wolajacy `otworz(tylko_odczyt=True)` - w zakresie nie wolane |
| baza.py:321 | `_polacz` | `pol = sqlite3.connect(plik, isolation_level=None)  # transakcje jawne ...` | nie podany (5.0 s); `busy_timeout` 5000 ms (324) | None | nie podany (True) | wolajacy `otworz()`: okno (aplikacja.py:456), pula-katalog (pula.py:361 z aplikacja.py:745), atrapa (kontroler_api.py:4388); takze 434 po kopii przed migracja |
| baza.py:581 | `Baza.kopia` | `docelowe = sqlite3.connect(cel)` | nie podany (5.0 s) | nie podany (domyslny "") | nie podany (True) | nie wiadomo (brak wywolania w zakresie) |
| samokontrola.py:677 | `_polacz_do_odczytu` | `pol = sqlite3.connect(_uri_do_odczytu(plik), uri=True, isolation_level=None, timeout=CZEKAJ_NA_BAZE_MS / 1000)` | 1.0 s (stala `CZEKAJ_NA_BAZE_MS` = 1000) + `busy_timeout` 1000 ms (679) | None | nie podany (True) | samokontrola-baza / samokontrola-pula |

### E2. PRAGMA (pelna tresc)

| plik:linia | funkcja | tresc |
|---|---|---|
| baza.py:323 | `_polacz` | `PRAGMA foreign_keys = ON` |
| baza.py:324 | `_polacz` | `f"PRAGMA busy_timeout = {int(czekaj_ms)}"` (domyslnie 5000) |
| baza.py:336 | `_wersja` | `PRAGMA user_version` |
| baza.py:387 | `_migruj` | `f"PRAGMA user_version = {int(wersja)}"` (w transakcji BEGIN IMMEDIATE) |
| baza.py:476 | `Baza.wersja` | `PRAGMA user_version` |
| baza.py:493 | `Baza._ustaw_czekanie` | `f"PRAGMA busy_timeout = {int(czekaj_ms)}"` (z `Baza.czekanie`) |
| baza.py:535 | `Baza.kolumny` | `f"PRAGMA table_info({tabela})"` |
| kontroler_api.py:1879 | `_klucz_punktow` | `PRAGMA data_version` |
| kontroler_api.py:2299 | `_krotkie_czekanie_na_baze.czekanie` | `f"PRAGMA busy_timeout = {int(CZEKAJ_ZDARZENIA_MS)}"` (150) |
| kontroler_api.py:2308 | `_krotkie_czekanie_na_baze.czekanie` | `f"PRAGMA busy_timeout = {int(getattr(baza, 'czekaj_ms', B.CZEKAJ_NA_BLOKADE_MS))}"` (przywrocenie) |
| samokontrola.py:679 | `_polacz_do_odczytu` | `f"PRAGMA busy_timeout = {int(CZEKAJ_NA_BAZE_MS)}"` (1000) |
| samokontrola.py:703 | `_quick_check` | `PRAGMA quick_check(5)` (przerwanie przez `set_progress_handler` 701 po `LIMIT_QUICK_CHECK_S` = 4.0 s, krok 20000) |
| samokontrola.py:744 | `_baza` | `PRAGMA user_version` |

### E3. BEGIN / COMMIT / ROLLBACK / executescript / VACUUM / backup

| plik:linia | funkcja | fragment | uwaga |
|---|---|---|---|
| baza.py:384 | `_migruj` | `pol.execute("BEGIN IMMEDIATE")` | czeka na blokade do `busy_timeout` |
| baza.py:388 | `_migruj` | `pol.execute("COMMIT")` | |
| baza.py:391 | `_migruj` | `pol.execute("ROLLBACK")` | |
| baza.py:512 | `Baza.transakcja` | `self._wykonaj("BEGIN IMMEDIATE")` | zajeta po `busy_timeout` -> `BladBazy` (502); zagniezdzenie = dolacza do zewnetrznej (509-511) |
| baza.py:515 | `Baza.transakcja` | `self._wykonaj("COMMIT")` | |
| baza.py:518 | `Baza.transakcja` | `self.polaczenie.execute("ROLLBACK")` | |
| baza.py:583 | `Baza.kopia` | `self.polaczenie.backup(docelowe)` | bez `pages` / `sleep` (cala baza jednym krokiem); limitu nie ma - wg implementacji CPython sqlite3 krok jest ponawiany co `sleep` = 0.25 s, dopoki BUSY / LOCKED; brak wywolania w zakresie |
| baza.py:70, 72 | `_tylko_dopisywanie` | `... BEFORE UPDATE ON {tabela} BEGIN ` | to DDL wyzwalacza (czesc migracji), nie transakcja |

Brak w zakresie: `.commit(`, `.rollback(`, `executescript(`, `VACUUM`, `with <polaczenie>:`.
Wszystkie polaczenia programu maja `isolation_level=None` (autocommit); transakcje tylko przez `Baza.transakcja`.

### E4. Bloki `with` zamiast `with <polaczenie>:`

`with baza.transakcja():` (BEGIN IMMEDIATE ... COMMIT):
aplikacja.py:1418 (`_zapis_w_bazie`), indeks.py:241 (`indeksuj`), indeks.py:298 (`_folder`), kontroler_api.py:2346
(`_zdarzenia_ramki.zapisz_serie`), 2464 (`_zdarzenie_ramki`), 2491 i 2514 (`_zamknij_piec_z_ramki`), 4302
(`indeks_rano_sztuczny`), 4352 (`indeks_sztuczny`).

Krotsze czekanie na blokade (`busy_timeout` na czas bloku):
aplikacja.py:1121 (`start_skanu`, 200 ms); kontroler_api.py:1347 (`_odswiez`, `czekaj_ms` = 100 / 0), 2250
(`_przetworz_ramki`, 150 ms), 3483 (`_polecenie`, 200 ms), 3703 (`podaj_numer_plytki`, 200), 3959 (`projekty_kuwety`,
200), 4069 (`szczegoly_pracy`, 200), 4452 (atrapa `start_skanu`, 200). Wszystkie poza 2250 przez `Baza.czekanie`
(baza.py:479-489). Bez takiego bloku dziala `busy_timeout` polaczenia (5000 ms).

### E5. Wywolania SQL policzone per funkcja (execute / _wykonaj / wykonaj / wstaw / zdarzenie / wiersz / wiersze; O = odczyt, Z = zapis)

Oznaczenie [WIELE] = wiecej niz 1 zapis w jednej transakcji; [PETLA] = zapis w petli.

| plik | funkcja | wywolania |
|---|---|---|
| baza.py | `_polacz` | 2 (PRAGMA) |
| baza.py | `_wersja` | 1 O |
| baza.py | `_migruj` | 5 miejsc: BEGIN, SQL w petli 385-386, PRAGMA user_version =, COMMIT, ROLLBACK [WIELE] [PETLA] |
| baza.py | `otworz` | 1 Z (`zdarzenie` 442, poza transakcja) |
| baza.py | `wersja` / `_ustaw_czekanie` / `_wykonaj` / `wykonaj` | po 1 |
| baza.py | `transakcja` | 3 (BEGIN IMMEDIATE, COMMIT, ROLLBACK) |
| baza.py | `wiersze` / `wiersz` / `kolumny` | po 1 O |
| baza.py | `wstaw` | 2 Z (545, 547; jedno na wywolanie) |
| baza.py | `zdarzenie` | 1 Z (przez `wstaw`) |
| baza.py | `zrzut` | 1 O w petli po tabelach |
| aplikacja.py | `start` | 1 O (551) + 1 Z (564); petla 553-555 wola `_nowy_skan` [PETLA] |
| aplikacja.py | `_sprzatnij_podglady` | 1 O |
| aplikacja.py | `_pula_wpisow_policzona` / `_zdarzenie_puli` / `ustaw_pule` / `start_skanu` / `_zdarzenie_silnika` | po 1 Z |
| aplikacja.py | `_rozstrzygnij_sprawdzenia` | 1 Z w petli 1021 (kazdy osobno, autocommit) [PETLA] |
| aplikacja.py | `_zdarzenie_skrzynki` | 2 Z (alternatywy) |
| aplikacja.py | `_skan_z_wynikiem` | 1 O |
| aplikacja.py | `_nowy_skan` | 2 Z (alternatywy) + 1 O |
| aplikacja.py | `_przejmij_przemianowany` | 2 Z (alternatywy) |
| aplikacja.py | `_zapis_w_bazie` | jedna transakcja 1418: 1 O + 1-2 Z wlasne (1421 / 1434) + `sesja.przyjmij_wynik` / `rano.przyjmij_wynik` / `przyjmij_blad` (zapisy w session, poza zakresem) + `_zapisz_podglad` (1 Z) [WIELE] |
| aplikacja.py | `_blad_analizy` | 3 Z (alternatywy) |
| aplikacja.py | `zamknij` | 1 Z (1554); petla 1538 `_zapisz` (transakcja na pozycje) [PETLA] |
| aplikacja.py | `przetworz` / `ponow_zapis` | petle 1144 / 1457 `_zapisz` (transakcja na pozycje) [PETLA] |
| kontroler_api.py | `_wczytaj_tryb`, `_rozlozone`, `_klucz_punktow`, `_piec_zamkniety`, `_z_przeniesienia`, `_ostatni_zamkniety_id`, `_klucz_zapisany`, `_potwierdzone_z_bazy`, `_excel_zalatwione`, `_wyczysc_excel_otwartego`, `_przyczyna_bledu`, `_rodzaj_bledu`, `_minut_od`, `_wczytaj_odrzucone`, `_sesja_skanu`, `_plik_podgladu`, `projekty_kuwety` | po 1 O |
| kontroler_api.py | `_miniatury` | 1 O w petli (porcje po 500) |
| kontroler_api.py | `_stan_rano_pieca` | 2 O |
| kontroler_api.py | `_klucze_zrodla` | 2 O |
| kontroler_api.py | `_excel_przelicz_zalegle` | 1 O + w petli odczyty (`_excel_zalatwione`, `rano.wynik_pieca`) |
| kontroler_api.py | `_excel_krok_piec` | 1 O (2880) + odczyty posrednie |
| kontroler_api.py | `_krotkie_czekanie_na_baze.czekanie` | 2 (PRAGMA) |
| kontroler_api.py | `_wpisz_zdarzenie_ramki` | 1 Z |
| kontroler_api.py | `_zdarzenie_ramki` | transakcja 2464: 1 O + 1 Z |
| kontroler_api.py | `_zdarzenia_ramki.zapisz_serie` | transakcja 2346 z petla 2348 po zdarzeniach (kazde 1 O + 1 Z) [WIELE] [PETLA] |
| kontroler_api.py | `_zdarzenia_ramki.zapisz_po_jednym` | petla 2322, transakcja na zdarzenie [PETLA] |
| kontroler_api.py | `_zamknij_piec_z_ramki` | transakcja 2491: 1 O + `rano.zamknij_piec` (zapisy session_rano) + 1 Z [WIELE]; transakcja 2514: 1 O + 1 Z |
| kontroler_api.py | `przejmij_ramke`, `odrzuc_ponowny_skan`, `przelacz_tryb`, `potwierdz_kuwete`, `cofnij_kuwete` (funkcje `wykonaj`), `_zapisz_podglad` | po 1 Z |
| kontroler_api.py | `ukruszona.wykonaj` | 1 O + `sesja.decyzja` (poza zakresem) |
| kontroler_api.py | `indeks_rano_sztuczny` (atrapa) | 1 O + transakcja 4302 z petla: `wstaw` x2 + `wykonaj` [WIELE] [PETLA] |
| kontroler_api.py | `indeks_sztuczny` (atrapa) | 1 O + transakcja 4352 z petla: `wstaw` x3 [WIELE] [PETLA] |
| kontroler_api.py | `AtrapaKontrolera.start_skanu` / `ustaw_pule` | po 1 Z |
| indeks.py | `indeksuj` | 2 O (196, 209 w petli po zrodlach) + transakcja 241 w petli po znikajacych zleceniach z 2 Z (242, 243) + 1 Z (246) [WIELE] [PETLA] |
| indeks.py | `_folder` | 1 O + transakcja 298 z 6 miejscami zapisu (300, 305, 311, 315, 318, 324), w petlach 308 i 323 [WIELE] [PETLA] |
| indeks.py | `IndeksPlikow.__init__` | 2 O |
| pula.py | `_wiersze_okna`, `_nieaktualne_okna`, `pula_poranna` | po 1 O |
| pula.py | `_z_cechami`, `sciezki_plikow` | 1 O w petli (porcje) |
| pula.py | `KatalogPul.odswiez` | 1 Z (395) + `I.indeksuj` + `W.wczytaj_do_bazy` + `W.powiaz_frezowania` (zapisy poza zakresem) - kolejno, nie w jednej transakcji |
| pula.py | `_zapisz_sprzecznosci` | 1 O + 1 Z |
| samokontrola.py | `_polacz_do_odczytu` | 1 (PRAGMA) |
| samokontrola.py | `_quick_check` | 1 O |
| samokontrola.py | `_baza` | 2 O |
| samokontrola.py | `_pula_wpisow` | 1 miejsce, 3 O (generator po 3 zapytaniach) |
| silnik.py, scanner.py, pamiec_puli.py, ustawienia.py, __init__.py | - | 0 |

---------------------------------------------------------------------------------------------------------------------

## F. Operacje plikowe (mogace wisiec na dysku sieciowym / zajetym pliku)

Kolumna "petla ponowien": "nie" = poza petla ponowien (petla po plikach / folderach to nie ponowienie).

### silnik.py (proces potomny, chyba ze zaznaczono)

| plik:linia | funkcja | fragment | petla ponowien |
|---|---|---|---|
| silnik.py:240 | `CzyscicielNazw.__init__` | `wpisy = list(korzen.rglob("*")) if korzen.is_dir() else []` | nie |
| silnik.py:245 | `CzyscicielNazw.__init__` | `plik = p.is_file()` | nie |
| silnik.py:439 | `PamiecPul._klucz_wpisow` | `st = os.stat(plik)` | nie |
| silnik.py:509 | `PamiecPul.dla.pula_dla` | `for p in S.pliki_projektow(f):` (listowanie w synth) | nie |
| silnik.py:510 | `PamiecPul.dla.pula_dla` | `st = p.stat()` | nie |
| silnik.py:533 | `_skrot16` | `with open(plik, "rb") as f:` | nie |
| silnik.py:575 | `_sprzataj_katalog_roboczy` | `wpisy = list(os.scandir(katalog))` | nie |
| silnik.py:586 | `_sprzataj_katalog_roboczy` | `if e.is_dir(follow_symlinks=False):` | nie |
| silnik.py:587 | `_sprzataj_katalog_roboczy` | `shutil.rmtree(e.path, ignore_errors=True)` | nie |
| silnik.py:589 | `_sprzataj_katalog_roboczy` | `os.unlink(e.path)` | nie |
| silnik.py:597 | `_sprzataj_tmp` | `wpisy = list(os.scandir(folder))` | nie |
| silnik.py:604 | `_sprzataj_tmp` | `os.unlink(e.path)` | nie |
| silnik.py:619 | `_kopiuj_skan` | `zrodlo = otworz_zrodlo(skan)` | tak, petla 617 z limitem `czekaj_s` (60 s) sprawdzanym miedzy probami |
| silnik.py:626 | `_kopiuj_skan` | `przed = os.fstat(zrodlo.fileno())` | tak (617), jw. |
| silnik.py:627 | `_kopiuj_skan` | `wolne = shutil.disk_usage(cel.parent).free` | tak (617), jw. |
| silnik.py:632 | `_kopiuj_skan` | `with open(cel, "wb") as f:` | tak (617), jw. |
| silnik.py:633 | `_kopiuj_skan` | `for blok in iter(lambda: zrodlo.read(BLOK_ODCZYTU), b""):` | tak (617), odczyt w obrebie proby bez limitu |
| silnik.py:636 | `_kopiuj_skan` | `po = os.fstat(zrodlo.fileno())` | tak (617), jw. |
| silnik.py:960 | `wczytaj_podglad` | `with np.load(plik) as z:` | nie; watek: nie wiadomo jednoznacznie (wolane przez kontroler_api.wczytaj_podglad 1164, opisane jako dla okna) |
| silnik.py:969 | `_zapisz_bez_nadpisania` | `with open(tmp, "wb") as f:` | w petli nazw 1004 (do 9999, bez czekania) |
| silnik.py:972 | `_zapisz_bez_nadpisania` | `os.rename(tmp, cel)  # Windows: ...` | jw. |
| silnik.py:974 | `_zapisz_bez_nadpisania` | `os.link(tmp, cel)` (poza Windows) | jw. |
| silnik.py:975 | `_zapisz_bez_nadpisania` | `os.unlink(tmp)` | jw. |
| silnik.py:978 | `_zapisz_bez_nadpisania` | `os.unlink(tmp)` | jw. |
| silnik.py:992 | `_zapisz_wyjscie` | `wyj.mkdir(parents=True, exist_ok=True)` | nie |
| silnik.py:993 | `_zapisz_wyjscie` | `_sprzataj_tmp(wyj)` | nie |
| silnik.py:1007 | `_zapisz_wyjscie` | `if p_json.exists() or p_npz.exists():` | petla 1004 `for n in range(1, 10000):` (granica 9999, bez czekania) |
| silnik.py:1011 | `_zapisz_wyjscie` | `_zapisz_bez_nadpisania(p_npz, lambda f: np.savez(f, **tablice))` | petla 1004 |
| silnik.py:1015 | `_zapisz_wyjscie` | `_zapisz_bez_nadpisania(p_json, lambda f: f.write(dane))` | petla 1004 |
| silnik.py:1019 | `_zapisz_wyjscie` | `os.unlink(p_npz)` | petla 1004 |
| silnik.py:1038 | `_wykonaj` | `if not skan.is_file():` | nie |
| silnik.py:1047 | `_wykonaj` | `_sprzataj_katalog_roboczy(katalog)` | nie |
| silnik.py:1050 | `_wykonaj` | `folder.mkdir(parents=True, exist_ok=True)` | nie |
| silnik.py:1052 | `_wykonaj` | `sha16 = _kopiuj_skan(skan, kopia, czekaj_na_plik_s, ...)` | petla wewnatrz (617) |
| silnik.py:1062 | `_wykonaj` | `shutil.rmtree(folder, ignore_errors=True)` | nie |
| silnik.py:1082 | `_ustaw_pamiec_linii` | `Path(katalog).mkdir(parents=True, exist_ok=True)` | nie |
| silnik.py:1111 | `_robotnik` | `log = open(plik_logu, "ab", buffering=0)` | nie |
| silnik.py:1114 | `_robotnik` | `sys.stdout = open(1, "w", encoding="utf-8", errors="replace", closefd=False, buffering=1)` | nie (deskryptor 1, nie plik z dysku) |
| silnik.py:1115 | `_robotnik` | `sys.stderr = open(2, "w", ...)` | nie (deskryptor 2) |
| silnik.py:1119 | `_robotnik` | `sys.stdout = sys.stderr = open(os.devnull, "w")` | nie |
| silnik.py:1141 | `_robotnik` | `... else Path(tempfile.gettempdir()) / KATALOG_ROBOCZY` | nie (gettempdir przy pierwszym uzyciu w procesie sprawdza katalogi zapisem pliku probnego) |
| silnik.py:1143 | `_robotnik` | `katalog.mkdir(parents=True, exist_ok=True)` | nie |
| silnik.py:1144 | `_robotnik` | `_sprzataj_katalog_roboczy(katalog)` | nie |
| silnik.py:1228 | `Silnik.__init__` | `... else os.path.join(tempfile.gettempdir(), KATALOG_ROBOCZY)` | nie; okno (Aplikacja.start 535) |

### aplikacja.py

| plik:linia | funkcja | fragment | petla ponowien / watek |
|---|---|---|---|
| aplikacja.py:97 | `stan_pliku` | `st = os.stat(plik)` | nie; pula-katalog (741), pula-plik-csv (803) |
| aplikacja.py:166 | `_istnieje` | `return Path(plik).is_file()` | nie; okno (wywolania 209, 217, 1257, 1281, 1497; posrednio przez `Zlecenie.zdarzenie/do_zapisu`: 1417, 655) |
| aplikacja.py:209 | `Zlecenie.sciezka_aktualna` | `if _istnieje(plik):` | petla po sciezkach (1 + len(zastepcze)), bez czekania; okno |
| aplikacja.py:217 | `Zlecenie.przejmij_zastepcza` | `if _istnieje(plik):` | `while self.zastepcze:` 215 (granica len), bez czekania; okno |
| aplikacja.py:272 | `BlokadaStanowiska.zajmij` | `self.plik.parent.mkdir(parents=True, exist_ok=True)` | nie; glowny watek (main 1692) |
| aplikacja.py:273 | `BlokadaStanowiska.zajmij` | `fd = os.open(self.plik, os.O_RDWR \| os.O_CREAT, 0o644)` | nie (plik `<baza>.blokada`, bez O_EXCL) |
| aplikacja.py:278 | `BlokadaStanowiska.zajmij` | `msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)` | nie (LK_NBLCK - jedna proba; blad -> `ProgramJuzDziala`) |
| aplikacja.py:282 | `BlokadaStanowiska.zajmij` | `fcntl.flock(fd, fcntl.LOCK_EX \| fcntl.LOCK_NB)` | nie (poza Windows) |
| aplikacja.py:302 | `BlokadaStanowiska.zwolnij` | `os.lseek(fd, 0, os.SEEK_SET)` | nie; okno (zamknij 1564) / main 1714 |
| aplikacja.py:303 | `BlokadaStanowiska.zwolnij` | `msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)` | nie |
| aplikacja.py:399 | `pliki_stl` | `return sum(1 for p in folder.rglob("*") if p.suffix.lower() == ".stl" and p.is_file()` | nie; pula-liczenie |
| aplikacja.py:533 | `Aplikacja.start` | `self.katalog_logow.mkdir(parents=True, exist_ok=True)` | nie; okno |
| aplikacja.py:563 | `Aplikacja.start` | `(self.katalog_danych / PLIK_ZADAN).unlink(missing_ok=True)` | nie; okno |
| aplikacja.py:604 | `_sprzatnij_podglady` | `if not katalog.is_dir():` | nie; okno |
| aplikacja.py:613 | `_sprzatnij_podglady` | `for p in katalog.iterdir():` | nie; okno |
| aplikacja.py:616 | `_sprzatnij_podglady` | `p.unlink()` | nie; okno |
| aplikacja.py:631 | `_usun_pliki_wyniku` | `Path(pliki[klucz]).unlink(missing_ok=True)` | nie; okno |
| aplikacja.py:637 | `_wczytaj_zadania` | `if not plik.is_file():` | nie; okno |
| aplikacja.py:640 | `_wczytaj_zadania` | `dane = json.loads(plik.read_text(encoding="utf-8"))` | nie; okno |
| aplikacja.py:652 | `_zapisz_zadania` | `plik.unlink(missing_ok=True)` | nie; okno (zamknij 1549) |
| aplikacja.py:655 | `_zapisz_zadania` | `tmp.write_text(json.dumps({"wersja": 1, ...` | nie; okno |
| aplikacja.py:657 | `_zapisz_zadania` | `os.replace(tmp, plik)` | nie; okno |
| aplikacja.py:662 | `_wczytaj_pule` | `dane = json.loads((self.katalog_danych / PLIK_PULI).read_text(encoding="utf-8"))` | nie; okno (Aplikacja.__init__ 525); takze samokontrola-<kod> (samokontrola.py:940) |
| aplikacja.py:696 | `_policz_pule.licz` | `wynik = ("pula", (nr, pliki_stl(folder) if folder.is_dir() else None))` | nie; pula-liczenie |
| aplikacja.py:741 | `_odswiez_katalog.licz` | `csv_stan = stan_pliku(plik_csv)` | nie; pula-katalog |
| aplikacja.py:803 | `_kontrola_katalogu.sprawdz` | `stan = ("ok", stan_pliku(plik))` | nie; pula-plik-csv |
| aplikacja.py:1046 | `ustaw_pule` | `self.katalog_danych.mkdir(parents=True, exist_ok=True)` | nie; okno |
| aplikacja.py:1047 | `ustaw_pule` | `(self.katalog_danych / PLIK_PULI).write_text(json.dumps({...` | nie; okno |
| aplikacja.py:1257 | `_nowy_skan` | `przemianowany = ... and not _istnieje(jest["plik"])` | nie; okno |
| aplikacja.py:1281 | `_przejmij_przemianowany` | `if _istnieje(x.plik) or not any(_istnieje(p) for p, _ in x.zastepcze):` | nie; okno |
| aplikacja.py:1497 | `_blad_analizy` | `if not _istnieje(z.plik) and z.przejmij_zastepcza():` | nie; okno |
| aplikacja.py:1578 | `konfiguruj_logi` | `katalog.mkdir(parents=True, exist_ok=True)` | nie; glowny watek |
| aplikacja.py:1586 | `konfiguruj_logi` | `uchwyt = logging.handlers.RotatingFileHandler(plik, maxBytes=2 * 1024 * 1024, backupCount=5, encoding="utf-8")` | nie; kazdy wpis logu z kazdego watku pisze do tego pliku (rotacja = zmiana nazw plikow) |

### kontroler_api.py (okno)

| plik:linia | funkcja | fragment | petla ponowien |
|---|---|---|---|
| kontroler_api.py:1478 | `_wynik_skanu` | `if plik is not None and plik.is_file():` | nie |
| kontroler_api.py:1479 | `_wynik_skanu` | `tresc = json.loads(plik.read_text(encoding="utf-8"))` | nie |
| kontroler_api.py:3124 | `_zapisz_liste_po_zmianie` | `self.sesja.zapisz_do_dofrezowania(None, katalog=self._katalog_listy())` (zapis pliku w session, poza zakresem) | nie |
| kontroler_api.py:4013 | `zapisz_liste` | `nazwa = self.sesja.zapisz_do_dofrezowania(doba, katalog=self._katalog_listy()).name` | nie |
| kontroler_api.py:4093 | `_plik_podgladu` | `return plik if plik is not None and plik.is_file() else None` | nie |
| kontroler_api.py:4386 | `AtrapaKontrolera.__init__` | `self.katalog = Path(tempfile.mkdtemp(prefix="qc_atrapa_")) if katalog is None else Path(katalog)` | nie (atrapa) |
| kontroler_api.py:4387 | `AtrapaKontrolera.__init__` | `self.katalog.mkdir(parents=True, exist_ok=True)` | nie (atrapa) |
| kontroler_api.py:4577 | `AtrapaKontrolera.zamknij` | `shutil.rmtree(self.katalog, ignore_errors=True)` | nie (atrapa) |
| kontroler_api.py:4701 | `_sztuczny_podglad` | `katalog.mkdir(parents=True, exist_ok=True)` | nie (atrapa) |
| kontroler_api.py:4703 | `_sztuczny_podglad` | `np.savez(plik, **tablice)` | nie (atrapa) |

### scanner.py (watek scanner, chyba ze zaznaczono)

| plik:linia | funkcja | fragment | petla ponowien |
|---|---|---|---|
| scanner.py:149 | `sprawdz_stl` | `rozmiar = os.stat(plik).st_size` | tak: plik zajety ponawiany w kolejnych obiegach bez limitu liczby prob (682) |
| scanner.py:150 | `sprawdz_stl` | `with otworz_zrodlo(plik) as f:` | tak, jw. |
| scanner.py:180 | `skrot16_pliku` | `with otworz_zrodlo(plik) as f:` | tak (703), jw. |
| scanner.py:182 | `skrot16_pliku` | `blok = f.read(BLOK_ODCZYTU)` (petla 181 do konca pliku) | tak, jw. |
| scanner.py:245 | `_podpis` | `st = os.stat(sciezka)` | nie |
| scanner.py:254 | `_identyfikator` | `st = os.stat(folder)` | nie; scanner albo okno (start -> `_uruchom_watchdog` 503) |
| scanner.py:391 | `Scanner.przygotuj` | `self._folder_dostepny = self.folder.is_dir()` | nie; okno (start z aplikacja.py:562) |
| scanner.py:401 | `_ustal_zastane` | `pliki = list(pliki_w_folderze(self.folder, niedostepne=niedostepne))` | nie; okno (z `przygotuj` 394) albo scanner (z `_przeglad` 637) |
| scanner.py:465 | `_uruchom_watchdog_bez_zamka` | `if self._tryb != "watchdog" or self._watchdog is not None or not self.folder.is_dir():` | nie; okno / scanner; pod zamkiem `_zamek_watchdog` |
| scanner.py:575 | `Scanner.obieg` | `st = os.stat(kand["sciezka"])` | tak: co obieg (0.05 s przy kandydatach), bez limitu |
| scanner.py:626 | `_przeglad` | `dostepny = self.folder.is_dir()` | tak: co `przeglad_s` (2.0 s), bez limitu |
| scanner.py:641 | `_przeglad` | `for rel, rozmiar, mtime_ns in pliki_w_folderze(self.folder, niedostepne=niedostepne):` | tak: co `przeglad_s`, bez limitu |
| scanner.py:660 | `_przeglad` | `os.stat(k)` | tak: co `przeglad_s` (petla po znanych) |
| scanner.py:669 | `_rozstrzygnij` | `if teraz - kand["od"] < self.odrzuc_po_s or ktos_pisze(sciezka):` | tak (obiegi, bez limitu) |
| scanner.py:679 | `_rozstrzygnij` | `if not os.path.exists(sciezka):` | tak, jw. |
| scanner.py:685 | `_rozstrzygnij` | `if teraz - kand["od"] < self.odrzuc_po_s or ktos_pisze(sciezka):` | tak, jw. |
| scanner.py:687 | `_rozstrzygnij` | `if _podpis(sciezka) != kand["podpis"] or w.rozmiar != kand["podpis"][0]:` | tak, jw. |
| scanner.py:693 | `_rozstrzygnij` | `if ktos_pisze(sciezka):` | tak, jw. |
| scanner.py:697 | `_rozstrzygnij` | `sha16 = skrot16_pliku(sciezka)` | tak, jw. |
| scanner.py:698 | `_rozstrzygnij` | `st = os.stat(sciezka)` | tak, jw. |

### baza.py (watek wolajacego `otworz` / `kopia`)

| plik:linia | funkcja | fragment | petla ponowien |
|---|---|---|---|
| baza.py:319 | `_polacz` | `... sqlite3.connect(f"{plik.resolve().as_uri()}?mode=ro", ...)` (`resolve`) | nie |
| baza.py:355 | `_ta_sama_tresc` | `if not (a.is_file() and b.is_file()) or a.stat().st_size != b.stat().st_size:` | nie (petla po kopiach 368) |
| baza.py:357 | `_ta_sama_tresc` | `with open(a, "rb") as fa, open(b, "rb") as fb:` | nie (odczyt w petli 358 do konca pliku) |
| baza.py:368 | `_kopia_przed_migracja` | `for istniejaca in sorted(plik.parent.glob(f"{plik.stem}.kopia_v{wersja}_*.sqlite")):` | nie |
| baza.py:374 | `_kopia_przed_migracja` | `while cel.exists():` | petla bez gornej granicy obrotow (do pierwszej wolnej nazwy), bez czekania |
| baza.py:377 | `_kopia_przed_migracja` | `shutil.copy2(plik, cel)` | nie |
| baza.py:407 | `otworz` | `if not plik.exists():` | nie |
| baza.py:421 | `otworz` | `istnial = plik.exists() and plik.stat().st_size > 0` | nie |
| baza.py:422 | `otworz` | `plik.parent.mkdir(parents=True, exist_ok=True)` | nie |
| baza.py:578 | `Baza.kopia` | `if cel.exists():` | nie |
| baza.py:580 | `Baza.kopia` | `cel.parent.mkdir(parents=True, exist_ok=True)` | nie |

### pula.py (pula-katalog)

| plik:linia | funkcja | fragment | petla ponowien |
|---|---|---|---|
| pula.py:375 | `KatalogPul.odswiez` | `if self.plik_csv is not None and self.plik_csv.is_file():` | nie |
| pula.py:377 | `KatalogPul.odswiez` | `wymagane \|= {w.plik for w in W.wczytaj_csv(self.plik_csv, dzis=teraz.date()) if ...}` (odczyt CSV, poza zakresem) | nie |
| pula.py:380 | `KatalogPul.odswiez` | `r = I.indeksuj(self.baza, self.zrodla, teraz, ...)` (odczyt folderow zlecen, indeks.py) | nie |
| pula.py:386 | `KatalogPul.odswiez` | `elif not self.plik_csv.is_file():` | nie |
| pula.py:390 | `KatalogPul.odswiez` | `wynik["csv"] = W.wczytaj_do_bazy(self.baza, self.plik_csv, teraz=teraz).do_slownika()` (odczyt CSV, poza zakresem) | nie |

### pamiec_puli.py (proces potomny silnika - jedyne wywolanie w zakresie: silnik.py:410-412)

| plik:linia | funkcja | fragment | petla ponowien |
|---|---|---|---|
| pamiec_puli.py:127 | `PamiecPuli.pliki` | `if self.katalog is None or not self.katalog.is_dir():` | nie |
| pamiec_puli.py:129 | `PamiecPuli.pliki` | `return sorted(p for p in self.katalog.glob("*.npz") if ".tmp" not in p.name)` | nie |
| pamiec_puli.py:133 | `PamiecPuli.skrot` | `st = os.stat(plik)` | nie |
| pamiec_puli.py:136 | `PamiecPuli.skrot` | `self._skroty[k] = S.skrot_pliku(plik)` (czyta plik, synth) | nie |
| pamiec_puli.py:155 | `PamiecPuli.lekki` | `pr = _projekt_z_pliku(plik, wspolczynnik, orientacja)` (czyta STL, match) | nie (petla po plikach puli silnik.py:459) |
| pamiec_puli.py:176 | `PamiecPuli._czytaj_lekki` | `if plik is None or not plik.is_file():` | nie |
| pamiec_puli.py:180 | `PamiecPuli._czytaj_lekki` | `with np.load(plik, allow_pickle=False) as d:` | nie |
| pamiec_puli.py:215 | `PamiecPuli.projekt` | `pr = _projekt_z_pliku(plik, lk.wspolczynnik, orientacja)` | nie |
| pamiec_puli.py:221 | `PamiecPuli.projekt` | `if p is not None and not p.is_file():` | nie |
| pamiec_puli.py:236 | `PamiecPuli._czytaj_ciezki` | `if plik is None or not plik.is_file():` | nie |
| pamiec_puli.py:240 | `PamiecPuli._czytaj_ciezki` | `with np.load(plik, allow_pickle=False) as d:` | nie |
| pamiec_puli.py:267 | `PamiecPuli._zapisz` | `plik.parent.mkdir(parents=True, exist_ok=True)` | nie |
| pamiec_puli.py:268 | `PamiecPuli._zapisz` | `np.savez(tmp, meta=np.array(json.dumps(opis)), l_profil=lk.profil, ...)` | nie |
| pamiec_puli.py:269 | `PamiecPuli._zapisz` | `os.replace(tmp, plik)` | nie |
| pamiec_puli.py:274 | `PamiecPuli._zapisz` | `tmp.unlink(missing_ok=True)` | nie |
| pamiec_puli.py:281 | `PamiecPuli._dotknij` | `os.utime(plik)` | nie |
| pamiec_puli.py:287 | `PamiecPuli.sprzataj` | `if self.katalog is None or not self.katalog.is_dir():` | nie |
| pamiec_puli.py:291 | `PamiecPuli.sprzataj` | `for p in self.katalog.glob("*.npz"):` | nie |
| pamiec_puli.py:293 | `PamiecPuli.sprzataj` | `wiek = teraz - p.stat().st_mtime` | nie |
| pamiec_puli.py:295 | `PamiecPuli.sprzataj` | `p.unlink()` | nie |

### indeks.py (pula-katalog - jedyne wywolanie w zakresie: pula.py:380 z aplikacja.py:747)

| plik:linia | funkcja | fragment | petla ponowien |
|---|---|---|---|
| indeks.py:85 | `_czytaj_plik` | `return Path(p).read_bytes()` | nie |
| indeks.py:158 | `_policz_stl` | `for _, _, pliki in os.walk(katalog, onerror=lambda e: None):` | nie |
| indeks.py:167 | `_wpisy_folderu` | `with os.scandir(sciezka) as wpisy:` | nie |
| indeks.py:169 | `_wpisy_folderu` | `if p.is_dir():` | nie |
| indeks.py:171 | `_wpisy_folderu` | `elif p.is_file() and p.name.lower().endswith(".stl") and ...` | nie |
| indeks.py:172 | `_wpisy_folderu` | `st = p.stat()` | nie |
| indeks.py:198 | `indeksuj` | `if katalog is None or not Path(katalog).is_dir():` | nie |
| indeks.py:202 | `indeksuj` | `with os.scandir(katalog) as wpisy:` | nie |
| indeks.py:203 | `indeksuj` | `foldery = sorted((e for e in wpisy if e.is_dir() and ...` | nie |
| indeks.py:215 | `indeksuj` | `pliki, w_podfolderach = _wpisy_folderu(e.path)` | nie (petla po folderach 212) |
| indeks.py:216 | `indeksuj` | `zmieniono = max([e.stat().st_mtime] + [m / 1e9 for _, m, _ in pliki])` | nie |
| indeks.py:273 | `_folder` | `dane = _czytaj_plik(sciezka / plik)` | nie (petla po plikach 259) |

### ustawienia.py

| plik:linia | funkcja | fragment | petla ponowien / watek |
|---|---|---|---|
| ustawienia.py:19 | (modul) | `KORZEN = Path(__file__).resolve().parent.parent` | nie; przy imporcie w kazdym procesie |
| ustawienia.py:220 | `uzupelnij_uklady_wbudowane` | `if nazwa not in d["plytki"] and (KORZEN / KATALOG_MODELI_WZGLEDNY / nazwa / "uklad.json").exists():` | nie (petla po 10 ukladach) |
| ustawienia.py:351 | `wczytaj_ustawienia` | `if not plik.exists():` | nie; glowny watek (aplikacja.py:1683, samokontrola.py:1409), potomny gdy `ust` None (silnik.py:1125) |
| ustawienia.py:356 | `wczytaj_ustawienia` | `with open(plik, "rb") as f:` | nie; jw. |
| ustawienia.py:379 | `katalog_plytki` | `return (KORZEN / ust["plytki"][nazwa]).resolve()` | nie; okno (kontroler_api.py:1462) |

### samokontrola.py (watki samokontrola-<kod> pod `_z_limitem`, chyba ze zaznaczono)

| plik:linia | funkcja | fragment | petla ponowien |
|---|---|---|---|
| samokontrola.py:323 | `_istniejacy_przodek` | `while not p.exists() and p.parent != p:` | petla (granica: glebokosc sciezki), bez czekania |
| samokontrola.py:351 | `czytaj_wymagania` | `for linia in Path(plik).read_text(encoding="utf-8").splitlines():` | nie |
| samokontrola.py:444 | `klucze_domyslne` | `with open(plik, "rb") as f:` | nie |
| samokontrola.py:492 | `_czytaj_folder` | `if not p.exists():` | nie (pod `_z_limitem` 506, 5 s) |
| samokontrola.py:494 | `_czytaj_folder` | `if not p.is_dir():` | nie (jw.) |
| samokontrola.py:496 | `_czytaj_folder` | `with os.scandir(p) as wpisy:` | nie (jw.) |
| samokontrola.py:549 | `_proba_zapisu` | `uchwyt = os.open(nazwa, os.O_CREAT \| os.O_EXCL \| os.O_WRONLY \| getattr(os, "O_BINARY", 0), 0o600)` | petla 546: 3 proby (`PROBY_PLIKU_PROBNEGO`), bez czekania |
| samokontrola.py:553 | `_proba_zapisu` | `os.write(uchwyt, b"samokontrola")` | jw. |
| samokontrola.py:556 | `_proba_zapisu` | `os.unlink(nazwa)` | jw. |
| samokontrola.py:562 | `_wolne_miejsce` | `return shutil.disk_usage(folder).free` | nie |
| samokontrola.py:568 | `_dane_folder` | `if folder.is_dir():` | nie |
| samokontrola.py:577 | `_dane_folder` | `if folder.exists() or not przodek.is_dir() or not os.access(przodek, os.W_OK):` | nie |
| samokontrola.py:655 | `_dane_polozenie` | `if (k.korzen / PLIK_SUM).is_file() and _wewnatrz(k.folder_danych(), k.korzen):` | nie |
| samokontrola.py:689 | `_naglowek_bazy` | `with open(plik, "rb") as f:` | nie |
| samokontrola.py:713 | `_baza` | `if not plik.exists() or (plik.is_file() and plik.stat().st_size == 0):` | nie |
| samokontrola.py:716 | `_baza` | `if not plik.is_file():` | nie |
| samokontrola.py:718 | `_baza` | `rozmiar_mb = plik.stat().st_size / 2**20` | nie |
| samokontrola.py:787 | `_blokada_trzymana` | `if not plik_blokady.is_file():` | nie |
| samokontrola.py:790 | `_blokada_trzymana` | `uchwyt = os.open(plik_blokady, os.O_RDWR)` | nie (plik `.blokada`) |
| samokontrola.py:798 | `_blokada_trzymana` | `msvcrt.locking(uchwyt, msvcrt.LK_NBLCK, 1)` | nie (jedna proba) |
| samokontrola.py:801 | `_blokada_trzymana` | `os.lseek(uchwyt, 0, os.SEEK_SET)` | nie |
| samokontrola.py:802 | `_blokada_trzymana` | `msvcrt.locking(uchwyt, msvcrt.LK_UNLCK, 1)` | nie |
| samokontrola.py:807 | `_blokada_trzymana` | `fcntl.flock(uchwyt, fcntl.LOCK_EX \| fcntl.LOCK_NB)` | nie (poza Windows) |
| samokontrola.py:810 | `_blokada_trzymana` | `fcntl.flock(uchwyt, fcntl.LOCK_UN)` | nie |
| samokontrola.py:840 | `_wada_ukladu` | `if not katalog.is_dir():` | nie (petla po ukladach 874 / 879) |
| samokontrola.py:843 | `_wada_ukladu` | `if not plik.is_file():` | nie |
| samokontrola.py:855 | `_wada_ukladu` | `d = json.loads(plik.read_text(encoding="utf-8"))` | nie |
| samokontrola.py:858 | `_wada_ukladu` | `numery = [p.name for p in katalog.iterdir() if _WZOR_PLYTKI.fullmatch(p.name)]` | nie |
| samokontrola.py:900 | `_licz_stl` | `for _, podfoldery, pliki in os.walk(folder):` | limit 5 s miedzy katalogami (C) |
| samokontrola.py:964 | `_pula_z_folderu` | `... _licz_stl(folder, LIMIT_LICZENIA_S) if folder.is_dir() else None},` | pod `_z_limitem` 6 s |
| samokontrola.py:999 | `_pula_wpisow` | `... lambda: (k.sciezka("folder_millbox") / PLIK_WSPOLCZYNNIKOW).is_file()}, LIMIT_FOLDERU_S)` | pod `_z_limitem` 5 s |
| samokontrola.py:1022 | `_pamiec_puli` | `if katalog.exists() and not katalog.is_dir():` | nie |
| samokontrola.py:1027 | `_pamiec_puli` | `if projekty.is_dir():` | nie |
| samokontrola.py:1028 | `_pamiec_puli` | `with os.scandir(projekty) as wpisy:` | nie |
| samokontrola.py:1032 | `_pamiec_puli` | `bajty += w.stat().st_size` | nie |
| samokontrola.py:1034 | `_pamiec_puli` | `... ("" if katalog.is_dir() else " (folder powstanie ...)")` | nie |
| samokontrola.py:1153 | `czytaj_sumy` | `tekst = Path(plik).read_bytes().decode("utf-8-sig")` | nie |
| samokontrola.py:1179 | `_sha256` | `with open(plik, "rb") as f:` | nie (petla po plikach sum 1237) |
| samokontrola.py:1199 | `nadmiarowe` | `for katalog, podkatalogi, pliki in os.walk(korzen / strefa):` | nie |
| samokontrola.py:1207 | `nadmiarowe` | `wpisy = sorted(os.scandir(korzen), key=lambda w: w.name)` | nie |
| samokontrola.py:1211 | `nadmiarowe` | `if w.is_dir():` | nie |
| samokontrola.py:1212 | `nadmiarowe` | `if ... and (Path(w.path) / "__init__.py").is_file():` | nie |
| samokontrola.py:1225 | `_sumy` | `if not plik.is_file():` | nie |
| samokontrola.py:1229 | `_sumy` | `if not plik.is_file():` | nie |
| samokontrola.py:1240 | `_sumy` | `if not p.is_file():` | nie |
| samokontrola.py:1242 | `_sumy` | `elif _sha256(p) != suma:` | nie |
| samokontrola.py:1340 | `_folder_odpowiada` | `return os.path.exists(folder)` | pod `_z_limitem` 1307 (5 s) |
| samokontrola.py:1379 | `_ma_bom` | `with open(plik, "rb") as f:` | nie; GLOWNY watek samokontroli, bez `_z_limitem` |
| samokontrola.py:1409 | `main` | `ust = UST.wczytaj_ustawienia(plik)` | nie; GLOWNY watek, bez `_z_limitem` (ustawienia.py:351, 356) |

__init__.py: brak operacji plikowych (tylko podmiana `_wmi` w `sys.modules`, linie 16-26).

---------------------------------------------------------------------------------------------------------------------

## G. Uruchamianie procesow zewnetrznych

| plik:linia | funkcja | fragment | argumenty (timeout, daemon) | watek |
|---|---|---|---|---|
| silnik.py:1232 | `Silnik.__init__` | `self._ctx = multiprocessing.get_context("spawn")` | - | okno (Aplikacja.start 535) |
| silnik.py:1502 | `Silnik._proba_uruchomienia` | `p = self._ctx.Process(target=_robotnik, name="silnik-analiza", daemon=True,` | daemon=True; bez timeout | nadzorca |
| silnik.py:1445 | `_start_z_limitem.cel` | `p.start()` | samo bez limitu; nadzorca czeka najwyzej `limit_uruchomienia_s` = 30 s (1462), potem `_przerwij_start` (3 s); flaga CREATE_NO_WINDOW przez pelnomocnika `_WinapiZFlagami` | silnik-start |
| silnik.py:822 | `_WinapiZFlagami.CreateProcess` | `return self._winapi.CreateProcess(*argumenty, **nazwane)` | bez zmian (watki bez proby startu) | dowolny watek wolajacy multiprocessing |
| silnik.py:830 | `_WinapiZFlagami.CreateProcess` | `wynik = self._winapi.CreateProcess(*argumenty, **nazwane)` | flagi `FLAGI_PROCESU_ROBOCZEGO` = 0x08000000 (825) | silnik-start |
| silnik.py:1106 | `_robotnik` | `rodzic = multiprocessing.parent_process()` | - | potomny |
| aplikacja.py:1652 | `main` | `multiprocessing.freeze_support()` | - | glowny watek |

Konczenie procesow (dla kompletnosci): silnik.py:949 `p.kill()` (`_zamknij_porzucony`), 1539 `p.kill()`
(`_proba_uruchomienia`), 1558 `p.kill()` (`_zamknij_proces`), 916 `_winapi.TerminateProcess(uchwyt, 1)`
(`_przerwij_start`), 762 `_winapi.TerminateProcess(uchwyt_procesu, 1)` (`ProbaStartu.po_utworzeniu`), 338
`k32.TerminateProcess(k32.GetCurrentProcess(), kod)` (`_zakoncz_proces`, potomny), 341 `os._exit(kod)`.

Brak w zakresie: `subprocess.*`, `os.startfile`, `QProcess`, `Pool(`, `ProcessPoolExecutor`, `ThreadPoolExecutor`.

---------------------------------------------------------------------------------------------------------------------

## Dodatek 1. Watki tworzone w zakresie (do kolumny "watek")

| plik:linia | nazwa | daemon | proces |
|---|---|---|---|
| silnik.py:380 | silnik-straznik | True | potomny |
| silnik.py:1268 | silnik-nadzorca | True | okno |
| silnik.py:1458 | silnik-start | True | okno |
| scanner.py:346 | scanner | True | okno |
| scanner.py:495-498 | watchdog `Observer()` (watki biblioteki) | `obs.daemon = True` | okno |
| aplikacja.py:701 | pula-liczenie | True | okno |
| aplikacja.py:761 | pula-katalog | True | okno |
| aplikacja.py:808 | pula-plik-csv | True | okno |
| samokontrola.py:307 | samokontrola-<kod> | True | samokontrola |
| kontroler_api.py:1184 | QTimer lacznika kontrolera (30 ms -> `przetworz`) | - | okno |
| silnik.py:1796 | QTimer lacznika silnika (nieuzywany przez aplikacje) | - | okno |
| aplikacja.py:1722 | `QtCore.QTimer.singleShot(..., app.quit)` (tylko `--zamknij-po`) | - | okno |

## Dodatek 2. Inne wywolania mogace stac, spoza kategorii A-G (zauwazone przy czytaniu; tylko lista)

* aplikacja.py:152 `uchwyty_knowndlls` - do 2047 wywolan `NtQueryObject` (okno, `Aplikacja.start` 541); aplikacja.py:996
  `knowndlls_otwarty` (okno, z `przetworz` 1171).
* silnik.py:911 `_opis_potomka` (GetProcessTimes, EnumProcessModulesEx, GetModuleBaseNameW) i 931 `_anuluj_zapis`
  (CancelSynchronousIo) - nadzorca.
* silnik.py:1058 funkcja analizy (`porownaj`) w procesie potomnym - limit tylko z zewnatrz (nadzorca `limit_zadania_s`,
  Straznik, Job Object).
* samokontrola.py:1047 `http.client.HTTPConnection(host, int(port), timeout=limit_s)` (3.0 s, `LIMIT_RAMKI_S`);
  samokontrola.py:1129 `klient.GetActiveObject("Excel.Application")` (COM, pod `_z_limitem` 10 s).
* kontroler_api.py - wywolania klientow ramek i Excela (moduly indicate / excel / excel_com poza zakresem) w watku okna:
  2074 `ramki.uruchom()`, 2115 `k.stan()`, 2241 `k.odbierz_zdarzenia()`, 2426 `k.potwierdzone()`, 2562 / 2756 `k.zgas()`,
  2594 `k.ustaw_plan_rano(...)`, 2624 `k.skanowanie()`, 2636 `k.znacznik()`, 2651 `k.analiza()`, 2667 / 2694 `k.blad()`,
  2716 `k.wynik(...)`, 2760 `self.ramki.zatrzymaj()`, 2769 / 2859 `excel.rozlacz()`, 2888 `ex.propozycje(...)`,
  2904 `ex.zapisz_cien_bez_odczytu(...)`, 2918 `zaloguj_poprawki`, 2927 `zaloguj_juz_odhaczone`, 2989 `k.tryb(...)`,
  3008 `k.wznow()`, 3022 `excel.zatwierdz(...)`, 3035 `excel.pomin(...)`; aplikacja.py:414 `IND.Indicate.z_ustawien`,
  427 / 593 `EX.Excel.z_ustawien` (okno, start).
* Zapisy w `session` / `session_rano` (poza zakresem) wolane w watku okna, m.in. aplikacja.py:1424, 1426, 1430, 1432
  (w transakcji 1418) i kontroler_api.py:2502 (w transakcji 2491).

---------------------------------------------------------------------------------------------------------------------

## Wystapienia BEZ limitu czasu

A: brak (kazde `join` / `wait` ma limit).

B: silnik.py:1045, silnik.py:1091, silnik.py:1097, silnik.py:1130, silnik.py:1140, silnik.py:1147, silnik.py:1150,
silnik.py:1191, silnik.py:1553, silnik.py:1583, silnik.py:1615, silnik.py:1631 (wszystkie: send / recv na laczu).

C: silnik.py:373, silnik.py:459 (czas w petli), silnik.py:1148, silnik.py:1406, scanner.py:535, scanner.py:573 (liczba
prob), aplikacja.py:1144, aplikacja.py:1457, aplikacja.py:1519, aplikacja.py:1531, aplikacja.py:1538.
Limit tylko czesciowy: silnik.py:617 (miedzy probami), aplikacja.py:1147 (sprawdzany po zdarzeniu), samokontrola.py:900
(miedzy katalogami).

D: aplikacja.py:1671 (QMessageBox), aplikacja.py:1723 (app.exec).

E: baza.py:583 (backup; poza tym kazde polecenie SQL ma limit tylko na blokade - `busy_timeout` - a nie na I/O pliku).

F (same wywolania nie maja limitu; wyjete sa tylko te, na ktore wolajacy czeka z limitem w samokontroli):
silnik.py: 240, 245, 439, 509, 510, 533, 575, 586, 587, 589, 597, 604, 619, 626, 627, 632, 633, 636 (619-636: limit
tylko miedzy probami), 960, 969, 972, 974, 975, 978, 992, 993, 1007, 1011, 1015, 1019, 1038, 1047, 1050, 1052, 1062,
1082, 1111, 1119, 1141, 1143, 1144, 1228;
aplikacja.py: 97, 166, 209, 217, 272, 273, 278, 282, 302, 303, 399, 533, 563, 604, 613, 616, 631, 637, 640, 652, 655,
657, 662, 696, 741, 803, 1046, 1047, 1257, 1281, 1497, 1578, 1586;
kontroler_api.py: 1478, 1479, 3124, 4013, 4093, 4386, 4387, 4577, 4701, 4703;
scanner.py: 149, 150, 180, 182, 245, 254, 391, 401, 465, 575, 626, 641, 660, 669, 679, 685, 687, 693, 697, 698;
baza.py: 319, 355, 357, 368, 374, 377, 407, 421, 422, 578, 580;
pula.py: 375, 377, 380, 386, 390;
pamiec_puli.py: 127, 129, 133, 136, 155, 176, 180, 215, 221, 236, 240, 267, 268, 269, 274, 281, 287, 291, 293, 295;
indeks.py: 85, 158, 167, 169, 171, 172, 198, 202, 203, 215, 216, 273;
ustawienia.py: 19, 220, 351, 356, 379;
samokontrola.py: 1379, 1409 (glowny watek); pozostale F w samokontrola.py - bez limitu same, ale wolajacy czeka
najwyzej limit `_z_limitem`.

G: silnik.py:1445 (`p.start()` sam bez limitu; nadzorca czeka najwyzej 30 s + 3 s, watek silnik-start moze zostac).

---------------------------------------------------------------------------------------------------------------------

## Pliki przeczytane

| plik | liczba linii (wg Read, z koncowym pustym wierszem) | przeczytany w calosci |
|---|---|---|
| silnik.py | 1824 | tak (1-827, 828-1327, 1328-1824) |
| aplikacja.py | 1731 | tak (1-450, 450-849, 850-1249, 1250-1699, 1700-1731) |
| kontroler_api.py | 4757 | tak (1-400, 400-849, 850-1299, 1300-1699, 1700-2098, 2099-2498, 2499-2898, 2899-3298, 3299-3698, 3699-4148, 4148-4597, 4597-4757) |
| scanner.py | 754 | tak (1-450, 450-754) |
| baza.py | 587 | tak (1-400, 400-587) |
| pula.py | 443 | tak |
| pamiec_puli.py | 300 | tak |
| indeks.py | 396 | tak |
| ustawienia.py | 380 | tak |
| samokontrola.py | 1433 | tak (1-500, 500-949, 949-1433) |
| __init__.py | 30 | tak |

Zadnego zakresu linii nie pominieto. Po przeczytaniu numery linii kategorii A, B, D, E, F, G sprawdzone Grepem.
