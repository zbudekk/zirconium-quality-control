# instalacja - paczka wydania, instalacja, aktualizacja, powrot (E3-A11i, 20.11.2026; wariant B dystrybucji)

**Co robi.** Jedna paczka `Stanowisko_<wersja>.zip` (program + kola pip + instalator) instaluje program bez internetu do
katalogu wersji z wlasnym srodowiskiem wirtualnym; ustawienia i dane leza poza katalogiem wersji; aktualizacja i powrot
do poprzedniej wersji to jedno polecenie. Pliki: `narzedzia/zbuduj_wydanie.py` (budowa), `instalacja/instalator.py`
(logika, tylko biblioteka standardowa), `instalacja/zainstaluj.cmd`, `instalacja/wzory/*.cmd` (skrypty uruchamiajace),
`instalacja/zamrozone.txt` i `zamrozone_testy.txt` (wersje pakietow), `WERSJA` (numer wersji, jeden wiersz).
Instrukcja dla osoby instalujacej: `instrukcje/instalacja_i_aktualizacja.md`.

**Zasada nadrzedna.** W zadnej sciezce instalator ani powrot nie zostawia stanowiska bez bazy, z baza uszkodzona albo
ze starsza trescia bez jawnej zgody; wersja biezaca zmienia sie wylacznie po zielonej samokontroli; instalator usuwa
tylko katalogi, ktore sam oznaczyl.

## Paczka wydania

```
python narzedzia/zbuduj_wydanie.py --wyjscie <PC-katalog>\wydania [--wersja X] [--kola KATALOG] [--rewizja COMMIT]
python narzedzia/zbuduj_wydanie.py --pobierz-kola --kola KATALOG [--python python.exe]      (jedyny krok z internetem)
```

| W paczce | Co |
|---|---|
| `zainstaluj.cmd`, `CZYTAJ.txt` | start instalacji, trzy zdania dla czlowieka |
| `program/` | `stanowisko/`, `modele_plytek/`, `narzedzia/` (bez `zbuduj_wydanie.*`), `ramka/` (importuje ja `stanowisko/ramka_protokol.py`), CALY katalog `instrukcje/` (kazdy plik: `.md`, `.html`, podkatalogi - takze te, ktore dojda), `instalacja/`, `ustawienia.przyklad.toml`, `requirements.txt` (samokontrola porownuje z nim wersje pakietow), `WERSJA`; bez `testy/`, `raporty/`, `opisy_modulow/`, danych i `__pycache__` |
| `program/SUMY_PROGRAMU.sha256` | suma KAZDEGO pliku katalogu programu (takze `ramka/`, `requirements.txt` i pliki katalogu glownego), format `sha256sum` (umowa samokontroli A11s: `--sumy`; samokontrola liczy tez pliki nadmiarowe - instalator kopiuje do katalogu programu wylacznie pliki z listy) |
| `kola/` | kola binarne (Windows x64, Python 3.12) wszystkich pakietow z `zamrozone.txt`, takze zaleznosci posrednich |
| `kola_testy/` | pytest i jego zaleznosci (`zamrozone_testy.txt`) - instalowane tylko przez `zainstaluj.cmd /testy` |
| `wydanie.json` | wersja, commit, data commita, wersja Pythona (`python` = 3.12, `python_sprawdzony` = 3.12.10), lista kol z sumami i rozmiarami |
| `SHA256SUMS` | suma kazdego pliku paczki; instalator sprawdza ja jako pierwszy krok |

- **Zrodlo plikow programu:** commit `HEAD` (tresc obiektow gita - zmiany niezacommitowane i pliki spoza gita nie wchodza,
  jest ostrzezenie). `--zrodlo KATALOG --data RRRR-MM-DDTGG:MM:SS [--commit OPIS]` bierze pliki z katalogu (proby).
- **Powtarzalnosc bajtowa:** ten sam commit + te same kola = ten sam SHA-256 ZIP (data wpisow = data commita UTC, staly
  porzadek i atrybuty, kola bez kompresji, reszta deflate 9, skrypty `.cmd` zawsze z CRLF). Granica: inna wersja biblioteki
  zlib (inny Python budujacy) moze dac inne bajty kompresji - budowac tym samym interpreterem.
- **Numer wersji** (`0.3.<n>`): plik `WERSJA` albo `--wersja`. Kazda OPUBLIKOWANA budowa dostaje nowy numer - po budowie
  dopisz sume do `Ramki/etap3/wydania/SHA256SUMS_wydania.txt` i zwieksz `WERSJA`; budowa pod numerem z tej listy o innej
  sumie daje `OSTRZEZENIE`, a test pilnuje, ze `WERSJA` nie jest numerem juz opublikowanym. Numer jest nazwa katalogu
  w Windows: litery, cyfry, `.`, `_`, `-`, pierwszy i ostatni znak to litera albo cyfra (kropka na koncu znika z nazwy
  katalogu), do 32 znakow, nie nazwa urzadzenia (`NUL`, `COM1`...); numery rozniace sie wielkoscia liter to ten sam katalog.
- **Listy zamrozone** generuje `--pobierz-kola`: `pip freeze` interpretera, na ktorym przechodza testy, sluzy jako
  ograniczenia (`-c`); do `zamrozone.txt` trafia to, co pip dobiera dla `requirements.txt` bez pytest (73 pakiety), do
  `zamrozone_testy.txt` reszta potrzebna pytestowi (3). Z `pip freeze` odpadaja `pip` i pakiety spoza zaleznosci.
  Pobieranie: `pip download --only-binary=:all: --platform win_amd64 --python-version 3.12`; pakiet bez kola binarnego
  = blad (budowa nie kompiluje ze zrodel). Zmiana `requirements.txt` = ponowne `--pobierz-kola` (test pilnuje zgodnosci).
  Paczka nie jest odchudzana z zaleznosci nieuzywanych: srodowisko = dokladnie to, na ktorym przechodza testy.
- Bez modulu `stanowisko/samokontrola.py` budowa odmawia (`--bez-samokontroli` tylko do prob; instalator takiej paczki nie
  zainstaluje: "blad wydania"). ZIP, kola i katalogi robocze nigdy do gita; sumy wydan: `Ramki/etap3/wydania/`.

## Katalog instalacji

```
<KATALOG>\                      domyslnie C:\Stanowisko (opcja /katalog); nie w OneDrive / SharePoint
  Stanowisko.cmd  Samokontrola.cmd  Wroc_do_poprzedniej.cmd  Wersje.cmd  Polecenie.cmd
  ustawienia.toml               przy pierwszej instalacji ze wzoru, potem nietykany (bajt w bajt)
  dane\                         baza, wyniki, logi, dane\kopie\ (kopie bazy) - poza katalogiem wersji
  wersja_biezaca.txt            wskaznik = plik tekstowy z numerem wersji (nie dowiazanie), zapis atomowy
  wersja_poprzednia.txt         dokad wraca Wroc_do_poprzedniej.cmd
  dziennik_instalacji.txt       data, operacja, kroki, wynik samokontroli (poziom i kod sprawdzen, bez opisow)
  instalator.blokada            naraz jeden instalator / powrot w tym katalogu (drugie okno: kod 6 "juz trwa")
  wersje\<wersja>\program\      pliki z paczki; wersje\<wersja>\venv\ - srodowisko tej wersji
  wersje\<wersja>\instalacja.json, wydanie.json, pip.log;  NIEDOKONCZONA.txt = instalacja przerwana
  wersje\_stara_<wersja>\       wersja odlozona na czas naprawy (wraca, gdy naprawa sie nie uda)
```

Skrypty ustawiaja `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1` (katalog programu zostaje identyczny z paczka),
`PYTHONNOUSERSITE=1`, czyszcza `PYTHONPATH` i `PYTHONHOME` i uruchamiaja `wersje\<biezaca>\venv\Scripts\python.exe`
w katalogu programu. `Stanowisko.cmd` dodaje `--ustawienia <KATALOG>\ustawienia.toml` i przekazuje argumenty (`--atrapa`,
`--zamknij-po 5`); `Polecenie.cmd <argumenty pythona>` to Python wersji biezacej (np. `Polecenie.cmd -m stanowisko.dzien_skanera`).
Pauza na koncu: `zainstaluj.cmd`, `Wroc_do_poprzedniej.cmd` i `Wersje.cmd` czekaja na klawisz ZAWSZE, chyba ze podano
`/bez-pauzy` (okno uruchomione ze skrotu albo Win+R nie zamyka sie przed przeczytaniem wyniku); `Stanowisko.cmd`,
`Samokontrola.cmd` i `Polecenie.cmd` przekazuja wszystkie argumenty dalej, wiec czekaja tylko przy uruchomieniu bez argumentow.

## zainstaluj.cmd [/katalog K] [/python P] [/skrot] [/testy] [/bez-sieci] [/bez-pauzy]

`zainstaluj.cmd` czysci `PYTHONHOME` / `PYTHONPATH`, szuka Pythona 3.12 (opcja `/python`, zmienna `STANOWISKO_PYTHON`,
`py -3.12`, typowe katalogi `Python312`, `python` z PATH; proby z `-I`; wskazany wprost musi byc 3.12, inaczej stop)
i uruchamia `instalator.py zainstaluj`:

1. sumy `SHA256SUMS` kazdego pliku paczki; niezgodnosc, brak `wydanie.json` albo modulu samokontroli, zly numer wersji
   = stop (kod 3),
2. Python: wersja z `wydanie.json` (3.12), 64 bity, modul `venv` (kod 4). Wersja poprawkowa inna niz `python_sprawdzony`
   (3.12.10) jest przyjmowana z wierszem `OSTRZEZENIE: Python ...` na ekranie i w dzienniku,
3. katalog instalacji: nie w folderze synchronizowanym, bez srednika w sciezce, sciezki plikow pakietow do 259 znakow,
   prawo zapisu; blokada instalatora; sprzatanie po przerwanych probach - WYLACZNIE katalogow oznaczonych przez instalator:
   wersja ze znacznikiem `NIEDOKONCZONA.txt` (nie biezaca) jest usuwana, wersja odlozona `_stara_<wersja>` wraca na miejsce
   (przerwana naprawa) albo jest usuwana (naprawa zakonczona). Inne wpisy w `wersje\` (cudze katalogi, takze o nazwie jak
   numer wersji) zostaja nietkniete: liczba w dzienniku, nazwy tylko na ekranie,
4. ustawienia: brak pliku = wzor z kazda wzgledna sciezka `[sciezki]` zamieniona na `<KATALOG>/dane/...`; plik istniejacy
   zostaje. Kod programu z paczki (`ustawienia.wczytaj_ustawienia`, `baza.sciezka_bazy`, `max(baza.MIGRACJE)`) odpowiada,
   gdzie jest baza i jaki schemat obsluguje wersja; blad pliku, znak BOM na poczatku albo sciezka wzgledna w `[sciezki]`
   = stop (kod 7; wartosc pusta, np. `folder_millbox = ""`, nie jest sciezka wzgledna); program uruchomiony (plik
   `<baza>.blokada`, ten sam co `aplikacja.BlokadaStanowiska`) = stop (kod 5). Pod blokada programu baza jest otwierana
   (wycofanie przerwanego zapisu, wersja schematu): baza zajeta = kod 5, nieczytelna albo slad przerwanego przywracania
   (`<baza>.nowy` bez bazy) = kod 6 - wszystko PRZED instalacja pakietow,
5. katalog wersji: numer zapisany inaczej niz istniejacy katalog (wielkosc liter) = kod 3; katalog o numerze paczki, ktorego
   nie zalozyl instalator = kod 6; miejsce na dysku (rozmiar kol po rozpakowaniu x 1,3 + program + 300 MB), znacznik,
   pliki programu (kontrola sum), `python -m venv --copies`, `pip install --isolated --no-index --only-binary=:all:
   --find-links kola -r zamrozone.txt`, porownanie `pip list` z lista zamrozona (n z n; `pip` zalozony przez venv nie jest
   liczony), `instalacja.json`, zdjecie znacznika. Wersja juz zainstalowana z tej samej paczki i cala = bez zmian - od razu
   samokontrola i przelaczenie (z `/testy` dokladany jest sam zestaw testowy). Wersja uszkodzona = NAPRAWA: stary katalog
   jest odkladany jako `wersje\_stara_<wersja>` (zmiana nazwy pod blokada programu), nowy powstaje od zera, a przy bledzie
   albo przerwaniu stary wraca na miejsce - wersja biezaca nie zostaje w polowie. Paczka o tym samym numerze, ale innej
   tresci (inne sumy `wydanie.json` albo `SUMY_PROGRAMU.sha256` niz w `instalacja.json`) nie zastepuje wersji biezacej ani
   poprzedniej (kod 3) - nowe wydanie = nowy numer; wersje nieuzywana zastepuje (ta sama droga co naprawa),
6. kopia bazy `dane\kopie\<baza>_przed_<wersja>_<data>_<godzina>_v<schemat>.sqlite`, gdy wersja inna niz biezaca i baza
   istnieje: mechanizm kopii SQLite z bazy otwartej do zapisu (przerwany zapis jest najpierw wycofywany), potem kontrola
   kopii (`PRAGMA quick_check` = ok, ta sama wersja schematu). Kopii nie da sie zrobic albo nie przechodzi kontroli = stop
   (kod 6), wersja nie jest przelaczana; kopii "niesprawdzonej" nie ma nigdy,
7. samokontrola nowej wersji: `python -m stanowisko.samokontrola --ustawienia <KATALOG>\ustawienia.toml --sumy
   program\SUMY_PROGRAMU.sha256 [--bez-sieci]`; kod 1 albo 2 = wersja zostaje zainstalowana, ale NIE biezaca. Kod spoza
   umowy 0 / 1 / 2 (proces samokontroli zginal, np. `0xC0000005`) = do 2 powtorzen po 3 s przerwy, kazde z wierszem
   `UWAGA samokontrola: ...` na ekranie i w dzienniku; trzecia awaria z rzedu = kod 2 instalatora z rada "uruchom ponownie",
8. zapis skryptow ze wzorow i przelaczenie wskaznika (pod blokada programu); poprzednia wersja zapamietana,
9. skrot na pulpicie tylko z `/skrot` (PowerShell `WScript.Shell`; niepowodzenie = ostrzezenie).

Wiersz koncowy: `INSTALACJA: GOTOWA - wersja biezaca X ...`; przy bledzie `BLAD: ...`, `CO ZROBIC: ...`,
`INSTALACJA: NIEUDANA (kod N) - wersja biezaca bez zmian: X` (gdy katalog wersji biezacej jest niekompletny po zamknieciu
okna w trakcie naprawy: `... - UWAGA: wersja biezaca X jest niekompletna ...`); bledy samego `zainstaluj.cmd` (kod 4,
brak instalatora): `INSTALACJA: NIEUDANA (kod N) - niczego nie zmieniono.` **Pierwsza instalacja** (nie ma jeszcze wersji
biezacej), gdy samokontrola daje kod 1: zasada "wersja biezaca zawsze po zielonej samokontroli" zostaje, ale to zamierzony
etap, nie niepowodzenie - wiersze `BLAD ...` samokontroli, `Plik ustawien: <pelna sciezka>`, `CO ZROBIC: ...` i wiersz
koncowy `INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom zainstaluj.cmd ponownie (kod 10)`. Ponowne
`zainstaluj.cmd` tej samej paczki nie buduje srodowiska od nowa (kilka sekund).

| Kod | Znaczenie |
|---|---|
| 0 | wersja z paczki jest wersja biezaca |
| 1 / 2 | samokontrola przy aktualizacji: bledy / nie dalo sie wykonac - wersja zainstalowana, nie przelaczona |
| 3 | paczka: sumy, braki, blad wydania, inna budowa albo inna pisownia numeru wersji uzywanej |
| 4 | brak Pythona 3.12 albo zla wersja |
| 5 | program uruchomiony albo baza zajeta przez inny program |
| 6 | katalog, miejsce na dysku, venv, pip, przerwanie, baza nieczytelna / kopia bazy nieudana, druga instalacja naraz |
| 7 | ustawienia: blad pliku, BOM albo sciezki wzgledne w `[sciezki]` |
| 8 | powrot: baza nowsza niz poprzednia wersja - potrzebna zgoda `/przywroc-kopie` albo brak sprawdzonej kopii |
| 9 | brak wersji (powrot bez poprzedniej; usuwanie biezacej, poprzedniej albo nieistniejacej) |
| 10 | pierwsza instalacja WSTRZYMANA: wersja zainstalowana, samokontrola czeka na uzupelnienie `ustawienia.toml` |
| 11 | powrot ANULOWANY: odpowiedz na pytanie T / N inna niz T - nic nie zmieniono |

## Wroc_do_poprzedniej.cmd [/tak] [/przywroc-kopie] [/bez-pauzy], Wersje.cmd [/usun WERSJA] [/bez-pauzy]

- **Powrot** przelacza wskaznik na wersje poprzednia (ponowny powrot wraca do nowszej). Bez opcji pyta
  `Powrot z wersji A do wersji B. Kontynuowac? [T/N]` (skrypt lezy obok `Stanowisko.cmd`; brak odpowiedzi albo inna niz T
  = kod 11, nic nie zmienione); `/tak` pomija pytanie (skrypty, test T12), `/przywroc-kopie` tez jest jawna zgoda.
  Przed przelaczeniem: kod poprzedniej wersji musi przyjac obecny `ustawienia.toml` (klucz dodany dla nowszej wersji =
  stop, kod 7), program musi byc zamkniety, baza czytelna, a schemat bazy (`PRAGMA user_version`) nie moze byc nowszy niz
  obslugiwany przez poprzednia wersje.
  - Baza nowsza: ostrzezenie (ktora kopia wroci, ile jest starszych i pominietych, ile wpisow w ktorych tabelach przybylo
    od tej kopii) i stop z kodem 8. Kopia do przywrocenia = NAJNOWSZA (czas z nazwy pliku) sprawdzona (`quick_check` = ok)
    kopia o schemacie obslugiwanym przez wersje docelowa, ze wszystkich zrodel: kopie instalatora
    `dane\kopie\<baza>_przed_*` i kopie programu sprzed migracji `<baza>.kopia_v*`.
  - Z `/przywroc-kopie`: (1) sprawdzona kopia biezacej bazy do `dane\kopie\<baza>_odlozona_v<schemat>_<czas>.sqlite`
    (kopia tresci mechanizmem SQLite), (2) sprawdzona kopia wybranego pliku jako `<baza>.nowy`, (3) jedna zamiana atomowa
    `<baza>.nowy` -> `<baza>`. Plik bazy istnieje i jest caly w kazdej chwili; blad = baza bez zmian, kod 6.
  - Baza STARSZA niz schemat wersji docelowej ("powrot" do nowszej wersji, ktora zmigruje baze przy starcie): przed
    przelaczeniem powstaje kopia `<baza>_przed_<wersja>_...` - tak jak przy aktualizacji.
  - Bez roznicy schematu baza nie jest ruszana. Po przelaczeniu samokontrola wersji docelowej - informacyjnie.
- **Wersje** i kopie bazy nie sa kasowane automatycznie. `Wersje.cmd` wypisuje wersje (BIEZACA, poprzednia, NIEDOKONCZONA,
  OBCY KATALOG); `/usun WERSJA` usuwa katalog wersji zalozony przez instalator, ktora nie jest ani biezaca, ani
  poprzednia. Ustawien i danych nie dotyka.

## Kryterium "dziala"

`testy/test_zbuduj_wydanie.py` (budowa: dwie budowy = ten sam ZIP, zawartosc, sumy, kola, tryb commita, numer wersji)
i `testy/test_instalacja.py` (instalacja, aktualizacja, powrot, bledy - na malej paczce w `tmp_path`; baza z przerwanym
zapisem, przerwane przywrocenie kopii, drugi powrot, cudze katalogi, pisownia numeru, przerwana naprawa; polecenia
`venv` / `pip`; jeden test z prawdziwym `python -m venv` i skryptami `.cmd` przy wrogim `PYTHONPATH` / `PYTHONHOME`).
Proby na PC z pelna paczka i liczby: `raporty/E3-A11i_2026-11-20.md`.

## Zalozenia i granice

- Python 3.12 instaluje sie raz recznie (sprawdzona wersja 3.12.10); instalator niczego nie instaluje w systemie i nie
  uzywa sieci.
- Srodowisko wersji wskazuje interpreter bazowy (`pyvenv.cfg`): odinstalowanie albo przeniesienie Pythona 3.12 psuje
  wszystkie wersje - naprawa: ponowne `zainstaluj.cmd`. Katalogu instalacji nie przenosic (skrypty srodowiska maja
  wpisana sciezke).
- **Znane ograniczenie (a) - dane w katalogu wersji.** `stanowisko/dzien_skanera_rdzen.py` (sesje `dane/dzien_skanera/`)
  i `stanowisko/ui_test.py` (`dane/decyzje.csv`) pisza na stale do `<katalog programu>/dane`, czyli w instalacji z paczki
  do katalogu WERSJI: te dane nie przechodza do nowej wersji i znikaja z `Wersje.cmd /usun`. Poprawka nalezy do osobnej
  paczki (sciezka z ustawien zamiast stalej). Program "Stanowisko" (baza, wyniki, logi) tego nie dotyczy.
- **Znane ograniczenie (b) - przyszly klucz `[sciezki]`.** Dane poza katalogiem wersji trzyma wylacznie `ustawienia.toml`
  ze sciezkami bezwzglednymi. Nowy klucz `[sciezki]` z domyslna wartoscia wzgledna (`dane/...`), ktorego nie ma
  w istniejacym pliku, zatrzyma aktualizacje (kod 7) do recznego dopisania wiersza podanego w komunikacie - instalator
  pliku ustawien nie zmienia.
- **Znane ograniczenie (c) - laptop firmowy.** Instalacji nie sprawdzono na laptopie firmowym: WDAC, antywirus (skanowanie
  ok. 18 tys. plikow srodowiska, blokady plikow przy zmianie nazwy katalogu), ostrzezenie Windows przy uruchomieniu pliku
  `.cmd` z paczki pobranej z sieci ("Windows ochronil ten komputer" / znacznik pochodzenia), polityka PowerShell dla
  skrotu. Nie sprawdzono tez prawdziwego braku miejsca na dysku (symulacja) ani Pythona 3.12 innego niz 3.12.10.
- Okno zamkniete w trakcie NAPRAWY wersji biezacej zostawia ja niekompletna do nastepnego `zainstaluj.cmd` (skrypty
  odmawiaja startu z komunikatem; instalator przywraca wtedy odlozony katalog). Blad pip albo Ctrl+C cofa naprawe od razu.
- Kopia "odlozona" i kopie `_przed_` to kopie tresci (mechanizm kopii SQLite), nie pliki bajt w bajt (inny licznik zmian
  w naglowku). Kazda zajmuje tyle, co baza; nic nie jest kasowane automatycznie.
- Zabicie instalatora miedzy zapisem `wersja_poprzednia.txt` a `wersja_biezaca.txt` (milisekundy) zostawia oba wskazniki
  z ta sama wersja: `Wroc_do_poprzedniej.cmd` odpowiada "nie ma poprzedniej wersji" (kod 9), ponowne `zainstaluj.cmd` naprawia.
- Starsza wersja programu odrzuca nieznane klucze ustawien: po recznym dopisaniu klucza nowej wersji powrot wymaga
  jego usuniecia (instalator to wykrywa przed przelaczeniem).
- Skrot na pulpicie zalezy od polityki komputera (PowerShell w trybie ograniczonym nie zalozy skrotu) - wtedy dwuklik
  `Stanowisko.cmd`.
- `kola/` zawiera caly zestaw zaleznosci Open3D i PySide6 (m.in. PySide6 WebEngine 132 MB, plotly 10 MB, dash 9 MB - razem co najmniej ok. 160 MB), ktorych
  program nie importuje, ale ktorych wymaga pip przy instalacji przypietych wersji (decyzja: paczki nie odchudzamy).
