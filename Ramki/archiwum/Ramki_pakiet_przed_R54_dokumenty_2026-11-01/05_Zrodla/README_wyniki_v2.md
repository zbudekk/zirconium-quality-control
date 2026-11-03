# Ramki świetlne — pliki v2

Wszystko w tym folderze generuje `ramka_generator.py` z `parametry.json` i `plan_ramki_v2.md` (R14). Plików nie edytuje się ręcznie (R28). Ostatni przebieg: etap C, iteracja 5, raport `raport/raport_wykonawcy_C_iter5.md` (sumy SHA‑256 wszystkich plików).

## Jak uruchomić

Pełny przebieg (części, sprawdzenia, `.blend`, rendery, arkusze; kilka minut — rendery Cycles):

```
cd <PC>\Desktop\Ramki
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P ramka_generator.py -- --etap ALL --iter 1
```

- `--etap A|B|C|ALL` buduje wszystko do etapu włącznie (A: płytki i pokrywka; B: + wkładka, blat, korpusy W i P; C/ALL: + tulejka DC, 3 podkładki panelu, `.blend` z materiałami, rendery, arkusze, README).
- `--etap SPRAWDZ --iter n` — tylko sprawdzenia K‑xx na plikach, które już są w `wyniki_v2/` (nic nie generuje poza raportem `raport_wykonawcy_SPRAWDZ_itern.md` i rzutami kontrolnymi).
- Wynik w logu: linia `[ramka] RAPORT … B=0 P=0 D=0`. Kod wyjścia 1 = błąd projektu (komunikat `[ramka] BLAD: …`).
- Powtarzalność (K‑59): w czystej kopii folderu (bez `wyniki_v2/`) to samo polecenie odtwarza wszystkie pliki; STL są bajtowo identyczne (kanoniczna kolejność trójkątów), z wyjątkiem `ramka_wkladka_v2.stl`: zależnie od przebiegu różni się znak zera w zapisanych normalnych albo przekątna w dwóch płaskich prostokątach fazy (te same wierzchołki, objętość i gabaryt). JSON gniazd powstaje z D6, gdy go nie ma.

## Jak zmienić parametr (R14, R28)

1. W `parametry.json` zmień `"value"` i ustaw `"status": "ZMIERZONE"` (pomiary: plan, sekcja 10). Nie dodawaj ani nie zmieniaj nazw kluczy — nieznany albo brakujący klucz zatrzymuje skrypt.
2. Wartości `LICZONE` (`panel_pcb_z`, `blat_top_z`, `korpus_h`, `panel_standoff_l`, `cover_inner_h`, `snap_pocket_z`, `snap_hook_z`, `blat_screw_z`, `label_pos_z`) przelicz ze wzoru w polu `wzor` i wpisz — skrypt porównuje (różnica > 0,01 = błąd).
3. Uruchom pełny przebieg (`--etap ALL`), potem recenzja. Żadnej ręcznej edycji STL.

## Pliki (SHA‑256 z chwili zapisu README; README, `do_v3.md` i raport — w raporcie, sekcja 2)

| Plik | Rozmiar [B] | SHA‑256 |
|---|---|---|
| `json/uklad_gniazd_wieczorna.json` | 5230 | `83779187c2cf7259c8fd31ef8a3616242f68fae001bc9fb829513f516fbe6067` |
| `json/uklad_gniazd_poranna.json` | 6988 | `3d6aa7ab225e8233ba6bd34f0d670285684d954c94640cf371ee6d6589bca367` |
| `stl/ramka_plytka_wieczorna_v2.stl` | 1099684 | `f02aed867a600d93e98ea319c82b09f219c52dca6f38ded3d01066567e7e4d3b` |
| `stl/ramka_plytka_wieczorna_n1_v2.stl` | 1097884 | `b2803c829885795b7a06e9d2597a1de6080bdec459e426238d8cd9c05a6e8b52` |
| `stl/ramka_plytka_wieczorna_n2_v2.stl` | 1106884 | `8bab264ca661b8d95f8d5f99a76a63956b6722f8d330d60b52bc1f0d4585b82e` |
| `stl/ramka_plytka_wieczorna_n3_v2.stl` | 1116984 | `d3a44e8d7122d167e068d885db53ad485c441dc85b747764bd185bd2d53183cf` |
| `stl/ramka_plytka_poranna_v2.stl` | 1293384 | `5767cf1d387ab1abda6a660db437048c9bc68865aad982bfd1bbf7bfdb79afc0` |
| `stl/ramka_plytka_poranna_n4_v2.stl` | 1294884 | `3186d1ab86f2442302edf057d8bbbc227bbf7f691d4620304f79b377e6773089` |
| `stl/ramka_plytka_poranna_n5_v2.stl` | 1313684 | `70bd4dd499506e38c9973bd50fb66e133d9a2ff34b71cf2494df8d7727866cbb` |
| `stl/ramka_plytka_poranna_n6_v2.stl` | 1306484 | `562d23f69b9bb3f4b015df6e2afdee2ee6aaddc39dfe08370aa418e3d5edcefb` |
| `stl/ramka_pokrywka_v2.stl` | 41084 | `ad23444483ac95733e92169af00e5271d8fc3b19a91854e8c8acddf06c8cd454` |
| `arkusze/kody_plytek.md` | 1706 | `5822f0f7f4a66afc7fb5ab0a620327e498182166ac8813c8aef0ff138938073d` |
| `stl/ramka_wkladka_v2.stl` | 90384 | `f4196fbc640450998634f50caa86051f89df2cbb2c218e317f5c2b193e3ef92b` |
| `stl/ramka_blat_v2.stl` | 284684 | `8c48856eb9addee2b37cfa5a03e5686ab7670bd92b724e488ccc8d8dd3a4b418` |
| `stl/ramka_korpus_W_v2.stl` | 939984 | `bd55871c88cf2604c1c8efa5035148ba39c3803a0788015cc35548e8e9afff9a` |
| `stl/ramka_korpus_P_v2.stl` | 895184 | `aadb91c9364cf39f1f4062d328616aa518e474b957315ed4a941de4f935ab2b7` |
| `stl/ramka_tulejka_dc_v2.stl` | 88584 | `b393256cd8cafdac6d125d6f9f25647c5f94840d1bc5eb87941b436f510bcc00` |
| `stl/ramka_podkladka_panelu_05_v2.stl` | 31584 | `4260d1f1957f32d101cae5da2cf4634e24239caf738592edd7007fc0728ec6b4` |
| `stl/ramka_podkladka_panelu_1_v2.stl` | 31584 | `e79a805121499f8d65b7d23ef6d2ae255549b4f55579ded7061b8996b91c9b78` |
| `stl/ramka_podkladka_panelu_2_v2.stl` | 31584 | `9c47aea4fbc946c16dab3813561d936745b88afde6092542de1d67a21656d5b5` |
| `ramka_v2.blend` | 12021662 | `3235c9c901c778a8125916402c7a840ab9da3416108de3102e3e8bf4947a2a4d` |
| `render/render_rozstrzelony.png` | 1748433 | `d1d296e9050f2d17f024d802d1a76241ce161d8042a75d67471af0bb82995254` |
| `render/render_zlozony.png` | 1761705 | `1df95487eb6a1594d8114e331bf26bbd67663059d91e5e475395724a8815009d` |
| `render/render_plytki.png` | 1929960 | `0e6596e91dbd18b2313544839a95536dbd42e5c7fd26fbf11c87ad4e27c5fd7f` |
| `arkusze/arkusz_zamowienia.csv` | 3658 | `9a74c2611d8cea83765f3bdee65fcbe9eadd285779e0a19906259a258cd16eea` |
| `arkusze/arkusz_zamowienia.md` | 5810 | `61389d75cb6cb29e556185e9febdf57c41bdfe54869a6b6a40cab3ffb6660d17` |
| `arkusze/arkusz_wymiarow.md` | 49726 | `a875026e1ce50938e268da9ec80526dee522a02a8f0e066760a6666e7200f596` |

Dodatkowo: `raport/` (raporty wykonawcy, notatki, rzuty kontrolne), `do_v3.md` (lista drobnych).

## Rejestr odstępstw (z raportu tego przebiegu)

| # | Czego dotyczy | Co zrobiono inaczej | Dlaczego | Wymaga zatwierdzenia? |
|---|---|---|---|---|
| 1 | tabela 3 planu / `panel_slot_w` | przyjęto 3.6 (parametry.json) zamiast 3.4 z tabeli 3 | sprzeczność plan ↔ JSON | tak |
| 2 | tabela 3 planu / `panel_screw_hole_d` | przyjęto 3.6 (parametry.json) zamiast 3.4 z tabeli 3 | sprzeczność plan ↔ JSON | tak |
| 3 | tabela 3 planu / `snap_pocket_w` | przyjęto 11 (parametry.json) zamiast 10 z tabeli 3 | sprzeczność plan ↔ JSON | tak |
| 4 | tabela 3 planu / `snap_pocket_h` | przyjęto 3.5 (parametry.json) zamiast 2.5 z tabeli 3 | sprzeczność plan ↔ JSON | tak |
| 5 | tabela 3 planu / `snap_pocket_depth` | przyjęto 1.3 (parametry.json) zamiast 1 z tabeli 3 | sprzeczność plan ↔ JSON | tak |
| 6 | tabela 3 planu / `snap_pocket_z` | przyjęto 52.1 (parametry.json) zamiast 52.6 z tabeli 3 | sprzeczność plan ↔ JSON | tak |
| 7 | tabela 3 planu / `blat_skirt_clearance` | przyjęto 0.7 (parametry.json) zamiast 0.5 z tabeli 3 | sprzeczność plan ↔ JSON | tak |
| 8 | tabela 3 planu / `snap_hook_h` | przyjęto 1.5 (parametry.json) zamiast 1.3 z tabeli 3 | sprzeczność plan ↔ JSON | tak |
| 9 | tabela 3 planu / `insert_opening` | przyjęto 96.8 (parametry.json) zamiast 96.6 z tabeli 3 | sprzeczność plan ↔ JSON | tak |
| 10 | tabela 3 planu / `orient_post_gap` | przyjęto 0.6 (parametry.json) zamiast 0.5 z tabeli 3 | sprzeczność plan ↔ JSON | tak |
| 11 | tabela 3 planu / `blat_pin_hole_d` | przyjęto 3.4 (parametry.json) zamiast 3.3 z tabeli 3 | sprzeczność plan ↔ JSON | tak |
| 12 | tabela 3 planu / `dc_bush_outer_d` | przyjęto 11.85 (parametry.json) zamiast 12 z tabeli 3 | sprzeczność plan ↔ JSON | tak |
| 13 | R47 / bryła zastępcza gniazda DC: grubość nakrętki | grubość nakrętki = `dc_pocket_wall` (2.0) | plan podaje „nakrętka ø15 × 2”, grubość bez własnego klucza; wartość liczbowo równa | nie — przyjęte informacyjnie (R51) |
| 14 | bryła zastępcza `proxy_odbiornik_usb` (tylko korpus P) | położenie przyjęte: wystaje 19 mm w +X od krawędzi portów Pi (x = 35), oś y = 0, Z 8…14 | plan mówi tylko „dolny port USB Pi”; pozycji portu nie ma w parametrach | nie — przyjęte informacyjnie (R51) |
| 15 | protokół K‑57 / arkusz zamówienia: wzór kosztu pokazowego | najtańszy = obj × szt × `cost_rate_min`…`cost_rate_max`; pokazowy = najtańszy × `cost_dye_factor` × `cost_smooth_factor` dla korpusu i blatu (Z19), części białe bez mnożników | opis K‑57 („koszt_max … × dye dla grafitu × smooth dla korpusu/blatu”) jest niejednoznaczny; przyjęto wzór z planu 12.1 i sekcji 11, zapisany pod tabelą arkusza | nie — informacyjnie |
| 16 | render rozstrzelony (prompt: rozsunięcie wzdłuż Z) | gniazda DC i USB oraz tulejka wysunięte w lewo ekranu (280 mm) przy Z korpusu | w izometrii części wewnątrz korpusu zasłaniają ściany i warstwy wyżej; lista §11 wymaga ich widoczności (K‑60 mierzy widoczność) | nie — informacyjnie |
| 17 | bryła zastępcza gniazda DC z tulejką (K‑53) | bez gwintu ø8 w otworze tulejki | średnica gwintu gniazda nie ma klucza (wynik pomiaru #16) | nie — informacyjnie (do_v3) |
| 18 | plan 4.4 p. 3 i 4.11 (opis) | kołnierz blatu na 95,0…97,0 (z `parametry.json`, R48) | tekst planu: „zrośnięte z kołnierzem 95,2…97,2”, „wnętrze kołnierza 97,2” — opis sprzed R48; STL bez wpływu | nie — do poprawy opisu w planie (do_v3) |
| 19 | K‑59 / `ramka_wkladka_v2.stl` | brak zmian; SHA wkładki może się różnić między przebiegami | różnica tylko w znaku zera (−0,0 / +0,0) zapisanych normalnych (wierzchołki i trójkąty identyczne); normalizacja w `stl_kanoniczny` zmieniłaby bajty wszystkich STL, także zatwierdzonych płytek | nie — rozstrzygnięte przez nadzór po C iter1 (K‑59 kanonicznie; normalizacja w v3, `do_v3.md` #9) |
| 20 | protokół K‑52b, plan 4.x (tulejka DC) — opis | walec ø11,85 z `parametry.json` (R52: `dc_hole_d` − 0,15, luz 0,075/stronę w otworze ø12, reguła 4.8 „wciskane”) | tekst K‑52b („walec ø12 × 2”, „walec r 6”) i opis pliku w planie („walec ø`dc_bush_outer_d` 12”) sprzed R52; sondy K‑52b (r 5,5 W, r 6,8 POZA) bez zmian; w złożeniu walec nie przenika ściany (luz geometryczny 0,075/stronę, K‑53 bez przecięcia) | nie — do poprawy opisu w protokole i planie |
