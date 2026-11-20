# samokontrola - czy program ma na tym komputerze wszystko, czego potrzebuje (E3-A11s, 20.11.2026)

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
- Kod 2 (brak pliku ustawien, blad skladni albo walidacji ustawien, nieznana opcja polecenia): na wyjsciu jeden wiersz
  `BLAD ustawienia: <opis>; <co zrobic>` i `SAMOKONTROLA: NIEWYKONANA (blad ustawien - zadnego sprawdzenia nie wykonano)`,
  bez sladu wyjatku. Opis to komunikat modulu `ustawienia` (nazwa pliku, sekcja, klucz) bez polskich znakow. Nieznana
  opcja: komunikat `argparse` na wyjsciu bledow.
- `--json`: jeden obiekt JSON (ASCII): `samokontrola` (ZIELONA / CZERWONA / NIEWYKONANA), `kod_wyjscia`, `ok`,
  `ostrzezenia`, `bledy`, `podsumowanie` (ostatni wiersz wyjscia tekstowego), `czas_s`, `sprawdzenia` = lista obiektow
  `{kod, poziom, opis, rada}` w tej samej kolejnosci i z tymi samymi tekstami, co wyjscie tekstowe.
- `--sumy PLIK`: plik w formacie `sha256sum` (`<64 znaki hex>  <sciezka wzgledna od katalogu programu>`; dopuszczone `*`
  przed sciezka, konce linii CRLF, ukosniki w obie strony). Bez opcji: sprawdzany jest `SUMY_PROGRAMU.sha256` z katalogu
  programu, a gdy go nie ma - OSTRZEZENIE "kopia robocza bez pliku sum". Opcja wskazujaca plik, ktorego nie ma = BLAD `sumy`.
- `--bez-sieci`: bez proby polaczenia z ramkami (oba wiersze ramek = OSTRZEZENIE "pominieto").
- `--ustawienia PLIK`: domyslnie `ustawienia.toml` w katalogu programu (jak program).

**API.** `samokontrola.wykonaj(ust, *, plik_ustawien=None, sumy=None, bez_sieci=False, korzen=None, limit_ramki_s=None)
-> Wynik`. `ust` = wynik `ustawienia.wczytaj_ustawienia`; `plik_ustawien` potrzebny tylko do listy kluczy domyslnych;
`korzen` = katalog programu (domyslnie ten, z ktorego dziala modul). `Wynik`: `sprawdzenia` (lista `Sprawdzenie` z polami
`kod`, `poziom`, `opis`, `rada`; `wiersz()`), `sprawdzenie(kod)`, `ok`, `ostrzezenia`, `bledy`, `zielona`, `kod_wyjscia`,
`podsumowanie()`, `wiersze()`, `tekst()`, `do_slownika()`, `czas_s`; mozna po nim iterowac. `rada` jest pusta dokladnie
wtedy, gdy poziom to `OK`. `wykonaj` nie rzuca wyjatku z powodu stanu komputera: sprawdzenie przerwane bledem ma poziom
BLAD ("sprawdzenie przerwane bledem programu"). Stale: `KODY` (kolejnosc wierszy), `OK`, `OSTRZEZENIE`, `BLAD`, `PLIK_SUM`.
Uwaga dla ekranu: wywolanie trwa do kilku sekund (ramki, foldery sieciowe) - wolac poza watkiem okna.

## Sprawdzenia

| Nr | Kod | Co sprawdza | OSTRZEZENIE, gdy | BLAD, gdy |
|---|---|---|---|---|
| 1 | `python` | wersja Pythona 3.12 | - | inna wersja niz 3.12 |
| 2 | `pakiety` | wersje pakietow z `requirements.txt` (metadane, bez importu); `pytest` pomijany | inna wersja niz przypieta (lista `nazwa jest (wymagana x)`); brak pakietu dodatkowego: `pywin32`, `rtree`, `beautifulsoup4`, `pypdf`; brak `requirements.txt` w katalogu programu | brak pakietu potrzebnego w pracy: `numpy`, `scipy`, `trimesh`, `pillow`, `open3d`, `PySide6`, `watchdog` |
| 3 | `moduly` | import modulow z DLL ta sama funkcja i lista, co start programu (`aplikacja.zaladuj_moduly_dll`: Qt, `MODULY_DLL`, `MODULY_DLL_PULI`, `stanowisko.porownaj`) | nie laduje sie tylko `pythoncom` / `win32com.client` (bez Excela) | nie laduje sie jakikolwiek inny modul |
| 4 | `ustawienia` | plik wczytany i poprawny; lista kluczy uzupelnionych wartoscia domyslna (informacja) | - | (kod wyjscia 2: brak albo blad pliku) |
| 5 | `operatorzy` | `[sesja] operatorzy` niepusta (podaje tylko liczbe osob) | lista pusta: program nie zapisuje decyzji | - |
| 6 | `folder_skanera` | `[sciezki] folder_eksportu_skanera` istnieje i daje sie czytac | - | brak, nie folder, nieczytelny, brak odpowiedzi w 5 s |
| 7 | `folder_cyrkon` | `[sciezki] folder_cyrkon`, jak wyzej | - | jak wyzej |
| 8 | `folder_prywatne` | `[sciezki] folder_prywatne`, jak wyzej | jak wyzej (zawsze tylko ostrzezenie) | - |
| 9 | `folder_millbox` | `[sciezki] folder_millbox`, jak wyzej | jak wyzej przy `[silnik] pula_wpisow = false` | jak wyzej przy `pula_wpisow = true` |
| 10 | `dane_folder` | folder danych (= folder pliku bazy) istnieje i przyjmuje zapis pliku probnego | folderu nie ma, ale da sie go utworzyc ("zostanie zalozony przy pierwszym starcie", zapisu nie sprawdzono) | zapis pliku probnego nieudany; na sciezce lezy plik albo brak prawa zapisu |
| 11 | `dane_miejsce` | wolne miejsce na dysku folderu danych | ponizej 10 GB | ponizej 1 GB |
| 12 | `dane_polozenie` | sciezki danych z `[sciezki]` (`baza`, `log_excel`, `wyniki`, `podglady`, `pula_cache`, `logi`, `kalibracja_ramek`) poza folderami synchronizowanymi | folder danych w katalogu programu zainstalowanego z paczki (obok lezy `SUMY_PROGRAMU.sha256`): aktualizacja "zgubi" baze | ktorakolwiek sciezka w folderze OneDrive / SharePoint |
| 13 | `baza` | plik bazy otwierany tylko do odczytu: wersja schematu wobec programu, `PRAGMA quick_check` | brak pliku albo plik pusty ("zostanie zalozona przy pierwszym starcie"); wersja starsza ("migracja z kopia przy starcie"); baza zajeta; niedokonczony zapis (plik `-journal`); `quick_check` nie zmiescil sie w 4 s | wersja nowsza niz program; plik nie jest baza; `quick_check` zglasza problemy |
| 14 | `modele` | kazdy uklad z `[plytki]`: katalog, `uklad.json` poprawny wg `uklad.wczytaj`, co najmniej jeden `plytka_n<numer>.stl` | - | ktorykolwiek uklad wadliwy (lista `nazwa: wada`) |
| 15 | `pula` | stan puli wg `[silnik] pula_wpisow` - licznikami | pula pusta albo folder puli niedostepny; przy puli per praca: brak bazy, 0 projektow w indeksie, brak `wspolczynniki.csv` | - |
| 16 | `pamiec_puli` | `[sciezki] pula_cache` / `projekty`: liczba wpisow i rozmiar | sciezka jest plikiem, nie folderem | - |
| 17 | `ramka_wieczorna` | `GET /stan` pod `[ramki] wieczorna_host`:`port`, limit 3 s | ramka nieobecna, brak odpowiedzi w limicie, zly klucz (401), inna rola, inny program, blad sprzetu ramki, `--bez-sieci` | - |
| 18 | `ramka_poranna` | to samo dla `poranna_host` | jak wyzej | - |
| 19 | `excel` | pywin32 i uruchomiony Excel - ta sama droga, co `excel_com.polacz` (`GetActiveObject`), bez otwierania arkusza; uwagi `excel.Konfiguracja.z_ustawien` | brak pywin32; Excel nieuruchomiony; uwaga do ustawien `[excel]` / `log_excel` | - |
| 20 | `egzemplarz` | czy program dziala teraz na tej bazie (blokada `<baza>.blokada`) i czy baza byla zajeta | program uruchomiony; baza zajeta przez inny program (to informacja, kod wyjscia zostaje 0) | - |
| 21 | `sumy` | sumy SHA-256 plikow programu z listy; pliki nadmiarowe | brak pliku sum w katalogu programu ("kopia robocza bez pliku sum") | plik zmieniony, brakujacy, nieczytelny albo nadmiarowy (pierwszych 10 roznic + liczba kolejnych); zly albo brakujacy plik sum |

Poczatki opisow, ktore instrukcja moze cytowac (reszta opisu to sciezka z ustawien albo liczby):

| Kod | Poziom | Opis zaczyna sie od | Rada |
|---|---|---|---|
| `python` | BLAD | `program uruchomiony Pythonem` | `zainstaluj Python 3.12 i zainstaluj program ponownie z paczki wydania` |
| `pakiety` | BLAD | `wersje pakietow zgodne N z M z requirements.txt - brak <pakiet>` | `zainstaluj program ponownie z paczki wydania (pakiety instaluje instalator, bez internetu)` |
| `moduly` | BLAD | `moduly programu z bibliotekami DLL: zaladowane N z M - nie laduja sie:` | `zainstaluj program ponownie z paczki wydania, gdy blad wraca - zglos ten wiersz osobie, ktora instaluje program` |
| `ustawienia` | BLAD (kod 2) | `brak pliku ustawien:` / `plik ustawien niepoprawny -` | `skopiuj ustawienia.przyklad.toml jako ustawienia.toml i uzupelnij sciezki albo podaj plik w --ustawienia` / `popraw plik ustawien (wzor: ustawienia.przyklad.toml) albo podaj wlasciwy plik w --ustawienia` |
| `operatorzy` | OSTRZEZENIE | `lista osob jest pusta` | `wpisz osoby w pliku ustawien: [sesja] operatorzy = ["...", "..."]` |
| `folder_skanera`, `folder_cyrkon`, `folder_prywatne`, `folder_millbox` | BLAD / OSTRZEZENIE | `brak folderu` / `sciezka folderu ... nie jest folderem` / `folderu ... nie da sie czytac` / `folder ... nie odpowiada w 5 s` | `utworz albo podlacz ten folder, albo popraw [sciezki] <klucz> w pliku ustawien` |
| `dane_folder` | BLAD | `w folderze danych nie udal sie zapis pliku probnego` / `folderu danych nie da sie utworzyc` | `nadaj prawo zapisu do folderu danych albo popraw [sciezki] baza w pliku ustawien` |
| `dane_folder` | OSTRZEZENIE | `folder danych nie istnieje - zostanie zalozony przy pierwszym starcie programu` | `nic nie rob - po pierwszym uruchomieniu programu uruchom samokontrole jeszcze raz` |
| `dane_miejsce` | BLAD / OSTRZEZENIE | `wolne miejsce na dysku folderu danych: X GB` | `zwolnij miejsce na dysku - ...` |
| `dane_polozenie` | BLAD | `dane programu leza w folderze synchronizowanym OneDrive / SharePoint:` | `przenies dane poza folder synchronizowany i popraw te sciezki w pliku ustawien - ...` |
| `baza` | OSTRZEZENIE | `brak pliku bazy - zostanie zalozona przy pierwszym starcie programu` | `nic nie rob - baza powstanie sama przy pierwszym uruchomieniu programu` |
| `baza` | OSTRZEZENIE | `baza starsza niz program: wersja schematu N, program ma M - migracja z kopia przy starcie programu` | `nic nie rob - program przy starcie sam zrobi kopie pliku bazy i ja zaktualizuje` |
| `baza` | OSTRZEZENIE | `baza ma niedokonczony zapis po przerwanej pracy` | `uruchom program, zamknij go i uruchom samokontrole ponownie - pliku z koncowka -journal nie usuwaj i nie kopiuj bazy bez niego` |
| `baza` | BLAD | `baza nowsza niz program: wersja schematu N` | `zainstaluj wersje programu, ktora zalozyla te baze, albo nowsza - nie uruchamiaj na niej starszego programu` |
| `baza` | BLAD | `plik nie jest baza SQLite albo jest uszkodzony` / `baza uszkodzona: quick_check` | `zamknij program i przywroc baze z kopii (plik kopii obok bazy albo kopia zrobiona przez instalator) - samokontrola bazy nie naprawia, ...` |
| `modele` | BLAD | `uklady plytek z [plytki]: poprawne N z M -` | `zainstaluj program ponownie z paczki wydania (katalog modele_plytek) albo popraw [plytki] w pliku ustawien` |
| `pula` | OSTRZEZENIE | `pula z jednego folderu (pula_wpisow = false): 0 plikow STL` / `pula per praca (pula_wpisow = true):` | `skopiuj projekty STL do folderu puli i uzyj w programie Odswiez pule - bez projektow skany czekaja` (i podobne) |
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
| Cyrkon | BLAD | pula projektow: `Aplikacja._policz_pule` przy braku folderu daje pule niedostepna i kazdy skan czeka (`pula_brak_folderu`, poziom blad); przy puli per praca `indeks` zglasza "brak katalogu" i pula jest pusta. PW zal. F: "Wszystkie gniazda szare (brak projektow)". |
| Prywatne | OSTRZEZENIE | czytany tylko przy `pula_wpisow = true` (`indeks.zrodla_z_ustawien`); bez niego do puli nie wchodza tylko prace prywatne, reszta pracy idzie normalnie. |
| MillBox | OSTRZEZENIE przy `pula_wpisow = false`, BLAD przy `true` | czytany tylko przy puli per praca: w nim lezy `wspolczynniki.csv`, z ktorego pochodza wiersze puli wieczornej (`pula.pula_wieczorna` = wiersze `frezowania`); bez folderu pula wieczorna nie dostaje nowych prac i skany wieczorne czekaja (`pula_wpisow_pusta`, poziom blad). Przy `pula_wpisow = false` program z folderu nie korzysta. |

Folder istniejacy, ale pusty, nie jest bledem (swieza instalacja): pusta pula to OSTRZEZENIE w wierszu `pula`
("skany beda czekac"), choc sam program pokazuje wtedy komunikat poziomu blad - dopiero gdy skany naprawde czekaja.
Folder sieciowy, ktory nie odpowiada w 5 s (`LIMIT_FOLDERU_S`), jest traktowany jak brak; cztery foldery sa sprawdzane rownolegle.

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
  Nie sa nadmiarowe: `__pycache__/`, `*.pyc`, `ustawienia.toml`, `dane/`, srodowisko wirtualne wersji, sam plik sum.
- Wniosek dla A11i: lista sum musi obejmowac kazdy plik z katalogow, ktore wymienia (takze `ramka/` - importuje ja
  `indicate`), a pliki tworzone przy instalacji w tych katalogach beda zglaszane jako nadmiarowe.
- Sumy liczone sa z bajtow pliku: zamiana koncow linii przy kopiowaniu (git, edytor) = "zmieniony".

## Czego samokontrola nie zmienia

- Baza: polaczenie `mode=ro`; nie zaklada pliku, nie migruje, nie cofa niedokonczonego zapisu (test: sumy plikow bazy,
  dziennika i ustawien przed i po; brak nowych plikow i folderow). `quick_check` ma limit 4 s - krotszy niz czekanie
  programu na baze (5 s), wiec samokontrola uruchomiona obok pracujacego programu nie powoduje w nim "nie zapisano".
- Foldery: zadnego nie tworzy. Jedyny zapis: plik probny `samokontrola_*.tmp` w ISTNIEJACYM folderze danych, usuwany od
  razu. Gdy folderu danych jeszcze nie ma, proby zapisu nie ma (OSTRZEZENIE, nie sprawdzono).
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
sciezki), nazwy osob z `[sesja] operatorzy` (liczba), klucz ramek, tresc bledow systemu (sam typ wyjatku, bo komunikat
zawiera sciezke). Testy: `test_wyjscie_bez_nazw_zlecen_takze_przy_bledach`, `test_pula_*`, `test_folder_nieczytelny_*`,
`test_ramki_zly_klucz_*`.

## Limity czasu i stale (wszystkie w naglowku modulu, z komentarzem)

`LIMIT_RAMKI_S` 3 s (obie ramki rownolegle, nazwa `.local` bez odpowiedzi tez konczy sie w limicie), `LIMIT_FOLDERU_S` 5 s,
`LIMIT_LICZENIA_S` 5 s (liczenie STL puli - potem "co najmniej N"), `LIMIT_QUICK_CHECK_S` 4 s, `CZEKAJ_NA_BAZE_MS` 1000,
`MIEJSCE_OSTRZEZENIE_GB` 10, `MIEJSCE_BLAD_GB` 1, `MAKS_ROZNIC` 10. Zmierzone na PC 20.11.2026 (swiezy katalog, ustawienia ze
wzoru, foldery istnieja): z `--bez-sieci` 1,8-2,0 s (caly proces 2,3-4,0 s), z proba nieobecnych ramek 4,7 s.

**Kryterium "dziala".** `testy/test_samokontrola.py` (90 testow): kazde sprawdzenie w stanie OK i w stanie zlym, kody
wyjscia 0 / 1 / 2, format wierszy i `--json`, `--sumy` (zgodne, zmieniony, brakujacy, nadmiarowy, zly plik sum), swiezy
katalog ze wzoru ustawien = 0 bledow i ramki = ostrzezenie, brak zmian w bazie / ustawieniach / folderach, prawdziwe
polecenie `python -m stanowisko.samokontrola` w osobnym procesie ponizej 20 s.

**Zalozenia i granice.**
- Samokontrola zielona nie znaczy, ze skaner, ramki i Excel dzialaja poprawnie - tylko ze program ma do nich droge.
- Ustawienia ze wzoru bez poprawionych sciezek (`C:/sciezka/do/...`) daja BLAD `folder_skanera` i `folder_cyrkon`
  (kod 1) - zamierzone: bez tych folderow nie da sie pracowac. Instalator musi wiec dostac prawdziwe sciezki albo
  potraktowac kod 1 z samymi bledami folderow pracy jako "program zainstalowany, uzupelnij ustawienia" (decyzja A11i).
- Bez `requirements.txt` w katalogu programu wiersz `pakiety` to OSTRZEZENIE (wersji nie ma z czym porownac); pakiety
  potrzebne w pracy sa wtedy sprawdzane z listy `PAKIETY_W_PRACY`.
- Folder synchronizowany jest rozpoznawany po zmiennych `OneDrive*`, po wpisach OneDrive w rejestrze uzytkownika i po
  nazwie czesci sciezki (zaczyna sie od "OneDrive" albo zawiera "SharePoint"). Inne uslugi (Dropbox, Dysk Google) nie sa
  rozpoznawane. Falszywy alarm przy folderze nazwanym np. "OneDrive stary" usuwa zmiana nazwy folderu.
- [usunieto w kopii: opis dostepu ssh]
  Excela technika (OSTRZEZENIE mimo otwartego Excela).
- `uklad.json` jest sprawdzany funkcja programu (`uklad.wczytaj`, potrzebuje numpy); gdy numpy sie nie laduje (BLAD
  w `moduly`), kontrola modeli jest uproszczona (klucze pliku, obecnosc `plytka_n*.stl`).
- Stale `PLIK_PULI`, `PLIK_WSPOLCZYNNIKOW`, `NAGLOWEK_KLUCZA` powtarzaja stale modulow `aplikacja` i `indicate` (bez
  importu tych modulow na poziomie pliku); rownosc pilnuja testy.
- Nie sprawdza: zawartosci pliku `wspolczynniki.csv`, kalibracji ramek, uprawnien do folderow pracy poza odczytem
  listy, wolnego miejsca w folderze skanera, zegara systemowego.
