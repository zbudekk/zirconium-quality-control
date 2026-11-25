# instalacja - paczka wydania, instalacja, aktualizacja, powrot (E3-A11i, 20.11.2026; wariant B dystrybucji; E3-I1, 25.11.2026: Python w paczce i okno instalatora)

**Co robi.** Jedna paczka `Stanowisko_<wersja>.zip` (program + kola pip + instalator) instaluje program bez internetu do
katalogu wersji z wlasnym srodowiskiem wirtualnym; ustawienia i dane leza poza katalogiem wersji; aktualizacja i powrot
do poprzedniej wersji to jedno polecenie. Pliki: `narzedzia/zbuduj_wydanie.py` (budowa), `instalacja/instalator.py`
(logika, tylko biblioteka standardowa), `instalacja/zainstaluj.cmd`, `instalacja/wzory/*.cmd` (skrypty uruchamiajace),
`instalacja/zamrozone.txt` i `zamrozone_testy.txt` (wersje pakietow), `WERSJA` (numer wersji, jeden wiersz).
E3-I1: `instalacja/Instaluj.cmd` (dwuklik - okno), `instalacja/okno_instalatora.py` (okno Qt), `instalacja/kreator.py` (logika okna
i trybu bez okna, tylko biblioteka standardowa), `instalacja/napisy_instalatora.py` (teksty ekranu, UTF-8 ze znakami diakrytycznymi),
`instalacja/wzory/start_bez_konsoli.pyw` (starter ikon) - sekcja "Python w paczce i okno instalatora (E3-I1)".
Instrukcja dla osoby instalujacej: `instrukcje/instalacja_i_aktualizacja.md`.

**Zasada nadrzedna.** W zadnej sciezce instalator ani powrot nie zostawia stanowiska bez bazy, z baza uszkodzona albo
ze starsza trescia bez jawnej zgody; wersja biezaca zmienia sie wylacznie po zielonej samokontroli; instalator usuwa
tylko katalogi, ktore sam oznaczyl.

## Paczka wydania

```
python narzedzia/zbuduj_wydanie.py --wyjscie <PC-katalog>\wydania [--wersja X] [--kola KATALOG] [--rewizja COMMIT]
python narzedzia/zbuduj_wydanie.py --pobierz-kola --kola KATALOG [--python python.exe]      (krok z internetem)
python narzedzia/zbuduj_wydanie.py --pobierz-pythona --python-nuget KATALOG                 (krok z internetem, E3-I1)
```

E3-I1: budowa domyslnie bierze pakiet Pythona z `<wyjscie>/python_nuget/python.3.12.10.nupkg` (`--python-nuget` - inny plik albo
katalog); bez niego odmawia (`--bez-pythona` - paczka jak dotad, bez Pythona i okna, tylko do prob).

| W paczce | Co |
|---|---|
| `Instaluj.cmd` | E3-I1: dwuklik = okno instalatora (`start "" python\pythonw.exe -I -B program\instalacja\okno_instalatora.py`; konsola znika) |
| `zainstaluj.cmd`, `CZYTAJ.txt` | start instalacji z wiersza polecen, kilka zdan dla czlowieka |
| `python/` | E3-I1: pelny Python 3.12.10 64 bit = katalog `tools/` pakietu `python` z nuget.org (oryginalne pliki: `python.exe`, `pythonw.exe`, `python312.dll`, `*.pyd` podpisane przez PSF; jest `venv` i `ensurepip` z kolem pip 25.0.1); suma pakietu przypieta w `zbuduj_wydanie.PYTHON_NUGET_SHA256`, zapisana obok pakietu przy pobraniu i sprawdzana przy budowie (1322 pliki) |
| `okno/` | E3-I1: biblioteka okna instalatora - wycinek kol `shiboken6` i `pyside6_essentials` z `kola/` (`WYCINEK_OKNA`: QtCore, QtGui, QtWidgets, wtyczki `qwindows` / `qoffscreen`, styl, biblioteki VC; 37 plikow, ok. 45 MB) - okno startuje z Pythona paczki, zanim powstanie srodowisko wersji |
| `program/` | `stanowisko/`, `modele_plytek/`, `narzedzia/` (bez `zbuduj_wydanie.*`), `ramka/` (importuje ja `stanowisko/ramka_protokol.py`), CALY katalog `instrukcje/` (kazdy plik: `.md`, `.html`, podkatalogi - takze te, ktore dojda), `instalacja/`, `ustawienia.przyklad.toml`, `requirements.txt` (samokontrola porownuje z nim wersje pakietow), `WERSJA`; bez `testy/`, `raporty/`, `opisy_modulow/`, danych i `__pycache__` |
| `program/SUMY_PROGRAMU.sha256` | suma KAZDEGO pliku katalogu programu (takze `ramka/`, `requirements.txt` i pliki katalogu glownego), format `sha256sum` (umowa samokontroli A11s: `--sumy`; samokontrola liczy tez pliki nadmiarowe - instalator kopiuje do katalogu programu wylacznie pliki z listy) |
| `kola/` | kola binarne (Windows x64, Python 3.12) wszystkich pakietow z `zamrozone.txt`, takze zaleznosci posrednich |
| `kola_testy/` | pytest i jego zaleznosci (`zamrozone_testy.txt`) - instalowane tylko przez `zainstaluj.cmd /testy` |
| `wydanie.json` | wersja, commit, data commita, wersja Pythona (`python` = 3.12, `python_sprawdzony` = 3.12.10), lista kol z sumami i rozmiarami; E3-I1: `python_w_paczce` (wersja, zrodlo, plik, sha256 pakietu, liczba plikow) i `okno_instalatora` (kola, liczba plikow) - tylko w paczce z Pythonem (paczka bez niego zostaje bajt w bajt taka jak przed E3-I1) |
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
  Stanowisko.cmd  Samokontrola.cmd  Wroc_do_poprzedniej.cmd  Wersje.cmd  Polecenie.cmd  Dzien_skanera.cmd
  start_bez_konsoli.pyw         E3-I1: starter ikon pulpitu (wzor jak skrypty; wersje sprzed E3-I1 go nie maja i nie usuwaja)
  python\<wersja Pythona>\      E3-I1: kopia Pythona z paczki (np. python\3.12.10\) - interpreter bazowy srodowisk wersji
                                instalowanych z paczki (pyvenv.cfg: home = ten katalog); instalator go nie usuwa
  dane\ostatni_start_<cel>.txt  E3-I1: wyjscie programu uruchomionego ikona (starter; nadpisywany przy kazdym starcie)
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
`--zamknij-po 5`); `Polecenie.cmd <argumenty pythona>` to Python wersji biezacej (np. `Polecenie.cmd narzedzia\symulator_skanera.py`).
`Dzien_skanera.cmd` (E3-O4) uruchamia okno "Dzien skanera" tym samym sposobem co `Stanowisko.cmd`: `-m stanowisko.dzien_skanera
--ustawienia <KATALOG>\ustawienia.toml --dane <KATALOG>\dane\dzien_skanera` + argumenty (`--nowa`, `--sprawdz <zip>`,
`--zamknij-po 5`); sesje trafiaja do `<KATALOG>\dane\dzien_skanera\` (katalog podany wprost - takze modul wersji 0.3.1,
uruchomiony tym skryptem po powrocie do niej, zapisuje sesje tam, a nie w katalogu wersji), przy bledzie okno czeka tylko,
gdy uruchomiono bez argumentow. `wroc` skryptow nie zmienia: po powrocie do 0.3.1 w katalogu zostaje 6 skryptow nowszej wersji.
Lista skryptow: `instalator.WZORY_SKRYPTOW` (6 pozycji) - `zapisz_skrypty` kopiuje je przy przelaczeniu wersji; samokontrola
listy skrotow nie ma (sprawdza katalog programu wersji, nie katalog instalacji).
Pauza na koncu: `zainstaluj.cmd`, `Wroc_do_poprzedniej.cmd` i `Wersje.cmd` czekaja na klawisz ZAWSZE, chyba ze podano
`/bez-pauzy` (okno uruchomione ze skrotu albo Win+R nie zamyka sie przed przeczytaniem wyniku); `Stanowisko.cmd`,
`Samokontrola.cmd`, `Polecenie.cmd` i `Dzien_skanera.cmd` przekazuja wszystkie argumenty dalej, wiec czekaja tylko przy uruchomieniu bez argumentow.

## zainstaluj.cmd [/katalog K] [/python P] [/skrot] [/testy] [/bez-sieci] [/bez-pauzy]

`zainstaluj.cmd` czysci `PYTHONHOME` / `PYTHONPATH`, wybiera Pythona 3.12: opcja `/python`, zmienna `STANOWISKO_PYTHON`, E3-I1:
Python z paczki (`python\python.exe` - wtedy `instalator.py zainstaluj --python-z-paczki`), a w paczce bez niego szuka w systemie
(`py -3.12`, typowe katalogi `Python312`, `python` z PATH; proby z `-I`; wskazany wprost musi byc 3.12, inaczej stop)
i uruchamia `instalator.py zainstaluj`. E3-I1: opcje z okna (dzialaja tez z wiersza polecen) `--folder-skanow`, `--folder-projektow`
(pusty = `<KATALOG>/dane/projekty`, zakladany), `--osoba` (powtarzalna), `--ramki-wylaczone` sa wpisywane WYLACZNIE do nowego
pliku ustawien (`ustawienia_ze_wzoru(..., wartosci)`: wartosc wiersza zastapiona, komentarz zostaje; klucza nieobecnego we wzorze
- nowy wiersz pod naglowkiem sekcji); istniejacy plik zostaje bajt w bajt, a na ekranie jest wiersz "foldery i osoby podane w oknie
NIE zostaly wpisane". `--ramki-wylaczone` wpisuje `[ramki] wlaczone = false` tylko, gdy kod programu z paczki zna ten klucz
(zapytanie programu: `klucze_ramek`) - program odrzuca klucze nieznane; wersja 0.3.9-i1 go nie zna (POTRZEBUJE w raporcie E3-I1).
Krok 2 z `--python-z-paczki` sprawdza Pythona paczki, a na poczatku kroku 5 instalator kopiuje katalog `python/` paczki do
`<KATALOG>\python\<wersja>\` (`przygotuj_pythona`: pliki zgodne z sumami zostaja, brakujace i zmienione przez plik tymczasowy,
na koniec kontrola sum calej kopii; blad zapisu = kod 6) - od tej chwili srodowisko wersji powstaje z KOPII (nie z pendrive'a):

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
   pliki programu (kontrola sum), `python -m venv --copies --without-pip`, plik `stanowisko_bez_wmi.pth`, `ensurepip`
   (patrz "Srodowisko wersji bez zapytan WMI"), `pip install --isolated --no-index --only-binary=:all:
   --find-links kola -r zamrozone.txt`, porownanie `pip list` z lista zamrozona (n z n; `pip` zalozony przez `ensurepip` nie
   jest liczony), `instalacja.json`, zdjecie znacznika. Wersja juz zainstalowana z tej samej paczki i cala = bez zmian - od razu
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
   program\SUMY_PROGRAMU.sha256 [--bez-sieci]`; kod 1 albo 2 = wersja zostaje zainstalowana, ale NIE biezaca. Wynik to kod
   wyjscia ORAZ ostatni wiersz wyjscia (umowa A11s): kod 0 liczy sie tylko z ostatnim wierszem `SAMOKONTROLA: ZIELONA ...`,
   kod 1 tylko z `SAMOKONTROLA: CZERWONA ...`. Kod spoza umowy 0 / 1 / 2 (proces samokontroli zginal, np. `0xC0000005`) albo
   kod 0 / 1 bez takiego wiersza (np. blad importu modulu = kod 1 Pythona i sam slad wyjatku) = do 2 powtorzen po 3 s
   przerwy, kazde z wierszem `UWAGA samokontrola: ...` na ekranie i w dzienniku; trzeci taki wynik z rzedu = kod 2
   instalatora ("zakonczyla sie awaryjnie" / "nie podala wyniku") z rada "to nie blad ustawien, uruchom ponownie",
8. zapis skryptow ze wzorow i przelaczenie wskaznika (pod blokada programu); poprzednia wersja zapamietana,
9. ikony na pulpicie tylko z `/skrot` (E3-I1: "Stanowisko" i "Dzien skanera" - `pythonw.exe` interpretera bazowego wersji biezacej
   (`home` z `pyvenv.cfg`) + `<KATALOG>\start_bez_konsoli.pyw stanowisko|dzien_skanera`, bez okna konsoli; wersja bez startera:
   skrot do `.cmd`). Skrot zaklada PowerShell (`WScript.Shell`, wyjscie UTF-8); gdy sie nie uda - instalator sam zapisuje plik
   `.lnk` (`zapisz_lnk`, format MS-SHLLINK: lista ID powloki z `ILCreateFromPathW`, LinkInfo, napisy UTF-16). Wiersze
   `SKROT ZALOZONY: <nazwa> | <plik>` / `SKROT NIEUDANY: <nazwa> | <plik .cmd do klikniecia>` czyta okno; niepowodzenie nie
   zatrzymuje instalacji (ostrzezenie).

Wiersz koncowy: `INSTALACJA: GOTOWA - wersja biezaca X ...`; przy bledzie `BLAD: ...`, `CO ZROBIC: ...`,
`INSTALACJA: NIEUDANA (kod N) - wersja biezaca bez zmian: X` (gdy katalog wersji biezacej jest niekompletny po zamknieciu
okna w trakcie naprawy: `... - UWAGA: wersja biezaca X jest niekompletna ...`); bledy samego `zainstaluj.cmd` (kod 4,
brak instalatora): `INSTALACJA: NIEUDANA (kod N) - niczego nie zmieniono.` **Pierwsza instalacja** (nie ma jeszcze wersji
biezacej), gdy samokontrola daje kod 1 i WSZYSTKIE wiersze `BLAD <sprawdzenie>: ...` dotycza ustawien (`blad_ustawien`:
sprawdzenia `folder_*`, `operatorzy`, `ustawienia` - to, co technik wpisuje w `ustawienia.toml`): zasada "wersja biezaca
zawsze po zielonej samokontroli" zostaje, ale to zamierzony etap, nie niepowodzenie - wiersze `BLAD ...` samokontroli,
`Plik ustawien: <pelna sciezka>`, `CO ZROBIC: ...` i wiersz koncowy `INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml
i uruchom zainstaluj.cmd ponownie (kod 10)`. Ponowne `zainstaluj.cmd` tej samej paczki nie buduje srodowiska od nowa
(kilka sekund). Choc jeden blad spoza ustawien (`baza`, `moduly`, `pakiety`, `sumy`, `python`, `pula`, `dane_*`, `modele`,
kazde nieznane sprawdzenie) - takze przy pierwszej instalacji - to kod 1: `Bledy samokontroli wersji X (n):`, wiersze `BLAD`,
`BLAD: samokontrola ... zglosila bledy`, `CO ZROBIC:` z lista sprawdzen spoza ustawien, `INSTALACJA: NIEUDANA (kod 1)`.

| Kod | Znaczenie |
|---|---|
| 0 | wersja z paczki jest wersja biezaca |
| 1 | samokontrola czerwona (aktualizacja; pierwsza instalacja, gdy choc jeden blad nie dotyczy ustawien) - wersja zainstalowana, nie przelaczona |
| 2 | samokontroli nie dalo sie wykonac: kod 2 modulu, proces zginal w 3 probach albo kod 0 / 1 bez wiersza koncowego `SAMOKONTROLA:` - wersja zainstalowana, nie przelaczona |
| 3 | paczka: sumy, braki, blad wydania, inna budowa albo inna pisownia numeru wersji uzywanej |
| 4 | `zainstaluj.cmd`: brak Pythona 3.12 albo zla wersja; skrypty katalogu instalacji (`Stanowisko.cmd`, `Samokontrola.cmd`, `Wroc_do_poprzedniej.cmd`, `Wersje.cmd`, `Polecenie.cmd`, `Dzien_skanera.cmd`): nie ma gotowej wersji biezacej (brak wskaznika, brak srodowiska albo znacznik `NIEDOKONCZONA.txt`) - "uruchom zainstaluj.cmd z rozpakowanej paczki wydania" |
| 5 | program uruchomiony albo baza zajeta przez inny program (takze odmowa dostepu przy zamianie pliku bazy w powrocie i plik `-journal` obok bazy) |
| 6 | katalog, miejsce na dysku, venv, pip, przerwanie, baza nieczytelna / kopia bazy nieudana, druga instalacja naraz |
| 7 | ustawienia: blad pliku, BOM albo sciezki wzgledne w `[sciezki]` |
| 8 | powrot: baza nowsza niz poprzednia wersja - potrzebna zgoda `/przywroc-kopie` albo brak sprawdzonej kopii |
| 9 | brak wersji (powrot bez poprzedniej; usuwanie biezacej, poprzedniej albo nieistniejacej) |
| 10 | pierwsza instalacja WSTRZYMANA: wersja zainstalowana, wszystkie bledy samokontroli dotycza ustawien - czeka na uzupelnienie `ustawienia.toml` |
| 11 | powrot ANULOWANY: odpowiedz na pytanie T / N inna niz `T` / `t` (takze sam Enter, `tak`, brak konsoli) - nic nie zmieniono |

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
    `<baza>.nowy` -> `<baza>`. Plik bazy istnieje i jest caly w kazdej chwili; blad = baza bez zmian, kod 6 (odmowa
    dostepu przy samej zamianie pliku bazy albo niepusty `-journal` obok niej = inny program trzyma baze: kod 5).
  - Baza STARSZA niz schemat wersji docelowej ("powrot" do nowszej wersji, ktora zmigruje baze przy starcie): przed
    przelaczeniem powstaje kopia `<baza>_przed_<wersja>_...` - tak jak przy aktualizacji.
  - Bez roznicy schematu baza nie jest ruszana. Po przelaczeniu samokontrola wersji docelowej - informacyjnie.
- **Wersje** i kopie bazy nie sa kasowane automatycznie. `Wersje.cmd` wypisuje wersje (BIEZACA, poprzednia, NIEDOKONCZONA,
  OBCY KATALOG); `/usun WERSJA` usuwa katalog wersji zalozony przez instalator, ktora nie jest ani biezaca, ani
  poprzednia. Ustawien i danych nie dotyka.

## Python w paczce i okno instalatora (E3-I1)

Cel (decyzja wlasciciela 23.11 nr 6 i 25.11): laptop bez Pythona, osoba bez wiersza polecen - rozpakowana paczka, dwuklik
`Instaluj.cmd`, okno, ikony, program dziala; bez internetu, bez okna konsoli z pytaniami.

- **Droga Pythona: pakiet `python` 3.12.10 z nuget.org** (pelny, przenosny Python z PSF: `venv`, `ensurepip`, oryginalne podpisane
  pliki; bez instalatora MSI i bez zmian w systemie). Odrzucone: dystrybucja "embeddable" (nie ma `venv` - caly mechanizm wersji,
  powrotu i kol pip trzeba by przepisac), PyInstaller i inne pakowacze (niepodpisany `.exe` - antywirus / WDAC), instalator python.org
  (instaluje w systemie). Mechanizm wersji (venv + kola pip z paczki, powrot, kody) zostaje bez zmian.
- **Okno:** PySide6 z kol paczki - nuget nie ma `tkinter` (proba 25.11: brak `_tkinter.pyd` i `tcl`). Budowa wycina z kol
  `shiboken6` i `pyside6_essentials` (te same wersje co program) 37 plikow do `okno/`; okno startuje `pythonw.exe -I -B` Pythona
  paczki z `okno/` na `sys.path` (proba: platforma `windows`, styl `windows11`). Brak biblioteki = komunikat systemowy
  (`MessageBoxW`) z rada "zainstaluj.cmd", kod 4.
- **Kroki okna** (makieta `etap3/nowy_interfejs/makieta/Instalator.dc.html`): (1) Foldery - skany (wymagany, istniejacy), projekty
  (opcjonalny; pusty = `<KATALOG>/dane/projekty`), miejsce instalacji (domyslnie `C:\Stanowisko`; bledy: brak, sciezka wzgledna,
  brak dysku, plik zamiast folderu, srednik, OneDrive / SharePoint, za malo miejsca = pliki kol x 1,3 + program + 300 MB + Python);
  (2) Osoby - co najmniej 1, bez powtorzen (wielkosc liter), do 40 znakow, bez znakow sterujacych; (3) Instalacja - proces
  `instalator.py zainstaluj` (Python paczki, `-I -B -X utf8`, ukryta konsola `CREATE_NO_WINDOW` - venv, pip i samokontrola nie
  otwieraja okien), 9 krokow z wierszy `[n/9]`, blad = zdanie dla kodu (`napisy_instalatora.ZDANIA_KODOW`, kazdy kod 0-11) +
  `BLAD:` + `CO ZROBIC:` + plik dziennika, "Sprobuj ponownie"; (4) Gotowe - ikony (albo plik do klikniecia), "Uruchom program" /
  "Otworz Dzien skanera" (starter z kopii Pythona w katalogu instalacji, proces odlaczony - okno i pendrive mozna zamknac).
  Opcje instalatora z okna: `--python-z-paczki --skrot --bez-sieci --bez-pauzy` + foldery, osoby i `--ramki-wylaczone`.
- **Aktualizacja w oknie:** w miejscu instalacji jest `ustawienia.toml` = foldery i osoby pokazane z pliku, pola zablokowane,
  instalator dostaje tylko `--katalog` (ustawienia zostaja bajt w bajt). Instalacja 0.3.3 (Python systemu) aktualizuje sie tak samo:
  nowa wersja ma srodowisko z kopii Pythona paczki, stara zostaje przy swoim (powrot bez zmian).
- **Tryb bez okna** (testy; ta sama logika - `kreator.main_bez_okna`): `python\python.exe -I -B program\instalacja\okno_instalatora.py
  --bez-okna --folder-skanow X [--folder-projektow Y] [--katalog K] --osoba A [--osoba B] [--skrot-katalog D]`; kod = kod
  instalatora, blad wyboru = kod 12 (zdanie na ekranie, nic nie zmieniono). Zrzuty 4 krokow: `--zrzuty KATALOG`.
- **Starter ikon** `start_bez_konsoli.pyw <cel> [opcje]`: robi to, co `Stanowisko.cmd` / `Dzien_skanera.cmd` (wersja biezaca, jej
  venv, katalog programu, te same zmienne), program przez `python.exe` srodowiska z ukryta konsola, wyjscie do
  `dane\ostatni_start_<cel>.txt`; brak wersji (kod 4) albo blad programu (kod inny niz 0, a dla "stanowisko" takze inny niz 3) =
  okienko z komunikatem (`STANOWISKO_START_BEZ_OKIENEK=1` - na stderr, proby). Kod wyjscia = kod programu.

## Srodowisko wersji bez zapytan WMI (latka E3-A11w)

Przyczyna (raport `raporty/E3-A11w_2026-11-20.md`): modul `platform` Pythona 3.12 pyta WMI w osobnym watku systemowym; gdy
WMI nie odpowie w limicie, porzucony watek po ok. 5 s zamyka LOSOWY uchwyt procesu - proces potem zawisa albo pada
(zawieszenia testow silnika w srodowisku wersji, `0xc000070a`, `0xC0000005`). Pytaja m.in. `import trimesh` i `pip`.

Co robi instalator: srodowisko powstaje bez `pip` (`python -m venv --copies --without-pip`), potem instalator zapisuje
w `wersje\<wersja>\venv\Lib\site-packages` plik `stanowisko_bez_wmi.pth` (jeden wiersz: `import sys; sys.modules['_wmi'] =
None`), i dopiero potem zaklada `pip` (`python -I -m ensurepip --upgrade --default-pip` - to samo polecenie, ktore
wykonalby `venv`: kolo `pip` dolaczone do Pythona, bez sieci). Plik `.pth` wykonuje sie przy starcie KAZDEGO procesu
interpretera wersji (takze z `-I`), wiec zaden z nich - program, proces roboczy silnika, samokontrola, `pip`, pytest (T1),
narzedzia przez `Polecenie.cmd` - nie laduje `_wmi`, a `platform` bierze dane ze sciezek zapasowych (`platform.machine()`,
`system()`, `win32_ver()` dzialaja). Kontrole:

- po zalozeniu srodowiska interpreter wersji ma odpowiedziec `sys.modules.get('_wmi') is None`; inaczej stop (kod 6),
- plik jest sprawdzany przy KAZDYM `zainstaluj.cmd` (pierwsza instalacja, aktualizacja, naprawa, `/testy`, wersja juz
  zainstalowana) i przy `Wroc_do_poprzedniej.cmd`: brak albo inna tresc (wersja zalozona starszym instalatorem) = plik
  jest dokladany bez zakladania srodowiska od nowa, z wierszem `dolozono plik stanowisko_bez_wmi.pth` w dzienniku,
- pliku nie da sie zapisac: instalacja zatrzymuje sie kodem 6 z komunikatem (wersja nie zostaje przelaczona); powrot do
  poprzedniej wersji NIE jest zatrzymywany (operacja awaryjna) - zostaje `OSTRZEZENIE` na ekranie i w dzienniku,
- plik nie nalezy do zadnego pakietu, wiec `pip install` / `pip uninstall` go nie usuwa; nie lezy w katalogu programu,
  wiec nie wchodzi do `SUMY_PROGRAMU.sha256`.

Granice: plik chroni tylko procesy interpretera WERSJI. Procesy interpretera bazowego uruchamiane przez instalator
(`instalator.py`, `python -m venv`, zapytanie programu o schemat bazy) modulu `platform` nie wczytuja (proba z
`-X importtime`: 6 polecen, 0 wczytan). `narzedzia/zbuduj_wydanie.py --pobierz-kola` uruchamia `pip` interpretera bazowego
przez `PIP_BEZ_WMI` (blokada `_wmi` przed importem `pip`). Reczne `python -m pip ...` interpreterem bazowym chronione nie jest.

## Kryterium "dziala"

`testy/test_zbuduj_wydanie.py` (budowa: dwie budowy = ten sam ZIP, zawartosc, sumy, kola, tryb commita, numer wersji)
i `testy/test_instalacja.py` (instalacja, aktualizacja, powrot, bledy - na malej paczce w `tmp_path`; baza z przerwanym
zapisem, przerwane przywrocenie kopii, drugi powrot, cudze katalogi, pisownia numeru, przerwana naprawa; polecenia
`venv` / `ensurepip` / `pip` i kolejnosc "plik `.pth` przed pierwszym procesem srodowiska"; plik `.pth` w kazdej sciezce
instalacji i powrotu; jeden test z prawdziwym `python -m venv` i skryptami `.cmd` przy wrogim `PYTHONPATH` / `PYTHONHOME`,
ktory sprawdza tez `_wmi = None`, `platform.machine()` i `pip --version` w interpreterze wersji).
Proby na PC z pelna paczka i liczby: `raporty/E3-A11i_2026-11-20.md`.
E3-I1: `testy/test_instalacja_i1.py` (paczka z Pythonem i oknem, przypieta suma pakietu, ustawienia z okna, kopia Pythona,
starter, ikony przez PowerShell i zapis wlasny - z uruchomieniem skrotu) i `testy/test_okno_instalatora.py` (okno bez ekranu:
4 kroki, walidacje, zdanie dla kazdego kodu, aktualizacja, zrzuty; tryb bez okna z prawdziwa instalacja malej paczki).
Proby z pelna paczka (K1-K5): `raporty/E3-I1_2026-11-25.md`.

## Zalozenia i granice

- E3-I1: Python jest w paczce i trafia do `<KATALOG>\python\<wersja>`; paczka bez katalogu `python` (do 0.3.3)
  wymaga Pythona 3.12 w systemie (sprawdzona wersja 3.12.10). Instalator niczego nie instaluje w systemie i nie uzywa sieci.
- Srodowisko wersji wskazuje interpreter bazowy (`pyvenv.cfg`): wersje z paczki z Pythonem - kopie w katalogu instalacji (nie
  usuwac katalogu `python`); wersje zainstalowane Pythonem systemu - ten Python (odinstalowanie albo przeniesienie psuje te
  wersje - naprawa: ponowne `zainstaluj.cmd`). Katalogu instalacji nie przenosic (skrypty srodowiska maja
  wpisana sciezke).
- **Znane ograniczenie (a) - dane w katalogu wersji (do wydania 0.3.1 wlacznie).** `stanowisko/ui_test.py`
  (`dane/decyzje.csv`) i `stanowisko/dzien_skanera_rdzen.py` (sesje `dane/dzien_skanera/`) pisaly do
  `<katalog programu>/dane`, czyli w instalacji z paczki do katalogu WERSJI: te dane nie przechodza do nowej wersji i znikaja
  z `Wersje.cmd /usun`. Program "Stanowisko" (baza, wyniki, logi) tego nie dotyczyl. Poprawione w E3-O4 (21.11.2026):
  w instalacji sesje ida do `<KATALOG>\dane\dzien_skanera\` (`opisy_modulow/dzien_skanera.md`, "W instalacji z paczki
  wydania"), a decyzje okna testowego do `<KATALOG>\dane\decyzje.csv` (`ui_test.plik_decyzji_domyslny` - to samo
  rozpoznanie instalacji; okno testowe nie ma skrotu w instalacji i dalej wymaga `--ustawienia <KATALOG>\ustawienia.toml`;
  `narzedzia/import_decyzji.py` bez opcji `--plik` szuka pliku dalej w katalogu programu - w instalacji trzeba podac
  `--plik <KATALOG>\dane\decyzje.csv`). Sesje i decyzje zapisane przez 0.3.1 zostaja
  w `wersje\0.3.1\program\dane\` - nie sa przenoszone automatycznie; przed `Wersje.cmd /usun 0.3.1` trzeba je skopiowac recznie.
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
- Ikony na pulpicie zaleza od polityki komputera: PowerShell w trybie ograniczonym ma zapas (wlasny zapis `.lnk`); polityka, ktora
  zabrania zapisu na pulpicie albo uruchamiania programow z katalogu instalacji, zostaje - wtedy dwuklik `Stanowisko.cmd` (z konsola).
- E3-I1, ramki: instalator nie wylacza ramek w programie 0.3.9-i1 (program nie ma klucza `[ramki] wlaczone`; zmiana `ustawienia.py`,
  `indicate.py`, `samokontrola.py` i okna poza ta paczka). Samokontrola z okna idzie z `--bez-sieci` (bez proby polaczenia).
- E3-I1, nie sprawdzone bez laptopa (lista: `instrukcje/instalacja_i_aktualizacja.md` punkt 8): antywirus, znacznik pochodzenia pliku
  z sieci / SmartScreen, ikony przy ograniczonej polityce, WDAC / AppLocker dla Pythona z pendrive'a, skalowanie ekranu.
- `kola/` zawiera caly zestaw zaleznosci Open3D i PySide6 (m.in. PySide6 WebEngine 132 MB, plotly 10 MB, dash 9 MB - razem co najmniej ok. 160 MB), ktorych
  program nie importuje, ale ktorych wymaga pip przy instalacji przypietych wersji (decyzja: paczki nie odchudzamy).
