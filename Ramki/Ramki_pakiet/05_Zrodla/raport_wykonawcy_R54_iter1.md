# Raport wykonawcy — etap C, iteracja 1 (R54)

Plik: `wyniki_v2/raport/raport_wykonawcy_R54_iter1.md`. Wypełniony automatycznie przez `ramka_generator.py` po pełnym przebiegu. Wszystkie liczby w sekcjach 2–3 pochodzą z plików w `wyniki_v2/` (STL wczytane z powrotem), nie z kodu.

## 1. Przebieg
- Polecenie uruchomienia (dosłownie, z `cd`): `cd <PC>\Desktop\Ramki && "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P ramka_generator.py -- --etap C --iter 1 --raport R54`
- Wersja Blendera (`blender --version`): 5.2.3 LTS
- Data: 2026-11-01 15:55
- Czas przebiegu: 34 s; błędy/ostrzeżenia w konsoli: brak
- Suma SHA‑256 `parametry.json` użytego w tym przebiegu: `e8e5fb7f665328f54f2dea4f7d00f6b675c0b86ac0b25e2d328de20083449afc`
- Suma SHA‑256 `ramka_generator.py`: `f84e25ee5b77252fe308aab8c215f61fcf7c87d4d2ad6753955106bac9b4e48f`
- Wartości LICZONE (wzór z `parametry.json` → plik, różnica): blat_screw_z 55.000 → 55.000 (0.0000); blat_top_z 63.600 → 63.600 (0.0000); cover_inner_h 14.000 → 14.000 (0.0000); korpus_h 59.600 → 59.600 (0.0000); label_pos_z 51.000 → 51.000 (0.0000); panel_pcb_z 54.000 → 54.000 (0.0000); panel_standoff_l 50.000 → 50.000 (0.0000); snap_hook_z 52.850 → 52.850 (0.0000); snap_pocket_z 52.100 → 52.100 (0.0000); socket_zone_r 47.000 → 47.000 (0.0000)
- Plik ukladu gniazd: uklad_gniazd_wieczorna.json: utworzony z D6 (ev_rows/mo_rows); uklad_gniazd_poranna.json: utworzony z D6 (ev_rows/mo_rows)
- Font: `Inter.woff2` z instalacji Blendera (R22, R47); napisy:

| Napis | Treść | Wys. zadana [mm] | Rozmiar fontu | Pogrubienie konturu [mm] | Wys. litery H zmierzona | Trzon H zmierzony [mm] | Szerokość napisu [mm] |
|---|---|---|---|---|---|---|---|
| cyfra n1 | 1 | 5.00 | 8.966 | 0.219 | 5.000 | 1.017 | 3.26 |
| cyfra n2 | 2 | 5.00 | 8.966 | 0.219 | 5.000 | 1.017 | 3.36 |
| cyfra n3 | 3 | 5.00 | 8.966 | 0.219 | 5.000 | 1.017 | 3.57 |
| cyfra n4 | 4 | 5.00 | 8.966 | 0.219 | 5.000 | 1.017 | 3.79 |
| cyfra n5 | 5 | 5.00 | 8.966 | 0.219 | 5.000 | 1.017 | 3.41 |
| cyfra n6 | 6 | 5.00 | 8.966 | 0.219 | 5.000 | 1.017 | 3.35 |
| korpus RAMKA WIECZORNA | RAMKA WIECZORNA | 8.00 | 14.940 | 0.200 | 8.000 | 1.364 | 104.28 |
| korpus RAMKA PORANNA | RAMKA PORANNA | 8.00 | 14.940 | 0.200 | 8.000 | 1.364 | 90.74 |

## 2. Pliki wytworzone w tym etapie

| Plik | Rozmiar [B] | SHA‑256 | Gabaryt X × Y × Z [mm] (STL) | Objętość [cm³] (STL) |
|---|---|---|---|---|
| `json/uklad_gniazd_wieczorna.json` | 4358 | `a4648f3562105bb19809bd7671e6421461f51fa2a4f29b5ecf0e1d6f29d1fb1e` | — | — |
| `json/uklad_gniazd_poranna.json` | 6342 | `6e8290c3a7c4becd3b065f8ccd39da9e8f8a2f0cb9bab6a1464fbcda84995812` | — | — |
| `stl/ramka_plytka_wieczorna_v2.stl` | 912884 | `a7ab083e658da206c40e93f18c556988167dae343a5a2a40e2362d06c5929f47` | 96.000 × 96.000 × 8.000 | 59.30 |
| `stl/ramka_plytka_wieczorna_n1_v2.stl` | 911684 | `515d32d3dd8a69ae0a94d293a639b201f2d9ce9af19df664ad1b44b59408f775` | 96.000 × 96.000 × 8.600 | 59.31 |
| `stl/ramka_plytka_wieczorna_n2_v2.stl` | 921784 | `360cff9ddd6bbcf8a84b463fed930532612a38118006f1550c2df01b02fa852d` | 96.000 × 96.000 × 8.600 | 59.31 |
| `stl/ramka_plytka_wieczorna_n3_v2.stl` | 932284 | `2fc7040e212ace4a8efda17f61909ca09563009513adcd82ecf5bcaac3e98aaf` | 96.000 × 96.000 × 8.600 | 59.31 |
| `stl/ramka_plytka_poranna_v2.stl` | 1184984 | `c3536c64b3ac143160f6db4a80ab1530f8442ba4d538369a536d2228579783d8` | 96.000 × 96.000 × 8.000 | 60.86 |
| `stl/ramka_plytka_poranna_n4_v2.stl` | 1189084 | `a8d07cbeb0dafc0e55d3fe2fe516c7d3e854a6259bce587785b796d34b54c65e` | 96.000 × 96.000 × 8.600 | 60.87 |
| `stl/ramka_plytka_poranna_n5_v2.stl` | 1204884 | `159503ca4cd66b90a1e2441cae64016901ed83390b48a27345f9484ac1a05830` | 96.000 × 96.000 × 8.600 | 60.87 |
| `stl/ramka_plytka_poranna_n6_v2.stl` | 1200984 | `0d5d712d42084a19846f24d385484d01b2254c5c1ec3945d71cfd3493816f15e` | 96.000 × 96.000 × 8.600 | 60.87 |
| `stl/ramka_pokrywka_v2.stl` | 41084 | `ad23444483ac95733e92169af00e5271d8fc3b19a91854e8c8acddf06c8cd454` | 99.600 × 99.600 × 20.000 | 30.06 |
| `arkusze/kody_plytek.md` | 1706 | `5822f0f7f4a66afc7fb5ab0a620327e498182166ac8813c8aef0ff138938073d` | — | — |
| `stl/ramka_wkladka_v2.stl` | 90384 | `f4196fbc640450998634f50caa86051f89df2cbb2c218e317f5c2b193e3ef92b` | 130.000 × 148.400 × 11.000 | 12.41 |
| `stl/ramka_blat_v2.stl` | 284684 | `8c48856eb9addee2b37cfa5a03e5686ab7670bd92b724e488ccc8d8dd3a4b418` | 200.000 × 200.000 × 14.000 | 72.52 |
| `stl/ramka_korpus_W_v2.stl` | 939984 | `bd55871c88cf2604c1c8efa5035148ba39c3803a0788015cc35548e8e9afff9a` | 200.000 × 200.600 × 59.600 | 233.49 |
| `stl/ramka_korpus_P_v2.stl` | 895184 | `aadb91c9364cf39f1f4062d328616aa518e474b957315ed4a941de4f935ab2b7` | 200.000 × 200.600 × 59.600 | 233.47 |
| `stl/ramka_tulejka_dc_v2.stl` | 88584 | `b393256cd8cafdac6d125d6f9f25647c5f94840d1bc5eb87941b436f510bcc00` | 14.999 × 14.999 × 3.000 | 0.24 |
| `stl/ramka_podkladka_panelu_05_v2.stl` | 31584 | `4260d1f1957f32d101cae5da2cf4634e24239caf738592edd7007fc0728ec6b4` | 9.000 × 8.997 × 0.500 | 0.03 |
| `stl/ramka_podkladka_panelu_1_v2.stl` | 31584 | `e79a805121499f8d65b7d23ef6d2ae255549b4f55579ded7061b8996b91c9b78` | 9.000 × 8.997 × 1.000 | 0.05 |
| `stl/ramka_podkladka_panelu_2_v2.stl` | 31584 | `9c47aea4fbc946c16dab3813561d936745b88afde6092542de1d67a21656d5b5` | 9.000 × 8.997 × 2.000 | 0.11 |
| `ramka_v2.blend` | 10945026 | `75320f6dfc9adb32da3ede38eb1697000688dfef8b2ae9031567049492697d3c` | — | — |
| `render/render_rozstrzelony.png` | 1746639 | `97ee07e7121cb5b10c5bdeacbd83023edc30c6d053ad7ea80683707966ff9a48` | — | — |
| `render/render_zlozony.png` | 1759258 | `9651dc0ff28128bcd7d9082eccf6edc437f0e4405069dd23390e288e4fe9a680` | — | — |
| `render/render_plytki.png` | 1909348 | `f4d964924fbccd481212c4d37bee5245c4199019f36d39103d29bc0b1f5ba6ff` | — | — |
| `arkusze/arkusz_zamowienia.csv` | 3658 | `510f833c2ebca04a4d228a68bbc3ad927794b9206baa8c4af2ae411449d895b7` | — | — |
| `arkusze/arkusz_zamowienia.md` | 5810 | `7e1697a542a43127650cc06e9828100440c9c1de5a9d0f59c0b2a739c485da6d` | — | — |
| `arkusze/arkusz_wymiarow.md` | 51612 | `0f5185f0431ac5a80293549e3176c949af4118d43f260dceabda1822127512a5` | — | — |
| `do_v3.md` | 2261 | `c33508c2464bf4b87c8192e5525f5e469e6b4f6b75eb50ca245fdbbacd70bce8` | — | — |
| `README.md` | 8352 | `d1bea70cd287011de00e6e6978bc4f0d7787e1e7dd721a8f806ae0816ea31828` | — | — |

## 3. Wyniki sprawdzeń (protokół v2) — wszystkie K‑xx etapu

| Id | Wynik (ZAL/NIE/N/D) | Wartość zmierzona | Oczekiwane | Uwaga |
|---|---|---|---|---|
| K‑01 (B) | ZAL | ramka_plytka_wieczorna_v2.stl: 18256 trójkątów, NaN: nie<br>ramka_plytka_wieczorna_n1_v2.stl: 18232 trójkątów, NaN: nie<br>ramka_plytka_wieczorna_n2_v2.stl: 18434 trójkątów, NaN: nie<br>ramka_plytka_wieczorna_n3_v2.stl: 18644 trójkątów, NaN: nie<br>ramka_plytka_poranna_v2.stl: 23698 trójkątów, NaN: nie<br>ramka_plytka_poranna_n4_v2.stl: 23780 trójkątów, NaN: nie<br>ramka_plytka_poranna_n5_v2.stl: 24096 trójkątów, NaN: nie<br>ramka_plytka_poranna_n6_v2.stl: 24018 trójkątów, NaN: nie<br>ramka_pokrywka_v2.stl: 820 trójkątów, NaN: nie<br>ramka_wkladka_v2.stl: 1806 trójkątów, NaN: nie<br>ramka_blat_v2.stl: 5692 trójkątów, NaN: nie<br>ramka_korpus_W_v2.stl: 18798 trójkątów, NaN: nie<br>ramka_korpus_P_v2.stl: 17902 trójkątów, NaN: nie<br>ramka_tulejka_dc_v2.stl: 1770 trójkątów, NaN: nie<br>ramka_podkladka_panelu_05_v2.stl: 630 trójkątów, NaN: nie<br>ramka_podkladka_panelu_1_v2.stl: 630 trójkątów, NaN: nie<br>ramka_podkladka_panelu_2_v2.stl: 630 trójkątów, NaN: nie | > 100, bez NaN |  |
| K‑02 (B) | ZAL | ramka_plytka_wieczorna_v2.stl: 96.000 × 96.000 × 8.000; X -48.000…48.000, Y -48.000…48.000, Z -8.000…0.000<br>ramka_plytka_wieczorna_n1_v2.stl: 96.000 × 96.000 × 8.600; X -48.000…48.000, Y -48.000…48.000, Z -8.000…0.600<br>ramka_plytka_wieczorna_n2_v2.stl: 96.000 × 96.000 × 8.600; X -48.000…48.000, Y -48.000…48.000, Z -8.000…0.600<br>ramka_plytka_wieczorna_n3_v2.stl: 96.000 × 96.000 × 8.600; X -48.000…48.000, Y -48.000…48.000, Z -8.000…0.600<br>ramka_plytka_poranna_v2.stl: 96.000 × 96.000 × 8.000; X -48.000…48.000, Y -48.000…48.000, Z -8.000…0.000<br>ramka_plytka_poranna_n4_v2.stl: 96.000 × 96.000 × 8.600; X -48.000…48.000, Y -48.000…48.000, Z -8.000…0.600<br>ramka_plytka_poranna_n5_v2.stl: 96.000 × 96.000 × 8.600; X -48.000…48.000, Y -48.000…48.000, Z -8.000…0.600<br>ramka_plytka_poranna_n6_v2.stl: 96.000 × 96.000 × 8.600; X -48.000…48.000, Y -48.000…48.000, Z -8.000…0.600<br>ramka_pokrywka_v2.stl: 99.600 × 99.600 × 20.000; X -49.800…49.800, Y -49.800…49.800, Z -20.000…0.000<br>ramka_wkladka_v2.stl: 130.000 × 148.400 × 11.000; X -65.000…65.000, Y -52.400…96.000, Z -3.500…7.500<br>ramka_blat_v2.stl: 200.000 × 200.000 × 14.000; X -100.000…100.000, Y -100.000…100.000, Z -14.000…0.000<br>ramka_korpus_W_v2.stl: 200.000 × 200.600 × 59.600; X -100.000…100.000, Y -100.600…100.000, Z 0.000…59.600<br>ramka_korpus_P_v2.stl: 200.000 × 200.600 × 59.600; X -100.000…100.000, Y -100.600…100.000, Z 0.000…59.600<br>ramka_tulejka_dc_v2.stl: 14.999 × 14.999 × 3.000; X -7.499…7.500, Y -7.500…7.500, Z 0.000…3.000<br>ramka_podkladka_panelu_05_v2.stl: 9.000 × 8.997 × 0.500; X -4.500…4.500, Y -4.498…4.498, Z 0.000…0.500<br>ramka_podkladka_panelu_1_v2.stl: 9.000 × 8.997 × 1.000; X -4.500…4.500, Y -4.498…4.498, Z 0.000…1.000<br>ramka_podkladka_panelu_2_v2.stl: 9.000 × 8.997 × 2.000; X -4.500…4.500, Y -4.498…4.498, Z 0.000…2.000 | tabela 1 ± 0,1 |  |
| K‑03 (B) | ZAL | ramka_plytka_wieczorna_v2.stl: 0 / 0 / 0 (trójkąty o polu < 1e-6 mm²: 0)<br>ramka_plytka_wieczorna_n1_v2.stl: 0 / 0 / 0 (trójkąty o polu < 1e-6 mm²: 0)<br>ramka_plytka_wieczorna_n2_v2.stl: 0 / 0 / 0 (trójkąty o polu < 1e-6 mm²: 0)<br>ramka_plytka_wieczorna_n3_v2.stl: 0 / 0 / 0 (trójkąty o polu < 1e-6 mm²: 0)<br>ramka_plytka_poranna_v2.stl: 0 / 0 / 0 (trójkąty o polu < 1e-6 mm²: 0)<br>ramka_plytka_poranna_n4_v2.stl: 0 / 0 / 0 (trójkąty o polu < 1e-6 mm²: 0)<br>ramka_plytka_poranna_n5_v2.stl: 0 / 0 / 0 (trójkąty o polu < 1e-6 mm²: 0)<br>ramka_plytka_poranna_n6_v2.stl: 0 / 0 / 0 (trójkąty o polu < 1e-6 mm²: 0)<br>ramka_pokrywka_v2.stl: 0 / 0 / 0 (trójkąty o polu < 1e-6 mm²: 0)<br>ramka_wkladka_v2.stl: 0 / 0 / 0 (trójkąty o polu < 1e-6 mm²: 0)<br>ramka_blat_v2.stl: 0 / 0 / 0 (trójkąty o polu < 1e-6 mm²: 0)<br>ramka_korpus_W_v2.stl: 0 / 0 / 0 (trójkąty o polu < 1e-6 mm²: 8)<br>ramka_korpus_P_v2.stl: 0 / 0 / 0 (trójkąty o polu < 1e-6 mm²: 8)<br>ramka_tulejka_dc_v2.stl: 0 / 0 / 0 (trójkąty o polu < 1e-6 mm²: 0)<br>ramka_podkladka_panelu_05_v2.stl: 0 / 0 / 0 (trójkąty o polu < 1e-6 mm²: 0)<br>ramka_podkladka_panelu_1_v2.stl: 0 / 0 / 0 (trójkąty o polu < 1e-6 mm²: 0)<br>ramka_podkladka_panelu_2_v2.stl: 0 / 0 / 0 (trójkąty o polu < 1e-6 mm²: 0) | 0 / 0 / 0 |  |
| K‑04 (B) | ZAL | ramka_plytka_wieczorna_v2.stl: 1<br>ramka_plytka_wieczorna_n1_v2.stl: 1<br>ramka_plytka_wieczorna_n2_v2.stl: 1<br>ramka_plytka_wieczorna_n3_v2.stl: 1<br>ramka_plytka_poranna_v2.stl: 1<br>ramka_plytka_poranna_n4_v2.stl: 1<br>ramka_plytka_poranna_n5_v2.stl: 1<br>ramka_plytka_poranna_n6_v2.stl: 1<br>ramka_pokrywka_v2.stl: 1<br>ramka_wkladka_v2.stl: 1<br>ramka_blat_v2.stl: 1<br>ramka_korpus_W_v2.stl: 1<br>ramka_korpus_P_v2.stl: 1<br>ramka_tulejka_dc_v2.stl: 1<br>ramka_podkladka_panelu_05_v2.stl: 1<br>ramka_podkladka_panelu_1_v2.stl: 1<br>ramka_podkladka_panelu_2_v2.stl: 1 | 1 |  |
| K‑04b (B) | ZAL | ramka_plytka_wieczorna_v2.stl: 59.30 cm³ (orient. 62 → 43.4…80.6)<br>ramka_plytka_wieczorna_n1_v2.stl: 59.31 cm³ (orient. 62 → 43.4…80.6)<br>ramka_plytka_wieczorna_n2_v2.stl: 59.31 cm³ (orient. 62 → 43.4…80.6)<br>ramka_plytka_wieczorna_n3_v2.stl: 59.31 cm³ (orient. 62 → 43.4…80.6)<br>ramka_plytka_poranna_v2.stl: 60.86 cm³ (orient. 61 → 42.7…79.3)<br>ramka_plytka_poranna_n4_v2.stl: 60.87 cm³ (orient. 61 → 42.7…79.3)<br>ramka_plytka_poranna_n5_v2.stl: 60.87 cm³ (orient. 61 → 42.7…79.3)<br>ramka_plytka_poranna_n6_v2.stl: 60.87 cm³ (orient. 61 → 42.7…79.3)<br>ramka_pokrywka_v2.stl: 30.06 cm³ (orient. 30 → 21.0…39.0)<br>ramka_wkladka_v2.stl: 12.41 cm³ (orient. 16 → 11.2…20.8)<br>ramka_blat_v2.stl: 72.52 cm³ (orient. 83 → 58.1…107.9)<br>ramka_korpus_W_v2.stl: 233.49 cm³ (orient. 225 → 157.5…292.5)<br>ramka_korpus_P_v2.stl: 233.47 cm³ (orient. 225 → 157.5…292.5)<br>ramka_tulejka_dc_v2.stl: 0.24 cm³ (orient. 0 → 0.2…0.4)<br>ramka_podkladka_panelu_05_v2.stl: 0.03 cm³ (orient. 0 → 0.0…0.0)<br>ramka_podkladka_panelu_1_v2.stl: 0.05 cm³ (orient. 0 → 0.0…0.1)<br>ramka_podkladka_panelu_2_v2.stl: 0.11 cm³ (orient. 0 → 0.1…0.1) | objętość > 0 i orient. z tab. 1 ± 30 % |  |
| K‑05 (B) | ZAL | uklad_gniazd_wieczorna.json: round/trough 18/2 (oczekiwane 18/2 z ev_rows); rzędów 5; max promień obrysu 46.389 (id 2) ≤ 47; min ścianka 3.000 (id 1–3); błędy: brak<br>uklad_gniazd_poranna.json: round/trough 31/2 (oczekiwane 31/2 z mo_rows); rzędów 7; max promień obrysu 46.931 (id 33) ≤ 47; min ścianka 3.000 (id 1–2); błędy: brak | (a)–(g) wszystkie; (c) także koło socket_zone_r 47 [R54] |  |
| K‑06 (B) | ZAL | ramka_plytka_wieczorna_v2.stl: 90/90 sond zgodnych<br>ramka_plytka_wieczorna_n1_v2.stl: 90/90 sond zgodnych<br>ramka_plytka_wieczorna_n2_v2.stl: 90/90 sond zgodnych<br>ramka_plytka_wieczorna_n3_v2.stl: 90/90 sond zgodnych<br>ramka_plytka_poranna_v2.stl: 155/155 sond zgodnych<br>ramka_plytka_poranna_n4_v2.stl: 155/155 sond zgodnych<br>ramka_plytka_poranna_n5_v2.stl: 155/155 sond zgodnych<br>ramka_plytka_poranna_n6_v2.stl: 155/155 sond zgodnych | wszystkie |  |
| K‑07 (B) | ZAL | ramka_plytka_wieczorna_v2.stl: 18/18 (rozmiary [9, 12, 15])<br>ramka_plytka_wieczorna_n1_v2.stl: 18/18 (rozmiary [9, 12, 15])<br>ramka_plytka_wieczorna_n2_v2.stl: 18/18 (rozmiary [9, 12, 15])<br>ramka_plytka_wieczorna_n3_v2.stl: 18/18 (rozmiary [9, 12, 15])<br>ramka_plytka_poranna_v2.stl: 18/18 (rozmiary [7.5, 10, 12.5])<br>ramka_plytka_poranna_n4_v2.stl: 18/18 (rozmiary [7.5, 10, 12.5])<br>ramka_plytka_poranna_n5_v2.stl: 18/18 (rozmiary [7.5, 10, 12.5])<br>ramka_plytka_poranna_n6_v2.stl: 18/18 (rozmiary [7.5, 10, 12.5]) | tak |  |
| K‑08 (B) | ZAL | ramka_plytka_wieczorna_v2.stl: 20/20<br>ramka_plytka_wieczorna_n1_v2.stl: 20/20<br>ramka_plytka_wieczorna_n2_v2.stl: 20/20<br>ramka_plytka_wieczorna_n3_v2.stl: 20/20<br>ramka_plytka_poranna_v2.stl: 20/20<br>ramka_plytka_poranna_n4_v2.stl: 20/20<br>ramka_plytka_poranna_n5_v2.stl: 20/20<br>ramka_plytka_poranna_n6_v2.stl: 20/20 | tak |  |
| K‑09 (B) | ZAL | ramka_plytka_wieczorna_v2.stl: 15/15 (znaczniki A (-35.5, -26.5), B (-35.5, 26.5), C (35.5, 26.5): 12 sond; kontrola odwrotna dawnych rogów (-42, -42), (-42, 42), (42, 42) na Z −1: 3 sond W)<br>ramka_plytka_wieczorna_n1_v2.stl: 15/15 (znaczniki A (-35.5, -26.5), B (-35.5, 26.5), C (35.5, 26.5): 12 sond; kontrola odwrotna dawnych rogów (-42, -42), (-42, 42), (42, 42) na Z −1: 3 sond W)<br>ramka_plytka_wieczorna_n2_v2.stl: 15/15 (znaczniki A (-35.5, -26.5), B (-35.5, 26.5), C (35.5, 26.5): 12 sond; kontrola odwrotna dawnych rogów (-42, -42), (-42, 42), (42, 42) na Z −1: 3 sond W)<br>ramka_plytka_wieczorna_n3_v2.stl: 15/15 (znaczniki A (-35.5, -26.5), B (-35.5, 26.5), C (35.5, 26.5): 12 sond; kontrola odwrotna dawnych rogów (-42, -42), (-42, 42), (42, 42) na Z −1: 3 sond W)<br>ramka_plytka_poranna_v2.stl: 15/15 (znaczniki A (-34.5, -28), B (-30, 32.5), C (30, 32.5): 12 sond; kontrola odwrotna dawnych rogów (-42, -42), (-42, 42), (42, 42) na Z −1: 3 sond W)<br>ramka_plytka_poranna_n4_v2.stl: 15/15 (znaczniki A (-34.5, -28), B (-30, 32.5), C (30, 32.5): 12 sond; kontrola odwrotna dawnych rogów (-42, -42), (-42, 42), (42, 42) na Z −1: 3 sond W)<br>ramka_plytka_poranna_n5_v2.stl: 15/15 (znaczniki A (-34.5, -28), B (-30, 32.5), C (30, 32.5): 12 sond; kontrola odwrotna dawnych rogów (-42, -42), (-42, 42), (42, 42) na Z −1: 3 sond W)<br>ramka_plytka_poranna_n6_v2.stl: 15/15 (znaczniki A (-34.5, -28), B (-30, 32.5), C (30, 32.5): 12 sond; kontrola odwrotna dawnych rogów (-42, -42), (-42, 42), (42, 42) na Z −1: 3 sond W) | tak; dawne rogi W BRYLE |  |
| K‑10 (B) | ZAL | ramka_plytka_wieczorna_v2.stl: 4/4<br>ramka_plytka_wieczorna_n1_v2.stl: 4/4<br>ramka_plytka_wieczorna_n2_v2.stl: 4/4<br>ramka_plytka_wieczorna_n3_v2.stl: 4/4<br>ramka_plytka_poranna_v2.stl: 4/4<br>ramka_plytka_poranna_n4_v2.stl: 4/4<br>ramka_plytka_poranna_n5_v2.stl: 4/4<br>ramka_plytka_poranna_n6_v2.stl: 4/4 | tak |  |
| K‑11 (B) | ZAL | ramka_plytka_wieczorna_v2.stl: 6/6; dołki zmierzone: A+B+C<br>ramka_plytka_wieczorna_n1_v2.stl: 3/3; dołki zmierzone: A<br>ramka_plytka_wieczorna_n2_v2.stl: 3/3; dołki zmierzone: B<br>ramka_plytka_wieczorna_n3_v2.stl: 3/3; dołki zmierzone: A+B<br>ramka_plytka_poranna_v2.stl: 6/6; dołki zmierzone: A+B+C<br>ramka_plytka_poranna_n4_v2.stl: 3/3; dołki zmierzone: C<br>ramka_plytka_poranna_n5_v2.stl: 3/3; dołki zmierzone: A+C<br>ramka_plytka_poranna_n6_v2.stl: 3/3; dołki zmierzone: B+C | bazowy A+B+C; n1 A, n2 B, n3 A+B, n4 C, n5 A+C, n6 B+C |  |
| K‑12 (B) | ZAL | ramka_plytka_wieczorna_v2.stl: 13/13<br>ramka_plytka_wieczorna_n1_v2.stl: 13/13<br>ramka_plytka_wieczorna_n2_v2.stl: 13/13<br>ramka_plytka_wieczorna_n3_v2.stl: 13/13<br>ramka_plytka_poranna_v2.stl: 13/13<br>ramka_plytka_poranna_n4_v2.stl: 13/13<br>ramka_plytka_poranna_n5_v2.stl: 13/13<br>ramka_plytka_poranna_n6_v2.stl: 13/13 | tak |  |
| K‑13 (B) | ZAL | ramka_plytka_wieczorna_v2.stl: max Z = 0.000<br>ramka_plytka_wieczorna_n1_v2.stl: max Z = 0.600<br>ramka_plytka_wieczorna_n2_v2.stl: max Z = 0.600<br>ramka_plytka_wieczorna_n3_v2.stl: max Z = 0.600<br>ramka_plytka_poranna_v2.stl: max Z = 0.000<br>ramka_plytka_poranna_n4_v2.stl: max Z = 0.600<br>ramka_plytka_poranna_n5_v2.stl: max Z = 0.600<br>ramka_plytka_poranna_n6_v2.stl: max Z = 0.600 | bazowy 0,00 ± 0,02; warianty 0,60 ± 0,05 |  |
| K‑14 (B) | ZAL | ramka_plytka_wieczorna_v2.stl: 16/16<br>ramka_plytka_wieczorna_n1_v2.stl: 16/16<br>ramka_plytka_wieczorna_n2_v2.stl: 16/16<br>ramka_plytka_wieczorna_n3_v2.stl: 16/16<br>ramka_plytka_poranna_v2.stl: 16/16<br>ramka_plytka_poranna_n4_v2.stl: 16/16<br>ramka_plytka_poranna_n5_v2.stl: 16/16<br>ramka_plytka_poranna_n6_v2.stl: 16/16 | tak |  |
| K‑15 (D) | ZAL | ramka_plytka_wieczorna_v2.stl: 3/3<br>ramka_plytka_wieczorna_n1_v2.stl: 3/3<br>ramka_plytka_wieczorna_n2_v2.stl: 3/3<br>ramka_plytka_wieczorna_n3_v2.stl: 3/3<br>ramka_plytka_poranna_v2.stl: 3/3<br>ramka_plytka_poranna_n4_v2.stl: 3/3<br>ramka_plytka_poranna_n5_v2.stl: 3/3<br>ramka_plytka_poranna_n6_v2.stl: 3/3 | tak |  |
| K‑16 (B) | ZAL | wieczorna: dołek–krawędź płytki 2.00 (≥ 1.5); dołek–znacznik 6.62 (≥ 1.5); dołek–gniazdo 9.77 (≥ 3.0); stożek znacznika–krawędź 10.00 (≥ 1.5); kieszeń magnesu–krawędź 3.40 (≥ 1.5); promień znacznika (max) 44.30 (≤ 44.5); znacznik–gniazdo 3.01 (≥ 3.0); znacznik–kieszeń magnesu (XY) 11.71 (≥ 1.5)<br>poranna: dołek–krawędź płytki 2.00 (≥ 1.5); dołek–znacznik 7.19 (≥ 1.5); dołek–gniazdo 11.56 (≥ 3.0); stożek znacznika–krawędź 11.00 (≥ 1.5); kieszeń magnesu–krawędź 3.40 (≥ 1.5); promień znacznika (max) 44.43 (≤ 44.5); znacznik–gniazdo 3.01 (≥ 3.0); znacznik–kieszeń magnesu (XY) 10.21 (≥ 1.5) | ≥ 1,5 / ≥ 3,0 / promień znacznika ≤ socket_zone_r − d/2 [R54] | wieczorna: znaczniki: A (-35.5, -26.5) promień 44.30 ≤ 44.5, do gniazda 3.17 (id 7), do kieszeni magnesu 11.71; B (-35.5, 26.5) promień 44.30 ≤ 44.5, do gniazda 3.01 (id 19), do kieszeni magnesu 11.71; C (35.5, 26.5) promień 44.30 ≤ 44.5, do gniazda 3.01 (id 15), do kieszeni magnesu 11.71; dołek–dołek 1.00 (rozstaw 3.0 − ø2.0, z planu D11; ścianka 1 mm głęb., informacyjnie); dołek–rowek pokrywki: w poziomie 1.20, w pionie 0.50, po przekątnej 1.30 (R47: 1,3 lokalnie)<br>poranna: znaczniki: A (-34.5, -28) promień 44.43 ≤ 44.5, do gniazda 7.00 (id 4), do kieszeni magnesu 10.78; B (-30, 32.5) promień 44.23 ≤ 44.5, do gniazda 3.01 (id 33), do kieszeni magnesu 10.21; C (30, 32.5) promień 44.23 ≤ 44.5, do gniazda 3.01 (id 33), do kieszeni magnesu 10.21; dołek–dołek 1.00 (rozstaw 3.0 − ø2.0, z planu D11; ścianka 1 mm głęb., informacyjnie); dołek–rowek pokrywki: w poziomie 1.20, w pionie 0.50, po przekątnej 1.30 (R47: 1,3 lokalnie) |
| K‑17 (B) | ZAL | ramka_pokrywka_v2.stl: 6/6; kontrola K‑19 (dawne otwory) 3/3 W; kontrola K‑21: wierzch z promieni (|x|, |y| ≤ 40, krok 0,5, 25921 punktów) Z -0.000…0.000 | tak; kontrola K‑19 W; wierzch 0,00 ± 0,02 |  |
| K‑18 (B) | ZAL | ramka_pokrywka_v2.stl: 8/8 | tak |  |
| K‑19 (P) | N/D | — | — | uchylone R50‑U17 (pokrywka bez otworów); kontrola odwrotna w K‑17: 3/3 sond W |
| K‑20 (P) | ZAL | ramka_pokrywka_v2.stl: 4/4 | tak |  |
| K‑21 (D) | N/D | — | — | uchylone R50‑U14 (bez napisu GÓRA); kontrola odwrotna w K‑17: max Z wierzchu 0.000 |
| K‑22 (B) | ZAL | ramka_pokrywka_v2.stl: (48,1) POZA, (48,5) W → wnęka 96,6 ± 0,2 | 48,1 POZA / 48,5 W | część złożeniowa (pokrywka–wkładka, K-53) N/D w etapie A |
| K‑23 (B) | ZAL | ramka_wkladka_v2.stl: 6/6 | tak |  |
| K‑24 (B) | ZAL | ramka_wkladka_v2.stl: 7/7 | tak |  |
| K‑25 (B) | ZAL | ramka_wkladka_v2.stl: 9/9 | tak |  |
| K‑27 (B) | ZAL | ramka_wkladka_v2.stl: 4/4 | tak |  |
| K‑28 (B) | ZAL | ramka_wkladka_v2.stl: 4/4 | tak |  |
| K‑29 (B) | ZAL | ramka_wkladka_v2.stl: 20/20 | tak |  |
| K‑30 (P) | ZAL | ramka_wkladka_v2.stl: 7/7 | tak |  |
| K‑31 (P) | ZAL | ramka_wkladka_v2.stl: max w obszarach strzałek 6.600; max w pasie y −49,95…−48,35 6.000 | 6,6 ± 0,05 / 6,0 ± 0,05; kształt z rzutu PNG | rzut: wyniki_v2/raport/rzuty/rzut_wkladka_strzalki_iter1.png |
| K‑32 (B) | ZAL | ramka_wkladka_v2.stl: (48,2) POZA, (48,6) W → otwór 96,8 ± 0,2 (R53) | 48,2 POZA / 48,6 W; złożenie płytka–wkładka = 0 (K‑53) | część złożeniowa: K‑53, para wkladka–plytka_wieczorna_n1 |
| K‑33 (B) | ZAL | spód wkładki (poza kołkami) 63.600; wierzch dyfuzora 63.600; wierzch blatu 63.600; przecięcia wkładka–blat 0, wkładka–dyfuzor 0; kołki w otworach blatu: tak | 63,6 ± 0,02; 0 przecięć; kołki w otworach |  |
| K‑34 (B) | ZAL | ramka_korpus_W_v2.stl: 10/10<br>ramka_korpus_P_v2.stl: 10/10 | tak |  |
| K‑35 (B) | ZAL | ramka_korpus_W_v2.stl: 17/17<br>ramka_korpus_P_v2.stl: 17/17 | tak |  |
| K‑36 (B) | ZAL | ramka_korpus_W_v2.stl: 16/16<br>ramka_korpus_P_v2.stl: 16/16 | tak |  |
| K‑37 (B) | ZAL | ramka_korpus_W_v2.stl: 12/12<br>ramka_korpus_P_v2.stl: 12/12 | tak |  |
| K‑38 (B) | ZAL | ramka_korpus_W_v2.stl: 24/24<br>ramka_korpus_P_v2.stl: 24/24 | tak |  |
| K‑39 (B) | ZAL | ramka_korpus_W_v2.stl: 13/13<br>ramka_korpus_P_v2.stl: 13/13 | tak |  |
| K‑40 (B) | ZAL | ramka_korpus_W_v2.stl: sondy 7/7; promienie 429/429 trafiają w ścianę, y -100.600…-100.000<br>ramka_korpus_P_v2.stl: sondy 7/7; promienie 429/429 trafiają w ścianę, y -100.600…-100.000 | tak; każdy promień y ∈ [−100,6; −100,0] |  |
| K‑42 (B) | ZAL | ramka_korpus_W_v2.stl: 12/12<br>ramka_korpus_P_v2.stl: 12/12 | tak |  |
| K‑43 (B) | ZAL | W: min Y (Z 46…56) -100.600, (Z 35…41) -100.000; P: -100.600, -100.000; SHA różne: tak; obj. W − P = 0.029 cm³ | −100,6 ± 0,05 / −100,0; SHA ≠; 0 < ΔV < 0,5 | rzuty: wyniki_v2/raport/rzuty/rzut_korpus_W_napis_iter1.png, wyniki_v2/raport/rzuty/rzut_korpus_P_napis_iter1.png |
| K‑44 (P) | ZAL | ramka_korpus_W_v2.stl: 4/4<br>ramka_korpus_P_v2.stl: 4/4 | tak |  |
| K‑44b (B) | ZAL | przecięcia Pi/wtyk (-X) z korpusem, dystansami i panelem: brak; luz Z = 42.000 − 34.000 = 8.000; test 3 kierunków wtyku 40 mm: -X (x -90.0…-50.0, y 17.0…27.0) 0 przecięć; -Y (x -55.0…-45.0, y -18.0…22.0) 0 przecięć; +Y (x -55.0…-45.0, y 22.0…62.0) 0 przecięć | 0 / ≥ 8; 3 kierunki 0 |  |
| K‑45 (B) | ZAL | ramka_blat_v2.stl: 7/7 | tak |  |
| K‑46 (B) | ZAL | ramka_blat_v2.stl: 14/14 | tak |  |
| K‑47 (B) | ZAL | ramka_blat_v2.stl: 19/19; dno otworu kołka: z góry -3.800, z dołu -4.000 | tak; −3,8 ± 0,05 / −4,0 ± 0,05 |  |
| K‑48 (B) | N/D | — | — | uchylone R50‑U1 (rama dyfuzora usunięta; plik nie powstaje) |
| K‑49 (B) | ZAL | kołnierz blatu–ściana korpusu 0.700 (x 96.800 → 97.500); dyfuzor–kieszeń 1.000; spód blatu 59.600 − PCB 55.600 = 4.000; PCB pod oknem: nakładka 1.000/stronę (okno 79.000, PCB 80.000); dystanse (spód / wierzch stadionu pod nim / przecięcia z korpusem): proxy_dystans_1 4.000/4.000/0, proxy_dystans_2 4.000/4.000/0, proxy_dystans_3 4.000/4.000/0, proxy_dystans_4 4.000/4.000/0; przecięcia panel–blat 0, blat–korpus 0 | 0,5 / 1,0; panel–blat ≥ 2 (4,0); nakładka 1,0; dystanse na stadionach Z 4; 0 przecięć |  |
| K‑52 (P) | N/D | — | — | uchylone R50‑U8 (uchwyt kabli usunięty); w zamian K‑52b, K‑52c |
| K‑52b (P) | ZAL | ramka_tulejka_dc_v2.stl: 7/7<br>ramka_tulejka_dc_v2.stl: walec ø 11,848 (4 promienie)<br>ramka_tulejka_dc_v2.stl: otwór ø 8,200 (4 promienie)<br>ramka_tulejka_dc_v2.stl: kołnierz ø 14,999 (4 promienie) | tak |  |
| K‑52c (P) | ZAL | ramka_podkladka_panelu_05_v2.stl: 4/4; gabaryt 9.000 × 8.997 × 0.500<br>ramka_podkladka_panelu_1_v2.stl: 4/4; gabaryt 9.000 × 8.997 × 1.000<br>ramka_podkladka_panelu_2_v2.stl: 4/4; gabaryt 9.000 × 8.997 × 2.000 | tak; gabaryt 9 × 9 × t ± 0,05 |  |
| K‑53 (B) | ZAL | 24 obiektów, 276 par; pary z przecięciami: brak | 0 dla każdej pary | skurcz −0.05 mm wzdłuż normalnych wierzchołków; zestaw: blat, korpus_W, plytka_wieczorna_n1, pokrywka, proxy_dyfuzor, proxy_dystans_1, proxy_dystans_2, proxy_dystans_3, proxy_dystans_4, proxy_gniazdo_dc, proxy_gniazdo_usb, proxy_hall_A, proxy_hall_B, proxy_hall_C, proxy_magnes_A, proxy_panel, proxy_pi_bonnet, proxy_stopka_1, proxy_stopka_2, proxy_stopka_3, proxy_stopka_4, proxy_wtyk_bonnet, tulejka_dc, wkladka<br>kontrola czułości (bez skurczu, pary stykowe): proxy_dystans_1–korpus_W 56; proxy_dystans_1–proxy_panel 81; wkladka–proxy_dyfuzor 180; plytka_wieczorna_n1–wkladka 315; proxy_pi_bonnet–korpus_W 875; tulejka_dc–korpus_W 928; tulejka_dc–proxy_gniazdo_dc 1014<br>informacyjnie (recenzja B iter3 §6.1): odbiornik USB w położeniu hipotetycznym w zestawie W (x 35.0…54.0, Z 8.0…14.0): przecięcia korpus_W 0, proxy_panel 0, proxy_gniazdo_usb 0, proxy_wtyk_bonnet 0, proxy_dystans_1 0, proxy_dystans_2 0, proxy_dystans_3 0, proxy_dystans_4 0; najmniejsza odległość wierzchołków odbiornika: korpus_W 5.00 mm, proxy_dystans_4 49.64 mm |
| K‑54 (B) | ZAL | blat (90, 0) 63.600 (63.60); dyfuzor (0, 70) 63.600 (63.60); rama wkładki (0, 50,3) 69.600 (69.60); płytka n1 (0, −46,5) 74.100 (74.10); pokrywka (40, 40) 90.100 (90.10); min Z pokrywki 70.100 (70.10); max Z proxy_pi_bonnet 34.000 (34.00); min Z proxy_panel 42.000 (42.00); PCB panelu spód (70, 70) 54.000 (54.00); PCB panelu wierzch (70, 70) 55.600 (55.60); szczyt dystansów 54.000 (54.00); stadion: wierzch (−64, 60) 4.000 (4.00); dno obok stadionu (−70, 50) 3.000 (3.00); korpus wierzch 59.600 (59.60); stopki min Z -4.000 (-4.00); stopki max Z 0.000 (0.00) | ± 0,05 |  |
| K‑55 (B) | ZAL | spód magnesu A 66.300 − wierzch czujnika A 65.100 = 1.200; + 0,5 (struktura TO‑92) = 1.700 ≤ 4 | 1,2 ± 0,05 |  |
| K‑56 (B) | ZAL | pas przedni 27.60 mm, prawy 27.61 mm → 11 pełnych pikseli; punktów nad pasem zasłoniętych przez inne części: 0 | 27,6 / 11 |  |
| K‑57 (P) | ZAL | arkusz_zamowienia.csv: 15 wierszy (10 drukarnia + 5 druk własny); max różnica objętości 0.005 cm³, gabarytu 0.003 mm, kosztu względem wzoru 0.004 zł; uwaga STEP/FreeCAD: jest; błędy: brak | 15 wierszy (= quantities); obj. ± 0,01; gabaryt ± 0,1; materiały per część; koszt tylko drukarnia |  |
| K‑58 (P) | ZAL | kody_plytek.md: 6 wierszy; zgodność z K-11 i D11; słowa biegun/S/jednakowy: są; błędy: brak | tak |  |
| K‑59 (B) | N/D | — | SHA każdego STL = raport po przebiegu w czystej kopii | wykonuje recenzent (prompt wykonawcy, etap C); kolejność trójkątów w STL kanoniczna (`stl_kanoniczny`) |
| K‑60 (P) | ZAL | render_rozstrzelony.png 1600 × 1200; render_zlozony.png 1600 × 1200; render_plytki.png 1600 × 1200; podpisy 12/12 z widocznymi częściami (lista kontrolna §11; widoczne próbki: korpus W (napis RAMKA WIECZORNA) 139/407, Pi 4 + Bonnet z wtykiem DC (zastępcze) 9/16, dystanse M3 F-F 50 ×4 na stadionach (zastępcze) 366/648, panel HUB75 (zastępczy) 8/16, blat 175/406, dyfuzor (zastępczy) 6/8, wkładka 107/448, płytka wieczorna n1 132/413, pokrywka 127/412, gniazdo DC (zastępcze) 379/680, tulejka DC 113/443, gniazdo USB (zastępcze) 7/8); K‑xx etapów A+B+C w raporcie: wszystkie; zrzut parametry.json w arkusz_wymiarow.md: zgodny; LICZONE max różnica 0.0000; błędy: brak | 3 PNG ≥ 1600 × 1200; podpisane części z §11 widoczne; raport kompletny; zrzut JSON; LICZONE zgodne |  |

Podsumowanie: B = 0, P = 0, D = 0 (liczba sprawdzeń z wynikiem NIE w każdej wadze).

## 4. Rejestr odstępstw od planu v2 (puste = brak)

| # | Czego dotyczy (sekcja/parametr) | Co zrobiono inaczej | Dlaczego (błąd wykryty przez K‑xx / niemożność) | Wymaga zatwierdzenia na bramce? |
|---|---|---|---|---|
| 1 | R47 / bryła zastępcza gniazda DC: grubość nakrętki | grubość nakrętki = `dc_pocket_wall` (2.0) | plan podaje „nakrętka ø15 × 2”, grubość bez własnego klucza; wartość liczbowo równa | nie — przyjęte informacyjnie (R51) |
| 2 | bryła zastępcza `proxy_odbiornik_usb` (tylko korpus P) | położenie przyjęte: wystaje 19 mm w +X od krawędzi portów Pi (x = 35), oś y = 0, Z 8…14 | plan mówi tylko „dolny port USB Pi”; pozycji portu nie ma w parametrach | nie — przyjęte informacyjnie (R51) |
| 3 | protokół K‑57 / arkusz zamówienia: wzór kosztu pokazowego | najtańszy = obj × szt × `cost_rate_min`…`cost_rate_max`; pokazowy = najtańszy × `cost_dye_factor` × `cost_smooth_factor` dla korpusu i blatu (Z19), części białe bez mnożników | opis K‑57 („koszt_max … × dye dla grafitu × smooth dla korpusu/blatu”) jest niejednoznaczny; przyjęto wzór z planu 12.1 i sekcji 11, zapisany pod tabelą arkusza | nie — informacyjnie |
| 4 | render rozstrzelony (prompt: rozsunięcie wzdłuż Z) | gniazda DC i USB oraz tulejka wysunięte w lewo ekranu (280 mm) przy Z korpusu | w izometrii części wewnątrz korpusu zasłaniają ściany i warstwy wyżej; lista §11 wymaga ich widoczności (K‑60 mierzy widoczność) | nie — informacyjnie |
| 5 | bryła zastępcza gniazda DC z tulejką (K‑53) | bez gwintu ø8 w otworze tulejki | średnica gwintu gniazda nie ma klucza (wynik pomiaru #16) | nie — informacyjnie (do_v3) |
| 6 | plan 4.4 p. 3 i 4.11 (opis) | kołnierz blatu na 95,0…97,0 (z `parametry.json`, R48) | tekst planu: „zrośnięte z kołnierzem 95,2…97,2”, „wnętrze kołnierza 97,2” — opis sprzed R48; STL bez wpływu | nie — do poprawy opisu w planie (do_v3) |
| 7 | K‑59 / `ramka_wkladka_v2.stl` | brak zmian; SHA wkładki może się różnić między przebiegami | różnica tylko w znaku zera (−0,0 / +0,0) zapisanych normalnych (wierzchołki i trójkąty identyczne); normalizacja w `stl_kanoniczny` zmieniłaby bajty wszystkich STL, także zatwierdzonych płytek | nie — rozstrzygnięte przez nadzór po C iter1 (K‑59 kanonicznie; normalizacja w v3, `do_v3.md` #9) |
| 8 | protokół K‑52b, plan 4.x (tulejka DC) — opis | walec ø11,85 z `parametry.json` (R52: `dc_hole_d` − 0,15, luz 0,075/stronę w otworze ø12, reguła 4.8 „wciskane”) | tekst K‑52b („walec ø12 × 2”, „walec r 6”) i opis pliku w planie („walec ø`dc_bush_outer_d` 12”) sprzed R52; sondy K‑52b (r 5,5 W, r 6,8 POZA) bez zmian; w złożeniu walec nie przenika ściany (luz geometryczny 0,075/stronę, K‑53 bez przecięcia) | nie — do poprawy opisu w protokole i planie |

## 5. Odpowiedź na recenzję poprzedniej iteracji (od iteracji 2)

| Id uwagi recenzenta | Co poprawiono | Które K‑xx teraz ZAL |
|---|---|---|
| recenzja B iter3: ZALICZONY (G3′), uwag B/P brak | D §6.1: test informacyjny odbiornika USB w położeniu hipotetycznym w zestawie W (uwaga przy K‑53); D §6.1 i §6.2 wpisane do `do_v3.md` | K‑53 (uwaga) |
| etap C po R50 (polecenie „R50 WPISANE”, pkt 6) | bez uchwytu kabli i ramy dyfuzora; tulejka DC i 3 podkładki panelu (K‑52b, K‑52c); tulejka w zestawie złożonym (K‑53); arkusz zamówienia 15 wierszy, koszt tylko „PA12 drukarnia”, druk własny w osobnym bloku; rendery i lista podpisów wg protokołu §11 po R50 | K‑52b, K‑52c, K‑53, K‑57, K‑60 |

## 6. Co nie zostało zrobione i dlaczego (puste = wszystko)

- K‑59 (powtarzalność) wykonuje recenzent (prompt); wynik w raporcie = N/D.
- Bramka G4b (trzecie oko) — osobna sesja; `arkusz_wymiarow.md` §2–§3 zawiera wymiary i pasowania zmierzone z siatek jako punkt wyjścia.


## 7. Wdrożenie R54 — zmiany wykonawcy (dopisane ręcznie po przebiegu; liczby z sekcji 2–3 i z siatek)

Zakres (zadanie nadzoru 1.11, `R54_wdrozenie_zmiany.md` §5): generator wg R54, nowe pliki płytek; wszystkie pozostałe części bez zmian. Raport powstał z polecenia `--etap C --iter 1 --raport R54` (pełny przebieg od zera: A + B + C, 17 STL, `.blend`, rendery, arkusze), bo K‑53 z nową płytką n1 i arkusze objętości wymagają zestawu złożonego. Kontrola wstępna na parametrach: `node narzedzia/weryfikuj_uklad_R54.js` → „WYNIK: układ zgodny z R54”.

### 7.1 Zmiany w `ramka_generator.py` (SHA przed `b94fd473ddc30d2e3e22197fe7c485d87c596ebde844ca0915d21dc38a516a99` → po `f84e25ee5b77252fe308aab8c215f61fcf7c87d4d2ad6753955106bac9b4e48f`; kopia sprzed: `archiwum/ramka_generator_przed_R54_2026-11-01.py`)

| # | Miejsce | Zmiana |
|---|---|---|
| 1 | `WYMAGANE_KLUCZE` (R14) | dopisane 6 kluczy: `scan_field_d`, `scan_center_tol`, `work_overhang`, `socket_zone_r` (LICZONE — wzór z `parametry.json` sprawdzany jak dotąd: 47,000 → 47,000, różnica 0), `ev_marker_pos`, `mo_marker_pos` |
| 2 | `pozycje_znacznikow(P, typ)` (nowa), `uklad_pochodne(P, typ)` | `markers` z `ev_marker_pos` / `mo_marker_pos` zależnie od typu (walidacja kluczy A, B, C); `magnet_pockets` nadal z `marker_offset` (rogi ±42); `wczytaj_uklad` przekazuje typ |
| 3 | `sprawdz_uklad_json` (K‑05) | (a) oczekiwane liczby round/trough liczone z `ev_rows` / `mo_rows` (nie stałe 24/2, 35/2); (c) dodatkowo dla obu końców osi obrysu √(x² + y²) + r ≤ `socket_zone_r`, raport podaje max promień i id; (d) narożniki bez zmian |
| 4 | `sprawdz_plytke` (K‑09) | sondy 4 × znacznik z pozycji `markers` JSON; kontrola odwrotna: dawne rogi (pozycje `magnet_pockets` w XY: (−42, −42), (−42, 42), (42, 42)) na Z −1 W BRYLE — 3 sondy dodatkowe (15 sond na płytkę zamiast 12) |
| 5 | `sprawdz_scianki_naroznikow` (K‑16) | dodane: promień środka znacznika ≤ `socket_zone_r` − d/2 (44,5), znacznik–gniazdo ≥ `socket_wall_min` 3, znacznik–dołek ≥ 1,5 (wszystkie znaczniki, nie tylko A), znacznik–kieszeń magnesu (XY) ≥ 1,5; usunięte „stożek–kieszeń magnesu (Z)” (Z4 uchylone); uwaga raportu wypisuje każdy znacznik z promieniem, najbliższym gniazdem (id) i odległością do kieszeni |
| 6 | `lista_wymiarow` (arkusz wymiarów) | wiersz „stożek znacznika A ø na wierzchu” mierzony w pozycji z JSON (wieczorna (−35,5, −26,5), poranna (−34,5, −28)) zamiast w rogu (−42, −42); „gniazdo id …” mierzy pierwsze gniazdo OKRĄGŁE (id 1 wieczornej jest teraz rynienką — dawny kod brał `sockets[0]` i przerwał przebieg; błąd własny, poprawiony) |
| 7 | `main`, `zapisz_raport`, `zapisz_readme` | nowy argument `--raport ETYKIETA` (nazwa raportu `raport_wykonawcy_R54_iter1.md`, tytuł i polecenie w sekcji 1, README); w README lista LICZONE uzupełniona o `socket_zone_r` |

Nie zmieniono: budowa płytki (`zbuduj_plytke` czyta `markers` i `magnet_pockets` z JSON — bez edycji), wkładka, pokrywka, blat, korpus, bryły zastępcze, K‑06…K‑08, K‑10…K‑15, K‑17…K‑60.

### 7.2 Archiwum (nic nie usunięte bez kopii)

`archiwum/wyniki_v2_przed_R54_2026-11-01/` (cały folder wyników sprzed przebiegu, stan C iter5), `archiwum/uklad_gniazd_wieczorna_przed_R54_2026-11-01.json` (SHA `83779187…`, układ 24 + 2), `archiwum/uklad_gniazd_poranna_przed_R54_2026-11-01.json` (SHA `3d6aa7ab…`, 35 + 2), `archiwum/sha256_stl_przed_R54_2026-11-01.txt` (17 STL sprzed R54), `archiwum/ramka_generator_przed_R54_2026-11-01.py`, `archiwum/raport_wykonawcy_R54_probaA_iter1_2026-11-01.md` (próbny przebieg samego etapu A przed przebiegiem C: 0 NIE, te same liczby). Stare JSON usunięte z `wyniki_v2/json/`; skrypt odtworzył je z `ev_rows` / `mo_rows` („utworzony z D6”, sekcja 1), `leds` puste, id wg §5 p. 5 (wieczorna 1 rynienka przednia, 2–7 ø12, 8–14 ø9, 15–19 ø15, 20 rynienka tylna; poranna 1–3 ø7,5, 4 rynienka, 5–11 ø10, 12–17 ø12,5, 18–25 ø7,5, 26–32 ø7,5, 33 rynienka).

### 7.3 Wyniki R54 w skrócie (pełne wiersze w sekcji 3, sondy w załączniku A)

| Sprawdzenie | Wieczorna | Poranna | Wymaganie |
|---|---|---|---|
| K‑05 (a) liczba gniazd / rynienek | 18 / 2 (= `ev_rows`) | 31 / 2 (= `mo_rows`) | z `parametry.json` |
| K‑05 (c) max promień obrysu | 46,389 (id 2, ø12 w (37,5, −15)) | 46,931 (id 33, rynienka tylna) | ≤ 47 |
| K‑05 (e) min ścianka gniazdo–gniazdo | 3,000 (id 1–3) | 3,000 (id 1–2) | ≥ 3 |
| K‑09 sondy znaczników + dawne rogi | 15/15 × 4 pliki | 15/15 × 4 pliki | wszystkie; rogi W BRYLE |
| K‑16 promień znacznika | 44,30 / 44,30 / 44,30 | 44,43 / 44,23 / 44,23 | ≤ 44,5 |
| K‑16 znacznik–gniazdo | 3,17 (A, id 7) / 3,01 (B, id 19) / 3,01 (C, id 15) | 7,00 (A, id 4) / 3,01 (B, id 33) / 3,01 (C, id 33) | ≥ 3,0 |
| K‑16 dołek–znacznik / dołek–gniazdo | 6,62 / 9,77 | 7,19 / 11,56 | ≥ 1,5 / ≥ 3,0 |
| K‑16 znacznik–kieszeń magnesu (XY) | 11,71 | 10,78 / 10,21 / 10,21 | ≥ 1,5 |
| K‑53 (zestaw z nową płytką n1) | 24 obiekty, 276 par, 0 przecięć | — | 0 |
| K‑55 magnes–czujnik Halla | 1,200 (66,300 − 65,100) | — | 1,2 ± 0,05 |
| K‑58 kody płytek | zgodne (A; B; A+B) | zgodne (C; A+C; B+C) | = D11 |

Liczby K‑05 (c), K‑16 są co do setnej równe wartościom z D6 i `R54_wdrozenie_zmiany.md` („SPÓJNOŚĆ SPRAWDZONA”). Objętość płytek wzrosła (mniej gniazd): wieczorna 57,94 → 59,30 cm³, poranna 60,22 → 60,86 cm³ (K‑04b nadal w zakresie tabeli 1: 62 / 61 ± 30 %). Razem 0 NIE: 60 sprawdzeń etapów A + B + C w sekcji 3 (55 ZAL, 5 N/D: K‑19, K‑21, K‑48, K‑52 uchylone, K‑59 wykonuje recenzent).

### 7.4 Pliki zmienione i niezmienione (SHA‑256 z siatek po przebiegu; pełna lista 17 STL: `raport/sha256_stl_po_R54_iter1.txt`)

Zmienione (tylko płytki, JSON układów i arkusze):

| Plik | SHA przed R54 (C iter5) | SHA po R54 | Objętość przed → po [cm³] |
|---|---|---|---|
| `stl/ramka_plytka_wieczorna_v2.stl` | `f02aed86…` | `a7ab083e658da206c40e93f18c556988167dae343a5a2a40e2362d06c5929f47` | 57,94 → 59,30 |
| `stl/ramka_plytka_wieczorna_n1_v2.stl` | `b2803c82…` | `515d32d3dd8a69ae0a94d293a639b201f2d9ce9af19df664ad1b44b59408f775` | 57,95 → 59,31 |
| `stl/ramka_plytka_wieczorna_n2_v2.stl` | `8bab264c…` | `360cff9ddd6bbcf8a84b463fed930532612a38118006f1550c2df01b02fa852d` | 57,95 → 59,31 |
| `stl/ramka_plytka_wieczorna_n3_v2.stl` | `d3a44e8d…` | `2fc7040e212ace4a8efda17f61909ca09563009513adcd82ecf5bcaac3e98aaf` | 57,95 → 59,31 |
| `stl/ramka_plytka_poranna_v2.stl` | `5767cf1d…` | `c3536c64b3ac143160f6db4a80ab1530f8442ba4d538369a536d2228579783d8` | 60,22 → 60,86 |
| `stl/ramka_plytka_poranna_n4_v2.stl` | `3186d1ab…` | `a8d07cbeb0dafc0e55d3fe2fe516c7d3e854a6259bce587785b796d34b54c65e` | 60,23 → 60,87 |
| `stl/ramka_plytka_poranna_n5_v2.stl` | `70bd4dd4…` | `159503ca4cd66b90a1e2441cae64016901ed83390b48a27345f9484ac1a05830` | 60,23 → 60,87 |
| `stl/ramka_plytka_poranna_n6_v2.stl` | `562d23f6…` | `0d5d712d42084a19846f24d385484d01b2254c5c1ec3945d71cfd3493816f15e` | 60,23 → 60,87 |
| `json/uklad_gniazd_wieczorna.json` | `83779187…` (24 + 2) | `a4648f3562105bb19809bd7671e6421461f51fa2a4f29b5ecf0e1d6f29d1fb1e` (18 + 2) | — |
| `json/uklad_gniazd_poranna.json` | `3d6aa7ab…` (35 + 2) | `6e8290c3a7c4becd3b065f8ccd39da9e8f8a2f0cb9bab6a1464fbcda84995812` (31 + 2) | — |
| `arkusze/arkusz_zamowienia.csv/.md`, `arkusze/arkusz_wymiarow.md`, `ramka_v2.blend`, `render/*.png`, `README.md`, `do_v3.md` | — | sekcja 2 | objętości płytek jw.; arkusz wymiarów: 0 pozycji ✗ |

`arkusze/kody_plytek.md`: SHA `5822f0f7…` — bajtowo identyczny z poprzednim (treść nie zależy od układu gniazd).

Niezmienione — SHA po przebiegu R54 bajtowo RÓWNE SHA sprzed R54 (`archiwum/sha256_stl_przed_R54_2026-11-01.txt` = raport C iter5 z 31.10):

| Plik | SHA‑256 (przed = po) |
|---|---|
| `stl/ramka_korpus_W_v2.stl` | `bd55871c88cf2604c1c8efa5035148ba39c3803a0788015cc35548e8e9afff9a` |
| `stl/ramka_korpus_P_v2.stl` | `aadb91c9364cf39f1f4062d328616aa518e474b957315ed4a941de4f935ab2b7` |
| `stl/ramka_blat_v2.stl` | `8c48856eb9addee2b37cfa5a03e5686ab7670bd92b724e488ccc8d8dd3a4b418` |
| `stl/ramka_wkladka_v2.stl` | `f4196fbc640450998634f50caa86051f89df2cbb2c218e317f5c2b193e3ef92b` (patrz uwaga niżej) |
| `stl/ramka_pokrywka_v2.stl` | `ad23444483ac95733e92169af00e5271d8fc3b19a91854e8c8acddf06c8cd454` |
| `stl/ramka_tulejka_dc_v2.stl` | `b393256cd8cafdac6d125d6f9f25647c5f94840d1bc5eb87941b436f510bcc00` |
| `stl/ramka_podkladka_panelu_05_v2.stl` | `4260d1f1957f32d101cae5da2cf4634e24239caf738592edd7007fc0728ec6b4` |
| `stl/ramka_podkladka_panelu_1_v2.stl` | `e79a805121499f8d65b7d23ef6d2ae255549b4f55579ded7061b8996b91c9b78` |
| `stl/ramka_podkladka_panelu_2_v2.stl` | `9c47aea4fbc946c16dab3813561d936745b88afde6092542de1d67a21656d5b5` |

Uwaga do wkładki (odstępstwo #7 w sekcji 4, znane od B3): przebieg C wykonano trzykrotnie (poprawki tekstu README między przebiegami); 16 pozostałych STL były bajtowo identyczne w każdym przebiegu, wkładka miała SHA `386e0d21…`, `de0d26c5…`, `f4196fbc…`. Porównanie siatek (skrypt na binarnym STL, 1806 trójkątów): kolejność trójkątów, współrzędne wierzchołków i normalne identyczne z plikiem sprzed R54 we wszystkich trzech wariantach; różnica wyłącznie w znaku zera (−0,0 / +0,0) składowych normalnych. Pokrywka, tulejka i podkładki są też bajtowo identyczne z `archiwum/sha256_stl_przed_R53.txt`.

### 7.5 Do planu / protokołu / dokumentów (rozbieżności i uwagi; nic nie zmieniono w `plan_ramki_v2.md`, `parametry.json`, `protokol_weryfikacji_v2.md`)

1. Wzorzec SHA części niezmienionych: zadanie wskazuje `archiwum/sha256_stl_przed_R53.txt`, ale ten plik jest sprzed R53 i dla blatu, korpusów W/P i wkładki ma inne sumy (R53 zmienił te części: T1–T5, luz wkładki 0,4). Właściwy wzorzec „przed R54” to raport C iter5 (31.10) = `archiwum/sha256_stl_przed_R54_2026-11-01.txt`; z nim zgodność 9/9 (tabela wyżej).
2. `00_PRZEPLYW_I_BRAMKI.md` §3 (tabela G0, wiersz Z20/D6) nadal podaje „[cytat usuniety]”; §2 i prompt wykonawcy opisują etapy bez `--raport`. Dokumenty właściciela — do aktualizacji przy okazji dokumentów stanowiska (§6 `R54_wdrozenie_zmiany.md`).
3. Protokół K‑05 (c): wartości oczekiwane „wieczorna max 46,39, poranna 46,93” potwierdzone z JSON (46,389 / 46,931). Protokół K‑16: oczekiwane 3,17/3,01/3,01 i 7,00/3,01/3,01 potwierdzone. Bez rozbieżności.
4. Tabela 1 protokołu (K‑04b, objętości orientacyjne płytek 62 / 61 cm³): po R54 płytki mają 59,3 / 60,9 cm³ — nadal w ± 30 %, zmiana tabeli niepotrzebna.
5. Arkusz wymiarów: pozycja „gniazdo id …” płytki wieczornej mierzy teraz id 2 (ø12 w (37,5, −15)), bo id 1 to rynienka; porannej id 1 (ø7,5). Protokół nie precyzuje, które gniazdo — informacyjnie.
6. Model 3D (`ramka_3d.html`, artefakt v3), animacja, pakiet `Ramki_pakiet/` i dokumenty stanowiska / „Zakupy i druk” nadal pokazują dawny układ 24 + 2 / 35 + 2 — poza zakresem tego zadania (§6 `R54_wdrozenie_zmiany.md`), wymagają osobnej sesji po recenzji płytek.
7. Rendery i `ramka_v2.blend` w `wyniki_v2/` zostały odtworzone w tym przebiegu z nowymi płytkami (zestaw złożony z `plytka_wieczorna_n1` po R54); K‑60 ZAL (12/12 podpisów widocznych).

Gotowe do komunikatu: `RECENZJA R54, iteracja 1. Raport wykonawcy: wyniki_v2/raport/raport_wykonawcy_R54_iter1.md` (zakres recenzji wg §5 p. 7: K‑01…K‑04b dla 8 STL płytek, K‑05…K‑16, K‑58, K‑53 z nową n1, K‑55; SHA 9 części niezmienionych).

## Załącznik A. Wszystkie sondy (układ montażowy części)

Metoda `w_bryle`: parzystość przecięć promienia w 3 kierunkach (+X, +Y, +Z, każdy odchylony o ~0,1° od osi, żeby nie trafiać w krawędzie siatki), wynik większościowy; „głosy” = liczba kierunków z nieparzystą liczbą przecięć. Odległość = `BVHTree.find_nearest` do siatki; < 0,1 mm oznaczone *.

| K | Plik | Punkt (x, y, z) | Oczekiwane | Wynik | Głosy | Odl. [mm] | Zgodna |
|---|---|---|---|---|---|---|---|
| K‑06 | ramka_plytka_wieczorna_v2.stl | (37.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (37.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (37.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (39.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (45.1, -15, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (22.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (22.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (22.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (24.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (30.1, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (7.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (7.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (7.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (9.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (15.1, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-7.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-7.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-7.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-5.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (0.1, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-22.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-22.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-22.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-20.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-14.9, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-37.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-37.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-37.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-35.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-29.9, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (36, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (36, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (36, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (38, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (42.1, -1.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (24, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (24, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (24, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (26, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (30.1, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (12, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (12, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (12, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (14, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (18.1, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (0, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (0, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (0, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (2, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (6.1, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-12, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-12, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-12, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-10, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-5.9, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-24, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-24, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-24, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-22, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-17.9, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-36, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-36, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-36, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-34, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-29.9, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (36, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (36, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (36, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (38, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (45.1, 13.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (18, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (18, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (18, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (20, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (27.1, 13.5, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (0, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (0, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (0, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (2, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (9.1, 13.5, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-18, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-18, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-18, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-16, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-8.9, 13.5, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-36, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-36, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-36, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-34, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_v2.stl | (-26.9, 13.5, -2) | W | W | 3/3 | 1.870 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (42.815, -15, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (43.115, -15, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (27.815, -15, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (28.115, -15, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (12.815, -15, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (13.115, -15, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (39.815, -1.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (40.115, -1.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (27.815, -1.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (28.115, -1.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (15.815, -1.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (16.115, -1.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (42.815, 13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (43.115, 13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (24.815, 13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (25.115, 13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (6.815, 13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_v2.stl | (7.115, 13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (0, -31.5, -2) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (29, -31.5, -2) | POZA | POZA | 0/3 | 0.447 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (-29, -31.5, -2) | POZA | POZA | 0/3 | 0.447 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (29.5, -24.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (31.6, -31.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (0, -31.5, -6) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (-18, -31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (-6, -31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (6, -31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (18, -31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (0, 31.5, -2) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (29, 31.5, -2) | POZA | POZA | 0/3 | 0.447 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (-29, 31.5, -2) | POZA | POZA | 0/3 | 0.447 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (29.5, 38.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (31.6, 31.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (0, 31.5, -6) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (-18, 31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (-6, 31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (6, 31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_v2.stl | (18, 31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑09 | ramka_plytka_wieczorna_v2.stl | (-35.5, -26.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_wieczorna_v2.stl | (-35.5, -26.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_wieczorna_v2.stl | (-34, -26.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_wieczorna_v2.stl | (-32.8, -26.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_wieczorna_v2.stl | (-35.5, 26.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_wieczorna_v2.stl | (-35.5, 26.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_wieczorna_v2.stl | (-34, 26.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_wieczorna_v2.stl | (-32.8, 26.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_wieczorna_v2.stl | (35.5, 26.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_wieczorna_v2.stl | (35.5, 26.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_wieczorna_v2.stl | (37, 26.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_wieczorna_v2.stl | (38.2, 26.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_wieczorna_v2.stl | (-42, -42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑09 | ramka_plytka_wieczorna_v2.stl | (-42, 42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑09 | ramka_plytka_wieczorna_v2.stl | (42, 42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑10 | ramka_plytka_wieczorna_v2.stl | (45.5, -45, -4) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑10 | ramka_plytka_wieczorna_v2.stl | (45.5, -45, -7.9) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑10 | ramka_plytka_wieczorna_v2.stl | (41.5, -45, -4) | W | W | 3/3 | 1.500 | tak |
| K‑10 | ramka_plytka_wieczorna_v2.stl | (45.5, -41.5, -4) | W | W | 3/3 | 1.500 | tak |
| K‑11 | ramka_plytka_wieczorna_v2.stl | (-45, -36, -0.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑11 | ramka_plytka_wieczorna_v2.stl | (-45, -36, -1.3) | W | W | 3/3 | 0.300 | tak |
| K‑11 | ramka_plytka_wieczorna_v2.stl | (-45, -33, -0.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑11 | ramka_plytka_wieczorna_v2.stl | (-45, -33, -1.3) | W | W | 3/3 | 0.300 | tak |
| K‑11 | ramka_plytka_wieczorna_v2.stl | (-45, -30, -0.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑11 | ramka_plytka_wieczorna_v2.stl | (-45, -30, -1.3) | W | W | 3/3 | 0.300 | tak |
| K‑12 | ramka_plytka_wieczorna_v2.stl | (-42, -42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_wieczorna_v2.stl | (-42, -42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_v2.stl | (-39.55, -42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_wieczorna_v2.stl | (-39.2, -42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_v2.stl | (-42, 42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_wieczorna_v2.stl | (-42, 42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_v2.stl | (-39.55, 42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_wieczorna_v2.stl | (-39.2, 42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_v2.stl | (42, 42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_wieczorna_v2.stl | (42, 42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_v2.stl | (44.45, 42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_wieczorna_v2.stl | (44.8, 42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_v2.stl | (42, -42, -7) | W | W | 3/3 | 1.000 | tak |
| K‑14 | ramka_plytka_wieczorna_v2.stl | (47.5, 0, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_v2.stl | (46.9, 0, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_v2.stl | (47.5, 0, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_v2.stl | (47.5, 0, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_v2.stl | (0, 47.5, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_v2.stl | (0, 46.9, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_v2.stl | (0, 47.5, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_v2.stl | (0, 47.5, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_v2.stl | (-47.5, 0, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_v2.stl | (-46.9, 0, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_v2.stl | (-47.5, 0, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_v2.stl | (-47.5, 0, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_v2.stl | (0, -47.5, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_v2.stl | (0, -46.9, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_v2.stl | (0, -47.5, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_v2.stl | (0, -47.5, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑15 | ramka_plytka_wieczorna_v2.stl | (47.8, 47.8, -4) | POZA | POZA | 0/3 | 0.138 | tak |
| K‑15 | ramka_plytka_wieczorna_v2.stl | (47.9, 0, -0.05) | POZA | POZA | 0/3 | 0.248 | tak |
| K‑15 | ramka_plytka_wieczorna_v2.stl | (47.9, 0, -1) | W | W | 3/3 | 0.100 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (37.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (37.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (37.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (39.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (45.1, -15, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (22.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (22.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (22.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (24.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (30.1, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (7.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (7.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (7.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (9.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (15.1, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-7.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-7.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-7.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-5.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (0.1, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-22.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-22.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-22.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-20.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-14.9, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-37.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-37.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-37.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-35.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-29.9, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (36, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (36, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (36, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (38, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (42.1, -1.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (24, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (24, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (24, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (26, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (30.1, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (12, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (12, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (12, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (14, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (18.1, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (0, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (0, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (0, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (2, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (6.1, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-12, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-12, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-12, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-10, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-5.9, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-24, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-24, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-24, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-22, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-17.9, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-36, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-36, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-36, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-34, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-29.9, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (36, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (36, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (36, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (38, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (45.1, 13.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (18, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (18, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (18, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (20, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (27.1, 13.5, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (0, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (0, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (0, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (2, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (9.1, 13.5, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-18, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-18, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-18, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-16, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-8.9, 13.5, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-36, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-36, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-36, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-34, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n1_v2.stl | (-26.9, 13.5, -2) | W | W | 3/3 | 1.870 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (42.815, -15, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (43.115, -15, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (27.815, -15, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (28.115, -15, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (12.815, -15, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (13.115, -15, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (39.815, -1.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (40.115, -1.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (27.815, -1.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (28.115, -1.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (15.815, -1.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (16.115, -1.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (42.815, 13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (43.115, 13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (24.815, 13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (25.115, 13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (6.815, 13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n1_v2.stl | (7.115, 13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (0, -31.5, -2) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (29, -31.5, -2) | POZA | POZA | 0/3 | 0.447 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (-29, -31.5, -2) | POZA | POZA | 0/3 | 0.447 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (29.5, -24.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (31.6, -31.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (0, -31.5, -6) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (-18, -31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (-6, -31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (6, -31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (18, -31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (0, 31.5, -2) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (29, 31.5, -2) | POZA | POZA | 0/3 | 0.447 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (-29, 31.5, -2) | POZA | POZA | 0/3 | 0.447 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (29.5, 38.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (31.6, 31.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (0, 31.5, -6) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (-18, 31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (-6, 31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (6, 31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n1_v2.stl | (18, 31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑09 | ramka_plytka_wieczorna_n1_v2.stl | (-35.5, -26.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_wieczorna_n1_v2.stl | (-35.5, -26.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_wieczorna_n1_v2.stl | (-34, -26.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_wieczorna_n1_v2.stl | (-32.8, -26.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_wieczorna_n1_v2.stl | (-35.5, 26.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_wieczorna_n1_v2.stl | (-35.5, 26.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_wieczorna_n1_v2.stl | (-34, 26.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_wieczorna_n1_v2.stl | (-32.8, 26.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_wieczorna_n1_v2.stl | (35.5, 26.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_wieczorna_n1_v2.stl | (35.5, 26.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_wieczorna_n1_v2.stl | (37, 26.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_wieczorna_n1_v2.stl | (38.2, 26.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_wieczorna_n1_v2.stl | (-42, -42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑09 | ramka_plytka_wieczorna_n1_v2.stl | (-42, 42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑09 | ramka_plytka_wieczorna_n1_v2.stl | (42, 42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑10 | ramka_plytka_wieczorna_n1_v2.stl | (45.5, -45, -4) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑10 | ramka_plytka_wieczorna_n1_v2.stl | (45.5, -45, -7.9) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑10 | ramka_plytka_wieczorna_n1_v2.stl | (41.5, -45, -4) | W | W | 3/3 | 1.500 | tak |
| K‑10 | ramka_plytka_wieczorna_n1_v2.stl | (45.5, -41.5, -4) | W | W | 3/3 | 1.500 | tak |
| K‑11 | ramka_plytka_wieczorna_n1_v2.stl | (-45, -36, -0.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑11 | ramka_plytka_wieczorna_n1_v2.stl | (-45, -33, -0.5) | W | W | 3/3 | 0.500 | tak |
| K‑11 | ramka_plytka_wieczorna_n1_v2.stl | (-45, -30, -0.5) | W | W | 3/3 | 0.500 | tak |
| K‑12 | ramka_plytka_wieczorna_n1_v2.stl | (-42, -42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n1_v2.stl | (-42, -42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n1_v2.stl | (-39.55, -42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_wieczorna_n1_v2.stl | (-39.2, -42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n1_v2.stl | (-42, 42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n1_v2.stl | (-42, 42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n1_v2.stl | (-39.55, 42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_wieczorna_n1_v2.stl | (-39.2, 42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n1_v2.stl | (42, 42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n1_v2.stl | (42, 42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n1_v2.stl | (44.45, 42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_wieczorna_n1_v2.stl | (44.8, 42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n1_v2.stl | (42, -42, -7) | W | W | 3/3 | 1.000 | tak |
| K‑14 | ramka_plytka_wieczorna_n1_v2.stl | (47.5, 0, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n1_v2.stl | (46.9, 0, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n1_v2.stl | (47.5, 0, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n1_v2.stl | (47.5, 0, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n1_v2.stl | (0, 47.5, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n1_v2.stl | (0, 46.9, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n1_v2.stl | (0, 47.5, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n1_v2.stl | (0, 47.5, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n1_v2.stl | (-47.5, 0, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n1_v2.stl | (-46.9, 0, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n1_v2.stl | (-47.5, 0, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n1_v2.stl | (-47.5, 0, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n1_v2.stl | (0, -47.5, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n1_v2.stl | (0, -46.9, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n1_v2.stl | (0, -47.5, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n1_v2.stl | (0, -47.5, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑15 | ramka_plytka_wieczorna_n1_v2.stl | (47.8, 47.8, -4) | POZA | POZA | 0/3 | 0.138 | tak |
| K‑15 | ramka_plytka_wieczorna_n1_v2.stl | (47.9, 0, -0.05) | POZA | POZA | 0/3 | 0.248 | tak |
| K‑15 | ramka_plytka_wieczorna_n1_v2.stl | (47.9, 0, -1) | W | W | 3/3 | 0.100 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (37.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (37.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (37.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (39.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (45.1, -15, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (22.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (22.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (22.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (24.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (30.1, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (7.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (7.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (7.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (9.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (15.1, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-7.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-7.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-7.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-5.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (0.1, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-22.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-22.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-22.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-20.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-14.9, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-37.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-37.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-37.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-35.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-29.9, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (36, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (36, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (36, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (38, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (42.1, -1.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (24, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (24, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (24, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (26, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (30.1, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (12, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (12, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (12, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (14, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (18.1, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (0, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (0, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (0, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (2, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (6.1, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-12, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-12, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-12, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-10, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-5.9, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-24, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-24, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-24, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-22, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-17.9, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-36, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-36, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-36, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-34, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-29.9, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (36, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (36, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (36, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (38, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (45.1, 13.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (18, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (18, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (18, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (20, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (27.1, 13.5, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (0, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (0, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (0, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (2, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (9.1, 13.5, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-18, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-18, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-18, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-16, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-8.9, 13.5, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-36, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-36, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-36, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-34, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n2_v2.stl | (-26.9, 13.5, -2) | W | W | 3/3 | 1.870 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (42.815, -15, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (43.115, -15, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (27.815, -15, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (28.115, -15, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (12.815, -15, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (13.115, -15, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (39.815, -1.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (40.115, -1.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (27.815, -1.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (28.115, -1.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (15.815, -1.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (16.115, -1.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (42.815, 13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (43.115, 13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (24.815, 13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (25.115, 13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (6.815, 13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n2_v2.stl | (7.115, 13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (0, -31.5, -2) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (29, -31.5, -2) | POZA | POZA | 0/3 | 0.447 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (-29, -31.5, -2) | POZA | POZA | 0/3 | 0.447 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (29.5, -24.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (31.6, -31.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (0, -31.5, -6) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (-18, -31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (-6, -31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (6, -31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (18, -31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (0, 31.5, -2) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (29, 31.5, -2) | POZA | POZA | 0/3 | 0.447 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (-29, 31.5, -2) | POZA | POZA | 0/3 | 0.447 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (29.5, 38.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (31.6, 31.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (0, 31.5, -6) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (-18, 31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (-6, 31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (6, 31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n2_v2.stl | (18, 31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑09 | ramka_plytka_wieczorna_n2_v2.stl | (-35.5, -26.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_wieczorna_n2_v2.stl | (-35.5, -26.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_wieczorna_n2_v2.stl | (-34, -26.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_wieczorna_n2_v2.stl | (-32.8, -26.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_wieczorna_n2_v2.stl | (-35.5, 26.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_wieczorna_n2_v2.stl | (-35.5, 26.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_wieczorna_n2_v2.stl | (-34, 26.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_wieczorna_n2_v2.stl | (-32.8, 26.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_wieczorna_n2_v2.stl | (35.5, 26.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_wieczorna_n2_v2.stl | (35.5, 26.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_wieczorna_n2_v2.stl | (37, 26.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_wieczorna_n2_v2.stl | (38.2, 26.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_wieczorna_n2_v2.stl | (-42, -42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑09 | ramka_plytka_wieczorna_n2_v2.stl | (-42, 42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑09 | ramka_plytka_wieczorna_n2_v2.stl | (42, 42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑10 | ramka_plytka_wieczorna_n2_v2.stl | (45.5, -45, -4) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑10 | ramka_plytka_wieczorna_n2_v2.stl | (45.5, -45, -7.9) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑10 | ramka_plytka_wieczorna_n2_v2.stl | (41.5, -45, -4) | W | W | 3/3 | 1.500 | tak |
| K‑10 | ramka_plytka_wieczorna_n2_v2.stl | (45.5, -41.5, -4) | W | W | 3/3 | 1.500 | tak |
| K‑11 | ramka_plytka_wieczorna_n2_v2.stl | (-45, -36, -0.5) | W | W | 3/3 | 0.500 | tak |
| K‑11 | ramka_plytka_wieczorna_n2_v2.stl | (-45, -33, -0.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑11 | ramka_plytka_wieczorna_n2_v2.stl | (-45, -30, -0.5) | W | W | 3/3 | 0.500 | tak |
| K‑12 | ramka_plytka_wieczorna_n2_v2.stl | (-42, -42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n2_v2.stl | (-42, -42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n2_v2.stl | (-39.55, -42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_wieczorna_n2_v2.stl | (-39.2, -42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n2_v2.stl | (-42, 42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n2_v2.stl | (-42, 42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n2_v2.stl | (-39.55, 42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_wieczorna_n2_v2.stl | (-39.2, 42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n2_v2.stl | (42, 42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n2_v2.stl | (42, 42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n2_v2.stl | (44.45, 42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_wieczorna_n2_v2.stl | (44.8, 42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n2_v2.stl | (42, -42, -7) | W | W | 3/3 | 1.000 | tak |
| K‑14 | ramka_plytka_wieczorna_n2_v2.stl | (47.5, 0, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n2_v2.stl | (46.9, 0, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n2_v2.stl | (47.5, 0, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n2_v2.stl | (47.5, 0, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n2_v2.stl | (0, 47.5, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n2_v2.stl | (0, 46.9, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n2_v2.stl | (0, 47.5, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n2_v2.stl | (0, 47.5, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n2_v2.stl | (-47.5, 0, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n2_v2.stl | (-46.9, 0, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n2_v2.stl | (-47.5, 0, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n2_v2.stl | (-47.5, 0, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n2_v2.stl | (0, -47.5, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n2_v2.stl | (0, -46.9, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n2_v2.stl | (0, -47.5, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n2_v2.stl | (0, -47.5, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑15 | ramka_plytka_wieczorna_n2_v2.stl | (47.8, 47.8, -4) | POZA | POZA | 0/3 | 0.138 | tak |
| K‑15 | ramka_plytka_wieczorna_n2_v2.stl | (47.9, 0, -0.05) | POZA | POZA | 0/3 | 0.248 | tak |
| K‑15 | ramka_plytka_wieczorna_n2_v2.stl | (47.9, 0, -1) | W | W | 3/3 | 0.100 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (37.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (37.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (37.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (39.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (45.1, -15, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (22.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (22.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (22.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (24.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (30.1, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (7.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (7.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (7.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (9.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (15.1, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-7.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-7.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-7.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-5.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (0.1, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-22.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-22.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-22.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-20.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-14.9, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-37.5, -15, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-37.5, -15, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-37.5, -15, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-35.5, -15, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-29.9, -15, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (36, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (36, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (36, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (38, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (42.1, -1.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (24, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (24, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (24, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (26, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (30.1, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (12, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (12, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (12, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (14, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (18.1, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (0, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (0, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (0, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (2, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (6.1, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-12, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-12, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-12, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-10, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-5.9, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-24, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-24, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-24, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-22, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-17.9, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-36, -1.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-36, -1.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-36, -1.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-34, -1.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-29.9, -1.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (36, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (36, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (36, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (38, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (45.1, 13.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (18, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (18, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (18, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (20, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (27.1, 13.5, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (0, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (0, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (0, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (2, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (9.1, 13.5, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-18, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-18, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-18, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-16, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-8.9, 13.5, -2) | W | W | 3/3 | 1.870 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-36, 13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-36, 13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-36, 13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-34, 13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_wieczorna_n3_v2.stl | (-26.9, 13.5, -2) | W | W | 3/3 | 1.870 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (42.815, -15, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (43.115, -15, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (27.815, -15, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (28.115, -15, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (12.815, -15, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (13.115, -15, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (39.815, -1.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (40.115, -1.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (27.815, -1.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (28.115, -1.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (15.815, -1.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (16.115, -1.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (42.815, 13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (43.115, 13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (24.815, 13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (25.115, 13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (6.815, 13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_wieczorna_n3_v2.stl | (7.115, 13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (0, -31.5, -2) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (29, -31.5, -2) | POZA | POZA | 0/3 | 0.447 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (-29, -31.5, -2) | POZA | POZA | 0/3 | 0.447 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (29.5, -24.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (31.6, -31.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (0, -31.5, -6) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (-18, -31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (-6, -31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (6, -31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (18, -31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (0, 31.5, -2) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (29, 31.5, -2) | POZA | POZA | 0/3 | 0.447 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (-29, 31.5, -2) | POZA | POZA | 0/3 | 0.447 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (29.5, 38.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (31.6, 31.5, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (0, 31.5, -6) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (-18, 31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (-6, 31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (6, 31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_wieczorna_n3_v2.stl | (18, 31.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑09 | ramka_plytka_wieczorna_n3_v2.stl | (-35.5, -26.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_wieczorna_n3_v2.stl | (-35.5, -26.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_wieczorna_n3_v2.stl | (-34, -26.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_wieczorna_n3_v2.stl | (-32.8, -26.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_wieczorna_n3_v2.stl | (-35.5, 26.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_wieczorna_n3_v2.stl | (-35.5, 26.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_wieczorna_n3_v2.stl | (-34, 26.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_wieczorna_n3_v2.stl | (-32.8, 26.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_wieczorna_n3_v2.stl | (35.5, 26.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_wieczorna_n3_v2.stl | (35.5, 26.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_wieczorna_n3_v2.stl | (37, 26.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_wieczorna_n3_v2.stl | (38.2, 26.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_wieczorna_n3_v2.stl | (-42, -42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑09 | ramka_plytka_wieczorna_n3_v2.stl | (-42, 42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑09 | ramka_plytka_wieczorna_n3_v2.stl | (42, 42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑10 | ramka_plytka_wieczorna_n3_v2.stl | (45.5, -45, -4) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑10 | ramka_plytka_wieczorna_n3_v2.stl | (45.5, -45, -7.9) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑10 | ramka_plytka_wieczorna_n3_v2.stl | (41.5, -45, -4) | W | W | 3/3 | 1.500 | tak |
| K‑10 | ramka_plytka_wieczorna_n3_v2.stl | (45.5, -41.5, -4) | W | W | 3/3 | 1.500 | tak |
| K‑11 | ramka_plytka_wieczorna_n3_v2.stl | (-45, -36, -0.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑11 | ramka_plytka_wieczorna_n3_v2.stl | (-45, -33, -0.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑11 | ramka_plytka_wieczorna_n3_v2.stl | (-45, -30, -0.5) | W | W | 3/3 | 0.500 | tak |
| K‑12 | ramka_plytka_wieczorna_n3_v2.stl | (-42, -42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n3_v2.stl | (-42, -42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n3_v2.stl | (-39.55, -42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_wieczorna_n3_v2.stl | (-39.2, -42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n3_v2.stl | (-42, 42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n3_v2.stl | (-42, 42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n3_v2.stl | (-39.55, 42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_wieczorna_n3_v2.stl | (-39.2, 42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n3_v2.stl | (42, 42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n3_v2.stl | (42, 42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n3_v2.stl | (44.45, 42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_wieczorna_n3_v2.stl | (44.8, 42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_wieczorna_n3_v2.stl | (42, -42, -7) | W | W | 3/3 | 1.000 | tak |
| K‑14 | ramka_plytka_wieczorna_n3_v2.stl | (47.5, 0, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n3_v2.stl | (46.9, 0, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n3_v2.stl | (47.5, 0, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n3_v2.stl | (47.5, 0, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n3_v2.stl | (0, 47.5, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n3_v2.stl | (0, 46.9, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n3_v2.stl | (0, 47.5, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n3_v2.stl | (0, 47.5, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n3_v2.stl | (-47.5, 0, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n3_v2.stl | (-46.9, 0, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n3_v2.stl | (-47.5, 0, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n3_v2.stl | (-47.5, 0, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n3_v2.stl | (0, -47.5, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n3_v2.stl | (0, -46.9, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_wieczorna_n3_v2.stl | (0, -47.5, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_wieczorna_n3_v2.stl | (0, -47.5, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑15 | ramka_plytka_wieczorna_n3_v2.stl | (47.8, 47.8, -4) | POZA | POZA | 0/3 | 0.138 | tak |
| K‑15 | ramka_plytka_wieczorna_n3_v2.stl | (47.9, 0, -0.05) | POZA | POZA | 0/3 | 0.248 | tak |
| K‑15 | ramka_plytka_wieczorna_n3_v2.stl | (47.9, 0, -1) | W | W | 3/3 | 0.100 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (10.5, -41.25, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (10.5, -41.25, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (10.5, -41.25, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (12.5, -41.25, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (15.85, -41.25, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (0, -41.25, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (0, -41.25, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (0, -41.25, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (2, -41.25, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (5.35, -41.25, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-10.5, -41.25, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-10.5, -41.25, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-10.5, -41.25, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-8.5, -41.25, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-5.15, -41.25, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (39, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (39, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (39, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (41, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (45.6, -13.5, -2) | W | W | 3/3 | 1.600 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (26, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (26, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (26, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (28, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (32.6, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (13, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (13, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (13, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (15, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (19.6, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (0, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (0, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (0, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (2, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (6.6, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-13, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-13, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-13, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-11, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-6.4, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-26, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-26, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-26, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-24, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-19.4, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-39, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-39, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-39, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-37, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-32.4, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (38.75, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (38.75, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (38.75, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (40.75, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (46.6, 0.75, -2) | W | W | 3/3 | 0.600 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (23.25, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (23.25, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (23.25, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (25.25, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (31.1, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (7.75, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (7.75, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (7.75, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (9.75, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (15.6, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-7.75, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-7.75, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-7.75, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-5.75, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (0.1, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-23.25, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-23.25, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-23.25, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-21.25, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-15.4, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-38.75, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-38.75, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-38.75, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-36.75, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-30.9, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (36.75, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (36.75, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (36.75, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (38.75, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (42.1, 13.6, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (26.25, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (26.25, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (26.25, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (28.25, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (31.6, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (15.75, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (15.75, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (15.75, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (17.75, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (21.1, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (5.25, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (5.25, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (5.25, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (7.25, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (10.6, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-5.25, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-5.25, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-5.25, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-3.25, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (0.1, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-15.75, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-15.75, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-15.75, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-13.75, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-10.4, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-26.25, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-26.25, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-26.25, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-24.25, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-20.9, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-36.75, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-36.75, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-36.75, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-34.75, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-31.4, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (31.5, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (31.5, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (31.5, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (33.5, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (36.85, 22.7, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (21, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (21, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (21, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (23, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (26.35, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (10.5, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (10.5, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (10.5, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (12.5, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (15.85, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (0, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (0, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (0, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (2, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (5.35, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-10.5, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-10.5, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-10.5, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-8.5, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-5.15, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-21, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-21, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-21, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-19, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-15.65, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-31.5, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-31.5, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-31.5, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-29.5, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_v2.stl | (-26.15, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (13.565, -41.25, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (13.865, -41.25, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (3.065, -41.25, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (3.365, -41.25, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (-7.435, -41.25, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (-7.135, -41.25, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (43.315, -13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (43.615, -13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (30.315, -13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (30.615, -13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (17.315, -13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (17.615, -13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (44.315, 0.75, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (44.615, 0.75, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (28.815, 0.75, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (29.115, 0.75, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (13.315, 0.75, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_v2.stl | (13.615, 0.75, -2) | W | W | 3/3 | 0.145 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (0, -28, -2) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (24, -28, -2) | POZA | POZA | 0/3 | 0.448 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (-24, -28, -2) | POZA | POZA | 0/3 | 0.448 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (24.5, -22, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (26.6, -28, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (0, -28, -6) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (-15, -28, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (-5, -28, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (5, -28, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (15, -28, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (0, 35.95, -2) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (24, 35.95, -2) | POZA | POZA | 0/3 | 0.448 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (-24, 35.95, -2) | POZA | POZA | 0/3 | 0.448 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (24.5, 41.95, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (26.6, 35.95, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (0, 35.95, -6) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (-15, 35.95, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (-5, 35.95, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (5, 35.95, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_v2.stl | (15, 35.95, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑09 | ramka_plytka_poranna_v2.stl | (-34.5, -28, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_poranna_v2.stl | (-34.5, -28, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_poranna_v2.stl | (-33, -28, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_poranna_v2.stl | (-31.8, -28, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_poranna_v2.stl | (-30, 32.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_poranna_v2.stl | (-30, 32.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_poranna_v2.stl | (-28.5, 32.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_poranna_v2.stl | (-27.3, 32.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_poranna_v2.stl | (30, 32.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_poranna_v2.stl | (30, 32.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_poranna_v2.stl | (31.5, 32.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_poranna_v2.stl | (32.7, 32.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_poranna_v2.stl | (-42, -42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑09 | ramka_plytka_poranna_v2.stl | (-42, 42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑09 | ramka_plytka_poranna_v2.stl | (42, 42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑10 | ramka_plytka_poranna_v2.stl | (45.5, -45, -4) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑10 | ramka_plytka_poranna_v2.stl | (45.5, -45, -7.9) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑10 | ramka_plytka_poranna_v2.stl | (41.5, -45, -4) | W | W | 3/3 | 1.500 | tak |
| K‑10 | ramka_plytka_poranna_v2.stl | (45.5, -41.5, -4) | W | W | 3/3 | 1.500 | tak |
| K‑11 | ramka_plytka_poranna_v2.stl | (-45, -36, -0.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑11 | ramka_plytka_poranna_v2.stl | (-45, -36, -1.3) | W | W | 3/3 | 0.300 | tak |
| K‑11 | ramka_plytka_poranna_v2.stl | (-45, -33, -0.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑11 | ramka_plytka_poranna_v2.stl | (-45, -33, -1.3) | W | W | 3/3 | 0.300 | tak |
| K‑11 | ramka_plytka_poranna_v2.stl | (-45, -30, -0.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑11 | ramka_plytka_poranna_v2.stl | (-45, -30, -1.3) | W | W | 3/3 | 0.300 | tak |
| K‑12 | ramka_plytka_poranna_v2.stl | (-42, -42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_poranna_v2.stl | (-42, -42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_v2.stl | (-39.55, -42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_poranna_v2.stl | (-39.2, -42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_v2.stl | (-42, 42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_poranna_v2.stl | (-42, 42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_v2.stl | (-39.55, 42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_poranna_v2.stl | (-39.2, 42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_v2.stl | (42, 42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_poranna_v2.stl | (42, 42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_v2.stl | (44.45, 42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_poranna_v2.stl | (44.8, 42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_v2.stl | (42, -42, -7) | W | W | 3/3 | 1.000 | tak |
| K‑14 | ramka_plytka_poranna_v2.stl | (47.5, 0, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_v2.stl | (46.9, 0, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_v2.stl | (47.5, 0, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_v2.stl | (47.5, 0, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_v2.stl | (0, 47.5, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_v2.stl | (0, 46.9, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_v2.stl | (0, 47.5, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_v2.stl | (0, 47.5, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_v2.stl | (-47.5, 0, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_v2.stl | (-46.9, 0, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_v2.stl | (-47.5, 0, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_v2.stl | (-47.5, 0, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_v2.stl | (0, -47.5, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_v2.stl | (0, -46.9, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_v2.stl | (0, -47.5, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_v2.stl | (0, -47.5, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑15 | ramka_plytka_poranna_v2.stl | (47.8, 47.8, -4) | POZA | POZA | 0/3 | 0.138 | tak |
| K‑15 | ramka_plytka_poranna_v2.stl | (47.9, 0, -0.05) | POZA | POZA | 0/3 | 0.248 | tak |
| K‑15 | ramka_plytka_poranna_v2.stl | (47.9, 0, -1) | W | W | 3/3 | 0.100 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (10.5, -41.25, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (10.5, -41.25, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (10.5, -41.25, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (12.5, -41.25, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (15.85, -41.25, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (0, -41.25, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (0, -41.25, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (0, -41.25, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (2, -41.25, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (5.35, -41.25, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-10.5, -41.25, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-10.5, -41.25, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-10.5, -41.25, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-8.5, -41.25, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-5.15, -41.25, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (39, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (39, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (39, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (41, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (45.6, -13.5, -2) | W | W | 3/3 | 1.600 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (26, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (26, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (26, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (28, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (32.6, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (13, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (13, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (13, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (15, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (19.6, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (0, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (0, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (0, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (2, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (6.6, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-13, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-13, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-13, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-11, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-6.4, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-26, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-26, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-26, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-24, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-19.4, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-39, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-39, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-39, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-37, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-32.4, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (38.75, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (38.75, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (38.75, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (40.75, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (46.6, 0.75, -2) | W | W | 3/3 | 0.600 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (23.25, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (23.25, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (23.25, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (25.25, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (31.1, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (7.75, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (7.75, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (7.75, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (9.75, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (15.6, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-7.75, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-7.75, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-7.75, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-5.75, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (0.1, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-23.25, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-23.25, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-23.25, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-21.25, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-15.4, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-38.75, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-38.75, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-38.75, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-36.75, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-30.9, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (36.75, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (36.75, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (36.75, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (38.75, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (42.1, 13.6, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (26.25, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (26.25, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (26.25, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (28.25, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (31.6, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (15.75, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (15.75, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (15.75, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (17.75, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (21.1, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (5.25, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (5.25, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (5.25, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (7.25, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (10.6, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-5.25, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-5.25, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-5.25, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-3.25, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (0.1, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-15.75, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-15.75, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-15.75, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-13.75, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-10.4, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-26.25, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-26.25, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-26.25, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-24.25, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-20.9, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-36.75, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-36.75, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-36.75, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-34.75, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-31.4, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (31.5, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (31.5, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (31.5, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (33.5, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (36.85, 22.7, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (21, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (21, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (21, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (23, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (26.35, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (10.5, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (10.5, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (10.5, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (12.5, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (15.85, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (0, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (0, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (0, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (2, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (5.35, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-10.5, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-10.5, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-10.5, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-8.5, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-5.15, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-21, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-21, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-21, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-19, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-15.65, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-31.5, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-31.5, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-31.5, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-29.5, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n4_v2.stl | (-26.15, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (13.565, -41.25, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (13.865, -41.25, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (3.065, -41.25, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (3.365, -41.25, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (-7.435, -41.25, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (-7.135, -41.25, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (43.315, -13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (43.615, -13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (30.315, -13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (30.615, -13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (17.315, -13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (17.615, -13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (44.315, 0.75, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (44.615, 0.75, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (28.815, 0.75, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (29.115, 0.75, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (13.315, 0.75, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n4_v2.stl | (13.615, 0.75, -2) | W | W | 3/3 | 0.145 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (0, -28, -2) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (24, -28, -2) | POZA | POZA | 0/3 | 0.448 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (-24, -28, -2) | POZA | POZA | 0/3 | 0.448 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (24.5, -22, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (26.6, -28, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (0, -28, -6) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (-15, -28, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (-5, -28, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (5, -28, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (15, -28, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (0, 35.95, -2) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (24, 35.95, -2) | POZA | POZA | 0/3 | 0.448 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (-24, 35.95, -2) | POZA | POZA | 0/3 | 0.448 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (24.5, 41.95, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (26.6, 35.95, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (0, 35.95, -6) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (-15, 35.95, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (-5, 35.95, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (5, 35.95, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n4_v2.stl | (15, 35.95, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑09 | ramka_plytka_poranna_n4_v2.stl | (-34.5, -28, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_poranna_n4_v2.stl | (-34.5, -28, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_poranna_n4_v2.stl | (-33, -28, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_poranna_n4_v2.stl | (-31.8, -28, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_poranna_n4_v2.stl | (-30, 32.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_poranna_n4_v2.stl | (-30, 32.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_poranna_n4_v2.stl | (-28.5, 32.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_poranna_n4_v2.stl | (-27.3, 32.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_poranna_n4_v2.stl | (30, 32.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_poranna_n4_v2.stl | (30, 32.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_poranna_n4_v2.stl | (31.5, 32.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_poranna_n4_v2.stl | (32.7, 32.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_poranna_n4_v2.stl | (-42, -42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑09 | ramka_plytka_poranna_n4_v2.stl | (-42, 42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑09 | ramka_plytka_poranna_n4_v2.stl | (42, 42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑10 | ramka_plytka_poranna_n4_v2.stl | (45.5, -45, -4) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑10 | ramka_plytka_poranna_n4_v2.stl | (45.5, -45, -7.9) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑10 | ramka_plytka_poranna_n4_v2.stl | (41.5, -45, -4) | W | W | 3/3 | 1.500 | tak |
| K‑10 | ramka_plytka_poranna_n4_v2.stl | (45.5, -41.5, -4) | W | W | 3/3 | 1.500 | tak |
| K‑11 | ramka_plytka_poranna_n4_v2.stl | (-45, -36, -0.5) | W | W | 3/3 | 0.500 | tak |
| K‑11 | ramka_plytka_poranna_n4_v2.stl | (-45, -33, -0.5) | W | W | 3/3 | 0.500 | tak |
| K‑11 | ramka_plytka_poranna_n4_v2.stl | (-45, -30, -0.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑12 | ramka_plytka_poranna_n4_v2.stl | (-42, -42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_poranna_n4_v2.stl | (-42, -42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n4_v2.stl | (-39.55, -42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_poranna_n4_v2.stl | (-39.2, -42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n4_v2.stl | (-42, 42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_poranna_n4_v2.stl | (-42, 42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n4_v2.stl | (-39.55, 42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_poranna_n4_v2.stl | (-39.2, 42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n4_v2.stl | (42, 42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_poranna_n4_v2.stl | (42, 42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n4_v2.stl | (44.45, 42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_poranna_n4_v2.stl | (44.8, 42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n4_v2.stl | (42, -42, -7) | W | W | 3/3 | 1.000 | tak |
| K‑14 | ramka_plytka_poranna_n4_v2.stl | (47.5, 0, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n4_v2.stl | (46.9, 0, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n4_v2.stl | (47.5, 0, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n4_v2.stl | (47.5, 0, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n4_v2.stl | (0, 47.5, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n4_v2.stl | (0, 46.9, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n4_v2.stl | (0, 47.5, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n4_v2.stl | (0, 47.5, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n4_v2.stl | (-47.5, 0, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n4_v2.stl | (-46.9, 0, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n4_v2.stl | (-47.5, 0, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n4_v2.stl | (-47.5, 0, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n4_v2.stl | (0, -47.5, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n4_v2.stl | (0, -46.9, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n4_v2.stl | (0, -47.5, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n4_v2.stl | (0, -47.5, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑15 | ramka_plytka_poranna_n4_v2.stl | (47.8, 47.8, -4) | POZA | POZA | 0/3 | 0.138 | tak |
| K‑15 | ramka_plytka_poranna_n4_v2.stl | (47.9, 0, -0.05) | POZA | POZA | 0/3 | 0.248 | tak |
| K‑15 | ramka_plytka_poranna_n4_v2.stl | (47.9, 0, -1) | W | W | 3/3 | 0.100 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (10.5, -41.25, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (10.5, -41.25, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (10.5, -41.25, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (12.5, -41.25, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (15.85, -41.25, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (0, -41.25, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (0, -41.25, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (0, -41.25, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (2, -41.25, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (5.35, -41.25, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-10.5, -41.25, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-10.5, -41.25, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-10.5, -41.25, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-8.5, -41.25, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-5.15, -41.25, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (39, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (39, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (39, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (41, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (45.6, -13.5, -2) | W | W | 3/3 | 1.600 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (26, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (26, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (26, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (28, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (32.6, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (13, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (13, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (13, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (15, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (19.6, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (0, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (0, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (0, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (2, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (6.6, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-13, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-13, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-13, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-11, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-6.4, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-26, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-26, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-26, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-24, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-19.4, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-39, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-39, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-39, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-37, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-32.4, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (38.75, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (38.75, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (38.75, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (40.75, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (46.6, 0.75, -2) | W | W | 3/3 | 0.600 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (23.25, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (23.25, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (23.25, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (25.25, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (31.1, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (7.75, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (7.75, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (7.75, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (9.75, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (15.6, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-7.75, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-7.75, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-7.75, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-5.75, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (0.1, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-23.25, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-23.25, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-23.25, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-21.25, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-15.4, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-38.75, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-38.75, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-38.75, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-36.75, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-30.9, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (36.75, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (36.75, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (36.75, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (38.75, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (42.1, 13.6, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (26.25, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (26.25, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (26.25, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (28.25, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (31.6, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (15.75, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (15.75, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (15.75, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (17.75, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (21.1, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (5.25, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (5.25, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (5.25, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (7.25, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (10.6, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-5.25, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-5.25, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-5.25, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-3.25, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (0.1, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-15.75, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-15.75, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-15.75, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-13.75, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-10.4, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-26.25, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-26.25, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-26.25, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-24.25, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-20.9, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-36.75, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-36.75, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-36.75, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-34.75, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-31.4, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (31.5, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (31.5, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (31.5, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (33.5, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (36.85, 22.7, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (21, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (21, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (21, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (23, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (26.35, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (10.5, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (10.5, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (10.5, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (12.5, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (15.85, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (0, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (0, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (0, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (2, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (5.35, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-10.5, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-10.5, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-10.5, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-8.5, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-5.15, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-21, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-21, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-21, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-19, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-15.65, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-31.5, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-31.5, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-31.5, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-29.5, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n5_v2.stl | (-26.15, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (13.565, -41.25, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (13.865, -41.25, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (3.065, -41.25, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (3.365, -41.25, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (-7.435, -41.25, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (-7.135, -41.25, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (43.315, -13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (43.615, -13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (30.315, -13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (30.615, -13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (17.315, -13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (17.615, -13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (44.315, 0.75, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (44.615, 0.75, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (28.815, 0.75, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (29.115, 0.75, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (13.315, 0.75, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n5_v2.stl | (13.615, 0.75, -2) | W | W | 3/3 | 0.145 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (0, -28, -2) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (24, -28, -2) | POZA | POZA | 0/3 | 0.448 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (-24, -28, -2) | POZA | POZA | 0/3 | 0.448 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (24.5, -22, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (26.6, -28, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (0, -28, -6) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (-15, -28, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (-5, -28, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (5, -28, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (15, -28, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (0, 35.95, -2) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (24, 35.95, -2) | POZA | POZA | 0/3 | 0.448 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (-24, 35.95, -2) | POZA | POZA | 0/3 | 0.448 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (24.5, 41.95, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (26.6, 35.95, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (0, 35.95, -6) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (-15, 35.95, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (-5, 35.95, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (5, 35.95, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n5_v2.stl | (15, 35.95, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑09 | ramka_plytka_poranna_n5_v2.stl | (-34.5, -28, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_poranna_n5_v2.stl | (-34.5, -28, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_poranna_n5_v2.stl | (-33, -28, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_poranna_n5_v2.stl | (-31.8, -28, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_poranna_n5_v2.stl | (-30, 32.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_poranna_n5_v2.stl | (-30, 32.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_poranna_n5_v2.stl | (-28.5, 32.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_poranna_n5_v2.stl | (-27.3, 32.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_poranna_n5_v2.stl | (30, 32.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_poranna_n5_v2.stl | (30, 32.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_poranna_n5_v2.stl | (31.5, 32.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_poranna_n5_v2.stl | (32.7, 32.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_poranna_n5_v2.stl | (-42, -42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑09 | ramka_plytka_poranna_n5_v2.stl | (-42, 42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑09 | ramka_plytka_poranna_n5_v2.stl | (42, 42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑10 | ramka_plytka_poranna_n5_v2.stl | (45.5, -45, -4) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑10 | ramka_plytka_poranna_n5_v2.stl | (45.5, -45, -7.9) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑10 | ramka_plytka_poranna_n5_v2.stl | (41.5, -45, -4) | W | W | 3/3 | 1.500 | tak |
| K‑10 | ramka_plytka_poranna_n5_v2.stl | (45.5, -41.5, -4) | W | W | 3/3 | 1.500 | tak |
| K‑11 | ramka_plytka_poranna_n5_v2.stl | (-45, -36, -0.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑11 | ramka_plytka_poranna_n5_v2.stl | (-45, -33, -0.5) | W | W | 3/3 | 0.500 | tak |
| K‑11 | ramka_plytka_poranna_n5_v2.stl | (-45, -30, -0.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑12 | ramka_plytka_poranna_n5_v2.stl | (-42, -42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_poranna_n5_v2.stl | (-42, -42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n5_v2.stl | (-39.55, -42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_poranna_n5_v2.stl | (-39.2, -42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n5_v2.stl | (-42, 42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_poranna_n5_v2.stl | (-42, 42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n5_v2.stl | (-39.55, 42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_poranna_n5_v2.stl | (-39.2, 42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n5_v2.stl | (42, 42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_poranna_n5_v2.stl | (42, 42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n5_v2.stl | (44.45, 42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_poranna_n5_v2.stl | (44.8, 42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n5_v2.stl | (42, -42, -7) | W | W | 3/3 | 1.000 | tak |
| K‑14 | ramka_plytka_poranna_n5_v2.stl | (47.5, 0, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n5_v2.stl | (46.9, 0, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n5_v2.stl | (47.5, 0, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n5_v2.stl | (47.5, 0, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n5_v2.stl | (0, 47.5, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n5_v2.stl | (0, 46.9, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n5_v2.stl | (0, 47.5, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n5_v2.stl | (0, 47.5, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n5_v2.stl | (-47.5, 0, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n5_v2.stl | (-46.9, 0, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n5_v2.stl | (-47.5, 0, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n5_v2.stl | (-47.5, 0, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n5_v2.stl | (0, -47.5, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n5_v2.stl | (0, -46.9, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n5_v2.stl | (0, -47.5, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n5_v2.stl | (0, -47.5, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑15 | ramka_plytka_poranna_n5_v2.stl | (47.8, 47.8, -4) | POZA | POZA | 0/3 | 0.138 | tak |
| K‑15 | ramka_plytka_poranna_n5_v2.stl | (47.9, 0, -0.05) | POZA | POZA | 0/3 | 0.248 | tak |
| K‑15 | ramka_plytka_poranna_n5_v2.stl | (47.9, 0, -1) | W | W | 3/3 | 0.100 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (10.5, -41.25, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (10.5, -41.25, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (10.5, -41.25, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (12.5, -41.25, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (15.85, -41.25, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (0, -41.25, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (0, -41.25, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (0, -41.25, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (2, -41.25, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (5.35, -41.25, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-10.5, -41.25, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-10.5, -41.25, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-10.5, -41.25, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-8.5, -41.25, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-5.15, -41.25, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (39, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (39, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (39, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (41, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (45.6, -13.5, -2) | W | W | 3/3 | 1.600 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (26, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (26, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (26, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (28, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (32.6, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (13, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (13, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (13, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (15, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (19.6, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (0, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (0, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (0, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (2, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (6.6, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-13, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-13, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-13, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-11, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-6.4, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-26, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-26, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-26, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-24, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-19.4, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-39, -13.5, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-39, -13.5, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-39, -13.5, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-37, -13.5, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-32.4, -13.5, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (38.75, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (38.75, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (38.75, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (40.75, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (46.6, 0.75, -2) | W | W | 3/3 | 0.600 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (23.25, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (23.25, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (23.25, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (25.25, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (31.1, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (7.75, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (7.75, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (7.75, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (9.75, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (15.6, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-7.75, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-7.75, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-7.75, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-5.75, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (0.1, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-23.25, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-23.25, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-23.25, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-21.25, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-15.4, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-38.75, 0.75, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-38.75, 0.75, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-38.75, 0.75, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-36.75, 0.75, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-30.9, 0.75, -2) | W | W | 3/3 | 1.869 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (36.75, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (36.75, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (36.75, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (38.75, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (42.1, 13.6, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (26.25, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (26.25, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (26.25, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (28.25, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (31.6, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (15.75, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (15.75, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (15.75, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (17.75, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (21.1, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (5.25, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (5.25, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (5.25, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (7.25, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (10.6, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-5.25, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-5.25, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-5.25, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-3.25, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (0.1, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-15.75, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-15.75, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-15.75, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-13.75, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-10.4, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-26.25, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-26.25, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-26.25, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-24.25, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-20.9, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-36.75, 13.6, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-36.75, 13.6, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-36.75, 13.6, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-34.75, 13.6, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-31.4, 13.6, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (31.5, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (31.5, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (31.5, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (33.5, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (36.85, 22.7, -2) | W | W | 3/3 | 2.000 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (21, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (21, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (21, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (23, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (26.35, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (10.5, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (10.5, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (10.5, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (12.5, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (15.85, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (0, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (0, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (0, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (2, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (5.35, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-10.5, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-10.5, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-10.5, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-8.5, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-5.15, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-21, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-21, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-21, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-19, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-15.65, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-31.5, 22.7, -2) | POZA | POZA | 0/3 | 2.497 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-31.5, 22.7, -3.9) | POZA | POZA | 0/3 | 1.498 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-31.5, 22.7, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-29.5, 22.7, -6) | W | W | 3/3 | 0.500 | tak |
| K‑06 | ramka_plytka_poranna_n6_v2.stl | (-26.15, 22.7, -2) | W | W | 3/3 | 1.871 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (13.565, -41.25, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (13.865, -41.25, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (3.065, -41.25, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (3.365, -41.25, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (-7.435, -41.25, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (-7.135, -41.25, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (43.315, -13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (43.615, -13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (30.315, -13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (30.615, -13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (17.315, -13.5, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (17.615, -13.5, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (44.315, 0.75, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (44.615, 0.75, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (28.815, 0.75, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (29.115, 0.75, -2) | W | W | 3/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (13.315, 0.75, -2) | POZA | POZA | 0/3 | 0.145 | tak |
| K‑07 | ramka_plytka_poranna_n6_v2.stl | (13.615, 0.75, -2) | W | W | 3/3 | 0.145 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (0, -28, -2) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (24, -28, -2) | POZA | POZA | 0/3 | 0.448 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (-24, -28, -2) | POZA | POZA | 0/3 | 0.448 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (24.5, -22, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (26.6, -28, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (0, -28, -6) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (-15, -28, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (-5, -28, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (5, -28, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (15, -28, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (0, 35.95, -2) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (24, 35.95, -2) | POZA | POZA | 0/3 | 0.448 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (-24, 35.95, -2) | POZA | POZA | 0/3 | 0.448 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (24.5, 41.95, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (26.6, 35.95, -2) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (0, 35.95, -6) | W | W | 3/3 | 2.000 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (-15, 35.95, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (-5, 35.95, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (5, 35.95, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑08 | ramka_plytka_poranna_n6_v2.stl | (15, 35.95, -6) | POZA | POZA | 0/3 | 1.495 | tak |
| K‑09 | ramka_plytka_poranna_n6_v2.stl | (-34.5, -28, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_poranna_n6_v2.stl | (-34.5, -28, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_poranna_n6_v2.stl | (-33, -28, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_poranna_n6_v2.stl | (-31.8, -28, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_poranna_n6_v2.stl | (-30, 32.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_poranna_n6_v2.stl | (-30, 32.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_poranna_n6_v2.stl | (-28.5, 32.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_poranna_n6_v2.stl | (-27.3, 32.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_poranna_n6_v2.stl | (30, 32.5, -1) | POZA | POZA | 0/3 | 1.279 | tak |
| K‑09 | ramka_plytka_poranna_n6_v2.stl | (30, 32.5, -3.3) | W | W | 3/3 | 0.300 | tak |
| K‑09 | ramka_plytka_poranna_n6_v2.stl | (31.5, 32.5, -1) | POZA | POZA | 0/3 | 0.128 | tak |
| K‑09 | ramka_plytka_poranna_n6_v2.stl | (32.7, 32.5, -1) | W | W | 3/3 | 0.794 | tak |
| K‑09 | ramka_plytka_poranna_n6_v2.stl | (-42, -42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑09 | ramka_plytka_poranna_n6_v2.stl | (-42, 42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑09 | ramka_plytka_poranna_n6_v2.stl | (42, 42, -1) | W | W | 3/3 | 1.000 | tak |
| K‑10 | ramka_plytka_poranna_n6_v2.stl | (45.5, -45, -4) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑10 | ramka_plytka_poranna_n6_v2.stl | (45.5, -45, -7.9) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑10 | ramka_plytka_poranna_n6_v2.stl | (41.5, -45, -4) | W | W | 3/3 | 1.500 | tak |
| K‑10 | ramka_plytka_poranna_n6_v2.stl | (45.5, -41.5, -4) | W | W | 3/3 | 1.500 | tak |
| K‑11 | ramka_plytka_poranna_n6_v2.stl | (-45, -36, -0.5) | W | W | 3/3 | 0.500 | tak |
| K‑11 | ramka_plytka_poranna_n6_v2.stl | (-45, -33, -0.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑11 | ramka_plytka_poranna_n6_v2.stl | (-45, -30, -0.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑12 | ramka_plytka_poranna_n6_v2.stl | (-42, -42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_poranna_n6_v2.stl | (-42, -42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n6_v2.stl | (-39.55, -42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_poranna_n6_v2.stl | (-39.2, -42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n6_v2.stl | (-42, 42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_poranna_n6_v2.stl | (-42, 42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n6_v2.stl | (-39.55, 42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_poranna_n6_v2.stl | (-39.2, 42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n6_v2.stl | (42, 42, -7) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑12 | ramka_plytka_poranna_n6_v2.stl | (42, 42, -5.6) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n6_v2.stl | (44.45, 42, -7) | POZA | POZA | 0/3 | 0.150 | tak |
| K‑12 | ramka_plytka_poranna_n6_v2.stl | (44.8, 42, -7) | W | W | 3/3 | 0.200 | tak |
| K‑12 | ramka_plytka_poranna_n6_v2.stl | (42, -42, -7) | W | W | 3/3 | 1.000 | tak |
| K‑14 | ramka_plytka_poranna_n6_v2.stl | (47.5, 0, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n6_v2.stl | (46.9, 0, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n6_v2.stl | (47.5, 0, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n6_v2.stl | (47.5, 0, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n6_v2.stl | (0, 47.5, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n6_v2.stl | (0, 46.9, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n6_v2.stl | (0, 47.5, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n6_v2.stl | (0, 47.5, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n6_v2.stl | (-47.5, 0, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n6_v2.stl | (-46.9, 0, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n6_v2.stl | (-47.5, 0, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n6_v2.stl | (-47.5, 0, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n6_v2.stl | (0, -47.5, -2) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n6_v2.stl | (0, -46.9, -2) | W | W | 3/3 | 0.300 | tak |
| K‑14 | ramka_plytka_poranna_n6_v2.stl | (0, -47.5, -0.8) | W | W | 3/3 | 0.500 | tak |
| K‑14 | ramka_plytka_poranna_n6_v2.stl | (0, -47.5, -3.2) | W | W | 3/3 | 0.500 | tak |
| K‑15 | ramka_plytka_poranna_n6_v2.stl | (47.8, 47.8, -4) | POZA | POZA | 0/3 | 0.138 | tak |
| K‑15 | ramka_plytka_poranna_n6_v2.stl | (47.9, 0, -0.05) | POZA | POZA | 0/3 | 0.248 | tak |
| K‑15 | ramka_plytka_poranna_n6_v2.stl | (47.9, 0, -1) | W | W | 3/3 | 0.100 | tak |
| K‑17 | ramka_pokrywka_v2.stl | (0, 0, -1) | W | W | 3/3 | 1.000 | tak |
| K‑17 | ramka_pokrywka_v2.stl | (0, 0, -2.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑17 | ramka_pokrywka_v2.stl | (48.1, 0, -10) | POZA | POZA | 0/3 | 0.200 | tak |
| K‑17 | ramka_pokrywka_v2.stl | (48.5, 0, -10) | W | W | 3/3 | 0.200 | tak |
| K‑17 | ramka_pokrywka_v2.stl | (50, 0, -10) | POZA | POZA | 0/3 | 0.200 | tak |
| K‑17 | ramka_pokrywka_v2.stl | (0, 0, -19.9) | POZA | POZA | 0/3 | 17.900 | tak |
| K‑17 | ramka_pokrywka_v2.stl | (15, 0, -1) | W | W | 3/3 | 1.000 | tak |
| K‑17 | ramka_pokrywka_v2.stl | (15, 30, -1) | W | W | 3/3 | 1.000 | tak |
| K‑17 | ramka_pokrywka_v2.stl | (-15, -30, -1) | W | W | 3/3 | 1.000 | tak |
| K‑18 | ramka_pokrywka_v2.stl | (47.8, 0, -18) | W | W | 3/3 | 0.193 | tak |
| K‑18 | ramka_pokrywka_v2.stl | (47.8, 20, -18) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑18 | ramka_pokrywka_v2.stl | (-47.8, 0, -18) | W | W | 3/3 | 0.193 | tak |
| K‑18 | ramka_pokrywka_v2.stl | (25, -47.8, -18) | W | W | 3/3 | 0.193 | tak |
| K‑18 | ramka_pokrywka_v2.stl | (0, -47.8, -18) | POZA | POZA | 0/3 | 1.118 | tak |
| K‑18 | ramka_pokrywka_v2.stl | (-25, 47.8, -18) | W | W | 3/3 | 0.193 | tak |
| K‑18 | ramka_pokrywka_v2.stl | (25, 47.8, -18) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑18 | ramka_pokrywka_v2.stl | (47.8, 0, -16.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑20 | ramka_pokrywka_v2.stl | (0, -49, -19) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑20 | ramka_pokrywka_v2.stl | (20, -49, -19) | W | W | 3/3 | 0.700 | tak |
| K‑20 | ramka_pokrywka_v2.stl | (0, 49, -19) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑20 | ramka_pokrywka_v2.stl | (0, -49, -16) | W | W | 3/3 | 0.700 | tak |
| K‑23 | ramka_wkladka_v2.stl | (48.2, 0, 3) | POZA | POZA | 0/3 | 0.200 | tak |
| K‑23 | ramka_wkladka_v2.stl | (48.6, 0, 3) | W | W | 3/3 | 0.200 | tak |
| K‑23 | ramka_wkladka_v2.stl | (52.6, 0, 3) | POZA | POZA | 0/3 | 0.200 | tak |
| K‑23 | ramka_wkladka_v2.stl | (48.6, 0, 5.9) | POZA | POZA | 0/3 | 0.495 | tak |
| K‑23 | ramka_wkladka_v2.stl | (49.5, 0, 5.9) | W | W | 3/3 | 0.100 | tak |
| K‑23 | ramka_wkladka_v2.stl | (0, 0, 3) | POZA | POZA | 0/3 | 48.400 | tak |
| K‑24 | ramka_wkladka_v2.stl | (-38, -38, 1.5) | W | W | 3/3 | 1.000 | tak |
| K‑24 | ramka_wkladka_v2.stl | (-38, -38, 3) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑24 | ramka_wkladka_v2.stl | (38, 38, 1.5) | W | W | 3/3 | 1.000 | tak |
| K‑24 | ramka_wkladka_v2.stl | (-38, 38, 1.5) | W | W | 3/3 | 1.000 | tak |
| K‑24 | ramka_wkladka_v2.stl | (38, -38, 1.5) | W | W | 3/3 | 1.000 | tak |
| K‑24 | ramka_wkladka_v2.stl | (-30, -30, 1.5) | POZA | POZA | 0/3 | 9.051 | tak |
| K‑24 | ramka_wkladka_v2.stl | (-35.5, -35.5, 1.5) | POZA | POZA | 0/3 | 1.273 | tak |
| K‑25 | ramka_wkladka_v2.stl | (-42, -42, 1.5) | POZA | POZA | 0/3 | 2.500 | tak |
| K‑25 | ramka_wkladka_v2.stl | (-42, 42, 1.5) | POZA | POZA | 0/3 | 2.500 | tak |
| K‑25 | ramka_wkladka_v2.stl | (42, 42, 1.5) | POZA | POZA | 0/3 | 2.500 | tak |
| K‑25 | ramka_wkladka_v2.stl | (42, -42, 1.5) | W | W | 3/3 | 1.000 | tak |
| K‑25 | ramka_wkladka_v2.stl | (-45, -45, 0.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑25 | ramka_wkladka_v2.stl | (-45, -45, 1.8) | W | W | 3/3 | 0.559 | tak |
| K‑25 | ramka_wkladka_v2.stl | (-50, -50, 0.7) | POZA | POZA | 0/3 | 0.800 | tak |
| K‑25 | ramka_wkladka_v2.stl | (-50, -50, 2.2) | W | W | 3/3 | 0.700 | tak |
| K‑25 | ramka_wkladka_v2.stl | (-51.5, -51.5, 0.7) | POZA | POZA | 0/3 | 0.800 | tak |
| K‑27 | ramka_wkladka_v2.stl | (45.6, -45.6, 5) | W | W | 3/3 | 2.200 | tak |
| K‑27 | ramka_wkladka_v2.stl | (45.6, -45.6, 8) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑27 | ramka_wkladka_v2.stl | (45.6, -45.6, 7.2) | W | W | 3/3 | 0.300 | tak |
| K‑27 | ramka_wkladka_v2.stl | (48.15, -45.6, 5) | POZA | POZA | 0/3 | 0.250 | tak |
| K‑28 | ramka_wkladka_v2.stl | (0, -50.3, 3) | POZA | POZA | 0/3 | 15.000 | tak |
| K‑28 | ramka_wkladka_v2.stl | (0, -50.3, 0.3) | POZA | POZA | 0/3 | 15.000 | tak |
| K‑28 | ramka_wkladka_v2.stl | (20, -50.3, 3) | W | W | 3/3 | 1.900 | tak |
| K‑28 | ramka_wkladka_v2.stl | (-20, -50.3, 3) | W | W | 3/3 | 1.900 | tak |
| K‑29 | ramka_wkladka_v2.stl | (58, 80, 1.5) | W | W | 3/3 | 1.500 | tak |
| K‑29 | ramka_wkladka_v2.stl | (58, 80, 4) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑29 | ramka_wkladka_v2.stl | (-58, 80, 1.5) | W | W | 3/3 | 1.500 | tak |
| K‑29 | ramka_wkladka_v2.stl | (47, 55, 1.5) | W | W | 3/3 | 0.300 | tak |
| K‑29 | ramka_wkladka_v2.stl | (47, 55, 3.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑29 | ramka_wkladka_v2.stl | (62, 55, 1.5) | W | W | 3/3 | 0.300 | tak |
| K‑29 | ramka_wkladka_v2.stl | (62, 50, 1.5) | POZA | POZA | 0/3 | 2.400 | tak |
| K‑29 | ramka_wkladka_v2.stl | (47, 59, 1.5) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑29 | ramka_wkladka_v2.stl | (56, 55, 0.5) | POZA | POZA | 0/3 | 0.700 | tak |
| K‑29 | ramka_wkladka_v2.stl | (56, 55, 2) | W | W | 3/3 | 0.800 | tak |
| K‑29 | ramka_wkladka_v2.stl | (48, 50.5, 0.5) | POZA | POZA | 0/3 | 0.600 | tak |
| K‑29 | ramka_wkladka_v2.stl | (58, 93.5, -2) | W | W | 3/3 | 1.495 | tak |
| K‑29 | ramka_wkladka_v2.stl | (58, 93.5, -3.8) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑29 | ramka_wkladka_v2.stl | (58, 86, 1.5) | POZA | POZA | 0/3 | 2.697 | tak |
| K‑29 | ramka_wkladka_v2.stl | (58, 89, 1.5) | W | W | 3/3 | 0.300 | tak |
| K‑29 | ramka_wkladka_v2.stl | (64, 70, 0.5) | POZA | POZA | 0/3 | 0.700 | tak |
| K‑29 | ramka_wkladka_v2.stl | (64, 70, 2) | W | W | 3/3 | 0.800 | tak |
| K‑29 | ramka_wkladka_v2.stl | (64, 89, 0.5) | POZA | POZA | 0/3 | 0.700 | tak |
| K‑29 | ramka_wkladka_v2.stl | (58, 95.5, 1.5) | W | W | 3/3 | 0.500 | tak |
| K‑29 | ramka_wkladka_v2.stl | (58, 96.5, 1.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑30 | ramka_wkladka_v2.stl | (51.5, 0, 0.7) | POZA | POZA | 0/3 | 0.800 | tak |
| K‑30 | ramka_wkladka_v2.stl | (50.2, 0, 0.7) | POZA | POZA | 0/3 | 0.300 | tak |
| K‑30 | ramka_wkladka_v2.stl | (49.4, 0, 0.7) | W | W | 3/3 | 0.500 | tak |
| K‑30 | ramka_wkladka_v2.stl | (51.5, 0, 2) | W | W | 3/3 | 0.500 | tak |
| K‑30 | ramka_wkladka_v2.stl | (-51.5, 0, 0.7) | POZA | POZA | 0/3 | 0.800 | tak |
| K‑30 | ramka_wkladka_v2.stl | (0, 51.5, 0.7) | POZA | POZA | 0/3 | 0.800 | tak |
| K‑30 | ramka_wkladka_v2.stl | (20, -51.5, 0.7) | W | W | 3/3 | 0.700 | tak |
| K‑45 | ramka_blat_v2.stl | (80.5, 0, -1) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑45 | ramka_blat_v2.stl | (80.5, 0, -3) | W | W | 3/3 | 1.000 | tak |
| K‑45 | ramka_blat_v2.stl | (81.5, 0, -1) | W | W | 3/3 | 0.500 | tak |
| K‑45 | ramka_blat_v2.stl | (0, 0, -3) | POZA | POZA | 0/3 | 79.000 | tak |
| K‑45 | ramka_blat_v2.stl | (78, 0, -3) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑45 | ramka_blat_v2.stl | (80.5, 80.5, -1) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑45 | ramka_blat_v2.stl | (81.5, 81.5, -1) | W | W | 3/3 | 0.707 | tak |
| K‑46 | ramka_blat_v2.stl | (96, 0, -9) | W | W | 3/3 | 0.700 | tak |
| K‑46 | ramka_blat_v2.stl | (94, 0, -9) | POZA | POZA | 0/3 | 1.300 | tak |
| K‑46 | ramka_blat_v2.stl | (97.8, 20, -9) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑46 | ramka_blat_v2.stl | (97.8, 0, -9.75) | W | W | 3/3 | 0.277 | tak |
| K‑46 | ramka_blat_v2.stl | (97.8, 20, -9.75) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑46 | ramka_blat_v2.stl | (97.8, 0, -12.5) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑46 | ramka_blat_v2.stl | (0, -97.8, -9.75) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑46 | ramka_blat_v2.stl | (50, -97.8, -9.75) | W | W | 3/3 | 0.277 | tak |
| K‑46 | ramka_blat_v2.stl | (-50, 97.8, -9.75) | W | W | 3/3 | 0.277 | tak |
| K‑46 | ramka_blat_v2.stl | (50, 97.8, -9.75) | POZA | POZA | 0/3 | 1.001 | tak |
| K‑46 | ramka_blat_v2.stl | (-97.8, 0, -9.75) | W | W | 3/3 | 0.277 | tak |
| K‑46 | ramka_blat_v2.stl | (96, 4.5, -9) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑46 | ramka_blat_v2.stl | (96, 7, -9) | W | W | 3/3 | 0.800 | tak |
| K‑46 | ramka_blat_v2.stl | (96, 4.5, -4.5) | W | W | 3/3 | 0.500 | tak |
| K‑47 | ramka_blat_v2.stl | (75, 93, -8.6) | POZA | POZA | 0/3 | 1.244 | tak |
| K‑47 | ramka_blat_v2.stl | (75, 89.6, -8.6) | W | W | 3/3 | 0.400 | tak |
| K‑47 | ramka_blat_v2.stl | (75, 90.5, -8.6) | W | W | 3/3 | 0.300 | tak |
| K‑47 | ramka_blat_v2.stl | (75, 88, -8.6) | POZA | POZA | 0/3 | 1.200 | tak |
| K‑47 | ramka_blat_v2.stl | (75, 93, -6) | W | W | 3/3 | 1.350 | tak |
| K‑47 | ramka_blat_v2.stl | (75, 93, -12) | W | W | 3/3 | 2.000 | tak |
| K‑47 | ramka_blat_v2.stl | (78, 92, -8.6) | W | W | 3/3 | 1.000 | tak |
| K‑47 | ramka_blat_v2.stl | (70, 96, -9) | W | W | 3/3 | 0.800 | tak |
| K‑47 | ramka_blat_v2.stl | (58, 93.5, -2) | POZA | POZA | 0/3 | 1.695 | tak |
| K‑47 | ramka_blat_v2.stl | (58, 93.5, -4.2) | POZA | POZA | 0/3 | 0.200 | tak |
| K‑47 | ramka_blat_v2.stl | (58, 86, -1) | POZA | POZA | 0/3 | 1.300 | tak |
| K‑47 | ramka_blat_v2.stl | (58, 86, -3) | W | W | 3/3 | 0.700 | tak |
| K‑47 | ramka_blat_v2.stl | (66, 90, -2) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑47 | ramka_blat_v2.stl | (66, 90, -3.95) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑47 | ramka_blat_v2.stl | (66, 90, -4.3) | POZA | POZA | 0/3 | 2.022 | tak |
| K‑47 | ramka_blat_v2.stl | (90, 90, -6) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑47 | ramka_blat_v2.stl | (92.5, 90, -6) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑47 | ramka_blat_v2.stl | (90, 90, -3) | W | W | 3/3 | 1.000 | tak |
| K‑47 | ramka_blat_v2.stl | (84, 0, -7) | POZA | POZA | 0/3 | 3.000 | tak |
| K‑34 | ramka_korpus_W_v2.stl | (0, 0, 1.5) | W | W | 3/3 | 1.500 | tak |
| K‑34 | ramka_korpus_W_v2.stl | (0, 0, 10) | POZA | POZA | 0/3 | 7.000 | tak |
| K‑34 | ramka_korpus_W_v2.stl | (98.75, 0, 20) | W | W | 3/3 | 1.250 | tak |
| K‑34 | ramka_korpus_W_v2.stl | (96, 0, 20) | POZA | POZA | 0/3 | 1.500 | tak |
| K‑34 | ramka_korpus_W_v2.stl | (0, 98.75, 20) | W | W | 3/3 | 1.250 | tak |
| K‑34 | ramka_korpus_W_v2.stl | (99, 99, 20) | POZA | POZA | 0/3 | 0.657 | tak |
| K‑34 | ramka_korpus_W_v2.stl | (0, 0, 59.5) | POZA | POZA | 0/3 | 56.429 | tak |
| K‑34 | ramka_korpus_W_v2.stl | (98.75, 0, 59.4) | W | W | 3/3 | 0.200 | tak |
| K‑34 | ramka_korpus_W_v2.stl | (98.75, 0, 59.7) | POZA | POZA | 0/3 | 0.100 | tak |
| K‑34 | ramka_korpus_W_v2.stl | (99.9, 0, 0.3) | POZA | POZA | 1/3 | 0.963 | tak |
| K‑35 | ramka_korpus_W_v2.stl | (60, 60, 1.5) | POZA | POZA | 0/3 | 1.800 | tak |
| K‑35 | ramka_korpus_W_v2.stl | (55, 55, 1.5) | POZA | POZA | 0/3 | 1.796 | tak |
| K‑35 | ramka_korpus_W_v2.stl | (65, 65, 1.5) | POZA | POZA | 0/3 | 1.796 | tak |
| K‑35 | ramka_korpus_W_v2.stl | (-60, 60, 1.5) | POZA | POZA | 0/3 | 1.800 | tak |
| K‑35 | ramka_korpus_W_v2.stl | (-60, -60, 1.5) | POZA | POZA | 0/3 | 1.800 | tak |
| K‑35 | ramka_korpus_W_v2.stl | (60, -60, 1.5) | POZA | POZA | 0/3 | 1.800 | tak |
| K‑35 | ramka_korpus_W_v2.stl | (52, 52, 1.5) | W | W | 3/3 | 1.500 | tak |
| K‑35 | ramka_korpus_W_v2.stl | (68, 68, 1.5) | W | W | 3/3 | 1.500 | tak |
| K‑35 | ramka_korpus_W_v2.stl | (58, 62, 1.5) | W | W | 3/3 | 1.028 | tak |
| K‑35 | ramka_korpus_W_v2.stl | (63, 60, 0.5) | W | W | 3/3 | 0.321 | tak |
| K‑35 | ramka_korpus_W_v2.stl | (-91, 0, 1.5) | W | W | 3/3 | 1.500 | tak |
| K‑35 | ramka_korpus_W_v2.stl | (-49, 0, 1.5) | W | W | 3/3 | 1.500 | tak |
| K‑35 | ramka_korpus_W_v2.stl | (-8, 10, 1.5) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑35 | ramka_korpus_W_v2.stl | (-8, -10, 1.5) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑35 | ramka_korpus_W_v2.stl | (-8, 13, 1.5) | W | W | 3/3 | 1.000 | tak |
| K‑35 | ramka_korpus_W_v2.stl | (-25, 10, 1.5) | W | W | 3/3 | 1.500 | tak |
| K‑35 | ramka_korpus_W_v2.stl | (-60, 10, 1.5) | W | W | 3/3 | 1.500 | tak |
| K‑36 | ramka_korpus_W_v2.stl | (64, 60, 3.5) | W | W | 3/3 | 0.500 | tak |
| K‑36 | ramka_korpus_W_v2.stl | (64, 60, 4.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑36 | ramka_korpus_W_v2.stl | (-64, 60, 3.5) | W | W | 3/3 | 0.500 | tak |
| K‑36 | ramka_korpus_W_v2.stl | (64, -60, 3.5) | W | W | 3/3 | 0.500 | tak |
| K‑36 | ramka_korpus_W_v2.stl | (-64, -60, 3.5) | W | W | 3/3 | 0.500 | tak |
| K‑36 | ramka_korpus_W_v2.stl | (53, 53, 3.5) | W | W | 3/3 | 0.500 | tak |
| K‑36 | ramka_korpus_W_v2.stl | (69, 69, 3.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑36 | ramka_korpus_W_v2.stl | (60, 60, 3.5) | POZA | POZA | 0/3 | 1.800 | tak |
| K‑36 | ramka_korpus_W_v2.stl | (-43.5, -24.5, 6) | W | W | 3/3 | 1.000 | tak |
| K‑36 | ramka_korpus_W_v2.stl | (-46.5, -24.5, 6) | POZA | POZA | 0/3 | 1.045 | tak |
| K‑36 | ramka_korpus_W_v2.stl | (-46.5, -24.5, 8.5) | POZA | POZA | 0/3 | 1.158 | tak |
| K‑36 | ramka_korpus_W_v2.stl | (14.5, 24.5, 6) | W | W | 3/3 | 1.000 | tak |
| K‑36 | ramka_korpus_W_v2.stl | (11.5, 24.5, 6) | POZA | POZA | 0/3 | 1.045 | tak |
| K‑36 | ramka_korpus_W_v2.stl | (-88.5, -24.5, 6) | POZA | POZA | 0/3 | 3.000 | tak |
| K‑36 | ramka_korpus_W_v2.stl | (23, 75, 6) | POZA | POZA | 0/3 | 3.000 | tak |
| K‑36 | ramka_korpus_W_v2.stl | (-17, 75, 6) | POZA | POZA | 0/3 | 3.000 | tak |
| K‑37 | ramka_korpus_W_v2.stl | (-54, 98.75, 8) | POZA | POZA | 0/3 | 1.500 | tak |
| K‑37 | ramka_korpus_W_v2.stl | (-54, 98.75, 6.2) | W | W | 3/3 | 0.300 | tak |
| K‑37 | ramka_korpus_W_v2.stl | (-54, 98.75, 9.8) | W | W | 3/3 | 0.300 | tak |
| K‑37 | ramka_korpus_W_v2.stl | (-36, 98.75, 8) | W | W | 3/3 | 1.250 | tak |
| K‑37 | ramka_korpus_W_v2.stl | (-63, 98.75, 8) | W | W | 3/3 | 1.250 | tak |
| K‑37 | ramka_korpus_W_v2.stl | (-54, 101, 9.6) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑37 | ramka_korpus_W_v2.stl | (98.75, -36, 8) | POZA | POZA | 0/3 | 1.500 | tak |
| K‑37 | ramka_korpus_W_v2.stl | (-98.75, 36, 8) | POZA | POZA | 0/3 | 1.500 | tak |
| K‑37 | ramka_korpus_W_v2.stl | (98.75, 0, 8) | POZA | POZA | 0/3 | 1.500 | tak |
| K‑37 | ramka_korpus_W_v2.stl | (98.75, -45, 8) | W | W | 3/3 | 1.250 | tak |
| K‑37 | ramka_korpus_W_v2.stl | (101, 0, 9.6) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑37 | ramka_korpus_W_v2.stl | (0, -98.75, 8) | W | W | 3/3 | 1.250 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-60, 90, 26) | POZA | POZA | 0/3 | 10.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-85, 90, 26) | POZA | POZA | 0/3 | 10.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-79, 85, 26) | POZA | POZA | 0/3 | 5.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-60, 99, 15) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-60, 99, 13) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-43, 99, 26) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-40.5, 99, 26) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-90, 99, 26) | POZA | POZA | 0/3 | 3.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-95, 99, 26) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-92.5, 99, 14.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-96, 85, 26) | W | W | 3/3 | 0.500 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-60, 85, 13) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-60, 85, 10) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-60, 85, 39) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-60, 85, 41) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-60, 79, 30) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-60, 77, 30) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-41, 89, 30) | POZA | POZA | 0/3 | 5.999 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-41, 89, 37) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-41, 81.5, 30) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-41, 96.5, 30) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-41, 89, 23) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-39, 89, 30) | POZA | POZA | 0/3 | 6.081 | tak |
| K‑38 | ramka_korpus_W_v2.stl | (-43, 89, 30) | POZA | POZA | 0/3 | 6.081 | tak |
| K‑39 | ramka_korpus_W_v2.stl | (60, 98.75, 24) | POZA | POZA | 0/3 | 4.500 | tak |
| K‑39 | ramka_korpus_W_v2.stl | (60, 98.75, 29.5) | W | W | 3/3 | 1.000 | tak |
| K‑39 | ramka_korpus_W_v2.stl | (60, 98.75, 18.5) | W | W | 3/3 | 1.000 | tak |
| K‑39 | ramka_korpus_W_v2.stl | (67, 98.75, 24) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑39 | ramka_korpus_W_v2.stl | (69, 98.75, 24) | W | W | 3/3 | 0.904 | tak |
| K‑39 | ramka_korpus_W_v2.stl | (51, 98.75, 24) | W | W | 3/3 | 0.904 | tak |
| K‑39 | ramka_korpus_W_v2.stl | (47, 98.75, 24) | POZA | POZA | 0/3 | 1.600 | tak |
| K‑39 | ramka_korpus_W_v2.stl | (73, 98.75, 24) | POZA | POZA | 0/3 | 1.600 | tak |
| K‑39 | ramka_korpus_W_v2.stl | (47, 98.75, 26.5) | W | W | 3/3 | 0.900 | tak |
| K‑39 | ramka_korpus_W_v2.stl | (43, 98.75, 24) | W | W | 3/3 | 1.250 | tak |
| K‑39 | ramka_korpus_W_v2.stl | (75, 98.75, 55) | POZA | POZA | 0/3 | 1.799 | tak |
| K‑39 | ramka_korpus_W_v2.stl | (-75, 98.75, 55) | POZA | POZA | 0/3 | 1.799 | tak |
| K‑39 | ramka_korpus_W_v2.stl | (75, 98.75, 52) | W | W | 3/3 | 0.779 | tak |
| K‑40 | ramka_korpus_W_v2.stl | (30, -98.75, 22) | W | W | 3/3 | 1.250 | tak |
| K‑40 | ramka_korpus_W_v2.stl | (-70, -98.75, 38) | W | W | 3/3 | 1.250 | tak |
| K‑40 | ramka_korpus_W_v2.stl | (-82, -98.75, 38) | W | W | 3/3 | 1.250 | tak |
| K‑40 | ramka_korpus_W_v2.stl | (-58, -98.75, 38) | W | W | 3/3 | 1.250 | tak |
| K‑40 | ramka_korpus_W_v2.stl | (0, -98.75, 20) | W | W | 3/3 | 1.250 | tak |
| K‑40 | ramka_korpus_W_v2.stl | (60, -98.75, 30) | W | W | 3/3 | 1.250 | tak |
| K‑40 | ramka_korpus_W_v2.stl | (-60, -98.75, 30) | W | W | 3/3 | 1.250 | tak |
| K‑42 | ramka_korpus_W_v2.stl | (98, 0, 53.8) | POZA | POZA | 0/3 | 0.800 | tak |
| K‑42 | ramka_korpus_W_v2.stl | (98, 4.5, 53.8) | POZA | POZA | 0/3 | 0.800 | tak |
| K‑42 | ramka_korpus_W_v2.stl | (98, 6, 53.8) | W | W | 3/3 | 0.500 | tak |
| K‑42 | ramka_korpus_W_v2.stl | (98, 0, 51.6) | W | W | 3/3 | 0.500 | tak |
| K‑42 | ramka_korpus_W_v2.stl | (98, 0, 56.1) | W | W | 3/3 | 0.500 | tak |
| K‑42 | ramka_korpus_W_v2.stl | (99.2, 0, 53.8) | W | W | 3/3 | 0.400 | tak |
| K‑42 | ramka_korpus_W_v2.stl | (-98, 0, 53.8) | POZA | POZA | 0/3 | 0.800 | tak |
| K‑42 | ramka_korpus_W_v2.stl | (50, -98, 53.8) | POZA | POZA | 0/3 | 0.800 | tak |
| K‑42 | ramka_korpus_W_v2.stl | (0, -98, 53.8) | W | W | 3/3 | 0.500 | tak |
| K‑42 | ramka_korpus_W_v2.stl | (-50, 98, 53.8) | POZA | POZA | 0/3 | 0.800 | tak |
| K‑42 | ramka_korpus_W_v2.stl | (50, 98, 53.8) | W | W | 3/3 | 0.500 | tak |
| K‑42 | ramka_korpus_W_v2.stl | (98, 0, 48.8) | W | W | 3/3 | 0.500 | tak |
| K‑44 | ramka_korpus_W_v2.stl | (75, 75, 6) | POZA | POZA | 0/3 | 3.000 | tak |
| K‑44 | ramka_korpus_W_v2.stl | (70, 70, 6) | POZA | POZA | 0/3 | 3.000 | tak |
| K‑44 | ramka_korpus_W_v2.stl | (88, 88, 0.2) | W | W | 3/3 | 0.200 | tak |
| K‑44 | ramka_korpus_W_v2.stl | (88, 88, 0.8) | W | W | 3/3 | 0.800 | tak |
| K‑34 | ramka_korpus_P_v2.stl | (0, 0, 1.5) | W | W | 3/3 | 1.500 | tak |
| K‑34 | ramka_korpus_P_v2.stl | (0, 0, 10) | POZA | POZA | 0/3 | 7.000 | tak |
| K‑34 | ramka_korpus_P_v2.stl | (98.75, 0, 20) | W | W | 3/3 | 1.250 | tak |
| K‑34 | ramka_korpus_P_v2.stl | (96, 0, 20) | POZA | POZA | 0/3 | 1.500 | tak |
| K‑34 | ramka_korpus_P_v2.stl | (0, 98.75, 20) | W | W | 3/3 | 1.250 | tak |
| K‑34 | ramka_korpus_P_v2.stl | (99, 99, 20) | POZA | POZA | 0/3 | 0.657 | tak |
| K‑34 | ramka_korpus_P_v2.stl | (0, 0, 59.5) | POZA | POZA | 0/3 | 56.429 | tak |
| K‑34 | ramka_korpus_P_v2.stl | (98.75, 0, 59.4) | W | W | 3/3 | 0.200 | tak |
| K‑34 | ramka_korpus_P_v2.stl | (98.75, 0, 59.7) | POZA | POZA | 0/3 | 0.100 | tak |
| K‑34 | ramka_korpus_P_v2.stl | (99.9, 0, 0.3) | POZA | POZA | 1/3 | 0.963 | tak |
| K‑35 | ramka_korpus_P_v2.stl | (60, 60, 1.5) | POZA | POZA | 0/3 | 1.800 | tak |
| K‑35 | ramka_korpus_P_v2.stl | (55, 55, 1.5) | POZA | POZA | 0/3 | 1.796 | tak |
| K‑35 | ramka_korpus_P_v2.stl | (65, 65, 1.5) | POZA | POZA | 0/3 | 1.796 | tak |
| K‑35 | ramka_korpus_P_v2.stl | (-60, 60, 1.5) | POZA | POZA | 0/3 | 1.800 | tak |
| K‑35 | ramka_korpus_P_v2.stl | (-60, -60, 1.5) | POZA | POZA | 0/3 | 1.800 | tak |
| K‑35 | ramka_korpus_P_v2.stl | (60, -60, 1.5) | POZA | POZA | 0/3 | 1.800 | tak |
| K‑35 | ramka_korpus_P_v2.stl | (52, 52, 1.5) | W | W | 3/3 | 1.500 | tak |
| K‑35 | ramka_korpus_P_v2.stl | (68, 68, 1.5) | W | W | 3/3 | 1.500 | tak |
| K‑35 | ramka_korpus_P_v2.stl | (58, 62, 1.5) | W | W | 3/3 | 1.028 | tak |
| K‑35 | ramka_korpus_P_v2.stl | (63, 60, 0.5) | W | W | 3/3 | 0.321 | tak |
| K‑35 | ramka_korpus_P_v2.stl | (-91, 0, 1.5) | W | W | 3/3 | 1.500 | tak |
| K‑35 | ramka_korpus_P_v2.stl | (-49, 0, 1.5) | W | W | 3/3 | 1.500 | tak |
| K‑35 | ramka_korpus_P_v2.stl | (-8, 10, 1.5) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑35 | ramka_korpus_P_v2.stl | (-8, -10, 1.5) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑35 | ramka_korpus_P_v2.stl | (-8, 13, 1.5) | W | W | 3/3 | 1.000 | tak |
| K‑35 | ramka_korpus_P_v2.stl | (-25, 10, 1.5) | W | W | 3/3 | 1.500 | tak |
| K‑35 | ramka_korpus_P_v2.stl | (-60, 10, 1.5) | W | W | 3/3 | 1.500 | tak |
| K‑36 | ramka_korpus_P_v2.stl | (64, 60, 3.5) | W | W | 3/3 | 0.500 | tak |
| K‑36 | ramka_korpus_P_v2.stl | (64, 60, 4.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑36 | ramka_korpus_P_v2.stl | (-64, 60, 3.5) | W | W | 3/3 | 0.500 | tak |
| K‑36 | ramka_korpus_P_v2.stl | (64, -60, 3.5) | W | W | 3/3 | 0.500 | tak |
| K‑36 | ramka_korpus_P_v2.stl | (-64, -60, 3.5) | W | W | 3/3 | 0.500 | tak |
| K‑36 | ramka_korpus_P_v2.stl | (53, 53, 3.5) | W | W | 3/3 | 0.500 | tak |
| K‑36 | ramka_korpus_P_v2.stl | (69, 69, 3.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑36 | ramka_korpus_P_v2.stl | (60, 60, 3.5) | POZA | POZA | 0/3 | 1.800 | tak |
| K‑36 | ramka_korpus_P_v2.stl | (-43.5, -24.5, 6) | W | W | 3/3 | 1.000 | tak |
| K‑36 | ramka_korpus_P_v2.stl | (-46.5, -24.5, 6) | POZA | POZA | 0/3 | 1.045 | tak |
| K‑36 | ramka_korpus_P_v2.stl | (-46.5, -24.5, 8.5) | POZA | POZA | 0/3 | 1.158 | tak |
| K‑36 | ramka_korpus_P_v2.stl | (14.5, 24.5, 6) | W | W | 3/3 | 1.000 | tak |
| K‑36 | ramka_korpus_P_v2.stl | (11.5, 24.5, 6) | POZA | POZA | 0/3 | 1.045 | tak |
| K‑36 | ramka_korpus_P_v2.stl | (-88.5, -24.5, 6) | POZA | POZA | 0/3 | 3.000 | tak |
| K‑36 | ramka_korpus_P_v2.stl | (23, 75, 6) | POZA | POZA | 0/3 | 3.000 | tak |
| K‑36 | ramka_korpus_P_v2.stl | (-17, 75, 6) | POZA | POZA | 0/3 | 3.000 | tak |
| K‑37 | ramka_korpus_P_v2.stl | (-54, 98.75, 8) | POZA | POZA | 0/3 | 1.500 | tak |
| K‑37 | ramka_korpus_P_v2.stl | (-54, 98.75, 6.2) | W | W | 3/3 | 0.300 | tak |
| K‑37 | ramka_korpus_P_v2.stl | (-54, 98.75, 9.8) | W | W | 3/3 | 0.300 | tak |
| K‑37 | ramka_korpus_P_v2.stl | (-36, 98.75, 8) | W | W | 3/3 | 1.250 | tak |
| K‑37 | ramka_korpus_P_v2.stl | (-63, 98.75, 8) | W | W | 3/3 | 1.250 | tak |
| K‑37 | ramka_korpus_P_v2.stl | (-54, 101, 9.6) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑37 | ramka_korpus_P_v2.stl | (98.75, -36, 8) | POZA | POZA | 0/3 | 1.500 | tak |
| K‑37 | ramka_korpus_P_v2.stl | (-98.75, 36, 8) | POZA | POZA | 0/3 | 1.500 | tak |
| K‑37 | ramka_korpus_P_v2.stl | (98.75, 0, 8) | POZA | POZA | 0/3 | 1.500 | tak |
| K‑37 | ramka_korpus_P_v2.stl | (98.75, -45, 8) | W | W | 3/3 | 1.250 | tak |
| K‑37 | ramka_korpus_P_v2.stl | (101, 0, 9.6) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑37 | ramka_korpus_P_v2.stl | (0, -98.75, 8) | W | W | 3/3 | 1.250 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-60, 90, 26) | POZA | POZA | 0/3 | 10.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-85, 90, 26) | POZA | POZA | 0/3 | 10.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-79, 85, 26) | POZA | POZA | 0/3 | 5.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-60, 99, 15) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-60, 99, 13) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-43, 99, 26) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-40.5, 99, 26) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-90, 99, 26) | POZA | POZA | 0/3 | 3.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-95, 99, 26) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-92.5, 99, 14.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-96, 85, 26) | W | W | 3/3 | 0.500 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-60, 85, 13) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-60, 85, 10) | POZA | POZA | 0/3 | 2.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-60, 85, 39) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-60, 85, 41) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-60, 79, 30) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-60, 77, 30) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-41, 89, 30) | POZA | POZA | 0/3 | 5.999 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-41, 89, 37) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-41, 81.5, 30) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-41, 96.5, 30) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-41, 89, 23) | W | W | 3/3 | 1.000 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-39, 89, 30) | POZA | POZA | 0/3 | 6.081 | tak |
| K‑38 | ramka_korpus_P_v2.stl | (-43, 89, 30) | POZA | POZA | 0/3 | 6.081 | tak |
| K‑39 | ramka_korpus_P_v2.stl | (60, 98.75, 24) | POZA | POZA | 0/3 | 4.500 | tak |
| K‑39 | ramka_korpus_P_v2.stl | (60, 98.75, 29.5) | W | W | 3/3 | 1.000 | tak |
| K‑39 | ramka_korpus_P_v2.stl | (60, 98.75, 18.5) | W | W | 3/3 | 1.000 | tak |
| K‑39 | ramka_korpus_P_v2.stl | (67, 98.75, 24) | POZA | POZA | 0/3 | 1.000 | tak |
| K‑39 | ramka_korpus_P_v2.stl | (69, 98.75, 24) | W | W | 3/3 | 0.904 | tak |
| K‑39 | ramka_korpus_P_v2.stl | (51, 98.75, 24) | W | W | 3/3 | 0.904 | tak |
| K‑39 | ramka_korpus_P_v2.stl | (47, 98.75, 24) | POZA | POZA | 0/3 | 1.600 | tak |
| K‑39 | ramka_korpus_P_v2.stl | (73, 98.75, 24) | POZA | POZA | 0/3 | 1.600 | tak |
| K‑39 | ramka_korpus_P_v2.stl | (47, 98.75, 26.5) | W | W | 3/3 | 0.900 | tak |
| K‑39 | ramka_korpus_P_v2.stl | (43, 98.75, 24) | W | W | 3/3 | 1.250 | tak |
| K‑39 | ramka_korpus_P_v2.stl | (75, 98.75, 55) | POZA | POZA | 0/3 | 1.799 | tak |
| K‑39 | ramka_korpus_P_v2.stl | (-75, 98.75, 55) | POZA | POZA | 0/3 | 1.799 | tak |
| K‑39 | ramka_korpus_P_v2.stl | (75, 98.75, 52) | W | W | 3/3 | 0.779 | tak |
| K‑40 | ramka_korpus_P_v2.stl | (30, -98.75, 22) | W | W | 3/3 | 1.250 | tak |
| K‑40 | ramka_korpus_P_v2.stl | (-70, -98.75, 38) | W | W | 3/3 | 1.250 | tak |
| K‑40 | ramka_korpus_P_v2.stl | (-82, -98.75, 38) | W | W | 3/3 | 1.250 | tak |
| K‑40 | ramka_korpus_P_v2.stl | (-58, -98.75, 38) | W | W | 3/3 | 1.250 | tak |
| K‑40 | ramka_korpus_P_v2.stl | (0, -98.75, 20) | W | W | 3/3 | 1.250 | tak |
| K‑40 | ramka_korpus_P_v2.stl | (60, -98.75, 30) | W | W | 3/3 | 1.250 | tak |
| K‑40 | ramka_korpus_P_v2.stl | (-60, -98.75, 30) | W | W | 3/3 | 1.250 | tak |
| K‑42 | ramka_korpus_P_v2.stl | (98, 0, 53.8) | POZA | POZA | 0/3 | 0.800 | tak |
| K‑42 | ramka_korpus_P_v2.stl | (98, 4.5, 53.8) | POZA | POZA | 0/3 | 0.800 | tak |
| K‑42 | ramka_korpus_P_v2.stl | (98, 6, 53.8) | W | W | 3/3 | 0.500 | tak |
| K‑42 | ramka_korpus_P_v2.stl | (98, 0, 51.6) | W | W | 3/3 | 0.500 | tak |
| K‑42 | ramka_korpus_P_v2.stl | (98, 0, 56.1) | W | W | 3/3 | 0.500 | tak |
| K‑42 | ramka_korpus_P_v2.stl | (99.2, 0, 53.8) | W | W | 3/3 | 0.400 | tak |
| K‑42 | ramka_korpus_P_v2.stl | (-98, 0, 53.8) | POZA | POZA | 0/3 | 0.800 | tak |
| K‑42 | ramka_korpus_P_v2.stl | (50, -98, 53.8) | POZA | POZA | 0/3 | 0.800 | tak |
| K‑42 | ramka_korpus_P_v2.stl | (0, -98, 53.8) | W | W | 3/3 | 0.500 | tak |
| K‑42 | ramka_korpus_P_v2.stl | (-50, 98, 53.8) | POZA | POZA | 0/3 | 0.800 | tak |
| K‑42 | ramka_korpus_P_v2.stl | (50, 98, 53.8) | W | W | 3/3 | 0.500 | tak |
| K‑42 | ramka_korpus_P_v2.stl | (98, 0, 48.8) | W | W | 3/3 | 0.500 | tak |
| K‑44 | ramka_korpus_P_v2.stl | (75, 75, 6) | POZA | POZA | 0/3 | 3.000 | tak |
| K‑44 | ramka_korpus_P_v2.stl | (70, 70, 6) | POZA | POZA | 0/3 | 3.000 | tak |
| K‑44 | ramka_korpus_P_v2.stl | (88, 88, 0.2) | W | W | 3/3 | 0.200 | tak |
| K‑44 | ramka_korpus_P_v2.stl | (88, 88, 0.8) | W | W | 3/3 | 0.800 | tak |
| K‑52b | ramka_tulejka_dc_v2.stl | (0, 0, 1.5) | POZA | POZA | 0/3 | 4.098 | tak |
| K‑52b | ramka_tulejka_dc_v2.stl | (3.5, 0, 1.5) | POZA | POZA | 0/3 | 0.600 | tak |
| K‑52b | ramka_tulejka_dc_v2.stl | (4.8, 0, 1.5) | W | W | 3/3 | 0.700 | tak |
| K‑52b | ramka_tulejka_dc_v2.stl | (5.5, 0, 2) | W | W | 3/3 | 0.425 | tak |
| K‑52b | ramka_tulejka_dc_v2.stl | (6.8, 0, 2) | POZA | POZA | 0/3 | 0.875 | tak |
| K‑52b | ramka_tulejka_dc_v2.stl | (6.8, 0, 0.5) | W | W | 3/3 | 0.500 | tak |
| K‑52b | ramka_tulejka_dc_v2.stl | (8, 0, 0.5) | POZA | POZA | 0/3 | 0.500 | tak |
| K‑52c | ramka_podkladka_panelu_05_v2.stl | (0, 0, 0.25) | POZA | POZA | 0/3 | 1.695 | tak |
| K‑52c | ramka_podkladka_panelu_05_v2.stl | (1.5, 0, 0.25) | POZA | POZA | 0/3 | 0.199 | tak |
| K‑52c | ramka_podkladka_panelu_05_v2.stl | (3, 0, 0.25) | W | W | 3/3 | 0.250 | tak |
| K‑52c | ramka_podkladka_panelu_05_v2.stl | (4.7, 0, 0.25) | POZA | POZA | 0/3 | 0.200 | tak |
| K‑52c | ramka_podkladka_panelu_1_v2.stl | (0, 0, 0.5) | POZA | POZA | 0/3 | 1.695 | tak |
| K‑52c | ramka_podkladka_panelu_1_v2.stl | (1.5, 0, 0.5) | POZA | POZA | 0/3 | 0.199 | tak |
| K‑52c | ramka_podkladka_panelu_1_v2.stl | (3, 0, 0.5) | W | W | 3/3 | 0.500 | tak |
| K‑52c | ramka_podkladka_panelu_1_v2.stl | (4.7, 0, 0.5) | POZA | POZA | 0/3 | 0.200 | tak |
| K‑52c | ramka_podkladka_panelu_2_v2.stl | (0, 0, 1) | POZA | POZA | 0/3 | 1.695 | tak |
| K‑52c | ramka_podkladka_panelu_2_v2.stl | (1.5, 0, 1) | POZA | POZA | 0/3 | 0.199 | tak |
| K‑52c | ramka_podkladka_panelu_2_v2.stl | (3, 0, 1) | W | W | 3/3 | 1.000 | tak |
| K‑52c | ramka_podkladka_panelu_2_v2.stl | (4.7, 0, 1) | POZA | POZA | 0/3 | 0.200 | tak |
