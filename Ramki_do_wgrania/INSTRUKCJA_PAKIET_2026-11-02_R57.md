# Pakiet Ramki R57 — 2 listopada 2026 — jak rozpakować i co jest nowe

Autor: Michał Budek. Ten pakiet ZASTĘPUJE Ramki_pakiet_2026-11-01_R56 (starszych plików na Dysku nie usuwamy; obowiązuje najnowszy numer R).

## Pliki
- Ramki_pakiet_2026-11-02_R57_cz1_dokumenty_druk.zip — 01_Dokumenty (3 PDF + MD: plan wdrożenia, Zakupy i druk, Budowa ramki — decyzje i zamienniki; plan budowy ramek; R53/R54), 02_Druk_drukarnia_PA12 (12 STL, w tym płytki okrągłe n8 i n9, + arkusz zamówienia), 03_Druk_wlasny (PETG FDM), README.txt, SHA256SUMS.
- Ramki_pakiet_2026-11-02_R57_cz2_model.zip — 04_Model_i_animacje (model 3D v3 R54 offline, animacja, rendery; bez płytki okrągłej).
- Ramki_pakiet_2026-11-02_R57_cz3_zrodla.zip — 05_Zrodla (parametry.json, generator, protokół, blend, arkusze, JSON układów gniazd w tym okrągłe, bazowe STL okrągłe, R57_wdrozenie_zmiany.md, raport wykonawcy R57 i recenzja R57).
- SHA256SUMS_2026-11-02_R57.txt — sumy wszystkich 63 plików pakietu (ścieżki względem folderu Ramki_pakiet_2026-11-02_R57/).
- Osobno (do otwarcia bez rozpakowywania, identyczne z cz1): 01_Plan_wdrozenia_v2_2026-11-02_R57.pdf, 02_Zakupy_i_druk_2026-11-02_R57.pdf, 03_Budowa_ramki_decyzje_i_zamienniki_2026-11-02_R57.pdf.

Rozpakować wszystkie trzy ZIP-y do jednego folderu — każdy zawiera ten sam katalog nadrzędny `Ramki_pakiet_2026-11-02_R57/`, więc podfoldery 01–05 złożą się w całość.

## Co nowego w R57
- Płytka okrągła ø100 × 8 — drugi wariant do testu skanera (porównanie kwadrat vs koło na egzemplarzu skanera). Do zamówienia od razu w drukarni, PA12 biały mat, bez wygładzania, ±0,3 mm:
  - `ramka_plytka_okragla_wieczorna_n8_v2.stl` — SHA-256 `c4c8a18d0b83fd2a2903f5d782188a8de4827ee07c55dca9df7bd0d8e4a37d32`, 49,01 cm³, 100 × 100 × 8,6 mm
  - `ramka_plytka_okragla_poranna_n9_v2.stl` — SHA-256 `a87bc6c5f8f0323bc202e5ebfeab6be6d7c8432beba6aafe4a8372d70666e2be`, 50,56 cm³, 100 × 100 × 8,6 mm
- Gniazda, rynienki i stożki znaczników identyczne jak w płytkach kwadratowych; ścięcie orientacyjne na obwodzie (cięciwa 16 mm) — drukarnia nie wygładza; bez kieszeni magnesów — płytka tylko do skanera, wkładka i pokrywka ramki jej nie obsługują (przyszła zmiana R58, jeśli test wskaże koło).
- Dokumenty 01–03 z płytką okrągłą; arkusz zamówienia 17 pozycji (drukarnia z płytkami okrągłymi: 998–1 775 zł najtańszy / 1 307–2 323 zł pokazowy).
- Pliki STL z pakietu R56 bajtowo identyczne (te same sumy SHA-256).

Zamawiać w drukarni wyłącznie pliki z sumami SHA-256 z dokumentu 02 („Specyfikacja zamówienia”).
