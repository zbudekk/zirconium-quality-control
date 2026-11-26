# S1 / sub_B - opisy modulow vs kod, uklady plytek okraglych, rozgalezienia po nazwie ukladu

Data: 2026-11-23. Worktree: <PC-katalog>\qc-wt\analiza-s1 (galaz analiza/s1). Tylko czytanie (Read/Grep, Get-ChildItem); bez Pythona, bez testow.
Sciezki skrocone: `uklad.py` = Ramki\stanowisko\stanowisko\uklad.py, `uklad.md` = Ramki\stanowisko\opisy_modulow\uklad.md itd.
Stan: `zgodne` / `ROZJAZD` / `nie znaleziono w kodzie`. `(dane)` = liczba jest w uklad.json, nie w kodzie. `(test)` = kryterium testu - testow nie uruchamiano.

---------------------------------------------------------------------------------------------------------------------
## CZESC 1 - opis vs kod

### 1.1 uklad (uklad.md vs uklad.py)

| opis (cytat skrocony) | kod plik:linia | stan | co sie rozni |
|---|---|---|---|
| md:3 "gniazda (okragle stozkowe i rynienki)" | uklad.py:25, 266-267 | zgodne | TYPY_GNIAZD = ("round", "trough") |
| md:3 "trzy znaczniki (stozkowe wglebienia fi5 x 3 mm)" | uklad.py:244-252, 351 | czesciowo | kod NIE sprawdza liczby znacznikow (=3) ani wartosci d/depth; 5 / 3 tylko w plikach (dane) |
| md:3 "Plik jest sprawdzany przy wczytaniu" | uklad.py:326 | zgodne | |
| md:5 "domyslnie KATALOG_MODELI/<nazwa>" | uklad.py:22, 318 | zgodne | |
| md:5 "programy biora katalog z [plytki] (ustawienia.katalog_plytki)" | porownaj.py:124, 151, 258; synth.py:1240 | zgodne | |
| md:5 lista nazw (R59, *_r54, okragla_ramkowa_*) | ustawienia.py:147-149 (UKLADY_WBUDOWANE) | zgodne | 10 nazw |
| md:5 "UkladPlytki.nazwa to nazwa, pod ktora wczytano, nie pole plate" | uklad.py:140, 348 | zgodne | |
| md:5 "typ_plytki("okragla_poranna_r54") -> okragla_poranna" | uklad.py:29, 32-38 | zgodne | regex `_r\d+$` usuwa dowolny przyrostek `_r<cyfry>` na koncu, nie tylko `_r54` |
| md:7 "uklad wybiera czlowiek, a plate sprawdza, czy skan do niego pasuje" | porownaj.py:627 (`--plytka` domyslnie "auto"), porownaj.py:257-285; plate.py:754-864 | ROZJAZD | od 15.11 domyslnie program sam rozpoznaje uklad (`plate.rozpoznaj_uklad`); opis mowi tylko o wyborze recznym |
| md:7 "id gniazd: po y rzedu, w rzedzie od prawej" | (dane) | zgodne z plikami | |
| md:11-14 tabela gniazd / rynienek / stozkow / dolkow | (dane) | zgodne z plikami | szczegoly w CZESCI 2; w kodzie tych liczb nie ma |
| md:16 "Sumy SHA-256 wszystkich 28 plikow" | (test) | liczba plikow zgodna | Get-ChildItem: 28 plikow R59/R54 + 10 R58 = 38 (CZESC 2.9) |
| md:18 "okragla_ramkowa_wieczorna (1,2,3; 19 gniazd), _poranna (4,5,6; 24 gniazda)" | (dane) | zgodne | STL plytka_n1..n3 / n4..n6; sockets 19 / 24 |
| md:18 "4 dolki kodu w kole r 47" | (dane) | zgodne | najwiekszy promien dolka okraglego 43,932 (CZESC 2.8) |
| md:18 "3 kieszenie magnesow na promieniu 45" | (dane) | zgodne | 31,8198 * sqrt(2) = 45,000 |
| md:18 "magnet_pockets, cover_groove, key_slot (i coords, units, version) nie sa czytane - walidacja pomija nieznane klucze" | uklad.py:217-292, 327-360 | zgodne | ignorowane sa tez: number_relief, leds, hole_d, hole_pitch, hole_count; flat.corner i flat.opis trafiaja do slownika flat (359) |
| md:18 "straznik ich nie rozroznia - rozroznia plate.rozpoznaj_uklad po numerze z dolkow i ksztalcie brzegu" | plate.py:826-850 | zgodne | kolejnosc w kodzie: numer podany (834) -> numer z dolkow (837) -> ksztalt (840) -> "dolki_wykluczaja" (845-847) -> "domyslny" (849-850, pewny=False) |
| md:20 metody UkladPlytki / Gniazdo | uklad.py:153, 159, 162, 165, 176, 186-201; 57, 63-66, 68-78, 90, 94 | zgodne | n = A + 2B + 4C + 8D (192) |
| md:22 "dno gniazda na z = 4" | uklad.py:63-66 | zgodne | z_top(8) - depth(4); dane |
| md:22 "promien dolny z kata 15 deg" | uklad.py:75-78, 284 | zgodne | okragle: d_bottom/2 z pliku (sprawdzany 284); rynienka: liczony z tan15 (78) |
| md:24 "JSON: poczatek w srodku gornej powierzchni; STL gora na z = thickness; Z_TOP tylko domyslna" | uklad.py:4-6, 23, 57, 342 | zgodne | |
| md:27 "BladUkladu, podklasa ValueError, komunikat 'plik X: gniazdo N: brak d_top'" | uklad.py:41, 212-213, 271 | zgodne | |
| md:27 wymagane klucze plate, thickness, markers, code_dimples, sockets (>= 1) | uklad.py:217-219, 257-258 | zgodne | |
| md:27 "type in {round, trough}" | uklad.py:266-267 | zgodne | |
| md:27 pola zalezne od typu | uklad.py:268-273 | zgodne | |
| md:27 "unikalne id" | uklad.py:274-276 | zgodne | id musi byc int (nie bool) |
| md:27 "0 < depth <= thickness" | uklad.py:277-278 | zgodne | |
| md:27 "d_bottom zgodne z 15 deg (+/-0,01 mm)" | uklad.py:284-285 | zgodne | dodatkowo 282-283: 0 < d_bottom <= d_top (nie w opisie) |
| md:27 "kazde gniazdo w obrysie plytki" | uklad.py:286-292 | zgodne | okragle: 36 punktow (286); rynienki: 72 punkty stadionu (290) |
| md:27 "dodatkowe klucze w znacznikach i dolkach ignorowane" | uklad.py:244-252, 346, 351 | zgodne | |
| md:28 "shape opcjonalne: square (domyslnie, size) albo round (d)" | uklad.py:220-225, 239-242 | zgodne | |
| md:28 "Ksztalt wplywa TYLKO na sprawdzenie 'gniazdo w obrysie'" | uklad.py:223-225, 231-232, 328, 358 | ROZJAZD (drobny) | ksztalt decyduje tez: ktore pole wymiaru jest wymagane (size/d), czy flat jest dozwolony, czy UkladPlytki.d jest ustawione; size dla round = d["size"] gdy klucz jest (328) |
| md:28 "notch opcjonalny" | uklad.py:217 (komentarz), 352 | zgodne | notch nie jest walidowany |
| md:28 "flat (angle_deg, chord_w, dist) tylko przy round -> UkladPlytki.flat" | uklad.py:229-237, 359 | zgodne | walidacja 0 < dist < d/2 i chord_w > 0 (236) - nie w opisie |
| md:29 "plytka_bazowa.stl pomijany bez ostrzezenia" | uklad.py:28, 300-301 | zgodne | |
| md:30 "R59 kwadrat: shape square + 4 dolki (D na (-45;-27)); R54: bez shape, 3 dolki - kod czyta oba" | uklad.py:220, 253-255 | zgodne | dane zgodne |
| md:31 "dolki A, B, C, opcjonalnie D (dla przyszlych plytek okraglych n8/n9)" | uklad.py:26, 253-255 | ROZJAZD (drobny) | bit D maja tez kwadraty R59 i okragle ramkowe; kod wymaga kolejnosci dokladnie [A,B,C] albo [A,B,C,D] (254) - nie w opisie |
| md:31 "bity_z_numeru(n, liczba_bitow=3) -> ValueError poza 0..2^k-1" | uklad.py:195-201 | zgodne | dodatkowo liczba_bitow tylko 3 albo 4 (197); bool odrzucony (199) |
| md:31 "numer_z_bitow tylko bool/0/1" | uklad.py:187-192 | zgodne | |
| md:32 "numery tylko z plytka_n<numer>.stl (re.fullmatch); inne .stl z ostrzezeniem" | uklad.py:27, 298, 302-303 | zgodne | |
| md:32 "numer wiekszy niz pozwalaja dolki -> blad" | uklad.py:306-307 | ROZJAZD (drobny) | kod odrzuca tez numer 0 (dozwolone 1..2^k-1) |
| md:33 najblizsze_gniazdo (margines, najglebiej, None) | uklad.py:165-174 | zgodne | |
| md:33 odleglosc do obrysu: okragle hypot - r, rynienka stadion | uklad.py:86-88, 94-102 | zgodne | |
| md:33 "72 punkty stadionu; R54 46,18 / 46,93; R59 45,93 / 46,41" | uklad.py:290 | zgodne | (dane) analitycznie: R54 wieczorna 38,71 + 7,5 = 46,21 (72 punkty daja mniej), R54 poranna 46,93, R59 wieczorna gn 17/19 = 45,93, R59 poranna gn 22/24 = 46,41 |
| md:33 "Gniazdo.obrys(n)" | uklad.py:104-117 | zgodne | |
| md:34 "KAT_SCIANKI_DEG" | uklad.py:24 | zgodne | 15.0 |
| md:35 "hole_d, kieszenie, relief, wyciecie D nie modelowane; to samo dla pol R58" | uklad.py:327-360 | zgodne | notch jest trzymany jako dict (352), bez uzycia w uklad.py |
| md:22 kryterium testow | (test) | nie sprawdzano | |

W kodzie, a nie w opisie (uklad.py):
- stale: `TYPY_GNIAZD` (25), `BITY_KODU = ("A","B","C","D")` (26), `WZOR_PLIKU_PLYTKI = plytka_n(\d+)\.stl` (27), `PLIK_PLYTKI_BAZOWEJ = "plytka_bazowa.stl"` (28), `WZOR_WERSJI_UKLADU = _r\d+$` (29), `Z_TOP = 8.0` (23), `KATALOG_MODELI` (22).
- klasy `Znacznik` (120-126), `Dolek` (129-135); `UkladPlytki.liczba_bitow` (182-184); `Gniazdo.okragle` (59-61); `Gniazdo.angle` (56).
- walidacja rynienki: `min(l,w)/2 > depth*tan15` (288-289).
- brak plikow `plytka_n*.stl` nie jest bledem wczytania: `numery = []` (295-309, 356).

### 1.2 katalog (katalog.md vs katalog.py; CLI w narzedzia\katalog_projektow.py)

| opis | kod | stan | roznica |
|---|---|---|---|
| md:3 "podfoldery _* pomijane" | katalog.py:119 -> synth.py:124-130 | zgodne | |
| md:3 "identyfikator 16 znakow SHA-256 zawartosci" | katalog.py:125 -> synth.py:119-121 | zgodne | |
| md:3 typ pracy korona/most/waxup/bez_lacznika/nieznany | katalog.py:28-30, 53-58 | zgodne | |
| md:3 lista cech (trojkaty, szczelnosc, objetosc, pole, bbox, obrys xy, wysokosc, hull, brzeg, exocad, gniazdo) | katalog.py:34-50, 61-86 | zgodne | pole `krawedzie_brzegu_mm` (48, 84) nie wymienione |
| md:3 "obrys xy ... po obrocie brzegiem do gory" | katalog.py:66-70 | zgodne | `cechy` uzywa zawsze orientacji "auto" (69); CLI `--orientacja` dziala tylko w `gniazdo_dla` (97, 127) - nie w opisie |
| md:3 "ta sama procedura co generator: kandydaci_gniazd + osadz_w_gniezdzie, seed 0" | katalog.py:100, 105 | zgodne | `gniazdo_dla` pomija duplikaty (typ, d_top / (l,w)) (101-104); kazdy projekt ma wlasne rng seed 0 (105) |
| md:3 "nazwy plikow nie trafiaja do katalogu; mapa osobno" | katalog.py:122, 129, 135, 147-153 | zgodne | `pominiete` = liczba (135) |
| md:5 "slownik plytek nazwa -> (uklad, wspolczynnik)" | katalog.py:111, 126-127 | zgodne | |
| md:5 CLI `--wyjscie dane/katalog.json --mapa dane/mapa_sciezek.json --orientacja --wspolczynnik 1.22 --bez-gniazd --plytki` | katalog_projektow.py:33-39 | zgodne | `WSPOLCZYNNIK_WIECZORNA = 1.22` (28) z komentarzem "srodek [synth]"; srodek [synth] 1,20-1,25 = 1,225 (porownaj.py:81 uzywa 1,225) |
| md:5 "domyslnie plytki kwadratowe: wieczorna, poranna, wieczorna_r54, poranna_r54" | katalog_projektow.py:47 | zgodne | filtr `not n.startswith("okragla_")` - wyklucza tez okragla_ramkowa_* |
| md:7 katalog.json (wersja, liczba, czas_s, plytki, pominiete, projekty) | katalog.py:130-137 | zgodne | WERSJA_KATALOGU = 1 (31) |
| md:7 mapa_sciezek.json id -> sciezka bezwzgledna | katalog.py:129 | zgodne | `str(p.resolve())` |
| md:7 katalog.wczytaj(plik) -> dict[id, Projekt] | katalog.py:141-144 | zgodne | |
| md:7 "na stdout tabela bez nazw (streszczenie)" | katalog.py:156-169 | zgodne | |
| md:12 wzor nazwy exocad; zeby = ostatnia grupa dwucyfrowa przed typem | katalog.py:28 | zgodne | regex IGNORECASE; docstring katalog.py:11 podaje "waxup_slm" jako typ, regex dopuszcza `_slm` po kazdym typie |
| md:13 "plik ..._cad.stl -> brzeg na dole z konwencji exocad; heurystyka tylko informacyjnie" | synth.py:209-210; katalog.py:64-65, 83 | zgodne | |
| md:14 "objetosc nieszczelnej przyblizona (abs); hull_mm3 stabilne" | katalog.py:77, 82 | zgodne | |
| md:15 liczby pojemnosci R59 (17 projektow, 20 seedow) | (pomiar) | nie do sprawdzenia w kodzie | |
| md:16 "R54: wieczorna x1,22, poranna x1,0 (CLI)" | katalog_projektow.py:28, 49 | zgodne | 49: `S.WSPOLCZYNNIK_PORANNA[0] if S.poranna(nazwa) else a.wspolczynnik` |
| md:16 "praca nie moze wisiec > 1,5 mm nad dnem" | synth.py:40, 764 | zgodne | MAKS_UNIESIENIE = 1.5 |
| md:16 "mosty szersze niz 15 / 13 mm po skurczu nie wejda" | synth.py:758-759 | ROZJAZD (prog) | kod odrzuca rynienke juz przy szerokosci > w - 0,4 (14,6 / 12,6 mm) albo dlugosci > l - 1,0 (59 / 49 mm) |
| md:17 "nie ma jeszcze: Cyrkon/Prywatne, MillBox, SQLite, miniatur" | katalog.py (calosc) | zgodne | w katalog.py tego nie ma |
| md:9 kryterium testow | (test) | nie sprawdzano | |

W kodzie, a nie w opisie (katalog.py): `zapisz()` (147-153), `TYP_NIEZNANY` (30), `TYPY` (29), nazwy funkcji `typ_i_zeby_z_nazwy` (53), `cechy` (61), `gniazdo_dla` (89; zwraca `{"typ": None, "powod": ...}` gdy nie miesci sie - 107-108), `zbuduj` (111).

### 1.3 metryki (metryki.md vs metryki.py; CLI w narzedzia\raport_metryk.py)

| opis | kod | stan | roznica |
|---|---|---|---|
| md:3 "strona do 60 linii" | metryki.py:539-602 | nie znaleziono w kodzie | 60 jest tylko w docstringu (540); kod nie obcina strony |
| md:3 "progi w jednym slowniku, wartosc rowna progowi zalicza" | metryki.py:68-78, 88-93 | zgodne | |
| md:3 "M2 z dopiskiem 'wymaga zmiany schematu'" | metryki.py:79-84, 452-453, 488 | zgodne | |
| md:5 "tylko biblioteka standardowa + baza, session, session_rano" | metryki.py:39-48 | zgodne | |
| md:9-11 CLI --od --do --tryb --baza --ustawienia --json | raport_metryk.py:41-46 | zgodne | |
| md:11 "bez --od 7 dob konczacych sie na --do" | raport_metryk.py:66; metryki.py:54 | zgodne | od = do - (7-1) |
| md:11 "tryb wieczor/rano/oba (domyslnie)" | metryki.py:51-52, 457, 467-468 | zgodne | |
| md:11 "metryki trybu pominietego nie maja wiersza; stabilnosc i M2 zawsze" | metryki.py:427-454 | zgodne | |
| md:11 "baza tylko do odczytu (baza.otworz(tylko_odczyt=True))" | raport_metryk.py:72 | zgodne | |
| md:11 "bez ustawien: 6:00; 6/14/22; 0,6" | metryki.py:140-141; session.py:56-57; session_rano.py:79 | zgodne | |
| md:11 kody wyjscia 0/3/4/2 | metryki.py:82, 493-496; raport_metryk.py:36, 50 | zgodne | |
| md:13 sygnatura `policz(...)` i wartosci domyslne | metryki.py:457-459 | zgodne | |
| md:13 strona, ocena, bez_kandydata, posiedzenia, sprawdz_okres, biezaca_doba, parametry_z_ustawien | metryki.py:539, 88, 146, 116, 122, 133, 138 | zgodne | |
| md:13 stale PROGI, TRYBY, PRZERWA_MIN, STATUSY_POWTORZONE, KLASY_Z_PRAWDA, OKRES_DOMYSLNY_DOB, KOD_*, OCENA_* | metryki.py:68, 52, 53, 56, 57, 54, 82, 80-81 | zgodne | |
| md:13 pola wyniku i wierszy | metryki.py:479-496, 420-424 | zgodne | |
| md:15 stan_wieczoru dla kazdej doby; stan_pieca dla zamknietych piecow | metryki.py:267, 331-332 | zgodne | |
| md:15 "nie czyta decyzje.operator" | metryki.py:211 | zgodne | SELECT d.czas, d.praca_id, d.skan_id |
| md:15 "_SesjaOdczyt/_SesjaRanoOdczyt: do_dofrezowania, konflikty, wynik_pieca puste" | metryki.py:155-171 | zgodne | wynik_pieca zwraca None |
| md:15 migawka (backup jednym krokiem) | metryki.py:174-186 | zgodne | |
| md:15 "baza rok 2 MB: do 2 ms; 203 MB: ok. 180 ms" | metryki.py:176 (docstring) | ROZJAZD (liczby opisu) | docstring: "2 MB - ok. 1 ms; 200 MB - ok. 0,3 s" |
| md:15 "PRAGMA query_only = ON" | metryki.py:185 | zgodne | |
| md:21 falszywe alarmy: tylko skany PRZYJETE; bez do_powtorzenia; para ponownego skanu | metryki.py:269-308, 320 | zgodne | z pary bez odpowiedzi pomijany: nowszy gdy tylko starszy ma decyzje, inaczej starszy (282) |
| md:21 prog <= 15 % | metryki.py:69 | zgodne | |
| md:22 top-1/top-2: piece zamkniete z sesje_pieca.data; mianownik; chybienie "bez projektu" | metryki.py:327-354 | zgodne | praca z `klasa is None` pomijana (336) - nie w opisie |
| md:22 progi >= 85 % / >= 95 % | metryki.py:70-71 | zgodne | |
| md:23 nieznane: brak 1. kandydata / 1. ponizej progu / zaden z 2 nie w indeksie | metryki.py:146-152, 309-311, 340-341 | ROZJAZD (brzegowy) | wieczor: lista budowana z pominieciem pustego kandydata 1, wiec kandydat 2 staje sie "1." (309-310); rano: przekazana cala lista `kandydaci` z stan_pieca, bez obciecia do 2 (340-341) |
| md:23 "szara praca z kandydatem >= progu = dwuznaczne" | metryki.py:313 | ROZJAZD (drobny) | warunek `p["sha16"] is None` - bez sprawdzenia koloru "szary" |
| md:23 prog <= 10 % | metryki.py:72-73 | zgodne | |
| md:24 czas przy stanowisku (chwile, zastany, system/podglad, tryb najblizszego skanu, posiedzenia, srednia, > 20 min) | metryki.py:198-238, 104-113, 249-261 | zgodne | |
| md:24 prog <= 20 min | metryki.py:74 | zgodne | |
| md:25 skany powtorzone (statusy, bez importu) | metryki.py:56, 190-195, 315-317, 356-364 | zgodne | |
| md:25 prog <= 5 % | metryki.py:75-76 | zgodne | |
| md:26 awarie (restart bez stop, silnik_nie_startuje, wrocil sam), dziennik po id | metryki.py:374-417 | zgodne | silnik bez rozstrzygniecia na koncu dziennika = awaria (403-404) |
| md:26 "ocena tylko gdy w okresie dni pracy > 0" | metryki.py:447 | zgodne | |
| md:26 "seria < 5, bez awarii w historii i dni pracy < 5 = za krotki okres" | metryki.py:449 | ROZJAZD (nieostre) | kod porownuje `dni_historii` (wszystkie doby z wpisami przed koncem okresu, 405), nie `dni_pracy` (doby okresu, 412) |
| md:26 prog >= 5 dni | metryki.py:77 | zgodne | |
| md:27 M2 bez wartosci, nie wplywa na kod | metryki.py:452-453, 493-496 | zgodne | PROG_WYKRYWALNOSCI = 0.80 (79) |
| md:29 informacyjnie: klasy, dwuznaczne, piece niezamkniete, czas pieca, uruchomiony bez stop | metryki.py:365-371, 417, 588 | zgodne | |
| md:39 dane osobowe | metryki.py (calosc) | zgodne | brak nazw w SELECT |
| md:53 kryterium testow | (test) | nie sprawdzano | |
| md:57 "PRZERWA_MIN = 10" | metryki.py:53 | zgodne | |
| md:58 "start_skanu do trybu najblizszego skanu (najwyzej 10 min)" | metryki.py:231-235 | zgodne | |
| md:60 "granice okresu: ta sama formula co Sesja.doba" | metryki.py:471-473 | zgodne | |

W kodzie, a nie w opisie (metryki.py): `WERSJA = "etap3-A10r4"` (50), `STATUS_IMPORT = "import"` (55), `KOLOR_ALARMU = "czerwony"` (58), `TYP_START/TYP_STOP/TYP_SILNIK/TYP_START_SKANU` (59), `ZRODLO_OKNA = "ui"` (60), `TYP_NOWY_SKAN` (61), `TYP_SKAN_PRZYJETY` (62), `TYP_ODRZUCONY` (63), `AWARIA_RESTART/AWARIA_SILNIK/SILNIK_WROCIL` (64), `PROG_WYKRYWALNOSCI = 0.80` (79), `OCENA_ZA_KROTKI` (81), `POWOD_M2` (83), `MAX_DOB_NA_STRONIE = 5` (85); funkcja publiczna `migawka` (174) nie jest na liscie API (wymieniona w "Skad dane").

### 1.4 synth (synth.md vs synth.py)

| opis | kod | stan | roznica |
|---|---|---|---|
| md:3 "przechyl do 4 deg" | synth.py:737 | zgodne | |
| md:3 ubytki fi0,2-1,5 z [inspect], pas 1,5 mm, glebokosc 0,7 r | synth.py:43, 814-817; ustawienia.przyklad.toml:57-59 | zgodne | |
| md:3 K6 rozmiar 0,08-0,40 | synth.py:819; ustawienia.przyklad.toml:78-79 | zgodne | |
| md:3 szum sigma [synth] 0,03 wzdluz normalnych | synth.py:538-547, 812; toml:74 | zgodne | szum tez na siatce plytki (798) |
| md:3 "drgniecie: kopia 50 % siatki przesunieta o 0,08-0,15" | synth.py:637-649 | ROZJAZD (drobny) | 0,08-0,15 zgodne (639); "polowa" = trojkaty po jednej stronie losowej plaszczyzny przez centroid (645-647), nie dokladnie 50 % |
| md:3 "plytka zageszczona wokol znacznikow i dolkow, bez spodu" | synth.py:780-798 | zgodne | szczegoly nieopisane: znaczniki d/2+1,5, dolki d/2+1,0, tylko z > thickness-3,5, max_edge 0,12; spod = trojkaty z srodkiem z <= 0,5 usuniete |
| md:5 nazwy ukladow; "poranna = typ bez przyrostka konczy sie na poranna, skala 1,0" | synth.py:804-806, 813 | zgodne | |
| md:5 "Opcje: pola None = wartosci z ustawienia.toml; Opcje.z_toml(ust, plytka)" | synth.py:851-856, 862-867 | ROZJAZD (czesciowo) | `Opcje()` bez z_toml uzupelnia pola None wartosciami dla "wieczorna" (853) - takze gdy chodzi o plytke poranna (wspolczynnik 1,20-1,25) |
| md:5 --wspolczynnik X | synth.py:1207-1208, 1253 | zgodne | |
| md:5 --orientacja | synth.py:1209, 191-219 | zgodne | |
| md:5 "--poza-uklad: obrot 0..360, przechyl 0..3, przesuniecie +/-20 mm" | synth.py:1106-1112 | ROZJAZD (drobny) | kod przesuwa tez w z o +/-5 mm (1111) |
| md:5 "--pole D: kolo +/-1,5 mm, zageszczenie 0,4 mm" | synth.py:1070-1075, 1083-1103 | zgodne | |
| md:5 "--bokiem p: 90 +/- 20 deg, 1/3 do gory nogami, normalna z < -0,15 usunieta" | synth.py:53, 574-589 | zgodne | |
| md:5 "--pokrycie: 30-60 % w 2-4 plamach" | synth.py:592-620, 1214 | zgodne | rng.integers(2,5) |
| md:5 "--poprawka: g(1-(rho/R)^2)^2, R 1,5-3, g 0,15-0,4" | synth.py:550-571 | zgodne | |
| md:5 "ubytki/poprawki PRZED obrotem bokiem" | synth.py:963-995 | zgodne | |
| md:5 "widoczny: >= 3 wierzcholki na sferze +/-0,01; wersja 1: w promieniu 0,5 r" | synth.py:623-634, 1027-1032 | zgodne | wersja 1: r = max(0,5 r, 0,06) (633) - minimum 0,06 nie w opisie; sprawdzane tylko gdy pokrycie < 1 (1027) |
| md:5 --wersja-ubytkow 2/1, domyslnie 2 | synth.py:1216-1217 | zgodne | |
| md:5 --odstep-ubytku domyslnie 0,05 | synth.py:1218-1219; toml:77 | zgodne | |
| md:5 --krawedz domyslnie 0-0 | synth.py:1220-1221 | zgodne | |
| md:5 --krawedz-rozmiar / --krawedz-rozmiary / --krawedz-polozenie | synth.py:1222-1227 | zgodne | domyslnie srodek,zewn,wewn |
| md:5 --pamiec-linii | synth.py:1228-1229, 1270-1271 | zgodne | |
| md:7 nazwa skan_<uklad>_n<numer>_s<seed>.stl | synth.py:1278 | zgodne | seed z zerami do 4 cyfr (`s{seed:04d}`) |
| md:7 pole plytka = nazwa ukladu | synth.py:1055 | zgodne | |
| md:7 "pominiete ... (takze ostrzezenie na stdout)" | synth.py:1064-1068 | ROZJAZD (drobny) | `warnings.warn` - standardowo stderr, nie stdout |
| md:7 mapa_projektow.json w katalogu nad wyjsciem | synth.py:1273 | zgodne | |
| md:11 projekt = 16 znakow SHA-256 | synth.py:119-121, 1041 | zgodne | |
| md:16 "heurystyka: kat > 40 deg, pas 20 %; gdy po zadnej stronie nie ma krawedzi albo stosunek < 1,5 -> brzeg na dole z ostrzezeniem" | synth.py:158, 178-183, 211-218 | ROZJAZD (drobny) | warunek "niejasny" to `max(dol,gora) < 1.0` mm (nie zero) albo `max < 1.5 * min` (181) |
| md:16 (brak wzmianki) | synth.py:209-210 | nie w opisie | w trybie auto plik `..._cad.stl` -> brzeg na dole bez heurystyki (opisane w katalog.md:13, nie w synth.md) |
| md:20 PROG_MOSTU_MM = 20; okragle od najmniejszego >= 0,55 szerokosci; potem rynienki | synth.py:55, 700-712 | zgodne | |
| md:21 jedna rynienka = jedna praca | synth.py:1006 | zgodne | zajete gniazdo usuwane z listy wolnych |
| md:22 "numer losowany z uk.numery tylko bez --numer" | synth.py:1276-1277 | zgodne | |
| md:23 mosty wzdluz rynienki; sciana stadionu z * tan15 | synth.py:652-675, 735-736 | zgodne | |
| md:24 "przesuniecie przed uniesieniem; MAKS_UNIESIENIE 1,5; przenikanie <= 1e-6 -> AssertionError" | synth.py:40-41, 744, 764-773 | zgodne | luz_xy = 0,6 (723) nie w opisie |
| md:25 "otwor fi3 nie modelowany" | synth.py:657-697 | zgodne | |
| md:26 geometria P4 (1,6 r + 0,3; bisekcja; sfera co odstep; 4000 kierunkow; znak Open3D / normalna) | synth.py:49, 278-391 | zgodne | |
| md:27 K6 (srodek na powierzchni, >= 2 mm + promienie, sciana > rozmiar + 0,15) | synth.py:47-48, 472-535 | zgodne | |
| md:28 "wytnij_ubytek losuje miejsca w pasie od ZWERYFIKOWANYCH stacji" | synth.py:448-454, 967-970 | ROZJAZD (czesciowo) | gdy praca nie ma zadnej zweryfikowanej stacji -> gorny pas z (452); pusty pas -> wszystkie wierzcholki (453-454); linie liczone tylko przy wersji != 1 (967) |
| md:29 szum na kazdy wierzcholek; wersja 1 bajtowo | synth.py:546, 222-275 | zgodne | |
| md:30 wykrywalny: glebokosc >= prog i srednica w zakresie | synth.py:925-928, 974, 985 | zgodne | 0,08/0,7*2 = 0,229 |
| md:31 wspolczynnik: wieczor [synth] min..max, rano WSPOLCZYNNIK_PORANNA = 1,0 | synth.py:42, 813 | zgodne | |
| md:32 walidacja wejsc, --nadpisz | synth.py:133-152, 235-236, 540-541, 869-923, 1120-1123, 1279-1280 | zgodne | |
| md:33 S5 (wektor drgniecia nie w prawdzie), S6 (prace_na_plytce cicho), S8 (scianki kieszeni), S10 (wczytaj_prawde) | synth.py:95, 945-948, 796-797, 1140-1146 | zgodne | |
| md:33 "S11: glob("*.stl") na POSIX pomija .STL" | synth.py:124-130 | ROZJAZD | kod uzywa `rglob("*")` + `p.suffix.lower() == ".stl"` - pliki .STL sa brane |
| md:13 kryterium testow | (test) | nie sprawdzano | |

W kodzie, a nie w opisie (synth.py): stale `TAN_SCIANKI` (39), `TOLERANCJA_PRZENIKANIA = 1e-6` (41), `WERSJE_UBYTKOW = (1,2)` (44), `POLOZENIA_UKRUSZEN` (45), `KLASY_POLOZENIA` (46), `PROB_UKRUSZENIA = 60` (50; uzywane tez jako liczba prob dla zwyklych ubytkow, 455), `ORIENTACJE` (51), `ULOZENIA` (52), `WZOR_EXOCAD = _cad\.stl$` (54); walidacja K6 tylko z wersja 2 (903-904); domyslne `--ubytki 0-2` (1203), `--plytka wieczorna` (1198), `--wyjscie dane/syntetyczne` (1231); funkcje publiczne bez wzmianki: wczytaj_projekt, brzeg_z_heurystyki, plik_exocad, orientacja_brzegiem_do_gory, polozenie_wzgledem_brzegu, dodaj_szum, poprawka_reczna, obrot_bokiem, widok_z_gory, usun_plamy, ubytek_widoczny, drgniecie, szerokosc_pracy, os_glowna_deg, osadz_w_gniezdzie, siatka_plytki, poranna, generuj_plytke, przytnij_do_kola, losowa_poza_skanu, zapisz, dopisz_mape_projektow, klasa Material.

### 1.5 wspolczynniki.py i porownaj.py - pliki opisu

Potwierdzenie: w opisy_modulow\ NIE ma `wspolczynniki.md` ani `porownaj.md` (Glob opisy_modulow\*.md).
- opisy_modulow\README.md: tabela modulow (linie 7-23) nie ma wiersza "porownaj" ani "wspolczynniki"; `porownaj` wystepuje tylko w wierszach session (15: "wynik porownaj") i silnik (20).
- Ramki\stanowisko\README.md: `porownaj` opisany jako CLI (46, 53, 61-62, 67, 77, 80, 104, 110, 112, 171, 189 "porownaj (CLI: caly lancuch)"); `wspolczynniki` - brak.
- Inne opisy: `wspolczynniki.py` jest opisany w opisy_modulow\pula.md (linia 6 oraz tabela decyzji 37, 40, 41); docstring wspolczynniki.py:33 "Opis: opisy_modulow/pula.md". `porownaj` wspominany w plate.md (20, 63, 64), silnik.md (3, 18, 23, 37, 288), session.md:5, inspect.md, match.md, ui.md:3 - bez osobnego opisu.

**wspolczynniki.py - funkcje publiczne (wg docstringu):**
- `format_wspolczynnika(w)` (116) - 1.23 -> "1,2300" do komunikatow.
- `wspolczynnik_z_tekstu(wartosc, wspolczynnik_min=1.0, wspolczynnik_max=1.6)` (130) - liczba z tekstu "1,2250"/"1.2250" albo z liczby; ValueError z opisem.
- `data_z_tekstu(tekst)` (150) - data RRRR-MM-DD albo DD.MM.RRRR; ValueError.
- `wczytaj_csv(plik, *, dzis, okno_dat_dni, przyszlosc_dni, wspolczynnik_min, wspolczynnik_max)` (168) - wiersze CSV `plik;krazek;wspolczynnik;data`; kazdy blad = BladWspolczynnikow z numerami wszystkich blednych linii.
- `wczytaj_do_bazy(baza, plik, *, teraz, ...)` (273) - wczytuje CSV do `frezowania` w jednej transakcji (calosc albo nic) i laczy z indeksem; RaportCsv.
- `pliki_frezowan(baza, pierwsza, ostatnia)` (338) - nazwy plikow z aktualnych wierszy frezowania z dat (do indeksu folderow starych).
- `powiaz_frezowania(baza, *, okno=None)` (352) - laczy aktualne wiersze frezowania z indeksem; RaportPowiazania.
- `doba_robocza(teraz, granica_doby_godz=6)` (387) - data doby roboczej (ta sama regula co Sesja.doba).
- `wspolczynnik_krazka(baza, krazek)` (396) - ostatni wpis reczny krazka albo None.
- `wpisy_reczne(baza)` (406) - krazek -> wpisy reczne rosnaco.
- `stan_krazkow(baza, krazki=None)` (459) - krazek -> StanKrazka z wszystkich aktualnych wierszy.
- `wpisz_reczny(baza, krazek, wspolczynnik, *, operator, data=None, zmien=False, teraz=None, ...)` (481) - wpis reczny wspolczynnika krazka; zwraca id wiersza.
- klasy: `BladWspolczynnikow` (68), `WierszCsv` (77), `RaportCsv` (86, do_slownika), `RaportPowiazania` (105, do_slownika), `StanKrazka` (416).
Stale: `NAGLOWEK = ("plik","krazek","wspolczynnik","data")` (49), `WSPOLCZYNNIK_MIN = 1.0` (50), `WSPOLCZYNNIK_MAX = 1.6` (51), `ZRODLO_CSV = "csv"` (52), `ZRODLO_CSV_NIEAKTUALNY = "csv_nieaktualny"` (53), `ZRODLO_RECZNY = "reczny"` (54), `ZRODLO_RECZNY_POTWIERDZONY = "reczny_potwierdzony"` (55), `ZRODLA_RECZNE` (56), `OKNO_DAT_DNI = 60` (57), `PRZYSZLOSC_DNI = 2` (58), `GRANICA_DOBY_GODZ = 6` (59), `_PORCJA = 500` (60), `KODOWANIA = ("utf-8-sig","cp1250")` (61), `PODPOWIEDZ` (62), `BLEDOW_W_KOMUNIKACIE = 10` (63), `_DATA_PL` (64), `_DATA_ISO` (65), `_RECZNE_SQL` (393), `_POLA_WPISU` (429).

**porownaj.py - funkcje publiczne (wg docstringu; "brak" = bez docstringu, opis z kodu):**
- `gniazda_nie_sprawdzone(wynik)` (72) - numery gniazd ze statusem inspect `nie_sprawdzono`.
- `wspolczynnik_domyslny(plytka, ust)` (78, brak) - 1,0 gdy `S.poranna(plytka)`, inaczej (wspolczynnik_min + wspolczynnik_max)/2 z [synth].
- `ustawienia_bez_filtru(ust)` (84, brak) - kopia ust z `filtr_wymiar_mm` i `filtr_objetosc_udzial` = 1e9.
- `status_gniazda(status_match, inspekcja)` (88) - kolor gniazda: szary -> match; inaczej status inspect. Kod: `inspekcja` None albo pusta -> status match (90-91); status inspect bez mapowania albo "pominieto" (mapa -> None, 64) -> status match (92).
- `inspekcja_z_bledem(gniazdo, projekt, pokrycie, blad)` (100) - wpis inspekcji dla wyjatku: status `nie_sprawdzono` (zolte).
- `uklady_pasujace(stozki, ust, wybrany)` (115) - inne uklady z [plytki] o pasujacym rozstawie stozkow.
- `brak_ukladow_poprzednich(ust)` (136) - czy w [plytki] nie ma ukladu z przyrostkiem wersji.
- `uklady_z_ustawien(ust)` (144) - wszystkie uklady z [plytki], ktore da sie wczytac, w kolejnosci ustawien.
- `opis_ukladu(nazwa, uk=None)` (157) - opis ukladu dla czlowieka.
- `dopasuj_fragmenty(wyr, pula, ust, bez_filtru, inspekcja, podglad, start, statystyka)` (173) - match (+ inspect) kazdego fragmentu (bez drobnych). Kod: inspekcja tylko gdy `r.status != "szary"` i jest kandydat z transformacja (216); inaczej `inspekcja` = None -> status gniazda = status match (228 -> 90-91).
- `porownaj(skan, foldery, plytka, ust, ...)` (233) - caly lancuch na jednym skanie; plytka "auto" = rozpoznanie.
- `metryki(wynik, prawda, pula)` (352, brak) - metryki wzgledem prawdy (wyrownanie_ok gdy max przesuniecie < 0,05 mm (372), numer, top-1/top-2, blad pozy).
- `scenariusz(p)` (385) - dobrze / bokiem / czesciowo / drgniecie.
- `metryki_inspekcji(wynik, prawda, pula=None)` (408) - wykryte / falszywe ubytki per metoda i scenariusz.
- `tabela(wynik)` (494, brak) - tabela tekstowa wyniku.
- `mapa_png(wynik, uk, plik, px=0.1)` (534, brak) - mapa PNG plytki.
- `wczytaj_wpisy(plik)` (588) - wpisy puli per praca z CSV (wspolczynnik 0,5-2,0, 615).
- `main(argv=None)` (621) - wiersz polecen; `--bez-inspekcji` -> `inspekcja=False` (634, 667).
Stale: `KOLORY` (60-61), `STATUSY_GNIAZDA = ("zielony","czerwony","zolty","szary","pomaranczowy")` (62), `INSPECT_NA_STATUS = {ok: zielony, ubytek: czerwony, sprawdz: zolty, sprawdz_ulozenie: zolty, popraw_ulozenie: zolty, skan_ponownie: zolty, poprawka: pomaranczowy, nie_sprawdzono: zolty, pominieto: None}` (63-64), `OPISY_STATUSU` (65), `OPISY_INSPEKCJI` (67-68), `KLASY_POLOZENIA = ("krawedz","sciana","nieznane")` (69), `STATUS_BLEDU_INSPEKCJI = "nie_sprawdzono"` (95), `UWAGA_BLEDU_INSPEKCJI` = tekst "blad inspekcji" (96), `DLUGOSC_TRESCI_BLEDU = 300` (97), `PODPOWIEDZ_BRAK_R54` (132-133), `AUTO = "auto"` (141), `SCENARIUSZE = ("dobrze","bokiem","czesciowo","drgniecie")` (396), `KOLUMNY_WPISOW = ("plik","wspolczynnik","krazek","frezowanie_id","projekt_id")` (585).

---------------------------------------------------------------------------------------------------------------------
## CZESC 2 - uklad.json dziesieciu ukladow

Skroty: W = wieczorna, P = poranna; kw = kwadrat; ot = okragla testowa (okragla_*); or = okragla ramkowa (okragla_ramkowa_*).

### 2.1 Klucze najwyzszego poziomu (w kolejnosci z pliku)

| uklad | klucze |
|---|---|
| wieczorna, poranna (kw R59) | plate, version, units, coords, thickness, markers, code_dimples, shape, size, notch, magnet_pockets, number_relief, sockets, leds (14) |
| wieczorna_r54, poranna_r54 (kw R54) | plate, version, units, coords, size, thickness, markers, notch, code_dimples, magnet_pockets, number_relief, sockets, leds (13; brak `shape`) |
| okragla_wieczorna, okragla_poranna, okragla_wieczorna_r54, okragla_poranna_r54 (ot) | plate, version, units, coords, thickness, markers, code_dimples, shape, size, d, flat, magnet_pockets, number_relief, sockets, leds (15) |
| okragla_ramkowa_wieczorna, okragla_ramkowa_poranna (or) | plate, version, units, coords, thickness, markers, code_dimples, shape, size, d, flat, magnet_pockets, number_relief, cover_groove, key_slot, sockets, leds (17) |

### 2.2 Pola ogolne

| uklad | plate | version / units | coords (4. klucz) | shape | size | d | thickness | notch / flat | leds |
|---|---|---|---|---|---|---|---|---|---|
| wieczorna | wieczorna | v2 / mm | notch_corner "D = (+48, -48), przod-prawy" | square | 96 | - | 8 | notch D x 43..48, y -48..-43 | {} |
| poranna | poranna | v2 / mm | notch_corner (jw.) | square | 96 | - | 8 | notch (jw.) | {} |
| wieczorna_r54 | wieczorna | v2 / mm | notch_corner (jw.) | (brak -> square) | 96 | - | 8 | notch (jw.) | {} |
| poranna_r54 | poranna | v2 / mm | notch_corner (jw.) | (brak -> square) | 96 | - | 8 | notch (jw.) | {} |
| okragla_wieczorna | okragla_wieczorna | v2 / mm | flat "sciecie orientacyjne na kierunku -45 deg od +X ..." | round | 100.0 | 100.0 | 8 | flat: corner D, angle_deg -45.0, chord_w 16, dist 49.3559 | {} |
| okragla_poranna | okragla_poranna | jw. | jw. | round | 100.0 | 100.0 | 8 | flat jw. | {} |
| okragla_wieczorna_r54 | okragla_wieczorna | jw. | jw. | round | 100.0 | 100.0 | 8 | flat jw. | {} |
| okragla_poranna_r54 | okragla_poranna | jw. | jw. | round | 100.0 | 100.0 | 8 | flat jw. | {} |
| okragla_ramkowa_wieczorna | okragla_ramkowa_wieczorna | jw. | jw. | round | 100.0 | 100.0 | 8 | flat jw. | {} |
| okragla_ramkowa_poranna | okragla_ramkowa_poranna | jw. | jw. | round | 100.0 | 100.0 | 8 | flat jw. | {} |

(dist 49,3559 = sqrt(50^2 - 8^2) - sprawdzone recznie.) Pole `plate` w plikach *_r54 = to samo co w R59 (uklad.py nie czyta `plate`, uzywa nazwy z [plytki]).

### 2.3 Znaczniki (markers; wszystkie d = 5, depth = 3)

| rodzina | A | B | C | pliki |
|---|---|---|---|---|
| W R59 | (-35.5, -26.5) | (-31.0, 31.5) | (42.0, 14.5) | wieczorna, okragla_wieczorna, okragla_ramkowa_wieczorna |
| P R59 | (-30.5, -32.0) | (-37.5, 23.5) | (41.5, 16.0) | poranna, okragla_poranna, okragla_ramkowa_poranna |
| W R54 | (-35.5, -26.5) | (-35.5, 26.5) | (35.5, 26.5) | wieczorna_r54, okragla_wieczorna_r54 |
| P R54 | (-34.5, -28.0) | (-30.0, 32.5) | (30.0, 32.5) | poranna_r54, okragla_poranna_r54 |

### 2.4 Dolki kodu (code_dimples; wszystkie d = 2, depth = 1)

| pliki | A | B | C | D |
|---|---|---|---|---|
| wieczorna, poranna (kw R59) | (-45.0, -36) | (-45.0, -33) | (-45.0, -30) | (-45.0, -27.0) |
| wieczorna_r54, poranna_r54 (kw R54) | (-45.0, -36) | (-45.0, -33) | (-45.0, -30) | - (3 bity) |
| okragla_wieczorna, okragla_wieczorna_r54, okragla_ramkowa_wieczorna | (-4.5, -43.5) | (-1.5, -43.5) | (1.5, -43.5) | (4.5, -43.5) |
| okragla_poranna, okragla_ramkowa_poranna | (36.5, 18.5) | (36.5, 21.5) | (43.0, 6.0) | (43.0, 9.0) |
| okragla_poranna_r54 | (30.5, -31.0) | (30.5, -28.0) | (30.5, -25.0) | (30.5, -22.0) |

### 2.5 Gniazda (sockets; wszystkie depth = 4, hole_d = 3; rynienki angle 0, hole_count 4)

**W R59 (wieczorna, okragla_wieczorna, okragla_ramkowa_wieczorna) - 19 gniazd, identyczne we wszystkich trzech plikach:**
- id 1 trough (0, -30.2) l 60, w 15, hole_pitch 12
- id 2-7 round d_top 12, d_bottom 9.86, y -13.7, x 37.5 / 22.5 / 7.5 / -7.5 / -22.5 / -37.5
- id 8-12 round 15 / 12.86, y 2.75, x 36 / 18 / 0 / -18 / -36
- id 13-16 round 15 / 12.86, y 18.35, x 27 / 9 / -9 / -27
- id 17-19 round 15 / 12.86, y 33.95, x 18 / 0 / -18
- razem: 1 rynienka, 6 x fi12, 12 x fi15

**P R59 (poranna, okragla_poranna, okragla_ramkowa_poranna) - 24 gniazda, identyczne we wszystkich trzech plikach:**
- id 1 trough (0, -35.3) l 50, w 13, hole_pitch 10
- id 2-6 round 12.5 / 10.36, y -19.55, x 31 / 15.5 / 0 / -15.5 / -31
- id 7-12 round 12.5, y -6.1, x 38.75 / 23.25 / 7.75 / -7.75 / -23.25 / -38.75
- id 13-16 round 12.5, y 8, x 32.25 / 16.75 / -16.75 / -32.25
- id 17 round 15 / 12.86 (0, 8.75); id 18 round 15 (24.5, 22.85); id 19 round 15 (-24.5, 22.85)
- id 20-21 round 12.5, y 23.6, x 7.75 / -7.75
- id 22-24 round 12.5, y 37.05, x 15.5 / 0 / -15.5
- razem: 1 rynienka, 20 x fi12,5, 3 x fi15

**W R54 (wieczorna_r54, okragla_wieczorna_r54) - 20 gniazd, identyczne w obu plikach:**
- id 1 trough (0, -31.5) 60 x 15, pitch 12; id 20 trough (0, 31.5) 60 x 15, pitch 12
- id 2-7 round 12 / 9.86, y -15, x 37.5 ... -37.5 (co 15)
- id 8-14 round 9 / 6.86, y -1.5, x 36 / 24 / 12 / 0 / -12 / -24 / -36
- id 15-19 round 15 / 12.86, y 13.5, x 36 / 18 / 0 / -18 / -36
- razem: 2 rynienki, 6 x fi12, 7 x fi9, 5 x fi15

**P R54 (poranna_r54, okragla_poranna_r54) - 33 gniazda, identyczne w obu plikach:**
- id 1-3 round 7.5 / 5.36, y -41.25, x 10.5 / 0 / -10.5
- id 4 trough (0, -28) 50 x 13, pitch 10; id 33 trough (0, 35.95) 50 x 13, pitch 10
- id 5-11 round 10 / 7.86, y -13.5, x 39 / 26 / 13 / 0 / -13 / -26 / -39
- id 12-17 round 12.5 / 10.36, y 0.75, x 38.75 / 23.25 / 7.75 / -7.75 / -23.25 / -38.75
- id 18-25 round 7.5, y 13.6, x 36.75 / 26.25 / 15.75 / 5.25 / -5.25 / -15.75 / -26.25 / -36.75
- id 26-32 round 7.5, y 22.7, x 31.5 / 21 / 10.5 / 0 / -10.5 / -21 / -31.5
- razem: 2 rynienki, 18 x fi7,5, 7 x fi10, 6 x fi12,5

### 2.6 Klucze dodatkowe

| pliki | magnet_pockets | number_relief (x, y; text_h 5, relief_h 0.6) | cover_groove | key_slot |
|---|---|---|---|---|
| kw (4 pliki) | A (-42,-42), B (-42,42), C (42,42); d 5.2, depth 2.2 | (39.5, -44.5) | - | - |
| okragla_wieczorna, okragla_wieczorna_r54 | [] | (35.0, -26.5) | - | - |
| okragla_poranna | [] | (-44.0, 5.5) | - | - |
| okragla_poranna_r54 | [] | (36.5, -24.5) | - | - |
| okragla_ramkowa_wieczorna | A angle_deg 225 (-31.8198,-31.8198), B 135 (-31.8198,31.8198), C 45 (31.8198,31.8198); d 5.2, depth 2.2 | (35.0, -26.5) | z 2, w 1.0, depth 0.8 ("rowek na calym obwodzie (takze przez sciecie)...") | angle_deg -45.0, r0 46.0, w 3.6, h 5.0 ("rowek klucza od spodu...") |
| okragla_ramkowa_poranna | jak ramkowa wieczorna | (-44.0, 5.5) | jw. | jw. |

coords: kw = {origin, x, y, notch_corner}; okragle = {origin, x, y, flat}. units "mm", version "v2" we wszystkich 10 plikach. Strona (spod/wierzch) kieszeni magnesow nie jest zapisana w uklad.json (uklad.md:18 mowi "od spodu").

### 2.7 Roznice

**(a) okragla_wieczorna_r54 vs wieczorna_r54**
- `plate`: okragla_wieczorna vs wieczorna
- `coords`: klucz `flat` vs `notch_corner`
- `shape`: round vs brak (domyslnie square, uklad.py:220)
- `size`: 100.0 vs 96; `d`: 100.0 vs brak
- `flat` (angle -45, chord 16, dist 49.3559) vs `notch` (x 43..48, y -48..-43)
- `code_dimples`: 4 bity A-D na y = -43.5 (x -4.5/-1.5/1.5/4.5) vs 3 bity A-C na x = -45 (y -36/-33/-30)
- `magnet_pockets`: [] vs 3 kieszenie (+/-42, +/-42)
- `number_relief`: (35.0, -26.5) vs (39.5, -44.5)
- kolejnosc kluczy (kw R54 ma `size` przed `thickness`)
- BEZ roznic: version, units, thickness, markers (A/B/C), sockets (20 gniazd, id, polozenia, srednice, glebokosci), leds
- STL: plytka_n8 + plytka_bazowa vs plytka_n1..n3 (numery 8 vs 1-3; liczba bitow 4 vs 3 -> dozwolone numery 1..15 vs 1..7, uklad.py:306)

**(a') okragla_poranna_r54 vs poranna_r54** (dla porzadku): te same rodzaje roznic; dolki (30.5, -31/-28/-25/-22) vs (-45, -36/-33/-30); number_relief (36.5, -24.5) vs (39.5, -44.5); markers i 33 gniazda identyczne; STL n9 + bazowa vs n4..n6.

**(b) okragla_ramkowa_wieczorna vs okragla_wieczorna vs wieczorna**
- ramkowa vs okragla_wieczorna (testowa): `plate`; `magnet_pockets` 3 kieszenie na r = 45 (z polem angle_deg) vs []; dodatkowe `cover_groove` i `key_slot`. Wszystko inne identyczne (coords, thickness, markers, code_dimples, shape, size, d, flat, number_relief, sockets, leds). STL: n1, n2, n3 + bazowa vs n8 + bazowa.
- okragla_wieczorna vs wieczorna (kw R59): `plate`; coords flat/notch_corner; `code_dimples` (y -43.5, x -4.5..4.5 vs x -45, y -36..-27); `shape` round/square; `size` 100.0/96; `d` 100.0/brak; `flat` vs `notch`; `magnet_pockets` []/(+/-42); `number_relief` (35.0,-26.5)/(39.5,-44.5); kolejnosc kluczy. Identyczne: markers, 19 gniazd, thickness, version, units, leds.
- ramkowa vs wieczorna (kw): suma powyzszych; kieszenie (+/-31.8198) r 45 vs (+/-42) r 59,40; ramkowa ma cover_groove i key_slot. Numery plytek TE SAME (1, 2, 3).
- Istotne dla rozpoznania: wierzch ramkowej = wierzch okraglej testowej (stozki, gniazda, dolki, sciecie, obrys); od kwadratu rozni sie obrysem i polozeniem dolkow; od testowej - tylko numerem (1-3 vs 8) i spodem/obwodem (kieszenie, rowek pokrywki z = 2 +/- 0,5 mm pod wierzchem, rowek klucza od spodu h 5).

**(c) okragla_ramkowa_poranna vs okragla_poranna vs poranna**
- ramkowa vs okragla_poranna: `plate`; `magnet_pockets` (3 na r 45) vs []; `cover_groove`, `key_slot`. Reszta identyczna (w tym dolki (36.5,18.5)/(36.5,21.5)/(43,6)/(43,9), number_relief (-44.0, 5.5), 24 gniazda). STL n4, n5, n6 + bazowa vs n9 + bazowa.
- okragla_poranna vs poranna (kw R59): `plate`; coords; `code_dimples` (prawa strona, 2 pary vs x -45); `shape`; `size` 100.0/96; `d`; `flat` vs `notch`; `magnet_pockets` []/(+/-42); `number_relief` (-44.0, 5.5)/(39.5, -44.5). Identyczne: markers, 24 gniazda, thickness, version, units, leds.
- ramkowa vs poranna (kw): suma; numery plytek TE SAME (4, 5, 6).

### 2.8 Odleglosci dolkow kodu i kieszeni magnesow (liczone recznie)

Wzory (wspolrzedne xy, wartosc ujemna = nakladanie w rzucie xy):
- promien: r = sqrt(x^2 + y^2)
- do gniazda okraglego: sqrt((x-xg)^2 + (y-yg)^2) - d_top/2 - d/2
- do rynienki (angle 0, stadion): hypot(max(|x-xg| - (l-w)/2, 0), y-yg) - w/2 - d/2
- do stozka znacznika: sqrt((x-xm)^2 + (y-ym)^2) - 5/2 - d/2
(d/2 dolka = 1,0; d/2 kieszeni = 2,6.) Odleglosci w rzucie xy; kieszen ma depth 2,2 (wg uklad.md:18 od spodu, z 0..2,2), dno gniazda z = 4, stozek z 5..8.

**Dolki kodu**

| uklad(y) | dolek (x, y) | r | najblizsze gniazdo: rachunek -> wynik | najblizszy stozek: rachunek -> wynik |
|---|---|---|---|---|
| kw W R59 (wieczorna) | A (-45,-36) | 57.628 | ryn 1 (0,-30.2): hypot(22.5, 5.8)=23.236-7.5-1 -> 14.736 (gn 7: 23.528-6-1=16.528) | A (-35.5,-26.5): sqrt(9.5^2+9.5^2)=13.435-3.5 -> 9.935 |
| | B (-45,-33) | 55.803 | gn 7 (-37.5,-13.7) fi12: sqrt(7.5^2+19.3^2)=20.706-7 -> 13.706 | A: sqrt(9.5^2+6.5^2)=11.511-3.5 -> 8.011 |
| | C (-45,-30) | 54.083 | gn 7: sqrt(7.5^2+16.3^2)=17.943-7 -> 10.943 | A: 10.124-3.5 -> 6.624 |
| | D (-45,-27) | 52.479 | gn 7: sqrt(7.5^2+13.3^2)=15.269-7 -> 8.269 | A: 9.513-3.5 -> 6.013 |
| kw P R59 (poranna) | A (-45,-36) | 57.628 | gn 6 (-31,-19.55) fi12,5: sqrt(14^2+16.45^2)=21.601-7.25 -> 14.351 (ryn 1: 19.009) | A (-30.5,-32): sqrt(14.5^2+4^2)=15.042-3.5 -> 11.542 |
| | B (-45,-33) | 55.803 | gn 6: 19.414-7.25 -> 12.164 | A: 14.534-3.5 -> 11.034 |
| | C (-45,-30) | 54.083 | gn 6: 17.470-7.25 -> 10.220 | A: 14.637-3.5 -> 11.137 |
| | D (-45,-27) | 52.479 | gn 6: 15.859-7.25 -> 8.609 | A: 15.338-3.5 -> 11.838 |
| kw W R54 (wieczorna_r54) | A (-45,-36) | 57.628 | ryn 1 (0,-31.5): hypot(22.5, 4.5)=22.946-8.5 -> 14.446 (gn 7: 15.299) | A (-35.5,-26.5) -> 9.935 |
| | B (-45,-33) | 55.803 | gn 7 (-37.5,-15) fi12: sqrt(7.5^2+18^2)=19.5-7 -> 12.500 | A -> 8.011 |
| | C (-45,-30) | 54.083 | gn 7: sqrt(7.5^2+15^2)=16.771-7 -> 9.771 | A -> 6.624 |
| kw P R54 (poranna_r54) | A (-45,-36) | 57.628 | gn 11 (-39,-13.5) fi10: sqrt(6^2+22.5^2)=23.286-6 -> 17.286 (ryn 4: 20.181) | A (-34.5,-28): sqrt(10.5^2+8^2)=13.200-3.5 -> 9.700 |
| | B (-45,-33) | 55.803 | gn 11: 20.402-6 -> 14.402 | A: 11.630-3.5 -> 8.130 |
| | C (-45,-30) | 54.083 | gn 11: 17.557-6 -> 11.557 | A: 10.689-3.5 -> 7.189 |
| okragla_wieczorna, okragla_ramkowa_wieczorna (W R59) | A (-4.5,-43.5) | 43.732 | ryn 1 (0,-30.2): hypot(0, 13.3)=13.3-7.5-1 -> 4.800 | A (-35.5,-26.5): sqrt(31^2+17^2)=35.355-3.5 -> 31.855 |
| | B (-1.5,-43.5) | 43.526 | ryn 1 -> 4.800 | A: sqrt(34^2+17^2)=38.013-3.5 -> 34.513 |
| | C (1.5,-43.5) | 43.526 | ryn 1 -> 4.800 | A: 40.719-3.5 -> 37.219 |
| | D (4.5,-43.5) | 43.732 | ryn 1 -> 4.800 | A: 43.463-3.5 -> 39.963 |
| okragla_wieczorna_r54 (W R54) | A..D jak wyzej | 43.732 / 43.526 / 43.526 / 43.732 | ryn 1 (0,-31.5): 12.0-7.5-1 -> 3.500 (kazdy z 4) | A (-35.5,-26.5): 31.855 / 34.513 / 37.219 / 39.963 |
| okragla_poranna, okragla_ramkowa_poranna (P R59) | A (36.5,18.5) | 40.921 | gn 13 (32.25,8) fi12,5: sqrt(4.25^2+10.5^2)=11.328-7.25 -> 4.078 (gn 18: 4.264) | C (41.5,16): sqrt(5^2+2.5^2)=5.590-3.5 -> 2.090 |
| | B (36.5,21.5) | 42.361 | gn 18 (24.5,22.85) fi15: sqrt(12^2+1.35^2)=12.076-8.5 -> 3.576 | C: sqrt(5^2+5.5^2)=7.433-3.5 -> 3.933 |
| | C (43.0,6.0) | 43.417 | gn 13: sqrt(10.75^2+2^2)=10.935-7.25 -> 3.685 (gn 7: 5.575) | C: sqrt(1.5^2+10^2)=10.112-3.5 -> 6.612 |
| | D (43.0,9.0) | 43.932 | gn 13: sqrt(10.75^2+1^2)=10.796-7.25 -> 3.546 | C: sqrt(1.5^2+7^2)=7.159-3.5 -> 3.659 |
| okragla_poranna_r54 (P R54) | A (30.5,-31) | 43.489 | ryn 4 (0,-28): hypot(12, 3)=12.369-7.5 -> 4.869 | C (30,32.5): 63.502-3.5 -> 60.002 |
| | B (30.5,-28) | 41.404 | ryn 4: hypot(12, 0)=12-7.5 -> 4.500 | C: 57.002 |
| | C (30.5,-25) | 39.437 | ryn 4: 12.369-7.5 -> 4.869 (gn 6: 6.349) | C: 54.002 |
| | D (30.5,-22) | 37.607 | gn 6 (26,-13.5) fi10: sqrt(4.5^2+8.5^2)=9.618-6 -> 3.618 (ryn 4: 5.916) | C: 51.002 (A (-34.5,-28): 61.776) |

**Kieszenie magnesow** (okragle testowe ot: brak kieszeni, magnet_pockets = [])

| uklad(y) | kieszen (x, y) | r | najblizsze gniazdo: rachunek -> wynik | najblizszy stozek: rachunek -> wynik |
|---|---|---|---|---|
| kw W R59 (wieczorna) | A (-42,-42) | 59.397 | ryn 1 (0,-30.2): hypot(19.5, 11.8)=22.792-7.5-2.6 -> 12.692 | A (-35.5,-26.5): sqrt(6.5^2+15.5^2)=16.808-5.1 -> 11.708 |
| | B (-42,42) | 59.397 | gn 19 (-18,33.95) fi15: sqrt(24^2+8.05^2)=25.314-10.1 -> 15.214 | B (-31,31.5): sqrt(11^2+10.5^2)=15.207-5.1 -> 10.107 |
| | C (42,42) | 59.397 | gn 17 (18,33.95): -> 15.214 | C (42,14.5): 27.5-5.1 -> 22.400 |
| kw P R59 (poranna) | A (-42,-42) | 59.397 | ryn 1 (0,-35.3): hypot(23.5, 6.7)=24.436-6.5-2.6 -> 15.336 (gn 6: 16.150) | A (-30.5,-32): sqrt(11.5^2+10^2)=15.240-5.1 -> 10.140 |
| | B (-42,42) | 59.397 | gn 19 (-24.5,22.85): sqrt(17.5^2+19.15^2)=25.942-10.1 -> 15.842 | B (-37.5,23.5): sqrt(4.5^2+18.5^2)=19.039-5.1 -> 13.939 |
| | C (42,42) | 59.397 | gn 18 (24.5,22.85): -> 15.842 | C (41.5,16): 26.005-5.1 -> 20.905 |
| kw W R54 (wieczorna_r54) | A (-42,-42) | 59.397 | ryn 1 (0,-31.5): hypot(19.5, 10.5)=22.147-10.1 -> 12.047 | A: 11.708 |
| | B (-42,42) | 59.397 | ryn 20 (0,31.5): -> 12.047 | B (-35.5,26.5): 16.808-5.1 -> 11.708 |
| | C (42,42) | 59.397 | ryn 20: -> 12.047 | C (35.5,26.5): -> 11.708 |
| kw P R54 (poranna_r54) | A (-42,-42) | 59.397 | ryn 4 (0,-28): hypot(23.5, 14)=27.354-9.1 -> 18.254 | A (-34.5,-28): sqrt(7.5^2+14^2)=15.882-5.1 -> 10.782 |
| | B (-42,42) | 59.397 | ryn 33 (0,35.95): hypot(23.5, 6.05)=24.266-9.1 -> 15.166 (gn 32: 15.621) | B (-30,32.5): sqrt(12^2+9.5^2)=15.305-5.1 -> 10.205 |
| | C (42,42) | 59.397 | ryn 33: -> 15.166 | C (30,32.5): -> 10.205 |
| okragla_ramkowa_wieczorna | A (-31.8198,-31.8198) | 45.000 | ryn 1 (0,-30.2): hypot(9.3198, 1.6198)=9.4595-7.5-2.6 -> **-0.640** (gn 7: 10.389) | A (-35.5,-26.5): sqrt(3.6802^2+5.3198^2)=6.4687-5.1 -> 1.369 |
| | B (-31.8198,31.8198) | 45.000 | gn 19 (-18,33.95): sqrt(13.8198^2+2.1302^2)=13.983-10.1 -> 3.883 (gn 16: 4.206) | B (-31,31.5): sqrt(0.8198^2+0.3198^2)=0.880-5.1 -> **-4.220** |
| | C (31.8198,31.8198) | 45.000 | gn 17 (18,33.95): -> 3.883 (gn 13: 4.206) | C (42,14.5): sqrt(10.1802^2+17.3198^2)=20.090-5.1 -> 14.990 |
| okragla_ramkowa_poranna | A (-31.8198,-31.8198) | 45.000 | gn 6 (-31,-19.55) fi12,5: sqrt(0.8198^2+12.2698^2)=12.297-6.25-2.6 -> 3.447 (ryn 1: 4.667) | A (-30.5,-32): sqrt(1.3198^2+0.1802^2)=1.332-5.1 -> **-3.768** |
| | B (-31.8198,31.8198) | 45.000 | gn 19 (-24.5,22.85) fi15: sqrt(7.3198^2+8.9698^2)=11.577-10.1 -> 1.477 | B (-37.5,23.5): sqrt(5.6802^2+8.3198^2)=10.074-5.1 -> 4.974 |
| | C (31.8198,31.8198) | 45.000 | gn 18 (24.5,22.85): -> 1.477 | C (41.5,16): sqrt(9.6802^2+15.8198^2)=18.546-5.1 -> 13.446 |

Wartosci ujemne (nakladanie w rzucie xy): ramkowa W - kieszen A pod rynienka 1 (-0,640), kieszen B pod stozkiem B (-4,220); ramkowa P - kieszen A pod stozkiem A (-3,768). W osi z: kieszen 0..2,2 (jesli od spodu), dno gniazda/rynienki z = 4, wierzcholek stozka z = 5.
Dla porownania z plate.py: R_KSZTALTU_MIN = 47,5, PAS_KSZTALTU_Z = 3,0 (plate.py:75, 77) - rowek pokrywki (z 2 +/- 0,5 mm pod wierzchem, glebokosc 0,8) lezy w pasie z ocenianym przez `ksztalt_plytki`; kieszenie (r 45) i dolki (r <= 43,93) sa ponizej R_KSZTALTU_MIN.

### 2.9 Pliki w katalogach ukladow (Get-ChildItem, bajty)

| katalog | plik | bajty |
|---|---|---|
| wieczorna | plytka_n1.stl / n2 / n3 / uklad.json | 946584 / 956284 / 967084 / 4305 |
| poranna | plytka_n4.stl / n5 / n6 / uklad.json | 1095984 / 1113784 / 1107984 / 5106 |
| wieczorna_r54 | plytka_n1.stl / n2 / n3 / uklad.json | 911684 / 921784 / 932284 / 4358 |
| poranna_r54 | plytka_n4.stl / n5 / n6 / uklad.json | 1189084 / 1204884 / 1200984 / 6342 |
| okragla_wieczorna | plytka_bazowa.stl / plytka_n8.stl / uklad.json | 971484 / 985784 / 4243 |
| okragla_poranna | plytka_bazowa.stl / plytka_n9.stl / uklad.json | 1115584 / 1128884 / 5039 |
| okragla_wieczorna_r54 | plytka_bazowa.stl / plytka_n8.stl / uklad.json | 935784 / 950484 / 4403 |
| okragla_poranna_r54 | plytka_bazowa.stl / plytka_n9.stl / uklad.json | 1206384 / 1217584 / 6389 |
| okragla_ramkowa_wieczorna | plytka_bazowa.stl / n1 / n2 / n3 / uklad.json | 1113584 / 1105084 / 1114784 / 1125484 / 5044 |
| okragla_ramkowa_poranna | plytka_bazowa.stl / n4 / n5 / n6 / uklad.json | 1258284 / 1253884 / 1275984 / 1266684 / 5840 |

Razem 38 plikow (28 + 10).

---------------------------------------------------------------------------------------------------------------------
## CZESC 3 - rozroznianie plytki po NAZWIE albo NUMERZE

Wynik dla czterech nazw: RW = okragla_ramkowa_wieczorna, RP = okragla_ramkowa_poranna, W54 = okragla_wieczorna_r54, P54 = okragla_poranna_r54.

| plik:linia | warunek | RW | RP | W54 | P54 |
|---|---|---|---|---|---|
| uklad.py:29, 32-38 `typ_plytki` | regex `_r\d+$` usuniety | "okragla_ramkowa_wieczorna" (bez zmian) | "okragla_ramkowa_poranna" (bez zmian) | "okragla_wieczorna" | "okragla_poranna" |
| uklad.py:220-225, 240-242, 328, 358 | po polu `shape` (nie po nazwie) | round, d 100 | round | round | round |
| uklad.py:254 | bity [A,B,C] albo [A,B,C,D] | 4 bity | 4 | 4 | 4 |
| uklad.py:306 | numer 1 <= n < 2^liczba_dolkow | 1..15 (n1-n3 ok) | 1..15 (n4-n6 ok) | 1..15 (n8 ok) | 1..15 (n9 ok) |
| synth.py:804-806 `poranna()` | `typ_plytki(...).endswith("poranna")` | False | **True** | False | True |
| synth.py:813 `_z_ustawien` | wspolczynnik: poranna -> (1.0, 1.0), inaczej [synth] min..max | (1.20, 1.25) | (1.0, 1.0) | (1.20, 1.25) | (1.0, 1.0) |
| synth.py:851-856 `Opcje.__post_init__` | pola None wypelniane `_z_ustawien(..., "wieczorna")` (stala nazwa) | wieczorna | **wieczorna (1.20-1.25)** gdy Opcje() bez z_toml | wieczorna | **wieczorna** gdy Opcje() bez z_toml |
| synth.py:863 `Opcje.z_toml(plytka="wieczorna")` | domyslna nazwa | - | - | - | - |
| synth.py:1198 `--plytka` | domyslnie "wieczorna" | - | - | - | - |
| synth.py:1245-1247 main | `Opcje.z_toml(ust, a.plytka, ...)` | poprawnie (jak 813) | poprawnie (1.0) | poprawnie | poprawnie (1.0) |
| porownaj.py:78-81 `wspolczynnik_domyslny` | `S.poranna(plytka)` -> 1.0, inaczej srodek [synth] | 1.225 | **1.0** | 1.225 | 1.0 |
| porownaj.py:136-138 `brak_ukladow_poprzednich` | `typ_plytki(nazwa) != nazwa` = uklad "poprzedni" | nie poprzedni | nie poprzedni | poprzedni | poprzedni |
| porownaj.py:164-170 `opis_ukladu` | `typ.startswith("okragla")` (gdy uk None) / `uk.shape`; `typ.startswith("okragla_ramkowa_")`; `typ.endswith("poranna")`; wersja = reszta nazwy | "plytka wieczorna, okragla ramkowa (do ramki), nowy uklad gniazd (R59)" | "plytka poranna, okragla ramkowa (do ramki), nowy uklad gniazd (R59)" | "plytka wieczorna, okragla testowa (poza ramka), stary uklad gniazd (R54)" | "plytka poranna, okragla testowa (poza ramka), stary uklad gniazd (R54)" |
| porownaj.py:195 `dopasuj_fragmenty` | `bez_korekty` gdy `S.poranna(wyr.plytka)` (wyr.plytka = uk.nazwa, plate.py:687) | korekta skali stosowana | **korekta tylko mierzona** (jak poranna) | stosowana | tylko mierzona |
| porownaj.py:259, 320-322 | wspolczynnik None -> `wspolczynnik_domyslny` (recznie od razu, auto po rozpoznaniu) | 1.225 | 1.0 | 1.225 | 1.0 |
| porownaj.py:263 | pula z innym wspolczynnikiem odrzucana (auto, bez per_praca) | - | - | - | - |
| porownaj.py:535, 543, 575 `mapa_png` | po polu `uk.shape` | kolo d 100 | kolo | kolo | kolo |
| porownaj.py:641, 662 main | nazwa musi byc w [plytki]; wspolczynnik_domyslny | jak wyzej | jak wyzej | jak wyzej | jak wyzej |
| plate.py (caly) | po nazwie - BRAK (nazwy tylko w docstringach/komunikatach: 19, 303, 317, 760, 764) | - | - | - | - |
| plate.py:563-566 `plik_modelu_plytki` | numer w `uk.numery` -> ten STL, inaczej `uk.numery[0]` | n1 gdy numer None/obcy | n4 | n8 | n9 |
| plate.py:661-674 | numer podany > numer z dolkow > "nieznany" (ostrzezenie 667 gdy numer z dolkow nie ma STL) | ogolne | ogolne | ogolne | ogolne |
| plate.py:790, 805, 807, 854 `rozpoznaj_uklad` | numer liczy sie tylko gdy `in uk.numery` | numery [1,2,3] = te same co kw `wieczorna` | [4,5,6] = te same co kw `poranna` | [8] = te same co `okragla_wieczorna` | [9] = te same co `okragla_poranna` |
| plate.py:826-850 `rozpoznaj_uklad` | wybor: jedyny / numer podany (1 uklad) / numer z dolkow (1 uklad) / ksztalt (roznica >= 40 mm^2) / dolki_wykluczaja / domyslny = pierwszy uklad z `dolki_widoczne == 0` (pewny False) | `--numer 2`: pasuje do `wieczorna` i RW -> numer podany nie rozstrzyga (834), dalej dolki (837); gdy dolki i ksztalt nie rozstrzygaja -> galaz "domyslny" wybiera kwadrat `wieczorna` (pierwszy bez widocznych dolkow, kolejnosc [plytki]) z pewny=False | analogicznie: kwadrat `poranna` w galezi "domyslny" | W54 vs `wieczorna_r54`: numery [8] vs [1,2,3]; rozstrzyga numer (podany albo z dolkow) albo ksztalt | analogicznie z `poranna_r54` |
| plate.py:760-768 (docstring) | "numer podany przez czlowieka (n1-n6 = kwadrat, n8-n9 = kolo)" | docstring nieaktualny dla RW (n1-n3 = kolo); kod nie uzywa stalych zakresow, tylko `uk.numery` | jw. (n4-n6) | - | - |
| match.py | po nazwie / numerze - BRAK (bez_korekty przekazywany z porownaj; docstringi 934, 1138) | - | - | - | - |
| inspect.py | BRAK (779: `polozenie.startswith("krawedz")` - klasa ubytku, nie plytka) | - | - | - | - |
| katalog.py | BRAK | - | - | - | - |
| narzedzia\katalog_projektow.py:47 (poza lista, dla pelnosci) | domyslne plytki: `not n.startswith("okragla_")` | wykluczona | wykluczona | wykluczona | wykluczona |
| narzedzia\katalog_projektow.py:49 | `S.poranna(nazwa)` -> 1.0, inaczej `--wspolczynnik` (1.22) | 1.22 | 1.0 | 1.22 | 1.0 |
| wspolczynniki.py | BRAK (230, 233: koncowki nazw plikow STL w CSV, nie plytki) | - | - | - | - |
| metryki.py | BRAK (tylko tryb wieczor/rano) | - | - | - | - |

Odpowiedz na pytanie z zamowienia: plytka `okragla_ramkowa_poranna` jest w synth / porownaj uznana za poranna (synth.py:806 -> True): wspolczynnik domyslny 1,0 (porownaj.py:80), korekta skali tylko mierzona (porownaj.py:195), w generatorze (1.0, 1.0) przez `Opcje.z_toml` (synth.py:813, 1245). Wyjatek: `Opcje()` tworzone bez `z_toml` bierze wartosci "wieczorna" dla kazdej nazwy (synth.py:853). `okragla_poranna_r54` - tak samo (poranna). `okragla_ramkowa_wieczorna` i `okragla_wieczorna_r54` - wieczorne (1,225 w porownaj; 1,20-1,25 w synth; 1,22 w katalog_projektow).

Miejsca poza lista modulow, ktore tez rozrozniaja po nazwie (NIE przejrzane w tej czesci, tylko wskazane z Grep): session.py:78, 128-161 (`_WZOR_UKLADU`, `czesci_ukladu`, `rodzina_ukladu`, `numery_ramkowe`, `typ_plytki` - inna funkcja o tej samej nazwie co uklad.typ_plytki), 171-181 (`powod_nie_z_trybu`); session_rano.py:114, 121; silnik.py:494 (typ "poranna" z wspolczynnika = 1,0); aplikacja.py:766; kontroler_api.py:97, 1802, 3210, 4631; ustawienia.py:147-149; ui\czesci.py:740; statusy.py:555.

---------------------------------------------------------------------------------------------------------------------
## Czego nie przejrzano / ograniczenia
- Testy (testy\*.py) - nie czytane i nie uruchamiane; wszystkie "Kryterium dziala" oznaczone (test).
- plate.py przeczytany tylko w zakresie 540-878 + Grep po calym pliku (nazwy, numery, shape); `odczytaj_bity`, `zgodnosc_ukladu`, `potnij_na_fragmenty`, `ksztalt_plytki` - logika wewnetrzna nie analizowana.
- match.py, inspect.py - tylko Grep (nazwa/numer/plytka/uklad), bez czytania calosci.
- narzedzia\raport_metryk.py - tylko Grep (argumenty, kody, tylko_odczyt); narzedzia\katalog_projektow.py - tylko Grep.
- opisy_modulow\pula.md - tylko Grep (wzmianki o wspolczynniki); zgodnosci pula.md z wspolczynniki.py nie sprawdzano.
- session.py przeczytany tylko 125-184; session_rano.py, silnik.py, aplikacja.py, kontroler_api.py, ui - tylko wynik Grep.
- Pliki STL - tylko rozmiary; zawartosci (np. czy dolek D jest tylko w plytka_bazowa.stl, czy kieszenie sa od spodu) nie sprawdzano.
- Odleglosci w 2.8 liczone recznie z liczb w uklad.json (zaokraglenia do 0,001 mm); tylko w rzucie xy.
