# Raport recenzenta - PR #39 (E3-A11i, paczka wydania, instalacja, aktualizacja, powrot - wariant B), runda 3

- Data: 20.11.2026, 22:35-22:58, PC, konto `<konto-PC>`. Recenzja przyrostowa po poprawkach wykonawcy; runda 3 z 3.
- Zakres: commity `7f18cdf..223d27f` galezi `e3/a11i` (4 commity z kodem, testami, instrukcja i opisem modulu: 68529ad,
  1f6e353, 0b8b0ef, 223d27f; 4 pliki, 351 wierszy dodanych, 45 usunietych) + commit d14f91c (22:41, sam raport paczki,
  253 wiersze - sprawdzony na koncu). HEAD objety recenzja kodu: **223d27f**; HEAD galezi w chwili konca recenzji: d14f91c
  (`git fetch origin` 22:55: brak nowszych commitow). Calosc `git diff main...origin/e3/a11i --stat`: 21 plikow.
- Metoda: wlasny przeglad diffu rundy 3 (`instalator.py`, testy, instrukcja, opis modulu) i prawdziwego modulu samokontroli
  (`origin/e3/a11s` 6befc0d = plik w kopii integracyjnej `qc-wt\integ`, porownanie bez roznic); potem wlasne proby; raport
  wykonawcy (sekcja 13) czytany na koncu. Pliki robocze: `<PC-katalog>\koordynator\robocze\rec-a11i\runda3\` (dalej `R3`):
  `logi\` (pomiary), `proby\` (skrypty: `glowna.py`, `glowna2.py`, `test_rec_r3.py`, `test_rec_r3b.py`, `mutacje_r3.sh`).
- Uruchomiono: testy paczki po jednym pliku (22 + 90 passed); 3 budowy paczki z klonu kopii integracyjnej a2236c1
  (0.3.1, 0.3.2 z `--wersja`, 0.3.3 z kopii drzewa z latka recenzenta w module samokontroli - tylko do proby); PROBA GLOWNA
  na prawdziwej instalacji z prawdziwym modulem samokontroli (24 kroki, 2 pelne instalacje srodowiska) i proba dodatkowa
  (9 krokow, 1 pelna instalacja srodowiska) - obie przez `narz\ciezki.ps1 -Tor 4 -Kto rec-a11i`; 60 sond na malej paczce
  z prawdziwym procesem samokontroli-atrapy; 10 wstrzykniec bledu (7 zleconych + 3 dodatkowe; 10 z 10 wykrytych). Pelnego pytest nie
  uruchamialem. Naraz najwyzej 2 procesy python recenzenta w krokach lekkich (seria wstrzykniec w kopii `rec-a11i`, sondy
  i testy paczki w osobnej czystej kopii plikow 223d27f w `R3\kod`, porownanie bajtowe z commitem: bez roznic).
- Sprzatanie: usuniete instalacje probne (`R3\K` 2,7 GB), rozpakowane paczki, 3 pliki ZIP, klon drzewa i kopia z latka;
  zostaly logi, skrypty, pliki `.sha256` i kopia `R3\kod` (27 MB). Kopia recenzenta `qc-wt\rec-a11i`: HEAD 223d27f,
  `git status --short` pusty. W kopii integracyjnej, w worktree wykonawcy i w repo glownym niczego nie zmienialem
  (klon `git clone --shared` do `R3\drzewo` tylko czyta obiekty). Cudzych procesow nie dotykalem.
- Pomylki wlasne (bez wplywu na wynik): pierwszy start proby glownej nieudany z mojego bledu w cudzyslowach polecenia
  (0 krokow, log `20_glowna_*_nieudany_start.log`); w sondach E i F pierwszej serii "awaria" okazala sie wyjatkiem Pythona
  (kod 1), wiec prawdziwy kod 0xC0000005 sprawdzilem osobno (seria `41`, proba dodatkowa krok B); pierwsze uruchomienie
  testow paczki ze zla sciezka (0 testow), drugie miarodajne.

## 0. Werdykt

**Do scalenia.** B 0, P 0, D 4.

Uwaga P1 rundy 2 jest zamknieta i potwierdzona wlasna proba na prawdziwej instalacji z prawdziwym modulem samokontroli:
same bledy folderow = kod 10 WSTRZYMANA; baza nowsza niz program (sama albo razem z bledami folderow) = kod 1 NIEUDANA
z wierszami `BLAD` i lista sprawdzen spoza ustawien; modul bez wiersza koncowego (blad importu), proces ginacy z kodem
0xC0000005 i wiersz obcy po wyniku = kod 2. W zadnym z 33 krokow na prawdziwej instalacji i w zadnej z 40 sond samokontroli
wersja nie zostala przelaczona przy kodzie innym niz 0 (i zawsze przy 0). Bledow wprowadzonych poprawkami nie znalazlem.
Zostaja 4 uwagi drobne (1 odlozona z rundy 1, 3 nowe) - zadna nie narusza danych ani nie przelacza wersji bez zgody.

## 1. Uwagi

Linie: `I` = `Ramki/stanowisko/instalacja/instalator.py` (stan 223d27f).

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| D1 | D | `I:955-964` | (= D1 rundy 2, D6 rundy 1; wykonawca: odlozone, 13.1) Zabicie procesu miedzy zapisem `wersja_poprzednia.txt` a `wersja_biezaca.txt` zostawia oba wskazniki z ta sama wersja; `Wroc_do_poprzedniej.cmd` = kod 9, program dziala, ponowne `zainstaluj.cmd` naprawia. W rundzie 3 nie powtarzane (kod bez zmian). | Moze zostac. |
| D2 | D | `I:1014-1018`, `I:1398` | Klasyfikacja "blad ustawien" patrzy tylko na NAZWE sprawdzenia. Prawdziwy modul nadaje nazwe sprawdzenia takze bledom, ktore nie sa ustawieniami: `wykonaj` zwraca `BLAD folder_skanera: sprawdzenie przerwane bledem programu (...)` albo `... nie zakonczylo sie w N s` (samokontrola.py:1304-1314). Pierwsza instalacja z takim wierszem = kod 10, "WSTRZYMANA - uzupelnij ustawienia.toml" (sonda M: kod 10; przy aktualizacji kod 1). Wymaga bledu w module samokontroli albo zawieszonego folderu; wiersz `BLAD` z prawdziwa przyczyna i rada "zglos" jest na ekranie nad wierszem koncowym; wersja nie jest przelaczana. Wykonawca opisal przypadek limitu czasu (13.2, p. 6). | Za blad ustawien uznawac `folder_*` / `operatorzy` / `ustawienia` tylko wtedy, gdy opis nie zaczyna sie od "sprawdzenie przerwane" / "sprawdzenie nie zakonczylo sie"; albo zostawic. |
| D3 | D | `I:1480-1483`; `opisy_modulow/instalacja.md:147` | `Wroc_do_poprzedniej.cmd` uruchomione przez proces bez uchwytu wejscia (`sys.stdin` = `None`, np. uruchomienie odlaczone od konsoli): `input()` rzuca `RuntimeError`, ktorego `zapytaj_konsole` nie lapie - wynik `BLAD: nieoczekiwany blad (RuntimeError: lost sys.stdin)`, `POWROT: NIEUDANA (kod 6)` zamiast `ANULOWANY (kod 11)` (sonda `41`: kod 6, wersja bez zmian). Opis modulu podaje "brak konsoli" = kod 11. Zwykle uruchomienia sa poprawne: wejscie z `NUL`, pusty potok, sam Enter = kod 11 (proba glowna, 7 z 7). | `except (EOFError, OSError, RuntimeError)`. |
| D4 | D | `I:1626-1662` (`main`, `argparse`) | Opcja z literowka (`zainstaluj.cmd /nieznana-opcja`): kod 2 biblioteki `argparse`, tekst `usage: ... error: unrecognized arguments` po angielsku, bez wiersza koncowego `INSTALACJA: ...` (wlasna proba `logi\23`: kod 2). Kod 2 w instrukcji i opisie modulu znaczy "samokontroli nie dalo sie wykonac". Stan od rundy 1, zglosil go sam wykonawca (13.3, uwaga a); niczego nie zmienia na dysku. | Wlasny komunikat po polsku i wiersz koncowy "niczego nie zmieniono" (albo dopisek w wierszu kodu 2). |

### 1.1 Uwagi rundy 2 - stan

| Uwaga r2 | Stan | Dowod z wlasnej proby |
|---|---|---|
| **P1** pierwsza instalacja: kazdy kod 1 = "WSTRZYMANA - uzupelnij ustawienia.toml" | **zamknieta** | Prawdziwa instalacja, prawdziwy modul (`logi\20_glowna_wyniki.log`): krok 1 (wzor ustawien) = kod 10, 2 wiersze `BLAD` (`folder_skanera`, `folder_cyrkon`), `WSTRZYMANA`; krok 1a (to samo + baza o schemacie 5) = **kod 1**, `Bledy samokontroli wersji 0.3.1 (3):`, `CO ZROBIC: ... Sprawdzenia spoza ustawien: baza - tego NIE poprawi wpisanie folderow ...; foldery (folder_skanera, folder_cyrkon) popraw w <plik>`, `INSTALACJA: NIEUDANA (kod 1) - wersja biezaca bez zmian: brak`; krok 1b (foldery poprawione, baza v5 - przypadek z rundy 2) = **kod 1**, 1 wiersz `BLAD baza`, slowa "WSTRZYMANA" nie ma; po usunieciu bazy kod 0. Proba dodatkowa (`logi\30`): blad importu modulu = kod 2 "nie podala wyniku ... To nie jest blad ustawien - nie zmieniaj pliku ustawienia.toml" (3 uruchomienia), 0xC0000005 x 3 = kod 2 "zakonczyla sie awaryjnie". Sondy (2.3): 40 z 40 zgodnych z opisem modulu. Nazwy: 21 z 21 prawdziwych sprawdzen sklasyfikowanych zgodnie z opisem (4 x `folder_*`, `operatorzy`, `ustawienia` = ustawienia; 15 pozostalych = nie). Wstrzykniecia M1, M2, M5, M6 wykryte. |
| D1 dwa wskazniki | otwarta (odlozona) | bez zmian w kodzie; teraz D1 |
| D2 luka latki `.pth` | zamknieta | Prawdziwa instalacja: plik usuniety z wersji biezacej, `zainstaluj.cmd /testy` = kod 0; w wyjsciu wiersz "dolozono plik stanowisko_bez_wmi.pth" (nr 10) przed "dokladam zestaw testowy" (nr 11); po probie `_wmi` = `None` w srodowisku (`logi\22`). Sonda: plik jest przy kazdym z 3 wywolan pip (`pip list`, `pip install`, `pip list`). Wstrzykniecie M3 wykryte przez test wykonawcy. |
| D3 ostatni wiersz samokontroli | zamknieta | jak P1: kod 0 / 1 bez zgodnego ostatniego wiersza = 3 proby i kod 2 (sondy D, G, I; proba dodatkowa A i C); przy powrocie tylko ostrzezenie (krok G: kod 0, "bez wiersza koncowego SAMOKONTROLA: (nie podala wyniku)") |
| D4 `PermissionError` przy zamianie pliku bazy | zamknieta | Sonda z prawdziwym drugim uchwytem pliku bazy (bez transakcji): kod 5, "baza ... jest zajeta przez inny program (... pliku ... nie da sie zamienic ...)", "Zamknij programy ...", baza bajt w bajt, `.nowy` sprzatniety; po zamknieciu uchwytu kod 0. Ten sam komunikat dostaje plik bazy z atrybutem "tylko do odczytu" (sonda D4b: kod 5) - przyczyna inna niz w tekscie, przypadek skrajny, bez osobnej uwagi. Wstrzykniecie M4 wykryte. |
| D5 kod 4 skryptow nieopisany | zamknieta | instrukcja: osobny wiersz kodu 4 dla 4 skryptow; opis modulu: 5 skryptow; 5 z 5 wzorow `.cmd` ma `exit /b 4` w `:brak_wersji` (przeglad) |
| D6 testy do wstrzykniec R2, R4, R6 | zamknieta | R2, R4, R6 wykryte (2.4); pytanie T / N na prawdziwej instalacji: wejscie z `NUL`, sam Enter, `tak`, `n`, `N`, spacja, pusty potok = 7 z 7 kod 11 i wersja bez zmian; `T`, `t`, `T ` (ze spacja) = zgoda |

## 2. Wlasne proby

`PY` = `<PC>\AppData\Local\Programs\Python\Python312\python.exe`, `K` = `R3\K`, `P1` / `P2` / `P3` = rozpakowane
paczki 0.3.1 / 0.3.2 / 0.3.3. Kroki na instalacji: `cmd /s /c "<polecenie>"`, wejscie z urzadzenia pustego (chyba ze
podano odpowiedz), Qt offscreen, 2 watki; czas z zegara monotonicznego skryptu.

### 2.1 Testy paczki (kopia `R3\kod` = 223d27f, po jednym pliku)

| Polecenie | Wynik |
|---|---|
| `py.cmd -m pytest -q -p no:cacheprovider testy/test_zbuduj_wydanie.py` | **22 passed**, 6,8 s |
| `py.cmd -m pytest -q -p no:cacheprovider testy/test_instalacja.py` | **90 passed**, 137,3 s (rownolegle z seria wstrzykniec) |

Razem 112 passed - zgodne z raportem wykonawcy (112 passed, 127,9 s).

### 2.2 PROBA GLOWNA - paczka z kopii integracyjnej (a2236c1 = `e3/a11i` 223d27f + `e3/a11s` + `e3/a11w` + `e3/p14`)

Budowa (klon `git clone --shared` kopii integracyjnej w `R3\drzewo`, tryb domyslny = tresc commita):
`py.cmd narzedzia\zbuduj_wydanie.py --wyjscie R3\wydanie --kola <PC-katalog>\wydania\kola` = kod 0, 7 s,
`Stanowisko_0.3.1.zip`, 444 145 046 B, SHA-256 `5f348279...80e2`, 202 pliki + `SHA256SUMS` (program 123, kola 73, kola
testowe 3), "kontrola wlasna sum: zgodne"; to samo z `--wersja 0.3.2` = kod 0, 5 s, 444 145 046 B, `ef0ad9c5...1914`.
Opcje instalacji spoza domyslnych: `/katalog K /python PY /bez-pauzy /bez-sieci`.

| Krok | Polecenie | Kod | Czas | Ostatnie wiersze / stan |
|---|---|---|---|---|
| 1 | `P1\zainstaluj.cmd ...` (pusty katalog, ustawienia ze wzoru) | **10** | 70,5 s | `SAMOKONTROLA: CZERWONA (ok 11, ostrzezenia 8, bledy 2)`; "Wersja 0.3.1 jest zainstalowana, ale jeszcze NIE jest wersja biezaca"; 2 wiersze `BLAD` z rada modulu ("otworz plik ustawien <pelna sciezka> i popraw klucz [sciezki] ..."); `Plik ustawien: ...`; `CO ZROBIC: otworz plik ustawien w Notatniku ...`; `INSTALACJA: WSTRZYMANA ... (kod 10)`. Wskaznika wersji i skryptow w `K` nie ma. |
| 1a | baza o schemacie 5 w `K\dane` + to samo polecenie (blad ustawien + inny blad naraz) | **1** | 3,8 s | `CZERWONA (ok 11, ostrzezenia 7, bledy 3)`; `Bledy samokontroli wersji 0.3.1 (3):` + 3 wiersze `BLAD`; `BLAD: samokontrola wersji 0.3.1 zglosila bledy - wersji biezacej nadal nie ma`; `CO ZROBIC:` wymienia `baza` jako sprawdzenie spoza ustawien i 2 foldery do poprawienia w pliku; `INSTALACJA: NIEUDANA (kod 1) - wersja biezaca bez zmian: brak`. Wersja nie przelaczona. |
| 1b | 4 foldery i `operatorzy` wpisane, baza v5 zostaje (przypadek P1 rundy 2) | **1** | 3,8 s | `CZERWONA (ok 16, ostrzezenia 4, bledy 1)`; 1 wiersz `BLAD baza: baza nowsza niz program ...; zainstaluj wersje programu, ktora zalozyla te baze, albo nowsza ...`; `NIEUDANA (kod 1)`; "WSTRZYMANA" 0 razy. Wersja nie przelaczona. |
| 2 | baza v5 usunieta, to samo polecenie | **0** | 4,1 s | `ZIELONA (ok 16, ostrzezenia 5)`, "wersja biezaca: 0.3.1; poprzednia: brak", `INSTALACJA: GOTOWA`; 5 skryptow w `K`; SHA-256 ustawien w krokach 1b i 2 ten sam |
| 3 | `K\Samokontrola.cmd --bez-sieci` | 0 | 2,4 s | `ZIELONA (ok 16, ostrzezenia 5)`, sumy 122 z 122, nadmiarowych 0 |
| 3 | `K\Stanowisko.cmd --atrapa --zamknij-po 5` / `--zamknij-po 5` | 0 / 0 | 6,7 s / 7,9 s | program startuje i zamyka sie; baza zalozona (schemat 1) |
| 3b | plik `.pth` usuniety z `wersje\0.3.1\venv`, `P1\zainstaluj.cmd ... /testy` | 0 | 6,5 s | "dolozono plik stanowisko_bez_wmi.pth" przed "dokladam zestaw testowy"; `ZIELONA (ok 17, ostrzezenia 4)`; `GOTOWA` |
| 4 | `P2\zainstaluj.cmd ...` (aktualizacja do 0.3.2) | **0** | 73,2 s | kopia `kopie\stanowisko_przed_0.3.2_20261120_224201_v1.sqlite`; `ZIELONA (ok 17, ostrzezenia 4)`; "wersja biezaca: 0.3.2; poprzednia: 0.3.1"; SHA-256 ustawien i bazy przed = po |
| 4 | `K\Stanowisko.cmd --zamknij-po 5`; `K\Wersje.cmd` | 0; 0 | 8,0 s; 0,2 s | 0.3.1 poprzednia, 0.3.2 BIEZACA |
| 5 | `K\Wroc_do_poprzedniej.cmd /bez-pauzy`: wejscie z `NUL`, sam Enter, `tak`, `n`, `N`, spacja, pusty potok | **11** x 7 | po 0,2 s | pytanie `Powrot z wersji 0.3.2 do wersji 0.3.1. Kontynuowac? [T/N]:`; `POWROT: ANULOWANY (kod 11) - wersja biezaca bez zmian: 0.3.2. Odpowiedz T przelacza wersje; w skryptach: Wroc_do_poprzedniej.cmd /tak`; wskazniki i baza bez zmian |
| 5 | to samo, odpowiedz `T` | **0** | 2,7 s | `POWROT: GOTOWY - wersja biezaca 0.3.1 (poprzednia: 0.3.2)`; SHA-256 bazy i ustawien przed = po; `Stanowisko.cmd --zamknij-po 5` na 0.3.1 = kod 0 (7,9 s) |
| 5 | odpowiedz `t` (mala) / `T ` (ze spacja) / opcja `/tak` | 0 / 0 / 0 | 2,8 s / 2,8 s / 4,0 s | kazda przelacza (0.3.1 -> 0.3.2 -> 0.3.1 -> 0.3.2); koniec: 0.3.2 BIEZACA, 0.3.1 poprzednia |

Samokontrola prawdziwego modulu w tej probie: 10 uruchomien przez instalator / powrot + 1 przez `Samokontrola.cmd`,
0 awarii procesu, 0 przypadkow "wynik niezgodny z umowa" (po wierszu `SAMOKONTROLA:` modul niczego nie wypisuje).
Dziennik instalacji (`logi\21`, 171 wierszy): wyniki `WSTRZYMANA` / `NIEUDANA (kod 1)` x 2 / `GOTOWA` x 3 / `ANULOWANY` x 7 /
`GOTOWY` x 4; wiersze samokontroli jako poziom + nazwa sprawdzenia bez opisu; nazw osob 0 (sciezki tylko katalogu proby).

### 2.3 Proba dodatkowa na prawdziwej instalacji i sondy

Paczka 0.3.3 zbudowana z kopii drzewa (`--zrodlo`, `--data`, `--commit proba-recenzenta-r3`; 444 148 751 B, `29e2ccde...e7d8`),
w ktorej modul samokontroli ma na poczatku latke recenzenta sterowana zmienna `REC_SAMOKONTROLA` (kopia robocza, usunieta).

| Krok | Stan / polecenie | Kod | Czas | Wynik |
|---|---|---|---|---|
| A | `P3\zainstaluj.cmd ...`, modul rzuca `ImportError` przy imporcie (kod 1 Pythona, sam slad wyjatku) | **2** | 80,0 s | 3 uruchomienia; `BLAD: samokontrola wersji 0.3.3 nie podala wyniku (kod wyjscia 1 bez wiersza koncowego SAMOKONTROLA: CZERWONA, proby: 3) - wersja biezaca zostaje 0.3.2`; `CO ZROBIC: To nie jest blad ustawien - nie zmieniaj pliku ustawienia.toml. Uruchom zainstaluj.cmd ponownie ...; gdy to sie powtarza, zglos ...`; biezaca 0.3.2 |
| B | to samo, proces konczy sie kodem 0xC0000005 | **2** | 8,1 s | 3 x `UWAGA samokontrola: proces zakonczyl sie awaryjnie (kod 0xC0000005), proba i z 3`; "zakonczyla sie awaryjnie ... To nie jest blad ustawien"; biezaca 0.3.2 |
| C | to samo, kod 0 i wiersz `ZIELONA`, po nim obcy wiersz na wyjsciu standardowym | **2** | 19,2 s | "nie podala wyniku (kod wyjscia 0 bez wiersza koncowego SAMOKONTROLA: ZIELONA, proby: 3)"; biezaca 0.3.2 (kod 0 bez zgodnego ostatniego wiersza nie jest zielony) |
| D | `K\Samokontrola.cmd --bez-sieci`; `K\Stanowisko.cmd --atrapa --zamknij-po 5` (wersja biezaca po 3 nieudanych probach) | 0; 0 | 2,3 s; 6,7 s | wersja 0.3.2 nietknieta |
| E | `P3\zainstaluj.cmd ...` bez zaklocen | **0** | 3,6 s | srodowisko nie jest budowane drugi raz; biezaca 0.3.3, poprzednia 0.3.2 |
| F, H | `K\Wroc_do_poprzedniej.cmd /bez-pauzy /tak` | 0; 0 | 2,5 s; 2,6 s | 0.3.3 -> 0.3.2 |
| G | powrot 0.3.2 -> 0.3.3, samokontrola informacyjna z bledem importu | 0 | 6,7 s | `OSTRZEZENIE: samokontrola wersji 0.3.3 zakonczyla sie kodem 1 bez wiersza koncowego SAMOKONTROLA: (nie podala wyniku)`; `POWROT: GOTOWY` (zgodnie z opisem: po powrocie samokontrola jest informacyjna) |

Sondy na malej paczce (`proby\test_rec_r3.py`, `test_rec_r3b.py`; prawdziwy proces modulu-atrapy; wyniki `logi\40`, `41`):

| Przypadek (pierwsza instalacja / aktualizacja) | Kod instalatora | Procesy samokontroli |
|---|---|---|
| A: 2 x `BLAD folder_*`, kod 1, `CZERWONA` | **10** / 1 | 1 |
| B: `BLAD baza` | 1 / 1 | 1 |
| C: `folder_skanera` + `baza` + `folder_cyrkon` | 1 / 1 (rada wymienia `baza` i osobno 2 foldery) | 1 |
| D: blad importu (kod 1, slad wyjatku) | 2 / 2 | 3 |
| G: wiersze `BLAD folder_*` bez wiersza koncowego, kod 1 | 2 / 2 | 3 |
| E2: kod 0xC0000005 bez wyjscia; F2: wiersze `BLAD` + `CZERWONA`, potem 0xC0000005; F3 / F4: `ZIELONA`, potem 0xC0000005 / 0xC0000142 | 2 / 2 (4 przypadki) | 3 |
| H: kod 0, ostrzezenia, `ZIELONA` | 0 / 0 (przelaczona) | 1 |
| I: kod 0, `ZIELONA`, potem obcy wiersz na stdout | 2 / 2 | 3 |
| J: kod 0, `ZIELONA`, obcy wiersz na stderr | 0 / 0 (przelaczona) | 1 |
| K: kod 2, `BLAD ustawienia` + `NIEWYKONANA` | 2 / 2 ("nie dalo sie wykonac ... popraw przyczyne podana powyzej") | 1 |
| L: kod 1, `CZERWONA`, 0 wierszy `BLAD` | 1 / 1 ("(samokontrola nie wypisala zadnego wiersza BLAD)") | 1 |
| M: `BLAD folder_skanera: sprawdzenie przerwane bledem programu` | 10 / 1 (uwaga D2) | 1 |
| N: `BLAD dane_folder` | 1 / 1 | 1 |
| O: wiersz `BLAD` z wcieciem i CRLF; P: slowo BLAD w opisie ostrzezenia | 10 / 1 | 1 |
| E, F pierwszej serii (wyjatek Pythona po wypisaniu `CZERWONA`: kod 1 + slad na stderr) | 2 / 2 (E), 10 / 1 (F - zgodnie z umowa: kod 1 i ostatni wiersz stdout `CZERWONA`) | 3 / 1 |

Razem 40 przypadkow samokontroli (20 x pierwsza instalacja / aktualizacja): w 40 z 40 wersja przelaczona wtedy i tylko
wtedy, gdy kod instalatora = 0 (asercja sondy). Pozostale sondy: nazwy prawdziwego modulu 21 z 21 (1.1); pytanie T / N
z prawdziwym plikiem na wejsciu, 14 tresci: zgoda dla `T\n`, `t\r\n`, `T` (bez Entera), `T \r\n`, ` t\n`, `t\nN\n`
(liczy sie pierwszy wiersz); brak zgody dla pustego, `\n`, `\r\n`, `tak\n`, `n\n`, `N\n`, `TT\n`, BOM + `T\n`; wejscie
z `NUL` = brak zgody; `sys.stdin` = `None` = D3; D4 (1.1); `.pth` (1.1) oraz srodowisko, w ktorym pliku nie da sie zapisac:
kod 6 z rada, wersja biezaca bez zmian.

### 2.4 Wstrzykniecia bledu (`proby\mutacje_r3.sh`, `logi\50_mutacje.log`, kopia `rec-a11i` 223d27f)

Przebieg: caly `testy/test_instalacja.py` bez testu prawdziwego srodowiska, `pytest -x`; po kazdym wstrzyknieciu plik wraca z gita.

| Nr | Wstrzykniecie | Wynik | Test, ktory pada pierwszy |
|---|---|---|---|
| M1 | klasyfikacja bledow ustawien odwrocona (`blad_ustawien` zwraca negacje) | wykryte (1 failed, 1,7 s) | `test_czysta_instalacja_najpierw_wstrzymana_po_poprawce_ustawien_gotowa` |
| M2 | brak wiersza koncowego nie jest sprawdzany (`wiersz_koncowy_zgodny` = `True`: kod 1 bez wiersza traktowany jak czerwona, czyli kod 10 przy bledach folderow) | wykryte (1 failed, 66 passed) | `test_r3_p1_brak_wiersza_koncowego_to_samokontrola_niewykonana[slad_wyjatku-pierwsza_instalacja]` |
| M3 | plik `.pth` dopiero po pip (wczesne dolozenie wylaczone) | wykryte (1 failed, 79 passed) | `test_r3_plik_blokady_wmi_jest_przed_pierwszym_procesem_pip_w_wersji_starszego_instalatora` |
| M4 | `PermissionError` przy zamianie pliku bazy = kod 6 | wykryte (1 failed, 35 passed) | `test_p2_przerwane_przywrocenie_kopii_nie_zostawia_stanowiska_bez_bazy[blad_syste...]` |
| R2 | `przywroc_kopie` bez kontroli pliku `-journal` (niewykryte w rundzie 2) | wykryte (1 failed, 81 passed) | `test_r3_przywrocenie_kopii_zatrzymuje_plik_journal_obok_bazy` |
| R4 | sam Enter = zgoda (niewykryte w rundzie 2) | wykryte (1 failed, 80 passed) | `test_r3_pytanie_t_n_sam_enter_i_kazda_odpowiedz_inna_niz_t_to_brak_zgody` |
| R6 | kopia bazy pomijana przy dowolnej identycznej kopii (niewykryte w rundzie 2) | wykryte (1 failed, 82 passed) | `test_r3_kopia_bazy_jest_pomijana_tylko_przy_identycznej_najnowszej_kopii` |

**Wynik zlecony: 7 z 7 wykrytych** (4 nowe w kodzie rundy 3 + 3 niewykryte w rundzie 2). Dodatkowe (ponad zlecenie):
M5 usuniety warunek "kod 0 / 1 bez wiersza koncowego = kod 2" - wykryte (1 failed, 66 passed); M6 WSTRZYMANA takze przy
bledach mieszanych - wykryte (1 failed, 63 passed); M7 `tak` znow jest zgoda - wykryte (1 failed, 80 passed). Razem 10 z 10. Wykonawca: 5 z 5 na wyborze `-k r3`
(R2, R4, R6 i 2 nowe) - zgodne z moimi wynikami dla tych samych wstrzykniec.

## 3. Kryteria zlecenia

| Nr | Kryterium | Ocena w rundzie 3 |
|---|---|---|
| 1 | 2 budowy = ten sam SHA-256; `SHA256SUMS` zgodne | sumy: potwierdzone wlasna proba (3 budowy "kontrola wlasna sum: zgodne"; instalator w kroku 1 sprawdza 202 z 202 przy kazdej z 3 instalacji); rownosc 2 budow: potwierdzone testem paczki (22 passed), wlasnej pary budow tego samego numeru nie robilem; kod budowy w rundzie 3 bez zmian |
| 2 | czysta instalacja bez sieci, start z `--atrapa` i bez | potwierdzone wlasna proba (kroki 1-3), prawdziwy modul samokontroli |
| 3 | srodowisko bez pakietow bazowych, wersje = lista zamrozona | potwierdzone przegladem (kod bez zmian w rundzie 3; instalator sam porownuje pakiety z lista przy kazdej instalacji - 3 instalacje bez roznic); wlasny pomiar 73 z 73 w rundzie 2 |
| 4 | aktualizacja N -> N+1 jednym poleceniem | potwierdzone wlasna proba (krok 4; drugi raz krok E) |
| 5 | powrot do N jednym poleceniem | potwierdzone wlasna proba (krok 5: odpowiedz `T` albo `/tak`) |
| 6 | scenariusz z migracja | potwierdzone wlasna proba w rundzie 2; w rundzie 3 zmiana w tej sciezce to tylko D4 (sonda z prawdziwym uchwytem + testy paczki), prawdziwej instalacji z migracja nie powtarzalem |
| 7 | bledy: wersja biezaca nietknieta i jasny komunikat | samokontrola kod 1 (3 odmiany), wynik bez wiersza koncowego, awaria procesu: potwierdzone wlasna proba na prawdziwej instalacji; baza trzymana innym uchwytem: sonda; pozostale (zepsuty plik, brak Pythona, program uruchomiony, brak miejsca): testy paczki + proby rund 1-2 |
| 8 | testy na malej paczce; pelny pytest 0 failed | testy paczki: potwierdzone wlasna proba (112 passed); pelny pytest na 223d27f: wg wykonawcy W TOKU (22:55 log `robocze\a11i\logi_r3\90_pytest_pelny_223d27f.log` doszedl do ok. 80 %, same kropki) - **niesprawdzone, wynik sprawdza koordynator** |
| 9 | instrukcja jednostronicowa | potwierdzone przegladem i proba: 69 wierszy; kazdy komunikat koncowy z proby glownej i dodatkowej (kody 0, 1, 2, 10, 11) ma wiersz w tabeli p. 6 o tym samym znaczeniu; punkt 2.4 mowi, co znaczy `NIEUDANA (kod 1)` zamiast `WSTRZYMANA` |

Zgodnosc trojstronna kodow 0-11 (`instalator.py` + skrypty / instrukcja p. 6 / tabela w opisie modulu) - porownanie wlasne:
**12 z 12** (runda 2: 11 z 12). Kody zmienione w rundzie 3: 1 (pierwsza instalacja z bledem spoza ustawien), 2 (trzeci
komunikat "nie podala wyniku"), 4 (drugie znaczenie: skrypty katalogu instalacji), 5 (odmowa dostepu przy zamianie pliku
bazy, `-journal`), 10 ("wszystkie bledy dotycza ustawien"), 11 ("inna niz T, takze sam Enter"). Jedyne rozejscie z opisem:
"brak konsoli" przy `sys.stdin` = `None` (D3) i kod 2 biblioteki `argparse` (D4). Skrypty: `zainstaluj.cmd` i 4 wzory
(`Samokontrola`, `Stanowisko`, `Wersje`, `Wroc_do_poprzedniej`) zapamietuja `%errorlevel%` w `KOD` i koncza `exit /b %KOD%`,
`Polecenie.cmd` konczy `exit /b %errorlevel%`; w probie kody 0, 1, 2, 10, 11 instalatora doszly do `cmd /c` bez zmiany.

## 4. Zakres plikow i zasady

- `git diff --name-status main...origin/e3/a11i`: 21 plikow, wszystkie z listy zlecenia (19 nowych, zmienione `README.md`
  i `opisy_modulow/README.md`); runda 3: 4 pliki + raport. Plikow nietykalnych 0; `baza.py`, `ustawienia.py`,
  `ustawienia.przyklad.toml`, `requirements.txt`, `samokontrola.py`, `aplikacja.py` bez zmian (schemat bazy nietkniety).
- Pliki nowe: 0 znakow CR i 0 wierszy spoza ASCII; 6 plikow `.cmd`: CR = LF w kazdym wierszu (81, 25, 27, 29, 36, 38);
  `README.md` (istniejacy) w swoim stylu (CRLF, polskie znaki), `opisy_modulow/README.md` (istniejacy) LF. Dodane wiersze
  rundy 3: 0 spoza ASCII.
- ZIP, kol i katalogow roboczych w gicie nie ma (najwiekszy plik galezi: raport paczki 108 501 B, potem `instalator.py` 104 314 B). Danych osobowych
  w diffie rundy 3 nie znalazlem (testy: sciezki wzorcowe i `tmp_path`). 5 z 5 commitow rundy 3 ze stopka `Co-Authored-By`.
- Umowa A11s na prawdziwym module 6befc0d: wywolanie bez zmian; kod wyjscia ORAZ ostatni wiersz stdout (`ZIELONA` /
  `CZERWONA`); format `BLAD <nazwa>: <opis>; <rada>` - instalator czyta nazwe wyrazeniem `BLAD ([^:\s]+):` (zgodne
  z `Sprawdzenie.wiersz`). Lista "bledow ustawien" (`folder_*`, `operatorzy`, `ustawienia`) wobec 21 nazw modulu: bez
  literowek; `operatorzy` jest w module tylko ostrzezeniem, `ustawienia` z poziomem BLAD wychodzi z kodem 2 (obslugiwany
  osobno) - oba wpisy sa zapasem i szkody nie robia. Do wiadomosci A11s: po wierszu `SAMOKONTROLA:` modul nie moze
  niczego wypisac na wyjscie standardowe (dzis nie wypisuje - 11 uruchomien w probie glownej); taki wiersz zatrzymalby kazda instalacje
  kodem 2 (proba dodatkowa, krok C).
- Raport wykonawcy, sekcja 13 (d14f91c) wobec moich pomiarow: testy paczki 112 passed - zgodne; pierwsza instalacja kod 10
  i `ok 11, ostrzezenia 8, bledy 2` - zgodne; baza v5 po poprawie folderow kod 1 - zgodne (u wykonawcy `ok 15, ostrzezenia 5`,
  u mnie `ok 16, ostrzezenia 4`, bo wpisalem tez `operatorzy`); zgodnosc kodow 12 z 12 - zgodne; wstrzykniecia 5 z 5 -
  zgodne; rozmiar paczki inny (444 132 217 B wobec 444 145 046 B), bo inne drzewo (bez A11w i P14). Rozbieznosci nie
  znalazlem. Wykonawca uczciwie wypisal, czego nie sprawdzil na prawdziwej instalacji (wynik bez wiersza koncowego, `.pth`
  na wersji bez pliku, D4 z prawdziwym uchwytem) - te trzy rzeczy sprawdzilem sam (2.2 krok 3b, 2.3). Wynik pelnego
  pytest w raporcie: "W TOKU" - **raport rundy 3 w tej czesci niesprawdzony** (koordynator sprawdzi log i dopisany commit).

## 5. Do decyzji wlasciciela

1. Mieszane bledy przy pierwszej instalacji (foldery ze wzoru + np. baza) daja `NIEUDANA (kod 1)`, a nie `WSTRZYMANA` -
   przyjete domyslnie przez wykonawce; uwazam to za wlasciwe (komunikat wymienia osobno, co poprawic w pliku, a co nie).
2. Slowo `tak` nie jest juz zgoda na pytanie T / N (tylko `T` / `t`) - zmiana wobec rundy 2, zgodna z instrukcja; do
   wiadomosci autora instrukcji technika (A11d).
3. Nieudana proba pierwszej instalacji z baza w `dane\` zostawia kopie w `dane\kopie\` (krok 1a: 1 plik) - kopie nie sa
   kasowane automatycznie (decyzja z rundy 2, bez zmian).
4. Niesprawdzone na PC, jak w rundach 1-2: laptop firmowy (WDAC, antywirus, znacznik pliku z sieci), prawdziwy brak
   miejsca, Python 3.12.x inny niz 3.12.10, dwuklik w Eksploratorze, katalog domyslny `C:\Stanowisko`.
5. Paczka koncowa do T0 / T12 musi powstac z `main` po scaleniu A11s, A11w, A11d i tej galezi; moje paczki probne
   (z a2236c1 i z kopii z latka) usunalem - sumy w `R3\wydanie\*.sha256` nie sa wydaniem.

WERDYKT: do scalenia (B 0, P 0, D 4)
