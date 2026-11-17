# Ramki świetlne — pliki v2

Wszystko w tym folderze generuje `ramka_generator.py` z `parametry.json` i `plan_ramki_v2.md` (R14). Plików nie edytuje się ręcznie (R28). Ostatni przebieg: etap C (R57), iteracja 2, raport `raport/raport_wykonawcy_R57_iter2.md` (sumy SHA‑256 wszystkich plików).

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
| `json/uklad_gniazd_wieczorna.json` | 4465 | `88ebc12701a6ab2c775e800062b70de232375099624d270dfe00b0bf881eb40c` |
| `json/uklad_gniazd_poranna.json` | 6449 | `36648acc22be6ae45187bc6c22bf7fcf00793144de10e2614c416cd5ef2a9e8d` |
| `json/uklad_gniazd_okragla_wieczorna.json` | 4403 | `260f807c630211dcd3c1b552cded03838d1367156c856fc51f3a3f7ec12f0743` |
| `json/uklad_gniazd_okragla_poranna.json` | 6389 | `5adcc977dd9b456e5261d1e2225bc386def23a165d79de124b5733fb9ef43d53` |
| `stl/ramka_plytka_wieczorna_v2.stl` | 919284 | `fa77f61d637b61c99f9a9545afb13f811b2053faba8ac9c38abe73c9db2320db` |
| `stl/ramka_plytka_wieczorna_n1_v2.stl` | 911684 | `515d32d3dd8a69ae0a94d293a639b201f2d9ce9af19df664ad1b44b59408f775` |
| `stl/ramka_plytka_wieczorna_n2_v2.stl` | 921784 | `360cff9ddd6bbcf8a84b463fed930532612a38118006f1550c2df01b02fa852d` |
| `stl/ramka_plytka_wieczorna_n3_v2.stl` | 932284 | `2fc7040e212ace4a8efda17f61909ca09563009513adcd82ecf5bcaac3e98aaf` |
| `stl/ramka_plytka_poranna_v2.stl` | 1191384 | `dd00fcdab0270402af978c1b5f4928a6351080daf3bedf8b918ae7e2faa26306` |
| `stl/ramka_plytka_poranna_n4_v2.stl` | 1189084 | `a8d07cbeb0dafc0e55d3fe2fe516c7d3e854a6259bce587785b796d34b54c65e` |
| `stl/ramka_plytka_poranna_n5_v2.stl` | 1204884 | `159503ca4cd66b90a1e2441cae64016901ed83390b48a27345f9484ac1a05830` |
| `stl/ramka_plytka_poranna_n6_v2.stl` | 1200984 | `0d5d712d42084a19846f24d385484d01b2254c5c1ec3945d71cfd3493816f15e` |
| `stl/ramka_plytka_okragla_wieczorna_v2.stl` | 935784 | `3ca8178262f7f1f253480ca1d49adbbccf2db3648647814ec2390311e5553ace` |
| `stl/ramka_plytka_okragla_wieczorna_n8_v2.stl` | 950484 | `c4c8a18d0b83fd2a2903f5d782188a8de4827ee07c55dca9df7bd0d8e4a37d32` |
| `stl/ramka_plytka_okragla_poranna_v2.stl` | 1206384 | `713aef6c0cef1dc2fc3b3809ce3756557b41b0cc4268c85166e985f18f74e0dd` |
| `stl/ramka_plytka_okragla_poranna_n9_v2.stl` | 1217584 | `a87bc6c5f8f0323bc202e5ebfeab6be6d7c8432beba6aafe4a8372d70666e2be` |
| `stl/ramka_pokrywka_v2.stl` | 41084 | `ad23444483ac95733e92169af00e5271d8fc3b19a91854e8c8acddf06c8cd454` |
| `arkusze/kody_plytek.md` | 2408 | `7e5b4d2fb126367c7e17c58698a9537524d67044d752c51e39fe966433bbcb15` |
| `stl/ramka_wkladka_v2.stl` | 90384 | `92e1e5cd6038f70d6d09640d0ddfd9d347afcc1b42f2bdced67787c5667f0bf2` |
| `stl/ramka_blat_v2.stl` | 284684 | `8c48856eb9addee2b37cfa5a03e5686ab7670bd92b724e488ccc8d8dd3a4b418` |
| `stl/ramka_korpus_W_v2.stl` | 939984 | `bd55871c88cf2604c1c8efa5035148ba39c3803a0788015cc35548e8e9afff9a` |
| `stl/ramka_korpus_P_v2.stl` | 895184 | `aadb91c9364cf39f1f4062d328616aa518e474b957315ed4a941de4f935ab2b7` |
| `stl/ramka_tulejka_dc_v2.stl` | 88584 | `b393256cd8cafdac6d125d6f9f25647c5f94840d1bc5eb87941b436f510bcc00` |
| `stl/ramka_podkladka_panelu_05_v2.stl` | 31584 | `4260d1f1957f32d101cae5da2cf4634e24239caf738592edd7007fc0728ec6b4` |
| `stl/ramka_podkladka_panelu_1_v2.stl` | 31584 | `e79a805121499f8d65b7d23ef6d2ae255549b4f55579ded7061b8996b91c9b78` |
| `stl/ramka_podkladka_panelu_2_v2.stl` | 31584 | `9c47aea4fbc946c16dab3813561d936745b88afde6092542de1d67a21656d5b5` |
| `ramka_v2.blend` | 14936678 | `5559fad05410e1cc9ab53ca337eab56a829c4a7a2cd9c0ec17fb1eac949c98a0` |
| `render/render_rozstrzelony.png` | 1746639 | `ec1b76a01ca41c6e2e082c72f4cca08b5a66fef198b78ed172cb34f5ab2f5b59` |
| `render/render_zlozony.png` | 1759258 | `e6fbd603fb78c26141df8ee420f393099c19a61309f780efed6c6cb45f4b7cb1` |
| `render/render_plytki.png` | 1909348 | `562da9e514d6b88cdd8a7dc1af6babd683d1f8448baf0c7bcb1225f0c4c5bcf5` |
| `arkusze/arkusz_zamowienia.csv` | 3487 | `53832fe3a2cbb27c961506c25b4b3960b02c3ae2cd85f8a11789400ba8d504d0` |
| `arkusze/arkusz_zamowienia.md` | 5611 | `47b05d926e41bdfdd92914448fd15a26cd50432a3d9c5d1a2042615e76c34bf9` |
| `arkusze/arkusz_wymiarow.md` | 57541 | `f29ec1913f63e5e7056b6bc3f8a7416045fc922a7e328f66bb2a5e5c668df5b3` |

Dodatkowo: `raport/` (raporty wykonawcy, notatki, rzuty kontrolne), `do_v3.md` (lista drobnych).

## Rejestr odstępstw (z raportu tego przebiegu)

| # | Czego dotyczy | Co zrobiono inaczej | Dlaczego | Wymaga zatwierdzenia? |
|---|---|---|---|---|
| 1 | tabela 3 planu / `plate_round_d` | przyjęto 100 (parametry.json) zamiast 98 z tabeli 3 | sprzeczność plan ↔ JSON | tak |
| 2 | tabela 3 planu / `round_flat_w` | przyjęto 16 (parametry.json) zamiast 8 z tabeli 3 | sprzeczność plan ↔ JSON | tak |
| 3 | R57 / `plate_round_d` (zadanie: 96; decyzja nadzoru 2.11: 100) | płytka okrągła ø100 = granica pola skanowania; gniazda jak R54 w kole 47 | przy ø96 ścianka obrys górny rynienki tylnej porannej (r 46,93) i stożków znaczników (r 44,43 + 2,5) do krawędzi = 1,07 (do początku fazy 0,57) < 1,5 (reguła 4.8, K‑16); ø98 dawało 1,57–2,07; przy ø100 ścianka do krawędzi 2,57 (K‑16); kwadrat ma rogi na promieniu 67,9, więc ø100 mieści się w skanerze wszędzie tam, gdzie kwadrat | tak — właściciel (ZAŁOŻENIE nadzoru) |
| 4 | R57 / `round_flat_w` (zadanie: 8; decyzja nadzoru 2.11: 16) | ścięcie o cięciwie 16: płaszczyzna 49.356 od środka, głębokość 0.644 | cięciwa 8 dawała głębokość 0,16 (mniej niż faza 0,5 i tolerancja ±0,3 — niewidoczne); 16 daje 0.64 ≥ `round_flat_depth_min` 0.6 przy ściance od płaszczyzny ścięcia do obrysów ≥ 3 (K‑61 e, f); 20 odpada (ścianka 1,3) | tak — właściciel (ZAŁOŻENIE nadzoru) |
| 5 | R57 / `code_dimples_round` (zadanie: wzdłuż lewej krawędzi; nadzór 2.11: zaakceptowane per typ) | pozycje per typ: wieczorna rząd y −43,5 (x −4,5…4,5) przed rynienką przednią; poranna kolumna x 30,5 (y −31…−22) przód‑prawo | przegląd siatki 0,5 mm: żadna linia 4 dołków o rozstawie 3 nie mieści się w kole r 44 wspólnie dla obu układów gniazd ani przy lewej krawędzi (gniazda sięgają x −45); ścianki: do gniazd 3,50 / 3,62, do stożków 31,9 / 51,0, promień 43,73 / 43,49, do krawędzi 5,27 / 5,35 (ø100); program czyta pozycje z JSON `code_dimples` | nie — ZAŁOŻENIE zaakceptowane przez nadzór 2.11 (właściciel może cofnąć) |
| 6 | R57 / `number_pos_round` (nadzór 2.11: zaakceptowane) | cyfra reliefu na okrągłych w kole 47: wieczorna (35, −26,5), poranna (36,5, −24,5) | dawne miejsce (39,5, −44,5) leży poza kołem (promień 59,6); obrys cyfry 5 × 3,6 w promieniu ≤ 46,9, odstęp od gniazd ≥ 3,0, od dołków ≥ 3,2, od płaszczyzny ścięcia 2,8 / 3,2 | nie — ZAŁOŻENIE zaakceptowane przez nadzór 2.11 (właściciel może cofnąć; `null` = bez cyfry) |
| 7 | R57 / K‑08 na okrągłych | sonda zaokrąglonego końca rynienki na 45° od środka półokręgu (w/2 + 0,6) zamiast narożnika prostokąta | narożnik (x + l/2 − 0,5, y + w/2 − 0,5) rynienek tylnych leży w promieniu 48,5–48,6, czyli poza obrysem okrągłym (sonda z protokołu niewykonalna); nowa sonda rozróżnia koniec prostokątny od zaokrąglonego tak samo | nie — informacyjnie (zapis w protokole K‑08) |
| 8 | R57 / pliki bazowe kwadratowe (`ramka_plytka_wieczorna_v2.stl`, `ramka_plytka_poranna_v2.stl`) | plik bazowy = wszystkie 4 dołki (A+B+C+D), więc bazowe kwadratowe dostały dołek D (−45, −27) i zmieniły bajty | zasada „bazowy = wszystkie dołki” (4.1 p. 5, K‑11) rozszerzona o bit D; pliki bazowe nie są drukowane ani w pakiecie; n1–n6 bez bitu D — bajtowo identyczne z R56 | tak — albo bazowe bez D (wtedy K‑11 bazowy A+B+C) |
| 9 | R57 / boolean i triangulacja płytek okrągłych | otwory ø3 cięte w drugiej różnicy; ściany poziome triangulowane Delaunayem z ograniczeniami (CDT) | jedna różnica ze wszystkimi bryłami zostawiała w bazowej okrągłej wieczornej 3 zbędne ściany na dnie otworów (K‑03: 514 przecięć); kwadratowe bez zmian w kolejności brył i triangulacji (SHA R56 bez zmian) | nie — informacyjnie |
| 10 | R47 / bryła zastępcza gniazda DC: grubość nakrętki | grubość nakrętki = `dc_pocket_wall` (2.0) | plan podaje „nakrętka ø15 × 2”, grubość bez własnego klucza; wartość liczbowo równa | nie — przyjęte informacyjnie (R51) |
| 11 | bryła zastępcza `proxy_odbiornik_usb` (tylko korpus P) | położenie przyjęte: wystaje 19 mm w +X od krawędzi portów Pi (x = 35), oś y = 0, Z 8…14 | plan mówi tylko „dolny port USB Pi”; pozycji portu nie ma w parametrach | nie — przyjęte informacyjnie (R51) |
| 12 | protokół K‑57 / arkusz zamówienia: wzór kosztu pokazowego | najtańszy = obj × szt × `cost_rate_min`…`cost_rate_max`; pokazowy = najtańszy × `cost_dye_factor` × `cost_smooth_factor` dla korpusu i blatu (Z19), części białe bez mnożników | opis K‑57 („koszt_max … × dye dla grafitu × smooth dla korpusu/blatu”) jest niejednoznaczny; przyjęto wzór z planu 12.1 i sekcji 11, zapisany pod tabelą arkusza | nie — informacyjnie |
| 13 | render rozstrzelony (prompt: rozsunięcie wzdłuż Z) | gniazda DC i USB oraz tulejka wysunięte w lewo ekranu (280 mm) przy Z korpusu | w izometrii części wewnątrz korpusu zasłaniają ściany i warstwy wyżej; lista §11 wymaga ich widoczności (K‑60 mierzy widoczność) | nie — informacyjnie |
| 14 | bryła zastępcza gniazda DC z tulejką (K‑53) | bez gwintu ø8 w otworze tulejki | średnica gwintu gniazda nie ma klucza (wynik pomiaru #16) | nie — informacyjnie (do_v3) |
| 15 | plan 4.4 p. 3 i 4.11 (opis) | kołnierz blatu na 95,0…97,0 (z `parametry.json`, R48) | tekst planu: „zrośnięte z kołnierzem 95,2…97,2”, „wnętrze kołnierza 97,2” — opis sprzed R48; STL bez wpływu | nie — do poprawy opisu w planie (do_v3) |
| 16 | K‑59 / `ramka_wkladka_v2.stl` | brak zmian; SHA wkładki może się różnić między przebiegami | różnica tylko w znaku zera (−0,0 / +0,0) zapisanych normalnych (wierzchołki i trójkąty identyczne); normalizacja w `stl_kanoniczny` zmieniłaby bajty wszystkich STL, także zatwierdzonych płytek | nie — rozstrzygnięte przez nadzór po C iter1 (K‑59 kanonicznie; normalizacja w v3, `do_v3.md` #9) |
| 17 | protokół K‑52b, plan 4.x (tulejka DC) — opis | walec ø11,85 z `parametry.json` (R52: `dc_hole_d` − 0,15, luz 0,075/stronę w otworze ø12, reguła 4.8 „wciskane”) | tekst K‑52b („walec ø12 × 2”, „walec r 6”) i opis pliku w planie („walec ø`dc_bush_outer_d` 12”) sprzed R52; sondy K‑52b (r 5,5 W, r 6,8 POZA) bez zmian; w złożeniu walec nie przenika ściany (luz geometryczny 0,075/stronę, K‑53 bez przecięcia) | nie — do poprawy opisu w protokole i planie |
