# S3 - wyliczenie 3: operacje mogace zamrozic okno, szerokie except, zamki i watki, sygnaly

Data: 2026-11-23. Analiza TYLKO DO ODCZYTU (bez uruchamiania). Worktree: `<PC-katalog>\qc-wt\analiza-s3`, kod: `Ramki\stanowisko`.
Bez oceny wagi i bez propozycji poprawek - samo wyliczenie i fakty.

## Zakres i metoda

- Czytane w calosci (Read): `stanowisko/indicate.py`, `ramka_protokol.py`, `excel.py`, `excel_com.py`, `ui/obraz.py`, `ramka/serwer.py`,
  `ramka/program.py`, `ramka/sprzet_atrapa.py`.
- Czytane fragmentami i przeszukane w calosci wzorcami (Grep: `baza.`, `open(`, `read_text`, `write_text`, `read_bytes`, `write_bytes`,
  `shutil`, `os.replace`, `unlink`, `mkdir`, `sleep(`, `.join(`, `.wait(`, `acquire`, `Lock`, `Thread`, `Event`, `Condition`, `Queue`,
  `subprocess`, `socket`, `urllib`, `http`, `win32`, `pythoncom`, `while `, `glob`, `except`, `QTimer`, `singleShot`, `Signal(`, `emit(`,
  `connect(`): `session.py` (Read 1-632 i 1265-1303), `session_rano.py` (Read 172-177, 196-321, 947-982, 1274-1352), `statusy.py`,
  `ui/*.py` (Read: mapa.py 40-79, okno.py 624-643 i 905-935, czesci.py 545-564), `ramka/sprzet_rpi.py` (Read 60-231),
  `ramka/kalibracja.py` (Read 80-294), `ramka/logika.py` (Read 128-139, 404-419), `ramka/test_led.py` (Read 40-130); `ramka/protokol.py`,
  `ramka/obraz.py`, `ramka/czcionka.py`, `ramka/sprzet.py`, `ramka/__init__.py`, `ramka/__main__.py` - tylko Grep (brak trafien
  poza stalymi: `protokol.py:68 CZEKAJ_MAX_S = 25.0`, klasy bledow).
- Watek wywolania: fragmenty `stanowisko/aplikacja.py` i `stanowisko/kontroler_api.py`.
- POZA ZAKRESEM, tylko po wartosc limitu SQLite: `stanowisko/baza.py:45`, `317-324`, `396-397`, `478-517`.
- `statusy.py`: brak operacji z listy i brak `try/except` (Grep `try:` - zero trafien) - 0 wierszy w A i B.

## Legenda

Skroty plikow (kolumna "watek" i "skutek"): `I:` indicate.py, `RP:` ramka_protokol.py, `E:` excel.py, `EC:` excel_com.py, `S:` session.py,
`SR:` session_rano.py, `K:` kontroler_api.py, `A:` aplikacja.py, `KAL:` ramka/kalibracja.py. Sciezki laptopa wzgledem
`Ramki/stanowisko/stanowisko/`, ramki wzgledem `Ramki/stanowisko/`.

Watki (laptop):
- `OKNO-Z` - watek okna, zegar Qt: `QTimer` K:1184-1187 (co 30 ms, K:128) -> `_tyk` K:1190 -> `Aplikacja.przetworz` A:1135 (A:1146,
  A:1155, A:1162, A:1174).
- `OKNO-P` - watek okna, polecenie z okna (slot Qt -> metoda kontrolera -> `_polecenie` K:3465, blok czekania na baze K:3483).
- `OKNO-S` - watek glowny = watek okna przy starcie: A:1705-1706 (`Aplikacja(...)`, `start()`) przed `app.exec()` A:1723.
- `OKNO-Q` - watek okna przy zamknieciu: A:1719 (`aboutToQuit`) albo A:1725 -> `Aplikacja.zamknij` A:1511.
- Dowod, ze polecenia i zegar kontrolera ida w watku okna: w `kontroler_api.py` jedynym obiektem czasu/watku jest `QTimer` K:1184
  (Grep `Thread|QTimer|moveToThread|invokeMethod|ThreadPool|Process|Queue|Lock|Event|Condition`); sygnaly lacznika sa emitowane
  synchronicznie z `_powiadom` K:1315-1323. W `aplikacja.py` watki A:701, A:761, A:808 licza tylko `pliki_stl` / `pula.KatalogPul` /
  `stan_pliku` (poza zakresem) i oddaja wynik przez kolejke A:481.
- `NIEUSTALONE` - brak wywolania w `aplikacja.py` / `kontroler_api.py` (Grep nazwy) albo tylko testy.

Limity SQLite (`PRAGMA busy_timeout`; ogranicza tylko czekanie na blokade innego programu - baza.py:479-494, nie czas zapytania
ani zapisu na dysk; K:115-118: zmierzone czekanie na Windows dluzsze niz wartosc):
- `B5000` - 5000 ms, stala `baza.py:45` (`CZEKAJ_NA_BLOKADE_MS`), ustawiana `baza.py:324`, domyslna `otworz` baza.py:397 (A:456 bez
  parametru) - obowiazuje poza blokami ponizej.
- `B200` - 200 ms, stala K:119, blok K:3483 (`_polecenie`) i K:3703.
- `BST` - budowa stanu: 100 ms (stala K:120, blok K:1347) albo 0 ms (K:121, K:1398); BEZ bloku (czyli B5000): pierwszy stan K:1330
  (A:583 przy starcie) i stan koncowy A:1555.
- `B150` - 150 ms, stala K:113, blok K:2250 / K:2299 (zapis zdarzen ramek).
- `Bwg` - zalezy od wolajacego (wymienione w wierszu); maksimum podane w wierszu.

Skutki (kolumna "skutek"):
- `P-BAZA` - polecenie: `BladBazy` -> odmowa `baza_zajeta` z "Ponow teraz" (K:3487-3488); `BladSesji` -> odmowa z tekstem (K:3485-3486);
  inny wyjatek -> log + `blad_polecenia` (K:3489-3492).
- `S-BAZA` - budowa stanu: zostaje poprzedni stan, nadrabianie z zegara (K:1349-1360); bez poprzedniego stanu wyjatek idzie dalej (K:1354-1355).
- `Z-BAZA` - zapis wyniku / bledu skanu: transakcja wycofana, pozycja czeka w `_do_zapisu` z komunikatem (A:1384-1392) albo skan "blad" (A:1393-1401).
- `R-BAZA` - zdarzenia ramek: odlozone, ponowienie najczesciej co 1 s (K:2245-2253).
- `RP-PLAN` - plan ramki P: ramka P zgaszona, komunikat, ponowienie co 2 s (K:2600-2611).
- `X-KROK` - krok Excela z zegara: `BladExcela` -> `_excel_blad_kroku` (K:2889-2891); inny wyjatek -> log + komunikat (K:2845-2853).
- `X-POL` - polecenie Excela: `BladExcela` -> `BladSesji` -> odmowa z tekstem (K:3023-3024, K:3036-3037, K:3049-3050, K:3063-3064).
- `Z-W` - zamek bez limitu: watek czeka, az inny watek zwolni zamek. W `indicate.py` pod `_warunek` watki robocze nie wykonuja I/O sieci
  (I:584-599 poza zamkiem); najdluzszy odcinek pod zamkiem to budowa i walidacja planu (I:1061 -> RP.plan_rano / RP.plan_wieczor ->
  `ramka.protokol.sprawdz_plan` z `deepcopy`, RP:168).

Cytaty sa skracane (`...`), zawsze z linii podanej w kolumnie plik:linia.

## Tabela A - operacje mogace czekac (310 wierszy)

### A.1 stanowisko/indicate.py

| nr | plik:linia | funkcja | operacja (cytat) | limit czasu | watek wywolania + dowod | po limicie / po wyjatku |
|---|---|---|---|---|---|---|
| 1 | indicate.py:243 | kursor | `with self._warunek:` | BRAK (RLock) | NIEUSTALONE - brak `.kursor` w A/K | Z-W |
| 2 | indicate.py:249 | uruchom | `with self._warunek:` | BRAK | OKNO-S: K:2074 <- A:584 <- A:569 | Z-W |
| 3 | indicate.py:267 | KlientRamki.zatrzymaj | `with self._warunek:` | BRAK | watek pomocniczy `zatrzymaj_klienta` (I:1318-1323) <- K:2760 <- A:1511 (OKNO-Q) | Z-W |
| 4 | indicate.py:282 | KlientRamki.zatrzymaj | `w.join(czas + 0.1)` | czas = min(0.6, ...) (I:276) + 0.1 s - stale | `zatrzymaj_klienta` (jw.) | dalej; zgaszenie niedoszle -> zwraca False (I:274, I:287) |
| 5 | indicate.py:285 | KlientRamki.zatrzymaj | `w.join(max(0.0, koniec - time.monotonic()))` | do start + 1.0 s (ZATRZYMANIE_S I:56, I:266) - stala | `zatrzymaj_klienta` | watki daemon zostaja, `_watki` czyszczone (I:286) |
| 6 | indicate.py:292 | _wyslij_przy_zamykaniu | `st, _ = self._zadanie(metoda, sciezka, ... timeout=czas,` | czas <= 0.6 s (I:276) | watek `indicate-<rola>-zamykanie` (I:279-281) | blad sieci/odpowiedzi -> log.warning (I:299-300), wynik False |
| 7 | indicate.py:296 | _wyslij_przy_zamykaniu | `with self._warunek:` | BRAK | `indicate-<rola>-zamykanie` | Z-W |
| 8 | indicate.py:305 | _przerwij_polaczenia | `with self._warunek:` | BRAK | `zatrzymaj_klienta` (wolane I:273, I:283) | Z-W |
| 9 | indicate.py:321 | wznow | `with self._warunek:` | BRAK | OKNO-P: K:3008 (`przejmij_ramke`, K:3012) | Z-W |
| 10 | indicate.py:335 | stan | `with self._warunek:` | BRAK | OKNO-Z: K:2115 <- K:2271; OKNO-S: A:419, K:2067; okno: K:2784 | Z-W; wyjatek -> log (K:2116-2118) |
| 11 | indicate.py:359 | odbierz_zdarzenia | `with self._warunek:` | BRAK | OKNO-Z: K:2241 <- K:2233.. <- A:1174 | Z-W; wyjatek -> log (K:2242-2243) |
| 12 | indicate.py:367 | czekaj | `with self._warunek:` | BRAK | NIEUSTALONE - brak `.czekaj(` w A/K | Z-W |
| 13 | indicate.py:374 | czekaj | `self._warunek.wait(min(pozostalo, 0.05))` (petla `while True` I:368) | timeout 5.0 s domyslnie (parametr I:364) | NIEUSTALONE | po czasie zwraca False (I:372-373) |
| 14 | indicate.py:377 | potwierdzone | `with self._warunek:` | BRAK | okno: K:2426 (zdarzenia ramki, K:2251, OKNO-Z) | Z-W |
| 15 | indicate.py:388 | znacznik | `with self._warunek:` | BRAK | OKNO-Z: K:2636 <- A:1272 | Z-W; wyjatek -> log (K:2637-2639) |
| 16 | indicate.py:412 | ustaw_plan_rano | `with self._warunek:` | BRAK | okno: K:2594 <- K:2268 (OKNO-Z) i K:1363 (`_po_odswiezeniu`) | Z-W; wyjatek -> RP-PLAN |
| 17 | indicate.py:439 | zgas | `with self._warunek:` | BRAK | okno: K:2562 (`_zgas_ramke_p`); OKNO-Q: K:2756 | Z-W; wyjatek -> log (K:2563-2564, K:2757-2758) |
| 18 | indicate.py:454 | tryb | `with self._warunek:` | BRAK | okno: K:2624 <- A:1127 (Spacja, OKNO-P); K:2651 <- A:1342 (OKNO-Z); K:2667, K:2694; K:2636 (rola W); OKNO-P: K:2989 | Z-W; wyjatek -> log (K:2626-2627, K:2652-2653, K:2668-2669) |
| 19 | indicate.py:486 | wynik | `with self._warunek:` | BRAK | okno: K:2716 (`_synchronizuj_ramke_w`, po K:1363) | Z-W |
| 20 | indicate.py:579 | _zadanie | `with self._warunek:` | BRAK | watki `indicate-<rola>-odpytywanie` / `-polecenia` / `-zamykanie` (I:256-257, I:279) | Z-W |
| 21 | indicate.py:584 | _zadanie | `sock = socket.create_connection((self.host, self.port), timeout=timeout or self._limit)` | argument `timeout` albo `limit_polaczenia_s` = 5.0 s (stala domyslna I:145; I:1300-1302 jej nie zmienia) | jw. | wpis "blad" w dzienniku ruchu, wyjatek do wolajacego (I:600-602) |
| 22 | indicate.py:585 | _zadanie | `with self._warunek:` | BRAK | jw. | Z-W |
| 23 | indicate.py:590 | _zadanie | `sock.sendall(glowa.encode("ascii") + (tresc or b""))` | timeout gniazda jak w 21 | jw. | jak 21 |
| 24 | indicate.py:593 | _zadanie | `b = sock.recv(65536)` (petla `while True` I:592) | timeout gniazda na kazde `recv` (jak 21); calej petli - BRAK (konczy ja `b""` albo > MAX_ODPOWIEDZI + 64 KiB, I:594-598) | jw. | jak 21 |
| 25 | indicate.py:605 | _zadanie | `with self._warunek:` | BRAK | jw. | Z-W |
| 26 | indicate.py:623 | _petla_odpytywania | `with self._warunek:` | BRAK | `indicate-<rola>-odpytywanie` (I:256-257) | Z-W |
| 27 | indicate.py:626 | _petla_odpytywania | `if self._wznow.wait(0.5):` | 0.5 s - stala | odpytywanie | kolejny obieg |
| 28 | indicate.py:640 | _petla_odpytywania | `stop.wait(self._przerwa_max * 5)` | 5 x `przerwa_max_s` (1.0 s, I:144) = 5 s | odpytywanie | kolejny obieg |
| 29 | indicate.py:643 | _petla_odpytywania | `with self._warunek:` | BRAK | odpytywanie | Z-W |
| 30 | indicate.py:650 | _petla_odpytywania | `with self._warunek:` | BRAK | odpytywanie | Z-W |
| 31 | indicate.py:655 | _petla_odpytywania | `if stop.wait(przerwa):` | 0.2..1.0 s (I:144, I:657) | odpytywanie | ponowna proba |
| 32 | indicate.py:668 | _ustaw_zly_klucz | `with self._warunek:` | BRAK | odpytywanie (I:678, I:754), polecenia (I:1002, I:1149) | Z-W |
| 33 | indicate.py:676 | _migawka | `st, d = self._zadanie("GET", "/stan", stop=stop)` | 5.0 s | odpytywanie | I:642-654: polaczona=False, bledy_sieci+1, przerwa |
| 34 | indicate.py:683 | _migawka | `with self._warunek:` | BRAK | odpytywanie | Z-W |
| 35 | indicate.py:745 | _odpytaj | `with self._warunek:` | BRAK | odpytywanie | Z-W |
| 36 | indicate.py:751 | _odpytaj | `st, d = self._zadanie("GET", f"/zdarzenia?od={od}&czekaj={czekaj:g}...", ... timeout=czekaj + self._limit` (I:752) | `[ramki] odpytywanie_s` (ustawienia, domyslnie 25.0 s - I:1301) + 5.0 s = 30 s; przy `_szybko` 0 + 5 s | odpytywanie | jak 33 |
| 37 | indicate.py:759 | _odpytaj | `with self._warunek:` | BRAK | odpytywanie | Z-W |
| 38 | indicate.py:925 | _petla_polecen | `with self._warunek:` | BRAK | `indicate-<rola>-polecenia` (I:256-257) | Z-W |
| 39 | indicate.py:932 | _petla_polecen | `self._warunek.wait(max(czas, 0.005))` | <= 0.2 s (I:928) - stala | polecenia | kolejny obieg |
| 40 | indicate.py:942 | _petla_polecen | `stop.wait(self._przerwa_max)` | 1.0 s (I:144) | polecenia | kolejny obieg |
| 41 | indicate.py:977 | _wykonaj_gaszace | `st, d = self._zadanie(metoda, sciezka, tresc, stop=stop)` | 5.0 s | polecenia | polecenie zostaje w kolejce, pauza, ponowienie (I:978-982) |
| 42 | indicate.py:979 | _wykonaj_gaszace | `with self._warunek:` | BRAK | polecenia | Z-W |
| 43 | indicate.py:983 | _wykonaj_gaszace | `with self._warunek:` | BRAK | polecenia | Z-W |
| 44 | indicate.py:1057 | _wykonaj_plan | `with self._warunek:` | BRAK | polecenia | Z-W (pod zamkiem budowa planu I:1061) |
| 45 | indicate.py:1093 | _wykonaj_plan | `st, d = self._zadanie("PUT", "/plan", tresc, stop=stop)` | 5.0 s | polecenia | zapamietane ponowienie tej samej tresci, pauza (I:1094-1101) |
| 46 | indicate.py:1095 | _wykonaj_plan | `with self._warunek:` | BRAK | polecenia | Z-W |
| 47 | indicate.py:1102 | _wykonaj_plan | `with self._warunek:` | BRAK | polecenia | Z-W |
| 48 | indicate.py:1113 | _stan_po_odmowie | `st, d = self._zadanie("GET", "/stan", stop=stop)` | 5.0 s | polecenia | return, zostaje warunek przyblizony (I:1117-1118) |
| 49 | indicate.py:1119 | _stan_po_odmowie | `with self._warunek:` | BRAK | polecenia | Z-W |
| 50 | indicate.py:1204 | wczytaj_kalibracje | `return RP.kalibracja_domyslna(katalog_modeli), [` (glob + odczyt `uklad.json`) | BRAK | OKNO-S: I:1290 <- A:414 <- A:577 <- A:569 <- A:1706 | None + ostrzezenie (I:1206-1207) |
| 51 | indicate.py:1209 | wczytaj_kalibracje | `kal = RP.wczytaj_kalibracje(sciezka)` | BRAK | OKNO-S (jw.) | BladKalibracji -> None + ostrzezenie (I:1210-1211); inny -> A:415 (ramki niepodlaczone) |
| 52 | indicate.py:1222 | _uzupelnij_kalibracje | `dane, dopisane = RP.uzupelnij_kalibracje(sciezka, katalog_modeli)` (odczyt, zapis .tmp, kopia, os.replace) | BRAK | OKNO-S (I:1212) | OSError -> uzupelnienie w pamieci (I:1223-1233); inny -> log, kalibracja z pliku (I:1234-1236) |
| 53 | indicate.py:1225 | _uzupelnij_kalibracje | `dopisane = RP.uzupelnij_kalibracje_w_pamieci(kal, katalog_modeli)` | BRAK | OKNO-S | log, (kal, []) (I:1226-1228) |
| 54 | indicate.py:1248 | identyfikator_laptopa | `tekst = plik.read_text(encoding="ascii").strip()` | BRAK | OKNO-S: I:1292 | nowy identyfikator (I:1251-1253) |
| 55 | indicate.py:1255 | identyfikator_laptopa | `plik.parent.mkdir(parents=True, exist_ok=True)` | BRAK | OKNO-S | OSError -> log.warning (I:1257-1258) |
| 56 | indicate.py:1256 | identyfikator_laptopa | `plik.write_text(lid + "\n", encoding="ascii")` | BRAK | OKNO-S | jak 55 |
| 57 | indicate.py:1264 | _zapisany_identyfikator | `return (Path(katalog) / PLIK_ID_LAPTOPA).read_text(encoding="ascii").strip() == lid` | BRAK | OKNO-S: I:1293 | False -> ostrzezenie (I:1293-1297) |
| 58 | indicate.py:1326 | Indicate.zatrzymaj | `w.join(max(0.0, koniec - time.monotonic()))` | 1.0 s (I:56, K:2760 bez argumentu) + 0.1 s (I:1324) = 1.1 s | OKNO-Q: K:2760 <- A:1511 | zwraca zebrane wyniki; False -> log.warning (K:2761-2763) |

### A.2 stanowisko/ramka_protokol.py

| nr | plik:linia | funkcja | operacja (cytat) | limit czasu | watek wywolania + dowod | po limicie / po wyjatku |
|---|---|---|---|---|---|---|
| 59 | ramka_protokol.py:70 | wczytaj_kalibracje | `return KAL.wczytaj(sciezka)` (read_text KAL:165) | BRAK | OKNO-S: I:1209 | BladKalibracji do wolajacego |
| 60 | ramka_protokol.py:76 | kalibracja_domyslna | `return KAL.domyslna(katalog_modeli)` (glob + read_text KAL:94-95) | BRAK | OKNO-S: I:1204 | wyjatek do wolajacego (I:1206) |
| 61 | ramka_protokol.py:83 | uzupelnij_kalibracje | `return KAL.uzupelnij_plik(sciezka, katalog_modeli)` (KAL:204-227) | BRAK | OKNO-S: I:1222 | OSError do wolajacego |
| 62 | ramka_protokol.py:88 | uzupelnij_kalibracje_w_pamieci | `return KAL.uzupelnij(kal, katalog_modeli)` (KAL:184 -> odczyt uklad.json) | BRAK | OKNO-S: I:1225 | wyjatek do wolajacego |

### A.3 stanowisko/excel.py

| nr | plik:linia | funkcja | operacja (cytat) | limit czasu | watek wywolania + dowod | po limicie / po wyjatku |
|---|---|---|---|---|---|---|
| 63 | excel.py:603 | z_ustawien.zrodlo (fabryka) | `return excel_com.polacz(konf.skoroszyt, konf.arkusz)` | BRAK (COM) | okno, wolane z E:624 | BladExcela "Excel niedostepny" (E:625-626) |
| 64 | excel.py:624 | zrodlo | `self._zrodlo = self._fabryka()` | BRAK | okno: E:648, E:668, E:851 (wolajacy jak 66) | jak 63 |
| 65 | excel.py:636 | rozlacz | `zwolnij()` (ArkuszCom.zwolnij tylko zeruje referencje COM, EC:111) | BRAK | okno: E:644; OKNO-Q: K:2769; OKNO-Z: K:2859 | wyjatek pomijany (E:637-638) |
| 66 | excel.py:650 | odswiez | `wartosci = z.odczytaj(self.konf.pierwszy_wiersz, self.konf.ostatnia_kolumna)` | BRAK | OKNO-Z: E:729 <- K:2888 <- K:2840 <- K:2233 <- A:1174; E:1000 <- K:2918; E:850 <- K:2927. OKNO-P: E:850 <- K:3022; K:3048, K:3062 -> K:2888. E:711 - NIEUSTALONE | rozlaczenie, BladExcela (E:652-654) -> X-KROK / X-POL |
| 67 | excel.py:651 | odswiez | `skoroszyt, sciezka, arkusz = str(getattr(z, "skoroszyt", "")), str(getattr(z, "sciezka", "")), ...` (Workbook.Name, FullName, Worksheet.Name) | BRAK | jak 66 | jak 66 |
| 68 | excel.py:668 | _wypelnienie | `return self.zrodlo().wypelnienie(nr, self._kol_b)` | BRAK | okno: przez `dopasuj` (E:680 -> E:447), E:702, `_kolor_b` E:676 (E:862, E:884, E:906); wolajacy jak 66 | rozlaczenie, BladExcela (E:671-673) |
| 69 | excel.py:692 | _sprawdz_piec | `w = self.baza.wiersz("SELECT zamknieto FROM sesje_pieca WHERE id = ?", (sesja_pieca_id,))` | B5000 (OKNO-Z) / B200 (OKNO-P) | E:728 (propozycje, jak 66), E:837 (<- K:3022); E:710 - NIEUSTALONE | X-KROK / P-BAZA |
| 70 | excel.py:716 | _zlecenie | `w = self.baza.wiersz("SELECT folder, kuweta, zrodlo FROM zlecenia WHERE id = ?", (zlecenie_id,))` | B5000 / B200 | E:733 (propozycje), E:1003 (<- K:2918) | BladBazy nie jest lapany w E:735 -> X-KROK (K:2845-2853) albo P-BAZA |
| 71 | excel.py:757 | _sprawdz_log | `self.konf.log.parent.mkdir(parents=True, exist_ok=True)` | BRAK | OKNO-P: E:877 <- K:3022 | OSError -> BladExcela (E:760-761) -> X-POL |
| 72 | excel.py:758 | _sprawdz_log | `with open(self.konf.log, "a", encoding="utf-8"):` | BRAK | jak 71 | jak 71 |
| 73 | excel.py:766 | _dopisz_csv | `plik.parent.mkdir(parents=True, exist_ok=True)` | BRAK | okno: E:787 <- `_loguj` <- `_zalatw` E:919 <- K:3022, K:3035 (OKNO-P); K:2904, K:2918, K:2927 (OKNO-Z) | OSError -> wpis w bazie, potem BladExcela (E:788-802) |
| 74 | excel.py:768 | _dopisz_csv | `with open(plik, "a", encoding="utf-8-sig" if nowy else "utf-8", newline="") as f:` | BRAK | jak 73 | jak 73 |
| 75 | excel.py:793 | _loguj | `id_wpisu = self.baza.wstaw("excel_zapisy", czas=teraz.isoformat(), ...` | B200 (K:3022, K:3035) / B5000 (K:2904, K:2918, K:2927) | jak 73 | BladExcela z opisem, gdzie jest wpis (E:797-799) |
| 76 | excel.py:879 | zatwierdz | `z.ustaw_wypelnienie(nr, self._kol_b, self.konf.kolor)` | BRAK (jedno wywolanie COM, EC:142) | OKNO-P: K:3022 (droga K:2927 konczy sie przed zapisem - E:863-866) | odczyt koloru, do 3 prob albo odmowa "sprawdz recznie" (E:880-900) |
| 77 | excel.py:896 | zatwierdz | `self._czekaj(PRZERWA_PONOWIENIA_S)` (= time.sleep, E:591) | 0.5 s - stala E:75; najwyzej 2 razy (PONOWIENIA_ZAPISU = 3, E:74) | OKNO-P: K:3022 | kolejna proba calego kroku (E:897) |
| 78 | excel.py:905 | zatwierdz | `po = {r: _surowy(z.wiersz(r, self.konf.ostatnia_kolumna)) for r in (nr - 1, nr, nr + 1) ...}` | BRAK | OKNO-P: K:3022 | rozlaczenie, odmowa "sprawdz recznie" (E:907-909) |

### A.4 stanowisko/excel_com.py (kazde wywolanie COM; limit czasu BRAK - w zakresie brak CoInitialize, filtra wiadomosci i limitu; Grep `CoInitialize|MessageFilter|pythoncom`)

| nr | plik:linia | funkcja | operacja (cytat) | limit czasu | watek wywolania + dowod | po limicie / po wyjatku |
|---|---|---|---|---|---|---|
| 79 | excel_com.py:54 | polacz | `aplikacja = klient.GetActiveObject("Excel.Application")` | BRAK | okno: E:603 <- E:624 (jak 64) | BladCom "Excel nie jest uruchomiony" (EC:55-56) |
| 80 | excel_com.py:63 | _skoroszyt | `wb = aplikacja.ActiveWorkbook` | BRAK | okno: EC:57 | wyjatek -> E:625-626 |
| 81 | excel_com.py:68 | _skoroszyt | `otwarte = list(aplikacja.Workbooks)` | BRAK | okno: EC:57 | jak 80 |
| 82 | excel_com.py:69 | _skoroszyt | `pasujace = [wb for wb in otwarte if str(wb.Name).casefold() == w] or ...` | BRAK | okno: EC:57 | jak 80 |
| 83 | excel_com.py:79 | _arkusz | `return wb.ActiveSheet` | BRAK | okno: EC:58 | jak 80 |
| 84 | excel_com.py:81 | _arkusz | `return wb.Worksheets(nazwa)` | BRAK | okno: EC:58 | BladCom (EC:82-83) |
| 85 | excel_com.py:99 | nazwa | `return str(self._arkusz().Name)` | BRAK | okno: E:651 | E:652-654 |
| 86 | excel_com.py:103 | skoroszyt | `return str(self._wb.Name) if self._wb is not None else ""` | BRAK | okno: E:651 | E:652-654 |
| 87 | excel_com.py:107 | sciezka | `return str(getattr(self._wb, "FullName", "")) if self._wb is not None else ""` | BRAK | okno: E:651 | E:652-654 |
| 88 | excel_com.py:114 | _ostatni_wiersz | `uzyty = self._arkusz().UsedRange` | BRAK | okno: EC:125 <- E:650 | E:652-654 |
| 89 | excel_com.py:115 | _ostatni_wiersz | `return int(uzyty.Row) + int(uzyty.Rows.Count) - 1` | BRAK | okno: jak 88 | E:652-654 |
| 90 | excel_com.py:119 | _zakres | `v = ws.Range(ws.Cells(w1, k1), ws.Cells(w2, k2)).Value` | BRAK | okno: EC:128 <- E:650; EC:131 <- E:905 | E:652-654 / E:907-909 |
| 91 | excel_com.py:134 | wypelnienie | `wnetrze = self._arkusz().Cells(nr, kolumna).Interior` | BRAK | okno: E:668 | E:671-673 |
| 92 | excel_com.py:135 | wypelnienie | `if int(wnetrze.ColorIndex) == XL_BRAK_WYPELNIENIA:` | BRAK | okno: E:668 | E:671-673 |
| 93 | excel_com.py:137 | wypelnienie | `return kolor_na_rgb(wnetrze.Color)` | BRAK | okno: E:668 | E:671-673 |
| 94 | excel_com.py:142 | ustaw_wypelnienie | `self._arkusz().Cells(nr, kolumna).Interior.Color = rgb_na_kolor(rgb)` | BRAK | OKNO-P: E:879 <- K:3022 | BladCom (EC:145-146) -> E:880 |

### A.5 stanowisko/session.py (wszystkie wywolania w watku okna; brak zamkow i watkow w pliku)

| nr | plik:linia | funkcja | operacja (cytat) | limit czasu | watek wywolania + dowod | po limicie / po wyjatku |
|---|---|---|---|---|---|---|
| 95 | session.py:299 | z_ustawien | `baza = B.otworz(B.sciezka_bazy(ust))` | B5000 (baza.py:397) | NIEUSTALONE - w programie baza podawana (A:456, A:461), galaz nie wykonywana | - |
| 96 | session.py:396 | przyjmij_wynik | `with self.baza.transakcja():` (zagniezdzona w A:1418, BEGIN IMMEDIATE baza.py:512) | B5000 | OKNO-Z: A:1426 <- A:1383 <- A:1146 / A:1155; SR:300 <- A:1424 | Z-BAZA |
| 97 | session.py:399 | przyjmij_wynik | `skan_id = self.baza.wstaw(` | B5000 | jak 96 | Z-BAZA |
| 98 | session.py:423 | przyjmij_wynik | `self.baza.zdarzenie("silnik", ZDARZENIE_PRZYPISAN, {"wpisy": do_wyboru, ...` | B5000 | jak 96 | Z-BAZA |
| 99 | session.py:427 | przyjmij_wynik | `self.baza.wykonaj("UPDATE skany SET wynik_json = ? WHERE id = ?", (self._zapisz_wynik(wynik, teraz, sha16), skan_id))` | B5000 | jak 96 | Z-BAZA |
| 100 | session.py:428 | przyjmij_wynik | `self.baza.zdarzenie("silnik", "skan_przyjety", {"status": status, ...` | B5000 | jak 96 | Z-BAZA |
| 101 | session.py:432 | przyjmij_wynik | `self.baza.zdarzenie("system", "konflikt_projektu", {"sha16": nowe}, ...` | B5000 | jak 96 | Z-BAZA |
| 102 | session.py:449 | przyjmij_blad | `with self.baza.transakcja():` | B5000 | OKNO-Z: A:1432; SR:311 <- A:1430 | Z-BAZA |
| 103 | session.py:450 | przyjmij_blad | `skan_id = self.baza.wstaw("skany", plik=str(plik), sha16=_pole(zdarzenie, "sha16"), ...` | B5000 | jak 102 | Z-BAZA |
| 104 | session.py:453 | przyjmij_blad | `self.baza.zdarzenie("silnik", "blad_analizy", {"typ": typ, "opis": opis}, ...` | B5000 | jak 102 | Z-BAZA |
| 105 | session.py:469 | _wstaw_prace | `return self.baza.wstaw(` | B5000 | S:411 (jak 96) | Z-BAZA |
| 106 | session.py:483 | _projekt | `w = self.baza.wiersze("SELECT id FROM projekty WHERE sha16 = ? AND usuniety = 0 ORDER BY id LIMIT 2", (sha16,))` | B5000 | S:492 <- S:466 (jak 96) | Z-BAZA |
| 107 | session.py:497 | _projekt_kandydata | `return pid if self.baza.wiersz("SELECT id FROM projekty WHERE id = ? AND usuniety = 0", (pid,)) else None` | B5000 | S:466 | Z-BAZA |
| 108 | session.py:507 | _frezowanie | `if wskazany is not None and self.baza.wiersz("SELECT id FROM frezowania WHERE id = ?", (wskazany,)):` | B5000 | S:467 | Z-BAZA |
| 109 | session.py:511 | _frezowanie | `w = self.baza.wiersze("SELECT id FROM frezowania WHERE projekt_id = ? ORDER BY id LIMIT 2", (projekt_id,))` | B5000 | S:467 | Z-BAZA |
| 110 | session.py:523 | _zapisz_wynik | `self.katalog_wynikow.mkdir(parents=True, exist_ok=True)` | BRAK | OKNO-Z: S:427 (w transakcji S:396) | wyjatek wycofuje transakcje -> Z-BAZA |
| 111 | session.py:531 | _zapisz_wynik | `with open(cel, "x", encoding="utf-8") as f:` (petla `while True` S:528 po nazwach _2, _3...) | BRAK | jak 110 | FileExistsError -> nastepna nazwa (S:534-535); inny -> jak 110 |
| 112 | session.py:549 | osierocone_wyniki | `for w in self.baza.wiersze("SELECT wynik_json FROM skany WHERE wynik_json IS NOT NULL"):` | B5000 | NIEUSTALONE - brak wywolania w A/K | - |
| 113 | session.py:552 | osierocone_wyniki | `return sorted(x for x in self.katalog_wynikow.glob("*_wynik.json") if x.resolve() not in znane)` | BRAK | NIEUSTALONE | - |
| 114 | session.py:556 | sciezka_wyniku | `w = self.baza.wiersz("SELECT wynik_json FROM skany WHERE id = ?", (skan_id,))` | Bwg: BST (max B5000) / B200 | okno: K:1477 (`_wynik_skanu` <- K:1489, K:3295) | S-BAZA / P-BAZA |
| 115 | session.py:592 | decyzja | `with self.baza.transakcja():` | B200 | OKNO-P: K:3618; K:3623 (przez S:632) | P-BAZA |
| 116 | session.py:596 | decyzja | `decyzja_id = self.baza.wstaw("decyzje", praca_id=praca["id"], rodzaj=rodzaj, operator=osoba, czas=teraz)` | B200 | jak 115 | P-BAZA |
| 117 | session.py:599 | decyzja | `self.baza.zdarzenie("system", "ukruszona_powtorzona", {` | B200 | jak 115 | P-BAZA |
| 118 | session.py:608 | _punkt_na_liscie | `return self.baza.wiersz(` | B200 | S:594 | P-BAZA |
| 119 | session.py:618 | pozycja_projektu | `praca = self.baza.wiersz("SELECT id, projekt_id FROM prace WHERE id = ?", (praca_id,))` | B5000 (domyslne) | NIEUSTALONE - brak wywolania w A/K | - |
| 120 | session.py:637 | cofnij | `with self.baza.transakcja():` | B200 | OKNO-P: K:3626 | P-BAZA |
| 121 | session.py:642 | cofnij | `decyzja_id = self.baza.wstaw("decyzje", praca_id=praca["id"], rodzaj=RODZAJ_COFNIECIE, ...` | B200 | jak 120 | P-BAZA |
| 122 | session.py:654 | _przypisania_skanow | `for w in self.baza.wiersze(f"SELECT dane FROM zdarzenia WHERE zrodlo = 'silnik' AND typ = ? AND skan_id IN (...) "` | Bwg: B200 (S:722, S:754) / BST (S:1150; max B5000) | okno | P-BAZA / S-BAZA |
| 123 | session.py:673 | wpis_puli_pracy | `for w in self.baza.wiersze("SELECT dane FROM zdarzenia WHERE zrodlo = 'silnik' AND typ = ? AND skan_id = ? ORDER BY id DESC",` | Bwg: B200 (S:728; SR:583 <- SR:573) / B5000 (SR:583 <- SR:303 <- A:1424) | okno | P-BAZA / Z-BAZA |
| 124 | session.py:689 | _wybory_wpisow | `decyzje = self.baza.wiersze(f"SELECT * FROM decyzje WHERE rodzaj IN (?, ?) AND praca_id IN (...) ORDER BY id",` | Bwg: B200 (S:714, S:721) / BST (S:1151) | okno | P-BAZA / S-BAZA |
| 125 | session.py:701 | _przypisz_wpis | `self.baza.wykonaj("UPDATE prace SET frezowanie_id = ?, projekt_id = ? WHERE id = ?", ...` | B200 | S:726, S:732, S:764 | P-BAZA |
| 126 | session.py:712 | cofnij_wpis | `with self.baza.transakcja():` | B200 | OKNO-P: K:3633 | P-BAZA |
| 127 | session.py:719 | cofnij_wpis | `decyzja_id = self.baza.wstaw("decyzje", praca_id=praca["id"], skan_id=praca["skan_id"], rodzaj=RODZAJ_COFNIJ_WPIS, ...` | B200 | jak 126 | P-BAZA |
| 128 | session.py:730 | cofnij_wpis | `if pid is not None and not self.baza.wiersz("SELECT id FROM projekty WHERE id = ? AND usuniety = 0", (pid,)):` | B200 | jak 126 | P-BAZA |
| 129 | session.py:740 | _projekt_wpisu | `fr = self.baza.wiersz("SELECT projekt_id FROM frezowania WHERE id = ?", (fid,))` | B200 | S:726, S:761 | P-BAZA |
| 130 | session.py:752 | wybierz_wpis | `with self.baza.transakcja():` | B200 | OKNO-P: K:3629 | P-BAZA |
| 131 | session.py:759 | wybierz_wpis | `if self.baza.wiersz("SELECT id FROM frezowania WHERE id = ?", (fid,)) is None:` | B200 | jak 130 | P-BAZA |
| 132 | session.py:762 | wybierz_wpis | `decyzja_id = self.baza.wstaw("decyzje", praca_id=praca["id"], skan_id=praca["skan_id"], rodzaj=RODZAJ_WYBOR_WPISU, ...` | B200 | jak 130 | P-BAZA |
| 133 | session.py:784 | cofnij_zastapienie | `with self.baza.transakcja():` | B200 | OKNO-P: K:3656 <- K:3678; SR:355 <- K:3656 | P-BAZA |
| 134 | session.py:792 | cofnij_zastapienie | `decyzja_id = self.baza.wstaw("decyzje", skan_id=nowy["id"], rodzaj=RODZAJ_COFNIJ_ZASTAPIENIE, ...` | B200 | jak 133 | P-BAZA |
| 135 | session.py:794 | cofnij_zastapienie | `self.baza.wykonaj("UPDATE skany SET status = ? WHERE id = ?", (self._status_z_prac(stary["id"]), stary["id"]))` | B200 | jak 133 | P-BAZA |
| 136 | session.py:795 | cofnij_zastapienie | `self.baza.wykonaj("UPDATE skany SET zastepuje_id = NULL WHERE id = ?", (nowy["id"],))` | B200 | jak 133 | P-BAZA |
| 137 | session.py:807 | dopusc_plytke | `with self.baza.transakcja():` | B200 | OKNO-P: K:3656 <- K:3681; S:574 | P-BAZA |
| 138 | session.py:812 | dopusc_plytke | `decyzja_id = self.baza.wstaw("decyzje", skan_id=skan_id, rodzaj="uklad", wartosc=DOPUSC_PLYTKE, operator=osoba, czas=teraz)` | B200 | jak 137 | P-BAZA |
| 139 | session.py:814 | dopusc_plytke | `self.baza.wykonaj("UPDATE skany SET status = ? WHERE id = ?", (status, skan_id))` | B200 | jak 137 | P-BAZA |
| 140 | session.py:816 | dopusc_plytke | `self.baza.zdarzenie("ui", "plytka_nie_z_trybu_dopuszczona", {"decyzja_id": decyzja_id, ...` | B200 | jak 137 | P-BAZA |
| 141 | session.py:824 | cofnij_dopuszczenie | `with self.baza.transakcja():` | B200 | OKNO-P: K:3656 <- K:3684; SR:410; S:576 | P-BAZA |
| 142 | session.py:826 | cofnij_dopuszczenie | `dopuszczenia = self.baza.wiersze("SELECT id FROM decyzje WHERE skan_id = ? AND rodzaj = 'uklad' AND wartosc = ? ORDER BY id", ...` | B200 | jak 141 | P-BAZA |
| 143 | session.py:827 | cofnij_dopuszczenie | `cofniete = {int(d["wartosc"]) for d in self.baza.wiersze("SELECT wartosc FROM decyzje WHERE skan_id = ? AND praca_id IS NULL AND rodzaj = ?",` | B200 | jak 141 | P-BAZA |
| 144 | session.py:836 | cofnij_dopuszczenie | `decyzja_id = self.baza.wstaw("decyzje", skan_id=skan_id, rodzaj=RODZAJ_COFNIECIE, wartosc=str(obowiazujace[-1]), ...` | B200 | jak 141 | P-BAZA |
| 145 | session.py:837 | cofnij_dopuszczenie | `self.baza.wykonaj("UPDATE skany SET status = ? WHERE id = ?", (STATUS_PLYTKA_NIE_Z_TRYBU, skan_id))` | B200 | jak 141 | P-BAZA |
| 146 | session.py:839 | cofnij_dopuszczenie | `self.baza.zdarzenie("ui", "plytka_nie_z_trybu_blokada_przywrocona", {"decyzja_id": decyzja_id}, ...` | B200 | jak 141 | P-BAZA |
| 147 | session.py:844 | _przelicz_punkty_skanu | `for praca in self.baza.wiersze("SELECT * FROM prace WHERE skan_id = ? AND projekt_id IS NOT NULL ORDER BY id", (sk["id"],)):` | B200 | S:796, S:815, S:838, S:1037 | P-BAZA |
| 148 | session.py:856 | podaj_numer_plytki | `with self.baza.transakcja():` | B200 (blok K:3703) | OKNO-P: K:3721 | P-BAZA |
| 149 | session.py:858 | podaj_numer_plytki | `powiazane = self.baza.wiersze("SELECT * FROM skany WHERE zastepuje_id = ? OR id = ?", (skan_id, sk["zastepuje_id"]))` | B200 | jak 148 | P-BAZA |
| 150 | session.py:863 | podaj_numer_plytki | `decyzja_id = self.baza.wstaw("decyzje", skan_id=skan_id, rodzaj="numer_plytki", wartosc=str(n), ...` | B200 | jak 148 | P-BAZA |
| 151 | session.py:864 | podaj_numer_plytki | `self.baza.wykonaj("UPDATE skany SET numer_plytki = ?, numer_zrodlo = 'podany' WHERE id = ?", (n, skan_id))` | B200 | jak 148 | P-BAZA |
| 152 | session.py:868 | _skan | `sk = self.baza.wiersz("SELECT * FROM skany WHERE id = ?", (skan_id,)) if skan_id is not None else None` | B200 | S:785, S:788, S:808, S:825, S:857, S:1005, S:1014 | P-BAZA |
| 153 | session.py:875 | _status_z_prac | `n = self.baza.wiersz(` | B200 | S:794, S:813 | P-BAZA |
| 154 | session.py:884 | _praca_do_decyzji | `praca = self.baza.wiersz("SELECT p.*, s.status AS status_skanu, s.tryb AS tryb_skanu FROM prace p JOIN skany s ON s.id = p.skan_id "` | B200 | S:593, S:638, S:713, S:753 | P-BAZA |
| 155 | session.py:902 | _decyzja_pracy | `return _obowiazujace(self.baza.wiersze("SELECT * FROM decyzje WHERE praca_id = ? ORDER BY id", (praca_id,))).get(praca_id)` | B200 | S:639, S:1056 | P-BAZA |
| 156 | session.py:907 | _decyzje_skanow | `return _obowiazujace(self.baza.wiersze(` | Bwg: B200 (S:1074) / BST (S:1146, S:1208) / B5000 (S:1289 <- `konflikty` <- S:397, S:430) | okno | P-BAZA / S-BAZA / Z-BAZA |
| 157 | session.py:940 | _projekty_rozpoznane | `return {p["kandydat1_sha16"] for p in self.baza.wiersze("SELECT kandydat1_sha16, status_match FROM prace WHERE skan_id = ?", (skan_id,))` | Bwg: BST (S:952 <- S:967 <- S:1155) / B200 (S:999 <- S:1009) / BST, B5000 (SR:485 <- SR:890 `_oblicz`) | okno | P-BAZA / S-BAZA / RP-PLAN |
| 158 | session.py:981 | _propozycja_zastapienia | `cofniete = {int(d["wartosc"]) for d in self.baza.wiersze("SELECT wartosc FROM decyzje WHERE skan_id = ? AND rodzaj = ?",` | Bwg: BST (S:1155) / B200 (S:999) | okno | S-BAZA / P-BAZA |
| 159 | session.py:983 | _propozycja_zastapienia | `kandydaci = self.baza.wiersze(` | jak 158 | okno | jak 158 |
| 160 | session.py:1004 | _zastap | `with self.baza.transakcja():` | B200 | S:775 (`zastap_skan` <- K:3656 <- K:3663; SR:349); S:580 | P-BAZA |
| 161 | session.py:1034 | _zastap | `decyzja_id = self.baza.wstaw("decyzje", skan_id=nowy["id"], rodzaj="powtorz_skan", wartosc=str(poprzedni["id"]), ...` | B200 | jak 160 | P-BAZA |
| 162 | session.py:1035 | _zastap | `self.baza.wykonaj("UPDATE skany SET status = ? WHERE id = ?", (STATUS_ZASTAPIONY, poprzedni["id"]))` | B200 | jak 160 | P-BAZA |
| 163 | session.py:1036 | _zastap | `self.baza.wykonaj("UPDATE skany SET zastepuje_id = ? WHERE id = ?", (poprzedni["id"], nowy["id"]))` | B200 | jak 160 | P-BAZA |
| 164 | session.py:1059 | _odswiez_punkt | `punkt = self.baza.wiersz("SELECT * FROM stan_punktow WHERE projekt_id = ?", (projekt_id,))` | B200 | S:597, S:644, S:704, S:705, S:845 | P-BAZA |
| 165 | session.py:1071 | _najnowsza_ukruszona | `prace = self.baza.wiersze(` | B200 | S:1062 | P-BAZA |
| 166 | session.py:1079 | _ustaw_punkt | `self.baza.wykonaj(` | B200 | S:1064, S:1066 | P-BAZA |
| 167 | session.py:1092 | _skany_sesji | `return self.baza.wiersze(sql + " ORDER BY id", parametry)` | Bwg: BST (S:1144) / B5000 (S:1287 <- `konflikty` <- S:397, S:430) | okno | S-BAZA / Z-BAZA |
| 168 | session.py:1097 | _prace_skanow | `return self.baza.wiersze(` | Bwg: BST (S:1148, S:1210, S:1235) / B5000 (S:1291) | okno | S-BAZA / Z-BAZA |
| 169 | session.py:1227 | do_dofrezowania | `decyzje = _obowiazujace(self.baza.wiersze(` | Bwg: BST (S:1192) / B200 (S:1274 <- K:4013) | okno | S-BAZA / P-BAZA |
| 170 | session.py:1262 | _wiersze_po_id | `wynik += self.baza.wiersze(sql.format(_znaki(len(czesc))), tuple(czesc))` | jak 169 (S:1233, S:1234) | okno | jak 169 |
| 171 | session.py:1269 | zapisz_do_dofrezowania | `katalog.mkdir(parents=True, exist_ok=True)` | BRAK | okno: K:4013 (`zapisz_liste`, OKNO-P), K:3124 (`_zapisz_liste_po_zmianie`) | wyjatek do wolajacego (K:4013 -> P-BAZA) |
| 172 | session.py:1271 | zapisz_do_dofrezowania | `with open(cel, "w", newline="", encoding="utf-8") as f:` | BRAK | jak 171 | jak 171 |

### A.6 stanowisko/session_rano.py (wszystkie wywolania w watku okna; brak zamkow i watkow w pliku)

| nr | plik:linia | funkcja | operacja (cytat) | limit czasu | watek wywolania + dowod | po limicie / po wyjatku |
|---|---|---|---|---|---|---|
| 173 | session_rano.py:199 | _ostatnia_aktywnosc | `skany = self.baza.wiersze("SELECT id, czas_analizy, uklad FROM skany WHERE sesja_pieca_id = ? AND status = ? AND czas_analizy IS NOT NULL",` | Bwg jak 174 (max B5000) | okno: SR:216 (`_biezacy` <- `otwarty_piec`, `otwarte_piece`) | jak 174 |
| 174 | session_rano.py:222 | otwarty_piec | `for w in self.baza.wiersze("SELECT * FROM sesje_pieca WHERE zamknieto IS NULL ORDER BY id DESC"):` | Bwg: BST (K:1968) / B5000 (K:2576 i SR:1289 <- K:2590, po K:1363; SR:317 <- A:1424, A:1430) / B150 (K:2457, K:2490) / B200 (SR:997) | okno | S-BAZA / RP-PLAN / Z-BAZA / R-BAZA |
| 175 | session_rano.py:233 | otwarte_piece | `for w in self.baza.wiersze("SELECT * FROM sesje_pieca WHERE zamknieto IS NULL ORDER BY id")]` | Bwg: BST (K:2034; SR:874) / B5000 (SR:874 <- `plan_plytek`) / B200 (SR:1069, SR:1163) | okno | S-BAZA / RP-PLAN / P-BAZA |
| 176 | session_rano.py:237 | _ostatni_zamkniety_w_dobie | `w = self.baza.wiersz("SELECT * FROM sesje_pieca WHERE zamknieto IS NOT NULL ORDER BY zamknieto DESC, id DESC LIMIT 1")` | BST (max B5000) | okno: SR:955 (`stan_pieca` bez id, K:1972) | S-BAZA |
| 177 | session_rano.py:243 | otworz_piec | `with self.baza.transakcja():` | B5000 | NIEUSTALONE - brak wywolania w A/K | - |
| 178 | session_rano.py:252 | _otworz | `nr = self.baza.wiersz("SELECT count(*) AS n FROM sesje_pieca WHERE data = ?", (data,))["n"] + 1` | Bwg: B5000 (SR:318 <- A:1424, A:1430) / B200 (SR:1022 <- K:3809) | okno | Z-BAZA / P-BAZA |
| 179 | session_rano.py:253 | _otworz | `pid = self.baza.wstaw("sesje_pieca", data=data, nr_w_dniu=nr, otwarto=teraz)` | jak 178 | okno | jak 178 |
| 180 | session_rano.py:254 | _otworz | `self.baza.zdarzenie(zrodlo, TYP_OTWARTY, {"sesja_pieca_id": pid, "data": data, "nr_w_dniu": nr}, czas=teraz)` | jak 178 | okno | jak 178 |
| 181 | session_rano.py:258 | _piec_po_id | `w = self.baza.wiersz("SELECT * FROM sesje_pieca WHERE id = ?", (sesja_pieca_id,))` | Bwg: BST (SR:959 <- K:1908) / B5000 (SR:959 <- SR:1296 <- K:2590) / B200 (SR:1028) | okno | S-BAZA / RP-PLAN / P-BAZA |
| 182 | session_rano.py:265 | _piec_otwarty_dla | `w = self.baza.wiersz("SELECT * FROM sesje_pieca WHERE id = ?", (sesja_pieca_id,)) if sesja_pieca_id is not None else None` | B200 | SR:327, SR:507 | P-BAZA |
| 183 | session_rano.py:282 | piece | `wiersze = self.baza.wiersze(` | BST (max B5000) | okno: K:1965 | S-BAZA |
| 184 | session_rano.py:298 | przyjmij_wynik | `with self.baza.transakcja():` (zagniezdzona w A:1418) | B5000 | OKNO-Z: A:1424 <- A:1383 | Z-BAZA |
| 185 | session_rano.py:301 | przyjmij_wynik | `self.baza.wykonaj("UPDATE skany SET sesja_pieca_id = ? WHERE id = ?", (pid, skan_id))` | B5000 | jak 184 | Z-BAZA |
| 186 | session_rano.py:302 | przyjmij_wynik | `for p in self.baza.wiersze("SELECT * FROM prace WHERE skan_id = ? ORDER BY id", (skan_id,)):` | B5000 | jak 184 | Z-BAZA |
| 187 | session_rano.py:309 | przyjmij_blad | `with self.baza.transakcja():` | B5000 | OKNO-Z: A:1430 | Z-BAZA |
| 188 | session_rano.py:312 | przyjmij_blad | `self.baza.wykonaj("UPDATE skany SET sesja_pieca_id = ? WHERE id = ?", (pid, skan_id))` | B5000 | jak 187 | Z-BAZA |
| 189 | session_rano.py:322 | _skan_rano | `sk = self.baza.wiersz("SELECT * FROM skany WHERE id = ?", (skan_id,)) if skan_id is not None else None` | B200 | SR:336, SR:354, SR:366, SR:402, SR:409, SR:418, SR:436 | P-BAZA |
| 190 | session_rano.py:335 | zastap_skan | `with self.baza.transakcja():` | B200 | OKNO-P: K:3656 <- K:3663 | P-BAZA |
| 191 | session_rano.py:343 | zastap_skan | `stary = self.baza.wiersz("SELECT * FROM skany WHERE id = ?", (poprzedni_id,))` | B200 | jak 190 | P-BAZA |
| 192 | session_rano.py:353 | cofnij_zastapienie | `with self.baza.transakcja():` | B200 | OKNO-P: K:3656 <- K:3678 | P-BAZA |
| 193 | session_rano.py:365 | podaj_numer_plytki | `with self.baza.transakcja():` | B200 (blok K:3703) | OKNO-P: K:3719 | P-BAZA |
| 194 | session_rano.py:380 | podaj_numer_plytki | `inne = self.baza.wiersze(f"SELECT * FROM skany WHERE sesja_pieca_id = ? AND numer_plytki = ? AND id != ? "` | B200 | jak 193 | P-BAZA |
| 195 | session_rano.py:395 | podaj_numer_plytki | `self.baza.zdarzenie("ui", TYP_NUMER_MIMO, {"decyzja_id": d, "skan_id": sk["id"], ...` | B200 | jak 193 | P-BAZA |
| 196 | session_rano.py:408 | cofnij_dopuszczenie | `with self.baza.transakcja():` | B200 | OKNO-P: K:3656 <- K:3684 | P-BAZA |
| 197 | session_rano.py:417 | pomin_skan | `with self.baza.transakcja():` | B200 | OKNO-P: K:3835 | P-BAZA |
| 198 | session_rano.py:427 | pomin_skan | `d = self.baza.wstaw("decyzje", skan_id=sk["id"], rodzaj=RODZAJ_POMIN_SKAN, operator=osoba, czas=teraz)` | B200 | jak 197 | P-BAZA |
| 199 | session_rano.py:428 | pomin_skan | `self.baza.zdarzenie("ui", TYP_POMINIETY, {"decyzja_id": d, "status": sk["status"], ...` | B200 | jak 197 | P-BAZA |
| 200 | session_rano.py:435 | cofnij_pominiecie | `with self.baza.transakcja():` | B200 | OKNO-P: K:3838 | P-BAZA |
| 201 | session_rano.py:440 | cofnij_pominiecie | `return self.baza.wstaw("decyzje", skan_id=sk["id"], rodzaj=SE.RODZAJ_COFNIECIE, wartosc=str(ob[-1]["id"]), operator=osoba,` | B200 | jak 200 | P-BAZA |
| 202 | session_rano.py:457 | _propozycje | `skany = self.baza.wiersze(f"SELECT * FROM skany WHERE sesja_pieca_id = ? AND status IN (...) ORDER BY id",` | Bwg: B200 (SR:338) / BST, B5000 (SR:890 `_oblicz`) | okno | P-BAZA / S-BAZA / RP-PLAN |
| 203 | session_rano.py:500 | _praca_rano | `p = self.baza.wiersz("SELECT p.*, s.status AS status_skanu, s.tryb AS tryb_skanu, s.sesja_pieca_id FROM prace p "` | B200 | SR:528, SR:547, SR:564 | P-BAZA |
| 204 | session_rano.py:520 | _decyzja_przypisania | `return _obowiazujaca(self.baza.wiersze("SELECT * FROM decyzje WHERE praca_id = ? AND rodzaj IN (?, ?, ?) ORDER BY id",` | B200 | SR:565, SR:572 | P-BAZA |
| 205 | session_rano.py:527 | wybierz_kandydata | `with self.baza.transakcja():` | B200 | OKNO-P: K:3752 | P-BAZA |
| 206 | session_rano.py:537 | wybierz_kandydata | `d = self.baza.wstaw("decyzje", praca_id=p["id"], skan_id=p["skan_id"], rodzaj=RODZAJ_WYBOR, wartosc=sha16, operator=osoba,` | B200 | jak 205 | P-BAZA |
| 207 | session_rano.py:546 | przypisz_recznie | `with self.baza.transakcja():` | B200 | OKNO-P: K:3757 | P-BAZA |
| 208 | session_rano.py:552 | przypisz_recznie | `if self.baza.wiersz("SELECT id FROM projekty WHERE id = ? AND usuniety = 0", (projekt_id,)) is None:` | B200 | jak 207 | P-BAZA |
| 209 | session_rano.py:554 | przypisz_recznie | `d = self.baza.wstaw("decyzje", praca_id=p["id"], skan_id=p["skan_id"], rodzaj=RODZAJ_PRZYPISANIE,` | B200 | jak 207 | P-BAZA |
| 210 | session_rano.py:563 | cofnij_przypisanie | `with self.baza.transakcja():` | B200 | OKNO-P: K:3761 | P-BAZA |
| 211 | session_rano.py:570 | cofnij_przypisanie | `d = self.baza.wstaw("decyzje", praca_id=p["id"], skan_id=p["skan_id"], rodzaj=SE.RODZAJ_COFNIECIE, wartosc=str(ob["id"]),` | B200 | jak 210 | P-BAZA |
| 212 | session_rano.py:601 | _zapisz_przypisanie | `self.baza.wykonaj("UPDATE prace SET projekt_id = ? WHERE id = ?", (projekt_id, praca_id))` | Bwg: B5000 (SR:303) / B200 (SR:539, SR:556, SR:573) / B200, B150 (SR:1102 <- `_zamknij`) | okno | Z-BAZA / P-BAZA / R-BAZA |
| 213 | session_rano.py:609 | _wiersze_in | `wynik += self.baza.wiersze(sql.format(_znaki(len(czesc))), tuple(czesc))` | Bwg (max B5000): wolane z SR:446, SR:461, SR:618, SR:623, SR:632, SR:650, SR:662, SR:672, SR:728, SR:730 | okno | wg wolajacego |
| 214 | session_rano.py:684 | _wlasny_stan | `return _wiersz_stanu(self.baza.wiersz("SELECT * FROM stan_punktow WHERE projekt_id = ?", (projekt_id,)))` | B200 / B150 | SR:1094, SR:1184, SR:1236, SR:1261, SR:1265 | P-BAZA / R-BAZA |
| 215 | session_rano.py:687 | _ustaw_punkt | `self.baza.wykonaj(` | B200 / B150 | SR:697, SR:1096, SR:1243 | P-BAZA / R-BAZA |
| 216 | session_rano.py:695 | _przywroc_punkt | `self.baza.wykonaj("DELETE FROM stan_punktow WHERE projekt_id = ?", (projekt_id,))` | B200 | SR:1187, SR:1267 | P-BAZA |
| 217 | session_rano.py:724 | _oblicz | `skany = self.baza.wiersze("SELECT * FROM skany WHERE sesja_pieca_id = ? ORDER BY id", (pid,))` | Bwg: BST (SR:960 <- K:1908, K:1972) / B5000 (SR:960 <- SR:1296 <- K:2590) / B200, B150 (SR:1086) | okno | S-BAZA / RP-PLAN / P-BAZA |
| 218 | session_rano.py:979 | zamknij_piec | `with self.baza.transakcja():` | B200 (K:3791) / B150 (K:2502 <- K:2450 <- K:2251) | okno | P-BAZA / R-BAZA |
| 219 | session_rano.py:995 | zamknij_piec_i_przenies | `with self.baza.transakcja():` | B200 | OKNO-P: K:3809 | P-BAZA |
| 220 | session_rano.py:1002 | zamknij_piec_i_przenies | `w_piecu = self.baza.wiersze("SELECT * FROM skany WHERE sesja_pieca_id = ? ORDER BY id", (piec["id"],))` | B200 | jak 219 | P-BAZA |
| 221 | session_rano.py:1020 | zamknij_piec_i_przenies | `self.baza.wykonaj(f"UPDATE skany SET sesja_pieca_id = NULL WHERE id IN ({_znaki(len(ids))})", tuple(ids))` | B200 | jak 219 | P-BAZA |
| 222 | session_rano.py:1023 | zamknij_piec_i_przenies | `self.baza.wykonaj(f"UPDATE skany SET sesja_pieca_id = ? WHERE id IN ({_znaki(len(ids))})", (nowy, *ids))` | B200 | jak 219 | P-BAZA |
| 223 | session_rano.py:1025 | zamknij_piec_i_przenies | `d = self.baza.wstaw("decyzje", rodzaj=RODZAJ_PRZENIES, operator=osoba, czas=teraz,` | B200 | jak 219 | P-BAZA |
| 224 | session_rano.py:1027 | zamknij_piec_i_przenies | `self.baza.zdarzenie("ui", TYP_PRZENIESIONE, {"z_pieca": piec["id"], "do_pieca": nowy, ...` | B200 | jak 219 | P-BAZA |
| 225 | session_rano.py:1037 | cofnij_przeniesienie | `with self.baza.transakcja():` | B200 | OKNO-P: K:3819 | P-BAZA |
| 226 | session_rano.py:1038 | cofnij_przeniesienie | `nowy = self.baza.wiersz("SELECT * FROM sesje_pieca WHERE id = ?", (sesja_pieca_id,))` | B200 | jak 225 | P-BAZA |
| 227 | session_rano.py:1041 | cofnij_przeniesienie | `wiersze = self.baza.wiersze("SELECT * FROM decyzje WHERE praca_id IS NULL AND skan_id IS NULL AND rodzaj IN (?, ?) ORDER BY id",` | B200 | jak 225 | P-BAZA |
| 228 | session_rano.py:1047 | cofnij_przeniesienie | `stary = self.baza.wiersz("SELECT * FROM sesje_pieca WHERE id = ?", (dane["z_pieca"],))` | B200 | jak 225 | P-BAZA |
| 229 | session_rano.py:1048 | cofnij_przeniesienie | `w_nowym = {w["id"] for w in self.baza.wiersze("SELECT id FROM skany WHERE sesja_pieca_id = ?", (nowy["id"],))}` | B200 | jak 225 | P-BAZA |
| 230 | session_rano.py:1052 | cofnij_przeniesienie | `pozniej = self.baza.wiersz("SELECT count(*) AS n FROM sesje_pieca WHERE zamknieto IS NOT NULL AND id > ?", (stary["id"],))["n"]` | B200 | jak 225 | P-BAZA |
| 231 | session_rano.py:1058 | cofnij_przeniesienie | `self.baza.wykonaj(f"UPDATE skany SET sesja_pieca_id = ? WHERE id IN ({_znaki(len(ids))})", (stary["id"], *ids))` | B200 | jak 225 | P-BAZA |
| 232 | session_rano.py:1059 | cofnij_przeniesienie | `self.baza.wykonaj("UPDATE sesje_pieca SET zamknieto = NULL, zamknal = NULL WHERE id = ?", (stary["id"],))` | B200 | jak 225 | P-BAZA |
| 233 | session_rano.py:1060 | cofnij_przeniesienie | `self.baza.wykonaj("UPDATE sesje_pieca SET zamknieto = ?, zamknal = ? WHERE id = ?", (teraz, osoba, nowy["id"]))` | B200 | jak 225 | P-BAZA |
| 234 | session_rano.py:1061 | cofnij_przeniesienie | `d = self.baza.wstaw("decyzje", rodzaj=SE.RODZAJ_COFNIECIE, wartosc=str(ob[-1]["id"]), operator=osoba, czas=teraz)` | B200 | jak 225 | P-BAZA |
| 235 | session_rano.py:1064 | cofnij_przeniesienie | `self.baza.zdarzenie("ui", TYP_PRZENIESIENIE_COFNIETE, {**wynik, "pusty_piec": nowy["id"], "skany": ids}, czas=teraz)` | B200 | jak 225 | P-BAZA |
| 236 | session_rano.py:1118 | _zamknij | `self.baza.wykonaj("UPDATE sesje_pieca SET zamknieto = ?, zamknal = ? WHERE id = ?", (teraz, osoba, piec["id"]))` | B200 / B150 | SR:980, SR:1021 | P-BAZA / R-BAZA |
| 237 | session_rano.py:1119 | _zamknij | `juz = {d.get("praca_id") for d in (json.loads(w["dane"]) for w in self.baza.wiersze(` | B200 / B150 | jak 236 | jak 236 |
| 238 | session_rano.py:1122 | _zamknij | `self.baza.zdarzenie("system", TYP_POPRAWKA, {**x, "sesja_pieca_id": piec["id"]}, skan_id=x["skan_id"], czas=teraz)` | B200 / B150 | jak 236 | jak 236 |
| 239 | session_rano.py:1130 | _zamknij | `self.baza.zdarzenie("ui", TYP_ZAMKNIETY, zapis, czas=teraz)` | B200 / B150 | jak 236 | jak 236 |
| 240 | session_rano.py:1134 | _zapis_zamkniecia | `for w in reversed(self.baza.wiersze("SELECT dane FROM zdarzenia WHERE typ = ? ORDER BY id", (TYP_ZAMKNIETY,))):` | Bwg: jak 241 (SR:1146) / B200 (SR:1181) | okno | jak 241 |
| 241 | session_rano.py:1143 | wynik_pieca | `piec = self.baza.wiersz("SELECT * FROM sesje_pieca WHERE id = ?", (sesja_pieca_id,))` | Bwg: BST (K:1908; SR:962) / B5000 (K:2822 <- K:2093 <- A:595, OKNO-S; K:2863, K:2874, K:2914 OKNO-Z; SR:962 <- `plan_plytek`) / B200 (K:2874 <- K:3048, K:3062; SR:1131) / B150 (SR:1131 <- zamkniecie z ramki) | okno | S-BAZA / X-KROK / P-BAZA / R-BAZA |
| 242 | session_rano.py:1157 | otworz_piec_ponownie | `with self.baza.transakcja():` | B200 | OKNO-P: K:3828 | P-BAZA |
| 243 | session_rano.py:1158 | otworz_piec_ponownie | `piec = self.baza.wiersz("SELECT * FROM sesje_pieca WHERE id = ?", (sesja_pieca_id,))` | B200 | jak 242 | P-BAZA |
| 244 | session_rano.py:1166 | otworz_piec_ponownie | `ostatni = self.baza.wiersz("SELECT max(id) AS id FROM sesje_pieca")["id"]` | B200 | jak 242 | P-BAZA |
| 245 | session_rano.py:1171 | otworz_piec_ponownie | `self.baza.wykonaj("UPDATE sesje_pieca SET zamknieto = NULL, zamknal = NULL WHERE id = ?", (piec["id"],))` | B200 | jak 242 | P-BAZA |
| 246 | session_rano.py:1172 | otworz_piec_ponownie | `d = self.baza.wstaw("decyzje", rodzaj=RODZAJ_OTWORZ_PIEC, wartosc=str(piec["id"]), operator=osoba, czas=teraz)` | B200 | jak 242 | P-BAZA |
| 247 | session_rano.py:1175 | otworz_piec_ponownie | `self.baza.zdarzenie("ui", TYP_OTWARTY_PONOWNIE, wynik, czas=teraz)` | B200 | jak 242 | P-BAZA |
| 248 | session_rano.py:1199 | braki | `kandydaci = self.baza.wiersze(` | BST (max B5000) | okno: K:1898 <- K:1966 | S-BAZA |
| 249 | session_rano.py:1223 | zamknij_brak_recznie | `with self.baza.transakcja():` | B200 | OKNO-P: K:3845 | P-BAZA |
| 250 | session_rano.py:1240 | zamknij_brak_recznie | `d = self.baza.wstaw("decyzje", rodzaj=RODZAJ_ZAMKNIECIE_RECZNE, operator=osoba, czas=teraz,` | B200 | jak 249 | P-BAZA |
| 251 | session_rano.py:1245 | zamknij_brak_recznie | `self.baza.zdarzenie("ui", TYP_ZAMKNIETY_RECZNIE, {"decyzja_id": d, "projekt_id": projekt_id, ...` | B200 | jak 249 | P-BAZA |
| 252 | session_rano.py:1254 | cofnij_zamkniecie_reczne | `with self.baza.transakcja():` | B200 | OKNO-P: K:3849 | P-BAZA |
| 253 | session_rano.py:1255 | cofnij_zamkniecie_reczne | `wiersze = self.baza.wiersze("SELECT * FROM decyzje WHERE praca_id IS NULL AND skan_id IS NULL AND rodzaj IN (?, ?) ORDER BY id",` | B200 | jak 252 | P-BAZA |
| 254 | session_rano.py:1269 | cofnij_zamkniecie_reczne | `d = self.baza.wstaw("decyzje", rodzaj=SE.RODZAJ_COFNIECIE, wartosc=str(ob[-1]["id"]), operator=osoba, czas=teraz)` | B200 | jak 252 | P-BAZA |
| 255 | session_rano.py:1270 | cofnij_zamkniecie_reczne | `self.baza.zdarzenie("ui", TYP_ZAMKNIETY_RECZNIE + "_cofniete", {"decyzja_id": d, "projekt_id": projekt_id}, czas=teraz)` | B200 | jak 252 | P-BAZA |

### A.7 stanowisko/ui/*.py (bezposrednich wywolan SQLite / COM / sieci brak; patrz Uwagi 3)

| nr | plik:linia | funkcja | operacja (cytat) | limit czasu | watek wywolania + dowod | po limicie / po wyjatku |
|---|---|---|---|---|---|---|
| 256 | ui/mapa.py:65 | geometria_ukladu | `_GEOMETRIE[klucz] = U.wczytaj(nazwa, katalog)` (odczyt uklad.json w `stanowisko/uklad.py` - poza zakresem) | BRAK (wynik zapamietany w `_GEOMETRIE`) | okno: ui/okno.py:682, ui/okno.py:847, ui/ekran_rano.py:758, ui/ekran_rano.py:956 (metody widzetow) | log.warning, mapa w kratke, ponowienie po PONOW_UKLAD_S (mapa.py:51-53, 66-69) |
| 257 | ui/obraz.py:132 | WczytywaczObrazow._dane_pliku | `self._pliki[klucz] = K.wczytaj_podglad(plik)` (silnik.wczytaj_podglad, K:1164) | BRAK | watek roboczy QThreadPool (obraz.py:108-109; start obraz.py:124 <- okno.py:926; run obraz.py:86) | log.warning, obraz None -> napis (obraz.py:90-91, okno.py:931-932) |
| 258 | ui/obraz.py:147 | zakoncz | `self._pula.waitForDone(3000)` | 3000 ms - stala | okno: ui/okno.py:638 (closeEvent) | zamykanie dalej; zadanie konczy sie bez sygnalu (obraz.py:92-93) |

### A.8 ramka/*.py (proces ramki; RPi = `--sprzet rpi`)

| nr | plik:linia | funkcja | operacja (cytat) | limit czasu | watek wywolania + dowod | po limicie / po wyjatku |
|---|---|---|---|---|---|---|
| 259 | ramka/serwer.py:143 | _czytaj_tresc | `b = self.rfile.read(min(65536, reszta))` (petla `while reszta > 0` serwer.py:142) | 15 s na odczyt (`timeout = 15`, serwer.py:90) | proces ramki: watek obslugi zadania (ThreadingHTTPServer, serwer.py:288-289) | wyjatek -> serwer.py:215-217 (500; polecenie - gaszenie serwer.py:218-223) |
| 260 | ramka/serwer.py:149 | _czytaj_tresc | `dane = self.rfile.read(n) if n else b""` | 15 s | jak 259 | jak 259 |
| 261 | ramka/serwer.py:164 | _wyrzuc_tresc | `b = self.rfile.read1(min(65536, reszta))` (petla serwer.py:163) | 1.0 s (CZAS_WYRZUCANIA_S serwer.py:36, settimeout serwer.py:162) | jak 259 | timeout pomijany (serwer.py:168-169) |
| 262 | ramka/serwer.py:283 | _odpowiedz | `self.wfile.write(cialo)` (takze send_response / end_headers serwer.py:275-281) | 15 s | jak 259 | OSError -> log.info (serwer.py:284-285) |
| 263 | ramka/serwer.py:302 | get_request | `polaczenie, adres = super().get_request()` (accept) | BRAK (accept po gotowosci w serve_forever, poll_interval 0.1 s - program.py:301) | proces ramki: watek `ramka-serwer` (program.py:301) | obsluga w socketserver (poza zakresem) |
| 264 | ramka/serwer.py:303 | get_request | `with self._blok_czasow:` | BRAK (Lock) | `ramka-serwer` | Z-W (pod zamkiem tylko zegar) |
| 265 | ramka/serwer.py:308 | czas_odbioru | `with self._blok_czasow:` | BRAK | watek obslugi zadania (setup serwer.py:101) | Z-W |
| 266 | ramka/serwer.py:313 | shutdown_request | `with self._blok_czasow:` | BRAK | `ramka-serwer` / watek obslugi | Z-W |
| 267 | ramka/program.py:57 | wczytaj_konfiguracje | `dane = json.loads(Path(sciezka).read_text(encoding="utf-8"))` | BRAK | proces ramki: watek glowny przy starcie (program.py:344 <- program.py:364); test_led.py:88 | program: brak obslugi w main (program.py:364) - proces konczy sie wyjatkiem; test_led: komunikat, kod 1 (test_led.py:89-92) |
| 268 | ramka/program.py:129 | krok | `with self.warunek:` | BRAK | watek `ramka-petla` (program.py:303) | Z-W |
| 269 | ramka/program.py:140 | _krok | `with self.warunek:` | BRAK | `ramka-petla` | Z-W |
| 270 | ramka/program.py:166 | _awaria | `with self.warunek:` | BRAK | `ramka-petla` | Z-W |
| 271 | ramka/program.py:191 | _petla | `self._stop.wait(0.5)` | 0.5 s - stala | `ramka-petla` | kolejny obieg |
| 272 | ramka/program.py:194 | _petla | `self._stop.wait(0.5)` | 0.5 s - stala | `ramka-petla` | kolejny obieg |
| 273 | ramka/program.py:195 | _petla | `self._budzik.wait(self.konf.okres_s)` | okres_s = 0.01 s (konfiguracja, program.py:39) | `ramka-petla` | kolejny obieg |
| 274 | ramka/program.py:205 | stan | `with self.warunek:` | BRAK | watek obslugi zadania (serwer.py:246) | Z-W |
| 275 | ramka/program.py:215 | zdarzenia | `with self.warunek:` | BRAK | watek obslugi zadania (serwer.py:254) | Z-W |
| 276 | ramka/program.py:234 | zdarzenia | `self.warunek.wait(pozostalo)` (petla `while` program.py:230) | min(czekaj z zadania, CZEKAJ_MAX_S = 25.0 s (protokol.py:68), limit_odpytywania() = max(0.5, min(limit_lacznosci_s 30 s, plan_wazny_s) / 3) (logika.py:132-137, program.py:43)) - program.py:227 | watek obslugi zadania | odpowiedz bez nowych zdarzen (program.py:235-240) |
| 277 | ramka/program.py:243 | plan | `with self.warunek:` | BRAK | watek obslugi zadania (serwer.py:256) | Z-W |
| 278 | ramka/program.py:252 | odrzucenie | `with self.warunek:` | BRAK | watek obslugi zadania (serwer.py:221) | Z-W |
| 279 | ramka/program.py:259 | usun_plan | `with self.warunek:` | BRAK | watek obslugi zadania (serwer.py:261) | Z-W |
| 280 | ramka/program.py:266 | tryb | `with self.warunek:` | BRAK | watek obslugi zadania (serwer.py:263) | Z-W |
| 281 | ramka/program.py:314 | zatrzymaj | `with self.warunek:` | BRAK | proces ramki: watek glowny (program.py:387) | Z-W |
| 282 | ramka/program.py:318 | zatrzymaj | `self.serwer.shutdown()` | BRAK (czeka na koniec serve_forever; poll 0.1 s) | watek glowny | - |
| 283 | ramka/program.py:322 | zatrzymaj | `w.join(5)` | 5 s - stala | watek glowny | zamykanie dalej (watki daemon) |
| 284 | ramka/program.py:384 | main | `while not koniec.wait(0.5):` | 0.5 s na obieg; calosc do SIGINT/SIGTERM (program.py:376-381) | watek glowny | - |
| 285 | ramka/sprzet_rpi.py:134 | _znajdz_klawiature | `for sciezka in evdev.list_devices():` (lista /dev/input) | BRAK | proces ramki RPi: watek `ramka-klawiatura` (sprzet_rpi.py:118) | - |
| 286 | ramka/sprzet_rpi.py:136 | _znajdz_klawiature | `d = evdev.InputDevice(sciezka)` (otwarcie urzadzenia) | BRAK | `ramka-klawiatura` | OSError -> nastepne urzadzenie (sprzet_rpi.py:141-142) |
| 287 | ramka/sprzet_rpi.py:162 | _czytaj_klawiature | `self._stop.wait(2.0)` | 2.0 s - stala | `ramka-klawiatura` | kolejna proba |
| 288 | ramka/sprzet_rpi.py:167 | _czytaj_klawiature | `r, _, _ = select.select([d.fd], [], [], 0.5)` | 0.5 s - stala | `ramka-klawiatura` | kolejny obieg |
| 289 | ramka/sprzet_rpi.py:170 | _czytaj_klawiature | `for ev in d.read():` | BRAK (po select - dane gotowe) | `ramka-klawiatura` | OSError -> log.warning, 2 s (sprzet_rpi.py:175-177) |
| 290 | ramka/sprzet_rpi.py:177 | _czytaj_klawiature | `self._stop.wait(2.0)` | 2.0 s - stala | `ramka-klawiatura` | kolejna proba |
| 291 | ramka/sprzet_rpi.py:212 | temperatura | `with open(PLIK_TEMPERATURY, encoding="ascii") as f:` | BRAK | `ramka-petla` (program.py:138), co ok. 500 obiegow (sprzet_rpi.py:210) | temperatura None (sprzet_rpi.py:214-215) |
| 292 | ramka/sprzet_rpi.py:221 | zamknij | `self._watek.join(2)` | 2 s - stala | proces ramki: watek glowny (program.py:324) | zamykanie dalej |
| 293 | ramka/kalibracja.py:95 | domyslna | `uklad = json.loads(plik.read_text(encoding="utf-8"))` (petla po glob kalibracja.py:94) | BRAK | laptop OKNO-S (RP:76 <- I:1204; KAL:184 <- RP:88 <- I:1225; KAL:205 <- RP:83 <- I:1222); CLI kalibracja.py:275 | wyjatek do wolajacego |
| 294 | ramka/kalibracja.py:165 | wczytaj | `dane = json.loads(Path(sciezka).read_text(encoding="utf-8"))` | BRAK | laptop OKNO-S (RP:70 <- I:1209; KAL:204 <- I:1222); CLI test_led.py:98, kalibracja.py:281 | BladKalibracji (kalibracja.py:166-167) |
| 295 | ramka/kalibracja.py:174 | zapisz | `Path(sciezka).parent.mkdir(parents=True, exist_ok=True)` | BRAK | laptop OKNO-S (KAL:211 <- I:1222); CLI kalibracja.py:276 | OSError do wolajacego |
| 296 | ramka/kalibracja.py:175 | zapisz | `with open(sciezka, "w", encoding="ascii", newline="\n") as f:` | BRAK | jak 295 | jak 295 |
| 297 | ramka/kalibracja.py:213 | uzupelnij_plik | `kopia.write_bytes(sciezka.read_bytes())` | BRAK | laptop OKNO-S (RP:83 <- I:1222) | OSError -> usuniecie nowej kopii, wyjatek dalej (kalibracja.py:216-222) -> I:1223 |
| 298 | ramka/kalibracja.py:215 | uzupelnij_plik | `os.replace(tymczasowy, sciezka)` | BRAK | jak 297 | jak 297 |
| 299 | ramka/kalibracja.py:219 | uzupelnij_plik | `kopia.unlink()` | BRAK | jak 297 | OSError pomijany (kalibracja.py:220-221) |
| 300 | ramka/kalibracja.py:225 | uzupelnij_plik | `tymczasowy.unlink()` | BRAK | jak 297 | OSError pomijany (kalibracja.py:226-227) |
| 301 | ramka/sprzet_atrapa.py:40 | poloz_plytke | `with self._warunek:` | BRAK (Condition) | atrapa (nie RPi): watek obslugi `/atrapa/plytka` (program.py:283) albo test | Z-W |
| 302 | ramka/sprzet_atrapa.py:50 | nacisnij | `with self._warunek:` | BRAK | atrapa: `/atrapa/klawisz` (program.py:290) | Z-W |
| 303 | ramka/sprzet_atrapa.py:63 | czekaj | `with self._warunek:` | BRAK | NIEUSTALONE (tylko testy; brak wywolania w ramka/*.py) | Z-W |
| 304 | ramka/sprzet_atrapa.py:70 | czekaj | `self._warunek.wait(min(pozostalo, 0.05))` (petla `while True` sprzet_atrapa.py:64) | timeout 2.0 s domyslnie (sprzet_atrapa.py:60) | NIEUSTALONE (testy) | False (sprzet_atrapa.py:68-69) |
| 305 | ramka/sprzet_atrapa.py:78 | pobierz_klawisze | `with self._warunek:` | BRAK | `ramka-petla` (program.py:137) | Z-W |
| 306 | ramka/sprzet_atrapa.py:86 | _zapisz | `with self._warunek:` | BRAK | `ramka-petla` (pokaz program.py:158, 178; wygas program.py:183) | Z-W |
| 307 | ramka/test_led.py:53 | uruchom_test | `sen(czas_s)` (time.sleep) | `--czas`, domyslnie 0.7 s na gniazdo (test_led.py:77, 121) | proces CLI test_led (RPi), watek glowny | - |
| 308 | ramka/test_led.py:88 | main | `konf = program.wczytaj_konfiguracje(a.konfiguracja) if a.konfiguracja else program.Konfiguracja()` | BRAK | CLI, watek glowny | komunikat stderr, kod 1 (test_led.py:89-92) |
| 309 | ramka/test_led.py:98 | main | `kal = kalibracja.wczytaj(a.kalibracja)` | BRAK | CLI, watek glowny | komunikat, kod 1 (test_led.py:100-102) |
| 310 | ramka/test_led.py:118 | main | `time.sleep(10.0 if na_ramce else 0.0)` | 10 s - stala | CLI, watek glowny | - |

## Tabela B - except szerokie i ciche (53 wiersze)

Kryterium: kazde `except Exception` / `except BaseException` / gole `except:` (golych `except:` i `except BaseException` w zakresie
brak) oraz `except` konczace sie `pass` / `continue` / `return` bez logu i bez komunikatu dla technika. Kolumna "STARA wartosc":
czy po zlapaniu wynik / stan diody / komorka Excela zostaje ze STARA wartoscia.

| nr | plik:linia | funkcja | co lapie | co robi po zlapaniu | STARA wartosc |
|---|---|---|---|---|---|
| 1 | indicate.py:310 | _przerwij_polaczenia | OSError (sock.shutdown) | pass, bez logu | NIE |
| 2 | indicate.py:314 | _przerwij_polaczenia | OSError (sock.close) | pass, bez logu | NIE |
| 3 | indicate.py:561 | _zapisz | Exception (dziennik ruchu) | log.exception, dalej | NIE (w programie dziennik None - A:414) |
| 4 | indicate.py:600 | _zadanie | Exception | wpis "blad" w dzienniku ruchu, raise | NIE (wyjatek idzie dalej) |
| 5 | indicate.py:664 | _wywolaj | Exception (na_zdarzenie) | log.exception, dalej | NIE (w programie na_zdarzenie None - A:414) |
| 6 | indicate.py:939 | _petla_polecen | Exception | log.exception (gdy nie stop), czekanie przerwa_max (I:942); polecenie zostaje w kolejce | NIEJASNE (polecenie ponawiane; gdy wyjatek po wyslaniu - I:1105 - stan laptopa moze nie odpowiadac ramce) |
| 7 | indicate.py:978 | _wykonaj_gaszace | BladOdpowiedzi, OSError, HTTPException | bledy_sieci+1, pauza, return - bez logu, bez kodu bledu (polaczona bez zmian) | TAK (polecenie gaszace czeka w kolejce; do udanego ponowienia albo konca waznosci planu na ramce zostaje poprzedni obraz) |
| 8 | indicate.py:1094 | _wykonaj_plan | BladOdpowiedzi, OSError, HTTPException | bledy_sieci+1, zapamietane ponowienie, pauza, return - bez logu | TAK (nowa wersja planu nie doszla; na ramce zostaje poprzednia wersja planu albo obraz sprzed polecenia) |
| 9 | indicate.py:1117 | _stan_po_odmowie | BladOdpowiedzi, OSError, HTTPException | return, bez logu | NIE (ramka po 409 jest zgaszona - I:1156-1159) |
| 10 | indicate.py:1206 | wczytaj_kalibracje | Exception | return (None, [ostrzezenie]) - komunikat, bez logu | NIE (gniazda nie wskazywane) |
| 11 | indicate.py:1226 | _uzupelnij_kalibracje | Exception | log.exception, return (kal, []) | NIE (kalibracja z pliku; brakujace uklady ciemne) |
| 12 | indicate.py:1234 | _uzupelnij_kalibracje | Exception | log.exception, return (kal, []) | NIE |
| 13 | indicate.py:1251 | identyfikator_laptopa | OSError, UnicodeDecodeError | pass, bez logu | NIE (nowy identyfikator) |
| 14 | indicate.py:1265 | _zapisany_identyfikator | OSError, UnicodeDecodeError | return False, bez logu (ostrzezenie dodaje wolajacy I:1293-1297) | NIE |
| 15 | ramka_protokol.py:94 | _blok | KeyError, TypeError, ValueError | return None, bez logu (plytka do `pominiete["brak_kalibracji"]`, RP:156-158) | NIE (plytka ciemna) |
| 16 | excel.py:206 | data_z_komorki | ValueError | continue (nastepny format), bez logu | NIE |
| 17 | excel.py:625 | zrodlo | Exception | raise BladExcela("Excel niedostepny") | NIE |
| 18 | excel.py:637 | rozlacz | Exception (zwolnij) | pass, bez logu | NIE (`_zrodlo` i tak zerowane E:639) |
| 19 | excel.py:652 | odswiez | Exception | rozlaczenie, raise BladExcela | NIE |
| 20 | excel.py:671 | _wypelnienie | Exception | rozlaczenie, raise BladExcela | NIE |
| 21 | excel.py:797 | _loguj | Exception (wpis excel_zapisy) | raise BladExcela z opisem, gdzie jest wpis | NIE |
| 22 | excel.py:880 | zatwierdz | Exception (zapis koloru COM) | odczyt koloru; ponowienie albo odmowa "sprawdz recznie" | NIEJASNE (kod zaklada, ze zapis mogl dojsc - E:881-882) |
| 23 | excel.py:907 | zatwierdz | Exception (odczyt kontrolny) | rozlaczenie, odmowa "sprawdz recznie" | NIEJASNE |
| 24 | excel_com.py:55 | polacz | Exception (GetActiveObject) | raise BladCom | NIE |
| 25 | excel_com.py:82 | _arkusz | Exception | raise BladCom | NIE |
| 26 | excel_com.py:145 | ustaw_wypelnienie | Exception | raise BladCom | NIEJASNE (komorka mogla zostac zmieniona - obsluga E:880) |
| 27 | session.py:538 | _zapisz_wynik | ValueError (relative_to) | return sciezka bezwzgledna, bez logu | NIE |
| 28 | session.py:658 | _przypisania_skanow | ValueError (json) | continue, bez logu | NIE (dane tego zdarzenia pominiete) |
| 29 | session.py:677 | wpis_puli_pracy | ValueError, AttributeError | continue, bez logu | NIE |
| 30 | ui/mapa.py:66 | geometria_ukladu | Exception | LOG.warning, geometria None (mapa w kratke) | NIE |
| 31 | ui/obraz.py:63 | rysuj_odchylki | KeyError, TypeError, ValueError | continue, bez logu (ubytek nienarysowany) | NIE |
| 32 | ui/obraz.py:90 | _Zadanie.run | Exception | LOG.warning, obraz None -> napis "brak" | NIE |
| 33 | ui/obraz.py:96 | _Zadanie.run | RuntimeError (emit po zamknieciu okna) | pass | NIE |
| 34 | ui/okno.py:636 | closeEvent | RuntimeError, TypeError (disconnect) | pass | NIE |
| 35 | ramka/serwer.py:168 | _wyrzuc_tresc | OSError, socket.timeout | pass | NIE (401 juz wyslane) |
| 36 | ramka/serwer.py:215 | _obsluz | Exception | log.exception, odpowiedz 500, dla polecen gaszenie (serwer.py:218-223) | NIE |
| 37 | ramka/serwer.py:222 | _obsluz | Exception (program.odrzucenie) | log.exception | NIEJASNE (gaszenie po odrzuceniu moglo nie dojsc) |
| 38 | ramka/program.py:121 | krok | Exception | log.exception tylko gdy logika nie jest w awarii (program.py:122-123), `_awaria()` | NIE (matryca bez gniazd) |
| 39 | ramka/program.py:170 | _awaria | Exception (logika) | log.exception, klatka pusta | NIE |
| 40 | ramka/program.py:180 | _awaria | Exception (sprzet.pokaz) | log.exception, wygas() | NIE |
| 41 | ramka/program.py:184 | _awaria | Exception (sprzet.wygas) | log.exception | NIEJASNE (matryca nie przyjela ani klatki, ani wygaszenia; kolejna proba w nastepnym obiegu) |
| 42 | ramka/program.py:192 | _petla | Exception | log.exception, czekanie 0.5 s | NIEJASNE (ostatnia ochrona; krok() sam lapie Exception) |
| 43 | ramka/program.py:325 | zatrzymaj | Exception (sprzet.zamknij) | log.exception | NIE |
| 44 | ramka/sprzet_rpi.py:113 | SprzetRpi.__init__ | Exception | raise BladSprzetu | NIE |
| 45 | ramka/sprzet_rpi.py:141 | _znajdz_klawiature | OSError | continue, bez logu | NIE |
| 46 | ramka/sprzet_rpi.py:155 | _petla_klawiatury | Exception | log.exception, watek klawiatury konczy sie | NIE (dotyczy klawiatury) |
| 47 | ramka/sprzet_rpi.py:181 | _czytaj_klawiature | OSError (d.close) | pass | NIE |
| 48 | ramka/sprzet_rpi.py:189 | pobierz_klawisze | queue.Empty | return wynik (zwykle zakonczenie petli) | NIE |
| 49 | ramka/sprzet_rpi.py:224 | zamknij | Exception (matryca.Clear) | pass, bez logu | NIEJASNE (przy zamykaniu matryca mogla nie zostac wyczyszczona) |
| 50 | ramka/sprzet_rpi.py:229 | zamknij | Exception (czujnik.close) | pass, bez logu | NIE |
| 51 | ramka/kalibracja.py:220 | uzupelnij_plik | OSError (kopia.unlink) | pass | NIE |
| 52 | ramka/kalibracja.py:226 | uzupelnij_plik | OSError (tymczasowy.unlink) | pass | NIE |
| 53 | ramka/logika.py:421 | _znajdz_kuwete | ValueError | return None, bez logu | NIE |

Poza kryterium (ciche, ale z przypisaniem albo z komunikatem - do wiadomosci): indicate.py:431 (`pom = {}`), indicate.py:637 i 639
(`continue`; log I:673 / komunikat ustawiony przed rzuceniem I:669, I:687), indicate.py:642 i 649 (stan bledu bez logu, komunikat przez
`stan()`), indicate.py:989 i 1131 (`zla_odpowiedz` bez logu, z kodem bledu), excel.py:788 (`blad_csv = e`, potem BladExcela E:800-802),
session.py:534 (`nr += 1`), session.py:851 i session_rano.py:164, 373 (wartosc zastepcza, potem BladSesji), sprzet_rpi.py:214
(`self._temp = None`).

## Tabela C - zamki, zdarzenia, kolejki, watki, zegary w zakresie (28 wierszy)

| nr | plik:linia | obiekt | kto bierze / uzywa | dwa zamki naraz? |
|---|---|---|---|---|
| 1 | indicate.py:169 | `threading.Condition(threading.RLock())` `_warunek` (jeden na klienta W / P) | watek okna (I:249, 321, 335, 359, 367, 377, 388, 412, 439, 454, 486 - wolajacy w A.1); `indicate-<rola>-odpytywanie` (I:579, 585, 605, 623, 643, 650, 668, 683, 745, 759); `indicate-<rola>-polecenia` (I:579, 585, 605, 668, 925, 979, 983, 1057, 1095, 1102, 1119); `-zamykanie` (I:296, 579, 605); `zatrzymaj_klienta` (I:267, 305) | NIE - jeden zamek; I/O sieci poza nim (I:584-599); wywolania zwrotne poza nim (I:560 z I:577/601/608, I:663 z I:635, I:1091); `czekaj()` wola `warunek(self.stan())` pod tym samym RLock (I:369, reentrant; tylko testy) |
| 2 | indicate.py:170, 252 | `threading.Event` `_stop` (nowy przy kazdym `uruchom`) | set I:269; wait I:640, I:655, I:942 | - |
| 3 | indicate.py:172 | `threading.Event` `_wznow` | set I:272, I:330; wait I:626; clear I:627, I:671 | - |
| 4 | indicate.py:173 | `threading.Event` `_szybko` | set I:965, I:1123, I:1162; is_set/clear I:749-750 | - |
| 5 | indicate.py:257 | `threading.Thread` x2: `indicate-<rola>-odpytywanie`, `indicate-<rola>-polecenia`, daemon | start I:259 (<- K:2074); join I:285 | - |
| 6 | indicate.py:279 | `threading.Thread` `indicate-<rola>-zamykanie`, daemon | start I:281; join I:282 (<= 0.7 s) | - |
| 7 | indicate.py:1321 | `threading.Thread` (bez nazwy) `zatrzymaj_klienta`, daemon, po jednym na klienta | start I:1323; join w watku okna I:1326 (<= 1.1 s) | - |
| 8 | ramka/serwer.py:296 | `threading.Lock` `_blok_czasow` | `ramka-serwer` (get_request serwer.py:303, shutdown_request serwer.py:313), watki obslugi (czas_odbioru serwer.py:308 z setup serwer.py:101) | NIE - pod zamkiem tylko `self.program.zegar()` (time.perf_counter, program.py:85) |
| 9 | ramka/serwer.py:288-289 | `ThreadingHTTPServer`, `daemon_threads = True` - watek na kazde zadanie HTTP | watki obslugi wola program.stan / zdarzenia / plan / usun_plan / tryb / odrzucenie (serwer.py:221, 246-263) | - |
| 10 | ramka/program.py:99 | `threading.Condition(threading.RLock())` `warunek` | `ramka-petla` (program.py:129, 140, 166), watki obslugi (program.py:205, 215, 243, 252, 259, 266), watek glowny (program.py:314) | NIE - pod zamkiem tylko logika (bez zamkow); sprzet poza zamkiem (program.py:136-138, 158, 178); zamek atrapy (sprzet_atrapa.py:78) brany poza `warunek` (program.py:137) |
| 11 | ramka/program.py:103 | `threading.Event` `_stop` | set program.py:312; wait program.py:191, 194 | - |
| 12 | ramka/program.py:104 | `threading.Event` `_budzik` | set program.py:200, 284, 291, 313; wait program.py:195 | - |
| 13 | ramka/program.py:301 | `threading.Thread` `ramka-serwer` (serve_forever, poll 0.1 s), daemon | join program.py:322 (5 s) | - |
| 14 | ramka/program.py:303 | `threading.Thread` `ramka-petla`, daemon | join program.py:322 (5 s) | - |
| 15 | ramka/program.py:374 | `threading.Event` `koniec` | set przez sygnal (program.py:376-381); wait program.py:384 | - |
| 16 | ramka/sprzet_rpi.py:85 | `queue.Queue` `_kolejka` (bez limitu) | put `ramka-klawiatura` (sprzet_rpi.py:174); get_nowait `ramka-petla` (sprzet_rpi.py:188) | - |
| 17 | ramka/sprzet_rpi.py:86 | `threading.Event` `_stop` | set sprzet_rpi.py:219; wait sprzet_rpi.py:162, 177 | - |
| 18 | ramka/sprzet_rpi.py:118 | `threading.Thread` `ramka-klawiatura`, daemon (rola P albo z_klawiatura) | join sprzet_rpi.py:221 (2 s) | - |
| 19 | ramka/sprzet_atrapa.py:24 | `threading.Condition()` `_warunek` (atrapa) | watki obslugi `/atrapa/*` (sprzet_atrapa.py:40, 50), `ramka-petla` (sprzet_atrapa.py:78, 86), testy (sprzet_atrapa.py:63) | NIE |
| 20 | ui/obraz.py:108-109 | `QThreadPool(self)`, `setMaxThreadCount(1)` | start obraz.py:124 (watek okna); waitForDone obraz.py:147 (3 s) | - |
| 21 | ui/czesci.py:494 | `QTimer` `_blysk` (singleShot) | watek okna (start czesci.py:526) | - |
| 22 | ui/czesci.py:555 | `QTimer.singleShot(... + 50, self, self._sprawdz_liczenie)` | watek okna | - |
| 23 | ui/ekran_rano.py:512 | `QTimer` `_ochrona` (singleShot) | watek okna (start ekran_rano.py:750) | - |
| 24 | ui/okno.py:119 | `QTimer` `_ochrona` (singleShot) | watek okna (start okno.py:338, 717; stop okno.py:631) | - |
| 25 | ui/okno.py:181 | `QTimer.singleShot(0, ...)` | watek okna | - |
| 26 | ui/okno.py:182 | `QTimer.singleShot(0, ...)` | watek okna | - |
| 27 | ui/okno.py:183 | `QTimer.singleShot(0, ...)` | watek okna | - |
| 28 | ui/okno.py:446 | `QTimer.singleShot(0, ...)` | watek okna | - |

Brak zamkow, watkow i zegarow w: `excel.py`, `excel_com.py`, `session.py`, `session_rano.py`, `statusy.py`, `ramka_protokol.py`,
`ramka/logika.py`, `ramka/kalibracja.py`, `ramka/protokol.py`, `ramka/obraz.py` (Grep). Kontekst poza zakresem (nie wiersze tabeli):
`QTimer` K:1184 (zegar okna 30 ms), `threading.Lock` A:331, `queue.Queue` A:481, watki A:701, A:761, A:808.

## Tabela D - sygnaly Qt i wywolania zwrotne miedzy watkiem roboczym a oknem (20 wierszy)

| nr | plik:linia | gdzie | wywolanie | watek nadawcy -> odbiorcy | dotyka widzetow z watku roboczego bez sygnalu? |
|---|---|---|---|---|---|
| 1 | ui/obraz.py:104 | WczytywaczObrazow | `gotowy = Signal(object, object)` | definicja; obiekt tworzony w watku okna (ui/okno.py:123) | - |
| 2 | ui/obraz.py:95 | _Zadanie.run | `self.wczytywacz.gotowy.emit(self.klucz, obraz)` | watek QThreadPool (obraz.py:124) -> sloty obiektow watku okna (wiersze 3, 4) | NIE - run() czyta tylko `wczytywacz.koniec` (obraz.py:92) i wola `_dane_pliku` (obraz.py:86; `_pliki` uzywane tylko w tym watku, obraz.py:110) |
| 3 | ui/obraz.py:114 | WczytywaczObrazow.__init__ | `self.gotowy.connect(self._zapamietaj)` | slot obraz.py:137-142 w watku okna | NIE |
| 4 | ui/okno.py:124 | OknoWieczor.__init__ | `self.wczytywacz.gotowy.connect(self._obraz_gotowy)` | slot okno.py:928-934 (ustawia widok) w watku okna | NIE |
| 5 | ui/okno.py:129 | OknoWieczor.__init__ | `lacznik.stan_zmieniony.connect(self._na_stan)` | emit K:1194 w `_odbierz` K:1192, wolane synchronicznie z `_powiadom` K:1315-1323 w watku okna (K:1186-1190) | NIE (okno -> okno) |
| 6 | ui/okno.py:130 | OknoWieczor.__init__ | `lacznik.postep.connect(self._na_postep)` | emit K:1196, jak 5 | NIE |
| 7 | ui/okno.py:131 | OknoWieczor.__init__ | `lacznik.zamkniety.connect(self._na_zamkniety)` | emit K:1202, jak 5 | NIE |
| 8 | ui/okno.py:635 | closeEvent | `sygnal.disconnect(odbiorca)` (petla okno.py:632-635) | rozlaczenie 5-7 | - |
| 9 | ui/okno.py:181 | OknoWieczor.__init__ | `self.lista_plytek.wybrano.connect(lambda skan_id: QTimer.singleShot(0, lambda: self._pokaz_plytke(skan_id)))` | okno -> okno (odlozenie do petli zdarzen) | NIE |
| 10 | ui/okno.py:182 | OknoWieczor.__init__ | `self.lista_plytek.przelacz_wczesniejsze.connect(lambda: QTimer.singleShot(0, self._przelacz_wczesniejsze))` | okno -> okno | NIE |
| 11 | ui/okno.py:183 | OknoWieczor.__init__ | `self.lista_plytek.ponow_zapis.connect(lambda: QTimer.singleShot(0, lambda: self._polecenie("ponow_zapis")))` | okno -> okno (polecenie kontrolera w watku okna) | NIE |
| 12 | ui/okno.py:446 | OknoWieczor | `QTimer.singleShot(0, lambda: self._pokaz_plytke(skan_id, gniazdo, poza))` | okno -> okno | NIE |
| 13 | ui/czesci.py:555 | pasek stanu (ustaw) | `QTimer.singleShot(int(LIMIT_LICZENIA_PULI_S * 1000) + 50, self, self._sprawdz_liczenie)` | okno -> okno | NIE |
| 14 | ui/czesci.py:496 | pasek stanu | `self._blysk.timeout.connect(lambda: self._ustaw_blysk(False))` | QTimer w watku okna | NIE |
| 15 | ui/okno.py:122 | OknoWieczor.__init__ | `self._ochrona.timeout.connect(self._koniec_ochrony)` | QTimer w watku okna | NIE |
| 16 | ui/ekran_rano.py:515 | ekran poranny | `self._ochrona.timeout.connect(self._koniec_ochrony)` | QTimer w watku okna | NIE |
| 17 | indicate.py:663 | _wywolaj | `self._na_zdarzenie(dict(z))` (wywolanie zwrotne bez sygnalu Qt) | watek `indicate-<rola>-odpytywanie` (I:635); w programie `na_zdarzenie` = None (A:414 go nie podaje; domyslne I:1277) - zdarzenia odbiera watek okna przez `odbierz_zdarzenia` (K:2241) | NIE (w programie nieustawione) |
| 18 | indicate.py:560 | _zapisz | `self._dziennik(wpis)` | watki indicate; w programie None (A:414) | NIE |
| 19 | indicate.py:1091 | _wykonaj_plan | `hak()` (`przed_wyslaniem_planu`, I:168 - hak testow) | watek `-polecenia`; w programie None | NIE |
| 20 | ui/czesci.py, ui/kandydaci.py, ui/mapa.py | sygnaly widzetow | definicje: czesci.py:423-428, 643-645, 683, 829, 928-931, 1057-1062, 1288-1290; kandydaci.py:65, 108-109; mapa.py:93. emit: czesci.py:454, 664, 708, 889, 896, 1139, 1149, 1204, 1304, 1305, 1370; kandydaci.py:97, 247, 252, 262, 300; mapa.py:424 | okno -> okno (emit w slotach klikniec) | NIE |

QMetaObject.invokeMethod w zakresie: brak (Grep). Pozostale `connect(` w ui/*.py lacza sygnaly widzetow z metodami okna (watek
okna) - nie wyliczane pojedynczo. Odpowiedz na pytanie z tabeli D: w zakresie zadne wywolanie zwrotne z watku roboczego nie dotyka
widzetow bezposrednio.

## Uwagi (fakty)

1. Laptop: `kontroler_api.py` nie ma wlasnych watkow; wszystko z `session.py`, `session_rano.py`, `excel.py`, `excel_com.py` oraz
   publiczne metody `KlientRamki` sa wolane w watku okna (zegar K:1184-1190 albo slot okna). Siec ramek jest tylko w watkach
   `indicate` (A.1 wiersze 20-49); watek okna czeka na nie wylacznie przez zamek `_warunek` i przez `join` przy zamknieciu (A.1 wiersz 58).
2. `LIMIT_PRZETWARZANIA_S = 0.05` (K:127) ogranicza tylko liczbe zdarzen obslugiwanych w jednym `przetworz` (A:1166-1167), nie czas
   pojedynczej operacji.
3. `ui/*.py` nie wola bezposrednio bazy, COM ani sieci; polecenia ida przez metody kontrolera w watku okna, np. ui/okno.py:921
   `self.k.szczegoly_pracy(...)` (komentarz okno.py:919-920: "w watku okna: ... jedno zapytanie do bazy"; blok K:4069, B200).
4. COM: w zakresie brak `CoInitialize`, filtra wiadomosci i limitu (Grep); import `win32com.client` przy pierwszym polaczeniu
   (excel_com.py:40, 50) w watku okna; `CoInitialize` jest tylko w `samokontrola.py:1125` (poza zakresem).
5. Petle `while` bez czekania na warunek zewnetrzny (nie w tabeli A): session.py:528 (wolna nazwa pliku - otwarcie w wierszu 111),
   session_rano.py:855, ui/czesci.py:141, ui/mapa.py:270, ui/obraz.py:133, 141, ramka/logika.py:184, ramka/sprzet_rpi.py:186.
6. Wywolania sprzetu RPi poza kategoriami tabeli A (nie wiersze): `SetPixel` / `SwapOnVSync` (sprzet_rpi.py:200-201), `Clear`
   (sprzet_rpi.py:205, 223), `c.is_active` (sprzet_rpi.py:126) - watek `ramka-petla` (albo glowny przy zamknieciu), poza `warunek`.

## E. Wyciag - wiersze tabeli A z limitem BRAK albo > 3 s i watkiem okna albo NIEUSTALONE (114 wierszy)

A: 1, 2, 9-19, 50-57, 59-76, 78-114, 119, 122-124, 156-159, 167-181, 183-188, 202, 212, 213, 217, 240, 241, 248, 256, 303.
(BST liczone jako > 3 s, bo pierwszy stan K:1330 <- A:583 i stan koncowy A:1555 ida z B5000; wiersze tylko-B200 / B150 nie wchodza.)

## F. Wyciag - tabela B, STARA wartosc = TAK

B: 7 (indicate.py:978), 8 (indicate.py:1094).
