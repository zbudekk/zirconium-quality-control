# Czesc B paczki "program przed skanerem": linie krawedzi brzegu, generator ukruszen K6 (P4), pas brzegu od linii i "nie sprawdzono" (P2)

Data: 2026-11-15/16. Wykonawca czesci B (galaz `czesc-b`, od `8b83da7` = origin/bp/r59). Zgoda wlasciciela 15.11.2026
na P2 i P4 z `raporty/testy_krawedz/WNIOSKI_I_DECYZJE_2026-11-09.md` pkt 4. Obliczenia: PC (`<PC-katalog>\app\b`),
na MSI tylko edycja i git. W raporcie wylacznie skroty projektow (16 znakow SHA-256). Wszystkie dane sa SZTUCZNE
(skanera nie ma) - to pomiar kodu, nie skanera.

**[usunieto w kopii: opis dostepu ssh]
odpowiedzial na 1 z 2 pingow, potem nic). Zrobione i odczytane: linie (17 projektow), geometria generatora przed / po
(680 ubytkow), zgodnosc wstecz seed 7001 (bajty i prawda), zestaw R59 "przed" i zestawy r54 "przed / po" (liczby
zbiorcze). NIE zrobione / nie odczytane: R59 "po", rozbicie r54 na przejscia i powody, zestaw K6 (generowanie ruszylo
w chwili zerwania polaczenia), geometria K6 po rozmiarach, porownaj na skanach seed 7001, czas inspect przed / po,
sprzatanie `dane` na PC. Polecenia do dokonczenia: pkt 8.

## 0. Wynik w skrocie

1. **Linie krawedzi brzegu (etap 1):** 17 / 17 projektow, 23 petle (korony 1, kazdy filar mostu / waxupu osobno,
   obwod powierzchni przylegania koron bez lacznika); 14 wiarygodnych, 9 czesciowych, 0 niepewnych; liczba
   zweryfikowanych przekrojow i wybrany wariant kazdego filaru = T9 w 23 z 23 petli. 3-9 s na projekt (raz).
2. **Generator (P4 a):** na tych samych 680 miejscach (17 projektow x 40, w pasie od linii) czasza ubytku w powietrzu
   (> 10 % pola) - przed **293 / 680** (na krawedzi **263 / 341**), po **25 / 680** (krawedz 22 / 341). Wszystkie 25
   przypadkow "po" leza na 2 siatkach (korony bez lacznika `5a3a03ddfb5d8577` 14, `a4d10c94db53a1a1` 11), w ktorych
   znak "wewnatrz bryly" jest sprzeczny z normalnymi w 16 % punktow przy powierzchni (oba programy - Open3D i trimesh -
   licza go tak samo, `is_volume` = False): tam "material" jest niejednoznaczny i ani generator, ani pomiar nie sa
   wiarygodne. Na pozostalych 15 siatkach: 0 czasz w powietrzu.
3. **K6 (P4 b):** ukruszenia celowe na srodku plaskiej krawedzi / narozniku zewn. / wewn. / scianie, 0,08-0,40 mm,
   srodek kuli NA powierzchni (testy: odleglosc < 1e-4 mm), rzeczywista glebokosc w prawdzie (testy: <= rozmiar,
   zgodna z niezaleznym pomiarem). Pomiaru na 17 projektach po rozmiarach i zestawu K6 nie ma (PC).
4. **Zgodnosc wstecz (P4 d):** te same seedy daja po P4 INNE skany: wersja 2 zmienia geometrie ubytku, a szum jest
   losowany na kazdy wierzcholek, wiec od pierwszej pracy z ubytkiem rozjezdza sie caly strumien losowy (seed 7001:
   inna liczba prac na 4 z 4 plytek). `--wersja-ubytkow 1` daje STL bajtowo rowny kodowi sprzed P4 (4 / 4 plytki
   seed 7001) i prawde rowna we wszystkich starych polach (4 / 4).
5. **P2 - zestawy r54 (40 skanow, 231 ubytkow, 136 prac calych), ten sam plate + match, inspect przed / po:**
   prace cale z czerwonym **0 -> 0**; z alarmem (zolte "sprawdz") 1 -> 0; **"nie sprawdzono" 0 -> 39 z 136 (29 %)**;
   falszywe miejsca 3 -> 0. Wykrycia dowolna metoda **215 -> 186 / 231** (krawedz 94 -> 93 / 102, sciana **121 -> 93 /
   129**), czerwone 88 -> 76. Spadek dotyczy prawie wylacznie scian: stary generator losowal ubytki w pasie 1,5 mm od
   najwyzszego punktu pracy (takze na przeslach, lacznikach i scianach daleko od linii brzegu), a nowy pas tych miejsc
   juz nie obejmuje (przyczyna potwierdzona na 1 skanie; rozbicie wg odleglosci od linii - niezweryfikowane, PC).
6. **P2 - zestaw R59 "przed"** (nowy kod, `pas_brzegu_od = "plaszczyzna"`): liczby R59 z 14.11 odtworzone co do jednej
   (221 / 248, prace cale 0 czerwonych i 0 alarmow ze 127, falszywe 7 / 2 czerwone, top-1 382 / 397) - sciezka
   "przed" = stary kod. Liczb "po" dla R59 nie ma (PC).
7. **Filary mostow:** przed 7 z 12 filarow prac wieloczlonowych lezy w calosci ponizej pasa 1,5 mm (T9 pisal 6 z 12 -
   z tabeli T9 wynika 7); po: pas idzie za linia kazdego filaru, 0 z 12 poza pasem; 6 z 12 filarow ma linie
   "czesciowa" (przy lacznikach) i z progiem 0,9 dostanie "nie sprawdzono" na kazdej pracy.
8. pytest: 294 passed / 3 skipped / **1 failed** (`test_match.py`, plik poza moja lista - przyczyna i jednolinijkowa
   poprawka w pkt 2).

## 1. Co zmieniono i dlaczego

### Etap 1 - linie krawedzi brzegu (`stanowisko/krawedz.py`, nowy modul)

- Prototyp T9 (`testy_krawedz/T9/skrypty/t9_linie.py` + `t9_wybor.py`) przeniesiony do programu bez zmiany konstrukcji
  i stalych: mapa wysokosci z gory, niecki (wneka filaru albo kanal sruby), dzial wodny Meyera, przekroje co 0,5 st.,
  narozniki O / I, warianty startu 1 / 2 / 3, wybor wariantu, weryfikacja kazdego przekroju (2 zgodne wyznaczenia O do
  0,10 mm, szerokosc plaskiej krawedzi 0,10-1,50 mm), werdykt petli (wiarygodna >= 90 % i ciag <= 10 st.,
  czesciowa >= 60 %, inaczej niepewna). Bez zaleznosci od plikow spoza repo (potrzebne funkcje T3 przeniesione do modulu).
- Dodane: linia S (srodek plaskiej krawedzi zrzutowany NA powierzchnie projektu - do K6), jawny brak linii (`stan` =
  `brak`, `uwagi`), pamiec podreczna per projekt niezalezna od skali i przesuniecia (w pamieci procesu; opcjonalnie na
  dysku, plik `.npz` na projekt), `stacje()` do drzew odleglosci, `klucz_projektu()`.
- Zmiany wydajnosciowe bez zmiany wyniku: podsiatka filaru ograniczona takze w z (4 mm pod grzbietem), sasiedztwo
  odcinkow przekroju przez sortowanie zamiast slownika, wypelnianie niecek i zalewanie na listach Pythona. Wynik na 17
  projektach = T9 co do przekroju (pkt 3.1).

### Etap 2 - P4: generator (`stanowisko/synth.py`)

- (a) `wytnij_ubytek` w wersji 2: material w kuli usuniety, powierzchnia pracy przycieta dokladnie na sferze, w jej
  miejsce czesc sfery lezaca W materiale (przycieta na pierwotnej powierzchni i na wczesniej wycietych kulach tej
  pracy), gestosc punktow nowej powierzchni = `[synth] odstep_ubytku_mm` (0,05); w prawdzie klasa polozenia
  (`krawedz_srodek` / `krawedz_zewn` / `krawedz_wewn` / `sciana`), zmierzona glebokosc, filar, odleglosc od linii. Pas
  losowania = pas od linii brzegu (jak inspect po P2). Stara wersja zostaje BEZ ZMIAN pod `--wersja-ubytkow 1`
  (`Opcje.wersja_ubytkow = 1`) wylacznie do odtwarzania starych zestawow bajt w bajt.
- (b) K6: `wytnij_ukruszenie(linie, polozenie, rozmiar)`: rozmiar = promien kuli o srodku DOKLADNIE na powierzchni
  projektu (blad fali 1 - srodek pod powierzchnia - wykluczony konstrukcja i sprawdzony pomiarem), miejsca tylko na
  zweryfikowanych przekrojach linii (takze filary mostow i obwod powierzchni przylegania korony implantowej), >= 2 mm
  od innych ubytkow; CLI `--krawedz`, `--krawedz-rozmiar` / `--krawedz-rozmiary`, `--krawedz-polozenie`,
  `--pamiec-linii`, `--odstep-ubytku`, `--wersja-ubytkow`; klucze `[synth] odstep_ubytku_mm`,
  `krawedz_rozmiar_min_mm` = 0,08, `krawedz_rozmiar_max_mm` = 0,40.
- (c) Metryki osobno krawedz / sciana: `porownaj.metryki_inspekcji` (`klasy`, lista `ubytki` z wynikiem kazdego
  ubytku), `narzedzia/metryki_P3a.py` (klasy, powody "nie sprawdzono", czas bez linii), `narzedzia/metryki_krawedz.py
  analiza` (po rozmiarach, polozeniach i grupach prac). Stara prawda (bez nowych pol) wczytuje sie; jej klasa
  polozenia jest liczona z linii brzegu projektu.
- `ubytek_widoczny` dla wersji 2 sprawdza wierzcholki na sferze kuli (stara regula "0,5 r od srodka" nie pasuje do
  czaszy wersji 2; dla wersji 1 bez zmian - patrz granice).

### Etap 3 - P2: pas brzegu od linii + "nie sprawdzono" (`stanowisko/inspect.py`, `porownaj.py`, `ui_test.py`)

- (a) Pas `pas_brzegu_mm` = odleglosc od linii brzegu (stacje O i I) kazdego filaru: metoda A (plama w pasie) i
  probka metody B (powierzchnia projektu <= pas od linii, takze ponizej z = -1,5). `[inspect] pas_brzegu_od` =
  `linia` (domyslnie) albo `plaszczyzna` (sposob sprzed P2, tylko do porownan - tym samym kodem liczono "przed").
- (b) Status `nie_sprawdzono`: stacja linii O sprawdzona = zweryfikowany przekroj linii projektu ORAZ dane skanu przy
  linii (>= 50 % punktow pasa w 0,3 mm ma powierzchnie skanu wg reguly metody B); filar sprawdzony = udzial >=
  `brzeg_min_sprawdzony` (0,9) i najdluzszy odcinek bez sprawdzenia <= `brzeg_max_przerwa_mm` (1,5). Inaczej status
  `nie_sprawdzono`, gniazdo zolte z podpisem "nie sprawdzono" (`porownaj.INSPECT_NA_STATUS`, `OPISY_INSPEKCJI`, okno);
  wynik JSON `brzeg`: ktore filary, udzialy, powody (`linia` / `dane`), do 12 odcinkow z polozeniem. Brak danych nigdy
  nie daje czerwonego i nie gasi wykrytego ubytku (ubytek ma pierwszenstwo, brak danych idzie do `uwagi`).
- Nowe klucze `[inspect]`: `pas_brzegu_od`, `brzeg_min_sprawdzony`, `brzeg_max_przerwa_mm` (wartosci startowe,
  niestrojone: 0,9 = prog "wiarygodnej" petli z T9, 1,5 = szerokosc pasa).
- Miejsce zastosowania transformacji projekt <-> skan w `inspect.sprawdz` nie zmienione (zmienia je rownolegle inny agent).

## 2. Testy (PC, `run.cmd -m pytest testy -q -p no:cacheprovider`)

| Stan | passed | skipped | failed | log (`<PC-katalog>\app\b\logi\`) |
|---|---|---|---|---|
| punkt odniesienia `8b83da7` | 252 | 3 | 0 | `pytest_00_baza.log` |
| po etapie 2 (synth) | 285 | 3 | 1 | `pytest_02_etap2.log` |
| po etapie 3 (`8d1bced`) | 294 | 3 | 1 | `pytest_03_etap3.log` |

- Po `8d1bced` zmienily sie tylko: nazwa jednego klucza pomocniczego w `krawedz` (`kanal_na_wylot` -> `otwor_na_wylot`,
  zaden test go nie uzywa; kod sprawdzony przebiegiem `linie`) i narzedzie `metryki_krawedz.py` (nie importuje go zaden
  test). Pelnego pytest na `e983ae6` nie powtorzono (PC).

- Nowe testy: `test_krawedz.py` 14, `test_synth.py` +8 funkcji (11 pozycji), `test_edge_synth.py` +4 funkcje
  (9 pozycji), `test_inspect.py` +9 = 43 pozycje (255 -> 298 zebranych). Pominiete 3 = te same co w punkcie odniesienia.
- **1 failed: `test_match.py::test_zgrubne_obroty_i_ocena[okragla_wieczorna_r54]` - plik POZA moja lista.** Fixture
  `fragmenty` generuje skan seed 22 z domyslnym generatorem; wersja 2 zmienia geometrie ubytkow i (przez szum losowany
  na wierzcholek) caly dalszy strumien losowy, a ostatnia asercja testu sprawdza sama sciezke RANSAC (seed 0), opisana w
  docstringu testu jako krucha (R59: "0,90 / 0,53 / 0,90 zaleznie od seeda"). Deterministyczne: 3 / 3 przebiegi failed,
  kod sprzed P4 10 / 10 passed. Sprawdzone na kopii roboczej testu (plik repo bez zmian): z `wersja_ubytkow=1` w
  `synth.Opcje.z_toml(...)` fixture skan jest bajtowo ten sam co przed P4 i test_match przechodzi 10 / 10.
  **Do zrobienia przez koordynatora:** w `testy/test_match.py`, fixture `fragmenty`, dopisac `wersja_ubytkow=1` do
  `synth.Opcje.z_toml(...)` (zachowuje skan, na ktorym dobrano seed 22). Logiki `match` nie dotykalem.
- Zmienione istniejace testy (uzasadnienie):
  - `test_edge_synth.py::test_transformacje_z_prawdy_sa_sztywne_i_nakladaja_kazda_prace`: (1) przenikanie liczone
    `przenikanie_ryn` dla pracy w rynience (nowe losowanie kladzie jedna prace w rynience - wczesniej test zakladal
    gniazda okragle, sprawdzenie nie oslabione, tylko dobrane do typu gniazda); (2) pas ubytku sprawdzany jako odleglosc
    od linii brzegu (`odleglosc_od_linii <= pas`, z prawdy) zamiast "z w 1,5 mm od najwyzszego punktu pracy w gniezdzie"
    (P2/P4 zmienia definicje pasa; przechyl pracy w gniezdzie do 4 st. obniza brzeg, wiec dla z dopuszczono 1,0 mm).
  - `test_synth.py::test_ubytek_jest_pod_powierzchnia` - bez zmian (przechodzi na wersji 2).
  - Pozostale testy sprzed P2 / P4 bez zmian oczekiwan.

## 3. Pomiary

### 3.1 Linie krawedzi brzegu, 17 projektow (`metryki_krawedz.py linie`, projekt x 1,22; `dane\krawedz\linie.json`)

| projekt | typ, zeby | filar | war. | zweryf. / 720 | ciag [st.] | werdykt | dl. O (zweryf.) [mm] | z O [mm] | caly pod starym pasem |
|---|---|---|---|---|---|---|---|---|---|
| 066fcc6858e01759 | bez lacznika 16 | 1 | 3 | 717 (1,00) | 0,5 | wiarygodna | 19,1 (19,1) | 0 | nie |
| 1f4b07ddb918d111 | waxup 37-36-35 | 1 | 2 | 566 (0,79) | 33,5 | czesciowa | 42,3 (32,9) | -9,88 ... -4,24 | TAK |
| | | 2 | 2 | 511 (0,71) | 53,5 | czesciowa | 32,4 (23,0) | -9,62 ... -4,72 | TAK |
| 25c7c2dfa3a17c58 | waxup 35-34-33 | 1 | 3 | 719 (1,00) | 0,5 | wiarygodna | 18,6 (18,6) | -0,29 ... 0 | nie |
| | | 2 | 3 | 718 (1,00) | 0,5 | wiarygodna | 18,6 (18,6) | -4,31 ... -4,02 | TAK |
| 2754d1d81ad47906 | waxup 21-22-23 | 1 | 1 | 462 (0,64) | 61,5 | czesciowa | 37,0 (20,6) | -7,63 ... -1,80 | TAK |
| | | 2 | 2 | 432 (0,60) | 66,0 | czesciowa | 38,3 (19,4) | -6,80 ... -1,74 | TAK |
| 2e15189ef6d12701 | bez lacznika 46 | 1 | 3 | 720 (1,00) | 0 | wiarygodna | 18,3 (18,3) | 0 | nie |
| 37aa171c0355693b | waxup 12-11-21 | 1 | 2 | 491 (0,68) | 51,5 | czesciowa | 31,6 (16,4) | -3,38 ... -0,48 | nie |
| | | 2 | 3 | 696 (0,97) | 2,5 | wiarygodna | 22,6 (22,0) | -3,11 ... -2,02 | TAK |
| 3d091aaa646d9c32 | korona 22 | 1 | 1 | 714 (0,99) | 3,0 | wiarygodna | 23,2 (23,0) | -2,36 ... -0,03 | nie |
| 5a3a03ddfb5d8577 | bez lacznika 46 | 1 | 3 | 720 (1,00) | 0 | wiarygodna | 16,9 (16,9) | 0 | nie |
| 6570c1796f152c01 | bez lacznika 14 | 1 | 3 | 720 (1,00) | 0 | wiarygodna | 14,8 (14,8) | 0 | nie |
| 91c1dea0b2060be3 | korona 14 | 1 | 3 | 662 (0,92) | 5,0 | wiarygodna | 34,1 (31,7) | -4,30 ... -0,03 | nie |
| 96087639f65a8cbb | waxup 13 | 1 | 3 | 545 (0,76) | 12,5 | czesciowa | 37,5 (28,5) | -4,90 ... -0,02 | nie |
| a4d10c94db53a1a1 | bez lacznika 36 | 1 | 3 | 568 (0,79) | 67,5 | czesciowa | 25,0 (13,4) | -0,36 ... 0 | nie |
| a823e3b4aff6b60e | korona 17 | 1 | 3 | 710 (0,99) | 1,0 | wiarygodna | 41,7 (41,1) | -2,61 ... -0,03 | nie |
| bc137fec92efdba6 | waxup 16-15 | 1 | 3 | 712 (0,99) | 0,5 | wiarygodna | 13,4 (13,2) | -0,63 ... -0,57 | nie |
| | | 2 | 3 | 716 (0,99) | 0,5 | wiarygodna | 13,4 (13,4) | -0,06 ... 0 | nie |
| cf168832a2757d95 | most 23-24-25-26 | 1 | 3 | 677 (0,94) | 3,0 | wiarygodna | 44,0 (41,4) | -2,66 ... -0,03 | nie |
| | | 2 | 3 | 579 (0,80) | 14,0 | czesciowa | 33,0 (25,6) | -7,72 ... -2,60 | TAK |
| d8d245b4c01ae11b | korona 18 | 1 | 1 | 649 (0,90) | 14,5 | czesciowa | 41,5 (38,6) | -6,26 ... -0,02 | nie |
| ea47d2adbe45456e | korona 46 | 1 | 3 | 686 (0,95) | 4,0 | wiarygodna | 42,1 (40,1) | -3,05 ... -0,02 | nie |

- Zgodnosc z T9 (`T9\RAPORT.md` pkt 2.4): liczba petli 23 = 23; liczba zweryfikowanych przekrojow i wariant - 23 z 23
  petli identyczne; dlugosc O identyczna w petlach wiarygodnych (najwyzej 0,1 mm: `cf168832` F1 44,0 vs 43,9),
  w petlach czesciowych 0,1-0,7 mm dluzsza (niezweryfikowane "wycieczki" linii przy lacznikach - prawdopodobnie skutek
  ograniczenia podsiatki w z, ktore przyspiesza liczenie; dlugosc zweryfikowana rozna tylko w `37aa171c` F1: 16,4 vs 16,5).
- Miejsca niepewne (odcinki niezweryfikowane) jak w T9: przy lacznikach filarow prac wieloczlonowych, `a4d10c94`
  (korona bez lacznika, najdluzszy ciag 67,5 st.), `96087639` (waxup), `d8d245b4` (szeroka polka brzegu - kryterium
  szerokosci, linia prawdopodobnie poprawna).
- Czas: 3,1-9,2 s na projekt (mediana 6,4 s; 17 procesow na obciazonym PC), liczone raz na projekt w procesie (pamiec
  modulu; opcjonalnie na dysku). T9 podawal ok. 30 s.
- Zasieg starego pasa: 7 z 12 filarow prac wieloczlonowych (i 7 z 23 petli) lezy w calosci ponizej z = -1,5. T9 w tekscie
  pisze "6 z 12", ale jego wlasna tabela (z O) daje 7 - `2754d1d8` F1 i F2 maja z O do -1,80 / -1,74.

### 3.2 Generator: geometria ubytkow przed / po (P4 a; `metryki_krawedz.py ubytki --ile 40 --seed 0`, `dane\krawedz\ubytki.json`)

680 ubytkow (17 projektow x 40), srednica losowa 0,2-1,5 mm, miejsce = losowy wierzcholek w pasie 1,5 mm od linii
brzegu; dla KAZDEGO miejsca wycieto ubytek wersja 1 (sprzed P4) i wersja 2 o tym samym srodku i promieniu. Pomiar
niezalezny od kodu generatora (trimesh): nowa powierzchnia = trojkaty, ktorych wszystkie wierzcholki leza na sferze
kuli; "w powietrzu" = punkt dalej niz 0,01 mm NA ZEWNATRZ pierwotnej bryly. Klasa: krawedz = kula siega linii O / S / I.

| miara | wersja 1 (przed) | wersja 2 (po) |
|---|---|---|
| czasza w powietrzu > 10 % pola - wszystkie / krawedz / sciana | **293 / 680**, 263 / 341, 30 / 339 | **25 / 680**, 22 / 341, 3 / 339 |
| jakakolwiek czesc czaszy w powietrzu | 547 / 680 | 34 / 680 |
| sredni udzial pola czaszy w powietrzu - wszystkie / krawedz | 13,4 % / 23,9 % | 1,4 % / 2,2 % |
| czasza > 0,08 mm nad pierwotna powierzchnia | 343 / 680 (krawedz 276) | 34 / 680 (krawedz 29) |
| material w kuli bez powierzchni (> 10 % kierunkow) | 34 / 680 | 18 / 680 |
| wierzcholki pozostawione wewnatrz kuli | 0 | 0 |
| glebokosc rzeczywista / nominalna 0,7 r, p10 / med / p90 - wszystkie | 0,83 / 1,00 / 1,00 | 0,82 / 0,99 / 1,00 |
| to samo - krawedz / sciana | 0,78 / 0,95 / 1,00; 0,99 / 1,00 / 1,00 | 0,76 / 0,93 / 1,00; 0,97 / 1,00 / 1,00 |

- **Przypadki wersji 2 z czasza w powietrzu: 25 z 25 na dwoch siatkach** (`5a3a03ddfb5d8577` 14 / 40,
  `a4d10c94db53a1a1` 11 / 40; obie korony bez lacznika z kanalem sruby). Kontrola (`skrypty\znak_siatek.py`, 4000
  punktow przy powierzchni kazdego projektu): Open3D (generator) i trimesh (pomiar) licza "wewnatrz" identycznie
  (0 % roznic na 17 projektach), ale na tych dwoch siatkach znak jest sprzeczny z normalnymi trojkatow w 16,1 % i
  16,3 % punktow (na pozostalych 15: 0-1,1 %), `is_volume` = False. Material jest tam niejednoznaczny (prawdopodobnie
  samoprzeciecie albo zdublowana powierzchnia kanalu) - wynik generatora i pomiaru na tych siatkach jest niepewny;
  cechy "nad" = "glebokosc" w tych przypadkach wskazuja na odwrocony znak, nie na blad wycinania.
- Pozostale 3 przypadki (`3d091aaa` 1, `bc137fec` 2) to tylko "material bez powierzchni" 11-17 % przy kulach
  o srednicy 0,22-0,25 mm (kilkanascie punktow czaszy przy odstepie 0,05 mm - granica rozdzielczosci pomiaru), 0 %
  w powietrzu.
- Na siatkach szczelnych zgodnosc glebokosci z generatora (`glebokosc_rzeczywista`) z pomiarem trimesh: najwiecej
  0,011 mm roznicy.
- Porownanie z T5 (`T5\RAPORT.md` pkt 6.1, zestawy P2 + P3a, wersja 1): "krawedz <= 0,15 mm: 76 / 83 z czasza > 10 %
  w powietrzu, srednio 36 %". Tu definicja krawedzi jest szersza (kula siega linii), stad 263 / 341 i 24 %.
- Liczby wersji 1 bez dwoch niejednoznacznych siatek nie zostaly policzone (plik `ubytki.json` zostal na PC).
- Glebokosc rzeczywista (wersja 2) w prawdzie: na scianie = nominalna (mediana 1,00), na krawedzi mniejsza (mediana
  0,93 nominalnej, p10 0,76) - powierzchnia na krawedzi opada, a "glebokosc 0,7 r" jest liczona od plaszczyzny stycznej.

### 3.3 K6 - ukruszenia celowe (P4 b)

- Sprawdzone testami (`test_synth.py::test_ukruszenie_celowe_na_krawedzi_brzegu`, 4 polozenia x 3 rozmiary 0,08 /
  0,15 / 0,30 na atrapie): srodek kuli na powierzchni (< 1e-4 mm) i na linii O / S / I (< 1e-3 mm), nic w powietrzu,
  w kuli nie zostaje zaden wierzcholek, glebokosc rzeczywista <= rozmiar i zgodna z niezaleznym pomiarem, na srodku
  plaskiej krawedzi > 0,85 x rozmiar (do 0,15), na narozniku 0,4-0,98 x rozmiar, na scianie > 0,8 x rozmiar; ubytki
  pracy >= 2 mm + promienie od siebie; bez linii - jawnie "nie postawiono". CLI: `test_edge_synth.py::test_cli_ukruszenia_krawedzi`.
- **Nie zmierzone (PC):** glebokosc rzeczywista po rozmiarach i polozeniach na 17 projektach (`metryki_krawedz.py k6`),
  osobno korony / korony bez lacznika / filary prac wieloczlonowych, oraz zestaw K6 (40 plytek, 2-3 ukruszenia na prace,
  rozmiary 0,08 / 0,10 / 0,15 / 0,20 / 0,30 / 0,40, polozenia srodek / zewn / wewn / sciana) z metrykami krawedz /
  sciana przed / po. Polecenia gotowe (pkt 8).

### 3.4 Zgodnosc wstecz - seed 7001 (P4 d; skany jak `R59_odbior/baseline.md` pkt 5, uklady `*_r54`)

| plytka | kod sprzed P4 (`8b83da7`) | nowy kod `--wersja-ubytkow 1` | nowy kod, domyslnie (wersja 2) |
|---|---|---|---|
| wieczorna_r54 n3 | 9 prac, 12 ubytkow, STL `efbf3dad...` | STL bajtowo rowny, prawda rowna w starych polach | 10 prac (pominietych 7), 5 ubytkow, inny STL |
| poranna_r54 n6 | 9 prac, 9 ubytkow | rowny / rowna | 8 prac, 5 ubytkow |
| okragla_wieczorna_r54 n8 | 9 prac, 9 ubytkow | rowny / rowna | 8 prac, 3 ubytki |
| okragla_poranna_r54 n9 | 8 prac, 10 ubytkow | rowny / rowna | 9 prac, 12 ubytkow |

- Co sie zmienia przy tym samym seedzie (wersja 2): numer plytki, kolejnosc projektow, wspolczynnik i pierwsza
  praca sa te same; pierwszy ubytek ma inna geometrie (inna liczba wierzcholkow) i inne miejsce (pas od linii, nie od
  najwyzszego punktu); szum `dodaj_szum` losuje jedna liczbe na wierzcholek, wiec od tej chwili caly strumien losowy jest
  przesuniety: inne liczby ubytkow, inne gniazda, inne prace na plytce. Mapa `t8_mapa_seed7001.json` (gniazdo -> projekt)
  nie jest wiec odtwarzalna domyslnym generatorem; jest odtwarzalna z `--wersja-ubytkow 1` (skan bajtowo ten sam).
- Prawda z `--wersja-ubytkow 1` ma nowe pola z wartosciami "nieznane" (`polozenie` "", `glebokosc_rzeczywista` null,
  `filar` 0, `odleglosc_od_linii` null, `celowy` false, `ukruszenia_pominiete` 0); stare pola rowne (4 / 4).
- **Niezweryfikowane:** statusy gniazd mapy t8 po P2. Skan z `--wersja-ubytkow 1` jest ten sam, ale inspect z
  `pas_brzegu_od = "linia"` moze zmienic `status_gniazda` (np. zielone -> zolte "nie sprawdzono" dla projektow z linia
  czesciowa; w mapie t8 sa m.in. `96087639`, `2754d1d8` i granicznie `d8d245b4`). Dla testu odbiorczego R59:
  generowac `--wersja-ubytkow 1`, a porownaj liczyc z `--ustawienia` z `pas_brzegu_od = "plaszczyzna"`, zeby dostac
  mape t8 bez zmian, albo przyjac nowa mape po P2. Porownaj na tych skanach nie zostal uruchomiony (PC).

### 3.5 P2 - inspect przed / po na zestawach odniesienia (`metryki_krawedz.py przed_po` i `metryki_P3a.py`)

"Przed" = nowy kod z `pas_brzegu_od = "plaszczyzna"` (sciezka sprzed P2 - pkt 6 skrotu: odtwarza R59 co do jednej
liczby). "Po" = `pas_brzegu_od = "linia"`, `brzeg_min_sprawdzony` 0,9, `brzeg_max_przerwa_mm` 1,5. W `przed_po` plate
i match sa liczone raz, inspect dwa razy na tych samych fragmentach i transformacjach - roznice wynikaja tylko z P2.

| miara | R59 przed | R59 po | r54 przed | r54 po |
|---|---|---|---|---|
| skanow / ubytkow wykrywalnych | 40 / 248 | - (PC) | 40 / 231 | 40 / 231 |
| wykryte dowolna metoda | 221 | - | 215 | **186** |
| - krawedz (kula siega linii) | 106 / 121 | - | 94 / 102 | 93 / 102 |
| - sciana | 115 / 127 | - | 121 / 129 | **93 / 129** |
| wykryte A / B / A+B / czerwone | 184 / 107 / 69 / 79 | - | 184 / 109 / 78 / 88 | 161 / 92 / 67 / 76 |
| czerwone krawedz / sciana | 43 / 36 | - | 52 / 36 | 50 / 26 |
| prace cale | 127 | - | 136 | 136 |
| prace cale z czerwonym | **0** | - | **0** | **0** |
| prace cale z zoltym "sprawdz" / "ubytek" (falszywy alarm) | 0 | - | 1 | 0 |
| prace cale "nie sprawdzono" (zolte) | 0 | - | 0 | **39 (29 %)** |
| falszywe miejsca (wszystkie prace) / w tym czerwone | 7 / 2 | - | 3 / 0 | 0 / 0 |
| top-1 | 382 / 397 | - | nie odczytano | ten sam match co "przed" |

- **Prace cale, ktore zmieniaja kolor z zielonego na zolty "nie sprawdzono" (r54): 38 albo 39 ze 136.** "Nie
  sprawdzono" powstaje tylko tam, gdzie wynik bylby "ok"; przed byly to prace zielone, z wyjatkiem byc moze jednej
  (jedyny falszywy "sprawdz" przed zniknal po). Dokladnych przejsc i powodow nie odczytano (`analiza` nie zdazyla - PC).
  **Najbardziej prawdopodobna przyczyna (niezweryfikowane):** projekty z petla "czesciowa" (7 z 17: `1f4b07dd`,
  `2754d1d8`, `37aa171c`, `cf168832`, `96087639`, `a4d10c94`, granicznie `d8d245b4` z 0,90) nie spelnia kryterium linii
  0,9 / 1,5 mm na KAZDEJ pracy - kazda ich praca cala jest "nie sprawdzono" z powodem `linia`; powod `dane` (dziury
  skanu przy linii) dotyczy glownie prac czesciowych / bokiem.
- Falszywe alarmy na pracach calych przy wiekszym obszarze kontroli: r54 czerwone 0 -> 0, zolte "sprawdz" 1 -> 0,
  falszywe miejsca 3 -> 0. Obszar kontroli nie tylko rosnie (glebokie brzegi), ale i maleje (przesla, laczniki, sciany
  daleko od linii) - na tych zestawach netto mniej falszywych zgloszen.
- **Wykrycia: 29 straconych na r54, w tym 28 na scianach.** Ubytki zestawow odniesienia sa z generatora wersji 1, ktory
  losowal je w pasie 1,5 mm od najwyzszego punktu pracy; czesc z nich lezy dalej niz 1,5 mm od linii brzegu (przesla,
  laczniki mostow, sciany koron tam, gdzie linia schodzi nisko) i po P2 nie jest juz kontrolowana. Na probie z 1 skanu
  (R59 `okragla_wieczorna_n8_s0100`) stracony byl 1 ubytek sciany z 12 (przed 12 / 12, po 11 / 12); rozbicie 29 wg
  odleglosci od linii i grupy pracy: niezweryfikowane (polecenie `analiza` w pkt 8). To decyzja wlasciciela, czy
  ukruszenia przesel / lacznikow maja byc kontrolowane (dzis pas od linii ich nie obejmuje, zostaje tylko regula
  "0,5 mm od ostrej krawedzi projektu") - patrz pkt 6.
- Pokrycie filarow mostow pasem: przed 7 z 12 filarow prac wieloczlonowych w calosci poza pasem; po 0 z 12 poza pasem.
  Sprawdzalnosc (kryterium 0,9 / 1,5 mm na linii projektu): 6 z 12 filarow ma linie wiarygodna (`25c7c2df` F1 F2,
  `37aa171c` F2, `bc137fec` F1 F2, `cf168832` F1), 6 z 12 "czesciowa" -> "nie sprawdzono" (`1f4b07dd` F1 F2, `2754d1d8`
  F1 F2, `37aa171c` F1, `cf168832` F2). Udzial sprawdzonych na pracach calych - niezweryfikowane (PC).
- Czas inspect na plytke przed / po: **nie zmierzony porownywalnie** (PC). Znane: R59 "przed" w przebiegu 4-procesowym
  na obciazonym PC - mediana inspect 1,8 s na plytke (R59 14.11, 1 proces: 0,9 s); linie brzegu: 3-9 s raz na projekt
  w procesie (w `przed_po` / `metryki_P3a` pole `czas_s.linie_brzegu` i `inspect_bez_linii`).

## 4. Odstepstwa od zlecenia

1. **Pomiary niepelne** (PC przestal odpowiadac) - lista na poczatku raportu; polecenia do dokonczenia w pkt 8.
   Sprzatanie `<PC-katalog>\app\b\Ramki\stanowisko\dane` NIE wykonane (pkt 6).
2. **Plik poza lista:** `testy/test_match.py` wymaga jednej linii (`wersja_ubytkow=1` w fixture) - nie zmienialem;
   do decyzji koordynatora (pkt 2). Do tego czasu pytest ma 1 failed.
3. Zmienione 2 asercje istniejacego testu `test_edge_synth.py::test_transformacje...` - uzasadnienie w pkt 2.
4. Wersja 1 generatora zostawiona w kodzie (`_wytnij_ubytek_v1`, `--wersja-ubytkow 1`) zamiast usuniecia - jedyny sposob
   na odtworzenie zestawow odniesienia i mapy seed 7001 (P4 d).
5. Nowe klucze `[inspect] pas_brzegu_od`, `brzeg_min_sprawdzony`, `brzeg_max_przerwa_mm` - nowe parametry nowego
   statusu (nie strojenie istniejacych progow); wartosci startowe opisane, nie dobierane na danych.
6. `opisy_modulow/README.md` (tabela modulow) nie zaktualizowany - plik nie byl na mojej liscie; brakuje wiersza
   `krawedz` (tekst: "krawedz | gotowy (P2/P4 15.11) | linie krawedzi brzegu kazdego filaru projektu | siatka projektu ->
   petle O / I / S z weryfikacja | test_krawedz (14), 23 petle na 17 projektach = T9").
7. `porownaj.main` (poza dozwolonymi fragmentami) wola `metryki_inspekcji(wynik, prawda)` bez puli - dla prawdy sprzed P4
   klasa krawedz / sciana jest tam "nieznane"; narzedzia (`metryki_P3a`, `metryki_krawedz`) podaja pule.
8. Pomiar "przed / po" robilem narzedziem `metryki_krawedz.py przed_po` (plate + match raz, inspect dwa razy), a nie
   dwoma przebiegami `metryki_P3a.py` - szybciej o polowe i bez rozrzutu match miedzy przebiegami. R59 "przed" policzony
   takze `metryki_P3a.py` (ten sam wynik co raport R59).
9. Nazwa raportu: nazwa pliku w zleceniu byla nieczytelna (zamaskowana) - przyjalem `raporty/P2_P4_krawedz_brzegu_2026-11-16.md`.

## 5. Znane granice

- Wszystko na danych sztucznych. Linie krawedzi z siatki projektu; na skanie linii nie wyznacza nic (metody
  krawedziowe M / C2 / G - poza zakresem, decyzja 10.11).
- "Nie sprawdzono" zalezy od linii projektu: projekt z petla czesciowa jest "nie sprawdzono" ZAWSZE (7 z 17 projektow
  puli testowej). Bez poprawy linii przy lacznikach (propozycja T9 pkt 6) albo bez zgody na nizszy prog mosty i czesc
  koron bez lacznika nigdy nie beda zielone.
- Pas od linii nie obejmuje przesel, lacznikow i scian dalej niz 1,5 mm od linii - dawniej (pas od plaszczyzny) czesc
  z nich byla kontrolowana metoda A. Ubytki tam (np. ukruszenie przesla) wykrywa dzis tylko regula ostrej krawedzi.
- Dane skanu przy linii = regula metody B (wierzcholek o zgodnej normalnej w 0,8 mm). Na skanach sztucznych dziur
  przy krawedzi prawie nie ma; prawdziwy skaner ma ich najwiecej wlasnie na ostrych krawedziach - udzial "nie
  sprawdzono" z powodu `dane` trzeba zmierzyc w P3b.
- Dwie siatki projektow (`5a3a03dd`, `a4d10c94`, korony bez lacznika) maja niejednoznaczny znak "wewnatrz" (16 %
  punktow przy powierzchni sprzecznych z normalnymi): generator ubytkow i inspect (znak odchylki z normalnej, metoda A)
  moga sie tam mylic. Warto sprawdzic te pliki w exocad / MeshLab (samoprzeciecia, zdublowane powierzchnie kanalu).
- Szwy miedzy przycieta powierzchnia pracy a czasza ubytku nie sa zszyte (skan sztuczny nie musi byc szczelny);
  `ubytek_widoczny` dla wersji 1 zostawiony bez zmian (regula "3 wierzcholki w 0,5 r od srodka" odrzuca prawie kazdy
  ubytek wersji 1 o r > 0,09 mm przy `--pokrycie`/`--bokiem` - blad sprzed P4, opisany w `synth.md`).
- Klasa "krawedz" w metrykach = kula ubytku siega linii O / S / I (szersza niz "<= 0,15 mm od krawedzi" w T5); duze
  kule ze sciany tez sie lapia. Ukruszenia K6 maja klase dokladna (miejsce postawienia).
- Wersja 2 generatora jest wolniejsza (pomiar glebokosci 4000 kierunkow, zageszczenie do 0,05 mm); synth na plytke
  ok. 10-14 s zamiast 7-10 s (seed 7001).
- Linie przy skali innej niz 1,22 sa przeliczeniem linii liczonych na x 1,22 (stale metody w mm pracy zielonej); dla
  prac porannych (x 1,0) nie sprawdzano osobno.

## 6. Zadania dla czlowieka

1. [usunieto w kopii: opis dostepu ssh]
   - **usunac pliki z nazwami pacjentow**, ktore utworzyl generator w moim katalogu roboczym:
     `<PC-katalog>\app\b\Ramki\stanowisko\dane\s7001\mapa_projektow.json` oraz (jesli powstal)
     `<PC-katalog>\app\b\Ramki\stanowisko\dane\mapa_projektow.json`;
   - usunac duze pliki: `dane\s7001\*\skan_*.stl` (12 skanow, ok. 0,6 GB), `dane\syntetyczne_K6\*.stl` (jesli powstaly);
     zostawic JSON, logi (`<PC-katalog>\app\b\logi`), `dane\krawedz`, `dane\wyniki_krawedz`, `dane\linie_cache`;
   - (albo zlecic to koordynatorowi / kolejnej sesji razem z dokonczeniem pomiarow z pkt 8).
2. Decyzja: czy w `testy/test_match.py` dopisac `wersja_ubytkow=1` w fixture (pkt 2) - koordynator.
3. Decyzja wlasciciela: progi "nie sprawdzono" (`brzeg_min_sprawdzony` 0,9, `brzeg_max_przerwa_mm` 1,5) przy wyniku
   ok. 29 % prac calych zoltych na zestawie r54 (glownie mosty / waxupy z linia czesciowa przy lacznikach) - zostawic,
   czy najpierw poprawic linie przy lacznikach (T9 pkt 6, osobna paczka).
4. Decyzja wlasciciela: czy ukruszenia przesel i lacznikow mostow maja byc kontrolowane osobno (po P2 pas od linii ich
   nie obejmuje; na r54 to 28 z 29 straconych wykryc).
5. Po aktualizacji programu: dopisac 6 nowych kluczy do lokalnych `ustawienia.toml` (pulpit PC, laptop stanowiska) -
   wzor w `ustawienia.przyklad.toml` (tekst w pkt 7).
6. Sprawdzic w exocad / MeshLab dwa projekty bez lacznika (`5a3a03ddfb5d8577`, `a4d10c94db53a1a1`): niejednoznaczny
   znak "wewnatrz bryly" w 16 % punktow (pkt 3.2).

## 7. Do README

Tekst do wstawienia w `Ramki/stanowisko/README.md` (sekcja o inspect, po akapicie "Pelny lancuch plate -> match -> inspect"):

> **Krawedz brzegu (P2 / P4, 16.11.2026).** Pas brzegu (`[inspect] pas_brzegu_mm`) liczy sie od linii krawedzi brzegu
> KAZDEGO filaru projektu (modul `stanowisko/krawedz.py`: korona - 1 petla, most - petla na filar, korona implantowa bez
> lacznika - obwod powierzchni przylegania), a nie od najwyzszego punktu pracy. Gdy brzegu ktoregos filaru nie da sie
> sprawdzic (linia projektu niepewna, np. przy lacznikach mostu, albo brak danych skanu przy linii), gniazdo jest
> ZOLTE z opisem "nie sprawdzono" (status inspect `nie_sprawdzono`), nigdy zielone i nigdy czerwone; w JSON pole
> `inspekcja.brzeg` mowi, ktory filar, jaka czesc linii i dlaczego. Progi: `brzeg_min_sprawdzony`,
> `brzeg_max_przerwa_mm`; `pas_brzegu_od = "plaszczyzna"` przywraca sposob sprzed P2 (tylko do porownan).
> Generator: ubytek wycina material poprawnie (czasza kuli lezy w materiale); ukruszenia celowe na samej krawedzi:
> `--krawedz 1-2 --krawedz-rozmiary 0.08,0.10,0.15 --krawedz-polozenie srodek,zewn,wewn` (rozmiar = promien kuli o srodku
> na powierzchni); `--wersja-ubytkow 1` odtwarza bajt w bajt zestawy sprzed 15.11.2026. Pomiary:
> `narzedzia/metryki_krawedz.py` (`linie`, `ubytki`, `k6`, `przed_po`, `analiza`, `mapa`), raport
> `raporty/P2_P4_krawedz_brzegu_2026-11-16.md`.

oraz w sekcji "Ustawienia" / "Laptop firmowy" (zadanie po aktualizacji programu):

> Po aktualizacji programu dopisz do lokalnego `ustawienia.toml` 6 kluczy ze wzoru `ustawienia.przyklad.toml`:
> `[inspect] pas_brzegu_od`, `brzeg_min_sprawdzony`, `brzeg_max_przerwa_mm` i `[synth] odstep_ubytku_mm`,
> `krawedz_rozmiar_min_mm`, `krawedz_rozmiar_max_mm` - bez nich program konczy sie bledem "brak klucza" z nazwa klucza.

## 8. Gdzie leza dane i jak powtorzyc

PC, `<PC-katalog>\app\b\` (program w `Ramki\stanowisko` = galaz `czesc-b`; kod sprzed P4 w `baza\` do porownan;
`run.cmd` / `run_baza.cmd`; lokalny `ustawienia.toml` = wzor PC + 6 nowych kluczy; `ustawienia_przed.toml` = to samo z
`pas_brzegu_od = "plaszczyzna"`; skrypty jednorazowe w `skrypty\`; logi w `logi\`):

- `dane\krawedz\linie.json` (3.1), `dane\krawedz\ubytki.json` (3.2), `dane\linie_cache\*.npz` (linie 17 projektow),
  `dane\wyniki_krawedz\R59_przed.json` (metryki_P3a), `r54_przed.json` + `r54_po.json` (przed_po),
  `dane\wyniki_krawedz\proba\` (1 skan), `dane\s7001\{baza,v1,v2}\` (skany i prawda seed 7001).
- Prawdopodobnie na PC (proces osierocony po przerwaniu lancucha, nie odczytany): `dane\wyniki_krawedz\R59_po.json`
  (metryki_P3a, pas od linii) - mozna go uzyc zamiast "R59 po" z `przed_po` (inne przebiegi match, rozrzut ok. 1 gniazda).

Polecenia (z `Ramki\stanowisko`, przez `run.cmd`; `P` = `<PC-katalog>\app\Prace_test`, `D` = `<PC-katalog>\app\dane_ref`,
`UP` = plik ustawien z `pas_brzegu_od = "plaszczyzna"`):
```
run.cmd -m pytest testy -q -p no:cacheprovider
run.cmd narzedzia\metryki_krawedz.py linie --projekty P --wyjscie dane\krawedz --pamiec dane\linie_cache --procesy 17
run.cmd narzedzia\metryki_krawedz.py ubytki --projekty P --ile 40 --seed 0 --procesy 4 --wyjscie dane\krawedz
run.cmd narzedzia\metryki_P3a.py --skany D\syntetyczne_R59_P2 D\syntetyczne_R59_P3a --projekty P --ustawienia UP --wyjscie dane\wyniki_krawedz --nazwa R59_przed.json --procesy 4 --pamiec-linii dane\linie_cache
run.cmd narzedzia\metryki_krawedz.py przed_po --skany D\syntetyczne_r54_P2 D\syntetyczne_r54_P3a --projekty P --sufiks-ukladu _r54 --ustawienia-przed UP --pamiec-linii dane\linie_cache --procesy 4 --wyjscie dane\wyniki_krawedz --nazwa r54
-m stanowisko.synth --projekty P --plytka <wieczorna|poranna|okragla_wieczorna|okragla_poranna>_r54 --ile 1 --seed 7001 --wspolczynnik <1.22|1.0> --drgniecie 0.1 --poza-uklad --pole 100 [--wersja-ubytkow 1] --wyjscie dane\s7001\<v1|v2>
```
Do dokonczenia (nie uruchomione albo nie odczytane):
```
run.cmd narzedzia\metryki_krawedz.py przed_po --skany D\syntetyczne_R59_P2 D\syntetyczne_R59_P3a --projekty P --ustawienia-przed UP --pamiec-linii dane\linie_cache --procesy 4 --wyjscie dane\wyniki_krawedz --nazwa R59
run.cmd narzedzia\metryki_krawedz.py analiza --przed dane\wyniki_krawedz\r54_przed.json --po dane\wyniki_krawedz\r54_po.json --linie dane\krawedz\linie.json --wyjscie dane\wyniki_krawedz --nazwa analiza_r54.json
run.cmd narzedzia\metryki_krawedz.py analiza --przed dane\wyniki_krawedz\R59_przed.json --po dane\wyniki_krawedz\R59_po.json --linie dane\krawedz\linie.json --wyjscie dane\wyniki_krawedz --nazwa analiza_R59.json
run.cmd narzedzia\metryki_krawedz.py k6 --projekty P --linie dane\krawedz\linie.json --powtorzen 4 --procesy 6 --wyjscie dane\krawedz
rem zestaw K6: 40 plytek (po 10: wieczorna seed 6000-6009, poranna 6100-6109, okragla_wieczorna 6050-6059, okragla_poranna 6150-6159; wspolczynnik 1.22 / 1.0)
run.cmd -m stanowisko.synth --projekty P --plytka <typ> --ile 1 --seed <s> --wspolczynnik <w> --drgniecie 0 --poza-uklad --pole 100 --ubytki 0-0 --krawedz 2-3 --krawedz-rozmiary 0.08,0.10,0.15,0.20,0.30,0.40 --krawedz-polozenie srodek,zewn,wewn,sciana --pamiec-linii dane\linie_cache --wyjscie dane\syntetyczne_K6
run.cmd narzedzia\metryki_krawedz.py przed_po --skany dane\syntetyczne_K6 --projekty P --ustawienia-przed UP --pamiec-linii dane\linie_cache --procesy 4 --wyjscie dane\wyniki_krawedz --nazwa K6
run.cmd narzedzia\metryki_krawedz.py analiza --przed dane\wyniki_krawedz\K6_przed.json --po dane\wyniki_krawedz\K6_po.json --linie dane\krawedz\linie.json --wyjscie dane\wyniki_krawedz --nazwa analiza_K6.json
-m stanowisko.porownaj --skan dane\s7001\v1\<skan>.stl --projekty P --plytka <P>_r54 --wspolczynnik <w> [--numer 3|6] --prawda dane\s7001\v1\<skan>.json --wyjscie dane\s7001\v1\wynik --bez-png [--ustawienia UP]
run.cmd narzedzia\metryki_krawedz.py mapa --wyniki dane\s7001\v1\wynik --wzor <repo>\Ramki\R59_odbior\baseline\t8_mapa_seed7001.json
```
`analiza` daje: przejscia statusu prac calych przed -> po, powody "nie sprawdzono" (linia / dane) na projekt, wykrycia
krawedz / sciana na grupe pracy (korona / korona bez lacznika / wieloczlonowe), K6 po polozeniu x rozmiarze i po grupie,
zyskane / stracone wykrycia wg odleglosci od linii, filary prac wieloczlonowych (sprawdzone na pracach calych), czasy.
Generator zapisuje `mapa_projektow.json` (nazwy plikow!) w katalogu nad `--wyjscie` - po pomiarach usunac.
