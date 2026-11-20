# Raport recenzenta - R58 (komplet okragly do ramki), runda 2

Data: 2026-11-19. Recenzowany stan: commit `ca6b446` wzgledem `f429605` (galaz `r58/plytki-okragle-ramka`; w trakcie recenzji HEAD przesunal sie na `f3f62b0`, ktory zmienia tylko `narzedzia/arkusz_zamowienia_R58.py` - poza zakresem). Pliki: 10 STL rundy 2 w `Ramki/wyniki_v2/stl/` (poza gitem), pliki rundy 1 w `wyniki_v2/stl_r58_runda1/` (porownanie), 2 JSON ukladow, `parametry.json`, plan, protokol, `R58_wdrozenie_zmiany.md` (R2-0...R2-9), `raport_wykonawcy_R58_SPRAWDZ_iter4.md`.
Metoda: wlasny kod (numpy, bez Blendera i bez funkcji generatora) w `recenzja/r58_runda2/` (kopie narzedzi rundy 1: `siatka.py`, `rastr.py`, `kolizje.py`; nowe `r2`, `r5`, `r7`, `r13`, `r16`, `r30`, `r31`, `r40`-`r42`; logi `log_*.txt`). Wszystko na MSI.

## 0. Werdykt

- **Czesci z drukarni (6 plytek n1...n6 + 3 wkladki): do zamowienia po poprawkach** - 6 plytek jest gotowych bez zmian, a wkladke trzeba poprawic jedna zmiana zebra klucza (P1: przy skrajnym, osiagalnym ustawieniu plytki i pokrywki dolna krawedz kolnierza pokrywki siada na wierzchu zebra, wnikanie 0,16 mm).
- **Pokrywka okragla (druk wlasny PETG): do zamowienia** - wydrukowac najpierw 1 sztuke probna; zalecane wydluzenie szczelin i zaokraglenie ich koncow (P2).

Uwagi rundy 2: **B 0 / P 2 / D 6**. B1 rundy 1 zamkniete - niezaleznie potwierdzone (sekcja 1.1). Wszystko, co w rundzie 1 bylo zgodne, nadal jest zgodne (sekcja 2).

## 1. Najwazniejsze pomiary rundy 2

### 1.1 B1 - ulozenia plaskie plytki we wkladce (wlasna metoda, `r30_ulozenia.py`, log `log_r30.txt`)

- Metoda: przeszkody wkladki = wezly mapy wierzchu (krok 0,1) z Z > polka + 0,01 wewnatrz otworu: 967 wezlow, wylacznie zebro (h 3,52...4,50 nad polka, u 46,53...49,64). Sciana otworu i sciecie - analitycznie z wymiarow zmierzonych (plytka R 50,000, sciecie 49,356; otwor 50,397, sciecie 49,756). Mapa wnek spodu plytki krok 0,05 (0 = pelny spod, 2,2 kieszen, 5,0 rowek klucza). Obrot 0...360 st. co 0,25 st. x przesuniecie w kole 0,45 co 0,1; wneki poszerzone o 1 wezel (gorna granica okna) i zwezone o 1 wezel (dolna granica). Puste kieszenie NIE zaklejone.
- Mapy wnek wszystkich 8 plytek w pierscieniu r > 44 sa identyczne (0 roznych wezlow) - wynik dotyczy kazdej z 8 plytek; liczylem mimo to kazda osobno.
- Wynik (8 z 8 plytek): plytka lezy plasko **tylko** dla obrotu -0,75...+0,75 st. (granica dolna -0,50...+0,50); w -1,75...+1,75 st. krawedz rowka lezy na fazie zebra (uniesienie 3,59...4,29 - faza 45 st. sprowadza plytke do rowka); w kazdym innym obrocie uniesienie 4,4...4,5 (plytka lezy na wierzchu zebra). Zadnego innego kata bez kolizji, zadnych katow 90/180/270. = twierdzenie wykonawcy (R2-4: -0,75...+0,75, naprowadzenie +-1,75).
- Zebro nie moze wejsc w nic poza rowkiem klucza: jest wyzsze (4,5) niz kieszen magnesu (2,2) i siega dalej (u 49,756) niz kieszen (r 47,6); rowek pokrywki jest na Z 8,0...9,0 (uklad wkladki), a wierzch zebra na 7,0.
- Zly obrot: przechyl ok. 2,6 st., krawedz plytki +4,5 mm (oparcie na zewnetrznym koncu wierzchu zebra u 49,74 i na wystepie po przeciwnej stronie; dzwignia ok. 99,4); plytka nie moze zsunac sie z zebra (zeby je ominac musialaby przesunac sie o ok. 3,5 przy luzie 0,4), zaklinowania nie ma. Czujniki A i C uniesione ok. 2,25 (magnes-czujnik ok. 3,95 mm - na granicy progu D5), B ok. 0,2 (patrz D2).
- Do gory dnem (n1, n4): w zadnym obrocie nie lezy plasko, uniesienie 4,5 (wierzch plytki w pasie r 46,5...49,7 jest pelny) - lezy na zebrze; magnesy po drugiej stronie plytki (ok. 7 mm + przechyl od czujnika) - ramka czyta 0 (rachunek).
- Stare n8 / n9: w zadnym obrocie nie leza plasko (uniesienie 4,5) - leza na zebrze, ramka czyta 0. Plytka kwadratowa: nie wchodzi w otwor w zadnym obrocie (rachunek jak w rundzie 1), odczyt 0.
- Luz zebro-rowek z siatek: boki 0,30 / 0,30 (rowek 3,600, zebro 3,000), czolo 0,50 (46,0 / 46,5), nad zebrem 0,50 (sufit Z 7,5 / wierzch 7,0); przy przesunieciu plytki o 0,4 w strone zebra czolo 0,1 - kolizja 3D 0 (`r31`).
- Wytrzymalosc zebra: ponizej Z 6 zebro jest zrosniete ze sciana sciecia (faza otworu za nim wypelniona) i stoi na polce D - pracuje jak zebro przyporowe; wolna jest tylko czapka fazy Z 6...7 (wierzch 1,0 x 2,26). Upuszczona plytka (ok. 50 g) moze najwyzej wgniesc krawedz fazy (kosmetycznie); zlamania nie oczekuje (ocena, bez MES).

### 1.2 Kolizje 3D (`r31_kolizje.py`, przeciecia krawedz-trojkat)

| Uklad | Przeciecia |
|---|---|
| nominal: plytka (+0,002) - wkladka; plytka - pokrywka; wkladka - pokrywka; plytka n4 - wkladka | 0 / 0 / 0 / 0 |
| kontrola czulosci: plytka 0,05 w polce | 1147 / 1172 |
| plytka 0,399 w strone zebra (D) - wkladka; pokrywka wspolosiowa - wkladka | 0; 0 |
| plytka 0,399 OD zebra + pokrywka +0,15 od zebra wzgl. plytki: pokrywka - wkladka | **5 / 6** (Z 6,5...7,0 przy (35,6; -35,6) - kolnierz na wierzchu zebra) |
| j.w. pokrywka +0,30 | **5 / 6** |
| plytka w srodku + pokrywka +0,30 od zebra | 0 |

## 2. Uwagi

### P1 - Dolna krawedz kolnierza pokrywki moze siasc na wierzchu zebra klucza (wnikanie do 0,16 mm)

- Gdzie: `ramka_wkladka_okragla_v2.stl` - czesc zebra nad wierzchem wkladki (Z 6,0...7,0) siega do lica sciecia u 49,756 (`bryly_zebra_klucza`: `gorna` od r0 do `do`); `parametry.json` `round_key_rib_h` 4,5; K-67 sprawdza kolnierz tylko przy pokrywce wspolosiowej z wkladka (pierscien r 50,2...51,9).
- Dowod: kolnierz pokrywki konczy sie na Z 6,5 (garby w rowku plytki ustalaja wysokosc +-0,1), wierzch zebra jest na Z 7,0. Plytka moze stac 0,40 od zebra (luz otworu), a pokrywka wzgledem plytki jeszcze ok. 0,30 w te sama strone (luz 0,3 na obwodzie kolowym; w strone sciecia plytki wiecej miejsca - ograniczaja konce cieciwy: 0,304). Lico wewnetrzne kolnierza na osi zebra wypada wtedy na r 50,3 - 0,704 = 49,596 < 49,756 -> wnikanie 0,16. Proba 3D: 5 / 6 przeciec juz przy 0,40 + 0,15 (tabela 1.2). Uklad osiagalny w normalnej obsludze (plytka lezy dowolnie w luzie 0,4).
- Skutek: pokrywka nie domyka sie po stronie zebra (kolnierz na zebrze 0,5 wyzej, garb 335 st. nie wchodzi w rowek), az uzytkownik przesunie plytke; krawedz kolnierza (FDM) i czapka zebra moga sie wycierac.
- Poprawka (wkladka, 1 zmiana, potem K-65 e i K-67): czesc zebra nad Z 6 konczyc na u <= 49,40 (zamiast lica 49,756) - zapas do kolnierza w najgorszym ustawieniu 49,59 - 49,40 = 0,19; albo obnizyc zebro do `round_key_rib_h` 3,9 (wierzch Z 6,4 < 6,5; fazy 0,4) - zebro nadal 1,7 wyzsze od kieszeni magnesu. Do K-67 dopisac kolnierz przy przesunieciu plytki o luz 0,4 i pokrywki o 0,3 (najgorszy kierunek).

### P2 - Jezyk pokrywki: odksztalcenie nasady w poprzek warstw FDM do 1,6 %, ostry koniec szczeliny

- Gdzie: `ramka_pokrywka_okragla_v2.stl`, `round_cover_slit_w` 1,0, `round_cover_slit_h` 12, `round_cover_slit_offset` 6,5.
- Dowod (zmierzone): 8 szczelin przelotowych 1,000 x 12,000 (gora Z -8,000) na 17,58 / 32,43 / 147,57 / 162,43 / 197,58 / 212,43 / 327,58 / 342,43 st.; jezyk 12,0 szer. (po licu), 1,5 gr.; garb (srodek Z -18) 10 mm od nasady. Rachunek belki (`r42_jezyk.py`, E 2000 MPa): ugiecie 0,40 (nominal) -> 8,1 N na garb, odksztalcenie nasady 0,90 % (18 MPa); 0,55 (otwor FDM zanizony o 0,3) -> 1,24 %; 0,70 (pokrywka zsunieta o luz przy wciskaniu) -> 1,57 % (31 MPa). Pokrywka drukowana wierzchem w dol, wiec naprezenie przy nasadzie dziala w poprzek warstw (wytrzymalosc miedzywarstwowa PETG ok. 25...35 MPa), a szczelina konczy sie ostrym prostokatem (spietrzenie naprezen ok. 2...3x).
- Skutek: przy wielokrotnym zakladaniu mozliwe pekniecie jezyka od konca szczeliny (czesc tania, druk wlasny; nie wplywa na zamowienie PA12).
- Poprawka: `round_cover_slit_h` 15 (garb 13 od nasady: 0,53 % nominal / 0,93 % najgorszy przypadek, 3,7...6,5 N na garb) i koniec szczeliny zaokraglony (otwor o1,5...2,0 na koncu); do tego wydruk probny 1 szt. przed 4 szt.

### D (drobne)

- D1 Pasek 0,5 x 0,156 przy scieciu: sufit rowka klucza (Z -3,0) i dno rowka pokrywki (Z -2,5) w pasku u 49,20...49,356, szer. 3,6 (zmierzone: promienie w gore z sufitu przy u 49,25 / 49,30 trafiaja w -2,5 / -1,5 / 0). Detal ponizej rozdzielczosci MJF - nieszkodliwy (rowek pokrywki ma tam i tak 0,156), wykonawca opisal informacyjnie. Bez zmiany.
- D2 Odczyt w zlym obrocie na zebrze: czujniki A i C ok. 3,95 mm od magnesu (prog D5 przy 4 mm), B ok. 1,9 mm - ramka moze odczytac numer obroconej plytki, ktora lezy wyraznie krzywo (+4,5 mm). Jak w kwadracie (kolek 5); ostrzezenie w programie - paczka programu.
- D3 Plan 13, wpis R58 (glowna kolumna) nadal wymienia `round_key_pin_d/h/chamfer` wsrod nowych kluczy (opis rundy 1, dopisek rundy 2 jest dalej) - dopisac "(runda 2: zastapione `round_key_rib_*`)"; plan 14 p. 30 odsyla do "`R58_wdrozenie_zmiany.md`, sekcja 13", a sekcje rundy 2 to R2-0...R2-9.
- D4 Wkladka okragla ma 3 warianty bajtowe (EXACT); dokument kaze brac `baf94bf8...` - przy pakowaniu tylko ten plik (jak w rundzie 1).
- D5 Uwagi rundy 1 D4 (rowek 0,156 w scieciu), D5 (kalibracja programu ramki dla `okragla_ramkowa_*`), D8 (arkusz zamowienia) zostaja otwarte swiadomie - poza geometria; D8 czesciowo: `narzedzia/arkusz_zamowienia_R58.py` (commity `ded8b29`, `f3f62b0`), arkusza nie sprawdzalem.
- D6 K-67 wykonawcy: siatka przesuniec 0,1 w kole 0,4 (49 polozen) i erozja krawedzi plytki o 1 wezel - granice okna +-0,15 st. (opisane w rejestrze); wynik zgodny z moim (sekcja 1.1), metoda wiarygodna; kontrola czulosci (nominal 0, opuszczona 0,05 > 0, przesunieta poza luz > 0, geometria rundy 1 odtwarza okna 90/180/270) jest w kodzie.

## 3. Status uwag rundy 1

| Uwaga | Status | Dowod |
|---|---|---|
| B1 kolek w pustej kieszeni | **zamknieta** | sekcja 1.1: plasko tylko -0,75...+0,75 st. dla kazdej z 8 plytek (moj przeglad 360 st. co 0,25 st. x przesuniecia); zebro 4,5 > kieszen 2,2 |
| P1 plytka "prawie dobrze" na kolku | **zamknieta** | zly obrot = uniesienie 4,4...4,5, przechyl 2,6 st. (widoczne, jak kwadrat); naprowadzenie +-1,75 st.; resztka odczytu - D2 |
| P2 zatrzask pokrywki | **czesciowo** | 8 szczelin sa (zmierzone), nominal 0,9 % - patrz P2 rundy 2 |
| P3 `wyczysc_wyniki` kasuje R58 | **zamknieta** | kod (`rdzenie_R58`, pomijanie w `stl/`); test `narzedzia/test_R58_p3_d1.py` uruchomiony przeze mnie: 10 pominietych, stare usuniete |
| D1 wyjatek K-60 | **zamknieta** | kod: zgodny tylko bez zadnego klucza R58 i przy wszystkich 18 w parametrach; test: 5 przypadkow jak w R2-8 |
| D2 scianki ze stalych, kolnierz w 1 punkcie | **czesciowo** | scianki 3D z siatki (moje: rowek klucza - wnetrze >= 2,86 wieczorna / 6,65 poranna, wykonawca 2,676 / 6,364 z najblizszego punktu); kolnierz z calego pierscienia, ale tylko przy pokrywce wspolosiowej - P1 |
| D3 opis dna rowka pokrywki | zamknieta | plan 4.11: 2,72 / 2,68 (3D) |
| D4 rowek 0,156 w scieciu | otwarta swiadomie | ryzyka R58 doc sekcja 11 |
| D5 kalibracja programu | otwarta (paczka programu) | sekcje 11, 12 |
| D6 montaz A3144 / przewody | zamknieta (dokument) | sekcja 11 |
| D7 n8/n9, kwadrat | zamknieta | moj przeglad: n8/n9 uniesienie 4,5 w kazdym obrocie |
| D8 arkusz zamowienia | czesciowo | skrypt `arkusz_zamowienia_R58.py` - nie sprawdzalem |

## 4. Wymiary - plan / zmierzone (uklady jak w rundzie 1)

| Wymiar | Plan / parametry | Zmierzone | Zgodne |
|---|---|---|---|
| 10 STL: szczelnosc, rozmaitosc, przeciecia wlasne, normalne | 0 bledow, 1 skladowa | 10/10: krawedzi != 2: 0, zwroty zgodne, zdegenerowane 0, przeciec wlasnych 0, normalne zapisane zgodne, 1 skladowa | tak |
| Objetosci [cm3] | 48,90 / 48,91 / 49,18 / 49,20 / 22,45 / 25,12 | 48,8957; 48,9081...48,9110; 49,1833; 49,1952...49,1982; 22,4481; 25,1181 | tak |
| Gabaryty | plytki 100 x 100 x 8 (8,6); wkladka 130 x 148,4 x 10,5; pokrywka 103,6 x 103,6 x 20 | to samo (wkladka montazowo Z -3,5...7,0) | tak |
| Wierzch plytek = runda 1 = okragla R59 | identyczny (poza dolkami i cyfra) | 0 roznic vs runda 1 (8/8); bazowe vs R59: 0; warianty: roznice tylko dolki i cyfra (1547...1881 wezlow jak w rundzie 1) | tak |
| Spod plytek vs runda 1 | tylko rowek klucza | 2270 wezlow roznic, 0 poza obszarem starego i nowego rowka; dawny rowek u 43...46 pelny (Z -8) | tak |
| Obrys, sciecie, rowek pokrywki | R 50, 49,356, dno 49,2, Z -1,5...-2,5 | 49,996...50,000; 49,356 (v +-4,9, Z -1/-4/-7,5); 49,196...49,200 | tak |
| Kieszenie magnesow | o5,2 x 2,2 w osiach r 45 | mapy spodu bez zmian vs runda 1 (0 roznic poza rowkiem klucza) | tak |
| Rowek klucza | 3,6 x 5,0 od r 46,0, os -45 st. | 3,600 (os 0,000) na u 46,2...49,3 i Z -7,9 / -5,5 / -3,1; sufit Z -3,000; r0 46,000 (v -1,5 / 0 / 1,5; Z -7,5 / -5 / -3,2) | tak |
| Scianki 3D rowka klucza | >= 1,5 (wykonawca 2,676 / 6,364) | wieczorna: sufit 2,93, boki 2,86, czolo 3,20 (promienie co 15 st.); poranna: boki 6,65, czolo 7,13; do rowka pokrywki 0,50 w pasku 0,156 (D1) | tak |
| Zebro klucza | 3,0; od r 46,5 do 49,756; Z 2,5...7,0; faza 1,0 | szer. 3,000 (v +-1,500) na Z 2,6...5,9 i u 46,7...49,7; czolo u 46,500 (Z 2,6...5,5), 47,0 na Z 6,5, 47,45 na Z 6,95; wierzch Z 7,000 (u 47,6...49,74), szer. wierzchu 1,0; za licem (u 49,8) Z 6,0 | tak |
| Wkladka poza zebrem = runda 1 | bez zmian | z gory: roznice tylko u 43,56...50,70, |v| <= 1,48 (kolek -> zebro); od spodu 0 roznic | tak |
| Interfejs do blatu = wkladka kwadratowa | identyczny | mapy z gory i od spodu: 0 roznic poza |x|, |y| > 51,35 | tak |
| Otwor, sciecie, wystep, Hall | o100,8; 49,756; r 47; 5,0 x 5,5 | 50,397...50,399; 49,756 (v +-2,5 / +-4); 46,997; 5,000 x 5,500 w osiach (0,000) | tak |
| Kanaly Halla | ciagle | spod wkladki = runda 1 (0 roznic) -> jak runda 1 (ciagle do szczeliny przy uchu) | tak |
| Pokrywka poza szczelinami = runda 1 | bez zmian | roznice promieni tylko na katach szczelin (384 probki, Z -19,9...-8,4) | tak |
| Szczeliny pokrywki | 8 x 1,0 x 12, srodki +-7,4 st. od garbow | 8 sektorow przelotowych (Z -19,5...-8,05), srodki 17,58 / 32,43 / 147,57 / 162,43 / 197,58 / 212,43 / 327,58 / 342,43; szer. 1,000; gora Z -8,000; do wyciec palcowych ok. 40 st. | tak |
| Luz plytka - otwor | 0,4 | 0,397...0,399 (kolizje nominalne 0) | tak |
| Zebro w rowku | 0,3 / 0,5 / 0,5 | 0,30 / 0,30; 0,50; 0,50 | tak |
| Kolnierz nad wkladka | >= 0,4 | 0,5 przy pokrywce wspolosiowej; przy skrajnym ustawieniu wnikanie 0,16 w zebro | **nie** (P1) |
| SHA 12 plikow | = `sha256_stl_po_R58.txt` = tabela R2-0 | 12/12 znak po znaku, kazda suma 64 znaki (takze pokrywka `8e2385...223787`); w plikach nie ma sumy o innej dlugosci | tak |
| Pliki rundy 1 | = tabela rundy 1 | 10/10 w `stl_r58_runda1` | tak |
| Stare 21 STL + 4 JSON | = SHA256SUMS R59 | 25/25 | tak |

## 5. Kod (`git diff f429605 ca6b446 -- Ramki/ramka_generator.py`)

- Nowy K-67 (`ulozenia_plaskie`, `unoszenie`): naprawde przeszukuje obrot 0...360 co 0,25 st. x przesuniecie w kole luzu dla kazdej z 8 plytek, przeszkody = wszystko powyzej polki (sciana, sciecie, zebro), z kontrola czulosci i odtworzeniem B1 na geometrii rundy 1; wynik = moj. Ograniczenie: kolnierz pokrywki liczony tylko wspolosiowo (P1).
- `wyczysc_wyniki(out, P)`: pomija tylko STL o nazwach z `rdzenie_R58(P)`; wywolanie bez P - dawne zachowanie; `main` wola z P. Test uruchomiony (sekcja 3).
- K-60: wyjatek zaostrzony poprawnie (D1 zamkniete).
- Budowa: zebro jako `dodatnie_po` (nie tnie go faza otworu), szczeliny jako bryly tnace; stare czesci nietkniete - wykonawca: `--etap A` w kopii przebudowal 13 plikow bajtowo = SUMS R59, `SPRAWDZ_iter16` = iter12 (nie powtarzalem, Blender).
- `narzedzia/studium_R58.py`: zdanie o "blokadzie zgrubnej" usuniete (w. 7: "sciecie NIE blokuje obrotu").
- Pozostalosci po kolku: brak w `parametry.json` i generatorze; w planie tylko wpis skreslony w 3.4 i opisy historii (D3); w `R58_wdrozenie_zmiany.md` tylko w czesci "RUNDA 1 (historia)".

## 6. Czego NIE sprawdzilem

- Powtarzalnosci (K-59) i przebiegu `--etap A` / `SPRAWDZ_iter16` - nie uruchamialem Blendera.
- MES zebra i jezyka pokrywki (tylko rachunek belki i ocena); wytrzymalosci miedzywarstwowej konkretnego PETG.
- Pola magnetycznego przy przechyle na zebrze (D2 - przyjete wg D5).
- Kolizji 3D wszystkich 8 plytek w ulozeniach skrajnych (zrobione dla wieczornej bazowej i porannej n4; mapy spodu 8 plytek identyczne).
- Proby 3D proponowanej poprawki P1 (tylko rachunek zapasu 0,19).
- Arkusza zamowienia R58 i commitu `f3f62b0`.
- Rzutow PNG i raportow R58_iter5...iter7, R58powt_iter2, A_kopiaP3_iter1, SPRAWDZ_iter16.