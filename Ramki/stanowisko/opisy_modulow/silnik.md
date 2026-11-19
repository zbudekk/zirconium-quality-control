# silnik - analiza skanu w osobnym procesie (paczka E3-A2, 17.11.2026)

**Co robi.** Wykonuje `porownaj.porownaj` (plate -> match -> inspect) w OSOBNYM PROCESIE: kolejka zadan, jedna
analiza naraz, postep, wynik, obsluga awarii. Powod: Open3D w watku pod Qt zawisa (okno testowe: 195 s bez wyniku,
`raporty/P3a_przekazanie.md` pkt 5.1). Pliki: `stanowisko/silnik.py`, testy `testy/test_silnik.py`. Sam modul uzywa
tylko biblioteki standardowej - numpy, trimesh i Open3D laduje wylacznie proces roboczy (jest na to test).

**Wejscie.** `ZadanieAnalizy` (kontrakt z planu etapu 3, sekcja 3.8):

| Pole | Domyslnie | Znaczenie |
|---|---|---|
| `skan` | - | plik STL skanu |
| `pula` | - | `OpisPuli`: `foldery` projektow, `wspolczynnik` (None = domyslny dla rozpoznanej plytki, jak w wierszu polecen), `orientacja`, `wspolczynniki` (skrot projektu -> wspolczynnik pracy) |
| `tryb` | `wieczor` | wieczor / rano - dla odbiorcy wyniku; analiza od trybu nie zalezy |
| `uklad` | `auto` | `auto` albo `rozpoznaj` = program rozpoznaje uklad plytki (zalozenie Z2); inaczej nazwa z `[plytki]` |
| `numer` | brak | numer plytki, gdy dolki kodu sa poza skanem |
| `skan_sha16` | brak | skrot ze `ZdarzenieSkanu` - porownywany ze skrotem kopii roboczej (P1, N1); bez niego silnik liczy sam |
| `inspekcja`, `bez_filtru`, `straznik` | tak, nie, tak | jak w `porownaj` |
| `wyjscie` | brak | folder na `<czas przyjecia>_<sha16>[_n]_wynik.json` i `..._podglad.npz` (bez nazwy skanu, D-N6) |
| `zadanie_id`, `przyjete` | - | nadaje `zlec` (numer od 1 w kazdym obiekcie `Silnik`, czas przyjecia) |

Parametry `Silnik(...)`: `ust` (slownik ustawien) albo `plik_ustawien` (None = `ustawienia.toml` programu),
`funkcja` (`"modul:funkcja"` analizy; domyslnie `stanowisko.porownaj:porownaj`), `limit_zadania_s` (600),
`limit_startu_s` (180: od `Process.start()` do zgloszenia gotowosci przez proces roboczy), `pul_w_pamieci` (2),
`plik_logu` (wyjscie bibliotek z procesu roboczego), `pamiec_linii`
(katalog pamieci linii brzegu na dysku; domyslnie wylaczona), `katalog_roboczy` (kopie robocze skanow; domyslnie
`<katalog tymczasowy systemu>\qc_silnik`), `czekaj_na_plik_s` (60: jak dlugo ponawiac kopiowanie zajetego pliku skanu),
`na_zdarzenie`, `limit_uruchomienia_s` (30: limit samego `Process.start()`) i `proby_uruchomienia` (3) - E3-A2p, nizej.

**Wyjscie.** `ZdarzenieSilnika` do funkcji `na_zdarzenie` (wolanej w watku nadzorcy) albo do kolejki `Silnik.zdarzenia`:

| `typ` | Pola |
|---|---|
| `gotowy` | proces roboczy wystartowal (`czas_s` = czas startu) |
| `start` | zadanie wyslane do procesu (`zadanie_id`, `zadanie`) |
| `postep` | `etap`, `udzial` 0-1 (etapy z `porownaj`; przed analiza ewentualnie `oczekiwanie na zwolnienie pliku skanu` z udzialem 0, gdy plik trzyma inny program) |
| `wynik` | `wynik` = slownik `porownaj` w postaci z pliku `<skan>_wynik.json` (z `ostrzezenia`, jak w wierszu polecen; teksty wolne bez nazw z puli, pola decyzji bez zmian) + `zadanie_id` + `skan_sha16` (skrot kopii roboczej = tresci faktycznie analizowanej); `pliki` (sciezki z `wyjscie` TEGO zadania); `czas_s` |
| `blad` | `rodzaj`: `analiza` (wyjatek, brak pliku, pusta pula, brak miejsca na kopie robocza), `proces` (proces zniknal - `kod wyjscia` w komunikacie), `limit_czasu`, `start` (proces nie umie wystartowac), `plik_zmieniony` (plik nadpisany, zanim analiza ruszyla: skrot kopii inny niz w zdarzeniu skanu; oba skroty w komunikacie, bez analizy - nowa tresc ma wlasne zdarzenie), `plik_niedostepny` (pliku skanu nie dalo sie skopiowac przez `czekaj_na_plik_s` - inny program trzyma go bez zgody na odczyt albo brak uprawnien; nazwa pliku i powod systemu w komunikacie - POKAZAC technikowi, zlecic ponownie); `blad` (jedno zdanie), `szczegoly` (slad wyjatku), `czas_s` |
| `zatrzymany` | `niezakonczone` - krotka `ZadanieAnalizy` przerwanych przez `stop()` (w toku pierwsze, potem kolejka); wolane w watku, ktory wywolal `stop()` |

`..._podglad.npz`: dla kazdego gniazda z inspekcja tablice `g<nr>_P` (punkty w ukladzie plytki) i `g<nr>_d`
(odchylka w mm) - material na obraz odchylek w oknie; odczyt `silnik.wczytaj_podglad(plik)`. Pliki w `wyjscie` (P4, D-N6):
nazwa `<czas przyjecia RRRRMMDD_GGMMSS>_<sha16>` i kolejny numer `_n`, gdy taki plik juz jest - BEZ nazwy skanu (jak
w A1: program skanera moze nazywac eksport nazwiskiem ze zlecenia); zapis przez plik tymczasowy i zmiane nazwy bez
nadpisywania, najpierw `_podglad.npz`, potem `_wynik.json` (plik wyniku = komplet) - dwa skany `scan.stl` z dwoch
podfolderow i ponowna analiza tego samego skanu daja osobne komplety, a urwany zapis nie zostawia polowy pliku. Pliki
tymczasowe `*.<pid>.tmp` po procesie zabitym w trakcie zapisu sa usuwane przy kolejnym zapisie do tego folderu.

**Jak dziala.** `Silnik.start()` uruchamia watek nadzorcy (zwykly watek Pythona: bez Open3D i bez Qt) i proces roboczy
(`multiprocessing`, metoda `spawn`, lacze `Pipe` - bez wspolnych kolejek, wiec zabity proces niczego nie blokuje).
`zlec(zadanie)` / `zlec_skan(zdarzenie_skanu, pula)` dopisuje do kolejki i zwraca `zadanie_id`; `anuluj(id)` usuwa
zadanie, ktore jeszcze nie ruszylo. Nadzorca wysyla zadania po jednym, w kolejnosci zlecen. Awarie: wyjatek analizy
(takze `SystemExit` z `porownaj` przy pustej puli) = `blad` i nastepne zadanie w tym samym procesie; proces zniknal
(zabity, awaria biblioteki) albo przekroczyl `limit_zadania_s` = `blad` tego zadania, nowy proces, nastepne zadanie
(bez ponawiania zadania, ktore zabilo proces). Proces, ktory nie umie wystartowac (brak pakietu, zly plik ustawien),
oddaje `blad` rodzaju `start` kolejnym zadaniom - jedna proba na zadanie, bez petli restartow. Limit czasu nadzorca
sprawdza takze przy kazdej wiadomosci z procesu (zadanie, ktore stale przysyla postep, tez zostanie przerwane).
`stop()` konczy proces i ZWRACA zadania niezakonczone (w toku i w kolejce), zglaszajac je zdarzeniem `zatrzymany` (P2);
kolejne `stop()` zwraca []. Gwarancja (D-N3, D-N4): kazde przyjete zadanie albo dostaje dokladnie jedno zdarzenie
`wynik` / `blad`, albo jest na liscie `stop()` - nigdy oba; po rozpoczeciu `stop()` spoznione `wynik` / `blad` sa
odrzucane. Jedyny wyjatek: zadanie, ktorego zdarzenie koncowe nadzorca WLASNIE przekazuje, gdy `na_zdarzenie` blokuje sie
dluzej niz `czekaj_s` - nie ma go na liscie, a zdarzenie dojdzie po `zatrzymany`. `zlec` po rozpoczeciu `stop()` odmawia
wyjatkiem `SilnikZatrzymany` (podklasa `RuntimeError`): zadanie nie ruszy; gdy `stop()` jeszcze nie zebral listy, jest
na liscie niezakonczonych (`na_liscie` True), inaczej `na_liscie` False. Proces roboczy, ktory zaczal startowac, gdy
`stop()` juz ruszyl (wolny start), jest od razu zabijany.

Start procesu z limitem czasu (E3-A2p, 18.11). `Process.start()` (spawn, Windows) tworzy proces potomny i zapisuje mu do
lacza anonimowego dane startowe (dane przygotowania + obiekt procesu z ustawieniami - w programie ok. 5 KB, wiecej niz
bufor lacza 4 KB), wiec konczy sie dopiero, gdy potomek je przeczyta. Potomek, ktory zawisnie albo zginie przed odczytem,
zatrzymywal `Process.start()` na zawsze: uchwyt odczytu lacza trzyma tez proces okna (`popen_spawn_win32`, bpo-33929),
wiec smierc potomka zapisu nie konczy, a `limit_startu_s` liczyl sie dopiero po `start()` (D7 z raportu E3-A7: watek
`silnik-nadzorca` stal w `popen_spawn_win32.py:72`, analiza bez komunikatu). Teraz `start()` biegnie w watku pomocniczym
`silnik-start`, nadzorca czeka najwyzej `limit_uruchomienia_s` (30 s; normalnie start trwa ulamek sekundy - potomek
importuje tylko modul glowny programu), a co 0,5 s sprawdza, czy potomek jeszcze zyje (martwy juz nie przeczyta danych -
proba konczy sie od razu, z kodem wyjscia w opisie). Po przekroczeniu albo smierci potomka: opis potomka do logu (kod
wyjscia albo "dziala", czas CPU, uchwyty, zaladowane moduly), zabicie potomka, anulowanie zawieszonego zapisu
(`CancelSynchronousIo` na uchwycie watku), zamkniecie obu koncow `Pipe` i kolejna proba po 0,5 s. Potomka nadzorca zna
z `ProbaStartu` (runda 2, P1): pelnomocnik `_winapi` (nizej) zaraz po `CreateProcess`, jeszcze przed zapisem danych
startowych, wklada potomka do obiektu zadania procesu okna (D-N5 - ginie z procesem okna takze po porzuceniu proby)
i przekazuje nadzorcy `pid` oraz kopie uchwytu procesu. Watek, ktorego nie da sie odblokowac w 3 s (np. stoi w samym
`CreateProcess` - antywirus), zostaje porzucony: potomek z `CreateProcess`, ktory wroci po porzuceniu, jest zabijany od
razu (start konczy sie wyjatkiem przed zapisem), a proces, ktorego `start()` skonczy sie mimo to - zaraz po nim. Wyjatek z `start()` (np. blad
`CreateProcess`) to tez nieudana proba - przedtem wracal do petli nadzorcy co 0,2 s bez zadnego zdarzenia. Po
`proby_uruchomienia` (3) nieudanych probach: `blad` rodzaju `start` pierwszego zadania z kolejki (tekst "proces silnika
nie wystartowal: 3 proby uruchomienia nieudane (ostatnia: ...)", w `szczegoly` - kazda proba z opisem potomka); aplikacja
zleca zadanie raz ponownie, potem pokazuje komunikat "silnik nie startuje" (A3) i wstrzymuje skany do ponownego startu
programu. `stop()` w trakcie zawieszonego startu przerywa go od razu (bez czekania na limit). `stan()["nieudane_uruchomienia"]`
- liczba nieudanych prob od utworzenia obiektu; `limit_startu_s` liczony jest teraz od poczatku `Process.start()`.

Przyczyna zawieszen D7 (PC, 18.11, raport E3-A2p): proces potomny ginal przy starcie z kodem 0xC0000142
(STATUS_DLL_INIT_FAILED, czas CPU 0,00 s), zanim przeczytal dane startowe. W takim stanie z procesu testow ginal KAZDY
nowy proces podlaczany do jego konsoli (python.exe, `python -I -S`, cmd.exe, z minimalnym srodowiskiem, z przekierowanym
wyjsciem), takze 5-240 s pozniej, a startowaly procesy bez tej konsoli (`DETACHED_PROCESS`, `CREATE_NO_WINDOW`,
pythonw.exe). Wyczerpanie sterty pulpitu tego nie daje (zmierzone: 945 okien do bledu, potomkowie startuja). Dlatego
proces roboczy startuje z wlasna, niewidoczna konsola (`CREATE_NO_WINDOW`, stala `FLAGI_PROCESU_ROBOCZEGO`): biblioteka
standardowa wola `CreateProcess` z flagami 0, wiec `multiprocessing.popen_spawn_win32._winapi` jest zastapione
pelnomocnikiem (`_WinapiZFlagami`), ktory dodaje flage tylko w watku `silnik-start` (lokalna zmienna watku) i tylko przy
znanej postaci wywolania (9 argumentow pozycyjnych; inaczej bez flagi i jedno ostrzezenie w logu). Wywolania z innych
watkow ida bez zmian, z dowolnymi argumentami (runda 2, P2). Skutki: wyjscie procesu roboczego nie trafia juz do konsoli
okna. Po przekierowaniu w `_robotnik` program pisze je do `silnik.log` jak dotad; ginie wyjscie SPRZED przekierowania
(import modulu glownego programu jako `__mp_main__` w `spawn_main`, rozpakowanie argumentow, bledy krytyczne
interpretera) - przedtem widoczne w oknie `uruchom_stanowisko.bat`, w logach nigdy; zostaje kod wyjscia w logu nadzorcy
(runda 2, D1: przekierowanie juz w `CreateProcess` wymagaloby dziedziczenia uchwytu pliku logu przez `STARTUPINFO`
z lista uchwytow - poza zakresem; przy kodzie wyjscia potomka przy starcie sprawdzic recznie
`py -3.12 -c "import stanowisko.aplikacja"`). Ctrl+C w konsoli okna nie dociera do procesu roboczego. Program uruchomiony
przez pythonw - bez zmian (proces roboczy to wtedy pythonw.exe, bez konsoli; flaga nic nie zmienia). Dodatkowy proces
conhost.exe na czas zycia procesu roboczego. Znany wyciek biblioteki standardowej (runda 2, D3): kazda nieudana proba
zostawia w procesie okna 1 uchwyt (kopia konca `Pipe` dla potomka, ktory mial ja "ukrasc", a zginal wczesniej) - najwyzej
kilka na awarie (proby ogranicza logika A3).

Proces roboczy pilnuje sie sam (P6, `Straznik`): watek sprawdza co 0,5 s, czy zyje proces okna
(`multiprocessing.parent_process()`), i konczy proces roboczy od razu, gdy go nie ma (zmierzone: 0,4 s po zabiciu procesu
okna, gdy analiza zwalnia GIL). Ma tez wlasny limit zadania: `limit_zadania_s` + 30 s (nadzorcy moze juz nie byc).
`Straznik` nie dostaje czasu, gdy analiza stoi w wywolaniu natywnym trzymajacym GIL (zmierzone przez recenzenta:
`segment_plane`, `estimate_normals` w Open3D) - dlatego na Windows proces roboczy jest dodatkowo w obiekcie zadania
(Job Object) procesu okna z `KILL_ON_JOB_CLOSE` (D-N5, `ctypes`): system konczy go razem z procesem okna niezaleznie od
jego stanu (test z wywolaniem natywnym trzymajacym GIL 60 s: procesu roboczego nie ma 0,0 s po zabiciu okna).
`stan()["obiekt_zadania"]` mowi, czy sie udalo; gdy obiektu zadania nie da sie utworzyc albo przypisac, silnik dziala jak
dotad (sam `Straznik`, ostrzezenie w logu).

Kopia robocza skanu (N1, runda 3): proces roboczy kopiuje plik skanu do `katalog_roboczy\<pid>_<zadanie_id>\<nazwa
skanu>` przez `otworz_zrodlo` (pelne wspoldzielenie - program skanera moze w tym czasie pisac, przenosic i usuwac plik),
liczy skrot KOPII przy kopiowaniu i analizuje kopie (ta sama nazwa pliku, wiec `wynik["skan"]` jak w wierszu polecen).
Skrot kopii inny niz `skan_sha16` zdarzenia = plik nadpisany, zanim analiza ruszyla: `plik_zmieniony`, analiza nie rusza
(nowa tresc ma wlasne zdarzenie ze `scanner`). Pozniejsza blokada, przeniesienie albo usuniecie pliku skanu nie
uniewaznia wyniku - tresc analizowana i skrot sa z definicji te same. Plik zajety (inny program trzyma go bez zgody na
odczyt) albo zmieniajacy sie w trakcie kopiowania: ponawianie co 0,1 s, potem 2x, 4x ... rzadziej (najrzadziej co 2 s;
jak `scanner` B1), postep `oczekiwanie na zwolnienie pliku skanu`, po `czekaj_na_plik_s` blad `plik_niedostepny`.
Brak pliku = blad `analiza` "brak pliku skanu ...". Kopia jest usuwana po zadaniu; resztki po procesach zabitych w trakcie
zadania (i wlasne) sa usuwane przy starcie procesu roboczego i przed kazda kopia - na dysku jest najwyzej jedna kopia na
proces roboczy; kopie innych zyjacych procesow zostaja. Kopia powstaje tylko, gdy po niej zostanie 256 MB wolnego miejsca.
Koszt: 0,04-0,11 s na skan 46-55 MB (PC, 17.11).

Dane osobowe (P5, `CzyscicielNazw`): ostrzezenia, uwagi i teksty bledow z procesu roboczego (zdarzenia, pliki
w `wyjscie`) nie zawieraja nazw plikow ani folderow puli projektow - sciezka pod folderem puli i nazwa folderu =
`<projekt>`, nazwa pliku z puli (z rozszerzeniem albo bez) = `<projekt sha16>`; tylko cale nazwy (granice slowa
i separatory), najdluzsza najpierw. W wyniku czyszczone sa WYLACZNIE pola z tekstem wolnym (N2, runda 3:
`POLA_TEKSTU_WOLNEGO` - `ostrzezenia`, `uwagi`, `blad`, `powod`, `powod_filtru`, `komunikat`, `podpowiedz`, `opis` ...
i klucze konczace sie na `_` + jedno z nich, np. `uklad_komunikat`); statusy, typy, kolory, identyfikatory, nazwa skanu
i liczby nigdy nie sa zmieniane - folder `OK` albo plik `korona.stl` w puli nie zmienia `inspekcja.status` ani
`kandydaci[].typ`. Zostaja: sam folder puli z zadania (`foldery_projektow`), nazwy folderow z mniej niz 2 literami (numer
kuwety), rdzenie nazw plikow krotsze niz 3 znaki. Nazwy etapow postepu to stale z `porownaj` - nie sa czyszczone.

Pula projektow zostaje w pamieci procesu roboczego (`PamiecPul`): budowana raz na (foldery, wspolczynnik, orientacja,
lista plikow w folderach z rozmiarami i czasami) - zmiana plikow w folderze = nowa pula przy nastepnym zadaniu.
Razem z pula zostaja linie brzegu projektow (pamiec modulu `krawedz`), wiec druga i kolejne plytki nie licza ich od
nowa; `pamiec_linii` dodaje zapis tych linii na dysk (przezywaja restart procesu i programu).

W oknie Qt: `lacznik = lacznik_qt(silnik)` - obiekt z sygnalami `gotowy()`, `start(int)`, `postep(int, str, float)`,
`wynik(int, object)`, `blad(int, str, str)`, `zdarzenie(object)`, emitowanymi w watku okna (zegar Qt oproznia kolejke
`silnik.zdarzenia`). PySide6 jest importowane dopiero w `lacznik_qt`.

**Pomiary (PC wlasciciela, 17.11.2026).** Liczby i obciazenie komputera w chwili pomiaru: `raporty/E3-A2_2026-11-17.md`.

**Zalozenia i granice.**
- Wynik silnika a wiersz polecen: te same pola i te same decyzje, ale NIE rownosc bit w bit - `porownaj` nie jest
  powtarzalne nawet miedzy dwoma uruchomieniami wiersza polecen na tym samym skanie (zawsze szum rzedu 1e-15 z
  wielowatkowego ICP Open3D; czasem inna galaz ICP korekty skali jednego gniazda: `skala.iteracje` 20 albo 41,
  transformacja o ok. 1e-5, za tym liczniki punktow o 1 i miary o 0,001-0,05 mm). Testy na plytkach z atrap porownuja
  pole po polu z tolerancja 2e-3 dla liczb zmiennoprzecinkowych (liczniki probek o 2 albo 1 %, bez liczby iteracji),
  warianty na skanach odniesienia wymagaja rownych decyzji (struktura, statusy, identyfikatory) i liczb
  zmiennoprzecinkowych do 0,1 (prog posredni z recenzji); szczegoly w `testy/test_silnik.py` (`roznice`, `_rowne`)
  i w raporcie paczki.
- Import PySide6 dopiero PO wykonaniu prawdziwych analiz przez silnik w tym samym procesie konczyl sie na PC wlasciciela
  bledem "DLL load failed while importing Shiboken" (3 z 3 prob jednej sciezki testu; przyczyna nieustalona). E3-A2p runda 2:
  ten sam objaw przy `import sqlite3` - kilka sekund po zakonczeniu procesu roboczego w procesie okna znika uchwyt katalogu
  obiektow otwarty przy starcie procesu (najpewniej `\KnownDlls`), zamykany spoza kodu Pythona; zalezy od ukladu pamieci /
  czasu (raport E3-A2p). Dotyczy kazdego modulu z DLL ladowanego pierwszy raz po takim zdarzeniu.
  ZALECENIE dla A3: wszystkie uzywane moduly PySide6 (QtCore, QtGui, QtWidgets, wydruk ...) importowac W CALOSCI przy
  starcie programu - na poczatku `main()`, przed pierwszym uzyciem silnika - oraz test "analiza, potem pierwsze otwarcie
  kazdego okna".
- Plik startowy programu (A3) NIE moze importowac Qt na poziomie modulu (D8): proces roboczy (`spawn`) wykonuje go
  ponownie jako `__mp_main__`, wiec import Qt na gorze pliku laduje Qt w procesie liczacym obok Open3D (test
  `test_qt_w_procesie_roboczym_zalezy_od_pliku_startowego`: Qt w `main()` -> brak PySide6 w procesie roboczym; Qt na
  gorze -> jest). Importy Qt w `main()`, reszta modulu bez skutkow ubocznych. W wersji zamrozonej (DY1) dochodzi
  `multiprocessing.freeze_support()` na poczatku `main()`.
- Czas plytki to czas `porownaj`; silnik dodaje start procesu (jednorazowo, 2-4 s) i oszczedza budowe puli oraz linii
  brzegu od drugiej plytki. Pierwsza plytka po starcie procesu (takze po awarii) placi za pule i linie brzegu
  dopasowanych projektow - stad `pamiec_linii` i miejsce na "rozgrzewke" puli w A3 / A5.
- Jedna analiza naraz i jeden proces (plan 3.8); rownolegle analizy nie sa przewidziane.
- Program uruchamiajacy silnik musi miec glowny modul chroniony `if __name__ == "__main__":` (wymaganie
  `multiprocessing` na Windows); proces roboczy wykonuje glowny modul programu (patrz D8 wyzej).
- Nazwa pliku skanu zostaje w komunikatach (np. "brak pliku skanu ...") i w polu `wynik["skan"]`; w nazwach plikow
  `wyjscie` juz nie (D-N6). Nazwy z puli nie wychodza nigdzie.
- Kolejka zadan zyje w pamieci procesu okna. Po zamknieciu programu nic nie ginie, o ile A3: (1) w `closeEvent` wola
  NAJPIERW `scanner.stop()`, POTEM `niezakonczone = silnik.stop()` (odwrotna kolejnosc: `zlec_skan` z watku obserwatora
  dostaje `SilnikZatrzymany` - zadanie jest na liscie, gdy lista nie byla jeszcze zebrana, inaczej wraca dopiero przez
  nadrabianie) i zapisuje zwrocone zadania (sciezka, `skan_sha16`, tryb, numer) w bazie albo pliku; (2) po starcie zleca je
  ponownie (`zlec` nadaje nowe numery); (3) przy awarii bez `stop()` - nadrabianie w `scanner` (`znane`). `na_zdarzenie`
  nie moze czekac na watek wolajacy `stop()` (najprosciej `lacznik_qt`). Bez `stop()` przy wyjsciu zostaje kosmetyczny
  slad "Exception ignored in atexit" (D2); proces roboczy i tak konczy sie sam (obiekt zadania, `Straznik`).
- Kopia robocza (N1): katalog roboczy musi miec miejsce na jedna kopie skanu + 256 MB (inaczej blad `analiza` z powodem).
  Program skanera, ktory nadpisuje plik w miejscu w trakcie kopiowania, daje kopie, ktorej skrot nie zgadza sie ze
  zdarzeniem (`plik_zmieniony`) albo ponowienie kopii; plik trwale bez uprawnien do odczytu = `plik_niedostepny` po 60 s.
- Obiekt zadania (D-N5) obejmuje tez procesy uruchomione przez proces roboczy (dzis zadnych). Bez Windows albo przy
  odmowie systemu zostaje sam `Straznik` - zawieszenie w wywolaniu natywnym trzymajacym GIL zostawia wtedy proces roboczy
  do konca tego wywolania.
- `zadanie_id` liczy sie od 1 w kazdym obiekcie `Silnik` (po `stop()` trzeba utworzyc nowy); sygnaly `wynik(int, object)`
  i `blad(int, str, str)` lacznika niosa tylko numer - A3 kluczuje po obiekcie silnika albo bierze `zdarzenie(object)`
  (D7). `zatrzymany` przychodzi tylko przez `zdarzenie(object)`.
- Priorytet procesu roboczego jest zwykly (okno "Dzien skanera" obniza priorytet swojej kontroli - tu nie, bo wynik ma
  byc szybko; do decyzji po probach na laptopie stanowiska, D4).
- Proces roboczy, ktory zglasza gotowosc i ginie bez zadania, jest uruchamiany od nowa bez licznika (D4 b, malo
  prawdopodobne).

## Pula per praca w silniku (E3-A5i, 19.11.2026)

**Opis puli.** `OpisPuli(wpisy=..., sciezki=..., korzenie=...)`: `wpisy` - wpisy puli dnia (`pula.Wpis` albo slowniki: `sha16`,
`wspolczynnik`, `krazek`, `frezowanie_id`, `projekt_id`), `sciezki` - `projekt_id` -> plik STL (`KatalogPul.sciezki`; DANE OSOBOWE:
tylko w procesie roboczym, poza `repr`), `korzenie` - zrodla zlecen ("Cyrkon", "Prywatne") do czyszczenia sciezek z komunikatow.
`opis.per_praca` = sa wpisy. Bez wpisow - pula z folderu jak dotad (`foldery` ma teraz wartosc domyslna `()`).

**Budowa.** `PamiecPul(limit, ust)` trzyma jedna `pamiec_puli.PamiecPuli` na proces roboczy (`[sciezki] pula_cache` / `projekty`,
`pamiec_puli.z_ustawien`) i buduje `match.Pula.z_wpisow(wpisy, sciezki, pamiec=...)`; czesci lekkie zostaja w procesie, wiec pula po
odswiezeniu (nowe wiersze CSV) liczy tylko nowe geometrie. Klucz puli w procesie: wpisy, pliki z rozmiarem i czasem zmiany,
orientacja (plik zmieniony = nowa pula). Dla puli per praca `pula_dla(w)` nie zalezy od wspolczynnika plytki. Postep budowy:
rozgrzewka czesci lekkich kazdej geometrii (`pamiec.lekki`, ta sama regula sciezki i wspolczynnika co `z_wpisow`), potem
`z_wpisow` bierze je z pamieci procesu.

**Regula zimnej puli (wybrana w E3-A5i): skany czekaja w kolejce silnika, az pula wpisow sie zbuduje.** `Silnik.przygotuj_pule(opis)`
(ostatnie wywolanie wygrywa, None = nic) - nadzorca wysyla pule do procesu roboczego, gdy ten jest gotowy i wolny, PRZED kolejnym
zadaniem z kolejki; zadanie trwajace konczy sie najpierw. Zdarzenia `ZdarzenieSilnika(typ="pula")`: `etap` start / budowa
(`wynik` = {gotowe, razem} najczesciej co `ODSTEP_POSTEPU_PULI_S` = 0,25 s) / gotowa (`wynik` = `Pula.opis()` - liczniki
`wpisow`, `geometrii`, `brak_pliku`, `plik_zmieniony`, `bez_wspolczynnika`, `pominiete`, statystyka pamieci - oraz
`czas_przygotowania_s`) / blad. Proces bez postepu budowy dluzej niz `limit_zadania_s` = zabity; smierc procesu w trakcie
budowy = nowa proba po restarcie, po `PROBY_PRZYGOTOWANIA_PULI` (2) takich z rzedu koniec prob; wyjatek budowy (nie smierc) - bez
ponawiania. W obu przypadkach zadania ida dalej i buduja pule same (bez postepu). Po kazdym restarcie procesu roboczego (awaria,
limit czasu) pula zadana buduje sie od nowa sama. `stan()["pula"]` = {zadana, w_toku, gotowa, gotowe, razem}.
Dlaczego nie "skany na pule z folderu do czasu gotowosci": pula z folderu to caly "Cyrkon" z jednym wspolczynnikiem (inny krazek =
zla skala) i budowa takiej puli trwa dluzej niz pula wpisow; analiza w drugim watku obok budowy - Open3D / BLAS w watkach (plan 3.8).
Pomiar (PC, test `test_k2_k3_*`): zimna pula 24 wpisow + 3 skany w trakcie budowy - 30 s, petla okna max 61 ms; restart z ciepla
pamiecia - budowa 0,14 s (4,3 s od startu programu). Pula 400 wpisow zimna: ok. 5 min (raport E3-A5) - skany tyle czekaja.

**Sprzatanie i pamiec linii.** `Silnik(pamiec_puli_dni=N)` - przy starcie procesu roboczego `PamiecPuli.sprzataj(N)` (wpisy
nieuzywane od N dni; liczba usunietych w `stan()["pamiec_puli_usuniete"]`, wiadomosc `sprzatanie`). `pamiec_linii` jest ustawiana,
gdy modul `krawedz` jest juz zaladowany (funkcja analizy `porownaj` laduje go przy starcie) - proces z funkcja, ktora krawedzi nie
uzywa, nie laduje Open3D tylko po to (program wlacza pamiec linii domyslnie od E3-A5i).

**Dane osobowe.** `CzyscicielNazw(foldery, pomin, pliki=..., korzenie=...)`: dla puli wpisow nazwy plikow z `OpisPuli.sciezki`, ich
rdzenie i nazwy folderow zlecen -> `<projekt sha16>` / `<projekt>`, pelne sciezki pod `korzenie` -> `<projekt>` (bez przegladania
drzewa "Cyrkon"; P3 recenzji PR #25). Blad budowy puli wraca do nadzorcy po tym samym czyszczeniu.
