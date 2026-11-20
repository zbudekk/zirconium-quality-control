# instalacja - paczka wydania, instalacja, aktualizacja, powrot (E3-A11i, 20.11.2026; wariant B dystrybucji)

**Co robi.** Jedna paczka `Stanowisko_<wersja>.zip` (program + kola pip + instalator) instaluje program bez internetu do
katalogu wersji z wlasnym srodowiskiem wirtualnym; ustawienia i dane leza poza katalogiem wersji; aktualizacja i powrot
do poprzedniej wersji to jedno polecenie. Pliki: `narzedzia/zbuduj_wydanie.py` (budowa), `instalacja/instalator.py`
(logika, tylko biblioteka standardowa), `instalacja/zainstaluj.cmd`, `instalacja/wzory/*.cmd` (skrypty uruchamiajace),
`instalacja/zamrozone.txt` i `zamrozone_testy.txt` (wersje pakietow), `WERSJA` (numer wersji, jeden wiersz).
Instrukcja dla osoby instalujacej: `instrukcje/instalacja_i_aktualizacja.md`.

## Paczka wydania

```
python narzedzia/zbuduj_wydanie.py --wyjscie <PC-katalog>\wydania [--wersja X] [--kola KATALOG] [--rewizja COMMIT]
python narzedzia/zbuduj_wydanie.py --pobierz-kola --kola KATALOG [--python python.exe]      (jedyny krok z internetem)
```

| W paczce | Co |
|---|---|
| `zainstaluj.cmd`, `CZYTAJ.txt` | start instalacji, trzy zdania dla czlowieka |
| `program/` | `stanowisko/`, `modele_plytek/`, `narzedzia/` (bez `zbuduj_wydanie.*`), `ramka/` (importuje ja `stanowisko/ramka_protokol.py`), `instrukcje/`, `instalacja/`, `ustawienia.przyklad.toml`, `requirements.txt`, `WERSJA`; bez `testy/`, `raporty/`, `opisy_modulow/`, danych i `__pycache__` |
| `program/SUMY_PROGRAMU.sha256` | suma kazdego pliku programu, format `sha256sum` (umowa samokontroli A11s: `--sumy`) |
| `kola/` | kola binarne (Windows x64, Python 3.12) wszystkich pakietow z `zamrozone.txt`, takze zaleznosci posrednich |
| `kola_testy/` | pytest i jego zaleznosci (`zamrozone_testy.txt`) - instalowane tylko przez `zainstaluj.cmd /testy` |
| `wydanie.json` | wersja, commit, data commita, wersja Pythona, lista kol z sumami i rozmiarami |
| `SHA256SUMS` | suma kazdego pliku paczki; instalator sprawdza ja jako pierwszy krok |

- **Zrodlo plikow programu:** commit `HEAD` (tresc obiektow gita - zmiany niezacommitowane i pliki spoza gita nie wchodza,
  jest ostrzezenie). `--zrodlo KATALOG --data RRRR-MM-DDTGG:MM:SS [--commit OPIS]` bierze pliki z katalogu (proby).
- **Powtarzalnosc bajtowa:** ten sam commit + te same kola = ten sam SHA-256 ZIP (data wpisow = data commita UTC, staly
  porzadek i atrybuty, kola bez kompresji, reszta deflate 9, skrypty `.cmd` zawsze z CRLF). Granica: inna wersja biblioteki
  zlib (inny Python budujacy) moze dac inne bajty kompresji - budowac tym samym interpreterem.
- **Listy zamrozone** generuje `--pobierz-kola`: `pip freeze` interpretera, na ktorym przechodza testy, sluzy jako
  ograniczenia (`-c`); do `zamrozone.txt` trafia to, co pip dobiera dla `requirements.txt` bez pytest (73 pakiety), do
  `zamrozone_testy.txt` reszta potrzebna pytestowi (3). Z `pip freeze` odpadaja `pip` i pakiety spoza zaleznosci.
  Pobieranie: `pip download --only-binary=:all: --platform win_amd64 --python-version 3.12`; pakiet bez kola binarnego
  = blad (budowa nie kompiluje ze zrodel). Zmiana `requirements.txt` = ponowne `--pobierz-kola` (test pilnuje zgodnosci).
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
  wersje\<wersja>\program\      pliki z paczki; wersje\<wersja>\venv\ - srodowisko tej wersji
  wersje\<wersja>\instalacja.json, wydanie.json, pip.log;  NIEDOKONCZONA.txt = instalacja przerwana
```

Skrypty ustawiaja `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1` (katalog programu zostaje identyczny z paczka),
`PYTHONNOUSERSITE=1`, czyszcza `PYTHONPATH` i uruchamiaja `wersje\<biezaca>\venv\Scripts\python.exe` w katalogu programu.
`Stanowisko.cmd` dodaje `--ustawienia <KATALOG>\ustawienia.toml` i przekazuje argumenty (`--atrapa`, `--zamknij-po 5`);
`Polecenie.cmd <argumenty pythona>` to Python wersji biezacej (np. `Polecenie.cmd -m stanowisko.dzien_skanera`).

## zainstaluj.cmd [/katalog K] [/python P] [/skrot] [/testy] [/bez-sieci] [/bez-pauzy]

`zainstaluj.cmd` szuka Pythona 3.12 (opcja `/python`, zmienna `STANOWISKO_PYTHON`, `py -3.12`, typowe katalogi
`Python312`, `python` z PATH; wskazany wprost musi byc 3.12, inaczej stop) i uruchamia `instalator.py zainstaluj`:

1. sumy `SHA256SUMS` kazdego pliku paczki; niezgodnosc, brak `wydanie.json` albo modulu samokontroli = stop (kod 3),
2. Python: wersja z `wydanie.json` (3.12), 64 bity, modul `venv` (kod 4),
3. katalog instalacji: nie w folderze synchronizowanym, sciezki plikow pakietow do 259 znakow, prawo zapisu; sprzatanie
   katalogow wersji ze znacznikiem `NIEDOKONCZONA.txt`,
4. ustawienia: brak pliku = wzor z kazda wzgledna sciezka `[sciezki]` zamieniona na `<KATALOG>/dane/...`; plik istniejacy
   zostaje. Kod programu z paczki (`ustawienia.wczytaj_ustawienia`, `baza.sciezka_bazy`, `max(baza.MIGRACJE)`) odpowiada,
   gdzie jest baza i jaki schemat obsluguje wersja; blad pliku albo sciezka wzgledna w `[sciezki]` = stop (kod 7); program
   uruchomiony (plik `<baza>.blokada`, ten sam co `aplikacja.BlokadaStanowiska`) = stop (kod 5),
5. katalog wersji: miejsce na dysku (rozmiar kol po rozpakowaniu x 1,3 + program + 300 MB), znacznik, pliki programu
   (kontrola sum), `python -m venv --copies`, `pip install --no-index --only-binary=:all: --find-links kola -r zamrozone.txt`,
   porownanie `pip list` z lista zamrozona (n z n; `pip` zalozony przez venv nie jest liczony), `instalacja.json`,
   zdjecie znacznika. Wersja juz zainstalowana z tej samej paczki i cala = bez zmian (z `/testy` dokladany jest sam
   zestaw testowy: `--find-links kola --find-links kola_testy -r zamrozone_testy.txt`); uszkodzona = od nowa (miejsce
   na dysku sprawdzane przed usunieciem). Paczka o tym samym numerze wersji, ale innej tresci (inne sumy `wydanie.json`
   albo `SUMY_PROGRAMU.sha256` niz w `instalacja.json`) nie zastepuje wersji biezacej ani poprzedniej (kod 3) - nowe
   wydanie = nowy numer; wersje nieuzywana zastepuje,
6. kopia bazy `dane\kopie\<baza>_przed_<wersja>_<data>_<godzina>_v<schemat>.sqlite` (mechanizm kopii SQLite), gdy wersja
   inna niz biezaca i baza istnieje,
7. samokontrola nowej wersji: `python -m stanowisko.samokontrola --ustawienia <KATALOG>\ustawienia.toml --sumy
   program\SUMY_PROGRAMU.sha256 [--bez-sieci]`; kod 1 albo 2 = wersja zostaje zainstalowana, ale NIE biezaca,
8. zapis skryptow ze wzorow i przelaczenie wskaznika (pod blokada programu); poprzednia wersja zapamietana,
9. skrot na pulpicie tylko z `/skrot` (PowerShell `WScript.Shell`; niepowodzenie = ostrzezenie).

Kazdy blad: `BLAD: ...`, `CO ZROBIC: ...`, `INSTALACJA: NIEUDANA (kod N) - wersja biezaca bez zmian: X`.

| Kod | Znaczenie |
|---|---|
| 0 | wersja z paczki jest wersja biezaca |
| 1 / 2 | samokontrola: bledy / nie dalo sie wykonac - wersja zainstalowana, nie przelaczona |
| 3 | paczka: sumy, braki, blad wydania |
| 4 | brak Pythona 3.12 albo zla wersja |
| 5 | program uruchomiony |
| 6 | katalog, miejsce na dysku, venv, pip, przerwanie |
| 7 | ustawienia: blad pliku albo sciezki wzgledne w `[sciezki]` |
| 8 | powrot: baza nowsza niz poprzednia wersja - potrzebna zgoda `/przywroc-kopie` albo brak kopii |
| 9 | brak wersji (powrot bez poprzedniej; usuwanie biezacej, poprzedniej albo nieistniejacej) |

## Wroc_do_poprzedniej.cmd [/przywroc-kopie], Wersje.cmd [/usun WERSJA]

- **Powrot** przelacza wskaznik na wersje poprzednia (ponowny powrot wraca do nowszej). Przed przelaczeniem: kod
  poprzedniej wersji musi przyjac obecny `ustawienia.toml` (klucz dodany dla nowszej wersji = stop, kod 7), program musi
  byc zamkniety, a schemat bazy (`PRAGMA user_version`) nie moze byc nowszy niz obslugiwany przez poprzednia wersje.
  Baza nowsza: ostrzezenie z licznikami (ile wpisow w ktorych tabelach przybylo od kopii i z kiedy jest kopia) i stop z
  kodem 8; z `/przywroc-kopie` biezaca baza (z plikami `-wal`, `-shm`) jest odkladana jako
  `dane\kopie\<baza>_odlozona_v<schemat>_<czas>.sqlite`, a w jej miejsce wraca kopia sprzed aktualizacji (najpierw kopia
  instalatora sprzed wersji biezacej, potem inne kopie instalatora, na koncu kopie programu `<baza>.kopia_v*`).
  Bez zmiany schematu baza nie jest ruszana. Po przelaczeniu samokontrola poprzedniej wersji - informacyjnie.
- **Wersje** nie sa kasowane automatycznie. `Wersje.cmd` wypisuje je (BIEZACA, poprzednia, NIEDOKONCZONA);
  `/usun WERSJA` usuwa katalog wersji, ktora nie jest ani biezaca, ani poprzednia. Ustawien i danych nie dotyka.

## Kryterium "dziala"

`testy/test_zbuduj_wydanie.py` (budowa: dwie budowy = ten sam ZIP, zawartosc, sumy, kola, tryb commita) i
`testy/test_instalacja.py` (instalacja, aktualizacja, powrot, bledy - na malej paczce w `tmp_path`, jeden test z prawdziwym
`python -m venv` i skryptami `.cmd`). Proby na PC z pelna paczka i liczby: `raporty/E3-A11i_2026-11-20.md`.

## Zalozenia i granice

- Python 3.12 instaluje sie raz recznie; instalator niczego nie instaluje w systemie i nie uzywa sieci.
- Srodowisko wersji wskazuje interpreter bazowy (`pyvenv.cfg`): odinstalowanie albo przeniesienie Pythona 3.12 psuje
  wszystkie wersje - naprawa: ponowne `zainstaluj.cmd` po usunieciu katalogu wersji. Katalogu instalacji nie przenosic.
- Dane poza katalogiem wersji trzyma wylacznie `ustawienia.toml` ze sciezkami bezwzglednymi. Przyszly klucz `[sciezki]`
  z wartoscia domyslna `dane/...`, ktorego nie ma w istniejacym pliku, zatrzyma aktualizacje (kod 7) z gotowym wierszem
  do wpisania - instalator pliku ustawien nie zmienia.
- Moduly spoza programu "Stanowisko", ktore pisza do `<katalog programu>/dane` na stale (`dzien_skanera`: sesje,
  `ui_test`: `decyzje.csv`), w instalacji z paczki pisza do katalogu wersji - te dane nie przechodza do nowej wersji.
- Starsza wersja programu odrzuca nieznane klucze ustawien: po recznym dopisaniu klucza nowej wersji powrot wymaga
  jego usuniecia (instalator to wykrywa przed przelaczeniem).
- Powtorzona proba instalacji wersji, ktora nie przeszla samokontroli, robi kolejna kopie bazy tylko wtedy, gdy baza sie
  zmienila. Kopie i odlozone bazy nie sa kasowane.
- Skrot na pulpicie zalezy od polityki komputera (PowerShell w trybie ograniczonym nie zalozy skrotu) - wtedy dwuklik
  `Stanowisko.cmd`. Na laptopie firmowym nie sprawdzono (plan etapu 3, sekcja 12.1, poz. 14).
- `kola/` zawiera caly zestaw zaleznosci Open3D i PySide6 (m.in. PySide6 WebEngine 132 MB, plotly 10 MB, dash 9 MB - razem co najmniej ok. 160 MB), ktorych
  program nie importuje, ale ktorych wymaga pip przy instalacji przypietych wersji.
