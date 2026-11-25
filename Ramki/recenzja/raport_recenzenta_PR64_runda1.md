# Raport recenzenta - PR #64 (E3-U1b: tryb poranny i panel Excela w nowym oknie), runda 1

Data: 25.11.2026. Recenzent: konto 3 (zlecenie rec-u1b-r1).
Zakres: `git diff origin/e3/u1-okno...origin/e3/u1b`, baza `e57fabe` (galaz U1a), HEAD `233ed1b`; 29 plikow, +2094 / -887
(w tym 8 PNG). Kod U1a (okno wieczorne, motyw, czesci wspolne) nie byl oceniany ponownie - tylko to, co U1b w nim zmienia.
Miara: `konto3\zlecenia\u1b.md`, `Ramki/etap3/nowy_interfejs/SPEC.md`, makieta `Rano.dc.html`, znalezisko S3-16.

Metoda: (1) caly diff przeczytany (nowy `ui/ekran_rano.py` w calosci, stary z bazy w calosci dla porownania funkcji; `kandydaci.py`,
`okno_excela.py`, `okno.py`, `czesci.py`, `motyw.py`, `mapa*.py`, `napisy*.py`, testy, narzedzia); (2) testy paczki we wlasnej
kopii `<PC-katalog>\qc-wt\rec-u1b` (detached `233ed1b`); (3) wlasne proby celowane na atrapie kontrolera (skrypty w
`<PC-katalog>\konto3\robocze\rec-u1b-r1\proby\`, wyniki `proby_wynik.txt`); (4) 20 wstrzykniec bledu w kopii
(`wstrzykniecia.ps1`, wyniki `wstrzykniecia_wynik.txt`); (5) pomiar porownawczy na bazie `e57fabe`; (6) raport wykonawcy
i `KONIEC_u1b.txt` przeczytane na koncu. Pelny pytest nie byl powtarzany. Okno NIE bylo ogladane na prawdziwym ekranie
(Qt offscreen) - jak u wykonawcy. Po probach kopia czysta (`git status --short` pusty, HEAD `233ed1b`).

## 0. Werdykt

**Do scalenia po poprawkach.** B 0 / P 4 / D 4.

Nie znalazlem bledu, ktory pokazuje technikowi zla kuwete albo zly stan z danych: przy 33 kuwetach x 3 rozmiary okna duzy
numer, liczba prac, gniazda w napisie, obwodki na mapach i wiersz "teraz" listy zgadzaly sie ze stanem kontrolera
(0 niezgodnosci na 99 sprawdzen). Uwagi P dotycza: klikniecia w liste kuwet, ktora przesunela sie w tle (S3-16 nie jest
zamkniete w calosci), przycisku "Excel: wskaz wiersz", ktory w nowym ukladzie bywa martwy, jednakowej barwy dwoch roznych
obwodek gniazda na mapie porannej oraz trzech luk w testach.

## 1. Uwagi

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| 1 | P | `ui/ekran_rano.py:625-626`, `637-640`, `647-652` | S3-16, lista kuwet. Ochrona 800 ms wlacza sie tylko, gdy w tle zmienila sie KOLEJNOSC kuwet. Gdy w tle zmienia sie biezaca kuweta ("Rozlozona" z ramki porannej albo z drugiego stanowiska - `atrapa.potwierdz_kuwete` poza oknem), lista przewija sie do niej (`scrollToItem`) i pod nieruchomym kursorem staje inna kuweta - bez ochrony. Pomiar (33 kuwety, 33 x "Rozlozona" z tla): kuweta pod stalym punktem listy zmienila sie 8 razy przy 1920x1001 (samo przewijanie), 13 razy przy 1536x784 i 19 razy przy 1280x642 (w tym po 1 razie skok wysokosci wiersza - uwaga 6); klikniecie zaraz po zmianie przy 1920x1001 (krok 24, kolejnosc listy bez zmian): pod punktem bylo 3298, po zmianie 3305, ochrona nieaktywna, okno wyslalo `wybierz_kuwete 3305` i pokazalo "Teraz rozkladasz 3305" (pomylka o jedna pozycje). Test `test_s3_16_lista_kuwet_*` sprawdza tylko zmiane kolejnosci. Stary kod przewijal liste po kazdej zmianie (`PositionAtTop`), wiec jest lepiej niz bylo, ale znalezisko ("po nowym stanie wiersz pod kursorem moze byc inna kuweta") zostaje otwarte dla przewijania. | Ochrona takze wtedy, gdy stan z tla zmienil kuwete w ktorymkolwiek widocznym wierszu (porownac przed / po: wiersz pod kazda pozycja ekranu albo `verticalScrollBar().value()` i wysokosc wiersza), albo nie przewijac listy przy zmianie z tla. Test: "Rozlozona" z tla przy liscie dluzszej niz pole -> klikniecie w ciagu 800 ms pominiete. |
| 2 | P | `ui/ekran_rano.py:757-761`, `1053-1060` | Panel Excela. Po "Zamknij piec" (tryb "pytaj") zakladka "Excel" otwiera sie sama. Technik przechodzi na "Kompletne i braki" (lista kompletnych), klika widoczny, aktywny przycisk "Excel: wskaz wiersz": okno wysyla `excel_pokaz(1)`, stan dostaje nowa wersje, ale zakladka zostaje "Kompletne i braki" - nic sie nie dzieje (proba B: `strona='wynik'`, panel Excela niewidoczny, bez odmowy). Powod: `pokaz()` przelacza na "Excel" tylko, gdy `excel.widoczne` zmienia sie z False na True albo zmienia sie piec. W starym ukladzie panel Excela i wynik byly widoczne obok siebie, wiec przycisk nie mial czego otwierac; teraz jest to funkcja, ktora w tym stanie zginela (obejscie: zakladka "Excel"). Raport p. 9 ("otwiera sie sama ... po Excel: wskaz wiersz") w tym przypadku nie jest prawda. | Po udanym `excel_pokaz` wyslanym z ekranu (przycisk wyniku, zalegly piec) ustawic zakladke "Excel" bez wzgledu na poprzednia wartosc `widoczne`. Test: zakladka "Kompletne i braki" przy widocznym oknie Excela -> klik "Excel: wskaz wiersz" -> `strona() == "excel"`. |
| 3 | P | `ui/mapa_rano.py:22`, `151-156`; `ui/mapa.py:346-349`; `ui/napisy_rano.py` (`NA_RAMCE`, usuniety `KUWETY_PODPOWIEDZ`) | Mapa poranna, wg ktorej technik rozklada. Gniazda biezacej kuwety maja obwodke w kolorze akcentu (`KOLOR_BIEZACEJ = motyw.AKCENT`), a gniazdo WYBRANE kliknieciem - pierscien w tym samym kolorze akcentu (mapa z U1a). Na zrzucie wykonawcy `rano_kandydaci_1536x864.png`: "Teraz rozkladasz 3221 - Plytka 4 - gniazda 1 i 2", a na plytce 4 niebieska obwodke maja TRZY sasiednie gniazda: 1 i 2 (kuweta 3221) oraz 3 (otwarta praca "wybierz", ktorej jeden z kandydatow to wlasnie 3221). Roznia sie tylko tym, ze pierscien wybranego stoi 3 px od gniazda (wycinek powiekszony: `robocze\rec-u1b-r1\wycinek_pierscienie.png`). W `main` oznaczenia mialy rozne barwy (wybrane: bialo-ciemne, kuweta: bialo-niebieskie). Do tego z ekranu zniknal napis "Gniazda biezacej kuwety sa obwiedzione na plytkach" - nowy napis mowi tylko o ramce; legenda "Na plytkach" obwodki nie objasnia. Zderzenie barw powstalo juz na bazie U1a (stary uklad poranny w barwach motywu), ale to U1b oddaje wyglad poranka i wlasny zrzut to pokazuje. Skutek: praca z gniazda otwartego do obejrzenia moze trafic do biezacej kuwety. | Rozne oznaczenia w trybie porannym (np. wybrane gniazdo: pierscien bialy albo przerywany; kuweta: akcent) + pozycja legendy albo napis "obwodka = biezaca kuweta". Test: barwa / styl pierscienia wybranego gniazda rozne od obwodki kuwety (odczyt pikseli jak `test_ui_rano.Ekran.piksele`). |
| 4 | P | `ui/ekran_rano.py:136-145` i `445-449`; `ui/kandydaci.py:272`; `ui/ekran_rano.py:452` | Luki w testach (zlecenie p. 5: "kazda akcja"). Trzy z 20 wstrzykniec nie zostaly wykryte przez `test_ui_poranek.py` + `test_ui_rano.py` + `test_p14_ekran.py` (85 passed): (a) E7 - napis "Plytka 4 - gniazda 2 i 9" pokazuje tylko PIERWSZE gniazdo biezacej kuwety (nowy napis, wg ktorego technik bierze prace z plytki - zaden test go nie czyta); (b) K2 - "To ten projekt" DRUGIEGO kandydata zapisuje pierwszego (testy klikaja tylko `kandydat_1_wybierz`; uklad kart kandydatow jest w U1b nowy); (c) E18 - "Rozlozona" aktywne bez wybranej osoby (kontroler i tak odmawia - najslabsza z trzech). Kod jest dzis poprawny (proba C: 0 niezgodnosci), ale nic go nie pilnuje. | (a) test: dla kuwety na 2 plytkach `rano_kuweta_miejsca` == gniazda z `KuwetaRano.gniazda` (takze `rano_kuweta_miejsca_krotko` w ukladzie zwartym); (b) test: klik `kandydat_2_wybierz` -> `wybierz_kandydata(praca_id, sha drugiego)` i projekt pracy = projekt drugiego kandydata; (c) test: bez osoby `rano_potwierdz_kuwete` i `rano_cofnij_kuwete` nieaktywne. |
| 5 | D | `ui/ekran_rano.py:348`, `447-449` | Okno 1280x642 (1920x1080 przy 150 %): gniazda biezacej kuwety sa w jednym wierszu skracanym wielokropkiem. 2 z 33 kuwet scenariusza (kuweta na 2 plytkach z dwucyfrowym gniazdem): "Plytka 4 - gniazdo 23; Plytka 5 - gniaz..." - numer gniazda na drugiej plytce nieczytelny (pelny tekst tylko w podpowiedzi; obwodki na mapach sa). Kuweta na 3 plytkach nie zmiesci sie nigdy. SPEC p. 1: "nic ucietego"; test 6 rozmiarow sprawdza tylko pierwsza kuwete. Przy 1536x784 i 1920x1001: 0 z 33. | Krotszy zapis w ukladzie zwartym (np. "pl. 4: 23 - pl. 5: 1") albo dwa wiersze; test po wszystkich kuwetach scenariusza. |
| 6 | D | `ui/ekran_rano.py:102-103`; `ui/okno_excela.py:50-51` | Uklad zwarty (1536x784, 1280x642): po otwarciu okna / zmianie rozmiaru wiersze tabel maja 30 px zamiast 26 (pomiar: wysokosc 30, domyslna 30, minimalna 26); przy pierwszej zmianie stanu kuwet skacza na 26 px i dalsze wiersze listy przesuwaja sie pod kursorem (np. punkt w polowie listy: wiersz 9 -> 10 przy 1536x784, 6 -> 7 przy 1280x642). Powod: `setDefaultSectionSize(26)` jest wolane przed `setMinimumSectionSize(26)`, gdy minimum wynosi jeszcze 30 z ukladu wysokiego - Qt przycina 26 do 30. | Odwrocic kolejnosc dwoch wywolan (najpierw minimum, potem domyslna) w obu funkcjach. |
| 7 | D | `ui/ekran_rano.py:523-535` | Piec z 5-6 plytkami w oknie 1280x642: `_najlepsze_kolumny` uklada wszystkie mapy w jednym wierszu bez sprawdzenia minimalnej szerokosci mapy. 5 plytek: 5 usterek `sprawdz_uklad` (skrocone tytuly kart "Plytka 1"), promien gniazda 7,8 px; 6 plytek: 13 usterek, "uklad potrzebuje 1368x618" (okno 1280). 3 i 4 plytki: 0 usterek we wszystkich 3 rozmiarach; 5 plytek przy 1536x784 i 1920x1001: 0 usterek. | Liczbe kolumn ograniczyc tak, zeby szerokosc mapy nie spadla ponizej `Uklad.mapa_rano_min` (wtedy drugi wiersz albo przewijanie pionowe). Patrz p. 5 pkt 3. |
| 8 | D | `ui/ekran_rano.py:435-437`, `633-634` | Kuweta juz rozlozona, wybrana ponownie numerem (proba I: 3221 po "Rozlozona", potem cyfry + Enter): ekran pisze "Teraz rozkladasz 3221, kuweta - 3 prace", lista pokazuje "teraz" (nie "rozlozona"), "Rozlozona" jest aktywne - nigdzie nie widac, ze ta kuweta jest juz rozlozona; drugi Enter zapisze drugie potwierdzenie. Regula listy jest taka sama jak w starym oknie (nie regresja), ale nowy naglowek "Teraz rozkladasz" wzmacnia mylny obraz. | W wierszu kuwety i na liscie dopisek "juz rozlozona" (stan: `KuwetaRano.potwierdzona` i `biezaca` naraz). |

Nie zglaszam (znane wg zlecenia): `ramka/logika.py` (S3-16 po stronie ramki), instrukcje i `opisy_modulow/ui_rano.md`,
brak proby na prawdziwym ekranie, narzedzia odbioru T2 / T3.

## 2. Wlasne proby

Kopia `<PC-katalog>\qc-wt\rec-u1b`, katalog `Ramki\stanowisko`, `<PC-katalog>\koordynator\narz\py.cmd`, 1 proces python.

| Proba | Polecenie | Wynik |
|---|---|---|
| testy nowego trybu | `py.cmd -m pytest -q -p no:cacheprovider testy\test_ui_poranek.py` | 20 passed, 0 failed (30 s) |
| pozostale testy okna paczki | to samo dla `test_ui_rano.py test_p14_ekran.py test_ui_motyw.py test_ui_wieczor.py test_instrukcje.py test_aplikacja_rano.py` (tor 1) | 245 passed, 0 failed (247 s) |
| skala 150 % | `set QT_SCALE_FACTOR=1.5` + `test_ui_poranek.py` | 20 passed, 0 failed |
| pelny pytest (nie powtarzany) | ostatni wiersz `konto3\log\u1b_pytest.txt` | `2589 passed, 9 skipped, 1 warning in 2009.03s` - 0 failed |
| A: lista kuwet po "Rozlozona" z tla | `proby\test_proby_rec.py::test_a_*`, 3 rozmiary | kuweta pod stalym punktem zmienila sie 8 / 13 / 19 razy na 33 kroki; ochrona nieaktywna; klikniecie wybralo inna kuwete (uwaga 1) |
| B: "Excel: wskaz wiersz" przy widocznym oknie Excela | `test_b_*` | polecenie wyslane, zakladka zostaje "wynik", panel Excela niewidoczny (uwaga 2) |
| C: ekran a stan dla kazdej kuwety jako biezacej | `test_c_*`, 33 kuwety x 3 rozmiary | niezgodnych ze stanem 0 z 99 (numer, liczba gniazd w napisie, obwodki map, wiersz "teraz"); skrocone wielokropkiem 0 / 0 / 2 (uwaga 5); napisy uciete w ukladzie wysokim 0 |
| D, F: 3 / 4 / 5 / 6 plytek w piecu | `test_d_*`, `test_f_*` | usterek ukladu: 3 plytki 0 / 0 / 0; 4 plytki 0 / 0 / 0; 5 plytek 0 / 0 / 5; 6 plytek 0 / 0 / 13 (kolejno 1920x1001 / 1536x784 / 1280x642). Otwarta praca dwuznaczna z przypisaniem recznym przy 6 plytkach: przyciski kandydatow, decyzji, "Rozlozona", "Cofnij", "Zamknij piec" widoczne w calosci we wszystkich 3 rozmiarach |
| E: wysokosc wiersza listy | `test_e_*` | wysoki 30 -> 30; zwarty 30 -> 26 po pierwszej zmianie stanu (uwaga 6) |
| G: mapy, stary uklad (baza `e57fabe`) a nowy, 3 plytki | `proby\test_baza_promien.py` na obu commitach | promien gniazda stary / nowy: 25,9 / 26,6 px (1920x1001), 19,9 / 19,5 px (1536x784), 14,4 / 13,5 px (1280x642); gniazd z numerem kuwety 69 / 69, 69 / 69, 65 / 65 z 72 - mapy nie sa mniej czytelne niz w starym ukladzie |
| H: uklad zwarty, wpisywanie numeru | `proby\test_proby3.py::test_h_*`, 2 rozmiary | pole numeru widoczne w miejscu opisu, duzy numer zostaje, Enter wysyla `wybierz_kuwete` z wpisanym numerem, mapy w miejscu |
| I: kuweta rozlozona wybrana ponownie | `test_i_*` | lista "teraz", "Rozlozona" aktywne (uwaga 8) |
| zrzuty odtworzone | `py.cmd narzedzia\zrzuty_okna.py --wyjscie <robocze> --tylko rano_rozkladanie rano_kandydaci rano_zamknij_mimo --rozmiar 1536x864` | 3 z 3 PNG identyczne co do bajta z plikami w repo (SHA-256) |
| `styl.py` | wyszukanie `styl.py`, `ui.styl`, `import styl` w calym drzewie `233ed1b` (py, cmd, bat, ps1, toml, spec, md) | 0 importow i 0 odwolan w programie, narzedziach i instalacji; trafienia tylko w raportach, starych dowodach odbioru i w tescie, ktory tego pilnuje |

Wstrzykniecia (kazde: 1 zamiana w kopii, `pytest -x` na 3 plikach testow poranka, przywrocenie pliku): **17 z 20 wykrytych**.

| Wstrzykniecie | Wynik |
|---|---|
| E1 klikniecie listy kuwet mimo ochrony | wykryte (`test_s3_16_lista_kuwet_*`) |
| E2 ochrona listy nie startuje | wykryte (ten sam) |
| E3 numer zapisany w wierszu przesuniety o jedna pozycje | wykryte (ten sam) |
| E4 "mozesz zamknac piec" mimo blokad | wykryte (`test_s3_16_wszystkie_kuwety_*`) |
| K1 "dopasowanie pewne" takze przy konflikcie | wykryte (`test_s3_16_przypisanie_programu_*`) |
| E5 duzy numer = pierwsza kuweta listy zamiast biezacej | wykryte |
| E6 Enter potwierdza pierwsza kuwete listy zamiast pokazanej | wykryte |
| E7 napis gniazd biezacej kuwety: tylko pierwsze gniazdo | **NIE wykryte** (85 passed) |
| E8 lista: kuweta rozlozona pokazana jako "czeka" | wykryte (`test_k3_rozkladanie_*`) |
| E9 brak ochrony map po wejsciu w tryb rano | wykryte |
| E10 brak ochrony strefy pytan rano | wykryte |
| E11 mapy przesuwaja sie o 6 px przy wpisywaniu numeru | wykryte (`test_mapy_rano_nie_przesuwaja_sie_*`) |
| E12 Enter przy pytaniu przed "Zamknij piec" rozklada kuwete | wykryte |
| E13 "Zamknij piec" bez pytania przy pracach bez rozstrzygniecia | wykryte |
| E14 "Cofnij" wysyla kuwete biezaca zamiast ostatniej potwierdzonej | wykryte (`test_skroty_poranka`) |
| E15 zakladka "Excel" nie pokazuje sie sama | wykryte |
| K2 "To ten projekt" drugiego kandydata wysyla pierwszego | **NIE wykryte** (85 passed) |
| E16 przytrzymany Enter powtarza "Rozlozona" | wykryte |
| E17 "Zamknij piec" aktywne mimo blokad | wykryte |
| E18 "Rozlozona" aktywne bez osoby | **NIE wykryte** (85 passed) |

## 3. Kryteria zlecenia

| Kryterium / zakres | Ocena | Dowod |
|---|---|---|
| zakres 1: poranek w nowym szkielecie, czesci wspolne, barwy i rozmiary z `motyw`, mapa i strefa o stalym polozeniu | potwierdzone wlasna proba | `test_ui_poranek` 20 passed; E11 wykryte; proby D, F, H; `test_barwy_sa_tylko_w_motywie` obejmuje pliki poranka. Zastrzezenia: uwagi 3, 5, 7 |
| zakres 2: panel Excela w nowym motywie | potwierdzone przegladem i testem | diff `okno_excela.py` zmienia tylko wyglad i `ustaw_uklad`; logika zapisu (B1: przyciski aktywne dopiero po wyborze pozycji) bez zmian; E15 wykryte. Zastrzezenie: uwaga 2 |
| zakres 3: S3-16 zamkniete, z testem | **czesciowo** | "mozesz zamknac piec" tylko bez blokad - potwierdzone (E4); "dopasowanie pewne" nie przy konflikcie - potwierdzone (K1); lista kuwet: ochrona przy zmianie kolejnosci potwierdzona (E1-E3), przy przewinieciu w tle - NIE (uwaga 1) |
| zakres 4: `ui/styl.py` i stary uklad usuniete, `utworz_okno` bez zmian | potwierdzone wlasna proba | 0 importow (wyszukanie + `test_styl_usuniety_*`); `ui/__init__.py` poza diffem; usuniete napisy (`PRZELACZ_NA`, `PIEC_OTWARTY`, `BLOKADY_TYTUL`, `ZAMKNIJ_PIEC_SKROT`, `KUWETY_PODPOWIEDZ`, `JESZCZE`...) nie maja uzyc w programie ani narzedziach |
| zakres 5: testy bez ekranu (akcje, skroty, pytania, stany szczegolne, 6 rozmiarow, 800 ms), tabela stary -> nowy | potwierdzone z lukami | 17 z 20 wstrzykniec wykrytych; luki: uwaga 4. Tabela w raporcie p. 6.2 zgodna z diffem testow (zaden test nie usuniety; zmiany asercji w `test_ui_rano`, `test_p14_ekran`, `test_aplikacja_rano` wynikaja z ukladu). Zmiana asercji P14 ("Wroc" na prawo od "Zamknij piec mimo to" -> "Zamknij piec mimo to" nie lezy na miejscu "Zamknij piec") uzasadniona: przycisk jest teraz w lewym dolnym rogu, pytanie w strefie u gory |
| zakres 6: zrzuty 1920x1080 i 1536x864, min. 3 sceny | potwierdzone wlasna proba | 8 PNG w repo (3 sceny w obu rozmiarach + 2 w 1536x864); 3 odtworzone identyczne |
| kryterium: pliki testow okna 0 failed | potwierdzone wlasna proba | 7 plikow: 265 passed, 0 failed |
| kryterium: pelny pytest 0 failed | potwierdzone w logu (nie powtarzane) | 2589 passed / 9 skipped / 0 failed |
| kryterium: kontrast kazdej pary >= 4,5 : 1 | potwierdzone biegiem testu | `test_ui_motyw.py` passed w moim biegu; U1b dodaje 1 pare (napis `#B8B8B8` na tle miniatury `#000000`) |
| kryterium: mapa nie przesuwa sie przy zmianach stanu rano | potwierdzone wstrzyknieciem | E11 (6 px) wykryte przez test 16 zmian x 4 rozmiary; proba H |
| kryterium: zrzuty w repo, lista zmienionych tekstow w raporcie | potwierdzone przegladem | raport p. 7 i p. 8 (17 wierszy "bylo -> jest") zgodne z `napisy_rano.py` |

Funkcje starego trybu porannego i panelu Excela (porownanie starego `ekran_rano.py` z bazy z nowym, wiersz po wierszu): akcje
pieca i plytek, pytania, wybor numeru, kandydaci, przypisanie reczne, reczne zamkniecie braku, zalegle piece Excela, skroty
(cyfry, "#", Enter, Backspace, Esc, Spacja), ochrona map po zmianie zestawu plytek - sa w nowym oknie (tabela raportu p. 5
zgodna z kodem). Zginelo tylko to, co opisuje uwaga 2, oraz objasnienie obwodki (uwaga 3). Bledy programu rano przeszly
z wlasnego paska ekranu na liste okna - nowy blad rozwija ja sam (test passed).

Odstepstwa od makiety z `KONIEC_u1b.txt` (10 pozycji raportu p. 9): mapy w srodku i strefa pytan nad zakladkami wynikaja
wprost ze zlecenia; kolumna "Praca" 340 px i margines mapy 4 px sa w granicach SPEC i poparte pomiarem (proba G: mapy
jak w starym ukladzie); pole "Inna kuweta" jako napis, kafelki z licznikami, naglowek kolumny "Praca" z "Zamknij [Esc]",
blokady tylko z kontrolera - zachowuja funkcje starego okna. Do oceny wlasciciela zostaja: lista kuwet w kolumnie "Praca"
(p. 5 pkt 1) i napisy zostawione dla cytatow instrukcji (p. 5 pkt 5).

## 4. Zakres plikow i zasady

- Poza lista plikow zlecenia: (a) `narzedzia/zrzuty_instrukcji.py`, 1 wiersz (2 linie diffu): `styl.CZCIONKA` ->
  `motyw.CZCIONKI[-1]`. Wartosc ta sama ("Segoe UI" - w bazie `styl.CZCIONKA = motyw.CZCIONKI[-1]`), zmiana konieczna po
  usunieciu `styl.py`, zachowanie narzedzia bez zmian. **Uzasadniona i nieszkodliwa.** (b) `testy/test_instrukcje.py`,
  `ZRODLA_CYTATOW`, 3 wpisy: "Zamknij piec" (-1 zrodlo: usuniety nieuzywany napis `ZAMKNIJ_PIEC_SKROT`; przycisk bierze napis
  ze `statusy`), "dwie prace" (+2: nowe wzory "{n} prace" w `napisy_rano` pasuja do cytatu przypadkiem), "konflikt" (+1 w
  `ekran_rano.py` i `kandydaci.py`: nazwa klasy w kodzie). Zadna z trzech zmian nie odpowiada zmianie napisu, ktory instrukcja
  cytuje - **uzasadnione i nieszkodliwe**. Uwaga do wiadomosci: straznik zostaje zielony takze dla cytatu "Kuweta 3228",
  bo napis `KUWETA_BIEZACA` zostal jako podpowiedz i opis dla czytnika ekranu, a na ekranie jest juz sam numer pod
  "Teraz rozkladasz" - straznik nie przypomni o tej roznicy przy odswiezaniu instrukcji (instrukcje sa znane jako nieaktualne).
  (c) 8 PNG w `etap3/nowy_interfejs/zrzuty/` - wymagane zakresem 6; razem 1 164 931 bajtow.
- Nietykalne (`kontroler_api.py`, `aplikacja.py`, `session*.py`, `silnik.py`, `scanner.py`, `porownaj.py`, `inspect.py`,
  `match.py`, schemat bazy, `statusy.py`): 0 plikow w diffie.
- ASCII: znaki spoza ASCII tylko w `napisy.py` i `napisy_rano.py` (teksty ekranu, pliki istniejace). Konce linii: wszystkie
  zmienione pliki tekstowe LF. Bez nowych pakietow, okien modalnych, cieni, gradientow, emoji (test passed).
- Dane osobowe: brak (dane atrapy: kuwety fikcyjne, "Technik A"). Duze dane: brak poza zrzutami.
- Commity: 6, przedrostek "E3-U1b", stopka `Co-Authored-By: Claude Opus 5.5` w 6 z 6. T13 (0 naruszen) - wg wykonawcy,
  niesprawdzone.

## 5. Do decyzji wlasciciela

1. Lista kuwet stoi w kolumnie "Praca" i znika, gdy otwarta jest praca (makieta: lista zawsze widoczna pod "Teraz
   rozkladasz"). Przy otwartej pracy widac "Teraz rozkladasz" i mapy, ale nie stany kuwet (rozlozona / czeka / braki).
2. Wyglad obwodki biezacej kuwety wobec pierscienia wybranego gniazda (uwaga 3) - SPEC mowi tylko o wybranym gniezdzie.
3. Ile plytek moze miec jeden piec? Okno 1280x720 miesci bez usterek 3-4 mapy (uwaga 7); od 4 plytek przy 1536x784 i od
   3 przy 1280x642 promien gniazda spada ponizej 16 px (w gniezdzie sam numer kuwety, bez zeba).
4. Enter, Backspace i cyfry dzialaja takze na zakladkach "Kompletne i braki", "Ostatni zamkniety piec" i "Excel", gdzie
   nie widac wiersza "Teraz rozkladasz" ani pola numeru (tak samo bylo w starym oknie na stronie wyniku). Czy klawisze
   rozkladania maja dzialac tylko na zakladce "Rozkladanie kuwet"?
5. "Cofnij  [Backspace]" (makieta: "Cofnij poprzednia") i "Kuweta n" jako podpowiedz zostaly ze wzgledu na cytaty
   w instrukcjach - do rozstrzygniecia przy odswiezaniu instrukcji.
