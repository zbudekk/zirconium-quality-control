# R59-P - program stanowiska na nowym ukladzie gniazd (raport)

Data: 2026-11-14. Subsesja R59-P (wykonawca programu). Stan wyjsciowy: commit `bc76f9f` (R59-A: nowe `parametry.json`,
modele programu jeszcze stare). Plan: `../../plan_sesji_R59_uklad_gniazd_2026-11-14.md` sekcja 9. Commity robi koordynator.
Decyzje wlasciciela (G0): W-b, P-e, jedna rynienka, stare plytki nadal skanowane (`*_r54` + straznik), numery bez zmian.

## Stan

| Krok | Co | Stan |
|---|---|---|
| 0 | kopia testowa na PC, pytest na HEAD | zrobione: 165 passed / 3 skipped / 1 failed |
| 1 | foldery `*_r54` + nazwy ukladow | zrobione: 14 plikow bajtowo = HEAD |
| 2 | testy starego ukladu przepiete na `*_r54` | zrobione: zielone przed i po podmianie modeli |
| 3 | testy nowego ukladu (najpierw czerwone) | zrobione: `test_uklad_r59.py` 17 failed / 16 passed przed podmiana modeli |
| 4 | modele nowego ukladu | zrobione: 14 plikow, SHA = `R59_wdrozenie_zmiany.md` pkt 0 |
| 5 | straznik ukladu | zrobione: 0 / 520 falszywych, 240 / 240 wykrytych (obie warstwy) |
| 6 | dane i metryki | zrobione: tabela w pkt 6; jedno kryterium na granicy (pkt 6.2) |
| 7 | pojemnosc | zrobione: tabela w pkt 7 |
| 8 | opisy modulow, README | zrobione |
| 9 | pytest koncowy, SHA PC = worktree | zrobione: 250 passed / 3 skipped / 0 failed; 78 z 78 plikow programu na PC = worktree (SHA-256) |
| 10 | poprawki po recenzji PR, runda 1 (15.11.2026; pkt 11) | zrobione: 252 passed / 3 skipped / 0 failed; 78 z 78 plikow programu na PC = worktree |

Nic nie jest w toku. Gdyby recenzja R59-B zmienila STL albo JSON: powtorzyc pkt 3 (kopie modeli, tabela `SHA_MODELI` w
`testy/test_uklad_r59.py`), `pytest`, `narzedzia/straznik_R59.py`, `pomiary\generuj_R59.py` i `narzedzia/metryki_P3a.py`
(polecenia w pkt 10).

## 1. Co zmieniono

1. **Dwa uklady w programie.** Nazwa ukladu = klucz z `[plytki]`: `wieczorna`, `poranna`, `okragla_wieczorna`,
   `okragla_poranna` (R59) oraz te same nazwy z `_r54` (uklad sprzed R59, stare plytki fizyczne). `UkladPlytki.nazwa`
   jest teraz nazwa ukladu (dotad pole `plate` z pliku, takie samo w obu ukladach) - trafia do prawdy generatora, do
   wyniku `plate` i do komunikatow. `uklad.typ_plytki()` zdejmuje przyrostek `_r<NN>`; `synth.poranna()` dziala takze
   dla `poranna_r54` i `okragla_poranna_r54` (bez tego stara plytka poranna dostalaby skurcz wieczorny).
2. **Straznik ukladu** w `plate.py` (pkt 5): wyjatek `NiezgodnyUklad` z komunikatem "plytka nie pasuje do wybranego
   ukladu", `porownaj` zwraca wynik bez gniazd (`uklad_zgodny` = false), okno pokazuje komunikat.
3. **Narzedzia:** `metryki_P3a.py` i `metryki_P2.py` - `--sufiks-ukladu _r54` dla zestawow sprzed R59, skan niezgodny
   trafia na liste `uklad_niezgodny`; `metryki_P3a.py` - `--procesy N` i metryki per srednica gniazda;
   `rzut_z_gory.py --plytka`; `katalog_projektow.py --plytki` (domyslnie 4 uklady kwadratowe); nowe
   `straznik_R59.py` (liczniki straznika) i `pojemnosc_R59.py` (pojemnosc plytek).
4. **Ustawienia:** `ustawienia.przyklad.toml [plytki]` ma 8 ukladow. W `SCHEMAT` (`ustawienia.py`) zmienil sie tylko
   komentarz: nazwy w `[plytki]` byly i sa dowolne, wymagane sa `wieczorna` i `poranna` (patrz odstepstwo 1).
5. Nie zmieniono: `match.py`, `inspect.py`, progow `[match]` / `[inspect]`, `katalog.py`, `requirements.txt`.
6. Przeglad `synth.kandydaci_gniazd` / `katalog.gniazdo_dla` pod katem zalozen o trzech srednicach: brak - dobor idzie
   po gniazdach okraglych z `uklad.json` od najmniejszego (>= 0,55 szerokosci pracy), potem rynienki; kluczy
   `*_socket_d_s/m/l` program nie czyta. Zmiany kodu nie byly potrzebne.

## 2. Testy przed -> po (PC, `run.cmd -m pytest testy -q -p no:cacheprovider`)

| Stan | passed | skipped | failed | Log (`<PC-katalog>\r59\program\logi\`) |
|---|---|---|---|---|
| punkt odniesienia koordynatora (`origin/main`, stary uklad) | 166 | 3 | 0 | `R59_odbior/baseline.md` |
| HEAD `bc76f9f` (nowe `parametry.json`, stare modele) | 165 | 3 | 1 | `pytest_00_HEAD.log` |
| po krokach 1-2 (`*_r54`, testy przepiete; modele pod nowymi nazwami jeszcze stare) | 184 | 3 | 2 | `pytest_01_r54.log` |
| po kroku 4 (modele R59) | 218 | 3 | 1 | `pytest_03_modele_r59.log` |
| po kroku 5 (straznik) | 250 | 3 | 0 | `pytest_05_straznik_calosc.log` |
| stan koncowy (253 testy zebrane) | 250 | 3 | 0 | `pytest_06_koncowy.log` |
| po poprawkach recenzji PR, runda 1 (255 zebranych; pkt 11) | 252 | 3 | 0 | `pytest_07_po_recenzji_PR.log` |

- 1 failed na HEAD i 2 failed po krokach 1-2 dotycza nowego ukladu (zgodnosc `uklad.json` z `parametry.json`; 4 dolki
  kodu na nowym kwadracie) - oczekiwane, modele byly jeszcze stare. Wszystkie testy na `*_r54` byly w tym stanie zielone.
- 1 failed po kroku 4: `test_match.py::test_zgrubne_obroty_i_ocena` na nowym ukladzie - patrz odstepstwo 2.
- Pominiete 3 = te same co w punkcie odniesienia (`test_katalog.py` - brak folderu z pulpitu; `test_ui.py` x 2 - okno
  jest szkicem). Zadnego nowego `skip`.
- Nowe pliki testow: `testy/test_uklad_r59.py` (33 testy, liczby z `../parametry.json`), `testy/test_straznik.py` (28;
  po poprawkach recenzji PR 30).
  Testy z liczbami ukladu R54 dzialaja na `*_r54` bez zmiany oczekiwan; testy ogolne (siatki "wszystkie gniazda",
  lancuch plate, match) dzialaja na obu ukladach.

## 3. Modele

- `modele_plytek/{wieczorna,poranna,okragla_wieczorna,okragla_poranna}`: `uklad.json` = `wyniki_v2/json/uklad_gniazd_<typ>.json`,
  `plytka_n<N>.stl` = `wyniki_v2/stl/ramka_plytka_<typ>_n<N>_v2.stl`, okragle `plytka_bazowa.stl` = `..._v2.stl`.
  SHA-256 (16 znakow): n1 3b0db5452a0cd953, n2 b87026134b25cf32, n3 59e615d596771c6c, n4 20f15f2214f6c9a9,
  n5 a275775b9c9b5ddd, n6 c44be370c8b9ad2b, n8 d5591f652ea1b6b2, n9 f9444e6f14e37d9d, bazowe okragle aad8033e6c1d1f34 /
  e35835d7618e6665; JSON 7ae07ba861950724 / 46e474b759c4b78b / c07791f4bb976be2 / b943e6c5dd54a8b3 - 14 z 14 zgodnych z
  `R59_wdrozenie_zmiany.md` pkt 0.
- `modele_plytek/*_r54`: 14 plikow, kazdy bajtowo rowny plikowi `modele_plytek/<typ>/...` z HEAD `bc76f9f`
  (porownanie `git show HEAD:...` z kopia: 14 z 14).
- Pelne SHA wszystkich 28 plikow sa w `testy/test_uklad_r59.py` (`SHA_MODELI`, `SHA_MODELI_R54`) i sprawdza je test
  `test_pliki_modeli_bajtowo_bez_zmian` (takze: zadnych innych plikow w tych folderach).
- Uwaga: plik ukladu R59 plytki kwadratowej ma 4 dolki kodu (bit D na (-45; -27), generator pisze go od R57) i pole
  `shape`; program czyta oba warianty. W polu fi 100 dolki kwadratu sa nadal niewidoczne (numer trzeba podac).

## 4. Stary uklad dziala jak w punkcie odniesienia

| Sprawdzenie | Wynik |
|---|---|
| Zestawy z 2.11 (`baseline\...\dane\syntetyczne_P2` + `_P3a`, 40 skanow) nowym programem z `--sufiks-ukladu _r54` | wyrownanie 40 / 40 (max 0,0137 mm), top-1 411 / 420, P2 271 / 271, dowolna metoda 259 / 282 (dobrze 258 / 279), numer z dolkow 24 / 24, falszywe czerwone 0, prace cale z alarmem 1 / 129 - wszystkie liczby jak w punkcie odniesienia; statusy gniazd zolte 157 / szare 42 (punkt odniesienia 158 / 41, raport z 2.11: 157 / 42) |
| Skany seed 7001 na `*_r54` (polecenia z `baseline.md` pkt 5) | mapa gniazdo -> projekt -> status = `t8_mapa_seed7001.json`: 4 z 4 plytek; macierz wyrownania identyczna (roznica 0,0) |
| Bajty STL skanu seed 7001 vs `baseline\t8` | kwadraty 2 z 2 rowne; okragle: 3 z 4 przebiegow rowne, w 1 przebiegu 54 z 984 102 normalnych rozni ostatni bit float32 (wierzcholki identyczne) |
| Zestaw P3a z 2.11 odtworzony nowym programem na `*_r54` (te same polecenia i seedy) | 16 z 16 skanow: prawda identyczna, STL bajtowo rowny |
| Polecenie P2 kodem z punktu odniesienia (`baseline\Ramki\stanowisko`) vs nowym programem na `*_r54` | 3 z 3 sprawdzonych skanow bajtowo rowne (wieczorna s100, okragla_poranna s200, poranna s203) |

Uwagi do tych sprawdzen (wazne dla testu T8 koordynatora):
- **`--numer` zmienia losowanie na kwadratach.** `synth` losuje numer plytki z `uk.numery` tylko wtedy, gdy nie podano
  `--numer`; przy trzech numerach (kwadraty) to jedno losowanie wiecej, wiec `--numer 3` daje INNY skan niz ten sam seed
  bez `--numer` (zmierzone: inna prawda, inna mapa, 10 prac zamiast 9). Punkt odniesienia powstal bez `--numer`
  (wylosowal n3 i n6). Zeby dostac te sama mape: `synth --plytka wieczorna_r54` / `poranna_r54` BEZ `--numer`, a
  `--numer 3` / `--numer 6` tylko w `porownaj`. Na okraglych (jeden numer) `--numer` niczego nie zmienia. To cecha
  generatora sprzed R59, nie tej paczki.
- **Nazwa ukladu nie wplywa na losowanie ani na wynik.** Zmienia sie tylko nazwa pliku skanu
  (`skan_wieczorna_r54_n3_s7001` zamiast `skan_wieczorna_n3_s7001`) i pole `plytka` w prawdzie (`wieczorna_r54`).
- Roznica ostatniego bitu normalnych w jednym przebiegu okraglej wieczornej to szum numeryczny (os glowna mostu z
  `numpy.linalg.eigh` w `synth.os_glowna_deg`; w prawdzie roznica na 16. cyfrze) - wystepuje miedzy dwoma
  uruchomieniami tego samego polecenia, niezaleznie od nazwy ukladu.
- Zestawu P2 z 2.11 nie da sie odtworzyc dzisiejszym generatorem (0 z 24; inne liczby prac na plytce) - takze kodem z
  punktu odniesienia. Powstal wczesniejsza wersja `synth` (przed scenariuszami P3a). Dlatego w pkt 6 sa trzy kolumny.
- Roznica 1 gniazda (zolte / szare) miedzy dwoma przebiegami tych samych skanow tym samym kodem to rozrzut miedzy
  uruchomieniami (praca "bokiem" na granicy progu match), nie skutek zmian.

## 5. Straznik ukladu

### 5.1 Pomiar stanu przed zmiana (`pomiary\stan_obecny.py`, 32 przypadki)

4 typy x 2 kierunki x (plytka pusta, plytka z 8-12 pracami), skan `--poza-uklad --pole 100`, seed 7101:
- plytka NIEZGODNA z wybranym ukladem: 16 z 16 konczylo sie wyjatkiem `BladWyrownania: stozki nie pasuja do
  znacznikow plytki <nazwa>: reszta 3.151 mm > 0.3` (pary wieczorne) albo `reszta 8.933 mm` (pary poranne) - bez
  wyniku, bez pliku JSON, w oknie "Blad porownania" ze sladem stosu. Czyli zielonych gniazd nie bylo, ale komunikat
  nie mowil, ze wybrano zly uklad;
- plytka ZGODNA: 16 z 16 normalny wynik (stozki 3, reszta 0,0001-0,0004 mm).
Powod: stozki znacznikow obu ukladow leza w innych miejscach (wieczorna: boki trojkata 53,0 / 71,0 / 88,6 mm w R54 i
58,2 / 75,0 / 87,7 mm w R59; poranna 60,0 / 60,7 / 88,4 i 55,9 / 79,4 / 86,5).

### 5.2 Rozwiazanie (dwie warstwy, `plate.py`)

1. **Rozstaw stozkow.** Trzy dobrze dopasowane stozki o innym rozstawie niz znaczniki ukladu -> `NiezgodnyUklad`
   (podklasa `BladWyrownania`), powod `stozki`, komunikat: "plytka nie pasuje do wybranego ukladu <nazwa>: stozki
   znacznikow nie pasuja do ukladu (rozstaw w skanie ..., w ukladzie ...; reszta ...)". `porownaj` sprawdza tymi
   stozkami pozostale uklady z `[plytki]` i dopisuje, do ktorych skan pasuje (np. `wieczorna_r54, okragla_wieczorna_r54`).
2. **Gniazda** (`plate.zgodnosc_ukladu`, po wyrownaniu i ICP). Mapa wysokosci skanu (najwyzszy punkt w pikselu
   0,5 mm) kontra model STL, tylko w strefach pewnych modelu wyznaczonych promieniami z gory: "dno gniazda" (odsuniete
   1,0 mm od scianki i od otworu fi 3) i "pelny wierzch" (odsuniety 1,5 mm od gniazd, stozkow, dolkow, reliefu, brzegu).
   K1 = pole dna gniazd modelu, nad ktorym skan ma plaski wierzch plytki (gniazdo modelu nad pelnym materialem);
   K2 = pole pelnego wierzchu modelu, w ktorym skan jest glebszy niz 1,5 mm (pelny material modelu nad dziura).
   K1 >= 150 mm2 albo K2 >= 50 mm2 -> `NiezgodnyUklad`, powod `gniazda`. K1 dziala takze na plytce pelnej prac
   (prace leza w gniazdach plytki zeskanowanej, nie zaslaniaja jej wierzchu); K2 na pelnej plytce maleje.
   W parze R59 / R54 pierwsza warstwa zatrzymuje skan wczesniej, wiec druga jest zabezpieczeniem na przypadek dwoch
   ukladow o tych samych stozkach (i bledu w plikach modeli); mierzona osobno (ponizej, kolumna "sam straznik gniazd").
3. Przy niezgodnosci: `wyrownaj` nie zwraca wyniku (wyjatek niesie `jakosc["uklad_zgodny"] = False`, `uklad_powod`,
   miary); `porownaj` zwraca slownik z `uklad_zgodny: false`, `uklad_komunikat`, `uklady_pasujace`, pusta lista
   `gniazda`, `statusy_gniazd` same zera, ostrzezenie (`warnings` -> `ostrzezenia` w JSON, "UWAGA:" na stdout), mapa PNG
   przekreslona; kod wyjscia CLI zostaje 0. Okno: ostrzezenie "Plytka nie pasuje do wybranego ukladu" z podpowiedzia,
   mapa przekreslona, gniazda bez kolorow, tabela pusta. Przy zgodnosci `jakosc["uklad_zgodny"] = True` i miary K1, K2.
4. `porownaj --bez-straznika` / `wyrownaj(straznik=False)` wylacza tylko warstwe 2 (wyjscie awaryjne na wypadek, gdyby
   prawdziwy skaner dawal obraz gniazd inny niz dane syntetyczne); warstwa 1 dziala zawsze.

### 5.3 Liczniki (`narzedzia/straznik_R59.py --seedy 10`, 240 skanow, 342 s)

4 typy x 2 uklady x 3 zajetosci x 10 seedow; polowa skanow (seedy nieparzyste) z pracami bokiem, czesciowym pokryciem
i poprawkami; pula: 17 projektow, dla plytki pelnej 17 projektow + 13 atrap, kazdy 3 razy.

| Zajetosc | Skanow | Prac na plytce | ZGODNA: falszywe "nie pasuje" | ZGODNA: K1 max / K2 max [mm2] | NIEZGODNA, program: wykryte (powod) | NIEZGODNA, sam straznik gniazd: wykryte | K1 min-max | K2 min-max |
|---|---|---|---|---|---|---|---|---|
| pusta | 80 | 0 | 0 / 80 | 0,00 / 0,00 | 80 / 80 (stozki) | 80 / 80 | 448,5-810,25 | 284,0-706,5 |
| czesciowa | 80 | 3-6 | 0 / 80 | 23,50 / 0,00 | 80 / 80 (stozki) | 80 / 80 | 437,25-808,75 | 180,25-659,5 |
| pelna | 80 | 19-33 (R59: 19 / 19 i 24 / 24 gniazd; R54: 20 / 20 i 29-33 / 33) | 0 / 80 | 47,75 / 0,00 | 80 / 80 (stozki) | 80 / 80 | 410,0-779,5 | 54,0-385,0 |
| razem | 240 | | 0 / 240 | 47,75 / 0,00 | 240 / 240, komunikat poprawny 240 / 240 | 240 / 240 | >= 410,0 | >= 54,0 |

Per typ i uklad (po 10 skanow w kazdej komorce): 0 falszywych i 10 / 10 wykrytych we wszystkich 24 komorkach - pelna
tabela w logu `logi\straznik_R59.log` i w `dane\straznik_R59\straznik_R59.json`.
- "Sam straznik gniazd" = skan wyrownany wlasnym ukladem i oceniony z modelem drugiego ukladu (tak, jakby stozki obu
  ukladow lezaly w tych samych miejscach).
- Prog K1 = 150 mm2 lezy 3,1 x nad najwiekszym K1 plytki zgodnej (47,75) i 2,7 x pod najmniejszym K1 plytki niezgodnej
  (410,0). K1 > 0 na plytce zgodnej bierze sie z den wnetrza koron lezacych na wysokosci wierzchu plytki (1-2 mm2 na prace).
- Dodatkowo plytki zgodne z przebiegow metryk (pkt 6): 280 skanow, 0 falszywych "nie pasuje", K1 max 30,25, K2 = 0.
  Razem 0 / 520 falszywych.
- Testy: `testy/test_straznik.py` (28): 8 par niezgodnych, 8 ukladow zgodnych, warstwa gniazd na pustych modelach i na
  ukladzie-hybrydzie (stozki jednego ukladu, gniazda i STL drugiego - 4 przypadki, powod `gniazda`), `porownaj`, CLI, okno.
- Granice: dane tylko syntetyczne - progi do potwierdzenia na pierwszym prawdziwym skanie starej i nowej plytki (P3b);
  przy mniej niz 3 dopasowanych stozkach blad pozostaje ogolny ("znaleziono N stozki"), bo nie da sie odroznic zlego
  ukladu od zlego skanu; maly wycinek plytki w skanie niczego nie rozstrzyga (brak danych nie jest dowodem).

## 6. Dane i metryki (stary vs nowy uklad)

Zestawy (PC, poza repo): `dane\syntetyczne_R59_P2` (24 skany) i `dane\syntetyczne_R59_P3a` (16) - polecenia i seedy z
`README.md` / `P3a_przekazanie.md` pkt 4 na ukladzie R59; kontrolnie te same polecenia na `*_r54`
(`dane\syntetyczne_r54_P2`, `_P3a`) oraz wiekszy zestaw kontrolny (polecenie P2, seedy 1000-1019 i 2000-2019, po 80
skanow na uklad). Generowanie: 80 skanow w 47 s i 160 skanow w 93 s (16 procesow). Metryki: `narzedzia/metryki_P3a.py`.

### 6.1 Tabela

| Miara | Punkt odniesienia (zestawy 2.11, kod `origin/main`) | Zestawy 2.11, nowy program na `*_r54` | `*_r54`, zestawy dzisiejsze | **R59, zestawy dzisiejsze** | `*_r54`, zestaw duzy | **R59, zestaw duzy** |
|---|---|---|---|---|---|---|
| skanow / prac w prawdzie | 40 / 420 | 40 / 420 | 40 / 384 | 40 / 397 | 80 / 753 | 80 / 790 |
| wyrownanie OK (max blad mm) | 40 / 40 (0,0137) | 40 / 40 (0,0137) | 40 / 40 (0,0145) | **40 / 40 (0,0143)** | 80 / 80 (0,0149) | **80 / 80 (0,0152)** |
| numer z dolkow, okragle | 24 / 24 | 24 / 24 | 24 / 24 | **24 / 24** | 40 / 40 | **40 / 40** |
| top-1 razem | 411 / 420 | 411 / 420 | 376 / 384 | **382 / 397** | 753 / 753 | **790 / 790** |
| top-1 zestaw P2 | 271 / 271 | 271 / 271 | 235 / 235 | **240 / 240** | - | - |
| top-1 bledny, scenariusz "dobrze" | 0 / 300 | 0 / 300 | 0 / 261 | **0 / 276** | 0 / 662 | **0 / 719** |
| wykrycie dowolna metoda, razem | 259 / 282 (91,8 %) | 259 / 282 | 215 / 231 (93,1 %) | **221 / 248 (89,1 %)** | 554 / 594 (93,3 %) | **659 / 704 (93,6 %)** |
| wykrycie dowolna metoda, "dobrze" | 258 / 279 (92,5 %) | 258 / 279 | 214 / 228 (93,9 %) | **219 / 245 (89,4 %)** | 554 / 594 | **659 / 704** |
| metoda A / B / czerwone | 230 / 133 / 113 | 230 / 133 / 113 | 184 / 109 / 88 | **184 / 107 / 79** | 507 / 268 / 232 | **599 / 294 / 245** |
| prace cale: z czerwonym / z alarmem | 0 / 1 z 129 | 0 / 1 z 129 | 0 / 1 z 136 | **0 / 0 z 127** | 0 / 0 z 245 | **0 / 0 z 247** |
| falszywe ubytki (miejsca) / w tym czerwone | 3 / 0 | 3 / 0 | 3 / 0 | **7 / 2** | 0 / 0 | **0 / 0** |
| drgniecie wykryte / falszywe "skan ponownie" | 28 / 34, 1 | 28 / 34, 0 | 34 / 37, 0 | **35 / 39, 2** | 88 / 91, 0 | **64 / 71, 0** |
| poprawki reczne | 12 / 20 | 12 / 20 | 12 / 20 | **5 / 14** | - | - |
| projekty pominiete (nie weszly na plytke) | 260 | 260 | 296 | **283** | 607 | **570** |
| straznik: falszywe "nie pasuje" (K1 max) | - | 0 / 40 (20,75) | 0 / 40 (20,75) | **0 / 40 (24,00)** | 0 / 80 (30,25) | **0 / 80 (22,75)** |

Czas na plytke (mediana, przebieg jednoprocesowy na zestawach R59): 11,7 s (plate 1,9 + match 8,9 + inspect 0,9; 40 skanow w 8 min 52 s); punkt odniesienia 12,3 s (11 min 13 s). Ten powtorzony przebieg dal te same liczby co przebieg rownolegly (221 / 248, 219 / 245, 382 / 397, 40 / 40) z rozrzutem 1 gniazda (zolte 161 / szare 33 zamiast 162 / 32; falszywe "skan ponownie" 1 zamiast 2). Przebiegi z
`--procesy 10-12` maja czasy zawyzone przez wspoldzielenie procesora (26-48 s) - sa tylko do liczb jakosci.

### 6.2 Kryteria z planu (sekcja 9 pkt 6) na ukladzie R59

| Kryterium | Wynik | Ocena |
|---|---|---|
| wyrownanie 100 % skanow, blad < 0,05 mm | 40 / 40, max 0,0143 mm (zestaw duzy 80 / 80, 0,0152) | spelnione |
| numer z dolkow na okraglych 100 % | 24 / 24 (40 / 40) | spelnione |
| top-1 w scenariuszu "dobrze" 100 % | 276 / 276 (719 / 719) | spelnione |
| falszywe czerwone na pracach calych 0 | 0 / 127 (0 / 247) | spelnione |
| wykrycie "dowolna metoda" nie nizsze niz punkt odniesienia o wiecej niz 3 pkt proc. | razem 89,1 % vs 91,8 % = -2,7 pkt; scenariusz "dobrze" 89,4 % vs 92,5 % = -3,1 pkt | na granicy: razem w normie, "dobrze" o 0,1 pkt za nisko - analiza ponizej, progow nie ruszano |

Odstepstwa od punktu odniesienia poza kryteriami (zestaw P3a, trudne scenariusze): 2 falszywe czerwone miejsca (oba
na JEDNEJ pracy lezacej bokiem w gniezdzie fi 12,5, skan `okragla_poranna_n9_s0311`, metoda B, wciecia 0,43 i 0,62 mm;
praca ma w prawdzie ubytki, wiec nie liczy sie jako "cala"); 2 falszywe "skan ponownie" (prace bokiem, fi 12 i fi 15);
poprawki 5 / 14. To znane slabosci `inspect` na pracach bokiem (P3a_przekazanie pkt 2.4, 2.5), tu na innym losowaniu
prac; na zestawie duzym (bez trudnych scenariuszy) falszywych ubytkow jest 0.

### 6.3 Analiza per srednica gniazda (scenariusz "dobrze", ubytki wykrywalne: wykryte dowolna metoda / wszystkie)

| Klasa gniazda | Zestawy 2.11 na `*_r54` | `*_r54` dzisiejsze | R59 dzisiejsze | `*_r54` duzy | R59 duzy |
|---|---|---|---|---|---|
| fi 7,5 / fi 9 | 1 / 1 | 5 / 5 | - | 12 / 13 | - |
| fi 10 | 58 / 62 (93,5 %) | 37 / 39 (94,9 %) | - | 98 / 102 (96,1 %) | - |
| fi 12 | 57 / 59 (96,6 %) | 40 / 42 (95,2 %) | 54 / 61 (88,5 %) | 102 / 108 (94,4 %) | 131 / 136 (96,3 %) |
| fi 12,5 | 48 / 55 (87,3 %) | 35 / 38 (92,1 %) | 75 / 85 (88,2 %) | 89 / 98 (90,8 %) | 230 / 242 (95,0 %) |
| fi 15 | 41 / 47 (87,2 %) | 36 / 41 (87,8 %) | 63 / 71 (88,7 %) | 95 / 105 (90,5 %) | 223 / 245 (91,0 %) |
| rynienka | 53 / 55 (96,4 %) | 61 / 63 (96,8 %) | 27 / 28 (96,4 %) | 158 / 168 (94,0 %) | 75 / 81 (92,6 %) |
| razem "dobrze" | 258 / 279 (92,5 %) | 214 / 228 (93,9 %) | 219 / 245 (89,4 %) | 554 / 594 (93,3 %) | 659 / 704 (93,6 %) |

Wnioski (bez strojenia progow):
1. Wykrywalnosc zalezy od klasy gniazda takze na starym ukladzie: w fi 12,5 i fi 15 jest 87-92 %, w fi 10, fi 12 i w
   rynienkach 93-97 %. Nowy uklad przesuwa prace do fi 12,5 / fi 15 (w zestawach 40 skanow: 278 z 397 prac zamiast 182
   z 420) i zabiera jedna rynienke (40 prac zamiast 80), wiec srednia spada sama ze zmiany skladu: stawki per klasa z
   zestawow 2.11 przylozone do skladu R59 daja 90,6 % w scenariuszu "dobrze" (z 92,5 %) i 89,9 % razem (z 91,8 %),
   czyli ok. 1,9 pkt spadku wynika z samego skladu.
2. Reszta to klasa fi 12 w malym zestawie R59 (54 / 61): 5 z 7 pominietych ubytkow nalezy do jednego projektu
   (`2e15189ef6d12701`, w fi 12: 12 / 17), ktory na starym ukladzie w tym samym gniezdzie fi 12 mial 23 / 23. Gniazdo
   fi 12 jest w obu ukladach takie samo, wiec przyczyny w geometrii ukladu nie widac.
3. Zestaw duzy (2,8 x wiecej ubytkow) nie potwierdza spadku: R59 93,6 % vs `*_r54` 93,3 %, w kazdej klasie okraglej
   R59 jest nie gorsze (fi 12: 96,3 vs 94,4; fi 12,5: 95,0 vs 90,8; fi 15: 91,0 vs 90,5). Roznica -2,7 / -3,1 pkt
   na zestawach 40 skanow (248 ubytkow) miesci sie w rozrzucie probki i zmianie skladu.
4. Do obserwacji na prawdziwych skanach (P3b): wykrywalnosc ubytkow w gniazdach fi 12,5 / fi 15 (ok. 90 %) oraz
   drgniecie na nowym ukladzie (zestaw duzy: 64 / 71 = 90 % vs 88 / 91 = 97 % na starym).

## 7. Pojemnosc (`narzedzia/pojemnosc_R59.py`, 17 projektow, 20 seedow na uklad, ta sama procedura co generator)

Pula 17 projektow: 11 pojedynczych prac (korony, prace bez lacznika, 1 waxup pojedynczy) i 6 mostow / waxupow o
obrysie 18-30 mm, ktore wchodza tylko do rynienki.

| Miara | Wieczorna R54 (1,22) | **Wieczorna R59 (1,22)** | Poranna R54 (1,0) | **Poranna R59 (1,0)** |
|---|---|---|---|---|
| gniazda okragle + rynienki | 18 + 2 | **18 + 1** | 31 + 2 | **23 + 1** |
| gniazda okragle, w ktore wchodzi choc jedna z 17 prac | 11 (fi 9: 0 z 7 uzytych) | **18** | 13 (fi 7,5: 0 z 18 uzytych) | **23** |
| pierwsza plytka: prace osadzone z 17 (min-max) | 11,30 (11-12) | **10,65 (10-11)** | 11,10 (11-12) | **12,00 (12-12)** |
| pierwsza plytka: pominiete | 5,70 | **6,35** | 5,90 | **5,00** |
| - w gniazdach okraglych | 9,30 | **9,65** | 9,10 | **11,00** |
| - w rynience (mosty + inne prace) | 2,00 (1,60 + 0,40) | **1,00 (0,85 + 0,15)** | 2,00 (1,30 + 0,70) | **1,00 (0,80 + 0,20)** |
| zajetosc per srednica (srednio zajetych / gniazd) | fi 9: 0 / 7; fi 12: 4,95 / 6; fi 15: 4,35 / 5; rynienki 2 / 2 | **fi 12: 4,80 / 6; fi 15: 4,85 / 12; rynienka 1 / 1** | fi 7,5: 0 / 18; fi 10: 4,85 / 7; fi 12,5: 4,25 / 6; rynienki 2 / 2 | **fi 12,5: 9,75 / 20; fi 15: 1,25 / 3; rynienka 1 / 1** |
| plytek potrzebnych na cala pule (min-max) | 4,00 (4-4) | **7,05 (7-8)** | 4,00 (4-4) | **6,00 (6-6)** |
| pelna plytka (pula x 3 = 51 prac): prac na plytce | 13 (z 20 gniazd) | **19 (z 19)** | 15 (z 33 gniazd) | **24 (z 24)** |

Co z tego wynika dla wlasciciela:
1. **Korony i prace pojedyncze: wiecej miejsca.** Pelna plytka miesci 19 prac zamiast 13 (wieczorna, +46 %) i 24 zamiast
   15 (poranna, +60 %), bo w gniazda fi 9 i fi 7,5 starego ukladu nie wchodzila zadna z 17 prac. Na plytce porannej
   dwa duze trzonowce bez lacznika (`a4d10c94db53a1a1`, `066fcc6858e01759`) laduja w gniazdach okraglych (fi 15 / fi 12,5)
   20 razy na 20; na starym ukladzie trafialy na pierwsza plytke 6 i 3 razy na 20 (rynienka). Wszystkie 11 prac
   pojedynczych lezy w gniazdach okraglych pierwszej plytki porannej (stary uklad: srednio 9,1).
2. **Mosty: jeden na plytke.** W puli jest 6 mostow / waxupow, a rynienka jedna, wiec na cala pule trzeba 6 plytek
   porannych zamiast 4 i 7 wieczornych zamiast 4 (wieczorem do rynienki musi isc tez trzonowiec 9,2 x 11,3, ktory
   przy skurczu 1,22 nie wchodzi w fi 15). To wprost skutek decyzji "jedna rynienka" (D3-a): przy dniach z wieloma
   mostami potrzeba wiecej plytek albo wariantu z dwiema krotkimi rynienkami (D3-b, odlozony).
3. Wieczorem na pierwszej plytce jest o 0,65 pracy mniej (10,65 vs 11,30) - cala roznica to brak drugiej rynienki
   (w gniazdach okraglych jest 9,65 vs 9,30); rano o 0,9 wiecej (12,0 vs 11,1).
4. Sprawdzenie gniazda fi 15 na plytce porannej wg `katalog.gniazdo_dla` (wsp. 1,0): w fi 15 laduja `066fcc6858e01759`
   (obrys 11,6 x 10,6) i `a4d10c94db53a1a1` (11,3 x 9,2); korona o najdluzszym boku (`a823e3b4aff6b60e`, 11,7 x 9,1)
   miesci sie w fi 12,5 - to poprawne (dobor idzie od najmniejszego pasujacego gniazda).

## 8. Zmienione i nowe pliki (wszystkie w `Ramki/stanowisko/`)

- Modele: `modele_plytek/{wieczorna,poranna,okragla_wieczorna,okragla_poranna}/*` (14 plikow podmienionych),
  `modele_plytek/{...}_r54/*` (14 nowych, kopie sprzed R59).
- Kod: `stanowisko/plate.py` (straznik), `porownaj.py` (wynik niezgodny, `--bez-straznika`, mapa), `uklad.py`
  (`nazwa` = nazwa ukladu, `typ_plytki`), `synth.py` (`poranna`, opis `--plytka`), `ui_test.py` (komunikat),
  `ustawienia.py` (komentarz), `ustawienia.przyklad.toml` (4 klucze `*_r54`).
- Narzedzia: zmienione `narzedzia/metryki_P3a.py`, `metryki_P2.py`, `rzut_z_gory.py`, `katalog_projektow.py`; nowe
  `narzedzia/straznik_R59.py`, `narzedzia/pojemnosc_R59.py`.
- Testy: zmienione `testy/test_uklad.py`, `test_edge_uklad.py`, `test_synth.py`, `test_edge_synth.py`, `test_plate.py`,
  `test_katalog.py`, `test_match.py`, `test_ustawienia.py`; nowe `testy/test_uklad_r59.py`, `testy/test_straznik.py`.
- Opisy: `README.md`, `opisy_modulow/{README,uklad,plate,synth,katalog,ui}.md`, ten raport.
- Konce linii kazdego zmienionego pliku zachowane (`git diff --numstat` = `--ignore-cr-at-eol` dla wszystkich).
- Skrypty pomiarowe jednorazowe (poza repo, PC `<PC-katalog>\r59\program\pomiary\`): `stan_obecny.py`, `t8_r54.py`,
  `t8_roznica.py`, `generuj_R59.py`, `generuj_duzy.py`, `porownaj_zestawy_r54.py`, `analiza_ubytkow.py`,
  `analiza_projekty.py`, `lista_sha.py`.

## 9. Odstepstwa, ograniczenia, czego nie zrobiono

1. `SCHEMAT` w `ustawienia.py` nie dostal nowych kluczy wymaganych: nazwy w `[plytki]` sa dowolne (tak bylo), a wymog
   4 kluczy `*_r54` zatrzymalby program na kazdej maszynie ze starym `ustawienia.toml`. Skutek: stary `ustawienia.toml`
   dziala, ale nie ma w nim ukladow `*_r54` (test `test_przyklad_ma_te_same_klucze_co_lokalny` to pokaze) - trzeba
   dopisac 4 wiersze ze wzoru (zadanie dla czlowieka na pulpicie PC i na laptopie stanowiska).
2. `test_match.py::test_zgrubne_obroty_i_ocena` dziala tylko na `okragla_wieczorna_r54`. Ostatnia asercja sprawdza sam
   RANSAC (seed 0) na pierwszym fragmencie; ta sciezka jest krucha niezaleznie od ukladu (zmierzone, seed skanu 22:
   `_r54` fragment 0 - seed RANSAC 0 / 1 / 2 daje pokrycie 0,90 / 0,53 / 0,90; R59 fragment 0 - 0,27 / 0,89 / 0,89).
   Pelne `dopasuj` przechodzi na obu ukladach (`test_dopasowanie_top1_i_transformacja` x 2). Logiki `match` nie ruszano.
3. Straznik rzuca wyjatek zamiast zwracac `WynikWyrownania` z flaga: przy niezgodnych stozkach wyrownania nie ma, a
   jeden sposob obslugi (wyjatek z `jakosc["uklad_zgodny"] = False`) nie pozwala przez nieuwage uzyc gniazd z
   niezgodnego ukladu. `porownaj` zamienia wyjatek na zwykly wynik z `uklad_zgodny: false`.
4. Kryterium "dowolna metoda" w scenariuszu "dobrze": -3,1 pkt (granica 3) na zestawach 40 skanow; razem -2,7 pkt.
   Analiza w pkt 6.3; zestaw duzy nie potwierdza spadku. Progow nie strojono.
5. Na zestawie P3a R59: 2 falszywe czerwone miejsca na jednej pracy lezacej bokiem i 2 falszywe "skan ponownie" (pkt 6.2).
6. Okno (`ui_test.py`) pozostaje szkicem z P3a (watek silnika zawisa; 2 testy okna pominiete jak dotad). Komunikat
   straznika jest sprawdzony testem bez watku (`test_okno_lista_ukladow_i_komunikat_straznika`), nie w dzialajacym oknie.
7. Zestawy `syntetyczne_R59_*` maja inny sklad niz zestaw P2 z 2.11 (pkt 4) - porownanie "stary vs nowy" opiera sie
   glownie na kolumnach "zestawy dzisiejsze" i "zestaw duzy" (ten sam generator, te same polecenia).
8. Czasy na plytke z przebiegow rownoleglych nie sa porownywalne z punktem odniesienia (pkt 6.1).
9. Nie robiono: prawdziwych skanow (nie ma skanera), strojenia progow, zmian w `match` / `inspect`, dokumentow poza
   `Ramki/stanowisko`.
10. Nowe pliki tekstowe sa ASCII z wyjatkiem czterech `modele_plytek/*_r54/uklad.json` - to bajtowe kopie plikow
   sprzed R59 (opisy pol z polskimi znakami), celowo nie zmieniane.

Zadania dla czlowieka wynikajace z tej czesci:
- PO AKTUALIZACJI PROGRAMU dopisac 4 wiersze `wieczorna_r54`, `poranna_r54`, `okragla_wieczorna_r54`,
  `okragla_poranna_r54` do lokalnego `ustawienia.toml`, sekcja `[plytki]` (pulpit PC, laptop stanowiska) - wzor w
  `ustawienia.przyklad.toml`. Bez nich: (a) stare plytki fizyczne nie sa rozpoznawane - nie ma ich na liscie, a kazdy
  ich skan konczy sie "plytka nie pasuje do wybranego ukladu" (od poprawek po recenzji PR komunikat podpowiada wtedy,
  ze brakuje tych 4 wierszy); (b) czesc testow jest czerwona, bo biora lokalny plik ustawien: `test_straznik.py`
  (fixture `wynik_niezgodny` i testy z niej korzystajace), `test_uklad.py::test_wszystkie_plytki_z_ustawien`,
  `test_ustawienia.py` (`test_przyklad_ma_te_same_klucze_co_lokalny`, `test_sciezki_plytek_jedno_zrodlo`). Testow nie
  przerabiano (wzorzec sprzed R59: lokalny plik ma miec te same klucze co wzor);
- opisac stare plytki fizyczne ("R54") i trzymac je osobno; w programie wybierac dla nich uklad `..._r54`;
- lista do sprawdzenia na pierwszym prawdziwym skanie (P3b; to samo w `README.md`, "Laptop firmowy" pkt 7):
  1. stara plytka z ukladem `..._r54`, pusta i pelna prac: w JSON `jakosc_wyrownania.uklad_zgodny` = true,
     `uklad_gniazdo_nad_pelnym_mm2` (K1; na skanach syntetycznych plytka zgodna <= 48, prog 150),
     `uklad_dziura_w_pelnym_mm2` (K2; zgodna 0, prog 50) - progi sa dobrane wylacznie na skanach syntetycznych z 17 projektow;
  2. ten sam skan z celowo wybranym nowym ukladem: ma byc "plytka nie pasuje do wybranego ukladu" z nazwa wlasciwego ukladu;
  3. falszywy alarm na plytce zgodnej: okno NIE MA odpowiednika `--bez-straznika` i technik nie przejdzie w nim dalej -
     najpierw oczyscic stozki znacznikow i zeskanowac ponownie (falszywy albo zabrudzony stozek daje ten sam komunikat),
     a gdy alarm zostaje: `py -3.12 -m stanowisko.porownaj ... --bez-straznika` z wiersza polecen i zapisac K1, K2;
  4. granica na przyszlosc: straznik nie odrozni dwoch ukladow o tych samych stozkach rozniacych sie tylko podzialem
     rynienki (odlozony wariant D3-b; dzis takiej pary nie ma) - opis i liczby w `opisy_modulow/plate.md`.

## 10. Gdzie leza dane i jak powtorzyc (PC, `<PC-katalog>\r59\program\`)

- Program: `Ramki\stanowisko` (= worktree: 78 z 78 plikow o tym samym SHA-256, sprawdzone skryptem `pomiary\lista_sha.py` po ostatniej wysylce), `Ramki\parametry.json`, `run.cmd`, lokalny
  `ustawienia.toml` (kopia z pulpitu + 4 klucze `*_r54`).
- Logi: `logi\pytest_0*.log`, `straznik_R59.log`, `stan_obecny.log`, `t8_r54.log`, `generuj_R59.log`,
  `generuj_duzy.log`, `metryki_a_zestawy_2_11_r54.log`, `metryki_b_r54_dzis.log`, `metryki_c_R59.log`,
  `metryki_d_R59_duzy.log`, `metryki_e_r54_duzy.log`, `metryki_f_R59_sekwencyjnie.log`, `pojemnosc_R59.log`,
  `pojemnosc_R59_x3.log`.
- Dane (`Ramki\stanowisko\dane\`, poza repo, ok. 14 GB): `syntetyczne_R59_P2`, `syntetyczne_R59_P3a`,
  `syntetyczne_r54_P2`, `syntetyczne_r54_P3a`, `syntetyczne_R59_duzy`, `syntetyczne_r54_duzy`, `t8_r54`,
  `straznik_stan_obecny`, `straznik_R59` (JSON; skanow nie zapisywano), `straznik_cli`, `kontrola_stary_kod`.
- Wyniki: `dane\wyniki_R59\metryki_*.json` (6 plikow), `dane\straznik_R59\straznik_R59.json`,
  `dane\pojemnosc_R59\pojemnosc_R59.json`, `dane\pojemnosc_R59_x3\pojemnosc_R59.json`, `dane\t8_r54\t8_r54.json`,
  `dane\straznik_stan_obecny\stan_obecny.json`, `dane\katalog_R59.json`.
- Pliki z nazwami projektow (mapy skrot -> nazwa pliku) zostaly po pomiarach usuniete z `dane\`; w wynikach sa tylko skroty.

Polecenia (z `Ramki\stanowisko`, przez `run.cmd`; `P` = `<PC-katalog>\r59\Prace_test`):
```
run.cmd -m pytest testy -q -p no:cacheprovider
run.cmd narzedzia\straznik_R59.py --projekty P --wyjscie dane\straznik_R59 --seedy 10 --procesy 14
run.cmd <PC-katalog>\r59\program\pomiary\generuj_R59.py --procesy 16
run.cmd narzedzia\metryki_P3a.py --skany dane\syntetyczne_R59_P2 dane\syntetyczne_R59_P3a --projekty P --wyjscie dane\wyniki_R59 --nazwa metryki_R59.json --procesy 12
run.cmd narzedzia\metryki_P3a.py --skany <baseline>\dane\syntetyczne_P2 <baseline>\dane\syntetyczne_P3a --projekty P --sufiks-ukladu _r54 --wyjscie dane\wyniki_R59 --nazwa metryki_zestawy_2_11_na_r54.json --procesy 12
run.cmd narzedzia\pojemnosc_R59.py --projekty P --wyjscie dane\pojemnosc_R59 --seedy 20 --procesy 10
run.cmd narzedzia\pojemnosc_R59.py --projekty P --wyjscie dane\pojemnosc_R59_x3 --seedy 20 --procesy 10 --powtorz 3 --tylko-pierwsza
run.cmd -m stanowisko.synth --projekty P --plytka wieczorna_r54 --ile 1 --seed 7001 --wspolczynnik 1.22 --drgniecie 0.1 --poza-uklad --pole 100 --wyjscie dane\t8
run.cmd -m stanowisko.porownaj --skan dane\t8\skan_wieczorna_r54_n3_s7001.stl --projekty P --plytka wieczorna_r54 --wspolczynnik 1.22 --numer 3 --prawda dane\t8\skan_wieczorna_r54_n3_s7001.json --wyjscie dane\t8\wynik
```

## 11. Poprawki po recenzji PR (runda 1), 15.11.2026

Recenzja: `../../recenzja/raport_recenzenta_PR_R59_runda1.md` (B 0 / P 0 / D 12); do programu naleza uwagi 1, 2, 3, 4,
11 i 12c. Same teksty, komentarze i jedno narzedzie pomiarowe - logika straznika, progi K1 / K2, `plate.py`, `match.py`,
`inspect.py` i `synth.py` BEZ ZMIAN, wiec licznikow straznika i metryk nie przeliczano.

| Uwaga | Co zmieniono | Plik |
|---|---|---|
| 1 | Przy obu blokach starych polecen (P2 i P3a) dopisek "Od R59": zestawy `dane/syntetyczne_P2` / `_P3a` wygenerowane przed R59 sa w ukladzie R54 i wymagaja `--plytka ..._r54` / `--sufiks-ukladu _r54`; polecenia z bloku dzialaja na zestawach generowanych od nowa | `README.md` |
| 2 | Skan odrzucony przez straznika zostaje w wyniku: lista `uklad_niezgodny` (skan, uklad, powod, komunikat, miary) w JSON, liczniki `plate.uklad_niezgodny` i `plate.skanow_w_zestawie`, wiersz "UKLAD NIEZGODNY: n z N" w podsumowaniu; gdy nie pasuje zaden skan, JSON tez powstaje | `narzedzia/metryki_P2.py` |
| 3a | Granica: reszta > 0,3 mm przy >= 3 dopasowanych stozkach daje "plytka nie pasuje..." takze przy falszywym albo zabrudzonym stozku - oczyscic stozki, skan ponownie | `opisy_modulow/plate.md`, `README.md` |
| 3b | Gdy `uklady_pasujace` jest puste i w `[plytki]` nie ma zadnego ukladu z przyrostkiem `_r<NN>`: komunikat `porownaj` (i nowe pole wyniku `uklad_podpowiedz`), wiersz tabeli, napis na mapie PNG i okno podpowiadaja "dopisz 4 wiersze *_r54 z ustawienia.przyklad.toml"; przy pelnych ustawieniach `uklad_podpowiedz` = "" | `stanowisko/porownaj.py`, `stanowisko/ui_test.py`, `opisy_modulow/plate.md`, `opisy_modulow/ui.md` |
| 3b - testy | `test_stary_plik_ustawien_podpowiada_brakujace_uklady_r54` (podpowiedz jest przy starych ustawieniach; nie ma jej, gdy uklady `_r54` sa, takze wtedy, gdy zaden nie pasuje), `test_okno_podpowiada_brak_ukladow_r54` | `testy/test_straznik.py` |
| 4a | Opis: okno nie ma odpowiednika `--bez-straznika`; progi K1 / K2 dobrane na skanach syntetycznych; przelacznik przy naprawie okna (P3a-2). Zadnej nowej funkcji | `opisy_modulow/plate.md`, `opisy_modulow/ui.md`, `README.md` (lista P3b), ten raport (zadania czlowieka) |
| 4b | Opis granicy: dwa uklady o tych samych stozkach rozniace sie tylko podzialem rynienki (D3-b, odlozony) nie sa rozrozniane; liczby z rachunku recenzenta (K1 ok. 46 < 150, K2 ok. 31 < 50); dopisek, ze K2 z licznikow "sam straznik gniazd" zawiera ok. 15 mm2 od stozkow drugiego ukladu, wiec dla ukladow o wspolnych stozkach decyduje K1 | `opisy_modulow/plate.md`, `README.md`, ten raport |
| 11 | Po aktualizacji programu trzeba dopisac 4 wiersze `*_r54` do lokalnego `ustawienia.toml` - inaczej stare plytki nie sa rozpoznawane, a czesc testow jest czerwona; zapisane w sekcji "Ustawienia" i "Laptop firmowy" pkt 4 oraz w zadaniach czlowieka (pkt 9). Testow nie przerabiano | `README.md`, ten raport |
| 12c | Komentarz przy `skip` testu `test_okno_na_skanie_P2`: zestaw `dane/syntetyczne_P2` jest w ukladzie R54, po zdjeciu `skip` trzeba wybrac uklad z przyrostkiem `_r54`. Stan `skip` bez zmian | `testy/test_ui.py` |

- pytest (PC): 250 passed / 3 skipped / 0 failed -> **252 passed / 3 skipped / 0 failed** (255 zebranych; +2 testy z uwagi
  3b). Pominiete te same 3 testy; numer linii jednego z nich w wykazie zmienil sie z `test_ui.py:126` na `test_ui.py:129`
  (3 linie komentarza z uwagi 12c).
- Sciezka obliczen: poprawka 3b dotyka `porownaj.porownaj` tylko w galezi `except NiezgodnyUklad` (tekst komunikatu i
  nowe pole `uklad_podpowiedz`); wynik dla skanu zgodnego i wszystkie liczby (wyrownanie, match, inspect, K1, K2) licza
  sie tym samym kodem co przed poprawkami. `metryki_P2.py`: zmiana tylko w obsludze skanu odrzuconego i w skladaniu
  JSON; sprawdzone na zestawie mieszanym (1 skan R59 + 1 skan sprzed R59 bez przyrostka): `plate.skanow` 1,
  `skanow_w_zestawie` 2, `uklad_niezgodny` 1, liczby skanu zgodnego jak przed zmiana (wyrownanie 0,0019 mm, top-1 12 / 12).
- Zmienione pliki (8, wszystkie w `Ramki/stanowisko/`): `README.md`, `narzedzia/metryki_P2.py`, `opisy_modulow/plate.md`,
  `opisy_modulow/ui.md`, `stanowisko/porownaj.py`, `stanowisko/ui_test.py`, `testy/test_straznik.py`, `testy/test_ui.py`
  oraz ten raport. Konce linii zachowane; pliki programu PC = worktree 78 z 78 (SHA-256).
- Nie zrobiono (zgodnie z zakresem uwag): przelacznika straznika w oknie ani w `ustawienia.toml` (uwaga 4a - przy
  naprawie okna, po pomiarze na prawdziwych skanach), rozrozniania ukladow D3-b (uwaga 4b - wariant odlozony),
  przerabiania testow na `ustawienia.przyklad.toml` (uwaga 11 - wybrano zapis w zadaniach czlowieka).
