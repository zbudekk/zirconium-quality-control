WERDYKT T5: ZAL z odstepstwem O8 (czesc A, 127.0.0.1, kod z instalacji: potwierdzenia 5 z 5 w 100 z 100 powtorzen = 500 z 500, 0 powtorek; plan odtworzony maks 0,52 s; stan po Spacji maks 9 ms / 36 ms z oknem; czesc B na adresie LAN <adres-IP>: plan i kolory na ramce W w 3 z 3 skanow, posredniki 57 i 20 polaczen)

# T5 - Ramka na atrapie w sieci lokalnej - WYNIK (odbior 21.11.2026)

Wykonawca: sesja T3/T6/T5 (tor ciezkich krokow 3). Plik prowadzony przyrostowo (werdykt w pierwszym wierszu - na koncu).
`<K>` = `<PC-katalog>\t0\odbior\Stanowisko` (instalacja wspolna 0.3.1, GOTOWE 02:51:47), `<ST>` =
`<PC-katalog>\t0\repo\Ramki\stanowisko`, `<ODB>` = `<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy`, `<ROB>` =
`<PC-katalog>\koordynator\robocze\odbior\T5`. Porty 8765-8768 uzywa tylko ta sesja (przed testem wolne - `netstat`).

## Czesc A - liczby kryterium (testy na kodzie z instalacji, 127.0.0.1)

Polecenia planu bez zmian (dodane tylko `< NUL`), pliki `krok_t5_a1.cmd` i `krok_t5_a2.cmd`, `set QT_QPA_PLATFORM=offscreen`:

    call <K>\Polecenie.cmd <ODB>\narzedzia\pytest_instalacja.py --st <ST> --wynik <ROB>\t5_zrodlo_kodu_1.txt -- <ST>\testy\test_indicate.py <ST>\testy\test_ramka.py -q -s -rA -p no:cacheprovider --rootdir <ST> -k "test_k1 or test_k2 or test_k4 or test_k5 or test_k6 or test_k7 or test_zz_k8" > <ROB>\t5_testy.log 2>&1 < NUL
    call <K>\Polecenie.cmd <ODB>\narzedzia\pytest_instalacja.py --st <ST> --wynik <ROB>\t5_zrodlo_kodu_2.txt -- <ST>\testy\test_aplikacja_rano.py -q -s -rA -p no:cacheprovider --rootdir <ST> -k "test_a_ or test_k1_plan_ramki_porannej or test_k2_enter or test_k4_spacja" > <ROB>\t5_testy_2.log 2>&1 < NUL

| Polecenie | Czas (zegar `.cmd`) | Kod | Wiersz podsumowania | Zrodlo kodu |
|---|---|---|---|---|
| 1 (`test_indicate.py`, `test_ramka.py`) | 2:57:55,61 - 2:58:44,22 | 0 | `20 passed, 99 deselected in 46.11s` (wierszy `PASSED` 20, `FAILED` / `ERROR` 0) | INSTALACJA: 20 modulow z instalacji, 0 z repo; pliki `*.py` instalacji = repo 79 z 79 |
| 2 (`test_aplikacja_rano.py`) | 2:58:47,45 - 2:59:03,91 | 0 | `4 passed, 24 deselected in 13.49s` (wierszy `PASSED` 4) | INSTALACJA: 60 modulow z instalacji, 0 z repo; pliki 79 z 79 |

Jedna proba kazdego polecenia; zaden test czasowy nie padl, wiec powtorek wg reguly planu nie bylo. O14 NIE zachodzi
(werdykt INSTALACJA, kod 0 w obu przebiegach). Ograniczenie narzedzia (zapisane w `t5_zrodlo_kodu_*.txt`): procesy
potomne testow (ramka w osobnym procesie) importuja kod sami - dla nich zgodnosc potwierdza licznik plikow 79 z 79.

**Co jeszcze liczylo na PC w czasie pomiarow czasu (02:57:55-02:59:04; `ciezkie.log` + `Get-Process python`):** T1
`krok_4.cmd` (pelny pytest, tor 1, od 02:53:21), T10 `krok_t10.cmd` (regresja silnika, tor 2, od 02:52:26), T12
`krok_B.cmd` (tor 4, od 02:55:37; instalacja `K_B` 0.3.9-migracja). Wolny RAM 71347 MB. Pomiary sa wiec "pod obciazeniem".

Wartosci zmierzone (wyjscie `-s`, przepisane z `t5_testy.log` i `t5_testy_2.log`):

| Liczba kryterium | Test | Zmierzone w odbiorze | Prog | Werdykt |
|---|---|---|---|---|
| 5 z 5 potwierdzen bez sieci, 0 powtorek | `test_indicate.py::test_k5_utrata_sieci_5_potwierdzen_100_powtorzen` | `POMIAR K5: 100 powtorzen, zdarzen odebranych 500 z 500 (0 powtorek, 0 luk), nieudanych zadan laptopa 225, odpowiedzi zgubionych przez posrednik 225` = 5 z 5 w 100 z 100 powtorzen | 5 z 5, 0 powtorek | spelnione |
| jw. (strona ramki) | `test_ramka.py::test_k5_utrata_sieci_5_potwierdzen_100_powtorzen` | `POMIAR K5: 100 powtorzen, potwierdzen odebranych 500 z 500, zdarzen 602, nieudanych odpytan (awaria / zgubiona odpowiedz) 222` | 5 z 5 | spelnione |
| plan odtworzony do 5 s (restart ramki) | `test_indicate.py::test_k6_restart_ramki_laptop_wysyla_plan_ponownie_do_5_s` | `POMIAR K6: 3 restarty ramki, plan ponownie po 0.03, 0.03, 0.52 s od startu ramki, 0.22, 0.23, 0.74 s od zabicia poprzedniego procesu ramki` - maks. 0,52 s (0,74 s od zabicia) | <= 5 s | spelnione |
| jw. (strona ramki) | `test_ramka.py::test_k6_restart_ramki_laptop_wysyla_plan_ponownie_do_5_s` | `POMIAR K6: plan ponownie w ramce po 0.06 s od zatrzymania programu ramki` | <= 5 s | spelnione |
| stan po Spacji ponizej 1 s | `test_indicate.py::test_k7_spacja_zmienia_stan_ramki_w_ponizej_1_s_dwa_procesy` | `POMIAR K7: 10 Spacji, stan ramki W po: mediana 7 ms, maks 9 ms` | < 1000 ms | spelnione |
| jw. (strona ramki) | `test_ramka.py::test_k7_spacja_zmienia_stan_ramki_w_ponizej_1_s_dwa_procesy` | `POMIAR K7: 10 zmian stanu, mediana 4 ms, maks 4 ms` | < 1000 ms | spelnione |
| jw. (program + okno) | `test_aplikacja_rano.py::test_k4_spacja_ramka_w_ponizej_1s_kolory_rowne_mapie_i_petla_okna` | `[kryterium 4] Spacja -> stan atrapy W: maks 36 ms (5 prob, prog 1000 ms); kolory W = mapa w 95 gniazdach; najdluzsza przerwa petli okna 34 ms (tykniec 378)` | < 1000 ms | spelnione |
| jw. (prawdziwa aplikacja) | `test_aplikacja_rano.py::test_a_prawdziwa_aplikacja_spacja_ramka_w_kolory_mapy_i_plan_ramki_p` | `[A12, Aplikacja] Spacja -> ramka W 69 ms; kolory W = mapa w 19 gniazdach; plan P = session: 278 pol` | < 1000 ms | spelnione |
| plan, kolory | `test_indicate.py::test_k1_plan_porannej_23_gniazda_matryca_piksel_po_pikselu`, `test_ramka.py::test_k1_*` (3 testy), `test_aplikacja_rano.py::test_k1_plan_ramki_porannej_rowny_planowi_session_pole_po_polu` | 5 z 5 PASSED; `[kryterium 1] 5 plany na atrapie P = plan_plytek: 1115 pol zgodnych, 0 roznych` | zgodne | spelnione |
| kuweta po kuwecie | `test_indicate.py::test_k2_*` (1), `test_ramka.py::test_k2_*` (4), `test_aplikacja_rano.py::test_k2_enter_na_ramce_raz_w_zdarzeniach_po_restarcie_i_zamknij_piec_tylko_biezacy` | 6 z 6 PASSED; `[kryterium 2] potwierdzenie z Enter: 1 wpis po 3 uruchomieniach (historia x2); zamknij_piec biezacy: zamknieto 1; z historii: nieaktualne, piec otwarty; zdarzen ramki 17, duplikatow 0` | zgodne | spelnione |
| zmiana plytki | `test_ramka.py::test_k4_zmiana_plytki_4_0_5_ponizej_100_ms_i_zdarzenia` (+ 2 testy `test_k4_*czas_sztuczny*`) | `POMIAR K4 seria 1: ok; 40 przelaczen (czujniki -> klatka na matrycy), sciennie: mediana 38 ms, ponizej 100 ms 40 z 40, maks 48 ms; ... przestoje procesu 0`; 3 z 3 PASSED | < 100 ms | spelnione |
| ruch bez nazw (do T9) | `test_indicate.py::test_zz_k8_*`, `test_ramka.py::test_zz_k8_*` | `POMIAR K8: 3178 zapisow ruchu (1894820 znakow), trafien nazw 0, kluczy poza naglowkiem 0`; `POMIAR K8: zapis ruchu 1507 komunikatow, 690365 znakow; trafienia nazw: 0 wymagane` | 0 | spelnione |

Procesy po czesci A (`Get-Process python`, 02:59:10): zadnego procesu tej sesji.

## Czesc B - atrapa na adresie sieci lokalnej + zapis ruchu (pierwsze wykonanie - krok po kroku)

Pelny zapis krok po kroku, tabela godzin, liczby z posrednikow i lista potkniec: **`t5_siec_lokalna.md`**. Skrot:

- **Adres:** karta Ethernet PC **<adres-IP>** (LAN, nie 127.0.0.1) - atrapy W (port 8765) i P (port 8767) oraz posrednik
  ramki W (port 8766) na tym adresie; posrednik ramki P na 127.0.0.1:8766 (wg kroku 3 planu - jeden `[ramki] port`).
  Zapora nie odmowila nasluchu. To nadal jeden komputer (O8).
- **B1 (03:00:13 / 03:00:15)** - polecenia planu (pliki `krok_t5_b1_atrapa_w.cmd`, `krok_t5_b1_atrapa_p.cmd`):
  `call <K>\Polecenie.cmd narzedzia\atrapa_ramki.py --rola W --host <adres-IP> --port 8765 --sterowanie` i
  `call <K>\Polecenie.cmd narzedzia\atrapa_ramki.py --rola P --host <adres-IP> --port 8767 --sterowanie`; konsola przez
  potok z pliku polecen (sesja bez okien), kody wyjscia obu atrap 0 (po `koniec`).
- **B2 (03:00:33)** - `PY -I <ROB>\robocze\posrednik_ctrlc.py <ODB>\narzedzia\posrednik_ruchu.py --sluchaj <adres-IP>:8766
  --cel <adres-IP>:8765 --zapis <ROB>\ruch_ramka_w.bin` oraz `... --sluchaj 127.0.0.1:8766 --cel <adres-IP>:8767
  --zapis <ROB>\ruch_ramka_p.bin` (POLECENIE PLANU ZMIENIONE: dodany pomocnik `posrednik_ctrlc.py`, ktory tylko wlacza
  obsluge Ctrl+C i uruchamia niezmieniony `posrednik_ruchu.py` - bez niego Ctrl+C w sesji bez okna nie dziala; port 8768
  nieuzyty).
- **B3 (02:59:30)** - `<ROB>\ustawienia.toml` = kopia `<K>\ustawienia.toml` z `[ramki] port = 8766`, `wieczorna_host =
  "<adres-IP>"`, `poranna_host = "127.0.0.1"` (3 wiersze rozne); `<K>\ustawienia.toml` bez zmian (SHA-256 przed i po
  4303ec76c74fb4a2925fa93056a3bf8b58639119117554795cd30b143e144e4d).
- **B4 (03:01:18-03:03:56, ciezki krok pod blokada: `powershell -NoProfile -ExecutionPolicy Bypass -File
  <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 3 -Kto odb-T5 -Polecenie "<PC-katalog>\koordynator\robocze\odbior\T5\krok_t5_b4.cmd"`)**,
  w pliku polecenie planu: `call <K>\Polecenie.cmd <ODB>\narzedzia\t2_wieczor.py --ustawienia-wzor <ROB>\ustawienia.toml
  --roboczy <ROB>\t5_wieczor --projekty <ROB>\robocze\Cyrkon --wybierz 1,3,8 --odstep 60 > <ROB>\t5_wieczor.log 2>&1 < NUL`
  (`<folder_cyrkon>` = wlasna kopia `<PC-katalog>\app\Prace_test`: 15 folderow, 17 STL). Kod sterownika **0**, kod
  `ciezki.ps1` 0. Jedna proba.
  - Ramka W dostala plan i kolory w **3 z 3 skanow**: 10 x `PUT /plan -> 200` (plytki 1, 3, 2; po 9 gniazd), 9 x
    `PUT /tryb -> 200` (3 x skanowanie, analiza, gotowa), 1 x `DELETE /plan -> 200` przy zamknieciu programu. Kolory
    pierwszej wersji planu kazdego skanu = kolory mapy odczytane z ekranu przez sterownik (czerwony / zolty / zielony:
    2/4/3, 2/1/6, 1/2/6 - zgodne 3 z 3 skanow, 27 z 27 gniazd wg licznikow); 7 decyzji "Ukruszona" na pracach zoltych =
    7 kolejnych wersji planu (zolty -> czerwony).
  - Konsola atrapy W (polecenia planu): `plytka 1` (03:02:21) -> `stan`: plytka 1, plan wazny, tryb `wynik`;
    `klawisz enter` (03:02:23) -> `stan` bez zmiany (ramka W nie ma klawiszy); potem `plytka 3`, `plytka 2` po planach
    skanow 2 i 3 - plan wazny w 3 z 3 odczytow po polozeniu plytki. Nowy skan gasi plan poprzedniego (3 z 3).
  - Ramka P: program polaczyl sie przez posrednik (17 x `GET /zdarzenia`, 1 x `GET /stan`, 1 x `DELETE /plan`), planu nie
    wysylal (tryb wieczorny) - zgodnie z planem ramka P w programie z paczki NIE jest sprawdzana.
- **B5 (03:04:45, Ctrl+C)**: `POSREDNIK koniec: polaczen 57, nieudanych polaczen z celem 0, bajtow do ramki 14265, bajtow z
  ramki 20794` (W) i `POSREDNIK koniec: polaczen 20, nieudanych polaczen z celem 0, bajtow do ramki 2681, bajtow z ramki
  6625` (P). N > 0 w obu - proba wazna.
- **Co jeszcze liczylo w kroku B4:** T1 `krok_4.cmd` (pelny pytest; ok. 22 % o 03:00, czyli przed `test_silnik.py`), T10
  `krok_t10.cmd` (tor 2), T12 `krok_B_uzup.cmd` (tor 4, do 03:03:55), od 03:03:56 T7 `krok_A.cmd`; RAM wolny 69349 MB.
  Czesc B nie ma progow czasowych T5; czasy sterownika (informacyjnie): start analizy 0,442 / 0,446 / 0,381 s, mapa
  54,12 s (pierwsza plytka, pula zimna) / 26,26 / 25,31 s, najdluzsza przerwa petli okna 50,6 ms.
- **Czego czesc B nie mierzy (O8):** 5 potwierdzen bez sieci, restart ramki, Spacja, ramka P z planem - na adresie LAN
  NIE ZMIERZONO (tak stanowi plan); te liczby sa tylko z czesci A (127.0.0.1).

### Obserwacja z kroku B4 poza kryterium T5 (do wiadomosci koordynatora przed T2)

Sterownik T2 w tej probie skroconej (3 skany) wypisal "lista do dofrezowania: ROZNA (oczekiwanych 13, w programie 12,
brakuje 1)" i "T2 LACZNIE: FAIL (4 z 5 kryteriow ZAL, 1 FAIL)": 1 praca z ubytkiem wg prawdy zostala pokazana na ZIELONO
(pozycja 8 scenariusza, sha16 247ee785f428396f; ubytki wg prawdy 13: czerwone 5, zolte 7, zielone 1). To nie jest wynik
T2 (proba skrocona) ani czesc kryterium T5, ale te same skany sa w pelnym scenariuszu T2. Pierwsza plytka (pula zimna):
mapa 54,12 s od zapisu (ponad 40 s; pod obciazeniem T1 / T10 / T12).

## Procesy i porty po tescie

03:05:00: `netstat` - 0 gniazd `LISTENING` na portach 8765-8768 (same `TIME_WAIT`); `Get-Process python` - zadnego procesu
tej sesji (atrapy PID 34260, 39404 i posredniki PID 29584, 35112 zakonczone; kody atrap 0). Cudzych procesow nie ruszano.
`<K>` bez zmian (zadnego pliku nowszego niz GOTOWE.txt poza `dane\`; suma `ustawienia.toml` jak przed testem);
`git -C <REPO> status --short` pusty.

## Werdykt czesci kryterium

| Czesc kryterium | Zmierzone | Gdzie | Werdykt |
|---|---|---|---|
| plan, kolory | 5 z 5 testow `test_k1_*` PASSED; 1115 pol planu zgodnych, 0 roznych | A (127.0.0.1, kod z instalacji) | ZAL z odstepstwem O8 |
| plan, kolory na adresie LAN | plan i kolory w 3 z 3 skanow, 10 planow x kod 200, kolory = mapa 3 z 3 | B (<adres-IP>, program z paczki) | wykonane (O8: bez progu) |
| kuweta po kuwecie | 6 z 6 testow `test_k2_*` PASSED; duplikatow zdarzen 0 | A | ZAL z odstepstwem O8 |
| zmiana plytki | 40 z 40 przelaczen ponizej 100 ms, mediana 38 ms, maks 48 ms | A | ZAL z odstepstwem O8 |
| 5 potwierdzen bez sieci: 5 z 5 dostarczonych, 0 powtorek | 500 z 500 w 100 powtorzeniach (5 z 5 w 100 z 100), 0 powtorek, 0 luk; strona ramki 500 z 500 | A | ZAL z odstepstwem O8 |
| restart ramki: plan odtworzony do 5 s | 0,03 / 0,03 / 0,52 s od startu ramki (0,22 / 0,23 / 0,74 s od zabicia procesu), 3 z 3; strona ramki 0,06 s | A | ZAL z odstepstwem O8 |
| Spacja: stan ponizej 1 s | maks 9 ms (10 Spacji, mediana 7 ms); strona ramki maks 4 ms; program + okno maks 36 ms (5 prob); prawdziwa aplikacja 69 ms | A | ZAL z odstepstwem O8 |
| zrodlo kodu = INSTALACJA | 2 z 2 przebiegow, 0 modulow z repo, pliki 79 z 79, kody 0 | A | spelnione (O14 nie zachodzi) |
| posredniki: N > 0 | W 57 polaczen, P 20 polaczen | B | spelnione |

**T5 = ZAL z odstepstwem O8** (wszystkie liczby kryterium z testow na 127.0.0.1, atrapa i program na jednym komputerze;
na adresie LAN <adres-IP> tylko przebieg ramki W z 3 skanami - wykonany, 3 z 3). Testy czasowe czesci A mierzone pod
obciazeniem (T1, T10, T12) - wszystkie przeszly w pierwszej probie, powtorek nie bylo.

Odstepstwa: **O8**. O14 nie zachodzi. **NOWE (sposob wykonania czesci B, nie zmienia liczb):** (1) sesja bez okien - konsola
atrap przez potok z pliku polecen, polecenia wpisywal skrypt wykonawcy; (2) posrednik uruchomiony przez pomocnik
`posrednik_ctrlc.py` (wlacza Ctrl+C; kod posrednika z repo bez zmian), Ctrl+C wyslany pomocnikiem `ctrlc.py`; (3) posrednik
ramki P na 127.0.0.1:8766 zamiast `<adres PC>:8768` (sprzecznosc krokow 2 i 3 planu - obowiazuje krok 3).

## Polecenia planu, ktore trzeba bylo zmienic

1. Krok B2: `PY -I <ODB>\narzedzia\posrednik_ruchu.py ...` -> `PY -I <ROB>\robocze\posrednik_ctrlc.py
   <ODB>\narzedzia\posrednik_ruchu.py ...` (blad pierwotnego: po Ctrl+C w sesji bez okna proces zyje dalej, brak wiersza
   `POSREDNIK koniec`; proba o 02:50 na porcie 8768).
2. Krok B2, ramka P: `--sluchaj <adres PC>:8768` -> `--sluchaj 127.0.0.1:8766` (wg kroku 3 planu).
3. Krok B1: bez `< NUL` (konsola atrapy czyta polecenia z wejscia); uruchomienie w tle zamiast w 2 oknach.
4. Krok B4: `--projekty <folder_cyrkon>` = `<ROB>\robocze\Cyrkon` (wlasna kopia; plan nie podaje sciezki).
Czesc A: bez zmian.

## Do decyzji koordynatora / wlasciciela

- Obserwacja B4: 1 praca z ubytkiem pokazana na zielono na pozycji 8 scenariusza T2 (lista do dofrezowania rozna) -
  do zestawienia z wynikiem T2.
- Czy sposob wykonania czesci B (skrypt zamiast czlowieka przy konsoli atrapy, pomocnik Ctrl+C) wystarcza, czy czesc B
  ma byc powtorzona recznie w sesji z oknami.
- Zapora Windows: nasluch na adresie karty bez pytania; dostep z innego komputera niesprawdzony (T15).

## Dowody (w `<ROB>`)

`t5_testy.log`, `t5_testy_2.log`, `t5_zrodlo_kodu_1.txt`, `t5_zrodlo_kodu_2.txt`, `t5_wieczor.log`, `t5_siec_lokalna.md`,
`t5_wynik.md` (kopia `WYNIK.md` pod nazwa z planu), `WYNIK.md`, `kody.txt`, `krok_t5_*.cmd`, `atrapa_w.log`,
`atrapa_p.log` (log i odpowiedzi `stan` atrap: tylko adres, metoda, trasa, kod, liczby), `posrednik_w.log`,
`posrednik_p.log` (+ puste `.err`), `t5_konsola_w.log` (dziennik polecen konsoli), `t5_ruch_liczniki.txt` (liczniki z
zapisu ruchu). NIE do repo (zostaja w `<ROB>`): `ruch_ramka_w.bin`, `ruch_ramka_p.bin` (do T9), `t5_wieczor\` (baza,
kopie skanow STL, logi programu - 165 MB), `robocze\` (kopia puli projektow z nazwami folderow zlecen, pomocniki,
pliki polecen konsoli), `ustawienia.toml` (kopia ustawien z `[ramki]` - znaki spoza ASCII).
