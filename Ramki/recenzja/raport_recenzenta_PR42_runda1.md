# Raport recenzenta - PR #42 (E3-P14: poprawki programu przed testami T7 i T14) - runda 1

Data: 20.11.2026. Zakres: `git -C <PC-katalog>\qc diff main...e3/p14`, main 9ba9e91, HEAD 05a568e (9 commitow, 22 pliki,
+1693 / -86). Recenzja prowadzona przez dwoch recenzentow: pierwszy 18:30-18:49 (sesja zginela przy restarcie PC), drugi
od 19:08 (przejecie: proby z logami przyjete bez powtarzania, reszta wykonana). Metoda: wlasny przeglad diffu, proby na
atrapie kontrolera i w oknie offscreen w kopii `<PC-katalog>\qc-wt\rec-p14` (detached 05a568e, po pracy czysta),
wstrzykniecia bledow, porownanie z `main` (kopia `robocze\rec-p14\main_kopia`). Uruchomiono: testy paczki, 6 istniejacych
plikow testow dotknietych modulow (po jednym), 12 wstrzykniec, 7 skryptow prob (13 przebiegow). Pelnego pytest nie uruchamiano (zasada).
Pliki robocze i logi: `<PC-katalog>\koordynator\robocze\rec-p14\`. Kazda liczba ponizej jest z pomiaru recenzentow, chyba
ze oznaczono "wg wykonawcy".

## 0. Werdykt i liczby

**Do scalenia po poprawkach.** B 0 / P 4 / D 10.

Rdzen paczki dziala: decyzja przy zajetej bazie nie ginie po cichu i nie zapisuje sie dwa razy (3 x "Ponow teraz" = 1
wiersz decyzji), okno odpowiada w 0,66-0,87 s, reguly liczenia pieca sa niezmienione (wynik identyczny z `main` dla dwoch
piecow), przyciski decyzji sa widoczne w 12 sprawdzonych rozmiarach okna. Do poprawy przed scaleniem: 5 polecen plytki
nadal zatrzymuje okno na 7,4 s i konczy sie wyjatkiem bez komunikatu (P1), drugie klikniecie w miejsce "Zamknij piec" trafia
w "Zamknij piec mimo to" i zamyka piec bez przeczytania pytania (P2), panel "Nowy wynik czeka" przesuwa mape pod reka
(P3), dwie luki w testach (P4).

## 1. Uwagi

| Nr | Waga | Gdzie | Scenariusz i dowod | Czego oczekuje od poprawki |
|---|---|---|---|---|
| P1 | P | `stanowisko/kontroler_api.py:3441-3460, 3475-3484, 3502` (`_sesja_skanu` / `_wieczorny` wolane PRZED `_polecenie`: `potwierdz_ponowny_skan`, `cofnij_zastapienie`, `dopusc_plytke`, `cofnij_dopuszczenie`, `podaj_numer_plytki`) | Technik klika "Tak, to ponowny skan" (albo "Dopusc plytke", podaje numer plytki, "Cofnij zastapienie"), gdy inny program trzyma baze na wylacznosc (ta sama blokada `BEGIN EXCLUSIVE`, ktorej uzywaja testy paczki). Odczyt `SELECT tryb FROM skany` idzie poza `try` i poza krotkim czekaniem: kontroler 7402-7455 ms i wyjatek `BladBazy` z `wykonaj` (4 polecenia zmierzone, `cofnij_dopuszczenie` - ta sama konstrukcja, z kodu); w oknie 7,37 s, wyjatek w slocie Qt idzie tylko na stderr (programu `sys.excepthook` nie ma). Technik widzi: okno stoi ponad 7 s, potem nic sie nie zmienia - pytanie zostaje, zadnego komunikatu, zadnego "Ponow teraz", decyzja nie zapisana. Po zwolnieniu bazy pytanie nadal jest i mozna kliknac jeszcze raz (decyzja nie przepada trwale). Przy blokadzie zapisu (RESERVED) te same polecenia dzialaja poprawnie: 292-323 ms i komunikat z "Ponow teraz". Raport wykonawcy podaje je jako "ida ta sama droga, nie mierzone". Logi: `proby_n1_s1.log`, `proby_ui_1.log` (U2). | Odczyt trybu skanu wewnatrz `_polecenie` (w `try`, pod `CZEKAJ_POLECENIA_MS`), tak zeby zajeta baza dawala odmowe `baza_zajeta` z komunikatem do ponowienia w limicie 1 s i zeby `wykonaj` nie rzucalo. Te 5 polecen dopisac do testu parametryzowanego `test_n1_polecenie_klikane_przy_zajetej_bazie_wraca_w_limicie_i_daje_sie_ponowic` (blokada EXCLUSIVE) i do tabeli "polecenie -> przed / po" w raporcie. |
| P2 | P | `stanowisko/ui/ekran_rano.py:874-885` (`_panel_zamkniecia`: kolejnosc i polozenie przyciskow), `:946-947` (panel pytania dokladany NAD naglowkiem pieca) | Piec z praca zolta, nad naglowkiem pieca nie ma innego komunikatu (ramka podlaczona albo komunikat o ramce zamkniety - zwykly stan pracy). Technik klika "Zamknij piec" dwa razy (dwuklik albo niecierpliwe drugie klikniecie). Pytanie pojawia sie w miejscu naglowka pieca, a przycisk "Zamknij piec mimo to" laduje pod kursorem: 1920 x 1080 - stary przycisk x 1219-1349, y 111-166, "mimo to" x 1158-1346, y 124-167 (wspolna czesc 128 x 43 px); 1600 x 900 - wspolna czesc 128 x 33 px; 1536 x 864 - 128 x 22 px; 1280 x 720 - 114 x 13 px. Drugie klikniecie w srodek starego przycisku ZAMYKA piec przy 1920 x 1080 i 1600 x 900 (piec otwarty = False), przy 1536 x 864 i 1280 x 720 srodek trafia w tlo pytania, a w przycisk trafia dolne 22 / 13 px. Pytania nikt nie przeczytal, a "domyslna" odpowiedz "Wroc do rozstrzygania" lezy z boku (x 942-1149). Z komunikatem nad piecem (4 rozmiary) wspolna czesc 0 px. Zlecenie p. 4: program pyta wprost i domyslna odpowiedzia jest powrot do rozstrzygania. Proba na dwoch kolejnych kliknieciach w oknie offscreen (`proby_dwuklik.py`, log `proby_dwuklik.log`); test paczki klika przyciski po nazwie. | Drugie klikniecie w miejsce "Zamknij piec" nie moze zamknac pieca: pod starym przyciskiem ma lezec "Wroc do rozstrzygania" albo nic klikalnego (np. zamiana kolejnosci, pytanie w miejscu niezmieniajacym polozenia naglowka, albo "Zamknij piec mimo to" nieaktywny przez czas ochrony po pojawieniu sie pytania). Test: prostokat `przycisk_zamknij_piec` sprzed klikniecia nie ma czesci wspolnej z `zamknij_mimo_tak` w 4 rozmiarach okna, bez komunikatu nad piecem; drugie klikniecie w to samo miejsce zostawia piec otwarty. |
| P3 | P | `stanowisko/ui/okno.py:818-821` (panel `panel_nowy_wynik` dokladany nad mapa), `ui/czesci.py` `panel_nowego_wyniku` | Technik oglada plytke 1 i siega po gniazdo; przychodzi wynik nastepnej plytki. Panel "Nowy wynik czeka" pojawia sie nad mapa, mapa ogladanej plytki zjezdza o 75 px i maleje (1536 x 864: 680 x 539 -> 680 x 464; srodek gniazda 2 z (812, 570) na (783, 597)), ochrona klikniec (A-P2) nie wlacza sie. Klikniecie w STARY srodek gniazda trafia w INNE gniazdo: 1536 x 864 - 4 z 19 gniazd (17 z 95 punktow probnych: srodek i 4 punkty w polowie promienia), 1600 x 900 - 2 z 19 (14 z 95), 1280 x 720 - 0 z 19 (10 z 95), 1920 x 1080 - 0 z 19 (0 z 95); przyklady 9 -> 13, 10 -> 14, 11 -> 16. Otwiera sie widok innej pracy, a nastepne "Ukruszona" / "OK" trafia do niej = zla pozycja na liscie do dofrezowania. Zlecenie (p. 3): zasada "nie podmieniaj mapy pod reka" zostaje. Test paczki sprawdza tylko, ze pokazana plytka sie nie zmienila. Log: `proby_przesuniecie.log`, `proby_ui_1.log` (U3). | Mapa ogladanej plytki nie zmienia polozenia ani rozmiaru, gdy panel sie pojawia, rosnie (kolejne wyniki) albo znika - albo na ten moment wlacza sie istniejaca ochrona klikniec i skrotow U / O / C. Test: srodki gniazd przed i po przyjsciu nowego wyniku przy 1536 x 864 i 1600 x 900 (te same albo ochrona aktywna). |
| P4 | P | testy: `testy/test_p14_ekran.py:296`, `testy/test_ui_rano.py:336`, `testy/test_aplikacja_rano.py:78` (pomocnik `zamknij_piec(e)`), `testy/test_p14_baza_zajeta.py` | 2 z 12 wstrzyknietych bledow przechodza wszystkie testy. (a) M5: z warunku `kontroler_api.py:1977` usuniete `and p["decyzja"] is None` (praca "nieznana" ze swiadomym "Bez projektu" liczona jako nierozstrzygnieta = falszywe pytanie przed "Zamknij piec" i falszywa grupa po zamknieciu): 63 passed (`test_p14_*` 31 + `test_ui_rano.py` 32). Pomocnik `zamknij_piec(e)` klika "Zamknij piec mimo to" zawsze, gdy pytanie jest - w 13 miejscach nie odroznia pytania slusznego od falszywego (np. `test_aplikacja_rano`: wg wykonawcy pytanie ma sie pojawic w 2 z 6 testow, w pozostalych 4 falszywe pytanie przeszloby niezauwazone). (b) M14: `_nadrob_stan` zawsze zwraca False (zalegly stan nigdy nie nadrabiany): 31 passed. Proba `proby_male.py`: zapis "Ukruszona" udany, odczyt stanu raz nieudany -> ekran pokazuje prace bez decyzji (w bazie 1 decyzja), po 1,15 s zegar okna pokazuje "ukruszona" (mechanizm dziala); z wylaczonym nadrabianiem po "Cofnij decyzje" (zapisane) ekran przez 2,25 s i 3 obiegi zegara nadal pokazuje "ukruszona" - technik widzi stan sprzeczny z baza. | (a) Pomocnik z jawnym oczekiwaniem (np. `zamknij_piec(e, pytanie=True / False)` z asercja obecnosci / braku pytania) w 13 miejscach + test: jedyna praca "nieznana" pieca ma "Bez projektu" -> `nierozstrzygniete_prace == ()`, brak pytania, brak grupy. (b) Test: zapis decyzji udany, odczyt stanu raz nieudany (baza zajeta) -> po `OKRES_NADRABIANIA_STANU_S` zegar okna pokazuje decyzje, `_stan_zalegly` False. |
| D1 | D | `kontroler_api.py:3376-3391` (`ponow_polecenie`), okno: przycisk `komunikat_ponow_polecenie` | "Zamknij piec" klikniete przy zajetej bazie czeka w komunikacie; w tym czasie dochodzi skan z praca zolta; "Ponow teraz" zamyka piec BEZ pytania N3 (proba S3f: nierozstrzygniete przed (), po [(plytka 5, gniazdo 3)], piec zamkniety). Rzadkie zlozenie (zajeta baza w chwili klikniecia + nowy skan przed ponowieniem), skutek odwracalny (grupa "Prace bez rozstrzygniecia", "Otworz piec ponownie"). | Ponowienie `zamknij_piec` z okna przez te sama sciezke co przycisk (z pytaniem) albo zdjecie wpisu, gdy zestaw skanow pieca zmienil sie od klikniecia. Razem ze sprawa 2 w sekcji 5. |
| D2 | D | `ui/ekran_rano.py:1036-1068` (klawisze), `:874-885` (panel pytania) | Pytanie "Zamknac piec mimo prac bez rozstrzygniecia?" nie przejmuje klawiszy: Enter = "Rozlozona" biezacej kuwety (zdarzen `kuweta_potwierdzona` 0 -> 1), Spacja = start skanu, Esc = nic; pytanie zostaje, piec otwarty (proba U4). Na pytanie da sie odpowiedziec tylko mysza; domyslna odpowiedz jest tylko wyrozniona kolorem i kolejnoscia. Bezpieczne dla pieca (zaden klawisz go nie zamyka), ale Enter wcisniety "na pytanie" zapisuje rozlozenie kuwety (cofa je Backspace). | Przy otwartym pytaniu: Esc = "Wroc do rozstrzygania", Enter nie potwierdza kuwety (uzgodnic z klawiatura ramki, ktora wysyla Enter). |
| D3 | D | `kontroler_api.py:3341-3352` (`_opis_polecenia`: `ST.PRZYCISKI.get(nazwa, nazwa)`), `statusy.py:222-260` | `wybierz_wpis` i `cofnij_wpis` (wybor krazka, pula per praca) nie maja napisu w `ST.PRZYCISKI` - komunikat N1 pokaze technikowi nazwe programisty: ""wybierz_wpis" - plytka 1, gniazdo 9 - decyzja NIE jest zapisana ..." (proba `proby_male.py`; dla "ukruszona": ""Ukruszona" - plytka 1, gniazdo 9"). Pozostale 23 polecenia z list ponawiania maja napis. | Dopisac napisy obu polecen (albo wziac napis przycisku z ekranu) + asercja w tescie: kazde polecenie z `PONAWIANE_Z_LICZB` i `DECYZJE_O_PRACY` ma napis. |
| D4 | D | `kontroler_api.py` `zamknij`, `zamknij_komunikat` (`:3783`) | Zamkniecie programu (albo "Rezygnuje - nie zapisuj") z wiszacym komunikatem "Decyzja NIE zostala zapisana": decyzja znika bez wpisu w dzienniku i bez pytania przy zamykaniu (proba S3j, "Ukruszona" na zielonej pracy: 0 wierszy decyzji, 0 zdarzen). Po restarcie praca zielona wyglada na nieruszona. Komunikat mowil o tym wprost, wiec to swiadome pominiecie, ale sladu dla diagnozy nie ma. | Zdarzenie dziennika "decyzja porzucona" (polecenie, praca, osoba) przy rezygnacji i przy zamknieciu z lista do ponowienia; do rozwazenia ostrzezenie przy zamykaniu programu. |
| D5 | D | raport wykonawcy `raporty/E3-P14_2026-11-20.md`, p. 3 | Lista zmienionych napisow dla A11d niekompletna wobec diffu: brak `statusy.py:270` `NAPIS_NIC_DO_PONOWIENIA` ("Tego polecenia nie ma juz na liscie do ponowienia (zostalo zapisane albo z niego zrezygnowano).") - technik widzi go po drugim kliknieciu "Ponow teraz". Niewymienione warianty: `MIEJSCE_KUWETA` (""Rozlozona" - kuweta 3221"), `MIEJSCE_POZA_GNIAZDEM` ("..., praca poza gniazdem"), `NIEROZSTRZYGNIETA_POZA` ("Plytka n, poza gniazdem (...)"), `NIEROZSTRZYGNIETE_DALEJ` ("; ... i jeszcze n" powyzej 8 prac), formy liczby `ZAMKNIJ_MIMO_ILE` ("2 prace sa", "5 prac jest"). Reszta listy (15 pozycji) i lista 9 ekranow zgodne z diffem `ui/napisy.py`, `ui/napisy_rano.py`, `statusy.py`, `ui/kandydaci.py`, `ui/okno_excela.py`. | Dopisac brakujace pozycje w rundzie 2 (bez zmiany kodu). |
| D6 | D | `ui/czesci.py` `panel_nowego_wyniku`, `ui/okno.py:401-404` (`_pokaz_nowa`) | Przy 3 nowych wynikach panel wymienia plytki w kolejnosci skanow ("Plytka 2, Plytka 3, Plytka 4"), a "Pokaz nowy wynik" otwiera najnowsza: kolejno 4, 3, 2 (proba U3); panel znika po obejrzeniu ostatniej. Zgodne ze starym przyciskiem nad lista ("Pokaz nowe wyniki (3): Plytka 4"), ale nowy przycisk nie mowi, ktora plytke pokaze. | Nazwa plytki na przycisku panelu albo kolejnosc od najstarszej nieobejrzanej. |
| D7 | D | `kontroler_api.py:3789-3808` (`zapisz_liste`) | "Zapisz liste do pliku" przy blokadzie EXCLUSIVE: 934 ms (limit 1 s) i odmowa `lista_nie_zapisana` z istniejacym przyciskiem ponowienia - nic nie ginie, ale zapas do limitu to 66 ms na tym PC; polecenia nie ma w tabeli wykonawcy. | Dopisac do tabeli i do testu czasu albo skrocic (czas wyglada na dwa odczyty stanu po ok. 0,46 s - przypuszczenie z kodu, niezmierzone osobno). |
| D8 | D | `kontroler_api.py:4230` `AtrapaKontrolera.start_skanu` | Atrapa: Spacja przy blokadzie EXCLUSIVE 7443 ms i wyjatek `BladBazy` (prawdziwa `Aplikacja` poprawiona i pilnowana testem - wstrzykniecie M18 wykryte). Dotyczy tylko testow i symulatora na atrapie. | Ta sama oslona co w `Aplikacja.start_skanu`. |
| D9 | D | `ui/ekran_rano.py:58` | `PYTANE ={` - zgubiona spacja przed `{` (wiersz zmieniony tylko przez to). | Przywrocic `PYTANE = {`. |
| D10 | D | kryterium 2 zlecenia (zrzuty) | Wykonawca obejrzal 3 z 13 zrzutow "przed" i 8 z 19 "po" (podane uczciwie jako odstepstwo). Recenzenci obejrzeli 19 z 19 "po" (odtworzone z HEAD: 19 z 19 rowne co do bajta plikom wykonawcy; drugi recenzent 13, w tym 9 z 11 pominietych przez wykonawce, pozostale 2 - 1920 x 1080 - pierwszy recenzent) i 6 z 13 wlasnych zrzutow pierwszego recenzenta: bez ucietych napisow, nakladania, pustych paneli i zlych kolorow stanu; jedyne ustalenia ze zrzutow to P2 i P3. 10 zrzutow "przed" nie obejrzal nikt. | Nic do poprawy w kodzie. |

Podejrzenia z przegladu ZAMKNIETE bez uwagi: `ui/okno.py:395` (`plytka(skan_id).moze_zastapic` - wiersz 389 wychodzi, gdy
plytki nie ma w stanie); `zamknij_piec` + `_po_zamknieciu_pieca` (po zatwierdzeniu transakcji nie ma zapisow do bazy -
komunikat "NIE wykonano" przy zamknietym piecu nie powstanie); grupowanie jednakowych komunikatow a "Ponow teraz" (wpis na
liste jest jeden na prace / polecenie, tekst zawiera miejsce).

## 2. Wlasne proby

| Nr | Polecenie / skrypt (katalog `robocze\rec-p14\`) | Wynik |
|---|---|---|
| 1 | `py.cmd -m pytest -q -p no:cacheprovider testy/test_p14_baza_zajeta.py testy/test_p14_ekran.py` | 31 passed, 85 s |
| 2 | istniejace pliki testow, po jednym: `test_ui_rano.py` / `test_aplikacja_rano.py` / `test_baza.py` / `test_session_wieczor.py` / `test_session_rano.py` / `test_ui_wieczor.py` | 32 / 28 / 70 / 64 / 73 / 89 passed, 0 failed (84 s / 73 s / 6 s / 103 s / 14 s / 162 s) |
| 3 | `mutacje.sh` + `mutacje2.sh` - 12 wstrzykniec (logi `mutacje.log`, `mutacje2.log`) | 10 wykrytych: M1a udane polecenie nie zdejmuje wpisu, M1b ponowienie wykonuje 2 razy, M2 `busy_timeout` nie wraca, M3 pytanie N3 pomijane, M4 panel N2 nie znika, M6 "Rezygnuje" nie zdejmuje wpisu, M8 ponowienie przy zajetej bazie gubi wpis, M12 decyzje o tej samej pracy nie zastepuja sie, M9 lista kuwet nie znika w niskim oknie, M18 Spacja bez krotkiego czekania. 2 NIEWYKRYTE: M5 (63 passed), M14 (31 passed) - uwaga P4 |
| 4 | `proby_n1.py s1` - polecenia okna przy blokadzie EXCLUSIVE i RESERVED (`proby_n1_s1.log`) | EXCLUSIVE: 4 polecenia plytki 7402-7455 ms + wyjatek (P1); odrzuc_ponowny_skan 673, przelacz_tryb 669-678, pomin_skan 686, otworz_piec_ponownie 661, cofnij_przypisanie 683, przypisz_recznie 667 ms - komunikat z "Ponow teraz"; zamknij_pytanie 451, zamknij_komunikat 455, wybierz_operatora 448, wybierz_kuwete 451, ustaw_kolejnosc 448 ms; zapisz_liste 934 ms. RESERVED: polecenia plytki 292-323 ms, komunikat |
| 5 | `proby_n1.py s3` - ponawianie po zmianie stanu (`proby_n1_s3.log`) | 3 x "Ponow" przy zajetej bazie -> 1 komunikat; po zwolnieniu 3 x "Ponow" -> 1 wiersz decyzji (2 odmowy); decyzja odwrotna kliknieta wprost zdejmuje komunikat, ponowienie starej = odmowa, 1 wiersz; skan zastapiony -> odmowa sesji z powodem, 0 wierszy dla starej pracy; bez osoby -> `brak_operatora`, komunikat zostaje; inna osoba -> decyzja z nowa osoba; wieczor -> rano: komunikat zostaje, ponowienie dziala (1 wiersz); zmieniona kuweta -> `kuweta_zmienila_sie`, komunikat znika; zamkniecie programu: 0 wierszy, 0 zdarzen (D4); "Zamknij piec" + nowy skan (D1); baza zajeta 6 s: klikniecia 0,67-0,87 s, 1 komunikat, `przetworz` 0 ms; po bloku `busy_timeout` = 5000 |
| 6 | `proby_ui.py` U1-U6 - okno offscreen (`proby_ui_1.log`, `proby_ui_2.log`, 13 zrzutow w `zrzuty_rec\`) | U1 klawisz U przy zajetej bazie 0,68 s, komunikat z dwoma przyciskami widoczny w calosci przy 1536 x 864, 2 klikniecia "Ponow" -> 1 wiersz; U2 = P1; U3 = P3, D6; U4 = D2 (pytanie znika samo po rozstrzygnieciu pracy; bez osoby "Zamknij piec mimo to" nieaktywny); U5 poz. 9 w 12 rozmiarach (1920 x 1080 ... 1240 x 640): 0 przyciskow niewidocznych w calosci, wolne pod "To ten projekt" 173-433 px, lista kuwet widoczna od wysokosci 1000; U6 rano dwa komunikaty N1 naraz przy 1536 x 864: nic niewidocznego, oba ponowione |
| 7 | `proby_n3.py` na galezi i na `main_kopia` (`n3_galaz.json`, `n3_main.json`, po ok. 1740 wierszy) | roznica TYLKO w nowym polu `nierozstrzygniete_prace`; liczniki, kompletne, braki, `wynik_pieca`, `stan_punktow`, kuwety identyczne. Piec T14: kompletne 3228, 3235; braki 3221, 3242. Piec pokazowy (3 plytki): 24 kompletne, 8 brakow; nierozstrzygniete 2 dwuznaczne + 3 nieznane, nowe pole 4 prace (bez "nieznanej" z "Bez projektu") |
| 8 | `proby_przesuniecie.py` (`proby_przesuniecie.log`) | P3: klik w stary srodek gniazda trafia w inne gniazdo - 4 z 19 (1536 x 864), 2 z 19 (1600 x 900), 0 z 19 (1280 x 720, 1920 x 1080) |
| 9 | `proby_pula.py` - falszywe "NIE zapisano" przy pisarzu w tle, SYMULACJA drugim polaczeniem (`proby_pula.log`) | bez pisarza 0 z 40; transakcje krotkie co 5 ms 0 z 60; co 20 ms 0 z 60; 100 ms co 1 s 0 z 60; 300 ms co 1 s 0 z 60; 600 ms co 2 s 4 z 60; 1500 ms co 5 s 2 z 60 (kazde zdjete "Ponow teraz": 4 i 5 klikniec); przy czekaniu 5000 ms 0 z 40 (max czas polecenia 1354 ms). Czas polecenia mediana 15-41 ms, max 355 ms |
| 10 | `proby_male.py` (`proby_male.log`) | (1) bez napisu w `ST.PRZYCISKI`: `cofnij_wpis`, `wybierz_wpis` (D3); (2) nadrabianie zaleglego stanu dziala: po udanym zapisie i nieudanym odczycie ekran po 1,15 s pokazuje decyzje; z wylaczonym nadrabianiem stan sprzeczny z baza zostaje (P4 b) |
| 11 | zrzuty wykonawcy odtworzone z HEAD (`P14_ZRZUTY`, 19 passed) | 19 z 19 rowne co do bajta; obejrzane 19 z 19 "po" (D10) |
| 12 | zakres, ASCII, LF, dane osobowe, stopki (git) | 22 pliki, wszystkie z listy; 0 plikow nietykalnych; 3 nowe pliki: 0 wierszy spoza ASCII; 0 bajtow CR w 22 plikach; `WERSJA_SCHEMATU` / `MIGRACJE` 0 wystapien w diffie; osoba w testach "Technik A"; stopka w 9 z 9 commitow |
| 13 | `proby_dwuklik.py` - drugie klikniecie w miejsce "Zamknij piec", 4 rozmiary x (z komunikatem nad piecem / bez) (`proby_dwuklik.log`) | bez komunikatu: piec ZAMKNIETY po drugim kliknieciu przy 1920 x 1080 i 1600 x 900, otwarty przy 1536 x 864 i 1280 x 720 (wspolna czesc przyciskow 128 x 43 / 128 x 33 / 128 x 22 / 114 x 13 px); z komunikatem: 4 z 4 otwarty, wspolna czesc 0 px (P2) |


Falszywe "NIE zapisano" przy zwyklej pracy z `pula_wpisow = true` - oszacowanie. Z kodu: drugi pisarz to watek
"pula-katalog" (`aplikacja.py:761`, wlasne polaczenie); rusza przy starcie, "Odswiez pule", zmianie trybu, zmianie doby,
zmianie pliku wspolczynnikow i bledzie analizy - nie po kazdym wyniku. Indeks pisze transakcje per folder
(`indeks.py:241, 298`), plik wspolczynnikow jedna transakcja na caly plik (`wspolczynniki.py:298`). Z proby 9: transakcje
do 300 ms nie daja ani jednego falszywego komunikatu; daja je dopiero transakcje 600 ms i dluzsze, i tylko dla klikniec
trafiajacych w czas ich trwania. Wniosek: przy odswiezaniu puli komunikat moze sie pojawic sporadycznie (kilka okazji na
zmiane, tylko gdy pojedyncza transakcja trwa ponad ok. 0,3 s), kazdy zdejmuje jedno "Ponow teraz", nic nie ginie. Czasu
transakcji prawdziwego `KatalogPul` na duzym katalogu NIE mierzylem (proba jest symulacja).

`Baza.czekanie(ms)`: schemat nietkniety; `busy_timeout` wraca po bloku i po wyjatku (`finally`; M2 wykryte; po probie S3
5000); zagniezdzenie z poprzednim pomocnikiem `_krotkie_czekanie_na_baze` (150 ms, zdarzenia ramek) w obu kolejnosciach
konczy sie wartoscia 5000 (przeglad); polaczenia uzywa tylko watek okna (watki puli otwieraja wlasne). Sciezki, ktore
musza sie zapisac: migracja - przy `otworz`, przed jakimkolwiek krotkim czekaniem (nieobjeta); zapis wynikow skanow w
`przetworz` - nieobjety; "Zamknij piec" - objety, przy zajetej bazie komunikat z "Ponow teraz" (nic nie ginie, po
zatwierdzeniu brak dalszych zapisow); zapis listy do pliku - objety przez odswiezenie stanu, przy zajetej bazie odmowa
`lista_nie_zapisana` z istniejacym przyciskiem, a zapis samoczynny nadrabia zegar okna (mechanizm bez testu - P4 b).

## 3. Kryteria zlecenia

| Punkt / kryterium | Ocena |
|---|---|
| p. 1 N1 (a) decyzja nie ginie po cichu | potwierdzone wlasna proba dla decyzji o pracy, kuwety, pieca, kandydata (proby 4, 5, 6; M1a, M1b, M6, M8, M12) |
| p. 1 N1 (b) okno odpowiada w 1 s, inne zapisy z klikniecia | NIESPELNIONE dla 5 polecen plytki przy blokadzie EXCLUSIVE (P1); pozostale 0,45-0,93 s |
| p. 1 tabela "polecenie -> przed / po" | czesciowo: 9 wierszy zmierzonych przez wykonawce, reszta "nie mierzone" (w tym 5 polecen z P1) |
| p. 2 poz. 9 / D8 przyciski widoczne w 4 rozmiarach | potwierdzone wlasna proba (4 rozmiary zlecenia + 8 dodatkowych, 0 usterek; M9 wykryte); technik przy otwartej pracy widzi biezaca kuwete z "Rozlozona" / "Cofnij", traci tylko liste pozostalych kuwet do zamkniecia pracy |
| p. 3 N2 trwaly sygnal nowej plytki | potwierdzone wlasna proba (panel z pytaniami i komunikatami, M4 wykryte); warunek "bez zabierania ogladanej pracy" naruszony przesunieciem mapy (P3) |
| p. 4 N3 pytanie przed zamknieciem, grupa po zamknieciu, reguly bez zmian | potwierdzone wlasna proba (proba 7: liczenie identyczne z `main`; M3 wykryte); luka testu M5 (P4 a); pytanie da sie ominac drugim kliknieciem w to samo miejsce (P2); sciezki bez pytania: D1 i sprawa 2 w sekcji 5 |
| p. 5 poz. 8 nowy skan nie wyglada na sprawdzony | potwierdzone zrzutem i przegladem ("Plytka 2 - nowy skan, czeka na odpowiedz", kafelek "poprzedni skan") |
| p. 6 poz. 6 przycisk skanu | potwierdzone zrzutem i przegladem; dzialanie Spacji bez zmian (M18: oslona przy zajetej bazie pilnowana testem) |
| p. 7 poz. 1, 2, 3, 4, 7; poz. 5, 10, 11, 12 nieruszone | potwierdzone przegladem diffu i zrzutami |
| kryt. 1 test padajacy bez poprawki dla p. 1-6 | potwierdzone wstrzyknieciami dla N1, bazy, N2, N3, poz. 9 (10 z 12); poz. 8 i poz. 6 - przegladem testow; czerwone na `main` 11 z 11 i 18 z 19 - wg wykonawcy, niesprawdzone |
| kryt. 2 zrzuty przed / po obejrzane | czesciowo (D10) |
| kryt. 3 stare testy nieoslabiane | asercje bez zmian (13 klikniec przepietych na pomocnik: 7 + 6, potwierdzone diffem); pomocnik maskuje falszywe pytanie (P4 a) |
| kryt. 4 testy czasowe okna | `test_ui_wieczor.py` caly: 89 passed (w tym `test_6_*`); `test_aplikacja::test_f`, `test_ramka::test_k4` - wg wykonawcy, niesprawdzone |
| kryt. 5 pelny pytest 0 failed | wg wykonawcy 1861 / 9 / 0 na 3efb95f; na koncowym HEAD 05a568e pelnego przebiegu NIE bylo (dopisany 1 test, komentarz, opisy) - do sprawdzenia przez koordynatora |

## 4. Zakres plikow i zasady

- 22 pliki, wszystkie z listy zlecenia; `session.py`, `session_rano.py` bez zmian; pliki nietykalne, `instrukcje/**`,
  `README.md`, `samokontrola.py`, `instalacja/**`, `Ramki/etap3/**` - 0 zmian.
- `baza.py`: tylko `Baza.czekanie` i `_ustaw_czekanie` (+18 wierszy); `WERSJA_SCHEMATU`, `MIGRACJE` nietkniete.
- Nowe pliki (2 testy, raport): ASCII, LF. Pliki istniejace: 0 bajtow CR.
- Dane osobowe: w testach, raporcie i zrzutach tylko dane sztuczne ("Technik A", kuwety 32xx-34xx); nazw folderow i
  plikow zlecen brak.
- Commity: 9, przedrostek `E3-P14:`, po polsku bez znakow diakrytycznych, stopka w 9 z 9.
- Kontrakt kontrolera: zmiany addytywne (`ponow_polecenie`, 2 rodzaje komunikatow, `StanRano.nierozstrzygniete_prace`);
  `WERSJA_KONTRAKTU` bez zmiany - przyjete przez wykonawce domyslnie, nie blokuje.

## 5. Do decyzji wlasciciela

Raport wykonawcy (p. 8) oddaje 7 spraw. Zadna nie blokuje scalenia.

1. N3 - regula liczenia (praca nierozstrzygnieta "nie liczy sie", jej zab trafia do brakow jako "nie wyszedl z pieca"):
   mozna scalic bez decyzji - regula jest ta sama co na `main` (proba 7), paczka dodaje tylko pytanie i nazwanie prac.
2. N3 - klawisz "Zamknij piec" ramki porannej i polecenie kontrolera nie pytaja: mozna scalic bez decyzji - zachowanie
   ramki jest takie jak na `main`, po zamknieciu ekran nazywa prace i jest "Otworz piec ponownie". Dopoki wlasciciel nie
   zdecyduje, poprawka N3 dziala tylko dla przycisku na ekranie; ta sama klasa: "Ponow teraz" (D1).
3. N3 - "nieznana" ze swiadomym "Bez projektu" poza lista, choc licznik A6 ja liczy: mozna scalic bez decyzji - widoczna
   jest tylko roznica liczb (znaczek "nieznana: 3", lista 2 prace w piecu pokazowym); zachowania nie pilnuje zaden test (P4 a).
4. N1 - czas czekania 200 ms: mozna scalic bez decyzji - proba 9: 0 falszywych komunikatow przy transakcjach do 300 ms,
   4 z 60 i 2 z 60 przy 600 ms i 1500 ms; nic nie ginie. Do obserwacji w trybie cienia, jak proponuje wykonawca.
5. N1 - wariant "ponawia osoba": mozna scalic bez decyzji - wariant bezpieczny (zadnego zapisu bez klikniecia, brak
   podwojnego zapisu w probach 5 i 6); slabe miejsce to zamkniecie programu z wiszacym komunikatem (D4).
6. Poz. 9 - lista kuwet znika przy otwartej pracy w oknach nizszych niz 1000 punktow: mozna scalic bez decyzji - biezaca
   kuweta i jej przyciski zostaja, lista wraca po "Zamknij [Esc]"; 12 rozmiarow bez usterek.
7. Teksty nowych komunikatow i przyciskow: mozna scalic bez decyzji - do zatwierdzenia razem z pozostalymi napisami;
   lista dla A11d wymaga uzupelnienia (D5).

## 6. Notatki robocze (zapis przyrostowy obu recenzentow, bez porzadkowania)

- start: przeczytane recenzent.md, wspolne.md, p14.md, czesci raportu PR40 (B1, D8, sekcja 7, proby).
- przeglad diffu kodu (baza.py, kontroler_api.py, aplikacja.py, statusy.py, ui/**) - zrobiony.
- pomiar: `py.cmd -m pytest -q -p no:cacheprovider testy/test_p14_baza_zajeta.py testy/test_p14_ekran.py` -> 31 passed, 85 s.
- pomiar: `testy/test_ui_rano.py` -> 32 passed, 84 s.
- do sprawdzenia proba (podejrzenia z przegladu):
  - `potwierdz_ponowny_skan`, `cofnij_zastapienie`, `dopusc_plytke`, `cofnij_dopuszczenie`, `podaj_numer_plytki` czytaja baze
    (`_sesja_skanu` / `_wieczorny`, kontroler_api.py:3441-3523) PRZED `_polecenie`, poza `try` i poza krotkim czekaniem -
    przy blokadzie EXCLUSIVE: 5 s i wyjatek w slocie okna? (raport wykonawcy: "ida ta sama droga, nie mierzone").
  - `zamknij_piec`: `_po_zamknieciu_pieca` po zapisie w tej samej funkcji - BladBazy po zapisie = komunikat "NIE wykonano", choc piec zamkniety?
  - grupowanie jednakowych komunikatow (`grupuj`, okno.py:75) a przycisk "Ponow teraz" (tylko pierwszy id), "Rezygnuje" (wszystkie).
  - pytanie N3: Enter / Spacja / Esc ida do okna (Enter = "Rozlozona"), pytanie nie przechwytuje klawiszy.
- pomiar: `testy/test_aplikacja_rano.py` -> 28 passed, 73 s.
- PROBA S1 (`robocze\rec-p14\proby_n1.py s1`, log `proby_n1_s1.log`): blokada EXCLUSIVE (ta sama co w testach paczki):
  `potwierdz_ponowny_skan` 7455 ms + WYJATEK BladBazy z `wykonaj`; `dopusc_plytke` 7435 ms + wyjatek; `podaj_numer_plytki`
  7402 ms (wieczor) / 7440 ms (rano) + wyjatek; `cofnij_zastapienie` 7437 ms + wyjatek; zadnego komunikatu do ponowienia.
  Przy blokadzie RESERVED (BEGIN IMMEDIATE) te same polecenia: 292-323 ms, odmowa `baza_zajeta`, komunikat z "Ponow teraz".
  Pozostale przy EXCLUSIVE: odrzuc_ponowny_skan 673 ms (komunikat), przelacz_tryb 669-678 ms (komunikat), pomin_skan 686,
  otworz_piec_ponownie 661, cofnij_przypisanie 683, przypisz_recznie 667 (komunikaty); zamknij_pytanie 451, zamknij_komunikat
  455, wybierz_operatora 448, wybierz_kuwete 451, ustaw_kolejnosc 448 (ok, stan zalegly); zapisz_liste 934 ms (odmowa
  lista_nie_zapisana - blisko limitu 1 s); atrapa `start_skanu` 7443 ms + wyjatek (tylko atrapa; Aplikacja poprawiona).
- PROBA S3 (log `proby_n1_s3.log`): 3 x "Ponow" przy zajetej bazie -> 1 komunikat (id zmienia sie przy kazdej probie:
  do_ponowienia:2, :3, :4); po zwolnieniu 3 x "Ponow" -> 1 wiersz decyzji (drugi i trzeci: odmowa); decyzja odwrotna
  kliknieta wprost zdejmuje komunikat, ponowienie starego = odmowa, 1 wiersz; skan zastapiony -> ponowienie = odmowa sesji
  z powodem, 0 wierszy dla starej pracy; bez osoby -> brak_operatora, komunikat zostaje; inna osoba -> decyzja z nowa osoba;
  wieczor -> rano: komunikat zostaje i da sie ponowic w trybie rano (1 wiersz); zamkniecie programu z wiszacym
  komunikatem (Ukruszona na ZIELONEJ pracy): 0 wierszy decyzji, 0 wpisow dziennika o porzuconej decyzji;
  "Rozlozona": wprost zdejmuje komunikat, 1 wpis kuweta_potwierdzona; zmieniona kuweta -> kuweta_zmienila_sie, komunikat znika;
  "Zamknij piec" czekajacy + nowy skan z praca nierozstrzygnieta -> "Ponow teraz" zamyka piec BEZ pytania N3;
  baza zajeta 6 s: klikniecia 0,67-0,87 s kazde, 1 komunikat, przetworz 0 ms; po bloku busy_timeout = 5000.
- Zrzuty: 19 zrzutow "po" odtworzone z HEAD (`P14_ZRZUTY`, 19 passed) - 19 z 19 rowne co do bajta plikom wykonawcy.
  Obejrzane przeze mnie 15 (wszystkie 11 nieobejrzanych przez wykonawce + 4 inne). Uwagi w sekcji zrzutow.
  - `ui/ekran_rano.py:58` `PYTANE ={` - zgubiona spacja (drobiazg).
  - `ui/okno.py:395` `self._stan.plytka(skan_id).moze_zastapic` - None, gdy plytki nie ma w stanie?

Przejecie recenzji (drugi recenzent, od 19:08):

- kopia rec-p14: cofniete wstrzykniecie M6 w kontroler_api.py (`git checkout -- .`), `git status --short` pusty.
- proby poprzednika z logami przyjete bez powtarzania (proby_n1_s1.log, proby_n1_s3.log, proby_ui_1.log, proby_ui_2.log).
- `ui/okno.py:395` (podejrzenie None) - ZAMKNIETE przegladem: wiersz 389 wychodzi, gdy plytki nie ma w stanie.
- seria wstrzykniec (mutacje.log + mutacje2.log): M1a, M1b, M2, M3, M4 - test paczki pada; M5 (pytanie N3 takze o prace
  rozstrzygniete swiadomie) - 63 passed, NIE wykryte (test_p14_* + test_ui_rano.py); M6, M8, M12, M9 - test pada.
- z logu U2 (okno, "Tak, to ponowny skan" przy EXCLUSIVE): 7,37 s, wyjatek BladBazy w slocie Qt (stderr), pytanie zostaje,
  zadnego komunikatu; `sys.excepthook` w programie nie ma (tylko dzien_skanera.py) - technik nie widzi nic.
- z logu U3 (N2): panel "Nowy wynik czeka" przesuwa mape o 75 px w dol i zmniejsza ja (1536x864: 680x539 -> 680x464;
  srodek gniazda 2 z (812,570) na (783,597)); klik w stare miejsce gniazda przy 1536x864 nie trafia w gniazdo;
  ochrona klikniec po przyjsciu wyniku nieaktywna. Kolejnosc "Pokaz nowy wynik" przy 3 nowych: 4, 3, 2 (od najnowszej).
- z logu U4 (N3): Enter przy otwartym pytaniu = "Rozlozona" biezacej kuwety (0 -> 1), Spacja = start skanu, Esc nic;
  pytanie zostaje; piec otwarty. Pytanie znika samo po rozstrzygnieciu pracy.
- wstrzykniecia dokonczone (mutacje2.log): M14 (stan zalegly nigdy nie nadrabiany) - 31 passed, NIE wykryte; M18 (Spacja bez
  krotkiego czekania na Aplikacja) - test pada. Razem 12 wstrzykniec: 10 wykrytych, 2 niewykryte (M5, M14). Kopia czysta.
- PROBA N3 liczenie (proby_n3.py na galezi i na main_kopia; n3_galaz.json / n3_main.json, ok. 1740 wierszy kazdy): roznica
  TYLKO w nowym polu `nierozstrzygniete_prace`; liczniki, kompletne, braki, wynik_pieca, stan_punktow, kuwety - identyczne
  (piec T14: kompletne 3228, 3235; braki 3221, 3242; piec pokazowy: 24 kompletne, 8 brakow; nierozstrzygniete 2 + 3,
  nowe pole 4 prace - bez "nieznanej" ze swiadomym "Bez projektu").
- PROBA N2 przesuniecie mapy (proby_przesuniecie.py, log proby_przesuniecie.log): panel "Nowy wynik czeka" przesuwa mape
  ogladanej plytki (y 244 -> 319; 1280x720: 179 -> 234), ochrona klikniec nieaktywna. Klik w STARY srodek gniazda trafia
  w INNE gniazdo: 1536x864 - 4 z 19 gniazd (17 z 95 punktow probnych), 1600x900 - 2 z 19 (14 z 95), 1280x720 - 0 z 19
  (10 z 95), 1920x1080 - 0 z 19 (0 z 95). Przyklady: 9->13, 10->14, 11->16.
- PROBA pula (proby_pula.py, log proby_pula.log; SYMULACJA: drugie polaczenie pisze transakcje BEGIN IMMEDIATE o zadanym
  czasie; technik = polecenie ok / cofnij co ok. 70 ms, 60 polecen na wariant): bez pisarza 0 z 40; krotkie transakcje co
  5 ms - 0 z 60 (max czas polecenia 355 ms); co 20 ms - 0 z 60; 100 ms co 1 s - 0 z 60; 300 ms co 1 s - 0 z 60 (max 347 ms);
  600 ms co 2 s - 4 z 60 falszywych "NIE zapisano" (kazde zdjete 1 kliknieciem "Ponow teraz"); 1500 ms co 5 s - 2 z 60
  (5 klikniec "Ponow teraz"); to samo przy czekaniu 5000 ms - 0 z 40 (max czas polecenia 1354 ms). "Stan zalegly po
  poleceniu": 0 we wszystkich wariantach. Pierwszy przebieg (pisarz BEZ przerwy miedzy transakcjami): ponawianie nie
  przechodzilo ponad 100 s - proba przerwana przeze mnie, wariant nierealistyczny (zastapiony przerwa 5 ms).
- z kodu: watek "pula-katalog" (aplikacja.py:761) rusza przy starcie, "Odswiez pule", zmianie trybu, zmianie doby, zmianie
  pliku wspolczynnikow, bledzie analizy - NIE po kazdym wyniku; indeks pisze transakcje per folder (indeks.py:241, 298),
  plik wspolczynnikow jedna transakcja na caly plik (wspolczynniki.py:298) - czasu tej transakcji nie mierzylem.
- test_baza.py: 70 passed (6 s).
- pliki: 22 zmienione, wszystkie z listy zlecenia; nietykalnych 0; WERSJA_SCHEMATU / MIGRACJE w diffie 0 wystapien;
  3 nowe pliki ASCII (0 wierszy spoza ASCII) i LF (0 bajtow CR we wszystkich 22 plikach); osoba w testach "Technik A";
  stopka Co-Authored-By w 9 z 9 commitow.
- `wybierz_wpis`, `cofnij_wpis` nie maja napisu w ST.PRZYCISKI (kontroler_api.py `_opis_polecenia`: `ST.PRZYCISKI.get(nazwa, nazwa)`).
- lista napisow w raporcie wykonawcy (p. 3) wobec diffu: brak `statusy.NAPIS_NIC_DO_PONOWIENIA`; warianty nie wymienione:
  `MIEJSCE_KUWETA` / `MIEJSCE_POZA_GNIAZDEM`, `NIEROZSTRZYGNIETA_POZA`, `NIEROZSTRZYGNIETE_DALEJ`, formy `ZAMKNIJ_MIMO_ILE`.
- test_session_wieczor.py 64 passed (103 s); test_session_rano.py 73 passed (14 s); test_ui_wieczor.py 89 passed (162 s).
- PROBA male (proby_male.py): `wybierz_wpis` / `cofnij_wpis` bez napisu przycisku; nadrabianie stanu dziala (1,15 s),
  wylaczone - ekran sprzeczny z baza po 2,25 s.
- PROBA dwuklik (proby_dwuklik.py): drugie klikniecie w miejsce "Zamknij piec" zamyka piec przy 1920x1080 i 1600x900,
  gdy nad naglowkiem pieca nie ma komunikatu (uwaga P2).
- zrzuty wykonawcy "po" obejrzane przez drugiego recenzenta: 13 (poz9 1536 / 1280 / 1600, p8 1280, p7 pytanie / tak / nie /
  popraw, p1 po skanie plytki 2, p5 scenariusz / zamkniety, n3 pytanie, poz6) - bez usterek wygladu.
- sprzatanie: kopia rec-p14 czysta (`git status --short` pusty); wlasny proces python zawieszonej proby puli zatrzymany.

WERDYKT: do scalenia po poprawkach (B 0 / P 4 / D 10)
