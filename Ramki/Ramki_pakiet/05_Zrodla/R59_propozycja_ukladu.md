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
Od wersji po recenzji PR (runda 1, uwaga 5) reguly domyslne wymagaja dokladnie 1 rynienki na plytke (G0: D3 = a), wiec
pliki wariantow D3-b (`W-b-D3b`, `P-b-D3b`) sprawdza sie z przelacznikiem `--d3b`; bez niego rynienka podzielona to BLAD.

## 7. Odstepstwa i ograniczenia

- Weryfikator na dzisiejszym `parametry.json` bez przelacznika zglasza 3 bledy: 2 rynienki na kazdej plytce i regule
  bokow trojkata na porannej. Z `--r54` (stare reguly) zglasza 0 bledow i liczby zgodne z dokumentacja R54 / R57.
- Od wersji po recenzji PR warianty D3-b wymagaja `--d3b` (wczesniej przechodzily bez przelacznika, choc na G0 przyjeto
  D3-a); sama geometria i pliki wariantow D3-b sie nie zmienily.
- Narzedzie przeglada uklady RZEDOWE (rzedy symetryczne, ciasno, takze w szachownice); to nie dowod, ze nie istnieje
  gestszy uklad nieregularny. Przeglad wieczornej jest pelny (do 6 rzedow). Przeglad porannej jest zawezony (do 7
  rzedow, najwyzej 2 rzedy fi 7,5, najmniejszy rozstaw); pelny nie skonczyl sie w 17 min. P-c nie pochodzi
  z przegladu - to dzisiejsze rzedy 1-5 i dwa dopisane.
- P-a i P-b wybrano z warunkiem "rynienka pierwsza, y nie mniej niz -33" (rzad dolkow okraglej przed rynienka). Bez
  niego P-a mialoby 24 gniazda (6 x fi 10, 13 x fi 12,5, 5 x fi 15), a dolki okraglej bylyby blokiem 2 x 2 z tylu.
- Przeliczenie 17 projektow dla nowych gniazd zrobil skrypt pomocniczy na PC, poza repozytorium
  (`<PC-katalog>\r59\uklad\pomiar\pomiar_gniazd_R59.py`); w wynikach sa tylko skroty projektow.
- Nie sprawdzono na siatkach STL (R59-A / R59-B) ani wplywu na wyniki programu (R59-P).

## 8. Wariant P-d (zmiana wlasciciela na G0)

Wlasciciel wybral W-b i D3-a, a w porannej P-b ze zmiana: rzad fi 7,5 -> rzad fi 10, jeden rzad fi 10 -> drugi rzad
fi 12,5. Zestaw rzedow: rynienka 50 x 13 + fi 10 + fi 10 + fi 12,5 + fi 12,5 + fi 15, bez fi 7,5; rynienka pierwsza,
jak w P-b. Narzedzie przejrzalo wszystkie kolejnosci tych rzedow (`front --plytka=poranna --srednice=10,12.5,15
--dokladnie=10:2,12.5:2,15:1 --t-pierwsza --t-ymin=-33 --rozstawy=wszystkie --krok=0.05`; przeglad pelny, 2 s).
**Zestaw sie miesci.** Najwiecej wychodzi 26 gniazd, ale wtedy z tylu sa 2 gniazda fi 15 (w P-b byly 3); z trzema
fi 15 najwiecej jest 25.

| | fi 7,5 | fi 10 | fi 12,5 | fi 15 | razem | max promien (47) | min scianka | stozek - gniazdo | boki trojkata stozkow | okragla: krawedz / sciecie / dolek - gniazdo |
|---|---|---|---|---|---|---|---|---|---|---|
| dzis (R54) | 18 | 7 | 6 | 0 | 31 + 2 | 46,93 | 3,00 | 3,01 | 60,7 / 60,0 / 88,4 | 3,07 / 4,87 / 3,62 |
| P-b | 8 | 13 | 6 | 3 | 30 + 1 | 46,50 | 3,00 | 3,35 | 60,0 / 65,0 / 88,5 | 3,50 / 6,01 / 3,50 |
| **P-d** najwiecej gniazd | 0 | 13 | 11 | 2 | 26 + 1 | 45,73 | 3,00 | 3,01 | 65,0 / 59,0 / 88,5 | 4,27 / 6,79 / 3,50 |
| P-d1 jak P-d, ale 3 x fi 15 | 0 | 13 | 9 | 3 | 25 + 1 | 46,28 | 3,00 | 3,01 | 63,5 / 72,0 / 87,3 | 3,72 / 6,79 / 3,50 |
| P-d2 jak P-d, ale 5 x fi 15 | 0 | 13 | 7 | 5 | 25 + 1 | 46,41 | 3,00 | 3,00 | 67,1 / 55,5 / 88,8 | 3,59 / 6,79 / 3,50 |

| ile gniazd przyjmie prace | dzis | P-b | P-d | P-d1 | P-d2 |
|---|---|---|---|---|---|
| fi 10 i wieksze | 13 | 22 | 26 | 25 | 25 |
| fi 12,5 i wieksze | 6 | 9 | 13 | 12 | 12 |
| fi 15 | 0 | 3 | 2 | 3 | 5 |

Wspolne dla P-d, P-d1, P-d2: rynienka 50 x 13 (y -32,5) | fi 10 x 6 (y -18; x +-6,5, +-19,5, +-32,5) | fi 10 x 7
(y -6,7; x 0, +-13, +-26, +-39); plytka okragla: dolki rzad y -43,5, x -4,5 / -1,5 / 1,5 / 4,5, cyfra (32; -29). Dalej:
- **P-d:** fi 12,5 x 6 (y 7,55; x +-7,75, +-23,25, +-38,75) | fi 12,5 x 5 (y 21; x 0, +-15,5, +-31) | fi 15 x 2
  (y 36,45; x +-9). Stozki A (-30,5; -32), B (-29,5; 33), C (29,5; 33).
- **P-d1:** fi 12,5 x 5 (y 7,55; x 0, +-18, +-36) | fi 12,5 x 4 (y 20,2; x +-9, +-27) | fi 15 x 3 (y 34,35; x 0, +-18).
  Stozki A (-30,5; -32), B (-31; 31,5), C (40; 19,5).
- **P-d2:** fi 15 x 5 (y 8,8; x 0, +-18, +-36) | fi 12,5 x 4 (y 22,95; x +-9, +-27) | fi 12,5 x 3 (y 37,05; x 0, +-15,5).
  Stozki A (-30,5; -32,25), B (-27,75; 34,75), C (27,75; 34,75).

`weryfikuj_uklad_R59.js`: 3 z 3 plikow bez bledu (kod wyjscia 0). Inne kolejnosci: 26 gniazd daje tez uklad z rzedami
fi 12,5 z przodu i fi 10 za nimi (te same liczby) - wybrano kolejnosc od najmniejszych z przodu, z fi 15 z tylu jak
w P-b; istnieje tez 13 x fi 10, 8 x fi 12,5, 4 x fi 15 = 25 (nie rysowane).

**Zalecenie: P-d** - spelnia zmiane doslownie, ma najwiecej gniazd (26) i najwiecej fi 12,5 (11). Jedyna strata wobec
P-b: fi 15 jest 2 zamiast 3 (w probie fi 15 potrzebuja rano 2 z 17 prac). Gdy maja zostac 3 x fi 15 - P-d1; gdy fi 15
ma byc wiecej - P-d2. Skutki jak w P-b: wszystkie trzy stozki, dolki i cyfra plytki okraglej zmieniaja miejsce. W P-d
rzad fi 12,5 x 6 siega granicy strefy +-45 (jak dzis i w P-b); w P-d1 i P-d2 nie (44,00).
Szkice: `szkic_P-d.png`, `szkic_P-d1.png`, `szkic_P-d2.png`, zbiorczy `szkic_przeglad_poranna_G0.png`.

## 9. Rodzina P-e (szkic wlasciciela: fi 12,5 i fi 15)

Szkic wlasciciela, rzedy od przodu: rynienka 50 x 13 | fi 12,5, fi 12,5, fi 15, fi 12,5, fi 12,5 | fi 12,5 x 6 |
fi 12,5 x 6 | fi 12,5 x 5 | fi 15 x 2 = 21 x fi 12,5 + 3 x fi 15 = 24 gniazda.
**Werdykt: doslownie NIE - brakuje 2,7 mm wysokosci** (`uloz spec_P-e-szkic.json --diagnoza`: 2,68). Z przodu rynienka
nie moze lezec nizej niz y -36,03 (kolo skanowania), a zeby para fi 15 z tylu zmiescila sie w strefie +-45, musialaby
lezec w y -38,71. Cala strata to fi 15 nad rynienka: rzad za nia lezy 31,85 zamiast 29,17 od rynienki; bez niej uklad
bylby dokladnie na styk (brak 0,006 mm). **Blisko - TAK.**

Rodzina P-e = tylko fi 12,5 i fi 15, jedna rynienka jako pierwszy rzad. Narzedzie dostalo rzedy mieszane (fi 15 w rzedzie
fi 12,5; w pliku to osobne wpisy rzedu o innym y, weryfikator bez zmian). Najwiecej gniazd dla danej liczby fi 15:

| fi 15 | rynienka dosunieta do przodu (y do -36): fi 12,5 / razem / max promien | rynienka y >= -33 (dolki okraglej przed nia): fi 12,5 / razem / max promien |
|---|---|---|
| 0 | 25 / **25** / 46,98 (P-e0) | 24 / **24** / 46,76 (P-e0-33) |
| 1 | 23 / 24 / 46,35 | 21 / 22 / 46,30 |
| 2 | 21 / 23 / 46,35 | 20 / 22 / 45,62 |
| 3 | 20 / **23** / 46,41 (P-e) | 18 / **21** / 46,81 (P-e-33) |
| 4 | 19 / 23 / 46,98 | 18 / 22 / 45,62 |
| 5 | 17 / 22 / 46,57 | 16 / 21 / 46,81 |

Pliki i szkice (wszystkie: weryfikator kod 0, scianka min 3,000):

| wariant | fi 12,5 | fi 15 | razem | rynienka y | max promien (47) | stozek - gniazdo | boki trojkata | okragla: krawedz / sciecie / dolek - gniazdo |
|---|---|---|---|---|---|---|---|---|
| P-d (dla porownania: + 13 x fi 10) | 11 | 2 | 26 + 1 | -32,5 | 45,73 | 3,01 | 65,0 / 59,0 / 88,5 | 4,27 / 6,79 / 3,50 |
| **P-e** najblizej szkicu, 3 x fi 15 | 20 | 3 | 23 + 1 | -35,3 | 46,41 | 3,02 | 55,9 / 79,4 / 86,5 | 3,59 / 4,81 / 3,55 |
| P-e1 para fi 15 z tylu (wyglad szkicu) | 19 | 3 | 22 + 1 | -35,7 | 46,71 | 3,03 | 65,0 / 59,0 / 88,1 | 3,29 / 4,53 / 4,05 |
| P-e-33 3 x fi 15 z tylu | 18 | 3 | 21 + 1 | -32,9 | 46,81 | 3,03 | 53,7 / 79,0 / 87,3 | 3,19 / 5,52 / 3,10 |
| **P-e0** same fi 12,5 | 25 | 0 | 25 + 1 | -36 | 46,98 | 3,02 | 66,5 / 57,0 / 88,6 | 3,02 / 4,32 / 3,67 |
| P-e0-33 same fi 12,5 | 24 | 0 | 24 + 1 | -32,9 | 46,76 | 3,03 | 68,1 / 52,0 / 88,4 | 3,24 / 6,51 / 3,10 |

Rzedy (y; x) i plytka okragla:
- **P-e:** rynienka y -35,3 | fi 12,5 x 5 (-19,55; 0, +-15,5, +-31) | fi 12,5 x 6 (-6,1; +-7,75, +-23,25, +-38,75) | rzad
  mieszany: fi 12,5 x 4 (8; +-16,75, +-32,25) i fi 15 (8,75; 0) | rzad mieszany: fi 15 x 2 (22,85; +-24,5) i fi 12,5 x 2
  (23,6; +-7,75) | fi 12,5 x 3 (37,05; 0, +-15,5). Stozki A (-30,5; -32), B (-37,5; 23,5), C (41,5; 16). Okragla: dolki
  w dwoch parach z prawej (36,5; 18,5), (36,5; 21,5), (43; 6), (43; 9), cyfra (-44; 5,5).
- **P-e1:** rynienka y -35,7 | fi 12,5 x 4 (-19,95; +-7,75, +-23,25) | x 5 (-6,5) | x 6 (6,95) | rzad mieszany: fi 12,5 x 4
  (21,05; +-16,75, +-32,25) i fi 15 (21,8; 0) | fi 15 x 2 (37,4; +-9). Stozki A (-30,5; -32), B (-29,5; 33), C (29,5; 32,5).
  Okragla: dolki kolumna x 34,5, y -27 / -24 / -21 / -18 (prawie jak dzis), cyfra (41; -15).
- **P-e-33:** rynienka y -32,9 | fi 12,5 x 5 (-17,15; 0, +-18, +-36) | x 4 (-4,5; +-9, +-27) | x 5 (8,15) | x 4 (20,8) |
  fi 15 x 3 (34,95; 0, +-18). Stozki A (-30,5; -32), B (-39; 21), C (40; 19,5). Okragla: dolki rzad y -43,5, cyfra (31,5; -29,5).
- **P-e0:** rynienka y -36 | fi 12,5 x 5 (-20,25) | x 6 (-6,8) | x 6 (8,7) | x 5 (22,15) | x 3 (37,65; 0, +-15,5). Stozki
  A (-30; -32,5), B (-28,5; 34), C (28,5; 34). Okragla: dolki w przerwach miedzy rzedami x 6: y 1, x -15,5 / 0 / 15,5 / 31
  (rzad co 15,5 - innego miejsca nie ma), cyfra (30; -32).
- **P-e0-33:** rynienka y -32,9 | fi 12,5 x 5 (-17,15) | x 6 (-3,7) | x 6 (11,8) | x 5 (25,25) | x 2 (38,7; +-7,75). Stozki
  A (-30,5; -32), B (-26; 36), C (26; 36). Okragla: dolki rzad y -43,5, cyfra (31,5; -29,5).

Ile gniazd przyjmie prace (P-d / P-e / P-e1 / P-e-33 / P-e0 / P-e0-33): fi 10 i wieksze 26 / 23 / 22 / 21 / 25 / 24;
fi 12,5 i wieksze 13 / 23 / 22 / 21 / 25 / 24; fi 15: 2 / 3 / 3 / 3 / 0 / 0.

**Zalecenie:** jesli ma byc "jak na szkicu" - **P-e** (23 gniazda, 3 x fi 15; jedno fi 12,5 mniej niz na szkicu), a gdy
wazniejszy jest wyglad szkicu (para fi 15 na samym tyle) - P-e1 (22). Cena obu: rynienka dosunieta do przodu, wiec na
plytce OKRAGLEJ dolki kodu nie mieszcza sie przed rynienka (miejsca wyzej); na kwadratowej nic sie nie zmienia. Gdy dolki
okraglej maja zostac przed rynienka jak w P-b / P-d - P-e-33 (21). P-e0 (25) ma najwiecej gniazd, ale ani jednego fi 15
(2 z 17 prac proby wracaja wtedy do rynienki) i zapas do kola skanowania tylko 0,02 mm z przodu i z tylu - nie zalecam.
Wobec P-d rodzina P-e ma o 1-5 gniazd mniej, za to wszystkie od fi 12,5 w gore.
Ograniczenia: przeglad z rynienka jako pierwszym rzedem jest pelny (10-15 s); uklady z rzedem gniazd przed rynienka
przejrzane tylko czesciowo (limit 180 s, 1441 z 4173 startow) - nie daly nic lepszego. Rzedy mieszane: wszystkie
symetryczne wzory 3-5 gniazd z fi 12,5 i fi 15 w najciasniejszym rozstawie (10 wzorow).
Szkice: `szkic_P-e*.png`, zbiorczy `szkic_przeglad_poranna_G0b.png` (P-d | P-e | P-e1 | P-e-33 | P-e0 | P-e0-33).
