# R59 - propozycja nowego ukladu gniazd plytek (do bramki G0)

Data: 2026-11-14, subsesja R59-U. PROPOZYCJA: `parametry.json` nie jest zmieniony, wybiera wlasciciel. Pozycje policzylo
`narzedzia/uklad_kolo_R59.js`, sprawdzil osobny `narzedzia/weryfikuj_uklad_R59.js` (8 z 8 plikow wariantow: 0 bledow,
kod wyjscia 0). Szkice: `R59_szkice/szkic_*.png` (stary uklad nad nowym) i `szkic_przeglad_*.png`. Wymiary w mm.

## 1. Dzis i warianty

| Plytka WIECZORNA | fi 9 | fi 12 | fi 15 | rynienki | razem | max promien obrysu (limit 47) | min scianka |
|---|---|---|---|---|---|---|---|
| dzis (R54) | 7 | 6 | 5 | 2 | 18 + 2 | 46,39 | 3,00 |
| W-a najwiecej fi 15 | 0 | 0 | 16 | 1 | 16 + 1 | 45,81 | 3,00 |
| **W-b zrownowazony** | 0 | 6 | 12 | 1 | 18 + 1 | 45,93 | 3,00 |
| W-c najmniejsza zmiana | 7 | 6 | 8 | 1 | 21 + 1 | 46,39 | 3,00 |

| Plytka PORANNA | fi 7,5 | fi 10 | fi 12,5 | fi 15 | rynienki | razem | max promien obrysu (limit 47) | min scianka |
|---|---|---|---|---|---|---|---|---|
| dzis (R54) | 18 | 7 | 6 | 0 | 2 | 31 + 2 | 46,93 | 3,00 |
| P-a najwiecej duzych | 0 | 7 | 11 | 5 | 1 | 23 + 1 | 45,76 | 3,00 |
| **P-b zrownowazony** | 8 | 13 | 6 | 3 | 1 | 30 + 1 | 46,50 | 3,00 |
| P-c najmniejsza zmiana | 13 | 7 | 6 | 3 | 1 | 29 + 1 | 46,32 | 3,00 |

**Zalecenie: W-b i P-b, rynienka jedna dluga (D3-a).** Powody (liczby w pkt 2):
- W-b: tyle gniazd co dzis (18), ale w kazde wchodzi praca z proby - dzis 7 z 18 to fi 9, w ktore nie weszla zadna.
  Gniazd fi 15 jest 12 zamiast 5; zapas do kola skanowania rosnie z 0,61 do 1,07.
- P-b: 30 gniazd (dzis 31); fi 7,5 jest 8 zamiast 18, fi 10 jest 13 zamiast 7, dochodza 3 x fi 15. Znika rynienka
  tylna, ktora dzis lezy 0,07 od granicy kola; najmniejszy zapas rosnie do 0,50.
- W-a / P-a - gdy ida glownie duze prace (gniazd mniej: 16 i 23). W-c / P-c - gdy ma sie zmienic jak najmniej, ale
  zostaje w nich 7 x fi 9 i 13 x fi 7,5.

**W kazdym wariancie zostaje rynienka PRZEDNIA:** (1) most lezy najblizej technika, jak dzis w rynience przedniej;
(2) w porannej usuwana rynienka tylna to dzis najciasniejsze miejsce ukladu; (3) w W-c przod plytki sie nie zmienia,
wiec stozki, dolki i cyfra zostaja. W P-a i P-b rynienka jest pierwszym rzedem (dzis drugim), zeby przed nia zmiescil
sie rzad dolkow plytki okraglej - w tym samym miejscu co na wieczornej.

## 2. Co mowia projekty (17 sztuk - proba mala i dobrana do testow, nie przekroj produkcji)

Najmniejsze gniazdo, w ktore wchodzi projekt (regula programu: `kandydaci_gniazd` + `osadz_w_gniezdzie`):

| | fi 9 / 7,5 | fi 12 / 10 | fi 15 / 12,5 | potrzebne wieksze gniazdo | tylko rynienka |
|---|---|---|---|---|---|
| wieczorna (skala 1,22) | 0 z 17 | 5 z 17 | 4 z 17 | 2 z 17 (nie wchodza w fi 15, wchodza w fi 18) | 6 z 17 |
| poranna (skala 1,0) | 0 z 17 | 5 z 17 | 4 z 17 | 2 z 17 (wchodza w fi 15) | 6 z 17 |

Zrodlo: `katalog.json` oraz przeliczenie ta sama procedura dla gniazd, ktorych dzis nie ma (fi 15 w porannej, fi 18,
krotkie rynienki); dla gniazd dzisiejszych wynik zgadza sie z katalogiem 17 / 17.
- W fi 9 i fi 7,5 nie weszla zadna z 17 prac - popiera zlecenie pkt 1.
- Dzis w rynienke trafia 8 z 17 prac: 6 dlugich (mosty, ponad 20 mm) i 2 trzonowce za duze na najwieksze gniazdo.
  Na porannej te 2 wejda w fi 15 - popiera zlecenie pkt 2.
- Na wieczornej te 2 nie wchodza nawet w fi 15 (jedna na granicy) i dalej zajma rynienke. Do rozwazenia: W-b z dwoma
  fi 18 z tylu zamiast trzech fi 15 (6 x fi 12, 9 x fi 15, 2 x fi 18 = 17 + rynienka; policzone, nie rysowane).
- Rynienki potrzebuje 6 z 17 prac, a po zmianie plytka przyjmie JEDNA taka prace (decyzja D3, pkt 4).

Ile gniazd przyjmie prace danej wielkosci (wieksze gniazdo tez sie nadaje):

| wieczorna | dzis | W-a | W-b | W-c | poranna | dzis | P-a | P-b | P-c |
|---|---|---|---|---|---|---|---|---|---|
| fi 12 i wieksze | 11 | 16 | 18 | 14 | fi 10 i wieksze | 13 | 23 | 22 | 16 |
| fi 15 | 5 | 16 | 12 | 8 | fi 12,5 i wieksze | 6 | 16 | 9 | 9 |
| | | | | | fi 15 | 0 | 5 | 3 | 3 |

## 3. Warianty: rzedy od przodu (y srodka rzedu; x srodkow gniazd)

- **W-a:** rynienka 60 x 15 (y -31) | fi 15 x 4 (y -13; x +-9, +-27) | fi 15 x 5 (y 2,6; x 0, +-18, +-36) | fi 15 x 4
  (y 18,2; x +-9, +-27) | fi 15 x 3 (y 33,8; x 0, +-18). Stozki A (-35; -27), B (-31; 31,5), C (42; 14,5).
- **W-b:** rynienka 60 x 15 (y -30,2) | fi 12 x 6 (y -13,7; x +-7,5, +-22,5, +-37,5) | fi 15 x 5 (y 2,75; x 0, +-18,
  +-36) | fi 15 x 4 (y 18,35; x +-9, +-27) | fi 15 x 3 (y 33,95; x 0, +-18). Stozki A (-35,5; -26,5) jak dzis,
  B (-31; 31,5), C (42; 14,5).
- **W-c:** cztery pierwsze rzedy jak dzis | w miejscu rynienki tylnej fi 15 x 3 (y 31,5; x 0, +-18). Stozki jak dzis.
- **P-a:** rynienka 50 x 13 (y -32,8) | fi 12,5 x 5 (y -17,05; x 0, +-15,5, +-31) | fi 12,5 x 6 (y -3,6; x +-7,75,
  +-23,25, +-38,75) | fi 15 x 5 (y 12,95; x 0, +-18, +-36) | fi 10 x 5 (y 28,45; x 0, +-13, +-26) | fi 10 x 2 (y 39,75;
  x +-6,5). Stozki A (-30,5; -32), B (-22; 38,5), C (22; 38,5).
- **P-b:** rynienka 50 x 13 (y -32,5) | fi 7,5 x 8 (y -19,25; x +-5,25 do +-36,75 co 10,5) | fi 12,5 x 6 (y -6,4;
  x jak w P-a) | fi 10 x 7 (y 7,85; x 0, +-13, +-26, +-39) | fi 10 x 6 (y 19,15; x +-6,5, +-19,5, +-32,5) | fi 15 x 3
  (y 34,6; x 0, +-18). Stozki A (-32,5; -30), B (-32,5; 30), C (32,5; 30).
- **P-c:** piec pierwszych rzedow jak dzis | fi 15 x 3 (y 27,7; x 0, +-18) | fi 7,5 x 2 (y 38,75; x +-9).
  Stozki A (-29,5; -33), B (-31; 31,5), C (38; 23).

Plytka okragla: w W-a, W-b, W-c i P-c dolki kodu i cyfra zostaja tam, gdzie dzis. W P-a i P-b dolki to rzad y -43,5,
x -4,5 / -1,5 / 1,5 / 4,5 (jak wieczorna); cyfra (31,5; -29,5) w P-a, (32; -28,5) w P-b.

Wynik `weryfikuj_uklad_R59.js` - wszystkie linie OK; wartosci najblizsze granicy:

| wariant | max promien / co | stozek - gniazdo (min 3) | boki trojkata stozkow | okragla: krawedz / sciecie / dolek - gniazdo |
|---|---|---|---|---|
| W-a | 45,81 rynienka | 3,12 | 58,6 / 75,0 / 87,5 | 4,03 / 4,03 / 4,00 |
| W-b | 45,93 fi 15 z tylu | 3,19 | 58,2 / 75,0 / 87,7 | 4,07 / 4,59 / 4,80 |
| W-c | 46,39 fi 12 | 3,01 | 53,0 / 71,0 / 88,6 | 3,61 / 3,67 / 3,50 |
| P-a | 45,76 fi 15 | 3,03 | 71,0 / 44,0 / 87,9 | 4,24 / 6,58 / 3,20 |
| P-b | 46,50 fi 15 z tylu | 3,35 | 60,0 / 65,0 / 88,5 | 3,50 / 6,01 / 3,50 |
| P-c | 46,32 fi 7,5 z przodu | 3,08 | 64,5 / 69,5 / 87,7 | 3,69 / 4,87 / 3,62 |

Scianka miedzy obrysami gniazd wynosi w kazdym wariancie dokladnie 3,000 (rzedy ulozone ciasno, tak jak dzis).

## 4. Dwa mosty w jednej rynience (decyzja D3)

- **D3-a, jedna dluga (60 x 15 / 50 x 13):** wchodzi kazda z 6 dlugich prac proby, ale tylko jedna na plytke.
- **D3-b, rynienka podzielona** (pliki `W-b-D3b`, `P-b-D3b`; reszta ukladu bez zmian): wieczorna 2 x 28,5 x 15 (srodki
  x +-15,75), poranna 2 x 23,5 x 13 (x +-13,25), miedzy nimi scianka 3. W kazdej 2 otwory fi 3 zamiast 4, rozstaw bez
  zmian (12 / 10). Dno ma 26,4 i 21,4 - wiecej niz prog mostu 20, w porannej ledwie. Na probie w krotka rynienke
  wchodza 3 z 6 dlugich prac; pozostale 3 (28,4 / 34,3 / 36,7 wieczorem, 23,3 / 28,1 / 30,1 rano) nie maja wtedy na
  plytce zadnego miejsca. Dluzsze krotkie rynienki (2 x 31 x 15, 2 x 27,5 x 13) mieszcza sie w kole i przyjmuja 4 z 6,
  ale trzeba przeniesc stozek A i dolki, a na okraglej porannej nie ma juz miejsca na cyfre. D3-b wymaga zmiany
  generatora (4 otwory sa zaszyte w sprawdzeniu K-08).
- **D3-c, dwie prace w dlugiej rynience:** wedlug dlugosci (szacunek, nie pomiar programem) mieszcza sie, gdy razem maja
  do ok. 57 (wieczorna) / 47 (poranna) - np. trzy najkrotsze dlugie prace proby parami. Wymaga zmiany programu (dzis
  jedno gniazdo = jedna praca), osobna paczka.
- **Zalecenie: D3-a.** D3-b odbiera miejsce polowie dlugich prac z proby. Gdy na plytce maja lezec 2 mosty - D3-c.

## 5. Skutki uboczne

- Stozki znacznikow: W-c bez zmian; W-b przenosi B i C; W-a, P-a, P-b, P-c przenosza wszystkie trzy. Dolki i cyfra
  plytki okraglej zmieniaja sie tylko w P-a i P-b. Dolki, cyfra i wyciecie D plytki kwadratowej zostaja zawsze.
- Numery gniazd (id) zmieniaja sie w kazdym wariancie; rynienka ma id 1 (w P-c id 4, jak dzis przednia).
- Nowa regula z planu (boki trojkata stozkow rozne o co najmniej 5): warianty ja spelniaja, P-b i P-c na granicy
  (5,00). Dzisiejsza poranna jej NIE spelnia (60,67 i 60,00), a program i tak przypisuje stozki pewnie: bledne
  przypisanie daloby reszte 20, przy dopuszczalnej 0,3. Weryfikator sprawdza oba warunki.
- Scianki nie maja zapasu (3,000), a w porannej rzad fi 12,5 x 6 siega granicy strefy +-45 (jak dzis) - kazda
  korekta tylko narzedziem, nigdy z reki.

## 6. Jak powtorzyc (PC, `<PC-katalog>\r59\uklad` = kopia `narzedzia`, `R59_szkice`, `parametry.json`)

```
node narzedzia\weryfikuj_uklad_R59.js R59_szkice\parametry_wariant_W-b.json     (kod wyjscia 0 = bez bledu)
node narzedzia\weryfikuj_uklad_R59.js parametry.json --r54                      (uklad dzisiejszy: 0 bledow)
node narzedzia\uklad_kolo_R59.js uloz R59_szkice\spec_W-b.json --wyjscie=R59_szkice\parametry_wariant_W-b.json
node R59_szkice\rysuj_szkice_R59.js parametry.json R59_szkice                   (SVG; PNG robi Chrome bez okna)
```

`parametry_wariant_<id>.json` = pelna kopia `parametry.json` ze zmienionymi tylko kluczami ukladu jednej plytki; druga
plytka zostaje w nim w stanie R54 i nie jest sprawdzana (wymusza to `--plytka=obie`). Docelowy `parametry.json` po G0
sprawdza sie tym samym poleceniem bez przelacznikow - wtedy obie plytki.

## 7. Odstepstwa i ograniczenia

- Weryfikator na dzisiejszym `parametry.json` bez przelacznika zglasza 3 bledy: 2 rynienki na kazdej plytce i regule
  bokow trojkata na porannej. Z `--r54` (stare reguly) zglasza 0 bledow i liczby zgodne z dokumentacja R54 / R57.
- Narzedzie przeglada uklady RZEDOWE (rzedy symetryczne, ciasno, takze w szachownice); to nie dowod, ze nie istnieje
  gestszy uklad nieregularny. Przeglad wieczornej jest pelny (do 6 rzedow). Przeglad porannej jest zawezony (do 7
  rzedow, najwyzej 2 rzedy fi 7,5, najmniejszy rozstaw); pelny nie skonczyl sie w 17 min. P-c nie pochodzi
  z przegladu - to dzisiejsze rzedy 1-5 i dwa dopisane.
- P-a i P-b wybrano z warunkiem "rynienka pierwsza, y nie mniej niz -33" (rzad dolkow okraglej przed rynienka). Bez
  niego P-a mialoby 24 gniazda (6 x fi 10, 13 x fi 12,5, 5 x fi 15), a dolki okraglej bylyby blokiem 2 x 2 z tylu.
- Przeliczenie 17 projektow dla nowych gniazd zrobil skrypt pomocniczy na PC, poza repozytorium
  (`<PC-katalog>\r59\uklad\pomiar\pomiar_gniazd_R59.py`); w wynikach sa tylko skroty projektow.
- Nie sprawdzono na siatkach STL (R59-A / R59-B) ani wplywu na wyniki programu (R59-P).
