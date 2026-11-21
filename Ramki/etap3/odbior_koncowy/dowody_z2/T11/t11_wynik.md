# T11 - liczniki i tabela skan po skanie (commit wydania 0fedbf6, czesc B z powtorki 21.11.2026 20:14; zrodla: sql_odczyt.py, t11_prawda.txt, t11_symulator.json, auto_uklad.json z czesci A 17:48; skrypt sprawdz_t11.py)

```
A bez_numeru z rekordow: ok 40 z 40, zle_ale_pewny 0 | podsumowanie narzedzia: ok 40 z 40, zle_ale_pewny 0 | zgodne: TAK
A z_numerem z rekordow: ok 16 z 16, zle_ale_pewny 0 | podsumowanie narzedzia: ok 16 z 16, zle_ale_pewny 0 | zgodne: TAK
prawda: 40 skanow, roznych sha16 40
dziennik: dobrych zapisow 40, roznych sha16 40, spoza prawdy 0
skany (TSV): wierszy 40, roznych sha16 40, spoza dziennika 0, sha16 z wiecej niz 1 wierszem 0
(n) skany z dziennika z wierszem w skany: 40 z 40 (bez wiersza = NIE ZMIERZONO: 0)
(a) uklad rozpoznany (skany.uklad = plytka z prawdy, status inny niz niezgodny_uklad, uklad_zgodny inny niz 0): 40 z 40
    uklad_zrodlo = auto: 40 z 40
    uklad zapisany, ale inny niz w prawdzie: 0
(b) skany ze zlym ukladem (niezgodny_uklad / uklad_zgodny = 0 / uklad inny niz prawda): 0; zielonych na nich: 0
(c) skany.uklad niepusty: 40 z 40
    grupa status / uklad / zrodlo / zgodny: do_powtorzenia / okragla_wieczorna_r54 / auto / 1: 8
    grupa status / uklad / zrodlo / zgodny: do_powtorzenia / wieczorna_r54 / auto / 1: 7
    grupa status / uklad / zrodlo / zgodny: plytka_nie_z_trybu / okragla_poranna_r54 / auto / 1: 12
    grupa status / uklad / zrodlo / zgodny: plytka_nie_z_trybu / poranna_r54 / auto / 1: 8
    grupa status / uklad / zrodlo / zgodny: przyjety / okragla_wieczorna_r54 / auto / 1: 4
    grupa status / uklad / zrodlo / zgodny: przyjety / wieczorna_r54 / auto / 1: 1
    P2 okragla_poranna_r54: rozpoznane 6 z 6
    P2 okragla_wieczorna_r54: rozpoznane 6 z 6
    P2 poranna_r54: rozpoznane 6 z 6
    P2 wieczorna_r54: rozpoznane 6 z 6
    P3a okragla_poranna_r54: rozpoznane 6 z 6
    P3a okragla_wieczorna_r54: rozpoznane 6 z 6
    P3a poranna_r54: rozpoznane 2 z 2
    P3a wieczorna_r54: rozpoznane 2 z 2
czas_s (kolumna skany.czas_s; nie jest kryterium): min 12.4, mediana 25.2, max 50.6, pierwszy skan 50.6
informacyjnie: zielonych razem 114; na skanach plytka_nie_z_trybu (20 skanow): 56
```

| Nr | sha16 skanu | Zestaw | Skan syntetyczny | Uklad wg prawdy | Uklad w bazie (`skany.uklad`) | Rozpoznany = prawda | Status skanu | uklad_zrodlo, uklad_zgodny | Gniazd zielonych (baza) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | a33966994b515b9e | P2 | skan_okragla_poranna_r54_n9_s0200.stl | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 3 |
| 2 | af212769571c0d65 | P2 | skan_okragla_poranna_r54_n9_s0201.stl | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 4 |
| 3 | a5c5683e20431cf3 | P2 | skan_okragla_poranna_r54_n9_s0202.stl | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 4 |
| 4 | 5e03ed10436c2b30 | P2 | skan_okragla_poranna_r54_n9_s0203.stl | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 5 |
| 5 | 40f034fd7d24fbcb | P2 | skan_okragla_poranna_r54_n9_s0204.stl | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 3 |
| 6 | 6e60a2f8be92efe5 | P2 | skan_okragla_poranna_r54_n9_s0205.stl | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 3 |
| 7 | ec033c0713e90c42 | P2 | skan_okragla_wieczorna_r54_n8_s0100.stl | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | auto, 1 | 5 |
| 8 | 65df2f5ed75a75c9 | P2 | skan_okragla_wieczorna_r54_n8_s0101.stl | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | auto, 1 | 3 |
| 9 | 8358e17160a25742 | P2 | skan_okragla_wieczorna_r54_n8_s0102.stl | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | przyjety | auto, 1 | 4 |
| 10 | b0aabeec69834bca | P2 | skan_okragla_wieczorna_r54_n8_s0103.stl | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | auto, 1 | 3 |
| 11 | 842d039b1fc1020c | P2 | skan_okragla_wieczorna_r54_n8_s0104.stl | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | przyjety | auto, 1 | 3 |
| 12 | 9d5eeb980330c768 | P2 | skan_okragla_wieczorna_r54_n8_s0105.stl | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | przyjety | auto, 1 | 7 |
| 13 | 75fa520430894f99 | P2 | skan_poranna_r54_n4_s0200.stl | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 1 |
| 14 | b03385ae8316e226 | P2 | skan_poranna_r54_n4_s0201.stl | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 3 |
| 15 | 823181c04ea8f815 | P2 | skan_poranna_r54_n4_s0202.stl | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 3 |
| 16 | b75451bfe836239b | P2 | skan_poranna_r54_n4_s0203.stl | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 5 |
| 17 | 007e56008bd77efb | P2 | skan_poranna_r54_n5_s0205.stl | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 3 |
| 18 | b7dfa66ec8a53eb3 | P2 | skan_poranna_r54_n6_s0204.stl | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 4 |
| 19 | 37b6d5f5a6f45340 | P2 | skan_wieczorna_r54_n1_s0101.stl | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | auto, 1 | 4 |
| 20 | f20136b8b0af6e00 | P2 | skan_wieczorna_r54_n1_s0105.stl | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | auto, 1 | 0 |
| 21 | 7e2cb93bbeaf4701 | P2 | skan_wieczorna_r54_n2_s0102.stl | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | auto, 1 | 4 |
| 22 | 9a1cc0ad42a1b9b0 | P2 | skan_wieczorna_r54_n2_s0103.stl | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | auto, 1 | 2 |
| 23 | 9cc2bd761deb672b | P2 | skan_wieczorna_r54_n3_s0100.stl | wieczorna_r54 | wieczorna_r54 | TAK | przyjety | auto, 1 | 6 |
| 24 | 1745b6260092155c | P2 | skan_wieczorna_r54_n3_s0104.stl | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | auto, 1 | 7 |
| 25 | 5283ca8eabec7b56 | P3a | skan_okragla_poranna_r54_n9_s0310.stl | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 5 |
| 26 | c34cb8aea9d7521d | P3a | skan_okragla_poranna_r54_n9_s0311.stl | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 4 |
| 27 | 2b3f8513e75dbc18 | P3a | skan_okragla_poranna_r54_n9_s0312.stl | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 3 |
| 28 | 5acb59ca6e629bdd | P3a | skan_okragla_poranna_r54_n9_s0313.stl | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 0 |
| 29 | 71df6882795263d3 | P3a | skan_okragla_poranna_r54_n9_s0350.stl | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 0 |
| 30 | 27f3b336d128b75e | P3a | skan_okragla_poranna_r54_n9_s0351.stl | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 0 |
| 31 | 15765b8dc8c550ff | P3a | skan_okragla_wieczorna_r54_n8_s0300.stl | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | auto, 1 | 2 |
| 32 | 3af0bf2e971a0fb3 | P3a | skan_okragla_wieczorna_r54_n8_s0301.stl | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | auto, 1 | 0 |
| 33 | e6681afc6aff4161 | P3a | skan_okragla_wieczorna_r54_n8_s0302.stl | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | auto, 1 | 1 |
| 34 | 0d01a86e2bcffb6f | P3a | skan_okragla_wieczorna_r54_n8_s0303.stl | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | przyjety | auto, 1 | 3 |
| 35 | f8bf9a17bacae2a9 | P3a | skan_okragla_wieczorna_r54_n8_s0340.stl | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | auto, 1 | 1 |
| 36 | efc49cb95972ce92 | P3a | skan_okragla_wieczorna_r54_n8_s0341.stl | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | auto, 1 | 0 |
| 37 | 7d134f6dfa68ea80 | P3a | skan_poranna_r54_n4_s0331.stl | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 1 |
| 38 | cad653fc6eda187d | P3a | skan_poranna_r54_n5_s0330.stl | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | auto, 1 | 2 |
| 39 | 5b09c9516ebe0634 | P3a | skan_wieczorna_r54_n1_s0320.stl | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | auto, 1 | 2 |
| 40 | c5d76faa2066aa63 | P3a | skan_wieczorna_r54_n2_s0321.stl | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | auto, 1 | 1 |
