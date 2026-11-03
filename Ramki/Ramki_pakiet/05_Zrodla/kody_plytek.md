# Kody płytek (D11, R4, R57)

Numer płytki n = A + 2·B + 4·C + 8·D [R57: 4. bit D]. Na płytkach kwadratowych bit = 1 oznacza magnes wklejony w kieszeni narożnika (A przód‑lewy, B tył‑lewy, C tył‑prawy; narożnik D z wycięciem bez kieszeni; bit D nie ma kieszeni i na n1–n6 nie występuje). Ten sam numer kodują dołki ø2 × 1 na wierzchu — dołek jest tylko dla bitu = 1; pozycje (x, y) z `uklad_gniazd_<typ>.json → code_dimples`: kwadrat wieczorna A (-45, -36), B (-45, -33), C (-45, -30), D (-45, -27); kwadrat poranna A (-45, -36), B (-45, -33), C (-45, -30), D (-45, -27); okrągła wieczorna A (-4.5, -43.5), B (-1.5, -43.5), C (1.5, -43.5), D (4.5, -43.5); okrągła poranna A (30.5, -31), B (30.5, -28), C (30.5, -25), D (30.5, -22). Płytki okrągłe (R57, tylko do skanera) nie mają kieszeni magnesów — numer tylko w dołkach. 7 = rezerwa, 0 = brak płytki.

| n | Typ płytki | Magnesy w kieszeniach | Dołki kodu (bity) | Plik STL |
|---|---|---|---|---|
| 1 | wieczorna | A | A | `ramka_plytka_wieczorna_n1_v2.stl` |
| 2 | wieczorna | B | B | `ramka_plytka_wieczorna_n2_v2.stl` |
| 3 | wieczorna | A + B | A + B | `ramka_plytka_wieczorna_n3_v2.stl` |
| 4 | poranna | C | C | `ramka_plytka_poranna_n4_v2.stl` |
| 5 | poranna | A + C | A + C | `ramka_plytka_poranna_n5_v2.stl` |
| 6 | poranna | B + C | B + C | `ramka_plytka_poranna_n6_v2.stl` |
| 8 | okragla wieczorna | brak kieszeni (okrągła, R57) | D | `ramka_plytka_okragla_wieczorna_n8_v2.stl` |
| 9 | okragla poranna | brak kieszeni (okrągła, R57) | A + D | `ramka_plytka_okragla_poranna_n9_v2.stl` |

## Klejenie magnesów (ø5 × 2 N35)

1. Biegun: we wszystkich płytkach biegun **S** skierowany w dół (do czujnika Halla). Biegun musi być jednakowy we wszystkich płytkach.
2. Wzorzec: jeden magnes oznacz raz (biegun S flamastrem) według kompasu lub czujnika A3144 (reaguje tylko na biegun S). Każdy kolejny magnes przyłóż do wzorca: strona przyciągana przez oznaczoną stronę S wzorca to biegun N — tę stronę kieruj do góry (do dna kieszeni), a stronę S w dół.
3. Przed klejeniem sprawdź płytkę na wkładce ramki: odczyt numeru musi być równy n z tabeli; dopiero potem kropla kleju CA żelowego w kieszeń (od spodu płytki), magnes cofnięty 0,2 mm w kieszeni 2.2 mm.
4. Kontrola po klejeniu: płytka położona na wkładce daje n w < 100 ms; bez płytki 0.
