# Notatki wykonawcy dla następcy (aktualizowane w miejscu)

**Stan na (1.11, R55):** R55 iter1 oddana (`raport_wykonawcy_R55_iter1.md`, `--etap C --iter 1 --raport R55`): tylko teksty o żywicy w generatorze (SHA `72e64aad…`) i arkusze; 17 STL bez zmian; sekcja 13. Wcześniej: iteracja R54 iter1 oddana (`raport_wykonawcy_R54_iter1.md`, przebieg `--etap C --iter 1 --raport R54`): B 0 / P 0 / D 0; generator SHA `f84e25ee…`; szczegóły w sekcji 12 niżej. Wcześniej: etap C iteracja 2 (R52) oddana 27.10: B = 0, P = 0, D = 0 (`raport_wykonawcy_C_iter2.md`); SPRAWDZ iter2 na końcowym zestawie B 0 / P 0 / D 0. Czeka na nadzór / recenzję C iter2, potem pomiary (ALL). A (G2), B iter2 (G3), B iter3 (G3'), C iter1 (G4) i G4b zaliczone.

**Plik:** `ramka_generator.py`, ok. 3970 linii; SHA‑256 `dca71676…` (raporty C iter2 i SPRAWDZ iter2, sekcja 1). Kopia wersji C iter1 (`cf643dbd…`): scratchpad `ramka_generator_C_iter1.py`.

**Następca:** zacznij od sekcji 4 („Stan i co dalej”) i sekcji 3 („Pułapki”). Kodu nie pisz od nowa, tylko dopisz etap C. Sekcja 7: przejęcie przez wykonawcę 2 i znalezione nieścisłości.

## 1. Struktura `ramka_generator.py`

Sekcje w kolejności występowania w pliku:

### Stałe narzędziowe (nie są wymiarami części, więc mogą być w kodzie)

| Stała | Wartość | Znaczenie |
|---|---|---|
| `NADDATEK` | 0,1 | bryły tnące wystają, bryły dodatnie są zanurzone o 0,1 |
| `SCALANIE` | 0,001 | `remove_doubles` po booleanie |
| `SPAW_IMPORT` | 1e‑5 | spawanie wierzchołków po imporcie STL |
| `KROK_PROMIENIA` | 1e‑4 | przeskok za trafieniem przy liczeniu przecięć |
| `DL_CIECIWY` | 0,25 | długość boku wieloboku na łuku (mm) |
| `MIN_SEG` / `MAX_SEG` | 32 / 256 | min. i maks. liczba boków okręgu |
| `ROZDZ_TEKSTU` | 8 | rozdzielczość krzywych tekstu |
| `KROK_TEKSTU` | 0,04 | krok siatki pola odległości przy pogrubianiu napisów |
| `TRZON_MIN` | 1,0 | minimalna grubość kreski liter (R22) |
| `ZAPAS_TRZONU` | — | zapas przy doborze pogrubienia |
| `TOL_LICZONE` | 0,01 | dopuszczalna różnica wartości `LICZONE` |
| `TOL_WYM` | 0,1 | tolerancja wymiarów i gabarytów |
| `SONDA_BLISKO` | 0,1 | sondy bliżej ściany są oznaczane * |
| `SKURCZ_K53` | 0,05 | skurcz kopii w teście przenikań K‑53 |
| `POLE_ZDEG` | 1e‑6 mm² | próg trójkąta zdegenerowanego |
| `ODSUNIECIE_WARIANTOW` | 260 | odsunięcie części wariantowych w `.blend` (R47) |
| `ODSTEP_PLYTEK` | 110 | odstęp płytek wariantowych w rzędzie |

- `OBJ_ORIENT`: objętości orientacyjne z tabeli 1 protokołu (pokrywka = 30 po poprawce właściciela).
- `WYMAGANE_KLUCZE`: pełna lista kluczy `parametry.json`. Brakujący albo nieznany klucz to błąd, więc **każdy nowy klucz od sesji 1 trzeba tu dopisać**.
- `PLAN_LICZNOSCI`: klucze z tabeli 3 planu, które w JSON są listami (`vent_slots_rear` → `vent_slots_rear_x`).
- `ODPOWIEDZI`: sekcja 5 raportu dla par (etap, iteracja). **Przy każdej iteracji po recenzji dopisz wiersze**, odpowiedź na każdą uwagę U‑… po numerze.

### (1) Parametry
- `wczytaj_parametry`: płaski słownik `P`, walidacja kluczy. `LICZONE` liczone z pola `wzor` przez `eval`; różnica > 0,01 względem pliku to błąd.
- `porownaj_plan_z_json`: parsuje tabelę 3 planu. Brak klucza to błąd. Różnice liczbowe idą do rejestru odstępstw jako sprzeczność plan ↔ JSON.

### (2) Pomocnicze bmesh
- Profile 2D (CCW):
  - `okrag`;
  - `prostokat`;
  - `prostokat_zaokr`: ta sama liczba wierzchołków dla tego samego `n_luk`, dzięki czemu da się robić loft między różnymi promieniami;
  - `stadion`.
- Bryły:
  - `bm_z_pierscieni`: loft pierścieni z denkami; pierścień 1‑punktowy = wierzchołek stożka; kolejność dowolna, normalne są przeliczane.
  - `bm_pryzmat`, `bm_walec`, `bm_prostopadloscian`.
  - `bm_pierscien`: rura między dwoma profilami.
  - `bm_skorupa`: kubek, użyty w pokrywce.
  - `bm_profil_wyciagniety`, `bm_przesun`.
  - `rozdziel_wyspy`: jeden bmesh na każdą spójną część.
- `obiekt_z_bm`, `usun_obiekt`.
- `oczysc_siatke`: `remove_doubles` 0,001, normalne, `validate`.
- `boolean`: modyfikator EXACT z operandem = kolekcja, czyli suma wszystkich brył w jednej operacji. Wynik przez `new_from_object`, bez `modifier_apply`.
- `zbuduj_z_operacji(nazwa, baza, dodatnie, tnace, dodatnie_po)`: baza → unia dodatnich → jedna różnica → unia `dodatnie_po`.

### Napisy
- `font`: plik `datafiles/fonts/<font_name>.*` (Inter.woff2).
- `kontury_fontu`: krzywa FONT z `fill_mode='NONE'` daje same kontury.
- `_krawedzie`, `_przedzialy_wnetrza`: wnętrze regułą niezerowego nawinięcia.
- `_rdp`: upraszczanie konturu.
- `kontur_pogrubiony`: pole odległości (KDTree z próbek konturu) + marching squares na poziomie `off`.
- `bm_z_konturow`: `triangle_fill` + wyciągnięcie.
- `szerokosci_trzonu`, `metryka_fontu` (wersalik H przy rozmiarze 1).
- `parametry_tekstu`: rozmiar i pogrubienie.
- `bryly_tekstu(P, tresc, wys, relief, cx, cy, opis, pelna)`: napis w XY od −0,1 do `relief`. Opcja `pelna`: cały obrys z diakrytykami ma wysokość `wys`.
- `obrot_z`.

### (3) Części etapu A
- `uklad_pochodne`, `generuj_gniazda`, `wczytaj_uklad`:
  - JSON gniazd jest źródłem prawdy dla `sockets` i `leds`;
  - pola pochodne (znaczniki, wycięcie, dołki, kieszenie, numer) są aktualizowane z parametrów przy każdym przebiegu.
- `bity`.
- `zbuduj_plytke`.
- `wymiary_pokrywki`, `polozenia_garbow`, `zbuduj_pokrywke`.

### (3b) Części etapu B
- Helpery:
  - `bm_transformuj`.
  - `M_os(os, srodek)`: lokalne (u, v, w) → świat; `w` to oś bryły X/Y/Z.
  - `bm_stozek_os`, `bm_profil_os`: walce, stożki i profile wzdłuż osi X/Y.
  - `bm_belka`.
  - `bm_pierscien_poziomy`: pierścień o zmiennym profilu; z niego jest faza wkładki.
  - `bm_polacz`.
  - `pozycje_scian(P)`: (kąt boku, położenie wzdłuż boku) dla R6 (prawy 0°, tył 90°, lewy 180°, przód 270°).
  - `M_sciana(kat, odl)`: lokalny układ ściany, u = na zewnątrz, v = Z, c = wzdłuż boku.
  - `bm_lokalny_box`.
- Części:
  - `zbuduj_wkladke`;
  - `zbuduj_rame`;
  - `wymiary_blatu`, `zbuduj_blat`;
  - `pozycje_podkladek`, `pozycje_bossow_pi`, `zbuduj_korpus(P, napis, nazwa)`.
- Bryły zastępcze:
  - `bryly_zastepcze(P)`: zestaw złożony, układ globalny;
  - `bryly_zastepcze_boczne(P, przes_P, przes_n6)`: odbiornik USB w korpusie P, magnesy B i C w płytce n6.

### (4) Eksport
- `M_druk(P, czesc)`: z układu montażowego do orientacji druku.
- `stl_kanoniczny`: sortuje rekordy STL.
- `eksportuj_stl`:
  - kopia mesha;
  - triangulacja BEAUTY;
  - `rotate_edges` najdłuższej krawędzi trójkątów o polu < 1e‑6;
  - `wm.stl_export` w skali 1, bez jednostek sceny;
  - `stl_kanoniczny`.

### (5) Sprawdzenia
- **Ogólne:**
  - `Siatka`: import STL, transformacja do układu montażowego, spawanie, BVH; `w_bryle` = parzystość w 3 kierunkach odchylonych o ok. 0,1° od osi, większość głosów; `odleglosc`; `max_z_w_obszarze`; `mapa_wysokosci` z promieni.
  - `zapisz_png`.
  - `Wyniki`: K‑xx + wszystkie sondy.
  - `ogolne_stl`: K‑01…K‑04b.
- **Etap A:**
  - `odl_punkt_odcinek`, `ksztalt`, `odl_odcinkow`;
  - `sprawdz_uklad_json`: K‑05;
  - `sprawdz_plytke`: K‑06…K‑15;
  - `sprawdz_scianki_naroznikow`: K‑16;
  - `sprawdz_pokrywke`: K‑17…K‑22;
  - `rzut_cyfry`.
- **Etap B:**
  - `_sondy`, `pierwsze_trafienie`;
  - `sprawdz_wkladke`: K‑23…K‑32;
  - `sprawdz_korpus`: K‑34…K‑44;
  - `napis_korpusu`: K‑43, min Y promieniami;
  - `sprawdz_blat`: K‑45…K‑47;
  - `sprawdz_rame`: K‑48.
- **Złożenie:**
  - `ObiektZlozenia`: wierzchołki globalnie, BVH zwykłe i BVH skurczone o 0,05 wzdłuż normalnych wierzchołków;
  - `obiekt_ze_stl`, `zbuduj_zlozenie(P, stl, out)`: kolekcje, położenia, zapis `.blend`;
  - `sprawdz_zlozenie`: K‑33, K‑44b, K‑49, K‑53 z kontrolą czułości, K‑54, K‑55, K‑56;
  - `Siatka_w`.

### (6) Raport
- `sha256`, `zapisz_kody_plytek`, `sprawdz_kody` (K‑58), `zapisz_raport` (wg szablonu + Załącznik A ze wszystkimi sondami).

### (7) Przebieg
- `przygotuj_scene`, `wyczysc_wyniki`, `nazwa_stl`.
- `etap_A`: zwraca (pliki, `stl`), gdzie `stl` to rdzeń → (ścieżka, `M_druk`).
- `wpis_pliku`.
- `etap_B`: dopisuje wpisy informacyjne do rejestru odstępstw, a każde K‑xx etapu B z wynikiem NIE także tam.
- `rzut_konturow_png`.
- `ODPOWIEDZI`, `main`.

### Kolejność wywołań
`main` → `wczytaj_parametry` → `porownaj_plan_z_json` → `przygotuj_scene` → `wyczysc_wyniki` → `etap_A` → (`etap_B`, jeśli `--etap B`) → SHA plików → `zapisz_raport`.

### Flagi
- `--etap A|B`.
- `C`, `ALL`, `SPRAWDZ`: jeszcze niezaimplementowane, kończą się `BladProjektu`.
- `--out`: domyślnie `wyniki_v2`; ścieżka bezwzględna działa.
- `--iter n`: numer raportu.

## 2. Decyzje implementacyjne nieopisane w planie

### Bryły zaokrąglone bez booleanów
Loft pierścieni `prostokat_zaokr` z offsetem na łuku (ta sama liczba wierzchołków):
- korpus: R5 pionowe + R3 dolna krawędź; cała skorupa jednym loftem (zewnętrze w górę, rant na Z 54,6, wnętrze w dół, denko na Z = `floor_t`);
- blat: R5 + R1,5 górna krawędź;
- płytka: R1 + faza 0,5;
- pokrywka: `bm_skorupa`.

### Booleany
- Jedna unia dodatnich i jedna różnica tnących; operand to kolekcja, solver EXACT.
- Daszki szczelin korpusu dokładane po różnicy (`dodatnie_po`), żeby tnąca szczeliny nie ścięła ich nasady.

### Unikanie ścian współpłaszczyznowych
- Kanał Halla (wys. 1,0) i przelot w ściance (1,5) mają tę samą szerokość. Dlatego są jedną bryłą: profil wzdłuż przekątnej narożnika.
- Łapa ramy: osobny blok zespalający x, y 81,1…84,9, Z 2…4,1, zanurzony w kołnierzu (R46).
- Wkładka składa się z warstw:
  - spód: jeden obrys rama + nasady L + uszy, z otworem w kształcie krzyża (półki w narożach), do Z 2,5;
  - warstwa 2,4…3: ten sam obrys z otworem zaokrąglonym;
  - pierścień ramy 2,9…6;
  - faza jako pierścień tnący, który nie sięga kołka D.
- Słupki blatu i kołnierz mają wspólne dno na Z −14. EXACT to łączy; K‑03 = 0.

### Napisy
Inter.woff2 to font zmienny, a jego kontury składowe się nakładają (np. „1”, „4”). Ani wypełnienie Blendera, ani `TextCurve.offset` nie daje manifoldu, a offset tworzy pętle samoprzecięć. Dlatego napis budowany jest tak:
1. Kontury z `fill_mode='NONE'`, bez offsetu.
2. Wnętrze regułą niezerowego nawinięcia.
3. Pogrubienie o `off`: pole odległości (KDTree), marching squares, krok `min(off/4, 0,04)`.
4. RDP z tolerancją krok/10.
5. Usunięcie odcinków < krok/10. Bez tego EXACT robił niemanifoldowe drzazgi w „RAMKA PORANNA”. **Nie zwiększać tego progu**: przy krok/2 zmieniały się już zatwierdzone pliki A.
6. `triangle_fill` i wyciągnięcie od −0,1 do reliefu.

Wysokość i pogrubienie:
- Wysokość liter = wysokość wersalika H z pogrubieniem.
- `off` = max(`font_offset`, minimum na trzon 1,0 mm).
- Rozmiar fontu = (wys − 2·off) / c.
- Trzon i wysokość są mierzone na zbudowanej literze H i trafiają do raportu.
- Napis korpusu ma ok. 104 mm szerokości przy 8 mm (R47 dopuszcza).
- Napis na przedniej ściance korpusu: budowany w XY, potem macierz (x, y, z) → (x, −z − B/2, y).

### Transformacje eksportu (`M_druk`)
| Część | Transformacja |
|---|---|
| płytki | Z + 8 |
| pokrywka | dokładnie Rx180, potem Z + `label_relief_h` |
| wkładka | Z + `tab_pin_h` |
| rama, korpus | tożsamość (rama modelowana w układzie ze spodem łap na Z 0) |
| blat | dokładnie Rx180 macierzą (1, −1, −1), bez przesunięcia |

Sprawdzenia biorą `M_druk.inverted()`.

### Złożenie (`zbuduj_zlozenie`)
- **Położenia w zestawie złożonym:**
  - blat i wkładka: +`blat_top_z`;
  - rama: `blat_top_z` − `blat_t` − `rama_h` − `rama_ear_t` (= 44,6);
  - płytka n1: +`blat_top_z` + `insert_shelf_h` + `plate_thickness` (= 69,1);
  - pokrywka: + 16 nad płytką (= 85,1).
- **Części wariantowe** (poza testem K‑53):
  - korpus_P (+ odbiornik USB) na +260 X;
  - pozostałe płytki w rzędzie y = −260, od x = −385 co 110, Z + 8;
  - magnesy B i C w płytce n6.
- **Bryły zastępcze** są z parametrów:
  - dystans: walec `standoff_d`;
  - wtyk Bonnetu: górna krawędź na szczycie stosu Pi, kierunek z `bonnet_dc_dir`;
  - nakrętka DC: grubość `dc_pocket_wall`;
  - odbiornik USB: na krawędzi portów Pi, oś y Pi, Z od spodu PCB.
- **K‑53:** skurcz −0,05 wzdłuż normalnych wierzchołków. Raport podaje kontrolę czułości: pary stykowe bez skurczu dają setki przecięć, ze skurczem 0.
- **K‑56:** promienie z góry co 0,5 nad pasem przednim (x ±80, y −80…−52,3) i prawym (x 52,3…80, y −80…52,3); najwyższe trafienie musi być dyfuzorem na 58,6.

### Kanał kablowy wkładki (R51)
- (A) w dnie ścianki tylnej przy rowku, y 48,8…50,9, x 44…52,4;
- (B) łącznik x 44…46 do kanału (C);
- (C) pod nasadą L, y 54,15…56,15 (środek części tylnej nasady), x 44…65,1;
- (D) pod uchem, x 63…65,1, y 54,25…90.

Wszystkie odcinki mają wysokość `tab_cable_channel_h`.

## 3. Pułapki Blendera 5.2.3 i obejścia

- **Kod wyjścia.** Wyjątek w skrypcie `-b -P` nie zmienia kodu wyjścia Blendera. `main` łapie wyjątki i robi `sys.exit(1)`. Zawsze sprawdzaj w logu linię `[ramka] RAPORT … B=… P=… D=…`.
- **Zaznaczanie.** `view_layer.objects` po usuwaniu obiektów może zawierać None; zaznaczam przez `scene.objects` ze sprawdzeniem.
- **Niedeterminizm EXACT.** Boolean EXACT jest wielowątkowy, więc ta sama geometria wychodzi w różnej kolejności trójkątów i SHA STL się zmienia. `stl_kanoniczny` sortuje rekordy; dwa przebiegi dają bajtowo identyczne pliki (K‑59).
  - Nie używaj `dissolve_limit` ani żadnej operacji zależnej od kolejności przed eksportem: psuje determinizm.
- **Mostki EXACT.** EXACT robi mostki (keyhole) w ścianach z otworami, a eksporter STL tnie wielokąty z wierzchołkami współliniowymi na trójkąty o zerowym polu. K‑03 widzi je jako stykające się trójkąty, i to zależnie od kolejności. Lekarstwo: triangulacja BEAUTY + `rotate_edges` w `eksportuj_stl`.
- **Normalne.** `calc_normals_split` nie istnieje w 5.x; `v.normal` jest dostępne od razu.
- **Atrybut `offset`.** `hasattr(bpy.types.TextCurve, 'offset')` zwraca False, ale atrybut działa na instancji (i tak go nie używamy).
- **Import STL.** `bpy.ops.wm.stl_import` / `stl_export` (nowe operatory C++); `global_scale` 1, `use_scene_unit=False`.
- **Rozmiary.** Płaskie ściany nie mają wierzchołków w środku, więc pomiary „min Y wierzchołków” zastępuj promieniami (R47 p. 15 dopuszcza).
- **Python.** Systemowego Pythona nie ma. Skrypty pomocnicze uruchamiaj przez Blendera: `blender -b --factory-startup -P skrypt.py`. Moduł generatora można zaimportować (`sys.path.insert` + `import ramka_generator`); `main` nie ruszy, bo `__name__` ≠ `'__main__'`.

## 4. Stan i co dalej

### Gotowe
- **Etap A** (zaliczony G2). Pliki A są bajtowo identyczne od iter1 A; pokrywka nie zmieniła się mimo zmian w kodzie napisów.
- **Etap B iter2:**
  - 5 STL: wkładka, rama dyfuzora, blat, korpus W i P;
  - `ramka_v2.blend` z czterema kolekcjami;
  - raport `raport_wykonawcy_B_iter2.md`: 54 K‑xx, wszystkie ZAL.
- **Decyzje właściciela wdrożone:** R48, R49, R49a, R51.
  - Rejestr odstępstw zawiera tylko #1 (nakrętka DC) i #2 (odbiornik USB), oba przyjęte informacyjnie.

### Do zrobienia — etap C

#### 1. Uchwyt kabli `ramka_uchwyt_kabli_v2.stl`
- Wymiary: 40 × 20 × 12; stopa 40 × 20 × 2,5 z otworem ø3,4; rowek 1,8 × 4 na płytkę proto; grzebień 1,5 z 3 szczelinami 4 × 8.
- K‑52 każe wykonawcy zdefiniować położenie rowka i grzebienia i wpisać je do `arkusz_wymiarow.md`. Sondy z protokołu: (10, 0, 1) W; (0, 0, 1) POZA; (−10, 0, 8) i (−10, 0, 11,9) POZA (szczelina w grzebieniu przy x = −10); (19, 9, 1) W; (21, 0, 1) POZA. Projektuj tak, żeby te sondy przechodziły.
- Układ: środek stopy, spód Z 0; oś długa (40) wzdłuż Y w złożeniu (R43); boss w (±20, 75).
- Dodaj do `M_druk`, `OBJ_ORIENT` ('uchwyt_kabli': 6), złożenia (kolekcja `akcesoria`, 2 szt. na bossach (±20, 75), Z od wierzchu bossa = `floor_t` + `holder_boss_h`) i do K‑53.

#### 2. Materiały i kolory w `.blend` (R27)
- grafit #3b3e43: korpus, blat, rama;
- biały #efede6: płytki, pokrywka, wkładka, uchwyty;
- pleksi #e8ecef półprzezroczysta;
- PCB #1f6b3a;
- mosiądz #c8a24a: dystanse.
- Wartości `color_*` są w JSON; pleksi, PCB i mosiądz nie mają kluczy (R27 w planie). Jeśli potrzebne, poproś sesję 1 o klucze albo wpisz do rejestru odstępstw.

#### 3. Trzy rendery (Cycles CPU, 64 próbek, denoise, ≥ 1600 × 1200)
- Renderuj w tle: osobny proces, bo potrwa > 2 min.
- Rendery:
  - **rozstrzelony**: izometria, przesunięcia Z w kolejności montażu z promptu (korpus 0, Pi +30, dystanse +45, panel +70, rama +95, blat +120, dyfuzor +135, wkładka +160, płytka +185, pokrywka +215), podpisy jako obiekty tekstowe skierowane do kamery;
  - **złożony**: 3/4 od przodu, z płytką wieczorną;
  - **płytki**: obie z góry.
- Lista kontrolna K‑60 jest w protokole §11.

#### 4. Arkusze
- `arkusz_zamowienia.csv` i `.md`: dokładnie 13 wierszy, bez płytek bazowych.
  - Kolumny wg 12.1 planu.
  - Ilości z `quantities`, materiały z `materials`.
  - Koszt najtańszy = Σ obj × szt × `cost_rate_min`…`cost_rate_max`.
  - Koszt pokazowy = części grafitowe × `cost_dye_factor` × `cost_smooth_factor`.
  - Wzory pod tabelą; uwaga STEP/FreeCAD dla CNC (K‑57).
- `arkusz_wymiarow.md`:
  - wymiary z siatek;
  - pasowania (tabela 4.11);
  - opis uchwytu dla K‑52;
  - pełny zrzut `parametry.json`.

#### 5. README, raport C, `do_v3.md`
- `README.md`: polecenia od `cd <PC>\Desktop\Ramki`, jak zmienić parametr (R14, R28), lista plików, rejestr odstępstw skopiowany z raportów.
- Raport C, który jest jednocześnie raportem ALL.
- `wyniki_v2/do_v3.md` na G4: lista uwag D.

#### 6. `main`
- Dopisz etap C (A → B → C) i `ALL`.
- `wyczysc_wyniki` już kasuje render/arkusze/README.

### Znane problemy i uwagi
- Rendery w Cycles CPU mogą trwać długo. Uruchamiaj w tle; najlepiej oddzielnym poleceniem z flagą tylko‑render albo w tym samym przebiegu z `run_in_background`.
- K‑59 (recenzent): ten sam SHA przy powtórce zapewnia `stl_kanoniczny`. Nie dodawaj losowości ani zależności od czasu w STL.
- `wyniki_v2/raport/rzuty/` zawiera rzuty kontrolne (cyfry, GÓRA, strzałki wkładki, napisy korpusu). Rzut `rzut_wkladka_PRZOD_*_iter1.png` jest historyczny, z iteracji 1.

## 5. Uruchomienie

```
cd <PC>\Desktop\Ramki
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P ramka_generator.py -- --etap B --iter 2
```

- Czas ok. 25 s.
- Wynik w `wyniki_v2/`, raport `wyniki_v2/raport/raport_wykonawcy_<etap>_iter<n>.md`. W logu szukaj `[ramka] RAPORT … B=0 P=0 D=0`.
- Sprawdzenia są częścią każdego przebiegu; osobnego `--etap SPRAWDZ` jeszcze nie ma.
- **Przebieg próbny** (nie rusza `wyniki_v2`): skopiuj `wyniki_v2/json/*.json` do pustego folderu `X\json\` i uruchom z `--out X` (ścieżka bezwzględna).
- **Porównanie z poprzednimi plikami:** `cmp` plików STL; zatwierdzone pliki A muszą zostać bajtowo te same.

## 6. Klucze `parametry.json` dopisane do walidatora po starcie (`WYMAGANE_KLUCZE`)

| Klucz | Źródło |
|---|---|
| `blat_post_w` | R48 |
| `blat_post_hole_depth` | R49a |
| `rib_start_r` | R51 |
| `tab_root_x_out` | R51 |

- Klucze z R47 (G1) były w JSON przed pierwszym przebiegiem.
- Same wartości zmieniane później (bez nowych kluczy) bierze JSON: `pi_boss_d`, `holder_boss_d`, `blat_skirt_clearance`, `snap_hook_h`, `cover_snap_r`, `insert_hole_m3`/`_m25`, `insert_depth_m3`/`_m25`, `insert_label_h` (0 = bez napisu), `insert_arrow_x` (lista).
- **Każdy nowy klucz od sesji 1 dopisz do `WYMAGANE_KLUCZE`**, inaczej skrypt zatrzyma się błędem „nieznane klucze”.

## 7. Przejęcie przez wykonawcę 2 (2026-10-26)

- Sprawdzone na plikach: SHA‑256 `ramka_generator.py`, `parametry.json` i wszystkich 14 STL w `wyniki_v2/stl/` = SHA z raportu B iter2. Stan plików = stan oddany do recenzji.
- Czekam na komunikat sesji nadzorującej (W‑3 „ETAP B ZALICZONY — zacznij etap C.” albo „RECENZJA … NIE ZALICZONY”) i na R50 (sesja ODPORNOŚĆ, może wymagać powtórki części B).

### Nieścisłości znalezione przy przejęciu (bez zmian w plikach)
1. **K‑47, sonda słupka:** kod i raport B iter2 używają (75, 90,5, −8,6) W; protokół podaje (75, 89,6, −8,6) W. Brak wpisu w rejestrze odstępstw. Obie sondy leżą w materiale słupka (y 89,2…91,0). Przy następnym przebiegu: sonda z protokołu (ew. obie).
2. **Plan, nieaktualne opisy po R48/R49/R49a/R51** (geometria bierze liczby z JSON, więc STL bez wpływu):
   - sekcja 7, tabela mocowań: otwory ø3,4 × 5 / ø4,0 × 5 / ø4,0 × 6, „od lica 97,2” (ma być ø2,1 / ø2,5, lico 97,0);
   - 4.4 i 4.11: słupki „x ±72…78” (R48: ±71…79); 4.11 wiersz „Napis PRZÓD a kołnierz pokrywki” (R51: napisu nie ma);
   - sekcja 7 „Wentylacja”: luz kołnierza 0,3 (R48: 0,5); sekcja 9 krok 7: „każda wkładka licuje” (R49: bez wkładek);
   - sekcja 14 bez pozycji R49a i R51; nagłówek sekcji 13 „R1…R51”, a R50 jeszcze nie wpisane.
3. **Protokół, opisy:** K‑36 „otwór ø3,4”, K‑47 „otwór ø4 od lica 97,2 do 91,2”, tabela 1 rama „uszy ø8 × 4” (R46: łapy 13 × 13). Sondy w osiach otworów nadal poprawne. Objętość orientacyjna ramy: tabela 1 = 20, plan sekcja 11 = 18.
4. **`parametry.json`:** opis `pi_boss_d` mówi o wkładce M2,5 (R49). Brak kluczy kolorów pleksi / PCB / mosiądz (R27) — potrzebne do renderów etapu C. Brak klucza na otwór ø3,4 stopy uchwytu kabli (4.9) i na położenie rowka / grzebienia (K‑52: definiuje wykonawca).
5. **Arkusz zamówienia vs decyzje właściciela:** `quantities` i `materials` mają 13 pozycji, wszystkie PA12 (K‑57 tego wymaga). Według `00_NADZOR_STAN.md` i `00_PRZEPLYW_I_BRAMKI.md` §11/11a pokrywki, ramy dyfuzora i uchwyty drukuje kolega (FDM PETG), płytki wieczorne może żywica. Do decyzji, czy arkusz ma kolumnę / uwagę „[cytat usuniety]”.
6. **Skrypt:** `--etap SPRAWDZ` (prompt, plan 12.2) nie istnieje; recenzent A prosi, żeby poprawki wyników robić ponownym przebiegiem, nie edycją raportu. Dopisać w etapie C. Komentarze w kodzie mówią jeszcze o „wkładkach M3/M2,5” (kosmetyka).

## 8. Przygotowanie etapu C (wykonawca 2, po G3, przed R50) — kod gotowy, przebieg do `wyniki_v2/` NIE uruchomiony

Polecenie nadzoru po G3: przygotować kod C bez przebiegu; W‑3 wstrzymane do R50 (iteracja B3). Kopia skryptu sprzed zmian: `scratchpad/ramka_generator_B_iter2.py` (SHA d7222834…, = raport B iter2).

### Co doszło do `ramka_generator.py`
- **Tryby:** `--etap C` i `ALL` (A → B → C), `--etap SPRAWDZ` (bez budowy: wykrywa etapy po kompletach STL w `out/stl`, JSON gniazd tylko czyta, nie zapisuje `.blend`/arkuszy/README; raport `raport_wykonawcy_SPRAWDZ_iter<n>.md`, rzuty z przyrostkiem `_SPRAWDZ_iter<n>`), `--bez-renderow` (przebieg próbny; K‑60 = NIE).
- **Przebudowa przebiegu:** `etap_A/B/C(..., iter_, buduj)`; `iter_` jest teraz znacznikiem tekstowym (`'iter2'`) w nazwach rzutów — nazwy plików jak dotąd. Złożenie wyjęte z `etap_B` do `main`: `zbuduj_zlozenie(P, stl)` → `(Z, wszystkie)`, zapis osobno `zapisz_blend(out)`. Odstępstwa informacyjne B → `odstepstwa_informacyjne_B`, K‑xx z NIE do rejestru → `wyniki_nie_do_rejestru` (lista `K_ETAPU`). Objętości i bbox STL każdego rdzenia w `DZIENNIK['stl']` (arkusze, K‑57).
- **Uchwyt kabli** (`wymiary_uchwytu`, `zbuduj_uchwyt_kabli`, `sondy_uchwytu`, `sprawdz_uchwyt` = K‑52): obrys boczny XZ jednym profilem wyciągniętym wzdłuż Y (stopa + blok rowka + grzebień, bez ścian współpłaszczyznowych) − otwór ø3,4 − rowek 1,8 × 4 wzdłuż Y przelotowy w x = 12,5 − 3 szczeliny 4 × 8 w grzebieniu x = −10 (y −6/0/6, zęby 2). Objętość ≈ 4,8 cm³ (tab. 1: 6 ± 30 %). W złożeniu 2 szt. `uchwyt_kabli_L/P` na bossach (±20, 75), Z 8, obrót 90° (`holder_axis` Y); K‑52 część montażowa: spód = wierzch bossa, promień w osi otworu trafia boss. **Po R50‑U8 uchwyt znika — do usunięcia w B3** (funkcje, `RDZENIE_ETAPU['C']`, K‑52 → N/D/uchylone, klucze proponowane `holder_*`).
- **Klucze proponowane** (`KLUCZE_PROPONOWANE`, funkcja `proponowany`): walidator je przyjmuje, jeśli nadzór je dopisze; do tego czasu wartość z planu + wpis w rejestrze odstępstw („tak — klucz do dopisania”). Lista dla nadzoru niżej.
- **Rendery** (`przygotuj_scene_renderu`, `rendery`): materiały R27 na obiektach `.blend` (grafit, biały, pleksi α 0,55, PCB, mosiądz; gniazda/wtyk/magnesy = mosiądz, Hall/stopki = grafit), świat, słońce, Cycles CPU 64 próbek + OIDN, 1600 × 1200, `Standard`; kamera `kamera_zlozony` zapisana w `.blend`. `.blend` zapisany PRZED renderami (pozycja złożona); rendery przestawiają obiekty tylko w pamięci. Rozstrzelony: kamera ortogonalna (wysokość 22°, azymut 45°, przód‑prawo), `ROZSUNIECIE` z promptu; uchwyty i gniazda DC/USB (wnętrze korpusu, w rzucie zasłonięte) wysunięte w lewo ekranu o 280 mm; 13 podpisów (`PODPISY` = lista K‑60 §11) fontem DejaVuSansMono (Inter ma nakładające się kontury), w kolumnach z liniami odniesienia, przed wszystkimi częściami. Widoczność każdej podpisanej części mierzona `scene.ray_cast` z próbek wierzchołków w stronę kamery (K‑60). Płytki: n1 i n4 z góry, ortogonalnie.
- **Arkusze:** `arkusz_zamowienia.csv` (`;`, przecinek dziesiętny, UTF‑8 z BOM; koszty min/max w osobnych kolumnach; koszty z objętości zaokrąglonej do 0,01 — tak jak w CSV) i `.md` (zakresy, sumy wszystkich pozycji i „w tym do drukarni”, stawki i wzory, uwaga STEP/FreeCAD); kolumny „wykonanie” i „szt. do drukarni” z `print_route`. `arkusz_wymiarow.md`: §1 gabaryty/objętości, §2 ok. 90 wymiarów z siatek promieniami (`lista_wymiarow`, typy z/w/p) z nominałem z JSON i ✓/✗ (0,05), §3 22 pasowania zmierzone w złożeniu (`lista_pasowan`, luz ze znakiem: ujemny = zahaczenie), §4 opis uchwytu dla K‑52, §5 klucze proponowane, §6 pełny zrzut `parametry.json`.
- **K‑57** (`sprawdz_arkusz_zamowienia`): CSV ↔ pomiar STL z tego przebiegu, quantities, materials, wzory kosztów, 13 wierszy, brak bazowych, STEP/FreeCAD. **K‑59** = N/D (recenzent). **K‑60** (`sprawdz_K60`): 3 PNG ≥ 1600 × 1200, widoczność 13 podpisów, komplet K‑xx etapów w raporcie (`k_raportu`), zrzut JSON w arkuszu = plik, LICZONE.
- **README.md, do_v3.md** (lista `DO_V3`: D z recenzji A i B + nieścisłości dokumentów z §7 + boss uchwytu) — tylko w C/ALL.
- Poprawki z polecenia: komentarze R49 (bez „wkładek”), K‑47 sonda z protokołu (75, 89,6, −8,6) + dotychczasowa (75, 90,5) jako druga.

### Przebiegi próbne (poza `wyniki_v2/`, w scratchpadzie)
- `parametry.json` z B iter2 odtworzony w scratchpadzie (SHA 3749b7b5… = raport B iter2), plan jako zaślepka sekcji 3 (bieżący plan ma już R50).
- `--etap C --bez-renderow`: 24 s, B 0 / P 1 (tylko K‑60 bez renderów); K‑52 23/23 sond, K‑57 ZAL (po poprawce: `;` w polu tekstowym, koszt z objętości zaokrąglonej), arkusz wymiarów 0 ✗ (po przesunięciu 3 punktów pomiaru: wycięcie palcowe, R3 dolnej krawędzi, otwór DC na drodze promienia).
- Regresja: 13 z 14 STL etapów A/B bajtowo = B iter2. **Wyjątek `ramka_wkladka_v2.stl`**: SHA różny przy KAŻDYM przebiegu, także oryginalnym skryptem B iter2 (d7222834…) — to istniejąca niepowtarzalność, nie skutek zmian. Te same 1113 wierzchołki, 2242 trójkąty; różnią się przekątne 2 płaskich prostokątów fazy w narożnikach A i C (remis BEAUTY: równe przekątne, rozstrzygany kolejnością wierzchołków z wielowątkowego EXACT). K‑59 recenzenta przy innym SHA: objętość ± 0,001 i gabaryt ± 0,01 → ZAL z uwagą D. Propozycja do B3: w `eksportuj_stl` po triangulacji kanoniczny wybór przekątnej w remisach (krawędź płaskiego czworokąta o równych przekątnych → przekątna z najmniejszym leksykograficznie wierzchołkiem); może zmienić bajty innych plików z remisami, więc tylko w iteracji, która i tak idzie do recenzji.

### Klucze do dopisania przez nadzór (propozycja; walidator już je przyjmuje)
| Klucz | Wartość | Źródło | Po R50 |
|---|---|---|---|
| `color_plexi` | "#e8ecef" | R27 | potrzebny |
| `color_pcb` | "#1f6b3a" | R27 | potrzebny |
| `color_brass` | "#c8a24a" | R27 | potrzebny |
| `print_route` | {plik: [wykonanie, szt. do drukarni]} — 13 pozycji wg §11/11a | `00_PRZEPLYW` §11/11a | potrzebny, z nowymi częściami R50 (tulejka DC, podkładki 05/1/2; bez ramy i uchwytu; pokrywka FDM) |
| `holder_foot_hole_d` | 3.4 | plan 4.9 | zbędny (R50‑U8) |
| `holder_slot_count` | 3 | plan 4.9 | zbędny |
| `holder_comb_x` | −10 | K‑52 | zbędny |
| `holder_block_x0` | 5 | wykonawca, K‑52 | zbędny |

### Do zrobienia w B3 (po komunikacie R50) — z punktu widzenia kodu C
- Usunąć uchwyt i ramę dyfuzora z budowy, złożenia, renderów (`PODPISY`, `grupa_rozsuniecia`, `ROZSUNIECIE`: rama), arkuszy (`lista_wymiarow`, `lista_pasowan`: rama–panel, łapy–bossy), `OBJ_ORIENT`, `M_druk`, `K_ETAPU`; dodać tulejkę DC i podkładki panelu (nowe STL, K‑xx z protokołu po R50).
- `WYMAGANE_KLUCZE`: dopisać nowe klucze R50, usunąć skasowane (walidator zatrzyma się na obu).

### Wynik przygotowania (stan końcowy, 26.10 ~22:35)
- `ramka_generator.py` SHA‑256 `42b2ff1bee15d8313356cba9b1a6ab3d9aeaa63b129e8f750804f5939587ff2c`.
- Pełny przebieg próbny `--etap C` (z renderami) na `parametry.json` z B iter2: 39 s (rendery ok. 4 s każdy), **B 0 / P 0 / D 0**; K‑52, K‑53 (26 obiektów, 325 par, 0 przecięć), K‑57, K‑60 (3 × 1600 × 1200, 13/13 podpisów widocznych) ZAL; K‑59 N/D. Arkusz wymiarów: 124 pomiary i pasowania, 0 poza ± 0,05. Rendery obejrzane: rozstrzelony z podpisami, złożony 3/4 z płytką n1, płytki n1 i n4 z góry (orientacja D przód‑prawo poprawna).
- `--etap SPRAWDZ` na tym wyniku: B 0 / P 0 / D 0; nie zmienia żadnego istniejącego pliku (porównanie SHA całego folderu), dopisuje tylko raport i rzuty `_SPRAWDZ_iter1`.
- `wyniki_v2/` nietknięte: 18 plików = SHA z raportu B iter2 (zmieniły się tylko te notatki).
- Środowisko testowe: `scratchpad/test_C/` (kopia skryptu, `parametry.json` B iter2, zaślepka planu). Uruchomienie próbne: skopiować skrypt do `test_C`, `blender -b -P test_C/ramka_generator.py -- --etap C --iter 1 --out wyniki` (cwd = `test_C`).
- Po R50 kod wymaga zmian z listy „Do zrobienia w B3” wyżej; bieżący `parametry.json` (z R50) zatrzymuje walidator (brakujące klucze) — to oczekiwane do czasu iteracji B3.

## 9. Etap B iteracja 3 (R50) — stan po przebiegu 26.10 ~22:55

**Uwaga:** sekcja 8 opisuje stan sprzed R50. Uchwyt kabli, rama dyfuzora i `KLUCZE_PROPONOWANE` z wartościami są już usunięte z kodu (wybór wykonawcy: funkcje usunięte, nie tylko wyłączone z eksportu). `KLUCZE_PROPONOWANE = {}` i `proponowany()` zostają jako mechanizm na przyszłe brakujące klucze.

### Co zmieniono w kodzie (R50, `R50_wdrozenie_zmiany.md`)
- **Walidator:** `WYMAGANE_KLUCZE` wygenerowany z bieżącego `parametry.json` (273 klucze; −49, +21). 4 nowe LICZONE (`snap_pocket_z`, `snap_hook_z`, `blat_screw_z`, `label_pos_z`) liczy istniejący mechanizm pola `wzor`.
- **Korpus:**
  - stadiony panelu (`bm_stadion_os`, `os_rowka`: oś po przekątnej ±55…±65, szer. `panel_pad_d`) i rowki `panel_slot_w` przez dno i stadion, bez pogłębień;
  - bossy Pi z `pi_pos_x` −50; wloty 30 × 4 w (−8, ±10); szczeliny 4/3/3 bez daszków;
  - kieszeń DC: skrzynka x −97,6…`dc_pos_x` (unia z lewą ścianą), wnętrze + okno jednym pryzmatem L (x −95,5…−42; okno `dc_pocket_x_window` ± 25,5); skrypt sprawdza, że prawa krawędź okna = wewn. lico ściany gniazda;
  - otwór ø`dc_hole_d` osią X w ścianie −42…−40 (`dc_socket_axis` musi być "X");
  - USB: okno 16 × 9 + 2 rowki-stadiony osie 60 ± 11,5…14;
  - bez SD, gniazd stopek, żeber, bossów uchwytów; Z kieszeni, wkrętów i napisu z LICZONE.
- **Blat:** bez bossów ramy; kieszeń dyfuzora ostra (`prostokat_r`: r = 0 → prostokąt).
- **Wkładka:**
  - otwór ostry, faza jako pierścień 4‑wierzchołkowy;
  - rowek `wire_rabbet_w` 2,5 × `wire_rabbet` 1,5; przelot w narożniku ma ten sam przekrój i wychodzi poza naroże, więc z rowkiem jest jedna ciągła pustka (sonda K‑25 (−51,5, −51,5, 0,7) POZA);
  - dawny kanał (A) usunięty, bo wnikałby w otwór/półkę; łącznik (B) zaczyna się w rowku. Kołki były już jedną bryłą (stożek 0,5).
- **Pokrywka:** bez otworów i GÓRA; `M_druk` = sam obrót 180° wokół X (wierzch na Z 0); gabaryt 20,0.
- **Bryły zastępcze:**
  - `bm_wtyk_bonnet(P, kierunek)`;
  - gniazdo DC osią X od x = `dc_pos_x` w +X (korpus `dc_socket_body_l` 18) + nakrętka grubości `dc_pocket_wall`;
  - reszta automatycznie z JSON.
- **Sprawdzenia:**
  - sondy K‑34…K‑47 przepisane z protokołu po R50;
  - K‑17 zawiera kontrole odwrotne K‑19 i K‑21 (K‑19, K‑21 = N/D „uchylone” z wynikiem kontroli w uwadze);
  - K‑48 N/D;
  - K‑44b: test 3 kierunków wtyku (−X, −Y, +Y od `bonnet_dc_pos`) względem korpusu, dystansów i panelu — bez samego Pi, na którym gniazdo stoi;
  - K‑49: blat–korpus, dyfuzor, PCB–spód blatu (4,0), nakładka PCB pod oknem (1,0), dystanse na stadionach;
  - K‑54 rozszerzone; K‑53 pary stykowe dystans–korpus, dystans–panel.
- **Etap C (gotowy, nieuruchomiony w `wyniki_v2`):**
  - `zbuduj_tulejke_dc`, `zbuduj_podkladke`, `rdzenie_podkladek` (0,5 → `_05`); K‑52b, K‑52c; K‑52 = N/D;
  - tulejka w zestawie złożonym (kołnierz na licu −42, oś X), podkładki obok zestawu;
  - arkusz zamówienia 15 wierszy: koszt tylko dla materiału zaczynającego się od „PA12 drukarnia”, druk własny w bloku B bez kosztu; grafit = korpus i blat (Z19, `czesc_grafitowa`);
  - rendery: 12 podpisów wg protokołu §11; tulejka, gniazdo DC i USB wysunięte w lewo;
  - lista wymiarów i pasowań przepisana (24 pasowania, m.in. tulejka w otworze 0,0, wtyk −X do ściany 7,5).

### Wyniki
- Oficjalny `--etap B --iter 3`: B 0 / P 0 / D 0, 20 s. Płytki A bajtowo = B iter2 (zatwierdzone); pokrywka nowa (20,0; 30,06 cm³).
- Próba `--etap C` (scratchpad, ten sam `parametry.json`): B 0 / P 0 / D 0, 33 s. K‑52b 7/7, K‑52c 4/4 × 3, K‑53 24 obiekty / 276 par / 0 przecięć, K‑57 15 wierszy, K‑60 12/12 podpisów widocznych; arkusz wymiarów bez ✗ po przesunięciu punktu „wkładka na dyfuzorze” poza rowek.
- **Powtarzalność:** drugi przebieg B3: 12/13 STL bajtowo identyczne. `ramka_wkladka_v2.stl` różni się tylko znakiem zera (−0,0/+0,0) w 6 bajtach zapisanych normalnych; trójkąty i wierzchołki identyczne. Każdy STL ma −0,0 w normalnych, więc normalizacja w `stl_kanoniczny` zmieniłaby bajty także zatwierdzonych płytek — nie wdrożona bez decyzji nadzoru (wpis w `DO_V3`).

### Interpretacje (do wiadomości recenzenta / nadzoru)
- K‑44b „test 3 kierunków od `bonnet_dc_pos`”: wtyk 40 od (−50, 22) w −Y i +Y przechodzi przez obrys samego Pi. Overlap liczony z korpusem, dystansami i panelem, jak wymienia protokół.
- Plan 4.4 p. 3 i 4.11: „kołnierz 95,2…97,2” / „wnętrze kołnierza 97,2” — po R48 kołnierz leży na 95,0…97,0 (skrypt bierze liczby z JSON). Wpis D w `DO_V3`.
- Proxy gniazda DC bez gwintu ø8 w tulejce: brak klucza średnicy (pomiar #16). Wpis D.
- K‑57 (protokół) opisuje „koszt_max × dye × smooth” niejednoznacznie. Arkusz C liczy: najtańszy = obj × szt × stawka min…max; pokazowy = najtańszy × dye × smooth dla korpusu i blatu (Z19). Wzór jest pod tabelą.

## 10. Etap C iteracja 1 — 26.10 ~23:15

- **Polecenie W‑3:** po G3' (recenzja B iter3: ZALICZONY, 2 uwagi D).
- **Przebiegi:**
  - `--etap C --iter 1`: 33 s, B 0 / P 0 / D 0;
  - `--etap SPRAWDZ --iter 1`: B 0 / P 0 / D 0, wszystkie K‑xx A + B + C; żaden plik poza `raport/` się nie zmienił (porównanie SHA).
- **Pliki w `wyniki_v2/`:**
  - 17 STL;
  - `ramka_v2.blend` z materiałami, światłem i kamerą `kamera_zlozony`;
  - 3 rendery;
  - `arkusze/` (zamówienie CSV i MD, wymiary, kody);
  - `README.md` z tabelą plików i SHA;
  - `do_v3.md` (10 pozycji).
- **Dopisane od sekcji 9:**
  - test informacyjny odbiornika USB w położeniu hipotetycznym w zestawie W (uwaga D §6.1 recenzji B3): 0 przecięć, uwaga przy K‑53;
  - `odstepstwa_informacyjne_C` — 5 wpisów w sekcji 4 raportu: wzór kosztu pokazowego, wysunięcie wnętrza na renderze, gwint DC w tulejce, opis kołnierza w planie, powtarzalność wkładki (jedyny „tak — decyzja nadzoru”);
  - README: SHA plików;
  - sortowanie K‑xx w raporcie (K‑52, K‑52b, K‑52c).
- **Własny test K‑59:** pełny `--etap C` w czystej kopii (scratchpad, bez `wyniki_v2`, JSON odtworzony z D6). Pliki bajtowo identyczne z `wyniki_v2`: wszystkie STL oprócz wkładki, oba JSON i wszystkie arkusze. Wkładka różni się tylko znakiem zera w normalnych (sekcja 9).
- **Do zrobienia po pomiarach:** W‑P → `--etap ALL --iter 1`; raport ALL.

## 11. Etap C iteracja 2 (R52) — 27.10

- **Polecenie:** po G4 (recenzja C iter1: ZALICZONY) i G4b (trzecie oko: 0 blokujących). R52 w `parametry.json`: `dc_bush_outer_d` 12 → 11,85 (U1 trzeciego oka). SHA `parametry.json`: `81212b7a…`.
- **Zmiany w kodzie:**
  - K‑52b: poza 7 sondami z protokołu mierzy średnice walca, otworu i kołnierza (4 promienie, ± 0,05). Wynik: 11,848 / 8,200 / 14,999.
  - Arkusz wymiarów §4: średnica walca z 2 miejscami po przecinku (wcześniej `liczba_pl(…, 0)` dałoby „12”). Opis pasowania tulejka–otwór: „wciskane 0,075/stronę (R52, 4.8)”.
  - Rejestr: wpis K‑59 → „rozstrzygnięte przez nadzór (K‑59 kanonicznie)”; nowy wpis informacyjny o tekście K‑52b i planu (ø12 sprzed R52).
  - `ODPOWIEDZI[('C', 2)]` (sekcja 5 raportu).
- **Przebiegi:**
  - `--etap C --iter 2`: 33 s, B 0 / P 0 / D 0.
  - `--etap SPRAWDZ --iter 2`: B 0 / P 0 / D 0; pliki poza `raport/` bez zmian (SHA).
- **SHA STL względem C iter1:** 15/17 bajtowo identyczne.
  - Nowa tulejka: `b393256c…`.
  - Wkładka `ef7503c7…` (C1: `719eeb31…`). SHA kanoniczny (−0,0 → +0,0, skrypt scratchpad `kanon.py`): `f641176c…`, identyczny z obiema czystymi powtórkami C1 (moją i recenzenta).
- **K‑53:** 24 obiekty / 276 par / 0 przecięć. Tulejka w położeniu montażowym: walec ø11,85 w otworze ø12 to luz geometryczny 0,075/stronę (bez przenikania). Bez skurczu: 928 styków z korpusem (kołnierz na licu ściany).
- **Uwaga do sekcji 4:** mechanizm porównania z tabelą 3 planu sam dodał wpis #1 („tabela 3: 12, JSON: 11,85; wymaga zatwierdzenia: tak”). Tabela 3 planu nie jest jeszcze poprawiona po R52; skrypt bierze JSON.

## 12. R54 (1.11.2026) — gniazda i znaczniki w kole pola skanowania (wykonawca 3)

- Zadanie: `R54_wdrozenie_zmiany.md` §5. Zmiany w generatorze (SHA `b94fd473…` → `f84e25ee…`, kopia sprzed w `archiwum/ramka_generator_przed_R54_2026-11-01.py`): 6 nowych kluczy w `WYMAGANE_KLUCZE` (`scan_field_d`, `scan_center_tol`, `work_overhang`, `socket_zone_r` LICZONE, `ev_marker_pos`, `mo_marker_pos`); `pozycje_znacznikow(P, typ)` + `uklad_pochodne(P, typ)` (markers per typ, magnet_pockets nadal z `marker_offset`); K‑05 (a) liczby z `ev_rows`/`mo_rows`, (c) koło `hypot(x, y) + r ≤ socket_zone_r` dla obu końców osi; K‑09 sondy z JSON + 3 sondy dawnych rogów (pozycje `magnet_pockets`, Z −1) W BRYLE; K‑16 promień znacznika ≤ `socket_zone_r` − d/2, znacznik–gniazdo ≥ 3, dołek–znacznik (wszystkie znaczniki) ≥ 1,5, znacznik–kieszeń magnesu (XY) ≥ 1,5, usunięte „stożek–kieszeń (Z)”.
- Pułapka: `lista_wymiarow` brała `sockets[0]` jako gniazdo okrągłe — po R54 id 1 wieczornej to rynienka (`KeyError: d_top`); teraz pierwsze gniazdo `type == 'round'`. Stożek znacznika A w arkuszu wymiarów mierzony w pozycji z JSON.
- Nowy argument `--raport ETYKIETA`: nazwa pliku raportu (`raport_wykonawcy_R54_iter1.md`), tytuł, polecenie w sekcji 1 i README; bez niego nazwa jak dotąd z etapu.
- Stare `wyniki_v2/json/uklad_gniazd_*.json` (24 + 2 / 35 + 2) → `archiwum/*_przed_R54_2026-11-01.json`; skrypt odtwarza je z D6 (`leds` puste). Cały `wyniki_v2/` sprzed przebiegu: `archiwum/wyniki_v2_przed_R54_2026-11-01/`.
- Wyniki: 18 + 2 / 31 + 2; max promień 46,389 / 46,931; znaczniki 44,30 / 44,43 / 44,23; ścianki 3,17/3,01/3,01 i 7,00/3,01/3,01; K‑53 276 par / 0; 9 STL spoza płytek bajtowo = C iter5 (`archiwum/sha256_stl_przed_R54_2026-11-01.txt`, `raport/sha256_stl_po_R54_iter1.txt`). Wkładka: SHA zmienny (znak zera normalnych, odstępstwo #7), siatka identyczna.
- Po recenzji R54: dokumenty stanowiska, model 3D/animacja, pakiet — osobne zadanie (§6 `R54_wdrozenie_zmiany.md`).

## 13. R55 (1.11.2026) — bez żywicy, druk własny tylko FDM PETG (wykonawca 3)

- Polecenie nadzoru: dwa zaszyte teksty o żywicy w `ramka_generator.py` (linie 2954, 3039) → `'FDM PETG (druk własny, R55)'` i `'- Płytki wieczorne n1–n3 liczone do drukarni (R55: bez alternatywy żywicznej).'`; `parametry.json → materials` zmienione przez nadzór. Generator SHA `f84e25ee…` → `72e64aad…` (kopia `archiwum/ramka_generator_przed_R55_2026-11-01.py`).
- Przebieg `--etap C --iter 1 --raport R55` (31 s): 60 sprawdzeń, 55 ZAL, 5 N/D, 0 NIE. Pierwszy przebieg był z `--iter 2` (raport w `archiwum/raport_wykonawcy_R55_probaC_iter2_2026-11-01.md`), powtórzony z `--iter 1` dla zgodności nazwy z poleceniem.
- 16 STL bajtowo = R54 iter1; wkładka SHA inny, siatka identyczna (1806 trójkątów, odstępstwo #7). K‑57 koszty bez zmian. Arkusze: tylko kolumny materiał/technologia i stopka; stare w `archiwum/*_przed_R55_2026-11-01.*`.
- `grep -i żywic` nie daje 0, bo zadany tekst zawiera „żywicznej”, a `materials.opis` nadzoru „bez żywicy” (zrzut w `arkusz_wymiarow.md`) — zgłoszone w raporcie §7.4.
