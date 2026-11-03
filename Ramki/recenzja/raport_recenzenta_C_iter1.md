# Raport recenzenta — etap C, iteracja 1 (końcowa weryfikacja G4)

Plik: `recenzja/raport_recenzenta_C_iter1.md`. Pomiary własnymi skryptami na KOŃCOWYM zestawie plików w `wyniki_v2/` (SHA z raportu C):
- `recenzja/sprawdz_A.py -- --iter C1 --bez-pokrywki` → `wyniki_A_iterC1.json` (płytki: K‑01…K‑16, K‑58; 125 sprawdzeń, 1907 sond),
- `recenzja/sprawdz_B.py -- --iter C1` → `wyniki_B_iterC1.json` (pokrywka, wkładka, blat, korpusy, `.blend`: K‑01…K‑04b, K‑17…K‑47, K‑49, K‑53–K‑56; 73 sprawdzenia, 529 sond, 43 pary K‑53),
- `recenzja/sprawdz_C.py -- --iter 1` → `wyniki_C_iter1.json` (tulejka, 3 podkładki: K‑01…K‑04b, K‑52b, K‑52c; K‑57; K‑60; 27 sprawdzeń),
- `recenzja/sprawdz_K59.py` → `wyniki_C_iter1_K59.json` (powtarzalność), `recenzja/sprawdz_B_kanaly.py` (kanały Halla),
- logi `recenzja/log_{A,B}_iterC1.txt`, `log_C_iter1.txt`; rzuty `recenzja/relief_*.png`, `spod_wkladki_kanaly.png`; czysty przebieg w `recenzja/powtorka/`.

## 0. Werdykt
**ETAP C: ZALICZONY** — B = 0, P = 0, D = 0. Pełna powtórka K‑01…K‑56 na końcowym zestawie + K‑52b, K‑52c, K‑57, K‑59, K‑60: 225 sprawdzeń, 0 NIE; 2469 sond, 0 niestabilnych. Uchylone (R50/Z28): K‑19, K‑21, K‑26, K‑41, K‑48, K‑50–K‑52 — N/D zgodnie z protokołem. Zestaw 17 STL gotowy do wyceny (G4).

## 1. Niezależność pomiaru
- SHA‑256 zgodne z raportem wykonawcy (sekcja 2): **TAK** — 17/17 STL, `ramka_v2.blend`, 2 JSON, 4 arkusze, 3 rendery, README, do_v3: 29/29. Rozmiary zgodne.
- Skrypty recenzenta napisane bez czytania `ramka_generator.py`: **TAK** (przed K‑59 sprawdziłem tylko, że skrypt używa ścieżek względnych do `__file__` — bezpieczeństwo czystej kopii; implementacji nie czytałem).
- **Powtarzalność (K‑59)**: czysty przebieg w `recenzja/powtorka/` (kopia `ramka_generator.py`, `parametry.json`, `plan_ramki_v2.md`, `protokol_weryfikacji_v2.md`, `wyniki_v2/json/`; bez pozostałych plików `wyniki_v2/`), polecenie z README (`--etap ALL --iter 1`), 32 s, log `[ramka] RAPORT … B=0 P=0 D=0`: powstało 17/17 STL + JSON, arkusze, `.blend`, rendery, README, do_v3. STL identyczne bajt w bajt: **16/17**; `ramka_wkladka_v2.stl`: SHA ≠, ale **wierzchołki i trójkąty identyczne po kanonicznym sortowaniu (1806/1806, 0 różnych trójkątów)**, objętość 12,4057/12,4057, gabaryt identyczny — ZAL wg decyzji nadzoru (odstępstwo #7). Pozostałe: 2 JSON, CSV, 3 arkusze .md, do_v3 — bajtowo identyczne; `.blend` i 3 PNG — SHA ≠ (szum renderu/metadane, rozmiar PNG +18 B), README — różni się tylko zdaniem „Ostatni przebieg: etap ALL” i SHA renderów. Różnice objętości: 0,000 cm³.
- Metoda sond jak w etapach A/B; najmniejsza odległość od ściany 0,10 (sondy protokołu K‑15, K‑23, K‑34), stabilne.

## 2. Wyniki sprawdzeń (końcowy zestaw)
| Id | Wynik | Zmierzone przez recenzenta | Zadeklarowane przez wykonawcę | Oczekiwane | Waga | Uwaga |
|---|---|---|---|---|---|---|
| K‑01 | ZAL | 17 STL: trójkąty płytki 21992…26272, pokrywka 820, wkładka 1806, blat 5716, korpus W 18220 / P 17324, tulejka 1776, podkładki 3 × 630; NaN brak | identycznie | > 100 | B | |
| K‑02 | ZAL | płytki 96 × 96 × 8 (n: 8,6); pokrywka 99,6 × 99,6 × 20,0; wkładka 130 × 148,3 × 11,0; blat 200 × 200 × 14; korpusy 200 × 200,6 × 59,6; tulejka 14,999 × 14,999 × 3,000; podkładki 9,000 × 8,997 × 0,5/1/2 | identycznie | tabela 1 ± 0,1 | B | |
| K‑03 | ZAL | 17 × (0 / 0 / 0) | 0/0/0 | 0/0/0 | B | |
| K‑04 | ZAL | 17 × 1 składowa | 1 | 1 | B | |
| K‑04b | ZAL | płytki 57,941…57,953 / 60,222…60,234; pokrywka 30,064; wkładka 12,406; blat 72,569; korpus W 233,661 / P 233,633; tulejka 0,244; podkładki 0,027 / 0,055 / 0,109 cm³ | identycznie (do 0,01) | tabela 1 ± 30 % | B | |
| K‑05…K‑16 | ZAL | jak w raporcie A (8 płytek: K‑05 24/2 i 35/2, min ścianka 3,000; K‑06 120/175 sond; K‑07…K‑12, K‑14, K‑15 wszystkie sondy zgodne; K‑13 cyfry 1…6 z rzutów; K‑16 min 3,62/3,53, dołek–rowek 1,30) | identycznie | — | B | płytki niezmienione od etapu A (SHA te same) |
| K‑17, K‑18, K‑20, K‑22 | ZAL | pokrywka 20,0 bez otworów i reliefu: 12/12, 8/8, 4/4; wnęka 96,600 × 96,600; para pokrywka–wkładka w K‑53: 0 | identycznie | tak | B/P | kontrole odwrotne K‑19 (6/6 W) i K‑21 (wierzch 0,000) ZAL |
| K‑23…K‑32 | ZAL | wkładka: 10/10, 7/7, 19/19, 4/4, 4/4, 38/38, 11/11; strzałki 6,600/6,600, pas 6,000; otwór 96,600 × 96,600 | identycznie | tak | B/P | wkładka z etapu C (SHA `719eeb…`) zmierzona ponownie |
| K‑33 | ZAL | spód wkładki 63,600; dyfuzor 63,600; kołki w otworach 4/4 | identycznie | 63,6 ± 0,02 | B | |
| K‑34…K‑44 | ZAL | korpus W i P: 10/10, 33/33, 29/29, 18/18, 28/28, 20/20, K‑40 7/7 + 429 promieni y ∈ [−100,600, −100,000], 12/12, K‑43 −100,600 / −100,000 (napisy z rzutów), 8/8 | identycznie | tak | B/P | |
| K‑43 W/P | ZAL | SHA różne; objętość W − P = 0,0287 cm³ | 0,029 | ≠ 0, < 0,5 | B | |
| K‑44b | ZAL | 12 par Pi/wtyk × 0; luz 8,000; 3 kierunki wtyku × 7 obiektów: 0 | identycznie | 0 / ≥ 8 | B | |
| K‑45…K‑47 | ZAL | blat: 13/13, 14/14, 43/43; dno otworów kołków −3,800 / −4,000 | identycznie | tak | B | |
| K‑49 | ZAL | luz kołnierz–korpus 0,500/0,500; dyfuzor–kieszeń 1,000; PCB–blat 4,00; PCB pod oknem 1,00/stronę; dystanse na stadionach Z 4; przecięcia 0 | identycznie | tak | B | |
| K‑52b | ZAL | tulejka: 12/12 sond; z promieni otwór ø8,200, walec ø11,999, kołnierz ø14,999; gabaryt 14,999 × 14,999 × 3,000 | 7/7 | tak; 15 × 15 × 3 ± 0,1 | P | |
| K‑52c | ZAL | podkładki 0,5 / 1 / 2: 7/7 sond każda; otwór ø3,395; gabaryt 9,000 × 8,997 × t | 4/4 ×3 | tak; ± 0,05 | P | |
| K‑53 | ZAL | zestaw złożony 24 obiekty (z `tulejka_dc`; 3 podkładki odsunięte): 43 pary z nakładającym się bbox po skurczu −0,05: 0 przecięć (pozostałe 233 pary rozłączne w bbox); kontrola czułości bez skurczu: styki wykrywane (469/180/314/104/162) | 276 par, 0 | 0 | B | |
| K‑54 | ZAL | łańcuch 63,6 / 63,6 / 69,6 (71,1) / 74,1 (74,7) / 90,1 / 70,1 / 34 / 42 / 54…55,6 / 54 / 4 i 3 / −4…0 / 59,6 | identycznie | ± 0,05 | B | |
| K‑55 | ZAL | 66,300 − 65,100 = 1,200 | 1,200 | 1,2 ± 0,05 | B | |
| K‑56 | ZAL | pasy 27,700 / 27,700 → 11 px; 0 obiektów nad pasami | 27,70 / 27,71 | 27,7 / 11 | B | |
| K‑57 | ZAL | CSV 15 wierszy (10 drukarnia + 5 własne); vs moje pomiary: max |Δobjętość| 0,0045 cm³, |Δgabaryt| 0,003 mm; ilości i materiały = `quantities`/`materials`; koszty wg wzoru z arkusza (min/max × 1,2 × 1,3 dla grafitu) |Δ| 0,005 zł; druk własny bez kosztu; sumy drukarni 1004,20 cm³, 904–1607 / 1212–2155 zł = .md; brak płytek bazowych; uwaga STEP/FreeCAD: jest | identycznie | wszystko | P | |
| K‑58 | ZAL | tabela n → magnesy → dołki 6/6, instrukcja bieguna obecna | identycznie | tak | P | |
| K‑59 | ZAL | czysty przebieg: 17/17 STL; 16 identycznych bajtowo, wkładka identyczna kanonicznie (0 różnych trójkątów); objętości i gabaryty identyczne; JSON/CSV/arkusze identyczne | N/D (wykonuje recenzent) | tak (kryterium nadzoru) | B | |
| K‑60 | ZAL | 3 PNG 1600 × 1200; render rozstrzelony: podpisane i widoczne 12/12 pozycji z §11 (korpus W z napisem, blat, dyfuzor, panel, Pi + Bonnet z wtykiem, 4 dystanse na stadionach, wkładka, płytka n1, pokrywka, gniazdo DC, tulejka DC, gniazdo USB), przednia ścianka gładka z napisem, kolory grafit/biały/pleksi/PCB/mosiądz; render złożony i płytek (n1 z cyfrą 1, n4 z cyfrą 4, dołki przy lewej krawędzi, wycięcie przód‑prawe) obejrzane; raport C: wszystkie 56 K‑xx etapów A+B+C; zrzut `parametry.json` w `arkusz_wymiarow.md` zgodny (273 klucze); LICZONE 9/9; README z poleceniami od `cd`; do_v3.md jest | identycznie | tak | P | |

## 3. Uwagi do poprawy (tylko NIE), z numerami
| Nr uwagi | K‑xx | Waga | Plik / cecha | Co jest | Co ma być |
|---|---|---|---|---|---|
| — | — | — | brak sprawdzeń NIE | — | — |

## 4. Rozbieżności między raportem wykonawcy a pomiarem recenzenta
Brak. Wszystkie wartości (objętości, gabaryty, sondy, łańcuch wysokości, luzy, arkusz, rendery) zgodne; moje liczby sond większe tam, gdzie rozszerzyłem je na cechy symetryczne.

## 5. Ocena rejestru odstępstw wykonawcy
| # | Zasadne? | Wymaga decyzji właściciela? | Komentarz |
|---|---|---|---|
| 1 (nakrętka DC 2,0) | TAK | NIE (R51) | bryła zastępcza |
| 2 (`proxy_odbiornik_usb` x 35…54) | TAK | NIE (R51) | wykonawca dodał test informacyjny w zestawie W: 0 przecięć, 5,0 mm do korpusu |
| 3 (wzór kosztu pokazowego) | TAK | NIE | wzór zapisany pod tabelą arkusza; mój przelicznik tym wzorem daje |Δ| 0,005 zł; sumy zgodne |
| 4 (gniazda i tulejka wysunięte w bok na renderze) | TAK | NIE | czytelność renderu; widoczność potwierdzona |
| 5 (bez gwintu ø8 w tulejce) | TAK | NIE (do_v3) | zależy od pomiaru #16 |
| 6 (opis planu 95,2…97,2) | TAK | nadzór poprawi opis | STL zgodne z `parametry.json` (kołnierz 95,0…97,0 zmierzony w K‑46/K‑49) |
| 7 (SHA wkładki między przebiegami) | TAK | rozstrzygnięte przez nadzór | potwierdzone pomiarem: różnica tylko w bajtach, siatka identyczna |

## 6. Lista drobnych (D) do v3
1. `ramka_wkladka_v2.stl` nie jest bajtowo powtarzalna (znak zera w normalnych / przekątna remisowa) — kanoniczna normalizacja w `stl_kanoniczny` w v3 (do_v3 #9).
2. `.blend` i rendery różnią się SHA między przebiegami (szum/metadane) — oczekiwane; README po czystym przebiegu wpisuje „etap ALL” zamiast „etap C” (kosmetyka).
3. Pozycje z do_v3.md #1–#10 pozostają aktualne.

## 7. Sprawdzenia dodatkowe (poza protokołem)
- Ciągłość kanałów Halla A/B/C w spodzie końcowej wkładki (SHA `719eeb…`): ciągłe (BFS, 17 010 komórek kanałowych).
- K‑44b: 3 kierunki wtyku Bonnetu wobec 7 obiektów — 0 przecięć.
- Tulejka i podkładki: średnice z promieni (8,200 / 11,999 / 14,999; 3,395) zgodne z `dc_bush_*`, `panel_shim_*`.
- Pasowanie tulejka–otwór ø12 ściany skrzynki: w `.blend` para `tulejka_dc`–`korpus_W` i `tulejka_dc`–`proxy_gniazdo_dc` po skurczu 0 (bez skurczu 2422 / 719 styków — części stykają się, nie przenikają).
