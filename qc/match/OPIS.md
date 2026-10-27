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
- Seed open3d (RANSAC) ustawiany przez `qc.open3d_wspolne.ziarno(n)` - blokada wspolna z `qc.plate`.

### Definicja pokrycia

Pokrycie = udzial wierzcholkow fragmentu WYGLADZONEGO jednym krokiem usredniania z sasiadami (wierzcholek
i jego pierscien, waga rowna) w odleglosci <= `odleglosc_mm` od powierzchni projektu po T (probka 12 000
wierzcholkow, stale ziarno). Wygladzenie tlumi szum skanera ok. 2,5 x; bez niego pokrycie przy prawdziwej
pozie wynosi tylko 0,83 (szum 0,03 x k 1,22 = 0,037 mm przy progu 0,05). Wygladzony fragment sluzy tylko
do dopasowania - `inspect` dostaje surowy fragment i T. Wszystkie progi pokrycia (`min_pokrycie_*`,
`wczesne_pokrycie`, `margines_*`) zaleza od tej definicji: przy innej gestosci siatki skanu (tu ~0,1 mm)
albo innym szumie trzeba je zmierzyc ponownie.

### Przebieg `dopasuj` (na kandydata, projekt przeskalowany o k)

1. Fragment raz na wywolanie: cechy (`policz`), wygladzenie, chmury voxel 1,5 mm (zgrubna) i 0,4 mm
   (ICP), osie PCA (3 ramki: kazda os glowna jako os wyrozniona) i wyraznosc osi.
2. Projekt: probka 6000 pkt (losowanie wazone polem, normalne scian) -> voxel `voxel_fpfh_mm`; probka
   20 000 pkt i scena RaycastingScene siatki CAD dopiero, gdy kandydat przejdzie sito.
3. Zgrubne (PCA + przeglad katow): os kazdej ramki fragmentu (2 zwroty) ustawiana na os wyrozniona
   projektu (os wprowadzenia korony, os dluga mostu) x 12 katow obrotu wokol niej x 5 przesuniec srodka
   wzdluz tej osi (0, +-10 %, +-20 % dlugosci projektu - niepelny skan mostu przesuwa srodek o 3-6 mm)
   = 360 poz, szeregowanych jednym zapytaniem o odleglosc punkt-plaszczyzna od chmury rzadkiej (NNS,
   bez BVH siatki); kazdy kat bierze najlepsze przesuniecie.
   - Z kazdej z 6 ramek 4 katy (wzajemnie >= 90 st.; korona bywa prawie symetryczna o 180 st.) ->
     24 zgrubne ICP point-to-plane (1,5 mm).
   - Sito: fitness (udzial punktow <= 0,25 mm) od chmury rzadkiej < `prog_sita` = odrzucony bez
     budowy sceny siatki.
   - Dla pozostalych fitness tych samych poz (bez nowego ICP) od siatki (scena); < `prog_zgrubny` =
     odrzucony (nie trafia do wyniku).
4. Do 5 odrebnych hipotez z fitness >= 0,9 x najlepszego: ICP 0,5 mm (chmura rzadka) i pokrycie na 4000
   pkt; zwyciezca: ICP 0,1 mm na probce 20 000 pkt, pokrycie koncowe.
5. Zabezpieczenie (wyzwalane rzadko): wyraznosc osi PCA fragmentu < `prog_wyraznosci_osi` (os
   nieokreslona, np. bryla prawie kulista) -> zamiast PCA zgrubne FPFH + RANSAC (voxel `voxel_fpfh_mm`,
   normalne 2 x voxel, FPFH 5 x voxel, 100 000 iteracji, 2 proby z roznym ziarnem) dla
   najwyzej `max_kandydatow` wpisow na wywolanie (rano drugi etap jest bez limitu - bez tego praca spoza
   puli 60 dawala 120 wywolan RANSAC, 85 s); dalsze wpisy ida sciezka PCA. W 190 fragmentach
   testowych nie uruchomilo sie ani razu (zmierzona wyraznosc min 0,068 > 0,05); sciezke sprawdza
   `test_ransac_awaryjny` (prog 1,0 w kopii ustawien).
6. Wczesne wyjscie: kandydat z pokryciem >= `wczesne_pokrycie`, a nastepny ma odleglosc cech > 2 x
   biezacej - koniec.
7. Drugi etap: gdy nic nie osiaga `min_pokrycie` (rano: `wczesne_pokrycie`), kolejne wpisy wg odleglosci
   cech bez progow `pasuje`: wieczorem najwyzej 1 x `max_kandydatow`, rano bez limitu (niepelny skan psuje
   cechy: przy puli 200 wlasciwy projekt bywa na pozycji 25-62); stop po pokryciu >= `wczesne_pokrycie`.
8. Kontrola obrotu o 180 st. - tylko wieczorem (T idzie do `inspect`; rano liczy sie projekt), top-1 z
   pokryciem >= min: poza obrocona wokol osi wyroznionej projektu po ICP zastepuje top-1 tylko przy
   pokryciu wiekszym o > `margines_obrotu_180`; pozy blizsze niz `obrot_inna_poza_mm` = ta sama poza.
   Pewnosci nie zmienia (obnizanie dawalo falszywe "dwuznaczny": rano 6/30, wieczorem 16/130 bez
   zmiany pozy). Rms nie rozstrzyga: w 75 zmierzonych przypadkach pokrycie wskazalo wlasciwa poze 74 razy,
   rms wskazaloby zla poze w 18 z 39 bliskich.
9. Ranking i pewnosc; wynik obciety do `max_kandydatow`.

### Pomiary (dane syntetyczne, pula 30, k 1,20-1,25, szum 0,03)

- FPFH + RANSAC wg pierwotnej specyfikacji: 0,4-0,5 s na kandydata, w 3/8 przypadkow poza obrocona
  o ~180 st. (blad 8-12 mm). PCA + przeglad katow + ICP: blad pozy p95 <= 0,03 mm, ok. 0,1 s na kandydata.
- Fitness zgrubny od siatki: wlasciwe >= 0,84 (47 przypadkow: pelne, z gory, ubytki + szum 0,04, mosty,
  rano 0,7), bledne mediana 0,49, p90 0,75 - prog 0,7. Mosty rano z pokryciem 0,7 (10 sztuk, po dodaniu
  przesuniec): od siatki >= 0,73.
- Sito (fitness od chmury) dla wlasciwych, korony rano 0,7 / mosty rano 0,7: 1 start na ramke
  0,86 / 0,43 (odrzucalo mosty), 2 starty 0,87 / 0,46, 4 starty 0,87 / 0,67 - stad 4 starty i
  `prog_sita` 0,55; korony bez spowolnienia (0,5 s na fragment wieczorem), praca spoza puli rano
  3,4 -> 4,1 s.
- Rano pokrycie wlasciwego >= 0,94 (p5 0,98), obcych kandydatow do 0,88 (recenzja, pula 60) - stad
  `min_pokrycie_rano` 0,90.

### Watki i pamiec

Brak stanu globalnego; jedyny wspolny stan to seed open3d przed RANSAC - pod blokada
`qc.open3d_wspolne.BLOKADA_SEED`. `dopasuj(..., pamiec=dict)` - opcjonalny slownik wywolujacego na dane
projektow (chmury, sito NNS, scena), klucz `(projekt_id, k zaokraglone do 1e-6, voxel)`: pod tym samym
projekt_id musi byc ta sama siatka (zmiana pliku STL = nowa pamiec). Np. jedna pamiec na plytke; slownik
nie jest wspoldzielony miedzy watkami. Bez `pamiec` dane zyja tylko w obrebie wywolania.

## Wejscie

- `dopasuj(fragment: Trimesh, pula: list[WpisPuli], ustawienia, tryb="wieczor"|"rano", pamiec=None)`.
- `WpisPuli(projekt_id, siatka: Trimesh w ukladzie CAD, cechy: Cechy | None, wspolczynnik: float)`.
- Ustawienia `[dopasowanie]` (zakresy sprawdzane w `qc/ustawienia.py`):
  - `tolerancja_objetosci`, `tolerancja_wymiarow_mm` - filtr (`cechy.pasuje`);
  - `odleglosc_mm` (0,05) - prog pokrycia;
  - `min_pokrycie_wieczor` (0,85), `min_pokrycie_rano` (0,90), `margines_pewnosci` (0,10) - pewnosc;
  - `voxel_fpfh_mm` (0,5) - chmura rzadka projektu, FPFH; chmura zgrubna fragmentu = 3 x;
  - `max_kandydatow` (8);
  - `prog_zgrubny` (0,7) - fitness zgrubny ponizej = kandydat odrzucony;
  - `wczesne_pokrycie` (0,97) - konczy szukanie (wczesne wyjscie, drugi etap);
  - `prog_wyraznosci_osi` (0,05) - ponizej zgrubne FPFH + RANSAC;
  - `margines_obrotu_180` (0,005), `obrot_inna_poza_mm` (0,5) - kontrola obrotu o 180 st. (wieczor);
  - `prog_sita` (0,55) - fitness od chmury rzadkiej ponizej = odrzucony przed budowa sceny.
- Funkcje skladowe: `filtr.kandydaci(cechy_fragmentu, pula, ustawienia)`;
  `dopasowanie.zgrubne(fragment_pc, projekt_pc, voxel)` (FPFH + RANSAC, 4x4 projekt -> fragment),
  `dopasowanie.dokladne(fragment_pc, projekt_pc, T0, max_odleglosc)` (ICP point-to-plane, (T, rms)),
  `dopasowanie.pokrycie(fragment, projekt, T, prog_mm, scena=None)` (wierzcholki jak podane - wygladzenie
  robi `dopasuj`). zgrubne/dokladne: projekt_pc juz przeskalowany o k, T sztywne; pokrycie: T ze skala.

## Wyjscie

- `WynikDopasowania(kandydaci, pewnosc)`; kandydaci malejaco po pokryciu (rowne +-0,005 -> mniejsze rms),
  najwyzej `max_kandydatow`, tylko kandydaci po zgrubnym wyrownaniu (fitness >= `prog_zgrubny`).
- `Kandydat(projekt_id, wspolczynnik, T_projekt_do_fragmentu, pokrycie, rms_mm)`: T 4x4 ze skala
  (projekt w ukladzie CAD -> fragment); pokrycie wg definicji wyzej; rms = rms ICP 0,1 mm w mm.
- `pewnosc`: `pewny` - top1 >= min i (brak top2 albo top1 - top2 >= margines albo top2 < min);
  `dwuznaczny` - top1, top2 >= min i roznica < margines; `brak` - top1 < min albo brak kandydatow.
  min = `min_pokrycie_wieczor` albo `min_pokrycie_rano` wg trybu; inny tryb = ValueError.

## Kryterium "dziala"

- `python -m pytest tests/test_match.py -m "not wolne"` zielone (testy 1-11, RANSAC awaryjny i jego limit
  rano, klucz pamieci, pewnosc wieczorem).
- `-m wolne -k match`: test 12 (200 fragmentow: top-1 >= 190, top-2 >= 196, brak <= 2, tabela), rano
  pula 200 (top-1 >= 19/20, 0 pewnych na zlym projekcie), rano spoza puli (0 pewnych), pewnosc rano
  (>= 38/40), mosty rano z pokryciem 0,7 (top-1 >= 9/10).
- Sekcja 14 planu: >= 85 % poprawnych identyfikacji (top-1) na prawdziwych skanach stanowiska.

Ograniczenia:

- Blizniaki (roznica na poziomie szumu, np. 0,05 mm w kuli 1 mm) - pokrycia prawie rowne, wynik
  `dwuznaczny`; rozstrzyga operator.
- Korona prawie symetryczna: przy skanie niepelnym poza obrocona o 180 st. przy poprawnym top-1 zdarzala
  sie w 1/20-1/30 (recenzja) - rano bez znaczenia (liczy sie projekt), wieczorem `inspect` dostalby zla T;
  kontrola obrotu (pkt 8) wybiera wtedy poze o wiekszym pokryciu; przy roznicy pokrycia <= 0,005 zla
  poza moze zostac (pewnosc tego nie sygnalizuje).
- Skan z gory: dziala na danych syntetycznych (20/20), ale fragment bez wnetrza ma slabsze osie PCA;
  prawdziwy skaner moze gubic wiecej (cienie przy brzegu).
- Czas (bez `pamiec`): ok. 0,5 s na fragment wieczorem (pula 30), ok. 1 s dla pracy spoza puli
  wieczorem, rano 1-1,5 s (pula 60), praca spoza puli rano ok. 4 s (cala pula w drugim etapie,
  ok. 55 ms na odrzuconego kandydata - glownie probka siatki 150 tys. scian). Stale 0,05-0,15 s to
  `policz` cech fragmentu. Z `pamiec` (jedna na plytke) koszt projektu liczy sie raz.
