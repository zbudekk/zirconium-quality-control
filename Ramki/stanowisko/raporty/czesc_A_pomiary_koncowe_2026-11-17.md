# Czesc A - pomiary koncowe na scalonym kodzie (krok 6 raportu `czesc_A_filtr_i_skala_2026-11-15.md`)

Data: 17.11.2026 (PC 14:50 - 19:15). Kod: galaz `przed-skanerem`, HEAD `fe66217` (PR #13 scalony: czesc A + czesc B
[usunieto w kopii: opis dostepu ssh]
Dane wylacznie syntetyczne (`<PC-katalog>\app\dane_ref`, pula 17 projektow z `Prace_test`) - to pomiar kodu, nie skanera.
Projekty tylko jako skroty. Repo nie zmieniane poza tym plikiem.

Punkty odniesienia (tylko odczyt, `<PC-katalog>\app\a\wyniki`): stary kod `8b83da7` = `baza\metryki_R59.json`,
`baza\metryki_r54.json`; kod `15820d5` = `v1\` (liczby raportu czesci A); kod `319f861` = `v2\program_R59_e0.json`
(przebieg z 16.11 01:12-01:27, ktory raport czesci A opisal jako "nieodczytany" - byl kompletny, odczytany teraz).
`stanowisko/match.py` i `narzedzia/metryki_skala.py` sa w `fe66217` bajt w bajt takie jak w `319f861`
(`git diff --stat 319f861 fe66217`), wiec `319f861` = "sama czesc A", a roznica `319f861` -> `fe66217` = czesc B
(`inspect.py`, pas brzegu `linia_i_plaszczyzna`), `plate.py` (rozpoznawanie ukladu), `porownaj.py`.
Pliki programu na PC = HEAD: 99 z 99 (SHA-256, `skrypty\lista_sha.py`). Lokalny `ustawienia.toml` = kopia
`ustawienia_wzor_pc.toml` BEZ dopisywania kluczy - 5 kluczy `[match]` czesci A i 3 klucze `[inspect]` czesci B weszly z
wartosci domyslnych w kodzie (sprawdzone: `skrypty\spr_ust.py`).

## Stan

| Nr | Co | Stan |
|---|---|---|
| 1 | R59 blad 0 na scalonym kodzie vs stary kod | zmierzone (pkt 2): 3 przebiegi, zgodne |
| 2 | r54 na nowym kodzie vs `metryki_r54.json` | zmierzone (pkt 3); rozdzielenie czesc A / czesc B na r54: zmierzone (pkt 3; kod `319f861` policzony na r54) |
| 3 | P1: filtr w 6 scenariuszach widocznosci + progi wysokosci, caly P2 (240 prac) | zmierzone (pkt 4.1) |
| 4 | P1: pelne dopasowanie stary / nowy filtr (top-1, status, czas) | zmierzone na calym P2: 24 skany, 240 prac, w dwoch partiach (pkt 4.2) |
| 5 | plytki poranne przy bledzie +-0,5 % (ostrzezenie) | zmierzone, 20 skanow (pkt 5.1) |
| 6 | plytki wieczorne przy bledzie +-0,1 ... +-1 % na scalonym kodzie | zmierzone z korekta, 8 bledow x 20 skanow (pkt 5.2); bez korekty: nie zmierzone (pkt 9.6) |
| 7 | strefa brzegu a estymata skali, caly P2 (217 prac "dobrze") | zmierzone (pkt 6) |
| 8 | skutek poprawki `319f861` na zestawach | zmierzone (pkt 7) |
| 9 | czas na plytke jednoprocesowo: stary kod / P1 / P1 + P3 | zmierzone, 2 rundy x 4 plytki, PC obciazony innymi sesjami (pkt 8) |

Przerwa i limity (szczegoly pkt 9): ok. 16:00 wlasciciel zatrzymal PC (0,4 GB wolnego RAM, CPU 88 C - liczyly trzy
sesje naraz, do 38 procesow python). Wszystkie moje przebiegi liczone 15:12-16:02 przepadly (bez plikow wynikowych) i
zostaly powtorzone. Od 16:15 limity koordynatora: 3 procesy / >= 8 GB wolnego RAM, od ok. 16:30: 2 procesy robocze,
2 watki na proces (`OMP_NUM_THREADS` itd. = 2), start partii tylko przy >= 10 GB wolnego RAM, jedno polecenie naraz.
Od ok. 18:10 (decyzja wlasciciela): 6 procesow, bez warunku RAM, bez limitu watkow. Ktory pomiar szedl w jakich
warunkach: tabela w pkt 9.5.

## 1. Co zmienia scalenie wzgledem liczb raportu czesci A (wprost)

1. **Rozpoznanie (top-1, top-2, statusy match) i estymata skali: bez zmian.** `fe66217` vs `319f861` na R59, praca po
   pracy (413 wierszy prac, korekta wlaczona): top-1 388 = 388, rozne 0; poprawka skali 397 par, |roznica| <= 0,01 w
   397, max 0,0075; korekta zastosowana 168 = 168; status match rozny w 1 pracy.
2. **Kolory gniazd i wykrycia: zmienione przez czesc B, nie przez czesc A.** R59: zielone 155 -> 116, zolte 164 -> 201,
   czerwone 65 -> 66. 39 gniazd zielone -> zolte, wszystkie w zestawie P3a, z tego 38 to status inspect `ok` ->
   `nie_sprawdzono` (prace lezace bokiem 18, czesciowo zasloniete 20; prace "dobrze" i z drgnieciem 0). Zestaw P2
   (prace dobrze polozone): zielone 95 = 95, `nie_sprawdzono` 0. Wykrycia ubytkow 222 -> 226 z 249, czerwone 79 -> 83
   (P2: 57 -> 63, P3a: 22 -> 20).
3. Liczb gniazd zielonych / zoltych z raportu czesci A (pkt 3.1 a, 3.2 c-e) nie nalezy wiec porownywac ze scalonym
   kodem wprost; liczby top-1, estymaty skali i filtra P1 - mozna.
4. **Czas inspect: +16 ... +29 s na plytke przy pierwszym uzyciu projektow** (wyznaczenie linii brzegu, czesc B) - pkt 8.
5. **`narzedzia/metryki_skala.py program` na scalonym kodzie konczy sie bledem** po przeliczeniu wszystkich skanow, przed
   zapisem wyniku: `podsumuj_program`, linia 300, `TypeError: unsupported operand type(s) for +: int and dict`.
   Przyczyna: `porownaj.metryki_inspekcji()["razem"]` ma od czesci B zagniezdzony slownik `klasy`, a sumowanie w
   narzedziu czesci A obsluguje tylko slowniki plaskie. Program (`porownaj`) dziala; nie dziala narzedzie pomiarowe w
   trybie `program` (tryby `p1` i `brzeg` dzialaja). Pliku nie zmienialem - pomiary poszly przez owijke
   `k2a\skrypty\ms.py` (podsumowanie bez zagniezdzonych slownikow; w JSON rekordy pelne). **Do naprawy w repo.**

## 2. R59, blad wspolczynnika 0 (40 skanow, 397 prac)

| Miara | stary kod `8b83da7` | `319f861` P1 (korekta wyl.) | `319f861` P1 + P3 | **`fe66217` P1 (korekta wyl.)** | **`fe66217` P1 + P3 (domyslne)** |
|---|---|---|---|---|---|
| top-1 razem | 382 / 397 | 388 / 397 | 388 / 397 | 389 / 397 | **388 / 397** |
| top-2 razem | 384 / 397 | 390 / 397 | 390 / 397 | 390 / 397 | 390 / 397 |
| top-1 zestaw P2 | 240 / 240 | 240 / 240 | 240 / 240 | 240 / 240 | 240 / 240 |
| top-1 dobrze / bokiem / czesciowo / drgniecie | 276/276, 32/59, 35/37, 39/41 | 276/276, 38/59, 35/37, 39/41 | 276/276, 38/59, 35/37, 39/41 | 276/276, 39/59, 35/37, 39/41 | 276/276, 38/59, 35/37, 39/41 |
| statusy match zielony / zolty / szary | 339 / 42 / 32 | 344 / 43 / 26 | 344 / 44 / 25 | 344 / 43 / 26 | 344 / 43 / 26 |
| gniazda zielone / czerwone / zolte / szare / pomaranczowe | 150 / 65 / 162 / 32 / 4 | 155 / 65 / 163 / 26 / 4 | 155 / 65 / 164 / 25 / 4 | 116 / 66 / 201 / 26 / 4 | 116 / 66 / 201 / 26 / 4 |
| ubytki wykryte dowolna / A / B / A+B / czerwone | 221 / 184 / 107 / 69 / 79 z 248 | 222 / 185 / 107 / 69 / 79 z 249 | 222 / 185 / 107 / 69 / 79 z 249 | 226 / 189 / 110 / 72 / 83 z 249 | 226 / 189 / 110 / 72 / 83 z 249 |
| prace cale z alarmem / z czerwonym | 0 / 0 z 127 | 0 / 0 z 127 | 0 / 0 z 127 | 0 / 0 z 127 | 0 / 0 z 127 |
| prace cale "nie sprawdzono" (zolte) / wszystkie prace "nie sprawdzono" | - | - | - | 9 z 127 / 38 | 9 z 127 / 38 |
| falszywe ubytki (czerwone) | 7 (2) | 7 (2) | 7 (2) | 7 (2) | 7 (2) |
| drgniecie wykryte / falszywe "skan ponownie" | 35 z 39 / 2 | 35 z 39 / 2 | 36 z 39 / 2 | 35 z 39 / 2 | 36 z 39 / 2 |

- Kolumny `fe66217` = przebieg 3 (po przerwie, 2 procesy, 2 watki; `wyniki\zl_R59_e0.json` = `program_R59_P2_e0.json` +
  `program_R59_P3a_e0.json`). Przebieg 1 (14:57-15:09, 8 procesow, bez limitu watkow; sumy z logu, bo narzedzie padlo
  przy podsumowaniu - pkt 1.5) i przebieg 2 (15:12-16:00, przerwany; z logu komplet 40 skanow z korekta i 24 skany P2
  bez korekty) daly te same sumy: top-1 388 / 397 (P2 240 / 240), wykrycia 226 / 249, prace cale z alarmem / z czerwonym
  0 / 0 z 127, gniazda 116 / 66 / 201 / 26 / 4. Jedyna roznica miedzy przebiegami: top-1 bez korekty 388 (przebieg 1) /
  389 (przebieg 3) - ta sama jedna praca co w pkt 7.
- Kryterium "top-1 / top-2 nie gorsze niz stary kod": spelnione (388-389 >= 382, 390 >= 384, P2 240 / 240).
- **Pogorszenie wzgledem punktu odniesienia:** gniazda zielone 150 -> 116 (skutek statusu "nie sprawdzono" czesci B:
  38 prac, w tym 9 prac calych; pkt 1.2). Zadne inne liczniki nie sa gorsze niz na starym kodzie. Wzgledem `319f861`:
  wykrycia czerwone w P3a 22 -> 20 (3 gniazda czerwone -> zolte "sprawdz", 1 odwrotnie), razem czerwone 79 -> 83.
- Zmiany statusu inspect `319f861` -> `fe66217` (korekta wl., 413 wierszy): `ok` -> `nie_sprawdzono` 38, `sprawdz` ->
  `ubytek` 4, `ubytek` -> `sprawdz` 3, `ok` -> `sprawdz` 1, `sprawdz_ulozenie` -> `sprawdz` 1, `skan_ponownie` -> brak 1.
  Prace bez ubytkow zielone: "dobrze" 109 -> 109 (ze 111), bokiem 10 -> 5 (z 20), czesciowo 4 -> 0 (z 8).

Wg pory plytki, `fe66217`, korekta wlaczona (P2 + P3a; w nawiasie `319f861`, gdy inne):

| Pora | skanow / prac | top-1 | gniazda ziel / czerw / zolte / szare / pom | ubytki dowolna / czerwone | prace cale alarm / czerw. | korekta zastosowana | ostrzezen | estymata prac "dobrze" w 0,05 (max) | estymaty wiarygodne w 0,05 (max) | niepewne w 0,05 (max) |
|---|---|---|---|---|---|---|---|---|---|---|
| wieczorne | 20 / 174 | 170 (170) | 49 / 26 / 91 / 11 / 4 (63 / 25 / 78 / 11 / 4) | 103 / 31 z 113 (100 / 28) | 0 / 0 z 55 | 168 (168) | 0 | 123 / 123 (0,029) | 151 / 153 (0,170) | 3 / 15 (0,349) |
| poranne | 20 / 223 | 218 (218) | 67 / 40 / 110 / 15 / 0 (92 / 40 / 86 / 14 / 0) | 123 / 52 z 136 (122 / 51) | 0 / 0 z 72 | 0 (0) | 0 | 153 / 153 (0,046) | 189 / 191 (0,221) | 4 / 27 (2,346) |

Estymata skali przy bledzie 0 jest identyczna z `319f861` (te same liczniki i maksima).

## 3. r54, blad wspolczynnika 0 (40 skanow, 384 prace, `--sufiks-ukladu _r54`)

| Miara | stary kod `8b83da7` | **`fe66217` P1 (korekta wyl.)** | **`fe66217` P1 + P3 (domyslne)** |
|---|---|---|---|
| top-1 razem | 375 / 384 | 376 / 384 | **376 / 384** |
| top-2 razem | 376 / 384 | 377 / 384 | 376 / 384 |
| top-1 / top-2 zestaw P2 | 235 / 235, 235 | 235 / 235, 235 | 235 / 235, 235 |
| top-1 dobrze / bokiem / czesciowo / drgniecie | 261/261, 49/76, 28/36, 37/40 | 261/261, 48/76, 31/36, 36/40 | 261/261, 48/76, 31/36, 36/40 |
| statusy match zielony / zolty / szary | 333 / 38 / 42 | 335 / 37 / 41 | 335 / 38 / 40 |
| gniazda zielone / czerwone / zolte / szare / pomaranczowe | 159 / 70 / 135 / 42 / 7 | 114 / 67 / 183 / 41 / 8 | 114 / 67 / 184 / 40 / 8 |
| ubytki wykryte dowolna / A / B / A+B / czerwone | 215 / 184 / 109 / 78 / 88 z 231 | 213 / 187 / 103 / 77 / 87 z 231 | 213 / 187 / 103 / 77 / 87 z 231 |
| prace cale z alarmem / z czerwonym | 1 / 0 z 136 | 0 / 0 z 136 | 0 / 0 z 136 |
| prace cale "nie sprawdzono" / wszystkie prace "nie sprawdzono" | - | 19 z 136 / 47 | 19 z 136 / 47 |
| falszywe ubytki (czerwone) | 3 (0) | 0 (0) | 0 (0) |
| drgniecie wykryte / falszywe | 34 z 37 / 0 | 33 z 36 / 0 | 33 z 36 / 1 |
| poprawki reczne wykryte | 12 z 20 | 12 z 21 | 12 z 21 |

- Kryterium top-1 / top-2: spelnione (376 >= 375, 376 >= 376, P2 235 / 235).
- **Pogorszenia wzgledem starego kodu na r54:** top-1 prac lezacych bokiem 49 -> 48 z 76 i z drgnieciem 37 -> 36 z 40
  (czesciowo zasloniete 28 -> 31, razem +1); ubytki wykryte dowolna metoda 215 -> 213, metoda B 109 -> 103, A+B 78 -> 77,
  czerwone 88 -> 87 z 231; drgniecie wykryte 34 z 37 -> 33 z 36, falszywe "skan ponownie" 0 -> 1 (z korekta); gniazda
  zielone 159 -> 114 (47 prac "nie sprawdzono", w tym 19 prac calych - wszystkie w zestawie P3a; P2: 0).
  Te same liczby z korekta i bez korekty, wiec to nie skutek P3. Rozdzielenie (`wyniki\a319_program_r54_e0_tak.json` =
  kod `319f861`, sama czesc A, z korekta, policzony 17.11 18:21): top-1 377 / 384, top-2 377, P2 235 / 235, scenariusze
  261/261, 48/76, 31/36, 37/40; ubytki 215 / 184 / 109 / 78 / 88 z 231 (= stary kod co do sztuki); gniazda 161 / 70 / 134 /
  41 / 7; prace cale z alarmem 1; falszywe 3 (0); drgniecie 33 z 36 / 0. **Spadek wykryc na r54 (dowolna -2, B -6, czerwone
  -1) i spadek zielonych wchodza w calosci miedzy `319f861` a `fe66217`, czyli z czescia B** (praca po pracy: `ubytek` ->
  `sprawdz` 5, `sprawdz` -> `ubytek` 2, `ok` -> `nie_sprawdzono` 47: bokiem 25, czesciowo 22, "dobrze" 0). Top-1 bokiem
  48 / 76 jest juz na `319f861` (stary kod 49: 1 praca, czesc A albo rozrzut RANSAC - nierozstrzygniete); top-1 razem
  377 (`319f861`) vs 376 (`fe66217`): 1 praca szara / zolta.
- Korekta skali na r54 przy bledzie 0: zastosowana 180 razy (plytki wieczorne), w tym przy pokryciu po korekcie < 0,6:
  0; powod "praca nierozpoznana" 1 (bokiem); top-1 rozne z korekta / bez: 0 z 413 par. Estymata prac "dobrze": wieczorne
  132 / 132 w granicy 0,05 (max 0,031), poranne 129 / 129 (max 0,048); estymaty wiarygodne wieczorne 161 / 164, poranne
  167 / 170 (max 0,267).
- **1 falszywe ostrzezenie skali przy bledzie 0** (r54 P3a, plytka okragla wieczorna, praca lezaca bokiem, drugi
  fragment w tym samym gniezdzie; estymata +1,52 %, "wiarygodna" przy pokryciu 0,93, poza oknem - korekty nie
  zastosowano, gniazdo zolte "nie sprawdzono"). Na R59 przy bledzie 0: 0 ostrzezen.
- Zestaw P2 r54 policzony dwa razy (przypadkiem, pkt 9.4): oba przebiegi daly identyczne liczniki.

## 4. P1 - filtr wymiarow

### 4.1 Sam filtr w scenariuszach widocznosci, caly `syntetyczne_R59_P2` (24 skany, 240 prac: 217 "dobrze" + 23 z drgnieciem)

`metryki_skala.py p1` bez `--dopasuj` (`wyniki\p1_R59_P2_filtr.json`). Raport czesci A mial tu 1 skan (12 prac).

| scenariusz (prace "dobrze", 217) | wysokosc fragmentu / projektu (min-mediana) | wlasciwy projekt odrzucony: stary / nowy filtr | przechodzi filtr srednio (z 17): stary / nowy |
|---|---|---|---|
| pelny (jak dane syntetyczne) | 0,95-1,01 | 0 / 217 -> 0 / 217 | 1,65 / 2,24 |
| z gory (stozek 30 st.) | 0,79-0,92 | 3 / 217 -> 0 / 217 | 1,64 / 2,50 |
| z gory + zaslania plytka | 0,79-0,92 | 4 / 217 -> 0 / 217 | 1,63 / 2,49 |
| bez dolnych 1,5 mm | 0,72-0,87 | 19 / 217 -> 0 / 217 | 1,59 / 2,48 |
| bez dolnych 3,0 mm | 0,48-0,72 | **216 / 217 -> 1 / 217** | 0,74 / 2,45 |
| tylko nad plytka | 0,36-0,64 | **217 / 217 -> 17 / 217** | 0,48 / 2,21 |

Prace z drgnieciem (23): pelny, z gory, z gory + plytka, bez 1,5 mm: 0 / 23 -> 0 / 23; bez 3,0 mm 23 / 23 -> 0 / 23; tylko
nad plytka 23 / 23 -> 2 / 23. Nowy filtr nie odrzuca wlasciwego projektu w zadnym scenariuszu, w ktorym stary go
przepuszczal (brak pogorszen). Zostaje 1 / 217 (bez 3,0 mm) i 17 / 217 (tylko nad plytka): fragment ponizej 50 %
wysokosci projektu - zgodnie z opisem granicy w raporcie czesci A pkt 5.

Progi `[match] filtr_wysokosc_min_udzial` (nowy filtr; prace "dobrze": wlasciwy odrzucony z 217 / przechodzi srednio):

| scenariusz | 0 | **0,5 (domyslny)** | 0,6 | 0,7 | 0,8 | 1,0 (= regula sprzed zmiany) |
|---|---|---|---|---|---|---|
| pelny | 0 / 2,24 | 0 / 2,24 | 0 / 2,24 | 0 / 2,16 | 0 / 1,81 | 0 / 1,59 |
| z gory | 0 / 2,50 | 0 / 2,50 | 0 / 2,42 | 0 / 2,13 | 1 / 1,69 | 3 / 1,64 |
| z gory + plytka | 0 / 2,49 | 0 / 2,49 | 0 / 2,41 | 0 / 2,12 | 1 / 1,68 | 4 / 1,63 |
| bez dolnych 1,5 mm | 0 / 2,52 | 0 / 2,48 | 0 / 2,35 | 0 / 1,99 | 10 / 1,74 | 19 / 1,59 |
| bez dolnych 3,0 mm | 0 / 2,76 | 1 / 2,45 | 22 / 2,06 | 92 / 1,55 | 193 / 0,90 | 216 / 0,74 |
| tylko nad plytka | 1 / 2,80 | 17 / 2,21 | 74 / 1,71 | 160 / 1,10 | 211 / 0,62 | 217 / 0,48 |

Prog 0,5 kosztuje srednio +0,6 ... +0,9 projektu w puli po filtrze (2,2-2,5 zamiast 1,6); prog 0 daje jeszcze 16 prac
"tylko nad plytka" przy +0,6 projektu. Prog 0,7 zostawia wszystkie prace w scenariuszach do "bez 1,5 mm", ale gubi 92 / 217
przy schowanych 3,0 mm.

Zestaw `syntetyczne_R59_P3a` (16 skanow, scenariusz widocznosci "pelny", `wyniki\p1_R59_P3a.json`), wlasciwy projekt
odrzucony stary -> nowy filtr: prace "dobrze" 0 / 59 -> 0 / 59, lezace bokiem 21 / 31 -> 17 / 31, czesciowo zasloniete
6 / 37 -> 3 / 37, z drgnieciem 4 / 16 -> 4 / 16 (przechodzi srednio 1,4-1,6 -> 1,9-2,2). Progi dla prac "dobrze" P3a: 0 / 59
odrzuconych przy kazdym progu 0 ... 1,0.

### 4.2 Pelne dopasowanie starym i nowym filtrem (top-1, status, czas match)

`metryki_skala.py p1 --dopasuj`, caly `syntetyczne_R59_P2` w dwoch partiach: 8 skanow `skan_*0[0-1].stl`
(`wyniki\p1_R59_P2_dopasuj_8.json`; 2 procesy, 2 watki) + 16 skanow `skan_*0[2-5].stl` (`p1_R59_P2_dopasuj_16.json`;
6 procesow, bez limitu watkow); zlaczone `p1_R59_P2_dopasuj.json` (`skrypty\p1scal.py`). Pelne `match.dopasuj` z korekta
wylaczona, raz ze starym filtrem, raz z nowym. Raport czesci A mial tu 1 skan (10 prac "dobrze").

| scenariusz (prace "dobrze", 217) | wlasciwy odrzucony: stary / nowy | top-1: stary -> nowy | top-1 zielony: stary -> nowy | czas match na prace [s], stary -> nowy: 8 skanow (2 procesy, 2 watki) | to samo: 16 skanow (6 procesow, bez limitu) |
|---|---|---|---|---|---|
| pelny | 0 / 0 | 217 / 217 -> 217 / 217 | 217 -> 217 | 0,83 -> 1,34 | 1,46 -> 2,58 |
| z gory | 3 / 0 | 214 / 217 -> 217 / 217 | 214 -> 217 | 0,65 -> 1,25 | 1,36 -> 2,77 |
| z gory + zaslania plytka | 4 / 0 | 213 / 217 -> 217 / 217 | 213 -> 217 | 0,62 -> 1,24 | 1,33 -> 2,78 |
| bez dolnych 1,5 mm | 19 / 0 | 212 / 217 -> 217 / 217 | 212 -> 217 | 1,12 -> 1,39 | 3,92 -> 3,12 |
| bez dolnych 3,0 mm | 216 / 1 | **116 / 217 -> 217 / 217** | 116 -> 217 | 7,61 -> 1,33 | 16,82 -> 2,98 |
| tylko nad plytka | 217 / 17 | **137 / 217 -> 217 / 217** | 137 -> 217 | 9,36 -> 1,72 | 18,85 -> 3,92 |

- **Nowy filtr: top-1 217 / 217 w kazdym z 6 scenariuszy** (stary: 217, 214, 213, 212, 116, 137); kazda z tych prac jest
  zielona. Prac, ktore stary filtr rozpoznawal, a nowy nie: 0.
- Prace z drgnieciem (23): top-1 stary -> nowy: pelny, z gory, z gory + plytka, bez 1,5 mm 23 / 23 -> 23 / 23; bez 3,0 mm
  8 / 23 -> 23 / 23; tylko nad plytka 11 / 23 -> 23 / 23. Zielona jest 1 z 23 (z definicji drgniecie nie daje zieleni).
- 1 praca (bez 3,0 mm) i 17 prac (tylko nad plytka), ktorym nowy filtr odrzuca wlasciwy projekt (pkt 4.1), i tak dostaje
  wlasciwy projekt z ratunku "dopasuj wszystkie" - stad 217 / 217.
- **Koszt czasu:** praca w pelni widoczna +0,5 s match na prace przy 2 procesach z limitem watkow (0,83 -> 1,34 s) i
  +1,1 s przy 6 procesach bez limitu (1,46 -> 2,58 s; czasy zawyzone rownoleglym liczeniem) - w obu partiach x 1,6-1,8,
  bo wiecej projektow przechodzi filtr (1,65 -> 2,24). Praca niska (bez 3,0 mm, tylko nad plytka): 5-6 razy szybciej
  (7,6-9,4 -> 1,3-1,7 s i 16,8-18,9 -> 3,0-3,9 s), bo stary filtr wpada w "dopasuj wszystkie". Raport czesci A podawal
  +0,16 s na prace z 1 skanu - na calym zestawie koszt jest wiekszy (+0,5 s).

## 5. P3 - blad wspolczynnika

### 5.1 Plytki poranne R59 przy bledzie +-0,5 % (20 skanow, 223 prace; korekta wlaczona = rano tylko mierzona)

`wyniki\program_R59_P2_rano_bledy.json` (12 skanow) + `program_R59_P3a_rano_bledy.json` (8 skanow); blad 0 z pkt 2.

| Miara | blad 0 | blad +0,5 % | blad -0,5 % |
|---|---|---|---|
| **ostrzezenie skali: prace z ostrzezeniem / estymaty wiarygodne** | 0 / 191 | **190 / 191** | **189 / 189** |
| ostrzezenie wsrod prac "dobrze" | 0 / 153 | 152 / 153 | 152 / 153 |
| ostrzezenie wsrod estymat "niepewnych" (z definicji brak) | 0 / 27 | 0 / 27 | 0 / 27 |
| estymata prac "dobrze" w granicy 0,05 (max) | 153 / 153 (0,046) | 153 / 153 (0,048) | 153 / 153 (0,046) |
| korekta zastosowana | 0 | 0 | 0 |
| top-1 (P2 + P3a) | 136 + 82 = 218 / 223 | 136 + 83 = 219 / 223 | 136 + 81 = 217 / 223 |
| statusy match zielony / zolty / szary | 191 / 26 / 15 | 111 / 106 / 15 | 119 / 96 / 17 |
| gniazda zielone / czerwone / zolte / szare | 67 / 40 / 110 / 15 | 41 / 17 / 159 / 15 | 34 / 9 / 172 / 17 |
| ubytki wykryte dowolna / czerwone | 123 / 52 z 136 | 51 / 19 z 136 | 59 / 12 z 136 |
| prace cale z alarmem / z czerwonym | 0 / 0 z 72 | 0 / 0 z 72 | 8 / 0 z 71 |
| falszywe ubytki (czerwone) | 5 (2) | 5 (1) | 24 (0) |
| "popraw ulozenie" / "skan ponownie" | 4 / 22 | 16 / 99 | 18 / 80 |

- **Ostrzezenie przy +-0,5 % pojawia sie na plytkach porannych**: dla wszystkich estymat wiarygodnych poza jedna
  (190 / 191 i 189 / 189). Jedyna praca "dobrze" bez ostrzezenia (ta sama przy +0,5 i -0,5; estymata +0,506 / -0,494,
  czyli trafna) ma pokrycie po korekcie 0,83 < 0,85, wiec estymata jest oznaczona jako "niepewna" i ostrzezenia nie daje.
- **Rano blad wspolczynnika psuje wynik programu tak jak wieczorem bez korekty** (z zalozenia: rano korekta nie jest
  stosowana): zielonych gniazd 67 -> 41 / 34, wykrycia 123 -> 51 / 59 ze 136, "skan ponownie" 22 -> 99 / 80, a przy -0,5 %
  8 prac calych z alarmem (zolte "sprawdz", 0 czerwonych) i 24 falszywe ubytki (0 czerwonych). Operator dostaje wtedy
  ostrzezenie skali na prawie kazdej pracy - to jedyny sygnal, ze przyczyna jest skala, nie ulozenie.

### 5.2 Plytki wieczorne R59 przy bledzie +-0,1 ... +-1 % na scalonym kodzie

`wyniki\program_R59_wiecz_blad_05.json`, `..._03.json`, `..._10.json`, `..._01.json` (zlaczone: `zl_R59_wiecz_bledy.json`);
20 skanow wieczornych, 174 prace, 113 ubytkow wykrywalnych, 55 prac calych; **tylko z korekta** (wariant bez korekty na
scalonym kodzie nie liczony - pkt 9.6; liczby bez korekty: raport czesci A pkt 3.2 d, kod `15820d5`). Blad 0 z pkt 2.

| e % | top-1 | match ziel / zolty / szary | gniazda ziel / czerw / zolte / szare / pom | ubytki dowolna / czerwone z 113 | prace cale alarm / czerw. z 55 | falszywe (czerw.) | "popraw ulozenie" / "skan ponownie" | korekta zastosowana | w tym przy pokryciu < 0,6 | ostrzezen / estymaty wiarygodne | ostrzezenie wsrod prac "dobrze" | estymata "dobrze" w 0,05 (max) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 170 | 153 / 17 / 11 | 49 / 26 / 91 / 11 / 4 | 103 / 31 | 0 / 0 | 2 (0) | 1 / 16 | 168 | 0 | 0 / 153 | 0 / 123 | 123 / 123 (0,029) |
| +0,1 | 170 | 154 / 16 / 11 | 48 / 26 / 92 / 11 / 4 | 102 / 31 | 0 / 0 | 2 (0) | 1 / 15 | 168 | 0 | 0 / 154 | 0 / 123 | 123 / 123 (0,029) |
| -0,1 | 170 | 153 / 17 / 11 | 49 / 27 / 90 / 11 / 4 | 103 / 33 | 0 / 0 | 2 (0) | 1 / 16 | 168 | 0 | 0 / 153 | 0 / 123 | 123 / 123 (0,031) |
| +0,3 | 171 | 155 / 17 / 9 | 49 / 24 / 95 / 9 / 4 | 103 / 29 | 0 / 0 | 1 (0) | 1 / 16 | 168 | 0 | 100 / 154 | 81 / 123 | 123 / 123 (0,029) |
| -0,3 | 169 | 153 / 17 / 11 | 49 / 25 / 92 / 11 / 4 | 102 / 31 | 0 / 0 | 2 (0) | 1 / 16 | 168 | 0 | 51 / 153 | 40 / 123 | 123 / 123 (0,031) |
| +0,5 | 171 | 154 / 15 / 12 | 48 / 25 / 92 / 12 / 4 | 105 / 31 | 0 / 0 | 2 (0) | 1 / 13 | 168 | 0 | **154 / 154** | 123 / 123 | 123 / 123 (0,030) |
| -0,5 | 169 | 153 / 16 / 12 | 49 / 25 / 91 / 12 / 4 | 103 / 31 | 0 / 0 | 2 (0) | 1 / 15 | 167 | 0 | **153 / 153** | 123 / 123 | 123 / 123 (0,030) |
| +1,0 | 172 | 154 / 15 / 12 | 49 / 24 / 92 / 12 / 4 | 104 / 29 | 0 / 0 z 56 | 2 (0) | 0 / 15 | 164 | 0 | 154 / 154 | 123 / 123 | 123 / 123 (0,029) |
| -1,0 | 171 | 154 / 10 / 17 | 49 / 27 / 84 / 17 / 4 | 100 / 33 | 0 / 0 | 2 (0) | 1 / 9 | 159 | 0 | 155 / 155 | 123 / 123 | 123 / 123 (0,031) |

- Z korekta program przy kazdym bledzie -1 ... +1 % daje to samo co bez bledu: zielonych gniazd 48-49 (bez bledu 49),
  zielonych match 153-155 (153), wykrycia 100-105 / 113 (103), czerwone 29-33 (31), prace cale z alarmem i z czerwonym
  0 / 55 wszedzie, falszywe ubytki 1-2, zadnego czerwonego. Top-1 169-172 (170).
- Ostrzezenie (> 0,3 %): przy +-0,5 i +-1 % dla wszystkich estymat wiarygodnych (153-155) i wszystkich 123 prac "dobrze";
  przy +0,3 % 100 / 154, przy -0,3 % 51 / 153 (blad na progu - jak w raporcie czesci A: 100 i 51); przy +-0,1 i 0: zadne.
- Estymaty wiarygodne w granicy 0,05: 151-152 z 153-155 przy kazdym bledzie (p95 <= 0,031, max 0,174); "niepewne" (14-15
  prac, drgniecie): 2-3 w granicy, max 0,35 - bez zmian wzgledem raportu czesci A.
- Granica okna: przy -1 % korekta zastosowana 159 razy, przy +1 % 164 (168 bez bledu) - poprawka poza oknem 14 i 11
  razy; "skan ponownie" 9 zamiast 16 przy -1 % (prace z drgnieciem staja sie szare: szarych 17 zamiast 11). To samo
  zjawisko co w raporcie czesci A pkt 3.2 d4 (tam 9 zamiast 15).
- **Skutek poprawki `319f861` przy bledzie:** korekt zastosowanych przy pokryciu po korekcie < 0,6: 0 w kazdej z 8 grup
  (na `15820d5`: 3, 2, 1, 1, 0, 3, 0, 1 = 11); powod "praca nierozpoznana" 0-3 na grupe (razem 11, wszystkie bokiem).
  Top-1 z korekta na `fe66217` vs z korekta na `15820d5` (raport: 170, 170, 171, 169, 171, 169, 171, 172 dla +0,1, -0,1,
  +0,3, -0,3, +0,5, -0,5, +1, -1): 170, 170, 171, 169, 171, 169, 172, 171 - roznice 1 pracy przy +-1 %.
- Wzgledem raportu czesci A (kod `15820d5`, z korekta) zielonych gniazd jest 48-49 zamiast 62-64 - to skutek czesci B
  ("nie sprawdzono" w P3a, pkt 1.2), nie korekty.

## 6. Strefa brzegu a estymata skali (zastrzezenie R2b), caly `syntetyczne_R59_P2`

`metryki_skala.py brzeg`, 217 prac "dobrze" z 24 skanow (wieczorne i poranne; raport czesci A: 95 prac z 12 skanow
wieczornych na `15820d5`), zmiana +-0,02 mm, prog "bez zmiany" 0,02 punktu proc. (`wyniki\brzeg_R59_P2.json`):

| wariant | z wylaczeniem pasa brzegu (program): w progu / srednia / p95 / max | bez wylaczenia (pas 0 mm, kontrola): w progu / srednia / p95 / max |
|---|---|---|
| powtorka | 217 / 217, +0,0000, 0,0001, 0,0006 | 217 / 217, -0,0000, 0,0001, 0,0004 |
| grubosc +0,02, pas A | 217 / 217, +0,0001, 0,0007, 0,0117 | 122 / 217, +0,0193, 0,0378, 0,0440 |
| grubosc -0,02, pas A | 217 / 217, -0,0001, 0,0006, 0,0104 | 127 / 217, -0,0184, 0,0362, 0,0415 |
| przesuniecie z +0,02, pas A | 217 / 217, +0,0001, 0,0005, 0,0119 | 185 / 217, +0,0112, 0,0228, 0,0289 |
| przesuniecie z -0,02, pas A | 217 / 217, -0,0001, 0,0005, 0,0104 | 193 / 217, -0,0089, 0,0237, 0,0282 |
| grubosc +0,02, pas C | 217 / 217, +0,0003, 0,0012, 0,0118 | **25 / 217**, +0,0795, 0,1699, 0,1853 |
| grubosc -0,02, pas C | 217 / 217, -0,0001, 0,0006, 0,0103 | **21 / 217**, -0,0773, 0,1612, 0,1766 |
| 3 ukruszenia fi 1,0 mm | 217 / 217, -0,0001, 0,0005, 0,0098 | 217 / 217, +0,0015, 0,0057, 0,0116 |

Z wylaczeniem pasa: 1519 / 1519 porownan (7 wariantow x 217 prac) w progu, max 0,012 (raport czesci A: 665 / 665, max
0,010). Bez wylaczenia zmiana strefy C przesuwa skale do 0,19 % (raport: 0,14 %). Wniosek raportu czesci A potwierdzony
na scalonym kodzie i na plytkach porannych.

## 7. Skutek poprawki `319f861` (korekty nie stosuje sie, gdy pokrycie po korekcie < 0,6)

| Miara (blad 0, korekta wlaczona) | `15820d5` R59 | `319f861` R59 | `fe66217` R59 | `fe66217` r54 |
|---|---|---|---|---|
| wierszy prac | 413 | 413 | 413 | 413 |
| korekta zastosowana | 171 | 168 | 168 | 180 |
| w tym przy pokryciu po korekcie < 0,6 | **3** | **0** | **0** | **0** |
| korekta niezastosowana z powodem "praca nierozpoznana" | 0 | 3 (bokiem) | 3 (bokiem) | 1 (bokiem) |
| top-1 inne z korekta niz bez (utracone / zyskane) | 1 / 0 | 0 / 0 | 1 / 0 | 0 / 0 |

- Poprawka dziala zgodnie z opisem: na zestawach nie ma juz ani jednej korekty zastosowanej do pracy o pokryciu < 0,6
  (bylo 3 na R59 przy bledzie 0 i 0-3 na kazdy blad w `v1\program_R59_wiecz_bledy.json`, razem 11 w 8 grupach).
- **Przypadek z pkt 3.0 raportu czesci A nie zniknal jednoznacznie.** To jedna praca (R59 P3a, plytka wieczorna n1,
  trzeci fragment w gniezdzie 3, lezy bokiem, szara w kazdym przebiegu). Bez korekty top-1 trafne w 2 z 3 odczytanych
  przebiegow (pokrycie wlasciwego projektu 0,4253; w trzecim wygral obcy projekt z 0,448), z korekta nietrafne w 3 z 3
  (obcy projekt 0,461 na `15820d5`, 0,442 na `319f861`, 0,429 na `fe66217`; dla wlasciwego "skali nie wyznaczono: za malo
  punktow przy projekcie (286 < 300)"). Sumy z dwoch dalszych przebiegow `fe66217` (388 / 397 z korekta) sa z tym
  zgodne. Dwa projekty roznia sie tu o 0,003-0,04 pokrycia przy pokryciu ok. 0,43, wiec wynik zalezy od rozrzutu
  RANSAC; 3 przebiegi nie rozstrzygaja, czy korekta systematycznie przegrywa. Skutek dla operatora: zaden (gniazdo
  szare w obu wariantach). Na r54: 0 roznic na 413 par.
- Skutek poprawki przy bledzie wspolczynnika (wieczorne): pkt 5.2.

## 8. Czas na plytke, jeden proces

`narzedzia\metryki_P3a.py --procesy 1`, 4 plytki z `syntetyczne_R59_P2` (po jednej kazdego ukladu, razem 40 prac), kazdy
pomiar = osobny proces z 1 skanem, warianty na przemian skan po skanie: stary kod `8b83da7` / scalony z
`korekta_skali = false` (P1) / scalony domyslny (P1 + P3). Dwie rundy po przerwie, kazda w jednych warunkach dla
wszystkich wariantow: **runda 1 (17:24-17:31) z limitem 2 watkow, runda 2 (18:26-18:34) bez limitu watkow** - rund nie
laczyc. W obu rundach PC byl **obciazony przez inne sesje** (5-10 procesow python, 15-20 GB wolnego RAM), moje partie
w tym czasie nie liczyly. Czasy w sekundach na plytke; "linie" = jednorazowe wyznaczenie linii brzegu projektow
(czesc B) - liczone od zera, bo kazdy pomiar to nowy proces.

| Plytka (prac) | runda | stary kod: razem | P1: razem / bez linii | P1 + P3: razem / bez linii |
|---|---|---|---|---|
| wieczorna n3 (8) | 1 (2 watki) | 8,56 | 34,94 / 17,14 | 31,19 / 15,56 |
| wieczorna n3 (8) | 2 (bez limitu) | 7,79 | 34,01 / 16,13 | 32,44 / 16,21 |
| poranna n4 (12) | 1 | 12,97 | 48,96 / 23,16 | 51,00 / 24,72 |
| poranna n4 (12) | 2 | 15,59 | 52,76 / 24,78 | 51,98 / 24,63 |
| okragla wieczorna n8 (8) | 1 | 6,78 | 32,65 / 13,05 | 34,72 / 14,21 |
| okragla wieczorna n8 (8) | 2 | 6,64 | 31,70 / 12,60 | 31,60 / 13,01 |
| okragla poranna n9 (12) | 1 | 19,66 | 58,28 / 29,68 | 53,32 / 26,88 |
| okragla poranna n9 (12) | 2 | 15,02 | 45,68 / 22,07 | 46,98 / 23,34 |
| **suma 4 plytek** | 1 | **47,97** | **174,83 / 83,03** | **170,23 / 81,37** |
| **suma 4 plytek** | 2 | **45,04** | **164,15 / 75,58** | **163,00 / 77,19** |

Skladniki sumy 4 plytek (runda 1 / runda 2):

| Skladnik | stary kod | P1 | P1 + P3 |
|---|---|---|---|
| plate | 8,78 / 8,73 | 9,49 / 8,65 | 9,10 / 8,56 |
| match bez inspect | 30,54 / 27,82 | 57,25 / 51,63 | 56,53 / 53,39 |
| inspect bez linii brzegu | 4,39 / 4,17 | 11,79 / 11,16 | 11,40 / 10,88 |
| linie brzegu (jednorazowo na proces) | - | 91,80 / 88,57 | 88,86 / 85,79 |

- Stary kod -> scalony, plytka "ciepla" (bez linii): 11-12 s -> 19-21 s na plytke srednio (+68 ... +73 %); z liniami
  brzegu liczonymi od zera 41-44 s (x 3,6). Linie brzegu to 16-29 s na plytke i 88-92 s na 4 plytki.
- **Korekta skali (P1 -> P1 + P3): roznica ponizej rozrzutu pomiaru** - suma bez linii 83,0 -> 81,4 s (runda 1) i 75,6 ->
  77,2 s (runda 2); na samych plytkach wieczornych (tylko tam korekta jest stosowana) 30,2 -> 29,8 s i 28,7 -> 29,2 s.
  Zgodne z sonda z raportu czesci A (0,06-0,14 s na prace).
- **"match bez inspect" 28-31 s -> 52-57 s (+0,6 s na prace) miedzy starym kodem a scalonym** jest wieksze niz +0,16 s na
  prace z proby w raporcie czesci A (1 skan). Pomiar P1 z pelnym dopasowaniem (pkt 4.2) daje dla samego filtra +0,5 s na
  prace pelnej wysokosci (0,83 -> 1,34 s), wiec wiekszosc tego wzrostu to P1 (wiecej projektow przechodzi filtr: 2,2
  zamiast 1,65). Nie rozdzielalem, ile z reszty przypada na zmiany `porownaj.py` / `plate.py`.
- To sa czasy z PC obciazonego innymi sesjami, 1 runda na warunki - rozrzut miedzy rundami do 8 s na plytke; do
  planowania przyjac rzad wielkosci, nie dokladne wartosci. Pomiary sprzed przerwy (`wyniki\czasy\`, 38 procesow na PC)
  daly czasy kilka razy dluzsze i sa bezuzyteczne.

## 9. Odstepstwa i zdarzenia

1. **Budzet.** Zlecenie: ok. 90 min. Faktycznie ok. 4 h 25 min (14:50-19:15), w tym zatrzymanie PC ok. 16:00 i powtorka utraconych partii - po przerwie koordynator wydluzyl budzet ("kompletnosc
   wazniejsza niz tempo").
2. **Blad narzedzia `metryki_skala.py program`** (pkt 1.5) - pierwszy przebieg R59 (12 min, 8 procesow) przeliczyl 80
   zadan i padl przy podsumowaniu; liczby z niego sa tylko z logu.
3. **Zatrzymanie PC ok. 16:00** (wlasciciel; 0,4 GB wolnego RAM, CPU 88 C). O 15:59 bylo 38 procesow python trzech
   sesji, z tego moich 16 (11 roboczych w 4 torach + pomiar czasu); wolny RAM w mojej sesji schodzil do 0,8-1,2 GB juz od
   15:00 (PC mial na starcie 14,9 GB wolnego z 31,6 GB, nie 32 GB; proces roboczy bierze 2-2,7 GB pamieci roboczej,
   3,5-4,4 GB zatwierdzonej). Przepadly: R59 blad 0 (60 / 80 zadan), r54 (27 / 40), poranne +-0,5 % (16 / 24), P1 z
   dopasowaniem (1 / 24 skanow po 49 min), ostatni z 12 pomiarow czasu. Wszystko powtorzone po przerwie pod limitami
   (jedyny wyjatek: plytki wieczorne przy bledach w wariancie bez korekty - pkt 9.6). Zapis wyniku dopiero na koncu przebiegu byl przyczyna strat - powtorki szly w malych partiach.
4. **Moje bledy operacyjne (bez wplywu na liczby):** (a) o 15:00 chcialem zatrzymac wlasny przebieg 8-procesowy przy
   [usunieto w kopii: opis dostepu ssh]
   przebieg doszedl do konca; (b) o 15:21 proba owijki uruchomila przez pomylke dodatkowy przebieg 3-procesowy, ktory
   sam sie zakonczyl po 6,5 min (bez wyniku); (c) dwukrotnie podmienilem `run.cmd` w trakcie dzialajacego kroku
   (dopisanie limitow watkow) - `cmd` wykonal krok drugi raz: partie r54 P2 i r54 P3a policzyly sie po dwa razy (wyniki
   obu powtorek identyczne; w JSON jest druga).
5. **Warunki liczenia poszczegolnych pomiarow** (limity zmienialy sie trzy razy: 16:15, ok. 16:30, ok. 18:10 - ostatnia
   zmiana to decyzja wlasciciela: 6 procesow, bez warunku RAM, bez limitu watkow). Limit watkow = `OMP_NUM_THREADS` =
   `OPENBLAS_NUM_THREADS` = `MKL_NUM_THREADS` = 2 w `run.cmd`. **Czasy miedzy wierszami o roznych warunkach nie sa
   porownywalne**; liczniki sa (R59 blad 0 dal te same sumy w 8 procesach bez limitu i w 2 procesach z limitem).

   | Pomiar (plik wyniku) | godz. PC | procesy robocze | limit watkow |
   |---|---|---|---|
   | R59 blad 0, przebieg 1 (tylko log) | 14:57-15:09 | 8 | brak |
   | przebiegi przerwane (tylko logi) | 15:12-16:02 | 3 + 3 + 2 + 2 + 1 naraz | brak |
   | `p1_R59_P2_filtr.json` | 15:32-15:36 | 2 | brak (PC przeciazony) |
   | `program_R59_P2_rano_bledy.json` | 16:08-16:16 | 4 | brak |
   | `program_r54_P2_e0_tak.json` (druga z dwoch powtorek) | 16:21-16:27 | 3 | brak |
   | `program_r54_P3a_e0_tak.json` (druga z dwoch powtorek) | 16:33-16:38 | 2 | 2 |
   | `program_R59_P3a_e0.json`, `program_R59_P2_e0.json` | 16:38-16:59 | 2 | 2 |
   | `program_R59_P3a_rano_bledy.json`, `program_r54_e0_nie.json`, `brzeg_R59_P2.json`, `p1_R59_P3a.json` | 16:59-17:23 | 2 | 2 |
   | czas, runda 1 (`czasy2`, pliki `czas_r1_*`) | 17:24-17:31 | 1 | 2 |
   | `p1_R59_P2_dopasuj_8.json` | 17:31-17:51 | 2 | 2 |
   | `program_R59_wiecz_blad_05.json`, `_03`, `_10` | 17:51-18:15 | 2 | 2 |
   | `program_R59_wiecz_blad_01.json` | 18:15-18:21 | 6 | 2 (zmienna zostala w srodowisku dzialajacej kolejki) |
   | `a319_program_r54_e0_tak.json` (kod `319f861`) | 18:21-18:26 | 6 | brak |
   | czas, runda 2 (`czasy2`, pliki `czas_r2_*`) | 18:26-18:34 | 1 | brak |
   | `p1_R59_P2_dopasuj_16.json` | 18:34-19:07 | 6 | brak |

   Kontrola wolnego RAM przed partia (>= 8 GB od 16:15, >= 10 GB od ok. 16:30, bez warunku od 18:10) byla wbudowana w
   owijke `ms.py` - kazda partia zapisuje stan RAM w pierwszej linii swojego logu; zadna partia nie czekala.
6. **Zakres mniejszy niz w `v2a.cmd` / `v2b.cmd`:** plytki wieczorne przy bledach tylko z korekta (wariant bez korekty na
   scalonym kodzie rozni sie od `15820d5` tylko czescia B i zostal pominiety); P1 z dopasowaniem policzone na calym P2, ale w dwoch partiach o roznych warunkach (8 + 16 skanow, pkt 4.2) - liczniki laczne, czasy osobno.
7. Analizy pomocnicze (`porownanie2.py`, `ab.py` itd.) to krotkie pojedyncze procesy python uruchamiane obok partii
   pomiarowej (kilka sekund).

## 10. Gdzie leza dane i jak powtorzyc (PC, `<PC-katalog>\app\k2a\`)

- Program: `Ramki\stanowisko` (= `fe66217`), `run.cmd` (z limitami watkow), `run_baza.cmd` (stary kod w `..\a\baza`, tylko
  odczyt), `run_a319.cmd` (kod `319f861` w `..\a`, tylko odczyt); warianty ustawien `ust_bez_korekty.toml`,
  `ust_plaszczyzna.toml`, `ust_plaszczyzna_bez_korekty.toml` (`skrypty\mkust.py`; uzyty tylko pierwszy).
- Wyniki `wyniki\`: `program_R59_P2_e0.json`, `program_R59_P3a_e0.json` (zlaczone: `zl_R59_e0.json`),
  `program_r54_P2_e0_tak.json`, `program_r54_P3a_e0_tak.json`, `program_r54_e0_nie.json` (zlaczone: `zl_r54_e0.json`),
  `program_R59_P2_rano_bledy.json`, `program_R59_P3a_rano_bledy.json`, `p1_R59_P2_filtr.json`, `p1_R59_P3a.json`,
  `brzeg_R59_P2.json`, `czasy2\czas_r<runda>_<skan>_<baza|p1|p1p3>.json` (po przerwie, 2 watki), `czasy\` (przed przerwa,
  PC przeciazony - nie uzywac), `program_R59_wiecz_blad_01/03/05/10.json` (zlaczone: `zl_R59_wiecz_bledy.json`), `p1_R59_P2_dopasuj_8.json`,
  `p1_R59_P2_dopasuj_16.json` (zlaczone: `p1_R59_P2_dopasuj.json`), `a319_program_r54_e0_tak.json` (kod `319f861` na r54). Logi: `logi\` (`postep.log` = kolejnosc i godziny; `program_R59_e0.log` = przebieg 1,
  `program_R59_e0_b.log`, `program_r54_e0_tak.log`, `program_R59_P2_rano_bledy.log` = przebiegi przerwane o 16:02).
- Skrypty robocze `skrypty\` (poza repo): `ms.py` (owijka narzedzia: obejscie bledu z pkt 1.5, limit 2 procesow,
  kontrola >= 10 GB RAM), `ms_a319.py` (to samo dla `319f861`), `ram10.py`, `torF.cmd`, `torG.cmd`, `torH.cmd` (kolejki po
  przerwie; `torA`-`torE.cmd`, `czasy2.cmd` = kolejki sprzed przerwy), `porownanie2.py` (stary kod vs nowy),
  `perzestaw.py`, `ab.py` (dwa kody praca po pracy), `skutek_319.py`, `ostrz.py`, `odst.py`, `bezostrz.py`, `jedna.py`,
  `czasy3.py`, `scal.py`, `spr_ust.py`, kopie skryptow z `..\a\skrypty`.
- Polecenia (`R` = `<PC-katalog>\app\k2a\run.cmd`, `S` = `<PC-katalog>\app\k2a\skrypty`, `W` = `...\k2a\wyniki`,
  `D` = `<PC-katalog>\app\dane_ref`, `P` = `<PC-katalog>\app\Prace_test`, `B` = `<PC-katalog>\app\a\wyniki\baza`):
```
R S\ms.py program --skany D\syntetyczne_R59_P2 --projekty P --wyjscie W --nazwa program_R59_P2_e0.json --bledy 0 --procesy 2
R S\ms.py program --skany D\syntetyczne_R59_P3a --projekty P --wyjscie W --nazwa program_R59_P3a_e0.json --bledy 0 --procesy 2
R S\ms.py program --skany D\syntetyczne_r54_P2 --projekty P --sufiks-ukladu _r54 --wyjscie W --nazwa program_r54_P2_e0_tak.json --bledy 0 --korekta tak --procesy 2
R S\ms.py program --skany D\syntetyczne_r54_P3a --projekty P --sufiks-ukladu _r54 --wyjscie W --nazwa program_r54_P3a_e0_tak.json --bledy 0 --korekta tak --procesy 2
R S\ms.py program --skany D\syntetyczne_r54_P2 D\syntetyczne_r54_P3a --projekty P --sufiks-ukladu _r54 --wyjscie W --nazwa program_r54_e0_nie.json --bledy 0 --korekta nie --procesy 2
R S\ms.py program --skany D\syntetyczne_R59_P2 --projekty P --wyjscie W --nazwa program_R59_P2_rano_bledy.json --wzorzec skan_*poranna* --bledy 0.5,-0.5 --korekta tak --procesy 2
R S\ms.py program --skany D\syntetyczne_R59_P3a --projekty P --wyjscie W --nazwa program_R59_P3a_rano_bledy.json --wzorzec skan_*poranna* --bledy 0.5,-0.5 --korekta tak --procesy 2
R S\ms.py p1 --skany D\syntetyczne_R59_P2 --projekty P --wyjscie W --nazwa p1_R59_P2_filtr.json --progi-wysokosci 0 0.5 0.6 0.7 0.8 1.0 --procesy 2
R S\ms.py p1 --skany D\syntetyczne_R59_P3a --projekty P --wyjscie W --nazwa p1_R59_P3a.json --scenariusze pelny --progi-wysokosci 0 0.5 0.6 0.7 0.8 1.0 --procesy 2
R S\ms.py p1 --skany D\syntetyczne_R59_P2 --projekty P --wyjscie W --nazwa p1_R59_P2_dopasuj_8.json --wzorzec skan_*0[0-1].stl --dopasuj --progi-wysokosci 0 0.5 0.6 0.7 0.8 1.0 --procesy 2      (16 pozostalych: --wzorzec skan_*0[2-5].stl -> p1_R59_P2_dopasuj_16.json; zlaczenie: R S\p1scal.py)
R S\ms.py brzeg --skany D\syntetyczne_R59_P2 --projekty P --wyjscie W --nazwa brzeg_R59_P2.json --procesy 2
R S\ms.py program --skany D\syntetyczne_R59_P2 D\syntetyczne_R59_P3a --projekty P --wyjscie W --nazwa program_R59_wiecz_blad_05.json --wzorzec skan_*wieczorna* --bledy 0.5,-0.5 --korekta tak --procesy 2      (tak samo 0.3,-0.3 / 1,-1 / 0.1,-0.1 -> ..._03, ..._10, ..._01)
R S\scal.py W\zl_R59_e0.json W\program_R59_P2_e0.json W\program_R59_P3a_e0.json
R S\porownanie2.py B\metryki_R59.json W\zl_R59_e0.json            (r54: B\metryki_r54.json W\zl_r54_e0.json)
R S\ab.py <PC-katalog>\app\a\wyniki\v2\program_R59_e0.json W\zl_R59_e0.json
R S\skutek_319.py W\zl_R59_e0.json      R S\ostrz.py W\program_R59_P2_rano_bledy.json      R S\czasy3.py W\czasy2
```
  Czas: `skrypty\torG.cmd` krok g5 / `torH.cmd` krok h2 (`run_baza.cmd` / `run.cmd narzedzia\metryki_P3a.py --wzorzec
  skan_<skan>.stl --procesy 1`, wariant P1 z `--ustawienia k2a\ust_bez_korekty.toml`).
- Uwaga dla powtarzajacego: nie podmieniac `run.cmd` w trakcie kroku (pkt 9.4c); procesy startowane przez ssh dzialaja
  dalej po zerwaniu polaczenia; `metryki_skala.py` zapisuje JSON dopiero na koncu przebiegu.
