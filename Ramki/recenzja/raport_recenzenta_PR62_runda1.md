# Raport recenzenta - PR #62 (E3-U1a: nowe okno - motyw, szkielet, tryb wieczorny), runda 1

- Data: 25.11.2026. Zlecenie: `rec-u1a-r1`. Recenzent: niezalezny, PC, konto `<konto-PC>` (Claude Code konta 3).
- Zakres: `git -C <PC-katalog>\qc diff main...origin/e3/u1-okno`, `main` = `b856b9e`, HEAD = `e57fabe`
  (40 plikow, +6262 / -1822 - `git diff --stat`, moj pomiar).
- Miara: `Ramki/etap3/nowy_interfejs/SPEC.md` p. 1-5 (zakres U1a: p. 5 punkty 1, 2, 5, 6 dla trybu wieczornego), makieta
  `makieta/Main.dc.html`, `raporty/E3-U1a_przekazanie.md` (lista "nietkniete", p. (d), (e), (g)), raport
  `raporty/E3-U1a_2026-11-25.md` (przeczytany po wlasnym przegladzie kodu i pierwszych probach).
- Metoda: (1) przeglad calego nowego kodu `ui/okno.py`, `ui/wieczor.py`, `ui/czesci.py`, diff `ui/mapa.py`, `ekran_rano.py`,
  `kandydaci.py`, `mapa_rano.py`, `obraz.py`, `napisy.py`, `__init__.py`, `statusy.py`, testow; (2) porownanie ze starym kodem
  z `main` (`okno.py`, `czesci.py` - sygnaly, polecenia, klawisze, kolejnosc paneli, widok pracy, pasek stanu); (3) testy
  paczki; (4) 5 plikow wlasnych prob na oknie sterowanym jak przez technika (Qt `offscreen`, dane `AtrapaKontrolera`);
  (5) 47 wstrzykniec bledu w kopii recenzenta - kazde z biegiem 4 plikow testow okna.
- Uruchomiono (kopia `<PC-katalog>\qc-wt\rec-u1a`, detached `e57fabe`; 1 proces python naraz; kroki dluzsze niz 3 min przez
  `ciezki.ps1 -Tor 3`): szczegoly i liczby w p. 2. Pelnego pytest nie powtarzalem; log wykonawcy
  `<PC-katalog>\konto3\log\u1a_pytest.txt`, ostatni wiersz: `2565 passed, 9 skipped, 1 warning in 1957.83s` (odczyt wlasny).
- Niczego nie poprawialem i nie commitowalem. Kopia po probach: `git status --short` pusty, HEAD `e57fabe`. Pliki robocze:
  `<PC-katalog>\konto3\robocze\rec-u1a-r1\`.
- Okna nie widzialem na prawdziwym ekranie (jak wykonawca) - wszystkie pomiary geometrii sa z Qt `offscreen`.

## 0. Werdykt

**Do scalenia po poprawkach.** B 0 / P 3 / D 8.

Bledu, ktory zapisuje zly wynik albo gubi dane, nie znalazlem. Kod okna jest zgodny ze starym tam, gdzie mial zostac
(polecenia, klawisze, decyzja tylko dla pokazanej pracy, pytania, komunikaty), a cztery znaleziska S3 sa zrobione wg litery
SPEC i maja testy, ktore padaja po zepsuciu kodu (19 z 20 wstrzykniec w te miejsca wykryte). Trzy uwagi P:

- **P1** - znak "POPRZEDNIA PLYTKA" znika w chwili przyjscia wyniku takze wtedy, gdy ekran ZOSTAJE na poprzedniej plytce;
  technik widzi wtedy stara mape w pelnych kolorach i bez oznaczenia (takze przy ponownym skanie plytki o tym samym numerze).
- **P2** - ochrona 800 ms skrotow decyzji U / O / C nie ma juz zadnego testu (stary test to sprawdzal, zostal zastapiony testem
  odwrotnej sytuacji); to trzecie, nieopisane w raporcie miejsce, w ktorym nowe testy sa lagodniejsze niz stare.
- **P3** - kolor statusu w trzech z czterech miejsc ekranu (znacznik w kolumnie "Praca", kropka legendy, kropka licznika na
  kafelku) i napis zapisanej decyzji nie sa przypiete zadnym testem (4 wstrzykniecia, 0 padniec; test legendy sprawdza liste
  skladana obok, nie kropke).

Poprawki P1-P3 sa male (kilka linii kodu + testy); nie wymagaja zmiany kontraktu ani ukladu.

## 1. Uwagi

Sciezki wzgledem `Ramki/stanowisko/`. Numery linii wg `e57fabe`.

| Nr | Waga | Plik:linia | Scenariusz (stan / co robi technik -> co sie dzieje) | Propozycja |
|---|---|---|---|---|
| P1 | P | `stanowisko/ui/okno.py:411-420` (wolane z `:359`, `:799`) | Plytka A na ekranie ma prace do obejrzenia (albo technik ma otwarta prace, otwarte pytanie, plytke bez numeru - regula A-P2 / S3-3: ekran nie przelacza sie sam). Technik skanuje nastepna plytke. W czasie analizy naglowek pokazuje "POPRZEDNIA PLYTKA - wynik nowego skanu nie jest jeszcze gotowy", mapa jest przygaszona. Wynik przychodzi: ekran zostaje na A, znak ZNIKA, mapa A wraca do pelnych kolorow. Technik, ktory czekal na wynik, widzi "rozjasniona" mape - to nadal stara plytka. Proba A (p. 2): po wyniku `pokazana == A`, `mapa_poprzednia` niewidoczna, `mapa.poprzednia() == False`; przy ponownym skanie TEJ SAMEJ plytki naglowek brzmi dalej "Plytka 1", rozni sie tylko godzina skanu w drugim wierszu. Zostaja sygnaly z E3-P14 (przycisk "Pokaz nowy wynik", informacja "Nowy wynik czeka", znaczek "NOWA", blysk paska) - sa w lewej kolumnie, nie przy mapie. Znikniecie znaku, ktorego tresc mowila "wynik nie jest jeszcze gotowy", jest nowym, mylacym sygnalem "wynik jest i to on". SPEC p. 4 (S3-14) mowi tylko o czasie analizy - litera spelniona, cel znaleziska ("zielona mapa plytki A, gdy w skanerze lezy juz plytka B") nie. | W `_oznacz_poprzednia`: znak i przygaszenie takze wtedy, gdy wsrod `_nieobejrzane` jest skan nowszy niz pokazany; inny napis, np. "POPRZEDNIA PLYTKA - nowy wynik czeka: Pokaz nowy wynik". Test: scenariusz proby A (plytka z pracami do obejrzenia, analiza, wynik) - znak zostaje do klikniecia "Pokaz nowy wynik". |
| P2 | P | `stanowisko/ui/okno.py:707-709`; `testy/test_p15_ekran.py:151`; `testy/test_ui_okno.py:259-286` | Wstrzykniecie O10: warunek `if not self.ochrona_aktywna()` przy klawiszach U / O / C zamieniony na `if True` - 164 z 164 testow plikow `test_ui_okno`, `test_ui_motyw`, `test_ui_wieczor`, `test_p15_ekran` przeszlo. Na `main` pilnowal tego `test_p15_ochrona_po_komunikacie_ogolnym_konczy_sie_sama_i_pomija_skroty_decyzji` (praca otwarta, ochrona, "U" -> nic nie zapisane); w paczce zastapiony testem `..._nie_wlacza_ochrony_skrot_decyzji_dziala` (sytuacja odwrotna). Test S3-15 sprawdza pod ochrona N, Enter i klik mapy, ale nie U / O / C. Raport wymienia DWA miejsca, w ktorych nowy test jest lagodniejszy niz stary (przekazanie (d) 10) - to jest trzecie. Samo zachowanie jest dzis poprawne (proba I: po powrocie z "Poranka" z otwarta praca 3 klawisze pod ochrona -> 0 decyzji, po ochronie "U" -> 1 decyzja). | Do `test_s3_15_powrot_z_trybu_rano_...` (albo nowy test): otwarta praca przed przejsciem do "Poranka", po powrocie U, O, C pod ochrona -> zero polecen decyzji; po ochronie "U" zapisuje. Dopisac to miejsce do listy "test lagodniejszy" w raporcie paczki. |
| P3 | P | `stanowisko/ui/wieczor.py:685` (znacznik statusu pracy), `:285` (kropka legendy), `:109` (kropka licznika kafelka), `:700-705` (napis zapisanej decyzji); `testy/test_ui_okno.py:721-723` | SPEC p. 1: "kolory i napisy statusow wylacznie ze stanu". Na mapie pilnuja tego testy (piksel = `Gniazdo.rgb`; wstrzykniecie M1 wykryte). W pozostalych miejscach, pisanych w tej paczce od nowa, nie pilnuje nic: W3 (znacznik statusu w kolumnie "Praca" zawsze zielony), W4 (kropka legendy zawsze zielona), W5 (kropka licznika na kafelku zawsze zielona), W6 (napis "Decyzja: ..." zawsze "OK", takze po "Ukruszona") - kazde 164 z 164 testow przeszlo. Test legendy porownuje `Legenda.pozycje()` - liste skladana obok rysowania z tych samych danych, a nie kolor kropki (metoda `Kropka.kolor()` "do testow" nie jest uzyta w zadnym tescie). Kod jest dzis poprawny (przeglad: `zrodlo.rgb`, `g.rgb`, `ST.status(STATUS_WG_KOLORU[klasa]).hex`), ale kryterium jest nieudowodnione, a przebudowa U1b pojdzie po tych samych czesciach. | Testy: (a) dla pracy czerwonej, zoltej, szarej i z decyzja: kolor tla `praca_status` (arkusz albo piksel) == `Praca.rgb`; (b) `Kropka.kolor()` kazdej pozycji legendy == `Gniazdo.rgb`; (c) `Kropka.kolor()` licznikow kafelka == kolor statusu klasy; (d) `praca_decyzja` po "Ukruszona" zawiera `PRZYCISKI["ukruszona"]`, po "OK" - `PRZYCISKI["ok"]`, osobe i godzine. |
| D1 | D | `stanowisko/ui/okno.py:325-336`, `:849-860`; `stanowisko/ui/czesci.py:1027-1073`; `testy/test_ui_wieczor.py:2023` | Lista osob rozwija sie sama w tle (koniec zmiany -> `wymaga_operatora`) i nie ma ochrony 800 ms, ktora maja strefa pytan i lista bledow (SPEC p. 4, S3-3: "ochrona 800 ms obejmuje takze panele"). Proba B, 4 rozmiary okna: lista (420 px) zaslania 37 px (1920 x 1080, 1600 x 900, 1536 x 864) albo 87 px (1280 x 720) prawej czesci OBU przyciskow pytania o ponowny skan i caly przycisk "Zamknij [Esc]"; przycisk pierwszej osoby naklada sie na "Nie, to nowy wsad" na 20 x 11 px (1280 x 720: 70 x 7 px). Klik w ten skrawek w chwili rozwiniecia = `wybierz_operatora(pierwsza osoba)` zamiast odpowiedzi; klik w reszte zaslonietej czesci jest polykany. Zdarza sie raz na zmiane, pole jest male - stad D. `sprawdz_uklad` pomija pary "przycisk w nakladce / przycisk pod nakladka" (`:2023`), wiec testy ukladu tego nie widza. | Zaslona 800 ms na `PanelOsoby`, gdy lista rozwinela sie w tle (jak `ListaBledow.chron`), albo szerokosc listy = szerokosc kolumny "Praca" (360 / 320 px) - wtedy nie wchodzi na strefe pytan. |
| D2 | D | `stanowisko/ui/okno.py:411-413` | Proba C: plik skanu jest juz w folderze, ale zajety (`skaner.zajete = 1`, pasek: "plik skanu zajety - czekam") albo technik nacisnal Spacje (`czeka_na_skan`, "czekam na plik skanu...") - mapa poprzedniej plytki NIE jest oznaczona ani przygaszona; znak wchodzi dopiero z kolejka / analiza. To czas, w ktorym plytka B lezy juz w skanerze (cel S3-14). Litera SPEC ("w czasie analizy") spelniona - do decyzji wlasciciela (p. 5). | Jesli wlasciciel chce: `_nowy_skan_w_drodze` takze przy `stan.skaner.zajete > 0` i `czeka_na_skan`. |
| D3 | D | `stanowisko/ui/czesci.py:1206-1215`; `stanowisko/ui/okno.py:339` | Pierwsze z dwoch zgloszonych zlagodzen testu (`test_ap3_*`). Pomiar (proba F): przy 2 bledach programu w calosci widac 2 z 2 przy 1920 x 1080, 1600 x 900 i 1536 x 864, a 1 z 2 przy 1280 x 720 (lista 944 x 130 px, drugi blad po przewinieciu; licznik "Bledy programu: 2" jest na pasku stanu). Stare okno gwarantowalo 2. Nowy blad sam rozwija liste (wstrzykniecie O15 wykryte) i ma ochrone 800 ms (C1b wykryte). | Przyjac albo podniesc limit wysokosci listy w ukladzie zwartym - decyzja wlasciciela (p. 5). |
| D4 | D | `stanowisko/ui/czesci.py:1236-1413`; `testy/test_ui_okno.py:553-569` | Drugie zgloszone zlagodzenie (pola paska stanu skracane). Test "bez skrotow w zwyklej pracy" nie ma w stanie RAMEK, a stanowisko je ma. Pomiar z ramkami W i P (proby E, G): przy 1536 x 864 i 1366 x 768 - 0 skrotow we wszystkich 8 stanach; przy 1280 x 720 - 0 skrotow w 8 stanach zwyklej pracy (takze analiza + 1 skan w kolejce, ramka P bez polaczenia, licznik bledow), ale 3 pola skrocone, gdy po Spacji ("czekam na plik skanu...") trwa analiza i 1 skan czeka: "skany w kolejc...", "plikow projektow:..." (liczba niewidoczna), "W: gotowa (plytka 1) - P: got..."; przy 1240 x 640 skroty juz przy "ramka P bez polaczenia + analiza + 1 w kolejce" i przy "ramka P bez polaczenia + licznik bledow". Pelny napis jest w podpowiedzi (test). | Dodac ramki do `test_pasek_stanu_bez_skrotow_w_zwyklej_pracy`; w ukladzie zwartym odzyskac miejsce (np. krotsze podpisy "Skaner" / "Projekty" albo wezszy pasek postepu). |
| D5 | D | `stanowisko/ui/wieczor.py:91-93`, `:110` | Licznik na kafelku plytki nosi napis statusu PODSTAWOWEGO klasy koloru. Proba H: plytka, na ktorej obie prace czerwone maja juz decyzje "Ukruszona" - kafelek: "UBYTEK 2", mapa i legenda: "UKRUSZONA" (2); "sprawdz 3" na kafelku to w legendzie "sprawdz" 1, "nie sprawdzono" 1, "blad kontroli" 1. Liczby i kolory sie zgadzaja, nazwa na kafelku jest nazwa klasy, nie statusu. Stare okno mialo te nazwe tylko w podpowiedzi. | Zostawic albo liczyc kafelek wg `podpis` jak legenda - do decyzji wlasciciela. |
| D6 | D | `stanowisko/ui/okno.py:651`, `:459-460`, `:518-519`, `:925`; `testy/test_ui_motyw.py:134-142` | Wstrzykniecia niewykryte, ktorych nie licze jako P, bo logika i testy sa tu takie same jak na `main` albo skutek jest kosmetyczny: O11 (decyzja bez sprawdzenia, ze widok pokazuje wybrana prace), O17 (nowa plytka zabiera ekran przy otwartej pracy na plytce bez prac do obejrzenia - `test_nowa_plytka_nie_zabiera_otwartej_pracy` uzywa plytki, ktora i tak blokuje przelaczenie; zachowanie poprawne - proba J), O21 (klik pracy poza gniazdem pod ochrona - uprzaz zawsze czeka na koniec ochrony), O19 (tytul pytania plytki Z numerem bez "skan z GG:MM" - nowy format z tabeli tekstow nie ma asercji), S4 (`test_statusy_zmienione_tylko_rgb_ekranu` nie pilnuje pola `opis`; diff `statusy.py` sprawdzilem recznie: 27 wierszy, zmienione wylacznie trojki RGB i komentarz). | Tanie asercje przy okazji P2 / P3. |
| D7 | D | `testy/test_ui_okno.py:216-247`, `:614`, `:648` | Przy `QT_SCALE_FACTOR=1.25` padaja 2, przy `1.5` - 3 testy `test_ui_okno.py` (s3_14, status nie tylko barwa, przyciski ze skrotem). Przyczyna po stronie testu: obraz z `grab()` ma `devicePixelRatio` 1,25 / 1,5, a test probkuje we wspolrzednych logicznych (proba K: kolor gniazda zgodny w 1 z 9 / 0 z 9 punktow logicznych i w 9 z 9 po przemnozeniu przez skale). Okno rysuje poprawnie; `test_ui_rozdzielczosc.py` przechodzi przy obu skalach (2 z 2). Pelny pytest biegnie bez skali. | Probkowac `punkt * devicePixelRatio` (jeden pomocnik) - wtedy testy pikselowe beda wazne takze przy skali. |
| D8 | D | `Ramki/stanowisko/raporty/E3-U1a_2026-11-25.md` p. 10 pkt 10; `E3-U1a_przekazanie.md` (d) 10 | Poza dwoma zgloszonymi zlagodzeniami sa w testach jeszcze trzy, opisane tylko w kolumnie "co zmienione" tabeli testow albo wcale: obraz pracy min. 250 px (bylo 300), przyciski decyzji min. 52 / 48 px (bylo 56), oraz P2. Dwa pierwsze wynikaja z ukladu SPEC (kolumna 360 px, cel klikniecia 44 px) - przyjmuje. | Uzupelnic punkt o P2. |

## 2. Wlasne proby

Wszystkie z katalogu `<PC-katalog>\qc-wt\rec-u1a\Ramki\stanowisko`, przez `<PC-katalog>\koordynator\narz\py.cmd`. Logi i pliki
prob: `<PC-katalog>\konto3\robocze\rec-u1a-r1\`.

| Nr | Polecenie / proba | Wynik (liczby) |
|---|---|---|
| 1 | `pytest -q testy\test_ui_okno.py testy\test_ui_motyw.py` | 57 passed, 0 failed, 22 s (`p1_okno_motyw.txt`) |
| 2 | testy paczki, 9 plikow: `test_ui_wieczor`, `test_ui_okno`, `test_ui_motyw`, `test_ui_rozdzielczosc`, `test_p15_ekran`, `test_p14_ekran`, `test_okragle_ekran`, `test_ui_rano`, `test_kontroler_api` (`ciezki.ps1 -Tor 3`) | 397 passed, 0 failed, 261 s (`p3_testy_paczki.txt`) |
| 3 | `test_ui_rozdzielczosc.py` + `test_ui_okno.py` z `QT_SCALE_FACTOR=1.25` i `1.5` | 1,25: 36 passed / 2 failed; 1,5: 35 passed / 3 failed; wszystkie padniecia w `test_ui_okno.py` (D7), `test_ui_rozdzielczosc.py` 2 z 2 w obu biegach (`p7_skala_*.txt`) |
| A | `test_rec_proby.py::test_proba_a_*`: plytka A z 7 pracami do obejrzenia, analiza 60 %, potem wynik B (ten sam numer plytki) | w czasie analizy: znak i przygaszenie = tak; po wyniku: pokazana = A, znak = nie, przygaszenie = nie, naglowek "Plytka 1", "Pokaz nowy wynik" = tak, "Nowy wynik czeka" = tak; to samo dla wyniku plytki o innym numerze (P1) |
| B | `::test_proba_b_*`, 4 rozmiary okna: otwarte pytanie o ponowny skan i otwarta praca, w tle konczy sie zmiana | lista osob 420 x 162 px; zaslania 37 / 37 / 37 / 87 px obu przyciskow pytania i caly "Zamknij [Esc]"; przycisk osoby na przycisku "Nie, to nowy wsad": 20 x 11 / 20 x 11 / 20 x 11 / 70 x 7 px; ochrona mapy, strefy i nakladek: 0 z 3 aktywna (D1) |
| C | `::test_proba_c_*`: `zajete = 1`; `czeka_na_skan`; `niezapisane = 1` | znak poprzedniej plytki: nie / nie / tak (D2) |
| D | `::test_proba_d_*`: pytanie o ponowny skan + informacja ekranu + odmowa | kolejnosc strefy: informacja, odmowa, pytanie, komunikat plytki; pokazana 1 pozycja, licznik "i jeszcze 3" (zgodne z opisem, bez uwagi) |
| E | `test_rec_proby2.py::test_proba_e_*`, 4 rozmiary, ramki W i P, 6 stanow | 1920 x 1080, 1600 x 900, 1536 x 864: 0 pol skroconych w 6 z 6 stanow; 1280 x 720: 3 pola skrocone w 3 z 6 stanow (wszystkie po Spacji + analiza + kolejka albo kolejka z 3 czesciami) (D4) |
| F | `::test_proba_f_*`, 4 rozmiary, 1 i 2 bledy programu | bledow widocznych w calosci: 1 z 1 wszedzie; 2 z 2 przy trzech wiekszych rozmiarach; 1 z 2 przy 1280 x 720 (D3) |
| G | `test_rec_proby3.py`, rozmiary 1536 x 864, 1366 x 768, 1280 x 720, 1240 x 640; 8 stanow z ramkami i bez | 0 skrotow w 8 z 8 stanow dla trzech pierwszych rozmiarow; 1240 x 640: skroty w 2 z 8 stanow (D4) |
| H | `test_rec_proby4.py::test_proba_h_*`: 2 prace czerwone z decyzja "Ukruszona" | kafelek "UBYTEK 2", legenda ("UKRUSZONA", 2) (D5) |
| I | `::test_proba_i_*`: otwarta praca, "Poranek" i powrot, klawisze U, O, C pod ochrona | decyzji wyslanych pod ochrona: 0; po ochronie "U": 1 (zachowanie poprawne; test paczki tego nie sprawdza - P2) |
| J | `::test_proba_j_*`: otwarta praca na plytce bez prac do obejrzenia, przychodzi wynik B | ekran zostaje na A, widok pracy otwarty, "Pokaz nowy wynik" = tak (zachowanie poprawne) |
| K | `test_rec_proby5.py` przy skali 1 / 1,25 / 1,5: kolor piksela gniazda w punkcie probnym | zgodny we wspolrzednych logicznych: 9 / 1 / 0 z 9; we wspolrzednych x skala: 9 / 9 / 9 z 9 (D7) |
| W | 47 wstrzykniec (`wstrzykniecia.ps1`, `ciezki.ps1 -Tor 3`): jedna zamiana tekstu w kodzie, `pytest -x -q` na `test_ui_okno`, `test_ui_motyw`, `test_ui_wieczor`, `test_p15_ekran` (164 testy), przywrocenie pliku | wykryte 37, niewykryte 10 (`wstrzykniecia_wynik.txt`); tabela nizej |

Wstrzykniecia (W = wykryte, w nawiasie test, ktory padl pierwszy; N = wszystkie 164 testy przeszly):

| Kod | Co zepsute | Wynik |
|---|---|---|
| W1a | S3-4: "bez projektu" nie daje "nie sprawdzil" | W (`test_s3_4_*`) |
| W1b | S3-4: kazdy wynik kontroli = "nie wskazal ubytku" | W (`test_s3_4_*`) |
| W1c | S3-4: stare zachowanie (zawsze "nie wskazal") | W (`test_s3_4_*`) |
| O1 | S3-14: znak tylko przy analizie, nie przy kolejce | W (`test_s3_14_mapa_poprzedniej_*`) |
| O2 | S3-14: brak oznaczenia po sygnale postepu | W (`test_s3_14_mapa_poprzedniej_*`) |
| M4 | S3-14: mapa poprzedniej plytki nieprzygaszona | W (`test_s3_14_mapa_poprzedniej_*`) |
| O3 | S3-3: otwarte pytanie nie wstrzymuje przelaczenia | W (`test_s3_3_pytanie_pokazanej_plytki_*`) |
| O4 | S3-3: brak numeru nie wstrzymuje przelaczenia | W (`test_s3_3_wybor_numeru_*`) |
| O5 | S3-3: brak ochrony strefy | W (`test_s3_3_ochrona_strefy_*`) |
| O5b | S3-3: ochrona strefy takze po kliknieciu technika | W (`test_s3_3_ochrona_strefy_*`) |
| C1 | strefa: przycisk dziala mimo ochrony (mysz i Enter) | W (`test_s3_3_ochrona_strefy_*`) |
| C1b | lista bledow: przycisk dziala mimo ochrony | W (`test_lista_bledow_*`) |
| C3 | S3-3: pytanie o numer bez godziny skanu | W (`test_s3_3_pytanie_o_numer_*`) |
| O16 | strefa pokazuje pytania innych plytek | W (`test_s3_3_pytanie_o_numer_*`) |
| O19 | S3-3: tytul pytania plytki z numerem bez godziny skanu | **N** (D6) |
| O6 | S3-15: kursor nie zerowany po powrocie | W (`test_s3_15_powrot_*`) |
| O7 | S3-15: brak ochrony po powrocie z "Poranka" | W (`test_s3_15_powrot_*`) |
| O8 | S3-15: klawisz N bez ochrony | W (`test_s3_15_powrot_*`) |
| O9 | S3-15: pozycja listy otwiera pierwsza prace gniazda | W (`test_s3_15_klawisz_n_*`) |
| M3 | mapa przyjmuje klik mimo przygaszenia | W (`test_s3_15_powrot_*`) |
| O10 | skroty U / O / C bez ochrony 800 ms | **N** (P2) |
| O11 | decyzja bez sprawdzenia, ze widok pokazuje wybrana prace | **N** (D6) |
| O12 | widok pracy zostaje po podmianie pracy w tle | W (`test_ap2_widok_pracy_*`) |
| O13 | stan o nizszej wersji nie jest pomijany | W (`test_stan_o_nizszej_wersji_*`) |
| O14 | pozycje ukryte sa pokazywane | W (`test_4_pozycje_ukryte_*`) |
| O15 | nowy blad nie rozwija listy bledow | W (`test_lista_bledow_*`) |
| O17 | nowa plytka zabiera ekran przy otwartej pracy | **N** (D6) |
| O18 | przytrzymana Spacja powtarza start skanu | W (`test_3_spacja_start_skanu_dokladnie_raz`) |
| O20 | blad programu nie trafia na liste bledow | W (`test_lista_bledow_*`) |
| O21 | klik pracy poza gniazdem bez ochrony | **N** (D6) |
| O22 | odmowa spoza stanu nie jest pokazywana | W (`test_przelacznik_trybu_*`) |
| C4 | odpowiedzi pytania aktywne bez osoby | W (`test_4_ponowny_skan_nowy_wsad_i_bez_osoby`) |
| C5 | brak ostrzezenia o decyzjach przy ponownym skanie | W (`test_pytania_mieszcza_sie_*`) |
| C6 | Spacja klika przycisk z fokusem | W (`test_klawiatura_strzalki_enter_tab`) |
| W2 | decyzje aktywne bez osoby | W (`test_4_bez_osoby_*`) |
| W3 | znacznik statusu pracy zawsze zielony | **N** (P3) |
| W4 | kropka legendy zawsze zielona | **N** (P3) |
| W5 | kropka licznika kafelka zawsze zielona | **N** (P3) |
| W6 | zapisana decyzja: zawsze napis "OK" | **N** (P3) |
| M1 | mapa: gniazdo zawsze zielone | W (`test_s3_14_mapa_poprzedniej_*`) |
| M2 | mapa: brak obwodki ubytku | W (`test_status_na_mapie_*`) |
| MO1 | motyw: napis przygaszony za ciemny | W (`test_kolory_glowne_ze_specyfikacji`) |
| S1 | `statusy`: zmieniony napis statusu | W (`test_statusy_zmienione_tylko_rgb_ekranu`) |
| S2 | `statusy`: zmieniony kolor diody ramki | W (`test_statusy_zmienione_tylko_rgb_ekranu`) |
| S3 | `statusy`: zmieniona klasa koloru statusu | W (`test_statusy_zmienione_tylko_rgb_ekranu`) |
| S4 | `statusy`: zmieniony opis statusu | **N** (D6) |
| P1 | sciezka folderu skanera na pasku stanu | W (`test_wersja_programu_na_pasku_stanu`, kontrola sciezek) |

## 3. Kryteria

Miara: SPEC p. 1-5 w zakresie U1a. "Proba" = potwierdzone wlasna proba (bieg testow paczki + wstrzykniecie albo proba z p. 2);
"przeglad" = potwierdzone przegladem kodu / plikow.

| Kryterium | Stan |
|---|---|
| p. 5.1 `ui/motyw.py` (kolory, czcionki, arkusz), test kontrastu, czesci wspolne | potwierdzone proba (`test_ui_motyw` 21 passed; MO1 wykryte) i przegladem |
| p. 5.2 szkielet okna i tryb wieczorny w calosci | potwierdzone proba (397 passed) i przegladem - z uwaga P1 |
| p. 5.5 testy nowego okna: akcje, skroty, pytania, stany szczegolne, rozdzielczosci, zakaz sciezek, ochrona 800 ms, znaleziska | czesciowo: 37 z 47 wstrzykniec wykrytych; niepotwierdzone dla ochrony skrotow decyzji (P2) i kolorow statusu poza mapa (P3) |
| p. 5.5 lista "stary test -> nowy test" | potwierdzone przegladem diffu `test_ui_wieczor.py` (nazwy testow bez zmian, 1 zmieniona zgodnie z tabela); lista zlagodzen niepelna (P2, D8) |
| p. 5.6 zrzuty z atrapy 1920 x 1080 i 1536 x 864 (wieczor) | potwierdzone przegladem: 8 plikow PNG, 2 obejrzane (pytanie o ponowny skan, analiza nowego skanu) - zgodne z opisem; zrzuty poranne to U1b |
| p. 1 kontrakt bez zmian (`kontroler_api.py`, `aplikacja.py`) | potwierdzone proba: plikow nie ma w `git diff --name-status` |
| p. 1 kazda funkcja starego okna zostaje | potwierdzone przegladem: sygnaly i polecenia starego `OknoWieczor` (skan, pula, osoba, tryb, ramki, plytki, mapa, decyzje, krazek, lista, zapis, panele pytan i komunikatow z przyciskami, polecenia plytki, prace poza gniazdami, znacznik dopuszczenia, klawisze Spacja / U / O / C / N / Esc / strzalki / Enter / Tab) maja odpowiednik; nowe: Esc zamyka liste osob takze w "Poranku"; stare testy o tych samych nazwach przechodza |
| p. 1 zadnych okien modalnych; wejscie `utworz_okno` | potwierdzone proba (testy `test_lista_osob_*`, `test_pakiet_ui_*`) |
| p. 1 kolory i napisy statusow wylacznie ze stanu | potwierdzone przegladem; proba tylko dla mapy (M1) - reszta nieudowodniona (P3) |
| p. 1 zero sciezek i nazw plikow | potwierdzone proba (P1 wykryte) |
| p. 1 Spacja nigdy nie klika przycisku | potwierdzone proba (C6, O18 wykryte) |
| p. 1 ochrona 800 ms po zmianie zawartosci | mapa, strefa, lista bledow: potwierdzone proba (O5, O7, O8, C1, C1b, M3); skroty decyzji: dziala (proba I), bez testu (P2); lista osob: brak ochrony (D1) |
| p. 1 rozdzielczosci 1920 x 1080, 1536 x 864, 1280 x 720, skala 1,25 / 1,5 | uklad: potwierdzone proba (`test_ui_rozdzielczosc` 2 z 2 takze przy obu skalach; `sprawdz_uklad` w testach paczki); pasek stanu z ramkami: skroty przy 1280 x 720 w 3 z 14 zmierzonych stanow (D4) |
| p. 2 kolory SPEC, status nie tylko barwa, kontrast 4,5 : 1 | potwierdzone proba (`test_ui_motyw`, M2 wykryte); 8 kolorow statusow z SPEC porownalem recznie z `statusy.py` - 8 z 8 zgodnych |
| p. 3 uklad: paski 52 / 32 px, kolumny 280 / 360 (240 / 320), strefa o stalej wysokosci, decyzje na stalym miejscu, mapa sie nie przesuwa | potwierdzone proba (`test_ap1_*`, `test_p15_*` w biegu 397 passed) |
| p. 4 S3-3 | potwierdzone proba: 6 z 7 wstrzykniec wykrytych (O3, O4, O5, O5b, C1, C3; O19 nie - D6) |
| p. 4 S3-4 | potwierdzone proba: 3 z 3 wstrzykniec wykrytych; przeglad `napis_ubytkow` wobec `statusy.INSPEKCJE_NIESPRAWDZONE` |
| p. 4 S3-14 | litera potwierdzona proba (O1, O2, M4 wykryte); cel znaleziska niespelniony po przyjsciu wyniku, gdy ekran zostaje (P1), i w czasie skanowania (D2) |
| p. 4 S3-15 | potwierdzone proba (O6, O7, O8, O9, M3 wykryte) |
| p. 4 pytanie o ponowny skan pokazuje tekst ze stanu | potwierdzone proba (C5 wykryte; ostrzezenie o decyzjach osobnym napisem) |
| Pelny pytest 2565 passed / 9 skipped / 0 failed | odczyt ostatniego wiersza logu wykonawcy - zgodny; biegu nie powtarzalem (wg zlecenia) |

## 4. Zakres plikow i zasady

- Zmiany poza `stanowisko/ui/**` (wg `git diff --name-status b856b9e..e57fabe`): `stanowisko/statusy.py` - WYLACZNIE trojki RGB
  (27 wierszy) i komentarz nad tabela, sprawdzone linia po linii w diffie; pola `ramka`, `napis`, klasa koloru pilnuje test
  (S1, S2, S3 wykryte), pola `opis` nie (S4, D6). RGB z `statusy` czyta tylko `kontroler_api` (budowa stanu ekranu) i `ui/**`
  (`grep` po `.rgb` / `.hex` w calym `Ramki`: 17 plikow, zaden poza ekranem, testami i narzedziami odbioru, ktore czytaja
  kolor dynamicznie); diody ramki i mapa PNG z wiersza polecen nie zaleza od tych liczb.
- `testy/test_kontroler_api.py`: 1 zmieniona asercja (RGB == `porownaj.KOLORY` -> RGB == SPEC p. 2 z `test_ui_motyw.KOLORY_SPEC`,
  "pusty" == kolor plytki, klasy kolorow dalej w `porownaj.KOLORY`). Wynika z dozwolonej zmiany RGB; test kontraktu importuje
  teraz plik testu okna - przyjmuje, do uporzadkowania przy U1b.
- `narzedzia/zrzuty_instrukcji.py` (czekanie na koniec ochrony strefy), `narzedzia/zrzuty_okna.py` (nowe narzedzie zrzutow),
  pozostale pliki testow - w zakresie paczki. `kontroler_api.py`, `aplikacja.py`, `session*.py`, `silnik.py`, `scanner.py`,
  `porownaj.py`, `inspect.py`, `match.py`, `plate.py`, `synth.py`, `uklad.py`, `modele_plytek/**`, schemat bazy,
  `ui/napisy_rano.py`, `ui/okno_excela.py`: brak w diffie (lista "nietkniete" z przekazania potwierdzona).
- ASCII / LF (moj pomiar po bajtach, 32 pliki tekstowe): nowe pliki kodu, testow i raportow - 0 bajtow spoza ASCII, 0 znakow CR;
  spoza ASCII tylko 3 pliki makiety (znane, nie zglaszam) oraz istniejace `ui/napisy.py` i `statusy.py` (teksty ekranu po polsku
  - pliki istniejace zostaja w swoim stylu).
- Duze dane: 8 zrzutow PNG, razem ok. 1,18 MB (109-168 kB kazdy) - wymagane przez SPEC p. 5.6; dane na zrzutach sztuczne
  ("Technik A", kuwety 90xx). Danych osobowych, nazw zlecen ani sciezek w nowych plikach nie znalazlem.
- Nowych zaleznosci, okien modalnych, cieni, gradientow, emoji nie ma (testy `test_ui_motyw`, przeglad).
- Znane i niezglaszane (wg zlecenia): 3 naruszenia T13 w makiecie; okno nieuruchomione na prawdziwym ekranie; narzedzia
  odbioru T2 / T3 niedostosowane; instrukcje i `opisy_modulow/ui_wieczor.md` nieaktualne.

## 5. Do decyzji wlasciciela

1. **S3-14, zakres znaku "POPRZEDNIA PLYTKA".** SPEC mowi "w czasie analizy". Proponuje (P1) trzymac znak takze po przyjsciu
   wyniku, dopoki ekran pokazuje starsza plytke niz najnowszy wynik. Osobno do decyzji (D2): czy znak ma sie pojawiac juz
   wtedy, gdy program wie o skanie w drodze - po Spacji ("czekam na plik skanu") i gdy plik skanu jest zajety.
2. **Lista bledow przy 1280 x 720** pokazuje w calosci 1 z 2 bledow (stare okno: 2); przy 1536 x 864 i wiecej - 2 z 2 (D3).
3. **Pasek stanu w jednym wierszu**: z ramkami przy 1280 x 720 pola kolejki, puli i ramek bywaja skrocone takze poza "scenami
   przeciazonymi" (Spacja + analiza + 1 skan w kolejce); pelny napis tylko w podpowiedzi (D4).
4. **Lista osob** zaslania gorna czesc kolumny "Praca" (zgloszone przez wykonawce) oraz 37-87 px przyciskow pytania; rozwija
   sie w tle bez ochrony 800 ms (D1).
5. **Licznik na kafelku plytki** nazywa klase koloru napisem statusu podstawowego: prace z decyzja "Ukruszona" licza sie pod
   "UBYTEK n" (D5).
6. Sobota 28.11: P1-P3 nie zmieniaja wyniku analizy ani zapisu decyzji. Jesli poprawki nie zdaza przed pokazem, technik
   powinien wiedziec jedno: po zniknieciu znaku "POPRZEDNIA PLYTKA" trzeba spojrzec na numer i godzine skanu w naglowku oraz na
   przycisk "Pokaz nowy wynik" w lewej kolumnie - mapa mogla zostac na poprzedniej plytce.
