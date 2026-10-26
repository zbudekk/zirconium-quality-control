# qc.syntetyka - generator syntetycznych prac i skanow

## Co robi

Tworzy proceduralne projekty koron i mostow z cyrkonii (zamiast prawdziwych STL) oraz sztuczne skany
tych prac ze znana prawda: skala spiekania, szum skanera, ukruszenia przy brzegu, poprawki
(szlifowanie), drgniecie skanera, niepelne pokrycie i widok tylko z gory. Sluzy do testow modulow
`catalog`, `plate`, `match`, `inspect` z metrykami wykryte / pominiete / falszywe.

- `prace.py` - korona z profilu (r, z) 60 wezlow (brzeg, ekwator ~0,35 h i ~1,08 R, bark, powierzchnia
  zujaca z guzkami i owalnoscia), wnetrze = profil przesuniety o grubosc sciany, pas trojkatow na
  brzegu; mosty = 3-4 korony na osi X co (srednica + 2 mm) + walce laczace (bez boolean).
- `skan.py` - brzeg projektu i skan pracy z prawda.
- `prawda.py` - dataclassy prawdy i zapis/odczyt JSON (wersja 1).

Tylko numpy i trimesh (bez scipy: normalne wierzcholkow liczone w numpy, bez `split`, `convex_hull`,
`sample_surface_even`, `remove_close`).

## Wejscie

- `prace.korona(ziarno, rodzaj=None, krok_mm=0.1)` - rodzaj `"trzonowiec"`, `"przedtrzonowiec"`,
  `"siekacz"` albo None (losowy z ziarna); krok = gestosc wzdluz profilu i po obwodzie.
- `prace.most(ziarno, punkty=4, krok_mm=0.1)` - 3 albo 4 punkty.
- `prace.pula_projektow(n=30, ziarno=1)`; `prace.przepis(ziarno, rodzaj, krok_mm)`,
  `prace.przepis_mostu(ziarno, punkty, krok_mm)`, `prace.z_przepisu(przepis)`.
- `skan.brzeg(projekt)`.
- `skan.skan_pracy(projekt, ziarno, wspolczynnik=1.0, szum_mm=0.02, ubytki=0, poprawki=0,
  drgniecie=False, pokrycie=1.0, widocznosc="pelna")` - `ubytki`/`poprawki` jako liczba albo lista
  slownikow (`srednica_mm`, `glebokosc_mm`, opcjonalnie `srodek`; brakujace pola losowane).
- Uklad projektu: mm, brzeg w z ~ 0, powierzchnia zujaca w gore, os wprowadzenia Z.

## Wyjscie

- Projekt: `trimesh.Trimesh` (korona zamknieta, wysokosc 5-11 mm, srednica 5-13 mm, sciana 0,6-1,5 mm;
  most 20-45 mm, niezamkniety - konkatenacja czesci). `metadata["id"]`, `metadata["przepis"]`.
- `Projekt(id, rodzaj, siatka, parametry)` w puli; przepisy sa slownikami JSON bez geometrii.
- `brzeg`: (N, 3) wierzcholki powierzchni zewnetrznej w pasie |z| < 0,3 mm.
- `skan_pracy`: `(Trimesh, PrawdaPracy)`. Kolejnosc: ubytki (uklad projektu) -> pokrycie -> szum
  N(0, szum) wzdluz normalnych liczonych przed ubytkami -> drgniecie -> widocznosc -> skala k
  (`T_projekt_do_skanu` = diag(k, k, k, 1)) -> tasowanie wierzcholkow i scian.
- Ukruszenie: srodek = wierzcholek sciany zewnetrznej 0,30-0,55 mm nad plaszczyzna brzegu (<= 0,5 mm od
  krzywej brzegu); ubytek nie przecina krawedzi brzegu (dno nie schodzi pod z = 0). Srednica 0,2-0,6,
  glebokosc 0,1-0,3, profil ostry (pelna glebokosc do 0,7 r, liniowo do 0 w r). Srodki parami >= 2 mm.
- Male ubytki lokalnie zageszczaja siatke (podzial trojkatow w kuli 2r): liczba scian rosnie, a na
  granicy podzialu powstaja T-junctions - skan NIE jest wodoszczelny. Inne moduly nie moga wymagac
  `is_watertight` skanu (projekt korony jest wodoszczelny, most nie).
- Poprawka: srednica 2,5-4, glebokosc 0,08-0,2, profil gaussowski (sigma r/2), srodek ~r nad brzegiem.
- Drgniecie: plat = 40 % scian najbardziej zgodnych z losowym kierunkiem poziomym u (z polowy bryly od
  strony u), w tym czesc scian wewnetrznych; kopia platu przesunieta o 0,10 mm wzdluz sredniej normalnej
  platu (normalne wyrownane znakiem do u) i dodana do siatki. Tylko ok. 50 % scian platu ma
  |n . n_sr| >= 0,7 (spojny plat o zgodnych normalnych to najwyzej ok. 15-20 % scian korony).
- Pokrycie < 1: 3-6 platow usunietych PRZED szumem tak, by pole pozostalych scian bez szumu =
  pokrycie x pole projektu (x k^2 po skali); prawda.pokrycie nie zalezy od szum_mm. Pole skanu z szumem
  jest wieksze (szum 0,02 przy kroku 0,1 zawyza pole o ok. 14 %).
- `widocznosc="z_gory"` usuwa sciany o normalnej z < -0,3.
- Bledne argumenty (krok_mm <= 0, pokrycie poza (0; 1], wspolczynnik <= 0, szum_mm < 0, ubytki/poprawki
  < 0, nieznana widocznosc) -> `ValueError` z polskim komunikatem.
- Normalne wierzcholkow licz `qc.syntetyka.skan.normalne_wierzcholkow(v, f)` - `trimesh.vertex_normals`
  bez scipy przechodzi na wolna petle (ok. 2 min na korone).
- Prawda JSON (`Prawda.do_json` / `Prawda.z_json`): macierze jako listy list, srodki ubytkow w
  ukladzie projektu bez skali.

## Kryterium "dziala"

- `tests/test_syntetyka_prace.py` testy 1-19 zielone (`python -m pytest -q tests/test_syntetyka_prace.py`).
- Pula 30 projektow (`pula_projektow(30, 1)`) odrozniana przez modul `match` w >= 95 % przypadkow.
