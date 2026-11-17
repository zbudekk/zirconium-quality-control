# R59 - nowy uklad gniazd plytek: jedna rynienka, wieksze gniazda (lista edycji w zrodle prawdy)

Data: 2026-11-14. Zlecenie wlasciciela 14.11.2026: plytka poranna - mniej malych gniazd, w ich miejsce wieksze (takze fi 15); plytka wieczorna - wiecej gniazd fi 15; obie plytki - jedna rynienka zamiast dwoch. Plan paczki: `plan_sesji_R59_uklad_gniazd_2026-11-14.md` (sekcja 7 = subsesja R59-A, wykonawca). Studium wariantow: `R59_propozycja_ukladu.md`.
Zakres edycji (R59-A): `parametry.json`, `ramka_generator.py`, `plan_ramki_v2.md`, `protokol_weryfikacji_v2.md`, `00_PRZEPLYW_I_BRAMKI.md` (jeden wiersz), `wyniki_v2/` (12 STL plytek, 4 JSON ukladu, arkusze, rendery, `.blend`, README, raporty), ten plik.
NIE dotknieto: `stanowisko/`, trzech dokumentow stanowiska i PDF, `Ramki_pakiet/`, `Ramki_do_wgrania/`, Dysku Google, modelu 3D i animacji, `narzedzia/`, `R59_szkice/`, `R59_propozycja_ukladu.md`, `00_NADZOR_STAN.md`. Kopie sprzed edycji: `archiwum/*_przed_R59_2026-11-14.*` (5 plikow), `archiwum/wyniki_v2_przed_R59_2026-11-14/` (caly `wyniki_v2` sprzed zmiany: 209 plikow + `sha256_stl_przed_R59.txt`).

## 0. Wynik

- `--etap ALL --iter 2 --raport R59` (z renderami): 58 ZAL, 5 N/D, 0 NIE (B 0 / P 0 / D 0); 2509 sond, 0 niezgodnych; czas 38 s.
- `--etap SPRAWDZ --iter 12`: 58 ZAL, 5 N/D, 0 NIE (B 0 / P 0 / D 0). Punkt odniesienia koordynatora na starym ukladzie: 58 ZAL, 5 N/D, 0 NIE.
- 5 x N/D jak przed R59: K-19, K-21, K-48, K-52 (uchylone w R50) i K-59 (powtarzalnosc - wykonuje recenzent).
- `node narzedzia\weryfikuj_uklad_R59.js parametry.json` (PC, bez przelacznikow, obie plytki): kod wyjscia 0, 103 linie OK, 0 bledow, 0 uwag.
- 9 plikow nieplytkowych (korpus W, korpus P, blat, wkladka, pokrywka, tulejka DC, 3 podkladki) bajtowo = `Ramki_pakiet/SHA256SUMS_2026-11-02_R57.txt`: 9 z 9.
- Lista `sockets` w JSON plytek okraglych = JSON kwadratu tego typu: 2 z 2 (K-05 h, porownanie pol).
- `arkusz_wymiarow.md`: 146 wierszy wymiarow i pasowan w tolerancji 0,05, 0 poza.
- Raport: `wyniki_v2/raport/raport_wykonawcy_R59_iter2.md` (sekcja 7 = uzupelnienie wykonawcy), `wyniki_v2/raport/raport_wykonawcy_SPRAWDZ_iter12.md`, lista `wyniki_v2/raport/sha256_stl_po_R59_iter2.txt`.

| Plik | SHA-256 | Objetosc [cm3] |
|---|---|---|
| `ramka_plytka_wieczorna_v2.stl` (bazowy) | 604ef8f2079184460c3e059edde4849e9feeefeab39a755c18d0079ea1e561a9 | 59,64 |
| `ramka_plytka_wieczorna_n1_v2.stl` | 3b0db5452a0cd9533464772c10b67c05fa7a006fcdb3d140a74af275e79946f7 | 59,66 |
| `ramka_plytka_wieczorna_n2_v2.stl` | b87026134b25cf32a84a231b73d5c4eb9fde4dfeb5b16b627cf09ccc3f29c999 | 59,66 |
| `ramka_plytka_wieczorna_n3_v2.stl` | 59e615d596771c6c0351284c710e94e406a965afef423ffeae5cd18ffa2c4dd3 | 59,66 |
| `ramka_plytka_poranna_v2.stl` (bazowy) | a306032651bbdb0c77693aa27f6314e8c5ede874d1e99b1fa73e158a1a83bc9f | 59,93 |
| `ramka_plytka_poranna_n4_v2.stl` | 20f15f2214f6c9a9baf2b4701e7f99bfbc5f739b6379398294e9f931b8763237 | 59,95 |
| `ramka_plytka_poranna_n5_v2.stl` | a275775b9c9b5ddd015b68659f213505bdd28b9476cad5e13405bef2df5b64d1 | 59,95 |
| `ramka_plytka_poranna_n6_v2.stl` | c44be370c8b9ad2b70f9e486c3f6f9d2b227b91f2a6544bfe14bf7e66bd65b21 | 59,94 |
| `ramka_plytka_okragla_wieczorna_v2.stl` (bazowy) | aad8033e6c1d1f34b43825861d18e82b45599a76ebb453c294400a7713ebbd83 | 49,34 |
| `ramka_plytka_okragla_wieczorna_n8_v2.stl` | d5591f652ea1b6b23825abb5ad05ac12b78d17f6abb52946bd1a010ef5e4ff54 | 49,36 |
| `ramka_plytka_okragla_poranna_v2.stl` (bazowy) | e35835d7618e6665fdda84cbe2d65a3c7b46d7f9cef1e99141b42af2eb9e22c7 | 49,63 |
| `ramka_plytka_okragla_poranna_n9_v2.stl` | f9444e6f14e37d9d0bcc8ae84cfec5249146bce20420c53a86a73965727fd4c4 | 49,64 |
| `uklad_gniazd_wieczorna.json` | 7ae07ba861950724cf68ce9de0b45f3a05436089df8f73b3b4fc07bf2cc05869 | - |
| `uklad_gniazd_poranna.json` | 46e474b759c4b78b7975fc8c5580c9916a4cc64c6a88cd4711b2207e3978b98b | - |
| `uklad_gniazd_okragla_wieczorna.json` | c07791f4bb976be2ad5eddaaeefe011b2384ea71e3fabd25cf55da690eb14a33 | - |
| `uklad_gniazd_okragla_poranna.json` | b943e6c5dd54a8b3b35974908a3910bd654062bb659284a649ee68679174268e | - |

Objetosci przed zmiana (R57, pliki bazowe): wieczorna 59,30, poranna 60,86, okragla wieczorna 48,99, okragla poranna 50,55. Suma arkusza zamowienia (10 pozycji drukarni x ilosci): 1009,77 -> 1008,05 cm3.

Liczby ukladu (z JSON i z siatek, K-05 / K-16 / K-61 / K-62 raportu `R59_iter2`; te same wartosci daje `weryfikuj_uklad_R59.js`):

| | wieczorna (W-b) | poranna (P-e) |
|---|---|---|
| gniazda | 18 (6 x fi 12, 12 x fi 15) + 1 rynienka 60 x 15 | 23 (20 x fi 12,5, 3 x fi 15) + 1 rynienka 50 x 13 |
| max promien obrysu (limit 47) | 45,927 (id 17) | 46,412 (id 22) |
| max abs(x) + r, abs(y) + r (limit 45) | 43,50 | 45,00 |
| min scianka miedzy obrysami (limit 3) | 3,000 (id 1 - 3) | 3,000 (id 1 - 3) |
| stozki: promien srodka A / B / C (limit 44,5) | 44,30 / 44,20 / 44,43 | 44,21 / 44,25 / 44,48 |
| stozek - gniazdo A / B / C (limit 3) | 3,52 / 3,23 / 3,19 | 3,45 / 3,02 / 3,48 |
| kwadrat: dolek - gniazdo (3) / dolek - stozek (1,5) | 8,27 / 6,01 | 8,61 / 11,03 |
| okragla: gniazdo - krawedz (1,5) / stozek - krawedz (1,5) | 4,07 / 3,07 | 3,59 / 3,02 |
| okragla: sciecie - obrysy (3), K-61 f | 4,59 | 4,81 |
| okragla: dolek - gniazdo (3) / dolek - stozek (1,5) / dolek - krawedz (1,5) | 4,80 / 31,86 / 5,27 | 3,55 / 2,09 / 5,07 |

## 1. Decyzje wlasciciela - bramka G0 (14.11.2026), doslownie i odczyt

- Odpowiedz 1: "w-b / p-b, ale zamiast jednego rzedu 10-tek, chce drugi rzad 12,5. zamast calego rzedu 7.5 chce rzad 10-tek / na poprzedniej plytce wieczorej beda skanowane zeby jak tylko przyjdzie skaner, nowe plytki zamawiamy w miedzyczasie, wiec program musi umiec pracowac na starych plytkach. / d6 - okragle raczej (jak zmienia sie liczba sdlotow w okraglych?) / d8 - b / reszta domyslnie". Potem wlasciciel przyslal wlasny szkic (prawie same fi 12,5 i trzy fi 15) i po obejrzeniu policzonych wariantow odpowiedzial: "chcwe p-e".
- D1 = W-b: plytka wieczorna 6 x fi 12 + 12 x fi 15 = 18 gniazd + 1 rynienka 60 x 15 (przednia, y -30,2).
- D2 = P-e: plytka poranna 20 x fi 12,5 + 3 x fi 15 = 23 gniazda + 1 rynienka 50 x 13 (przednia, y -35,3); ZERO fi 7,5 i fi 10. Uklad ma "rzedy mieszane": w `mo_rows` sa to osobne wpisy rzedu o roznym y (np. fi 12,5 x 4 w y 8 i fi 15 x 1 w y 8,75); numery id gniazd ida wtedy po y.
- D3 = a: jedna dluga rynienka na plytke, 4 otwory jak dzis (zadnych zmian liczby / rozstawu otworow).
- D4 = TAK: stare plytki fizyczne (uklad R54) beda jeszcze skanowane - dotyczy programu (R59-P), u wykonawcy tylko rzetelne archiwum starego ukladu (pkt 6).
- D5 = A: numery plytek bez zmian (n1-n3 wieczorna, n4-n6 poranna, n8 okragla wieczorna, n9 okragla poranna) - zadnych zmian numeracji w generatorze.
- D6: "okragle raczej" - `quantities` BEZ ZMIAN (decyzja o zamowieniu po odbiorze); ilosci nie zmieniono.
- D7 = a, D8 = b - nie dotycza tego etapu.

Zrodlo wartosci (jedyne; pozycje policzylo narzedzie `narzedzia/uklad_kolo_R59.js`, nic z reki): `R59_szkice/parametry_wariant_W-b.json` (klucze `ev_rows`, `ev_marker_pos`) i `R59_szkice/parametry_wariant_P-e.json` (klucze `mo_rows`, `mo_marker_pos`, `code_dimples_round.poranna`, `number_pos_round.poranna`). Klucz `_meta.r59_wariant` nie zostal przeniesiony. Zgodnosc wartosci w `parametry.json` z plikami wariantow sprawdzona porownaniem po wczytaniu JSON: 6 z 6 kluczy identycznych.

## 2. `parametry.json` - wartosci stare -> nowe

| Klucz | Bylo (R54 / R57) | Jest (R59) |
|---|---|---|
| `ev_rows` | 5 wpisow: rynienka 60 x 15 (y -31,5), fi 12 x 6 (y -15), fi 9 x 7 (y -1,5), fi 15 x 5 (y 13,5), rynienka 60 x 15 (y 31,5) = 18 + 2 | 5 wpisow: rynienka 60 x 15 (y -30,2; x 0), fi 12 x 6 (y -13,7; x +-7,5, +-22,5, +-37,5), fi 15 x 5 (y 2,75; x 0, +-18, +-36), fi 15 x 4 (y 18,35; x +-9, +-27), fi 15 x 3 (y 33,95; x 0, +-18) = 18 + 1 |
| `mo_rows` | 7 wpisow: fi 7,5 x 3 (y -41,25), rynienka 50 x 13 (y -28), fi 10 x 7 (y -13,5), fi 12,5 x 6 (y 0,75), fi 7,5 x 8 (y 13,6), fi 7,5 x 7 (y 22,7), rynienka 50 x 13 (y 35,95) = 31 + 2 | 8 wpisow: rynienka 50 x 13 (y -35,3; x 0), fi 12,5 x 5 (y -19,55; x 0, +-15,5, +-31), fi 12,5 x 6 (y -6,1; x +-7,75, +-23,25, +-38,75), fi 12,5 x 4 (y 8; x +-16,75, +-32,25), fi 15 x 1 (y 8,75; x 0), fi 15 x 2 (y 22,85; x +-24,5), fi 12,5 x 2 (y 23,6; x +-7,75), fi 12,5 x 3 (y 37,05; x 0, +-15,5) = 23 + 1 |
| `ev_marker_pos` | A (-35,5; -26,5), B (-35,5; 26,5), C (35,5; 26,5) | A (-35,5; -26,5) bez zmian, B (-31; 31,5), C (42; 14,5) |
| `mo_marker_pos` | A (-34,5; -28), B (-30; 32,5), C (30; 32,5) | A (-30,5; -32), B (-37,5; 23,5), C (41,5; 16) |
| `code_dimples_round.poranna` | A (30,5; -31), B (30,5; -28), C (30,5; -25), D (30,5; -22) | A (36,5; 18,5), B (36,5; 21,5), C (43; 6), D (43; 9) |
| `number_pos_round.poranna` | (36,5; -24,5) | (-44; 5,5) |

Rzedy mieszane porannej: wpisy 4 + 5 (fi 12,5 x 4 i fi 15 w srodku) oraz 6 + 7 (dwa fi 15 po bokach i fi 12,5 x 2 w srodku). Numery id ida po y wpisu: rynienka 1; fi 12,5: 2-6, 7-12, 13-16; fi 15: 17; fi 15: 18-19; fi 12,5: 20-21, 22-24. Wieczorna: rynienka 1; fi 12: 2-7; fi 15: 8-12, 13-16, 17-19. Numery id sa inne niz w ukladzie R54.

Bez zmian wartosci: `code_dimples_round.wieczorna`, `number_pos_round.wieczorna`, `quantities` (D6), `plate_numbers_ev/mo/round` (D5-A), wymiary rynienek 60 x 15 i 50 x 13, `trough_hole_count` 4 i rozstawy otworow 12 / 10 (D3-a), wszystkie pozostale klucze.

Opisy (`opis`) napisane na nowo z liczbami R59: 6 kluczy z tabeli (pole `zrodlo`: `D6/R59`, `R59/D6`, `R57/R59`); dopisane liczby po R59 w `trough_hole_count`, `plate_round_d`, `round_flat_w`; nowy `opis` w `ev_socket_d_s/m/l` i `mo_socket_d_s/m/l`.

Klucze `ev_socket_d_s/m/l`, `mo_socket_d_s/m/l` (i `ev_/mo_trough_l`, `ev_/mo_trough_w`): potwierdzone w kodzie generatora - wystepuja tylko na liscie `WYMAGANE_KLUCZE`, zadna funkcja ich nie czyta; srednica gniazda pochodzi z pola `d` wpisu rzedu, wymiary rynienki z pol `l`, `w`. Dlatego fi 15 w porannej nie wymaga nowego klucza. Wartosci zostaly (typoszereg ze specyfikacji 9 / 12 / 15 i 7,5 / 10 / 12,5); w opisach zapisano, ze od R59 fi 9, fi 7,5 i fi 10 nie wystepuja w ukladzie, a fi 15 porannej jest tylko w `mo_rows`. Kluczy nie usunieto (usuniecie wymagaloby zmiany walidatora R14 i tabeli 3.1 planu, bez potrzeby).

Liczba kluczy 287, bez zmian (plytka 61, pokrywka 16, panel_dyfuzor_pi 42, korpus 70, blat_rama_wkladka 62, male_czesci 11, sterowanie 25); statusy bez zmian (SPEC 53, ZALOZENIE 203, DO_ZMIERZENIA 21, LICZONE 10); `_meta` bez zmian; plik sie parsuje; wartosci LICZONE zgodne (max roznica 0,0000). SHA-256: b7b52942b71c... -> 8434aafe1584bdd5e8cb88776566e5c697fd48dac8bc02685b02b3d70d32f3b2. Diff: 29 linii dodanych, 28 usunietych.

## 3. `ramka_generator.py` - zmiany (kazda z powodem)

Uklad gniazd jest dana (`ev_rows` / `mo_rows` -> JSON -> bryly i sondy), wiec geometria i sprawdzenia nie wymagaly zmian kodu. Zmienione (diff 42 linie dodane, 18 usunietych; SHA-256 09268b1457f1... -> d3b56f63be525bf42372d71efc2fa661c3f7ad34346bd151b52eeb4d619fa7b1):

| # | Miejsce | Zmiana | Powod |
|---|---|---|---|
| 1 | `OBJ_ORIENT` | plytka wieczorna 62 -> 60, poranna 61 -> 60, okragla poranna 51 -> 50 (okragla wieczorna 49 bez zmian) | objetosci orientacyjne K-04b maja odpowiadac siatkom po zmianie ukladu (59,64 / 59,93 / 49,34 / 49,63) i tabeli 1 protokolu; wstawione po pierwszym przebiegu |
| 2 | `odstepstwa_informacyjne_R57` (rejestr odstepstw raportu, 7 wpisow) | liczby ukladu R54 oznaczone jako historyczne ("decyzja 2.11 na ukladzie R54"); pozycje dolkow i cyfry okraglych brane z `parametry.json` zamiast stalych w tekscie; odeslania do K-16 / K-61 / K-62 tego samego raportu; zapisy "SHA R56 bez zmian" uzupelnione o stan po R59 | po zmianie ukladu teksty podawaly nieprawdziwe liczby i pozycje (rynienka tylna porannej, dolki x 30,5, cyfra (36,5; -24,5), scianki 3,50 / 3,62, "n1-n6 bajtowo jak R56") |
| 3 | ten sam rejestr, wpis "K-08 na okraglych" | tresc powodu poprawiona: sonda na 45 st. powstala przy fi 96 / 98; przy fi 100 naroznik prostokata lezy w plytce; po R59 rynienka jest tylko z przodu (naroznik w promieniu 37,5 / 38,2) | stary tekst ("poza obrysem okraglym") byl nieaktualny od decyzji fi 100 (uwaga D1 recenzji R57-B, juz poprawiona w protokole); przy R59 zniknely rynienki tylne, o ktorych mowil |
| 4 | nowa `odstepstwa_informacyjne_R59` + wywolanie w `main()` | jeden wpis informacyjny rejestru: liczby gniazd policzone z `ev_rows` / `mo_rows` i regula numeracji id w rzedach mieszanych | raport ma mowic, jaki uklad zbudowano, i jawnie zapisac interpretacje R13 dla rzedu mieszanego (id po y wpisu) |
| 5 | `sprawdz_uklad_json` (K-05), tekst wyniku | "rzedow N" -> "wpisow rzedow (roznych y) N" | rzad mieszany P-e to dwa wpisy; liczba 8 nie jest liczba rzedow plytki porannej |
| 6 | komentarze | docstring `generuj_gniazda` (R59: id po y wpisu), komentarz przy sondzie K-08 plytek okraglych | opis zachowania przy rzedach mieszanych i po usunieciu rynienek tylnych; bez wplywu na dzialanie |

Sprawdzone i pozostawione BEZ ZMIAN:
- `generuj_gniazda`: sortuje wpisy po y, w wpisie po x malejaco - rzedy mieszane daja id po y bez zmiany kodu.
- K-05: (a) liczby oczekiwane z `ev_rows` / `mo_rows` (18/1 i 23/1), (b) symetria liczona w grupie o tym samym y (kazdy wpis rzedu mieszanego jest symetryczny), (g) kolejnosc id po y i x - bez zalozenia "jedna srednica w jednym y".
- K-06, K-07, K-08, K-09: sondy liczone z JSON; sondy sasiadow sprawdzone na nowym ukladzie (wszystkie zgodne). 4 otwory rynienki sa zaszyte w K-08 (k = -1,5 ... 1,5) - zostaje, bo D3-a nie zmienia liczby otworow.
- K-16, K-61 (f), K-62: petle po wszystkich gniazdach i rynienkach z JSON; nie zakladaja 2 rynienek ani rynienki tylnej.
- K-63: sondy od spodu na promieniu 45,5 - zaden otwor nowego ukladu nie lezy w poblizu (najdalszy srodek otworu: promien 40,2).
- `lista_wymiarow` i `lista_pasowan`: punkty pomiarowe (m.in. (0; -46,5), (-38; -38), pierwsze gniazdo okragle z JSON) nie trafiaja w nowe gniazda - 146 wierszy w tolerancji, 0 poza.
- Nazwy `plytka_wieczorna_n1`, `plytka_poranna_n4`, wyrazenie numeru jednocyfrowego: bez zmian (D5-A).
- Walidator kluczy R14: bez zmian (zadnych nowych ani usunietych kluczy).
- Sonda K-08 plytek okraglych: nadal tylko sonda na 45 st. (protokol wymienia tez sonde naroznika prostokata) - kod sprawdzen nie byl zmieniany; opisane w rejestrze raportu (#5).

## 4. `plan_ramki_v2.md` - edycje

| Miejsce | Zmiana |
|---|---|
| wstep | rejestr R1...R57 i R59 (R58 zarezerwowany) |
| 1. Zalozenia: Z20 | przepisane: jedna rynienka (przednia) na plytce, wieczorna 18 + 1 (6 x fi 12, 12 x fi 15), poranna 23 + 1 (20 x fi 12,5, 3 x fi 15), rzedy mieszane; stan R54 jako "dawniej"; uzasadnienie z proby 17 prac |
| Z30 | "ten sam uklad co kwadrat tego typu (od R59 W-b / P-e)" zamiast "co kwadrat R54" |
| D6 | przepisane: zasady (jedna rynienka jako pierwszy rzad, rzad mieszany = dwa wpisy, id po y), tabele wpisow obu plytek (y, zakres, zawartosc, id, skrajny promien), bloki y (79,15 i 85,1), scianki w rzedach i po przekatnej, znaczniki z promieniami, sciankami i bokami trojkata, wyniki `weryfikuj_uklad_R59.js`, warianty nie wybrane, odeslanie do archiwum ukladu R54 |
| D11 | scianki dolkow kwadratu do stozka A i gniazd po R59 (6,01 / 11,03 i 8,27 / 8,61); cyfra okraglej porannej (-44; 5,5) |
| 3.1 Tabela parametrow | opisy: `trough_hole_count`, `plate_round_d`, `code_dimples_round`, `number_pos_round`, `ev_socket_d_s/m/l`, `mo_socket_d_s/m/l` (wartosci liczbowe bez zmian - kontrola plan <-> JSON generatora: 251 wierszy, 0 roznic) |
| 4.1 p. 2 i 3 | jedna rynienka; pozycje stozkow obu typow (R54 jako "dawniej"), warunek bokow trojkata |
| 4.1 przyklad JSON | `markers` i `sockets` wg nowego ukladu; dopisek o id w rzedzie mieszanym |
| 4.1a | gabaryt (scianki do krawedzi po R59: 4,07 / 3,59; faza 3,57 / 3,09; stozki 3,07 / 3,02), sciecie (4,59 / 4,81), dolki kodu (poranna: dwie pary z prawej, liczby K-62), numer (poranna z lewej, odstepy obrysu cyfry), sprawdzenia (SHA po R59) |
| 4.11 | wiersze "Dolki kodu" (dopisek R59), "Kolo pola skanowania" i "Plytka okragla" (liczby R59, R54 jako "dawniej"), "Gniazda wieczornej" i "Gniazda porannej" (przepisane na uklad R59; dotad opisywaly uklad sprzed R54) |
| 12.1 | bez zmian - lista plikow sie nie zmienila |
| 13. Rejestr | naglowek R1...R57, R59; wiersz R59 po R57 (z uwaga, ze R58 jest zarezerwowany) |
| 14. Zmiany | punkt 28 |
| po recenzji R59-B iter 1, uwaga D3 | wiersz rejestru R59 (linia 890): odeslanie do `raport_wykonawcy_R59_iter2.md` zamiast `..._iter1.md` i dopisany werdykt recenzji (ZALICZONY, B 0 / P 0 / D 5); lista zmian protokolu w wierszu R59 i w sekcji 14 pkt 28 (linia 955) uzupelniona o K-11 i K-13 (wg diff protokolu: tabela 1, K-05, K-08, K-09, K-11, K-13, K-16, K-59, K-61, K-62) |
| po recenzji R59-B iter 1, uwaga D5 | 4.1 p. 5 (linia 463): 4 dolki kodu zamiast 3 - dopisany bit D (-45; -27) z `code_bit_d_pos`, plik bazowy = 4 dolki, n = A + 2B + 4C + 8D (na n1-n6 dolka D nie ma); przyklad JSON (linia 478): dopisany dolek D. Zgodne z `parametry.json` i z `uklad_gniazd_wieczorna.json` |

Sekcja 11 planu (wstepny koszt, objetosci "ok. 62 / 61") zostala bez zmian: to szacunek sprzed R54, obowiazuja wartosci z `arkusz_zamowienia`.
SHA-256: 8ce66391a01e... -> a9b0903f2e4da661e4b298b8ccc5f4c2904983c7961e6b0235ed523893c2cf97 (stan po poprawkach po recenzji; wersja oddana do recenzji R59-B iter 1 miala d49de129b04b...). Diff wzgledem stanu sprzed R59: 59 linii dodanych, 56 usunietych (poprawki po recenzji: 4 linie).

## 5. `protokol_weryfikacji_v2.md` i `00_PRZEPLYW_I_BRAMKI.md` - edycje

| Sprawdzenie | Zmiana |
|---|---|
| Tabela 1 | objetosci orientacyjne: wieczorna 60 [59,6 z siatki], poranna 60 [59,9], okragla wieczorna 49 [49,3], okragla poranna 50 [49,6]; wartosci R54 / R57 jako "dawniej" |
| K-05 | (a) 18/1 i 23/1 (R54: 18/2 i 31/2); (b) rzad mieszany = dwa wpisy, kazdy symetryczny; (c) max promien 45,93 / 46,41; (g) id w rzedzie mieszanym po y wpisu |
| K-08 | jedna rynienka (przednia) na plytce; naroznik prostokata w promieniu 37,5 / 38,2 (zapis o rynienkach tylnych jako historyczny) |
| K-09 | pozycje znacznikow R59 (R54 jako "dawniej") |
| K-11 | zapis "n1-n6 bajtowo bez zmian" ograniczony do R57; po R59 nowe SHA plytek |
| K-13 | cyfra okraglej porannej (-44; 5,5) |
| K-16 | wartosci oczekiwane po R59 (znacznik-gniazdo, dolek-gniazdo, dolek-znacznik, okragle: krawedz, stozek, dolek); wartosci R54 jako "dawniej" |
| K-61 | scianka sciecie-obrysy 4,59 / 4,81 (R54: 3,68 / 4,87) |
| K-62 | pozycje i liczby dolkow po R59 (poranna: dwie pary z prawej) |
| K-59 | 12 plikow plytek ma nowe SHA (lista w tym pliku); 9 plikow pozostalych czesci bajtowo = SHA256SUMS R57 |

Bez zmian: K-06, K-07 (sondy z JSON), K-10, K-12, K-14, K-15 (cechy kwadratu), K-17...K-57, K-58 (D5-A: numery bez zmian), K-60, K-63.
SHA-256 protokolu: e910edb2689e... -> da33c0b22dd78a4a7cc34f39e205c0f3e8362355d4ab207bc0d1a95fd5a23a5c. Diff: 13 linii zmienionych.
`00_PRZEPLYW_I_BRAMKI.md`, sekcja 3, wiersz Z20/D6: dopisek "[R59, 14.11.2026] zastapione: 18 + 1 wieczorna, 23 + 1 poranna, jedna rynienka" i status decyzji (1 linia; plik ma konce linii CRLF - zachowane). SHA-256: 527b71e2336e... -> eefb5e6d4ba52074dc0107157a477f216b1f84e5db19e0040d4ac7b4fa48e1bd.

## 6. Pliki wynikowe, przebiegi i archiwum

Przebiegi (PC, konto `<konto-PC>`, katalog `<PC-katalog>\r59\Ramki`, Blender 5.2.3 LTS; logi w `<PC-katalog>\r59\Ramki\_r59a\*.log`):

| # | Polecenie (po `--`) | Generator (SHA) | Wynik ZAL / N/D / NIE | Uwagi |
|---|---|---|---|---|
| 1 | `--etap ALL --iter 1 --raport R59proba --bez-renderow` | a11b02d8... | 57 / 5 / 1 | przebieg probny (objetosci do `OBJ_ORIENT`); jedyne NIE = K-60, bo rendery wylaczone przelacznikiem; 27 s |
| 2 | `--etap ALL --iter 1 --raport R59` | 978a29c2... | 58 / 5 / 0 | z renderami (Cycles dziala na koncie `<konto-PC>`); wkladka wyszla z innym znakiem zera normalnych (nizej); 38 s |
| 3 | `--etap SPRAWDZ --iter 10` | 978a29c2... | 58 / 5 / 0 | przed przywroceniem wkladki |
| 4 | `--etap SPRAWDZ --iter 11` | 978a29c2... | 58 / 5 / 0 | po przywroceniu wkladki f4196fbc |
| 5 | `--etap ALL --iter 2 --raport R59` | d3b56f63... | 58 / 5 / 0 | STAN KONCOWY; po poprawce tekstu rejestru (pkt 3 #3); JSON ukladu utworzone od nowa z rzedow; wkladka od razu f4196fbc; 38 s |
| 6 | `--etap SPRAWDZ --iter 12` | d3b56f63... | 58 / 5 / 0 | STAN KONCOWY |

SHA-256 12 STL plytek i 4 JSON ukladu sa identyczne w trzech przebiegach budujacych (1, 2, 5) - porownanie list. Przed przebiegiem 1 cztery stare `wyniki_v2/json/uklad_gniazd_*.json` przeniesiono do archiwum (inaczej generator zachowalby stara liste `sockets`).

Wkladka (znana pulapka): w przebiegu 2 `ramka_wkladka_v2.stl` mial SHA de0d26c5796a...; porownanie z plikiem f4196fbc6404... z archiwum: po 1806 trojkatow, 0 trojkatow z roznymi wierzcholkami, 4 normalne rozne bajtowo - we wszystkich 4 tylko znak zera (wartosci rowne). Plik f4196fbc przywrocony z `archiwum/wyniki_v2_przed_R59_2026-11-14/stl/`, wariant odlozony jako `archiwum/ramka_wkladka_v2_po_R59_iter1_znak_zera.stl`. W przebiegach 1 i 5 wkladka wyszla od razu z SHA f4196fbc (bez przywracania).

9 plikow nieplytkowych, stan koncowy = `Ramki_pakiet/SHA256SUMS_2026-11-02_R57.txt`: blat 8c48856e, korpus P aadb91c9, korpus W bd55871c, wkladka f4196fbc, pokrywka ad234444, tulejka DC b393256c, podkladki 4260d1f1 / e79a8051 / 9c47aea4.

Nowe lub zmienione w `wyniki_v2/`: `stl/` (21 plikow, w tym 12 nowych plytek; STL poza gitem), `json/uklad_gniazd_*.json` (4), `arkusze/` (`kody_plytek.md` - pozycje dolkow okraglej porannej; `arkusz_wymiarow.md`; `arkusz_zamowienia.*` - objetosci plytek), `render/` (3 PNG), `ramka_v2.blend`, `README.md`, `do_v3.md` (bez zmian tresci), `raport/raport_wykonawcy_R59_iter2.md`, `raport/raport_wykonawcy_SPRAWDZ_iter12.md`, `raport/sha256_stl_po_R59_iter2.txt`, 33 nowe rzuty kontrolne w `raport/rzuty/` (zaden istniejacy plik rzutu nie zmienil bajtow). Slad wczesniejszych przebiegow: `raport/raport_wykonawcy_R59proba_iter1.md`, `raport_wykonawcy_R59_iter1.md`, `raport_wykonawcy_SPRAWDZ_iter10.md`, `_iter11.md`, `sha256_stl_po_R59_iter1.txt`.

Archiwum (MSI: `Ramki/archiwum/`, PC: `<PC-katalog>\r59\Ramki\archiwum\`): `ramka_generator_przed_R59_2026-11-14.py`, `parametry_przed_R59_2026-11-14.json`, `plan_ramki_v2_przed_R59_2026-11-14.md`, `protokol_weryfikacji_v2_przed_R59_2026-11-14.md`, `00_PRZEPLYW_I_BRAMKI_przed_R59_2026-11-14.md`; `wyniki_v2_przed_R59_2026-11-14/` = caly `wyniki_v2` sprzed zmiany (209 plikow, lista SHA archiwum = lista SHA zrodla) + `sha256_stl_przed_R59.txt` (21 STL ukladu R54 / R57; na MSI STL leza w archiwum, ale nie sa sledzone przez git); `ramka_wkladka_v2_po_R59_iter1_znak_zera.stl`.

Gdzie leza pliki dla recenzenta: PC `<PC-katalog>\r59\Ramki\wyniki_v2\stl` (21 STL) i `...\wyniki_v2\json` (4 JSON); stary uklad do kontroli odwrotnej: `<PC-katalog>\r59\Ramki\archiwum\wyniki_v2_przed_R59_2026-11-14\json` i `...\stl`, `archiwum\parametry_przed_R59_2026-11-14.json`. MSI: `Ramki/wyniki_v2/stl/` (21 STL, SHA = lista PC, 21 z 21).

Odstepstwa i ograniczenia:
1. Byly dwa przebiegi `ALL` z etykieta R59 (iter 1 i iter 2); iter 2 powstal po poprawce jednego tekstu rejestru odstepstw w generatorze. Wyniki K-xx i SHA plytek sa w obu identyczne; obowiazuje iter 2.
2. Przebieg probny (1) ma K-60 = NIE - swiadomie uruchomiony z `--bez-renderow`; w przebiegach 2 i 5 K-60 = ZAL (3 PNG 1600 x 1200, podpisy 12 z 12).
3. Plik wariantu wkladki w `archiwum/` ma nazwe wg wzoru z R57 (nie `*_przed_R59_2026-11-14.*`); to STL, wiec nie trafia do gita.
4. Sekcja 1 raportu generatora podaje polecenie ze stala sciezka `cd <PC>\Desktop\Ramki` (tekst zaszyty w generatorze, nie zmieniany); faktyczny katalog przebiegu to `<PC-katalog>\r59\Ramki` - zapisane w sekcji 7 raportu.
5. `<PC>\Desktop\Ramki` (pulpit wlasciciela) nie zostal zmieniony - konto `<konto-PC>` ma tam tylko odczyt.

## 7. Co dalej (poza R59-A)

1. R59-B: recenzja z siatek (12 STL, 4 JSON, kontrola odwrotna starych pozycji, SHA, K-53) - swieza subsesja.
2. R59-P: program stanowiska - nowe modele plytek z `wyniki_v2/stl` i `wyniki_v2/json`; stary uklad jako `*_r54` z archiwum (D4); uwaga: numery id gniazd sa inne niz w R54.
3. R59-D / R59-M: dokumenty i model 3D (liczby 18 + 1 / 23 + 1; objetosci do zamowienia: n1-n3 59,66, n4 i n5 59,95, n6 59,94, n8 49,36, n9 49,64 cm3).
4. R59-K: pakiet i nowe SHA256SUMS (po G1).
5. Do rozwazenia (nie zrobione, poza zakresem "tylko konieczne zmiany"): sonda naroznika prostokata w K-08 takze na plytkach okraglych (protokol ja wymienia, generator wykonuje tylko sonde na 45 st.); odstep obrysu cyfry od gniazd sprawdza tylko `weryfikuj_uklad_R59.js`, nie generator; szacunkowe objetosci plytek w sekcji 11 planu (62 / 61) sa sprzed R54.
