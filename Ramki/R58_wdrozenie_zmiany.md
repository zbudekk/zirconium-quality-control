# R58 - komplet okragly do ramki: plytki okragle ramkowe, wkladka okragla, pokrywka okragla (lista edycji w zrodle prawdy; runda 3 po recenzji)

Data: 2026-11-19. Zlecenie wlasciciela 19.11.2026 (decyzje zamkniete): plytki OKRAGLE pod produkt koncowy, czyli lezace na ramce swietlnej - zarezerwowana zmiana R58 ("wkladka i pokrywka plytki okraglej"). Projekt luzow koordynatora: `narzedzia/studium_R58.py` (0 bledow). Wykonawca: R58-A.
Zakres edycji: `parametry.json`, `ramka_generator.py`, `plan_ramki_v2.md`, `protokol_weryfikacji_v2.md`, `wyniki_v2/` (10 nowych STL poza gitem, 2 nowe JSON, raporty, rzuty kontrolne), ten plik; od rundy 2 takze `narzedzia/studium_R58.py` (warunki pod nowa geometrie) i `narzedzia/test_R58_p3_d1.py`.
NIE dotknieto: `stanowisko/`, `Ramki_do_wgrania/`, `Ramki_pakiet/`, `00_NADZOR_STAN.md`, dokumentow dla wlasciciela (`Zakupy i druk...`, `Budowa ramki...`, `Stanowisko kontroli...`), arkuszy `R59_*`, `narzedzia/` poza dwoma plikami wyzej (m.in. `arkusz_zamowienia_R58.py` koordynatora), `wyniki_v2/arkusze/`, `wyniki_v2/render/`, `wyniki_v2/ramka_v2.blend`, `wyniki_v2/README.md`, `wyniki_v2/do_v3.md`, 21 STL i 4 JSON ukladu R59 (plikow plytek okraglych n8/n9 tez nie).

# STAN PO RUNDZIE 3 (poprawki po recenzji `recenzja/raport_recenzenta_R58_runda2.md`, B 0 / P 2 / D 6) - obowiazuje

Sekcje R3-0 ... R3-7 opisuja stan oddany po rundzie 3. Sekcje R2-* (runda 2) i 0 ... 12 (runda 1) nizej to historia - tam, gdzie R3 mowi inaczej, obowiazuje R3 (liczby, SHA wkladki i pokrywki, ryzyka 2 i 8, "co dalej").

## R3-0. Wynik

- Zmienily sie tylko `ramka_wkladka_okragla_v2.stl` i `ramka_pokrywka_okragla_v2.stl`. 8 STL plytek i 2 JSON bajtowo jak w rundzie 2 (porownanie 10 / 10 w R3-4; pliki rundy 2 odlozone w `wyniki_v2/stl_r58_runda2/` na MSI i PC przed przebudowa).
- `--etap R58_SPRAWDZ --iter 5 --r58-poprzednie stl_r58_runda1 --r58-runda2 stl_r58_runda2` na plikach oddanych: 19 ZAL, 0 N/D, 0 NIE (B 0 / P 0 / D 0); 1862 sondy, 0 niezgodnych, 0 blizej niz 0,1 od sciany.
- Budowa `--etap R58 --iter 8` (generator koncowy 1518e4c2...): 19 ZAL / 0 NIE; wkladka z tej budowy = wariant najczestszy (R3-0 nizej), pokrywka deterministyczna.
- `--etap SPRAWDZ --iter 17` (stare pliki, generator koncowy): 58 ZAL, 5 N/D, 0 NIE (jak `SPRAWDZ_iter16`; K-60: zrzut sprzed R58 bez zadnego z 20 kluczy R58 = zgodny).
- 25 plikow R59 bez zmian: 25 / 25 na PC po wszystkich przebiegach rundy 3 (`SHA256SUMS_2026-11-16_R59.txt`); na MSI worktree ma z nich tylko 4 JSON - 4 / 4.
- `narzedzia/studium_R58.py`: BLEDY 0, kod 0 (nowe warunki: wierzch zebra nad wkladka 0,70 >= 0,5; zapas w rzucie lico kolnierza - koniec czesci gornej zebra 0,40 >= 0,2).
- Plan <-> JSON: 0 roznic; walidator R14: 307 kluczy (287 + 20 R58), LICZONE 0,0000. `narzedzia/test_R58_p3_d1.py`: bez zmian wyniku (P3 i D1 jak w R2-8; D1 liczy teraz 20 kluczy R58).

Pliki oddane (STL w `Ramki/wyniki_v2/stl/` worktree, poza gitem; lista `wyniki_v2/raport/sha256_stl_po_R58.txt` - SHA nizej skopiowane z tej listy skryptem; objetosc i gabaryt z raportu `R58_SPRAWDZ_iter5`, orientacja druku):

| Plik | SHA-256 (runda 3) | Objetosc [cm3] | Gabaryt X x Y x Z [mm] | Szt. / material | Zmiana w rundzie 3 |
|---|---|---|---|---|---|
| `ramka_plytka_okragla_ramkowa_wieczorna_v2.stl` (bazowy) | 322eb892b7acf81ce5e0ff5f437436b44f22490a662f1b1bd9939353b4a4125c | 48,90 | 100,000 x 100,000 x 8,000 | - (wzorzec) | brak (= runda 2) |
| `ramka_plytka_okragla_ramkowa_wieczorna_n1_v2.stl` | 84d361e2389bef12fd07278bf3e2e65fd170c83d4012f8fbbfa12b8ad172325f | 48,91 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia | brak |
| `ramka_plytka_okragla_ramkowa_wieczorna_n2_v2.stl` | 7848aa2395638b338e4bd2e83473b1329c53c61500a7ec1ba5a63a8c5aaaaa94 | 48,91 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia | brak |
| `ramka_plytka_okragla_ramkowa_wieczorna_n3_v2.stl` | 1b8ac3d390870f0a4607b3289f50201ef28cf2049801ac853aaa1427735321aa | 48,91 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia | brak |
| `ramka_plytka_okragla_ramkowa_poranna_v2.stl` (bazowy) | 845e4bd61b40562010dec24b18ee873e90d8937f07728f81589c407f826ba266 | 49,18 | 100,000 x 100,000 x 8,000 | - (wzorzec) | brak |
| `ramka_plytka_okragla_ramkowa_poranna_n4_v2.stl` | 5d81f55b8b114ba9cf307bb4ba63e70083aa6570ab0bb646acef69b8cd6cceb5 | 49,20 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia | brak |
| `ramka_plytka_okragla_ramkowa_poranna_n5_v2.stl` | 64867b5b63a31db88715c9c9636c33015566bbe48af2c8f4a90330797f063381 | 49,20 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia | brak |
| `ramka_plytka_okragla_ramkowa_poranna_n6_v2.stl` | 7630a029157b2fc65144c5f6b32ad28c02048f0642855cc3d23c2570ea28991e | 49,20 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia | brak |
| `ramka_wkladka_okragla_v2.stl` | 287e001fddd655f9df91663d7fb7a8cf6a9b3aa89d8bc2e470bf50f59f8be6c5 | 22,45 (22,446) | 130,000 x 148,400 x 10,500 | 3 / PA12 drukarnia | P1: czesc zebra nad wierzchem do r 49,2 z faza |
| `ramka_pokrywka_okragla_v2.stl` | f1a133cf19fda391bf749797c1a7e1480a8a0062b7d49eee2d248fd5c8d70889 | 25,06 | 103,600 x 103,600 x 20,000 | 4 / PETG FDM (wlasny) | P2: szczeliny 15 z otworem o2,0 |
| `json/uklad_gniazd_okragla_ramkowa_wieczorna.json` | d66ef99b799f37c241b83b73d979ab70a5810cec7fc4aec369f3e0da6c4c17a9 | - | - | - | brak |
| `json/uklad_gniazd_okragla_ramkowa_poranna.json` | ab6e02a0a9602216d4b9251a725d4281a4e04c1db6d1261af6a7ab97e4517412 | - | - | - | brak |

Wkladka - warianty bajtowe (D4 recenzji rundy 2; boolean EXACT, jak w rundach 1 i 2): 17 budow rundy 3 (`R58_iter8` + 8 osobnych procesow Blendera po 2 budowy, skrypt `r3_warianty.py` z tymi samymi funkcjami i eksportem co `--etap R58`) dalo 3 warianty, rozniace sie tylko 1 wierzcholkiem na wierzchu wkladki (Z 6,0, przy reliefie do Z 6,4; dwa punkty symetryczne wzgledem osi D) o 0,00085 mm i triangulacja 5 trojkatow; objetosc 22,446169 cm3 we wszystkich, gabaryt identyczny:
- `287e001fddd655f9df91663d7fb7a8cf6a9b3aa89d8bc2e470bf50f59f8be6c5` 9 x (iter8, a1, b0, c1, d0, e0, f1, g1, h1) - ODDANY (najczestszy; raport `R58_SPRAWDZ_iter5` dotyczy dokladnie tego pliku);
- `faa7a964552df24e2d07ce5be4759c64c26702ed9f94ee1724d11bb91d7f54ec` 4 x (b1, c0, d1, f0);
- `1335fe927f2d1180ebc53241e4ec04f34d6db4fb0b8e7e7c6c923dedecb02c82` 4 x (a0, e1, g0, h0).
Pokrywka: 17 / 17 budow `f1a133cf19fda391bf749797c1a7e1480a8a0062b7d49eee2d248fd5c8d70889` (deterministyczna). Przy pakowaniu brac pliki oddane, nie przebudowywac.

Komplet do drukarni (sekcja 7 raportu `R58_SPRAWDZ_iter5`): 6 plytek x 48,91 / 49,20 + 3 wkladki x 22,45 = 361,66 cm3 -> 325...579 zl (bez zmian wzgledem rundy 2); druk wlasny: 4 pokrywki x 25,06 PETG.

Zrodla (stan koncowy rundy 3): `ramka_generator.py` 1518e4c2624482a33e1e370b57b4b1480320738ab517a96042629aebb8713e60 (runda 2: 54aebd7c...), `parametry.json` bdcca0f709890f6e31a1e62c1ca72345fbce7e044ff9f702799dde8554307297 (runda 2: d90d5759...); plan i protokol - SHA w commicie (tabele 3 planu w przebiegach rundy 3 takie jak w commicie; porownanie 0 roznic).

## R3-1. Co zmieniono (geometria i parametry)

| Klucz `parametry.json` | Runda 2 | Runda 3 | Powod |
|---|---|---|---|
| `round_key_rib_top_r1` (nowy) | - (czesc gorna do lica sciecia 49,756) | 49,2 | P1: kolnierz pokrywki (lico r 50,3, dol Z 6,5) przy plytce przesunietej o luz 0,4 i pokrywce o luz 0,3 od strony zebra schodzil na osi zebra do r 49,6 i siadal na czesci zebra nad wierzchem wkladki (wnikanie 0,16) |
| `round_cover_slit_h` | 12 | 15 | P2: dluzszy jezyk (garb 13 od nasady) - odksztalcenie nasady z rachunku recenzenta ok. 0,53 % nominalnie / 0,93 % w najgorszym przypadku (runda 2: 0,90 / 1,57 %) |
| `round_cover_slit_end_d` (nowy) | - (koniec szczeliny ostry prostokat) | 2,0 | P2: zaokraglony koniec - otwor przelotowy o2,0 przez scianke kolnierza, srodek na osi szczeliny na jej gornym koncu (dziurka od klucza) |

Opisy zmienione (wartosci bez zmian): `round_key_rib_r0` (powyzej Z 6 koniec na `round_key_rib_top_r1`), `round_key_rib_chamfer` (faza takze na krawedzi zewnetrznej czesci gornej).

- Wkladka: czesc zebra powyzej wierzchu wkladki (Z 6...7) konczy sie promieniowo na r 49,2; faza 1,0 x 45 st. takze na nowej krawedzi zewnetrznej (bryla bez komplikacji: ta sama bryla z pierscieni, gorny pierscien u 47,5...48,2 zamiast 47,5...49,756) -> wierzch 1,0 x 0,7; ponizej Z 6 zebro bez zmian (do lica sciecia 49,756, zrosniete ze sciana, faza otworu za zebrem wypelniona). Wysokosc 4,5, szerokosc 3,0, r0 46,5, faza 1,0 bez zmian. Objetosc -0,002 cm3.
- Pokrywka: 8 szczelin 1,0 szerokosci, od dolnej krawedzi kolnierza do Z -5 (15), na gornym koncu otwor o2,0 (srodek Z -5, gorny koniec Z -4,0; do spodu wierzchu pokrywki Z -2 zostaje 2,0 >= 1,5; do wierzchu 4,0). Polozenia katowe bez zmian (garb +-7,4 st.).

## R3-2. Generator (`ramka_generator.py`) - zmiany rundy 3

- `KLUCZE_R58` + `round_key_rib_top_r1`, `round_cover_slit_end_d` (20 kluczy).
- `bryly_zebra_klucza`: gorny pierscien czesci gornej do `r1 - c` (faza na krawedzi zewnetrznej), pierscienie dolne do `r1`; walidacja `r0 + 2c < r1 <= lico sciecia` (inaczej `BladProjektu`, bez cichej zmiany).
- `zbuduj_pokrywke_okragla`: szczelina do `-wys + round_cover_slit_h`, otwor koncowy = walec wzdluz promienia (`bm_stozek_os('X', ...)` obrocony na kat szczeliny); walidacja: otwor >= szerokosc szczeliny, gorny koniec ponizej spodu wierzchu.
- K-65 (e): wierzch mierzony w srodku wierzchu (u (r0 + r1)/2); koniec czesci gornej z 2 promieni poziomych z zewnatrz (Z 6,25 / 6,75) -> r1 i nachylenie fazy; sondy fazy zewnetrznej i pustki nad wierzchem za koncem zebra.
- K-66: szczelina - szerokosc czesci prostej (Z -13), otwor koncowy - srodek Z i srednica z promieni pionowych z wnetrza otworu (v +-0,75), szerokosc na Z srodka, gorny koniec (promien od dolu w osi) i odstep do spodu wierzchu (>= 1,5); przeglad co 0,1 st. na Z -13 i na Z -5 (8 sektorow, szerokosc otworow 2,21 st.); odstepy katowe szczelin i otworow od siebie, od garbow i od wyciec (otwor i jego wlasna szczelina pominiete); sondy przelotowosci otworu przy obu licach.
- K-67: luz nad zebrem w srodku wierzchu; nowa funkcja `kolnierz_w_skrajnych` (+ `swobodny_przesuw`, `probki_krawedzi`, `wierzcholki_skurczone`, `opis_kolnierza`): kolnierz w ustawieniach skrajnych i kontrola czulosci na geometrii rundy 2 (argument `--r58-runda2 <katalog wzgledem --out>`; bez niego K-67 pisze "nie wykonana").
- `narzedzia/studium_R58.py`: argument `--zebro_r1` (domyslnie z `parametry.json`), 2 nowe warunki (R3-0).

## R3-3. Wyniki K rundy 3 (`raport_wykonawcy_R58_SPRAWDZ_iter5.md`, pliki oddane; te same wartosci w `R58_iter8`)

| K | Wynik | Kluczowe wartosci (z siatek) |
|---|---|---|
| K-01...K-16, K-61, K-62, K-64 | ZAL | plytki i JSON bez zmian - wartosci jak w rundzie 2 |
| K-65 | ZAL | sondy 90 / 90; (e) zebro: szerokosc 3,000, poczatek r 46,500, wierzch Z 7,000; czesc nad wierzchem: koniec zewnetrzny u 48,950 / 48,450 na Z 6,25 / 6,75 -> koniec r 49,200 (zadane 49,2), nachylenie fazy -1,00 (45 st.); nad wierzchem przy licu sciecia pusto (sonda) |
| K-66 | ZAL | sondy 133 / 133; 8 szczelin (17,60 / 32,40 / 147,60 / 162,40 / 197,60 / 212,40 / 327,60 / 342,40 st.): szerokosc 1,000, srodek otworu 15,000 od dolu kolnierza (Z -5,000), o otworu 1,991 z promieni pionowych przy v +-0,75 (32-kat) / 2,000 na Z srodka, gorny koniec Z -4,000, odstep do spodu wierzchu (Z -2,000) **2,000**; przeglad: 8 sektorow na Z -13 i 8 na Z -5 (szerokosc 2,2 st., oczekiwane 2,21); odstepy katowe: garb-szczelina 1,14 st. (1,00 mm), garb-otwor 0,57 st. (0,50 mm; otwor 12 mm wyzej niz garb), otwor-otwor 12,53 st., otwor-szczelina 13,10 st., szczelina-szczelina 13,67 st., otwor-wyciecie 39,11 st., szczelina-wyciecie 39,68 st. - wszystkie > 0 |
| K-67 | ZAL | nominal jak w rundzie 2 (17 par bez kolizji, luz 0,4, zebro w rowku 0,3 / 0,3, czolo 0,5, nad zebrem 0,5, garby 0,4, kolnierz nad wkladka 0,500); **kolnierz w ustawieniach skrajnych**: 8 kierunkow od osi D co 45 st.; przesuw plytki (swobodny z siatek, max 0,4): 0,400 / 0,398 / 0,300 / 0,400 / 0,399 / 0,400 / 0,300 / 0,400 (kierunki -45 / 0 / 45 / 90 / 135 / 180 / 225 / 270 st.; styczne do zebra 0,300 - zebro w rowku), pokrywka wzgledem plytki 0,300 we wszystkich; 8 plytek x 64 = 512 ustawien (63 rozne polozenia pokrywki): kolizje wkladka-plytka / plytka-pokrywka / wkladka-pokrywka 0 / 0 / 0; **najmniejszy odstep 3D kolnierz-zebro 0,620** (plytka 0,399 + pokrywka 0,300 w kierunku 135 st., tj. od zebra - lico kolnierza po stronie zebra najblizej zebra; najblizej dolna krawedz kolnierza Z 6,5 - faza zewnetrzna zebra); luz w rzucie lico kolnierza - zebro nad wierzchem min 0,375 (na narozach zebra v +-1,5; na osi zebra 49,601 - 49,2 = 0,40); kolnierz - wkladka 0,500; czulosc przesuwow: swobodny + 0,12 daje kolizje w 8 / 8 kierunkach (plytka-wkladka i pokrywka-plytka); **czulosc na geometrii rundy 2**: to samo ustawienie (0,399 + 0,300 od zebra) - kolizja wkladka-pokrywka 11 par, luz w rzucie -0,180 (recenzent na osi: -0,16), kolizja w 3 / 63 polozeniach pokrywki; ulozenia plaskie: kazda z 8 plytek okno -0,75...+0,75 st. (jedyne, bez zmian), poza strefa naprowadzenia +-2,00 st. (runda 2: +-1,75) plytka lezy na zebrze: uniesienie 4,48 (bez zmian), przechyl 2,61 st., krawedz +4,56 (runda 2: 2,59 st.; punkt oparcia na wierzchu zebra blizej srodka plytki, r ok. 48,3); geometria rundy 1 nadal odtwarza okna 90/180/270 st. |

## R3-4. Porownanie SHA plytek i JSON z runda 2 (10 / 10)

Lista rundy 2 = `sha256_stl_po_R58.txt` z commita 2be8676 (kopia przed poprawka); runda 3 = ta sama lista po rundzie 3. Roznia sie tylko 2 wiersze (wkladka, pokrywka).

| Plik | Runda 2 | Runda 3 | Bajtowo |
|---|---|---|---|
| `stl/ramka_plytka_okragla_ramkowa_poranna_n4_v2.stl` | 5d81f55b8b114ba9cf307bb4ba63e70083aa6570ab0bb646acef69b8cd6cceb5 | 5d81f55b8b114ba9cf307bb4ba63e70083aa6570ab0bb646acef69b8cd6cceb5 | tak |
| `stl/ramka_plytka_okragla_ramkowa_poranna_n5_v2.stl` | 64867b5b63a31db88715c9c9636c33015566bbe48af2c8f4a90330797f063381 | 64867b5b63a31db88715c9c9636c33015566bbe48af2c8f4a90330797f063381 | tak |
| `stl/ramka_plytka_okragla_ramkowa_poranna_n6_v2.stl` | 7630a029157b2fc65144c5f6b32ad28c02048f0642855cc3d23c2570ea28991e | 7630a029157b2fc65144c5f6b32ad28c02048f0642855cc3d23c2570ea28991e | tak |
| `stl/ramka_plytka_okragla_ramkowa_poranna_v2.stl` | 845e4bd61b40562010dec24b18ee873e90d8937f07728f81589c407f826ba266 | 845e4bd61b40562010dec24b18ee873e90d8937f07728f81589c407f826ba266 | tak |
| `stl/ramka_plytka_okragla_ramkowa_wieczorna_n1_v2.stl` | 84d361e2389bef12fd07278bf3e2e65fd170c83d4012f8fbbfa12b8ad172325f | 84d361e2389bef12fd07278bf3e2e65fd170c83d4012f8fbbfa12b8ad172325f | tak |
| `stl/ramka_plytka_okragla_ramkowa_wieczorna_n2_v2.stl` | 7848aa2395638b338e4bd2e83473b1329c53c61500a7ec1ba5a63a8c5aaaaa94 | 7848aa2395638b338e4bd2e83473b1329c53c61500a7ec1ba5a63a8c5aaaaa94 | tak |
| `stl/ramka_plytka_okragla_ramkowa_wieczorna_n3_v2.stl` | 1b8ac3d390870f0a4607b3289f50201ef28cf2049801ac853aaa1427735321aa | 1b8ac3d390870f0a4607b3289f50201ef28cf2049801ac853aaa1427735321aa | tak |
| `stl/ramka_plytka_okragla_ramkowa_wieczorna_v2.stl` | 322eb892b7acf81ce5e0ff5f437436b44f22490a662f1b1bd9939353b4a4125c | 322eb892b7acf81ce5e0ff5f437436b44f22490a662f1b1bd9939353b4a4125c | tak |
| `stl/ramka_wkladka_okragla_v2.stl` | baf94bf89665987d0f3866433e5fa19908f86ccaed2d3307aefea4df04bc0fdb | 287e001fddd655f9df91663d7fb7a8cf6a9b3aa89d8bc2e470bf50f59f8be6c5 | NIE (zmiana rundy 3) |
| `stl/ramka_pokrywka_okragla_v2.stl` | 8e2385350d459540c272748f04b26b0d9e1e5d8ba1c8cf73d5255f09d9223787 | f1a133cf19fda391bf749797c1a7e1480a8a0062b7d49eee2d248fd5c8d70889 | NIE (zmiana rundy 3) |
| `json/uklad_gniazd_okragla_ramkowa_poranna.json` | ab6e02a0a9602216d4b9251a725d4281a4e04c1db6d1261af6a7ab97e4517412 | ab6e02a0a9602216d4b9251a725d4281a4e04c1db6d1261af6a7ab97e4517412 | tak |
| `json/uklad_gniazd_okragla_ramkowa_wieczorna.json` | d66ef99b799f37c241b83b73d979ab70a5810cec7fc4aec369f3e0da6c4c17a9 | d66ef99b799f37c241b83b73d979ab70a5810cec7fc4aec369f3e0da6c4c17a9 | tak |

## R3-5. Przebiegi rundy 3 (PC, `<PC-katalog>\r58\Ramki`, Blender 5.2.3 LTS, jeden moj proces naraz, wolny RAM 17,25 GB przed startem, bez innego Blendera; logi `_r58\*.log`)

| # | Przebieg | Wynik |
|---|---|---|
| 1 | kopia 10 STL rundy 2 do `wyniki_v2/stl_r58_runda2/` (MSI i PC; SHA = lista rundy 2) | 10 plikow |
| 2 | `--etap R58 --iter 8 --r58-poprzednie stl_r58_runda1 --r58-runda2 stl_r58_runda2` | 19 ZAL / 0 NIE; plytki + JSON 10 / 10 = runda 2; wkladka 287e001f, pokrywka f1a133cf |
| 3 | `r3_warianty.py` w 8 osobnych procesach (a...h) po 2 budowy wkladki i pokrywki | warianty wkladki R3-0; pokrywka 16 / 16 f1a133cf |
| 4 | `--etap R58_SPRAWDZ --iter 5 --r58-poprzednie stl_r58_runda1 --r58-runda2 stl_r58_runda2` (pliki oddane) | 19 ZAL / 0 N/D / 0 NIE |
| 5 | `--etap SPRAWDZ --iter 17` | 58 ZAL / 5 N/D / 0 NIE |
| 6 | SHA wszystkich plikow `wyniki_v2/stl` i `json` na PC | 25 / 25 R59; 12 plikow R58 = lista rundy 3 |

## R3-6. Odpowiedz na recenzje runda 2 (kazda uwaga)

- **P1** (kolnierz na wierzchu zebra, wnikanie 0,16) - poprawione wg decyzji koordynatora: `round_key_rib_top_r1` 49,2 (czesc nad Z 6), faza 1,0 takze na krawedzi zewnetrznej (nie komplikuje bryly). K-67 dopisane: ustawienia skrajne 8 x 8 kierunkow (w tym w strone zebra -45 st. i od zebra 135 st.) dla kazdej z 8 plytek - 0 kolizji, odstep 3D kolnierz-zebro 0,620, w rzucie 0,375 (naroza) / 0,40 (os); kontrola czulosci: geometria rundy 2 daje kolizje w ustawieniu 0,40 + 0,30 od zebra (11 par, -0,180). Okno plytki -0,75...+0,75 st. (jedyne) bez zmian, uniesienie w zlym obrocie 4,48.
- **P2** (jezyk pokrywki) - poprawione: `round_cover_slit_h` 15 i otwor koncowy `round_cover_slit_end_d` 2,0; K-66 mierzy wysokosc 15, otwor (o, srodek), odstep konca od spodu wierzchu 2,0 i rozlacznosc. Ryzyko zostaje: **1 sztuka probna przed seria** (rachunek recenzenta: ok. 0,53 % nominalnie, ok. 0,93 % w najgorszym przypadku; 3,7...6,5 N na garb) - ryzyko 2 w R3-7.
- **D1** (pasek 0,5 x 0,156 przy scieciu) - bez zmiany (zgodnie z recenzja; plytki bez zmian).
- **D2** (odczyt w zlym obrocie na zebrze: czujniki A i C ok. 3,95 mm od magnesu, prog D5 przy 4 mm) - dopisane do ryzyk i "co dalej" jako wymaganie dla paczki programu (R3-7).
- **D3** (plan 13, wpis R58; plan 14 p. 30) - poprawione: z glownej kolumny wpisu R58 usuniete `round_key_pin_*` (w ich miejscu klucze zebra rundy 2 i 3 oraz szczelin), dopisek rundy 2 bez nazw kluczy kolka, dopisek rundy 3; p. 30 odsyla do sekcji R2-0...R2-9, nowy p. 31 (runda 3) do R3-0...R3-7. Zostal tylko wiersz skreslony w tabeli 3.4 (konwencja usunietych kluczy).
- **D4** (warianty bajtowe wkladki) - oddany wariant najczestszy 287e001f (9 / 17), wszystkie SHA w R3-0; raport `R58_SPRAWDZ_iter5` na tym pliku; przy pakowaniu tylko ten plik.
- **D5** (uwagi rundy 1 D4, D5, D8 otwarte swiadomie) - bez zmian (poza geometria; arkusz zamowienia R58 nie byl ruszany).
- **D6** (metoda K-67: siatka 0,1, erozja 1 wezla) - bez zmian; wynik rundy 3 ta sama metoda: okno -0,75...+0,75 st. dla 8 plytek.

## R3-7. Ryzyka i co dalej - zmiany wzgledem sekcji 11 i 12

- Ryzyko 2 (zatrzask pokrywki) - stan rundy 3: garb na jezyku 12 x 15 x 1,5 (13 od nasady) miedzy szczelinami zakonczonymi otworem o2,0 (bez ostrego naroza na koncu szczeliny); rachunek recenzenta: odksztalcenie nasady ok. 0,53 % nominalnie / 0,93 % w najgorszym przypadku (runda 2: 0,90 / 1,57 %), 3,7...6,5 N na garb; druk wierzchem w dol - naprezenie przy nasadzie w poprzek warstw. **Wydrukowac 1 sztuke probna przed 4**; jesli zatrzask za slaby / za mocny - `cover_snap_bump`, `round_cover_slit_h` albo katy, nowa sztuka probna.
- Ryzyko 8 (klucz, zly obrot) - stan rundy 3: plytka lezy plasko tylko w oknie -0,75...+0,75 st.; w zlym obrocie lezy na zebrze (uniesienie 4,48, przechyl 2,61 st., krawedz +4,56) - wyraznie widoczne. **Wymaganie dla paczki programu (D2 recenzji rundy 2):** przy takim przechyle czujniki A i C sa ok. 3,95 mm od magnesu (prog D5 przy 4 mm), wiec ramka moze odczytac numer obroconej plytki - program ma ostrzegac, gdy odczytany numer nie pasuje do roli ramki (n1-n3 na P, n4-n6 na W), i nie przyjmowac takiego odczytu bez potwierdzenia.
- Nowe (informacyjnie): czesc zebra nad wierzchem wkladki to czapka 1,0 wysokosci z fazami ze wszystkich stron (wierzch 1,0 x 0,7); upuszczona plytka moze wgniesc krawedz fazy (kosmetycznie, ocena recenzenta dla rundy 2 dotyczy tej samej czapki); nizej zebro zrosniete ze sciana.
- Co dalej (zamiast sekcji 12 p. 1 i 3): (1) recenzja rundy 3 - tylko wkladka i pokrywka (plytki i JSON bajtowo jak w recenzji rundy 2); (2) paczka programu: ostrzezenie o numerze niepasujacym do roli ramki (D2) i kalibracja z ukladu kwadratowego po numerze (ryzyko 9); (3) pakiet i SHA256SUMS: wkladka 287e001f, pokrywka f1a133cf, plytki i JSON bez zmian; (4) pokrywka: 1 sztuka probna przed seria.

# STAN PO RUNDZIE 2 (poprawki po recenzji `recenzja/raport_recenzenta_R58_runda1.md`, B 1 / P 3 / D 8) (historia)

Sekcje R2-0 ... R2-9 opisuja stan oddany po rundzie 2. Sekcje 0 ... 12 nizej to zapis rundy 1 (historia; liczby i SHA rundy 1 nieaktualne tam, gdzie R2 mowi inaczej).

## R2-0. Wynik

- `--etap R58_SPRAWDZ --iter 4 --r58-poprzednie stl_r58_runda1` na plikach oddanych: 19 ZAL, 0 N/D, 0 NIE (B 0 / P 0 / D 0); 1744 sondy, 0 niezgodnych, 0 blizej niz 0,1 od sciany; w tym nowy K-67 (szukanie ulozen plaskich, 34 s).
- Budowa: `--etap R58 --iter 7` (generator koncowy 54aebd7c...): 19 ZAL / 0 NIE; czysta kopia folderu `--out wyniki_powt` 3 razy: 19 ZAL / 0 NIE, 9 plytek + pokrywka + 2 JSON bajtowo = pliki oddane za kazdym razem.
- `--etap SPRAWDZ --iter 16` (stare pliki, generator koncowy): 58 ZAL, 5 N/D, 0 NIE; sekcje 3-6 i zalacznik A identyczne z `SPRAWDZ_iter12` poza dopiskiem K-60 (18 kluczy R58).
- 25 plikow R59 bez zmian: 25 / 25 na PC (po wszystkich przebiegach rundy 2) i na MSI.
- P3: `--etap A --out wyniki_test_p3` na kopii katalogu (21 STL R59 + 10 R58 + 6 JSON): czyszczenie pominelo 10 STL R58 (dziennik raportu), po przebiegu 10 / 10 plikow R58 = pliki oddane (SHA), 13 przebudowanych plikow etapu A (12 plytek + pokrywka) = `SHA256SUMS_2026-11-16_R59.txt` 13 / 13 (raport `wyniki_v2/raport/raport_wykonawcy_A_kopiaP3_iter1.md`: 25 ZAL, 2 N/D, 0 NIE). Test funkcji bez Blendera: `narzedzia/test_R58_p3_d1.py` (wynik w R2-8).
- `narzedzia/studium_R58.py` (koordynatora, poprawione pod nowa geometrie): BLEDY 0, kod 0.
- Plan <-> JSON: 0 roznic; walidator R14: 305 kluczy (287 + 18 R58), LICZONE 0,0000.

Pliki oddane (STL w `Ramki/wyniki_v2/stl/` worktree, poza gitem; lista `wyniki_v2/raport/sha256_stl_po_R58.txt`; gabaryt w orientacji druku z siatki; pliki rundy 1 odlozone w `wyniki_v2/stl_r58_runda1/` na MSI i PC):

| Plik | SHA-256 (runda 2) | Objetosc [cm3] | Gabaryt X x Y x Z [mm] | Szt. / material |
|---|---|---|---|---|
| `ramka_plytka_okragla_ramkowa_wieczorna_v2.stl` (bazowy) | 322eb892b7acf81ce5e0ff5f437436b44f22490a662f1b1bd9939353b4a4125c | 48,90 | 100,000 x 100,000 x 8,000 | - (wzorzec) |
| `ramka_plytka_okragla_ramkowa_wieczorna_n1_v2.stl` | 84d361e2389bef12fd07278bf3e2e65fd170c83d4012f8fbbfa12b8ad172325f | 48,91 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_plytka_okragla_ramkowa_wieczorna_n2_v2.stl` | 7848aa2395638b338e4bd2e83473b1329c53c61500a7ec1ba5a63a8c5aaaaa94 | 48,91 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_plytka_okragla_ramkowa_wieczorna_n3_v2.stl` | 1b8ac3d390870f0a4607b3289f50201ef28cf2049801ac853aaa1427735321aa | 48,91 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_plytka_okragla_ramkowa_poranna_v2.stl` (bazowy) | 845e4bd61b40562010dec24b18ee873e90d8937f07728f81589c407f826ba266 | 49,18 | 100,000 x 100,000 x 8,000 | - (wzorzec) |
| `ramka_plytka_okragla_ramkowa_poranna_n4_v2.stl` | 5d81f55b8b114ba9cf307bb4ba63e70083aa6570ab0bb646acef69b8cd6cceb5 | 49,20 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_plytka_okragla_ramkowa_poranna_n5_v2.stl` | 64867b5b63a31db88715c9c9636c33015566bbe48af2c8f4a90330797f063381 | 49,20 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_plytka_okragla_ramkowa_poranna_n6_v2.stl` | 7630a029157b2fc65144c5f6b32ad28c02048f0642855cc3d23c2570ea28991e | 49,20 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_wkladka_okragla_v2.stl` | baf94bf89665987d0f3866433e5fa19908f86ccaed2d3307aefea4df04bc0fdb | 22,45 | 130,000 x 148,400 x 10,500 | 3 / PA12 drukarnia |
| `ramka_pokrywka_okragla_v2.stl` | 8e2385350d459540c272748f04b26b0d9e1e5d8ba1c8cf73d5255f09d9223787 | 25,12 | 103,600 x 103,600 x 20,000 | 4 / PETG FDM (wlasny) |
| `json/uklad_gniazd_okragla_ramkowa_wieczorna.json` | d66ef99b799f37c241b83b73d979ab70a5810cec7fc4aec369f3e0da6c4c17a9 | - | - | - |
| `json/uklad_gniazd_okragla_ramkowa_poranna.json` | ab6e02a0a9602216d4b9251a725d4281a4e04c1db6d1261af6a7ab97e4517412 | - | - | - |

Wkladka - warianty bajtowe (boolean EXACT, jak w rundzie 1 i jak wkladka kwadratowa): w 6 budowach rundy 2 powstaly 3 warianty roznicace sie tylko 1-2 wierzcholkami na krawedzi otworu na wysokosci polki (Z 2,5; punkty symetryczne wzgledem osi D) o 0,00085 mm i triangulacja 5-10 trojkatow; objetosc 22,448114 cm3 we wszystkich, gabaryt identyczny: `baf94bf89665987d0f3866433e5fa19908f86ccaed2d3307aefea4df04bc0fdb` 3 x (czyste kopie a, b, c) - ODDANY; `f751581235e6930627af132ba5b03efaecc9dec1a2a81fd62b81d97a8338bcd3` 2 x (iter5, iter6); `3ad9c7ef3ba9ebc1...` 1 x (iter7; pelna suma w `raport_wykonawcy_R58_iter7.md`). Raport oddany `R58_SPRAWDZ_iter4` dotyczy dokladnie pliku baf94bf8 (wstawiony do `wyniki_v2/stl` na PC przed sprawdzeniem). Przy pakowaniu brac ten plik, nie przebudowywac.

Komplet do drukarni (sekcja 7 raportu `R58_SPRAWDZ_iter4`): 6 plytek x 48,91 / 49,20 + 3 wkladki x 22,45 = 361,66 cm3 -> 325...579 zl (stawka 0,90...1,60 zl/cm3, czesci biale bez mnoznikow); druk wlasny: 4 pokrywki x 25,12 PETG.

Zrodla (stan koncowy rundy 2): `ramka_generator.py` 54aebd7c2caf1fef4f445573af5775d245b656595e8bd2beb97c8c905feff537 (runda 1: fe6cd095...), `parametry.json` d90d57593f4d51a8ed5d26a652cf1c59fb919130e150dee5be75f60d66c65e8d (runda 1: 2686c881...), `plan_ramki_v2.md` i `protokol_weryfikacji_v2.md` - SHA w commicie (plan czyta generator tylko w `porownaj_plan_z_json`; przebiegi rundy 2 szly z planem o tych samych tabelach 3, roznica tylko w opisach - porownanie za kazdym razem 0 roznic).

## R2-1. Co zmieniono (geometria i parametry)

| Czesc | Bylo (runda 1) | Jest (runda 2) | Klucze |
|---|---|---|---|
| Wkladka okragla - klucz | kolek o3 x 2 na polce D (r 45), faza 0,5 | ZEBRO na osi D przy scieciu: szerokosc styczna 3,0; od r 46,5 do lica sciecia 49,756; ponizej Z 6 zrosniete ze sciana sciecia (faza otworu za zebrem wypelniona, jedna bryla); powyzej Z 6 konczy sie na licu sciecia; wierzch Z 7,0 (4,5 nad polka, 1,0 nad wierzchem wkladki); faza 1,0 na obu bokach i czole wewnetrznym (wierzch 1,0 szeroki); polka D 10 x 10 zostaje | usuniete `round_key_pin_d/h/chamfer`; nowe `round_key_rib_w` 3,0, `round_key_rib_r0` 46,5, `round_key_rib_h` 4,5, `round_key_rib_chamfer` 1,0 |
| Plytka okragla ramkowa - rowek klucza | r0 43, wysokosc 2,5 (Z -8...-5,5) | r0 46,0, wysokosc 5,0 (Z -8...-3,0), szerokosc 3,6 bez zmian; wierzch plytki bez zmian | `round_key_slot_r0` 46,0, `round_key_slot_h` 5,0 |
| Pokrywka okragla | 4 garby, bez szczelin | + 8 pionowych szczelin odciazajacych przez kolnierz: 1,0 x 12 od dolnej krawedzi, srodki +-6,5 po licu wewnetrznym od srodka garbu (+-7,4 st.); garb na jezyku 12 x 12 x 1,5 | nowe `round_cover_slit_w` 1,0, `round_cover_slit_h` 12, `round_cover_slit_offset` 6,5 |
| Gabaryt / objetosc | wkladka 10,1 / 22,42; pokrywka 25,26; plytka poranna bazowa 49,19 | wkladka 10,5 / 22,45; pokrywka 25,12; plytka poranna bazowa 49,18 (rowek klucza 3,6 x 5,0 x 3,36 zamiast 3,6 x 2,5 x 6,36) | - |

Luzy klucza: zebro 3,0 w rowku 3,6 = 0,3 na strone; czolo zebra r 46,5 vs koniec rowka r 46,0 = 0,5; nad zebrem 5,0 - 4,5 = 0,5 (zmierzone w K-67: 0,300 / 0,300, 0,500, 0,500). Zebro siega r 49,756, kieszen magnesu konczy sie na r 47,6: 2,156 >= 1,5 - w zadnym obrocie i przesunieciu w luzie zebro nie miesci sie w kieszeni. Sciecie zostaje jako znak wzrokowy i oparcie zebra - NIE jest blokada (wnikanie plytki w sciecie wkladki 0,244 < luz 0,4).

## R2-2. Generator (`ramka_generator.py`) - zmiany rundy 2

| # | Miejsce | Zmiana | Powod (uwaga recenzji) |
|---|---|---|---|
| 1 | `bryly_zebra_klucza`, `zbuduj_wkladke_okragla` | zebro (czesc dolna do lica + faza otworu + 0,2, czesc gorna z faza) doklejane PO roznicach (`dodatnie_po`), zeby faza otworu go nie ciela; kolek usuniety | B1 |
| 2 | `zbuduj_pokrywke_okragla`, `polozenia_szczelin_pokrywki` | 8 szczelin (bryly rownolegloscienne wzdluz promienia, po dwie na garb) | P2 |
| 3 | `rdzenie_R58`, `wyczysc_wyniki(out, P)`, `main` | czyszczenie przed A/B/C/ALL pomija STL kompletu R58 (lista z parametrow: typy R58, `plate_numbers_round_frame`, wkladka i pokrywka okragla); wpis w dzienniku raportu | P3 |
| 4 | `zrzut_parametrow_zgodny` | wyjatek K-60 tylko gdy w zrzucie nie ma ZADNEGO klucza R58, wszystkie sa w `parametry.json` i poza tym brak roznic | D1 |
| 5 | `klasy_scian_plytki`, `probki_scian`, `scianki_3d_plytki`, K-64 (d) | scianki 3D z siatki (probki co <= 0,2 mm na rowku klucza, rowku pokrywki i kieszeniach -> najblizsza powierzchnia wnetrza, BVH `find_nearest`); stale z parametrow usuniete | D2, D3 |
| 6 | `sprawdz_okragla` K-61 (b) | dla ramkowej na Z -4 i -7,5 promienie rownolegle odsuniete o +-4,9 (rowek klucza w osi siega Z -3) | nowa geometria |
| 7 | `sprawdz_wkladke_okragla` K-65 (a), (e) | sciecie mierzone promieniami odsunietymi (w osi zebro); (e) zebro: szerokosc, poczatek, wierzch, koniec nad wierzchem na licu, zrosniecie ze sciana, fazy | B1 |
| 8 | `sprawdz_pokrywke_okragla` K-66 | szczeliny: szerokosc, wysokosc, przelotowosc, przeglad co 0,1 st., odstepy od garbow / wyciec / siebie; sprawdzenie "obok luku garbu" w polowie przerwy garb-szczelina | P2 |
| 9 | `sprawdz_pasowania_R58` K-67 + `mapa_przeszkod_wkladki`, `mapa_spodu_plytki`, `unoszenie`, `przedzialy`, `ulozenia_plaskie`, `opis_ulozen` | zebro w rowku (boki, czolo, nad zebrem); kolnierz z calego pierscienia (D2); szukanie ulozen plaskich obrot x przesuniecie dla kazdej z 8 plytek z kontrola czulosci; informacyjnie n8/n9 i geometria rundy 1 (`--r58-poprzednie`) | B1, P1, D2, D7 |
| 10 | `etap_R58`, `main` | argument `--r58-poprzednie DIR`; referencje n8/n9 (pliki R59, tylko odczyt) | B1, D7 |
| 11 | `KLUCZE_R58`, `odstepstwa_informacyjne_R58` | 18 kluczy; rejestr: K-60 (D1), K-61 (Z -4 i -7,5), pokrywka ze szczelinami, nowy wpis o metodzie K-67 | - |

## R2-3. Wyniki K rundy 2 (`raport_wykonawcy_R58_SPRAWDZ_iter4.md`, pliki oddane)

| K | Wynik | Najwazniejsze wartosci zmierzone |
|---|---|---|
| K-01...K-04b | ZAL | 10 STL szczelne, 1 skladowa; objetosci 48,90-49,20 / 22,45 / 25,12 w +-30 % od 49 / 22 / 25; gabaryty jak w tabeli R2-0 |
| K-05, K-16 | ZAL | jak runda 1 (uklad R59; sockets = kwadrat) |
| K-06...K-09, K-11, K-13 | ZAL | jak runda 1 (8 plytek) |
| K-61 | ZAL | promien 49,996...50,000; sciecie 49,356 na Z -4 i -7,5 (promienie +-4,9 od osi) |
| K-62 | ZAL | jak runda 1 |
| K-64 | ZAL | kieszenie (+-31,820; +-31,820) o 5,200 x 5,194, gl. 2,200, scianka do krawedzi 2,402; rowek pokrywki 0,800 x 1,000, srodek Z -2,000, w scieciu dno r 49,200; rowek klucza 3,600 x 5,000 od r 46,000; scianki 3D (wieczorna / poranna): rowek klucza - wnetrze 2,676 (rynienka) / 6,364 (gniazdo o12,5 id 2), rowek pokrywki - wnetrze 2,718 / 2,682 (stozek C; do gniazd 3,55 / 3,08), kieszenie - wnetrze 1,851 (A, dno rynienki) / 2,801 (A, stozek), rowek klucza - rowek pokrywki 0,500 (pasek przy scieciu, informacyjnie); mapa wierzchu = plytka okragla R59 (0 roznic) |
| K-65 | ZAL | otwor o100,795, sciecie 49,756 (4 promienie); wystep r 47; polka 2,500; kieszenie Halla w osiach (0,000); ZEBRO: szerokosc 3,000 (os 0,000), poczatek r 46,500, wierzch Z 7,000, nad wierzchem konczy sie na u 49,756; sondy zrosniecia i faz zgodne; scianka w osiach 2,001-2,003; dno 2,903; wyciecie 30,000; K-56 0; zgodnosc z wkladka kwadratowa (K-29 20/20, K-30 7/7, mapy 0 roznic); kanaly ciagle |
| K-66 | ZAL | o100,593...100,600 / 103,593...103,600; wierzch 2,000; garby 25/155/205/335 st. wystep 0,700, Z -18,000; wyciecia 30 x 3; SZCZELINY 8 x 1,000 x 12,000 na 17,60 / 32,40 / 147,60 / 162,40 / 197,60 / 212,40 / 327,60 / 342,40 st.; przeglad co 0,1 st.: 8 przelotowych sektorow (srodki +-0,05 st.); odstepy: szczelina-garb 1,14 st. (1,00 mm), szczelina-szczelina 13,67 st. (12,00 mm), szczelina-wyciecie 39,68 st. (34,83 mm) |
| K-67 | ZAL | 0 kolizji nominalnych (17 par); luz promieniowy 0,397-0,402, na scieciu 0,400; spod 2,500 = polka; osie magnes-Hall 0,000; zebro w rowku 0,300 / 0,300, czolo 0,500, nad zebrem 0,500; pokrywka 0,300; garby 0,400 w rowku, dZ 0,000; kolnierz 0,500 nad wkladka (max Z wkladki 6,000 w calym pierscieniu r 50,2-51,9); ULOZENIA PLASKIE - patrz R2-4 |

## R2-4. Klucz: okno wejscia i ulozenia plaskie (K-67, B1 i P1)

Metoda (z siatek): mapa wysokosci wierzchu wkladki (promienie z gory co 0,1 mm w kole R + luz + 0,1; przeszkody = 4598 wezlow z Z > polka + 0,02: sciana otworu, sciecie, zebro) i mapa spodu kazdej plytki (promienie od spodu co 0,1 mm w pierscieniu przeszkod; 0 = pelny spod, kieszen 2,2, rowek klucza 5,0; braki materialu poszerzone o 1 wezel). Dla kazdej z 8 plytek (puste kieszenie NIE zaklejone - najgorszy przypadek): obrot 0...360 st. co 0,25 st. x przesuniecie w kole luzu 0,4 co 0,1 mm (49 polozen) -> uniesienie potrzebne, zeby plytka nie kolidowala przy spodzie na polce (min po przesunieciach). Uniesienie 0 = plytka lezy plasko.

| Plytka | Katy, w ktorych plytka lezy plasko | Inne katy bez kolizji | Strefa naprowadzenia (krawedz rowka na fazie zebra) | Poza nia: plytka lezy na zebrze |
|---|---|---|---|---|
| kazda z 8 (bazowe i n1...n6) | -0,75...+0,75 st. (okno 1,50 st.) | brak | -1,75...+1,75 st. | uniesienie 4,48, przechyl 2,59 st., krawedz plytki +4,52 |

Kontrola czulosci: nominal 0 st. bez przesuniecia - uniesienie 0,000; plytka opuszczona o 0,05 w polke (wszystkie wezly wkladki) - 0,030 > 0; przesunieta o luz + 0,2 w strone sciecia - 3,508 > 0; geometria rundy 1 (pliki `stl_r58_runda1`, kolek o3 x 2, rowek r0 43 / h 2,5) ta sama metoda: plytki bazowe wieczorna i poranna leza plasko w -0,75...0,75 / 88,50...91,50 / 178,50...181,50 / 268,50...271,50 st. - B1 recenzji odtworzony (recenzent: +-1,7 st.). Informacyjnie stare plytki n8/n9 w nowej wkladce: zaden kat bez kolizji, leza na zebrze (uniesienie 4,48, przechyl 2,59 st., krawedz +4,53) - ramka czyta 0 (brak magnesow).

P1 zamkniete rachunkiem: w zlym obrocie plytka nie lezy plasko i nie "prawie dobrze" - lezy na zebrze 4,5 nad polka z przechylem ok. 2,6 st. i krawedzia +4,5 (jak naroznik kwadratu na kolku 5); okno wejscia 1,5 st., strefa naprowadzenia 3,5 st. Odczyt magnesow przy przechyle nie byl liczony (pole przy 4,5 mm podniesienia krawedzi - poza tym, co ramka uznaje za poprawne ulozenie; ostrzezenie programu - paczka programu).

## R2-5. Scianki 3D rowka klucza (z siatki, K-64 d; rachunek `narzedzia/studium_R58.py`)

| Do czego | Wieczorna | Poranna | Prog |
|---|---|---|---|
| rynienka | 2,676 (siatka) / 2,67 (rachunek) | 6,90 (rachunek; nie jest najblizsza w siatce) | >= 1,5 |
| gniazda okragle | 12,31 (rachunek) | 6,364 (siatka, gniazdo o12,5 x 31 y -19,55) / 6,36 (rachunek) | >= 1,5 |
| stozki znacznikow, dolki, otwory o3 | dalej niz rynienka (w siatce zadna probka nie ma ich najblizej); otwory o3 w rzucie 12,23 | dalej niz gniazdo id 2; otwory o3 w rzucie 10,53 | >= 1,5 |
| rowek pokrywki | 0,500 tylko w pasku 0,156 przy scieciu (dno rowka pokrywki Z -2,5 nad sufitem rowka klucza Z -3,0; tam rowek pokrywki ma i tak 0,156 glebokosci - D4 recenzji) - informacyjnie | 0,500 jak obok | informacyjnie |

Wszystkie >= 1,5 poza paskiem 0,156 x 3,6 przy scieciu (opisany, bez zmiany r0 / h).

## R2-6. Przebiegi rundy 2 (PC, `<PC-katalog>\r58\Ramki`, Blender 5.2.3 LTS, jeden proces naraz, wolny RAM 17,3 GB; logi `_r58\*.log`)

| # | Polecenie | Generator | ZAL / N/D / NIE | Uwagi |
|---|---|---|---|---|
| 14 | `--etap R58 --iter 5 --r58-poprzednie stl_r58_runda1` | 85a0da912ce... | 17 / 0 / 2 | K-64 (d): rowek pokrywki - wnetrze 1,405 - trojkat fazy wierzchu przy scieciu zaklasyfikowany jako wnetrze (tolerancja promienia 0,001 < strzalka wieloboku 0,004; diagnostyka `debug_rowek.py` na PC); K-66: promien "obok luku garbu" na +-7,7 st. przechodzil przez nowa szczeline. Obie metody poprawione (geometria bez zmian) |
| 15 | `--etap R58 --iter 6 ...` | 54aebd7c2ca... (koncowy) | 19 / 0 / 0 | wkladka f7515812 |
| 16 | `--etap R58 --iter 1 --out wyniki_powt` (czysta kopia) x 2 | 54aebd7c2ca... | - | przerwane bledem: w czystej kopii brak plikow n8/n9 (odniesienie informacyjne K-67); skopiowane do kopii |
| 17, 18 | `--etap R58 --iter 1 --out wyniki_powt` (czysta kopia a, b) | 54aebd7c2ca... | 19 / 0 / 0 | wkladka baf94bf8 (oba); 11 pozostalych plikow = #15 |
| 19 | `--etap R58 --iter 7 ...` | 54aebd7c2ca... | 19 / 0 / 0 | wkladka 3ad9c7ef |
| 20 | czysta kopia c | 54aebd7c2ca... | 19 / 0 / 0 | wkladka baf94bf8; raport `raport_wykonawcy_R58powt_iter2.md` |
| 21 | wkladka baf94bf8 wstawiona do `wyniki_v2/stl` (PC); `--etap R58_SPRAWDZ --iter 4 --r58-poprzednie stl_r58_runda1` | 54aebd7c2ca... | 19 / 0 / 0 | STAN KONCOWY plikow R58 |
| 22 | `--etap SPRAWDZ --iter 16` | 54aebd7c2ca... | 58 / 5 / 0 | STAN KONCOWY plikow R59 |
| 23 | `--etap A --iter 1 --out wyniki_test_p3` (kopia) | 54aebd7c2ca... | 25 / 2 / 0 | P3 (R2-0) |

## R2-7. Dowod: 25 plikow R59 bez zmian (runda 2)

Jak w sekcji 8 (te same 25 sum): PC po przebiegu #22 - 25 / 25; MSI (21 STL w glownym repo, 4 JSON w worktree) - 25 / 25. Dodatkowo (P3) przebieg #23 przebudowal z generatora rundy 2 13 plikow etapu A w kopii: wszystkie bajtowo = SUMS R59 - generator rundy 2 buduje etap A tak jak R59.

## R2-8. Test P3 i D1 bez Blendera (`python narzedzia/test_R58_p3_d1.py Ramki`)

```
== P3: wyczysc_wyniki na kopii katalogu (pliki puste o nazwach z wyniki_v2) ==
przed: stl 14 (stare 4 + R58 10), arkusze 1, json 2
po:    stl 10, arkusze 0, json 2; pominiete przez wyczysc_wyniki: 10
zostaly dokladnie pliki R58: True ; stare usuniete: True
wywolanie bez P (dawne zachowanie) usuwa wszystko w stl: True
== D1: zrzut_parametrow_zgodny (K-60) ==
zrzut R59 bez zmian (brak wszystkich kluczy R58)                                 -> zgodny
zrzut z jednym kluczem R58 o poprawnej wartosci (pozostalych brak)               -> NIE
zrzut z jednym kluczem R58 o BLEDNEJ wartosci (pozostalych brak)                 -> NIE
zrzut bez kluczy R58, ale zmieniony stary klucz plate_size                       -> NIE
zrzut = biezacy parametry.json (pelny)                                           -> zgodny
```

## R2-9. Odpowiedz na recenzje runda 1 (kazda uwaga)

| Uwaga | Co zrobiono | Dowod |
|---|---|---|
| B1 klucz (kolek w pustej kieszeni, sciecie nie blokuje) | decyzja koordynatora: zebro na osi D przy scieciu zamiast kolka (R2-1); rowek plytki r0 46 / h 5; klucze kolka usuniete z `parametry.json`, `WYMAGANE_KLUCZE`, planu (3.4 skreslone) i protokolu; zdania o "blokadzie" scieciem poprawione w planie (D5, 4.1b p. 3, 4.11, rejestr R58) i w studium; K-67 przerobione (przeszukanie obrotu i przesuniecia, kazda z 8 plytek, kontrola czulosci, geometria rundy 1) | R2-4: tylko okno -0,75...+0,75 st.; runda 1 ta metoda: okna 90/180/270 st. |
| P1 plytka "prawie dobrze" na kolku | zamkniete rachunkiem po zmianie (bez dodatkowej geometrii): okno 1,5 st., strefa naprowadzenia 3,5 st., poza nia uniesienie 4,48 i przechyl 2,59 st. (krawedz +4,5) | R2-4 |
| P2 zatrzask pokrywki | 8 szczelin odciazajacych 1,0 x 12 (jezyk 12 x 12 x 1,5); K-66 sprawdza szczeliny; ryzyko "sila zatrzasku na 1. wydruku" zostaje; skala XY PETG (zanizenie otworu) dopisana do ryzyk | R2-3 K-66; sekcja 11 |
| P3 ALL kasuje pliki R58 | `wyczysc_wyniki(out, P)` pomija STL z `rdzenie_R58(P)` | R2-0, R2-8 |
| D1 wyjatek K-60 | tylko zrzut bez zadnego klucza R58 | R2-8; SPRAWDZ_iter16 K-60 ZAL |
| D2 scianki pionowe i kolnierz ze stalych | K-64 (d) ze siatki (scianki 3D), kolnierz z calego pierscienia | R2-3 |
| D3 "dno rowka pokrywki - obrysy" pozioma | scianka 3D 2,718 / 2,682 (do stozka C), do gniazd 3,55 / 3,08 | R2-3, plan 4.11 |
| D4 rowek pokrywki w scieciu 0,156 | bez zmiany geometrii (decyzja: informacyjne); dopisane do ryzyk / informacji dla drukarni ("nie wygladzac sciecia"; pasek moze zaniknac) | sekcja 11 |
| D5 kalibracja ramki dla JSON `okragla_ramkowa_*` | dopisane do ryzyk i co dalej: kalibracja moze uzyc ukladu kwadratowego po numerze (gniazda identyczne, ten sam srodek) - do zapisania w paczce programu | sekcje 11, 12 |
| D6 montaz A3144, dlugosc przewodow | dopisane do ryzyk: wyprowadzenia zaginane o 45 st. jak w kwadracie; kanal do naroza dluzszy o ok. 14 mm (29 zamiast 15) - wiazka dluzsza | sekcja 11 |
| D7 n8/n9 i plytka kwadratowa w nowej wkladce | n8/n9 policzone K-67 (leza na zebrze, odczyt 0); plytka kwadratowa - rachunek recenzenta (nie wchodzi w otwor, odczyt 0) dopisany do ryzyk | R2-4, sekcja 11 |
| D8 arkusz zamowienia, `kody_plytek.md`, `arkusz_wymiarow.md` | bez zmian (zlecenie: arkusze R59 nietkniete); przed zamowieniem potrzebny arkusz z 7 pozycjami R58 - krok koordynatora | sekcja 12 |

# RUNDA 1 (historia - stan oddany do recenzji runda 1, commit f429605)

## 0. Wynik [runda 1]

- `--etap R58 --iter 4` (generator koncowy): 19 ZAL, 0 N/D, 0 NIE (B 0 / P 0 / D 0); 1744 sondy, 0 niezgodnych, 0 sond blizej niz 0,1 od sciany; 25 s.
- `--etap R58_SPRAWDZ --iter 3` na plikach oddanych (lista nizej): 19 ZAL, 0 NIE.
- Powtarzalnosc: `--etap R58` w czystej kopii folderu (`--out wyniki_powt`: tylko 4 JSON R59 i 3 STL odniesienia) - 10 STL i 2 JSON bajtowo = pliki oddane (12 z 12, dwa razy: przebiegi 7 i 11). Wyjatek jak przy wkladce kwadratowej: w 1 z 4 przebiegow z koncowym zapisem (przebieg 9) `ramka_wkladka_okragla_v2.stl` wyszla w wariancie z jednym wierzcholkiem przesunietym o 0,00085 mm (objetosc rozna o 1e-9 cm3, gabaryt identyczny, wszystkie K = ZAL) - patrz 6 i 10.
- `--etap SPRAWDZ --iter 15` (stare pliki, generator koncowy): 58 ZAL, 5 N/D, 0 NIE (B 0 / P 0 / D 0), 2509 sond, 0 niezgodnych. Wyniki K, wartosci zmierzone i wszystkie sondy identyczne z `SPRAWDZ_iter12` (stan R59); jedyna roznica: dopisek w K-60 o zrzucie parametrow (10, odstepstwo 3). 5 x N/D jak dotad: K-19, K-21, K-48, K-52 (uchylone R50) i K-59 (recenzent).
- 25 starych plikow bez zmian: 21 STL + 4 JSON = `Ramki_pakiet/SHA256SUMS_2026-11-16_R59.txt` na MSI (21 STL w `<MSI>\kod\qc\Ramki\wyniki_v2\stl`, 4 JSON w `Ramki/wyniki_v2/json` tego worktree) i na PC po wszystkich przebiegach: 25 z 25 (sekcja 8).
- Plan <-> JSON (`porownaj_plan_z_json`): 0 roznic (po dopisaniu 14 kluczy do tabel 3.1, 3.4, 3.6); walidator kluczy R14: 301 kluczy (287 + 14), LICZONE max roznica 0,0000.

Pliki oddane (STL w `Ramki/wyniki_v2/stl/` tego worktree - nie w gicie; lista `wyniki_v2/raport/sha256_stl_po_R58.txt`; gabaryt w orientacji druku z siatki STL):

| Plik | SHA-256 | Objetosc [cm3] | Gabaryt X x Y x Z [mm] | Szt. / material (`quantities_r58`, `materials_r58`) |
|---|---|---|---|---|
| `ramka_plytka_okragla_ramkowa_wieczorna_v2.stl` (bazowy) | 18089783cd0ad01532b9b4d5e3ffcea6b45a4e8fa5f3cf100686718e44b6789e | 48,90 | 100,000 x 100,000 x 8,000 | - (wzorzec) |
| `ramka_plytka_okragla_ramkowa_wieczorna_n1_v2.stl` | f50c60de374d73e0c90f2163d7c7723fef6b912bc9a02e23dde3cf5c0f13d674 | 48,91 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_plytka_okragla_ramkowa_wieczorna_n2_v2.stl` | 34c91cba851b580a61688a7a2669c05f62849bd6ad45dff6ad19ec9ef880953b | 48,91 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_plytka_okragla_ramkowa_wieczorna_n3_v2.stl` | 6b8ceabc7d232c390a9c8b3438b2bd0621e0035e38b7db5a53b9eaef697301a6 | 48,91 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_plytka_okragla_ramkowa_poranna_v2.stl` (bazowy) | 44d67d1980a96708178a4c4fb29827b663f4790e7ef903f96c6d7de208538fce | 49,19 | 100,000 x 100,000 x 8,000 | - (wzorzec) |
| `ramka_plytka_okragla_ramkowa_poranna_n4_v2.stl` | 7f80acf3c8ba03a3f53409232f066fd8ca9736d26d317ee445991d2bed24e022 | 49,20 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_plytka_okragla_ramkowa_poranna_n5_v2.stl` | f6e24d4991920dded47044800ea83b5c7ae6377f6802b3132fec499139347f39 | 49,20 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_plytka_okragla_ramkowa_poranna_n6_v2.stl` | 3c78322049b49d2c849324af66d2525949b25430d0a933e2c3b8cc6814204b53 | 49,20 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_wkladka_okragla_v2.stl` | 0ca13cd723c2e3f3261ce01d3f9f6e460198f2f52ad72b0f62b7f0e2083e7e0f | 22,42 | 130,000 x 148,400 x 10,100 | 3 / PA12 drukarnia |
| `ramka_pokrywka_okragla_v2.stl` | 86e9976b6e38b60579d37088c79eede4fe1cf2b2f7ebfb21467feae7183642b1 | 25,26 | 103,600 x 103,600 x 20,000 | 4 / PETG FDM (wlasny) |
| `json/uklad_gniazd_okragla_ramkowa_wieczorna.json` | 16c4544b70ccd4c5f5ca6124d0093703cd5588768083f3196065e199c8b61e21 | - | - | - |
| `json/uklad_gniazd_okragla_ramkowa_poranna.json` | 20fce19e53ca10795cf397e9ba0381ff5c54941d6b45d054056875a0a324a277 | - | - | - |

Orientacja druku: plytki gniazdami do gory, spod plaski na Z = 0 (kieszenie i rowek klucza otwarte od spodu); wkladka spodem w dol, lezy na koncach kolkow ustalajacych (jak kwadratowa); pokrywka wierzchem w dol. Komplet do drukarni (7 pozycji x ilosci): 6 plytek x 48,91 / 49,20 + 3 wkladki x 22,42 = 361,60 cm3 -> 325...579 zl (stawka 0,90...1,60 zl/cm3, czesci biale bez mnoznikow); druk wlasny: 4 pokrywki x 25,26 = 101,05 cm3 PETG. Arkusz zamowienia R59 nie zawiera tych pozycji (odstepstwo 2).

Zrodla (stan koncowy): `ramka_generator.py` fe6cd09507e82f445a20fd3dc2f3a39bb8c5a2c0661ecf245db9a6d1f65ab99a (bylo d3b56f63be52..., diff +1370 / -34 linii), `parametry.json` 2686c881ceb1d22942b13112ebb6cbabb38b9d8e14d9e011436cdf3c6a8ab8b0 (bylo 8434aafe1584..., +26 / -4), `plan_ramki_v2.md` 296200b126f66e4a4abee0cacb16d41d0eac3d19dd4197c7cae486ce29222d9f (bylo 5e7379a688ee..., +60 / -8; plan czyta generator tylko w `porownaj_plan_z_json` - przebiegi #1-#4 szly z planem sprzed R58, #5-#13 z wersja 7b48089a... (rozni sie od koncowej jednym zdaniem w 4.1b); wynik porownania za kazdym razem: 0 roznic), `protokol_weryfikacji_v2.md` b5341ae3245edf150d3bd4c082c44898d8f2fd59fd709ff246f005f01b783d2e (bylo da33c0b22dd7..., +20 / -5).

## 1. Decyzje wlasciciela (19.11.2026) i ich odczyt [runda 1]

1. Pelny komplet: plytki okragle z magnesami i rowkiem pokrywki + okragla wkladka + okragla pokrywka; korpus i blat BEZ ZMIAN -> nowe typy plytek `okragla_ramkowa_wieczorna` / `okragla_ramkowa_poranna`, nowe czesci `wkladka_okragla`, `pokrywka_okragla`; obrys zewnetrzny wkladki = kwadratowa (blat bez zmian).
2. Numery jak kwadratowe: n1-n3 wieczorne, n4-n6 poranne; ramka czyta 3 magnesy A/B/C, program ramki bez zmian. Dzisiejsze okragle n8/n9 zostaja plytkami testowymi skanera - ich pliki nie byly ruszane (SHA w sekcji 8).
3. Srednica 100 zostaje (pole skanowania niezmierzone - ryzyko przyjete przez wlasciciela).

Kody kompletu (bit = magnes w kieszeni A/B/C na r 45 = dolek kodu; bit D = 0, dolek D tylko w pliku bazowym):

| n | typ | magnesy (kieszenie z magnesem) | dolki | pozycje dolkow (`code_dimples_round`) | cyfra (`number_pos_round`) |
|---|---|---|---|---|---|
| 1 | wieczorna | A | A | A (-4,5; -43,5), B (-1,5; -43,5), C (1,5; -43,5) | (35; -26,5) |
| 2 | wieczorna | B | B | j.w. | j.w. |
| 3 | wieczorna | A + B | A + B | j.w. | j.w. |
| 4 | poranna | C | C | A (36,5; 18,5), B (36,5; 21,5), C (43; 6) | (-44; 5,5) |
| 5 | poranna | A + C | A + C | j.w. | j.w. |
| 6 | poranna | B + C | B + C | j.w. | j.w. |

Osie kieszeni magnesow plytki i kieszeni Halla wkladki: A (-31,82; -31,82), B (-31,82; 31,82), C (31,82; 31,82) (promien 45 na przekatnych; kwadrat ma je w rogach (+-42, +-42)). Klucz: runda 1 kolek o3 na osi D (31,82; -31,82); runda 2 zebro na osi D przy scieciu (R2-1). Magnes jak w kwadracie: ten sam biegun w dol (instrukcja w `kody_plytek.md`).

## 2. `parametry.json` - nowe klucze (wszystkie status ZALOZENIE, zrodlo R58, opis po polsku z rachunkiem scianek) [runda 1]

| Klucz | Sekcja | Wartosc | Znaczenie |
|---|---|---|---|
| `round_magnet_r` | plytka | 45 | promien osi kieszeni magnesow A/B/C (plytka), kieszeni Halla A/B/C i kolka klucza D (wkladka); osie na przekatnych, D = `round_flat_angle` |
| `round_key_slot_w` | plytka | 3.6 | szerokosc rowka klucza od spodu plytki |
| `round_key_slot_r0` | plytka | 43 | promien plaskiego konca wewnetrznego rowka klucza |
| `round_key_slot_h` | plytka | 2.5 | wysokosc rowka klucza od spodu |
| `plate_numbers_round_frame` | plytka | {"wieczorna": [1, 2, 3], "poranna": [4, 5, 6]} | numery plytek okraglych ramkowych |
| `round_cover_snap_angles` | pokrywka | [25, 155, 205, 335] | katy garbow pokrywki okraglej |
| `round_insert_clearance` | blat_rama_wkladka | 0.4 | luz promieniowy plytki okraglej we wkladce (otwor 100,8, sciecie 49,756) |
| `round_insert_ledge_r` | blat_rama_wkladka | 47 | promien wewnetrzny wystepu wkladki |
| `round_insert_shelf` | blat_rama_wkladka | 10 | bok 4 polek kwadratowych wkladki |
| `round_key_pin_d` | blat_rama_wkladka | 3.0 | kolek klucza |
| `round_key_pin_h` | blat_rama_wkladka | 2.0 | wysokosc kolka nad polka |
| `round_key_pin_chamfer` | blat_rama_wkladka | 0.5 | faza wierzcholka kolka |
| `quantities_r58` | sterowanie | n1...n6 po 1, wkladka okragla 3, pokrywka okragla 4 | ilosci kompletu (osobno od `quantities`) |
| `materials_r58` | sterowanie | plytki i wkladka "PA12 drukarnia", pokrywka "PETG FDM (wlasny)" (w JSON ta sama tresc co w `materials`, z polska litera) | materialy kompletu |

Bez zmian wartosci: wszystkie 287 dotychczasowe klucze (w tym `quantities`, `materials`, `plate_numbers_round`, `code_dimples_round`, `number_pos_round`). Uzyte bez nowego klucza: `magnet_pocket_d/depth`, `cover_groove_w/depth/z`, `cover_clearance`, `cover_skirt_t`, `cover_inner_h`, `cover_top_t`, `cover_skirt_below`, `cover_snap_bump/hgt/r/w/z`, `cover_finger_w/h`, `insert_*`, `hall_*`, `wire_rabbet*`, `tab_*`, `finger_cut_w`.

## 3. `ramka_generator.py` - zmiany (kazda z powodem) [runda 1]

| # | Miejsce | Zmiana | Powod |
|---|---|---|---|
| 1 | naglowek, `main` | tryby `--etap R58` (buduje i sprawdza tylko 10 STL + 2 JSON) i `--etap R58_SPRAWDZ` (tylko sprawdza); nowa `main_R58`: bez `wyczysc_wyniki` i bez etapow A-C; raport `raport_wykonawcy_R58_iter<n>.md` przez istniejacy `zapisz_raport` (+ sekcja 7: ilosci kompletu) | zlecenie: nie przebudowywac i nie nadpisywac 25 plikow R59 (wkladka kwadratowa nie odtwarza sie bajtowo) |
| 2 | `WYMAGANE_KLUCZE`, `KLUCZE_R58` | 14 nowych kluczy dopisanych do walidatora R14 | R14: brak / nieznany klucz = blad |
| 3 | `OBJ_ORIENT` | plytka okragla ramkowa wieczorna 49, poranna 49, wkladka okragla 22, pokrywka okragla 25 (z siatek: 48,90 / 49,19 / 22,42 / 25,26) | K-04b |
| 4 | `TYPY_PLYTEK_R58`, `typ_bazowy`, `plytka_ramkowa`, `osie_okragle`, `NAROZA_CCW` | osobna krotka typow R58 (petle etapow A-C po `TYPY_PLYTEK` ich nie widza); osie A-D liczone z `round_magnet_r` i `round_flat_angle` co cwierc obrotu | etapy A-C i `--etap SPRAWDZ` bez zmian; zadnych liczb w kodzie |
| 5 | `uklad_pochodne`, `numery_plytek`, `wczytaj_uklad` | galaz ramkowa: `magnet_pockets` (3, z `angle_deg`), `cover_groove`, `key_slot`; numery z `plate_numbers_round_frame`; `wczytaj_uklad(..., opis_odczytu)` (tekst w dzienniku przy odczycie odniesien) | JSON wg zlecenia; uklady R59 czytane tylko do porownan |
| 6 | `zbuduj_plytke` | dla JSON z `cover_groove` / `key_slot`: pierscien tnacy rowka pokrywki (R + 0,2 ... R - 0,8, te same katy wierzcholkow co walec) i bryla rowka klucza (konce poza plytka odsuniete od plaszczyzn bryly sciecia); kieszenie magnesow z istniejacej petli `magnet_pockets`; bryly dopisane na koncu listy tnacej | plytki okragle R57/R59 (bez tych pol) buduja sie identycznie |
| 7 | `zbuduj_pokrywke_okragla`, `wymiary_pokrywki_okraglej`, `przekroj_garbu`, `bm_profil_po_luku` | kubek + 4 garby wyciagniete po luku o stalym przekroju + wyciecia palcowe; przekroj garbu = konstrukcja z `zbuduj_pokrywke` (kopia; `zbuduj_pokrywke` bez zmian) | 4.2a |
| 8 | `zbuduj_wkladke_okragla`, `otwor_wkladki_okraglej`, `kontur_polek_okraglych`, `_wkl_obrys`, `_wkl_dodatnie_wspolne`, `_wkl_tnace_wspolne` | wkladka okragla; obrys, uszy, kolki, strzalki, rowek kablowy, kanaly pod uszami i magnesy - kopie logiki `zbuduj_wkladke` (ktora zostala bez zmian) | 4.6a; obrys zgodny z kwadratowa (K-65 i) |
| 9 | `M_druk` | `pokrywka_okragla` jak `pokrywka`, `wkladka_okragla` jak `wkladka` | orientacja druku |
| 10 | `stl_kanoniczny`, `eksportuj_stl` | parametr `zero_dodatnie` (domyslnie False): -0,0 zapisywane jako +0,0; wlaczony tylko w `etap_R58` | znak zera w normalnych eksportera zmienia sie miedzy przebiegami (`do_v3.md` #9); pliki etapow A-C zapisywane jak dotad |
| 11 | `sprawdz_plytke` (K-09, K-13), `sprawdz_scianki_naroznikow` (K-16), `sprawdz_okragla` (K-61 b, K-63) | K-09: kontrola odwrotna dawnych rogow tylko na kwadracie (okragla R57 miala liste pusta - bez zmian); K-13: gdy w obszarze cyfry sa tylko wierzcholki cech od spodu (Z < -0,02: koniec rowka klucza), wysokosc z promieni z gory; K-16: opis dla ramkowej; K-61 (b) dla ramkowej na Z -7,5 promieniami odsunietymi o +-4,9; K-63 pomijane dla ramkowej | rowek klucza w osi sciecia; dla plikow R57/R59 wyniki identyczne (SPRAWDZ_iter15 = iter12) |
| 12 | `sprawdz_wkladke`, `SONDY_K29`, `SONDY_K30` | listy sond K-29 i K-30 przeniesione do stalych modulu (bez zmian tresci - porownane po wczytaniu: rowne) | te same sondy dla wkladki okraglej (K-65 i) |
| 13 | nowy blok (5a): `sprawdz_ramkowa` (K-64), `sprawdz_wkladke_okragla` (K-65), `sprawdz_pokrywke_okragla` (K-66), `sprawdz_pasowania_R58` (K-67) + pomocnicze (`trafienia`, `srodek_wneki`, `srodek_bryly`, `mapa_promieni`, `porownaj_mapy`, `punkty_kola`, `otwory_o3`) | sprawdzenia na STL wczytanych z powrotem; rzuty kontrolne od spodu i z gory | wymaganie 3 zlecenia |
| 14 | `etap_R58`, `odstepstwa_informacyjne_R58`, `DZIENNIK['ilosci_r58']`, `zapisz_raport` (opcjonalny `dodatek`) | przebieg R58; kontrola `quantities_r58` / `materials_r58` (dokladnie 8 czesci do zamowienia); rejestr odstepstw (7 wpisow) | |
| 15 | `zrzut_parametrow_zgodny`, `sprawdz_K60` | zrzut `parametry.json` w `arkusz_wymiarow.md` sprzed R58 zgodny, gdy rozni sie TYLKO brakiem kluczy `KLUCZE_R58`; uwaga w wyniku K-60 | arkusze R59 bez zmian (zlecenie) - bez tego `--etap SPRAWDZ` dawalby K-60 = NIE (P) |

## 4. `plan_ramki_v2.md` - edycje [runda 1]

| Miejsce | Zmiana |
|---|---|
| wstep | rejestr R1...R59 (bez "R58 zarezerwowany") |
| D5, D8, D11, D12 | dopiski [R58]: wkladka okragla (otwor, wystep, polki, kieszenie Halla w osiach r 45, kolek klucza), pokrywka okragla (garby po luku, rowek na calym obwodzie), numery n1-n6 okraglych ramkowych (kod, magnesy na r 45, n8/n9 testowe; ten sam numer co kwadrat), wkladka okragla = kwadratowa w obrysie, uszach, kolkach, magnesach, rowku |
| 3.1, 3.4, 3.6 | 14 wierszy nowych kluczy (porownanie plan <-> JSON: 0 roznic) |
| 4.1a | funkcja: do ramki sluzy 4.1b (bylo "na ramce dopiero po nowej wkladce i pokrywce (R58, po tescie)") |
| nowa 4.1b | plytka okragla ramkowa: identycznosc z 4.1a, kieszenie, rowek pokrywki, rowek klucza, numery, obrys cyfry, pliki i JSON, objetosci, sprawdzenia |
| nowa 4.2a | pokrywka okragla |
| nowa 4.6a | wkladka okragla |
| 4.11 | 4 wiersze: plytka okragla ramkowa, plytka we wkladce okraglej, wkladka okragla, pokrywka okragla |
| 12.1 | pozycja 17: pliki R58 i tryb `--etap R58` |
| 13 | naglowek R1...R59; wiersz R58 (przed R59); w wierszu R59 "(Numer R58 jest zarezerwowany ... bez wpisu.)" -> "(... wpis R58 z 19.11.2026 wyzej.)" |
| 14 | punkt 29 |

## 5. `protokol_weryfikacji_v2.md` - edycje [runda 1]

| Miejsce | Zmiana |
|---|---|
| tabela 1 | 4 wiersze R58 (gabaryt, objetosc orientacyjna 49 / 49 / 25 / 22 z siatek 48,9 / 49,2 / 25,3 / 22,4, orientacja = jak plytka okragla / pokrywka / wkladka, etap R58) |
| 2 | sprawdzenia ogolne K-01...K-04b takze dla 10 plikow R58 (`--etap R58`) |
| nowa 3b | opis kompletu, ukladow i osi; K-64 (plytka ramkowa), K-65 (wkladka okragla), K-66 (pokrywka okragla), K-67 (pasowania) z metodami, sondami i tolerancjami |
| K-61 | uwaga [R58]: (b) na Z -7,5 promieniami rownoleglymi odsunietymi o +-4,9 |
| K-63 | nie dotyczy plytek okraglych ramkowych (K-64) |
| K-59 | [R58]: czysta kopia odtwarza 10 STL + 2 JSON (zapis +0,0); 21 STL i 4 JSON = SHA256SUMS R59 |
| K-60 | [R58]: zrzut sprzed R58 zgodny, gdy brakuje tylko 14 kluczy R58; kazda inna roznica = NIE |

## 6. Przebiegi (PC, konto `<konto-PC>`, katalog `<PC-katalog>\r58\Ramki`, Blender 5.2.3 LTS, jeden proces naraz, wolny RAM 17,3 GB; logi `<PC-katalog>\r58\Ramki\_r58\*.log`) [runda 1]

| # | Polecenie (po `--`) | Generator (SHA) | ZAL / N/D / NIE | Uwagi |
|---|---|---|---|---|
| 1 | `--etap R58 --iter 1` | 9687304e806... | 17 / 0 / 2 | K-13 (B): plik bazowy wieczorny - w obszarze cyfry jedyne wierzcholki to koniec rowka klucza (Z -5,5), wiec "max Z wierzcholkow" = -5,5 zamiast 0 (blad metody, nie geometrii); K-65 (B) (h): 46 wierzcholkow y = 52,4 w float32 (52,39999771) policzonych jako "y < 52,4" (tolerancja 1e-6). Obie metody poprawione (sekcja 3 #11, #13) |
| 2 | `--etap R58 --iter 2` | ea3fbfee442... | 19 / 0 / 0 | wkladka okragla: SHA inna niz w #1 (3 normalne, tylko znak zera) |
| 3 | `--etap SPRAWDZ --iter 13` | ea3fbfee442... | 58 / 5 / 0 | stare pliki |
| 4 | `--etap R58 --iter 1 --out wyniki_powt` | ea3fbfee442... | 19 / 0 / 0 | czysta kopia: 9 STL + 2 JSON = #2, wkladka rozna (znak zera) -> dodany zapis +0,0 (sekcja 3 #10); raport nadpisany przez #7 i #11 |
| 5 | `--etap R58 --iter 3` | fa5799e438e... | 19 / 0 / 0 | z zapisem +0,0: wszystkie 10 STL maja nowe SHA (wczesniej zawieraly -0,0) |
| 6 | `--etap R58_SPRAWDZ --iter 1` | fa5799e438e... | 19 / 0 / 0 | |
| 7 | `--etap R58 --iter 1 --out wyniki_powt` (czysta kopia) | fa5799e438e... | 19 / 0 / 0 | 12 z 12 bajtowo = #5 |
| 8 | `--etap SPRAWDZ --iter 14` | fa5799e438e... | 58 / 5 / 0 | |
| 9 | `--etap R58 --iter 4` | fe6cd09507e... (koncowy; od #5 tylko teksty rejestru i raportu) | 19 / 0 / 0 | 11 plikow = #5; wkladka okragla 9187827b... (wariant: 1 wierzcholek o 0,00085 mm, 5 trojkatow inaczej; objetosc 22,419780 w obu, roznica 1e-9 cm3; gabaryt identyczny) |
| 10 | `--etap R58_SPRAWDZ --iter 2` | fe6cd09507e... | 19 / 0 / 0 | na plikach #9 (z wariantem wkladki) |
| 11 | `--etap R58 --iter 1 --out wyniki_powt` (czysta kopia) | fe6cd09507e... | 19 / 0 / 0 | 12 z 12 bajtowo = #5 (wkladka 0ca13cd7...); raport: `wyniki_v2/raport/raport_wykonawcy_R58powt_iter1.md` |
| 12 | `--etap SPRAWDZ --iter 15` | fe6cd09507e... | 58 / 5 / 0 | STAN KONCOWY starych plikow |
| 13 | wkladka 0ca13cd7... (z #11) wstawiona do `wyniki_v2/stl` na PC, wariant #9 odlozony jako `_r58\wkladka_okragla_iter4_wariant.stl`; `--etap R58_SPRAWDZ --iter 3` | fe6cd09507e... | 19 / 0 / 0 | STAN KONCOWY plikow R58 (= pliki w worktree) |

Raporty w gicie (`wyniki_v2/raport/`): `raport_wykonawcy_R58_iter1...iter4.md`, `raport_wykonawcy_R58_SPRAWDZ_iter1...iter3.md`, `raport_wykonawcy_R58powt_iter1.md` (przebieg #11, plik z `wyniki_powt`), `raport_wykonawcy_SPRAWDZ_iter13...iter15.md`, `sha256_stl_po_R58.txt` (format `sha256sum -c`, sciezki wzgledem `wyniki_v2/`). Rzuty kontrolne (31 PNG) tylko z przebiegow koncowych #9, #12, #13: od spodu plytek bazowych (kieszenie, rowek klucza), z gory i od spodu wkladki okraglej (polki, kieszenie Halla, kolek, kanaly), cyfry n1-n6; rzuty przebiegow #1, #2, #3, #5, #6, #8 nie zostaly sprowadzone (raporty tych przebiegow wskazuja pliki, ktorych w gicie nie ma).

## 7. Wyniki K (`raport_wykonawcy_R58_iter4.md`; te same wartosci w `R58_SPRAWDZ_iter3` na plikach oddanych) [runda 1]

| K | Wynik | Najwazniejsze wartosci zmierzone |
|---|---|---|
| K-01 | ZAL | 10 STL, 5164...25518 trojkatow, bez NaN |
| K-02 | ZAL | plytki 100 x 100 x 8 / 8,6 (X, Y +-50,000); wkladka 130 x 148,4 x 10,1; pokrywka 103,6 x 103,6 x 20 |
| K-03 | ZAL | 0 / 0 / 0 we wszystkich 10 (0 trojkatow o polu < 1e-6) |
| K-04 | ZAL | 1 skladowa w kazdym |
| K-04b | ZAL | 48,90...49,20 (orient. 49), 22,42 (22), 25,26 (25) |
| K-05 | ZAL | 18/1 i 23/1; max promien 45,927 / 46,412; scianka 3,000; (h) sockets = kwadrat: tak / tak |
| K-06, K-07, K-08 | ZAL | 90/90 i 115/115; 12/12; 10/10 we wszystkich 8 plytkach |
| K-09 | ZAL | 12/12 (znaczniki R59) |
| K-11 | ZAL | bazowe A+B+C+D; n1 A, n2 B, n3 A+B, n4 C, n5 A+C, n6 B+C |
| K-13 | ZAL | bazowe 0,000; warianty 0,600 |
| K-16 | ZAL | jak plytki okragle R59 (gniazdo-krawedz 4,07 / 3,59; stozek-krawedz 3,07 / 3,02; znacznik-gniazdo 3,19 / 3,02) |
| K-61 | ZAL | promien 49,996...50,000; sciecie 49,356 (Z -4 w osi; Z -7,5 promieniami +-4,9); glebokosc 0,644; sciecie-obrysy 4,59 / 4,81 |
| K-62 | ZAL | jak plytki okragle R59; bity = n |
| K-64 | ZAL | kieszenie: srodek (+-31,820; +-31,820), o 5,200 x 5,194, gl. 2,200, scianka do krawedzi 2,402; rowek pokrywki 0,800 (16 kierunkow), wysokosc 1,000, srodek Z -2,000, w scieciu dno r 49,200 (0,156 w cieciwie); rowek klucza 3,600 x 2,500 od r 43,000 (os 0,000); scianki (wieczorna / poranna): kieszen-otwor 9,81 / 7,48, sufit kieszeni-dno gniazda 1,80, sufit rowka klucza-dno gniazda 1,50, rowek klucza-otwor 9,73 / 8,11, dno rowka pokrywki-obrysy na Z -1,5 3,52 (stozek C) / 3,19 (gniazdo id 22), stozek-kieszen w pionie 2,80; sockets = kwadrat; cyfra n1-n6: do gniazda 3,28...3,47, naroznik r <= 46,88; mapa wierzchu = plytka okragla tego typu: 128 191 / 127 067 punktow, 0 niezgodnych trafien, max dz 0,0000 |
| K-65 | ZAL | otwor r 50,397...50,400 (o 100,795); sciecie 49,756 / 49,756 / 49,756; wystep r 46,997...46,998; polka Z 2,500 (7 punktow); kieszenie Halla w osiach A/B/C (odchylka 0,000), 5,000 x 5,500; kolek klucza (31,820; -31,820) o 3,000 x 2,990, wierzch 4,500; scianka w osiach 2,003 / 2,001 / 2,001; dno po rowku 2,903; wyciecie 30,000; K-56: 0 wierzcholkow; zgodnosc z wkladka kwadratowa: K-29 20/20, K-30 7/7, mapy z gory / od spodu 37 028 punktow, 0 / 0 niezgodnych, max dz 0,0000 / 0,0000; kanaly A 390, B 185, C 185 punktow - 0 w bryle |
| K-66 | ZAL | o 100,593...100,600 / 103,593...103,600; wierzch 2,000; Z -20...0; garby 25/155/205/335 st.: wystep 0,700, srodek Z -18,000, wysokosc 0,800, przeglad co 1 st. = 4 sektory w zadanych katach; wyciecia 30,000 x 3,000 przod i tyl |
| K-67 | ZAL | 0 kolizji (17 par, skurcz 0,05); styk plytka-polka bez skurczu 1430-1431 par (czulosc); luz promieniowy 0,397...0,402 (8 kierunkow), na scieciu 0,400; spod plytki 2,500 = polka 2,500; os magnesu - os kieszeni Halla 0,000 (A, B, C); kolek w rowku 0,300 / 0,300, nad kolkiem 0,500; pokrywka-plytka 0,300; garby: zaglebienie 0,400, do dna rowka 0,403, dZ 0,000; kolnierz nad wkladka 0,500; plytka obrocona o 90 / 180 / 270 st.: 59 / 58 / 57 kolizji (nie wchodzi) |

Sprawdzenia etapow A-C nie wchodza do raportu R58 (sa w `SPRAWDZ_iter15`). K-58 (kody) dla kompletu R58 nie istnieje - tabela kodow w sekcji 1 (arkusz `kody_plytek.md` bez zmian).

## 8. Dowod: 25 plikow R59 bez zmian [runda 1]

Porownanie SHA-256 z `Ramki/Ramki_pakiet/SHA256SUMS_2026-11-16_R59.txt` (po nazwie pliku): przed praca (MSI), po wszystkich przebiegach na PC (`Get-FileHash`, `<PC-katalog>\r58\Ramki\wyniki_v2`) i na koniec na MSI - 25 z 25 za kazdym razem.

| Plik | SHA-256 (= SHA256SUMS R59) |
|---|---|
| ramka_blat_v2.stl | 8c48856eb9addee2b37cfa5a03e5686ab7670bd92b724e488ccc8d8dd3a4b418 |
| ramka_korpus_P_v2.stl | aadb91c9364cf39f1f4062d328616aa518e474b957315ed4a941de4f935ab2b7 |
| ramka_korpus_W_v2.stl | bd55871c88cf2604c1c8efa5035148ba39c3803a0788015cc35548e8e9afff9a |
| ramka_plytka_okragla_poranna_n9_v2.stl | f9444e6f14e37d9d0bcc8ae84cfec5249146bce20420c53a86a73965727fd4c4 |
| ramka_plytka_okragla_poranna_v2.stl | e35835d7618e6665fdda84cbe2d65a3c7b46d7f9cef1e99141b42af2eb9e22c7 |
| ramka_plytka_okragla_wieczorna_n8_v2.stl | d5591f652ea1b6b23825abb5ad05ac12b78d17f6abb52946bd1a010ef5e4ff54 |
| ramka_plytka_okragla_wieczorna_v2.stl | aad8033e6c1d1f34b43825861d18e82b45599a76ebb453c294400a7713ebbd83 |
| ramka_plytka_poranna_n4_v2.stl | 20f15f2214f6c9a9baf2b4701e7f99bfbc5f739b6379398294e9f931b8763237 |
| ramka_plytka_poranna_n5_v2.stl | a275775b9c9b5ddd015b68659f213505bdd28b9476cad5e13405bef2df5b64d1 |
| ramka_plytka_poranna_n6_v2.stl | c44be370c8b9ad2b70f9e486c3f6f9d2b227b91f2a6544bfe14bf7e66bd65b21 |
| ramka_plytka_poranna_v2.stl | a306032651bbdb0c77693aa27f6314e8c5ede874d1e99b1fa73e158a1a83bc9f |
| ramka_plytka_wieczorna_n1_v2.stl | 3b0db5452a0cd9533464772c10b67c05fa7a006fcdb3d140a74af275e79946f7 |
| ramka_plytka_wieczorna_n2_v2.stl | b87026134b25cf32a84a231b73d5c4eb9fde4dfeb5b16b627cf09ccc3f29c999 |
| ramka_plytka_wieczorna_n3_v2.stl | 59e615d596771c6c0351284c710e94e406a965afef423ffeae5cd18ffa2c4dd3 |
| ramka_plytka_wieczorna_v2.stl | 604ef8f2079184460c3e059edde4849e9feeefeab39a755c18d0079ea1e561a9 |
| ramka_podkladka_panelu_05_v2.stl | 4260d1f1957f32d101cae5da2cf4634e24239caf738592edd7007fc0728ec6b4 |
| ramka_podkladka_panelu_1_v2.stl | e79a805121499f8d65b7d23ef6d2ae255549b4f55579ded7061b8996b91c9b78 |
| ramka_podkladka_panelu_2_v2.stl | 9c47aea4fbc946c16dab3813561d936745b88afde6092542de1d67a21656d5b5 |
| ramka_pokrywka_v2.stl | ad23444483ac95733e92169af00e5271d8fc3b19a91854e8c8acddf06c8cd454 |
| ramka_tulejka_dc_v2.stl | b393256cd8cafdac6d125d6f9f25647c5f94840d1bc5eb87941b436f510bcc00 |
| ramka_wkladka_v2.stl | f4196fbc640450998634f50caa86051f89df2cbb2c218e317f5c2b193e3ef92b |
| uklad_gniazd_okragla_poranna.json | b943e6c5dd54a8b3b35974908a3910bd654062bb659284a649ee68679174268e |
| uklad_gniazd_okragla_wieczorna.json | c07791f4bb976be2ad5eddaaeefe011b2384ea71e3fabd25cf55da690eb14a33 |
| uklad_gniazd_poranna.json | 46e474b759c4b78b7975fc8c5580c9916a4cc64c6a88cd4711b2207e3978b98b |
| uklad_gniazd_wieczorna.json | 7ae07ba861950724cf68ce9de0b45f3a05436089df8f73b3b4fc07bf2cc05869 |

Dlaczego to trwale: tryb R58 nie wola `wyczysc_wyniki` ani budowy etapow A-C; uklady R59 czyta z `zapisuj=False`; nowe typy plytek nie sa w `TYPY_PLYTEK`; zmiany w funkcjach wspolnych dzialaja tylko dla JSON z polami R58 (`cover_groove`, `key_slot`) albo dla nowych nazw czesci, a `zero_dodatnie` jest domyslnie wylaczone - wiec takze przyszly przebieg ALL zbuduje pliki etapow A-C tak jak dotad (z zastrzezeniem znanej niepowtarzalnosci `ramka_wkladka_v2.stl`). Arkusze R59 (`arkusz_wymiarow.md`, `arkusz_zamowienia.*`, `kody_plytek.md`), rendery, `.blend`, README i `do_v3.md` nie byly zapisywane (git: brak zmian w `wyniki_v2/arkusze`, `render`, `ramka_v2.blend`, `README.md`, `do_v3.md`).

## 9. Liczby projektu - zrealizowane bez zmian [runda 1]

Wszystkie liczby koordynatora przyjete wprost: o100, kieszenie o5,2 x 2,2 w osiach na r 45, rowek 1,0 x 0,8 na Z -2 (przez sciecie, 0,156 w srodku cieciwy), rowek klucza 3,6 x 2,5 od r 43, otwor wkladki 100,8 ze scieciem 49,756, faza 1 x 45 st. na calym obrysie otworu, wystep r 47, polki 10 x 10, kieszenie Halla 5,0 x 5,5, kanaly 2,5 x 1,0 / 2,5 x 1,5 (t_h = 50,4 - 45, t_k = zw x sqrt(2) - 45 + 5 x NADDATEK), kolek o3 x 2 z faza 0,5, wyciecie palcowe 30 (koniec bryly: odstepstwo 1 - bryla wyniku ta sama), scianka w osiach 2,0, dno 2,9, pokrywka 100,6 / 103,6 x 20, garby 25 / 155 / 205 / 335 st. Zadna scianka < 1,5, zadna kolizja, zadne sprawdzenie nie wymagalo zmiany wymiaru.

## 10. Odstepstwa (rejestr raportu R58_iter4, 7 wpisow) [runda 1]

1. Wyciecie palcowe wkladki okraglej: koniec bryly tnacej z parametrow -sqrt(47^2 - 15^2) + 5 x 0,1 = -44,042 zamiast "-44,0" ze zlecenia; za okregiem wystepu jest tylko wolny otwor, wiec bryla wyniku identyczna; bez nowego klucza. Informacyjnie.
2. Ilosci i materialy w osobnych kluczach `quantities_r58` / `materials_r58`: dopisanie do `quantities` zmieniloby arkusz zamowienia R59 i K-57 starych plikow. Do decyzji koordynatora (wlaczenie do arkusza w przebiegu ALL).
3. K-60 przy `--etap SPRAWDZ`: zrzut `parametry.json` w `arkusz_wymiarow.md` sprzed R58 uznawany za zgodny, gdy brakuje w nim tylko 14 kluczy R58 (kazda inna roznica nadal NIE). Bez tego wymaganie "SPRAWDZ dalej 0 NIE" i "arkusze bez zmian" byly sprzeczne. Do zatwierdzenia przez koordynatora (protokol K-60 juz z dopiskiem); po przebiegu ALL zrzut bedzie pelny i tolerancja przestanie byc potrzebna.
4. Sprawdzenia plytki ramkowej: K-61 (b) na Z -7,5 promieniami odsunietymi o +-4,9 (w osi lezy rowek klucza), K-63 nie dotyczy (K-64), K-09 bez kontroli odwrotnej dawnych rogow. Zapisane w protokole.
5. Numery n1-n6 wspolne z plytkami kwadratowymi (decyzja wlasciciela); `kody_plytek.md` nie generowany na nowo - tabela kodow w sekcji 1. Program stanowiska nie odrozni dzis okraglej n1 od kwadratowej n1 (osobna paczka).
6. Pokrywka okragla bez klucza: mozna ja zalozyc w dowolnym obrocie; garb nad scieciem plytki nie zahacza (czubek r 49,60 > sciecie 49,356) - wtedy trzymaja 3 garby. K-67 sprawdza polozenie nominalne (wyciecia z przodu i z tylu).
7. Zapis STL kompletu R58 z +0,0 zamiast -0,0 (`stl_kanoniczny(zero_dodatnie=True)` tylko w trybie R58): usuwa niepowtarzalnosc znaku zera w normalnych; pliki etapow A-C zapisywane bez zmian. Normalizacja dla wszystkich plikow zostaje w v3 (`do_v3.md` #9).

Dodatkowo (nie w rejestrze generatora): `ramka_wkladka_okragla_v2.stl` - jak `ramka_wkladka_v2.stl` - nie zawsze odtwarza sie bajtowo nawet po zapisie +0,0: w 1 z 4 przebiegow (#9) boolean EXACT dal wierzcholek przesuniety o 0,00085 mm (na krawedzi otworu na wysokosci polki, Z 2,5) i inna triangulacje 5 trojkatow; objetosc 22,419780 cm3 w obu wariantach, gabaryt identyczny, wszystkie K = ZAL w obu (R58_SPRAWDZ_iter2 i iter3). Oddany jest wariant 0ca13cd7..., ktory powstal w 3 przebiegach (#5, #7, #11); przy pakowaniu brac ten plik (nie przebudowywac), jak przy wkladce kwadratowej. Wg K-59: roznica SHA przy objetosci +-0,001 i gabarycie +-0,01 = ZAL z uwaga D.

## 11. Ryzyka (stan po rundzie 2)

1. Pole skanowania niezmierzone (`scan_field_d` 100 DO_ZMIERZENIA, pomiar #12): plytka o100 = granica pola przy zalozeniu 100; jesli pole wyjdzie mniejsze, krawedz plytki i gniazda skrajne (promien obrysu 45,93 / 46,41) moga wypasc poza skan - ryzyko przyjete przez wlasciciela.
2. Sila zatrzasku pokrywki okraglej do sprawdzenia na pierwszym wydruku FDM (PETG): runda 2 - garb na jezyku 12 x 12 x 1,5 miedzy szczelinami odciazajacymi (P2 recenzji), zaglebienie 0,4; jesli za mocno / za slabo - zmiana `cover_snap_bump`, `round_cover_slit_h` albo katow, nowy wydruk 1 sztuki przed 4. PETG FDM zwykle zaniza otwor o 0,2-0,3 na srednicy (luz 0,3/strone moze spasc do ok. 0,15) - skala XY w slicerze jak przy tulejce (R55).
3. Program stanowiska nie zna jeszcze plytek okraglych n1-n6 (te same numery co kwadratowe; inne pozycje dolkow i magnesow): osobna paczka (modele `modele_plytek`, JSON z `magnet_pockets` / `key_slot`, rozroznienie ksztaltu).
4. Scianka ramy wkladki w osiach 2,0 (kwadratowa: 4,0) - zgodnie z zasada 4.8 (>= 1,5), ale wkladka jest sztywniejsza tylko dzieki wystepowi i polkom; MJF/SLS +-0,3 zostawia >= 1,4 w najgorszym razie lokalnie.
5. Rowek klucza (runda 2: do Z -3, wyzej niz dno gniazd): scianki 3D z siatki 2,68 (wieczorna, rynienka) / 6,36 (poranna); pod rowkiem pokrywki zostaje 0,5 w pasku 0,156 x 3,6 przy scieciu (tam rowek pokrywki ma 0,156 glebokosci i moze w druku zaniknac - D4 recenzji; informacja dla drukarni: sciecia nie wygladzac). Runda 1 (rowek do Z -5,5): po przekatnej 1,54.
6. Kieszenie magnesow 2,4 od krawedzi plytki (przy rowku pokrywki 1,6 w rzucie, rowek 3,3 wyzej) - wystarczajace wg 4.8; magnes wklejany od spodu.
7. Arkusz zamowienia, `kody_plytek.md`, `arkusz_wymiarow.md`, rendery i `.blend` nie zawieraja kompletu R58, dopoki koordynator nie zrobi przebiegu ALL z dolaczonymi czesciami (D8 recenzji; przebieg A/B/C/ALL nie kasuje juz plikow R58 - P3).
8. Klucz (runda 2): plytka lezy plasko tylko w oknie -0,75...+0,75 st.; w zlym obrocie lezy na zebrze z przechylem ok. 2,6 st. (krawedz +4,5) - wyraznie widoczne. Odczyt magnesow przy takim przechyle nie byl liczony; program ramki powinien ostrzegac, gdy numer nie pasuje do roli ramki (n1-n3 na P, n4-n6 na W) - paczka programu.
9. Kalibracja ramki (D5 recenzji): `stanowisko/ramka/kalibracja.py` pomija uklady z `shape` != "square" i `plate` spoza {wieczorna, poranna}, wiec JSON `okragla_ramkowa_*` nie dostanie kalibracji startowej. Poniewaz `sockets` = kwadrat tego typu, a srodek otworu wkladki okraglej = srodek kwadratowej (obrys identyczny, zmierzone), ramka moze uzyc kalibracji ukladu kwadratowego po numerze - do zapisania w paczce programu.
10. Montaz czujnikow (D6 recenzji): kanal wychodzi z naroza kieszeni Halla 5,0 x 5,5 po przekatnej; A3144 (obudowa ok. 4,1 x 3,0) obrocony o 45 st. sie nie zmiesci, wiec wyprowadzenia zagina sie o 45 st. przy obudowie - jak we wkladce kwadratowej; kanal do naroza jest dluzszy o ok. 14 mm (ok. 29 zamiast 15), wiec przewody wiazki dla wkladki okraglej sa dluzsze - do instrukcji budowy.
11. Inne plytki w nowej wkladce (D7 recenzji, informacyjnie): stare okragle n8/n9 mieszcza sie w otworze i leza na zebrze w kazdym obrocie (K-67: uniesienie 4,48, przechyl 2,59 st.), ramka czyta 0 (brak magnesow); plytka kwadratowa nie wchodzi w otwor (polprzekatna ok. 67 > 50,4), lezy na ramie, magnesy r 59,4 poza czujnikami r 45 - odczyt 0 (rachunek recenzenta, bez proby 3D); plytka ramkowa nie wchodzi w stara wkladke kwadratowa (o100 > 96,8).

## 12. Co dalej (koordynator, poza R58-A; stan po rundzie 2)

1. Recenzja rundy 2 (zmiana klucza, szczeliny pokrywki, nowy K-67; 10 STL, 2 JSON) - swieza subsesja.
2. Decyzja o odstepstwach 2, 3, 7 i o tym, czy tryb R58 ma zostac osobny, czy komplet wejdzie do etapow A/B (wtedy nowe arkusze, render, `.blend`, `kody_plytek.md` z n1-n6 okraglymi, K-58 i K-57 z `quantities_r58`).
3. Program stanowiska (plytki okragle n1-n6; kalibracja z ukladu kwadratowego po numerze - ryzyko 9; ostrzezenie o numerze niepasujacym do ramki - ryzyko 8), dokumenty dla wlasciciela (zamowienie z arkuszem 7 pozycji R58 - D8; budowa: zaginanie wyprowadzen A3144 i dluzsze przewody - ryzyko 10), pakiet i SHA256SUMS (wkladka: oddany wariant baf94bf8).
