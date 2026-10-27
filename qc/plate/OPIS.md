# qc.plate - plytka: wyrownanie, numer, ciecie na fragmenty gniazd

## Co robi

Skan plytki z pracami (uklad skanera) przenosi do ukladu plytki z `qc.uklad`, odczytuje numer plytki z
dolkow kodu i tnie skan na fragmenty: jeden na kazde gniazdo (praca, puste, podwojne) i osobne dla
prac lezacych na sciance. Fragmenty ida do `match` / `inspect`.

- `wyrownanie.py`:
  1. plaszczyzna wierzchu: open3d `segment_plane` (0,15 mm, 3 punkty, 500 iteracji) na probce
     150 tys. wierzcholkow. Gdy w skanie jest tez dno plytki (druga plaszczyzna w odleglosci
     `grubosc`), wierzch to ta plaszczyzna, pod ktora jest wiecej punktow zaglebien gniazd
     (0,3-4,5 mm). Bez dna kierunek "w gore" = +Z skanera. Potem dopasowanie najmniejszych kwadratow
     do punktow wierzchu;
  2. znaczniki = wklesle stozki: skupiska punktow na glebokosci znacznika (+-0,6 mm) o rozmiarze
     <= 2 mm. W kole R + 1 mm nic nie moze byc glebiej (gniazda maja dno -4 i otwor), a pierscien
     r w (R + 0,4; R + 1,0) musi lezec na plaszczyznie (+-0,25 mm). Kieszen magnesu od spodu jest
     ignorowana. Trojka A, B, C wybierana po dlugosciach bokow (+-0,5 mm) i orientacji trojkata
     (kat prosty w B);
  3. wstepna T: Kabsch na 3 wierzcholkach stozkow;
  4. ICP point-to-plane (open3d, 0,5 i potem 0,2 mm, 50 iteracji) punktow z otoczen 6 mm znacznikow
     i z pasa plaskiego wierzchu przy krawedziach (|x| albo |y| w 45,5-47,4 mm, poza gniazdami;
     bez dolkow kodu i reliefu) do siatki referencyjnej `qc.syntetyka.plytka.siatka_plytki(uklad,
     None, krok 0,2)` (model plytki stanowiska; cache na uklad, chroniony blokada);
  5. kontrola orientacji: brak materialu w wycieciu D.
- `kod.py` - mediana z wierzcholkow w kole 0,6 x d/2 wokol dolka (z w [-2 x glebokosc; 0,3], bez
  dna, kieszeni i prac); mediana < -0,5 x glebokosc = bit 1; `qc.uklad.numer_z_kodu`.
- `ciecie.py`:
  1. sciany ze srodkiem > 0,25 mm od modelu plytki (z numerem: z dolkami i reliefem) = prace.
     Jedna `RaycastingScene` na wywolanie, sciany wyzej niz model + 0,5 mm bez liczenia odleglosci;
  2. skladowe spojne po wspolnych wierzcholkach (numpy: zaczepianie na minimum + kompresja sciezek).
     Male skladowe (< `min_pole_pracy_mm2`) blizej niz 0,2 mm od duzej sa do niej dolaczane, reszta
     malych odpada;
  3. duze skladowe przecinajace sie (>= 30 krawedzi jednej przebija trojkaty drugiej; czesci mostu
     syntetycznego: 186-230, prace lezace na sobie: 0) = jedna praca;
  4. gniazdo = obrys gorny powiekszony o `margines_gniazda_mm`, w ktorym lezy srodek masy (pole,
     rzut XY). Gdy srodek jest tylko w pasie marginesu, a praca nie siega ponizej -1 mm, to praca
     lezy na sciance;
  5. stan: 0 skladowych = "puste", 1 = "praca", >= 2 = "podwojne"; skladowa poza obrysami =
     "poza_gniazdem" z gniazdem o najblizszym obrysie.

Tylko numpy, trimesh, open3d. Funkcje bez stanu globalnego poza cache siatek referencyjnych pod
blokada, wiec mozna je wolac z wielu watkow.

## Wejscie

- `wyrownaj(skan, uklad, ustawienia)`: `trimesh.Trimesh` skanu plytki (uklad skanera, mm) i `Uklad`
  z `qc.uklad.wczytaj`.
- `numer_plytki(skan_wyrownany, uklad)`, `potnij(skan_wyrownany, uklad, ustawienia, numer=...)`: skan
  w ukladzie plytki. `numer` jest opcjonalny, domyslnie liczony z dolkow.
- `analizuj(skan, uklad, ustawienia)`.

Progi z `ustawienia.toml`, sekcja `[plytka]`:

| Klucz | Znaczenie |
|---|---|
| `max_blad_wyrownania_mm` | max RMS par ICP (inaczej `BladPlytki("zly uklad ...")`) |
| `margines_gniazda_mm` | powiekszenie obrysu gniazda przy przypisaniu pracy |
| `min_pole_pracy_mm2` | mniejsze skladowe nie sa praca |

Stale algorytmu w kodzie (nie progi stanowiska): `wyrownanie.py` (plaszczyzna, znaczniki, ICP,
wyciecie), `kod.py` (`PROMIEN_POMIARU`, `PROG_BITU`, `ZAKRES_Z`), `ciecie.py` (`PROG_OD_PLYTKI_MM`,
`ZAPAS_NAD_PLYTKA_MM`, `SCALANIE_MM`, `ZAPAS_PRZECIECIA_MM`, `MIN_PRZECIEC`, `MIN_Z_W_GNIEZDZIE_MM`).

## Wyjscie

- `Wyrownanie(T_skan_do_plytki 4x4, blad_mm, znaczniki_xyz (3,3))`. Znaczniki w kolejnosci A, B, C,
  w ukladzie skanu: wierzcholki stozkow z modelu przeniesione przez odwrotnosc T.
- `BladPlytki`: komunikat "brak znacznikow: ..." (mniej niz 3 dolki znacznikow) albo "zly uklad: ..."
  (trojka nie pasuje do trojkata, za duzy blad ICP, material w wycieciu D).
- `numer_plytki` -> numer z `uklad.numery` albo None (kod 0 / 7 / numer innego ukladu).
- `Fragment(gniazdo, siatka, stan)`: siatka w ukladzie plytki, tylko sciany pracy i tylko uzywane
  wierzcholki; dla "puste" siatka pusta. Kolejnosc: gniazda wg ukladu, potem "poza_gniazdem".
- `WynikPlytki(numer, wyrownanie, fragmenty, skan_wyrownany)`.

## Kryterium "dziala"

`tests/test_plate.py` zielone (`python -m pytest -q tests/test_plate.py`, wolne: `-m wolne -k plate`):

- wyrownanie (skan z pracami, T losowa, szum 0,02): translacja <= 0,05 mm, kat <= 0,05 st.,
  `blad_mm` <= 0,1, znaczniki <= 0,08 mm. Przy szumie 0,04: <= 0,08 mm / 0,08 st. Obrot Z 10 st. +
  przechyl 1 st.: <= 0,05 mm / 0,05 st.;
- brak 2 znacznikow -> `BladPlytki` "brak znacznikow";
- numer 1-6 poprawny dla obu ukladow, plytka bazowa -> None;
- ciecie: kazdy fragment "praca" ma >= 95 % scian swojej pracy, <= 2 % scian cudzych prac i <= 1 %
  pola plytki. Stany puste / podwojne / poza_gniazdem zgodne z prawda, most w rynience;
- lancuch plate -> inspect: >= 5/6 ukruszen wykrytych na fragmentach;
- czas `analizuj` (laptop): 6 + 1 prac <= 15 s, 24 + 2 <= 40 s.

## Ograniczenia

- Pole skanowania skanera jeszcze nieznane. Jesli plytka nie miesci sie w jednym skanie, trzeba laczyc
  skany (etap 3); wyrownanie wymaga wszystkich 3 znacznikow w jednym skanie.
- Prace wyzsze niz 10 mm nad wierzchem (np. na sciance albo na innej pracy) moga wyjsc poza pole
  skanera; ciecie ich nie ogranicza.
- Model plytki = idealna geometria z ukladu ramki. Prawdziwy wydruk (tolerancje, wypaczenie) moze
  wymagac wiekszego `PROG_OD_PLYTKI_MM` albo modelu z pomiaru plytki.
- Bez numeru (kod nieczytelny) ciecie uzywa modelu bazowego: relief numeru (ok. 20 mm2) moze wyjsc
  jako fragment "poza_gniazdem".
- Drgniecie skanera (zdublowany plat pracy, bez przeciecia z praca) moze dac stan "podwojne";
  drgniecie rozpoznaje `inspect`.
- Sciany pracy blizej niz 0,25 mm od plytki (miejsca styku) nie trafiaja do fragmentu.
- Gdy skan nie zawiera dna plytki, kierunek "w gore" jest brany z osi Z skanera.
