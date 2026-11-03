#!/bin/bash
# Buduje pakiet R57 (R57‑C, 2.11.2026): pakiet R56 + płytki okrągłe n8 (wieczorna) i n9 (poranna) — drugi wariant do testu skanera.
# Na wzór zbuduj_pakiet_R56.sh; różnice: dokumenty 01–04 z sufiksem _2026-11-02_R57 (płytka okrągła w Zakupach, planie wdrożenia, Budowie ramki,
# poprawki D1/D3 w planie i protokole), 02_Druk_drukarnia_PA12 + ramka_plytka_okragla_wieczorna_n8_v2.stl / …_poranna_n9_v2.stl,
# arkusz zamówienia = arkusz generatora (15 pozycji, K‑57) + 2 wiersze okrągłych (narzedzia/arkusz_zamowienia_R57.py; wyniki_v2/ bez zmian),
# 05_Zrodla + bazowe STL okrągłe, uklad_gniazd_okragla_*.json, R57_wdrozenie_zmiany.md, raport wykonawcy R57 iter2, raport recenzenta R57 iter1,
# README z R57, SHA256SUMS_<data>_R57.txt. Na końcu kontrola: pliki STL z SHA256SUMS_2026-11-01_R56.txt bajtowo identyczne w nowym pakiecie.
# Uruchom z folderu Ramki:  bash narzedzia/zbuduj_pakiet_R57.sh [katalog_docelowy]
# Kopia pakietu R56 sprzed przebudowy: archiwum/Ramki_pakiet_przed_dokumenty_R57_2026-11-02/.
set -e
cd "$(dirname "$0")/.."
D="${1:-Ramki_pakiet}"
DATA=2026-11-02
R=R57
SUMY_R56=archiwum/Ramki_pakiet_przed_dokumenty_R57_2026-11-02/SHA256SUMS_2026-11-01_R56.txt
[ -f "$SUMY_R56" ] || { echo "BLAD: brak $SUMY_R56 (kopia pakietu R56)"; exit 1; }
if command -v py >/dev/null; then PY="py -3 -X utf8"; else PY="python3 -X utf8"; fi
rm -rf "$D"; mkdir -p "$D/01_Dokumenty" "$D/02_Druk_drukarnia_PA12" "$D/03_Druk_wlasny/PETG_FDM" "$D/04_Model_i_animacje/rendery" "$D/05_Zrodla"
cp "Stanowisko kontroli cyrkonii — plan wdrozenia v2.pdf" "$D/01_Dokumenty/01_Plan_wdrozenia_v2_${DATA}_${R}.pdf"
cp "Zakupy i druk — stanowisko kontroli cyrkonii.pdf" "$D/01_Dokumenty/02_Zakupy_i_druk_${DATA}_${R}.pdf"
cp "Stanowisko kontroli cyrkonii — plan wdrozenia v2.md" "$D/01_Dokumenty/01_Plan_wdrozenia_v2_${DATA}_${R}.md"
cp "Zakupy i druk — stanowisko kontroli cyrkonii.md" "$D/01_Dokumenty/02_Zakupy_i_druk_${DATA}_${R}.md"
cp "Budowa ramki — decyzje i zamienniki.pdf" "$D/01_Dokumenty/03_Budowa_ramki_decyzje_i_zamienniki_${DATA}_${R}.pdf"
cp "Budowa ramki — decyzje i zamienniki.md" "$D/01_Dokumenty/03_Budowa_ramki_decyzje_i_zamienniki_${DATA}_${R}.md"
cp dostawcy_druk_i_pleksi.md "$D/05_Zrodla/dostawcy_druk_i_pleksi.md"
cp narzedzia/buduj_plan_wdrozenia.py "$D/05_Zrodla/buduj_plan_wdrozenia.py"
cp plan_ramki_v2.md "$D/01_Dokumenty/04_Plan_budowy_ramek_v2_${DATA}_${R}.md"
cp sesje_2026-10-31/poprawki_pasowan/R53_projekt.md "$D/01_Dokumenty/05_R53_projekt_poprawek_pasowan_2026-10-31.md"
cp sesje_2026-10-31/poprawki_pasowan/weryfikacja_R53.md "$D/01_Dokumenty/06_R53_weryfikacja_2026-10-31.md"
cp R54_wdrozenie_zmiany.md "$D/01_Dokumenty/07_R54_gniazda_w_kole_pola_skanowania_2026-11-01.md"
cp recenzja/raport_recenzenta_R54_iter1.md "$D/01_Dokumenty/08_R54_recenzja_plytek_2026-11-01.md"
for f in ramka_korpus_W_v2 ramka_korpus_P_v2 ramka_blat_v2 ramka_wkladka_v2 ramka_plytka_wieczorna_n1_v2 ramka_plytka_wieczorna_n2_v2 ramka_plytka_wieczorna_n3_v2 ramka_plytka_poranna_n4_v2 ramka_plytka_poranna_n5_v2 ramka_plytka_poranna_n6_v2 ramka_plytka_okragla_wieczorna_n8_v2 ramka_plytka_okragla_poranna_n9_v2; do cp "wyniki_v2/stl/$f.stl" "$D/02_Druk_drukarnia_PA12/"; done
# R57: arkusz generatora (15 pozycji) + 2 płytki okrągłe — tylko w pakiecie, wyniki_v2/arkusze bez zmian
$PY narzedzia/arkusz_zamowienia_R57.py "$D/02_Druk_drukarnia_PA12"
# R55: wkladka — generator zapisuje czasem inny znak zera normalnych (K-59, odstepstwo #7; siatka identyczna). Do zamowienia idzie plik
# zweryfikowany w R53/R54 (SHA f4196fbc…, jak w "Specyfikacji zamowienia"); kopia z pakietu R54 w archiwum.
WK_R54=archiwum/Ramki_pakiet_przed_R55_2026-11-01/02_Druk_drukarnia_PA12/ramka_wkladka_v2.stl
if [ "$(sha256sum "$D/02_Druk_drukarnia_PA12/ramka_wkladka_v2.stl" | cut -c1-64)" != "f4196fbc640450998634f50caa86051f89df2cbb2c218e317f5c2b193e3ef92b" ]; then
  [ -f "$WK_R54" ] || { echo "BLAD: brak $WK_R54"; exit 1; }
  cp "$WK_R54" "$D/02_Druk_drukarnia_PA12/ramka_wkladka_v2.stl"; echo "wkladka: uzyto pliku R54 (f4196fbc…), wyniki_v2 mial inny znak zera normalnych (K-59 #7)"
fi
# R57: pliki do zamowienia n8 / n9 musza miec SHA z raportu wykonawcy R57 iter2 §7.1 (= recenzja R57-B, zatwierdzone 2.11)
for p in "ramka_plytka_okragla_wieczorna_n8_v2.stl c4c8a18d0b83fd2a2903f5d782188a8de4827ee07c55dca9df7bd0d8e4a37d32" "ramka_plytka_okragla_poranna_n9_v2.stl a87bc6c5f8f0323bc202e5ebfeab6be6d7c8432beba6aafe4a8372d70666e2be"; do
  set -- $p; [ "$(sha256sum "$D/02_Druk_drukarnia_PA12/$1" | cut -c1-64)" = "$2" ] || { echo "BLAD: $1 ma inne SHA niz zatwierdzone ($2)"; exit 1; }
done
cp wyniki_v2/stl/ramka_pokrywka_v2.stl "$D/03_Druk_wlasny/PETG_FDM/"
for f in ramka_tulejka_dc_v2 ramka_podkladka_panelu_05_v2 ramka_podkladka_panelu_1_v2 ramka_podkladka_panelu_2_v2; do cp "wyniki_v2/stl/$f.stl" "$D/03_Druk_wlasny/PETG_FDM/"; done
cp wyniki_v2/stl/ramka_plytka_wieczorna_n1_v2.stl "$D/03_Druk_wlasny/PETG_FDM/ramka_plytka_wieczorna_n1_v2_TEST_SKANERA.stl"
if [ -f wyniki_model_R54/ramka_3d_v3_R54.html ]; then cp wyniki_model_R54/ramka_3d_v3_R54.html "$D/04_Model_i_animacje/"; MODEL="model 3D v3 R54 (ramka_3d_v3_R54.html — otworz dwuklikiem, dziala z dysku bez internetu; online: https://claude.ai/artifact/N1W9QKGcXq87t3GPhFp5Sf; bez plytki okraglej)"; else MODEL="model 3D v3 R54: BRAK (zbuduj: node narzedzia/zbuduj_model_offline.js wyniki_model_R54/ramka_3d_v3_R54.html)"; fi
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
# R57: zrodla plytki okraglej
cp wyniki_v2/stl/ramka_plytka_okragla_wieczorna_v2.stl wyniki_v2/stl/ramka_plytka_okragla_poranna_v2.stl "$D/05_Zrodla/"
cp wyniki_v2/json/uklad_gniazd_okragla_wieczorna.json wyniki_v2/json/uklad_gniazd_okragla_poranna.json "$D/05_Zrodla/"
cp R57_wdrozenie_zmiany.md wyniki_v2/raport/raport_wykonawcy_R57_iter2.md recenzja/raport_recenzenta_R57_iter1.md narzedzia/arkusz_zamowienia_R57.py "$D/05_Zrodla/"
cat > "$D/README.txt" <<TXT
Ramki swietlne i plytki 96x96 + plytki okragle o100 — pakiet wynikowy v2 po R57, ${DATA}
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
Zamawiac TYLKO pliki z tego pakietu (SHA-256 w SHA256SUMS_${DATA}_${R}.txt i w dokumencie 02_Zakupy_i_druk, sekcja "Specyfikacja zamowienia").

01_Dokumenty            01 plan wdrozenia stanowiska (PDF+MD), 02 zakupy i druk z lista firm (PDF+MD), 03 budowa ramki — decyzje i zamienniki (PDF+MD),
                        04 plan budowy ramek (MD, zrodlo prawdy, rejestr R1–R57), 05–06 projekt i weryfikacja R53 (pasowania), 07 opis zmiany R54, 08 recenzja plytek R54
02_Druk_drukarnia_PA12  STL do zamowienia w drukarni MJF/SLS PA12 + arkusz zamowienia (ilosci, objetosci, materialy)
                        od razu: ramka_korpus_W, ramka_korpus_P, ramka_blat (x2), plytki okragle n8 i n9 (R57, test skanera);
                        po potwierdzeniu pola skanowania (#12): ramka_wkladka (x3), plytki n1-n6
03_Druk_wlasny          PETG_FDM (wszystko FDM PETG u kolegi): pokrywka (x4); tulejka DC (x2, tylko przy gniezdzie z gwintem o8, drukowana
                        PO pomiarze otworu, skalowanie XY w slicerze), podkladki panelu 0,5/1/2 (po 8), plytka n1 do testu skanera (PETG bialy matowy)
04_Model_i_animacje     ${MODEL}; animacja_ramki_R53.html (wymiary po R50/R53, bez ukladu gniazd — aktualna); zrzuty modelu R54 i rendery Blendera po R54
05_Zrodla               parametry.json (jedyne zrodlo liczb), uklad_gniazd_*.json (wspolrzedne gniazd i znacznikow; R57: uklad_gniazd_okragla_*.json),
                        model Blendera ramka_v2.blend, protokol weryfikacji, generator Blendera, README wynikow (SHA-256 plikow), arkusz wymiarow, kody plytek,
                        raporty wykonawcy R54, R55, R57 iter2 i recenzenta R57 iter1, R57_wdrozenie_zmiany.md, bazowe STL plytek okraglych (tylko do sprawdzen),
                        skrypty ukladu kolowego (uklad_kolo_R54.js, weryfikuj_uklad_R54.js), dostawcy_druk_i_pleksi.md, buduj_plan_wdrozenia.py,
                        arkusz_zamowienia_R57.py (dopisuje n8 / n9 do arkusza generatora)
Nie usuwac starszych plikow na Dysku; nowsze wersje maja date w nazwie.
TXT
( cd "$D" && find . -type f ! -name "SHA256SUMS_*" | sort | sed 's|^\./||' | xargs -d '\n' sha256sum > "SHA256SUMS_${DATA}_${R}.txt" )
# Kontrola R57: kazdy STL z sum R56 ma w nowym pakiecie te sama sciezke i SHA
ZLE=0; N=0
while read -r h f; do
  f="${f#\*}"
  case "$f" in *.stl)
    N=$((N+1)); h2=$(grep -F " *$f" "$D/SHA256SUMS_${DATA}_${R}.txt" | cut -c1-64)
    [ "$h" = "$h2" ] || { echo "ROZNICA: $f"; ZLE=$((ZLE+1)); };;
  esac
done < "$SUMY_R56"
echo "STL z pakietu R56: $N, identyczne w R57: $((N-ZLE))"; [ "$ZLE" = 0 ] || { echo "BLAD: pliki R56 zmienione"; exit 1; }
echo "Pakiet gotowy: $D"; find "$D" -type f | wc -l; du -sh "$D"
