# GOTOWOŚĆ RECENZENTA (bramka G1)

Przeczytane w całości: `plan_ramki_v2.md`, `parametry.json`, `protokol_weryfikacji_v2.md`, `szablon_raport_recenzenta.md`, `sesja2_pliki.md` (sekcje 1–9), `00_PRZEPLYW_I_BRAMKI.md`. Nie czytałem: `plan_ramki_v1.md`, `spec_3d_ramka.md`, `prompt_wykonawca.md`, `ramka_3d.html`, `animacja_ramki.html`. Blender 5.2.3 LTS uruchamia się w trybie `-b`, `bpy.ops.wm.stl_import` dostępny. Folder `recenzja/` utworzony. `wyniki_v2/` jeszcze nie istnieje (oczekiwane).

## (a) Sprawdzenia etapu A, które wykonam

- K‑01, K‑02, K‑03, K‑04, K‑04b — dla 9 STL: `ramka_plytka_wieczorna_v2`, `ramka_plytka_poranna_v2`, `…_wieczorna_n1/n2/n3_v2`, `…_poranna_n4/n5/n6_v2`, `ramka_pokrywka_v2`.
- K‑05 … K‑16 (płytki: JSON i STL), K‑17 … K‑22 (pokrywka), K‑58 (`kody_plytek.md`).
- K‑22 i K‑32 mają część „w złożeniu” (przecięcie w `.blend`) — w etapie A wykonam tylko część z sond (wnęka 96,6 ± 0,2); część złożeniową oznaczę N/D do etapu C (`.blend` powstaje w C).
- Dodatkowo już teraz: K‑60 w części „`parametry.json` LICZONE vs wzory” — przeliczyłem: korpus_h 54,6 ✓, blat_top_z 58,6 ✓, panel_pcb_z 49 ✓, panel_standoff_l 45 ✓, cover_inner_h 14 ✓. Plik spójny.

## (b) Sondy błędnie położone lub niejednoznaczne (z propozycją poprawki)

Liczby liczone z `parametry.json` i planu v2 (sekcje 4, 7). Stosuję protokół jak jest do czasu odpowiedzi właściciela; przy sondach, które z definicji trafiają < 0,1 mm od ściany, zastosuję regułę z sekcji 12 protokołu (przesunięcie 0,1 w głąb oczekiwanego obszaru, zapisane w raporcie).

### Błędy (sonda daje zły wynik na POPRAWNEJ części)

| # | K‑xx | Co jest w protokole | Dlaczego źle | Propozycja |
|---|---|---|---|---|
| 1 | K‑18 | garby na Z = −16 („2 mm nad dolną krawędzią”) | Dolna krawędź kołnierza jest na −20 (wierzch 2 + wnęka 18), 2 mm nad nią = **−18**. Wierzch płytki leży na −16, rowek płytki (środek 2 mm pod wierzchem) na −18. Garb na −16 trafiałby w górną krawędź płytki, nie w rowek. | wszystkie sondy K‑18 na Z = **−18**: (47,8, 0, −18) W; (47,8, 20, −18) POZA; (−47,8, 0, −18) W; (25, −47,8, −18) W; (0, −47,8, −18) POZA; (−25, 47,8, −18) W; (25, 47,8, −18) POZA |
| 2 | K‑24 | (−40, −40, 1,5) W; (40, 40, 1,5) W; (−40, 40, 1,5) W | Kieszeń Halla 5,0 × 5,5 ma środek (±42, ±42) → obejmuje x 39,5…44,5, y 39,25…44,75. Punkt (±40, ±40) leży **wewnątrz kieszeni przelotowej** (K‑25 w tym samym miejscu oczekuje POZA). Na poprawnej części K‑24 A/B/C wypadnie NIE. | (−38, −38, 1,5) W; (−38, −38, 3) POZA; (38, 38, 1,5) W; (−38, 38, 1,5) W; (38, −38, 1,5) W (D bez kieszeni, może zostać 40); (−30, −30, 1,5) POZA; (−35,5, −35,5, 1,5) POZA bez zmian |
| 3 | Tabela 1, wkładka | gabaryt Z 9,5 | Kołek orientacyjny na półce D sięga Z 7,5 (K‑27: „szczyt 7,5”), kołki ø3 pod spód 3,5 → STL ma Z = 3,5 + 7,5 = **11,0** (napis PRZÓD 6,6 nie jest najwyższy). K‑02 ±0,1 wypadnie NIE na poprawnej części. | 104,6 × 148,3 × **11,0** |
| 4 | Tabela 1, pokrywka | gabaryt 99,6 × 99,6 × 20 | Napis „GÓRA” relief 0,6 na wierzchu (K‑21) → STL ma Z = **20,6** (jak płytki n: 8,6). | 99,6 × 99,6 × **20,6** |
| 5 | K‑46 | haczyk na Z = −12,5 (globalnie 46,1) | Kieszeń w korpusie (K‑42, `snap_pocket_z`) to Z 47,6…50,1 = w układzie blatu **−11,0…−8,5**. Haczyk na −12,5 jest 1,5 mm pod kieszenią → w złożeniu wchodzi w ścianę (K‑53 blat–korpus ≠ 0). Źródło: plan 4.4.2 „krawędź haczyka 1 mm nad dolną krawędzią kołnierza” (= 45,6) jest sprzeczne z `snap_pocket_z` 47,6 (= 3 mm nad dolną krawędzią kołnierza 44,6). **Uwaga do planu**: ujednolicić — proponuję dolna krawędź haczyka 3 mm nad dolną krawędzią kołnierza (globalnie 47,6), wysokość haczyka 2,5. | sondy haczyków na Z = **−10**: (97,7, 0, −10) W; (97,7, 20, −10) POZA; (0, −97,7, −10) POZA; (50, −97,7, −10) W; (−50, 97,7, −10) W; (50, 97,7, −10) POZA; (−97,7, 0, −10) W |
| 6 | K‑47 | słupki „(±75, 95,2)”, sondy (75, 91, −8,6) POZA, (75, 97, −8,6) POZA | Plan 4.4.3 i sekcja 7: słupek 6 × 6 × 10 **na wewnętrznej stronie** tylnego kołnierza (kołnierz y 95,2…97,2) → słupek y 89,2…95,2; otwór ø4 × 6 od zewnętrznego lica kołnierza (97,2) → y 91,2…97,2. Wtedy (75, 91, −8,6) jest w materiale słupka (0,2 od dna otworu), nie w powietrzu. Zapis 4.11 „słupki y 92…98” jest literówką (słupek wystawałby 0,8 poza kołnierz, w ścianę korpusu). | (75, 93, −8,6) POZA (otwór); (75, 90,5, −8,6) W (słupek za dnem otworu); (75, 88, −8,6) POZA (powietrze przed słupkiem); (75, 93, −6) W; (75, 93, −12) W. **Uwaga do planu**: poprawić 4.11 na „y 89,2…95,2” |
| 7 | K‑54 | max Z: rama wkładki 64,6; płytka 69,1; pokrywka 85,1 (± 0,05) | max Z obiektu wkładki = **66,1** (kołek na półce D), płytki n1 = **69,7** (relief cyfry), pokrywki = **85,7** (relief GÓRA). Mierzone jako max Z siatki wypadną NIE na poprawnych częściach. | wierzch ramy wkładki 64,6 mierzyć poza kołkiem i napisem (np. ray z góry w (0, 50,3)); płytka: 69,1 to wierzch płaski (ray w (0, 0)… nie — w (−20, −44) poza gniazdami), relief 69,7; pokrywka: wierzch 85,1 mierzyć poza napisem (np. (40, 40)), relief 85,7 |

### Sondy < 0,1 mm od ściany (z definicji niestabilne) — proponowane przesunięcia

| # | K‑xx | Sonda | Odległość od ściany | Propozycja |
|---|---|---|---|---|
| 8 | K‑06 | (x + 1,6, y, −6) W | 0,1 od otworu ø3 (przy siatce stożka/walca jeszcze mniej) | (x + 2,0, y, −6) W |
| 9 | K‑17, K‑22 | (48,2, 0, −10) POZA | 0,1 od ściany wnęki 48,3 | (48,1, 0, −10) POZA (wnęka nadal 96,6 ± 0,2 ✓ z parą 48,1/48,5) |
| 10 | K‑23, K‑32 | (48,2, 0, 3) POZA | 0,1 od ściany otworu 48,3 | (48,1, 0, 3) POZA |
| 11 | K‑34 | (98,75, 0, 54,5) W | 0,1 od wierzchu 54,6 | (98,75, 0, 54,4) W |
| 12 | K‑47 | (58, 93,5, −3,95) W („dno 0,2”) | 0,05 od spodu blatu (−4,0) | zamiast sondy parzystości: pomiar grubości dna promieniem (z góry pierwszy trafiony Z = −3,8 ± 0,05, z dołu = −4,0 ± 0,05) |
| 13 | K‑37 | (−63, 101, 10,5) W; (101, 45, 10,5) W | Daszek 1,5 gruby pochylony 45° z dolnym licem od (y 100, Z 9,5): na y = 101 zajmuje Z 8,5…10,62 → 10,5 jest 0,085 od górnego lica. Jeśli wykonawca poprowadzi górne lico od Z 9,5 + 1,5 = 11 (grubość pionowa 1,5), daszek to Z 8,5…10,0 i sonda wypada POZA. Geometria daszka (R24) jest niedookreślona. | (−63, 101, 9,6) W; (−63, 101, 7,4) POZA; (101, 45, 9,6) W. **Uwaga do planu**: dopisać w D14/R24 definicję: dolne lico daszka zaczyna się na zewnętrznym licu ściany na górnej krawędzi szczeliny (Z 9,5), schodzi 45° przez 2 mm wysięgu; grubość 1,5 prostopadle |

### Niejednoznaczne (wynik zależy od interpretacji wykonawcy)

| # | K‑xx | Problem | Propozycja |
|---|---|---|---|
| 14 | Tabela 1, blat | „obrót 180° wokół X” — jeśli wykonawca obróci blat do druku wokół **Y** (też poprawne „wierzchem w dół”), po moim obrocie wokół X wszystkie cechy będą obrócone o 180° wokół Z (słupki i otwory kołków z przodu zamiast z tyłu); K‑02 tego nie wykryje (200 × 200), K‑47 wypadnie NIE, choć część nie jest odbita. Pokrywka jest na to odporna (symetria garbów ±25). | Zapis w tabeli 1: „eksport blatu: obrót dokładnie o 180° wokół osi X (y → −y, z → −z)”. W skrypcie dodam test rozpoznawczy: jeśli K‑47 nie przechodzi, a przechodzi po dodatkowym obrocie 180° wokół Z — raportuję „zła oś obrotu eksportu (B wg K‑02), część nieodbita” |
| 15 | K‑19, K‑21 | `cover_vent_d`: „siatka 2×3, rozstaw 30” — protokół zakłada x = ±15, y = −30/0/30; równie dobrze może być x = −30/0/30, y = ±15. Wysokość liter „GÓRA” nie jest parametrem (plan 4.2 nie podaje); „obszar środka” w K‑21 nieokreślony. | Plan 4.2 / parametry: dopisać „kolumny x = ±15, rzędy y = −30, 0, 30” i `cover_label_h` (proponuję 5). K‑21: obszar |x| ≤ 12, |y| ≤ 4 (poza otworami ø4 w (±15, 0)). |
| 16 | K‑31 | Napis „PRZÓD” 4 mm na górnej powierzchni przedniego boku: faza 1 × 45° na krawędzi wewnętrznej zostawia 3 mm płaskiego wierzchu (y −49,3…−52,3), więc litery 4 mm się nie mieszczą; położenie x (który segment poza wycięciem palcowym −15…15) nie jest w planie ani w parametrach. Protokół zakłada x ∈ [18, 46]. | Plan 4.6.8: litery 2,5 mm, środek napisu (33,6, −51,0), strzałka na segmencie lewym; parametr `insert_label_h`. **Uwaga do planu (kolizja)**: relief 0,6 nad ramą (Z 65,2 w złożeniu) leży pod kołnierzem pokrywki (dół 65,1, y −48,3…−49,8) → K‑22/K‑53 pokrywka–wkładka ≠ 0, jeśli litery wejdą w pas y −49,3…−49,8. Napis trzymać w y −50,0…−52,3 albo obniżyć relief w tym pasie. |
| 17 | K‑25 | Przelot 2,5 × 1,5 w ściance ramy: sonda (−50, −50, 0,7) zakłada przelot po przekątnej przez narożnik ściany. Plan 4.6.3 mówi tylko „w ściance ramy przelot do rowka zewnętrznego”. | Plan 4.6.3: „przelot po przekątnej narożnika, od (−48,3, −48,3) do (−52,3, −52,3), szer. 2,5, wys. 1,5 od spodu”; wtedy sonda jest poprawna |
| 18 | K‑22, K‑32 | odsyłają do „K‑44” (test przecięcia) — K‑44 to żebra/stopki; test przecięć par to K‑53 | zamienić na K‑53 |
| 19 | K‑13, K‑43, K‑21, K‑31 | „max Z / min Y wierzchołków w obszarze” — płaska ściana bez wierzchołków w obszarze da pusty zbiór (np. baza płytki bez cyfry, ściana korpusu w Z 30…36). | mierzę promieniami (siatka 0,25 mm) z góry / z przodu: max Z pierwszych trafień; wierzchołki tylko pomocniczo. Proszę o zgodę na tę metodę jako równoważną |
| 20 | plan 3.4 | `snap_hook_arm_l` 12 > `blat_skirt_h` 10 — ramię sprężyste nie może być dłuższe niż kołnierz; nacięcia (K‑46) muszą sięgać min. Z −9 (sonda (96,2, 4,5, −9)). | **Uwaga do planu**: ramię = długość nacięcia ≤ 9 (proponuję 8, od dolnej krawędzi kołnierza); parametr 12 → 8 |

Wszystkie pozostałe sondy K‑05…K‑17, K‑19, K‑20, K‑23, K‑25 (poza przelotem), K‑27…K‑30, K‑34…K‑36, K‑38 (wersje po „poprawka”), K‑39, K‑40, K‑42…K‑45, K‑48, K‑49 przeliczyłem względem `parametry.json` — położone poprawnie, odległość od ścian ≥ 0,15 mm.

## (c) Jak zaimplementuję test „w bryle / poza bryłą”

1. Import STL (`bpy.ops.wm.stl_import`), sprawdzenie K‑01, transformacja do układu montażowego wg tabeli 1 własnym kodem (macierz: obrót + przesunięcie wyliczone z bbox; dla korpusu środek XY z obrysu dna Z ≈ 0, nie z bbox z daszkami; dla wkładki y_środka = y_min + 52,3).
2. `BVHTree.FromPolygons` na przekształconej siatce (po `calc_loop_triangles`).
3. Dla każdej sondy: promienie w 3 kierunkach lekko „irracjonalnych”, by nie trafiać w krawędzie: ≈ +X (1, 0,00071, 0,00137), ≈ +Y, ≈ +Z; dla każdego kierunku zliczam WSZYSTKIE przecięcia (po trafieniu przesuwam początek 1e‑4 za punkt trafienia i strzelam dalej); parzystość nieparzysta = w bryle. Zapisuję 3 wyniki cząstkowe + 3 liczby przecięć.
4. Wynik sondy = większość; jeśli 3 wyniki niezgodne → „niestabilna” → przesunięcie 0,1 mm w głąb oczekiwanego obszaru (w kierunku od najbliższej ściany: `find_nearest`), nowa pozycja i 3 wyniki zapisane w JSON; jeśli nadal niezgodne → NIE z adnotacją (możliwy niemanifold, por. K‑03).
5. Kontrola krzyżowa dla każdej sondy: `find_nearest` + znak iloczynu normalnej i wektora do punktu; rozbieżność z parzystością również raportuję.
6. K‑03: `bmesh` — krawędzie z liczbą ścian ≠ 2, luźne wierzchołki, `BVHTree.overlap(self, self)` z odrzuceniem par trójkątów dzielących wierzchołek. K‑04: BFS po krawędziach → liczba składowych. K‑04b: objętość z dywergencji (suma (a·(b×c))/6) — znak = orientacja normalnych.
7. Reliefy (K‑13/K‑21/K‑31/K‑43): mapa wysokości promieniami z góry/przodu na siatce 0,25 mm → PPM/PNG zapisany własnym kodem (bez matplotlib) → oglądam plik (Read) i wpisuję odczytaną cyfrę/tekst.
8. Wyniki: `recenzja/wyniki_A_iter<n>.json` (id, wynik, wartość, sondy z 3 wynikami cząstkowymi), raport wg szablonu, uruchomienie: `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P recenzja/sprawdz_A.py`.

Czekam na komunikat „RECENZJA ETAPU A, iteracja 1”.

---
## Uzupełnienie po aktualizacji protokołu (R47) — ponowna lektura

Przeczytane ponownie: `protokol_weryfikacji_v2.md`, `parametry.json` (302 klucze; LICZONE zgodne ze wzorami), plan v2 R46/R47 oraz 4.1, 4.2, 4.4, 4.5, 4.6. Font `Inter.woff2` jest w instalacji Blendera 5.2. Uwagi 1–20 wdrożone poprawnie; doprecyzowanie haczyka (Z 47,85…49,85, luz 0,25) przyjmuję. Nowe sondy wprowadziły 4 błędy i 1 niespójność:

| # | K‑xx | Co jest | Dlaczego źle | Propozycja |
|---|---|---|---|---|
| 21 | K‑47 | (75, 96,2, −9) W „kołnierz” | Otwór ø4 od lica 97,2 do 91,2, oś Z 50 (lokalnie −8,6) obejmuje x 73…77, Z −10,6…−6,6 → punkt (75, 96,2, −9) leży **w otworze** → POZA. | (70, 96,2, −9) W (kołnierz poza słupkiem) albo (75, 96,2, −12) W |
| 22 | K‑46 | (98, 0, −9) POZA | Po przeniesieniu haczyka na Z −10,75…−8,75 punkt (98, 0, −9) leży **wewnątrz występu haczyka** (x 97,2…98,2, y ±4) — 0,2 od czubka. | (98, 20, −9) POZA (poza haczykiem) albo (98, 0, −6) POZA |
| 23 | K‑54 | płytka n1: promień z góry w (−20, −44) → 69,1 | Wieczorna, rząd R1: gniazdo ø9 w (−18, −40,5) → odległość do (−20, −44) = 4,03 < 4,5 → punkt leży **w stożku gniazda**, promień trafi poniżej wierzchu. | (0, −46,5) → 69,1 (pas między rzędem R1 (y do −45) a fazą 47,5; wolny w obu płytkach) |
| 24 | K‑31 / plan 4.6.8 | strzałka ku −Y: „długość 10, szerokość 2”, środek (−32, −51,15) | Pas płaski ma 2,3 mm (y −50,0…−52,3); strzałka 10 mm wzdłuż Y się nie mieści; wzdłuż X (10 mm) nie wskazywałaby −Y. Wykonawca nie może zbudować planu jak jest. | trójkąt ▼ 2 mm (Y) × 3 mm (X), relief 0,6, środek (−32, −51,15); K‑31 bez zmian (obszar [−40, −24] nadal pokrywa) |
| 25 | K‑22, K‑32 | „(48,2 POZA, 48,5 W) → 96,6 ± 0,2” | K‑17/K‑23 mają już 48,1; odsyłacz nieaktualny (kosmetyka). | zamienić na 48,1 |

Do odnotowania (nie błąd sond): (a) rampa naprowadzająca haczyka od dołu nie ma zdefiniowanej długości — sonda (97,7, 0, −12,5) POZA ma margines 0,125 nawet przy rampie od samego dołu kołnierza, więc zostaje; (b) ciągłość kanału Halla C: przelot po przekątnej (szer. 2,5, do (52,3, 52,3)) musi łączyć się z kanałem pod nasadą (y 49,5…51,5) — w etapie B sprawdzę promieniem wzdłuż kanału, poza sondami protokołu; (c) dołek kodu przy x −45,0 ma do rowka pokrywki 1,3 mm < 1,5 (4.8) — przyjęte w R47(10), wpiszę jako D w raporcie etapu A.

---
## Uzupełnienie po R49 (wkręty formujące, bez wkładek)

| # | K‑xx | Co jest | Dlaczego źle | Propozycja |
|---|---|---|---|---|
| 26 | K‑47 | (75, 90,5, −8,6) W „słupek za dnem otworu” | Otwór słupka ø2,5 sięga teraz od lica 97,2 do **90,2** (głębokość 7) → punkt (75, 90,5) leży **w otworze**, 0,3 od jego dna → POZA. | (75, 89,7, −8,6) W (0,5 za dnem otworu, 0,5 przed czołem słupka 89,2) |

Uwaga do planu (R49): słupek blatu ma w Y 6 + kołnierz 2 = 8 mm (y 89,2…97,2); otwór 7 głęboki zostawia **1,0 mm** materiału za dnem (< 1,5 z zasady 4.8). Wkręt PT 3,0 × 8 przez ścianę 2,5 + luz 0,5 wchodzi 5 mm, więc głębokość 6 (do 91,2) wystarcza i zostawia 2,0 — proponuję `insert_depth_m3` 7 tylko dla bossów ramy (boss 6 + 1 w płycie blatu) i uchwytów, a dla słupków blatu 6 (albo słupek 7 w Y). Pozostałe sondy K‑36/K‑47 z otworami 2,5/2,1 zachowują marginesy ≥ 1,05 mm (sondy osiowe) i ≥ 1,25 mm (sondy obok otworu).
