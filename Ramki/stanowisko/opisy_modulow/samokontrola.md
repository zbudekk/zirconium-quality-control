# samokontrola - czy program ma na tym komputerze wszystko, czego potrzebuje (E3-A11s, 20.11.2026, runda 2 po recenzji PR #38)

**Co robi.** Jedno polecenie sprawdza srodowisko (Python, pakiety, moduly z DLL), plik ustawien, foldery pracy, folder
danych, baze, modele plytek, pule projektow, ramki, Excel, drugi egzemplarz programu i sumy plikow programu. Wynik: jeden
wiersz na sprawdzenie i wiersz podsumowania "ZIELONA" / "CZERWONA". Wywoluje ja instalator (A11i) po instalacji i przed
przelaczeniem wersji, technik przez `Samokontrola.cmd`, a program moze ja wywolac jako funkcje. **Niczego nie naprawia
i nie zmienia.** Plik: `stanowisko/samokontrola.py`; tylko biblioteka standardowa i moduly programu.

## Umowa wywolania (styk z A11i i A11d - nie zmieniac bez uzgodnienia)

```
python -m stanowisko.samokontrola [--ustawienia PLIK] [--sumy PLIK] [--json] [--bez-sieci]
```

- Wiersz sprawdzenia: `OK <kod>: <opis>` albo `OSTRZEZENIE <kod>: <opis>; <co zrobic>` albo `BLAD <kod>: <opis>; <co zrobic>`.
  Opis nigdy nie zawiera srednika (srednik w sciezce jest zamieniany na przecinek), wiec pierwszy "; " w wierszu oddziela
  opis od rady. Kody sa stale, z malych liter, cyfr i podkreslnika; kolejnosc wierszy jest stala (tabela nizej, 21 wierszy).
- Ostatni wiersz: `SAMOKONTROLA: ZIELONA (ok N, ostrzezenia M)` przy 0 bledow, `SAMOKONTROLA: CZERWONA (ok N,
  ostrzezenia M, bledy K)` gdy sa bledy.
- Kod wyjscia: 0 = brak bledow (takze z ostrzezeniami), 1 = co najmniej jeden BLAD, 2 = samokontroli nie dalo sie wykonac.
- Kod 2 (brak pliku ustawien, blad skladni albo walidacji ustawien, plik nie w UTF-8 albo z BOM, nieznana opcja polecenia):
  na wyjsciu jeden wiersz `BLAD ustawienia: <opis>; <co zrobic>` i `SAMOKONTROLA: NIEWYKONANA (blad ustawien - zadnego
  sprawdzenia nie wykonano)`, bez sladu wyjatku. Opis to komunikat modulu `ustawienia` (nazwa pliku, sekcja, klucz) bez
  polskich znakow i BEZ wartosci wpisanej w pliku - wyjatki: wartosci z `[sciezki]` i `[plytki]` (sciezki glowne) oraz
  liczby; w pozostalych przypadkach zamiast wartosci jest `(wartosci nie pokazano)` albo `jest wartosc typu str` (w
  `[sesja] operatorzy` sa nazwy osob). Plik zapisany w Notatniku jako ANSI albo "Unicode": `plik ustawien nie jest zapisany
  w kodowaniu UTF-8`; jako "UTF-8 z BOM": `plik ustawien zaczyna sie od znacznika BOM`. Nieznana opcja: komunikat
  `argparse` na wyjsciu bledow.
- `--json`: jeden obiekt JSON (ASCII): `samokontrola` (ZIELONA / CZERWONA / NIEWYKONANA), `kod_wyjscia`, `ok`,
  `ostrzezenia`, `bledy`, `podsumowanie` (ostatni wiersz wyjscia tekstowego), `czas_s`, `sprawdzenia` = lista obiektow
  `{kod, poziom, opis, rada}` w tej samej kolejnosci i z tymi samymi tekstami, co wyjscie tekstowe.
- `--sumy PLIK`: plik w formacie `sha256sum` (`<64 znaki hex>  <sciezka wzgledna od katalogu programu>`; dopuszczone `*`
  przed sciezka, konce linii CRLF, ukosniki w obie strony). Bez opcji: sprawdzany jest `SUMY_PROGRAMU.sha256` z katalogu
  programu, a gdy go nie ma - OSTRZEZENIE "kopia robocza bez pliku sum". Opcja wskazujaca plik, ktorego nie ma = BLAD `sumy`.
- `--bez-sieci`: bez proby polaczenia z ramkami (oba wiersze ramek = OSTRZEZENIE "pominieto").
- E3-R1: `[ramki] wlaczone = false` - bez proby polaczenia (takze bez `--bez-sieci`), oba wiersze ramek = OK "ramki wylaczone
  w ustawieniach" z podpowiedzia, jak je wlaczyc (wiersz neutralny: nie OSTRZEZENIE, nie BLAD; format wierszy bez zmian).
- `--ustawienia PLIK`: domyslnie `ustawienia.toml` w katalogu programu (jak program).

**API.** `samokontrola.wykonaj(ust, *, plik_ustawien=None, sumy=None, bez_sieci=False, korzen=None, limit_ramki_s=None)
-> Wynik`. `ust` = wynik `ustawienia.wczytaj_ustawienia`; `plik_ustawien` potrzebny tylko do listy kluczy domyslnych;
`korzen` = katalog programu (domyslnie ten, z ktorego dziala modul). `Wynik`: `sprawdzenia` (lista `Sprawdzenie` z polami
`kod`, `poziom`, `opis`, `rada`; `wiersz()`), `sprawdzenie(kod)`, `ok`, `ostrzezenia`, `bledy`, `zielona`, `kod_wyjscia`,
`podsumowanie()`, `wiersze()`, `tekst()`, `do_slownika()`, `czas_s`; mozna po nim iterowac. `rada` jest pusta dokladnie
wtedy, gdy poziom to `OK`. `wykonaj` nie rzuca wyjatku z powodu stanu komputera i nie wisi: sprawdzenie przerwane bledem
ma poziom BLAD ("sprawdzenie przerwane bledem programu"), sprawdzenie niezakonczone w swoim limicie czasu - BLAD
("sprawdzenie nie zakonczylo sie w N s"; ramki i Excel: OSTRZEZENIE), a pozostale sa wykonywane. Stale: `KODY` (kolejnosc
wierszy), `OK`, `OSTRZEZENIE`, `BLAD`, `PLIK_SUM`. Uwaga dla ekranu: wywolanie trwa do kilku sekund (ramki, foldery
sieciowe) - wolac poza watkiem okna; kazde sprawdzenie dziala w watku pomocniczym, a watek, ktory nie skonczyl w limicie
(dysk sieciowy bez odpowiedzi), zostaje w tle do konca procesu.

## Sprawdzenia

| Nr | Kod | Co sprawdza | OSTRZEZENIE, gdy | BLAD, gdy |
|---|---|---|---|---|
| 1 | `python` | wersja Pythona 3.12 | - | inna wersja niz 3.12 |
| 2 | `pakiety` | wersje pakietow z `requirements.txt` (metadane, bez importu); `pytest` pomijany | inna wersja niz przypieta (lista `nazwa jest (wymagana x)`); brak pakietu dodatkowego: `pywin32`, `rtree`, `beautifulsoup4`, `pypdf`; brak `requirements.txt` w katalogu programu | brak pakietu potrzebnego w pracy: `numpy`, `scipy`, `trimesh`, `pillow`, `open3d`, `PySide6`, `watchdog` |
| 3 | `moduly` | import modulow z DLL ta sama funkcja i lista, co start programu (`aplikacja.zaladuj_moduly_dll`: Qt, `MODULY_DLL`, `MODULY_DLL_PULI`, `stanowisko.porownaj`) | nie laduje sie tylko `pythoncom` / `win32com.client` (bez Excela) | nie laduje sie jakikolwiek inny modul |
| 4 | `ustawienia` | plik wczytany i poprawny; lista kluczy uzupelnionych wartoscia domyslna (informacja) | - | (kod wyjscia 2: brak albo blad pliku) |
| 5 | `operatorzy` | `[sesja] operatorzy` niepusta (podaje tylko liczbe osob) | lista pusta: program nie zapisuje decyzji | - |
| 6 | `folder_skanera` | `[sciezki] folder_eksportu_skanera` istnieje i daje sie czytac | - | brak, nie folder, nieczytelny, brak odpowiedzi w 5 s |
| 7 | `folder_cyrkon` | `[sciezki] folder_cyrkon`, jak wyzej | jak obok, gdy program z tego folderu nie korzysta: `pula_wpisow = false` i folder puli wybrany w programie (wtedy BLAD jest w wierszu `pula`) | brak, nie folder, nieczytelny, brak odpowiedzi w 5 s - gdy program z niego korzysta |
| 8 | `folder_prywatne` | `[sciezki] folder_prywatne`, jak wyzej | jak wyzej (zawsze tylko ostrzezenie) | - |
| 9 | `folder_millbox` | `[sciezki] folder_millbox`, jak wyzej | jak wyzej (zawsze tylko ostrzezenie; przy `pula_wpisow = true` rada: "skany beda czekac na wspolczynnik") | - |
| 10 | `dane_folder` | folder danych (= folder pliku bazy) istnieje i przyjmuje zapis pliku probnego | folderu nie ma, ale da sie go utworzyc ("zostanie zalozony przy pierwszym starcie", zapisu nie sprawdzono) | zapis pliku probnego nieudany (np. brak prawa zapisu); na sciezce lezy plik albo folder nadrzedny jest tylko do odczytu; folder danych nie odpowiada w 5 s |
| 11 | `dane_miejsce` | wolne miejsce na dysku folderu danych | ponizej 10 GB | ponizej 1 GB |
| 12 | `dane_polozenie` | sciezki danych z `[sciezki]` (`baza`, `log_excel`, `wyniki`, `podglady`, `pula_cache`, `logi`, `kalibracja_ramek`) poza folderami synchronizowanymi | sciezka ma katalog o nazwie jak OneDrive / SharePoint, ale system nie zna go jako synchronizowanego (rozpoznanie tylko po nazwie); folder danych w katalogu programu zainstalowanego z paczki (obok lezy `SUMY_PROGRAMU.sha256`): aktualizacja "zgubi" baze | ktorakolwiek sciezka w folderze, ktory system zna jako synchronizowany: zmienna srodowiska `OneDrive*` albo wpis OneDrive w rejestrze uzytkownika |
| 13 | `baza` | plik bazy otwierany tylko do odczytu: wersja schematu wobec programu, `PRAGMA quick_check` | brak pliku albo plik pusty ("zostanie zalozona przy pierwszym starcie"); wersja starsza ("migracja z kopia przy starcie"); baza zajeta; niedokonczony zapis (plik `-journal`); `quick_check` nie zmiescil sie w 4 s; baza w trybie WAL (nie jest otwierana) | wersja nowsza niz program; plik nie jest baza albo jest uszkodzony (tylko wtedy rada o kopii); `quick_check` zglasza problemy; pliku nie da sie otworzyc (zajety przez inny program albo brak dostepu - rada bez przywracania kopii) |
| 14 | `modele` | kazdy uklad z `[plytki]`: katalog, `uklad.json` poprawny wg `uklad.wczytaj`, co najmniej jeden `plytka_n<numer>.stl`; do tego (E3-O3) kazdy uklad dostarczany z programem (`ustawienia.UKLADY_WBUDOWANE` - 10 ukladow: kwadratowe i okragle testowe R59 i R54 oraz okragle ramkowe `okragla_ramkowa_wieczorna` / `okragla_ramkowa_poranna`), ktorego w `[plytki]` nie ma - program dopisuje taki uklad sam, gdy jego katalog z `uklad.json` istnieje, wiec jego brak w ustawieniach = brak modelu w katalogu programu. Program kompletny: `poprawne 10 z 10` (wiecej, gdy w `[plytki]` sa uklady wlasne) | - | ktorykolwiek uklad wadliwy (lista `nazwa: wada`); brak modelu ukladu dostarczanego z programem, np. `poprawne 8 z 10 - okragla_ramkowa_wieczorna: brak katalogu modelu dostarczanego z programem (modele_plytek/okragla_ramkowa_wieczorna), ...` - takze przy starym pliku ustawien bez wierszy ukladow ramkowych (przed E3-O3 bylo wtedy `poprawne 8 z 8` i samokontrola zielona) |
| 15 | `pula` | stan puli wg `[silnik] pula_wpisow` - licznikami; przy `pula_wpisow = false` folder, z ktorego program naprawde bierze pule (wybor w programie ma pierwszenstwo przed `folder_cyrkon`) | pula pusta (0 plikow STL); `folder_cyrkon` niedostepny (BLAD jest wtedy w wierszu `folder_cyrkon`); przy puli per praca: brak bazy, 0 projektow w indeksie, brak `wspolczynniki.csv` | folder puli wybrany w programie niedostepny albo nieustawiony (pula pusta, skany czekaja); pliku wyboru puli `stanowisko_pula.json` program nie umie wczytac (program nie wystartuje) |
| 16 | `pamiec_puli` | `[sciezki] pula_cache` / `projekty`: liczba wpisow i rozmiar | sciezka jest plikiem, nie folderem | - |
| 17 | `ramka_wieczorna` | `GET /stan` pod `[ramki] wieczorna_host`:`port`, limit 3 s | ramka nieobecna, brak odpowiedzi w limicie, zly klucz (401), inna rola, inny program, blad sprzetu ramki, `--bez-sieci` | - |
| 18 | `ramka_poranna` | to samo dla `poranna_host` | jak wyzej | - |
| 19 | `excel` | pywin32 i uruchomiony Excel - ta sama droga, co `excel_com.polacz` (`GetActiveObject`), bez otwierania arkusza; uwagi `excel.Konfiguracja.z_ustawien` | brak pywin32; Excel nieuruchomiony; uwaga do ustawien `[excel]` / `log_excel` | - |
| 20 | `egzemplarz` | czy program dziala teraz na tej bazie (blokada `<baza>.blokada`) i czy baza byla zajeta | program uruchomiony; baza zajeta przez inny program (to informacja, kod wyjscia zostaje 0) | - |
| 21 | `sumy` | sumy SHA-256 plikow programu z listy; pliki nadmiarowe (bez `Thumbs.db` i `desktop.ini`) | brak pliku sum w katalogu programu ("kopia robocza bez pliku sum") | plik zmieniony, brakujacy, nieczytelny albo nadmiarowy (pierwszych 10 roznic + liczba kolejnych); zly albo brakujacy plik sum |

Kazdy wiersz moze dodatkowo miec poziom BLAD z opisem `sprawdzenie przerwane bledem programu (...)` (nieprzewidziany blad
w sprawdzeniu) albo `sprawdzenie nie zakonczylo sie w N s - samokontrola nie czekala dluzej` (limit czasu sprawdzenia:
30 s, `moduly` 120 s, `excel` 10 s); wiersze `ramka_wieczorna`, `ramka_poranna` i `excel` maja po limicie OSTRZEZENIE.
Gdy folder danych nie odpowiada w 5 s: `dane_folder` = BLAD, a `dane_miejsce`, `baza`, `pula`, `pamiec_puli`, `egzemplarz` =
OSTRZEZENIE `nie sprawdzono - folder danych nie odpowiada (wiersz dane_folder)`.

Zmiany rundy 2 wobec rundy 1 (dla instrukcji A11d): `folder_millbox` nigdy nie jest BLAD; `folder_cyrkon` bywa OSTRZEZENIE;
`pula` bywa BLAD; `dane_polozenie` po samej nazwie katalogu = OSTRZEZENIE; `baza` ma nowy BLAD "pliku bazy nie da sie
otworzyc" i nowe OSTRZEZENIE "baza w trybie zapisu WAL"; rady wierszy `folder_*` podaja plik ustawien i klucz; kod 2 ma dwa
nowe opisy (UTF-8, BOM) i nie pokazuje wartosci z pliku. Liczba i kolejnosc wierszy (21) oraz kody bez zmian.

Poczatki opisow, ktore instrukcja moze cytowac (reszta opisu to sciezka z ustawien albo liczby):

| Kod | Poziom | Opis zaczyna sie od | Rada |
|---|---|---|---|
| `python` | BLAD | `program uruchomiony Pythonem` | `zainstaluj Python 3.12 i zainstaluj program ponownie z paczki wydania` |
| `pakiety` | BLAD | `wersje pakietow zgodne N z M z requirements.txt - brak <pakiet>` | `zainstaluj program ponownie z paczki wydania (pakiety instaluje instalator, bez internetu)` |
| `moduly` | BLAD | `moduly programu z bibliotekami DLL: zaladowane N z M - nie laduja sie:` | `zainstaluj program ponownie z paczki wydania, gdy blad wraca - zglos ten wiersz osobie, ktora instaluje program` |
| `ustawienia` | BLAD (kod 2) | `brak pliku ustawien:` / `plik ustawien niepoprawny -` | `skopiuj ustawienia.przyklad.toml jako ustawienia.toml i uzupelnij sciezki albo podaj plik w --ustawienia` / `popraw plik ustawien (wzor: ustawienia.przyklad.toml) albo podaj wlasciwy plik w --ustawienia` |
| `ustawienia` | BLAD (kod 2) | `plik ustawien nie jest zapisany w kodowaniu UTF-8:` | `zapisz plik w kodowaniu UTF-8 (Notatnik: Plik - Zapisz jako - Kodowanie: UTF-8) i uruchom samokontrole ponownie` |
| `ustawienia` | BLAD (kod 2) | `plik ustawien zaczyna sie od znacznika BOM (zapisany jako UTF-8 z BOM):` | `zapisz plik w kodowaniu UTF-8 bez BOM (Notatnik: Plik - Zapisz jako - Kodowanie: UTF-8, nie UTF-8 z BOM) i uruchom samokontrole ponownie` |
| `operatorzy` | OSTRZEZENIE | `lista osob jest pusta` | `wpisz osoby w pliku ustawien: [sesja] operatorzy = ["...", "..."]` |
| `folder_skanera`, `folder_cyrkon`, `folder_prywatne`, `folder_millbox` | BLAD / OSTRZEZENIE | `brak folderu` / `sciezka folderu ... nie jest folderem` / `folderu ... nie da sie czytac` / `folder ... nie odpowiada w 5 s` | `otworz plik ustawien <plik> i popraw klucz [sciezki] <klucz> (wiersz <klucz> = "...", sciezka z ukosnikami /) albo utworz / podlacz ten folder`; `<plik>` = pelna sciezka pliku ustawien, `<klucz>` = `folder_eksportu_skanera`, `folder_cyrkon`, `folder_prywatne`, `folder_millbox` |
| `folder_cyrkon` | OSTRZEZENIE | `brak folderu projektow Cyrkon: <sciezka> - program korzysta z folderu puli wybranego w programie (wiersz pula), a nie z tego folderu` | jak wyzej |
| `folder_millbox` | OSTRZEZENIE (przy `pula_wpisow = true`) | `brak folderu MillBox: <sciezka> - bez pliku wspolczynniki.csv pula wieczorna nie dostaje nowych prac` | `wlacz komputer z folderem MillBox albo podlacz ten folder - do tego czasu skany beda czekac na wspolczynnik, albo otworz plik ustawien <plik> i popraw klucz [sciezki] folder_millbox (...)` |
| `dane_folder` | BLAD | `w folderze danych nie udal sie zapis pliku probnego` / `folderu danych nie da sie utworzyc` / `folder danych nie odpowiada w 5 s` | `nadaj prawo zapisu do folderu danych albo popraw [sciezki] baza w pliku ustawien` / `podlacz dysk folderu danych albo popraw [sciezki] baza w pliku ustawien` |
| `dane_folder` | OSTRZEZENIE | `folder danych nie istnieje - zostanie zalozony przy pierwszym starcie programu` | `nic nie rob - po pierwszym uruchomieniu programu uruchom samokontrole jeszcze raz` |
| `dane_miejsce` | BLAD / OSTRZEZENIE | `wolne miejsce na dysku folderu danych: X GB` | `zwolnij miejsce na dysku - ...` |
| `dane_polozenie` | BLAD | `dane programu leza w folderze synchronizowanym OneDrive / SharePoint:` | `przenies dane poza folder synchronizowany i popraw te sciezki w pliku ustawien - ...` |
| `dane_polozenie` | OSTRZEZENIE | `sciezka danych programu ma katalog o nazwie jak folder OneDrive / SharePoint - rozpoznano tylko po nazwie, synchronizacji nie potwierdzono:` | `sprawdz, czy ten katalog jest synchronizowany (ikona chmury w Eksploratorze): jesli tak - przenies dane poza niego i popraw te sciezki w pliku ustawien (synchronizacja uszkadza plik bazy), jesli nie - nic nie rob` |
| `baza` | OSTRZEZENIE | `brak pliku bazy - zostanie zalozona przy pierwszym starcie programu` | `nic nie rob - baza powstanie sama przy pierwszym uruchomieniu programu` |
| `baza` | OSTRZEZENIE | `baza starsza niz program: wersja schematu N, program ma M - migracja z kopia przy starcie programu` | `nic nie rob - program przy starcie sam zrobi kopie pliku bazy i ja zaktualizuje` |
| `baza` | OSTRZEZENIE | `baza ma niedokonczony zapis po przerwanej pracy` | `uruchom program, zamknij go i uruchom samokontrole ponownie - pliku z koncowka -journal nie usuwaj i nie kopiuj bazy bez niego` |
| `baza` | BLAD | `baza nowsza niz program: wersja schematu N` | `zainstaluj wersje programu, ktora zalozyla te baze, albo nowsza - nie uruchamiaj na niej starszego programu` |
| `baza` | BLAD | `plik nie jest baza SQLite albo jest uszkodzony (SQLITE_NOTADB / SQLITE_CORRUPT)` / `baza uszkodzona: quick_check` | `zamknij program i przywroc baze z kopii (plik kopii obok bazy albo kopia zrobiona przez instalator) - samokontrola bazy nie naprawia, ...` |
| `baza` | BLAD | `pliku bazy nie da sie otworzyc (<powod>: zajety przez inny program albo brak dostepu) - pliku nie zmieniono:` | `zamknij program, ktory trzyma plik bazy (archiwizacja dysku, antywirus, przegladarka bazy), sprawdz dostep do folderu danych i uruchom samokontrole ponownie - to nie jest uszkodzenie bazy, pliku bazy niczym nie zastepuj` |
| `baza` | OSTRZEZENIE | `baza w trybie zapisu WAL (program go nie ustawia - przestawil ja inny program, np. przegladarka bazy)` | `to nie blad - program pracuje na takiej bazie, a samokontrola jej nie otwiera, zeby nie tworzyc obok plikow -shm i -wal` |
| `modele` | BLAD | `uklady plytek z [plytki]: poprawne N z M -` | `zainstaluj program ponownie z paczki wydania (katalog modele_plytek) albo popraw [plytki] w pliku ustawien` |
| `pula` | OSTRZEZENIE | `pula z jednego folderu (pula_wpisow = false): 0 plikow STL` / `pula per praca (pula_wpisow = true):` | `skopiuj projekty STL do folderu puli i uzyj w programie Odswiez pule - bez projektow skany czekaja` (i podobne) |
| `pula` | BLAD | `pula z jednego folderu (pula_wpisow = false): folder wybrany w programie niedostepny - pula pusta, skany czekaja bez wyniku` | `podlacz ten folder albo wskaz w programie inny folder puli projektow` |
| `pula` | BLAD | `pula z jednego folderu (pula_wpisow = false): folder puli nie jest ustawiony w programie - pula pusta, skany czekaja bez wyniku` | `wskaz w programie folder puli projektow` |
| `pula` | BLAD | `pliku wyboru puli stanowisko_pula.json w folderze danych program nie umie wczytac (<typ bledu>) - program nie wystartuje` | `usun plik stanowisko_pula.json z folderu danych i po uruchomieniu programu wskaz folder puli projektow ponownie, zglos ten wiersz osobie, ktora instaluje program` |
| kazdy | BLAD (ramki, Excel: OSTRZEZENIE) | `sprawdzenie nie zakonczylo sie w N s - samokontrola nie czekala dluzej` | `uruchom samokontrole ponownie, a gdy ten wiersz wraca - zglos ten wiersz osobie, ktora instaluje program`; ramki i Excel: `to nie blad - bez ramek i bez Excela program dziala, uruchom samokontrole ponownie (Excel: zakoncz edycje komorki i zamknij okna dialogowe)` |
| `ramka_wieczorna`, `ramka_poranna` | OSTRZEZENIE | `ramka wieczorna nieobecna:` / `proby polaczenia z ramka ... nie bylo - pominieto (--bez-sieci)` / `... odrzuca klucz laptopa` / `... odpowiada ramka o innej roli` | `wlacz ramke, sprawdz Wi-Fi i [ramki] <klucz hosta> w pliku ustawien, bez ramek program dziala - rozkladanie wedlug podpisow na ekranie`; przy pominietej probie: `gdy ramka jest wlaczona, uruchom samokontrole bez --bez-sieci, bez ramek program dziala - ...` |
| `excel` | OSTRZEZENIE | `Excel nie jest uruchomiony w tej sesji uzytkownika` / `brak pakietu pywin32` | `przed poranna praca otworz plik zlecen w Excelu na tym laptopie (z Autozapisem), bez Excela program dziala - zlecenia odhacza sie wtedy recznie` |
| `egzemplarz` | OSTRZEZENIE | `program Stanowisko jest teraz uruchomiony na tej bazie` | `to nie blad - przed aktualizacja programu albo powrotem do poprzedniej wersji zamknij program` |
| `sumy` | OSTRZEZENIE | `kopia robocza bez pliku sum` | `na stanowisku instaluj program z paczki wydania - w kopii roboczej programisty to nie blad` |
| `sumy` | BLAD | `sumy SHA-256 plikow programu zgodne N z M (...) - roznice: zmieniony <plik>, brak <plik>, nadmiarowy <plik>` | `zainstaluj program ponownie z paczki wydania - katalog programu rozni sie od wydania (pliki zmienione, brakujace albo nadmiarowe)` |

## Foldery pracy: ktory brak zatrzymuje prace

Program nie konczy sie przy braku zadnego z czterech folderow (kryterium T7 planu etapu 3: komunikat i dalsza praca).
Samokontrola pyta o co innego: czy po starcie da sie pracowac. Ustalenie z kodu programu i z PW zal. F:

| Folder | Poziom braku | Dlaczego |
|---|---|---|
| eksport skanera | BLAD | `scanner` nie ma czego obserwowac, program pokazuje komunikat `folder_skanera_niedostepny` (w `statusy.py` poziom blad) i zaden skan nie trafia do analizy. PW zal. F: "Skan nie pojawia sie w programie - sprawdzic folder eksportu". |
| Cyrkon | BLAD, gdy program z niego korzysta; OSTRZEZENIE, gdy nie korzysta | pula projektow: `Aplikacja._policz_pule` przy braku folderu daje pule niedostepna i kazdy skan czeka (`pula_brak_folderu`, poziom blad); przy puli per praca `indeks` zglasza "brak katalogu" i pula jest pusta. PW zal. F: "Wszystkie gniazda szare (brak projektow)". Przy `pula_wpisow = false` program bierze jednak pule z folderu WYBRANEGO W PROGRAMIE, jesli technik go wskazal (plik `stanowisko_pula.json` obok bazy, `Aplikacja._wczytaj_pule`) - wtedy `[sciezki] folder_cyrkon` nie jest w ogole czytany, jego brak to OSTRZEZENIE, a BLAD dotyczy folderu wybranego (wiersz `pula`). |
| Prywatne | OSTRZEZENIE | czytany tylko przy `pula_wpisow = true` (`indeks.zrodla_z_ustawien`); bez niego do puli nie wchodza tylko prace prywatne, reszta pracy idzie normalnie. |
| MillBox | OSTRZEZENIE (zawsze) | czytany tylko przy puli per praca: w nim lezy `wspolczynniki.csv`, z ktorego pochodza wiersze puli wieczornej (`pula.pula_wieczorna` = wiersze `frezowania`); bez folderu pula wieczorna nie dostaje nowych prac i skany czekaja na wspolczynnik. Decyzja koordynatora po recenzji PR #38: mimo to OSTRZEZENIE takze przy `pula_wpisow = true` - folder bywa udzialem komputera frezarki, a wylaczony komputer frezarki nie moze blokowac aktualizacji programu (instalator przelacza wersje tylko przy kodzie 0). Przy `pula_wpisow = false` program z folderu nie korzysta. |

**Folder puli faktycznie uzywany (B1 z recenzji PR #38).** Samokontrola ustala go ta sama droga, co program: wywoluje metode
programu `Aplikacja._wczytaj_pule` na obiekcie zastepczym (folder danych, folder domyslny z `[sciezki] folder_cyrkon`), bez
kopiowania jej logiki - takze czesciowo bledny plik wyboru daje ten sam folder, co w programie (test porownuje z prawdziwym
`Aplikacja(ust)` dla 13 tresci pliku). Wynik w wierszu `pula`: folder wybrany niedostepny albo nieustawiony = BLAD (bez
sciezki - moze zawierac nazwe zlecenia); plik wyboru, na ktorym metoda programu konczy sie wyjatkiem (tresc JSON niebedaca
obiektem, np. `[1, 2]`) = BLAD "program nie wystartuje" - program wczytuje ten plik przy kazdym starcie, takze przy puli per praca.

Folder istniejacy, ale pusty, nie jest bledem (swieza instalacja): pusta pula to OSTRZEZENIE w wierszu `pula`
("skany beda czekac"), choc sam program pokazuje wtedy komunikat poziomu blad - dopiero gdy skany naprawde czekaja.
Folder sieciowy, ktory nie odpowiada w 5 s (`LIMIT_FOLDERU_S`), jest traktowany jak brak; cztery foldery sa sprawdzane rownolegle.

**Pierwsza instalacja ze wzorem ustawien** (decyzja koordynatora): foldery `C:/sciezka/do/...` ze wzoru nie istnieja, wiec
`folder_skanera` i `folder_cyrkon` = BLAD i kod wyjscia 1 - zostaje (instalator nazywa to "wstrzymana - uzupelnij
ustawienia"). Rada tych wierszy podaje doslownie plik do edycji i klucz, np. `otworz plik ustawien C:\...\ustawienia.toml
i popraw klucz [sciezki] folder_cyrkon (wiersz folder_cyrkon = "...", sciezka z ukosnikami /) albo utworz / podlacz ten folder`.

## Sumy plikow programu i plik nadmiarowy

- Liczone sa sumy plikow wymienionych w pliku sum; wynik "zgodne n z n" albo lista pierwszych 10 roznic
  (`zmieniony`, `brak`, `nieczytelny`, `nadmiarowy`) i liczba kolejnych.
- **Plik nadmiarowy to BLAD** (ustalenie paczki A11s). Uzasadnienie: suma ma potwierdzic, ze katalog programu jest rowny
  wydaniu, a plik spoza listy moze zmienic dzialanie programu bez zmiany zadnego pliku z listy - modul o nazwie biblioteki
  w katalogu glownym (`json.py`, `numpy/`) zostalby zaladowany zamiast wlasciwego (katalog programu jest pierwszy na
  sciezce importu), dodatkowy `plytka_n7.stl` dodaje numer plytki do ukladu, a plik ze starej wersji programu oznacza
  instalacje "na wierzch", ktorej wariant B nie przewiduje.
- Strefa, w ktorej szuka sie plikow nadmiarowych: (1) katalogi najwyzszego poziomu wymienione na liscie sum (np.
  `stanowisko/`, `ramka/`, `modele_plytek/`, `narzedzia/`) z podkatalogami; (2) w katalogu glownym programu tylko pliki,
  ktore Python moze zaladowac (`.py`, `.pyw`, `.pyd`, `.pth`, `.dll`), i katalogi z `__init__.py` spoza listy.
  Nie sa nadmiarowe: `__pycache__/`, `*.pyc`, `ustawienia.toml`, `dane/`, srodowisko wirtualne wersji, sam plik sum oraz
  pliki systemowe Windows `Thumbs.db` i `desktop.ini` (Eksplorator tworzy je po zmianie widoku folderu, nie zmieniaja
  dzialania programu; wielkosc liter bez znaczenia; decyzja koordynatora po recenzji PR #38). Kazdy inny plik spoza listy
  w strefie to nadal BLAD.
- Wniosek dla A11i: lista sum musi obejmowac kazdy plik z katalogow, ktore wymienia (takze `ramka/` - importuje ja
  `indicate`), a pliki tworzone przy instalacji w tych katalogach beda zglaszane jako nadmiarowe.
- Sumy liczone sa z bajtow pliku: zamiana koncow linii przy kopiowaniu (git, edytor) = "zmieniony".

## Czego samokontrola nie zmienia

- Baza: polaczenie `mode=ro`; nie zaklada pliku, nie migruje, nie cofa niedokonczonego zapisu (test: sumy plikow bazy,
  dziennika i ustawien przed i po; brak nowych plikow i folderow). `quick_check` ma limit 4 s - krotszy niz czekanie
  programu na baze (5 s), wiec samokontrola uruchomiona obok pracujacego programu nie powoduje w nim "nie zapisano".
  Baza w trybie WAL (program go nie ustawia; moze go wlaczyc przegladarka bazy) NIE jest otwierana: samo otwarcie, takze
  tylko do odczytu, tworzy obok pliki `-shm` i `-wal`. Tryb i wersja schematu sa czytane z naglowka pliku (100 bajtow,
  zwykle otwarcie pliku), wynik to OSTRZEZENIE "spojnosci nie sprawdzono".
- Foldery: zadnego nie tworzy. Jedyny zapis: plik probny `samokontrola_<pid>_<losowe>.tmp` w ISTNIEJACYM folderze danych,
  usuwany od razu (jedno `os.open` z nowa nazwa - bez `tempfile.mkstemp`, ktore w folderze bez prawa tworzenia plikow
  ponawia probe 2^31 razy i wisi). Gdy folderu danych jeszcze nie ma, proby zapisu nie ma (OSTRZEZENIE, nie sprawdzono).
- Log programu: wywolanie metody programu `Aplikacja._wczytaj_pule` (folder puli) nie zostawia wpisu w logu programu ani
  na wyjsciu bledow (filtr wpisow biezacego watku na czas wywolania).
- Ramki: jedno `GET /stan` na ramke, z naglowkiem `X-Ramka-Klucz` (gdy ustawiony) i bez `X-Laptop-Id` - ramka nie
  zapisuje kontaktu laptopa, nie zmienia planu ani wlasciciela (test na atrapie ramki: stan przed i po).
- Excel: tylko `GetActiveObject("Excel.Application")`; nie uruchamia Excela, nie dotyka skoroszytu ani arkusza.
- Blokada programu: proba zajmuje blokade pliku `<baza>.blokada` na ulamek milisekundy i od razu ja zwalnia; pliku nie
  tworzy i nie zmienia. Program startujacy dokladnie w tej chwili zobaczylby "program juz dziala" (trzeba uruchomic ponownie).
- Rejestr Windows: tylko odczyt `HKCU\Software\SyncEngines\Providers\OneDrive\*\MountPoint` (foldery synchronizowane).
- Python sam tworzy `__pycache__` w katalogu programu przy pierwszym imporcie - to nie jest zmiana danych i nie jest plikiem nadmiarowym.

## Dane osobowe

W wyjsciu sa tylko sciezki wpisane w `[sciezki]` (foldery glowne, plik ustawien, folder danych), hosty ramek i liczniki.
Nie sa wypisywane: nazwy podfolderow i plikow zlecen (pula i indeks = same liczby; folder puli wybrany w programie = bez
sciezki), nazwy osob z `[sesja] operatorzy` (liczba; takze w komunikacie kodu 2 - komunikat bledu ustawien jest pokazywany
bez wartosci z pliku, poza `[sciezki]`, `[plytki]` i liczbami), klucz ramek, tresc bledow systemu (sam typ wyjatku, bo
komunikat zawiera sciezke). Testy: `test_wyjscie_bez_nazw_zlecen_takze_przy_bledach`, `test_pula_*`, `test_b1_*`,
`test_folder_nieczytelny_*`, `test_ramki_zly_klucz_*`, `test_p2_*`, `test_p4_*`.

## Limity czasu i stale (wszystkie w naglowku modulu, z komentarzem)

**Samokontrola nie wisi.** Kazde sprawdzenie dziala w watku pomocniczym i ma gorny limit czasu: `LIMIT_SPRAWDZENIA_S` 30 s,
`moduly` 120 s (`LIMIT_MODULOW_S`: pierwszy import Qt i Open3D z zimnego dysku), `excel` 10 s (`LIMIT_EXCELA_S`: Excel zajety
edycja komorki moze nie odpowiedziec). Po limicie wiersz to BLAD `sprawdzenie nie zakonczylo sie w N s` (ramki, Excel:
OSTRZEZENIE) i wykonywane sa nastepne sprawdzenia. Limity wewnetrzne sa krotsze, wiec w zwyklych stanach limit ogolny nie
dziala: `LIMIT_RAMKI_S` 3 s (obie ramki rownolegle, nazwa `.local` bez odpowiedzi tez konczy sie w limicie),
`LIMIT_FOLDERU_S` 5 s (foldery pracy; wstepne sprawdzenie folderu danych - bez odpowiedzi wiersze danych nie dotykaja
dysku), `LIMIT_LICZENIA_S` 5 s (liczenie STL puli - potem "co najmniej N"), `LIMIT_QUICK_CHECK_S` 4 s, `CZEKAJ_NA_BAZE_MS`
1000. Pozostale stale: `MIEJSCE_OSTRZEZENIE_GB` 10, `MIEJSCE_BLAD_GB` 1, `MAKS_ROZNIC` 10, `PLIKI_SYSTEMOWE`.
Powod (20.11.2026): w rundzie 1 plik probny tworzyl `tempfile.mkstemp`, ktory w folderze bez prawa tworzenia plikow (zakaz
w uprawnieniach NTFS) kreci sie w petli 2^31 prob na 100 % rdzenia: skrypt proby z tym wywolaniem wisial ponad 2 godziny,
a samokontrola rundy 1 w tym stanie nie dala wyniku w 60 s (przerwana). Teraz ten stan daje `BLAD dane_folder`, caly proces 2,6 s.

Zmierzone na PC 20.11.2026, runda 2 (swiezy katalog, ustawienia ze wzoru, foldery istnieja): z `--bez-sieci` `czas_s`
2,1-2,3 s (caly proces 2,5-2,6 s; 3 pomiary), z proba nieobecnych ramek 5,0 s (proces 5,2-5,3 s; 2 pomiary).

**Kryterium "dziala".** `testy/test_samokontrola.py` (148 testow): kazde sprawdzenie w stanie OK i w stanie zlym, kody
wyjscia 0 / 1 / 2, format wierszy i `--json`, `--sumy` (zgodne, zmieniony, brakujacy, nadmiarowy, zly plik sum), swiezy
katalog ze wzoru ustawien = 0 bledow i ramki = ostrzezenie, brak zmian w bazie / ustawieniach / folderach, prawdziwe
polecenie `python -m stanowisko.samokontrola` w osobnym procesie ponizej 20 s; prawdziwe stany zle bez podmiany funkcji
samokontroli: brak pakietu (prawdziwe metadane), modul z bledem importu (prawdziwe ladowanie funkcja programu), zakaz zapisu
w folderze danych (uprawnienia NTFS), baza trzymana przez inny program bez wspoldzielenia, baza w trybie WAL, folder puli
wybrany w programie (zgodnosc z prawdziwym `Aplikacja`), wyjatek i brak odpowiedzi w jednym sprawdzeniu.

**Zalozenia i granice.**
- Samokontrola zielona nie znaczy, ze skaner, ramki i Excel dzialaja poprawnie - tylko ze program ma do nich droge.
- Ustawienia ze wzoru bez poprawionych sciezek (`C:/sciezka/do/...`) daja BLAD `folder_skanera` i `folder_cyrkon`
  (kod 1) - zamierzone i potwierdzone decyzja koordynatora: bez tych folderow nie da sie pracowac, instalator nazywa ten
  stan "wstrzymana - uzupelnij ustawienia".
- Bez `requirements.txt` w katalogu programu wiersz `pakiety` to OSTRZEZENIE (wersji nie ma z czym porownac); pakiety
  potrzebne w pracy sa wtedy sprawdzane z listy `PAKIETY_W_PRACY`.
- Folder synchronizowany: BLAD tylko wtedy, gdy system zna folder jako synchronizowany - zmienne srodowiska `OneDrive*`
  albo wpisy OneDrive w rejestrze uzytkownika (obejmuja biblioteki SharePoint). Sama nazwa czesci sciezki (zaczyna sie od
  "OneDrive" albo zawiera "SharePoint") to OSTRZEZENIE z rada, jak to sprawdzic (decyzja koordynatora po recenzji PR #38:
  nazwy "OneDriveTemp", "Archiwum SharePoint 2024" dawaly falszywy BLAD). Skutek uboczny: dane w folderze OneDrive innego
  konta Windows niz to, z ktorego dziala samokontrola, to tylko OSTRZEZENIE. Inne uslugi (Dropbox, Dysk Google) nie sa
  rozpoznawane.
- Folder danych, ktorego jeszcze nie ma: prawa zapisu nie da sie sprawdzic bez tworzenia folderu (`os.access` w Windows
  widzi tylko atrybut "tylko do odczytu", nie uprawnienia) - OSTRZEZENIE "zapisu nie sprawdzono"; po zalozeniu folderu
  przez instalator albo program zapis sprawdza plik probny.
- Limit czasu sprawdzenia nie przerywa watku, tylko przestaje na niego czekac: w poleceniu konczy sie razem z procesem,
  a przy wywolaniu `wykonaj` z programu zostaje w tle, dopoki system nie odda sterowania (np. dysk sieciowy wroci).
- Plik `stanowisko_pula.json` o tresci JSON niebedacej obiektem zatrzymuje start programu (`Aplikacja._wczytaj_pule`
  nie lapie `AttributeError`) - samokontrola zglasza to jako BLAD `pula`; poprawka nalezy do `aplikacja.py` (poza A11s).
- Baza w trybie WAL: wersja schematu pochodzi z naglowka pliku (zmiany czekajace w pliku `-wal` nie sa widoczne).
- [usunieto w kopii: opis dostepu ssh]
  Excela technika (OSTRZEZENIE mimo otwartego Excela).
- `uklad.json` jest sprawdzany funkcja programu (`uklad.wczytaj`, potrzebuje numpy); gdy numpy sie nie laduje (BLAD
  w `moduly`), kontrola modeli jest uproszczona (klucze pliku, obecnosc `plytka_n*.stl`).
- Stale `PLIK_PULI`, `PLIK_WSPOLCZYNNIKOW`, `NAGLOWEK_KLUCZA` powtarzaja stale modulow `aplikacja` i `indicate` (bez
  importu tych modulow na poziomie pliku); rownosc pilnuja testy.
- Nie sprawdza: zawartosci pliku `wspolczynniki.csv`, kalibracji ramek, uprawnien do folderow pracy poza odczytem
  listy, wolnego miejsca w folderze skanera, zegara systemowego.
