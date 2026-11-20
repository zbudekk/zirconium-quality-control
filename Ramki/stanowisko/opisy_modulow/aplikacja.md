# aplikacja - program "Stanowisko": kontroler, kontrakt dla okna i tabela statusow (paczka E3-A3a, 17.11.2026)

**Co robi.** Spina `scanner` -> `silnik` -> `session` / `baza` w jeden program bez udzialu czlowieka: plik STL w folderze skanera -> analiza w osobnym procesie -> zapis w sesji wieczornej -> stan dla ekranu. Sam niczego nie rysuje - ekran wieczorny (`stanowisko/ui/**`) buduje paczka A3b na kontrakcie z `kontroler_api.py`. Trzy pliki:

| Plik | Rola |
|---|---|
| `stanowisko/kontroler_api.py` | KONTRAKT dla okna: typy stanu, polecenia, sygnaly, `lacznik_qt`; `KontrolerSesji` (wspolna czesc: stan z `session`, polecenia o decyzjach); `AtrapaKontrolera` (dane sztuczne, bez skanera i silnika) |
| `stanowisko/aplikacja.py` | `Aplikacja` - prawdziwy kontroler (scanner, silnik, pula, restart, zamkniecie); `main()` - plik startowy (`uruchom_stanowisko.bat`) |
| `stanowisko/statusy.py` | JEDNA tabela statusow, kolorow i napisow dla technika (Z8, Z9); teksty komunikatow, pytan i przyciskow |

Testy: `testy/test_kontroler_api.py` (wspolny test kontraktu: ten sam zestaw dla atrapy i prawdziwej aplikacji), `testy/test_aplikacja.py`.

## Kontrakt dla okna (A3b)

**Co okno dostaje.** `kontroler.stan() -> StanAplikacji` (zamrozone obiekty, zwykle dane, pole `wersja` rosnie):
- `operator`, `operatorzy`, `wymaga_operatora`, `doba`, `zmiana`, `tryb`;
- `plytki` - skany biezacej doby roboczej (`Plytka`): `status` skanu (przyjety / do_powtorzenia / zastapiony / niezgodny_uklad / plytka_nie_z_trybu / blad), `aktywna`, `numer`, `uklad` (nazwa do `uklad.wczytaj` - geometria mapy), `gniazda` (wszystkie gniazda ukladu, takze puste), `poza_gniazdem`, `liczniki`, `zielonych`, `dozwolone` (polecenia majace sens dla plytki), wlasne `komunikaty` i `pytania`; `biezaca_plytka` = ostatni skan;
- `Gniazdo`: `nr`, `status` (klucz `statusy.STATUSY`), `kolor` (klasa koloru jak w `session`: zielony / czerwony / zolty / szary / pomaranczowy / zatwierdzona_ok / None), `rgb` (`#rrggbb`), `podpis`, `prace`;
- `Praca` (widok pracy): `status`, `kolor`, `rgb`, `podpis`, `opis`, `status_programu` (ocena sprzed decyzji), `decyzja`, `operator`, `sha16`, `kuweta`, `zeby`, `krazek`, `ubytki`, `ubytek_max_mm`, `blad_inspekcji`, `na_liscie` ("ten zab jest juz na liscie": `ta_praca`, skan, doba, zmiana, gotowy `tekst`), `dozwolone` (`ukruszona` / `ok` / `cofnij`); szczegoly po kliknieciu: `kontroler.szczegoly_pracy(praca_id)` -> ubytki z rozmiarem, uwagi, kandydaci, `plik_podgladu` (`silnik.wczytaj_podglad`: punkty i odchylki gniazda do obrazu odchylek);
- `do_dofrezowania` (pozycje tej doby) i `do_dofrezowania_biezaca` (wszystkie otwarte): `PozycjaListy`;
- `pytania` (`Pytanie`: `ponowny_skan` z `liczba_decyzji` i `liczba_ukruszonych`, ktore przestana obowiazywac; `plytka_nie_z_trybu`; `brak_numeru_plytki` z `numery`) - kazde ma `odpowiedzi` = przyciski (`polecenie`, `napis`, `argumenty`) do `kontroler.wykonaj(...)`;
- `komunikaty` (`Komunikat`: `rodzaj`, `poziom` info / ostrzezenie / blad, `tytul`, `tekst`, `skan_id`, `gniazda`, `trwaly`): `niezgodny_uklad`, `skan_do_powtorzenia`, `blad_inspekcji`, `blad_analizy`, `plik_zajety` ("czeka na zwolnienie"), `plik_niedostepny`, `plik_zmieniony`, `plik_odrzucony`, `skan_juz_jest`, `pula_pusta`, `pula_brak_folderu`, `folder_skanera_niedostepny`, `silnik_nie_startuje`, `baza_zajeta`, `brak_operatora`, `pusta_lista_operatorow`, `nowa_zmiana`, `wznowiono`, `konflikt_projektu`, `odmowa` ...;
- `analiza` (`Postep`: etap, udzial 0-1) albo None, `kolejka` (`w_toku`, `czeka`, `wstrzymane`, `razem`), `pula` (`folder`, `wspolczynnik`, `liczba_stl`, `stan`, `napis`), `skaner` (`dostepny`, `zajete`, `startow_skanu`, `czeka_na_skan`).

**Co okno wysyla** (kazde polecenie zwraca `Odpowiedz(ok, tekst, kod, dane)`; odmowa to odpowiedz i komunikat w stanie, nigdy wyjatek): `wybierz_operatora(nazwa)`, `ukruszona(praca_id)`, `ok(praca_id)`, `cofnij(praca_id)`, `potwierdz_ponowny_skan(skan_id)`, `odrzuc_ponowny_skan(skan_id)`, `cofnij_zastapienie(skan_id)`, `dopusc_plytke(skan_id)`, `cofnij_dopuszczenie(skan_id)`, `podaj_numer_plytki(skan_id, numer)`, `zamknij_pytanie(id)` ("pozniej"), `zamknij_komunikat(id)`, `start_skanu()` (Spacja), `ustaw_pule(folder, wspolczynnik)`, `odswiez_pule()`, `zamknij()`, `zapisz_liste(doba=None)`, `ponow_zapis()`; `wykonaj(nazwa, *argumenty)` wola polecenie po nazwie. Zle argumenty = odmowa `zle_argumenty`, nigdy wyjatek.

**Sygnaly.** `lacznik = kontroler_api.lacznik_qt(kontroler)`: `stan_zmieniony(object)`, `postep(object)`, `komunikat(object)`, `pytanie(object)`, `zamkniety()`; zegar lacznika co 30 ms wola `kontroler.przetworz()` (bez tego zdarzenia skanera i silnika czekaja w kolejkach). Bez Qt: `kontroler.subskrybuj(funkcja)` + wlasne wywolania `przetworz()`.

**Czego oknu nie wolno.** Siegac do `session` / `baza` / `scanner` / `silnik` z pominieciem kontrolera; trzymac wlasnych kolorow i napisow statusow (tylko `statusy.py` i pola stanu); pokazywac sciezek i nazw plikow (stan ich nie zawiera - poza `pula.folder` i `skaner.folder`, ktore sa ustawieniami); zmieniac obiektow stanu; wolac kontrolera z innego watku; otwierac okien modalnych (`exec`) w slotach sygnalow - zagniezdzona petla okna dostarcza wtedy nowszy stan przed koncem obslugi starszego (stan o nizszej `wersja` trzeba pominac); importowac Qt na poziomie modulu w pliku startowym.

**Miejsce na ekran.** `aplikacja.utworz_okno(kontroler, lacznik)` importuje pakiet `stanowisko.ui` i wola `ui.utworz_okno(kontroler, lacznik)` (okno Qt, jeszcze niepokazane); dopoki pakietu nie ma, `main()` pokazuje okno zastepcze z tekstem stanu. `closeEvent` okna nie musi niczego robic: `main()` wola `kontroler.zamknij()` po wyjsciu z petli (i przez `aboutToQuit`).

**Atrapa.** `AtrapaKontrolera()` - prawdziwa `Sesja` na bazie w katalogu tymczasowym, bez skanera i silnika: `symuluj_skan(rodzaj, numer=, gniazda=, projekty=)` (rodzaje: zwykla, czysta, do_powtorzenia, niezgodny_uklad, nie_z_trybu, bez_numeru, blad), `symuluj_postep`, `symuluj_komunikat(rodzaj)`, `scenariusz_pokazowy()`; pliki podgladu sztuczne (ten sam format, co z silnika). `py -3.12 -m stanowisko.aplikacja --atrapa` pokazuje okno na tych danych. `sztuczny_wynik(...)` i `kolory_oczekiwane(...)` - dane i prawda dla testow. Od rundy 2 czesc "zywa" atrapy dziala jak w prawdziwym kontrolerze (lista nizej) - test `test_p6_atrapa_i_prawdziwy_kontroler_daja_te_same_odpowiedzi`.

## Zmiany kontraktu po rundzie 2 (recenzja PR #20; `WERSJA_KONTRAKTU = 2`, wszystkie addytywne)

Okno zbudowane na wersji 1 dziala bez zmian; ponizsze trzeba obsluzyc, zeby pokazac nowe stany.

| Uwaga | Zmiana | Co z tym robi okno |
|---|---|---|
| P4 | Praca jest zielona TYLKO, gdy kolor z sesji jest zielony ORAZ `status_inspekcji == "ok"` ORAZ dopasowanie ma znany status (`zielony` / `zolty`). Inspekcji brak / pominieta -> `status = "nie_sprawdzono"`; nieznany status inspekcji albo dopasowania -> `status = "nieznany"`; w obu przypadkach `kolor = "zolty"`, `rgb` zolty, praca nie liczy sie do `zielonych` ani `liczniki["zielony"]`. Skan aktywny bez koloru pracy -> `nieznany` (D3). Nowe funkcje `statusy.kolor_pracy(kolor, status)`, parametr `status_pracy(..., status_match=)`; stale `INSPEKCJA_ZIELONA`, `DOPASOWANIA_ZIELONE`. | rysowac wg `status` / `rgb` (bez zmian); nie wnioskowac zielonego ze `status_programu` |
| P6 | Atrapa: te same odmowy i kody co prawdziwy kontroler: `ustaw_pule` -> `zly_wspolczynnik` (nie liczba, NaN, `bool`, poza 0,9-1,5; przecinek dziesietny dozwolony), `zle_argumenty` (folder nie jest napisem / sciezka); `ustaw_pule(None)` -> `ok`, `dane="nieustawiona"`, `pula.stan = "nieustawiona"`; `ustaw_pule` / `odswiez_pule` -> `ok`, `dane="liczenie"`, `pula.stan = "liczenie"`, wynik liczenia w nastepnym `przetworz()` (w obu kontrolerach `dane` = stan puli po poleceniu; dawniej atrapa `dane=16`, prawdziwy `None`). Nieudany `start_skanu` -> odmowa `start_skanu_nieudany`. `AtrapaKontrolera(liczba_stl=0)` startuje z pula `pusta`. Nowe: `symuluj_pule(stan, liczba)` (nieustawiona / liczenie / gotowa / pusta / brak_folderu), `symuluj_kolejke(czeka, wstrzymane, silnik_gotowy)` (komunikaty `pula_pusta` / `pula_brak_folderu` / `silnik_nie_startuje`), `symuluj_skaner(dostepny, zajete, start_udany)` (`folder_skanera_niedostepny`, `plik_zajety`), `symuluj_blad_zapisu(ile, przyczyna)`. Stala `STANY_PULI`, `WSPOLCZYNNIK_MIN`, `WSPOLCZYNNIK_MAX` w `kontroler_api`. | obsluzyc stany puli `liczenie` / `pusta` / `brak_folderu` / `nieustawiona`, `kolejka.wstrzymane > 0`, `skaner.dostepny = False`, odmowe startu skanu |
| P7 | 17. polecenie `zapisz_liste(doba=None) -> Odpowiedz(dane=<nazwa pliku>)`: lista biezaca `do_dofrezowania_biezaca.csv` (albo `do_dofrezowania_<RRRR-MM-DD>.csv`) w folderze danych (folder bazy, `dane/`), bez nazw zlecen; odmowa `lista_nie_zapisana` (dysk) albo `zle_argumenty`. Kontroler zapisuje plik listy biezacej SAM po kazdej zmianie listy; `StanAplikacji.lista_zapisana` = czas ostatniego zapisu; blad zapisu = komunikat `lista_nie_zapisana`. Napis przycisku `statusy.PRZYCISKI["zapisz_liste"]`. | przycisk "Zapisz liste do pliku" (opcjonalny - plik i tak powstaje) |
| P1, P8 | Nowy komunikat TRWALY `rodzaj = "blad_zapisu"` o stalym `id = kontroler_api.ID_BLAD_ZAPISU` (`"blad_zapisu"`, `trwaly=True`, poziom `blad`): wynik analizy nie dal sie zapisac (pelny dysk, blad dysku); zostaje do udanego zapisu albo zamkniecia przez technika (wraca tylko z nowym takim skanem). `baza_zajeta` (id `baza_zajeta:wyniki`) znika sam po udanym zapisie. Nowe pole `StanAplikacji.niezapisane` - krotka `Niezapisany` (`sha16`, `rodzaj` wynik / blad, `przyczyna` blad_zapisu / baza_zajeta, `napis` "nie zapisano - blad zapisu", `od`, `proby`, `numer`, `uklad`, `prac`) i `Kolejka.niezapisane` (czesc `wstrzymane`). 18. polecenie `ponow_zapis()` - proba zapisu na zadanie (`ok` = nic nie czeka; inaczej odmowa z kodem przyczyny, `dane` = ile czeka). | pokazac pozycje "nie zapisano" (np. obok plytek) i przycisk "Ponow zapis" (`statusy.PRZYCISKI["ponow_zapis"]`) |
| D1 | Polecenia i `wykonaj` NIGDY nie rzucaja wyjatku: zly typ / zla liczba argumentow -> `Odpowiedz(ok=False, kod="zle_argumenty")` + komunikat; nieoczekiwany blad polecenia -> `kod="blad_polecenia"`. Identyfikatory musza byc liczbami calkowitymi (nie `bool`), napisy - napisami. | nie lapac wyjatkow |
| D2 | `liczniki` (stan i plytka), `konflikty` (krotka slownikow, `miejsca` - krotka) oraz `ubytki` / `kandydaci` w `SzczegolyPracy` to `ZamrozonySlownik` (podklasa `dict` tylko do odczytu: zmiana = `TypeError`); caly `StanAplikacji` ma `hash`. Czyta sie je jak dotad. | nie zmieniac |
| D6 | `stan.pytania` / `stan.komunikaty` = otwarte (do okienek); `Plytka.pytania` / `Plytka.komunikaty` = pelny stan plytki, pozycje zamkniete przez technika maja nowe pole `ukryte=True`. | okienka tylko ze `stan.*` |
| D7 | `wybierz_operatora(None)` = nikt nie jest wybrany (technik odchodzi): `Odpowiedz(ok=True, kod="wylogowano")`, `stan.operator = None`, decyzje odmawiane (`brak_operatora`) do wyboru osoby. Napis przycisku `statusy.PRZYCISK_WYLOGUJ`. | opcjonalny przycisk "Odchodze od stanowiska" |
| D12 | `kontroler_api.wczytaj_podglad(plik)` (plik z `SzczegolyPracy.plik_podgladu`) zamiast `silnik.wczytaj_podglad`. | obraz odchylek przez kontrakt |
| - | Nowe klucze `statusy.KOMUNIKATY`: `blad_zapisu`, `zle_argumenty`, `blad_polecenia`, `lista_nie_zapisana`, `lista_zapisana`, `wylogowano`; `statusy.NAPISY_NIEZAPISANE`. Nowe rodzaje prac danych sztucznych (`sztuczny_wynik`): `zielony_bez_inspekcji`, `zielony_pominieto`, `zielony_nowa_inspekcja`, `zielony_nowe_dopasowanie`. | - |

## Poranek - kontrakt w wersji 3 (E3-A7, 18.11.2026; wszystko addytywne - okno wieczorne dziala bez zmian)

**Tryb.** `stan.tryb` = `wieczor` / `rano`. Zmienia go tylko czlowiek poleceniem `przelacz_tryb(tryb)` (Z1; bez osoby); wybor trafia do dziennika (`zdarzenia`, typ `tryb_zmieniony`), wiec po restarcie programu wraca ostatni tryb (`Aplikacja(ust, tryb=None)` / `AtrapaKontrolera(tryb=None)` = z dziennika, domyslnie `wieczor`). Skan dostaje tryb przy obsludze zdarzenia obserwatora w `przetworz` (watek okna); skan w kolejce zostaje w swoim trybie (przelaczenie w trakcie analizy nie zmienia sesji, do ktorej idzie wynik - test na `Aplikacja`). W trybie `rano` wynik i blad analizy ida do `session_rano.SesjaRano.przyjmij_wynik` / `przyjmij_blad` (piec otwiera sie sam - wymaganie A6; blad rano tez ma wpis `blad_analizy_rodzaj`), polecenia plytki (`podaj_numer_plytki`, `potwierdz_ponowny_skan`, `cofnij_zastapienie`, `cofnij_dopuszczenie`) ida do sesji, ktora obsluguje skan (wg `skany.tryb`); `dopusc_plytke` rano odmawia (A6 runda 2 - plytke nie z trybu sie pomija).

**`stan.rano` (`StanRano`, tylko w trybie `rano`)** - piec biezacy otwarty, a gdy go nie ma - ostatnio zamkniety piec z jawnym id, takze z poprzedniej doby (z `wynik` "Zamknij piec"; recenzja PR #26, P1); przy otwartym piecu `ostatni_zamkniety` = `StanRano` ostatnio zamknietego pieca bez plytek (lista do Excela nadal na ekranie): `sesja_pieca_id`, `plan_id`, `nr_w_dniu`, `otwarto`, `zamknieto`, `zamknal`, `otwarty`, `z_poprzedniej_doby`; `plytki` (`Plytka` jak wieczorem + `pominieta`, `na_ramce`; gniazda `Gniazdo` z `prace` = `PracaRano`; `podpis` gniazda = numer kuwety albo napis statusu; `liczniki` - po klasie pracy porannej; `dozwolone`: `podaj_numer_plytki`, `potwierdz_ponowny_skan` / `odrzuc_ponowny_skan`, `cofnij_zastapienie`, `cofnij_dopuszczenie`, `pomin_skan` (tylko skan, ktory blokuje), `cofnij_pominiecie`); `liczniki`, `nierozstrzygniete`, `kompletne` / `braki` (`ZlecenieRano` z `BrakujacyPunkt`; w otwartym piecu prowizoryczne), `poprawki` (`PoprawkaRano`), `konflikty`, `zajety` (`analiza_trwa` - skan w analizie, w kolejce albo wynik czeka na zapis; `skanowanie_trwa` - od "start skanu" do pierwszego pliku, najwyzej `LIMIT_SKANOWANIA_S` = 180 s, albo plik skanera w zapisie; None), `blokady` (napisy dla osoby: najpierw `zajety`, potem wlasne dla braku numeru, dwoch skanow z jednym numerem - ponowny skan albo nowy wsad - i konfliktu, pozostale - tekst A6 z numerem skanu zamienionym na plytke i godzine), `ostrzezenia`, `inne_otwarte_piece`, `dozwolone` (`zamknij_piec` - tylko bez blokad i bez `zajety`; `zamknij_piec_i_przenies` - przy `nowy_wsad`; `cofnij_przeniesienie` - piec powstaly z przeniesienia; `otworz_piec_ponownie` - ostatni piec zamkniety), `nowy_wsad` (`NowyWsad`: plytki, skany - A6 runda 4), `kolejnosc`, `kuwety` (`KuwetaRano`: kuweta, prac, plytki, potwierdzona, biezaca, braki, `gniazda` ((skan_id, gniazdo) prac liczonych do `prac`) - te same reguly co plan ramki A6, plus plytka okragla, ktora rozklada sie wedlug ekranu), `kuweta_biezaca` (STALA: zostaje, dopoki lezy na plytkach pieca; zmienia ja tylko osoba - Enter, Backspace, numer, kolejnosc; B1), `kuweta_do_cofniecia` (ostatnia potwierdzona), `obwodka(skan_id)` (numery gniazd biezacej kuwety na plytce - okno tylko je rysuje, P4), `braki_biezace` (lista brakow ze wszystkich piecow - z pamieci, liczona od nowa po zdarzeniach zmieniajacych stan punktow: polecenie spoza `NIE_RUSZA_PUNKTOW`, skan wieczorny, nowa doba, zapis innego polaczenia do bazy - `PRAGMA data_version`; P2), `piece` (doby), `ramka` / `excel` (do A12: False). Blad czesci porannej przy budowie stanu nie zatrzymuje odswiezania (zostaje poprzedni `stan.rano`, komunikat `rano_niedostepny` - D13).

**`PracaRano`**: `praca_id`, `skan_id`, `gniazdo`, `klasa` (pewna / przypisana / dwuznaczna / nieznana / poprawka / konflikt / do_powtorzenia; None - skan, ktory sie nie liczy), `status` (klucz `statusy`: wiersze poranne `rano_*`, `nieznana_rano`, `dofrezowany`, `rano_juz_rozpoznany` przy poprawce do zlecenia z brakami, `skan_do_powtorzenia`; kolor ekranu = kolor wiersza, ktory podaje A6), `kolor`, `rgb`, `podpis`, `opis`, `kuweta`, `zeby`, `typ`, `sha16`, `projekt_id`, `miniatura` (PNG z `cechy_stl`), `kandydaci` (`Kandydat`: `sha16`, `pokrycie`, `projekt_id` do wyboru albo None, `kuweta` / `zeby` / `typ` - plik w kilku zleceniach: tylko wartosc wspolna wszystkim, inaczej None (D10), `zlecen`, `miniatura`), `przypisanie`, `decyzja`, `decyzja_id`, `operator`, `czas_decyzji`, `konflikt`, `konflikt_z` ((numer plytki, gniazdo)), `zlecenie_odhaczone`, `domyka_dofrezowanie`, `kuweta_do_sprawdzenia`, `dozwolone` (`wybierz_kandydata`, `przypisz_recznie`, `cofnij_przypisanie`).

**Polecenia poranne (`POLECENIA_RANO`, kazde zwraca `Odpowiedz`, nigdy wyjatek)**: `przelacz_tryb(tryb)`; `wybierz_kandydata(praca_id, sha16)`; `przypisz_recznie(praca_id, projekt_id=None)` (None = "bez projektu"); `cofnij_przypisanie(praca_id, decyzja_id=None)`; `zamknij_piec(sesja_pieca_id=None)` (pokazany piec; odmowa `analiza_trwa` / `skanowanie_trwa` wg `StanRano.zajety` - blokada w kontrolerze, P3; `dane` = wynik A6; bez Excela komunikat `excel_niedostepny` z WLASNA lista kuwet pieca); `zamknij_piec_i_przenies(sesja_pieca_id, skany)` (odpowiedz "Tak" na pytanie `nowy_wsad`; te same odmowy + odmowy A6 jako komunikat); `cofnij_przeniesienie(sesja_pieca_id)` (A6 runda 5); `otworz_piec_ponownie(sesja_pieca_id)`; `podaj_numer_plytki(skan_id, numer, mimo_nowego_wsadu=False)` - rano zmiana numeru plytki ze skanem innego wsadu daje odmowe `numer_nowy_wsad` i pytanie `numer_nowy_wsad` ("Zmien numer na N mimo to" = to samo polecenie z `True`); `pomin_skan(skan_id)` / `cofnij_pominiecie(skan_id)`; `zamknij_brak_recznie(projekt_id, powod)` (kod z `session_rano.POWODY_ZAMKNIECIA`) / `cofnij_zamkniecie_reczne(projekt_id)`; `ustaw_kolejnosc("liczba" | "numer")` i `wybierz_kuwete(kuweta)` (U7: trzeci sposob - numer wpisany recznie; zera wiodace i spacje bez znaczenia; bez osoby); `potwierdz_kuwete(kuweta)` (Enter - kuweta POKAZANA na ekranie; wpis `kuweta_potwierdzona` w dzienniku) i `cofnij_kuwete(kuweta)` (Backspace - `kuweta_do_cofniecia`; `kuweta_cofnieta`): gdy w kontrolerze biezaca / ostatnia jest inna - odmowa `kuweta_zmienila_sie` bez wpisu (B1); potwierdzenia sa w pamieci kontrolera i w dzienniku (po restarcie odtwarzane dla pieca); wpisy `kuweta_*` i `tryb_zmieniony` bez nazwiska (jak dziennik sesji porannej - D4). Zapytanie (nie polecenie): `projekty_kuwety(kuweta) -> tuple[ProjektPuli]` (projekty zlecenia do przypisania recznego: zab, typ, stan punktu, miniatura; bez nazw folderow i plikow).

**Komunikaty poranne**: `ramka_niedostepna` (staly id `ID_RAMKA_PORANNA`, info, w trybie `rano`, mozna zamknac), `excel_niedostepny` (id `ID_EXCEL`, po "Zamknij piec" ze zleceniami kompletnymi: nr pieca, doba, godzina zamkniecia i numery kuwet - najwyzej `MAX_KUWET_KOMUNIKATU`) - program dziala dalej wedlug ekranu (kryterium 5); odmowy `analiza_trwa`, `skanowanie_trwa`, `kuweta_zmienila_sie`; trwaly `rano_niedostepny`. Pytania plytek porannych (brak numeru, ponowny skan - z podstawa propozycji A6, plytka nie z trybu z przyciskiem "Pomin skan") oraz pytania pieca `nowy_wsad` ("Poprzedni piec nie zostal zamkniety. Zamknac go i przeniesc nowe skany do nowego pieca?") i `numer_nowy_wsad` sa w `stan.pytania` jak wieczorne (`RODZAJE_PYTAN`).

**Atrapa**: `indeks_rano_sztuczny(baza, czas)` (38 fikcyjnych zlecen, kuwety 3200-3445, "#1234", "#1301", miniatury `miniatura_sztuczna`), `sztuczny_wynik_rano(...)` (rodzaje `RODZAJE_PRAC_RANO`: pewna, zolta, dwuznaczna, nieznana, brak, podwojny), `symuluj_skan_rano(numer, gniazda, projekty=...)`, `scenariusz_poranny()` (piec 1 zamkniety, piec 2: 3 plytki x 23 prace - `plan_scenariusza_rano`); `py -3.12 -m stanowisko.aplikacja --atrapa --rano` pokazuje okno na tych danych. Testy: `test_kontroler_api.py::test_rano_*` (atrapa i prawdziwa aplikacja; runda 2: `test_rano_r2_*` - B1, P1-P4, A6 r4/r5, D13 i test prawdziwej `Aplikacja`: przelaczenie trybu w trakcie analizy, blad skanu porannego, restart w trybie rano), `test_ui_rano.py`; ekran: `ui_rano.md`.

## Ramki i Excel - kontrakt w wersji 4 (E3-A12, 18.11.2026; wszystko addytywne)

**Podlaczenie.** `Aplikacja(ust, ramki=True, excel=True)` (tak wola `main()`): przy `start()` klienci ramek z `[ramki]`
(`aplikacja.utworz_ramki` -> `indicate.Indicate.z_ustawien`, identyfikator laptopa w folderze bazy) i Excel z `[excel]`
(`aplikacja.utworz_excel` -> `excel.Excel.z_ustawien(ust, baza=...)`, polaczenie COM dopiero przy pierwszym odczycie arkusza).
Domyslnie (`ramki=False`, `excel=False`) - bez ramek i Excela (testy, atrapa). Testy podaja obiekt `Indicate` i zrodlo arkusza
(`ArkuszWPamieci`). Wspolna czesc obu kontrolerow: `KontrolerSesji.podlacz_ramki(indicate)` / `podlacz_excel(excel)` - plan pieca
idzie do klienta PRZED pierwszym kontaktem z ramka (potwierdzenia kuwet z bazy, gdy ramka planu juz nie ma), potem `uruchom()`.
Zle ustawienia ramek / brak Excela = ostrzezenie (log, komunikat), program dziala dalej (kryterium 5).

**Stan.** `stan.ramki` (`StanRamek`: `wieczorna` / `poranna` = `StanRamki` - `polaczona`, `blad`, `komunikat`, `plytka`, `tryb_ramki`,
`plan_przyjety`, `wstrzymane`, `potwierdzone`, `ostrzezenia`; `test_led`) - czytany z klientow co `OKRES_STANU_RAMEK_S` (0,25 s)
w `przetworz()`; zmiana polaczenia / bledu = pelny stan (komunikaty, `StanRano.ramka`), reszta = czesc "zywa". `stan.excel`
(`StanExcel`: `tryb`, piec, `pozycje` = `PozycjaExcel` - kuweta, klasa, wiersz, regula, powod, `do_sprawdzenia`, data,
`kandydatow`, `zalatwiona`, `wynik`; `widoczne`, `blad`, `ostrzezenia`, `do_zalatwienia`) - bez nazw folderow i kolumny H;
te okno dostaje zapytaniem `excel_szczegoly(nr) -> SzczegolyExcel` (folder, `KandydatExcel` z H) - tylko na ekran.
`StanRano.ramka` = ramka poranna polaczona i bez bledu, `StanRano.excel` = program ma Excel. Komunikaty: `ramka_niedostepna`
(rano), `ramka_wieczorna_niedostepna` (wieczor, staly id `ID_RAMKA_WIECZORNA`), `ramka_blad` (zly klucz, drugi laptop, awaria),
`ramka_piec_zamkniety`, `ramka_zamknij_odmowa`, `ramka_zamknij_nieaktualne`, `ramki_test_led`, `excel_blad` / `excel_cien` /
`excel_niedostepny` (staly id `ID_EXCEL`). Teksty komunikatow i bledow ramek (`BLEDY_RAMEK`): `statusy.py` (runda 2, D4).

**Zdarzenia ramek (zegar okna -> `przetworz()`).** Kazde zdarzenie odebrane z `odbierz_zdarzenia()` (takze pominiete i odrzucone)
trafia do dziennika `zdarzenia` (zrodlo `ramka_p` / `ramka_w`, typ = typ zdarzenia, dane: `klucz` = `start_id:nr`
(`indicate.klucz_zdarzenia`), `z_historii`, `nieaktualne`, numery plytki / kuwety / planu, `skutek`). Klucz jest sprawdzany
w TEJ SAMEJ transakcji co skutek (pamiec ostatnich 4000 kluczy z dziennika + wpisy dopisane po jej odczycie) - historia ramki po
restarcie programu nie daje duplikatow ani drugiego skutku; bez zmiany schematu (klucz w danych). Kolejne zdarzenia bez skutku
w sesji - jedna transakcja na serie. `potwierdzenie` / `cofniecie` / `kuweta_wybrana` - wpis (`skutek` "zapisano" albo
"inny_piec"). `zamknij_piec` - `session_rano.zamknij_piec(plan_id=...)` TYLKO gdy `nieaktualne` False, `plan_id` = otwarty piec
biezacy, nie trwa analiza / skanowanie i jest wybrana osoba; inaczej wpis z `skutek` "nieaktualne" / "inny_piec" / "analiza_trwa"
/ "skanowanie_trwa" / "odmowa" (z powodem sesji) i komunikat. Enter / Backspace na ramce = takze kuweta rozlozona / cofnieta na ekranie (decyzja, runda 2): kuweta potwierdzona na WSZYSTKICH plytkach planu, na ktorych lezy (lustro `potwierdzone()` klienta) - pole `kuweta_rozlozona` / `kuweta_cofnieta` we wpisie zdarzenia (`_rozlozone` czyta je obok wpisow ekranu).

**Plan ramki porannej.** Po kazdym pelnym zbudowaniu stanu w trybie `rano`: gdy zmienil sie piec na ekranie (plytki, prace,
braki, kolejnosc kuwet z ekranu) - `SesjaRano.plan_plytek(sesja_pieca_id, kolejnosc)` -> `poranna.ustaw_plan_rano(...)`; brak
otwartego pieca biezacego = `zgas()`. Pierwszy plan pieca w uruchomieniu niesie potwierdzenia z dziennika ramki (lustro: potwierdzenie
dopisuje, cofniecie usuwa).

**Ramka wieczorna.** Spacja (udany `start_skanu`, tryb `wieczor`) -> `skanowanie()`; plik skanu -> znacznik Spacji albo
`znacznik()` (skan bez Spacji = nowy skan, ramka gasi poprzedni wynik); pierwszy `start` analizy skanu -> `analiza()` raz na skan
i tylko dla ostatniego skanu (recenzja PR #28 D5: ponowna analiza tego samego skanu - bez drugiego `analiza()`); wynik zapisany ->
po zbudowaniu stanu `wynik(numer, uklad, {gniazdo: ramka_protokol.kolor_ramki(Gniazdo.status)}, znacznik)` - te same statusy, co
mapa na ekranie, wysylane ponownie po decyzji / podaniu numeru; skan zablokowany albo blad analizy -> `blad()`. "Test LED" -
`tryb("test_led")` obu ramek; po 8,5 s plan pieca ponownie.

**Excel po "Zamknij piec"** (przycisk albo klawisz ramki; takze `zamknij_piec_i_przenies`): bez Excela - komunikat z lista kuwet
(A7); tryb "pytaj" - `excel.propozycje(wynik)` (swiezy odczyt), poprawki do logu (`zaloguj_poprawki`), "juz odhaczone" bez
watpliwosci - `zaloguj_juz_odhaczone` bez pytania, reszta czeka w `stan.excel` na okno "Excel: wskaz wiersz"; tryb "cien" -
`zapisz_cien` (sam log) i komunikat `excel_cien`. `BladExcela` (Excel nie uruchomiony, arkusz zmieniony) = `rozlacz()`, komunikat
`excel_blad` z lista kuwet i praca dalej. Polecenia (`POLECENIA_A12`): `excel_zatwierdz(sesja_pieca_id, zlecenie_id, wiersz=None)` (tylko po kliknieciu;
osoba = wybrana na zmianie), `excel_pomin(sesja_pieca_id, zlecenie_id)`, `excel_odswiez()`, `excel_pokaz(sesja_pieca_id=None)` (takze po restarcie: zlecenia
kompletne bez wpisu w `excel_zapisy` tego pieca), `excel_zamknij()` ("Pozniej"), `test_led()`, `przejmij_ramke(rola)` (`wznow()`
po "drugi laptop" / "zly klucz" - decyzja osoby). `otworz_piec_ponownie` czysci propozycje tego pieca.

**Zamkniecie.** `zamknij()` najpierw: `zgas()` obu ramek, `Indicate.zatrzymaj()` (najwyzej ok. 1 s; zgaszenie, ktore nie doszlo -
ostrzezenie w logu), `excel.rozlacz()`. Zdarzenia nieodebrane do chwili zamkniecia wracaja po starcie jako historia (`zamknij_piec`
z historii - tylko wpis i komunikat).

**Wymaganie dla dalszych paczek (recenzja PR #26, D1, D2).** Kazda zmiana stanu punktow zlecen w procesie programu idzie przez
polecenie kontrolera (`_polecenie`) albo konczy sie `_uniewaznij_punkty()` (tak robi "Zamknij piec" z ramki); `_polecenie`
uniewaznia pamiec brakow takze po nieoczekiwanym wyjatku (mogl wypasc po zapisie).

**Dziennik `start_skanu`** (prosba A10): dane `{"udany", "tryb"}`. Powrot procesu silnika po `silnik_nie_startuje` = wpis
`silnik_wrocil` (A10 D-R2).

**Runda 2 (recenzja PR #30).** B1: okno Excela - "Zatwierdz" / "Pomin" tylko dla pozycji wybranej kliknieciem; po zapisie nieaktywne
do nastepnego klikniecia, `do_sprawdzenia` wymaga wskazania wiersza. P1: Excel po "Zamknij piec" odroczony (`stan.excel.w_toku`):
najpierw `zgas` ramki P i ekran, potem kroki z zegara okna - propozycje (jeden odczyt arkusza), poprawki (jeden), "juz odhaczone"
(po jednym na obieg); tryb "cien" = log z odczytu propozycji (`excel.zapisz_cien_bez_odczytu`, bez odczytu na pozycje). P2: kazdy
blad `plan_plytek` = ramka P zgaszona, komunikat `ramka_plan_blad`, ponowienie co `OKRES_PONOWIENIA_PLANU_S`. P3: zamkniecie pieca
(przycisk, ramka, w kazdym trybie) gasi ramke P od razu; w trybie "wieczor" plan sie nie zmienia, ale zamkniety piec nie swieci
(D10). P4: polecenia Excela adresowane tozsamoscia `excel_zatwierdz(sesja_pieca_id, zlecenie_id, wiersz=None)`,
`excel_pomin(sesja_pieca_id, zlecenie_id)`, `excel_szczegoly(sesja_pieca_id, zlecenie_id)` - lista zmieniona = odmowa bez zapisu.
P5: niezalatwione pozycje poprzedniego pieca nie znikaja - `StanExcel.zalegle` (przyciski w oknie, `excel_pokaz`), komunikat
`excel_zalegle`; przy starcie piece zamkniete w ostatnich `ZALEGLE_EXCELA_H` godzinach. P6: znacznik ramki W dopiero dla skanu
zleconego do analizy (nie dla powtorki ani pliku przemianowanego). P7: "Zamknij piec" z ramki dla pieca zamknietego / otwartego
ponownie - nieaktualne do przyjecia planu nowej wersji (`plan_przyjety` z wyzsza `wersja`). P8: kazdy wyjatek kroku Excela =
komunikat `excel_blad` z lista kuwet. D1: `_klucze_od` przesuwany po wlasnych wpisach. D2: zdarzenia ramek przy zajetej bazie
czekaja na ponowienie (nie gina), blad ramek / Excela nie przerywa `przetworz`, blad klawisza "Zamknij piec" = komunikat. D3:
`cofnij_przeniesienie` czysci propozycje, ponowne zamkniecie bez dubli w logu. D7: komunikaty "ramka nie odpowiada" po
`CZAS_NA_POLACZENIE_RAMEK_S`, utracone zdarzenia w podpowiedzi paska. D8: `podlacz_excel` tylko z baza programu. D9: poprzednia
proba z bledem (`PozycjaExcel.poprzedni_blad`, `poprzedni_wiersz`) pokazana w oknie. D6 ("Przejmij ramke" bez pytania) - bez zmian
(raport).

**Runda 3 (recenzja PR #30 r2).** P-N1: kuweta rozlozona z ramki tylko, gdy potwierdzona na KAZDEJ plytce, na ktorej lezy wedlug
ekranu (`KuwetaRano.plytki`); praca na plytce poza ramka (okragla) - rozlozenie potwierdza osoba na ekranie. P-N2: pozycja Excela
z bledem jednego zlecenia dostaje `zlecenie_id` z `kompletne[i]` (da sie ja pominac; "cien" bez dubli logu). P-N3: zalegle piece
Excela - przyciski na stronie "Kompletne i braki" (`wynik_excel_zalegly_<id>`); okno pokazane jawnie (`excel_pokaz`) widoczne takze
bez pozycji, gdy sa zalegle piece. D-N1: zdarzenia ramek przy zajetej bazie - ponowienie co `OKRES_PONOWIENIA_ZDARZEN_S` (1 s),
czekanie na baze przy ich zapisie `CZEKAJ_ZDARZENIA_MS` (150 ms zamiast 5 s - runda 4, D-R3-1). D-N2: wskazany wiersz kandydata zerowany, gdy znika
z listy. D-N3: Backspace na ramce nie przestawia biezacej kuwety laptopa. D-N4 (`_plany_czekaja` bez sprzatania - plan_id z data,
kierunek bezpieczny), D-N6 (D6 / D10) - bez zmian.

**Runda 4 (recenzja PR #30 r3).** P-R3-1: kuweta, ktorej nie ma na liscie kuwet ekranu (tryb "wieczor" - `stan.rano` None, skan
liczony inaczej), nie jest oznaczana jako rozlozona Enterem na ramce (wpis zdarzenia jak zawsze). D-R3-2: "Odswiez z Excela" nie
zamyka okna pokazanego jawnie (takze tylko dla zaleglych piecow).

## Jak dziala `Aplikacja`

- **Jeden egzemplarz (B1):** `Aplikacja(ust)` (i wczesniej `main()`) zajmuje `BlokadaStanowiska` - plik `<baza>.blokada` obok bazy zablokowany przez caly czas pracy (`msvcrt.locking`; poza Windows `fcntl.flock`), ZANIM otworzy baze, log i folder skanera. Drugi egzemplarz na tej samej bazie: `ProgramJuzDziala` - `main()` pokazuje "program juz dziala" i konczy sie kodem 3, niczego nie zapisujac. Blokade trzyma system: znika razem z procesem (awaria, zabicie) - nie ma czego sprzatac recznie; `zamknij()` zwalnia ja na koncu. Dodatkowo kazdy zapis wyniku sprawdza w tej samej transakcji (`BEGIN IMMEDIATE`), czy ta sama tresc (`sha16`) nie ma juz wyniku - wtedy wynik jest odsiewany (wpis `wynik_powtorzony`), wiec nawet dwa programy piszace do jednej bazy nie dadza dwoch skanow.
- **Start** (`Aplikacja(ust)`, `start()`): baza i sesja z `ustawienia.toml`; sprzatanie `dane/podglady` (P9: kopie `*_wynik.json` i pliki `*_podglad.npz` bez wpisu `podglad` w dzienniku - po awarii albo zamknieciu); silnik z `ust` (proces sam nie czyta pliku); uklady plytek z `[plytki]` wczytane od razu (numpy laduje sie przy starcie, nie w petli okna przy pierwszej plytce); liczenie puli w tle; zadania z `dane/zadania_niezakonczone.json` zlecane ponownie; dopiero potem `Scanner(..., znane=ZnanePliki(<wszystkie wiersze skany> + <zadania wznowione>))` - skany zapisane, gdy program nie dzialal, wracaja z `zastany=True` i sa analizowane (komunikat `wznowiono` z liczba), a pliki juz przyjete nie sa zglaszane.
- **Powtorki** (zaden skan liczony dwa razy): ta sama tresc (`sha16`) co skan, ktory MA wynik w bazie (kazdy status poza `blad`), albo co zadanie czekajace w kolejce - nie jest liczona ponownie (wpis `skan_powtorzony` w dzienniku; na zywo komunikat `skan_juz_jest`, ale nie dla zmiany nazwy pliku juz przyjetego). Samo zobaczenie pliku niczego trwale nie zapisuje, wiec awaria miedzy zdarzeniem a wynikiem nie gubi skanu.
- **Plik przemianowany w kolejce (P2):** ta sama tresc pod INNA sciezka, gdy skan czeka (zapis pod nazwa robocza, poprawiona nazwa) = sciezka zastepcza zlecenia; gdy stara sciezka zniknela, zadanie ja przejmuje (wstrzymane - od razu; w kolejce silnika - `anuluj` i zlecenie ponowne; wpis `skan_przemianowany`). Gdy silnik zdazyl siegnac po stara sciezke ("brak pliku" = blad `analiza`), zadanie jest zlecane ponownie z nowa. W bazie (`skany.plik`) i w pliku zadan - sciezka, pod ktora plik lezy teraz.
- **Wynik** -> `session.przyjmij_wynik` (pole `skan` wyniku = `sha16` zamiast nazwy pliku); wpis `podglad` w dzienniku wiaze skan z plikiem `*_podglad.npz` (oba w jednej transakcji = jeden zapis na dysk); kopia wyniku zapisana przez silnik (zawiera folder puli) jest usuwana od razu po odebraniu wyniku (P9); plik podgladu - gdy wynik nie zostal zapisany (blad danych, powtorka, zamkniecie z wynikiem niezapisanym).
- **Zapis, ktory sie nie udal (P1, P8):** baza zajeta (`BladBazy`) albo blad zapisu (pelny dysk, blad wejscia / wyjscia, dysk odlaczony - `OSError` / `sqlite3.OperationalError`) przy zapisie wyniku ALBO bledu analizy: pozycja zostaje w pamieci (`stan.niezapisane`, "nie zapisano - blad zapisu" / "baza zajeta", czesc `kolejka.wstrzymane`) i jest zapisywana ponownie sama co `OKRES_KONTROLI_S`, potem 2x, 4x ... rzadziej (najrzadziej co 30 s), bez ponownej analizy, oraz na polecenie `ponow_zapis()`. Komunikat: trwaly `blad_zapisu` (staly id) albo `baza_zajeta`; oba znikaja po udanym zapisie. Zamkniecie z pozycja niezapisana: zadanie wraca do pliku zadan i liczy sie od nowa po starcie. Blad danych (wynik, ktorego sesja nie umie przyjac) - skan `blad` z komunikatem, jak dotad.
- **Bledy silnika:** `proces` / `limit_czasu` -> `session.przyjmij_blad` (skan `blad`, wpis `blad_analizy_rodzaj`) + komunikat `blad_analizy`; `analiza` -> najpierw pula liczona od nowa (P3, nizej), blad zapisywany dopiero, gdy pula jest niepusta; `plik_zmieniony` -> tylko komunikat i wpis w dzienniku (nowa tresc ma wlasne zdarzenie); `plik_niedostepny` -> komunikat i ponowne zlecenie `[silnik] ponow_plik_niedostepny` razy (3), potem skan `blad` z komunikatem `plik_niedostepny`; `start` (proces analizy nie umie wystartowac) -> jedna ponowna proba, potem skany CZEKAJA z komunikatem `silnik_nie_startuje` (nie dostaja bledu, wracaja po restarcie programu).
- **Pula projektow - poziom 1 planu:** jeden folder (domyslnie `[sciezki] folder_cyrkon`) + wspolczynnik wpisany recznie (None = domyslny dla rozpoznanego typu plytki, jak w oknie testowym); wybor technika zapisany w `dane/stanowisko_pula.json`. Liczba STL liczona w watku pomocniczym (regula jak `synth.pliki_projektow`) przy starcie, po "Odswiez pule", po kazdym nowym skanie, po kazdym wyniku i po kazdym bledzie analizy (P3; najwyzej jedno liczenie naraz - D4). Pula pusta albo bez folderu: skany czekaja (`kolejka.wstrzymane`, komunikat) do "Odswiez pule" - nie dostaja bledu analizy, takze gdy folder oprozniono PO policzeniu puli (blad analizy -> liczenie -> pusta = skan wstrzymany, zadania czekajace w kolejce silnika wracaja do wstrzymanych). Katalog i pule z bazy: paczki A4 / A5.
- **Start skanu (DW5):** `start_skanu()` wola `Scanner.start_skanu` dokladnie raz; akcja to atrapa (parametr `start_skanu=`), prawdziwa powstanie po probach na skanerze (B2). Zadnego automatu klikajacego.
- **Zamkniecie** (`zamknij()`): `scanner.stop()`, potem `silnik.stop()`; wyniki, ktore zdazyly przyjsc, sa przyjmowane; ostatnia proba zapisu pozycji niezapisanych; zadania w toku, w kolejce, wstrzymane i niezapisane -> `dane/zadania_niezakonczone.json` (sciezka, `sha16`, rozmiar, czas pliku, tryb, numer); plik znika po wczytaniu przy starcie; na koncu zwolnienie blokady. Awaria bez `zamknij`: pliku nie ma, skany bez wyniku wracaja przez nadrabianie folderu.
- **Log (P5):** `konfiguruj_logi` wlacza `FiltrNazw` w loggerach programu (`__main__`, `stanowisko.*`, w tym `scanner` i `silnik`) i na uchwycie pliku: argument wpisu, ktory jest sciezka albo nazwa pliku, staje sie `sha16` skanu (znanym z wpisu albo z kontrolera) albo `<plik>`, sciezki w tekscie i sladach wyjatkow -> `<sciezka>` (moduly programu - sama nazwa pliku `.py`). `odlacz_logi` - odwrotnosc.
- **Watek.** Wszystko w watku okna; `scanner` i watek liczenia puli wkladaja zdarzenia do kolejki, silnik do `silnik.zdarzenia`; `przetworz()` obsluguje je najwyzej 50 ms naraz. Blad obslugi jednego zdarzenia = wpis w logu i nastepne zdarzenie.

## Reguly ponad `session` (do potwierdzenia przez wlasciciela - lista w raporcie paczki)

1. **Operator na zmiane:** wybor osoby wygasa, gdy zmieni sie numer zmiany (6 / 14 / 22) i po kazdym starcie programu - komunikat `nowa_zmiana`, decyzje odrzucane do wyboru osoby.
2. **"Ukruszona" na pracy, ktorej program nie oznaczyl na czerwono,** zapisuje sie jako `ukruszona_niewykryta` (SE9, tryb cienia); na czerwonej - `ukruszona`.
3. **Plytka bez numeru:** prace zielone maja status `czeka_na_numer` i nie maja koloru (nic zielonego) do podania numeru; czerwone i zolte sa widoczne, decyzje sa przyjmowane. Wylacznik: `statusy.ZIELONE_BEZ_NUMERU_PLYTKI`.
4. **Odrzucenie propozycji ponownego skanu** ("to nowy wsad") wymaga operatora, jest zapisywane w dzienniku (`ponowny_skan_odrzucony`) i nie wraca po restarcie; zastapienie wprost nadal dziala. "Pozniej" (`zamknij_pytanie`) i `zamknij_komunikat` ukrywaja pozycje tylko do konca pracy programu. E3-A1p (18.11.2026): pytanie `ponowny_skan` pada tylko, gdy na plytce leza te same prace co w poprzednim skanie (regula w `session`, `opisy_modulow/session.md`; plytka z nowym wsadem nie dostaje pytania ani konfliktu). Dopoki skan czeka na odpowiedz (takze po "Pozniej"), konflikty projektu TYLKO miedzy skanami jednej spojnej skladowej grafu par czekajacych (skan czekajacy - skan, ktory proponuje zastapic; np. ta sama plytka zeskanowana trzy razy bez odpowiedzi: A, B, C - runda 3, recenzja PR #22 P1), po jednym miejscu w kazdym skanie, nie daja komunikatu `konflikt_projektu` (pasek bledow) - `stan.konflikty` podaje je jak dotad; po "Nie, to nowy wsad" skan wypada ze skladowej i komunikaty pojawiaja sie normalnie, po "Tak" konflikty znikaja (poprzedni skan zastapiony); konflikt z innym skanem albo w obrebie jednego skanu - bez zmian (`KontrolerSesji._konflikt_ponownego_skanu`).
5. **Z9:** `pomaranczowy` = "poprawiana recznie", `dofrezowany` (bursztyn, rano - A6) = "zab dofrezowany".
6. **P4:** praca zielona tylko przy inspekcji "ok" i znanym dopasowaniu (`statusy.status_pracy` / `kolor_pracy`).

Reguly 3, 4 i 6 zyja tylko w kontrolerze: inny odbiorca stanu `session` (ramka A8, raport) widzi dzis zielone na plytce bez numeru i przy inspekcji innej niz "ok" oraz propozycje ponownego skanu odrzucona przez technika - przed A8 trzeba je przeniesc do `session` (POTRZEBUJE w raporcie paczki).

## Ustawienia (wszystkie nowe klucze opcjonalne; plik sprzed etapu 3 wczytuje sie bez zmian)

`[sciezki] podglady = "dane/podglady"`, `pula_cache = "dane/pula_cache"` (pamiec linii brzegu silnika), `logi = "dane/logi"`; `[scanner] stabilizacja_ms, min_rozmiar_mb, min_trojkatow, wzorzec_pliku, rekurencyjnie, obserwator`; `[silnik] limit_zadania_s, czekaj_na_plik_s, pamiec_linii, ponow_plik_niedostepny`. Wartosci domyslne rowne domyslnym modulow `scanner` i `silnik` (test porownuje 9 z 10; `ponow_plik_niedostepny` to regula aplikacji). `pamiec_linii` od rundy 2 domyslnie `false` - jak w `silnik` (D11); `true` przyspiesza pierwsza plytke po starcie (linie brzegu projektow z dysku, `dane/pula_cache` rosnie bez sprzatania do DW4). Uzywane bez zmian: `[sciezki] folder_eksportu_skanera, folder_cyrkon, baza, wyniki`, `[sesja]`.

## Dane osobowe

Komunikaty, stan, sygnaly, dziennik, log programu (takze wpisy `scanner` i `silnik` - `FiltrNazw`, P5), pliki wynikow sesji (pole `skan` = `sha16`) i plik listy "do dofrezowania" nie zawieraja nazw plikow ani folderow (skanu, puli, zlecen) - skan opisuje `sha16`; teksty bledow z silnika sa czyszczone z nazwy i folderu pliku skanu, zanim trafia do `session`. Test `test_i_...`: fikcyjna nazwa folderu zlecenia uzyta jako podfolder puli i podfolder folderu skanera oraz fikcyjne nazwisko w nazwie PLIKU skanu - 0 wystapien w logu (plik i `caplog`), stanie, sygnalach, dzienniku, plikach wynikow, nazwach plikow i liscie "do dofrezowania". Znane granice: (1) `skany.plik` = sciezka pliku skanu (kolumna z planu, pisze `session`); (2) `dane/zadania_niezakonczone.json` (sciezki skanow czekajacych na analize, istnieje miedzy zamknieciem a startem) i `dane/stanowisko_pula.json` (folder puli) - pliki robocze obok bazy, poza repo; (3) kopia wyniku silnika w `dane/podglady` (folder puli, nazwa skanu) istnieje od zapisu przez silnik do odebrania wyniku przez kontroler; po awarii w tym czasie - do nastepnego startu (sprzatanie, P9); (4) `silnik.log` (wyjscie bibliotek z procesu analizy) nie przechodzi przez `FiltrNazw` - w testach i wariancie odniesienia bez nazw.

## Kryterium "dziala"

`test_kontroler_api.py`: kazdy test kontraktu w dwoch wariantach (atrapa / prawdziwa aplikacja z funkcja analizy na danych sztucznych w procesie silnika) - kolory gniazd = wynik analizy po decyzjach w 100 % gniazd, decyzje i odmowa bez operatora, start skanu, plytka niezgodna / do powtorzenia / nie z trybu / bez numeru (nic zielonego), ponowny skan (pytanie z liczba decyzji, potwierdzenie, cofniecie, odrzucenie, po 61 min nowy wsad), "zab juz na liscie", operator na zmiane, pula, sygnaly, `lacznik_qt`, zamkniecie; od rundy 2: P4 (zielony tylko przy inspekcji "ok"; tabela wszystkich par), P7 (plik listy), D1 (zle argumenty kazdego polecenia), D2, D6, D7 i test zgodnosci atrapy z prawdziwym kontrolerem (ta sama sekwencja polecen = te same odpowiedzi). `test_aplikacja.py`: prawdziwa analiza `porownaj` na plytce z atrap zapisanej przez symulator skanera, zamkniecie w trakcie analizy i restart, awaria bez zamkniecia, dodatkowe punkty awarii (wynik oddany przez silnik i nieprzyjety; plik zadan pozostawiony po starcie), powtorki, petla Qt przy 10 plytkach, pula pusta i oprozniona po policzeniu (P3), `plik_zmieniony`, `plik_niedostepny`, plik przemianowany w kolejce (P2), zabity proces, silnik bez startu, baza zajeta przy wyniku i przy bledzie (P8), blad zapisu (P1), drugi egzemplarz programu i blokada po zabitym procesie (B1), wynik tresci juz zapisanej, kopie wynikow i podglady (P9), folder skanera pojawiajacy sie pozniej, nazwy zlecen i nazwisko w nazwie pliku skanu (P5), kolejnosc zamykania, parametry z ustawien, plik startowy bez Qt, `main()`. Testy zalezne od czasu analizy czekaja na plik-brame (`"brama"` w opisie sztucznego skanu, D13) zamiast na uplyw czasu; zalezny od czasu zostaje tylko pomiar petli Qt (f). Wariant na duzych sztucznych skanach (45-55 MB) i puli prawdziwych projektow przez cala aplikacje w petli Qt: zmienne `E3A3_DANE_REF` (folder `skan_<typ>_n*.stl`) i `E3A3_PROJEKTY` (folder puli), bez nich pomijany; z `-s` wypisuje czasy, najdluzsza przerwe petli okna i najdluzsze kroki w watku okna. Liczby: `raporty/E3-A3a_2026-11-17.md`.

## Zalozenia i granice

- Od E3-A7 tryb `wieczor` i `rano` (opis wyzej); od E3-A12 ramki i Excel (opis wyzej). Stan pokazuje biezaca dobe robocza (06:00-06:00) - o 6:00 plytki znikaja z mapy, lista biezaca "do dofrezowania" zostaje.
- Nie ma polecenia "analizuj ten skan ponownie" (np. po zmianie wspolczynnika): ta sama tresc pliku ma juz wynik i jest odsiewana - plytke trzeba zeskanowac jeszcze raz. Do decyzji, czy dodac.
- Rozstrzygniecie konfliktu projektu (ten sam projekt w dwoch gniazdach), `wybor_kandydata` i `przypisanie_reczne` nie sa obslugiwane przez `session` - stan podaje `konflikty` i komunikat, bez polecenia.
- Liczba STL to liczba plikow w folderze, nie liczba projektow, ktore analiza zdola wczytac; folder sieciowy z tysiacami plikow jest listowany przy kazdym odswiezeniu (w tle) i przez silnik przy kazdym zadaniu - pomiar na prawdziwym folderze: A4 / A5.
- Skan `blad` (takze `plik_niedostepny` po ponowieniach) jest "znany": po restarcie nie jest analizowany sam; ten sam plik zapisany ponownie albo skopiowany pod inna nazwa - tak.
- Wynik, ktory czekal na zapis (baza zajeta, dysk), a program zostal zamkniety: zadanie wraca do pliku zadan i skan jest liczony od nowa po starcie.
- P2: gdy silnik zglosi "brak pliku", ZANIM obserwator zauwazy nowa nazwe pliku (wyscig rzedu sekund), skan dostaje `blad` (po sprawdzeniu puli), a nowa nazwa jest liczona osobno (skan `blad` wyniku nie ma) - na mapie zostaje plytka "analiza nie powiodla sie" obok poprawnej.
- Blokada jednego egzemplarza dotyczy jednego pliku bazy: dwa programy z roznymi `[sciezki] baza` na jednym folderze skanera nadal liczylyby skany dwa razy (kazdy do swojej bazy) - konfiguracja, nie przypadek obslugi.
- Baza zajeta przez inny program blokuje watek okna do `czekaj_ms` (5 s) przy kazdym zapisie (D5, znane); ponowienia zapisu wyniku sa coraz rzadsze (najrzadziej co 30 s), wiec okno nie stoi caly czas.
- Okno zastepcze w `aplikacja.py` jest tylko po to, zeby program dal sie uruchomic przed A3b.
- Prawdziwa akcja "start skanu", nazwy i sposob zapisu plikow prawdziwego skanera: po dniu skanera (B2).

## Pula per praca w programie - kontrakt w wersji 5 (E3-A5i, 19.11.2026; addytywnie)

**Wlaczenie.** `[silnik] pula_wpisow = true` (domyslnie false - pula z folderu jak dotad; decyzja wlasciciela przy wdrozeniu).
Pula = `KatalogPul.z_ustawien(ust)` w watku pomocniczym `pula-katalog` (wlasne polaczenie z baza, kontrakt A4): `odswiez` (indeks
`folder_cyrkon` / `folder_prywatne` z cechami nowych plikow, `folder_millbox/wspolczynniki.csv`, powiazanie), potem `pula_wieczorna`,
`pula_poranna` i `sciezki`. Kiedy (runda 2, P1): przy starcie i "Odswiez pule" (glosno: stan `liczenie`, skany czekaja), przy zmianie
trybu (glosno - skany nowego trybu czekaja na swieza pule), przy zmianie doby roboczej i pliku `wspolczynniki.csv` (czas zmiany albo
rozmiar - `aplikacja.stan_pliku` w watku pomocniczym `pula-plik-csv` co `OKRES_KONTROLI_S`, najwyzej jedno sprawdzenie naraz, wynik
przez skrzynke - okno nie czeka na udzial sieciowy, runda 3 B1; cicho: pula zostaje do nowej) oraz po bledzie analizy (P3). Doba
i stan pliku zapisywane po UDANYM odswiezeniu; nieudane ponawiane po `PONOW_KATALOG_S` (60 s; runda 3 D8). NIE po kazdym wyniku ani skanie
(indeks "Cyrkon" to sekundy-minuty). Jeden watek indeksu naraz: zamowienie w trakcie = kolejne odswiezenie po biezacym (glosne, gdy
"Odswiez pule"; D8). Skan dostaje pule swojego trybu (`_opis_puli(z.tryb)`: wpisy + sciezki + zrodla, `druga` = pula drugiego trybu -
plytka drugiego typu dostaje ja w silniku, P6). Stan `pula.stan`: liczenie / gotowa (sa wpisy) / pusta (brak wpisow - skany czekaja,
komunikat `pula_wpisow_pusta` z przyczyna) / brak_folderu (katalog niedostepny - `pula_wpisow_brak`; poprzednia pula zostaje, gdy byla).

**Budowa w tle.** Po odswiezeniu `silnik.przygotuj_pule(opis trybu)`, ZANIM skany wstrzymane pojda do silnika - regula zimnej
puli: skany czekaja w kolejce silnika do konca budowy (`silnik.md`). Pasek: `pula.napis` ("wpisow puli: N - buduje pule: k z r
(analiza czeka)", potem "wpisow puli: N (brak pliku: x, bez wspolczynnika: y)" - niezerowe liczniki KatalogPul i `z_wpisow`), pasek
postepu z wartoscia `budowa_gotowe` / `budowa_razem`. Nowe pola `Pula`: `zrodlo` (folder / wpisy), `wpisy`, `liczniki`
(`ZamrozonySlownik`), `budowa_gotowe`, `budowa_razem`, `czas_budowy_s`. Dziennik: `pula / pula_wpisow` (liczby wpisow, czas
odswiezenia), `pula / pula_zbudowana` (geometrie, czas, liczniki). Sprzatanie pamieci puli: `[silnik] pamiec_puli_dni` (30; 0 =
nie) przekazane do silnika tylko z pula wpisow.

**Praca.** `Praca.wpisy_do_wyboru` (`WpisDoWyboru`: frezowanie_id, krazek, wspolczynnik, wybrany), `Praca.propozycja`,
`Praca.wybor_wpisu_osoba`; `dozwolone` + "wybierz_wpis", gdy sa wpisy do wyboru. Polecenie (19.) `wybierz_wpis(praca_id,
frezowanie_id)` - `KontrolerSesji`, wiec takze atrapa; zle argumenty = `zle_argumenty`, bez osoby = `brak_operatora`, wpis spoza listy =
odmowa `session`. Ekran: rzad "Krazek do wyboru:" w widoku pracy (przycisk na krazek, wybrany z dopiskiem).

**Start programu.** `main()` po utworzeniu `QApplication` wola `zaladuj_moduly_dll()` (`MODULY_DLL`: numpy, sqlite3, ctypes, socket,
select, http.client, unicodedata, zipfile, bz2, lzma, trimesh, PIL, `stanowisko.indicate`, `stanowisko.pula`, pywin32) - przed
pierwszym procesem roboczym (A2p POTRZEBUJE 4, recenzja PR #31 D2); wynik w logu po `konfiguruj_logi`. Diagnostyka PR #31 D1:
`uchwyty_knowndlls()` (NtQueryObject - typ obiektu przed nazwa, tylko katalogi) przy starcie; po kazdym kolejnym starcie procesu
roboczego (poprzedni sie zakonczyl) po `KNOWNDLLS_SPRAWDZ_PO_S` (5 i 30 s) wpis w logu "diagnostyka KnownDlls - N s po zakonczeniu
procesu roboczego (pid ...): uchwyt 0x.. procesu okna otwarty / zniknal (...)" - tylko log, bez wplywu na prace.

**Granice.** Pula wpisow pusta nie przechodzi na pule z folderu (pytanie do wlasciciela w raporcie E3-A5i). Zimna pula kilkuset wpisow (pierwszy start, zmiana
programu / bibliotek - nowy odcisk pamieci) = minuty czekania pierwszego skanu z postepem na pasku.

**Runda 2 (recenzja PR #32 r1).**
- Komunikaty puli wpisow (P4): `pula_wpisow_pusta` / `pula_wpisow_brak` (id `pula`, gdy skany czekaja) z przyczyna
  (`statusy.PRZYCZYNY_PULI`: brak / zly plik wspolczynnikow z numerami linii, brak frezowan w oknie dob, krazki sprzeczne i bez
  wspolczynnika z liczba prac i nazwami krazkow, pliki z CSV spoza katalogu, rano - brak zmienionych zlecen) zamiast komunikatu trybu
  folderu; staly `pula_wpisow_krazki` (id `pula_krazki`), gdy pula trybu ma krazki sprzeczne / bez wspolczynnika. Nowe pola `Pula`:
  `krazki_sprzeczne`, `krazki_bez_wspolczynnika`, `przyczyna`, `blad_budowy`; licznik `sprzeczne_wspolczynniki` na pasku; blad budowy
  w tle z przyczyna w napisie (D2). Wpisu recznego wspolczynnika w programie nie ma (`KatalogPul.wpisz_wspolczynnik` bez polecenia okna).
- Zdarzenia `pula` z `rodzaj` (tryb i numer odswiezenia); postep innej puli nie zmienia paska (D1); wpisy dziennika `pula_wpisow` /
  `pula_zbudowana` po ustawieniu stanu, blad bazy nie zostawia `liczenie` (D3).
- `MODULY_DLL_PULI` (scipy.spatial, scipy.ndimage, open3d, `stanowisko.synth` / `katalog` / `indeks`) - w `main()`, gdy `pula_wpisow`
  (P5): watek indeksu liczy cechy i miniatury nowych plikow w procesie okna (Open3D w procesie okna - koszt pamieci, opisany).
- Polecenie (20.) `cofnij_wpis(praca_id)` (D9): cofa wybor krazka - poprzedni wybor albo praca "nierozstrzygnieta"; w `dozwolone`, gdy
  wybor obowiazuje; ekran: "Cofnij wybor krazka" w rzedzie krazkow.

**Runda 3 (recenzja PR #32 r2).** B1: zaden `os.stat` folderu MillBox / udzialow w watku okna (wyzej). D1: plytka drugiego typu
(np. poranna dopuszczona wieczorem), gdy pula drugiego trybu jest pusta - komunikat `pula_plytki_pusta` z `skan_id` plytki (prace
dopasowane do puli biezacego trybu sa szare); komunikat ulotny (nie wraca po restarcie). D6: `cofnij_wpis(praca_id, decyzja_id)`,
`Praca.wybor_wpisu_id` - ekran podaje id pokazanego wyboru (podwojne klikniecie nie cofa drugiego; wieczorne "Cofnij" bez zmian).
D4: czas ladowania modulow z DLL w logu startu (z Open3D przy `pula_wpisow`) - do pomiaru na laptopie.

## Baza zajeta w chwili polecenia (E3-P14, 20.11.2026; N1 z recenzji PR #40)

- **Polecenie nie ginie po cichu (wariant "ponawia osoba").** Polecenie z `POLECENIA`, ktore przy zapisie trafia na baze
  zajeta przez inny program, konczy sie odmowa `baza_zajeta` i komunikatem TRWALYM poziomu "blad": `decyzja_niezapisana`
  (decyzje o pracy: `ukruszona`, `ok`, `cofnij`, `wybierz_wpis`, `cofnij_wpis`, `wybierz_kandydata`, `przypisz_recznie`,
  `cofnij_przypisanie`) albo `polecenie_niezapisane` (pozostale). Tekst mowi wprost "NIE", nazywa polecenie (napis
  przycisku) i miejsce (plytka i gniazdo albo kuweta). Kontroler pamieta nazwe i argumenty polecenia pod id komunikatu.
- **21. polecenie `ponow_polecenie(id komunikatu)`** ("Ponow teraz"): wykonuje to samo polecenie jeszcze raz - wszystkie
  sprawdzenia od nowa, osoba = wybrana teraz. Udane: komunikat znika. Odmowa przejsciowa (`KODY_DO_PONOWIENIA`: baza nadal
  zajeta, brak osoby, trwa analiza / skanowanie, blad polecenia): polecenie czeka dalej. Inna odmowa (np. `session` nie
  przyjmuje juz tej decyzji, biezaca kuweta jest inna): wpis znika, powod jest w komunikacie odmowy.
- Komunikat znika takze, gdy osoba kliknie te sama decyzje jeszcze raz i zapis sie uda (jedna pozycja na prace: nowa
  nieudana proba zastepuje poprzednia) albo zamknie komunikat ("Rezygnuje - nie zapisuj" = `zamknij_komunikat`). Udane
  polecenie dla INNEJ pracy go nie zdejmuje. Program sam decyzji NIE ponawia (decyzje zapisuje tylko klikniecie osoby;
  po restarcie programu lista do ponowienia jest pusta, a praca jest nadal "do obejrzenia").
- Polecenia, ktorych argumentow kontroler nie zna w calosci (ramki, Excel), dostaja zwykla odmowe `baza_zajeta` (bez
  przycisku ponowienia) - jak dotad.
- **Okno nie stoi.** Polecenie czeka na baze najwyzej `CZEKAJ_POLECENIA_MS` = 200 (`baza.Baza.czekanie`; prawdziwe
  czekanie na Windows: 0,30 s, gdy inny program pisze, 0,68 s, gdy trzyma baze na wylacznosc - `baza.md`), odczyt stanu
  po poleceniu / zdarzeniu `CZEKAJ_STANU_MS` = 100. Gdy stanu nie da sie odczytac, okno dostaje poprzedni stan z BIEZACYMI
  komunikatami ulotnymi (`_pokaz_komunikaty` - bez czytania bazy), a zegar okna ponawia odczyt co
  `OKRES_NADRABIANIA_STANU_S` = 1 s jedna proba bez czekania (`_nadrob_stan`; `KontrolerSesji.przetworz` i
  `Aplikacja.przetworz`). Zmierzone (atrapa, baza trzymana przez drugie polaczenie `BEGIN EXCLUSIVE`): przed 14,7-14,9 s,
  po 0,7 s - tabela w raporcie E3-P14.
- `Aplikacja.start_skanu` (Spacja): wpis `start_skanu` w dzienniku czeka na baze tak samo krotko; gdy baza jest zajeta,
  Spacja dziala (program czeka na plik), brakuje tylko wpisu dziennika (ostrzezenie w logu) - wczesniej 5 s i wyjatek.
- **`StanRano.nierozstrzygniete_prace`** (N3): krotka `NierozstrzygnietaRano` (`praca_id`, `skan_id`, `numer_plytki`,
  `gniazdo`, `klasa`) - prace dwuznaczne i nieznane BEZ decyzji osoby (nieznana ze swiadomym "Bez projektu" jest
  rozstrzygnieta), dla pieca otwartego, zamknietego i `ostatni_zamkniety`. Reguly liczenia `session_rano` bez zmian
  (takie prace nie licza sie przy "Zamknij piec"); pole sluzy oknu: pytanie przed zamknieciem i nazwanie prac po nim
  (`ui_rano.md`). Polecenie `zamknij_piec` kontrolera i klawisz "Zamknij piec" ramki NIE pytaja - pyta okno.
- Testy: `testy/test_p14_baza_zajeta.py` (11), `testy/test_p14_ekran.py` (N3).