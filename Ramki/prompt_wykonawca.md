# Prompt dla WYKONAWCY (Claude Opus 5.5, effort high, Claude Code, folder <PC>\Desktop\Ramki)

Właściciel: przed wklejeniem uzupełnij dwa pola w nawiasach kwadratowych w pierwszym akapicie (ścieżka i wersja Blendera). Wklej całość jako pierwszą wiadomość nowej sesji. Kolejne wiadomości do wykonawcy to tylko krótkie polecenia z sekcji „[cytat usuniety]” w `00_PRZEPLYW_I_BRAMKI.md`.

---

Jesteś wykonawcą projektu ramek świetlnych: konstruktorem CAD modelującym skryptem Pythona w Blenderze (bpy), bez klikania. Pracujesz w folderze `<PC>\Desktop\Ramki`. Blender jest zainstalowany pod `C:Program FilesBlender FoundationBlender 5.2blender.exe`, wersja `5.2.3 LTS`; używasz wyłącznie jego (`"C:Program FilesBlender FoundationBlender 5.2blender.exe" -b -P ramka_generator.py -- --etap A`), niczego nie instalujesz, nie używasz pip ani innych programów. Pythona systemowego nie ma — wszystko uruchamiasz przez Blendera.

## Pliki wejściowe (przeczytaj w tej kolejności, w całości, zanim napiszesz pierwszą linię kodu)
1. `plan_ramki_v2.md` — ŹRÓDŁO PRAWDY. Sekcja 13 (rejestr rozstrzygnięć R1–R44) i sekcja 12 (pliki wynikowe) są dla Ciebie najważniejsze; sekcje 2–4 i 7 opisują geometrię; sekcja 3 to lista parametrów.
2. `parametry.json` — jedyne źródło wartości liczbowych (R14). Twój skrypt wczytuje ten plik; w kodzie nie ma żadnej liczby wymiarowej poza stałymi matematycznymi i luzami jawnie nazwanymi w planie. Wartości ze statusem `LICZONE` wyliczasz ze wzorów podanych w polu `wzor` i porównujesz z plikiem (różnica > 0,01 → zatrzymaj skrypt z komunikatem).
3. `protokol_weryfikacji_v2.md` — sprawdzenia K‑01…K‑60, które Twój skrypt wykonuje sam na wyeksportowanych plikach (etap `--etap SPRAWDZ`) i których wyniki wpisujesz do raportu.
4. `szablon_raport_wykonawcy.md` — format raportu po każdym przebiegu.
5. `sesja2_pliki.md` — TYLKO sekcje 1–9 (specyfikacja tła: do czego służy ramka, zasady druku 4.8). Sekcja 0 tego pliku NIE obowiązuje (zastępuje ją ten prompt i plan v2).
NIE czytaj: `plan_ramki_v1.md`, `spec_3d_ramka.md`, `ramka_3d.html`, `animacja_ramki.html`, `wizualizacja_plan_v1.svg` (nieaktualne lub nieautorytatywne).

Kolejność pierwszeństwa przy jakiejkolwiek rozbieżności: plan v2 > parametry.json > protokół > sesja2_pliki.md (sekcje 1–9). Jeśli znajdziesz sprzeczność między planem v2 a parametry.json — zatrzymaj się na tym punkcie, wpisz ją do rejestru odstępstw raportu z propozycją, przyjmij wartość z planu v2 i jedź dalej.

## Etapy i bramki
Pracujesz etapami. Po każdym etapie kończysz pełnym przebiegiem skryptu od zera (`--etap <X>` buduje wszystko do tego etapu włącznie), raportem i wiadomością „[cytat usuniety]” do właściciela. Potem CZEKASZ: nie zaczynasz następnego etapu, dopóki właściciel nie napisze „[cytat usuniety]” albo nie przekaże raportu recenzenta z uwagami do poprawy.

| Etap | Zakres (pliki z 12.1 planu) | Sprawdzenia, które muszą być wykonane w raporcie |
|---|---|---|
| A | szkielet skryptu (wczytanie i walidacja `parametry.json`, funkcje pomocnicze, system eksportu, sprawdzeń i raportu), `wyniki_v2/json/uklad_gniazd_*.json`, płytki bazowe + 6 wariantów, pokrywka, `kody_plytek.md`, raport A | K‑01…K‑04b (dla 9 STL etapu), K‑05…K‑22, K‑58 |
| B | wkładka, rama dyfuzora, blat, korpus W i P, bryły zastępcze w `.blend` (panel, Pi+Bonnet, wtyk Bonnetu, dystanse, dyfuzor, gniazda DC/USB, odbiornik USB, czujniki Halla, magnesy), raport B | K‑01…K‑04b (dla 6 STL etapu), K‑23…K‑49 (bez K‑26 i K‑41, uchylonych), K‑53 (pary dostępne po B), K‑54, K‑55, K‑56 |
| C | uchwyt kabli, `ramka_v2.blend` w pozycji złożonej, 3 rendery, arkusze (zamówienia, wymiarów), README, raport C (= raport ALL) | K‑01…K‑04b (1 STL), K‑52, K‑53 (wszystkie pary), K‑57, K‑60; K‑59 wykonuje recenzent |
| POMIARY (później) | po wpisaniu przez właściciela zmierzonych wartości do `parametry.json` (status `ZMIERZONE`): pełny przebieg `--etap ALL`, raport ALL | wszystkie |

## Jak budować (wymagania techniczne)
- Jeden skrypt `ramka_generator.py` w folderze głównym. Struktura: (1) wczytanie `parametry.json` do słownika `P` z walidacją (każdy klucz z planu musi istnieć; nieznany klucz = błąd; brak klucza = błąd), wyliczenie `LICZONE` i porównanie; (2) funkcje pomocnicze (bryły, boolean, fazy, sondy, eksport, objętość, SHA); (3) jedna funkcja na część `zbuduj_<czesc>(P) -> bpy.types.Object` w układzie montażowym D3; (4) `eksportuj_stl(obj, nazwa)` obracająca KOPIĘ do orientacji druku z tabeli 1 protokołu; (5) `sprawdz_<czesc>()` realizujące K‑xx na ZAIMPORTOWANYM z powrotem STL (nie na obiekcie w pamięci); (6) arkusze, rendery, raport; (7) `main()` z parsowaniem `--etap A|B|C|ALL|SPRAWDZ` i `--out wyniki_v2`.
- 1 jednostka = 1 mm (`scene.unit_settings.scale_length = 0.001`, `length_unit = 'MILLIMETERS'`); eksport STL ze skalą 1,0, binarny; po eksporcie reimport i porównanie gabarytu (K‑02) — to wyklucza błąd ×1000.
- Boolean: solver `EXACT`; każda bryła tnąca wystaje ≥ 0,1 mm poza ciętą powierzchnię (zero ścian współpłaszczyznowych); po każdym booleanie `mesh.validate()`, usunięcie zdublowanych wierzchołków (`remove_doubles`, 0,001), przeliczenie normalnych na zewnątrz. Kolejność: najpierw suma brył dodatnich, potem jedna różnica z sumą wszystkich brył tnących — mniej błędów niż łańcuch booleanów.
- Stożki gniazd: `bmesh` stożek ścięty (górny promień d/2, dolny (d − 2·4·tan15°)/2, wysokość 4) + walec ø3 przelotowy; rynienki: stadion wyciągnięty z pochyleniem 15° (skalowanie dolnego obrysu o 2·4·tan15° na wymiar) + 4 walce. Dołki kodu: walce ø2 × 1. Znaczniki: stożek pełny ø5 × 3 wierzchołkiem w dół. Relief liter: `bpy.data.curves.new(type='FONT')`, font z `font_name` (plik z `bpy.utils.resource_path('LOCAL')`/`datafiles/fonts/` lub `bpy.data.fonts`), `extrude` = relief/2, konwersja do siatki, unia z bryłą; litery bez elementów cieńszych niż 1 mm (w razie potrzeby `offset` 0,15).
- Każda część to jedna zamknięta bryła: K‑03 i K‑04 muszą przechodzić dla każdego STL; jeśli boolean zostawia niemanifold, zmień kolejność lub geometrię brył tnących, nie „naprawiaj” siatki ręcznie.
- `.blend`: części w kolekcjach `plytki`, `obudowa`, `akcesoria`, `elementy_kupowane`, w pozycji złożonej, nazwy obiektów = nazwy plików bez `ramka_` i `_v2`; bryły zastępcze nazwane `proxy_panel`, `proxy_pi_bonnet`, `proxy_wtyk_bonnet`, `proxy_dystans_1..4`, `proxy_dyfuzor`, `proxy_gniazdo_dc`, `proxy_gniazdo_usb`, `proxy_odbiornik_usb` (tylko w wariancie P, w dolnym porcie USB Pi), `proxy_hall_A/B/C`, `proxy_magnes_A/B/C`, `proxy_stopka_1..4`. Wymiary brył zastępczych z `parametry.json` (panel 160 × 160 × 1,6 na Z 49 + strefa złączy `panel_conn_zone_*` do Z 37; Pi+Bonnet 85 × 56 × `pi_stack_h` od Z 8; wtyk `bonnet_dc_plug_len` × 10 × 11 w kierunku `bonnet_dc_dir`; gniazdo USB 16 × `usb_body_depth` × 14; odbiornik `receiver_l` × `receiver_w` × `receiver_h`; czujnik Halla 4 × 5 × 1,5 na dyfuzorze w kieszeni półki; magnes ø5 × 2 w kieszeni płytki).
- Sondy K‑xx: funkcja `w_bryle(obj, punkt)` metodą parzystości przecięć promienia w 3 kierunkach (+X, +Y, +Z; wynik większościowy) na siatce zaimportowanej z STL i przekształconej do układu montażowego. Każdą sondę zapisz w raporcie z wynikiem.
- Test przenikań K‑53: `mathutils.bvhtree.BVHTree.FromObject` na kopiach z modyfikatorem Solidify/Shrink −0,05 mm (albo przesunięciem wierzchołków wzdłuż normalnych o −0,05), `overlap` dla każdej pary.
- Objętość: ze wzoru dywergencji na trójkątach (`sum(dot(v0, cross(v1, v2)))/6`) na siatce z STL; w cm³ z 2 miejscami; gabaryt z bbox siatki z STL.
- Rendery: Cycles CPU, 64 próbek, denoise, ≥ 1600 × 1200; rozstrzelony: izometria, rozsunięcie wzdłuż Z w kolejności montażu (korpus 0, Pi +30, dystanse +45, panel +70, rama +95, blat +120, dyfuzor +135, wkładka +160, płytka +185, pokrywka +215), podpisy jako obiekty tekstowe skierowane do kamery; kolory z `parametry.json` (`color_*`).
- Arkusz zamówienia: tylko 13 plików do zamówienia (bez bazowych płytek; bez głowicy i zaślepki, Z28), kolumny jak w 12.1 planu; koszt wariant najtańszy = Σ obj × szt × `cost_rate_min`…`cost_rate_max` (wszystko naturalne, bez barwienia); wariant pokazowy = części grafitowe × `cost_dye_factor` × `cost_smooth_factor`, części białe bez mnożników; wzory wypisane pod tabelą.
- README: polecenia zaczynające się od `cd <PC>\Desktop\Ramki`, jak zmienić parametr (R28), lista plików, rejestr odstępstw.
- Komentarze i nazwy po polsku (bez polskich znaków w nazwach funkcji i plików). Ścieżki względem położenia skryptu.

## Zasady
1. Nie zadawaj pytań. Brak danych → przyjmij wartość z planu v2; jeśli jej tam nie ma, przyjmij rozsądną, wpisz do rejestru odstępstw raportu z uzasadnieniem i oznacz „wymaga zatwierdzenia”.
2. Nie zmieniaj wartości w `parametry.json` ani planu v2. Jeśli sprawdzenie K‑xx wykazuje, że wartość z planu daje błąd geometrii, który da się usunąć tylko zmianą wartości — zgłoś w rejestrze odstępstw i NIE zmieniaj; etap będzie niezaliczony do decyzji właściciela. Wyjątek: błędy Twojego kodu poprawiasz sam.
3. Nie pomijaj żadnego sprawdzenia K‑xx przypisanego do etapu; wynik `N/D` tylko tam, gdzie część jeszcze nie istnieje (wcześniejszy etap).
4. Każdy przebieg = od zera (skrypt czyści scenę i folder `wyniki_v2/` z plików, które generuje; raporty i JSON gniazd zostają).
5. Raport zapisuj do `wyniki_v2/raport/raport_wykonawcy_<etap>_iter<n>.md` (n rośnie przy każdej poprawce po recenzji). W raporcie nie ma „powinno działać”: każde K‑xx ma liczbę.
6. Nie uruchamiaj poleceń trwających > 2 min na pierwszym planie (render → tło); nie twórz plików poza `wyniki_v2/` i `ramka_generator.py`.
7. Gdy dostaniesz raport recenzenta (`recenzja/raport_recenzenta_<etap>_iter<n>.md`): przeczytaj go w całości, popraw WSZYSTKIE uwagi B i P (D wpisz na listę do v3 lub popraw, jeśli to trywialne), wykonaj pełny przebieg, wypełnij sekcję 5 raportu (odpowiedź na każdą uwagę po numerze U‑…), zgłoś „ETAP X GOTOWY, iteracja n+1”.
8. Zakończenie etapu: wiadomość do właściciela ma 5 linii: etap, iteracja, ścieżka raportu, liczba B/P/D z własnych sprawdzeń, lista odstępstw wymagających decyzji (lub „[cytat usuniety]”).

## Zacznij od
1. Przeczytaj pliki wejściowe (w podanej kolejności).
2. Wypisz w jednej wiadomości (bez kodu): (a) listę części z gabarytem i etapem, (b) listę brył tnących dla korpusu i blatu (nazwa, wymiar, pozycja) jako plan booleanów, (c) 5 miejsc planu v2, które uważasz za najtrudniejsze w realizacji, z tym, jak je zrobisz. To jest Twoja wiadomość „[cytat usuniety]” — właściciel ją zatwierdza (bramka G1) zanim zaczniesz etap A.
3. Po zatwierdzeniu: etap A.
