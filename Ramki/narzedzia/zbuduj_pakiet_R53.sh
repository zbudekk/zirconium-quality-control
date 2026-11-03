#!/bin/bash
# Buduje pakiet R53 (po poprawkach pasowań z 31.10.2026) do wgrania na Google Drive / serwer.
# Uruchom z folderu Ramki:  bash narzedzia/zbuduj_pakiet_R53.sh [katalog_docelowy]
# Domyślnie buduje Ramki_pakiet/ (kopia sprzed przebudowy: archiwum/Ramki_pakiet_przed_dokumenty_R53_2026-10-31/).
# Różnice wobec zbuduj_pakiet.sh: STL z wyniki_v2/ po R53, dokumenty z 31.10, model 3D NIE jest budowany tutaj —
# plik wyniki_model_R53/ramka_3d_v3_R53.html kopiowany jest do 04_, jeśli istnieje (buduje go osobna sesja).
set -e
cd "$(dirname "$0")/.."
D="${1:-Ramki_pakiet}"
DATA=2026-10-31
rm -rf "$D"; mkdir -p "$D/01_Dokumenty" "$D/02_Druk_drukarnia_PA12" "$D/03_Druk_wlasny/PETG_FDM" "$D/03_Druk_wlasny/Zywica" "$D/04_Model_i_animacje/rendery" "$D/05_Zrodla"
cp "Stanowisko kontroli cyrkonii — plan wdrozenia v2.pdf" "$D/01_Dokumenty/01_Plan_wdrozenia_v2_${DATA}_R53.pdf"
cp "Zakupy i druk — stanowisko kontroli cyrkonii.pdf" "$D/01_Dokumenty/02_Zakupy_i_druk_${DATA}_R53.pdf"
cp "Stanowisko kontroli cyrkonii — plan wdrozenia v2.md" "$D/01_Dokumenty/01_Plan_wdrozenia_v2_${DATA}_R53.md"
cp "Zakupy i druk — stanowisko kontroli cyrkonii.md" "$D/01_Dokumenty/02_Zakupy_i_druk_${DATA}_R53.md"
cp plan_ramki_v2.md "$D/01_Dokumenty/03_Plan_budowy_ramek_v2_${DATA}_R53.md"
cp sesje_2026-10-31/poprawki_pasowan/R53_projekt.md "$D/01_Dokumenty/04_R53_projekt_poprawek_pasowan_${DATA}.md"
cp sesje_2026-10-31/poprawki_pasowan/weryfikacja_R53.md "$D/01_Dokumenty/05_R53_weryfikacja_${DATA}.md"
for f in ramka_korpus_W_v2 ramka_korpus_P_v2 ramka_blat_v2 ramka_wkladka_v2 ramka_plytka_wieczorna_n1_v2 ramka_plytka_wieczorna_n2_v2 ramka_plytka_wieczorna_n3_v2 ramka_plytka_poranna_n4_v2 ramka_plytka_poranna_n5_v2 ramka_plytka_poranna_n6_v2; do cp "wyniki_v2/stl/$f.stl" "$D/02_Druk_drukarnia_PA12/"; done
cp wyniki_v2/arkusze/arkusz_zamowienia.csv wyniki_v2/arkusze/arkusz_zamowienia.md "$D/02_Druk_drukarnia_PA12/"
cp wyniki_v2/stl/ramka_pokrywka_v2.stl "$D/03_Druk_wlasny/PETG_FDM/"
for f in ramka_tulejka_dc_v2 ramka_podkladka_panelu_05_v2 ramka_podkladka_panelu_1_v2 ramka_podkladka_panelu_2_v2; do cp "wyniki_v2/stl/$f.stl" "$D/03_Druk_wlasny/Zywica/"; done
cp wyniki_v2/stl/ramka_plytka_wieczorna_n1_v2.stl "$D/03_Druk_wlasny/Zywica/ramka_plytka_wieczorna_n1_v2_TEST_SKANERA.stl"
if [ -f wyniki_model_R53/ramka_3d_v3_R53.html ]; then cp wyniki_model_R53/ramka_3d_v3_R53.html "$D/04_Model_i_animacje/"; MODEL="model 3D v3 R53 (ramka_3d_v3_R53.html — otworz dwuklikiem, dziala z dysku bez internetu)"; else MODEL="model 3D v3 R53: CZEKA NA MODEL (buduje osobna sesja; plik ramka_3d_v3_R53.html zostanie dolozony)"; fi
cp animacja_ramki.html "$D/04_Model_i_animacje/animacja_ramki_v2.html"
if [ -f wyniki_model_R53/animacja_ramki_R53.html ]; then cp wyniki_model_R53/animacja_ramki_R53.html "$D/04_Model_i_animacje/"; ANIM="animacja_ramki_R53.html (wymiary po R50/R53) i starsza animacja_ramki_v2.html (sprzed R50, tylko historycznie)"; else ANIM="starsza animacja_ramki_v2.html (sprzed R50)"; fi
cp wyniki_v2/render/*.png "$D/04_Model_i_animacje/rendery/" 2>/dev/null || true
cp parametry.json protokol_weryfikacji_v2.md ramka_generator.py "$D/05_Zrodla/"
cp wyniki_v2/ramka_v2.blend "$D/05_Zrodla/"
cp wyniki_v2/README.md "$D/05_Zrodla/README_wyniki_v2.md"
cp wyniki_v2/arkusze/arkusz_wymiarow.md wyniki_v2/arkusze/kody_plytek.md "$D/05_Zrodla/"
cp wyniki_v2/raport/raport_wykonawcy_SPRAWDZ_iter5.md "$D/05_Zrodla/raport_wykonawcy_SPRAWDZ_iter5_R53.md"
cat > "$D/README.txt" <<TXT
Ramki swietlne i plytki 96x96 — pakiet wynikowy v2 po R53 (poprawki pasowan), ${DATA}
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
04_Model_i_animacje     ${MODEL}; ${ANIM}; rendery po R53
05_Zrodla               parametry.json (jedyne zrodlo liczb, 13 kluczy R53), model Blendera ramka_v2.blend, protokol weryfikacji,
                        generator Blendera, README wynikow (SHA-256 plikow), arkusz wymiarow, kody plytek, raport SPRAWDZ iter5
Nie usuwac starszych plikow na Dysku; nowsze wersje maja date w nazwie.
TXT
echo "Pakiet gotowy: $D"; find "$D" -type f | wc -l; du -sh "$D"
