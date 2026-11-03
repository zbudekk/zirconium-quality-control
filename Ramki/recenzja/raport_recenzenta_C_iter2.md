# Raport recenzenta — etap C, iteracja 2 (po R52: tulejka DC ø11,85)

Plik: `recenzja/raport_recenzenta_C_iter2.md`. Data: 2026‑10‑27. Blender 5.2.3 LTS, tryb `-b`.
Raport wykonawcy: `wyniki_v2/raport/raport_wykonawcy_C_iter2.md` (przebieg 2026‑10‑27 00:12, 33 s, B=0 P=0 D=0).

## 0. Werdykt

**ZALICZONY** — B = 0, P = 0, D = 0 (liczba sprawdzeń z wynikiem NIE w każdej wadze).

Zakres C2 wg polecenia nadzoru: (a) SHA 16 STL vs C1, (b) tulejka K‑01…K‑04b, K‑52b na 11,85, K‑53 z tulejką, (c) K‑57, K‑60 (arkusze/README/SHA). Pełnego zestawu nie powtarzano — 15 STL identyczne bajtowo z C1, wkładka identyczna kanonicznie (K‑59); dodatkowo powtórzono cały skrypt etapu B (73 sprawdzenia, 572 sondy) — bez zmian.

## 1. Metoda

Skrypty własne (bez czytania `ramka_generator.py`):
- `recenzja/sprawdz_C2_sha.py` — SHA‑256 wszystkich 29 plików z tabeli §2 raportu C2 vs dysk; SHA STL vs tabela §2 raportu C1; porównanie kanoniczne (posortowane trójkąty, wierzchołki zaokrąglone do 1e‑5) z czystą kopią C1 (`recenzja/powtorka/wyniki_v2`, identyczna kanonicznie z C1 — K‑59 w C1). Wynik: `recenzja/wyniki_C_iter2_sha.json`, log `log_C_iter2_sha.txt`.
- `recenzja/sprawdz_C.py --iter 2` (poprzednia wersja zachowana jako `sprawdz_C_iter1.py`): K‑01…K‑04b i K‑52b tulejki z oczekiwanym walcem ø11,85 ± 0,05 (promienie X i Y) oraz 4 dodatkowymi sondami przy promieniu 5,925 (r 5,85 W / r 6,0 POZA, w X i Y); K‑52c podkładek; INFO‑sha; K‑57; K‑60. Wynik: `wyniki_C_iter2.json`, log `log_C_iter2.txt`.
- `recenzja/sprawdz_B.py --iter C2` — cały etap B łącznie z `.blend` (K‑53 z tulejką, K‑54, K‑33, K‑44b, K‑55, K‑56, K‑49). Wynik: `wyniki_B_iterC2.json`, log `log_B_iterC2.txt`.
- `recenzja/sprawdz_C2_tulejka_blend.py` — położenie tulejki w `.blend`: oś, promienie wierzchołków, luz promieniowy walec→korpus (`find_nearest`), średnica otworu korpusu z 72 promieni, styk kołnierza z korpusem i gniazdem. Wynik: `wyniki_C_iter2_tulejka_blend.json`, log `log_C_iter2_tulejka_blend.txt`.

Sondy: parzystość przecięć w 3 skośnych kierunkach, głosowanie, przy braku jednomyślności przesunięcie 0,1 mm wzdłuż normalnej. Łącznie 100 sprawdzeń (27 + 73), 609 sond, 0 niestabilnych, 0 NIE.

## 2. (a) SHA i powtarzalność (K‑59)

| Plik | SHA raport C2 = dysk | vs C1 |
|---|---|---|
| 15 STL: płytki ×8, pokrywka, blat, korpus W, korpus P, podkładki ×3 | tak (29/29 plików) | SHA identyczne |
| `ramka_wkladka_v2.stl` | tak | SHA inne; trójkąty identyczne (1806/1806, 0 różnych), objętość 12,4057 = 12,4057 — kryterium K‑59 kanoniczne (decyzja nadzoru po C1) |
| `ramka_tulejka_dc_v2.stl` | tak | zmieniona zgodnie z R52: 1770 trójkątów (C1: 1776), objętość 0,2389 cm³ (C1: 0,2445) |
| `json/*.json`, `arkusze/arkusz_zamowienia.csv/.md`, `kody_plytek.md`, `do_v3.md` | tak | SHA identyczne |
| `README.md`, `arkusze/arkusz_wymiarow.md`, `ramka_v2.blend`, 3 rendery | tak | zmienione (tabela SHA tulejki, opis ø11,85, zrzut parametrów, nowa tulejka w złożeniu) |

Rozmiary plików z tabeli §2 = dysk (29/29). Zestaw 10 STL do drukarni (blok A arkusza) bajt w bajt taki sam jak zatwierdzony w C1.

## 3. (b) Tulejka DC

| Id | Wynik | Pomiar |
|---|---|---|
| K‑01 | ZAL | 1770 trójkątów, bez NaN |
| K‑02 | ZAL | 14,999 × 14,999 × 3,000 (15 × 15 × 3 ± 0,1) |
| K‑03 | ZAL | 0 krawędzi niemanifold, 0 luźnych wierzchołków, 0 samoprzecięć |
| K‑04 | ZAL | 1 składowa |
| K‑04b | ZAL | 0,239 cm³ (wzór: π·5,925²·2 + π·7,5²·1 − π·4,1²·3 = 0,239) |
| K‑52b | ZAL | 16/16 sond (7 protokołu + 9 dodatkowych, w tym r 5,85 W / r 6,0 POZA w X i Y); z promieni: otwór ø8,200, walec ø11,849 (X) / ø11,848 (Y), kołnierz ø14,999 |
| K‑52c | ZAL | 3 podkładki bez zmian: 7/7 sond każda, 9,000 × 8,997 × t, otwór ø3,395 |

Złożenie w `.blend` (`sprawdz_C2_tulejka_blend.py`):
- oś tulejki X; walec x −42,0…−40,0 (ściana kieszeni DC grubości 2,0: lico wewnętrzne x −42, zewnętrzne x −40), kołnierz x −43,0…−42,0 po stronie kieszeni — zgodnie z opisem w `arkusz_wymiarow.md` §216;
- otwór w ścianie: ø11,998 (72 promienie; r 5,998…6,000);
- luz promieniowy walec→korpus: 0,0737…0,0750 (oczekiwane 0,075 = (12 − 11,85)/2) — walec nie przenika ściany, wcisk 0,15 jest zamierzeniem na druk (reguła 4.8), nie w geometrii;
- kołnierz→korpus 0,000 (styk z licem), tulejka→gniazdo DC 0,000 (styk) — bez przenikania.

K‑53 (`.blend`, 24 obiekty zestawu W, skurcz −0,05 mm): 43 pary z nakładającym się bbox, **0 par z przecięciem**. Kontrola czułości bez skurczu potwierdza styki (blat–korpus 469, wkładka–dyfuzor 180, płytka–wkładka 314 …). Pozostałe sprawdzenia `.blend` bez zmian wobec C1: K‑54 (26 wartości ± 0,05), K‑33, K‑44b (3 kierunki wtyku 0 przecięć), K‑55 (1,200), K‑56 (27,700 / 11 px), K‑49 (luzy 0,5 / 1,0 / 4,0 / 1,0).

## 4. (c) Arkusze, README, raport

| Id | Wynik | Pomiar |
|---|---|---|
| K‑57 | ZAL | arkusz 15 wierszy (10 drukarnia + 5 druk własny); objętości vs moje pomiary max |Δ| 0,0045 cm³ (tulejka 0,24 — bez zmiany po zaokrągleniu), gabaryt |Δ| 0,003; ilości i materiały = `parametry.json`; sumy drukarni 1004,20 cm³, 904–1607 / 1212–2155 zł zgodne z .md; uwaga STEP/FreeCAD jest |
| K‑60 | ZAL | 3 rendery 1600 × 1200; raport C2: 56 K‑xx etapów A+B+C; zrzut `parametry.json` w `arkusz_wymiarow.md` zgodny (273 klucze, `dc_bush_outer_d` 11,85); LICZONE 9/9; README z poleceniem `cd …`, tabela SHA = dysk (tulejka `b393256c…`) |
| INFO‑sha | ZAL | STL zmierzone w C1 (A/B) = obecne; wkładka: inne bajty, identyczne trójkąty |

Raport wykonawcy C2 §3: K‑52b podaje walec ø11,848 — zgodne z moim 11,849/11,848. Rejestr odstępstw #1–#9: #1 (11,85 zamiast 12 z tabeli 3) jest wprost treścią R52; #9 (opis K‑52b i planu z ø12) — tekstowe, patrz §6.

## 5. Rendery (ocena wizualna)

Nie oglądano ponownie — rendery zmienione tylko przez nową tulejkę (ø11,85 vs 12 nierozróżnialne w skali renderu); podpisy 12/12 potwierdzone w C1, K‑60 wymiary 1600 × 1200 zmierzone z IHDR.

## 6. Uwagi D (nieblokujące, do v3 / poprawy tekstu)

1. `protokol_weryfikacji_v2.md` K‑52b nadal opisuje „walec ø12 × 2” i sondę „(5,5, 0, 2) W (walec r 6)”; plan 4.x opisuje plik tulejki jako „walec ø`dc_bush_outer_d` 12”. Po R52 powinno być ø11,85 (r 5,925). Sondy protokołu pozostają poprawne (r 5,5 W, r 6,8 POZA), ale nie rozróżniają 12 od 11,85 — proponuję dodać do protokołu sondy r 5,85 W / r 6,0 POZA (użyte w tej recenzji). Zgłoszone też przez wykonawcę (rejestr #9).
2. Bez zmian z C1: D z `do_v3.md` #1–#10 (m.in. bajtowa powtarzalność wkładki #9).

## 7. Pliki recenzji

`recenzja/sprawdz_C2_sha.py`, `sprawdz_C.py` (iter 2), `sprawdz_C_iter1.py`, `sprawdz_B.py`, `sprawdz_C2_tulejka_blend.py`; wyniki `wyniki_C_iter2_sha.json`, `wyniki_C_iter2.json`, `wyniki_B_iterC2.json`, `wyniki_C_iter2_tulejka_blend.json`; logi `log_C_iter2_sha.txt`, `log_C_iter2.txt`, `log_B_iterC2.txt`, `log_C_iter2_tulejka_blend.txt`.
