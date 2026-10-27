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
- `ubytki.py`:
  1. korekta sztywnego niedopasowania T: liniowe dopasowanie d ~ n.t + (p x n).w + c (jak krok ICP
     point-to-plane) z odrzucaniem punktow odstajacych (> 2,5 sigma reszty, 3 iteracje); ukruszenia i
     poprawki odpadaja jako odstajace. Usuwa przesuniecie T rzedu 0,05 mm / 0,1 st.;
  2. wygladzanie w mm: jadro gaussowskie po pozycjach (sigma = promien / 2) w promieniu 1,5 x
     max(`skaner.gestosc_mm`, mediana krawedzi skanu) - czulosc nie zalezy od podzialu siatki;
  3. nasiona d <= -`min_glebokosc_mm`, skladowe spojne grafu par punktow w promieniu wygladzania
     (>= 4 punkty); obszar ubytku = skladowa d <= -poziom zawierajaca nasiona (poziom = max(0,25 x
     glebokosc szczytowa, 3 sigma szumu, 0,02 mm));
  4. stromosc obwodu (mm/mm) = (p2 - p1) / (r1 - r2), r = promien obszaru na poziomie p, p1 = 0,3 g,
     p2 = 0,7 g; klasyfikacja.
- `drgniecie.py` - podwojna powierzchnia: udzial wierzcholkow, ktore maja pare w odleglosci <= 2 x
  `drgniecie_odleglosc_mm`, niepolaczona krawedzia siatki, z |d1 - d2| >= `drgniecie_odleglosc_mm` -
  0,02 (d wygladzone po 1-pierscieniu siatki: warstwy nie maja wspolnych krawedzi), >=
  `drgniecie_udzial`. Sztywne przesuniecie T zmienia d lagodnie, wiec nie daje par (pomiar: drgniecie
  0,30-0,49, bez drgniecia <= 0,07 takze przy T zaburzonym o 0,05 mm i szumie 0,04).
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
| `ubytki.ostrosc_min` | min. stromosc obwodu ukruszenia, mm/mm (ukruszenia >= 0,4, poprawki <= 0,12) |
| `ubytki.pas_brzegu_mm` | pas od krzywej brzegu, w ktorym ukruszenie jest alarmem |
| `ubytki.poprawka_min_srednica_mm` | gladkie zaglebienie szersze = poprawka |
| `ubytki.drgniecie_udzial`, `ubytki.drgniecie_odleglosc_mm` | prog udzialu i srodek pasma drgniecia |
| `skaner.gestosc_mm` | promien wygladzania (1,5 x max(gestosc, odstep punktow skanu)) |

Stale algorytmu w kodzie (nie progi stanowiska): `PROMIEN_WYGLADZANIA`, `MIN_PUNKTOW`,
`UDZIAL_POZIOMU`, `SIGMY_SZUMU`, `MIN_POZIOM_MM`, `DOLNY_POZIOM`, `GORNY_POZIOM`, `ITERACJE_KOREKTY`,
`PROG_ODRZUCENIA`, `CO_KTORY_PUNKT_KOREKTY` (ubytki.py), `PROMIEN_PARY`, `ZAPAS_ROZNICY_MM`
(drgniecie.py), `PAS_Z_BRZEGU_MM` (odchylki.py).

## Wyjscie

- `Mapa(punkty (N,3), odleglosci (N,), normalne_projektu (N,3), przy_brzegu (N,) bool, sciany)` -
  `sciany` = sciany fragmentu (krawedzie dla drgniecia, odstep punktow), opcjonalne. `odleglosci` bez
  korekty niedopasowania (korekta tylko wewnatrz `szukaj_ubytkow`).
- `WynikInspekcji(ubytki, poprawki, inne, drgniecie, mapa)`; `Ubytek(srodek, srednica_mm,
  glebokosc_mm, przy_brzegu, stromosc)` w ukladzie fragmentu (mm skanu, ze skala).
  - srodek = srednia punktow obszaru wazona glebokoscia; glebokosc = 10. percentyl wygladzonego d
    (wartosc dodatnia); srednica = 2 x (90. percentyl odleglosci od srodka) / sqrt(0,9); dla
    gladkich zaglebien przeliczona z profilu gaussowskiego (4 sigma).
  - ostra krawedz = stromosc >= `ostrosc_min` (plytkie szerokie ukruszenia 1,2 / 0,10 mm: >= 0,41).
  - `ubytki`: ostra, srednica w [min; max], najglebszy punkt przy brzegu; `poprawki`: gladka,
    srednica > `poprawka_min_srednica_mm`; reszta -> `inne`.
- Przy drgnieciu `sprawdz` zwraca `drgniecie=True` i puste listy (skan do powtorzenia).
- `Porownanie(wykryte, pominiete, falszywe, pary)` - pary (Ubytek wykryty, UbytekPrawda); przypisanie
  zachlanne po rosnacej odleglosci srodkow, jeden do jednego; liczone tylko prawdy "ukruszenie",
  srodki prawdy przenoszone przez T_prawdy.

## Ograniczenia

- Dokladnosc zalezy od T z modulu `match`. Sztywny blad T do ok. 0,05 mm / 0,1 st. jest korygowany
  (test 17: 60/60); wiekszy albo niesztywny (deformacja) nie jest.
- Male ubytki (0,2-0,3 mm) na siatce 0,08 mm bez zageszczenia: ok. 2/3 wykrytych (test 20), bo
  wygladzanie 0,12 mm jest porownywalne z ubytkiem; mierzona srednica < 0,2 mm -> `inne`.
- Wydajnosc i watki: `sprawdz` korony ok. 0,3 s szeregowo (mapa 0,09, sasiedztwo open3d 0,12, reszta
  numpy). W wielu watkach skaluje sie slabo: 16 prac na 1 / 2 / 4 / 8 watkach = 4,9 / 3,9 / 3,4 / 3,3 s
  (GIL w numpy i wlasne watki open3d). Degradacji RaycastingScene z recenzji (0,04 -> 3-8 s) w gosciu
  nie zaobserwowano: 30 kolejnych zapytan 0,08-0,10 s, przy 8 watkach max 0,55 s. Jesli wystapi na
  laptopie stanowiska - ograniczyc afinicznosc procesu do 4 rdzeni (bez obejscia w kodzie).
- Skan nie musi byc wodoszczelny (dziury, T-junctions). Krawedzie dziur nie daja ujemnych d, wiec nie
  sa osobno pomijane; obszar bez danych jest po prostu niewidoczny (ubytek w dziurze = pominiety).
- Drgniecie przy szumie 0,04 nie bylo testowane (pasmo zaczyna sie od 0,04 mm).

## Kryterium "dziala"

- `tests/test_inspect.py` testy 1-15 i 17-20 zielone: `python -m pytest -q -m "not wolne" tests/test_inspect.py`.
- Test 16 (`-m wolne -k metryki_pelne -s`) drukuje tabele wykryte / pominiete / falszywe per klasa
  srednicy i sigma; klasy >= 0,3 mm przy sigma 0,02 wykryte >= 85 %.
- `sprawdz` jednej korony (krok 0,1) <= 3 s, `mapa_odchylek` <= 1,5 s (pomiar ok. 0,3 s / 0,08 s).
