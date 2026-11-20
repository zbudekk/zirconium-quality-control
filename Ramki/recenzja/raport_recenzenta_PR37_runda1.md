# Raport recenzenta - PR #37 (E3-T0d), runda 1

- Data: 20.11.2026.
- Zakres: `git -C <PC-katalog>\qc diff main...e3/t0d`, `main` = `bf00921`, HEAD = `8a25455` (4 commity: `6b7b4b1`,
  `1df5d6c`, `e3eefda`, `8a25455`). 4 pliki, +256 / -4.
- Metoda: wlasny przeglad diffu, potem wlasne proby w kopii `<PC-katalog>\qc-wt\rec-t0d` (detached na `8a25455`),
  raport wykonawcy czytany na koncu. Kod psuty tylko w tej kopii i po kazdej probie przywracany (na koncu
  `git status --short` pusty, `baza.py` bajt w bajt rowny HEAD). Niczego nie commitowano. Worktree wykonawcy i repo
  glowne tylko czytane. Jeden proces python naraz.
- Uruchomiono: `testy/test_baza.py` na HEAD; 6 wstrzykniec bledu (I0-I6, w tym powrot do `filecmp`); petle 200 i 1000
  przebiegow testow `test_d2*` na kodzie starym i nowym; skrypt przypadkow brzegowych (dlugosci, puste pliki, bajt na
  granicach bloku 1 MB, 2 x 96 MB z pomiarem pamieci, plik zablokowany, plik zmieniany w trakcie, kilka kopii);
  skrypt zliczajacy "ten sam mtime a liczba kopii" (1000 prob na kod). Pelnego pytest nie powtarzano (zasada 3).
- Pliki robocze i logi: `<PC-katalog>\koordynator\robocze\rec-t0d\`.

## 0. Werdykt i liczby

**Do scalenia.** B 0 / P 0 / D 3.

Poprawka jest poprawna i minimalna, przyczyna potwierdzona moim pomiarem (takze naturalna porazka starego testu na
starym kodzie, ktorej wykonawca nie zdolal wywolac), test deterministyczny pada na starym kodzie 200 z 200, stary
`test_d2` nie zostal zmieniony, poza zleconym minimum nic sie nie zmienilo.

## 1. Uwagi

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| 1 | D | `testy/test_baza.py:470` (`test_d2_porownanie_tresci_idzie_blokami_i_nie_pamieta_wyniku`) | Nazwa i opis testu mowia "idzie blokami", ale test nie sprawdza, ze odczyt jest ograniczony do bloku. Wstrzykniecie I5 (na poczatku pomocnika `return a.read_bytes() == b.read_bytes()`, czyli cala baza w pamieci): `test_baza.py` 70 passed, 0 failed. Druga polowa kryterium 2 ("bez wczytywania calej bazy naraz") jest wiec spelniona w kodzie (przeglad + moj pomiar pamieci), ale zaden test jej nie pilnuje. | Przy okazji: w tescie podmienic `B.open` na owijke liczaca najwiekszy argument `read` i wymagac `<= _BLOK_POROWNANIA` (albo liczby odczytow > 1 dla pliku 50 bajtow przy bloku 7). Nie blokuje scalenia. |
| 2 | D | `raporty/E3-T0d_2026-11-20.md:99` i `:147` | Raport podaje "w pamieci naraz najwyzej 2 bloki (2 MB)". Pomiar (`tracemalloc`, 2 pliki po 96 MB): szczyt 4,02 MB - przy `blok_a, blok_b = fa.read(...), fb.read(...)` (`baza.py:359`) stara para blokow zyje do konca odczytu nowej pary, wiec naraz sa do 4 blokow. Bez znaczenia dla programu (4 MB zamiast 2 MB), nieprawdziwa jest tylko liczba w raporcie. | Poprawic liczbe w raporcie na "do 4 blokow (4 MB)" przy najblizszej okazji; kodu nie ruszac. |
| 3 | D | `opisy_modulow/baza.md:45` | Dopisane zdanie mowi, ze tresc jest porownywana "przy kazdym otwarciu". Porownanie dziala tylko wtedy, gdy baza wymaga migracji i obok lezy kopia tej samej wersji (`baza.py:430-433`, `:368`); zwykle otwarcie bazy w biezacej wersji niczego nie porownuje. Czytelnik opisu moze uznac, ze kazdy start programu czyta cala baze dwa razy. | Zamienic na "przy kazdej probie migracji" (jedno slowo w tym samym zdaniu). |

Uwag B i P nie ma.

## 2. Wlasne proby

Polecenia z katalogu `<PC-katalog>\qc-wt\rec-t0d\Ramki\stanowisko`; `py.cmd` = `<PC-katalog>\koordynator\narz\py.cmd`;
`R` = `<PC-katalog>\koordynator\robocze\rec-t0d`. "Stary kod" = HEAD z przywroconym `import filecmp` i wierszem
`if filecmp.cmp(istniejaca, plik, shallow=False):` (wariant I0; `diff` wobec `baza.py` z `main` pokazuje tylko 20
dodanych wierszy nieuzywanego pomocnika, czyli porownanie jest dokladnie takie jak na `main`).

### 2.1 Testy paczki i wstrzykniecia bledu

| Nr | Stan kodu | Polecenie | Wynik |
|---|---|---|---|
| a | HEAD `8a25455` | `py.cmd -m pytest -q -p no:cacheprovider testy/test_baza.py` | 70 passed, 0 failed |
| b | I0: stare porownanie `filecmp` | jak (a) | 2 failed, 68 passed: nowy test deterministyczny (`assert 0 == 1`, "baza o zmienionej tresci nie dostala nowej kopii przed migracja") i `test_modul_bazy_tylko_biblioteka_standardowa` (wrocil import `filecmp`) |
| c | I0 | `py.cmd R\powt.py 200 -q -p no:cacheprovider testy/test_baza.py -k test_d2 --tb=no -rf` (3 testy x 200 w jednym procesie) | przebieg 2: 200 failed, 400 passed; wszystkie 200 to nowy test deterministyczny (200 z 200). Przebieg 1 (bez listy nazw): 201 failed, 399 passed - 201. porazki nie przypisano do testu |
| d | I0 | `py.cmd R\powt.py 1000 ... -k test_d2_kolejne --tb=line -rf` (sam STARY test, 1000 razy) | **10 failed, 990 passed**; wszystkie 10: `test_baza.py:430`, `assert 1 == 2` - ta sama porazka co w logu ze zlecenia |
| e | HEAD | jak (d) | **1000 passed**, 0 failed |
| f | HEAD | jak (c), `--tb=short` | **600 passed**, 0 failed (zebrane: 200 + 200 + 200 pozycji trzech testow `test_d2*`) |
| g | I1: porownanie samego rozmiaru (`if False:` zamiast `if blok_a != blok_b:`) | jak (a) | 3 failed, 67 passed: stary `test_d2`, nowy deterministyczny, test pomocnika |
| h | I2: porownanie tylko pierwszego bloku | jak (a) | 1 failed, 69 passed: test pomocnika, `(49, 7)` - roznica w drugim bloku |
| i | I3: nigdy "identyczne" (utrata zachowania "identyczna kopia juz jest = zwroc ja") | jak (a) | 2 failed, 68 passed: stary `test_d2` (`3 == 1` kopii) i nowy deterministyczny (`2 == 1`) |
| j | I5: cala tresc do pamieci (`read_bytes`) | jak (a) | 70 passed - test tego nie widzi (uwaga 1) |
| k | I6: bez sprawdzenia "zwykly plik" i rozmiaru | jak (a) | 1 failed, 69 passed: test pomocnika (`PermissionError` przy katalogu) |

Wniosek: test deterministyczny naprawde pada na starym kodzie (200 z 200) i przechodzi na nowym (200 z 200); stary
`test_d2` nadal pilnuje obu stron zachowania (I1: brak nowej kopii po zmianie bazy; I3: mnozenie kopii).

### 2.2 Przyczyna: ten sam mtime a liczba kopii

`py.cmd R\proba_mtime.py 1000 R\tmp_...` - kroki starego `test_d2` 1000 razy w jednym procesie, bez `os.utime`,
z zapisem: czy `st_mtime_ns` bazy po dopisaniu wiersza jest taki jak przed, ile kopii na koncu.

| Kod | ten sam mtime | rozmiar ten sam | kopii na koncu | prob |
|---|---|---|---|---|
| stary (I0) | nie | tak | 2 (dobrze) | 850 z 1000 |
| stary (I0) | **tak** | tak | **1 (blad)** | **150 z 1000** |
| HEAD | nie | tak | 2 (dobrze) | 836 z 1000 |
| HEAD | tak | tak | 2 (dobrze) | 164 z 1000 |

Na starym kodzie blad wystapil w 150 z 150 prob z tym samym mtime i w 0 z 850 pozostalych; na HEAD 164 z 164 prob
z tym samym mtime dostalo nowa kopie. To pomiar naturalny (bez symulacji zegara): w czasie moich prob ten sam mtime
zdarzal sie sam. Uzupelnia punkt 3.3 raportu wykonawcy ("naturalnej porazki nie udalo sie wywolac") - razem z proba
(d) / (e) kryterium 3 rozroznia kod przed i po poprawce.

### 2.3 Przypadki brzegowe porownania (`py.cmd R\proba_brzegi.py R\tmp_brzegi`, logi `proba_brzegi_HEAD.log`, `proba_brzegi_stary.log`)

| Nr | Proba | HEAD | Stary kod (I0) |
|---|---|---|---|
| 1 | 12 par dlugosci (0 i 0, 0 i 1, 1 i 0, 1 MB +/- 1, 1 MB i 1 MB + 1, 2 MB i 2 MB - 1, 3 MB + 5 ...) | zlych 0 z 12; dwa puste = identyczne, pusty i niepusty = rozne | zlych 0 z 12 |
| 2 | jeden bajt inny przy tym samym rozmiarze i przywroconym mtime; 7 dlugosci (1 bajt do 3 MB + 5), pozycje: 0, srodek, 1 MB - 1, 1 MB, 1 MB + 1, 2 MB - 1, 2 MB, ostatni; w obu kolejnosciach argumentow | zlych 0 z 30 | zlych 30 z 30 (pamiec `filecmp`) |
| 3 | 2 pliki po 96 MB: identyczne, potem ostatni bajt inny | `True` w 0,05 s (pliki w pamieci podrecznej systemu), szczyt pamieci 4,02 MB; ostatni bajt inny -> `False` | nie mierzono |
| 4 | katalog zamiast pliku / brak pliku | `False` / `False` | `False` / `FileNotFoundError` |
| 5 | blad odczytu: plik otwarty przez inny uchwyt bez wspoldzielenia | `PermissionError` (obie kolejnosci argumentow) | `PermissionError` |
| 6 | caly `otworz`: po nieudanej migracji kopia zablokowana, kolejne otwarcie | `PermissionError`; kopii nadal 1, plik bazy bajt w bajt bez zmian, wersja 1 (migracja nie ruszyla) | to samo |
| 7 | 2 kopie tej wersji: pierwsza (wg nazwy) inna przy tym samym rozmiarze i mtime, druga identyczna | zwraca druga, trzeciej nie robi (kopii 2) | to samo |
| 8 | pusty plik o nazwie kopii obok niepustej bazy | nowa kopia rowna bazie (kopii 2) | to samo |
| 9 | plik zmieniany w trakcie porownania (blok 4 bajty, zmiana po drugim odczycie): a) bajt w czesci jeszcze nie czytanej, b) dopisanie na koncu, c) bajt w czesci juz przeczytanej, d) skrocenie | a) `False`, b) `False`, c) `True`, d) `False` | nie mierzono |

Odpowiedzi na pytania koordynatora:

- Rozna dlugosc: `False` bez czytania tresci (rozmiar z `stat`); gdyby rozmiar zmienil sie po `stat`, petla i tak konczy
  `False` (krotszy plik oddaje krotszy albo pusty blok - proba 9b, 9d). Puste pliki: dwa puste = identyczne.
- Blad odczytu: **wyjatek, nie nowa kopia** - `PermissionError` wychodzi z `otworz`, migracja nie rusza, baza bez zmian
  (proba 6). Tak samo zachowuje sie `main` (kolumna "stary kod"), wiec paczka tego nie zmienia. To wariant bezpieczny
  (zadnej migracji bez potwierdzonej kopii). Jedyna roznica wobec `main`: kopia, ktora znikla miedzy wyszukaniem
  a porownaniem, daje `False` (nowa kopia) zamiast `FileNotFoundError` - bezpieczne.
- Plik zmieniany w trakcie: zmiana w czesci juz przeczytanej nie moze byc zauwazona (9c) - to cecha kazdego
  porownania bez blokady pliku, `filecmp` mial ja tak samo; kopia powstaje przy zamknietym polaczeniu (stan sprzed
  paczki, opisany w `baza.md`). Paczka tego nie pogarsza.
- "Identyczna kopia tej wersji juz jest = zwroc ja": zachowane (proby 7, I3, stary `test_d2`: 1 kopia po 3 probach).
- `BufferedReader.read(n)` dociaga do `n` bajtow albo konca pliku, wiec krotki odczyt z dysku nie daje falszywej
  roznicy (przeglad; nie proba).

## 3. Kryteria zlecenia

| Nr | Kryterium | Ocena |
|---|---|---|
| 1 | przyczyna potwierdzona pomiarem; test deterministyczny pada zawsze przed poprawka, przechodzi po | **potwierdzone wlasna proba**: 2.1 c (200 z 200 failed na starym kodzie), f (200 z 200 passed), 2.2 (150 z 150 prob z tym samym mtime = blad na starym kodzie, 164 z 164 dobrze na HEAD), 2.3 nr 2 (`filecmp` 30 z 30 zle). Przyczyna to pamiec `filecmp`, innej nie znalazlem |
| 2 | porownanie tresci bez pamieci zaleznej od mtime, bez wczytywania calej bazy naraz | **potwierdzone wlasna proba**: 2.3 nr 2 (0 z 30 zlych przy tym samym rozmiarze i mtime), nr 3 (szczyt 4,02 MB dla 2 x 96 MB). Test paczki pilnuje pierwszej polowy; drugiej nie (uwaga 1, D) |
| 3 | 200 przebiegow `test_d2` + nowego testu: 200 z 200 | **potwierdzone wlasna proba**: 2.1 f (600 passed z 600), dodatkowo e (stary test 1000 z 1000 na HEAD wobec 990 z 1000 na starym kodzie) |
| 4 | caly `test_baza.py` 0 failed | **potwierdzone wlasna proba**: 70 passed, 0 failed |
| 4 | pelny pytest 0 failed | **wg wykonawcy, niesprawdzone przebiegiem**: 1831 passed / 9 skipped / 0 failed wobec 1829 / 9 / 0 punktu odniesienia; odczytalem tylko ostatnie wiersze obu logow (`robocze\t0d\07_pytest_calosc_e3eefda.log`, `log\pytest_bazowy_bf00921.log`) - liczby zgodne z raportem, roznica +2 = 2 nowe testy. Przebieg na `e3eefda`; po nim doszedl tylko plik raportu |

Dodatkowe warunki zlecenia:

- "istniejacego `test_d2` nie oslabiaj": **potwierdzone przegladem** - w diffie `test_baza.py` jest 1 wiersz usuniety
  (lista dozwolonych importow w `test_modul_bazy_tylko_biblioteka_standardowa`, zaostrzona o brak `filecmp`), tresc
  `test_d2_kolejne...` (wiersze 413-430) bez zmian; zadnego skip / xfail.
- "testy najpierw": commit `6b7b4b1` zawiera sam test (1 plik, +38), poprawka w nastepnym `1df5d6c`.
- Testy pisza tylko do `tmp_path`, bez internetu: potwierdzone przegladem.

## 4. Zakres plikow i zasady

- Zmienione pliki (4) = lista ze zlecenia: `stanowisko/baza.py` (+21 / -2), `testy/test_baza.py` (+68 / -1),
  `opisy_modulow/baza.md` (1 wiersz: dopisane jedno zdanie), `raporty/E3-T0d_2026-11-20.md` (nowy, 166 wierszy).
- `baza.py`: zmiana ogranicza sie do usuniecia `import filecmp`, stalej `_BLOK_POROWNANIA`, pomocnika `_ta_sama_tresc`
  i jednego wiersza w `_kopia_przed_migracja`. Schemat, `WERSJA_SCHEMATU`, `MIGRACJE`, wzorzec i budowa nazw kopii
  (`<nazwa>.kopia_v<wersja>_<znacznik>[_n].sqlite`), `shutil.copy2`, `otworz`, `_migruj` - bez zmian (przeglad diffu).
- Pliki nietykalne: nie ruszone. Nowych pakietow brak (modul nadal tylko biblioteka standardowa - test (a)).
- ASCII / konce linii: 0 znakow spoza ASCII w dodanych wierszach; wszystkie 4 pliki LF (0 znakow CR), `git diff --check` czysty.
- Dane osobowe i duze dane: w diffie brak nazw zlecen i folderow; dane testowe sztuczne (`skan_x.stl`, `skan_y.stl`);
  najwiekszy nowy plik to raport (12 752 bajty).
- Commity: 4, przedrostek `E3-T0d:`, po polsku bez znakow diakrytycznych, kazdy ze stopka `Co-Authored-By`.
  Worktree wykonawcy: `git status --short` pusty, HEAD `8a25455`.
- Raport wykonawcy: liczby, ktore powtorzylem, zgadzaja sie z moimi (70 passed; 200 z 200 failed przed; 600 passed po);
  jedna liczba niescisla (uwaga 2). Raport sam wymienia odstepstwa i to, czego nie zmierzono.

## 5. Do decyzji wlasciciela (nie blokuje)

1. Komunikat przy bledzie odczytu kopii (stan sprzed paczki, poza jej zakresem): gdy kopia sprzed migracji jest
   zajeta przez inny program (np. kopia zapasowa albo antywirus), start konczy sie surowym
   `[Errno 13] Permission denied: '<sciezka kopii>'`, a nie zdaniem po polsku jak pozostale bledy bazy (`BladBazy`).
   Dane sa bezpieczne (migracja nie rusza). Do rozwazenia w osobnej paczce: komunikat dla technika albo zrobienie
   nowej kopii zamiast przerwania.
2. `opisy_modulow/baza.md`, "Kryterium dziala", podaje "45 testow"; `test_baza.py` ma 70 (68 przed paczka). Wykonawca
   to zauwazyl i zgodnie ze zleceniem nie poprawial. Do poprawienia przy okazji.
3. Znaczenie bledu na stanowisku (wg wykonawcy, sprawdzone przeze mnie tylko wyszukaniem wywolan `otworz` - 6 miejsc,
   bez ponawiania w tym samym procesie): pamiec `filecmp` zyje w jednym procesie, a program otwiera baze raz na
   start, wiec u technika blad mial male szanse wystapic; poprawka jest mimo to wlasciwa i nic nie kosztuje.
