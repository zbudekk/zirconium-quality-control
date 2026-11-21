# T1 - wynik przebiegow (21.11.2026)

Commit testow i kodu: 571e186cb8178209da670dde244dfc56bba5e300 (`<REPO>` = `<PC-katalog>\t0\repo`, detached; = commit paczki 0.3.1).
Kontrola `<REPO>` przed startem: `core.autocrlf` = `false`; `git status --short` puste (takze po obu przebiegach).
Liczba z `--collect-only`: **2222** (interpreter srodowiska wersji 2222, bazowy 2222, roznic w listach 0).

| | Przebieg 1 - srodowisko wersji (krok 4) | Przebieg 2 - interpreter bazowy (krok 5) |
|---|---|---|
| Interpreter | `<PC-katalog>\t0\odbior\Stanowisko\wersje\0.3.1\venv\Scripts\python.exe` przez `<K>\Polecenie.cmd` | `<PC>\AppData\Local\Programs\Python\Python312\python.exe` przez `narz\py.cmd` |
| Log | `t1_pytest.log` | `t1_pytest_bazowy.log` |
| Start - koniec | 02:53:21,10 - 03:22:57,26 | 03:22:58,13 - 03:48:55,11 |
| Wolny RAM przed startem | 75393 MB z 95652 | 73482 MB z 95652 |
| **Wiersz podsumowania** | `2213 passed, 9 skipped, 1 warning in 1773.05s (0:29:33)` | `2213 passed, 9 skipped, 1 warning in 1554.25s (0:25:54)` |
| **Kod wyjscia procesu (osobno)** | **0** (`kody.txt`: `krok4_pytest_wersja KOD=0`; `ciezkie.log`: `KONIEC odb-T1 tor 1 \| kod 0`) | **0** (`kody.txt`: `krok5_pytest_bazowy KOD=0`; `ciezkie.log`: `KONIEC odb-T1 tor 1 \| kod 0`) |
| passed / skipped / failed / errors | 2213 / 9 / 0 / 0 | 2213 / 9 / 0 / 0 |
| Suma wobec `--collect-only` | 2213 + 9 + 0 = 2222 = 2222 | 2213 + 9 + 0 = 2222 = 2222 |
| Znaki postepu w logu | 2222: `.` 2213, `s` 9, `F` 0, `E` 0 | 2222: `.` 2213, `s` 9, `F` 0, `E` 0 |
| Pominiete wobec listy 9 znanych | 9 z 9 znanych, spoza listy 0 | 9 z 9 znanych, spoza listy 0 |
| Czas | 29 min 33 s (pytest), 29 min 36 s (zegar) | 25 min 54 s (pytest), 25 min 57 s (zegar) |
| Zjawiska PC (`0xC0000409`, `0xC0000142`, `0xc000070a`) | nie wystapily | nie wystapily |
| Co jeszcze liczylo | T10 tor 2 (do 03:06:49), T12 tor 4 (do 03:03:55), T5 B4 tor 3 (03:01:18-03:03:56), T7 tor 4 (od 03:03:56: A, B2, B3); 5-21 procesow `python` | T7 tor 4 (B3 do 03:30:25, B1b 03:30:26-03:34:41); od 03:35 poza T1 nic ciezkiego; 2-6 procesow `python` |

Punkt odniesienia: `main` bf00921 = 1829 / 9 / 0, `main` 9ba9e91 = 1831 / 9 / 0; oczekiwane w planie na commicie wydania: ok. 2222, w tym
9 pominietych (galaz `e3/p15` po rundzie 2: 2213 passed / 9 skipped) - zgodne co do sztuki.

Testy nieudane: 0 w obu przebiegach - powtorek pojedynczych testow (5 razy) i powtorki calego przebiegu NIE bylo trzeba.
`test_aplikacja.py::test_b1_blokada_znika_razem_z_procesem` (padal w probie generalnej w srodowisku wersji 6 z 6): w przebiegu 1 passed.

Kryterium: 0 failed, 0 errors - spelnione w obu przebiegach; pominiete tylko znane z punktu odniesienia - spelnione (`t1_pominiete.txt`).
**T1: ZAL.**
