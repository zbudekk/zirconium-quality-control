# Plan testow koncowych etapu 3 (T0-T13)

Paczka E3-ODB, 20.11.2026. Zrodlo kryteriow: `Ramki/plan_etap3_pelna_aplikacja_2026-11-16.md`, sekcja 7 (kryteria ponizej
sa przepisane doslownie). Plan jest napisany dla stanu "`main` po scaleniu paczek A11s, A11i, A11w, P14, A11d";
nazwy plikow i opcji paczek A11s, A11i, A11w, P14 potwierdzono w etapie 2 na kopii integracyjnej (nizej) - w tym pliku
nie ma juz miejsc "do potwierdzenia po scaleniu"; zostaly tylko odsylacze do paczki A11d w `T14/README.md` (runda 2 tej
paczki trwa). Po scaleniu wszystkiego do `main` wystarczy kontrola: commit wydania = stan sprawdzony (roznica plikow
`git diff --stat a2236c1 <commit wydania> -- Ramki/stanowisko`). Testow koncowych jeszcze nikt nie wykonal - to jest przepis.

**Etap 2 (20.11, wieczor):** wpisane decyzje koordynatora do 6 pytan z etapu 1 (T2 i T3 - sterowniki `t2_wieczor.py` i
`t3_poranek.py`; T7, T11, T13, T4 - akapity "Decyzja koordynatora 20.11"). Nazwy i opcje potwierdzone na kopii
integracyjnej `<PC-katalog>\qc-wt\integ` (commit a2236c1 = `main` 9ba9e91 + `e3/a11w` + `e3/a11s` + `e3/a11i` + `e3/p14`);
paczka A11d (runda 2 w toku) nie jest w tej kopii - jej odsylacze zostaja "do potwierdzenia".

**Runda 1 recenzji PR #44 (21.11, noc):** poprawione wg raportu recenzenta (uwagi 1-28) i 8 decyzji koordynatora:
T2 (sterownik czyta kolory prac z ekranu i klika tylko prace czerwone / zolte), T3 (liczba "n z 32" z ekranu), T9
(szukanie bez wielkosci liter i znakow diakrytycznych, samotest), T5 / T6 / T7 (testy na kodzie z instalacji przez
`pytest_instalacja.py`), T8 (sciezki baz), T11 (40 skanow, regula nazwy ukladu), T12 czesc B (polecenia), T13 (dowody
ASCII + LF przez `dowody_lf.py`), T14 (22 z 22). `main` = bcd0678 zawiera juz wszystkie paczki (A11s, A11i, A11w, P14,
A11d); w drodze jest tylko E3-P15 (ochrona klikniec mapy - sterownik T2 ja obsluguje). Przy kazdym poleceniu planu jest
teraz wiadomo, czy bylo wykonane: tabela "Stan sprawdzenia polecen" na koncu pliku (instalacja probna z paczki
`<PC-katalog>\t0\proba\Stanowisko`, wersja 0.3.1 z commita f5c3e01 = `main` + P15, albo kopia repo).

Zasady wykonania (obowiazuja kazdego wykonawce):

- Test nieudany = wpis **FAIL** z liczba i logiem. Nie pomijac, nie oslabiac, nie powtarzac "az wyjdzie" bez zapisu
  kazdej proby. Krok niewykonalny = wpis "NIE ZMIERZONO" z powodem, nie puste pole.
- Liczniki, nie same procenty (np. 10 z 10).
- Dane osobowe: w dowodach, logach i wiadomosciach tylko `sha16` i numery kuwet z danych sztucznych. Nazw folderow i
  plikow zlecen nie wypisywac (takze z `<PC-katalog>\app\Prace_test`). Zapytania do bazy tylko przez
  `narzedzia\sql_odczyt.py` (odrzuca tabele z nazwami).
- Wynik testu ma jedna z czterech wartosci: **ZAL**, **ZAL z odstepstwem O<n>** (kryterium zmierzone inaczej niz
  doslownie albo spelnione z zastrzezeniem - numer odstepstwa z `RAPORT.md` jest obowiazkowy), **FAIL**, **NIE
  ZMIERZONO**. "ZAL z odstepstwem" to OSOBNA wartosc, nie ZAL: w `RAPORT.md` ma wlasny licznik i kazde takie
  odstepstwo trafia na liste decyzji wlasciciela (decyzja koordynatora nr 7 po recenzji).
- Dowody: male pliki tekstowe / JSON. W trakcie testow wykonawca pisze je do `<ROB>` =
  `<PC-katalog>\koordynator\robocze\odbior\T<nr>\` (poza repo); po komplecie trafiaja do
  `Ramki/etap3/odbior_koncowy/dowody/T<nr>/` osobna galezia (w tym pliku `<DOW>`). Bez STL, baz, zapisow ruchu, ZIP-ow -
  te zostaja w `<ROB>`. Pliki dowodow: ASCII + LF. Przekierowanie `cmd >` daje CRLF, a czesc narzedzi programu pisze
  znaki spoza ASCII - dlatego PRZED `git add` kazdy katalog dowodow przechodzi przez
  `PY -I <ODB>\narzedzia\dowody_lf.py --katalog <DOW> --napraw --wynik <DOW>\dowody_lf.txt` (zamienia CRLF na LF i
  znaki spoza ASCII na ASCII, liczy zamiany; kod 0 = czysto; kod 1 = zostaly naruszenia albo plik zakazany: STL, baza,
  ZIP, zapis ruchu, plik > 1024 KB). Narzedzia tej paczki z opcja `--wynik` (T9, `dowody_lf.py`,
  `pytest_instalacja.py`) pisza od razu ASCII + LF.
- Ciezki krok tylko przez blokade (`wspolne.md`): `powershell -NoProfile -ExecutionPolicy Bypass -File
  <PC-katalog>\koordynator\narz\ciezki.ps1 -Kto <kod> [-Tor 2] -Polecenie "<linia cmd z cd /d i przekierowaniem>"`.
  Blok z wiecej niz jednym poleceniem zapisz jako plik `<ROB>\krok_<nazwa>.cmd` i podaj jego sciezke w `-Polecenie`.
  W pliku `.cmd` KAZDE wywolanie `Polecenie.cmd`, `Stanowisko.cmd`, `Samokontrola.cmd`, `zainstaluj.cmd`,
  `Wroc_do_poprzedniej.cmd`, `Wersje.cmd`, `py.cmd` poprzedz slowem `call` - bez `call` plik konczy sie po pierwszym
  skrypcie i dalsze polecenia NIE sa wykonane. Zaraz po kazdym: `echo <krok> KOD=%ERRORLEVEL% >> <ROB>\kody.txt`.
  Na poczatku pliku: `set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe` i
  `set QT_QPA_PLATFORM=offscreen`; wejscie kazdego polecenia `< NUL`. (Potkniecie D11 proby generalnej; kod wyjscia
  `ciezki.ps1` = kod pliku, gdy plik konczy sie `exit /b <kod>`. Bloki polecen w tym planie maja `call` wpisane tam,
  gdzie polecenie zaczyna wiersz; polecenia podane w tekscie krokow - T0, T12, T1, T7, T11 - przepisujac do pliku
  `.cmd` poprzedz `call` sam. W poleceniach planu `PY` i `%PY%` znacza to samo: zmienna z `set PY=...`.)
  Tor 2 = seria pomiarowa (T2, T4, T10, T11 - jedna naraz na calym PC). Wynik kazdego przebiegu dopisywac do pliku od
  razu (PC bywa restartowany). Od 20.11 22:35 `wspolne.md` ma 4 tory (numer przydziela koordynator) - seria pomiarowa
  nadal jedna naraz na calym PC, a czasy mierzone przy innych ciezkich krokach w toku trzeba opisac ("co jeszcze liczylo").

## Oznaczenia

| Znak | Znaczenie |
|---|---|
| `PY` | `<PC>\AppData\Local\Programs\Python\Python312\python.exe` (Python 3.12.10) |
| `<ZIP_N>`, `<ZIP_N1>` | paczki wydania `<PC-katalog>\wydania\Stanowisko_<N>.zip` i `Stanowisko_<N+1>.zip` (buduje koordynator, p. "Krok wspolny") |
| `<P1>`, `<P2>` | rozpakowane paczki: `<PC-katalog>\t0\paczka_N`, `<PC-katalog>\t0\paczka_N1` |
| `<K>` | katalog instalacji z paczki: `<PC-katalog>\t0\<nazwa>` (T0: `czysta`; kazdy wykonawca ma wlasny: `w1`, `w2`, `w3`) |
| `<DANE>` | `<K>\dane` (baza `stanowisko.sqlite`, `logi\stanowisko.log`, `wyniki\`, `log_excel.csv`, kopie bazy `kopie\`) - sprawdzone w `instalator.py` galezi `e3/a11i` (dane poza katalogiem wersji; sciezki bezwzgledne w `<K>\ustawienia.toml`, sekcja `[sciezki]`) |
| `<REPO>` | czysta kopia `main` z TEGO SAMEGO commita, z ktorego zbudowano `<ZIP_N>`: `<PC-katalog>\t0\repo` (zaklada koordynator: `git clone --no-checkout -c core.autocrlf=false <PC-katalog>\qc <PC-katalog>\t0\repo` + `git -C <PC-katalog>\t0\repo checkout --detach <commit>` - wykonane w probie generalnej 21.11, 4,5 s, repo glowne bez zmian. `<REPO>` MUSI miec konce linii LF: systemowy git na PC ma `core.autocrlf=true`, klon BEZ `-c core.autocrlf=false` dostaje CRLF i testy czytajace bajty plikow padaja - kontrola przed T1: `git -C <REPO> config --get core.autocrlf` ma wypisac `false`. `git worktree add` dziedziczy ustawienie repo, ale nie byl probowany) |
| `<ST>` | `<REPO>\Ramki\stanowisko` |
| `<ODB>` | `<REPO>\Ramki\etap3\odbior_koncowy` (skrypty: `<ODB>\narzedzia\`) |
| `<DOW>` | katalog dowodow testu: w trakcie testow `<ROB>` (poza repo), po komplecie `Ramki\etap3\odbior_koncowy\dowody\T<nr>\` |
| `<ROB>` | katalog roboczy poza repo: `<PC-katalog>\koordynator\robocze\odbior\T<nr>\` |
| `POL` | `<K>\Polecenie.cmd` = Python wersji biezacej uruchomiony w `<K>\wersje\<wersja>\program` (sa tam `stanowisko\`, `narzedzia\`, `ramka\`, `modele_plytek\`; NIE ma `testy\`) |

Ktore testy ida na instalacji z paczki, a ktore wymagaja repo:

| Test | Instalacja z paczki (`<K>`) | Repo (`<REPO>`) |
|---|---|---|
| T0, T12 | tak (to jest przedmiot testu) | nie |
| T1 | interpreter i pakiety z `<K>` (`zainstaluj.cmd /testy`) | testy i kod z `<REPO>` |
| T2 | sterownik `POL <ODB>\narzedzia\t2_wieczor.py` (program + symulator w jednym przebiegu) | skrypt i scenariusz z `<ODB>`; testy uzupelniajace |
| T11 | program przez `Stanowisko.cmd`, symulator przez `POL` | tylko testy uzupelniajace |
| T4, T10 | narzedzia pomiarowe przez `POL narzedzia\...` | nie |
| T3 | sterownik `POL <ODB>\narzedzia\t3_poranek.py` (program z `<K>`) | skrypt z `<ODB>`, dane i tabela SE10 z `<ST>\testy` |
| T5, T6, T7 | interpreter I KOD PROGRAMU z `<K>` (`POL <ODB>\narzedzia\pytest_instalacja.py`) | testy z `<REPO>`, skrypt z `<ODB>` |
| T8 | `POL narzedzia\raport_metryk.py` | skrypt `sql_odczyt.py` z `<ODB>` |
| T9 | cele: `<DANE>`, logi, dowody | repo jako cel, skrypt z `<ODB>` |
| T13 | nie | tak (`git`, skrypt z `<ODB>`) |

## Krok wspolny (koordynator, przed T0): paczki wydania

Zrodlo: raport `Ramki/stanowisko/raporty/E3-A11i_2026-11-20.md`, p. 12.8 (galaz `e3/a11i`).

```
cd /d <PC-katalog>\qc\Ramki\stanowisko
call <PC-katalog>\koordynator\narz\py.cmd narzedzia\zbuduj_wydanie.py --wyjscie <PC-katalog>\wydania --kola <PC-katalog>\wydania\kola
call <PC-katalog>\koordynator\narz\py.cmd narzedzia\zbuduj_wydanie.py --wyjscie <PC-katalog>\wydania --kola <PC-katalog>\wydania\kola --wersja <N+1>
```

- Wynik: `Stanowisko_<N>.zip` + `.zip.sha256` (suma takze w ostatnim wierszu wyjscia). `<N>` = tresc pliku
  `Ramki/stanowisko/WERSJA` (na galezi `e3/a11i`: `0.3.1`). Budowa bierze commit `HEAD`, nie katalog roboczy; ok. 6-15 s;
  bez internetu (76 kol w `<PC-katalog>\wydania\kola`).
- Po budowie: wiersz `<sha256>  Stanowisko_<N>.zip` do `Ramki/etap3/wydania/SHA256SUMS_wydania.txt`, wiersz w
  `Ramki/etap3/wydania/README.md`, zwiekszenie `WERSJA` (inaczej pada `test_numer_wersji_i_lista_wydan`).
- Stara `<PC-katalog>\wydania\Stanowisko_0.3.0.zip` (runda 1, bez samokontroli) jest nieinstalowalna - nie uzywac.
- Do `RAPORT.md`: numer wersji, SHA-256, commit, rozmiar, liczba plikow.

Przygotowanie instalacji roboczej wykonawcy (`w1`, `w2`, `w3`) = kroki 1-5 z T0 w katalogu `<PC-katalog>\t0\<nazwa>`,
z opcja `/testy` (doinstalowuje pytest z `kola_testy`), bez zapisu dowodow. Ustawienia `[sciezki]` w `<K>\ustawienia.toml`:

```
folder_eksportu_skanera = "<PC-katalog>/t0/<nazwa>_wej/eksport"
folder_cyrkon = "<PC-katalog>/t0/<nazwa>_wej/Cyrkon"        # kopia <PC-katalog>\app\Prace_test (15 folderow, 17 STL)
folder_prywatne = "<PC-katalog>/t0/<nazwa>_wej/Prywatne"    # pusty
folder_millbox = "<PC-katalog>/t0/<nazwa>_wej/millbox"      # pusty (pula_wpisow = false)
```

Kopie robi sie poleceniem `robocopy <zrodlo> <cel> /E` (zrodla tylko do odczytu). `[sesja] operatorzy = ["Technik A"]`.

---

## T0 - Czysta instalacja

**Kryterium (plan):** paczka wydania na czystym koncie PC, wg instrukcji, bez internetu - program startuje;
samokontrola zielona; sumy SHA-256 zgodne.

**Gdzie:** instalacja z paczki. **Dane:** `<ZIP_N>` i `<ZIP_N>.sha256`; instrukcja
`Ramki/stanowisko/instrukcje/instalacja_i_aktualizacja.md` (po scaleniu A11i; w paczce `program\instrukcje\`).

**Przyjeta interpretacja (odstepstwo O1):** "czyste konto PC" = swiezy, pusty katalog `<PC-katalog>\t0\czysta` na koncie
`<konto-PC>` (nowego konta Windows nie da sie zalozyc bez administratora); "bez internetu" = instalator ZAWSZE
instaluje pakiety tylko z kol paczki (pip `--no-index` - takze bez opcji `/bez-sieci`; ta opcja wylacza jedynie probe
polaczenia samokontroli z ramkami - stwierdzone w probie generalnej 21.11) - fizycznie sieci nie odcinamy. Pelne T0 na
czystym komputerze = laptop stanowiska (`ODLOZONE.md`, D4).

**Kroki** (okno `cmd.exe`; kazdy krok z przekierowaniem do `<ROB>\t0_<nr>.log`; kody wyjscia zapisz `echo KOD=%errorlevel%`):

1. `<PC-katalog>\koordynator\narz\ram.cmd` - zapisz wolny RAM. Krok 3 jest ciezki: uruchom go przez `ciezki.ps1` (tor 1).
2. Sumy paczki: `certutil -hashfile <ZIP_N> SHA256` - porownaj z `<ZIP_N>.sha256` i z wierszem w
   `SHA256SUMS_wydania.txt`. Rozpakuj:
   `powershell -NoProfile -Command "Expand-Archive -LiteralPath <ZIP_N> -DestinationPath <PC-katalog>\t0\paczka_N"`.
3. `<P1>\zainstaluj.cmd /katalog <PC-katalog>\t0\czysta /python %PY% /bez-sieci /bez-pauzy`
   Oczekiwane: **kod 10** ("WSTRZYMANA": wersja zainstalowana, samokontrola czeka na foldery w `ustawienia.toml`);
   na ekranie sumy "zgodne 210 z 210" (paczka z f5c3e01: program 131 plikow, kola 73, kola testowe 3; liczba moze byc
   inna - zapisz) i pakiety "73 z 73". Czas: 52,5 s w probie generalnej (PC malo obciazony), do 210 s pod obciazeniem.
4. Wpisz foldery w `<K>\ustawienia.toml` (jak w "Krok wspolny"; katalogi musza istniec).
5. Ponownie krok 3. Oczekiwane: **kod 0**, "juz zainstalowana i zgodna", samokontrola ZIELONA. Czas 6-15 s.
6. `<K>\Samokontrola.cmd --bez-sieci` - oczekiwane: kod 0, wiersz podsumowania "ZIELONA" z licznikami (ok / ostrzezenia /
   bledy = n / m / 0). Kody: 0 zielona, 1 bledy, 2 nie dalo sie wykonac. Zapisz tez wersje JSON:
   `<K>\Samokontrola.cmd --bez-sieci --json > <ROB>\t0_samokontrola.json` (wzor `Samokontrola.cmd` przekazuje opcje
   dalej - `%*` - i sam dodaje `--ustawienia` oraz `--sumy`; sprawdzone w pliku wzoru na galezi `e3/a11i`).
7. Start programu: `set QT_QPA_PLATFORM=offscreen` i `<K>\Stanowisko.cmd --atrapa --zamknij-po 5` (kod 0), potem
   `<K>\Stanowisko.cmd --zamknij-po 20` (prawdziwy kontroler, kod 0). W `<DANE>\logi\stanowisko.log` 0 wierszy `Traceback`.
8. Kontrola srodowiska wersji (latka A11w): `<K>\Polecenie.cmd -c "import stanowisko, sys; print(sys.modules.get('_wmi', 'brak'))"`
   ma wypisac `None`.
9. Kontrola "bez internetu": `findstr /c:"Ignoring indexes" /c:"Looking in links" <K>\wersje\<N>\pip.log` ma dac 2 wiersze
   (`Ignoring indexes: https://pypi.org/simple` = dowod `--no-index`, NIE siegniecie do sieci; `Looking in links: ...\kola`),
   a w `<K>\dziennik_instalacji.txt` jest wiersz "instalacja 73 pakietow z kol paczki (bez sieci)". (Poprzednia postac
   kroku - `findstr /i "pypi https://"` na logu ekranu - dawala 0 wierszy, ale ekran nie pokazuje adresow, wiec niczego
   nie dowodzila; na `pip.log` daje 1 wiersz, ktory nie jest naruszeniem.)

**Liczby kryterium:** (a) program startuje = kody 0 w kroku 7 (2 z 2; liczy sie przede wszystkim start BEZ `--atrapa` -
`--atrapa` to pokaz okna na danych sztucznych, bez kontrolera, bazy, silnika i blokady); (b) samokontrola = kod 0 i "bledy 0" w kroku 6;
(c) sumy = zgodnosc SHA-256 ZIP w kroku 2 (1 z 1) + licznik "sumy n z n" instalatora w kroku 3.

**Dowody w `T0/`:** `t0_kroki.md` (tabela krok / polecenie / kod / czas / wynik), `t0_sha256.txt`, `t0_zainstaluj_1.log`,
`t0_zainstaluj_2.log`, `t0_samokontrola.txt`, `t0_samokontrola.json`, `t0_start.txt`.

**Czas:** 20 min. **Ciezar:** ciezki (krok 3; tor 1). **Rownolegle:** nie z T1 i T12 (ten sam tor); z lekkimi tak.

**Pulapki:** opcja `/python %PY%` jest na tym PC OBOWIAZKOWA w kazdym wywolaniu `zainstaluj.cmd` (bez niej kod 4:
Python 3.12 lezy w profilu innego konta); `Samokontrola.cmd` BEZ argumentow czeka na klawisz - zawsze podawaj opcje
(`--bez-sieci`) albo `< NUL`; `zainstaluj.cmd` bez `/bez-pauzy` czeka na klawisz; kod 10 przy pierwszej instalacji to wynik poprawny
(decyzja koordynatora 20.11 nr 1), nie FAIL; sesja bez ekranu wymaga `QT_QPA_PLATFORM=offscreen`; brak folderu MillBox i
ramek = OSTRZEZENIE, nie blad; kod 5 = program juz dziala albo baza zajeta (zamknij inne instalacje w tym samym `<K>`).

## T12 - Aktualizacja

**Kryterium (plan):** wersja N -> N+1 -> powrot do N - jedno polecenie; ustawienia zachowane; baza zmigrowana z kopia.

**Gdzie:** instalacja z paczki, katalog `<K>` = `<PC-katalog>\t0\czysta` po T0 (z baza po co najmniej jednym starcie
programu). **Dane:** `<ZIP_N1>`; do czesci B paczka z probna migracja (nizej).

**Kroki:**

1. Przed: `certutil -hashfile <K>\ustawienia.toml SHA256` -> `t12_ustawienia_przed.txt`; `<K>\Wersje.cmd /bez-pauzy` -> lista
   wersji; `PY -I <ODB>\narzedzia\sql_odczyt.py --baza <DANE>\stanowisko.sqlite "SELECT count(*) FROM skany"`.
   Uwaga: suma SHA-256 pliku bazy zmienia sie po KAZDYM starcie programu (zdarzenia startu) - "dane nietkniete" licz
   zapytaniami `count(*)` (na instalacji swiezej po T0 liczba skanow = 0, dlatego licz takze
   `"SELECT count(*) FROM zdarzenia"`), a sume bazy porownuj tylko miedzy "przed aktualizacja" a kopia obok bazy.
   Wersja doinstalowana aktualizacja (N+1) nie ma pytest, dopoki jej `zainstaluj.cmd` nie dostal `/testy` - T12 rob na
   instalacji, na ktorej nie biegna juz testy wymagajace pytest, albo dodaj `/testy` w kroku 2.
2. Rozpakuj `<ZIP_N1>` do `<P2>`. Aktualizacja jednym poleceniem (tor 1):
   `<P2>\zainstaluj.cmd /katalog <K> /python %PY% /bez-sieci /bez-pauzy` - oczekiwane kod 0, `wersja_biezaca.txt` = N+1.
3. `<K>\Samokontrola.cmd --bez-sieci` (kod 0); `<K>\Stanowisko.cmd --zamknij-po 20` (kod 0); suma `ustawienia.toml` =
   suma z kroku 1.
4. Powrot jednym poleceniem: `<K>\Wroc_do_poprzedniej.cmd /tak /bez-pauzy` - oczekiwane kod 0, `wersja_biezaca.txt` = N.
   Kod 8 = baza nowsza niz poprzednia wersja: wtedy `<K>\Wroc_do_poprzedniej.cmd /przywroc-kopie /bez-pauzy` (to jest
   drugie polecenie - zapisz to jako fakt, patrz czesc B).
5. Po powrocie: `Samokontrola.cmd --bez-sieci` (kod 0), `Stanowisko.cmd --zamknij-po 20` (kod 0), suma ustawien bez
   zmian, liczba skanow w bazie = liczba z kroku 1, `<K>\Wersje.cmd /bez-pauzy`.

**Czesc B - "baza zmigrowana z kopia" (odstepstwo O2):** schemat bazy miedzy wydaniami N i N+1 jest ten sam
(`WERSJA_SCHEMATU` = 1 w calym etapie 3), wiec zwykla aktualizacja niczego nie migruje. Migracje sprawdza sie na paczce
PROBNEJ: kopia drzewa programu z `<REPO>` z `WERSJA_SCHEMATU` + 1 i dodatkowa pozycja `MIGRACJE[2]` (pusta tabela
`proba_migracji_odbior`). Paczke buduje `<ODB>\narzedzia\t12_paczka_migracja.py` (repo zostaje bez zmian - skrypt
porownuje `git status --short` przed i po; gdy wiersze `WERSJA_SCHEMATU` / `MIGRACJE` w `baza.py` nie pasuja do wzorca
dokladnie 1 raz: kod 2 i brak paczki = czesc B "NIE ZMIERZONO"). Paczki probnej NIE publikowac i nie wpisywac do
`SHA256SUMS_wydania.txt`.

Oznaczenia czesci B: `<ROB>` = `<PC-katalog>\koordynator\robocze\odbior\T12` (bez katalogu `drzewo_M`), `<KB>` =
`<ROB>\K_B` (OSOBNA instalacja - nie `<K>` z czesci A), `<PM>` = `<ROB>\paczka_M`, `<M>` = numer paczki probnej
`0.3.9-migracja` (dowolny numer wiekszy od N, ktorego nie ma w `<KB>\wersje`), `<P1>` = rozpakowana paczka wersji N.
Wszystkie polecenia w jednym oknie `cmd`, z wejsciem `< NUL`, po `set QT_QPA_PLATFORM=offscreen`; calosc jako jeden
plik `.cmd` pod blokada (tor 1) - w pliku KAZDE `zainstaluj.cmd`, `Stanowisko.cmd`, `Wroc_do_poprzedniej.cmd` z `call`
i z `echo <krok> KOD=%ERRORLEVEL% >> <ROB>\kody.txt` zaraz po nim (bez `call` wykona sie tylko krok 2 - "Zasady
wykonania"). Odczyt bazy (bez nazw): `PY -I <ODB>\narzedzia\sql_odczyt.py --baza
<KB>\dane\stanowisko.sqlite "SELECT count(*) FROM zdarzenia"` i `"SELECT user_version FROM pragma_user_version"`;
sumy: `certutil -hashfile <plik> SHA256`.

Kroki (polecenia wykonane 21.11.2026 na commicie f5c3e0182533, wyniki w nawiasach):

1. Budowa paczki probnej (kod 0; 6 s + 3 s rozpakowanie; ZIP 444 935 009 B, 210 plikow + SHA256SUMS):
   `PY -I <ODB>\narzedzia\t12_paczka_migracja.py --repo <REPO> --roboczy <ROB> --wersja 0.3.9-migracja --wyjscie <ROB>\paczki --kola <PC-katalog>\wydania\kola`
   - wypisuje commit, "schemat bazy w kopii: 1 -> 2", sciezke ZIP i SHA-256 (zapisz), "repo zrodlowe bez zmian".
   `powershell -NoProfile -Command "Expand-Archive -LiteralPath <ROB>\paczki\Stanowisko_0.3.9-migracja.zip -DestinationPath <PM>"`
2. Instalacja wersji N w nowym katalogu:
   `<P1>\zainstaluj.cmd /katalog <KB> /python %PY% /bez-sieci /bez-pauzy` - oczekiwany kod 10 (brak folderow);
   wpisz w `<KB>\ustawienia.toml` 4 foldery `[sciezki]` (wlasne puste katalogi `<ROB>\wej\eksport`, `Cyrkon`,
   `Prywatne`, `millbox`, ukosniki `/`) i `operatorzy = ["Technik A"]`; to samo polecenie ponownie - kod 0.
3. Baza z wpisami: `<KB>\Stanowisko.cmd --zamknij-po 5` dwa razy (kod 0, 0). Zapisz stan "przed": SHA-256 bazy,
   `user_version` (bylo 1), liczba zdarzen (bylo 4), liczba plikow w `<KB>\dane\kopie` (bylo 0), a dla pliku bazy
   takze rozmiar i skrot tresci bez naglowka:
   `PY -I -c "import hashlib,sys;d=open(sys.argv[1],'rb').read();print(len(d),hashlib.sha256(d[100:]).hexdigest())" <KB>\dane\stanowisko.sqlite`
4. Aktualizacja paczka probna: `<PM>\zainstaluj.cmd /katalog <KB> /python %PY% /bez-sieci /bez-pauzy` - kod 0.
   Kontrola c1: w `<KB>\dane\kopie` 1 nowy plik `stanowisko_przed_<M>_<data>_v1.sqlite`; baza jeszcze bez zmian (SHA-256
   jak w kroku 3). Kopia ma rozmiar bazy z kroku 3 i ten sam skrot tresci bez naglowka (to samo polecenie `PY -I -c` na
   pliku kopii), `user_version` i liczbe zdarzen jak w kroku 3. UWAGA: SHA-256 CALEGO pliku kopii NIE jest rowne sumie
   pliku bazy (zmierzone: 0 z 2 prob) - pliki roznia sie tylko w pierwszych 100 bajtach (naglowek SQLite), rozmiar
   86 016 B i bajty od 100. sa identyczne, skrot zrzutu SQL identyczny (sprawdzone w 1 z 2 prob; w drugiej po
   przywroceniu kopii `user_version` i liczba zdarzen byly jak przed aktualizacja).
   Porownanie `certutil` calych plikow da wiec "rozne" - to nie jest FAIL; ocenia sie skrot bez naglowka.
5. Pierwsze uruchomienie wersji probnej (program migruje): `<KB>\Stanowisko.cmd --zamknij-po 5` - kod 0.
   Kontrola c2: `user_version` 1 -> 2; liczba zdarzen rosnie (bylo 4 -> 7); w `<KB>\dane\kopie` nadal 1 plik.
6. Powrot bez zgody na przywrocenie kopii: `<KB>\Wroc_do_poprzedniej.cmd /tak /bez-pauzy` - oczekiwany kod 8
   ("baza nowsza niz poprzednia wersja"); wersja biezaca i baza bez zmian (SHA-256 jak po kroku 5).
7. Powrot z przywroceniem kopii: `<KB>\Wroc_do_poprzedniej.cmd /przywroc-kopie /bez-pauzy` - kod 0; wersja biezaca
   = N. Kontrola e: SHA-256 pliku bazy = SHA-256 pliku kopii z kroku 4 (tu porownanie calych plikow jest
   rowne: tak, 1 z 1), `user_version` = 1, liczba zdarzen = 4 (jak w kroku 3; 3 wpisy dopisane przez wersje probna
   przepadly), baza zmigrowana odlozona jako `dane\kopie\stanowisko_odlozona_v2_<data>.sqlite` (2 pliki w `kopie`).
8. `<KB>\Stanowisko.cmd --zamknij-po 5` - kod 0 (wersja N dziala na przywroconej bazie).

**Liczby kryterium czesci B:** kody 9 polecen programu = 10, 0, 0, 0, 0, 0, 8, 0, 0 (kolejno kroki 2-8; zmierzone 9 z 9
zgodnych, razem z 2 poleceniami kroku 1: 11 z 11); kopia sprzed migracji: 1 plik w `<KB>\dane\kopie` o rozmiarze i
skrocie tresci bez naglowka rownym bazie z kroku 3 (NIE suma calego pliku - patrz kontrola c1); `user_version` po
kroku 5 wieksze niz w kroku 3 i po kroku 7 rowne wartosci z kroku 3; SHA-256 bazy po kroku 7 = suma kopii;
liczba zdarzen po kroku 7 = liczba z kopii (wpisy dopisane przez wersje probna miedzy krokiem 5 a 7 przepadaja -
podaj ile).

**Regula wyniku:** "jedno polecenie" ocenia czesc A (aktualizacja i powrot bez zmiany schematu: po 1 wywolaniu, kod 0).
W czesci B powrot po migracji wymaga 2 polecen (kod 8, potem `/przywroc-kopie`) - to zachowanie zamierzone programu
(nie przywraca kopii bez zgody). Wynik czesci B: "baza zmigrowana z kopia: ZAL / FAIL" wg liczb wyzej, a "powrot po
migracji = 2 polecenia" wpisz do `RAPORT.md` jako pozycje do decyzji wlasciciela - nie FAIL i nie ciche ZAL. Kod inny
niz oczekiwany w ktorymkolwiek kroku = FAIL czesci B (zapisz fakt i log, programu nie poprawiaj).

**Dowody czesci B w `T12/`:** `t12_migracja_B.md` (tabela: krok, polecenie, kod, czas, ostatnie wiersze + stany bazy),
`t12_B_paczka.txt` (wyjscie kroku 1), logi krokow 2-8 (`t12_B_<nr>.log`, tylko wyjscie instalatora / programu).

**Czas czesci B:** zmierzone 2 min 45 s samych polecen (instalacje 63 s i 56 s, budowa paczki 6 s); z zapisem
dowodow 15 min (ciezki, tor 1). **Pulapki:** `--roboczy` nie moze zawierac `drzewo_M` (kod 2 - usun albo
podaj nowy katalog); kopia bazy nie jest bajtowo rowna plikowi bazy (naglowek) - porownuj skrot bez naglowka;
kazde `Wroc_do_poprzedniej.cmd /tak` z N do wersji probnej robi kolejna kopie (zmierzone: +1 plik) - licz pliki
w `kopie` po kazdym kroku; `<KB>` po probie nie nadaje sie do innych testow;
`--wyjscie` i `--roboczy` poza repo; paczka probna ma ok. 424 MB (nie do gita); nie instaluj
paczki probnej w `<K>` z czesci A ani w instalacjach roboczych (baza zostalaby zmigrowana); numer wersji probnej
rozny od N i N+1 tez wielkoscia liter; folderow danych innych wykonawcow nie wpisuj do `<KB>\ustawienia.toml`.

**Liczby kryterium:** jedno polecenie = 1 wywolanie `zainstaluj.cmd` (kod 0) i 1 wywolanie `Wroc_do_poprzedniej.cmd`
(kod 0) w czesci A - to czesc A ocenia "jedno polecenie". Powrot po migracji bazy (czesc B) wymaga 2 polecen (kod 8, potem
`/przywroc-kopie`): to NIE jest FAIL i NIE jest ciche ZAL - wynik T12 = "ZAL z odstepstwem O2" i pozycja na liscie decyzji
wlasciciela w `RAPORT.md` (czy powrot po migracji w 2 poleceniach jest do przyjecia); ustawienia = 3 sumy SHA-256 identyczne (przed / po N+1 / po powrocie);
baza = kopia istnieje i ma rozmiar oraz skrot tresci bez naglowka rowny bazie sprzed migracji (czesc B - suma CALEGO
pliku kopii rozni sie od sumy pliku bazy naglowkiem SQLite, zmierzone 21.11), liczba skanow bez zmian (czesc A).

**Dowody w `T12/`:** `t12_kroki.md`, `t12_ustawienia_sumy.txt`, `t12_wersje_przed_po.txt`, `t12_zainstaluj_N1.log`,
`t12_wroc.log`, `t12_migracja_B.md`.

**Czas:** 30 min (czesc A 15 - same polecenia 2 min 40 s w probie generalnej; czesc B 15 - same polecenia 2 min 45 s). **Ciezar:** ciezki (tor 1). **Rownolegle:** nie z T0 i T1; po T0, przed
uzyciem `czysta` do czegokolwiek innego.

**Pulapki:** `Wroc_do_poprzedniej.cmd` bez `/tak` pyta T / N (kod 11 = anulowany); kod 5 = program dziala; stare wersje
i kopie bazy nie sa kasowane (1,4 GB na wersje - po tescie zostawic, sprzata koordynator).

## T1 - Testy programu

**Kryterium (plan):** pytest caly - 0 failed, 0 errors; pominiete tylko znane z punktu odniesienia.

**Gdzie:** interpreter i pakiety srodowiska wersji (`<K>` zainstalowane z `/testy`), testy i kod z `<REPO>` (ten sam
commit co paczka). Zrodlo polecenia: raport `E3-A11w_2026-11-20.md`, p. 7.

**Kroki:**

1. `<P1>\zainstaluj.cmd /katalog <K> /python %PY% /bez-sieci /bez-pauzy /testy` (kod 0).
2. Kontrola koncow linii `<REPO>` (potkniecie B2 proby generalnej): `git -C <REPO> config --get core.autocrlf` ma
   wypisac `false`, a `git -C <REPO> status --short` ma byc puste - inaczej T1 nie startuje (zaloz `<REPO>` od nowa,
   patrz "Oznaczenia"). Potem `copy <ST>\ustawienia.przyklad.toml <ST>\ustawienia.toml` (plik ignorowany przez git).
3. `<K>\Polecenie.cmd -c "import stanowisko, sys; print(sys.modules.get('_wmi', 'brak'))"` -> `None`.
4. Przez `ciezki.ps1` (tor 1), jedna linia:
   `<K>\Polecenie.cmd -X faulthandler -m pytest <ST>\testy -q -rs -p no:cacheprovider --rootdir <ST> -o faulthandler_timeout=900 < NUL > <ROB>\t1_pytest.log 2>&1`
5. Drugi przebieg interpreterem bazowym (porownanie z punktem odniesienia, ta sama blokada):
   `cmd /c "cd /d <ST> && <PC-katalog>\koordynator\narz\py.cmd -m pytest -q -p no:cacheprovider -rs > <ROB>\t1_pytest_bazowy.log 2>&1"`

**Liczby kryterium:** wiersz podsumowania pytest w logu (`... N passed, S skipped ... in ...s`; `failed` i `error` maja
nie wystapic) ORAZ osobno kod wyjscia procesu - oba do `t1_wynik.md`. Brak wiersza podsumowania = NIE ZMIERZONO
(powtorz przebieg). Kod 1 i `failed` w podsumowaniu = FAIL. Kod 0xC0000409 (-1073740791) PO wierszu podsumowania bez
`failed` / `error` = znane zjawisko zamykania interpretera z Qt (raport E3-A11w): wynik liczy sie z wiersza
podsumowania, kod wpisz jako uwage. Suma passed + skipped + failed = liczba z `--collect-only`. Pominiete: lista
z `-rs` (jest w obu poleceniach) porownana z punktem odniesienia: `main` bf00921 = 1829 / 9 / 0
(`<PC-katalog>\koordynator\log\pytest_bazowy_bf00921.log`), `main` 9ba9e91 = 1831 / 9 / 0. Oczekiwana liczba testow =
wynik `--collect-only` na commicie wydania (oczekiwana ok. 2222, w tym 9 pominietych: pelny pytest interpreterem
bazowym na galezi `e3/p15` po rundzie 2 = 2213 passed / 9 skipped; na f5c3e01 bylo 2212, w tym 9 pominietych). Liczba
testow NIE jest kryterium - kryterium to 0 failed, 0 errors i pominiete tylko znane z punktu odniesienia;
kazdy pominiety test spoza listy 9 znanych = FAIL kryterium.

**Stwierdzone w probie generalnej 21.11 na instalacji z paczki (f5c3e01):** (a) `--collect-only` dawal 2212 testow -
liczbe oczekiwana ustal przed odbiorem poleceniem
`<K>\Polecenie.cmd -m pytest <ST>\testy -q --collect-only -p no:cacheprovider --rootdir <ST>` na commicie wydania
(interpreter bazowy i wersji maja dac te sama); (b) `test_aplikacja.py::test_b1_blokada_znika_razem_z_procesem` PADAL w
srodowisku wersji zawsze (6 z 6 uruchomien osobnych; interpreterem bazowym 2 z 2 passed) - wlasnosc testu w `venv`
(`sys.executable` to posrednik; blokada bazy zwalnia sie kilka ms po `wait()`), nie blad programu. Paczka E3-P15
(runda 2) dopasowala ten test do srodowiska wersji - po scaleniu P15 oczekiwane w T1 jest 0 failed takze interpreterem
wersji. Gdyby test (albo inny) nadal padal na commicie wydania: wynik T1 = FAIL z ta liczba (bez oslabiania), a decyzja
o poprawce testu albo odstepstwie nalezy do koordynatora / wlasciciela.
Polecenie odtworzenia (2,5 s):
`<K>\Polecenie.cmd -m pytest <ST>\testy\test_aplikacja.py -q -p no:cacheprovider --rootdir <ST> -k test_b1_blokada_znika_razem_z_procesem`.
(c) Wiersze `PASSED` / `FAILED` z `-rA` maja sciezki wzgledem katalogu programu wersji (`..\..\..\..\repo\Ramki\...`) -
licz przez `findstr /b PASSED`, nie przez szukanie `testy\test_` na poczatku wiersza.

**Dowody w `T1/`:** `t1_pytest.log`, `t1_pytest_bazowy.log`, `t1_collect.txt` (ostatni wiersz `--collect-only`),
`t1_pominiete.txt` (9 pozycji z powodem), `t1_wynik.md` (wiersz podsumowania i OSOBNO kod wyjscia kazdego przebiegu,
passed / skipped / failed, liczba z `--collect-only`, czas, commit, wynik kontroli `core.autocrlf`, wolny RAM przed
startem).

**Czas:** 30-45 min na przebieg (interpreter bazowy ok. 20-29 min). **Ciezar:** ciezki (tor 1). **Rownolegle:** nie.

**Pulapki:** bez `--rootdir` pytest bierze za katalog glowny `<PC-katalog>` (zle identyfikatory, `-k` lapie nazwy
katalogow); testy importuja pakiet `stanowisko` z `<REPO>`, nie z `<K>` - dlatego ten sam commit; zawieszenie oceniac po
stanie procesu, nie po zegarze (pod obciazeniem `test_silnik.py` trwa ponad 8 min); zjawisko PC `0xC0000142` /
`0xc000070a` = opisac i powtorzyc przebieg (oba logi zostaja); testy czasowe wrazliwe na obciazenie: `test_ramka::test_k4`,
`test_ui_wieczor::test_6`, `test_aplikacja::test_f` (raport E3-T0p). Caly pytest w srodowisku wersji: proba generalna
21.11 - 2202 passed / 9 skipped / 1 failed, 27 min 20 s, kod 1. `<REPO>` z koncami CRLF (klon bez
`-c core.autocrlf=false`) daje falszywe `failed` w testach czytajacych bajty plikow - kontrola w kroku 2.

## T2 - Wieczor od poczatku do konca

**Kryterium (plan):** symulator wrzuca 10 plytek co 60 s: uklady R59 i R54, okragle, 1 niezgodny uklad, 1 drgniecie,
1 plik uciety - 10 z 10 obsluzonych zgodnie z prawda; start analizy ponizej 1 s od zapisu; mapa do 40 s (mediana); okno
bez przerw ponad 200 ms; lista "do dofrezowania" = prawda.

**Gdzie:** program z paczki, prowadzony sterownikiem `<ODB>\narzedzia\t2_wieczor.py` (decyzja koordynatora 20.11 nr 1 -
brak B1 usuniety; kryterium mierzone na programie z paczki, nie testami jednostkowymi). Sterownik uruchamia PRAWDZIWY
program (`stanowisko.aplikacja.main` - ta sama funkcja, ktora wola `Stanowisko.cmd`; prawdziwy obserwator folderu,
prawdziwy proces silnika, prawdziwe okno), podaje pliki symulatorem skanera programu (`narzedzia\symulator_skanera.py`,
osobny proces, `--rownolegle 1`, `--zle uciety`) wg tabeli prawdy `narzedzia\t2_scenariusz.json`, a decyzje technika
wykonuje KLIKNIECIAMI w oknie po nazwach obiektow (`osoba_0`, kafelek `plytka_<id>`, gniazdo mapy, `przycisk_ukruszona`,
`przycisk_ok`, `odp_odrzuc_ponowny_skan`); polecen kontrolera nie wola, niczego w programie nie podmienia. Naglowek pliku sterownika
wymienia wszystkie miejsca, w ktorych sterownik czyta stan programu (`kontroler.stan()`, `okno.pokazana_plytka()`, baza i
log po zamknieciu - tylko odczyt).

**Odstepstwa (O3, O4 - wersja po decyzji nr 1):** (O3) program biegnie w procesie sterownika (zegar pomiaru i klikniecia
musza byc w watku okna), z opcja `--zamknij-po` jako bezpiecznikiem, a nie przez plik `Stanowisko.cmd`; interpreter,
katalog programu i plik ustawien sa te same, co w `Stanowisko.cmd` (uruchomienie przez `<K>\Polecenie.cmd`); program
dostaje KOPIE `<K>\ustawienia.toml` z sekcja `[sciezki]` przestawiona na katalog roboczy (pusta baza, pusta pamiec puli =
pula zimna, wlasny folder eksportu). (O4) okno `offscreen` (sesja bez ekranu) - platforma Qt jest w wyniku; zegar
sterownika w watku okna (co 20 ms: odczyt stanu, klikniecia) wlicza sie do przerw petli.

**Tabela prawdy (`t2_scenariusz.json`, 10 plikow; plytki wskazane przez katalog danych odniesienia, nazwe sztucznego skanu
z generatora i `sha16` pliku - sterownik sprawdza `sha16` przed startem):**

| Nr | Skad (`<PC-katalog>\app\dane_ref\...`) | Sklad wg kryterium | Oczekiwany stan | Jak powstaje plik |
|---|---|---|---|---|
| 1 | `syntetyczne_R59_P2`, wieczorna n1 | uklad R59, kwadratowa | `przyjety` + "Ukruszona" wg prawdy | plik danych odniesienia bez zmian (symulator kopiuje go w kawalkach do folderu eksportu) |
| 2 | `syntetyczne_R59_P2`, okragla wieczorna n8 | uklad R59, okragla | `przyjety` + "Ukruszona" | bez zmian |
| 3 | `syntetyczne_r54_P2`, wieczorna n3 | uklad R54, kwadratowa | `przyjety` + "Ukruszona" | bez zmian |
| 4 | `syntetyczne_r54_P2`, okragla wieczorna n8 | uklad R54, okragla | `przyjety` + "Ukruszona" | bez zmian |
| 5 | (plik nr 1) | 1 plik uciety | `plik_odrzucony`: brak plytki, 1 zdarzenie `plik_odrzucony` | robi symulator (`--zle uciety`): 60 % bajtow pierwszego pliku zrodlowego; miejsce w kolejce wyznacza symulator - sterownik bierze je z dziennika |
| 6 | `syntetyczne_R59_P2`, wieczorna n2 | 1 drgniecie (w prawdzie 1 praca z `drgniecie`) | `do_powtorzenia`, 0 zielonych | bez zmian |
| 7 | `syntetyczne_R59_P2`, wieczorna n3 | 1 niezgodny uklad | `niezgodny_uklad`, 0 zielonych | plik pochodny w `<ROB>\t2\zrodla\`: wspolrzedne X i Y wierzcholkow x 1,12 (rozstaw stozkow nie pasuje do zadnego ukladu) - robi sterownik |
| 8 | `syntetyczne_R59_P2`, wieczorna n2 | uklad R59, kwadratowa | `przyjety` + "Ukruszona" | bez zmian |
| 9 | `syntetyczne_R59_P2`, poranna n4 (0 drgniec w prawdzie) | plytka poranna wieczorem | `plytka_nie_z_trybu`, 0 zielonych, pytanie `plytka_nie_z_trybu` | bez zmian |
| 10 | `syntetyczne_r54_P2`, okragla wieczorna n8 | uklad R54, okragla | `przyjety` + "Ukruszona" | bez zmian |

Prawda kazdej plytki = plik `.json` obok skanu (`plytka`, `numer`, `prace[].gniazdo`, `prace[].ubytki`,
`prace[].drgniecie`). Skad prawda: plik zapisal generator skanow sztucznych w chwili tworzenia skanu (prace, gniazda i
ubytki, ktore generator wycial w siatce; zestawy raportu R59, pliki z 14.11.2026) - przed uruchomieniem programu i
niezaleznie od jego wyniku; sterownik niczego do prawdy nie dopisuje. W 6 plytkach przyjetych scenariusza prawda ma 26 prac
z ubytkiem (6 + 3 + 3 + 4 + 4 + 6 na 57 prac); kazda z nich ma co najmniej jeden ubytek oznaczony w prawdzie jako
wykrywalny i widoczny (sprawdzone 21.11: 0 z 26 bez takiego ubytku) - praca "przeoczona" nie bedzie wiec skutkiem
ubytku, ktorego w skanie nie widac.

**Decyzje technika i "lista = prawda" (decyzja koordynatora nr 1 po recenzji, uwaga 1):** sterownik nasladuje technika,
ktory oglada tylko to, co program mu wskazal. Po pojawieniu sie plytki przyjetej wybiera jej kafelek i czyta kolor
KAZDEJ pracy Z EKRANU (obraz mapy, piksel gniazda; klasa koloru wg tabeli statusow programu) - przed jakimkolwiek
kliknieciem w te plytke; odczyt kazdej pracy jest w wyniku (`plytki[].kolory_prac_z_ekranu`). Potem:

- praca z ubytkiem wg prawdy pokazana na CZERWONO albo ZOLTO: klikniecie gniazda + "Ukruszona",
- praca z ubytkiem wg prawdy pokazana na ZIELONO (albo inaczej) = **przeoczona przez program**: sterownik jej NIE klika;
  pozycji nie ma wtedy na liscie programu, a werdykt "lista = prawda" to **FAIL** z licznikiem (n przeoczonych z m),
- praca cala wg prawdy pokazana na czerwono = falszywy alarm: klikniecie "OK" (licznik osobno; listy nie psuje),
- prac calych pokazanych na zolto sterownik nie klika (liczy je).

Oczekiwana lista "do dofrezowania" = WSZYSTKIE prace z ubytkiem w prawdzie plytek przyjetych (plytka, gniazdo) - nie
zalezy od tego, co sterownik kliknal. Ochrona klikniec mapy (mapa przygaszona ok. 800 ms po zmianie zawartosci albo po
zmianie komunikatow nad mapa - E3-P15): sterownik czeka na jej zdjecie, przed decyzja sprawdza, ze widok pracy pokazuje
wlasnie te prace, a klikniecie bez skutku ponawia od klikniecia gniazda; liczba ponowien i czekan jest w wyniku.
Wstrzykniecie 21.11 (kopia pliku prawdy: ubytek dopisany pracy, ktora program pokazuje na zielono; ubytek zdjety z pracy
czerwonej): nowy sterownik - lista FAIL (1 z 6 przeoczona), "OK" 1 z 1; sterownik sprzed poprawki - lista ZAL. Numery plytek w zestawie
powtarzaja sie (1, 2, 8) - na pytanie programu "to ponowny skan?" sterownik odpowiada "to nowy wsad"
(`odp_odrzuc_ponowny_skan`). Pytanie `plytka_nie_z_trybu` zostaje bez odpowiedzi (zapisane, ze sie pojawilo). Kopie i pliki
pochodne powstaja tylko w `<ROB>\t2` (poza repo). Projekty: `--projekty` = kopia `<PC-katalog>\app\Prace_test`.

**Kroki (tor pomiarowy, plik `.cmd` przez `ciezki.ps1` - z `call`, patrz "Zasady wykonania"; katalog `<ROB>\t2` nowy / pusty):**

```
set QT_QPA_PLATFORM=offscreen
call <K>\Polecenie.cmd <ODB>\narzedzia\t2_wieczor.py --ustawienia-wzor <K>\ustawienia.toml --roboczy <ROB>\t2 --projekty <folder_cyrkon> > <ROB>\t2_sterownik.log 2>&1
echo KOD=%ERRORLEVEL% >> <ROB>\kody.txt
```

- Domyslnie 10 plikow co 60 s (`--plytki 10 --odstep 60`); sterownik sam czeka na gotowa pule i silnik, startuje
  symulator, klika decyzje, zamyka program i liczy wynik. Czas: ok. 11-13 min (9 x 60 s miedzy startami plikow + start + ostatnia analiza);
  limit calosci domyslnie 10 x 60 + 1200 s = 30 min (`--limit`), po nim wynik czesciowy i kod 3.
- Kody: 0 = pomiar wykonany w calosci (werdykty sa w pliku wyniku - kod 0 NIE znaczy ZAL; z opcja `--wymagaj-zal` kod 1,
  gdy wiersz "T2 LACZNIE" nie jest ZAL), 2 = blad przygotowania (np.
  `sha16` skanu inne niz w scenariuszu, katalog roboczy niepusty), 3 = limit czasu (werdykty "mapa" i "okno" sa wtedy
  "NIE ZMIERZONO (pomiar przerwany; czesciowo: ...)"), 4 = program albo sterownik z bledem.
- Proba skrocona (nie jest wynikiem odbioru): `... --wybierz 2,4,5,7 --odstep 5` albo `--plytki 3`.
- Po przebiegu: `powershell Get-Process python` - nie ma procesow sterownika (PID-y w `<ROB>\t2\t2_pid.txt`); sterownik
  konczy symulator i proces silnika takze po bledzie i po limicie.

**Liczby kryterium (`<ROB>\t2\t2_wynik.json` i tabela `t2_wynik.txt`; sekcja `werdykty`):**

| Liczba | Pole | Jak mierzona |
|---|---|---|
| 10 z 10 zgodnie z prawda | `obsluzone_zgodnie_z_prawda`, wiersze `plytki[]` | status, uklad i numer plytki ze stanu programu wobec prawdy; nieprzyjete: 0 zielonych; uciety: brak plytki + 1 zdarzenie `plik_odrzucony` w bazie |
| start analizy < 1 s | `start_analizy_od_zapisu_s` (`ponizej_1_s`, `max`, `wartosci`) | DOSLOWNIE: `analiza.od` ze stanu programu (czas zdarzenia "start" procesu silnika) minus koniec zapisu pliku z dziennika symulatora; liczone dla wszystkich 9 plikow dobrych; pliki zapisane, gdy program liczyl poprzednia plytke, sa wskazane osobno (`czekaly_w_kolejce`) - to przyczyna, nie wylaczenie z kryterium |
| mapa do 40 s (mediana) | `mapa_od_zapisu_s` (`mediana`, `max`, `pierwsza_plytka`, `kolejne`, `do_40_s`, `w_oknie`) | GORNE OGRANICZENIE: pierwszy odczyt plytki w stanie programu (zegar co 20 ms w watku okna) minus koniec zapisu; obok chwila, w ktorej okno samo pokazalo mape tej plytki (`w_oknie`), i `czas_s` analizy podany przez program; pierwsza plytka (pula zimna) i kolejne osobno z licznikami "do 40 s: n z m" |
| okno bez przerw > 200 ms | `petla_okna` (`najdluzsza_przerwa_ms`, `przekroczen`, `przekroczenia[]`) | DOSLOWNIE od pierwszego tykniecia w petli okna do zamkniecia: zegar Qt co 20 ms w watku okna, przerwa = odstep kolejnych tykniec; start programu przed pokazaniem okna - NIE ZMIERZONO |
| lista "do dofrezowania" = prawda | `lista_do_dofrezowania` (`rowna`, `brakuje_w_programie`, `nadmiarowe_w_programie`), `kolory_prac`, `klikniecia`, `decyzje[]` | lista biezaca programu po decyzjach technika wobec WSZYSTKICH prac z ubytkiem w prawdzie plytek przyjetych; technik klika tylko prace pokazane na czerwono / zolto (kolor z ekranu przed kliknieciem). W wyniku osobne wiersze: ubytki wg prawdy: n czerwonych / n zoltych / n zielonych (przeoczonych); prace cale: n czerwonych (falszywe alarmy); lista = prawda TAK / NIE; `decyzje[]`: kolor przed kliknieciem, wynik, liczba ponowien i czekan na ochrone mapy |
| T2 LACZNIE | `werdykty["T2 LACZNIE"]` | ZAL tylko gdy 5 x ZAL; inaczej FAIL / NIE ZMIERZONO z licznikami |

Zdarzenia srodowiska (proces silnika ginie - `0xC0000142`, restart silnika, blad analizy) sa w polu
`zdarzenia_srodowiska`; przebieg z takim zdarzeniem opisz i powtorz w nowym katalogu (oba wyniki zostaja).

**Testy uzupelniajace (z `<REPO>` interpreterem wersji; nie zastepuja sterownika):**

```
set E3A3_DANE_REF=<PC-katalog>\app\dane_ref\syntetyczne_R59_P2
set E3A3_PROJEKTY=<folder_cyrkon>
call <K>\Polecenie.cmd -m pytest <ST>\testy\test_aplikacja.py -q -s -p no:cacheprovider --rootdir <ST> -k "test_skany_odniesienia_przez_cala_aplikacje_w_petli_qt or test_f_petla_qt_bez_przerw_podczas_analizy_10_plytek" > <ROB>\t2_petla.log 2>&1
call <K>\Polecenie.cmd -m pytest <ST>\testy\test_ui_wieczor.py -q -s -p no:cacheprovider --rootdir <ST> -k "test_6_petla_okna_bez_przerw_10_plytek_po_19_prac" >> <ROB>\t2_petla.log 2>&1
```

**Dowody w `T2/`:** `t2_wynik.json`, `t2_wynik.txt`, `t2_sterownik.log`, `t2_symulator.json` (dziennik symulatora: `sha16`,
rozmiary, czasy - bez nazw zlecen), `t2_log_ostrzezenia.txt` (po kontroli `t9_dane_osobowe.py`), `t2_petla.log`,
`t2_wynik.md` (tabela 5 liczb kryterium: wartosc, zrodlo, ZAL / FAIL / NIE ZMIERZONO; osobne wiersze: zgodnosc obslugi
n z 10; ubytki wg prawdy: czerwonych / zoltych / zielonych (przeoczonych); lista = prawda TAK / NIE; falszywe alarmy;
ponowienia klikniec; wolny RAM i co jeszcze liczylo na PC). Log sterownika jest pusty do konca przebiegu (wyjscie
buforowane) - postep widac w `<ROB>\t2\t2_symulator.log`. Baze `<ROB>\t2\dane\stanowisko.sqlite` zostaw - potrzebna do T8 i T9.

**Czas:** 30 min (sterownik 11-13, testy uzupelniajace 10, zestawienie 5). **Ciezar:** ciezki, seria pomiarowa (tor
pomiarowy). **Rownolegle:** nie z T4, T10, T11 ani z pelnym pytestem (czasy i przerwy petli zaleza od obciazenia).

**Pulapki:** kod 0 sterownika to "pomiar wykonany", nie "ZAL" - czytaj `werdykty`; katalog `--roboczy` musi byc pusty;
sterownik uruchamiac z katalogu programu (robi to `Polecenie.cmd`) - `--program` wskazuje inny katalog programu; gdy w
srodowisku wersji nie ma `psutil` (paczka z f5c3e01 go ma: `psutil-7.2.2`), sterownik sledzi procesy `multiprocessing`
(silnik) i symulator; pierwsza plytka
liczy linie brzegu od zera (63-68 s w raportach A5 / A5i) - przy odstepie 60 s druga plytka moze czekac w kolejce i miec
start analizy > 1 s (to wynik pomiaru, patrz T4 decyzja nr 6 o puli zimnej); COMMIT SQLite w watku okna potrafi
przekroczyc 200 ms przy zajetym dysku (E3-T0p: 226 ms w 1500 probach); pod obciazeniem plytka dochodzi do 46,8 s (E3-A5).
Sterownik w wersji sprzed poprawek recenzji byl uruchomiony na instalacji z paczki w probie generalnej 21.11 (polecenie
z tej sekcji bez zmian, `--wybierz 2,4,5,7 --odstep 5`: 4 z 4, 89 s); wersja po poprawkach (kolory z ekranu) - w probie
skroconej na kopii repo `main` + P15 (3 plytki co 5 s: 3 z 3, ubytki 12: czerwone 5, zolte 7, zielone 0, lista = prawda)
i na instalacji probnej - patrz tabela "Stan sprawdzenia polecen". Pelnego przebiegu 10 x 60 s nikt nie wykonal. Pierwsze
uruchomienie przez `Polecenie.cmd` zacznij od proby skroconej (2 min). Na plytkach
kwadratowych program nie odczytuje numeru (dolki poza polem skanu - raport R59) i pyta "Podaj numer plytki": sterownik
klika numer z prawdy (`odp_podaj_numer_plytki_<n>`), a zrodlo numeru kazdej plytki jest w wyniku (`numery_plytek`).

## T3 - Poranek od poczatku do konca

**Kryterium (plan):** scenariusz SE10 z A6 przez ekran: 3 piece, dofrezowany zab, poprawka, dwuznaczna, nieznana - listy
kompletnych i brakow zgodne z tabela oczekiwan w 100 % wierszy.

**Gdzie:** interpreter i program z paczki, sterownik `<ODB>\narzedzia\t3_poranek.py` (decyzja koordynatora 20.11 nr 2 -
brak B2 usuniety), dane i tabela oczekiwan z `<REPO>` (`testy\test_session_rano.py`: `TABELA_SE10` = 32 wiersze R01-R32,
`testy\dane_sesji\rano\se10.json`; w paczce nie ma katalogu `testy\`). Sterownik przeprowadza TEN SAM scenariusz co
`test_session_rano.py::_scenariusz` (te same dane, te same 32 wiersze liczone tymi samymi funkcjami testu), ale na
prawdziwym kontrolerze programu (`stanowisko.aplikacja.Aplikacja` + `start()`) i w oknie programu: kazda czynnosc
technika idzie kliknieciem albo klawiszem po nazwach obiektow - wybor osoby, przelaczenie trybu, "Ukruszona", wybor
kandydata pracy dwuznacznej, przypisanie reczne po numerze kuwety, potwierdzenie ponownego skanu, "bez projektu",
"Zamknij piec" x 3 (z odpowiedzia na pytanie P14, gdy okno zapyta), 3 restarty programu na tej samej bazie.

**Odstepstwo O5 (wersja po decyzji nr 2):** wyniki skanow SE10 sa sztuczne (scenariusz nie ma plikow STL) i wchodza do
programu ta sama funkcja sesji, ktora kontroler wola po analizie; zegar staly ustawiany na czasy scenariusza
(17-19.11.2026); zlecenia SE10 wpisane do bazy funkcja testu (w programie robi to indeks folderow); okno `offscreen`;
ramki i Excel wylaczone. Lista miejsc, w ktorych sterownik siega do wnetrza programu, jest w naglowku pliku.

**Kroki (instalacja z `/testy` - potrzebny pytest; katalog `<ROB>\t3` nowy / pusty):**

```
set QT_QPA_PLATFORM=offscreen
call <K>\Polecenie.cmd <ODB>\narzedzia\t3_poranek.py --testy <ST>\testy --wyjscie <ROB>\t3 --ustawienia-wzor <K>\ustawienia.toml > <ROB>\t3_sterownik.log 2>&1
echo KOD=%ERRORLEVEL% >> <ROB>\kody.txt
call <K>\Polecenie.cmd -m pytest <ST>\testy\test_session_rano.py -q -rA -p no:cacheprovider --rootdir <ST> -k "se10" --basetemp <ROB>\t3_tmp > <ROB>\t3_se10.log 2>&1
call <K>\Polecenie.cmd -m pytest <ST>\testy\test_ui_rano.py <ST>\testy\test_aplikacja_rano.py -q -rA -p no:cacheprovider --rootdir <ST> > <ROB>\t3_ekran.log 2>&1
```

- Sterownik: ok. 15 s (limit calosci `--limit-s`, domyslnie 600 s). Kody: 0 = scenariusz doszedl do konca i wynik
  zapisany (liczba w pliku i w dwoch ostatnich wierszach wyjscia), 1 = tylko z `--wymagaj-100`: n < 32 (takze przez
  "FAIL (ekran)") - w odbiorze DODAJ te opcje do polecenia, 2 = blad sterownika /
  scenariusz przerwany / limit czasu (wiersze niepoliczone = "nie policzono" z powodem). `--ustawienia-wzor` mozna
  pominac - sterownik bierze wtedy `ustawienia.przyklad.toml` z katalogu programu.
- Dwa pozostale polecenia to testy uzupelniajace (SE10 na poziomie sesji i ekran poranny na innym scenariuszu).

**Liczby kryterium (po recenzji, uwaga 3):** liczba "n z 32" jest liczona z tego, co POKAZUJE ekran: wiersz, ktorego
wartosc z API sesji jest zgodna, ale odczyt ekranu to "nie" albo "nie odczytano", ma wynik "FAIL (ekran)" i NIE liczy sie
do n (liczba wg samego API jest podana obok). Ostatni wiersz wyjscia i pliku: "WERDYKT T3: ZAL / ZAL z odstepstwem O5 /
FAIL (n z 32; ekran: tak a, czesciowo b, nie dotyczy c, nie d, nie odczytano e)" - "ZAL z odstepstwem O5", gdy n = 32, a
ktorys wiersz ma "czesciowo" albo "nie dotyczy". Wstrzykniecie 21.11 (znieksztalcony odczyt tabeli ekranu): 27 z 32,
5 x "FAIL (ekran)", kod 1 z `--wymagaj-100` (przed poprawka: 32 z 32, kod 0).
`<ROB>\t3\t3_wynik.txt` / `t3_wynik.json`: "SE10 przez ekran: n z 32 wierszy zgodnych" (ma byc 32 z
32) oraz kolumna "ekran" dla 10 wierszy z listami kompletnych i brakow (R11, R14, R15, R17, R21, R22, R28, R29, R30,
R31): kuwety i zeby odczytane z tabel okna (`tabela_kompletne`, `tabela_braki`, `tabela_braki_biezace`) wobec
oczekiwanych - "tak" / "czesciowo" / "nie dotyczy" z powodem. Proba 20.11 na kopii integracyjnej: 32 z 32; ekran "tak" 8,
"czesciowo" 1 (R31: po restarcie ekran pokazuje tylko ostatni zamkniety piec; piece 1 i 2 z poprzedniej doby tylko z
API), "nie dotyczy" 1 (R17: listy "do dofrezowania" ekran poranny nie pokazuje). Kazde "nie" w kolumnie "ekran" = FAIL
wiersza - liczy to juz sam sterownik. Testy uzupelniajace: `t3_se10.log` 33 `PASSED`; `t3_ekran.log` w calosci `passed`.

**Do oceny koordynatora (stwierdzone w probie, nie jest to roznica wobec tabeli SE10):** przed "Zamknij piec" 2 okno NIE
zadalo pytania P14, choc sesja liczy 1 prace nieznana jako nierozstrzygnieta (R22) - okno pyta tylko o prace bez
decyzji, a ta ma decyzje "bez projektu" (R20). Sterownik zapisuje to w polu `pytania_zamkniecia` i wierszu UWAGA.

**Dowody w `T3/`:** `t3_wynik.txt`, `t3_wynik.json`, `t3_sterownik.log`, `t3_se10.log`, `t3_ekran.log`, `t3_wynik.md`.
Baze `<ROB>\t3\baza\stanowisko.sqlite` zostaw (do T8); katalog `<ROB>\t3_tmp` tez (`--basetemp` zachowuje pliki testu).

**Czas:** 15 min. **Ciezar:** lekki (sterownik) / sredni (2 pliki testow; przy wolnym RAM < 3000 MB czekac).
**Rownolegle:** tak, poza seria pomiarowa z testami czasowymi (`test_k4_spacja...` ma prog 1 s).

**Pulapki:** katalog `--wyjscie` musi byc nowy albo pusty; sterownik uruchamiac z katalogu programu (robi to
`Polecenie.cmd`); bez pytest w srodowisku wersji sterownik konczy kodem 2 z komunikatem (instalacja z `/testy`); czesc
wierszy SE10 sprawdza API, nie ekran (R12 / R13 plan ramki, R32 dane osobowe); `--basetemp` kasuje wskazany katalog
przed startem - podaj katalog tylko do tego celu. Sterownik (wersja sprzed poprawek recenzji) byl uruchomiony na
instalacji z paczki w probie generalnej 21.11 poleceniem z tej sekcji bez zmian: 32 z 32, kod 0, 10,9 s; wersja po
poprawkach - na kopii repo `main` + P15 (32 z 32) i na instalacji probnej (tabela "Stan sprawdzenia polecen").

## T7 - Odpornosc

**Kryterium (plan):** zabicie silnika w trakcie analizy; zamkniecie programu w polowie wieczoru; brak folderu "Cyrkon";
brak sieci; brak ramki; baza zajeta - za kazdym razem komunikat z PW zal. F i dalsza praca; stan odtworzony z bazy.

**Gdzie:** testy z `<REPO>` na KODZIE PROGRAMU Z INSTALACJI (czesc A; decyzja koordynatora nr 4 po recenzji) + 3 proby
reczne na programie z paczki (czesc B).

**Czesc A - testy (jedna linia na przypadek; log `<ROB>\t7_<nr>.log`):** kazdy przypadek przez
`<K>\Polecenie.cmd <ODB>\narzedzia\pytest_instalacja.py --st <ST> --wynik <ROB>\t7_<nr>_zrodlo_kodu.txt -- <ST>\testy\<plik> -q -rA -p no:cacheprovider --rootdir <ST> -k "<nazwy>" > <ROB>\t7_<nr>.log 2>&1`
(skrypt laduje pakiety `stanowisko` i `ramka` z katalogu programu wersji przed startem pytest i po testach wypisuje, ile
modulow programu przyszlo z instalacji, a ile z repo; ostatni wiersz "WERDYKT ZRODLA KODU: INSTALACJA" jest warunkiem
zaliczenia przypadku jako "na programie z paczki"; kod 3 albo werdykt "REPO" = przypadek liczony z odstepstwem O14).
Procesy potomne testow (proces silnika, ramka) importuja kod sami - dla przypadku 1 (zabicie silnika) zgodnosc kodu
potwierdza tylko wiersz "pliki *.py instalacji = repo: a z b" (O14). Testy czytajace ustawienia domyslne dostaja plik
`<ST>\ustawienia.toml` (T1 krok 2 - skrypt ustawia sciezke w procesie testow i wypisuje to w wierszu "plik ustawien
domyslnych w testach"; w katalogu programu wersji takiego pliku nie ma - bez tego `test_silnik.py` konczyl sie bledem
"brak pliku ustawien"). Test, ktory mimo to konczy sie bledem zwiazanym z ukladem katalogow instalacji (nie z programem),
powtorz zwyklym `<K>\Polecenie.cmd -m pytest ...` i zapisz OBA wyniki - ten przypadek liczy sie wtedy z odstepstwem O14.

| Nr | Przypadek | Testy (`<ST>\testy\...`) |
|---|---|---|
| 1 | zabicie silnika | `test_aplikacja.py -k "test_zabity_proces_analizy_komunikat_i_nastepny_skan or test_silnik_nie_startuje_skan_czeka_i_wraca_po_restarcie"`; `test_silnik.py -k "test_zabicie_procesu_z_zewnatrz or test_awarie_zly_plik_zabity_proces_brak_pliku or test_awaria_prawdziwej_analizy_i_nastepne_zadanie"` |
| 2 | zamkniecie w polowie wieczoru | `test_aplikacja.py -k "test_e_zamkniecie_w_trakcie_analizy_i_ponowny_start or test_e_awaria_bez_zamkniecia_nadrabianie_folderu or test_e_dodatkowe_punkty_awarii"`; `test_ui_wieczor.py -k test_5_restart_programu_odtwarza_plytki_i_decyzje_na_ekranie` |
| 3 | brak folderu "Cyrkon" | `test_aplikacja.py -k "test_g_bez_projektow_skany_czekaja_do_odswiezenia_puli or test_folder_skanera_pojawia_sie_pozniej"`; `test_pula_aplikacja_r3.py -k test_r3_d8_nieudane_odswiezenie_ponawiane` |
| 4 | brak sieci | `test_indicate.py -k test_k5_utrata_sieci_5_potwierdzen_100_powtorzen`; `test_ramka.py -k "test_k5_utrata_sieci or test_ramka_poranna_bez_sieci_trzyma_plan_do_limitu"`; `test_excel.py -k test_excel_niedostepny_komunikat_bez_awarii` |
| 5 | brak ramki | `test_aplikacja_rano.py -k test_k5_wylaczona_ramka_i_brak_excela_ostrzezenie_i_dalsza_praca`; `test_ui_rano.py -k test_k5_bez_ramki_i_excela_komunikat_program_dziala_dalej` |
| 6 | baza zajeta | `test_aplikacja.py -k "test_baza_zajeta_wynik_nie_ginie or test_p8_blad_analizy_przy_zajetej_bazie"`; `test_baza.py -k test_d1_baza_zajeta_przez_inny_proces_daje_czytelny_komunikat`; `test_aplikacja_rano.py -k test_d2_baza_zajeta_zdarzenia_ramki_czekaja_i_wracaja`; po scaleniu P14: `test_p14_baza_zajeta.py` (caly plik: prawdziwa blokada `BEGIN EXCLUSIVE` / `IMMEDIATE`, 17 przypadkow, odpowiedz w 1,0 s, komunikat `decyzja_niezapisana` / `polecenie_niezapisane` z "Ponow teraz") - potwierdzone 20.11 na kopii integracyjnej a2236c1: plik `testy\test_p14_baza_zajeta.py` jest, oba rodzaje komunikatow sa w `statusy.py` |

**Czesc B - proby reczne na programie z paczki (`set QT_QPA_PLATFORM=offscreen`; kazda: stan przed, zdarzenie, log, stan po):**

1. Brak folderu "Cyrkon": zmien nazwe katalogu `<nazwa>_wej\Cyrkon` na `Cyrkon_x`, `<K>\Stanowisko.cmd --zamknij-po 30`,
   w `<DANE>\logi\stanowisko.log` szukaj komunikatu `pula_brak_folderu`; przywroc nazwe; `Samokontrola.cmd --bez-sieci`
   przy braku folderu ma dac kod 1 (blad) z wierszem o folderze.
2. Zamkniecie w polowie wieczoru (dwa okna `cmd`; pusta baza; folder eksportu pusty):
   okno 1: `<K>\Stanowisko.cmd --zamknij-po 600`;
   okno 2: `<K>\Polecenie.cmd narzedzia\symulator_skanera.py --folder <folder_eksportu_skanera> --zrodla <PC-katalog>\app\dane_ref\syntetyczne_R59_P2 --ile 4 --odstep 60 --rownolegle 1 --seed 1 --dziennik <ROB>\t7_b2_symulator.json`.
   PID programu = JEDYNY proces `python` ze sciezka w `<K>\wersje\`:
   `powershell -NoProfile -Command "Get-Process python | Where-Object { $_.Path -like '<K>\wersje\*' } | Select-Object Id,StartTime,Path"`
   - przed startem okna 1 ma dac 0 wierszy, po starcie 1 wiersz (posrednik srodowiska wersji; wlasciwy interpreter i
   proces silnika maja sciezke Pythona bazowego, taka jak procesy innych wykonawcow - po sciezce ich nie odroznisz).
   Inna liczba wierszy niz 1 = NIE ZMIERZONO. Zakonczenie posrednika konczy takze interpreter i proces silnika
   (sprawdzone 21.11: 3 z 3 procesow nie zyje po 1,5 s). Instalacja `<K>` tylko tego wykonawcy. Oba odczyty zapisz do
   `<ROB>\t7_b2_pid.txt`; odczyt "po starcie" zrob PRZED startem okna 2 (symulator przez `Polecenie.cmd` to tez proces
   ze sciezka `<K>\wersje\*`); cudzych PID-ow nie ruszac. Po zapisie 2. skanu (dziennik symulatora: 2 pozycje w
   `zapisy`) zakoncz program:
   `powershell -NoProfile -Command "Stop-Process -Id <pid programu> -Force"`; symulator zostaw; uruchom okno 1 ponownie.
   Oczekiwane: `PY -I <ODB>\narzedzia\sql_odczyt.py --baza <DANE>\stanowisko.sqlite "SELECT status, count(*) FROM skany GROUP BY status"`
   po ok. 6 min = 4 skany z 4; w `<DANE>\logi\stanowisko.log` wiersz `(plik zastany - nadrabianie)` dla 2. skanu i w
   zdarzeniach `nowy_skan` z `"zastany": true` (`sql_odczyt.py ... "SELECT typ, dane FROM zdarzenia ORDER BY id"`);
   komunikat `wznowiono` jest tylko na ekranie - potwierdza go test czesci A
   `test_e_awaria_bez_zamkniecia_nadrabianie_folderu`; pliku `zadania_niezakonczone.json` nie ma po nadrobieniu.
3. Zabicie silnika: ten sam uklad dwoch okien z `--ile 3`; w trakcie analizy 2. skanu (ok. 5 s po 2. pozycji `zapisy`)
   zakoncz proces silnika: z listy `Get-Process python | Select-Object Id,StartTime,Path` wez procesy ze sciezka Pythona
   bazowego i `StartTime` w ciagu 5 s po `StartTime` posrednika z p. 2 - maja byc dokladnie 2 (interpreter programu i,
   mlodszy, silnik); inna liczba = NIE ZMIERZONO (przypadek 1 liczy sie wtedy tylko testami czesci A - wpisz to):
   `Stop-Process -Id <pid silnika> -Force`;
   oczekiwane: komunikat `blad_analizy` ("przerwana") w logu i zdarzeniach, nastepny skan przyjety (3. skan ma status w bazie).
   Proba 2 wykonana przez recenzenta 21.11 na instalacji probnej (2 skany `*_r54`, program z wlasnym plikiem ustawien:
   `skany` 2 z 2, `nowy_skan` z `zastany` true, slowo `wznowiono` w logu 0 razy); proba 3 NIE byla wykonana - pierwsze
   wykonanie zapisz krok po kroku; gdy PID-u nie da sie ustalic jednoznacznie: "NIE ZMIERZONO" (nie zabijac na probe).
   Na instalacji WSPOLNEJ odbioru (sekcja "Ustalenia koordynatora do wykonania odbioru") regula "0 wierszy przed
   startem, 1 po starcie" jest spelnialna tylko wtedy, gdy w tym czasie zaden inny test nie uruchamia niczego przez
   `<K>\Polecenie.cmd` / `<K>\Stanowisko.cmd` - patrz tam punkt "T7 czesc B".

**Komunikaty a PW zal. F:** tresci komunikatow sa w `stanowisko\statusy.py` (`KOMUNIKATY`, `BLEDY_RAMEK`). Zalacznik F
jest w dokumencie "Stanowisko kontroli cyrkonii - plan wdrozenia v2" (`Ramki/`, plik `.md` z pauza w nazwie); wg
recenzji PR #40 runda 1 ma 12 wierszy, z czego 8 ma odpowiednik w programie. Testy sprawdzaja `rodzaj` komunikatu, nie
tekst wzgledem zal. F. Wykonawca sporzadza tabele `t7_komunikaty.md`: 6 przypadkow x (rodzaj komunikatu z testu, tekst
ze `statusy.py`, wiersz zal. F albo wiersz tabeli `instrukcje/co_robic_gdy_nie_dziala.md` z A11d, zgodne tak / nie).
**Decyzja koordynatora 20.11 nr 3 (zamyka POTRZEBUJE 4):** przypadek, w ktorym program daje komunikat i pracuje dalej,
ale tekstu komunikatu nie ma w PW zal. F: wynik przypadku = **"ZAL z odstepstwem (komunikat spoza zal. F: <tekst>)"** +
pozycja na liscie zadan wlasciciela w `RAPORT.md` (uzupelnic zal. F albo zmienic napis). Brak komunikatu ALBO brak
dalszej pracy ALBO stan nieodtworzony z bazy = **FAIL** przypadku. W `t7_komunikaty.md` kolumna "wynik" ma wiec trzy
wartosci: ZAL / ZAL z odstepstwem / FAIL; w `RAPORT.md` liczniki "przypadki n z 6, w tym z odstepstwem k".

**Liczby kryterium:** 6 z 6 przypadkow: (a) testy `PASSED` (licznik na przypadek), (b) komunikat wskazany w tabeli
(tekst w zal. F = ZAL; tekst spoza zal. F = ZAL z odstepstwem; brak komunikatu = FAIL), (c) "dalsza praca" i "stan z
bazy" = asercje testow z wiersza 1, 2, 6 + proby B (brak ktoregokolwiek = FAIL).

**Dowody w `T7/`:** `t7_1.log`..`t7_6.log`, `t7_proby_reczne.md`, `t7_komunikaty.md`, `t7_wynik.md`.

**Czas:** 45 min. **Ciezar:** `test_silnik.py` (wybrane testy) - sredni, uruchamiac pojedynczo; reszta lekka.
**Rownolegle:** tak, poza seria pomiarowa; proby B na wlasnej instalacji roboczej.

**Pulapki:** nie zabijac cudzych procesow (PID tylko z wlasnego logu); `test_baza_zajeta_wynik_nie_ginie` podstawia blad
przez monkeypatch (to nie jest prawdziwa blokada - prawdziwa jest w `test_d1` i `test_p14_baza_zajeta.py`); przed P14
decyzja kliknieta przy zajetej bazie przepadala, a okno stalo ok. 15 s (recenzja PR #40).

## T10 - Regresja silnika

**Kryterium (plan):** zestawy R59 (40 skanow) - wyrownanie 40 z 40, top-1 "dobrze" 100 %, falszywe czerwone na pracach
calych 0 (R59 pkt 6.2).

**Gdzie:** narzedzie z paczki przez `POL`. **Dane:** `<PC-katalog>\app\dane_ref\syntetyczne_R59_P2` (24 STL + 24 pliki
prawdy) i `syntetyczne_R59_P3a` (16 + 16) = 40 skanow (kopia tych samych zestawow:
`<PC-katalog>\r59\program\Ramki\stanowisko\dane\`); projekty: `<PC-katalog>\app\Prace_test` (15 folderow, 17 STL).

**Kroki (tor 2, jedna linia):**

```
call <K>\Polecenie.cmd narzedzia\metryki_P3a.py --skany <PC-katalog>\app\dane_ref\syntetyczne_R59_P2 <PC-katalog>\app\dane_ref\syntetyczne_R59_P3a --projekty <PC-katalog>\app\Prace_test --wyjscie <ROB>\t10 --nazwa t10_surowe_metryki.json --procesy 1 --ustawienia <K>\ustawienia.toml > <ROB>\t10_surowe.log 2>&1
```

**Liczby kryterium (surowe wyjscie: plik `<ROB>\t10\t10_surowe_metryki.json` i log `<ROB>\t10_surowe.log`):**

| Liczba | Pole |
|---|---|
| wyrownanie n z 40 | `plate_match.wyrownanie_ok` / `plate_match.skanow` (w sekcji zbiorczej pliku wyniku) |
| top-1 "dobrze" | `top1_per_scenariusz.dobrze`: `prac` i `top1_bledny` (= 0) |
| falszywe czerwone na pracach calych | wiersz logu zaczynajacy sie od `PRACE CA` (w logu z polska litera): `..., z czerwonym N` (N = 0; liczby `prac_calych`, `prace_cale_z_czerwonym`) |

Punkt odniesienia: R59 pkt 6.2 (`raporty/R59_2026-11-14.md`): 40 / 40, 276 / 276, 0 / 127; E3-A5 runda 4 (pula): 40 / 40,
276 / 276, 0 / 132. Nazwy pol sprawdzone w kodzie `metryki_P3a.py` (wiersze 188-233) i w wyniku proby z `--limit 2` na
instalacji probnej 21.11 (2 skany, 68 s, kod 0): sekcja zbiorcza nazywa sie `zbiorczo` (`zbiorczo.plate_match.skanow`,
`zbiorczo.plate_match.wyrownanie_ok`, `zbiorczo.top1_per_scenariusz.dobrze.prac` / `.top1_bledny`); wiersz logu
"PRACE CA..." ma litere spoza ASCII - kopia logu (`t10.log`) przed dodaniem do dowodow przechodzi przez
`dowody_lf.py --napraw`.

**Dowody w `T10/`:** `t10_metryki.json` = KOPIA surowego `t10\t10_surowe_metryki.json`, zrobiona dopiero po kontroli
`PY -I <ODB>\narzedzia\t9_dane_osobowe.py N --cel <ROB>\t10\t10_surowe_metryki.json --cel <ROB>\t10_surowe.log --wynik <ROB>\t10_t9.txt`
BEZ `--dozwolone` (kod 0; przy trafieniach do dowodow idzie tylko `t10_wynik.md`), `t10.log` = kopia
`t10_surowe.log` (ta sama kontrola), `t10_t9.txt`, `t10_wynik.md`. Nazwy plikow surowych maja czlon `surowe` po to,
zeby wzor `--dozwolone t10_surowe` w T9 NIE obejmowal zadnego pliku z listy dowodow (uwaga 33 recenzji rundy 2).

**Czas:** 40-60 min (40 skanow x 25-70 s w 1 procesie). **Ciezar:** ciezki, seria pomiarowa (tor 2). **Rownolegle:** nie
z T2, T4, T11.

**Pulapki:** `--procesy` > 1 zawyza czasy (i lamie zasade 1 procesu); miedzy przebiegami rozrzut 1 gniazda (RANSAC) -
jeden przebieg jest wynikiem, powtorka tylko z opisem obu; `<PC-katalog>\r59\Prace_test` z raportu R59 juz nie istnieje;
wynik zawiera nazwy plikow projektow = dane - do repo idzie tylko to, co przeszlo kontrole T9.

## T11 - Stare plytki

**Kryterium (plan):** skany `*_r54` przez aplikacje - uklad rozpoznany albo ostrzezenie z nazwa wlasciwego ukladu;
0 zielonych przy zlym ukladzie; uklad zapisany w `skany`.

**Gdzie:** program z paczki (`Stanowisko.cmd`) + symulator skanera programu przez `Polecenie.cmd`. **Dane:** `<PC-katalog>\app\dane_ref\syntetyczne_r54_P2`
(24 skany, w tym 12 okraglych) i `syntetyczne_r54_P3a` (16, w tym 12 okraglych); wzorzec nazw
`skan_<okragla_>wieczorna|poranna_r54_n<k>_s<seed>.stl` + prawda `.json`.

**Kroki:**

1. Czesc A (rozpoznanie, szybka, lekka):
   `<K>\Polecenie.cmd narzedzia\auto_uklad.py --skany <PC-katalog>\app\dane_ref\syntetyczne_r54_P2 <PC-katalog>\app\dane_ref\syntetyczne_r54_P3a --wyjscie <ROB>\t11_auto --procesy 1 --ustawienia <K>\ustawienia.toml`
   Liczby: `auto_uklad.json`, `podsumowanie.bez_numeru` i `z_numerem`: `ok` = 40 z 40, `zle_ale_pewny` = 0.
2. Czesc B (przez aplikacje, tor 2): pusta baza; `<K>\Stanowisko.cmd --zamknij-po <s>` i
   `<K>\Polecenie.cmd narzedzia\symulator_skanera.py --folder <folder_eksportu_skanera> --zrodla <PC-katalog>\app\dane_ref\syntetyczne_r54_P2 <PC-katalog>\app\dane_ref\syntetyczne_r54_P3a --ile 40 --odstep 45 --rownolegle 1 --seed 1 --dziennik <ROB>\t11_symulator.json`
   (WSZYSTKIE 40 skanow `*_r54` zestawu: 24 z P2 + 16 z P3a - decyzja koordynatora nr 5 po recenzji; `--zamknij-po` =
   40 x 45 s + 300 s zapasu = 2100). Gdy w zestawie jest inna liczba plikow albo symulator nie przyjmie dwoch katalogow -
   podaj liczbe faktyczna i powod (liczniki "z <tyle, ile bylo>"). Plytki poranne w trybie wieczornym dostaja status
   `plytka_nie_z_trybu` - uklad ma byc mimo to zapisany.
3. `PY -I <ODB>\narzedzia\sql_odczyt.py --baza <DANE>\stanowisko.sqlite "SELECT id, status, uklad, uklad_zrodlo, uklad_zgodny FROM skany ORDER BY id"`
   i `"SELECT s.id, s.status, s.uklad, sum(p.status_gniazda='zielony') AS zielonych FROM skany s LEFT JOIN prace p ON p.skan_id = s.id GROUP BY s.id"`
   (kolumny `prace.skan_id` i `prace.status_gniazda` sprawdzone w `baza.py`).
4. Zly uklad (wymuszony recznie) - testy: `<K>\Polecenie.cmd -m pytest <ST>\testy\test_session_wieczor.py <ST>\testy\test_straznik.py <ST>\testy\test_kontroler_api.py <ST>\testy\test_auto_uklad.py -q -rA -p no:cacheprovider --rootdir <ST> -k "niezgodny_uklad or niezgodna_z_ukladem or auto or innego_ukladu"`.

**Liczby kryterium:** (a) `uklad` z bazy = `plytka` z pliku prawdy skanu (pole prawdy MA JUZ koncowke `_r54` - sprawdzone
na 4 nazwach x 6 skanow; niczego nie doklejac) dla n z 40 skanow (ma byc 40 z 40; kazdy inny skan = FAIL skanu, decyzja
nr 4), `uklad_zrodlo` = `auto`; pary skan - prawda laczy `sha16` z dziennika symulatora; (b) skany o statusie
`niezgodny_uklad` albo z `uklad_zgodny` = 0: suma `zielonych` = 0 - gdy wszystkie 40 ukladow sa rozpoznane, ten licznik
jest pusty (0 z 0): skan z niezgodnym ukladem przez aplikacje to wtedy pozycja nr 7 scenariusza T2 (`zielonych` = 0 w
`t2_wynik.json`, wiersz plytki nr 7) - wpisz odsylacz i liczbe; (c) `uklad` nie jest pusty w zadnym wierszu `skany` (40 z 40).

**Uwaga do kryterium (O6):** przy rozpoznawaniu automatycznym "zly uklad" oznacza "zaden uklad nie pasuje"; komunikat
`niezgodny_uklad` w `statusy.py` NIE zawiera nazwy wlasciwego ukladu (lista `uklady_pasujace` jest tylko w wyniku
`porownaj` i starym `ui_test.py`). Druga galaz kryterium ("ostrzezenie z nazwa wlasciwego ukladu") jest wiec dzis
niespelnialna przez aplikacje - test zalicza sie pierwsza galezia (uklad rozpoznany 40 z 40), a brak drugiej galezi jest
pozycja do decyzji wlasciciela w `RAPORT.md` (O6: dopisac nazwe wlasciwego ukladu do komunikatu albo przyjac kryterium
w brzmieniu "uklad rozpoznany").

**Decyzja koordynatora 20.11 nr 4 (zamyka POTRZEBUJE 5):** kryterium ma "albo" - plytka z ukladem rozpoznanym = skan
zaliczony; ostrzezenie BEZ nazwy wlasciwego ukladu (skan nierozpoznany, status `niezgodny_uklad`) = **FAIL tego skanu**
(licznik "FAIL n z 40" w wyniku); zielona praca przy zlym ukladzie (skan z `uklad_zgodny` = 0 albo statusem
`niezgodny_uklad` i `zielonych` > 0) = **FAIL calego testu**. Wynik T11 = "ZAL z odstepstwem O6" tylko przy 40 z 40
rozpoznanych i 0 zielonych przy zlym ukladzie (O6: druga galaz kryterium niespelnialna).

**Dowody w `T11/`:** `t11_auto_uklad_podsumowanie.json` (sama sekcja `podsumowanie`), `t11_skany.tsv`, `t11_zielone.tsv`,
`t11_testy.log`, `t11_wynik.md`.

**Czas:** 60 min (A 5, B 40 = 40 x 45 s + start + ostatnia analiza, testy 10). **Ciezar:** czesc B ciezka (tor 2), reszta lekka. **Rownolegle:** B nie z T2, T4, T10.

**Pulapki:** uklady `*_r54` wymagaja katalogow `modele_plytek\*_r54` (sa w paczce - potwierdza samokontrola); skany
`_r54` sa tylko sztuczne; `<PC-katalog>\e3`, `r58` i `<PC>\Desktop\Ramki` nie maja skanow `r54`.

## T4 - Pula

**Kryterium (plan):** 400 wpisow, dwa wspolczynniki na plytce, STL w dwoch raportach - top-1 "dobrze" 100 %; plytka do
40 s; pamiec do 8 GB.

**Gdzie:** narzedzie z paczki przez `POL`. **Dane (gotowe, tylko odczyt):** `<PC-katalog>\e3\a5\pomiary\pula400\`:
`pula_400.csv` (400 wpisow + naglowek), `stl\` (356 STL), `plytki\` (10 skanow + 10 plikow prawdy, prace z krazkow o
wspolczynniku 1,20 i 1,25 na jednej plytce). Zestaw do przebiegu przez program: `<PC-katalog>\e3\a5i\t4\` (`drzewo\Cyrkon`
47 folderow / 373 STL, `millbox\wspolczynniki.csv` 400 wpisow, `eksport\` 10 skanow).

**Kroki (tor 2; pamiec podreczna puli w nowym, pustym katalogu `<ROB>\pamiec`):**

```
call <K>\Polecenie.cmd narzedzia\metryki_pula.py czas --katalog <PC-katalog>\e3\a5\pomiary\pula400 --wpisow 400 --pamiec <ROB>\pamiec --linie <ROB>\linie --wyjscie <ROB>\t4 --nazwa t4_surowe_czas_zimna.json --procesy 1 --ustawienia <K>\ustawienia.toml > <ROB>\t4_czas_zimna.log 2>&1
call <K>\Polecenie.cmd narzedzia\metryki_pula.py czas --katalog <PC-katalog>\e3\a5\pomiary\pula400 --wpisow 400 --pamiec <ROB>\pamiec --linie <ROB>\linie --wyjscie <ROB>\t4 --nazwa t4_surowe_czas_ciepla.json --procesy 1 --ustawienia <K>\ustawienia.toml > <ROB>\t4_czas_ciepla.log 2>&1
call <K>\Polecenie.cmd narzedzia\metryki_pula.py jakosc --katalog <PC-katalog>\e3\a5\pomiary\pula400 --wpisow 400 --pamiec <ROB>\pamiec --linie <ROB>\linie --wyjscie <ROB>\t4 --nazwa t4_surowe_jakosc.json --procesy 1 --ustawienia <K>\ustawienia.toml > <ROB>\t4_jakosc.log 2>&1
```

Trzy polecenia w jednym pliku `.cmd` wymagaja `call` (bez niego nie bedzie przebiegu cieplego ani `jakosc`).
Pierwszy przebieg zaczyna od pustych `<ROB>\pamiec` i `<ROB>\linie` (pula zimna), drugi korzysta z tego, co zapisal
pierwszy (pula ciepla). Opcje `czas` sprawdzone przez `--help`: `--katalog` (wymagana), `--wyjscie`, `--nazwa`, `--pamiec`
("pusty = pamiec zimna"), `--linie`, `--wpisow`, `--plytek`, `--procesy`, `--seed`, `--limit`, `--ustawienia`.
Podpolecenie `jakosc` ma te same opcje (`jakosc --help` uruchomione 20.11). Gdy narzedzie mimo `--wyjscie` probuje pisac
obok zestawu w `<PC-katalog>\e3` (tylko odczyt), skopiuj zestaw do `<ROB>\pula400` (`robocopy /E`) i podaj te kopie.

**Liczby kryterium:**

| Liczba | Pole wyniku |
|---|---|
| top-1 "dobrze" n z n | `jakosc`: `top1_projekt` i `top1_wpis` (licznik / prac); `zielone` ze zlym wpisem = 0 |
| plytka do 40 s | `czas`: `plytki[].czas_s` - osobno: plytka 1 przebiegu zimnego, plytki 2-10 przebiegu zimnego, plytki 1-10 przebiegu cieplego; dla kazdej grupy maksimum, mediana i licznik "do 40 s: n z m" (decyzja nr 6) |
| pamiec do 8 GB | `czas`: `szczyt_mb` (szczyt zbioru roboczego procesu, `psutil` `peak_wset`) |
| dwa wspolczynniki, STL w dwoch raportach | licznik prac z prawdy z 1,20 i 1,25 na plytce; `wpis_niejednoznaczny` |

**Decyzja koordynatora 20.11 nr 6 (O7, zamyka pytanie o pule zimna / ciepla):** mierz i podaj OBA przebiegi - pierwsza
plytka po starcie programu (pula zimna) i kolejne (pula ciepla) - z osobnymi licznikami "do 40 s: n z m". Kryterium
"plytka do 40 s" jest liczone dla WSZYSTKICH plytek: (a) wszystkie do 40 s = ZAL; (b) przekracza je TYLKO pierwsza plytka
po zimnym starcie = **"ZAL z odstepstwem"** z liczba sekund i pozycja do decyzji wlasciciela w `RAPORT.md`; (c) przekracza
ktorakolwiek plytka przy puli cieplej (plytki 2-10 przebiegu zimnego i wszystkie 10 przebiegu cieplego) = **FAIL**.
W `t4_wynik.md` trzy wiersze: "zimna, plytka 1: _ s (do 40 s: _ z 1)", "zimna, plytki 2-10: maks. _ s (do 40 s: _ z 9)",
"ciepla, plytki 1-10: maks. _ s (do 40 s: _ z 10)". Dotychczasowe pomiary: przy puli zimnej plytka 1 liczy linie brzegu
od zera - 63,4 s (E3-A5i) i 67,9 s (E3-A5), czyli wariant (b). "Pamiec do 8 GB": w odbiorze mierzony jest JEDEN proces
(`szczyt_mb` z `metryki_pula czas`); szczyt procesu okna NIE jest mierzony w odbiorze - do sumy bierze sie liczbe z
raportu E3-A5 (ok. 1,0 GB; razem 3,95 GB + 1,0 GB) i zapisuje wprost "okno: wg raportu E3-A5, nie mierzone w odbiorze".
Zmierzone dotad: top-1 187 / 187, plytki 2-10 maks. 34,2 s, ciepla maks. 28,8 s, szczyt 3,82-3,95 GB.

**Dowody w `T4/`:** `t4_wynik.md` (tabela liczb, pula ciepla i zimna osobno), `t4_czas_ciepla.json`, `t4_czas_zimna.json`,
`t4_jakosc.json` = KOPIE plikow surowych `t4\t4_surowe_*.json` (czlon `surowe` w nazwie: wzor `--dozwolone t4_surowe`
w T9 nie obejmuje wtedy zadnego pliku z listy dowodow) - kopie tylko po kontroli `t9_dane_osobowe.py` BEZ
`--dozwolone` na plikach surowych (pliki puli zawieraja sciezki z nazwami zlecen;
przy trafieniach do repo idzie sam `t4_wynik.md`).

**Czas:** 45 min (budowa puli zimnej ok. 285 s, 10 plytek x ok. 25 s, 3 przebiegi). **Ciezar:** ciezki, seria pomiarowa
(tor 2; szczyt ok. 4 GB - start przy wolnym RAM >= 6000 MB). **Rownolegle:** NIE - jedyna sesja pomiarowa naraz
(nie z T10, T2, T11).

**Pulapki:** `pula_400.csv` ma krazek z trzema wartosciami wspolczynnika - w programie to sprzecznosc (pierwsza proba
A5i dala pule 54 wpisow; odstepstwo 7 raportu E3-A5i) - dlatego T4 liczy sie narzedziem `metryki_pula`, a przebieg przez
program (skrypt poza repo `<PC-katalog>\e3\a5i\t4.py`) jest opcjonalnym potwierdzeniem z ustawieniem
`[silnik] pula_wpisow = true`; pod obciazeniem plytka dochodzila do 46,8 s.

## T5 - Ramka na atrapie w sieci lokalnej

**Kryterium (plan):** plan, kolory, kuweta po kuwecie, zmiana plytki, 5 potwierdzen bez sieci, restart ramki, Spacja -
5 z 5 potwierdzen dostarczonych, 0 powtorek; plan odtworzony do 5 s; stan po Spacji ponizej 1 s.

**Gdzie:** testy z `<REPO>` na kodzie programu z instalacji (liczby kryterium, 127.0.0.1) + proba z atrapa ramki na
adresie sieci lokalnej PC na programie z paczki (zapis ruchu do T9).

**Odstepstwo O8 (pelny opis, decyzja koordynatora nr 4 po recenzji):** WSZYSTKIE liczby kryterium T5 (5 z 5, 0 powtorek,
plan do 5 s, Spacja ponizej 1 s) pochodza z testow pytest, w ktorych atrapa ramki i program stoja na TYM SAMYM komputerze
i lacza sie przez 127.0.0.1 (adres jest wpisany w testach - plikow testow ta paczka nie zmienia). Na adresie karty
sieciowej PC i programie z paczki (czesc B) sprawdzany jest tylko przebieg ramki W z 3 skanami - bez pomiaru 5 potwierdzen
bez sieci, restartu ramki i Spacji; ramka P tylko w testach. Takze czesc B to "atrapa i program na tym samym komputerze":
ruch przechodzi przez stos sieciowy, nie przez kabel ani Wi-Fi. Prawdziwa siec = T15 (odlozony). Wynik T5 to najwyzej
"ZAL z odstepstwem O8".

**Czesc A - liczby kryterium (testy na dwoch procesach, 127.0.0.1; kod programu z instalacji):**

```
call <K>\Polecenie.cmd <ODB>\narzedzia\pytest_instalacja.py --st <ST> --wynik <ROB>\t5_zrodlo_kodu_1.txt -- <ST>\testy\test_indicate.py <ST>\testy\test_ramka.py -q -s -rA -p no:cacheprovider --rootdir <ST> -k "test_k1 or test_k2 or test_k4 or test_k5 or test_k6 or test_k7 or test_zz_k8" > <ROB>\t5_testy.log 2>&1
call <K>\Polecenie.cmd <ODB>\narzedzia\pytest_instalacja.py --st <ST> --wynik <ROB>\t5_zrodlo_kodu_2.txt -- <ST>\testy\test_aplikacja_rano.py -q -s -rA -p no:cacheprovider --rootdir <ST> -k "test_a_ or test_k1_plan_ramki_porannej or test_k2_enter or test_k4_spacja" > <ROB>\t5_testy_2.log 2>&1
```

Ostatni wiersz kazdego przebiegu: "WERDYKT ZRODLA KODU: INSTALACJA" (kod 0) - inaczej liczby pochodza z kodu repo i w
`t5_wynik.md` trzeba to zapisac (odstepstwo O14). Testy z ramka w osobnym procesie uruchamiaja ten proces same (kod z
katalogu podanego przez test) - dla nich zgodnosc potwierdza wiersz "pliki *.py instalacji = repo: a z b".

| Liczba | Test | Zmierzone dotad |
|---|---|---|
| 5 z 5 potwierdzen, 0 powtorek | `test_indicate.py::test_k5_utrata_sieci_5_potwierdzen_100_powtorzen`, `test_ramka.py::test_k5_...` | 500 z 500, 0 powtorek (E3-A8i) |
| plan odtworzony do 5 s | `test_indicate.py::test_k6_restart_ramki_laptop_wysyla_plan_ponownie_do_5_s` | 0,03-0,07 s |
| stan po Spacji ponizej 1 s | `test_indicate.py::test_k7_spacja_zmienia_stan_ramki_w_ponizej_1_s_dwa_procesy`, `test_aplikacja_rano.py::test_k4_spacja_ramka_w_ponizej_1s_kolory_rowne_mapie_i_petla_okna` | maks. 9-35 ms |
| plan, kolory, kuweta po kuwecie, zmiana plytki | `test_k1_*`, `test_k2_*`, `test_ramka.py::test_k4_zmiana_plytki_4_0_5_ponizej_100_ms_i_zdarzenia` | K4 mediana 47 ms |

Wartosci zmierzone sa w wyjsciu `-s` - przepisz je do `t5_wynik.md` (nie samo `PASSED`).

**Czesc B - atrapa w sieci lokalnej + zapis ruchu (odstepstwo O8):** wszystkie pomiary paczek szly na 127.0.0.1. Na PC
"siec lokalna" = adres karty sieciowej PC (`ipconfig`, np. 192.168.x.x), ramka i program na tym samym komputerze - ruch
przechodzi przez stos sieciowy, ale nie przez kabel ani Wi-Fi. Prawdziwa siec = T15 (`ODLOZONE.md`).

1. Ramki (2 okna, procesy wlasne): `<K>\Polecenie.cmd -m ramka --rola W --sprzet atrapa --host <adres PC> --port 8765 --sterowanie-atrapy`
   i `--rola P --port 8767`. Alternatywa z konsola polecen (`plytka <n>`, `klawisz <nazwa>`, `stan`, `koniec`):
   `<K>\Polecenie.cmd narzedzia\atrapa_ramki.py --rola P --host <adres PC> --port 8767 --sterowanie`.
2. Posrednik z zapisem ruchu (po jednym na ramke):
   `PY -I <ODB>\narzedzia\posrednik_ruchu.py --sluchaj <adres PC>:8766 --cel <adres PC>:8765 --zapis <ROB>\ruch_ramka_w.bin`
   (ramka P: `--sluchaj <adres PC>:8768 --cel <adres PC>:8767 --zapis <ROB>\ruch_ramka_p.bin`).
3. `<K>\ustawienia.toml`, `[ramki]`: `port` = 8766 (port posrednika), `wieczorna_host` = `<adres PC>`. Uwaga: `[ramki]
   port` jest JEDEN dla obu ramek (sprawdzone w `ustawienia.py` i `indicate.py`), a obie atrapy stoja na jednym
   komputerze - dlatego posrednik ramki P musi sluchac na tym samym porcie pod innym adresem: `--sluchaj 127.0.0.1:8766
   --cel <adres PC>:8767`, `poranna_host` = `127.0.0.1` (posrednik ramki W: `--sluchaj <adres PC>:8766`).
4. Wieczor - 3 skany wieczorne przez program z paczki prowadzony sterownikiem T2 (sekcja `[ramki]` przechodzi z pliku
   wzoru do kopii ustawien sterownika; `set QT_QPA_PLATFORM=offscreen`):
   `<K>\Polecenie.cmd <ODB>\narzedzia\t2_wieczor.py --ustawienia-wzor <K>\ustawienia.toml --roboczy <ROB>\t5_wieczor --projekty <folder_cyrkon> --wybierz 1,3,8 --odstep 60 > <ROB>\t5_wieczor.log 2>&1`
   (ramka W ma dostac plan i kolory; w konsoli atrapy: `plytka 1`, `stan`,
   `klawisz enter` - klawisze ramki: `enter`, `backspace`, `zamknij_piec`, cyfry `0`-`9`; Spacja to klawisz laptopa, nie
   ramki - sprawdzone w `ramka\protokol.py`). Tryb poranny wybiera sie na ekranie
   (opcja `--rano` dziala tylko z `--atrapa` - sprawdzone w kodzie), wiec ramka P w programie z paczki bez czlowieka
   przy ekranie NIE jest sprawdzana - jej ruch pokrywa `test_aplikacja_rano.py` z czesci A i test `test_zz_k8`.
5. Zatrzymaj posredniki (Ctrl+C): zapisz wiersz `POSREDNIK koniec: polaczen N, ... bajtow ...` (N > 0 - inaczej program
   nie szedl przez posrednik i proba jest niewazna).
6. Czesc B NIE byla wykonana w rundzie poprawek (3 procesy w 3 oknach; posrednik i atrapa sprawdzone osobno na danych
   sztucznych - raport paczki) - pierwsze wykonanie zapisz krok po kroku. Gdy PC nie ma adresu sieci lokalnej (`ipconfig`)
   albo zapora odmowi nasluchu: 127.0.0.1 i wpis "NIE ZMIERZONO w sieci lokalnej" (O8).

**Dowody w `T5/`:** `t5_testy.log`, `t5_wynik.md`, `t5_siec_lokalna.md` (adres, porty, liczby z posrednikow, co widziala
atrapa). Plikow `ruch_ramka_*.bin` NIE dodawac do repo (zostaja w `<ROB>` do T9).

**Czas:** 40 min (A 10, B 30). **Ciezar:** lekki. **Rownolegle:** czesc A nie w czasie serii pomiarowej (progi 1 s i
100 ms; `test_k4` bywal niestabilny pod obciazeniem - E3-A8p, E3-A5 runda 3); porty 8765-8768 zajmuje jeden wykonawca.

**Pulapki:** ramka loguje tylko `ip METODA trasa -> status` na stderr (bez tresci) - dlatego posrednik; klucz `[ramki]
klucz` pusty = brak naglowka `X-Ramka-Klucz` (przy wpisanym kluczu ten sam w `--konfiguracja` ramki); ramka W pokazuje
tylko ostatni skan (decyzja koordynatora); zapora Windows moze zapytac o zgode na nasluch pod adresem karty - odmowa =
wpis "NIE ZMIERZONO w sieci lokalnej" i proba na 127.0.0.1 (nie obchodzic).

## T6 - Excel na sztucznym arkuszu

**Kryterium (plan):** 200 zapytan na 30 tys. wierszy; tryb "pytaj" i "cien" - 200 z 200; 0 zlych wierszy; log zgodny z
regula 6.

**Gdzie:** testy z `<REPO>` na kodzie programu z instalacji (`pytest_instalacja.py`); arkusz powstaje w pamieci z `narzedzia\arkusz_syntetyczny.py`
(`--wierszy 30000 --zapytan 200 --seed <n> --csv <plik>`; samo narzedzie tylko buduje arkusz i wypisuje liczniki).

**Kroki:**

```
call <K>\Polecenie.cmd narzedzia\arkusz_syntetyczny.py --wierszy 30000 --zapytan 200 > <ROB>\t6_arkusz.txt 2>&1
call <K>\Polecenie.cmd <ODB>\narzedzia\pytest_instalacja.py --st <ST> --wynik <ROB>\t6_zrodlo_kodu.txt -- <ST>\testy\test_excel.py -q -s -rA -p no:cacheprovider --rootdir <ST> > <ROB>\t6_excel.log 2>&1
call <K>\Polecenie.cmd <ODB>\narzedzia\pytest_instalacja.py --st <ST> --wynik <ROB>\t6_zrodlo_kodu_2.txt -- <ST>\testy\test_aplikacja_rano.py -q -s -rA -p no:cacheprovider --rootdir <ST> -k "test_k3_excel_pytaj or test_k3_excel_cien" > <ROB>\t6_aplikacja.log 2>&1
```

Warunek: ostatni wiersz kazdego przebiegu "WERDYKT ZRODLA KODU: INSTALACJA" (kod 0); werdykt "REPO" albo kod 3 = liczby
pochodza z kodu repo (zapisz jako odstepstwo O14).

| Liczba | Test (`test_excel.py::...`) | Zmierzone dotad (E3-A9) |
|---|---|---|
| 200 z 200 | `test_k1_200_zapytan_wlasciwa_klasa` | 200 z 200 |
| 0 zlych wierszy | `test_k1_zero_zapisow_w_zlym_wierszu`, `test_k5_zapis_dotyka_tylko_koloru_jednej_komorki` | 110 + 38 zapisow, 0 w zlym wierszu |
| log zgodny z regula 6 | `test_k3_log_csv_ma_pola_reguly_6` (pola `data;godzina;kuweta;folder;numer_zlecenia_b;arkusz;wiersz;kto_zatwierdzil`) | zgodny |
| tryb "pytaj" | `test_k4_domyslnie_pytaj_przed_zapisem`, `test_aplikacja_rano.py::test_k3_excel_pytaj_*` | - |
| tryb "cien" | `test_k4_tryb_cien_nie_zapisuje_niczego`, `test_k4_zapisz_cien_loguje_caly_piec`, `test_k3_excel_cien_*` | 0 zmian, 200 wpisow |

**Odstepstwo O9:** testy ida na atrapie arkusza w pamieci, bez programu Excel. Na PC jest Excel
(`C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE`) i `win32com`, ale nie ma narzedzia, ktore puszcza 200
zapytan przez `excel_com` na prawdziwym skoroszycie, a raport E3-A9 mowi wprost "prawdziwego Excela / COM nie
uruchamiano". Uruchamianie Excela wlasciciela z konta `<konto-PC>` bez jego decyzji pomijamy (wariant najbezpieczniejszy);
Excel na prawdziwym skoroszycie = T17 (`ODLOZONE.md`).

**Dowody w `T6/`:** `t6_arkusz.txt` (liczniki arkusza), `t6_excel.log`, `t6_aplikacja.log`, `t6_wynik.md`. Log Excela
z testow (kolumna `folder`) to dane sztuczne - mimo to nie kopiowac go do dowodow.

**Czas:** 15 min. **Ciezar:** lekki. **Rownolegle:** tak.

## T8 - Metryki

**Kryterium (plan):** raport jednym poleceniem na bazie z T2 i T3 - wartosci = policzone recznie.

**Gdzie:** `POL narzedzia\raport_metryk.py` na dwoch bazach (sciezki poprawione po recenzji, uwaga 4): (W) baza wieczoru
ze sterownika T2: `<ROB T2>\t2\dane\stanowisko.sqlite` (sterownik pisze do katalogu `--roboczy`, NIE do `<DANE>`
instalacji) - skopiuj do `<ROB>\baza_t2.sqlite`; (R) baza SE10 ze sterownika T3: `<ROB T3>\t3\baza\stanowisko.sqlite` -
skopiuj do `<ROB>\baza_t3.sqlite`. (Baza testu pytest w `<ROB T3>\t3_tmp\se10*` to INNA baza - tej nie uzywac.)

**Kroki:**

```
call <K>\Polecenie.cmd narzedzia\raport_metryk.py --baza <ROB>\baza_t2.sqlite --tryb wieczor --od <data T2> --do <data T2> --json <ROB>\t8_wieczor.json > <ROB>\t8_wieczor.txt
call <K>\Polecenie.cmd narzedzia\raport_metryk.py --baza <ROB>\baza_t3.sqlite --tryb oba --od 2026-11-17 --do 2026-11-19 --json <ROB>\t8_rano.json > <ROB>\t8_rano.txt
```

Kody: 0 = wszystko w progu, 3 = cos ponizej progu, 4 = brak danych, 2 = blad (kod 3 i 4 to nie jest FAIL testu T8 -
T8 sprawdza zgodnosc liczb, nie progi).

**Liczenie reczne (niezaleznie od `metryki.py`; zapytania przez `PY -I <ODB>\narzedzia\sql_odczyt.py --baza <plik> "<SELECT>"`,
definicje: `opisy_modulow/metryki.md`):**

| Metryka | Licznik / mianownik recznie |
|---|---|
| Falszywe alarmy | prace ze `status_gniazda` = `czerwony` w skanach `tryb` = `wieczor`, `status` = `przyjety`, z obowiazujaca decyzja `rodzaj` = `ok` (ostatnia decyzja pracy, po cofnieciach) / wszystkie takie prace czerwone z decyzja |
| Skany powtorzone | `SELECT status, count(*) FROM skany GROUP BY status`: (`zastapiony` + `do_powtorzenia` + `niezgodny_uklad` + `plytka_nie_z_trybu` + `blad`) / wszystkie skany okresu |
| Prace nieznane | prace z pustym `kandydat1_sha16` albo `kandydat1_pokrycie` < `[match] prog_ostrzezenia_pokrycie` (0,6) / prace |
| Top-1 / top-2 (rano) | piece zamkniete (`sesje_pieca.zamknieto IS NOT NULL`): `kandydat1_sha16` (top-2: takze `kandydat2_sha16`) = `sha16` projektu potwierdzonego / prace rozstrzygniete |
| Czas przy stanowisku | chwile z `skany.czas_analizy`, `decyzje.czas`, `zdarzenia` (zrodlo `ui`, `scanner/nowy_skan`); posiedzenie konczy przerwa ponad 10 min |
| Dni bez awarii | `zdarzenia` `program_start` bez wczesniejszego `program_stop` |

Dla bazy T2 (10 skanow) wykonawca liczy recznie WSZYSTKIE metryki wieczoru i wpisuje do `t8_recznie.md`: metryka,
zapytanie, licznik / mianownik, wartosc raportu, zgodne tak / nie. Dla bazy SE10: top-1, top-2, prace nieznane rano.

**Liczby kryterium:** n z n metryk zgodnych (wartosc i licznik) miedzy `t8_*.json` a `t8_recznie.md`. Punkt odniesienia:
E3-A10: 65 z 65 wierszy `OCZEKIWANE` (`test_metryki.py`, 106 passed) - uruchom tez
`<K>\Polecenie.cmd -m pytest <ST>\testy\test_metryki.py -q -p no:cacheprovider --rootdir <ST>`.

**Dowody w `T8/`:** `t8_wieczor.txt`, `t8_wieczor.json`, `t8_rano.txt`, `t8_rano.json`, `t8_recznie.md`, `t8_test_metryki.log`.

**Czas:** 45 min (reczne liczenie). **Ciezar:** lekki. **Rownolegle:** tak; PO T2 i T3.

**Pulapki:** metryki licza przez API sesji (decyzja obowiazujaca po cofnieciach, para "ponowny skan?" jako jeden albo
dwa wsady) - proste `count(*)` da inny wynik, trzeba liczyc wg definicji z `metryki.md`; domyslny okres to 7 dob
konczacych sie dzis, doba od 6:00 - dla SE10 podaj `--od` / `--do`; baza zbudowana sama sesja (SE10) nie ma zdarzen
`program_start` - "dni bez awarii" = "brak danych"; doba metryk zaczyna sie o 6:00 - T2 wykonany w nocy nalezy do doby
poprzedniej: podaj `--od <dzien przed>` `--do <dzien T2>`; baza T2 ze sterownika `t2_wieczor.py` ma decyzje "Ukruszona",
a decyzje "OK" tylko wtedy, gdy program dal falszywy alarm - gdy metryka "falszywe alarmy" daje w raporcie "brak danych",
regula jest taka: "brak danych" w raporcie = 0 z 0 w liczeniu recznym = ZGODNE (nie "NIE ZMIERZONO"); kazda inna para
(raport "brak danych", recznie n z m przy m > 0 albo odwrotnie) = niezgodne; M2 nie jest liczona (wymaga zmiany
schematu - decyzja wlasciciela).

## T9 - Dane osobowe

**Kryterium (plan):** wyszukanie nazw folderow zlecen w repo, logach, plikach wynikow, ruchu sieciowym do ramki -
0 trafien; nazwy tylko w `dane/` (baza, log Excela).

**Gdzie:** skrypt `<ODB>\narzedzia\t9_dane_osobowe.py` (interpreter bazowy `PY -I`). Lista nazw istnieje tylko w pamieci
skryptu; wypisywane sa liczby i `sha16`; czlon sciezki z nazwa albo czlonem nazwy jest wypisywany jako `<sha16:...>`.
Wykonuje sie NA KONCU (po T2-T8, T10, T11), bo przeszukuje ich wyniki. Kazdy przebieg zaczyna sie samotestem (wiersz
"Samotest: ... nieznalezionych 0"); samotest nieudany = kod 2 i "NIE ZMIERZONO" (nie ZAL).

**Skad nazwy:** `--nazwy-z <PC-katalog>\app\Prace_test` (15 folderow), `--nazwy-z <PC-katalog>\e3\a5i\t4\drzewo\Cyrkon`
(47 folderow), `--nazwy-z <PC-katalog>\t0\<nazwa>_wej\Cyrkon` kazdej instalacji roboczej, `--baza <DANE>\stanowisko.sqlite`
kazdej instalacji (tabele `zlecenia.folder`, `projekty.plik`), `--baza <baza SE10>`.

**Kroki (kazdy wynik do osobnego pliku przez `--wynik` - skrypt sam pisze plik ASCII z LF; NIE uzywac przekierowania
`>`, ktore daje CRLF; `T9` = `PY -I <ODB>\narzedzia\t9_dane_osobowe.py`, `N` = wspolne opcje `--nazwy-z ... --baza ...`,
`D` = `--dozwolone stanowisko.sqlite --dozwolone stanowisko.kopia_ --dozwolone log_excel.csv`):**

1. Repo: `PY -I <ODB>\narzedzia\t9_dane_osobowe.py N --repo <REPO> --json <DOW>\t9_repo.json --wynik <DOW>\t9_repo.txt`
   (tresc i sciezki plikow sledzonych + historia od `2537f6f` do `HEAD`: opis, autor i tresc zmian kazdego commita,
   `--od` domyslnie `2537f6f`). PRZED `git add` dowodow:
   `T9 N --cel <worktree>\Ramki\etap3\odbior_koncowy\dowody --wynik <ROB>\t9_dowody.txt` BEZ `--dozwolone` - wymagany
   kod 0; po scaleniu galezi dowodow powtorz krok 1.
2. Logi: `T9 N --cel <DANE>\logi --cel <PC-katalog>\koordynator\robocze\odbior D --dozwolone t4_surowe --dozwolone t10_surowe --wyklucz \zrodla\ --wynik <DOW>\t9_logi.txt`
   (dla kazdej instalacji roboczej). Dozwolone (przeszukiwane, liczone osobno): bazy T2 / T3 i ich kopie, log Excela,
   surowe wyniki T4 / T10 (`t4\t4_surowe_*.json`, `t10\t10_surowe_metryki.json`, `t10_surowe.log` - zawieraja sciezki
   zlecen i zostaja w `<ROB>`; wzor `--dozwolone` NIE moze pasowac do zadnego pliku z listy dowodow - dlatego `t10_surowe`,
   nie `t10_`: nazwa wstrzyknieta do `T10\t10_wynik.txt` dawala przy wzorze `t10_` kod 0; do `<DOW>`
   ida tylko po kontroli opisanej w T4 i T10). Wykluczone (nieczytane, liczba w pierwszym wierszu): kopie zrodel
   `\zrodla\`. Kazde inne trafienie w `robocze\odbior` = FAIL, dopoki nie wskazesz, ze plik jest dana wejsciowa
   (wtedy dopisz `--dozwolone`, powtorz i opisz w `t9_wynik.md`); log programu i dowody nigdy nie sa dozwolone.
3. Pliki wynikow: `T9 N --cel <DANE>\wyniki --cel <DANE>\podglady --cel <DANE>\pula_cache --cel <DANE>\do_dofrezowania_biezaca.csv --wynik <DOW>\t9_wyniki.txt`
   (katalog, ktorego nie ma w instalacji, pomin w poleceniu i wpisz to do `t9_wynik.md` - skrypt konczy kodem 2).
4. Ruch do ramki: `T9 N --cel <ROB T5>\ruch_ramka_w.bin --cel <ROB T5>\ruch_ramka_p.bin --wynik <DOW>\t9_ruch.txt`
   + test `<K>\Polecenie.cmd -m pytest <ST>\testy\test_indicate.py <ST>\testy\test_ramka.py -q -rA -p no:cacheprovider --rootdir <ST> -k test_zz_k8`
   (caly ruch testow przez posrednik w pamieci; zmierzone w A8i: 0 trafien w ok. 3450 zapisach).
5. Dowod "nazwy tylko w `dane/`": `T9 N --cel <DANE> --cel <ROB T3>\t3\baza D --dozwolone \kopie\ --wynik <DOW>\t9_dane.txt`
   (drugi cel = baza SE10 ze sterownika T3: ma nazwy sztuczne, ktore sa w `N` przez `--baza <baza SE10>`; proba
   recenzenta 21.11: 33 trafienia dozwolone, kod 0)
   - "Trafienia w miejscach dozwolonych" > 0 (baza zawiera nazwy - to dowod, ze skrypt umie je znalezc),
   "TRAFIENIA calych nazw poza miejscami dozwolonymi" = 0. NIE podawac `--dozwolone stanowisko.` - obejmuje takze
   `logi\stanowisko.log` (proba: nazwa w logu + taki wzor = kod 0, falszywe ZAL; z `D` kod 1).
6. Proba dodatnia skryptu = samotest w kazdym przebiegu (kazda nazwa znaleziona we wlasnych bajtach UTF-8, cp1250,
   UTF-16 LE, `\uXXXX`, wielkimi i malymi literami, bez znakow diakrytycznych) ORAZ krok 5 (nazw nie wpisujemy recznie
   do zadnego pliku). Gdy samotest poda "nieznalezionych" > 0 albo krok 5 da 0 trafien dozwolonych w bazie SE10
   (`<ROB T3>\t3\baza`): wynik calego T9 = "NIE ZMIERZONO"; 0 trafien dozwolonych w `<DANE>` jest poprawne, gdy
   `sql_odczyt.py --baza <DANE>\stanowisko.sqlite "SELECT count(*) FROM zlecenia"` daje 0 (`pula_wpisow = false`) -
   zapisz te liczbe. Przy "NIE ZMIERZONO" szukaj przyczyny (kodowanie, pusta baza SE10, zla sciezka `--baza`).

**Liczby kryterium:** suma "TRAFIENIA calych nazw poza miejscami dozwolonymi" z krokow 1-5 = 0 (kod wyjscia 0 w kazdym;
kod 2 = NIE ZMIERZONO). Werdykt skryptu: "ZAL (0 trafien)", "ZAL - czlony do wyjasnienia: N" albo "FAIL".
"Czlony nazw do wyjasnienia" (pojedyncze slowa z nazw o co najmniej 5 znakach, np. zwykle slowa) NIE sa kryterium, ale
przy N > 0 test nie jest zamkniety, dopoki wykonawca nie opisze w `t9_wynik.md` kazdej grupy (plik albo liczba plikow,
`sha16` czlonu, wyjasnienie: slowo pospolite / nazwisko) - nie wpisujac samego czlonu. Nazwisko poza `dane/` = FAIL.
"Nieprzeszukane" (zip, pdf, png, xlsx, pliki > 300 MB; sama sciezka jest sprawdzana) i "zmian plikow binarnych z
nieprzeszukana trescia" w historii: podaj liczby; ZIP wydania nie zawiera danych (sprawdza T13 i lista plikow paczki).

**Dowody w `T9/`:** `t9_repo.txt`, `t9_repo.json`, `t9_dowody.txt` (katalog `dowody\` przed `git add`, bez
`--dozwolone`), `t9_logi.txt`, `t9_wyniki.txt`, `t9_ruch.txt`, `t9_dane.txt`, `t9_wynik.md`.

**Czas:** 30 min. **Ciezar:** lekki (czyta pliki; baza i logi male). **Rownolegle:** tak; po pozostalych testach.

**Pulapki:** nie zapisywac do pliku niczego poza wynikiem skryptu (nie robic `dir` katalogow zlecen do logu);
`--nazwy-z` wskazuje katalog NADRZEDNY folderow zlecen; nazwy krotsze niz 4 znaki sa pomijane i liczone (liczba w
pierwszym wierszu - gdy > 0, opisz); skrypt nie rozroznia wielkosci liter (takze polskich) ani znakow diakrytycznych
(nazwa zapisana bez ogonkow tez jest trafieniem), szuka w UTF-8, cp1250, UTF-16 LE i `\uXXXX`; spacja, `_` i `-`
nazwy pasuja takze do siebie nawzajem oraz do `+` i `%20` (poprawka po uwadze 45 recenzji rundy 2; proba na nazwie
sztucznej: cala nazwa znaleziona w 7 z 8 wariantow separatora, przed poprawka 2 z 8; nieznajdowany wariant: dwie
spacje zamiast jednej - wtedy zglaszane sa tylko czlony "do wyjasnienia"). Nie szuka: UTF-16 BE, cp852, iso-8859-2,
postaci rozlozonej NFD (litera + osobny znak diakrytyczny), `%XX` (poza `%20`), `\xNN`, `\uXXXX` zapisanego
podwojnie (JSON w JSON: `\\u0142`), wnetrza plikow spakowanych, tresci plikow binarnych w historii git - nazwa w
takiej postaci moze dac tylko trafienia czlonow ASCII ("do wyjasnienia"), dlatego kazda grupe czlonow trzeba opisac.
Czlony nazw: 1-2 znakowe i same numery nie sa ani szukane, ani maskowane; 3-4 znakowe z litera sa tylko maskowane
w wypisywanych sciezkach (nie liczone - `--min-czlon 3` wlacza ich liczenie); pliki sztucznego drzewa A5i maja nazwy
fikcyjne - trafienia ich czlonow w repo to zwykle slowa. `--dozwolone` / `--wyklucz` to podciag sciezki (wielkosc
liter bez znaczenia; `*` i `?` w obrebie jednego czlonu sciezki) - wzor za szeroki ukrywa trafienia.

## T13 - Higiena repo

**Kryterium (plan):** diff wzgledem poczatku etapu - tylko pliki z list paczek; nowe pliki ASCII; brak STL i danych.

**Poczatek etapu 3:** commit `2537f6f` (`2537f6fdf33c79993998225f9c644ca553ccbccc`, 16.11.2026 00:05, "Plan etapu 3: pelna
aplikacja stanowiska (do akceptacji wlasciciela, bramka G0)"). Ustalony poleceniem
`git log --follow --format="%h %ad %s" --date=iso -- Ramki/plan_etap3_pelna_aplikacja_2026-11-16.md` (ostatni wiersz =
pierwszy commit pliku planu; jest przodkiem `main`: `git merge-base --is-ancestor 2537f6f main`).

**Kroki:**

```
PY -I <ODB>\narzedzia\t13_higiena.py --repo <REPO> --od 2537f6f --do <commit wydania> --json <DOW>\t13_wynik.json > <DOW>\t13_wynik.txt
git -C <REPO> diff --stat 2537f6f <commit wydania> > <DOW>\t13_diff_stat.txt
```

Skrypt (tylko odczyt): lista plikow z `git diff --name-status --no-renames`; kazda sciezka musi pasowac do przedrostka z
`narzedzia\t13_dozwolone.txt` (grupa `E3` = paczki etapu 3; `R58`, `R59` = prace wlasciciela spoza etapu 3 scalone w tym
samym czasie - liczone osobno); nowe pliki grupy E3: ASCII, LF (`.cmd` / `.bat` / `.ps1`: CRLF), bez STL poza
`modele_plytek`, bez plikow danych, nie wieksze niz 1024 KB. Kod 0 = 0 naruszen.

**Liczby kryterium:** wiersz `NARUSZENIA (grupa E3 i sciezki poza listami): N` (N = 0), wiersz `nie-ASCII: napisy
ekranu, odstepstwo O11 ...: k plikow z 7 na liscie` (z liczba wierszy w kazdym) i tabela grup (nowe / zmienione /
usuniete). Kazde naruszenie = poprawka przez wlasciwa paczke albo wyjatek zapisany decyzja koordynatora w `RAPORT.md`.

**Proba na obecnym `main` 9ba9e91 (20.11, to jeszcze NIE odbior):** 579 plikow zmienionych, 503 nowe; E3: 164 nowe /
22 zmienione; R58: 242 / 4; R59: 97 / 34 / 16 usunietych; sciezek poza listami 0; **naruszen 7** - wszystkie "nie ASCII"
w nowych plikach: `stanowisko/dzien_skanera.py`, `dzien_skanera_kroki.toml`, `dzien_skanera_rdzen.py`, `statusy.py`,
`ui/napisy.py`, `ui/napisy_rano.py`, `testy/test_dzien_skanera.py` (napisy ekranu i krokow po polsku ze znakami
diakrytycznymi). Wynik: `T13/proba_main_9ba9e91.txt`.

**Decyzja koordynatora 20.11 nr 5 (zamyka POTRZEBUJE 6) = odstepstwo O11:** 7 nowych plikow nie-ASCII z napisami ekranu
(polskie znaki widziane przez technika - styl programu przyjety przez wlasciciela w paczkach A3 / A6) to odstepstwo jawne,
nie naruszenie. Lista plikow: `narzedzia\t13_wyjatki_ascii.txt` (zmiana listy = decyzja koordynatora w `RAPORT.md`).
Skrypt wypisuje je OSOBNO - wiersze "nie-ASCII: napisy ekranu, odstepstwo O11" z liczba wierszy i bajtow nie-ASCII w kazdym
pliku - i nadal zglasza jako naruszenie KAZDY inny nowy plik ze znakiem spoza ASCII. Wynik bez naruszen:
"ZAL z odstepstwem O11".

**Proba po zmianie skryptu na kopii integracyjnej a2236c1 (20.11, to jeszcze NIE odbior; `T13/proba_integ_a2236c1.txt`):**
608 plikow zmienionych, 530 nowych; E3: 191 nowych / 24 zmienione; odstepstwo O11: 7 plikow z 7 na liscie (wierszy
nie-ASCII: `dzien_skanera.py` 109, `dzien_skanera_kroki.toml` 134, `dzien_skanera_rdzen.py` 102, `statusy.py` 240,
`ui/napisy.py` 66, `ui/napisy_rano.py` 111, `testy/test_dzien_skanera.py` 45); **naruszen 1**:
`Ramki/stanowisko/stanowisko/ui/kandydaci.py` - nie ASCII (2 bajty) - plik spoza listy siedmiu, wiec zgloszony zgodnie z
decyzja; do rozstrzygniecia przed odbiorem (poprawka pliku przez wlasciwa paczke albo dopisanie do listy decyzja
koordynatora).

**Odstepstwo O10:** "tylko pliki z list paczek" jest sprawdzane na poziomie katalogow paczek (plik `t13_dozwolone.txt`),
nie listy pojedynczych plikow z kazdego zlecenia - zlecenia paczek fali 1-3 nie sa w repo. Kontrola dokladna dla paczek
z 20.11 (zlecenia w `<PC-katalog>\koordynator\zlecenia\`): `git diff --stat main...e3/<kod>` wobec listy plikow zlecenia -
robi koordynator przy scalaniu. Pliki grup R58 / R59 (STL do zamowienia, PDF, ZIP pakietow) nie sa wynikiem etapu 3.

**Dowody w `T13/`:** `t13_wynik.txt`, `t13_wynik.json`, `t13_diff_stat.txt`.

**Czas:** 10 min. **Ciezar:** lekki. **Rownolegle:** tak; uruchomic na commicie wydania i jeszcze raz po dodaniu dowodow.

**Dowody a T13 (uwaga 9 recenzji):** logi z przekierowania `cmd >` maja CRLF (zmierzone: 15 CR w 15 wierszach), a czesc
wyjsc ma znaki spoza ASCII - takie pliki dodane do repo daja naruszenia w drugim przebiegu T13. Dlatego przed `git add`
dowodow: `PY -I <ODB>\narzedzia\dowody_lf.py --katalog <DOW> --napraw --wynik <DOW>\dowody_lf.txt` (kod 0), a wykonawca
T13 przed drugim przebiegiem uruchamia to samo BEZ `--napraw` na calym katalogu `dowody\` (kod 0 = 0 naruszen). Wyniki
T13 pisz przez `--json` i przekierowanie, po czym przepusc przez `dowody_lf.py` jak kazdy inny dowod.

---

## Podzial na wykonawcow i kolejnosc

Warunek startu: paczki A11s, A11i, A11w, P14, A11d scalone; `<ZIP_N>` i `<ZIP_N1>` zbudowane; `<REPO>` zalozone.
Kazdy wykonawca: wlasna instalacja robocza `<PC-katalog>\t0\w<n>` (z `/testy`), wlasna galaz `e3/odb-w<n>`, rozlaczne
katalogi dowodow.

| Wykonawca | Testy (w tej kolejnosci) | Katalogi dowodow | Instalacja | Tor | Lacznie |
|---|---|---|---|---|---|
| W1 "instalacja" | T0 -> T12 -> T1 | `T0/`, `T12/`, `T1/` | `t0\czysta` | tor 1 (ciezkie po kolei) | ok. 2 h |
| W2 "pomiary" (jedyna sesja pomiarowa) | T10 -> T4 -> T2 -> T11 | `T10/`, `T4/`, `T2/`, `T11/` | `t0\w2` | tor 2 (jedna seria naraz) | ok. 3,5-4 h |
| W3 "poranek i odpornosc" | T3 -> T6 -> T5 -> T7 | `T3/`, `T6/`, `T5/`, `T7/` | `t0\w3` | lekkie; T7 `test_silnik` pojedynczo | ok. 2 h |
| W4 "zestawienia" (moze byc W3 po przerwie albo koordynator) | T13 -> T8 (po T2 i T3) -> T9 (na koncu) | `T13/`, `T8/`, `T9/` | korzysta z baz W2 i W3 (kopie) | lekkie | ok. 1,5 h |

Kolejnosc i zaleznosci:

1. Koordynator: budowa paczek, `<REPO>`; decyzje do POTRZEBUJE 1-6 sa podjete 20.11 i wpisane w sekcjach T2, T3, T7, T11,
   T13, T4 (naruszenie `ui/kandydaci.py` w T13 nie wystepuje juz na f5c3e01 - proba generalna 21.11: 0 naruszen).
   Zaraz po T0 jedno uruchomienie kontroli zestawu T14 na instalacji z paczki (dowod `T14\t14_sprawdz_paczka.txt`):
   `set QT_QPA_PLATFORM=offscreen` i
   `<K>\Polecenie.cmd <REPO>\Ramki\etap3\t14\symulator_t14.py --sprawdz --program . > <ROB>\t14_sprawdz_paczka.txt 2>&1`
   - ostatni wiersz "SPRAWDZENIE T14 BEZ EKRANU: zgodne 22 z 22 krokow", kod 0 (wykonane w probie generalnej 21.11: 8,3 s).
2. W1 zaczyna T0 (tor 1). Rownolegle W2 i W3 zakladaja instalacje robocze - **po kolei przez tor 1** (instalacja probna =
   ciezki krok), wiec realnie: T0 -> instalacja `w2` -> instalacja `w3` -> T12 -> T1.
3. W2: T10 i T4 nie potrzebuja programu w oknie - startuja zaraz po instalacji `w2`; T4 i T10 nigdy jednoczesnie
   (jedna sesja pomiarowa naraz); T2 i T11 po nich. T1 (tor 1) i seria W2 (tor 2) moga isc jednoczesnie tylko przy wolnym
   RAM >= 6000 MB przed startem T4 - inaczej T4 czeka na koniec T1.
4. W3: T3, T6 od razu po instalacji `w3`; czesc A T5 i testy czasowe T7 poza oknami serii pomiarowej W2 (albo powtorka
   po serii, z zapisem obu wynikow).
5. W4: T13 kiedykolwiek; T8 po T2 i T3; T9 na samym koncu, po zebraniu dowodow wszystkich wykonawcow.
6. Koordynator: `RAPORT.md`, FAIL -> paczki poprawek -> powtorka testu (stary dowod zostaje z dopiskiem `_proba1`).

## Kolejnosc i czasy T0-T13 - skrot dla koordynatora (stan 21.11)

Czasy = czas wykonawcy z zapisem dowodow; w nawiasie czas samych polecen zmierzony w probach 21.11 (PC malo obciazony),
gdy byl mierzony. "Seria pomiarowa" = test, ktorego liczby zaleza od obciazenia PC (jedna naraz na calym PC).

| Test | Ciezar | Czas | Po czym | Rownolegle z |
|---|---|---|---|---|
| T0 | ciezki (instalacja) | 20 min (polecenia: 52,5 s + 5,8 s + starty ok. 1 min) | budowa paczek | lekkimi; nie z T1 / T12 na tej samej instalacji |
| T14 kontrola zestawu | lekki | 1 min (8,3 s) | T0 | wszystkim |
| T12 | ciezki | 30 min (A: 2 min 40 s; B: 2 min 45 s, osobna instalacja) | T0 | lekkimi; czesc B wszystkim poza seria pomiarowa |
| T1 | ciezki | 30-45 min na przebieg (zmierzone interpreterem wersji: 27 min 20 s), 2 przebiegi | T0 (instalacja z `/testy`) | nie z seria pomiarowa (testy czasowe) |
| T10 | ciezki, seria pomiarowa | 40-60 min | instalacja robocza | nie z T2, T4, T11, T1 |
| T4 | ciezki, seria pomiarowa | 45 min | instalacja robocza | nie z T2, T10, T11, T1 |
| T2 | ciezki, seria pomiarowa | 30 min (sterownik 11-13 min; proba skrocona 89 s) | instalacja robocza | nie z T4, T10, T11, T1 |
| T11 | czesc B ciezka, seria pomiarowa | 60 min (B: ok. 35 min) | instalacja robocza | B nie z T2, T4, T10 |
| T3 | lekki | 15 min (sterownik 11 s; testy uzupelniajace 2 s + 73 s) | instalacja z `/testy` | wszystkim poza seria pomiarowa |
| T6 | lekki | 15 min (`test_excel.py` przez `pytest_instalacja.py`: ok. 20 s) | instalacja z `/testy` | wszystkim |
| T5 | lekki; czuly na obciazenie | 40 min (A: ok. 1 min; B: 30 min, 3 okna) | instalacja z `/testy` | nie w czasie serii pomiarowej; porty 8765-8768 jeden wykonawca |
| T7 | sredni (`test_silnik` pojedynczo) | 45 min | instalacja z `/testy` | poza seria pomiarowa; proby B na wlasnej instalacji |
| T13 | lekki | 10 min (1,3 s) | commit wydania; drugi raz po dodaniu dowodow | wszystkim |
| T8 | lekki | 45 min (reczne liczenie; raporty ok. 2 s) | T2 i T3 | wszystkim |
| T9 | lekki | 30 min (repo: 14 s) | wszystkie pozostale | wszystkim; na samym koncu |

Rownolegle mozna puscic najwyzej: 1 serie pomiarowa (T10 -> T4 -> T2 -> T11, razem ok. 3-3,5 h) + 1 ciezki krok
instalacyjny / pytest (T0 -> T12 -> T1, ok. 2 h; T1 NIE w czasie T2 / T4 - czeka albo idzie przed nimi) + testy lekkie
(T3, T6, T13, T8, T9 w dowolnej chwili; T5 czesc A i testy czasowe T7 w oknach miedzy seriami pomiarowymi). Najkrotsza
sciezka zegarowa: ok. 4 h przy 3 wykonawcach (seria pomiarowa wyznacza czas); wszystko po kolei: ok. 9 h.

## Stan sprawdzenia polecen (21.11, runda 1 recenzji)

"Instalacja probna" = `<PC-katalog>\t0\proba\Stanowisko`, wersja 0.3.1 zainstalowana z paczki zbudowanej z f5c3e01
(`main` bcd0678 + P15), `<REPO>` = klon tego commita; "proba generalna" = osobny wykonawca, ktory przeszedl T0, T1, T12,
T13 i sterowniki na tej instalacji 21.11; "ta paczka" = wykonawca i pomocnik E3-ODB w rundzie poprawek. Wyniki prob tej
paczki leza poza repo (katalog roboczy paczki). To NIE sa wyniki odbioru.

| Test | Polecenie planu | Wykonane | Gdzie | Wynik proby |
|---|---|---|---|---|
| T0 | kroki 2-8 | tak (proba generalna) | instalacja probna | kody 10 / 0; sumy 210 z 210; samokontrola ZIELONA (ok 17, ostrzezenia 4); starty 5 z 5 + 1 kod 0 |
| T0 | krok 9 w nowej postaci (`findstr` na `pip.log`) | tak (proba generalna podala te postac) | instalacja probna | 2 wiersze |
| T12 | czesc A, kroki 1-5 | tak (proba generalna) | instalacja probna | kody 0 / 0; 6 z 6 sum ustawien rownych |
| T12 | czesc B, kroki 1-8 | tak (ta paczka) | osobna instalacja w katalogu roboczym paczki | kody 11 z 11 zgodne; kopia = baza co do tresci, nie co do sumy calego pliku |
| T1 | kroki 1-4 | tak (proba generalna) | instalacja probna | `1 failed, 2202 passed, 9 skipped` w 27 min 20 s (2212 = `--collect-only`); nieudany: `test_b1_blokada_znika_razem_z_procesem` (pada w srodowisku wersji 6 z 6, interpreterem bazowym 2 z 2 passed); testy czasowe: 0 nieudanych |
| T1 | krok 5 (interpreter bazowy) | NIE w tej rundzie | - | punkt odniesienia z 20.11 istnieje |
| T2 | sterownik (proba skrocona `--plytki 3 --odstep 5`), wersja po poprawkach | tak (ta paczka) | instalacja probna i kopia repo `main` + P15 | 3 z 3; ubytki 12: czerwone 5, zolte 7, zielone 0; lista = prawda TAK; ponowien 0; kod 0 (oba przebiegi) |
| T2 | sterownik, pelne 10 x 60 s | NIE | - | - |
| T2 | testy uzupelniajace (2 polecenia) | tak (ta paczka) | instalacja probna | polecenie 1: kod 0; 2 passed, 27 deselected in 119.12s (0:01:59); polecenie 2: kod 0; 1 passed, 88 deselected in 10.01s; wczesniej `--collect-only` w probie generalnej: wybor `-k` trafia (2 i 1 test) |
| T3 | sterownik z `--wymagaj-100`, wersja po poprawkach | tak (ta paczka) | instalacja probna (wersja po uwadze 3) i kopia repo (wersja koncowa, po uwadze 19) | 32 z 32, "ZAL z odstepstwem O5", kod 0 (3 z 3 przebiegow) |
| T3 | 2 polecenia testow uzupelniajacych | tak (proba generalna) | instalacja probna | 33 passed; 60 passed |
| T7 | czesc A, przypadki 2-6 przez `pytest_instalacja.py` | tak (ta paczka) | instalacja probna | przypadek 2: 4 passed; 3: 3 passed; 4: 3 passed (+ `test_k5` z `test_indicate.py` w T5); 5: 2 passed; 6: 1 + 30 passed (w tym caly `test_p14_baza_zajeta.py`); wszystkie kod 0, zrodlo kodu: INSTALACJA |
| T7 | czesc A, przypadek 1 (zabicie silnika; 2 polecenia) | tak (ta paczka) | instalacja probna | `test_aplikacja.py`: kod 0; 2 passed, 27 deselected in 2.87s; zrodlo kodu: INSTALACJA; `test_silnik.py`: pierwszy przebieg kod 1 (2 passed, 1 error: brak pliku ustawien w katalogu programu wersji); po poprawce narzedzia kod 0; 3 passed, 66 deselected in 85.59s (0:01:25); zrodlo kodu: INSTALACJA |
| T7 | czesc B, proby 1-3 | NIE | - | - |
| T10 | polecenie z `--limit 2` | tak (ta paczka) | instalacja probna | patrz raport paczki (sekcja "Runda 1 recenzji") |
| T10 | pelne 40 skanow | NIE | - | - |
| T11 | czesc A z `--limit 2` | tak (ta paczka) | instalacja probna | kod 0, `auto_uklad.json` powstal |
| T11 | czesc B (40 skanow przez aplikacje) | NIE | - | `symulator_skanera.py --help` na instalacji: `--zrodla` przyjmuje wiele katalogow |
| T11 | krok 3 (2 zapytania `sql_odczyt.py`) | tak (ta paczka) | baza proby T2 | kod 0 |
| T11 | krok 4 (testy) | tak (ta paczka) | instalacja probna | kod 0; 45 passed, 174 deselected, 121 s |
| T4 | 3 polecenia `metryki_pula.py` | tylko `czas --help` (ta paczka) | instalacja probna | kod 0; pomiarow NIE wykonano |
| T5 | czesc A, polecenie 1 przez `pytest_instalacja.py` | tak (ta paczka) | instalacja probna | kod 0, 20 x PASSED, zrodlo kodu: INSTALACJA; K5: 500 z 500, 0 powtorek |
| T5 | czesc A, polecenie 2 przez `pytest_instalacja.py` | tak (ta paczka) | instalacja probna | kod 0; 4 passed; zrodlo kodu: INSTALACJA (60 modulow, 0 z repo) |
| T5 | czesc B (atrapa na adresie karty, posrednik, 3 skany) | NIE | - | posrednik i narzedzie T9 sprawdzone osobno na danych sztucznych |
| T6 | `arkusz_syntetyczny.py` | tak (ta paczka) | instalacja probna | kod 0; 30000 wierszy, 200 zapytan |
| T6 | `test_excel.py` przez `pytest_instalacja.py` | tak (ta paczka) | instalacja probna | kod 0, 129 x PASSED, zrodlo kodu: INSTALACJA (17 modulow, 0 z repo) |
| T6 | polecenie 3 (`test_aplikacja_rano.py -k ...`) przez `pytest_instalacja.py` | tak (ta paczka) | instalacja probna | kod 0; 2 passed; zrodlo kodu: INSTALACJA |
| T8 | `raport_metryk.py` x 2 | tak (ta paczka) | instalacja probna, bazy prob T2 i T3 tej paczki | kod 3 i 3 (ponizej progu - to nie FAIL T8) |
| T8 | `sql_odczyt.py` | tak (ta paczka) | baza proby T2 | kod 0 |
| T8 | `test_metryki.py` | tak (ta paczka) | instalacja probna | kod 0; 106 passed |
| T9 | kroki 1-5 | tak (ta paczka; krok 1 na worktree paczki, kroki 2-5 na danych sztucznych) | kopia repo / katalog roboczy | kody 0; proby ujemne kod 1 |
| T9 | krok 4, test `test_zz_k8` | tak - w ramach T5 czesc A polecenie 1 | instalacja probna | PASSED |
| T13 | `t13_higiena.py` | tak (proba generalna, wersja sprzed poprawki; ta paczka - wersja po poprawce) | kopia repo f5c3e01 | sprzed poprawki: 0 naruszen; po poprawce (liczenie samotnych CR): 1 naruszenie - `Ramki/stanowisko/raporty/E3-A6_2026-11-18.md`, 1 samotny CR |
| T13 | `dowody_lf.py` | tak (ta paczka) | 4 logi prob | 3 z 4 z CRLF naprawione; plik `.sqlite` zgloszony jako zakazany |
| T14 | kontrola zestawu `--sprawdz` | tak (proba generalna) | instalacja probna | zgodne 22 z 22 krokow, kod 0, 8,3 s |

Niewykonane ani razu (pierwsze wykonanie bedzie w odbiorze - zapisywac krok po kroku): T2 pelny (10 x 60 s); T4 pomiary; T5 czesc B; T7 czesc B (proby 1-3); T10 pelny; T11 czesc B (40 skanow przez aplikacje); T1 krok 5.

## Lista "sprawdzone przez --help / w kodzie" (stan `main` 9ba9e91 i galezi z 20.11)

| Co | Jak sprawdzone |
|---|---|
| `narzedzia\symulator_skanera.py`: `--folder --zrodla --ile --odstep --rownolegle --zle uciety --seed --dziennik --analiza --projekty --wyjscie --ustawienia`; pola dziennika `zapisy`, `analizy` | `--help` (rozpoznanie) + kod (wiersze 284-396) |
| `narzedzia\metryki_P3a.py`: `--skany --projekty --wyjscie --nazwa --procesy --ustawienia --limit --wzorzec` | kod (argparse, wiersze 135-144) |
| `narzedzia\metryki_pula.py`: podpolecenia `przygotuj czas jakosc r59 ranking pamiec`; `czas` i `jakosc`: `--katalog --wyjscie --nazwa --pamiec --linie --wpisow --plytek --procesy --ustawienia` | `czas --help` i `jakosc --help` uruchomione przeze mnie |
| `narzedzia\metryki_P3a.py`: pola wyniku `plate_match.skanow`, `plate_match.wyrownanie_ok`, `top1_per_scenariusz.<s>.prac` / `top1_bledny`, wiersz `PRACE CA...: N, z czerwonym M` | kod (wiersze 188-233) |
| `Samokontrola.cmd` (wzor, `e3/a11i`): przekazuje opcje (`%*`), sam dodaje `--ustawienia` i `--sumy`; dane instalacji w `<K>\dane` | tresc pliku wzoru; `instalator.py` wiersze 10, 1243 |
| `[ramki] port` jeden dla obu ramek; klawisze ramki `enter backspace zamknij_piec 0-9` | `ustawienia.py` 105-107, `indicate.py` 1267-1271, `ramka\protokol.py` 42 |
| baza SE10 w pliku `<katalog testu>\dane\stanowisko.sqlite` | `test_session_rano.py`, klasa `Stanowisko` |
| `narzedzia\raport_metryk.py`: `--od --do --tryb --baza --ustawienia --json`; kody 0 / 3 / 4 / 2 | `--help` (rozpoznanie) |
| `narzedzia\auto_uklad.py`: `--skany --wyjscie --procesy --limit --ustawienia` | `--help` (rozpoznanie) |
| `narzedzia\arkusz_syntetyczny.py`: `--wierszy --zapytan --seed --csv` | `--help` (rozpoznanie) |
| `narzedzia\atrapa_ramki.py`: `--rola --port --host --sterowanie --bez-konsoli --limit-lacznosci --konfiguracja`; `python -m ramka`: `--rola --sprzet --host --port --konfiguracja --sterowanie-atrapy --gadatliwie` | `--help` (rozpoznanie) |
| `stanowisko.aplikacja`: `--ustawienia --zamknij-po --atrapa --rano` (`--rano` tylko z `--atrapa`) | kod (argparse, wiersze 1652-1655) |
| `stanowisko.samokontrola` (galaz `e3/a11s`): `--ustawienia --sumy --json --bez-sieci`; kody 0 / 1 / 2 | kod (argparse, wiersze 1380-1384) |
| `zainstaluj.cmd` (galaz `e3/a11i`): `/katalog /python /skrot /testy /bez-sieci /bez-pauzy`; kody 0-11 | plik `.cmd` wiersz 3; raport A11i p. 12.7 |
| `Polecenie.cmd`, `Stanowisko.cmd` (wzory, `e3/a11i`): przekazuja argumenty, `cd` do `wersje\<wersja>\program` | tresc plikow |
| `narzedzia\zbuduj_wydanie.py` (`e3/a11i`): `--wyjscie --wersja --kola --rewizja --zrodlo --commit --data --pobierz-kola`; paczka = `program\{stanowisko, modele_plytek, narzedzia, ramka, instrukcje, instalacja}`, bez `testy\` | kod (wiersze 9-12, 33, 332-341) |
| wszystkie nazwy testow pytest wymienione w planie: 19 plikow, 64 nazwy funkcji (takze przedrostki z `-k`) | `grep "def <nazwa>"` w `testy*.py` (`main` 9ba9e91; `test_p14_baza_zajeta.py` na galezi `e3/p14`): 0 brakow |
| tabele `zlecenia` (`folder`), `skany` (`uklad`, `uklad_zrodlo`, `uklad_zgodny`, `czas_pliku`, `czas_analizy`, `czas_s`, `status`), `prace` (`skan_id`, `status_gniazda`, `kandydat1_sha16`), `zdarzenia` (`zrodlo`, `typ`, `skan_id`, `dane`) | `stanowisko\baza.py` (wiersze 80-210) + rozpoznanie |
| katalogi danych i liczby plikow (T2, T4, T10, T11) | listowanie 20.11: R59_P2 24 + 24, R59_P3a 16 + 16, r54_P2 24 + 24, r54_P3a 16 + 16, pula400 `plytki` 10 + 10, `a5i\t4\eksport` 10, `Prace_test` 15 folderow, `a5i` Cyrkon 47 folderow |
| `symulator_t14.py` (`e3/a11d`): `wieczor` / `rano`, `--sprawdz --program --scenariusz --opoznienie --dziennik --zamknij-po` | kod (argparse, wiersze 354-360) |
| skrypty `odbior_koncowy\narzedzia\*.py` | proby na danych sztucznych - `E3-ODB_raport_2026-11-20.md` |
| sterowniki `t2_wieczor.py`, `t3_poranek.py`: opcje wg `--help`; obiekty okna `osoba_0`, `plytka_<id>`, `przycisk_ukruszona`, `odp_odrzuc_ponowny_skan`, `przycisk_przelacz_tryb`, `przycisk_zamknij_piec`, `pytanie_zamknij_mimo`, `zamknij_mimo_tak`, `tabela_kompletne`, `tabela_braki`; `StanAplikacji.analiza.od` / `.sha16`; `aplikacja.main` opcje `--ustawienia --zamknij-po` | proby 20.11 na kopii integracyjnej a2236c1 (T3: caly SE10; T2: proby skrocone z prawdziwa analiza) - `E3-ODB_raport_2026-11-20.md`, sekcja "Etap 2"; NIE sprawdzone na instalacji z paczki |
| `Polecenie.cmd`, `Stanowisko.cmd` (wzory w `instalacja\wzory`, kopia integracyjna a2236c1): `cd /d wersje\<wersja>\program`, python z `venv\Scripts`, `PYTHONPATH` puste; `Stanowisko.cmd` = `-m stanowisko.aplikacja --ustawienia <K>\ustawienia.toml %*` | tresc plikow (etap 2) |
| `stanowisko.aplikacja` na kopii integracyjnej: `--ustawienia --atrapa --rano --zamknij-po` (wiersze 1658-1661) | kod (etap 2) |

"Rozpoznanie" = sprawdzenie wykonane 20.11 przez pomocnicze sesje odczytu tej paczki (`--help` uruchomione na `main`
9ba9e91); pozycje bez dopisku sprawdzilem sam w plikach.

## Zrodla liczb kryteriow - skrot

| Test | Liczba kryterium | Zrodlo |
|---|---|---|
| T0 | kody 0 / 10 / 0; samokontrola bledy 0; SHA-256 | kody wyjscia `.cmd`, wyjscie `Samokontrola.cmd`, `certutil` |
| T1 | 0 failed, 0 errors, pominiete = 9 znanych | ostatni wiersz i sekcja `-rs` logu pytest |
| T2 | 10 z 10; start < 1 s; mapa mediana <= 40 s; przerwa <= 200 ms; lista | `t2_wynik.json` sterownika `t2_wieczor.py`: `obsluzone_zgodnie_z_prawda`, `start_analizy_od_zapisu_s` (doslownie), `mapa_od_zapisu_s` (gorne ograniczenie), `petla_okna` (doslownie od pierwszego tykniecia okna), `lista_do_dofrezowania` + `kolory_prac` (kolory z ekranu, przeoczone), `werdykty` z wierszem "T2 LACZNIE" |
| T3 | 32 z 32 wierszy; listy kompletnych i brakow | `t3_wynik.txt` sterownika `t3_poranek.py`: wiersz "WERDYKT T3" (n z 32 liczone z ekranu), kolumna "ekran" dla 10 wierszy z listami; uzupelniajaco `test_se10[R01..R32]` |
| T4 | top-1 n z n; plytka maks. s; szczyt MB | `metryki_pula jakosc` / `czas`: `top1_projekt`, `top1_wpis`, `plytki[].czas_s`, `szczyt_mb` |
| T5 | 5 z 5, 0 powtorek; plan <= 5 s; Spacja < 1 s | wyjscie `-s` testow `test_k5`, `test_k6`, `test_k7` (127.0.0.1, O8) + `t5_zrodlo_kodu_*.txt` (kod z instalacji) |
| T6 | 200 z 200; 0 zlych; log regula 6 | testy `test_k1_*`, `test_k3_*`, `test_k4_*` + `t6_zrodlo_kodu.txt` (kod z instalacji) |
| T7 | 6 z 6 przypadkow | testy z tabeli + proby reczne + tabela komunikatow |
| T8 | n z n metryk zgodnych | `raport_metryk --json` wobec `t8_recznie.md` |
| T9 | 0 trafien calych nazw | wyjscie `t9_dane_osobowe.py` |
| T10 | 40 z 40; top-1 dobrze n z n; czerwone na calych 0 | `metryki_P3a`: `zbiorczo.plate_match`, `top1_per_scenariusz.dobrze`, wiersz `PRACE CALE` |
| T11 | uklad 40 z 40; zielone przy zlym 0 (i pozycja 7 z T2); kolumna `uklad` niepusta | baza `skany`, `prace`; `auto_uklad.json`; `t2_wynik.json` |
| T12 | 1 polecenie; 3 sumy ustawien rowne; kopia bazy | kody `.cmd`, `certutil`, pliki kopii, `PRAGMA user_version` |
| T13 | naruszen 0 | wyjscie `t13_higiena.py` |
