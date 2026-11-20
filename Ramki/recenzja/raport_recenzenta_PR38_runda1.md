# Raport recenzenta - PR #38 (E3-A11s, samokontrola programu), runda 1

- Data: 20.11.2026, PC, konto `<konto-PC>`.
- Zakres: `git -C <PC-katalog>\qc diff main...e3/a11s`, HEAD `c67fbe5` (6 commitow od `bf00921`), 4 pliki nowe, 2575 linii.
- Metoda: wlasny przeglad calego diffu (modul 1182 linie, testy 1018 linii, opis, raport wykonawcy na koncu), potem
  proby w kopii `<PC-katalog>\qc-wt\rec-a11s` (detached `c67fbe5`); pliki robocze i logi: `<PC-katalog>\koordynator\robocze\rec-a11s\`.
- Uruchomiono: testy paczki (91 passed), 5 skryptow prob celowanych (`proby1.py` ... `proby5.py`), 19 uruchomien
  polecenia `python -m stanowisko.samokontrola` w osobnym procesie, 7 wstrzykniec bledu z pelnym plikiem testow po kazdym.
  Pelnego pytest nie powtarzano. Naraz 1 proces python. Kopia recenzenta po probach czysta (`git status --short --ignored` pusty).
- Zgodnosc z A11i sprawdzona odczytem `qc-wt\a11i` (HEAD `eb77d7d`), bez zmian w cudzym worktree.

## 0. Werdykt

**Do scalenia po poprawkach.** B 1, P 5, D 5.

Modul jest staranny: umowa (wiersze, ostatni wiersz, kody 0 / 1 / 2, `--json`, `--sumy`, plik `SUMY_PROGRAMU.sha256`)
dziala w prawdziwym procesie, niczego nie zmienia w zwyklych stanach, limity czasu dzialaja, prawdziwy brak pakietow
i prawdziwy blad importu DLL daja BLAD i kod 1 bez sladu wyjatku. Do poprawy przed scaleniem: jeden zly wynik przy puli
wybranej w programie (B1), bledna diagnoza bazy z ryzykowna rada (P1), dwa komunikaty kodu 2 (P2, P3) i luki testow,
przez ktore 4 z 7 wstrzyknietych bledow nie zostaly wykryte (P4, P5).

## 1. Uwagi

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| B1 | B | `stanowisko/samokontrola.py:440-445, 463-487, 795-814` | `pula_wpisow = false` (wzor), technik wskazal folder puli w programie (`stanowisko_pula.json` obok bazy - wtedy program w ogole nie czyta `[sciezki] folder_cyrkon`, `aplikacja.py:498, 660-669`). (a) `folder_cyrkon` z ustawien nie istnieje, pula wybrana ma 3 pliki STL: wyjscie `BLAD folder_cyrkon: ... pula projektow jest pusta i skany czekaja bez wyniku` i zarazem `OK pula: ... 3 pliki STL, folder wybrany w programie`, `CZERWONA`, kod 1 - instalator nie przelaczy wersji na stanowisku, ktore pracuje poprawnie, a komunikat jest nieprawdziwy. (b) odwrotnie: folder wybrany w programie nie istnieje, nieuzywany `folder_cyrkon` istnieje: `OK folder_cyrkon`, `OSTRZEZENIE pula: folder wybrany w programie niedostepny - pula pusta, skany beda czekac`, `ZIELONA`, kod 0 - ten sam stan (brak folderu puli = praca stoi), ktory dla `folder_cyrkon` jest BLAD, tu przechodzi na zielono. Obie proby wlasne (`proby4.py`, `proby5.py`). | Poziom BLAD przypiac do folderu, z ktorego program naprawde bierze pule: przy `pula_wpisow = false` i puli wybranej w programie brak `folder_cyrkon` = OSTRZEZENIE ("program korzysta z folderu wybranego w programie"), a niedostepny folder wybrany = BLAD w wierszu `pula` (bez sciezki). Test obu stanow na prawdziwych folderach. |
| P1 | P | `stanowisko/samokontrola.py:596-601, 645-659` | Kazdy blad otwarcia inny niz "zajeta" / "readonly" konczy sie wierszem `BLAD baza: plik nie jest baza SQLite albo jest uszkodzony ...; zamknij program i przywroc baze z kopii`. Proba wlasna: poprawna baza otwarta przez inny program bez wspoldzielenia (kopia zapasowa, antywirus) -> ten wiersz, kod 1, po 3,67 s; po zwolnieniu pliku `OK`. Druga droga (wywolanie funkcji): baza na sciezce UNC `//serwer/udzial/...` -> `as_uri()` daje `file://serwer/...`, SQLite odrzuca (`invalid uri authority`), a program taka baze otwiera zwykla sciezka (`baza.py:322`). Technik, ktory poslucha rady, nadpisze dobra baze starsza kopia (utrata decyzji). | Rozroznic kody SQLite: tylko `SQLITE_NOTADB` (26) i `SQLITE_CORRUPT` (11) = "nie jest baza / uszkodzona" z rada o kopii; `CANTOPEN` (14), `IOERR` (10), `PERM` (3), blad URI = BLAD "pliku bazy nie da sie otworzyc (zajety przez inny program albo brak dostepu) - pliku nie zmieniono" z rada "zamknij program trzymajacy plik i powtorz", bez slowa o przywracaniu. URI dla UNC zbudowac poprawnie (`file:////serwer/udzial/...`) i sprawdzic testem. |
| P2 | P | `stanowisko/samokontrola.py:1171-1172` (obietnica: `:25-27`, `opisy_modulow/samokontrola.md:146-148`) | Blad w `[sesja] operatorzy` (powtorzona osoba albo napis zamiast listy) -> kod 2 i w wyjsciu tekstowym oraz `--json` pelna lista / nazwa osob: `... [sesja] operatorzy: lista niepustych, roznych nazw osob (moze byc pusta) (jest ['<osoba>', '<osoba>'])`. Modul i opis deklaruja, ze nazwy osob nie sa wypisywane; wyjscie trafia na ekran instalatora (A11i drukuje je w calosci). Proba wlasna z fikcyjna osoba: nazwa w wyjsciu - tak (2 z 2 przypadkow). | W `main` dla komunikatu `BladUstawien` dotyczacego `[sesja] operatorzy` uciac czesc "(jest ...)" (albo ogolnie: wartosc pokazywac tylko dla kluczy z `[sciezki]`, `[plytki]` i liczb). Test: nazwa osoby nie wystepuje w wyjsciu kodu 2. Poprawic zdanie w opisie, jesli zakres ma byc wezszy. |
| P3 | P | `stanowisko/samokontrola.py:1165-1176` | Plik ustawien zapisany w Notatniku jako ANSI (cp1250; wystarczy polska litera w sciezce lub komentarzu - wzor ma je w komentarzach): `tomllib` rzuca `UnicodeDecodeError`, ktorego `ustawienia.wczytaj_ustawienia` nie zamienia na `BladUstawien`, wiec trafia do galezi ogolnej: `BLAD ustawienia: samokontrola przerwana bledem programu (UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd3 in position 4: invalid continuation byte); zglos ten wiersz osobie, ktora instaluje program`. Kod 2 jest poprawny, ale to nie jest "komunikat dla czlowieka" z umowy: mowi o bledzie programu, nie o pliku, i odsyla dalej zamiast powiedziec, co poprawic. Proba wlasna. | W `main` osobna galaz `UnicodeDecodeError` (przed ogolna): "plik ustawien nie jest zapisany w UTF-8: <plik>" + rada "zapisz plik w kodowaniu UTF-8 (Notatnik: Zapisz jako, Kodowanie UTF-8)". Test z plikiem cp1250. Przy okazji: plik z BOM UTF-8 daje dzis "blad skladni TOML: Invalid statement (at line 1, column 1)" - warto dopisac do rady "albo zapisz bez BOM". |
| P4 | P | `stanowisko/samokontrola.py:1132-1139`; `testy/test_samokontrola.py:383-393` | Wymaganie "wyjatek w jednym sprawdzeniu = wiersz BLAD, reszta wykonana" nie ma testu. Jedyny test tego rodzaju rzuca wyjatek w `_zaladuj`, ktory lapie samo `_moduly` (`:392`), nie petla `wykonaj`. Wstrzykniecie M1 (lapanie w `wykonaj` zawezone do `ZeroDivisionError`): 91 z 91 testow przechodzi. Sam kod dziala (proba S1: `ValueError` w `_dane_miejsce` -> 21 wierszy, `BLAD dane_miejsce: sprawdzenie przerwane bledem programu (ValueError: ... <sciezka>)`, kod 1, nazwa z komunikatu wycieta). | Test: podmienic funkcje uzywana przez jedno sprawdzenie (np. `_wolne_miejsce`) na rzucajaca wyjatek spoza przewidzianych, z nazwa zlecenia w tresci; sprawdzic 21 wierszy, BLAD tylko w tym wierszu, kod 1, brak nazwy w wyjsciu. Drugi przypadek dla sprawdzenia wielowierszowego (`_foldery`: 4 wiersze BLAD). |
| P5 | P | `stanowisko/samokontrola.py:327-332, 378-382, 492-499`; `testy/test_samokontrola.py:117-126, 318-363, 368-400, 490-512` | Trzy drogi do falszywej "ZIELONEJ" sa w testach wylacznie podmienione, wiec zepsucie prawdziwej funkcji przechodzi niezauwazone (kazde: 91 z 91 passed): M2 `_wersja_pakietu` zwraca "0" zamiast None (brak pakietu potrzebnego w pracy staje sie OSTRZEZENIEM "inna wersja", kod 0); M3 `_zaladuj` ignoruje wynik `zaladuj_moduly_dll` (modul z DLL sie nie laduje, wiersz `OK moduly`); M10 `_proba_zapisu` niczego nie zapisuje (folder danych bez prawa zapisu = `OK ... zapis mozliwy`). Dzisiejszy kod jest poprawny (proby W1-W3 i G2 w prawdziwym procesie), ale nic go przed taka regresja nie chroni, a instalator przelacza wersje na slepo po kodzie 0. | Testy bez podmiany funkcji modulu: (1) pakiet o nazwie, ktorej nie ma (dopisany do tymczasowego `requirements.txt` w `korzen=tmp_path`) -> BLAD przez prawdziwe `importlib.metadata`; (2) `monkeypatch.setattr(S, "MODULY_QT", ("modul_ktorego_nie_ma",))` albo atrapa pakietu rzucajaca `ImportError` na `sys.path` -> BLAD przez prawdziwe `aplikacja.zaladuj_moduly_dll`; (3) podmiana `tempfile.mkstemp` / `os.write` (nie `_proba_zapisu`) -> BLAD i brak pliku probnego; plus asercja, ze przy stanie OK plik probny byl naprawde tworzony (np. licznik wywolan `tempfile.mkstemp`). |
| D1 | D | `stanowisko/samokontrola.py:596-601` | Baza przestawiona na tryb WAL (np. przez przegladarke bazy; program sam WAL nie ustawia): po samokontroli obok bazy zostaja `stanowisko.sqlite-shm` (32768 B) i `stanowisko.sqlite-wal` (0 B). Plik bazy bez zmian (suma ta sama). Jedyny znaleziony stan, w ktorym "nie zostawia plikow" nie jest prawda. | Dopisac do `samokontrola.md` ("Zalozenia i granice") albo wykrywac tryb WAL i zglaszac OSTRZEZENIE bez `quick_check`. |
| D2 | D | `stanowisko/samokontrola.py:506-535, 619-631, 703-705, 781-789, 853-866` | Limit czasu maja foldery pracy, pula, ramki i `quick_check`; operacje na folderze danych (`is_dir`, `exists`, `mkstemp`, `disk_usage`, `scandir`, plik blokady, `stanowisko_pula.json`) nie. Folder danych na udziale sieciowym, ktory nie odpowiada, wydluzy samokontrole o czas kolejnych prob systemu (wg komentarza `aplikacja.py:94`: ok. 21 s na jedno `os.stat`; kilkanascie takich wywolan). Nie zmierzono (brak udzialu na PC); dane na dysku sieciowym nie sa przewidziane planem. | Jedno wstepne sprawdzenie folderu danych przez `_z_limitem`; po przekroczeniu limitu wiersze `dane_*`, `baza`, `pamiec_puli`, `egzemplarz` = "folder danych nie odpowiada". |
| D3 | D | `stanowisko/samokontrola.py:516` | `os.access(przodek, os.W_OK)` w Windows sprawdza tylko atrybut "tylko do odczytu", nie uprawnienia: galaz "brak prawa zapisu" dla nieistniejacego folderu danych praktycznie nie zadziala, wynik to zawsze OSTRZEZENIE "zostanie zalozony". Przy ukladzie A11i (instalator zaklada `dane\`) bez znaczenia. | Usunac obietnice "brak prawa zapisu" z komunikatu albo zostawic z dopiskiem w opisie. |
| D4 | D | `stanowisko/samokontrola.py:1031-1037` | Pliki systemowe Windows w strefie programu (`Thumbs.db`, `desktop.ini` po zmianie widoku folderu w Eksploratorze) sa "nadmiarowe" = BLAD, kod 1 (proba wlasna: 2 z 2 zgloszone). Nie zmieniaja dzialania programu. | Pominac `Thumbs.db` i `desktop.ini` (jak `__pycache__`) - patrz tez sekcja 5. |
| D5 | D | `stanowisko/samokontrola.py:538-557`; `testy/test_samokontrola.py:124` | Petla po wpisach rejestru OneDrive nie jest wykonywana ani w testach (funkcja zawsze podmieniona), ani na PC (klucza nie ma na tym koncie); pierwszy raz wykona sie na laptopie stanowiska. Wlasna proba tego samego kodu na zastepczym kluczu HKCU z 2 podkluczami: dziala (1 wpis, bez wyjatku). | Test z atrapa modulu `winreg` w `sys.modules` (2 wpisy, jeden bez `MountPoint`). |

## 2. Wlasne proby

Wszystkie w kopii recenzenta, dane fikcyjne w `koordynator\robocze\rec-a11s\`. `p.sh` = `py.cmd` z katalogu `Ramki\stanowisko` kopii.

| Nr | Polecenie / proba | Wynik |
|---|---|---|
| 1 | `py.cmd -m pytest -q -p no:cacheprovider testy/test_samokontrola.py` | 91 passed, 36,29 s (73 funkcje testowe, 0 skip / xfail) |
| 2 | Prawdziwy proces: `py.cmd -m stanowisko.samokontrola --ustawienia k1\ustawienia.toml --bez-sieci` (swiezy katalog ze wzoru, foldery pracy istnieja) | 22 wiersze (21 + podsumowanie), `SAMOKONTROLA: ZIELONA (ok 13, ostrzezenia 8)`, kod 0, 0 BLAD, caly proces 2,7 s; lista plikow i folderow przed i po identyczna; `git status --short --ignored` kopii pusty |
| 3 | To samo z proba ramek, hosty ze wzoru (`ramka-w.local`, `ramka-p.local`), 3 uruchomienia `--json` | kod 0 x 3, `czas_s` 4,7 / 4,8 / 4,8 s, oba wiersze ramek OSTRZEZENIE "nieobecna ... (gaierror)" |
| 4 | Wzor ustawien bez zmian (`--ustawienia ustawienia.przyklad.toml --bez-sieci`) | kod 1, 2 BLAD (`folder_skanera`, `folder_cyrkon`), `CZERWONA (ok 9, ostrzezenia 10, bledy 2)` - zgodnie z ustaleniem wykonawcy |
| 5 | W1: `python -S` (bez zadnych pakietow), prawdziwe `importlib.metadata` i prawdziwy import | kod 1, 22 wiersze, `BLAD pakiety` (brak 7 potrzebnych + 4 dodatkowe), `BLAD moduly` (zaladowane 12 z 27), brak sladu wyjatku, stderr pusty |
| 6 | W2 / W3: atrapa `open3d` / `numpy` rzucajaca `ImportError("DLL load failed ...")` na poczatku sciezki importu | kod 1 x 2, `BLAD moduly` (23 z 27 / 19 z 27), pozostale wiersze wykonane (22), `modele` w trybie uproszczonym OK 8 z 8 |
| 7 | W4: moduly po `import stanowisko.samokontrola` i po kodzie 2 | z listy numpy, PySide6, open3d, scipy, trimesh, win32com, pythoncom, PIL, `stanowisko.aplikacja`, `stanowisko.uklad`, http.client: zaladowanych 0 |
| 8 | C1: `[sesja] operatorzy` z powtorzona fikcyjna osoba / napis zamiast listy | kod 2 x 2, nazwa osoby w wyjsciu: tak x 2 (tekst i `--json`) -> P2 |
| 9 | D1: plik ustawien w cp1250 / z BOM / katalog zamiast pliku | kod 2 x 3; cp1250: "samokontrola przerwana bledem programu (UnicodeDecodeError ...)" -> P3; BOM: "blad skladni TOML ... line 1, column 1"; katalog: "pliku ustawien nie da sie odczytac (PermissionError)" |
| 10 | F1: obok programu - blokada programu trzymana, otwarta transakcja zapisu (RESERVED) | `OK baza`, `OSTRZEZENIE egzemplarz` (program uruchomiony), 0,02 s; COMMIT programu po samokontroli udany; pliki w `dane` bez zmian; blokada po probie wolna |
| 11 | F1b: zapis programu w czasie, gdy samokontrola trzyma odczyt przez pelny limit 4 s (`_quick_check` sztucznie wydluzony), czekanie programu 5 s | zapis udany po 3,11 s czekania, bez "database is locked" |
| 12 | F2: baza 294 MB w jednej tabeli; pelny `quick_check` i przerwanie limitem 0,05 s | pelny: `['ok']` w 0,52 s; przerwany po 0,072 s (`interrupted`) - limit dziala takze w srodku jednej tabeli |
| 13 | G1: plik bazy otwarty przez inny uchwyt bez wspoldzielenia | `BLAD baza: plik nie jest baza SQLite albo jest uszkodzony ... przywroc baze z kopii`, kod 1, 3,67 s -> P1 |
| 14 | E1: `_polacz_do_odczytu(Path("//serwer/udzial/dane/stanowisko.sqlite"))` (bez dostepu do sieci: blad przed otwarciem pliku) | `OperationalError: invalid uri authority: serwer`; calosci na prawdziwym udziale nie zmierzono (udzial administracyjny PC niedostepny dla konta) -> P1 |
| 15 | E2: baza w folderze ze znakami `#`, `%`, spacja i literami spoza ASCII | `OK baza`, `ZIELONA` |
| 16 | G2: `os.write` rzuca "brak miejsca" w trakcie zapisu pliku probnego | `BLAD dane_folder`, w folderze danych 0 plikow po probie |
| 17 | S1: `ValueError` ze sciezka zlecenia w `_wolne_miejsce` | 21 wierszy, 1 BLAD `dane_miejsce`, sciezka zastapiona `<sciezka>`, kod 1 |
| 18 | T1: obcy serwer HTTP pod adresem ramki (rola z srednikiem i nowa linia w tresci), pusty host, serwer przyjmujacy polaczenie i milczacy | 3,53 s / 3,01 s; wiersze OSTRZEZENIE, tekst roli oczyszczony i przyciety, liczba wierszy 22 |
| 19 | U1: 7 nazw katalogu w sciezce bazy | BLAD: `OneDrive - Pracownia`, `onedrive_stary`, `OneDriveTemp`, `Archiwum SharePoint 2024`; OK: `MojOneDrive`, `one drive`, `Dysk Google` |
| 20 | H1 / H2: prawdziwy rejestr tego konta; kod petli na kluczu zastepczym | 0 wpisow (klucza OneDrive brak); na kluczu zastepczym 1 wpis, bez wyjatku -> D5 |
| 21 | I1: eksport programu z gita (bez `testy`, `raporty`), lista sum zbudowana jak w A11i (kazdy plik), samokontrola uruchomiona z eksportu | 139 plikow, 23,0 MB; `OK sumy: zgodne 139 z 139, plikow nadmiarowych 0`, kod 0 - takze po powstaniu `__pycache__` (2 katalogi) i z `--sumy` podanym jawnie |
| 22 | I2: w eksporcie dodane `stanowisko/stary_modul.py`, `sitecustomize.py`, `notatka.txt`, `dane/a.txt`, `ustawienia.toml`, `Thumbs.db`, `desktop.ini` | kod 1; nadmiarowe 4 (`stary_modul.py`, `sitecustomize.py`, `Thumbs.db`, `desktop.ini`); `notatka.txt`, `dane/`, `ustawienia.toml` pominiete -> D4 |
| 23 | I3: plik sum w UTF-16; pusty; z wierszem komentarza; wskazujacy sam siebie; lezacy w strefie; wielkie litery hex + odwrotne ukosniki + `.\`; zmieniony koniec linii w 1 pliku | BLAD x 5 z czytelnym powodem (UTF-16, pusty, komentarz, sam siebie = "zmieniony", w strefie = "nadmiarowy"); wielkie litery / ukosniki: OK 3 z 3; CRLF w 1 pliku: `zgodne 138 z 139 ... zmieniony modele_plytek/poranna/uklad.json`, kod 1 |
| 24 | X1: baza w trybie WAL | `OK baza`, po probie 2 nowe pliki (`-shm` 32768 B, `-wal` 0 B), plik bazy bez zmian -> D1 |
| 25 | X2 / X3: obca baza SQLite (wersja 0); `stanowisko_pula.json` o 5 zlych tresciach, w tym folder z fikcyjnym nazwiskiem | bez wyjatku; nazwisko w wyjsciu: 0 z 5 |
| 26 | proby4 / proby5: pula wybrana w programie | (a) kod 1 przy 3 plikach STL w puli; (b) kod 0 przy niedostepnym folderze puli -> B1 |
| 27 | Zgodnosc z A11i (odczyt): wywolanie `python -B -X utf8 -m stanowisko.samokontrola --ustawienia PLIK --sumy <program>\SUMY_PROGRAMU.sha256 [--bez-sieci]`, kod 1 / 2 = wersja nieprzelaczona; `requirements.txt` w paczce; piny `requirements.txt` wobec `instalacja/zamrozone.txt` | zgodne z umowa; piny rowne 11 z 11 (pytest osobno w `zamrozone_testy.txt`); dziennik instalatora zapisuje tylko poziom i kod wiersza |

Wstrzykniecia bledu (po kazdym caly `test_samokontrola.py`, potem `git checkout` pliku):

| Nr | Zepsucie | Wynik testow | Wykryte |
|---|---|---|---|
| M1 | `wykonaj`: wyjatek sprawdzenia nie jest lapany | 91 passed | NIE (P4) |
| M2 | `_wersja_pakietu`: brak pakietu zwraca "0" | 91 passed | NIE (P5) |
| M3 | `_zaladuj`: wynik ladowania modulow zamieniony na same True | 91 passed | NIE (P5) |
| M4 | baza otwierana `mode=rw` zamiast `mode=ro` | 1 failed, 90 passed | tak |
| M5 | plik probny nie jest usuwany | 3 failed, 88 passed | tak |
| M6 | `_quick_check` zawsze zwraca "ok" | 2 failed, 89 passed | tak |
| M10 | `_proba_zapisu` niczego nie zapisuje | 91 passed | NIE (P5) |

Razem: 3 z 7 wykryte.

## 3. Kryteria zlecenia

| Nr | Kryterium | Ocena |
|---|---|---|
| 1 | Testy pokrywaja kazde sprawdzenie w stanie OK i zlym, kody 0 / 1 / 2, format, `--json`, `--sumy` (zgodne, zmieniony, brakujacy, nadmiarowy - ustalone: BLAD, opisane) | Potwierdzone przegladem i uruchomieniem (91 passed; kazdy z 21 kodow ma test stanu OK i zlego). Zastrzezenie: czesc stanow zlych tylko przez podmiane funkcji modulu - 4 z 7 wstrzyknietych bledow niewykryte (P4, P5); stan z B1 bez testu. |
| 2 | Swiezy katalog, ustawienia ze wzoru, foldery pracy istnieja: 0 bledow, ramki = ostrzezenie, kod 0 | Potwierdzone wlasna proba (proby 2 i 3: kod 0, 0 BLAD, ramki OSTRZEZENIE). |
| 3 | Samokontrola nie zmienia bazy ani ustawien | Potwierdzone wlasna proba (proba 2: drzewo bez zmian; proba 10: pliki obok dzialajacego programu bez zmian; M4 i M5 wykryte przez testy). Wyjatek poza kryterium: baza w trybie WAL (D1). |
| 4 | Czas z `--bez-sieci` do 20 s; proba ramek ograniczona limitem | Potwierdzone wlasna proba: proces 2,7 s; z proba nieobecnych ramek `czas_s` 4,7-4,8 s; serwer milczacy 3,01 s. Zimny dysk i laptop stanowiska: nie zmierzono. |
| 5 | Pelny pytest: 0 failed | Niepowtarzane (zasada 3). Wg logu wykonawcy `robocze\a11s\pytest_pelny_4ba1504_przebieg2.log` (ostatni wiersz przeczytany): 1920 passed, 9 skipped; przebieg 1 z 1 failed (test czasowy okna) - wg wykonawcy, niesprawdzone. |

Umowa wywolania: format wierszy, ostatni wiersz, kody 0 / 1 / 2, `--json` (jeden obiekt, ASCII), `--sumy`, domyslny
`SUMY_PROGRAMU.sha256`, "kopia robocza bez pliku sum", `wykonaj(ust, ...)` z polami kod / poziom / opis / rada - potwierdzone
wlasnymi probami (2, 4, 5, 9, 21-23). Import ciezkich modulow tylko w sprawdzeniu `moduly` - potwierdzone (proba 7).

## 4. Zakres plikow i zasady

- Pliki: 4 z 4 z listy zlecenia, wszystkie nowe (`samokontrola.py`, `test_samokontrola.py`, `samokontrola.md`, raport);
  zadnej zmiany poza lista, zadnego pliku nietykalnego, bez zmiany schematu bazy i stosu (tylko biblioteka standardowa).
- ASCII / LF: w 4 plikach 0 bajtow spoza ASCII, 0 CR, 0 tabulatorow, 0 spacji na koncu linii, ostatni bajt LF; `git diff --check` pusty.
- Commity: 6, przedrostek `E3-A11s:`, po polsku bez znakow diakrytycznych, stopka `Co-Authored-By` w 6 z 6; pierwszy commit to testy przed kodem.
  Worktree wykonawcy czysty, HEAD `c67fbe5`.
- Testy: pisza tylko do `tmp_path`, siec tylko `127.0.0.1` / `127.0.0.2`, 0 skip / xfail; dane fikcyjne.
- Dane osobowe: w wyjsciu sciezki z `[sciezki]`, liczniki, hosty ramek; nazw podfolderow i plikow zlecen nie znalazlem
  w zadnej probie (pula, indeks, pula wybrana w programie, wyjatki, obcy serwer). Wyjatek: nazwy osob z `[sesja] operatorzy`
  w komunikacie kodu 2 (P2). Raport i opis wykonawcy bez danych osobowych.
- Raport wykonawcy rzetelny: sam wskazal stany testowane przez podmiane funkcji (odstepstwo 4) i skutek dla pierwszej instalacji.

## 5. Do decyzji wlasciciela (nie blokuje)

1. **Pierwsza instalacja ze wzorem ustawien = kod 1** (proba 4: 2 BLAD folderow). Instalator A11i przy kodzie 1 nie przelacza
   wersji i kaze poprawic foldery oraz uruchomic `zainstaluj.cmd` ponownie, wiec pierwsza instalacja ma dwa kroki. Obie paczki
   sa tu ze soba zgodne; decyzja, czy tak ma zostac, czy instalator ma pytac o foldery.
2. **Plik nadmiarowy = BLAD.** Uzasadnienie wykonawcy (modul o nazwie biblioteki w katalogu glownym, dodatkowy model plytki,
   instalacja "na wierzch") jest trafne i zgodne z lista sum A11i (139 z 139, 0 nadmiarowych). Do rozwazenia wyjatek dla
   `Thumbs.db` / `desktop.ini` (D4).
3. **OneDrive / SharePoint po samej nazwie = BLAD.** W probie 19 falszywy alarm dla 2 z 7 nazw (`OneDriveTemp`,
   `Archiwum SharePoint 2024`); skutek: instalacja zablokowana do zmiany nazwy folderu albo sciezki. Wariant ostrozniejszy:
   zmienne `OneDrive*` i rejestr = BLAD, sama nazwa = OSTRZEZENIE.
4. **MillBox przy `pula_wpisow = true` = BLAD.** Jesli folder MillBox jest udzialem komputera frezarki, wylaczony komputer
   w chwili aktualizacji zablokuje przelaczenie wersji. Przy wzorze (`pula_wpisow = false`) to tylko OSTRZEZENIE.
5. **Progi miejsca 10 GB / 1 GB** - bez zastrzezen; tempa przyrostu `dane\` nikt nie zmierzyl (takze wg wykonawcy).
6. **Plik `-journal` obok bazy = OSTRZEZENIE** - oceniam jako wlasciwe: tylko odczyt nie moze cofnac zapisu, program cofa go
   przy starcie (test wykonawcy na prawdziwych plikach; M4 pokazuje, ze test naprawde pilnuje trybu tylko do odczytu).
   Uwaga wykonawcy dla A11i o kopii bazy razem z dziennikiem pozostaje aktualna.
