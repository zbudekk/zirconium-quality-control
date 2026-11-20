# Raport koncowy etapu 3 - SZKIELET (wypelnia koordynator po testach)

Stan: **SZKIELET z 20.11.2026 (paczka E3-ODB) - zaden test nie zostal jeszcze wykonany.** Puste pola = "nie wykonano".
Przepis testow: `PLAN_TESTOW.md`; odlozone: `ODLOZONE.md`; proba z czlowiekiem: `T14/README.md`.

Zasady wypelniania: wynik tylko `ZAL` / `FAIL` / `ODLOZONE` / `NIE ZMIERZONO` (czesc kryterium); liczniki, nie procenty;
kazdy FAIL zostaje w tabeli "FAIL i poprawki" takze po poprawce; dowody = sciezki wzgledem `Ramki/etap3/odbior_koncowy/`.

## 1. Wydanie

| Pole | Wartosc |
|---|---|
| Numer wersji (N) | |
| Plik paczki | `Stanowisko_<N>.zip` |
| SHA-256 paczki | |
| Rozmiar, liczba plikow programu, liczba kol | |
| Commit `main`, z ktorego zbudowano paczke | |
| Data budowy | |
| Paczka N+1 do T12 (numer, SHA-256) | |
| Wiersz w `Ramki/etap3/wydania/SHA256SUMS_wydania.txt` dopisany | tak / nie |
| Pelny pytest na commicie wydania (interpreter bazowy) | passed / skipped / failed |
| Scalone paczki (PR, commit scalenia) | A11s: ; A11i: ; A11w: ; P14: ; A11d: ; ODB: |

## 2. Tabela testow T0-T17

| Nr | Test | Wynik | Liczniki (kryterium -> zmierzone) | Wykonawca, data | Dowody |
|---|---|---|---|---|---|
| T0 | Czysta instalacja | | start programu _ z 2; samokontrola: ok _ / ostrzezenia _ / bledy _; SHA-256 zgodne _ z _ | | `T0/` |
| T1 | Testy programu | | passed _ / skipped _ / failed _ / errors _; pominiete spoza punktu odniesienia: _ | | `T1/` |
| T2 | Wieczor od poczatku do konca | | obsluzone _ z 10; start analizy maks. _ s; mapa mediana _ s (maks. _ s, plytka 1: _ s); przerwa okna maks. _ ms; lista "do dofrezowania": _ | | `T2/` |
| T3 | Poranek od poczatku do konca | | wiersze tabeli SE10: _ z 32; listy kompletnych i brakow: _ z 10 wierszy; przez ekran: _ | | `T3/` |
| T4 | Pula | | top-1 "dobrze" _ z _; plytka maks. _ s (ciepla) / _ s (zimna); pamiec szczyt _ GB | | `T4/` |
| T5 | Ramka na atrapie w sieci lokalnej | | potwierdzenia _ z 5 (seria _ z _), powtorek _; plan po restarcie _ s; Spacja maks. _ ms; siec lokalna: _ | | `T5/` |
| T6 | Excel na sztucznym arkuszu | | zapytania _ z 200; zle wiersze _; log regula 6: _; tryb "pytaj": _; tryb "cien": _ | | `T6/` |
| T7 | Odpornosc | | przypadki _ z 6 (silnik _, zamkniecie _, brak "Cyrkon" _, brak sieci _, brak ramki _, baza zajeta _); komunikaty zgodne z zal. F: _ z _ | | `T7/` |
| T8 | Metryki | | metryki zgodne z liczeniem recznym: _ z _ (wieczor _ z _, rano _ z _) | | `T8/` |
| T9 | Dane osobowe | | trafienia calych nazw: repo _, logi _, wyniki _, ruch do ramki _; czlony wyjasnione _ z _; nazwy w `dane/`: _ | | `T9/` |
| T10 | Regresja silnika | | wyrownanie _ z 40; top-1 "dobrze" _ z _; falszywe czerwone na pracach calych _ z _ | | `T10/` |
| T11 | Stare plytki | | uklad rozpoznany _ z _; zielone przy zlym ukladzie _; uklad zapisany w `skany` _ z _ | | `T11/` |
| T12 | Aktualizacja | | N -> N+1: polecen _, kod _; powrot: polecen _, kod _; ustawienia: sumy rowne _ z 3; baza: kopia _, migracja probna _ | | `T12/` |
| T13 | Higiena repo | | naruszen _ (poza listami _, nie ASCII _, konce linii _, STL / dane _); wyjatki przyjete decyzja: _ | | `T13/` |
| T14 | Proba "technik obsluguje bez instrukcji" (czlowiek) | | zadania _ z 11; interwencje _; zawahania ponad 10 s: _ (poprawione _, zostawione _) | wlasciciel, | `T14/` |
| T15 | Ramki na sprzecie | ODLOZONE (do potwierdzenia) | - | - | `ODLOZONE.md` |
| T16 | Prawdziwy skaner | ODLOZONE (do potwierdzenia) | - | - | `ODLOZONE.md` |
| T17 | Excel i MillBox na prawdziwych danych | ODLOZONE (do potwierdzenia) | - | - | `ODLOZONE.md` |

Podsumowanie: T0-T13 zaliczone _ z 14; T14: _; T15-T17: odlozone _ z 3 (powod i warunek wznowienia w `ODLOZONE.md`).

## 3. Definicja "koniec etapu 3 = gotowe do trybu cienia" (plan, sekcja 7)

| Warunek | Stan | Dowod |
|---|---|---|
| T0-T14 zaliczone | | tabela 2 |
| T15-T17 zaliczone albo jawnie odlozone z powodem i warunkiem wznowienia | | `ODLOZONE.md` |
| Instrukcje jednostronicowe gotowe (wieczor, poranek) | | `Ramki/stanowisko/instrukcje/wieczor.html`, `poranek.html` (A11d) |
| Tabela "co robic, gdy nie dziala" gotowa | | `Ramki/stanowisko/instrukcje/co_robic_gdy_nie_dziala.html` (A11d) |
| Kroki 1-5 z PW "Uruchomienie" da sie wykonac bez programisty przy klawiaturze | | `instrukcje/instalacja_i_aktualizacja.md`, T0, T12 |

## 4. Odstepstwa (przyjete interpretacje kryteriow)

Lista wyjsciowa z `PLAN_TESTOW.md` - koordynator potwierdza albo zmienia kazda pozycje i dopisuje te, ktore wyjda w testach.

| Nr | Test | Odstepstwo | Potwierdzone (tak / nie / zmienione) |
|---|---|---|---|
| O1 | T0 | "czyste konto" = swiezy katalog na koncie `<konto-PC>`; "bez internetu" = `/bez-sieci` (pip `--no-index`), sieci fizycznie nie odcinano | |
| O2 | T12 | "baza zmigrowana z kopia" sprawdzona na paczce probnej z `MIGRACJE[2]` (schemat wydan N i N+1 jest ten sam) | |
| O3 | T2 | start analizy < 1 s mierzony symulatorem z `--analiza` (obserwator + silnik, bez okna) | |
| O4 | T2 | przerwy petli okna: prawdziwa analiza na 3 plytkach, 10 plytek na analizie sztucznej (testy), nie w programie z paczki | |
| O5 | T3 | SE10 na poziomie sesji (32 wiersze) + ekran na innym scenariuszu; SE10 przez ekran nie istnieje | |
| O6 | T11 | zaliczenie galezia "uklad rozpoznany"; ostrzezenie nie podaje nazwy wlasciwego ukladu | |
| O7 | T4 | "plytka do 40 s" liczona przy puli cieplej; pierwsza plytka przy puli zimnej podana osobno; pamiec = proces roboczy + okno | |
| O8 | T5 | "siec lokalna" = adres karty sieciowej PC, ramka i program na jednym komputerze; ramka poranna tylko w testach | |
| O9 | T6 | arkusz w pamieci (atrapa), bez programu Excel | |
| O10 | T13 | "listy paczek" na poziomie katalogow; prace R58 / R59 liczone osobno | |

## 5. FAIL i poprawki

| Nr | Test | Co nie przeszlo (liczba, log) | Paczka poprawki (galaz, PR) | Powtorka: wynik, data, dowod |
|---|---|---|---|---|
| | | | | |

## 6. Braki narzedzi stwierdzone przy planowaniu (stan na 20.11 - uzupelnic, co z nimi zrobiono)

| Nr | Brak | Skutek dla testu | Decyzja / paczka |
|---|---|---|---|
| B1 | sterownik T2 (program z paczki + pomiar petli okna + decyzje wg prawdy + zapis startu analizy) | T2: lista "do dofrezowania" i przerwy okna nie sa mierzone w jednym przebiegu przez program z paczki | |
| B2 | scenariusz SE10 przez ekran / kontroler aplikacji | T3: "przez ekran" niezmierzone | |
| B3 | 200 zapytan przez prawdziwy Excel (COM) | T6 tylko na atrapie arkusza (dalej: T17) | |
| B4 | porownanie tekstow komunikatow z PW zal. F | T7: tabela sporzadzana recznie | |
| B5 | ostrzezenie z nazwa wlasciwego ukladu w aplikacji | T11: druga galaz kryterium niespelnialna | |
| B6 | pliki napisow ekranu ze znakami spoza ASCII (7 nowych plikow) | T13: 7 naruszen na `main` 9ba9e91 | |

## 7. Zadania wlasciciela

| Nr | Zadanie | Co dostaje | Ile trwa | Stan |
|---|---|---|---|---|
| 1 | Proba T14 z osoba, ktora nie widziala programu | `T14/README.md`, zestaw `Ramki/etap3/t14/` | ok. 1 h | |
| 2 | Wizyta przy laptopie stanowiska (T0, T2, T3 na laptopie; otwarte 4-6) | `ODLOZONE.md`, paczka wydania | 1-2 h | |
| 3 | Skaner: "Dzien skanera" i pierwsze skany (T16) | `ODLOZONE.md` | | |
| 4 | Ramki: zlozenie i siec (T15) | `ODLOZONE.md` | | |
| 5 | Raporty MillBox i kopia pliku Excela (T17) | `ODLOZONE.md` | | |
| 6 | Decyzje otwarte: tabela `testy_wykrywalnosci` (M2), waxup w folderze zlecenia, wygasanie listy brakow, kolory pola B, uwagi do pokazu G2 | `Ramki/00_NADZOR_STAN.md` | | |

## 8. Decyzje koordynatora przyjete domyslnie (do odwolania przez wlasciciela)

Z `Ramki/00_NADZOR_STAN.md` (19.11 i 20.11) - przepisac stan koncowy i dopisac decyzje z testow koncowych.

| Nr | Decyzja | Skad | Nadal obowiazuje |
|---|---|---|---|
| 1 | Pierwsza instalacja: wersja nie jest przelaczana przy czerwonej samokontroli ("wstrzymana - uzupelnij ustawienia", kod 10) | 20.11 nr 1 | |
| 2 | Folder danych w OneDrive / SharePoint: zmienne srodowiska i rejestr = BLAD, sama nazwa katalogu = OSTRZEZENIE | 20.11 nr 2 | |
| 3 | Brak folderu MillBox = OSTRZEZENIE | 20.11 nr 3 | |
| 4 | `Wroc_do_poprzedniej.cmd` bez argumentow pyta T / N | 20.11 nr 4 | |
| 5 | Python 3.12.10 wskazany; inne 3.12.x z ostrzezeniem | 20.11 nr 5 | |
| 6 | Numeracja wydan `0.3.<n>`; katalog domyslny `C:\Stanowisko`; skrot tylko na zadanie | 20.11 nr 6 | |
| 7 | Paczka nie jest odchudzana z zaleznosci nieuzywanych | 20.11 nr 7 | |
| 8 | Stare wersje i kopie bazy nie sa kasowane automatycznie | 20.11 nr 8 | |
| 9 | Obrazki instrukcji wpisane w strony `.html`; instrukcje dla `pula_wpisow = false` | 20.11 nr 9 | |
| 10 | Proba T14 w etapie 3 na atrapie kontrolera; powtorka na prawdziwym skanerze przed praca produkcyjna | 20.11 nr 10 | |
| 11 | Regula ponownego skanu (zbiory projektow >= 0,5); ramka W tylko ostatni skan; Enter na ramce = kuweta rozlozona; `maks_wiek_dni` 60; sprzatanie puli 30 dni; pusta pula = skany czekaja; kalibracja ramki obowiazkowa od C2 | 19.11 | |
| | (decyzje z testow koncowych) | | |

## 9. Podpis

Koordynator: ____ ; data: ____ ; `main` po odbiorze: ____ ; koniec etapu 3: TAK / NIE (powod).
