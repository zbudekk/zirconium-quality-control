WERDYKT T1: ZAL (oba przebiegi: 2213 passed / 9 skipped / 0 failed / 0 errors, kod wyjscia 0; 2222 = --collect-only; pominiete 9 z 9 znanych, spoza listy 0)

# T1 - Testy programu (pelny pytest) - WYNIK

Wykonawca: sesja testow koncowych (tor 1), PC, konto `<konto-PC>`, 21.11.2026 od 02:51. Plan: `PLAN_TESTOW.md`, sekcja "T1 - Testy programu".
`<K>` = `<PC-katalog>\t0\odbior\Stanowisko` (wersja 0.3.1 z paczki, po `/testy`: 76 pakietow), `<REPO>` = `<PC-katalog>\t0\repo`
(detached 571e186cb8178209da670dde244dfc56bba5e300 = commit paczki), `<ST>` = `<REPO>\Ramki\stanowisko`, `<P1>` = `<PC-katalog>\t0\odbior\paczka_0.3.1`,
`<ROB>` = `<PC-katalog>\koordynator\robocze\odbior\T1`, `PY` = `<PC>\AppData\Local\Programs\Python\Python312\python.exe`.

**Kryterium (plan):** pytest caly - 0 failed, 0 errors; pominiete tylko znane z punktu odniesienia.

## Kroki 1-3 i --collect-only (wykonane)

| Krok | Godzina | Polecenie | Kod | Wynik | Dowod |
|---|---|---|---|---|---|
| 1 | 02:51:29 | przez `ciezki.ps1 -Tor 1 -Kto odb-T1` plik `krok_1_3.cmd`: `call <P1>\zainstaluj.cmd /katalog <K> /python %PY% /bez-sieci /bez-pauzy /testy < NUL > <ROB>\t1_zainstaluj_testy.log 2>&1` | **0** | 6,2 s; "dokladam zestaw testowy", "zestaw testowy (pytest): 3 pakietow", "pakiety zgodne z lista zamrozona: 76 z 76", `SAMOKONTROLA: ZIELONA (ok 18, ostrzezenia 3)`, `INSTALACJA: GOTOWA - wersja biezaca 0.3.1 (poprzednia: brak)` | `t1_zainstaluj_testy.log`, `t1_1_czas.txt`, `kody.txt` |
| 3 | 02:51:35 | `call <K>\Polecenie.cmd -c "import stanowisko, sys; print(sys.modules.get('_wmi', 'brak'))" < NUL` | 0 | `None` | `t1_3_wmi.log` |
| 2a | 02:52:15 | `git -C <REPO> config --get core.autocrlf` | 0 | `false` | `t1_2_repo.txt` |
| 2b | 02:52:15 | `git -C <REPO> status --short` | 0 | puste (0 wierszy); `rev-parse HEAD` = 571e186cb8178209da670dde244dfc56bba5e300 | `t1_2_repo.txt` |
| 2c | 02:52:15 | `copy <ST>\ustawienia.przyklad.toml <ST>\ustawienia.toml` (przed krokiem pliku nie bylo) | 0 | "1 file(s) copied."; `git status --short` po kopii nadal puste (plik ignorowany) | `t1_2_repo.txt` |
| collect (wersja) | 02:52:16 | `call <K>\Polecenie.cmd -m pytest <ST>\testy -q --collect-only -p no:cacheprovider --rootdir <ST> < NUL` | 0 | `2222 tests collected in 5.87s` | `t1_collect.txt` |
| collect (bazowy) | 02:52:24 | `cd /d <ST>` i `call <PC-katalog>\koordynator\narz\py.cmd -m pytest -q --collect-only -p no:cacheprovider < NUL` | 0 | `2222 tests collected in 6.46s`; roznic w listach identyfikatorow obu interpreterow: 0 | `t1_collect.txt` |

Kolejnosc: krok 3 wykonany zaraz po kroku 1 (przed krokiem 2), bo od kroku 1 + 3 zalezal znak `..\T0\GOTOWE.txt` dla innych wykonawcow
(zapisany 02:51:47). Liczba oczekiwana: **2222** testow (plan: "ok. 2222") w 50 plikach `testy\test_*.py`.

## Punkt odniesienia dla pominietych

`<PC-katalog>\koordynator\log\pytest_bazowy_bf00921.log`: `1829 passed, 9 skipped, 2 warnings in 1372.05s (0:22:52)`. Ten log jest BEZ `-rs` -
nie ma w nim nazw pominietych testow, tylko litery `s` w wierszach postepu: testy nr 29, 550, 1489-1493, 1560, 1561 (uklad 1 + 1 + 5 + 2).
Lista nazw z powodami pochodzi z logu proby generalnej 21.11 (`robocze\proba\logi\04f_t1_pytest.log`, srodowisko wersji, f5c3e01,
`1 failed, 2202 passed, 9 skipped`) - 6 wierszy `SKIPPED` = 9 testow w tym samym ukladzie 1 + 1 + 5 + 2:

| Nr | Plik:wiersz | Ile | Powod |
|---|---|---|---|
| 1 | `test_aplikacja.py:1129` | 1 | wariant na duzych skanach odniesienia: ustaw E3A3_DANE_REF ... i E3A3_PROJEKTY |
| 2 | `test_katalog.py:133` | 1 | brak folderu projektow z pulpitu |
| 3-6 | `test_silnik.py:1981` | 4 | wariant na duzych skanach odniesienia: ustaw E3A2_DANE_REF ... i E3A2_PROJEKTY |
| 7 | `test_silnik.py:1988` | 1 | wariant na duzych skanach odniesienia: ustaw E3A2_DANE_REF ... i E3A2_PROJEKTY |
| 8 | `test_ui.py:67` | 1 | P3a: okno jest szkicem - watek silnika nie konczy sie pod offscreen; naprawa w P3a-2 |
| 9 | `test_ui.py:129` | 1 | brak dane/syntetyczne_P2 albo projektow z pulpitu |

(Numery wierszy plikow moga sie roznic miedzy f5c3e01 a 571e186 - porownanie po pliku, liczbie i powodzie.)

## Przebiegi (uzupelniane po kazdym)

Oba przebiegi ida jako kolejka odlaczona (`kolejka_t1.ps1`, `Start-Process -WindowStyle Hidden`), kazdy przez
`powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 1 -Kto odb-T1 -Polecenie "<ROB>\krok_<n>.cmd"`;
dziennik kolejki: `t1_kolejka.log`; godziny i kody: `t1_czasy.txt`, `kody.txt`; "co jeszcze liczylo" co 120 s: `t1_co_liczylo.txt`
(wolny RAM, liczba procesow `python` wg katalogu, zajete tory blokady).

- Przebieg 1 (krok 4, interpreter srodowiska wersji), plik `krok_4.cmd`:
  `call <K>\Polecenie.cmd -X faulthandler -m pytest <ST>\testy -q -rs -p no:cacheprovider --rootdir <ST> -o faulthandler_timeout=900 < NUL > <ROB>\t1_pytest.log 2>&1`
  START 02:53:21,10 (`ciezkie.log`: `START odb-T1 tor 1 | RAM 75351 MB`); wolny RAM przed: 75393 MB z 95652.
  KONIEC 03:22:57,26. **Wiersz podsumowania: `2213 passed, 9 skipped, 1 warning in 1773.05s (0:29:33)`. Kod wyjscia (osobno): 0**
  (`kody.txt`: `krok4_pytest_wersja KOD=0`; `ciezkie.log`: `03:22:57 KONIEC odb-T1 tor 1 | kod 0`). failed 0, errors 0.
  Znaki postepu w logu: 2222 = 2213 kropek + 9 `s` + 0 `F` + 0 `E`; suma 2213 + 9 + 0 = 2222 = `--collect-only`. Wierszy z
  `failed` / `error` / `Fatal Python` / `Traceback` / `Timeout (` w logu: 0. 1 ostrzezenie: `UserWarning` w
  `test_auto_uklad.py::test_numer_spoza_rozpoznanej_rodziny_jest_pomijany` (tresc w logu). Zjawiska `0xC0000409` / `0xC0000142` nie bylo.
  Pominiete: 6 wierszy `SKIPPED` = 9 testow, te same pliki, liczby i powody co lista odniesienia (tabela wyzej; jedyna roznica:
  `test_aplikacja.py:1142` zamiast `:1129` - przesuniecie wiersza w pliku miedzy f5c3e01 a 571e186); pozycje `s`: 29, 678, 1846-1850,
  1922, 1923 (uklad 1 + 1 + 5 + 2 jak w bf00921). Spoza listy 9 znanych: 0. Szczegoly: `t1_pominiete.txt`.
  Co jeszcze liczylo (z `ciezkie.log` i `t1_co_liczylo.txt`): T10 tor 2 (02:52:26-03:06:49, ciezka analiza), T12 tor 4 (instalacje
  i czesc B do 03:03:55), T5 B4 tor 3 (03:01:18-03:03:56), T7 tor 4 (czesc A 03:03:56-03:08:06, B2 03:08:16-03:20:02, B3 od 03:20:03);
  procesow `python` na PC 5-21 (szczyt 21 o 03:03), wolny RAM 66,9-74,8 GB. Czas 29 min 33 s (proba generalna, PC malo obciazony: 27 min 20 s).
  Testy czasowe (`test_k4`, `test_6`, `test_f`, klasa `Petla`): 0 nieudanych mimo obciazenia. **Przebieg 1: 0 failed, 0 errors.**
- Przebieg 2 (krok 5, interpreter bazowy), plik `krok_5.cmd`:
  `cd /d <ST>` i `call <PC-katalog>\koordynator\narz\py.cmd -m pytest -q -p no:cacheprovider -rs < NUL > <ROB>\t1_pytest_bazowy.log 2>&1`
  START 03:22:58,13 (`ciezkie.log`: `START odb-T1 tor 1 | RAM 73434 MB`); wolny RAM przed: 73482 MB z 95652. KONIEC 03:48:55,11.
  **Wiersz podsumowania: `2213 passed, 9 skipped, 1 warning in 1554.25s (0:25:54)`. Kod wyjscia (osobno): 0**
  (`kody.txt`: `krok5_pytest_bazowy KOD=0`; `ciezkie.log`: `03:48:55 KONIEC odb-T1 tor 1 | kod 0`). failed 0, errors 0.
  Znaki postepu: 2222 = 2213 kropek + 9 `s` + 0 `F` + 0 `E`; suma = 2222 = `--collect-only`. Wierszy z `failed` / `error` /
  `Fatal Python` / `Traceback` w logu: 0. To samo 1 ostrzezenie co w przebiegu 1. Zjawisk `0xC0000409` / `0xC0000142` nie bylo.
  Pominiete: te same 6 wierszy `SKIPPED` = 9 testow na tych samych pozycjach (29, 678, 1846-1850, 1922, 1923); spoza listy 9 znanych: 0.
  Co jeszcze liczylo: T7 tor 4 (B3 do 03:30:25, B1b 03:30:26-03:34:41); od 03:35 zaden inny tor blokady nie byl zajety;
  procesow `python` na PC 2-6, wolny RAM 71,9-73,6 GB. Czas 25 min 54 s (punkt odniesienia bf00921: 22 min 52 s przy 1838 testach).
  **Przebieg 2: 0 failed, 0 errors.**

W plikach `krok_4.cmd` / `krok_5.cmd` na poczatku `set QT_QPA_PLATFORM=offscreen` (zasada planu); liczby watkow (`OMP_NUM_THREADS` itd.)
w przebiegu 1 NIE ustawiano - polecenie planu doslownie (`Polecenie.cmd` ich nie ustawia); w przebiegu 2 ustawia je `py.cmd` (2 watki).

## Werdykt czesci kryterium

| Czesc kryterium | Przebieg 1 (srodowisko wersji) | Przebieg 2 (bazowy) | Werdykt |
|---|---|---|---|
| 0 failed | 0 (wiersz podsumowania bez `failed`; 0 znakow `F`) | 0 | ZAL |
| 0 errors | 0 (wiersz podsumowania bez `error`; 0 znakow `E`) | 0 | ZAL |
| pominiete tylko znane z punktu odniesienia | 9 z 9 znanych, spoza listy 0 | 9 z 9 znanych, spoza listy 0 | ZAL |
| kod wyjscia procesu (osobno) | 0 | 0 | - |
| suma = `--collect-only` | 2213 + 9 + 0 = 2222 | 2213 + 9 + 0 = 2222 | zgodne |

**Calosc T1: ZAL** (bez odstepstwa). Zestawienie: `t1_wynik.md`; pominiete: `t1_pominiete.txt`; liczba testow: `t1_collect.txt`.

Testy nieudane: brak w obu przebiegach, wiec regula "powtorz test osobno 5 razy obydwoma interpreterami / powtorz caly przebieg po
ciezkich testach" nie miala zastosowania - zadnej powtorki nie wykonano. Kazdy przebieg wykonany 1 raz (1 proba = 1 wynik).
`test_aplikacja.py::test_b1_blokada_znika_razem_z_procesem` (proba generalna: failed w srodowisku wersji 6 z 6) - teraz passed w obu
przebiegach (test nr 16 kolejnosci, w logach kropka). Testy czasowe (`test_ramka::test_k4`, `test_ui_wieczor::test_6`,
`test_aplikacja::test_f`, klasa `Petla`): 0 nieudanych, mimo ze przebieg 1 szedl rownolegle z T10, T12, T5 B4 i T7.

## Polecenia planu zmienione / potkniecia

1. Polecenia krokow 1, 3, 4, 5 i `--collect-only` wykonane doslownie, w plikach `.cmd` z `call`, `< NUL` i `set QT_QPA_PLATFORM=offscreen`
   (zasada planu). Krok 5: zamiast `cmd /c "cd /d <ST> && ...py.cmd ..."` w pliku `krok_5.cmd` jest `cd /d %ST%` i `call ...py.cmd ...` -
   to samo polecenie w postaci pliku (wymog `ciezki.ps1` + zapis kodu wyjscia).
2. Kolejnosc: krok 3 (`_wmi`) przed krokiem 2 (kontrola `<REPO>`) - oba przed przebiegami; powod: znak `GOTOWE.txt`.
3. `--collect-only` interpreterem bazowym: plan podaje polecenie tylko dla srodowiska wersji; dla bazowego uzyto
   `cd /d <ST>` i `py.cmd -m pytest -q --collect-only -p no:cacheprovider` (odpowiednik polecenia kroku 5).
4. Punkt odniesienia `pytest_bazowy_bf00921.log` nie zawiera listy nazw pominietych (log bez `-rs`) - "lista 9" odtworzona z: pozycji
   liter `s` w tym logu (uklad 1 + 1 + 5 + 2), zrodel testow w bf00921 (`git grep`, te same miejsca pominiec) i wierszy `-rs` proby
   generalnej. Wynik porownania jednoznaczny (te same 9 testow), ale droga porownania jest inna niz "lista z logu odniesienia".

## Do decyzji koordynatora / wlasciciela

- Brak: T1 = ZAL bez odstepstwa. Do wiadomosci: p. 4 wyzej (log odniesienia bez `-rs` - przy nastepnym punkcie odniesienia uruchomic z `-rs`).
- W `<REPO>` po testach leza 2 pozycje IGNOROWANE przez git (`git status --short` puste): `Ramki/stanowisko/ustawienia.toml`
  (zalozony w kroku 2 - zostawiony dla T5 / T6 / T7) i `Ramki/stanowisko/ramka/__pycache__/` (powstal 03:12:48, w czasie przebiegu 1;
  nie ustalono, czy z testu T1 uruchamiajacego proces potomny bez `PYTHONDONTWRITEBYTECODE`, czy z innego wykonawcy uzywajacego `<REPO>`).
  Niczego nie usuwano.

## Uwagi o srodowisku

- Sesja wykonawcy ma `PYTHONUTF8=1` i `PYTHONIOENCODING=utf-8:surrogateescape`; oba przebiegi je dziedzicza (`Polecenie.cmd` i `py.cmd`
  ustawiaja `PYTHONUTF8=1` same; `PYTHONIOENCODING` pochodzi z sesji).
- Nastepca po zgineciu sesji: sprawdz `t1_kolejka.log` (wiersze `KONIEC przebieg <n> | kod ...`), `kody.txt`, ostatnie wiersze obu logow
  pytest i `<PC-katalog>\koordynator\log\ciezkie.log`; przebieg bez wiersza podsumowania = NIE ZMIERZONO, powtorz go tym samym plikiem `krok_<n>.cmd`.
