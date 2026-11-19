# R58 - komplet okragly do ramki: plytki okragle ramkowe, wkladka okragla, pokrywka okragla (lista edycji w zrodle prawdy)

Data: 2026-11-19. Zlecenie wlasciciela 19.11.2026 (decyzje zamkniete): plytki OKRAGLE pod produkt koncowy, czyli lezace na ramce swietlnej - zarezerwowana zmiana R58 ("wkladka i pokrywka plytki okraglej"). Projekt luzow koordynatora: `narzedzia/studium_R58.py` (0 bledow). Wykonawca: R58-A.
Zakres edycji: `parametry.json`, `ramka_generator.py`, `plan_ramki_v2.md`, `protokol_weryfikacji_v2.md`, `wyniki_v2/` (10 nowych STL poza gitem, 2 nowe JSON, raporty, rzuty kontrolne), ten plik.
NIE dotknieto: `stanowisko/`, `Ramki_do_wgrania/`, `Ramki_pakiet/`, `00_NADZOR_STAN.md`, dokumentow dla wlasciciela (`Zakupy i druk...`, `Budowa ramki...`, `Stanowisko kontroli...`), arkuszy `R59_*`, `narzedzia/`, `wyniki_v2/arkusze/`, `wyniki_v2/render/`, `wyniki_v2/ramka_v2.blend`, `wyniki_v2/README.md`, `wyniki_v2/do_v3.md`, 21 STL i 4 JSON ukladu R59 (plikow plytek okraglych n8/n9 tez nie).

## 0. Wynik

- `--etap R58 --iter 4` (generator koncowy): 19 ZAL, 0 N/D, 0 NIE (B 0 / P 0 / D 0); 1744 sondy, 0 niezgodnych, 0 sond blizej niz 0,1 od sciany; 25 s.
- `--etap R58_SPRAWDZ --iter 3` na plikach oddanych (lista nizej): 19 ZAL, 0 NIE.
- Powtarzalnosc: `--etap R58` w czystej kopii folderu (`--out wyniki_powt`: tylko 4 JSON R59 i 3 STL odniesienia) - 10 STL i 2 JSON bajtowo = pliki oddane (12 z 12, dwa razy: przebiegi 7 i 11). Wyjatek jak przy wkladce kwadratowej: w 1 z 4 przebiegow z koncowym zapisem (przebieg 9) `ramka_wkladka_okragla_v2.stl` wyszla w wariancie z jednym wierzcholkiem przesunietym o 0,00085 mm (objetosc rozna o 1e-9 cm3, gabaryt identyczny, wszystkie K = ZAL) - patrz 6 i 10.
- `--etap SPRAWDZ --iter 15` (stare pliki, generator koncowy): 58 ZAL, 5 N/D, 0 NIE (B 0 / P 0 / D 0), 2509 sond, 0 niezgodnych. Wyniki K, wartosci zmierzone i wszystkie sondy identyczne z `SPRAWDZ_iter12` (stan R59); jedyna roznica: dopisek w K-60 o zrzucie parametrow (10, odstepstwo 3). 5 x N/D jak dotad: K-19, K-21, K-48, K-52 (uchylone R50) i K-59 (recenzent).
- 25 starych plikow bez zmian: 21 STL + 4 JSON = `Ramki_pakiet/SHA256SUMS_2026-11-16_R59.txt` na MSI (21 STL w `<MSI>\kod\qc\Ramki\wyniki_v2\stl`, 4 JSON w `Ramki/wyniki_v2/json` tego worktree) i na PC po wszystkich przebiegach: 25 z 25 (sekcja 8).
- Plan <-> JSON (`porownaj_plan_z_json`): 0 roznic (po dopisaniu 14 kluczy do tabel 3.1, 3.4, 3.6); walidator kluczy R14: 301 kluczy (287 + 14), LICZONE max roznica 0,0000.

Pliki oddane (STL w `Ramki/wyniki_v2/stl/` tego worktree - nie w gicie; lista `wyniki_v2/raport/sha256_stl_po_R58.txt`; gabaryt w orientacji druku z siatki STL):

| Plik | SHA-256 | Objetosc [cm3] | Gabaryt X x Y x Z [mm] | Szt. / material (`quantities_r58`, `materials_r58`) |
|---|---|---|---|---|
| `ramka_plytka_okragla_ramkowa_wieczorna_v2.stl` (bazowy) | 18089783cd0ad01532b9b4d5e3ffcea6b45a4e8fa5f3cf100686718e44b6789e | 48,90 | 100,000 x 100,000 x 8,000 | - (wzorzec) |
| `ramka_plytka_okragla_ramkowa_wieczorna_n1_v2.stl` | f50c60de374d73e0c90f2163d7c7723fef6b912bc9a02e23dde3cf5c0f13d674 | 48,91 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_plytka_okragla_ramkowa_wieczorna_n2_v2.stl` | 34c91cba851b580a61688a7a2669c05f62849bd6ad45dff6ad19ec9ef880953b | 48,91 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_plytka_okragla_ramkowa_wieczorna_n3_v2.stl` | 6b8ceabc7d232c390a9c8b3438b2bd0621e0035e38b7db5a53b9eaef697301a6 | 48,91 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_plytka_okragla_ramkowa_poranna_v2.stl` (bazowy) | 44d67d1980a96708178a4c4fb29827b663f4790e7ef903f96c6d7de208538fce | 49,19 | 100,000 x 100,000 x 8,000 | - (wzorzec) |
| `ramka_plytka_okragla_ramkowa_poranna_n4_v2.stl` | 7f80acf3c8ba03a3f53409232f066fd8ca9736d26d317ee445991d2bed24e022 | 49,20 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_plytka_okragla_ramkowa_poranna_n5_v2.stl` | f6e24d4991920dded47044800ea83b5c7ae6377f6802b3132fec499139347f39 | 49,20 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_plytka_okragla_ramkowa_poranna_n6_v2.stl` | 3c78322049b49d2c849324af66d2525949b25430d0a933e2c3b8cc6814204b53 | 49,20 | 100,000 x 100,000 x 8,600 | 1 / PA12 drukarnia |
| `ramka_wkladka_okragla_v2.stl` | 0ca13cd723c2e3f3261ce01d3f9f6e460198f2f52ad72b0f62b7f0e2083e7e0f | 22,42 | 130,000 x 148,400 x 10,100 | 3 / PA12 drukarnia |
| `ramka_pokrywka_okragla_v2.stl` | 86e9976b6e38b60579d37088c79eede4fe1cf2b2f7ebfb21467feae7183642b1 | 25,26 | 103,600 x 103,600 x 20,000 | 4 / PETG FDM (wlasny) |
| `json/uklad_gniazd_okragla_ramkowa_wieczorna.json` | 16c4544b70ccd4c5f5ca6124d0093703cd5588768083f3196065e199c8b61e21 | - | - | - |
| `json/uklad_gniazd_okragla_ramkowa_poranna.json` | 20fce19e53ca10795cf397e9ba0381ff5c54941d6b45d054056875a0a324a277 | - | - | - |

Orientacja druku: plytki gniazdami do gory, spod plaski na Z = 0 (kieszenie i rowek klucza otwarte od spodu); wkladka spodem w dol, lezy na koncach kolkow ustalajacych (jak kwadratowa); pokrywka wierzchem w dol. Komplet do drukarni (7 pozycji x ilosci): 6 plytek x 48,91 / 49,20 + 3 wkladki x 22,42 = 361,60 cm3 -> 325...579 zl (stawka 0,90...1,60 zl/cm3, czesci biale bez mnoznikow); druk wlasny: 4 pokrywki x 25,26 = 101,05 cm3 PETG. Arkusz zamowienia R59 nie zawiera tych pozycji (odstepstwo 2).

Zrodla (stan koncowy): `ramka_generator.py` fe6cd09507e82f445a20fd3dc2f3a39bb8c5a2c0661ecf245db9a6d1f65ab99a (bylo d3b56f63be52..., diff +1370 / -34 linii), `parametry.json` 2686c881ceb1d22942b13112ebb6cbabb38b9d8e14d9e011436cdf3c6a8ab8b0 (bylo 8434aafe1584..., +26 / -4), `plan_ramki_v2.md` 296200b126f66e4a4abee0cacb16d41d0eac3d19dd4197c7cae486ce29222d9f (bylo 5e7379a688ee..., +60 / -8; plan czyta generator tylko w `porownaj_plan_z_json` - przebiegi #1-#4 szly z planem sprzed R58, #5-#13 z wersja 7b48089a... (rozni sie od koncowej jednym zdaniem w 4.1b); wynik porownania za kazdym razem: 0 roznic), `protokol_weryfikacji_v2.md` b5341ae3245edf150d3bd4c082c44898d8f2fd59fd709ff246f005f01b783d2e (bylo da33c0b22dd7..., +20 / -5).

## 1. Decyzje wlasciciela (19.11.2026) i ich odczyt

1. Pelny komplet: plytki okragle z magnesami i rowkiem pokrywki + okragla wkladka + okragla pokrywka; korpus i blat BEZ ZMIAN -> nowe typy plytek `okragla_ramkowa_wieczorna` / `okragla_ramkowa_poranna`, nowe czesci `wkladka_okragla`, `pokrywka_okragla`; obrys zewnetrzny wkladki = kwadratowa (blat bez zmian).
2. Numery jak kwadratowe: n1-n3 wieczorne, n4-n6 poranne; ramka czyta 3 magnesy A/B/C, program ramki bez zmian. Dzisiejsze okragle n8/n9 zostaja plytkami testowymi skanera - ich pliki nie byly ruszane (SHA w sekcji 8).
3. Srednica 100 zostaje (pole skanowania niezmierzone - ryzyko przyjete przez wlasciciela).

Kody kompletu (bit = magnes w kieszeni A/B/C na r 45 = dolek kodu; bit D = 0, dolek D tylko w pliku bazowym):

| n | typ | magnesy (kieszenie z magnesem) | dolki | pozycje dolkow (`code_dimples_round`) | cyfra (`number_pos_round`) |
|---|---|---|---|---|---|
| 1 | wieczorna | A | A | A (-4,5; -43,5), B (-1,5; -43,5), C (1,5; -43,5) | (35; -26,5) |
| 2 | wieczorna | B | B | j.w. | j.w. |
| 3 | wieczorna | A + B | A + B | j.w. | j.w. |
| 4 | poranna | C | C | A (36,5; 18,5), B (36,5; 21,5), C (43; 6) | (-44; 5,5) |
| 5 | poranna | A + C | A + C | j.w. | j.w. |
| 6 | poranna | B + C | B + C | j.w. | j.w. |

Osie kieszeni magnesow plytki i kieszeni Halla wkladki: A (-31,82; -31,82), B (-31,82; 31,82), C (31,82; 31,82) (promien 45 na przekatnych; kwadrat ma je w rogach (+-42, +-42)). Kolek klucza: os D (31,82; -31,82). Magnes jak w kwadracie: ten sam biegun w dol (instrukcja w `kody_plytek.md`).

## 2. `parametry.json` - nowe klucze (wszystkie status ZALOZENIE, zrodlo R58, opis po polsku z rachunkiem scianek)

| Klucz | Sekcja | Wartosc | Znaczenie |
|---|---|---|---|
| `round_magnet_r` | plytka | 45 | promien osi kieszeni magnesow A/B/C (plytka), kieszeni Halla A/B/C i kolka klucza D (wkladka); osie na przekatnych, D = `round_flat_angle` |
| `round_key_slot_w` | plytka | 3.6 | szerokosc rowka klucza od spodu plytki |
| `round_key_slot_r0` | plytka | 43 | promien plaskiego konca wewnetrznego rowka klucza |
| `round_key_slot_h` | plytka | 2.5 | wysokosc rowka klucza od spodu |
| `plate_numbers_round_frame` | plytka | {"wieczorna": [1, 2, 3], "poranna": [4, 5, 6]} | numery plytek okraglych ramkowych |
| `round_cover_snap_angles` | pokrywka | [25, 155, 205, 335] | katy garbow pokrywki okraglej |
| `round_insert_clearance` | blat_rama_wkladka | 0.4 | luz promieniowy plytki okraglej we wkladce (otwor 100,8, sciecie 49,756) |
| `round_insert_ledge_r` | blat_rama_wkladka | 47 | promien wewnetrzny wystepu wkladki |
| `round_insert_shelf` | blat_rama_wkladka | 10 | bok 4 polek kwadratowych wkladki |
| `round_key_pin_d` | blat_rama_wkladka | 3.0 | kolek klucza |
| `round_key_pin_h` | blat_rama_wkladka | 2.0 | wysokosc kolka nad polka |
| `round_key_pin_chamfer` | blat_rama_wkladka | 0.5 | faza wierzcholka kolka |
| `quantities_r58` | sterowanie | n1...n6 po 1, wkladka okragla 3, pokrywka okragla 4 | ilosci kompletu (osobno od `quantities`) |
| `materials_r58` | sterowanie | plytki i wkladka "PA12 drukarnia", pokrywka "PETG FDM (wlasny)" (w JSON ta sama tresc co w `materials`, z polska litera) | materialy kompletu |

Bez zmian wartosci: wszystkie 287 dotychczasowe klucze (w tym `quantities`, `materials`, `plate_numbers_round`, `code_dimples_round`, `number_pos_round`). Uzyte bez nowego klucza: `magnet_pocket_d/depth`, `cover_groove_w/depth/z`, `cover_clearance`, `cover_skirt_t`, `cover_inner_h`, `cover_top_t`, `cover_skirt_below`, `cover_snap_bump/hgt/r/w/z`, `cover_finger_w/h`, `insert_*`, `hall_*`, `wire_rabbet*`, `tab_*`, `finger_cut_w`.

## 3. `ramka_generator.py` - zmiany (kazda z powodem)

| # | Miejsce | Zmiana | Powod |
|---|---|---|---|
| 1 | naglowek, `main` | tryby `--etap R58` (buduje i sprawdza tylko 10 STL + 2 JSON) i `--etap R58_SPRAWDZ` (tylko sprawdza); nowa `main_R58`: bez `wyczysc_wyniki` i bez etapow A-C; raport `raport_wykonawcy_R58_iter<n>.md` przez istniejacy `zapisz_raport` (+ sekcja 7: ilosci kompletu) | zlecenie: nie przebudowywac i nie nadpisywac 25 plikow R59 (wkladka kwadratowa nie odtwarza sie bajtowo) |
| 2 | `WYMAGANE_KLUCZE`, `KLUCZE_R58` | 14 nowych kluczy dopisanych do walidatora R14 | R14: brak / nieznany klucz = blad |
| 3 | `OBJ_ORIENT` | plytka okragla ramkowa wieczorna 49, poranna 49, wkladka okragla 22, pokrywka okragla 25 (z siatek: 48,90 / 49,19 / 22,42 / 25,26) | K-04b |
| 4 | `TYPY_PLYTEK_R58`, `typ_bazowy`, `plytka_ramkowa`, `osie_okragle`, `NAROZA_CCW` | osobna krotka typow R58 (petle etapow A-C po `TYPY_PLYTEK` ich nie widza); osie A-D liczone z `round_magnet_r` i `round_flat_angle` co cwierc obrotu | etapy A-C i `--etap SPRAWDZ` bez zmian; zadnych liczb w kodzie |
| 5 | `uklad_pochodne`, `numery_plytek`, `wczytaj_uklad` | galaz ramkowa: `magnet_pockets` (3, z `angle_deg`), `cover_groove`, `key_slot`; numery z `plate_numbers_round_frame`; `wczytaj_uklad(..., opis_odczytu)` (tekst w dzienniku przy odczycie odniesien) | JSON wg zlecenia; uklady R59 czytane tylko do porownan |
| 6 | `zbuduj_plytke` | dla JSON z `cover_groove` / `key_slot`: pierscien tnacy rowka pokrywki (R + 0,2 ... R - 0,8, te same katy wierzcholkow co walec) i bryla rowka klucza (konce poza plytka odsuniete od plaszczyzn bryly sciecia); kieszenie magnesow z istniejacej petli `magnet_pockets`; bryly dopisane na koncu listy tnacej | plytki okragle R57/R59 (bez tych pol) buduja sie identycznie |
| 7 | `zbuduj_pokrywke_okragla`, `wymiary_pokrywki_okraglej`, `przekroj_garbu`, `bm_profil_po_luku` | kubek + 4 garby wyciagniete po luku o stalym przekroju + wyciecia palcowe; przekroj garbu = konstrukcja z `zbuduj_pokrywke` (kopia; `zbuduj_pokrywke` bez zmian) | 4.2a |
| 8 | `zbuduj_wkladke_okragla`, `otwor_wkladki_okraglej`, `kontur_polek_okraglych`, `_wkl_obrys`, `_wkl_dodatnie_wspolne`, `_wkl_tnace_wspolne` | wkladka okragla; obrys, uszy, kolki, strzalki, rowek kablowy, kanaly pod uszami i magnesy - kopie logiki `zbuduj_wkladke` (ktora zostala bez zmian) | 4.6a; obrys zgodny z kwadratowa (K-65 i) |
| 9 | `M_druk` | `pokrywka_okragla` jak `pokrywka`, `wkladka_okragla` jak `wkladka` | orientacja druku |
| 10 | `stl_kanoniczny`, `eksportuj_stl` | parametr `zero_dodatnie` (domyslnie False): -0,0 zapisywane jako +0,0; wlaczony tylko w `etap_R58` | znak zera w normalnych eksportera zmienia sie miedzy przebiegami (`do_v3.md` #9); pliki etapow A-C zapisywane jak dotad |
| 11 | `sprawdz_plytke` (K-09, K-13), `sprawdz_scianki_naroznikow` (K-16), `sprawdz_okragla` (K-61 b, K-63) | K-09: kontrola odwrotna dawnych rogow tylko na kwadracie (okragla R57 miala liste pusta - bez zmian); K-13: gdy w obszarze cyfry sa tylko wierzcholki cech od spodu (Z < -0,02: koniec rowka klucza), wysokosc z promieni z gory; K-16: opis dla ramkowej; K-61 (b) dla ramkowej na Z -7,5 promieniami odsunietymi o +-4,9; K-63 pomijane dla ramkowej | rowek klucza w osi sciecia; dla plikow R57/R59 wyniki identyczne (SPRAWDZ_iter15 = iter12) |
| 12 | `sprawdz_wkladke`, `SONDY_K29`, `SONDY_K30` | listy sond K-29 i K-30 przeniesione do stalych modulu (bez zmian tresci - porownane po wczytaniu: rowne) | te same sondy dla wkladki okraglej (K-65 i) |
| 13 | nowy blok (5a): `sprawdz_ramkowa` (K-64), `sprawdz_wkladke_okragla` (K-65), `sprawdz_pokrywke_okragla` (K-66), `sprawdz_pasowania_R58` (K-67) + pomocnicze (`trafienia`, `srodek_wneki`, `srodek_bryly`, `mapa_promieni`, `porownaj_mapy`, `punkty_kola`, `otwory_o3`) | sprawdzenia na STL wczytanych z powrotem; rzuty kontrolne od spodu i z gory | wymaganie 3 zlecenia |
| 14 | `etap_R58`, `odstepstwa_informacyjne_R58`, `DZIENNIK['ilosci_r58']`, `zapisz_raport` (opcjonalny `dodatek`) | przebieg R58; kontrola `quantities_r58` / `materials_r58` (dokladnie 8 czesci do zamowienia); rejestr odstepstw (7 wpisow) | |
| 15 | `zrzut_parametrow_zgodny`, `sprawdz_K60` | zrzut `parametry.json` w `arkusz_wymiarow.md` sprzed R58 zgodny, gdy rozni sie TYLKO brakiem kluczy `KLUCZE_R58`; uwaga w wyniku K-60 | arkusze R59 bez zmian (zlecenie) - bez tego `--etap SPRAWDZ` dawalby K-60 = NIE (P) |

## 4. `plan_ramki_v2.md` - edycje

| Miejsce | Zmiana |
|---|---|
| wstep | rejestr R1...R59 (bez "R58 zarezerwowany") |
| D5, D8, D11, D12 | dopiski [R58]: wkladka okragla (otwor, wystep, polki, kieszenie Halla w osiach r 45, kolek klucza), pokrywka okragla (garby po luku, rowek na calym obwodzie), numery n1-n6 okraglych ramkowych (kod, magnesy na r 45, n8/n9 testowe; ten sam numer co kwadrat), wkladka okragla = kwadratowa w obrysie, uszach, kolkach, magnesach, rowku |
| 3.1, 3.4, 3.6 | 14 wierszy nowych kluczy (porownanie plan <-> JSON: 0 roznic) |
| 4.1a | funkcja: do ramki sluzy 4.1b (bylo "na ramce dopiero po nowej wkladce i pokrywce (R58, po tescie)") |
| nowa 4.1b | plytka okragla ramkowa: identycznosc z 4.1a, kieszenie, rowek pokrywki, rowek klucza, numery, obrys cyfry, pliki i JSON, objetosci, sprawdzenia |
| nowa 4.2a | pokrywka okragla |
| nowa 4.6a | wkladka okragla |
| 4.11 | 4 wiersze: plytka okragla ramkowa, plytka we wkladce okraglej, wkladka okragla, pokrywka okragla |
| 12.1 | pozycja 17: pliki R58 i tryb `--etap R58` |
| 13 | naglowek R1...R59; wiersz R58 (przed R59); w wierszu R59 "(Numer R58 jest zarezerwowany ... bez wpisu.)" -> "(... wpis R58 z 19.11.2026 wyzej.)" |
| 14 | punkt 29 |

## 5. `protokol_weryfikacji_v2.md` - edycje

| Miejsce | Zmiana |
|---|---|
| tabela 1 | 4 wiersze R58 (gabaryt, objetosc orientacyjna 49 / 49 / 25 / 22 z siatek 48,9 / 49,2 / 25,3 / 22,4, orientacja = jak plytka okragla / pokrywka / wkladka, etap R58) |
| 2 | sprawdzenia ogolne K-01...K-04b takze dla 10 plikow R58 (`--etap R58`) |
| nowa 3b | opis kompletu, ukladow i osi; K-64 (plytka ramkowa), K-65 (wkladka okragla), K-66 (pokrywka okragla), K-67 (pasowania) z metodami, sondami i tolerancjami |
| K-61 | uwaga [R58]: (b) na Z -7,5 promieniami rownoleglymi odsunietymi o +-4,9 |
| K-63 | nie dotyczy plytek okraglych ramkowych (K-64) |
| K-59 | [R58]: czysta kopia odtwarza 10 STL + 2 JSON (zapis +0,0); 21 STL i 4 JSON = SHA256SUMS R59 |
| K-60 | [R58]: zrzut sprzed R58 zgodny, gdy brakuje tylko 14 kluczy R58; kazda inna roznica = NIE |

## 6. Przebiegi (PC, konto `<konto-PC>`, katalog `<PC-katalog>\r58\Ramki`, Blender 5.2.3 LTS, jeden proces naraz, wolny RAM 17,3 GB; logi `<PC-katalog>\r58\Ramki\_r58\*.log`)

| # | Polecenie (po `--`) | Generator (SHA) | ZAL / N/D / NIE | Uwagi |
|---|---|---|---|---|
| 1 | `--etap R58 --iter 1` | 9687304e806... | 17 / 0 / 2 | K-13 (B): plik bazowy wieczorny - w obszarze cyfry jedyne wierzcholki to koniec rowka klucza (Z -5,5), wiec "max Z wierzcholkow" = -5,5 zamiast 0 (blad metody, nie geometrii); K-65 (B) (h): 46 wierzcholkow y = 52,4 w float32 (52,39999771) policzonych jako "y < 52,4" (tolerancja 1e-6). Obie metody poprawione (sekcja 3 #11, #13) |
| 2 | `--etap R58 --iter 2` | ea3fbfee442... | 19 / 0 / 0 | wkladka okragla: SHA inna niz w #1 (3 normalne, tylko znak zera) |
| 3 | `--etap SPRAWDZ --iter 13` | ea3fbfee442... | 58 / 5 / 0 | stare pliki |
| 4 | `--etap R58 --iter 1 --out wyniki_powt` | ea3fbfee442... | 19 / 0 / 0 | czysta kopia: 9 STL + 2 JSON = #2, wkladka rozna (znak zera) -> dodany zapis +0,0 (sekcja 3 #10); raport nadpisany przez #7 i #11 |
| 5 | `--etap R58 --iter 3` | fa5799e438e... | 19 / 0 / 0 | z zapisem +0,0: wszystkie 10 STL maja nowe SHA (wczesniej zawieraly -0,0) |
| 6 | `--etap R58_SPRAWDZ --iter 1` | fa5799e438e... | 19 / 0 / 0 | |
| 7 | `--etap R58 --iter 1 --out wyniki_powt` (czysta kopia) | fa5799e438e... | 19 / 0 / 0 | 12 z 12 bajtowo = #5 |
| 8 | `--etap SPRAWDZ --iter 14` | fa5799e438e... | 58 / 5 / 0 | |
| 9 | `--etap R58 --iter 4` | fe6cd09507e... (koncowy; od #5 tylko teksty rejestru i raportu) | 19 / 0 / 0 | 11 plikow = #5; wkladka okragla 9187827b... (wariant: 1 wierzcholek o 0,00085 mm, 5 trojkatow inaczej; objetosc 22,419780 w obu, roznica 1e-9 cm3; gabaryt identyczny) |
| 10 | `--etap R58_SPRAWDZ --iter 2` | fe6cd09507e... | 19 / 0 / 0 | na plikach #9 (z wariantem wkladki) |
| 11 | `--etap R58 --iter 1 --out wyniki_powt` (czysta kopia) | fe6cd09507e... | 19 / 0 / 0 | 12 z 12 bajtowo = #5 (wkladka 0ca13cd7...); raport: `wyniki_v2/raport/raport_wykonawcy_R58powt_iter1.md` |
| 12 | `--etap SPRAWDZ --iter 15` | fe6cd09507e... | 58 / 5 / 0 | STAN KONCOWY starych plikow |
| 13 | wkladka 0ca13cd7... (z #11) wstawiona do `wyniki_v2/stl` na PC, wariant #9 odlozony jako `_r58\wkladka_okragla_iter4_wariant.stl`; `--etap R58_SPRAWDZ --iter 3` | fe6cd09507e... | 19 / 0 / 0 | STAN KONCOWY plikow R58 (= pliki w worktree) |

Raporty w gicie (`wyniki_v2/raport/`): `raport_wykonawcy_R58_iter1...iter4.md`, `raport_wykonawcy_R58_SPRAWDZ_iter1...iter3.md`, `raport_wykonawcy_R58powt_iter1.md` (przebieg #11, plik z `wyniki_powt`), `raport_wykonawcy_SPRAWDZ_iter13...iter15.md`, `sha256_stl_po_R58.txt` (format `sha256sum -c`, sciezki wzgledem `wyniki_v2/`). Rzuty kontrolne (31 PNG) tylko z przebiegow koncowych #9, #12, #13: od spodu plytek bazowych (kieszenie, rowek klucza), z gory i od spodu wkladki okraglej (polki, kieszenie Halla, kolek, kanaly), cyfry n1-n6; rzuty przebiegow #1, #2, #3, #5, #6, #8 nie zostaly sprowadzone (raporty tych przebiegow wskazuja pliki, ktorych w gicie nie ma).

## 7. Wyniki K (`raport_wykonawcy_R58_iter4.md`; te same wartosci w `R58_SPRAWDZ_iter3` na plikach oddanych)

| K | Wynik | Najwazniejsze wartosci zmierzone |
|---|---|---|
| K-01 | ZAL | 10 STL, 5164...25518 trojkatow, bez NaN |
| K-02 | ZAL | plytki 100 x 100 x 8 / 8,6 (X, Y +-50,000); wkladka 130 x 148,4 x 10,1; pokrywka 103,6 x 103,6 x 20 |
| K-03 | ZAL | 0 / 0 / 0 we wszystkich 10 (0 trojkatow o polu < 1e-6) |
| K-04 | ZAL | 1 skladowa w kazdym |
| K-04b | ZAL | 48,90...49,20 (orient. 49), 22,42 (22), 25,26 (25) |
| K-05 | ZAL | 18/1 i 23/1; max promien 45,927 / 46,412; scianka 3,000; (h) sockets = kwadrat: tak / tak |
| K-06, K-07, K-08 | ZAL | 90/90 i 115/115; 12/12; 10/10 we wszystkich 8 plytkach |
| K-09 | ZAL | 12/12 (znaczniki R59) |
| K-11 | ZAL | bazowe A+B+C+D; n1 A, n2 B, n3 A+B, n4 C, n5 A+C, n6 B+C |
| K-13 | ZAL | bazowe 0,000; warianty 0,600 |
| K-16 | ZAL | jak plytki okragle R59 (gniazdo-krawedz 4,07 / 3,59; stozek-krawedz 3,07 / 3,02; znacznik-gniazdo 3,19 / 3,02) |
| K-61 | ZAL | promien 49,996...50,000; sciecie 49,356 (Z -4 w osi; Z -7,5 promieniami +-4,9); glebokosc 0,644; sciecie-obrysy 4,59 / 4,81 |
| K-62 | ZAL | jak plytki okragle R59; bity = n |
| K-64 | ZAL | kieszenie: srodek (+-31,820; +-31,820), o 5,200 x 5,194, gl. 2,200, scianka do krawedzi 2,402; rowek pokrywki 0,800 (16 kierunkow), wysokosc 1,000, srodek Z -2,000, w scieciu dno r 49,200 (0,156 w cieciwie); rowek klucza 3,600 x 2,500 od r 43,000 (os 0,000); scianki (wieczorna / poranna): kieszen-otwor 9,81 / 7,48, sufit kieszeni-dno gniazda 1,80, sufit rowka klucza-dno gniazda 1,50, rowek klucza-otwor 9,73 / 8,11, dno rowka pokrywki-obrysy na Z -1,5 3,52 (stozek C) / 3,19 (gniazdo id 22), stozek-kieszen w pionie 2,80; sockets = kwadrat; cyfra n1-n6: do gniazda 3,28...3,47, naroznik r <= 46,88; mapa wierzchu = plytka okragla tego typu: 128 191 / 127 067 punktow, 0 niezgodnych trafien, max dz 0,0000 |
| K-65 | ZAL | otwor r 50,397...50,400 (o 100,795); sciecie 49,756 / 49,756 / 49,756; wystep r 46,997...46,998; polka Z 2,500 (7 punktow); kieszenie Halla w osiach A/B/C (odchylka 0,000), 5,000 x 5,500; kolek klucza (31,820; -31,820) o 3,000 x 2,990, wierzch 4,500; scianka w osiach 2,003 / 2,001 / 2,001; dno po rowku 2,903; wyciecie 30,000; K-56: 0 wierzcholkow; zgodnosc z wkladka kwadratowa: K-29 20/20, K-30 7/7, mapy z gory / od spodu 37 028 punktow, 0 / 0 niezgodnych, max dz 0,0000 / 0,0000; kanaly A 390, B 185, C 185 punktow - 0 w bryle |
| K-66 | ZAL | o 100,593...100,600 / 103,593...103,600; wierzch 2,000; Z -20...0; garby 25/155/205/335 st.: wystep 0,700, srodek Z -18,000, wysokosc 0,800, przeglad co 1 st. = 4 sektory w zadanych katach; wyciecia 30,000 x 3,000 przod i tyl |
| K-67 | ZAL | 0 kolizji (17 par, skurcz 0,05); styk plytka-polka bez skurczu 1430-1431 par (czulosc); luz promieniowy 0,397...0,402 (8 kierunkow), na scieciu 0,400; spod plytki 2,500 = polka 2,500; os magnesu - os kieszeni Halla 0,000 (A, B, C); kolek w rowku 0,300 / 0,300, nad kolkiem 0,500; pokrywka-plytka 0,300; garby: zaglebienie 0,400, do dna rowka 0,403, dZ 0,000; kolnierz nad wkladka 0,500; plytka obrocona o 90 / 180 / 270 st.: 59 / 58 / 57 kolizji (nie wchodzi) |

Sprawdzenia etapow A-C nie wchodza do raportu R58 (sa w `SPRAWDZ_iter15`). K-58 (kody) dla kompletu R58 nie istnieje - tabela kodow w sekcji 1 (arkusz `kody_plytek.md` bez zmian).

## 8. Dowod: 25 plikow R59 bez zmian

Porownanie SHA-256 z `Ramki/Ramki_pakiet/SHA256SUMS_2026-11-16_R59.txt` (po nazwie pliku): przed praca (MSI), po wszystkich przebiegach na PC (`Get-FileHash`, `<PC-katalog>\r58\Ramki\wyniki_v2`) i na koniec na MSI - 25 z 25 za kazdym razem.

| Plik | SHA-256 (= SHA256SUMS R59) |
|---|---|
| ramka_blat_v2.stl | 8c48856eb9addee2b37cfa5a03e5686ab7670bd92b724e488ccc8d8dd3a4b418 |
| ramka_korpus_P_v2.stl | aadb91c9364cf39f1f4062d328616aa518e474b957315ed4a941de4f935ab2b7 |
| ramka_korpus_W_v2.stl | bd55871c88cf2604c1c8efa5035148ba39c3803a0788015cc35548e8e9afff9a |
| ramka_plytka_okragla_poranna_n9_v2.stl | f9444e6f14e37d9d0bcc8ae84cfec5249146bce20420c53a86a73965727fd4c4 |
| ramka_plytka_okragla_poranna_v2.stl | e35835d7618e6665fdda84cbe2d65a3c7b46d7f9cef1e99141b42af2eb9e22c7 |
| ramka_plytka_okragla_wieczorna_n8_v2.stl | d5591f652ea1b6b23825abb5ad05ac12b78d17f6abb52946bd1a010ef5e4ff54 |
| ramka_plytka_okragla_wieczorna_v2.stl | aad8033e6c1d1f34b43825861d18e82b45599a76ebb453c294400a7713ebbd83 |
| ramka_plytka_poranna_n4_v2.stl | 20f15f2214f6c9a9baf2b4701e7f99bfbc5f739b6379398294e9f931b8763237 |
| ramka_plytka_poranna_n5_v2.stl | a275775b9c9b5ddd015b68659f213505bdd28b9476cad5e13405bef2df5b64d1 |
| ramka_plytka_poranna_n6_v2.stl | c44be370c8b9ad2b70f9e486c3f6f9d2b227b91f2a6544bfe14bf7e66bd65b21 |
| ramka_plytka_poranna_v2.stl | a306032651bbdb0c77693aa27f6314e8c5ede874d1e99b1fa73e158a1a83bc9f |
| ramka_plytka_wieczorna_n1_v2.stl | 3b0db5452a0cd9533464772c10b67c05fa7a006fcdb3d140a74af275e79946f7 |
| ramka_plytka_wieczorna_n2_v2.stl | b87026134b25cf32a84a231b73d5c4eb9fde4dfeb5b16b627cf09ccc3f29c999 |
| ramka_plytka_wieczorna_n3_v2.stl | 59e615d596771c6c0351284c710e94e406a965afef423ffeae5cd18ffa2c4dd3 |
| ramka_plytka_wieczorna_v2.stl | 604ef8f2079184460c3e059edde4849e9feeefeab39a755c18d0079ea1e561a9 |
| ramka_podkladka_panelu_05_v2.stl | 4260d1f1957f32d101cae5da2cf4634e24239caf738592edd7007fc0728ec6b4 |
| ramka_podkladka_panelu_1_v2.stl | e79a805121499f8d65b7d23ef6d2ae255549b4f55579ded7061b8996b91c9b78 |
| ramka_podkladka_panelu_2_v2.stl | 9c47aea4fbc946c16dab3813561d936745b88afde6092542de1d67a21656d5b5 |
| ramka_pokrywka_v2.stl | ad23444483ac95733e92169af00e5271d8fc3b19a91854e8c8acddf06c8cd454 |
| ramka_tulejka_dc_v2.stl | b393256cd8cafdac6d125d6f9f25647c5f94840d1bc5eb87941b436f510bcc00 |
| ramka_wkladka_v2.stl | f4196fbc640450998634f50caa86051f89df2cbb2c218e317f5c2b193e3ef92b |
| uklad_gniazd_okragla_poranna.json | b943e6c5dd54a8b3b35974908a3910bd654062bb659284a649ee68679174268e |
| uklad_gniazd_okragla_wieczorna.json | c07791f4bb976be2ad5eddaaeefe011b2384ea71e3fabd25cf55da690eb14a33 |
| uklad_gniazd_poranna.json | 46e474b759c4b78b7975fc8c5580c9916a4cc64c6a88cd4711b2207e3978b98b |
| uklad_gniazd_wieczorna.json | 7ae07ba861950724cf68ce9de0b45f3a05436089df8f73b3b4fc07bf2cc05869 |

Dlaczego to trwale: tryb R58 nie wola `wyczysc_wyniki` ani budowy etapow A-C; uklady R59 czyta z `zapisuj=False`; nowe typy plytek nie sa w `TYPY_PLYTEK`; zmiany w funkcjach wspolnych dzialaja tylko dla JSON z polami R58 (`cover_groove`, `key_slot`) albo dla nowych nazw czesci, a `zero_dodatnie` jest domyslnie wylaczone - wiec takze przyszly przebieg ALL zbuduje pliki etapow A-C tak jak dotad (z zastrzezeniem znanej niepowtarzalnosci `ramka_wkladka_v2.stl`). Arkusze R59 (`arkusz_wymiarow.md`, `arkusz_zamowienia.*`, `kody_plytek.md`), rendery, `.blend`, README i `do_v3.md` nie byly zapisywane (git: brak zmian w `wyniki_v2/arkusze`, `render`, `ramka_v2.blend`, `README.md`, `do_v3.md`).

## 9. Liczby projektu - zrealizowane bez zmian

Wszystkie liczby koordynatora przyjete wprost: o100, kieszenie o5,2 x 2,2 w osiach na r 45, rowek 1,0 x 0,8 na Z -2 (przez sciecie, 0,156 w srodku cieciwy), rowek klucza 3,6 x 2,5 od r 43, otwor wkladki 100,8 ze scieciem 49,756, faza 1 x 45 st. na calym obrysie otworu, wystep r 47, polki 10 x 10, kieszenie Halla 5,0 x 5,5, kanaly 2,5 x 1,0 / 2,5 x 1,5 (t_h = 50,4 - 45, t_k = zw x sqrt(2) - 45 + 5 x NADDATEK), kolek o3 x 2 z faza 0,5, wyciecie palcowe 30 (koniec bryly: odstepstwo 1 - bryla wyniku ta sama), scianka w osiach 2,0, dno 2,9, pokrywka 100,6 / 103,6 x 20, garby 25 / 155 / 205 / 335 st. Zadna scianka < 1,5, zadna kolizja, zadne sprawdzenie nie wymagalo zmiany wymiaru.

## 10. Odstepstwa (rejestr raportu R58_iter4, 7 wpisow)

1. Wyciecie palcowe wkladki okraglej: koniec bryly tnacej z parametrow -sqrt(47^2 - 15^2) + 5 x 0,1 = -44,042 zamiast "-44,0" ze zlecenia; za okregiem wystepu jest tylko wolny otwor, wiec bryla wyniku identyczna; bez nowego klucza. Informacyjnie.
2. Ilosci i materialy w osobnych kluczach `quantities_r58` / `materials_r58`: dopisanie do `quantities` zmieniloby arkusz zamowienia R59 i K-57 starych plikow. Do decyzji koordynatora (wlaczenie do arkusza w przebiegu ALL).
3. K-60 przy `--etap SPRAWDZ`: zrzut `parametry.json` w `arkusz_wymiarow.md` sprzed R58 uznawany za zgodny, gdy brakuje w nim tylko 14 kluczy R58 (kazda inna roznica nadal NIE). Bez tego wymaganie "SPRAWDZ dalej 0 NIE" i "arkusze bez zmian" byly sprzeczne. Do zatwierdzenia przez koordynatora (protokol K-60 juz z dopiskiem); po przebiegu ALL zrzut bedzie pelny i tolerancja przestanie byc potrzebna.
4. Sprawdzenia plytki ramkowej: K-61 (b) na Z -7,5 promieniami odsunietymi o +-4,9 (w osi lezy rowek klucza), K-63 nie dotyczy (K-64), K-09 bez kontroli odwrotnej dawnych rogow. Zapisane w protokole.
5. Numery n1-n6 wspolne z plytkami kwadratowymi (decyzja wlasciciela); `kody_plytek.md` nie generowany na nowo - tabela kodow w sekcji 1. Program stanowiska nie odrozni dzis okraglej n1 od kwadratowej n1 (osobna paczka).
6. Pokrywka okragla bez klucza: mozna ja zalozyc w dowolnym obrocie; garb nad scieciem plytki nie zahacza (czubek r 49,60 > sciecie 49,356) - wtedy trzymaja 3 garby. K-67 sprawdza polozenie nominalne (wyciecia z przodu i z tylu).
7. Zapis STL kompletu R58 z +0,0 zamiast -0,0 (`stl_kanoniczny(zero_dodatnie=True)` tylko w trybie R58): usuwa niepowtarzalnosc znaku zera w normalnych; pliki etapow A-C zapisywane bez zmian. Normalizacja dla wszystkich plikow zostaje w v3 (`do_v3.md` #9).

Dodatkowo (nie w rejestrze generatora): `ramka_wkladka_okragla_v2.stl` - jak `ramka_wkladka_v2.stl` - nie zawsze odtwarza sie bajtowo nawet po zapisie +0,0: w 1 z 4 przebiegow (#9) boolean EXACT dal wierzcholek przesuniety o 0,00085 mm (na krawedzi otworu na wysokosci polki, Z 2,5) i inna triangulacje 5 trojkatow; objetosc 22,419780 cm3 w obu wariantach, gabaryt identyczny, wszystkie K = ZAL w obu (R58_SPRAWDZ_iter2 i iter3). Oddany jest wariant 0ca13cd7..., ktory powstal w 3 przebiegach (#5, #7, #11); przy pakowaniu brac ten plik (nie przebudowywac), jak przy wkladce kwadratowej. Wg K-59: roznica SHA przy objetosci +-0,001 i gabarycie +-0,01 = ZAL z uwaga D.

## 11. Ryzyka

1. Pole skanowania niezmierzone (`scan_field_d` 100 DO_ZMIERZENIA, pomiar #12): plytka o100 = granica pola przy zalozeniu 100; jesli pole wyjdzie mniejsze, krawedz plytki i gniazda skrajne (promien obrysu 45,93 / 46,41) moga wypasc poza skan - ryzyko przyjete przez wlasciciela.
2. Sila zatrzasku pokrywki okraglej do sprawdzenia na pierwszym wydruku FDM (PETG): garby po luku na scianie kubka 1,5 (sztywniejszej obwodowo niz bok kwadratu), zaglebienie 0,4; jesli za mocno / za slabo - zmiana `cover_snap_bump` albo katow, nowy wydruk pokrywki (tania czesc druku wlasnego).
3. Program stanowiska nie zna jeszcze plytek okraglych n1-n6 (te same numery co kwadratowe; inne pozycje dolkow i magnesow): osobna paczka (modele `modele_plytek`, JSON z `magnet_pockets` / `key_slot`, rozroznienie ksztaltu).
4. Scianka ramy wkladki w osiach 2,0 (kwadratowa: 4,0) - zgodnie z zasada 4.8 (>= 1,5), ale wkladka jest sztywniejsza tylko dzieki wystepowi i polkom; MJF/SLS +-0,3 zostawia >= 1,4 w najgorszym razie lokalnie.
5. Rowek klucza: sufit 1,5 pod poziomem dna gniazd (dokladnie minimum 4.8). W rzucie zadne dno gniazda nie lezy nad rowkiem; najblizej dno rynienki wieczornej: 0,37 w poziomie i 1,5 w pionie (po przekatnej 1,54), w porannej 4,43 (gniazdo id 2) - tolerancja druku +-0,3 moze lokalnie zejsc ponizej 1,5.
6. Kieszenie magnesow 2,4 od krawedzi plytki (przy rowku pokrywki 1,6 w rzucie, rowek 3,3 wyzej) - wystarczajace wg 4.8; magnes wklejany od spodu.
7. Arkusz zamowienia, `kody_plytek.md`, `arkusz_wymiarow.md`, rendery i `.blend` nie zawieraja kompletu R58, dopoki koordynator nie zrobi przebiegu ALL z dolaczonymi czesciami.

## 12. Co dalej (koordynator, poza R58-A)

1. Recenzja R58 z siatek (10 STL, 2 JSON; K-64...K-67 wg protokolu 3b) - swieza subsesja.
2. Decyzja o odstepstwach 2, 3, 7 i o tym, czy tryb R58 ma zostac osobny, czy komplet wejdzie do etapow A/B (wtedy nowe arkusze, render, `.blend`, `kody_plytek.md` z n1-n6 okraglymi, K-58 i K-57 z `quantities_r58`).
3. Program stanowiska (plytki okragle n1-n6), dokumenty dla wlasciciela (zamowienie, budowa), pakiet i SHA256SUMS.
