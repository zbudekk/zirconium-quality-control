WERDYKT T0: ZAL z odstepstwem O1 (wydanie 0.3.3: kody instalacji 10 -> 0, program startuje 2 z 2, samokontrola ZIELONA kod 0 / bledy 0, sumy 1 z 1 + 227 z 227 + 147 z 147, pip tylko z kol paczki 73 z 73; UWAGA: pomylka wykonawcy 17:37:40 w katalogach nocy - sekcja nizej, do decyzji koordynatora)

# T0 - Czysta instalacja z paczki wydania 0.3.3 - WYNIK

Wykonawca: sesja testow koncowych f1 (tor 1), PC, konto `<konto-PC>`, 21.11.2026 17:36-17:45. Przedmiot: paczka
`<PC-katalog>\wydania\Stanowisko_0.3.3.zip` (447318667 bajtow, SHA-256 b6049229848afb124771944a3a3037664a0ec68aaeaa18a09da76f05103b1377,
commit 0fedbf6e4f97dc68b2f4679061a960ac81edbdbd). Plan: `<REPO>\Ramki\etap3\odbior_koncowy\PLAN_TESTOW.md` (`<REPO>` = `<PC-katalog>\t0\repo2`),
sekcja "T0 - Czysta instalacja" + "Ustalenia koordynatora"; sciezki wg `odbior2-final.md`.

Katalogi: swiezy `<PC-katalog>\t0\odbior2\` (przed testem nie istnial - sprawdzone 17:37:10); `<P1>` = `<PC-katalog>\t0\odbior2\paczka_0.3.3`;
`<K>` = `<PC-katalog>\t0\odbior2\Stanowisko`; foldery wejsciowe `<PC-katalog>\t0\odbior2\dane\{eksport,Cyrkon,Prywatne,millbox}`;
`<ROB>` = `<PC-katalog>\koordynator\robocze\odbior2\final\T0`. Punkt odniesienia: noc 20/21.11, wydanie 0.3.1
(`<PC-katalog>\koordynator\robocze\odbior\T0\WYNIK.md`).

## Kryterium (sekcja 7 planu etapu)

"Paczka wydania na czystym koncie PC, wg instrukcji, bez internetu - program startuje; samokontrola zielona; sumy SHA-256 zgodne."

| Czesc kryterium | Liczba (0.3.3) | Noc (0.3.1) | Dowod | Werdykt |
|---|---|---|---|---|
| (a) program startuje | 2 z 2 startow z kodem 0: `Stanowisko.cmd --atrapa --zamknij-po 5` kod 0 (6,4 s); `Stanowisko.cmd --zamknij-po 20` (prawdziwy kontroler) kod 0 (22,5 s); `Traceback` w `dane\logi\stanowisko.log`: 0 wierszy (log: 7 wierszy) | 2 z 2 (6,5 s / 22,5 s), 0 | `t0_start.txt`, `kody.txt` | ZAL |
| (b) samokontrola zielona | `Samokontrola.cmd --bez-sieci`: kod 0, `SAMOKONTROLA: ZIELONA (ok 17, ostrzezenia 4)`, bledy 0; pelna (`--json`): kod 0, ok 17 / ostrzezenia 4 / bledy 0, 21 sprawdzen | to samo (17 / 4 / 0, 21) | `t0_samokontrola.txt`, `t0_samokontrola.json` | ZAL |
| (c) sumy SHA-256 zgodne | ZIP: 1 z 1 (certutil = `.zip.sha256` = zlecenie = wiersz `SHA256SUMS_wydania.txt` z `main` 1f231d9); pliki paczki wg instalatora: "zgodne 227 z 227" (3 uruchomienia z 3); pliki programu wg samokontroli: 147 z 147, nadmiarowych 0 | 1 z 1; 210 z 210; 130 z 130 | `t0_sha256.txt`, `t0_2.log`, `t0_zainstaluj_1.log`, `t0_zainstaluj_2.log` | ZAL |
| (d) "bez internetu" (odstepstwo O1) | `pip.log`: 2 wiersze z 2 (`Ignoring indexes: https://pypi.org/simple`, `Looking in links: <PC-katalog>\t0\odbior2\paczka_0.3.3\kola`); dziennik instalacji: wiersz "instalacja 73 pakietow z kol paczki (bez sieci)"; pakiety "73 z 73"; w `pip.log` 0 wierszy `Downloading` i 1 wiersz z `http` (ten sam `Ignoring indexes`) | to samo (73 z 73) | `t0_pip_bez_sieci.txt` | ZAL z odstepstwem O1 |
| "czyste konto PC" (odstepstwo O1) | swiezy katalog na koncie `<konto-PC>`, nie nowe konto Windows; sieci fizycznie nie odcinano | to samo | ten plik | ZAL z odstepstwem O1 |
| "wg instrukcji" | 9 krokow instalatora; pierwsza instalacja kod 10 `WSTRZYMANA`, po uzupelnieniu `ustawienia.toml` kod 0 `GOTOWA` | to samo (10 -> 0) | `t0_zainstaluj_1.log`, `t0_zainstaluj_2.log` | ZAL |

Calosc: **ZAL z odstepstwem O1** (O1 = przyjeta interpretacja "czystego konta" i "bez internetu" z `RAPORT.md` 4a; nowych odstepstw od
kryterium brak). Pelne T0 na czystym komputerze (laptop stanowiska) = poza tym testem (`ODLOZONE.md`, D4).

## Liczby instalatora do dokumentow (wydanie 0.3.3)

| Liczba | Wartosc 0.3.3 | Noc 0.3.1 | Zrodlo |
|---|---|---|---|
| Rozmiar ZIP | 447318667 bajtow | 444935199 | `ls`, zlecenie |
| Pliki rozpakowanej paczki | 228 plikow, 472631490 bajtow (450,7 MB): `kola\` 73, `kola_testy\` 3, `program\` 148, `CZYTAJ.txt`, `SHA256SUMS`, `wydanie.json`, `zainstaluj.cmd` | 211 plikow, 462922182 bajtow | zliczenie `find -type f` po rozpakowaniu |
| Sumy paczki wg instalatora | **zgodne 227 z 227** (`SHA256SUMS`: 227 wierszy = 228 plikow bez samego `SHA256SUMS`) | 210 z 210 | `t0_zainstaluj_1.log` wiersz 2 |
| Pliki programu | **"program: skopiowano 148 plikow, sumy zgodne"**; `wydanie.json`: `pliki_programu` 148; w `<K>\wersje\0.3.3\program` 148 plikow, 34630685 bajtow (33,0 MB) | 131 | `t0_zainstaluj_1.log`, zliczenie |
| Sumy programu wg samokontroli | **zgodne 147 z 147**, plikow nadmiarowych 0 (148 = 147 + `SUMY_PROGRAMU.sha256`) | 130 z 130 | `t0_samokontrola.txt` |
| Pakiety pip | 73 z 73 z kol paczki; po `/testy` 76 z 76 (3 pakiety zestawu testowego) | 73 z 73; 76 z 76 | logi instalacji |
| Uklady plytek | **"uklady plytek z [plytki]: poprawne 10 z 10 (uklad.json i modele plytka_n*.stl)"** | 8 z 8 | `t0_samokontrola.txt` |
| `modele_plytek` w instalacji | **38 plikow** | - (nie liczono) | zliczenie w `<K>\wersje\0.3.3\program\modele_plytek` |
| `ramka\rpi` w instalacji | **4 pliki**: `ramka.json.wzor`, `ramka.service`, `sprawdz_ramke.sh`, `zainstaluj_ramke.sh` | - | zliczenie w `<K>\wersje\0.3.3\program\ramka\rpi` |
| Skroty w `<K>` | **6**: `Dzien_skanera.cmd`, `Polecenie.cmd`, `Samokontrola.cmd`, `Stanowisko.cmd`, `Wersje.cmd`, `Wroc_do_poprzedniej.cmd` | 5 (bez `Dzien_skanera.cmd`) | `ls <K>\*.cmd` |
| Czas instalacji | pierwsza **60,5 s** (kod 10; w tym pip 45,5 s wg `pip.log` 17:38:50,9-17:39:36,4); druga **3,2 s** (kod 0); z `/testy` **5,9 s** (kod 0). Od startu pierwszej do `GOTOWA`, z reczna edycja ustawien: 1 min 41 s (17:38:41-17:40:22) | 65,5 s / 3,3 s / 6,2 s | `t0_3_czas.txt`, `t0_5_czas.txt`, `..\T1\t1_1_czas.txt` |
| Rozmiar katalogu instalacji `<K>` | **1392554923 bajtow (1328,0 MB), 25552 pliki** - zmierzone 17:47, po `/testy` (76 pakietow) i po 2 startach programu; w tym `wersje\0.3.3\venv` 1357729701 bajtow (1294,8 MB, 25384 pliki), `program` 33,0 MB, `dane` 87210 bajtow (6 plikow) | nie mierzono | zliczenie `find -type f` (suma rozmiarow plikow, nie miejsce zajete na dysku) |
| Szacunek instalatora | "miejsce na dysku: potrzeba ok. 1869 MB, wolne 35517 MB" | "ok. 1860 MB, wolne 64580 MB" | `t0_zainstaluj_1.log` |

## Kody i czasy instalacji

| Instalacja | Godzina | Kod | Czas | Wiersz koncowy |
|---|---|---|---|---|
| pierwsza (krok 3) | 17:38:41 | 10 | 60,5 s | `INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom zainstaluj.cmd ponownie (kod 10)` |
| po uzupelnieniu ustawien (krok 5) | 17:40:19 | 0 | 3,2 s | `INSTALACJA: GOTOWA - wersja biezaca 0.3.3 (poprzednia: brak). Uruchamianie: <PC-katalog>\t0\odbior2\Stanowisko\Stanowisko.cmd` |
| z `/testy` (T1 krok 1, zaraz po T0) | 17:44:26 | 0 | 5,9 s | `INSTALACJA: GOTOWA - wersja biezaca 0.3.3 (poprzednia: brak). ...`; "zestaw testowy (pytest): 3 pakietow", "pakiety zgodne z lista zamrozona: 76 z 76" |

Wpisy `ciezkie.log`: `17:38:41 START f1 tor 1 | RAM 71760 MB` / `17:39:42 KONIEC f1 tor 1 | kod 10`; `17:40:19 START` / `17:40:22 KONIEC ... kod 0`;
`17:44:26 START` / `17:44:32 KONIEC ... kod 0` (krok `/testy`).
Co jeszcze liczylo na PC (z `ciezkie.log`): w czasie krokow 3 i 5 w torze 2 biegl T2 (`f2`, START 17:38:20, sterownik wieczoru z analiza);
tory 3 i 4 wolne; wolny RAM przed krokiem 1: 72652 MB z 95652. Procesow `python` innych wykonawcow nie liczono w tej minucie.

Samokontrola: `SAMOKONTROLA: ZIELONA (ok 17, ostrzezenia 4)` (kod 0). Ostrzezenia (4): `baza` (brak pliku bazy przed pierwszym startem -
powstala w kroku 7b), `ramka_wieczorna`, `ramka_poranna` (bez ramek w sieci), `excel` (Excel nie jest uruchomiony).
Po kroku `/testy` (baza juz istnieje): `SAMOKONTROLA: ZIELONA (ok 18, ostrzezenia 3)`.

Pelna tabela krokow (polecenie / kod / czas / wynik): `t0_kroki.md`.

## Kontrola zestawu T14 na instalacji (zaraz po T0 i `/testy`)

`call <K>\Polecenie.cmd <PC-katalog>\t0\repo2\Ramki\etap3\t14\symulator_t14.py --sprawdz --program . < NUL > <ROB>\t14_sprawdz_paczka.txt 2>&1`
(plik `..\T1\krok_t14.cmd`), 17:44:32-17:44:40 (8,4 s), kod 0, ostatni wiersz: `SPRAWDZENIE T14 BEZ EKRANU: zgodne 22 z 22 krokow`
(noc: 22 z 22). Dowod: `t14_sprawdz_paczka.txt`, `t14_czas.txt`.

## Znak gotowosci

`GOTOWE.txt` zapisany **17:44:53** (po kroku `/testy`, kontroli `_wmi` -> `None` i kontroli T14). Po tym pliku wykonawca T0 niczego w
`<K>` nie zmienia (uzywa jej tylko do uruchamiania: T1 przez `<K>\Polecenie.cmd`).

## Pomylka wykonawcy 17:37:40 (NOWE - nie jest wynikiem testu; do decyzji koordynatora)

Pierwsza wersja pliku `krok_3.cmd` powstala przez skopiowanie pliku nocy z zamiana sciezek poleceniem `sed`; zamiana NIE zadzialala
(podwojny ukosnik wsteczny we wzorcu zostal po drodze zredukowany do pojedynczego), a wykonawca uruchomil plik przed sprawdzeniem tresci.
Plik mial wiec sciezki NOCY i o 17:37:40-17:37:44 (przez `ciezki.ps1`, tor 1, wpis `START f1 ... kod 0` w `ciezkie.log`) wykonal:
`<PC-katalog>\t0\odbior\paczka_0.3.1\zainstaluj.cmd /katalog <PC-katalog>\t0\odbior\Stanowisko /python %PY% /bez-sieci /bez-pauzy`.
Skutki (sprawdzone 17:38-17:39, tylko odczyt):

1. Instalacja nocy `<PC-katalog>\t0\odbior\Stanowisko` (miala byc nietykana): instalator 0.3.1 uruchomiony ponownie na tej samej wersji -
   "wersja 0.3.1 jest juz zainstalowana i zgodna z paczka - pliki bez zmian", `ustawienia.toml` bez zmian (SHA-256 4303ec76c74fb4a2... jak w nocy),
   samokontrola ZIELONA (ok 18, ostrzezenia 3), kod 0. Zmienione pliki: `dziennik_instalacji.txt` (dopisane 15 wierszy 17:37:41-17:37:44);
   zmieniona data katalogu `dane` (plik blokady instalatora). Program, srodowisko wersji, baza: innych plikow z data po 17:00 nie znaleziono
   (`find -newermt`, poza `venv\Lib`).
2. Katalog dowodow nocy `<PC-katalog>\koordynator\robocze\odbior\T0\`: NADPISANE 2 pliki - `t0_zainstaluj_1.log` (bylo 6192 bajty, jest
   3584) i `t0_3_czas.txt` (bylo 80, jest 79); do `kody.txt` DOPISANY 1 wiersz `krok3_zainstaluj_1 KOD=0` (308 -> 335 bajtow).
   Tresc pierwotna tych 3 plikow jest w repo: `<PC-katalog>\qc\Ramki\etap3\odbior_koncowy\dowody\T0\` (wersje po `dowody_lf.py`, LF:
   6146 B + 46 wierszy = 6192, 78 + 2 = 80, 298 + 10 = 308 - rozmiary zgodne z oryginalami CRLF).
3. Paczki 0.3.3, katalogu `<PC-katalog>\t0\odbior2` i wynikow T0 / T1 pomylka nie dotyczy (`<K>` powstal dopiero 17:38:41).

Wykonawca NICZEGO w katalogach nocy nie naprawial (zlecenie: tylko odczyt) - stan po pomylce zostal. Kopia 3 plikow w stanie po pomylce:
`robocze\pomylka_1737\`. Mozliwa naprawa (decyzja koordynatora): odtworzyc 3 pliki z `dowody\T0\` w repo (z zamiana LF -> CRLF daja
rozmiary oryginalow); 15 wierszy dziennika instalacji nocy zostaje jako slad. Od tego miejsca kazdy plik `.cmd` byl przed uruchomieniem
sprawdzany na stare sciezki (`grep`: 0 trafien) - wpisy w tym pliku i w `..\T1\WYNIK.md`.

## Polecenia planu zmienione / potkniecia (to tez jest wynik)

1. Krok 2, rozpakowanie: zamiast `Expand-Archive` z planu uzyto `C:\Windows\System32\tar.exe -xf <ZIP_N> -C <P1>` (ustalenie koordynatora
   w `odbior2-final.md`; 0,7 s, 228 plikow, kod 0).
2. Krok 2: w `<REPO>` (commit wydania 0fedbf6) plik `SHA256SUMS_wydania.txt` NIE ma wiersza 0.3.3 - wiersz jest w `main` (1f231d9);
   porownanie z plikiem w `<PC-katalog>\qc` (tylko odczyt). To samo co w nocy dla 0.3.1.
3. Kroki 7c i 9c (`find /c ...`): plik `krok_6_9.cmd` byl uruchomiony z sesji Git Bash, w ktorej `find` to program z Git, nie
   `C:\Windows\System32\find.exe`. Zamiast liczby wierszy wypisal liste plikow dysku C do `t0_start.txt` (130 MB) i `t0_pip_bez_sieci.txt`
   (261 MB) i trwal 2 min 13 s. Oba pliki przyciete do wierszy sprzed `find` (lista plikow dysku usunieta - nie jest dowodem i zawiera nazwy
   plikow spoza testu), a zliczenia powtorzone plikiem `krok_7c_9c.cmd` z pelna sciezka `C:\Windows\System32\find.exe` (17:44:25): Traceback 0,
   Downloading 0, http 1. W `kody.txt` wiersze `krok7c_find_traceback KOD=1` i `krok9c_find_downloading KOD=1` sa z nieudanej proby (kod
   programu z Git) - wazne sa wiersze `..._powtorka`. Startow programu (7a, 7b), krokow 6, 8, 9a, 9b NIE powtarzano - ich wyniki sa z
   pierwszego wykonania. Kopia listy plikow dysku zostala tez w pliku wynikow narzedzia sesji wykonawcy (poza katalogiem dowodow:
   `C:\Users\<konto-PC>\.claude\projects\C--<konto-PC>-qc\...\tool-results\bq01c5snd.txt`, 64 MB) - do usuniecia przez koordynatora.
4. Kroki 3, 4, 5 i plik `krok_6_9.cmd` uruchomione z sesji Git Bash (zmienna `PATH` z katalogami Git na poczatku); od 17:44:25 (kroki
   7c / 9c powtorka, `/testy`, T14, caly T1) z sesji PowerShell. Wplywu na instalacje nie widac (sumy 227 z 227, pip z kol paczki 73 z 73,
   samokontrola ZIELONA takze w uruchomieniu `/testy` z PowerShell), ale nie bylo to mierzone osobno.
5. Krok 4: `robocopy ... /E` z dodatkowymi `/NFL /NDL /NJH /NP` (bez nazw folderow i plikow zlecen w dowodzie) - jak w nocy. Kod 1
   robocopy = pliki skopiowane, bez bledow. W `ustawienia.toml` zmieniono tylko wartosci 5 kluczy (komentarze w wierszach zostaly).
6. Nazwy logow instalacji jak w nocy: `t0_zainstaluj_1.log`, `t0_zainstaluj_2.log` (lista "Dowody"), nie `t0_3.log`, `t0_5.log`.
7. Krok 6b: stderr `Samokontrola.cmd --json` do osobnego pliku `t0_samokontrola_json_stderr.txt` (0 bajtow) - jak w nocy.

## Czego T0 nie sprawdza (jak w nocy)

Dwuklik w Eksploratorze i pauza na koncu (uzyto `/bez-pauzy`), opcja `/skrot`, samodzielne szukanie Pythona (na tym PC `/python` jest
obowiazkowe), instalacja Pythona z python.org, `Dzien_skanera.cmd` (sprawdzono tylko, ze skrot powstal - nie byl uruchamiany).

## Uwagi o srodowisku (opis, nie wynik testu)

- Srodowisko wersji odciete od pakietow Pythona bazowego: `<K>\wersje\0.3.3\venv\pyvenv.cfg`: `include-system-site-packages = false`.
- Zjawisk `0xC0000142` / `0xc000070a` / `0xC0000409` w T0 nie bylo.
- Dysk C: przed T0 36 GB wolne (17:36), po T0 i starcie T1 32 GB (17:47; w tym czasie instalowaly tez inne testy).
- Procesy: przed T0 (17:37) na PC byl tylko proces `python` PID 12560 (znany, niczyj). Po krokach T0 osobnej listy nie zapisano -
  pierwsza lista po T0 jest z 17:46:02 (`..\T1\t1_co_liczylo.txt`), juz w czasie przebiegow T1 (procesy pytest wykonawcy); stan koncowy
  procesow: `..\T1\WYNIK.md`.

## Do decyzji koordynatora / wlasciciela

- **Pomylka 17:37:40** (sekcja wyzej): czy odtworzyc 3 pliki dowodow nocy z repo; czy 15 dopisanych wierszy w dzienniku instalacji nocy
  wymaga adnotacji w dokumentach.
- O1: "czyste konto" = swiezy katalog, siec nieodcieta - jak w `RAPORT.md` 4a pozycja 16.
- Plan, krok 2 i krok 7 / 9: polecenia `Expand-Archive` i `find /c` zaleza od sesji wykonawcy (PowerShell 7, Git Bash) - w planie warto
  wpisac pelne sciezki `C:\Windows\System32\tar.exe` i `C:\Windows\System32\find.exe`.
- Plik wynikow narzedzia z lista plikow dysku (potkniecie 3) - do usuniecia.
