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
| `skan_sha16` | brak | skrot ze `ZdarzenieSkanu` - sprawdzany przed analiza i po niej (P1); bez niego silnik liczy sam |
| `inspekcja`, `bez_filtru`, `straznik` | tak, nie, tak | jak w `porownaj` |
| `wyjscie` | brak | folder na `<czas przyjecia>_<sha16>_<nazwa skanu>[_n]_wynik.json` i `..._podglad.npz` |
| `zadanie_id`, `przyjete` | - | nadaje `zlec` (numer od 1 w kazdym obiekcie `Silnik`, czas przyjecia) |

Parametry `Silnik(...)`: `ust` (slownik ustawien) albo `plik_ustawien` (None = `ustawienia.toml` programu),
`funkcja` (`"modul:funkcja"` analizy; domyslnie `stanowisko.porownaj:porownaj`), `limit_zadania_s` (600),
`limit_startu_s` (180), `pul_w_pamieci` (2), `plik_logu` (wyjscie bibliotek z procesu roboczego), `pamiec_linii`
(katalog pamieci linii brzegu na dysku; domyslnie wylaczona), `na_zdarzenie`.

**Wyjscie.** `ZdarzenieSilnika` do funkcji `na_zdarzenie` (wolanej w watku nadzorcy) albo do kolejki `Silnik.zdarzenia`:

| `typ` | Pola |
|---|---|
| `gotowy` | proces roboczy wystartowal (`czas_s` = czas startu) |
| `start` | zadanie wyslane do procesu (`zadanie_id`, `zadanie`) |
| `postep` | `etap`, `udzial` 0-1 (etapy z `porownaj`) |
| `wynik` | `wynik` = slownik `porownaj` w postaci z pliku `<skan>_wynik.json` (z `ostrzezenia`, jak w wierszu polecen; teksty bez nazw z puli) + `zadanie_id` + `skan_sha16` (tresci faktycznie analizowanej); `pliki` (sciezki z `wyjscie` TEGO zadania); `czas_s` |
| `blad` | `rodzaj`: `analiza` (wyjatek, brak pliku, pusta pula), `proces` (proces zniknal - `kod wyjscia` w komunikacie), `limit_czasu`, `start` (proces nie umie wystartowac), `plik_zmieniony` (tresc pliku inna niz w zdarzeniu skanu - przed analiza albo w jej trakcie; oba skroty w komunikacie, bez wyniku); `blad` (jedno zdanie), `szczegoly` (slad wyjatku), `czas_s` |
| `zatrzymany` | `niezakonczone` - krotka `ZadanieAnalizy` przerwanych przez `stop()` (w toku pierwsze, potem kolejka); wolane w watku, ktory wywolal `stop()` |

`..._podglad.npz`: dla kazdego gniazda z inspekcja tablice `g<nr>_P` (punkty w ukladzie plytki) i `g<nr>_d`
(odchylka w mm) - material na obraz odchylek w oknie; odczyt `silnik.wczytaj_podglad(plik)`. Pliki w `wyjscie` (P4):
nazwa `<czas przyjecia RRRRMMDD_GGMMSS>_<sha16>_<nazwa skanu: litery ASCII, cyfry, ._->` i kolejny numer `_n`, gdy taki
plik juz jest; zapis przez plik tymczasowy i zmiane nazwy bez nadpisywania - dwa skany `scan.stl` z dwoch podfolderow
i ponowna analiza tego samego skanu daja osobne komplety, a urwany zapis nie zostawia polowy pliku.

**Jak dziala.** `Silnik.start()` uruchamia watek nadzorcy (zwykly watek Pythona: bez Open3D i bez Qt) i proces roboczy
(`multiprocessing`, metoda `spawn`, lacze `Pipe` - bez wspolnych kolejek, wiec zabity proces niczego nie blokuje).
`zlec(zadanie)` / `zlec_skan(zdarzenie_skanu, pula)` dopisuje do kolejki i zwraca `zadanie_id`; `anuluj(id)` usuwa
zadanie, ktore jeszcze nie ruszylo. Nadzorca wysyla zadania po jednym, w kolejnosci zlecen. Awarie: wyjatek analizy
(takze `SystemExit` z `porownaj` przy pustej puli) = `blad` i nastepne zadanie w tym samym procesie; proces zniknal
(zabity, awaria biblioteki) albo przekroczyl `limit_zadania_s` = `blad` tego zadania, nowy proces, nastepne zadanie
(bez ponawiania zadania, ktore zabilo proces). Proces, ktory nie umie wystartowac (brak pakietu, zly plik ustawien),
oddaje `blad` rodzaju `start` kolejnym zadaniom - jedna proba na zadanie, bez petli restartow. Limit czasu nadzorca
sprawdza takze przy kazdej wiadomosci z procesu (zadanie, ktore stale przysyla postep, tez zostanie przerwane).
`stop()` konczy proces i ZWRACA zadania niezakonczone (w toku i w kolejce), zglaszajac je zdarzeniem `zatrzymany` (P2) -
zadne z nich nie dostaje `wynik` ani `blad`; kolejne `stop()` zwraca [].

Proces roboczy pilnuje sie sam (P6, `Straznik`): watek sprawdza co 0,5 s, czy zyje proces okna
(`multiprocessing.parent_process()`), i konczy proces roboczy od razu, gdy go nie ma - takze W TRAKCIE analizy (zmierzone:
0,4 s po zabiciu procesu okna). Ma tez wlasny limit zadania: `limit_zadania_s` + 30 s (nadzorcy moze juz nie byc).
Plik skanu zmieniony po zdarzeniu (P1): proces roboczy liczy skrot przed analiza (inny niz `skan_sha16` zdarzenia =
`plik_zmieniony`, analiza nie rusza) i po niej (inny = `plik_zmieniony`, wynik odrzucony); nowa tresc ma wlasne
zdarzenie ze `scanner`. Dane osobowe (P5, `CzyscicielNazw`): ostrzezenia, uwagi i teksty bledow z procesu roboczego
(zdarzenia, pliki w `wyjscie`) nie zawieraja nazw plikow ani folderow puli projektow - sciezka pod folderem puli i nazwa
folderu = `<projekt>`, nazwa pliku z puli (z rozszerzeniem albo bez) = `<projekt sha16>`; zostaja: sam folder puli
z zadania (`foldery_projektow`), nazwy folderow z mniej niz 2 literami (numer kuwety), rdzenie nazw plikow krotsze niz
3 znaki. Nazwy etapow postepu to stale z `porownaj` - nie sa czyszczone.

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
  bledem "DLL load failed while importing Shiboken" (3 z 3 prob jednej sciezki testu; przyczyna nieustalona).
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
- Nazwa pliku skanu zostaje w komunikatach (np. "brak pliku skanu ...") i w nazwach plikow `wyjscie`; nazwy z puli nie.
- Kolejka zadan zyje w pamieci procesu okna. Po zamknieciu programu nic nie ginie, o ile A3: (1) w `closeEvent` wola
  `stop()` i zapisuje zwrocone zadania (sciezka, `skan_sha16`, tryb, numer) w bazie albo pliku; (2) po starcie zleca je
  ponownie (`zlec` nadaje nowe numery); (3) przy awarii bez `stop()` - nadrabianie w `scanner` (`znane`). Bez `stop()`
  przy wyjsciu zostaje kosmetyczny slad "Exception ignored in atexit" (D2); proces roboczy i tak konczy sie sam.
- `zadanie_id` liczy sie od 1 w kazdym obiekcie `Silnik` (po `stop()` trzeba utworzyc nowy); sygnaly `wynik(int, object)`
  i `blad(int, str, str)` lacznika niosa tylko numer - A3 kluczuje po obiekcie silnika albo bierze `zdarzenie(object)`
  (D7). `zatrzymany` przychodzi tylko przez `zdarzenie(object)`.
- Priorytet procesu roboczego jest zwykly (okno "Dzien skanera" obniza priorytet swojej kontroli - tu nie, bo wynik ma
  byc szybko; do decyzji po probach na laptopie stanowiska, D4).
- Proces roboczy, ktory zglasza gotowosc i ginie bez zadania, jest uruchamiany od nowa bez licznika (D4 b, malo
  prawdopodobne).
