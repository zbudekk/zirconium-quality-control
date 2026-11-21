# Raport recenzenta - PR #43 (E3-A11w), runda 1

Data: 20.11.2026, recenzja 20:13-20:30. Zakres: `git -C <PC-katalog>\qc diff main...origin/e3/a11w`, HEAD `2a6cac5`
(14 commitow, 5 plikow: `stanowisko/__init__.py` +28, `testy/conftest.py` +8 -4, `testy/test_silnik.py` +78 -1,
`opisy_modulow/silnik.md` +27, `raporty/E3-A11w_2026-11-20.md` +507). O 20:25 galaz nadal na `2a6cac5`.

Metoda: najpierw wlasny przeglad diffu i zrodla `platform.py` Pythona 3.12.10, wlasne proby w kopii
`<PC-katalog>\qc-wt\rec-a11w` (detached `2a6cac5`; po probach `git status --short` pusty, niczego nie commitowalem),
potem logi i skrypty wykonawcy (`robocze\a11w\logi`, `proby`), na koncu raport wykonawcy. Wszystkie liczby ponizej sa z
moich pomiarow, chyba ze oznaczone "wg wykonawcy". Pliki robocze: `<PC-katalog>\koordynator\robocze\rec-a11w\`
(`logi\01`-`05`, `logi\szpieg\`, `proby\`).

Uruchomiono (1 proces python naraz, 2 watki): caly `testy/test_silnik.py` interpreterem bazowym 1 raz (RAM 67587 MB
wolnych, bez blokady); `-k a11w` 6 razy (1 bez zmian + 5 wstrzykniec); `test_limit_czasu_zadania` 5 razy na HEAD i 5 razy
na `main`; proby `wartosci.py` (6), `uchwyty.py` (12), szpieg zapytan WMI na 14 drogach startu + 7 testow silnika.
Przebiegow w srodowisku wersji (K) nie uruchamialem. Pelnego pytest nie powtarzalem.

Odczyty `serie.log` wykonawcy: 20:13:25 (79 wierszy), 20:25:07 (82 wiersze), 20:28:04 (83 wiersze) - liczniki w p. 2.8.

## 0. Werdykt i liczby

**Do scalenia po poprawkach.** B 0 / P 2 / D 5.

Diagnoza jest udowodniona eksperymentem wlacz / wylacz (takze moim, niezaleznym), poprawka dziala we wszystkich
sprawdzonych drogach startu programu i nie zmienia wartosci modulu `platform`. Do zamkniecia przed scaleniem: P1 (pomiary
kryterium 2 i pelny pytest nie sa jeszcze skonczone i wpisane do raportu - bez zmiany kodu) i P2 (kolejnosc importow w
`conftest.py`, czyli ochrona procesu testow, nie ma testu, ktory bez niej pada).

## 1. Uwagi

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| P1 | P | `raporty/E3-A11w_2026-11-20.md`:139-156, 233-237, 416, 418, 429 | Kryterium 2 i 4 w chwili recenzji nieudowodnione w raporcie: tabela 5.1 ma stan z 19:59 (B 5 z 5), krok 3 po poprawce "W KOLEJCE" (0 z 3 uruchomien; o 20:28 pliki `235`-`237*.zad` nadal czekaja), pelny pytest "brak - nie uruchomiony" (koordynator uruchomil go 20:08:43 na `2a6cac5`; o 20:28 ok. 80 %, 0 liter F / E w logu). Sam `serie.log` o 20:28:04 pokazuje juz 12 udanych przebiegow B z 12 dokonczonych (p. 2.8), ale program z prawdziwa analiza po poprawce (krok 3) nie byl jeszcze uruchomiony ani razu. | Bez zmiany kodu: dokonczyc kolejke (234c, 235-237), wpisac do raportu tabele 5.1 i 5.2, kryteria 2 i 4 oraz wynik pelnego pytest (oczekiwane 1835 / 9 / 0 wg wykonawcy). Jesli krok 3 pokaze zawieszenie albo restart silnika - wraca do recenzji. |
| P2 | P | `testy/conftest.py`:17-23; `testy/test_silnik.py`:2057-2072 | Czesc poprawki chroniaca PROCES TESTOW (to on zawisal w seriach) nie ma testu, ktory bez niej pada. Wstrzykniecie I2: w `conftest.py` `import stanowisko` przeniesiony ZA `import trimesh` -> `-k a11w`: 4 passed z 4. `test_a11w_proces_testow_nie_pyta_wmi` sprawdza tylko, ze po fakcie `platform.win32_ver()` nie pyta; 2 zapytan wyslanych wczesniej przy `import trimesh` nie widzi (wynik `uname()` jest juz w pamieci, a `_wmi_query` podmienione pozniej). Ktos (albo narzedzie porzadkujace importy bez znajomosci `noqa: I001`) przywraca stara kolejnosc -> proces testow znow traci losowy uchwyt po 5 s, T1 znow zawisa, a wszystkie testy `a11w` sa zielone. | Test w podprocesie ze szpiegiem (wzor `KOD_WMI` albo zdarzenie audytu `_wmi.exec_query`): `import conftest` z katalogu `testy` -> 0 zapytan; bez poprawnej kolejnosci ma dawac 2. Moj pomiar ze szpiegiem audytu: `pytest testy --collect-only` na HEAD = 0 zapytan, wiec taki test dzis przejdzie. |
| D1 | D | `testy/test_silnik.py`:92-94 | `analiza_probna` (funkcja probna ok. 50 istniejacych testow silnika) dostala `platform.system()` w mierzonej sciezce KAZDEGO zadania. Z blokada pierwsze wywolanie w swiezym procesie roboczym uruchamia podproces `cmd.exe /c ver`: czas szybkiego zadania wg analizy 0,051 s -> 0,101-0,110 s, wg silnika 0,094-0,110 s -> 0,156-0,171 s (6 + 6 pomiarow). Jedyny nieudany `test_limit_czasu_zadania` w logach na PC (1 plik z FAILED wobec 48 plikow z PASSED, `grep` po `koordynator\log` i `robocze`) to przebieg 229_Ap - po tej zmianie; szybkie zadanie przekroczylo limit 1,5 s. Zwiazek NIEUDOWODNIONY: dodatek to ok. 0,05 s z 1,5 s, u mnie 5 z 5 na HEAD i 5 z 5 na `main`; ale kazde nowe uruchomienie procesu (`cmd`) w mierzonej sciezce to dodatkowa okazja do zaciecia na obciazonym PC. | Wywolywac `platform.system()` tylko na zadanie (np. tresc pliku `WMI`) albo w osobnej funkcji probnej dla `test_a11w_proces_roboczy_nie_laduje_wmi` - pozostale testy czasowe maja wtedy te sama sciezke co na `main`. W raporcie dopisac zmierzony wklad. |
| D2 | D | `stanowisko/__init__.py`:14-15; `opisy_modulow/silnik.md`:224-225; raport p. 3 | Opis mowi, ze `platform` bierze dane z `sys.getwindowsversion()` i zmiennych srodowiska. Niepelne: sciezka zapasowa `_win32_ver` wola `_syscmd_ver()`, czyli podproces `cmd.exe /c "ver"` (zrodlo `platform.py`:280-287, 414; pomiar: 1 podproces na pierwsze `platform.system()` w procesie, kolejny na kazde `win32_ver()` / `platform()`). Kazdy start okna i kazdy start procesu roboczego uruchamia wiec raz `cmd`. Skutki ocenione: koszt 0,065-0,089 s (5 pomiarow; bez blokady na tym koncie 0,507 s, bo dochodza 2 limity WMI); okno konsoli nie mignie, bo program startuje przez `Stanowisko.cmd` / skrot do niego (`python.exe` z konsola), a proces roboczy ma wlasna niewidoczna konsole (E3-A2p); przy starcie przez `pythonw.exe` mignelaby. Gdy `cmd` nie wystartuje (zjawisko 0xC0000142), `platform` lapie blad i bierze `getwindowsversion()`. | Dopisac jedno zdanie w docstringu i w `silnik.md` (podproces `ver` raz na proces, bez okna dzieki konsoli procesu). Kodu nie zmieniac. |
| D3 | D | raport p. 6 (wiersz 256); `opisy_modulow/silnik.md`:228-229 | Lista narzedzi niechronionych niepelna: brak `narzedzia/auto_uklad.py`:30 i `narzedzia/straznik_R59.py`:39 (`import trimesh` w funkcji procesu puli PRZED `from stanowisko import` - procesy potomne puli pytaja WMI; proces glowny przy `--help` 0 zapytan) oraz `narzedzia/atrapy_koron.py` uruchamianego jako skrypt (zmierzone: 2 zapytania). Drugie zrodlo zapytan poza `trimesh`: `import numpy.testing` (`numpy/testing/_private/utils.py`:90, `platform.machine()`; zmierzone: 2 zapytania) - raport podaje "numpy: 0" (prawda dla samego `import numpy`). Dotyczy narzedzi deweloperskich uruchamianych interpreterem bazowym, nie programu technika. | Uzupelnic liste i zdanie "Granice" (numpy.testing). Trwale: `import stanowisko` jako pierwszy import w narzedziach - poza zakresem tej paczki (p. 5). |
| D4 | D | `stanowisko/__init__.py`:22-26 | Luka opisana przez wykonawce (raport p. 6.2): `_wmi` juz zaladowany, a `platform` jeszcze nie -> brak ochrony. Dzis nie wystepuje (moj `grep -rlw _wmi --include=*.py` w `site-packages`: 0 plikow; w bibliotece standardowej tylko `platform.py` i testy). | Skoro i tak bedzie runda poprawek: `_sys.modules["_wmi"] = None` bezwarunkowo + trzeci wariant testu (`import _wmi` na poczatku), jak proponuje wykonawca. |
| D5 | D | raport p. 7 (wiersze 389, 399) | Rekomendacja T1 / T2 odsyla do `proby\stosy.py` i `proby\krok3.ps1` - pliki istnieja, ale w katalogu roboczym wykonawcy (`<PC-katalog>\koordynator\robocze\a11w\proby\`), ktory ma byc sprzatany; w repo ich nie ma. | Podac pelna sciezke i zaznaczyc, ze katalogu `proby` nie sprzatac przed T1 / T2. |

## 2. Wlasne proby

### 2.1 Zrodlo `platform.py` (Python 3.12.10)

- `platform.py`:316-332: `try: import _wmi / except ImportError:` -> `_wmi_query` zglasza `OSError("not supported")`; inaczej
  `_wmi.exec_query("SELECT ... FROM Win32_OperatingSystem | Win32_Processor")`.
- Wpis `None` w `sys.modules` daje przy `import _wmi` wyjatek `ModuleNotFoundError` (podklasa `ImportError`) - dokladnie
  ten, ktory `platform` obsluguje. Nikt inny `_wmi` nie importuje (p. 1, D4).
- `platform.system()` -> `uname()` -> `win32_ver()` -> `_win32_ver()`: przy `OSError` z WMI sciezka zapasowa
  `getwindowsversion()` + `_syscmd_ver()` (podproces `ver`, `shell=True`) + rejestr `CurrentType`; potem
  `_get_machine_win32()`: przy `OSError` zmienne `PROCESSOR_ARCHITEW6432` / `PROCESSOR_ARCHITECTURE`. To ta sama sciezka,
  ktora Python mial przed 3.12 i ktora na tym koncie wykonuje sie takze BEZ blokady (po bledzie limitu WMI).

### 2.2 Eksperyment wlacz / wylacz (wlasny, niezalezny od skryptow wykonawcy)

`narz\py.cmd proby\uchwyty.py <bez|z> <monitor|przyneta>` z katalogu kopii; `z` = `import stanowisko` z HEAD przed
`import trimesh` (prawdziwa poprawka jako wylacznik), `bez` = sam `import trimesh`. Log `logi\02_proby_wmi.log`.

| Proba | Bez blokady | Z blokada |
|---|---|---|
| przyneta: po `import trimesh` stos watku glownego pokryty wartoscia uchwytu Event (128 KB), 9 s | zamkniety przez obcy watek **3 z 3** | **0 z 3** |
| monitor: proces zyje 15 s, obserwacja 169 uchwytow istniejacych przy starcie | zmiana 0 z 3 | zmiana 0 z 3 |

Wniosek: przy naturalnym wyzwalaczu (`import trimesh`) porzucony watek zamyka uchwyt o wartosci wzietej ze stosu watku
glownego, a import pakietu `stanowisko` to wylacza. Sam monitor w golym procesie niczego nie rozroznia (wartosc ze stosu
nie trafia tam w uchwyt ze startu) - potwierdzenia "ginie 0x5c" w procesie pytest nie powtarzalem, przeliczylem je z plikow
wykonawcy: `monitor_A.txt` 3 z 3 sesji, `monitor_B.txt` 3 z 3 (5,28-5,30 s po poczatku importu), `monitor_po_A.txt` 0 z 2,
`monitor_po_B.txt` 0 z 2; `wmi_dowod.py`: `z` 3 z 3 (A) i 3 z 3 (B), `kontrola` 0 z 2, `bez` 0 z 2 - zgodne z raportem.

### 2.3 Wartosci `platform` z blokada i bez

`narz\py.cmd proby\wartosci.py <bez|z>` (1 + 5 uruchomien): identyczne w obu wariantach - `system()` Windows, `machine()`
AMD64, `release()` 11, `version()` 10.0.26300, `win32_ver()` ('11', '10.0.26300', 'SP0', 'Multiprocessor Free'),
`platform()` Windows-11-10.0.26300-SP0, `processor()` i `uname()` te same, `win32_edition()` Professional; zadnego wyjatku.
Podprocesy: w obu wariantach 3 x `cmd.exe /c "ver"` (po jednym na `system()`, `win32_ver()`, `platform()`).
Pierwsze `platform.system()`: bez blokady 0,507 s, z blokada 0,065 / 0,089 / 0,070 / 0,071 / 0,081 s.
Ograniczenie: na koncie `<konto-PC>` WMI nie odpowiada, wiec wariant "bez" tez idzie sciezka zapasowa; porownania z
wartosciami z dzialajacego WMI (komputer stanowiska) nie zmierzylem - wg zrodla roznic w `system` / `machine` / `release`
/ `version` byc nie powinno.

### 2.4 Zasieg ochrony - szpieg zdarzenia audytu `_wmi.exec_query`

`proby\zasieg.sh` (szpieg `proby\szpieg\sitecustomize.py` na `PYTHONPATH`, nie importuje `_wmi`; `logi\04_zasieg.log`):

| Proces | Zapytan WMI |
|---|---|
| kontrola: `-c "import trimesh"` | 2 (`trimesh/interfaces/blender.py`:10) |
| `-c "import stanowisko, trimesh, open3d, numpy, scipy, PySide6.QtWidgets, requests"` | 0 |
| `-c "import numpy, numpy.testing, scipy, scipy.spatial, open3d, PySide6.QtWidgets, shiboken6, requests, plotly, dash, win32api"` (bez pakietu) | 2 (`numpy/testing/_private/utils.py`:90) |
| `-m stanowisko.aplikacja --atrapa --zamknij-po 4` (okno, Qt offscreen) | 0 |
| `-m stanowisko.porownaj --help`, `-m stanowisko.ui_test --help`, `-m stanowisko.dzien_skanera --sprawdz <brak>` | 0, 0, 0 |
| `narzedzia/rzut_z_gory.py --help`, `metryki_P2.py --help`, `atrapy_koron.py --help` | 2, 2, 2 (niechronione) |
| `narzedzia/auto_uklad.py --help`, `straznik_R59.py --help`, `symulator_skanera.py --help` | 0, 0, 0 (proces glowny; procesy puli dwoch pierwszych - D3, przeglad) |
| `-m pytest testy --collect-only` (import `conftest.py` i wszystkich modulow testow) | 0 |
| 7 testow silnika pod szpiegiem (`test_postep_i_pliki_wyjscia`, `test_awaria_prawdziwej_analizy_i_nastepne_zadanie`, `test_limit_czasu_zadania`, 4 x `a11w`; proces testow + procesy robocze z prawdziwa analiza), 7 passed w 105 s (`logi\05_szpieg_silnik.log`) | 0 w calym drzewie procesow |

Przeglad kodu: kazda droga startu programu to `python -m stanowisko.<modul>` (`Stanowisko.cmd`, `Samokontrola.cmd`,
`uruchom_*.bat`) - pakiet importuje sie przed modulem; proces roboczy (`spawn`) importuje `stanowisko.silnik` przy
odtwarzaniu obiektu procesu, a gdy modul glowny to `stanowisko.aplikacja` - jeszcze wczesniej. Pliku `.pth` (PR #39) nie
ocenialem.

### 2.5 Testy paczki i wstrzykniecia bledow

`narz\py.cmd -m pytest -q -p no:cacheprovider testy\test_silnik.py -k a11w` (`logi\03_wstrzykniecia.log`):

| Wariant | Wynik | Ocena |
|---|---|---|
| HEAD bez zmian | 4 passed | |
| I1: wywolanie `_bez_wmi()` usuniete z `__init__.py` | **4 failed z 4** | wykryte (zgodne z wykonawca) |
| I2: `conftest.py` - `import stanowisko` ZA `import trimesh` | 4 passed | **niewykryte -> P2** |
| I3: blokada tylko w procesie glownym (`multiprocessing.current_process().name != "MainProcess"` -> bez blokady) | 1 failed (`test_a11w_proces_roboczy_nie_laduje_wmi`: `assert True is False`), 3 passed | wykryte - test naprawde sprawdza proces roboczy |
| I4: bez podmiany `platform._wmi_query` (platform zaladowany wczesniej) | 2 failed (`[import platform]`, `proces_testow`), 2 passed | wykryte |

Uwaga do I3: pierwsza wersja mojego wstrzykniecia (`parent_process() is not None`) dala 4 passed, bo w chwili importu
pakietu w procesie potomnym `parent_process()` jest jeszcze `None` - blad wstrzykniecia, nie testu; liczy sie wersja wyzej.

Caly `testy\test_silnik.py` interpreterem bazowym w kopii recenzenta, 20:13:51-20:18:00: **63 passed, 5 skipped, 0 failed**
w 247 s, kod 0, 0 wierszy `fatal exception` (`logi\01_test_silnik_A.log`).

### 2.6 `test_limit_czasu_zadania` (przebieg 229_Ap)

- `testy\test_silnik.py::test_limit_czasu_zadania`: HEAD **5 z 5 passed** (2,79-2,96 s), `main` (`<PC-katalog>\qc`, tylko
  uruchomienie, `git status` pusty po probie) **5 z 5 passed** (2,68-3,15 s).
- Limit 1,5 s liczy sie od wyslania zadania do GOTOWEGO procesu roboczego (`silnik.py`:1611, 1673) - ponowny start
  procesu sie nie wlicza (odpowiedz na pytanie wykonawcy z p. 5.1).
- Czas szybkiego zadania w swiezym procesie roboczym (`proby\test_rec_czas.py`, po 6 pomiarow): HEAD wg silnika
  0,156-0,171 s, wg analizy 0,101-0,110 s; z usunietym `platform.system()` z `analiza_probna`: 0,094-0,110 s i 0,051 s.
- Ocena: nieudany przebieg to nie zawieszenie ani naruszenie pamieci; zwiazek z paczka mozliwy (D1), nieudowodniony.

### 2.7 Przebiegi 221 i 222

`p_221_Bp_stan.txt`: proces testow 100 s procesora (w zawieszeniu 104b: 5,2 s), zywy potomek z 28 s procesora i watkiem
`Running`, zrzut `faulthandler` - watek glowny w `subprocess.run` (`_uruchom_cli`, przygotowanie
`test_wynik_silnika_rowny_wierszowi_polecen[wieczorna]`); wolny RAM 6,0 i 4,1 GB. W 104b: brak zywych potomkow, wszystkie
watki czekaja. Wylaczenie obu z licznika (ani udane, ani zawieszone) jest zasadne i uczciwie opisane.

### 2.8 Liczniki z `serie.log` (wlasne liczenie; caly `test_silnik.py`)

| Stan | Wariant | Udane | Zawieszenia | Naruszenia pamieci | Inne |
|---|---|---|---|---|---|
| przed poprawka | A (bazowy) | 6 z 6 (101a, 102a, 103a, 104a, 105a, 106a) | 0 | 0 | 2 wiersze 103a / 103b przerwane przez wykonawce i powtorzone - nie liczone |
| przed poprawka | B (srodowisko wersji) | 4 z 6 | 2 (104b, 105b) | 0 | - |
| po poprawce, odczyt 20:13:25 | B | 8 (106c, 224, 225, 227, 228, 230, 231, 232) | 0 | 0 | 2 nie dokonczone (221, 222), 1 urwany restartem PC (201, bez wiersza) |
| po poprawce, odczyt 20:25:07 | B | 11 (+ 233, 234, 234a) | 0 | 0 | jak wyzej |
| po poprawce, odczyt 20:28:04 | B | **12 z 12 dokonczonych** (+ 234b) | **0** | **0** | jak wyzej |
| po poprawce, odczyt 20:28:04 | A | 3 z 4 (106d, 223, 226) | 0 | 0 | 1 nieudany (229: `test_limit_czasu_zadania`); 234c w toku |
| po poprawce, recenzent | A | 1 z 1 (p. 2.5) | 0 | 0 | poza seria wykonawcy |

Odstepstwo od "20 z 20" (decyzja koordynatora: co najmniej 12 B): licznik B o 20:28:04 = 12 udanych z 12 dokonczonych.
Dla orientacji: przy czestosci niepowodzen B sprzed poprawki 2 z 6 (wykonawca) 12 udanych z rzedu bez dzialajacej
poprawki ma prawdopodobienstwo ok. 0,8 %; przy 7 z 16 (z seria recenzenta PR #39, wg wykonawcy) ok. 0,1 %.

## 3. Kryteria zlecenia

| Nr | Kryterium | Ocena |
|---|---|---|
| 1 | Przyczyna nazwana i pokazana eksperymentem wlacz / wylacz | **potwierdzone wlasna proba** (p. 2.2: 3 z 3 wobec 0 z 3) i przegladem zrodla / logow wykonawcy. Zastrzezenia wykonawcy sa prawdziwe i uczciwie zapisane: lancuch "zamkniety uchwyt -> zawieszenie" pokazany proba wymuszona (2 z 2 w B, wg wykonawcy, niesprawdzone), nie w zawieszonym przebiegu serii; "dlaczego B czesciej niz A" nie ustalono. |
| 2 | Po poprawce `test_silnik.py` w srodowisku wersji bez zawieszen i naruszen pamieci; krok 3: wszystkie plytki, 0 zawieszen | **czesciowo**: seria B - potwierdzone przegladem `serie.log` (12 z 12 dokonczonych o 20:28:04; prog koordynatora 12 osiagniety, "20 z 20" ze zlecenia - nie); krok 3 po poprawce - **niepotwierdzone** (0 uruchomien w chwili recenzji) -> P1 |
| 3 | Rekomendacja T1 / T2 | **potwierdzone przegladem**: opcje istnieja (`--rootdir`, `-o faulthandler_timeout`, `-p no:cacheprovider`; `symulator_skanera.py`: `--folder`, `--zrodla`, `--odstep`, `--rownolegle`, `--seed`; `aplikacja`: `--zamknij-po`; instalator `/testy` z `pytest==9.1.1`), napisy do liczenia w logu istnieja w kodzie (`przyjety jako`, `proces silnika ...`, `uruchomienia procesu roboczego nieudana`, `diagnostyka KnownDlls`), proba `303_rootdir_k_B` jest w `serie.log` (4 passed, 64 deselected). Polecen w srodowisku wersji nie uruchamialem. Drobiazg: D5. |
| 4 | Testy, ktore bez poprawki padaja; pelny pytest 0 failed | testy: **potwierdzone wlasna proba** dla `__init__.py` (I1: 4 z 4, I3, I4), **niepotwierdzone** dla zmiany w `conftest.py` (I2 -> P2); pelny pytest: **niepotwierdzone** w chwili recenzji (w toku u koordynatora) -> P1 |
| 5 | Galaz wypchnieta | potwierdzone przegladem (`origin/e3/a11w` = `2a6cac5`) |

Kroki zlecenia: krok 1 - po 6 przebiegow na wariant zamiast 12; krok 2 - wariantow C / D / E nie wykonano. Oba odstepstwa
sa w raporcie wykonawcy (p. 2.2, p. 9) i nie podwazaja diagnozy (przyczyna pokazana wprost) - do wiadomosci w p. 5.

## 4. Zakres plikow i zasady

- Pliki zmienione: 5, wszystkie z opisu zakresu. Poza lista zlecenia: `stanowisko/__init__.py` i `testy/conftest.py`.
  Ocena: konieczne i najmniejsze mozliwe - blokada musi zadzialac przed pierwszym `import trimesh` w KAZDYM procesie
  (okno tez importuje `trimesh`), a jedynym kodem wykonywanym zawsze wczesniej jest import pakietu; poprawka w samym
  `silnik.py` (dozwolonym) nie chronilaby okna ani wiersza polecen. W `conftest.py` zmieniona tylko kolejnosc importow.
  Zlecenie dopuszcza inne pliki, "gdy diagnoza wskaze je jednoznacznie" - uzasadnienie jest w raporcie (p. 4).
- `conftest.py` nie zaslania zachowania programu: program blokuje tak samo (p. 2.4: okno, wiersz polecen, proces roboczy
  po 0 zapytan bez udzialu `conftest.py`).
- Pliki nietykalne (`match.py`, `inspect.py`, `plate.py`, `synth.py`, `uklad.py`, `modele_plytek/**`, progi, schemat bazy):
  nietkniete. Brak nowych pakietow. Brak duzych danych.
- Nowy plik (raport): ASCII (0 wierszy ze znakami spoza ASCII), LF (`git ls-files --eol`: `i/lf w/lf`). W calym diffie 0
  dodanych wierszy ze znakami spoza ASCII; pliki istniejace w swoim stylu (LF).
- Commity: 14, wszystkie ze stopka `Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>`, z przedrostkiem `E3-A11w:`.
- Dane osobowe: w raporcie i w cytowanych wierszach logow brak nazw zlecen, folderow prac i osob; sa tylko sciezki konta
  `<konto-PC>` i nazwy testow.
- Uczciwosc raportu: liczniki zamiast procentow, przebiegi 221 / 222 / 229 / 201 opisane osobno, "nie zmierzono" pisane
  wprost; zadnego testu nie pominieto ani nie oslabiono (63 passed / 5 skipped wobec 59 / 5 przed zmiana = 4 nowe testy).

## 5. Do decyzji wlasciciela (nie blokuje)

1. Kryterium "20 z 20" zastapione progiem koordynatora "co najmniej 12 B i 4 A": stan 20:28:04 - B 12 z 12 dokonczonych,
   A 3 z 4 (+ 1 z 1 recenzenta), 2 przebiegi B nie dokonczone przy przeciazonym PC. Czy to wystarcza przed T1 / T2, czy
   dociagnac do 20.
2. Krok 1 i 2 zlecenia skrocone (po 6 przebiegow przed poprawka, bez wariantow C / D / E); nie wiadomo, dlaczego
   srodowisko wersji zawisalo czesciej niz bazowe przy tym samym mechanizmie. Poprawka usuwa przyczyne w obu.
3. Nie wiadomo, czy na komputerze stanowiska WMI w ogole przekracza limit (na koncie `<konto-PC>`: zawsze). Poprawka jest
   tam nieszkodliwa (te same wartosci `platform`, jeden podproces `ver` na proces).
4. Narzedzia z `narzedzia/` uruchamiane interpreterem bazowym i procesy `pip` pozostaja niechronione (lista: raport p. 6
   + D3). W srodowisku wersji ma je chronic plik `.pth` z PR #39 (tu nieoceniany). Osobna mala paczka moglaby dac
   `import stanowisko` jako pierwszy import w narzedziach.
5. `test_limit_czasu_zadania` (limit 1,5 s) jest wrazliwy na obciazenie PC niezaleznie od tej paczki; przy pelnym pytest
   moze dac pojedynczy falszywy blad - decyzja, czy poluzowac test osobna paczka.

WERDYKT: do scalenia po poprawkach (B 0 / P 2 / D 5): P1 - dokonczyc i wpisac do raportu krok 3 po poprawce, serie i pelny pytest; P2 - test, ktory pada, gdy conftest.py importuje trimesh przed pakietem stanowisko.
