# Raport recenzenta - paczka E3-R1 (przelacznik "ramki wylaczone"), PR #65, runda 1

- Data: 26.11.2026 (PC, konto 3, zlecenie rec-r1-r1).
- Zakres: commity R1 na `origin/e3/r1` po scaleniu `e3/i1`: `711963a..51d3438` (5 commitow: e696878 testy, ec3e838 kod,
  4a93fd1 opisy, 25e82ff zrzuty, 51d3438 raport). Dodatkowo samo scalenie 711963a (= `origin/e3/u1b` f170218 + `origin/e3/i1`
  2640471). U1a / U1b / I1 maja wlasne recenzje - nie powtarzane.
- Metoda: najpierw wlasny przeglad diffu `git diff 711963a 51d3438` (kod, testy, opisy, instrukcja, zrzuty), potem proby we
  wlasnej kopii `<PC-katalog>\qc-wt\rec-r1` (detached 51d3438, `ustawienia.toml` = wzor); raport wykonawcy przeczytany na koncu.
- Co uruchomiono (wszystko jako procesy odlaczone z przynet `robocze\rec-r1-r1\przyneta\`, pod `ciezki.ps1` tor 4; 0 uruchomien
  przez powloke / skrot): testy okna i instalatora oraz R1 na HEAD (3 biegi), wlasne proby celowane (9), 15 wstrzykniec bledu,
  proba aktualizacji na prawdziwych paczkach 0.3.9-i1b -> 0.3.9-rc1 (bez Pythona w PATH). Pelnego pytest nie powtarzalem
  (log wykonawcy). Logi: `<PC-katalog>\konto3\robocze\rec-r1-r1\logi\`.

## 0. Werdykt

**Do scalenia po poprawkach.** B 0 / P 1 / D 3.

Kod R1 robi to, co zlecenie: przy `false` zero prob polaczenia, neutralny pasek, samokontrola OK, nic poza ramkami nie jest
wyciszane; brak klucza i `true` = zachowanie dotychczasowe; aktualizacja nie rusza pliku ustawien (sprawdzone takze na
prawdziwych paczkach). Scalenie `e3/i1` nie zgubilo zmian. Jedyna P to staly napis na ekranie porannym, ktory przy ramkach
wylaczonych mowi nieprawde - poprawka wymaga pliku spoza listy zlecenia (wykonawca zglosil to jako POTRZEBUJE).

## 1. Uwagi

| nr | waga | plik:linia | scenariusz | propozycja |
|---|---|---|---|---|
| P1 | P | `Ramki/stanowisko/stanowisko/ui/ekran_rano.py:377` (tekst `ui/napisy_rano.py:69`) | Instalacja na pokaz (`wlaczone = false`), tryb Poranek: pod numerem kuwety stoi staly napis "Na ramce porannej swieca gniazda biezacej kuwety." (widac na zrzucie `rano_ramki_wylaczone_1536x864.png`, obejrzany). Ramki nie ma, a R1 usunal komunikat "Ramka poranna nie jest podlaczona", ktory dotad temu przeczyl - teraz nic na ekranie nie prostuje falszywej informacji w sciezce technika (i szefa na pokazie). | Ukryc `self.na_ramce`, gdy `stan.ramki is None or stan.ramki.wylaczone` (albo gdy `not stan.rano.ramka`) + asercja w `test_okno_pasek_ramki_wylaczone_neutralny_wieczor_i_rano` (rano: napis niewidoczny) i w tescie "jak dotad" (z ramka: widoczny). Wymaga dopisania `ui/ekran_rano.py` do listy plikow R1 - decyzja koordynatora. |
| D1 | D | `Ramki/stanowisko/testy/test_ramki_wylaczone.py:220` | Nowy plik ma 1 wiersz z litera spoza ASCII (napis "wylaczone" z polskimi literami w asercji) - zasada: nowe pliki ASCII. | Porownywac tylko z `NR.RAMKI_WYLACZONE` albo zapisac `"wy\u0142\u0105czone"`. |
| D2 | D | `Ramki/stanowisko/instrukcje/instalacja_i_aktualizacja.md:38-39`, `ui/napisy_rano.py:174-175` (`RAMKI_WYLACZONE_OPIS`) | "Aby wlaczyc ramki ... wpisz `wlaczone = true`": w pliku jest juz wiersz `wlaczone = false`. Technik, ktory dopisze drugi wiersz, dostaje program, ktory nie startuje: zmierzone - `BladUstawien: ustawienia.toml: blad skladni TOML: Cannot overwrite a value (at line 98...)`. | "zmien w wierszu `wlaczone = false` slowo `false` na `true`" (instrukcja i podpowiedz paska). |
| D3 | D | `Ramki/stanowisko/testy/test_instalacja_i1.py:238-240`, galaz `instalacja/instalator.py:625-626` | Zmiana testu usunela jedyna asercje galezi "ta wersja programu nie ma przelacznika ramek" (program z paczki bez klucza); zostala tylko asercja przeciwna (`not in`). Galaz jest dzis praktycznie martwa (instalator i program ida w jednej paczce), ale nietestowana. | Test z paczka, w ktorej `SCHEMAT["ramki"]` nie ma `wlaczone` (jak stary test, odwrotnie), albo usunac galaz. |

## 2. Wlasne proby

| # | polecenie (log w `robocze\rec-r1-r1\logi\`) | wynik |
|---|---|---|
| 1 | `git diff --name-only` merge-base b856b9e..f170218 (U1) i ..2640471 (I1); porownanie blobow kazdego zmienionego pliku z 711963a | U1: 56 plikow, I1: 22, wspolne 0; 78 z 78 plikow w scaleniu = stan swojej galezi (`styl.py` usuniety w U1b - w scaleniu tez brak). Scalenie nic nie zgubilo. `origin/e3/u1b` = f170218, `origin/e3/i1` = 2640471 (aktualne galezie = rodzice scalenia). |
| 2 | pytest `test_okno_instalatora.py test_instalacja_i1.py test_instalacja.py test_zbuduj_wydanie.py` na 51d3438 (`a1_instalator.log`) | **150 passed**, 0 failed, 149 s |
| 3 | pytest `test_ui_okno.py test_ui_poranek.py test_ui_wieczor.py test_ui_rano.py test_aplikacja_rano.py` (`a2_okno.log`) | **247 passed**, 0 failed, 301 s |
| 4 | pytest `test_ramki_wylaczone.py test_samokontrola.py test_kontroler_api.py` (`a3_r1.log`) | **255 passed**, 0 failed, 96 s |
| 5 | wlasne proby `test_rec_r1_proby.py` (plik tymczasowy, zachowany w `robocze\rec-r1-r1\skrypty\`; `b_proby.log`) | **9 passed**: (a) roznicowo atrapa "bez ramek" vs "wylaczone", wieczor i rano, ze skanerem bez folderu, pula `brak_folderu`, silnik nie startuje, `baza_zajeta`: te same komunikaty (3 x poziom blad), te same role pola skanera / puli / analizy (`stan_uwaga` x2), ta sama lista bledow, licznik "Bledy programu: 3" w obu, 1 niezapisany w obu; jedyna roznica - rano wariant "bez ramek" ma dodatkowo `ramka_poranna` (info), "wylaczone" nie; (b) prawdziwa `Aplikacja` z `wlaczone = false` + usuniety folder skanera: komunikaty identyczne z wariantem bez ramek, w tym `folder_skanera` (blad); atrapa TCP: 0 polaczen, 0 obiektow `KlientRamki`; (c) samokontrola `false` vs `true` (`--bez-sieci`) ze zlym folderem skanera: rozne tylko 2 wiersze ramek, `folder_skanera` BLAD w obu, kod wyjscia 1 w obu; (d) wzor ustawien z `main` (b856b9e, bez klucza) wczytany nowym programem: `wlaczone` True; (e) `wlaczone = 0` / `"false"` / `False` / `nie`: 4 z 4 = `BladUstawien` z czytelnym tekstem ("oczekiwano bool, jest 0 (int)" itd.). |
| 6 | 15 wstrzykniec (`skrypty\wstrzyk.py`, kazde = 1 podmiana w kopii, testy celowane, potem `git checkout`; `W*.log`, `przebieg.txt`) | **15 z 15 wykrytych** (kod pytest 1): W1 `ramki_wlaczone` zawsze True - 5 failed `test_ramki_wylaczone` (W1b) + 1 failed samokontrola; W2 `DOMYSLNE_NOWYCH wlaczone False` - 4 failed (w tym aktualizacja instalatora); W3 Aplikacja ignoruje klucz - 1; W4 `Indicate.z_ustawien` bez wczesnego wyjscia - 1; W5 komunikat `ramka_niedostepna` mimo wylaczenia - 2; W6 rola `stan_uwaga` - 1; W7 "Test LED" widoczny - 1; W8 samokontrola probuje laczyc - 1; W9 `main --atrapa` nie czyta klucza - 1; W10 instalator wpisuje `true` - 2; W11 wzor `wlaczone = false` - 1; W12 `wylacz_ramki` bez stanu - 4; W13 pasek bez galezi "wylaczone" - 1; W14 Aplikacja bez `wylacz_ramki()` - 1; W15 instalator nadpisuje istniejacy plik ustawien - 2. Po serii kopia czysta (`git status`: tylko moj plik prob). |
| 7 | proba aktualizacji na prawdziwych paczkach (`skrypty\proby_rec.py`, `proby_rec.jsonl`): `okno_instalatora.py --bez-okna` Pythonem z paczki, PATH bez Pythona; najpierw 0.3.9-i1b (SHA-256 68cfb6f5...), potem 0.3.9-rc1 (SHA-256 380f0e53..., = paczka wykonawcy) do `robocze\rec-r1-r1\proba` | i1b: kod 0 (63,9 s), plik bez wiersza `wlaczone` (program i1b nie zna klucza); rc1 (aktualizacja): **kod 0** (60,0 s), `wersja_biezaca` 0.3.9-rc1, `ustawienia.toml` SHA-256 przed = po (`fe022d43b375651c`), 0 wierszy `wlaczone`; samokontrola po aktualizacji `--bez-sieci` i z siecia: ZIELONA (ok 14, ostrzezenia 7), wiersze ramek jak przed R1 (OSTRZEZENIE "pominieto" / "nieobecna ... gaierror"), 0 bledow ustawien (brak kodu 7); start prawdziwy `Stanowisko.cmd --zamknij-po 8` (offscreen): **kod 0**, log: 3 wpisy WARNING o ramkach (brak kalibracji, zgaszenie W i P nie doszlo) = program laczy sie z ramkami jak dotad. |
| 8 | podmiana: drugi wiersz `wlaczone = true` pod `[ramki]` obok `wlaczone = false` (`skrypty\dubel.py`) | `BladUstawien ... Cannot overwrite a value (at line 98, column 17)` (D2) |
| 9 | obejrzenie zrzutow `wieczor_ramki_wylaczone_1536x864.png`, `rano_ramki_wylaczone_1536x864.png` | Pasek "Ramki: wylaczone" zwyklym kolorem, kropka pusta (jak "Analiza: nic nie czeka"), bez "Test LED", strefa "Brak pytan i komunikatow"; rano widoczny napis "Na ramce porannej swieca gniazda biezacej kuwety." (P1). |

Liczby wykonawcy niesprawdzone przeze mnie: pelny pytest 2 x 2683 / 9 / 0 (odczytalem tylko wiersze podsumowania w
`robocze\r1\logi\pytest_pelny*.log`: zgodne, 0 wierszy FAILED/ERROR), regresja na e696878 17 failed / 2 passed (wiersze
podsumowania logow zgodne: 13 + 4 failed, 2 passed), nowa instalacja rc1 z `wlaczone = false` i samokontrola ZIELONA ok 16 /
ostrz. 5 (plik `robocze\r1\proba\ustawienia.toml`: 1 wiersz `wlaczone = false` z komentarzem - odczytany; wyjscie samokontroli z
siecia: oba wiersze ramek OK "wylaczone w ustawieniach" - odczytane), start atrapy, Dzien skanera, starter (wg wykonawcy).

## 3. Kryteria zlecenia r1

| # | kryterium | ocena |
|---|---|---|
| 1 | brak klucza = `true`, stare instalacje i aktualizacja bez zmian, bez kodu 7 | potwierdzone wlasna proba (2.5d, 2.7: aktualizacja i1b -> rc1 na prawdziwych paczkach, plik bajt w bajt, samokontrola zielona, start kod 0, ramki jak dotad; W2 wykrywa zmiane domyslnej) |
| 2 | `false`: 0 prob polaczenia, brak szukania ramek | potwierdzone wlasna proba (2.5b: licznik TCP 0, 0 klientow; W3, W4, W14 wykrywane) |
| 3 | `false`: pasek "Ramki: wylaczone" neutralnie, bez wpisu na liscie bledow, bez komunikatow "ramka nieobecna" w strefie pytan | potwierdzone wlasna proba (2.5a, zrzuty; W5, W6, W7, W12, W13) |
| 4 | `false`: samokontrola - wiersz ramek neutralny | potwierdzone wlasna proba (2.5c; W8). Poziom OK ("neutralny" przyjety przez wykonawce jako OK - styk z instalatorem zna OK/OSTRZEZENIE/BLAD) |
| 5 | `false`: reszta programu bez zmian; przelacznik nie wycisza innych bledow | potwierdzone wlasna proba (2.5a-c: skaner, pula, silnik, baza dalej widoczne, identycznie jak bez ramek) i przegladem (jedyny nowy warunek poza ramkami - brak); skan / analiza / Excel - przegladem i testami okna 2.3 |
| 6 | `false`: bez mylacych napisow na ekranie | **niespelnione w calosci** - P1 (staly napis o ramce porannej) |
| 7 | `true`: nic sie nie zmienilo, w tym komunikaty o braku ramki | potwierdzone wlasna proba (2.4 testy kontrolera i okna 0 failed; 2.7 aktualizacja: ostrzezenia ramek jak dotad) i przegladem (warunek `not self._ramki_wylaczone` tylko przy `wylacz_ramki`) |
| 8 | instalator: nowa instalacja z okna wpisuje `false` | potwierdzone wlasna proba (W10 wykrywane; testy 2.2) i przegladem (`kreator.polecenie_instalacji` dodaje `--ramki-wylaczone` tylko przy nowej instalacji; `ustawienia_ze_wzoru` podmienia wartosc w wierszu wzoru, bez dubla); na paczce - wg wykonawcy, plik `ustawienia.toml` instalacji wykonawcy odczytany |
| 9 | instalator: aktualizacja nie rusza `ustawienia.toml` | potwierdzone wlasna proba (2.7 SHA-256 przed = po; W15 wykrywane) |
| 10 | `ustawienia.przyklad.toml` z kluczem i komentarzem jak wlaczyc | potwierdzone przegladem (wiersz 97, CRLF jak reszta pliku; W11 wykrywane) |
| 11 | testy padaja po zepsuciu kodu | potwierdzone wlasna proba (15 z 15 wstrzykniec) |
| 12 | pelny pytest 0 failed | wg wykonawcy, niesprawdzone (podsumowania logow zgodne) |
| 13 | paczka probna, instalacja bez Pythona w PATH, start, Dzien skanera | czesciowo potwierdzone wlasna proba (2.7: ta sama paczka rc1, aktualizacja kod 0, start kod 0); nowa instalacja, atrapa, Dzien skanera - wg wykonawcy |
| 14 | zrzuty wieczor i rano | potwierdzone (obejrzane, 2 PNG 141 145 B i 132 622 B) |
| 15 | scalenie `e3/i1` bez utraty zmian, testy okna i instalatora 0 failed | potwierdzone wlasna proba (2.1-2.3) |

## 4. Zakres plikow i zasady

- Pliki R1 (20): kod `ustawienia.py`, `indicate.py`, `samokontrola.py`, `aplikacja.py` (start polaczenia), `ui/czesci.py` +
  `ui/napisy_rano.py` (pasek), `kontroler_api.py`; `ustawienia.przyklad.toml`; 5 opisow modulow; instrukcja instalacji; 3 pliki
  testow; raport; 2 PNG. `kontroler_api.py` nie byl wymieniony z nazwy - wykonawca opisal to jako odstepstwo ("miejsce startu
  polaczenia": `podlacz_ramki`, plus warunek komunikatu porannego). Zmiana addytywna (pole z domyslna, metoda, jeden warunek) -
  uznaje za mieszczaca sie w "miejsce startu polaczenia z ramka"; bez uwagi. Kod `instalacja/` bez zmian (mechanizm z I1).
- Nietykalne (`match.py`, `inspect.py`, `plate.py`, `synth.py`, `uklad.py`, `porownaj.py`, `session*.py`, `silnik.py`, `scanner.py`,
  `modele_plytek/**`, schemat bazy, `ramka/`): 0 zmian (grep listy zmienionych plikow).
- Testy przed kodem: e696878 zawiera tylko 3 pliki testow, kod w ec3e838 - potwierdzone `git show --stat`.
- Konce linii: nowe pliki LF (`git ls-files --eol`: test, raport - i/lf); istniejace w swoim stylu (`ustawienia.py`,
  `ustawienia.przyklad.toml` dalej i/crlf, bez mieszania). ASCII: dodane wiersze ASCII poza `ui/napisy_rano.py` (plik istniejacy,
  napisy okna z polskimi literami - styl pliku) i 1 wierszem nowego testu (D1).
- Dane osobowe: brak (osoby "Technik A", "Anna Proba", kuwety z danych atrapy). Duze dane: brak (PNG 132-141 KB).
- Commity: 5, przedrostek `E3-R1`, po polsku bez diakrytykow, stopka `Co-Authored-By: Claude Opus 5.5` w 5 z 5.

## 5. Do decyzji wlasciciela / koordynatora

1. P1 wymaga zgody na `ui/ekran_rano.py` (poza lista plikow zlecenia r1). Poprawka to kilka wierszy + test; bez niej pokaz
   28.11 pokaze rano zdanie o swiecacych gniazdach ramki, ktorej nie ma.
2. Aktualizacja zostawia plik ustawien bajt w bajt (zgodnie ze zleceniem). Skutek zmierzony w 2.7: jesli na laptopie przed sobota
   zainstalowano juz 0.3.9-i1 / i1b (program bez klucza), to aktualizacja do rc1 zostawi ramki WLACZONE (ostrzezenia "ramka
   nieobecna" w samokontroli z siecia, wpisy WARNING w logu). Na laptop bez ramek: instalacja od nowa albo reczne
   `wlaczone = false` w `[ramki]`. Instrukcja mowi tylko, jak ramki wlaczyc.
3. Instalacja z wiersza polecen (`zainstaluj.cmd`, bez okna) nie podaje `--ramki-wylaczone` - nowy plik dostaje `wlaczone = true`
   ze wzoru. Zgodne ze zleceniem ("instalator okienkowy"); do wiadomosci.
4. Poza zakresem R1, z obejrzenia zrzutu porannego: pole "Excel: niedostepny" na pasku ma wyrozniona ramke (styl uwagi) - na
   laptopie bez skonfigurowanego Excela bedzie widoczne na pokazie.
