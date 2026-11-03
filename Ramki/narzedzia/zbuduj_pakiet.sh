#!/bin/bash
# Buduje folder Ramki_pakiet/ (do wgrania na Google Drive) z aktualnych plików projektu. Uruchom z folderu Ramki: bash narzedzia/zbuduj_pakiet.sh
set -e
cd "$(dirname "$0")/.."
D=Ramki_pakiet; rm -rf "$D"; mkdir -p "$D/01_Dokumenty" "$D/02_Druk_drukarnia_PA12" "$D/03_Druk_wlasny/PETG_FDM" "$D/03_Druk_wlasny/Zywica" "$D/04_Model_i_animacje/rendery" "$D/05_Zrodla"
DATA=$(date +%Y-%m-%d)
cp "Stanowisko kontroli cyrkonii — plan wdrozenia v2.pdf" "$D/01_Dokumenty/01_Plan_wdrozenia_v2_${DATA}.pdf"
cp "Zakupy i druk — stanowisko kontroli cyrkonii.pdf" "$D/01_Dokumenty/02_Zakupy_i_druk_${DATA}.pdf"
cp "Stanowisko kontroli cyrkonii — plan wdrozenia v2.md" "$D/01_Dokumenty/01_Plan_wdrozenia_v2_${DATA}.md"
cp "Zakupy i druk — stanowisko kontroli cyrkonii.md" "$D/01_Dokumenty/02_Zakupy_i_druk_${DATA}.md"
cp plan_ramki_v2.md "$D/01_Dokumenty/03_Plan_budowy_ramek_v2_${DATA}.md"
for f in ramka_korpus_W_v2 ramka_korpus_P_v2 ramka_blat_v2 ramka_wkladka_v2 ramka_plytka_wieczorna_n1_v2 ramka_plytka_wieczorna_n2_v2 ramka_plytka_wieczorna_n3_v2 ramka_plytka_poranna_n4_v2 ramka_plytka_poranna_n5_v2 ramka_plytka_poranna_n6_v2; do cp "wyniki_v2/stl/$f.stl" "$D/02_Druk_drukarnia_PA12/"; done
cp wyniki_v2/arkusze/arkusz_zamowienia.csv wyniki_v2/arkusze/arkusz_zamowienia.md "$D/02_Druk_drukarnia_PA12/"
cp wyniki_v2/stl/ramka_pokrywka_v2.stl "$D/03_Druk_wlasny/PETG_FDM/"
for f in ramka_tulejka_dc_v2 ramka_podkladka_panelu_05_v2 ramka_podkladka_panelu_1_v2 ramka_podkladka_panelu_2_v2; do cp "wyniki_v2/stl/$f.stl" "$D/03_Druk_wlasny/Zywica/"; done
cp wyniki_v2/stl/ramka_plytka_wieczorna_n1_v2.stl "$D/03_Druk_wlasny/Zywica/ramka_plytka_wieczorna_n1_v2_TEST_SKANERA.stl"
node narzedzia/zbuduj_model_offline.js "$D/04_Model_i_animacje/ramka_3d_v3.html"
cp animacja_ramki.html "$D/04_Model_i_animacje/animacja_ramki_v2.html"
cp wyniki_v2/render/*.png "$D/04_Model_i_animacje/rendery/" 2>/dev/null || true
cp parametry.json protokol_weryfikacji_v2.md ramka_generator.py "$D/05_Zrodla/"
cp wyniki_v2/ramka_v2.blend "$D/05_Zrodla/"
cp wyniki_v2/README.md "$D/05_Zrodla/README_wyniki_v2.md"
cp wyniki_v2/arkusze/arkusz_wymiarow.md wyniki_v2/arkusze/kody_plytek.md "$D/05_Zrodla/"
cat > "$D/README.txt" <<TXT
Ramki swietlne i plytki 96x96 — pakiet wynikowy v2 (po R50/R52), ${DATA}
01_Dokumenty            plan wdrozenia stanowiska (PDF+MD), zakupy i druk (PDF+MD), plan budowy ramek (MD, zrodlo prawdy)
02_Druk_drukarnia_PA12  STL do zamowienia w drukarni MJF/SLS PA12 + arkusz zamowienia (ilosci, objetosci, materialy)
                        od razu: ramka_korpus_W, ramka_korpus_P, ramka_blat (x2); po potwierdzeniu pola skanowania: ramka_wkladka (x3), plytki n1-n6
03_Druk_wlasny          PETG_FDM: pokrywka (x4); Zywica: tulejka DC (x2, tylko przy gniezdzie z gwintem o8), podkladki panelu 0,5/1/2 (po 8), plytka n1 do testu skanera
04_Model_i_animacje     model 3D v3 (otworz ramka_3d_v3.html dwuklikiem — plik ma w sobie STL i three.js, dziala z dysku bez internetu; wersja online z plikami STL: https://claude.ai/artifact/N1W9QKGcXq87t3GPhFp5Sf), starsza animacja, rendery
05_Zrodla               parametry.json (jedyne zrodlo liczb), model Blendera ramka_v2.blend, protokol weryfikacji, generator Blendera, README wynikow, arkusz wymiarow, kody plytek
Model 3D online ma zakladke "Zmierz": lista pomiarow elektroniki (#1-#17) z miejscem pomiaru na modelu.
Nie usuwac starszych plikow na Dysku; nowsze wersje maja date w nazwie.
TXT
echo "Pakiet gotowy: $D"; find "$D" -type f | wc -l; du -sh "$D"
