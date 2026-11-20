# Raport recenzenta - PR #39 (E3-A11i, paczka wydania, instalacja, aktualizacja, powrot - wariant B), runda 1

- Data: 20.11.2026, PC, konto `<konto-PC>`.
- Zakres: `git -C <PC-katalog>\qc diff main...e3/a11i`, HEAD `eb77d7d` (8 commitow od `bf00921`), 21 plikow (19 nowych,
  2 zmienione), 3720 linii dodanych, 1 usunieta.
- Metoda: wlasny przeglad calego diffu (`instalator.py` 1100 linii, `zainstaluj.cmd` i 5 wzorow `.cmd`,
  `zbuduj_wydanie.py` 328 linii, 2 pliki testow, instrukcja, opis modulu; raport wykonawcy na koncu), potem proby w kopii
  `<PC-katalog>\qc-wt\rec-a11i` (detached `eb77d7d`); pliki robocze i logi: `<PC-katalog>\koordynator\robocze\rec-a11i\`
  (`logi\01..54_*`, skrypty prob w `proby\`).
- Uruchomiono: 3 budowy paczki z `--kola` (2 x commit 1437621, 1 x HEAD) i 2 paczki probne z prawdziwym modulem
  samokontroli z galezi `e3/a11s` (`c67fbe5`, SHA-256 pliku `ceed874e...58c5`); 3 pelne instalacje (0.3.0 i 0.3.1 w katalogu
  ze spacja, nawiasami i znakami spoza ASCII; 0.3.0 w katalogu ASCII) + 1 instalacja przerwana zabiciem procesow; przejscie
  instrukcji krok po kroku; 2 proby zabicia instalatora; testy paczki (50 passed); 18 wstrzykniec bledu; 16 sond stanu na
  malej paczce (`proby\test_rec_a11i.py`); 7 sciezek z trudnymi znakami na prawdziwym venv (`proby\test_rec_cmd.py`);
  proba kopii bazy z goracym plikiem `-journal`; serie `testy\test_silnik.py` w srodowisku wersji i interpreterem bazowym.
  Pelnego pytest nie powtarzano. Naraz 1 proces python recenzenta (wyjatek: program uruchomiony w tle w probie "program
  dziala", ok. 45 s). Kopia recenzenta po probach czysta (`git status --short` pusty).
- Sprzatanie: katalogi prob (instalacje, rozpakowane paczki, ZIP-y, drzewa; 6,7 GB) usuniete; zostaly `logi\` (53 pliki)
  i `proby\` (5 skryptow). Przerywalem wylacznie wlasne procesy (instalator w probach zabicia, 4 zawieszone przebiegi pytest).

## 0. Werdykt

**Do scalenia po poprawkach.** B 0, P 7, D 7.

Glowne sciezki dzialaja i sa dobrze zabezpieczone: budowa jest powtarzalna bajtowo i bierze tresc z commita, instalacja
bez sieci daje srodowisko odciete od interpretera bazowego (73 z 73 pakietow), aktualizacja nie rusza ustawien, bazy ani
starej wersji, a wskaznik przelacza sie dopiero po zielonej samokontroli; zabicie instalatora w kroku pip i w kroku
samokontroli zostawilo wersje biezaca, ustawienia i dane bajt w bajt. Skrypty `.cmd` przeszly sciezki ze spacja, nawiasami,
`&`, `!`, `^`, `'` i znakami spoza ASCII oraz wrogie `PYTHONPATH` / `PYTHONHOME`. Testy sa rzeczowe: 16 z 18 wstrzyknietych
bledow wykryte.

Do poprawy przed scaleniem sa sciezki rzadkie, ale takie, w ktorych stanowisko traci albo przestaje widziec dane: kopia
bazy przy pliku `-journal` (P1), przywrocenie kopii przerwane w polowie (P2), wybor starej kopii przy drugim powrocie
(P3), sprzatanie obcych katalogow (P4) i wymiana katalogu wersji biezacej w miejscu (P5); do tego luka testow izolacji
(P6). P7 wykracza poza pliki paczki: `testy\test_silnik.py` uruchomiony w srodowisku wersji (tak, jak raport wykonawcy
proponuje T1) nie udal sie w 5 z 10 przebiegow (4 zawieszenia, 1 access violation), a interpreterem bazowym przeszedl
6 z 6 - przyczyna nieustalona, proba mala (sekcja 2.9). To jest najwazniejsza otwarta sprawa przed T0 / T1.

## 1. Uwagi

Linie: `I` = `Ramki/stanowisko/instalacja/instalator.py`, `Z` = `Ramki/stanowisko/narzedzia/zbuduj_wydanie.py`.

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| P1 | P | `I:480-491, 504-538, 541-553` | Program zabity albo zanik zasilania w trakcie zapisu (obok bazy zostaje `stanowisko.sqlite-journal`; program pracuje w trybie `journal_mode = delete`), aktualizacja uruchomiona przed nastepnym startem programu. `wersja_schematu` otwiera baze `mode=ro`, SQLite nie moze wycofac dziennika -> `None` -> `kopia_bazy` robi `shutil.copy2` samego pliku glownego, bez `-journal`. Proba wlasna (`logi\40`, 20000 wierszy, transakcja przerwana `os._exit`): kopia `..._vx.sqlite` = "database disk image is malformed", instalator wypisuje zwykly wiersz "kopia bazy: ... (schemat bazy 1 ...)" bez ostrzezenia, a `znajdz_kopie` zwraca te kopie jako pierwsza do przywrocenia (ma czytelny `user_version`). Sama baza po otwarciu do zapisu: 20000 wierszy, `integrity_check` ok. Ta sama galaz (`except sqlite3.Error` -> kopia bajtowa) wykona sie przy bazie zajetej przez inny proces (przeglad, bez proby). | Pod blokada programu otworzyc baze do zapisu (SQLite wycofa dziennik) albo kopiowac razem z `-journal` / `-wal`; po kopii `PRAGMA quick_check` na kopii; kopia niezweryfikowana = stop z kodem 6 przed samokontrola (nie przelaczac wersji bez dobrej kopii) albo co najmniej wyrazne OSTRZEZENIE i nazwa `_NIESPRAWDZONA`; `znajdz_kopie` pomija kopie bez `quick_check = ok`. Test z dziennikiem. |
| P2 | P | `I:568-585, 986-1006` | `Wroc_do_poprzedniej.cmd /przywroc-kopie`: blad systemu (np. `PermissionError` od antywirusa / indeksowania na swiezo zapisanym pliku) albo zabicie miedzy `os.replace(baza -> kopie\..._odlozona...)` a `os.replace(baza.nowy -> baza)`. Sonda E2 (`logi\53`): pliku bazy nie ma (zostaje `stanowisko.sqlite.nowy`), komunikat "POWROT: NIEUDANA (kod 6) - wersja biezaca bez zmian: 2.0". Ponowne `Wroc_do_poprzedniej.cmd /przywroc-kopie`: "Baza: schemat brak pliku ... schemat zgodny" -> "POWROT: GOTOWY", wskaznik na wersji poprzedniej, bazy nadal nie ma - program przy starcie zalozy PUSTA. Dane leza w `kopie\` i w `.nowy`, ale technik ich nie zobaczy, a komunikat mowi, ze nic sie nie zmienilo. | Baza nie moze znikac: najpierw kopia biezacej bazy do `kopie\` (z `-journal` / `-wal`), potem jedno `os.replace(.nowy -> baza)`; albo `try / except` z odlozeniem z powrotem. Na poczatku `wroc` i `zainstaluj`: `<baza>.nowy` bez pliku bazy = stop z komunikatem, co przywrocic. Test z wstrzyknietym bledem `os.replace`. |
| P3 | P | `I:541-553` | Aktualizacja N -> N+1 z migracja (kopia A), powrot z `/przywroc-kopie`, praca na N, `Wroc_do_poprzedniej.cmd` do N+1 (bez instalatora nie powstaje nowa kopia `_przed_`; program N+1 sam robi `stanowisko.kopia_v1_<czas>.sqlite` i migruje), drugi powrot z `/przywroc-kopie`. `znajdz_kopie` bierze najpierw kopie `_przed_<N+1>_*` - czyli stara kopie A - choc obok lezy nowsza kopia programu. Proba na prawdziwej instalacji (0.3.0 / 0.3.1): proponowana kopia z 11:54 (4 wpisy `zdarzenia`), pominieta kopia programu z 13:10 (8 wpisow); ostrzezenie "+7" zamiast "+3". Sonda A: po drugim powrocie 3 skany w bazie, w kopii programu 7. Praca wykonana na N miedzy powrotami znika z bazy roboczej (zostaje w plikach kopii). | Wybierac najnowsza (czas z nazwy / mtime) kopie o schemacie <= obslugiwanego sposrod WSZYSTKICH zrodel (instalator i program) i wypisac, ile jest nowszych / starszych; albo robic kopie `_przed_` przy kazdym przelaczeniu na wersje o wyzszym schemacie, takze w `wroc`. Test scenariusza dwoch powrotow. |
| P4 | P | `I:594-601, 841-844` | `zainstaluj.cmd /katalog <istniejacy katalog>`, w ktorym jest juz podkatalog `wersje` z czymkolwiek (np. `D:\Dokumenty\wersje\projekt ...`). Krok 3 uznaje kazdy podkatalog `wersje\*` bez `instalacja.json` za "niedokonczona instalacje" i usuwa go `rmtree` (bez kosza), zanim cokolwiek zapyta. Sonda I: obcy katalog z plikiem zniknal, wiersz "usunieto niedokonczona instalacje wersji projekt 2025 - wersja robocza", kod 0. Na domyslnym `C:\Stanowisko` nie wystapi; skutek nieodwracalny. | Usuwac wylacznie katalogi ze znacznikiem `NIEDOKONCZONA.txt` (plus pusty katalog o nazwie zgodnej z `WZOR_WERSJI`); pozostale zostawic i wypisac. Test. |
| P5 | P | `I:62, 871-892, 948-954`; `Z:42`; `instrukcje/instalacja_i_aktualizacja.md:57` | Katalog wersji BIEZACEJ jest wymieniany w miejscu (usun, potem zaloz). (a) Sonda J: paczka o numerze rozniacym sie tylko wielkoscia liter albo kropka na koncu (`1.0-rc1` / `1.0-RC1`, `1.0` / `1.0.` - w Windows ten sam katalog, a napisy rozne) omija straznika "inna budowa" (kod 3): wersja biezaca zostala usunieta i zastapiona budowa, ktora NIE przeszla samokontroli (kod 1), wiersz koncowy "wersja biezaca bez zmian: 1.0". To jest dokladnie przypadek, ktory mial zamknac commit 1437621. (b) Sonda C: naprawa wersji biezacej (uszkodzony plik albo nadmiarowy pakiet) przerwana w kroku pip albo zamknieciem okna: katalog wersji biezacej ma znacznik `NIEDOKONCZONA.txt`, `Stanowisko.cmd` odmawia startu, a instalator konczy "INSTALACJA: NIEUDANA (kod 6) - wersja biezaca bez zmian: 1.0"; to samo twierdzi ostatnie zdanie instrukcji. | (a) Porownania numerow przez `casefold()`, w `WZOR_WERSJI` (instalator i budowa) zakaz kropki na koncu; katalog istniejacy pod inna pisownia = kod 3. (b) Wersje biezaca / poprzednia naprawiac w katalogu tymczasowym i podmieniac po sukcesie (rename), a co najmniej: `_zglos` sprawdza `stan_wersji(biezaca)` i pisze prawde ("wersja biezaca X wymaga ponownego zainstaluj.cmd - program nie wystartuje"), zdanie w instrukcji poprawic. Testy obu przypadkow. |
| P6 | P | `testy/test_instalacja.py:42-50, 587-608`; `I:318-323`; `instalacja/wzory/*.cmd:15-16` | Luka w testach izolacji. Mutacja M9 (usuniete `--no-index` z polecenia pip) i M12 (usuniete `set "PYTHONPATH="` / `set "PYTHONHOME="` ze wzoru `Stanowisko.cmd`): 30 passed w obu. Polecenie pip nie jest nigdzie sprawdzane (atrapa srodowiska je zastepuje), a test z prawdziwym venv sam usuwa `PYTHONPATH` ze srodowiska przed uruchomieniem skryptow. Wymaganie "zadnego dostepu do sieci" i "bez PYTHONPATH z zewnatrz" trzyma dzis tylko przeglad (proba wlasna 54: wzory dzialaja poprawnie). | Test polecenia `Srodowisko.instaluj` (podmienione `I.uruchom`: sa `--no-index`, `--isolated`, `--only-binary=:all:`, nie ma `--index-url` / `--extra-index-url`); w tescie `.cmd` ustawic `PYTHONPATH` na `site-packages` interpretera bazowego i `PYTHONHOME` na nieistniejacy katalog (dla wszystkich skryptow, takze `zainstaluj.cmd` - patrz D1). |
| P7 | P | poza plikami paczki (`stanowisko/silnik.py`, `testy/test_silnik.py`); styk: `instalacja/wzory/Polecenie.cmd`, raport wykonawcy sekcja 6 (polecenie T1) | Polecenie T1 z raportu wykonawcy (`<K>\Polecenie.cmd -m pytest <repo>\Ramki\stanowisko\testy`, "NIE sprawdzono") dla jednego pliku `testy\test_silnik.py`: w srodowisku wersji z paczki przebiegi konczyly sie zawieszeniem bez pracy procesora i bez procesow potomnych (w roznych testach uzywajacych `Silnik`) albo `Windows fatal exception: access violation` (kod 0xC0000005), a interpreterem bazowym przechodzily. Liczby i przeplot: sekcja 2.9. Przyczyny nie ustalilem (hipoteza niesprawdzona: znane zjawisko konsoli / 0xC0000142 z E3-A2p nasilone przez proces posredni `venv\Scripts\python.exe`). Program na stanowisku bedzie dzialal wlasnie w tym srodowisku; kryterium 2 dowodzi tylko startu (`--zamknij-po 5`), nie analizy skanu. | Wykonawca albo koordynator: powtorzyc serie przeplatana (co najmniej 5 + 5 przebiegow), z `faulthandler` i kodami wyjscia potomkow ustalic przyczyne i wpisac wynik do raportu; jesli przyczyna lezy w `silnik.py` / testach - `POTRZEBUJE` (poza lista plikow). Do czasu wyjasnienia nie traktowac T1 w srodowisku wersji jako wykonalnego jednym poleceniem i dodac do T0 prawdziwa analize skanu w srodowisku wersji (np. `narzedzia\symulator_skanera.py`). |
| D1 | D | `instalacja/zainstaluj.cmd:28, 33, 45, 74` | Laptop ze zmienna `PYTHONHOME` ustawiona przez inny program: wywolania probne `"%PY%" -c ...` ida bez `-I`, Python nie startuje, a komunikat brzmi "BLAD: zla wersja Pythona - opcja /python wskazuje interpreter inny niz 3.12" przy poprawnym 3.12.10 (proba wlasna, kod 4; nic nie zmienione). Rada "zainstaluj Pythona 3.12" nie pomoze. | `-I` w czterech wywolaniach probnych albo `set "PYTHONHOME="` i `set "PYTHONPATH="` na poczatku skryptu; test razem z P6. |
| D2 | D | `I:799-945` (brak blokady instalatora) | `zainstaluj.cmd` uruchomiony drugi raz, gdy pierwszy jeszcze instaluje pakiety (podwojny dwuklik). Sonda B: drugi usuwa "niedokonczona" wersje pierwszego i konczy kodem 0, pierwszy konczy kodem 6 `nieoczekiwany blad instalatora (FileNotFoundError ... NIEDOKONCZONA.txt)`. Przy prawdziwym pip (pliki srodowiska zajete) drugi skonczy raczej "nie mozna usunac katalogu" po usunieciu samego znacznika - to wynik przegladu, nie proby. Wersja biezaca, ustawienia i dane nietkniete; ponowne uruchomienie naprawia. | Plik blokady instalatora w `<KATALOG>` (`msvcrt.locking`, jak `BlokadaProgramu`): "instalacja juz trwa w innym oknie". |
| D3 | D | `instalacja/zainstaluj.cmd:10-11, 68`; wzory: `if "%~1"=="" pause` | Skrypt uruchomiony z argumentem spoza okna polecen (skrot, Win+R, np. `zainstaluj.cmd /katalog D:\Stanowisko`): okno zamyka sie od razu po ostatnim wierszu, wyniku nie da sie przeczytac (zostaje dziennik). `/bez-pauzy` niczego dzis nie zmienia - pauza zalezy tylko od tego, czy sa argumenty. | Pauza zawsze, chyba ze podano `/bez-pauzy`. |
| D4 | D | `I:392-393, 416-426` | (a) `folder_millbox = ""` (program taki plik przyjmuje): kod 7 "sciezki wzgledne w [sciezki] (folder_millbox) ... np.: folder_millbox = "<KATALOG>/"" - rada bez sensu dla pustego folderu (sonda D). (b) `ustawienia.toml` zapisany z BOM (starszy Notatnik, "UTF-8"): kod 7 "blad skladni TOML: Invalid statement (at line 1, column 1)" - nic o kodowaniu, a instrukcja kaze edytowac w Notatniku. | (a) Pusta wartosc nie jest sciezka wzgledna - pominac albo osobny komunikat. (b) W instrukcji: "zapisz jako UTF-8 (bez BOM)"; w komunikacie kodu 7 dopisac te podpowiedz, gdy blad jest w wierszu 1, kolumnie 1. |
| D5 | D | `I:302-308, 817-827` | `/katalog` ze srednikiem w sciezce: `python -m venv` odmawia ("contains the PATH separator ;"), kod 6 z rada "Sprawdz miejsce na dysku i prawa zapisu" (proba 54, 1 z 7 nazw). | Sprawdzic `;` w kroku 3 razem z dlugoscia sciezki i podac wlasciwa rade. |
| D6 | D | `I:620-628` | Zabicie miedzy zapisem `wersja_poprzednia.txt` a `wersja_biezaca.txt` (sonda E1): oba wskazniki maja te sama wersje, `Wroc_do_poprzedniej.cmd` odpowiada "nie ma poprzedniej wersji" (kod 9), informacja o poprzedniej ginie. Ponowne `zainstaluj.cmd` naprawia stan po aktualizacji; po przerwanym powrocie trzeba instalowac z paczki. Okno czasowe: milisekundy. | Jeden plik wskaznika z obiema wartosciami (jeden `os.replace`) albo zapis biezacej przed poprzednia z kontrola spojnosci przy odczycie. |
| D7 | D | `instrukcje/instalacja_i_aktualizacja.md:17-18, 52, 57` | (a) Cytowany wiersz koncowy "`INSTALACJA: NIEUDANA (kod N) - wersja biezaca bez zmian`" nie pasuje do kodu 4 i do braku instalatora: tam jest "... - niczego nie zmieniono.", a przy braku instalatora nie ma wiersza `CO ZROBIC`. (b) Wiersz kodu 6 nie wymienia komunikatow "nie mozna usunac katalogu", "srodowisko wirtualne nie startuje", "pakiety srodowiska niezgodne", "nieoczekiwany blad instalatora", a rada "zwolnij miejsce albo wybierz inny katalog" do nich nie pasuje (kazdy ma wlasne `CO ZROBIC` na ekranie). (c) Zdanie koncowe "W kazdym z tych przypadkow wersja biezaca programu, ustawienia i dane zostaja bez zmian" jest nieprawdziwe dla P2 i P5. Reszta instrukcji zgadza sie z ekranem (sekcja 2.3). | Poprawic trzy miejsca; przy kodzie 6 odeslac do wiersza `CO ZROBIC` na ekranie. |

## 2. Wlasne proby

`PY` = `<PC>\AppData\Local\Programs\Python\Python312\python.exe`, `R` = `<PC-katalog>\koordynator\robocze\rec-a11i`,
`K1` = `R\Proba (1) z\Stanowisko` (w nazwie naprawde litery `o` z kreska i `z` z kropka), `K3` = `R\p3\S`.

### 2.1 Budowa (kryterium 1)

| Polecenie | Wynik |
|---|---|
| `py.cmd narzedzia\zbuduj_wydanie.py --wyjscie R\budowa_a --kola <PC-katalog>\wydania\kola --rewizja 1437621 --bez-samokontroli`, to samo do `budowa_b` | 2 x SHA-256 `6464d984...2310`, 444 093 596 bajtow, 201 plikow + `SHA256SUMS`; rowne sumie w `Ramki/etap3/wydania/SHA256SUMS_wydania.txt` i plikowi `<PC-katalog>\wydania\Stanowisko_0.3.0.zip` |
| to samo bez `--rewizja` (HEAD `eb77d7d`) | `ed7cd463...93cd`, 444 093 593 bajty (inny commit w `wydanie.json` - zgodnie z opisem) |
| lista wpisow ZIP z HEAD (`logi\04`) | 202 wpisy: program 122, `kola/` 73, `kola_testy/` 3, `zainstaluj.cmd`, `CZYTAJ.txt`, `wydanie.json`, `SHA256SUMS`; `testy/`, `raporty/`, `dane/`, `ustawienia.toml`, `__pycache__`, `*.pyc`, `opisy_modulow/`, `zbuduj_wydanie.py`: 0; sa `requirements.txt`, `instrukcje/` (1 plik), `ramka/` (14), `narzedzia/` (21), `SUMY_PROGRAMU.sha256` (121 wierszy = 121 pozostalych plikow programu), `SHA256SUMS` (201 wierszy = 201 pozostalych wpisow) |
| paczki probne `--zrodlo R\drzewa\N` (drzewo `eb77d7d` + `samokontrola.py` z `c67fbe5`) i `R\drzewa\M` (+ probna `MIGRACJE[2]`) | 0.3.0: `1bfae17a...6ec3`, 444 113 318 bajtow; 0.3.1: `bfdc9878...145c`; po rozpakowaniu (.NET `ZipFile`) `sha256sum -c SHA256SUMS`: OK 202 z 202, `sha256sum -c SUMY_PROGRAMU.sha256`: OK 122 z 122 |
| przeglad `Z:71-91` | tresc plikow z obiektow gita commita (`ls-tree` + `cat-file --batch`), nie z katalogu roboczego; pliki niesledzone nie wchodza (test `test_budowa_z_commita_nie_z_katalogu_roboczego`, mutacja M16 wykryta) |

### 2.2 Czysta instalacja i srodowisko (kryteria 2, 3) - `K1`, katalog biezacy inny niz paczka

| Polecenie | Wynik |
|---|---|
| `zainstaluj.cmd /katalog K1 /bez-sieci` (bez Pythona w typowych miejscach tego konta) | kod 4, "nie znaleziono Pythona 3.12 (sprawdzono: ...)", katalog `K1` nie powstal |
| `zainstaluj.cmd /katalog K1 /python C:\Windows\System32\where.exe` | kod 4, "zla wersja Pythona - opcja /python wskazuje interpreter inny niz 3.12", nic nie powstalo |
| `zainstaluj.cmd /katalog K1 /python PY` (z `PYTHONPATH` ustawionym z zewnatrz) | kod 1 po 64 s: sumy 202 z 202, pakiety 73 z 73, samokontrola CZERWONA (2 x BLAD: folder skanera i Cyrkon ze wzoru), "wersji biezacej nadal nie ma"; katalog wersji 1370 MB; w `K1` nie ma jeszcze skryptow `*.cmd` |
| edycja 4 folderow i `operatorzy` w `K1\ustawienia.toml`, to samo polecenie | kod 0 po 6 s: "juz zainstalowana i zgodna z paczka", ZIELONA (ok 16, ostrzezenia 5), wskaznik `0.3.0`, SHA-256 ustawien przed = po (`977d74e6...`) |
| `Polecenie.cmd -c "import sys ..."` przy `PYTHONPATH` = `site-packages` interpretera bazowego i `PYTHONHOME` = zly katalog | `sys.prefix` w `K1\wersje\0.3.0\venv`, `sys.path` 10 pozycji, 0 z `Python312\Lib\site-packages`, numpy z venv |
| `Polecenie.cmd -m pip list --format=freeze` wobec `zamrozone.txt` | 73 z 73 zgodne, jedyny nadmiarowy: `pip==25.0.1` |
| `Stanowisko.cmd --atrapa --zamknij-po 5`; `Stanowisko.cmd --zamknij-po 5` (Qt offscreen) | kod 0; kod 0, baza zalozona w `K1\dane\`, 0 katalogow `__pycache__` w katalogu programu |
| `zainstaluj.cmd ... /testy` na wersji zainstalowanej | kod 0: "dokladam zestaw testowy", pakiety 76 z 76, `pytest 9.1.1` |
| `zainstaluj.cmd ...` przy `PYTHONHOME` z zewnatrz | kod 4 "zla wersja Pythona" (D1) |

### 2.3 Instrukcja krok po kroku (kryterium 9)

Sekcje 2-5 instrukcji wykonane doslownie w `K1` (z `/katalog` i `/python`, bo konto nie ma prawa zapisu w `C:\Stanowisko`
ani Pythona w typowym miejscu): 9 krokow na ekranie w podanej kolejnosci; pierwsza instalacja = kod 1 i wskazowka edycji
ustawien; druga = kilka sekund; skrypty `Stanowisko.cmd`, `Samokontrola.cmd`, `Wroc_do_poprzedniej.cmd`, `Wersje.cmd` sa;
aktualizacja; powrot z ostrzezeniem kodu 8 i `/przywroc-kopie`; `Wersje.cmd` wypisuje `BIEZACA` / `poprzednia`.
Niezgodnosci: D7. Dwuklik (okno z pauza) oceniony przegladem skryptow, nie proba.

### 2.4 Aktualizacja, przerwania, powrot (kryteria 4-7)

| Proba | Wynik |
|---|---|
| Z1: aktualizacja do 0.3.1, w kroku pip zabite 3 wlasne procesy (instalator, proces posredni venv, pip) | wskaznik `0.3.0`, brak `wersja_poprzednia.txt`, `wersje\0.3.1\NIEDOKONCZONA.txt` jest; SHA-256 ustawien, bazy, pliku wynikow, wskaznika, 5 skryptow i skrot 18663 plikow `wersje\0.3.0`: 11 z 11 bez roznic (`logi\20`, `22`) |
| Z2: ponowna aktualizacja, instalator zabity 2 s po "[7/9] Samokontrola" | "usunieto niedokonczona instalacje wersji 0.3.1", pakiety 73 z 73, kopia `kopie\stanowisko_przed_0.3.1_20261120_115306_v1.sqlite`; po zabiciu: wskaznik `0.3.0`, wersja 0.3.1 zainstalowana, nie biezaca |
| aktualizacja przy programie uruchomionym (`Stanowisko.cmd --zamknij-po 45` w tle) | kod 5 "program "Stanowisko" jest uruchomiony", wskaznik `0.3.0` |
| aktualizacja do 0.3.1 (trzecie uruchomienie) | kod 0: "juz zainstalowana", druga kopia bazy (baza zmienila sie od Z2), ZIELONA, wskaznik `0.3.1`, poprzednia `0.3.0`, SHA-256 ustawien bez zmian; `Stanowisko.cmd --zamknij-po 5` = kod 0, baza w schemacie 2, kopia programu `stanowisko.kopia_v1_...` |
| `Wroc_do_poprzedniej.cmd` | kod 8: "zniknie ... 3 wpisow w 1 tabelach; tabela zdarzenia: 4 w kopii, 7 teraz (+3)", wskaznik i SHA-256 bazy bez zmian |
| `Wroc_do_poprzedniej.cmd /przywroc-kopie` | kod 0: baza = kopia (SHA-256 rowne), dotychczasowa baza w `kopie\stanowisko_odlozona_v2_...` (SHA-256 rowne bazie sprzed powrotu), wskaznik `0.3.0`; `Stanowisko.cmd --zamknij-po 5` = kod 0 |
| `Wroc_do_poprzedniej.cmd` przy bazie w schemacie 1 (powrot bez migracji, 0.3.0 -> 0.3.1) | kod 0: "schemat zgodny - baza zostaje bez zmian", SHA-256 bazy przed = po |
| start 0.3.1 (druga migracja), `Wroc_do_poprzedniej.cmd` | kod 8 z kopia z 11:54 zamiast nowszej kopii programu z 13:10 (P3) |
| zepsuty 1 bajt w `program\stanowisko\aplikacja.py` paczki 0.3.1 | kod 3 "sumy SHA-256 paczki niezgodne: 1 z 202 plikow", wskaznik, ustawienia i baza bez zmian |
| brak miejsca | nie powtarzano proba (test paczki + mutacja; kontrola miejsca przed usunieciem katalogu: `I:879-890`) |

### 2.5 Kopia bazy z plikiem `-journal` (`proby\goracy_dziennik.py`, `logi\40`)

Baza 20000 wierszy, proces z otwarta transakcja zakonczony `os._exit`: obok bazy `-journal` 5 218 816 bajtow.
`wersja_schematu` = None; kopia `..._vx.sqlite` 5 226 496 bajtow, odczyt: "database disk image is malformed";
`znajdz_kopie(..., schemat_max=1)` zwraca te kopie. Baza po otwarciu do zapisu: 20000 wierszy, 0 niezatwierdzonych. -> P1.

### 2.6 Sondy stanu na malej paczce (`proby\test_rec_a11i.py`, 16 przypadkow, `logi\52`, `53`)

| Sonda | Wynik |
|---|---|
| A: dwa powroty z migracja | po drugim powrocie 3 skany w bazie, 7 w nowszej kopii programu -> P3 |
| B: drugi instalator w trakcie pierwszego | drugi usuwa katalog pierwszego i konczy kodem 0, pierwszy kodem 6 (`FileNotFoundError ... NIEDOKONCZONA.txt`); stan koncowy spojny -> D2 |
| C: przerwana naprawa wersji biezacej | kod 6, "wersja biezaca bez zmian: 1.0" przy wersji biezacej w stanie `niedokonczona`; ponowna proba kod 0 -> P5 |
| D: `folder_millbox = ""` / BOM / CRLF w ustawieniach | kod 7 (rada mylaca) / kod 7 (blad skladni wiersz 1) / kod 0 -> D4 |
| E1: zabicie miedzy zapisem wskaznikow | `biezaca = poprzednia = 1.0`, `wroc` kod 9, ponowna instalacja kod 0 -> D6 |
| E2: blad / zabicie w srodku `przywroc_kopie` (3 przypadki) | 2 z 3: brak pliku bazy, ponowny powrot "GOTOWY" bez bazy -> P2; 1 z 3 (blad nie wystapil): poprawnie |
| F: pliki spoza `SHA256SUMS` w paczce | nie trafiaja do katalogu wersji (kopiowane sa tylko pliki z listy) - dobrze |
| G: kopia bazy nieudana (brak miejsca) | kod 6, wersja nie przelaczona - dobrze |
| H: starsza paczka na baze w nowszym schemacie | instalator sam nie odmawia - polega na samokontroli (umowa A11s: baza nowsza = BLAD); atrapa testowa tego nie sprawdza |
| I: obcy podkatalog w `wersje\` | usuniety -> P4 |
| J: numer wersji rozniacy sie wielkoscia liter / kropka (2 przypadki) | 2 z 2: wersja biezaca wymieniona na budowe z czerwona samokontrola -> P5 |

### 2.7 Skrypty `.cmd` na trudnych sciezkach (`proby\test_rec_cmd.py`, `logi\54`)

7 nazw katalogu paczki i instalacji: `A & B`, `Program Files (x86)`, `Wyk!rzyknik`, nazwa z 7 polskimi literami, `a,b;c=d`,
`it's`, `dasz^ek`; prawdziwe venv i pip (male kolo), katalog biezacy inny, `PYTHONPATH` = pakiety bazowe i `PYTHONHOME` =
zly katalog dla skryptow wzorow. 6 z 7: `zainstaluj.cmd` kod 0 i 5 z 5 skryptow z oczekiwanym kodem (`Stanowisko.cmd` 0,
`Samokontrola.cmd` 0, `Wersje.cmd` 0, `Wroc_do_poprzedniej.cmd` 9, `Polecenie.cmd` 0 bez pakietow bazowych w `sys.path`).
1 z 7 (`;`): kod 6 (D5). `zainstaluj.cmd` przy `PYTHONHOME`: kod 4 w 6 z 6 (D1). Konce linii 6 plikow `.cmd` w commicie:
CRLF w kazdym wierszu (76, 25, 27, 29, 27, 27), same znaki ASCII, brak blokow w nawiasach (same `goto` - stad odpornosc
na `)` i `%ERRORLEVEL%` czytany poza blokiem).

### 2.8 Testy paczki i wstrzykniecia bledu (`proby\mutacje.sh`, `logi\50`, `51`)

`py.cmd -m pytest -q -p no:cacheprovider testy\test_instalacja.py testy\test_zbuduj_wydanie.py`: 50 passed, 42,7 s.
18 mutacji, po kazdej plik przywrocony z gita: 16 wykrytych (przelaczenie wskaznika przed samokontrola, pominiecie kontroli
sum, nadpisanie ustawien, brak kopii bazy, brak blokady programu, przywrocenie bez zgody, kasowanie bazy zamiast
odlozenia, inna budowa zastepuje biezaca, `--system-site-packages`, kod 2 jak 0, brak sprzatania, powrot bez kontroli
schematu; budowa: `testy/` w paczce, data wpisow = teraz, `SHA256SUMS` bez czesci plikow, pliki z katalogu roboczego);
2 niewykryte: M9 `--no-index`, M12 czyszczenie `PYTHONPATH` / `PYTHONHOME` we wzorze (P6).

### 2.9 Testy silnika w srodowisku wersji (P7; `logi\32`-`35`, `proby\seria_silnik.ps1`)

Polecenie: `<K>\Polecenie.cmd -u -X faulthandler -m pytest <kopia rec-a11i>\Ramki\stanowisko\testy\test_silnik.py -v -p no:cacheprovider`
(po `/testy`; wyjscie do pliku, wejscie `NUL`; pierwszy przebieg z `-q` bez opcji diagnostycznych, przebiegi 3 i 4
dodatkowo z `-o faulthandler_timeout=420`); kontrola: to samo przez `py.cmd` z katalogu `Ramki\stanowisko`.

| Srodowisko | Przebiegi | Wynik |
|---|---|---|
| `K1` (wersja 0.3.0, katalog ze spacja, nawiasami i literami spoza ASCII), 12:09-12:38 | 4 | 1 x 59 passed / 5 skipped (242 s); 2 x zawieszenie: w przygotowaniu `test_wynik_silnika_rowny_wierszowi_polecen[wieczorna]` (wyniki silnika juz zapisane; przerwane przeze mnie po ok. 11 min) i w `test_qt_w_procesie_roboczym_zalezy_od_pliku_startowego[True]` (46 PASSED, przerwane po 719 s; mimo `faulthandler_timeout=420` brak zrzutu watkow); 1 x `Windows fatal exception: access violation` w `test_pamiec_pul` przy imporcie modulu, kod procesu 0xC0000005 po 79 s (47 PASSED) |
| `K3` (wersja 0.3.0, katalog ASCII), 12:55-13:09 i 13:22-13:36 | 6 | 4 x 59 passed / 5 skipped (217-221 s); 2 x zawieszenie w `test_qt_offscreen_plytka_bez_zamrozenia_okna` (58 PASSED, przerwane po 480 s i 420 s) |
| interpreter bazowy (`py.cmd`, katalog `Ramki\stanowisko` kopii), 12:41-12:53 i 13:11-13:22 | 6 | 6 x 59 passed / 5 skipped (210-236 s) |

Razem: srodowisko wersji 5 z 10 przebiegow nieudanych (4 zawieszenia, 1 access violation), interpreter bazowy 0 z 6.
Przy 2 z 4 zawieszen sprawdzilem stan: proces pytest nie zuzywal procesora, wszystkie watki czekaly, procesow potomnych nie bylo; przy pozostalych 2 skrypt serii zabil 3 procesy (cmd, proces posredni venv, pytest), czyli potomkow tez nie bylo.
Zastrzezenia: proba mala (dokladny test Fishera, jednostronny, dla 5 z 10 wobec 0 z 6: p = 0,06); serie szly blokami, nie na przemian
(zaplanowane 3 przebiegi przeplatane w `K1` nie odbyly sie z mojego bledu - wersja biezaca `K1` nie miala wtedy pytest);
PC jest wspoldzielony; w tych przebiegach katalog biezacy to katalog programu wersji, a testy i modul `stanowisko` sa
z kopii repozytorium (tak jak w poleceniu T1 z raportu wykonawcy). Programu "Stanowisko" z prawdziwa analiza skanu
w srodowisku wersji nie uruchamialem - 8 startow `Stanowisko.cmd ... --zamknij-po N` w `K1` (6 bez `--atrapa`) zakonczylo sie kodem 0.

### 2.10 Zasady i zakres

`git diff --name-status`: 19 A, 2 M, wszystkie z listy zlecenia; plikow nietykalnych 0; `ustawienia.py`,
`ustawienia.przyklad.toml`, `requirements.txt` bez zmian. Nowe pliki: 0 wierszy spoza ASCII, LF (0 znakow CR), 6 plikow
`.cmd` z CRLF; `README.md` (istniejacy, CRLF i polskie znaki) w swoim stylu. Najwiekszy plik 65 159 bajtow; ZIP, kol
i katalogow roboczych w gicie nie ma. 8 z 8 commitow ze stopka `Co-Authored-By`. Danych osobowych nie znalazlem (w
raporcie wykonawcy 2 razy sciezka interpretera z nazwa konta PC - ta sama, co w `CLAUDE.md`).

## 3. Kryteria zlecenia

| Nr | Kryterium | Ocena |
|---|---|---|
| 1 | 2 budowy = ten sam SHA-256; `SHA256SUMS` zgodne po rozpakowaniu | potwierdzone wlasna proba (2.1) |
| 2 | czysta instalacja, pip `--no-index`, start z `--atrapa` i bez | potwierdzone wlasna proba w `K1` i `K3` (katalogu `robocze\a11i\proba1` nie ruszalem); `--no-index` potwierdzone przegladem `I:319`, bez testu (P6) |
| 3 | srodowisko bez pakietow bazowych, wersje = lista zamrozona | potwierdzone wlasna proba: 0 pozycji bazowych w `sys.path`, 73 z 73 |
| 4 | aktualizacja N -> N+1 jednym poleceniem | potwierdzone wlasna proba (2.4) |
| 5 | powrot do N jednym poleceniem | potwierdzone wlasna proba (powrot bez zmiany bazy i powrot z przywroceniem); wybor kopii przy drugim powrocie: P3 |
| 6 | scenariusz z migracja | potwierdzone wlasna proba (paczka 0.3.1 z probna `MIGRACJE[2]` tylko w kopii drzewa) |
| 7 | bledy: wersja biezaca nietknieta i jasny komunikat | zepsuty plik, brak / zla wersja Pythona, samokontrola kod 1 (pierwsza instalacja), program uruchomiony, zabicie w kroku pip: potwierdzone wlasna proba; brak miejsca i samokontrola kod 1 / 2 przy aktualizacji: potwierdzone testem paczki i mutacja. Wyjatki od "nietknieta": P5 (wymiana wersji biezacej w miejscu), P2 (powrot) |
| 8 | testy na malej paczce w `tmp_path`; pelny pytest 0 failed | testy paczki: potwierdzone wlasna proba (50 passed; 1 test z prawdziwym venv); luka P6. Pelny pytest: wg wykonawcy 1879 passed / 9 skipped / 0 failed na `1437621` (ostatni wiersz logu `robocze\a11i\logi\11_...` widzialem; pozniejsze 2 commity zmieniaja tylko raport i sumy wydania) - niesprawdzone przeze mnie |
| 9 | instrukcja jednostronicowa | potwierdzone przejsciem krok po kroku (58 wierszy); niezgodnosci D7 |

## 4. Zakres plikow i zasady

Zmiany tylko w plikach z listy zlecenia (2.10). Umowa A11s: wywolanie `python -m stanowisko.samokontrola --ustawienia PLIK
--sumy PLIK [--bez-sieci]` zgodne; kody 0 / 1 / 2 obsluzone osobno (inny kod = jak 2); plik `SUMY_PROGRAMU.sha256` w
formacie `sha256sum`, sciezki wzgledne od katalogu programu, 122 z 122 "zgodne" w prawdziwym module; brak modulu w paczce
= kod 3 przed jakakolwiek zmiana. Instalator uzywa tylko biblioteki standardowej. Wskaznik wersji to plik tekstowy,
dowiazan nie ma. Odstepstwa opisane przez wykonawce (Python szukany przed kontrola sum - inaczej sie nie da, do kroku sum
nic nie jest zapisywane; testy razem z kodem; paczka w `<PC-katalog>\wydania` bez samokontroli) przyjmuje.

Ustalenia wykonawcy: (1) "ten sam numer, inna tresc = kod 3" - sluszne, z luka P5a; (2) pierwsza instalacja z kodem 1 -
instalujacy widzi 2 wiersze `BLAD` samokontroli, `BLAD: samokontrola wersji ... zglosila bledy - wersji biezacej nadal nie
ma`, `CO ZROBIC` z pelna sciezka pliku ustawien; wyjscie jednym ruchem (edycja + to samo polecenie, 6 s) zgodne z
instrukcja; (3) `/testy` dziala (76 z 76); (4) `Wersje.cmd` dziala, usuwa tylko wersje nieuzywane (test paczki).

## 5. Do decyzji wlasciciela

1. P7: czy wyjasnienie zachowania testow silnika w srodowisku wersji ma poprzedzac scalenie tej paczki, czy T0 / T1.
2. Pierwsza instalacja konczy sie zawsze czerwonym "INSTALACJA: NIEUDANA (kod 1)", choc to zamierzony etap (ustawienia do
   uzupelnienia). Czy zostawic, czy nazwac inaczej (np. "INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml").
3. `Wroc_do_poprzedniej.cmd` dwuklikiem przelacza wersje od razu, bez pytania (lezy obok `Stanowisko.cmd`); drugi dwuklik
   wraca. Czy dodac pytanie T / N przy uruchomieniu bez argumentow.
4. Przyszly klucz `[sciezki]` z domyslna wartoscia wzgledna zatrzyma aktualizacje kodem 7 do recznej edycji ustawien
   (opisane przez wykonawce). Alternatywa dopuszczona zleceniem: opcjonalny klucz katalogu danych w `ustawienia.py`.
5. Python 3.12 w innej wersji poprawkowej niz 3.12.10: instalator przyjmuje kazde 3.12.x 64-bit; inny `pip` z
   `ensurepip` nie byl sprawdzony (na PC jest tylko 3.12.10). Czy instrukcja ma wskazac konkretna wersje.
6. Paczka w `<PC-katalog>\wydania` (`6464d984...`) jest nieinstalowalna (bez samokontroli, commit 1437621); po scaleniu
   potrzebna nowa budowa i nowy wiersz w `Ramki/etap3/wydania/`. Powtorka T0 w tym samym katalogu wymaga nowego numeru.
7. Niesprawdzone na PC: laptop firmowy (WDAC, antywirus, ostrzezenie Windows przy dwukliku na plik z paczki pobranej
   z sieci, polityka PowerShell dla skrotu), prawdziwy brak miejsca na dysku.
