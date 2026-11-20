# Raport recenzenta - PR #38 (E3-A11s, samokontrola programu), runda 2

- Data: 20.11.2026, PC, konto `<konto-PC>`. Recenzja przyrostowa po poprawkach wykonawcy.
- Zakres: `git -C <PC-katalog>\qc diff c67fbe5..e3/a11s` na 4 plikach paczki, HEAD `6befc0d` (commity `8d27ecb`, `0aa0df8`, `337d369`,
  `665dfac`, `6befc0d`; `9d556e9` = wciagniecie `main`). Calosc `git diff main...e3/a11s --stat`: 4 pliki, 3681 linii - tylko pliki paczki.
- Recenzja robiona przez dwoch recenzentow: pierwszy pracowal 18:30-18:49 i zginal przy restarcie PC, drugi przejal prace 19:08-19:40.
  Liczby pierwszego (testy paczki, proby B1, P1, P2, P3, decyzje koordynatora, POTRZEBUJE, serie e1-e4) sa ponizej oznaczone "[poprz.]":
  pochodza z jego logow przeczytanych w calosci przez drugiego recenzenta; wyrywkowo powtorzono B1 (zgodne). Reszta to pomiary drugiego.
- Metoda: przeglad diffu modulu, proby w kopii `<PC-katalog>\qc-wt\rec-a11s` (detached `6befc0d`), pliki robocze i logi
  `<PC-katalog>\koordynator\robocze\rec-a11s\runda2\`. Naraz 1 proces python. Pelnego pytest nie powtarzano.
- Uruchomiono: testy paczki [poprz.]; skrypty prob `r2_1.py` [poprz.], `r2_c.py`, `r2_c5.py`, `r2_d.py`; 15 wstrzykniec bledu z plikiem
  testow po kazdym (`mut.py`, `q.sh`); 76 uruchomien prawdziwego procesu samokontroli w 3 seriach na przemian stary / nowy modul, z blokada
  `_wmi` i bez (`a1.sh`, `wmi_wrap.py`) oraz 122 uruchomienia w seriach poprzednika (e1-e4). Kopia recenzenta po probach czysta
  (`git status --short --ignored` pusty, HEAD `6befc0d`).

## 0. Werdykt

**Do scalenia.** B 0, P 0, D 2 (nowe). Uwagi rundy 1: B1, P1-P5 zamkniete (6 z 6), D1-D5 zamkniete (5 z 5). 4 decyzje koordynatora wdrozone (4 z 4).

Warunek kolejnosci dla koordynatora (uwaga D6, sprawa miedzy paczkami): **scal E3-A11w (blokada `_wmi` w `stanowisko/__init__.py`) przed
PR #38 albo razem z nim** i po scaleniu powtorz serie `a1.sh` (oczekiwane 0 awarii). Bez poprawki A11w na PC proces samokontroli rundy 2
ginie z kodem 0xC0000005, gdy zyje dluzej niz ok. 5 s po `import trimesh` (9 z 13 przebiegow; kod rundy 1 w tych samych warunkach
0 z 13), a test paczki `test_polecenie_modulu_w_osobnym_procesie` pada przy obciazonym PC (2 z 13 przebiegow tego testu). Zmiany
w plikach PR #38 to nie wymaga - z blokada `_wmi` awarii 0 z 13.

Poprawki rundy 2 sa rzetelne: poziom BLAD idzie za folderem puli faktycznie uzywanym przez program (wywolanie metody programu, bez
okna i bez zapisu), diagnoza bazy rozroznia "niedostepna" od "uszkodzona", komunikaty kodu 2 nie pokazuja osob, limity czasu dzialaja
i nie daja falszywej zieleni, umowa wywolania jest co do pola taka sama jak w rundzie 1, a testy wykrywaja 15 z 15 wstrzyknietych bledow
(runda 1: 3 z 7).

## 1. Uwagi

### 1.1. Uwagi rundy 1 - stan

| Nr | Stan | Dowod |
|---|---|---|
| B1 | zamknieta | (a) pula wybrana w programie z 3 plikami STL, `folder_cyrkon` nie istnieje: kod 0, `OSTRZEZENIE folder_cyrkon ... program korzysta z folderu puli wybranego w programie`, `OK pula ... 3 pliki STL` (runda 1: kod 1) - `r2_c.py`, katalog `k_b1a`, oraz [poprz.]. (b) folder wybrany w programie nie istnieje, `folder_cyrkon` istnieje z 1 STL: kod 1, `BLAD pula ... folder wybrany w programie niedostepny`, `CZERWONA (ok 15, ostrzezenia 5, bledy 1)` (runda 1: kod 0) - `r2_d.py` oraz [poprz.]. Nazwa folderu wybranego w wyjsciu: 0 z 2 sprawdzonych wyjsc, [poprz.] 0 z 2. Wstrzykniecia N1 (folder zawsze z ustawien) i N6 (brak BLAD przy niedostepnym folderze wybranym): wykryte 2 z 2. |
| P1 | zamknieta | [poprz.] baza trzymana bez wspoldzielenia: `BLAD baza: pliku bazy nie da sie otworzyc (PermissionError: zajety przez inny program albo brak dostepu)`, rada bez slowa o kopii, 0,16 s (runda 1: "przywroc z kopii", 3,67 s); sciezka UNC: SQLITE_CANTOPEN zamiast "invalid uri authority"; 11 prawdziwych uszkodzen pliku: rada o kopii tylko przy CORRUPT / NOTADB, 10 z 10 wlasciwych. Wstrzykniecia N3 (kod 14 dopisany do "nie jest baza") i N10 (rada o kopii przy pliku zajetym): wykryte 2 z 2; M4 (`mode=rw`) wykryte. |
| P2 | zamknieta | [poprz.] 12 przypadkow blednych wartosci x 2 wyjscia (tekst, `--json`): nazwa osoby / klucz ramek w wyjsciu kodu 2: 0 z 24 (runda 1: 2 z 2); wartosc zostaje tylko dla `[sciezki]`, `[plytki]` i liczb. Przeglad nowych komunikatow (12 wierszy z wartoscia zmiennej): tylko plik ustawien, sciezki z `[sciezki]`, nazwa klucza, nazwa zmiennej srodowiska, nazwa bledu SQLite. |
| P3 | zamknieta | [poprz.] plik ustawien w cp1250 i UTF-16: `plik ustawien nie jest zapisany w kodowaniu UTF-8` + rada z Notatnikiem; z BOM: `zaczyna sie od znacznika BOM` + rada "bez BOM"; kod 2 w kazdym przypadku. Wstrzykniecie N4 (BOM nierozpoznawany): wykryte. |
| P4 | zamknieta | Wstrzykniecie M1 (wyjatek sprawdzenia nie jest lapany w `wykonaj`): wykrywa `test_p4_wyjatek_w_jednym_sprawdzeniu_wiersz_blad_reszta_wykonana` (runda 1: 91 z 91 passed). Proba wlasna limitu: 22 wiersze, BLAD tylko w jednym, kod 1. |
| P5 | zamknieta | Wstrzykniecia M2 (brak pakietu jako wersja "0"), M3 (wynik ladowania modulow ignorowany), M10 (proba zapisu niczego nie zapisuje): wykryte 3 z 3 (runda 1: 0 z 3), przez testy na prawdziwych stanach (`test_pakiety_brak_potrzebnego...`, `test_p5_modul_nie_laduje_sie_prawdziwe_ladowanie_funkcja_programu...`, `test_p5_dane_folder_prawdziwy_zakaz_zapisu...`). |
| D1 | zamknieta | Baza w trybie WAL rozpoznawana z naglowka i nieotwierana (OSTRZEZENIE, bez `-shm` / `-wal`) - przeglad kodu `:731-740`, test wykonawcy. |
| D2 | zamknieta | Wstepne sprawdzenie folderu danych z limitem 5 s + limit kazdego sprawdzenia - przeglad `:1291-1300` i proby wlasne limitu. |
| D3 | zamknieta | Komunikat bez obietnicy "brak prawa zapisu" - przeglad `:574-580`. |
| D4 | zamknieta | `Thumbs.db` / `desktop.ini` pomijane (decyzja koordynatora) - przeglad `:121`, test wykonawcy. |
| D5 | zamknieta | Petla po rejestrze wykonywana w tescie z atrapa `winreg` - przeglad testu. |

Decyzje koordynatora z `a11s-r2.md` [poprz., proby na prawdziwych katalogach]: OneDrive po samej nazwie = OSTRZEZENIE (4 z 4 nazw), po zmiennej
`OneDrive*` = BLAD (2 z 2; wstrzykniecie N7 wykryte); brak MillBox przy `pula_wpisow = true` = OSTRZEZENIE z rada o wspolczynniku;
`Thumbs.db` / `desktop.ini` pomijane; wzor ustawien = kod 1 z nazwa klucza i pliku w radzie. Wdrozone 4 z 4.

### 1.2. Nowe uwagi

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| D6 | D (sprawa miedzy paczkami) | `stanowisko/samokontrola.py:293-313, 1297-1302` | Runda 2 wykonuje kazde sprawdzenie w watku pomocniczym, a watek glowny czeka na niego w `join`. Na komputerze, na ktorym zapytanie WMI modulu `platform` nie odpowiada (PC, konto `<konto-PC>`: zawsze; przyczyna opisana w raporcie E3-A11w - `import trimesh` wola `platform.system()`, porzucony watek zapytania po ok. 5 s zamyka losowy uchwyt procesu), proces samokontroli ginie z kodem 0xC0000005, gdy zyje dluzej niz ok. 5 s po sprawdzeniu `moduly`. Seria na przemian z `dane_miejsce` wydluzonym o 7 s: **nowy kod 9 z 13 awarii** (kazda w srodku pracy, 0 wierszy wyjscia, po 5,6-7,1 s; 9 z 9 ten sam stos: watek glowny w `join`, watek sprawdzenia w `sleep`), **stary kod c67fbe5 0 z 13**, **nowy z `sys.modules['_wmi'] = None` 0 z 13**, stary z blokada 0 z 13. Bez wydluzenia (proces 2,0-3,0 s): 0 z 6 w kazdym wariancie; w seriach poprzednika nowy 4 z 71 (wszystkie 4 w przebiegach ok. 7 s, 4 z 4 po wypisaniu calego wyniku ZIELONA i z pustym stderr), stary 0 z 51. Przy obciazonym PC sam import modulow trwa do 16,8 s, wiec zjawisko trafia tez w zwykle uruchomienia: test paczki `test_polecenie_modulu_w_osobnym_procesie` padl z kodem 3221225477 w 2 z 13 przebiegow (oba po wypisaniu calego wyniku ZIELONA). Runda 2 zjawiska nie wprowadzila (zrodlem jest zapytanie WMI, takie samo w rundzie 1), ale wyraznie je nasilila. Skutek dla instalatora A11i (`10a39d9`, odczyt): kod spoza 0 / 1 / 2 = powtorka do 3 razy, potem "samokontrola zakonczyla sie awaryjnie" i wersja NIE jest przelaczana - falszywy blad, nigdy falszywa zielen. Waga D, bo poprawka istnieje poza paczka i usuwa zjawisko w calosci, a na laptopie ze sprawnym WMI porzuconego watku nie ma. | Bez zmiany w PR #38. Koordynator: scalic E3-A11w przed PR #38 albo razem i po scaleniu powtorzyc `a1.sh 5 7` na `main` (oczekiwane 0 awarii nowego kodu). Do czasu scalenia A11w: pad `test_polecenie_modulu_w_osobnym_procesie` z kodem 3221225477 w pelnym pytest to to zjawisko, nie blad paczki. Wykonawcy przy okazji: jedno zdanie w `samokontrola.md` ("Zalozenia i granice"), ze watki sprawdzen wymagaja blokady `_wmi` z pakietu `stanowisko`. |
| D7 | D | `stanowisko/samokontrola.py:552-556` | "Plik probny zawsze znika" nie zachodzi w 2 stanach (proby wlasne): (1) zamkniecie pliku zglasza blad po zapisie (np. dysk sieciowy, pelny dysk z opoznionym zapisem): `os.close` w `finally` rzuca i `os.unlink` w tym samym `finally` juz sie nie wykonuje - wiersz `BLAD dane_folder` jest poprawny, ale w folderze danych zostaje `samokontrola_<pid>_<hex>.tmp` (1 plik, 12 bajtow); (2) zapis wisi dluzej niz limit sprawdzenia i proces konczy sie, zanim watek dojdzie do usuniecia: `BLAD dane_folder: sprawdzenie nie zakonczylo sie w N s`, kod 1, plik zostaje (1 z 1). Gdy watek zdazy przed koncem procesu, plik znika (1 z 1). Zwykle bledy zapisu (`os.write` -> OSError, zakaz tworzenia plikow): plikow 0. Plik nie zawiera danych i niczego nie psuje (program go nie czyta). | Zagniezdzic: `try: os.close(uchwyt)` / `finally: os.unlink(nazwa)`; stan (2) opisac jednym zdaniem w `samokontrola.md` przy limicie czasu ("po limicie w folderze danych moze zostac plik `samokontrola_*.tmp` - mozna go usunac"). |

## 2. Wlasne proby

`py.cmd` = `<PC-katalog>\koordynator\narz\py.cmd` z katalogu `Ramki\stanowisko` kopii recenzenta. Dane fikcyjne w `robocze\rec-a11s\runda2\k_*`.

| Nr | Polecenie / proba | Wynik |
|---|---|---|
| 1 | [poprz.] `py.cmd -m pytest -q -p no:cacheprovider testy/test_samokontrola.py` | 148 passed, 132,08 s (log `pytest_paczki_r2.log`); w pliku 102 funkcje testowe, 1 `skipif(os.name != "nt")` (w Windows wykonywany), 0 xfail |
| 2 | [poprz.] `r2_1.py` (log `r2_1.log`): B1a, B1b, P1 (zajeta, UNC, 11 uszkodzen), P2 (12 x 2), P3 (cp1250, UTF-16, BOM), decyzje, POTRZEBUJE | jak w tabeli 1.1; POTRZEBUJE potwierdzone: prawdziwy `Aplikacja(ust)` na pliku puli o tresci `[1, 2]` / `"napis"` / `5` / `null` konczy sie `AttributeError` 4 z 4 |
| 3 | `r2_d.py`: wyrywkowe powtorzenie B1b z logu poprzednika | kod 1, `BLAD pula`, `OK folder_cyrkon` - zgodne z logiem |
| 4 | `r2_c.py` C1 (punkt b): 4 katalogi (pula wybrana w programie; pula wpisow; plik puli z bledna trescia; bez pliku puli) x 2 przebiegi `main` miedzy pomiarami (tekst, `--json`) i trzeci po pomiarze; stan katalogu przed / po = lista + rozmiar + sha256 + mtime kazdego pliku | plikow i katalogow 12 -> 12, 8 -> 8, 10 -> 10, 6 -> 6; roznic 0 z 36 pozycji; stderr 0 B; `QCoreApplication.instance()` = None i `QApplication.instance()` = None; uchwytow logowania programu 0 (same `NullHandler` bibliotek), filtr z `aplikacja.LOG` zdjety; watkow po 12 przebiegach 1 (glowny); po `import stanowisko.samokontrola` ciezkich modulow w `sys.modules` 0 z 7; `git status --short --ignored` kopii pusty (program nic nie zapisal obok siebie) |
| 5 | `r2_c.py` czasy sprawdzen (opakowanie `_z_limitem`, PC obciazony pelnym pytest koordynatora) | `moduly` 16,8 s przy pierwszym imporcie (limit 120 s), `pakiety` 0,16 s, `modele` 0,08 s, pozostale <= 0,03 s (limit 30 s); zwykly proces `--bez-sieci` 2,0-3,0 s (24 przebiegi), [poprz.] zimny start 20,3 s i 19,3 s (2 pierwsze z 20) |
| 6 | `r2_c.py` C2 (punkt a): `dane_miejsce` trwa 3 s przy limicie 1 s (stala zmieniona tylko w probie) | `BLAD dane_miejsce: sprawdzenie nie zakonczylo sie w 1 s - samokontrola nie czekala dluzej`, 22 wiersze, 1 BLAD, kod 1, czas calosci 1,20 s; watek zyje po wyniku i konczy sie sam po 3 s; `excel` po limicie: OSTRZEZENIE, kod 0 (ramki i Excel nigdy nie daja BLAD - przeglad `:1050-1128`) |
| 7 | `r2_c5.py` (prawdziwy proces, watek sprawdzenia wisi 120 s po limicie 1 s): tryby sleep / zapis pliku probnego / watek z otwartym polaczeniem i transakcja odczytu bazy | kod 1 x 3, 22 wiersze x 3, 1 BLAD w wlasciwym wierszu x 3, stderr 0 B; proces konczy sie od razu po wypisaniu (calosc 13-16 s lacznie z importami, nie 120 s); po trybie "baza" obok bazy 0 nowych plikow; po trybie "zapis" zostaje plik probny -> D7 |
| 8 | `r2_c.py` C3 (punkt c): `os.write` -> OSError(28); `os.close` -> OSError(5) po zapisie; zapis 3 s przy limicie 1 s | `BLAD dane_folder` x 3; plikow probnych po: 0 / 1 / 0 (po zakonczeniu watku) -> D7 |
| 9 | `r2_c.py` C4 (punkt d): umowa na 3 katalogach (kod 0, kod 0, kod 2), porownanie z modulem rundy 1 wczytanym z `c67fbe5` | wiersze zgodne z `OK <kod>: <opis>` / `OSTRZEZENIE|BLAD <kod>: <opis>; <rada>`: 43 z 43; ostatni wiersz zgodny 2 z 2 (kod 2: `SAMOKONTROLA: NIEWYKONANA (...)` jak w rundzie 1); `--json`: jeden obiekt, ASCII, klucze obiektu i sprawdzenia rowne rundzie 1 (3 z 3), 21 kodow w tej samej kolejnosci (3 z 3); kody wyjscia tekst = json = modul rundy 1 (3 z 3); kod 1 potwierdzony w probach 3, 6, 7 |
| 10 | Punkt (e): nazwa folderu puli wybranego w programie (fikcyjne nazwisko) w wyjsciu i na stderr | 0 z 2 sprawdzonych wyjsc (`k_b1a`, `k_spr`), [poprz.] 0 z 2; wyjatek metody programu pokazywany tylko nazwa typu (przeglad `:927-928`) |
| 11 | Sprawa 0xC0000005, serie `a1.sh` (prawdziwy proces przez `wmi_wrap.py`, `-X faulthandler`, 4 warianty na przemian, wynik kazdego przebiegu dopisywany do logu): `op7` 8 rund, `op7b` 5 rund (opoznienie `shutil.disk_usage` 7 s), `op0` 6 rund (bez opoznienia) | z opoznieniem: stary 0 z 13, nowy 9 z 13, nowy + blokada `_wmi` 0 z 13, stary + blokada 0 z 13; bez opoznienia: 0 z 6 x 4; logi `a1_op7.log`, `a1_op7b.log`, `a1_op0.log`, stosy `awaria_op7*.txt` (9) |
| 12 | [poprz.] serie e1-e4 (prawdziwy proces `--bez-sieci`, bez opoznienia; e3 z faulthandler, e4 na jednym rdzeniu), `rep.py` (import modulow w watku / w watku glownym) | nowy kod 4 z 71 awarii (e1: 4 z 20, przebiegi ok. 7 s), stary 0 z 51; `rep.py` 0 z 20 |

Wstrzykniecia bledu (`mut.py`; po kazdym `pytest -x testy/test_samokontrola.py`, potem `git checkout` pliku; status kopii pusty 15 z 15):

| Nr | Zepsucie | Pierwszy padajacy test | Wykryte |
|---|---|---|---|
| M1 | `wykonaj`: wyjatek sprawdzenia nie jest lapany | `test_p4_wyjatek_w_jednym_sprawdzeniu_wiersz_blad_reszta_wykonana` (*) | tak |
| M2 | `_wersja_pakietu`: brak pakietu zwraca "0" | `test_pakiety_brak_potrzebnego_blad_brak_pytest_bez_znaczenia_brak_dodatkowego_ostrzezenie` (*) | tak |
| M3 | `_zaladuj`: wynik ladowania modulow zamieniony na same True | `test_p5_modul_nie_laduje_sie_prawdziwe_ladowanie_funkcja_programu_blad_kod_1` | tak |
| M4 | baza otwierana `mode=rw` | `test_p1_uri_bazy_postac` | tak |
| M5 | plik probny nie jest usuwany | `test_samokontrola_nie_zmienia_bazy_ustawien_ani_folderow` | tak |
| M6 | `_quick_check` zawsze "ok" | `test_baza_uszkodzona_quick_check_blad` | tak |
| M10 | `_proba_zapisu` niczego nie zapisuje | `test_p5_dane_folder_prawdziwy_zakaz_zapisu_blad_bez_zawieszenia` | tak |
| N1 | `_folder_puli`: zawsze folder z ustawien (bez metody programu) | `test_pula_folder_wybrany_w_programie_bez_sciezki_w_wyjsciu` | tak |
| N2 | limit: kazdy wiersz po limicie = OSTRZEZENIE | `test_kazde_sprawdzenie_ma_gorny_limit_czasu` | tak |
| N3 | kod SQLite 14 (CANTOPEN) dopisany do "plik nie jest baza" | `test_p1_rada_o_kopii_tylko_dla_notadb_i_corrupt[14-SQLITE_CANTOPEN-False]` | tak |
| N4 | `_ma_bom` zawsze False | `test_p3_plik_ustawien_z_bom_rada_zapisz_bez_bom` | tak |
| N6 | niedostepny folder puli wybrany w programie nie daje BLAD | `test_b1_folder_puli_wybrany_w_programie_niedostepny_blad_w_wierszu_pula` | tak |
| N7 | OneDrive ze zmiennej srodowiska traktowany jak "po nazwie" | `test_dane_polozenie_w_onedrive_ze_zmiennej_blad` | tak |
| N9 | limit sprawdzenia wylaczony (1e6 s) | `test_kazde_sprawdzenie_ma_gorny_limit_czasu` | tak |
| N10 | rada o kopii przy pliku bazy zajetym przez inny program | `test_p1_baza_trzymana_przez_inny_program_blad_dostepu_bez_rady_o_kopii` | tak |

Razem: 7 z 7 rundy 1 (runda 1: 3 z 7) i 8 z 8 nowych. (*) M1, M2: pierwszy przebieg zatrzymal sie wczesniej na
`test_polecenie_modulu_w_osobnym_procesie`, ktorego proces potomny zginal z kodem 3221225477 (D6, bez zwiazku z wstrzyknieciem);
wynik w tabeli pochodzi z powtorki z tym jednym testem wylaczonym (`mut_M1_b.log`, `mut_M2_b.log`).

## 3. Kryteria zlecenia

| Nr | Kryterium | Ocena |
|---|---|---|
| R2-1 | Kazda uwaga B / P: test, ktory bez poprawki pada | Potwierdzone wlasna proba dla P4, P5 i kodu B1, P1, P3 przez wstrzykniecia (15 z 15 wykrytych); "55 failed z 144 na starym kodzie" - wg wykonawcy, niesprawdzone |
| R2-2 | `test_samokontrola.py`: 0 failed | Potwierdzone [poprz.]: 148 passed. Zastrzezenie D6: na PC bez poprawki A11w `test_polecenie_modulu_w_osobnym_procesie` pada losowo (2 z 13 przebiegow przy obciazeniu) |
| R2-3 | Pelny pytest: 0 failed | Niepowtarzane (zasada 3). Log koordynatora `robocze\koord\pytest_a11s_6befc0d.log` o 19:38: 61% przebiegu, znakow F / E: 0 - niedokonczony, wyniku koncowego nie ma. Wynik wykonawcy: wg wykonawcy, niesprawdzone |
| R2-4 | Umowa wywolania bez zmian; tabela kodow zaktualizowana | Umowa: potwierdzone wlasna proba (proba 9). Tabela w `samokontrola.md`: potwierdzone przegladem - 6 komunikatow z prob (`folder_cyrkon`, `folder_millbox`, `dane_polozenie`, `baza` zajeta, `pula` BLAD, `dane_folder`) zgodnych z tabela 6 z 6; calej tabeli wiersz po wierszu nie porownano |
| 1 | Testy pokrywaja kazde sprawdzenie w stanie OK i zlym, kody, format, `--json`, `--sumy` | Potwierdzone uruchomieniem [poprz.] i wstrzyknieciami; `monkeypatch.setattr(S, ...)` zostalo 17 (11 funkcji: `_zaladuj` 4, `_czytaj_folder` 2, `_zapytaj_ramke`, `_wolne_miejsce`, `_wersja_pythona`, `_polacz_do_odczytu`, `_folder_odpowiada`; 6 stalych) - stany grozace falszywa zielenia (brak pakietu, blad importu, zakaz zapisu, wyjatek sprawdzenia) maja testy na prawdziwych stanach, co pokazuja wstrzykniecia |
| 2 | Swiezy katalog ze wzoru i folderami: 0 bledow, ramki = ostrzezenie, kod 0 | Potwierdzone wlasna proba (katalog `k_mb`: kod 0, `ZIELONA (ok 14, ostrzezenia 7)`, 24 przebiegi procesu) |
| 3 | Samokontrola nie zmienia bazy ani ustawien | Potwierdzone wlasna proba (proba 4: 0 roznic w 4 katalogach; M4, M5 wykryte). Wyjatek: plik probny w 2 stanach bledu (D7) |
| 4 | Czas z `--bez-sieci` do 20 s na PC | Potwierdzone dla zwyklego uruchomienia: 2,0-3,0 s. Zimny start [poprz.]: 20,3 s i 19,3 s - na granicy (PC z 77 GB RAM zajetymi przez inny program); przy obciazonym PC sam import modulow do 16,8 s. Laptop stanowiska: nie zmierzono |
| 5 | Pelny pytest: 0 failed | jak R2-3 |

Punkty zlecenia recenzji: (a) limit czasu - watki pomocnicze `daemon`, po limicie wiersz BLAD (ramki, Excel: OSTRZEZENIE), proces konczy sie
od razu kodem 1 i nie wisi przy wyjsciu, wiszacy watek nie zostawia nic przy bazie (polaczenie tylko do odczytu), falszywa CZERWONA na
wolnym laptopie malo prawdopodobna (zapas: `moduly` 16,8 s wobec 120 s, reszta <= 0,16 s wobec 30 s); skutek uboczny watkow = D6.
(b) `_wczytaj_pule` wolane na obiekcie zastepczym: bez okna, bez `QApplication`, bez zapisu, 0 roznic. (c) plik probny: znika poza
2 stanami z D7. (d) umowa niezmieniona. (e) danych osobowych w nowych komunikatach nie znalazlem.

## 4. Zakres plikow i zasady

- Pliki: 4 z 4 z listy zlecenia; `git diff main...e3/a11s --stat` = 4 pliki. Zadnego pliku nietykalnego, bez zmiany schematu i stosu.
- ASCII / LF: w 4 plikach 0 bajtow spoza ASCII, 0 CR, 0 tabulatorow, 0 spacji na koncu linii, ostatni bajt LF; `git diff --check` pusty.
- Commity rundy 2: 5 + wciagniecie `main`, przedrostek `E3-A11s:`, stopka `Co-Authored-By` 6 z 6; pierwszy commit rundy to testy przed kodem.
  Worktree wykonawcy czysty, HEAD `6befc0d` (odczyt).
- Testy: 0 xfail, 1 `skipif` poza Windows; dane fikcyjne.
- Dane osobowe: w wyjsciu sciezki z `[sciezki]`, plik ustawien, liczniki; nazw podfolderow, plikow zlecen i osob nie znalazlem w zadnej probie.
- POTRZEBUJE wykonawcy (`aplikacja.py`, `Aplikacja._wczytaj_pule`: plik `stanowisko_pula.json` z JSON niebedacym obiektem konczy start
  programu `AttributeError`) - potwierdzone [poprz.] 4 z 4; do osobnej paczki, nie obciaza PR #38. Samokontrola zglasza ten stan jako BLAD `pula`.

## 5. Do decyzji wlasciciela (nie blokuje)

1. **Kolejnosc scalen (D6):** E3-A11w przed PR #38 albo razem. Jesli A11w mialoby nie wejsc, samokontrola potrzebuje wlasnej blokady `_wmi`
   (jeden wiersz na poczatku modulu, przed pierwszym importem `platform`) - wtedy to jest poprawka do PR #38.
2. **Baza w trybie WAL = OSTRZEZENIE bez sprawdzenia spojnosci** (poprawka D1 wg propozycji rundy 1): uszkodzona baza w trybie WAL przejdzie
   na zielono. Program trybu WAL nie ustawia, wiec stan powstaje tylko po otwarciu bazy obcym narzedziem - oceniam jako wlasciwe.
3. Sprawy z rundy 1 (progi miejsca 10 GB / 1 GB, plik nadmiarowy = BLAD, `-journal` = OSTRZEZENIE) - bez zmian.

## Dziennik roboczy (zapis przyrostowy obu recenzentow, bez zmian)

- [1] pytest paczki w kopii recenzenta (HEAD 6befc0d): 148 passed, 132,08 s (log `robocze\rec-a11s\runda2\pytest_paczki_r2.log`).
- [2] r2_1.py (log r2_1.log): B1a kod 0 (OSTRZEZENIE folder_cyrkon, OK pula 3 pliki STL), B1b kod 1 (BLAD pula) - B1 ZAMKNIETA.
  P1: baza trzymana bez wspoldzielenia -> BLAD "pliku bazy nie da sie otworzyc (PermissionError...)", rada bez kopii, 0,16 s; UNC: SQLITE_CANTOPEN
  (nie "invalid uri authority"); 11 prawdziwych uszkodzen pliku: CORRUPT / NOTADB -> rada o kopii 10 z 10 wlasciwych - P1 ZAMKNIETA.
  P2: 12 przypadkow x 2 (tekst, json): nazwa osoby / klucz w wyjsciu 0 z 24 - ZAMKNIETA. P3: cp1250, UTF-16, BOM: komunikat o kodowaniu - ZAMKNIETA.
  Decyzje: OneDrive po nazwie 4 z 4 OSTRZEZENIE, zmienna = BLAD; MillBox przy pula_wpisow=true OSTRZEZENIE z rada o wspolczynniku; wzor: kod 1, klucz i plik w radzie.
  POTRZEBUJE potwierdzone: prawdziwy Aplikacja(ust) na pliku puli "[1, 2]" / "napis" / 5 / null -> AttributeError (4 z 4).
- [3] UWAGA w toku: przy wstrzyknieciu M1 test `test_polecenie_modulu_w_osobnym_procesie` padl z innego powodu: proces samokontroli wypisal
  caly wynik ZIELONA i zakonczyl sie kodem 3221225477 (0xC0000005) - do zbadania (czestosc na kodzie rundy 2 wobec rundy 1).
- [4] PRZEJECIE recenzji 19:08 (poprzedni recenzent zginal przy restarcie PC 18:49-18:56; [1]-[3] przyjete, kopia `rec-a11s` czysta na 6befc0d).
  Logi poprzednika, przebiegi prawdziwego procesu `--bez-sieci` (kazdy 2,3-7 s): nowy kod 4 awarie z 71 (e1: 4 z 20, wszystkie w przebiegach
  trwajacych ok. 7 s; e2-e4: 0 z 51), stary kod c67fbe5: 0 z 51 (wszystkie przebiegi 2,3-4,7 s). Awarie tylko, gdy proces zyl dluzej niz ok. 5 s.
- [5] Seria `a1.sh` (w toku, log `a1_op7.log`): 4 warianty na przemian - stary / nowy / nowy z `sys.modules['_wmi']=None` / stary z blokada;
  `shutil.disk_usage` opozniony o 7 s (biblioteka standardowa, nie modul paczki), zeby proces zyl > 5 s po `import trimesh`.
  Pierwsza awaria nowego kodu: kod 0xC0000005 w SRODKU pracy (0 wierszy wyjscia), stos: watek glowny w `join` (`_z_limitem`), watek sprawdzenia w `sleep`.
  Instalator A11i (10a39d9, odczyt): kod spoza 0 / 1 / 2 = powtorka do 3 razy, potem "zakonczyla sie awaryjnie", wersja NIE przelaczona.
- [6] Seria `a1.sh 8 7 op7` (19:10-19:19, log `a1_op7.log`; 32 procesy, kazdy 12-29 s, w tle pelny pytest koordynatora): awarie 0xC0000005 -
  stary kod bez blokady 0 z 8, NOWY kod bez blokady 4 z 8 (kazda w srodku pracy, 0 wierszy wyjscia, po 6,6-7,1 s), nowy kod z `_wmi` zablokowanym
  0 z 8, stary z blokada 0 z 8. Wniosek roboczy: zjawisko srodowiska (zapytanie WMI modulu `platform`, znika z blokada `_wmi` = poprawka E3-A11w),
  ale kod rundy 2 (watek na kazde sprawdzenie, watek glowny czeka w `join`) jest na nie wyraznie bardziej wrazliwy niz kod rundy 1.
- [7] 19:20 kolejka `q.sh` (log `q.log`): proby C (`r2_c.py`), wyjscie z wiszacym watkiem (`r2_c5.py`), 11 wstrzykniec, druga seria a1.
- [8] `r2_c.py` (log `r2_c.log`), 1 proces: (b) 4 katalogi x 3 przebiegi `main` (tekst, `--json`): plikow i katalogow przed / po 12->12, 8->8, 10->10, 6->6,
  roznic (rozmiar, sha256, mtime) 0; `QCoreApplication.instance()` i `QApplication.instance()` = None; uchwytow logowania programu 0, filtr z `A.LOG`
  zdjety; watkow po przebiegach 1 (glowny); nazwa folderu puli wybranego w programie w wyjsciu 0 z 4. Czas `moduly` przy obciazonym PC 16,8 s
  (limit 120 s), pozostale sprawdzenia <= 0,16 s (limit 30 s). (d) klucze `--json`, klucze sprawdzenia, 21 kodow i ich kolejnosc = modul rundy 1 (3 z 3
  katalogow), wiersze zgodne z formatem 44 z 44. (a) limit 1 s w probie: `BLAD dane_miejsce: sprawdzenie nie zakonczylo sie w 1 s`, 22 wiersze, kod 1,
  czas 1,2 s; excel po limicie = OSTRZEZENIE, kod 0. (c) `os.write` -> OSError: BLAD, plikow probnych 0; `os.close` -> OSError: plik probny ZOSTAJE (1).
- [9] `r2_c5.py` (prawdziwy proces, watek wisi 120 s po limicie 1 s): sleep / zapis / baza -> kod 1 x 3, 22 wiersze, proces konczy sie od razu
  (13-16 s lacznie z importami przy obciazonym PC), stderr 0 B; tryb zapis: w folderze danych ZOSTAJE `samokontrola_<pid>_<hex>.tmp` (1 plik).
- [10] Wstrzykniecia (kolejka w toku): M1, M2, M3, M10 wykryte (4 z 4 dotad). UWAGA: w 2 z 3 pierwszych przebiegow test paczki
  `test_polecenie_modulu_w_osobnym_procesie` padl niezaleznie od wstrzykniecia - proces samokontroli zginal z kodem 3221225477 (zjawisko z [6]).
- [11] Wstrzykniecia - koniec (log `q.log`, `mut_*.log`): 7 z 7 rundy 1 wykryte (M1, M2, M3, M4, M5, M6, M10), 8 z 8 nowych wykryte (N1, N2, N3, N4,
  N6, N7, N9, N10). Kopia po kazdym przywrocona (status pusty 15 z 15).
- [12] Seria 2 `a1.sh 5 7 op7b` (19:29-19:32): stary bez blokady 0 z 5, NOWY bez blokady 5 z 5, nowy z blokada `_wmi` 0 z 5, stary z blokada 0 z 5.
  Razem obie serie z opoznieniem 7 s: stary 0 z 13, nowy 9 z 13, nowy z blokada 0 z 13, stary z blokada 0 z 13. 9 z 9 awarii: ten sam stos.
- [13] Wyrywkowo B1b z logu poprzednika (`r2_d.py`): kod 1, `BLAD pula ... folder wybrany w programie niedostepny`, `OK folder_cyrkon` - zgodne.
  Zasady: 4 pliki, 0 bajtow spoza ASCII, 0 CR, 0 TAB, ostatni bajt LF; commity rundy 2: 5 + wciagniecie main, stopka 6 z 6; `git diff --check` pusty.
- [14] 19:34 seria 3 bez opoznienia (`a1.sh 6 0 op0`); potem uklad koncowy raportu.
- [15] Seria 3 (19:34-19:35, log `a1_op0.log`): proces 2,0-3,0 s, awarii 0 z 6 w kazdym z 4 wariantow. 19:38 uklad koncowy raportu gotowy; pelny pytest
  koordynatora w toku (61 %, 0 znakow F / E) - wyniku koncowego recenzent nie widzial.

WERDYKT: do scalenia (B 0, P 0, D 2) - warunek kolejnosci: E3-A11w przed PR #38 albo razem (D6)
