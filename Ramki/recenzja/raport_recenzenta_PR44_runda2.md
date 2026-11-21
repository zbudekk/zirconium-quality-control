# Raport recenzenta - PR #44 (E3-ODB), runda 2

Data: 21.11.2026 (01:31-01:54). Zakres: `git diff 6e2fb0b..origin/e3/odb -- Ramki/etap3/odbior_koncowy` (7 commitow, 14 plikow,
+1701 / -297), HEAD 5b4c552; calosc paczki `origin/main...origin/e3/odb` = 19 plikow nowych. Miara: `zlecenia/odb-r3.md` (decyzje
koordynatora 1-8), `odb.md`, `odb-r2.md`, plan etapu 3 sekcja 7, notatki proby generalnej `robocze\proba\WYNIK.md`.

Metoda: wlasny przeglad diffu narzedzi (`t2_wieczor.py`, `t3_poranek.py`, `pytest_instalacja.py`, `t12_paczka_migracja.py` w calosci)
i wlasne proby na INSTALACJI PROBNEJ z paczki (`<PC-katalog>\t0\proba\Stanowisko`, wersja 0.3.1 = main + P15) wylacznie przez
`Polecenie.cmd`, z wlasnymi katalogami danych w `koordynator\robocze\rec-odb\runda2\` (baza i pliki instalacji bez zmian: plik bazy
instalacji ma nadal date 01:25; `git status` kopii `rec-odb`, `integ` i klonu proby pusty). Narzedzia z kopii `qc-wt\rec-odb` (5b4c552).
Dwie czesci wykonaly rozgalezienia recenzenta (ten sam kontekst): T9 + czesc F + `dowody_lf.py` / `sql_odczyt.py` / `t13_higiena.py`
(notatki `runda2\czesc_T9_F_notatki.md`) oraz przeglad dokumentow B / C / D bez uruchamiania (notatki `runda2\czesc_BCD_notatki.md`,
z gotowym tekstem kazdej poprawki) - liczby z tych czesci maja oznaczenie "(rozg.)". Pelnego pytest, pelnego T2 / T4 / T10 i budowy
paczki probnej T12 nie uruchamialem.

Uruchomiono: T2 skrocony x 2 z wstrzyknieciami (tor 3), T3 x 2 (czysty + wstrzykniecie), `pytest_instalacja.py` x 2 + zwykly pytest
x 1 (porownanie zrodla kodu), pomiar naglowka kopii bazy, proba T7 B2 + T11 B na programie z instalacji (program x 2, symulator
2 skany `*_r54`, zabicie wlasnego procesu programu; tor 3), `sql_odczyt.py` x 5, kontrola wzorca `t12_paczka_migracja.py`;
(rozg.) T9: 49 przebiegow + 3 kroki planu na instalacji probnej, `dowody_lf.py` na 17 plikach sztucznych, `sql_odczyt.py` 6 obejsc.

## 0. Werdykt i liczby

**Do scalenia po poprawkach.** B 0 / P 5 / D 15.

Obie uwagi blokujace rundy 1 i wszystkie 9 uwag P sa zamkniete (11 z 11) - potwierdzone wlasnymi wstrzyknieciami: T2 3 z 3, T3 1 z 1,
T9 12 z 12 wykonawcy i 13 z 20 wariantow wlasnych (kategorie: wielkosc liter 4 z 4, bez znakow diakrytycznych 4 z 4, `\uXXXX` 3 z 4,
inny separator 2 z 8). Narzedzie dajace "ZAL" niezaleznie od programu nie zostalo: kazdy z trzech sterownikow pada na wstrzyknieciu.
Nowe uwagi P (5) to wylacznie TEKST planu: polecenia albo reguly oceny, ktore w odbiorze dalyby "NIE ZMIERZONO" / falszywy FAIL / test
wykonany w czesci (T7 czesc B, pliki `.cmd` bez `call`, ocena T1, proba dodatnia T9, wzor `--dozwolone t10_`). Kodu narzedzi nie
trzeba zmieniac. Kazda poprawka ma ponizej gotowy tekst (stare -> nowe).

Stan uwag B i P rundy 1:

| Uwaga | Waga | Stan | Dowod (wlasna proba, chyba ze zaznaczono) |
|---|---|---|---|
| 1 | B | zamknieta | proby 1-2: ubytek dopisany do prawdy pracy zielonej -> "lista = prawda: NIE", kod 1; falszywy alarm -> "OK" 1 z 1, nadmiarowych 0; ekran inny niz stan -> przeoczone 2, kod 1 |
| 2 | B | zamknieta | (rozg.) 12 z 12; samotest 281 postaci, 0 nieznalezionych; wielkosc liter ze znakiem diakrytycznym 4 z 4 |
| 3 | P | zamknieta | proba 4: 27 z 32, 5 x "FAIL (ekran)", kod 1 przy `--wymagaj-100`; "wg samego API 32 z 32" podane obok |
| 4 | P | zamknieta | polecenia sa (T8 `:876-879`, T5 B4 `:809-811`, T7 B2 / B3 `:568-583`); T7 B2 wykonane przeze mnie - wymaga poprawki tekstu: nowa uwaga 29 |
| 5 | P | zamknieta | proba 5: w przebiegu `pytest_instalacja.py` `stanowisko.__file__` = katalog programu instalacji; O8 i O14 opisuja to wprost |
| 6 | P | zamknieta | plan `:663-678` (40 skanow, `uklad` = `plytka`, odsylacz do poz. 7 T2); proba 8: 2 z 2 skanow `*_r54` przez program z instalacji, `uklad` = prawda |
| 7 | P | zamknieta | (rozg.) 0 trafien czlonow nazw w stdout, `--wynik` i `--json` w 49 z 49 przebiegow |
| 8 | P | zamknieta | (rozg.) 10 z 10 opcji z planu istnieje; kroki 5, 2, 3 na instalacji probnej: kody 0, 0, 2 (krok 3 zgodnie z planem); zostaja nowe uwagi 32, 33 |
| 9 | P | zamknieta | (rozg.) `dowody_lf.py`: 17 plikow sztucznych, CRLF -> LF, nie-ASCII liczone, binarne / STL / UTF-16 nietkniete; polecenie w planie `:40-44` |
| 10 | P | zamknieta | (rozg., przeglad) `T14/README.md:17-19`, `:41-51`; plan `:1068-1071`; proba generalna: 22 z 22 na instalacji |
| 11 | P | zamknieta | plan `:211-254` (11 polecen, wykonane przez wykonawce 11 z 11 - niesprawdzone przeze mnie); proba 6-7: wzorzec skryptu pasuje do `baza.py`, pomiar naglowka; brak wzmianki w O2: uwaga 34 (D) |

## 1. Uwagi (nowe; numeracja ciagla po rundzie 1)

| Nr | Waga | Plik:linia | Scenariusz | Poprawka (stare -> nowe) |
|---|---|---|---|---|
| 29 | P | `PLAN_TESTOW.md:571-573`, `:576`, `:579` (T7 czesc B, proby 2 i 3) | Wykonane przeze mnie na instalacji probnej (proba 8). (a) Regula PID "nowe PID-y to program (najstarszy z nowych) i jego proces silnika (najmlodszy z nowych)" jest na tym PC niejednoznaczna: program z instalacji to 3 procesy `python` - posrednik `<K>\wersje\<N>\venv\Scripts\python.exe` oraz wlasciwy interpreter i proces silnika, oba ze sciezka `<PC>\...\Python312\python.exe`, TAKA SAMA jak procesy innych wykonawcow; w 60 s od startu doszly 4 cudze procesy `python` (najmlodszy z nowych = cudzy). Skutek wg planu: "NIE ZMIERZONO" obu prob albo zabicie cudzego procesu. (b) Oczekiwany dowod "w `stanowisko.log` komunikat `wznowiono`" nie istnieje: po zabiciu programu i ponownym starcie log ma `(plik zastany - nadrabianie)` i `start, zadan wznowionych 0, plikow znanych 1`, slowo `wznowiono` 0 razy (komunikat idzie tylko na ekran - `aplikacja.py:1309`); wykonawca zapisalby falszywy "brak komunikatu = FAIL". | `:571-573` STARE: "PID programu: przed startem okna 1 zapisz `... Get-Process python \| Select-Object Id,StartTime` do `<ROB>\t7_b2_pid_przed.txt`, po starcie jeszcze raz - nowe PID-y to program (najstarszy z nowych) i jego proces silnika; cudzych PID-ow nie ruszac." NOWE: "PID programu = JEDYNY proces `python` ze sciezka w `<K>\wersje\`: `powershell -NoProfile -Command \"Get-Process python \| Where-Object { $_.Path -like '<K>\wersje\*' } \| Select-Object Id,StartTime,Path\"` - przed startem okna 1 ma dac 0 wierszy, po starcie 1 wiersz (posrednik srodowiska wersji; wlasciwy interpreter i proces silnika maja sciezke Pythona bazowego, taka jak procesy innych wykonawcow - po sciezce ich nie odroznisz). Inna liczba wierszy niz 1 = NIE ZMIERZONO. Zakonczenie posrednika konczy takze interpreter i proces silnika (sprawdzone 21.11: 3 z 3 procesow nie zyje po 1,5 s). Instalacja `<K>` tylko tego wykonawcy." `:576` STARE: "w `<DANE>\logi\stanowisko.log` komunikat `wznowiono`" NOWE: "w `<DANE>\logi\stanowisko.log` wiersz `(plik zastany - nadrabianie)` dla 2. skanu i w zdarzeniach `nowy_skan` z `\"zastany\": true` (`sql_odczyt.py ... \"SELECT typ, dane FROM zdarzenia ORDER BY id\"`); komunikat `wznowiono` jest tylko na ekranie - potwierdza go test czesci A `test_e_awaria_bez_zamkniecia_nadrabianie_folderu`". `:579` STARE: "zakoncz proces potomny silnika (najmlodszy z nowych PID-ow z listy jak w p. 2)" NOWE: "zakoncz proces silnika: z listy `Get-Process python \| Select-Object Id,StartTime,Path` wez procesy ze sciezka Pythona bazowego i `StartTime` w ciagu 5 s po `StartTime` posrednika z p. 2 - maja byc dokladnie 2 (interpreter programu i, mlodszy, silnik); inna liczba = NIE ZMIERZONO (przypadek 1 liczy sie wtedy tylko testami czesci A - wpisz to)". |
| 30 | P | `PLAN_TESTOW.md:45-46` (+ `:206-207`, `:400`, `:618`, bloki T3, T4, T6) | Potkniecie D11 proby generalnej niepoprawione ((rozg.): w planie 0 x `call`). Plan kaze bloki 2-9 polecen uruchamiac "jako jeden plik `.cmd` pod blokada" (T12 B doslownie, `:206-207`). W pliku `.cmd` wywolanie `Polecenie.cmd` / `zainstaluj.cmd` bez `call` konczy caly plik po pierwszym skrypcie - reszta krokow nie jest wykonana (T12 B: tylko krok 2; T4: bez przebiegu cieplego). Moje pliki serii tej rundy dzialaly tylko z `call`. | Dopisac po `:46`: "Blok z wiecej niz jednym poleceniem zapisz jako plik `<ROB>\krok_<nazwa>.cmd` i podaj jego sciezke w `-Polecenie`. W pliku `.cmd` KAZDE wywolanie `Polecenie.cmd`, `Stanowisko.cmd`, `Samokontrola.cmd`, `zainstaluj.cmd`, `Wroc_do_poprzedniej.cmd`, `Wersje.cmd`, `py.cmd` poprzedz slowem `call` - bez `call` plik konczy sie po pierwszym skrypcie i dalsze polecenia NIE sa wykonane. Zaraz po kazdym: `echo <krok> KOD=%ERRORLEVEL% >> <ROB>\kody.txt`. Na poczatku pliku: `set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe` i `set QT_QPA_PLATFORM=offscreen`; wejscie kazdego polecenia `< NUL`." |
| 31 | P | `PLAN_TESTOW.md:301-305` (T1) | Potkniecie P0 poprawione w czesci: brak reguly "wiersz podsumowania + osobno kod wyjscia" i zjawiska 0xC0000409 (0 trafien w planie); stara liczba oczekiwana ("1831 + testy A11s, A11i (91)...") stoi obok nowej (2212). Przebieg z podsumowaniem bez `failed` i kodem 0xC0000409 albo log bez wiersza podsumowania nie ma dzis reguly oceny - a T1 to jeden z 4 testow, ktore maja byc ocenione doslownie. | `:301` STARE: "**Liczby kryterium:** ostatni wiersz logu `N passed, S skipped` - `failed` i `error` maja nie wystapic." NOWE: "**Liczby kryterium:** wiersz podsumowania pytest w logu (`... N passed, S skipped ... in ...s`; `failed` i `error` maja nie wystapic) ORAZ osobno kod wyjscia procesu - oba do `t1_wynik.md`. Brak wiersza podsumowania = NIE ZMIERZONO (powtorz przebieg). Kod 1 i `failed` w podsumowaniu = FAIL. Kod 0xC0000409 (-1073740791) PO wierszu podsumowania bez `failed` / `error` = znane zjawisko zamykania interpretera z Qt (raport E3-A11w): wynik liczy sie z wiersza podsumowania, kod wpisz jako uwage. Suma passed + skipped + failed = liczba z `--collect-only`." `:303-305` STARE: "Oczekiwana liczba testow po scaleniu paczek: 1831 + testy A11s, A11i (91), A11w, A11d, P14 - dokladna liczba = suma z raportow paczek po ostatniej rundzie;" NOWE: "Oczekiwana liczba testow = wynik `--collect-only` na commicie wydania (f5c3e01: 2212, w tym 9 pominietych);". `:329-330` STARE: "Calego pytest w srodowisku wersji nikt jeszcze nie uruchomil (A11w: \"nie zmierzono\")." NOWE: "Caly pytest w srodowisku wersji: proba generalna 21.11 - 2202 passed / 9 skipped / 1 failed, 27 min 20 s, kod 1." |
| 32 | P | `PLAN_TESTOW.md:957`, `:962` (T9 kroki 5-6) | (rozg., zmierzone) Proba dodatnia T9 jest na instalacji domyslnej niespelnialna: `pula_wpisow = false`, program nie wpisuje nazw do bazy (`zlecenia` 0 i `projekty` 0 w bazie instalacji probnej i w bazie T2 proby). Krok 5 da "dozwolone 0", a regula `:962` robi z tego "wynik calego T9 = NIE ZMIERZONO" - test, ktory ma byc oceniony doslownie, nie dostanie wyniku. | `:956` do polecenia kroku 5 dopisac drugi cel: `--cel <ROB T3>\t3\baza` (baza SE10 z nazwami sztucznymi, ktore sa w `N` przez `--baza <baza SE10>`; (rozg.) proba: 33 trafienia dozwolone, kod 0). `:962` STARE: "albo krok 5 da 0 trafien w miejscach dozwolonych: wynik calego T9 = \"NIE ZMIERZONO\"" NOWE: "albo krok 5 da 0 trafien dozwolonych w bazie SE10 (`<ROB T3>\t3\baza`): wynik calego T9 = \"NIE ZMIERZONO\"; 0 trafien dozwolonych w `<DANE>` jest poprawne, gdy `sql_odczyt.py --baza <DANE>\stanowisko.sqlite \"SELECT count(*) FROM zlecenia\"` daje 0 (`pula_wpisow = false`) - zapisz te liczbe". |
| 33 | P | `PLAN_TESTOW.md:945`, `:944` (T9 kroki 1-2) | (rozg., proba) Wzor `--dozwolone t10_` obejmuje takze pliki DOWODU T10 (`t10_wynik.md`, `t10_metryki.json`), bo dowody leza w tym samym katalogu roboczym: nazwa wstrzyknieta do `T10\t10_wynik.txt` daje kod 0 i "ZAL (0 trafien)". Kontrola repo z dowodami jest dopiero "po scaleniu galezi" (`:944`) - nazwa bylaby juz w historii gita. | `:945` STARE: "`--dozwolone t10_ --dozwolone t10.log`" NOWE: "`--dozwolone t10_surowe --dozwolone t10.log`" i w sekcji T10 nazwac surowe wyjscie `t10_surowe*.json` (albo wymienic w `--dozwolone` pelne nazwy plikow surowych; zadnego wzoru, ktory pasuje do pliku z listy dowodow). `:944` STARE: "Powtorz dla worktree z dowodami wszystkich wykonawcow po scaleniu ich galezi." NOWE: "PRZED `git add` dowodow: `T9 N --cel <worktree>\Ramki\etap3\odbior_koncowy\dowody --wynik <ROB>\t9_dowody.txt` BEZ `--dozwolone` - wymagany kod 0; po scaleniu galezi dowodow powtorz krok 1." |
| 34 | D | `RAPORT.md:81` (O2), `:51` | Zmiana sposobu porownania kopii bazy T12 (rozmiar + SHA-256 bajtow od 100.) jest w planie (`:224-232`, `:245`, `:272-273`), ale nie w O2 - wlasciciel czyta `RAPORT.md`. Sama zmiana jest uczciwa (p. 3, T12). | O2 dopisac na koncu: "; kopia bazy sprzed migracji porownywana z baza co do rozmiaru i SHA-256 bajtow od 100. (naglowek SQLite: w kopii inne sa 3 liczniki - zmian pliku, zmian schematu i `version-valid-for`; sumy calych plikow sa rozne) oraz `user_version` i liczby zdarzen osobnym zapytaniem; po powrocie z przywroceniem suma calego pliku bazy = suma pliku kopii". `:51`: "kopia = baza sprzed _" -> "kopia = baza sprzed (rozmiar _, skrot bez naglowka _, user_version _, zdarzen _)". |
| 35 | D | `RAPORT.md:86` (O7) | (rozg.) Koncowka "pamiec = proces roboczy + okno" jest sprzeczna z planem `:741-743` (mierzony szczyt jednego procesu, okno z raportu A5) - reszta uwagi 18. | "pamiec = proces roboczy + okno" -> "pamiec: w odbiorze mierzony szczyt JEDNEGO procesu (`szczyt_mb`); szczyt procesu okna niemierzony - do sumy liczba z raportu E3-A5 (ok. 1,0 GB)". |
| 36 | D | `RAPORT.md:60-62`, `:94` (O14), `:100`; `PLAN_TESTOW.md:736`, `:591`, `:737` | "10 z 14 testow moze dostac najwyzej ZAL z odstepstwem" to przesada dla T6 i T11 (p. 3) i warunkowo dla T4, T7; O14 wymienia T1, a `:60` mowi "T1 bez odstepstwa". | `:60-62` NOWE: "Bez odstepstwa moga byc zaliczone T1, T8, T9, T10 oraz - do potwierdzenia przez koordynatora - T6 (sekcja 7: \"na sztucznym arkuszu\") i T11 (40 z 40 pierwsza galezia \"albo\"); T4 i T7 - gdy nie zajdzie przypadek z O7 / O12; pozostale (T0: O1; T12: O2; T2: O3, O4, O13; T3: O5; T5: O8, O14; T13: O10, O11) maja najwyzej \"ZAL z odstepstwem\"." `:94` kolumna Test: "T5, T6, T7 czesc A, T1" -> "T5, T6, T7 czesc A (T1: informacja, nie odstepstwo)". Plan `:591`: "ZAL z odstepstwem (komunikat..." -> "ZAL z odstepstwem O12 (komunikat..."; `:737`: dodac "O7". |
| 37 | D | `RAPORT.md:18` | (rozg.) Dowody maja trafic do `odbior_koncowy/dowody/T<nr>/` (plan `:36-38`), a szkielet podaje sciezki wzgledem `odbior_koncowy/` (`T0/`...). | "dowody = sciezki wzgledem `Ramki/etap3/odbior_koncowy/`" -> "... `Ramki/etap3/odbior_koncowy/dowody/`". |
| 38 | D | `PLAN_TESTOW.md:542-543`; listy dowodow `:600`, `:823`, `:867` | (rozg.) T7 czesc A: przypadki maja po 2-4 pliki testow, a jeden log `t7_<nr>.log` z `>` - kolejne polecenie nadpisuje poprzednie; na listach dowodow brak `*_zrodlo_kodu.txt`. | "log `<ROB>\t7_<nr><a,b,c>.log`, wynik `t7_<nr><a,b,c>_zrodlo_kodu.txt` - osobne polecenie na kazdy plik testow"; dopisac pliki do list dowodow T5, T6, T7. |
| 39 | D | `PLAN_TESTOW.md:664-666`, `:674` (T11 B) | Zmierzone (proba 8): skan `*_r54` 47,5 s przy puli zimnej i 27,4 s przy cieplej; `--zamknij-po 2100` ma 300 s zapasu na start, pule i kolejke. Skan bez wiersza w `skany` w chwili zamkniecia liczylby sie jako FAIL skanu. | "`--zamknij-po` = ... = 2100" -> "= 3000"; dopisac: "skan z dziennika symulatora bez wiersza w `skany` w chwili zamkniecia programu = NIE ZMIERZONO (powtorz z dluzszym czasem), nie FAIL". |
| 40 | D | `PLAN_TESTOW.md:799-816` (T5 B) | (rozg., z odczytu kodu) Krok 4 kaze pisac `plytka 1`, `stan` "w konsoli atrapy", a krok 1 uruchamia ramke W przez `-m ramka` (bez konsoli; `--help` na instalacji sprawdzone przeze mnie: opcje z planu istnieja); brak "przywroc `[ramki]`" przed T7 B na tej samej instalacji. | Krok 1: obie role przez `narzedzia\atrapa_ramki.py --rola W\|P --host ... --port ... --sterowanie`; po kroku 5: "przywroc `[ramki]` w `<K>\ustawienia.toml` (kopia pliku sprzed kroku 3)". |
| 41 | D | `PLAN_TESTOW.md:1075-1077`, `:1108` | (rozg.) `:1075-1076` dopuszcza T1 rownolegle z seria pomiarowa, `:1092` i `:1106` zabraniaja; nie ma reguly, kiedy W3 uruchamia kroki z silnikiem. | `:1075-1076` NOWE: "T1 (2 przebiegi po 30-45 min) nie biegnie w czasie T2, T4, T10 ani T11 czesc B - W1 wykonuje T1 przed startem serii W2 albo po niej; W3 kroki z silnikiem (T5 B4, T7 `test_silnik`, B2 / B3) tak samo - godziny podaje koordynator." (najkrotsza sciezka zegarowa: ok. 5-5,5 h, nie 4 h). |
| 42 | D | `PLAN_TESTOW.md:945`, `:940` | (rozg.) T9 krok 2: `--cel ...\robocze\odbior` obejmuje instalacje T12 B (ok. 2,6 GB - wniosek, niezmierzone); wzor `stanowisko.kopia_` nie pasuje do kopii instalatora `kopie\stanowisko_przed_<wersja>_<data>_v<n>.sqlite` (proba: kod 1, falszywy FAIL w kroku 2). | `:945` dopisac `--wyklucz \wersje\ --wyklucz \paczka_M\ --wyklucz \drzewo_M\`; `:940` "`--dozwolone stanowisko.kopia_`" -> "`--dozwolone \kopie\stanowisko_`". |
| 43 | D | `PLAN_TESTOW.md:134`, `:140-142` (T0) | (rozg.) Samokontrola w T0 tylko z `--bez-sieci`, choc pelna jest wykonalna (proba generalna: kod 0, ZIELONA). | Krok 6: dodac `<K>\Samokontrola.cmd --json > <ROB>\t0_samokontrola.json` (bez `--bez-sieci`). |
| 44 | D | `PLAN_TESTOW.md:6-7`, `:13`, `:561` | (rozg.) Zdania nieaktualne (A11d "do potwierdzenia"); "17 przypadkow" (`test_p14_baza_zajeta.py` ma 27 testow - reszta potkniecia D12). | `:561` "17 przypadkow" -> "27 testow na f5c3e01"; `:6-7`, `:13` usunac albo "(stan 20.11)". |
| 45 | D | `narzedzia/t9_dane_osobowe.py:150-151`; `PLAN_TESTOW.md:982` | (rozg.) Nazwa z innym separatorem nie jest znajdowana jako cala nazwa w 6 z 8 wariantow (`_` -> spacja, spacja -> `-`, `-` -> spacja, `+`, dwie spacje, `_` -> `-`): kod 0, "ZAL - czlony do wyjasnienia: 2" (czlony sa zgloszone, wiec nie jest to ciche ZAL); JSON w JSON (`\\u0142`) 1 z 4 nie; cp852, iso-8859-2, NFD, `%XX`, `\xNN` nie sa szukane ani wymienione w "Nie szuka". | `if znak == " ": zbior \|= {"_", "%20"}` -> `if znak in " _-": zbior \|= {" ", "_", "-", "+", "%20"}`; `:982` dopisac cp852, iso-8859-2, NFD, `%XX`, `\xNN`. Tanie - warto zrobic razem z P. |
| 46 | D | `narzedzia/dowody_lf.py:87`, `:22`; `narzedzia/t9_dane_osobowe.py:92-93` | (rozg.) `dowody_lf.py --napraw` na pliku tylko do odczytu = nieobsluzony `PermissionError` w polowie katalogu, bez pliku `--wynik`; `.csv` jest w `TEKST`, a `t13_higiena.py:33` zglasza `.csv` jako dane; `--baza` wskazujaca plik nie-SQLite obok `--nazwy-z` = kod 0 bez ostrzezenia. | `try / except OSError` -> naruszenie; usunac `.csv` z `TEKST`; wypisac liczbe nazw z kazdego zrodla. |
| 47 | D | `narzedzia/pytest_instalacja.py:129-130`, `:144`; `narzedzia/t2_wieczor.py:892` | Werdykt "INSTALACJA" i kod 0 takze wtedy, gdy licznik "pliki instalacji = repo" pokazuje pliki ROZNE (a to jedyny dowod dla procesow potomnych); w wyniku T2 "'Ukruszona' wykonanych 2 z 3 zaplanowanych" liczy jako zaplanowana takze prace celowo pominieta (proba 1). | `werdykt`: przy `rozne or brak` -> "INSTALACJA (UWAGA: pliki instalacji rozne od repo: n)" i kod 3; T2: mianownik = decyzje bez wyniku "POMINIETA". |
| 48 | D | uwaga 23 rundy 1 | Odlozona przez wykonawce (O10 doprecyzowane, grupa `NIETYKALNE` niewypisywana). | bez zmian - do decyzji wlasciciela p. 5.6. |

## 2. Wlasne proby

Wszystkie na instalacji probnej przez `<K>\Polecenie.cmd` (`K` = `<PC-katalog>\t0\proba\Stanowisko`), `QT_QPA_PLATFORM=offscreen`;
pliki w `koordynator\robocze\rec-odb\runda2\`.

| Nr | Polecenie (skrot) | Wynik |
|---|---|---|
| 1 | T2, wstrzykniecie (a)+(b): `t2_wieczor.py --dane-ref runda2\t2_ref --wybierz 2 --odstep 5 --wymagaj-zal` (kopia prawdy plytki nr 2: gniazdo 3 - cale, zielone - dostaje ubytek; gniazdo 2 - ubytek, czerwone - bez ubytku); tor 3 | kod 1; "lista = prawda: NIE; ubytki wg prawdy 3: czerwone 0, zolte 2, zielone (przeoczone) 1; nieklikniete 1 z 3; falszywe alarmy 1 z 6"; "OK" 1 z 1; lista: brakuje 1, nadmiarowych 0 (falszywy alarm listy nie psuje); ponowien 0, czekan na ochrone 0; procesy potomne po sprzataniu []. Wykryte 2 z 2 |
| 2 | T2, wstrzykniecie (c): nakladka `t2_wstrz_ekran.py` - mapa RYSUJE gniazda o klasie stanu "czerwony" kolorem zielonym (stan i baza bez zmian), `--wybierz 3` | kod 1; "zielone (przeoczone) 2", "kolor z ekranu inny niz klasa w stanie programu: 2 z 9 prac"; 'Ukruszona' 1 z 3; lista: brakuje 2. Kolor pochodzi z obrazu widzetu (`mapa.grab()`), nie ze stanu ani z bazy. Wykryte 1 z 1 |
| 3 | T3 czysty: `t3_poranek.py --testy <ST>\testy --wymagaj-100` | kod 0; 32 z 32; "WERDYKT T3: ZAL z odstepstwem O5 (ekran: tak 8, czesciowo 1, nie dotyczy 1, nie 0)" |
| 4 | T3, wstrzykniecie: nakladka `t3_wstrz_ekran.py` (odczyt `tabela_kompletne` inny niz stan - to samo co proba 8 rundy 1) | kod 1; "27 z 32 ...; wg samego API sesji 32 z 32"; 5 wierszy "FAIL (ekran)"; "WERDYKT T3: FAIL". Wykryte 1 z 1 (runda 1: kod 0, "32 z 32") |
| 5 | `pytest_instalacja.py --st <ST> --wynik ... -- <ST>\testy\test_excel.py runda2\skad\test_skad.py -k "test_skad or zapytan"` wobec `Polecenie.cmd -m pytest` z tymi samymi plikami | `pytest_instalacja`: kod 0, `stanowisko.__file__`, `excel`, `aplikacja` = `K\wersje\0.3.1\program\stanowisko\...`; "z instalacji 18 modulow, z repo poza testami 0, modulow testow z repo 2; pliki = repo 79 z 79; WERDYKT ZRODLA KODU: INSTALACJA". Zwykly pytest: te same moduly z `...\proba\repo\Ramki\stanowisko\...`. "Z repo" zostaja: pliki testow z `conftest.py`, plik `<ST>\ustawienia.toml` (stala `PLIK_USTAWIEN` ustawiana w procesie testow) i kod w procesach potomnych, gdy test podaje im katalog repo - O14 mowi to wprost |
| 6 | Naglowek kopii bazy (T12): kopia bazy instalacji probnej (86 016 B) mechanizmem `backup` (jak `instalator.py:677`), porownanie bajtow | rozne 3 bajty: 27 (licznik zmian pliku 21 -> 1), 43 (licznik zmian schematu 17 -> 1), 95 (`version-valid-for` 21 -> 1); bajty od 100. identyczne, rozmiar rowny; polecenie z planu `:224` wykonane w `cmd`: 2 z 2 te same wartosci; zmiana `user_version` w kopii zmienia tylko naglowek (bajt 63) - skrot od 100. jej nie widzi, plan sprawdza `user_version` osobno |
| 7 | `t12_paczka_migracja.py`: wzorzec na `baza.py` z integ; wiersz o innej postaci; `--roboczy` w repo | 1 -> 2, skladnia zmienionego pliku poprawna; "pasuje 0 razy" (odmowa); kod 2. Budowy paczki nie powtarzalem (wg wykonawcy 11 z 11 kodow - niesprawdzone) |
| 8 | T7 B2 + T11 B na programie z instalacji z WLASNYM plikiem ustawien (kopia `K\ustawienia.toml`, baza / logi / eksport w `runda2\t7`): `Polecenie.cmd -m stanowisko.aplikacja --ustawienia ... --zamknij-po 400` (= `Stanowisko.cmd` z innym plikiem ustawien; tor 3), `Polecenie.cmd narzedzia\symulator_skanera.py --folder ... --zrodla <r54_P2> <r54_P3a> --ile 2 --odstep 45 --rownolegle 1 --seed 1 --dziennik ...`, po 2. zapisie `Stop-Process` wlasnego posrednika, ponowny start | symulator kod 0, 2 pliki; przed startem 0 procesow ze sciezka `K\`, po starcie 1 (posrednik) + 2 ze sciezka Pythona bazowego; w 60 s 4 cudze nowe procesy `python`; po `Stop-Process` posrednika 3 z 3 nie zyje (1,5 s), kod programu -1; po ponownym starcie (kod 0 po `--zamknij-po 170`): `skany` 2 z 2, `uklad` = `plytka` z prawdy 2 z 2 (`uklad_zrodlo` auto, bez operatora), czasy 47,5 s i 27,4 s; `zdarzenia`: `program_start` z `znane_pliki` 1, `nowy_skan` z `zastany` true; w logu `wznowiono` 0 razy; pliku `zadania_niezakonczone.json` nie ma. Polecenia dzialaja; tekst planu do poprawy (uwaga 29) |
| 9 | `Polecenie.cmd -m ramka --help` (T5 B krok 1) | kod 0; opcje `--rola --sprzet --host --port --sterowanie-atrapy` istnieja. Przebiegu T5 B (3 procesy, adres karty) nie wykonalem |
| 10 | (rozg.) T9: 12 wstrzykniec wykonawcy + wlasne; kroki 5, 2, 3 planu na instalacji probnej | 12 z 12; (a) 4 z 4, (b) 3 z 4, (c) 4 z 4, (d) 2 z 8; czlony nazw w dowodach 0 w 49 z 49; kody 0, 0, 2; pusta lista / brak katalogu / same krotkie nazwy = kod 2 |
| 11 | (rozg.) `dowody_lf.py` na 17 plikach sztucznych; `sql_odczyt.py` 6 obejsc; `t13_higiena.py` (nowy) na integ f5c3e01 | bez `--napraw` 0 zmienionych; binarne nietkniete; 6 z 6 obejsc odrzuconych kodem 2; T13: kod 1, 1 naruszenie poza paczka (p. 5.2) |

Odpowiedzi na pytania zlecenia:

- **Ochrona klikniec P15:** sterownik przed kazda czynnoscia sprawdza `okno.ochrona_aktywna()` i `mapa.przygaszona()` i czeka (licznik
  `czekan_na_ochrone`, raz na epizod); klikniecie bez skutku (widok pokazuje inna prace po 0,3 s albo decyzja nie weszla w 1 s) ponawia
  od klikniecia gniazda (licznik `ponowien`); oba liczniki sa w wyniku przy kazdej decyzji i lacznie; limit 60 s na decyzje konczy sie
  "NIEWYKONANA" = brak na liscie = FAIL (strona bezpieczna). W moich 2 przebiegach na main + P15: ponowien 0, czekan 0 (wykonawca: 2
  czekania). Ochrony w chwili klikniecia nie wymuszalem - sciezka ponowien potwierdzona tylko przegladem kodu.
- **O13:** opisuje zmiane uczciwie (lista z klikniec sterownika na pracach czerwonych / zoltych, kolor z obrazu mapy, zielona = FAIL listy,
  wykrywalnosc mierza T10 / T16, prac zoltych calych nie klika). Brakuje jednego zdania: sterownik zaklada, ze technik ogladajacy prace
  zolta zawsze zauwazy ubytek (zolte, czyli niewykryte przez program: 7 z 12 ubytkow w probie wykonawcy i w mojej probie rundy 1, 2 z 3 w probie 1) - liczby sa w wierszu T2.
- **Zmiana kryterium T12:** uczciwa. Porownanie "rozmiar + SHA-256 bajtow od 100." obejmuje cala tresc wszystkich tabel (kazda strone
  pliku poza 100-bajtowym naglowkiem), jest wiec ostrzejsze niz porownanie zrzutu SQL; poza skrotem zostaja tylko liczniki naglowka i
  `user_version`, ktore plan sprawdza zapytaniem. Sekcja 7 wymaga "baza zmigrowana z kopia" - rownosc kopii z baza jest dodatkiem planu,
  nie oslabieniem kryterium. Opisana jawnie w planie; w `RAPORT.md` O2 jej nie ma (uwaga 34).

## 3. Kryteria

Kryterium z sekcji 7 planu etapu jest w kazdej sekcji przepisane doslownie: 14 z 14 ((rozg.), porownane z tabela).

| Test | Co mierzy PLAN_TESTOW po zmianach | Ocena | Wykonalnosc (polecenia / dowody / liczenie / czas) |
|---|---|---|---|
| T0 | 2 starty kod 0, samokontrola, SHA-256 ZIP + licznik sum, `pip.log` | slabsze z O1 (konieczne: nowego konta i odciecia sieci nie ma) | komplet; wykonane w probie generalnej; uwaga 43 |
| T1 | wiersz podsumowania + lista `-rs` | rowne; dzis wynik = FAIL (`test_b1_blokada...` pada interpreterem wersji) - plan NIE oslabia | komplet; regula kodu wyjscia: uwaga 31; krok 5 niewykonany |
| T2 | sterownik, kolory z ekranu, 5 werdyktow + "T2 LACZNIE" | start / mapa rowne albo ostrzejsze; okno z O3, O4; lista wg decyzji 1 z O13 (pelne) | komplet; pelny przebieg niewykonany (proby skrocone: wykonawca, proba generalna, moje 2) |
| T3 | n z 32 liczone z ekranu, "WERDYKT T3" | rowne z O5 (pelne) | komplet; wykonane (proba 3) |
| T4 | `metryki_pula` zimna / ciepla / jakosc | slabsze z O7 (decyzja r2 nr 6; na liscie decyzji wlasciciela); opis pamieci w O7: uwaga 35 | komplet; pomiary niewykonane |
| T5 | pytest 127.0.0.1 na kodzie z instalacji + przebieg ramki W na adresie karty | slabsze z O8, O14 (pelne) | czesc A wykonana (wg wykonawcy); czesc B niewykonana, uwaga 40 |
| T6 | `test_excel.py` na arkuszu w pamieci, kod z instalacji | rowne (sekcja 7: "na sztucznym arkuszu"); O9 jawne, mozliwe ze zbedne | komplet; wykonane (wg wykonawcy; moja proba 5 czesciowo) |
| T7 | testy na kodzie z instalacji + 3 proby reczne | slabsze z O12 (decyzja r2 nr 3, warunkowe), O14 | czesc A wykonana (wg wykonawcy); czesc B: B2 wykonane przeze mnie - uwaga 29; uwaga 38 |
| T8 | `raport_metryk` na bazach T2 / T3 + liczenie reczne | rowne | komplet; sciezki baz spojne (`:447`, `:522`, `:876-879`) |
| T9 | `t9_dane_osobowe.py` na repo, logach, wynikach, ruchu | rowne; narzedzie poprawione | uwagi 32, 33, 42, 45; kroki 1 i 4 na instalacji niewykonane |
| T10 | `metryki_P3a` 24 + 16 | rowne | komplet; pelny niewykonany |
| T11 | 40 skanow `*_r54` przez aplikacje, pierwsza galaz "albo" | ostrzejsze (O6) | komplet; czesc B: 2 z 40 wykonane przeze mnie (proba 8); uwaga 39 |
| T12 | A: N -> N+1 -> N; B: paczka probna z migracja | rowne z O2; porownanie kopii opisane w planie, nie w O2 (uwaga 34) | komplet; A wykonane (proba generalna), B wykonane (wg wykonawcy) |
| T13 | `t13_higiena.py` od 2537f6f | slabsze z O10, O11 (jawne) | komplet; wykonane |

Razem (14): rowne 5 (T1, T6, T8, T9, T10); ostrzejsze 1 (T11) + T2 start / mapa; slabsze z jawnym odstepstwem 8 (T0, T2, T3, T4, T5,
T7, T12, T13); **slabsze bez pelnego odstepstwa: 0** (runda 1: 3). Opis w `RAPORT.md` wezszy niz w planie w 2 miejscach (O2, O7 -
uwagi 34, 35; D).

Odstepstwa O1-O14: nazwane uczciwie, z informacja, co zmierzono zamiast - O1, O3, O4, O5, O6, O8, O9, O10, O11, O12, O13, O14 (12 z 14);
do uzupelnienia jednym zdaniem O2 i O7. Decyzja 7 spelniona: `RAPORT.md:13-17` ("ZAL z odstepstwem NIE jest ZAL"), `:58-59` (cztery
osobne liczniki, suma 14), `:68`, sekcja 4a (15 pozycji, kazde O<n> ma wiersz); odstepstwa zamieniajace FAIL w "ZAL z odstepstwem"
(O7, O11, O12) sa na liscie decyzji wlasciciela (4a poz. 3, 9, 12).

"10 z 14 najwyzej ZAL z odstepstwem" - ocena: odstepstwo KONIECZNE (kryterium niewykonalne doslownie na tym PC) w T0, T2, T3, T5, T12,
T13. Przesada: T6 (arkusz w pamieci jest "sztucznym arkuszem" z sekcji 7) i T11 (40 z 40 rozpoznanych spelnia "albo" doslownie pierwsza
galezia; brak B5 to osobna sprawa do decyzji). Warunkowe: T4 (plan `:736` sam mowi "wszystkie do 40 s = ZAL") i T7 (O12 dziala tylko
przy komunikacie spoza zal. F, O14 tylko przy werdykcie "REPO"). **Doslownie wg sekcji 7 da sie na tym PC wykonac: T1, T8, T9, T10,
T6, T11; warunkowo T4 i T7** (uwaga 36).

Potkniecia proby generalnej wobec planu (20 pozycji: B1, B2, P0-P3, D1-D12, 2 x "UWAGA do planu"; (rozg.), wiersze w notatkach):
poprawione 17 (w tym D2 - dotyczy instrukcji, nie planu; P3 bez `set PY` - w poprawce uwagi 30), czesciowo 2 (P0 - uwaga 31; D12 -
uwaga 44), niepoprawione 1 (D11 - uwaga 30). Sprawdzone przeze mnie w pliku: `<REPO>` z LF i kontrola `core.autocrlf` (`:60`), 2212
i `--collect-only` (`:307-310`), regula dla `test_b1_blokada...` = FAIL bez oslabiania (`:310-316`), `pip.log` jako dowod "bez
internetu" (O1), `/python %PY%` w poleceniach instalatora, `PY -I` w T12, 210 plikow (`:213`).

Podzial na wykonawcow ((rozg.), `:1051-1108`): instalacje rozlaczne (`czysta` dla W1 z T0 / T12 A / T1; `w2`, `w3`; T12 B w osobnej
`<KB>` w katalogu roboczym), sterowniki T2 / T3 pisza do `<ROB>`, nie do `<DANE>`; seria T10 -> T4 -> T2 -> T11 u jednego wykonawcy
w jednym torze; T9 na koncu; T8 po T2 i T3. Kolizje: uwaga 41 (T1 a seria), uwaga 29 (PID-y na wspolnym PC), uwaga 42.

Kryteria rundy (`odb-r3.md`):

| Kryterium | Stan |
|---|---|
| 1. Raport paczki: sekcja "Runda 1 recenzji", tabela 1-28 | potwierdzone przegladem (rozg.) |
| 2. B1, B2, P3: FAIL osiagalny | potwierdzone wlasna proba (1, 2, 4) i (rozg.) proba 10 |
| 3. Proby T3 caly, T2 skrocona z tabela kolorow, T9 z nazwami sztucznymi | potwierdzone wlasna proba (3; 1-2 z tabela kolorow; 10) |
| 4. Commit po kazdej uwadze, `git status` pusty | 7 commitow; stanu worktree wykonawcy nie sprawdzalem |
| decyzja 6: KAZDE polecenie planu wykonane przynajmniej raz | niespelnione w 7 miejscach - wypisane wprost w planie `:1155` (T2 pelny, T4, T5 B, T7 B, T10 pelny, T11 B, T1 krok 5); T7 B2 i T11 B (2 skany) wykonalem - dzialaja, z poprawka tekstu (uwaga 29) |
| decyzje 1-5, 7 wpisane do planu i raportu | potwierdzone przegladem (`RAPORT.md` poz. 18-23, O13, O14) |

## 4. Zakres plikow i zasady

- (rozg.) 19 plikow, wszystkie nowe, 0 poza `Ramki/etap3/odbior_koncowy/`; od rundy 1 doszly `dowody_lf.py`, `pytest_instalacja.py`,
  `t12_paczka_migracja.py`. Najwiekszy: `PLAN_TESTOW.md` 110 296 B; STL / ZIP / baz 0.
- (rozg.) ASCII + LF: 0 bajtow powyzej 127, 0 CR i 0 NUL w 19 z 19 plikow (tresc z gita).
- (rozg.) Dane osobowe: 435 nazw folderow i plikow z 3 katalogow prac - 0 trafien calych nazw w 19 plikach; 1 czlon jako cale slowo,
  2 trafienia (slowo pospolite).
- D 12-28 rundy 1: 12 zamknieta, 13 zamknieta, 14 zamknieta, 15 zamknieta, 16 zamknieta, 17 zamknieta, 18 zamknieta (reszta: uwaga 35),
  19 zamknieta, 20 zamknieta, 21 zamknieta, 22 zamknieta, 23 odlozona, 24 zamknieta, 25 zamknieta, 26 zamknieta, 27 zamknieta,
  28 zamknieta (12-14, 19: moj przeglad diffu i proby 1-4; reszta (rozg.)).
- Sprzatanie: po probach 0 moich procesow `python`; cudzych nie ruszalem (zabity 1 proces - wlasny posrednik programu z proby 8).
  Instalacja probna, kopie `integ`, `rec-odb` i klon proby bez zmian.

## 5. Do decyzji wlasciciela / koordynatora

1. T1 na interpreterze wersji da dzis FAIL (1 failed: `test_aplikacja.py::test_b1_blokada_znika_razem_z_procesem`, wlasnosc testu
   w `venv`; proba generalna 6 z 6). Plan slusznie nie oslabia - potrzebna poprawka testu w paczce programu przed budowa wydania albo
   jawne odstepstwo.
2. (rozg.) T13 nowym `t13_higiena.py` na f5c3e01 da FAIL: 1 naruszenie poza paczka (`Ramki/stanowisko/raporty/E3-A6_2026-11-18.md`,
   1 samotne CR; proba generalna miala 0, bo uzyla narzedzia sprzed poprawki uwagi 22) - poprawka 1 bajtu przed commitem wydania.
3. Czy T6 i T11 moga dostac "ZAL" bez odstepstwa, gdy liczby beda w normie (uwaga 36); czy "ZAL z odstepstwem" liczy sie jako
   zaliczenie konca etapu (4a poz. 1).
4. T2: sterownik zaklada, ze technik zauwazy ubytek w kazdej pracy zoltej (w probach wiekszosc ubytkow byla zolta, nie czerwona) -
   O13 / 4a poz. 2.
5. T7 B3 (zabicie silnika na programie z paczki) na wspolnym PC moze skonczyc sie "NIE ZMIERZONO" - przypadek 1 liczony wtedy
   testami czesci A (uwaga 29).
6. O10 (T13): pliki nietykalne zmienione od poczatku etapu nadal niewyroznione (uwaga 23 odlozona).

WERDYKT: do scalenia po poprawkach (B 0; P 5: uwagi 29-33 - sam tekst PLAN_TESTOW.md; D 15: uwagi 34-48); uwagi 1-11 rundy 1 zamkniete 11 z 11
