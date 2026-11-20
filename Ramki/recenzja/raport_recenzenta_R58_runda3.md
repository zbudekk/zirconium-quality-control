# Raport recenzenta - R58 (komplet okragly do ramki), runda 3 (przyrostowa)

Data: 2026-11-19. Recenzowany stan: commit `d7bf1b2` wzgledem `ca6b446` (HEAD = `d7bf1b2`). Zakres: poprawki P1 i P2 rundy 2 (`ramka_wkladka_okragla_v2.stl`, `ramka_pokrywka_okragla_v2.stl`), regresja, spojnosc, kod, arkusz zamowienia `narzedzia/arkusz_zamowienia_R58.py`.
Metoda: wlasny kod (numpy, bez Blendera i bez funkcji generatora) w `recenzja/r58_runda3/` (narzedzia z rund 1-2 i nowe `r32_kolnierz.py`; logi `log_*.txt`). Pliki rundy 2 do porownania: `wyniki_v2/stl_r58_runda2/`.

## 0. Werdykt

- **(a) 6 plytek n1...n6 + 3 wkladki okragle (drukarnia PA12): do zamowienia.**
- **(b) Pokrywka okragla (druk wlasny PETG): do zamowienia** - najpierw 1 sztuka probna (jak w planie 4.2a i ryzyku 2).

Uwagi rundy 3: **B 0 / P 0 / D 4**. P1 i P2 rundy 2 zamkniete (sekcja 2).

## 1. Pomiary

### 1.1 Co sie zmienilo (SHA i siatki)

- `sha256_stl_po_R58.txt` (d7bf1b2) vs ta sama lista w `2be8676`: rowne 10 z 12 (8 plytek, 2 JSON), rozne tylko wkladka i pokrywka. SHA 12 plikow na dysku = lista = tabela R3-0, znak po znaku, kazda suma 64 znaki. Pliki w `stl_r58_runda2/` = tabela R2-0 (10/10). Stare 21 STL (glowne repo) + 4 JSON = `SHA256SUMS_2026-11-16_R59.txt` (25/25). `round_key_pin` - brak w generatorze, `parametry.json`, protokole; w planie tylko wiersz skreslony w 3.4.
- Wkladka (287e001f...) i pokrywka (f1a133cf...): szczelne, rozmaitosc 0 bledow, 1 skladowa, przeciec wlasnych 0, normalne zgodne, 0 liczb -0,0; objetosc 22,4462 / 25,0561 cm3 (= dokument 22,45 / 25,06). Najmniejszy trojkat wkladki 1,05e-6 mm2 (D3).

### 1.2 Wkladka (`r7_wkladka.py`)

- Roznice vs runda 2: z gory tylko u 48,22...49,71, |v| <= 1,48 (czapka zebra; Z r3 6,000...6,975 zamiast 6,015...7,000); od spodu 0 roznic -> kieszenie Halla, kanaly, otwor, wystep, polki bez zmian. Interfejs do blatu = `ramka_wkladka_v2.stl`: 0 roznic poza |x|, |y| > 51,35 (z gory i od spodu).
- Zebro ponizej Z 6: szer. 3,000, od u 46,500 (Z 5,5 / 5,95), do lica sciecia (bez zmian). Czapka Z 6...7: koniec zewnetrzny u 49,15 / 48,95 / 48,70 / 48,45 / 48,25 na Z 6,05 / 6,25 / 6,5 / 6,75 / 6,95 -> r1 49,2 i faza 45 st.; wierzch Z 7,000 na u 47,6...48,2, szer. wierzchu 1,0 (v +-0,5); za czapka (u 49,2...49,9) Z 6,000. Zgodne z R3-1 (`round_key_rib_top_r1` 49,2, wierzch 1,0 x 0,7).

### 1.3 Kolnierz pokrywki vs czapka zebra w ustawieniach skrajnych (`r32_kolnierz.py`, wlasna siatka)

- Polozenia plytki: obrot -0,8...+0,8 st. co 0,2 x przesuniecie co 0,02 w kole 0,46, warunki: obrys plytki (R 50,000, sciecie 49,356) w otworze (50,397 / 49,756) i rogi zebra w rowku (|v| <= 1,8, u >= 46,0) -> 4179 polozen; najwiekszy przesuw 0,397 (od zebra 0,396). Pokrywka wzgledem plytki: przesuniecie co 0,02 w kole 0,36, warunek lico r 50,3 obejmuje obrys plytki (z wariantem "garby nie siadaja na dnie rowka") -> najwiekszy przesuw 0,300. Razem 2 962 911 ustawien, wszystkie kierunki.
- Wynik: 0 ustawien z wierzcholkiem czapki (Z >= 6,5) w kolnierzu; najmniejszy luz w rzucie lico kolnierza - czapka 0,383 (plytka (-0,28; 0,28) + pokrywka (-0,18; 0,24), tj. od zebra); odleglosc 3D dolnej krawedzi lica (Z 6,5) od czapki w tym ustawieniu 0,626. Wykonawca: 0,375 / 0,620 (8 x 8 kierunkow, przesuwy 0,399 + 0,300 dokladnie wzdluz osi) - zgodnie.
- Proba 3D (`r31`, przeciecia krawedz-trojkat): nominal plytka-wkladka / plytka-pokrywka / wkladka-pokrywka 0 / 0 / 0; plytka 0,399 od zebra + pokrywka 0,30 lub 0,304 od zebra: wkladka-pokrywka 0 (runda 2: 5 / 6); przy 0,304 pokrywka-plytka 3 / 47 przeciec na koncach cieciwy (Z 6,5) - to jest granica fizyczna (styk lica z koncami cieciwy plytki), wiec przesuw pokrywki 0,300 jest najwiekszym osiagalnym; plytka 0,399 w strone zebra - 0; kontrola czulosci (plytka 0,05 w polce) 1147 / 1172.
- "min(0,4, swobodny przesuw)" wykonawcy nie zaniza najgorszego przypadku: swobodny przesuw plytki z siatek 0,397...0,400 (otwor wielobok 50,397) i pokrywki 0,300 (styk na koncach cieciwy) - wlasna siatka daje te same granice.

### 1.4 Ulozenia plaskie z nowa wkladka (`r30_ulozenia.py`, jak w rundzie 2)

- Wszystkie 8 plytek: plasko tylko -0,75...+0,75 st. (dolna granica +-0,50); naprowadzenie na fazie -1,75...+1,75 st. (uniesienie 3,59...4,22); w kazdym innym obrocie uniesienie >= 4,4 (max 4,50). n8 / n9 i plytki do gory dnem: zadnego kata plasko, uniesienie 4,50. Bez zmian wzgledem rundy 2 (przechyl wg wykonawcy 2,61 st.).

### 1.5 Pokrywka (`r13_pokrywka.py`, `r42`)

- Roznice vs runda 2 tylko na katach szczelin (16...18, 32...34, 146...148, 162...164, 196...198, 212...214, 326...328, 342...344 st.) w Z -7,9...-4,4 (przedluzenie szczeliny i otwor). Garby 0,700, spod wierzchu Z -2,000 bez zmian.
- 8 szczelin przelotowych na 17,58 / 32,43 / 147,57 / 162,43 / 197,58 / 212,43 / 327,58 / 342,43 st.: szer. 1,000 (Z -13 i -6,5), od dolnej krawedzi do otworu; otwor przelotowy o2,0 (szer. 2,000 na Z -5; pion przy v +-0,75: -4,35...-5,65 -> srodek Z -5,00, promien 1,0); gorny koniec Z -4,000, do spodu wierzchu 2,0; nad Z -3,9 sciana ciagla.
- Jezyk (rachunek belki, E 2000 MPa): szer. 12,0 (po licu), 1,5 gr., garb 13 od srodka otworu; w nasadzie (Z -5) szerokosc zwezona otworami do 13,04 - 2,0 = 11,0. Ugiecie 0,40 / 0,55 / 0,70 -> sila 3,7 / 5,1 / 6,5 N na garb; odksztalcenie nasady 0,53 / 0,73 / 0,93 % x 12/11 = 0,58 / 0,80 / 1,01 %; na krawedzi otworu (spietrzenie ok. 1,5...1,6 dla zaokraglonego konca) szczytowo ok. 0,9 / 1,2 / 1,6 %. Wzgledem rundy 2 (ostry koniec, 0,90 % nominalnie x Kt 2...3) wyraznie lepiej; najgorszy przypadek (pokrywka wciskana krzywo + zanizony otwor FDM) to wciaz ok. 32 MPa w poprzek warstw - stad sztuka probna (D1).
- Otwor przy garbie: garb (Z -18 +-0,4, luk +-5,7 st.) i otwor (Z -5 +-1, +-6,26...8,54 st. od srodka garbu) sa 12 mm od siebie w pionie - kat 0,57 st. miedzy nimi nie ma znaczenia; otwor nie oslabia kolnierza przy garbie, oslabia tylko nasade jezyka (wliczone wyzej). Pas sciany nad otworami Z -4...-2 (2,0 x 1,5) ciagly + wierzch 2,0.

### 1.6 Arkusz zamowienia (`python narzedzia/arkusz_zamowienia_R58.py <tmp> --raport wyniki_v2/raport/raport_wykonawcy_R58_SPRAWDZ_iter5.md`, katalog tymczasowy poza repo)

- Skrypt dziala, kontrole SHA "plik: zgodny" 8/8. Ilosci = `quantities_r58` (n1...n6 po 1, wkladka 3, pokrywka 4), materialy = `materials_r58`, objetosci 48,91 / 49,20 / 22,45 / 25,06 i SHA = pliki rundy 3.
- Sumy przeliczone: A 3 x 48,91 + 3 x 49,20 + 3 x 22,45 = 361,68 cm3 -> 326...579 zl (0,90 / 1,60); pozycje: plytka 44,02...78,26 / 44,28...78,72, wkladka 60,61...107,76; C (korpus W, P, 2 blaty) 612,00 cm3 -> 551...979 zl, pokazowy (x 1,20 x 1,30) 859...1528; razem A + C 973,68 cm3 -> 876...1558 zl, pokazowy 1185...2106 zl - zgodne.
- Tresc uwag zgodna z geometria rundy 3 (zebro 3,0 w rowku 3,6, rowek 3,6 x 5,0, plytka krzywo na zebrze +4,5, kanaly drozne, pokrywka 8 szczelin, sztuka probna); poza D2.

## 2. Uwagi rundy 3

- **D1** Plan 4.2a / `parametry.json` `round_cover_slit_h` podaja odksztalcenie nasady jezyka 0,53 / 0,93 % z mojego rachunku rundy 2 (szczelina 15 bez otworu). Otwor o2 zweza nasade do 11,0 (x 1,09) i ma spietrzenie ok. 1,5 - szczytowo ok. 0,9 % nominalnie / 1,6 % w najgorszym przypadku. Nie zmieniac geometrii; dopisac liczby i trzymac sie sztuki probnej (po kilkudziesieciu zalozeniach obejrzec okolice otworow pod katem pekniec).
- **D2** Arkusz zamowienia, akapit pod tabela D: "Plytki okragle n8 i n9 (bez magnesow) ... na ramce nie dzialaja (ramka odczyta 0 i 1)" - n8 i n9 nie maja kieszeni magnesow, ramka czyta 0 dla obu; do tego we wkladce okraglej leza na zebrze (uniesienie 4,5, moj przeglad 1.4), a do kwadratowej nie wchodza (o100 > 96,8). Poprawic na "ramka odczyta 0 (brak plytki); we wkladce okraglej leza krzywo na zebrze".
- **D3** Wkladka 287e001f: najmniejszy trojkat 1,05e-6 mm2 (o 5 % nad progiem K-03 1e-6; slad booleana EXACT przy czapce zebra, warianty bajtowe jak w R3-0). Na druk bez wplywu; pakowac tylko plik 287e001f (dokument to mowi).
- **D4** K-67 "kolnierz w ustawieniach skrajnych" (wykonawca): 8 x 8 kierunkow obejmuje najgorszy kierunek (os zebra), wynik = moja gesta siatka. Progi (3D >= 0,1, rzut > 0) sa slabe jako zapas na tolerancje druku: przy MJF +-0,15 na koncu czapki i FDM -0,15 na promieniu lica zostaje w rzucie ok. 0,08 (3D wiecej, bo czapka ma faze); prog np. "rzut >= 0,3" lepiej oddalby zamiar. Informacyjnie - geometria jest dobra.

Z rundy 2 przeniesione bez zmian (poza geometria, nie liczone jako nowe uwagi): D1 rundy 2 (pasek 0,5 x 0,156 na plytce - akceptowany), D2 rundy 2 (odczyt na zebrze - wymaganie dla paczki programu w R3-7), D5 rundy 2 (kalibracja programu ramki - paczka programu).

## 3. Status uwag rundy 2

| Uwaga | Status | Dowod |
|---|---|---|
| P1 kolnierz na czapce zebra | **zamknieta** | 1.3: 2 962 911 ustawien - 0 kolizji, luz w rzucie min 0,383, 3D 0,626; proba 3D w ustawieniu z rundy 2 (0,399 + 0,30 od zebra) 0 przeciec |
| P2 jezyk pokrywki | **zamknieta** | 1.5: szczeliny 1,0 x 15 + otwor o2,0, nominal ok. 0,6 % (szczyt ok. 0,9 %), najgorszy 1,0 % (szczyt ok. 1,6 %); sztuka probna - D1 |
| D1 pasek 0,5 x 0,156 | bez zmian, akceptowany | plytki bajtowo jak runda 2 |
| D2 odczyt w zlym obrocie | otwarta poza geometria | R3-7: wymaganie dla paczki programu (ostrzezenie przy numerze niepasujacym do roli ramki) |
| D3 pozostalosci w planie | **zamknieta** | wpis R58 bez `round_key_pin_*`; zostal tylko wiersz skreslony w 3.4; p. 30 / 31 odsylaja do R2 / R3 |
| D4 warianty wkladki | **zamknieta** | R3-0: 3 warianty, oddany 287e001f (9/17) = plik na dysku |
| D5 (D4, D5, D8 rundy 1) | czesciowo | D8: arkusz zamowienia sprawdzony (1.6) - poprawny poza D2; D4 i D5 rundy 1 bez zmian swiadomie |
| D6 metoda K-67 | zamknieta (informacyjnie) | 1.4: okno -0,75...+0,75 st. potwierdzone |

## 4. Kod (`git diff ca6b446 d7bf1b2 -- Ramki/ramka_generator.py`)

- `bryly_zebra_klucza`: czapka do `round_key_rib_top_r1` z faza na krawedzi zewnetrznej; walidacja `r0 + 2c < r1 <= lico` (blad, nie cicha zmiana). Czesc dolna bez zmian (pomiar 1.2 to potwierdza).
- `zbuduj_pokrywke_okragla`: szczelina do `-wys + slit_h`, otwor = walec wzdluz promienia; walidacja otwor >= szczelina, gorny koniec ponizej spodu wierzchu (2,0 zmierzone).
- K-65 (e): koniec czapki z 2 promieni poziomych (Z 6,25 / 6,75) i nachylenie fazy - mierzy to, co deklaruje (moje 48,95 / 48,45 = wykonawcy).
- K-66: szczeliny, otwor (srodek, o, gorny koniec, odstep do wierzchu), przeglad co 0,1 st. na Z -13 i -5 - zgodne z moimi pomiarami.
- K-67 `kolnierz_w_skrajnych`: przesuwy z siatek (promienie z wierzcholkow w kierunku d, ograniczone do luzu), 8 x 8 kierunkow x 8 plytek, kolizje K-53, odstep 3D (find_nearest w obie strony na probkach co 0,05), luz w rzucie, kolnierz-wkladka; kontrola czulosci: przesuw + 0,12 daje kolizje, geometria rundy 2 daje kolizje (11 par, -0,180). Uwagi do progow - D4.
- Stare etapy: zmiany tylko w funkcjach R58 i nowym argumencie `--r58-runda2`; wykonawca: `SPRAWDZ_iter17` = 58 ZAL / 5 N/D / 0 NIE (nie powtarzalem). Pliki R59 25/25 (moj pomiar).

## 5. Czego NIE sprawdzilem

- Przebiegow generatora (`R58_iter8`, `R58_SPRAWDZ_iter5`, `SPRAWDZ_iter17`, 17 budow wariantow) - nie uruchamialem Blendera; zgodnosc bajtowa wkladki i pokrywki z budowami tylko przez SHA z dokumentu.
- MES jezyka pokrywki i czapki zebra; wspolczynnik spietrzenia przy otworze przyjety z literatury (ok. 1,5), wytrzymalosc miedzywarstwowa PETG - szacunek.
- Tolerancji druku w pasowaniach (tylko oszacowanie w D4).
- Raportow wykonawcy rundy 3 poza tabelami w `R58_wdrozenie_zmiany.md` i rzutow PNG.
- Pliku CSV arkusza w programie arkuszowym (przeczytany jako tekst); dokumentow dla wlasciciela (`Zakupy i druk...`) - poza zakresem.