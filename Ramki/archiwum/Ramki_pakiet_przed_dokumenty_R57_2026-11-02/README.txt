Ramki swietlne i plytki 96x96 — pakiet wynikowy v2 po R56, 2026-11-01
Zastepuje pakiet Ramki_pakiet_2026-11-01_R55 (nie usuwac starego; nowsze wersje maja date i numer R w nazwie).

R56 (1.11.2026 wieczor, decyzja wlasciciela) — TYLKO DOKUMENTY, pliki STL i arkusze bez zmian (te same sumy SHA-256 co w pakiecie R55/R54):
- Plan wdrozenia v2: bez ram czasowych (daty, tygodnie, dni) — zostaja kolejnosc, warunki i bramki; bez sekcji "Co sie zmienilo wzgledem v1";
  przy pozycjach do zamowienia nazwy firm; strona tytulowa: Wersja = data i godzina budowy, Autor: Michal Budek (tez w stopce kazdej strony).
- Zakupy i druk: zwiezlej, bez dat, bez zapisow "Nie kupujemy..."; nowa sekcja "Gdzie zamawiac" (drukarnie PA12 i pleksi na wymiar, z linkami);
  kazda pozycja ma "po co" i nazwe pliku STL tam, gdzie to czesc drukowana; specyfikacja zamowienia z sumami SHA-256 bez zmian.
- NOWY dokument 03 "Budowa ramki — decyzje i zamienniki": dla kazdego elementu jak jest, dlaczego, czy mozna zmienic i co to wymusza;
  tabela wszystkiego, z czego zrezygnowano (przycisk, czujnik gestu, wkladki gwintowane, podstawka klawiatury, rama dyfuzora, uchwyty kabli,
  pianki, uszczelki, zywica, ...) z powodami; jak przeprowadzic zmiane (parametry.json -> generator -> protokol -> nowe SHA).
- Zrodla: 05_Zrodla/dostawcy_druk_i_pleksi.md (lista firm), buduj_plan_wdrozenia.py (skrypt budowy PDF).

STAN GEOMETRII (bez zmian od R54/R55): gniazda, rynienki i stozki znacznikow plytek w kole o promieniu 47 mm (pole skanowania o100 przy obrocie —
zalozenie, pomiar #12 makieta z okregami o90/94/100); wieczorna 18 gniazd + 2 rynienki, poranna 31 + 2. Obudowa 200x200x63,6, luzy R53.
Druk wlasny wylacznie FDM PETG u kolegi (pokrywka x4, tulejka DC x2, podkladki 3x8, plytka testowa n1, prototypy); z zywicy nic.
02_Druk_drukarnia_PA12/ramka_wkladka_v2.stl = plik zweryfikowany w R53/R54 (SHA f4196fbc...).
Zamawiac TYLKO pliki z tego pakietu (SHA-256 w SHA256SUMS_2026-11-01_R56.txt i w dokumencie 02_Zakupy_i_druk, sekcja "Specyfikacja zamowienia").

01_Dokumenty            01 plan wdrozenia stanowiska (PDF+MD), 02 zakupy i druk z lista firm (PDF+MD), 03 budowa ramki — decyzje i zamienniki (PDF+MD),
                        04 plan budowy ramek (MD, zrodlo prawdy, rejestr R1–R56), 05–06 projekt i weryfikacja R53 (pasowania), 07 opis zmiany R54, 08 recenzja plytek R54
02_Druk_drukarnia_PA12  STL do zamowienia w drukarni MJF/SLS PA12 + arkusz zamowienia (ilosci, objetosci, materialy)
                        od razu: ramka_korpus_W, ramka_korpus_P, ramka_blat (x2); po potwierdzeniu pola skanowania (#12): ramka_wkladka (x3), plytki n1-n6
03_Druk_wlasny          PETG_FDM (wszystko FDM PETG u kolegi): pokrywka (x4); tulejka DC (x2, tylko przy gniezdzie z gwintem o8, drukowana
                        PO pomiarze otworu, skalowanie XY w slicerze), podkladki panelu 0,5/1/2 (po 8), plytka n1 do testu skanera (PETG bialy matowy)
04_Model_i_animacje     model 3D v3 R54 (ramka_3d_v3_R54.html — otworz dwuklikiem, dziala z dysku bez internetu; online: https://claude.ai/artifact/N1W9QKGcXq87t3GPhFp5Sf); animacja_ramki_R53.html (wymiary po R50/R53, bez ukladu gniazd — aktualna); zrzuty modelu R54 i rendery Blendera po R54
05_Zrodla               parametry.json (jedyne zrodlo liczb), uklad_gniazd_*.json (wspolrzedne gniazd i znacznikow), model Blendera ramka_v2.blend,
                        protokol weryfikacji, generator Blendera, README wynikow (SHA-256 plikow), arkusz wymiarow, kody plytek, raporty wykonawcy R54 i R55,
                        skrypty ukladu kolowego (uklad_kolo_R54.js, weryfikuj_uklad_R54.js), dostawcy_druk_i_pleksi.md, buduj_plan_wdrozenia.py
Nie usuwac starszych plikow na Dysku; nowsze wersje maja date w nazwie.
