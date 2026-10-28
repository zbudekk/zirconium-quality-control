# qc.metryki - metryki odbiorcze calego lancucha (jedno polecenie, jedna strona)

## Co robi

Sekcja 14 planu: jedno polecenie daje jedna strone wynikow. `python -m qc.metryki` generuje dane
syntetyczne (`qc.syntetyka`), uruchamia caly lancuch stanowiska i porownuje go z prawda:

1. baza projektow: `prace.pula_projektow(n, ziarno)` + male korony `prace.korona(z, "siekacz")` o srednicy
   <= `MAX_MALA_MM` 6,3 (z = 10**6 + ziarno x 10 000 + i, wieksze odrzucane; ziarna z poza ziarnami
   `pula_projektow` - wczesniej przy `--ziarno 0` mala korona z = 2 byla korona-03 pod innym id) + mosty 3/4-punktowe (`prace.most`). Bez
   malych koron `rozmiesc` powtarzal siekacze w najmniejszych gniazdach (7,5 mm rano, 9,0 mm wieczorem):
   w pelnym rano 51 z 93 prac to kopie 7 projektow, a 9 wynikow "dwuznaczny" wieczorem = kopie. Z malymi
   koronami (szybko 10, pelne 26): 0 powtorek w obu trybach (`powtorzenia(tryb, ziarno)`);
2. plytki wg ukladow z ustawien (`[plytki] wieczorna / poranna`, pliki `modele/uklad_gniazd_*.json`):
   `plytka.rozmiesc` + `plytka.skan_plytki` (T losowa, szum sigma plytki). Wieczor: k 1,20-1,25, kazda
   praca 1-2 ukruszenia (srednica rowno z klas 0,2-0,3 / 0,3-0,4 / 0,4-0,6, glebokosc losowa ze
   skanu), w trybie pelnym co 6. praca takze poprawka. Rano: k = 1, cala plytka skanowana z gory (bez
   scian o normalnej z < -0,3, jak `test_plate::test_skan_z_gory`), bez ubytkow;
3. pula na plytke (`WpisPuli`, cechy `qc.catalog.cechy.policz` raz na projekt): wieczor = prace plytki z k
   z prawdy + wabiki spoza plytki z losowym k; rano = projekty plytki + losowe inne z bazy, razem `max_pula`
   (pelne 60, szybko 30), k = 1;
4. `plate.analizuj` -> numer, wyrownanie, fragmenty; fragmenty "praca" i "podwojne" ->
   `match.dopasuj(fragment.siatka, pula, u, tryb)`; wieczorem przy pewnosci "pewny" (i pracy w prawdzie) ->
   `inspect.sprawdz(fragment.siatka, projekt top-1, T_projekt_do_fragmentu, u)` ->
   `inspect.metryki.porownaj` z prawda przeniesiona do ukladu fragmentu ZMIERZONYM wyrownaniem
   (`wp.wyrownanie.T_skan_do_plytki @ T_projekt_do_skanu`, tolerancja srodka 0,5 mm) - jak na stanowisku;
5. rozliczenie po pracach z PRAWDY w gniazdach: praca "praca" bez fragmentu "praca" z plate = "brak";
   fragment "praca" bez pracy w prawdzie (fantom w pustym gniezdzie, gniazdo "podwojne" uznane za "praca")
   = nietrafiony. Mianownik top-1 = prace z prawdy + `fragmenty_bez_prawdy`. Gniazda z praca "podwojne" i prace "poza_gniazdem" sa
   poza mianownikiem (plate je zglasza, operator poprawia ulozenie i skanuje ponownie). Fragmenty jednej
   plytki licza sie w `WATKI` = 4 watkach (`match` i `inspect` bez stanu globalnego; `pamiec` dopasuj
   osobna na watek i plytke).

Wszystko deterministyczne dla danego ziarna (ziarna plytek = ziarno x 1000 + numer).

### Watki

Zmierzone w recenzji: na 24-watkowym CPU bez ograniczenia afinicznosci fixture szybko nie konczyla sie w
9 min, z maska 4 rdzeni ok. 100 s. Przyczyna nieustalona (prawdopodobnie nadsubskrypcja watkow open3d przy
`WATKI` = 4 watkach wolajacych; `OMP_NUM_THREADS` nie zmienial liczby watkow - open3d na Windows uzywa tez
TBB, a `os.cpu_count()` nie widzi maski). Do zbadania na laptopie stanowiska; `qc.metryki` niczego tu nie
ustawia. W gosciu (6 rdzeni) `--szybko` trwa ok. 33 s bez maski.

### Pamiec

Pelne (80 projektow w bazie, pula <= 60): szczyt ok. 2,7 GB (working set procesu). Bez trzech zabiegow bylo
7,2 GB: (a) po `policz` cech i po kazdej plytce czyszczony cache trimesh siatek projektow (ok. 35 MB na
projekt, siatki wspolne dla pul wszystkich plytek), (b) skan plytki zwalniany po cieciu, przed dopasowaniem,
(c) `gc.collect()` po fazie watkow i po plytce (cykle referencji w danych dopasowania, ok. 1 GB na plytke).
Plytki po kolei, bez generowania nastepnej w tle (z tym szczyt 5,2 GB).

Tryby:

| Tryb | Plytki | Prace (wszystkie / w mianowniku) | Ubytki | Sigma |
|---|---|---|---|---|
| `szybko` | wieczorne nr 1, 2 (6 + 1), poranna nr 4 (8 + 1) | 23 / 23 | ok. 20 | 0,02 / 0,03 |
| `pelne` | wieczorne 1-3 (24 + 2, 18 + 2 z "podwojne", 14 + 2), poranne 4-6 (35 + 2, 30 + 2 z "poza_gniazdem", 22 + 2) | 155 / 152 (190 fragmentow z pustymi) | ok. 100 | 0,02 / 0,03 / 0,04 |

## Wejscie

- `python -m qc.metryki [--szybko | --pelne] [--ziarno N] [--wyjscie plik.json] [--ustawienia plik.toml]`
  (domyslnie `--pelne`, ziarno 1, ustawienia jak `qc.ustawienia.wczytaj`).
- API: `policz(ustawienia, tryb="szybko"|"pelne", ziarno=1) -> dict`, `ocen(dict) -> (kod, nazwy)`,
  `powtorzenia(tryb, ziarno, ustawienia=None) -> {"wieczor"/"rano": {powtorzone, prace}}` (bez skanow).
- Progi wykrywania i dopasowania: z pliku ustawien (jak na stanowisku); metryki ich nie zmieniaja.

## Wyjscie

Strona tekstowa (<= 60 linii) i JSON z tymi samymi polami:

- `plytka`: `blad_wyrownania_max_mm` / `_sredni_mm` (max przesuniecie narozy plytki miedzy T a prawda),
  `numery {ok, zle, brak}`, `fragmenty {praca, puste, podwojne, poza_gniazdem} x {wynik, prawda}`,
  `gniazda`, `gniazda_zgodne`, `bledy` (BladPlytki);
- `identyfikacja`: `wieczor`, `rano`, `razem` - `prace` (mianownik: prace "praca" z prawdy), `fragmenty`
  (fragmenty "praca" z plate), `bez_fragmentu`, `fragmenty_bez_prawdy` (fantomy, nietrafione), `top1`,
  `top2` (projekt_id prawdy na 1. / w 2 pierwszych), `pewny` + `dwuznaczny` + `brak` = `prace` +
  `fragmenty_bez_prawdy`, udzialy top-1/top-2 wzgledem tej samej sumy, `falszywe_pewny` (pewny na zlym
  projekcie albo na fragmencie bez pracy), `powtorzone` (kopie projektu na plytce), `udzial_top1`,
  `udzial_top2`; `podwojne` - fragmenty "podwojne" i top-1 rowny jednej z prac gniazda (poza top-1);
- `ubytki`: `klasy` (srednica prawdy; falszywe wg srednicy zmierzonej) i `sigma`, kazde `wykryte`,
  `pominiete`, `falszywe`, `udzial_wykrytych` (na pracach sprawdzonych); `ubytki_bez_inspekcji` i
  `ubytki_bez_inspekcji_klasy` - ukruszenia prac wieczornych bez "pewny" (dwuznaczny / brak / bez
  fragmentu: inspect ich nie widzi); `udzial_wykrytych_od_0_3_wszystkie` = wykryte / (wykryte + pominiete +
  bez inspekcji), klasy >= 0,3 mm - PROG ODBIORCZY; `udzial_wykrytych_od_0_3` - ta sama miara tylko na
  pracach zidentyfikowanych ("pewny"), informacyjnie; `prace_z_falszywym_alarmem` i `udzial_...` (na pracach
  sprawdzonych), `sprawdzone_fragmenty` (= wieczorne "pewny"), `sprawdzone_rano` (zawsze 0);
- `prace`: lista prac z mianownika `{plytka, tryb, gniazdo, projekt_id, pewnosc, top1, ukruszenia,
  sprawdzona}`;
- `czasy`: `na_plytke_s` (analizuj), `na_fragment_s` (dopasuj + sprawdz, czas watku), `calosc_s` (z
  generacja danych);
- `wersja` (qc), `ziarno`, `tryb`, `progi_odbiorcze`, `kod`, `ponizej_progu`.

Kod wyjscia: 0 = wszystkie metryki odbiorcze spelnione; 3 = co najmniej jedna ponizej progu (lista na
stronie i w `ponizej_progu`); 2 = blad ustawien; inny niezerowy = wyjatek programu.

### Progi odbiorcze vs progi ustawien

`PROGI_ODBIORCZE` w `qc/metryki/__init__.py` to kryteria odbioru z sekcji 14 planu, nie parametry
stanowiska: top-1 >= 0,85, wykryte (klasy >= 0,3 mm) >= 0,80, prace z falszywym alarmem <= 0,15.
Wartosc rowna progowi zalicza. Nie stroi sie ich pod wynik - zmiana tylko po zmianie planu. Prog "wykryte"
liczony jest od `udzial_wykrytych_od_0_3_wszystkie`: ukruszenie na pracy, ktorej program nie zidentyfikowal
pewnie, operator musi znalezc sam - dla odbioru to ukruszenie niewykryte (recenzja: stara miara pokazywala
100 % przy 13 z 69 ukruszen poza mianownikiem; uczciwie 81,2 %). Slownik bez nowego pola (JSON sprzed
poprawki): `ocen` liczy je z `ubytki.klasy` i `ubytki_bez_inspekcji_klasy` (albo calej sumy
`ubytki_bez_inspekcji`); bez `klasy` tylko gdy nie ma ukruszen bez inspekcji (wtedy stara miara), inaczej
`KeyError`. Progi wykrywania (`[dopasowanie]`, `[ubytki]`, `[plytka]` w
`ustawienia.toml`) to strojenie stanowiska; `qc.metryki` mierzy ich skutek.

## Kryterium "dziala"

- `python -m pytest -q tests/test_metryki.py -m "not wolne"` zielone (15 testow, zmierzone ok. 86 s, limit
  120 s): klucze i udzialy, CLI (strona <= 60 linii, JSON, kod 0/3), progi odbiorcze (takze od miary
  "wszystkie" i ze slownika bez tego pola), spojnosc lancucha, mianownik top-1 z prawdy i z fantomem,
  ukruszenia bez inspekcji, powtorki <= 10 % w obu trybach, baza bez identycznych siatek (ziarno 0 i 1); szybko: top-1 >= 0,9, wykryte (>= 0,3 mm) >= 0,85, numery 3/3, kod 0.
- `-m wolne -k metryki`: `test_pelne` - tryb pelny bez wyjatku, kod 0, <= 20 min (zmierzone ok. 150 s).
- CI: `.github/workflows/metryki.yml` (reczny i niedzielny przebieg pelny, artefakt `metryki.json`).

## Ograniczenia

- Dane syntetyczne: plytka bez szumu (blad wyrownania ~0), skaner idealnie gesty; na prawdziwych skanach
  liczby beda gorsze. Odbior wg sekcji 14 wymaga powtorzenia na skanach stanowiska.
- Fragmenty "poza_gniazdem" nie sa identyfikowane, a "podwojne" nie wchodza do top-1 ani do ubytkow.
