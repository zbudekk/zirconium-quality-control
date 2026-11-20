# Plan testow koncowych etapu 3 (T0-T13)

Paczka E3-ODB, 20.11.2026. Zrodlo kryteriow: `Ramki/plan_etap3_pelna_aplikacja_2026-11-16.md`, sekcja 7 (kryteria ponizej
sa przepisane doslownie). Plan jest napisany dla stanu "`main` po scaleniu paczek A11s, A11i, A11w, P14, A11d";
miejsca oznaczone **[DO POTWIERDZENIA PO SCALENIU]** trzeba sprawdzic na scalonym `main` (nazwa pliku albo opcja mogla
sie zmienic w rundach poprawek). Testow jeszcze nikt nie wykonal - to jest przepis.

Zasady wykonania (obowiazuja kazdego wykonawce):

- Test nieudany = wpis **FAIL** z liczba i logiem. Nie pomijac, nie oslabiac, nie powtarzac "az wyjdzie" bez zapisu
  kazdej proby. Krok niewykonalny = wpis "NIE ZMIERZONO" z powodem, nie puste pole.
- Liczniki, nie same procenty (np. 10 z 10).
- Dane osobowe: w dowodach, logach i wiadomosciach tylko `sha16` i numery kuwet z danych sztucznych. Nazw folderow i
  plikow zlecen nie wypisywac (takze z `<PC-katalog>\app\Prace_test`). Zapytania do bazy tylko przez
  `narzedzia\sql_odczyt.py` (odrzuca tabele z nazwami).
- Dowody: male pliki tekstowe / JSON w `Ramki/etap3/odbior_koncowy/T<nr>/` (kazdy wykonawca tylko w swoich katalogach
  `T<nr>`). Bez STL, baz, zapisow ruchu, ZIP-ow - te zostaja w `<ROB>`.
- Ciezki krok tylko przez blokade (`wspolne.md`): `powershell -NoProfile -ExecutionPolicy Bypass -File
  <PC-katalog>\koordynator\narz\ciezki.ps1 -Kto <kod> [-Tor 2] -Polecenie "<linia cmd z cd /d i przekierowaniem>"`.
  Tor 2 = seria pomiarowa (T2, T4, T10, T11 - jedna naraz na calym PC). Wynik kazdego przebiegu dopisywac do pliku od
  razu (PC bywa restartowany).

## Oznaczenia

| Znak | Znaczenie |
|---|---|
| `PY` | `<PC>\AppData\Local\Programs\Python\Python312\python.exe` (Python 3.12.10) |
| `<ZIP_N>`, `<ZIP_N1>` | paczki wydania `<PC-katalog>\wydania\Stanowisko_<N>.zip` i `Stanowisko_<N+1>.zip` (buduje koordynator, p. "Krok wspolny") |
| `<P1>`, `<P2>` | rozpakowane paczki: `<PC-katalog>\t0\paczka_N`, `<PC-katalog>\t0\paczka_N1` |
| `<K>` | katalog instalacji z paczki: `<PC-katalog>\t0\<nazwa>` (T0: `czysta`; kazdy wykonawca ma wlasny: `w1`, `w2`, `w3`) |
| `<DANE>` | `<K>\dane` (baza `stanowisko.sqlite`, `logi\stanowisko.log`, `wyniki\`, `log_excel.csv`) - **[DO POTWIERDZENIA PO SCALENIU]**: instalator trzyma ustawienia i dane poza katalogiem wersji; dokladna sciezke wypisuje `Samokontrola.cmd` i jest w `<K>\ustawienia.toml`, sekcja `[sciezki]` |
| `<REPO>` | czysta kopia `main` z TEGO SAMEGO commita, z ktorego zbudowano `<ZIP_N>`: `<PC-katalog>\t0\repo` (zaklada koordynator: `git -C <PC-katalog>\qc worktree add --detach <PC-katalog>\t0\repo <commit>`) |
| `<ST>` | `<REPO>\Ramki\stanowisko` |
| `<ODB>` | `<REPO>\Ramki\etap3\odbior_koncowy` (skrypty: `<ODB>\narzedzia\`) |
| `<DOW>` | katalog dowodow testu w worktree wykonawcy: `Ramki\etap3\odbior_koncowy\T<nr>\` |
| `<ROB>` | katalog roboczy poza repo: `<PC-katalog>\koordynator\robocze\odbior\T<nr>\` |
| `POL` | `<K>\Polecenie.cmd` = Python wersji biezacej uruchomiony w `<K>\wersje\<wersja>\program` (sa tam `stanowisko\`, `narzedzia\`, `ramka\`, `modele_plytek\`; NIE ma `testy\`) |

Ktore testy ida na instalacji z paczki, a ktore wymagaja repo:

| Test | Instalacja z paczki (`<K>`) | Repo (`<REPO>`) |
|---|---|---|
| T0, T12 | tak (to jest przedmiot testu) | nie |
| T1 | interpreter i pakiety z `<K>` (`zainstaluj.cmd /testy`) | testy i kod z `<REPO>` |
| T2, T11 | program przez `Stanowisko.cmd`, symulator przez `POL` | tylko testy uzupelniajace |
| T4, T10 | narzedzia pomiarowe przez `POL narzedzia\...` | nie |
| T3, T5, T6, T7 | interpreter z `<K>` | testy z `<REPO>` |
| T8 | `POL narzedzia\raport_metryk.py` | skrypt `sql_odczyt.py` z `<ODB>` |
| T9 | cele: `<DANE>`, logi, dowody | repo jako cel, skrypt z `<ODB>` |
| T13 | nie | tak (`git`, skrypt z `<ODB>`) |

## Krok wspolny (koordynator, przed T0): paczki wydania

Zrodlo: raport `Ramki/stanowisko/raporty/E3-A11i_2026-11-20.md`, p. 12.8 (galaz `e3/a11i`).

```
cd /d <PC-katalog>\qc\Ramki\stanowisko
<PC-katalog>\koordynator\narz\py.cmd narzedzia\zbuduj_wydanie.py --wyjscie <PC-katalog>\wydania --kola <PC-katalog>\wydania\kola
<PC-katalog>\koordynator\narz\py.cmd narzedzia\zbuduj_wydanie.py --wyjscie <PC-katalog>\wydania --kola <PC-katalog>\wydania\kola --wersja <N+1>
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
`<konto-PC>` (nowego konta Windows nie da sie zalozyc bez administratora); "bez internetu" = opcja `/bez-sieci`
(pip `--no-index`, tylko kola z paczki) - fizycznie sieci nie odcinamy. Pelne T0 na czystym komputerze = laptop
stanowiska (`ODLOZONE.md`, D4).

**Kroki** (okno `cmd.exe`; kazdy krok z przekierowaniem do `<ROB>\t0_<nr>.log`; kody wyjscia zapisz `echo KOD=%errorlevel%`):

1. `<PC-katalog>\koordynator\narz\ram.cmd` - zapisz wolny RAM. Krok 3 jest ciezki: uruchom go przez `ciezki.ps1` (tor 1).
2. Sumy paczki: `certutil -hashfile <ZIP_N> SHA256` - porownaj z `<ZIP_N>.sha256` i z wierszem w
   `SHA256SUMS_wydania.txt`. Rozpakuj:
   `powershell -NoProfile -Command "Expand-Archive -LiteralPath <ZIP_N> -DestinationPath <PC-katalog>\t0\paczka_N"`.
3. `<P1>\zainstaluj.cmd /katalog <PC-katalog>\t0\czysta /python %PY% /bez-sieci /bez-pauzy`
   Oczekiwane: **kod 10** ("WSTRZYMANA": wersja zainstalowana, samokontrola czeka na foldery w `ustawienia.toml`);
   na ekranie sumy "202 z 202" (liczba plikow moze byc inna - zapisz) i pakiety "73 z 73". Czas 75-210 s.
4. Wpisz foldery w `<K>\ustawienia.toml` (jak w "Krok wspolny"; katalogi musza istniec).
5. Ponownie krok 3. Oczekiwane: **kod 0**, "juz zainstalowana i zgodna", samokontrola ZIELONA. Czas 6-15 s.
6. `<K>\Samokontrola.cmd --bez-sieci` - oczekiwane: kod 0, wiersz podsumowania "ZIELONA" z licznikami (ok / ostrzezenia /
   bledy = n / m / 0). Kody: 0 zielona, 1 bledy, 2 nie dalo sie wykonac. Zapisz tez wersje JSON:
   `<K>\Polecenie.cmd -m stanowisko.samokontrola --ustawienia <K>\ustawienia.toml --json --bez-sieci > <ROB>\t0_samokontrola.json`
   **[DO POTWIERDZENIA PO SCALENIU]**: czy `Samokontrola.cmd` przekazuje `--json`.
7. Start programu: `set QT_QPA_PLATFORM=offscreen` i `<K>\Stanowisko.cmd --atrapa --zamknij-po 5` (kod 0), potem
   `<K>\Stanowisko.cmd --zamknij-po 20` (prawdziwy kontroler, kod 0). W `<DANE>\logi\stanowisko.log` 0 wierszy `Traceback`.
8. Kontrola srodowiska wersji (latka A11w): `<K>\Polecenie.cmd -c "import stanowisko, sys; print(sys.modules.get('_wmi', 'brak'))"`
   ma wypisac `None`.
9. Kontrola "bez internetu": w logu kroku 3 nie ma adresu `pypi.org` ani `https://` w wierszach pip (`findstr /i "pypi https://" <log>` = 0 wierszy).

**Liczby kryterium:** (a) program startuje = kody 0 w kroku 7 (2 z 2); (b) samokontrola = kod 0 i "bledy 0" w kroku 6;
(c) sumy = zgodnosc SHA-256 ZIP w kroku 2 (1 z 1) + licznik "sumy n z n" instalatora w kroku 3.

**Dowody w `T0/`:** `t0_kroki.md` (tabela krok / polecenie / kod / czas / wynik), `t0_sha256.txt`, `t0_zainstaluj_1.log`,
`t0_zainstaluj_2.log`, `t0_samokontrola.txt`, `t0_samokontrola.json`, `t0_start.txt`.

**Czas:** 20 min. **Ciezar:** ciezki (krok 3; tor 1). **Rownolegle:** nie z T1 i T12 (ten sam tor); z lekkimi tak.

**Pulapki:** `zainstaluj.cmd` bez `/bez-pauzy` czeka na klawisz; kod 10 przy pierwszej instalacji to wynik poprawny
(decyzja koordynatora 20.11 nr 1), nie FAIL; sesja bez ekranu wymaga `QT_QPA_PLATFORM=offscreen`; brak folderu MillBox i
ramek = OSTRZEZENIE, nie blad; kod 5 = program juz dziala albo baza zajeta (zamknij inne instalacje w tym samym `<K>`).

## T12 - Aktualizacja

**Kryterium (plan):** wersja N -> N+1 -> powrot do N - jedno polecenie; ustawienia zachowane; baza zmigrowana z kopia.

**Gdzie:** instalacja z paczki, katalog `<K>` = `<PC-katalog>\t0\czysta` po T0 (z baza po co najmniej jednym starcie
programu). **Dane:** `<ZIP_N1>`; do czesci B paczka z probna migracja (nizej).

**Kroki:**

1. Przed: `certutil -hashfile <K>\ustawienia.toml SHA256` -> `t12_ustawienia_przed.txt`; `<K>\Wersje.cmd /bez-pauzy` -> lista
   wersji; `python <ODB>\narzedzia\sql_odczyt.py --baza <DANE>\stanowisko.sqlite "SELECT count(*) FROM skany"`.
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
(`WERSJA_SCHEMATU` bez zmian w etapie 3), wiec zwykla aktualizacja niczego nie migruje. Migracje sprawdza sie na paczce
probnej z dodatkowa pozycja `MIGRACJE[2]` zbudowanej z kopii drzewa (`zbuduj_wydanie.py --zrodlo <kopia> --data <data
commita> --wersja <X>`); przepis: `<PC-katalog>\koordynator\robocze\a11i\proby2_0_budowa.sh`, caly scenariusz dwoch
powrotow: `proby2_B.sh` w tym samym katalogu **[DO POTWIERDZENIA PO SCALENIU: nazwy plikow w `robocze\a11i`]**.
Oczekiwane: po aktualizacji obok bazy jest kopia sprzed migracji (identyczna bajtowo z baza sprzed aktualizacji -
porownaj SHA-256), `PRAGMA user_version` wzrasta, powrot zglasza kod 8 i po `/przywroc-kopie` baza = kopia. Paczki
probnej NIE publikowac i nie wpisywac do `SHA256SUMS_wydania.txt`. Uzupelniajaco: `test_instalacja.py` (69 testow) i
`test_baza.py` w T1.

**Liczby kryterium:** jedno polecenie = 1 wywolanie `zainstaluj.cmd` (kod 0) i 1 wywolanie `Wroc_do_poprzedniej.cmd`
(kod 0; w czesci B 2 wywolania - opisac); ustawienia = 3 sumy SHA-256 identyczne (przed / po N+1 / po powrocie);
baza = kopia istnieje i ma sume bazy sprzed migracji (czesc B), liczba skanow bez zmian (czesc A).

**Dowody w `T12/`:** `t12_kroki.md`, `t12_ustawienia_sumy.txt`, `t12_wersje_przed_po.txt`, `t12_zainstaluj_N1.log`,
`t12_wroc.log`, `t12_migracja_B.md`.

**Czas:** 30 min (czesc A 15, czesc B 15). **Ciezar:** ciezki (tor 1). **Rownolegle:** nie z T0 i T1; po T0, przed
uzyciem `czysta` do czegokolwiek innego.

**Pulapki:** `Wroc_do_poprzedniej.cmd` bez `/tak` pyta T / N (kod 11 = anulowany); kod 5 = program dziala; stare wersje
i kopie bazy nie sa kasowane (1,4 GB na wersje - po tescie zostawic, sprzata koordynator).

## T1 - Testy programu

**Kryterium (plan):** pytest caly - 0 failed, 0 errors; pominiete tylko znane z punktu odniesienia.

**Gdzie:** interpreter i pakiety srodowiska wersji (`<K>` zainstalowane z `/testy`), testy i kod z `<REPO>` (ten sam
commit co paczka). Zrodlo polecenia: raport `E3-A11w_2026-11-20.md`, p. 7.

**Kroki:**

1. `<P1>\zainstaluj.cmd /katalog <K> /python %PY% /bez-sieci /bez-pauzy /testy` (kod 0).
2. `copy <ST>\ustawienia.przyklad.toml <ST>\ustawienia.toml` (plik ignorowany przez git).
3. `<K>\Polecenie.cmd -c "import stanowisko, sys; print(sys.modules.get('_wmi', 'brak'))"` -> `None`.
4. Przez `ciezki.ps1` (tor 1), jedna linia:
   `<K>\Polecenie.cmd -X faulthandler -m pytest <ST>\testy -q -p no:cacheprovider --rootdir <ST> -o faulthandler_timeout=900 < NUL > <ROB>\t1_pytest.log 2>&1`
5. Drugi przebieg interpreterem bazowym (porownanie z punktem odniesienia, ta sama blokada):
   `cmd /c "cd /d <ST> && <PC-katalog>\koordynator\narz\py.cmd -m pytest -q -p no:cacheprovider -rs > <ROB>\t1_pytest_bazowy.log 2>&1"`

**Liczby kryterium:** ostatni wiersz logu `N passed, S skipped` - `failed` i `error` maja nie wystapic. Pominiete: lista
z `-rs` (dopisz `-rs` takze w kroku 4) porownana z punktem odniesienia: `main` bf00921 = 1829 / 9 / 0
(`<PC-katalog>\koordynator\log\pytest_bazowy_bf00921.log`), `main` 9ba9e91 = 1831 / 9 / 0. Oczekiwana liczba testow po
scaleniu paczek: 1831 + testy A11s, A11i (91), A11w, A11d, P14 - dokladna liczba = suma z raportow paczek po ostatniej
rundzie; kazdy pominiety test spoza listy 9 znanych = FAIL kryterium.

**Dowody w `T1/`:** `t1_pytest.log`, `t1_pytest_bazowy.log`, `t1_pominiete.txt` (9 pozycji z powodem),
`t1_wynik.md` (passed / skipped / failed, czas, commit, wolny RAM przed startem).

**Czas:** 30-45 min na przebieg (interpreter bazowy ok. 20-29 min). **Ciezar:** ciezki (tor 1). **Rownolegle:** nie.

**Pulapki:** bez `--rootdir` pytest bierze za katalog glowny `<PC-katalog>` (zle identyfikatory, `-k` lapie nazwy
katalogow); testy importuja pakiet `stanowisko` z `<REPO>`, nie z `<K>` - dlatego ten sam commit; zawieszenie oceniac po
stanie procesu, nie po zegarze (pod obciazeniem `test_silnik.py` trwa ponad 8 min); zjawisko PC `0xC0000142` /
`0xc000070a` = opisac i powtorzyc przebieg (oba logi zostaja); testy czasowe wrazliwe na obciazenie: `test_ramka::test_k4`,
`test_ui_wieczor::test_6`, `test_aplikacja::test_f` (raport E3-T0p). Calego pytest w srodowisku wersji nikt jeszcze nie
uruchomil (A11w: "nie zmierzono").

## T2 - Wieczor od poczatku do konca

**Kryterium (plan):** symulator wrzuca 10 plytek co 60 s: uklady R59 i R54, okragle, 1 niezgodny uklad, 1 drgniecie,
1 plik uciety - 10 z 10 obsluzonych zgodnie z prawda; start analizy ponizej 1 s od zapisu; mapa do 40 s (mediana); okno
bez przerw ponad 200 ms; lista "do dofrezowania" = prawda.

**Gdzie:** program z paczki przez `<K>\Stanowisko.cmd`, symulator przez `POL`. **BRAK NARZEDZIA (B1):** nie istnieje
sterownik, ktory w jednym przebiegu (a) mierzy przerwy petli okna w programie uruchomionym z paczki, (b) zapisuje chwile
startu analizy, (c) podaje decyzje "Ukruszona" zgodnie z prawda i porownuje liste "do dofrezowania". Program nie zapisuje
chwili startu analizy ani przerw petli (sprawdzone w kodzie: tabela `skany` ma `czas_pliku`, `czas_analizy`, `czas_s` z
dokladnoscia 1 s; pomiar 200 ms jest tylko w testach). Ponizej przepis zlozony z gotowych narzedzi (czesci A-C), ktory
mierzy 4 z 5 liczb wprost, a "lista do dofrezowania" i "okno" - testami uzupelniajacymi. Pelny pomiar w jednym
przebiegu wymaga sterownika `t2_wieczor.py` (opis w `E3-ODB_raport_2026-11-20.md`, POTRZEBUJE 1).

**Dane (katalogi nadrzedne, prawda = plik `.json` obok kazdego skanu, klucze `plytka`, `numer`, `prace[].drgniecie`,
`prace[].ubytki`, `prace[].poza_gniazdem`):**

| Skladnik zestawu | Skad | Ile |
|---|---|---|
| uklad R59, kwadratowe i okragle | `<PC-katalog>\app\dane_ref\syntetyczne_R59_P2` (24 skany) i `syntetyczne_R59_P3a` (16) | 5: 3 wieczorne kwadratowe, 2 okragle wieczorne |
| uklad R54 | `<PC-katalog>\app\dane_ref\syntetyczne_r54_P2` (24) i `syntetyczne_r54_P3a` (16) | 2: 1 kwadratowa, 1 okragla |
| 1 drgniecie | skan z P3a, w ktorego prawdzie co najmniej jedna praca ma `drgniecie` = prawda | 1 |
| 1 niezgodny uklad | `<PC-katalog>\r59\program\Ramki\stanowisko\dane\straznik_stan_obecny` (8 skanow) albo nowy z `POL narzedzia\straznik_R59.py --projekty <Cyrkon> --wyjscie <ROB>\straznik --seedy 1 --zachowaj` | 1 |
| 1 plytka poranna (blokada `plytka_nie_z_trybu`) | `syntetyczne_R59_P2`, wzorzec `skan_poranna_n*` | 1 |
| 1 plik uciety | robi symulator: `--zle uciety` (plik dodatkowy `zly_NN_uciety.stl`, 60 % bajtow pierwszego zrodla) | +1 (11. plik) |

Wybrane 10 skanow skopiuj do `<ROB>\zestaw10\` (z plikami prawdy), spisz `t2_zestaw.md`: nr, wzorzec nazwy skanu plytki,
uklad z prawdy, oczekiwany status (`przyjety` / `do_powtorzenia` / `niezgodny_uklad` / `plytka_nie_z_trybu`), liczba prac,
liczba prac z ubytkiem. Projekty: `folder_cyrkon` = kopia `<PC-katalog>\app\Prace_test`.

**Czesc A - program z paczki + symulator (10 z 10, mapa, start):**

1. Pusta baza: nowa instalacja robocza albo pusty `<DANE>`. `set QT_QPA_PLATFORM=offscreen`.
2. Okno 1 (tor 2, proces odlaczony): `<K>\Stanowisko.cmd --zamknij-po 1500 > <ROB>\t2_program.log 2>&1`
3. Okno 2, po 60 s od startu programu (pula zbudowana - w logu wiersz o puli):
   `<K>\Polecenie.cmd narzedzia\symulator_skanera.py --folder <folder_eksportu_skanera> --zrodla <ROB>\zestaw10 --ile 10 --odstep 60 --rownolegle 1 --zle uciety --seed 1 --dziennik <ROB>\t2_symulator.json`
   **[DO POTWIERDZENIA]**: `--zrodla` przyjmuje katalog i bierze pliki w kolejnosci nazw; ile i w ktorym miejscu staje
   plik uciety (`--help` i dziennik, pole `zapisy`).
4. Po zamknieciu programu (kod 0) policz:
   - statusy: `python <ODB>\narzedzia\sql_odczyt.py --baza <DANE>\stanowisko.sqlite "SELECT id, status, uklad, uklad_zrodlo, uklad_zgodny, czas_pliku, czas_analizy, czas_s FROM skany ORDER BY id"`
     i porownaj z `t2_zestaw.md` (10 z 10); plik uciety: `SELECT typ, count(*) FROM zdarzenia WHERE zrodlo='scanner' GROUP BY typ`
     (ma byc 1 x `plik_odrzucony`, 10 x `nowy_skan`) **[DO POTWIERDZENIA: nazwy kolumn `zrodlo`, `typ` w `zdarzenia`]**;
   - mapa: dla kazdego skanu `czas_analizy - czas_pliku` (rozdzielczosc 1 s) i `czas_s`; mediana z 10 ma byc <= 40 s;
     podaj tez maksimum i wartosc pierwszej plytki (pierwsza liczy linie brzegu od zera: 63-68 s w raportach A5 / A5i);
   - log: `findstr /c:"przyjety jako" <DANE>\logi\stanowisko.log` (10 wierszy minus skany nieprzyjete - zgodnie z
     zestawem), `findstr /r /c:"proces silnika" /c:"uruchomienia procesu roboczego nieudana" /c:"KnownDlls" <log>` (0).
5. Start analizy ponizej 1 s - ten sam zestaw przez obserwator i silnik bez okna (istniejacy pomiar S1 z E3-A2):
   `<K>\Polecenie.cmd narzedzia\symulator_skanera.py --folder <ROB>\eksport_s1 --zrodla <ROB>\zestaw10 --ile 10 --odstep 60 --rownolegle 1 --seed 1 --analiza --projekty <folder_cyrkon> --wyjscie <ROB>\s1_wyniki --dziennik <ROB>\t2_start.json`
   Liczba: `analizy[].start_od_konca_zapisu_s` - maksimum z 10 ma byc < 1 s (zmierzone w A2: 0,337-0,392 s).
   **Odstepstwo O3:** to pomiar modulow `scanner` + `silnik` bez okna; w pelnym programie chwila startu analizy nie jest
   zapisywana (brak B1).

**Czesc B - okno bez przerw ponad 200 ms (testy z `<REPO>` interpreterem wersji; prog 200 ms bez `E3A3_LUZNE`):**

```
set E3A3_DANE_REF=<PC-katalog>\app\dane_ref\syntetyczne_R59_P2
set E3A3_PROJEKTY=<folder_cyrkon>
<K>\Polecenie.cmd -m pytest <ST>\testy\test_aplikacja.py -q -s -p no:cacheprovider --rootdir <ST> -k "test_skany_odniesienia_przez_cala_aplikacje_w_petli_qt or test_f_petla_qt_bez_przerw_podczas_analizy_10_plytek" > <ROB>\t2_petla.log 2>&1
<K>\Polecenie.cmd -m pytest <ST>\testy\test_ui_wieczor.py -q -s -p no:cacheprovider --rootdir <ST> -k "test_6_petla_okna_bez_przerw_10_plytek_po_19_prac" >> <ROB>\t2_petla.log 2>&1
```

Liczba: w wyjsciu `-s` wiersz "najdluzsza przerwa petli Qt N ms (prog 200 ms)"; 3 testy, kazdy `passed`. **Odstepstwo O4:**
prawdziwa analiza w petli okna jest mierzona na 3 plytkach (test odniesienia), 10 plytek na analizie sztucznej.

**Czesc C - lista "do dofrezowania" = prawda:** lista powstaje tylko z decyzji technika "Ukruszona" (kontroler), wiec bez
sterownika (B1) w czesci A bedzie pusta - to nie jest wynik testu. Do czasu sterownika: `test_f` z czesci B sprawdza
`len(do_dofrezowania_biezaca) == 10`, `test_session_wieczor.py` (caly plik) sprawdza reguly listy. Wpis w raporcie:
"lista = prawda: zmierzone testami na danych sztucznych, przez program z paczki NIE ZMIERZONO (brak B1)" - chyba ze
koordynator zleci sterownik przed T2.

**Dowody w `T2/`:** `t2_zestaw.md`, `t2_symulator.json`, `t2_start.json`, `t2_skany.tsv`, `t2_zdarzenia.tsv`,
`t2_petla.log`, `t2_wynik.md` (tabela 5 liczb kryterium: wartosc, zrodlo, ZAL / FAIL / NIE ZMIERZONO).
Baze z czesci A zostaw w `<DANE>` - potrzebna do T8 i T9.

**Czas:** 75 min (przygotowanie zestawu 20, czesc A 25, krok 5: 20, czesc B 10). **Ciezar:** ciezki, seria pomiarowa
(tor 2). **Rownolegle:** nie z T4, T10, T11 ani z pelnym pytestem (czasy i przerwy petli zaleza od obciazenia).

**Pulapki:** symulator domyslnie zapisuje 4 pliki naraz - zawsze `--rownolegle 1`; program uruchamiac tylko przez
`Stanowisko.cmd`; COMMIT SQLite w watku okna potrafi przekroczyc 200 ms przy zajetym dysku (E3-T0p: 226 ms w 1500 probach);
pod obciazeniem plytka dochodzi do 46,8 s (E3-A5) - zapisz wolny RAM i co jeszcze liczylo; plytka poranna w trybie
wieczornym = pytanie `plytka_nie_z_trybu` i 0 zielonych (to wynik zgodny z prawda).

## T3 - Poranek od poczatku do konca

**Kryterium (plan):** scenariusz SE10 z A6 przez ekran: 3 piece, dofrezowany zab, poprawka, dwuznaczna, nieznana - listy
kompletnych i brakow zgodne z tabela oczekiwan w 100 % wierszy.

**Gdzie:** testy z `<REPO>` interpreterem wersji. **BRAK NARZEDZIA (B2):** SE10 istnieje tylko na poziomie sesji
(`testy\test_session_rano.py`: `TABELA_SE10` = 32 wiersze R01-R32, dane `testy\dane_sesji\rano\se10.json`, udawany zegar
17-19.11.2026, bez okna). Przez ekran przechodzi INNY scenariusz (`scenariusz_poranny()`: piec z 3 plytkami po 23 prace).
Odtworzenia SE10 przez okno / kontroler `Aplikacja` nie ma (POTRZEBUJE 2).

**Kroki (to, co da sie zmierzyc dzis):**

```
<K>\Polecenie.cmd -m pytest <ST>\testy\test_session_rano.py -q -rA -p no:cacheprovider --rootdir <ST> -k "se10" --basetemp <ROB>\t3_tmp > <ROB>\t3_se10.log 2>&1
<K>\Polecenie.cmd -m pytest <ST>\testy\test_ui_rano.py <ST>\testy\test_aplikacja_rano.py -q -rA -p no:cacheprovider --rootdir <ST> > <ROB>\t3_ekran.log 2>&1
```

**Liczby kryterium:** `t3_se10.log`: 33 `PASSED` (32 wiersze `test_se10[R01]`..`[R32]` + `test_se10_tabela_kompletna`) =
"32 z 32 wierszy tabeli"; wiersze z listami kompletnych i brakow: R11, R14, R15, R17, R21, R22, R28, R29, R30, R31 (10 z 10).
`t3_ekran.log`: w szczegolnosci `test_k4_zamknij_piec_kompletne_i_braki_rowne_wynikowi_A6` i
`test_k1_prawdziwy_kontroler_trzy_plytki_przez_skaner_i_petla_okna` = `PASSED`; zmierzone w A7: kompletne 24 = 24, braki 8 = 8.

**Odstepstwo O5:** kryterium "SE10 przez ekran" jest mierzone w dwoch kawalkach (SE10 na poziomie sesji + ekran na innym
scenariuszu). Wpis w raporcie: "SE10 przez ekran: NIE ZMIERZONO (brak B2)", dopoki nie powstanie test / sterownik.

**Dowody w `T3/`:** `t3_se10.log`, `t3_ekran.log`, `t3_wynik.md`. Katalog `<ROB>\t3_tmp` zostaw (baza SE10 do T8 -
`--basetemp` zachowuje pliki tymczasowe testu).

**Czas:** 15 min. **Ciezar:** lekki (2 pliki testow; przy wolnym RAM < 3000 MB czekac). **Rownolegle:** tak, poza seria
pomiarowa z testami czasowymi (`test_k4_spacja...` ma prog 1 s).

**Pulapki:** czesc wierszy SE10 sprawdza API, nie ekran (R12 / R13 plan ramki, R32 dane osobowe); `--basetemp` kasuje
wskazany katalog przed startem - podaj katalog tylko do tego celu.

## T7 - Odpornosc

**Kryterium (plan):** zabicie silnika w trakcie analizy; zamkniecie programu w polowie wieczoru; brak folderu "Cyrkon";
brak sieci; brak ramki; baza zajeta - za kazdym razem komunikat z PW zal. F i dalsza praca; stan odtworzony z bazy.

**Gdzie:** testy z `<REPO>` interpreterem wersji (czesc A) + 3 proby reczne na programie z paczki (czesc B).

**Czesc A - testy (jedna linia na przypadek; log `<ROB>\t7_<nr>.log`, opcje wspolne
`-q -rA -p no:cacheprovider --rootdir <ST>`):**

| Nr | Przypadek | Testy (`<ST>\testy\...`) |
|---|---|---|
| 1 | zabicie silnika | `test_aplikacja.py -k "test_zabity_proces_analizy_komunikat_i_nastepny_skan or test_silnik_nie_startuje_skan_czeka_i_wraca_po_restarcie"`; `test_silnik.py -k "test_zabicie_procesu_z_zewnatrz or test_awarie_zly_plik_zabity_proces_brak_pliku or test_awaria_prawdziwej_analizy_i_nastepne_zadanie"` |
| 2 | zamkniecie w polowie wieczoru | `test_aplikacja.py -k "test_e_zamkniecie_w_trakcie_analizy_i_ponowny_start or test_e_awaria_bez_zamkniecia_nadrabianie_folderu or test_e_dodatkowe_punkty_awarii"`; `test_ui_wieczor.py -k test_5_restart_programu_odtwarza_plytki_i_decyzje_na_ekranie` |
| 3 | brak folderu "Cyrkon" | `test_aplikacja.py -k "test_g_bez_projektow_skany_czekaja_do_odswiezenia_puli or test_folder_skanera_pojawia_sie_pozniej"`; `test_pula_aplikacja_r3.py -k test_r3_d8_nieudane_odswiezenie_ponawiane` |
| 4 | brak sieci | `test_indicate.py -k test_k5_utrata_sieci_5_potwierdzen_100_powtorzen`; `test_ramka.py -k "test_k5_utrata_sieci or test_ramka_poranna_bez_sieci_trzyma_plan_do_limitu"`; `test_excel.py -k test_excel_niedostepny_komunikat_bez_awarii` |
| 5 | brak ramki | `test_aplikacja_rano.py -k test_k5_wylaczona_ramka_i_brak_excela_ostrzezenie_i_dalsza_praca`; `test_ui_rano.py -k test_k5_bez_ramki_i_excela_komunikat_program_dziala_dalej` |
| 6 | baza zajeta | `test_aplikacja.py -k "test_baza_zajeta_wynik_nie_ginie or test_p8_blad_analizy_przy_zajetej_bazie"`; `test_baza.py -k test_d1_baza_zajeta_przez_inny_proces_daje_czytelny_komunikat`; `test_aplikacja_rano.py -k test_d2_baza_zajeta_zdarzenia_ramki_czekaja_i_wracaja`; po scaleniu P14: `test_p14_baza_zajeta.py` (caly plik: prawdziwa blokada `BEGIN EXCLUSIVE` / `IMMEDIATE`, 17 przypadkow, odpowiedz w 1,0 s, komunikat `decyzja_niezapisana` / `polecenie_niezapisane` z "Ponow teraz") **[DO POTWIERDZENIA PO SCALENIU]** |

**Czesc B - proby reczne na programie z paczki (`set QT_QPA_PLATFORM=offscreen`; kazda: stan przed, zdarzenie, log, stan po):**

1. Brak folderu "Cyrkon": zmien nazwe katalogu `<nazwa>_wej\Cyrkon` na `Cyrkon_x`, `<K>\Stanowisko.cmd --zamknij-po 30`,
   w `<DANE>\logi\stanowisko.log` szukaj komunikatu `pula_brak_folderu`; przywroc nazwe; `Samokontrola.cmd --bez-sieci`
   przy braku folderu ma dac kod 1 (blad) z wierszem o folderze.
2. Zamkniecie w polowie wieczoru: powtorz T2 czesc A z 4 skanami, po 2. skanie zakoncz proces programu
   (`powershell Stop-Process -Id <pid wlasnego procesu python>`), uruchom ponownie; liczba skanow i statusy w bazie po
   ponownym starcie = 4 z 4, w logu komunikat `wznowiono`; pliku `zadania_niezakonczone.json` nie ma po nadrobieniu.
3. Zabicie silnika: w trakcie analizy 2. skanu zakoncz proces potomny silnika (najmlodszy `python.exe` potomny programu
   - PID z logu `stanowisko.log`); oczekiwane: komunikat `blad_analizy` ("przerwana"), nastepny skan przyjety.

**Komunikaty a PW zal. F:** tresci komunikatow sa w `stanowisko\statusy.py` (`KOMUNIKATY`, `BLEDY_RAMEK`). Zalacznik F
jest w dokumencie "Stanowisko kontroli cyrkonii - plan wdrozenia v2" (`Ramki/`, plik `.md` z pauza w nazwie); wg
recenzji PR #40 runda 1 ma 12 wierszy, z czego 8 ma odpowiednik w programie. Testy sprawdzaja `rodzaj` komunikatu, nie
tekst wzgledem zal. F. Wykonawca sporzadza tabele `t7_komunikaty.md`: 6 przypadkow x (rodzaj komunikatu z testu, tekst
ze `statusy.py`, wiersz zal. F albo wiersz tabeli `instrukcje/co_robic_gdy_nie_dziala.md` z A11d, zgodne tak / nie).
Przypadek bez wiersza w zal. F = odstepstwo do opisania, nie FAIL z automatu - decyzja koordynatora (POTRZEBUJE 4).

**Liczby kryterium:** 6 z 6 przypadkow: (a) testy `PASSED` (licznik na przypadek), (b) komunikat wskazany w tabeli,
(c) "dalsza praca" i "stan z bazy" = asercje testow z wiersza 1, 2, 6 + proby B.

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
<K>\Polecenie.cmd narzedzia\metryki_P3a.py --skany <PC-katalog>\app\dane_ref\syntetyczne_R59_P2 <PC-katalog>\app\dane_ref\syntetyczne_R59_P3a --projekty <PC-katalog>\app\Prace_test --wyjscie <ROB>\t10 --nazwa t10_metryki.json --procesy 1 --ustawienia <K>\ustawienia.toml > <ROB>\t10.log 2>&1
```

**Liczby kryterium (plik `<ROB>\t10\t10_metryki.json` i `t10.log`):**

| Liczba | Pole |
|---|---|
| wyrownanie n z 40 | `zbiorczo.plate_match.wyrownanie_ok` / `zbiorczo.plate_match.skanow` |
| top-1 "dobrze" | `zbiorczo.top1_per_scenariusz.dobrze` (licznik prac i `top1_bledny` = 0) |
| falszywe czerwone na pracach calych | wiersz logu `PRACE CALE: ..., z czerwonym N` (N = 0) |

Punkt odniesienia: R59 pkt 6.2 (`raporty/R59_2026-11-14.md`): 40 / 40, 276 / 276, 0 / 127; E3-A5 runda 4 (pula): 40 / 40,
276 / 276, 0 / 132. **[DO POTWIERDZENIA]** nazwy pol przez podglad pliku wyniku z `--limit 2`.

**Dowody w `T10/`:** `t10_metryki.json` (bez sciezek do zlecen - sprawdz `t9_dane_osobowe.py` przed dodaniem; w razie
trafien dodaj tylko `t10_wynik.md`), `t10.log` (ta sama kontrola), `t10_wynik.md`.

**Czas:** 40-60 min (40 skanow x 25-70 s w 1 procesie). **Ciezar:** ciezki, seria pomiarowa (tor 2). **Rownolegle:** nie
z T2, T4, T11.

**Pulapki:** `--procesy` > 1 zawyza czasy (i lamie zasade 1 procesu); miedzy przebiegami rozrzut 1 gniazda (RANSAC) -
jeden przebieg jest wynikiem, powtorka tylko z opisem obu; `<PC-katalog>\r59\Prace_test` z raportu R59 juz nie istnieje;
wynik zawiera nazwy plikow projektow = dane - do repo idzie tylko to, co przeszlo kontrole T9.

## T11 - Stare plytki

**Kryterium (plan):** skany `*_r54` przez aplikacje - uklad rozpoznany albo ostrzezenie z nazwa wlasciwego ukladu;
0 zielonych przy zlym ukladzie; uklad zapisany w `skany`.

**Gdzie:** program z paczki + symulator (jak T2 czesc A). **Dane:** `<PC-katalog>\app\dane_ref\syntetyczne_r54_P2`
(24 skany, w tym 12 okraglych) i `syntetyczne_r54_P3a` (16, w tym 12 okraglych); wzorzec nazw
`skan_<okragla_>wieczorna|poranna_r54_n<k>_s<seed>.stl` + prawda `.json`.

**Kroki:**

1. Czesc A (rozpoznanie, szybka, lekka):
   `<K>\Polecenie.cmd narzedzia\auto_uklad.py --skany <PC-katalog>\app\dane_ref\syntetyczne_r54_P2 <PC-katalog>\app\dane_ref\syntetyczne_r54_P3a --wyjscie <ROB>\t11_auto --procesy 1 --ustawienia <K>\ustawienia.toml`
   Liczby: `auto_uklad.json`, `podsumowanie.bez_numeru` i `z_numerem`: `ok` = 40 z 40, `zle_ale_pewny` = 0.
2. Czesc B (przez aplikacje, tor 2): pusta baza; `<K>\Stanowisko.cmd --zamknij-po <s>` i
   `<K>\Polecenie.cmd narzedzia\symulator_skanera.py --folder <folder_eksportu_skanera> --zrodla <PC-katalog>\app\dane_ref\syntetyczne_r54_P2 --ile 24 --odstep 45 --rownolegle 1 --seed 1 --dziennik <ROB>\t11_symulator.json`
   (24 skany; `--zamknij-po` = 24 x 45 s + 300 s zapasu = 1380). Plytki poranne w trybie wieczornym dostaja status
   `plytka_nie_z_trybu` - uklad ma byc mimo to zapisany. **Wariant pelny** (40 skanow) tylko gdy starczy czasu toru.
3. `python <ODB>\narzedzia\sql_odczyt.py --baza <DANE>\stanowisko.sqlite "SELECT id, status, uklad, uklad_zrodlo, uklad_zgodny FROM skany ORDER BY id"`
   i `"SELECT s.id, s.status, s.uklad, sum(p.status_gniazda='zielony') AS zielonych FROM skany s LEFT JOIN prace p ON p.skan_id = s.id GROUP BY s.id"`
   **[DO POTWIERDZENIA: nazwa kolumny `prace.skan_id`]**.
4. Zly uklad (wymuszony recznie) - testy: `<K>\Polecenie.cmd -m pytest <ST>\testy\test_session_wieczor.py <ST>\testy\test_straznik.py <ST>\testy\test_kontroler_api.py <ST>\testy\test_auto_uklad.py -q -rA -p no:cacheprovider --rootdir <ST> -k "niezgodny_uklad or niezgodna_z_ukladem or auto or innego_ukladu"`.

**Liczby kryterium:** (a) `uklad` z bazy = `plytka` z prawdy + `_r54` dla n z 24 skanow (ma byc 24 z 24), `uklad_zrodlo`
= `auto`; (b) skany o statusie `niezgodny_uklad` albo z `uklad_zgodny` = 0: suma `zielonych` = 0; (c) `uklad` nie jest
pusty w zadnym wierszu `skany` (24 z 24).

**Uwaga do kryterium (O6):** przy rozpoznawaniu automatycznym "zly uklad" oznacza "zaden uklad nie pasuje"; komunikat
`niezgodny_uklad` w `statusy.py` NIE zawiera nazwy wlasciwego ukladu (lista `uklady_pasujace` jest tylko w wyniku
`porownaj` i starym `ui_test.py`). Druga galaz kryterium ("ostrzezenie z nazwa wlasciwego ukladu") jest wiec dzis
niespelnialna przez aplikacje - test zalicza sie pierwsza galezia (uklad rozpoznany 24 z 24); kazdy nierozpoznany skan =
FAIL (POTRZEBUJE 5).

**Dowody w `T11/`:** `t11_auto_uklad_podsumowanie.json` (sama sekcja `podsumowanie`), `t11_skany.tsv`, `t11_zielone.tsv`,
`t11_testy.log`, `t11_wynik.md`.

**Czas:** 50 min (A 5, B 30, testy 10). **Ciezar:** czesc B ciezka (tor 2), reszta lekka. **Rownolegle:** B nie z T2, T4, T10.

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
<K>\Polecenie.cmd narzedzia\metryki_pula.py jakosc --katalog <PC-katalog>\e3\a5\pomiary\pula400 --wpisow 400 --pamiec <ROB>\pamiec --ustawienia <K>\ustawienia.toml > <ROB>\t4_jakosc.log 2>&1
<K>\Polecenie.cmd narzedzia\metryki_pula.py czas --katalog <PC-katalog>\e3\a5\pomiary\pula400 --wpisow 400 --pamiec <ROB>\pamiec --ustawienia <K>\ustawienia.toml > <ROB>\t4_czas_ciepla.log 2>&1
<K>\Polecenie.cmd narzedzia\metryki_pula.py czas --katalog <PC-katalog>\e3\a5\pomiary\pula400 --wpisow 400 --pamiec <ROB>\pamiec_zimna --ustawienia <K>\ustawienia.toml > <ROB>\t4_czas_zimna.log 2>&1
```

**[DO POTWIERDZENIA przez `POL narzedzia\metryki_pula.py czas --help`]**: nazwa opcji katalogu zestawu (`--katalog`), gdzie
laduje plik wyniku (`--wyjscie` / `--nazwa`); narzedzie nie moze pisac do `<PC-katalog>\e3` - gdy pisze obok zestawu,
skopiuj zestaw do `<ROB>\pula400` (`robocopy /E`).

**Liczby kryterium:**

| Liczba | Pole wyniku |
|---|---|
| top-1 "dobrze" n z n | `jakosc`: `top1_projekt` i `top1_wpis` (licznik / prac); `zielone` ze zlym wpisem = 0 |
| plytka do 40 s | `czas`: `plytki[].czas_s` - maksimum z 10 dla puli cieplej i zimnej; podaj tez mediane |
| pamiec do 8 GB | `czas`: `szczyt_mb` (szczyt zbioru roboczego procesu, `psutil` `peak_wset`) |
| dwa wspolczynniki, STL w dwoch raportach | licznik prac z prawdy z 1,20 i 1,25 na plytce; `wpis_niejednoznaczny` |

**Interpretacja (O7), do decyzji koordynatora PRZED testem:** "plytka do 40 s" = kazda z 10 plytek przy puli cieplej
(pamiec linii brzegu na dysku z poprzedniego przebiegu). Przy puli zimnej plytka 1 liczy linie brzegu od zera: 63,4 s
(E3-A5i) i 67,9 s (E3-A5) - to przekracza 40 s i ma byc podane w raporcie jako liczba, nie ukryte. "Pamiec do 8 GB" =
szczyt procesu roboczego + szczyt okna (zmierzone: 3,95 GB + 1,0 GB); `metryki_pula` mierzy jeden proces.
Zmierzone dotad: top-1 187 / 187, plytki 2-10 maks. 34,2 s, ciepla maks. 28,8 s, szczyt 3,82-3,95 GB.

**Dowody w `T4/`:** `t4_wynik.md` (tabela liczb, pula ciepla i zimna osobno), `t4_czas_ciepla.json`, `t4_czas_zimna.json`,
`t4_jakosc.json` - pliki JSON tylko po kontroli `t9_dane_osobowe.py` (pliki puli zawieraja sciezki z nazwami zlecen;
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

**Gdzie:** testy z `<REPO>` interpreterem wersji (liczby kryterium) + proba z atrapa ramki na adresie sieci lokalnej PC
(zapis ruchu do T9).

**Czesc A - liczby kryterium (testy na dwoch procesach, 127.0.0.1):**

```
<K>\Polecenie.cmd -m pytest <ST>\testy\test_indicate.py <ST>\testy\test_ramka.py -q -s -rA -p no:cacheprovider --rootdir <ST> -k "test_k1 or test_k2 or test_k4 or test_k5 or test_k6 or test_k7 or test_zz_k8" > <ROB>\t5_testy.log 2>&1
<K>\Polecenie.cmd -m pytest <ST>\testy\test_aplikacja_rano.py -q -s -rA -p no:cacheprovider --rootdir <ST> -k "test_a_ or test_k1_plan_ramki_porannej or test_k2_enter or test_k4_spacja" >> <ROB>\t5_testy.log 2>&1
```

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
   `python <ODB>\narzedzia\posrednik_ruchu.py --sluchaj <adres PC>:8766 --cel <adres PC>:8765 --zapis <ROB>\ruch_ramka_w.bin`
   (ramka P: `--sluchaj <adres PC>:8768 --cel <adres PC>:8767 --zapis <ROB>\ruch_ramka_p.bin`).
3. `<K>\ustawienia.toml`, `[ramki]`: `wieczorna_host` / `poranna_host` = `<adres PC>`, `port` = port posrednika.
   **[DO POTWIERDZENIA]**: `[ramki] port` jest jeden dla obu ramek - wtedy dwa posredniki na roznych adresach (np.
   127.0.0.1 i adres karty) albo proba ramek po kolei.
4. Wieczor: T2 czesc A z 3 skanami (ramka W ma dostac plan i kolory); rano: `<K>\Stanowisko.cmd --rano` **[DO
   POTWIERDZENIA: opcja trybu porannego]** z 2 skanami plytek porannych, na atrapie `plytka 4`, `klawisz Enter`, `klawisz Spacja`.
5. Zatrzymaj posredniki (Ctrl+C): zapisz wiersz `POSREDNIK koniec: polaczen N, ... bajtow ...` (N > 0 - inaczej program
   nie szedl przez posrednik i proba jest niewazna).

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

**Gdzie:** testy z `<REPO>` interpreterem wersji; arkusz powstaje w pamieci z `narzedzia\arkusz_syntetyczny.py`
(`--wierszy 30000 --zapytan 200 --seed <n> --csv <plik>`; samo narzedzie tylko buduje arkusz i wypisuje liczniki).

**Kroki:**

```
<K>\Polecenie.cmd narzedzia\arkusz_syntetyczny.py --wierszy 30000 --zapytan 200 > <ROB>\t6_arkusz.txt 2>&1
<K>\Polecenie.cmd -m pytest <ST>\testy\test_excel.py -q -s -rA -p no:cacheprovider --rootdir <ST> > <ROB>\t6_excel.log 2>&1
<K>\Polecenie.cmd -m pytest <ST>\testy\test_aplikacja_rano.py -q -s -rA -p no:cacheprovider --rootdir <ST> -k "test_k3_excel_pytaj or test_k3_excel_cien" > <ROB>\t6_aplikacja.log 2>&1
```

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

**Gdzie:** `POL narzedzia\raport_metryk.py` na dwoch bazach: (W) baza wieczoru z T2 czesc A (`<DANE>\stanowisko.sqlite`
instalacji roboczej wykonawcy T2 - kopia do `<ROB>\baza_t2.sqlite`), (R) baza SE10 z T3 (`<ROB T3>\t3_tmp\...\*.sqlite` -
znajdz `dir /s /b <ROB>\t3_tmp\*.sqlite`; **[DO POTWIERDZENIA]**: test SE10 zostawia plik bazy w katalogu `--basetemp`).

**Kroki:**

```
<K>\Polecenie.cmd narzedzia\raport_metryk.py --baza <ROB>\baza_t2.sqlite --tryb wieczor --od <data T2> --do <data T2> --json <ROB>\t8_wieczor.json > <ROB>\t8_wieczor.txt
<K>\Polecenie.cmd narzedzia\raport_metryk.py --baza <baza SE10> --tryb oba --od 2026-11-17 --do 2026-11-19 --json <ROB>\t8_rano.json > <ROB>\t8_rano.txt
```

Kody: 0 = wszystko w progu, 3 = cos ponizej progu, 4 = brak danych, 2 = blad (kod 3 i 4 to nie jest FAIL testu T8 -
T8 sprawdza zgodnosc liczb, nie progi).

**Liczenie reczne (niezaleznie od `metryki.py`; zapytania przez `python <ODB>\narzedzia\sql_odczyt.py --baza <plik> "<SELECT>"`,
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
`program_start` - "dni bez awarii" = "brak danych"; baza T2 bez decyzji technika (brak B1) ma falszywe alarmy "brak
danych" - wtedy te metryke porownaj na bazie SE10 albo zapisz "NIE ZMIERZONO"; M2 nie jest liczona (wymaga zmiany
schematu - decyzja wlasciciela).

## T9 - Dane osobowe

**Kryterium (plan):** wyszukanie nazw folderow zlecen w repo, logach, plikach wynikow, ruchu sieciowym do ramki -
0 trafien; nazwy tylko w `dane/` (baza, log Excela).

**Gdzie:** skrypt `<ODB>\narzedzia\t9_dane_osobowe.py` (interpreter bazowy `PY -I`). Lista nazw istnieje tylko w pamieci
skryptu; wypisywane sa liczby i `sha16`. Wykonuje sie NA KONCU (po T2-T8, T10, T11), bo przeszukuje ich wyniki.

**Skad nazwy:** `--nazwy-z <PC-katalog>\app\Prace_test` (15 folderow), `--nazwy-z <PC-katalog>\e3\a5i\t4\drzewo\Cyrkon`
(47 folderow), `--nazwy-z <PC-katalog>\t0\<nazwa>_wej\Cyrkon` kazdej instalacji roboczej, `--baza <DANE>\stanowisko.sqlite`
kazdej instalacji (tabele `zlecenia.folder`, `projekty.plik`), `--baza <baza SE10>`.

**Kroki (kazdy wynik do osobnego pliku; `N` = wspolne opcje `--nazwy-z ... --baza ...`):**

1. Repo: `PY -I <ODB>\narzedzia\t9_dane_osobowe.py N --repo <REPO> --json <DOW>\t9_repo.json > <DOW>\t9_repo.txt`
   (tresc i sciezki plikow sledzonych + opisy commitow od `2537f6f`). Powtorz dla worktree z dowodami wszystkich
   wykonawcow po scaleniu ich galezi.
2. Logi: `... N --cel <DANE>\logi --cel <PC-katalog>\koordynator\robocze\odbior > <DOW>\t9_logi.txt` (dla kazdej instalacji roboczej).
3. Pliki wynikow: `... N --cel <DANE>\wyniki --cel <DANE>\podglady --cel <DANE>\pula_cache > <DOW>\t9_wyniki.txt`
   oraz plik `do_dofrezowania_biezaca.csv` obok bazy.
4. Ruch do ramki: `... N --cel <ROB T5>\ruch_ramka_w.bin --cel <ROB T5>\ruch_ramka_p.bin > <DOW>\t9_ruch.txt`
   + test `<K>\Polecenie.cmd -m pytest <ST>\testy\test_indicate.py <ST>\testy\test_ramka.py -q -rA -p no:cacheprovider --rootdir <ST> -k test_zz_k8`
   (caly ruch testow przez posrednik w pamieci; zmierzone w A8i: 0 trafien w ok. 3450 zapisach).
5. Dowod "nazwy tylko w `dane/`": `... N --cel <DANE> --dozwolone stanowisko.sqlite --dozwolone log_excel.csv > <DOW>\t9_dane.txt`
   - "Trafienia w miejscach dozwolonych" > 0 (baza zawiera nazwy - to dowod, ze skrypt umie je znalezc),
   "TRAFIENIA calych nazw poza miejscami dozwolonymi" = 0.
6. Kontrola skryptu przed uzyciem (proba dodatnia): `echo <jedna nazwa folderu wpisana z klawiatury> > <ROB>\probka.txt`
   NIE - nazwy nie wpisujemy recznie; zamiast tego krok 5 jest proba dodatnia (baza). Gdy krok 5 da 0 trafien dozwolonych,
   skrypt nie widzi nazw: wynik calego T9 = "NIE ZMIERZONO", szukaj przyczyny (kodowanie, pusta baza).

**Liczby kryterium:** suma "TRAFIENIA calych nazw poza miejscami dozwolonymi" z krokow 1-5 = 0 (kod wyjscia 0 w kazdym).
"Czlony nazw do wyjasnienia" (pojedyncze slowa z nazw, np. zwykle slowa i numery) NIE sa kryterium - wykonawca opisuje
w `t9_wynik.md` kazda grupe (plik, `sha16` czlonu, wyjasnienie: slowo pospolite / nazwisko). Nazwisko poza `dane/` = FAIL.
"Nieprzeszukane" (zip, pdf, png, xlsx, pliki > 300 MB): podaj liczbe; ZIP wydania nie zawiera danych (sprawdza T13 i
lista plikow paczki).

**Dowody w `T9/`:** `t9_repo.txt`, `t9_repo.json`, `t9_logi.txt`, `t9_wyniki.txt`, `t9_ruch.txt`, `t9_dane.txt`,
`t9_wynik.md`.

**Czas:** 30 min. **Ciezar:** lekki (czyta pliki; baza i logi male). **Rownolegle:** tak; po pozostalych testach.

**Pulapki:** nie przekierowywac do pliku niczego poza wyjsciem skryptu (nie robic `dir` katalogow zlecen do logu);
`--nazwy-z` wskazuje katalog NADRZEDNY folderow zlecen; nazwy krotsze niz 4 znaki sa pomijane i liczone (liczba w
pierwszym wierszu - gdy > 0, opisz); skrypt nie rozroznia wielkosci liter ASCII, polskie litery tylko w tej samej
wielkosci; pliki sztucznego drzewa A5i maja nazwy fikcyjne - trafienia ich czlonow w repo to zwykle slowa.

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

**Liczby kryterium:** wiersz `NARUSZENIA (grupa E3 i sciezki poza listami): N` (N = 0) i tabela grup (nowe / zmienione /
usuniete). Kazde naruszenie = poprawka przez wlasciwa paczke albo wyjatek zapisany decyzja koordynatora w `RAPORT.md`.

**Proba na obecnym `main` 9ba9e91 (20.11, to jeszcze NIE odbior):** 579 plikow zmienionych, 503 nowe; E3: 164 nowe /
22 zmienione; R58: 242 / 4; R59: 97 / 34 / 16 usunietych; sciezek poza listami 0; **naruszen 7** - wszystkie "nie ASCII"
w nowych plikach: `stanowisko/dzien_skanera.py`, `dzien_skanera_kroki.toml`, `dzien_skanera_rdzen.py`, `statusy.py`,
`ui/napisy.py`, `ui/napisy_rano.py`, `testy/test_dzien_skanera.py` (napisy ekranu i krokow po polsku ze znakami
diakrytycznymi). Wynik: `T13/proba_main_9ba9e91.txt`. To wymaga decyzji przed odbiorem (POTRZEBUJE 6): wyjatek "pliki
napisow ekranu" albo poprawka plikow.

**Odstepstwo O10:** "tylko pliki z list paczek" jest sprawdzane na poziomie katalogow paczek (plik `t13_dozwolone.txt`),
nie listy pojedynczych plikow z kazdego zlecenia - zlecenia paczek fali 1-3 nie sa w repo. Kontrola dokladna dla paczek
z 20.11 (zlecenia w `<PC-katalog>\koordynator\zlecenia\`): `git diff --stat main...e3/<kod>` wobec listy plikow zlecenia -
robi koordynator przy scalaniu. Pliki grup R58 / R59 (STL do zamowienia, PDF, ZIP pakietow) nie sa wynikiem etapu 3.

**Dowody w `T13/`:** `t13_wynik.txt`, `t13_wynik.json`, `t13_diff_stat.txt`.

**Czas:** 10 min. **Ciezar:** lekki. **Rownolegle:** tak; uruchomic na commicie wydania i jeszcze raz po dodaniu dowodow.

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

1. Koordynator: budowa paczek, `<REPO>`, decyzje POTRZEBUJE 1-6 (co najmniej: T4 pula ciepla / zimna, T13 wyjatek napisow).
2. W1 zaczyna T0 (tor 1). Rownolegle W2 i W3 zakladaja instalacje robocze - **po kolei przez tor 1** (instalacja probna =
   ciezki krok), wiec realnie: T0 -> instalacja `w2` -> instalacja `w3` -> T12 -> T1.
3. W2: T10 i T4 nie potrzebuja programu w oknie - startuja zaraz po instalacji `w2`; T4 i T10 nigdy jednoczesnie
   (jedna sesja pomiarowa naraz); T2 i T11 po nich. T1 (tor 1) i seria W2 (tor 2) moga isc jednoczesnie tylko przy wolnym
   RAM >= 6000 MB przed startem T4 - inaczej T4 czeka na koniec T1.
4. W3: T3, T6 od razu po instalacji `w3`; czesc A T5 i testy czasowe T7 poza oknami serii pomiarowej W2 (albo powtorka
   po serii, z zapisem obu wynikow).
5. W4: T13 kiedykolwiek; T8 po T2 i T3; T9 na samym koncu, po zebraniu dowodow wszystkich wykonawcow.
6. Koordynator: `RAPORT.md`, FAIL -> paczki poprawek -> powtorka testu (stary dowod zostaje z dopiskiem `_proba1`).

## Lista "sprawdzone przez --help / w kodzie" (stan `main` 9ba9e91 i galezi z 20.11)

| Co | Jak sprawdzone |
|---|---|
| `narzedzia\symulator_skanera.py`: `--folder --zrodla --ile --odstep --rownolegle --zle uciety --seed --dziennik --analiza --projekty --wyjscie --ustawienia`; pola dziennika `zapisy`, `analizy` | `--help` (rozpoznanie) + kod (wiersze 284-396) |
| `narzedzia\metryki_P3a.py`: `--skany --projekty --wyjscie --nazwa --procesy --ustawienia --limit --wzorzec` | kod (argparse, wiersze 135-144) |
| `narzedzia\metryki_pula.py`: podpolecenia `przygotuj czas jakosc r59 ranking pamiec`; `--wpisow --pamiec --ustawienia` | `--help` (rozpoznanie); opcja `--katalog` w `czas` / `jakosc` - do potwierdzenia |
| `narzedzia\raport_metryk.py`: `--od --do --tryb --baza --ustawienia --json`; kody 0 / 3 / 4 / 2 | `--help` (rozpoznanie) |
| `narzedzia\auto_uklad.py`: `--skany --wyjscie --procesy --limit --ustawienia` | `--help` (rozpoznanie) |
| `narzedzia\arkusz_syntetyczny.py`: `--wierszy --zapytan --seed --csv` | `--help` (rozpoznanie) |
| `narzedzia\atrapa_ramki.py`: `--rola --port --host --sterowanie --bez-konsoli --limit-lacznosci --konfiguracja`; `python -m ramka`: `--rola --sprzet --host --port --konfiguracja --sterowanie-atrapy --gadatliwie` | `--help` (rozpoznanie) |
| `stanowisko.aplikacja`: `--ustawienia --zamknij-po --atrapa --rano` | kod / test `test_main_uruchamia_program_i_zamyka_go_czysto` (rozpoznanie); `--rano` bez atrapy - do potwierdzenia |
| `stanowisko.samokontrola` (galaz `e3/a11s`): `--ustawienia --sumy --json --bez-sieci`; kody 0 / 1 / 2 | kod (argparse, wiersze 1380-1384) |
| `zainstaluj.cmd` (galaz `e3/a11i`): `/katalog /python /skrot /testy /bez-sieci /bez-pauzy`; kody 0-11 | plik `.cmd` wiersz 3; raport A11i p. 12.7 |
| `Polecenie.cmd`, `Stanowisko.cmd` (wzory, `e3/a11i`): przekazuja argumenty, `cd` do `wersje\<wersja>\program` | tresc plikow |
| `narzedzia\zbuduj_wydanie.py` (`e3/a11i`): `--wyjscie --wersja --kola --rewizja --zrodlo --commit --data --pobierz-kola`; paczka = `program\{stanowisko, modele_plytek, narzedzia, ramka, instrukcje, instalacja}`, bez `testy\` | kod (wiersze 9-12, 33, 332-341) |
| 36 nazw testow pytest wymienionych w T2, T3, T5, T6, T7, T8, T11 | `grep` nazwy funkcji w pliku testu (0 brakow) |
| tabela `zlecenia` (`folder`), `skany` (`uklad`, `uklad_zrodlo`, `uklad_zgodny`, `czas_pliku`, `czas_analizy`, `czas_s`, `status`) | `stanowisko\baza.py` (wiersze 80-155) + rozpoznanie |
| katalogi danych i liczby plikow (T2, T4, T10, T11) | listowanie 20.11: R59_P2 24 + 24, R59_P3a 16 + 16, r54_P2 24 + 24, r54_P3a 16 + 16, pula400 `plytki` 10 + 10, `a5i\t4\eksport` 10, `Prace_test` 15 folderow, `a5i` Cyrkon 47 folderow |
| `symulator_t14.py` (`e3/a11d`): `wieczor` / `rano`, `--sprawdz --program --scenariusz --opoznienie --dziennik --zamknij-po` | kod (argparse, wiersze 354-360) |
| skrypty `odbior_koncowy\narzedzia\*.py` | proby na danych sztucznych - `E3-ODB_raport_2026-11-20.md` |

"Rozpoznanie" = sprawdzenie wykonane 20.11 przez pomocnicze sesje odczytu tej paczki (`--help` uruchomione na `main`
9ba9e91); pozycje bez dopisku sprawdzilem sam w plikach.

## Zrodla liczb kryteriow - skrot

| Test | Liczba kryterium | Zrodlo |
|---|---|---|
| T0 | kody 0 / 10 / 0; samokontrola bledy 0; SHA-256 | kody wyjscia `.cmd`, wyjscie `Samokontrola.cmd`, `certutil` |
| T1 | 0 failed, 0 errors, pominiete = 9 znanych | ostatni wiersz i sekcja `-rs` logu pytest |
| T2 | 10 z 10; start < 1 s; mapa mediana <= 40 s; przerwa <= 200 ms; lista | baza `skany` + `zdarzenia`; dziennik symulatora `analizy[].start_od_konca_zapisu_s`; `czas_analizy - czas_pliku`; wyjscie `-s` testow petli; lista: brak B1 |
| T3 | 32 z 32 wierszy; listy kompletnych i brakow | `test_se10[R01..R32]`; przez ekran: brak B2 |
| T4 | top-1 n z n; plytka maks. s; szczyt MB | `metryki_pula jakosc` / `czas`: `top1_projekt`, `top1_wpis`, `plytki[].czas_s`, `szczyt_mb` |
| T5 | 5 z 5, 0 powtorek; plan <= 5 s; Spacja < 1 s | wyjscie `-s` testow `test_k5`, `test_k6`, `test_k7` |
| T6 | 200 z 200; 0 zlych; log regula 6 | testy `test_k1_*`, `test_k3_*`, `test_k4_*` |
| T7 | 6 z 6 przypadkow | testy z tabeli + proby reczne + tabela komunikatow |
| T8 | n z n metryk zgodnych | `raport_metryk --json` wobec `t8_recznie.md` |
| T9 | 0 trafien calych nazw | wyjscie `t9_dane_osobowe.py` |
| T10 | 40 z 40; top-1 dobrze n z n; czerwone na calych 0 | `metryki_P3a`: `zbiorczo.plate_match`, `top1_per_scenariusz.dobrze`, wiersz `PRACE CALE` |
| T11 | uklad 24 z 24; zielone przy zlym 0; kolumna `uklad` niepusta | baza `skany`, `prace`; `auto_uklad.json` |
| T12 | 1 polecenie; 3 sumy ustawien rowne; kopia bazy | kody `.cmd`, `certutil`, pliki kopii, `PRAGMA user_version` |
| T13 | naruszen 0 | wyjscie `t13_higiena.py` |
