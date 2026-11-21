WERDYKT T1: ZAL z odstepstwem NOWE (oba przebiegi: 2506 passed / 9 skipped / 0 failed / 0 errors = 2515 z --collect-only; pominiete 9 z 9 znanych, spoza listy 0; kody wyjscia PO wierszu podsumowania: srodowisko wersji 0xC0000005 - NOWE, bazowy 0xC0000409 - znane); T13: ZAL z odstepstwem O11 i O10 (naruszen 0)

# T1 - Testy programu (pelny pytest) na wydaniu 0.3.3 - WYNIK

Wykonawca: sesja testow koncowych f1, PC, konto `<konto-PC>`, 21.11.2026 od 17:44. Plan: `PLAN_TESTOW.md`, sekcja "T1 - Testy programu".
`<K>` = `<PC-katalog>\t0\odbior2\Stanowisko` (wersja 0.3.3 z paczki, po `/testy`: 76 pakietow), `<REPO>` = `<PC-katalog>\t0\repo2`
(detached 0fedbf6e4f97dc68b2f4679061a960ac81edbdbd = commit paczki), `<ST>` = `<REPO>\Ramki\stanowisko`, `<P1>` = `<PC-katalog>\t0\odbior2\paczka_0.3.3`,
`<ROB>` = `<PC-katalog>\koordynator\robocze\odbior2\final\T1`, `PY` = `<PC>\AppData\Local\Programs\Python\Python312\python.exe`.

**Kryterium (plan):** pytest caly - 0 failed, 0 errors; pominiete tylko znane z punktu odniesienia.

## Kroki 1-3 i --collect-only (wykonane)

| Krok | Godzina | Polecenie | Kod | Wynik | Dowod |
|---|---|---|---|---|---|
| 1 | 17:44:26 | przez `ciezki.ps1 -Tor 1 -Kto f1` plik `krok_1_3.cmd`: `call <P1>\zainstaluj.cmd /katalog <K> /python %PY% /bez-sieci /bez-pauzy /testy < NUL > <ROB>\t1_zainstaluj_testy.log 2>&1` | **0** | 5,9 s; "dokladam zestaw testowy", "zestaw testowy (pytest): 3 pakietow", "pakiety zgodne z lista zamrozona: 76 z 76", `SAMOKONTROLA: ZIELONA (ok 18, ostrzezenia 3)`, `INSTALACJA: GOTOWA - wersja biezaca 0.3.3 (poprzednia: brak)` | `t1_zainstaluj_testy.log`, `t1_1_czas.txt`, `kody.txt` |
| 3 | 17:44:32 | `call <K>\Polecenie.cmd -c "import stanowisko, sys; print(sys.modules.get('_wmi', 'brak'))" < NUL` | 0 | `None` | `t1_3_wmi.log` |
| 2a | 17:45:33 | `git -C <REPO> config --get core.autocrlf` | 0 | `false` | `t1_2_repo.txt` |
| 2b | 17:45:33 | `git -C <REPO> status --short` | 0 | puste (0 wierszy); `rev-parse HEAD` = 0fedbf6e4f97dc68b2f4679061a960ac81edbdbd | `t1_2_repo.txt` |
| 2c | 17:45:33 | `copy <ST>\ustawienia.przyklad.toml <ST>\ustawienia.toml` (przed krokiem pliku nie bylo: `BRAK`) | 0 | "1 file(s) copied."; `git status --short` po kopii nadal puste (plik ignorowany) | `t1_2_repo.txt` |
| collect (wersja) | 17:45:34 | `call <K>\Polecenie.cmd -m pytest <ST>\testy -q --collect-only -p no:cacheprovider --rootdir <ST> < NUL` | 0 | `2515 tests collected in 7.91s` | `t1_collect.txt` |
| collect (bazowy) | 17:45:43 | `cd /d <ST>` i `call <PC-katalog>\koordynator\narz\py.cmd -m pytest -q --collect-only -p no:cacheprovider < NUL` | 0 | `2515 tests collected in 5.28s`; roznic w listach identyfikatorow obu interpreterow: 0 | `t1_collect.txt` |

Kolejnosc: krok 3 zaraz po kroku 1 (przed krokiem 2), bo od krokow 1 + 3 i kontroli T14 zalezal znak `..\T0\GOTOWE.txt` (zapisany 17:44:53).
Liczba oczekiwana: **2515** testow w 59 plikach `testy\test_*.py` (punkt odniesienia koordynatora: 2506 passed + 9 skipped = 2515;
noc, wydanie 0.3.1: 2222 = 2213 + 9).

## Punkt odniesienia dla pominietych (lista 9 znanych - jak w nocy)

| Nr | Plik:wiersz | Ile | Powod |
|---|---|---|---|
| 1 | `test_aplikacja.py:1142` | 1 | wariant na duzych skanach odniesienia: ustaw E3A3_DANE_REF ... i E3A3_PROJEKTY |
| 2 | `test_katalog.py:133` | 1 | brak folderu projektow z pulpitu |
| 3-6 | `test_silnik.py:1981` | 4 | wariant na duzych skanach odniesienia: ustaw E3A2_DANE_REF ... i E3A2_PROJEKTY |
| 7 | `test_silnik.py:1988` | 1 | wariant na duzych skanach odniesienia: ustaw E3A2_DANE_REF ... i E3A2_PROJEKTY |
| 8 | `test_ui.py:67` | 1 | P3a: okno jest szkicem - watek silnika nie konczy sie pod offscreen; naprawa w P3a-2 |
| 9 | `test_ui.py:129` | 1 | brak dane/syntetyczne_P2 albo projektow z pulpitu |

Zrodla listy: `<PC-katalog>\koordynator\robocze\odbior\T1\t1_pominiete.txt` (noc, 571e186, oba przebiegi) i log koordynatora z `-rs`
`<PC-katalog>\koordynator\robocze\koord\pytest_o2_7ebb5cd.log` (21.11, `2496 passed, 9 skipped`; te same 6 wierszy `SKIPPED` = 9 testow).

## Przebiegi (uzupelniane po kazdym)

Oba przebiegi ida jako procesy odlaczone (`kolejka_t1.ps1 -Przebieg <n> -Tor <t> -Krok <plik>`, `Start-Process -WindowStyle Hidden` z sesji
PowerShell), kazdy przez `powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor <t> -Kto f1
-Polecenie "<ROB>\krok_<n>.cmd"`; dziennik: `t1_kolejka.log`; godziny i kody: `t1_czasy.txt`, `kody.txt`; "co jeszcze liczylo" co 120 s:
`t1_co_liczylo.txt` (wolny RAM, liczba procesow `python` wg katalogu, zajete tory blokady). ROWNOLEGLE (inaczej niz w nocy, gdzie szly
po kolei w torze 1): przebieg 1 w torze 1, przebieg 2 w torze 3 - zgodnie ze zleceniem ("jesli tor 3 jest wolny, oba przebiegi moga isc
rownolegle"; tor 3 byl wolny o 17:45:50).

- Przebieg 1 (krok 4, interpreter srodowiska wersji, tor 1), plik `krok_4.cmd`:
  `call <K>\Polecenie.cmd -X faulthandler -m pytest <ST>\testy -q -rs -p no:cacheprovider --rootdir <ST> -o faulthandler_timeout=900 < NUL > <ROB>\t1_pytest.log 2>&1`
  START 17:46:00,37 (`ciezkie.log`: `17:46:00 START f1 tor 1 | RAM 69652 MB`). KONIEC 18:23:30,35.
  **Wiersz podsumowania: `2506 passed, 9 skipped, 1 warning in 2246.86s (0:37:26)`. Kod wyjscia (osobno): -1073741819 = 0xC0000005**
  (`kody.txt`: `krok4_pytest_wersja KOD=-1073741819`; `ciezkie.log`: `18:23:30 KONIEC f1 tor 1 | kod -1073741819`). failed 0, errors 0.
  Znaki postepu w logu: 2515 = 2506 kropek + 9 `s` + 0 `F` + 0 `E`; suma 2506 + 9 + 0 = 2515 = `--collect-only`. Wierszy z `failed` /
  `Traceback` / `Timeout (` w logu: 0. PO wierszu podsumowania log ma jeszcze 12 wierszy: `Fatal Python error: Aborted`, `Current thread
  0x000012a8 (most recent call first): <no Python frame>`, lista modulow rozszerzen, 2 x `QThreadStorage: entry <n> destroyed before end of
  thread`, `Windows fatal exception: access violation`, `<no Python frame>` - czyli proces padl przy zamykaniu interpretera, po zakonczeniu
  i podsumowaniu wszystkich testow (tekst wypisuje `-X faulthandler` z polecenia planu). **NOWE: kod 0xC0000005 (naruszenie dostepu), nie
  znany z planu 0xC0000409** - plan mowi o ocenie po wierszu podsumowania tylko dla 0xC0000409; tu przyjeto te sama zasade (wynik testow z
  wiersza podsumowania, kod osobno) i oznaczono jako odstepstwo NOWE do decyzji koordynatora. W nocy (0.3.1) ten sam przebieg dal kod 0.
  1 ostrzezenie: `UserWarning` w `test_auto_uklad.py::test_numer_spoza_rozpoznanej_rodziny_jest_pomijany` (jak w nocy).
  Pominiete: 6 wierszy `SKIPPED` = 9 testow, te same pliki:wiersze, liczby i powody co lista odniesienia; pozycje `s`: 29, 730, 2115-2119,
  2191, 2192 (uklad 1 + 1 + 5 + 2). Spoza listy 9 znanych: 0. Szczegoly: `t1_pominiete.txt`.
  Czas 37 min 26 s (noc: 29 min 33 s przy 2222 testach, przebiegi po kolei). **Przebieg 1: 0 failed, 0 errors.**
- Przebieg 2 (krok 5, interpreter bazowy, tor 3), plik `krok_5.cmd`:
  `cd /d <ST>` i `call <PC-katalog>\koordynator\narz\py.cmd -m pytest -q -p no:cacheprovider -rs < NUL > <ROB>\t1_pytest_bazowy.log 2>&1`
  START 17:45:58,55 (`ciezkie.log`: `17:45:58 START f1 tor 3 | RAM 69834 MB`). KONIEC 18:23:07,68.
  **Wiersz podsumowania: `2506 passed, 9 skipped, 1 warning in 2225.26s (0:37:05)`. Kod wyjscia (osobno): -1073740791 = 0xC0000409**
  (`kody.txt`: `krok5_pytest_bazowy KOD=-1073740791`; `ciezkie.log`: `18:23:07 KONIEC f1 tor 3 | kod -1073740791`) - znane zjawisko PC:
  kod PO wierszu podsumowania, log konczy sie wierszem podsumowania (0 wierszy po nim). failed 0, errors 0.
  Znaki postepu: 2515 = 2506 kropek + 9 `s` + 0 `F` + 0 `E`; suma = 2515 = `--collect-only`. Wierszy z `failed` / `error` / `Fatal Python` /
  `Traceback` w logu: 0. To samo 1 ostrzezenie co w przebiegu 1. Pominiete: te same 6 wierszy `SKIPPED` = 9 testow na tych samych
  pozycjach (29, 730, 2115-2119, 2191, 2192); spoza listy 9 znanych: 0.
  Czas 37 min 5 s (noc: 25 min 54 s przy 2222 testach; koordynator na drzewie 7ebb5cd, 2505 testow: 34 min 50 s).
  **Przebieg 2: 0 failed, 0 errors. Liczby zgodne co do sztuki z punktem odniesienia 2506 / 9 / 0.**

Co jeszcze liczylo w czasie obu przebiegow (17:46-18:23; `ciezkie.log` i `t1_co_liczylo.txt`): oba przebiegi T1 nawzajem (tory 1 i 3);
T2 tor 2 (`f2`, do 17:47:58); T12 tor 2 (`f2`: `krok_A` 17:48:14-17:53:23, `krok_Z` 17:53:24-17:57:22, `krok_B` 17:57:23-17:59:30,
`krok_B2` 18:00:21-18:03:29 - instalacje i aktualizacje); T11 tor 4 (`f3-t11`, od 17:48:30, w chwili konca T1 nadal w toku); T10 tor 3
(`f3-t10`) wystartowal dopiero 18:23:31, po zwolnieniu toru 3 przez przebieg 2. Procesow `python` na PC 5-11, wolny RAM 59,2-69,4 GB.

Testy nieudane: brak w obu przebiegach, wiec regula "powtorz test osobno 5 razy" nie miala zastosowania - zadnej powtorki nie wykonano;
kazdy przebieg wykonany 1 raz (1 proba = 1 wynik). `test_silnik.py::test_pamiec_linii_na_dysku` (znany niestabilny): passed w obu
przebiegach. Testy czasowe (`test_ramka::test_k4`, `test_ui_wieczor::test_6`, `test_aplikacja::test_f`, klasa `Petla`): 0 nieudanych pod
obciazeniem (2 pelne przebiegi naraz + T11 + T12).

W plikach `krok_4.cmd` / `krok_5.cmd` na poczatku `set QT_QPA_PLATFORM=offscreen` (zasada planu); liczby watkow (`OMP_NUM_THREADS` itd.)
w przebiegu 1 NIE ustawiano - polecenie planu doslownie (`Polecenie.cmd` ich nie ustawia); w przebiegu 2 ustawia je `py.cmd` (2 watki).

## Werdykt czesci kryterium

| Czesc kryterium | Przebieg 1 (srodowisko wersji) | Przebieg 2 (bazowy) | Werdykt |
|---|---|---|---|
| 0 failed | 0 (wiersz podsumowania bez `failed`; 0 znakow `F`) | 0 | ZAL |
| 0 errors | 0 (wiersz podsumowania bez `error`; 0 znakow `E`) | 0 | ZAL |
| pominiete tylko znane z punktu odniesienia | 9 z 9 znanych, spoza listy 0 | 9 z 9 znanych, spoza listy 0 | ZAL |
| suma = `--collect-only` | 2506 + 9 + 0 = 2515 | 2506 + 9 + 0 = 2515 | zgodne |
| liczby wobec punktu odniesienia 2506 / 9 / 0 | 2506 / 9 / 0 | 2506 / 9 / 0 | zgodne |
| kod wyjscia procesu (osobno) | 0xC0000005 PO wierszu podsumowania - **NOWE** | 0xC0000409 PO wierszu podsumowania - znane zjawisko | uwaga / odstepstwo NOWE |

**Calosc T1: ZAL z odstepstwem NOWE** - kryterium (0 failed, 0 errors, pominiete tylko znane) spelnione w obu przebiegach wg wiersza
podsumowania; odstepstwo = kod wyjscia przebiegu 1 (0xC0000005) nie jest kodem opisanym w planie jako znane zjawisko. Wariant ostrozniejszy
przyjety przez wykonawce (plan nie ma reguly dla tego kodu); gdy koordynator uzna go za to samo zjawisko zamykania interpretera z Qt co
0xC0000409 - T1 = ZAL. Zestawienie: `t1_wynik.md`; pominiete: `t1_pominiete.txt`; liczba testow: `t1_collect.txt`.

## Polecenia planu zmienione / potkniecia

1. Polecenia krokow 1, 3, 4, 5 i `--collect-only` wykonane doslownie, w plikach `.cmd` z `call`, `< NUL` i `set QT_QPA_PLATFORM=offscreen`.
   Krok 5: zamiast `cmd /c "cd /d <ST> && ...py.cmd ..."` w pliku `krok_5.cmd` jest `cd /d %ST%` i `call ...py.cmd ...` (jak w nocy).
2. Kolejnosc: krok 3 (`_wmi`) przed krokiem 2 (kontrola `<REPO>`) - oba przed przebiegami; powod: znak `GOTOWE.txt`.
3. Przebiegi 1 i 2 ROWNOLEGLE (tor 1 i tor 3) zamiast po kolei w torze 1 ("ta sama blokada" w planie) - wg zlecenia koordynatora.
   Skutek: czasy o ok. 8-11 min dluzsze niz w nocy i T10 czekal na tor 3 do 18:23:31.
4. `--collect-only` interpreterem bazowym: `cd /d <ST>` i `py.cmd -m pytest -q --collect-only -p no:cacheprovider` (jak w nocy).
5. Wszystkie pliki `.cmd` T1 uruchomione z sesji PowerShell (nie z Git Bash - patrz `..\T0\WYNIK.md`, potkniecia 3 i 4); przed
   uruchomieniem kazdy sprawdzony na stare sciezki nocy (0 trafien).

## Stan po tescie

- `<REPO>`: `git status --short` puste (18:24), `HEAD` = 0fedbf6; pozycje IGNOROWANE przez git: `Ramki/stanowisko/ustawienia.toml`
  (zalozony w kroku 2 - zostawiony) i `Ramki/stanowisko/ramka/__pycache__/` (powstal w czasie przebiegow; w nocy tak samo). Nic nie usuwano.
- `<K>`: po `GOTOWE.txt` uzywana tylko do uruchamiania (`Polecenie.cmd` w przebiegu 1 i `--collect-only`).
- Katalogi tymczasowe pytest obu przebiegow (`%TEMP%\pytest-of-<konto-PC>\pytest-2136` i `pytest-2137`, utworzone 17:46:05 i 17:46:07,
  razem 5,9 GB) usuniete przez wykonawce 18:27 po zebraniu wynikow - dysk C mial 12,0 GB wolnego (18:25), po usunieciu 17,7 GB (18:27).
  Katalog `pytest-2138` (utworzony 17:46:32, 432 MB, ostatni zapis 17:49:41) zostawiony - nie ustalono, czyj.
- Procesy (18:24): procesy pytest wykonawcy zakonczone. Na PC zostaly: PID 12560 (znany, niczyj), PID 6308 i 15796 (start 17:53, T11 -
  rodzic `cmd` toru 4), PID 36496 (start 18:23:31, T10) oraz NOWY PID 34952: `python`, 0 watkow, 0 uchwytow, bez sciezki i rodzica -
  pojawil sie miedzy 18:22:05 a 18:24:00 (w `t1_co_liczylo.txt` do 18:22:05 jest 1 proces "bez-sciezki", o 18:24 sa 2), czyli w chwili,
  gdy oba procesy pytest wykonawcy konczyly sie kodami awarii i startowal T10. Najpewniej pozostalosc po jednym z procesow pytest T1
  (proces-wydmuszka), ale pochodzenia NIE potwierdzono - wykonawca go nie zabijal (zasada: cudzych nie zabijac). Do decyzji koordynatora.

## Do decyzji koordynatora / wlasciciela

- **Kod wyjscia 0xC0000005 przebiegu 1** (srodowisko wersji, `-X faulthandler`, po wierszu podsumowania): czy uznac za to samo zjawisko co
  0xC0000409 (wtedy T1 = ZAL), czy zlecic powtorke przebiegu 1 przy mniejszym obciazeniu PC (ok. 30 min, tor 1, plik `krok_4.cmd`).
- Proces `python` PID 34952 (0 watkow) - patrz "Stan po tescie".
- T13: odstepstwo dla 10 kopii bajtowych R58 ("decyzja wlasciciela nr 1 z 21.11.2026") nie ma numeru O<n> w `RAPORT.md` 4a commita wydania.
- Pomylka wykonawcy z 17:37:40 w katalogach nocy - opis w `..\T0\WYNIK.md`.

## T13 - Higiena repo na commicie wydania 0fedbf6 (dodatkowo, lekkie)

**WERDYKT T13 (pierwszy przebieg na commicie wydania 0.3.3): ZAL z odstepstwem O11 i O10 (naruszen 0; 7 plikow napisow ekranu nie-ASCII z 7 na
liscie; 10 kopii bajtowych R58 z 10 na liscie - "decyzja wlasciciela nr 1 z 21.11.2026"; kontrola na poziomie katalogow paczek)**

Godzina 17:46:35-17:46:37, krok lekki bez blokady, plik `krok_T13.cmd`; `<REPO>` tylko do odczytu: `git status --short` po T13 puste,
`HEAD` = 0fedbf6e4f97dc68b2f4679061a960ac81edbdbd (`t13_repo_stan.txt`). `<ODB>` = `<REPO>\Ramki\etap3\odbior_koncowy`.

| Polecenie | Kod | Czas | Wynik |
|---|---|---|---|
| `PY -I <ODB>\narzedzia\t13_higiena.py --repo <REPO> --od 2537f6f --do 0fedbf6e4f97dc68b2f4679061a960ac81edbdbd --json <ROB>\t13_wynik.json > <ROB>\t13_wynik.txt` (stderr osobno: 0 bajtow) | **0** | 1,5 s | `NARUSZENIA (grupa E3 i sciezki poza listami): 0`; ostatni wiersz: `WYNIK T13: ZAL z odstepstwem O11 (0 naruszen; 7 plikow napisow ekranu nie-ASCII; 10 kopii bajtowych R58 - decyzja wlasciciela nr 1 z 21.11.2026)` |
| `git -C <REPO> diff --stat 2537f6f 0fedbf6e4f97dc68b2f4679061a960ac81edbdbd > <ROB>\t13_diff_stat.txt` | 0 | - | `1129 files changed, 248681 insertions(+), 1285 deletions(-)` |
| `git -C <REPO> merge-base --is-ancestor 2537f6f 0fedbf6e4f97dc68b2f4679061a960ac81edbdbd` | 0 | - | poczatek etapu jest przodkiem commita wydania |

Liczby (noc, commit 571e186, w nawiasach):

- Zmienionych plikow 1145, w tym nowych 1062 (662 / 584). `git diff --stat`: 1129 plikow (646) - laczy w pary zmiany nazw (1145 - 16).

| Grupa | Nowe | Zmienione | Usuniete |
|---|---|---|---|
| E3 (paczki etapu 3) | 723 (245) | 29 (24) | 0 (0) |
| R58 (praca wlasciciela spoza etapu 3) | 242 (242) | 4 (4) | 0 (0) |
| R59 (praca wlasciciela spoza etapu 3) | 97 (97) | 34 (34) | 16 (16) |

- **Naruszen: 0** (noc: 0). Sciezek poza listami: 0 (wiersz `NARUSZENIA (grupa E3 i sciezki poza listami): 0`).
- Odstepstwo O11 (napisy ekranu nie-ASCII): **7 plikow z 7 na liscie**, razem 851 wierszy / 6936 bajtow nie-ASCII (noc: 807 / 6452):
  `dzien_skanera.py` 110 wierszy (866 B; noc 109 / 859), `dzien_skanera_kroki.toml` 134 (1783 B), `dzien_skanera_rdzen.py` 102 (946 B),
  `statusy.py` 283 (2142 B; noc 240 / 1665), `ui/napisy.py` 66 (318 B), `ui/napisy_rano.py` 111 (710 B), `testy/test_dzien_skanera.py` 45 (171 B).
- Odstepstwo dla kopii bajtowych R58 w `modele_plytek` ("decyzja wlasciciela nr 1 z 21.11.2026"; NOWE wobec nocy - w `RAPORT.md` 4a commita
  wydania nie ma jeszcze numeru O<n> dla tej pozycji): **10 plikow z 10 na liscie, suma SHA-256 = lista R58 w 10 z 10**:
  `okragla_ramkowa_poranna\{plytka_bazowa,plytka_n4,plytka_n5,plytka_n6}.stl` i `uklad.json`,
  `okragla_ramkowa_wieczorna\{plytka_bazowa,plytka_n1,plytka_n2,plytka_n3}.stl` i `uklad.json`. Co skrypt przy nich pominal: 8 plikow STL
  wiekszych niz 1024 KB (1079-1246 KB), 2 pliki `uklad.json` nie-ASCII (po 71 bajtow) z koncami CRLF (365 i 315 wierszy).
- Uwagi w grupach R58 / R59 (poza wynikiem T13, do oceny koordynatora): 126 (noc: 126) - R58: duzy plik 1, konce linii 23, nie ASCII 23,
  plik danych 2; R59: STL poza `modele_plytek` 2, duzy plik 10, konce linii 17, nie ASCII 43, plik danych 5.
- O10: kontrola "tylko pliki z list paczek" na poziomie katalogow (`t13_dozwolone.txt`) - jak w nocy.

Dowody T13: `t13_wynik.txt`, `t13_wynik.json`, `t13_wynik_stderr.txt`, `t13_diff_stat.txt`, `t13_repo_stan.txt`, `t13_czasy.txt`,
`krok_T13.cmd`. Drugi przebieg T13 (po dodaniu dowodow do repo) - poza tym zleceniem.

## Nastepca po zgineciu sesji

Sprawdz `t1_kolejka.log` (wiersze `KONIEC przebieg <n> | tor <t> | kod ...`), `kody.txt`, `t1_czasy.txt`, ostatnie wiersze obu logow pytest i
`<PC-katalog>\koordynator\log\ciezkie.log`; przebieg bez wiersza podsumowania = NIE ZMIERZONO, powtorz go tym samym plikiem
`krok_<n>.cmd` (przebieg 1: tor 1, przebieg 2: tor 3).
