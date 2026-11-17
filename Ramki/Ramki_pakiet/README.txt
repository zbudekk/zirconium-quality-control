Ramki swietlne i plytki 96x96 + plytki okragle o100 — pakiet wynikowy v2 po R59, 2026-11-16
Zastepuje pakiet Ramki_pakiet_2026-11-02_R57 (nie usuwac starego; nowsze wersje maja date i numer R w nazwie).

R59 — NOWY UKLAD GNIAZD PLYTEK (zlecenie wlasciciela; wykonawca R59-A; recenzja z siatek R59-B: ZALICZONA):
- Wieksze gniazda w miejscu malych i jedna rynienka zamiast dwoch:
    plytka wieczorna: 18 gniazd (6 x o12, 12 x o15) + 1 rynienka 60 x 15   — bylo 18 gniazd (7 x o9, 6 x o12, 5 x o15) + 2 rynienki
    plytka poranna:   23 gniazda (20 x o12,5, 3 x o15) + 1 rynienka 50 x 13 — bylo 31 gniazd (18 x o7,5, 7 x o10, 6 x o12,5) + 2 rynienki
  Plytki okragle n8 / n9 maja te same gniazda co kwadratowe tego samego typu. Numery plytek (n1-n6, n8, n9) i ilosci bez zmian.
- Zmienily sie TYLKO pliki plytek. Do zamowienia w drukarni (PA12 bialy mat, bez wygladzania, +-0,3 mm) — 8 plikow w 02_Druk_drukarnia_PA12:
    ramka_plytka_wieczorna_n1_v2.stl           SHA-256 3b0db5452a0cd9533464772c10b67c05fa7a006fcdb3d140a74af275e79946f7  59,66 cm3  96 x 96 x 8,6
    ramka_plytka_wieczorna_n2_v2.stl           SHA-256 b87026134b25cf32a84a231b73d5c4eb9fde4dfeb5b16b627cf09ccc3f29c999  59,66 cm3  96 x 96 x 8,6
    ramka_plytka_wieczorna_n3_v2.stl           SHA-256 59e615d596771c6c0351284c710e94e406a965afef423ffeae5cd18ffa2c4dd3  59,66 cm3  96 x 96 x 8,6
    ramka_plytka_poranna_n4_v2.stl             SHA-256 20f15f2214f6c9a9baf2b4701e7f99bfbc5f739b6379398294e9f931b8763237  59,95 cm3  96 x 96 x 8,6
    ramka_plytka_poranna_n5_v2.stl             SHA-256 a275775b9c9b5ddd015b68659f213505bdd28b9476cad5e13405bef2df5b64d1  59,95 cm3  96 x 96 x 8,6
    ramka_plytka_poranna_n6_v2.stl             SHA-256 c44be370c8b9ad2b70f9e486c3f6f9d2b227b91f2a6544bfe14bf7e66bd65b21  59,94 cm3  96 x 96 x 8,6
    ramka_plytka_okragla_wieczorna_n8_v2.stl   SHA-256 d5591f652ea1b6b23825abb5ad05ac12b78d17f6abb52946bd1a010ef5e4ff54  49,36 cm3  100 x 100 x 8,6
    ramka_plytka_okragla_poranna_n9_v2.stl     SHA-256 f9444e6f14e37d9d0bcc8ae84cfec5249146bce20420c53a86a73965727fd4c4  49,64 cm3  100 x 100 x 8,6
- UWAGA — TE SAME NAZWY, INNY UKLAD: w pakietach R54, R55, R56 i R57 pliki plytek nazywaja sie tak samo, ale maja poprzedni uklad gniazd.
  Nie mieszac plikow z roznych pakietow. Plik rozpoznaje sie po sumie SHA-256, nie po nazwie. Jesli drukarnia dostala wczesniej pliki plytek — zastapic.
- Stare plytki fizyczne (poprzedni uklad) zostaja w uzyciu. Numer na plytce jest w obu ukladach ten sam, wiec stare plytki trzeba opisac
  trwalym napisem (np. "R54") i trzymac osobno od nowych.
- Program stanowiska zna oba uklady (nowy pod dotychczasowymi nazwami, poprzedni z dopiskiem _r54) i ostrzega, gdy zeskanowana plytka
  nie pasuje do wybranego ukladu (opis: 05_Zrodla/stanowisko_README.md, liczby: 05_Zrodla/stanowisko_raport_R59_2026-11-14.md).
- Korpus W, korpus P, blat, wkladka, pokrywka, tulejka DC i 3 podkladki: bajtowo bez zmian — te same SHA-256 co w pakiecie R57 (9 plikow).
- Arkusz zamowienia: 17 pozycji (12 do drukarni z n8 / n9; drukarnia razem 996–1771 zl najtanszy / 1305–2320 zl pokazowy;
  bez plytek okraglych 907–1613 / 1216–2161 zl).
- Dokumenty 01–03 opisuja nowy uklad (sekcja "Nowy uklad gniazd plytek [R59]"); plan budowy (04) i protokol maja liczby R59;
  model 3D i animacja pokazuja nowy uklad.

STAN GEOMETRII: gniazda, rynienka i stozki znacznikow plytek w kole o promieniu 47 mm (pole skanowania o100 przy obrocie — zalozenie, pomiar #12
makieta z okregami o90/94/100). Plytka okragla o100 x 8: sciecie orientacyjne na obwodzie — NIE WYGLADZAC; tylko do skanera (bez kieszeni magnesow,
wkladka i pokrywka ramki jej nie obsluguja — przyszla zmiana R58). Ramka bez zmian od R53–R55: obudowa 200x200x63,6, luzy R53.
Druk wlasny wylacznie FDM PETG u kolegi (pokrywka x4, tulejka DC x2, podkladki 3x8, plytka testowa n1, prototypy); z zywicy nic.
02_Druk_drukarnia_PA12/ramka_wkladka_v2.stl = plik zweryfikowany w R53/R54 (SHA f4196fbc...).
Zamawiac TYLKO pliki z tego pakietu (SHA-256 w SHA256SUMS_2026-11-16_R59.txt i w dokumencie 02_Zakupy_i_druk, sekcja "Specyfikacja zamowienia").

01_Dokumenty            01 plan wdrozenia stanowiska (PDF+MD), 02 zakupy i druk z lista firm (PDF+MD), 03 budowa ramki — decyzje i zamienniki (PDF+MD),
                        04 plan budowy ramek (MD, zrodlo prawdy, rejestr R1–R59), 05–06 projekt i weryfikacja R53 (pasowania),
                        07 opis zmiany R54 i 08 recenzja plytek R54 (poprzedni uklad gniazd — dotycza starych plytek fizycznych)
02_Druk_drukarnia_PA12  STL do zamowienia w drukarni MJF/SLS PA12 + arkusz zamowienia (ilosci, objetosci, materialy)
                        od razu: ramka_korpus_W, ramka_korpus_P, ramka_blat (x2);
                        po decyzji wlasciciela (kwadratowe, okragle czy obie): plytki okragle n8 i n9;
                        po potwierdzeniu pola skanowania (#12): ramka_wkladka (x3), plytki n1-n6
03_Druk_wlasny          PETG_FDM (wszystko FDM PETG u kolegi): pokrywka (x4); tulejka DC (x2, tylko przy gniezdzie z gwintem o8, drukowana
                        PO pomiarze otworu, skalowanie XY w slicerze), podkladki panelu 0,5/1/2 (po 8), plytka n1 do testu skanera (PETG bialy matowy).
                        ramka_plytka_wieczorna_n1_v2_TEST_SKANERA.stl = kopia NOWEGO pliku n1 (uklad R59); wersja z poprzednim ukladem (R54) jest w pakiecie R57.
04_Model_i_animacje     model 3D v3 R59 (ramka_3d_v3_R59.html — otworz dwuklikiem, dziala z dysku bez internetu; nowy uklad gniazd; bez plytki okraglej;
                        wersja online podana w pakiecie R57 pokazuje poprzedni uklad); animacja_ramki_R59.html (pokazuje nowy uklad gniazd);
                        rendery: zrzuty modelu i animacji R59 (12 JPG) i rendery Blendera po R59 (3 PNG)
05_Zrodla               parametry.json (jedyne zrodlo liczb), uklad_gniazd_*.json (4 pliki: wspolrzedne gniazd i znacznikow nowego ukladu),
                        model Blendera ramka_v2.blend, protokol weryfikacji, generator Blendera, README wynikow (SHA-256 plikow), arkusz wymiarow, kody plytek,
                        R59: R59_wdrozenie_zmiany.md (co zmieniono, sumy plikow), R59_propozycja_ukladu.md (policzone warianty), raport wykonawcy R59 iter2,
                        raport recenzenta R59 iter1 (plytki sprawdzone z siatek), raport_recenzenta_PR_R59_runda1.md (recenzja calosci zmian),
                        bazowe STL 4 typow plytek (tylko do sprawdzen — NIE do zamowienia), skrypty ukladu (uklad_kolo_R59.js, weryfikuj_uklad_R59.js),
                        arkusz_zamowienia_R59.py (dopisuje n8 / n9 do arkusza generatora), stanowisko_README.md i stanowisko_raport_R59_2026-11-14.md
                        (program stanowiska: dwa uklady plytek i straznik ukladu),
                        starsze (poprzedni uklad i plytka okragla): raporty wykonawcy R54, R55, R57 iter2, recenzja R57 iter1, R57_wdrozenie_zmiany.md;
                        dostawcy_druk_i_pleksi.md, buduj_plan_wdrozenia.py (buduje PDF dokumentow 01–03)
Nie usuwac starszych plikow na Dysku; nowsze wersje maja date w nazwie.
