# Raport recenzenta - PR #43 (E3-A11w), runda 2

Data: 20.11.2026, recenzja 22:34-ok. 23:00. Zakres przyrostowy: `git -C <PC-katalog>\qc diff 2a6cac5..origin/e3/a11w`
(HEAD rundy 1 = `2a6cac5`). Na starcie HEAD `8cdc82d` (4 commity: `b93815e` testy; `9ecb752`, `58978ba`, `8cdc82d` raport i
`silnik.md`); w trakcie recenzji doszedl `ce12ffe` (sam raport, +51 -1) - objety, p. 2.9. Calosc `main...origin/e3/a11w`:
5 plikow, te same co w rundzie 1.

Metoda: najpierw wlasny przeglad diffu i wlasne proby w kopii `<PC-katalog>\qc-wt\rec-a11w` (detached `8cdc82d`; po kazdej
probie `git checkout -- <plik>`, na koncu `git status --short` pusty, niczego nie commitowalem), potem logi wykonawcy
(`robocze\a11w\logi`), na koncu raport paczki. Liczby ponizej sa z moich pomiarow, chyba ze oznaczone "wg wykonawcy".
Pliki robocze: `<PC-katalog>\koordynator\robocze\rec-a11w\runda2\` (`01`-`11`, skrypty `f35*.sh`, `wstrzykniecia2.sh`).

Uruchomiono (najwyzej 2 procesy python naraz): `--collect-only` 1 raz; test nr 35 pelnego pytest 45 razy (15 x kopia
recenzenta HEAD, 30 x `main` w `<PC-katalog>\qc` - tylko uruchomienie, `git status --short` po probach pusty); `-k a11w`
7 razy (1 bez zmian + 6 wariantow wstrzykniec); caly `testy\test_silnik.py` 1 raz przez `narz\ciezki.ps1 -Tor 4` (22:43:01-22:47:06);
czas szybkiego zadania 2 x 6 pomiarow; program `--atrapa --zamknij-po 3` 8 razy; 3 przebiegi plikow testow Qt z zapisem
kodu wyjscia; odczyt 10 zrzutow awaryjnych skryptem wykonawcy `proby\zrzut.ps1` + wlasne przeszukanie napisow w 3 zrzutach.
Pelnego pytest nie uruchamialem. Przebiegow w srodowisku wersji nie uruchamialem.

## 0. Werdykt i liczby

**Do scalenia po poprawkach. B 0 / P 1 / D 5 (P1 - reszta, bez zmiany kodu; D: 3 nowe D6-D8, 2 odlozone z rundy 1: docstring z D2 i D4).**

Kod programu (`stanowisko/__init__.py`, `testy/conftest.py`) jest w rundzie 2 BEZ ZMIAN wobec `2a6cac5`; zmienily sie tylko
testy (`testy/test_silnik.py` +29 -3), opis `silnik.md` i raport. Bledow wprowadzonych poprawkami nie znalazlem.
Wstrzykniecia: 3 z 3 wykryte przez testy paczki (+ 2 dodatkowe warianty P2 wykryte; cofniecie D1 z zalozenia niewykrywalne).

## 1. Uwagi

### 1.1 Uwagi rundy 1

| Uwaga rundy 1 | Stan | Dowod |
|---|---|---|
| **P1** - wyniki serii, krok 3 i pelny pytest w raporcie | **serie i krok 3: zamknieta; pelny pytest: otwarta formalnie** (wynik jest w logu, nie ma go w raporcie paczki) | Tabele p. 5.1 i 5.2 raportu paczki przeliczone z `serie.log` (87 wierszy) i dziennikow - zgodne co do przebiegu (p. 2.2): po poprawce B **12 udanych z 12 dokonczonych** (106c, 224, 225, 227, 228, 230, 231, 232, 233, 234, 234a, 234b; poza licznikiem 221, 222 - przerwane przez skrypt, 201 - restart PC), 0 zawieszen, 0 naruszen pamieci; A **4 z 5** (106d, 223, 226, 234c; 229 = `test_limit_czasu_zadania`); przed poprawka A 6 z 6, B 4 z 6 (2 zawieszenia). Krok 3 po poprawce: 235 B 10 z 10, 236 B 10 z 10, 237 A 10 z 10; w dziennikach `przyjety jako` 20 / 10, `proces silnika` 0 / 0, nieudanych startow 0 / 0, kod programu 0 w 3 z 3. Pelny pytest: przebieg wykonawcy na HEAD `8cdc82d` skonczyl sie 22:59:50 - w logu **1836 passed, 9 skipped, 0 failed** (kod wyjscia -1073740791, p. 2.9), ale raport paczki na `ce12ffe` ma w tym miejscu nadal "W TOKU" (wiersze 532, 616, 727, 745). Do zamkniecia: commit samego raportu z tym wynikiem, kodem wyjscia i bez znacznikow "W TOKU". |
| **P2** - test na kolejnosc importow w `conftest.py` | **zamknieta** | `test_a11w_conftest_importuje_pakiet_przed_trimesh` (`testy/test_silnik.py`:2076-2098). Wlasna proba (p. 2.3): na kodzie paczki 5 passed; `import stanowisko` przeniesiony ZA `import trimesh` -> 1 failed (nowy test, "zapytania ... : 2"), 4 passed; `import numpy.testing` przed pakietem -> 1 failed; `platform.machine()` przed pakietem -> 1 failed. Test nie jest kruchy: osobny podproces (`sys.executable -c`), wiec nie zalezy od kolejnosci plikow testow ani od tego, co proces testow juz zaimportowal; szpieg to zdarzenie audytu `_wmi.exec_query`, ktore pada przy WYSLANIU zapytania, wiec wynik nie zalezy od tego, czy WMI na danym komputerze odpowiada; sprawdza, ze zaimportowal sie wlasciwy `conftest.py`. Granica (nie uwaga): w srodowisku wersji z plikiem `.pth` z PR #39 i w Pythonie bez `_wmi` test przechodzi niezaleznie od kolejnosci (blokada dziala wczesniej) - wykrywa blad tylko interpreterem bazowym, czyli tam, gdzie biegnie pelny pytest. |
| D1 - `platform.system()` w kazdym zadaniu probnym | poprawiona | `analiza_probna` wola `platform.system()` tylko dla pliku o tresci `WMI`. Pomiar (p. 2.4): czas szybkiego zadania na HEAD 0,109-0,110 s wg silnika / 0,050-0,064 s wg analizy (jak przed paczka: 0,094-0,110 / 0,051 z rundy 1); z cofnietym D1 0,156-0,187 / 0,100-0,117 s. Test procesu roboczego nadal cos sprawdza: blokada tylko w procesie glownym -> 1 failed (W3). Zmiana dotyczy wylacznie funkcji probnej testow - silnik, dziennik i samokontrola nie maja z nia stycznosci. |
| D2 - opis pomija podproces `cmd /c ver` | czesciowo | `silnik.md` i raport p. 3 poprawione; docstring `stanowisko/__init__.py` odlozony (plik programu bez zmian) - opisane w raporcie (odstepstwo 10). |
| D3 - lista narzedzi niechronionych, `numpy.testing` | poprawiona | `silnik.md` akapit "Granice" i raport p. 6. |
| D4 - luka: `_wmi` zaladowany, `platform` nie | odlozona | bez zmian; opisana (raport p. 6.2, `silnik.md`). Dzis nie wystepuje. |
| D5 - T1 / T2 odsylaja do plikow spoza repo | poprawiona | raport p. 7: pelne sciezki `stosy.py`, `krok3.ps1`, zaznaczone "nie ma w repo, katalogu `proby` nie sprzatac". |

### 1.2 Nowe uwagi rundy 2

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| D6 | D | raport p. 8.1.1 (`ce12ffe`) | Raport podaje dla testu nr 35 (`test_k3_excel_pytaj_...`) "5 z 5 na HEAD i 5 z 5 na `main`". Moje powtorki: HEAD **14 z 15**, `main` **29 z 30** - test pada takze uruchamiany osobno, przy 77-81 GB wolnego RAM (HEAD: `petla.przerwa` 0,211 s > 0,2 s, wiersz 777; `main`: tresc bledu nie zapisana przez moj skrypt). Wniosek wykonawcy (test czasowy, nie paczka) jest przez to mocniejszy, ale zdanie "5 z 5" zaniza czestosc: ok. 1 na 22 uruchomien. | Dopisac w p. 8.1.1 liczby recenzenta i wniosek dla T1: ten test (i inne z klasa `Petla`) moze dac pojedyncze "failed" bez zwiazku z paczka - wtedy powtorka osobno wg `wspolne.md`. Kodu nie zmieniac. |
| D7 | D | raport p. 8.2, wiersz "Czy cos jest w logu po podsumowaniu" i Zalecenie (4) | Raport stwierdza brak komunikatu Qt w logu pytest, ale nie wyjasnia dlaczego, a tresc komunikatu uznaje za mozliwa do zdobycia dopiero osobna paczka. Moja proba (p. 2.6): proces bez okna konsoli (tak startuja procesy z sesji) NIE wypisuje komunikatow Qt na przekierowane stderr - 0 wierszy; z `QT_FORCE_STDERR_LOGGING=1` te same komunikaty sa w pliku - 3 wiersze. Brak komunikatu w logu nie przeczy wiec hipotezie "blad krytyczny Qt", a tresc da sie zlapac bez zmiany kodu. | Dopisac w p. 8.2: jeden dodatkowy pelny przebieg diagnostyczny z `set QT_FORCE_STDERR_LOGGING=1` (NIE przebieg T1 - komunikaty Qt trafia wtedy takze na stderr procesow potomnych; sprawdzilem tylko 3 pliki: 62 passed, 2 skipped, 0 failed). |
| D8 | D | raport p. 8.2, wiersze "Czy to zjawisko jest starsze niz ta paczka" i "Ocena" | Raport: "Jakie to byly procesy (pelny pytest czy pojedyncze pliki), nie ustalono" i czestosc "dzis 1 z 4". Moje ustalenie (p. 2.6): 9 z 9 zrzutow z 18-19.11 to konce PELNYCH pytestow innych paczek (czas zrzutu = ostatni zapis logu w `<PC-katalog>\e3` + 1-3 s), w tamtym oknie 9 z 14 pelnych przebiegow; dzis po przebiegu na HEAD 2 z 5, oba na tej galezi. Bez tej informacji czytelnik raportu widzi "z paczka 2 z 2, bez paczki 0 z 3" i moze uznac zjawisko za skutek paczki albo za rzadkie. | Dopisac w p. 8.2 dopasowanie zrzutow do logow i obie czestosci; w zaleceniu dla T1 zmienic "rzadkie" na "ok. polowa pelnych przebiegow". Rozstrzygniecie "czy paczka podnosi czestosc": 2-3 pelne przebiegi na `main` z zapisem kodu (koordynator; nie blokuje). |

## 2. Wlasne proby

### 2.1 Jedno "F" w przerwanym pelnym pytest na `b93815e` (log `robocze\a11w\logi\pytest_pelny_b93815e.log`)

- Log: 1261 wynikow z 1845 (1258 passed, 2 skipped, 1 failed), urwany na 66 %; litera `F` jest 35. znakiem pierwszego wiersza.
- `narz\py.cmd -m pytest -q -p no:cacheprovider --collect-only` w kopii recenzenta: 1845 testow; 29. =
  `test_aplikacja.py::test_skany_odniesienia_przez_cala_aplikacje_w_petli_qt` (zgodne z `s`), **35. =
  `testy/test_aplikacja_rano.py::test_k3_excel_pytaj_propozycje_rowne_kompletnym_i_tylko_kolor_wlasciwych_komorek`**
  (`runda2\01_collect.log`).
- Test spoza paczki, czasowy: asercja `petla.tykniec >= 20 and petla.przerwa <= UW.PROG_PRZERWY_S` (`test_aplikacja_rano.py`:777,
  prog 0,2 s przerwy petli okna, zegar scienny) + oczekiwanie z limitem 10 s (wiersz 739).
- Powtorki tego jednego testu, na przemian kopia recenzenta (HEAD `8cdc82d`) i `main` `9ba9e91` (22:35-22:40, 77-81 GB
  wolnego RAM, w tle 2 pelne pytesty innych sesji):

| Kod | Uruchomien | Passed | Failed | Szczegol |
|---|---|---|---|---|
| HEAD `8cdc82d` | 15 | **14** | 1 | nieudany: `assert (70 >= 20 and 0.2112 <= 0.2)` - przerwa petli 211 ms (`03_f35_HEAD_7_FAIL.txt`); w udanych 25-97 ms |
| `main` `9ba9e91` | 30 | **29** | 1 | nieudany przebieg `main #4` z pierwszej serii - tresci bledu moj skrypt nie zapisal (**nie ustalono, ktora asercja**); w udanych 22-98 ms |

- Droga od zmian paczki do tego testu: `b93815e` zmienia tylko `testy/test_silnik.py` (`git diff --stat 2a6cac5..b93815e`:
  1 plik); `test_aplikacja_rano.py` importuje `test_kontroler_api` i `test_ui_wieczor`, nie `test_silnik`; `conftest.py` i
  `stanowisko/__init__.py` sa takie same jak w `2a6cac5`, na ktorym pelny pytest dal 1835 / 9 / 0 (35. wynik = kropka).
- **Wniosek: test czasowy wrazliwy na obciazenie PC; pada z podobna czestoscia na `main` bez paczki (1 z 30) i na HEAD
  (1 z 15). To nie jest skutek `b93815e` (ani kolejnosci importow w `conftest.py`, ani D1).** Czego nie wiem: ktora asercja
  padla w przerwanym przebiegu z 21:12 (pytest wypisuje tresc dopiero w podsumowaniu) i w moim nieudanym przebiegu na `main`.

### 2.2 Serie i krok 3 - wlasne liczenie z `serie.log` (87 wierszy, stan koncowy 20:52)

| Stan | Wariant | Udane (kod 0, 0 failed) | Zawieszenia | Naruszenia pamieci | Inne |
|---|---|---|---|---|---|
| przed poprawka | A | 6 z 6 (101a, 102a, 103a, 104a, 105a, 106a; 59 passed / 5 skipped) | 0 | 0 | 2 wiersze przerwane przez wykonawce i powtorzone |
| przed poprawka | B | 4 z 6 (101b, 102b, 103b, 106b) | 2 (104b, 105b) | 0 | - |
| po poprawce | B | **12 z 12 dokonczonych** (63 passed / 5 skipped kazdy) | 0 | 0 | 221, 222 w logu jako `ZAWIESZONY` przy 6,0 / 4,1 GB wolnego RAM - przerwane przez skrypt przy pracujacym procesie (ocena z rundy 1, p. 2.7); 201 urwany restartem PC |
| po poprawce | A | **4 z 5** | 0 | 0 | 229: 1 failed (`test_limit_czasu_zadania`), 62 passed |
| po poprawce, recenzent runda 1 + runda 2 | A | 2 z 2 (runda 2: 64 passed / 5 skipped, p. 2.4) | 0 | 0 | poza seria wykonawcy |

Krok 3 po poprawce (logi `p_235`, `p_236`, `p_237`; dzienniki `k3_po_B_stanowisko.log`, `k3_po_A_stanowisko.log` - wlasny `grep`):

| Uruchomienie | Wariant | `przyjety jako` | `proces silnika` | nieudany start procesu roboczego | wiersze ERROR | Kod programu |
|---|---|---|---|---|---|---|
| 235 + 236 | B (`Stanowisko.cmd`, srodowisko wersji) | 20 (10 + 10) | 0 | 0 | 0 | 0 i 0 |
| 237 | A (bazowy) | 10 | 0 | 0 | 0 | 0 |

Wszystkie liczby tabel p. 5.1 i 5.2 raportu paczki zgadzaja sie z logami. Kryterium "20 z 20" zlecenia nadal zastapione
progiem koordynatora 12 B / 4 A (bez zmian od rundy 1, p. 5). Krok 3: 1 uruchomienie A zamiast 2 (odstepstwo 5 w raporcie).

### 2.3 Testy paczki i wstrzykniecia (`runda2\wstrzykniecia2.sh`, log `05_wstrzykniecia.log`)

`narz\py.cmd -m pytest -q -p no:cacheprovider testy\test_silnik.py -k a11w`:

| Wariant | Wynik | Ocena |
|---|---|---|
| W0: HEAD bez zmian | 5 passed, 64 deselected | |
| **W1: blokada usunieta** (wywolanie `_bez_wmi()` w `stanowisko/__init__.py` -> `pass`) | **5 failed z 5** | wykryte |
| **W2: blokada po imporcie** (`conftest.py`: `import stanowisko` ZA `import trimesh`) | **1 failed** (`test_a11w_conftest_importuje_pakiet_przed_trimesh`: "...: 2"), 4 passed | wykryte - P2 zamknieta |
| W2b: `import numpy.testing` w `conftest.py` przed pakietem | 1 failed (ten sam test, 2 zapytania), 4 passed | wykryte |
| W2c: `import platform; platform.machine()` w `conftest.py` przed pakietem | 1 failed (ten sam test, 2 zapytania), 4 passed | wykryte |
| **W3: blokada tylko w procesie glownym** (po D1) | **1 failed** (`test_a11w_proces_roboczy_nie_laduje_wmi`), 4 passed | wykryte - po D1 test nadal wywoluje `platform.system()` w procesie roboczym |
| W3b: D1 cofniete (`platform.system()` w kazdym zadaniu probnym) | 5 passed | niewykrywalne z zalozenia (D1 to zmiana w funkcji probnej testow, nie w programie); skutek widac w czasie zadania, p. 2.4 |

**Wstrzykniecia: 3 z 3 wykryte** (W1, W2, W3); dodatkowe warianty P2: 2 z 2 wykryte.

### 2.4 Testy silnika po jednym pliku i wplyw D1

- Caly `testy\test_silnik.py`, interpreter bazowy, kopia recenzenta, przez `narz\ciezki.ps1 -Tor 4` (22:43:01-22:47:06,
  77,9 GB wolnego RAM): **64 passed, 5 skipped, 0 failed** w 242 s, kod 0, 0 wierszy `fatal exception` / `Fatal Python`
  (`06_test_silnik_A.log`). 64 = 63 z rundy 1 + 1 nowy test. Najdluzsze: przygotowanie
  `test_wynik_silnika_rowny_wierszowi_polecen[wieczorna]` 87,9 s, `test_pamiec_linii_na_dysku` 19,2 s.
- Czas szybkiego zadania w swiezym procesie roboczym (`proby\test_rec_czas.py` z rundy 1, po 6 pomiarow, `09_czas_zadania.log`):
  HEAD 0,109-0,110 s wg silnika, 0,050-0,064 s wg analizy; z cofnietym D1 0,156-0,187 s i 0,100-0,117 s. D1 przywraca
  sciezke czasowa sprzed paczki (runda 1: 0,094-0,110 s / 0,051 s).
- D1 a zwykla sciezka programu: zmiana jest w `testy/test_silnik.py` (`analiza_probna`); `stanowisko/silnik.py`, dziennik i
  samokontrola nie sa dotkniete. Jedyny uzytkownik pola `wynik["wmi"]` to `test_a11w_proces_roboczy_nie_laduje_wmi`.

### 2.5 Czy blokada WMI szkodzi kodowi, ktory potrzebuje `platform`

- `git grep` po `origin/e3/a11w` (`stanowisko/*.py`, `narzedzia/*.py`, `instalacja/*.py`): **0 wywolan** `platform.system` /
  `machine` / `release` / `version` / `win32_ver` / `platform` / `uname` / `node` / `processor` i 0 `import platform` - program
  sam z modulu `platform` nie korzysta (dziennik, raport metryk tez nie).
- `git show origin/e3/a11s:Ramki/stanowisko/stanowisko/samokontrola.py`: 0 wywolan `platform.*`; jest tylko `sys.platform`
  (znacznik `sys_platform` w liscie pakietow, wiersze 344-356) - blokada go nie dotyczy.
- Galaz `e3/a11i`: `platform` tylko w testach i w opisie pliku `.pth` (ta sama blokada wczesniej).
- Biblioteki (trimesh przy imporcie, `numpy.testing`): z blokada dostaja te same wartosci co bez niej - zmierzone w rundzie 1
  (p. 2.3 tamtego raportu: `system()`, `machine()`, `release()`, `version()`, `win32_ver()`, `platform()` identyczne);
  w rundzie 2 `__init__.py` sie nie zmienil, wiec pomiaru nie powtarzalem.
- `conftest.py` a inne pliki testow: w rundzie 2 bez zmian; `trimesh` nadal jest importowany w `conftest.py` (tylko pozniej niz
  pakiet), wiec nic, co polegalo na tym imporcie, nie traci go. Pelny pytest na `2a6cac5` z ta kolejnoscia: 1835 / 9 / 0.

### 2.6 Kod wyjscia 0xC0000409 procesu pytest po "0 failed" (raport paczki p. 8.2)

**Co sprawdzilem sam.**

| Pytanie | Wynik | Dowod |
|---|---|---|
| Ile zrzutow i jaki podpis | 10 plikow `python.exe.*.dmp` w `C:\Users\<konto-PC>\AppData\Local\CrashDumps`: 9 z 18.11 23:36 - 19.11 04:43 (galaz `e3/a11w` powstala 20.11), 1 z 20.11 20:33. Wlasne uruchomienie `proby\zrzut.ps1` na kazdym: **10 z 10** kod 0xC0000409, parametr 0x7, adres `ucrtbase.dll+0xA527E`; `Qt6Core.dll+0xEBFA6` i `Qt6Widgets.dll+0x502AC` na stosie w 10 z 10 | `08_zrzuty_rec.log` |
| Czy to watek glowny przy zamykaniu | Zapisany stos watku wyjatku ma 1,6-2,9 KB (zrzut z 20.11: 1648 bajtow), a jego dno to `python.exe` <- `kernel32` <- `ntdll` (log wykonawcy `p_404`): watek startowy procesu, bardzo plytko - poziom `main` interpretera, nie wnetrze wykonywanego testu. Razem z czasem (podsumowanie 20:33:30, koniec procesu 20:33:32) to zgodne z zamykaniem interpretera | `08_zrzuty_rec.log`, `p_404_zrzut_pytest_2a6cac5.log` |
| Czy da sie odczytac komunikat Qt ze zrzutu | **nie**: przeszukanie napisow (ASCII i UTF-16) w 3 zrzutach - sa tylko nazwy klas i arkusze stylow, zadnego komunikatu bledu Qt | `11_zrzut_napisy.log` |
| Dlaczego w logu pytest nie ma komunikatu Qt | proces bez okna konsoli nie wypisuje komunikatow Qt na przekierowane stderr: program `--atrapa --zamknij-po 3` -> 0 wierszy wyjscia (6 uruchomien); z `QT_FORCE_STDERR_LOGGING=1` albo `QT_ASSUME_STDERR_HAS_CONSOLE=1` -> 3 wiersze (ostrzezenie o czcionkach). Czy proces pelnego pytest koordynatora nie mial okna konsoli - **nie sprawdzilem** (prawdopodobne: startowal z sesji tak samo jak moje) | `07_aplikacja_kod.log` |
| Czy krotkie przebiegi daja ten kod | **nie, 0 z 59 procesow pytest (49 z oknem Qt)**: 45 x jeden test z oknem Qt (kody 0 albo 1), 3 x pliki testow Qt z `QT_FORCE_STDERR_LOGGING=1` (`test_aplikacja_rano.py` 28 passed; `test_ui_rano.py` 32 passed; `test_ui.py` + `test_ui_rozdzielczosc.py` 2 passed, 2 skipped - kody 0, 0 wierszy po podsumowaniu), 1 x caly `test_silnik.py` (kod 0), 7 x `-k a11w`, 2 x pomiar czasu zadania, 1 x `--collect-only`. Nowych zrzutow po 20:33 nie ma (odczyt 22:49) | `02`-`06`, `10_qt_kod_wyjscia.log` |
| Czestosc w pelnych przebiegach dzis | **2 z 5** z zapisanym kodem (`log\ciezkie.log`, `kolejka_pytest.log`): a11s 0, a11i 0, p14 0, a11w `2a6cac5` -1073740791, a11w `8cdc82d` -1073740791 (22:59:50, nowy zrzut `python.exe.13604.dmp` z tym samym podpisem - `12_zrzut_HEAD.log`). Oba przebiegi z kodem 0xC0000409 sa na tej galezi, 3 z kodem 0 na galeziach bez paczki | wlasny odczyt logow |
| Jakie procesy daly 9 zrzutow z 18-19.11 (raport paczki: "nie ustalono") | **pelne pytesty innych paczek, sprzed tej galezi: 9 z 9**. Czas kazdego zrzutu = czas ostatniego zapisu logu pelnego pytest w `<PC-katalog>\e3` + 1-3 s: 23:36:39 <- `a12\pytest_koniec_15ffe4a_r2.log` 23:36:37 (1513 passed); 23:54:50 <- `a10r2\pytest_r4.txt` 23:54:48; 00:49:47 <- `a5\logi\pytest_head_cae8e95.log` 00:49:44; 00:53:26 <- `a2p\pytest_koniec_e21b4f5.log` 00:53:25; 01:21:26 <- `a12\pytest_koniec_9fc88c5.log` 01:21:25; 01:34:41 <- `a2p\pytest_koniec_e21b4f5_3.log` 01:34:39; 02:14:31 <- `a5i\pytest_baza.log` 02:14:30; 03:29:02 <- `a5i\pytest_koniec_9da2eed.log` 03:29:01; 04:43:01 <- `t0p\logi\pytest_calosc_9c06276.log` 04:43:00. W oknie 18.11 23:36 - 19.11 04:43 skonczylo sie 14 pelnych pytestow (ponad 1200 testow): **9 z 14 ze zrzutem**, 5 bez. Wszystkie maja pelne podsumowanie (z 0 albo 1 failed). Katalog trzyma 10 zrzutow, wiec o przebiegach sprzed 23:36 nic nie wiadomo | `13_pytest_logi_18_19.txt`, daty plikow zrzutow |
| Czy program konczy sie tak samo | **nie zaobserwowano, 0 z 11**: 3 uruchomienia kroku 3 wykonawcy (2 przez `Stanowisko.cmd` w srodowisku wersji, kody 0 - sprawdzone w `p_235`-`p_237`) + moje 8 x `-m stanowisko.aplikacja --atrapa [--rano] --zamknij-po 3` interpreterem bazowym (kody 0) | `07_aplikacja_kod.log` |

**Ocena wniosku wykonawcy ("`abort()` wywolany przez Qt w watku glownym przy zamykaniu interpretera, zjawisko starsze niz paczka").**

- Ma pokrycie: `abort()` (kod + parametr 0x7 + adres w `ucrtbase`), watek glowny (dno stosu w `python.exe`), "po testach"
  (pelne podsumowanie w logu, 2 s do konca procesu, plytki stos), "starsze niz paczka" (9 zrzutow z 18-19.11 z tym samym
  podpisem - daty plikow i podpisy sprawdzilem sam).
- Jest wnioskiem, nie pomiarem: "wywolany przez Qt" i "blad krytyczny Qt (`qFatal`)". Stos jest PRZEGLADEM pamieci stosu
  bez symboli i bez odwijania ramek: adresy z `Qt6Core` leza najblizej wierzcholka, ale nazw funkcji nie ma. Raport paczki
  pisze to wprost ("nazwy funkcji i tresc komunikatu Qt nie ustalone") - sformulowanie jest uczciwe.
- Nie wiadomo: ktory obiekt Qt i jaki komunikat.
- **Czy paczka zmienia czestosc - napisane wprost.** Dzis z paczka 2 z 2 pelnych przebiegow z kodem 0xC0000409, bez paczki
  0 z 3. Samo to wygladaloby na skutek paczki. Przeciw: bez paczki, 18-19.11, **9 z 14** pelnych pytestow skonczylo sie
  tym samym zrzutem (wiersz wyzej), wiec zjawisko jest czeste takze bez niej (razem bez paczki 9 z 17, z paczka 2 z 2 -
  taka roznica przy tak malych liczbach nie odroznia niczego); podpis (te same adresy w `Qt6Core` i `Qt6Widgets`) jest
  identyczny w 11 z 11 zrzutow; paczka nie dotyka Qt; proces testow nie wysyla zapytan WMI (0 w `--collect-only` i 0 w
  7 testach silnika, runda 1 p. 2.4). Ocena: zjawisko niezalezne od paczki; ze paczka NIE podnosi czestosci - nie jest
  udowodnione pomiarem (kodu wyjscia pelnego pytest na samym `main` `9ba9e91` nikt nie zapisal).

**Ryzyko dla testu koncowego T1 (kryterium 0 failed, 0 errors).** Wynikom testow nie zagraza: zdarzenie nastepuje po
wypisaniu pelnego podsumowania (11 z 11 logow przy zrzutach ma pelne podsumowanie). Zagraza ocenie po kodzie wyjscia, i to
CZESTO, nie rzadko: przebieg z 0 failed konczy sie kodem -1073740791 w ok. polowie pelnych przebiegow (9 z 14 w nocy
18 / 19.11, 2 z 5 dzis). T1 trzeba wiec oceniac po wierszu podsumowania ORAZ osobno zapisac kod; przy 0xC0000409 sprawdzic podpis
nowego zrzutu (`proby\zrzut.ps1`). W srodowisku wersji zjawiska **nikt nie mierzyl** (ten sam PySide6, wiec mozliwe).
Drugie, niezalezne ryzyko dla "0 failed": testy czasowe petli okna (p. 2.1: ok. 1 nieudany na 22 uruchomienia jednego testu,
takze na `main`) i `test_limit_czasu_zadania` (przebieg 229).

**Ryzyko dla technika.** Wiadomo: (1) program zamykany zegarem (`--zamknij-po`) przy Qt `offscreen` skonczyl sie kodem 0 w
11 z 11 uruchomien, w tym 2 przez `Stanowisko.cmd` w srodowisku wersji; (2) `main()` programu przed powrotem wola
`lacznik.zatrzymaj()` i `kontroler.zamknij()` (`aplikacja.py`:1717-1720), a dziennik w kroku 3 ma wiersz `zamkniete, zadan
niezakonczonych 0` - gdyby `abort()` nastapil przy zamykaniu interpretera, to juz PO zamknieciu silnika, skanera i bazy przez
program (wniosek z kodu, nie pomiar); (3) wzor `Stanowisko.cmd` z galezi `e3/a11i` konczy sie wierszem
`if not "%KOD%"=="0" if "%~1"=="" pause` - po starcie dwuklikiem kazdy kod inny niz 0 i 3 zostawia czarne okno konsoli
czekajace na klawisz, bez wyjasnienia. Nie wiadomo: czy program zamykany PRZEZ CZLOWIEKA (krzyzyk okna) na PRAWDZIWYM ekranie
(wtyczka `windows`, nie `offscreen`) po dlugiej sesji konczy sie zawsze kodem 0 - takiego uruchomienia nie zrobil ani
wykonawca, ani ja (sesja bez ekranu). Proces programu rozni sie od procesu pytest (jedno okno i jeden `QApplication`,
ktorych zmienne gina przy powrocie z `main()`, wobec obiektow Qt pozostawionych przez ok. 15 plikow testow do konca
interpretera), wiec z "pelny pytest konczy sie tak w ok. polowie przebiegow" NIE wynika "program pada" (krotkie przebiegi
pytest: 0 z 59); ale wykluczone to nie jest. Skutek, gdyby
wystapilo: okno konsoli z "Press any key" po zamknieciu programu i plik w `CrashDumps`; utraty danych nie przewiduje
(punkt 2). To trzeba zmierzyc w T2 - p. 5.

### 2.7 Zakres plikow rundy 2

`git diff 2a6cac5..origin/e3/a11w --numstat`: `testy/test_silnik.py` +29 -3, `opisy_modulow/silnik.md` +19 -3, raport
(reszta). `stanowisko/__init__.py` i `testy/conftest.py`: 0 zmian w rundzie 2.

### 2.8 Raport paczki a logi

- Tabele 5.1 / 5.2 - zgodne z logami (p. 2.2). P. 8.1: przerwany przebieg `b93815e` opisany poprawnie (1261 wynikow:
  1258 passed, 2 skipped, 1 failed - przeliczone z logu). P. 8.1.1: ten sam test co u mnie; liczby powtorek wykonawcy 5 + 5
  z `p_502_k3_excel_HEAD_main_5x.log` zgodne z logiem (10 x kod 0); moje powtorki pokazuja, ze test pada takze osobno (D6).
- Sekcja 10 (Runda 1): `p_401` kod 0, `p_402` kod 1, `p_403` kod 1 (ostatnie wiersze logow) - zgodne z moimi W0, W2, W3.

### 2.9 Pelny pytest na HEAD i commity, ktore doszly w trakcie recenzji

- `ce12ffe` (22:4x, sam raport: p. 8.1 wiersz przerwanego przebiegu + nowy p. 8.1.1): przejrzany, liczby zgodne z logami (p. 2.8).
- Pelny pytest wykonawcy na `8cdc82d` (kod i testy = `b93815e`; tor 1, 22:34:05-22:59:50), wlasny odczyt
  `robocze\a11w\logi\pytest_pelny_8cdc82d.log` i `log\ciezkie.log`: **1836 passed, 9 skipped, 0 failed, 0 errors**, 1 warning,
  1540,86 s; 0 liter `F` / `E` w wierszach postepu (35. wynik = kropka); 1836 = 1831 (`main`) + 5 testow `a11w`.
  **Kod wyjscia procesu -1073740791 (0xC0000409)** - po podsumowaniu (ostatni zapis logu 22:59:48, zrzut 22:59:49, `KONIEC`
  22:59:50), podpis zrzutu jak w p. 2.6.
- Ostatni `git fetch origin` 23:05: `origin/e3/a11w` = `ce12ffe` - commitu z wynikiem tego przebiegu jeszcze nie ma; raport paczki ma 4 wiersze "W TOKU" (532 wynik i kod HEAD, 616 ocena, 727 sprzatanie, 745 nowy test w srodowisku wersji). To jedyna otwarta reszta P1. Jesli wykonawca dopisze wynik commitem samego raportu, koordynator sprawdza: 1836 / 9 / 0, kod -1073740791, `git diff ce12ffe..HEAD --stat` = tylko raport.


## 3. Kryteria zlecenia

| Nr | Kryterium | Ocena po rundzie 2 |
|---|---|---|
| 1 | Przyczyna nazwana i pokazana eksperymentem wlacz / wylacz | **potwierdzone wlasna proba** (runda 1, p. 2.2: 3 z 3 wobec 0 z 3) - bez zmian; zastrzezenia z rundy 1 aktualne ("dlaczego B czesciej niz A" - nie ustalono) |
| 2 | Po poprawce `test_silnik.py` w srodowisku wersji bez zawieszen i naruszen pamieci; krok 3: wszystkie plytki, 0 zawieszen | **potwierdzone przegladem logow** w wersji koordynatora: B 12 z 12 dokonczonych, 0 zawieszen, 0 naruszen pamieci; krok 3: B 20 plytek z 20 w 2 uruchomieniach, A 10 z 10, 0 restartow silnika (p. 2.2). "20 z 20" ze zlecenia - nie (12); przebiegow w srodowisku wersji sam nie uruchamialem |
| 3 | Rekomendacja T1 / T2 | **potwierdzone przegladem** (runda 1) + dopisana ocena po kodzie wyjscia (raport p. 7, 8.2); uzupelnienia w p. 5 nizej |
| 4 | Testy, ktore bez poprawki padaja; pelny pytest 0 failed | testy: **potwierdzone wlasna proba** - W1 5 z 5, W2 (kolejnosc w `conftest.py`) 1 z 5, W3 1 z 5 (p. 2.3); pelny pytest: **potwierdzone przegladem logu** - `8cdc82d`: 1836 passed / 9 skipped / 0 failed / 0 errors (p. 2.9); w raporcie paczki jeszcze nie wpisane (P1 - reszta); kod wyjscia procesu 0xC0000409 po podsumowaniu - zjawisko spoza paczki (p. 2.6) |
| 5 | Galaz wypchnieta | potwierdzone przegladem (`origin/e3/a11w` = `ce12ffe`) |

## 4. Zakres plikow i zasady

- `git diff main...origin/e3/a11w --stat`: 5 plikow - `opisy_modulow/silnik.md`, `raporty/E3-A11w_2026-11-20.md`,
  `stanowisko/__init__.py`, `testy/conftest.py`, `testy/test_silnik.py`. Poza lista zlecenia nadal tylko `stanowisko/__init__.py`
  i `testy/conftest.py` (ocena z rundy 1: konieczne i najmniejsze mozliwe, uzasadnione w raporcie p. 4); w rundzie 2 oba bez zmian.
- Pliki nietykalne (`match.py`, `inspect.py`, `plate.py`, `synth.py`, `uklad.py`, `modele_plytek/**`, progi, `raporty/testy_krawedz/**`):
  nietkniete (0 trafien w liscie plikow). Schemat bazy: 0 wierszy diffu z `WERSJA_SCHEMATU` / `MIGRACJE`. Brak nowych pakietow
  i duzych danych.
- ASCII: 0 dodanych wierszy ze znakami spoza ASCII (runda 2 i calosc `main...HEAD`). Konce linii: `git ls-files --eol` dla
  5 plikow `i/lf w/lf`.
- Commity rundy 2: 5 (`b93815e`, `9ecb752`, `58978ba`, `8cdc82d`, `ce12ffe`), wszystkie z przedrostkiem `E3-A11w:` i stopka
  `Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>`.
- Dane osobowe: w dodanych wierszach rundy 2 brak nazw zlecen, folderow prac i osob; sa sciezki konta `<konto-PC>`, nazwy
  testow, numery przebiegow.
- Uczciwosc raportu paczki: liczniki zamiast procentow; przebiegi 221 / 222 / 229 / 201 i przerwany pytest `b93815e` opisane
  jako nie-wyniki; "nie ustalono" / "nie zmierzono" pisane wprost; zaden test nie pominiety ani oslabiony (D1 zmienia funkcje
  probna testow tak, by pozostale testy mialy sciezke jak na `main`).
- Kopia recenzenta po probach: `git status --short` pusty (poza ignorowanym `ustawienia.toml`); `main` w `<PC-katalog>\qc` -
  tylko uruchamiany, `git status --short` pusty.

## 5. Do decyzji wlasciciela (nie blokuje)

1. **T2 ma zmierzyc zamykanie programu na prawdziwym ekranie.** Wszystkie dotychczasowe zamkniecia programu (11 z 11 z
   kodem 0) byly przy Qt `offscreen` i przez zegar `--zamknij-po`. Propozycja: w T2 co najmniej 10 zamkniec krzyzykiem okna
   programu uruchomionego przez `Stanowisko.cmd` na zwyklym pulpicie, z zapisem `%errorlevel%` i sprawdzeniem, czy w
   `%LOCALAPPDATA%\CrashDumps` nie przybyl plik. Jesli kod inny niz 0 sie zdarzy: technik zobaczy po zamknieciu czarne okno
   "Press any key" (`pause` we wzorze `Stanowisko.cmd`, paczka A11i) - wtedy decyzja, czy wzor ma to okno pokazywac.
2. **T1: ocena po wierszu podsumowania i osobno po kodzie wyjscia** (zalecenie wykonawcy, popieram). Kryterium "0 failed,
   0 errors" czytac z podsumowania; kod 0xC0000409 po pelnym podsumowaniu = znane zjawisko zamykania (sprawdzic podpis
   zrzutu), zapisac jako odstepstwo. Czestosc dzis: 2 z 5 pelnych przebiegow z zapisanym kodem (oba na tej galezi); w nocy 18 / 19.11, przed paczka, 9 z 14 (p. 2.6).
3. **Tresc komunikatu Qt mozna zlapac tanio**: jeden dodatkowy pelny przebieg (nie T1) z `set QT_FORCE_STDERR_LOGGING=1` -
   bez okna konsoli Qt nie pisze na przekierowane stderr (p. 2.6, D7). Osobna mala paczka naprawcza - po poznaniu komunikatu.
4. **Testy czasowe petli okna** (`Petla`, prog 0,2 s): `test_k3_excel_pytaj_...` pada osobno ok. 1 raz na 22 uruchomienia,
   tak samo na `main` (p. 2.1); do tego `test_limit_czasu_zadania` (przebieg 229). Przy T1 mozliwy pojedynczy falszywy
   "failed" - procedura z `wspolne.md` (powtorka osobno 5 razy); decyzja, czy poluzowac progi osobna paczka.
5. Punkty 1-4 z rundy 1 bez zmian: "20 z 20" zastapione progiem 12 B / 4 A; kroki 1 i 2 zlecenia skrocone; nie wiadomo, czy
   na komputerze stanowiska WMI przekracza limit (poprawka jest tam nieszkodliwa); narzedzia z `narzedzia/` i `pip` chroni
   dopiero plik `.pth` z PR #39.
6. D4 (bezwarunkowe `sys.modules["_wmi"] = None`) i docstring z D2 odlozone przez wykonawce - mozna zrobic przy okazji
   nastepnej zmiany w `stanowisko/__init__.py`; dzis bez skutku dla technika.

WERDYKT: do scalenia po poprawkach (B 0 / P 1 / D 5): P1 reszta - wpisac do raportu paczki wynik pelnego pytest na HEAD (w logu 1836 passed / 9 skipped / 0 failed, kod wyjscia 0xC0000409) i usunac znaczniki "W TOKU"; kod bez zmian, P2 zamknieta.
