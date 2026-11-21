WERDYKT T9: ZAL z odstepstwem NOWE (nazwy zlecen = pula testowa + drzewo A5i, 435 nazw: 0 trafien calych nazw w repo 1265 plikow + 597 commitow, w worktree e3/odbior 9d9850a, w katalogach testow 1172 pliki, w plikach wynikow 120, w instalacjach 739, w ruchu do ramki 2 zapisy / 75 zadan i w katalogu dowodow 394 pliki; proba dodatnia dziala: 66 trafien dozwolonych w 2 bazach SE10; NOWE: z pelnym N planu kroki 1 i 2 koncza sie kodem 1 - 98 trafien 14 nazw SZTUCZNYCH SE10 w plikach testow repo, ich historii i 2 plikach T1\robocze; test test_zz_k8 doslownie 1 failed / 1 passed przez prog objetosci zapisu, trafien nazw 0)

# T9 - Dane osobowe - WYNIK (odbior 21.11.2026)

Wykonawca: sesja T9 (ostatni test odbioru). Plik prowadzony przyrostowo. Start pracy 05:44.
`<REPO>` = `<PC-katalog>\t0\repo` (571e186, tylko odczyt), `<ODB>` = `<REPO>\Ramki\etap3\odbior_koncowy`,
`<K>` = `<PC-katalog>\t0\odbior\Stanowisko`, `<ROB>` = `<PC-katalog>\koordynator\robocze\odbior\T9`,
`ODB_ROB` = `<PC-katalog>\koordynator\robocze\odbior`, `PY` = `<PC>\AppData\Local\Programs\Python\Python312\python.exe`,
`T9` = `PY -I <ODB>\narzedzia\t9_dane_osobowe.py`.

Zasada: w tym pliku, w logach i w wiadomosciach sa tylko liczby, `sha16` i sciezki z zamaskowanymi czlonami - zadnej
nazwy folderu / pliku zlecenia ani czlonu nazwy.

## Zrodla nazw (`N`) - zamrozone o 05:47 w pliku `t9_N.txt` (jeden argument w wierszu)

9 x `--nazwy-z` (katalogi nadrzedne folderow zlecen):

1. `<PC-katalog>\app\Prace_test` (pula testowa, 15 folderow),
2. `<PC-katalog>\e3\a5i\t4\drzewo\Cyrkon` (drzewo sztuczne A5i, 47 folderow),
3. `<PC-katalog>\t0\odbior\dane\Cyrkon` (instalacja wspolna, 15 folderow),
4. `<PC-katalog>\t0\odbior_t12\dane\Cyrkon` (instalacja T12, 15 folderow),
5. - 9. kopie puli testowej w katalogach roboczych testow (po 15 folderow): `ODB_ROB\T11\robocze\Cyrkon`,
   `ODB_ROB\T2\robocze\Cyrkon`, `ODB_ROB\T5\robocze\Cyrkon`, `ODB_ROB\T7\robocze\Cyrkon`, `ODB_ROB\T7\uzup\robocze\Cyrkon`.

36 x `--baza` (tabele `zlecenia.folder`, `projekty.plik`): bazy obu instalacji (`<K>\dane\stanowisko.sqlite`,
`<PC-katalog>\t0\odbior_t12\Stanowisko\dane\stanowisko.sqlite` + 1 kopia w `kopie\`) i WSZYSTKIE 33 pliki `*.sqlite`
w `ODB_ROB` poza `\wersje\`, `\paczka_M\`, `\drzewo_M\` (m.in. baza T2 `T2\t2\dane`, baza SE10 `T3\t3\baza`, baza
`T3\t3_tmp\se100\dane`, T5 `t5_wieczor\dane`, T11 `robocze\dane`, T7 `robocze\b*` i `uzup\robocze\p*`, T12 `K_B`, `K_B2`
z kopiami, kopie T8 `robocze\baza_t2.sqlite`, `baza_t3.sqlite`). Pelna lista: `t9_N.txt`.

Foldery `Prywatne` wszystkich instalacji i testow sa puste (0 podfolderow) - nie sa zrodlem.

Sposob uruchamiania: `krok_t9.ps1` (w `<ROB>`) sklada polecenie `PY -I <ODB>\narzedzia\t9_dane_osobowe.py <N z t9_N.txt>
<opcje kroku> --wynik <plik>`; pelne polecenie kazdego przebiegu jest w `t9_polecenia.txt`, kod wyjscia i godziny w
`kody.txt`. POLECENIE PLANU ZMIENIONE tylko co do formy: plan pisze polecenia dla `cmd.exe`; `N` z 45 sciezkami + 76
celow kroku 3 przekracza limit 8191 znakow wiersza `cmd.exe`, dlatego narzedzie jest wolane z PowerShell z lista
argumentow (te same opcje, to samo narzedzie, `--wynik` zamiast przekierowania).

## Przebieg (dopisywany po kazdym kroku)

Samotest narzedzia w KAZDYM przebiegu: "nieznalezionych 0" (pelne N: nazw 449, czlonow 61, tekstow maski 524, postaci
sprawdzonych 8229; N bez baz SE10: nazw 435, czlonow 48, postaci 7749); nazw pominietych jako krotsze niz 4 znaki: 0;
nazw bez postaci ASCII: 7 (dla nich postac "bez znakow diakrytycznych" nie jest sprawdzana samotestem).

Sklad N (plik `t9_zrodla_repo.txt`, pomocnik `robocze\t9_analiza.py` - wypisuje tylko liczby i sha16): 449 roznych nazw =
32 z puli testowej (15 folderow + 17 plikow STL; te same 32 w 7 kopiach puli) + 420 z drzewa sztucznego A5i (17
wspolnych z pula: nazwy plikow STL) + 14 nazw SZTUCZNYCH SE10 (5 folderow + 9 plikow projektow), ktore sa tylko w 3
bazach: `T3\t3\baza`, `T3\t3_tmp\se100\dane`, `T8\robocze\baza_t3.sqlite`. Pozostale 33 bazy (obie instalacje, T2, T5,
T7, T11, T12) maja 0 nazw: `sql_odczyt.py ... "SELECT count(*) FROM zlecenia"` = 0 i `FROM projekty` = 0 (program z
paczki ma `pula_wpisow = false`; liczby w `t9_sql_liczby.txt`; baza SE10: zlecenia 5, projekty 9).

### Krok 1 - repo `<REPO>` (571e186) z historia `2537f6f..HEAD`

| Proba | Polecenie (opcje poza N) | Godz. | Kod | Wynik narzedzia |
|---|---|---|---|---|
| 1 (doslownie, pelne N) | `--repo <PC-katalog>\t0\repo --json <ROB>\t9_repo.json --wynik <ROB>\t9_repo.txt` | 05:48:00-05:48:53 | **1** | przeszukanych 1862 (1265 plikow sledzonych + 597 commitow), nieprzeszukanych 798, zmian binarnych w historii z nieprzeszukana trescia 136; **TRAFIENIA calych nazw: 96 w 13 miejscach** (6 plikow sledzonych + 7 commitow); czlony 9158 w 883; "FAIL" |
| 2 (N bez 3 baz SE10 = pula testowa + drzewo A5i + 33 bazy, plik `t9_N_bez_SE10.txt`) | jw., pliki `t9_repo_bez_SE10.txt`, `.json` | 05:50:41-05:51:28 | **0** | przeszukanych 1862, nieprzeszukanych 798; **TRAFIENIA calych nazw: 0 w 0 plikach**; czlony 9020 w 876; "ZAL - czlony do wyjasnienia" |

Proba 1 - co trafiono (przypisanie sha16 do zrodel: `t9_zrodla_repo.txt`): 14 roznych sha16, WSZYSTKIE 14 sa wylacznie w 3
bazach SE10 (0 z puli testowej, 0 z drzewa A5i). Miejsca: `Ramki/stanowisko/testy/dane_sesji/indeks.json` (16 trafien),
`.../dane_sesji/rano/se10.json` (14), `testy/test_baza.py` (10), `test_excel.py` (2), `test_nazwy.py` (1),
`test_session_rano.py` (5) oraz 7 commitow historii (48 trafien: 783d4969a84e, b3e16ebcb134, 0c29a7d3a79e, 1adc2e84e1b0,
d84b8422c878, da49f0af4bfe, 9ee7801391c4 - commity, ktore te pliki testow dodawaly / zmienialy). To sa DANE SZTUCZNE testow
programu: baze SE10 sterownik T3 buduje wlasnie z `<ST>\testy\dane_sesji\rano\se10.json` (plan: "dane i tabela SE10 z
`<ST>\testy`"; `test_session_rano.py` wiersz 15: "fikcyjne zlecenia i pliki"). Obejrzane przez wykonawce na konsoli (bez
zapisu): kazda z 5 nazw folderow SE10 ma w miejscu nazwiska slowo znaczace "dana sztuczna" (5 roznych slow tego rodzaju) i
pospolite imie, a 9 nazw plikow projektow jest z nich utworzonych. Repo jest wiec ZRODLEM tych 14 nazw, a plan sam dodal
je do N (`--baza <baza SE10>`) jako probe dodatnia - z pelnym N krok 1 nie moze dac kodu 0. Nazwy zlecen z puli testowej
(jedyne nazwy prawdziwych zlecen na tym PC) i nazwy drzewa A5i: 0 trafien w plikach sledzonych i w 597 commitach.

### Krok 1 (ciag dalszy) - katalog dowodow i worktree `e3/odbior`

Znak `ODB_ROB\DOWODY_GOTOWE.txt` byl juz zapisany (05:47:31, HEAD 807aa83); skany wykonane na stanie zastanym o 05:55:
`git -C <PC-katalog>\qc-wt\odbior log --oneline -1` = `3a4afbf` (9 commitow i 400 plikow zmienionych wobec 571e186;
`status --short` pusty; ten sam HEAD przed i po skanach, 05:55:50 i 05:57:37).

| Cel | Polecenie (opcje poza N) | Godz. | Kod | Wynik narzedzia |
|---|---|---|---|---|
| katalog `dowody\` BEZ `--dozwolone`, pelne N | `--cel <PC-katalog>\qc-wt\odbior\Ramki\etap3\odbior_koncowy\dowody --wynik <ROB>\t9_dowody.txt` | 05:55:37-05:55:40 | **0** | przeszukanych 394 z 394 plikow, nieprzeszukanych 0; **TRAFIENIA calych nazw: 0**; dozwolone 0; czlony 232 w 88 plikach (4 rozne) |
| worktree jako repo, N bez baz SE10 | `--repo <PC-katalog>\qc-wt\odbior` -> `t9_repo_odbior_bez_SE10.txt` | 05:55:51-05:56:44 | **0** | przeszukanych 2267 (1661 plikow + 606 commitow), nieprzeszukanych 798, binarne w historii 136; **TRAFIENIA: 0**; czlony 9499 w 967 |
| worktree jako repo, pelne N | `--repo <PC-katalog>\qc-wt\odbior` -> `t9_repo_odbior.txt` | 05:56:45-05:57:37 | **1** | przeszukanych 2267; TRAFIENIA 96 w 13 miejscach - DOKLADNIE te same 6 plikow testow i 7 commitow co w `<REPO>` (14 nazw sztucznych SE10); w katalogu `dowody\` i w 9 commitach galezi `e3/odbior`: 0 |

Historia `2537f6f..HEAD` obejmuje zmiany wobec `main` (9 commitow galezi). Uwaga: galaz dowodow zmienia sie nadal (w
znaku: "drugi przebieg T13, RAPORT.md ... dojda w kolejnych commitach") - pliki dodane po 3a4afbf (w tym dowody T9) NIE sa
objete tym skanem.

### Krok 4 - ruch sieciowy do ramki (zapis T5 czesc B, adres LAN <adres-IP>)

`--cel ODB_ROB\T5\ruch_ramka_w.bin --cel ODB_ROB\T5\ruch_ramka_p.bin --wynik <ROB>\t9_ruch.txt` (pelne N), 05:53:15,
kod **0**: przeszukanych 2 z 2 plikow, **TRAFIENIA calych nazw 0, dozwolone 0, czlony 0** - "ZAL (0 trafien)".

Co jest w zapisie (odczyt wlasny + `T5\t5_ruch_liczniki.txt`, `T5\posrednik_*.log`):

| Plik | Bajtow | SHA-256 (16 znakow) | Kawalkow `#RUCH` | Polaczen | Bajtow do ramki / z ramki | Zadania |
|---|---|---|---|---|---|---|
| `ruch_ramka_w.bin` (ramka W) | 37678 | a603fe15d1a10b22 | 166 | 57 (56 z danymi) | 14265 / 20794 | 56: `GET /zdarzenia` 35, `PUT /plan` 10, `PUT /tryb` 9, `GET /stan` 1, `DELETE /plan` 1 |
| `ruch_ramka_p.bin` (ramka P) | 10157 | 2ee47a6c87785ad6 | 55 | 20 (19 z danymi) | 2681 / 6625 | 19: `GET /zdarzenia` 17, `GET /stan` 1, `DELETE /plan` 1 |

Postac tresci: czysty HTTP z trescia JSON (`content-type: application/json`), bez kompresji (0 naglowkow
`content-encoding`, 0 wystapien gzip / deflate), 0 bajtow >= 0x80 i 0 bajtow zerowych w obu plikach - caly zapis to ASCII,
wiec postacie obslugiwane przez narzedzie (UTF-8, cp1250, UTF-16 LE, `\uXXXX`) pokrywaja wszystko, co w nim jest
(UTF-16 BE i tresc spakowana w tym zapisie nie wystepuja). Kluczy JSON roznych: 46 (W) i 32 (P) - numery plytek, gniazd,
kuwet, kolory, tryby, identyfikatory planu; zadnego pola z nazwa. Zapis obejmuje 3 skany wieczorne na programie z paczki
(ramka P: tylko odpytywanie - tryb wieczorny planu jej nie wysyla; plan ramki P nie przeszedl przez zapis LAN - O8 w T5).

Test z planu (interpreter instalacji `<K>` przez `Polecenie.cmd`; zrodla importowanego kodu nie sprawdzano - polecenie
planu nie uzywa tu `pytest_instalacja.py`; plik `krok_t9_4_test.cmd`):

| Proba | Polecenie | Godz. | Kod | Wynik |
|---|---|---|---|---|
| 1 (doslownie) | `call <K>\Polecenie.cmd -m pytest <ST>\testy\test_indicate.py <ST>\testy\test_ramka.py -q -rA -p no:cacheprovider --rootdir <ST> -k test_zz_k8 > <ROB>\t9_test_zz_k8_proba1.log 2>&1 < NUL` | 05:53:39-05:53:42 | **1** | `1 failed, 1 passed, 117 deselected in 1.51s`; `test_indicate.py::test_zz_k8_*` PASSED ("POMIAR K8: 43 zapisow ruchu (18901 znakow), trafien nazw 0"); `test_ramka.py::test_zz_k8_*` FAILED na `assert n >= 20` (`assert 16 >= 20`, wiersz 2900) - "POMIAR K8: zapis ruchu 16 komunikatow, 5532 znakow"; asercja nazw (`trafienia == []`, wiersz 2899) PRZESZLA |
| 2 (to samo polecenie, jedna powtorka dla sprawdzenia powtarzalnosci) | jw. -> `t9_test_zz_k8_proba2.log` | 05:54 | **1** | `1 failed, 1 passed`; znow 16 komunikatow (< 20), trafien nazw 0 - wynik powtarzalny, nie losowy |
| 3 (POLECENIE ZMIENIONE: tylko `-k "test_k1 or test_k2 or test_zz_k8"`, plik `krok_t9_4_test_proba3.cmd`) | -> `t9_test_zz_k8_proba3.log` | 05:54:29-05:54:32 | **0** | `11 passed, 108 deselected in 1.91s`; "POMIAR K8: 177 zapisow ruchu (466893 znakow), trafien nazw 0, kluczy poza naglowkiem 0"; "POMIAR K8: zapis ruchu 26 komunikatow, 9406 znakow; trafienia nazw: 0 wymagane" |

Wniosek: polecenie planu w postaci doslownej (`-k test_zz_k8`) NIE przechodzi - test `test_ramka.py::test_zz_k8_*`
uruchomiony sam wytwarza 16 komunikatow, a wymaga co najmniej 20 (prog objetosci zapisu, nie nazw). W planie polecenie
bylo sprawdzone tylko razem z innymi testami (T5 czesc A, polecenie 1). Liczba kryterium T9 (trafienia nazw w ruchu) = 0
we wszystkich 3 probach oraz w przebiegu T5 z dzisiaj (`T5\t5_testy.log`: oba testy PASSED, 3178 zapisow / 1894820
znakow i 1507 komunikatow / 690365 znakow, trafien nazw 0). Niczego nie naprawiano. `git -C <REPO> status --short` po
probach: pusty.

### Krok 3 - pliki wynikow

Cele: wszystkie istniejace katalogi `wyniki`, `podglady`, `pula_cache` i pliki `do_dofrezowania_biezaca.csv` obu
instalacji i katalogow danych testow - 76 celow, lista w `t9_cele_wyniki.txt` (wyniki 18, podglady 17, pula_cache 13,
csv 28). Pominiete, bo nie istnieja: `wyniki` i `podglady` w `<K>\dane` i w `<PC-katalog>\t0\odbior_t12\Stanowisko\dane`
(na instalacjach nie skanowano plytek). Polecenie: `<N> <76 x --cel> --wynik <ROB>\t9_wyniki.txt` (pelne N), 05:55:26,
kod **0**: przeszukanych 120 plikow, nieprzeszukanych 161 (wszystkie `.npz`), **TRAFIENIA calych nazw 0**, dozwolone 0,
czlony 1665 w 73 plikach (1 czlon, sha16 7da6cb013511d41b - patrz "Czlony").

### Krok 5 - "nazwy tylko w `dane/`" i proba dodatnia

Cele: 29 katalogow `dane` (obie instalacje + wszystkie katalogi danych testow w `ODB_ROB`) + `ODB_ROB\T3\t3\baza` - lista
`t9_cele_dane.txt`. Polecenie: `<N> <30 x --cel> --dozwolone stanowisko.sqlite --dozwolone \kopie\stanowisko_
--dozwolone log_excel.csv --dozwolone \kopie\ --wynik <ROB>\t9_dane.txt` (pelne N), 05:54:46, kod **0**:
przeszukanych 263 plikow, nieprzeszukanych 150 (`.npz`), **TRAFIENIA calych nazw poza miejscami dozwolonymi: 0**,
**trafienia w miejscach dozwolonych: 66 w 2 plikach** (`T3\t3\baza\stanowisko.sqlite`: 33 trafienia 14 nazw;
`T3\t3_tmp\se100\dane\stanowisko.sqlite`: 33 trafienia 14 nazw), czlony 1670 w 74 plikach (2 rozne).

**Proba dodatnia dziala:** baza SE10 daje 33 trafienia dozwolone (jak w probie recenzenta: 33), wiec narzedzie znajduje
nazwy tam, gdzie wolno im byc. Katalogi `dane` instalacji i testow wieczornych: 0 trafien dozwolonych - poprawne, bo
`SELECT count(*) FROM zlecenia` = 0 (i `projekty` = 0) w `<K>\dane`, instalacji T12, T2, T5, T7 b2, T11
(`t9_sql_liczby.txt`). Wniosek dla kryterium "nazwy tylko w `dane/` (baza, log Excela)": nazwy puli testowej NIE sa
zapisane nigdzie w katalogach danych (ani w bazie, ani w logach, ani w wynikach) - program trzyma tylko `sha16`; nazwy
sztuczne SE10 sa wylacznie w bazie. Plikow `log_excel.csv` z nazwami: 0 trafien.
### Krok 2 - logi i katalogi robocze wszystkich testow (`ODB_ROB` w calosci + logi obu instalacji)

Wspolne opcje: `--cel <PC-katalog>\t0\odbior\Stanowisko\dane\logi --cel <PC-katalog>\t0\odbior_t12\Stanowisko\dane\logi
--cel <PC-katalog>\koordynator\robocze\odbior --dozwolone stanowisko.sqlite --dozwolone \kopie\stanowisko_ --dozwolone
log_excel.csv --dozwolone t4_surowe --dozwolone t10_surowe --wyklucz \zrodla\ --wyklucz \wersje\ --wyklucz \paczka_M\
--wyklucz \drzewo_M\` (polecenie planu doslownie). Jeden przebieg trwa ok. 10,5 min (4,4 GB, glownie skany STL).

| Proba | Zmiana wobec planu | Godz. | Kod | Wynik narzedzia |
|---|---|---|---|---|
| 1 (doslownie, pelne N) -> `t9_logi_proba1.txt` | brak | 05:47:59-05:58:43 | **1** | przeszukanych 1136, nieprzeszukanych 652, wykluczonych 101649; TRAFIENIA 239 w 105 plikach; dozwolone 66 w 2; czlony 3046 w 289 |
| 2 (pelne N) -> `t9_logi.txt` | dopisane `--dozwolone \robocze\Cyrkon\ --dozwolone \robocze\Cyrkon3\ --dozwolone \T8\robocze\baza_t` (dane wejsciowe - nizej) | 05:59:36-06:10:18 | **1** | przeszukanych 1172, nieprzeszukanych 652, wykluczonych 101649; **TRAFIENIA 2 w 2 plikach**; dozwolone 303 w 105; czlony 3050 w 292 |
| 3 (N bez baz SE10) -> `t9_logi_bez_SE10.txt` | jak proba 2 | 05:59:40-06:09:52 | **0** | przeszukanych 1172, nieprzeszukanych 652, wykluczonych 101649; **TRAFIENIA 0**; dozwolone 204 w 102; czlony 3150 w 281 |

Proba 1 - rozklad 239 trafien w 105 plikach (pelna lista z `--json`, sciezki zamaskowane):

- 102 pliki, 204 trafienia: 6 kopii puli testowej uzytych przez testy jako folder projektow - `T2\robocze\Cyrkon`,
  `T5\robocze\Cyrkon`, `T7\robocze\Cyrkon`, `T7\uzup\robocze\Cyrkon`, `T7\uzup\robocze\Cyrkon3`, `T11\robocze\Cyrkon` (po
  17 plikow STL; w kazdym pliku 2 trafienia = nazwa folderu i nazwa pliku W SCIEZCE, 32 rozne sha16 = komplet puli).
  To sa DANE WEJSCIOWE testow (kopie `<PC-katalog>\app\Prace_test`, zrodlo nazw) -> `--dozwolone`. Wzory nie pasuja do
  zadnego pliku z list dowodow (katalogi `robocze\` nie ida do repo).
- 1 plik, 33 trafienia (14 nazw sztucznych SE10): `T8\robocze\baza_t3.sqlite` - kopia bazy SE10 zrobiona przez T8 (baza =
  miejsce dozwolone kryterium; wzor `stanowisko.sqlite` jej nie obejmuje, bo T8 nadal kopii inna nazwe) -> `--dozwolone`.
- 2 pliki, 2 trafienia, sha16 5460764f2024f994 (nazwa SZTUCZNA SE10): `T1\robocze\t1_collect_bazowy_pelny.txt` i
  `t1_collect_wersja_pelny.txt` - wydruk `pytest --collect-only`; trafienie w wierszu 926 w identyfikatorze testu
  `testy/test_nazwy.py::test_kuweta_z_nazwy_folderu[...]` (parametr testu z repo). To NIE jest dana wejsciowa, wiec
  `--dozwolone` NIE dopisano - zostaja jako 2 trafienia proby 2 (kod 1). Pliki sa w `T1\robocze` i nie sa dowodami.

Proba 3 (N bez nazw sztucznych SE10): 0 trafien, kod 0 - zadna nazwa puli testowej ani drzewa A5i nie wystepuje w logach,
wynikach, plikach roboczych i dowodach 14 katalogow testow poza 6 kopiami puli (204 trafienia dozwolone w sciezkach = takze
dowod, ze narzedzie znajduje nazwy prawdziwej puli tam, gdzie sa). Surowe wyniki T4 / T10 (`t4_surowe`, `t10_surowe`):
0 trafien. Logi obu instalacji: 0 trafien.

### Krok dodatkowy (poza planem) - instalacje w calosci

`<N> --cel <PC-katalog>\t0\odbior --cel <PC-katalog>\t0\odbior_t12 --dozwolone stanowisko.sqlite --dozwolone
\kopie\stanowisko_ --dozwolone log_excel.csv --dozwolone \dane\Cyrkon\ --wyklucz \venv\ --wynik <ROB>\t9_instalacje.txt`
(pelne N), 06:10:36-06:11:05, kod **0**: przeszukanych 739 plikow (program wersji, paczki rozpakowane, `dane`, logi
instalatora, `ustawienia.toml`), nieprzeszukanych 152 (`.whl`), wykluczonych 75704 (`\venv\` - pakiety obce z kol
paczki); **TRAFIENIA calych nazw 0**; dozwolone 68 w 34 plikach (2 foldery wejsciowe `dane\Cyrkon` po 17 plikow -
zrodlo nazw); czlony 3213 w 276 plikach (16 roznych - te same slowa co w repo, bo to kod programu z paczki).

### Kontrole dodatkowe wykonawcy (poza planem, pomocniki w `<ROB>\robocze\`, importuja funkcje narzedzia bez zmian)

1. Wnetrze plikow `.npz` (`t9_npz_dodatkowo.txt`, 06:11-06:20, kod 0): 586 plikow `.npz` z `ODB_ROB` i obu instalacji
   (te same wykluczenia co w kroku 2 + `\venv\`), 9063 elementy rozpakowane w pamieci, 2 507 512 811 bajtow; wzorzec
   narzedzia na bajtach surowych i po usunieciu bajtow zerowych (napisy numpy = UTF-32 LE): **calych nazw 0**; czlony 995
   (12 sha16; 792 to jedno slowo pospolite sha16 5054e1b14a2e813f, reszta po 2-54 trafienia w danych binarnych - NIE
   rozstrzygane pojedynczo, w tym 3 sha16 niewystepujace w innych krokach: 195d0f538f63d8bd x2, 45f91df25dac1d48 x2,
   813684c987347d60 x4). Ograniczenie tej kontroli: postac UTF-32 po usunieciu zer nie jest znajdowana dla 3 z 449 nazw.
2. Czlony w plikach binarnych (`t9_czlony_binarne.txt`): 72 pliki `.stl` / `.ttf` z czlonami, 3 394 807 408 bajtow -
   patrz "Czlony".
3. Typy plikow nieprzeszukanych (`t9_nieprzeszukane_typy.txt`).

## Czlony "do wyjasnienia" (nie sa kryterium; `t9_zrodla_wszystkie.txt`, `t9_czlony_binarne.txt`)

Lacznie we wszystkich przebiegach: 22 rozne sha16 (21 slow - 414777f6c840fa40 i 180af17142fb4a0a to to samo slowo pisane
wielka i mala litera). Slowa obejrzane przez wykonawce tylko na konsoli (kazde z nich juz wystepuje w repo albo w wynikach
programu); tu tylko sha16, liczby i rozstrzygniecie. Najwieksze liczby: repo 9158 w 883 plikach (pelne N) / 9020 w 876
(bez SE10); worktree 9653 w 978 / 9499 w 967; `ODB_ROB` 3050 w 292 / 3150 w 281; instalacje 3213 w 276; `dane` 1670 w 74;
wyniki 1665 w 73; dowody 232 w 88; ruch do ramki 0.

| Grupa | sha16 | Skad czlon (liczba nazw) | Gdzie trafia | Rozstrzygniecie |
|---|---|---|---|---|
| A. slowa "dana sztuczna" i imiona z nazw SE10 | 414777f6c840fa40, 6d223affc23ef544, bb5fe2500e4c0440, fffd71d486fd229a (4 slowa znaczace atrape / test / fikcje / przyklad); 923818e5629f40f9, d980ff4703675303 (2 pospolite imiona) | tylko nazwy sztuczne SE10 (po 1 nazwie) | repo (kod, testy, opisy; do 3606 trafien w 334 plikach - worktree), dowody (99 w 31 i 5 w 4), logi testow; imie 923818...: w repo 3 pliki (2 generatory danych syntetycznych - listy imion - i 1 test) + 2 commity, w `T6\robocze\logi_excel\` 3 pliki CSV testow (15); imie d980ff...: tylko 22 skany STL (30, binarne) | slowa pospolite / dane sztuczne; nie nazwiska |
| B. slowa z nazw drzewa sztucznego A5i | 180af17142fb4a0a (322 nazwy), 5054e1b14a2e813f (34), b78cb9ce56d5b7e2 (47), bef9ad6bbec0ddef (80), f563e2c6c0dcbf98 (81), c9647b1cbff0d9de (74) | tylko A5i (dane fikcyjne) | repo (do 3662 w 342 plikach), dowody (99 w 47; 29 w 14), logi | slowa pospolite (m.in. 3 nazwy rodzajow zebow, "zlecenie", "wariant"); nie nazwiska |
| C. slowa branzowe z nazw plikow puli testowej | 0dcfafab5f8035e7 (5 nazw puli), 7da6cb013511d41b (6), 9722d4a4b59ce537 (5), 1216b2a88975f9d3 (5), 17f29b073143d8cd (1), f253e9a27ab18977 (5) | pula testowa (i jej kopie w A5i) - angielskie slowa dopisywane do nazw plikow przez program CAD (rodzaj pracy protetycznej itp.) | repo (do 321 w 64 plikach); 7da6cb...: wartosc pola `"typ"` w plikach `*_wynik.json` programu (1665-1677 trafien w 73-75 plikach, zawsze w postaci `"typ": "<slowo>"`); 1216b2...: 5 czcionek `.ttf` w `T7\uzup\robocze\czcionki` (36 trafien, 6 to napis ASCII - tekst angielski w czcionce); 0dcfaf...: takze 12 trafien w 2 skanach STL (0 napisow ASCII - przypadek) | slowa branzowe / pospolite angielskie; nie nazwiska |
| D. imiona z nazw puli testowej | d3fc3547346f0ef9, 702370082a6ab1a0, ec16cd73f88aeaa6 (po 1 nazwie puli) | pula testowa | WYLACZNIE skany binarne STL w `eksport\` testow: 246 w 44, 173 w 27, 82 w 14 plikach; w plikach tekstowych (logi, wyniki, dowody, repo, instalacje): 0 | zbieznosci przypadkowe w liczbach binarnych: 0 z 501 trafien jest napisem z liter ASCII (narzedzie dopasowuje tez bajty >= 0x80 jako litery ze znakami diakrytycznymi cp1250); to nie tekst |
| E. czlon wygladajacy na nazwisko z nazwy puli testowej | 3dea4293d4bdc355 (1 nazwa puli) | pula testowa | WYLACZNIE 6 skanow binarnych STL (12 trafien): 3 kopie jednego skanu (sha256 c85504f17628ac3f, `T7\robocze\b1b`, `b2`, `b3`) po 3 trafienia + 3 skany po 1; w plikach tekstowych, dowodach, repo, instalacjach: 0 | zbieznosc przypadkowa: 9 trafien to te same 5 bajtow wspolrzednej jednego wierzcholka powtorzonej w 3 rekordach trojkatow (rekordy 1051821, 1051879, 1051880; litery o mieszanej wielkosci, sasiednie bajty binarne, poza naglowkiem STL), 3 pozostale to bajty >= 0x80; NIE jest to nazwisko zapisane tekstem -> nie FAIL |

Zadna grupa nie zawiera nazwiska zapisanego tekstem poza `dane/`. Skany `eksport\skan_*.stl` to binarne STL z pustym
naglowkiem (sprawdzone na 5 plikach: rozmiar = 84 + 50 x liczba trojkatow).

## Pliki nieprzeszukane i ograniczenia

| Przebieg | Nieprzeszukane (sama sciezka sprawdzona) | Typy |
|---|---|---|
| repo `<REPO>` i worktree `e3/odbior` | 798 | `.png` 708, `.pdf` 41, `.jpg` 39, `.zip` 10 |
| historia git (oba) | 136 zmian plikow binarnych z nieprzeszukana trescia | - |
| `ODB_ROB` (krok 2) | 652 | `.npz` 586, `.png` 65, `.zip` 1 |
| pliki wynikow (krok 3) / `dane` (krok 5) | 161 / 150 | `.npz` |
| instalacje | 152 | `.whl` |
| dowody, ruch do ramki | 0 | - |

Wykluczone (nieczytane): krok 2 - 101649 plikow (`\wersje\`, `\paczka_M\`, `\drzewo_M\`, `\zrodla\` wg planu: instalacje i
paczki probne T12 czesc B, kopie zrodel); instalacje - 75704 plikow `\venv\`.

Ograniczenia narzedzia (z `--help` i planu): nie szuka UTF-16 BE, cp852, iso-8859-2, postaci NFD, `%XX` (poza `%20`),
`\xNN`, `\\uXXXX` podwojnego, dwoch spacji zamiast jednego separatora; nie czyta wnetrza plikow spakowanych (zip, npz, whl,
pdf, png, jpg, xlsx...) ani tresci zmian binarnych w historii git; pliki > 300 MB (tu: 0). Dla 7 nazw bez postaci ASCII
samotest nie sprawdza transliteracji. Czlony 1-2 znakowe i same numery nie sa szukane, 3-4 znakowe nie sa liczone.
Wnetrze `.npz` sprawdzono dodatkowo (wyzej); wnetrza `.png`, `.pdf`, `.jpg`, `.zip`, `.whl` NIE.
Prawdziwe nazwy zlecen na tym PC = tylko pula testowa (32 nazwy); T9 nie mowi nic o danych laboratorium, ktorych tu nie ma.

## Werdykt czesci kryterium

| Czesc kryterium | Przeszukano | Trafienia calych nazw: pula testowa + drzewo A5i (435 nazw) | Trafienia z pelnym N (449 nazw, + 14 sztucznych SE10) | Ocena |
|---|---|---|---|---|
| repo (pliki sledzone `<REPO>`) | 1265 plikow + 798 tylko sciezka | 0 (kod 0) | 48 w 6 plikach testow (kod 1) | 0 nazw zlecen; nazwy sztuczne SE10 w swoim zrodle (testy programu) |
| historia `2537f6f..HEAD` | 597 commitow | 0 | 48 w 7 commitach (te same pliki testow) | jw. |
| worktree `e3/odbior` (3a4afbf) | 1661 plikow + 606 commitow | 0 (kod 0) | 96 - te same 13 miejsc (kod 1) | jw.; 9 commitow galezi: 0 |
| logi i pliki robocze testow (`ODB_ROB`, logi instalacji) | 1172 pliki | 0 (kod 0) | 2 w 2 plikach `T1\robocze` (kod 1; 1 nazwa sztuczna w identyfikatorze testu) | 0 nazw zlecen |
| pliki wynikow | 120 plikow (+ 161 `.npz`) | 0 | 0 (kod 0) | spelnione |
| instalacje | 739 plikow | 0 | 0 (kod 0) | spelnione |
| ruch sieciowy do ramki | 2 zapisy, 47835 bajtow, 75 zadan | 0 | 0 (kod 0); czlony 0 | spelnione; test `test_zz_k8`: 0 nazw, ale polecenie planu doslownie konczy sie kodem 1 (prog objetosci) |
| katalog dowodow (3a4afbf) | 394 pliki | 0 | 0 (kod 0, bez `--dozwolone`) | spelnione |
| nazwy tylko w `dane/` + proba dodatnia | 263 pliki w 30 katalogach | 0 poza dozwolonymi | 0 poza dozwolonymi; 66 dozwolonych w 2 bazach SE10 | spelnione; proba dodatnia dziala |

Suma trafien calych nazw ZLECEN (pula testowa, drzewo A5i) poza miejscami dozwolonymi = **0**. Z pelnym N narzedzie
konczy kroki 1 i 2 kodem 1 wylacznie przez 14 nazw sztucznych SE10 (98 trafien: 96 w repo - pliki testow i ich historia,
2 w `T1\robocze`), ktorych zrodlem jest samo repo.

## Odstepstwa

W `RAPORT.md` sekcja 4a nie ma odstepstwa dla T9 - oba ponizsze sa **NOWE**:

1. **NOWE (T9-a):** kryterium "0 trafien" ocenione dla nazw zlecen (pula testowa + drzewo A5i, `t9_N_bez_SE10.txt`), a nie
   doslownie wg planu ("kod 0 w kazdym kroku" z N zawierajacym baze SE10). Doslownie: krok 1 kod 1 (96 trafien), krok 2
   kod 1 (2 trafienia) - wszystkie to nazwy sztuczne SE10 w plikach testow repo, ich historii i wydruku listy testow.
   Plan jest tu wewnetrznie sprzeczny: dodaje nazwy SE10 do N (proba dodatnia), a ich zrodlem jest przeszukiwane repo.
2. **NOWE (T9-b):** test z kroku 4 w postaci doslownej (`-k test_zz_k8`) konczy sie `1 failed, 1 passed` (2 proby z 2):
   `test_ramka.py::test_zz_k8_*` uruchomiony sam ma 16 komunikatow przy progu 20; trafien nazw 0. Z szerszym wyborem
   testow (`-k "test_k1 or test_k2 or test_zz_k8"`): 11 passed, trafien nazw 0.

## Polecenia planu, ktore trzeba bylo zmienic

1. Forma wywolania: PowerShell z lista argumentow zamiast wiersza `cmd.exe` (limit 8191 znakow) - `krok_t9.ps1`.
2. Krok 1: dodatkowy przebieg z N bez 3 baz SE10 (pelne N daje kod 1 - opis wyzej).
3. Krok 2: dopisane 3 x `--dozwolone` dla danych wejsciowych (kopie puli, kopia bazy T8) wg reguly planu; dodatkowy
   przebieg z N bez baz SE10.
4. Krok 3 i 5: `<DANE>` = wszystkie katalogi danych testow i obu instalacji (listy `t9_cele_*.txt`); nieistniejace
   `wyniki` / `podglady` instalacji pominiete.
5. Krok 4, test: polecenie doslowne pada (2 proby); proba 3 ze zmienionym `-k`.
6. Dodane poza planem: skan instalacji, kontrola wnetrza `.npz`, kontrola czlonow w plikach binarnych.

## Do decyzji koordynatora / wlasciciela

1. Czy 14 nazw sztucznych SE10 w plikach testow repo (6 plikow, 7 commitow) i w 2 plikach `T1\robocze` przyjac jako dane
   sztuczne (wtedy T9 = ZAL z odstepstwem), czy trzymac sie doslownie "kod 0 w kazdym kroku" (wtedy T9 = FAIL: 98 trafien
   nazw sztucznych). Wykonawca przyjal pierwsze, bo zadna z tych nazw nie jest nazwa zlecenia, a repo jest ich zrodlem.
2. Poprawka planu / testu po odbiorze: N kroku 1 bez bazy SE10 albo `--dozwolone` dla plikow testow; test
   `test_ramka.py::test_zz_k8_*` uruchomiony osobno (16 < 20).
3. Dowody T9 i wszystko, co doszlo do galezi `e3/odbior` po 3a4afbf, nie byly objete skanem katalogu `dowody\` - skan
   trzeba powtorzyc po dodaniu (T9 krok 1: "po scaleniu galezi dowodow powtorz krok 1").
4. Wnetrza `.png` / `.pdf` / `.jpg` / `.zip` w repo (798 plikow) i 136 zmian binarnych w historii nie sa przeszukiwane
   zadnym narzedziem odbioru.
5. Kontrola `.npz`: 3 sha16 czlonow (8 trafien lacznie) i czlon grupy E (8 trafien) we wnetrzu `.npz` nie zostaly
   sprawdzone co do postaci (dane binarne siatek; calych nazw 0).

## Procesy, obciazenie, stan po tescie

Kroki lekkie, bez blokady `ciezki.ps1`; najwyzej 2 procesy python tej sesji naraz (2 razy przez ok. 3 s trzeci - krotki
pomocnik analizy; opisane tu wprost). Rownolegle na PC biegl pomiar innego wykonawcy (procesy python z 05:47 i 06:01 -
nie ruszane). `<REPO>`: `git status --short` pusty; worktree `e3/odbior` tylko czytany (`git ls-files`, `git log`).
### Powtorka skanow galezi dowodow na nowszym HEAD (galaz poszla do przodu w trakcie T9)

06:22:48: `git -C <PC-katalog>\qc-wt\odbior log --oneline -1` = `9d9850a` (11 commitow wobec 571e186, `status --short`
pusty, 394 pliki w `dowody\`; ten sam HEAD po skanach, 06:23:47).

| Cel | Plik wyniku | Godz. | Kod | Wynik |
|---|---|---|---|---|
| `dowody\` BEZ `--dozwolone`, pelne N | `t9_dowody_2.txt` | 06:22:48-06:22:50 | **0** | 394 z 394 plikow; **TRAFIENIA calych nazw 0**; czlony 232 w 88 |
| worktree jako repo, N bez baz SE10 | `t9_repo_odbior_bez_SE10_2.txt` | 06:22:51-06:23:43 | **0** | 2269 (1661 plikow + 608 commitow), nieprzeszukanych 798; **TRAFIENIA 0**; czlony 9537 w 968 |
| worktree jako repo, pelne N | `t9_repo_odbior_2.txt` | 06:22:51-06:23:47 | **1** | 96 trafien w tych samych 13 miejscach (6 plikow testow + 7 commitow, nazwy sztuczne SE10); w 11 commitach galezi i w `dowody\`: 0 |

### Skan wlasnych dowodow T9 przed przekazaniem

`<N> --cel <ROB> --wyklucz \T9\robocze\ --wynik <ROB>\t9_dowody_wlasne.txt` (pelne N, BEZ `--dozwolone`; wykonany po
zapisaniu `t9_wynik.md`, 06:24:31): kod 0, 40 plikow, TRAFIENIA calych nazw 0, czlony 31 w 6 plikach (slowa pospolite z
przepisanych sciezek i opisow).

## Dowody (w `<ROB>`)

Z listy planu: `t9_repo.txt`, `t9_repo.json`, `t9_dowody.txt` (+ `t9_dowody_2.txt`), `t9_logi.txt`, `t9_wyniki.txt`,
`t9_ruch.txt`, `t9_dane.txt`, `t9_wynik.md` (kopia `WYNIK.md` pod nazwa z planu). Dodatkowe: `t9_logi_proba1.txt`,
`t9_logi_bez_SE10.txt`, `t9_repo_bez_SE10.txt` / `.json`, `t9_repo_odbior*.txt` (4), `t9_instalacje.txt`,
`t9_npz_dodatkowo.txt`, `t9_czlony_binarne.txt`, `t9_zrodla_repo.txt`, `t9_zrodla_wszystkie.txt`,
`t9_nieprzeszukane_typy.txt`, `t9_sql_liczby.txt`, `t9_N.txt`, `t9_N_bez_SE10.txt`, `t9_cele_wyniki.txt`,
`t9_cele_dane.txt`, `t9_polecenia.txt` (pelne polecenia), `kody.txt`, `krok_t9.ps1`, `krok_t9_4_test.cmd`,
`krok_t9_4_test_proba3.cmd`, `t9_test_zz_k8_proba1..3.log` (+ `_czas.txt`), `t9_dowody_wlasne.txt`, `WYNIK.md`.
NIE do repo (zostaja w `<ROB>\robocze\`): pliki `.json` przebiegow (do 17 MB - listy plikow wykluczonych) i pomocniki
`t9_analiza.py`, `t9_typy.py`, `t9_npz.py`, `t9_binarne.py`. CRLF ma 9 plikow (2 x `.cmd`, 3 logi i 3 pliki
czasu testu, `kody.txt`) - przed `git add`: `dowody_lf.py --napraw`; `krok_t9.ps1` ma LF.

Koniec pracy wlasnej: 06:25 (start 05:44; na znak nie czekano - byl zapisany o 05:47:31).