# Raport recenzenta - PR #39 (E3-A11i, paczka wydania, instalacja, aktualizacja, powrot - wariant B), runda 2

- Data: 20.11.2026, 20:14-21:00, PC, konto `<konto-PC>`. Recenzja przyrostowa po poprawkach wykonawcy.
- Zakres: commity `eb77d7d..7f18cdf` galezi `e3/a11i` (17 commitow wykonawcy + wciagniecie `main` 5685f44); calosc
  `git diff main...origin/e3/a11i --stat` = 21 plikow, 5534 linie dodane, 1 usunieta.
- Metoda: wlasny przeglad `instalator.py` w calosci (1589 linii), 6 skryptow `.cmd`, diffu `zbuduj_wydanie.py`, instrukcji
  i opisu modulu; potem proby w kopii `<PC-katalog>\qc-wt\rec-a11i`; raport wykonawcy (sekcje 12-12.12) czytany na koncu.
  Pliki robocze: `<PC-katalog>\koordynator\robocze\rec-a11i\runda2\` (dalej `R2`): `logi\` (44 pliki), `proby\` (skrypty).
- Uruchomiono: testy paczki przed scaleniem (91 passed); skrypty prob rundy 1 na nowym kodzie (goracy dziennik, 16 sond);
  lokalne scalenie `e3/a11s` (6befc0d) + `e3/a11w` (2a6cac5) i 3 budowy paczki (0.3.1, 0.3.2 z `--wersja`, 0.3.3 z kopii
  drzewa z probna `MIGRACJE[2]`); PROBA GLOWNA kroki 1-7 na prawdziwej instalacji z prawdziwym modulem samokontroli
  (4 pelne instalacje srodowiska, 1 naprawa pelna i 2 przerwane, 2 powroty z przywroceniem kopii); 18 nowych sond na malej paczce;
  6 prawdziwych zakonczen procesu w trakcie kopii / przywracania bazy 137 MB; 13 wstrzykniec bledu; 1 przebieg
  `test_silnik.py` w srodowisku wersji. Pelnego pytest nie powtarzano. Naraz 1 proces python recenzenta (instalator
  z potomkami). Wolny RAM 65-67 GB przez cala sesje (`narz\ram.cmd` >= 20000 MB), wiec blokada `ciezki.ps1` nie byla wymagana.
- Sprzatanie: usuniete instalacje probne (`K` 4,1 GB, `K2` 1,4 GB), rozpakowane paczki, 3 pliki ZIP, kopia drzewa; zostaly
  logi, skrypty i pliki `.sha256`. Kopia recenzenta: `git checkout --detach origin/e3/a11i`, HEAD 7f18cdf, `git status
  --short` pusty (lokalny commit scalenia 82ce1c9 niewypchniety, bez galezi). Zatrzymywalem wylacznie wlasne procesy prob
  zabicia (okno polecen, instalator, 2 x `pip`), cudzych zadnego.

## 0. Werdykt

**Do scalenia po poprawkach.** B 0, P 1, D 6.

Poprawki rundy 2 sa rzetelne. Wszystkie uwagi P1-P6 rundy 1 sa zamkniete i kazda potwierdzilem wlasna proba (tabela 1.1);
baza nie zniknela ani nie zepsula sie w zadnej z 13 prob przerwania (6 prawdziwych zakonczen procesu, 4 punkty
sondy S4, 3 przypadki sondy E2). Proba glowna (T0 + T12 na paczce z lokalnego scalenia
`a11i + a11s + a11w`) przeszla w calosci: kody 10 -> 0 -> 0 -> 0 -> 11 / 0 / 8 / 0 -> 0 -> 0, a `test_silnik.py` w srodowisku
wersji dal 63 passed / 5 skipped w 245,6 s (w rundzie 1: 5 z 10 przebiegow nieudanych) - 1 przebieg, wiec to nie jest
pomiar czestosci.

Jedna uwaga P jest nowa i pochodzi z wdrozenia decyzji koordynatora: przy pierwszej instalacji KAZDY kod 1 samokontroli
daje `INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml`, takze gdy blad nie dotyczy ustawien (potwierdzone na prawdziwej
instalacji z prawdziwym modulem). Poprawka jest mala (kilka wierszy + test). Uwagi D mozna zrobic przy okazji; z nich
2 wiersze latki `.pth` (D2) warto dolozyc w tej samej rundzie.

## 1. Uwagi

Linie: `I` = `Ramki/stanowisko/instalacja/instalator.py` (stan 7f18cdf).

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| P1 | P | `I:1337-1347`; `instrukcje/instalacja_i_aktualizacja.md:20-25, 62` | Pierwsza instalacja (nie ma wersji biezacej), samokontrola konczy kodem 1 z powodu INNEGO niz ustawienia: modul z DLL nie laduje sie (laptop firmowy, WDAC - znane ograniczenie (c)), pakiety, baza. Galaz `kod == 1 and biezaca is None` nie patrzy, co jest bledem: wynik to zawsze `CO ZROBIC: otworz plik ustawien w Notatniku, wpisz w [sciezki] foldery ...` i `INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom zainstaluj.cmd ponownie (kod 10)`; instrukcja mowi "To nie blad". Proba na prawdziwej instalacji (`logi\47`, katalog `K2`, ustawienia poprawne, w `dane\` baza o schemacie 5): prawdziwy modul wypisal 1 blad `BLAD baza: baza nowsza niz program ...`, instalator: kod 10, WSTRZYMANA, rada o folderach. Sonda S1 (`BLAD moduly`): to samo. Sonda S2: proces samokontroli z kodem 1 i samym sladem wyjatku (blad importu, bez wiersza `SAMOKONTROLA:`): kod 10, WSTRZYMANA, 0 wierszy `BLAD` na ekranie. Technik poprawia plik, ktory jest dobry, i dostaje ten sam wynik bez konca; w rundzie 1 ten sam przypadek mial poprawny tekst ("popraw to, co wskazuja wiersze BLAD"). Danych nie narusza, wersja nie jest przelaczana. | Kod 10 / WSTRZYMANA tylko wtedy, gdy ostatni wiersz wyjscia to `SAMOKONTROLA: CZERWONA ...` i wszystkie wiersze `BLAD` maja kody z grupy ustawien (`folder_*` itp.); w pozostalych przypadkach dotychczasowe `NIEUDANA (kod 1)` z rada "popraw to, co wskazuja wiersze BLAD powyzej", a wyjscie bez wiersza `SAMOKONTROLA:` traktowac jak awarie (powtorzenie, potem kod 2). Test: pierwsza instalacja z `BLAD moduly` i z samym sladem wyjatku. |
| D1 | D | `I:951-959` | Uwaga D6 rundy 1 bez zmian (wykonawca: odlozone, opisane w "Zalozenia i granice"): zabicie miedzy zapisem `wersja_poprzednia.txt` a `wersja_biezaca.txt` zostawia oba wskazniki z ta sama wersja, `Wroc_do_poprzedniej.cmd` = kod 9; ponowne `zainstaluj.cmd` naprawia (sonda E1: bez zmian). | Jak w rundzie 1; moze zostac. |
| D2 | D | `I:1278-1284` wobec `I:1315` | Luka latki zgloszona przez wykonawce (12.11): wersja zalozona STARSZYM instalatorem (bez pliku `.pth`). `zainstaluj.cmd` uruchamia w kroku 5 `pip list` (`_zgodna_z_paczka`), a z `/testy` jeszcze `pip install` i drugie `pip list` (`_doinstaluj_testy`), i dopiero po kroku 5 doklada plik. Te 1-3 procesy `pip` startuja bez blokady `_wmi`. Skutek najgorszy: jeden z nich pada, instalator konczy kodem 6, ponowne uruchomienie przechodzi. Na stanowisku takich wersji nie ma (paczka 0.3.0 byla nieinstalowalna); sa tylko w katalogach prob na PC. Proba (`logi\46`): po usunieciu pliku z wersji biezacej i zmianie tresci w poprzedniej - `zainstaluj.cmd` i `Wroc_do_poprzedniej.cmd` dolozyly plik ("dolozono plik stanowisko_bez_wmi.pth"), kod 0. | Waga D - nie blokuje scalenia. Poprawka 2 wierszy (`zablokuj_wmi` przed `_zgodna_z_paczka` w galezi `stan == "zainstalowana"`) + asercja kolejnosci w tescie: dolozyc razem z P1, bo runda poprawek i tak bedzie. |
| D3 | D | `I:1006, 1348-1360` | Instalator ocenia samokontrole wylacznie po kodzie wyjscia, nie po ostatnim wierszu (umowa A11s podaje oba). Aktualizacja, proces samokontroli konczy kodem 1 bez wiersza `SAMOKONTROLA: CZERWONA` (blad importu modulu = kod 1 Pythona): "samokontrola zglosila bledy ... popraw to, co wskazuja wiersze BLAD powyzej", a wierszy `BLAD` nie ma (sonda S2). Wersja nie jest przelaczana. Prawdziwy modul lapie wyjatki w `main` i zwraca 2, wiec dotyczy to tylko bledu przed `main` (import). | Kod 0 uznawac tylko z ostatnim wierszem `SAMOKONTROLA: ZIELONA`, kod 1 tylko z `SAMOKONTROLA: CZERWONA`; inaczej jak awaria. Razem z P1. |
| D4 | D | `I:850-857, 604-611` | `Wroc_do_poprzedniej.cmd /przywroc-kopie`, gdy inny program trzyma plik bazy otwarty bez transakcji (przegladarka bazy): zamiana `<baza>.nowy` -> baza konczy sie `PermissionError`, kod 6 "pliku bazy nie da sie odczytac albo skopiowac ... Sprawdz dysk i miejsce na nim" zamiast kodu 5 "zamknij programy, ktore maja otwarta baze" (sonda S3). Baza cala i bez zmian, `.nowy` sprzatniety, w `kopie\` zostaje kopia `_odlozona_`. Przy bazie zablokowanej transakcja jest poprawnie kod 5. | `PermissionError` przy zamianie pliku bazy zglaszac jak baze zajeta (kod 5). |
| D5 | D | `instalacja/wzory/*.cmd` (`exit /b 4` w `:brak_wersji`); `instrukcje/instalacja_i_aktualizacja.md:56`; `opisy_modulow/instalacja.md:132` | Zgodnosc kodow 0-11 (kod / instrukcja / opis modulu): 11 z 12 zgodnych. Niezgodny kod 4: 5 skryptow katalogu instalacji zwraca 4 przy "nie ma gotowej wersji biezacej" (np. `Stanowisko.cmd` po zabiciu naprawy - proba kroku 6), a instrukcja i opis modulu opisuja 4 tylko jako brak / zla wersje Pythona (znaczenie skryptow podaje jedynie raport wykonawcy 12.7). Komunikat na ekranie jest jasny ("uruchom zainstaluj.cmd z rozpakowanej paczki wydania"). | Dopisac do wiersza kodu 4 w instrukcji i w opisie modulu. |
| D6 | D | `testy/test_instalacja.py` (brak testow); `I:1415`, `I:846-849`, `I:758-762` | 3 z 7 nowych wstrzykniec niewykryte (2.6): R4 sam Enter = zgoda na pytanie T / N; R2 `przywroc_kopie` bez kontroli pliku `-journal` obok bazy; R6 kopia bazy pomijana przy DOWOLNEJ identycznej kopii zamiast najnowszej. Kod jest poprawny; to zabezpieczenia drugiego rzedu (R2 i R6 nie umialem doprowadzic do zlego wyniku dla uzytkownika), ale R4 pilnuje bezpiecznej odpowiedzi domyslnej w skrypcie lezacym obok `Stanowisko.cmd`. | Test: pusta odpowiedz, spacja, `n` = kod 11; pozostale dwa wedle uznania. |

### 1.1 Uwagi rundy 1 - stan

| Uwaga r1 | Stan | Dowod z wlasnej proby |
|---|---|---|
| P1 kopia bazy przy `-journal` | zamknieta | Skrypt rundy 1 (`proby\goracy_dziennik_r2.py`, `logi\02`): baza 20000 wierszy, transakcja przerwana `os._exit`, `-journal` 5 218 816 B -> kopia `..._v1.sqlite` 4 575 232 B, 20000 wierszy, 0 niezatwierdzonych, `integrity_check ok`, `schemat_kopii` = 1 (r1: "malformed", nazwa `_vx`). 3 prawdziwe zakonczenia procesu w trakcie kopii bazy 137 MB (po 40 / 150 / 400 ms z 678 ms): baza cala, zostaje tylko `*.sqlite.nowy` - nie jest kandydatem do przywrocenia (`logi\45`). |
| P2 przerwane `przywroc_kopie` | zamknieta | Sonda E2 rundy 1, 3 przypadki (`logi\03`): plik bazy jest w kazdym; blad systemu przy zamianie = kod 6, baza bez zmian; ponowny powrot kod 0. Sonda S4, 4 punkty zabicia: 4 z 4 baza jest, `quick_check ok`. 3 prawdziwe zakonczenia procesu w trakcie przywracania (100 / 600 / 1100 ms z ok. 1350 ms): baza 400000 wierszy, cala. Zabicia dokladnie w chwili zamiany pliku nie trafilem zegarem - pokrywa je wstrzykniecie. |
| P3 wybor kopii przy drugim powrocie | zamknieta | Prawdziwa instalacja (`logi\43`): po pracy na 0.3.1 10 zdarzen -> `Wroc /tak` do 0.3.3 robi kopie `_przed_0.3.3_..._203334_v1` -> druga migracja (13 zdarzen) -> `/przywroc-kopie` wybiera `stanowisko.kopia_v1_..._203338` (najnowsza), "10 w kopii, 13 teraz (+3)", po powrocie 10 zdarzen. Sonda A: 7 skanow = 7 w kopii programu (r1: 3). |
| P4 obce podkatalogi `wersje\*` | zamknieta | Sonda I: obcy katalog z plikiem zostal, kod 0 (r1: usuniety). Wstrzykniecie W-N8 wykryte. |
| P5 wymiana wersji biezacej; pisownia numeru | zamknieta | (a) Sonda J: `1.0-RC1` na `1.0-rc1` = kod 3, pliki wersji biezacej bez zmian; `1.0.` odrzucone juz przy budowie. (b) Prawdziwa instalacja, krok 6: blad `pip` w naprawie wersji biezacej = "naprawa nieudana - przywrocono katalog wersji 0.3.1 sprzed naprawy", kod 6; prawdziwe zabicie instalatora 10 s po starcie `pip` = `_stara_0.3.1` + znacznik, `Stanowisko.cmd` kod 4 z komunikatem, nastepne `zainstaluj.cmd`: "przywrocono wersje 0.3.1 sprzed przerwanej wymiany (naprawy)", kod 0. |
| P6 testy izolacji | zamknieta | Wstrzykniecia W-N27 (plik `.pth` po `ensurepip`) i W-N24 (wzor bez czyszczenia `PYTHONPATH`) wykryte (`logi\50`); polecenie `pip` w tescie `test_p6_polecenia_srodowiska...`. |
| P7 testy silnika w srodowisku wersji | zamyka PR #43 + latka | Poza paczka. Krok 7: 1 przebieg, 63 passed / 5 skipped, 245,6 s, kod 0. |
| D1 `PYTHONHOME` | zamknieta | `zainstaluj.cmd` czysci zmienne, proby z `-I` (przeglad). |
| D2 dwa instalatory | zamknieta | Sonda B: drugi = kod 6 "inna instalacja albo powrot juz trwa", pierwszy kod 0; wstrzykniecie R5 wykryte. |
| D3 pauza | zamknieta | Pauza zawsze, chyba ze `/bez-pauzy` (przeglad; proby z `/bez-pauzy`). |
| D4 pusty folder, BOM | zamknieta | Sonda D: pusty `folder_millbox` kod 0; BOM kod 7 z rada o kodowaniu. |
| D5 srednik | zamknieta | Przeglad `I:1211-1213` (bez proby). |
| D6 dwa wskazniki | otwarta | Sonda E1 bez zmian (teraz D1). |
| D7 instrukcja | zamknieta | Przejscie instrukcji w probie glownej; reszta: D5. |

## 2. Wlasne proby

`PY` = `<PC>\AppData\Local\Programs\Python\Python312\python.exe`, `K` = `R2\K`, `P1` / `P2` / `P3` = rozpakowane paczki
0.3.1 / 0.3.2 / 0.3.3. Kazde polecenie przez `cmd /c ... < NUL`, czas mierzony zegarem powloki.

### 2.1 Testy paczki przed scaleniem

`py.cmd -m pytest -q -p no:cacheprovider testy\test_instalacja.py testy\test_zbuduj_wydanie.py` w kopii 7f18cdf:
**91 passed, 106,5 s** (`logi\01`; wykonawca: 91 passed, 105,8 s).

### 2.2 Lokalne scalenie i budowa

`git -C <PC-katalog>\qc-wt\rec-a11i merge --no-edit origin/e3/a11s origin/e3/a11w`: **bez konfliktow** (jedno scalenie
trzech galezi, commit lokalny 82ce1c9; 9 plikow z A11s / A11w, zaden wspolny z A11i).

| Polecenie | Wynik |
|---|---|
| `py.cmd narzedzia\zbuduj_wydanie.py --wyjscie R2\wydanie --kola <PC-katalog>\wydania\kola` | kod 0, 6 s: `Stanowisko_0.3.1.zip`, 444 131 034 B, SHA-256 `66872dff...d376`, 202 pliki + `SHA256SUMS` (program 123, kola 73, kola testowe 3) |
| to samo z `--wersja 0.3.2` | kod 0, 7 s: 444 131 031 B, `65311bab...16c6` |
| po rozpakowaniu 0.3.1 | `sha256sum -c SHA256SUMS`: 202 OK, 0 zlych; `SUMY_PROGRAMU.sha256`: 122 OK (123 pliki w `program\` razem z plikiem sum); sa `requirements.txt`, `instrukcje\` (1 plik - A11d niescalone), `ramka\`, `narzedzia\`; `testy/`, `raporty/`, `opisy_modulow/`, `__pycache__`, `zbuduj_wydanie.py`: 0; 6 skryptow `.cmd` z CRLF |
| `--zrodlo <kopia drzewa z probna MIGRACJE[2]> --wersja 0.3.3 --data ...` | kod 0: 444 131 051 B, `e7dbb5e4...9b14` (tylko do proby migracji; repo bez zmian) |

Dwoch budow tego samego numeru w rundzie 2 nie porownywalem (kryterium 1: test paczki + proba rundy 1).

### 2.3 PROBA GLOWNA (proba generalna T0 i T12) - wg `instrukcje/instalacja_i_aktualizacja.md`

Opcje spoza domyslnych: `/katalog K /python PY` (konto nie ma prawa zapisu w `C:\Stanowisko` ani Pythona w typowym miejscu)
i `/bez-pauzy`; od kroku 4 takze `/bez-sieci`.

| Krok | Polecenie | Kod | Czas | Ostatnie wiersze / stan | Czy mowi, co zrobic |
|---|---|---|---|---|---|
| 1 | `P1\zainstaluj.cmd /katalog K /python PY /bez-pauzy` (pusty katalog) | 10 | 73 s | pakiety 73 z 73; `SAMOKONTROLA: CZERWONA (ok 11, ostrzezenia 8, bledy 2)`; 2 wiersze `BLAD` (folder skanera, folder Cyrkon), `Plik ustawien: <pelna sciezka>`, `CO ZROBIC: otworz plik ustawien w Notatniku ...`, `INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom zainstaluj.cmd ponownie (kod 10)`; w `K` nie ma jeszcze skryptow ani wskaznika | tak |
| 2 | edycja 4 folderow i `operatorzy`, to samo polecenie | 0 | 6,3 s | "juz zainstalowana i zgodna z paczka - pliki bez zmian", `ZIELONA (ok 16, ostrzezenia 5)`, `INSTALACJA: GOTOWA - wersja biezaca 0.3.1`; SHA-256 ustawien przed = po | tak |
| 3 | `K\Samokontrola.cmd --bez-sieci` | 0 | 2,2 s | `ZIELONA (ok 16, ostrzezenia 5)`; "sumy SHA-256 plikow programu zgodne 122 z 122, plikow nadmiarowych 0"; "pakiety zgodne 11 z 11 z requirements.txt (bez pytest)" | - |
| 3 | `K\Stanowisko.cmd --atrapa --zamknij-po 5` / `--zamknij-po 5` (Qt offscreen) | 0 / 0 | 6,7 s / 7,8 s | program startuje i zamyka sie; baza zalozona w `K\dane` | - |
| 3 | `K\Polecenie.cmd -I -c "import sys; print(sys.modules.get('_wmi', 'brak'), sys.prefix)"` | 0 | ponizej 1 s | `None ...\wersje\0.3.1\venv`; plik `Lib\site-packages\stanowisko_bez_wmi.pth` jest (tresc jak w kodzie); `platform.system()`, `machine()`, `win32_ver()` dzialaja; `sys.path` 9 pozycji, 0 z interpretera bazowego | - |
| 3 | `K\Polecenie.cmd -I -m pip --version`; `pip list --format=freeze` wobec `zamrozone.txt` | 0 | 0,3 s | `pip 25.0.1`; 73 z 73 zgodne, jedyny nadmiarowy `pip==25.0.1` | - |
| 4 | `P2\zainstaluj.cmd /katalog K /python PY /bez-pauzy /bez-sieci` | 0 | 78,3 s | kopia `kopie\stanowisko_przed_0.3.2_20261120_202154_v1.sqlite` "sprawdzona (quick_check ok ...)", `ZIELONA (ok 17, ostrzezenia 4)`, wersja biezaca 0.3.2, poprzednia 0.3.1; SHA-256 ustawien, bazy i pliku w `dane\wyniki` przed = po; `Stanowisko.cmd --zamknij-po 5` kod 0 (8,3 s); `Wersje.cmd`: 0.3.1 poprzednia, 0.3.2 BIEZACA | tak |
| 5 | `K\Wroc_do_poprzedniej.cmd /bez-pauzy`, wejscie puste / odpowiedz `N` | 11 / 11 | 0,3 s | pytanie `Powrot z wersji 0.3.2 do wersji 0.3.1. Kontynuowac? [T/N]:`, `POWROT: ANULOWANY (kod 11) - wersja biezaca bez zmian: 0.3.2. Odpowiedz T przelacza wersje; ...`; wskaznik i baza bez zmian | tak |
| 5 | to samo, odpowiedz `T` | 0 | 2,8 s | "schemat zgodny - baza zostaje bez zmian", `POWROT: GOTOWY - wersja biezaca 0.3.1 (poprzednia: 0.3.2)`; SHA-256 bazy przed = po; `Stanowisko.cmd --zamknij-po 5` kod 0 | tak |
| 5b | paczka 0.3.3 z probna migracja: `P3\zainstaluj.cmd ...`, start programu, `Wroc_do_poprzedniej.cmd /tak /bez-pauzy` | 0, 0, 8 | 62,7 s; 7,8 s; 0,4 s | baza v2 + kopia programu; ostrzezenie: "Kopia sprzed aktualizacji: ... z 2026-11-20 20:32 (schemat 1) - najnowsza sprawdzona", "tabela zdarzenia: 6 w kopii, 9 teraz (+3)", `POWROT: NIEUDANA (kod 8) - wersja biezaca bez zmian: 0.3.3`; baza bez zmian; odpowiedz `T` bez opcji: tez kod 8 | tak (`/przywroc-kopie`) |
| 5b | `K\Wroc_do_poprzedniej.cmd /przywroc-kopie /bez-pauzy` | 0 | 2,9 s | baza v1 z 6 zdarzeniami, dotychczasowa w `kopie\stanowisko_odlozona_v2_...`, 0.3.1 startuje (kod 0); drugi powrot po pracy na 0.3.1: tabela 1.1, P3 | tak |
| 6 | `P1\zainstaluj.cmd ...` na wersji biezacej 0.3.1 (ten sam numer) | 0 | 3,6 s | "juz zainstalowana i zgodna z paczka", "ta sama wersja co biezaca - kopia bazy niepotrzebna", `GOTOWA` | tak |
| 6 | to samo po dopisaniu wiersza do `program\stanowisko\statusy.py` (naprawa) | 0 | 81,7 s | "pliki programu niezgodne z sumami (1) - naprawa (instalacja od nowa)", 73 z 73, `ZIELONA`, `GOTOWA`; przedtem 2 przerwania naprawy: tabela 1.1, P5 | tak |
| 7 | `P1\zainstaluj.cmd ... /testy` | 0 | 7,4 s | "dokladam zestaw testowy", "zestaw testowy (pytest): 3 pakietow", pakiety 76 z 76 | tak |
| 7 | `K\Polecenie.cmd -X faulthandler -m pytest <kopia>\Ramki\stanowisko\testy\test_silnik.py -q -p no:cacheprovider --rootdir <kopia>\Ramki\stanowisko -o faulthandler_timeout=900` (kopia = commit paczki 82ce1c9) | 0 | 245,6 s | `63 passed, 5 skipped in 245.62s` (20:27:23-20:31:31), 1 przebieg | - |

Dziennik instalacji (`logi\60`, 253 wiersze): kroki, kody i poziomy wierszy samokontroli bez opisow; nazwy konta 0 razy.
Niesprawdzone w tej probie: dwuklik w oknie Eksploratora, skrot na pulpicie (`/skrot`), katalog domyslny `C:\Stanowisko`.

### 2.4 Bezpieczenstwo bazy i przerwania (kod zmieniony w rundzie 2)

| Proba | Wynik |
|---|---|
| prawdziwe zakonczenie procesu (`os._exit` z watku) w `kopia_bazy` po 40 / 150 / 400 ms i w `przywroc_kopie` po 100 / 600 / 1100 ms, baza 136,9 MB (`proby\zabicie_czasowe.py`, `logi\45`) | 6 z 6: plik bazy jest, 400000 wierszy, `quick_check ok`; w `kopie\` zostaja `*.sqlite.nowy` i `*.nowy-journal` (do 137 MB, nie sa kandydatami; nastepna kopia tej samej wersji przechodzi i jest cala) |
| sonda S4: zabicie po backup przed kontrola kopii / przy zmianie nazwy kopii / po odlozeniu bazy / po przywroceniu przed przelaczeniem (`logi\40`) | 4 z 4: baza jest i cala; ponowne polecenie kod 0; 0 kopii `*.sqlite` bez kontroli; pliki `.nowy` sprzatniete |
| sonda S3: baza zablokowana przez inne polaczenie (`BEGIN EXCLUSIVE`) od poczatku aktualizacji | kod 5 "baza ... jest zajeta przez inny program", 0 plikow zmienionych poza dziennikiem; po zwolnieniu kod 0 |
| to samo, blokada zalozona dopiero w kroku pip | kod 5 w kroku kopii; nowe pliki tylko w `wersje\2.0`, wskaznik bez zmian |
| powrot `/przywroc-kopie` przy bazie zablokowanej / otwartej przez inny uchwyt | kod 5, 0 zmian / kod 6 (D4), baza cala |
| sonda S2: samokontrola ginie 3 razy (`0xC0000005`) | kod 2, 3 uruchomienia, wersja nie przelaczona (pierwsza instalacja i aktualizacja): "samokontrola ... zakonczyla sie awaryjnie (kod 0xC0000005, proby: 3) ... To nie jest blad ustawien. Uruchom zainstaluj.cmd ponownie ..." |
| sonda S2: awaria, potem kod 0 | 2 uruchomienia, przelaczenie - zgodnie z zalozeniem; w 6 z 6 przypadkow zakonczonych awaria albo kodem 1 wersja nie zostala przelaczona |
| sonda B (runda 1): drugi instalator w trakcie pierwszego | drugi kod 6, pierwszy kod 0 |
| prawdziwy modul, baza o schemacie nowszym niz program (sonda H rundy 1; `logi\47`) | `BLAD baza: baza nowsza niz program` -> wersja nie jest przelaczana (dobrze); komunikat koncowy: P1 |

### 2.5 Latka `.pth` i `ensurepip`

- Kolejnosc w `Srodowisko.utworz` (`I:343-367`): `venv --copies --without-pip` -> plik -> `ensurepip` -> proba (`_wmi` ma byc
  `None`, inaczej kod 6). `pyvenv.cfg` instalacji: `command = ... -m venv --without-pip ...`.
- Siec: `Lib\ensurepip\__init__.py` 3.12.10 uruchamia `pip install --no-cache-dir --no-index --find-links <katalog tymczasowy>`,
  usuwa zmienne `PIP_*`, ustawia `PIP_CONFIG_FILE` na urzadzenie puste (przeglad linii 115-120, 190); `pip install` pakietow:
  `--isolated --no-index --only-binary=:all:`, w `pip.log` "Ignoring indexes: https://pypi.org/simple". Fizycznie
  odcietej sieci nie sprawdzalem.
- Wersja `pip`: 25.0.1 (kolo dolaczone do Pythona 3.12.10) - poza lista zamrozona (`PAKIETY_SRODOWISKA`), kontrola srodowiska
  go pomija; samokontrola porownuje 11 pakietow z `requirements.txt` i `pip` wsrod nich nie ma. Inny 3.12.x da inna wersje
  `pip` bez skutku dla obu kontroli (przeglad; na PC jest tylko 3.12.10).
- Z opcja `-S` interpretera plik nie dziala (`brak`) - zaden skrypt paczki jej nie uzywa.
- Uzupelnianie pliku: `logi\46` (D2).

### 2.6 Wstrzykniecia bledu (`proby\mutacje_r2.sh`, `logi\50`, stan 7f18cdf, `pytest -x`)

Powtorzone z listy wykonawcy (6, rozne obszary): **5 z 6 wykrytych** - W-N5 baza przenoszona przed wstawieniem kopii, W-N8
katalog bez zapisu instalacji = niedokonczony, W-N11 nieudana naprawa nie przywraca wersji, W-N27 plik `.pth` po `ensurepip`,
W-N24 wzor `Stanowisko.cmd` bez czyszczenia `PYTHONPATH`. Niewykryte: W-N2 w MOIM wariancie (tryb `ro` tylko w `kopia_bazy`;
68 passed) - to zmiana bez skutku, bo krok 4 wczesniej otwiera baze do zapisu i wycofuje dziennik; wariantu wykonawcy
(`schemat_bazy` tylko do odczytu) nie powtorzylem.

Nowe w kodzie rundy 2 (7): **4 z 7 wykrytych** - R1 trzy awarie samokontroli = zielona, R3 powrot do wersji o nowszym
schemacie bez kopii bazy, R5 powrot bez blokady instalatora, R7 brak kontroli pliku `.nowy` bez bazy w instalacji.
Niewykryte: R2, R4, R6 (D6). Dwa pierwsze uruchomienia skryptu byly nieudane z mojego bledu w cudzyslowach (0 testow;
logi `50_mutacje_nieudany_start*`), trzecie jest miarodajne.

### 2.7 Zasady i zakres

`git diff --name-status main...origin/e3/a11i`: 21 plikow, wszystkie z listy zlecenia; plikow nietykalnych 0;
`ustawienia.py`, `ustawienia.przyklad.toml`, `requirements.txt`, `baza.py` bez zmian. Pliki nowe: 0 wierszy spoza ASCII,
0 znakow CR; 6 plikow `.cmd`: CR = LF w kazdym wierszu (81, 25, 27, 29, 36, 38); `README.md` (istniejacy, CRLF i polskie
znaki) w swoim stylu, `opisy_modulow/README.md` (istniejacy) - wiersz samokontroli identyczny ze zdaniem z raportu A11s.
ZIP, kol i katalogow roboczych w gicie nie ma; najwiekszy plik paczki 98 283 B. 17 z 17 commitow wykonawcy w rundzie ze stopka `Co-Authored-By`. Danych osobowych nie znalazlem (test uzywa fikcyjnej nazwy profilu).

## 3. Kryteria zlecenia

| Nr | Kryterium | Ocena w rundzie 2 |
|---|---|---|
| 1 | 2 budowy = ten sam SHA-256; `SHA256SUMS` zgodne | sumy po rozpakowaniu: potwierdzone wlasna proba (202 z 202); rownosc 2 budow: potwierdzone testem paczki, w rundzie 2 nie powtarzane |
| 2 | czysta instalacja bez sieci, start z `--atrapa` i bez | potwierdzone wlasna proba (kroki 1-3), z prawdziwym modulem samokontroli |
| 3 | srodowisko bez pakietow bazowych, wersje = lista zamrozona | potwierdzone wlasna proba (0 pozycji bazowych, 73 z 73) |
| 4 | aktualizacja N -> N+1 jednym poleceniem | potwierdzone wlasna proba (krok 4) |
| 5 | powrot do N jednym poleceniem | potwierdzone wlasna proba (krok 5; `/tak` albo odpowiedz T) |
| 6 | scenariusz z migracja | potwierdzone wlasna proba (krok 5b, dwa powroty) |
| 7 | bledy: wersja biezaca nietknieta i jasny komunikat | baza zajeta, przerwana naprawa, 3 awarie samokontroli, drugi instalator: potwierdzone wlasna proba; zepsuty plik paczki, brak Pythona, program uruchomiony, brak miejsca: potwierdzone testem paczki (proby wlasne w rundzie 1). Komunikat pierwszej instalacji przy bledzie spoza ustawien: P1 |
| 8 | testy na malej paczce; pelny pytest 0 failed | testy paczki: potwierdzone wlasna proba (91 passed); pelny pytest: wg wykonawcy 1922 passed / 9 skipped / 0 failed na e877827 (ostatnie wiersze logu `logi_r2\70` widzialem; pozniejsze commity zmieniaja tylko raport) - niesprawdzone przeze mnie |
| 9 | instrukcja jednostronicowa | potwierdzone przejsciem krok po kroku (67 wierszy); braki: D5, P1 (wiersz kodu 10) |

Decyzje koordynatora (`a11i-r2.md`): WSTRZYMANA / kod 10 - wdrozone, zakres za szeroki (P1); czas drugiego uruchomienia
6,3 s; pytanie T / N i kod 11, `/tak` - wdrozone (krok 5); inna wersja poprawkowa 3.12 z ostrzezeniem - potwierdzone
przegladem (`I:1199-1204`, `1232-1233`) i testem wykonawcy; numeracja `0.3.<n>` - `WERSJA` = 0.3.1, ostrzezenie przy numerze
z listy wydan (przeglad). Uwagi miedzy paczkami: `requirements.txt` w paczce, `SUMY_PROGRAMU` (122 z 122, 0 nadmiarowych
w prawdziwym module), caly katalog `instrukcje/`, wiersz w `opisy_modulow/README.md`, kopia bazy z `-journal` - wdrozone.
Znane ograniczenia (a) (b) (c) sa w `README.md` i w opisie modulu.

## 4. Zakres plikow i zasady

Zmiany tylko w plikach z listy zlecenia. Umowa A11s sprawdzona na prawdziwym module (6befc0d): wywolanie
`python -m stanowisko.samokontrola --ustawienia PLIK --sumy PLIK [--bez-sieci]`, kody 0 / 1 / 2 obsluzone osobno, kod spoza
umowy powtarzany do 3 razy i nigdy zielony; instalator NIE czyta ostatniego wiersza (D3). Po instalacji samokontrola nie
zglasza obcych ani zmienionych plikow. Instalator uzywa tylko biblioteki standardowej; wskaznik wersji to plik tekstowy.

Odstepstwa wykonawcy, ktore przyjmuje: P2 na prawdziwej instalacji przez blad wstrzykniety (prawdziwe zakonczenia procesu
zrobilem sam, 2.4); jedna instalacja probna po latce; pelny pytest rownolegle z innym. Raport wykonawcy zgadza sie z moimi
pomiarami tam, gdzie je powtorzylem (kody krokow, 73 z 73, czasy 6-7 s i 60-80 s).

## 5. Do decyzji wlasciciela

1. P1: czy kod 10 ma zostac dla kazdego bledu pierwszej instalacji z neutralnym tekstem, czy wrocic do "NIEUDANA (kod 1)"
   dla bledow spoza ustawien (propozycja w tabeli).
2. Po zamknieciu okna w trakcie NAPRAWY wersji biezacej program nie startuje do nastepnego `zainstaluj.cmd` - potrzebna jest
   rozpakowana paczka tej wersji (opisane przez wykonawce). Czy instrukcja ma kazac zachowac paczke ostatniej instalacji.
3. Kopie bazy i pozostalosci po przerwaniach (`kopie\*.sqlite.nowy`) nie sa kasowane; w probie 5b po 2 powrotach bylo
   7 plikow kopii. Kto i kiedy je porzadkuje.
4. Niesprawdzone na PC, jak w rundzie 1: laptop firmowy (WDAC, antywirus, znacznik pliku z sieci), prawdziwy brak miejsca,
   Python 3.12.x inny niz 3.12.10, dwuklik w Eksploratorze.
5. Paczka koncowa do T0 / T12 musi powstac z `main` po scaleniu A11s, A11w i tej galezi; moje paczki probne (commit lokalny
   82ce1c9) usunalem, sumy sa w `R2\wydanie\*.sha256` i nie sa wydaniem.

WERDYKT: do scalenia po poprawkach (B 0, P 1, D 6)
