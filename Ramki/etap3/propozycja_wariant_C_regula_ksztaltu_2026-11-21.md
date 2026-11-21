WNIOSEK: zmiana reguly "najpierw ksztalt" usuwa pewny zly KWADRAT dla plytki testowej n8 / n9 (24 z 24 nowych przypadkow), ale daje tam uklad dobry "niepewny", a nie "pewny" jak przed paczka; na 80 skanach odniesienia nic sie nie zmienia (160 z 160); regula w brzmieniu recenzenta (C1) bez jednego wyjatku pogarsza 13 z 54 przebiegow z recznie wpisanym zlym numerem - dlatego proponuje wariant C3.

# Pomiar "co by bylo": regula ksztaltu kolo / kwadrat w rozpoznaniu ukladu (wariant C) - 21.11.2026

Pomiar, nie paczka: `plate.py` bez zmian, 0 commitow. Regule alternatywna liczy skrypt poza repo (`pomiar_c.py`), kod programu
z kopii `qc-wt\wc` (43d78e1). Wszystkie skany sa SZTUCZNE (generator programu); prawdziwych skanow plytek okraglych nie ma.
466 przebiegow na 252 skanach, 10:44-11:09, bledow 0, przebiegow bez wyniku 0.

## 1. Najwazniejsze (takze to, co gorsze)
1. GORSZE niz przed paczka takze po zmianie: plytka testowa n8 / n9 z nieczytelnym dolkiem i bez scianki bocznej w skanie -
   przed paczka (8 ukladow) "dobry pewny" 30 z 32, po zmianie reguly "dobry NIEPEWNY" 24 z 32 (+ 6 pewnych, 2 zle). Powod: bez
   scianki i bez dolkow plytki testowej nie da sie odroznic od ramkowej; program bierze pierwsza z listy (testowa) i sam
   oznacza wybor jako niepewny. Program glowny flagi `pewny` dzis nie czyta (raport recenzenta, W12).
2. GORSZE w wariancie C1 (regula doslownie wg recenzenta): plytka testowa z CZYTELNYMI dolkami, gdy czlowiek wpisze recznie numer
   1-6: dzis (10 ukladow) dobrze i pewnie 18 z 18; C1 - zle 13 z 18 (6 "zly pewny", 7 "zly niepewny" = plytka ramkowa zamiast
   testowej). Wariant C3 (C1 + jeden wyjatek, sekcja 4) i C2 tego nie psuja: 18 z 18 jak dzis.
3. LEPSZE (C1, C2, C3 tak samo): pewny zly KWADRAT dla plytki testowej znika - 24 z 24 przypadkow wprowadzonych paczka.
4. BEZ ZMIAN: 80 skanow odniesienia (160 z 160), plytki ramkowe n1-n6 (24 z 24), pola 96 / 94 (56 z 56), kwadraty R59 przy
   polu 99-97 (12 z 12). Plytki kwadratowe z numerem z ramki: 0 zmian ukladu, 0 zmian `pewny` (sekcja 5).

## 2. Dowod, ze kopia logiki liczy to samo co oryginal
Regula DZISIEJSZA w kopii wobec oryginalnego `plate.rozpoznaj_uklad` (uklad, `pewny`, `powod`, numer, zrodlo numeru):
86 z 86 przebiegow zgodnych przy 8 ukladach i 86 z 86 przy 10 (48 skanow: 32 odniesienia w obu trybach + 16 z zestawu C -
plytki testowe z zaslonietym dolkiem, ramkowe, kwadraty). Powody w probie: ksztalt 26, numer_podany 24, dolki_wykluczaja 20,
numer_z_dolkow 16. Kolumny "dzis" ponizej pochodza z tej kopii (uklady liczone raz na skan; "8" = ta sama lista bez 2 ramkowych).

## 3. Tabela (liczniki; DP dobry pewny, DN dobry niepewny, ZP zly pewny, ZN zly niepewny)
| Zestaw (skany / przebiegi) | dzis 8 ukladow | dzis 10 ukladow | regula C (C3) | C1 / C2, gdy inaczej |
|---|---|---|---|---|
| A: 80 skanow odniesienia, bez numeru i z numerem (80 / 160) | DP 160 z 160 | DP 160 z 160 | DP 160 z 160 | - |
| B: ramkowe n1-n6, 2 ziarna, pole 100, oba tryby (12 / 24) | nie dotyczy (*) | DP 24 z 24 | DP 24 z 24 | - |
| C: testowa n8 / n9, dolek zasloniety (D albo 4), pole 99 / 98 / 97 albo bez scianki, bez numeru (32 / 32) | DP 30, ZP 2 | DP 6, ZP 26 | DP 6, DN 24, ZP 2 | - |
| C: testowa, dolki czytelne (5 warunkow) albo zasloniete przy polu 100 ze scianka, bez numeru (28 / 28) | DP 28 z 28 | DP 28 z 28 | DP 28 z 28 | - |
| C: testowa, wszystkie 60 skanow z numerem zgodnym (60 / 60) | DP 60 z 60 | DP 60 z 60 | DP 60 z 60 | - |
| C: ramkowa, 4 dolki zasloniete, pole 100 / 99 / 98, oba tryby (12 / 24) | nie dotyczy (*) | DP 24 z 24 | DP 24 z 24 | - |
| C: ramkowa, 4 dolki zasloniete, bez scianki, bez numeru (4 / 4) | nie dotyczy (*) | ZP 4 (kwadrat) | ZN 4 (testowa) | - |
| C: ramkowa, 4 dolki zasloniete, bez scianki, z numerem zgodnym (4 / 4) | nie dotyczy (*) | ZP 4 (kwadrat) | DP 4 | C2: ZN 4 |
| C: ramkowa, dolki czytelne, bez scianki, oba tryby (4 / 8) | nie dotyczy (*) | DP 8 z 8 | DP 8 z 8 | - |
| C: kwadraty R59 n2 / n5, pole 99 / 98 / 97, oba tryby (6 / 12) | DP 12 z 12 | DP 12 z 12 | DP 12 z 12 | - |
| D: pola 96 i 94, 10 ukladow, oba tryby (28 / 56) | DP 40 z 40 (*) | DP 56 z 56 | DP 56 z 56 | - |
| E: kwadrat R59 z wpisanym 8 / 9, pole 100 i 96 (8 / 8) | ZP 5, ZN 3 | ZP 5, ZN 3 | DN 3, ZP 5 | C2: jak dzis |
| E: kwadrat R54 z wpisanym 8 (4 / 4) | ZP 2, ZN 2 | ZP 2, ZN 2 | DN 2, ZP 2 | C2: jak dzis |
| E: testowa R54 z wpisanym numerem kwadratu (4 / 4) | ZP 2, ZN 2 | ZP 2, ZN 2 | DN 2, ZP 2 | C2: jak dzis |
| E: testowa R59 z wpisanym 1 / 4, pole 100 i 96 (8 / 8) | ZP 4, ZN 4 | DP 8 | DP 8 | C1: DP 4, ZN 4 |
| E: ramkowa z wpisanym 8 / 9 (8 / 8) | nie dotyczy (*) | ZP 1, ZN 7 | ZP 1, ZN 7 | - |
| E: ramkowa n1 z wpisanym 2 i 4 (4 / 8) | nie dotyczy (*) | DP 8 z 8 | DP 8 z 8 | - |
| F (dodany): testowa R59, dolki czytelne, wpisany 1 / 4, pola 100-97 i bez scianki (10 / 10) | ZP 1, ZN 9 | DP 10 | DP 10 | C1: DP 1, ZP 6, ZN 3 |
| F (dodany): ramkowa z wpisanym 8 / 9, pole 98 i bez scianki (4 / 4) | nie dotyczy (*) | ZP 2, ZN 2 | ZP 2, ZN 2 | - |
| **Pogorszenie wobec dzis 8 ukladow** (plytki z listy 8: 366 przebiegow) | - | 24 (DP -> ZP) | 24 (DP -> DN) | C1: 30 (24 DP -> DN, 6 ZN -> ZP); C2: 24 (DP -> DN) |
| **Poprawa wobec dzis 8 ukladow** (te same 366) | - | 18 | 25 | C1: 12; C2: 18 |
| **Pogorszenie wobec dzis 10 ukladow** (466 przebiegow) | - | - | 0 | C1: 13 (DP -> ZN 7, DP -> ZP 6); C2: 0 |
| **Poprawa wobec dzis 10 ukladow** (466) | - | - | 39 (ZP -> DN 24, ZP -> DP 4, ZP -> ZN 4, ZN -> DN 7) | C1: 39; C2: 32 (ZP -> DN 24, ZP -> ZN 8) |

(*) ukladu ramkowego nie ma na liscie 8, wiec wynik zawsze zly (w D licznik 8 ukladow bez 16 przebiegow plytek ramkowych).
Dla porownania z recenzentem (17 z 26 par): u mnie 24 z 32 skanow "8 ukladow dobrze i pewnie -> 10 ukladow kwadrat, pewny".

## 4. Regula slowami i pseudokodem
Dzis: program porownuje ksztalt DWOCH najlepszych ukladow; po paczce sa nimi dwa okragle, wiec ksztalt nie rozstrzyga i regula
"dolki wykluczaja" odrzuca oba okragle. Propozycja: najpierw pytanie "kolo czy kwadrat", potem reszta tylko w tym ksztalcie.

    kola, kwadraty = uklady okragle / kwadratowe, ktore przeszly stozki i gniazda
    jesli sa oba ksztalty i |najlepsze kolo - najlepszy kwadrat| >= 40 mm2 (PROG_KSZTALTU_MM2, bez zmiany):
        pula = uklady wygranego ksztaltu
        jeden uklad w puli -> ten uklad (powod "ksztalt"); kilka -> reguly DZISIEJSZE na samej puli
            (numer podany, numer z dolkow, ksztalt dwoch najlepszych, dolki wykluczaja, domyslny z pewny = False)
        numer podany albo z dolkow pasuje tylko do ukladu przegranego ksztaltu -> ksztalt wygrywa, pewny = False
        [tylko C3] wyjatek: gdyby w puli wygral numer podany, a ten numer pasuje tez do ukladu drugiego ksztaltu
            i inny uklad puli ma wazny numer z dolkow -> zostaje wynik reguly dzisiejszej (numer z dolkow)
    w przeciwnym razie (ksztalt nie rozstrzyga, np. pole 96): reguly dzisiejsze na wszystkich ukladach, bez zmiany

- C1 = powyzsze bez wyjatku (propozycja recenzenta). C3 = z wyjatkiem (dodalem po wyniku zestawu E; zalecany).
- C2 = zmiana najmniejsza: numer podany, numer z dolkow i ksztalt dwoch najlepszych jak dzis; tylko ostatnia galaz ("dolki
  wykluczaja" / domyslny) dziala w obrebie ksztaltu, ktory wygral. Nie psuje niczego, ale nie korzysta z numeru z ramki dla
  plytki ramkowej bez scianki (ZN 4 zamiast DP 4) i nie poprawia "kwadrat z wpisanym 8 / 9".
- "Numer podany pasuje do jednego ukladu, ksztalt mowi co innego": dzis numer wygrywa, `pewny` = False (zly uklad niepewny);
  C1 / C3 - wygrywa ksztalt, numer pominiety, `pewny` = False (uklad dobry niepewny 7 z 8 przy polu 100; 1 z 8 zostaje zly pewny);
  C2 - jak dzis. Bez brzegu w skanie (pole 96) wszystkie warianty jak dzis: zly pewny 8 z 8 (zestaw E).

## 5. Co by sie zmienilo w `plate.py` i dla plytek kwadratowych
- C3: wiersze 826-850 (25 wierszy) zastapione ok. 45: dzisiejsze reguly przeniesione bez zmian do funkcji pomocniczej + ok. 20
  nowych wierszy; do tego opis w naglowku funkcji (wiersze 763-768) i w `opisy_modulow/plate.md`. C2: tylko wiersze 842-850,
  ok. 6 nowych wierszy. `ksztalt_plytki`, progi, wyrownanie, straznik - bez zmian.
- Kwadraty R59 (68 przebiegow z A, C, D, E): bez numeru i z numerem z ramki - 60 z 60 bez zmiany ukladu, `pewny`, `powod`
  i numeru; jedyne 3 zmiany to kwadrat z recznie wpisanym 8 / 9 (uklad zly -> dobry, `pewny` False bez zmiany).
- Kwadraty R54 (44 przebiegi): zmian ukladu 2 (obie = poprawa przy wpisanym 8), `pewny` 0; `powod` 17 razy zmienia etykiete
  "numer_podany" -> "ksztalt" (15 w zestawie A). Okragle R54 (60): uklad 2 (poprawa), `pewny` 0, etykieta `powod` 52 razy
  (-> "ksztalt"). W rodzinie R54 sa tylko 2 uklady, wiec ksztalt wybiera od razu; uklad, numer i `pewny` te same. W C2: 0 zmian.
- Miara ksztaltu kolo / kwadrat ani razu nie wskazala zlego ksztaltu z przewaga >= 40 mm2 (0 z 466 przebiegow).

## 6. Co zostaje nierozwiazane takze po zmianie
1. Testowa wobec ramkowej bez scianki bocznej i bez waznego numeru z dolkow: wybor domyslny = pierwsza na liscie (testowa),
   `pewny` = False. Plytka testowa: dobry niepewny 24 z 24; plytka ramkowa bez numeru: ZLY niepewny 4 z 4 (testowa zamiast
   ramkowej; z numerem z ramki C1 / C3 dobrze 4 z 4). Do decyzji: ktory uklad okragly ma byc domyslny i czy program ma czytac `pewny`.
2. Testowa z zaslonietym dolkiem przy polu 97: 2 z 8 kwadrat pewny takze przy 8 ukladach (miara ksztaltu 34-35 < 40).
3. Recznie wpisany numer drugiego ksztaltu, gdy w skanie nie ma brzegu (pole 96): zly pewny 8 z 8; przy polu 100 - 1 z 8.
4. Plytka ramkowa z wpisanym 8 / 9: zly uklad (testowa) 12 z 12 w kazdym wariancie (3 pewne) - numer podany wygrywa z dolkami.

## 7. Regresja potrzebna przed scaleniem prawdziwej paczki i szacunek pracy
- Testy najpierw: ok. 8 nowych testow (przypadki z zestawow C, E, F); testy sprawdzajace `powod` (22 wiersze w 2 plikach) do
  przejrzenia - etykieta zmienia sie dla R54, chyba ze paczka zachowa stara etykiete.
- Narzedzie bramki `auto_uklad_r58.py` na 80 skanach (po poprawce uwagi 3 recenzenta), T10 (40 skanow), T11 (40 skanow),
  pelny pytest (ok. 20 min; punkt odniesienia galezi O1 wg wykonawcy: 2275 passed, 9 skipped), proby recenzenta W6-W9
  (`proba_bramka.py`, `proba_k4.py`, `proba_d.py`) i ten pomiar powtorzony na prawdziwym kodzie (`pomiar_c.py`, ok. 25 min).
- Szacunek (nie pomiar): wykonawca 3-4 godziny (kod i testy ok. 2 h, serie ok. 1,5 h pracy PC), recenzja 1 runda ok. 2 h.

## 8. Czego nie zmierzono / przyjete domyslnie
- Prawdziwych skanow nie ma - wszystko sztuczne; "bez scianki" to konstrukcja recenzenta (usuniete trojkaty r >= 49 mm).
- Pola 90 i 80 mm (wg recenzenta brak wyniku przed wyborem ukladu), T10, T11, pelny pytest, ciecie na gniazda, czas rozpoznania.
- Malo ziaren: 1-2 na przypadek; plytki testowe R54 i kwadraty z zaslona - nie badane. Zestaw D: 28 skanow (1-2 plytki na uklad).
- Przyjete domyslnie: kolumny "dzis" z kopii logiki (zgodnosc 86 z 86), nie z oryginalu; wariant C3 i zestaw F dodane przeze
  mnie; C3 dla serii policzonych przed jego dopisaniem (452 przebiegi) wyliczony z zapisanych wierszy - ta sama metoda
  sprawdzona wprost na 14 z 14 przebiegow zestawu F.

## 9. Pliki (katalog `<PC-katalog>\koordynator\robocze\wariant_c\`)
`pomiar_c.py` (kopia logiki, reguly dzis / C1 / C2 / C3, zestawy A-F), `tabela.py` (zestawienie), `wyniki_1.jsonl` (A, E, D),
`wyniki_2.jsonl` (C, B), `wyniki_3.jsonl` (F), `tabela_wszystko.txt` (pelne liczniki wg grup), `krok_pomiar.cmd`, logi.
