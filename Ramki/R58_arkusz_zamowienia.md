# Arkusz zamowienia R58 - komplet okragly do ramki (19.11.2026)

Wygenerowany przez `narzedzia/arkusz_zamowienia_R58.py`. Objetosci, gabaryty (orientacja druku) i sumy SHA-256 z raportu generatora `raport_wykonawcy_R58_SPRAWDZ_iter5.md` (pomiar na plikach oddanych); ilosci i materialy z `parametry.json` -> `quantities_r58` / `materials_r58`. Ten sam arkusz w `R58_arkusz_zamowienia.csv` (separator ;, przecinek dziesietny).

Decyzje wlasciciela 19.11.2026: pelny komplet okragly (plytki + wkladka + pokrywka), numery n1-n3 wieczorne i n4-n6 poranne, srednica 100 mm (pole skanowania niezmierzone - ryzyko przyjete). Korpusy i blaty ramek bez zmian (pliki R59).

## A. Nowe pliki do drukarni (PA12, bialy naturalny, mat, bez wygladzania)

| Plik STL | Czesc | Szt. | Obj. [cm3] | Gabaryt X x Y x Z [mm] | Koszt [zl] | SHA-256 | Uwagi |
|---|---|---|---|---|---|---|---|
| `ramka_plytka_okragla_ramkowa_wieczorna_n1_v2.stl` | plytka okragla ramkowa wieczorna n1 | 1 | 48,91 | 100,0 x 100,0 x 8,6 | 44-78 | `84d361e2389bef12fd07278bf3e2e65fd170c83d4012f8fbbfa12b8ad172325f` | R58: lezy na ramce (3 kieszenie magnesow od spodu, rowek pokrywki na obwodzie, rowek klucza od spodu przy scieciu); sciecia orientacyjnego i rowkow nie wygladzac; nie pasuje do wkladki kwadratowej |
| `ramka_plytka_okragla_ramkowa_wieczorna_n2_v2.stl` | plytka okragla ramkowa wieczorna n2 | 1 | 48,91 | 100,0 x 100,0 x 8,6 | 44-78 | `7848aa2395638b338e4bd2e83473b1329c53c61500a7ec1ba5a63a8c5aaaaa94` | R58: lezy na ramce (3 kieszenie magnesow od spodu, rowek pokrywki na obwodzie, rowek klucza od spodu przy scieciu); sciecia orientacyjnego i rowkow nie wygladzac; nie pasuje do wkladki kwadratowej |
| `ramka_plytka_okragla_ramkowa_wieczorna_n3_v2.stl` | plytka okragla ramkowa wieczorna n3 | 1 | 48,91 | 100,0 x 100,0 x 8,6 | 44-78 | `1b8ac3d390870f0a4607b3289f50201ef28cf2049801ac853aaa1427735321aa` | R58: lezy na ramce (3 kieszenie magnesow od spodu, rowek pokrywki na obwodzie, rowek klucza od spodu przy scieciu); sciecia orientacyjnego i rowkow nie wygladzac; nie pasuje do wkladki kwadratowej |
| `ramka_plytka_okragla_ramkowa_poranna_n4_v2.stl` | plytka okragla ramkowa poranna n4 | 1 | 49,20 | 100,0 x 100,0 x 8,6 | 44-79 | `5d81f55b8b114ba9cf307bb4ba63e70083aa6570ab0bb646acef69b8cd6cceb5` | R58: lezy na ramce (3 kieszenie magnesow od spodu, rowek pokrywki na obwodzie, rowek klucza od spodu przy scieciu); sciecia orientacyjnego i rowkow nie wygladzac; nie pasuje do wkladki kwadratowej |
| `ramka_plytka_okragla_ramkowa_poranna_n5_v2.stl` | plytka okragla ramkowa poranna n5 | 1 | 49,20 | 100,0 x 100,0 x 8,6 | 44-79 | `64867b5b63a31db88715c9c9636c33015566bbe48af2c8f4a90330797f063381` | R58: lezy na ramce (3 kieszenie magnesow od spodu, rowek pokrywki na obwodzie, rowek klucza od spodu przy scieciu); sciecia orientacyjnego i rowkow nie wygladzac; nie pasuje do wkladki kwadratowej |
| `ramka_plytka_okragla_ramkowa_poranna_n6_v2.stl` | plytka okragla ramkowa poranna n6 | 1 | 49,20 | 100,0 x 100,0 x 8,6 | 44-79 | `7630a029157b2fc65144c5f6b32ad28c02048f0642855cc3d23c2570ea28991e` | R58: lezy na ramce (3 kieszenie magnesow od spodu, rowek pokrywki na obwodzie, rowek klucza od spodu przy scieciu); sciecia orientacyjnego i rowkow nie wygladzac; nie pasuje do wkladki kwadratowej |
| `ramka_wkladka_okragla_v2.stl` | wkladka okragla gniazda plytki | 3 | 22,45 | 130,0 x 148,4 x 10,5 | 61-108 | `287e001fddd655f9df91663d7fb7a8cf6a9b3aa89d8bc2e470bf50f59f8be6c5` | R58: zamiast ramka_wkladka_v2.stl; 2 do ramek + 1 zapas; scianka w osiach 2,0 mm - nie szlifowac |

Razem nowe pliki: 7 pozycji, 9 sztuk, 361,68 cm3, 326-579 zl (stawka 0,90-1,60 zl/cm3, czesci biale bez mnoznikow).

## B. Druk wlasny (PETG FDM, bez kosztu drukarni)

| Plik STL | Czesc | Szt. | Obj. [cm3] | Gabaryt X x Y x Z [mm] | SHA-256 | Uwagi |
|---|---|---|---|---|---|---|
| `ramka_pokrywka_okragla_v2.stl` | pokrywka okragla plytki | 4 | 25,06 | 103,6 x 103,6 x 20,0 | `f1a133cf19fda391bf749797c1a7e1480a8a0062b7d49eee2d248fd5c8d70889` | R58: druk wlasny wierzchem w dol; 8 szczelin 1 x 15 z otworem 2 mm przy zatrzaskach; najpierw 1 sztuka probna (sila zatrzasku), potem seria |

Male czesci druku wlasnego z pakietu R59 (tulejka DC, podkladki panelu) bez zmian.

## C. Czesci ramki bez zmian - pliki z pakietu R59 (sumy w `SHA256SUMS_2026-11-16_R59.txt`)

| Plik STL | Szt. | Obj. [cm3] | Gabaryt [mm] | Najtanszy [zl] | Pokazowy [zl] |
|---|---|---|---|---|---|
| `ramka_korpus_W_v2.stl` | 1 | 233,49 | 200,0 x 200,6 x 59,6 | 210-374 | 328-583 |
| `ramka_korpus_P_v2.stl` | 1 | 233,47 | 200,0 x 200,6 x 59,6 | 210-374 | 328-583 |
| `ramka_blat_v2.stl` | 2 | 72,52 | 200,0 x 200,0 x 14,0 | 131-232 | 204-362 |

## D. Pozycje pakietu R59, ktorych w wariancie okraglym NIE zamawiamy

| Plik STL | Szt. | Powod |
|---|---|---|
| `ramka_plytka_wieczorna_n1_v2.stl` | 1 | zastapiona plytka okragla ramkowa o tym samym numerze |
| `ramka_plytka_wieczorna_n2_v2.stl` | 1 | zastapiona plytka okragla ramkowa o tym samym numerze |
| `ramka_plytka_wieczorna_n3_v2.stl` | 1 | zastapiona plytka okragla ramkowa o tym samym numerze |
| `ramka_plytka_poranna_n4_v2.stl` | 1 | zastapiona plytka okragla ramkowa o tym samym numerze |
| `ramka_plytka_poranna_n5_v2.stl` | 1 | zastapiona plytka okragla ramkowa o tym samym numerze |
| `ramka_plytka_poranna_n6_v2.stl` | 1 | zastapiona plytka okragla ramkowa o tym samym numerze |
| `ramka_wkladka_v2.stl` | 3 | zastapiona przez `ramka_wkladka_okragla_v2.stl` |
| `ramka_pokrywka_v2.stl` | 4 | zastapiona przez `ramka_pokrywka_okragla_v2.stl` (druk wlasny) |

Plytki okragle n8 i n9 (bez kieszeni magnesow) zostaja plytkami testowymi tylko do skanera - zamowienie wedlug uznania; na ramce nie dzialaja (ramka czyta 0, a we wkladce okraglej leza krzywo na zebrze klucza).

## Sumy - drukarnia

| Zakres | Objetosc [cm3] | Najtanszy [zl] | Pokazowy [zl] |
|---|---|---|---|
| A. nowe pliki R58 (6 plytek + 3 wkladki) | 361,68 | 326-579 | 326-579 |
| C. korpus W + korpus P + 2 blaty (R59) | 612,00 | 551-979 | 859-1528 |
| **Komplet okragly A + C** | **973,68** | **876-1558** | **1185-2106** |
| dla porownania: pozycje D z drukarni (6 plytek kwadratowych + 3 wkladki) | 396,05 | 356-634 | 356-634 |

Wariant pokazowy: korpusy i blaty barwione na grafit i wygladzane (x 1,20 x 1,30); czesci biale bez mnoznikow.

## Czego wymagac od drukarni i co sprawdzic przy odbiorze

- Plytki: sciecia orientacyjnego, rowka na obwodzie i rowka od spodu nie wygladzac ani nie zalewac; orientacja druku gniazdami do gory.
- Plytka: 3 kieszenie od spodu - magnes 5 x 2 mm ma wejsc (kieszen 5,2 x 2,2); rowek klucza od spodu przy scieciu: szerokosc 3,6, wysokosc 5,0.
- Wkladka: plytka siada plasko tylko scieciem do sciecia - zebro klucza 3,0 wchodzi w rowek 3,6 od spodu plytki; w kazdym innym obrocie plytka lezy krzywo na zebrze (krawedz ok. 4,5 mm wyzej). Luz na srednicy 0,8.
- Wkladka: 3 kieszenie czujnikow 5,0 x 5,5 i kanaly przewodow od spodu maja byc drozne (odpylone).
- Zamawiac wylacznie pliki o sumach SHA-256 z tabel A i B.
