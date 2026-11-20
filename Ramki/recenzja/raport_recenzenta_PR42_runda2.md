# Raport recenzenta - PR #42 (E3-P14: poprawki programu przed testami T7 i T14) - runda 2

Data: 20.11.2026. STAN: ZAMKNIETY. Recenzja przyrostowa: `git -C <PC-katalog>\qc diff 05a568e..origin/e3/p14`, HEAD 5cd4199
(7 commitow, 13 plikow, +648 / -97); calosc `main...origin/e3/p14` (main 9ba9e91): 22 pliki, +2266 / -108.
Recenzje prowadzilo dwoch recenzentow: pierwszy 21:11-21:27 (sesja zatrzymana; jego notatki z liczbami - sekcja 6, bez
zmian), drugi 22:33-22:47 (przejecie: proby P1, P2, P3 poprzednika przyjete z logow bez powtarzania, reszta wykonana).
Oznaczenia zrodla liczb: **[PP]** = proba poprzedniego recenzenta tej rundy (logi `robocze\rec-p14\runda2\`), **[W]** =
pomiar wlasny drugiego recenzenta, "wg wykonawcy" = z raportu paczki, niesprawdzone.
Metoda: przeglad diffu rundy 2 (kod, testy, raport), proby na atrapie i w oknie offscreen [PP], wstrzykniecia bledow [W],
porownanie z `main` [PP], zrzuty obejrzane narzedziem Read (8 [PP] + 5 [W]).
Uruchomiono [W]: 16 wstrzykniec zlecenia + 4 dodatkowe + 2 celowane na testy geometrii, `test_ui_wieczor.py` caly,
`test_ui_rano.py` + `test_aplikacja_rano.py`, testy czasowe `test_f` / `test_k4`, proba pliku listy (D7), proba pierwszego
zapisu w polaczeniu. Pelnego pytest nie uruchamiano (zasada) - koncowka logu wykonawcy przeczytana.
Jak uruchomiono serie [W]: dwa strumienie po 1 procesie python (kopia `qc-wt\rec-p14` i zwykla kopia plikow
`robocze\rec-p14\runda2\kopia2`), kazdy krok 2-90 s, razem 22:35-22:45. Tor 1 blokady `ciezki.ps1` zajal o 22:34:05 pelny
pytest a11w (ok. 25 min), wiec serii NIE prowadzilem przez blokade - poszla jako kroki lekkie (prompt recenzji: do 2
procesow python naraz). Wpis w kolejce toru 1 zalozony przed ta decyzja zostal zamieniony na pusty (`runda2\mut.cmd` =
`exit /b 0`): gdy tor sie zwolni, w `ciezkie.log` pojawi sie START / KONIEC `rec-p14` trwajacy ponizej 1 s - to nie jest proba.
Kopia `rec-p14` po pracy: `git status --short` pusty, HEAD 5cd4199.

## 0. Werdykt i liczby

**Do scalenia.** B 0 / P 0 / D 8 (2 odlozone z rundy 1: D1, D4; 6 nowych: R2-D1 ... R2-D6).

Wszystkie 4 uwagi P rundy 1 sa zamkniete i kazda ma test, ktory bez poprawki pada: 16 z 16 wstrzykniec wykrytych (12
rundy 1, w tym M5 i M14 niewykryte w rundzie 1, + 4 nowe w kod rundy 2). Poprawki nie zmienily zachowania przy wolnej bazie
(43 wiersze odmow i skutkow identyczne z `main` [PP]), `busy_timeout` wraca do 5000 po kazdym wywolaniu [PP], pelny pytest
wykonawcy na kodzie koncowym 1891 passed / 9 skipped / 0 failed. Zadna z 8 uwag D nie daje zlego wyniku ani utraty danych
i zadnej technik nie napotka w zwyklej pracy: dwie dotycza polecen, ktorych okno nie wysyla, dwie - wygladu w rzadkim
zlozeniu stanow, jedna - sciezki osiagalnej tylko w symulacji, jedna - martwego kodu; D1 i D4 odlozono bezpiecznie.

## 1. Uwagi

### 1.1 Uwagi rundy 1 - stan

| Uwaga r1 | Stan | Dowod |
|---|---|---|
| P1 (5 polecen plytki: 7,4 s i wyjatek przy EXCLUSIVE) | ZAMKNIETA | [PP] `r2_p1.py`: 5 polecen przy EXCLUSIVE 657-701 ms (wieczor i rano; runda 1: 7402-7455 ms + wyjatek), przy RESERVED 284-301 ms; odmowa `baza_zajeta`, 1 komunikat z "Ponow teraz", `wykonaj` nie rzuca, po zwolnieniu bazy ponowienie ok w 5 z 5 (obie blokady); prawdziwa `Aplikacja`: 665-668 ms. Odczyty okna z przegladu wykonawcy: `szczegoly_pracy` 663 ms -> None, `projekty_kuwety` 662-715 ms -> (). Wolna baza: 43 wiersze identyczne z `main`. [W] wstrzykniecia R1 (`podaj_numer_plytki` bez oslony) i R1b (`dopusc_plytke` czyta przed oslona): pada `test_n1_polecenie_klikane_...[plytka-<polecenie>-EXCLUSIVE]`; R1c (`szczegoly_pracy` bez oslony): pada `test_r2_p1_odczyty_okna_...`. Tabela "polecenie -> czas i skutek" jest w raporcie (13.2, 18 wierszy, z uczciwym "nie mierzone"). Poza oslona zostaly 2 polecenia, ktorych okno nie wysyla - R2-D1, R2-D2. |
| P2 (drugie klikniecie w miejsce "Zamknij piec" zamyka piec) | ZAMKNIETA | [PP] `r2_p2.py`: 8 wariantow (4 rozmiary x z komunikatem nad piecem / bez) x 9 punktow starego przycisku x 2 kolejne klikniecia = 144 klikniecia: piec zamkniety 0 razy (runda 1: 2 z 8 wariantow); czesc wspolna starego przycisku z "Zamknij piec mimo to" 0 x 0 px w 8 z 8 (runda 1: 128 x 43 ... 114 x 13 px); decyzji / potwierdzen kuwet po 144 kliknieciach 0; przyciski pytania widoczne w calosci w 8 z 8. [W] wstrzykniecie R2 (kolejnosc przyciskow z rundy 1): pada `test_n3_zamknij_piec_pyta_...` (asercja kolejnosci), a sam test geometrii `test_r2_p2_...` pada w 4 z 8 przypadkow (wszystkie "bez komunikatu": "piec ZAMKNIETY po drugim kliknieciu", trafione `zamknij_mimo_tak`). Skutek uboczny poprawki - R2-D3. |
| P3 (panel "Nowy wynik czeka" przesuwa mape) | ZAMKNIETA | [PP] `proby_przesuniecie.py` (skrypt rundy 1 bez zmian): klik w stary srodek gniazda trafia w inne gniazdo 0 z 19 w 4 z 4 rozmiarow (runda 1: 4 / 2 / 0 / 0 z 19), punkty probne 95 z 95 "to samo"; `r2_p3.py`: przy 1-4 nowych wynikach prostokat mapy i srodki 19 gniazd bez zmian w 32 z 32 krokow (8 serii), po zniknieciu panelu mapa bez zmian; przycisk "Pokaz nowe wyniki (n): Plytka x" widoczny w calosci w 48 z 48 krokow. [W] wstrzykniecie R3 (panel z powrotem nad mapa): pada `test_n2_nowa_plytka_...`, a test geometrii `test_r2_p3_...` pada w 4 z 4 rozmiarow ("przesunietych gniazd 19 z 19"). Ciasnota panelu w rzadkim stanie - R2-D4; przesuniecie mapy przez komunikat ogolny z `main` - lista "poza paczka" (1.3). |
| P4 a (pomocnik `zamknij_piec(e)` maskuje falszywe pytanie; M5) | ZAMKNIETA | [W] diff: `zamknij_piec(e, *, pytanie: bool)` z asercja w 13 miejscach (`test_ui_rano.py` 7: 6 x True, 1 x False; `test_aplikacja_rano.py` 6: 2 x True, 4 x False) + nowy test `test_r2_p4_jedyna_nieznana_z_bez_projektu_...`; wstrzykniecie M5: 1 failed, 52 passed (runda 1: 63 passed). |
| P4 b (nadrabianie zaleglego stanu bez testu; M14) | ZAMKNIETA | [W] wstrzykniecie M14: pada `test_r2_p4_zalegly_stan_po_udanym_zapisie_nadrabia_zegar_okna` ("po 3.01 s ekran nadal bez decyzji"; runda 1: 31 passed). [PP] w przebiegu bez wstrzykniecia: stan nadrobiony po 1,06 s, 2 odczyty. |
| D1 ("Ponow teraz" zamyka piec bez pytania N3) | OTWARTA (odlozona) | wykonawca: 13.6; ocena w 1.2 |
| D2 (klawisze przy pytaniu N3) | ZAMKNIETA | [PP] przy pytaniu Enter i Enter numeryczny: 0 zmian, pytanie zostaje; Esc = pytanie znika + otwarta praca zolta; cyfry + Enter = wybor kuwety; po pytaniu skroty wracaja (Enter = "Rozlozona" 1 -> 2). [W] wstrzykniecia R4 (Esc nic nie robi) i R5 (Enter znow potwierdza): pada `test_r2_d2_...`. Ramka poranna nie wysyla klawiszy do okna (przeglad: zdarzenia ida przez kontroler). |
| D3 (napisy `wybierz_wpis`, `cofnij_wpis`) | ZAMKNIETA | [W] diff `statusy.py:262-263` + test `test_r2_d3_...` w 27 passed [PP] |
| D4 (brak zdarzenia "decyzja porzucona") | OTWARTA (odlozona) | wykonawca: 13.6; ocena w 1.2 |
| D5 (lista napisow niekompletna) | ZAMKNIETA | [W] sekcja 4: lista zgodna z diffem, 24 odwolania plik:linia sprawdzone |
| D6 (przycisk panelu nie mowi, ktora plytke pokaze) | ZAMKNIETA | panel nie ma przycisku; jedyny przycisk nazywa plytke ("Pokaz nowe wyniki (4): Plytka 4") - [PP] 48 z 48 krokow, [W] 3 zrzuty |
| D7 (`zapisz_liste` 934 ms) | ZAMKNIETA | [PP] 441-451 ms, 1 odczyt stanu; [W] 459 ms, plik listy bez zmian przy odmowie, lista kompletna (sekcja 2, proba 9); wstrzykniecie R6: pada `test_r2_d7_...` |
| D8 (atrapa `start_skanu`) | ZAMKNIETA | [PP] 655-658 ms, bez wyjatku (runda 1: 7443 ms + wyjatek) |
| D9 (`PYTANE ={`) | ZAMKNIETA | diff `ui/ekran_rano.py:58` |
| D10 (zrzuty nieobejrzane) | bez zmian kodu | zrzuty rundy 2: 12 z 12 obejrzane wg wykonawcy; recenzenci: [PP] 8 z 36 wlasnych zrzutow, [W] 4 z tych 36 (3 te same) + 1 z 12 wykonawcy |

### 1.2 Uwagi otwarte po rundzie 2 (wszystkie D)

| Nr | Waga | Gdzie | Scenariusz i dowod | Propozycja |
|---|---|---|---|---|
| D1 (r1) | D | `kontroler_api.py:3378-3393` (`ponow_polecenie`) | "Zamknij piec" klikniete przy zajetej bazie czeka w komunikacie; przed "Ponow teraz" dochodzi skan z praca zolta; ponowienie zamyka piec bez pytania N3. ODLOZONE przez wykonawce. Bezpieczne: zlozenie rzadkie (zajeta baza w chwili klikniecia + nowy skan przed ponowieniem), skutek odwracalny i widoczny (grupa "Prace bez rozstrzygniecia - NIE policzone w tym piecu", "Otworz piec ponownie"), ta sama klasa co klawisz ramki i polecenie kontrolera (sprawa 2 wlasciciela z rundy 1). Bez zmian kodu w rundzie 2 (diff). | Razem z decyzja wlasciciela w sprawie 2 (kto pyta: okno czy kontroler). |
| D4 (r1) | D | `kontroler_api.py` `zamknij`, `zamknij_komunikat` | "Rezygnuje - nie zapisuj" albo zamkniecie programu z wiszacym komunikatem "Decyzja NIE zostala zapisana": brak wpisu w dzienniku. ODLOZONE. Bezpieczne: komunikat (trwaly, poziom bledu) mowi wprost "tej decyzji nie ma w programie", rezygnacja jest kliknieciem; brakuje tylko sladu do diagnozy. Powod odlozenia (nowy typ zdarzenia czytany przez moduly spoza zakresu) uznaje za ostrozny i zasadny. | Osobne male zadanie po sprawdzeniu czytelnikow dziennika. |
| R2-D1 | D | `kontroler_api.py:4273-4280` (atrapa `ustaw_pule`), `aplikacja.py:1035-1051` | Polecenie `ustaw_pule` przy blokadzie EXCLUSIVE: 7403 ms (5538 ms przy RESERVED) i wyjatek `BladBazy` z `wykonaj`, atrapa i prawdziwa `Aplikacja` (7398 / 5522 ms) [PP]; `busy_timeout` po wyjatku 5000. Technik tego NIE napotka: w `ui/**` nie ma wywolania (`ui/czesci.py:31` - tylko lista `BEZ_OSOBY`), w `ramka/` 0 wystapien [W, grep]. Wykonawca opisal to w 13.2 jako niepoprawione. | Oslona jak w `start_skanu`, gdy okno dostanie przycisk puli; do tego czasu bez zmian. |
| R2-D2 | D | `kontroler_api.py:3819-3825` (`zapisz_liste(doba)`) | `zapisz_liste` Z doba przy EXCLUSIVE: 7857 ms, bez wyjatku (odmowa `lista_nie_zapisana`) [PP]. Okno wola polecenie bez doby (`ui/okno.py:555`, przycisk `ui/czesci.py:809` z argumentami `()`), a ten wariant ma 441-459 ms. Wariantu z doba nie ma w tabeli 13.2 wykonawcy. | `with self._czekanie_okna(CZEKAJ_POLECENIA_MS)` wokol `zapisz_do_dofrezowania(doba, ...)`, gdy powstanie przycisk listy doby. |
| R2-D3 | D | `ui/ekran_rano.py:874-885` (`_panel_zamkniecia`), `:848` (`_odpowiedz_zamkniecia`) | Dwuklik w "Zamknij piec" przy 1920 x 1080 i 1600 x 900, bez komunikatu nad piecem: drugie klikniecie trafia we "Wroc do rozstrzygania" - pytanie mignie i znika, otwiera sie pierwsza praca bez rozstrzygniecia, piec zostaje otwarty; przy 1536 x 864 i 1280 x 720 trafia w tlo pytania (pytanie zostaje) [PP]. Zrzut po dwukliku obejrzany [W]: naglowek "Piec 1 ... otwarty od 06:30" z przyciskiem "Zamknij piec", po prawej "Plytka 4 - gniazdo 3", znaczek "wybierz" i zdanie "porownaj je z praca i kliknij To ten projekt" - technik widzi, ze piec jest otwarty i ktora prace ma rozstrzygnac, ale tresci pytania (co sie stanie z praca po zamknieciu) nie przeczytal; trzecie klikniecie "Zamknij piec" pokazuje pytanie znowu, nigdy nie trafia w "mimo to". Bezpieczne (nic nie zapisane, 0 decyzji po 144 kliknieciach) i zgodne z wymaganiem p14-r2 p. 2 ("pod starym przyciskiem lezy Wroc do rozstrzygania albo nic klikalnego"). Wykonawca oddaje to wlascicielowi (13.7 nr 8). | Przyciski pytania nieaktywne przez ok. 0,5 s po jego pojawieniu sie (wtedy dwuklik zostawia pytanie na ekranie) - po decyzji wlasciciela. |
| R2-D4 | D | `ui/czesci.py:782-797` (`panel_nowego_wyniku`), `:948` (`_miejsce_panelu`), `ui/okno.py:656-660` | Wieczor, technik zostaje na plytce 1, nad mapa stoja 3 komunikaty (kolumna "Plytki tej zmiany" zaczyna sie w polowie okna) i czeka 4-6 nieobejrzanych wynikow z pytaniami / komunikatami: panel dostaje mniej miejsca niz potrzebuje - 1536 x 864: 269 px zamiast 307 (4 nowe), 278 zamiast 418 (6 nowych); 1280 x 720: 245 zamiast 265 [PP]. Zrzuty obejrzane [W]: `n2_1536x864_lista9_6_nowych` - ostatni wiersz tytulu ("numeru, Plytka 5") nachodzi na pierwszy wiersz opisu, opis urwany na "Plytka 4 (skan z"; `n2_1280x720_lista9_4_nowych` - opis urwany na "(skan z 19:35): pytanie"; lista kafelkow w pasku 68 px. Czytelne zostaja: przycisk "Pokaz nowe wyniki (n): Plytka x", naglowek z liczba i nazwami plytek, rada. Przy 1 komunikacie i 4 nowych wynikach (`n2_1536x864_lista1_4_nowych`) panel jest caly i czysty. Sygnal wymagany w p. 3 zlecenia (trwaly, nie do przeoczenia) nie ginie - ginie szczegol, ktory technik zobaczy po kliknieciu przycisku. Stan rzadki: co najmniej 3 komunikaty naraz i 4 wyniki bez obejrzenia. Wykonawca: "przy 4 i wiecej wynikach z pytaniami w oknie 1280 x 720 NIE mierzylem" (13.7 nr 9). | Opis w panelu ograniczyc do 2-3 plytek i "... i jeszcze n" (jak `NIEROZSTRZYGNIETE_DALEJ`) albo dac panelowi minimalna wysokosc z `sizeHint`; test: 6 nowych wynikow z pytaniami przy 1280 x 720 - wysokosc panelu >= potrzebna. |
| R2-D5 | D | `baza.py:531-536` (`Baza.kolumny`: `PRAGMA table_info` poza zamiana na `BladBazy`), `kontroler_api.py:3295-3300` | SYMULACJA [W, skrypt poprzednika `r2_male.py`]: pamiec kolumn polaczenia wyczyszczona recznie (stan "zaden zapis do tabeli w tym uruchomieniu"), blokada EXCLUSIVE: `przelacz_tryb` 1112 ms, `odrzuc_ponowny_skan` 1125 ms, `potwierdz_kuwete` 1164 ms -> odmowa `blad_polecenia` ("Blad programu albo dysku - nic nie zostalo zapisane"), BEZ "Ponow teraz", ponad limit 1 s; `ukruszona`, `ok`, `wybierz_kandydata`, `zamknij_piec` w tym samym stanie 657-673 ms i poprawny komunikat z "Ponow teraz"; `busy_timeout` 5000 po kazdym. W prawdziwym programie te 3 polecenia zaczynaja od wpisu do dziennika, a kolumny dziennika sa znane od startu (`aplikacja.py:564` zapisuje zdarzenie `program_start`) - sciezki nie umiem osiagnac bez czyszczenia pamieci; komunikat jest prawdziwy (nic nie zapisano), po ponownym kliknieciu polecenie przechodzi. Wykonawca opisal mechanizm (13.6, POTRZEBUJE 2). | W `_polecenie` traktowac `sqlite3.OperationalError` "locked / busy" jak `BladBazy` (jedna galaz `except`) albo poprawic `Baza.kolumny` w zadaniu wlasciciela pliku. |
| R2-D6 | D | `ui/napisy.py:42, 49`, `ui/czesci.py:37`, `ui/okno.py:869` | Po przeniesieniu panelu zostaly: nieuzywany napis `NOWY_WYNIK_POKAZ`, galaz `LOKALNE_POKAZ_NOWA`, ktorej nic juz nie wysyla (panel nie ma przycisku), komentarz "panel nad lista plytek i mapa". Rada panelu mowi "kliknij Pokaz nowy wynik", a przy kilku wynikach przycisk nazywa sie "Pokaz nowe wyniki (n): ..." (drobna niezgodnosc slow, przycisk stoi tuz nad panelem). | Usunac martwy kod przy najblizszej zmianie tych plikow. |

### 1.3 Poza paczka (do koordynatora - nie sa uwagami do PR #42)

1. Wieczor: komunikat ogolny "Ten sam projekt w dwoch gniazdach" (`konflikt_projektu`, bez `skan_id`), gdy dochodzi nad mape
   podczas ogladania plytki, przesuwa mape o 97-118 px, ochrona klikniec nieaktywna - 12 przesuniec na galezi i 12 na `main`,
   te same wartosci (99 / 97 / 118 px) [PP, `r2_p3b.py`]. Ta sama klasa bledu co P3, zachowanie z `main`, poza zakresem
   poprawki P3. Propozycja: osobne zadanie (komunikaty ogolne przychodzace w trakcie ogladania nie zmieniaja geometrii mapy
   albo wlaczaja ochrone klikniec).
2. `baza.py` `Baza.kolumny` - surowy `sqlite3.OperationalError` zamiast `BladBazy` (R2-D5; POTRZEBUJE 2 wykonawcy).
3. Komunikat `lista_nie_zapisana` po odmowie "Zapisz liste do pliku" zostaje na ekranie takze po tym, jak zapis samoczynny
   juz sie udal (plik 5 wierszy, komunikat nadal jest; znika po kliknieciu jego przycisku) [W, proba 9]. Zachowanie sprzed
   paczki (ten sam identyfikator komunikatu na `main`), nieszkodliwe.
4. Testy "petla okna" `test_ui_rano::test_k1_prawdziwy_kontroler_*` i `test_aplikacja_rano::test_k4_spacja_ramka_*` padly
   wykonawcy w przebiegach zbiorczych pod obciazeniem toru 1 (0,222-0,297 s przy progu 0,2 s), 5 z 5 osobno i w pelnym
   pytest przeszly (wg wykonawcy). U recenzentow oba pliki przeszly 2 razy przy dwoch pelnych pytestach innych paczek w tle
   (sekcja 2, proby 1 i 6). Czulosc tych testow na obciazenie PC to sprawa srodowiska, nie paczki.
5. Wykonawca nadpisal plik recenzenta `robocze\rec-p14\zrzuty_rec\n3_po_drugim_kliknieciu_1536x864.png` (zglosil sam, 13.6);
   kod kopii `rec-p14` nietkniety. Bez skutku dla oceny (proba dwukliku powtorzona w rundzie 2 [PP]).

## 2. Wlasne proby

| Nr | Kto | Polecenie / skrypt (katalog `robocze\rec-p14\runda2\`) | Wynik |
|---|---|---|---|
| 1 | [PP] | `seria_r2.sh` (log `testy_r2.log`), 21:23-21:27, po jednym pliku | `test_p14_baza_zajeta.py` 27 passed (33 s; czasy N1: EXCLUSIVE 661-672 ms, IMMEDIATE 287-307 ms, okno 672 ms, limit 1000 ms), `test_p14_ekran.py` 33 passed (39 s), `test_ui_wieczor.py -k test_6` 2 passed (40 s), `test_aplikacja.py -k test_f` 2 passed (7 s), `test_ramka.py -k test_k4` 3 passed (3 s), `test_ui_rano.py` 32 passed (49 s), `test_aplikacja_rano.py` 28 passed (36 s) |
| 2 | [W] | `mut_c.sh` (koniec strumienia B) | `test_ui_wieczor.py` caly: 89 passed, 86 s (w tym `test_6_*`) |
| 3 | [W] | `mut_c.sh` - 16 wstrzykniec zlecenia (logi `mut_A.log`, `mut_B.log`; diffy kazdego w `diffs\`) | **16 z 16 wykrytych.** Runda 1: M1a, M1b (`test_n1_decyzja_przy_zajetej_bazie_zostaje_do_ponowienia`), M2 (`test_n1_baza_czekanie_...`: 100 == 200), M3 (`test_n3_zamknij_piec_pyta_...`), M4 (`test_n2_nowa_plytka_...`), M5 (`test_r2_p4_jedyna_nieznana_...`), M6, M8, M12 (`test_n1_ponowna_decyzja_technika_...`), M9 (`test_poz9_rano_...[1600x900]`), M14 (`test_r2_p4_zalegly_stan_...`), M18 (`test_n1_spacja_na_prawdziwej_aplikacji_...`: 7,49 s). Nowe: R1 oslona `podaj_numer_plytki` usunieta (`test_n1_polecenie_klikane_...[plytka-podaj_numer_plytki-EXCLUSIVE]`), R2 kolejnosc przyciskow pytania przywrocona (`test_n3_zamknij_piec_pyta_...`), R3 panel z powrotem nad mapa (`test_n2_nowa_plytka_...`), R4 Esc w pytaniu nic nie robi (`test_r2_d2_...`). 0 wstrzykniec "nie weszlo", kopie przywrocone po kazdym (0 ostrzezen) |
| 4 | [W] | dodatkowe wstrzykniecia (poza 16) | 4 z 4 wykryte: R1b `dopusc_plytke` czyta tryb przed oslona, R1c `szczegoly_pracy` bez oslony, R5 Enter przy pytaniu potwierdza kuwete, R6 `zapisz_liste` czeka dwa razy |
| 5 | [W] | `mut_d.sh` (log `mut_D.log`) - R2 i R3 wprost na testy geometrii | R2 -> `test_r2_p2_...`: 4 failed, 4 passed (4 x "bez komunikatu": piec zamkniety po drugim kliknieciu w lewy dolny rog / srodek); R3 -> `test_r2_p3_...`: 4 failed z 4 (mapa przesunieta, 19 z 19 gniazd) |
| 6 | [W] | `test_ui_rano.py` + `test_aplikacja_rano.py`, potem `test_aplikacja.py` + `test_ramka.py -k "test_f or test_k4"` (log `testy_r2b.log`) | `test_ui_rano.py` + `test_aplikacja_rano.py`: 60 passed (32 + 28), 69 s; `test_aplikacja.py -k test_f` 2 passed (6 s); `test_ramka.py -k test_k4` 3 passed (3 s); `test_ui_wieczor.py -k test_6` 2 passed, 1 ostrzezenie (31 s). W tle szly 2 pelne pytesty innych paczek (tory 1 i 2) |
| 7 | [PP] | `r2_p1.py zajeta / wolna / aplikacja`, `proby_n1.py s1` (logi `r2_p1_*.log`, `proby_n1_s1.log`) | 31 polecen / odczytow wieczor + 27 rano przy EXCLUSIVE i IMMEDIATE; 5 polecen plytki 657-701 / 284-301 ms; `szczegoly_pracy` 663 ms, `projekty_kuwety` 662-715 ms, `zapisz_liste` 447-451 ms, `start_skanu` atrapy 655 ms, rano 1120 ms (668 wpis + 452 pelne odswiezenie), `Aplikacja`: 8 polecen 450-669 ms; `ustaw_pule` 7403 / 5538 ms + wyjatek (R2-D1), `zapisz_liste(doba)` 7857 ms (R2-D2); `busy_timeout` = 5000 po KAZDYM wywolaniu, takze po wyjatku; wolna baza: 43 wiersze identyczne z `main` |
| 8 | [W] | `r2_male_k3.py` cz. 1 (log `r2_male.log`) - pierwszy zapis w polaczeniu przy EXCLUSIVE, pamiec kolumn wyczyszczona | 8 polecen: 4 poprawnie (657-673 ms, "Ponow teraz"), `start_skanu` 677 ms ok, 3 z `blad_polecenia` w 1112-1164 ms (R2-D5); `busy_timeout` 5000 w 8 z 8 |
| 9 | [W] | `r2_male_k3b.py` cz. 2 (log `r2_male_p2.log`) - plik listy przy odmowie D7 | wolna baza: 3 pozycje, plik 4 wiersze (naglowek + 3); EXCLUSIVE: 459 ms, `lista_nie_zapisana`, plik bez zmian co do bajta, stan zalegly; po zwolnieniu i 1 obiegu zegara stan nadrobiony, plik 4 wiersze; po 4. decyzji zapis samoczynny: 5 wierszy; `zapisz_liste`: ok, 5 wierszy = 4 pozycje + naglowek, komunikat znika; `busy_timeout` 5000 |
| 10 | [PP] | `r2_p2.py` (log `r2_p2.log`, 16 zrzutow `zrzuty\n3_*`) | 144 klikniecia, piec zamkniety 0 razy; dwuklik 1920 / 1600 -> "Wroc" (R2-D3); klawisze (D2) |
| 11 | [PP] | `proby_przesuniecie.py`, `r2_p3.py`, `r2_p3b.py` (logi, 20 zrzutow `zrzuty\n2_*`) | 0 z 19 gniazd w 4 rozmiarach; 32 z 32 krokow bez zmiany mapy; panel 130 -> 307 px; ciasnota (R2-D4); 12 przesuniec przez komunikat ogolny na galezi i na `main` (poza paczka 1) |
| 12 | [W] | zrzuty obejrzane narzedziem Read | `n2_1536x864_lista9_6_nowych`, `n2_1280x720_lista9_4_nowych`, `n2_1536x864_lista1_4_nowych`, `n3_po_2_kliknieciu_1920x1080_bez_komunikatu` (poprzednika), `r2_n3_pytanie_1920x1080_bez_komunikatu` (wykonawcy: pytanie w 2 wierszach, "Zamknij piec mimo to" bialy po lewej, "Wroc do rozstrzygania" granatowy nad przyciskiem "Zamknij piec", nic nie uciete); [PP] 8 zrzutow (lista w sekcji 6) |
| 13 | [W] | git: zakres, schemat, ASCII, LF, stopki, log pelnego pytest | sekcja 4 |

Zakres (c) zlecenia recenzji - czekanie na baze:
- `busy_timeout` wraca do 5000: [PP] po kazdym wywolaniu proby 7 (31 polecen i odczytow wieczor + 27 rano, obie blokady), takze po wyjatku `ustaw_pule`; [W] w 8 z 8
  i 3 z 3 wywolan prob 8 i 9; M2 wykryte. `Baza.czekanie` (`baza.py:479-494`, `finally`) bez zmian w rundzie 2.
- Zapisy, ktore musza sie udac - przeglad diffu rundy 2 [W]: nowe bloki krotkiego czekania to 3 ODCZYTY (`_sesja_skanu` w
  `podaj_numer_plytki` `:3510`, `projekty_kuwety` `:3767`, `szczegoly_pracy` `:3877`) i wpis dziennika `start_skanu` atrapy
  (`:4260`, tylko testy / symulator; przy zajetej bazie brak wpisu, skan czeka normalnie). `zamknij_piec` (`:3588-3603`) i
  zapis wynikow skanow w `przetworz` - bez zmian w rundzie 2: zamkniecie pieca idzie przez `_polecenie` z czekaniem 200 ms
  (decyzja z rundy 1; przy zajetej bazie komunikat trwaly z "Ponow teraz", nic nie ginie - [W] proba 8: 673 ms, komunikat
  `polecenie_niezapisane`), zapis wynikow nieobjety krotkim czekaniem. Zapis listy: runda 2 NIE dodala krotkiego czekania -
  usunela drugi odczyt stanu przy odmowie.
- D7 - co skrocono: gdy pierwszy odczyt stanu w `zapisz_liste` nie udal sie z powodu zajetej bazy (`_stan_zalegly`),
  komunikat `lista_nie_zapisana` jest dokladany przez `_pokaz_komunikaty` bez drugiego `_odswiez` (`:3813-3816`; bylo 2 x
  ok. 0,46 s). Sciezka przy wolnej bazie i sam zapis pliku bez zmian; lista kompletna (proba 9: pozycje = wiersze pliku,
  przy odmowie plik nietkniety, po zwolnieniu bazy zapis samoczynny i reczny dzialaja).

## 3. Kryteria zlecenia (runda 2, `p14-r2.md`)

| Kryterium | Ocena |
|---|---|
| 1. Kazda uwaga P: test padajacy bez poprawki + proba recenzenta powtorzona (przed / po) | potwierdzone wlasna proba: P1 (R1, R1b, R1c; 7402-7455 ms + wyjatek -> 657-701 ms), P2 (R2; 2 z 8 zamkniec -> 0 z 144 klikniec), P3 (R3; 4 / 2 z 19 -> 0 z 19), P4 (M5, M14 wykryte); 16 z 16 wstrzykniec |
| 2. Zrzuty "po" (pytanie N3, panel) w 4 rozmiarach, kazdy obejrzany | potwierdzone przegladem: 12 plikow `r2_*` w `robocze\p14\zrzuty_r2\` istnieje, opis w 13.4 (3 grupy po 4 pliki, 12 z 12 obejrzane - wg wykonawcy); 1 z 12 obejrzany [W] + wlasne zrzuty recenzentow tych samych ekranow (36 plikow, 9 obejrzanych) zgodne z opisem |
| 3. Testy czasowe okna przechodza | potwierdzone wlasna proba: [PP] `test_6` 2, `test_f` 2, `test_k4` 3 passed; [W] `test_ui_wieczor.py` caly 89 passed; [W] `test_f` 2, `test_k4` 3, `test_6` 2 passed (1 ostrzezenie pytest, tresci nie czytalem) |
| 4. Raport: sekcja "Runda 2" + pelna lista napisow i ekranow wobec `main` | potwierdzone przegladem: 13.1-13.8 sa; lista napisow (p. 3: 15 pozycji + 7a, 7b) pokrywa kazdy napis z diffu `ui/napisy.py`, `ui/napisy_rano.py`, `statusy.py` (+ `ui/kandydaci.py`, `ui/okno_excela.py` z rundy 1), 24 odwolania plik:linia zgodne z HEAD; lista ekranow (p. 4: 9 pozycji) z dopiskami rundy 2 w poz. 3 i 7 |
| 5. Pelny pytest na kodzie koncowym: 0 failed | potwierdzone w logu wykonawcy (sekcja 4): 1891 passed, 9 skipped, 0 failed na 1117fef; po 1117fef zmienial sie tylko raport |
| p14.md p. 1 (b) okno odpowiada w 1 s (niespelnione w rundzie 1) | potwierdzone wlasna proba dla wszystkich polecen wysylanych z okna i klawiatury (440-715 ms; `start_skanu` rano na atrapie 1120 ms - wpis + pelne odswiezenie, bez zatrzymania skanu); poza limitem tylko polecenia, ktorych okno nie wysyla (R2-D1, R2-D2) i symulacja R2-D5 |
| p14.md kryt. 3 stare testy nieoslabiane | potwierdzone przegladem diffu rundy 2: 13 wywolan pomocnika dostalo jawne oczekiwanie (zaostrzenie), 3 testy paczki zmienione z powodu zmiany ukladu (kolejnosc przyciskow, panel bez przycisku) - wypisane w 13.5 |

## 4. Zakres plikow i zasady

- `git diff main...origin/e3/p14 --stat`: 22 pliki, wszystkie z listy zlecenia (5 opisow modulow, raport, `aplikacja.py`,
  `baza.py`, `kontroler_api.py`, `statusy.py`, 7 plikow `ui/`, 4 pliki testow). Runda 2: 13 plikow - `baza.py`,
  `aplikacja.py`, `session.py`, `session_rano.py` bez zmian w rundzie 2 (2 ostatnie bez zmian w calej paczce).
- Pliki nietykalne, `instrukcje/**`, `Ramki/etap3/**`, `instalacja/**`, `samokontrola.py`, `README.md`: 0 zmian.
- Schemat: `WERSJA_SCHEMATU` / `MIGRACJE` - 0 wystapien w diffie calej paczki; `baza.py` +18 wierszy (`czekanie`,
  `_ustaw_czekanie`).
- Nowe pliki (3: raport, 2 testy): 0 wierszy spoza ASCII; 0 bajtow CR we wszystkich 22 plikach (`tr -cd '\r' | wc -c`).
- Dane osobowe: w wierszach dodanych w rundzie 2 osoba tylko "Technik A" (5 wystapien), 0 sciezek uzytkownika; kuwety
  sztuczne 32xx; zrzuty - dane sztuczne.
- Commity rundy 2: 7, przedrostek `E3-P14 r2:` w 7 z 7, stopka `Co-Authored-By` w 7 z 7.
- Pelny pytest wykonawcy: `robocze\p14\pytest_r2_1117fef.log` (36 wierszy) konczy sie "1891 passed, 9 skipped, 2 warnings
  in 1489.58s (0:24:49)", 0 failed; `ciezkie.log`: START p14 20:41:01, KONIEC 21:05:54, kod 0. Commit 1117fef 20:35:04 (przed
  startem), `git diff 1117fef..5cd4199 --stat`: 1 plik (raport). 1891 = 1831 (`main`) + 60 testow paczki (27 + 33). Jedno z
  2 ostrzezen: `test_ui_wieczor::test_6` spelnione w pomiarze 2 (przerwa petli 222 ms, z tego 166 ms przestoj dysku) - pod
  obciazeniem; osobno i w calym pliku przechodzi (proby 1 i 2).
- Lista zmienionych napisow i ekranow (p. 3, p. 4, 13.8 raportu wykonawcy) - kompletna wobec diffu (kryterium 4); paczka
  instrukcji moze z niej korzystac. Dla A11d wazne zmiany rundy 2: panel "Nowy wynik czeka" w lewej kolumnie i bez wlasnego
  przycisku, kolejnosc przyciskow pytania ("Zamknij piec mimo to" po lewej, "Wroc do rozstrzygania" po prawej), Esc przy pytaniu.
- Odstepstwa wykonawcy opisane uczciwie (13.6): testy D7, D8, D2, D3 pisane razem z poprawka (bez czerwonego przebiegu) -
  wstrzykniecia R4, R5, R6 [W] pokazuja, ze D2 i D7 sa pilnowane; nadpisany plik recenzenta (poza paczka 5).

## 5. Do decyzji wlasciciela

Sprawy 1-7 z rundy 1 bez zmian (zadna nie blokuje). Nowe / zmienione w rundzie 2 - zadna nie blokuje scalenia:

8. R2-D3 - dwuklik w "Zamknij piec" odpowiada sam "Wroc do rozstrzygania" (pytanie nieprzeczytane, piec otwarty, otwarta
   praca do rozstrzygniecia). Mozna scalic bez decyzji: skutek bezpieczny. Wariant: przyciski pytania nieaktywne ok. 0,5 s.
9. R2-D4 - panel "Nowe wyniki czekaja" przy 3 komunikatach i 4-6 nieobejrzanych wynikach jest scisniety. Mozna scalic bez
   decyzji: sygnal zostaje; do poprawy razem z krotszym tekstem panelu (propozycja wykonawcy 13.7 nr 9).
10. D1 i D4 odlozone - mozna scalic bez decyzji (uzasadnienie w 1.2); D1 rozstrzyga sie razem ze sprawa 2 z rundy 1.
11. Przesuniecie mapy przez komunikat "Ten sam projekt w dwoch gniazdach" (zachowanie z `main`, 97-118 px) - poza paczka;
    do rozwazenia jako osobne zadanie przed T14, bo to ta sama klasa bledu, ktora w P3 dawala klikniecie w inne gniazdo.

## 6. Notatki robocze poprzedniego recenzenta tej rundy (21:11-21:27, bez zmian - zrodlo liczb prob P1, P2, P3)

- 21:11 start; kopia rec-p14 na 5cd4199, git status --short pusty; calosc main...origin/e3/p14: 22 pliki (te same co w rundzie 1).
- 21:20 przeglad diffu kodu rundy 2 (kontroler_api.py, statusy.py, ui/czesci.py, ui/ekran_rano.py, ui/okno.py) - zrobiony.
- PROBA proby_n1.py s1 na 5cd4199 (log runda2\proby_n1_s1.log): EXCLUSIVE rano podaj_numer_plytki 669 ms odmowa baza_zajeta
  z wpisem do ponowienia (runda 1: 7440 ms + wyjatek); RESERVED wieczor 4 polecenia plytki 291-527 ms; start_skanu atrapy 655 ms bez wyjatku (D8).
- PROBA r2_p1.py zajeta (log runda2\r2_p1_zajeta.log), atrapa, 31 polecen / odczytow wieczor + 27 rano, EXCLUSIVE i IMMEDIATE:
  5 polecen plytki EXCLUSIVE 657-701 ms (wieczor i rano), IMMEDIATE 284-301 ms; odmowa baza_zajeta, 1 komunikat do ponowienia,
  wykonaj nie rzuca, po zwolnieniu "Ponow teraz" ok=True 5 z 5 (obie blokady); szczegoly_pracy 663 ms -> None; projekty_kuwety
  662-715 ms -> (); zapisz_liste 447-451 ms; busy_timeout po KAZDYM wywolaniu = 5000 (takze po wyjatku ustaw_pule).
  Poza oslona zostaly: ustaw_pule (7403 ms EXCLUSIVE / 5538 ms IMMEDIATE + wyjatek BladBazy; atrapa i prawdziwa Aplikacja 7398 / 5522 ms)
  - w ui/ NIE ma przycisku, ktory je wysyla (grep: tylko lista BEZ_OSOBY); zapisz_liste(doba) 7857 ms bez wyjatku - okno wola
  zapisz_liste bez doby. start_skanu rano na atrapie przy EXCLUSIVE: 1120 ms (668 wpis + 452 pelne odswiezenie po zmianie "zajety").
- PROBA r2_p1.py wolna na galezi i na main_kopia (r2_p1_wolna_galaz.log / r2_p1_wolna_main.log): 43 wiersze odmow i skutkow
  5 polecen plytki, 2 odczytow i zapisz_liste przy WOLNEJ bazie - identyczne z main (diff -w pusty).
- PROBA r2_p1.py aplikacja (prawdziwa Aplikacja): start_skanu 655-669 ms, odswiez_pule 450, ponow_zapis 451, zapisz_liste 451,
  potwierdz_ponowny_skan 668, podaj_numer_plytki 665, przelacz_tryb 667, projekty_kuwety 668 ms; ustaw_pule 7398 ms + wyjatek.
- PROBA r2_p2.py (log runda2\r2_p2.log, zrzuty runda2\zrzuty\n3_*.png): 4 rozmiary x (bez komunikatu nad piecem / z komunikatem),
  9 punktow starego przycisku (srodek, 4 rogi, 4 srodki krawedzi), 2. i 3. klikniecie w to samo miejsce: piec ZAMKNIETY 0 razy
  (8 wariantow x 9 punktow x 2 klikniecia = 144 klikniecia); czesc wspolna starego przycisku z "Zamknij piec mimo to" 0 x 0 px w 8 z 8;
  ze "Wroc do rozstrzygania": 128x43 / 128x33 / 128x22 / 114x13 px (bez komunikatu), 0 x 0 (z komunikatem przy 1536 i 1280).
  2. klik bez komunikatu trafia we "Wroc" w 4 / 4 / 2 / 3 z 9 punktow (1920 / 1600 / 1536 / 1280), reszta w tlo pytania; 3. klik po
  "Wroc" trafia znow w "Zamknij piec" (pytanie wraca) - nigdy w "mimo to". Prawdziwy dwuklik (zdarzenie DblClick w to, co lezy pod
  kursorem): 1920 i 1600 bez komunikatu -> "Wroc": pytanie znika, otwiera sie praca zolta (Plytka 4 - gniazdo 3), piec otwarty;
  1536 i 1280 -> tlo pytania, pytanie zostaje. Z komunikatem nad piecem przy 1920 / 1600: dolna krawedz starego przycisku lezy na
  przycisku "Zamknij" komunikatu "Ramka poranna nie jest podlaczona" (2. klik zamyka ten komunikat; tak samo w rundzie 1).
  Przyciski pytania widoczne w calosci w 8 z 8 (niewidoczne_w_calosci = []). Decyzji / potwierdzen kuwet po 144 kliknieciach: 0.
  Klawisze (1536 x 864): bez pytania Enter = Rozlozona (0 -> 1), Backspace = cofnij; przy pytaniu Enter i Enter numeryczny: 0 zmian,
  pytanie zostaje; cyfry + Enter = wybor kuwety (dziala); Esc = pytanie znika + otwarta praca zolta; drugi Esc zamyka prace; potem
  Enter = Rozlozona (1 -> 2); po samoczynnym zniknieciu pytania (To ten projekt) Enter = Rozlozona (2 -> 3). Skroty wracaja.
- zrzuty obejrzane: n3_pytanie_1280x720_bez_komunikatu, n3_pytanie_1536x864_z_komunikatu, n3_po_2_kliknieciu_1920x1080_bez_komunikatu -
  pytanie w calosci, przyciski nie nachodza na nic, "Wroc do rozstrzygania" wyrozniony po prawej.
- PROBA proby_przesuniecie.py (runda 1) na 5cd4199 (log runda2\proby_przesuniecie.log): klik w stary srodek gniazda trafia w INNE
  gniazdo: 0 z 19 w 4 z 4 rozmiarow (runda 1: 4 / 2 / 0 / 0 z 19); wszystkie punkty probne 95 z 95 "to samo" w 4 rozmiarach; mapa y bez zmian.
- PROBA r2_p3.py (log runda2\r2_p3.log, 20 zrzutow runda2\zrzuty\n2_*.png): 4 rozmiary x (1 plytka na liscie / 9 plytek), nowe wyniki
  dochodza po jednym do 6 (czysta, do powtorzenia, ponowny skan z pytaniem, nie z trybu z pytaniem, bez numeru, do powtorzenia).
  Przy 1-4 nowych: prostokat mapy i srodki 19 gniazd bez zmian w 8 z 8 serii (32 z 32 krokow), ekran zostaje na plytce 1, panel rosnie
  130 -> 175 -> 238 -> 307 px (1280 x 720: 110 -> 149 -> 206 -> 265); po obejrzeniu wszystkich nowych panel znika, mapa bez zmian.
  Przycisk "Pokaz nowe wyniki (n): Plytka x" widoczny w calosci w 48 z 48 krokow, panel nie nachodzi na przycisk ani na kafelki.
  Kolejnosc "Pokaz nowy wynik": od najnowszej (5, bez numeru, 4, 3, 2) - nazwa plytki jest na przycisku (D6 zamkniete napisem).
  Kroki 5 i 6 mojej serii przesuwaja mape o 97-118 px - NIE przez panel: dochodzi komunikat ogolny "Ten sam projekt w dwoch
  gniazdach" (konflikt_projektu, skan_id None) nad mapa. PROBA r2_p3b.py na galezi i na main_kopia: 12 przesuniec w obu, te same
  wartosci (99 / 97 / 118 px), ochrona klikniec nieaktywna - zachowanie z main, poza zakresem P3 (uwaga do koordynatora).
  Ciasno: gdy nad mapa stoja 3 komunikaty (kolumna zaczyna sie w polowie okna) i czekaja 4-6 nowe wyniki z pytaniami, panel dostaje
  mniej miejsca niz potrzebuje (1536 x 864, 9 plytek: 269 px zamiast 307 przy 4 nowych; 1280 x 720: 245 zamiast 265; przy 6 nowych
  i 1 plytce: 278 zamiast 418 / 269) - wiersze tekstu nachodza na siebie, tytuly pytan dalszych plytek uciete; lista kafelkow zostaje
  w pasku 68 px (0-1 kafelek w calosci). Przycisk i naglowek "Nowe wyniki czekaja (n)" zostaja czytelne.
- zrzuty obejrzane: n2_1280x720_lista1_4_nowych (czysto, tekst caly), n2_1536x864_lista1_2_nowych (czysto), n2_1536x864_lista9_6_nowych,
  n2_1280x720_lista9_4_nowych, n2_1280x720_lista1_6_nowych (tekst panelu scisniety / uciety - opis wyzej).

WERDYKT: do scalenia (B 0 / P 0 / D 8)
