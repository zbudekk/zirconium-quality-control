# Raport recenzenta - PR #44 (E3-ODB), runda 1

Data: 20/21.11.2026 (23:53-00:20). Zakres: `git diff main...origin/e3/odb`, HEAD 6e2fb0b (16 plikow nowych, +4121 wierszy,
wszystkie w `Ramki/etap3/odbior_koncowy/`). Miara: `zlecenia/odb.md`, `odb-r2.md` (6 decyzji koordynatora), plan etapu 3
sekcja 7 i 9, `zlecenie.md` p. 4.

Metoda: wlasny przeglad calego diffu (PLAN_TESTOW.md, t2_wieczor.py, t2_scenariusz.json, t3_poranek.py w calosci; RAPORT.md,
raport wykonawcy na koncu); proby narzedzi z kopii `qc-wt\rec-odb` (6e2fb0b) na kodzie programu `qc-wt\integ\Ramki\stanowisko`
(main 2d1e010, tylko odczyt - po probach `git status` pusty); dane i wyniki w `koordynator\robocze\rec-odb\`. Czesci D-F
wykonalo rozgalezienie recenzenta (ten sam kontekst; notatki `robocze\rec-odb\czesc_DEF_notatki.md`) - liczby z tych czesci
sa oznaczone "(rozg.)"; dwie z nich sprawdzilem ponownie sam (t9 wiersze 79 / 92; "22 z 22" na origin/e3/a11d 6e75c6c).
Pelnego pytest i pelnego T2 nie uruchamialem (zgodnie ze zleceniem).

Uruchomiono: T2 skrocony x 3 (tor 3: proba, przebieg z 3 wstrzyknieciami, limit), T3 caly x 5 (proba + 4 wstrzykniecia),
`sql_odczyt.py` x 2 na bazie proby T2, proby D (rozg.): t13 na main + 8 wstrzykniec, t9 na danych sztucznych, posrednik,
sql_odczyt 17 zapytan.

## 0. Werdykt i liczby

**Do scalenia po poprawkach.** B 2 / P 9 / D 17.

Sterowniki T2 i T3 prowadza prawdziwy program i wykrywaja bledy wstrzykniete w tabele prawdy, petle okna, limit i decyzje
(T2 4 z 4, T3 2 z 3). Dwie rzeczy daja dzis falszywe "ZAL": werdykt T2 "lista do dofrezowania = prawda" (nie zalezy od
tego, co program pokazal) i narzedzie T9 (nie znajduje nazw z wielka litera spoza ASCII). Plan ma 5 miejsc bez wykonalnego
polecenia albo z bledna regula liczenia.

## 1. Uwagi

| Nr | Waga | Plik:linia | Scenariusz | Poprawka |
|---|---|---|---|---|
| 1 | B | `narzedzia/t2_wieczor.py:487-499` (krok "ukruszona"), `:630-631`, `:694`; `RAPORT.md:72` (O4); `PLAN_TESTOW.md:291` | Sterownik klika "Ukruszona" na KAZDEJ pracy, ktora ma ubytek w pliku prawdy - bez wzgledu na to, jak program te prace pokazal (takze gdyby byla zielona). Lista programu powstaje wylacznie z tych klikniec, wiec "lista = prawda: ZAL" dowodzi tylko drogi klikniecie -> lista, nie tego, ze wieczor z programem daje prawdziwa liste. Proba wlasna: 12 klikniec z 12, z tego 5 na pracach czerwonych, 7 na zoltych, 0 na zielonych (zapytanie do bazy proby); wykonawca: 18 z 29 na pracach nieczerwonych. Praca z ubytkiem pokazana na zielono (technik jej nie obejrzy) dalaby dzis nadal "ZAL". W `RAPORT.md` nie ma o tym odstepstwa (O4 mowi tylko "decyzje = klikniecia wg tabeli prawdy"); wykonawca zglosil to jedynie w raporcie paczki 10.9 nr 4. | (a) w kroku "ukruszona" przed kliknieciem zapisz `praca.status_programu` i `praca.kolor`; gdy `kolor == "zielony"`: NIE klikaj, `zamknij("POMINIETA: praca z ubytkiem w prawdzie jest zielona w programie")` - pozycja zostaje w `brakuje_w_programie` i werdykt = FAIL; (b) w wyniku pole `prace_z_ubytkiem_wg_programu: {czerwony, zolty, zielony, z}` i werdykt w postaci "ZAL (program: czerwone n, zolte m, zielone 0 z N)"; (c) `RAPORT.md`: nowe odstepstwo "O13 T2: lista 'do dofrezowania' powstaje z klikniec sterownika wg pliku prawdy na pracach czerwonych i zoltych; wykrywalnosc ubytkow mierzy T10 / T16, nie T2" + te same liczby w wierszu T2 (`RAPORT.md:34`) i w `PLAN_TESTOW.md:291`. |
| 2 | B | `narzedzia/t9_dane_osobowe.py:79`, `:92`; `PLAN_TESTOW.md:762` | Wzorzec to `tekst.lower().encode(...)` (male litery wg Unicode), a dane sa zmniejszane przez `bytes.lower()` (tylko ASCII). Nazwa z wielka litera spoza ASCII zapisana w logu / wyniku / ruchu do ramki w swoim zwyklym brzmieniu NIE jest znajdowana: wynik "ZAL (0 trafien)", kod 0. Tak samo nazwa w JSON z `ensure_ascii` (`\uXXXX` - tak pisze protokol ramki). (rozg.): na 32 prawdziwych nazwach katalogu prac testowych nie znaleziono doslownie 3 z 32 (UTF-8), 4 z 32 (UTF-16LE), 7 z 32 (JSON-ASCII). Kontrola dodatnia z kroku 5 tego nie lapie (inne nazwy daja trafienia). Opis w planie ("polskie litery tylko w tej samej wielkosci") jest nieprawdziwy. | W `wzorzec`: dla wariantow `{n, n.lower(), n.upper(), n.casefold()}` klucz = `wariant.encode(kod).lower()` oraz klucz `json.dumps(wariant)[1:-1].encode("ascii").lower()`; na starcie samotest: kazda nazwa musi byc znaleziona we wlasnych bajtach UTF-8, UTF-16LE i w `json.dumps(nazwa)` - inaczej kod 2 "NIE ZMIERZONO"; poprawic `PLAN_TESTOW.md:762`. Test: plik z nazwa sztuczna zaczynajaca sie wielka litera spoza ASCII -> 1 trafienie, kod 1. |
| 3 | P | `narzedzia/t3_poranek.py:789-807` (`zbuduj_wynik`), `:965-971` (kod wyjscia) | Liczba "n z 32" i kod wyjscia licza tylko zgodnosc wartosci z API sesji (jak test), a to, co POKAZUJE ekran, jest w osobnej kolumnie. Wstrzykniecie wlasne (kopia sterownika znieksztalca odczyt tabeli ekranu): 5 wierszy "ekran: nie", a wynik nadal "SE10 przez ekran: 32 z 32 wierszy zgodnych", kod 0 mimo `--wymagaj-100`; jedyny slad to "listy z ekranu: 4 z 9". Plan (`PLAN_TESTOW.md:364`) kaze liczyc "nie" jako FAIL wiersza recznie - latwo przeoczyc, a poprawny wynik tez nie jest pelny ("8 z 9"). | W `zbuduj_wynik`: wiersz z `ekran` w ("nie", "nie odczytano") dostaje `wynik = "FAIL (ekran)"` i NIE liczy sie do n; `--wymagaj-100` zwraca 1 takze wtedy; ostatni wiersz: "WERDYKT T3: ZAL / FAIL (n z 32; ekran: tak a, czesciowo b, nie dotyczy c, nie d)". |
| 4 | P | `PLAN_TESTOW.md:407-411` (T7 B2, B3), `:615` (T5 B4), `:479`, `:673-677` (T8) | Plan odsyla do "T2 czesc A z 4 / 3 skanami", ktorej po etapie 2 nie ma - T7 B2 / B3 i T5 B4 nie maja polecenia. T8 kaze brac baze wieczoru z `<DANE>` instalacji, a sterownik T2 pisze do `<ROB>\t2\dane\stanowisko.sqlite` (`:308`); baze SE10 wskazuje w `t3_tmp\se10*`, a `:372` mowi `<ROB>\t3\baza` - metryki bylyby liczone na zlej albo pustej bazie. | T8: (W) = `<ROB T2>\t2\dane\stanowisko.sqlite`, (R) = `<ROB T3>\t3\baza\stanowisko.sqlite`. T5 B4: `<K>\Polecenie.cmd <ODB>\narzedzia\t2_wieczor.py --ustawienia-wzor <K>\ustawienia.toml --roboczy <ROB>\t5_wieczor --projekty <folder_cyrkon> --wybierz 1,3,8 --odstep 60` (sekcja `[ramki]` przechodzi ze wzoru). T7 B2 / B3: `Stanowisko.cmd --zamknij-po <s>` + `Polecenie.cmd narzedzia\symulator_skanera.py --folder ... --zrodla ... --ile 4 --odstep 60 --rownolegle 1 --dziennik ...` z podanym sposobem odczytu PID. |
| 5 | P | `PLAN_TESTOW.md:582-599`, `:388-400`; `RAPORT.md:76` (O8) | Wszystkie liczby kryterium T5 (5 z 5, 0 powtorek, plan do 5 s, Spacja ponizej 1 s) pochodza z testow pytest na 127.0.0.1 z kodem z `<REPO>`; czesc B (adres karty PC, program z paczki) niczego z kryterium nie mierzy (3 skany wieczorne, ramka W). O8 mowi tylko "siec lokalna = adres karty PC; ramka poranna tylko w testach" - opis wezszy niz faktyczna zamiana. To samo T6 i T7 czesc A (przypadki 4-6 bez proby na programie z paczki): kod programu w tych testach to `<REPO>`, z paczki sa tylko interpreter i pakiety - w `RAPORT.md` nie ma o tym odstepstwa. | `RAPORT.md`: O8 zastapic tekstem "liczby kryterium T5 z testow pytest na 127.0.0.1 (kod z `<REPO>` tego samego commita, interpreter wersji); na adresie karty PC i programie z paczki tylko przebieg ramki W z 3 skanami - bez pomiaru 5 potwierdzen bez sieci, restartu ramki i Spacji; ramka P tylko w testach" i dopisac O14 "T5, T6, T7 czesc A, T1: testy biora kod programu z `<REPO>` (ten sam commit co paczka; zgodnosc plikow instalacji z paczka potwierdza licznik sum w T0)". Lepiej: w T5 B dopisac pomiar na programie z paczki (zatrzymanie posrednika = brak sieci, 5 klawiszy na atrapie, wznowienie; liczba zdarzen w bazie przez `sql_odczyt.py`). |
| 6 | P | `PLAN_TESTOW.md:488-499` (T11) | (a) Przez aplikacje ida tylko 24 skany zestawu P2; 16 skanow P3a (prace bokiem / do gory nogami) "tylko gdy starczy czasu" - zawezenie do latwiejszej czesci bez odstepstwa. (b) Regula liczenia jest bledna: "`uklad` z bazy = `plytka` z prawdy + `_r54`", a pliki prawdy maja juz nazwe z `_r54` (sprawdzone: 4 nazwy x 6 skanow) - doslownie policzone da 0 z 24. (c) "0 zielonych przy zlym ukladzie" jest puste, gdy wszystkie uklady sa rozpoznane. | (a) `--zrodla <r54_P2> <r54_P3a> --ile 40`, `--zamknij-po 2100`, liczniki "z 40" (albo jawne odstepstwo z powodem); (b) "`uklad` z bazy = `plytka` z prawdy"; (c) dopisac odsylacz: skan z niezgodnym ukladem przez aplikacje = pozycja nr 7 scenariusza T2 (`zielonych` = 0 w `t2_wynik.json`). |
| 7 | P | `narzedzia/t9_dane_osobowe.py:129-130`, `:175`, `:187` | (rozg., sprawdzone proba) Sciezka pliku zawierajaca czlon nazwy (np. samo nazwisko w nazwie pliku) jest wypisywana jawnie do dowodu `t9_*.txt`; `ukryj` chowa tylko cale nazwy - dowod T9 moze sam wniesc dane osobowe do repo. | `ukryj`: po zbudowaniu wzorca czlonow chowac sciezke takze przy trafieniu czlonu (`sha16` sciezki). |
| 8 | P | `PLAN_TESTOW.md:737`, `:743` | (rozg., z przegladu) T9 krok 2: `--cel ...\robocze\odbior` bez `--dozwolone` obejmuje bazy T2 / T3 i wyniki T4 / T10 z nazwami -> pewny falszywy FAIL. Krok 5: `--dozwolone stanowisko.sqlite` nie obejmuje kopii bazy `stanowisko.kopia_v<n>_<data>.sqlite` w `dane\kopie`. | Krok 2: dodac `--dozwolone stanowisko. --dozwolone log_excel.csv` i wykluczyc `\zrodla\`, `t4_*.json`, `t10_*`; krok 5: `--dozwolone stanowisko. --dozwolone \kopie\`. |
| 9 | P | `PLAN_TESTOW.md:818`, `:23` | (rozg., zmierzone: 15 CR w 15 wierszach pliku z przekierowania `cmd >`) T13 "jeszcze raz po dodaniu dowodow" padnie na wlasnych dowodach: logi z przekierowania maja CRLF, a `t10.log` litere spoza ASCII (`:458`). | Dopisac krok przed `git add`: dowody do LF i ASCII (maly skrypt w `narzedzia/`) albo jawna regula i odstepstwo dla `odbior_koncowy/T*/`. |
| 10 | P | `T14/README.md:18`, `:41`, `:48-50` | Na origin/e3/a11d (6e75c6c) kontrola wypisuje "zgodne 22 z 22 krokow" (sprawdzone: `symulator_t14.py:453`, README zestawu `:29`), a `T14/README.md` kaze czekac na "18 z 18" i wstrzymac probe przy innym wyniku. | `:18` i `:48`: "18 z 18" -> "22 z 22"; `:41`: znacznik zastapic "(potwierdzone na `e3/a11d` 6e75c6c: paczka wydania zawiera tylko `stanowisko`, `modele_plytek`, `narzedzia`, `ramka`, `instrukcje`, `instalacja` - zestaw T14 bierze sie z repo, krok zostaje)"; `:50`: znacznik usunac, polecenie: `<K>\Polecenie.cmd <REPO>\Ramki\etap3\t14\symulator_t14.py --sprawdz --program .` (postac zgodna z `scenariusz_symulatora.md` A11d). Dopisac w planie po T0 jedno uruchomienie tego polecenia z dowodem `T14/t14_sprawdz_paczka.txt` (nikt nie uruchomil zestawu z instalacji z paczki). |
| 11 | P | `PLAN_TESTOW.md:161-169`, `:172-173` (T12 czesc B) | Czesc B (migracja) nie ma polecen: odsyla do dwoch skryptow `.sh` w katalogu roboczym innej paczki (poza repo; sa tam dzis - sprawdzone, ale "sciezki trzeba dopasowac"). Regula wyniku dla "jedno polecenie" przy powrocie w 2 poleceniach (kod 8 + `/przywroc-kopie`) nie jest podana ("opisac"). | Przepisac kroki budowy paczki probnej i dwoch powrotow do planu jako polecenia `cmd` (albo skrypt w `odbior_koncowy/narzedzia/`); regula: "jedno polecenie" ocenia czesc A; powrot po migracji w 2 poleceniach = wpis do decyzji wlasciciela (nie FAIL, nie ciche ZAL). |
| 12 | D | `narzedzia/t2_wieczor.py:598-609` | "Zgodnie z prawda" dla plytki przyjetej nie porownuje liczby prac (`prac_program` / `prac_prawda` sa tylko wypisane); numer plytek kwadratowych podaje sam sterownik z prawdy (porownanie puste, opisane w wyniku). | Dodac `p["prac"] == poz["prac"]` do `zgodne` (w probach bylo 9 / 9, 11 / 11, 8 / 8). |
| 13 | D | `narzedzia/t2_wieczor.py:692-693` | Werdykty "mapa" i "okno" licza sie takze z pomiaru przerwanego: proba wlasna z limitem 25 s dala kod 3 i "okno bez przerw > 200 ms: ZAL"; "mapa: ZAL" jest mozliwe przy brakujacych plytkach. | `nz if not pomiar_caly` takze dla tych dwoch werdyktow (albo dopisek "pomiar czesciowy"). |
| 14 | D | `narzedzia/t2_wieczor.py:685-695` | Plik wyniku ma 5 werdyktow, bez jednego wiersza lacznego. | Dopisac "T2 LACZNIE: ZAL tylko gdy 5 x ZAL; inaczej FAIL / NIE ZMIERZONO". |
| 15 | D | `narzedzia/t2_scenariusz.json:32-33` | Dobor skanow byl poprawiony po probie: skan zestawu P3a bez drgniecia w prawdzie dostal od programu "do_powtorzenia" i zostal usuniety ze scenariusza. To stwierdzenie o programie (falszywe "skan ponownie") jest tylko w opisie scenariusza. | Wpisac do `RAPORT.md` p. 7 / p. 5 jako obserwacje do zestawienia z T10 (R59 pkt 6.2: 2 falszywe "skan ponownie"). |
| 16 | D | `PLAN_TESTOW.md:150`, `:492`, `:609`, `:689` | Polecenia zaczynaja sie od `python ...` - na PC nie ma `python` w PATH (sprawdzone: 0). | `PY -I <ODB>\narzedzia\...`. |
| 17 | D | `PLAN_TESTOW.md:198` wobec `:203` | Krok 4 T1 nie ma `-rs`, choc liczenie pominietych go wymaga ("dopisz"). | Wpisac `-rs` do polecenia. |
| 18 | D | `PLAN_TESTOW.md:560-561` | "Pamiec do 8 GB = proces roboczy + okno", ale polecenia T4 mierza jeden proces; zrodla szczytu okna w odbiorze nie ma. | Podac zrodlo (pomiar albo "wg raportu E3-A5, nie mierzone w odbiorze"). |
| 19 | D | `narzedzia/t3_poranek.py:739`, `:741`, `:758-760` | Ekran R29 sprawdzany przez podciagi "3301" i "21" w napisie; R30 przez `bz == []` na sztywno (nie z tabeli); R31 zawsze obnizany do "czesciowo". | Porownywac z wartosciami z `ocz[...]`; R29 - dopasowanie calych pol. |
| 20 | D | `PLAN_TESTOW.md:367-369`; `RAPORT.md` p. 7 | Obserwacja z T3 (okno nie pyta przed "Zamknij piec" 2, gdy praca nieznana ma decyzje "bez projektu"; potwierdzona w probie wlasnej) jest tylko w planie. | Pozycja w `RAPORT.md` p. 7 (decyzja wlasciciela: zamierzone czy poprawka P14). |
| 21 | D | `narzedzia/sql_odczyt.py:30-32` | (rozg., 2 z 2 prob) `SELECT count(*) FROM zlecenia UNION SELECT folder FROM zlecenia` wypisuje nazwy; blad SQL konczy sie sladem bledu. | Przy tabelach z nazwami odrzucac `union` / `intersect` / `except` i drugi `select`; `sqlite3.Error` -> "BLAD", kod 2. |
| 22 | D | `narzedzia/t13_higiena.py:110` | (rozg.) Nowy plik tekstowy UTF-16 (z bajtami NUL) uznany za binarny i pominiety; samotne CR nieliczone. | NUL przy rozszerzeniu spoza listy binarnych zglaszac; liczyc samotne `\r`. |
| 23 | D | `narzedzia/t13_dozwolone.txt:5`; `RAPORT.md:78` (O10) | (rozg.) Jeden przedrostek `E3 Ramki/stanowisko/` obejmuje caly program - "tylko pliki z list paczek" niczego w nim nie rozroznia; pliki nietykalne zmienione od poczatku etapu (wg rozg.: `match.py` 9 commitow, `inspect.py` 7, `synth.py` 1) nie sa wyroznione. | Grupa `NIETYKALNE` wypisywana osobno; O10 doprecyzowac (patrz p. 5). |
| 24 | D | `narzedzia/t9_dane_osobowe.py:134-141`, `:192` | (rozg.) `--repo` czyta pliki HEAD i opisy commitow, tresci historii nie; "ZAL (0 trafien)" takze przy czlonach do wyjasnienia. | Dodac `git log -p 2537f6f..HEAD`; werdykt "ZAL - czlony do wyjasnienia: N". |
| 25 | D | `ODLOZONE.md:20`, `:46` | (rozg.) "T6: 200 z 200" i "T5 ... 5 z 5" podane jak wyniki testow koncowych, ktorych jeszcze nie wykonano. | "pomiar paczki A9 / A8i; wynik T6 / T5 w `RAPORT.md`". |
| 26 | D | `RAPORT.md:9`, `:51`, `:57` | Brak reguly, czy "ZAL z odstepstwem" liczy sie do "zaliczone _ z 14" i do "T0-T14 zaliczone". | Dopisac regule (decyzja wlasciciela, p. 5). |
| 27 | D | `PLAN_TESTOW.md:715-717` (T8) | Baza T2 nie ma decyzji "OK", wiec metryka "falszywe alarmy" da "brak danych" - plan dopuszcza "NIE ZMIERZONO". | Zapisac regule: "brak danych" w raporcie = 0 z 0 w liczeniu recznym = zgodne. |
| 28 | D | `Ramki/stanowisko/stanowisko/ui/kandydaci.py:74` (poza paczka) | (rozg.) Znak U+00B7 w komentarzu (2 bajty) - T13 da FAIL (1), dopoki zostaje. | Poprawka komentarza przed budowa wydania; nie dopisywac pliku do listy O11. |

## 2. Wlasne proby

Wszystkie z katalogu `qc-wt\integ\Ramki\stanowisko` przez `narz\py.cmd`; T2 przez `narz\ciezki.ps1 -Tor 3 -Kto rec-odb`.

| Nr | Polecenie (skrot) | Wynik |
|---|---|---|
| 1 | `t2_wieczor.py --roboczy ...\t2_p1 --projekty <prace testowe> --plytki 3 --odstep 5 --limit 900` | kod 0; 3 z 3 zgodnie z prawda; start analizy 0,412 / 36,678 / 52,144 s (1 z 3 ponizej 1 s - kolejka przy odstepie 5 s); mapa mediana 58,17 s, pierwsza plytka 41,96 s; najdluzsza przerwa petli 41,8 ms, przekroczen 0 (4373 tykniec); lista rowna (12 z 12); procesow po probie 0 (4 PID-y z `t2_pid.txt` nie zyja) |
| 2 | `sql_odczyt.py --baza ...\t2_p1\dane\stanowisko.sqlite "SELECT d.rodzaj, p.status_gniazda, count(*) ..."` | `ukruszona` / czerwony 5; `ukruszona_niewykryta` / zolty 7; zielonych 0 |
| 3 | T2 z 3 wstrzyknieciami: nakladka `t2_wstrz.py` (QTimer: `sleep(0.4)` w 25. s) + kopia scenariusza (plytka 4: oczekiwany `do_powtorzenia`; plytka 6: decyzje wg prawdy), `--wybierz 2,4,6 --odstep 5` | kod 0 ("pomiar wykonany"); "10 z 10: FAIL (2 z 3)"; "okno bez przerw: FAIL" (411,1 ms w 25,09 s, 1 przekroczenie); "lista: FAIL" (oczekiwanych 7, w programie 3, brakuje 4). Wykryte 3 z 3 |
| 4 | T2 `--plytki 3 --odstep 5 --limit 25` (srodowisko jak `Polecenie.cmd`: PYTHONPATH bez katalogu programu) | kod 3; "PRZERWANO: limit 25 s"; 3 werdykty NIE ZMIERZONO, start FAIL, okno ZAL (uwaga 13); procesow po sprzataniu 0. Wykryte 1 z 1 |
| 5 | `t3_poranek.py --wyjscie ...\t3_p1 --wymagaj-100` | kod 0; 32 z 32; ekran: tak 8, czesciowo 1 (R31), nie dotyczy 1 (R17); 12 s; pytanie przed "Zamknij piec" 2: oczekiwane tak, bylo nie |
| 6 | T3, 1 wiersz oczekiwan zmieniony (R14 -> inna kuweta; nakladka na modul testu) | kod 1; 31 z 32; R14 FAIL, ekran R14 "nie". Wykryte |
| 7 | T3, 1 decyzja zmieniona (kopia sterownika: wybor drugiego kandydata pracy dwuznacznej) | kod 1; 30 z 32 (R06, R08 FAIL). Wykryte |
| 8 | T3, ekran inny niz API (kopia sterownika znieksztalca odczyt `tabela_kompletne`) | kod 0; "32 z 32"; ekran "nie" x 5, "4 z 9". NIE odbite w liczbie ani w kodzie (uwaga 3) |
| 9 | T3 z kopia samego pliku testu w innym katalogu | kod 2, "KeyError" - modul testu bierze kalibracje ramki z katalogu nadrzednego `testy`; nie wada: plan podaje `--testy <ST>\testy` |
| 10 | (rozg.) `t13_higiena.py --repo <PC-katalog>\qc --od 2537f6f --do main` (2d1e010) | 608 zmienionych, 530 nowych; dokladnie 1 naruszenie (`ui/kandydaci.py`, 2 bajty); O11: 7 z 7. Twierdzenie wykonawcy potwierdzone. 2537f6f = pierwszy commit pliku planu (16.11 00:05) |
| 11 | (rozg.) t13, 8 wstrzykniec w sztucznym repo (nie-ASCII spoza listy, CRLF w `.py`, LF w `.cmd`, plik 1171 KB, STL, `.csv`, sciezka poza listami, `.pkl`) | 8 z 8 wykrytych, kod 1; brzegowe niewykryte: UTF-16, samotne CR (uwaga 22) |
| 12 | (rozg.) t9 na nazwach sztucznych (17 celow + zapis ruchu) | kod 1, 8 trafien w 7 plikach, wypisuje tylko `sha16` i liczby; niewykryte: wielka litera spoza ASCII, `\uXXXX` (uwaga 2); czlon nazwy w sciezce wypisany jawnie (uwaga 7) |
| 13 | (rozg.) `posrednik_ruchu.py` (ruch do ramki = HTTP po TCP) | 2 polaczenia, 241 bajtow do ramki, 80 z ramki, 2 z 2 odpowiedzi przekazane; t9 na zapisie znalazl nazwe ASCII |
| 14 | (rozg.) `sql_odczyt.py`, 17 zapytan na sztucznej bazie | 15 zgodnie z opisem, 2 obejscia przez UNION (uwaga 21); zapis niemozliwy (`mode=ro`) |

Odpowiedzi na pytania zlecenia do B i C:

- T2 prowadzi prawdziwy program: `stanowisko.aplikacja.main` z prawdziwym obserwatorem, silnikiem i oknem. W pliku nie ma
  `setattr`, podmiany metody, podklasy klas programu ani zapisu do bazy (baza i log tylko do odczytu po zamknieciu). Jedyne
  ingerencje: wlasny `QTimer` w watku okna, `QApplication` zalozona przed `main`, kopia pliku ustawien, `QApplication.quit()`.
- Tabela prawdy T2 nie powstaje z wyniku programu: statusy sa w `t2_scenariusz.json`, uklad / numer / ubytki w plikach prawdy
  generatora; `sha16` skanow sprawdzane przed startem. Zastrzezenie: dobor skanow poprawiano po probach (uwaga 15).
- Czasy: start analizy = `Postep.od` (czas zdarzenia "start" silnika, `aplikacja.py:1339`) minus koniec zapisu z dziennika
  symulatora - doslownie; mapa = pierwszy odczyt plytki w stanie co 20 ms - gorne ograniczenie, liczone dla 9 plikow dobrych
  (takze nieprzyjetych); przerwy = odstep tykniec zegara w watku okna - wykrywa blokade (proba 3).
- Kod 0 = "pomiar wykonany" (proba 3: kod 0 przy 4 werdyktach FAIL); werdykty sa w pliku jednoznaczne, bez wiersza lacznego.
- T3 przechodzi SE10 przez okno: wszystkie czynnosci technika to `QTest` po nazwach obiektow; kolejnosc krokow i 32 wiersze
  sa te same co w `test_session_rano._scenariusz` (porownane wiersz po wierszu; tabela importowana z modulu testu). Sztuczne:
  wyniki skanow (`przyjmij_wynik` + prywatne `_po_skanie`, `_odswiez`), zegar, `wypelnij_indeks` (INSERT do bazy) - opisane w O5.
  Liczba "n z 32" porownuje jednak API sesji; ekran jest porownywany osobno w 10 wierszach (uwaga 3).
- "18 z 29 poza czerwonymi": lista = prawda nie jest dowodem wykrywania. W probie wlasnej wszystkie takie prace byly zolte
  (do obejrzenia), zadna zielona - proba 2. Narzedzie tej liczby nie podaje i nie padloby przy zielonej (uwaga 1).

## 3. Kryteria - PLAN_TESTOW.md wobec sekcji 7 planu etapu

Kryterium z planu jest w kazdej sekcji `PLAN_TESTOW.md` przepisane doslownie (porownane z tabela sekcji 7: 14 z 14 zgodnych).

| Test | Kryterium (plan, skrot) | W PLAN_TESTOW | Ocena | Polecenie / dane / dowod / liczenie |
|---|---|---|---|---|
| T0 | program startuje; samokontrola zielona; sumy zgodne | 2 starty kod 0, samokontrola kod 0 i bledy 0, SHA-256 ZIP + licznik sum | rowne (O1 jawne: swiezy katalog, `/bez-sieci` - zgodne z `zlecenie.md` p. 4) | komplet |
| T1 | 0 failed, 0 errors; pominiete tylko znane | ostatni wiersz logu + lista `-rs` wobec 9 znanych | rowne | komplet (uwaga 17) |
| T2 | 10 z 10 wg prawdy; start ponizej 1 s; mapa do 40 s (mediana); okno bez przerw ponad 200 ms; lista = prawda | sterownik: status / uklad / numer; start doslownie dla 9 plikow; mapa - gorne ograniczenie; przerwy od pierwszego tykniecia; lista po kliknieciach wg prawdy | start i mapa: rowne / ostrzejsze; okno: rowne z O3, O4 (offscreen, bez startu programu); 10 z 10: rowne wg decyzji nr 1 (uwaga 12); lista: SLABSZE bez odstepstwa (uwaga 1, B) | komplet; potwierdzone proba 1, 3, 4 |
| T3 | SE10 przez ekran; listy zgodne w 100 % wierszy | 32 z 32 + kolumna "ekran" 10 wierszy | rowne z O5 (jawne: sztuczne wyniki skanow, R31 czesciowo, R17 wcale); narzedzie nie odbija ekranu w liczbie (uwaga 3, P) | komplet; potwierdzone proba 5-8 |
| T4 | top-1 100 %; plytka do 40 s; pamiec do 8 GB | `metryki_pula` zimna / ciepla / jakosc; pierwsza plytka zimna ponad 40 s = "ZAL z odstepstwem" | SLABSZE jawnie (O7, decyzja nr 6) - wymaga decyzji wlasciciela | komplet (uwaga 18); potwierdzone przegladem |
| T5 | 5 z 5, 0 powtorek; plan do 5 s; Spacja ponizej 1 s - w sieci lokalnej | liczby z pytest na 127.0.0.1; czesc B bez liczb | SLABSZE; O8 opisuje mniej, niz zmieniono (uwaga 5, P) | czesc B krok 4 bez polecenia (uwaga 4) |
| T6 | 200 z 200; 0 zlych wierszy; log regula 6 | testy `test_excel.py` na arkuszu w pamieci | inne - jawne (O9); kod z `<REPO>` (uwaga 5) | komplet; liczb testow nie sprawdzalem |
| T7 | 6 przypadkow: komunikat z zal. F, dalsza praca, stan z bazy | testy + 3 proby reczne; komunikat spoza zal. F = "ZAL z odstepstwem" | SLABSZE jawnie (O12, decyzja nr 3) - wymaga decyzji wlasciciela; przypadki 4-6 tylko testami (uwaga 5) | B2 / B3 bez polecenia (uwaga 4) |
| T8 | wartosci raportu = policzone recznie | `raport_metryk` na bazach T2 i T3 + liczenie reczne przez `sql_odczyt` | rowne | bledne sciezki baz (uwaga 4); uwaga 27 |
| T9 | 0 trafien; nazwy tylko w `dane/` | `t9_dane_osobowe.py` na repo, logach, wynikach, zapisie ruchu | rowne w planie; narzedzie daje falszywe ZAL (uwaga 2, B) | uwagi 7, 8 |
| T10 | 40 z 40; top-1 100 %; falszywe czerwone 0 | `metryki_P3a` na 24 + 16 skanach | rowne | komplet; nazwa sekcji zbiorczej do potwierdzenia proba `--limit 2` |
| T11 | uklad rozpoznany albo ostrzezenie z nazwa; 0 zielonych przy zlym; uklad w `skany` | 24 z 40 skanow przez aplikacje; brak rozpoznania = FAIL skanu | regula "albo": ostrzejsze (O6, decyzja nr 4); zakres 24 z 40 i regula liczenia: SLABSZE / bledne (uwaga 6, P) | uwaga 16 |
| T12 | jedno polecenie; ustawienia zachowane; baza zmigrowana z kopia | N -> N+1 -> N + paczka probna z migracja | rowne z O2 (jawne) | czesc B bez polecen (uwaga 11) |
| T13 | tylko pliki z list paczek; nowe ASCII; brak STL i danych | `t13_higiena.py` od 2537f6f | SLABSZE jawnie (O10: poziom katalogow, R58 / R59 poza wynikiem; O11: 7 plikow) - O10 zmienia sens bardziej, niz mowi opis (p. 5) | komplet; uwaga 9; potwierdzone proba 10, 11 |

Razem (14 testow): rowne 7 (T0, T1, T3, T8, T9, T10, T12); ostrzejsze w czesci 2 (T2 start / mapa, T11 regula "albo");
slabsze z jawnym odstepstwem 4 (T4, T6, T7, T13); slabsze bez pelnego odstepstwa 3 (T2 lista, T5, T11 zakres).

Odstepstwa O1-O12: opisane uczciwie - O1, O2, O3, O5, O6, O9, O11, O12. Opis wezszy niz skutek - O4 (brak slowa o liscie,
uwaga 1), O8 (uwaga 5), O10 (uwaga 23). O7 i O12 sa rzetelne, ale to one zamieniaja FAIL na "ZAL z odstepstwem".

Kryteria zlecenia paczki (`odb.md`, `odb-r2.md`):

| Kryterium | Stan |
|---|---|
| odb 1: polecenia T0-T13 sprawdzone co do plikow i opcji | niepotwierdzone w 5 miejscach (uwagi 4, 6, 11, 16); reszta potwierdzona przegladem |
| odb 2: zrodlo kazdej liczby kryterium | potwierdzone przegladem, poza T8 (uwaga 4) i T4 pamiec (uwaga 18) |
| odb 3: brak nazw zlecen, ASCII + LF | potwierdzone proba (rozg.): 0 trafien, 0 bajtow powyzej 127, 0 CR w 16 plikach |
| odb 4: krotka proba kazdego skryptu | potwierdzone wlasnymi probami (p. 2) |
| r2 1: oba sterowniki - proba kodem 0 z plikiem wyniku | potwierdzone wlasna proba (1 i 5) |
| r2 2: `--help`, limit czasu, sprzatanie procesow takze po bledzie | potwierdzone wlasna proba (limit: proba 4; T2: 12 PID-ow z 	2_pid.txt 3 przebiegow nie zyje; T3: sterownik zglasza 0 procesow potomnych do zabicia w 4 przebiegach); straznik zawieszonej petli nie byl probowany (takze przez wykonawce) |
| r2 3: ASCII + LF, bez nazw zlecen | potwierdzone (rozg.) |
| decyzje 1-6 wpisane do planu i raportu | potwierdzone przegladem (T2, T3, T7, T11, T13, T4; `RAPORT.md` O3-O7, O11, O12, decyzje 12-17) |

## 4. Zakres plikow i zasady

- (rozg.) 16 plikow, wszystkie nowe, wszystkie w `Ramki/etap3/odbior_koncowy/`; najwiekszy 75 KB; duzych danych i STL brak.
- (rozg.) ASCII + LF: 0 bajtow powyzej 127 i 0 CR w kazdym z 16 plikow (tresc z gita).
- (rozg.) Dane osobowe: 49 nazw folderow i plikow katalogu prac testowych - 0 trafien calych nazw w 16 plikach; imion i
  nazwisk 0. `T13/proba_*.txt`: tylko sciezki kodu.
- `ODLOZONE.md` (rozg.): T15, T16, T17 i otwarte 4-6 z wpisu 19.11 maja kazde powod i warunek wznowienia; tresc 4-6 zgodna
  z wpisem; odlozen bez powodu nie ma. Wykonalne na PC, a przesuniete jawnie: Excel przez COM (O9 -> T17), ramka poranna
  na programie z paczki (O8).
- `RAPORT.md`: tabela T0-T17 z kolumna wyniku, licznikami i sciezkami dowodow; pola T0-T14 puste, T15-T17 "ODLOZONE (do
  potwierdzenia)"; wynikow "na zapas" nie ma (uwagi 25, 26).
- `T14/README.md`: 9 wskazanych sciezek istnieje na origin/e3/a11d; A11d nie jest jeszcze w `main`; `przycisk_nowa_plytka`
  jest w `ui/czesci.py`; 2 znaczniki - co wpisac: uwaga 10.
- Kopia `qc-wt\integ` po probach bez zmian; cudzych procesow nie ruszalem.

## 5. Do decyzji wlasciciela

1. T2 "lista do dofrezowania = prawda" (uwaga 1): czy technik-sterownik ma klikac wg prawdy, czy tylko prace pokazane jako
   czerwone / zolte. W probach program sam oznaczyl na czerwono 5 z 12 (proba wlasna) i 11 z 29 (wykonawca) prac z
   ubytkiem; pozostale 7 z 12 byly zolte, zielonych 0.
2. O7 (T4, T2): pierwsza plytka po zimnym starcie ponad 40 s = "ZAL z odstepstwem". Zmierzone: 41,96 s (proba wlasna),
   36,7-51,5 s (wykonawca), 63-68 s (raporty A5 / A5i). Przy odstepie 60 s druga plytka moze przez to czekac w kolejce i
   dac FAIL "start analizy ponizej 1 s" - tego plan nie lagodzi.
3. O12 (T7): komunikat spoza PW zal. F = "ZAL z odstepstwem" - uzupelnic zalacznik albo zmienic napisy.
4. O5 (T3): po restarcie ekran pokazuje tylko ostatni zamkniety piec (R31), listy "do dofrezowania" ekran poranny nie
   pokazuje (R17); okno nie pyta przed "Zamknij piec", gdy praca nieznana ma decyzje "bez projektu" (uwaga 20).
5. O4 (T2): przerwy petli mierzone w oknie offscreen - bez kosztu rysowania na prawdziwym ekranie.
6. O8 / O9 (T5, T6): liczby z testow na 127.0.0.1 i na arkuszu w pamieci; Excel przez COM jest na PC, a zostal przeniesiony do T17.
7. O10 (T13): kontrola na poziomie katalogow; pliki R58 / R59 (wg rozg.: 2 STL, 7 plikow danych, 11 duzych) poza wynikiem;
   pliki nietykalne zmienione od poczatku etapu nie sa wyroznione.
8. T11: druga galaz kryterium (ostrzezenie z nazwa wlasciwego ukladu) jest w programie niespelnialna (brak B5).
9. T12: powrot po migracji bazy wymaga 2 polecen (uwaga 11).
10. Czy "ZAL z odstepstwem" liczy sie jako zaliczenie konca etapu (uwaga 26).
11. `ui/kandydaci.py`: poprawka komentarza przed wydaniem czy FAIL w T13 (uwaga 28).

WERDYKT: do scalenia po poprawkach (B 2: uwagi 1, 2; P 9: uwagi 3-11; D 17: uwagi 12-28)
