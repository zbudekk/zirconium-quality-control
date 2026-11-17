Ramki swietlne i plytki 96x96 + plytki okragle o100 — pakiet wynikowy v2 po R57, 2026-11-02
Zastepuje pakiet Ramki_pakiet_2026-11-01_R56 (nie usuwac starego; nowsze wersje maja date i numer R w nazwie).

R57 (2.11.2026, wlasciciel; wykonawca R57-A, recenzja R57-B ZALICZONA 100/100, zalozenia zatwierdzone przez wlasciciela 2.11):
- NOWE do zamowienia od razu w drukarni (PA12 bialy mat, bez wygladzania, +-0,3 mm) — drugi wariant plytki do testu skanera:
    02_Druk_drukarnia_PA12/ramka_plytka_okragla_wieczorna_n8_v2.stl  SHA-256 c4c8a18d0b83fd2a2903f5d782188a8de4827ee07c55dca9df7bd0d8e4a37d32  49,01 cm3  100 x 100 x 8,6
    02_Druk_drukarnia_PA12/ramka_plytka_okragla_poranna_n9_v2.stl    SHA-256 a87bc6c5f8f0323bc202e5ebfeab6be6d7c8432beba6aafe4a8372d70666e2be  50,56 cm3  100 x 100 x 8,6
  Plytka okragla o100 x 8 (o100 = granica pola skanowania): gniazda, rynienki, otwory o3 i stozki znacznikow IDENTYCZNE jak plytka kwadratowa
  tego typu; sciecie orientacyjne na obwodzie (cieciwa 16 mm, glebokosc 0,644, przod-prawo) — NIE WYGLADZAC; dolki kodu w kole, kod 4-bitowy:
  okragla wieczorna = n8 (dolek D), poranna = n9 (dolki A + D); cyfra 8 / 9 w kole; bez kieszeni magnesow, rowka pokrywki i wyciecia — spod plaski.
  Tylko do skanera: wkladka i pokrywka ramki jej nie obsluguja (uzycie na ramce = przyszla zmiana R58, jesli test wskaze kolo).
- Arkusz zamowienia: 17 pozycji (12 do drukarni z n8 / n9; drukarnia razem 998–1775 zl najtanszy / 1307–2323 zl pokazowy).
- Dokumenty 01–03 z plytka okragla (zakupy: kolejnosc, specyfikacja z SHA, wymagania dla drukarni, checklista odbioru; plan wdrozenia poz. 7a i zal. A;
  budowa ramki: element "Plytka okragla (n8, n9)"); plan budowy (04) i protokol: poprawki tekstu wg recenzji R57-B (D1 K-08, D3 scianki do krawedzi
  w obu bazach: do sciany pionowej W 3,61 / P 3,07, do poczatku fazy W 3,11 / P 2,57) — liczby projektu bez zmian.
- Pliki STL z pakietu R56 (do zamowienia i druku wlasnego) bajtowo bez zmian — te same SHA-256 co w pakiecie R56/R55/R54.

STAN GEOMETRII PLYTEK KWADRATOWYCH I RAMKI (bez zmian od R54/R55): gniazda, rynienki i stozki znacznikow plytek w kole o promieniu 47 mm (pole skanowania o100
przy obrocie — zalozenie, pomiar #12 makieta z okregami o90/94/100); wieczorna 18 gniazd + 2 rynienki, poranna 31 + 2. Obudowa 200x200x63,6, luzy R53.
Druk wlasny wylacznie FDM PETG u kolegi (pokrywka x4, tulejka DC x2, podkladki 3x8, plytka testowa n1, prototypy); z zywicy nic.
02_Druk_drukarnia_PA12/ramka_wkladka_v2.stl = plik zweryfikowany w R53/R54 (SHA f4196fbc...).
Zamawiac TYLKO pliki z tego pakietu (SHA-256 w SHA256SUMS_2026-11-02_R57.txt i w dokumencie 02_Zakupy_i_druk, sekcja "Specyfikacja zamowienia").

01_Dokumenty            01 plan wdrozenia stanowiska (PDF+MD), 02 zakupy i druk z lista firm (PDF+MD), 03 budowa ramki — decyzje i zamienniki (PDF+MD),
                        04 plan budowy ramek (MD, zrodlo prawdy, rejestr R1–R57), 05–06 projekt i weryfikacja R53 (pasowania), 07 opis zmiany R54, 08 recenzja plytek R54
02_Druk_drukarnia_PA12  STL do zamowienia w drukarni MJF/SLS PA12 + arkusz zamowienia (ilosci, objetosci, materialy)
                        od razu: ramka_korpus_W, ramka_korpus_P, ramka_blat (x2), plytki okragle n8 i n9 (R57, test skanera);
                        po potwierdzeniu pola skanowania (#12): ramka_wkladka (x3), plytki n1-n6
03_Druk_wlasny          PETG_FDM (wszystko FDM PETG u kolegi): pokrywka (x4); tulejka DC (x2, tylko przy gniezdzie z gwintem o8, drukowana
                        PO pomiarze otworu, skalowanie XY w slicerze), podkladki panelu 0,5/1/2 (po 8), plytka n1 do testu skanera (PETG bialy matowy)
04_Model_i_animacje     model 3D v3 R54 (ramka_3d_v3_R54.html — otworz dwuklikiem, dziala z dysku bez internetu; online: https://claude.ai/artifact/N1W9QKGcXq87t3GPhFp5Sf; bez plytki okraglej); animacja_ramki_R53.html (wymiary po R50/R53, bez ukladu gniazd — aktualna); zrzuty modelu R54 i rendery Blendera po R54
05_Zrodla               parametry.json (jedyne zrodlo liczb), uklad_gniazd_*.json (wspolrzedne gniazd i znacznikow; R57: uklad_gniazd_okragla_*.json),
                        model Blendera ramka_v2.blend, protokol weryfikacji, generator Blendera, README wynikow (SHA-256 plikow), arkusz wymiarow, kody plytek,
                        raporty wykonawcy R54, R55, R57 iter2 i recenzenta R57 iter1, R57_wdrozenie_zmiany.md, bazowe STL plytek okraglych (tylko do sprawdzen),
                        skrypty ukladu kolowego (uklad_kolo_R54.js, weryfikuj_uklad_R54.js), dostawcy_druk_i_pleksi.md, buduj_plan_wdrozenia.py,
                        arkusz_zamowienia_R57.py (dopisuje n8 / n9 do arkusza generatora)
Nie usuwac starszych plikow na Dysku; nowsze wersje maja date w nazwie.
