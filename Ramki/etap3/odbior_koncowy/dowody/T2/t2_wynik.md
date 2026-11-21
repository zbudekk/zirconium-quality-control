# T2 - Wieczor od poczatku do konca: tabela liczb kryterium (odbior 21.11.2026, paczka 0.3.1, commit 571e186)

Sterownik t2_wieczor.py przez <K>\Polecenie.cmd, pelny scenariusz (10 pozycji co 60 s), JEDEN przebieg 04:17:52 - 04:27:21,
kod wyjscia procesu 0, kod programu 0, Qt offscreen. Zrodlo liczb: t2_wynik.json / t2_wynik.txt.

| Czesc kryterium | Wartosc | Zrodlo (pole) | Werdykt |
|---|---|---|---|
| (a) 10 z 10 obsluzonych zgodnie z prawda | 10 z 10 | `obsluzone_zgodnie_z_prawda`, `plytki[]` | ZAL |
| (b) start analizy ponizej 1 s od zapisu | max 0,428 s; ponizej 1 s: 9 z 9; w kolejce czekalo 0 | `start_analizy_od_zapisu_s` | ZAL |
| (c) mapa do 40 s (mediana) | mediana 15,04 s; max 39,54 s; pierwsza plytka (pula zimna) 39,54 s (do 40 s: 1 z 1); kolejne max 24,39 s (do 40 s: 8 z 8) | `mapa_od_zapisu_s` | ZAL |
| (d) okno bez przerw ponad 200 ms | najdluzsza przerwa 34,7 ms; ponad 200 ms: 0 (28281 tykniec) | `petla_okna` | ZAL |
| (e) lista "do dofrezowania" = prawda | lista = prawda: NIE; oczekiwanych 26, w programie 25, brakuje 1, nadmiarowych 0 | `lista_do_dofrezowania` | FAIL |
| T2 LACZNIE | 4 z 5 ZAL, 1 FAIL, 0 NIE ZMIERZONO | `werdykty` | FAIL |

Wiersze osobne:

- zgodnosc obslugi: 10 z 10 (przyjety 6 z 6, plik_odrzucony 1 z 1, do_powtorzenia 1 z 1, niezgodny_uklad 1 z 1,
  plytka_nie_z_trybu 1 z 1);
- ubytki wg prawdy (prace z ubytkiem na 6 plytkach przyjetych): 26 -> czerwonych 10 / zoltych 15 / zielonych
  (przeoczonych) 1: pozycja 8, gniazdo 4, sha16 247ee785f428396f;
- lista = prawda: NIE;
- falszywe alarmy (prace cale na czerwono): 0 z 31; prace cale na zolto: 0 z 31;
- klikniecia: "Ukruszona" 25 z 26 zaplanowanych, "OK" 0 z 0; ponowienia klikniec (ochrona klikniec mapy): 0;
  czekan na zdjecie ochrony mapy: 5;
- kod wyjscia programu: 0 (0xC0000409 nie wystapil); zdarzenia srodowiska: 0; log programu: WARNING 4, ERROR 0;
- wolny RAM: 74626 MB na starcie, min. 71699 MB; co jeszcze liczylo na PC: nic (zadnego innego ciezkiego kroku ani
  obcego procesu python liczacego; szczegoly w WYNIK.md);
- odstepstwa pomiaru: O3, O4, O13 (RAPORT.md sekcja 4 / 4a).
