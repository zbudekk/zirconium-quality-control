# Czesc A - filtr wymiarow w match (P1) i korekta skali ze skanu (P3)

Data: 15-16.11.2026. Paczka "program przed skanerem", czesc A. Zgoda wlasciciela na P1 i P3: 15.11.2026.
Decyzja o wspolczynniku: `dyskusja_ubytki_0_02mm_2026-11-06.md` pkt 9a (wspolczynnik z puli + korekta skali ze
skanu w oknie +-1 %, ostrzezenie > 0,3 %, rano bez korekty). Stan wyjsciowy: `8b83da7` (= `origin/bp/r59` bez
ostatniego commitu z `00_NADZOR_STAN.md`). Galaz `czesc-a`. Wszystkie obliczenia na PC (`<PC-katalog>\app\a`),
dane wylacznie syntetyczne (skanera jeszcze nie ma). Projekty w tekscie tylko jako skrot (16 znakow SHA-256).

## Stan

| Krok | Co | Stan |
|---|---|---|
| 0 | kopia na PC, pytest na `8b83da7` | zrobione: 252 passed / 3 skipped / 0 failed (= punkt odniesienia) |
| 1 | P1 filtr + P3 korekta skali w `match`, pola w `porownaj`, `inspect` przyjmuje podobienstwo, klucze `[match]` | zrobione (`b5e1f48`, poprawka `319f861`) |
| 2 | testy (`test_match`, nowy `test_skala`, `test_ustawienia`, `test_narzedzia`) | zrobione; pelny pytest na `8ad7821`: 276 / 3 / 0; po `319f861` tylko podzbior (pkt 2) |
| 3 | narzedzie `narzedzia/metryki_skala.py` (tryby `p1`, `program`, `brzeg`) | zrobione (`15820d5`, `319f861`) |
| 4 | punkt odniesienia: stary kod na zestawach R59 i r54 | zrobione (pkt 3) |
| 5 | pomiary nowego kodu: R59 blad 0, strefa brzegu, R59 wieczorne przy bledzie +-0,1 ... +-1 % | zrobione na kodzie `15820d5` (przed poprawka `319f861`; pkt 3.0) |
| 6 | pomiary koncowe na `319f861` (R59, r54, P1 z widocznoscia na calym zestawie, rano przy bledzie, czas jednoprocesowo) | **NIE zrobione: PC przestal odpowiadac ok. 01:35 (16.11), 3 proby co 60 s bez odpowiedzi** - polecenia w pkt 8 |

**Przerwane.** Pomiary koncowe (krok 6) ruszyly o 01:12 czasu PC i urwaly sie razem z polaczeniem; wyniki, ktore
zdazyly powstac, leza na PC w `<PC-katalog>\app\a\wyniki\v2` (nieodczytane). Liczby w tym raporcie sa z kroku 4
(stary kod) i kroku 5 (kod `15820d5`). Roznica `15820d5` -> `319f861` dotyczy tylko prac nierozpoznanych (pkt 3.0).

## 1. Co zmieniono i dlaczego

### 1.1 P1 - filtr wymiarow (`match.filtr`)

Przed: wysokosc, oba boki obrysu xy i objetosc otoczki fragmentu porownywane z CALYM projektem x wspolczynnik,
tolerancja max(1,5 mm, 15 %) / 35 %. Fragment ze skanu bywa nizszy niz projekt (widok z gory: 82-92 % wysokosci -
T7; dolne 1,5 mm w gniezdzie - T10), wiec wlasciwy projekt wypadal z puli po wysokosci, a gdy przechodzil wysokosc -
mogl wypasc po otoczce (otoczka nizszego fragmentu jest mniejsza).

Po:
1. Wysokosc jednostronnie: fragment nie wyzszy niz projekt + tolerancja (jak dotad) i nie nizszy niz
   `filtr_wysokosc_min_udzial` x wysokosc projektu (nowy klucz, 0,5), przy czym dolna granica nigdy nie jest
   ostrzejsza niz dotychczasowa (projekt - tolerancja). `filtr_wysokosc_min_udzial = 1.0` = regula sprzed zmiany.
2. Obrys xy i objetosc otoczki porownywane z projektem PRZYCIETYM do wysokosci fragmentu (od brzegu w dol;
   `Projekt.cechy_do_glebokosci`, krok 0,5 mm w gore, z probki powierzchni 40 tys. punktow, zapamietane na projekcie).
   Dla fragmentu pelnej wysokosci to cechy calego projektu - filtr sprzed zmiany. Tolerancje bez zmian.
Dlaczego tak, a nie "bez wysokosci": dolna granica 50 % i porownanie obrysu / otoczki z czescia projektu trzymaja
pule waska (pkt 3.1: przechodzi srednio 2,2-2,8 projektu z 17 zamiast 0,4-2,0), a fragment wyzszy niz projekt nadal
odpada.

### 1.2 P3 - korekta skali ze skanu (`match.skala_ze_skanu`, `match.koryguj_skale`)

Po rankingu, dla najlepszego kandydata (dla drugiego tylko, gdy jego pokrycie >= 0,5 x pokrycie pierwszego - ranking
niepewny, jak przy bledzie wspolczynnika; potem ranking od nowa):
1. **Estymata** - podobienstwo x = s R p + t (obrot, przesuniecie, jedna skala) dopasowane do siatki projektu x
   wspolczynnik puli: Gauss-Newton, odleglosc punkt-plaszczyzna do najblizszego trojkata (Open3D RaycastingScene), wagi
   Tukeya, start z transformacji z `dopasuj_pare`. To metoda T7 wariant C, z trzema zmianami:
   - **punkty w pasie brzegu wylaczone** (zastrzezenie R2b): punkt skanu blizej brzegu niz `korekta_skali_pas_brzegu_mm`
     (2,0 mm od z = 0 projektu w ukladzie puli) nie bierze udzialu. Pas 2,0 > 1,5 mm pasa ukruszen `[inspect]` i > 2,0 mm
     strefy wersji C z R2b (pelna zmiana do 1,4, wygaszenie do 2,0 mm);
   - **stala siatka usredniania 0,1 mm** (poczatek w zerze ukladu, nie w rogu chmury jak `voxel_down_sample`): punkty
     poza pasem daja te same srednie niezaleznie od tego, co jest w pasie - ukruszenie brzegu nie zmienia danych estymaty;
   - **reszty w mm skanu (r / s), nie w ukladzie puli**: skalowanie punktow skanu skaluje tez ich szum, wiec minimum
     sumy r^2 lezy przy za malym s (obciazenie ok. +sigma^2 / srednia (n.u)^2). Zmierzone na 9 projektach (sonda, pkt 6):
     przy sigma 0,03 mm obciazenie +0,005 ... +0,049 % (to jest "+0,01 %" z raportu T7), po zmianie -0,003 ... +0,011 %.
   Dwa przejscia: po pierwszym reszty usrednione po otoczeniu 0,3 mm wyznaczaja obszary odbiegajace od projektu
   (|srednia| > max(0,03 mm, sigma reszt): gladka poprawka reczna, ubytek poza pasem) i w drugim sa pominiete (T7:
   bez tego poprawka reczna przeciaga skale do 0,09 %). Brak skali, gdy poza pasem zostaje < 300 punktow albo
   dopasowanie ucieka ponad +-5 % (obcy projekt).
2. **Zastosowanie** - poprawka e = (1/s - 1) x 100 % (praca o e % wieksza niz projekt x wspolczynnik puli). Gdy
   |e| <= `korekta_skali_okno_proc` (1,0) + 0,05 (dokladnosc estymaty), plytka nie jest poranna, pokrycie po korekcie
   >= `prog_ostrzezenia_pokrycie` i nie spada o ponad 0,02: pokrycie, RMS i transformacja kandydata sa liczone w skali
   skorygowanej (po estymacie krotki ICP 0,2 -> 0,08 mm na wszystkich punktach przy ustalonej skali). Transformacja
   (projekt x w) -> plytka jest wtedy podobienstwem; `inspect` liczy na niej odchylki (jedyna zmiana w `inspect.py`:
   normalne obracane bez skali).
3. **Ostrzezenie** - |e| > `korekta_skali_ostrzezenie_proc` (0,3), takze poza oknem; nie ma go, gdy estymata jest
   **niepewna** (pokrycie po korekcie < `prog_akceptacji_pokrycie`: skan nie pasuje do projektu w zadnej skali -
   drgniecie, praca bokiem; pkt 4.1: blad estymaty do +-0,5 %, wiec liczba nic nie mowi o wspolczynniku).
4. **Rano** - `porownaj` przekazuje dla plytki porannej `bez_korekty`: poprawka jest liczona i pokazywana (z
   ostrzezeniem - odchylka skali pracy spieczonej to wada pracy), ale nie stosowana.
5. **Wynik** - kazde gniazdo w JSON `porownaj` ma pole `skala`: `poprawka_proc`, `zastosowana`, `powod` (dlaczego
   nie), `ostrzezenie`, `niepewna`, `wspolczynnik_puli`, `wspolczynnik_ze_skanu`, `pokrycie_przed`, `pokrycie_po`,
   liczby punktow, `iteracje`, `czas_s` (to samo w `kandydaci[0].skala`). Tabela na stdout: kolumna "skala %" (w
   nawiasie = zmierzona, niezastosowana; "!" = ostrzezenie; "?" = niepewna) i wiersz "OSTRZEZENIE SKALI ..." z
   numerami gniazd; ostrzezenie trafia tez do `uwagi` gniazda.
6. **Wspolczynnik per projekt** - `match.Pula(..., wspolczynniki={skrot: w})`: droga dla wspolczynnika z raportu MillBox
   kazdej pracy (nikt go dzis nie podaje; parsera MillBox nie budowalem).

Nowe klucze `[match]` (SCHEMAT w `ustawienia.py` z walidacja, `ustawienia.przyklad.toml`, testy w `test_ustawienia.py`):
`filtr_wysokosc_min_udzial = 0.5`, `korekta_skali = true`, `korekta_skali_okno_proc = 1.0`,
`korekta_skali_ostrzezenie_proc = 0.3`, `korekta_skali_pas_brzegu_mm = 2.0`. Parametry estymatora (siatka 0,1 mm,
wagi, liczby iteracji) sa stalymi w `match.py` jak dotychczasowe parametry ICP - to nie sa progi decyzji.

### 1.3 Zmienione pliki (wszystkie w `Ramki/stanowisko/`)

`stanowisko/match.py` (filtr, `Projekt.cechy_do_glebokosci`, `Pula(wspolczynniki=)`, `KorektaSkali`,
`skala_ze_skanu`, `koryguj_skale`, `skala_macierzy`, `ocena` i `blad_pozy` dla podobienstwa), `stanowisko/porownaj.py`
(tylko `dopasuj_fragmenty` i `tabela`), `stanowisko/inspect.py` (1 linia: normalne bez skali), `stanowisko/ustawienia.py`
i `ustawienia.przyklad.toml` (5 kluczy `[match]`), `testy/test_match.py` (+3 testy), nowy `testy/test_skala.py`
(12 funkcji, 14 przypadkow), `testy/test_ustawienia.py` (+5 przypadkow nowych kluczy), `testy/test_narzedzia.py`
(+1), nowe `narzedzia/metryki_skala.py`, `opisy_modulow/match.md`, ten raport. Konce linii zachowane.
Istniejacych testow nie zmienialem (tylko dopisane przypadki).

## 2. Testy (PC, `run.cmd -m pytest testy -q -p no:cacheprovider`)

| Stan | passed | skipped | failed | Log (`<PC-katalog>\app\a\logi\`) |
|---|---|---|---|---|
| `8b83da7` (punkt odniesienia) | 252 | 3 | 0 | `pytest_00_baza.log` |
| po P1 + P3 + testach (`8ad7821`) | 276 | 3 | 0 | `pytest_01_po_zmianach.log` |
| `319f861`: `test_skala.py` + `test_narzedzia.py` + `test_match.py` | 38 | 0 | 0 | (stdout) |
| `319f861`: pelny zestaw | - | - | - | **nie uruchomiony (PC niedostepny)**; oczekiwane 277 / 3 / 0 |

- +24 przypadki w `8ad7821`: `test_match` +5 (3 funkcje, dwie na obu ukladach plytek), `test_skala` 14, `test_ustawienia` +5;
  po nim `test_narzedzia` +1. Pominiete te same 3 testy co w punkcie odniesienia.
- Miedzy `8ad7821` a `319f861` zmienil sie z kodu programu tylko jeden warunek w `match.koryguj_skale` (pkt 3.0) -
  dotyczy prac o pokryciu < 0,6, ktorych w testach poza `test_skala` nie ma; pelnego przebiegu na `319f861` nie bylo.
- Pliki programu na PC = worktree: 81 z 81 (SHA-256, `skrypty\lista_sha.py`) przed startem pomiarow koncowych.

## 3. Pomiary

Zestawy odniesienia (PC, tylko odczyt): `syntetyczne_R59_P2` (24 skany) + `syntetyczne_R59_P3a` (16) = R59, 40 skanow,
397 prac; `syntetyczne_r54_P2` + `syntetyczne_r54_P3a` = r54, 40 skanow, 384 prace (to sa "zestawy dzisiejsze r54" z
raportu R59 pkt 6.1, nie zestawy z 2.11 - patrz odstepstwo 4). Pula: 17 projektow z `Prace_test`. Wspolczynnik puli =
wspolczynnik z prawdy (wieczorem 1,22, rano 1,0), a "blad wspolczynnika e" = pula liczona z 1,22 / (1 + e/100), czyli
praca jest o e % wieksza niz projekt x wspolczynnik puli. Wszystkie przebiegi wieloprocesowe (`--procesy 7`) - czasy
z nich sa zawyzone i porownywalne tylko w obrebie jednego przebiegu.

### 3.0 Ktory kod zmierzono

Pomiary nowego kodu zrobilem na `15820d5`. Pomiar R59 przy bledzie 0 pokazal 1 utracone top-1 przez korekte (praca
lezaca bokiem: wlasciwy projekt bez estymaty skali - za malo punktow poza pasem brzegu - a obcy projekt z drugiego
miejsca po korekcie 0,40 -> 0,46 wyprzedzil go; oba szare). Poprawka `319f861`: korekty nie stosuje sie, gdy pokrycie
po korekcie < `prog_ostrzezenia_pokrycie` (0,6). Zmienia to wynik wylacznie prac, ktore i tak sa szare; pomiar
koncowy na `319f861` przerwal brak PC - **skutek poprawki na zestawach jest niezweryfikowany** (sprawdza go tylko
test `test_ustawienia_steruja_korekta`).

### 3.1 P1 - filtr wymiarow

**(a) Pelny lancuch, R59, blad 0 - stary kod (`8b83da7`) vs nowy filtr (korekta wylaczona) vs nowy kod (korekta wlaczona):**

| Miara | stary kod | nowy, korekta wyl. (P1) | nowy, korekta wl. (P1 + P3, `15820d5`) |
|---|---|---|---|
| top-1 razem | 382 / 397 | **389 / 397** | 388 / 397 |
| top-2 razem | 384 / 397 | 390 / 397 | 390 / 397 |
| top-1 zestaw P2 | 240 / 240 | 240 / 240 | 240 / 240 |
| top-1 "dobrze" / "bokiem" / "czesciowo" / "drgniecie" | 276/276, 32/59, 35/37, 39/41 | 276/276, **39/59**, 35/37, 39/41 | 276/276, 38/59, 35/37, 39/41 |
| statusy match zielony / zolty / szary | 339 / 42 / 32 | 344 / 43 / 26 | 345 / 42 / 26 |
| gniazda zielone / czerwone / zolte / szare / pomaranczowe | 150 / 65 / 162 / 32 / 4 | 155 / 65 / 163 / 26 / 4 | 155 / 65 / 163 / 26 / 4 |
| ubytki wykryte dowolna / A / B / A+B / czerwone | 221 / 184 / 107 / 69 / 79 z 248 | 222 / 185 / 107 / 69 / 79 z 249 | 222 / 185 / 107 / 69 / 79 z 249 |
| prace cale z alarmem / z czerwonym | 0 / 0 z 127 | 0 / 0 z 127 | 0 / 0 z 127 |
| falszywe ubytki (czerwone) | 7 (2) | 7 (2) | 7 (2) |
| drgniecie wykryte / falszywe "skan ponownie" | 35 z 39 / 2 | 35 z 39 / 2 | 36 z 39 / 1 |

Ubytkow jest 249 zamiast 248, bo ubytki licza sie tylko na pracach z trafnym top-1, a P1 rozpoznaje 7 prac wiecej.
Utracone top-1 w kolumnie 3 = przypadek z pkt 3.0. Kryterium "top-1 / top-2 nie gorsze" na R59: spelnione dla P1
(389 >= 382, P2 240 / 240); dla P1 + P3 na `15820d5` 388 >= 382. **r54 na nowym kodzie nie zmierzone** (pkt 6) -
punkt odniesienia starego kodu na r54: top-1 375 / 384, top-2 376 / 384, P2 235 / 235 (raport R59: 376 / 384 - rozrzut
1 gniazda miedzy przebiegami).

**(b) Sam filtr w scenariuszach widocznosci** (`metryki_skala.py p1 --dopasuj`) - **tylko przebieg probny na 1 skanie**
(`skan_okragla_poranna_n9_s0200`, 12 prac: 10 "dobrze" + 2 z drgnieciem; kod filtra = `319f861`). Pelny przebieg na
`syntetyczne_R59_P2` + `_P3a` byl w kroku 6 - nie zrobiony.

| scenariusz (prace "dobrze") | wysokosc fragmentu / projektu (min-mediana) | wlasciwy odrzucony: stary / nowy | przechodzi filtr srednio (z 17): stary / nowy | top-1: stary / nowy | top-1 zielony: stary / nowy | czas match na prace [s]: stary / nowy |
|---|---|---|---|---|---|---|
| pelny (jak dane syntetyczne) | 0,99-1,03 | 0/10 / 0/10 | 2,0 / 2,3 | 10/10 / 10/10 | 10/10 / 10/10 | 0,72 / 0,88 |
| z gory (stozek 30 st., zaslania sama praca) | 0,83-0,93 | 0/10 / 0/10 | 1,8 / 2,5 | 10/10 / 10/10 | 10/10 / 10/10 | 0,54 / 0,85 |
| z gory + zaslania plytka | 0,82-0,93 | 0/10 / 0/10 | 1,8 / 2,5 | 10/10 / 10/10 | 10/10 / 10/10 | 0,56 / 0,86 |
| bez dolnych 1,5 mm (T10) | 0,81-0,88 | 1/10 / 0/10 | 1,8 / 2,8 | 10/10 / 10/10 | 10/10 / 10/10 | 1,45 / 1,14 |
| bez dolnych 3,0 mm | 0,61-0,71 | **10/10 / 0/10** | 0,8 / 2,8 | **4/10 / 10/10** | 4/10 / 10/10 | 3,14 / 0,93 |
| tylko nad plytka | 0,48-0,62 | **10/10 / 1/10** | 0,4 / 2,2 | **6/10 / 10/10** | 6/10 / 10/10 | 4,77 / 1,31 |

Prace z drgnieciem (2): bez dolnych 3,0 mm odrzucone 2/2 / 0/2, top-1 1/2 / 2/2; tylko nad plytka 2/2 / 1/2, top-1
1/2 / 2/2. Stary filtr po odrzuceniu wszystkich projektow wpada w "dopasuj wszystkie" (stad top-1 4-6 / 10 zamiast 0
i czas 3-5 s na prace); nowy przepuszcza wlasciwy projekt i 1-2 inne. Czas nowego filtra na pelnej pracy +0,16 s na
prace (wiecej kandydatow przechodzi), przy pracy niskiej szybciej (bez "dopasuj wszystkie"). Odtworzenie bledu testem:
`test_filtr_nie_odrzuca_pracy_ze_schowanym_dolem` (dolne 3 mm odciete: stara regula odrzuca, nowa daje wlasciwy
projekt na zielono, na obu ukladach plytek). Zrodla T7 / T10 (82-92 % wysokosci, 20/20) odtworzone w scenariuszach
"z gory" i "bez dolu"; w tym skanie "z gory" nie przekroczylo jeszcze starej tolerancji (T7: 3/20 skanow).

### 3.2 P3 - korekta skali

**(a) Blad estymaty skali** (poprawka ze skanu - blad prawdziwy, punkty proc.; prace z trafnym top-1; R59, kod
`15820d5`, estymata nie zalezy od poprawki `319f861`). Plytki wieczorne 20 skanow x 9 bledow; poranne tylko blad 0.

| blad e | prace "dobrze": w granicy 0,05 / max | estymaty wiarygodne (nie "niepewna"): w granicy 0,05 / p95 / max | estymaty "niepewne": w granicy / max |
|---|---|---|---|
| 0 (wieczorne) | 123 / 123, max 0,029 | 151 / 154, p95 0,029, max 0,170 | 2 / 14, max 0,35 |
| 0 (poranne) | 153 / 153, max 0,046 | 189 / 191, p95 0,034, max 0,221 | 4 / 27, max 2,35 |
| +0,1 / -0,1 | 123/123 (0,029) / 123/123 (0,031) | 151/154 / 151/153, p95 0,029 / 0,030 | 2/14 / 3/15 |
| +0,3 / -0,3 | 123/123 (0,029) / 123/123 (0,031) | 151/154 / 151/153, p95 0,029 / 0,029 | 2/14 / 3/15 |
| +0,5 / -0,5 | 123/123 (0,030) / 123/123 (0,030) | 151/153 / 151/153, p95 0,029 / 0,029 | 3/15 / 3/15 |
| +1,0 / -1,0 | 123/123 (0,029) / 123/123 (0,031) | 152/154 / 152/155, p95 0,028 / 0,031 | 3/15 / 2/14 |
| **razem e = -1 ... +1 %** | **1260 / 1260** (9 x 123 + 153 poranne) | **1550 / 1574** | 27 / 158 |

Srednia bledu w kazdym wierszu -0,0006 ... +0,0028. Poza granica 0,05 wsrod estymat wiarygodnych sa tylko prace
lezace bokiem i czesciowo zasloniete (max 0,22); estymaty "niepewne" to prace z drgnieciem (podwojna powierzchnia:
blad do +-0,35 %) - dla nich ostrzezenia nie ma (pkt 1.2). Obciazenie estymaty usuniete zmiana reszt (pkt 1.2; sonda
na 9 projektach, sigma 0,03 mm, cala powierzchnia: przed +0,005 ... +0,049 %, po -0,003 ... +0,011 %).

**(b) Strefa brzegu a estymata (zastrzezenie R2b)** - `metryki_skala.py brzeg`, 95 prac "dobrze" z 12 skanow
wieczornych `syntetyczne_R59_P2`, zmiana +-0,02 mm, kod `15820d5`. Zmiana estymaty wzgledem tej samej pracy bez zmian
[punkty proc.]; prog "bez zmiany" 0,02 = rozrzut estymaty na pracach "dobrze" (p95 bledu 0,022-0,030, tabela (a)).

| wariant | z wylaczeniem pasa brzegu (program): w progu / srednia / p95 / max | bez wylaczenia (pas 0 mm, kontrola): w progu / srednia / p95 / max |
|---|---|---|
| powtorka (inne ziarno RANSAC) | 95/95, +0,0000, 0,0000, 0,0004 | 95/95, +0,0000, 0,0000, 0,0004 |
| grubosc +0,02 w pasie A (0-0,3-0,5 mm) | 95/95, +0,0001, 0,0005, 0,0064 | 61/95, +0,0164, 0,0316, 0,0340 |
| grubosc -0,02, pas A | 95/95, -0,0001, 0,0004, 0,0104 | 68/95, -0,0147, 0,0281, 0,0299 |
| przesuniecie z +0,02, pas A | 95/95, +0,0000, 0,0004, 0,0023 | 90/95, +0,0091, 0,0198, 0,0224 |
| przesuniecie z -0,02, pas A | 95/95, -0,0001, 0,0005, 0,0104 | 94/95, -0,0061, 0,0146, 0,0201 |
| grubosc +0,02 w pasie C (0-1,4-2,0 mm, R2b wersja C) | 95/95, +0,0003, 0,0006, 0,0094 | **18/95**, +0,0677, 0,1366, 0,1426 |
| grubosc -0,02, pas C | 95/95, -0,0001, 0,0007, 0,0103 | **14/95**, -0,0655, 0,1333, 0,1415 |
| 3 ukruszenia fi 1,0 mm do 1 mm od brzegu | 95/95, -0,0001, 0,0004, 0,0098 | 95/95, +0,0012, 0,0057, 0,0085 |

Bez wylaczenia pasa zmiana strefy przy krawedzi przesuwa skale o 0,07-0,14 % (to jest efekt R2b w skali), z
wylaczeniem - ponizej szumu estymaty we wszystkich 665 porownaniach (7 wariantow x 95 prac; max 0,010, bo poza startowa z `dopasuj_pare`
liczona jest na wszystkich punktach i granica pasa przesuwa sie o ulamek woksela). Test: `test_strefa_brzegu_nie_wplywa_na_skale`
(grubszy / odgiety / ukruszony brzeg: estymator daje identyczna skale; bez wylaczenia pasa odgiety brzeg ja przesuwa).

**(c) Korekta nie "zjada" ukruszen** - te same skany R59, blad 0, korekta wylaczona vs wlaczona (`15820d5`):
wykrycia wieczorne 100 / 82 / 44 / 28 (dowolna / A / B / czerwone) z 113 w obu, poranne 122 / 103 / 63 / 51 z 136 w
obu (rano korekta tylko mierzona), prace cale z czerwonym 0 / 127 w obu, falszywe ubytki 7 (2 czerwone) w obu
(pkt 3.1 a). Roznice miedzy przebiegami w 3 z 397 prac (2 prace z drgnieciem / bokiem: "sprawdz" <-> "skan ponownie";
1 = pkt 3.0). Przy bledzie wspolczynnika z korekta: 98-103 / 113 wykrytych, prace cale z czerwonym 0 / 55 we wszystkich
16 grupach: 8 bledow x z korekta / bez (tabela d). Test: `test_korekta_nie_zjada_ukruszen` (ten sam skan z ubytkami: pula o dokladnym
wspolczynniku bez korekty vs pula z bledem 0,5 % + korekta - te same statusy i wykrycia).

**(d) Blad wspolczynnika: program bez korekty i z korekta** (R59, plytki wieczorne: 20 skanow, 174 prace, 113 ubytkow
wykrywalnych, 55 prac calych; kod `15820d5`):

| e % | korekta | top-1 | match ziel / zolty / szary | gniazda ziel / czerw / zolte / szare | ubytki wykryte dowolna / czerwone | prace cale: alarm / czerwone | "popraw ulozenie" / "skan ponownie" | czas match [s] (7 proc.) |
|---|---|---|---|---|---|---|---|---|
| 0 | nie | 171 | 153 / 17 / 11 | 63 / 25 / 78 / 11 | 100 / 28 z 113 | 0 / 0 z 55 | 1 / 15 | 26,1 |
| 0 | tak | 170 | 154 / 16 / 11 | 63 / 25 / 78 / 11 | 100 / 28 | 0 / 0 | 1 / 15 | 27,7 |
| +0,1 | nie / tak | 171 / 170 | 154/16/11 / 154/16/11 | 63/24/79/11 / 63/24/79/11 | 99/27 / 99/27 | 0/0 / 0/0 | 1/14 / 1/15 | 25,5 / 28,6 |
| -0,1 | nie / tak | 170 / 170 | 151/19/11 / 153/17/11 | 62/24/80/11 / 62/27/77/11 | 95/28 / 101/32 | 1/0 / 1/0 | 2/15 / 1/16 | 27,6 / 30,0 |
| +0,3 | nie / tak | 171 / 171 | 140/32/9 / 155/17/9 | 59/26/84/9 / 64/24/80/9 | 90/29 / 100/28 | 0/0 / 0/0 | 2/28 / 1/16 | 29,9 / 33,8 |
| -0,3 | nie / tak | 169 / 169 | 142/28/11 / 153/17/11 | 57/20/88/11 / 63/25/78/11 | 83/26 / 101/30 | 1/0 / 0/0 | 4/26 / 1/16 | 27,7 / 29,9 |
| +0,5 | nie / tak | 171 / 171 | **31/138/12** / 153/18/10 | 13/4/151/12 / 62/27/78/10 | **18/5** / 103/32 | 0/0 / 0/0 | **10/131** / 1/16 | 29,8 / 33,3 |
| -0,5 | nie / tak | 170 / 169 | **48/123/10** / 153/16/12 | 17/2/150/10 / 63/23/79/12 | **17/2** / 99/26 | 2/0 / 0/0 | **13/119** / 1/15 | 32,0 / 31,0 |
| +1,0 | nie / tak | 171 / 171 | **1/134/46** / 154/14/13 | 1/0/134/46 / 64/25/75/13 | **0/0 z 86** / 102/30 | 0/0 z 46 / 0/0 z 56 | **74/59** / 0/14 | 54,3 / 61,7 |
| -1,0 | nie / tak | 172 / 172 | **3/131/47** / 155/10/16 | 3/0/131/47 / 64/27/70/16 | **4/0 z 86** / 98/31 | 0/0 z 45 / 1/0 | **95/29** / 1/9 | 83,9 / 68,5 |

(Przy +-1 % bez korekty 46-47 prac jest szarych i w ogole nie trafia do inspect, stad mianownik 86 / 45-46.)

Co z tego wynika:
1. Bez korekty blad wspolczynnika psuje program tak, jak pokazaly T5 / T7, ale na tym kodzie objawia sie glownie
   statusem, nie falszywymi ubytkami: od +-0,3 % rosnie liczba zoltych (falszywe "skan ponownie" 26-28 zamiast 15,
   wykrycia 83-90 zamiast 100), od +-0,5 % program jest bezuzyteczny (zielonych 31-48 ze 174, "skan ponownie" 119-131,
   wykrycia 17-18 ze 113), przy +-1 % prawie wszystkie prace sa zolte "popraw ulozenie" albo szare.
2. Z korekta program przy kazdym bledzie -1 ... +1 % daje to samo co bez bledu: zielonych 153-155 (bez bledu 153-154),
   wykrycia 98-103 / 113 (100), czerwone 26-32 (28), prace cale z czerwonym 0 / 55 wszedzie, z alarmem 0-1 / 55 (0),
   falszywe ubytki 1-3, wszystkie bez czerwonego (bez bledu 2). Te odchylenia +-3 to zamiany "ubytek" <-> "sprawdz" na
   pracach, ktore maja ubytki (rozne pozy z ICP), i jedna praca lezaca bokiem ("ok" -> "sprawdz" przy -0,1 i -1,0 %).
3. Ostrzezenie (> 0,3 %): przy +-0,5 i +-1 % 153-155 prac (wszystkie z estymata wiarygodna), przy +0,3 % 100, przy
   -0,3 % 51 (blad na granicy progu - polowa estymat po kazdej stronie), przy +-0,1 i 0 - zadne.
4. Wyjatek na granicy okna (+-1 %): prace z drgnieciem maja estymate z bledem do +-0,35 %, wiec przy -1 % 7 z 16, a
   przy +1 % 2 z 16 wypadaja poza okno 1,05 % - korekty nie ma i praca jest szara zamiast zoltej "skan ponownie" (bez
   korekty przy tym bledzie te prace tez sa szare albo zolte). Stad "skan ponownie" 9 zamiast 15 przy -1 %.
5. Top-1 z korekta 169-172 vs bez 169-172: przy -0,5 % i +0,1 % po 1 mniej - to prace lezace bokiem / z drgnieciem o
   pokryciu < 0,6 (szare w obu wariantach). Czesc z nich to rozrzut RANSAC (Open3D nie jest deterministyczny miedzy
   przebiegami: ta sama praca ma przed korekta pokrycie 0,84 w jednym i 0,56 w drugim przebiegu), czesc to przypadek z
   pkt 3.0 usuniety w `319f861` - **liczby po poprawce niezweryfikowane**.

**(e) Rano.** Plytki poranne R59 (20 skanow, 223 prace), blad 0: korekta zastosowana 0 razy (wylacznie pomiar),
ostrzezen 0, estymat niepewnych 33 (drgniecie, bokiem), estymata prac "dobrze" 153 / 153 w granicy 0,05 (max 0,046);
wyniki programu identyczne z korekta i bez: top-1 218 / 223, gniazda ziel. / czerw. / zolte / szare 92 / 40 / 85 / 15,
wykrycia 122 / 136, prace cale z czerwonym 0 / 72, "skan ponownie" 22. Plytki poranne z
bledem +-0,5 % (czy pojawia sie ostrzezenie): **nie zmierzone** (krok 6); sprawdza to tylko test
`test_porownaj_pola_skali_i_tabela` (plytka `okragla_poranna`, praca +0,5 %: poprawka zmierzona, w nawiasie, z ostrzezeniem).

### 3.3 Czas

| Co | Wynik | Zrodlo |
|---|---|---|
| korekta skali na prace (estymata + ICP + ocena, `KorektaSkali.czas_s`), 1 proces | 0,06-0,14 s, 9-49 iteracji | sonda `sonda1.py`, 3 plytki wieczorne, 27 prac |
| match na plytke, R59 blad 0, 7 procesow: korekta wyl. -> wl. | wieczorne 26,1 -> 27,7 s (+6 %), poranne 40,8 -> 47,1 s (+15 %; rano korekta jest tylko liczona) | przebieg `program_R59_e0` |
| razem na plytke, j.w. | wieczorne 32,1 -> 33,0 s, poranne 46,7 -> 51,9 s | j.w. |
| filtr P1, czas match na prace | pelna praca 0,72 -> 0,88 s; praca niska 3,1-4,8 -> 0,9-1,3 s | przebieg probny `p1` (1 skan) |
| czas na plytke jednoprocesowo, stary kod / P1 / P1 + P3 | **nie zmierzone** (`skrypty\czasy.cmd`, krok 6) | - |

Przy +-1 % match trwa dwa razy dluzej z korekta i bez niej (54-84 s) - to koszt przegladu obrotow, gdy RANSAC nie daje
pokrycia 0,85, nie korekty. Czasy z przebiegow 7-procesowych sa zawyzone (PC wspoldzielony z 3 innymi agentami).

## 4. Odstepstwa od zlecenia

1. **Pomiary koncowe na `319f861` nie zrobione** (PC niedostepny po 3 probach). Liczby sa z `15820d5`; roznica dotyczy
   tylko prac nierozpoznanych (pkt 3.0). Brakuje: r54 na nowym kodzie, P1 w scenariuszach widocznosci na calym zestawie
   (jest 1 skan), plytki poranne z bledem, czas jednoprocesowy, pelny pytest na `319f861`.
2. Estymator to wariant C z T7 z trzema zmianami (pkt 1.2); zmiana reszt (mm skanu) nie byla w zleceniu - wynika z
   pomiaru obciazenia (pkt 3.2 a). Pas brzegu 2,0 mm zamiast 1,5 mm `[inspect]` - zeby objac strefe C z R2b.
3. Korekta nie jest stosowana takze przy pokryciu po korekcie < `prog_ostrzezenia_pokrycie` i przy spadku pokrycia
   (warunki dodatkowe wobec "okno +-1 %"); okno ma margines 0,05 punktu (dokladnosc estymaty), zeby wynik przy bledzie
   rownym granicy nie zalezal od szumu. Estymata "niepewna" nie daje ostrzezenia (zlecenie: "flaga ostrzezenia > 0,3 %").
4. Liczby odniesienia ze zlecenia dla r54 (411 / 420, 271 / 271) dotycza zestawow z 2.11 - ich nie ma w `dane_ref`.
   `dane_ref\syntetyczne_r54_*` to "zestawy dzisiejsze r54" z raportu R59 (384 prace; tam 376 / 384, P2 235 / 235;
   moj przebieg starego kodu 375 / 384).
5. "Odtworzenie T5 / T7 na obecnym kodzie" zrobione na zestawach odniesienia (szum generatora sigma 0,03 mm) z bledem
   wspolczynnika puli, nie generatorem T5 (szum skorelowany, wygladzenie, profil realistyczny) - tamte skrypty leza poza
   programem.
6. Nazwa raportu: w zleceniu byla nieczytelna (zamaskowana); uzylem `raporty/czesc_A_filtr_i_skala_2026-11-15.md`.
7. Commity `b5e1f48`, `8ad7821`, `15820d5` maja linie `Co-Authored-By: Claude Fable 5.2`, `319f861` - `Claude Opus 5.5`
   (zmiana polecona przez koordynatora po przerwie; historii nie przepisywalem).

## 5. Znane granice

- Dane wylacznie syntetyczne: skan z tej samej siatki co projekt. Deformacja ksztaltu 0,01-0,02 mm (frezowanie,
  spiekanie) jest dla estymaty nieodroznialna od skali (T7: blad 0,07-0,13 %) - tu nie mierzona.
- Jedna skala: anizotropia skurczu (inna skala w z) zostaje (T7: 0,3 % w z -> ok. 0,1 % bledu korekty).
- Pas brzegu liczony od plaszczyzny z = 0 projektu: przy mostach filary z brzegiem nizej nie sa wylaczone z estymaty
  (chronia je tylko wagi odporne i wylaczanie obszarow). Gdy `inspect` dostanie linie brzegu filarow (paczka P2), pas
  trzeba brac stamtad.
- Po korekcie odchylki `inspect` sa w skali projektu x wspolczynnik puli (progi w mm rozne od mm skanu o <= 1 %).
- Prace z drgnieciem: estymata do +-0,35 %, przy bledzie wspolczynnika ~1 % czesc wypada poza okno (pkt 3.2 d4).
- Filtr: praca widoczna w < 50 % wysokosci nadal odpada (ratunek "dopasuj wszystkie" zostaje); prace lezace bokiem
  filtr rozumie tylko tyle, ile daje porownanie z przycietym projektem (top-1 bokiem 39 / 59).
- Rozrzut Open3D RANSAC miedzy przebiegami: pojedyncze prace lezace bokiem zmieniaja status / top-1 miedzy przebiegami
  tego samego kodu (raport R59 tez to notuje); roznice rzedu 1 gniazda w tabelach nie sa skutkiem zmian.
- Ostrzezenie nie zmienia koloru gniazda (jest w polu `skala`, w `uwagi` i w tabeli); okno (`ui_test.py`) go nie pokazuje
  - poza zakresem (plik spoza listy).

## 6. Zadania dla czlowieka

1. [usunieto w kopii: opis dostepu ssh]
   porzadku). Po wlaczeniu koordynator moze powtorzyc krok 6 (polecenia w pkt 8).
2. **Po scaleniu i aktualizacji programu dopisac 5 wierszy `[match]` do lokalnego `ustawienia.toml`** (pulpit PC, laptop
   stanowiska) - wzor w `ustawienia.przyklad.toml`: `filtr_wysokosc_min_udzial`, `korekta_skali`,
   `korekta_skali_okno_proc`, `korekta_skali_ostrzezenie_proc`, `korekta_skali_pas_brzegu_mm`. Bez nich program konczy
   sie bledem `ustawienia.toml: [match] filtr_wysokosc_min_udzial: brak klucza`.
3. Na pierwszym prawdziwym skanie (P3b) zapisac dla 5-10 zielonych koron z co najmniej 3 krazkow pole `skala` z JSON
   (`poprawka_proc`, `niepewna`, `pokrycie_przed` / `pokrycie_po`) obok wspolczynnika z MillBox - rozrzut poprawki
   rozstrzygnie, czy prog 0,3 % i okno 1 % sa dobre (T7 pkt 7.1).

## 7. Do README

Proponowany tekst (README nie edytowalem):

> **Filtr wymiarow i korekta skali (czesc A, 15.11.2026).** `match` porownuje fragment skanu z projektem przycietym do
> wysokosci fragmentu: praca, ktorej dol jest schowany w gniezdzie albo niewidoczny z gory, nie gubi juz wlasciwego
> projektu (`[match] filtr_wysokosc_min_udzial` - najmniejsza widoczna czesc wysokosci, 0,5). Dla rozpoznanej pracy
> program wyznacza ze skanu poprawke skali wzgledem projektu x wspolczynnik (punkty blizej brzegu niz
> `korekta_skali_pas_brzegu_mm` nie biora udzialu, wiec ukruszenie brzegu skali nie zmienia) i - gdy miesci sie w
> oknie +-`korekta_skali_okno_proc` (1 %) - porownuje skan z projektem w skali skorygowanej. Poprawka ponad
> `korekta_skali_ostrzezenie_proc` (0,3 %) daje ostrzezenie "sprawdz wspolczynnik / krazek": w JSON wyniku pole
> `skala` kazdego gniazda (`poprawka_proc`, `zastosowana`, `powod`, `ostrzezenie`, `niepewna`,
> `wspolczynnik_ze_skanu`), w tabeli kolumna "skala %" ("(...)" = zmierzona, niezastosowana; "!" = ostrzezenie;
> "?" = estymata niepewna) i wiersz "OSTRZEZENIE SKALI". Na plytkach porannych (prace spieczone) poprawka jest tylko
> mierzona. Wylacznik: `[match] korekta_skali = false`. Liczby: `raporty/czesc_A_filtr_i_skala_2026-11-15.md`.
>
> **Aktualizacja istniejacej instalacji (od czesci A):** dopisac w lokalnym `ustawienia.toml`, sekcja `[match]`,
> 5 wierszy z `ustawienia.przyklad.toml` (`filtr_wysokosc_min_udzial`, `korekta_skali`, `korekta_skali_okno_proc`,
> `korekta_skali_ostrzezenie_proc`, `korekta_skali_pas_brzegu_mm`) - inaczej program zatrzyma sie na bledzie "brak klucza".
>
> **Do listy P3b ("Laptop firmowy" pkt 7):** pole `skala` z JSON (poprawka ze skanu, `niepewna`) dla zielonych koron
> obok wspolczynnika z raportu MillBox.

## 8. Gdzie leza dane i jak powtorzyc (PC, `<PC-katalog>\app\a\`)

- Program: `Ramki\stanowisko` (= worktree `319f861`), `run.cmd` (zlecenie), `run_baza.cmd` + `baza\` (kopia `8b83da7`
  do punktu odniesienia), lokalny `ustawienia.toml` = `..\ustawienia_wzor_pc.toml` + 5 kluczy (`skrypty\dopisz_ust.py`).
- Wyniki: `wyniki\baza\metryki_R59.json`, `metryki_r54.json` (stary kod); `wyniki\v1\program_R59_e0.json`,
  `brzeg_R59_P2.json`, `program_R59_wiecz_bledy.json` (kod `15820d5`); `wyniki\proba\` (przebiegi probne, m.in.
  `p1_proba.json`); `wyniki\v2\` (przerwany krok 6, nieodczytany). Logi: `logi\`. Skrypty robocze (poza repo):
  `skrypty\` (`v2a.cmd`, `v2b.cmd`, `czasy.cmd`, `porownanie_e0.py`, `roznice.py`, `vs_e0.py`, `zbiorczo.py`,
  `odstajace.py`, `sonda1.py`, `sonda2.py`, `lista_sha.py`). Duzych plikow nie tworzylem (tylko JSON / logi i 3 male
  atrapy STL w `wyniki\sonda2`); `Ramki\stanowisko\dane` nie powstal.
- Polecenia (z `Ramki\stanowisko` przez `run.cmd`; `D` = `<PC-katalog>\app\dane_ref`, `P` = `<PC-katalog>\app\Prace_test`):
```
run.cmd -m pytest testy -q -p no:cacheprovider
run_baza.cmd narzedzia\metryki_P3a.py --skany D\syntetyczne_R59_P2 D\syntetyczne_R59_P3a --projekty P --wyjscie <wyj> --nazwa metryki_R59.json --procesy 7
run_baza.cmd narzedzia\metryki_P3a.py --skany D\syntetyczne_r54_P2 D\syntetyczne_r54_P3a --projekty P --sufiks-ukladu _r54 --wyjscie <wyj> --nazwa metryki_r54.json --procesy 7
run.cmd narzedzia\metryki_skala.py program --skany D\syntetyczne_R59_P2 D\syntetyczne_R59_P3a --projekty P --wyjscie <wyj> --nazwa program_R59_e0.json --bledy 0 --procesy 7
run.cmd narzedzia\metryki_skala.py program --skany D\syntetyczne_R59_P2 D\syntetyczne_R59_P3a --projekty P --wyjscie <wyj> --nazwa program_R59_wiecz_bledy.json --wzorzec "skan_*wieczorna*" --bledy 0.1,-0.1,0.3,-0.3,0.5,-0.5,1,-1 --procesy 7
run.cmd narzedzia\metryki_skala.py brzeg --skany D\syntetyczne_R59_P2 --projekty P --wyjscie <wyj> --nazwa brzeg_R59_P2.json --procesy 7
run.cmd narzedzia\metryki_skala.py p1 --skany D\syntetyczne_R59_P2 --projekty P --wyjscie <wyj> --nazwa p1_R59_P2.json --dopasuj --progi-wysokosci 0 0.5 0.6 0.7 0.8 1.0 --procesy 7
run.cmd narzedzia\metryki_skala.py program --skany D\syntetyczne_r54_P2 D\syntetyczne_r54_P3a --projekty P --sufiks-ukladu _r54 --wyjscie <wyj> --nazwa program_r54_e0.json --bledy 0 --procesy 7
run.cmd narzedzia\metryki_skala.py program --skany D\syntetyczne_R59_P2 D\syntetyczne_R59_P3a --projekty P --wyjscie <wyj> --nazwa program_R59_rano_bledy.json --wzorzec "skan_*poranna*" --bledy 0.5,-0.5 --korekta tak --procesy 7
```
  Krok 6 w calosci: `skrypty\v2a.cmd 7`, potem `skrypty\v2b.cmd 7`, potem `skrypty\czasy.cmd` (jeden proces, stary kod /
  P1 / P1 + P3 na przemian). Porownanie: `skrypty\porownanie_e0.py <baza\metryki_R59.json> <v2\program_R59_e0.json>`.
  Uwaga: w przebiegu `brzeg` kroku 5 byly tylko skany wieczorne (`--wzorzec "skan_*wieczorna*"`), w kroku 6 caly P2.
