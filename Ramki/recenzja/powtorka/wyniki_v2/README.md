# Ramki świetlne — pliki v2

Wszystko w tym folderze generuje `ramka_generator.py` z `parametry.json` i `plan_ramki_v2.md` (R14). Plików nie edytuje się ręcznie (R28). Ostatni przebieg: etap ALL, iteracja 1, raport `raport/raport_wykonawcy_ALL_iter1.md` (sumy SHA‑256 wszystkich plików).

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
| `stl/ramka_wkladka_v2.stl` | 90384 | `0af58844a2d2bd02237b75d8463c55fcb9b1c5a249c68d3c7135b65dedf11fcf` |
| `stl/ramka_blat_v2.stl` | 285884 | `060b439bf33d3bd3adcbd2520c8da6047e40ab4c0b12b9b7f36f1e0e235faa25` |
| `stl/ramka_korpus_W_v2.stl` | 911084 | `7e7c9298e50a21961571e7c33b622614b4c290552783a77ba72717dc41a37494` |
| `stl/ramka_korpus_P_v2.stl` | 866284 | `9c31c117983a944b31248693e374c2c5d784e825803e375b44db928cbe4e7e24` |
| `stl/ramka_tulejka_dc_v2.stl` | 88884 | `d670fb91a5b55e676874a840452c141513dfef30d52d9d3472adb099226d0f39` |
| `stl/ramka_podkladka_panelu_05_v2.stl` | 31584 | `4260d1f1957f32d101cae5da2cf4634e24239caf738592edd7007fc0728ec6b4` |
| `stl/ramka_podkladka_panelu_1_v2.stl` | 31584 | `e79a805121499f8d65b7d23ef6d2ae255549b4f55579ded7061b8996b91c9b78` |
| `stl/ramka_podkladka_panelu_2_v2.stl` | 31584 | `9c47aea4fbc946c16dab3813561d936745b88afde6092542de1d67a21656d5b5` |
| `ramka_v2.blend` | 11969866 | `fdeda113e1ca10b539178ad51d407685f5c60dac8e7c99cd859baffb0da7406b` |
| `render/render_rozstrzelony.png` | 1748477 | `56e762950cdb3e41e18feb582bb8a69112361ec3c823efbca8dd280c01af1148` |
| `render/render_zlozony.png` | 1761285 | `ce269095b91e9a86600fa8878e6a5ffe5a705d112d7eb5b79139806521c033e9` |
| `render/render_plytki.png` | 1929978 | `4d81ec2b322b607fb98e1daa0c0f2ae55f6548ecb66f5c31a63d847b5707cac0` |
| `arkusze/arkusz_zamowienia.csv` | 3658 | `3dad34a23403c15b36dac1d17d1e79520dc2e0138a1b4ab7f5fa2f2ce054ff5c` |
| `arkusze/arkusz_zamowienia.md` | 5810 | `1e2d645adfb4baf6b6aa6ae12d76774effdb626f34337f33f5f137ff39fba9de` |
| `arkusze/arkusz_wymiarow.md` | 48095 | `c4b08f484519f8c886c72ad34ec6bff64807608876887ad3a46d102a5cd030af` |

Dodatkowo: `raport/` (raporty wykonawcy, notatki, rzuty kontrolne), `do_v3.md` (lista drobnych).

## Rejestr odstępstw (z raportu tego przebiegu)

| # | Czego dotyczy | Co zrobiono inaczej | Dlaczego | Wymaga zatwierdzenia? |
|---|---|---|---|---|
| 1 | R47 / bryła zastępcza gniazda DC: grubość nakrętki | grubość nakrętki = `dc_pocket_wall` (2.0) | plan podaje „nakrętka ø15 × 2”, grubość bez własnego klucza; wartość liczbowo równa | nie — przyjęte informacyjnie (R51) |
| 2 | bryła zastępcza `proxy_odbiornik_usb` (tylko korpus P) | położenie przyjęte: wystaje 19 mm w +X od krawędzi portów Pi (x = 35), oś y = 0, Z 8…14 | plan mówi tylko „dolny port USB Pi”; pozycji portu nie ma w parametrach | nie — przyjęte informacyjnie (R51) |
| 3 | protokół K‑57 / arkusz zamówienia: wzór kosztu pokazowego | najtańszy = obj × szt × `cost_rate_min`…`cost_rate_max`; pokazowy = najtańszy × `cost_dye_factor` × `cost_smooth_factor` dla korpusu i blatu (Z19), części białe bez mnożników | opis K‑57 („koszt_max … × dye dla grafitu × smooth dla korpusu/blatu”) jest niejednoznaczny; przyjęto wzór z planu 12.1 i sekcji 11, zapisany pod tabelą arkusza | nie — informacyjnie |
| 4 | render rozstrzelony (prompt: rozsunięcie wzdłuż Z) | gniazda DC i USB oraz tulejka wysunięte w lewo ekranu (280 mm) przy Z korpusu | w izometrii części wewnątrz korpusu zasłaniają ściany i warstwy wyżej; lista §11 wymaga ich widoczności (K‑60 mierzy widoczność) | nie — informacyjnie |
| 5 | bryła zastępcza gniazda DC z tulejką (K‑53) | bez gwintu ø8 w otworze tulejki | średnica gwintu gniazda nie ma klucza (wynik pomiaru #16) | nie — informacyjnie (do_v3) |
| 6 | plan 4.4 p. 3 i 4.11 (opis) | kołnierz blatu na 95,0…97,0 (z `parametry.json`, R48) | tekst planu: „zrośnięte z kołnierzem 95,2…97,2”, „wnętrze kołnierza 97,2” — opis sprzed R48; STL bez wpływu | nie — do poprawy opisu w planie (do_v3) |
| 7 | K‑59 / `ramka_wkladka_v2.stl` | brak zmian; SHA wkładki może się różnić między przebiegami | różnica tylko w znaku zera (−0,0 / +0,0) zapisanych normalnych (wierzchołki i trójkąty identyczne); normalizacja w `stl_kanoniczny` zmieniłaby bajty wszystkich STL, także zatwierdzonych płytek | tak — decyzja nadzoru (normalizować −0,0 w kolejnej wersji czy przyjąć K‑59 z uwagą D) |
