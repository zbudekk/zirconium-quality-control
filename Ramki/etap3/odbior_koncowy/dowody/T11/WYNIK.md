WERDYKT T11: ZAL - N = 40 z 40 skanow *_r54 przez aplikacje; uklad rozpoznany 40 z 40 (P2 24 z 24, P3a 16 z 16), uklad_zrodlo auto 40 z 40; ostrzezenia o ukladzie: z nazwa 0, bez nazwy (FAIL skanu) 0; zielone przy zlym ukladzie 0 (0 z 0 skanow; T2 poz. 7: zielonych 0); skany.uklad zapisany 40 z 40; czesc A: auto_uklad bez_numeru 40 z 40, zle_ale_pewny 0 (z_numerem 16 z 16 - plan podaje 40 z 40), testy 45 passed / 0 failed; O6 = informacja (druga galaz kryterium niespelnialna w programie); kod programu 0

# T11 - Stare plytki - WYNIK (odbior koncowy etapu 3, 21.11.2026)

Wykonawca: sesja T11 (konto <konto-PC>). Plik prowadzony przyrostowo; werdykt w pierwszym wierszu dopiero na koncu.

## Stan wejsciowy (04:40)

- Paczka 0.3.1, commit 571e186; instalacja wspolna <K> = <PC-katalog>\t0\odbior\Stanowisko (wersja_biezaca.txt: 0.3.1);
  znak GOTOWE.txt w T0 jest. <K> tylko do uruchamiania - <K>\ustawienia.toml nie zmieniany (SHA-256 poczatek 4303EC76C74FB4A2).
- <REPO> = <PC-katalog>\t0\repo (tylko odczyt), <ST> = <REPO>\Ramki\stanowisko, <ODB> = <REPO>\Ramki\etap3\odbior_koncowy.
- <ROB> = <PC-katalog>\koordynator\robocze\odbior\T11. Duze pliki robocze (eksport skanow, kopia projektow, baza, wyniki,
  logi programu): <ROB>\robocze\ (poza dowodami).
- Zestaw skanow *_r54: <PC-katalog>\app\dane_ref\syntetyczne_r54_P2 = 24 STL + 24 prawdy .json (12 okraglych);
  syntetyczne_r54_P3a = 16 STL + 16 .json (12 okraglych). Razem N = 40 (zgodnie z planem).
- Tor ciezkich krokow: 2 (o 04:40 wolny; ostatni wpis ciezkie.log: KONIEC T2 tor 2 04:34:09). RAM wolny 75495 MB z 95652.
- Procesy python przed startem: 1 (PID 12012 z 01:37 - znany, niczyj).

## Przygotowanie (04:41-04:43)

- `robocopy <PC-katalog>\app\Prace_test <ROB>\robocze\Cyrkon /E` - kod 1 (pliki skopiowane): 15 folderow, 17 STL, 43 MB.
- Wlasny plik ustawien (zasada 3 "Ustalen koordynatora"): kopia <K>\ustawienia.toml -> <ROB>\ustawienia.toml; zmienionych
  wierszy 11 z 121 (11 kluczy [sciezki]): folder_eksportu_skanera = <ROB>/robocze/eksport, folder_cyrkon = <ROB>/robocze/Cyrkon,
  folder_prywatne = <ROB>/robocze/Prywatne (pusty), folder_millbox = <ROB>/robocze/millbox (pusty), baza, log_excel, wyniki,
  podglady, pula_cache, logi, kalibracja_ramek = <ROB>/robocze/dane/... ; 0 pozostalych odwolan do t0/odbior. Reszta pliku bez zmian.

## Czesc A

Plik <ROB>\krok_A.cmd (3 polecenia, kazde z `call`, wejscie `< NUL`), uruchomiony 04:43 przez
`powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 2 -Kto T11 -Polecenie "<PC-katalog>\koordynator\robocze\odbior\T11\krok_A.cmd"`
(plan: czesc A lekka; puszczona mimo to przez tor 2, bo razem trwa ponad 3 min - wspolne.md).
### A1 - krok 1 planu (rozpoznanie ukladu narzedziem z instalacji) - 04:42:47 - 04:45:45, kod 0

Polecenie (doslownie z planu; <ROB>\t11_auto jako --wyjscie):
`call <K>\Polecenie.cmd narzedzia\auto_uklad.py --skany <PC-katalog>\app\dane_ref\syntetyczne_r54_P2 <PC-katalog>\app\dane_ref\syntetyczne_r54_P3a --wyjscie <ROB>\t11_auto --procesy 1 --ustawienia <K>\ustawienia.toml < NUL > <ROB>\t11_auto_uklad.log 2>&1`

Wynik (`t11_auto\auto_uklad.json`, sekcja `podsumowanie`; wyciag: `t11_auto_uklad_podsumowanie.json`; log: `t11_auto_uklad.log`):

| Przebieg | skanow | ok | ok_i_pewny | zle_ale_pewny | numer_ok |
|---|---|---|---|---|---|
| bez_numeru | 40 | 40 | 40 | 0 | 24 |
| z_numerem | 16 | 16 | 16 | 0 | 16 |

- bez_numeru: ok = 40 z 40, zle_ale_pewny = 0 z 40 (okragla_poranna_r54 12 z 12, okragla_wieczorna_r54 12 z 12,
  poranna_r54 8 z 8, wieczorna_r54 8 z 8); podstawy: numer_z_dolkow 24, ksztalt 15, dolki_wykluczaja 1; ksztalt: wlasciwy
  max 0,0 mm2, inny min 21,2 mm2; czas rozpoznania mediana 2,45 s, max 2,86 s; calosc 177,9 s.
- z_numerem: ok = 16 z 16, zle_ale_pewny = 0 z 16. ROZNICA WOBEC PLANU: plan oczekuje "z_numerem: ok = 40 z 40"; narzedzie
  liczy przebieg z_numerem TYLKO dla plytek kwadratowych (`auto_uklad.py` wiersz 40: `if kwadrat`), a w zestawie jest 16
  kwadratowych i 24 okragle - 40 z 40 w tym przebiegu jest nieosiagalne z definicji narzedzia. Liczba faktyczna: 16 z 16
  (wszystkie, ktore narzedzie liczy). Do decyzji koordynatora: poprawka tekstu planu (nie wynik programu).
- Werdykt A1: bez_numeru 40 z 40 i 0 zle_ale_pewny - zgodne z planem; z_numerem 16 z 16 (plan: 40 z 40 - liczba planu bledna).
### A4 - krok 4 planu (testy "zly uklad wymuszony recznie") - polecenie planu doslownie - 04:45:45 - 04:47:35, kod 0

`call <K>\Polecenie.cmd -m pytest <ST>\testy\test_session_wieczor.py <ST>\testy\test_straznik.py <ST>\testy\test_kontroler_api.py <ST>\testy\test_auto_uklad.py -q -rA -p no:cacheprovider --rootdir <ST> -k "niezgodny_uklad or niezgodna_z_ukladem or auto or innego_ukladu" < NUL > <ROB>\t11_testy.log 2>&1`

- Wiersz podsumowania: `45 passed, 174 deselected, 1 warning in 108.51s (0:01:48)`; kod wyjscia 0 (proba paczki: 45 passed, 174 deselected).
- Uwaga: w tej postaci interpreter i pakiety sa z instalacji, a kod programu laduje sie z <REPO> (conftest.py wstawia <ST> na
  poczatek sys.path - opis w `pytest_instalacja.py`). Dlatego nizej ten sam wybor testow na kodzie z instalacji.

### A4i - ten sam wybor testow na KODZIE Z INSTALACJI (dodatek wykonawcy, wg zlecenia testu) - 04:47:35 - 04:49:25, kod 0

`call <K>\Polecenie.cmd <ODB>\narzedzia\pytest_instalacja.py --st <ST> --wynik <ROB>\t11_testy_zrodlo_kodu.txt -- <ST>\testy\test_session_wieczor.py <ST>\testy\test_straznik.py <ST>\testy\test_kontroler_api.py <ST>\testy\test_auto_uklad.py -q -rA -p no:cacheprovider --rootdir <ST> -k "niezgodny_uklad or niezgodna_z_ukladem or auto or innego_ukladu" < NUL > <ROB>\t11_testy_instalacja.log 2>&1`

- Wiersz podsumowania: `45 passed, 174 deselected, 1 warning in 107.92s (0:01:47)`; kod 0.
- `t11_testy_zrodlo_kodu.txt`: z instalacji 51 modulow, z repo poza testami 0 modulow; pliki *.py instalacji = repo: 79 z 79;
  WERDYKT ZRODLA KODU: INSTALACJA (ograniczenie narzedzia: procesy potomne testow importuja kod sami).

Czesc A razem (blokada toru 2: START 04:42:47, KONIEC 04:49:25, kod 0): A1 40 z 40 / 0 zle_ale_pewny; A4 45 passed, 0 failed
(2 przebiegi: kod z repo i kod z instalacji). Procesy python po czesci A: 1 (PID 12012 - cudzy, znany); moich 0.
Co jeszcze liczylo na PC w czasie czesci A: tory 1, 3, 4 bez wpisow START w tym oknie (ciezkie.log); rownolegle wykonawcy T8 i T7
(kroki lekkie) - czasy czesci A nie sa kryterium.

## Teksty komunikatow programu (z kodu instalacji) - 04:44

`call <K>\Polecenie.cmd <ROB>\robocze\narz\teksty_komunikatow.py <ROB>\t11_komunikaty.txt` (kod 0; skrypt wykonawcy, tylko odczyt:
wola `statusy.tekst_komunikatu` / `tekst_pytania` z `<K>\wersje\0.3.1\program\stanowisko\statusy.py`; zapis ASCII).

- status `niezgodny_uklad` -> komunikat (poziom blad) "Plytka nie pasuje do ukladu": "Program nie rozpoznal ukladu plytki na
  tym skanie - nic nie zostalo sprawdzone. Sprawdz, czy plytka lezy w skanerze prosto i w calosci, i zeskanuj ja ponownie."
  Nazwy ukladu NIE zawiera (wzor bez pol - nie ma gdzie wstawic nazwy).
- status `plytka_nie_z_trybu` -> pytanie (poziom blad) "Plytka nie z tego trybu": "To plytka poranna, a program pracuje w
  trybie "Wieczor". Skan jest zablokowany: nic nie jest zielone i nie mozna zapisywac decyzji." To blokada trybu, nie
  ostrzezenie o ukladzie; nazwy ukladu (np. poranna_r54) NIE zawiera - podaje tylko typ plytki (poranna / wieczorna).
- Druga galaz kryterium ("ostrzezenie z nazwa wlasciwego ukladu"): w programie NIESPELNIALNA - zaden z tekstow, ktore program
  pokazuje przy skanie o statusie `niezgodny_uklad`, nie ma pola na nazwe ukladu (potwierdzenie O6 / braku B5 na kodzie paczki).

## Czesc B (przez aplikacje, tor 2)

Pliki: <ROB>\krok_B.cmd (symulator + czekanie na koniec programu) i <ROB>\krok_B_program.cmd (program, startowany z krok_B.cmd
przez `start "" /b cmd /c`). Start 04:49:34 przez
`powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 2 -Kto T11 -Polecenie "<PC-katalog>\koordynator\robocze\odbior\T11\krok_B.cmd"`.

- Program: `call <K>\Polecenie.cmd -m stanowisko.aplikacja --ustawienia <ROB>\ustawienia.toml --zamknij-po 3000 < NUL > <ROB>\robocze\t11_program_stdout.log 2>&1`
  (QT_QPA_PLATFORM=offscreen; baza pusta - katalog <ROB>\robocze\dane przed startem: 0 plikow; tryb programu po starcie na pustej
  bazie: wieczor). `--zamknij-po` 3000 wg planu (40 x 45 s + 1200 s zapasu).
- Symulator (20 s po starcie programu): `call <K>\Polecenie.cmd narzedzia\symulator_skanera.py --folder <ROB>\robocze\eksport --zrodla <PC-katalog>\app\dane_ref\syntetyczne_r54_P2 <PC-katalog>\app\dane_ref\syntetyczne_r54_P3a --ile 40 --odstep 45 --rownolegle 1 --seed 1 --dziennik <ROB>\t11_symulator.json < NUL > <ROB>\t11_symulator.log 2>&1`
  (symulator bierze zrodla kolejno: 24 pliki P2 posortowane, potem 16 plikow P3a - kazdy skan dokladnie raz; zapisuje je pod
  nazwami skan_0001.stl ... skan_0040.stl, wiec program nie widzi nazwy ukladu w nazwie pliku).
- Prawda: <ROB>\t11_prawda.tsv (skrypt wykonawcy `robocze\narz\prawda_sha16.py`, PY -I, kod 0): 40 wierszy, 40 roznych sha16;
  pole `plytka` prawdy: P2 - po 6 x okragla_poranna_r54, okragla_wieczorna_r54, poranna_r54, wieczorna_r54; P3a - 6 x
  okragla_poranna_r54, 6 x okragla_wieczorna_r54, 2 x poranna_r54, 2 x wieczorna_r54. Razem 20 plytek porannych (w trybie
  wieczor oczekiwany status plytka_nie_z_trybu, uklad ma byc zapisany) i 20 wieczornych.

Przebieg (dopisywany):
- 04:49:34 start programu (posrednik srodowiska wersji PID 30200 -> interpreter PID 31804 -> proces silnika PID 9660);
  04:49:54 start symulatora (PID 19248 -> 25856). Inne procesy python w tej chwili: 5 ze sciezka instalacji odbior_t12 /
  Pythona bazowego z 04:50:14-16 (wykonawca T7 - cudze) i PID 12012 (znany).
- 04:52:11 odczyt w trakcie (sql_odczyt.py, baza tylko do odczytu): 3 wiersze `skany` (pliki w eksporcie: 4) - id 1-3: status
  plytka_nie_z_trybu, tryb wieczor, uklad okragla_poranna_r54, uklad_zrodlo auto, uklad_zgodny 1, numer 9; czas_s 43,56 (pula
  zimna), 19,55, 16,2.- 04:59:23 odczyt w trakcie: 13 wierszy `skany` na 13 plikow w eksporcie: plytka_nie_z_trybu + okragla_poranna_r54 x 6 (id 1-6),
  do_powtorzenia + okragla_wieczorna_r54 x 3, przyjety + okragla_wieczorna_r54 x 3 (id 7-12), plytka_nie_z_trybu + poranna_r54
  x 1 (id 13); wszystkie uklad_zrodlo auto, uklad_zgodny 1; czas_s max 43,6 (1. skan). Procesy programu zyja (silnik 3183 MB).- 05:07:30 odczyt w trakcie: 23 wiersze `skany` na 24 pliki w eksporcie (24. w analizie): okragla_poranna_r54 x 6 i poranna_r54
  x 6 (plytka_nie_z_trybu), okragla_wieczorna_r54 x 6 (3 do_powtorzenia, 3 przyjety), wieczorna_r54 x 5 (4 do_powtorzenia, 1
  przyjety); wszystkie uklad_zrodlo auto, uklad_zgodny 1. Procesy programu zyja.- 05:15:57 odczyt w trakcie: 35 wierszy `skany` na 35 plikow w eksporcie: okragla_poranna_r54 x 12 i poranna_r54 x 6
  (plytka_nie_z_trybu), okragla_wieczorna_r54 x 11 (7 do_powtorzenia, 4 przyjety), wieczorna_r54 x 6 (5 do_powtorzenia, 1
  przyjety); wszystkie uklad_zrodlo auto, uklad_zgodny 1; czas_s max 43,6. Procesy programu zyja (silnik 3428 MB).- 05:19:12 koniec symulatora: kod 0, "zapisano plikow: 40 (dobrych 40, zlych 0)"; dziennik <ROB>\t11_symulator.json.
- 05:20:16 odczyt WSTEPNY (program jeszcze dziala - czeka na --zamknij-po 3000, czyli do ok. 05:39:34): 40 wierszy `skany` na
  40 skanow z dziennika; rozpoznane 40 z 40, uklad_zrodlo auto 40 z 40, niezgodny_uklad 0, uklad niepusty 40 z 40.
  Odczyt koncowy (po zamknieciu programu) - nizej; ten wstepny jest tylko zabezpieczeniem na wypadek restartu PC.
- 05:30:29 kontrola stanu procesu (program czeka na --zamknij-po): procesy 30200 / 31804 / 9660 zyja, Responding = True,
  czas CPU interpretera okna rosnie (27,98 s o 05:20 -> 36,77 s o 05:30) - petla okna pracuje, to nie zawieszenie.
- 05:39:36 program zamknal sie sam: `B program KOD=0`; log programu: "zamkniete, zadan niezakonczonych 0"; zdarzenia:
  program_start 1, program_stop 1, nowy_skan 40, skan_przyjety 40, podglad 40, konflikt_projektu 7. 05:39:40 koniec blokady
  toru 2 (ciezkie.log: START T11 tor 2 04:49:34, KONIEC 05:39:40, kod 0).
- Log programu (<ROB>\robocze\dane\logi\stanowisko.log): "przyjety jako" 40 wierszy, "nie dala wyniku" 0, Traceback 0, ERROR 0;
  ostrzezenia: brak pliku kalibracji ramek (start) i 2 x "zgaszenie ramki ... nie doszlo" (zamkniecie; ramek w tescie nie ma).
  Wyjscie standardowe programu: 0 bajtow.
- Czasy analizy (kolumna skany.czas_s; NIE sa kryterium T11): min 11,0 s, srednia 22,3 s, max 49,6 s (id 36), 1. skan po
  zimnym starcie 43,6 s. Kolejka nie rosla: w kazdym odczycie w trakcie liczba wierszy `skany` = liczba plikow w eksporcie
  albo o 1 mniej (skan w analizie). Ostatni skan przyjety 05:19:39, czyli 27 s po koncu symulatora.
- Co jeszcze liczylo na PC w czasie czesci B: ciezkie.log - T7uzup tor 4 04:51:28 - 05:06:14 (seria z programem na instalacji
  odbior_t12); poza tym wykonawca T8 (kroki lekkie). Kryterium T11 nie zalezy od czasu.
- Po tescie (05:40:51): procesy python na PC: 1 (PID 12012 z 01:37 - znany, niczyj). Moich procesow python: 0.

### Krok 3 - odczyt KONCOWY bazy (05:39:58, po zamknieciu programu)

Skrypt wykonawcy <ROB>\robocze\narz\odczyt.ps1 wola dla kazdego zapytania
`PY -I <ODB>\narzedzia\sql_odczyt.py --baza <ROB>\robocze\dane\stanowisko.sqlite "<zapytanie>"` i zapisuje wyjscie (ASCII, LF).
Wszystkie 6 odczytow: kod 0.

- `t11_skany.tsv` (zapytanie planu doslownie): `SELECT id, status, uklad, uklad_zrodlo, uklad_zgodny FROM skany ORDER BY id` - 40 wierszy.
- `t11_zielone.tsv` (zapytanie planu doslownie): `SELECT s.id, s.status, s.uklad, sum(p.status_gniazda='zielony') AS zielonych FROM skany s LEFT JOIN prace p ON p.skan_id = s.id GROUP BY s.id` - 40 wierszy.
- Dodatkowe (wykonawca): `t11_skany_sha16.tsv` (id, sha16, status, tryb, uklad, uklad_zrodlo, uklad_zgodny, numer_plytki,
  czas_analizy, czas_s - do laczenia z prawda po sha16), `t11_zielone_prace.tsv` (prac / zielonych / zoltych / czerwonych /
  szarych na skan), `t11_statusy.tsv`, `t11_zdarzenia.tsv`.
- Laczenie skan - prawda: `PY -I <ROB>\robocze\narz\t11_zestaw.py <ROB>` (kod 0): sha16 z dziennika symulatora -> wiersz prawdy
  (`t11_prawda.tsv`, kontrola: numer zrodla w dzienniku = numer wiersza prawdy, 40 z 40) -> wiersz `skany`. Wynik:
  `t11_tabela.tsv` (pelna tabela), `t11_liczniki.txt`.
- Pliki wynikow skanow zapisane przez program (40 plikow <czas>_<sha16>_wynik.json): `PY -I <ROB>\robocze\narz\wyniki_uklad.py`
  -> `t11_wyniki_uklad.tsv`: 40 z 40 z `plytka` = uklad z prawdy, `plytka_wybor` = auto, `uklad_zgodny` = True,
  `uklad_komunikat` brak, ostrzezen o ukladzie w polu `ostrzezenia`: 0 z 40.

Grupy (t11_statusy.tsv):

| status | uklad | uklad_zrodlo | uklad_zgodny | skanow |
|---|---|---|---|---|
| plytka_nie_z_trybu | okragla_poranna_r54 | auto | 1 | 12 |
| plytka_nie_z_trybu | poranna_r54 | auto | 1 | 8 |
| do_powtorzenia | okragla_wieczorna_r54 | auto | 1 | 8 |
| przyjety | okragla_wieczorna_r54 | auto | 1 | 4 |
| do_powtorzenia | wieczorna_r54 | auto | 1 | 7 |
| przyjety | wieczorna_r54 | auto | 1 | 1 |

### Tabela skan po skanie (N = 40; kolejnosc = kolejnosc symulatora = id w `skany`)

Legenda kolumny "Ostrzezenie o ukladzie":
- "brak" - skan nie ma statusu `niezgodny_uklad`; program nie pokazuje ostrzezenia o ukladzie; w pliku wyniku skanu 0 ostrzezen
  o ukladzie.
- "brak (K-TRYB)" - ostrzezenia o ukladzie brak; skan ma status `plytka_nie_z_trybu` (plytka poranna w trybie wieczor - wg planu
  oczekiwane), do ktorego program pokazuje pytanie (tekst doslowny z kodu instalacji, `t11_komunikaty.txt`): "Plytka nie z tego
  trybu" / "To plytka poranna, a program pracuje w trybie "Wieczor". Skan jest zablokowany: nic nie jest zielone i nie mozna
  zapisywac decyzji." To komunikat o trybie, nie o ukladzie; nazwy ukladu nie zawiera (uklad jest rozpoznany i zapisany).
- "K-UKLAD" - status `niezgodny_uklad`, komunikat "Plytka nie pasuje do ukladu" (bez nazwy ukladu) - w tym tescie 0 skanow.
- Teksty ustalone z kodu instalacji dla statusu skanu odczytanego z bazy; okno programu bylo `offscreen` i ekranu nie
  odczytywano (zastrzezenie pomiaru).
- "Gniazd zielonych (baza)" = liczba prac skanu z `prace.status_gniazda` = 'zielony' (zapytanie planu).

| Nr | sha16 skanu | Zestaw | Uklad wg prawdy | Uklad rozpoznany przez program | Rozpoznany = prawda | Status skanu | Ostrzezenie o ukladzie | Zawiera nazwe wlasciwego ukladu | Gniazd zielonych (baza) | Prac | skany.uklad (zrodlo, uklad_zgodny) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | a33966994b515b9e | P2 | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 3 | 9 | okragla_poranna_r54 (auto, 1) |
| 2 | af212769571c0d65 | P2 | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 4 | 9 | okragla_poranna_r54 (auto, 1) |
| 3 | a5c5683e20431cf3 | P2 | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 4 | 9 | okragla_poranna_r54 (auto, 1) |
| 4 | 5e03ed10436c2b30 | P2 | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 5 | 10 | okragla_poranna_r54 (auto, 1) |
| 5 | 40f034fd7d24fbcb | P2 | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 3 | 12 | okragla_poranna_r54 (auto, 1) |
| 6 | 6e60a2f8be92efe5 | P2 | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 3 | 9 | okragla_poranna_r54 (auto, 1) |
| 7 | ec033c0713e90c42 | P2 | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 5 | 11 | okragla_wieczorna_r54 (auto, 1) |
| 8 | 65df2f5ed75a75c9 | P2 | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 3 | 9 | okragla_wieczorna_r54 (auto, 1) |
| 9 | 8358e17160a25742 | P2 | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | przyjety | brak | nie dotyczy | 4 | 10 | okragla_wieczorna_r54 (auto, 1) |
| 10 | b0aabeec69834bca | P2 | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 3 | 10 | okragla_wieczorna_r54 (auto, 1) |
| 11 | 842d039b1fc1020c | P2 | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | przyjety | brak | nie dotyczy | 3 | 10 | okragla_wieczorna_r54 (auto, 1) |
| 12 | 9d5eeb980330c768 | P2 | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | przyjety | brak | nie dotyczy | 7 | 11 | okragla_wieczorna_r54 (auto, 1) |
| 13 | 75fa520430894f99 | P2 | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 1 | 8 | poranna_r54 (auto, 1) |
| 14 | b03385ae8316e226 | P2 | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 3 | 8 | poranna_r54 (auto, 1) |
| 15 | 823181c04ea8f815 | P2 | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 3 | 10 | poranna_r54 (auto, 1) |
| 16 | b75451bfe836239b | P2 | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 5 | 10 | poranna_r54 (auto, 1) |
| 17 | 007e56008bd77efb | P2 | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 3 | 11 | poranna_r54 (auto, 1) |
| 18 | b7dfa66ec8a53eb3 | P2 | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 4 | 10 | poranna_r54 (auto, 1) |
| 19 | 37b6d5f5a6f45340 | P2 | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 4 | 9 | wieczorna_r54 (auto, 1) |
| 20 | f20136b8b0af6e00 | P2 | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 0 | 9 | wieczorna_r54 (auto, 1) |
| 21 | 7e2cb93bbeaf4701 | P2 | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 4 | 10 | wieczorna_r54 (auto, 1) |
| 22 | 9a1cc0ad42a1b9b0 | P2 | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 2 | 11 | wieczorna_r54 (auto, 1) |
| 23 | 9cc2bd761deb672b | P2 | wieczorna_r54 | wieczorna_r54 | TAK | przyjety | brak | nie dotyczy | 6 | 9 | wieczorna_r54 (auto, 1) |
| 24 | 1745b6260092155c | P2 | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 7 | 11 | wieczorna_r54 (auto, 1) |
| 25 | 5283ca8eabec7b56 | P3a | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 5 | 10 | okragla_poranna_r54 (auto, 1) |
| 26 | c34cb8aea9d7521d | P3a | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 4 | 11 | okragla_poranna_r54 (auto, 1) |
| 27 | 2b3f8513e75dbc18 | P3a | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 2 | 14 | okragla_poranna_r54 (auto, 1) |
| 28 | 5acb59ca6e629bdd | P3a | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 0 | 11 | okragla_poranna_r54 (auto, 1) |
| 29 | 71df6882795263d3 | P3a | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 0 | 11 | okragla_poranna_r54 (auto, 1) |
| 30 | 27f3b336d128b75e | P3a | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 0 | 9 | okragla_poranna_r54 (auto, 1) |
| 31 | 15765b8dc8c550ff | P3a | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 2 | 12 | okragla_wieczorna_r54 (auto, 1) |
| 32 | 3af0bf2e971a0fb3 | P3a | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 0 | 9 | okragla_wieczorna_r54 (auto, 1) |
| 33 | e6681afc6aff4161 | P3a | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 1 | 12 | okragla_wieczorna_r54 (auto, 1) |
| 34 | 0d01a86e2bcffb6f | P3a | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | przyjety | brak | nie dotyczy | 3 | 7 | okragla_wieczorna_r54 (auto, 1) |
| 35 | f8bf9a17bacae2a9 | P3a | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 1 | 8 | okragla_wieczorna_r54 (auto, 1) |
| 36 | efc49cb95972ce92 | P3a | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 0 | 15 | okragla_wieczorna_r54 (auto, 1) |
| 37 | 7d134f6dfa68ea80 | P3a | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 1 | 15 | poranna_r54 (auto, 1) |
| 38 | cad653fc6eda187d | P3a | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 2 | 12 | poranna_r54 (auto, 1) |
| 39 | 5b09c9516ebe0634 | P3a | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 2 | 12 | wieczorna_r54 (auto, 1) |
| 40 | c5d76faa2066aa63 | P3a | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 1 | 10 | wieczorna_r54 (auto, 1) |

### Liczniki (t11_liczniki.txt)

| Licznik | Wynik |
|---|---|
| Skany `*_r54` przeprowadzone przez aplikacje (z wierszem w `skany`) | 40 z 40 (bez wiersza: 0) |
| (a) uklad rozpoznany (`skany.uklad` = `plytka` z prawdy) | 40 z 40 (P2: 24 z 24, P3a: 16 z 16) |
| (a) `uklad_zrodlo` = auto | 40 z 40 |
| uklad zapisany, ale inny niz w prawdzie | 0 |
| ostrzezenie o ukladzie Z nazwa wlasciwego ukladu | 0 (nie wystapilo zadne ostrzezenie o ukladzie) |
| ostrzezenie o ukladzie BEZ nazwy wlasciwego ukladu (FAIL skanu) | 0 z 40 |
| (b) skany ze zlym ukladem (`niezgodny_uklad` / `uklad_zgodny` = 0 / uklad inny niz prawda) | 0 |
| (b) zielone przy zlym ukladzie | 0 (licznik pusty: 0 z 0 skanow) |
| (c) `skany.uklad` niepusty | 40 z 40 |

Po ukladach: okragla_poranna_r54 12 z 12 (P2 6, P3a 6), okragla_wieczorna_r54 12 z 12 (6 + 6), poranna_r54 8 z 8 (6 + 2),
wieczorna_r54 8 z 8 (6 + 2).

(b) - odsylacz wg planu (licznik pusty, bo wszystkie 40 ukladow rozpoznane): skan z niezgodnym ukladem przez aplikacje to
pozycja nr 7 scenariusza T2: `<PC-katalog>\koordynator\robocze\odbior\T2\t2_wynik.json`, wiersz plytki nr 7 (sha16
857369c6c1d3aef3): faktyczny_status = niezgodny_uklad, prac_program = 0, **zielonych = 0**, zgodne = true. (Caly T2 ma werdykt
FAIL z innego powodu - czesc (e) lista "do dofrezowania"; wiersz nr 7 jest zgodny z oczekiwaniem.)

## Werdykt

| Czesc kryterium (plan etapu, sekcja 7) | Wynik | Liczba |
|---|---|---|
| uklad rozpoznany ALBO ostrzezenie z nazwa wlasciwego ukladu | ZAL (pierwsza galezia) | rozpoznane 40 z 40; ostrzezen z nazwa 0; ostrzezen bez nazwy (FAIL skanu) 0 |
| 0 zielonych przy zlym ukladzie | ZAL | 0 (0 z 0 skanow; T2 poz. 7: zielonych 0) |
| uklad zapisany w `skany` | ZAL | 40 z 40 (`uklad_zrodlo` auto 40 z 40) |
| czesc A krok 1 (auto_uklad, kod z instalacji) | zgodne | bez_numeru ok 40 z 40, zle_ale_pewny 0; z_numerem ok 16 z 16, zle_ale_pewny 0 |
| czesc A krok 4 (testy "zly uklad") | zgodne | 45 passed, 0 failed (kod z repo); 45 passed, 0 failed (kod z instalacji) |

**WERDYKT T11: ZAL** (bez odstepstwa wyniku; regula z "Decyzji koordynatora nr 4": 40 z 40 rozpoznanych, 0 zielonych przy zlym
ukladzie, 40 z 40 ukladow zapisanych).

O6 (INFORMACJA, nie obniza wyniku): druga galaz kryterium ("ostrzezenie z nazwa wlasciwego ukladu") jest w programie
NIESPELNIALNA - potwierdzone na kodzie paczki 0.3.1: jedyny komunikat skanu o statusie `niezgodny_uklad` to staly tekst bez pola
na nazwe ukladu ("Program nie rozpoznal ukladu plytki na tym skanie - nic nie zostalo sprawdzone. ..."); napis statusu plytki:
"nie pasuje do zadnego ukladu plytek". W tym tescie galaz nie byla potrzebna ani probowana (0 skanow `niezgodny_uklad`).

## Odstepstwa i zmiany wobec polecen planu

- O6 - informacja (wyzej). Odstepstw wyniku: 0.
- NOWE (liczba planu, nie wynik programu): plan, krok 1, oczekuje `z_numerem`: ok = 40 z 40; narzedzie liczy ten przebieg tylko
  dla plytek kwadratowych (16 z 40 skanow) - wynik 16 z 16. Kryterium T11 (sekcja 7) tego nie dotyczy. Gdyby koordynator uznal
  liczbe kroku 1 za czesc kryterium, wynik bylby "ZAL z odstepstwem NOWE (z_numerem 16 z 16 zamiast 40 z 40)".
- Polecenia zmienione wobec doslownego tekstu planu:
  1. Program: zamiast `<K>\Stanowisko.cmd --zamknij-po <s>` - `call <K>\Polecenie.cmd -m stanowisko.aplikacja --ustawienia
     <ROB>\ustawienia.toml --zamknij-po 3000` (zasada 3 "Ustalen koordynatora" - wlasny plik ustawien; to nie moja zmiana).
  2. Sciezki danych programu w <ROB>\robocze\... (podkatalog <ROB>, zeby STL / baza nie lezaly w katalogu dowodow);
     wyjscie standardowe programu do <ROB>\robocze\t11_program_stdout.log (0 bajtow).
  3. Czesc A (lekka wg planu) puszczona przez blokade toru 2 (razem 6 min 38 s).
  4. Dodatki wykonawcy (nie zastepuja polecen planu): przebieg A4i przez `pytest_instalacja.py`, 4 dodatkowe zapytania
     `sql_odczyt.py`, skrypty w <ROB>\robocze\narz\ (prawda_sha16.py, teksty_komunikatow.py, t11_zestaw.py, wyniki_uklad.py,
     tabela_md.py, odczyt.ps1).
  Bez zmian: polecenie symulatora (poza `--folder` = folder eksportu wlasnego pliku ustawien), oba zapytania kroku 3,
  polecenie testow kroku 4, polecenie kroku 1.

## Do decyzji koordynatora / wlasciciela

1. O6 / brak B5 (wlasciciel): dopisac nazwe wlasciwego ukladu do komunikatu `niezgodny_uklad` albo przyjac kryterium w brzmieniu
   "uklad rozpoznany" - pozycja 10 w RAPORT.md 4a.
2. Tekst planu T11 krok 1: "z_numerem ok = 40 z 40" -> faktycznie 16 z 16 (przebieg tylko dla plytek kwadratowych).
3. Obserwacja poza kryterium: w bazie prace skanow zablokowanych (`plytka_nie_z_trybu`, 20 skanow) maja `status_gniazda` =
   'zielony' w 55 z 208 wierszy `prace` (to wynik analizy zapisany w bazie; uklad tych skanow jest rozpoznany poprawnie, wiec
   NIE jest to "zielone przy zlym ukladzie"). Program wg wlasnego komunikatu pokazuje taki skan jako zablokowany ("nic nie jest
   zielone") - ekranu w T11 nie odczytywano (NIE ZMIERZONO na ekranie). Uwaga dla narzedzi czytajacych baze wprost (np. metryki
   T8): liczenie zielonych bez filtra statusu skanu wlicza prace skanow zablokowanych.
4. Obserwacja: 16 plytek kwadratowych `*_r54` ma w `skany.numer_plytki` wartosc pusta (numer czytany z dolkow jest tylko na
   okraglych: 24 z 40 = prawda; zgodne z krokiem 1: numer_ok 24 z 40) - poza kryterium T11.
5. Obserwacja: po zamknieciu programu kodem 0 w katalogu danych zostaje plik `stanowisko.sqlite.blokada` (0 bajtow) - nie
   oceniam (poza T11).
6. Dowody przed `git add`: pliki z przekierowania cmd maja CRLF (czasy.txt, kody.txt, t11_auto_uklad.log, t11_symulator.log,
   t11_symulator.json, t11_testy.log, t11_testy_instalacja.log), a oba logi testow po 7 bajtow spoza ASCII (wyjscie pytest) -
   wymagaja `dowody_lf.py --napraw` na KOPII dowodow. Do repo NIE ida: `robocze\` (STL, baza, kopia projektow z nazwami
   folderow zlecen, logi programu), `ustawienia.toml` (znaki spoza ASCII - kopia pliku instalacji), `t11_auto\` (pelny
   auto_uklad.json - do dowodow tylko `t11_auto_uklad_podsumowanie.json`). `dowody_lf.py` na calym <ROB> nie uruchamialem
   (zmienilby pliki robocze potrzebne T9 i wypisal nazwy plikow kopii projektow). Kontrola wlasna: w plikach dowodow (poziom
   <ROB> i `t11_auto\`) 0 trafien nazw folderow / plikow z kopii `Prace_test` (32 nazwy sprawdzone).
7. Czas: test trwal ok. 65 min (04:38 - 05:43) przy budzecie ok. 60; czesc B 50 min, z czego ok. 20 min to bezczynne czekanie
   programu na `--zamknij-po 3000` (ostatni skan przyjety 05:19:39, zamkniecie 05:39:36). Zestawu nie skracano.
8. Zjawisko PC (bez wplywu na wynik): jeden wklejony fragment PowerShell (formatowanie tabeli) zostal zablokowany przez
   oprogramowanie antywirusowe ("skrypt zawiera zlosliwa zawartosc") - tabela zrobiona skryptem Python (tabela_md.py).

## Dane zostawione dla T9 (nic nie kasowano)

- Baza T11: `<PC-katalog>\koordynator\robocze\odbior\T11\robocze\dane\stanowisko.sqlite` (180224 bajty; 40 skanow, 413 prac).
- Wyniki skanow: `...\T11\robocze\dane\wyniki\` (40 plikow *_wynik.json); logi programu: `...\T11\robocze\dane\logi\`
  (stanowisko.log, silnik.log); podglady: `...\robocze\dane\podglady\`; pamiec puli: `...\robocze\dane\pula_cache\`.
- Folder eksportu: `...\T11\robocze\eksport\` (40 STL skan_0001 - skan_0040, ok. 1,9 GB); kopia projektow `...\T11\robocze\Cyrkon\`
  (kopia `<PC-katalog>\app\Prace_test`: 15 folderow, 17 STL - z natury zawiera nazwy folderow zlecen testowych).
- Plik ustawien testu: `...\T11\ustawienia.toml`.

## Lista dowodow (<ROB>)

Z listy planu: `t11_auto_uklad_podsumowanie.json`, `t11_skany.tsv`, `t11_zielone.tsv`, `t11_testy.log`, `t11_wynik.md`.
Dodatkowe: `WYNIK.md`, `t11_tabela.tsv`, `t11_liczniki.txt`, `t11_prawda.tsv`, `t11_skany_sha16.tsv`, `t11_zielone_prace.tsv`,
`t11_statusy.tsv`, `t11_zdarzenia.tsv`, `t11_wyniki_uklad.tsv`, `t11_komunikaty.txt`, `t11_symulator.json`, `t11_symulator.log`,
`t11_auto_uklad.log`, `t11_testy_instalacja.log`, `t11_testy_zrodlo_kodu.txt`, `kody.txt`, `czasy.txt`, `krok_A.cmd`,
`krok_B.cmd`, `krok_B_program.cmd`.
