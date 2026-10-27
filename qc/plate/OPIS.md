# qc.plate - plytka: wyrownanie, numer, ciecie na fragmenty gniazd

## Co robi

Skan plytki z pracami (uklad skanera) przenosi do ukladu plytki z `qc.uklad`, odczytuje numer plytki z
dolkow kodu i tnie skan na fragmenty: jeden na kazde gniazdo (praca, puste, podwojne) i osobne dla
prac lezacych na sciance. Fragmenty ida do `match` / `inspect`.

- `wyrownanie.py`:
  1. plaszczyzna wierzchu: open3d `segment_plane` (0,15 mm, 3 punkty, 3000 iteracji) na probce
     `voxel_down_sample` 0,5 mm (wierzcholki scian co drugi), wiec geste prace nie dominuja. Seed staly
     (1, potem 2 i 3) pod blokada, bo `open3d.utility.random.seed` jest globalny. Plaszczyzna musi miec
     pole inlierow >= 0,3 x rozmiar^2, inaczej nastepny seed albo `BladPlytki("brak znacznikow ...")`.
     Gdy w skanie jest tez dno plytki (druga plaszczyzna w odleglosci
     `grubosc`), wierzch to ta plaszczyzna, pod ktora jest wiecej punktow zaglebien gniazd
     (0,3-4,5 mm). Bez dna kierunek "w gore" = +Z skanera. Potem 3 razy dopasowanie najmniejszych kwadratow
     do punktow wierzchu (wynik nie zalezy od probki RANSAC);
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
  5. kontrola orientacji: brak materialu w wycieciu D;
  6. `znaczniki_xyz` = zmierzone dna dolkow: stozek o znanym nachyleniu dopasowany (Gauss-Newton) do
     punktow skanu w 0,8 R od osi, w ukladzie plytki, przeniesiony odwrotnoscia T.
- `kod.py` - tylko wierzcholki scian; mediana z w kole 0,6 x d/2 wokol dolka (z w [-2 x glebokosc;
  0,3], bez dna, kieszeni i prac); mediana < -0,5 x glebokosc = bit 1; `qc.uklad.numer_z_kodu`. Bit
  nieznany (< 5 punktow w kole albo pierscien d/2 + 0,3-0,9 mm bez danych / nieplaski: mediana |z| >
  0,25 x glebokosc) = numer None z przyczyna w `WynikPlytki.uwagi` (np. dolek zakryty praca).
- `ciecie.py`:
  1. sciany, ktorych srednia odleglosc 3 wierzcholkow od modelu bazowego plytki (3 dolki, bez reliefu)
     > `prog_od_plytki_mm` = prace. Scena `RaycastingScene` modelu raz na uklad (cache), wierzcholki
     wyzej niz model + 0,5 mm + prog bez liczenia odleglosci. Wypelniony dolek kodu to wyspa ok. 3 mm2
     (< `min_pole_pracy_mm2`);
  2. skladowe spojne po wspolnych wierzcholkach (numpy: zaczepianie na minimum + kompresja sciezek).
     Male skladowe (< `min_pole_pracy_mm2`) blizej niz 0,2 mm od duzej sa do niej dolaczane, reszta
     malych odpada;
  3. skladowa w calosci w obszarze reliefu numeru (kwadrat wysokosc tekstu + 2 x 1 mm, z <= relief +
     0,2) jest pomijana;
  4. gniazdo = obrys gorny powiekszony o `margines_gniazda_mm`, w ktorym lezy srodek masy (pole,
     rzut XY). Gdy srodek jest tylko w pasie marginesu, a praca nie siega ponizej -1 mm, to praca
     lezy na sciance;
  5. stan: 0 skladowych = "puste". W rynience (leza tam tylko mosty) dowolna liczba skladowych = jedna
     praca. W gniezdzie stozkowym osobna praca = skladowa o polu >= `min_udzial_drugiej_pracy` x
     najwieksza; jedna taka = "praca", >= 2 = "podwojne". Mniejsze wyspy (np. przy dnie gniazda w
     skanie z gory: 5-29 mm2 przy 320-730 mm2) naleza do pracy. Skladowa poza obrysami =
     "poza_gniazdem" z gniazdem o najblizszym obrysie.

Tylko numpy, trimesh, open3d. Funkcje sa bezpieczne dla watkow:
- stan globalny to tylko cache pod blokada: siatki referencyjne, chmura celu ICP i scena modelu
  (pierwsze zapytanie, czyli commit Embree, przy tworzeniu pod blokada); klucz = skrot tresci ukladu;
- duze tablice przeksztalcane bez BLAS (`przenies`, iloczyny elementowe, kowariancja przez einsum).
  Wielowatkowy OpenBLAS (`@` numpy) rownolegle z OpenMP open3d w innym watku dawal access violation
  (24 + 2, 3 watki); z OPENBLAS_NUM_THREADS=1 albo bez BLAS problemu nie ma.

## Wejscie

- `wyrownaj(skan, uklad, ustawienia)`: `trimesh.Trimesh` skanu plytki (uklad skanera, mm) i `Uklad`
  z `qc.uklad.wczytaj`.
- `numer_plytki(skan_wyrownany, uklad)`, `odczytaj_kod(...)` -> (numer, uwagi), `potnij(skan_wyrownany,
  uklad, ustawienia)`: skan w ukladzie plytki.
- `analizuj(skan, uklad, ustawienia)`.

Progi z `ustawienia.toml`, sekcja `[plytka]`:

| Klucz | Znaczenie |
|---|---|
| `max_blad_wyrownania_mm` | max RMS par ICP (inaczej `BladPlytki("zly uklad ...")`) |
| `margines_gniazda_mm` | powiekszenie obrysu gniazda przy przypisaniu pracy |
| `min_pole_pracy_mm2` | mniejsze skladowe nie sa praca |
| `prog_od_plytki_mm` | sciana dalej od modelu plytki = praca (0,25) |
| `min_udzial_drugiej_pracy` | druga skladowa w gniezdzie stozkowym = osobna praca od tego udzialu pola najwiekszej (0,2) |

Stale algorytmu w kodzie (nie progi stanowiska): `wyrownanie.py` (plaszczyzna, znaczniki, ICP,
wyciecie), `kod.py` (`PROMIEN_POMIARU`, `PROG_BITU`, `ZAKRES_Z`), `ciecie.py` (`ZAPAS_NAD_PLYTKA_MM`,
`SCALANIE_MM`, `MIN_Z_W_GNIEZDZIE_MM`, `ZAPAS_RELIEFU_MM`, `ZAPAS_WYSOKOSCI_RELIEFU_MM`).

## Wyjscie

- `Wyrownanie(T_skan_do_plytki 4x4, blad_mm, znaczniki_xyz (3,3))`. Znaczniki w kolejnosci A, B, C,
  w ukladzie skanu: zmierzone dna dolkow. T powtarzalna (staly seed): to samo wejscie = ta sama T.
- `BladPlytki`: komunikat "brak znacznikow: ..." (mniej niz 3 dolki znacznikow) albo "zly uklad: ..."
  (trojka nie pasuje do trojkata, za duzy blad ICP, material w wycieciu D).
- `numer_plytki` -> numer z `uklad.numery` albo None (kod 0 / 7 / numer innego ukladu / dolek bez
  danych).
- `Fragment(gniazdo, siatka, stan)`: siatka w ukladzie plytki, tylko sciany pracy i tylko uzywane
  wierzcholki; dla "puste" siatka pusta. Kolejnosc: gniazda wg ukladu, potem "poza_gniazdem".
- `WynikPlytki(numer, wyrownanie, fragmenty, skan_wyrownany, uwagi)`: uwagi = przyczyny numeru None.

## Kryterium "dziala"

`tests/test_plate.py` zielone (`python -m pytest -q tests/test_plate.py`, wolne: `-m wolne -k plate`):

- wyrownanie (skan z pracami, T losowa, szum 0,02): translacja <= 0,05 mm, kat <= 0,05 st.,
  `blad_mm` <= 0,1, znaczniki <= 0,08 mm. Przy szumie 0,04: <= 0,08 mm / 0,08 st. Obrot Z 10 st. +
  przechyl 1 st.: <= 0,05 mm / 0,05 st.;
- brak 2 znacznikow -> `BladPlytki` "brak znacznikow";
- powtarzalnosc: 10/10 wywolan na plytce 24 + 2 i 5/5 na 12 + 2 z ta sama T (+-1e-6);
- skan z gory (bez scian o normalnej z < -0,3, szum plytki 0,03): numer, 7/7 "praca", 0 "podwojne",
  T <= 0,05 mm / 0,05 st.;
- numer 1-6 poprawny dla obu ukladow, plytka bazowa -> None; zakryty dolek -> None, polowa dolka
  wystarcza; relief nie jest fragmentem "poza_gniazdem";
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
- Praca lezaca na reliefie numeru (w calosci w jego obszarze i nie wyzej niz relief + 0,2) bylaby
  pominieta; praktycznie niemozliwe (prace sa wyzsze).
- Druga praca w rynience nie daje stanu "podwojne" (w rynience wszystko = jeden most).
- Drgniecie skanera (zdublowany plat pracy >= 20 % pola) w gniezdzie stozkowym moze dac stan
  "podwojne"; drgniecie rozpoznaje `inspect`.
- Sciany pracy blizej niz 0,25 mm od plytki (miejsca styku) nie trafiaja do fragmentu.
- Gdy skan nie zawiera dna plytki, kierunek "w gore" jest brany z osi Z skanera.
