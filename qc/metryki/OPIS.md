# qc.metryki - metryki odbiorcze calego lancucha (jedno polecenie, jedna strona)

## Co robi

Sekcja 14 planu: jedno polecenie daje jedna strone wynikow. `python -m qc.metryki` generuje dane
syntetyczne (`qc.syntetyka`), uruchamia caly lancuch stanowiska i porownuje go z prawda:

1. baza projektow: `prace.pula_projektow(n, ziarno)` + mosty 3/4-punktowe (`prace.most`);
2. plytki wg ukladow z ustawien (`[plytki] wieczorna / poranna`, pliki `modele/uklad_gniazd_*.json`):
   `plytka.rozmiesc` + `plytka.skan_plytki` (T losowa, szum sigma plytki). Wieczor: k 1,20-1,25, kazda
   praca 1-2 ukruszenia (srednica rowno z klas 0,2-0,3 / 0,3-0,4 / 0,4-0,6, glebokosc losowa ze
   skanu), w trybie pelnym co 6. praca takze poprawka. Rano: k = 1, cala plytka skanowana z gory (bez
   scian o normalnej z < -0,3, jak `test_plate::test_skan_z_gory`), bez ubytkow;
3. pula na plytke (`WpisPuli`, cechy `qc.catalog.cechy.policz` raz na projekt): wieczor = prace plytki z k
   z prawdy + wabiki spoza plytki z losowym k; rano = wszystkie projekty bazy z k = 1 (<= 60);
4. `plate.analizuj` -> numer, wyrownanie, fragmenty; fragmenty "praca" i "podwojne" ->
   `match.dopasuj(fragment.siatka, pula, u, tryb)`; wieczorem przy pewnosci "pewny" ->
   `inspect.sprawdz(fragment.siatka, projekt top-1, T_projekt_do_fragmentu, u)` ->
   `inspect.metryki.porownaj` z prawda przeniesiona do ukladu fragmentu
   (`T_skan_do_plytki @ T_projekt_do_skanu`, tolerancja srodka 0,5 mm);
5. przypisanie fragmentu do prawdy po numerze gniazda. Fragmenty jednej plytki licza sie w 4 watkach
   (`WATKI`; `match` i `inspect` bez stanu globalnego; `pamiec` dopasuj osobna na watek i plytke).

Pamiec (pelne, 54 projekty, pula rano <= 60): szczyt ok. 2,5 GB (commit procesu). Bez trzech zabiegow bylo
7,2 GB: (a) po `policz` cech i po kazdej plytce czyszczony cache trimesh siatek projektow (ok. 35 MB na
projekt, siatki wspolne dla pul wszystkich plytek), (b) skan plytki zwalniany po cieciu, przed dopasowaniem,
(c) `gc.collect()` po fazie watkow i po plytce (cykle referencji w danych dopasowania, ok. 1 GB na plytke).
Plytki po kolei, bez generowania nastepnej w tle (z tym szczyt 5,2 GB).

Wszystko deterministyczne dla danego ziarna (ziarna plytek = ziarno x 1000 + numer).

Tryby:

| Tryb | Plytki | Prace | Ubytki | Sigma |
|---|---|---|---|---|
| `szybko` | wieczorne nr 1, 2 (6 + 1), poranna nr 4 (8 + 1) | 23 | ok. 20 | 0,02 / 0,03 |
| `pelne` | wieczorne 1-3 (24 + 2, 18 + 2 z "podwojne", 14 + 2), poranne 4-6 (35 + 2, 30 + 2 z "poza_gniazdem", 22 + 2) | 157, w gniazdach "praca" 152 (ok. 190 fragmentow z pustymi) | ok. 100 | 0,02 / 0,03 / 0,04 |

## Wejscie

- `python -m qc.metryki [--szybko | --pelne] [--ziarno N] [--wyjscie plik.json] [--ustawienia plik.toml]`
  (domyslnie `--pelne`, ziarno 1, ustawienia jak `qc.ustawienia.wczytaj`).
- API: `policz(ustawienia, tryb="szybko"|"pelne", ziarno=1) -> dict`, `ocen(dict) -> (kod, nazwy)`.
- Progi wykrywania i dopasowania: z pliku ustawien (jak na stanowisku); metryki ich nie zmieniaja.

## Wyjscie

Strona tekstowa (<= 60 linii) i JSON z tymi samymi polami:

- `plytka`: `blad_wyrownania_max_mm` / `_sredni_mm` (max przesuniecie narozy plytki miedzy T a prawda),
  `numery {ok, zle, brak}`, `fragmenty {praca, puste, podwojne, poza_gniazdem} x {wynik, prawda}`,
  `gniazda`, `gniazda_zgodne`, `bledy` (BladPlytki);
- `identyfikacja`: `wieczor`, `rano`, `razem` - `fragmenty` (tylko "praca"), `top1`, `top2` (projekt_id
  prawdy na 1. / w 2 pierwszych), `pewny`, `dwuznaczny`, `brak`, `falszywe_pewny` (pewny na zlym
  projekcie), `udzial_top1`, `udzial_top2`; `podwojne` - fragmenty "podwojne" i top-1 rowny jednej z prac
  gniazda (poza statystyka top-1);
- `ubytki`: `klasy` (srednica prawdy; falszywe wg srednicy zmierzonej) i `sigma`, kazde `wykryte`,
  `pominiete`, `falszywe`, `udzial_wykrytych`; `udzial_wykrytych_od_0_3` (klasy 0,3-0,4 i 0,4-0,6),
  `prace_z_falszywym_alarmem` i `udzial_...` (na pracach sprawdzonych), `sprawdzone_fragmenty`
  (= wieczorne "pewny"), `sprawdzone_rano` (zawsze 0), `ubytki_bez_inspekcji` (ukruszenia prac bez
  "pewny" - operator sprawdza je recznie, nie wchodza do udzialow);
- `czasy`: `na_plytke_s` (analizuj), `na_fragment_s` (dopasuj + sprawdz, czas watku), `calosc_s` (z
  generacja danych);
- `wersja` (qc), `ziarno`, `tryb`, `progi_odbiorcze`, `kod`, `ponizej_progu`.

Kod wyjscia: 0 = wszystkie metryki odbiorcze spelnione; 3 = co najmniej jedna ponizej progu (lista na
stronie i w `ponizej_progu`); 2 = blad ustawien; inny niezerowy = wyjatek programu.

### Progi odbiorcze vs progi ustawien

`PROGI_ODBIORCZE` w `qc/metryki/__init__.py` to kryteria odbioru z sekcji 14 planu, nie parametry
stanowiska: top-1 >= 0,85, wykryte (klasy >= 0,3 mm) >= 0,80, prace z falszywym alarmem <= 0,15.
Wartosc rowna progowi zalicza. Nie stroi sie ich pod wynik - zmiana tylko po zmianie planu. Progi
wykrywania (`[dopasowanie]`, `[ubytki]`, `[plytka]` w `ustawienia.toml`) to strojenie stanowiska;
`qc.metryki` mierzy ich skutek.

## Kryterium "dziala"

- `python -m pytest -q tests/test_metryki.py -m "not wolne"` zielone (testy 1-5, <= 120 s): klucze i
  udzialy, CLI (strona <= 60 linii, JSON, kod 0/3), progi odbiorcze, spojnosc lancucha, szybko: top-1 >= 0,9,
  wykryte (>= 0,3 mm) >= 0,85, numery 3/3, kod 0.
- `-m wolne -k metryki`: `test_pelne` - tryb pelny bez wyjatku, kod 0, <= 20 min.
- CI: `.github/workflows/metryki.yml` (reczny i niedzielny przebieg pelny, artefakt `metryki.json`).

## Ograniczenia

- Dane syntetyczne: plytka bez szumu (blad wyrownania ~0), skaner idealnie gesty; na prawdziwych skanach
  liczby beda gorsze. Odbior wg sekcji 14 wymaga powtorzenia na skanach stanowiska.
- Ten sam projekt moze lezec na plytce dwa razy (rozmiesc powtarza projekty przy braku pasujacych):
  dwa wpisy puli o tym samym projekt_id i roznym k czesto daja "dwuznaczny" przy poprawnym top-1 (pelne: 17 prac wieczornych z powtorzonym
  projektem, 9 wynikow "dwuznaczny", 0 falszywych "pewny").
- Fragmenty "poza_gniazdem" nie sa identyfikowane (operator poprawia polozenie pracy).
