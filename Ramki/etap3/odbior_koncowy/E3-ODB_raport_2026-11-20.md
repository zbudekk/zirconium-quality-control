# E3-ODB - przygotowanie odbioru koncowego etapu 3 - raport paczki (20.11.2026)

Galaz `e3/odb` od `main` 9ba9e91. Praca: 20.11.2026, 20:14 - ok. 20:40 (limit etapu 55 min; calosc w jednym etapie). Paczka dokumentow i skryptow pomocniczych: kodu programu nie zmienia, testow koncowych NIE wykonuje, pelnego
pytest nie uruchamiano (zgodnie ze zleceniem).

## 1. Zakres i pliki (wszystkie nowe, tylko `Ramki/etap3/odbior_koncowy/**`)

| Plik | Co to jest |
|---|---|
| `PLAN_TESTOW.md` | przepis T0-T13: kryterium doslownie, gdzie (paczka / repo), dane na PC, polecenia, zrodlo liczb, dowody, czas, ciezar, pulapki, braki; podzial na 4 wykonawcow; lista "sprawdzone przez --help / w kodzie" |
| `ODLOZONE.md` | T15, T16, T17 i otwarte 4-6 z 19.11: powod, czego brakuje, warunek wznowienia, co gotowe, pierwszy krok |
| `RAPORT.md` | szkielet raportu koncowego: wydanie, tabela T0-T17, definicja konca etapu, odstepstwa O1-O10, FAIL i poprawki, braki B1-B6, zadania wlasciciela, decyzje domyslne |
| `T14/README.md` | co wlasciciel dostaje do proby T14, przygotowanie z paczki wydania, czas (ok. 1 h) |
| `narzedzia/t13_higiena.py`, `narzedzia/t13_dozwolone.txt` | T13: pliki zmienione od poczatku etapu z kontrola sciezek, ASCII, koncow linii, STL / danych / duzych plikow |
| `narzedzia/t9_dane_osobowe.py` | T9: liczba trafien nazw folderow zlecen i plikow projektow; wypisuje tylko liczby i `sha16` |
| `narzedzia/posrednik_ruchu.py` | T5 / T9: posrednik TCP zapisujacy surowy ruch program <-> ramka do pliku |
| `narzedzia/sql_odczyt.py` | T2 / T8 / T11: SELECT do bazy programu tylko do odczytu, bez tabel z nazwami zlecen |
| `T13/proba_main_9ba9e91.txt` | wynik proby T13 na obecnym `main` (to nie jest odbior) |
| `E3-ODB_raport_2026-11-20.md` | ten raport |

## 2. Kryteria zlecenia

| Nr | Kryterium | Stan | Dowod |
|---|---|---|---|
| 1 | Kazdy T0-T13 ma polecenia sprawdzone co do istnienia plikow i opcji | **spelnione z zastrzezeniem** - 14 z 14 testow ma polecenia; opcje i pliki sprawdzone wg tabeli na koncu `PLAN_TESTOW.md` (`--help` albo kod); zostaly 3 miejsca "[DO POTWIERDZENIA]" (p. 5); zadne polecenie nie bylo uruchomione na instalacji z paczki | `PLAN_TESTOW.md`, sekcja "Lista sprawdzone..."; kontrola automatyczna wszystkich nazw testow z planu: 19 plikow i 64 nazwy funkcji (przedrostki), 0 brakow |
| 2 | Dla kazdego kryterium liczbowego wskazane zrodlo liczby | **spelnione z zastrzezeniem** - tabela "Zrodla liczb kryteriow - skrot"; 2 liczby NIE maja dzis zrodla w programie z paczki: T2 "lista do dofrezowania" i "okno bez przerw" (brak B1), T3 "przez ekran" (brak B2) | `PLAN_TESTOW.md`, T2, T3 |
| 3 | Brak nazw folderow i plikow zlecen w plikach paczki; ASCII + LF | **spelnione** - 0 trafien calych nazw (435 nazw z 2 katalogow danych, 11 plikow); 11 z 11 plikow ASCII i LF | p. 4 |
| 4 | Pelnego pytest nie uruchamiano; krotka proba kazdego skryptu | **spelnione** - 4 z 4 skryptow z proba | p. 3 |

## 3. Proby skryptow pomocniczych (dane sztuczne; logi w `<PC-katalog>\koordynator\robocze\odb\`)

| Skrypt | Proba | Wynik |
|---|---|---|
| `t13_higiena.py` | `--repo <worktree odb> --od 2537f6f --do main` (obecny `main` 9ba9e91) | kod 1; 579 plikow zmienionych, 503 nowe; grupy: E3 164 nowe / 22 zmienione, R58 242 / 4, R59 97 / 34 / 16 usunietych; sciezek poza listami 0; **naruszen 7** (nowe pliki nie ASCII: `dzien_skanera.py`, `dzien_skanera_kroki.toml`, `dzien_skanera_rdzen.py`, `statusy.py`, `ui/napisy.py`, `ui/napisy_rano.py`, `testy/test_dzien_skanera.py`); uwag w grupach spoza etapu 128 (R58 / R59: CRLF, nie ASCII, STL do zamowienia, duze pliki). Plik `T13/proba_main_9ba9e91.txt` |
| `t9_dane_osobowe.py` | katalog sztuczny: 2 foldery o fikcyjnych nazwach + 1 plik STL; cele: log czysty, log z cala nazwa (inna wielkosc liter), log z jednym czlonem, plik UTF-16, `log_excel.csv` jako miejsce dozwolone, zapis posrednika | kod 1 (oczekiwany); 3 nazwy, 6 czlonow; cale nazwy poza dozwolonymi: 2 w 2 plikach (log + zapis ruchu); dozwolone: 1; czlony do wyjasnienia: 3 w 2 plikach; w wyjsciu i w JSON 0 wystapien nazw (sprawdzone `grep`) |
| `t9_dane_osobowe.py` | te same nazwy sztuczne, `--repo <worktree odb>` | kod 0; 1196 plikow przeszukanych, 794 nieprzeszukane (png, pdf, zip, xlsx); 0 trafien calych nazw; czlony: 8497 w 492 plikach - slowa pospolite z nazw sztucznych (pokazuje, ze czlony wymagaja oceny, nie sa kryterium) |
| `posrednik_ruchu.py` | serwer echo + 2 polaczenia przez posrednik w jednym procesie | 2 polaczenia, 108 B do celu, 146 B z celu, plik zapisu 310 B; odpowiedzi doszly bez zmian; nazwa wyslana w 2. polaczeniu znaleziona potem w zapisie przez `t9_dane_osobowe.py` (1 trafienie); `--help` dziala |
| `sql_odczyt.py` | baza sztuczna (3 skany, 1 zlecenie) | `GROUP BY status` na `skany`: kod 0, 2 wiersze; `SELECT count(*) FROM zlecenia`: kod 0; `SELECT folder FROM zlecenia`: kod 2 (odmowa); `DELETE`: kod 2 (odmowa) |

Nie sprawdzono: `posrednik_ruchu.py` z prawdziwa atrapa ramki i programem (to czesc T5); `t9_dane_osobowe.py` na bazie
programu (`--baza` - sprawdzona tylko sciezka kodu przez przeglad, bez proby) - **do sprawdzenia w T9 krok 5 (proba dodatnia)**.

## 4. Kontrola tresci paczki

- ASCII i LF: 11 z 11 plikow paczki - 0 bajtow spoza ASCII, 0 znakow CR (skrypt jednorazowy; `T13/proba_main_9ba9e91.txt`
  mial 24 x CRLF z przekierowania na Windows - zamienione na LF przed commitem).
- Nazwy zlecen: `t9_dane_osobowe.py --nazwy-z <PC-katalog>\app\Prace_test --nazwy-z <PC-katalog>\e3\a5i\t4\drzewo\Cyrkon
  --cel <odbior_koncowy>`: 435 nazw (foldery i pliki STL), 48 czlonow, 11 plikow; **cale nazwy: 0 trafien**; czlony: 21
  trafien 4 czlonow w 4 plikach (razem z tym raportem) - sprawdzone wiersz po wierszu: 4 slowa pospolite (5, 6, 7 i 8
  liter), zadne nie jest nazwiskiem ani numerem zlecenia.
- Pierwsze uruchomienie tej kontroli podalem blednie z katalogiem zestawu pomiarowego jako zrodlem nazw - jego
  podkatalogi (`plytki`, `wyniki`) zostaly potraktowane jak nazwy zlecen (38 falszywych trafien). Wniosek wpisany do planu
  T9: `--nazwy-z` wskazuje katalog NADRZEDNY folderow zlecen.

## 5. Miejsca "[DO POTWIERDZENIA]" i rzeczy sprawdzone tylko w kodzie

W pierwszej wersji planu bylo 10 takich miejsc; 8 sprawdzilem jeszcze w tej sesji (opcje `metryki_pula czas` i `jakosc`
przez `--help`; `Samokontrola.cmd` przekazuje `--json`; `<DANE>` = `<K>/dane`; skrypty `proby2_*.sh` istnieja; pola
wyniku `metryki_P3a`; jeden `[ramki] port`; klawisze ramki; baza SE10 w pliku). Zostaly 3:

| Gdzie | Co potwierdzic po scaleniu |
|---|---|
| `PLAN_TESTOW.md`, T7 | plik `testy/test_p14_baza_zajeta.py` i nazwy komunikatow po scaleniu P14 |
| `T14/README.md` | czy zestaw `Ramki/etap3/t14` trafia do paczki wydania |
| `T14/README.md` | postac polecenia na instalacji z paczki (`Polecenie.cmd ... symulator_t14.py --program .`) - nie uruchamiane |

Sprawdzone tylko w kodzie albo przez `--help`, NIE uruchomieniem (pierwszy wykonawca testu potwierdza praktycznie):
wszystkie polecenia przez `<K>/Polecenie.cmd` (nie bylo instalowalnej paczki), nazwa sekcji zbiorczej w pliku wyniku
`metryki_P3a` (proba `--limit 2`), pola dziennika symulatora, zachowanie `--basetemp` (czy pytest zostawia baze SE10),
zapora Windows przy nasluchu atrapy ramki pod adresem karty sieciowej.

## 6. Odstepstwa i przyjete interpretacje kryteriow

Pelna lista O1-O10 jest w `RAPORT.md`, sekcja 4 (do potwierdzenia przez koordynatora). Najwazniejsze:

- O1 (T0): "czyste konto" = swiezy katalog; "bez internetu" = `/bez-sieci`.
- O2 (T12): migracja bazy tylko na paczce probnej (schemat N = N+1).
- O3-O5 (T2, T3): czesc liczb mierzona testami i narzedziem bez okna, nie programem z paczki - patrz braki B1, B2.
- O7 (T4): "plytka do 40 s" przy puli cieplej; pierwsza plytka przy puli zimnej to 63-68 s w dotychczasowych pomiarach.
- O8 (T5): "siec lokalna" = adres karty sieciowej PC na jednym komputerze.
- O9 (T6): bez programu Excel.
- Odstepstwo od zlecenia: lista "sprawdzone" opiera sie czesciowo na dwoch pomocniczych sesjach odczytu (uruchomily
  `--help` narzedzi i przejrzaly testy); sam sprawdzilem: `metryki_pula.py czas --help`, argparse `aplikacja.py`,
  `samokontrola.py`, `zbuduj_wydanie.py`, `metryki_P3a.py`, `symulator_skanera.py`, `symulator_t14.py`, pliki `.cmd`
  instalatora, schemat tabel w `baza.py`, 19 plikow i 64 nazwy funkcji testow z planu (`grep`, 0 brakow), liczby plikow w 8 katalogach danych.

## 7. Przyjete domyslnie

1. Poczatek etapu 3 = commit `2537f6f` (pierwszy commit pliku planu, 16.11.2026 00:05); diff T13 liczony od tego commita.
2. T13: grupy `R58` i `R59` (prace wlasciciela spoza etapu 3 scalone w tym samym czasie) liczone osobno, nie jako naruszenia.
3. T9: kryterium = cale nazwy; czlony nazw (slowa od 5 znakow) tylko "do wyjasnienia"; nazwy krotsze niz 4 znaki pomijane i liczone.
4. Kazdy wykonawca testow ma wlasna instalacje robocza z paczki (`<PC-katalog>\t0\w<n>`), zeby bazy i foldery skanera
   sie nie mieszaly; folder projektow = kopia `<PC-katalog>\app\Prace_test` poza repo.
5. T6: programu Excel wlasciciela nie uruchamiamy z konta `<konto-PC>` bez jego decyzji.
6. T11 czesc B na 24 skanach (zestaw `r54_P2`), wariant 40 skanow tylko gdy starczy czasu toru pomiarowego.

## 8. POTRZEBUJE (decyzje i braki przed wykonaniem testow)

| Nr | Czego | Dla testu | Propozycja |
|---|---|---|---|
| 1 | sterownik `t2_wieczor.py` (brak B1): uruchamia `Aplikacja` na ustawieniach instalacji, mierzy przerwy petli Qt zegarem 10 ms, zapisuje chwile zgloszenia skanu i przyjecia wyniku, podaje decyzje "Ukruszona" dla prac z `ubytki` w pliku prawdy, porownuje statusy i liste "do dofrezowania" z prawda; wzor: `test_aplikacja.py::test_skany_odniesienia_przez_cala_aplikacje_w_petli_qt` i `symulator_t14.py --sprawdz` | T2 | mala paczka (1 plik w `odbior_koncowy/narzedzia/` + proba), przed T2; bez niej T2 ma 2 liczby "NIE ZMIERZONO przez program z paczki" |
| 2 | scenariusz SE10 odtworzony przez kontroler / okno (brak B2) | T3 | test w `test_aplikacja_rano.py` albo sterownik; bez niego wpis O5 |
| 3 | decyzja: czy T6 ma wejsc na prawdziwy program Excel na PC (jest zainstalowany) | T6 | zostawic na T17 |
| 4 | decyzja: przypadek odpornosci bez wiersza w PW zal. F (wg recenzji PR #40: 8 z 12 wierszy ma odpowiednik) = odstepstwo czy FAIL | T7 | odstepstwo z opisem + wiersz w `co_robic_gdy_nie_dziala` |
| 5 | decyzja: T11 zaliczany galezia "uklad rozpoznany" (aplikacja nie podaje nazwy wlasciwego ukladu w ostrzezeniu) | T11 | przyjac; ewentualna paczka poprawki komunikatu |
| 6 | decyzja: 7 nowych plikow nie ASCII (napisy ekranu po polsku) - wyjatek od zasady albo poprawka | T13 | wyjatek dla plikow napisow i `dzien_skanera*` zapisany w `RAPORT.md` |
| 7 | decyzja: T4 "plytka do 40 s" przy puli cieplej czy zimnej | T4 | ciepla = kryterium, zimna podana jako liczba |
| 8 | paczki wydania N i N+1 oraz `<REPO>` z commita wydania | T0-T12 | koordynator, po scaleniu 5 paczek |

Zmian w plikach poza zakresem nie potrzebuje.

## 9. Czego nie zrobiono i dlaczego

- Testow koncowych nie wykonano (zgodnie ze zleceniem - paczki wydania jeszcze nie ma).
- Sterownika T2 i scenariusza SE10 przez ekran nie napisalem: to nie jest "maly skrypt pomiaru", wymaga prob z prawdziwa
  analiza (ciezki krok) - opisane jako POTRZEBUJE 1 i 2.
- Dokladnej listy plikow kazdej paczki (plik po pliku) do T13 nie odtworzylem - lista jest na poziomie katalogow (O10).
- Nie sprawdzilem zadnego polecenia na prawdziwej instalacji z paczki (nie bylo paczki instalowalnej; instalacja probna
  to ciezki krok).
- Instrukcji A11d i tresci zestawu T14 nie kopiowalem (zgodnie ze zleceniem) - `T14/README.md` tylko odsyla.

## 10. Etap 2 (20.11.2026, 22:34 - 23:12): sterowniki T2 i T3, decyzje koordynatora w planie testow

Zlecenie: `<PC-katalog>\koordynator\zlecenia\odb-r2.md` + zmiana z promptu koordynatora (kod programu do prob z kopii
integracyjnej `<PC-katalog>\qc-wt\integ`, commit a2236c1 = `main` 9ba9e91 + `e3/a11w` + `e3/a11s` + `e3/a11i` + `e3/p14`,
tylko odczyt; tor blokady 4). Etap przejety po wykonawcy zatrzymanym 20.11 o 21:27: zastalem 2 pliki niezacommitowane
(`t2_wieczor.py`, `t2_scenariusz.json` - szkic po 2 probach poprzednika, druga przerwana) i brak `t3_poranek.py`.
Kodu programu nie zmienialem; do kopii integracyjnej nic nie zapisano (`git status --short` pusty po kazdej probie).

### 10.1 Pliki etapu 2 (wszystkie w `Ramki/etap3/odbior_koncowy/`)

| Plik | Stan | Co |
|---|---|---|
| `narzedzia/t3_poranek.py` | nowy | sterownik T3: SE10 przez okno programu (napisal pomocnik - jedna sesja, model fable; uruchomilem i sprawdzilem sam przed commitem) |
| `narzedzia/t2_wieczor.py` | nowy (szkic poprzednika poprawiony) | sterownik T2: prawdziwy program + symulator skanera + decyzje kliknieciami + pomiar |
| `narzedzia/t2_scenariusz.json` | nowy (szkic poprawiony) | tabela prawdy T2: 10 plikow, `sha16` kazdego skanu, odpowiedzi technika |
| `narzedzia/t13_higiena.py` | zmieniony | decyzja nr 5: pliki napisow ekranu nie-ASCII raportowane osobno (odstepstwo O11) |
| `narzedzia/t13_wyjatki_ascii.txt` | nowy | lista 7 plikow odstepstwa O11 |
| `T13/proba_integ_a2236c1.txt` | nowy | proba T13 po zmianie skryptu (to nie odbior) |
| `PLAN_TESTOW.md` | zmieniony | T2 i T3 napisane od nowa (sterowniki), decyzje nr 3-6 w T7, T11, T13, T4, naglowek, tabele na koncu |
| `RAPORT.md` | zmieniony | liczniki T2, T3, T4, T7, T11, T13; odstepstwa O3-O7 zmienione, O11 i O12 nowe; braki B1, B2, B4-B6; decyzje 12-17; zadania wlasciciela 7-8 |
| `T14/README.md` | zmieniony | nazwa przycisku `przycisk_nowa_plytka` (P14 runda 2); odsylacze A11d nadal do potwierdzenia |

### 10.2 Kryteria etapu 2

| Nr | Kryterium | Stan | Dowod |
|---|---|---|---|
| 1 | Oba sterowniki: proba zakonczona kodem 0 z plikiem wyniku; liczby z proby | **spelnione** | T3: kod 0, 32 z 32 (p. 10.3); T2: 5 prob z kodem 0, w tym 4 z wynikiem "zgodne n z n" (p. 10.4) |
| 2 | Kazdy sterownik ma `--help`, limit czasu calosci i sprzata procesy takze po bledzie | **spelnione z zastrzezeniem** | `--help` obu uruchomione; T3: `--limit-s` (proba pomocnika z limitem 4 s: kod 2, wynik czesciowy 9 z 32, 0 procesow); T2: `--limit 25` (proba 7: przerwanie w trakcie pierwszej analizy - kod 3, "PRZERWANO: limit 25 s", wynik czesciowy zapisany, 0 procesow potomnych, `Get-Process python` 3 s po koncu bez procesow sterownika); po kazdej probie PID-y z `t2_pid.txt` wobec listy procesow: 0 zywych. Zastrzezenie: NIE sprawdzono proba watku-straznika T2 (zawieszona petla okna: limit + 120 s) ani zabicia sterownika z zewnatrz (wtedy procesy potomne zostaja - sterownik nie uzywa obiektu zadania Windows) |
| 3 | Pliki ASCII + LF, bez nazw zlecen; commit + push po kazdym zamknietym kroku | **spelnione** | 0 bajtow nie-ASCII i 0 CR w 9 plikach etapu; `t9_dane_osobowe.py` na calym katalogu paczki: 435 nazw, 16 plikow, 0 trafien calych nazw (czlony: 28 trafien slow pospolitych w 5 plikach, jak w etapie 1) |

### 10.3 Sterownik T3 `t3_poranek.py` - proba (caly SE10, krok lekki)

Polecenie (z katalogu `<PC-katalog>\qc-wt\integ\Ramki\stanowisko`):
`<PC-katalog>\koordynator\narz\py.cmd <odb>\narzedzia\t3_poranek.py --wyjscie <PC-katalog>\koordynator\robocze\odb\t3_odbior_proba --wymagaj-100`

| Liczba | Wynik proby |
|---|---|
| wiersze tabeli SE10 zgodne | **32 z 32**, kod 0 (z `--wymagaj-100`), czas 10,9 s; 4 starty programu (start + 3 restarty), 28 klikniec |
| listy kompletnych i brakow odczytane z ekranu (10 wierszy) | "tak" 8 (R11, R14, R15, R21, R22, R28, R29, R30), "czesciowo" 1 (R31: po restarcie ekran pokazuje tylko ostatni zamkniety piec), "nie dotyczy" 1 (R17: listy "do dofrezowania" ekran poranny nie pokazuje) |
| pytanie przed "Zamknij piec" (P14) | piec 1: nie / nie; piec 2: oczekiwane wg zlecenia tak, **bylo nie**; piec 3: nie / nie |
| limit czasu | proba pomocnika `--limit-s 4`: kod 2, wynik czesciowy, 0 osieroconych procesow |
| srodowisko jak z `Polecenie.cmd` (python bazowy, `PYTHONPATH` bez katalogu programu, opcje `--testy` i `--ustawienia-wzor` podane) | proba `t3_proba_jak_polecenie`: 32 z 32, kod 0, 12 s |

Co jest prawdziwe: kontroler `Aplikacja` + `start()` (silnik i obserwator dzialaja, nic nie analizuja), sesje, baza, okno,
WSZYSTKIE czynnosci technika kliknieciami / klawiszami po nazwach obiektow, restarty. Co sztuczne: wyniki skanow (SE10
nie ma plikow STL; wchodza funkcja sesji wolana po analizie + `kontroler._po_skanie` / `_odswiez`), zegar staly, indeks
zlecen wpisany funkcja testu, offscreen, ramki i Excel wylaczone. Pelna lista miejsc prywatnych - w naglowku pliku.

**Do oceny koordynatora:** okno NIE pyta przed "Zamknij piec" 2, choc sesja liczy 1 prace nieznana jako nierozstrzygnieta -
okno pyta tylko o prace bez decyzji, a ta ma decyzje "bez projektu". To zachowanie programu po P14, nie blad sterownika;
tabela SE10 tego nie obejmuje (32 z 32).

Polecenie na instalacji z paczki (po `zainstaluj.cmd /testy`; NIE uruchamiane - instalacji z paczki na PC jeszcze nie ma):

```
set QT_QPA_PLATFORM=offscreen
<K>\Polecenie.cmd <ODB>\narzedzia\t3_poranek.py --testy <ST>\testy --wyjscie <ROB>\t3 --ustawienia-wzor <K>\ustawienia.toml
```

### 10.4 Sterownik T2 `t2_wieczor.py` - proby skrocone (prawdziwa analiza, tor 4 przez `ciezki.ps1`)

**Czasy z prob NIE sa wynikiem odbioru:** odstep 5 s zamiast 60 s (pliki z definicji czekaja w kolejce za poprzednia
plytka), a na PC biegly rownolegle pelne pytesty innych paczek (tory 1-3). Werdykty "start" i "mapa" w probach to FAIL z
tego powodu; sterownik wypisuje w wyniku wiersz "UWAGA: PROBA SKROCONA".

| Proba | Pozycje scenariusza | Zgodne z prawda | Start analizy [s] | Mapa od zapisu [s] (mediana / maks. / pierwsza) | Przerwa petli maks. (tykniec; > 200 ms) | Lista "do dofrezowania" | Kod; czas calosci |
|---|---|---|---|---|---|---|---|
| 3 (22:53) | 2, 4, 5, 7: R59 okragla, R54 okragla, uciety, niezgodny uklad | **4 z 4** | 0,354; 41,2; 66,6 (2 czekaly w kolejce) | 70,1 / 72,7 / 51,5 | 35,6 ms (4670; 0) | rowna, 7 z 7 decyzji | 0; 97 s |
| 4 (22:57) | 6, 8, 9: drgniecie, R59 kwadratowa, poranna | 0 z 3 - **blad sterownika** (nie odpowiadal na pytanie "Podaj numer plytki"; statusy i uklady 3 z 3 zgodne) | 0,376; 33,3; 51,1 | 57,1 / 81,1 / 38,6 | 42,7 ms (4950; 0) | rowna, 4 z 4 | 0; 103 s |
| 5 (23:01) | 6, 8, 9 po poprawce (numer z prawdy kliknieciem; "to nowy wsad") | **3 z 3** | 0,422; 31,5; 49,4 | 55,5 / 78,4 / 36,7 | 47,4 ms (4808; 0) | rowna, 4 z 4 | 0; 99 s |
| 6 (23:03) | 1, 2, 3 (`--plytki 3`): R59 kwadratowa, R59 okragla, R54 kwadratowa - wersja zacommitowana (eb824ca) | **3 z 3** | 0,377; 34,9; 48,2 | 54,2 / 63,4 / 40,2 | 34,3 ms (4143; 0) | rowna, 12 z 12 | 0; 86 s |
| 7 (23:06) | 2, 5, 7 z `--limit 25` (proba limitu czasu) | przerwane: 1 z 3 (plik uciety odrzucony; 2 plytki "BRAK PLYTKI") | 0,372; reszta NIE ZMIERZONO | - | 0 przekroczen | NIE ZMIERZONO | **3** (limit); 27 s |
| 8 (23:07) | 10: druga okragla R54 | **1 z 1** | 0,377 | 46,0 (jedna plytka, pula zimna) | 28,7 ms (2662; 0) | rowna, 6 z 6 | 0; 58 s |

Proby 4 i 5 szly w srodowisku jak z `Polecenie.cmd` (python bazowy, `PYTHONPATH` BEZ katalogu programu, katalog biezacy =
katalog programu): sterownik, proces silnika i symulator znalazly moduly programu. Proby 3, 6, 7, 8 przez `narz\py.cmd`.
Lacznie przez program przeszlo 10 z 10 pozycji scenariusza (kazda co najmniej raz, zgodnie z prawda - po poprawce z proby 4).
Start analizy pliku zapisanego przy pustej kolejce: 0,354 / 0,376 / 0,422 / 0,377 / 0,372 / 0,377 s (6 prob).
Po kazdej probie: 0 procesow sterownika (`procesy potomne po sprzataniu: []`, kontrola `Get-Process python`).
Katalogi: `<PC-katalog>\koordynator\robocze\odb\t2_proba3` .. `t2_proba6`, `t2_proba7_limit`, `t2_proba8` (`t2_wynik.txt`,
`t2_wynik.json`).

Co sterownik mierzy:

| Liczba kryterium | Jak | Rodzaj pomiaru |
|---|---|---|
| 10 z 10 zgodnie z prawda | status, uklad, numer plytki ze stanu programu wobec pliku prawdy; nieprzyjete: 0 zielonych; uciety: brak plytki + 1 zdarzenie `plik_odrzucony` w bazie | doslownie |
| start analizy < 1 s | `analiza.od` stanu programu (czas zdarzenia "start" procesu silnika) minus koniec zapisu pliku z dziennika symulatora; dla wszystkich plikow dobrych, pliki czekajace w kolejce wskazane osobno | **doslownie** (0,35-0,42 s dla pliku przy pustej kolejce w 3 probach) |
| mapa do 40 s (mediana) | pierwszy odczyt plytki w `stan().plytki` (zegar 20 ms w watku okna) minus koniec zapisu; obok chwila, w ktorej okno samo pokazalo mape (`w_oknie`) i `czas_s` programu | **gorne ograniczenie** (dokladnosc: okres zegara + przerwa petli) |
| okno bez przerw > 200 ms | zegar Qt 20 ms w watku okna, odstep kolejnych tykniec, od pierwszego tykniecia w petli okna do tykniecia zamykajacego | doslownie w tym zakresie; **NIE ZMIERZONO**: start programu przed pokazaniem okna i zamykanie programu (ostatnie tykniecie trwa ok. 1,3 s - podane osobno) |
| lista "do dofrezowania" = prawda | lista biezaca programu po kliknieciach "Ukruszona" wg prawdy wobec prac z `ubytki` w prawdzie plytek przyjetych | doslownie |

Poprawki wobec szkicu poprzednika (kazda sprawdzona proba): (1) kryterium startu liczone dla WSZYSTKICH plikow - szkic
wylaczal z kryterium pliki czekajace w kolejce (oslabienie); (2) sterownik odpowiada na pytanie "Podaj numer plytki"
kliknieciem numeru z prawdy - na plytkach kwadratowych program numeru nie odczytuje (raport R59: dolki poza polem skanu),
bez tego 3 z 3 plytek kwadratowych bylo "niezgodnych" (proba 4); (3) `sha16` kazdego skanu w scenariuszu, sprawdzane
przed startem; (4) plytka poranna w scenariuszu zamieniona na skan bez drgniec (poprzedni mial 2 drgniecia - dwie
przyczyny odmowy naraz); (5) sledzenie i konczenie procesow bez `psutil` (w srodowisku programu go nie ma); (6) tykniecie
zamykajace program liczone osobno (w szkicu wygladalo jak 1,3 s "tykniecia w trakcie pomiaru"); (7) osobne liczniki
"do 40 s" dla pierwszej plytki (pula zimna) i kolejnych - zgodnie z decyzja nr 6; (8) zrodlo numeru plytki w wyniku.

Obserwacje z prob do oceny koordynatora (to nie sa werdykty odbioru):
- decyzje "Ukruszona" na pracach, ktorych program sam nie oznaczyl (`ukruszona_niewykryta`): proba 3: 5 z 7, proby 4 i 5:
  3 z 4, proba 6: 7 z 12, proba 8: 3 z 6 - czyli wiekszosc prac z `ubytki` w pliku prawdy zestawu P2 nie byla czerwona w programie. Kryterium T2 tego nie
  obejmuje (lista powstaje z decyzji technika), ale liczba jest w wyniku sterownika (`decyzje[]`) - warto ja zestawic z
  T10 / metryka wykrywalnosci, zanim ktos uzna "lista = prawda" za dowod wykrywania.
- pierwsza plytka (pula zimna) pod obciazeniem: 36,7-51,5 s do pojawienia sie w stanie programu; kolejne w probach
  czekaly w kolejce (odstep 5 s) - ich czasy nic nie mowia o kryterium 40 s.
- pytanie "to ponowny skan?" pojawilo sie dopiero po podaniu numeru (proba 5: plytki nr 6 i 8 maja ten sam uklad i
  numer 2); plytki okragle R59 i R54 o tym samym numerze 8 (proba 3) pytania nie wywolaly.

Polecenie pelnego testu na instalacji z paczki (NIE uruchamiane - instalacji z paczki na PC jeszcze nie ma; pierwsze
uruchomienie zacznij od proby skroconej `--wybierz 2,4,5,7 --odstep 5`, ok. 2 min):

```
set QT_QPA_PLATFORM=offscreen
<K>\Polecenie.cmd <ODB>\narzedzia\t2_wieczor.py --ustawienia-wzor <K>\ustawienia.toml --roboczy <ROB>\t2 --projekty <folder_cyrkon> > <ROB>\t2_sterownik.log 2>&1
```

Czas trwania pelnego testu: ok. 11-13 min (9 x 60 s miedzy startami plikow + start programu + ostatnia analiza);
limit calosci domyslnie 30 min (`--limit`, potem kod 3 i wynik czesciowy). `<folder_cyrkon>` = kopia
`<PC-katalog>\app\Prace_test`; katalog `<ROB>\t2` nowy / pusty; przez `ciezki.ps1` w torze pomiarowym, bez innych
ciezkich krokow na PC.

### 10.5 Decyzje koordynatora 1-6: gdzie wpisane

| Nr | Decyzja | `PLAN_TESTOW.md` | `RAPORT.md` |
|---|---|---|---|
| 1 | T2 sterownik | sekcja T2 (cala od nowa), tabele na koncu | wiersz T2, O3, O4, B1, decyzja 12 |
| 2 | T3 SE10 przez ekran | sekcja T3 (cala od nowa), tabele na koncu | wiersz T3, O5, B2, decyzja 13 |
| 3 | T7 komunikat spoza zal. F | T7: akapit "Decyzja koordynatora 20.11 nr 3", liczby kryterium | wiersz T7, O12, B4, decyzja 14, zadanie wlasciciela 7 |
| 4 | T11 "albo" | T11: akapit "Decyzja ... nr 4", liczby kryterium | wiersz T11, O6, B5, decyzja 15 |
| 5 | T13 napisy ekranu nie-ASCII | T13: akapit "Decyzja ... nr 5 = O11", proba po zmianie skryptu | wiersz T13, O11, B6, decyzja 16 |
| 6 | T4 pula zimna i ciepla | T4: akapit "Decyzja ... nr 6 (O7)", tabela liczb | wiersz T4, O7, decyzja 17, zadanie wlasciciela 8 |

Skrypt `t13_higiena.py` po zmianie - proba na kopii integracyjnej a2236c1 (`T13/proba_integ_a2236c1.txt`): odstepstwo
O11: 7 plikow z 7 na liscie (109 / 134 / 102 / 240 / 66 / 111 / 45 wierszy nie-ASCII); **naruszen 1**: nowy plik
`stanowisko/ui/kandydaci.py` z 2 bajtami nie-ASCII (spoza listy siedmiu - zgloszony zgodnie z decyzja nr 5). Proba z pusta
lista wyjatkow na `main` 9ba9e91: 7 naruszen jak w etapie 1 (skrypt bez listy zachowuje sie jak przedtem).

### 10.6 Miejsca "[DO POTWIERDZENIA]" po etapie 2

| Gdzie (stan z etapu 1) | Stan po etapie 2 |
|---|---|
| `PLAN_TESTOW.md`, T7: plik `testy/test_p14_baza_zajeta.py` i nazwy komunikatow po P14 | **potwierdzone** na kopii integracyjnej a2236c1: plik jest; `decyzja_niezapisana` i `polecenie_niezapisane` sa w `statusy.py` (3 wystapienia) - znacznik usuniety |
| `T14/README.md`: czy zestaw `Ramki/etap3/t14` trafia do paczki wydania | **zostaje** - runda 2 paczki A11d w toku, galezi `e3/a11d` nie ma w kopii integracyjnej |
| `T14/README.md`: postac polecenia na instalacji z paczki | **zostaje** (jak wyzej); dopisano nazwe przycisku `przycisk_nowa_plytka` (potwierdzona w `stanowisko/ui/czesci.py` kopii integracyjnej) |

W `PLAN_TESTOW.md` nie ma juz zadnego znacznika; w `T14/README.md` zostaly 2. Potwierdzone dodatkowo na kopii
integracyjnej: opcje `stanowisko.aplikacja` (`--ustawienia --atrapa --rano --zamknij-po`), tresc wzorow `Polecenie.cmd` i
`Stanowisko.cmd`, nazwy 3 testow petli okna z sekcji T2, nazwy obiektow okna uzywanych przez sterowniki (uzyte w probach).
NIE potwierdzalem ponownie pozostalych pozycji listy "sprawdzone" z etapu 1 (opcje `zainstaluj.cmd`, `samokontrola`,
`zbuduj_wydanie.py` na galeziach po rundach poprawek) - brak czasu; pierwszy wykonawca T0 potwierdza je praktycznie.

### 10.7 Odstepstwa etapu 2

1. Sterownik T2 prowadzi program w procesie sterownika (`aplikacja.main`), nie przez plik `Stanowisko.cmd` - inaczej nie
   da sie mierzyc petli okna ani klikac po nazwach obiektow (O3); okno offscreen (O4).
2. T3: wyniki skanow, zegar i indeks zlecen sztuczne; 2 skladniki prywatne kontrolera (`_po_skanie`, `_odswiez`) (O5).
3. Proba T2 miala 1-4 pliki co 5 s (zlecenie: "3 plytki co 5 s") - szesc prob zamiast jednej, bo kazda sprawdzala inna
   czesc scenariusza albo limit czasu (lacznie 10 z 10 pozycji scenariusza przeszlo przez program); razem ok. 9 min w torze 4.
4. Sterowniki NIE byly uruchomione na instalacji z paczki (nie istnieje na PC); srodowisko `Polecenie.cmd` bylo tylko
   nasladowane zmiennymi (proby 4 i 5).
5. Pomocnik: 1 sesja (model fable) napisala `t3_poranek.py` wg mojego opisu; plik uruchomilem i sprawdzilem sam (proba
   `t3_odbior_proba`, przeglad naglowka i miejsc prywatnych).

### 10.8 Przyjete domyslnie (etap 2)

1. "Zgodnie z prawda" dla numeru plytki: numer odczytany przez program ALBO podany przez technika (sterownik) na pytanie
   programu; zrodlo numeru jest w wyniku przy kazdej plytce. Plytka poranna wieczorem: program o numer nie pyta - numeru
   nie porownuje sie, gdy program go nie odczytal.
2. Na pytanie "to ponowny skan?" sterownik odpowiada "to nowy wsad" (kazdy plik zestawu to inna plytka); pytanie
   `plytka_nie_z_trybu` zostaje bez odpowiedzi.
3. Plik uciety = "obsluzony zgodnie z prawda", gdy nie powstala plytka i w bazie jest dokladnie 1 zdarzenie
   `plik_odrzucony`.
4. Kod wyjscia 0 obu sterownikow = "pomiar wykonany"; ZAL / FAIL czyta sie z pliku wyniku (T3: opcja `--wymagaj-100`).
5. Odstepstwa nowe: O11 (T13, napisy ekranu) i O12 (T7, komunikat spoza zal. F) - numery nadane przeze mnie.

### 10.9 POTRZEBUJE (etap 2)

Zmian w plikach poza zakresem nie potrzebuje. Do decyzji / zrobienia przez koordynatora:

| Nr | Co | Dla |
|---|---|---|
| 1 | `Ramki/stanowisko/stanowisko/ui/kandydaci.py`: 2 bajty nie-ASCII w nowym pliku (spoza listy O11) - poprawka przez paczke, ktora go dodala, albo dopisanie do `t13_wyjatki_ascii.txt` decyzja | T13 (inaczej FAIL: 1 naruszenie) |
| 2 | okno nie pyta przed "Zamknij piec", gdy jedyna praca nierozstrzygnieta ma decyzje "bez projektu" - czy to zamierzone (P14) | T3 (informacja; nie zmienia 32 z 32) |
| 3 | pierwsze uruchomienie obu sterownikow na instalacji z paczki (proba skrocona T2, caly T3) przed wlasciwym testem | T2, T3 |
| 4 | prace z `ubytki` w prawdzie zestawu P2 w wiekszosci nieoznaczone przez program (18 z 29 decyzji `ukruszona_niewykryta` w probach 3, 5, 6 i 8) - do zestawienia z T10 | T2 (interpretacja "lista = prawda") |

### 10.10 Czego nie zrobiono (etap 2)

- Pelnego T2 (10 plikow co 60 s) nie wykonano - to odbior (zgodnie ze zleceniem).
- Watek-straznik sterownika T2 (zawieszona petla okna, limit + 120 s) nie byl sprawdzony proba - sprawdzony jest limit
  w petli okna (proba 7). Zadna proba nie miala 10 plikow naraz ani odstepu 60 s.
- Sterowniki nie byly uruchomione przez prawdziwe `Polecenie.cmd` (brak instalacji z paczki).
- `t3_poranek.py`: nie sprawdzono, czy proces roboczy silnika faktycznie wystartowal (silnik nic nie analizuje w T3;
  zamkniecie czyste, 0 procesow potomnych do zabicia).
- Sekcji 1-9 tego raportu (etap 1) nie przepisywalem: tam, gdzie mowia "brak B1 / B2", "POTRZEBUJE 1-7", "zostaly 3
  miejsca do potwierdzenia", obowiazuje stan z sekcji 10.
