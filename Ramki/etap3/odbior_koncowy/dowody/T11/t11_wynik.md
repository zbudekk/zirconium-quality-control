# T11 - Stare plytki - wynik (odbior koncowy etapu 3, 21.11.2026)

WERDYKT T11: ZAL - N = 40 z 40 skanow *_r54 przez aplikacje; uklad rozpoznany 40 z 40 (P2 24 z 24, P3a 16 z 16), uklad_zrodlo auto 40 z 40; ostrzezenia o ukladzie: z nazwa 0, bez nazwy (FAIL skanu) 0; zielone przy zlym ukladzie 0 (0 z 0 skanow; T2 poz. 7: zielonych 0); skany.uklad zapisany 40 z 40; czesc A: auto_uklad bez_numeru 40 z 40, zle_ale_pewny 0 (z_numerem 16 z 16 - plan podaje 40 z 40), testy 45 passed / 0 failed; O6 = informacja (druga galaz kryterium niespelnialna w programie); kod programu 0

Paczka 0.3.1 (commit 571e186), instalacja wspolna, program z wlasnym plikiem ustawien; pelny protokol: WYNIK.md.

## Kryterium (plan etapu, sekcja 7)

- uklad rozpoznany albo ostrzezenie z nazwa wlasciwego ukladu: ZAL pierwsza galezia - rozpoznane 40 z 40; ostrzezen o
  ukladzie 0 (z nazwa 0, bez nazwy 0 = FAIL skanu 0 z 40);
- 0 zielonych przy zlym ukladzie: ZAL - skanow ze zlym ukladem 0, zielonych na nich 0 (odsylacz: T2 pozycja 7, zielonych 0);
- uklad zapisany w skany: ZAL - 40 z 40 (uklad_zrodlo auto 40 z 40).

O6 (informacja): druga galaz kryterium jest w programie niespelnialna (komunikat niezgodny_uklad nie ma nazwy ukladu).

## Liczniki (t11_liczniki.txt)

```
skanow w dzienniku symulatora (rodzaj dobry): 40
wierszy w tabeli skany: 40 (spoza dziennika symulatora: 0; sha16 z wiecej niz 1 wierszem: 0)
skany z dziennika z wierszem w skany: 40 z 40 (bez wiersza = NIE ZMIERZONO: 0)
(a) uklad rozpoznany (skany.uklad = plytka z prawdy, status inny niz niezgodny_uklad, uklad_zgodny inny niz 0): 40 z 40
    uklad_zrodlo = auto: 40 z 40
    uklad zapisany, ale inny niz w prawdzie: 0
    ostrzezenie o ukladzie Z nazwa wlasciwego ukladu: 0
    ostrzezenie o ukladzie BEZ nazwy wlasciwego ukladu (FAIL skanu): 0
(b) skany ze zlym ukladem (niezgodny_uklad / uklad_zgodny = 0 / uklad inny niz prawda): 0; zielonych na nich: 0 (skanow z zielonymi: 0)
(c) skany.uklad niepusty: 40 z 40
informacyjnie: status plytka_nie_z_trybu: 20 skanow, zielonych na nich: 55; zielonych razem na wszystkich skanach: 113; numer plytki = prawda: 24 z 40
    P2 okragla_poranna_r54: rozpoznane 6 z 6
    P2 okragla_wieczorna_r54: rozpoznane 6 z 6
    P2 poranna_r54: rozpoznane 6 z 6
    P2 wieczorna_r54: rozpoznane 6 z 6
    P3a okragla_poranna_r54: rozpoznane 6 z 6
    P3a okragla_wieczorna_r54: rozpoznane 6 z 6
    P3a poranna_r54: rozpoznane 2 z 2
    P3a wieczorna_r54: rozpoznane 2 z 2
```

## Czesc A

- krok 1 (auto_uklad.py, 40 skanow): bez_numeru ok 40 z 40, zle_ale_pewny 0; z_numerem ok 16 z 16, zle_ale_pewny 0 (przebieg
  tylko dla 16 plytek kwadratowych; plan podaje 40 z 40 - liczba planu do poprawy); kod 0.
- krok 4 (testy): 45 passed, 174 deselected, kod 0 (polecenie planu, kod z repo); 45 passed, 174 deselected, kod 0
  (pytest_instalacja.py, WERDYKT ZRODLA KODU: INSTALACJA, 51 modulow z instalacji, 0 z repo).

## Tabela skan po skanie

K-TRYB = pytanie programu o trybie (nie o ukladzie): "Plytka nie z tego trybu" / "To plytka poranna, a program pracuje w trybie
"Wieczor". Skan jest zablokowany: nic nie jest zielone i nie mozna zapisywac decyzji." (tekst z kodu instalacji dla statusu z bazy;
ekranu nie odczytywano). "Gniazd zielonych (baza)" = prace.status_gniazda = 'zielony'.

| Nr | sha16 skanu | Zestaw | Uklad wg prawdy | Uklad rozpoznany przez program | Rozpoznany = prawda | Status skanu | Ostrzezenie o ukladzie | Zawiera nazwe wlasciwego ukladu | Gniazd zielonych (baza) | Prac | skany.uklad (zrodlo, uklad_zgodny) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | a33966994b515b9e | P2 | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 3 | 9 | okragla_poranna_r54 (auto, 1) |
| 2 | af212769571c0d65 | P2 | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 4 | 9 | okragla_poranna_r54 (auto, 1) |
| 3 | a5c5683e20431cf3 | P2 | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 4 | 9 | okragla_poranna_r54 (auto, 1) |
| 4 | 5e03ed10436c2b30 | P2 | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 5 | 10 | okragla_poranna_r54 (auto, 1) |
| 5 | 40f034fd7d24fbcb | P2 | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 3 | 12 | okragla_poranna_r54 (auto, 1) |
| 6 | 6e60a2f8be92efe5 | P2 | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 3 | 9 | okragla_poranna_r54 (auto, 1) |
| 7 | ec033c0713e90c42 | P2 | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 5 | 11 | okragla_wieczorna_r54 (auto, 1) |
| 8 | 65df2f5ed75a75c9 | P2 | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 3 | 9 | okragla_wieczorna_r54 (auto, 1) |
| 9 | 8358e17160a25742 | P2 | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | przyjety | brak | nie dotyczy | 4 | 10 | okragla_wieczorna_r54 (auto, 1) |
| 10 | b0aabeec69834bca | P2 | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 3 | 10 | okragla_wieczorna_r54 (auto, 1) |
| 11 | 842d039b1fc1020c | P2 | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | przyjety | brak | nie dotyczy | 3 | 10 | okragla_wieczorna_r54 (auto, 1) |
| 12 | 9d5eeb980330c768 | P2 | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | przyjety | brak | nie dotyczy | 7 | 11 | okragla_wieczorna_r54 (auto, 1) |
| 13 | 75fa520430894f99 | P2 | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 1 | 8 | poranna_r54 (auto, 1) |
| 14 | b03385ae8316e226 | P2 | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 3 | 8 | poranna_r54 (auto, 1) |
| 15 | 823181c04ea8f815 | P2 | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 3 | 10 | poranna_r54 (auto, 1) |
| 16 | b75451bfe836239b | P2 | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 5 | 10 | poranna_r54 (auto, 1) |
| 17 | 007e56008bd77efb | P2 | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 3 | 11 | poranna_r54 (auto, 1) |
| 18 | b7dfa66ec8a53eb3 | P2 | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 4 | 10 | poranna_r54 (auto, 1) |
| 19 | 37b6d5f5a6f45340 | P2 | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 4 | 9 | wieczorna_r54 (auto, 1) |
| 20 | f20136b8b0af6e00 | P2 | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 0 | 9 | wieczorna_r54 (auto, 1) |
| 21 | 7e2cb93bbeaf4701 | P2 | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 4 | 10 | wieczorna_r54 (auto, 1) |
| 22 | 9a1cc0ad42a1b9b0 | P2 | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 2 | 11 | wieczorna_r54 (auto, 1) |
| 23 | 9cc2bd761deb672b | P2 | wieczorna_r54 | wieczorna_r54 | TAK | przyjety | brak | nie dotyczy | 6 | 9 | wieczorna_r54 (auto, 1) |
| 24 | 1745b6260092155c | P2 | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 7 | 11 | wieczorna_r54 (auto, 1) |
| 25 | 5283ca8eabec7b56 | P3a | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 5 | 10 | okragla_poranna_r54 (auto, 1) |
| 26 | c34cb8aea9d7521d | P3a | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 4 | 11 | okragla_poranna_r54 (auto, 1) |
| 27 | 2b3f8513e75dbc18 | P3a | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 2 | 14 | okragla_poranna_r54 (auto, 1) |
| 28 | 5acb59ca6e629bdd | P3a | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 0 | 11 | okragla_poranna_r54 (auto, 1) |
| 29 | 71df6882795263d3 | P3a | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 0 | 11 | okragla_poranna_r54 (auto, 1) |
| 30 | 27f3b336d128b75e | P3a | okragla_poranna_r54 | okragla_poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 0 | 9 | okragla_poranna_r54 (auto, 1) |
| 31 | 15765b8dc8c550ff | P3a | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 2 | 12 | okragla_wieczorna_r54 (auto, 1) |
| 32 | 3af0bf2e971a0fb3 | P3a | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 0 | 9 | okragla_wieczorna_r54 (auto, 1) |
| 33 | e6681afc6aff4161 | P3a | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 1 | 12 | okragla_wieczorna_r54 (auto, 1) |
| 34 | 0d01a86e2bcffb6f | P3a | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | przyjety | brak | nie dotyczy | 3 | 7 | okragla_wieczorna_r54 (auto, 1) |
| 35 | f8bf9a17bacae2a9 | P3a | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 1 | 8 | okragla_wieczorna_r54 (auto, 1) |
| 36 | efc49cb95972ce92 | P3a | okragla_wieczorna_r54 | okragla_wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 0 | 15 | okragla_wieczorna_r54 (auto, 1) |
| 37 | 7d134f6dfa68ea80 | P3a | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 1 | 15 | poranna_r54 (auto, 1) |
| 38 | cad653fc6eda187d | P3a | poranna_r54 | poranna_r54 | TAK | plytka_nie_z_trybu | brak (K-TRYB) | nie dotyczy | 2 | 12 | poranna_r54 (auto, 1) |
| 39 | 5b09c9516ebe0634 | P3a | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 2 | 12 | wieczorna_r54 (auto, 1) |
| 40 | c5d76faa2066aa63 | P3a | wieczorna_r54 | wieczorna_r54 | TAK | do_powtorzenia | brak | nie dotyczy | 1 | 10 | wieczorna_r54 (auto, 1) |
