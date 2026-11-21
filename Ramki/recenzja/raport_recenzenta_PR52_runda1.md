# Raport recenzenta - PR #52 (E3-O4), runda 1 (recenzja wczesna: etapy A i B1)

Data: 21.11.2026, 11:40-11:55. Zakres: `git -C <PC-katalog>\qc diff main...e3/o4`, main = beddde7, HEAD = 2337c15
(8 commitow, 24 pliki, 2812 wierszy dodanych).
Metoda: wlasny przeglad calego diffu (kod, skrypty bash, plik uslugi, wzor konfiguracji, 3 instrukcje, testy), potem proby
w kopii `<PC-katalog>\qc-wt\rec-o4` (detached 2337c15) i w odtworzonym ukladzie katalogow instalacji pod
`<PC-katalog>\koordynator\robocze\rec-o4\` (katalog ze spacja i polskimi znakami w nazwie). Raport wykonawcy czytany na
koncu (tylko sekcja 7 "ETAP B2").
Uruchomiono: testy paczki (8 plikow) przez `ciezki.ps1 -Tor 3`; 9 wstrzykniec bledu w 2 przebiegach; 17 prob wlasnych
(sekcja 2). Pelnego pytest nie uruchamiano (zgodnie ze zleceniem). Paczki probnej nie budowano, niczego nie instalowano.
Etap B2 (paczka probna, instalacja probna, aktualizacja z 0.3.1 i powrot, proby kryteriow 1, 2, 6 na instalacji, pelny
pytest) jeszcze sie nie odbyl - kryteria od niego zalezne maja status "czeka na etap B2".

## 0. Werdykt i liczby B / P / D

WERDYKT: do scalenia po poprawkach (B 0 / P 2 / D 8) - poprawki P1 i P2 do zrobienia razem z etapem B2.

- B: 0.
- P: 2 - obie dotycza tego samego celu paczki ("sesja nigdy w katalogu wersji"): P1 brak pliku ustawien instalacji albo
  wzgledna sciezka bazy = sesja znowu w katalogu wersji (odtworzone proba); P2 po powrocie do 0.3.1 nowy skrot po cichu
  zapisuje sesje do katalogu wersji 0.3.1 (odtworzone proba), instrukcja o tym milczy.
- D: 8.
- Kod etapow A i B1 jest porzadny: testy paczki 342 passed, 7 z 9 moich wstrzykniec wykrytych, program ramki odrzuca
  kazde zadanie bez klucza (168 z 168 obslugiwanych zadan = 401), klucz nie trafia do logu ani na ekran skryptow.

## 1. Uwagi

| Nr | Waga | Plik:linia | Scenariusz (stan -> co sie dzieje) | Propozycja |
|---|---|---|---|---|
| P1 | P | `stanowisko/dzien_skanera_rdzen.py:2674-2681` (`katalog_instalacji`), `:2709-2713` (`katalog_sesji`, regula 1); `narzedzia/pomiar_skanu/pomiar_skanu.py:652` | Rozpoznanie "jestem w instalacji" wymaga, zeby `<instalacja>\ustawienia.toml` ISTNIAL. (a) Pliku nie ma (skasowany, przeniesiony, zmieniona nazwa): `Dzien_skanera.cmd` startuje bez bledu, okno czyta `ustawienia.przyklad.toml` z katalogu wersji, obserwuje `C:\Aidite\Scandata` i zaklada sesje w `wersje\<w>\program\dane\dzien_skanera` - dokladnie objaw POTRZEBUJE 1 z S1 (proba A2: kod 0, 3 pliki w katalogu wersji). W tym samym stanie pomiar szczegolowy pisze "brak pliku ustawien: ...\wersje\<w>\program\ustawienia.toml - skopiuj ustawienia.przyklad.toml jako ustawienia.toml" (proba A5b), czyli radzi zalozyc plik ustawien W KATALOGU WERSJI. (b) Plik jest, ale `[sciezki] baza` jest wzgledna (np. `dane/stanowisko.sqlite` - recznie zmieniona po instalacji; instalator lapie to dopiero przy nastepnym `zainstaluj.cmd`): regula 1 liczy katalog bazy od katalogu programu i sesja laduje w `wersje\<w>\program\dane\dzien_skanera` (proba A3: kod 0, 3 pliki w katalogu wersji). Opis funkcji obiecuje "sesja nigdy nie trafia do katalogu wersji" - nie jest to prawda w 2 stanach. | (1) Rozpoznawac instalacje po ukladzie katalogow i znaczniku niezaleznym od ustawien: `wersje\<w>\instalacja.json` (zaklada go instalator; `pomiar_skanu.cmd` juz go uzywa) albo `<instalacja>\wersja_biezaca.txt`; brak `ustawienia.toml` = dalej instalacja (sesja w `<instalacja>\dane\dzien_skanera`, komunikat w oknie o braku pliku). (2) W `katalog_sesji`: gdy program lezy w instalacji, a wynik reguly 1 lezy wewnatrz `<instalacja>\wersje\`, uzyc `<instalacja>\dane\dzien_skanera`. (3) W pomiarze w instalacji komunikat ma wskazywac `<instalacja>\ustawienia.toml`. Testy: 2 nowe przypadki w `test_o4_instalacja_dzien_skanera.py` (brak pliku; baza wzgledna) - dzis oba by padly. |
| P2 | P | `instalacja/wzory/Dzien_skanera.cmd:19`; `instalacja/instalator.py:1436` (skrypty zapisuje tylko `zainstaluj`), `:1491` (`wroc` ich nie rusza); `instrukcje/instalacja_i_aktualizacja.md:51-57` (punkt 4) i `:86-103` (punkt 7) | Aktualizacja 0.3.1 -> nowa wersja zaklada `Dzien_skanera.cmd`. Potem `Wroc_do_poprzedniej.cmd` (albo ponowne `zainstaluj.cmd` z paczki 0.3.1: stary instalator zapisuje 5 skryptow, szosty zostaje): skrot dalej jest w katalogu i uruchamia modul wersji 0.3.1 z `--ustawienia <instalacja>\ustawienia.toml`. Stary modul bierze folder skanera z ustawien instalacji (wszystko wyglada dobrze), ale sesje zapisuje do `wersje\0.3.1\program\dane\dzien_skanera` (proba R1: sesja w `wersje/0.3.1/program/dane/dzien_skanera`, 0 komunikatow) - czyli blad, ktory paczka naprawia, wraca po cichu, pod nowym, "oficjalnym" skrotem. `Dzien_skanera.cmd --nowa --zamknij-po 5` (proba zalecana w punkcie 7 instrukcji) konczy sie wtedy kodem 2 i wierszem po angielsku `error: unrecognized arguments: --zamknij-po 5` (proba R2). Instrukcja (punkt 4 "Powrot", punkt 7) nie mowi o tym ani slowa; raport wykonawcy (7.1 p. 5) przewiduje to z odczytu kodu i zostawia "do opisania". Kryterium 6 wymaga: "nowy skrot nie psuje powrotu do wersji, ktora go nie ma - opisz, co zostaje w katalogu". | Najmniejsza zmiana, ktora usuwa skutek: skrot podaje katalog sesji wprost - `--ustawienia "%KAT%ustawienia.toml" --dane "%KAT%dane\dzien_skanera" %*` (modul 0.3.1 zna `--dane`; `%*` na koncu, wiec `--dane` czlowieka dalej wygrywa); wtedy po powrocie sesje i tak sa w `<instalacja>\dane\dzien_skanera`. Jesli wykonawca woli zostac przy samym `--ustawienia` (jak `Stanowisko.cmd`): skrot ma sprawdzic, czy wersja biezaca zna nowy mechanizm (np. `findstr /c:"def katalog_sesji"` na `%W%\program\stanowisko\dzien_skanera_rdzen.py`), a gdy nie - dodac `--dane` albo wypisac komunikat po polsku. Do tego 2 zdania w instrukcji (punkt 4: po powrocie do 0.3.1 skrot zostaje i co robi; `--zamknij-po` dziala od wersji z tej paczki) i proba w B2 (sekcja 6 p. 1). Wybor wariantu: sekcja 5 p. 1. |
| D1 | D | `narzedzia/zbuduj_wydanie.py:39` (`WYMAGANE`) | Wstrzykniecie W1b: usuniecie `instalacja/wzory/Dzien_skanera.cmd` z `WYMAGANE` - 0 padajacych testow (`test_zbuduj_wydanie.py` 22 passed, 3 pliki `test_o4_*` bez zmian). Paczka bez wzoru zatrzymalaby instalacje dopiero w kroku [8/9] (`zapisz_skrypty`, brak pliku). Dzis chroni przed tym posrednio `test_p6_...` (lista plikow `wzory/*.cmd`). | Jeden assert: `{"instalacja/wzory/" + n for n in instalator.WZORY_SKRYPTOW} <= set(zbuduj_wydanie.WYMAGANE)`. |
| D2 | D | `ramka/rpi/zainstaluj_ramke.sh:148, 154, 174, 183` | Wstrzykniecie W4b: `chmod 600` -> `644` (2 miejsca), `0o600` -> `0o644`, `umask 077` -> `022` - 0 padajacych testow (plik z kluczem czytelny dla kazdego konta na ramce). Na sprzecie zlapie to wiersz "prawa pliku" w `sprawdz_ramke.sh`, na PC nic. | Test tresci: w skrypcie sa `chmod 600 "$PLIK_KONFIGURACJI"` (2 razy), `0o600` i `umask 077`. |
| D3 | D | `instrukcje/ramka_raspberry_pi.md:287` | Krok 9.2: "wiersz tekstu zaczynajacy sie od `{"protokol": 1`". Program odpowiada bez odstepu: `{"protokol":1,"rola":"P","program":"0.1.` (proba H1; `serwer.py:273` `separators=(",", ":")`). Osoba porownujaca znak po znaku uzna, ze cos jest nie tak. | Wpisac `{"protokol":1` (bez odstepu). |
| D4 | D | `instrukcje/ramka_raspberry_pi.md:52-68` (krok 1) | Ramka przyszla od wykonawcy zewnetrznego i wg raportu S1 (luka L1, pytanie P3) nie wiadomo, co jest na jej karcie. Instrukcja zaczyna od "Zapisz karte" w Raspberry Pi Imager - jesli w ramce siedzi karta z systemem dostawcy, krok 1 nadpisuje ja bez ostrzezenia (nieodwracalne). | Jedno zdanie na poczatku kroku 1: jesli w ramce jest juz karta - nie nadpisuj jej, odloz i uzyj nowej (albo najpierw zrob kroki 2 i `sprawdz_ramke.sh` na karcie zastanej). Patrz sekcja 5 p. 2. |
| D5 | D | `instrukcje/ramka_raspberry_pi.md:380` ("Zmiana pliku konfiguracji"), `:398` ("Typowe bledy") | Znacznik `[NIE SPRAWDZONE BEZ SPRZETU]` jest w naglowku dokumentu i przy 12 z 12 krokow (13 wystapien), ale 2 sekcje koncowe go nie maja, a zawieraja twierdzenia nie do sprawdzenia na PC (np. sciezka menu `raspi-config` "Performance Options -> Overlay File System", komunikat `externally-managed-environment`, `sudo nmtui`). | Dopisac znacznik do 2 naglowkow; test `test_instrukcja_kazdy_krok_ma_znacznik...` rozszerzyc o te sekcje. |
| D6 | D | `ramka/rpi/zainstaluj_ramke.sh:58` (`--klucz`), `instrukcje/ramka_raspberry_pi.md:241` | Klucz podany w wierszu polecen drugiej ramki zostaje w historii powloki (`~/.bash_history` konta z kroku 1) i jest widoczny na liscie procesow w czasie instalacji. Skrypty poza tym klucza nie wypisuja (sprawdzone testem i wstrzyknieciem W4a). | Zdanie w kroku 7 (np. po instalacji `history -c`) albo przyjac jako znane ograniczenie i wpisac do "Czego ta instrukcja nie obejmuje". |
| D7 | D | `instrukcje/instalacja_i_aktualizacja.md:92` | Proba "bez klikania" `Dzien_skanera.cmd --nowa --zamknij-po 5` zostawia pusta NIEDOKONCZONA sesje (instrukcja to mowi). W dniu skanera pierwsze uruchomienie zapyta "Znaleziono niedokonczona sesje ... (0 plikow). Wznowic ja?" - instrukcja i karta nie mowia, co odpowiedziec. | Dopisac: "na pytanie o niedokonczona sesje z proby odpowiedz Tak albo Nie - obie odpowiedzi sa dobre". |
| D8 | D | `stanowisko/dzien_skanera_rdzen.py` (`wczytaj_ustawienia_bezpiecznie`, zachowanie zastane) | Plik ustawien instalacji zapisany z BOM (Notatnik; instrukcja ostrzega): sesja powstaje dobrze w `<instalacja>\dane\dzien_skanera` (regula 2, proba A4), ale okno pracuje na wzorze i obserwuje `C:\Aidite\Scandata`, nie folder z ustawien instalacji; czlowiek dostaje tylko uwage w oknie. Zachowanie sprzed paczki, w instalacji bardziej mylace niz w repo. | Bez zmiany w tej paczce; w dokumencie dnia sprzetu dopisac "gdy okno pisze: Plik ustawien ma blad - popraw plik i uruchom ponownie". |

## 2. Wlasne proby

Testy paczki (kopia `rec-o4`, `ciezki.ps1 -Tor 3`, log `robocze\rec-o4\testy_paczki.log`):

| Polecenie | Wynik |
|---|---|
| `py.cmd -m pytest -q -p no:cacheprovider testy/test_o4_instalacja_dzien_skanera.py testy/test_o4_test_led.py testy/test_o4_ramka_rpi.py testy/test_dzien_skanera.py testy/test_zbuduj_wydanie.py testy/test_instrukcje.py testy/test_ramka.py testy/test_instalacja.py` | 342 passed, 0 failed, 0 skipped, 275 s |
| `bash -n ramka/rpi/zainstaluj_ramke.sh`, `bash -n ramka/rpi/sprawdz_ramke.sh` (Git Bash) | kod 0, kod 0 |

Wstrzykniecia (kazde cofniete `git checkout -- .`; logi `robocze\rec-o4\wstrz1_*.log`, `wstrz2_o4.log`; uruchamiane 3 pliki
`test_o4_*` = 34 testy, dla W1b dodatkowo `test_zbuduj_wydanie.py` = 22 testy):

| Nr | Punkt | Co zepsuto | Padlo testow |
|---|---|---|---|
| W1 | 1 | `katalog_instalacji` zwraca zawsze None | 5 (w tym okno przez `Polecenie.cmd`, zly plik ustawien, pomiar przez `Polecenie.cmd`) |
| W1d | 1 | `wybierz_sesje` znowu bierze `R.KATALOG_SESJI` (stan 0.3.1) | 4 |
| W1b | 1 | `WYMAGANE` w `zbuduj_wydanie.py` bez `wzory/Dzien_skanera.cmd` | 0 z 56 - uwaga D1 |
| W2 | 2 | `wczytaj_ustawienia_pomiaru` bez pliku instalacji | 1 |
| W2c | 2 | `pomiar_skanu.cmd` bez wiersza srodowiska wersji | 1 |
| W3 | 3 | `test_led.utworz_sprzet` nie przekazuje `mapowanie` | 2 |
| W4a | 4 | `sprawdz_ramke.sh` wypisuje klucz zamiast jego dlugosci | 2 |
| W4c | 4 | `ramka.service`: `User=pi` zamiast `root` | 1 |
| W4b | 4 | `zainstaluj_ramke.sh`: prawa pliku z kluczem 644, `umask 022` | 0 z 34 - uwaga D2 |

Razem 9 wstrzykniec: 7 wykrytych, 2 niewykryte. Po jednym wykrytym na kazdy z punktow 1-4.

Proby w odtworzonym ukladzie instalacji (`robocze\rec-o4\<katalog ze spacja i polskimi znakami>\Stanowisko\wersje\9.9.9\program`
= kopia `stanowisko/` i `narzedzia/pomiar_skanu/` z HEAD; ustawienia = kopia ustawien instalacji S1 z podmienionymi
sciezkami; uruchamiane z katalogu programu przez `py.cmd`, wiec bez katalogu repo na sciezce importu):

| Nr | Polecenie / stan | Wynik |
|---|---|---|
| A1 | `-m stanowisko.dzien_skanera --ustawienia <K>\ustawienia.toml --nowa --zamknij-po 1`, dobry plik | kod 0; sesja w `<K>\dane\dzien_skanera`; folder obserwowany z ustawien instalacji; 0 plikow w `program\dane` |
| A2 | to samo, `<K>\ustawienia.toml` nie istnieje | kod 0; sesja w `<K>\wersje\9.9.9\program\dane\dzien_skanera` (3 pliki w katalogu wersji); ustawienia = wzor; folder `C:\Aidite\Scandata` - uwaga P1 |
| A3 | to samo, `baza = "dane/stanowisko.sqlite"` (wzgledna) | kod 0; sesja w katalogu wersji (3 pliki) - uwaga P1 |
| A4 | to samo, plik ustawien z BOM | kod 0; sesja w `<K>\dane\dzien_skanera`; ustawienia = wzor, folder `C:\Aidite\Scandata` - uwaga D8 |
| A5a | `narzedzia\pomiar_skanu\pomiar_skanu.py <skan> --bez-plytki`, plik ustawien z BOM | kod 2, 1 wiersz `blad: ustawienia: ...`, bez Traceback |
| A5b | to samo, brak pliku ustawien instalacji | kod 2; komunikat wskazuje `...\wersje\9.9.9\program\ustawienia.toml` i radzi go zalozyc - uwaga P1 |
| C1 | `cmd /c "<K>\Dzien_skanera.cmd" --nowa --zamknij-po 1 < NUL`, brak srodowiska wersji | kod 4, 2 wiersze BLAD / CO ZROBIC, bez pauzy (sciezka ze spacja i polskimi znakami przechodzi przez `%~dp0`) |
| C2 | to samo, pusty `wersja_biezaca.txt` | kod 4, komunikat jak wyzej |
| R1 | modul wersji 0.3.1 (kopia `stanowisko/` z `t0\s1`, tylko odczyt zrodla) wolany tak jak wola go nowy skrot: `wczytaj_ustawienia_bezpiecznie(<K>\ustawienia.toml)` + `wybierz_sesje` bez `--dane` | ustawienia z `<K>\ustawienia.toml`; sesja w `wersje/0.3.1/program/dane/dzien_skanera` - uwaga P2 |
| R2 | modul 0.3.1: `-m stanowisko.dzien_skanera --ustawienia <K>\ustawienia.toml --nowa --zamknij-po 5` | kod 2, `error: unrecognized arguments: --zamknij-po 5` - uwaga P2 |

Proby programu ramki i `test_led` (kopia `rec-o4`):

| Nr | Polecenie | Wynik |
|---|---|---|
| H1 | `robocze\rec-o4\proba_serwer.py`: program ramki na atrapie z kluczem ze wzoru; 10 metod x 7 sciezek (w tym `/atrapa/plytka`, nieznana, `/`) x 4 warianty naglowka (brak, zly klucz, pusty, klucz bez ostatniego znaku) = 280 zadan | GET / PUT / DELETE / POST / PATCH / HEAD: 168 z 168 = 401; OPTIONS / TRACE / CONNECT / nieznana metoda: 112 z 112 = 501 (nic nie wykonuja); stan po probach `gotowa`; log 282 wiersze, klucza w logu 0 razy; odpowiedz z kluczem zaczyna sie od `{"protokol":1,` (uwaga D3) |
| T1 | `-m ramka.test_led --kalibracja kal.json --uklad wieczorna --konfiguracja ramka\rpi\ramka.json.wzor --rola W` (sprzet `rpi` z pliku, PC bez biblioteki) | kod 2, `blad: sprzet niedostepny: brak biblioteki rgbmatrix (...)`, bez Traceback |
| T2 | to samo + `--sprzet atrapa` (wiersz polecen przed plikiem) | kod 0, `test LED: 19 gniazd ukladu wieczorna (ramka W)` |
| T3 | `--konfiguracja <wzor> --sprzet atrapa` bez `--rola` (rola P z pliku), uklad `wieczorna` | kod 1, `blad: brak ukladu w kalibracji tej ramki` (rola wzieta z pliku) |
| T4 | `--konfiguracja <plik, ktorego nie ma>` | kod 1, 1 wiersz `blad: konfiguracja ramki (...)`, bez Traceback |
| T5 | `-m ramka --sprzet rpi --konfiguracja ramka\rpi\ramka.json.wzor` na PC | kod 2, `sprzet niedostepny: brak biblioteki rgbmatrix` (ten sam kod co T1) |
| K1 | `-m ramka.kalibracja --domyslna --modele modele_plytek --wyjscie kal.json` (polecenie z kroku 10 instrukcji) | kod 0; W: wieczorna 19, wieczorna_r54 20; P: poranna 24, poranna_r54 33 |

Przeglad bez uruchamiania (odczyt kodu):

- `ramka/serwer.py:171-183`: klucz sprawdzany na poczatku `_obsluz`, przed odczytem tresci i przed jakimkolwiek dzialaniem,
  wspolnie dla 6 metod; `log_message` wylaczony, wlasny log bez sciezki klienta i bez naglowkow.
- `ramka.service`: `User=root`, `WorkingDirectory=/opt/ramka`, `After` / `Wants=network-online.target`, `Restart=always`,
  `RestartSec=2`, `StartLimitIntervalSec=0`; `program.main` obsluguje SIGTERM (`systemctl stop` gasi matryce przez
  `program.zatrzymaj`).
- `zainstaluj_ramke.sh`: cytowanie zmiennych poprawne; kopia przez `ramka.nowy` -> zamiana -> usuniecie `ramka.stary`
  (przerwanie w polowie: nastepne uruchomienie sprzata oba katalogi i kopiuje od nowa); istniejacy plik konfiguracji nie
  jest nadpisywany (warunek w bashu + `O_EXCL` w Pythonie); `chmod 600` + `chown root:root` takze dla pliku zastanego;
  biblioteki matrycy nie kompiluje. Bez `set -e`, ale kazdy krok ma jawne `|| blad`.
- `ramka.json.wzor`: 12 pol, wszystkie znane `program.Konfiguracja`, wartosci sprzetu rowne domyslnym z kodu, `host` 0.0.0.0,
  klucz zastepczy odrzucany przez oba skrypty.
- Instrukcja ramki a kod i `ramka/README.md`: port 8765, `/opt/ramka/ramka`, `/etc/ramka/ramka.json`, `dtparam=audio=off`,
  `dtparam=spi=off`, `isolcpus=3`, pakiety `python3-gpiozero` / `python3-evdev`, `make build-python`, komunikaty
  `slucha na 0.0.0.0:8765`, `ramka slucha tylko na 127.0.0.1`, `sprzet niedostepny: ...`, pola `[ramki]` ustawien laptopa,
  test LED 4 kolory / 8 s - zgodne. Fakty o sprzecie instrukcja zbiera w arkuszu (model Pi, nakladka, zworki, matryca),
  nie zgaduje ich; zdania o blacie / panelu i celu 60 s pochodza z planu wdrozenia.
- Instalator: `WZORY_SKRYPTOW` 6 pozycji, `zapisz_skrypty` wolane tylko w kroku [8/9] `zainstaluj`; `wroc` skryptow nie
  zmienia; `stanowisko/samokontrola.py` nie ma listy skrotow (0 trafien `.cmd`) - plik nie zostal zmieniony.
- Zmiana zachowania z repo (`--ustawienia INNY_PLIK` bez `--dane` = sesje w katalogu bazy z tego pliku): w repo nikt tak
  nie wola okna (`uruchom_dzien_skanera.bat` nie podaje `--ustawienia`; jedyne inne wystapienie to nowy skrot); sterownik
  S1 `dzien_skanera_proba.py:55` wola `wybierz_sesje(a, ust, None)` w starej postaci - dziala (regula 2), patrz sekcja 6 p. 4.

## 3. Kryteria zlecenia

| Nr | Kryterium | Status |
|---|---|---|
| 1 | Test w ukladzie instalacji (bez poprawki pada) | potwierdzone wlasna proba: 11 testow przechodzi, W1 -> 5 pada, W1d -> 4 pada, proba A1 kod 0; z zastrzezeniem P1 (2 stany, w ktorych sesja laduje w katalogu wersji) |
| 1 | Proba na instalacji probnej z galezi (`Dzien_skanera.cmd` istnieje, okno startuje, sesja w `<instalacja>\dane\dzien_skanera`, 0 nowych plikow w katalogu wersji, samokontrola zielona) | czeka na etap B2 |
| 2 | Test jednostkowy sciezki ustawien pomiaru | potwierdzone wlasna proba: W2 -> 1 pada, W2c -> 1 pada, A5a / A5b kod 2 z komunikatem |
| 2 | Przycisk i `Polecenie.cmd narzedzia\pomiar_skanu\...` na instalacji: kod 0, czas | czeka na etap B2 |
| 3 | `test_led`: konfiguracja czytana, brak biblioteki = kod 2 i komunikat | potwierdzone wlasna proba: 8 testow, W3 -> 2 pada, T1-T5 |
| 4 | Pliki, testy zgodnosci z kodem, `bash -n`, znacznik w instrukcji | potwierdzone wlasna proba: 4 pliki + instrukcja, 15 testow, `bash -n` 2 x kod 0, znacznik przy 12 z 12 krokow (uwaga D5 o 2 sekcjach bez znacznika), W4a i W4c wykryte, W4b nie (D2) |
| 4 | Katalog `ramka/rpi` w paczce probnej (liczba plikow) | czeka na etap B2 (regule wyboru plikow potwierdza test `test_katalog_rpi_i_instrukcja_trafiaja_do_paczki...`) |
| 5 | 6 rozbieznosci A3 | potwierdzone przegladem: 1 (kroki: 9, pierwsza instalacja staje po 7) poprawiona; 2 (2 foldery obowiazkowe, 2 ostrzezenia, folder tymczasowy skanera) poprawiona; 3 (katalog po kodzie 10, `instalator.blokada`) poprawiona i zgodna z lista z raportu S1; 4 (`Polecenie.cmd`, `Dzien_skanera.cmd`, karta, `.bat`) poprawiona; 5 (445 MB, 1,4 GB) poprawiona - liczby z S1 dla 0.3.1, do ponownego pomiaru w B2; 6 (ekran, dwuklik) zostaje - niesprawdzalne bez ekranu. Brak opisu powrotu do 0.3.1 = P2 |
| 6 | Instalacja probna 10 -> 0, sumy, samokontrola, aktualizacja z 0.3.1 i powrot | czeka na etap B2 (P2 dotyczy wlasnie powrotu) |
| 7 | Pelny pytest 0 failed; wstrzykniecia min. 4 | pelny pytest: czeka na etap B2; wstrzykniecia: moje 9, wykryte 7, po min. 1 na punkty 1-4 |

## 4. Zakres plikow i zasady

- 24 zmienione pliki, wszystkie z listy zlecenia. Nie ruszono: plikow nietykalnych, `aplikacja.py`, `scanner.py`,
  `ustawienia.py`, `samokontrola.py`, `ramka/README.md`, `ramka/kalibracja.py`, plikow paczek O1 / O2 / O3, `Ramki/etap3/**`.
- `instrukcje/instalacja_i_aktualizacja.html` nie istnieje (w `instrukcje/` strony `.html` maja tylko pliki paczki O3) -
  nie bylo czego odswiezac.
- Konce linii (`git ls-files --eol`): `ramka/rpi/*.sh`, `ramka.service`, `ramka.json.wzor`, instrukcja, 3 testy, raport - LF;
  `Dzien_skanera.cmd`, `pomiar_skanu.cmd`, `uruchom_dzien_skanera.bat` - CRLF. W repo nie ma `.gitattributes`, ale paczke
  buduje `zbuduj_wydanie.pliki_z_gita` (bajty z gita), wiec `.sh` trafia do paczki z LF takze przy `autocrlf=true`.
- ASCII: 10 nowych plikow - 0 znakow spoza ASCII; w 14 plikach zmienionych liczba wierszy ze znakami spoza ASCII bez zmian
  (`dzien_skanera.py` 109, `dzien_skanera_rdzen.py` 102 - styl zastany).
- Dane osobowe: 0 trafien w diffie. Duze dane: brak (najwiekszy nowy plik to raport, 558 wierszy).
- Brak zmiany schematu bazy, brak nowych pakietow, 0 `skip` / `xfail` w nowych testach (3 wystapienia `pytest.skip`, wszystkie dla komputera bez bash; u mnie 0 skipped).
- Kopia `rec-o4`: `git status --short` pusty po probach. Worktree wykonawcy, repo glowne i `t0\s1` tylko czytane.

## 5. Do decyzji wlasciciela

1. Skrot `Dzien_skanera.cmd`: czy katalog sesji ma byc zawsze `<instalacja>\dane\dzien_skanera` (skrot podaje `--dane`;
   prosto, odporne na powrot do 0.3.1 - propozycja z P2), czy ma isc za katalogiem bazy z ustawien (stan z paczki; zgodny
   z programem "Stanowisko", ale po powrocie do 0.3.1 wymaga dodatkowego zabezpieczenia w skrocie). Domyslnie: wariant z `--dane`.
2. Karta SD ramki od dostawcy (D4): czy instrukcja ma zakazywac nadpisania karty zastanej (zalecane), czy wlasciciel wie,
   ze karta jest pusta.
3. Program ramki uruchomiony z `host` innym niz 127.0.0.1 i BEZ klucza tylko ostrzega w logu i dziala (`ramka/program.py:367`,
   plik spoza tej paczki). Skrypt instalacji zawsze wpisuje klucz, a `sprawdz_ramke.sh` pokazuje pusty klucz jako BRAK, wiec
   droga z instrukcji jest bezpieczna; decyzja, czy program ma odmawiac startu bez klucza, nalezy do paczki ramki (O2 / C1).

## 6. Dla wykonawcy etapu B2: co sprawdzic na instalacji probnej

1. Powrot do 0.3.1 (P2): po `Wroc_do_poprzedniej.cmd /tak /bez-pauzy` wypisz skrypty w katalogu (oczekiwane 6) i uruchom
   okno przez `Dzien_skanera.cmd` BEZ `--zamknij-po` (stary modul nie zna opcji - kod 2), np. sterownikiem S1 wolanym tak
   jak skrot; porownaj liste plikow `wersje\0.3.1\program\dane` przed i po. Po poprawce P2: 0 nowych plikow w katalogu
   wersji, sesja w `<instalacja>\dane\dzien_skanera`. To samo po ponownym `zainstaluj.cmd` z paczki 0.3.1 na instalacji
   z wersja probna (stary instalator zapisuje 5 skryptow, szosty zostaje).
2. P1 na instalacji: zmien nazwe `<instalacja>\ustawienia.toml`, uruchom `Dzien_skanera.cmd --nowa --zamknij-po 2`, sprawdz,
   gdzie powstala sesja i co wypisal wiersz `DZIEN SKANERA: ...`; przywroc plik. Druga proba: `baza` wzgledna.
3. Skrot nie ustawia `QT_QPA_PLATFORM` - w sesji bez ekranu ustaw `set QT_QPA_PLATFORM=offscreen` przed wywolaniem i dawaj
   `< NUL` (przy kodzie roznym od 0 i braku argumentow skrot robi `pause`).
4. Sterownik S1 `dzien_skanera_proba.py:55` wola `wybierz_sesje(a, ust, None)` bez `plik_ustawien` - przechodzi wtedy przez
   regule 2, nie 1. W kopii w `robocze\o4` dodaj `plik_ustawien=plik_ust`, inaczej proba nie sprawdza drogi skrotu.
5. Katalog wersji po sesji okna i po pomiarze z przycisku: 0 nowych plikow (takze `__pycache__` - skrot ustawia
   `PYTHONDONTWRITEBYTECODE`, ale proces pomiaru dziedziczy srodowisko okna - sprawdz), samokontrola "plikow nadmiarowych 0".
6. Przycisk pomiaru: `sys.executable` okna = `wersje\<w>\venv\Scripts\python.exe`, w poleceniu jest `--ustawienia
   <instalacja>\ustawienia.toml`, kod 0, czas. `pomiar_skanu.cmd` nie da sie uruchomic bez ekranu w calosci (Notatnik, pauza),
   ale wybor interpretera mozna sprawdzic: `cmd /c "...\pomiar_skanu.cmd C:\nie_ma.stl" < NUL` - blad pliku skanu wypisany
   przez Pythona srodowiska wersji (nie `'py' is not recognized`), raportu nie ma, wiec Notatnik sie nie otwiera.
7. Paczka probna: `program\ramka\rpi` = 4 pliki, w ZIP i po instalacji bajt w bajt z gita (0 znakow CR w obu `.sh`
   i w `ramka.service`); `program\instrukcje\ramka_raspberry_pi.md` jest; liczba plikow programu (wykonawca oczekuje 137).
8. Aktualizacja z 0.3.1: po `zainstaluj.cmd` paczki probnej `Dzien_skanera.cmd` bajtowo rowny wzorowi z nowej wersji;
   sesje zapisane wczesniej przez 0.3.1 w `wersje\0.3.1\program\dane\dzien_skanera` zostaja nietkniete (instrukcja p. 7).
9. Katalog instalacji ze spacja w nazwie (np. `<PC-katalog>\t0\o4\Stanowisko proba`), jesli czas pozwoli: moja proba
   sprawdzila modul i sciezke bledu skrotu w takim katalogu, ale nie pelny start przez `cmd.exe` ze srodowiskiem wersji.
10. Rozmiary do instrukcji (445 MB, 1,4 GB) i liczba krokow / zawartosc katalogu po kodzie 10 - potwierdzic na paczce probnej.
