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
