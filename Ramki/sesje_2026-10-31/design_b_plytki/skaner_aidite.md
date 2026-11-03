# Skaner Aidite A‑IS Pro 3 — co ustalono o polu skanowania i zgodności płytki (DESIGN B, 31.10.2026)

Źródła: wyszukiwanie w sieci 31.10.2026 (agent badawczy, 84 odwołania), `notatki_dokumentacja_skanera.md`, `mail_aidite_zapytanie.md`, instrukcja DS‑EX V2.15 (PDF, machines-3d.com). Nic z tego nie zastępuje testu na egzemplarzu (kryterium 8 planu) — poniżej jest rozdzielone na POTWIERDZONE / POŚREDNIE / BRAK.

## 1. Tożsamość sprzętu

| Fakt | Wartość | Źródło | Pewność |
|---|---|---|---|
| Aidite nie publikuje strony „A‑IS Pro 3”; w katalogu jest „A‑IS Pro” (1,3 MP, < 10 µm, 260 × 270 × 420) | — | https://www.aidite.com/product/detail/21/AIS_Pro.html | potwierdzone |
| Specyfikacja „A‑IS Pro 3” u dystrybutorów (2 × 5 MP, 8 µm, 385 × 260 × 270, 5 kg, czasy 7/14/18/30/66 s, tryby Multi Path / High Quality / AI / Texture / HDR / Reduce High Brightness) jest **identyczna** z broszurą Shining3D AutoScan‑DS‑EX Pro(H) | — | https://www.medicalsearch.com.au/3d-dental-scanner-pro-3/p/283387 ; https://www.dhpsupply.com/itemFiles/AutoScan-DS-EX%20Pro(H)%20One-Page%20Brochure_%202024.pdf | pośrednie (bardzo zgodne) |
| Oprogramowanie DentalScan = OEM Shining3D (już w notatkach) | — | docs.shining3d.com/dentalscan | potwierdzone |

Wniosek: A‑IS Pro 3 ≈ DS‑EX Pro(H). Dane Shining3D dla rodziny DS‑EX traktuję jako obowiązujące do czasu odpowiedzi Aidite.

## 2. Pole skanowania

| Fakt | Wartość | Źródło | Pewność |
|---|---|---|---|
| Pole skanowania DS‑EX / DS‑EX Pro / DS‑MIX (tabela producenta OEM) | **100 × 100 × 75 mm** | https://support.shining3ddental.com/en/support/solutions/articles/60000699807-what-s-the-difference-among-ds-ex-ds-ex-pro-ds-mix | potwierdzone (OEM) |
| Pole DS‑EX Pro(H) (2 × 5 MP) | 100 × 100 × 75 | https://top3dshop.com/de-de/product/shining3d-autoscan-ds-ex-3d-scanner | pośrednie (sprzedawca) |
| Pole A‑IS Pro (1,3 MP) wg polskiego sprzedawcy | 100 × 100 × 75 | https://dentalstore.pl/skaner-a-is-pro-aidite.html | pośrednie (dystrybutor) |
| Pole A‑IS Pro 3 wprost od Aidite | — | — | **BRAK** |
| Wariant 110 × 80 × 80 | nie występuje w żadnym źródle | — | zaprzeczone |
| Kształt bryły pomiarowej (prostopadłościan vs stożek widzenia), kąt triangulacji, odległość robocza | — | — | **BRAK** |

### Rachunek dla płytki 96 × 96

| Cecha płytki | Promień od osi obrotu | W walcu ø100 (r ≤ 50)? | W kwadracie 100 × 100 ustawionym w osiach? |
|---|---|---|---|
| Stożki znaczników (±42, ±42) ø5 | 59,4 (krawędź 61,9) | NIE | TAK (x, y ≤ 44,5) |
| Dołki kodu (−45, −36…−30) | 54–57,6 | NIE | TAK (margines 5) |
| Narożniki płytki (±48, ±48) | 67,9 | NIE | TAK (margines 2) |
| Skrajne gniazda (R1: x ±34,5, y −45; P R5: x ±45) | ≤ 57 | NIE (x = 45) | TAK |
| Wysokość: 8 (płytka) + 10 (prace nad wierzchem) | — | 18 ≪ 75 | TAK |

Interpretacja: 100 × 100 × 75 jest „maksymalnym rozmiarem obiektu”, nie udokumentowanym kształtem pola widzenia kamer przy każdej pozycji stolika. Przy strategii **samego obrotu** (4–6 pozycji) i płytce ułożonej w osiach stolika na pozycjach 0/90/180/270° wszystkie cechy są w kwadracie 100 × 100 (margines 2 mm na narożnikach, 5,5 mm na stożkach); na pozycjach 45° narożniki wystają (przekątna 136 mm), ale stożki (r 59,4) są poza ø100 o 9,4 mm — **w tych ujęciach mogą nie być zarejestrowane**. Skaner skleja ujęcia, więc wystarczy, że każdy stożek jest w 1–2 ujęciach z dobrą ścianką; przy ujęciach co 60° (6 pozycji) nie ma pozycji „w osiach” poza 0/180 — strategia z 4 pozycjami (co 90°) jest dla naszej płytki lepsza niż 6.

**Ocena: na granicy, nieudowodnione.** Test (kryterium 8) pozostaje obowiązkowy. Plan B gotowy do uruchomienia bez nowego projektu: `plate_size` 90 (strefa gniazd 84, rzędy tracą po 1 gnieździe) albo znaczniki przesunięte do promienia ≤ 50 (np. (±35, ±35) → r 49,5 — tylko jeśli rzędy skrajne zostaną skrócone o 1 gniazdo z każdego końca; do przeliczenia w D6).

## 3. Stolik, mocowanie, tryby

| Fakt | Wartość | Źródło | Pewność |
|---|---|---|---|
| Stolik 2‑osiowy (obrót + przechył/swing); instrukcja DS‑EX rozdz. 8 „SysTest” ma ręczne „rotary angle on X / Y axis” (tryb serwisowy) | — | https://www.machines-3d.com/images/Image/File/Manuel/Scanner%203D/Dentaire/Shining3D%20DentalScan%20DS-EX%20User%20Manual%20V2.15.pdf s. 153–157 | potwierdzone |
| Zakres przechyłu w stopniach, blokada przechyłu w strategii produkcyjnej | — | — | **BRAK** (pytanie 5 do Aidite) |
| Mocowanie uchwytów: 3‑punktowy układ magnetyczny + kołek/otwór nr 1/nr 2 („quick release jig” w Pro(H)) | — | https://deltaface.com/shining-3d-ds-ex-metrologic-review/ ; instrukcja rozdz. 1 | potwierdzone (DS‑EX) / pośrednie (Pro H) |
| Średnica talerza, max obciążenie, STEP interfejsu | — | — | **BRAK** (pytania 11–12) |
| Tryb multi‑die: **do 8 stempli** („1–4 dies 18 s, 5–8 dies 30 s”; „tray can hold up to 8 teeth”), uchwyt z plasteliną, po skanie ręczna płaszczyzna cięcia uchwytu | ≤ 8 | https://www.aidite.com/product/detail/21/AIS_Pro.html ; https://docs.shining3d.com/dentalscan/3.1.2.4/en-us/die-in-one/ ; …/dietray/ | potwierdzone |
| Obszar skanu „Range Scan” (zaznaczenie obszaru myszą) | — | instrukcja 3.1.1; https://docs.shining3d.com/dentalscan/3.1.2.4/en-us/settingscan/ | potwierdzone |
| Użytkownik DS‑MIX: stolik „very quickly moves the scan plate around, and can jostle loose” | — | https://dentallabnetwork.com/forums/threads/shinig3d-scanner.34960/ | pośrednie (forum) |

**Skutek dla planu:** tryb Multidie (założony w `notatki_dokumentacja_skanera.md` i w mailu, pyt. 5/14) obsługuje ≤ 8 prac — płytkę z 24–35 pracami skanuje się jako **model (zlecenie „model/impression”, Range Scan)**, nie jako multi‑die. Pytania 5 i 14 w mailu trzeba przeformułować: „strategia samego obrotu dla skanu modelu/obszaru”. Uwaga z forum o szarpaniu stolika potwierdza kryterium 2 (prace drgają).

## 4. Optyka, widoczność stożków i gniazd

| Fakt | Wartość | Źródło | Pewność |
|---|---|---|---|
| Układ: projektor w środku, dwie kamery po bokach (stereo symetryczne), regulacja osi Z „tilts the camera up and down” | — | https://deltaface.com/shining-3d-ds-ex-metrologic-review/ ; https://docs.shining3d.com/dentalscan/3.1.2.4/en-us/parameters-scan/ | potwierdzone |
| Kąt triangulacji liczbowo | — | — | **BRAK** (typowo 20–30° dla tej klasy — moje założenie do rachunku) |
| Producent dokumentuje skan szczelin międzyzębowych o rozwarciu 7,4–21,4° | — | https://blueskybio.com/caffeine/uploads/files/documents/DS-EX%20PRO%20S.pdf s. 2 | pośrednie |
| Piksel na obiekcie: 5 MP (2592 × 1944) na 100 × 75 mm | ≈ 0,039 mm/px | obliczenie | oszacowanie |
| Wygładzanie w programie obniża rozdzielczość („smoothing reduces the resolution”) | — | deltaface (j.w.) | potwierdzone |
| Dokładność 8 µm: „Shining 3D internal test standard” (nie ISO 12836) | — | https://www.shining3ddental.com/en/solution/autoscan-ds-ex-pro-h | potwierdzone |

Rachunek dla naszych cech (kąt kamery 25° od pionu założony):
- **Stożek ø5 × 3** (ścianka 39,8° od pionu): bliższa ścianka widziana pod ~25°, dalsza pod ~75° (stycznie). Z 4 pozycji obrotu każda ścianka trafia pod dobry kąt. Ø5 = ~128 px, głębokość 3 = 375 × dokładność. Rozdzielczość — bez problemu; ryzyko tylko w polu (§2) i w cieniu sąsiednich prac (`pomiary_stl.md` P‑5).
- **Gniazdo 15° od pionu**, głębokość 4: ścianka gniazda widziana pod 40° / 10° — w porządku; **praca w gnieździe**: zewnętrzna ściana korony poniżej równika jest zasłonięta przez stożek gniazda (to zamierzone — kontrolowany jest brzeg i wnętrze u góry). Korona o średnicy bliskiej wierzchowi gniazda zasłania dno — bez znaczenia.
- **Dołek kodu ø2 × 1** (ścianka pionowa): ~50 px średnicy; dno widoczne na 1,53 mm z kamery 25°; ścianka niewidoczna → w siatce „dziura” z dnem — ryzyko, że „Fill holes” (promień 2/4/6 mm, docs) zamknie dołek. Zalecenie: dołek sferyczny R 1,5 (ø3 × 0,9) lub stożek 90°.
- **Cyrkonia**: zielona (matowa, biała) — nic nie wskazuje na problem; spieczona błyszcząca/przezierna — producent przy błyszczących, półprzeziernych płytach protez zaleca opaker/spray (https://www.shining3ddental.com/application/full-denture-scan-workflow-of-desktop-scanner); tryby HDR / Reduce High Brightness istnieją (broszura). Kryterium 5 planu pozostaje.

## 5. Materiał płytki a skan

| Fakt | Źródło | Pewność |
|---|---|---|
| Spray zalecany tylko dla metalu / silnie odbijających (FAQ DS‑EX Pro H) | https://www.shining3ddental.com/en/solution/autoscan-ds-ex-pro-h | potwierdzone |
| Shining3D ogólnie: „reflective, shiny, transparent **or dark** objects … need a spraying coat” | https://support.shining3d.com/en/support/solutions/articles/60001191284-preparation-for-laser-scanning | potwierdzone |
| Matowa czerń pochłania światło projektora (dłuższa ekspozycja, dziury) | https://www.einstar.com/blogs/news/how-to-3d-scan-dark-and-shiny-objects-with-einstar-3d-scanner ; https://www.insvision3d.com/en/news/industry-articles/when-black-surfaces-break-the-scanner-3d-scanning-reflective-and-dark-parts-without-spray/ | potwierdzone (inni producenci) |
| Błyszczące czarne anodowane Al = najgorszy przypadek; czarne tworzywa matowe skanują się bez sprayu | https://www.matterandform.net/products/three | pośrednie (użytkownik) |
| Jasnoszare matowe żywice modelowe sprzedawane jako „scan without spray” | https://imakr.com/eu/bluecast-resin/4005-bluecast-model-grey-dental-gray-lcddlp ; https://filament2print.com/en/dental-medicine/1991-model-pro-grey-resin.html | potwierdzone (deklaracje producentów) |
| Biały matowy PA12 wprost | — | **BRAK** (pytanie 13) |

Wniosek: **jasno‑/średnioszary mat** jest jedyną klasą powierzchni z dowodami „bez sprayu”. Biały mat (PA12 naturalny) prawie na pewno OK, ale daje zero kontrastu z białą cyrkonią dla oka (nie dla skanera — skaner nie potrzebuje kontrastu płytka/korona, program tnie po geometrii gniazd). Czarny mat: ryzyko średnie; czarny połysk: wykluczony. Płytka nie musi być jednym kolorem: ścianki gniazd/wierzch mogą być szare, a spód/boki ciemne — ale to komplikuje wykonanie.

## 6. Eksport i układ współrzędnych

| Fakt | Źródło | Pewność |
|---|---|---|
| Formaty: STL, OBJ, PLY | aidite.com ; broszura | potwierdzone |
| Eksport w stałym układzie stolika — brak dowodu; eksport wymaga „CAD Type”, jest auto‑obrót szczęki 180°, narzędzie „Coord adjust” | https://docs.shining3d.com/dentalscan/3.1.2.4/en-us/third-party-software/ ; …/coordadjust/ | pośrednie |

Wniosek: program **nie może** polegać na osiach pliku; wyrównanie po stożkach (plan) jest konieczne, a start ICP musi być odporny na dowolny obrót wokół z i przesunięcie (identyfikacja B jako wierzchołka kąta prostego — `pomiary_stl.md` P‑4).

## 7. Cena i dystrybucja (kontekst, nie zakres DESIGN B)

| Fakt | Wartość | Źródło |
|---|---|---|
| A‑IS Pro 3 w PL | brak oferty | — |
| DS‑EX Pro(H) w PL | 34 900–36 000 zł brutto | https://dentalstore.pl/shining-3d-skanner-ds-ex-pro-h.html |
| A‑IS Pro (1,3 MP) w PL | 30 999 zł brutto | https://dentalstore.pl/skaner-a-is-pro-aidite.html |
| DS‑EX Pro(H) DE / USA | 6 999 € / 7 499 USD | https://top3dshop.com/de-de/product/shining3d-autoscan-ds-ex-3d-scanner ; https://www.cad-ray.com/product/shining-3d-autoscan-ds-ex-pro/ |
| Dystrybutor Aidite PL | TAG Dental (ogłoszenie), Dentalstore, Hexdent | https://www.tagdental.pl/baza-wiedzy/blog/tag-dental-oficjalnym-dystrybutorem-aidite/ |

Budżet planu 20–25 tys. zł wygląda nisko wobec 35 tys. zł brutto za odpowiednik w PL (oferta Aidite może być inna — do potwierdzenia).

## 8. Co nadal do potwierdzenia (i gdzie)

1. Pole skanowania A‑IS Pro 3 wprost (kształt bryły, FOV przy stoliku) — mail pyt. 10; test: skan pustej płytki, 3 stożki + 3 dołki kompletne w jednym skanie.
2. Strategia samego obrotu dla skanu **modelu** (nie multi‑die) i jej zapis w zleceniu — mail pyt. 5 (przeformułować), 14.
3. Interfejs stolika (STEP), talerz, obciążenie — pyt. 11–12; potrzebny do adaptera płytki (nowa część, poza płytką).
4. PA12/żywica szara bez sprayu — pyt. 13; test.
5. Kąt triangulacji / wysokość kamer — pyt. nowe (dodać do maila): „kąt między osiami kamer a osią projektora i wysokość kamer nad stolikiem”.
6. Czy „Fill holes” da się wyłączyć globalnie (dołki kodu) — pyt. 17 (już jest).
