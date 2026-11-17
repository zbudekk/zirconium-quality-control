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

**Co okno wysyla** (kazde polecenie zwraca `Odpowiedz(ok, tekst, kod, dane)`; odmowa to odpowiedz i komunikat w stanie, nigdy wyjatek): `wybierz_operatora(nazwa)`, `ukruszona(praca_id)`, `ok(praca_id)`, `cofnij(praca_id)`, `potwierdz_ponowny_skan(skan_id)`, `odrzuc_ponowny_skan(skan_id)`, `cofnij_zastapienie(skan_id)`, `dopusc_plytke(skan_id)`, `cofnij_dopuszczenie(skan_id)`, `podaj_numer_plytki(skan_id, numer)`, `zamknij_pytanie(id)` ("pozniej"), `zamknij_komunikat(id)`, `start_skanu()` (Spacja), `ustaw_pule(folder, wspolczynnik)`, `odswiez_pule()`, `zamknij()`; `wykonaj(nazwa, *argumenty)` wola polecenie po nazwie.

**Sygnaly.** `lacznik = kontroler_api.lacznik_qt(kontroler)`: `stan_zmieniony(object)`, `postep(object)`, `komunikat(object)`, `pytanie(object)`, `zamkniety()`; zegar lacznika co 30 ms wola `kontroler.przetworz()` (bez tego zdarzenia skanera i silnika czekaja w kolejkach). Bez Qt: `kontroler.subskrybuj(funkcja)` + wlasne wywolania `przetworz()`.

**Czego oknu nie wolno.** Siegac do `session` / `baza` / `scanner` / `silnik` z pominieciem kontrolera; trzymac wlasnych kolorow i napisow statusow (tylko `statusy.py` i pola stanu); pokazywac sciezek i nazw plikow (stan ich nie zawiera - poza `pula.folder` i `skaner.folder`, ktore sa ustawieniami); zmieniac obiektow stanu; wolac kontrolera z innego watku; otwierac okien modalnych (`exec`) w slotach sygnalow - zagniezdzona petla okna dostarcza wtedy nowszy stan przed koncem obslugi starszego (stan o nizszej `wersja` trzeba pominac); importowac Qt na poziomie modulu w pliku startowym.

**Miejsce na ekran.** `aplikacja.utworz_okno(kontroler, lacznik)` importuje pakiet `stanowisko.ui` i wola `ui.utworz_okno(kontroler, lacznik)` (okno Qt, jeszcze niepokazane); dopoki pakietu nie ma, `main()` pokazuje okno zastepcze z tekstem stanu. `closeEvent` okna nie musi niczego robic: `main()` wola `kontroler.zamknij()` po wyjsciu z petli (i przez `aboutToQuit`).

**Atrapa.** `AtrapaKontrolera()` - prawdziwa `Sesja` na bazie w katalogu tymczasowym, bez skanera i silnika: `symuluj_skan(rodzaj, numer=, gniazda=, projekty=)` (rodzaje: zwykla, czysta, do_powtorzenia, niezgodny_uklad, nie_z_trybu, bez_numeru, blad), `symuluj_postep`, `symuluj_komunikat(rodzaj)`, `scenariusz_pokazowy()`; pliki podgladu sztuczne (ten sam format, co z silnika). `py -3.12 -m stanowisko.aplikacja --atrapa` pokazuje okno na tych danych. `sztuczny_wynik(...)` i `kolory_oczekiwane(...)` - dane i prawda dla testow.

## Jak dziala `Aplikacja`

- **Start** (`Aplikacja(ust)`, `start()`): baza i sesja z `ustawienia.toml`; silnik z `ust` (proces sam nie czyta pliku); uklady plytek z `[plytki]` wczytane od razu (numpy laduje sie przy starcie, nie w petli okna przy pierwszej plytce); liczenie puli w tle; zadania z `dane/zadania_niezakonczone.json` zlecane ponownie; dopiero potem `Scanner(..., znane=ZnanePliki(<wszystkie wiersze skany> + <zadania wznowione>))` - skany zapisane, gdy program nie dzialal, wracaja z `zastany=True` i sa analizowane (komunikat `wznowiono` z liczba), a pliki juz przyjete nie sa zglaszane.
- **Powtorki** (zaden skan liczony dwa razy): ta sama tresc (`sha16`) co skan, ktory MA wynik w bazie (kazdy status poza `blad`), albo co zadanie czekajace w kolejce - nie jest liczona ponownie (wpis `skan_powtorzony` w dzienniku; na zywo komunikat `skan_juz_jest`). Samo zobaczenie pliku niczego trwale nie zapisuje, wiec awaria miedzy zdarzeniem a wynikiem nie gubi skanu.
- **Wynik** -> `session.przyjmij_wynik`; wpis `podglad` w dzienniku wiaze skan z plikiem `*_podglad.npz` (oba w jednej transakcji = jeden zapis na dysk); kopia wyniku zapisana przez silnik (zawiera folder puli) jest usuwana - zostaje plik sesji bez sciezek. Baza zajeta: wynik czeka w pamieci i jest zapisywany ponownie co 1 s.
- **Bledy silnika:** `analiza` / `proces` / `limit_czasu` -> `session.przyjmij_blad` (skan `blad`, wpis `blad_analizy_rodzaj`) + komunikat `blad_analizy`; `plik_zmieniony` -> tylko komunikat i wpis w dzienniku (nowa tresc ma wlasne zdarzenie); `plik_niedostepny` -> komunikat i ponowne zlecenie `[silnik] ponow_plik_niedostepny` razy (3), potem skan `blad` z komunikatem `plik_niedostepny`; `start` (proces analizy nie umie wystartowac) -> jedna ponowna proba, potem skany CZEKAJA z komunikatem `silnik_nie_startuje` (nie dostaja bledu, wracaja po restarcie programu).
- **Pula projektow - poziom 1 planu:** jeden folder (domyslnie `[sciezki] folder_cyrkon`) + wspolczynnik wpisany recznie (None = domyslny dla rozpoznanego typu plytki, jak w oknie testowym); wybor technika zapisany w `dane/stanowisko_pula.json`. Liczba STL liczona w watku pomocniczym (regula jak `synth.pliki_projektow`). Pula pusta albo bez folderu: skany czekaja (`kolejka.wstrzymane`, komunikat) do "Odswiez pule" - nie dostaja bledu analizy. Katalog i pule z bazy: paczki A4 / A5.
- **Start skanu (DW5):** `start_skanu()` wola `Scanner.start_skanu` dokladnie raz; akcja to atrapa (parametr `start_skanu=`), prawdziwa powstanie po probach na skanerze (B2). Zadnego automatu klikajacego.
- **Zamkniecie** (`zamknij()`): `scanner.stop()`, potem `silnik.stop()`; wyniki, ktore zdazyly przyjsc, sa przyjmowane; zadania w toku, w kolejce i wstrzymane -> `dane/zadania_niezakonczone.json` (sciezka, `sha16`, rozmiar, czas pliku, tryb, numer); plik znika po wczytaniu przy starcie. Awaria bez `zamknij`: pliku nie ma, skany bez wyniku wracaja przez nadrabianie folderu.
- **Watek.** Wszystko w watku okna; `scanner` i watek liczenia puli wkladaja zdarzenia do kolejki, silnik do `silnik.zdarzenia`; `przetworz()` obsluguje je najwyzej 50 ms naraz. Blad obslugi jednego zdarzenia = wpis w logu i nastepne zdarzenie.

## Reguly ponad `session` (do potwierdzenia przez wlasciciela - lista w raporcie paczki)

1. **Operator na zmiane:** wybor osoby wygasa, gdy zmieni sie numer zmiany (6 / 14 / 22) i po kazdym starcie programu - komunikat `nowa_zmiana`, decyzje odrzucane do wyboru osoby.
2. **"Ukruszona" na pracy, ktorej program nie oznaczyl na czerwono,** zapisuje sie jako `ukruszona_niewykryta` (SE9, tryb cienia); na czerwonej - `ukruszona`.
3. **Plytka bez numeru:** prace zielone maja status `czeka_na_numer` i nie maja koloru (nic zielonego) do podania numeru; czerwone i zolte sa widoczne, decyzje sa przyjmowane. Wylacznik: `statusy.ZIELONE_BEZ_NUMERU_PLYTKI`.
4. **Odrzucenie propozycji ponownego skanu** ("to nowy wsad") wymaga operatora, jest zapisywane w dzienniku (`ponowny_skan_odrzucony`) i nie wraca po restarcie; zastapienie wprost nadal dziala. "Pozniej" (`zamknij_pytanie`) i `zamknij_komunikat` ukrywaja pozycje tylko do konca pracy programu.
5. **Z9:** `pomaranczowy` = "poprawiana recznie", `dofrezowany` (bursztyn, rano - A6) = "zab dofrezowany".

## Ustawienia (wszystkie nowe klucze opcjonalne; plik sprzed etapu 3 wczytuje sie bez zmian)

`[sciezki] podglady = "dane/podglady"`, `pula_cache = "dane/pula_cache"` (pamiec linii brzegu silnika), `logi = "dane/logi"`; `[scanner] stabilizacja_ms, min_rozmiar_mb, min_trojkatow, wzorzec_pliku, rekurencyjnie, obserwator`; `[silnik] limit_zadania_s, czekaj_na_plik_s, pamiec_linii, ponow_plik_niedostepny`. Wartosci domyslne rowne stalym modulow `scanner` i `silnik` (test). Uzywane bez zmian: `[sciezki] folder_eksportu_skanera, folder_cyrkon, baza, wyniki`, `[sesja]`.

## Dane osobowe

Komunikaty, stan, sygnaly, dziennik i log tego modulu nie zawieraja nazw plikow ani folderow (skanu, puli, zlecen) - skan opisuje `sha16`; teksty bledow z silnika sa czyszczone z nazwy i folderu pliku skanu, zanim trafia do `session`. Test `test_i_...`: fikcyjna nazwa folderu zlecenia uzyta jako podfolder puli i podfolder folderu skanera - 0 wystapien w logu, stanie, sygnalach, dzienniku, plikach wynikow i liscie "do dofrezowania". Znane granice: (1) `skany.plik` = sciezka pliku skanu (kolumna z planu, pisze `session`); (2) `dane/zadania_niezakonczone.json` (sciezki skanow czekajacych na analize, istnieje miedzy zamknieciem a startem) i `dane/stanowisko_pula.json` (folder puli) - pliki robocze obok bazy, poza repo; (3) log `scanner` (poziom INFO) zawiera nazwe pliku skanu, a `silnik` - "brak pliku skanu <nazwa>" - do rozstrzygniecia po pierwszych skanach (B2), jak w `scanner.md`; (4) po awarii miedzy zapisem plikow silnika a przyjeciem wyniku w `dane/podglady` moze zostac kopia `*_wynik.json` z folderem puli.

## Kryterium "dziala"

`test_kontroler_api.py`: kazdy test kontraktu w dwoch wariantach (atrapa / prawdziwa aplikacja z funkcja analizy na danych sztucznych w procesie silnika) - kolory gniazd = wynik analizy po decyzjach w 100 % gniazd, decyzje i odmowa bez operatora, start skanu, plytka niezgodna / do powtorzenia / nie z trybu / bez numeru (nic zielonego), ponowny skan (pytanie z liczba decyzji, potwierdzenie, cofniecie, odrzucenie, po 61 min nowy wsad), "zab juz na liscie", operator na zmiane, pula, sygnaly, `lacznik_qt`, zamkniecie. `test_aplikacja.py`: prawdziwa analiza `porownaj` na plytce z atrap zapisanej przez symulator skanera, zamkniecie w trakcie analizy i restart, awaria bez zamkniecia, powtorki, petla Qt przy 10 plytkach, pula pusta, `plik_zmieniony`, `plik_niedostepny`, zabity proces, silnik bez startu, baza zajeta, folder skanera pojawiajacy sie pozniej, nazwy zlecen, kolejnosc zamykania, parametry z ustawien, plik startowy bez Qt, `main()`. Wariant na duzych sztucznych skanach (45-55 MB) i puli prawdziwych projektow przez cala aplikacje w petli Qt: zmienne `E3A3_DANE_REF` (folder `skan_<typ>_n*.stl`) i `E3A3_PROJEKTY` (folder puli), bez nich pomijany; z `-s` wypisuje czasy, najdluzsza przerwe petli okna i najdluzsze kroki w watku okna. Liczby: `raporty/E3-A3a_2026-11-17.md`.

## Zalozenia i granice

- Tylko tryb `wieczor`; ekran poranny, sesja pieca, ramki i Excel to kolejne paczki. Stan pokazuje biezaca dobe robocza (06:00-06:00) - o 6:00 plytki znikaja z mapy, lista biezaca "do dofrezowania" zostaje.
- Nie ma polecenia "analizuj ten skan ponownie" (np. po zmianie wspolczynnika): ta sama tresc pliku ma juz wynik i jest odsiewana - plytke trzeba zeskanowac jeszcze raz. Do decyzji, czy dodac.
- Rozstrzygniecie konfliktu projektu (ten sam projekt w dwoch gniazdach), `wybor_kandydata` i `przypisanie_reczne` nie sa obslugiwane przez `session` - stan podaje `konflikty` i komunikat, bez polecenia.
- Liczba STL to liczba plikow w folderze, nie liczba projektow, ktore analiza zdola wczytac; folder sieciowy z tysiacami plikow jest listowany przy kazdym odswiezeniu (w tle) i przez silnik przy kazdym zadaniu - pomiar na prawdziwym folderze: A4 / A5.
- Skan `blad` (takze `plik_niedostepny` po ponowieniach) jest "znany": po restarcie nie jest analizowany sam; ten sam plik zapisany ponownie albo skopiowany pod inna nazwa - tak.
- Wynik, ktory czekal na zajeta baze, a program zostal zamkniety: zadanie wraca do pliku zadan i skan jest liczony od nowa po starcie.
- Okno zastepcze w `aplikacja.py` jest tylko po to, zeby program dal sie uruchomic przed A3b.
- Prawdziwa akcja "start skanu", nazwy i sposob zapisu plikow prawdziwego skanera: po dniu skanera (B2).
