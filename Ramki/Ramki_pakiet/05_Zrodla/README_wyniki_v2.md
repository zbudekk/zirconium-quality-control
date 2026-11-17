# Ramki świetlne — pliki v2

Wszystko w tym folderze generuje `ramka_generator.py` z `parametry.json` i `plan_ramki_v2.md` (R14). Plików nie edytuje się ręcznie (R28). Ostatni przebieg: etap C (R59), iteracja 2, raport `raport/raport_wykonawcy_R59_iter2.md` (sumy SHA‑256 wszystkich plików).

## Jak uruchomić

Pełny przebieg (części, sprawdzenia, `.blend`, rendery, arkusze; kilka minut — rendery Cycles):

```
cd <PC>\Desktop\Ramki
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P ramka_generator.py -- --etap ALL --iter 1
```

- `--etap A|B|C|ALL` buduje wszystko do etapu włącznie (A: płytki kwadratowe n1–n6, płytki okrągłe n8/n9 [R57] i pokrywka; B: + wkładka, blat, korpusy W i P; C/ALL: + tulejka DC, 3 podkładki panelu, `.blend` z materiałami, rendery, arkusze, README).
- `--etap SPRAWDZ --iter n` — tylko sprawdzenia K‑xx na plikach, które już są w `wyniki_v2/` (nic nie generuje poza raportem `raport_wykonawcy_SPRAWDZ_itern.md` i rzutami kontrolnymi).
- Wynik w logu: linia `[ramka] RAPORT … B=0 P=0 D=0`. Kod wyjścia 1 = błąd projektu (komunikat `[ramka] BLAD: …`).
- Powtarzalność (K‑59): w czystej kopii folderu (bez `wyniki_v2/`) to samo polecenie odtwarza wszystkie pliki; STL są bajtowo identyczne (kanoniczna kolejność trójkątów), z wyjątkiem `ramka_wkladka_v2.stl`: zależnie od przebiegu różni się znak zera w zapisanych normalnych albo przekątna w dwóch płaskich prostokątach fazy (te same wierzchołki, objętość i gabaryt). JSON gniazd powstaje z D6, gdy go nie ma.

## Jak zmienić parametr (R14, R28)

1. W `parametry.json` zmień `"value"` i ustaw `"status": "ZMIERZONE"` (pomiary: plan, sekcja 10). Nie dodawaj ani nie zmieniaj nazw kluczy — nieznany albo brakujący klucz zatrzymuje skrypt.
2. Wartości `LICZONE` (`panel_pcb_z`, `blat_top_z`, `korpus_h`, `panel_standoff_l`, `cover_inner_h`, `snap_pocket_z`, `snap_hook_z`, `blat_screw_z`, `label_pos_z`, `socket_zone_r` [R54]) przelicz ze wzoru w polu `wzor` i wpisz — skrypt porównuje (różnica > 0,01 = błąd).
3. Uruchom pełny przebieg (`--etap ALL`), potem recenzja. Żadnej ręcznej edycji STL.

## Pliki (SHA‑256 z chwili zapisu README; README, `do_v3.md` i raport — w raporcie, sekcja 2)

| Plik | Rozmiar [B] | SHA‑256 |
|---|---|---|
| `json/uklad_gniazd_wieczorna.json` | 4305 | `7ae07ba861950724cf68ce9de0b45f3a05436089df8f73b3b4fc07bf2cc05869` |
| `json/uklad_gniazd_poranna.json` | 5106 | `46e474b759c4b78b7975fc8c5580c9916a4cc64c6a88cd4711b2207e3978b98b` |
| `json/uklad_gniazd_okragla_wieczorna.json` | 4243 | `c07791f4bb976be2ad5eddaaeefe011b2384ea71e3fabd25cf55da690eb14a33` |
| `json/uklad_gniazd_okragla_poranna.json` | 5039 | `b943e6c5dd54a8b3b35974908a3910bd654062bb659284a649ee68679174268e` |
| `stl/ramka_plytka_wieczorna_v2.stl` | 954684 | `604ef8f2079184460c3e059edde4849e9feeefeab39a755c18d0079ea1e561a9` |
| `stl/ramka_plytka_wieczorna_n1_v2.stl` | 946584 | `3b0db5452a0cd9533464772c10b67c05fa7a006fcdb3d140a74af275e79946f7` |
| `stl/ramka_plytka_wieczorna_n2_v2.stl` | 956284 | `b87026134b25cf32a84a231b73d5c4eb9fde4dfeb5b16b627cf09ccc3f29c999` |
| `stl/ramka_plytka_wieczorna_n3_v2.stl` | 967084 | `59e615d596771c6c0351284c710e94e406a965afef423ffeae5cd18ffa2c4dd3` |
| `stl/ramka_plytka_poranna_v2.stl` | 1099784 | `a306032651bbdb0c77693aa27f6314e8c5ede874d1e99b1fa73e158a1a83bc9f` |
| `stl/ramka_plytka_poranna_n4_v2.stl` | 1095984 | `20f15f2214f6c9a9baf2b4701e7f99bfbc5f739b6379398294e9f931b8763237` |
| `stl/ramka_plytka_poranna_n5_v2.stl` | 1113784 | `a275775b9c9b5ddd015b68659f213505bdd28b9476cad5e13405bef2df5b64d1` |
| `stl/ramka_plytka_poranna_n6_v2.stl` | 1107984 | `c44be370c8b9ad2b70f9e486c3f6f9d2b227b91f2a6544bfe14bf7e66bd65b21` |
| `stl/ramka_plytka_okragla_wieczorna_v2.stl` | 971484 | `aad8033e6c1d1f34b43825861d18e82b45599a76ebb453c294400a7713ebbd83` |
| `stl/ramka_plytka_okragla_wieczorna_n8_v2.stl` | 985784 | `d5591f652ea1b6b23825abb5ad05ac12b78d17f6abb52946bd1a010ef5e4ff54` |
| `stl/ramka_plytka_okragla_poranna_v2.stl` | 1115584 | `e35835d7618e6665fdda84cbe2d65a3c7b46d7f9cef1e99141b42af2eb9e22c7` |
| `stl/ramka_plytka_okragla_poranna_n9_v2.stl` | 1128884 | `f9444e6f14e37d9d0bcc8ae84cfec5249146bce20420c53a86a73965727fd4c4` |
| `stl/ramka_pokrywka_v2.stl` | 41084 | `ad23444483ac95733e92169af00e5271d8fc3b19a91854e8c8acddf06c8cd454` |
| `arkusze/kody_plytek.md` | 2402 | `bd1ea418acbbae4c7ba8027d38adbc8daa9b4fa6a577c29bdbc9dd1b7a22c732` |
| `stl/ramka_wkladka_v2.stl` | 90384 | `f4196fbc640450998634f50caa86051f89df2cbb2c218e317f5c2b193e3ef92b` |
| `stl/ramka_blat_v2.stl` | 284684 | `8c48856eb9addee2b37cfa5a03e5686ab7670bd92b724e488ccc8d8dd3a4b418` |
| `stl/ramka_korpus_W_v2.stl` | 939984 | `bd55871c88cf2604c1c8efa5035148ba39c3803a0788015cc35548e8e9afff9a` |
| `stl/ramka_korpus_P_v2.stl` | 895184 | `aadb91c9364cf39f1f4062d328616aa518e474b957315ed4a941de4f935ab2b7` |
| `stl/ramka_tulejka_dc_v2.stl` | 88584 | `b393256cd8cafdac6d125d6f9f25647c5f94840d1bc5eb87941b436f510bcc00` |
| `stl/ramka_podkladka_panelu_05_v2.stl` | 31584 | `4260d1f1957f32d101cae5da2cf4634e24239caf738592edd7007fc0728ec6b4` |
| `stl/ramka_podkladka_panelu_1_v2.stl` | 31584 | `e79a805121499f8d65b7d23ef6d2ae255549b4f55579ded7061b8996b91c9b78` |
| `stl/ramka_podkladka_panelu_2_v2.stl` | 31584 | `9c47aea4fbc946c16dab3813561d936745b88afde6092542de1d67a21656d5b5` |
| `ramka_v2.blend` | 14628298 | `920ca516a8a4de748ecc7155ec29b6b8be7222530513babf9876e51df846f367` |
| `render/render_rozstrzelony.png` | 1746327 | `c44e7a148bff89ab2c101b65c15e979b4ad7085f718f530742d3e01440bd6ed9` |
| `render/render_zlozony.png` | 1760469 | `4e80b34c3615a36276983d7b7a8e2dcf35083c553897a81b62bfe467fb42802b` |
| `render/render_plytki.png` | 1914480 | `958e830b3ee60e420c3ec12205f6c58e6e56e631b98cfdb7ff4bc69f08eb23e1` |
| `arkusze/arkusz_zamowienia.csv` | 3487 | `da490eba92af1ec252dc0c56c9ed7e57a790551e3c1b8ae387171efd6e95d0f3` |
| `arkusze/arkusz_zamowienia.md` | 5611 | `5419d21b31b2513f2967ef79c8a31e5ebca14d9038dd1fc643df4f671da92a11` |
| `arkusze/arkusz_wymiarow.md` | 61842 | `ff6c2850556f3d8b5a075390e7cc0b562eef895ea57fc2c1f0aec10187f23ed3` |

Dodatkowo: `raport/` (raporty wykonawcy, notatki, rzuty kontrolne), `do_v3.md` (lista drobnych).

## Rejestr odstępstw (z raportu tego przebiegu)

| # | Czego dotyczy | Co zrobiono inaczej | Dlaczego | Wymaga zatwierdzenia? |
|---|---|---|---|---|
| 1 | R57 / `plate_round_d` (zadanie: 96; decyzja nadzoru 2.11: 100) | płytka okrągła ø100 = granica pola skanowania; gniazda jak płytka kwadratowa tego typu, w kole 47 | decyzja 2.11 na układzie R54: przy ø96 ścianka obrys górny rynienki tylnej porannej (r 46,93) i stożków znaczników (r 44,43 + 2,5) do krawędzi = 1,07 (do początku fazy 0,57) < 1,5 (reguła 4.8, K‑16); ø98 dawało 1,57–2,07; przy ø100 ścianka do krawędzi 2,57; po R59 (jedna rynienka przednia, układ W‑b / P‑e) ścianki do krawędzi są większe — liczby w K‑16 tego raportu; kwadrat ma rogi na promieniu 67,9, więc ø100 mieści się w skanerze wszędzie tam, gdzie kwadrat | tak — właściciel (ZAŁOŻENIE nadzoru) |
| 2 | R57 / `round_flat_w` (zadanie: 8; decyzja nadzoru 2.11: 16) | ścięcie o cięciwie 16: płaszczyzna 49.356 od środka, głębokość 0.644 | cięciwa 8 dawała głębokość 0,16 (mniej niż faza 0,5 i tolerancja ±0,3 — niewidoczne); 16 daje 0.64 ≥ `round_flat_depth_min` 0.6 przy ściance od płaszczyzny ścięcia do obrysów ≥ 3 (K‑61 e, f; liczba po R59 w K‑61 tego raportu); w decyzji 2.11 (układ R54) 20 odpadało (ścianka 1,3) | tak — właściciel (ZAŁOŻENIE nadzoru) |
| 3 | R57 / `code_dimples_round` (zadanie: wzdłuż lewej krawędzi; nadzór 2.11: zaakceptowane per typ) | pozycje per typ z `parametry.json`: wieczorna A (-4.5, -43.5), B (-1.5, -43.5), C (1.5, -43.5), D (4.5, -43.5); poranna A (36.5, 18.5), B (36.5, 21.5), C (43, 6), D (43, 9) | R57 (układ R54): przegląd siatki 0,5 mm — żadna linia 4 dołków o rozstawie 3 nie mieściła się w kole r 44 wspólnie dla obu układów gniazd ani przy lewej krawędzi (gniazda sięgają x −45); R59: wieczorna bez zmian (rząd przed rynienką przednią); poranna przeniesiona z kolumny x 30,5 (y −31…−22) — rynienka układu P‑e leży w y −35,3 i rząd przed nią się nie mieści, więc dwie pary z prawej strony (policzone `narzedzia/uklad_kolo_R59.js`); promienie i ścianki do gniazd, stożków i krawędzi: K‑62 tego raportu; program czyta pozycje z JSON `code_dimples` | nie — ZAŁOŻENIE zaakceptowane przez nadzór 2.11; pozycje porannej zmienione decyzją właściciela G0 14.11.2026 (R59, wariant P‑e) |
| 4 | R57 / `number_pos_round` (nadzór 2.11: zaakceptowane) | cyfra reliefu na okrągłych w kole 47 (z `parametry.json`): wieczorna (35, -26.5), poranna (-44, 5.5) | dawne miejsce kwadratu (39,5, −44,5) leży poza kołem (promień 59,6); obrys cyfry 5 × 3,6 w kole 47 i ≥ 3 od gniazd; R59: wieczorna bez zmian, poranna przeniesiona z (36,5, −24,5) na lewą stronę (dawne miejsce koliduje z gniazdem ø12,5 układu P‑e w (31; −19,55)); odstępy obrysu cyfry od gniazd, dołków, stożków i koła 47 liczy `narzedzia/weryfikuj_uklad_R59.js` (generator sprawdza tylko wysokość reliefu, K‑13) | nie — ZAŁOŻENIE zaakceptowane przez nadzór 2.11; pozycja porannej zmieniona decyzją właściciela G0 14.11.2026 (R59, wariant P‑e); `null` = bez cyfry |
| 5 | R57 / K‑08 na okrągłych | sonda zaokrąglonego końca rynienki na 45° od środka półokręgu (w/2 + 0,6) zamiast narożnika prostokąta | R57: sonda wprowadzona przy ø96/98, gdy narożnik (x + l/2 − 0,5, y + w/2 − 0,5) rynienek tylnych układu R54 (promień 48,5–48,6) leżał poza obrysem; przy ø100 narożnik leży w płytce (recenzja R57‑B D1, zapis w protokole K‑08), a po R59 rynienka jest tylko z przodu (narożnik w promieniu 37,5 / 38,2); protokół K‑08 wymienia dla płytek okrągłych obie sondy, generator wykonuje na nich nadal tylko sondę na 45° (kod sprawdzeń bez zmian w R59); rozróżnia ona koniec prostokątny od zaokrąglonego tak samo | nie — informacyjnie (zapis w protokole K‑08) |
| 6 | R57 / pliki bazowe kwadratowe (`ramka_plytka_wieczorna_v2.stl`, `ramka_plytka_poranna_v2.stl`) | plik bazowy = wszystkie 4 dołki (A+B+C+D), więc bazowe kwadratowe dostały dołek D (−45, −27) i zmieniły bajty | zasada „bazowy = wszystkie dołki” (4.1 p. 5, K‑11) rozszerzona o bit D; pliki bazowe nie są drukowane ani w pakiecie; n1–n6 bez bitu D (w R57 bajtowo identyczne z R56; po R59 wszystkie pliki płytek mają nowy układ gniazd i nowe SHA) | tak — albo bazowe bez D (wtedy K‑11 bazowy A+B+C) |
| 7 | R57 / boolean i triangulacja płytek okrągłych | otwory ø3 cięte w drugiej różnicy; ściany poziome triangulowane Delaunayem z ograniczeniami (CDT) | jedna różnica ze wszystkimi bryłami zostawiała w bazowej okrągłej wieczornej 3 zbędne ściany na dnie otworów (K‑03: 514 przecięć); kwadratowe bez zmian w kolejności brył i triangulacji (w R57 SHA płytek kwadratowych = R56; po R59 nowe SHA wynikają tylko z nowego układu gniazd) | nie — informacyjnie |
| 8 | R59 / `ev_rows`, `mo_rows` (decyzja właściciela G0 14.11.2026: warianty W‑b i P‑e) | układ gniazd z `parametry.json`: wieczorna 1 × rynienka 60 × 15 + 6 × ø12 + 12 × ø15; poranna 1 × rynienka 50 × 13 + 20 × ø12,5 + 3 × ø15; na każdej płytce jedna rynienka (przednia) | rząd mieszany płytki porannej (ø12,5 i ø15 obok siebie) jest zapisany jako dwa wpisy o różnym y; numery id (R13: rzędami od przodu, w rzędzie od prawej) idą wtedy po y wpisu — najpierw gniazda wpisu o mniejszym y, potem drugiego; id całego układu są inne niż w R54 (wyniki programu ze starego układu nie są porównywalne po numerze gniazda) | nie — informacyjnie (plan D6 i Z20 [R59]) |
| 9 | R47 / bryła zastępcza gniazda DC: grubość nakrętki | grubość nakrętki = `dc_pocket_wall` (2.0) | plan podaje „nakrętka ø15 × 2”, grubość bez własnego klucza; wartość liczbowo równa | nie — przyjęte informacyjnie (R51) |
| 10 | bryła zastępcza `proxy_odbiornik_usb` (tylko korpus P) | położenie przyjęte: wystaje 19 mm w +X od krawędzi portów Pi (x = 35), oś y = 0, Z 8…14 | plan mówi tylko „dolny port USB Pi”; pozycji portu nie ma w parametrach | nie — przyjęte informacyjnie (R51) |
| 11 | protokół K‑57 / arkusz zamówienia: wzór kosztu pokazowego | najtańszy = obj × szt × `cost_rate_min`…`cost_rate_max`; pokazowy = najtańszy × `cost_dye_factor` × `cost_smooth_factor` dla korpusu i blatu (Z19), części białe bez mnożników | opis K‑57 („koszt_max … × dye dla grafitu × smooth dla korpusu/blatu”) jest niejednoznaczny; przyjęto wzór z planu 12.1 i sekcji 11, zapisany pod tabelą arkusza | nie — informacyjnie |
| 12 | render rozstrzelony (prompt: rozsunięcie wzdłuż Z) | gniazda DC i USB oraz tulejka wysunięte w lewo ekranu (280 mm) przy Z korpusu | w izometrii części wewnątrz korpusu zasłaniają ściany i warstwy wyżej; lista §11 wymaga ich widoczności (K‑60 mierzy widoczność) | nie — informacyjnie |
| 13 | bryła zastępcza gniazda DC z tulejką (K‑53) | bez gwintu ø8 w otworze tulejki | średnica gwintu gniazda nie ma klucza (wynik pomiaru #16) | nie — informacyjnie (do_v3) |
| 14 | plan 4.4 p. 3 i 4.11 (opis) | kołnierz blatu na 95,0…97,0 (z `parametry.json`, R48) | tekst planu: „zrośnięte z kołnierzem 95,2…97,2”, „wnętrze kołnierza 97,2” — opis sprzed R48; STL bez wpływu | nie — do poprawy opisu w planie (do_v3) |
| 15 | K‑59 / `ramka_wkladka_v2.stl` | brak zmian; SHA wkładki może się różnić między przebiegami | różnica tylko w znaku zera (−0,0 / +0,0) zapisanych normalnych (wierzchołki i trójkąty identyczne); normalizacja w `stl_kanoniczny` zmieniłaby bajty wszystkich STL, także zatwierdzonych płytek | nie — rozstrzygnięte przez nadzór po C iter1 (K‑59 kanonicznie; normalizacja w v3, `do_v3.md` #9) |
| 16 | protokół K‑52b, plan 4.x (tulejka DC) — opis | walec ø11,85 z `parametry.json` (R52: `dc_hole_d` − 0,15, luz 0,075/stronę w otworze ø12, reguła 4.8 „wciskane”) | tekst K‑52b („walec ø12 × 2”, „walec r 6”) i opis pliku w planie („walec ø`dc_bush_outer_d` 12”) sprzed R52; sondy K‑52b (r 5,5 W, r 6,8 POZA) bez zmian; w złożeniu walec nie przenika ściany (luz geometryczny 0,075/stronę, K‑53 bez przecięcia) | nie — do poprawy opisu w protokole i planie |
