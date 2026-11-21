# Raport koncowy etapu 3 - SZKIELET (wypelnia koordynator po testach)

Stan: **SZKIELET z 20.11.2026 (paczka E3-ODB) - zaden test nie zostal jeszcze wykonany.** Puste pola = "nie wykonano".
Przepis testow: `PLAN_TESTOW.md`; odlozone: `ODLOZONE.md`; proba z czlowiekiem: `T14/README.md`.
Etap 2 paczki E3-ODB (20.11 wieczor): wpisane decyzje koordynatora do 6 pytan z etapu 1 (sekcja 8, pozycje 12-17),
zaktualizowane odstepstwa O3-O7, nowe O11 i O12, braki B1, B2, B4-B6 z decyzja; liczniki T2, T3, T4, T7, T11, T13 w
tabeli 2 dopasowane do decyzji.

Runda 1 recenzji PR #44 (21.11): "ZAL z odstepstwem" jest OSOBNA wartoscia wyniku z wlasnym licznikiem (decyzja
koordynatora nr 7 po recenzji, pozycja 18 w sekcji 8); nowe odstepstwa O13, O14, poprawione O1, O4, O6, O8, O10; lista
odstepstw do decyzji wlasciciela w sekcji 4a; liczniki T2, T3, T11 dopasowane do poprawionych narzedzi.

Zasady wypelniania: wynik tylko `ZAL` / `ZAL z odstepstwem O<n>` / `FAIL` / `ODLOZONE` / `NIE ZMIERZONO` (czesc kryterium).
**"ZAL z odstepstwem" NIE jest "ZAL"**: wpisuje sie je zawsze z numerem odstepstwa z sekcji 4, liczy w osobnym liczniku
(podsumowanie pod tabela 2 i sekcja 3) i kazde takie odstepstwo trafia na liste decyzji wlasciciela (sekcja 4a). Test,
ktorego kryterium zmierzono inaczej niz doslownie (odstepstwo w sekcji 4), moze miec najwyzej "ZAL z odstepstwem" - takze
gdy wszystkie liczby sa w normie. Liczniki, nie procenty;
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
| T2 | Wieczor od poczatku do konca | | sterownik `t2_wieczor.py` na programie z paczki: zgodnosc obslugi _ z 10; start analizy ponizej 1 s: _ z 9 (maks. _ s; czekalo w kolejce _); mapa mediana _ s (maks. _ s; plytka 1, pula zimna: _ s; do 40 s: _ z 1 i _ z 8) - gorne ograniczenie; przerwa okna maks. _ ms, przekroczen 200 ms: _; ubytki wg prawdy _: czerwonych _ / zoltych _ / zielonych (przeoczonych) _; prace cale na czerwono (falszywe alarmy): _ z _; lista "do dofrezowania" = prawda: TAK / NIE (brakuje _, nadmiarowych _); klikniecia "Ukruszona" _ z _, "OK" _ z _, ponowien _; T2 LACZNIE: _; platforma Qt: _ | | `T2/` |
| T3 | Poranek od poczatku do konca | | sterownik `t3_poranek.py` na programie z paczki, wiersz "WERDYKT T3": wiersze tabeli SE10 zgodne (liczone z ekranu) _ z 32, wg samego API _ z 32, "FAIL (ekran)" _; listy kompletnych i brakow odczytane z ekranu: tak _ / czesciowo _ / nie _ / nie dotyczy _ / nie odczytano _ (z 10 wierszy); pytanie przed "Zamknij piec": _; testy uzupelniajace: SE10 sesja _ z 33, ekran _ passed | | `T3/` |
| T4 | Pula | | top-1 "dobrze" _ z _; zimna, plytka 1: _ s (do 40 s: _ z 1); zimna, plytki 2-10: maks. _ s (do 40 s: _ z 9); ciepla, plytki 1-10: maks. _ s (do 40 s: _ z 10); pamiec szczyt _ GB | | `T4/` |
| T5 | Ramka na atrapie w sieci lokalnej | | (127.0.0.1, O8) potwierdzenia _ z 5 (seria _ z _), powtorek _; plan po restarcie _ s; Spacja maks. _ ms; zrodlo kodu w testach: INSTALACJA / REPO (modulow _ / _); adres karty PC: ramka W z 3 skanami: _ | | `T5/` |
| T6 | Excel na sztucznym arkuszu | | zapytania _ z 200; zle wiersze _; log regula 6: _; tryb "pytaj": _; tryb "cien": _ | | `T6/` |
| T7 | Odpornosc | | przypadki _ z 6 (silnik _, zamkniecie _, brak "Cyrkon" _, brak sieci _, brak ramki _, baza zajeta _), w tym "ZAL z odstepstwem (komunikat spoza zal. F)": _; komunikaty zgodne z zal. F: _ z _ | | `T7/` |
| T8 | Metryki | | metryki zgodne z liczeniem recznym: _ z _ (wieczor _ z _, rano _ z _) | | `T8/` |
| T9 | Dane osobowe | | trafienia calych nazw: repo _, logi _, wyniki _, ruch do ramki _; czlony wyjasnione _ z _; nazwy w `dane/`: _ | | `T9/` |
| T10 | Regresja silnika | | wyrownanie _ z 40; top-1 "dobrze" _ z _; falszywe czerwone na pracach calych _ z _ | | `T10/` |
| T11 | Stare plytki | | uklad rozpoznany _ z 40 (P2: _ z 24, P3a: _ z 16); skany FAIL (ostrzezenie bez nazwy wlasciwego ukladu): _; zielone przy zlym ukladzie _ (wiecej niz 0 = FAIL testu; gdy 0 z 0: pozycja 7 z T2: zielonych _); uklad zapisany w `skany` _ z _ | | `T11/` |
| T12 | Aktualizacja | | N -> N+1: polecen _, kod _; powrot: polecen _, kod _; ustawienia: sumy rowne _ z 3; baza: kopia _, migracja probna: schemat _ -> _, kopia = baza sprzed _, powrot po migracji: polecen _ (kody _ / _) | | `T12/` |
| T13 | Higiena repo | | naruszen _ (poza listami _, nie ASCII poza lista O11 _, konce linii _, STL / dane _); odstepstwo O11 (napisy ekranu nie-ASCII): _ plikow z 7, wierszy _ | | `T13/` |
| T14 | Proba "technik obsluguje bez instrukcji" (czlowiek) | | zadania _ z 11; interwencje _; zawahania ponad 10 s: _ (poprawione _, zostawione _) | wlasciciel, | `T14/` |
| T15 | Ramki na sprzecie | ODLOZONE (do potwierdzenia) | - | - | `ODLOZONE.md` |
| T16 | Prawdziwy skaner | ODLOZONE (do potwierdzenia) | - | - | `ODLOZONE.md` |
| T17 | Excel i MillBox na prawdziwych danych | ODLOZONE (do potwierdzenia) | - | - | `ODLOZONE.md` |

Podsumowanie T0-T13 (14 testow, cztery osobne liczniki, suma = 14): **ZAL _ ; ZAL z odstepstwem _ (numery: O_ ...) ;
FAIL _ ; NIE ZMIERZONO / niewykonane _**. T14: _. T15-T17: ODLOZONE _ z 3 (powod i warunek wznowienia w `ODLOZONE.md`).
Wg planu testow (stan 21.11) doslownie, bez odstepstwa, moga byc zaliczone tylko T1, T8, T9, T10; pozostale 10 testow ma
odstepstwo w sekcji 4 (T0: O1; T12: O2; T2: O3, O4, O13; T3: O5; T11: O6; T4: O7; T5: O8, O14; T6: O9, O14; T7: O12, O14;
T13: O10, O11), wiec ich najlepszy mozliwy wynik to "ZAL z odstepstwem".

## 3. Definicja "koniec etapu 3 = gotowe do trybu cienia" (plan, sekcja 7)

| Warunek | Stan | Dowod |
|---|---|---|
| T0-T14 zaliczone (regula do decyzji wlasciciela, sekcja 4a poz. 1: czy "ZAL z odstepstwem" liczy sie jako zaliczenie konca etapu; koordynator wpisuje tu osobno: ZAL _ / ZAL z odstepstwem _ / FAIL _) | | tabela 2 |
| T15-T17 zaliczone albo jawnie odlozone z powodem i warunkiem wznowienia | | `ODLOZONE.md` |
| Instrukcje jednostronicowe gotowe (wieczor, poranek) | | `Ramki/stanowisko/instrukcje/wieczor.html`, `poranek.html` (A11d) |
| Tabela "co robic, gdy nie dziala" gotowa | | `Ramki/stanowisko/instrukcje/co_robic_gdy_nie_dziala.html` (A11d) |
| Kroki 1-5 z PW "Uruchomienie" da sie wykonac bez programisty przy klawiaturze | | `instrukcje/instalacja_i_aktualizacja.md`, T0, T12 |

## 4. Odstepstwa (przyjete interpretacje kryteriow)

Lista wyjsciowa z `PLAN_TESTOW.md` - koordynator potwierdza albo zmienia kazda pozycje i dopisuje te, ktore wyjda w testach.

| Nr | Test | Odstepstwo | Potwierdzone (tak / nie / zmienione) |
|---|---|---|---|
| O1 | T0 | "czyste konto" = swiezy katalog na koncie `<konto-PC>`; "bez internetu" = instalator zawsze instaluje pakiety tylko z kol paczki (pip `--no-index`, dowod: 2 wiersze w `pip.log`), sieci fizycznie nie odcinano (opcja `/bez-sieci` wylacza tylko probe polaczenia samokontroli z ramkami - poprawione po probie generalnej 21.11) | |
| O2 | T12 | "baza zmigrowana z kopia" sprawdzona na paczce probnej z dodatkowa pozycja `MIGRACJE` (schemat wydan N i N+1 jest ten sam); powrot po migracji wymaga 2 polecen (kod 8, potem `/przywroc-kopie`) - "jedno polecenie" ocenia czesc A | |
| O3 | T2 | (zmienione w etapie 2, decyzja nr 12) program z paczki biegnie w procesie sterownika `t2_wieczor.py` (funkcja `aplikacja.main`, interpreter i katalog programu wersji przez `Polecenie.cmd`, opcja `--zamknij-po` jako bezpiecznik), a nie przez plik `Stanowisko.cmd`; dostaje kopie `ustawienia.toml` z `[sciezki]` w katalogu roboczym; start analizy mierzony doslownie (`analiza.od` stanu programu); czas do mapy = gorne ograniczenie (odczyt stanu co 20 ms); start programu przed pokazaniem okna poza pomiarem przerw petli | |
| O4 | T2 | (zmienione w etapie 2) okno `offscreen` (sesja bez ekranu); zegar sterownika w watku okna (odczyt stanu, klikniecia) wlicza sie do przerw petli (takze jednorazowy odczyt obrazu mapy kazdej plytki); przerwy petli mierzone bez kosztu rysowania na prawdziwym ekranie | |
| O5 | T3 | (zmienione w etapie 2, decyzja nr 13) SE10 przez okno prawdziwego kontrolera (`t3_poranek.py`, klikniecia po nazwach obiektow), ale wyniki skanow sztuczne (SE10 nie ma plikow STL - wchodza funkcja sesji wolana po analizie), zegar staly ustawiany przez sterownik, zlecenia SE10 wpisane do bazy funkcja testu, okno `offscreen`, ramki i Excel wylaczone; 2 z 10 wierszy z listami ekran pokazuje tylko czesciowo albo wcale (R31, R17) | |
| O6 | T11 | (decyzja nr 15) kryterium ma "albo": plytka z ukladem rozpoznanym = zaliczona; ostrzezenie bez nazwy wlasciwego ukladu = FAIL tego skanu (licznik); zielona przy zlym ukladzie = FAIL calego testu. Druga galaz kryterium ("ostrzezenie z nazwa wlasciwego ukladu") jest w programie NIESPELNIALNA (komunikat `niezgodny_uklad` nie zawiera nazwy ukladu - brak B5): kryterium liczone tylko pierwsza galezia, na 40 skanach `*_r54` | |
| O7 | T4 | (decyzja nr 17) mierzone i podane oba: pierwsza plytka po starcie (pula zimna) i kolejne (pula ciepla), osobne liczniki "do 40 s: n z m"; kryterium liczone dla wszystkich plytek; przekroczenie tylko przez pierwsza plytke po zimnym starcie = "ZAL z odstepstwem" z liczba sekund i pozycja do decyzji wlasciciela; przekroczenie przy puli cieplej = FAIL; pamiec = proces roboczy + okno | |
| O8 | T5 | wszystkie liczby kryterium T5 (5 z 5, 0 powtorek, plan do 5 s, Spacja ponizej 1 s) pochodza z testow pytest na 127.0.0.1 - atrapa ramki i program na TYM SAMYM komputerze (adres wpisany w testach); kod programu w tych testach z instalacji (`pytest_instalacja.py`, patrz O14). Na adresie karty sieciowej PC i programie z paczki tylko przebieg ramki W z 3 skanami - bez pomiaru 5 potwierdzen bez sieci, restartu ramki i Spacji; ramka P tylko w testach; takze ta czesc to jeden komputer (ruch przez stos sieciowy, nie przez kabel ani Wi-Fi). Prawdziwa siec = T15 (odlozony) | |
| O9 | T6 | arkusz w pamieci (atrapa), bez programu Excel | |
| O10 | T13 | "tylko pliki z list paczek" sprawdzane na poziomie KATALOGOW paczek, nie list pojedynczych plikow: jeden przedrostek `Ramki/stanowisko/` obejmuje caly program, wiec kontrola nie rozroznia, ktora paczka zmienila ktory plik, i NIE wyroznia plikow nietykalnych zmienionych od poczatku etapu (wg recenzji: `match.py` 9 commitow, `inspect.py` 7, `synth.py` 1 - zmiany z paczek, ktore mialy je w zakresie; do potwierdzenia przez koordynatora z historii PR); prace R58 / R59 (wg recenzji: 2 STL, 7 plikow danych, 11 duzych) liczone osobno i poza wynikiem | |
| O11 | T13 | (decyzja nr 16) 7 nowych plikow nie-ASCII z napisami ekranu (polskie znaki widziane przez technika - styl programu przyjety przez wlasciciela w paczkach A3 / A6): `stanowisko/dzien_skanera.py` (109 wierszy nie-ASCII), `stanowisko/dzien_skanera_kroki.toml` (134), `stanowisko/dzien_skanera_rdzen.py` (102), `stanowisko/statusy.py` (240), `stanowisko/ui/napisy.py` (66), `stanowisko/ui/napisy_rano.py` (111), `testy/test_dzien_skanera.py` (45) - liczby z proby na kopii integracyjnej a2236c1 (wpisac stan z commita wydania); lista w `narzedzia/t13_wyjatki_ascii.txt`; kazdy INNY nowy plik nie-ASCII = naruszenie (proba a2236c1: 1 taki plik - `stanowisko/ui/kandydaci.py`, 2 bajty - do rozstrzygniecia przed odbiorem) | |
| O12 | T7 | (decyzja nr 14) przypadek z komunikatem i dalsza praca, ale z tekstem komunikatu spoza PW zal. F = "ZAL z odstepstwem (komunikat spoza zal. F: <tekst>)" + pozycja w zadaniach wlasciciela; brak komunikatu albo brak dalszej pracy albo stan nieodtworzony = FAIL | |

| O13 | T2 | (decyzja nr 18, po recenzji PR #44) lista "do dofrezowania" powstaje z klikniec sterownika, ktory - jak technik - klika "Ukruszona" tylko na pracach z ubytkiem wg pliku prawdy pokazanych przez program na czerwono albo zolto (kolor czytany z obrazu mapy przed kliknieciem); praca z ubytkiem pokazana na zielono nie jest klikana i daje FAIL listy. T2 mierzy wiec, czy wieczor z programem daje prawdziwa liste na 7 plytkach przyjetych scenariusza (skany sztuczne); wykrywalnosc ubytkow jako taka mierza T10 / T16. Prac zoltych calych sterownik nie klika | |
| O14 | T5, T6, T7 czesc A, T1 | testy pytest pochodza z `<REPO>` (ten sam commit co paczka). T5, T6, T7 czesc A: kod programu ladowany z INSTALACJI przez `narzedzia/pytest_instalacja.py` (wynik podaje liczbe modulow z instalacji i z repo oraz "pliki *.py instalacji = repo: a z b"); procesy potomne testow (ramka w osobnym procesie, proces silnika) importuja kod sami i moga brac go z repo - tego licznik nie obejmuje. T1 (caly pytest): kod z `<REPO>`, z paczki tylko interpreter i pakiety; zgodnosc plikow instalacji z paczka potwierdza licznik sum w T0 | |

## 4a. Odstepstwa i sprawy do decyzji wlasciciela (kazde "ZAL z odstepstwem" musi tu miec wiersz)

| Nr | Sprawa | Odstepstwo / zrodlo | Decyzja wlasciciela |
|---|---|---|---|
| 1 | Czy "ZAL z odstepstwem" liczy sie jako zaliczenie konca etapu 3 (wg planu testow 10 z 14 testow T0-T13 ma odstepstwo) | sekcja 2, 3; uwaga 26 recenzji | |
| 2 | T2: technik-sterownik klika tylko prace czerwone / zolte; wykrywalnosc ubytkow mierza T10 / T16 | O13 | |
| 3 | T2 / T4: pierwsza plytka po zimnym starcie ponad 40 s (zmierzone w probach: 41,96-47,5 s; raporty A5: 63-68 s); przy odstepie 60 s druga plytka moze przez to czekac w kolejce i dac FAIL "start analizy ponizej 1 s" | O7 | |
| 4 | T2: przerwy petli okna mierzone w oknie `offscreen` (bez kosztu rysowania na ekranie) | O4 | |
| 5 | T3: po restarcie ekran pokazuje tylko ostatni zamkniety piec (R31), listy "do dofrezowania" ekran poranny nie pokazuje (R17) | O5 | |
| 6 | T3: okno nie pyta przed "Zamknij piec", gdy praca nieznana ma decyzje "bez projektu" (sesja liczy ja jako nierozstrzygnieta) - zamierzone czy poprawka P14 | obserwacja z prob T3 (3 z 3 przebiegow); uwaga 20 recenzji | |
| 7 | T5: liczby kryterium z testow na 127.0.0.1, atrapa i program na jednym komputerze | O8 | |
| 8 | T6: arkusz w pamieci; Excel przez COM jest na PC, a zostal przeniesiony do T17 | O9 | |
| 9 | T7: komunikaty spoza PW zal. F - uzupelnic zalacznik albo zmienic napisy | O12 | |
| 10 | T11: druga galaz kryterium (ostrzezenie z nazwa wlasciwego ukladu) niespelnialna w programie | O6, brak B5 | |
| 11 | T12: powrot po migracji bazy w 2 poleceniach (kod 8 + `/przywroc-kopie`) | O2 | |
| 12 | T13: kontrola na poziomie katalogow; pliki nietykalne niewyroznione; 7 plikow napisow nie-ASCII | O10, O11 | |
| 13 | T0: "czyste konto" = swiezy katalog, nie nowe konto Windows; sieci fizycznie nie odcinano | O1 | |
| 14 | T5-T7, T1: testy z repo; w T1 takze kod programu z repo | O14 | |
| 15 | Skan zestawu P3a bez drgniecia w prawdzie dostal od programu status "do_powtorzenia" (falszywe "skan ponownie"; proba doboru scenariusza T2, 20.11) - zestawic z wynikiem T10 (R59 pkt 6.2: 2 falszywe "skan ponownie") | uwaga 15 recenzji | |

## 5. FAIL i poprawki

| Nr | Test | Co nie przeszlo (liczba, log) | Paczka poprawki (galaz, PR) | Powtorka: wynik, data, dowod |
|---|---|---|---|---|
| | | | | |

## 6. Braki narzedzi stwierdzone przy planowaniu (stan na 20.11 - uzupelnic, co z nimi zrobiono)

| Nr | Brak | Skutek dla testu | Decyzja / paczka |
|---|---|---|---|
| B1 | sterownik T2 (program z paczki + pomiar petli okna + decyzje wg prawdy + zapis startu analizy) | T2: lista "do dofrezowania" i przerwy okna nie byly mierzone w jednym przebiegu przez program z paczki | USUNIETY: `narzedzia/t2_wieczor.py` + `t2_scenariusz.json` (E3-ODB etap 2, decyzja nr 12; po recenzji: kolory z ekranu, decyzja nr 18); proby skrocone na kopii repo i na instalacji probnej z paczki (21.11); pelnego przebiegu 10 x 60 s nie bylo |
| B2 | scenariusz SE10 przez ekran / kontroler aplikacji | T3: "przez ekran" niezmierzone | USUNIETY: `narzedzia/t3_poranek.py` (E3-ODB etap 2, decyzja nr 13); proba 20.11 na kopii integracyjnej: 32 z 32 |
| B3 | 200 zapytan przez prawdziwy Excel (COM) | T6 tylko na atrapie arkusza (dalej: T17) | |
| B4 | porownanie tekstow komunikatow z PW zal. F | T7: tabela sporzadzana recznie | zostaje (tabela reczna); regula wyniku: decyzja nr 14 (O12) |
| B5 | ostrzezenie z nazwa wlasciwego ukladu w aplikacji | T11: druga galaz kryterium niespelnialna | zostaje; regula wyniku: decyzja nr 15 (O6) |
| B6 | pliki napisow ekranu ze znakami spoza ASCII (7 nowych plikow) | T13: 7 naruszen na `main` 9ba9e91 | odstepstwo jawne O11 (decyzja nr 16); `t13_higiena.py` raportuje je osobno |

## 7. Zadania wlasciciela

| Nr | Zadanie | Co dostaje | Ile trwa | Stan |
|---|---|---|---|---|
| 1 | Proba T14 z osoba, ktora nie widziala programu | `T14/README.md`, zestaw `Ramki/etap3/t14/` | ok. 1 h | |
| 2 | Wizyta przy laptopie stanowiska (T0, T2, T3 na laptopie; otwarte 4-6) | `ODLOZONE.md`, paczka wydania | 1-2 h | |
| 3 | Skaner: "Dzien skanera" i pierwsze skany (T16) | `ODLOZONE.md` | | |
| 4 | Ramki: zlozenie i siec (T15) | `ODLOZONE.md` | | |
| 5 | Raporty MillBox i kopia pliku Excela (T17) | `ODLOZONE.md` | | |
| 6 | Decyzje otwarte: tabela `testy_wykrywalnosci` (M2), waxup w folderze zlecenia, wygasanie listy brakow, kolory pola B, uwagi do pokazu G2 | `Ramki/00_NADZOR_STAN.md` | | |
| 7 | (jesli wyjdzie w T7) komunikaty spoza PW zal. F: uzupelnic zal. F albo zmienic napis - lista tekstow z `T7/t7_komunikaty.md` | decyzja nr 14, O12 | | |
| 8 | (jesli wyjdzie w T4 / T2) pierwsza plytka po zimnym starcie programu ponad 40 s: przyjac albo zlecic poprawke - liczba sekund z `T4/t4_wynik.md` i `T2/t2_wynik.txt` | decyzja nr 17, O7 | | |
| 9 | Decyzje do odstepstw: lista w sekcji 4a (15 pozycji) - kazda "przyjmuje" / "poprawic" / "powtorzyc test" | sekcja 4a | 15-30 min | |

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
| 12 | T2: kryterium mierzone na programie z paczki sterownikiem `t2_wieczor.py` (prawdziwy program, okno - offscreen dopuszczalny jako odstepstwo, prawdziwy silnik, decyzje kliknieciami wg tabeli prawdy), nie zastapione testami jednostkowymi | 20.11 wieczor, odpowiedz nr 1 na pytania E3-ODB | |
| 13 | T3: SE10 (32 wiersze, dane i tabela z `test_session_rano.py`) przeprowadzony przez okno programu sterownikiem `t3_poranek.py`; na pytanie przed "Zamknij piec" sterownik odpowiada wg scenariusza | 20.11 wieczor, nr 2 | |
| 14 | T7: komunikat i dalsza praca, ale tekst spoza PW zal. F = "ZAL z odstepstwem (komunikat spoza zal. F: <tekst>)" + zadanie wlasciciela; brak komunikatu / dalszej pracy / stanu = FAIL | 20.11 wieczor, nr 3 | |
| 15 | T11: uklad rozpoznany = zaliczone; ostrzezenie bez nazwy wlasciwego ukladu = FAIL tego skanu (licznik); zielona przy zlym ukladzie = FAIL calego testu | 20.11 wieczor, nr 4 | |
| 16 | T13: 7 plikow nie-ASCII z napisami ekranu = odstepstwo jawne O11 z lista plikow i liczba wierszy; skrypt raportuje je osobno i zglasza kazdy inny plik | 20.11 wieczor, nr 5 | |
| 17 | T4: podawane oba pomiary (pula zimna - pierwsza plytka; pula ciepla - kolejne) z licznikami "do 40 s: n z m"; tylko pierwsza po zimnym starcie ponad 40 s = "ZAL z odstepstwem" + decyzja wlasciciela; ktorakolwiek przy cieplej = FAIL | 20.11 wieczor, nr 6 | |
| 18 | T2 "lista = prawda": sterownik klika "Ukruszona" / "OK" wylacznie na pracach, ktore program pokazal na czerwono albo zolto (kolor z ekranu przed kliknieciem, zapisany w wyniku); praca z ubytkiem pokazana na zielono = przeoczona, nieklikana, FAIL listy z licznikiem; praca cala na czerwono = falszywy alarm, klikniecie "OK", licznik osobno | 21.11, decyzja nr 1 po recenzji PR #44 | |
| 19 | T9: szukanie nazw bez wielkosci liter i znakow diakrytycznych, w UTF-8, cp1250, UTF-16 LE, `\uXXXX`; dowod bez zadnego czlonu nazwy | 21.11, nr 2 | |
| 20 | T3: "n z 32" liczone z tego, co pokazuje ekran; rozbieznosc ekran / stan = wiersz niezgodny | 21.11, nr 3 | |
| 21 | T5, T6, T7 czesc A: testy na programie zainstalowanym z paczki; T5 "siec lokalna" - odstepstwo O8 w pelnym brzmieniu, prawdziwa siec = T15 | 21.11, nr 4 | |
| 22 | T11: wszystkie 40 skanow `*_r54` przez aplikacje; kryterium liczone pierwsza galezia, druga - do decyzji wlasciciela | 21.11, nr 5 | |
| 23 | "ZAL z odstepstwem" = osobna wartosc i osobny licznik; kazde odstepstwo O<n> na liscie decyzji wlasciciela | 21.11, nr 7 | |
| | (decyzje z testow koncowych) | | |

## 9. Podpis

Koordynator: ____ ; data: ____ ; `main` po odbiorze: ____ ; koniec etapu 3: TAK / NIE (powod).
