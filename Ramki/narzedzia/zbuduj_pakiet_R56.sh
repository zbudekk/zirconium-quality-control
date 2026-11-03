#!/bin/bash
# Buduje pakiet R56 (R56: dokumenty bez ram czasowych, nowy dokument „Budowa ramki — decyzje i zamienniki”, firmy przy pozycjach, autor Michał Budek; 1.11.2026 wieczór).
# Geometria i STL bez zmian wobec R55/R54. Na wzór zbuduj_pakiet_R55.sh.
# Uruchom z folderu Ramki:  bash narzedzia/zbuduj_pakiet_R56.sh [katalog_docelowy]
# Domyślnie buduje Ramki_pakiet/ (kopia pakietu R54 sprzed przebudowy: archiwum/Ramki_pakiet_przed_dokumenty_R56_2026-11-01/ = pakiet R55).
# Na wzór zbuduj_pakiet_R54.sh; różnice: sufiks dokumentów _R55, folder 03_Druk_wlasny/PETG_FDM (bez Zywica), README z R55, SHA256SUMS_<data>_R55.txt.
# Różnice wobec zbuduj_pakiet_R53.sh: STL płytek po R54 (wyniki_v2/, recenzja R54 iter1 ZALICZONA), dokumenty z 1.11,
# model 3D i animacja z wyniki_model_R54/ (model budowany osobno: node narzedzia/zbuduj_model_offline.js), R54_wdrozenie_zmiany.md,
# raport wykonawcy R54, recenzja R54. Na końcu SHA256SUMS_<data>_R54.txt w katalogu pakietu.
set -e
cd "$(dirname "$0")/.."
D="${1:-Ramki_pakiet}"
DATA=2026-11-01
rm -rf "$D"; mkdir -p "$D/01_Dokumenty" "$D/02_Druk_drukarnia_PA12" "$D/03_Druk_wlasny/PETG_FDM" "$D/04_Model_i_animacje/rendery" "$D/05_Zrodla"
cp "Stanowisko kontroli cyrkonii — plan wdrozenia v2.pdf" "$D/01_Dokumenty/01_Plan_wdrozenia_v2_${DATA}_R56.pdf"
cp "Zakupy i druk — stanowisko kontroli cyrkonii.pdf" "$D/01_Dokumenty/02_Zakupy_i_druk_${DATA}_R56.pdf"
cp "Stanowisko kontroli cyrkonii — plan wdrozenia v2.md" "$D/01_Dokumenty/01_Plan_wdrozenia_v2_${DATA}_R56.md"
cp "Zakupy i druk — stanowisko kontroli cyrkonii.md" "$D/01_Dokumenty/02_Zakupy_i_druk_${DATA}_R56.md"
cp "Budowa ramki — decyzje i zamienniki.pdf" "$D/01_Dokumenty/03_Budowa_ramki_decyzje_i_zamienniki_${DATA}_R56.pdf"
cp "Budowa ramki — decyzje i zamienniki.md" "$D/01_Dokumenty/03_Budowa_ramki_decyzje_i_zamienniki_${DATA}_R56.md"
cp dostawcy_druk_i_pleksi.md "$D/05_Zrodla/dostawcy_druk_i_pleksi.md"
cp narzedzia/buduj_plan_wdrozenia.py "$D/05_Zrodla/buduj_plan_wdrozenia.py"
cp plan_ramki_v2.md "$D/01_Dokumenty/04_Plan_budowy_ramek_v2_${DATA}_R56.md"
cp sesje_2026-10-31/poprawki_pasowan/R53_projekt.md "$D/01_Dokumenty/05_R53_projekt_poprawek_pasowan_2026-10-31.md"
cp sesje_2026-10-31/poprawki_pasowan/weryfikacja_R53.md "$D/01_Dokumenty/06_R53_weryfikacja_2026-10-31.md"
cp R54_wdrozenie_zmiany.md "$D/01_Dokumenty/07_R54_gniazda_w_kole_pola_skanowania_${DATA}.md"
cp recenzja/raport_recenzenta_R54_iter1.md "$D/01_Dokumenty/08_R54_recenzja_plytek_${DATA}.md"
for f in ramka_korpus_W_v2 ramka_korpus_P_v2 ramka_blat_v2 ramka_wkladka_v2 ramka_plytka_wieczorna_n1_v2 ramka_plytka_wieczorna_n2_v2 ramka_plytka_wieczorna_n3_v2 ramka_plytka_poranna_n4_v2 ramka_plytka_poranna_n5_v2 ramka_plytka_poranna_n6_v2; do cp "wyniki_v2/stl/$f.stl" "$D/02_Druk_drukarnia_PA12/"; done
cp wyniki_v2/arkusze/arkusz_zamowienia.csv wyniki_v2/arkusze/arkusz_zamowienia.md "$D/02_Druk_drukarnia_PA12/"
# R55: wkladka — generator zapisuje czasem inny znak zera normalnych (K-59, odstepstwo #7; siatka identyczna). Do zamowienia idzie plik
# zweryfikowany w R53/R54 (SHA f4196fbc…, jak w "Specyfikacji zamowienia"); kopia z pakietu R54 w archiwum.
WK_R54=archiwum/Ramki_pakiet_przed_R55_2026-11-01/02_Druk_drukarnia_PA12/ramka_wkladka_v2.stl
if [ "$(sha256sum "$D/02_Druk_drukarnia_PA12/ramka_wkladka_v2.stl" | cut -c1-64)" != "f4196fbc640450998634f50caa86051f89df2cbb2c218e317f5c2b193e3ef92b" ]; then
  [ -f "$WK_R54" ] || { echo "BLAD: brak $WK_R54"; exit 1; }
  cp "$WK_R54" "$D/02_Druk_drukarnia_PA12/ramka_wkladka_v2.stl"; echo "wkladka: uzyto pliku R54 (f4196fbc…), wyniki_v2 mial inny znak zera normalnych (K-59 #7)"
fi
cp wyniki_v2/stl/ramka_pokrywka_v2.stl "$D/03_Druk_wlasny/PETG_FDM/"
for f in ramka_tulejka_dc_v2 ramka_podkladka_panelu_05_v2 ramka_podkladka_panelu_1_v2 ramka_podkladka_panelu_2_v2; do cp "wyniki_v2/stl/$f.stl" "$D/03_Druk_wlasny/PETG_FDM/"; done
cp wyniki_v2/stl/ramka_plytka_wieczorna_n1_v2.stl "$D/03_Druk_wlasny/PETG_FDM/ramka_plytka_wieczorna_n1_v2_TEST_SKANERA.stl"
if [ -f wyniki_model_R54/ramka_3d_v3_R54.html ]; then cp wyniki_model_R54/ramka_3d_v3_R54.html "$D/04_Model_i_animacje/"; MODEL="model 3D v3 R54 (ramka_3d_v3_R54.html — otworz dwuklikiem, dziala z dysku bez internetu; online: https://claude.ai/artifact/N1W9QKGcXq87t3GPhFp5Sf)"; else MODEL="model 3D v3 R54: BRAK (zbuduj: node narzedzia/zbuduj_model_offline.js wyniki_model_R54/ramka_3d_v3_R54.html)"; fi
cp wyniki_model_R54/animacja_ramki_R53.html "$D/04_Model_i_animacje/animacja_ramki_R53.html"
cp wyniki_model_R54/*.jpg "$D/04_Model_i_animacje/rendery/" 2>/dev/null || true
cp wyniki_v2/render/*.png "$D/04_Model_i_animacje/rendery/" 2>/dev/null || true
cp parametry.json protokol_weryfikacji_v2.md ramka_generator.py "$D/05_Zrodla/"
cp wyniki_v2/ramka_v2.blend "$D/05_Zrodla/"
cp wyniki_v2/README.md "$D/05_Zrodla/README_wyniki_v2.md"
cp wyniki_v2/arkusze/arkusz_wymiarow.md wyniki_v2/arkusze/kody_plytek.md "$D/05_Zrodla/"
cp wyniki_v2/json/uklad_gniazd_wieczorna.json wyniki_v2/json/uklad_gniazd_poranna.json "$D/05_Zrodla/"
cp wyniki_v2/raport/raport_wykonawcy_R54_iter1.md "$D/05_Zrodla/"
cp wyniki_v2/raport/raport_wykonawcy_R55_iter1.md "$D/05_Zrodla/"
cp narzedzia/uklad_kolo_R54.js narzedzia/weryfikuj_uklad_R54.js "$D/05_Zrodla/"
cat > "$D/README.txt" <<TXT
Ramki swietlne i plytki 96x96 — pakiet wynikowy v2 po R56, ${DATA}
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
Zamawiac TYLKO pliki z tego pakietu (SHA-256 w SHA256SUMS_${DATA}_R56.txt i w dokumencie 02_Zakupy_i_druk, sekcja "Specyfikacja zamowienia").

01_Dokumenty            01 plan wdrozenia stanowiska (PDF+MD), 02 zakupy i druk z lista firm (PDF+MD), 03 budowa ramki — decyzje i zamienniki (PDF+MD),
                        04 plan budowy ramek (MD, zrodlo prawdy, rejestr R1–R56), 05–06 projekt i weryfikacja R53 (pasowania), 07 opis zmiany R54, 08 recenzja plytek R54
02_Druk_drukarnia_PA12  STL do zamowienia w drukarni MJF/SLS PA12 + arkusz zamowienia (ilosci, objetosci, materialy)
                        od razu: ramka_korpus_W, ramka_korpus_P, ramka_blat (x2); po potwierdzeniu pola skanowania (#12): ramka_wkladka (x3), plytki n1-n6
03_Druk_wlasny          PETG_FDM (wszystko FDM PETG u kolegi): pokrywka (x4); tulejka DC (x2, tylko przy gniezdzie z gwintem o8, drukowana
                        PO pomiarze otworu, skalowanie XY w slicerze), podkladki panelu 0,5/1/2 (po 8), plytka n1 do testu skanera (PETG bialy matowy)
04_Model_i_animacje     ${MODEL}; animacja_ramki_R53.html (wymiary po R50/R53, bez ukladu gniazd — aktualna); zrzuty modelu R54 i rendery Blendera po R54
05_Zrodla               parametry.json (jedyne zrodlo liczb), uklad_gniazd_*.json (wspolrzedne gniazd i znacznikow), model Blendera ramka_v2.blend,
                        protokol weryfikacji, generator Blendera, README wynikow (SHA-256 plikow), arkusz wymiarow, kody plytek, raporty wykonawcy R54 i R55,
                        skrypty ukladu kolowego (uklad_kolo_R54.js, weryfikuj_uklad_R54.js), dostawcy_druk_i_pleksi.md, buduj_plan_wdrozenia.py
Nie usuwac starszych plikow na Dysku; nowsze wersje maja date w nazwie.
TXT
( cd "$D" && find . -type f ! -name "SHA256SUMS_*" | sort | sed 's|^\./||' | xargs -d '\n' sha256sum > "SHA256SUMS_${DATA}_R56.txt" )
echo "Pakiet gotowy: $D"; find "$D" -type f | wc -l; du -sh "$D"
