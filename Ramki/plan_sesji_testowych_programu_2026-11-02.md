# Plan sesji: płytka okrągła (R57) + testy programu stanowiska

Data: 2026-11-02 (wersja 2, zastępuje wersję z tego samego dnia). Autor planu: sesja nadzorująca (Claude).
Stan wyjściowy: repo `stanowisko/` commit `d867542`, drzewo czyste; pliki ramek R56 (pakiet `Ramki_pakiet/`, Drive QC).
Decyzje właściciela 2.11: skaner zamówiony; zamówione po 1 płytce kwadratowej wieczornej i porannej; jutro zamówienie płytek okrągłych (wieczorna + poranna); test skanu zębów na płytce decyduje o dalszym projekcie; obecny kod programu = FUNDAMENT (nie usuwać, po udanych testach oznaczyć jako właściwy); zero tolerancji błędów geometrii.

## 0. Fakty, które sesje muszą znać

- Do skanera wchodzi TYLKO płytka. Wkładka, pokrywka, korpus, blat służą ramce świetlnej (etap po teście). Płytka okrągła do testu skanera nie potrzebuje nowej wkładki ani pokrywki; dopiero jej użycie na ramce wymaga nowej wkładki (otwór okrągły, kołek, magnesy) i pokrywki.
- Po R54 (1.11) w rogach płytki kwadratowej NIE MA gniazd ani stożków znaczników: wszystkie obrysy gniazd, rynienek i stożków leżą w kole r 47 od środka (zapas na pole ø100 przy obrocie). Rogi (promień 67,9) wystają poza pole, ale są puste: wycięcie orientacyjne, dołki kodu, numer, kieszenie magnesów od spodu.
- RYZYKO wykryte 2.11: dołki kodu (bity A/B/C) leżą w (−45, −36/−33/−30), czyli promień 54–58 mm — POZA kołem ø100. Program ma czytać numer płytki z dołków ze skanu; na kwadracie mogą być niewidoczne w całym obrocie (widoczne tylko w części obrotu — do sprawdzenia na teście). Na płytce okrągłej dołki muszą leżeć wewnątrz r 47 (sesja R57‑A). Obejście w programie: numer płytki podaje użytkownik (`--numer`) albo czyta go ramka z magnesów.
- Plan B dla kwadratu (bez płytki okrągłej): jeśli pomiar #12 (makieta 96 × 96 z okręgami ø90/94/100) da pole mniejsze niż ø100, zmienia się JEDNA liczba `scan_field_d` w `parametry.json`; `narzedzia/uklad_kolo_R54.js` + `weryfikuj_uklad_R54.js` przeliczają rzędy gniazd do mniejszego koła; generator daje nowe pliki płytek; ramka, wkładka, pokrywka bez zmian. Koszt: mniej gniazd. Poniżej ~ø94 kwadrat traci sens i obowiązuje płytka okrągła.
- Płytka okrągła nie zwiększa pola: skaner widzi to samo koło. Jej zaleta: brak wystających rogów (mniej ryzyka kolizji w komorze i zacienienia), dołki kodu i wycięcie da się umieścić w polu. Wada: nowa wkładka i pokrywka do ramki, inne mocowanie orientacji.
- Program czyta tylko `modele_plytek/<nazwa>/uklad.json` + STL; obrys płytki jest mu obojętny. Wariant okrągły = nowy folder + parametr `--plytka`, bez zmian logiki.
- Numery płytek: kod 3‑bitowy n = A + 2B + 4C; zajęte n1–n6 (kwadrat). Wolne: n7 i n0. Zalecenie: dodać 4. bit D (dołek w kolejnej pozycji), zgodny wstecz (n1–n6 nie mają dołka D) → okrągła W = n8, okrągła P = n9. Decyzja właściciela w R57‑A.

## 1. Kolejność sesji

| Nr | Sesja | Model | Czas | Warunek startu |
|---|---|---|---|---|
| R57‑A | Płytka okrągła w generatorze (wykonawca) | Fable 5.1, effort high | 4–6 h | decyzje z sekcji 0 potwierdzone przez właściciela |
| R57‑B | Recenzja + trzecie oko płytki okrągłej | Fable 5.1, effort high, NOWA sesja (fresh) | 2–3 h | raport R57‑A |
| R57‑C | Dokumenty, arkusz zamówienia, pakiet, Drive | Opus 5.5 | 2 h | R57‑B ZALICZONY |
| P1 | Program: fundament i naprawa błędów | Opus 5.5 | 3 h | od razu, równolegle z R57 |
| P2 | Program: porównanie STL z folderu na pulpicie (plate + match) | Fable 5.1, effort high | 1 dzień | P1 gotowe + ≥ 30 prawdziwych STL w `Desktop\Prace_test\` (właściciel: 10 folderów) |
| P3a | Program: ubytki (inspect) na sztucznych skanach + proste okno (ui) + przełącznik płytki | Fable 5.1, effort high | 1,5 dnia | P2 gotowe (bez skanera) |
| P3b | Program: pierwszy prawdziwy skan — strojenie progów, werdykt kwadrat / koło, „idziemy / nie idziemy” | Fable 5.1, effort high | 0,5 dnia | P3a gotowe + STL z testu skanera na prawdziwych płytkach |

Dobór modelu: Fable 5.1 tam, gdzie powstaje nowa geometria, algorytmy dopasowania 3D (ICP, FPFH) lub niezależna weryfikacja z siatek (błąd = zła płytka albo zły werdykt). Opus 5.5 tam, gdzie zadanie jest dobrze opisane i sprawdzalne testami (naprawa znanych błędów, dokumenty, pakiet). Recenzent zawsze w osobnej, świeżej sesji, nigdy w tej samej co wykonawca.

## 2. Sesja R57‑A — płytka okrągła w generatorze (Fable 5.1)

Pliki: `ramka_generator.py`, `parametry.json`, `plan_ramki_v2.md` (rejestr R57, sekcja 14), `protokol_weryfikacji_v2.md`. Kopie sprzed edycji do `archiwum/*_przed_R57_<data>.*`. Pliki kwadratowych płytek, korpusu, blatu, wkładki, pokrywki: BEZ ZMIAN BAJTOWO (SHA jak w R56).

1. Nowe klucze `parametry.json` (walidator R14): `plate_shape_round` (bool, wariant), `plate_round_d` 96 (ZAŁOŻENIE: to samo koło gniazd r 47; średnica do potwierdzenia przy #12), `round_flat_w` (ścięcie orientacyjne zamiast wycięcia, zalecenie: cięciwa 8 mm z przodu‑prawo), `code_dimple_pos_round` (dołki A/B/C/D wewnątrz r 47, zalecenie: wzdłuż lewej krawędzi na promieniu ≤ 44, ≥ 3 mm od gniazd, ≥ 1,5 mm od stożków), `code_bit_d_pos` (4. bit także dla kwadratu — pozycja pusta na n1–n6).
2. Geometria: obrys walec ø96 × 8 z fazką jak kwadrat (`plate_top_chamfer`), ścięcie orientacyjne, gniazda i rynienki IDENTYCZNE jak R54 (ten sam `uklad.json` rzędy), stożki znaczników jak R54 (`ev_/mo_marker_pos`), dołki kodu w nowych pozycjach, numer reliefowy wewnątrz pola lub pominięty, BEZ kieszeni magnesów (wariant do skanera; magnesy wrócą z nową wkładką).
3. Pliki wynikowe: `ramka_plytka_okragla_wieczorna_v2.stl` (bazowy), `…_okragla_wieczorna_n8_v2.stl`, `…_okragla_poranna_v2.stl`, `…_okragla_poranna_n9_v2.stl`; `uklad_gniazd_okragla_wieczorna.json`, `…_poranna.json` (z polem `shape: round`, `d: 96`, `flat`).
4. Protokół: K‑05 (c) koło r 47 bez zmian; nowe K‑61 (obrys okrągły ø96 ± 0,05, ścięcie), K‑62 (dołki kodu w polu: promień ≤ 47, odległości), K‑63 (brak kieszeni magnesów, spód płaski); K‑59 (szczelność, SHA) dla nowych plików.
5. Raport wykonawcy wg `szablon_raport_wykonawcy.md`; `--etap SPRAWDZ` 0 NIE; nowe pliki do `wyniki_v2/stl/` i `wyniki_v2/json/`.

Gotowe = 4 STL + 2 JSON, sprawdzenia 0 NIE, pliki R56 bajtowo nietknięte, rejestr R57 wpisany.

## 3. Sesja R57‑B — recenzja i trzecie oko (Fable 5.1, nowa sesja)

1. Niezależnie z siatek STL (nie z JSON): obrys ø96, grubość 8, gniazda = R54 (pozycje, średnice górne i dolne, głębokość 4, otwory ø3), stożki, dołki, ścięcie — porównać z `parametry.json` i `uklad.json` sondami (jak `recenzja/sprawdz_R54.py`).
2. Koło: max promień obrysu gniazd ≤ 47; dołki ≤ 47; ścianki ≥ 3; dołek–stożek ≥ 1,5; dołek–gniazdo ≥ 3.
3. Szczelność, normalne, liczba brył = 1; SHA nowych plików = raport wykonawcy; SHA 15 plików R56 bez zmian.
4. Kontrola odwrotna: dawne pozycje dołków (−45, −36…−30) i rogi (±42, ±42) poza bryłą.
5. Raport `recenzja/raport_recenzenta_R57_iter1.md`, werdykt ZALICZONY / NIE ZALICZONY z listą B/P. NIE ZALICZONY → R57‑A iteracja, max 3.

## 4. Sesja R57‑C — dokumenty i zamówienie (Opus 5.5)

1. `Zakupy i druk`: wiersz „płytki okrągłe W + P (test skanera)” z SHA, objętością, PA12 biały mat, ±0,3 mm; „Specyfikacja zamówienia” rozszerzona.
2. Plan wdrożenia v2: pomiar #12 + wariant okrągły (po co, kiedy obowiązuje); „Budowa ramki — decyzje i zamienniki”: wpis o wkładce/pokrywce dla okrągłej (do zrobienia dopiero po teście).
3. `narzedzia/zbuduj_pakiet_R57.sh` → `Ramki_pakiet/` (nowe pliki, stare bez zmian), SHA256SUMS, README.
4. Drive QC: tylko NOWE pliki (ZIP R57 + SHA + instrukcja), nic nie usuwać, nic nie nadpisywać (zasada właściciela).
5. Rejestr: `00_NADZOR_STAN.md` wpis R57.

## 5. Sesja P1 — program: fundament i naprawa (Opus 5.5)

Wspólne reguły P1–P3: praca w `stanowisko/` (repo git); każda sesja kończy commitem; nic nie kasować z `archiwum/` i `sesje_2026-10-31/`; przed zmianą modułu czytać `opisy_modulow/<modul>.md`, po zmianie aktualizować „Założenia i granice”; uruchomienie `set PYTHONUTF8=1`, `py -3.12 -m pytest testy -q`; progi tylko z `ustawienia.toml`; identyfikator projektu w JSON/logach = skrót SHA‑256 + numer zęba, nie nazwa folderu; raport `stanowisko/raporty/<sesja>_<data>.md`.

1. Zamrozić: `git tag fundament-2026-11-02` + kopia `stanowisko/` (bez `dane/`) do `archiwum/stanowisko_fundament_2026-11-02/`.
2. Naprawić wg `sesje_2026-10-31/kod_a_stanowisko/znaleziska.md`: B1/B1b (`osadz_w_gniezdzie`: dx, dy przed pętlą, rynienka z pętlą, asercja 0 wierzchołków poza stożkiem), B2 (`najblizsze_gniazdo` po obrysie, `None` poza), B3 (`ustawienia.py` z tomllib, usunąć duplikaty progów), B4 (etykieta z `uklad`), S1/S2/S3/S9 (walidacje, `--nadpisz`).
3. `testy_edge` → XPASS → zdjąć `xfail`, przenieść do `testy/`.
4. `requirements.txt` z wersjami; README `py -3.12`; `uklad.py` toleruje `shape: round` w JSON (pole opcjonalne, domyślnie `square`).
5. Gotowe = pytest zielony, 0 xfail dla B‑błędów, toml czytany, commit, raport.

## 6. Sesja P2 — porównanie STL z folderu na pulpicie (Fable 5.1)

Warunek: P1 gotowe; `<PC>\Desktop\Prace_test\<zlecenie>\*.stl` (≥ 30 prawdziwych STL z exocad, w tym ≥ 2 mosty).

1. Orientacja prawdziwych STL w `synth` (30 plików, rzut z góry); w razie potrzeby `--orientacja`.
2. ≥ 20 sztucznych skanów (wieczorna ×1,22, poranna ×1,0, różne seedy, drgnięcie 10 %) z projektów z pulpitu.
3. `stanowisko/plate.py` wg `opisy_modulow/plate.md`: ICP na 3 stożkach, numer z dołków (z opcją `--numer`, gdy dołki niewidoczne), cięcie na gniazda, puste / podwójne / poza gniazdem.
4. `stanowisko/match.py` wg `opisy_modulow/match.md`: filtr objętość/wymiary → FPFH + RANSAC → ICP → ranking z pewnością; pula = folder z pulpitu; `--wspolczynnik`.
5. CLI `python -m stanowisko.porownaj --skan <stl> --projekty <folder> --plytka wieczorna|poranna|okragla_wieczorna|okragla_poranna [--wspolczynnik 1.22] [--numer N]` → tabela gniazdo → projekt → pewność, PNG mapy, JSON wyniku. Metryki na prawdzie: wyrównanie < 0,05 mm, numer 100 %, fragment w swoim gnieździe 100 %, top‑1 ≥ 95 %, top‑2 ≥ 99 % na ≥ 200 fragmentach. Testy `test_plate.py`, `test_match.py`; commit; raport.

## 7. Sesja P3a — ubytki i okno aplikacji, bez skanera (Fable 5.1)

Warunek: P2 gotowe (silnik plate + match, zestaw sztucznych skanów z `Prace_test`). Decyzja właściciela 2.11: P3 rozdzielone, żeby okno i ubytki były gotowe PRZED dostawą skanera; na dzień skanu zostaje tylko strojenie (P3b).

1. `stanowisko/inspect.py` wg `opisy_modulow/inspect.md` (mapa odchyłek skan–projekt, ubytki ≥ 0,08 mm pod powierzchnią, ø0,2–1,5, pas brzegu 1,5 mm, ostra krawędź, odrzucenie gładkich poprawek > 2 mm, wykrycie podwójnej powierzchni); test na ≥ 100 ubytkach syntetycznych z prawdy: wykryte ≥ 90 %, fałszywe ≤ 10 %, drgnięcie 100 %. Progi w `ustawienia.toml [inspect]`.
2. Pełny łańcuch plate → match → inspect w CLI `porownaj` (gniazda czerwone = ubytek) i w JSON wyniku; metryki na zestawie P2.
1a. **Zasady inspect przeciw fałszywym alarmom (właściciel 2.11: „[cytat usuniety]”):** (1) ubytek liczony tylko tam, gdzie skan ISTNIEJE (punkt skanu ≥ 0,08 mm pod powierzchnią projektu); brak punktów = „[cytat usuniety]”, nigdy „[cytat usuniety]”; (2) ubytek musi mieć ostrą krawędź na obwodzie plamy — plamy bez krawędzi (łagodny wzrost odchyłki do końca danych, jak przy dziurze w skanie) odrzucane; (3) ø ≤ 1,5 mm — większe różnice to złe dopasowanie, poprawka ręczna lub brak danych → osobny status „[cytat usuniety]”, nie czerwone; (4) najpierw jakość dopasowania: pokrycie poniżej progu `[match]` → gniazdo żółte „[cytat usuniety]”, ubytki nieliczone (praca bokiem wpada tutaj); (5) ubytki tylko w pasie 1,5 mm od brzegu i na krawędziach. Metryki osobno dla prac ułożonych dobrze, bokiem i częściowo zeskanowanych; jeśli „[cytat usuniety]” daje fałszywe alarmy, podnosić próg pokrycia, nie próg ubytku. Progi startowe z planu, strojenie w P3b na prawdziwych skanach z pracami całymi i celowo ukruszonymi.
1b. **Druga metoda: ciągłość linii brzegu (właściciel 2.11: „[cytat usuniety]”).** Obok mapy odchyłek zaimplementować detektor krawędzi: wyciąć ze skanu i z projektu linię brzegu korony (obwód przy styku z gniazdem, pas 0–1,5 mm), porównać ciągłość: wcięcie w linii skanu ≥ 0,2 mm względem projektu = ukruszenie; brak odcinka linii (zasłonięcie, bokiem) = „[cytat usuniety]”, nie alarm. Decyzja końcowa: czerwone, gdy obie metody się zgadzają lub wcięcie brzegu jest wyraźne (≥ 0,4 mm); żółte „[cytat usuniety]”, gdy tylko jedna. W raporcie metryki osobno dla każdej metody i dla kombinacji. Na później (po decyzji): porównanie z poprzednim skanem tej samej pracy; uczenie na decyzjach technika (zapisywanych od pierwszego dnia).
2a. **Scenariusze trudne (pytanie właściciela 2.11):** w generatorze opcje `--bokiem p` (praca położona bokiem lub do góry nogami, zamiast brzegiem do góry) i `--pokrycie p` (losowe wycięcie 30–60 % powierzchni skanu — zasłonięcia, spieczona cyrkonia); zestaw ≥ 10 skanów z tymi opcjami; raport: trafność top‑1 i odsetek „[cytat usuniety]” osobno dla prac ułożonych dobrze, bokiem i częściowo zeskanowanych. Program ma dawać „[cytat usuniety]” (żółte), nie fałszywie „[cytat usuniety]”.
3. Foldery `modele_plytek/okragla_wieczorna/`, `okragla_poranna/` z JSON + STL z R57 (jeśli P2 ich nie dodało); przełącznik `--plytka` dla 4 wariantów.
4. README: jak postawić program na laptopie firmowym (Python 3.12, `pip install -r requirements.txt`, foldery, `uruchom_okno.bat`) i jak przeprowadzić test skanera bez Excela i SharePointa.
5. Commit; raport `stanowisko/raporty/P3a_<data>.md`.
6. **Proste okno (decyzja właściciela 2.11: „[cytat usuniety]”)** — `stanowisko/ui_test.py` w PySide6, pierwszy krok modułu `ui` z planu wdrożenia, na tym samym silniku co CLI: wybór pliku skanu (STL), wybór folderu projektów, wybór płytki (4 warianty) i współczynnika, przycisk „[cytat usuniety]”; mapa płytki z gniazdami w kolorach (zielone = rozpoznane, żółte = dwuznaczne, szare = bez projektu, czerwone = ubytek); klik w gniazdo → podgląd 3D pracy z mapą odchyłek (lub PNG, jeśli 3D w Qt okaże się za drogie — opisać); tabela wyników; zapis JSON/PNG. Uruchomienie jednym plikiem `uruchom_okno.bat`. Bez Excela, SharePointa, ramki, obserwacji folderu — to przyszłe moduły. Czas: ok. 1 dzień dodatkowo; technik ma obsłużyć test skanera bez komendy w konsoli.

## 7b. Sesja P3b — pierwszy prawdziwy skan (Fable 5.1, dzień testu skanera)

Warunek: P3a gotowe; STL z Aidite dla prawdziwych płytek (kwadrat n1/n4 i okrągła n8/n9) z prawdziwymi pracami; folder projektów tych samych prac.

1. Pomiar na prawdziwym skanie: σ szumu na płaskiej części płytki, widoczność 3 stożków, widoczność dołków kodu (kwadrat vs okrągła — dołki kwadratu leżą na promieniu 54–58, poza kołem ø100), pokrycie powierzchni prac (zielone / spieczone), czy rogi kwadratu zacieniają gniazda skrajne; z tego odczyt faktycznego pola skanowania. Wpis do `ustawienia.toml`.
2. `porownaj` (okno i CLI) na prawdziwym skanie vs ręczne przypisanie prac; trafność i wykryte ubytki per płytka (kwadrat / okrągła).
3. Strojenie progów `[match]` i `[inspect]` na prawdziwym szumie; ponowny przebieg testów syntetycznych, żeby nic się nie zepsuło.
4. Raport `stanowisko/raporty/P3b_<data>.md`: werdykt „idziemy / nie idziemy” z liczbami, rekomendacja kwadrat / okrągła (→ ewentualne R58), lista rzeczy do poprawy przed modułami codziennej pracy. Commit.

## 8. Po wszystkim

- Testy udane: tag `wlasciwy-<data>` + kopia `archiwum/stanowisko_wlasciwy_<data>/`; dalsze moduły (catalog, session, ui, indicate, excel, scanner) na tym stanie; jeśli wygrała okrągła: R58 wkładka + pokrywka okrągła (wykonawca Fable 5.1, recenzja Fable 5.1 fresh).
- Testy nieudane: fundament nienaruszony (`fundament-2026-11-02`), wnioski w raportach.
