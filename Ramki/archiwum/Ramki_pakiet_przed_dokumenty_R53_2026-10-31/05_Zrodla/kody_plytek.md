# Kody płytek (D11, R4)

Numer płytki n = A + 2·B + 4·C, gdzie bit = 1 oznacza magnes wklejony w kieszeni narożnika (A przód‑lewy, B tył‑lewy, C tył‑prawy; narożnik D z wycięciem bez kieszeni). Ten sam numer koduje dołki ø2 × 1 na wierzchu przy lewej krawędzi (x = -45): dołek bitu A y = -36, bitu B y = -33, bitu C y = -30 — dołek jest tylko dla bitu = 1. 7 = rezerwa, 0 = brak płytki.

| n | Typ płytki | Magnesy w kieszeniach | Dołki kodu (bity) | Plik STL |
|---|---|---|---|---|
| 1 | wieczorna | A | A | `ramka_plytka_wieczorna_n1_v2.stl` |
| 2 | wieczorna | B | B | `ramka_plytka_wieczorna_n2_v2.stl` |
| 3 | wieczorna | A + B | A + B | `ramka_plytka_wieczorna_n3_v2.stl` |
| 4 | poranna | C | C | `ramka_plytka_poranna_n4_v2.stl` |
| 5 | poranna | A + C | A + C | `ramka_plytka_poranna_n5_v2.stl` |
| 6 | poranna | B + C | B + C | `ramka_plytka_poranna_n6_v2.stl` |

## Klejenie magnesów (ø5 × 2 N35)

1. Biegun: we wszystkich płytkach biegun **S** skierowany w dół (do czujnika Halla). Biegun musi być jednakowy we wszystkich płytkach.
2. Wzorzec: jeden magnes oznacz raz (biegun S flamastrem) według kompasu lub czujnika A3144 (reaguje tylko na biegun S). Każdy kolejny magnes przyłóż do wzorca: strona przyciągana przez oznaczoną stronę S wzorca to biegun N — tę stronę kieruj do góry (do dna kieszeni), a stronę S w dół.
3. Przed klejeniem sprawdź płytkę na wkładce ramki: odczyt numeru musi być równy n z tabeli; dopiero potem kropla kleju CA żelowego w kieszeń (od spodu płytki), magnes cofnięty 0,2 mm w kieszeni 2.2 mm.
4. Kontrola po klejeniu: płytka położona na wkładce daje n w < 100 ms; bez płytki 0.
