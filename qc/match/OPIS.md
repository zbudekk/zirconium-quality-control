# qc.match - identyfikacja prac (fragment skanu -> projekt STL)

## Co robi

Dla fragmentu skanu (jedna praca wycieta z plytki) wskazuje projekt z puli, polozenie projektu we
fragmencie i pewnosc identyfikacji. Wieczorem pula = STL z CSV wspolczynnikow (k 1,20-1,25, pelne skany
przed spiekaniem), rano pula z ostatnich dni (k = 1, skan plytki z gory, niepelny).

- `filtr.py` - `WpisPuli`; `kandydaci`: wpisy, ktore przechodza `qc.catalog.cechy.pasuje` (k wpisu),
  rosnaco po `cechy.odleglosc` do projektu przeskalowanego o k, najwyzej `max_kandydatow`; wpisy z
  cechami None (plik uszkodzony) pomijane. `wedlug_odleglosci` - ta sama kolejnosc bez progow (drugi etap).
- `dopasowanie.py` - chmury open3d, zgrubne i dokladne wyrownanie, pokrycie.
- `ranking.py` - `Kandydat`, `WynikDopasowania`, porzadek i pewnosc.
- `__init__.py` - `dopasuj` (calosc), eksport `dopasuj`, `WpisPuli`, `Kandydat`, `WynikDopasowania`.

Przebieg `dopasuj` (na kandydata, projekt przeskalowany o k):

1. Fragment raz na wywolanie: cechy (`policz`), wygladzenie wierzcholkow (1 krok usredniania z
   pierscieniem sasiadow - tlumi szum ok. 2,5 x), chmury voxel 1,5 mm (zgrubna) i 0,4 mm (ICP), osie PCA.
2. Projekt: probka 6000 pkt (voxel `voxel_fpfh_mm`, normalne scian) do zgrubnego etapu; probka 20 000 pkt
   (stale ziarno) dopiero dla 2. etapu ICP; scena RaycastingScene siatki CAD raz na kandydata.
3. Zgrubne: ramki osi glownych fragmentu (kazda z 3 osi jako os wyrozniona, 2 zwroty) ustawiane na os
   wyrozniona projektu (os wprowadzenia korony, os dluga mostu) x 12 katow obrotu wokol niej = 72 pozy;
   pozy szeregowane jednym zapytaniem do sceny, z kazdej z 6 ramek 4 katy (wzajemnie >= 90 st.) ->
   zgrubny ICP point-to-plane (1,5 mm) -> fitness = udzial punktow <= 0,25 mm od siatki. Najlepszy
   fitness < 0,7 = kandydat odrzucony (nie trafia do wyniku).
4. Do 5 odrebnych hipotez z fitness >= 0,9 x najlepszego: ICP 0,5 mm (chmura rzadka) i pokrycie na
   4000 pkt; zwyciezca: ICP 0,1 mm na probce 20 000 pkt, pokrycie koncowe na 12 000 pkt.
5. Os PCA fragmentu nieokreslona (wyraznosc < 0,05) i pokrycie < min: FPFH + RANSAC (2 proby, rozne ziarna).
6. Wczesne wyjscie: kandydat z pokryciem >= 0,97, a nastepny ma odleglosc cech > 2 x biezacej - koniec.
7. Drugi etap: gdy nic nie osiaga `min_pokrycie` (rano: 0,97), kolejne wpisy wg odleglosci cech bez
   progow `pasuje` (wieczorem 1 x, rano 2 x `max_kandydatow`), stop po pokryciu >= 0,97.
8. Ranking i pewnosc; wynik obciety do `max_kandydatow`.

Dlaczego tak (pomiary na danych syntetycznych, pula 30, k 1,20-1,25, szum 0,03):

- Pokrycie surowych wierzcholkow przy PRAWDZIWEJ pozie = 0,83 (szum po skali 0,037 mm vs prog 0,05) -
  ponizej `min_pokrycie_wieczor` 0,85. Pokrycie liczone jest wiec na wierzcholkach wygladzonych:
  0,99 przy dobrej pozie, 0,94-0,98 przy pozie symetrycznej korony, < 0,6 dla obcego projektu.
- FPFH + RANSAC wg specyfikacji (voxel 0,5, 100 000 iteracji): 0,4-0,5 s na kandydata, w 3/8 przypadkow
  poza obrocona o ~180 st. wokol osi (korona prawie symetryczna, blad 8-12 mm). Osie PCA + przeglad
  katow + ICP: 0/80 zlych poz w testach, ok. 0,1 s na kandydata. RANSAC zostal jako awaryjny.
- Fitness zgrubny wobec siatki: wlasciwe >= 0,84 (47 przypadkow: pelne, z gory, ubytki + szum 0,04,
  mosty, rano 0,7), bledne mediana 0,49, p90 0,75 - stad prog 0,7.
- Niepelny skan (rano, pokrycie 0,7): tylko 23/40 przechodzi `pasuje` (wymiary PCA sie zmieniaja), os
  wyrozniona fragmentu bywa inna niz projektu (70-89 st.) - stad 3 osie i drugi etap.

Brak stanu globalnego: wszystko liczone w obrebie wywolania; jedyny wyjatek to
`open3d.utility.random.seed` przed RANSAC (globalny w open3d, tylko w sciezce awaryjnej).
`dopasuj(..., pamiec=dict)` - opcjonalny slownik wywolujacego na chmury projektow (klucz projekt_id, k,
voxel, id siatki), np. jeden na plytke; slownik nie jest wspoldzielony miedzy watkami.

## Wejscie

- `dopasuj(fragment: Trimesh, pula: list[WpisPuli], ustawienia, tryb="wieczor"|"rano", pamiec=None)`.
- `WpisPuli(projekt_id, siatka: Trimesh w ukladzie CAD, cechy: Cechy | None, wspolczynnik: float)`.
- Ustawienia `[dopasowanie]`: `tolerancja_objetosci`, `tolerancja_wymiarow_mm` (filtr, przez
  `cechy.pasuje`), `odleglosc_mm` (prog pokrycia, 0,05), `min_pokrycie_wieczor` (0,85),
  `min_pokrycie_rano` (0,60), `margines_pewnosci` (0,10), `voxel_fpfh_mm` (0,5: chmura projektu,
  FPFH; zgrubna chmura fragmentu = 3 x), `max_kandydatow` (8).
- Funkcje skladowe: `filtr.kandydaci(cechy_fragmentu, pula, ustawienia)`;
  `dopasowanie.zgrubne(fragment_pc, projekt_pc, voxel)` (FPFH + RANSAC, 4x4 projekt -> fragment),
  `dopasowanie.dokladne(fragment_pc, projekt_pc, T0, max_odleglosc)` (ICP point-to-plane, (T, rms)),
  `dopasowanie.pokrycie(fragment, projekt, T, prog_mm, scena=None)`. zgrubne/dokladne: projekt_pc juz
  przeskalowany o k, T sztywne; pokrycie: T ze skala, projekt w ukladzie CAD.

## Wyjscie

- `WynikDopasowania(kandydaci, pewnosc)`; kandydaci malejaco po pokryciu (rowne +-0,005 -> mniejsze rms),
  najwyzej `max_kandydatow`, tylko kandydaci po zgrubnym wyrownaniu (fitness >= 0,7).
- `Kandydat(projekt_id, wspolczynnik, T_projekt_do_fragmentu, pokrycie, rms_mm)`: T 4x4 ze skala
  (projekt w ukladzie CAD -> fragment); pokrycie = udzial (wygladzonych) wierzcholkow fragmentu
  <= `odleglosc_mm` od projektu po T; rms = rms ICP 0,1 mm w mm.
- `pewnosc`: `pewny` - top1 >= min i (brak top2 albo top1 - top2 >= margines albo top2 < min);
  `dwuznaczny` - top1, top2 >= min i roznica < margines; `brak` - top1 < min albo brak kandydatow.
  min = `min_pokrycie_wieczor` albo `min_pokrycie_rano` wg trybu; inny tryb = ValueError.

## Kryterium "dziala"

- `python -m pytest tests/test_match.py -m "not wolne"` zielone (testy 1-11: top-1 wieczor/rano,
  blizniaki, brak kandydata, filtr, ubytki, szum 0,04, skan z gory, czas, transformacja, mosty).
- Test 12 (`-m wolne -k metryki_200 -s`): 200 fragmentow, top-1 >= 190, top-2 >= 196, brak <= 2,
  tabela w wydruku.
- Sekcja 14 planu: >= 85 % poprawnych identyfikacji (top-1) na prawdziwych skanach stanowiska.

Ograniczenia:

- Blizniaki (roznica na poziomie szumu, np. 0,05 mm w kuli 1 mm) - pokrycia prawie rowne, wynik
  `dwuznaczny`; rozstrzyga operator.
- Skan z gory: dziala na danych syntetycznych (20/20), ale fragment bez wnetrza ma slabsze osie PCA;
  prawdziwy skaner moze gubic wiecej (cienie przy brzegu).
- Rano (pula 60, skan niepelny): filtr cech zawodzi, drugi etap kosztuje ok. 1,2-1,5 s na fragment.
- Czas: ok. 0,5 s na fragment wieczorem (pula 30), 1-1,5 s dla fragmentu spoza puli (drugi etap);
  stale 0,1-0,2 s to `policz` cech fragmentu. Bez `pamiec` chmury projektow licza sie w kazdym wywolaniu.
- Pokrycie zalezy od szumu skanera: wygladzenie zaklada siatke skanu o kroku ~0,1 mm; dla innej
  gestosci progi (0,7 fitness, 0,97 wczesne wyjscie) trzeba zmierzyc ponownie.
