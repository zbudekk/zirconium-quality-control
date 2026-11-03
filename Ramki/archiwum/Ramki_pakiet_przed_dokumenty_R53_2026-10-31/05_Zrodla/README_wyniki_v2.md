# Ramki świetlne — pliki v2

Wszystko w tym folderze generuje `ramka_generator.py` z `parametry.json` i `plan_ramki_v2.md` (R14). Plików nie edytuje się ręcznie (R28). Ostatni przebieg: etap C, iteracja 2, raport `raport/raport_wykonawcy_C_iter2.md` (sumy SHA‑256 wszystkich plików).

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
| `stl/ramka_wkladka_v2.stl` | 90384 | `ef7503c7de3440426f3fce9f0fff37e25dc617521d84c7b5b6210c4527535c78` |
| `stl/ramka_blat_v2.stl` | 285884 | `060b439bf33d3bd3adcbd2520c8da6047e40ab4c0b12b9b7f36f1e0e235faa25` |
| `stl/ramka_korpus_W_v2.stl` | 911084 | `7e7c9298e50a21961571e7c33b622614b4c290552783a77ba72717dc41a37494` |
| `stl/ramka_korpus_P_v2.stl` | 866284 | `9c31c117983a944b31248693e374c2c5d784e825803e375b44db928cbe4e7e24` |
| `stl/ramka_tulejka_dc_v2.stl` | 88584 | `b393256cd8cafdac6d125d6f9f25647c5f94840d1bc5eb87941b436f510bcc00` |
| `stl/ramka_podkladka_panelu_05_v2.stl` | 31584 | `4260d1f1957f32d101cae5da2cf4634e24239caf738592edd7007fc0728ec6b4` |
| `stl/ramka_podkladka_panelu_1_v2.stl` | 31584 | `e79a805121499f8d65b7d23ef6d2ae255549b4f55579ded7061b8996b91c9b78` |
| `stl/ramka_podkladka_panelu_2_v2.stl` | 31584 | `9c47aea4fbc946c16dab3813561d936745b88afde6092542de1d67a21656d5b5` |
| `ramka_v2.blend` | 11969590 | `f8b03af089bf184b5d4b924c3674a1ea4cb5b1046321f52c0e5cb660af5274e3` |
| `render/render_rozstrzelony.png` | 1748579 | `30b3269d20fd4ff21404a42f30926a6f2f8567287bd6a8d487f704cf906d7567` |
| `render/render_zlozony.png` | 1761267 | `a1bf126b4aa239eb2849d916872b0a2713b6676f3abe551fc597461fe05519cb` |
| `render/render_plytki.png` | 1929960 | `c749a420b11684ab335fa78de1dd74902900c3a028bc572cde4ad35978bea830` |
| `arkusze/arkusz_zamowienia.csv` | 3658 | `3dad34a23403c15b36dac1d17d1e79520dc2e0138a1b4ab7f5fa2f2ce054ff5c` |
| `arkusze/arkusz_zamowienia.md` | 5810 | `1e2d645adfb4baf6b6aa6ae12d76774effdb626f34337f33f5f137ff39fba9de` |
| `arkusze/arkusz_wymiarow.md` | 48162 | `d250d93face93510616d40951603b538c157c01f94c32c916e0e27c60108b82a` |

Dodatkowo: `raport/` (raporty wykonawcy, notatki, rzuty kontrolne), `do_v3.md` (lista drobnych).

## Rejestr odstępstw (z raportu tego przebiegu)

| # | Czego dotyczy | Co zrobiono inaczej | Dlaczego | Wymaga zatwierdzenia? |
|---|---|---|---|---|
| 1 | tabela 3 planu / `dc_bush_outer_d` | przyjęto 11.85 (parametry.json) zamiast 12 z tabeli 3 | sprzeczność plan ↔ JSON | tak |
| 2 | R47 / bryła zastępcza gniazda DC: grubość nakrętki | grubość nakrętki = `dc_pocket_wall` (2.0) | plan podaje „nakrętka ø15 × 2”, grubość bez własnego klucza; wartość liczbowo równa | nie — przyjęte informacyjnie (R51) |
| 3 | bryła zastępcza `proxy_odbiornik_usb` (tylko korpus P) | położenie przyjęte: wystaje 19 mm w +X od krawędzi portów Pi (x = 35), oś y = 0, Z 8…14 | plan mówi tylko „dolny port USB Pi”; pozycji portu nie ma w parametrach | nie — przyjęte informacyjnie (R51) |
| 4 | protokół K‑57 / arkusz zamówienia: wzór kosztu pokazowego | najtańszy = obj × szt × `cost_rate_min`…`cost_rate_max`; pokazowy = najtańszy × `cost_dye_factor` × `cost_smooth_factor` dla korpusu i blatu (Z19), części białe bez mnożników | opis K‑57 („koszt_max … × dye dla grafitu × smooth dla korpusu/blatu”) jest niejednoznaczny; przyjęto wzór z planu 12.1 i sekcji 11, zapisany pod tabelą arkusza | nie — informacyjnie |
| 5 | render rozstrzelony (prompt: rozsunięcie wzdłuż Z) | gniazda DC i USB oraz tulejka wysunięte w lewo ekranu (280 mm) przy Z korpusu | w izometrii części wewnątrz korpusu zasłaniają ściany i warstwy wyżej; lista §11 wymaga ich widoczności (K‑60 mierzy widoczność) | nie — informacyjnie |
| 6 | bryła zastępcza gniazda DC z tulejką (K‑53) | bez gwintu ø8 w otworze tulejki | średnica gwintu gniazda nie ma klucza (wynik pomiaru #16) | nie — informacyjnie (do_v3) |
| 7 | plan 4.4 p. 3 i 4.11 (opis) | kołnierz blatu na 95,0…97,0 (z `parametry.json`, R48) | tekst planu: „zrośnięte z kołnierzem 95,2…97,2”, „wnętrze kołnierza 97,2” — opis sprzed R48; STL bez wpływu | nie — do poprawy opisu w planie (do_v3) |
| 8 | K‑59 / `ramka_wkladka_v2.stl` | brak zmian; SHA wkładki może się różnić między przebiegami | różnica tylko w znaku zera (−0,0 / +0,0) zapisanych normalnych (wierzchołki i trójkąty identyczne); normalizacja w `stl_kanoniczny` zmieniłaby bajty wszystkich STL, także zatwierdzonych płytek | nie — rozstrzygnięte przez nadzór po C iter1 (K‑59 kanonicznie; normalizacja w v3, `do_v3.md` #9) |
| 9 | protokół K‑52b, plan 4.x (tulejka DC) — opis | walec ø11,85 z `parametry.json` (R52: `dc_hole_d` − 0,15, luz 0,075/stronę w otworze ø12, reguła 4.8 „wciskane”) | tekst K‑52b („walec ø12 × 2”, „walec r 6”) i opis pliku w planie („walec ø`dc_bush_outer_d` 12”) sprzed R52; sondy K‑52b (r 5,5 W, r 6,8 POZA) bez zmian; w złożeniu walec nie przenika ściany (luz geometryczny 0,075/stronę, K‑53 bez przecięcia) | nie — do poprawy opisu w protokole i planie |
