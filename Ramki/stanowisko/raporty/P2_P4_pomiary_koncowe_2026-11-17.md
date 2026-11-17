# P2 / P4 - pomiary koncowe na scalonym kodzie: trzy tryby pasa brzegu, K6, mapa seed 7001, czas inspect

Data: 2026-11-17. Sesja pomiarowa (dokonczenie "czesci B" przerwanej 16.11, raport `P2_P4_krawedz_brzegu_2026-11-16.md`).
Kod: galaz `przed-skanerem`, HEAD `fe66217` (scalony PR #13), wyslany `git archive` na PC do `<PC-katalog>\app\k2b`.
W trakcie sesji galaz przesunela sie do `7b56025` (dzien_skanera, testy, opisy); `git diff fe66217 7b56025` dla `inspect.py`,
`match.py`, `plate.py`, `porownaj.py`, `synth.py`, `krawedz.py`, `ustawienia.py`, `uklad.py`, `narzedzia/`, `modele_plytek/` jest
pusty - pomiar dotyczy takze `7b56025`.
[usunieto w kopii: opis dostepu ssh]
Wszystkie skany sa SZTUCZNE - to pomiar kodu, nie skanera. Projekty tylko jako skroty SHA (16 znakow). Kodu w repo nie zmieniano.

Tryby `[inspect] pas_brzegu_od`: `plaszczyzna` = stan sprzed P2; `linia` = sam pas od linii brzegu filaru; `linia_i_plaszczyzna`
= suma obu pasow, tryb DOMYSLNY (dalej "suma").

## 0. Stan: co zmierzone, co nie

| pomiar | stan | uwagi |
|---|---|---|
| trzy tryby na r54 (40 skanow) | **zmierzone w calosci** | 15:03-15:44, bez limitu watkow |
| trzy tryby na R59 (40 skanow) | **zmierzone w calosci** | polowa "poranne" przerwana zatrzymaniem PC ok. 16:00 po 17 z 20 skanow (wynik zapisywany na koncu, wiec przepadl) i policzona od nowa 16:09-16:16; 17 skanow wspolnych daje te same liczniki |
| zestaw K6: 40 plytek, 1030 ukruszen, trzy tryby | **zmierzone w calosci** | pierwsza proba (polowa "wieczorne", 8 z 20 skanow) przepadla przy zatrzymaniu PC; calosc policzona 16:17-16:29 z limitem watkow 2 |
| geometria K6 na 17 projektach (`metryki_krawedz.py k6`) | **zmierzone w calosci** (1632 ukruszenia, 16:32-17:01) | dwie proby ubite (zatrzymanie PC; przerwanie kolejki przy nowych limitach), trzecia w 1 procesie roboczym |
| mapa seed 7001 vs `t8_mapa_seed7001.json` | **zmierzone** (3 tryby) | przez `trzy.py`, nie przez `porownaj` + `mapa` (pkt 5) |
| czas inspect przed / po | **zmierzone porownawczo**, nie na wolnym PC | ten sam proces, te same fragmenty i limity watkow dla wszystkich trybow (pkt 6) |
| rozbicie r54 "linia" wg odleglosci od linii, powody "nie sprawdzono", filary mostow na pracach calych (braki raportu 16.11) | zmierzone | pkt 3.1, 3.5 |
| `metryki_krawedz.py analiza`, `przed_po` | nie uzyte | zastapione `trzy.py` + `podsum.py` (trzy tryby naraz, zgodnosc z `porownaj` scalonego kodu) - pkt 2 |
| pelny pytest | poza zakresem tej sesji | liczy inna sesja (`app\k2`) |

Nie zmierzone / niezweryfikowane: czas inspect na nieobciazonym PC; przyczyna 4 z 10 strat czerwonych (przyjeta przez analogie,
pkt 3.4); skad +2 prace "nie sprawdzono" w trybie `linia` wobec raportu 16.11 (41 zamiast 39); wplyw limitu watkow 2 na wynik
match (r54 / R59 liczone bez limitu, K6 i seed 7001 z limitem - porownania miedzy trybami sa zawsze w obrebie jednego przebiegu).

## 1. Wynik w skrocie

| | r54: plaszczyzna / linia / **suma** | R59: plaszczyzna / linia / **suma** |
|---|---|---|
| metryka "dobrze" (wykryte dowolna metoda) | 214 / 185 / **212** z 228 | 219 / 207 / **223** z 245 |
| wykryte razem / czerwone | 215 / 186 / **213** z 231; 88 / 76 / **87** | 222 / 210 / **226** z 249; 79 / 77 / **83** |
| wykryte krawedz | 94 / 93 / **93** z 102 | 106 / 109 / **109** z 121 |
| wykryte sciana | 121 / 93 / **120** z 129 | 116 / 101 / **117** z 128 |
| prace cale zielone | 132 / 91 / **113** z 136 | 123 / 86 / **114** z 127 |
| prace cale czerwone | 0 / 0 / **0** | 0 / 0 / **0** |
| prace cale "nie sprawdzono" (powod linia / dane) | 0 / 41 (26 / 19 z danymi) / **19 (0 / 19)** | 0 / 37 (31 / 9) / **9 (0 / 9)** |
| falszywe alarmy na pracach calych | 1 / 0 / **0** | 0 / 0 / **0** |
| falszywe miejsca / czerwone | 3 / 0; 0 / 0; **0 / 0** | 7 / 2; 8 / 2; **7 / 2** |

(W wierszu "nie sprawdzono" dla `linii`: liczba prac z powodem `linia` (takze `linia` + `dane`) / z powodem `dane` (takze oba).)

1. **Tryb domyslny (suma) odzyskuje zasieg stracony przez sama linie** (r54 sciana 93 -> 120 z 129, przy 121 w `plaszczyzna`) i
   zostawia "nie sprawdzono" tylko z powodu braku danych skanu: 19 / 136 (r54) i 9 / 127 (R59) prac calych, **0 z 221 prac calych
   dobrze ulozonych** - wszystkie 28 to prace polozone bokiem albo czesciowo zeskanowane (zestawy P3a).
2. **Czy tryb domyslny jest gdzies gorszy od `plaszczyzna`: tak, o pojedyncze sztuki, tylko w metodzie B.** r54: -2 wykrycia
   "dowolna metoda" (jedna praca, gniazdo zostaje zolte), czerwone 88 -> 87; R59: zadnej straty "dowolna metoda" (+4), czerwone
   79 -> 83. Lacznie 8 ubytkow czerwone -> zolte (11 odwrotnie). Przyczyny rozpoznane (pkt 3.4): inna losowa probka pasa metody B
   na progu szerokosci 0,2 mm (8 z 10) i wylaczenie metody B progiem `linia_min_udzial` na pracach bokiem (2 z 10). Prace cale
   czerwone 0, falszywe alarmy i falszywe miejsca nie wieksze niz w `plaszczyzna` w zadnym zestawie.
3. **K6 (40 plytek, 1030 ukruszen celowych):** suma wykrywa 773, `plaszczyzna` 668; strat wobec `plaszczyzna` 0. Najmniejszy
   rozmiar wykrywany pewnie (>= 95 %): srodek plaskiej krawedzi 0,15 mm, naroznik wewnetrzny 0,15 mm, naroznik zewnetrzny 0,20 mm,
   sciana 0,15 mm (w `plaszczyzna` sciana nigdy: 133 / 274). 0,10 mm: 17-67 %, 0,08 mm: 3-27 %. Wykrycia prawie wylacznie zolte;
   czerwone tylko przy 0,40 mm. 14 z 408 prac z ukruszeniami (wszystkie <= 0,15 mm) zostaje zielonych.
4. **Mapa seed 7001:** `plaszczyzna` 35 / 35 gniazd zgodnych z mapa t8; tryb domyslny 34 / 35 - jedno gniazdo zolte -> czerwone
   (prawdziwy ubytek, teraz A+B).
5. **Czas inspect na plytke:** ok. 1,6 s -> 2,6 s (x 1,5-1,6; +1 s przy match 13-57 s na plytke), mierzone na obciazonym PC.
6. PC byl przeciazony (ta sesja + dwie inne), ok. 16:00 wlasciciel go zatrzymal; szczegoly i moj udzial - pkt 7.

## 2. Jak liczono

- **Jeden przebieg na skan, trzy inspekcje.** `metryki_krawedz.py przed_po` umie dwa tryby i (w scalonym kodzie) nie przekazuje
  do `match.dopasuj` parametru `bez_korekty` na plytce porannej, ktory przekazuje `porownaj.dopasuj_fragmenty` (czesc A dodala
  korekte skali po napisaniu narzedzia). Dlatego uzyty zostal skrypt pomocniczy na PC `k2b\skrypty\trzy.py`: plate + match raz na
  skan dokladnie jak `porownaj.dopasuj_fragmenty` (z `bez_korekty`), potem `inspect.sprawdz` trzy razy na TYCH SAMYCH fragmentach
  i transformacjach - z trzema plikami ustawien rozniacymi sie tylko kluczem `pas_brzegu_od` (`k2b\ust\{plaszczyzna,linia,suma}.toml`
  = `ustawienia_wzor_pc.toml` + 1 wiersz; sprawdzone: jedyna roznica wobec ustawien domyslnych to ten klucz). Metryki: bez zmian
  `porownaj.metryki` i `porownaj.metryki_inspekcji` z pula (klasa krawedz / sciana dla starej prawdy z linii brzegu projektu).
  Roznice miedzy trybami wynikaja wiec tylko z inspect.
- Pamiec linii brzegu (`linie_cache`, 17 projektow) skopiowana z czesci B - `krawedz.py` jest bajtowo ten sam (`git diff czesc-b HEAD`
  pusty, takze `synth.py` i `metryki_krawedz.py`).
- Zestawienia: `k2b\skrypty\podsum.py` (liczniki, przejscia wobec `plaszczyzna` na ten sam fragment i ten sam ubytek prawdy),
  `diag.py` (przyczyna kazdego straconego wykrycia), `dbg_wciecia.py` (wciecia metody B jednego gniazda w trzech trybach),
  `gestosc_probki.py` (gestosc probki metody B na projekt), `mapa3.py` (mapa seed 7001 dla trzech trybow).
- **Powtarzalnosc:** partia R59 "poranne" zostala przerwana po 17 z 20 skanow i policzona od nowa (inna liczba procesow, inne
  obciazenie PC): liczniki wszystkich 17 skanow w trzech trybach (wykryte, czerwone, prace cale, alarm, nie sprawdzono, falszywe) sa
  w obu przebiegach identyczne. Tryb `plaszczyzna` na r54 odtwarza "przed" czesci B co do jednej liczby (215 / 231, krawedz 94 / 102,
  sciana 121 / 129, A / B / A+B / czerwone 184 / 109 / 78 / 88), tryb `linia` - "po" czesci B w wykryciach (186 / 231, 93 / 102,
  93 / 129, 161 / 92 / 67 / 76).
- Definicje jak w `porownaj.metryki_inspekcji`: praca cala = praca bez ubytku w prawdzie, trafny top-1, policzona inspekcja, bez
  drgniecia (wliczone prace bokiem i czesciowo zeskanowane z zestawow P3a oraz prace z poprawka reczna); falszywy alarm = praca
  cala ze statusem `ubytek` (czerwone) albo `sprawdz` (zolte); "nie sprawdzono" liczone osobno (zolte, nie alarm); falszywe miejsce =
  wykrycie dalej niz srednica / 2 + 1 mm od kazdego ubytku prawdy (na wszystkich pracach); metryka "dobrze" = wykrycie dowolna
  metoda w scenariuszu "dobrze" (praca dobrze ulozona, cala powierzchnia).

## 3. Trzy tryby `pas_brzegu_od` na zestawach r54 i R59

Skany: `dane_ref\syntetyczne_{r54,R59}_{P2,P3a}` (po 24 + 16 = 40 skanow na zestaw; r54 z `--sufiks-ukladu _r54`).

### 3.1 Zestaw r54 (40 skanow, 384 prace, top-1 377; 231 ubytkow wykrywalnych, 136 prac calych)

| miara | plaszczyzna (przed P2) | linia | suma (domyslny) |
|---|---|---|---|
| wykryte dowolna metoda | **215 / 231** | 186 / 231 | **213 / 231** |
| metryka "dobrze": wykryte dowolna metoda | 214 / 228 | 185 / 228 | 212 / 228 |
| "dobrze": czerwone | 87 | 76 | 87 |
| "bokiem": wykryte / ubytkow | 1 / 3 | 1 / 3 | 1 / 3 |
| krawedz: wykryte dowolna / czerwone (z 102) | 94 / 52 | 93 / 50 | 93 / 50 |
| sciana: wykryte dowolna / czerwone (z 129) | 121 / 36 | 93 / 26 | 120 / 37 |
| wykryte A / B / A+B / czerwone | 184 / 109 / 78 / 88 | 161 / 92 / 67 / 76 | 187 / 103 / 77 / 87 |
| prace cale: zielone | **132** | 91 | **113** |
| prace cale: czerwone | 0 | 0 | 0 |
| prace cale: falszywy alarm (zolte "sprawdz") | 1 | 0 | 0 |
| prace cale: "nie sprawdzono" | 0 | 41 (30 %) | **19 (14 %)** |
| - powod `linia` / `dane` / `linia` + `dane` | - | 22 / 15 / 4 | 0 / 19 / 0 |
| - wg scenariusza: dobrze (110) / bokiem (20) / czesciowo (6) | - | 20 / 15 / 6 | **0** / 13 / 6 |
| prace cale: pomaranczowe (poprawka) | 3 | 4 | 4 |
| prace cale z uwaga "linia projektu niepewna" (zielone, informacja) | - | - | 28 |
| "nie sprawdzono" - wszystkie prace (takze z ubytkami w prawdzie) | 0 | 83 | 47 (wszystkie `dane`) |
| falszywe miejsca / w tym czerwone | 3 / 0 | 0 / 0 | 0 / 0 |
| gniazda: zielone / czerwone / zolte / szare / pomaranczowe | 161 / 70 / 134 / 41 / 7 | 97 / 59 / 208 / 41 / 8 | 114 / 67 / 183 / 41 / 8 |

Przejscia wobec `plaszczyzna` (ten sam fragment, ten sam ubytek prawdy):

- **suma:** ubytki - stracone "dowolna metoda" 2 (krawedz 1, sciana 1; oba na jednej pracy), zyskane 0; czerwone: stracone 4
  (krawedz 3, sciana 1), zyskane 3 (krawedz 1, sciana 2). Prace cale: 19 x zielone -> "nie sprawdzono" (`dane`), 1 x zolte
  "sprawdz" -> pomaranczowe "poprawka" (znika jedyny falszywy alarm; 2 falszywe miejsca B na tej pracy znikaja).
  Kolor gniazd: zielone -> zolte 47, czerwone -> zolte 5, zolte -> czerwone 2, zolte -> pomaranczowe 1, reszta bez zmian.
- **linia:** ubytki - stracone "dowolna metoda" 29 (sciana 28), zyskane 0; czerwone: stracone 15, zyskane 3. Rozbicie 29 straconych
  wg odleglosci srodka ubytku od linii brzegu (niezweryfikowane w raporcie 16.11, teraz policzone): <= 1,5 mm - 3, 1,5-3 mm - 6,
  > 3 mm - 20; wg projektu: `1f4b07dd` 8, `2754d1d8` 8 (waxupy 3-czlonowe, linie filarow 2-10 mm ponizej najwyzszego punktu),
  `bc137fec` 3, `37aa171c` 2, `cf168832` 2, `6570c179` 2, po 1: `066fcc68`, `2e15189e`, `5a3a03dd`, `a4d10c94`. Prace cale:
  41 x zielone -> "nie sprawdzono" (czesc B podawala 39; +2 przy tym samym kodzie inspect - prawdopodobnie roznica w match / filtrze czesci A,
  nie badana dalej).

### 3.2 Zestaw R59 (40 skanow, 397 prac, top-1 388; 249 ubytkow wykrywalnych, 127 prac calych)

| miara | plaszczyzna (przed P2) | linia | suma (domyslny) |
|---|---|---|---|
| wykryte dowolna metoda | **222 / 249** | 210 / 249 | **226 / 249** |
| metryka "dobrze": wykryte dowolna metoda | 219 / 245 | 207 / 245 | 223 / 245 |
| "dobrze": czerwone | 78 | 76 | 83 |
| "bokiem" / "czesciowo": wykryte / ubytkow | 2 / 3, 1 / 1 | 2 / 3, 1 / 1 | 2 / 3, 1 / 1 |
| krawedz: wykryte dowolna / czerwone (z 121) | 106 / 43 | 109 / 46 | 109 / 45 |
| sciana: wykryte dowolna / czerwone (z 128) | 116 / 36 | 101 / 31 | 117 / 38 |
| wykryte A / B / A+B / czerwone | 185 / 107 / 69 / 79 | 175 / 105 / 69 / 77 | 189 / 110 / 72 / 83 |
| prace cale: zielone | **123** | 86 | **114** |
| prace cale: czerwone | 0 | 0 | 0 |
| prace cale: falszywy alarm (zolte "sprawdz") | 0 | 0 | 0 |
| prace cale: "nie sprawdzono" | 0 | 37 (29 %) | **9 (7 %)** |
| - powod `linia` / `dane` / `linia` + `dane` | - | 28 / 6 / 3 | 0 / 9 / 0 |
| - wg scenariusza: dobrze (111) / bokiem (10) / czesciowo (6) | - | 27 / 6 / 4 | **0** / 5 / 4 |
| prace cale: zolte "sprawdz ulozenie" / pomaranczowe | 1 / 3 | 1 / 3 | 1 / 3 |
| prace cale z uwaga "linia projektu niepewna" (zielone, informacja) | - | - | 32 |
| "nie sprawdzono" - wszystkie prace | 0 | 74 | 38 (wszystkie `dane`) |
| falszywe miejsca / w tym czerwone | 7 / 2 | 8 / 2 | 7 / 2 |
| gniazda: zielone / czerwone / zolte / szare / pomaranczowe | 155 / 65 / 163 / 26 / 4 | 90 / 62 / 230 / 26 / 5 | 116 / 66 / 201 / 26 / 4 |

Przejscia wobec `plaszczyzna`:

- **suma:** ubytki - stracone "dowolna metoda" 0, zyskane 4 (krawedz 3, sciana 1); czerwone: stracone 4 (krawedz 2, sciana 2),
  zyskane 8 (krawedz 4, sciana 4). Prace cale: 9 x zielone -> "nie sprawdzono" (`dane`). Falszywe miejsca: 7 -> 7 (w scenariuszu
  bokiem 5 -> 4, czesciowo 0 -> 1), czerwone 2 -> 2 (oba na pracach bokiem).
- **linia:** ubytki - stracone "dowolna metoda" 16 (wszystkie sciana), zyskane 4; czerwone: stracone 10, zyskane 8. Prace cale:
  37 x zielone -> "nie sprawdzono" (z tego `96087639` 14, `a4d10c94` 9, `cf168832` 4, `1f4b07dd` 3 - projekty z linia "czesciowa").
- Liczby `plaszczyzna` roznia sie od raportu R59 z 14.11 (221 / 248, top-1 382 / 397) - prawdopodobnie o prace odzyskane nowym filtrem czesci A
  (top-1 388 / 397; +1 ubytek wykrywalny i +1 wykryty); prace cale 127, 0 czerwonych, 0 alarmow, falszywe 7 / 2 - bez zmian.

### 3.3 Czy tryb domyslny jest gdziekolwiek gorszy od `plaszczyzna`

Tak, w kilku licznikach, ale o pojedyncze sztuki; lista pelna (oba zestawy, 80 skanow, 480 ubytkow wykrywalnych, 263 prace cale):

| licznik | r54: plaszczyzna -> suma | R59: plaszczyzna -> suma | ocena |
|---|---|---|---|
| wykryte dowolna metoda | 215 -> 213 (-2) | 222 -> 226 (+4) | r54 gorzej o 2 (jedna praca, gniazdo zostaje zolte) |
| metryka "dobrze" | 214 -> 212 z 228 | 219 -> 223 z 245 | jak wyzej |
| czerwone | 88 -> 87 (-4, +3) | 79 -> 83 (-4, +8) | 8 ubytkow czerwone -> zolte "sprawdz" (dalej wykryte), 11 odwrotnie |
| krawedz: dowolna / czerwone | 94 -> 93 / 52 -> 50 | 106 -> 109 / 43 -> 45 | r54 gorzej o 1 / 2 |
| sciana: dowolna / czerwone | 121 -> 120 / 36 -> 37 | 116 -> 117 / 36 -> 38 | r54 dowolna gorzej o 1 |
| prace cale czerwone | 0 -> 0 | 0 -> 0 | bez zmian |
| prace cale falszywy alarm | 1 -> 0 | 0 -> 0 | lepiej |
| falszywe miejsca / czerwone | 3 / 0 -> 0 / 0 | 7 / 2 -> 7 / 2 | lepiej / bez zmian |
| prace cale zielone | 132 -> 113 | 123 -> 114 | mniej o 28: wszystkie -> "nie sprawdzono" z powodu `dane` |
| prace cale "nie sprawdzono" | 0 -> 19 | 0 -> 9 | 28 z 263 (10,6 %); **0 z 221 prac dobrze ulozonych i calych** |

Wniosek liczbowy: wobec samej `linii` tryb sumy odzyskuje prawie caly zasieg (r54 sciana 93 -> 120 z 129; R59 sciana 101 -> 117
z 128) i usuwa "nie sprawdzono" z powodu linii (r54 41 -> 19, R59 37 -> 9; na pracach dobrze ulozonych 20 -> 0 i 27 -> 0). Wobec
`plaszczyzna` nie jest scislym nadzbiorem: suma strat 2 wykrycia "dowolna metoda" i 8 czerwonych (na 480 ubytkow), suma zyskow 4 i 11.

### 3.4 Skad straty trybu domyslnego wobec `plaszczyzna` (10 przypadkow: 6 sprawdzonych wprost, 4 przez analogie)

Wszystkie straty dotycza metody B (wciecie linii brzegu); metoda A w trybie sumy nie stracila zadnego ubytku (pas A w sumie jest
nadzbiorem: odleglosc = mniejsza z odleglosci od linii i od plaszczyzny).

1. **8 z 10 (2 "dowolna" + 6 czerwonych): to samo wciecie B jest w trybie sumy za waskie o wlos.** Probka pasa metody B w trybie
   sumy to inne losowe punkty niz w trybie `plaszczyzna` (najpierw probka pasa od linii z innego wycinka siatki, potem reszta pasa
   od plaszczyzny), przy tej samej gestosci (1111 pkt / mm2). Szerokosc wciecia jest liczona z rozrzutu 10-40 punktow probki i
   przy ubytkach o glebokosci 0,27-0,41 mm (prog wciecia 0,2) wypada raz nad, raz pod progiem `srednica_min_mm` = 0,2. Sprawdzone
   wprost na 3 gniazdach (`dbg_wciecia.py`, wszystkie rodzaje wciec w trzech trybach):

   | skan, gniazdo, projekt | wciecie w `plaszczyzna` | to samo wciecie w `suma` (i `linia`) | skutek |
   |---|---|---|---|
   | r54 `okragla_wieczorna_r54_n8_s0102`, gn 7, `6570c179` | szer. 0,289 mm, 23 pkt, gleb. 0,348 -> `wciecie` | szer. 0,165 mm, 10 pkt, gleb. 0,330 -> `za_male` | 2 ubytki prawdy traca jedyne wykrycie; gniazdo zolte "sprawdz" -> zolte "sprawdz ulozenie" |
   | R59 `okragla_wieczorna_n8_s0340`, gn 1, `ea47d2ad` | szer. 0,203 mm, 23 pkt, gleb. 0,261 -> `wciecie` | szer. 0,168 mm, 24 pkt, gleb. 0,261 -> `za_male` | A+B czerwone -> A zolte |
   | r54 `wieczorna_r54_n1_s0105`, gn 4, `3d091aaa` | szer. 0,259 mm, 40 pkt, gleb. 0,284 -> `wciecie` | szer. 0,185 mm, 29 pkt, gleb. 0,284 -> `za_male` | A+B czerwone -> A zolte |

   Pozostale 4 z tych 8 (r54 `okragla_poranna_r54_n9_s0204` gn 17 `ea47d2ad` x 2; R59 `okragla_poranna_n9_s0351` gn 5
   `5a3a03dd` x 2: wciecie bylo w `plaszczyzna`, w `suma` licznik `wciec` = 0, linia widoczna w obu trybach > 90 %) nie byly
   ogladane wprost - przyczyna przyjeta przez analogie (niezweryfikowane). To szum probkowania na progu, dziala w obie strony (zyski czerwonych w
   sumie: 11), nie jest to utrata zasiegu.
2. **2 z 10 (czerwone, obie prace BOKIEM, mosty / waxupy): metoda B wylaczona progiem `linia_min_udzial` = 0,9.** Probka sumy
   obejmuje tez gleboki brzeg filarow, ktorego na pracy lezacej bokiem skan nie widzi, wiec udzial "linii ciaglej" spada pod
   prog: r54 `poranna_r54_n5_s0330` gn 33 `cf168832` 0,906 -> 0,853; R59 `okragla_poranna_n9_s0311` gn 1 `bc137fec` 0,9035 ->
   0,8986. Wtedy wszystkie wciecia B staja sie "brak danych" (regula sprzed P2, plan 1a). Ubytek zostaje wykryty metoda A (zolte).
3. Spostrzezenie uboczne (`gestosc_probki.py`, 17 projektow): limit 300000 punktow probki pasa od linii jest osiagany przy
   wspolczynniku 1,22 na 3 projektach wieloczlonowych (`1f4b07dd`, `2754d1d8`, `cf168832`; pole wycinka 296-320 mm2) - gestosc
   probki B spada tam do 0,84-0,91 pelnej (939-1014 zamiast 1111 pkt / mm2). Przy 1,0 limit nie jest osiagany. W zadnym z 10
   straconych przypadkow gestosc nie byla obnizona (projekty tych przypadkow: `6570c179`, `ea47d2ad`, `3d091aaa`, `5a3a03dd`,
   `bc137fec` - pelna gestosc przy obu wspolczynnikach; `cf168832` - przypadek 2 na plytce porannej, x 1,0).

### 3.5 "Nie sprawdzono" w trybie domyslnym - ile zostaje i gdzie

- Prace cale: r54 19 / 136, R59 9 / 127; **wszystkie z powodu `dane`** (brak danych skanu przy linii brzegu), zadna z powodu linii
  projektu. Wg scenariusza generatora: prace dobrze ulozone z cala powierzchnia **0 / 110 i 0 / 111**; prace bokiem 13 / 20 i
  5 / 10; prace czesciowo zeskanowane 6 / 6 i 4 / 6. Czyli na danych sztucznych "nie sprawdzono" pojawia sie tylko tam, gdzie
  skan naprawde nie ma powierzchni przy brzegu.
- Wszystkie prace (takze z ubytkami): r54 47, R59 38 gniazd zielonych -> zoltych "nie sprawdzono"; zadne gniazdo czerwone ani
  zolte "sprawdz" nie zmienilo sie przez to na "nie sprawdzono" (ubytek ma pierwszenstwo).
- Niepewna linia projektu w trybie sumy nie daje "nie sprawdzono", tylko uwage w wyniku gniazda: 28 (r54) i 32 (R59) prac calych
  zielonych ma te uwage (tam dziala pas od plaszczyzny).
- Projekty prac calych "nie sprawdzono" (suma): r54 `066fcc68` 6, `1f4b07dd` 2, `91c1dea0` 2, `d8d245b4` 2, po 1: `2e15189e`,
  `37aa171c`, `3d091aaa`, `5a3a03dd`, `6570c179`, `a4d10c94`, `bc137fec`; R59 `066fcc68` 2, `2e15189e` 2, po 1: `1f4b07dd`,
  `91c1dea0`, `96087639`, `a4d10c94`, `d8d245b4` - rozklad po projektach wynika z tego, ktore prace generator polozyl bokiem /
  przyslonil, nie z projektu.
- Filary prac wieloczlonowych na pracach calych dobrze ulozonych (r54 + R59, 12 filarow 6 projektow, 48 par praca x filar):
  w trybie `linia` sprawdzone 22 / 48 - szesc filarow z linia "czesciowa" (`1f4b07dd` F1 F2, `2754d1d8` F1 F2, `37aa171c` F1,
  `cf168832` F2) nie jest sprawdzonych na zadnej pracy (mediana udzialu sprawdzonej linii 0,51-0,78 przy danych skanu na
  0,98-1,00 dlugosci); w trybie sumy sprawdzone **48 / 48** (mediana udzialu 0,98-1,00). 7 z tych 12 filarow lezy w calosci
  ponizej pasa sprzed P2 - w `plaszczyzna` ich brzeg nie byl kontrolowany wcale.
- Uwaga do P3b: na prawdziwym skanie dziur przy ostrej krawedzi bedzie wiecej niz w generatorze - udzial "nie sprawdzono" z
  powodu `dane` na pracach dobrze ulozonych (tu 0) trzeba zmierzyc na skanerze.

## 4. K6 - ukruszenia celowe

### 4.1 Zestaw K6 - wykrywalnosc po polozeniu x rozmiarze (40 plytek)

Generowanie wg pkt 8 raportu 16.11 (uklady R59, po 10 plytek: `wieczorna` seed 6000-6009 i `okragla_wieczorna` 6050-6059 x 1,22;
`poranna` 6100-6109 i `okragla_poranna` 6150-6159 x 1,0; `--ubytki 0-0 --krawedz 2-3 --krawedz-rozmiary
0.08,0.10,0.15,0.20,0.30,0.40 --krawedz-polozenie srodek,zewn,wewn,sciana --drgniecie 0 --poza-uklad --pole 100`): 40 skanow,
408 prac (wszystkie dobrze ulozone, top-1 408 / 408), **1030 ukruszen celowych**, niepostawionych 0. Rozmiar = promien kuli o
srodku na powierzchni. 169 ukruszen 0,08 ma srednice 0,16 < `srednica_min_mm` 0,2, wiec w prawdzie sa "niewykrywalne" - ponizej
liczone sa wszystkie ukruszenia celowe. Inspect w trzech trybach na tych samych dopasowaniach (`trzy.py`, limit watkow 2).

Wykryte dowolna metoda / wszystkie (w nawiasie czerwone, gdy sa); `linia` = `suma` w kazdej komorce tej tabeli:

| polozenie | rozmiar | gleb. rzecz. mediana [mm] | n | plaszczyzna | suma (domyslny) |
|---|---|---|---|---|---|
| srodek plaskiej krawedzi | 0,08 | 0,080 | 41 | 6 | 6 (15 %) |
| | 0,10 | 0,100 | 35 | 21 | 21 (60 %) |
| | 0,15 | 0,150 | 52 | 52 | **52 (100 %)** |
| | 0,20 | 0,200 | 40 | 39 | 40 (100 %) |
| | 0,30 | 0,290 | 37 | 37 | 37 (100 %) |
| | 0,40 | 0,335 | 44 | 43 (11 cz.) | 44 (100 %; 15 cz.) |
| naroznik wewnetrzny | 0,08 | 0,074 | 35 | 1 | 1 (3 %) |
| | 0,10 | 0,092 | 43 | 12 | 12 (28 %) |
| | 0,15 | 0,141 | 48 | 41 | **46 (96 %)** |
| | 0,20 | 0,184 | 41 | 41 | 41 (100 %) |
| | 0,30 | 0,244 | 41 | 40 | 41 (100 %) |
| | 0,40 | 0,296 | 52 | 50 (9 cz.) | 52 (100 %; 13 cz.) |
| naroznik zewnetrzny | 0,08 | 0,067 | 45 | 3 | 3 (7 %) |
| | 0,10 | 0,082 | 52 | 9 | 9 (17 %) |
| | 0,15 | 0,126 | 40 | 32 | 33 (83 %) |
| | 0,20 | 0,162 | 36 | 36 | **36 (100 %)** |
| | 0,30 | 0,229 | 38 | 36 | 38 (100 %) |
| | 0,40 | 0,288 | 36 | 36 (2 cz.) | 36 (100 %; 1 cz.) |
| sciana | 0,08 | 0,080 | 48 | 9 | 13 (27 %) |
| | 0,10 | 0,100 | 42 | 16 | 28 (67 %) |
| | 0,15 | 0,150 | 51 | 36 | **51 (100 %)** |
| | 0,20 | 0,200 | 41 | 27 | 41 (100 %) |
| | 0,30 | 0,300 | 40 | 18 | 40 (100 %) |
| | 0,40 | 0,400 | 52 | 27 | 52 (100 %; 1 cz.) |
| razem | wszystkie | | 1030 | **668 (22 cz.)** | **773 (30 cz.)** |
| razem bez 0,08 (wykrywalne wg prawdy) | | | 861 | 649 | 750 |

- **Najmniejszy rozmiar wykrywany pewnie w trybie domyslnym** (>= 95 % wykrytych dowolna metoda; dane sztuczne, szum sigma
  0,03 mm): srodek plaskiej krawedzi **0,15** (52 / 52), naroznik wewnetrzny **0,15** (46 / 48; 100 % od 0,20), naroznik
  zewnetrzny **0,20** (36 / 36; przy 0,15: 33 / 40), sciana **0,15** (51 / 51). Ponizej: 0,10 mm - 17-67 %, 0,08 mm - 3-27 %.
  Granica wynika z progu `prog_glebokosci_mm` = 0,08: na narozniku zewnetrznym ukruszenie 0,10 ma rzeczywista glebokosc 0,082 mm
  (mediana), 0,15 - 0,126 mm.
- W trybie `plaszczyzna`: krawedz jak wyzej z dokladnoscia do pojedynczych sztuk (srodek 0,15; wewn. 0,20 - przy 0,15 jest
  41 / 48; zewn. 0,20), ale sciana nigdy nie jest pewna (133 / 274: ukruszenia przy glebokim brzegu leza ponizej pasa 1,5 mm
  od najwyzszego punktu pracy).
- **suma wobec plaszczyzna:** zyskane wykrycia 105 (sciana 92, naroznik wewn. 8, zewn. 3, srodek 2), stracone **0**; czerwone:
  zyskane 12, stracone 4 (22 -> 30). Falszywe miejsca 0 w kazdym trybie (1030 ukruszen, 408 prac).
- Kolor: prawie wszystko zolte "sprawdz" (sama metoda A). Czerwone (A+B) tylko przy 0,40 mm: srodek 15 / 44, naroznik wewn.
  13 / 52, zewn. 1 / 36, sciana 1 / 52 - metoda B wymaga wciecia >= 0,2 mm glebokosci i >= 0,2 mm szerokosci.
- **Prace z ukruszeniami oznaczone ZIELONO** (zadne z 2-3 ukruszen pracy nie wykryte): plaszczyzna 35 / 408, linia 12,
  **suma 14 / 408**. Na tych 14 pracach leza 32 ukruszenia: 21 x 0,08, 9 x 0,10, 2 x 0,15 (zadnego >= 0,20).
- "Nie sprawdzono" na zestawie K6: plaszczyzna 0, linia 2 (powod `linia`), suma 0.
- Wg grupy pracy, ukruszenia >= 0,15 mm, wykryte dowolna metoda (plaszczyzna -> suma): korony 216 -> 271 z 273 (sciana 22 -> 73
  z 73); korony implantowe bez lacznika 286 -> 286 z 293 (naroznik zewn. 56 z 61, wewn. 82 z 84); pojedyncze inne (waxup
  jednoczlonowy) 60 -> 74 z 74; prace wieloczlonowe 29 -> 49 z 49 (mala proba: na plytkach wieczornych wiekszosc prac
  wieloczlonowych nie miesci sie w gniazdach - generator pomija 7-9 z 17 projektow na plytke).

### 4.2 Geometria ukruszen celowych na 17 projektach (`metryki_krawedz.py k6`)

17 projektow x 4 polozenia x 6 rozmiarow x 4 powtorzenia = **1632 ukruszenia, postawione 1632 / 1632** (68 / 68 w kazdej
komorce; projekt x 1,22; pomiar niezalezny od generatora - trimesh; 1 proces roboczy, 29 min). Glebokosc rzeczywista [mm]:

| rozmiar | srodek plaskiej krawedzi: p10 / mediana / p90 (med. / rozmiar) | naroznik zewnetrzny | naroznik wewnetrzny | sciana |
|---|---|---|---|---|
| 0,08 | 0,076 / 0,078 / 0,079 (0,97) | 0,048 / 0,062 / 0,070 (0,78) | 0,054 / 0,068 / 0,075 (0,85) | 0,075 / 0,078 / 0,080 (0,98) |
| 0,10 | 0,097 / 0,098 / 0,099 (0,98) | 0,062 / 0,078 / 0,091 (0,78) | 0,075 / 0,088 / 0,096 (0,88) | 0,095 / 0,098 / 0,100 (0,98) |
| 0,15 | 0,146 / 0,149 / 0,150 (0,99) | 0,101 / 0,119 / 0,138 (0,80) | 0,114 / 0,135 / 0,146 (0,90) | 0,147 / 0,148 / 0,150 (0,99) |
| 0,20 | 0,183 / 0,199 / 0,199 (0,99) | 0,136 / 0,162 / 0,186 (0,81) | 0,155 / 0,181 / 0,195 (0,91) | 0,197 / 0,199 / 0,200 (0,99) |
| 0,30 | 0,228 / 0,278 / 0,299 (0,93) | 0,200 / 0,235 / 0,285 (0,78) | 0,219 / 0,259 / 0,288 (0,86) | 0,298 / 0,299 / 0,300 (1,00) |
| 0,40 | 0,276 / 0,349 / 0,399 (0,87) | 0,252 / 0,313 / 0,370 (0,78) | 0,273 / 0,325 / 0,384 (0,81) | 0,387 / 0,399 / 0,400 (1,00) |

- Srodek kuli na powierzchni projektu: najwieksza odleglosc 0,000003 mm (1632 z 1632 ponizej 0,001). Glebokosc rzeczywista nigdy
  nie przekracza rozmiaru. Glebokosc z generatora (pole prawdy) wobec niezaleznego pomiaru: mediana roznicy 0,0025 mm, najwiecej
  0,022 mm (2 przypadki > 0,02, oba na `5a3a03dd`).
- Polozenie zapisane w prawdzie zgodne z zamowionym w 1632 / 1632 (po 408 na polozenie).
- Naroznik zewnetrzny traci najwiecej glebokosci (0,78-0,81 rozmiaru): ukruszenie 0,10 ma tam mediane 0,078 mm, czyli ponizej
  progu `prog_glebokosci_mm` = 0,08 - stad 17 % wykrytych w pkt 4.1; na srodku plaskiej krawedzi i na scianie glebokosc = rozmiar
  do 0,20 mm, przy 0,30-0,40 na srodku krawedzi spada do 0,87-0,93 (prawdopodobnie kula wieksza niz szerokosc plaskiej krawedzi - niezweryfikowane).
- Wg grupy pracy (mediana glebokosci przy rozmiarze 0,15 na narozniku zewnetrznym; n = korony 20, korony implantowe 20,
  pojedyncze inne 4, wieloczlonowe 24 na komorke): 0,120 / 0,106 / 0,111 / 0,124 mm; na narozniku wewnetrznym 0,134 / 0,130 /
  0,143 / 0,139; na srodku krawedzi i scianie bez roznic miedzy grupami (0,148-0,149).
- **Czasza w powietrzu > 10 % pola: 99 z 1632 - wszystkie na dwoch siatkach o niejednoznacznym znaku "wewnatrz"** opisanych w
  raporcie 16.11 (`a4d10c94` 50 z 96, `5a3a03dd` 49 z 96; naroznik wewnetrzny 48 z 48, srodek 32 z 48, zewnetrzny 16 z 48, sciana
  3 z 48). Poza nimi: 3 ukruszenia z czescia czaszy w powietrzu <= 10 % na dwoch siatkach nieszczelnych (`96087639` 2,
  `1f4b07dd` 1); na pozostalych 13 siatkach 0 z 1248. Kolumna "czasza w powietrzu (szczelne)" narzedzia (8 na komorke) to
  wlasnie te dwie siatki - sa `is_watertight`, ale nie sa poprawna bryla. Wniosek z 16.11 (sprawdzic te dwa pliki w exocad /
  MeshLab) pozostaje; wyniki K6 na tych dwoch projektach (takze wykrywalnosc w pkt 4.1) sa niepewne.

## 5. Mapa statusow gniazd, seed 7001

Skany: 4 plytki seed 7001 z `--wersja-ubytkow 1` (uklady `*_r54`, bajtowo rowne skanom sprzed P4 - raport 16.11 pkt 3.4),
skopiowane z `app\b\...\dane\s7001\v1`. Porownanie na gniazdo (projekt, status match, kolor gniazda) z
`Ramki/R59_odbior/baseline/t8_mapa_seed7001.json` - ta sama regula co `metryki_krawedz.py mapa`, policzona dla trzech trybow z
jednego przebiegu plate + match (`trzy.py` + `mapa3.py`):

| tryb | gniazd zgodnych z mapa t8 | roznice |
|---|---|---|
| plaszczyzna | **35 / 35** (4 z 4 plytek zgodne) | brak - scalony kod z `pas_brzegu_od = "plaszczyzna"` odtwarza mape t8 |
| suma (domyslny) | **34 / 35** | `poranna` n6, gniazdo 6, `6570c179`: zolte "sprawdz" -> **czerwone** |
| linia | 33 / 35 | to samo gniazdo 6 oraz `okragla_poranna` n9, gniazdo 33, `2754d1d8`: czerwone -> zolte "nie sprawdzono" (`linia`) |

- Jedyna zmiana w trybie domyslnym jest poprawna: w gniezdzie 6 jest prawdziwy ubytek sciany o srednicy 1,15 mm; w `plaszczyzna`
  wykrywa go sama metoda A (zolte), w sumie A+B (czerwone). Projekt i status match bez zmian we wszystkich 35 gniazdach.
- Statusy gniazd na 4 plytkach: t8 = plaszczyzna - zielone 8, czerwone 10, zolte 17; suma - zielone 8, czerwone 11, zolte 16.
  Zadne gniazdo nie zmienilo sie na "nie sprawdzono" w trybie domyslnym. Wykrycia na tych plytkach (36 ubytkow wykrywalnych):
  34 -> 34, czerwone 14 -> 15; prace cale 8, alarmow 0, falszywych miejsc 0 w obu trybach.
- Dla testu odbiorczego R59 (T8): przy domyslnych ustawieniach mapa rozni sie od `t8_mapa_seed7001.json` w 1 gniezdzie
  (zolte -> czerwone); bez roznic przy `--ustawienia` z `pas_brzegu_od = "plaszczyzna"`.
- Odstepstwo: przebieg przez `trzy.py` (bez `--numer`; numer plytki nie wplywa na gniazda), a nie przez 4 x `stanowisko.porownaj` +
  `metryki_krawedz.py mapa`; zgodnosc 35 / 35 w trybie `plaszczyzna` potwierdza, ze daje to te sama mape.

## 6. Czas inspect na plytke

Czas `inspect.sprawdz` zsumowany po gniazdach plytki, bez jednorazowego wyznaczania linii brzegu (`inspect_bez_linii`; linie byly
w pamieci na dysku: 0,0-0,6 s na caly zestaw). "Przed" = `plaszczyzna`, "po" = `suma`. Wszystkie tryby liczone w TYM SAMYM
procesie, na tych samych fragmentach, jeden po drugim - czyli przy tym samym obciazeniu PC i tych samych limitach watkow dla
"przed" i "po". Wartosci bezwzgledne sa zawyzone obciazeniem PC (ani jednego pomiaru na wolnym komputerze); porownywalny jest stosunek.

| zestaw (plytek) | warunki | plaszczyzna: mediana na plytke / suma [s] | linia | suma (domyslny) | suma / plaszczyzna (z sum) |
|---|---|---|---|---|---|
| r54 (40) | 2 procesy sesji, PC 100 % CPU i 1-3 GB wolnego RAM (inne sesje), bez limitu watkow, kolejnosc trybow stala | 1,59 / 67,4 | 2,67 / 109,8 | 2,62 / 107,7 | 1,60 |
| R59 (40) | polowa jak r54, polowa po restarcie PC (4 procesy), bez limitu watkow, kolejnosc stala | 1,57 / 63,0 | 2,42 / 106,2 | 2,38 / 92,1 | 1,46 |
| K6 (40) | 2 procesy robocze, limit watkow 2 (`OMP` / `OPENBLAS` / `MKL`), inna sesja liczy rownolegle, kolejnosc stala | 1,61 / 64,6 | 2,71 / 112,7 | 2,61 / 103,6 | 1,60 |
| seed 7001 (4) | 1 proces, limit watkow 2, kolejnosc trybow ROTOWANA co fragment, inna sesja liczy rownolegle | 1,29 / 5,05 | 2,66 / 11,02 | 2,70 / 10,73 | 2,1 |

- **Inspect na plytke: ok. 1,6 s -> ok. 2,6 s (+1,0 s, x 1,5-1,6)** na zestawach po 40 plytek. Probka metody B w trybie sumy jest
  1-9 razy wieksza niz w `plaszczyzna` (pas od linii obejmuje caly gleboki brzeg, np. `96087639` 15 tys. -> 142 tys. punktow,
  `gestosc_probki.py`) i dochodzi ocena brzegu filarow.
- Na 4 plytkach seed 7001 stosunek jest wiekszy (2,1). Prawdopodobna przyczyna (niezweryfikowane): kazdy projekt pojawia sie
  tam raz-dwa razy w swojej puli (osobna pula dla x 1,22 i x 1,0), wiec wazy jednorazowe przygotowanie probki pasa projektu,
  ktore w dluzszych przebiegach rozklada sie na wiele plytek. To jedyny pomiar z rotowana kolejnoscia - w pozostalych
  `plaszczyzna` byla zawsze pierwsza.
- Dla skali: match na plytke w tych samych przebiegach - mediana 13-17 s (seed 7001), 21 s (K6), 57 s (r54 na przeciazonym PC).
- Nie zmierzone: czas na wolnym PC w 1 procesie (PC caly czas wspoldzielony), czas z zimna pamiecia linii (3-9 s raz na projekt
  w procesie - raport 16.11).

## 7. Odstepstwa od zlecenia i zdarzenia

1. **Narzedzie:** trzy tryby liczone skryptem pomocniczym `trzy.py` (na PC, poza repo), nie `metryki_krawedz.py przed_po` -
   powody w pkt 2. Do zgloszenia koordynatorowi: `metryki_krawedz.py przed_po` w scalonym kodzie wola `match.dopasuj` bez
   `bez_korekty`, czyli na plytkach porannych stosuje korekte skali, ktorej `porownaj` nie stosuje (narzedzie sprzed czesci A).
2. **Zatrzymanie PC ok. 16:00 (wlasciciel: 0,4 GB wolnego RAM, CPU 88 C); system wstal 16:02:47.** Na koncie `<konto-PC>`
   liczyly naraz trzy sesje. Stan tej sesji tuz przed zatrzymaniem: 2 procesy `trzy.py` (R59 "poranne", K6 "wieczorne") oraz -
   **moj blad** - uruchomiony o 15:56:30 pomiar geometrii k6 (3 procesy python) poza wlasna bramka pamieci, przy 2,9 GB wolnego
   RAM; o 15:57:14 odczyt pokazal 0,2 GB wolnego RAM i 0,2 GB wolnego przydzialu pamieci, przy ok. 27 procesach python innych
   sesji. Wczesniej (15:09-15:11) moja pierwsza kolejka zadan z za luznym progiem (start przy >= 3 GB) uruchomila 7 procesow
   naraz; zatrzymalem ja po 2 minutach i zastapilem ostrzejsza (2 procesy pewne, kolejne od 7 GB RAM i 11 GB przydzialu).
   Pojedynczy proces `trzy.py` bierze 1,3 GB na starcie i do 3,6-4,2 GB szczytu pamieci roboczej po kilkunastu skanach
   (przydzial 2,7-5 GB) - tego na poczatku nie wiedzialem.
   Stracone i powtorzone: R59 "poranne" (20 skanow), K6 (caly zestaw), geometria k6. Wyniki zapisane przed 15:45 (r54 caly, R59
   "wieczorne") sa kompletne - sprawdzone po restarcie (pliki JSON z 15:19, 15:29, 15:43; po 20 skanow kazdy).
3. **Nowe limity koordynatora** (16:16: najwyzej 3 procesy python, `OMP_NUM_THREADS` / `OPENBLAS_NUM_THREADS` /
   `MKL_NUM_THREADS` = 2 w `run.cmd`, start partii od 8 GB wolnego RAM; 16:21: najwyzej 2 procesy, start od 10 GB, zadnych
   samostartujacych lancuchow). Zastosowane od 16:17: kolejka zatrzymana, dalej pojedyncze polecenia po sprawdzeniu RAM
   (16 GB przed K6, 15 GB przed seed 7001, 10 GB przed geometria k6). Partia R59 "poranne" (16:09-16:16) szla jeszcze w 4
   procesach roboczych bez limitu watkow; partia K6 (start 16:17) w 2 procesach roboczych + proces nadrzedny = 3 procesy
   python - dokonczona po zaostrzeniu limitu do 2; seed 7001 w 1 procesie, geometria k6 w 1 procesie roboczym + nadrzedny.
   Zestawienia JSON-ow (zliczanie, bez plate / match / inspect) robione od 16:17 na MSI, zeby nie dokladac procesow na PC.
4. **Rozne warunki przebiegow:** r54 i R59 bez limitu watkow, K6 i seed 7001 z limitem 2 - nie mieszam ich w jednej tabeli;
   kazde porownanie trybow jest w obrebie jednego przebiegu (ten sam match). Wplywu limitu watkow na match nie mierzylem.
5. **Mapa seed 7001** przez `trzy.py` + `mapa3.py` zamiast `porownaj` + `metryki_krawedz.py mapa` (pkt 5) - jeden przebieg na
   trzy tryby zamiast osmiu przebiegow `porownaj`.
6. **Czas inspect** nie byl mierzony "na koncu na wolnym PC": PC byl wspoldzielony przez caly czas; podaje stosunek w tym samym
   procesie (pkt 6).
7. Budzet czasu: ok. 135 min (14:49-17:05 czasu PC) zamiast 90-120 min (przeciazony PC, zatrzymanie, powtorki, limity).
8. Pliki z nazwami plikow projektow (`mapa_projektow.json` generatora; kierowane opcja `--mapa` do `k2b\dane\mapy\`) usuniete
   dwa razy: po przerwanej probie generowania i po generowaniu K6 (16:09); w `k2b` nie ma zadnego `mapa_projektow.json`
   (sprawdzone `dir /s`). Cudzych katalogow (`app\b`, `app\k2`, `app\k2a`, `dane_ref`, `Prace_test`) nie zmienialem.

## 8. Gdzie leza dane na PC i jak powtorzyc

PC, `<PC-katalog>\app\k2b\` (wszystko utworzone przez te sesje):

- `Ramki\` - kod `fe66217` (`git archive HEAD Ramki/stanowisko Ramki/parametry.json Ramki/R59_odbior/baseline/t8_mapa_seed7001.json`);
  `Ramki\stanowisko\ustawienia.toml` = `ustawienia_wzor_pc.toml` (nowe klucze z wartosci domyslnych kodu).
- `run.cmd` - Python 3.12 pulpitu, `PYTHONPATH`, od 16:17 z limitem watkow 2.
- `ust\plaszczyzna.toml`, `ust\linia.toml`, `ust\suma.toml` - wzor PC + `pas_brzegu_od`.
- `skrypty\` - `trzy.py` (pomiar), `podsum.py`, `wyciag.py`, `diag.py`, `dbg_wciecia.py`, `gestosc_probki.py`, `mapa3.py`
  (zestawienia), `ust.py`, `stan.py`, `kolejka.py`, `drzewo.py` (pomocnicze; `kolejka.py` nie uzywac - samostartujacy lancuch).
- `dane\tryby\` - wyniki: `{r54w,r54p,R59w,R59p,K6,s7001}_{plaszczyzna,linia,suma}.json` (format `metryki_P3a` / `przed_po`;
  `w` = plytki wieczorne i okragle wieczorne, `p` = poranne), `podsum.json` (zestawienie r54, R59, K6).
- `dane\syntetyczne_K6\` - 40 skanow K6 z prawda (ok. 2,4 GB STL - do usuniecia, gdy niepotrzebne); `dane\s7001\v1\` - 4 skany
  seed 7001 (kopia z `app\b`, 0,2 GB); `dane\linie_cache\` (kopia z `app\b`), `dane\krawedz\linie.json` (kopia),
  `dane\krawedz\k6_geometria.json` (pkt 4.2), `dane\proba\` (proby 2-skanowe).
- `logi\` - logi przebiegow (`r54w.log`, `r54p.log`, `R59w.log`, `R59p.out`, `K6.log`, `s7001.log`, `k6geo.log`,
  `dbg_wciecia.log`, `gestosc_probki.log`, `kolejka_*.log`; `R59p.log` = przebieg przerwany zatrzymaniem PC, 17 skanow).
- Kopia JSON-ow wynikow i zestawien na MSI jest tylko w katalogu tymczasowym sesji (nie w repo).

Polecenia (cmd na PC; `K` = `<PC-katalog>\app\k2b`, `P` = `<PC-katalog>\app\Prace_test`, `D` = `<PC-katalog>\app\dane_ref`,
`W` = `plaszczyzna=K\ust\plaszczyzna.toml linia=K\ust\linia.toml suma=K\ust\suma.toml`; jedno polecenie naraz, przed startem
>= 10 GB wolnego RAM):

```
K\run.cmd K\skrypty\ust.py
K\run.cmd K\skrypty\trzy.py --skany D\syntetyczne_r54_P2 D\syntetyczne_r54_P3a --projekty P --sufiks-ukladu _r54 --warianty W --pamiec-linii K\dane\linie_cache --wyjscie K\dane\tryby --nazwa r54 --procesy 1
K\run.cmd K\skrypty\trzy.py --skany D\syntetyczne_R59_P2 D\syntetyczne_R59_P3a --projekty P --warianty W --pamiec-linii K\dane\linie_cache --wyjscie K\dane\tryby --nazwa R59 --procesy 1
K\run.cmd -m stanowisko.synth --projekty P --plytka <wieczorna|poranna|okragla_wieczorna|okragla_poranna> --ile 10 --seed <6000|6100|6050|6150> --wspolczynnik <1.22|1.0> --drgniecie 0 --poza-uklad --pole 100 --ubytki 0-0 --krawedz 2-3 --krawedz-rozmiary 0.08,0.10,0.15,0.20,0.30,0.40 --krawedz-polozenie srodek,zewn,wewn,sciana --pamiec-linii K\dane\linie_cache --mapa K\dane\mapy\mapa_<plytka>.json --wyjscie K\dane\syntetyczne_K6
del /q K\dane\mapy\*.json
K\run.cmd K\skrypty\trzy.py --skany K\dane\syntetyczne_K6 --projekty P --warianty W --pamiec-linii K\dane\linie_cache --wyjscie K\dane\tryby --nazwa K6 --procesy 1
K\run.cmd K\skrypty\trzy.py --skany K\dane\s7001\v1 --projekty P --sufiks-ukladu _r54 --warianty W --pamiec-linii K\dane\linie_cache --wyjscie K\dane\tryby --nazwa s7001 --procesy 1 --rotacja
K\run.cmd narzedzia\metryki_krawedz.py k6 --projekty P --linie K\dane\krawedz\linie.json --powtorzen 4 --procesy 1 --wyjscie K\dane\krawedz
K\run.cmd K\skrypty\podsum.py --katalog K\dane\tryby --zestaw r54=r54w,r54p --zestaw R59=R59w,R59p --zestaw K6=K6 --wyjscie K\dane\tryby\podsum.json
K\run.cmd K\skrypty\wyciag.py K\dane\tryby\podsum.json
K\run.cmd K\skrypty\diag.py --katalog K\dane\tryby --czesci r54w,r54p --baza plaszczyzna --wariant suma --skany D\syntetyczne_r54_P2 D\syntetyczne_r54_P3a
K\run.cmd K\skrypty\dbg_wciecia.py D\syntetyczne_r54_P2\skan_okragla_wieczorna_r54_n8_s0102.stl 7 _r54
K\run.cmd K\skrypty\gestosc_probki.py
K\run.cmd K\skrypty\mapa3.py K\dane\tryby s7001 K\Ramki\R59_odbior\baseline\t8_mapa_seed7001.json
```

W tej sesji r54 i R59 byly liczone w dwoch czesciach na zestaw (`--wzorzec skan_*wieczorna_*.stl` -> `r54w` / `R59w`,
`--wzorzec skan_*poranna_*.stl` -> `r54p` / `R59p`), stad nazwy plikow; `--procesy N` uruchamia N procesow roboczych + proces
nadrzedny (kazdy roboczy do ok. 4 GB RAM).

## 9. Do decyzji / do przekazania (nic nie zmienialem)

1. Tryb domyslny wobec `plaszczyzna`: straty to pojedyncze wykrycia metody B na progu szerokosci wciecia (pkt 3.4.1) - wynik
   metody B zalezy od losowej probki pasa. Do rozwazenia przy P3b: wspolna probka dla czesci pasa pokrywajacej sie w obu trybach
   albo margines na progu `srednica_min_mm`; na danych sztucznych bilans wykryc "dowolna metoda" to r54 -2, R59 +4, K6 +105.
2. Prog `linia_min_udzial` = 0,9 jest liczony na calej probce sumy (z glebokim brzegiem) - na pracach bokiem wylacza metode B
   czesciej niz przed P2 (2 rozpoznane przypadki na 135 prac bokiem w r54 + R59). Czy liczyc go osobno dla czesci "plaszczyzna" -
   decyzja po danych ze skanera.
3. Limit 300000 punktow probki pasa od linii obniza gestosc metody B o 9-16 % na 3 projektach wieloczlonowych przy x 1,22.
4. `metryki_krawedz.py przed_po` nie przekazuje `bez_korekty` na plytkach porannych (pkt 7.1) - do poprawy przed kolejnym uzyciem.
5. Test T8 (mapa seed 7001): przy domyslnych ustawieniach 1 gniazdo rozni sie od `t8_mapa_seed7001.json` (zolte -> czerwone,
   poprawnie) - przyjac nowa mape albo liczyc T8 z `pas_brzegu_od = "plaszczyzna"`.
6. Ukruszenia K6 <= 0,10 mm sa wykrywane w 3-67 %, a 14 z 408 prac z ukruszeniami (wszystkie <= 0,15 mm) zostaje zielonych -
   granica obecnych progow (`prog_glebokosci_mm` 0,08, `srednica_min_mm` 0,2), nie skutek P2.
7. PC: jeden proces pomiarowy bierze do 4 GB RAM; trzy sesje liczace naraz bez wspolnego limitu skonczyly sie zatrzymaniem PC.
   Skany K6 (2,4 GB, `k2b\dane\syntetyczne_K6`) mozna usunac, gdy nie beda potrzebne do powtorki.
