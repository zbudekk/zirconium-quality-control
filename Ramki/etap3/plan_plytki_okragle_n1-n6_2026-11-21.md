# Plan paczki "program zna plytki okragle n1-n6" (do decyzji wlasciciela, 21.11.2026)

Status: TYLKO PLAN. Nic nie zmieniono w kodzie ani w `modele_plytek/**`. Galaz `e3/plan-okragle` od `main` bcd0678.
Sciezki bez przedrostka sa wzgledem `Ramki/stanowisko/`; `STAN` = `Ramki/00_NADZOR_STAN.md`, `R58` =
`Ramki/R58_wdrozenie_zmiany.md`, `PLAN` = `Ramki/plan_etap3_pelna_aplikacja_2026-11-16.md`. Odwolania plik:linia
sprawdzone w worktree. Proby z punktu 1.4 wykonano poza repo (`<PC-katalog>\koordynator\robocze\okragle\`), kodem
programu bez zmian; pelnego pytest nie uruchamiano.

## 1. Stan dzisiejszy

### 1.1 Co powstalo w R58 (PR #35, scalony 19.11)

- Decyzje wlasciciela (STAN:267): pelny komplet okragly; numery "n1-n3 W, n4-n6 P" - te same co plytki kwadratowe;
  "okragle zastepuja kwadratowe nowego ukladu, n8 / n9 zostaja testowe do skanera"; pole skanowania o100 niezmierzone.
- Plytka `okragla_ramkowa_<typ>` = okragla R59 z identycznym wierzchem + 3 kieszenie magnesow na promieniu 45
  (225 / 135 / 45 st.) + rowek pokrywki na obwodzie + rowek klucza od spodu (STAN:269). Wymiar 100 x 100 x 8,6 mm
  (8 + relief cyfry 0,6), objetosc 48,91 / 49,20 cm3 (R58:26-32).
- Pliki ukladu w repo: `Ramki/wyniki_v2/json/uklad_gniazd_okragla_ramkowa_wieczorna.json` (sha16 d66ef99b799f37c2)
  i `..._poranna.json` (ab6e02a0a9602216). Porownanie pol (skrypt roboczy, 21.11): `sockets`, `markers`,
  `code_dimples`, `flat`, `d`, `thickness` sa IDENTYCZNE z `modele_plytek/okragla_wieczorna/uklad.json`
  i `modele_plytek/okragla_poranna/uklad.json`; wobec kwadratu (`modele_plytek/wieczorna`, `poranna`) identyczne
  sa `sockets` i `markers`, rozne `code_dimples` i obrys. Nowe pola: `magnet_pockets`, `cover_groove`, `key_slot`.
- Gniazda: wieczorna 19 (1 rynienka 60 x 15, 6 x o12, 12 x o15), poranna 24 (1 rynienka 50 x 13, 20 x o12,5,
  3 x o15). Stozki znacznikow A / B / C: W (-35,5; -26,5) / (-31; 31,5) / (42; 14,5), P (-30,5; -32) / (-37,5; 23,5) /
  (41,5; 16) - jak w R59 (`opisy_modulow/uklad.md:11-12`).
- Kod numeru (R58:318-329): 4 pozycje dolkow o2 x 1 (bit D zawsze 0, dolek D tylko w pliku bazowym); W: A (-4,5; -43,5),
  B (-1,5; -43,5), C (1,5; -43,5); P: A (36,5; 18,5), B (36,5; 21,5), C (43; 6). n1 = A, n2 = B, n3 = A+B, n4 = C,
  n5 = A+C, n6 = B+C. Magnes w kieszeni = ten sam bit; kieszenie na r 45, kwadrat ma je w rogach (+-42; +-42).
- Modele STL (8 sztuk: 6 numerowanych + 2 bazowe) NIE sa w repo (`.gitignore`: `*.stl`, wyjatek tylko
  `Ramki/Ramki_pakiet/**` i `Ramki/stanowisko/modele_plytek/**`); sa na PC w kopii roboczej R58 i w paczce
  zamowienia. Sumy: `Ramki/wyniki_v2/raport/sha256_stl_po_R58.txt:1-8`; 8 z 8 plikow na PC ma sumy zgodne z ta lista
  (sprawdzone 21.11).
- R58 nie dotknal `stanowisko/**` (STAN:272; R58:5).

### 1.2 Dokladne brzmienie otwartego punktu 1 (STAN:273)

"(1) program stanowiska nie zna okraglych n1-n6 (te same numery co kwadratowe; modele `okragla_*` maja `numery` 8 / 9) -
osobna paczka programu: modele `okragla_ramkowa_*`, kalibracja ramki po numerze (gniazda i srodek jak w kwadracie),
ostrzezenie gdy numer nie pasuje do roli ramki (plytka lezaca krzywo na zebrze moze zostac odczytana - czujniki ok.
3,95 mm od magnesu)". To samo w R58:498, R58:503-504 (ryzyka 3, 8, 9) i R58:124 (wymaganie D2 recenzji).

### 1.3 Co program umie dzis

- 8 ukladow wbudowanych: `wieczorna`, `poranna`, `okragla_wieczorna`, `okragla_poranna` i 4 x `*_r54`
  (`stanowisko/ustawienia.py:143-144`; `ustawienia.przyklad.toml:18-31`). Numery z nazw plikow `plytka_n<N>.stl`
  (`stanowisko/uklad.py:295-309`): kwadrat 1-3 / 4-6, okragle tylko 8 / 9. W repo 28 plikow `modele_plytek/**`.
- Okragle n8 / n9 (R57, plytki testowe skanera) sa obslugiwane: `shape = "round"` w ukladzie
  (`stanowisko/uklad.py:149-151`, `:220-242`), mapa ekranu rysuje kolo (`stanowisko/ui/mapa.py:189`, `:273-274`),
  test T2 planu wymaga "ukladow R59 i R54, okraglych" (PLAN:581), `testy/test_auto_uklad.py:20-21` sprawdza 8 ukladow.
- Rozpoznanie (`stanowisko/plate.py:754-864`): rozstaw 3 stozkow wybiera rodzine (W / P, R59 / R54), a kwadrat / kolo
  rozstrzyga kolejno: numer podany ("n1-n6 = kwadrat, n8-n9 = kolo", `plate.py:763-768`), numer z dolkow, ksztalt
  brzegu (`plate.py:737-751`, prog 40 mm2 w `plate.py:79`), wykluczenie po dolkach, wybor domyslny z `pewny = False`.
  Kandydaci = wszystkie uklady z `[plytki]` (`stanowisko/porownaj.py:144-153`).
- Liczba gniazd (19 / 24) nie jest zaszyta w kodzie - pochodzi z `uklad.json` (`stanowisko/uklad.py:330-345`).
- Zalozenia "kwadrat = ramka, kolo = poza ramka" zaszyte w programie:
  - nazwa ukladu: wzor `^(okragla_)?(wieczorna|poranna)(_r\d+)?$` (`stanowisko/session.py:128`); nazwa spoza wzoru =
    "nieznany uklad plytki" i blokada skanu (`session.py:160-170`, uzycie `session.py:369`);
  - poranek: numery okraglych = (9,) (`stanowisko/session_rano.py:85`, `:107-112`); `na_ramce` = tylko kwadrat, z
    uzasadnieniem "okragle nie pasuja do wkladki - R58" (`session_rano.py:115-118`) - nieaktualnym od R58;
  - kalibracja diod: tylko `plate` = wieczorna / poranna i `shape = square` (`ramka/kalibracja.py:33`, `:67-75`;
    `ramka/README.md:386-387`);
  - ramka wieczorna: wynik z ukladem bez kalibracji = "brak_kalibracji", ramka ciemna
    (`stanowisko/indicate.py:502-507`; `opisy_modulow/indicate.md:99`; test `testy/test_indicate.py:832`);
  - rodziny numerow ramek W (1, 2, 3) / P (4, 5, 6) (`ramka/protokol.py:41`) - pasuja do R58 bez zmian.
- Baza: `skany.uklad TEXT`, `skany.numer_plytki INTEGER`, `WERSJA_SCHEMATU = 1` (`stanowisko/baza.py:144`, `:147`,
  `:217`) - nazwa ukladu to dowolny tekst.

### 1.4 Proby 21.11 (13 skanow syntetycznych, po 1 na przypadek, pole o100, kod bez zmian)

Katalogi probne poza repo: JSON R58 + 6 STL numerowanych + 2 bazowe (9,2 MB). `uklad.wczytaj` wczytuje je bez zmian
kodu: numery [1, 2, 3] i [4, 5, 6]. Log: `robocze\okragle\proba_2.log`.

| Przypadek | Kandydaci | Wynik |
|---|---|---|
| ramkowa n1, n2 (numer podany), n3, n4, n6 (numer podany) | 8 + 2 nowe | 5 z 5: uklad `okragla_ramkowa_*`, `pewny`, powod `numer_z_dolkow`, gniazda zgodne z prawda |
| kwadrat n1 i n4 z numerem podanym, n1 bez numeru | 8 + 2 nowe | 3 z 3: uklad dobry i `pewny`, powod `ksztalt` (z numerem podanym dzis jest `numer_podany`) |
| okragla testowa n8, n9 | 8 + 2 nowe | 2 z 2: jak dzis (`numer_z_dolkow`) |
| kwadrat n1 z numerem podanym | 8 (dzis) | 1 z 1: `numer_podany` (punkt odniesienia) |
| ramkowa n1 bez numeru | 8 (dzis) | ZLE: `okragla_wieczorna`, `pewny = True`, numer 1 spoza numerow tego ukladu |
| ramkowa n4 z numerem 4 | 8 (dzis) | ZLE: `poranna` (kwadrat), `pewny = False` |

Wniosek: dzisiejszy program przyjmie skan plytki okraglej ramkowej, ale pod zla nazwa ukladu (gniazda wyjda dobrze,
bo sa te same). Samo dolozenie 2 katalogow modeli wystarcza funkcji `rozpoznaj_uklad` bez zmiany `plate.py`
(10 z 10 prob z 10 ukladami dobrze), przy zmianie sciezki decyzji dla kwadratow z numerem podanym.

## 2. Luka (kazdy brak z dowodem)

| Nr | Brak | Dowod |
|---|---|---|
| L1 | Modele gniazd: brak `modele_plytek/okragla_ramkowa_wieczorna` i `..._poranna` (uklad.json + 3 STL + bazowy) | brak katalogow; STL poza repo (1.1) |
| L2 | Lista ukladow: nowych nazw nie ma w ukladach wbudowanych ani we wzorze ustawien | `stanowisko/ustawienia.py:143-144`; `ustawienia.przyklad.toml:18-31` |
| L3 | Rozpoznanie: dzis zla nazwa ukladu (2 z 2 prob); regula "n1-n6 = kwadrat" nieprawdziwa po R58 | 1.4; `stanowisko/plate.py:763-768` |
| L4 | Numer plytki: okragla n1-n6 ma dolki w polu skanu, kwadrat nie - brak testu, ze numer podany (z ramki) i numer z dolkow sa zgodne | `plate.py:661-668` (tylko ostrzezenie w logu) |
| L5 | Wyrownanie i ciecie: brak pomiaru na zestawie (dzis 5 skanow probnych); rowek pokrywki lezy w pasie oceny ksztaltu (405 mm2 roznicy miedzy modelem n8 a ramkowa w probie) | 1.4; `plate.py:75-79`, `:737-751` |
| L6 | Sesja wieczorna: nazwa `okragla_ramkowa_*` = "nieznany uklad plytki", skan zablokowany; rodzina do ponownego skanu nie zna nazwy | `stanowisko/session.py:128`, `:141-144`, `:160-170`, `:369` |
| L7 | Sesja poranna: okragle maja numer tylko 9 i nie ida do planu ramki; blokady "Zamknij piec" licza tylko kwadraty | `stanowisko/session_rano.py:85`, `:107-118`, `:833-836`, `:1295-1300` |
| L8 | Ramka: brak kalibracji startowej dla ukladow okraglych, wiec plan pomija plytke (`brak_kalibracji`) rano i wieczorem; lokalny plik kalibracji na laptopie nie dostanie nowych ukladow sam | `ramka/kalibracja.py:33`, `:67-75`; `stanowisko/ramka_protokol.py:141-145`; `stanowisko/indicate.py:505-507` |
| L9 | Ostrzezenie "numer nie pasuje do roli ramki" (wymaganie R58:124): wynik `zla_plytka` / `brak_kalibracji` nie trafia na ekran - kontroler sprawdza tylko "niewazny" | `stanowisko/kontroler_api.py:2596-2597`; 0 trafien `zla_plytka` w `kontroler_api.py`, `aplikacja.py`, `ui/*.py` |
| L10 | Mapa ekranu wieczornego i porannego: kolo rysowane bez sciecia orientacyjnego; opis ukladu nie odroznia okraglej testowej od ramkowej | `stanowisko/ui/mapa.py:273-274`; `stanowisko/porownaj.py:157-163` |
| L11 | Baza: bez braku w schemacie (`uklad TEXT`); nowa wartosc w `skany.uklad` - metryki i raporty grupujace po nazwie nie byly sprawdzane | `stanowisko/baza.py:144`, `:217` |
| L12 | Symulator i dane testowe: 0 skanow plytek ramkowych w danych odniesienia na PC (80 skanow syntetycznych: po 12 okraglych n8 / n9 i po 8 kwadratowych na uklad, 8 ukladow; w 12 zestawach wynikow 0 wpisow `okragla_ramkowa`); testy znaja 8 ukladow | `testy/test_auto_uklad.py:20-21`; liczenie 21.11 |
| L13 | Instrukcje technika: 0 wzmianek o ksztalcie plytki w `instrukcje/*` i `Ramki/etap3/t14/*` - do sprawdzenia, czy obrazki pokazuja kwadrat | wyszukanie "okragl" / "kwadrat": 0 trafien |
| L14 | Samokontrola: sprawdza uklady z `[plytki]`, wiec nowe sprawdzi sama; brak testu na 10 ukladow | `stanowisko/samokontrola.py:837-873`; `testy/test_samokontrola.py:1142` |
| L15 | Paczka wydania: `modele_plytek` idzie do ZIP w calosci, ale wydanie 0.3.0 nie ma nowych modeli | `narzedzia/zbuduj_wydanie.py:33`; `Ramki/etap3/wydania/` |
| L16 | Opisy modulow mowia "okragle poza ramka" i znaja 8 ukladow | `opisy_modulow/session.md:113`, `:135`, `:138`; `opisy_modulow/uklad.md:7-14` |

## 3. Warianty wykonania

**Wariant A - nowe uklady jako dane + dopiecia w programie (zalecany).** Dwa nowe katalogi w `modele_plytek/`
(bajtowe kopie plikow R58), nowe nazwy `okragla_ramkowa_wieczorna` / `okragla_ramkowa_poranna`; zmiany w ustawieniach,
sesji, kalibracji ramki, kontrolerze, mapie, opisach.
- Pliki nietykalne: `match.py`, `inspect.py`, `plate.py`, `synth.py`, `uklad.py`, progi `[match]` / `[inspect]` - BEZ
  ZMIAN. `modele_plytek/**`: 28 istniejacych plikow bez zmian, ale dochodzi 10 nowych (2 JSON + 8 STL) - to jest
  wejscie w strefe nietykalna i WYMAGA OSOBNEJ ZGODY WLASCICIELA (decyzja 1). Unikniecie: modele w innym katalogu
  (np. `modele_r58/`) wymaga wyjatku w `.gitignore` i zmiany `zbuduj_wydanie.py` - gorsze, niezalecane.
- Schemat bazy: bez zmiany (nowa wartosc tekstowa w `skany.uklad`).
- Ryzyko dla R59 / R54 (T10 / T11): w rodzinie R59 sa 3 kandydaci zamiast 2; kwadrat z numerem podanym przechodzi
  z reguly `numer_podany` na `ksztalt` (3 z 3 prob dobrze). Gdy skan nie obejmuje brzegu plytki, zostaje regula
  "dolki wykluczaja" albo wybor domyslny z `pewny = False` - nie zmierzone. Uklady `*_r54` bez zmian (inne stozki).
- Pracochlonnosc: 3 paczki (S + M + S), 1 fala rownolegla po pierwszej.

**Wariant B - bez nowych nazw: numery 1-6 dopisane do istniejacych `okragla_wieczorna` / `okragla_poranna`.**
6 plikow STL R58 dolozone do dwoch istniejacych katalogow; nazwa ukladu zostaje, sesja nie wymaga zmiany wzoru.
- Pliki nietykalne: ZMIANA zawartosci istniejacych katalogow `modele_plytek/okragla_*` (zgoda wlasciciela); `numery`
  ukladu zmieniaja sie z [8] na [1, 2, 3, 8] - padaja testy zakladajace 8 / 9; plytka testowa i ramkowa (inny spod,
  rowek) pod jedna nazwa; "na ramce" trzeba liczyc z numeru zamiast z nazwy.
- Schemat bazy: bez zmiany. Ryzyko dla R59 / R54: jak w A plus zmiana znaczenia istniejacej nazwy w danych
  odniesienia (48 z 80 skanow odniesienia to `okragla_*`). Pracochlonnosc: 2 paczki. Niezalecany.

**Wariant C - A + jawna regula w `plate.py` (i ewentualnie pola R58 w `uklad.py`).** `rozpoznaj_uklad` dostaje
regule "numer podany + ksztalt" i powod zrozumialy dla czlowieka; `uklad.py` wczytuje `magnet_pockets` / `key_slot`.
- Pliki nietykalne: ZMIANA `plate.py` (i `uklad.py`) - WYMAGA OSOBNEJ ZGODY WLASCICIELA oraz pelnej regresji straznika
  i rozpoznania (80 skanow odniesienia, zestawy T10 / T11). Schemat bazy: bez zmiany.
- Ryzyko dla R59 / R54: najwyzsze z trzech. Pracochlonnosc: 4 paczki. Siegnac tylko wtedy, gdy pomiar w paczce O1
  pokaze wynik gorszy niz kryterium (4, O1).

## 4. Wariant zalecany (A) - 3 paczki o rozlacznych listach plikow

**E3-O1 - modele i rozpoznanie (S).** Cel: program wczytuje i rozpoznaje plytki okragle n1-n6 bez pogorszenia R59 / R54.
- Pliki: nowe `modele_plytek/okragla_ramkowa_wieczorna/{uklad.json, plytka_n1.stl, plytka_n2.stl, plytka_n3.stl,
  plytka_bazowa.stl}`, `modele_plytek/okragla_ramkowa_poranna/{uklad.json, plytka_n4..n6.stl, plytka_bazowa.stl}`;
  zmieniane `stanowisko/ustawienia.py`, `ustawienia.przyklad.toml`, `testy/test_ustawienia.py`; nowe
  `testy/test_uklad_r58.py`, `testy/test_auto_uklad_r58.py`, `narzedzia/auto_uklad_r58.py`; opisy
  `opisy_modulow/uklad.md`, `opisy_modulow/plate.md` (tylko tekst).
- Testy przed kodem: (a) sumy SHA-256 10 nowych plikow = lista R58 (pada: brak plikow); (b) `uklad.wczytaj` daje
  numery [1, 2, 3] / [4, 5, 6], 19 / 24 gniazda, `sockets` = kwadrat i okragla testowa; (c) 28 dotychczasowych plikow
  `modele_plytek/**` bajtowo bez zmian; (d) rozpoznanie na 10 ukladach.
- Kryteria: (1) 10 z 10 sum zgodnych; (2) 48 skanow syntetycznych ramkowych (6 numerow x 4 ziarna x bez numeru /
  z numerem): 48 z 48 uklad dobry i `pewny`, gniazda prac = prawda; (3) 80 z 80 skanow odniesienia: ten sam uklad
  i nie gorsza pewnosc niz przy 8 ukladach, lista zmian `powod` w raporcie; (4) 0 przypadkow "pewny ze zlym
  ukladem" takze przy polu skanu 90 i 80 mm (liczba niepewnych podana wprost); (5) zestaw T10 (40 skanow R59):
  wyrownanie 40 z 40; (6) czas rozpoznania plytki R59 nie rosnie o wiecej niz 1,0 s (mediana z 10); (7) pytest
  0 failed, passed nie mniej niz punkt odniesienia + nowe.
- Ryzyka: kryterium (3) albo (4) niespelnione = stop i decyzja o wariancie C; rowek pokrywki jako cecha ksztaltu
  dziala w syntetyku, na prawdziwym skanie niepewne.

**E3-O2 - sesja i ramki (M).** Cel: skan plytki okraglej ramkowej jest przyjmowany wieczorem i rano, idzie do planu
ramki, a zly numer wobec roli ramki daje widoczne ostrzezenie.
- Pliki: `stanowisko/session.py`, `stanowisko/session_rano.py`, `ramka/kalibracja.py`, `stanowisko/ramka_protokol.py`,
  `stanowisko/indicate.py`, `stanowisko/kontroler_api.py`, `stanowisko/statusy.py` (plik wspolny - tylko ta paczka
  w fali); nowe `testy/test_okragle_sesja.py`, `testy/test_okragle_ramka.py`; opisy `session.md`, `indicate.md`,
  `ramka/README.md`.
- Umowy: `czesci_ukladu` zwraca dodatkowo `ramkowa` (bool); rodzina ukladu ramkowego = rodzina kwadratu R59
  (ten sam rozstaw i gniazda); `na_ramce` = kwadrat albo okragla ramkowa; numery okraglej ramkowej porannej
  (4, 5, 6); kalibracja startowa ukladu ramkowego = geometria jego `uklad.json` (te same gniazda i srodek co
  kwadrat - R58:504), `zrodlo = "geometria"`; brakujace uklady dopisywane do lokalnego pliku kalibracji przy starcie
  bez ruszania wpisow `zrodlo = "kalibracja"`.
- Testy przed kodem: wynik z `plytka = okragla_ramkowa_wieczorna` dzis daje blokade "nieznany uklad" (pada);
  `plan_plytek` z okragla n4 dzis ma ja w `pominiete.poza_ramka` (pada); `wynik(2, "okragla_ramkowa_wieczorna", ...)`
  dzis = `brak_kalibracji` (pada).
- Kryteria: (1) wieczor: 3 skany n1-n3 przyjete, status `przyjety`, 0 blokad trybu; (2) rano: 3 plytki n4-n6
  w planie ramki, 24 z 24 gniazd z blokiem pikseli, bloki = bloki kwadratu `poranna` (72 z 72 porownan);
  (3) okragla testowa n8 / n9 zachowuje sie jak dzis (testy istniejace bez zmian: 0 zmienionych asercji);
  (4) numer z ramki rozny od numeru z dolkow albo numer spoza roli ramki (n4-n6 na W, n1-n3 na P): komunikat na
  ekranie w 6 z 6 przypadkow, ramka ciemna, skan nie przepada; (5) ponowny skan: okragla ramkowa nie zastepuje skanu
  kwadratu o tym samym numerze bez pytania; (6) stary plik kalibracji (tylko kwadraty) po starcie ma 2 nowe uklady,
  wpisy skalibrowane bez zmian; (7) pytest 0 failed.
- Ryzyka: PR #44 i #45 sa otwarte (STAN:285), listy ich plikow nie sprawdzano - start po ich scaleniu; `statusy.py`
  to plik wspolny (PLAN:634).

**E3-O3 - ekran, symulator, samokontrola, wydanie (S).** Cel: technik widzi plytke okragla z orientacja, zestawy
probne i paczka wydania zawieraja nowe uklady.
- Pliki: `stanowisko/ui/mapa.py`, `stanowisko/porownaj.py` (tylko `opis_ukladu`), `stanowisko/samokontrola.py`,
  `narzedzia/symulator_skanera.py` i scenariusze, `instrukcje/*.md` (gdy obrazki pokazuja kwadrat),
  `Ramki/etap3/wydania/**`; nowe `testy/test_okragle_ekran.py`; opisy `ui_wieczor.md`, `ui_rano.md`,
  `samokontrola.md`, `instalacja.md`.
- Kryteria: (1) mapa okragla ma sciecie po stronie przod-prawo (zrzut 1920 x 1080 i 1536 x 864), klik w 19 z 19
  i 24 z 24 gniazd trafia w dobre gniazdo; (2) samokontrola: "uklady plytek: poprawne 10 z 10"; (3) paczka
  wydania zawiera 38 plikow `modele_plytek/**`, instalacja probna zielona; (4) T2 powtorzony z 2 plytkami
  ramkowymi w zestawie 10 plytek: 10 z 10 zgodnie z prawda; (5) pytest 0 failed.

**Dane do testow.** Skanow plytek okraglych n1-n6 nie ma (L12). O1-O3 pracuja na skanach syntetyzowanych przez
`synth.generuj_plytke` z nowym ukladem (`synth.py` bez zmian - 5 roznych skanow probnych powstalo 21.11). Prawdziwe skany:
po wydruku plytek R58 i uruchomieniu skanera - osobny krok odbioru (T16), nie warunek startu.

**Kolejnosc.** O1 sam (bramka: kryteria 3 i 4). Po scaleniu O1: O2 i O3 rownolegle (pliki rozlaczne). Na koniec
pelny pytest, T2 / T10 / T11 i nowe wydanie. Wspolne zasady paczek: PLAN sekcja 9 (PLAN:625-640).

## 5. Decyzje potrzebne od wlasciciela i warunki startu

| Nr | Decyzja | Zalecenie | Skutek braku decyzji |
|---|---|---|---|
| 1 | Zgoda na 10 nowych plikow w `modele_plytek/**` (strefa nietykalna; istniejace 28 bez zmian) | TAK | paczki nie startuja |
| 2 | Wariant A / B / C | A; C tylko po nieudanym pomiarze w O1 | przyjmuje sie A |
| 3 | Nazwy ukladow `okragla_ramkowa_wieczorna` / `okragla_ramkowa_poranna` (jak pole `plate` w JSON R58), widoczne w bazie i metrykach | TAK | przyjmuje sie te nazwy |
| 4 | Czy kwadratowe n1-n6 (R59 i R54) i okragle n1-n6 moga byc w obiegu jednoczesnie | TAK - program rozroznia ze skanu; ramka ich nie odroznia | przyjmuje sie TAK (stare plytki R54 sa w uzyciu) |
| 5 | Reakcja na numer niezgodny z rola ramki albo z dolkami | komunikat na ekranie + ramka ciemna, skan przyjety, bez twardej blokady | zostaje jak dzis: ramka ciemna bez komunikatu |
| 6 | Kalibracja ramki dla okraglych: start z geometrii, kalibracja na sprzecie (C2) obowiazkowa przed praca | TAK | plytki okragle bez swiatel na ramce |
| 7 | Plytki testowe n8 / n9 zostaja w programie bez zmian | TAK | zostaja |
| 8 | Termin: przed czy po wydaniu 0.3.1 i testach T0-T13 | PO (osobne wydanie 0.3.2; koniec etapu 3 nie czeka) | po T0-T13 |
| 9 | Rysowanie sciecia orientacyjnego na mapie (drobna zmiana ekranu) | TAK | mapa zostaje kolem bez sciecia |

Warunki startu: (a) decyzja 1; (b) scalone PR #44 i #45 oraz zbudowane wydanie 0.3.1 (mozliwa kolizja
plikow - nie sprawdzano); (c) 8 plikow STL R58 dostepnych na PC z sumami z listy R58 (dzis: 8 z 8 zgodnych); (d) do O1-O3 NIE sa potrzebne: wydruk plytek, skaner, ramka.
Do odbioru na sprzecie potrzebne: wydrukowane plytki i wkladka okragla, zlozona ramka, skaner.

## 6. Czego NIE ustalono

1. Pole prawdziwego skanera (o100 niezmierzone - STAN:273 p. 4) i to, czy skaner widzi dolki o2 x 1 lezace na
   promieniu ok. 43,5 mm oraz scianke boczna z rowkiem pokrywki. Od tego zalezy, ktora regula rozpoznania zadziala.
2. Proby 21.11 to 13 skanow, po 1 ziarnie na przypadek, tylko syntetyczne, tylko pole o100 - to nie jest pomiar.
3. Zachowanie przy polu mniejszym niz plytka i przy plytce z pracami zaslaniajacymi dolki - nie mierzone.
4. Czy numer odczytany przez ramke wieczorna trafia do analizy jako numer podany - nie przesledzone w kodzie
   (`stanowisko/aplikacja.py:1301` przekazuje `numer` ze zdarzenia; zrodla tej wartosci nie sprawdzono).
5. Czy komplet R58 zostal zamowiony albo wydrukowany - w repo jest tylko paczka zamowienia (STAN:271).
6. Odczyt magnesow plytki lezacej krzywo na zebrze (ok. 3,95 mm od czujnika) - nie liczony ani nie mierzony (R58:124).
7. Polozenie diod pod wkladka okragla na sprzecie; rownosc srodkow wkladek zmierzono tylko na siatkach (R58:504).
8. Wplyw nowej nazwy ukladu na `metryki.py` i raporty - nie sprawdzane.
9. Sklad zestawu symulatora T2 i obrazki instrukcji - nie przegladane plik po pliku.
10. Pelny pytest na galezi - nie uruchamiany (plan nie zmienia kodu); listy plikow PR #44 i #45 - nie sprawdzane.
