# Raport recenzenta - PR #52 (E3-O4), runda 2 (recenzja przyrostowa: etap B2)

Data: 21.11.2026, 13:29-13:50. Zakres: commity wykonawcy od HEAD rundy 1 (2337c15) do 373cd79, bez scalenia `main`
(475b1e8): e8fefb1 i 5b62aa8 (kod, testy, dokumenty), 66dd543, ebaf0d8, 373cd79 (tylko raport paczki).
`git diff 475b1e8 373cd79`: 15 plikow, 672 wiersze dodane, 53 usuniete (bez raportu paczki: 14 plikow, 385 / 47).
Scalenie 475b1e8 jest czyste: zmienia 26 plikow i sa to dokladnie te same 26 plikow co `git diff beddde7 8001b55`
(0 roznic list) - nie oceniane. `main...e3/o4`: 26 plikow, 3435 wierszy dodanych.
Metoda: wlasny przeglad diffu rundy 2 (kod, wzor skrotu, 2 instrukcje, testy), potem proby w kopii
`<PC-katalog>\qc-wt\rec-o4` (detached 373cd79) i w odtworzonym ukladzie katalogow instalacji pod
`<PC-katalog>\koordynator\robocze\rec-o4\` (katalog ze spacja i polskimi znakami w nazwie; `wersje\9.9.9\program` =
kopia `stanowisko/` i `narzedzia/pomiar_skanu/` z HEAD, `wersje\0.3.1\program` = kopia modulu z instalacji 0.3.1
`<PC-katalog>\t0\s1`, tylko odczyt zrodla). Logi wykonawcy z instalacji probnej (`robocze\o4\r2_*`) czytane wiersz po
wierszu (liczby w sekcji 3 pochodza z logow, nie z raportu); raport wykonawcy czytany na koncu (sekcje 14.11 i 14.12).
Uruchomiono (wszystko przez `ciezki.ps1 -Tor 3`, 1 proces python naraz): testy paczki (8 plikow), test z
`PermissionError` 10 razy, 23 proby w ukladzie instalacji, 12 wstrzykniec w 7 przebiegach, proba zgodnosci z O2 i O3
(pliki obu galezi nalozone na kopie). Pelnego pytest nie powtarzano. Paczki nie budowano, niczego nie instalowano.

## 0. Werdykt i liczby B / P / D

WERDYKT: do scalenia (B 0 / P 0 / D 4) - P1 i P2 z rundy 1 zamkniete, kryteria 1-7 potwierdzone.

- B: 0. P: 0.
- D: 4 (N1-N4; zadna nie wymaga poprawki przed scaleniem, 2 z nich to pozycje "POTRZEBUJE" poza zakresem paczki).
- Uwagi rundy 1: P1 zamknieta, P2 zamknieta, D1-D8 (uwagi nr 3-10 rundy 1) zamkniete 8 z 8 (tabela nizej).
- Poprawki rundy 2 maja testy, ktore bez nich padaja: 12 z 12 moich wstrzykniec wykrytych.
- Liczby wykonawcy z instalacji probnej zgadzaja sie z logami (sekcja 3); 3 doprecyzowania bez wplywu na werdykt.

### Uwagi rundy 1: zamknieta / otwarta + dowod

| Uwaga | Stan | Dowod |
|---|---|---|
| P1 (brak `ustawienia.toml` instalacji albo wzgledna `baza` = sesja w katalogu wersji, kod 0) | zamknieta | Kod: `dzien_skanera_rdzen.py:2678-2688` (instalacja po `instalacja.json` / `wersja_biezaca.txt` / `ustawienia.toml`), `:2698-2716` (`sprawdz_katalog_sesji`), `:2767-2774` (bez pliku instalacji wzor z katalogu wersji nie jest czytany), `dzien_skanera.py:834, 896-900` (kod 1, komunikat), `pomiar_skanu.py:657-664`. Moje proby P1a-P1f, P2a, P3a, P4a-P4d (sekcja 2): w zadnej z 20 prob na module nowej wersji (P0a-P5b) okno ani pomiar nie zalozyly pliku w `<K>\wersje` (licznik plikow bez zmian, `program\dane` nie istnieje); bez pliku ustawien sesja w `<instalacja>\dane\dzien_skanera`, `ustawienia BRAK; foldery obserwowane: brak` + wiersz `UWAGA` z nazwa brakujacego pliku; baza wzgledna i baza bezwzgledna w `wersje\` bez `--dane` = kod 1 i `BLAD: katalog sesji ... lezy w katalogu wersji programu ... CO ZROBIC ...`; pomiar bez pliku = kod 2 i komunikat o pliku INSTALACJI (takze gdy w katalogu wersji lezy podlozony `ustawienia.toml`). Wstrzykniecia W1, W2, W3, W5, W6 wykryte (2-4 testy kazde). Logi wykonawcy z prawdziwej instalacji: `r2_k12.log:102-104` (brak pliku, skrot: kod 0, BRAK, UWAGA), `:114` (baza wzgledna przez `Polecenie.cmd`: BLAD), `:112-113` (baza wzgledna, skrot: kod 0, sesja w danych instalacji). Ocena "kod 0 bez pliku ustawien" - pod tabela. |
| P2 (po powrocie do 0.3.1 skrot pisze sesje do `wersje\0.3.1`, `--zamknij-po` = kod 2, instrukcja milczy) | zamknieta | Skrot: `instalacja/wzory/Dzien_skanera.cmd:21` podaje `--dane "%KAT%dane\dzien_skanera"` przed `%*`. Modul 0.3.1 zna `--dane` i `--ustawienia` (instalacja 0.3.1 `...\wersje\0.3.1\program\stanowisko\dzien_skanera.py:826, 863, 865`). Moja proba P6b: prawdziwe okno modulu 0.3.1 wolane tak jak wola je nowy skrot (12 s, potem zatrzymane): 1 nowa sesja w `<instalacja>\dane\dzien_skanera`, 0 nowych plikow w `wersje\` (100 -> 100); proba kontrolna P6c (stary skrot rundy 1, bez `--dane`): 3 nowe pliki w `wersje\0.3.1\program\dane` - czyli poprawka dziala i proba ja rozroznia. P6a: `--zamknij-po 5` na 0.3.1 = kod 2, `error: unrecognized arguments`. Logi wykonawcy z prawdziwej instalacji: `r2_akt.log:220` (powrot kod 0), `:226-237` (6 skryptow zostaje, skrot bajtowo rowny wzorowi), `:262-266` (kod 2), `:272-278` (prawdziwy skrot przy 0.3.1: 1 sesja w danych instalacji, `fc` listy `wersje\0.3.1` przed / po: brak roznic), `:323-343` (to samo po ponownym `zainstaluj.cmd` 0.3.1). Instrukcja: `instalacja_i_aktualizacja.md:59-65` (punkt 4: skrot zostaje, sesje w danych instalacji, `--zamknij-po` = kod 2 po angielsku "to nie awaria", pomiar w 0.3.1 nie dziala, to samo po ponownym `zainstaluj.cmd` 0.3.1) i `:98-102` (punkt 7: skrypt podaje katalog sesji wprost; "opcja dziala od wersji nastepnej po 0.3.1"). Wstrzykniecie W4 (skrot bez `--dane`) wykryte: 3 testy. |
| D1 (`WYMAGANE` a `WZORY_SKRYPTOW`) | zamknieta | `test_d1_kazdy_wzor_skrotu_instalatora_jest_wymagany_przy_budowie_paczki`; wstrzykniecie W8 wykryte. |
| D2 (prawa 600 pliku z kluczem bez testu) | zamknieta | `test_d2_plik_z_kluczem_ma_prawa_600_w_skrypcie_instalacji` (test tresci - Git Bash na NTFS praw nie zmienia, opisane w tescie); wstrzykniecie W10 (`umask 022`) wykryte. |
| D3 (`{"protokol": 1` w instrukcji ramki) | zamknieta | `ramka_raspberry_pi.md:296` `{"protokol":1` (bez odstepow); `test_d3_...` porownuje z prawdziwa odpowiedzia programu na atrapie; W9 wykryte. |
| D4 (karta SD zastana w ramce) | zamknieta | `ramka_raspberry_pi.md:56-59` (ostrzezenie przed punktem 1 kroku 1); `test_d4_d6_...`; W12 wykryte. |
| D5 (2 sekcje koncowe bez znacznika) | zamknieta | naglowki `:389` i `:407` maja `[NIE SPRAWDZONE BEZ SPRZETU]`; rozszerzony `test_instrukcja_kazdy_krok_ma_znacznik_niesprawdzone`; W11 wykryte. |
| D6 (`--klucz` w historii powloki) | zamknieta | `ramka_raspberry_pi.md:249-251` (`history -c && history -w`); `test_d4_d6_...`. |
| D7 (pusta sesja po `--zamknij-po`) | zamknieta | `instalacja_i_aktualizacja.md:107-109` i karta dnia skanera wiersze 17-18 ("Tak albo Nie, obie odpowiedzi sa dobre"); bez testu (sam tekst). |
| D8 (plik ustawien z BOM) | zamknieta w zakresie z rundy 1 (opis, bez zmiany zachowania) | wiersz `UWAGA: ustawienia: ...` w probie (`dzien_skanera.py:919-920`) i opis w instrukcji `:103-106`; moja proba P5a i log wykonawcy `r2_k12.log:118-120`: kod 0, sesja w danych instalacji, okno na wzorze i folder `C:\Aidite\Scandata` + wiersz UWAGA. Pozostalosc opisana jako N1. |

Ocena przyjetego domyslnie "bez pliku ustawien okno startuje z kodem 0" (pytanie koordynatora): bezpieczne, P1 uznaje za
zamknieta. Uzasadnienie z prob P1a-P1d i z kodu: (1) okno nie obserwuje wtedy ZADNEGO folderu (`foldery obserwowane:
brak`) - nie obserwuje po cichu folderu ze wzoru ani z pliku podlozonego w katalogu wersji (proba P1d); (2) czlowiek to
widzi: w oknie czerwony, pogrubiony napis "Zaden folder nie jest obserwowany - kliknij Dodaj folder..."
(`dzien_skanera.py:371`) i wpis bledu w dzienniku okna "Nie wczytano ustawien (ustawienia.toml: brak pliku <plik> - uruchom
zainstaluj.cmd ...) - zbieranie plikow dziala, ale skany nie beda sprawdzane" (`:81-82, 886`); w probie `--zamknij-po`
wiersze `ustawienia BRAK` i `UWAGA`; (3) sesja powstaje w danych instalacji, w katalogu wersji 0 nowych plikow; (4) pomiar
szczegolowy konczy sie wtedy kodem 2 z nazwa brakujacego pliku, a nie liczy na wzorze. Ryzyko resztkowe: czlowiek wskaze
folder recznie i zbierze caly dzien skanow bez szybkiej kontroli (tryb "brak") - to tryb awaryjny modulu sprzed paczki,
widoczny w oknie. Odmowa startu zamiast trybu awaryjnego = decyzja wlasciciela (sekcja 5 p. 1), nie blokuje.

## 1. Uwagi (nowe w rundzie 2)

| Nr | Waga | Plik:linia | Scenariusz (stan -> co sie dzieje) | Propozycja |
|---|---|---|---|---|
| N1 | D | `stanowisko/dzien_skanera_rdzen.py:2767-2769` (`zapasowe`), `stanowisko/dzien_skanera.py:748-749` | Plik ustawien instalacji ISTNIEJE, ale ma blad (np. zapisany Notatnikiem jako "UTF-8 z BOM"): okno dalej czyta wzor z katalogu wersji i obserwuje `C:\Aidite\Scandata` (proba P5a; log wykonawcy `r2_k12.log:118`), a przycisk "Pomiar szczegolowy" podalby narzedziu `--ustawienia ...\wersje\<w>\program\ustawienia.przyklad.toml` (odczyt kodu, nie uruchamiano). Dla BRAKU pliku runda 2 wzoru juz nie czyta ("wzor obserwowalby folder ze wzoru, nie folder tej instalacji" - opis funkcji) - ten sam argument dotyczy pliku z bledem. Czlowiek dostaje: w oknie wpis "Plik ustawien ma blad (...) - uzyto ustawienia.przyklad.toml" i folder w wierszu "Obserwuje", w probie wiersz `UWAGA`; instrukcja punkt 7 to opisuje. To pozostalosc D8 z rundy 1 (wtedy: "bez zmiany w tej paczce"), dlatego D. | Po scaleniu, przy okazji: w instalacji traktowac plik z bledem tak jak brak pliku (`zapasowe = []`, okno bez ustawien, zaden folder nie jest obserwowany). 1 wiersz + 1 test. Decyzja: sekcja 5 p. 1. |
| N2 | D | `stanowisko/dzien_skanera_rdzen.py:2711-2715` | `Dzien_skanera.cmd --dane C:\Stanowisko\wersje\x` (albo `--dane` wzgledne - katalog roboczy skrotu to katalog programu; proby P4a, P4b): kod 1, a komunikat radzi "popraw w pliku ustawienia.toml wiersz [sciezki] baza", choc przyczyna jest opcja `--dane`. Instrukcja punkt 7 (`:111-113`) wyjasnia oba przypadki. | Dopisac do komunikatu "albo nie podawaj --dane wskazujacego do wersje\" (kosmetyka). |
| N3 | D | `stanowisko/ui_test.py:47-53`; `narzedzia/import_decyzji.py:158` (plik poza zakresem paczki) | W instalacji okno testowe zapisuje teraz decyzje do `<instalacja>\dane\decyzje.csv`, a `import_decyzji.py` bez `--plik` szuka `wersje\<w>\program\dane\decyzje.csv`. Skutek: `brak pliku decyzji: <sciezka>`, kod 2 - glosno, niczego nie gubi (plik z decyzjami zostaje w danych instalacji i przezywa aktualizacje - to poprawa wobec 0.3.1). Nie ma tez scenariusza "stary plik zaimportowany po cichu": nowy katalog wersji nie ma `dane\`. Para zapis / odczyt i tak nie dziala dzis w instalacji bez opcji: okno testowe bez `--ustawienia` nie startuje (`ui_test.py:568` czyta `ustawienia.toml` z katalogu programu; odstepstwo O-B2-1 wykonawcy), `import_decyzji.py` bez `--baza` tez (`:163`); okno testowe nie ma skrotu w instalacji. Z kopii repo zachowanie bez zmian (`plik_decyzji_domyslny()` = `PLIK_DECYZJI`, sprawdza to `test_okno_testowe_decyzje_w_danych_instalacji`; W7 wykryte). Opisane w `opisy_modulow/instalacja.md:229-232` i w POTRZEBUJE 4 wykonawcy. | Po scaleniu: `import_decyzji.py` - ten sam `katalog_instalacji` (1-2 wiersze), w paczce, ktora ma ten plik w zakresie. Nie blokuje. |
| N4 | D | `testy/test_instalacja.py:472-473` (test z `main`, nie zmieniony przez paczke); `instalacja/instalator.py:1199` (wiersz nie zmieniony przez paczke) | Test `test_ponowna_instalacja_tej_samej_wersji_jest_bezpieczna` padl u wykonawcy 1 raz (`r2_testy_modulow.log:75`: `PermissionError: Odmowa dostepu` przy `os.rename` katalogu wersji, instalator zwrocil kod 6 "Niczego nie zmieniono"). Ocena: srodowisko + wrazliwosc testu na czas, NIE wyscig w instalatorze i nie wada paczki. Test zapisuje plik `aplikacja.py` w katalogu wersji i w tym samym momencie kaze instalatorowi przeniesc caly katalog; srodowisko w tescie jest atrapa (`SrodowiskoAtrapa`, zadnych procesow potomnych), instalator jest jednowatkowy - uchwyt do swiezo zapisanego pliku mogl trzymac tylko proces z zewnatrz (skaner antywirusowy / indeksowanie; w tym czasie na PC szly 3 pelne pytesty). Windows odmawia wtedy zmiany nazwy katalogu. Instalator zachowal sie poprawnie (kod 6, wersja bez zmian, rada "uruchom ponownie"). Powtorki: moje 10 z 10 passed (1,95-2,18 s), wykonawcy 5 z 5, moj przebieg testow paczki 354 passed, pelny pytest wykonawcy 0 failed. Diff paczki w `instalator.py` to 2 miejsca: opis ukladu i `WZORY_SKRYPTOW`. | Bez zmiany w tej paczce. Do rozwazenia osobno: `_wymien_wersje` ponawia `os.rename` 3 razy co 0,5 s przed kodem 6 (pomoze tez na laptopie z antywirusem). |

Bledow wprowadzonych poprawkami rundy 2 nie znalazlem (szukane: zachowanie z kopii repo, `--sesja` i `--sprawdz` przy
nowym `--dane` w skrocie, `--dane` czlowieka po `--dane` skrotu, sciezka ze spacja i polskimi znakami, wielkosc liter
`WERSJE`, `..` w sciezce, katalog `wersje_obok`, plik `--ustawienia`, ktorego nie ma, przy dobrym pliku instalacji).

## 2. Wlasne proby

Testy paczki (kopia `rec-o4`, log `robocze\rec-o4\testy_paczki_r2.log`):

| Polecenie | Wynik |
|---|---|
| `py.cmd -m pytest -q -p no:cacheprovider testy/test_o4_instalacja_dzien_skanera.py testy/test_o4_test_led.py testy/test_o4_ramka_rpi.py testy/test_dzien_skanera.py testy/test_zbuduj_wydanie.py testy/test_instrukcje.py testy/test_ramka.py testy/test_instalacja.py` | 354 passed, 0 failed, 0 skipped, 272 s (runda 1: 342). Kod procesu po wierszu podsumowania: 0xC0000409 (znane zjawisko PC po pytest; wynik w logu kompletny) |
| `testy/test_instalacja.py::test_ponowna_instalacja_tej_samej_wersji_jest_bezpieczna` 10 razy, kazdy w osobnym procesie (`powtorki_r2.log`) | 10 z 10 passed, kod 0, 1,95-2,18 s |

Proby w odtworzonym ukladzie instalacji `<K>` (log `robocze\rec-o4\proby_r2.log`; modul uruchamiany z katalogu
`<K>\wersje\9.9.9\program`; "jak skrot" = `-m stanowisko.dzien_skanera --ustawienia <K>\ustawienia.toml --dane
<K>\dane\dzien_skanera`, "bez opcji" = tak jak `Polecenie.cmd -m stanowisko.dzien_skanera`; wszedzie `--nowa --zamknij-po 1`).
Po kazdej probie liczone pliki w `<K>\wersje` (start: 100):

| Nr | Stan / polecenie | Wynik |
|---|---|---|
| P0a | dobry plik, jak skrot | kod 0; sesja w `<K>\dane\dzien_skanera`; ustawienia i folder obserwowany z pliku instalacji; pliki w `wersje` 100 -> 100 |
| P0b | dobry plik, bez opcji | kod 0; jak wyzej |
| P1a | brak `ustawienia.toml`, jak skrot | kod 0; sesja w `<K>\dane\dzien_skanera`; `ustawienia BRAK; foldery obserwowane: brak`; `UWAGA: ustawienia: ustawienia.toml: brak pliku <K>\ustawienia.toml - uruchom zainstaluj.cmd ...`; 100 -> 100 |
| P1b | brak pliku, bez opcji | kod 0; jak P1a |
| P1c | brak pliku i brak `wersja_biezaca.txt` (zostaje `instalacja.json`), bez opcji | kod 0; jak P1a (instalacja rozpoznana po `instalacja.json`) |
| P1d | brak pliku instalacji, `ustawienia.toml` podlozony w katalogu wersji, jak skrot | kod 0; `ustawienia BRAK`, foldery `brak` - pliku z katalogu wersji okno nie czyta |
| P1e | pomiar (`narzedzia\pomiar_skanu\pomiar_skanu.py <skan> --bez-plytki`) w stanie P1d | kod 2; `blad: ustawienia: brak pliku ustawien instalacji <K>\ustawienia.toml - uruchom zainstaluj.cmd ...`; bez Traceback |
| P1f | pomiar, brak pliku instalacji | kod 2; komunikat jak P1e |
| P2a | `baza = "dane/stanowisko.sqlite"` (wzgledna), bez opcji | kod 1; `BLAD: katalog sesji <K>\wersje\9.9.9\program\dane\dzien_skanera lezy w katalogu wersji programu (...) ... CO ZROBIC: uruchom <K>\Dzien_skanera.cmd ... albo popraw ... [sciezki] baza`; 0 nowych sesji, 100 -> 100 |
| P2b | baza wzgledna, jak skrot | kod 0; sesja w `<K>\dane\dzien_skanera`; ustawienia instalacji |
| P3a | baza bezwzgledna wskazujaca do `<K>\wersje\9.9.9\program\dane`, bez opcji | kod 1; BLAD jak P2a |
| P3b | to samo, jak skrot | kod 0; sesja w `<K>\dane\dzien_skanera` |
| P4a | jak skrot + `--dane <K>\wersje\moje` | kod 1; BLAD; 100 -> 100 |
| P4b | jak skrot + `--dane dane\dzien_skanera` (wzgledne) | kod 1; BLAD (katalog policzony od katalogu programu) |
| P4c | jak skrot + `--dane <K>\WERSJE\X` (wielkie litery) | kod 1; BLAD |
| P4d | jak skrot + `--dane <K>\dane\..\wersje\y` | kod 1; BLAD |
| P4e | jak skrot + `--dane <K>\wersje_obok\s` | kod 0; sesja w `<K>\wersje_obok\s` (sasiad o podobnej nazwie nie jest odrzucany - poprawnie) |
| P4f | `--ustawienia <K>\nie_ma.toml`, plik instalacji dobry | kod 0; ustawienia z pliku instalacji; `UWAGA: ustawienia: nie_ma.toml: brak pliku ...` |
| P5a | plik instalacji z BOM, jak skrot | kod 0; sesja w `<K>\dane\dzien_skanera`; `ustawienia <K>\wersje\9.9.9\program\ustawienia.przyklad.toml; foldery obserwowane: C:\Aidite\Scandata`; `UWAGA: ... blad skladni TOML` - uwaga N1 |
| P5b | plik z BOM, pomiar bez opcji | kod 2; 1 wiersz `blad: ustawienia: ustawienia.toml: blad skladni TOML ...` |
| P6a | modul 0.3.1 wolany jak nowy skrot + `--zamknij-po 5` | kod 2; `error: unrecognized arguments: --zamknij-po 5` (zgodne z instrukcja punkt 4) |
| P6b | modul 0.3.1 wolany jak nowy skrot, `--nowa --bez-kontroli`, okno 12 s, potem zatrzymane | sesji w `<K>\dane\dzien_skanera` 10 -> 11; pliki w `wersje` 100 -> 100 |
| P6c | proba kontrolna: modul 0.3.1 wolany jak skrot z rundy 1 (bez `--dane`) | pliki w `wersje` 100 -> 103 (3 pliki w `wersje\0.3.1\program\dane`) - stan sprzed poprawki P2 |

Razem 23 proby (P0a-P6c): 22 zgodne z oczekiwaniem poprawek, 1 (P5a) = uwaga N1. Katalogow
`__pycache__` w `<K>\wersje` po probach: 0.

Wstrzykniecia (kazde cofniete `git checkout -- .`, po kazdym `git status --short` pusty; log `wstrzykniecia_r2.log`):

| Nr | Poprawka | Co zepsuto | Padlo testow |
|---|---|---|---|
| W1 | P1 | `katalog_instalacji` znowu wymaga `ustawienia.toml` | 4 z 20 |
| W2 | P1 | `sprawdz_katalog_sesji` niczego nie odrzuca | 2 z 20 |
| W3 | P1 | bez pliku instalacji okno znowu czyta wzor z katalogu wersji | 2 z 20 |
| W4 | P2 | wzor `Dzien_skanera.cmd` bez `--dane` | 3 z 20 |
| W5 | P1 | `wybierz_sesje` nie wola `sprawdz_katalog_sesji` | 2 z 20 |
| W6 | P1 | `pomiar_skanu.py` bez kontroli pliku instalacji | 1 (`test_p1_pomiar_...`) |
| W7 | `ui_test` | decyzje znowu w katalogu programu | 1 (`test_okno_testowe_decyzje_...`) |
| W8 | D1 | `WYMAGANE` bez `wzory/Dzien_skanera.cmd` | 1 (`test_d1_...`) |
| W9 | D3 | instrukcja ramki: `{"protokol": 1` | 1 (`test_d3_...`) |
| W10 | D2 | `zainstaluj_ramke.sh`: `umask 022` | 1 (`test_d2_...`) |
| W11 | D5 | naglowek "Typowe bledy" bez znacznika | 1 (`test_instrukcja_kazdy_krok_...`) |
| W12 | D4 | instrukcja ramki bez ostrzezenia o karcie zastanej | 1 (`test_d4_d6_...`) |

Razem 12 wstrzykniec w 7 przebiegach (W6-W8 razem, W9-W12 razem - kazde ma wlasny, inny test): wykryte 12 z 12.

Zgodnosc z O2 i O3 (log `zgodnosc_r2.log`): na kopie O4 (373cd79) nalozone pliki galezi `e3/o2` (2c79335, 15 plikow) i `e3/o3`
(10a6e22, 14 plikow) - stan jak po scaleniu trzech paczek; potem `git reset --hard HEAD`, `git status --short` pusty.

| Polecenie | Wynik |
|---|---|
| `testy/test_o4_instalacja_dzien_skanera.py testy/test_o4_test_led.py testy/test_o4_ramka_rpi.py testy/test_zbuduj_wydanie.py testy/test_ramka.py testy/test_okragle_ramka.py` | 178 passed, 0 failed, 80 s |
| `testy/test_okragle_wydanie.py testy/test_instalacja.py -k "samokontrola or paczki or zip or p6 or skrypt"` | 30 passed, 0 failed, 91 odfiltrowanych, 38 s |

Testy O4 z liczbami na sztywno (6 wzorow skrotow, 7 skryptow `.cmd`, 4 pliki `ramka/rpi`, 19 gniazd ukladu `wieczorna` w
`test_led`) przechodza z `ramka/kalibracja.py` i `samokontrola.py` z O2 / O3; testy O3 liczace pliki paczki (38 plikow
modeli w liscie i w prawdziwym ZIP) przechodza z plikami O4. Pelny pytest polaczenia trzech paczek = przebieg koordynatora.

## 3. Kryteria zlecenia i 10 punktow z sekcji 6 rundy 1

Liczby w tej sekcji odczytane z logow wykonawcy `robocze\o4\` (plik:wiersz); instalacje probne sa juz usuniete, wiec
status "potwierdzone logiem wykonawcy" oznacza: log istnieje, jest spojny i pokazuje dokladnie te liczbe.

| Nr | Kryterium | Status |
|---|---|---|
| 1 | Test w ukladzie instalacji (bez poprawki pada) | potwierdzone wlasna proba: `test_o4_instalacja_dzien_skanera.py` 20 passed; W1-W5 wykryte; proby P0a-P4f |
| 1 | Proba na instalacji probnej z galezi | potwierdzone logiem wykonawcy: paczka `0.3.2-o4` z commita 5b62aa8 (`r2_inst_1.log:2, 6`); `Dzien_skanera.cmd` zalozony i bajtowo rowny wzorowi (`r2_sprawdz_inst.json`: 6 skryptow, 6 x zgodne); okno przez skrot kod 0, sesja `<instalacja>\dane\dzien_skanera\...`, folder obserwowany z ustawien instalacji (`r2_k12.log:3-4`); 9 uruchomien okna z kodem 0 = 9 sesji w danych instalacji (`r2_k12.log:124-131` 8 szt., `r2_k1b.log:3` 1 szt.), `program\dane` nie istnieje (`r2_k12.log:76`, `r2_k1b.log:38`); listy plikow katalogu wersji przed / po oknie i po pomiarach identyczne (28887 wierszy, `fc` brak roznic: `r2_k12.log:72-75`, `r2_k1b.log:36-37`; 0 katalogow `__pycache__` w `program`); samokontrola po probach ZIELONA, `147 z 147, plikow nadmiarowych 0`, kod 0 (`r2_k12.log:98-100`). Doprecyzowanie: z 9 sesji 3 powstaly w stanach celowo zepsutych (2 x brak pliku ustawien, 1 x BOM), 6 w stanie poprawnym; sterownik wolal `wybierz_sesje(..., plik_ustawien=plik_ust)` (`dzien_skanera_proba.py:58`) |
| 2 | Pomiar szczegolowy na instalacji, 2 drogi, kod 0 | potwierdzone logiem wykonawcy: `Polecenie.cmd narzedzia\pomiar_skanu\pomiar_skanu.py` kod 0, 52,8 s (`r2_k12.log:39-40`), pierwszy wiersz `ustawienia: <instalacja>\ustawienia.toml` (`r2_pomiar_polecenie_ekran.txt:1`); polecenie zlozone jak przycisk: kod 0, 53,1 s (`r2_k12.log:42`); prawdziwy przycisk w oknie: kod 0, 51,4 s i 53,5 s, interpreter `wersje\0.3.2-o4\venv\Scripts\python.exe` (`r2_ds\wynik.json`, `r2_ds2\wynik.json`). Test sciezki ustawien: W6 wykryte |
| 3 | `test_led`: konfiguracja, brak biblioteki = kod 2 | potwierdzone wlasna proba w rundzie 1; plik bez zmian w rundzie 2; `test_o4_test_led.py` przechodzi (w 354 passed) |
| 4 | Pliki `ramka/rpi`, testy, `bash -n`, znacznik, katalog w paczce | potwierdzone: testy `test_o4_ramka_rpi.py` 18 passed (0 skipped, czyli bash byl); znacznik takze w 2 sekcjach koncowych (D5); w paczce probnej i po instalacji 4 pliki `ramka/rpi`, 0 znakow CR, rowne repo, w sumach, instrukcja ramki jest (`r2_sprawdz_inst.json`: `ramka_rpi`, `zip_ramka_rpi`, `instrukcja_ramki`) |
| 5 | 6 rozbieznosci A3 | potwierdzone przegladem (runda 1) + luka P2 zamknieta. Rozmiary z paczki probnej: ZIP 447,3 MB (instrukcja: "ok. 445 MB"), katalog wersji 1388,9 MB ("ok. 1,4 GB"); kroki [1/9]-[9/9]; katalog po kodzie 10 jak w instrukcji (`r2_inst_1.log:62-71`) |
| 6 | Instalacja probna 10 -> 0, sumy, samokontrola, aktualizacja z 0.3.1 i powrot | potwierdzone logiem wykonawcy: `KOD_INSTALACJA_1=10`, `KOD_INSTALACJA_2=0` (`r2_inst_1.log:60, 116`); `zgodne 227 z 227` (`:15, 76`); `147 z 147, plikow nadmiarowych 0` (`:52, 109, 138`); `SAMOKONTROLA: ZIELONA (ok 14, ostrzezenia 7)`, kod 0 (`:139-140`); 6 skryptow. Aktualizacja (`r2_akt.log`): 0.3.1 10 -> 0 (`:52, 95`; 5 skryptow), aktualizacja do probnej kod 0 (`:154`; 6 skryptow, skrot = wzor `:163`), powrot kod 0 (`:219-220`; 6 skryptow zostaje), ponowne `zainstaluj.cmd` 0.3.1 kod 0 (`:323`), powrot do probnej kod 0 (`:373`), okno skrotem kod 0 (`:404-405`). To samo w katalogu ze spacja: 10 -> 0, okno i pomiar kod 0 (`r2_spacja.log:49, 92, 128-142`) |
| 7 | Pelny pytest 0 failed; wstrzykniecia min. 4 | pelny pytest: wg logu wykonawcy `pytest_66dd543.log` (ostatni wiersz `2335 passed, 9 skipped, 1 warning in 1969.56s`, `KOD_PYTEST=0`; commit 66dd543 rozni sie od 5b62aa8 i od HEAD 373cd79 tylko raportem paczki - sprawdzone `git log --stat`); nie powtarzany. Wstrzykniecia: moje 12 z 12 w rundzie 2 (+ 7 z 9 w rundzie 1) |

10 punktow z sekcji 6 rundy 1:

| Nr | Punkt | Wynik wg logow |
|---|---|---|
| 1 | Powrot do 0.3.1: 6 skryptow, okno bez `--zamknij-po`, 0 nowych plikow w `wersje\0.3.1`, to samo po ponownym `zainstaluj.cmd` 0.3.1 | zrobione: `r2_akt.log:226-237, 272-278, 326-343`; 3 listy `r2_akt_w031_*` identyczne (28873 wiersze) |
| 2 | P1 na instalacji: brak pliku, baza wzgledna | zrobione: `r2_k12.log:102-115` (+ BOM `:118-120`) |
| 3 | `QT_QPA_PLATFORM=offscreen`, `< NUL` | zrobione (`r2_krok_k12.cmd`) |
| 4 | Sterownik z `plik_ustawien=plik_ust` | zrobione (`dzien_skanera_proba.py:58`) |
| 5 | 0 nowych plikow w katalogu wersji, takze `__pycache__`; samokontrola | zrobione (kryterium 1); porownanie list nazw, tresc programu pokrywa wiersz sum samokontroli |
| 6 | Interpreter i ustawienia przycisku; `pomiar_skanu.cmd` z plikiem nieistniejacym | zrobione: interpreter srodowiska wersji, `--ustawienia <instalacja>\ustawienia.toml` (`r2_ds2\wynik.json`); `pomiar_skanu.cmd`: interpreter srodowiska wersji i ustawienia instalacji (`r2_k12.log:46, 58`), ale dla pliku, ktorego nie ma, narzedzie konczy sie sladem wyjatku `ValueError` i kodem 0 (`:48-69`) - zachowanie czesci liczacej sprzed paczki, POTRZEBUJE 5 wykonawcy |
| 7 | `ramka/rpi` 4 pliki bajt w bajt, instrukcja, liczba plikow programu | zrobione: 4 pliki, CR 0; plikow programu 148 (147 objetych sumami + plik sum); `modele_plytek` 38 plikow w ZIP i po instalacji, 10 katalogow |
| 8 | Po aktualizacji skrot = wzor; sesje 0.3.1 w katalogu wersji nietkniete | zrobione: `r2_akt.log:163`; `r2_akt_dane031_przed / po_akt / koniec` identyczne (porownanie nazw) |
| 9 | Katalog instalacji ze spacja | zrobione: `r2_spacja.log` (10 -> 0, 227 z 227, 147 z 147, 6 skryptow, okno kod 0 z sesja w `...\Stanowisko proba\dane\dzien_skanera`, pomiar kod 0) |
| 10 | Rozmiary i katalog po kodzie 10 | zrobione (kryterium 5) |

Doprecyzowania do liczb wykonawcy (bez wplywu na werdykt): (a) "9 z 9 sesji" - patrz kryterium 1; (b) "147 z 147" to
pliki objete sumami, plikow programu jest 148; (c) kontrola wolnego miejsca `(Get-PSDrive C).Free` zwrocila w logach 0
(`r2_inst_1.log:4, 12`), wiec prog "ponizej 10 GB nie instaluj" w kroku instalacji glownej faktycznie nie byl sprawdzany tym
poleceniem - instalator sam podal wolne 34521 MB (`:24`), a w `r2_akt.log:3` uzyto juz `DriveInfo` (29,01 GB); (d) przy
probie skrotu na 0.3.1 `taskkill` zwrocil "Access denied" (`r2_akt.log:269-270`) i sterownik zatrzymal tylko `cmd.exe` -
okno 0.3.1 moglo zyc dluzej niz planowano; kody i listy plikow sa mimo to spojne, a katalogu `t0\o4` juz nie ma.

## 4. Zakres plikow i zasady

- Runda 2: 15 plikow, wszystkie z listy `o4.md` albo wskazane w `o4-b2.md` (`README.md` wiersze 119 i 152, `ui_test.py`).
  `README.md`: zmienione dokladnie 2 wiersze (119 i 152; 2 dodane, 2 usuniete). `ui_test.py`: 11 wierszy dodanych,
  2 usuniete (funkcja `plik_decyzji_domyslny` + domyslna wartosc parametru). Nie ruszono: plikow nietykalnych,
  `aplikacja.py`, `scanner.py`, `ustawienia.py`, `samokontrola.py`, `import_decyzji.py`, `Ramki/etap3/**`.
- Zgodnosc z O2 (2c79335, 15 plikow) i O3 (10a6e22, 14 plikow): czesc wspolna list plikow z O4 (26 plikow) = 0 i 0
  (O2 z O3 tez 0); proba z nalozonymi plikami obu galezi: 178 + 30 passed, 0 failed (sekcja 2). `README.md` programu ramki (O2) nie odsyla jeszcze do nowej instrukcji - POTRZEBUJE 1 wykonawcy.
- Konce linii (`git ls-files --eol`): `Dzien_skanera.cmd` CRLF; `README.md` i `ui_test.py` CRLF jak przed zmiana (styl
  zastany, bez mieszania); pozostale 12 plikow LF; `ramka/rpi/*` 4 pliki LF.
- ASCII: w dodanych wierszach rundy 2 znaki spoza ASCII tylko w plikach, ktore mialy je wczesniej (`README.md` 2 z 2
  wierszy, `dzien_skanera.py` 1 z 13 - tytul okna dialogowego); w pozostalych 13 plikach 0 (w tym testy 0 z 206, raport
  paczki 0 z 287).
- Dane osobowe: 0 trafien w diffie rundy 2. Duze dane: brak. Brak zmiany schematu bazy i nowych pakietow. W dodanych
  wierszach testow 0 x `skip` / `xfail`.
- Kopia `rec-o4`: po probach `git status --short` pusty, HEAD 373cd79. Worktree wykonawcy, repo glowne, `t0\s1` i
  `robocze\o4` tylko czytane. Procesy python po mojej pracy: 0 wlasnych (wszystkie przebiegi czekaly na koniec procesu; 2 okna modulu 0.3.1 zatrzymane po 12 s i potwierdzone; na koncu, 13:45: dziala 1 proces python toru 4 koordynatora i znany proces-wydmuszka PID 12560 bez sciezki - nie moje). Blokada toru 3 zwolniona (13:43:24).

## 5. Do decyzji wlasciciela

1. Okno "Dzien skanera" w instalacji bez dzialajacego pliku ustawien. Dzis: BRAK pliku = okno startuje bez ustawien, nie
   obserwuje zadnego folderu i mowi o tym na czerwono (przyjete domyslnie przez wykonawce; oceniam jako bezpieczne); plik Z
   BLEDEM (np. BOM) = okno startuje na wzorze i obserwuje `C:\Aidite\Scandata` (uwaga N1). Do wyboru: (a) zostawic,
   (b) plik z bledem traktowac jak brak pliku (zalecane, 1 wiersz), (c) w obu stanach odmawiac startu z komunikatem i
   kodem != 0 (najostrzejsze; odbiera tryb awaryjny "zbieraj pliki bez ustawien").
2. Skrot zawsze podaje `--dane <instalacja>\dane\dzien_skanera` (wariant domyslny z rundy 1): sesje ze skrotu sa tam
   nawet wtedy, gdy ktos przeniesie baze w ustawieniach; droga `Polecenie.cmd -m stanowisko.dzien_skanera` idzie za
   katalogiem bazy. Opisane w raporcie paczki (14.11 p. 3) - do wiadomosci.
3. POTRZEBUJE wykonawcy poza zakresem paczki: `import_decyzji.py` (N3), `pomiar_skanu.py` dla pliku skanu, ktorego nie ma
   (slad wyjatku, kod 0 przez `pomiar_skanu.cmd`), `ramka/README.md` (odeslanie do nowej instrukcji - paczka O2), strona
   `.html` instrukcji ramki. Ponawianie `os.rename` w instalatorze (N4) - do rozwazenia przed instalacja na laptopie z
   antywirusem.
