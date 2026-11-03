# P3a — przekazanie (2.11.2026): inspect A+B, trudne scenariusze w generatorze, pełny łańcuch CLI

Zakres zamknięty w tej sesji: punkty 1–5 briefu P3a (inspect dwiema metodami, scenariusze trudne w `synth`, metryki per metoda i scenariusz, CLI z pełnym łańcuchem i statusami). Punkty 6–8 (okno, README dla laptopa, raport końcowy) — stan szkicu, lista zadań na końcu. Commity: `deeb2d2` → `71fd500` (7 commitów na `173dbd5`). `pytest testy`: **167 passed, 2 skipped** (testy okna oznaczone jako szkic). Wszystkie liczby z `narzedzia/metryki_P3a.py` na zestawach `dane/syntetyczne_P2` (24 skany) + `dane/syntetyczne_P3a` (16 skanów), 17 prawdziwych projektów z pulpitu; plik `dane/wyniki_P3a/metryki_P3a.json` (przebieg 5), wcześniejsze przebiegi `metryki_P3a_przebieg3.json`, `_przebieg4.json`.

## 1. Metryki (przebieg 5, kod `71fd500`)

40 skanów, 420 prac w prawdzie (449 fragmentów: prace bokiem po usunięciu spodu rozpadają się w `plate` na dwa skupiska), wyrównanie OK 40/40 (max 0,0137 mm), top‑1 411/420 — na zestawie P2 **271/271**, wszystkie błędy top‑1 to prace bokiem / do góry nogami / częściowe (szare, nie zielone). Czas na płytkę (mediana): plate 2,0 s, match 8,0 s, inspect 0,9 s, razem 11,1 s.

| scenariusz | prac | top‑1 błędny | gniazda zielone / czerwone / żółte / szare / pomarańczowe | ubytków wykrywalnych | A | B | A+B | czerwone | dowolna | prace całe | całe z alarmem | całe z czerwonym | fałszywe ubytki (A / B / A+B) | fałszywe czerwone |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dobrze | 300 | 0 | 103 / 86 / 108 / 0 / 3 | 279 | 229 (82 %) | 132 (47 %) | 103 (37 %) | 112 (40 %) | 258 (92 %) | 103 | 0 | 0 | 0 | 0 |
| bokiem | 76 | 27 | 32 / 2 / 8 / 31 / 3 | 3 | 1 | 1 | 1 | 1 | 1 | 20 | 1 | 0 | 3 (0 / 3 / 0) | 0 |
| częściowo | 36 | 8 | 19 / 1 / 7 / 8 / 1 | 0 | — | — | — | — | — | 6 | 0 | 0 | 0 | 0 |
| drgnięcie | 37 | 3 | 0 / 0 / 34 / 3 / 0 | 0 | — | — | — | — | — | 0 | 0 | 0 | 0 | 0 |
| razem | 449 | 38 | 154 / 89 / 157 / 42 / 7 | 282 | 230 (82 %) | 133 (47 %) | 104 (37 %) | 113 (40 %) | 259 (92 %) | 129 | 1 | 0 | 3 (0 / 3 / 0) | 0 |

- „ubytków wykrywalnych” = ubytki z prawdy spełniające specyfikację detektora (głębokość ≥ 0,08, ø 0,2–1,5) i widoczne w skanie; „A / B / A+B / czerwone / dowolna” = ile z nich ma wykrycie danej metody w promieniu ø/2 + 0,3 mm. „Prace całe” = prace bez żadnego ubytku; „z alarmem” = status `ubytek` albo `sprawdz`. Prace z drgnięciem: ubytki nieliczone z definicji (status „skan ponownie”).
- **Drgnięcie: 28/34 (82 %)**, fałszywych „skan ponownie” 0; 6 pominiętych ma status „popraw ułożenie” (żółte), żadne nie jest zielone. **Poprawki ręczne: 12/20** rozpoznane jako pomarańczowe (fałszywych 0); pozostałe 8 → żółte „popraw ułożenie” albo „sprawdź ułożenie”.
- Per zestaw: P2 (24 skany, 233 ubytki): A 190, B 109, czerwone 90, dowolna 215 (92 %), 82 prace całe bez alarmu, drgnięcie 20/23. P3a (16 skanów, 49 ubytków widocznych): A 40, B 24, czerwone 23, dowolna 44 (90 %), 47 prac całych: 1 alarm (żółty), drgnięcie 8/11.

**Cele planu:** wykryte ≥ 90 % — **tak** (92 % dowolną metodą; samą A 82 %, samą B 47 %); fałszywe alarmy ≤ 10 % na pracach całych — **tak** (1/129 = 0,8 %, żółty); fałszywe czerwone na pracach bokiem / zasłoniętych = 0 — **tak**; drgnięcie 100 % — **nie** (82 %, patrz decyzje).

## 2. Decyzje inspect i dlaczego (liczby z przebiegów 1–5)

1. **Odchyłka ze znakiem** z `RaycastingScene.compute_closest_points` + normalna najbliższego trójkąta (zgodność z `compute_signed_distance` 0,90–1,00; działa też na siatkach nieszczelnych).
2. **Rozmiar plamy A** = rozpiętość 2–98 percentyla rdzenia (≥ 0,08 pod powierzchnią); bez tego pojedyncze punkty szumu (0,4 % punktów ≤ −0,08 przy σ 0,03) doczepiały się do plamy i ø0,86 mierzyło 1,9 → „sprawdź ułożenie”. Histereza do −0,04 odrzucona (9 % punktów szumu). Dwa ubytki < 0,5 mm od siebie zlewają się w plamę > 1,5 mm → żółte „sprawdź ułożenie”, nie dwa czerwone (3 z 282 w zestawie).
3. **Ostra krawędź**: pierścień 0,15 mm (`krawedz_pas_mm`), mediana |d| ≤ prog/2; przy 0,3 mm gładka poprawka (profil kwartyczny) uchodziła za ostrą (mediana 0,037).
4. **Metoda B = pas 0–1,5 mm projektu**, nie ostra krawędź brzegu: na 17 projektach exocad 7 ma < 5 mm ostrych krawędzi (> 40°) przy brzegu, waxupy 0 mm. Wcięcie = cofnięcie skanu wzdłuż normalnej linii (wierzchołek skanu o zgodnej normalnej, w promieniu 0,8 mm, leżący głównie pod punktem linii). Trzy poprawki po drodze: (a) odległość do płaszczyzny stycznej zamiast do wierzchołka (siatki exocad mają wierzchołki co 0,1–0,3 mm → fałszywe wcięcia 0,5–0,9 na cienkich ściankach); (b) wierzchołek z drugiej strony cienkiej ścianki ma przeciwną normalną → szukany wśród 8 najbliższych pierwszy ze zgodną normalną; (c) na skraju dziury w skanie najbliższy wierzchołek leży bocznie i na wypukłej powierzchni pozornie „pod” → wymagane `pod ≥ 0,7·|R|`. Bramka widoczności linii `linia_min_udzial` = 0,9 (przy 0,6 prace bokiem dawały 18 fałszywych wcięć; przy 0,9 i promieniu 0,5 mm 16 % prac dobrze ułożonych traciło B przez rzadkie siatki → promień 0,8). Zostały 3 fałszywe wcięcia B (żółte) na 1 pracy bokiem.
5. **Drgnięcie**: udział komórek 1 mm z ≥ 10 % punktów |d| > 0,07 (drgnięcie 0,19–0,56, prace całe ≤ 0,03). Sama ta reguła dawała 37/37, ale duża gładka poprawka na małej atrapie też przekraczała 0,10. Reguła „po obu stronach powierzchni” liczona na komórce psuła wykrywanie (10/34: ICP trzyma się warstwy głównej, kopia leży po jednej stronie w komórce); liczona na całej pracy 27/34; z regułą rozproszenia (największe zwarte skupisko rozmytych komórek ≤ 60 %) 28/34. 6 pominiętych: udział 0,19–0,42, jednostronne (udział „nad” 0,05–0,18 albo 0,85) i w jednej plamie — nie do odróżnienia tymi regułami od poprawki; status żółty.
6. **Bramka pokrycia** (plan 1a pkt 4) z wyjątkiem: gdy pokrycie < 0,85 obniża gładka poprawka (po odjęciu jej punktów wraca nad próg) → pomarańczowe, nie „popraw ułożenie”.
7. **Decyzja końcowa** wg planu 1b: A+B w tym samym miejscu albo B ≥ 0,4 → czerwone; jedna metoda → żółte. Skutek: na pracach dobrze ułożonych czerwone dostaje 40 % ubytków, 52 % jest żółtych (tylko A) — B widzi tylko ubytki cofające powierzchnię o ≥ 0,2 mm (kula ø ≥ ~0,57). **Do decyzji właściciela:** czy samo A (82 %, 0 fałszywych na 129 pracach całych) ma dawać czerwone.
8. **`match`**: przy remisie obrotów zgrubnych (korona prawie okrągła: wszystkie 8 obrotów 0,998 przy 0,2 mm) o wyborze decyduje dokładne pokrycie na ≤ 4 obrotach równomiernie po kącie (seedy 21/27/29 testów na atrapach: 0,53 → 0,90). P2 top‑1 bez zmian 271/271.

## 3. Progi (`ustawienia.toml [inspect]`, wszystkie nowe klucze walidowane)

`prog_glebokosci_mm` 0,08 · `srednica_min_mm` 0,2 · `srednica_max_mm` 1,5 · `pas_brzegu_mm` 1,5 · `poprawka_min_mm` 2,0 · `krawedz_pas_mm` 0,15 · `min_punktow_plamy` 6 · `drgniecie_odchylka_mm` 0,07 · `drgniecie_udzial_w_komorce` 0,10 · `drgniecie_udzial_obszaru` 0,10 · `wciecie_min_mm` 0,2 · `wciecie_pewne_mm` 0,4 · `linia_min_udzial` 0,9. Stałe w kodzie (`inspect.py`): EPS_PLAMY 0,25, KAT_KRAWEDZI 40°, ODLEGLOSC_KRAWEDZI 0,5, BRAK_DANYCH 0,8, SASIADOW_LINII 8, ZGODNOSC_NORMALNEJ 0,2, UDZIAL_POD 0,7, UDZIAL_DRUGIEJ_STRONY 0,2, NAJWIEKSZA_PLAMA_DRGNIECIA 0,6. Wszystko dobrane na szumie generatora σ 0,03 — do oceny na prawdziwym skanie (P3b), nie strojone poza opisanymi wyżej zmianami.

## 4. Jak uruchomić

```
set PYTHONUTF8=1
py -3.12 -m pytest testy -q
py -3.12 -m stanowisko.porownaj --skan dane/syntetyczne_P2/skan_okragla_wieczorna_n8_s0100.stl --projekty <folder projektów> --plytka okragla_wieczorna --wspolczynnik 1.22 --prawda dane/syntetyczne_P2/skan_okragla_wieczorna_n8_s0100.json --wyjscie dane/wyniki_P3a
py -3.12 narzedzia/metryki_P3a.py --skany dane/syntetyczne_P2 dane/syntetyczne_P3a --projekty <folder projektów>      (≈ 11 min)
py -3.12 -m stanowisko.synth --projekty <folder projektów> --plytka okragla_wieczorna --ile 4 --seed 300 --wspolczynnik 1.22 --drgniecie 0.1 --poza-uklad --pole 100 --bokiem 0.35 --pokrycie 0.35 --poprawka 0.15 --wyjscie dane/syntetyczne_P3a
uruchom_okno.bat        (szkic: okno otwiera się, „Porównaj” zawisa — patrz 5.1)
```
`<folder projektów>` = folder z pulpitu (ścieżka w `dane/mapa_sciezek.json`, poza repo). Zestaw P3a: seedy 300–303 (okrągła wieczorna), 310–313 (okrągła poranna), 320–321 (wieczorna), 330–331 (poranna), 340–341 / 350–351 (`--bokiem 0.25 --pokrycie 0.5 --pokrycie-zakres 0.3-0.5 --poprawka 0.1 --ubytki 1-2`).

## 5. Do przejęcia (P3a‑2)

1. **Okno** (`stanowisko/ui_test.py`, `podglad3d.py`, `uruchom_okno.bat`, `opisy_modulow/ui.md`, `testy/test_ui.py` — 2 testy `skip`): silnik w `QThread` zawisa już na `match.Pula` (Open3D FPFH / RaycastingScene w wątku pod Qt: 195 s bez wyniku, w wątku głównym 3–4 s). Przenieść silnik do osobnego procesu (`multiprocessing` z `porownaj.porownaj` i postępem przez kolejkę albo `QProcess` + JSON), zdjąć `skip`, test okna zielony (ładuje skan, klika „Porównaj”, sprawdza kolory mapy, klik w gniazdo, decyzję CSV, zapis). Reszta okna (mapa, tabela, obraz odchyłek, decyzje, zapis, podgląd 3D w osobnym procesie) jest napisana i działa na wyniku.
2. **README „Laptop firmowy”** — sekcja napisana (instalacja, foldery, przebieg testu skanera, co zapisać dla P3b); przejrzeć po naprawie okna.
3. **Raport końcowy `raporty/P3a_<data>.md`** — z tego dokumentu + zrzut okna; w opisach modułów `inspect.md`, `synth.md`, `match.md`, `ui.md` „Założenia i granice” są aktualne.
4. Decyzja właściciela: samo A → czerwone? (pkt 2.7). Jeśli tak: w `polacz` kolor „[cytat usuniety]” = czerwony, metryka „[cytat usuniety]” rośnie z 40 % do 82 %.
5. Drgnięcie 82 %: ewentualnie trzecia reguła (porównanie z drugim skanem tej samej pracy / dwie warstwy w histogramie odchyłek w komórce) — po pomiarze prawdziwego drgnięcia w P3b.
6. `match`: prace bokiem rozpadają się na dwa fragmenty („podwójne”) i małe kawałki (≈ 1300 punktów) dostają zielony match — rozważyć minimalny udział powierzchni projektu (`pokrycie_odwrotne`) dla zielonego.
