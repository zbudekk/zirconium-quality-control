Ramki swietlne i plytki 96x96 — pakiet wynikowy v2 po R54 i R55, 2026-11-01
Zastepuje pakiet Ramki_pakiet_2026-11-01_R54 (nie usuwac starego; nowsze wersje maja date i numer R w nazwie).

CO ZMIENILO SIE W R55 (1.11.2026, decyzja wlasciciela, po pakiecie R54):
- Z zywicy nie drukujemy niczego. Druk wlasny = wylacznie FDM z PETG u kolegi: pokrywka x4, tulejka DC x2, podkladki panelu 3x8,
  plytka testowa n1 do testu skanera (PETG bialy matowy), prototypy pasowan. Plytki n1-n6 do pracy: tylko PA12 z drukarni (bez alternatywy zywicznej).
- Tulejka o11,85 na FDM: po wydruku sprawdzic w otworze o12 korpusu; przy luzie/zacisku skalowac XY w slicerze +-1 %, bez zmiany pliku.
  Podkladka 0,5 mm = 3-5 warstw 0,1-0,2 mm.
- Pliki STL BEZ ZMIAN wzgledem pakietu R54 (te same sumy SHA-256; 02_Druk_drukarnia_PA12/ramka_wkladka_v2.stl = plik zweryfikowany w R53/R54,
  SHA f4196fbc… — generator z 1.11 17:14 zapisal te sama siatke z innym znakiem zera normalnych, SHA b237ae56… w 05_Zrodla/README_wyniki_v2.md; K-59 #7).
  Zamowienie w drukarni bez zmian.
- Folder 03_Druk_wlasny ma teraz tylko PETG_FDM (dawny Zywica scalony). Dokumenty: plan wdrozenia v2 i Zakupy i druk bez ustawien druku
  zywicy (zmiany oznaczone "[R55]"); parametry.json materials: tulejka i podkladki "PETG FDM (wlasny)", plytki wieczorne "PA12 drukarnia".

CO ZMIENILO SIE W R54 (1.11.2026, decyzja wlasciciela):
- Skaner obraca plytke wokol osi, wiec w calym obrocie widzi KOLO o srednicy ok. 100 mm (zalozenie, pomiar #12 makieta
  z okregami o90/94/100), nie kwadrat 100x100. Dawny uklad gniazd siegal 54,9 / 52,6 mm od srodka, stozki znacznikow w rogach 61,9.
- Gniazda, rynienki i stozki znacznikow przeliczone do kola o promieniu 47 mm (= 100/2 - 1,5 ulozenie - 1,5 wysieg korony):
  wieczorna 18 gniazd (7 x o9, 6 x o12, 5 x o15) + 2 rynienki 60x15 (bylo 24 + 2); poranna 31 (18 x o7,5, 7 x o10, 6 x o12,5)
  + 2 rynienki 50x13 (bylo 35 + 2). Rynienki w rzedzie przednim i tylnym. Stozki znacznikow osobno dla typu plytki
  (wieczorna A(-35,5;-26,5) B(-35,5;26,5) C(35,5;26,5); poranna A(-34,5;-28) B(-30;32,5) C(30;32,5)); kieszenie magnesow w rogach bez zmian.
- NOWE STL (6 do druku + 2 bazowe): ramka_plytka_wieczorna_n1..n3, ramka_plytka_poranna_n4..n6 (objetosc 59,3 / 60,9 cm3).
  Korpus W/P, blat, wkladka, pokrywka, tulejka, podkladki: bajtowo identyczne z pakietem R53 (31.10). Obrys plytki 96x96x8,
  wyciecie, rowek pokrywki, magnesy, wkladka, pokrywka — BEZ ZMIAN, wiec zamowienie korpusow i blatow od R54 nie zalezy.
- Weryfikacja plytek: generator B=0 P=0 D=0, niezalezna recenzja R54 iter1 ZALICZONA (0 NIE; max promien 46,39 / 46,93 <= 47,
  min scianka 3,00, znaczniki 44,30 / 44,43 <= 44,5). Zamawiac TYLKO pliki z tego pakietu (SHA-256 w SHA256SUMS_2026-11-01_R54.txt
  i w dokumencie 02_Zakupy_i_druk, sekcja "Specyfikacja zamowienia").
- Dokumenty: plan wdrozenia v2 i Zakupy i druk zaktualizowane (zmiany oznaczone "[R54]"): 18/31 koron, zalozenie 11 (kolo przy obrocie),
  opis plytki, test skanera kryterium 8 (makieta z okregami), koszty drukarni z arkusza 909-1616 / 1217-2164 zl (1010 cm3).
- Model 3D v3 R54: plytki z nowym ukladem, parametry R54, grupa wymiarow "Plytka: kolo gniazd i znaczniki", pomiar #12 -> scan_field_d.

01_Dokumenty            plan wdrozenia stanowiska (PDF+MD), zakupy i druk (PDF+MD), plan budowy ramek (MD, zrodlo prawdy),
                        projekt i weryfikacja R53 (pasowania), opis zmiany R54 (lista edycji), recenzja plytek R54
02_Druk_drukarnia_PA12  STL do zamowienia w drukarni MJF/SLS PA12 + arkusz zamowienia (ilosci, objetosci, materialy)
                        od razu: ramka_korpus_W, ramka_korpus_P, ramka_blat (x2); po potwierdzeniu pola skanowania (#12): ramka_wkladka (x3), plytki n1-n6 (NOWE R54)
03_Druk_wlasny          PETG_FDM (R55, wszystko FDM PETG u kolegi, bez zywicy): pokrywka (x4); tulejka DC (x2, tylko przy gniezdzie z gwintem o8, drukowana
                        PO pomiarze otworu, skalowanie XY w slicerze), podkladki panelu 0,5/1/2 (po 8), plytka n1 do testu skanera (PETG bialy matowy; plik R54)
04_Model_i_animacje     model 3D v3 R54 (ramka_3d_v3_R54.html — otworz dwuklikiem, dziala z dysku bez internetu; online: https://claude.ai/artifact/N1W9QKGcXq87t3GPhFp5Sf); animacja_ramki_R53.html (wymiary po R50/R53, bez ukladu gniazd — aktualna); zrzuty modelu R54 i rendery Blendera po R54
05_Zrodla               parametry.json (jedyne zrodlo liczb; R54: 6 nowych kluczy, ev_rows/mo_rows; R55: materials), uklad_gniazd_*.json (wspolrzedne gniazd i znacznikow),
                        model Blendera ramka_v2.blend, protokol weryfikacji, generator Blendera, README wynikow (SHA-256 plikow),
                        arkusz wymiarow, kody plytek, raporty wykonawcy R54 i R55, skrypty ukladu kolowego (uklad_kolo_R54.js, weryfikuj_uklad_R54.js)
Nie usuwac starszych plikow na Dysku; nowsze wersje maja date w nazwie.
