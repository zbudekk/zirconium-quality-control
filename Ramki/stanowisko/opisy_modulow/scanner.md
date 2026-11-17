# scanner - obserwacja folderu eksportu skanera (paczka E3-A2, 17.11.2026)

**Co robi.** Patrzy na folder, do ktorego program skanera zapisuje pliki, i dla kazdego nowego pliku STL zglasza
zdarzenie "nowy skan" - dopiero po koncu zapisu i po sprawdzeniu pliku. Plik zly nie daje zdarzenia, tylko wpis
z powodem. Pliki: `stanowisko/scanner.py`, symulator do prob bez skanera `narzedzia/symulator_skanera.py`,
testy `testy/test_scanner.py`. Modul nie laduje numpy, trimesh, Open3D ani Qt (dziala w procesie okna, w zwyklym watku).

**Wejscie.** Folder (docelowo `[sciezki] folder_eksportu_skanera`) i parametry konstruktora `Scanner(...)`:

| Parametr | Domyslnie | Znaczenie |
|---|---|---|
| `wzorzec_pliku` | `*.stl` | wzorzec NAZWY pliku (bez rozrozniania wielkosci liter); inne pliki = wpis `poza_wzorcem` |
| `rekurencyjnie` | tak | czy patrzec w podfoldery (struktury folderu zlecenia nie zakladamy) |
| `stabilizacja_ms` | 300 | tyle bez zmiany rozmiaru i czasu pliku, zanim plik jest oceniany |
| `min_trojkatow` | 1 | mniej trojkatow = wpis `za_malo_trojkatow` |
| `min_rozmiar_mb` | 0 (bez progu) | mniejszy plik = wpis `za_maly` |
| `odrzuc_po_s` | 5 | plik zly i niezmieniany przez tyle sekund = wpis z powodem |
| `okres_s`, `przeglad_s` | 0,05 i 2 | co ile watek oglada pliki, na ktore czeka; co ile przeglada caly folder |
| `zglos_zastane` | nie | czy WSZYSTKIE pliki zastane (obecne przy pierwszym udanym przegladzie) sa nowymi skanami |
| `zglos_zastane_od` | brak | nadrabianie po restarcie: pliki zastane o czasie modyfikacji POZNIEJSZYM niz podany (sekundy od epoki) |
| `znane` | brak | nadrabianie po restarcie: funkcja `znane(sciezka, rozmiar, mtime_ns) -> bool` (True = plik juz przyjety; pytana raz na plik zastany, bez czytania pliku, TYLKO w watku obserwatora - kontrakt nizej; gotowa wersja z bazy A1: `ZnanePliki`); z `zglos_zastane_od` dziala razem (nowszy ORAZ nieznany) |
| `informuj_po_s`, `informuj_co_s` | 10 i 60 | plik zajety dluzej niz tyle = `Oczekiwanie`; kolejne co tyle |
| `obserwator` | `watchdog` | `odpytywanie` = bez biblioteki watchdog (np. dysk sieciowy), sam przeglad co `przeglad_s` |
| `start_skanu` | atrapa | funkcja akcji "start skanu" (patrz nizej) |

Podpiecie do `ustawienia.toml` robi paczka A3 (proponowane klucze `[scanner]`: `stabilizacja_ms`, `min_rozmiar_mb`,
`min_trojkatow`, `wzorzec_pliku`).

**Wyjscie.** `ZdarzenieSkanu` (kontrakt z planu etapu 3, sekcja 3.8): `plik`, `sha16` (16 znakow SHA-256 zawartosci),
`rozmiar`, `trojkaty`, `czas_pliku` (+ `mtime_ns`), `czas_zdarzenia`, `nr` (kolejny numer), `ponowny` (ta sama sciezka
byla juz zgloszona), `duplikat` i `duplikat_z` (ta sama zawartosc byla juz zgloszona pod inna nazwa - wskazanie
pierwszego pliku), `zastany` (plik byl w folderze przy starcie i zostal zgloszony przez nadrabianie). `Odrzucenie`:
`plik`, `powod`, `opis`, `rozmiar`, `czas`. `Oczekiwanie` (informacja, nie odrzucenie): `plik`, `od_s` (od ilu sekund
zajety), `opis` ("czeka na zwolnienie pliku ..."), `czas`. Trafiaja do funkcji `na_skan` / `na_odrzucenie` /
`na_oczekiwanie` (wolanych w watku obserwatora) albo, gdy ich nie podano, do kolejki `Scanner.zdarzenia`; odrzucenia
sa tez w `Scanner.odrzucone` (ostatnie 1000), wszystko w logu `stanowisko.scanner` (same nazwy plikow, bez sciezek).
`stan()`: `folder_dostepny`, `obserwator`, `startow_watchdog`, `zdarzen`, `odrzucen`, `oczekiwan`, `czeka`, `zajete`, `dziala`.

| Powod odrzucenia | Kiedy |
|---|---|
| `pusty` | 0 bajtow |
| `za_krotki` | mniej niz 84 bajty (naglowek binarnego STL) |
| `rozmiar_niezgodny` | rozmiar inny niz 84 + 50 x liczba trojkatow z naglowka: plik uciety, uszkodzony albo nie-STL |
| `stl_tekstowy` | STL tekstowy (zaczyna sie od `solid`, sam tekst) - program przyjmuje tylko binarny |
| `za_malo_trojkatow`, `za_maly` | ponizej progow z konstruktora |
| `poza_wzorcem` | nazwa nie pasuje do wzorca (jeden wpis na plik) |

Pliku, ktorego nie da sie otworzyc, obserwator NIE odrzuca (`sprawdz_stl` zwraca wtedy `blad_odczytu`, ale to stan
"zajety", patrz nizej).

**Jak dziala.** Biblioteka `watchdog` powiadamia o zmianach w folderze; niezaleznie co `przeglad_s` caly folder jest
przegladany (zgubione powiadomienia, folder, ktory pojawil sie pozniej, watchdog, ktory nie wystartowal). Kazdy plik,
ktory sie zmienil, jest "kandydatem". Koniec zapisu = wszystkie warunki naraz: (1) rozmiar i czas pliku bez zmian przez
`stabilizacja_ms`; (2) rozmiar zgodny z naglowkiem; (3) zaden program nie trzyma pliku otwartego do zapisu (Windows);
(4) po policzeniu skrotu rozmiar i czas nadal te same. Plik stabilny, ale zly, czeka `odrzuc_po_s` (moze byc dopisywany
z przerwami) i dopiero wtedy dostaje wpis (przed wpisem jeszcze raz sprawdzany rozmiar i czas - plik dopisany do konca
w tej chwili nie dostaje falszywego wpisu); odrzucenie nie jest ostateczne - po zmianie pliku ocena zaczyna sie od nowa.
Kilka plikow gotowych w tym samym obiegu jest zglaszanych w kolejnosci czasu zapisu. Plik zapisany ponownie pod ta sama
nazwa (nowy czas albo rozmiar) daje nowe zdarzenie z `ponowny`; plik usuniety i zapisany znowu - takze.

Plik zajety (B1, recenzja PR #17): inny program trzyma go bez zgody na odczyt (`File.Create` / `File.OpenWrite` w .NET,
podglad w programie skanera, antywirus, kopia zapasowa) albo plik jest kompletny, ale jeszcze otwarty do zapisu. To stan
przejsciowy: proby co `okres_s`, potem 2x, 4x ... rzadziej (najrzadziej co 2 s; dla pliku otwartego do zapisu co 0,25 s),
bez limitu liczby prob; po `informuj_po_s` (10 s) `Oczekiwanie` dla technika, powtarzane co `informuj_co_s` (60 s).
Plik zajety nie trafia do plikow znanych: po zwolnieniu przechodzi zwykla ocene i daje jedno zdarzenie; po restarcie
programu wraca przez nadrabianie (`znane` / `zglos_zastane_od`). Trwaly brak uprawnien do pliku wyglada tak samo
(`Oczekiwanie` co minute) - nic nie ginie po cichu.

Pliki zastane (P3). Stan poczatkowy ustala PIERWSZY udany przeglad folderu - przy starcie albo pozniej, gdy folder
(dysk sieciowy, OneDrive) pojawi sie po starcie z cala historia. Podfolder albo plik, ktorego przy tym nie dalo sie
odczytac, jest "zastany" przy pierwszym udanym odczycie. Zastany jest tylko plik o czasie modyfikacji NIE pozniejszym
niz start obserwatora (D-N1, runda 3): plik zapisany po starcie jest nowym skanem takze w folderze, ktory pojawil sie
pozniej (program skanera zaklada folder przy pierwszym eksporcie, dysk podlaczony po starcie), i w podfolderze
nieczytelnym przy starcie - bez nadrabiania nic nie przepada. Chwilowy blad listowania (folder albo podfolder
niedostepny, pusta lista) nie kasuje wiedzy o znanych plikach: plik nieobecny na liscie jest zapominany dopiero, gdy
`os.stat` mowi, ze go nie ma (albo watchdog zglosi usuniecie). Nadrabianie po restarcie (P2): z `zglos_zastane_od`
i / albo `znane` pliki zastane nowsze / nieznane ida zwykla droga i daja zdarzenie z `zastany=True` (w kolejnosci czasu
pliku); skrot liczony tylko dla nich, nie dla calej historii folderu. Pliki zastane sa ustalane w `start()` (przed
powrotem), a decyzja nadrabiania (wywolania `znane`) zapada w pierwszym obiegu watku obserwatora - nigdy w watku okna.
Folder usuniety i utworzony od nowa (D1): przeglad sprawdza,
czy watek watchdog zyje i czy folder ma ten sam numer pliku - jesli nie, obserwator watchdog rusza od nowa.
`stop()`, ktory nie doczekal sie konca watku (liczenie skrotu duzego pliku), zostawia watek widoczny w `dziala()`;
watek niczego juz nie zglasza, a `start()` nie uruchamia drugiego (D11).

**Kontrakt `znane` (D-N2, runda 3).**
- WATEK: wolana wylacznie w watku obserwatora (`scanner`; w testach w watku, ktory sam wola `obieg()`), po jednym
  wywolaniu naraz, nigdy w watku wolajacym `start()`. Nie moze uzywac obiektow przywiazanych do innego watku (polaczenie
  `sqlite3` otwarte w watku okna rzuca `ProgrammingError`; wyjatek = plik "nieznany", zgloszony drugi raz).
- ARGUMENTY: `sciezka` = `folder / sciezka wzgledna` (jak `ZdarzenieSkanu.plik`), `rozmiar` w bajtach, `mtime_ns` =
  `os.stat().st_mtime_ns` jako LICZBA CALKOWITA (`ZdarzenieSkanu.czas_pliku` = `mtime_ns / 1e9`). Baza A1 trzyma
  `skany.czas_pliku` jako czas lokalny ISO uciety do sekund (`session._czas_iso`) - porownanie przez
  `scanner.czas_pliku_iso(mtime_ns)` (ten sam napis, ktory A1 zapisala dla tego pliku) i `scanner.klucz_znanego(sciezka,
  rozmiar, czas_iso)` (sciezka po `normcase(abspath)`). Porownanie wprost z `mtime_ns` = zawsze "nieznany" (skrot calej
  historii folderu przy kazdym starcie i duplikaty do odsiania po `sha16` - bez strat, ale koszt i szum).
- ZNACZENIE: True = dla tej sciezki, rozmiaru i czasu aplikacja ma zapisany wynik analizy (dowolny status), blad pokazany
  technikowi albo zadanie zapisane z `Silnik.stop()` (A3 zleca je sama po starcie). Samo przyjete zdarzenie skanu bez
  wyniku = False (awaria miedzy zdarzeniem a wynikiem nie moze zgubic skanu).
- Gotowa funkcja: `ZnanePliki(wpisy)` - `wpisy` = krotki (`plik`, `rozmiar`, `czas_pliku`) z tabeli `skany` wczytane
  PRZED `start()`; zbior niezmienny, wiec wywolanie jest bezpieczne z kazdego watku i nie dotyka bazy. Stan z chwili
  startu wystarcza: pliki zapisane po starcie obserwatora sa nowe bez pytania o `znane` (D-N1).

Uzyte ponownie z okna "Dzien skanera" (`dzien_skanera_rdzen`, bez zmian w tamtym pliku): `ktos_pisze` (warunek 3),
`otworz_zrodlo` (odczyt z pelnym wspoldzieleniem: nie blokuje zapisu, zmiany nazwy ani usuniecia przez program
skanera), `pliki_w_folderze` (przeglad). Nie uzyto `Zbieracz`: odpytuje co 1,5 s i potrzebuje 2 zgodnych odczytow
(opoznienie 1,5-3 s wobec wymagania "ponizej 1 s"), kopiuje pliki do folderu sesji i przepuszcza pliki niepelne po 30 s -
to inne zadanie (zebrac wszystko) niz tutaj (zglosic tylko dobry skan, szybko).

**Akcja "start skanu" (decyzja DW5).** `Scanner.start_skanu()` wywoluje funkcje podana w konstruktorze i zwraca
True / False (wyjatek akcji = False). Domyslnie `AtrapaStartuSkanu`: niczego nie klika, zapisuje czasy wywolan.
Prawdziwa akcja (aktywuj okno programu skanera i nacisnij Spacje) powstanie po probach na skanerze (paczka B2).

**Symulator.** `py -3.12 narzedzia/symulator_skanera.py --folder F [--zrodla ...] [--ile N] [--czas 1 5] [--zle uciety
pusty ...] [--pomiar] [--analiza --projekty P]` - zapisuje pliki w kawalkach z przerwami, kilka naraz, dorzuca pliki
zle; z `--pomiar` liczy zdarzenia i opoznienia, z `--analiza` przepuszcza skany przez silnik. Opis w naglowku pliku.

**Pomiary (PC wlasciciela, 17.11.2026).** Liczby i obciazenie komputera w chwili pomiaru: `raporty/E3-A2_2026-11-17.md`.

**Zalozenia i granice.**
- Nazw, struktury folderow ani sposobu zapisu prawdziwego skanera nie znamy (plan etapu 3, S5): wszystko jest
  parametrem; symulator pokazuje cztery sposoby zapisu (plik otwarty caly czas, zamykany po kazdym kawalku, plik
  tymczasowy ze zmiana nazwy, plik otwarty bez zgody na wspoldzielenie - `--tryb wylaczny`), ale to nie jest opis
  skanera. Sprawdzenie na skanerze: paczka B2.
- Tylko binarny STL. STL tekstowy, PLY, OBJ = wpis z powodem, bez zdarzenia. Jesli skaner eksportuje inaczej - B2.
- Zdarzenie przed koncem zapisu jest wykluczone, gdy program skanera pisze naglowek z ostateczna liczba trojkatow albo
  trzyma plik otwarty do zapisu. Program, ktory od razu rezerwuje pelny rozmiar pliku, zamyka go i dopisuje dane
  pozniej, nie zostalby rozpoznany na Windows inaczej niz po `stabilizacja_ms` (poza Windows `ktos_pisze` zawsze
  zwraca False i decyduje sama stabilizacja oraz naglowek).
- `ktos_pisze` otwiera plik na chwile bez zgody na zapis innych programow; jest wolane dopiero dla pliku stabilnego
  i (dla plikow dobrych) zgodnego z naglowkiem, wiec okno kolizji z programem skanera to pojedyncze wywolania.
- Ponowny zapis, ktory zachowuje rozmiar i czas pliku co do 100 ns (kopia z zachowaniem czasu na ten sam plik bez
  usuwania), nie jest zauwazany - zawartosc jest wtedy w praktyce ta sama.
- Pamiec duplikatow (`sha16` -> pierwszy plik) i numeracja zdarzen zyja tyle, co obiekt `Scanner`; trwala historia
  skanow to zadanie sesji i bazy (A1, A3). Dlatego A3 MA podac nadrabianie: `znane=ZnanePliki(<wiersze z bazy>)` (lapie
  tez plik, ktory przed zamknieciem byl zajety albo czekal na wynik) albo przynajmniej `zglos_zastane_od` = czas pliku
  ostatniego skanu w bazie (tansze, ale zgubi plik starszy od ostatniego skanu, ktory nie dal zdarzenia). Skan zgloszony
  drugi raz (zastany i juz z wynikiem w bazie) A3 rozpozna po `sha16`. `zastany=True` nie znaczy "stary": to skan
  sprzed startu programu, ktorego baza nie zna.
- D-N1 porownuje czas pliku z zegarem komputera: plik na dysku sieciowym z czasem serwera przesunietym do przodu moze
  byc uznany za nowy (duplikat, nie strata); plik przeniesiony po starcie do folderu poznego z zachowanym starym czasem
  (napisany przed startem) jest zastany - wraca tylko z nadrabianiem. Rozdzielczosc: zegar systemu (ok. 16 ms na Windows).
- Folder niedostepny przy starcie albo znikajacy w trakcie nie jest bledem: obserwator czeka i wraca do pracy
  (`stan()["folder_dostepny"]`).
- Funkcje zwrotne i `znane` sa wolane w watku obserwatora; okno Qt powinno w nich tylko emitowac sygnal albo wkladac do kolejki.
- Nazwa pliku skanu jest w logu (poziom INFO) - jesli zlecenia w programie skanera beda nazywane nazwiskami, do decyzji
  po dniu skanera (D5, B2). Caly folder z podfolderami jest listowany co `przeglad_s` (D11 c - do pomiaru w B2).
