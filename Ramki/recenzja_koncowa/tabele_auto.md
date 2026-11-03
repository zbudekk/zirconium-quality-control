## Tabela A. Transformacje STL → złożenie (D3)

| STL | obiekt .blend | typ | przesunięcie (x, y, z) | max odległość wierzchołków | liczba wierzchołków/trójkątów zgodna |
|---|---|---|---|---|---|
| `ramka_blat_v2.stl` | blat | obrot_180_X | (0.0, 0.0, 63.6) | 1.1e-05 | tak |
| `ramka_korpus_P_v2.stl` | korpus_P | przesuniecie | (260.0, 0.0, 0.0) | 0.0e+00 | tak |
| `ramka_korpus_W_v2.stl` | korpus_W | przesuniecie | (0.0, 0.0, 0.0) | 0.0e+00 | tak |
| `ramka_plytka_poranna_n4_v2.stl` | plytka_poranna_n4 | przesuniecie | (55.0, -260.0, 0.0) | 0.0e+00 | tak |
| `ramka_plytka_poranna_n5_v2.stl` | plytka_poranna_n5 | przesuniecie | (165.0, -260.0, 0.0) | 0.0e+00 | tak |
| `ramka_plytka_poranna_n6_v2.stl` | plytka_poranna_n6 | przesuniecie | (275.0, -260.0, 0.0) | 0.0e+00 | tak |
| `ramka_plytka_poranna_v2.stl` | plytka_poranna | przesuniecie | (-55.0, -260.0, 0.0) | 0.0e+00 | tak |
| `ramka_plytka_wieczorna_n1_v2.stl` | plytka_wieczorna_n1 | przesuniecie | (0.0, 0.0, 66.1) | 8.0e-06 | tak |
| `ramka_plytka_wieczorna_n2_v2.stl` | plytka_wieczorna_n2 | przesuniecie | (-275.0, -260.0, 0.0) | 0.0e+00 | tak |
| `ramka_plytka_wieczorna_n3_v2.stl` | plytka_wieczorna_n3 | przesuniecie | (-165.0, -260.0, 0.0) | 0.0e+00 | tak |
| `ramka_plytka_wieczorna_v2.stl` | plytka_wieczorna | przesuniecie | (-385.0, -260.0, 0.0) | 0.0e+00 | tak |
| `ramka_podkladka_panelu_05_v2.stl` | podkladka_panelu_05 | przesuniecie | (-18.0, -480.0, 0.0) | 0.0e+00 | tak |
| `ramka_podkladka_panelu_1_v2.stl` | podkladka_panelu_1 | przesuniecie | (0.0, -480.0, 0.0) | 0.0e+00 | tak |
| `ramka_podkladka_panelu_2_v2.stl` | podkladka_panelu_2 | przesuniecie | (18.0, -480.0, 0.0) | 0.0e+00 | tak |
| `ramka_pokrywka_v2.stl` | pokrywka | obrot_180_X | (0.0, 0.0, 90.1) | 8.0e-06 | tak |
| `ramka_tulejka_dc_v2.stl` | tulejka_dc | obrot_+90_Y | (-43.0, 89.0, 30.0) | 0.0e+00 | tak |
| `ramka_wkladka_v2.stl` | wkladka | przesuniecie | (0.0, 0.0, 60.1) | 0.0e+00 | tak |

| część | sprawdzenie D3/D4 | bbox min | bbox max | ok |
|---|---|---|---|---|
| korpus_W | korpus 200x200, dno Z0, wierzch korpus_h, napis 0,6 na przodzie | [-100.0, -100.6, 0.0] | [100.0, 100.0, 59.6] | ✓ |
| korpus_P | korpus P jak W | [-100.0, -100.6, 0.0] | [100.0, 100.0, 59.6] | ✓ |
| blat | blat wierzch blat_top_z, kołnierz 10 w dół | [-100.0, -100.0, 49.6] | [100.0, 100.0, 63.6] | ✓ |
| wkladka | wkładka: spód ramy na blat_top_z, kołki 3,5 w dół, kołek orient. do 71,1 | [-65.0, -52.3, 60.1] | [65.0, 96.0, 71.1] | ✓ |
| plytka_n1 | płytka: spód na półce 66,1, wierzch 74,1 + relief 0,6 | [-48.0, -48.0, 66.1] | [48.0, 48.0, 74.7] | ✓ |
| pokrywka | pokrywka: wierzch 90,1, dół kołnierza 70,1 | [-49.8, -49.8, 70.1] | [49.8, 49.8, 90.1] | ✓ |
| tulejka | tulejka: kołnierz na licu x=-42 od strony kieszeni, walec w ścianie -42..-40 | [-43.0, 81.5, 22.5] | [-40.0, 96.5, 37.499] | ✓ |

## Tabela B. Karta pasowań (luzy z siatek STL i brył zastępczych)

| Para | Miejsce / punkt | Luz z planu | Luz zmierzony | Reguła 4.8 / źródło | Werdykt | Uwaga |
|---|---|---|---|---|---|---|
| płytka poranna_n4 – wkładka (otwór 96,6/96,0) | lewy y=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n4 – wkładka (otwór 96,6/96,0) | prawy y=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n4 – wkładka (otwór 96,6/96,0) | lewy y=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n4 – wkładka (otwór 96,6/96,0) | prawy y=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n4 – wkładka (otwór 96,6/96,0) | lewy y=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n4 – wkładka (otwór 96,6/96,0) | prawy y=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n4 – wkładka (otwór 96,6/96,0) | przód x=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n4 – wkładka (otwór 96,6/96,0) | przód x=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n4 – wkładka (otwór 96,6/96,0) | przód x=-40 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n4 – wkładka (otwór 96,6/96,0) | przód x=40 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n4 – wkładka (otwór 96,6/96,0) | tył x=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n4 – wkładka (otwór 96,6/96,0) | tył x=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n4 – wkładka (otwór 96,6/96,0) | tył x=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n4 – półka wkładki (styk Z) | narożnik (-38,-38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka poranna_n4 – półka wkładki (styk Z) | narożnik (-38,38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka poranna_n4 – półka wkładki (styk Z) | narożnik (38,38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka poranna_n4 – półka wkładki (styk Z) | narożnik (38,-38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka poranna_n4 – kołek orient. 4,4 w wycięciu 5 | X, Z=67.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK | plan 4.11 podaje 0,3 (kołek + 2·0,3 = 5,0); z 4.6.4 (kołek 0,5 od ściany otworu) i 4.1 (płytka 0,3 od ściany) wynika 0,4 przy płytce wycentrowanej; 0,1…0,7 w zakresie luzu płytki |
| płytka poranna_n4 – kołek orient. 4,4 w wycięciu 5 | Y, Z=67.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK |  |
| płytka poranna_n4 – kołek orient. 4,4 w wycięciu 5 | X, Z=69.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK | plan 4.11 podaje 0,3 (kołek + 2·0,3 = 5,0); z 4.6.4 (kołek 0,5 od ściany otworu) i 4.1 (płytka 0,3 od ściany) wynika 0,4 przy płytce wycentrowanej; 0,1…0,7 w zakresie luzu płytki |
| płytka poranna_n4 – kołek orient. 4,4 w wycięciu 5 | Y, Z=69.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK |  |
| płytka poranna_n4 – czujnik Halla A (proxy) | szczelina Z: spód płytki − wierzch czujnika w (-40.3,-39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka poranna_n4 – czujnik Halla B (proxy) | szczelina Z: spód płytki − wierzch czujnika w (-40.3,39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka poranna_n4 – czujnik Halla C (proxy) | szczelina Z: spód płytki − wierzch czujnika w (40.3,39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka poranna_n5 – wkładka (otwór 96,6/96,0) | lewy y=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n5 – wkładka (otwór 96,6/96,0) | prawy y=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n5 – wkładka (otwór 96,6/96,0) | lewy y=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n5 – wkładka (otwór 96,6/96,0) | prawy y=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n5 – wkładka (otwór 96,6/96,0) | lewy y=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n5 – wkładka (otwór 96,6/96,0) | prawy y=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n5 – wkładka (otwór 96,6/96,0) | przód x=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n5 – wkładka (otwór 96,6/96,0) | przód x=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n5 – wkładka (otwór 96,6/96,0) | przód x=-40 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n5 – wkładka (otwór 96,6/96,0) | przód x=40 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n5 – wkładka (otwór 96,6/96,0) | tył x=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n5 – wkładka (otwór 96,6/96,0) | tył x=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n5 – wkładka (otwór 96,6/96,0) | tył x=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n5 – półka wkładki (styk Z) | narożnik (-38,-38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka poranna_n5 – półka wkładki (styk Z) | narożnik (-38,38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka poranna_n5 – półka wkładki (styk Z) | narożnik (38,38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka poranna_n5 – półka wkładki (styk Z) | narożnik (38,-38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka poranna_n5 – kołek orient. 4,4 w wycięciu 5 | X, Z=67.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK | plan 4.11 podaje 0,3 (kołek + 2·0,3 = 5,0); z 4.6.4 (kołek 0,5 od ściany otworu) i 4.1 (płytka 0,3 od ściany) wynika 0,4 przy płytce wycentrowanej; 0,1…0,7 w zakresie luzu płytki |
| płytka poranna_n5 – kołek orient. 4,4 w wycięciu 5 | Y, Z=67.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK |  |
| płytka poranna_n5 – kołek orient. 4,4 w wycięciu 5 | X, Z=69.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK | plan 4.11 podaje 0,3 (kołek + 2·0,3 = 5,0); z 4.6.4 (kołek 0,5 od ściany otworu) i 4.1 (płytka 0,3 od ściany) wynika 0,4 przy płytce wycentrowanej; 0,1…0,7 w zakresie luzu płytki |
| płytka poranna_n5 – kołek orient. 4,4 w wycięciu 5 | Y, Z=69.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK |  |
| płytka poranna_n5 – czujnik Halla A (proxy) | szczelina Z: spód płytki − wierzch czujnika w (-40.3,-39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka poranna_n5 – czujnik Halla B (proxy) | szczelina Z: spód płytki − wierzch czujnika w (-40.3,39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka poranna_n5 – czujnik Halla C (proxy) | szczelina Z: spód płytki − wierzch czujnika w (40.3,39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka poranna_n6 – wkładka (otwór 96,6/96,0) | lewy y=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n6 – wkładka (otwór 96,6/96,0) | prawy y=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n6 – wkładka (otwór 96,6/96,0) | lewy y=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n6 – wkładka (otwór 96,6/96,0) | prawy y=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n6 – wkładka (otwór 96,6/96,0) | lewy y=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n6 – wkładka (otwór 96,6/96,0) | prawy y=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n6 – wkładka (otwór 96,6/96,0) | przód x=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n6 – wkładka (otwór 96,6/96,0) | przód x=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n6 – wkładka (otwór 96,6/96,0) | przód x=-40 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n6 – wkładka (otwór 96,6/96,0) | przód x=40 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n6 – wkładka (otwór 96,6/96,0) | tył x=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n6 – wkładka (otwór 96,6/96,0) | tył x=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n6 – wkładka (otwór 96,6/96,0) | tył x=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna_n6 – półka wkładki (styk Z) | narożnik (-38,-38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka poranna_n6 – półka wkładki (styk Z) | narożnik (-38,38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka poranna_n6 – półka wkładki (styk Z) | narożnik (38,38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka poranna_n6 – półka wkładki (styk Z) | narożnik (38,-38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka poranna_n6 – kołek orient. 4,4 w wycięciu 5 | X, Z=67.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK | plan 4.11 podaje 0,3 (kołek + 2·0,3 = 5,0); z 4.6.4 (kołek 0,5 od ściany otworu) i 4.1 (płytka 0,3 od ściany) wynika 0,4 przy płytce wycentrowanej; 0,1…0,7 w zakresie luzu płytki |
| płytka poranna_n6 – kołek orient. 4,4 w wycięciu 5 | Y, Z=67.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK |  |
| płytka poranna_n6 – kołek orient. 4,4 w wycięciu 5 | X, Z=69.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK | plan 4.11 podaje 0,3 (kołek + 2·0,3 = 5,0); z 4.6.4 (kołek 0,5 od ściany otworu) i 4.1 (płytka 0,3 od ściany) wynika 0,4 przy płytce wycentrowanej; 0,1…0,7 w zakresie luzu płytki |
| płytka poranna_n6 – kołek orient. 4,4 w wycięciu 5 | Y, Z=69.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK |  |
| płytka poranna_n6 – czujnik Halla A (proxy) | szczelina Z: spód płytki − wierzch czujnika w (-40.3,-39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka poranna_n6 – czujnik Halla B (proxy) | szczelina Z: spód płytki − wierzch czujnika w (-40.3,39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka poranna_n6 – czujnik Halla C (proxy) | szczelina Z: spód płytki − wierzch czujnika w (40.3,39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka poranna – wkładka (otwór 96,6/96,0) | lewy y=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna – wkładka (otwór 96,6/96,0) | prawy y=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna – wkładka (otwór 96,6/96,0) | lewy y=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna – wkładka (otwór 96,6/96,0) | prawy y=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna – wkładka (otwór 96,6/96,0) | lewy y=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna – wkładka (otwór 96,6/96,0) | prawy y=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna – wkładka (otwór 96,6/96,0) | przód x=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna – wkładka (otwór 96,6/96,0) | przód x=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna – wkładka (otwór 96,6/96,0) | przód x=-40 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna – wkładka (otwór 96,6/96,0) | przód x=40 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna – wkładka (otwór 96,6/96,0) | tył x=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna – wkładka (otwór 96,6/96,0) | tył x=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna – wkładka (otwór 96,6/96,0) | tył x=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka poranna – półka wkładki (styk Z) | narożnik (-38,-38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka poranna – półka wkładki (styk Z) | narożnik (-38,38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka poranna – półka wkładki (styk Z) | narożnik (38,38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka poranna – półka wkładki (styk Z) | narożnik (38,-38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka poranna – kołek orient. 4,4 w wycięciu 5 | X, Z=67.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK | plan 4.11 podaje 0,3 (kołek + 2·0,3 = 5,0); z 4.6.4 (kołek 0,5 od ściany otworu) i 4.1 (płytka 0,3 od ściany) wynika 0,4 przy płytce wycentrowanej; 0,1…0,7 w zakresie luzu płytki |
| płytka poranna – kołek orient. 4,4 w wycięciu 5 | Y, Z=67.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK |  |
| płytka poranna – kołek orient. 4,4 w wycięciu 5 | X, Z=69.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK | plan 4.11 podaje 0,3 (kołek + 2·0,3 = 5,0); z 4.6.4 (kołek 0,5 od ściany otworu) i 4.1 (płytka 0,3 od ściany) wynika 0,4 przy płytce wycentrowanej; 0,1…0,7 w zakresie luzu płytki |
| płytka poranna – kołek orient. 4,4 w wycięciu 5 | Y, Z=69.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK |  |
| płytka poranna – czujnik Halla A (proxy) | szczelina Z: spód płytki − wierzch czujnika w (-40.3,-39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka poranna – czujnik Halla B (proxy) | szczelina Z: spód płytki − wierzch czujnika w (-40.3,39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka poranna – czujnik Halla C (proxy) | szczelina Z: spód płytki − wierzch czujnika w (40.3,39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka wieczorna_n1 – wkładka (otwór 96,6/96,0) | lewy y=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n1 – wkładka (otwór 96,6/96,0) | prawy y=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n1 – wkładka (otwór 96,6/96,0) | lewy y=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n1 – wkładka (otwór 96,6/96,0) | prawy y=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n1 – wkładka (otwór 96,6/96,0) | lewy y=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n1 – wkładka (otwór 96,6/96,0) | prawy y=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n1 – wkładka (otwór 96,6/96,0) | przód x=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n1 – wkładka (otwór 96,6/96,0) | przód x=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n1 – wkładka (otwór 96,6/96,0) | przód x=-40 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n1 – wkładka (otwór 96,6/96,0) | przód x=40 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n1 – wkładka (otwór 96,6/96,0) | tył x=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n1 – wkładka (otwór 96,6/96,0) | tył x=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n1 – wkładka (otwór 96,6/96,0) | tył x=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n1 – półka wkładki (styk Z) | narożnik (-38,-38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka wieczorna_n1 – półka wkładki (styk Z) | narożnik (-38,38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka wieczorna_n1 – półka wkładki (styk Z) | narożnik (38,38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka wieczorna_n1 – półka wkładki (styk Z) | narożnik (38,-38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka wieczorna_n1 – kołek orient. 4,4 w wycięciu 5 | X, Z=67.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK | plan 4.11 podaje 0,3 (kołek + 2·0,3 = 5,0); z 4.6.4 (kołek 0,5 od ściany otworu) i 4.1 (płytka 0,3 od ściany) wynika 0,4 przy płytce wycentrowanej; 0,1…0,7 w zakresie luzu płytki |
| płytka wieczorna_n1 – kołek orient. 4,4 w wycięciu 5 | Y, Z=67.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK |  |
| płytka wieczorna_n1 – kołek orient. 4,4 w wycięciu 5 | X, Z=69.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK | plan 4.11 podaje 0,3 (kołek + 2·0,3 = 5,0); z 4.6.4 (kołek 0,5 od ściany otworu) i 4.1 (płytka 0,3 od ściany) wynika 0,4 przy płytce wycentrowanej; 0,1…0,7 w zakresie luzu płytki |
| płytka wieczorna_n1 – kołek orient. 4,4 w wycięciu 5 | Y, Z=69.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK |  |
| płytka wieczorna_n1 – czujnik Halla A (proxy) | szczelina Z: spód płytki − wierzch czujnika w (-40.3,-39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka n1 – magnes A – czujnik Halla A (proxy) | spód magnesu − wierzch czujnika | 1,200 | 1,200 | D5: 0,2 + 1,0 = 1,2 (≤ 4) | OK |  |
| płytka wieczorna_n1 – czujnik Halla B (proxy) | szczelina Z: spód płytki − wierzch czujnika w (-40.3,39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka wieczorna_n1 – czujnik Halla C (proxy) | szczelina Z: spód płytki − wierzch czujnika w (40.3,39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka n1 – magnes A ø5 w kieszeni ø5,2 | luz promieniowy X | 0,100 | 0,100 | magnesy 0,1–0,2 (klejone) | OK |  |
| płytka n1 – magnes A ø5 w kieszeni ø5,2 | luz promieniowy Y | 0,100 | 0,099 | magnesy 0,1–0,2 (klejone) | OK |  |
| płytka n1 – magnes A: sufit kieszeni | Z | 0,000 | -0,000 | magnes dosunięty do dna kieszeni | OK |  |
| płytka n1 – magnes A: cofnięcie w kieszeni | Z (spód magnesu − spód płytki) | 0,200 | 0,200 | D5: 0,2 | OK |  |
| płytka wieczorna_n2 – wkładka (otwór 96,6/96,0) | lewy y=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n2 – wkładka (otwór 96,6/96,0) | prawy y=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n2 – wkładka (otwór 96,6/96,0) | lewy y=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n2 – wkładka (otwór 96,6/96,0) | prawy y=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n2 – wkładka (otwór 96,6/96,0) | lewy y=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n2 – wkładka (otwór 96,6/96,0) | prawy y=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n2 – wkładka (otwór 96,6/96,0) | przód x=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n2 – wkładka (otwór 96,6/96,0) | przód x=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n2 – wkładka (otwór 96,6/96,0) | przód x=-40 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n2 – wkładka (otwór 96,6/96,0) | przód x=40 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n2 – wkładka (otwór 96,6/96,0) | tył x=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n2 – wkładka (otwór 96,6/96,0) | tył x=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n2 – wkładka (otwór 96,6/96,0) | tył x=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n2 – półka wkładki (styk Z) | narożnik (-38,-38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka wieczorna_n2 – półka wkładki (styk Z) | narożnik (-38,38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka wieczorna_n2 – półka wkładki (styk Z) | narożnik (38,38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka wieczorna_n2 – półka wkładki (styk Z) | narożnik (38,-38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka wieczorna_n2 – kołek orient. 4,4 w wycięciu 5 | X, Z=67.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK | plan 4.11 podaje 0,3 (kołek + 2·0,3 = 5,0); z 4.6.4 (kołek 0,5 od ściany otworu) i 4.1 (płytka 0,3 od ściany) wynika 0,4 przy płytce wycentrowanej; 0,1…0,7 w zakresie luzu płytki |
| płytka wieczorna_n2 – kołek orient. 4,4 w wycięciu 5 | Y, Z=67.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK |  |
| płytka wieczorna_n2 – kołek orient. 4,4 w wycięciu 5 | X, Z=69.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK | plan 4.11 podaje 0,3 (kołek + 2·0,3 = 5,0); z 4.6.4 (kołek 0,5 od ściany otworu) i 4.1 (płytka 0,3 od ściany) wynika 0,4 przy płytce wycentrowanej; 0,1…0,7 w zakresie luzu płytki |
| płytka wieczorna_n2 – kołek orient. 4,4 w wycięciu 5 | Y, Z=69.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK |  |
| płytka wieczorna_n2 – czujnik Halla A (proxy) | szczelina Z: spód płytki − wierzch czujnika w (-40.3,-39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka wieczorna_n2 – czujnik Halla B (proxy) | szczelina Z: spód płytki − wierzch czujnika w (-40.3,39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka wieczorna_n2 – czujnik Halla C (proxy) | szczelina Z: spód płytki − wierzch czujnika w (40.3,39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka wieczorna_n3 – wkładka (otwór 96,6/96,0) | lewy y=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n3 – wkładka (otwór 96,6/96,0) | prawy y=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n3 – wkładka (otwór 96,6/96,0) | lewy y=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n3 – wkładka (otwór 96,6/96,0) | prawy y=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n3 – wkładka (otwór 96,6/96,0) | lewy y=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n3 – wkładka (otwór 96,6/96,0) | prawy y=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n3 – wkładka (otwór 96,6/96,0) | przód x=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n3 – wkładka (otwór 96,6/96,0) | przód x=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n3 – wkładka (otwór 96,6/96,0) | przód x=-40 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n3 – wkładka (otwór 96,6/96,0) | przód x=40 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n3 – wkładka (otwór 96,6/96,0) | tył x=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n3 – wkładka (otwór 96,6/96,0) | tył x=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n3 – wkładka (otwór 96,6/96,0) | tył x=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna_n3 – półka wkładki (styk Z) | narożnik (-38,-38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka wieczorna_n3 – półka wkładki (styk Z) | narożnik (-38,38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka wieczorna_n3 – półka wkładki (styk Z) | narożnik (38,38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka wieczorna_n3 – półka wkładki (styk Z) | narożnik (38,-38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka wieczorna_n3 – kołek orient. 4,4 w wycięciu 5 | X, Z=67.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK | plan 4.11 podaje 0,3 (kołek + 2·0,3 = 5,0); z 4.6.4 (kołek 0,5 od ściany otworu) i 4.1 (płytka 0,3 od ściany) wynika 0,4 przy płytce wycentrowanej; 0,1…0,7 w zakresie luzu płytki |
| płytka wieczorna_n3 – kołek orient. 4,4 w wycięciu 5 | Y, Z=67.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK |  |
| płytka wieczorna_n3 – kołek orient. 4,4 w wycięciu 5 | X, Z=69.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK | plan 4.11 podaje 0,3 (kołek + 2·0,3 = 5,0); z 4.6.4 (kołek 0,5 od ściany otworu) i 4.1 (płytka 0,3 od ściany) wynika 0,4 przy płytce wycentrowanej; 0,1…0,7 w zakresie luzu płytki |
| płytka wieczorna_n3 – kołek orient. 4,4 w wycięciu 5 | Y, Z=69.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK |  |
| płytka wieczorna_n3 – czujnik Halla A (proxy) | szczelina Z: spód płytki − wierzch czujnika w (-40.3,-39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka wieczorna_n3 – czujnik Halla B (proxy) | szczelina Z: spód płytki − wierzch czujnika w (-40.3,39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka wieczorna_n3 – czujnik Halla C (proxy) | szczelina Z: spód płytki − wierzch czujnika w (40.3,39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka wieczorna – wkładka (otwór 96,6/96,0) | lewy y=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna – wkładka (otwór 96,6/96,0) | prawy y=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna – wkładka (otwór 96,6/96,0) | lewy y=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna – wkładka (otwór 96,6/96,0) | prawy y=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna – wkładka (otwór 96,6/96,0) | lewy y=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna – wkładka (otwór 96,6/96,0) | prawy y=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna – wkładka (otwór 96,6/96,0) | przód x=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna – wkładka (otwór 96,6/96,0) | przód x=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna – wkładka (otwór 96,6/96,0) | przód x=-40 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna – wkładka (otwór 96,6/96,0) | przód x=40 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna – wkładka (otwór 96,6/96,0) | tył x=-30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna – wkładka (otwór 96,6/96,0) | tył x=0 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna – wkładka (otwór 96,6/96,0) | tył x=30 | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| płytka wieczorna – półka wkładki (styk Z) | narożnik (-38,-38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka wieczorna – półka wkładki (styk Z) | narożnik (-38,38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka wieczorna – półka wkładki (styk Z) | narożnik (38,38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka wieczorna – półka wkładki (styk Z) | narożnik (38,-38) | 0,000 | -0,000 | styk (D5) | OK |  |
| płytka wieczorna – kołek orient. 4,4 w wycięciu 5 | X, Z=67.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK | plan 4.11 podaje 0,3 (kołek + 2·0,3 = 5,0); z 4.6.4 (kołek 0,5 od ściany otworu) i 4.1 (płytka 0,3 od ściany) wynika 0,4 przy płytce wycentrowanej; 0,1…0,7 w zakresie luzu płytki |
| płytka wieczorna – kołek orient. 4,4 w wycięciu 5 | Y, Z=67.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK |  |
| płytka wieczorna – kołek orient. 4,4 w wycięciu 5 | X, Z=69.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK | plan 4.11 podaje 0,3 (kołek + 2·0,3 = 5,0); z 4.6.4 (kołek 0,5 od ściany otworu) i 4.1 (płytka 0,3 od ściany) wynika 0,4 przy płytce wycentrowanej; 0,1…0,7 w zakresie luzu płytki |
| płytka wieczorna – kołek orient. 4,4 w wycięciu 5 | Y, Z=69.1 | 0,400 | 0,400 | ruchome (4.11: 0,3; geometria 4.6.4+4.1: 0,4) | OK |  |
| płytka wieczorna – czujnik Halla A (proxy) | szczelina Z: spód płytki − wierzch czujnika w (-40.3,-39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka wieczorna – czujnik Halla B (proxy) | szczelina Z: spód płytki − wierzch czujnika w (-40.3,39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| płytka wieczorna – czujnik Halla C (proxy) | szczelina Z: spód płytki − wierzch czujnika w (40.3,39.7) | 1,000 | 1,000 | D5: 1,0 | OK |  |
| wkładka – blat: kołek ø3 w otworze ø3,3 | kołek x=-58, X, Z=62.6 | 0,150 | 0,150 | wciskane 0,1–0,15 | OK |  |
| wkładka – blat: kołek ø3 w otworze ø3,3 | kołek x=-58, -X, Z=62.6 | 0,150 | 0,150 | wciskane 0,1–0,15 | OK |  |
| wkładka – blat: kołek ø3 w otworze ø3,3 | kołek x=-58, Y, Z=62.6 | 0,150 | 0,151 | wciskane 0,1–0,15 | OK |  |
| wkładka – blat: kołek ø3 w otworze ø3,3 | kołek x=-58, -Y, Z=62.6 | 0,150 | 0,151 | wciskane 0,1–0,15 | OK |  |
| wkładka – blat: kołek ø3 w otworze ø3,3 | kołek x=-58, X, Z=61.1 | 0,150 | 0,150 | wciskane 0,1–0,15 | OK |  |
| wkładka – blat: kołek ø3 w otworze ø3,3 | kołek x=-58, -X, Z=61.1 | 0,150 | 0,150 | wciskane 0,1–0,15 | OK |  |
| wkładka – blat: kołek ø3 w otworze ø3,3 | kołek x=-58, Y, Z=61.1 | 0,150 | 0,151 | wciskane 0,1–0,15 | OK |  |
| wkładka – blat: kołek ø3 w otworze ø3,3 | kołek x=-58, -Y, Z=61.1 | 0,150 | 0,151 | wciskane 0,1–0,15 | OK |  |
| wkładka – blat: kołek: koniec vs dno otworu ślepego | kołek x=-58 | 0,300 | 0,300 | luz osiowy (R8: 3,8 − 3,5) | OK |  |
| wkładka – magnes ø5 w otworze ucha ø5,4 | x=-58, promieniowo | 0,200 | 0,200 | magnesy 0,1–0,2 (klejone) | OK |  |
| blat – magnes ø5 w kieszeni ø5,4 | x=-58, promieniowo | 0,200 | 0,200 | magnesy 0,1–0,2 (klejone) | OK |  |
| wkładka – blat: współosiowość otworu magnesu i kieszeni | x=-58 (odległość środków XY) | 0,000 | 0,000 | współosiowe | OK |  |
| wkładka – blat/dyfuzor: ucho leży płasko | x=-56: ucho na dyfuzorze (y=70) | 0,000 | 0,000 | styk (R30) | OK |  |
| wkładka – blat/dyfuzor: ucho leży płasko | x=-56: ucho na blacie (y=82,5) | 0,000 | 0,000 | styk (R30) | OK |  |
| wkładka – blat/dyfuzor: ucho leży płasko | x=-61: ucho na blacie (y=92) | 0,000 | 0,000 | styk (R30) | OK |  |
| wkładka – blat: kołek ø3 w otworze ø3,3 | kołek x=58, X, Z=62.6 | 0,150 | 0,150 | wciskane 0,1–0,15 | OK |  |
| wkładka – blat: kołek ø3 w otworze ø3,3 | kołek x=58, -X, Z=62.6 | 0,150 | 0,150 | wciskane 0,1–0,15 | OK |  |
| wkładka – blat: kołek ø3 w otworze ø3,3 | kołek x=58, Y, Z=62.6 | 0,150 | 0,151 | wciskane 0,1–0,15 | OK |  |
| wkładka – blat: kołek ø3 w otworze ø3,3 | kołek x=58, -Y, Z=62.6 | 0,150 | 0,151 | wciskane 0,1–0,15 | OK |  |
| wkładka – blat: kołek ø3 w otworze ø3,3 | kołek x=58, X, Z=61.1 | 0,150 | 0,150 | wciskane 0,1–0,15 | OK |  |
| wkładka – blat: kołek ø3 w otworze ø3,3 | kołek x=58, -X, Z=61.1 | 0,150 | 0,150 | wciskane 0,1–0,15 | OK |  |
| wkładka – blat: kołek ø3 w otworze ø3,3 | kołek x=58, Y, Z=61.1 | 0,150 | 0,151 | wciskane 0,1–0,15 | OK |  |
| wkładka – blat: kołek ø3 w otworze ø3,3 | kołek x=58, -Y, Z=61.1 | 0,150 | 0,151 | wciskane 0,1–0,15 | OK |  |
| wkładka – blat: kołek: koniec vs dno otworu ślepego | kołek x=58 | 0,300 | 0,300 | luz osiowy (R8: 3,8 − 3,5) | OK |  |
| wkładka – magnes ø5 w otworze ucha ø5,4 | x=58, promieniowo | 0,200 | 0,200 | magnesy 0,1–0,2 (klejone) | OK |  |
| blat – magnes ø5 w kieszeni ø5,4 | x=58, promieniowo | 0,200 | 0,200 | magnesy 0,1–0,2 (klejone) | OK |  |
| wkładka – blat: współosiowość otworu magnesu i kieszeni | x=58 (odległość środków XY) | 0,000 | 0,000 | współosiowe | OK |  |
| wkładka – blat/dyfuzor: ucho leży płasko | x=56: ucho na dyfuzorze (y=70) | 0,000 | 0,000 | styk (R30) | OK |  |
| wkładka – blat/dyfuzor: ucho leży płasko | x=56: ucho na blacie (y=82,5) | 0,000 | 0,000 | styk (R30) | OK |  |
| wkładka – blat/dyfuzor: ucho leży płasko | x=61: ucho na blacie (y=92) | 0,000 | 0,000 | styk (R30) | OK |  |
| wkładka – dyfuzor: spód ramy na dyfuzorze | (30,-50.3) | 0,000 | 0,000 | styk (R30) | OK |  |
| wkładka – dyfuzor: spód ramy na dyfuzorze | (-30,-50.3) | 0,000 | 0,000 | styk (R30) | OK |  |
| wkładka – dyfuzor: spód ramy na dyfuzorze | (0,49) | 0,000 | 0,000 | styk (R30) | OK |  |
| wkładka – dyfuzor: spód ramy na dyfuzorze | (-49,0) | 0,000 | 0,000 | styk (R30) | OK |  |
| wkładka – dyfuzor: spód ramy na dyfuzorze | (49,0) | 0,000 | 0,000 | styk (R30) | OK |  |
| wkładka – dyfuzor: spód ramy na dyfuzorze | (-49,30) | 0,000 | 0,000 | styk (R30) | OK |  |
| pokrywka – wkładka: kołnierz nad ramą | (30,-49.5) | 0,500 | 0,500 | bez styku (4.11) | OK |  |
| pokrywka – wkładka: kołnierz nad ramą | (-30,49.5) | 0,500 | 0,500 | bez styku (4.11) | OK |  |
| pokrywka – wkładka: kołnierz nad ramą | (49.5,20) | 0,500 | 0,500 | bez styku (4.11) | OK |  |
| pokrywka – wkładka: strzałki ▼ pod kołnierzem (XY rozłączne) | szczyt strzałki Z vs dół kołnierza | 70,200 | 70,200 | 4.11: relief do 70,2 na y −50…−52,3; kołnierz y −48,3…−49,8 | OK |  |
| dyfuzor 160 – kieszeń blatu 162 | X w (80.5, 0) | 1,000 | 1,000 | luz 1,0 (D13) | OK |  |
| dyfuzor 160 – kieszeń blatu 162 | -X w (-80.5, 0) | 1,000 | 1,000 | luz 1,0 (D13) | OK |  |
| dyfuzor 160 – kieszeń blatu 162 | Y w (0, 80.5) | 1,000 | 1,000 | luz 1,0 (D13) | OK |  |
| dyfuzor 160 – kieszeń blatu 162 | -Y w (0, -80.5) | 1,000 | 1,000 | luz 1,0 (D13) | OK |  |
| dyfuzor 160 – kieszeń blatu 162 | X w (80.5, 50) | 1,000 | 1,000 | luz 1,0 (D13) | OK |  |
| dyfuzor 160 – kieszeń blatu 162 | -Y w (-50, -80.5) | 1,000 | 1,000 | luz 1,0 (D13) | OK |  |
| dyfuzor – półka kieszeni blatu (styk Z) | (79.5,0) | 0,000 | 0,000 | styk; półka 2 mm (79…81) | OK |  |
| dyfuzor – półka kieszeni blatu (styk Z) | (0,79.5) | 0,000 | 0,000 | styk; półka 2 mm (79…81) | OK |  |
| dyfuzor – półka kieszeni blatu (styk Z) | (-79.5,40) | 0,000 | 0,000 | styk; półka 2 mm (79…81) | OK |  |
| dyfuzor – blat: licowanie wierzchu | Z | 0,000 | 0,000 | licowany (R30) | OK |  |
| blat – korpus W: kołnierz 194,0 w 195 | X w (97.25,30,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus W: kołnierz 194,0 w 195 | X w (97.25,-60,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus W: kołnierz 194,0 w 195 | X w (97.25,60,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus W: kołnierz 194,0 w 195 | -X w (-97.25,30,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus W: kołnierz 194,0 w 195 | -X w (-97.25,-60,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus W: kołnierz 194,0 w 195 | -Y w (30,-97.25,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus W: kołnierz 194,0 w 195 | -Y w (-30,-97.25,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus W: kołnierz 194,0 w 195 | -Y w (80,-97.25,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus W: kołnierz 194,0 w 195 | Y w (30,97.25,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus W: kołnierz 194,0 w 195 | Y w (-70,97.25,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus W: kołnierz 194,0 w 195 | Y w (85,97.25,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus W: haczyk prawy — zahaczenie | czubek 98.300 − ściana wewn. 97.500 | 0,800 | 0,800 | zatrzask (R48: 0,8) | OK |  |
| blat – korpus W: haczyk prawy — luz do dna kieszeni | dno 98.500 − czubek 98.300 | 0,200 | 0,200 | zatrzask (0,2) | OK |  |
| blat – korpus W: haczyk prawy — luz pod występem (Z) | start rampy 52.87 − dno kieszeni 52.60 | 0,250 | 0,270 | zatrzask (R47: 0,25) | OK |  |
| blat – korpus W: haczyk prawy — luz nad występem (Z) | sufit kieszeni 55.10 − górna krawędź występu 54.84 | 0,250 | 0,260 | zatrzask (R47: 0,25) | OK |  |
| blat – korpus W: haczyk prawy — szerokość 8 w kieszeni 10 | luz wzdłuż Y na stronę | 1,000 | 1,000 | ruchome (1,0/stronę z planu) | OK |  |
| blat – korpus W: haczyk lewy — zahaczenie | czubek 98.300 − ściana wewn. 97.500 | 0,800 | 0,800 | zatrzask (R48: 0,8) | OK |  |
| blat – korpus W: haczyk lewy — luz do dna kieszeni | dno 98.500 − czubek 98.300 | 0,200 | 0,200 | zatrzask (0,2) | OK |  |
| blat – korpus W: haczyk lewy — luz pod występem (Z) | start rampy 52.87 − dno kieszeni 52.60 | 0,250 | 0,270 | zatrzask (R47: 0,25) | OK |  |
| blat – korpus W: haczyk lewy — luz nad występem (Z) | sufit kieszeni 55.10 − górna krawędź występu 54.84 | 0,250 | 0,260 | zatrzask (R47: 0,25) | OK |  |
| blat – korpus W: haczyk lewy — szerokość 8 w kieszeni 10 | luz wzdłuż Y na stronę | 1,000 | 1,000 | ruchome (1,0/stronę z planu) | OK |  |
| blat – korpus W: haczyk przedni — zahaczenie | czubek 98.300 − ściana wewn. 97.500 | 0,800 | 0,800 | zatrzask (R48: 0,8) | OK |  |
| blat – korpus W: haczyk przedni — luz do dna kieszeni | dno 98.500 − czubek 98.300 | 0,200 | 0,200 | zatrzask (0,2) | OK |  |
| blat – korpus W: haczyk przedni — luz pod występem (Z) | start rampy 52.87 − dno kieszeni 52.60 | 0,250 | 0,270 | zatrzask (R47: 0,25) | OK |  |
| blat – korpus W: haczyk przedni — luz nad występem (Z) | sufit kieszeni 55.10 − górna krawędź występu 54.85 | 0,250 | 0,250 | zatrzask (R47: 0,25) | OK |  |
| blat – korpus W: haczyk przedni — szerokość 8 w kieszeni 10 | luz wzdłuż X na stronę | 1,000 | 1,000 | ruchome (1,0/stronę z planu) | OK |  |
| blat – korpus W: haczyk tylny — zahaczenie | czubek 98.300 − ściana wewn. 97.500 | 0,800 | 0,800 | zatrzask (R48: 0,8) | OK |  |
| blat – korpus W: haczyk tylny — luz do dna kieszeni | dno 98.500 − czubek 98.300 | 0,200 | 0,200 | zatrzask (0,2) | OK |  |
| blat – korpus W: haczyk tylny — luz pod występem (Z) | start rampy 52.87 − dno kieszeni 52.60 | 0,250 | 0,270 | zatrzask (R47: 0,25) | OK |  |
| blat – korpus W: haczyk tylny — luz nad występem (Z) | sufit kieszeni 55.10 − górna krawędź występu 54.84 | 0,250 | 0,260 | zatrzask (R47: 0,25) | OK |  |
| blat – korpus W: haczyk tylny — szerokość 8 w kieszeni 10 | luz wzdłuż X na stronę | 1,000 | 1,000 | ruchome (1,0/stronę z planu) | OK |  |
| blat – korpus W: spód blatu na wierzchu ściany | (98.75,30) | 0,000 | -0,000 | styk | OK |  |
| blat – korpus W: spód blatu na wierzchu ściany | (-98.75,-30) | 0,000 | 0,000 | styk | OK |  |
| blat – korpus W: spód blatu na wierzchu ściany | (30,98.75) | 0,000 | -0,000 | styk | OK |  |
| blat – korpus W: spód blatu na wierzchu ściany | (30,-98.75) | 0,000 | 0,000 | styk | OK |  |
| blat – korpus W: wkręt x=-75 — współosiowość otworów | ściana ø3,2 vs słupek ø2,5 (XZ) | 0,000 | 0,002 | współosiowe (R7) | OK |  |
| blat – korpus W: wkręt x=-75 — ø w ścianie | cięciwa X | 3,200 | 3,195 | przelot M3 | OK |  |
| blat – korpus W: wkręt x=-75 — ø w słupku | cięciwa X | 2,500 | 2,500 | gwint formowany (R49) | OK |  |
| blat – korpus W: lico słupka/kołnierza vs ściana | x=-75, Y | 0,500 | 0,500 | 0,5 (R48) | OK |  |
| blat – korpus W: wkręt x=75 — współosiowość otworów | ściana ø3,2 vs słupek ø2,5 (XZ) | 0,000 | 0,002 | współosiowe (R7) | OK |  |
| blat – korpus W: wkręt x=75 — ø w ścianie | cięciwa X | 3,200 | 3,195 | przelot M3 | OK |  |
| blat – korpus W: wkręt x=75 — ø w słupku | cięciwa X | 2,500 | 2,500 | gwint formowany (R49) | OK |  |
| blat – korpus W: lico słupka/kołnierza vs ściana | x=75, Y | 0,500 | 0,500 | 0,5 (R48) | OK |  |
| panel (proxy) – spód blatu przy oknie | (79,5, 0) | 4,000 | 4,000 | ≥ 2 (K‑49) | OK |  |
| blat – korpus P: kołnierz 194,0 w 195 | X w (97.25,30,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus P: kołnierz 194,0 w 195 | X w (97.25,-60,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus P: kołnierz 194,0 w 195 | X w (97.25,60,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus P: kołnierz 194,0 w 195 | -X w (-97.25,30,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus P: kołnierz 194,0 w 195 | -X w (-97.25,-60,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus P: kołnierz 194,0 w 195 | -Y w (30,-97.25,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus P: kołnierz 194,0 w 195 | -Y w (-30,-97.25,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus P: kołnierz 194,0 w 195 | -Y w (80,-97.25,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus P: kołnierz 194,0 w 195 | Y w (30,97.25,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus P: kołnierz 194,0 w 195 | Y w (-70,97.25,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus P: kołnierz 194,0 w 195 | Y w (85,97.25,54.6) | 0,500 | 0,500 | ruchome 0,3 + SLS ±0,3/200 → 0,5 (R48) | OK |  |
| blat – korpus P: haczyk prawy — zahaczenie | czubek 98.300 − ściana wewn. 97.500 | 0,800 | 0,800 | zatrzask (R48: 0,8) | OK |  |
| blat – korpus P: haczyk prawy — luz do dna kieszeni | dno 98.500 − czubek 98.300 | 0,200 | 0,200 | zatrzask (0,2) | OK |  |
| blat – korpus P: haczyk prawy — luz pod występem (Z) | start rampy 52.87 − dno kieszeni 52.60 | 0,250 | 0,270 | zatrzask (R47: 0,25) | OK |  |
| blat – korpus P: haczyk prawy — luz nad występem (Z) | sufit kieszeni 55.10 − górna krawędź występu 54.84 | 0,250 | 0,260 | zatrzask (R47: 0,25) | OK |  |
| blat – korpus P: haczyk prawy — szerokość 8 w kieszeni 10 | luz wzdłuż Y na stronę | 1,000 | 1,000 | ruchome (1,0/stronę z planu) | OK |  |
| blat – korpus P: haczyk lewy — zahaczenie | czubek 98.300 − ściana wewn. 97.500 | 0,800 | 0,800 | zatrzask (R48: 0,8) | OK |  |
| blat – korpus P: haczyk lewy — luz do dna kieszeni | dno 98.500 − czubek 98.300 | 0,200 | 0,200 | zatrzask (0,2) | OK |  |
| blat – korpus P: haczyk lewy — luz pod występem (Z) | start rampy 52.87 − dno kieszeni 52.60 | 0,250 | 0,270 | zatrzask (R47: 0,25) | OK |  |
| blat – korpus P: haczyk lewy — luz nad występem (Z) | sufit kieszeni 55.10 − górna krawędź występu 54.84 | 0,250 | 0,260 | zatrzask (R47: 0,25) | OK |  |
| blat – korpus P: haczyk lewy — szerokość 8 w kieszeni 10 | luz wzdłuż Y na stronę | 1,000 | 1,000 | ruchome (1,0/stronę z planu) | OK |  |
| blat – korpus P: haczyk przedni — zahaczenie | czubek 98.300 − ściana wewn. 97.500 | 0,800 | 0,800 | zatrzask (R48: 0,8) | OK |  |
| blat – korpus P: haczyk przedni — luz do dna kieszeni | dno 98.500 − czubek 98.300 | 0,200 | 0,200 | zatrzask (0,2) | OK |  |
| blat – korpus P: haczyk przedni — luz pod występem (Z) | start rampy 52.87 − dno kieszeni 52.60 | 0,250 | 0,270 | zatrzask (R47: 0,25) | OK |  |
| blat – korpus P: haczyk przedni — luz nad występem (Z) | sufit kieszeni 55.10 − górna krawędź występu 54.85 | 0,250 | 0,250 | zatrzask (R47: 0,25) | OK |  |
| blat – korpus P: haczyk przedni — szerokość 8 w kieszeni 10 | luz wzdłuż X na stronę | 1,000 | 1,000 | ruchome (1,0/stronę z planu) | OK |  |
| blat – korpus P: haczyk tylny — zahaczenie | czubek 98.300 − ściana wewn. 97.500 | 0,800 | 0,800 | zatrzask (R48: 0,8) | OK |  |
| blat – korpus P: haczyk tylny — luz do dna kieszeni | dno 98.500 − czubek 98.300 | 0,200 | 0,200 | zatrzask (0,2) | OK |  |
| blat – korpus P: haczyk tylny — luz pod występem (Z) | start rampy 52.87 − dno kieszeni 52.60 | 0,250 | 0,270 | zatrzask (R47: 0,25) | OK |  |
| blat – korpus P: haczyk tylny — luz nad występem (Z) | sufit kieszeni 55.10 − górna krawędź występu 54.84 | 0,250 | 0,260 | zatrzask (R47: 0,25) | OK |  |
| blat – korpus P: haczyk tylny — szerokość 8 w kieszeni 10 | luz wzdłuż X na stronę | 1,000 | 1,000 | ruchome (1,0/stronę z planu) | OK |  |
| blat – korpus P: spód blatu na wierzchu ściany | (98.75,30) | 0,000 | -0,000 | styk | OK |  |
| blat – korpus P: spód blatu na wierzchu ściany | (-98.75,-30) | 0,000 | 0,000 | styk | OK |  |
| blat – korpus P: spód blatu na wierzchu ściany | (30,98.75) | 0,000 | -0,000 | styk | OK |  |
| blat – korpus P: spód blatu na wierzchu ściany | (30,-98.75) | 0,000 | 0,000 | styk | OK |  |
| blat – korpus P: wkręt x=-75 — współosiowość otworów | ściana ø3,2 vs słupek ø2,5 (XZ) | 0,000 | 0,002 | współosiowe (R7) | OK |  |
| blat – korpus P: wkręt x=-75 — ø w ścianie | cięciwa X | 3,200 | 3,195 | przelot M3 | OK |  |
| blat – korpus P: wkręt x=-75 — ø w słupku | cięciwa X | 2,500 | 2,500 | gwint formowany (R49) | OK |  |
| blat – korpus P: lico słupka/kołnierza vs ściana | x=-75, Y | 0,500 | 0,500 | 0,5 (R48) | OK |  |
| blat – korpus P: wkręt x=75 — współosiowość otworów | ściana ø3,2 vs słupek ø2,5 (XZ) | 0,000 | 0,002 | współosiowe (R7) | OK |  |
| blat – korpus P: wkręt x=75 — ø w ścianie | cięciwa X | 3,200 | 3,195 | przelot M3 | OK |  |
| blat – korpus P: wkręt x=75 — ø w słupku | cięciwa X | 2,500 | 2,500 | gwint formowany (R49) | OK |  |
| blat – korpus P: lico słupka/kołnierza vs ściana | x=75, Y | 0,500 | 0,500 | 0,5 (R48) | OK |  |
| panel (proxy) – spód blatu przy oknie | (79,5, 0) | 4,000 | 4,000 | ≥ 2 (K‑49) | OK |  |
| dystans 1 – stadion korpusu W (styk Z) | (-61.5,-58.5) | 0,000 | 0,000 | styk (R5, R50‑2) | OK |  |
| dystans 1 – stadion korpusu W: wierzch stadionu | Z | 4 | 4,000 | 3 + 1 = 4 | OK |  |
| dystans 1 – rowek w dnie korpusu W (szer. prostopadle do przekątnej) | (-60,-60, Z 1,5) | 3,400 | 3,400 | rowek 3,4 (R50‑2) | OK |  |
| dystans 1 – rowek w dnie korpusu W (długość wzdłuż przekątnej) | (-60,-60, Z 1,5) | 17,542 | 17,542 | od (±55,±55) do (±65,±65) + 3,4 | OK |  |
| dystans 1 – rowek przelotowy przez dno korpusu W | promień −Z w osi z Z 2,9 | 0,000 | 0,000 | 0 = przelot (R50‑U20, bez pogłębienia) | OK |  |
| dystans 1 – stadion korpusu P (styk Z) | (-61.5,-58.5) | 0,000 | 0,000 | styk (R5, R50‑2) | OK |  |
| dystans 1 – stadion korpusu P: wierzch stadionu | Z | 4 | 4,000 | 3 + 1 = 4 | OK |  |
| dystans 1 – rowek w dnie korpusu P (szer. prostopadle do przekątnej) | (-60,-60, Z 1,5) | 3,400 | 3,400 | rowek 3,4 (R50‑2) | OK |  |
| dystans 1 – rowek w dnie korpusu P (długość wzdłuż przekątnej) | (-60,-60, Z 1,5) | 17,542 | 17,542 | od (±55,±55) do (±65,±65) + 3,4 | OK |  |
| dystans 1 – rowek przelotowy przez dno korpusu P | promień −Z w osi z Z 2,9 | 0,000 | 0,000 | 0 = przelot (R50‑U20, bez pogłębienia) | OK |  |
| panel (proxy) – dystans 1 (styk Z) | (-61.5,-58.5) | 0,000 | 0,000 | styk (R50‑7) | OK |  |
| panel (proxy) – dystans 1: wierzch dystansu | Z | 54 | 54,000 | panel_pcb_z 54 | OK |  |
| dystans 1: ø bryły zastępczej | cięciwa X w Z 30 | 6,400 | 6,398 | 6,4 (sześciokąt 5,5) | OK |  |
| dystans 2 – stadion korpusu W (styk Z) | (-61.5,58.5) | 0,000 | 0,000 | styk (R5, R50‑2) | OK |  |
| dystans 2 – stadion korpusu W: wierzch stadionu | Z | 4 | 4,000 | 3 + 1 = 4 | OK |  |
| dystans 2 – rowek w dnie korpusu W (szer. prostopadle do przekątnej) | (-60,60, Z 1,5) | 3,400 | 3,400 | rowek 3,4 (R50‑2) | OK |  |
| dystans 2 – rowek w dnie korpusu W (długość wzdłuż przekątnej) | (-60,60, Z 1,5) | 17,542 | 17,542 | od (±55,±55) do (±65,±65) + 3,4 | OK |  |
| dystans 2 – rowek przelotowy przez dno korpusu W | promień −Z w osi z Z 2,9 | 0,000 | 0,000 | 0 = przelot (R50‑U20, bez pogłębienia) | OK |  |
| dystans 2 – stadion korpusu P (styk Z) | (-61.5,58.5) | 0,000 | 0,000 | styk (R5, R50‑2) | OK |  |
| dystans 2 – stadion korpusu P: wierzch stadionu | Z | 4 | 4,000 | 3 + 1 = 4 | OK |  |
| dystans 2 – rowek w dnie korpusu P (szer. prostopadle do przekątnej) | (-60,60, Z 1,5) | 3,400 | 3,400 | rowek 3,4 (R50‑2) | OK |  |
| dystans 2 – rowek w dnie korpusu P (długość wzdłuż przekątnej) | (-60,60, Z 1,5) | 17,542 | 17,542 | od (±55,±55) do (±65,±65) + 3,4 | OK |  |
| dystans 2 – rowek przelotowy przez dno korpusu P | promień −Z w osi z Z 2,9 | 0,000 | 0,000 | 0 = przelot (R50‑U20, bez pogłębienia) | OK |  |
| panel (proxy) – dystans 2 (styk Z) | (-61.5,58.5) | 0,000 | 0,000 | styk (R50‑7) | OK |  |
| panel (proxy) – dystans 2: wierzch dystansu | Z | 54 | 54,000 | panel_pcb_z 54 | OK |  |
| dystans 2: ø bryły zastępczej | cięciwa X w Z 30 | 6,400 | 6,398 | 6,4 (sześciokąt 5,5) | OK |  |
| dystans 3 – stadion korpusu W (styk Z) | (61.5,-58.5) | 0,000 | 0,000 | styk (R5, R50‑2) | OK |  |
| dystans 3 – stadion korpusu W: wierzch stadionu | Z | 4 | 4,000 | 3 + 1 = 4 | OK |  |
| dystans 3 – rowek w dnie korpusu W (szer. prostopadle do przekątnej) | (60,-60, Z 1,5) | 3,400 | 3,400 | rowek 3,4 (R50‑2) | OK |  |
| dystans 3 – rowek w dnie korpusu W (długość wzdłuż przekątnej) | (60,-60, Z 1,5) | 17,542 | 17,542 | od (±55,±55) do (±65,±65) + 3,4 | OK |  |
| dystans 3 – rowek przelotowy przez dno korpusu W | promień −Z w osi z Z 2,9 | 0,000 | 0,000 | 0 = przelot (R50‑U20, bez pogłębienia) | OK |  |
| dystans 3 – stadion korpusu P (styk Z) | (61.5,-58.5) | 0,000 | 0,000 | styk (R5, R50‑2) | OK |  |
| dystans 3 – stadion korpusu P: wierzch stadionu | Z | 4 | 4,000 | 3 + 1 = 4 | OK |  |
| dystans 3 – rowek w dnie korpusu P (szer. prostopadle do przekątnej) | (60,-60, Z 1,5) | 3,400 | 3,400 | rowek 3,4 (R50‑2) | OK |  |
| dystans 3 – rowek w dnie korpusu P (długość wzdłuż przekątnej) | (60,-60, Z 1,5) | 17,542 | 17,542 | od (±55,±55) do (±65,±65) + 3,4 | OK |  |
| dystans 3 – rowek przelotowy przez dno korpusu P | promień −Z w osi z Z 2,9 | 0,000 | 0,000 | 0 = przelot (R50‑U20, bez pogłębienia) | OK |  |
| panel (proxy) – dystans 3 (styk Z) | (61.5,-58.5) | 0,000 | 0,000 | styk (R50‑7) | OK |  |
| panel (proxy) – dystans 3: wierzch dystansu | Z | 54 | 54,000 | panel_pcb_z 54 | OK |  |
| dystans 3: ø bryły zastępczej | cięciwa X w Z 30 | 6,400 | 6,398 | 6,4 (sześciokąt 5,5) | OK |  |
| dystans 4 – stadion korpusu W (styk Z) | (61.5,58.5) | 0,000 | -0,000 | styk (R5, R50‑2) | OK |  |
| dystans 4 – stadion korpusu W: wierzch stadionu | Z | 4 | 4,000 | 3 + 1 = 4 | OK |  |
| dystans 4 – rowek w dnie korpusu W (szer. prostopadle do przekątnej) | (60,60, Z 1,5) | 3,400 | 3,400 | rowek 3,4 (R50‑2) | OK |  |
| dystans 4 – rowek w dnie korpusu W (długość wzdłuż przekątnej) | (60,60, Z 1,5) | 17,542 | 17,542 | od (±55,±55) do (±65,±65) + 3,4 | OK |  |
| dystans 4 – rowek przelotowy przez dno korpusu W | promień −Z w osi z Z 2,9 | 0,000 | 0,000 | 0 = przelot (R50‑U20, bez pogłębienia) | OK |  |
| dystans 4 – stadion korpusu P (styk Z) | (61.5,58.5) | 0,000 | -0,000 | styk (R5, R50‑2) | OK |  |
| dystans 4 – stadion korpusu P: wierzch stadionu | Z | 4 | 4,000 | 3 + 1 = 4 | OK |  |
| dystans 4 – rowek w dnie korpusu P (szer. prostopadle do przekątnej) | (60,60, Z 1,5) | 3,400 | 3,400 | rowek 3,4 (R50‑2) | OK |  |
| dystans 4 – rowek w dnie korpusu P (długość wzdłuż przekątnej) | (60,60, Z 1,5) | 17,542 | 17,542 | od (±55,±55) do (±65,±65) + 3,4 | OK |  |
| dystans 4 – rowek przelotowy przez dno korpusu P | promień −Z w osi z Z 2,9 | 0,000 | 0,000 | 0 = przelot (R50‑U20, bez pogłębienia) | OK |  |
| panel (proxy) – dystans 4 (styk Z) | (61.5,58.5) | 0,000 | 0,000 | styk (R50‑7) | OK |  |
| panel (proxy) – dystans 4: wierzch dystansu | Z | 54 | 54,000 | panel_pcb_z 54 | OK |  |
| dystans 4: ø bryły zastępczej | cięciwa X w Z 30 | 6,400 | 6,398 | 6,4 (sześciokąt 5,5) | OK |  |
| Pi (proxy) – boss korpusu W (-46.5,-24.5): styk Z | wierzch bossa vs spód PCB | 0,000 | 0,000 | styk | OK |  |
| Pi – boss korpusu W (-46.5,-24.5): wierzch bossa | Z | 8 | 8,000 | 3 + 5 = 8 | OK |  |
| Pi – boss korpusu W (-46.5,-24.5): otwór ø | cięciwa X w Z 6 | 2,100 | 2,100 | ø2,1 pod M2,5 formowany | OK |  |
| Pi – boss korpusu W (-46.5,-24.5): głębokość otworu | od wierzchu bossa | 5 | 5,000 | 5 | OK |  |
| Pi – boss korpusu W (-46.5,-24.5): ø bossa | promienie z zewnątrz X w Z 6 | 8 | 7,998 | ø8 (R48) | OK |  |
| Pi (proxy) – boss korpusu W (11.5,-24.5): styk Z | wierzch bossa vs spód PCB | 0,000 | 0,000 | styk | OK |  |
| Pi – boss korpusu W (11.5,-24.5): wierzch bossa | Z | 8 | 8,000 | 3 + 5 = 8 | OK |  |
| Pi – boss korpusu W (11.5,-24.5): otwór ø | cięciwa X w Z 6 | 2,100 | 2,100 | ø2,1 pod M2,5 formowany | OK |  |
| Pi – boss korpusu W (11.5,-24.5): głębokość otworu | od wierzchu bossa | 5 | 5,000 | 5 | OK |  |
| Pi – boss korpusu W (11.5,-24.5): ø bossa | promienie z zewnątrz X w Z 6 | 8 | 7,998 | ø8 (R48) | OK |  |
| Pi (proxy) – boss korpusu W (-46.5,24.5): styk Z | wierzch bossa vs spód PCB | 0,000 | 0,000 | styk | OK |  |
| Pi – boss korpusu W (-46.5,24.5): wierzch bossa | Z | 8 | 8,000 | 3 + 5 = 8 | OK |  |
| Pi – boss korpusu W (-46.5,24.5): otwór ø | cięciwa X w Z 6 | 2,100 | 2,100 | ø2,1 pod M2,5 formowany | OK |  |
| Pi – boss korpusu W (-46.5,24.5): głębokość otworu | od wierzchu bossa | 5 | 5,000 | 5 | OK |  |
| Pi – boss korpusu W (-46.5,24.5): ø bossa | promienie z zewnątrz X w Z 6 | 8 | 7,998 | ø8 (R48) | OK |  |
| Pi (proxy) – boss korpusu W (11.5,24.5): styk Z | wierzch bossa vs spód PCB | 0,000 | 0,000 | styk | OK |  |
| Pi – boss korpusu W (11.5,24.5): wierzch bossa | Z | 8 | 8,000 | 3 + 5 = 8 | OK |  |
| Pi – boss korpusu W (11.5,24.5): otwór ø | cięciwa X w Z 6 | 2,100 | 2,100 | ø2,1 pod M2,5 formowany | OK |  |
| Pi – boss korpusu W (11.5,24.5): głębokość otworu | od wierzchu bossa | 5 | 5,000 | 5 | OK |  |
| Pi – boss korpusu W (11.5,24.5): ø bossa | promienie z zewnątrz X w Z 6 | 8 | 7,998 | ø8 (R48) | OK |  |
| Pi – boss korpusu W: oś otworu vs otwór Pi (-46.5,-24.5) | odległość środków XY | 0,000 | 0,000 | współosiowe (R50‑6) | OK |  |
| Pi – boss korpusu W: oś otworu vs otwór Pi (-46.5,24.5) | odległość środków XY | 0,000 | 0,000 | współosiowe (R50‑6) | OK |  |
| Pi – boss korpusu W: oś otworu vs otwór Pi (11.5,-24.5) | odległość środków XY | 0,000 | 0,000 | współosiowe (R50‑6) | OK |  |
| Pi – boss korpusu W: oś otworu vs otwór Pi (11.5,24.5) | odległość środków XY | 0,000 | 0,000 | współosiowe (R50‑6) | OK |  |
| Pi (proxy) – boss korpusu P (-46.5,-24.5): styk Z | wierzch bossa vs spód PCB | 0,000 | 0,000 | styk | OK |  |
| Pi – boss korpusu P (-46.5,-24.5): wierzch bossa | Z | 8 | 8,000 | 3 + 5 = 8 | OK |  |
| Pi – boss korpusu P (-46.5,-24.5): otwór ø | cięciwa X w Z 6 | 2,100 | 2,100 | ø2,1 pod M2,5 formowany | OK |  |
| Pi – boss korpusu P (-46.5,-24.5): głębokość otworu | od wierzchu bossa | 5 | 5,000 | 5 | OK |  |
| Pi – boss korpusu P (-46.5,-24.5): ø bossa | promienie z zewnątrz X w Z 6 | 8 | 7,998 | ø8 (R48) | OK |  |
| Pi (proxy) – boss korpusu P (11.5,-24.5): styk Z | wierzch bossa vs spód PCB | 0,000 | 0,000 | styk | OK |  |
| Pi – boss korpusu P (11.5,-24.5): wierzch bossa | Z | 8 | 8,000 | 3 + 5 = 8 | OK |  |
| Pi – boss korpusu P (11.5,-24.5): otwór ø | cięciwa X w Z 6 | 2,100 | 2,100 | ø2,1 pod M2,5 formowany | OK |  |
| Pi – boss korpusu P (11.5,-24.5): głębokość otworu | od wierzchu bossa | 5 | 5,000 | 5 | OK |  |
| Pi – boss korpusu P (11.5,-24.5): ø bossa | promienie z zewnątrz X w Z 6 | 8 | 7,998 | ø8 (R48) | OK |  |
| Pi (proxy) – boss korpusu P (-46.5,24.5): styk Z | wierzch bossa vs spód PCB | 0,000 | 0,000 | styk | OK |  |
| Pi – boss korpusu P (-46.5,24.5): wierzch bossa | Z | 8 | 8,000 | 3 + 5 = 8 | OK |  |
| Pi – boss korpusu P (-46.5,24.5): otwór ø | cięciwa X w Z 6 | 2,100 | 2,100 | ø2,1 pod M2,5 formowany | OK |  |
| Pi – boss korpusu P (-46.5,24.5): głębokość otworu | od wierzchu bossa | 5 | 5,000 | 5 | OK |  |
| Pi – boss korpusu P (-46.5,24.5): ø bossa | promienie z zewnątrz X w Z 6 | 8 | 7,998 | ø8 (R48) | OK |  |
| Pi (proxy) – boss korpusu P (11.5,24.5): styk Z | wierzch bossa vs spód PCB | 0,000 | 0,000 | styk | OK |  |
| Pi – boss korpusu P (11.5,24.5): wierzch bossa | Z | 8 | 8,000 | 3 + 5 = 8 | OK |  |
| Pi – boss korpusu P (11.5,24.5): otwór ø | cięciwa X w Z 6 | 2,100 | 2,100 | ø2,1 pod M2,5 formowany | OK |  |
| Pi – boss korpusu P (11.5,24.5): głębokość otworu | od wierzchu bossa | 5 | 5,000 | 5 | OK |  |
| Pi – boss korpusu P (11.5,24.5): ø bossa | promienie z zewnątrz X w Z 6 | 8 | 7,998 | ø8 (R48) | OK |  |
| Pi – boss korpusu P: oś otworu vs otwór Pi (-46.5,-24.5) | odległość środków XY | 0,000 | 0,000 | współosiowe (R50‑6) | OK |  |
| Pi – boss korpusu P: oś otworu vs otwór Pi (-46.5,24.5) | odległość środków XY | 0,000 | 0,000 | współosiowe (R50‑6) | OK |  |
| Pi – boss korpusu P: oś otworu vs otwór Pi (11.5,-24.5) | odległość środków XY | 0,000 | 0,000 | współosiowe (R50‑6) | OK |  |
| Pi – boss korpusu P: oś otworu vs otwór Pi (11.5,24.5) | odległość środków XY | 0,000 | 0,000 | współosiowe (R50‑6) | OK |  |
| gniazdo DC – otwór ø12 w ścianie skrzynki (korpus W) | cięciwa Y | 12 | 11,999 | ø12 (R50‑3) | OK |  |
| gniazdo DC – otwór ø12 w ścianie skrzynki (korpus W) | cięciwa Z | 12 | 11,998 | ø12 (R50‑3) | OK |  |
| gniazdo DC – oś otworu (korpus W) | środek vs (y 89, Z 30) | 0,000 | 0,001 | oś (y 89, Z 30) wzdłuż X | OK |  |
| tulejka DC – otwór ø12 (korpus W) | (ø otworu − ø walca)/2 | 0,000 | 0,000 | wciskane 0,1–0,15 (opis dc_bush_outer_d: „pasowanie wciskane 0,1”) | OK / POZA REGULA 4.8 | dc_bush_outer_d = dc_hole_d = 12 → luz 0,0 z definicji parametrów |
| tulejka DC – kołnierz na licu ściany skrzynki (korpus W) | x kołnierza vs lico −42 | 0,000 | 0,000 | styk (R50‑3) | OK |  |
| tulejka DC – otwór ø8,2 dla gwintu gniazda ø8 | cięciwa Y | 0,100 | 0,100 | 0,1 (R50‑3) | OK |  |
| gniazdo DC (proxy) – nakrętka na ścianie od wnętrza (korpus W) | x nakrętki vs lico −40 | 0,000 | 0,000 | styk (R50‑3) | OK |  |
| wtyk DC kątowy 26 – lewa ściana skrzynki (korpus W) | zapas X: lico gniazda −45 − 26 vs ściana | 24,500 | 24,500 | 4.11: 27,5 od lica −42 (tu lico −45: kołnierz tulejki 1 + flansza gniazda 2) | OK |  |
| wtyk DC prosty 40 + zagięcie 12 – lewa ściana skrzynki (korpus W) | zapas X liczony jak w 4.11 (od lica −42) | 1,500 | 1,500 | 4.11: −94 > −95,5 (1,5) | OK |  |
| wtyk DC prosty 40 + zagięcie 12 – lewa ściana skrzynki (korpus W) | zapas X od realnego lica gniazda −45 (kołnierz tulejki 1 + flansza gniazda 2) — INFORMACYJNIE | -1,500 | -1,500 | informacyjnie; nie w 4.11 | OK | wtyk prosty 40 mieści się tylko przy kablu zagiętym ciaśniej niż 12 (albo bez tulejki / cieńszej flanszy); rekomendowany wtyk kątowy (plan 5) |
| wtyk ø11 w świetle okna (korpus W): Z | Z 24,5…35,5 w oknie 14…38 | 10,500 | 10,500 | 4.11 | OK |  |
| gniazdo DC – otwór ø12 w ścianie skrzynki (korpus P) | cięciwa Y | 12 | 11,999 | ø12 (R50‑3) | OK |  |
| gniazdo DC – otwór ø12 w ścianie skrzynki (korpus P) | cięciwa Z | 12 | 11,998 | ø12 (R50‑3) | OK |  |
| gniazdo DC – oś otworu (korpus P) | środek vs (y 89, Z 30) | 0,000 | 0,001 | oś (y 89, Z 30) wzdłuż X | OK |  |
| tulejka DC – otwór ø12 (korpus P) | (ø otworu − ø walca)/2 | 0,000 | 0,000 | wciskane 0,1–0,15 (opis dc_bush_outer_d: „pasowanie wciskane 0,1”) | OK / POZA REGULA 4.8 | dc_bush_outer_d = dc_hole_d = 12 → luz 0,0 z definicji parametrów |
| tulejka DC – kołnierz na licu ściany skrzynki (korpus P) | x kołnierza vs lico −42 | 0,000 | 0,000 | styk (R50‑3) | OK |  |
| tulejka DC – otwór ø8,2 dla gwintu gniazda ø8 | cięciwa Y | 0,100 | 0,100 | 0,1 (R50‑3) | OK |  |
| gniazdo DC (proxy) – nakrętka na ścianie od wnętrza (korpus P) | x nakrętki vs lico −40 | 0,000 | 0,000 | styk (R50‑3) | OK |  |
| wtyk DC kątowy 26 – lewa ściana skrzynki (korpus P) | zapas X: lico gniazda −45 − 26 vs ściana | 24,500 | 24,500 | 4.11: 27,5 od lica −42 (tu lico −45: kołnierz tulejki 1 + flansza gniazda 2) | OK |  |
| wtyk DC prosty 40 + zagięcie 12 – lewa ściana skrzynki (korpus P) | zapas X liczony jak w 4.11 (od lica −42) | 1,500 | 1,500 | 4.11: −94 > −95,5 (1,5) | OK |  |
| wtyk DC prosty 40 + zagięcie 12 – lewa ściana skrzynki (korpus P) | zapas X od realnego lica gniazda −45 (kołnierz tulejki 1 + flansza gniazda 2) — INFORMACYJNIE | -1,500 | -1,500 | informacyjnie; nie w 4.11 | OK | wtyk prosty 40 mieści się tylko przy kablu zagiętym ciaśniej niż 12 (albo bez tulejki / cieńszej flanszy); rekomendowany wtyk kątowy (plan 5) |
| wtyk ø11 w świetle okna (korpus P): Z | Z 24,5…35,5 w oknie 14…38 | 10,500 | 10,500 | 4.11 | OK |  |
| gniazdo USB (proxy 16×20×14) – ściana korpusu W | tył bryły vs lico wewn. ściany (Y) | 0,000 | 0,000 | styk | OK |  |
| gniazdo USB (proxy) – dystans (60,60) | odstęp Y (sześciokąt, tol 0,3) | 14,300 | 14,462 | 4.11: ≥ 8,8 | OK |  |
| gniazdo USB (proxy 16×20×14) – ściana korpusu P | tył bryły vs lico wewn. ściany (Y) | 0,000 | 0,000 | styk | OK |  |
| gniazdo USB (proxy) – dystans (60,60) | odstęp Y (sześciokąt, tol 0,3) | 14,300 | 14,462 | 4.11: ≥ 8,8 | OK |  |
| pokrywka – płytka poranna_n4: wnęka 96,6/96,0 | X w (48.15,20,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n4: wnęka 96,6/96,0 | X w (48.15,-30,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n4: wnęka 96,6/96,0 | -X w (-48.15,20,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n4: wnęka 96,6/96,0 | -X w (-48.15,-30,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n4: wnęka 96,6/96,0 | Y w (20,48.15,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n4: wnęka 96,6/96,0 | Y w (-20,48.15,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n4: wnęka 96,6/96,0 | -Y w (20,-48.15,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n4: wnęka 96,6/96,0 | -Y w (40,-48.15,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n4: garb prawy (y=0) — luz do dna rowka | wzdłuż X | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n4: garb prawy (y=0) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n4: garb prawy (y=0) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n4: garb prawy (y=0) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n4: garb lewy (y=0) — luz do dna rowka | wzdłuż -X | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n4: garb lewy (y=0) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n4: garb lewy (y=0) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n4: garb lewy (y=0) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n4: garb przedni (x=+25) — luz do dna rowka | wzdłuż -Y | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n4: garb przedni (x=+25) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n4: garb przedni (x=+25) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n4: garb przedni (x=+25) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n4: garb tylny (x=−25) — luz do dna rowka | wzdłuż Y | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n4: garb tylny (x=−25) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n4: garb tylny (x=−25) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n4: garb tylny (x=−25) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n4: prześwit nad płytką | spód wierzchu pokrywki − wierzch płytki (−46,5, 0) | 14 | 14,000 | 14 (D8) | OK |  |
| pokrywka – płytka poranna_n5: wnęka 96,6/96,0 | X w (48.15,20,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n5: wnęka 96,6/96,0 | X w (48.15,-30,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n5: wnęka 96,6/96,0 | -X w (-48.15,20,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n5: wnęka 96,6/96,0 | -X w (-48.15,-30,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n5: wnęka 96,6/96,0 | Y w (20,48.15,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n5: wnęka 96,6/96,0 | Y w (-20,48.15,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n5: wnęka 96,6/96,0 | -Y w (20,-48.15,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n5: wnęka 96,6/96,0 | -Y w (40,-48.15,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n5: garb prawy (y=0) — luz do dna rowka | wzdłuż X | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n5: garb prawy (y=0) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n5: garb prawy (y=0) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n5: garb prawy (y=0) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n5: garb lewy (y=0) — luz do dna rowka | wzdłuż -X | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n5: garb lewy (y=0) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n5: garb lewy (y=0) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n5: garb lewy (y=0) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n5: garb przedni (x=+25) — luz do dna rowka | wzdłuż -Y | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n5: garb przedni (x=+25) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n5: garb przedni (x=+25) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n5: garb przedni (x=+25) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n5: garb tylny (x=−25) — luz do dna rowka | wzdłuż Y | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n5: garb tylny (x=−25) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n5: garb tylny (x=−25) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n5: garb tylny (x=−25) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n5: prześwit nad płytką | spód wierzchu pokrywki − wierzch płytki (−46,5, 0) | 14 | 14,000 | 14 (D8) | OK |  |
| pokrywka – płytka poranna_n6: wnęka 96,6/96,0 | X w (48.15,20,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n6: wnęka 96,6/96,0 | X w (48.15,-30,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n6: wnęka 96,6/96,0 | -X w (-48.15,20,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n6: wnęka 96,6/96,0 | -X w (-48.15,-30,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n6: wnęka 96,6/96,0 | Y w (20,48.15,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n6: wnęka 96,6/96,0 | Y w (-20,48.15,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n6: wnęka 96,6/96,0 | -Y w (20,-48.15,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n6: wnęka 96,6/96,0 | -Y w (40,-48.15,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna_n6: garb prawy (y=0) — luz do dna rowka | wzdłuż X | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n6: garb prawy (y=0) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n6: garb prawy (y=0) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n6: garb prawy (y=0) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n6: garb lewy (y=0) — luz do dna rowka | wzdłuż -X | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n6: garb lewy (y=0) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n6: garb lewy (y=0) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n6: garb lewy (y=0) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n6: garb przedni (x=+25) — luz do dna rowka | wzdłuż -Y | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n6: garb przedni (x=+25) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n6: garb przedni (x=+25) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n6: garb przedni (x=+25) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n6: garb tylny (x=−25) — luz do dna rowka | wzdłuż Y | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n6: garb tylny (x=−25) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna_n6: garb tylny (x=−25) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n6: garb tylny (x=−25) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna_n6: prześwit nad płytką | spód wierzchu pokrywki − wierzch płytki (−46,5, 0) | 14 | 14,000 | 14 (D8) | OK |  |
| pokrywka – płytka poranna: wnęka 96,6/96,0 | X w (48.15,20,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna: wnęka 96,6/96,0 | X w (48.15,-30,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna: wnęka 96,6/96,0 | -X w (-48.15,20,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna: wnęka 96,6/96,0 | -X w (-48.15,-30,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna: wnęka 96,6/96,0 | Y w (20,48.15,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna: wnęka 96,6/96,0 | Y w (-20,48.15,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna: wnęka 96,6/96,0 | -Y w (20,-48.15,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna: wnęka 96,6/96,0 | -Y w (40,-48.15,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka poranna: garb prawy (y=0) — luz do dna rowka | wzdłuż X | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna: garb prawy (y=0) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna: garb prawy (y=0) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna: garb prawy (y=0) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna: garb lewy (y=0) — luz do dna rowka | wzdłuż -X | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna: garb lewy (y=0) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna: garb lewy (y=0) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna: garb lewy (y=0) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna: garb przedni (x=+25) — luz do dna rowka | wzdłuż -Y | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna: garb przedni (x=+25) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna: garb przedni (x=+25) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna: garb przedni (x=+25) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna: garb tylny (x=−25) — luz do dna rowka | wzdłuż Y | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna: garb tylny (x=−25) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka poranna: garb tylny (x=−25) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna: garb tylny (x=−25) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka poranna: prześwit nad płytką | spód wierzchu pokrywki − wierzch płytki (−46,5, 0) | 14 | 14,000 | 14 (D8) | OK |  |
| pokrywka – płytka wieczorna_n1: wnęka 96,6/96,0 | X w (48.15,20,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n1: wnęka 96,6/96,0 | X w (48.15,-30,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n1: wnęka 96,6/96,0 | -X w (-48.15,20,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n1: wnęka 96,6/96,0 | -X w (-48.15,-30,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n1: wnęka 96,6/96,0 | Y w (20,48.15,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n1: wnęka 96,6/96,0 | Y w (-20,48.15,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n1: wnęka 96,6/96,0 | -Y w (20,-48.15,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n1: wnęka 96,6/96,0 | -Y w (40,-48.15,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n1: garb prawy (y=0) — luz do dna rowka | wzdłuż X | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n1: garb prawy (y=0) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n1: garb prawy (y=0) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n1: garb prawy (y=0) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n1: garb lewy (y=0) — luz do dna rowka | wzdłuż -X | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n1: garb lewy (y=0) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n1: garb lewy (y=0) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n1: garb lewy (y=0) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n1: garb przedni (x=+25) — luz do dna rowka | wzdłuż -Y | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n1: garb przedni (x=+25) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n1: garb przedni (x=+25) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n1: garb przedni (x=+25) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n1: garb tylny (x=−25) — luz do dna rowka | wzdłuż Y | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n1: garb tylny (x=−25) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n1: garb tylny (x=−25) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n1: garb tylny (x=−25) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n1: prześwit nad płytką | spód wierzchu pokrywki − wierzch płytki (−46,5, 0) | 14 | 14,000 | 14 (D8) | OK |  |
| pokrywka – płytka wieczorna_n2: wnęka 96,6/96,0 | X w (48.15,20,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n2: wnęka 96,6/96,0 | X w (48.15,-30,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n2: wnęka 96,6/96,0 | -X w (-48.15,20,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n2: wnęka 96,6/96,0 | -X w (-48.15,-30,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n2: wnęka 96,6/96,0 | Y w (20,48.15,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n2: wnęka 96,6/96,0 | Y w (-20,48.15,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n2: wnęka 96,6/96,0 | -Y w (20,-48.15,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n2: wnęka 96,6/96,0 | -Y w (40,-48.15,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n2: garb prawy (y=0) — luz do dna rowka | wzdłuż X | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n2: garb prawy (y=0) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n2: garb prawy (y=0) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n2: garb prawy (y=0) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n2: garb lewy (y=0) — luz do dna rowka | wzdłuż -X | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n2: garb lewy (y=0) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n2: garb lewy (y=0) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n2: garb lewy (y=0) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n2: garb przedni (x=+25) — luz do dna rowka | wzdłuż -Y | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n2: garb przedni (x=+25) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n2: garb przedni (x=+25) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n2: garb przedni (x=+25) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n2: garb tylny (x=−25) — luz do dna rowka | wzdłuż Y | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n2: garb tylny (x=−25) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n2: garb tylny (x=−25) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n2: garb tylny (x=−25) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n2: prześwit nad płytką | spód wierzchu pokrywki − wierzch płytki (−46,5, 0) | 14 | 14,000 | 14 (D8) | OK |  |
| pokrywka – płytka wieczorna_n3: wnęka 96,6/96,0 | X w (48.15,20,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n3: wnęka 96,6/96,0 | X w (48.15,-30,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n3: wnęka 96,6/96,0 | -X w (-48.15,20,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n3: wnęka 96,6/96,0 | -X w (-48.15,-30,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n3: wnęka 96,6/96,0 | Y w (20,48.15,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n3: wnęka 96,6/96,0 | Y w (-20,48.15,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n3: wnęka 96,6/96,0 | -Y w (20,-48.15,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n3: wnęka 96,6/96,0 | -Y w (40,-48.15,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna_n3: garb prawy (y=0) — luz do dna rowka | wzdłuż X | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n3: garb prawy (y=0) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n3: garb prawy (y=0) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n3: garb prawy (y=0) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n3: garb lewy (y=0) — luz do dna rowka | wzdłuż -X | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n3: garb lewy (y=0) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n3: garb lewy (y=0) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n3: garb lewy (y=0) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n3: garb przedni (x=+25) — luz do dna rowka | wzdłuż -Y | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n3: garb przedni (x=+25) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n3: garb przedni (x=+25) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n3: garb przedni (x=+25) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n3: garb tylny (x=−25) — luz do dna rowka | wzdłuż Y | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n3: garb tylny (x=−25) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna_n3: garb tylny (x=−25) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n3: garb tylny (x=−25) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna_n3: prześwit nad płytką | spód wierzchu pokrywki − wierzch płytki (−46,5, 0) | 14 | 14,000 | 14 (D8) | OK |  |
| pokrywka – płytka wieczorna: wnęka 96,6/96,0 | X w (48.15,20,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna: wnęka 96,6/96,0 | X w (48.15,-30,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna: wnęka 96,6/96,0 | -X w (-48.15,20,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna: wnęka 96,6/96,0 | -X w (-48.15,-30,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna: wnęka 96,6/96,0 | Y w (20,48.15,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna: wnęka 96,6/96,0 | Y w (-20,48.15,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna: wnęka 96,6/96,0 | -Y w (20,-48.15,73.2) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna: wnęka 96,6/96,0 | -Y w (40,-48.15,70.5) | 0,300 | 0,300 | ruchome 0,2–0,3 | OK |  |
| pokrywka – płytka wieczorna: garb prawy (y=0) — luz do dna rowka | wzdłuż X | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna: garb prawy (y=0) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna: garb prawy (y=0) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna: garb prawy (y=0) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna: garb lewy (y=0) — luz do dna rowka | wzdłuż -X | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna: garb lewy (y=0) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna: garb lewy (y=0) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna: garb lewy (y=0) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna: garb przedni (x=+25) — luz do dna rowka | wzdłuż -Y | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna: garb przedni (x=+25) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna: garb przedni (x=+25) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna: garb przedni (x=+25) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna: garb tylny (x=−25) — luz do dna rowka | wzdłuż Y | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna: garb tylny (x=−25) — zahaczenie | czubek garbu vs bok płytki | 0,400 | 0,400 | zatrzask (0,4) | OK |  |
| pokrywka – płytka wieczorna: garb tylny (x=−25) — luz Z nad garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna: garb tylny (x=−25) — luz Z pod garbem | rowek 1,0 / garb 0,8 | 0,100 | 0,105 | zatrzask (0,1) | OK |  |
| pokrywka – płytka wieczorna: prześwit nad płytką | spód wierzchu pokrywki − wierzch płytki (−46,5, 0) | 14 | 14,000 | 14 (D8) | OK |  |
| stos Pi+Bonnet (proxy) – spód elementów panelu | (0,0) Z | 8 | 8,000 | D4/R50‑1: ≥ 8; z taśmą HUB75 (+5) zostaje 3 | OK |  |
| stos Pi+Bonnet: szczyt | Z | 34 | 34,000 | 8 + 26 = 34 | OK |  |
| wtyk DC Bonnetu (−X, proxy) – lewa ściana korpusu W | X | 7,500 | 7,500 | D10/R50‑6: 7,5 | OK |  |
| odbiornik USB (proxy, korpus P) – prawa ściana | X | 43,500 | 43,500 | 4.11: do 62 vs 97,5 | OK |  |
| podkładka 05 – wkręt M3 w otworze ø3,4 | luz promieniowy | 0,200 | 0,198 | 0,2 | OK |  |
| podkładka 05 – dystans ø6,4 / stadion 9 | ø zewn. | 9 | 9,000 | 9 = szerokość stadionu | OK |  |
| podkładka 1 – wkręt M3 w otworze ø3,4 | luz promieniowy | 0,200 | 0,198 | 0,2 | OK |  |
| podkładka 1 – dystans ø6,4 / stadion 9 | ø zewn. | 9 | 9,000 | 9 = szerokość stadionu | OK |  |
| podkładka 2 – wkręt M3 w otworze ø3,4 | luz promieniowy | 0,200 | 0,198 | 0,2 | OK |  |
| podkładka 2 – dystans ø6,4 / stadion 9 | ø zewn. | 9 | 9,000 | 9 = szerokość stadionu | OK |  |

## Tabela C. Gabaryty STL (orientacja druku, bbox)

| STL | X × Y × Z | min | max | wierzchołki | trójkąty |
|---|---|---|---|---|---|
| `ramka_blat_v2.stl` | 200,000 × 200,000 × 14,000 | [-100.0, -100.0, 0.0] | [100.0, 100.0, 14.0] | 2854 | 5716 |
| `ramka_korpus_P_v2.stl` | 200,000 × 200,600 × 59,600 | [-100.0, -100.6, 0.0] | [100.0, 100.0, 59.6] | 8620 | 17324 |
| `ramka_korpus_W_v2.stl` | 200,000 × 200,600 × 59,600 | [-100.0, -100.6, 0.0] | [100.0, 100.0, 59.6] | 9068 | 18220 |
| `ramka_plytka_poranna_n4_v2.stl` | 96,000 × 96,000 × 8,600 | [-48.0, -48.0, 0.0] | [48.0, 48.0, 8.6] | 12864 | 25896 |
| `ramka_plytka_poranna_n5_v2.stl` | 96,000 × 96,000 × 8,600 | [-48.0, -48.0, 0.0] | [48.0, 48.0, 8.6] | 13052 | 26272 |
| `ramka_plytka_poranna_n6_v2.stl` | 96,000 × 96,000 × 8,600 | [-48.0, -48.0, 0.0] | [48.0, 48.0, 8.6] | 12980 | 26128 |
| `ramka_plytka_poranna_v2.stl` | 96,000 × 96,000 × 8,000 | [-48.0, -48.0, 0.0] | [48.0, 48.0, 8.0] | 12849 | 25866 |
| `ramka_plytka_wieczorna_n1_v2.stl` | 96,000 × 96,000 × 8,600 | [-48.0, -48.0, 0.0] | [48.0, 48.0, 8.6] | 10916 | 21956 |
| `ramka_plytka_wieczorna_n2_v2.stl` | 96,000 × 96,000 × 8,600 | [-48.0, -48.0, 0.0] | [48.0, 48.0, 8.6] | 11006 | 22136 |
| `ramka_plytka_wieczorna_n3_v2.stl` | 96,000 × 96,000 × 8,600 | [-48.0, -48.0, 0.0] | [48.0, 48.0, 8.6] | 11107 | 22338 |
| `ramka_plytka_wieczorna_v2.stl` | 96,000 × 96,000 × 8,000 | [-48.0, -48.0, 0.0] | [48.0, 48.0, 8.0] | 10934 | 21992 |
| `ramka_podkladka_panelu_05_v2.stl` | 9,000 × 8,997 × 0,500 | [-4.5, -4.498, 0.0] | [4.5, 4.498, 0.5] | 315 | 630 |
| `ramka_podkladka_panelu_1_v2.stl` | 9,000 × 8,997 × 1,000 | [-4.5, -4.498, 0.0] | [4.5, 4.498, 1.0] | 315 | 630 |
| `ramka_podkladka_panelu_2_v2.stl` | 9,000 × 8,997 × 2,000 | [-4.5, -4.498, 0.0] | [4.5, 4.498, 2.0] | 315 | 630 |
| `ramka_pokrywka_v2.stl` | 99,600 × 99,600 × 20,000 | [-49.8, -49.8, 0.0] | [49.8, 49.8, 20.0] | 412 | 820 |
| `ramka_tulejka_dc_v2.stl` | 14,999 × 14,999 × 3,000 | [-7.499, -7.5, 0.0] | [7.5, 7.5, 3.0] | 888 | 1776 |
| `ramka_wkladka_v2.stl` | 130,000 × 148,300 × 11,000 | [-65.0, -52.3, 0.0] | [65.0, 96.0, 11.0] | 895 | 1806 |

## Tabela D. Wymiary (układ złożeniowy D3; tolerancja 0,05)

| STL | Wymiar | Parametr | Oczekiwane | Zmierzone | Różnica | Metoda | Werdykt |
|---|---|---|---|---|---|---|---|
| `ramka_wkladka_v2.stl` | kołek ustalający x=-58: ø na końcu stożka | tab_pin_chamfer (ø3→ø2) | 2,040 | 2,040 | 0,000 | cięciwa 0,02 nad końcem | OK |
| `ramka_wkladka_v2.stl` | kołek ustalający x=58: ø na końcu stożka | tab_pin_chamfer (ø3→ø2) | 2,040 | 2,040 | 0,000 | cięciwa 0,02 nad końcem | OK |
| `ramka_blat_v2.stl` | haczyk prawy: dolna krawędź występu (start rampy) Z | snap_hook_z | 52,850 | 52,870 | 0,020 | profil promieniami co 0,01 | OK |
| `ramka_blat_v2.stl` | haczyk prawy: górna krawędź występu Z | snap_hook_z + snap_hook_hgt | 54,850 | 54,840 | -0,010 | profil promieniami co 0,01 | OK |
| `ramka_blat_v2.stl` | haczyk prawy: wysokość występu (z rampą) | snap_hook_hgt | 2,000 | 1,980 | -0,020 | profil | OK |
| `ramka_blat_v2.stl` | haczyk prawy: rampa naprowadzająca (wysokość od startu do pełnego występu) | 4.4.2 „rampa od dołu” (bez liczby) | 1,000 | 0,980 | -0,020 | profil; informacyjnie | OK |
| `ramka_blat_v2.stl` | haczyk lewy: dolna krawędź występu (start rampy) Z | snap_hook_z | 52,850 | 52,870 | 0,020 | profil promieniami co 0,01 | OK |
| `ramka_blat_v2.stl` | haczyk lewy: górna krawędź występu Z | snap_hook_z + snap_hook_hgt | 54,850 | 54,840 | -0,010 | profil promieniami co 0,01 | OK |
| `ramka_blat_v2.stl` | haczyk lewy: wysokość występu (z rampą) | snap_hook_hgt | 2,000 | 1,980 | -0,020 | profil | OK |
| `ramka_blat_v2.stl` | haczyk lewy: rampa naprowadzająca (wysokość od startu do pełnego występu) | 4.4.2 „rampa od dołu” (bez liczby) | 1,000 | 0,980 | -0,020 | profil; informacyjnie | OK |
| `ramka_blat_v2.stl` | haczyk przedni: dolna krawędź występu (start rampy) Z | snap_hook_z | 52,850 | 52,870 | 0,020 | profil promieniami co 0,01 | OK |
| `ramka_blat_v2.stl` | haczyk przedni: górna krawędź występu Z | snap_hook_z + snap_hook_hgt | 54,850 | 54,850 | 0,000 | profil promieniami co 0,01 | OK |
| `ramka_blat_v2.stl` | haczyk przedni: wysokość występu (z rampą) | snap_hook_hgt | 2,000 | 1,990 | -0,010 | profil | OK |
| `ramka_blat_v2.stl` | haczyk przedni: rampa naprowadzająca (wysokość od startu do pełnego występu) | 4.4.2 „rampa od dołu” (bez liczby) | 1,000 | 0,980 | -0,020 | profil; informacyjnie | OK |
| `ramka_blat_v2.stl` | haczyk tylny: dolna krawędź występu (start rampy) Z | snap_hook_z | 52,850 | 52,870 | 0,020 | profil promieniami co 0,01 | OK |
| `ramka_blat_v2.stl` | haczyk tylny: górna krawędź występu Z | snap_hook_z + snap_hook_hgt | 54,850 | 54,840 | -0,010 | profil promieniami co 0,01 | OK |
| `ramka_blat_v2.stl` | haczyk tylny: wysokość występu (z rampą) | snap_hook_hgt | 2,000 | 1,980 | -0,020 | profil | OK |
| `ramka_blat_v2.stl` | haczyk tylny: rampa naprowadzająca (wysokość od startu do pełnego występu) | 4.4.2 „rampa od dołu” (bez liczby) | 1,000 | 0,980 | -0,020 | profil; informacyjnie | OK |
| `ramka_korpus_W_v2.stl` | stadion panelu (-60,-60): szerokość | panel_pad_d | 9 | 9,000 | 0,000 | promienie z zewnątrz prostopadle do przekątnej, Z 3,5 | OK |
| `ramka_korpus_W_v2.stl` | stadion panelu (-60,-60): długość | panel_slot_pitch + panel_pad_d | 23,142 | 23,139 | -0,003 | promienie z zewnątrz wzdłuż przekątnej, Z 3,5 | OK |
| `ramka_korpus_W_v2.stl` | stadion panelu (60,60): szerokość | panel_pad_d | 9 | 9,000 | 0,000 | promienie z zewnątrz prostopadle do przekątnej, Z 3,5 | OK |
| `ramka_korpus_W_v2.stl` | stadion panelu (60,60): długość | panel_slot_pitch + panel_pad_d | 23,142 | 23,139 | -0,003 | promienie z zewnątrz wzdłuż przekątnej, Z 3,5 | OK |
| `ramka_korpus_P_v2.stl` | stadion panelu (-60,-60): szerokość | panel_pad_d | 9 | 9,000 | 0,000 | promienie z zewnątrz prostopadle do przekątnej, Z 3,5 | OK |
| `ramka_korpus_P_v2.stl` | stadion panelu (-60,-60): długość | panel_slot_pitch + panel_pad_d | 23,142 | 23,139 | -0,003 | promienie z zewnątrz wzdłuż przekątnej, Z 3,5 | OK |
| `ramka_korpus_P_v2.stl` | stadion panelu (60,60): szerokość | panel_pad_d | 9 | 9,000 | 0,000 | promienie z zewnątrz prostopadle do przekątnej, Z 3,5 | OK |
| `ramka_korpus_P_v2.stl` | stadion panelu (60,60): długość | panel_slot_pitch + panel_pad_d | 23,142 | 23,139 | -0,003 | promienie z zewnątrz wzdłuż przekątnej, Z 3,5 | OK |
| `ramka_korpus_W_v2.stl` | skrzynka DC: sufit wewnętrzny Z | dc_pocket: 40 − 2 | 38,000 | 38,000 | 0,000 | promień +Z w świetle | OK |
| `ramka_korpus_W_v2.stl` | kieszeń DC: okno X | dc_pocket_w | 51 | 51,000 | 0,000 | cięciwa X w ścianie tylnej | OK |
| `ramka_korpus_W_v2.stl` | kieszeń DC: okno Z | dc_pocket_h | 24 | 24,000 | 0,000 | cięciwa Z w ścianie tylnej | OK |
| `ramka_korpus_W_v2.stl` | kieszeń DC: dolna krawędź okna Z | dc_pocket_z0 | 14 | 14,000 | 0,000 | promień −Z | OK |
| `ramka_korpus_W_v2.stl` | kieszeń DC: dno w świetle (y) | 100 − dc_pocket_depth | 80 | 80,000 | 0,000 | promień −Y przez okno (plan: skrzynka do y 78, w świetle 20 → 80) | OK |
| `ramka_korpus_W_v2.stl` | kieszeń DC: wnętrze X (ściana lewa skrzynki → prawa) | 4.11: −95,5…−42 | 53,500 | 53,500 | 0,000 | cięciwa X w świetle (poza otworem ø12) | OK |
| `ramka_korpus_W_v2.stl` | kieszeń DC: wnętrze Z (dno → sufit) | dc_pocket: 14…38 | 24,000 | 24,000 | 0,000 | cięciwa Z w świetle | OK |
| `ramka_korpus_P_v2.stl` | skrzynka DC: sufit wewnętrzny Z | dc_pocket: 40 − 2 | 38,000 | 38,000 | 0,000 | promień +Z w świetle | OK |
| `ramka_korpus_P_v2.stl` | kieszeń DC: okno X | dc_pocket_w | 51 | 51,000 | 0,000 | cięciwa X w ścianie tylnej | OK |
| `ramka_korpus_P_v2.stl` | kieszeń DC: okno Z | dc_pocket_h | 24 | 24,000 | 0,000 | cięciwa Z w ścianie tylnej | OK |
| `ramka_korpus_P_v2.stl` | kieszeń DC: dolna krawędź okna Z | dc_pocket_z0 | 14 | 14,000 | 0,000 | promień −Z | OK |
| `ramka_korpus_P_v2.stl` | kieszeń DC: dno w świetle (y) | 100 − dc_pocket_depth | 80 | 80,000 | 0,000 | promień −Y przez okno (plan: skrzynka do y 78, w świetle 20 → 80) | OK |
| `ramka_korpus_P_v2.stl` | kieszeń DC: wnętrze X (ściana lewa skrzynki → prawa) | 4.11: −95,5…−42 | 53,500 | 53,500 | 0,000 | cięciwa X w świetle (poza otworem ø12) | OK |
| `ramka_korpus_P_v2.stl` | kieszeń DC: wnętrze Z (dno → sufit) | dc_pocket: 14…38 | 24,000 | 24,000 | 0,000 | cięciwa Z w świetle | OK |
| `ramka_korpus_W_v2.stl` | okno USB X | usb_cut_w | 16 | 16,000 | -0,000 | cięciwa X | OK |
| `ramka_korpus_W_v2.stl` | okno USB Z | usb_cut_h | 9 | 9,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_W_v2.stl` | rowek flanszy USB lewy: długość X | usb_slot_pitch_min/max + usb_slot_w | 5,700 | 5,691 | -0,009 | cięciwa X | OK |
| `ramka_korpus_W_v2.stl` | rowek flanszy USB lewy: wysokość Z | usb_slot_w | 3,200 | 3,200 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_W_v2.stl` | rowek flanszy USB prawy: długość X | usb_slot_pitch_min/max + usb_slot_w | 5,700 | 5,691 | -0,009 | cięciwa X | OK |
| `ramka_korpus_W_v2.stl` | rowek flanszy USB prawy: wysokość Z | usb_slot_w | 3,200 | 3,200 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_P_v2.stl` | okno USB X | usb_cut_w | 16 | 16,000 | -0,000 | cięciwa X | OK |
| `ramka_korpus_P_v2.stl` | okno USB Z | usb_cut_h | 9 | 9,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_P_v2.stl` | rowek flanszy USB lewy: długość X | usb_slot_pitch_min/max + usb_slot_w | 5,700 | 5,691 | -0,009 | cięciwa X | OK |
| `ramka_korpus_P_v2.stl` | rowek flanszy USB lewy: wysokość Z | usb_slot_w | 3,200 | 3,200 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_P_v2.stl` | rowek flanszy USB prawy: długość X | usb_slot_pitch_min/max + usb_slot_w | 5,700 | 5,691 | -0,009 | cięciwa X | OK |
| `ramka_korpus_P_v2.stl` | rowek flanszy USB prawy: wysokość Z | usb_slot_w | 3,200 | 3,200 | 0,000 | cięciwa Z | OK |
| `ramka_plytka_poranna_n4_v2.stl` | gabaryt X | plate_size | 96 | 96,000 | 0,000 | bbox | OK |
| `ramka_plytka_poranna_n4_v2.stl` | gabaryt Y | plate_size | 96 | 96,000 | 0,000 | bbox | OK |
| `ramka_plytka_poranna_n4_v2.stl` | gabaryt Z | plate_thickness (+ relief 0,6 w n) | 8,600 | 8,600 | 0,000 | bbox | OK |
| `ramka_plytka_poranna_n4_v2.stl` | bok X (promienie) | plate_size | 96 | 96,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_poranna_n4_v2.stl` | bok Y (promienie) | plate_size | 96 | 96,000 | -0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_poranna_n4_v2.stl` | grubość (poza reliefem) | plate_thickness | 8 | 8,000 | -0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_poranna_n4_v2.stl` | wycięcie D: x od | notch_size (48−5) | 43 | 43,000 | 0,000 | promień −X w wycięciu | OK |
| `ramka_plytka_poranna_n4_v2.stl` | wycięcie D: y do | notch_size | -43 | -43,000 | 0,000 | promień +Y w wycięciu | OK |
| `ramka_plytka_poranna_n4_v2.stl` | wycięcie D przelotowe | 4.1 | 0,000 | 0,000 | 0,000 | promień −Z: 0 = przelot | OK |
| `ramka_plytka_poranna_n4_v2.stl` | stożek znacznika A: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_poranna_n4_v2.stl` | stożek znacznika A: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_poranna_n4_v2.stl` | stożek znacznika B: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_poranna_n4_v2.stl` | stożek znacznika B: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_poranna_n4_v2.stl` | stożek znacznika C: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_poranna_n4_v2.stl` | stożek znacznika C: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_poranna_n4_v2.stl` | kieszeń magnesu A: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_n4_v2.stl` | kieszeń magnesu A: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_poranna_n4_v2.stl` | kieszeń magnesu B: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_n4_v2.stl` | kieszeń magnesu B: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_poranna_n4_v2.stl` | kieszeń magnesu C: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_n4_v2.stl` | kieszeń magnesu C: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_poranna_n4_v2.stl` | dołek kodu A (-45,-36): głębokość (brak) | code_dimple_depth / D11 | 0,000 | 0,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_poranna_n4_v2.stl` | dołek kodu B (-45,-33): głębokość (brak) | code_dimple_depth / D11 | 0,000 | 0,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_poranna_n4_v2.stl` | dołek kodu C (-45,-30): głębokość (oczekiwany) | code_dimple_depth / D11 | 1 | 1,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_poranna_n4_v2.stl` | dołek kodu C: ø | code_dimple_d | 2 | 2,000 | 0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_n4_v2.stl` | rowek pokrywki: dno (-X) | cover_groove_depth | 47,200 | 47,200 | 0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_poranna_n4_v2.stl` | rowek pokrywki: dno (X) | cover_groove_depth | -47,200 | -47,200 | -0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_poranna_n4_v2.stl` | rowek pokrywki: dno (-Y) | cover_groove_depth | 47,200 | 47,200 | 0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_poranna_n4_v2.stl` | rowek pokrywki: dno (Y) | cover_groove_depth | -47,200 | -47,200 | -0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_poranna_n4_v2.stl` | rowek pokrywki: wysokość | cover_groove_w | 1,000 | 1,000 | 0,000 | cięciwa Z w rowku | OK |
| `ramka_plytka_poranna_n4_v2.stl` | rowek pokrywki: górna krawędź pod wierzchem | cover_groove_z − w/2 | 1,500 | 1,500 | 0,000 | promień +Z w rowku | OK |
| `ramka_plytka_poranna_n4_v2.stl` | faza górnej krawędzi: x boku na Z −0,25 | plate_top_chamfer | 47,750 | 47,750 | -0,000 | promień −X 0,25 pod wierzchem (faza 0,5 × 45°) | OK |
| `ramka_plytka_poranna_n4_v2.stl` | R pionowej krawędzi (naroże B/C): punkt na przekątnej | plate_edge_r | 47,707 | 47,703 | -0,004 | promień wzdłuż przekątnej narożnika w Z −4 | OK |
| `ramka_plytka_poranna_n4_v2.stl` | rynienka id 36: długość na wierzchu | ev/mo_trough_l | 49,973 | 49,973 | 0,000 | cięciwa X 0,05 pod wierzchem | OK |
| `ramka_plytka_poranna_n4_v2.stl` | rynienka id 36: szerokość na wierzchu | ev/mo_trough_w | 12,973 | 12,973 | 0,000 | cięciwa Y 0,05 pod wierzchem | OK |
| `ramka_plytka_poranna_n4_v2.stl` | rynienka id 36: głębokość | socket_depth | 4 | 4,000 | 0,000 | promień −Z | OK |
| `ramka_plytka_poranna_n4_v2.stl` | rynienka id 36: otwory ø3 przelotowe w rozstawie 10 | trough_hole_count | 4 | 4 | 0 | promienie −Z + cięciwy | OK |
| `ramka_plytka_poranna_n4_v2.stl` | rynienka id 37: długość na wierzchu | ev/mo_trough_l | 49,973 | 49,973 | 0,000 | cięciwa X 0,05 pod wierzchem | OK |
| `ramka_plytka_poranna_n4_v2.stl` | rynienka id 37: szerokość na wierzchu | ev/mo_trough_w | 12,973 | 12,973 | 0,000 | cięciwa Y 0,05 pod wierzchem | OK |
| `ramka_plytka_poranna_n4_v2.stl` | rynienka id 37: głębokość | socket_depth | 4 | 4,000 | 0,000 | promień −Z | OK |
| `ramka_plytka_poranna_n4_v2.stl` | rynienka id 37: otwory ø3 przelotowe w rozstawie 10 | trough_hole_count | 4 | 4 | 0 | promienie −Z + cięciwy | OK |
| `ramka_plytka_poranna_n4_v2.stl` | gniazda okrągłe wg JSON: liczba zgodnych | D6 (35) | 35 | 35 | 0 | wszystkie: przelot ø3, ø wierzchu, dno −4 | OK |
| `ramka_plytka_poranna_n4_v2.stl` | gniazda okrągłe: liczba w JSON | D6 | 35 | 35 | 0 | JSON | OK |
| `ramka_plytka_poranna_n4_v2.stl` | rynienki: liczba w JSON | D6 | 2 | 2 | 0 | JSON | OK |
| `ramka_plytka_poranna_n4_v2.stl` | JSON gniazd = parametry ev/mo_rows | ev_rows/mo_rows | 0 | 0 | 0 | różnica zbiorów pozycji/typów/średnic | OK |
| `ramka_plytka_poranna_n4_v2.stl` | relief cyfry 4: wysokość nad wierzchem | number_relief_h | 0,600 | 0,600 | -0,000 | max trafień −Z w polu 4×4 wokół (39,5, −44,5) | OK |
| `ramka_plytka_poranna_n4_v2.stl` | relief cyfry 4: wysokość znaku (Y) | number_text_h | 5 | 4,750 | -0,250 | skan 0,25 mm | OK |
| `ramka_plytka_poranna_n4_v2.stl` | relief cyfry 4: środek Y | number_pos_y | -44,500 | -44,500 | 0,000 | skan 0,25 mm | OK |
| `ramka_plytka_poranna_n4_v2.stl` | relief cyfry 4: środek X | number_pos_x | 39,500 | 39,500 | 0,000 | skan 0,25 mm | OK |
| `ramka_plytka_poranna_n5_v2.stl` | gabaryt X | plate_size | 96 | 96,000 | 0,000 | bbox | OK |
| `ramka_plytka_poranna_n5_v2.stl` | gabaryt Y | plate_size | 96 | 96,000 | 0,000 | bbox | OK |
| `ramka_plytka_poranna_n5_v2.stl` | gabaryt Z | plate_thickness (+ relief 0,6 w n) | 8,600 | 8,600 | 0,000 | bbox | OK |
| `ramka_plytka_poranna_n5_v2.stl` | bok X (promienie) | plate_size | 96 | 96,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_poranna_n5_v2.stl` | bok Y (promienie) | plate_size | 96 | 96,000 | -0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_poranna_n5_v2.stl` | grubość (poza reliefem) | plate_thickness | 8 | 8,000 | -0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_poranna_n5_v2.stl` | wycięcie D: x od | notch_size (48−5) | 43 | 43,000 | 0,000 | promień −X w wycięciu | OK |
| `ramka_plytka_poranna_n5_v2.stl` | wycięcie D: y do | notch_size | -43 | -43,000 | 0,000 | promień +Y w wycięciu | OK |
| `ramka_plytka_poranna_n5_v2.stl` | wycięcie D przelotowe | 4.1 | 0,000 | 0,000 | 0,000 | promień −Z: 0 = przelot | OK |
| `ramka_plytka_poranna_n5_v2.stl` | stożek znacznika A: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_poranna_n5_v2.stl` | stożek znacznika A: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_poranna_n5_v2.stl` | stożek znacznika B: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_poranna_n5_v2.stl` | stożek znacznika B: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_poranna_n5_v2.stl` | stożek znacznika C: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_poranna_n5_v2.stl` | stożek znacznika C: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_poranna_n5_v2.stl` | kieszeń magnesu A: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_n5_v2.stl` | kieszeń magnesu A: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_poranna_n5_v2.stl` | kieszeń magnesu B: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_n5_v2.stl` | kieszeń magnesu B: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_poranna_n5_v2.stl` | kieszeń magnesu C: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_n5_v2.stl` | kieszeń magnesu C: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_poranna_n5_v2.stl` | dołek kodu A (-45,-36): głębokość (oczekiwany) | code_dimple_depth / D11 | 1 | 1,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_poranna_n5_v2.stl` | dołek kodu A: ø | code_dimple_d | 2 | 2,000 | 0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_n5_v2.stl` | dołek kodu B (-45,-33): głębokość (brak) | code_dimple_depth / D11 | 0,000 | 0,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_poranna_n5_v2.stl` | dołek kodu C (-45,-30): głębokość (oczekiwany) | code_dimple_depth / D11 | 1 | 1,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_poranna_n5_v2.stl` | dołek kodu C: ø | code_dimple_d | 2 | 2,000 | 0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_n5_v2.stl` | rowek pokrywki: dno (-X) | cover_groove_depth | 47,200 | 47,200 | 0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_poranna_n5_v2.stl` | rowek pokrywki: dno (X) | cover_groove_depth | -47,200 | -47,200 | -0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_poranna_n5_v2.stl` | rowek pokrywki: dno (-Y) | cover_groove_depth | 47,200 | 47,200 | 0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_poranna_n5_v2.stl` | rowek pokrywki: dno (Y) | cover_groove_depth | -47,200 | -47,200 | -0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_poranna_n5_v2.stl` | rowek pokrywki: wysokość | cover_groove_w | 1,000 | 1,000 | 0,000 | cięciwa Z w rowku | OK |
| `ramka_plytka_poranna_n5_v2.stl` | rowek pokrywki: górna krawędź pod wierzchem | cover_groove_z − w/2 | 1,500 | 1,500 | 0,000 | promień +Z w rowku | OK |
| `ramka_plytka_poranna_n5_v2.stl` | faza górnej krawędzi: x boku na Z −0,25 | plate_top_chamfer | 47,750 | 47,750 | -0,000 | promień −X 0,25 pod wierzchem (faza 0,5 × 45°) | OK |
| `ramka_plytka_poranna_n5_v2.stl` | R pionowej krawędzi (naroże B/C): punkt na przekątnej | plate_edge_r | 47,707 | 47,703 | -0,004 | promień wzdłuż przekątnej narożnika w Z −4 | OK |
| `ramka_plytka_poranna_n5_v2.stl` | rynienka id 36: długość na wierzchu | ev/mo_trough_l | 49,973 | 49,973 | 0,000 | cięciwa X 0,05 pod wierzchem | OK |
| `ramka_plytka_poranna_n5_v2.stl` | rynienka id 36: szerokość na wierzchu | ev/mo_trough_w | 12,973 | 12,973 | 0,000 | cięciwa Y 0,05 pod wierzchem | OK |
| `ramka_plytka_poranna_n5_v2.stl` | rynienka id 36: głębokość | socket_depth | 4 | 4,000 | 0,000 | promień −Z | OK |
| `ramka_plytka_poranna_n5_v2.stl` | rynienka id 36: otwory ø3 przelotowe w rozstawie 10 | trough_hole_count | 4 | 4 | 0 | promienie −Z + cięciwy | OK |
| `ramka_plytka_poranna_n5_v2.stl` | rynienka id 37: długość na wierzchu | ev/mo_trough_l | 49,973 | 49,973 | 0,000 | cięciwa X 0,05 pod wierzchem | OK |
| `ramka_plytka_poranna_n5_v2.stl` | rynienka id 37: szerokość na wierzchu | ev/mo_trough_w | 12,973 | 12,973 | 0,000 | cięciwa Y 0,05 pod wierzchem | OK |
| `ramka_plytka_poranna_n5_v2.stl` | rynienka id 37: głębokość | socket_depth | 4 | 4,000 | 0,000 | promień −Z | OK |
| `ramka_plytka_poranna_n5_v2.stl` | rynienka id 37: otwory ø3 przelotowe w rozstawie 10 | trough_hole_count | 4 | 4 | 0 | promienie −Z + cięciwy | OK |
| `ramka_plytka_poranna_n5_v2.stl` | gniazda okrągłe wg JSON: liczba zgodnych | D6 (35) | 35 | 35 | 0 | wszystkie: przelot ø3, ø wierzchu, dno −4 | OK |
| `ramka_plytka_poranna_n5_v2.stl` | gniazda okrągłe: liczba w JSON | D6 | 35 | 35 | 0 | JSON | OK |
| `ramka_plytka_poranna_n5_v2.stl` | rynienki: liczba w JSON | D6 | 2 | 2 | 0 | JSON | OK |
| `ramka_plytka_poranna_n5_v2.stl` | JSON gniazd = parametry ev/mo_rows | ev_rows/mo_rows | 0 | 0 | 0 | różnica zbiorów pozycji/typów/średnic | OK |
| `ramka_plytka_poranna_n5_v2.stl` | relief cyfry 5: wysokość nad wierzchem | number_relief_h | 0,600 | 0,600 | -0,000 | max trafień −Z w polu 4×4 wokół (39,5, −44,5) | OK |
| `ramka_plytka_poranna_n5_v2.stl` | relief cyfry 5: wysokość znaku (Y) | number_text_h | 5 | 5,000 | 0,000 | skan 0,25 mm | OK |
| `ramka_plytka_poranna_n5_v2.stl` | relief cyfry 5: środek Y | number_pos_y | -44,500 | -44,625 | -0,125 | skan 0,25 mm | OK |
| `ramka_plytka_poranna_n5_v2.stl` | relief cyfry 5: środek X | number_pos_x | 39,500 | 39,500 | 0,000 | skan 0,25 mm | OK |
| `ramka_plytka_poranna_n6_v2.stl` | gabaryt X | plate_size | 96 | 96,000 | 0,000 | bbox | OK |
| `ramka_plytka_poranna_n6_v2.stl` | gabaryt Y | plate_size | 96 | 96,000 | 0,000 | bbox | OK |
| `ramka_plytka_poranna_n6_v2.stl` | gabaryt Z | plate_thickness (+ relief 0,6 w n) | 8,600 | 8,600 | 0,000 | bbox | OK |
| `ramka_plytka_poranna_n6_v2.stl` | bok X (promienie) | plate_size | 96 | 96,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_poranna_n6_v2.stl` | bok Y (promienie) | plate_size | 96 | 96,000 | -0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_poranna_n6_v2.stl` | grubość (poza reliefem) | plate_thickness | 8 | 8,000 | -0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_poranna_n6_v2.stl` | wycięcie D: x od | notch_size (48−5) | 43 | 43,000 | 0,000 | promień −X w wycięciu | OK |
| `ramka_plytka_poranna_n6_v2.stl` | wycięcie D: y do | notch_size | -43 | -43,000 | 0,000 | promień +Y w wycięciu | OK |
| `ramka_plytka_poranna_n6_v2.stl` | wycięcie D przelotowe | 4.1 | 0,000 | 0,000 | 0,000 | promień −Z: 0 = przelot | OK |
| `ramka_plytka_poranna_n6_v2.stl` | stożek znacznika A: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_poranna_n6_v2.stl` | stożek znacznika A: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_poranna_n6_v2.stl` | stożek znacznika B: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_poranna_n6_v2.stl` | stożek znacznika B: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_poranna_n6_v2.stl` | stożek znacznika C: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_poranna_n6_v2.stl` | stożek znacznika C: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_poranna_n6_v2.stl` | kieszeń magnesu A: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_n6_v2.stl` | kieszeń magnesu A: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_poranna_n6_v2.stl` | kieszeń magnesu B: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_n6_v2.stl` | kieszeń magnesu B: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_poranna_n6_v2.stl` | kieszeń magnesu C: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_n6_v2.stl` | kieszeń magnesu C: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_poranna_n6_v2.stl` | dołek kodu A (-45,-36): głębokość (brak) | code_dimple_depth / D11 | 0,000 | 0,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_poranna_n6_v2.stl` | dołek kodu B (-45,-33): głębokość (oczekiwany) | code_dimple_depth / D11 | 1 | 1,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_poranna_n6_v2.stl` | dołek kodu B: ø | code_dimple_d | 2 | 2,000 | 0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_n6_v2.stl` | dołek kodu C (-45,-30): głębokość (oczekiwany) | code_dimple_depth / D11 | 1 | 1,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_poranna_n6_v2.stl` | dołek kodu C: ø | code_dimple_d | 2 | 2,000 | 0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_n6_v2.stl` | rowek pokrywki: dno (-X) | cover_groove_depth | 47,200 | 47,200 | 0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_poranna_n6_v2.stl` | rowek pokrywki: dno (X) | cover_groove_depth | -47,200 | -47,200 | -0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_poranna_n6_v2.stl` | rowek pokrywki: dno (-Y) | cover_groove_depth | 47,200 | 47,200 | 0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_poranna_n6_v2.stl` | rowek pokrywki: dno (Y) | cover_groove_depth | -47,200 | -47,200 | -0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_poranna_n6_v2.stl` | rowek pokrywki: wysokość | cover_groove_w | 1,000 | 1,000 | 0,000 | cięciwa Z w rowku | OK |
| `ramka_plytka_poranna_n6_v2.stl` | rowek pokrywki: górna krawędź pod wierzchem | cover_groove_z − w/2 | 1,500 | 1,500 | 0,000 | promień +Z w rowku | OK |
| `ramka_plytka_poranna_n6_v2.stl` | faza górnej krawędzi: x boku na Z −0,25 | plate_top_chamfer | 47,750 | 47,750 | -0,000 | promień −X 0,25 pod wierzchem (faza 0,5 × 45°) | OK |
| `ramka_plytka_poranna_n6_v2.stl` | R pionowej krawędzi (naroże B/C): punkt na przekątnej | plate_edge_r | 47,707 | 47,703 | -0,004 | promień wzdłuż przekątnej narożnika w Z −4 | OK |
| `ramka_plytka_poranna_n6_v2.stl` | rynienka id 36: długość na wierzchu | ev/mo_trough_l | 49,973 | 49,973 | 0,000 | cięciwa X 0,05 pod wierzchem | OK |
| `ramka_plytka_poranna_n6_v2.stl` | rynienka id 36: szerokość na wierzchu | ev/mo_trough_w | 12,973 | 12,973 | 0,000 | cięciwa Y 0,05 pod wierzchem | OK |
| `ramka_plytka_poranna_n6_v2.stl` | rynienka id 36: głębokość | socket_depth | 4 | 4,000 | 0,000 | promień −Z | OK |
| `ramka_plytka_poranna_n6_v2.stl` | rynienka id 36: otwory ø3 przelotowe w rozstawie 10 | trough_hole_count | 4 | 4 | 0 | promienie −Z + cięciwy | OK |
| `ramka_plytka_poranna_n6_v2.stl` | rynienka id 37: długość na wierzchu | ev/mo_trough_l | 49,973 | 49,973 | 0,000 | cięciwa X 0,05 pod wierzchem | OK |
| `ramka_plytka_poranna_n6_v2.stl` | rynienka id 37: szerokość na wierzchu | ev/mo_trough_w | 12,973 | 12,973 | 0,000 | cięciwa Y 0,05 pod wierzchem | OK |
| `ramka_plytka_poranna_n6_v2.stl` | rynienka id 37: głębokość | socket_depth | 4 | 4,000 | 0,000 | promień −Z | OK |
| `ramka_plytka_poranna_n6_v2.stl` | rynienka id 37: otwory ø3 przelotowe w rozstawie 10 | trough_hole_count | 4 | 4 | 0 | promienie −Z + cięciwy | OK |
| `ramka_plytka_poranna_n6_v2.stl` | gniazda okrągłe wg JSON: liczba zgodnych | D6 (35) | 35 | 35 | 0 | wszystkie: przelot ø3, ø wierzchu, dno −4 | OK |
| `ramka_plytka_poranna_n6_v2.stl` | gniazda okrągłe: liczba w JSON | D6 | 35 | 35 | 0 | JSON | OK |
| `ramka_plytka_poranna_n6_v2.stl` | rynienki: liczba w JSON | D6 | 2 | 2 | 0 | JSON | OK |
| `ramka_plytka_poranna_n6_v2.stl` | JSON gniazd = parametry ev/mo_rows | ev_rows/mo_rows | 0 | 0 | 0 | różnica zbiorów pozycji/typów/średnic | OK |
| `ramka_plytka_poranna_n6_v2.stl` | relief cyfry 6: wysokość nad wierzchem | number_relief_h | 0,600 | 0,600 | -0,000 | max trafień −Z w polu 4×4 wokół (39,5, −44,5) | OK |
| `ramka_plytka_poranna_n6_v2.stl` | relief cyfry 6: wysokość znaku (Y) | number_text_h | 5 | 5,000 | 0,000 | skan 0,25 mm | OK |
| `ramka_plytka_poranna_n6_v2.stl` | relief cyfry 6: środek Y | number_pos_y | -44,500 | -44,625 | -0,125 | skan 0,25 mm | OK |
| `ramka_plytka_poranna_n6_v2.stl` | relief cyfry 6: środek X | number_pos_x | 39,500 | 39,500 | 0,000 | skan 0,25 mm | OK |
| `ramka_plytka_poranna_v2.stl` | gabaryt X | plate_size | 96 | 96,000 | 0,000 | bbox | OK |
| `ramka_plytka_poranna_v2.stl` | gabaryt Y | plate_size | 96 | 96,000 | 0,000 | bbox | OK |
| `ramka_plytka_poranna_v2.stl` | gabaryt Z | plate_thickness (+ relief 0,6 w n) | 8 | 8,000 | 0,000 | bbox | OK |
| `ramka_plytka_poranna_v2.stl` | bok X (promienie) | plate_size | 96 | 96,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_poranna_v2.stl` | bok Y (promienie) | plate_size | 96 | 96,000 | -0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_poranna_v2.stl` | grubość (poza reliefem) | plate_thickness | 8 | 8,000 | -0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_poranna_v2.stl` | wycięcie D: x od | notch_size (48−5) | 43 | 43,000 | 0,000 | promień −X w wycięciu | OK |
| `ramka_plytka_poranna_v2.stl` | wycięcie D: y do | notch_size | -43 | -43,000 | 0,000 | promień +Y w wycięciu | OK |
| `ramka_plytka_poranna_v2.stl` | wycięcie D przelotowe | 4.1 | 0,000 | 0,000 | 0,000 | promień −Z: 0 = przelot | OK |
| `ramka_plytka_poranna_v2.stl` | stożek znacznika A: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_poranna_v2.stl` | stożek znacznika A: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_poranna_v2.stl` | stożek znacznika B: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_poranna_v2.stl` | stożek znacznika B: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_poranna_v2.stl` | stożek znacznika C: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_poranna_v2.stl` | stożek znacznika C: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_poranna_v2.stl` | kieszeń magnesu A: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_v2.stl` | kieszeń magnesu A: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_poranna_v2.stl` | kieszeń magnesu B: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_v2.stl` | kieszeń magnesu B: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_poranna_v2.stl` | kieszeń magnesu C: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_v2.stl` | kieszeń magnesu C: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_poranna_v2.stl` | dołek kodu A (-45,-36): głębokość (oczekiwany) | code_dimple_depth / D11 | 1 | 1,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_poranna_v2.stl` | dołek kodu A: ø | code_dimple_d | 2 | 2,000 | 0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_v2.stl` | dołek kodu B (-45,-33): głębokość (oczekiwany) | code_dimple_depth / D11 | 1 | 1,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_poranna_v2.stl` | dołek kodu B: ø | code_dimple_d | 2 | 2,000 | 0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_v2.stl` | dołek kodu C (-45,-30): głębokość (oczekiwany) | code_dimple_depth / D11 | 1 | 1,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_poranna_v2.stl` | dołek kodu C: ø | code_dimple_d | 2 | 2,000 | 0,000 | cięciwa X | OK |
| `ramka_plytka_poranna_v2.stl` | rowek pokrywki: dno (-X) | cover_groove_depth | 47,200 | 47,200 | 0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_poranna_v2.stl` | rowek pokrywki: dno (X) | cover_groove_depth | -47,200 | -47,200 | -0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_poranna_v2.stl` | rowek pokrywki: dno (-Y) | cover_groove_depth | 47,200 | 47,200 | 0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_poranna_v2.stl` | rowek pokrywki: dno (Y) | cover_groove_depth | -47,200 | -47,200 | -0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_poranna_v2.stl` | rowek pokrywki: wysokość | cover_groove_w | 1,000 | 1,000 | 0,000 | cięciwa Z w rowku | OK |
| `ramka_plytka_poranna_v2.stl` | rowek pokrywki: górna krawędź pod wierzchem | cover_groove_z − w/2 | 1,500 | 1,500 | 0,000 | promień +Z w rowku | OK |
| `ramka_plytka_poranna_v2.stl` | faza górnej krawędzi: x boku na Z −0,25 | plate_top_chamfer | 47,750 | 47,750 | -0,000 | promień −X 0,25 pod wierzchem (faza 0,5 × 45°) | OK |
| `ramka_plytka_poranna_v2.stl` | R pionowej krawędzi (naroże B/C): punkt na przekątnej | plate_edge_r | 47,707 | 47,703 | -0,004 | promień wzdłuż przekątnej narożnika w Z −4 | OK |
| `ramka_plytka_poranna_v2.stl` | rynienka id 36: długość na wierzchu | ev/mo_trough_l | 49,973 | 49,973 | 0,000 | cięciwa X 0,05 pod wierzchem | OK |
| `ramka_plytka_poranna_v2.stl` | rynienka id 36: szerokość na wierzchu | ev/mo_trough_w | 12,973 | 12,973 | 0,000 | cięciwa Y 0,05 pod wierzchem | OK |
| `ramka_plytka_poranna_v2.stl` | rynienka id 36: głębokość | socket_depth | 4 | 4,000 | 0,000 | promień −Z | OK |
| `ramka_plytka_poranna_v2.stl` | rynienka id 36: otwory ø3 przelotowe w rozstawie 10 | trough_hole_count | 4 | 4 | 0 | promienie −Z + cięciwy | OK |
| `ramka_plytka_poranna_v2.stl` | rynienka id 37: długość na wierzchu | ev/mo_trough_l | 49,973 | 49,973 | 0,000 | cięciwa X 0,05 pod wierzchem | OK |
| `ramka_plytka_poranna_v2.stl` | rynienka id 37: szerokość na wierzchu | ev/mo_trough_w | 12,973 | 12,973 | 0,000 | cięciwa Y 0,05 pod wierzchem | OK |
| `ramka_plytka_poranna_v2.stl` | rynienka id 37: głębokość | socket_depth | 4 | 4,000 | 0,000 | promień −Z | OK |
| `ramka_plytka_poranna_v2.stl` | rynienka id 37: otwory ø3 przelotowe w rozstawie 10 | trough_hole_count | 4 | 4 | 0 | promienie −Z + cięciwy | OK |
| `ramka_plytka_poranna_v2.stl` | gniazda okrągłe wg JSON: liczba zgodnych | D6 (35) | 35 | 35 | 0 | wszystkie: przelot ø3, ø wierzchu, dno −4 | OK |
| `ramka_plytka_poranna_v2.stl` | gniazda okrągłe: liczba w JSON | D6 | 35 | 35 | 0 | JSON | OK |
| `ramka_plytka_poranna_v2.stl` | rynienki: liczba w JSON | D6 | 2 | 2 | 0 | JSON | OK |
| `ramka_plytka_poranna_v2.stl` | JSON gniazd = parametry ev/mo_rows | ev_rows/mo_rows | 0 | 0 | 0 | różnica zbiorów pozycji/typów/średnic | OK |
| `ramka_plytka_poranna_v2.stl` | plik bazowy: brak reliefu (Z max = 8,0) | 4.1 (R4) | 0,000 | 0,000 | 0,000 | bbox | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | gabaryt X | plate_size | 96 | 96,000 | 0,000 | bbox | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | gabaryt Y | plate_size | 96 | 96,000 | 0,000 | bbox | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | gabaryt Z | plate_thickness (+ relief 0,6 w n) | 8,600 | 8,600 | 0,000 | bbox | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | bok X (promienie) | plate_size | 96 | 96,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | bok Y (promienie) | plate_size | 96 | 96,000 | -0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | grubość (poza reliefem) | plate_thickness | 8 | 8,000 | -0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | wycięcie D: x od | notch_size (48−5) | 43 | 43,000 | 0,000 | promień −X w wycięciu | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | wycięcie D: y do | notch_size | -43 | -43,000 | 0,000 | promień +Y w wycięciu | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | wycięcie D przelotowe | 4.1 | 0,000 | 0,000 | 0,000 | promień −Z: 0 = przelot | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | stożek znacznika A: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | stożek znacznika A: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | stożek znacznika B: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | stożek znacznika B: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | stożek znacznika C: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | stożek znacznika C: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | kieszeń magnesu A: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | kieszeń magnesu A: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | kieszeń magnesu B: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | kieszeń magnesu B: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | kieszeń magnesu C: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | kieszeń magnesu C: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | dołek kodu A (-45,-36): głębokość (oczekiwany) | code_dimple_depth / D11 | 1 | 1,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | dołek kodu A: ø | code_dimple_d | 2 | 2,000 | 0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | dołek kodu B (-45,-33): głębokość (brak) | code_dimple_depth / D11 | 0,000 | 0,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | dołek kodu C (-45,-30): głębokość (brak) | code_dimple_depth / D11 | 0,000 | 0,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | rowek pokrywki: dno (-X) | cover_groove_depth | 47,200 | 47,200 | 0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | rowek pokrywki: dno (X) | cover_groove_depth | -47,200 | -47,200 | -0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | rowek pokrywki: dno (-Y) | cover_groove_depth | 47,200 | 47,200 | 0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | rowek pokrywki: dno (Y) | cover_groove_depth | -47,200 | -47,200 | -0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | rowek pokrywki: wysokość | cover_groove_w | 1,000 | 1,000 | 0,000 | cięciwa Z w rowku | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | rowek pokrywki: górna krawędź pod wierzchem | cover_groove_z − w/2 | 1,500 | 1,500 | 0,000 | promień +Z w rowku | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | faza górnej krawędzi: x boku na Z −0,25 | plate_top_chamfer | 47,750 | 47,750 | -0,000 | promień −X 0,25 pod wierzchem (faza 0,5 × 45°) | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | R pionowej krawędzi (naroże B/C): punkt na przekątnej | plate_edge_r | 47,707 | 47,703 | -0,004 | promień wzdłuż przekątnej narożnika w Z −4 | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | rynienka id 25: długość na wierzchu | ev/mo_trough_l | 59,973 | 59,971 | -0,002 | cięciwa X 0,05 pod wierzchem | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | rynienka id 25: szerokość na wierzchu | ev/mo_trough_w | 14,973 | 14,973 | 0,000 | cięciwa Y 0,05 pod wierzchem | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | rynienka id 25: głębokość | socket_depth | 4 | 4,000 | 0,000 | promień −Z | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | rynienka id 25: otwory ø3 przelotowe w rozstawie 12 | trough_hole_count | 4 | 4 | 0 | promienie −Z + cięciwy | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | rynienka id 26: długość na wierzchu | ev/mo_trough_l | 59,973 | 59,971 | -0,002 | cięciwa X 0,05 pod wierzchem | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | rynienka id 26: szerokość na wierzchu | ev/mo_trough_w | 14,973 | 14,973 | 0,000 | cięciwa Y 0,05 pod wierzchem | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | rynienka id 26: głębokość | socket_depth | 4 | 4,000 | 0,000 | promień −Z | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | rynienka id 26: otwory ø3 przelotowe w rozstawie 12 | trough_hole_count | 4 | 4 | 0 | promienie −Z + cięciwy | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | gniazda okrągłe wg JSON: liczba zgodnych | D6 (24) | 24 | 24 | 0 | wszystkie: przelot ø3, ø wierzchu, dno −4 | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | gniazda okrągłe: liczba w JSON | D6 | 24 | 24 | 0 | JSON | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | rynienki: liczba w JSON | D6 | 2 | 2 | 0 | JSON | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | JSON gniazd = parametry ev/mo_rows | ev_rows/mo_rows | 0 | 0 | 0 | różnica zbiorów pozycji/typów/średnic | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | relief cyfry 1: wysokość nad wierzchem | number_relief_h | 0,600 | 0,600 | -0,000 | max trafień −Z w polu 4×4 wokół (39,5, −44,5) | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | relief cyfry 1: wysokość znaku (Y) | number_text_h | 5 | 4,750 | -0,250 | skan 0,25 mm | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | relief cyfry 1: środek Y | number_pos_y | -44,500 | -44,500 | 0,000 | skan 0,25 mm | OK |
| `ramka_plytka_wieczorna_n1_v2.stl` | relief cyfry 1: środek X | number_pos_x | 39,500 | 39,500 | 0,000 | skan 0,25 mm | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | gabaryt X | plate_size | 96 | 96,000 | 0,000 | bbox | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | gabaryt Y | plate_size | 96 | 96,000 | 0,000 | bbox | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | gabaryt Z | plate_thickness (+ relief 0,6 w n) | 8,600 | 8,600 | 0,000 | bbox | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | bok X (promienie) | plate_size | 96 | 96,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | bok Y (promienie) | plate_size | 96 | 96,000 | -0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | grubość (poza reliefem) | plate_thickness | 8 | 8,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | wycięcie D: x od | notch_size (48−5) | 43 | 43,000 | 0,000 | promień −X w wycięciu | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | wycięcie D: y do | notch_size | -43 | -43,000 | 0,000 | promień +Y w wycięciu | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | wycięcie D przelotowe | 4.1 | 0,000 | 0,000 | 0,000 | promień −Z: 0 = przelot | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | stożek znacznika A: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | stożek znacznika A: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | stożek znacznika B: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | stożek znacznika B: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | stożek znacznika C: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | stożek znacznika C: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | kieszeń magnesu A: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | kieszeń magnesu A: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | kieszeń magnesu B: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | kieszeń magnesu B: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | kieszeń magnesu C: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | kieszeń magnesu C: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | dołek kodu A (-45,-36): głębokość (brak) | code_dimple_depth / D11 | 0,000 | 0,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | dołek kodu B (-45,-33): głębokość (oczekiwany) | code_dimple_depth / D11 | 1 | 1,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | dołek kodu B: ø | code_dimple_d | 2 | 2,000 | 0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | dołek kodu C (-45,-30): głębokość (brak) | code_dimple_depth / D11 | 0,000 | 0,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | rowek pokrywki: dno (-X) | cover_groove_depth | 47,200 | 47,200 | 0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | rowek pokrywki: dno (X) | cover_groove_depth | -47,200 | -47,200 | -0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | rowek pokrywki: dno (-Y) | cover_groove_depth | 47,200 | 47,200 | 0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | rowek pokrywki: dno (Y) | cover_groove_depth | -47,200 | -47,200 | -0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | rowek pokrywki: wysokość | cover_groove_w | 1,000 | 1,000 | 0,000 | cięciwa Z w rowku | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | rowek pokrywki: górna krawędź pod wierzchem | cover_groove_z − w/2 | 1,500 | 1,500 | 0,000 | promień +Z w rowku | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | faza górnej krawędzi: x boku na Z −0,25 | plate_top_chamfer | 47,750 | 47,750 | -0,000 | promień −X 0,25 pod wierzchem (faza 0,5 × 45°) | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | R pionowej krawędzi (naroże B/C): punkt na przekątnej | plate_edge_r | 47,707 | 47,703 | -0,004 | promień wzdłuż przekątnej narożnika w Z −4 | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | rynienka id 25: długość na wierzchu | ev/mo_trough_l | 59,973 | 59,971 | -0,002 | cięciwa X 0,05 pod wierzchem | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | rynienka id 25: szerokość na wierzchu | ev/mo_trough_w | 14,973 | 14,973 | 0,000 | cięciwa Y 0,05 pod wierzchem | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | rynienka id 25: głębokość | socket_depth | 4 | 4,000 | 0,000 | promień −Z | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | rynienka id 25: otwory ø3 przelotowe w rozstawie 12 | trough_hole_count | 4 | 4 | 0 | promienie −Z + cięciwy | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | rynienka id 26: długość na wierzchu | ev/mo_trough_l | 59,973 | 59,971 | -0,002 | cięciwa X 0,05 pod wierzchem | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | rynienka id 26: szerokość na wierzchu | ev/mo_trough_w | 14,973 | 14,973 | 0,000 | cięciwa Y 0,05 pod wierzchem | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | rynienka id 26: głębokość | socket_depth | 4 | 4,000 | 0,000 | promień −Z | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | rynienka id 26: otwory ø3 przelotowe w rozstawie 12 | trough_hole_count | 4 | 4 | 0 | promienie −Z + cięciwy | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | gniazda okrągłe wg JSON: liczba zgodnych | D6 (24) | 24 | 24 | 0 | wszystkie: przelot ø3, ø wierzchu, dno −4 | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | gniazda okrągłe: liczba w JSON | D6 | 24 | 24 | 0 | JSON | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | rynienki: liczba w JSON | D6 | 2 | 2 | 0 | JSON | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | JSON gniazd = parametry ev/mo_rows | ev_rows/mo_rows | 0 | 0 | 0 | różnica zbiorów pozycji/typów/średnic | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | relief cyfry 2: wysokość nad wierzchem | number_relief_h | 0,600 | 0,600 | -0,000 | max trafień −Z w polu 4×4 wokół (39,5, −44,5) | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | relief cyfry 2: wysokość znaku (Y) | number_text_h | 5 | 5,000 | 0,000 | skan 0,25 mm | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | relief cyfry 2: środek Y | number_pos_y | -44,500 | -44,375 | 0,125 | skan 0,25 mm | OK |
| `ramka_plytka_wieczorna_n2_v2.stl` | relief cyfry 2: środek X | number_pos_x | 39,500 | 39,500 | 0,000 | skan 0,25 mm | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | gabaryt X | plate_size | 96 | 96,000 | 0,000 | bbox | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | gabaryt Y | plate_size | 96 | 96,000 | 0,000 | bbox | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | gabaryt Z | plate_thickness (+ relief 0,6 w n) | 8,600 | 8,600 | 0,000 | bbox | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | bok X (promienie) | plate_size | 96 | 96,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | bok Y (promienie) | plate_size | 96 | 96,000 | -0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | grubość (poza reliefem) | plate_thickness | 8 | 8,000 | -0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | wycięcie D: x od | notch_size (48−5) | 43 | 43,000 | 0,000 | promień −X w wycięciu | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | wycięcie D: y do | notch_size | -43 | -43,000 | 0,000 | promień +Y w wycięciu | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | wycięcie D przelotowe | 4.1 | 0,000 | 0,000 | 0,000 | promień −Z: 0 = przelot | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | stożek znacznika A: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | stożek znacznika A: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | stożek znacznika B: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | stożek znacznika B: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | stożek znacznika C: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | stożek znacznika C: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | kieszeń magnesu A: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | kieszeń magnesu A: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | kieszeń magnesu B: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | kieszeń magnesu B: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | kieszeń magnesu C: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | kieszeń magnesu C: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | dołek kodu A (-45,-36): głębokość (oczekiwany) | code_dimple_depth / D11 | 1 | 1,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | dołek kodu A: ø | code_dimple_d | 2 | 2,000 | 0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | dołek kodu B (-45,-33): głębokość (oczekiwany) | code_dimple_depth / D11 | 1 | 1,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | dołek kodu B: ø | code_dimple_d | 2 | 2,000 | 0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | dołek kodu C (-45,-30): głębokość (brak) | code_dimple_depth / D11 | 0,000 | 0,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | rowek pokrywki: dno (-X) | cover_groove_depth | 47,200 | 47,200 | 0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | rowek pokrywki: dno (X) | cover_groove_depth | -47,200 | -47,200 | -0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | rowek pokrywki: dno (-Y) | cover_groove_depth | 47,200 | 47,200 | 0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | rowek pokrywki: dno (Y) | cover_groove_depth | -47,200 | -47,200 | -0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | rowek pokrywki: wysokość | cover_groove_w | 1,000 | 1,000 | 0,000 | cięciwa Z w rowku | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | rowek pokrywki: górna krawędź pod wierzchem | cover_groove_z − w/2 | 1,500 | 1,500 | 0,000 | promień +Z w rowku | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | faza górnej krawędzi: x boku na Z −0,25 | plate_top_chamfer | 47,750 | 47,750 | -0,000 | promień −X 0,25 pod wierzchem (faza 0,5 × 45°) | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | R pionowej krawędzi (naroże B/C): punkt na przekątnej | plate_edge_r | 47,707 | 47,703 | -0,004 | promień wzdłuż przekątnej narożnika w Z −4 | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | rynienka id 25: długość na wierzchu | ev/mo_trough_l | 59,973 | 59,971 | -0,002 | cięciwa X 0,05 pod wierzchem | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | rynienka id 25: szerokość na wierzchu | ev/mo_trough_w | 14,973 | 14,973 | 0,000 | cięciwa Y 0,05 pod wierzchem | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | rynienka id 25: głębokość | socket_depth | 4 | 4,000 | 0,000 | promień −Z | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | rynienka id 25: otwory ø3 przelotowe w rozstawie 12 | trough_hole_count | 4 | 4 | 0 | promienie −Z + cięciwy | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | rynienka id 26: długość na wierzchu | ev/mo_trough_l | 59,973 | 59,971 | -0,002 | cięciwa X 0,05 pod wierzchem | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | rynienka id 26: szerokość na wierzchu | ev/mo_trough_w | 14,973 | 14,973 | 0,000 | cięciwa Y 0,05 pod wierzchem | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | rynienka id 26: głębokość | socket_depth | 4 | 4,000 | 0,000 | promień −Z | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | rynienka id 26: otwory ø3 przelotowe w rozstawie 12 | trough_hole_count | 4 | 4 | 0 | promienie −Z + cięciwy | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | gniazda okrągłe wg JSON: liczba zgodnych | D6 (24) | 24 | 24 | 0 | wszystkie: przelot ø3, ø wierzchu, dno −4 | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | gniazda okrągłe: liczba w JSON | D6 | 24 | 24 | 0 | JSON | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | rynienki: liczba w JSON | D6 | 2 | 2 | 0 | JSON | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | JSON gniazd = parametry ev/mo_rows | ev_rows/mo_rows | 0 | 0 | 0 | różnica zbiorów pozycji/typów/średnic | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | relief cyfry 3: wysokość nad wierzchem | number_relief_h | 0,600 | 0,600 | -0,000 | max trafień −Z w polu 4×4 wokół (39,5, −44,5) | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | relief cyfry 3: wysokość znaku (Y) | number_text_h | 5 | 5,000 | 0,000 | skan 0,25 mm | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | relief cyfry 3: środek Y | number_pos_y | -44,500 | -44,625 | -0,125 | skan 0,25 mm | OK |
| `ramka_plytka_wieczorna_n3_v2.stl` | relief cyfry 3: środek X | number_pos_x | 39,500 | 39,500 | 0,000 | skan 0,25 mm | OK |
| `ramka_plytka_wieczorna_v2.stl` | gabaryt X | plate_size | 96 | 96,000 | 0,000 | bbox | OK |
| `ramka_plytka_wieczorna_v2.stl` | gabaryt Y | plate_size | 96 | 96,000 | 0,000 | bbox | OK |
| `ramka_plytka_wieczorna_v2.stl` | gabaryt Z | plate_thickness (+ relief 0,6 w n) | 8 | 8,000 | 0,000 | bbox | OK |
| `ramka_plytka_wieczorna_v2.stl` | bok X (promienie) | plate_size | 96 | 96,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_wieczorna_v2.stl` | bok Y (promienie) | plate_size | 96 | 96,000 | -0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_wieczorna_v2.stl` | grubość (poza reliefem) | plate_thickness | 8 | 8,000 | -0,000 | promienie z zewnątrz | OK |
| `ramka_plytka_wieczorna_v2.stl` | wycięcie D: x od | notch_size (48−5) | 43 | 43,000 | 0,000 | promień −X w wycięciu | OK |
| `ramka_plytka_wieczorna_v2.stl` | wycięcie D: y do | notch_size | -43 | -43,000 | 0,000 | promień +Y w wycięciu | OK |
| `ramka_plytka_wieczorna_v2.stl` | wycięcie D przelotowe | 4.1 | 0,000 | 0,000 | 0,000 | promień −Z: 0 = przelot | OK |
| `ramka_plytka_wieczorna_v2.stl` | stożek znacznika A: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_wieczorna_v2.stl` | stożek znacznika A: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_wieczorna_v2.stl` | stożek znacznika B: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_wieczorna_v2.stl` | stożek znacznika B: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_wieczorna_v2.stl` | stożek znacznika C: ø 0,05 pod wierzchem | marker_cone_d | 4,917 | 4,914 | -0,003 | cięciwa X (stożek ø5 × 3 → 4,917) | OK |
| `ramka_plytka_wieczorna_v2.stl` | stożek znacznika C: głębokość | marker_cone_depth | 3 | 3,000 | 0,000 | promień −Z w osi | OK |
| `ramka_plytka_wieczorna_v2.stl` | kieszeń magnesu A: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_v2.stl` | kieszeń magnesu A: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_wieczorna_v2.stl` | kieszeń magnesu B: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_v2.stl` | kieszeń magnesu B: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_wieczorna_v2.stl` | kieszeń magnesu C: ø | magnet_pocket_d | 5,200 | 5,200 | -0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_v2.stl` | kieszeń magnesu C: głębokość | magnet_pocket_depth | 2,200 | 2,200 | -0,000 | promień +Z do sufitu | OK |
| `ramka_plytka_wieczorna_v2.stl` | dołek kodu A (-45,-36): głębokość (oczekiwany) | code_dimple_depth / D11 | 1 | 1,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_wieczorna_v2.stl` | dołek kodu A: ø | code_dimple_d | 2 | 2,000 | 0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_v2.stl` | dołek kodu B (-45,-33): głębokość (oczekiwany) | code_dimple_depth / D11 | 1 | 1,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_wieczorna_v2.stl` | dołek kodu B: ø | code_dimple_d | 2 | 2,000 | 0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_v2.stl` | dołek kodu C (-45,-30): głębokość (oczekiwany) | code_dimple_depth / D11 | 1 | 1,000 | 0,000 | promień −Z w osi dołka | OK |
| `ramka_plytka_wieczorna_v2.stl` | dołek kodu C: ø | code_dimple_d | 2 | 2,000 | 0,000 | cięciwa X | OK |
| `ramka_plytka_wieczorna_v2.stl` | rowek pokrywki: dno (-X) | cover_groove_depth | 47,200 | 47,200 | 0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_wieczorna_v2.stl` | rowek pokrywki: dno (X) | cover_groove_depth | -47,200 | -47,200 | -0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_wieczorna_v2.stl` | rowek pokrywki: dno (-Y) | cover_groove_depth | 47,200 | 47,200 | 0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_wieczorna_v2.stl` | rowek pokrywki: dno (Y) | cover_groove_depth | -47,200 | -47,200 | -0,000 | promień poziomy w Z −2 | OK |
| `ramka_plytka_wieczorna_v2.stl` | rowek pokrywki: wysokość | cover_groove_w | 1,000 | 1,000 | 0,000 | cięciwa Z w rowku | OK |
| `ramka_plytka_wieczorna_v2.stl` | rowek pokrywki: górna krawędź pod wierzchem | cover_groove_z − w/2 | 1,500 | 1,500 | 0,000 | promień +Z w rowku | OK |
| `ramka_plytka_wieczorna_v2.stl` | faza górnej krawędzi: x boku na Z −0,25 | plate_top_chamfer | 47,750 | 47,750 | -0,000 | promień −X 0,25 pod wierzchem (faza 0,5 × 45°) | OK |
| `ramka_plytka_wieczorna_v2.stl` | R pionowej krawędzi (naroże B/C): punkt na przekątnej | plate_edge_r | 47,707 | 47,703 | -0,004 | promień wzdłuż przekątnej narożnika w Z −4 | OK |
| `ramka_plytka_wieczorna_v2.stl` | rynienka id 25: długość na wierzchu | ev/mo_trough_l | 59,973 | 59,971 | -0,002 | cięciwa X 0,05 pod wierzchem | OK |
| `ramka_plytka_wieczorna_v2.stl` | rynienka id 25: szerokość na wierzchu | ev/mo_trough_w | 14,973 | 14,973 | 0,000 | cięciwa Y 0,05 pod wierzchem | OK |
| `ramka_plytka_wieczorna_v2.stl` | rynienka id 25: głębokość | socket_depth | 4 | 4,000 | 0,000 | promień −Z | OK |
| `ramka_plytka_wieczorna_v2.stl` | rynienka id 25: otwory ø3 przelotowe w rozstawie 12 | trough_hole_count | 4 | 4 | 0 | promienie −Z + cięciwy | OK |
| `ramka_plytka_wieczorna_v2.stl` | rynienka id 26: długość na wierzchu | ev/mo_trough_l | 59,973 | 59,971 | -0,002 | cięciwa X 0,05 pod wierzchem | OK |
| `ramka_plytka_wieczorna_v2.stl` | rynienka id 26: szerokość na wierzchu | ev/mo_trough_w | 14,973 | 14,973 | 0,000 | cięciwa Y 0,05 pod wierzchem | OK |
| `ramka_plytka_wieczorna_v2.stl` | rynienka id 26: głębokość | socket_depth | 4 | 4,000 | 0,000 | promień −Z | OK |
| `ramka_plytka_wieczorna_v2.stl` | rynienka id 26: otwory ø3 przelotowe w rozstawie 12 | trough_hole_count | 4 | 4 | 0 | promienie −Z + cięciwy | OK |
| `ramka_plytka_wieczorna_v2.stl` | gniazda okrągłe wg JSON: liczba zgodnych | D6 (24) | 24 | 24 | 0 | wszystkie: przelot ø3, ø wierzchu, dno −4 | OK |
| `ramka_plytka_wieczorna_v2.stl` | gniazda okrągłe: liczba w JSON | D6 | 24 | 24 | 0 | JSON | OK |
| `ramka_plytka_wieczorna_v2.stl` | rynienki: liczba w JSON | D6 | 2 | 2 | 0 | JSON | OK |
| `ramka_plytka_wieczorna_v2.stl` | JSON gniazd = parametry ev/mo_rows | ev_rows/mo_rows | 0 | 0 | 0 | różnica zbiorów pozycji/typów/średnic | OK |
| `ramka_plytka_wieczorna_v2.stl` | plik bazowy: brak reliefu (Z max = 8,0) | 4.1 (R4) | 0,000 | 0,000 | 0,000 | bbox | OK |
| `ramka_pokrywka_v2.stl` | gabaryt X | plate_size + 2·cover_clearance + 2·cover_skirt_t | 99,600 | 99,600 | -0,000 | bbox | OK |
| `ramka_pokrywka_v2.stl` | gabaryt Y | j.w. | 99,600 | 99,600 | -0,000 | bbox | OK |
| `ramka_pokrywka_v2.stl` | gabaryt Z | cover_inner_h + cover_top_t + cover_skirt_below | 20 | 20,000 | 0,000 | bbox | OK |
| `ramka_pokrywka_v2.stl` | wnęka X | plate_size + 2·cover_clearance | 96,600 | 96,600 | -0,000 | cięciwa X | OK |
| `ramka_pokrywka_v2.stl` | wnęka Y | j.w. | 96,600 | 96,600 | -0,000 | cięciwa Y | OK |
| `ramka_pokrywka_v2.stl` | grubość wierzchu | cover_top_t | 2 | 2,000 | 0,000 | cięciwa Z w materiale | OK |
| `ramka_pokrywka_v2.stl` | wierzch płaski (bez reliefu, R50‑U14) | 4.2 | 90,100 | 90,100 | -0,000 | promień −Z | OK |
| `ramka_pokrywka_v2.stl` | wierzch pełny (bez otworów, R50‑U17) | 4.2 | 1,000 | 1,000 | 0,000 | promień −Z w dawnym otworze: 1 = materiał | OK |
| `ramka_pokrywka_v2.stl` | garb prawy: czubek | 48,3 − cover_snap_bump | 47,600 | 47,600 | -0,000 | promień poziomy w Z garbu | OK |
| `ramka_pokrywka_v2.stl` | garb prawy: szerokość | cover_snap_w | 10 | 10,000 | -0,000 | cięciwa 0,5 za czubkiem (w korpusie garbu) | OK |
| `ramka_pokrywka_v2.stl` | garb prawy: wysokość Z | cover_snap_hgt | 0,800 | 0,800 | 0,000 | cięciwa Z 0,5 za czubkiem | OK |
| `ramka_pokrywka_v2.stl` | garb prawy: środek Z (lokalnie −18) | cover_snap_z | 72,100 | 72,100 | -0,000 | środek cięciwy Z | OK |
| `ramka_pokrywka_v2.stl` | garb lewy: czubek | 48,3 − cover_snap_bump | 47,600 | 47,600 | -0,000 | promień poziomy w Z garbu | OK |
| `ramka_pokrywka_v2.stl` | garb lewy: szerokość | cover_snap_w | 10 | 10,000 | -0,000 | cięciwa 0,5 za czubkiem (w korpusie garbu) | OK |
| `ramka_pokrywka_v2.stl` | garb lewy: wysokość Z | cover_snap_hgt | 0,800 | 0,800 | 0,000 | cięciwa Z 0,5 za czubkiem | OK |
| `ramka_pokrywka_v2.stl` | garb lewy: środek Z (lokalnie −18) | cover_snap_z | 72,100 | 72,100 | -0,000 | środek cięciwy Z | OK |
| `ramka_pokrywka_v2.stl` | garb przedni: czubek | 48,3 − cover_snap_bump | 47,600 | 47,600 | 0,000 | promień poziomy w Z garbu | OK |
| `ramka_pokrywka_v2.stl` | garb przedni: szerokość | cover_snap_w | 10 | 10,000 | 0,000 | cięciwa 0,5 za czubkiem (w korpusie garbu) | OK |
| `ramka_pokrywka_v2.stl` | garb przedni: wysokość Z | cover_snap_hgt | 0,800 | 0,800 | -0,000 | cięciwa Z 0,5 za czubkiem | OK |
| `ramka_pokrywka_v2.stl` | garb przedni: środek Z (lokalnie −18) | cover_snap_z | 72,100 | 72,100 | 0,000 | środek cięciwy Z | OK |
| `ramka_pokrywka_v2.stl` | garb tylny: czubek | 48,3 − cover_snap_bump | 47,600 | 47,600 | 0,000 | promień poziomy w Z garbu | OK |
| `ramka_pokrywka_v2.stl` | garb tylny: szerokość | cover_snap_w | 10 | 10,000 | 0,000 | cięciwa 0,5 za czubkiem (w korpusie garbu) | OK |
| `ramka_pokrywka_v2.stl` | garb tylny: wysokość Z | cover_snap_hgt | 0,800 | 0,800 | -0,000 | cięciwa Z 0,5 za czubkiem | OK |
| `ramka_pokrywka_v2.stl` | garb tylny: środek Z (lokalnie −18) | cover_snap_z | 72,100 | 72,100 | -0,000 | środek cięciwy Z | OK |
| `ramka_pokrywka_v2.stl` | wycięcie palcowe przedni: szerokość | cover_finger_w | 30 | 30,000 | 0,000 | cięciwa X | OK |
| `ramka_pokrywka_v2.stl` | wycięcie palcowe przedni: wysokość | cover_finger_h | 3 | 3,000 | 0,000 | promień +Z od dołu | OK |
| `ramka_pokrywka_v2.stl` | wycięcie palcowe tylny: szerokość | cover_finger_w | 30 | 30,000 | 0,000 | cięciwa X | OK |
| `ramka_pokrywka_v2.stl` | wycięcie palcowe tylny: wysokość | cover_finger_h | 3 | 3,000 | -0,000 | promień +Z od dołu | OK |
| `ramka_pokrywka_v2.stl` | R pionowej krawędzi 3: punkt na przekątnej | cover_corner_r | 48,921 | 48,920 | -0,002 | promień wzdłuż przekątnej | OK |
| `ramka_wkladka_v2.stl` | gabaryt X | 2·65 (uszy) | 130,000 | 130,000 | 0,000 | bbox | OK |
| `ramka_wkladka_v2.stl` | gabaryt Y | 52,3 + tab_end_y | 148,300 | 148,300 | -0,000 | bbox | OK |
| `ramka_wkladka_v2.stl` | gabaryt Z | tab_pin_h + insert_shelf_h + orient_post_h | 11,000 | 11,000 | 0,000 | bbox | OK |
| `ramka_wkladka_v2.stl` | rama zewn. X | insert_opening + 2·insert_wall_w | 104,600 | 104,600 | -0,000 | promienie z zewnątrz | OK |
| `ramka_wkladka_v2.stl` | rama zewn. Y (x=20) | j.w. | 104,600 | 104,600 | -0,000 | promienie z zewnątrz | OK |
| `ramka_wkladka_v2.stl` | otwór X | insert_opening | 96,600 | 96,600 | -0,000 | cięciwa X | OK |
| `ramka_wkladka_v2.stl` | otwór Y (x=20) | insert_opening | 96,600 | 96,600 | -0,000 | cięciwa Y | OK |
| `ramka_wkladka_v2.stl` | otwór: naroże ostre (x przy y=48,1) | insert_opening_r 0 | 48,300 | 48,300 | 0,000 | promień +X | OK |
| `ramka_wkladka_v2.stl` | wysokość ramy | insert_h | 6 | 6,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_wkladka_v2.stl` | faza górnej krawędzi wewn. 1×45°: x na Z 6−0,5 | insert_chamfer | 48,800 | 48,800 | -0,000 | promień +X 0,5 pod wierzchem | OK |
| `ramka_wkladka_v2.stl` | półka A: wierzch Z | insert_shelf_h | 66,100 | 66,100 | -0,000 | promień −Z | OK |
| `ramka_wkladka_v2.stl` | półka A: grubość | insert_shelf_h | 2,500 | 2,500 | -0,000 | promienie z zewnątrz | OK |
| `ramka_wkladka_v2.stl` | półka A: zasięg 12 od ściany otworu | insert_shelf | 36,300 | 36,300 | 0,000 | promień poziomy od x=0 do krawędzi półki | OK |
| `ramka_wkladka_v2.stl` | półka B: wierzch Z | insert_shelf_h | 66,100 | 66,100 | -0,000 | promień −Z | OK |
| `ramka_wkladka_v2.stl` | półka B: grubość | insert_shelf_h | 2,500 | 2,500 | -0,000 | promienie z zewnątrz | OK |
| `ramka_wkladka_v2.stl` | półka B: zasięg 12 od ściany otworu | insert_shelf | 36,300 | 36,300 | 0,000 | promień poziomy od x=0 do krawędzi półki | OK |
| `ramka_wkladka_v2.stl` | półka C: wierzch Z | insert_shelf_h | 66,100 | 66,100 | -0,000 | promień −Z | OK |
| `ramka_wkladka_v2.stl` | półka C: grubość | insert_shelf_h | 2,500 | 2,500 | -0,000 | promienie z zewnątrz | OK |
| `ramka_wkladka_v2.stl` | półka C: zasięg 12 od ściany otworu | insert_shelf | 36,300 | 36,300 | -0,000 | promień poziomy od x=0 do krawędzi półki | OK |
| `ramka_wkladka_v2.stl` | półka D: wierzch Z | insert_shelf_h | 66,100 | 66,100 | -0,000 | promień −Z | OK |
| `ramka_wkladka_v2.stl` | półka D: grubość | insert_shelf_h | 2,500 | 2,500 | 0,000 | promienie z zewnątrz | OK |
| `ramka_wkladka_v2.stl` | półka D: zasięg 12 od ściany otworu | insert_shelf | 36,300 | 36,300 | 0,000 | promień poziomy od x=0 do krawędzi półki | OK |
| `ramka_wkladka_v2.stl` | kieszeń Halla A: X | hall_pocket_w | 5,000 | 5,000 | 0,000 | cięciwa X | OK |
| `ramka_wkladka_v2.stl` | kieszeń Halla A: Y | hall_pocket_l | 5,500 | 5,500 | -0,000 | cięciwa Y | OK |
| `ramka_wkladka_v2.stl` | kieszeń Halla A: przelotowa | D5 | 0,000 | 0,000 | 0,000 | promień −Z: 0 = przelot | OK |
| `ramka_wkladka_v2.stl` | kanał Halla A pod półką: wysokość | hall_lead_channel_h | 1,000 | 1,000 | -0,000 | promień +Z z Z 0,5 (sufit kanału) | OK |
| `ramka_wkladka_v2.stl` | kanał Halla A pod półką: szerokość | hall_lead_channel_w | 2,500 | 2,500 | 0,000 | cięciwa prostopadła do przekątnej | OK |
| `ramka_wkladka_v2.stl` | przelot w ściance ramy A: wysokość | hall_wall_pass_h | 1,500 | 1,500 | -0,000 | promień +Z (sufit przelotu) | OK |
| `ramka_wkladka_v2.stl` | przelot w ściance ramy A: otwarty po przekątnej przez całą ściankę (promień z (-47.5,-47.5) ku narożnikowi; do narożnika zewn. 6,8) | R50‑U9 (jedna bryła ciągła) | 0,000 | 0,000 | 0,000 | 0 = brak trafienia w ściankę przed narożnikiem zewn. (za nim w B i C leży nasada ucha) | OK |
| `ramka_wkladka_v2.stl` | kieszeń Halla B: X | hall_pocket_w | 5,000 | 5,000 | 0,000 | cięciwa X | OK |
| `ramka_wkladka_v2.stl` | kieszeń Halla B: Y | hall_pocket_l | 5,500 | 5,500 | -0,000 | cięciwa Y | OK |
| `ramka_wkladka_v2.stl` | kieszeń Halla B: przelotowa | D5 | 0,000 | 0,000 | 0,000 | promień −Z: 0 = przelot | OK |
| `ramka_wkladka_v2.stl` | kanał Halla B pod półką: wysokość | hall_lead_channel_h | 1,000 | 1,000 | -0,000 | promień +Z z Z 0,5 (sufit kanału) | OK |
| `ramka_wkladka_v2.stl` | kanał Halla B pod półką: szerokość | hall_lead_channel_w | 2,500 | 2,500 | 0,000 | cięciwa prostopadła do przekątnej | OK |
| `ramka_wkladka_v2.stl` | przelot w ściance ramy B: wysokość | hall_wall_pass_h | 1,500 | 1,500 | -0,000 | promień +Z (sufit przelotu) | OK |
| `ramka_wkladka_v2.stl` | przelot w ściance ramy B: otwarty po przekątnej przez całą ściankę (promień z (-47.5,47.5) ku narożnikowi; do narożnika zewn. 6,8) | R50‑U9 (jedna bryła ciągła) | 0,000 | 0,000 | 0,000 | 0 = brak trafienia w ściankę przed narożnikiem zewn. (za nim w B i C leży nasada ucha) | OK |
| `ramka_wkladka_v2.stl` | kieszeń Halla C: X | hall_pocket_w | 5,000 | 5,000 | 0,000 | cięciwa X | OK |
| `ramka_wkladka_v2.stl` | kieszeń Halla C: Y | hall_pocket_l | 5,500 | 5,500 | -0,000 | cięciwa Y | OK |
| `ramka_wkladka_v2.stl` | kieszeń Halla C: przelotowa | D5 | 0,000 | 0,000 | 0,000 | promień −Z: 0 = przelot | OK |
| `ramka_wkladka_v2.stl` | kanał Halla C pod półką: wysokość | hall_lead_channel_h | 1,000 | 1,000 | -0,000 | promień +Z z Z 0,5 (sufit kanału) | OK |
| `ramka_wkladka_v2.stl` | kanał Halla C pod półką: szerokość | hall_lead_channel_w | 2,500 | 2,500 | 0,000 | cięciwa prostopadła do przekątnej | OK |
| `ramka_wkladka_v2.stl` | przelot w ściance ramy C: wysokość | hall_wall_pass_h | 1,500 | 1,500 | -0,000 | promień +Z (sufit przelotu) | OK |
| `ramka_wkladka_v2.stl` | przelot w ściance ramy C: otwarty po przekątnej przez całą ściankę (promień z (47.5,47.5) ku narożnikowi; do narożnika zewn. 6,8) | R50‑U9 (jedna bryła ciągła) | 0,000 | 0,000 | 0,000 | 0 = brak trafienia w ściankę przed narożnikiem zewn. (za nim w B i C leży nasada ucha) | OK |
| `ramka_wkladka_v2.stl` | kołek orientacyjny: X | orient_post | 4,400 | 4,400 | -0,000 | promienie z odległości 2,5 w Z 5 | OK |
| `ramka_wkladka_v2.stl` | kołek orientacyjny: Y | orient_post | 4,400 | 4,400 | -0,000 | promienie z odległości 2,5 w Z 5 | OK |
| `ramka_wkladka_v2.stl` | kołek orientacyjny: szczyt Z | insert_shelf_h + orient_post_h | 71,100 | 71,100 | -0,000 | promień −Z | OK |
| `ramka_wkladka_v2.stl` | kołek orientacyjny: luz do ściany otworu (x) | orient_post_gap | 0,500 | 0,500 | -0,000 | cięciwa X w szczelinie | OK |
| `ramka_wkladka_v2.stl` | kołek orientacyjny: faza 1 na szczycie (X na Z szczyt−0,5) | orient_post_chamfer | 3,400 | 3,400 | -0,000 | promienie z zewnątrz 0,5 pod szczytem | OK |
| `ramka_wkladka_v2.stl` | wycięcie palcowe X | finger_cut_w | 30 | 30,000 | 0,000 | cięciwa X w ścianie przedniej | OK |
| `ramka_wkladka_v2.stl` | wycięcie palcowe: pełna wysokość | 4.6.5 | 0,000 | 0,000 | 0,000 | promień −Z: 0 = brak materiału | OK |
| `ramka_wkladka_v2.stl` | rowek kablowy prawy: dno | 52,3 − wire_rabbet_w | 49,800 | 49,800 | -0,000 | promień poziomy w Z 0,75 | OK |
| `ramka_wkladka_v2.stl` | rowek kablowy prawy: sufit | wire_rabbet | 65,100 | 65,100 | -0,000 | promień +Z od dołu | OK |
| `ramka_wkladka_v2.stl` | rowek kablowy lewy: dno | 52,3 − wire_rabbet_w | -49,800 | -49,800 | 0,000 | promień poziomy w Z 0,75 | OK |
| `ramka_wkladka_v2.stl` | rowek kablowy lewy: sufit | wire_rabbet | 65,100 | 65,100 | -0,000 | promień +Z od dołu | OK |
| `ramka_wkladka_v2.stl` | rowek kablowy tylny: dno | 52,3 − wire_rabbet_w | 49,800 | 49,800 | -0,000 | promień poziomy w Z 0,75 | OK |
| `ramka_wkladka_v2.stl` | rowek kablowy tylny: sufit | wire_rabbet | 65,100 | 65,100 | -0,000 | promień +Z od dołu | OK |
| `ramka_wkladka_v2.stl` | brak materiału poza ramą dla y<52,3 (prawy pas, K‑56) | R51(3) | 0,000 | 0,000 | 0,000 | promień −Z w (58,50): 0 = nic | OK |
| `ramka_wkladka_v2.stl` | nasada L: x 44…52,3 od y 48,8 (materiał w (48,49.5)) | tab_root_* | 1,000 | 1,000 | 0,000 | promień −Z: 1 = materiał | OK |
| `ramka_wkladka_v2.stl` | nasada L: materiał w (56, 55) (x 52,3…65 od y 52,3) | tab_root_x_out | 1,000 | 1,000 | 0,000 | promień −Z: 1 = materiał | OK |
| `ramka_wkladka_v2.stl` | nasada L: brak materiału w (56, 51) (poza obrysem ramy dla y < 52,3) | tab_root_x_out | 0,000 | 0,000 | 0,000 | promień −Z: 0 = nic | OK |
| `ramka_wkladka_v2.stl` | nasada L: materiał w (46, 50) (x 44…52,3 od y 48,8 — w obrysie ramy) | tab_root_x_in | 1,000 | 1,000 | 0,000 | promienie ±Z z Z 0,5: 1 = materiał | OK |
| `ramka_wkladka_v2.stl` | ucho x=-58: szerokość X | tab_w | 14 | 14,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_wkladka_v2.stl` | ucho x=-58: koniec Y | tab_end_y | 96 | 96,000 | 0,000 | promień −Y | OK |
| `ramka_wkladka_v2.stl` | ucho x=-58: grubość | tab_t | 3 | 3,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_wkladka_v2.stl` | kołek ustalający x=-58: ø | tab_pin_d | 3 | 3,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_wkladka_v2.stl` | kołek ustalający x=-58: koniec Z | tab_pin_h | 60,100 | 60,100 | -0,000 | promień +Z od dołu | OK |
| `ramka_wkladka_v2.stl` | otwór magnesu ucha x=-58: ø | tab_magnet_hole_d | 5,400 | 5,400 | 0,000 | cięciwa X | OK |
| `ramka_wkladka_v2.stl` | otwór magnesu ucha x=-58: przelotowy | D12 | 0,000 | 0,000 | 0,000 | promień −Z: 0 = przelot | OK |
| `ramka_wkladka_v2.stl` | kanał kablowy ucha x=-64: wysokość | tab_cable_channel_h | 1,200 | 1,200 | -0,000 | promień +Z od dołu | OK |
| `ramka_wkladka_v2.stl` | kanał kablowy ucha x=-64: szerokość (od krawędzi ucha 65 do ścianki kanału) | tab_cable_channel_w | 2 | 2,000 | 0,000 | promień do ścianki kanału; kanał otwarty na krawędzi ucha | OK |
| `ramka_wkladka_v2.stl` | kanał kablowy ucha x=-64: wylot na krawędzi ucha (y 90) | wire_slot_y | 1,000 | 1,000 | 0,000 | promień do krawędzi 65: 0 = otwarty | OK |
| `ramka_wkladka_v2.stl` | ucho x=58: szerokość X | tab_w | 14 | 14,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_wkladka_v2.stl` | ucho x=58: koniec Y | tab_end_y | 96 | 96,000 | 0,000 | promień −Y | OK |
| `ramka_wkladka_v2.stl` | ucho x=58: grubość | tab_t | 3 | 3,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_wkladka_v2.stl` | kołek ustalający x=58: ø | tab_pin_d | 3 | 3,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_wkladka_v2.stl` | kołek ustalający x=58: koniec Z | tab_pin_h | 60,100 | 60,100 | -0,000 | promień +Z od dołu | OK |
| `ramka_wkladka_v2.stl` | otwór magnesu ucha x=58: ø | tab_magnet_hole_d | 5,400 | 5,400 | 0,000 | cięciwa X | OK |
| `ramka_wkladka_v2.stl` | otwór magnesu ucha x=58: przelotowy | D12 | 0,000 | 0,000 | 0,000 | promień −Z: 0 = przelot | OK |
| `ramka_wkladka_v2.stl` | kanał kablowy ucha x=64: wysokość | tab_cable_channel_h | 1,200 | 1,200 | -0,000 | promień +Z od dołu | OK |
| `ramka_wkladka_v2.stl` | kanał kablowy ucha x=64: szerokość (od krawędzi ucha 65 do ścianki kanału) | tab_cable_channel_w | 2 | 2,000 | 0,000 | promień do ścianki kanału; kanał otwarty na krawędzi ucha | OK |
| `ramka_wkladka_v2.stl` | kanał kablowy ucha x=64: wylot na krawędzi ucha (y 90) | wire_slot_y | 1,000 | 1,000 | 0,000 | promień do krawędzi 65: 0 = otwarty | OK |
| `ramka_wkladka_v2.stl` | strzałka ▼ x=-32: relief nad ramą | number_relief_h | 0,600 | 0,600 | -0,000 | max trafień −Z w polu wokół środka | OK |
| `ramka_wkladka_v2.stl` | strzałka ▼ x=32: relief nad ramą | number_relief_h | 0,600 | 0,600 | -0,000 | max trafień −Z w polu wokół środka | OK |
| `ramka_blat_v2.stl` | gabaryt X | box_outer | 200,000 | 200,000 | 0,000 | bbox | OK |
| `ramka_blat_v2.stl` | gabaryt Y | box_outer | 200,000 | 200,000 | 0,000 | bbox | OK |
| `ramka_blat_v2.stl` | gabaryt Z | blat_t + blat_skirt_h | 14 | 14,000 | 0,000 | bbox | OK |
| `ramka_blat_v2.stl` | grubość płyty | blat_t | 4 | 4,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_blat_v2.stl` | spód płyty płaski (R50‑U1, (90,90)) | blat_t | 59,600 | 59,600 | -0,000 | promień +Z od dołu | OK |
| `ramka_blat_v2.stl` | kieszeń dyfuzora X | diffuser_pocket | 162 | 162,000 | -0,000 | cięciwa X | OK |
| `ramka_blat_v2.stl` | kieszeń dyfuzora Y | diffuser_pocket | 162 | 162,000 | -0,000 | cięciwa Y | OK |
| `ramka_blat_v2.stl` | kieszeń dyfuzora: głębokość | diffuser_t | 2 | 2,000 | 0,000 | promień −Z na półce | OK |
| `ramka_blat_v2.stl` | kieszeń dyfuzora: naroże ostre | diffuser_pocket_r 0 | 81,000 | 81,000 | 0,000 | promień +X przy y 80,8 | OK |
| `ramka_blat_v2.stl` | okno X | window_through | 158 | 158,000 | 0,000 | cięciwa X | OK |
| `ramka_blat_v2.stl` | okno Y | window_through | 158 | 158,000 | 0,000 | cięciwa Y | OK |
| `ramka_blat_v2.stl` | kołnierz zewn. X | 195 − 2·blat_skirt_clearance | 194,000 | 194,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_blat_v2.stl` | kołnierz zewn. Y | j.w. | 194,000 | 194,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_blat_v2.stl` | kołnierz: wysokość całkowita | blat_t + blat_skirt_h | 14 | 14,000 | -0,000 | promienie z zewnątrz | OK |
| `ramka_blat_v2.stl` | haczyk prawy: czubek | 97,0 + snap_hook_h | 98,300 | 98,300 | 0,000 | promień poziomy w środku występu | OK |
| `ramka_blat_v2.stl` | haczyk prawy: szerokość | snap_hook_w | 8 | 8,000 | -0,000 | cięciwa 0,3 za czubkiem | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku prawy (Y=-4.5): przelot przez kołnierz w Z 50,6 | snap_notch_w | 0,000 | 0,000 | 0,000 | promień poziomy: 0 = brak kołnierza (nacięcie) | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku prawy (Y=-4.5): koniec nacięcia (materiał w Z 59.1, lokalnie −4,5) | snap_hook_arm_l 9 (−14…−5) | 1,000 | 1,000 | 0,000 | promień poziomy: 1 = materiał | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku prawy (Y=-4.5): jeszcze nacięcie w Z 58.3 (lokalnie −5,3) | snap_hook_arm_l 9 | 0,000 | 0,000 | 0,000 | promień poziomy: 0 = nacięcie | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku prawy (Y=4.5): przelot przez kołnierz w Z 50,6 | snap_notch_w | 0,000 | 0,000 | 0,000 | promień poziomy: 0 = brak kołnierza (nacięcie) | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku prawy (Y=4.5): koniec nacięcia (materiał w Z 59.1, lokalnie −4,5) | snap_hook_arm_l 9 (−14…−5) | 1,000 | 1,000 | 0,000 | promień poziomy: 1 = materiał | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku prawy (Y=4.5): jeszcze nacięcie w Z 58.3 (lokalnie −5,3) | snap_hook_arm_l 9 | 0,000 | 0,000 | 0,000 | promień poziomy: 0 = nacięcie | OK |
| `ramka_blat_v2.stl` | haczyk lewy: czubek | 97,0 + snap_hook_h | 98,300 | 98,300 | 0,000 | promień poziomy w środku występu | OK |
| `ramka_blat_v2.stl` | haczyk lewy: szerokość | snap_hook_w | 8 | 8,000 | -0,000 | cięciwa 0,3 za czubkiem | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku lewy (Y=-4.5): przelot przez kołnierz w Z 50,6 | snap_notch_w | 0,000 | 0,000 | 0,000 | promień poziomy: 0 = brak kołnierza (nacięcie) | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku lewy (Y=-4.5): koniec nacięcia (materiał w Z 59.1, lokalnie −4,5) | snap_hook_arm_l 9 (−14…−5) | 1,000 | 1,000 | 0,000 | promień poziomy: 1 = materiał | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku lewy (Y=-4.5): jeszcze nacięcie w Z 58.3 (lokalnie −5,3) | snap_hook_arm_l 9 | 0,000 | 0,000 | 0,000 | promień poziomy: 0 = nacięcie | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku lewy (Y=4.5): przelot przez kołnierz w Z 50,6 | snap_notch_w | 0,000 | 0,000 | 0,000 | promień poziomy: 0 = brak kołnierza (nacięcie) | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku lewy (Y=4.5): koniec nacięcia (materiał w Z 59.1, lokalnie −4,5) | snap_hook_arm_l 9 (−14…−5) | 1,000 | 1,000 | 0,000 | promień poziomy: 1 = materiał | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku lewy (Y=4.5): jeszcze nacięcie w Z 58.3 (lokalnie −5,3) | snap_hook_arm_l 9 | 0,000 | 0,000 | 0,000 | promień poziomy: 0 = nacięcie | OK |
| `ramka_blat_v2.stl` | haczyk przedni: czubek | 97,0 + snap_hook_h | 98,300 | 98,300 | -0,000 | promień poziomy w środku występu | OK |
| `ramka_blat_v2.stl` | haczyk przedni: szerokość | snap_hook_w | 8 | 8,000 | 0,000 | cięciwa 0,3 za czubkiem | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku przedni (X=45.5): przelot przez kołnierz w Z 50,6 | snap_notch_w | 0,000 | 0,000 | 0,000 | promień poziomy: 0 = brak kołnierza (nacięcie) | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku przedni (X=45.5): koniec nacięcia (materiał w Z 59.1, lokalnie −4,5) | snap_hook_arm_l 9 (−14…−5) | 1,000 | 1,000 | 0,000 | promień poziomy: 1 = materiał | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku przedni (X=45.5): jeszcze nacięcie w Z 58.3 (lokalnie −5,3) | snap_hook_arm_l 9 | 0,000 | 0,000 | 0,000 | promień poziomy: 0 = nacięcie | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku przedni (X=54.5): przelot przez kołnierz w Z 50,6 | snap_notch_w | 0,000 | 0,000 | 0,000 | promień poziomy: 0 = brak kołnierza (nacięcie) | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku przedni (X=54.5): koniec nacięcia (materiał w Z 59.1, lokalnie −4,5) | snap_hook_arm_l 9 (−14…−5) | 1,000 | 1,000 | 0,000 | promień poziomy: 1 = materiał | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku przedni (X=54.5): jeszcze nacięcie w Z 58.3 (lokalnie −5,3) | snap_hook_arm_l 9 | 0,000 | 0,000 | 0,000 | promień poziomy: 0 = nacięcie | OK |
| `ramka_blat_v2.stl` | haczyk tylny: czubek | 97,0 + snap_hook_h | 98,300 | 98,300 | 0,000 | promień poziomy w środku występu | OK |
| `ramka_blat_v2.stl` | haczyk tylny: szerokość | snap_hook_w | 8 | 8,000 | 0,000 | cięciwa 0,3 za czubkiem | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku tylny (X=-54.5): przelot przez kołnierz w Z 50,6 | snap_notch_w | 0,000 | 0,000 | 0,000 | promień poziomy: 0 = brak kołnierza (nacięcie) | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku tylny (X=-54.5): koniec nacięcia (materiał w Z 59.1, lokalnie −4,5) | snap_hook_arm_l 9 (−14…−5) | 1,000 | 1,000 | 0,000 | promień poziomy: 1 = materiał | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku tylny (X=-54.5): jeszcze nacięcie w Z 58.3 (lokalnie −5,3) | snap_hook_arm_l 9 | 0,000 | 0,000 | 0,000 | promień poziomy: 0 = nacięcie | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku tylny (X=-45.5): przelot przez kołnierz w Z 50,6 | snap_notch_w | 0,000 | 0,000 | 0,000 | promień poziomy: 0 = brak kołnierza (nacięcie) | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku tylny (X=-45.5): koniec nacięcia (materiał w Z 59.1, lokalnie −4,5) | snap_hook_arm_l 9 (−14…−5) | 1,000 | 1,000 | 0,000 | promień poziomy: 1 = materiał | OK |
| `ramka_blat_v2.stl` | nacięcie przy haczyku tylny (X=-45.5): jeszcze nacięcie w Z 58.3 (lokalnie −5,3) | snap_hook_arm_l 9 | 0,000 | 0,000 | 0,000 | promień poziomy: 0 = nacięcie | OK |
| `ramka_blat_v2.stl` | słupek x=-75: X zakres (71…79) | blat_post_w | 8 | 8,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_blat_v2.stl` | słupek x=-75: przednie lico y | blat_post_y0 | 89,200 | 89,200 | -0,000 | promień +Y | OK |
| `ramka_blat_v2.stl` | słupek x=-75: dół Z (lokalnie −14) | blat_skirt_h | 49,600 | 49,600 | -0,000 | promień +Z od dołu | OK |
| `ramka_blat_v2.stl` | otwór słupka x=-75: ø | insert_hole_m3 | 2,500 | 2,500 | -0,000 | cięciwa X | OK |
| `ramka_blat_v2.stl` | otwór słupka x=-75: ø (Z) | insert_hole_m3 | 2,500 | 2,500 | 0,000 | cięciwa Z | OK |
| `ramka_blat_v2.stl` | otwór słupka x=-75: dno (y) | 97,0 − blat_post_hole_depth | 91,000 | 91,000 | 0,000 | promień −Y | OK |
| `ramka_blat_v2.stl` | otwór słupka x=-75: otwarty na licu kołnierza 97,0 | R49a | 0,000 | 0,000 | 0,000 | promień +Y: 0 = wychodzi na zewnątrz | OK |
| `ramka_blat_v2.stl` | otwór kołka x=-58: ø | blat_pin_hole_d | 3,300 | 3,300 | 0,000 | cięciwa X | OK |
| `ramka_blat_v2.stl` | otwór kołka x=-58: dno Z (ślepy) | blat_pin_hole_depth | 59,800 | 59,800 | -0,000 | promień −Z | OK |
| `ramka_blat_v2.stl` | kieszeń magnesu x=-58: ø | blat_magnet_pocket_d | 5,400 | 5,400 | 0,000 | cięciwa X | OK |
| `ramka_blat_v2.stl` | kieszeń magnesu x=-58: głębokość | blat_magnet_pocket_depth | 2,300 | 2,300 | 0,000 | promień −Z | OK |
| `ramka_blat_v2.stl` | szczelina kabla x=-66: X | wire_slot_w | 4 | 4,000 | -0,000 | cięciwa X | OK |
| `ramka_blat_v2.stl` | szczelina kabla x=-66: Y | wire_slot_l | 8 | 8,000 | 0,000 | cięciwa Y | OK |
| `ramka_blat_v2.stl` | szczelina kabla x=-66: przelotowa | D12 | 0,000 | 0,000 | 0,000 | promień −Z: 0 = przelot | OK |
| `ramka_blat_v2.stl` | słupek x=75: X zakres (71…79) | blat_post_w | 8 | 8,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_blat_v2.stl` | słupek x=75: przednie lico y | blat_post_y0 | 89,200 | 89,200 | -0,000 | promień +Y | OK |
| `ramka_blat_v2.stl` | słupek x=75: dół Z (lokalnie −14) | blat_skirt_h | 49,600 | 49,600 | -0,000 | promień +Z od dołu | OK |
| `ramka_blat_v2.stl` | otwór słupka x=75: ø | insert_hole_m3 | 2,500 | 2,500 | -0,000 | cięciwa X | OK |
| `ramka_blat_v2.stl` | otwór słupka x=75: ø (Z) | insert_hole_m3 | 2,500 | 2,500 | 0,000 | cięciwa Z | OK |
| `ramka_blat_v2.stl` | otwór słupka x=75: dno (y) | 97,0 − blat_post_hole_depth | 91,000 | 91,000 | 0,000 | promień −Y | OK |
| `ramka_blat_v2.stl` | otwór słupka x=75: otwarty na licu kołnierza 97,0 | R49a | 0,000 | 0,000 | 0,000 | promień +Y: 0 = wychodzi na zewnątrz | OK |
| `ramka_blat_v2.stl` | otwór kołka x=58: ø | blat_pin_hole_d | 3,300 | 3,300 | 0,000 | cięciwa X | OK |
| `ramka_blat_v2.stl` | otwór kołka x=58: dno Z (ślepy) | blat_pin_hole_depth | 59,800 | 59,800 | -0,000 | promień −Z | OK |
| `ramka_blat_v2.stl` | kieszeń magnesu x=58: ø | blat_magnet_pocket_d | 5,400 | 5,400 | 0,000 | cięciwa X | OK |
| `ramka_blat_v2.stl` | kieszeń magnesu x=58: głębokość | blat_magnet_pocket_depth | 2,300 | 2,300 | 0,000 | promień −Z | OK |
| `ramka_blat_v2.stl` | szczelina kabla x=66: X | wire_slot_w | 4 | 4,000 | 0,000 | cięciwa X | OK |
| `ramka_blat_v2.stl` | szczelina kabla x=66: Y | wire_slot_l | 8 | 8,000 | 0,000 | cięciwa Y | OK |
| `ramka_blat_v2.stl` | szczelina kabla x=66: przelotowa | D12 | 0,000 | 0,000 | 0,000 | promień −Z: 0 = przelot | OK |
| `ramka_blat_v2.stl` | R 5 pionowej krawędzi: punkt na przekątnej | blat_corner_r | 98,536 | 98,536 | 0,000 | promień wzdłuż przekątnej | OK |
| `ramka_blat_v2.stl` | R 1,5 górnej krawędzi: x boku na Z wierzch−0,2 | blat_top_edge_r | 99,248 | 99,241 | -0,008 | promień −X 0,2 pod wierzchem | OK |
| `ramka_blat_v2.stl` | kołnierz: R 4,5 naroża zewn. | R50‑U15 (4,5) | 95,682 | 95,681 | -0,001 | promień wzdłuż przekątnej | OK |
| `ramka_korpus_W_v2.stl` | gabaryt X | box_outer | 200 | 200,000 | 0,000 | bbox | OK |
| `ramka_korpus_W_v2.stl` | gabaryt Y (z napisem 0,6) | box_outer + label_relief_h | 200,600 | 200,600 | -0,000 | bbox | OK |
| `ramka_korpus_W_v2.stl` | gabaryt Z | korpus_h | 59,600 | 59,600 | -0,000 | bbox | OK |
| `ramka_korpus_W_v2.stl` | bok X | box_outer | 200 | 200,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_korpus_W_v2.stl` | bok Y (poza napisem) | box_outer | 200 | 200,000 | -0,000 | promienie z zewnątrz | OK |
| `ramka_korpus_W_v2.stl` | wnętrze X | box_outer − 2·wall_t | 195,000 | 195,000 | 0,000 | cięciwa X | OK |
| `ramka_korpus_W_v2.stl` | wnętrze Y | j.w. | 195,000 | 195,000 | -0,000 | cięciwa Y | OK |
| `ramka_korpus_W_v2.stl` | wierzch ściany Z | korpus_h | 59,600 | 59,600 | 0,000 | promień −Z | OK |
| `ramka_korpus_W_v2.stl` | dno: grubość | floor_t | 3 | 3,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_korpus_W_v2.stl` | R 5 pionowej krawędzi: punkt na przekątnej | box_corner_r | 98,536 | 98,536 | 0,000 | promień wzdłuż przekątnej | OK |
| `ramka_korpus_W_v2.stl` | R 3 dolnej krawędzi: x boku na Z 0,2 | box_edge_r | 98,077 | 98,070 | -0,007 | promień −X 0,2 nad dnem | OK |
| `ramka_korpus_W_v2.stl` | szczelina tylna x=-54: X | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa X | OK |
| `ramka_korpus_W_v2.stl` | szczelina tylna x=-54: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_W_v2.stl` | szczelina tylna x=-18: X | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa X | OK |
| `ramka_korpus_W_v2.stl` | szczelina tylna x=-18: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_W_v2.stl` | szczelina tylna x=18: X | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa X | OK |
| `ramka_korpus_W_v2.stl` | szczelina tylna x=18: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_W_v2.stl` | szczelina tylna x=54: X | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa X | OK |
| `ramka_korpus_W_v2.stl` | szczelina tylna x=54: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_W_v2.stl` | szczelina boczna x=− y=-36: Y | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa Y | OK |
| `ramka_korpus_W_v2.stl` | szczelina boczna x=− y=-36: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_W_v2.stl` | szczelina boczna x=+ y=-36: Y | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa Y | OK |
| `ramka_korpus_W_v2.stl` | szczelina boczna x=+ y=-36: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_W_v2.stl` | szczelina boczna x=− y=0: Y | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa Y | OK |
| `ramka_korpus_W_v2.stl` | szczelina boczna x=− y=0: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_W_v2.stl` | szczelina boczna x=+ y=0: Y | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa Y | OK |
| `ramka_korpus_W_v2.stl` | szczelina boczna x=+ y=0: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_W_v2.stl` | szczelina boczna x=− y=36: Y | vent_slot_w | 12 | 12,000 | -0,000 | cięciwa Y | OK |
| `ramka_korpus_W_v2.stl` | szczelina boczna x=− y=36: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_W_v2.stl` | szczelina boczna x=+ y=36: Y | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa Y | OK |
| `ramka_korpus_W_v2.stl` | szczelina boczna x=+ y=36: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_W_v2.stl` | wlot w dnie y=-10: X | floor_vent_l | 30 | 30,000 | 0,000 | cięciwa X | OK |
| `ramka_korpus_W_v2.stl` | wlot w dnie y=-10: Y | floor_vent_w | 4 | 4,000 | 0,000 | cięciwa Y | OK |
| `ramka_korpus_W_v2.stl` | wlot w dnie y=10: X | floor_vent_l | 30 | 30,000 | 0,000 | cięciwa X | OK |
| `ramka_korpus_W_v2.stl` | wlot w dnie y=10: Y | floor_vent_w | 4 | 4,000 | 0,000 | cięciwa Y | OK |
| `ramka_korpus_W_v2.stl` | kieszeń zatrzasku prawa: szerokość | snap_pocket_w | 10 | 10,000 | 0,000 | cięciwa | OK |
| `ramka_korpus_W_v2.stl` | kieszeń zatrzasku prawa: wysokość | snap_pocket_h | 2,500 | 2,500 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_W_v2.stl` | kieszeń zatrzasku prawa: dolna krawędź Z | snap_pocket_z | 52,600 | 52,600 | -0,000 | promień −Z | OK |
| `ramka_korpus_W_v2.stl` | kieszeń zatrzasku prawa: dno | 97,5 + snap_pocket_depth | 98,500 | 98,500 | 0,000 | promień poziomy | OK |
| `ramka_korpus_W_v2.stl` | kieszeń zatrzasku lewa: szerokość | snap_pocket_w | 10 | 10,000 | 0,000 | cięciwa | OK |
| `ramka_korpus_W_v2.stl` | kieszeń zatrzasku lewa: wysokość | snap_pocket_h | 2,500 | 2,500 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_W_v2.stl` | kieszeń zatrzasku lewa: dolna krawędź Z | snap_pocket_z | 52,600 | 52,600 | -0,000 | promień −Z | OK |
| `ramka_korpus_W_v2.stl` | kieszeń zatrzasku lewa: dno | 97,5 + snap_pocket_depth | 98,500 | 98,500 | 0,000 | promień poziomy | OK |
| `ramka_korpus_W_v2.stl` | kieszeń zatrzasku przednia: szerokość | snap_pocket_w | 10 | 10,000 | 0,000 | cięciwa | OK |
| `ramka_korpus_W_v2.stl` | kieszeń zatrzasku przednia: wysokość | snap_pocket_h | 2,500 | 2,500 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_W_v2.stl` | kieszeń zatrzasku przednia: dolna krawędź Z | snap_pocket_z | 52,600 | 52,600 | -0,000 | promień −Z | OK |
| `ramka_korpus_W_v2.stl` | kieszeń zatrzasku przednia: dno | 97,5 + snap_pocket_depth | 98,500 | 98,500 | 0,000 | promień poziomy | OK |
| `ramka_korpus_W_v2.stl` | kieszeń zatrzasku tylna: szerokość | snap_pocket_w | 10 | 10,000 | 0,000 | cięciwa | OK |
| `ramka_korpus_W_v2.stl` | kieszeń zatrzasku tylna: wysokość | snap_pocket_h | 2,500 | 2,500 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_W_v2.stl` | kieszeń zatrzasku tylna: dolna krawędź Z | snap_pocket_z | 52,600 | 52,600 | -0,000 | promień −Z | OK |
| `ramka_korpus_W_v2.stl` | kieszeń zatrzasku tylna: dno | 97,5 + snap_pocket_depth | 98,500 | 98,500 | 0,000 | promień poziomy | OK |
| `ramka_korpus_W_v2.stl` | otwór wkrętu blatu x=-75: ø | blat_screw_hole_d | 3,200 | 3,195 | -0,005 | cięciwa X | OK |
| `ramka_korpus_W_v2.stl` | pogłębienie stożkowe x=-75: ø 0,1 pod licem | blat_screw_csink_d | 6,100 | 6,100 | 0,000 | cięciwa X (90° → −0,2) | OK |
| `ramka_korpus_W_v2.stl` | otwór wkrętu blatu x=75: ø | blat_screw_hole_d | 3,200 | 3,195 | -0,005 | cięciwa X | OK |
| `ramka_korpus_W_v2.stl` | pogłębienie stożkowe x=75: ø 0,1 pod licem | blat_screw_csink_d | 6,100 | 6,100 | 0,000 | cięciwa X (90° → −0,2) | OK |
| `ramka_korpus_W_v2.stl` | napis: wysokość liter (Z) | label_text_h | 8 | 8,100 | 0,100 | skan 0,1 mm | OK |
| `ramka_korpus_W_v2.stl` | napis: środek Z | label_pos_z | 51,000 | 51,000 | 0,000 | skan 0,1 mm | OK |
| `ramka_korpus_W_v2.stl` | napis: środek X | 0 | 0,000 | 0,000 | 0,000 | skan 0,5 mm | OK |
| `ramka_korpus_W_v2.stl` | napis: relief | label_relief_h | 0,600 | 0,600 | 0,000 | min Y trafień | OK |
| `ramka_korpus_W_v2.stl` | przednia ściana gładka (Z28): brak otworów (skan Z 10…50, x −90…90) | D15 | 0 | 0 | 0 | liczba promieni +Y bez trafienia | OK |
| `ramka_korpus_P_v2.stl` | gabaryt X | box_outer | 200 | 200,000 | 0,000 | bbox | OK |
| `ramka_korpus_P_v2.stl` | gabaryt Y (z napisem 0,6) | box_outer + label_relief_h | 200,600 | 200,600 | -0,000 | bbox | OK |
| `ramka_korpus_P_v2.stl` | gabaryt Z | korpus_h | 59,600 | 59,600 | -0,000 | bbox | OK |
| `ramka_korpus_P_v2.stl` | bok X | box_outer | 200 | 200,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_korpus_P_v2.stl` | bok Y (poza napisem) | box_outer | 200 | 200,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_korpus_P_v2.stl` | wnętrze X | box_outer − 2·wall_t | 195,000 | 195,000 | 0,000 | cięciwa X | OK |
| `ramka_korpus_P_v2.stl` | wnętrze Y | j.w. | 195,000 | 195,000 | -0,000 | cięciwa Y | OK |
| `ramka_korpus_P_v2.stl` | wierzch ściany Z | korpus_h | 59,600 | 59,600 | 0,000 | promień −Z | OK |
| `ramka_korpus_P_v2.stl` | dno: grubość | floor_t | 3 | 3,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_korpus_P_v2.stl` | R 5 pionowej krawędzi: punkt na przekątnej | box_corner_r | 98,536 | 98,536 | 0,000 | promień wzdłuż przekątnej | OK |
| `ramka_korpus_P_v2.stl` | R 3 dolnej krawędzi: x boku na Z 0,2 | box_edge_r | 98,077 | 98,070 | -0,007 | promień −X 0,2 nad dnem | OK |
| `ramka_korpus_P_v2.stl` | szczelina tylna x=-54: X | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa X | OK |
| `ramka_korpus_P_v2.stl` | szczelina tylna x=-54: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_P_v2.stl` | szczelina tylna x=-18: X | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa X | OK |
| `ramka_korpus_P_v2.stl` | szczelina tylna x=-18: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_P_v2.stl` | szczelina tylna x=18: X | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa X | OK |
| `ramka_korpus_P_v2.stl` | szczelina tylna x=18: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_P_v2.stl` | szczelina tylna x=54: X | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa X | OK |
| `ramka_korpus_P_v2.stl` | szczelina tylna x=54: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_P_v2.stl` | szczelina boczna x=− y=-36: Y | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa Y | OK |
| `ramka_korpus_P_v2.stl` | szczelina boczna x=− y=-36: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_P_v2.stl` | szczelina boczna x=+ y=-36: Y | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa Y | OK |
| `ramka_korpus_P_v2.stl` | szczelina boczna x=+ y=-36: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_P_v2.stl` | szczelina boczna x=− y=0: Y | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa Y | OK |
| `ramka_korpus_P_v2.stl` | szczelina boczna x=− y=0: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_P_v2.stl` | szczelina boczna x=+ y=0: Y | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa Y | OK |
| `ramka_korpus_P_v2.stl` | szczelina boczna x=+ y=0: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_P_v2.stl` | szczelina boczna x=− y=36: Y | vent_slot_w | 12 | 12,000 | -0,000 | cięciwa Y | OK |
| `ramka_korpus_P_v2.stl` | szczelina boczna x=− y=36: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_P_v2.stl` | szczelina boczna x=+ y=36: Y | vent_slot_w | 12 | 12,000 | 0,000 | cięciwa Y | OK |
| `ramka_korpus_P_v2.stl` | szczelina boczna x=+ y=36: Z | vent_slot_h | 3 | 3,000 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_P_v2.stl` | wlot w dnie y=-10: X | floor_vent_l | 30 | 30,000 | 0,000 | cięciwa X | OK |
| `ramka_korpus_P_v2.stl` | wlot w dnie y=-10: Y | floor_vent_w | 4 | 4,000 | 0,000 | cięciwa Y | OK |
| `ramka_korpus_P_v2.stl` | wlot w dnie y=10: X | floor_vent_l | 30 | 30,000 | 0,000 | cięciwa X | OK |
| `ramka_korpus_P_v2.stl` | wlot w dnie y=10: Y | floor_vent_w | 4 | 4,000 | 0,000 | cięciwa Y | OK |
| `ramka_korpus_P_v2.stl` | kieszeń zatrzasku prawa: szerokość | snap_pocket_w | 10 | 10,000 | 0,000 | cięciwa | OK |
| `ramka_korpus_P_v2.stl` | kieszeń zatrzasku prawa: wysokość | snap_pocket_h | 2,500 | 2,500 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_P_v2.stl` | kieszeń zatrzasku prawa: dolna krawędź Z | snap_pocket_z | 52,600 | 52,600 | -0,000 | promień −Z | OK |
| `ramka_korpus_P_v2.stl` | kieszeń zatrzasku prawa: dno | 97,5 + snap_pocket_depth | 98,500 | 98,500 | 0,000 | promień poziomy | OK |
| `ramka_korpus_P_v2.stl` | kieszeń zatrzasku lewa: szerokość | snap_pocket_w | 10 | 10,000 | 0,000 | cięciwa | OK |
| `ramka_korpus_P_v2.stl` | kieszeń zatrzasku lewa: wysokość | snap_pocket_h | 2,500 | 2,500 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_P_v2.stl` | kieszeń zatrzasku lewa: dolna krawędź Z | snap_pocket_z | 52,600 | 52,600 | -0,000 | promień −Z | OK |
| `ramka_korpus_P_v2.stl` | kieszeń zatrzasku lewa: dno | 97,5 + snap_pocket_depth | 98,500 | 98,500 | 0,000 | promień poziomy | OK |
| `ramka_korpus_P_v2.stl` | kieszeń zatrzasku przednia: szerokość | snap_pocket_w | 10 | 10,000 | 0,000 | cięciwa | OK |
| `ramka_korpus_P_v2.stl` | kieszeń zatrzasku przednia: wysokość | snap_pocket_h | 2,500 | 2,500 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_P_v2.stl` | kieszeń zatrzasku przednia: dolna krawędź Z | snap_pocket_z | 52,600 | 52,600 | -0,000 | promień −Z | OK |
| `ramka_korpus_P_v2.stl` | kieszeń zatrzasku przednia: dno | 97,5 + snap_pocket_depth | 98,500 | 98,500 | 0,000 | promień poziomy | OK |
| `ramka_korpus_P_v2.stl` | kieszeń zatrzasku tylna: szerokość | snap_pocket_w | 10 | 10,000 | 0,000 | cięciwa | OK |
| `ramka_korpus_P_v2.stl` | kieszeń zatrzasku tylna: wysokość | snap_pocket_h | 2,500 | 2,500 | 0,000 | cięciwa Z | OK |
| `ramka_korpus_P_v2.stl` | kieszeń zatrzasku tylna: dolna krawędź Z | snap_pocket_z | 52,600 | 52,600 | -0,000 | promień −Z | OK |
| `ramka_korpus_P_v2.stl` | kieszeń zatrzasku tylna: dno | 97,5 + snap_pocket_depth | 98,500 | 98,500 | 0,000 | promień poziomy | OK |
| `ramka_korpus_P_v2.stl` | otwór wkrętu blatu x=-75: ø | blat_screw_hole_d | 3,200 | 3,195 | -0,005 | cięciwa X | OK |
| `ramka_korpus_P_v2.stl` | pogłębienie stożkowe x=-75: ø 0,1 pod licem | blat_screw_csink_d | 6,100 | 6,100 | 0,000 | cięciwa X (90° → −0,2) | OK |
| `ramka_korpus_P_v2.stl` | otwór wkrętu blatu x=75: ø | blat_screw_hole_d | 3,200 | 3,195 | -0,005 | cięciwa X | OK |
| `ramka_korpus_P_v2.stl` | pogłębienie stożkowe x=75: ø 0,1 pod licem | blat_screw_csink_d | 6,100 | 6,100 | 0,000 | cięciwa X (90° → −0,2) | OK |
| `ramka_korpus_P_v2.stl` | napis: wysokość liter (Z) | label_text_h | 8 | 8,100 | 0,100 | skan 0,1 mm | OK |
| `ramka_korpus_P_v2.stl` | napis: środek Z | label_pos_z | 51,000 | 51,000 | 0,000 | skan 0,1 mm | OK |
| `ramka_korpus_P_v2.stl` | napis: środek X | 0 | 0,000 | 0,000 | 0,000 | skan 0,5 mm | OK |
| `ramka_korpus_P_v2.stl` | napis: relief | label_relief_h | 0,600 | 0,600 | 0,000 | min Y trafień | OK |
| `ramka_korpus_P_v2.stl` | przednia ściana gładka (Z28): brak otworów (skan Z 10…50, x −90…90) | D15 | 0 | 0 | 0 | liczba promieni +Y bez trafienia | OK |
| `ramka_tulejka_dc_v2.stl` | gabaryt X/Y (kołnierz ø15) | dc_bush_flange_d | 15 | 14,999 | -0,001 | bbox | OK |
| `ramka_tulejka_dc_v2.stl` | gabaryt Z | dc_bush_t + dc_bush_flange_t | 3 | 3,000 | 0,000 | bbox | OK |
| `ramka_tulejka_dc_v2.stl` | walec ø zewn. | dc_bush_outer_d | 12 | 11,998 | -0,002 | promienie z zewnątrz (w złożeniu, oś X) | OK |
| `ramka_tulejka_dc_v2.stl` | otwór ø | dc_bush_inner_d | 8,200 | 8,200 | -0,000 | cięciwa | OK |
| `ramka_tulejka_dc_v2.stl` | kołnierz: grubość | dc_bush_flange_t | 1 | 1,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_tulejka_dc_v2.stl` | walec: długość | dc_bush_t | 2 | 2,000 | 0,000 | koniec walca (−40) − lico kołnierza od strony ściany (−42) | OK |
| `ramka_podkladka_panelu_05_v2.stl` | gabaryt X | panel_shim_d | 9 | 9,000 | 0,000 | bbox | OK |
| `ramka_podkladka_panelu_05_v2.stl` | gabaryt Y | panel_shim_d | 9 | 8,997 | -0,003 | bbox | OK |
| `ramka_podkladka_panelu_05_v2.stl` | gabaryt Z | panel_shim_t | 0,500 | 0,500 | 0,000 | bbox | OK |
| `ramka_podkladka_panelu_05_v2.stl` | ø zewn. | panel_shim_d | 9 | 9,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_podkladka_panelu_05_v2.stl` | otwór ø | panel_shim_hole_d | 3,400 | 3,395 | -0,005 | cięciwa X | OK |
| `ramka_podkladka_panelu_05_v2.stl` | otwór ø (Y) | panel_shim_hole_d | 3,400 | 3,393 | -0,007 | cięciwa Y | OK |
| `ramka_podkladka_panelu_05_v2.stl` | grubość | panel_shim_t | 0,500 | 0,500 | 0,000 | promienie z zewnątrz | OK |
| `ramka_podkladka_panelu_1_v2.stl` | gabaryt X | panel_shim_d | 9 | 9,000 | 0,000 | bbox | OK |
| `ramka_podkladka_panelu_1_v2.stl` | gabaryt Y | panel_shim_d | 9 | 8,997 | -0,003 | bbox | OK |
| `ramka_podkladka_panelu_1_v2.stl` | gabaryt Z | panel_shim_t | 1,000 | 1,000 | 0,000 | bbox | OK |
| `ramka_podkladka_panelu_1_v2.stl` | ø zewn. | panel_shim_d | 9 | 9,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_podkladka_panelu_1_v2.stl` | otwór ø | panel_shim_hole_d | 3,400 | 3,395 | -0,005 | cięciwa X | OK |
| `ramka_podkladka_panelu_1_v2.stl` | otwór ø (Y) | panel_shim_hole_d | 3,400 | 3,393 | -0,007 | cięciwa Y | OK |
| `ramka_podkladka_panelu_1_v2.stl` | grubość | panel_shim_t | 1,000 | 1,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_podkladka_panelu_2_v2.stl` | gabaryt X | panel_shim_d | 9 | 9,000 | 0,000 | bbox | OK |
| `ramka_podkladka_panelu_2_v2.stl` | gabaryt Y | panel_shim_d | 9 | 8,997 | -0,003 | bbox | OK |
| `ramka_podkladka_panelu_2_v2.stl` | gabaryt Z | panel_shim_t | 2,000 | 2,000 | 0,000 | bbox | OK |
| `ramka_podkladka_panelu_2_v2.stl` | ø zewn. | panel_shim_d | 9 | 9,000 | 0,000 | promienie z zewnątrz | OK |
| `ramka_podkladka_panelu_2_v2.stl` | otwór ø | panel_shim_hole_d | 3,400 | 3,395 | -0,005 | cięciwa X | OK |
| `ramka_podkladka_panelu_2_v2.stl` | otwór ø (Y) | panel_shim_hole_d | 3,400 | 3,393 | -0,007 | cięciwa Y | OK |
| `ramka_podkladka_panelu_2_v2.stl` | grubość | panel_shim_t | 2,000 | 2,000 | 0,000 | promienie z zewnątrz | OK |

## Tabela E. Ścianki minimalne

| STL | Miejsce | Oczekiwane | Zmierzone | Punkt | Min. | Werdykt | Uwaga |
|---|---|---|---|---|---|---|---|
| `ramka_korpus_W_v2.stl` | ścianka skrzynki DC z otworem ø12 (x −42…−40) | 2 | 2,000 | [-41, 81, 30] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | prawa ściana skrzynki nad otworem ø12: materiał od góry otworu (Z 36) do wierzchu skrzynki (Z 40); do sufitu wewn. 38 zostaje 2 | 4,000 | 4,001 | [-41, 89, 37.0] | 1.5 | OK | 4.11: „Z 24…36 → 2 do sufitu wewn.” |
| `ramka_korpus_P_v2.stl` | ścianka skrzynki DC z otworem ø12 (x −42…−40) | 2 | 2,000 | [-41, 81, 30] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | prawa ściana skrzynki nad otworem ø12: materiał od góry otworu (Z 36) do wierzchu skrzynki (Z 40); do sufitu wewn. 38 zostaje 2 | 4,000 | 4,001 | [-41, 89, 37.0] | 1.5 | OK | 4.11: „Z 24…36 → 2 do sufitu wewn.” |
| `ramka_korpus_W_v2.stl` | ścianka okno USB – rowek lewy | 1,900 | 1,904 | [51.05, 98.75, 24] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | ścianka okno USB – rowek prawy | 1,900 | 1,904 | [68.95, 98.75, 24] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | ścianka okno USB – rowek lewy | 1,900 | 1,904 | [51.05, 98.75, 24] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | ścianka okno USB – rowek prawy | 1,900 | 1,904 | [68.95, 98.75, 24] | 1.5 | OK |  |
| `ramka_plytka_poranna_n4_v2.stl` | materiał stożek A – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [-42.0, -42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_poranna_n4_v2.stl` | materiał stożek B – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [-42.0, 42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_poranna_n4_v2.stl` | materiał stożek C – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [42.0, 42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_poranna_n5_v2.stl` | materiał stożek A – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [-42.0, -42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_poranna_n5_v2.stl` | materiał stożek B – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [-42.0, 42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_poranna_n5_v2.stl` | materiał stożek C – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [42.0, 42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_poranna_n5_v2.stl` | dołek kodu A – krawędź płytki (2,0; R3) | 2,000 | 2,000 | [-47, -36, 73.6] | 1.5 | OK |  |
| `ramka_plytka_poranna_n5_v2.stl` | dołek kodu A – rowek pokrywki po przekątnej (R47: 1,3 lokalnie, dopuszczone) | 1,300 | 1,300 | [-46.6, -36, 72.85] | 1.3 | OK | R47(10): nie ścianka nośna; do_v3 #1 |
| `ramka_plytka_poranna_n6_v2.stl` | materiał stożek A – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [-42.0, -42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_poranna_n6_v2.stl` | materiał stożek B – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [-42.0, 42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_poranna_n6_v2.stl` | materiał stożek C – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [42.0, 42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_poranna_n6_v2.stl` | ścianka między dołkami kodu y -33/-30 (do_v3 #2: 1,0; głębokość 1, nie nośna) | 1 | 1,000 | [-45, -31.5, 73.5] | 1.0 | OK | do_v3 #2; dopuszczone w recenzji A |
| `ramka_plytka_poranna_v2.stl` | materiał stożek A – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [-42.0, -42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_poranna_v2.stl` | materiał stożek B – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [-42.0, 42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_poranna_v2.stl` | materiał stożek C – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [42.0, 42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_poranna_v2.stl` | dołek kodu A – krawędź płytki (2,0; R3) | 2,000 | 2,000 | [-47, -36, 73.6] | 1.5 | OK |  |
| `ramka_plytka_poranna_v2.stl` | dołek kodu A – rowek pokrywki po przekątnej (R47: 1,3 lokalnie, dopuszczone) | 1,300 | 1,300 | [-46.6, -36, 72.85] | 1.3 | OK | R47(10): nie ścianka nośna; do_v3 #1 |
| `ramka_plytka_poranna_v2.stl` | ścianka między dołkami kodu y -36/-33 (do_v3 #2: 1,0; głębokość 1, nie nośna) | 1 | 1,000 | [-45, -34.5, 73.5] | 1.0 | OK | do_v3 #2; dopuszczone w recenzji A |
| `ramka_plytka_poranna_v2.stl` | ścianka między dołkami kodu y -33/-30 (do_v3 #2: 1,0; głębokość 1, nie nośna) | 1 | 1,000 | [-45, -31.5, 73.5] | 1.0 | OK | do_v3 #2; dopuszczone w recenzji A |
| `ramka_plytka_wieczorna_n1_v2.stl` | materiał stożek A – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [-42.0, -42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_wieczorna_n1_v2.stl` | materiał stożek B – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [-42.0, 42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_wieczorna_n1_v2.stl` | materiał stożek C – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [42.0, 42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_wieczorna_n1_v2.stl` | dołek kodu A – krawędź płytki (2,0; R3) | 2,000 | 2,000 | [-47, -36, 73.6] | 1.5 | OK |  |
| `ramka_plytka_wieczorna_n1_v2.stl` | dołek kodu A – rowek pokrywki po przekątnej (R47: 1,3 lokalnie, dopuszczone) | 1,300 | 1,300 | [-46.6, -36, 72.85] | 1.3 | OK | R47(10): nie ścianka nośna; do_v3 #1 |
| `ramka_plytka_wieczorna_n2_v2.stl` | materiał stożek A – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [-42.0, -42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_wieczorna_n2_v2.stl` | materiał stożek B – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [-42.0, 42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_wieczorna_n2_v2.stl` | materiał stożek C – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [42.0, 42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_wieczorna_n3_v2.stl` | materiał stożek A – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [-42.0, -42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_wieczorna_n3_v2.stl` | materiał stożek B – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [-42.0, 42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_wieczorna_n3_v2.stl` | materiał stożek C – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [42.0, 42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_wieczorna_n3_v2.stl` | dołek kodu A – krawędź płytki (2,0; R3) | 2,000 | 2,000 | [-47, -36, 73.6] | 1.5 | OK |  |
| `ramka_plytka_wieczorna_n3_v2.stl` | dołek kodu A – rowek pokrywki po przekątnej (R47: 1,3 lokalnie, dopuszczone) | 1,300 | 1,300 | [-46.6, -36, 72.85] | 1.3 | OK | R47(10): nie ścianka nośna; do_v3 #1 |
| `ramka_plytka_wieczorna_n3_v2.stl` | ścianka między dołkami kodu y -36/-33 (do_v3 #2: 1,0; głębokość 1, nie nośna) | 1 | 1,000 | [-45, -34.5, 73.5] | 1.0 | OK | do_v3 #2; dopuszczone w recenzji A |
| `ramka_plytka_wieczorna_v2.stl` | materiał stożek A – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [-42.0, -42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_wieczorna_v2.stl` | materiał stożek B – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [-42.0, 42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_wieczorna_v2.stl` | materiał stożek C – kieszeń magnesu (Z4: 2,8) | 2,800 | 2,800 | [42.0, 42.0, 69.7] | 1.5 | OK |  |
| `ramka_plytka_wieczorna_v2.stl` | dołek kodu A – krawędź płytki (2,0; R3) | 2,000 | 2,000 | [-47, -36, 73.6] | 1.5 | OK |  |
| `ramka_plytka_wieczorna_v2.stl` | dołek kodu A – rowek pokrywki po przekątnej (R47: 1,3 lokalnie, dopuszczone) | 1,300 | 1,300 | [-46.6, -36, 72.85] | 1.3 | OK | R47(10): nie ścianka nośna; do_v3 #1 |
| `ramka_plytka_wieczorna_v2.stl` | ścianka między dołkami kodu y -36/-33 (do_v3 #2: 1,0; głębokość 1, nie nośna) | 1 | 1,000 | [-45, -34.5, 73.5] | 1.0 | OK | do_v3 #2; dopuszczone w recenzji A |
| `ramka_plytka_wieczorna_v2.stl` | ścianka między dołkami kodu y -33/-30 (do_v3 #2: 1,0; głębokość 1, nie nośna) | 1 | 1,000 | [-45, -31.5, 73.5] | 1.0 | OK | do_v3 #2; dopuszczone w recenzji A |
| `ramka_pokrywka_v2.stl` | kołnierz pokrywki (grubość) | 1,500 | 1,500 | [49.05, 20, 75.1] | 1.5 | OK |  |
| `ramka_pokrywka_v2.stl` | kołnierz pokrywki przy garbie (grubość za garbem) | 1,500 | 1,500 | [49.05, 0, 80.1] | 1.5 | OK |  |
| `ramka_wkladka_v2.stl` | półka A nad kanałem (2,5 − 1,0) | 1,500 | 1,500 | [-46.0, -46.0, 65.35] | 1.5 | OK |  |
| `ramka_wkladka_v2.stl` | półka B nad kanałem (2,5 − 1,0) | 1,500 | 1,500 | [-46.0, 46.0, 65.35] | 1.5 | OK |  |
| `ramka_wkladka_v2.stl` | półka C nad kanałem (2,5 − 1,0) | 1,500 | 1,500 | [46.0, 46.0, 65.35] | 1.5 | OK |  |
| `ramka_wkladka_v2.stl` | ścianka rowek kablowy – otwór (52,3 − 2,5 − 48,3) | 1,500 | 1,500 | [49.05, 0, 64.35] | 1.5 | OK |  |
| `ramka_wkladka_v2.stl` | ścianka rowek kablowy – otwór (tył) | 1,500 | 1,500 | [0, 49.05, 64.35] | 1.5 | OK |  |
| `ramka_wkladka_v2.stl` | rama nad rowkiem kablowym (6 − 1,5) | 4,500 | 4,500 | [51.05, 0, 67.35] | 1.5 | OK |  |
| `ramka_blat_v2.stl` | kołnierz blatu (grubość) | 2 | 2,000 | [96, 30, 54.6] | 1.5 | OK |  |
| `ramka_blat_v2.stl` | kołnierz blatu (grubość, tył) | 2 | 2,000 | [30, 96, 54.6] | 1.5 | OK |  |
| `ramka_blat_v2.stl` | ramię haczyka prawy (grubość poniżej występu, Z 50,6) | 1,500 | 1,500 | [96.8, 0.0, 50.6] | 1.5 | OK |  |
| `ramka_blat_v2.stl` | ramię haczyka lewy (grubość poniżej występu, Z 50,6) | 1,500 | 1,500 | [-96.8, 0.0, 50.6] | 1.5 | OK |  |
| `ramka_blat_v2.stl` | ramię haczyka przedni (grubość poniżej występu, Z 50,6) | 1,500 | 1,500 | [50.0, -96.8, 50.6] | 1.5 | OK |  |
| `ramka_blat_v2.stl` | ramię haczyka tylny (grubość poniżej występu, Z 50,6) | 1,500 | 1,500 | [-50.0, 96.8, 50.6] | 1.5 | OK |  |
| `ramka_blat_v2.stl` | dno pod otworem słupka x=-75 (91,0 − 89,2) | 1,800 | 1,800 | [-75, 90.1, 55.0] | 1.5 | OK |  |
| `ramka_blat_v2.stl` | dno blatu pod otworem kołka x=-58 (4 − 3,8 = 0,2; R8 dopuszczone lokalnie) | 0,200 | 0,200 | [-58, 93.5, 59.7] | 0.2 | OK | R8/4.11: nie ścianka nośna, może przebić się na wylot |
| `ramka_blat_v2.stl` | dno pod otworem słupka x=75 (91,0 − 89,2) | 1,800 | 1,800 | [75, 90.1, 55.0] | 1.5 | OK |  |
| `ramka_blat_v2.stl` | dno blatu pod otworem kołka x=58 (4 − 3,8 = 0,2; R8 dopuszczone lokalnie) | 0,200 | 0,200 | [58, 93.5, 59.7] | 0.2 | OK | R8/4.11: nie ścianka nośna, może przebić się na wylot |
| `ramka_korpus_W_v2.stl` | ściana korpusu prawa | 2,500 | 2,500 | [98.75, 20, 30] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | ściana korpusu lewa | 2,500 | 2,500 | [-98.75, -40, 30] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | ściana korpusu przednia (poza napisem) | 2,500 | 2,500 | [80, -98.75, 30] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | ściana korpusu tylna | 2,500 | 2,500 | [20, 98.75, 30] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | ściana korpusu prawa za kieszenią zatrzasku | 1,500 | 1,500 | [99.25, 0, 53.85] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | ściana korpusu przednia za kieszenią zatrzasku | 1,500 | 1,500 | [50, -99.25, 53.85] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | ściana korpusu tylna za kieszenią zatrzasku | 1,500 | 1,500 | [-50, 99.25, 53.85] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | ściana korpusu lewa za kieszenią zatrzasku | 1,500 | 1,500 | [-99.25, 0, 53.85] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | ściana korpusu tylna między szczelinami (x=0) | 2,500 | 2,500 | [0, 98.75, 8] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | ściana korpusu prawa nad szczeliną y=0 (Z 10) | 2,500 | 2,500 | [98.75, 0, 10] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | ściana korpusu tylna pod skrzynką DC (Z 11) | 2,500 | 2,500 | [-67.5, 98.75, 11] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | ściana korpusu tylna między oknem DC a narożnikiem (x=−95) | 2,500 | 2,500 | [-95, 98.75, 26] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | ściana korpusu tylna między oknem USB a rowkiem | 1,900 | 1,904 | [51.05, 98.75, 24] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | dno obok rowka panelu i poza stadionem ((64,54)) | 3 | 3,000 | [64, 54, 1.5] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | dno między wlotami (y=0, x=−8) | 3 | 3,000 | [-8, 0, 1.5] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | dno skrzynki DC (Z 12…14) | 2 | 2,000 | [-67.5, 88, 13] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | sufit skrzynki DC (Z 38…40) | 2 | 2,000 | [-67.5, 88, 39] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | przednia ściana skrzynki DC (y 78…80) | 2 | 2,000 | [-67.5, 79, 26] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | lewa ściana skrzynki DC (x −97,5…−95,5; w ścianie korpusu łącznie 4,5) | 4,500 | 4,500 | [-96.5, 88, 26] | 1.5 | OK |  |
| `ramka_korpus_W_v2.stl` | ścianka bossa Pi (ø8 − ø2,1)/2 | 2,950 | 2,950 | [-43.98, -24.5, 6] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | ściana korpusu prawa | 2,500 | 2,500 | [98.75, 20, 30] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | ściana korpusu lewa | 2,500 | 2,500 | [-98.75, -40, 30] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | ściana korpusu przednia (poza napisem) | 2,500 | 2,500 | [80, -98.75, 30] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | ściana korpusu tylna | 2,500 | 2,500 | [20, 98.75, 30] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | ściana korpusu prawa za kieszenią zatrzasku | 1,500 | 1,500 | [99.25, 0, 53.85] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | ściana korpusu przednia za kieszenią zatrzasku | 1,500 | 1,500 | [50, -99.25, 53.85] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | ściana korpusu tylna za kieszenią zatrzasku | 1,500 | 1,500 | [-50, 99.25, 53.85] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | ściana korpusu lewa za kieszenią zatrzasku | 1,500 | 1,500 | [-99.25, 0, 53.85] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | ściana korpusu tylna między szczelinami (x=0) | 2,500 | 2,500 | [0, 98.75, 8] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | ściana korpusu prawa nad szczeliną y=0 (Z 10) | 2,500 | 2,500 | [98.75, 0, 10] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | ściana korpusu tylna pod skrzynką DC (Z 11) | 2,500 | 2,500 | [-67.5, 98.75, 11] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | ściana korpusu tylna między oknem DC a narożnikiem (x=−95) | 2,500 | 2,500 | [-95, 98.75, 26] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | ściana korpusu tylna między oknem USB a rowkiem | 1,900 | 1,904 | [51.05, 98.75, 24] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | dno obok rowka panelu i poza stadionem ((64,54)) | 3 | 3,000 | [64, 54, 1.5] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | dno między wlotami (y=0, x=−8) | 3 | 3,000 | [-8, 0, 1.5] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | dno skrzynki DC (Z 12…14) | 2 | 2,000 | [-67.5, 88, 13] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | sufit skrzynki DC (Z 38…40) | 2 | 2,000 | [-67.5, 88, 39] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | przednia ściana skrzynki DC (y 78…80) | 2 | 2,000 | [-67.5, 79, 26] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | lewa ściana skrzynki DC (x −97,5…−95,5; w ścianie korpusu łącznie 4,5) | 4,500 | 4,500 | [-96.5, 88, 26] | 1.5 | OK |  |
| `ramka_korpus_P_v2.stl` | ścianka bossa Pi (ø8 − ø2,1)/2 | 2,950 | 2,950 | [-43.98, -24.5, 6] | 1.5 | OK |  |
| `ramka_tulejka_dc_v2.stl` | ścianka tulejki (12 − 8,2)/2 | 1,900 | 1,899 | [-41, 94.05, 30] | 1.5 | OK | druk własny (żywica/PETG); dopuszczone < 1,5? — reguła 4.8 dotyczy PA12 SLS |

## Tabela F. Symulacja montażu (BVHTree.overlap + głębokość wnikania; krok 0,1 mm)

| Krok | Droga od | Pierwsze przecięcie na drodze (odległość od pozycji końcowej, co) | Max wnikanie na drodze | Ugięcie haczyka / pierwszy kontakt (dz) | Pozycja końcowa: kontakty (część, pary trójkątów, wnikanie) | Werdykt | Uwaga |
|---|---|---|---|---|---|---|---|
| korpus W: Pi+Bonnet (proxy) na bossy (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('korpus_W', 875, 0.0, None)] | OK |  |
| korpus W: dystans 1 na stadion (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('korpus_W', 58, 0.0, None)] | OK |  |
| korpus W: dystans 2 na stadion (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('korpus_W', 58, 0.0, None)] | OK |  |
| korpus W: dystans 3 na stadion (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('korpus_W', 58, 0.0, None)] | OK |  |
| korpus W: dystans 4 na stadion (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('korpus_W', 58, 0.0, None)] | OK |  |
| korpus W: panel (proxy) na dystanse (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('proxy_dystans_1', 81, 0.0, None), ('proxy_dystans_2', 81, 0.0, None), ('proxy_dystans_3', 81, 0.0, None), ('proxy_dystans_4', 81, 0.0, None)] | OK |  |
| dyfuzor (proxy) w kieszeń blatu (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('blat', 12, 0.0, None)] | OK |  |
| korpus W: blat na korpus (haczyki; z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | 0,800 / 6.3 | [('korpus_W', 526, 0.0, None)] | OK (ugięcie haczyka 0.80 ≤ 1.30) |  |
| korpus W: dyfuzor (w blacie) opuszczany razem z blatem | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [] | OK |  |
| czujnik Halla A (proxy) w kieszeń półki wkładki (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [] | OK |  |
| czujnik Halla B (proxy) w kieszeń półki wkładki (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [] | OK |  |
| czujnik Halla C (proxy) w kieszeń półki wkładki (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [] | OK |  |
| wkładka na kołki blatu (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('proxy_dyfuzor', 176, 0.0, None)] | OK |  |
| czujnik Halla A (w wkładce) opuszczany z wkładką | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('proxy_dyfuzor', 4, 0.0, None)] | OK |  |
| czujnik Halla B (w wkładce) opuszczany z wkładką | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('proxy_dyfuzor', 4, 0.0, None)] | OK |  |
| czujnik Halla C (w wkładce) opuszczany z wkładką | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('proxy_dyfuzor', 4, 0.0, None)] | OK |  |
| magnes ø5×2 w kieszeń blatu x=-58 (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [] | OK |  |
| magnes ø5×2 w otwór ucha wkładki x=-58 (z góry 20; wkładka na blacie z magnesem blatu) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [] | OK |  |
| magnes ø5×2 w kieszeń blatu x=58 (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [] | OK |  |
| magnes ø5×2 w otwór ucha wkładki x=58 (z góry 20; wkładka na blacie z magnesem blatu) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [] | OK |  |
| płytka poranna_n4 na wkładkę/kołek orientacyjny (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('wkladka', 758, 0.001, None)] | OK |  |
| płytka poranna_n5 na wkładkę/kołek orientacyjny (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('wkladka', 758, 0.001, None)] | OK |  |
| płytka poranna_n6 na wkładkę/kołek orientacyjny (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('wkladka', 758, 0.001, None)] | OK |  |
| płytka poranna na wkładkę/kołek orientacyjny (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('wkladka', 762, 0.001, None)] | OK |  |
| płytka wieczorna_n1 na wkładkę/kołek orientacyjny (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('wkladka', 756, 0.001, None)] | OK |  |
| płytka wieczorna_n2 na wkładkę/kołek orientacyjny (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('wkladka', 756, 0.001, None)] | OK |  |
| płytka wieczorna_n3 na wkładkę/kołek orientacyjny (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('wkladka', 756, 0.001, None)] | OK |  |
| płytka wieczorna na wkładkę/kołek orientacyjny (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('wkladka', 756, 0.001, None)] | OK |  |
| magnes A (proxy) w kieszeni płytki n1 — z płytką | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [] | OK |  |
| pokrywka na płytkę poranna_n4 (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | 0,400 / 2.0 | [] | OK (ugięcie garbu 0.40 ≤ 0.45) | garby 0,7 przechodzą przez bok płytki (luz 0,3): dopuszczalne ugięcie kołnierza 0,4 (zatrzask), nie na końcu drogi |
| pokrywka na płytkę poranna_n5 (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | 0,400 / 2.0 | [] | OK (ugięcie garbu 0.40 ≤ 0.45) | garby 0,7 przechodzą przez bok płytki (luz 0,3): dopuszczalne ugięcie kołnierza 0,4 (zatrzask), nie na końcu drogi |
| pokrywka na płytkę poranna_n6 (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | 0,400 / 2.0 | [] | OK (ugięcie garbu 0.40 ≤ 0.45) | garby 0,7 przechodzą przez bok płytki (luz 0,3): dopuszczalne ugięcie kołnierza 0,4 (zatrzask), nie na końcu drogi |
| pokrywka na płytkę poranna (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | 0,400 / 2.0 | [] | OK (ugięcie garbu 0.40 ≤ 0.45) | garby 0,7 przechodzą przez bok płytki (luz 0,3): dopuszczalne ugięcie kołnierza 0,4 (zatrzask), nie na końcu drogi |
| pokrywka na płytkę wieczorna_n1 (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | 0,400 / 2.0 | [] | OK (ugięcie garbu 0.40 ≤ 0.45) | garby 0,7 przechodzą przez bok płytki (luz 0,3): dopuszczalne ugięcie kołnierza 0,4 (zatrzask), nie na końcu drogi |
| pokrywka na płytkę wieczorna_n2 (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | 0,400 / 2.0 | [] | OK (ugięcie garbu 0.40 ≤ 0.45) | garby 0,7 przechodzą przez bok płytki (luz 0,3): dopuszczalne ugięcie kołnierza 0,4 (zatrzask), nie na końcu drogi |
| pokrywka na płytkę wieczorna_n3 (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | 0,400 / 2.0 | [] | OK (ugięcie garbu 0.40 ≤ 0.45) | garby 0,7 przechodzą przez bok płytki (luz 0,3): dopuszczalne ugięcie kołnierza 0,4 (zatrzask), nie na końcu drogi |
| pokrywka na płytkę wieczorna (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | 0,400 / 2.0 | [] | OK (ugięcie garbu 0.40 ≤ 0.45) | garby 0,7 przechodzą przez bok płytki (luz 0,3): dopuszczalne ugięcie kołnierza 0,4 (zatrzask), nie na końcu drogi |
| korpus W: tulejka DC w otwór ściany skrzynki (od kieszeni, +X 20) | [-20.0, 0.0, 0.0] | None | 0,000 | — / None | [('korpus_W', 2422, 0.001, None)] | OK | luz 0 → oczekiwany styk walca z otworem (wnikanie ≤ sagitta tesselacji) |
| korpus W: gniazdo DC (flansza ø14 + gwint ø8) przez tulejkę (od kieszeni, +X 20) | [-20.0, 0.0, 0.0] | None | 0,000 | — / None | [('tulejka_dc', 302, 0.0, None)] | OK |  |
| korpus W: nakrętka+korpus gniazda DC (proxy) od wnętrza (−X 20) | [20.0, 0.0, 0.0] | None | 0,000 | — / None | [('korpus_W', 603, 0.0, None), ('tulejka_dc', 719, 0.0, None)] | OK |  |
| korpus W: gniazdo DC przez okno kieszeni (z tyłu, −Y 30; x −20) | [0.0, 30.0, 0.0] | None | 0,000 | — / None | [] | OK |  |
| korpus W: wtyk kątowy (26 + kabel ku +Y przez okno): wsuwanie na gniazdo (+X 12) | [-12.0, 0.0, 0.0] | None | 0,000 | — / None | [('gniazdo_DC_wlasne', 48, 0.0, None)] | OK |  |
| korpus W: wtyk kątowy: wejście przez okno (z tyłu, −Y 30; x −12) | [0.0, 30.0, 0.0] | None | 0,000 | — / None | [] | OK |  |
| korpus W: wtyk prosty 40 + kabel 12 w osi: pozycja końcowa i wsuwanie (+X 12) — INFORMACYJNIE | [-12.0, 0.0, 0.0] | (12.0, ['korpus_W(wierzch. 1.500, transw. 194 par, zanurz. 32.195)']) | 32,195 | — / None | [('korpus_W', 50, 14.613, ('wtyk_prosty', (-97.0, 92.0, 30.0))), ('gniazdo_DC_wlasne', 48, 0.0, None)] | INFORMACYJNIE: PRZECIECIE | 4.11 liczy od lica −42 (zapas 1,5); tu lico gniazda −45 (kołnierz tulejki 1 + flansza gniazda 2) → kabel w osi wchodzi 1,5 w lewą ścianę skrzynki; kabel realnie zagina się wcześniej; rekomendowany wtyk kątowy |
| korpus W: gniazdo USB (proxy, korpus 16×20×14) od wnętrza (+Y 20) — INFORMACYJNIE | [0.0, -20.0, 0.0] | (20.0, ['proxy_dystans_4(wierzch. 0.000, transw. 261 par, zanurz. 23.000)']) | 23,000 | — / None | [('korpus_W', 7, 0.0, None)] | INFORMACYJNIE: PRZECIECIE | droga 20 mm po prostej przecina dystans (60,60) stojący 14,3 przed bryłą; realnie wystarczy ≤ 8 mm ruchu (następny wiersz) |
| korpus W: gniazdo USB (proxy) od wnętrza (+Y 8) | [0.0, -8.0, 0.0] | None | 0,000 | — / None | [('korpus_W', 7, 0.0, None)] | OK |  |
| korpus W: wtyk DC Bonnetu −X (proxy): wsuwanie na gniazdo (+X 7) | [-7.0, 0.0, 0.0] | None | 0,000 | — / None | [] | OK | zapas do ściany 7,5 (D10) → wsuwanie ≤ 7 po prostej; dłuższa droga wymaga wpięcia wtyku przed przykręceniem Pi |
| korpus W: wtyk DC Bonnetu −X (proxy): wsuwanie (+X 20) — INFORMACYJNIE | [-20.0, 0.0, 0.0] | (20.0, ['korpus_W(wierzch. 0.000, transw. 20 par, zanurz. 78.000)']) | 78,000 | — / None | [] | INFORMACYJNIE: PRZECIECIE | 20 mm po prostej przecina lewą ścianę (zapas 7,5, D10) |
| korpus W: wtyk DC Bonnetu −Y (x −45…−35, y −68…−28): wsuwanie (+Y 20) | [0.0, -20.0, 0.0] | None | 0,000 | — / None | [] | OK |  |
| korpus W: wtyk DC Bonnetu +Y (x −45…−35, y 28…68): wsuwanie (−Y 9; skrzynka DC 10 za wtykiem) | [0.0, 9.0, 0.0] | None | 0,000 | — / None | [] | OK |  |
| korpus W: wtyk DC Bonnetu +Y: wsuwanie (−Y 20) — INFORMACYJNIE | [0.0, 20.0, 0.0] | (20.0, ['korpus_W(wierzch. 0.000, transw. 134 par, zanurz. 11.000)']) | 11,000 | — / None | [] | INFORMACYJNIE: PRZECIECIE | 20 mm po prostej przecina skrzynkę DC (zapas 10, 4.11) |
| korpus W: złożenie końcowe — pary ze wspólnymi trójkątami (styk = wnikanie ≤ 0,05) | — | — | — | — | [('korpus', 'blat', 526, 0.0, None), ('korpus', 'tulejka', 2422, 0.001, None), ('korpus', 'pi', 875, 0.0, None), ('korpus', 'gniazdo_dc', 603, 0.0, None), ('korpus', 'gniazdo_usb', 7, 0.0, None), ('korpus', 'dystans_1', 58, 0.0, None), ('korpus', 'dystans_2', 58, 0.0, None), ('korpus', 'dystans_3', 58, 0.0, None), ('korpus', 'dystans_4', 58, 0.0, None), ('blat', 'dyfuzor', 12, 0.0, None), ('wkladka', 'plytka_n1', 756, 0.001, None), ('wkladka', 'dyfuzor', 176, 0.0, None), ('plytka_n1', 'magnes_A', 97, 0.0, None), ('tulejka', 'gniazdo_dc', 719, 0.0, None), ('dyfuzor', 'hall_A', 4, 0.0, None), ('dyfuzor', 'hall_B', 4, 0.0, None), ('dyfuzor', 'hall_C', 4, 0.0, None), ('panel', 'dystans_1', 81, 0.0, None), ('panel', 'dystans_2', 81, 0.0, None), ('panel', 'dystans_3', 81, 0.0, None), ('panel', 'dystans_4', 81, 0.0, None), ('pi', 'wtyk_bonnet', 3, 0.0, None)] | OK | |
| korpus P: Pi+Bonnet (proxy) na bossy (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('korpus_P', 875, 0.0, None)] | OK |  |
| korpus P: dystans 1 na stadion (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('korpus_P', 58, 0.0, None)] | OK |  |
| korpus P: dystans 2 na stadion (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('korpus_P', 58, 0.0, None)] | OK |  |
| korpus P: dystans 3 na stadion (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('korpus_P', 58, 0.0, None)] | OK |  |
| korpus P: dystans 4 na stadion (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('korpus_P', 58, 0.0, None)] | OK |  |
| korpus P: panel (proxy) na dystanse (z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [('proxy_dystans_1', 81, 0.0, None), ('proxy_dystans_2', 81, 0.0, None), ('proxy_dystans_3', 81, 0.0, None), ('proxy_dystans_4', 81, 0.0, None)] | OK |  |
| korpus P: blat na korpus (haczyki; z góry 20) | [0.0, 0.0, 20.0] | None | 0,000 | 0,800 / 6.3 | [('korpus_P', 526, 0.0, None)] | OK (ugięcie haczyka 0.80 ≤ 1.30) |  |
| korpus P: dyfuzor (w blacie) opuszczany razem z blatem | [0.0, 0.0, 20.0] | None | 0,000 | — / None | [] | OK |  |
| korpus P: tulejka DC w otwór ściany skrzynki (od kieszeni, +X 20) | [-20.0, 0.0, 0.0] | None | 0,000 | — / None | [('korpus_P', 2422, 0.001, None)] | OK | luz 0 → oczekiwany styk walca z otworem (wnikanie ≤ sagitta tesselacji) |
| korpus P: gniazdo DC (flansza ø14 + gwint ø8) przez tulejkę (od kieszeni, +X 20) | [-20.0, 0.0, 0.0] | None | 0,000 | — / None | [('tulejka_dc', 302, 0.0, None)] | OK |  |
| korpus P: nakrętka+korpus gniazda DC (proxy) od wnętrza (−X 20) | [20.0, 0.0, 0.0] | None | 0,000 | — / None | [('korpus_P', 603, 0.0, None), ('tulejka_dc', 719, 0.0, None)] | OK |  |
| korpus P: gniazdo DC przez okno kieszeni (z tyłu, −Y 30; x −20) | [0.0, 30.0, 0.0] | None | 0,000 | — / None | [] | OK |  |
| korpus P: wtyk kątowy (26 + kabel ku +Y przez okno): wsuwanie na gniazdo (+X 12) | [-12.0, 0.0, 0.0] | None | 0,000 | — / None | [('gniazdo_DC_wlasne', 48, 0.0, None)] | OK |  |
| korpus P: wtyk kątowy: wejście przez okno (z tyłu, −Y 30; x −12) | [0.0, 30.0, 0.0] | None | 0,000 | — / None | [] | OK |  |
| korpus P: wtyk prosty 40 + kabel 12 w osi: pozycja końcowa i wsuwanie (+X 12) — INFORMACYJNIE | [-12.0, 0.0, 0.0] | (12.0, ['korpus_P(wierzch. 1.500, transw. 194 par, zanurz. 32.195)']) | 32,195 | — / None | [('korpus_P', 50, 14.613, ('wtyk_prosty', (-97.0, 92.0, 30.0))), ('gniazdo_DC_wlasne', 48, 0.0, None)] | INFORMACYJNIE: PRZECIECIE | 4.11 liczy od lica −42 (zapas 1,5); tu lico gniazda −45 (kołnierz tulejki 1 + flansza gniazda 2) → kabel w osi wchodzi 1,5 w lewą ścianę skrzynki; kabel realnie zagina się wcześniej; rekomendowany wtyk kątowy |
| korpus P: gniazdo USB (proxy, korpus 16×20×14) od wnętrza (+Y 20) — INFORMACYJNIE | [0.0, -20.0, 0.0] | (20.0, ['proxy_dystans_4(wierzch. 0.000, transw. 261 par, zanurz. 23.000)']) | 23,000 | — / None | [('korpus_P', 7, 0.0, None)] | INFORMACYJNIE: PRZECIECIE | droga 20 mm po prostej przecina dystans (60,60) stojący 14,3 przed bryłą; realnie wystarczy ≤ 8 mm ruchu (następny wiersz) |
| korpus P: gniazdo USB (proxy) od wnętrza (+Y 8) | [0.0, -8.0, 0.0] | None | 0,000 | — / None | [('korpus_P', 7, 0.0, None)] | OK |  |
| korpus P: wtyk DC Bonnetu −X (proxy): wsuwanie na gniazdo (+X 7) | [-7.0, 0.0, 0.0] | None | 0,000 | — / None | [] | OK | zapas do ściany 7,5 (D10) → wsuwanie ≤ 7 po prostej; dłuższa droga wymaga wpięcia wtyku przed przykręceniem Pi |
| korpus P: wtyk DC Bonnetu −X (proxy): wsuwanie (+X 20) — INFORMACYJNIE | [-20.0, 0.0, 0.0] | (20.0, ['korpus_P(wierzch. 0.000, transw. 20 par, zanurz. 78.000)']) | 78,000 | — / None | [] | INFORMACYJNIE: PRZECIECIE | 20 mm po prostej przecina lewą ścianę (zapas 7,5, D10) |
| korpus P: wtyk DC Bonnetu −Y (x −45…−35, y −68…−28): wsuwanie (+Y 20) | [0.0, -20.0, 0.0] | None | 0,000 | — / None | [] | OK |  |
| korpus P: wtyk DC Bonnetu +Y (x −45…−35, y 28…68): wsuwanie (−Y 9; skrzynka DC 10 za wtykiem) | [0.0, 9.0, 0.0] | None | 0,000 | — / None | [] | OK |  |
| korpus P: wtyk DC Bonnetu +Y: wsuwanie (−Y 20) — INFORMACYJNIE | [0.0, 20.0, 0.0] | (20.0, ['korpus_P(wierzch. 0.000, transw. 134 par, zanurz. 11.000)']) | 11,000 | — / None | [] | INFORMACYJNIE: PRZECIECIE | 20 mm po prostej przecina skrzynkę DC (zapas 10, 4.11) |
| korpus P: odbiornik USB (proxy) w port Pi (−X 20) | [20.0, 0.0, 0.0] | None | 0,000 | — / None | [] | OK |  |
| korpus P: złożenie końcowe — pary ze wspólnymi trójkątami (styk = wnikanie ≤ 0,05) | — | — | — | — | [('korpus', 'blat', 526, 0.0, None), ('korpus', 'tulejka', 2422, 0.001, None), ('korpus', 'pi', 875, 0.0, None), ('korpus', 'gniazdo_dc', 603, 0.0, None), ('korpus', 'gniazdo_usb', 7, 0.0, None), ('korpus', 'dystans_1', 58, 0.0, None), ('korpus', 'dystans_2', 58, 0.0, None), ('korpus', 'dystans_3', 58, 0.0, None), ('korpus', 'dystans_4', 58, 0.0, None), ('blat', 'dyfuzor', 12, 0.0, None), ('wkladka', 'plytka_n1', 756, 0.001, None), ('wkladka', 'dyfuzor', 176, 0.0, None), ('plytka_n1', 'magnes_A', 97, 0.0, None), ('tulejka', 'gniazdo_dc', 719, 0.0, None), ('dyfuzor', 'hall_A', 4, 0.0, None), ('dyfuzor', 'hall_B', 4, 0.0, None), ('dyfuzor', 'hall_C', 4, 0.0, None), ('panel', 'dystans_1', 81, 0.0, None), ('panel', 'dystans_2', 81, 0.0, None), ('panel', 'dystans_3', 81, 0.0, None), ('panel', 'dystans_4', 81, 0.0, None), ('pi', 'wtyk_bonnet', 3, 0.0, None), ('pi', 'odbiornik', 3, 0.0, None)] | OK | |

## Profil haczyków blatu (czubek w funkcji Z, promienie poziome; rampa od dołu)

- prawy: Z 51.60→97,000, Z 51.70→97,000, Z 51.80→97,000, Z 51.90→97,000, Z 52.00→97,000, Z 52.10→97,000, Z 52.20→97,000, Z 52.30→97,000, Z 52.40→97,000, Z 52.50→97,000, Z 52.60→97,000, Z 52.70→97,000, Z 52.80→97,000, Z 52.90→97,065, Z 53.00→97,195, Z 53.10→97,325, Z 53.20→97,455, Z 53.30→97,585, Z 53.40→97,715, Z 53.50→97,845, Z 53.60→97,975, Z 53.70→98,105, Z 53.80→98,235, Z 53.90→98,300, Z 54.00→98,300, Z 54.10→98,300, Z 54.20→98,300, Z 54.30→98,300, Z 54.40→98,300, Z 54.50→98,300, Z 54.60→98,300, Z 54.70→98,300, Z 54.80→98,300, Z 54.90→97,000, Z 55.00→97,000, Z 55.10→97,000, Z 55.20→97,000, Z 55.30→97,000, Z 55.40→97,000, Z 55.50→97,000, Z 55.60→97,000, Z 55.70→97,000, Z 55.80→97,000, Z 55.90→97,000, Z 56.00→97,000, Z 56.10→97,000
- lewy: Z 51.60→97,000, Z 51.70→97,000, Z 51.80→97,000, Z 51.90→97,000, Z 52.00→97,000, Z 52.10→97,000, Z 52.20→97,000, Z 52.30→97,000, Z 52.40→97,000, Z 52.50→97,000, Z 52.60→97,000, Z 52.70→97,000, Z 52.80→97,000, Z 52.90→97,065, Z 53.00→97,195, Z 53.10→97,325, Z 53.20→97,455, Z 53.30→97,585, Z 53.40→97,715, Z 53.50→97,845, Z 53.60→97,975, Z 53.70→98,105, Z 53.80→98,235, Z 53.90→98,300, Z 54.00→98,300, Z 54.10→98,300, Z 54.20→98,300, Z 54.30→98,300, Z 54.40→98,300, Z 54.50→98,300, Z 54.60→98,300, Z 54.70→98,300, Z 54.80→98,300, Z 54.90→97,000, Z 55.00→97,000, Z 55.10→97,000, Z 55.20→97,000, Z 55.30→97,000, Z 55.40→97,000, Z 55.50→97,000, Z 55.60→97,000, Z 55.70→97,000, Z 55.80→97,000, Z 55.90→97,000, Z 56.00→97,000, Z 56.10→97,000
- przedni: Z 51.60→97,000, Z 51.70→97,000, Z 51.80→97,000, Z 51.90→97,000, Z 52.00→97,000, Z 52.10→97,000, Z 52.20→97,000, Z 52.30→97,000, Z 52.40→97,000, Z 52.50→97,000, Z 52.60→97,000, Z 52.70→97,000, Z 52.80→97,000, Z 52.90→97,065, Z 53.00→97,195, Z 53.10→97,325, Z 53.20→97,455, Z 53.30→97,585, Z 53.40→97,715, Z 53.50→97,845, Z 53.60→97,975, Z 53.70→98,105, Z 53.80→98,235, Z 53.90→98,300, Z 54.00→98,300, Z 54.10→98,300, Z 54.20→98,300, Z 54.30→98,300, Z 54.40→98,300, Z 54.50→98,300, Z 54.60→98,300, Z 54.70→98,300, Z 54.80→98,300, Z 54.90→97,000, Z 55.00→97,000, Z 55.10→97,000, Z 55.20→97,000, Z 55.30→97,000, Z 55.40→97,000, Z 55.50→97,000, Z 55.60→97,000, Z 55.70→97,000, Z 55.80→97,000, Z 55.90→97,000, Z 56.00→97,000, Z 56.10→97,000
- tylny: Z 51.60→97,000, Z 51.70→97,000, Z 51.80→97,000, Z 51.90→97,000, Z 52.00→97,000, Z 52.10→97,000, Z 52.20→97,000, Z 52.30→97,000, Z 52.40→97,000, Z 52.50→97,000, Z 52.60→97,000, Z 52.70→97,000, Z 52.80→97,000, Z 52.90→97,065, Z 53.00→97,195, Z 53.10→97,325, Z 53.20→97,455, Z 53.30→97,585, Z 53.40→97,715, Z 53.50→97,845, Z 53.60→97,975, Z 53.70→98,105, Z 53.80→98,235, Z 53.90→98,300, Z 54.00→98,300, Z 54.10→98,300, Z 54.20→98,300, Z 54.30→98,300, Z 54.40→98,300, Z 54.50→98,300, Z 54.60→98,300, Z 54.70→98,300, Z 54.80→98,300, Z 54.90→97,000, Z 55.00→97,000, Z 55.10→97,000, Z 55.20→97,000, Z 55.30→97,000, Z 55.40→97,000, Z 55.50→97,000, Z 55.60→97,000, Z 55.70→97,000, Z 55.80→97,000, Z 55.90→97,000, Z 56.00→97,000, Z 56.10→97,000