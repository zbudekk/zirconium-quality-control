# qc.inspect - inspekcja ukruszen (skan vs projekt)

## Co robi

Porownuje fragment skanu jednej pracy z jej projektem po dopasowaniu (macierz T z modulu `match`) i
wskazuje ukruszenia przy brzegu, poprawki (szlifowanie) i inne zaglebienia oraz wykrywa drgniecie
skanera.

- `odchylki.py` - projekt przeniesiony przez T do open3d `RaycastingScene`, `compute_closest_points` dla
  wierzcholkow fragmentu; odleglosc ze znakiem z normalnej najblizszego trojkata (jedna sciezka dla
  bryl zamknietych, mostow i skanow z dziurami; zgodna ze znakiem `compute_signed_distance` dla
  zamknietej korony). Ujemna = pod powierzchnia projektu = brak materialu. Brzeg = wierzcholki projektu z
  |z| < 0,3 mm (uklad projektu) po T; `przy_brzegu` = odleglosc od nich <= `pas_brzegu_mm` (open3d nns).
- `ubytki.py` - wygladzanie d srednia po 1-pierscieniu sasiadow w siatce fragmentu (bez scian: 8
  najblizszych w promieniu 1,5 x `skaner.gestosc_mm`), nasiona d <= -`min_glebokosc_mm`, skladowe
  spojne po krawedziach siatki (>= 4 punkty), obszar ubytku = skladowa d <= -poziom zawierajaca nasiona
  (poziom = max(0,25 x glebokosc szczytowa, 3 sigma szumu, 0,02 mm)), klasyfikacja.
- `drgniecie.py` - udzial wierzcholkow z wygladzonym |d| w [`drgniecie_odleglosc_mm` - 0,04; 0,16]
  >= `drgniecie_udzial`. Wygladzanie po krawedziach siatki nie miesza kopii platu z oryginalem (kopia
  nie ma wspolnych krawedzi), a szum spada ok. 2,5 x.
- `metryki.py` - porownanie z prawda syntetycznego skanu (wykryte / pominiete / falszywe).

Tylko numpy i open3d; funkcje bez stanu globalnego (osobna `RaycastingScene` na wywolanie) - mozna
wolac z wielu watkow.

## Wejscie

- `mapa_odchylek(fragment, projekt, T_projekt_do_fragmentu, ustawienia)` - `trimesh.Trimesh` fragmentu
  (uklad skanu, mm), projekt w swoim ukladzie (brzeg w z ~ 0), T 4x4 projekt -> fragment (moze
  zawierac skale spiekania).
- `szukaj_ubytkow(mapa, ustawienia)`, `wykryj_drgniecie(fragment, projekt, T, ustawienia)`,
  `sprawdz(fragment, projekt, T, ustawienia)`.
- `metryki.porownaj(wynik, prawda, T_prawdy, tolerancja_mm=0.5)` - `PrawdaPracy` z `qc.syntetyka`.

Progi z `ustawienia.toml`:

| Klucz | Znaczenie |
|---|---|
| `ubytki.min_glebokosc_mm` | prog nasion (wygladzone d <= -prog) |
| `ubytki.min_srednica_mm`, `ubytki.max_srednica_mm` | zakres srednicy ukruszenia |
| `ubytki.pas_brzegu_mm` | pas od krzywej brzegu, w ktorym ukruszenie jest alarmem |
| `ubytki.poprawka_min_srednica_mm` | gladkie zaglebienie szersze = poprawka |
| `ubytki.drgniecie_udzial`, `ubytki.drgniecie_odleglosc_mm` | prog udzialu i srodek pasma drgniecia |
| `skaner.gestosc_mm` | promien sasiedztwa, gdy mapa nie ma scian |

Stale algorytmu w kodzie (nie progi stanowiska): `PROMIEN_WYGLADZANIA`, `MIN_PUNKTOW`,
`UDZIAL_POZIOMU`, `SIGMY_SZUMU`, `MIN_POZIOM_MM`, `OSTROSC` (ubytki.py), `ZAPAS_PASMA_MM`,
`GORA_PASMA_MM` (drgniecie.py), `PAS_Z_BRZEGU_MM` (odchylki.py).

## Wyjscie

- `Mapa(punkty (N,3), odleglosci (N,), normalne_projektu (N,3), przy_brzegu (N,) bool, sciany)` -
  `sciany` = sciany fragmentu (sasiedztwo), opcjonalne.
- `WynikInspekcji(ubytki, poprawki, inne, drgniecie, mapa)`; `Ubytek(srodek, srednica_mm,
  glebokosc_mm, przy_brzegu)` w ukladzie fragmentu (mm skanu, ze skala).
  - srodek = srednia punktow obszaru wazona glebokoscia; glebokosc = 10. percentyl wygladzonego d
    (wartosc dodatnia); srednica = 2 x (90. percentyl odleglosci od srodka) / sqrt(0,9); dla
    gladkich zaglebien przeliczona z profilu gaussowskiego (4 sigma).
  - ostra krawedz = glebokosc >= 0,13 x srednica (ukruszenia >= ok. 0,18, poprawki <= ok. 0,1).
  - `ubytki`: ostra, srednica w [min; max], najglebszy punkt przy brzegu; `poprawki`: gladka,
    srednica > `poprawka_min_srednica_mm`; reszta -> `inne`.
- Przy drgnieciu `sprawdz` zwraca `drgniecie=True` i puste listy (skan do powtorzenia).
- `Porownanie(wykryte, pominiete, falszywe, pary)` - pary (Ubytek wykryty, UbytekPrawda); przypisanie
  zachlanne po rosnacej odleglosci srodkow, jeden do jednego; liczone tylko prawdy "ukruszenie",
  srodki prawdy przenoszone przez T_prawdy.

## Ograniczenia

- Dokladnosc zalezy od T z modulu `match`; testy uzywaja T z prawdy (dopasowanie idealne). Blad
  dopasowania ~0,05 mm przesuwa d i zmniejsza zapas do progu 0,08 mm.
- Skan nie musi byc wodoszczelny (dziury, T-junctions). Krawedzie dziur nie daja ujemnych d, wiec nie
  sa osobno pomijane; obszar bez danych jest po prostu niewidoczny (ubytek w dziurze = pominiety).
- Drgniecie przy szumie 0,04 nie bylo testowane (pasmo zaczyna sie od 0,04 mm).

## Kryterium "dziala"

- `tests/test_inspect.py` testy 1-15 zielone: `python -m pytest -q -m "not wolne" tests/test_inspect.py`.
- Test 16 (`-m wolne -k metryki_pelne -s`) drukuje tabele wykryte / pominiete / falszywe per klasa
  srednicy i sigma; klasy >= 0,3 mm przy sigma 0,02 wykryte >= 85 %.
- `sprawdz` jednej korony (krok 0,1) <= 3 s, `mapa_odchylek` <= 1,5 s (pomiar ok. 0,15 s / 0,08 s).
