# Pakiet Ramki R59 — 2026-11-16 — jak rozpakować i co jest nowe

Ten pakiet ZASTĘPUJE Ramki_pakiet_2026-11-02_R57 (starszych plików na Dysku nie usuwamy; obowiązuje najnowszy numer R).

## Pliki
- Ramki_pakiet_2026-11-16_R59_cz1_dokumenty_druk.zip — 01_Dokumenty (3 PDF + MD: plan wdrożenia, Zakupy i druk, Budowa ramki — decyzje i zamienniki; plan budowy ramek; R53/R54), 02_Druk_drukarnia_PA12 (12 STL, w tym 8 plików płytek w nowym układzie gniazd, + arkusz zamówienia), 03_Druk_wlasny (PETG FDM), README.txt, SHA256SUMS.
- Ramki_pakiet_2026-11-16_R59_cz2_model.zip — 04_Model_i_animacje (model 3D v3 R59 offline i animacja — oba z nowym układem gniazd; zrzuty i rendery; bez płytki okrągłej).
- Ramki_pakiet_2026-11-16_R59_cz3_zrodla.zip — 05_Zrodla (parametry.json, generator, protokół, blend, arkusze, 4 JSON układów gniazd, bazowe STL 4 typów płytek, R59_wdrozenie_zmiany.md, R59_propozycja_ukladu.md, raport wykonawcy R59, recenzja płytek R59, recenzja całości zmian R59, opis programu stanowiska i jego raport R59; starsze raporty R54–R57).
- SHA256SUMS_2026-11-16_R59.txt — sumy wszystkich 81 plików pakietu (ścieżki względem folderu Ramki_pakiet_2026-11-16_R59/).
- Osobno (do otwarcia bez rozpakowywania, identyczne z cz1): 01_Plan_wdrozenia_v2_2026-11-16_R59.pdf, 02_Zakupy_i_druk_2026-11-16_R59.pdf, 03_Budowa_ramki_decyzje_i_zamienniki_2026-11-16_R59.pdf.

Rozpakować wszystkie trzy ZIP-y do jednego folderu — każdy zawiera ten sam katalog nadrzędny `Ramki_pakiet_2026-11-16_R59/`, więc podfoldery 01–05 złożą się w całość.

## Co nowego w R59
- Nowy układ gniazd płytek: większe gniazda w miejscu małych i jedna rynienka zamiast dwóch.
  - Płytka wieczorna: 18 gniazd (6 × ø12, 12 × ø15) i 1 rynienka 60 × 15 mm. Było: 18 gniazd (7 × ø9, 6 × ø12, 5 × ø15) i 2 rynienki.
  - Płytka poranna: 23 gniazda (20 × ø12,5, 3 × ø15) i 1 rynienka 50 × 13 mm. Było: 31 gniazd (18 × ø7,5, 7 × ø10, 6 × ø12,5) i 2 rynienki.
  - Płytki okrągłe nr 8 i 9 mają te same gniazda co kwadratowe tego samego typu.
- Zmieniły się tylko pliki płytek. Do zamówienia w drukarni (PA12 biały mat, bez wygładzania, ±0,3 mm) jest 8 plików z folderu 02_Druk_drukarnia_PA12:
  - `ramka_plytka_wieczorna_n1_v2.stl` — SHA-256 `3b0db5452a0cd9533464772c10b67c05fa7a006fcdb3d140a74af275e79946f7`, 59,66 cm³, 96 × 96 × 8,6 mm
  - `ramka_plytka_wieczorna_n2_v2.stl` — SHA-256 `b87026134b25cf32a84a231b73d5c4eb9fde4dfeb5b16b627cf09ccc3f29c999`, 59,66 cm³, 96 × 96 × 8,6 mm
  - `ramka_plytka_wieczorna_n3_v2.stl` — SHA-256 `59e615d596771c6c0351284c710e94e406a965afef423ffeae5cd18ffa2c4dd3`, 59,66 cm³, 96 × 96 × 8,6 mm
  - `ramka_plytka_poranna_n4_v2.stl` — SHA-256 `20f15f2214f6c9a9baf2b4701e7f99bfbc5f739b6379398294e9f931b8763237`, 59,95 cm³, 96 × 96 × 8,6 mm
  - `ramka_plytka_poranna_n5_v2.stl` — SHA-256 `a275775b9c9b5ddd015b68659f213505bdd28b9476cad5e13405bef2df5b64d1`, 59,95 cm³, 96 × 96 × 8,6 mm
  - `ramka_plytka_poranna_n6_v2.stl` — SHA-256 `c44be370c8b9ad2b70f9e486c3f6f9d2b227b91f2a6544bfe14bf7e66bd65b21`, 59,94 cm³, 96 × 96 × 8,6 mm
  - `ramka_plytka_okragla_wieczorna_n8_v2.stl` — SHA-256 `d5591f652ea1b6b23825abb5ad05ac12b78d17f6abb52946bd1a010ef5e4ff54`, 49,36 cm³, 100 × 100 × 8,6 mm
  - `ramka_plytka_okragla_poranna_n9_v2.stl` — SHA-256 `f9444e6f14e37d9d0bcc8ae84cfec5249146bce20420c53a86a73965727fd4c4`, 49,64 cm³, 100 × 100 × 8,6 mm
- Korpusy, blat, wkładka, pokrywka, tulejka i podkładki to bajtowo te same pliki co w pakiecie R57 (9 plików, te same sumy SHA-256).
- Uwaga na starsze pakiety: w pakietach R54, R55, R56 i R57 pliki płytek mają TE SAME NAZWY, ale poprzedni układ gniazd. Nie mieszać plików z różnych pakietów. Plik rozpoznaje się po sumie SHA-256, nie po nazwie. Jeśli drukarnia dostała wcześniej pliki płytek, trzeba je zastąpić plikami z tego pakietu.
- Stare płytki fizyczne (poprzedni układ) zostają w użyciu. Numer na płytce jest w obu układach ten sam, więc stare płytki trzeba opisać trwałym napisem (np. „R54”) i trzymać osobno od nowych.
- Program stanowiska zna oba układy (nowy pod dotychczasowymi nazwami, poprzedni z dopiskiem `_r54`) i ostrzega, gdy zeskanowana płytka nie pasuje do wybranego układu.
- Numery płytek (1–3 wieczorne, 4–6 poranne, 8 i 9 okrągłe) i ilości bez zmian. Arkusz zamówienia: 17 pozycji; drukarnia z płytkami okrągłymi 996–1771 zł (najtańszy) / 1305–2320 zł (pokazowy), bez okrągłych 907–1613 / 1216–2161 zł.
- Dokumenty 01–03 opisują nowy układ (sekcja „Nowy układ gniazd płytek [R59]”); model 3D i animacja pokazują nowy układ.

Zamawiać w drukarni wyłącznie pliki z sumami SHA-256 z dokumentu 02 („Specyfikacja zamówienia”).
