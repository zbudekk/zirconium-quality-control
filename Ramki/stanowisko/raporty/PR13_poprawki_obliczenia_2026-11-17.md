# PR #13 - poprawki po recenzji, czesc "obliczenia" (B1, P1, P7, D4-D8)

Data: 2026-11-17. Wykonawca: subsesja poprawek (obliczenia). Podstawa: `recenzja/raport_recenzenta_PR13_runda1.md`
(uwagi B1, P1, P7, D4, D5, D6, D7 czesc (b), D8). Start: `a6cf3a4` (`origin/przed-skanerem`), galaz `przed-skanerem-p1`.
Zakres plikow: `stanowisko/inspect.py`, `krawedz.py`, `porownaj.py`, testy tych modulow, opisy modulow,
`narzedzia/pomiar_skanu/c_wspolne.py`, ten raport. Nie ruszane: `match.py`, `plate.py`, `synth.py`, `dzien_skanera*`,
`ustawienia*`, progi, `modele_plytek`, plik stanu, `recenzja/`. Obliczenia tylko na PC (`<PC-katalog>\app\p1`), na MSI
edycja i git.

## 1. Co zrobiono

| Uwaga | Stan | Zmiana | Test (czerwony na `a6cf3a4`) |
|---|---|---|---|
| B1 | zrobione | `inspect._linia_brzegu`: odleglosc od linii i numer filaru tylko, gdy projekt ma linie (`brzeg.drzewo is not None`); bez linii - odleglosc od z = 0 i `filar` = 0, czyli wynik jak przy pasie od plaszczyzny. `probka_od_linii` sprawdza takze `drzewo_O`. | `test_inspect.py::test_projekt_bez_linii_z_wcieciem_w_trybie_sumy_dziala_jak_przed_p2` - scenariusz recenzenta (pudelko 8 x 6 x 5, wglebienie 0,3 mm na scianie i na wierzchu): przed `AttributeError` w `_linia_brzegu`, po `ubytek` A+B czerwony / `sprawdz` B zolty, ubytki, plamy i wciecia identyczne z trybem `plaszczyzna` |
| P1 | zrobione | `krawedz.LinieProjektu.filary_bez_linii` (numery filarow z przyjeta niecka bez linii, liczone z `niecki`), `stan` = `czesciowe`, gdy taki filar jest, `opis()` podaje liste. `inspect.ocena_brzegu`: tryb `linia` - filar liczony jako nie sprawdzony (numer w `nie_sprawdzono`, wpis w `filary` z `werdykt_linii` = `brak`, `powody` = [`linia`]) -> status `nie_sprawdzono`; tryb domyslny - pas od plaszczyzny jak przed P2 + uwaga w `uwagi_linii` i `uwagi`. Nowe pole `brzeg.filary_bez_linii` tylko wtedy, gdy taki filar jest. | `test_inspect.py::test_filar_z_niecka_bez_linii_nie_znika_po_cichu` (przed: tryb `linia` = `ok`, tryb domyslny bez uwagi), `test_krawedz.py::test_filar_z_niecka_bez_linii_jest_jawny` (przed: `stan` = `wiarygodne`) |
| P7 | zrobione | `porownaj.dopasuj_fragmenty`: `try` na gniazdo wokol `inspect.sprawdz`; wyjatek -> wpis `inspekcja_z_bledem` (zwykle pola wyniku inspekcji, status `nie_sprawdzono`, uwaga "blad inspekcji: <typ>: <tresc> (<plik>:<linia> <funkcja>)", pole `blad`), ostrzezenie, wiersz w tabeli; reszta plytki liczona, JSON zapisany. `MemoryError` przepuszczany jawnie, `KeyboardInterrupt` / `SystemExit` nie sa lapane (`except Exception`). | `test_porownaj_bledy.py::test_blad_inspekcji_jednego_gniazda_nie_kladzie_plytki`, `::test_cli_zapisuje_wynik_mimo_bledu_inspekcji` (oba czerwone przed), `::test_przerwanie_i_brak_pamieci_nie_sa_lapane` (3 przypadki, zielone przed i po - pilnuja, zeby lapanie nie objelo przerwania) |
| D4 | zrobione | jedno zdanie w granicach `opisy_modulow/match.md` (korekta skali wylacza tylko pas od plaszczyzny) | - |
| D5 | zrobione | tresc uwagi o niepewnej linii projektu w trybie domyslnym (bez zmiany logiki): mowi, ze pas od plaszczyzny obejmuje brzeg tylko do `pas_brzegu_mm` ponizej najwyzszego punktu pracy | istniejacy `test_linia_projektu_niepewna_albo_brak_linii_to_nie_sprawdzono` (szuka "linia projektu niepewna") |
| D6 | zrobione | jedno zdanie w granicach `opisy_modulow/synth.md` (ubytki tylko przy zweryfikowanej linii -> wykrywalnosc to gorna granica) | - |
| D7 (b) | zrobione | `opisy_modulow/inspect.md`: akapit "Tryby pasa brzegu" (domyslny `linia_i_plaszczyzna`, `linia`, `plaszczyzna`), tabela przypadkow bez pelnej linii po B1 / P1, akapit o bledzie inspekcji (P7), pola `uwagi_linii` i `filary_bez_linii`, liczba testow; `krawedz.md`: `filary_bez_linii` | - |
| D8 | zrobione | `narzedzia/pomiar_skanu/c_wspolne.py`: usunieta stala `PRACE` ze sciezka konta i import `Path` | - (patrz odstepstwo 3) |

Commity (`a6cf3a4..HEAD`): `f8d8c18` B1, `2ed0bd8` P1, `e2c8bcc` P7, `bea6a54` D8, `0c37e1e` D5, `43790ba` opisy modulow
(D4, D6, D7 b), ostatni - ten raport.

Testy nowe na kodzie sprzed poprawek (`a6cf3a4`, PC, `logi\czerwone_a6cf3a4.log`): 5 failed, 3 passed - czerwone sa
dokladnie testy B1, P1 (2) i P7 (2), kazdy w scenariuszu z raportu recenzenta; 3 zielone to przypadki "nie lap".

## 2. Decyzje, ktore warto obejrzec w recenzji przyrostowej

1. **P7: status `nie_sprawdzono`, nie `sprawdz`.** Slownik statusow (`inspect.STATUSY`, `porownaj.INSPECT_NA_STATUS`,
   `OPISY_INSPEKCJI`): `sprawdz` = "jedna z metod wskazala ubytek" i w `metryki_inspekcji` liczy sie jako alarm
   (`prace_cale_z_alarmem`); `nie_sprawdzono` = "nie dalo sie sprawdzic - nigdy zielone, nigdy czerwone", zolte gniazdo z
   wlasnym podpisem na mapie, w tabeli i w oknie. Blad inspekcji znaczy, ze pracy nie sprawdzono, wiec wybrany
   `nie_sprawdzono` z uwaga "blad inspekcji: ..." i polem `blad` (po nim da sie odroznic blad od braku danych przy linii).
   `status_gniazda` daje dla takiego wpisu zolty przy kazdym statusie match poza szarym (szary nie ma inspekcji).
2. **P7: wpis nie trafia do `podglad`.** Okno (`ui_test.py`, nie zmieniane) dla gniazda bez wpisu pokazuje "brak mapy
   odchylek" - bez wyjatku. Uwaga z bledem jest w JSON, w ostrzezeniach i w tabeli CLI; okno jej nie wyswietla (pokazuje
   podpis "nie sprawdzono" i licznik "z zoltych nie sprawdzono") - do rozwazenia w paczce okna.
3. **P1: wpis w `brzeg.filary` tylko w trybie `linia`.** Tam jedyna kontrola brzegu jest linia, wiec filar bez linii
   dostaje wpis ze `sprawdzony` = false (`filarow` go liczy). W trybie domyslnym brzegu tego filaru nie ocenia sie od
   linii (jak dla projektu bez zadnej linii: `sprawdzony` = true, pas sprzed P2), wiec wpisu nie ma - jest uwaga i pole
   `filary_bez_linii`. Narzedzia czytajace `filary` (`metryki_krawedz.py`, `metryki_P3a.py`) uzywaja pol `sprawdzony`,
   `powody`, `udzial_sprawdzony`, `nr` - wpis ma komplet pol zwyklego wpisu.
4. **P1: `LinieProjektu.stan`.** Projekt z filarem bez linii mial `stan` = `wiarygodne`, jesli pozostale filary byly
   wiarygodne; teraz `czesciowe`. `stan` czyta tylko `inspect` (`brzeg.stan_linii`) i testy. Wersja pamieci linii na
   dysku (`WERSJA`) bez zmiany: algorytm ten sam, a `filary_bez_linii` liczy sie z `niecki`, ktore sa w starych plikach.
5. **Wyjatek w samym wyznaczaniu linii (`krawedz`)** nie jest lapany w `inspect.brzeg_projektu` - po P7 daje zolte
   "nie sprawdzono / blad inspekcji" dla gniazda (na `main` taka praca bylaby liczona pasem od plaszczyzny). Zamiana na
   "brak linii -> pas sprzed P2" bylaby zmiana logiki poza zleceniem (moglaby dac zielone po bledzie) - zostawione.

## 3. Przeglad `inspect.py`: drzewa i tablice linii wobec `None` / pustych tablic

| Miejsce | Sytuacja | Wynik przegladu |
|---|---|---|
| `brzeg_projektu` | projekt bez stacji | `drzewo` i `drzewo_O` = `None` (bez zmiany) |
| `plamy_pod_powierzchnia` | `brzeg` None / `drzewo` None | obsluzone przed poprawka (suma: od z = 0, linia: brak pasa) |
| `probka_od_linii` | `drzewo` None; brak trojkatow przy linii; zero punktow w pasie | pusta probka; dodany warunek na `drzewo_O`; zapytanie drzewa pusta tablica jest poprawne |
| `probka_suma` | brak linii / pusty pas od plaszczyzny | sklejanie pustych tablic (0, 3) poprawne; czesc od linii = 0 punktow |
| `_linia_brzegu` | skupisko wciec, `drzewo` None | **B1 - poprawione**; pusta probka albo pusty skan = wczesny powrot bez maski |
| `ocena_brzegu` | brak filarow; `ma_dane` None; zero punktow probki przy stacjach | wczesny powrot / same "bez danych"; `bincount` z `minlength`; **P1 - filar bez linii** |
| `sprawdz` | `ma_dane` None, przyciecie maski do czesci od linii | poprawne (maska i `st_O` z tej samej probki) |
| `_odcinki_bez_sprawdzenia`, `wykryj_drgniecie`, `polozenie_ubytku_prawdy` | puste tablice, `drzewo` None | obsluzone przed poprawka |

Innego miejsca, w ktorym `None` albo pusta tablica linii konczy sie wyjatkiem, nie znalazlem. Sciezki nieznane lapie P7.

## 4. Warunek: wynik na zwyklych danych bez zmian

**4.1. Rownosci "co do bitu" dwoch niezaleznych przebiegow nie da sie uzyskac takze bez zmiany kodu.** Lancuch
`plate -> match` (ICP / RANSAC w Open3D) nie jest powtarzalny miedzy uruchomieniami tego samego kodu:

- Ten sam skan (`r54_P2 / skan_okragla_poranna_r54_n9_s0200`) dwa razy kodem `a6cf3a4`, biblioteki ograniczone do 1 watku
  (`wyniki\det_a`, `det_b`): z 2245 pol 1984 rowne dokladnie, 244 liczby rozne o <= 1e-9, 17 pol roznych bardziej (jedno
  gniazdo: transformacja z `match` rozna od 6. cyfry, `pewnosc` 0,7653 / 0,7654). Pierwsza roznica powstaje juz w
  `plate` (`jakosc_wyrownania.icp_poprawka_mm`).
- 12 skanow dwa razy kodem `a6cf3a4` (`wyniki\baza`, `baza2`; 4 ostatnie skany powtorki przerwalo zatrzymanie PC ok.
  16:00): 0 plikow rownych co do bitu, 4 rowne z dokladnoscia 1e-9, 8 z wiekszymi roznicami (379 z 28 945 pol; dalsi
  kandydaci rankingu `match` dostaja zupelnie inne transformacje, czasem inny projekt na 4.-5. miejscu). Po
  rozstrzygnieciach: 122 z 123 gniazd takie same, 1 gniazdo (fragment `podwojny`) raz `skan_ponownie`, raz `nie_sprawdzono`.

Dlatego dowod jest dwustopniowy: (a) ten sam skan przez `porownaj.main` kodu przed i po na IDENTYCZNYCH wynikach
`plate` i `match` - tu wymagana rownosc pole po polu; (b) niezalezne przebiegi przed / po porownane po rozstrzygnieciach,
na tle szumu "przed / przed".

**4.2. (a) Te same wyniki plate i match, kod przed i po (dowod wlasciwy).** Skrypt `p1\skrypty\dwa.py`: jeden proces na
skan, kod po = pakiet `stanowisko` (`43790ba`), kod przed = pakiet z `p1\baza` (`a6cf3a4`) wczytany pod nazwa
`stanowisko_baza`; `match.Pula`, `plate.wyrownaj` i `match.dopasuj` licza sie raz i sa podstawiane obu wersjom (`match.py`
i `plate.py` maja w obu katalogach ten sam SHA-256), a inspect, krawedz i porownaj (statusy gniazd, metryki, zapis JSON)
ida osobno kodem kazdej wersji przez jej `porownaj.main`. Skany: 16 = 4 typy plytek x zestawy r54 i R59 x po jednym z P2
i P3a (`--plytka` z nazwy pliku, `--wspolczynnik` z prawdy, `--prawda`, ustawienia = `ustawienia_wzor_pc.toml`, czyli
tryb domyslny `linia_i_plaszczyzna`). Porownanie: `p1\skrypty\rown.py` (wszystkie pola JSON rekurencyjnie; pomijane
tylko klucze zaczynajace sie od `czas`).

Wynik (`logi\rown_dwa_surowe.log`, `logi\rown_dwa_norma.log`): **16 z 16 skanow - wszystkie pola poza trescia uwagi D5
rowne co do znaku.**

| Licznik | Wartosc |
|---|---|
| skany / gniazda / gniazda z inspekcja | 16 / 169 / 150 |
| pola porownane (w tym liczbowe) | 40 053 (26 651) |
| pola rowne dokladnie | 40 005 - w tym wszystkie liczbowe (najwieksza roznica liczby: 0) |
| pola rozne tylko trescia uwagi D5 (`brzeg.uwagi_linii` i wpisy `uwagi`; rowne po `--norma-d5`) | 48 |
| pola rozne inaczej | 0 |
| pola tylko w wyniku "po" (`filary_bez_linii`, `blad`) / tylko "przed" | 0 / 0 |
| pola czasu pominiete | 887 |

| Skan | pol | tylko D5 | gniazd / z inspekcja |
|---|---|---|---|
| r54_P2 wieczorna n3 s0100 | 2026 | 2 | 9 / 9 |
| r54_P2 poranna n4 s0200 | 1829 | 2 | 8 / 8 |
| r54_P2 okragla_wieczorna n8 s0100 | 2619 | 6 | 11 / 11 |
| r54_P2 okragla_poranna n9 s0200 | 2245 | 2 | 9 / 9 |
| r54_P3a wieczorna n1 s0320 | 2791 | 4 | 12 / 8 |
| r54_P3a poranna n5 s0330 | 2824 | 2 | 12 / 8 |
| r54_P3a okragla_wieczorna n8 s0300 | 2953 | 4 | 12 / 10 |
| r54_P3a okragla_poranna n9 s0310 | 2129 | 2 | 10 / 10 |
| R59_P2 wieczorna n3 s0100 | 1851 | 2 | 8 / 8 |
| R59_P2 poranna n4 s0200 | 2592 | 2 | 12 / 12 |
| R59_P2 okragla_wieczorna n8 s0100 | 2108 | 4 | 8 / 8 |
| R59_P2 okragla_poranna n9 s0200 | 2993 | 4 | 12 / 12 |
| R59_P3a wieczorna n1 s0320 | 2660 | 2 | 10 / 8 |
| R59_P3a poranna n5 s0330 | 2565 | 4 | 11 / 9 |
| R59_P3a okragla_wieczorna n8 s0300 | 2625 | 4 | 11 / 9 |
| R59_P3a okragla_poranna n9 s0310 | 3243 | 2 | 14 / 11 |

Statusy inspect w tych skanach: `ok`, `ubytek`, `sprawdz`, `skan_ponownie`, `nie_sprawdzono`, `popraw_ulozenie`, `poprawka`
(oraz gniazda szare bez inspekcji). Dodatkowo jeden skan (r54_P3a
okragla_wieczorna) na kodzie `bea6a54`, czyli przed zmiana tekstu D5 (`wyniki\dwa_proba`): 2953 pola, wszystkie rowne co
do bitu.

Uwagi do przebiegu: (1) pierwsza wersja `dwa.py` nie powtarzala ostrzezen `plate` wersji liczonej jako druga (pole
`ostrzezenia`: "dolki kodu poza skanem" tylko w wyniku "po") - poprawione w skrypcie (ostrzezenia z prawdziwego
liczenia sa zapamietane i powtarzane obu wersjom), 8 skanow plytek kwadratowych policzonych ponownie; (2) czesc
przebiegow przerwalo zatrzymanie PC ok. 16:00 (jeden plik wyniku uszkodzony) - powtorzone; liczniki wyzej sa z
przebiegow zakonczonych, po jednym procesie naraz.

**4.3. (b) Niezalezne przebiegi.** `p1\skrypty\por.py` (zwykle `python -m stanowisko.porownaj` na tych samych 16 skanach),
porownanie rozstrzygniec `p1\skrypty\kat.py` (na gniazdo: status match, kolor gniazda, projekt top-1, status inspect,
ubytki (metoda, kolor), filary nie sprawdzone; na plytke: liczniki statusow, liczba ubytkow, numer).

| Porownanie | plytki rowne | gniazda rowne | pola JSON (`rown.py`, tolerancja 1e-9) |
|---|---|---|---|
| przed / przed (`baza` / `baza2`, `a6cf3a4`, 12 skanow) | 11 z 12 | 122 z 123 | 28 945 pol: 25 011 rownych dokladnie, 3557 liczb w tolerancji, 379 roznych |
| przed / po (`baza` / `po_bez_D5`, `a6cf3a4` / `bea6a54`, 16 skanow) | 13 z 16 | 166 z 169 | 40 028 pol: 34 252 rownych dokladnie, 5167 liczb w tolerancji, 633 rozne |

Trzy gniazda rozne w "przed / po" to fragmenty `podwojny` (r54_P3a okragla_wieczorna gn. 17, R59_P3a okragla_poranna
gn. 1, R59_P3a okragla_wieczorna gn. 11): rozni sie juz wynik `match` (status albo projekt top-1), czyli wejscie
inspekcji. Gniazdo 17 rozni sie tak samo w "przed / przed" (`skan_ponownie` / `nie_sprawdzono`). Na tych samych wynikach
`plate` / `match` (pkt 4.2) wszystkie trzy skany sa rowne. Wniosek: roznice niezaleznych przebiegow to szum lancucha,
nie skutek poprawek.

## 5. Pytest (PC, caly katalog `testy`)

| Kod | Wynik | Log |
|---|---|---|
| przed: `5ef199e` (kod = `a6cf3a4`; punkt odniesienia koordynatora) | 408 passed, 3 skipped, 0 failed (820 s) | `k2\pytest_5ef199e.log` |
| po: `43790ba` (wszystkie zmiany kodu i testow; ostatni commit dodaje tylko ten raport) | **416 passed, 3 skipped, 0 failed** (595 s) | `p1\logi\pytest_43790ba.log` |

Roznica + 8 = nowe przypadki: `test_inspect.py` 2, `test_krawedz.py` 1, `test_porownaj_bledy.py` 5 (3 funkcje, jedna z 3
parametrami). Zadnego istniejacego testu nie zmieniono ani nie oslabiono. Pelny pytest uruchomiony raz, na koncu, jako
jedyny proces python tej sesji, z limitem 2 watkow bibliotek. Kopia na PC = `git archive 43790ba` (zgodnosc SHA-256
zmienionych plikow z drzewem roboczym sprawdzona); `git init` + `git add Ramki` w `p1` dla testu sledzonych plikow.
Wczesniej, w trakcie pracy: nowe testy na `a6cf3a4` - 5 failed, 3 passed (pkt 1); pliki `test_porownaj_bledy.py`,
`test_krawedz.py`, `test_inspect.py` na kodzie `bea6a54` - 46 passed.

## 6. Odstepstwa

1. **Dowod "JSON-y rowne pole po polu" jest z tych samych wynikow plate i match (pkt 4.2), nie z dwoch niezaleznych
   przebiegow** - niezalezne przebiegi tego samego kodu roznia sie miedzy soba (pkt 4.1). Dotyczy to takze innych
   porownan "przed / po" robionych osobnymi przebiegami: roznice w gniazdach `podwojny` moga byc szumem, nie skutkiem zmian.
2. **D5 zmienia tekst w wyniku** (`brzeg.uwagi_linii`, `uwagi`) dla prac z niepewna linia projektu w trybie domyslnym -
   zlecone ("doprecyzuj tresc"), wiec te pola nie sa rowne co do znaku; `rown.py --norma-d5` zamienia stara i nowa
   koncowke uwagi na ten sam znacznik (scisle wyrazenia regularne) i liczy takie pola osobno. Statusy i liczby bez zmian.
3. **D8: stala nie byla calkiem nieuzywana** - czytala ja `wczytaj_pule()` na koncu pliku, ktorej nikt nie wola
   (`pomiar_skanu.py` bierze z `c_wspolne` tylko `linie_krawedzi`). Stala usunieta, a funkcja dostaje folder jako argument.
4. **Skrypty pomocnicze (`por.py`, `dwa.py`, `rown.py`, `kat.py`) nie sa w repozytorium** (poza lista plikow do zmiany) -
   leza w `<PC-katalog>\app\p1\skrypty`, wyniki w `p1\wyniki`, logi w `p1\logi`.
5. `ustawienia.przyklad.toml:59` i `README.md` opisuja zachowanie trybow - poza lista plikow, nie zmieniane; tresc jest
   zgodna z kodem po poprawkach (tryb `linia`: projekt / filar bez linii = "nie sprawdzono").

## 7. Czego nie sprawdzono

- Scenariusza P1 na prawdziwym projekcie (w puli 17 projektow nie wystepuje: 23 petle z 23) - test wywoluje go
  sztucznie (lista `filary` bez jednego filaru przy przyjetej niecce; w `test_krawedz` przez wyzerowanie przekrojow).
- P7 z prawdziwym wyjatkiem inspekcji (jedyny znany, B1, jest naprawiony) - test podstawia wyjatek w `inspect.sprawdz`.
- Okna (`ui_test.py`) z wpisem bledu inspekcji - tylko czytaniem kodu okna (pkt 2.2).
- Pomiarow koncowych czesci A i B (licza inne sesje); pkt 4.2 mowi tylko, ze na tych samych wynikach plate / match
  poprawki nie zmieniaja wyniku 16 skanow odniesienia.

## 8. Polecenia (PC, `cmd.exe`, katalog `<PC-katalog>\app\p1`)

```
run.cmd -m pytest -q -p no:cacheprovider                                  (kod po; run_baza.cmd = kod a6cf3a4 w p1\baza)
run.cmd skrypty\dwa.py wyniki\dwa_43790ba --jeden <zestaw> <skan>         (4.2: przed i po na tych samych plate / match;
                                                                           kolejka.cmd, kolejka2.cmd = skany po kolei)
run.cmd skrypty\rown.py wyniki\dwa_43790ba\przed wyniki\dwa_43790ba\po [--norma-d5]
run_baza.cmd skrypty\por.py wyniki\baza --procesy 4                       (4.3: niezalezne przebiegi; baza2 = powtorka)
run.cmd skrypty\por.py wyniki\po_bez_D5 --procesy 4                       (kod bea6a54)
run.cmd skrypty\kat.py wyniki\baza wyniki\baza2 ; run.cmd skrypty\kat.py wyniki\baza wyniki\po_bez_D5
```

Obciazenie PC: do ok. 16:00 ta sesja liczyla rownolegle (przebiegi 4.3 po 4 procesy, pierwsze podejscie do 4.2 w 6
procesach i pytest - razem do 11 procesow python), co dolozylo sie do przeciazenia PC, po ktorym wlasciciel zatrzymal
komputer. Po komunikacie koordynatora: jeden proces python naraz, `OMP / OPENBLAS / MKL_NUM_THREADS=2` w `run.cmd` i
`run_baza.cmd`, pelny pytest raz na koncu po sprawdzeniu wolnego RAM (9 GB). Wlasny proces pytest uruchomiony o 16:09,
jeszcze przed odczytaniem komunikatu, zostal zakonczony (`Stop-Process` po sprawdzeniu katalogu biezacego procesu -
cudzych procesow nie ruszano).
