Ramki swietlne i plytki 96x96 — pakiet wynikowy v2 po R53 (poprawki pasowan), 2026-10-31
Zastepuje pakiet Ramki_pakiet_2026-10-27_v2 (nie usuwac starego; nowsze wersje maja date w nazwie).

CO ZMIENILO SIE W R53 (31.10.2026):
- Luzy w plikach policzone na tolerancje druku MJF/SLS +-0,3 mm na KAZDEJ z dwoch wspolpracujacych czesci:
  kolnierz blatu 193,6 w 195 (luz 0,7/strone), haczyk zatrzasku 1,5 (czubek 98,3), kieszen zatrzasku 11 x 3,5 x 1,3
  na Z 52,1..55,6 (luz 0,75 pod i nad, do dna 0,5, boczny 1,5), otwor wkretu blatu o3,6, otwor kolka wkladki o3,4
  (pasowanie ruchome 0,2), otwor wkladki 96,8 (luz plytki 0,4/strone), rowek pod slupki panelu 3,6.
- NOWE STL (4): ramka_blat_v2, ramka_korpus_W_v2, ramka_korpus_P_v2, ramka_wkladka_v2. Pozostale 13 plikow STL
  sa bajtowo identyczne z pakietem z 27.10. Zamawiac TYLKO pliki z tego pakietu (SHA-256 w SHA256SUMS i w dokumencie
  02_Zakupy_i_druk, sekcja "Specyfikacja zamowienia").
- Weryfikacja: generator B=0 P=0 D=0, kopie recenzenta A/B/C 0 NIE, trzecie oko 0 blokujacych, pomiar z siatek 118/118.
- Dokumenty: plan wdrozenia v2 i Zakupy i druk zaktualizowane (zmiany oznaczone "[R53]"): przewiercanie o2,1/o2,5 przed
  pierwszym wkreceniem, specyfikacja zamowienia z SHA-256, kryterium odbioru (odchylka > +-0,5 mm = reklamacja),
  tulejka DC 11,85 drukowana po pomiarze otworu w gotowym korpusie, decyzje do wiadomosci wlasciciela.
- Interfejs plytki (96 x 96 x 8, wyciecie, rowek, magnesy), pokrywka, wysokosci 63,6 / 59,6 / 50 — bez zmian.

01_Dokumenty            plan wdrozenia stanowiska (PDF+MD), zakupy i druk (PDF+MD), plan budowy ramek (MD, zrodlo prawdy),
                        projekt R53 (tabela decyzji T1-T16) i weryfikacja R53 (pasowania przed/po z siatek)
02_Druk_drukarnia_PA12  STL do zamowienia w drukarni MJF/SLS PA12 + arkusz zamowienia (ilosci, objetosci, materialy)
                        od razu: ramka_korpus_W, ramka_korpus_P, ramka_blat (x2); po potwierdzeniu pola skanowania: ramka_wkladka (x3), plytki n1-n6
03_Druk_wlasny          PETG_FDM: pokrywka (x4); Zywica: tulejka DC (x2, tylko przy gniezdzie z gwintem o8, drukowana PO pomiarze otworu),
                        podkladki panelu 0,5/1/2 (po 8), plytka n1 do testu skanera
04_Model_i_animacje     model 3D v3 R53 (ramka_3d_v3_R53.html — otworz dwuklikiem, dziala z dysku bez internetu); animacja_ramki_R53.html (wymiary po R50/R53) i starsza animacja_ramki_v2.html (sprzed R50, tylko historycznie); rendery po R53
05_Zrodla               parametry.json (jedyne zrodlo liczb, 13 kluczy R53), model Blendera ramka_v2.blend, protokol weryfikacji,
                        generator Blendera, README wynikow (SHA-256 plikow), arkusz wymiarow, kody plytek, raport SPRAWDZ iter5
Nie usuwac starszych plikow na Dysku; nowsze wersje maja date w nazwie.
