# T1 - wynik przebiegow na wydaniu 0.3.3 (21.11.2026)

Commit testow i kodu: 0fedbf6e4f97dc68b2f4679061a960ac81edbdbd (`<REPO>` = `<PC-katalog>\t0\repo2`, detached; = commit paczki 0.3.3).
Kontrola `<REPO>` przed startem: `core.autocrlf` = `false`; `git status --short` puste (takze po obu przebiegach, sprawdzone 18:24).
Liczba z `--collect-only`: **2515** (interpreter srodowiska wersji 2515, bazowy 2515, roznic w listach 0).

| | Przebieg 1 - srodowisko wersji (krok 4, tor 1) | Przebieg 2 - interpreter bazowy (krok 5, tor 3) |
|---|---|---|
| Interpreter | `<PC-katalog>\t0\odbior2\Stanowisko\wersje\0.3.3\venv\Scripts\python.exe` przez `<K>\Polecenie.cmd` | `<PC>\AppData\Local\Programs\Python\Python312\python.exe` przez `narz\py.cmd` |
| Log | `t1_pytest.log` | `t1_pytest_bazowy.log` |
| Start - koniec | 17:46:00,37 - 18:23:30,35 | 17:45:58,55 - 18:23:07,68 |
| Wolny RAM przed startem | 69652 MB z 95652 | 69834 MB z 95652 |
| **Wiersz podsumowania** | `2506 passed, 9 skipped, 1 warning in 2246.86s (0:37:26)` | `2506 passed, 9 skipped, 1 warning in 2225.26s (0:37:05)` |
| **Kod wyjscia procesu (osobno)** | **-1073741819 = 0xC0000005** PO wierszu podsumowania (`kody.txt`: `krok4_pytest_wersja KOD=-1073741819`; `ciezkie.log`: `18:23:30 KONIEC f1 tor 1 \| kod -1073741819`) - NOWE, inny kod niz znany 0xC0000409 | **-1073740791 = 0xC0000409** PO wierszu podsumowania (`kody.txt`: `krok5_pytest_bazowy KOD=-1073740791`; `ciezkie.log`: `18:23:07 KONIEC f1 tor 3 \| kod -1073740791`) - znane zjawisko |
| passed / skipped / failed / errors | 2506 / 9 / 0 / 0 | 2506 / 9 / 0 / 0 |
| Suma wobec `--collect-only` | 2506 + 9 + 0 = 2515 = 2515 | 2506 + 9 + 0 = 2515 = 2515 |
| Znaki postepu w logu | 2515: `.` 2506, `s` 9, `F` 0, `E` 0 | 2515: `.` 2506, `s` 9, `F` 0, `E` 0 |
| Pominiete wobec listy 9 znanych | 9 z 9 znanych, spoza listy 0 | 9 z 9 znanych, spoza listy 0 |
| Czas | 37 min 26 s (pytest), 37 min 30 s (zegar) | 37 min 5 s (pytest), 37 min 9 s (zegar) |
| Tekst w logu po wierszu podsumowania | `Fatal Python error: Aborted`, `Current thread ... <no Python frame>`, lista modulow rozszerzen, 2 x `QThreadStorage: entry ... destroyed before end of thread`, `Windows fatal exception: access violation`, `<no Python frame>` (wypisuje to `-X faulthandler` z polecenia planu) | nic (log konczy sie wierszem podsumowania) |
| Co jeszcze liczylo | drugi przebieg T1 (tor 3) przez caly czas; T2 tor 2 (do 17:47:58); T12 tor 2 (17:48:14-18:03:29, 4 kroki z instalacjami); T11 tor 4 (od 17:48:30 do konca przebiegu); 5-11 procesow `python` na PC, wolny RAM 59,2-69,4 GB | pierwszy przebieg T1 (tor 1) przez caly czas; reszta jak obok |

Punkt odniesienia: pelny pytest drzewa wydania przed scaleniem, interpreter bazowy: 2506 passed / 9 skipped / 0 failed - **zgodne co do
sztuki w obu przebiegach**. Noc (0.3.1, 571e186): 2213 / 9 / 0 w obu srodowiskach, kody 0 i 0, 29 min 33 s i 25 min 54 s (przebiegi po kolei).

Testy nieudane: 0 w obu przebiegach - powtorek pojedynczych testow (5 razy) NIE bylo trzeba. `test_silnik.py::test_pamiec_linii_na_dysku`
(znany niestabilny): passed w obu przebiegach. Testy czasowe (`test_ramka::test_k4`, `test_ui_wieczor::test_6`, `test_aplikacja::test_f`,
klasa `Petla`): 0 nieudanych, mimo ze oba przebiegi szly rownolegle ze soba, z T11 i z T12.

Kryterium: 0 failed, 0 errors - spelnione w obu przebiegach (wiersz podsumowania); pominiete tylko znane z punktu odniesienia - spelnione
(`t1_pominiete.txt`). Kody wyjscia obu procesow rozne od 0, oba PO wierszu podsumowania: przebieg 2 - znane zjawisko 0xC0000409;
przebieg 1 - 0xC0000005 (NOWE; plan opisuje tylko 0xC0000409).
**T1: ZAL z odstepstwem NOWE (kod wyjscia przebiegu 1 = 0xC0000005 po wierszu podsumowania - do decyzji koordynatora).**
