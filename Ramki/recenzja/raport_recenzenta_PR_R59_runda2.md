# Raport recenzenta PR R59 - runda 2 (subsesja R59-R, swieza)

Data: 2026-11-16. Recenzent: swieza subsesja R59-R (Opus 5.5), niezalezna od wykonawcow i od recenzenta rundy 1.
Stan recenzowany: HEAD `b39e911`, PR #12 (`bp/r59` -> `main`), baza `origin/main` = `4cc6090`. Glowny zakres: zmiany od stanu
rundy 1 (`f54fd42`): poprawki po rundzie 1, powtorka testow, skrypt pakietu, PDF z poprawka skryptu PDF, pakiet R59.
Metoda: czytanie diffu i plikow w HEAD (Git Bash), male skrypty na MSI (Python 3.12.10 + pypdf; import skryptu PDF w venv
`qc-pdf` bez budowania PDF). Nie uruchamialem pytest, node, Blendera ani samego `zbuduj_pakiet_R59.sh`; PC i serwer nie byly uzyte.
Cytaty z plikow z polskimi znakami sa tu zapisane bez znakow diakrytycznych.

## 0. Werdykt

**do scalenia po poprawkach D** - B 0 / P 0 / D 4.

Wszystkie 12 uwag rundy 1 sa zalatwione albo swiadomie pozostawione i opisane w `00_NADZOR_STAN.md:182` (otwartych: 0).
Poprawki nie wprowadzily bledow logicznych. PDF i pakiet sa spojne z galezia: tekst trzech PDF = `.md` w HEAD, pakiet = zrodla
w HEAD (27 z 27 kopii), sumy, ZIP-y i ZIP calosci odtwarzaja sie bajtowo. Najwazniejsza uwaga (D1) dotyczy straznika sciezek
skryptu pakietu: sama funkcja `w_katalogu` jest poprawna, ale tryb probny i wlasny katalog pakietu nadal pozwalaja trafic
w prawdziwe `Ramki_pakiet` / `Ramki_do_wgrania` / repo. Poprawka D1 i D3 nie zmienia zadnego pliku pakietu ani PDF
(skryptu pakietu i pliku stanu nie ma w pakiecie) - zalecam je przed G2. D2 i D4 moga poczekac.

## 1. Uwagi (B = blokujacy, P = powazna, D = drobna)

| Nr | Waga | Wlasciciel | Plik:linia | Co jest zle | Oczekiwane |
|---|---|---|---|---|---|
| 1 | D (zalecane przed G2) | R59-K | `Ramki/narzedzia/zbuduj_pakiet_R59.sh:115-122, 142-145, 270, 669-682` | Straznik trybu probnego sprawdza tylko, czy `<katalog>` LEZY W `Ramki_pakiet` / `../Ramki_do_wgrania` / `archiwum` (:117-118), a nie, czy wynikowe cele `D=<katalog>/Ramki_pakiet` i `W=<katalog>/Ramki_do_wgrania` (:120) SA tymi katalogami. Sprawdzone na wyciagnietych funkcjach (bez uruchamiania skryptu): `--proba .` -> odmowa 0, `D` = prawdziwy `Ramki_pakiet` (`-ef` = prawda) -> w kroku 6 `rm -rf "$D"` i `mv` (:681-682) BEZ kopii do archiwum (archiwum tylko poza proba, :669) - sledzony pakiet R59 zastapiony probnym (README z napisem "PRZEBIEG PROBNY", PDF moga byc sprzed R59); `--proba ..` albo bezwzgledna sciezka katalogu glownego repo -> odmowa 0, `W` = prawdziwy `Ramki_do_wgrania` (zapis 9-10 plikow probnych obok prawdziwych, a z `--nadpisz` nadpisanie plikow `*_2026-11-16_R59*`), a `--calosc` musi tylko lezec w `<katalog>` (:143), wiec ZIP calosci laduje w repo. Tryb wlasciwy z wlasnym `katalog_pakietu` (:122) nie ma zadnego straznika sciezki - chroni tylko heurystyka "README.txt + SHA256SUMS_*.txt" (:270), ktora przepuszcza np. `archiwum/Ramki_pakiet_przed_R59_2026-11-16` (zostalby skasowany i zastapiony). Straznik `--calosc` (:144) chroni katalog glowny worktree, a nie glowna kopie repo `<MSI>/kod/qc`, w ktorej worktree lezy. Udokumentowane wywolania (`bash narzedzia/zbuduj_pakiet_R59.sh [--calosc <poza repo>]`, `--proba <katalog tymczasowy>`) sa bezpieczne; to ta sama klasa bledu co incydent 15.11. | (a) tryb probny: `<katalog>` poza repo (`w_katalogu "$CEL" ..` = odmowa) albo porownanie w obie strony: `D`, `W`, `CALOSC` nie sa i nie zawieraja `Ramki_pakiet`, `../Ramki_do_wgrania`, `archiwum`; (b) tryb wlasciwy: `D` = `Ramki_pakiet` albo katalog poza repo, nigdy w `archiwum`; (c) `--calosc`: odmowa takze wewnatrz dowolnego drzewa roboczego git (`git -C <rodzic> rev-parse --show-toplevel`); (d) przy okazji: zamiast `rm -rf "$D"` przed `mv` zamiana przez przemianowanie (`mv "$D" "$D.stary"`, `mv "$T" "$D"`, potem kasowanie) - nieudane `rm -rf` na Windows (plik otwarty w przegladarce PDF) zostawia dzis pakiet czesciowy. Plus 4-5 przypadkow do testu odmowy (`.`, `..`, sciezka repo w postaci `C:/`, `archiwum/...`). |
| 2 | D (moze poczekac) | R59-K | `Ramki/narzedzia/zbuduj_pakiet_R59.sh` (126 linii z polskimi znakami, np. :2-3) | Nowy plik spoza wyjatkow ASCII z rundy 1, wbrew `CLAUDE.md` qc ("pliki po polsku bez znakow diakrytycznych"). Wzor `zbuduj_pakiet_R57.sh` na `main` tez je mial (30 linii) - kontynuacja, nie regres. Generowane pliki dla czlowieka (INSTRUKCJA, DO_WGRANIA, README pakietu) z polskimi znakami - jak w R57, bez uwag. | Komentarze i komunikaty skryptu bez diakrytykow przy najblizszej edycji (np. razem z D1 albo przy kopii do R6x); tresc generowanych plikow bez zmian. |
| 3 | D (zalecane przed G2) | koordynator | `Ramki/00_NADZOR_STAN.md:205-206` (koniec sekcji R59); :206 pkt (b) | (a) Po odbiorze R59-K krok 2 nie ma wpisu "NASTEPNE": brak listy tego, co zostalo - T0, T3c, T11, T13, T14, R59-R runda 2, dwie recenzje poprawki `serwer-laptop` przerwane limitem 00:23 (:205; stanu ich wznowienia plik nie podaje), G2, wgranie na Dysk (D8-b), rejestracja ZIP calosci na serwerze, sprzatanie PC. Nowy koordynator nie ma punktu wejscia. (b) :206 "archiwum/Ramki_pakiet_przed_R59_2026-11-16: 64 pliki, sha256sum -c R57 63/63" - prawda na dysku MSI, ale w gicie kopia ma 44 pliki: 20 STL wylacza `.gitignore:2` (`*.stl`, wyjatki tylko `Ramki_pakiet/**` i `modele_plytek/**`). Po scaleniu `sha256sum -c` tej kopii w czystym klonie zglosi 20 brakow. Nic nie ginie (STL R57 sa w historii `origin/main:Ramki/Ramki_pakiet` i w ZIP-ach R57), wczesniejsze archiwa pakietu tez nie maja STL w gicie - ale wpis tego nie mowi. | (a) wpis "NASTEPNE" z ta lista; (b) jedno zdanie: kopia R57 w gicie bez 20 STL (`.gitignore`), pelna tylko na dysku MSI; STL R57 w historii git i w ZIP-ach R57. |
| 4 | D (moze poczekac) | R59-D | `Ramki/Budowa ramki - decyzje i zamienniki.md:96` (PDF Budowa) | Zdanie w biezacej czesci "Czy mozna zmienic" (panel P3 192 x 192): "raster nadal daje >= 2 x 2 piksele pod fi 7,5" - gniazd fi 7,5 po R59 nie ma (najmniejsze fi 12 / fi 12,5). Stwierdzenie nie jest falszywe (warunek dla fi 12 jest latwiejszy), ale odwoluje sie do usunietego gniazda; jedyne trafienie liczby starego ukladu w miejscu biezacym w trzech PDF (pkt 4). Przeoczone w rundzie 1. | Przy najblizszej edycji dokumentu: "pod najmniejszym gniazdem (fi 12)". Teraz nie przebudowywac PDF i pakietu tylko dla tego zdania. |

## 2. Pkt 1 - stan 12 uwag rundy 1

| Uwaga r1 | Stan | Dowod w HEAD |
|---|---|---|
| 1 README - stare przyklady bez `_r54` | zalatwiona | `Ramki/stanowisko/README.md:48` (blok P2) i `:84` (blok P3a): dopisek "Od R59" z `--plytka ..._r54` / `--sufiks-ukladu _r54` |
| 2 `metryki_P2.py` - odrzucony skan bez sladu | zalatwiona | `metryki_P2.py:117, 132-135` (lista `uklad_niezgodny`: skan, plytka, powod, komunikat, miary straznika), `:171-174` (JSON takze gdy nie pasuje zaden skan), `:187` (`skanow_w_zestawie`, `uklad_niezgodny`), `:209`, `:214-215` (wiersz w podsumowaniu). Wartosci serializowalne (float / list / str). |
| 3a falszywy stozek | zalatwiona | `opisy_modulow/plate.md:32` |
| 3b podpowiedz o brakujacych `*_r54` | zalatwiona | `porownaj.py:90-96` (`PODPOWIEDZ_BRAK_R54`, `brak_ukladow_poprzednich`), `:161-164, 169` (komunikat + pole `uklad_podpowiedz`), `:317` (tabela), `:379` (mapa PNG); `ui_test.py:378-385`; `plate.md:33`, `ui.md:9`; testy `test_straznik.py:225-288` |
| 4a brak wylacznika straznika w oknie | pozostawiona, opisana | `00_NADZOR_STAN.md:182` ("NIE poprawiane ... 4a"); `plate.md:34`; raport R59-P pkt 11 |
| 4b D3-b nierozroznialny | zalatwiona | `plate.md:35` (liczby K1 / K2 z rachunku rundy 1) |
| 5 weryfikator - 2 rynienki przechodza | zalatwiona | `weryfikuj_uklad_R59.js:4-11, 50-51, 64` (`--d3b` wyklucza `--r54`), `:81`, `:163`, `:229-234` (domyslnie dokladnie 1 rynienka, z `--d3b` dokladnie 2); `R59_propozycja_ukladu.md:133-134, 140-141`. Log `R59_odbior/logi/T1_weryfikator_po_poprawce.log`: `parametry.json` 103 OK, 0 bledow (wynik wariantow D3-b bez przelacznika jest tylko w pliku stanu - kod czytalem, nie uruchamialem). |
| 6 teksty generatora; lista SHA iter1 | czesc 1 pozostawiona, opisana; czesc 2 zalatwiona | `00_NADZOR_STAN.md:182` (generator d3b56f63 = recenzowany, sprawdzone: SHA w HEAD d3b56f63); `R59_wdrozenie_zmiany.md:172` (wyjasnienie listy iter1, de0d26c5 vs f4196fbc) |
| 7 "8 z 17" | zalatwiona | plan `:243`, `:568`; Budowa `:163` - "7-8 z 17" z wyjasnieniem 13 z 20 prob (= `katalog.md:15`) |
| 8 stozki "w naroznikach", "jedyny element" | zalatwiona | plan `:118` ("Trzy stozki znacznikow"), `:216`, `:647` (wyrownanie po stozkach + sprawdzenie ukladu) |
| 9 `buduj_pdf_R59.cmd` zawsze kod 0 | zalatwiona | `buduj_pdf_R59.cmd:32, 35, 98-145` (wszystkie galezie bledu -> `koniec_blad`, `KOD=1`), koniec `exit /b %KOD%` |
| 10 plik stanu i `baseline.md` | zalatwiona | (a) `00_NADZOR_STAN.md:165` 287 = 287; (b) `:156-157` 6 kluczy (W-b 2, P-e 4); (c) konce linii: HEAD 204 CRLF + 2 LF = jak `origin/main` (132 + 2); (d) `R59_odbior/baseline.md:69-70` |
| 11 testy zalezne od lokalnego `ustawienia.toml` | pozostawiona, opisana | `00_NADZOR_STAN.md:182` i zadanie czlowieka `:174`; `stanowisko/README.md:21, 103` (lista czerwonych testow) |
| 12a `mail_aidite_zapytanie.md:11` | pozostawiona, opisana | `00_NADZOR_STAN.md:182` (plik spoza paczki, decyzja wlasciciela) |
| 12b sekcja 11 planu | zalatwiona | `plan_ramki_v2.md:789` (liczby = arkusz: 1008,05 / 907-1613 / 1216-2161; 1107,05 / 996-1771 / 1305-2320; 178,98 / 179,84) |
| 12c `test_ui.py` skip | zalatwiona (komentarz, skip bez zmian) | `test_ui.py:126-128` |

Razem: zalatwione w calosci 8 (1, 2, 3, 5, 7, 8, 9, 10), czesciowo z reszta opisana 3 (4, 6, 12), pozostawiona opisana 1 (11); otwarte 0.

Nowe bledy z poprawek: 0. Sprawdzone przypadki brzegowe podpowiedzi (`porownaj.py:94-96, 161`):
- puste `[plytki]`: nieosiagalne z pliku (`ustawienia.py` wymaga `wieczorna` i `poranna`); w slowniku recznym `porownaj` i tak konczy sie wczesniej
  (`katalog_plytki` -> `BladUstawien`) - bez skutku;
- inny przyrostek (`_r57`, `_r59`): liczy sie jako "uklad poprzedni jest" -> bez podpowiedzi, choc tekst mowi o `_r54`; dzis takich nazw nie ma;
- czesciowo uzupelniony plik (np. tylko `wieczorna_r54`) i stara plytka poranna: bez podpowiedzi (warunek globalny, nie per typ) - zgodnie z zaleceniem
  rundy 1 i z opisem `plate.md:33`; test `test_straznik.py:259-264` sprawdza wlasnie ten przypadek;
- uklad zgodny: galaz `except NiezgodnyUklad` sie nie wykonuje, pola `uklad_podpowiedz` nie ma; `tabela`, `mapa_png`, okno czytaja je przez `.get` - poprawnie.
Nowe testy sprawdzaja to, co deklaruja (podpowiedz przy starych ustawieniach w komunikacie, tabeli, PNG i oknie; brak przy pelnych ustawieniach i przy
ukladach `_r54` innego typu); slowo "uruchom okno ponownie" jest jedynym, ktore odroznia tekst okna od `uklad_komunikat` - test je sprawdza.
Logi koordynatora po poprawkach: T5 252 passed / 3 skipped / 0 failed, T6-T10 FAIL 0 (`R59_odbior/logi/*_po_poprawkach.log`) = plik stanu i raport R59-P.

## 3. Pkt 2 - skrypt PDF `buduj_plan_wdrozenia.py` (06825cc9 -> 5cbf31da)

- Diff `:530-538`: klasa `num` (prawo + `white-space: nowrap`) dla pierwszej kolumny tylko, gdy wszystkie jej komorki maja <= 12 znakow. Warunek liczy
  `get_text(strip=True)` po renderowaniu markdown (bez `**` itd.), wiec jest poprawny.
- Sprawdzenie na prawdziwych dokumentach (import obu wersji skryptu w venv `qc-pdf`, `build_html` na trzech `.md`, porownanie klas): 46 tabel
  (plan 21, Zakupy 18, Budowa 7); tabele z pierwsza kolumna Krok / Nr / Dzien / Id / Nr uwagi: 8, wszystkie w planie. 7 z nich ma w pierwszej kolumnie
  komorki o dlugosci 1-2 znakow (klasa `num` jak dawniej: 11, 15, 8, 5, 10, 5, 4 komorek). Zmienia sie dokladnie 1 tabela - "Kolejnosc i bramki"
  (12 wierszy, najdluzsza komorka 162 znaki, 10 komorek > 12): `num` 12 -> 0. Innych roznic w klasyfikacji tabel: 0 (wszystkie pola, 3 dokumenty).
- Kopia `archiwum/buduj_plan_wdrozenia_przed_R59_PDF_2026-11-15.py` = 06825cc9 = wersja z `f54fd42` (bajtowo). Plik w HEAD = 5cbf31da.

## 4. Pkt 3 - trzy PDF w `Ramki/` (pypdf)

| PDF | SHA-256 | stron | "R59" | "23 gniazda" | podpisy / tabela |
|---|---|---|---|---|---|
| plan wdrozenia v2 | 57b5afd7 | 27 | 46 | 9 | Rys. 4 "18 gniazd i 1 rynienka" i Rys. 5 "23 gniazda i 1 rynienka" na str. 23; "Kolejnosc i bramki" z kolumna "Co odblokowuje" na str. 22 - 3 kolumny, 12 wierszy, wszystkie komorki obecne |
| Zakupy i druk | 71433fce | 11 | 28 | 5 | - |
| Budowa ramki | 8a16e9dc | 16 | 34 | 4 | - |

- PDF = te same pliki w `Ramki_pakiet/01_Dokumenty` i w `Ramki_do_wgrania` (3 z 3). PDF nowsze niz ostatnia zmiana `.md` (commit `8740198` po `fbb143f`).
- Tekst `.md` vs PDF (fragmenty >= 25 znakow, bez bialych znakow): plan 1080 fragmentow, brak 6 (tytul, wiersz metadanych, 4 znaczniki rysunkow
  zastapione rysunkami); Zakupy 426 / 1 (wiersz metadanych); Budowa 571 / 1 (wiersz metadanych). Poprawki rundy 1 (uwagi 7, 8) sa w PDF.
- Liczby starego ukladu w tekscie PDF (wzorce jak w rundzie 1): 83 trafienia (plan 26, Zakupy 19, Budowa 38); 74 w kontekscie historii, 9 obejrzanych
  recznie: 8 to tabela "bylo -> jest" (plan :236), tabela odrzuconych wariantow i wiersz nowego ukladu "6 x fi 12,5"; **w miejscu biezacym: 1** (uwaga 4).
- Daty: tylko strona tytulowa ("Wersja 16 listopada 2026, 00:0x") i stopka kazdej strony (27 / 11 / 16) - znacznik budowy; w tresci 0.
- Nazwiska: tylko autor (strona tytulowa i stopka: 28 / 12 / 17 = 1 + liczba stron); poza tym 0. Metadane: Title, Author, Subject.

## 5. Pkt 4 - skrypt pakietu `zbuduj_pakiet_R59.sh` (712 linii, SHA 30d1b32a)

Przeczytany w calosci.
- Funkcja `w_katalogu` (:85-99): przetestowana w izolacji (funkcje wyciete z pliku, `source` w Git Bash, katalog roboczy `Ramki`), 10 z 10 zgodnie
  z oczekiwaniem: postac `C:/`, `/c/`, `C:\`, wzgledna `../`, wielkie litery, nazwa 8.3 (`ADMINI~1/.../WORKTR~1/...`), sciezka przez zlacze katalogow
  (junction w scratchpadzie -> repo; zlacze usuniete po tescie), sciezka poza repo, sasiad o tym samym przedrostku (`<repo>2/x`), podkatalog.
  Porownanie napisow jest literalne (wzorzec w cudzyslowie, konczy sie `/`), petla `-ef` po przodkach dziala takze dla sciezek jeszcze nieistniejacych.
  Ograniczenie: gdy katalog porownania nie istnieje, zostaje samo porownanie napisow (dla 8.3 wynik "nie lezy" - przy `--calosc` w probie to kierunek
  bezpieczny: odmowa).
- Uzycie straznika: uwaga 1 (D1).
- Kolejnosc: wszystkie kontrole tresci (zrodla, sumy przypiete, 9 nieplytkowych, model 3D, PDF, pakiet, sumy, ZIP-y, ASCII `NA_SERWER`) sa przed
  krokiem 6; przed nimi tylko `mkdir -p "$CALOSC"` + plik proby zapisu (:274-276) i `mkdir -p "$W"` w probie. Odmowa nadpisania plikow R59
  (:277-279) i migawka pozostalych plikow `W` (:283-288, porownana po zapisie :688) - dzialaja.
- Kasowanie: `rm -rf "$T" "$TW"` (:292, pulapka EXIT) - tylko katalogi robocze `<D>.budowa_R59*` (cudzyslowy, przyrostek staly; dla `D` = `/`
  wychodzi `.budowa_R59` w `Ramki` - nieszkodliwe); `rm -rf "$D"` (:681) - `D` pusty albo z `README.txt` i `SHA256SUMS_*.txt`; warunki w D1.
- Spacje i pauza w nazwach: wszystkie sciezki w cudzyslowach; niecytowane tylko listy stalych nazw bez spacji (`$PLYTKI_DO_DRUKU`, `$PLYTKI_BAZOWE`).
  Przebieg wlasciwy na MSI odczytal 3 PDF z pauza w nazwie (plik stanu :206; potwierdzone moim pypdf).
- Kody wyjscia: `set -euo pipefail`, `blad` -> 1, Python `sys.exit(1)` przechodzi przez `set -e`, potok arkusza z `pipefail`; `pdf` -> kod 3 obslugiwany.
  `grep -F "$(suma_plytki ...)"` z pustym wzorcem przeszedlby zawsze - sumy n1 / n4 sa wpisane na stale, wiec nie dotyczy.
- Powtarzalnosc ZIP: staly czas wpisow (poludnie dnia pakietu), `create_system` 0, kolejnosc `LC_ALL=C sort`. Moja przebudowa (Python 3.12.10, zlib 1.3.1)
  z plikow `Ramki_pakiet`: cz1 4bd44322 (33 wpisy), cz2 dd199bb1 (17), cz3 21eaef15 (32) = pliki w `Ramki_do_wgrania` bajtowo; ZIP calosci
  83 wpisy, 19 852 286 B, d5c8508aa326... = `NA_SERWER_2026-11-16_R59.md`. Inna wersja zlib moze dac inne bajty - naglowek skryptu mowi to uczciwie.

## 6. Pkt 5 - pakiet (liczniki)

- `Ramki/Ramki_pakiet/`: 82 pliki = 81 + `SHA256SUMS_2026-11-16_R59.txt`; `sha256sum -c` 81 z 81 OK; pliki bez wpisu 0.
- 8 plikow plytek do zamowienia (`02_Druk_drukarnia_PA12`): suma = `R59_wdrozenie_zmiany.md` 8 z 8; wszystkie pliki plytek i JSON ukladu w pakiecie 17 z 17.
- 9 plikow nieplytkowych = `SHA256SUMS_2026-11-02_R57.txt` (sciezka i suma) 9 z 9.
- Pliki o starych sumach plytek / JSON (lista 16 sum z R57 + `sha256_stl_przed_R59.txt`): 0.
- `03_Druk_wlasny/PETG_FDM/ramka_plytka_wieczorna_n1_v2_TEST_SKANERA.stl` = nowe n1 (3b0db545) = `02_Druk/...n1` = `wyniki_v2/stl`.
- 3 ZIP (zipfile): 82 wpisy, kazdy plik pakietu w dokladnie jednym ZIP-ie, 0 brakow, 0 nadmiaru, 0 roznic tresci, CRC dobre; rozmiary 4 599 220 /
  8 359 286 / 6 891 313 B (< 10 000 000). Plik sum w `Ramki_do_wgrania` = plik sum pakietu.
- Kopie w pakiecie = zrodla w HEAD: 27 z 27 (3 dokumenty .md + PDF planu, plan budowy, 6 plikow zrodlowych, 4 narzedzia, 3 raporty, opis i raport
  programu, README wynikow, model i animacja, 4 JSON). Arkusz w pakiecie = `R59_arkusz_zamowienia.md` (rozni sie tylko nazwa pliku csv w zdaniu) i `.csv` bajtowo.
- `archiwum/Ramki_pakiet_przed_R59_2026-11-16/`: na dysku 64 pliki, `sha256sum -c` R57 63 z 63; w gicie 44 obiekty = `origin/main:Ramki/Ramki_pakiet`
  (wszystkie nie-STL identyczne obiekty git), 20 STL tylko na dysku (uwaga 3b).
- `Ramki_do_wgrania`: 25 plikow sledzonych; 10 nowych `*_2026-11-16_R59*` (3 ZIP, plik sum, INSTRUKCJA, DO_WGRANIA, NA_SERWER, 3 PDF); 15 starszych bez zmian.
- README / INSTRUKCJA / DO_WGRANIA / NA_SERWER: gniazda 18 + 1 (6 x fi 12, 12 x fi 15; rynienka 60 x 15) i 23 + 1 (20 x fi 12,5, 3 x fi 15; 50 x 13) = G0;
  "bylo" 18 + 2 / 31 + 2 tylko jako historia; objetosci 59,66 / 59,95 / 59,94 / 49,36 / 49,64 cm3 = arkusz; ceny 907-1613 / 1216-2161 i 996-1771 /
  1305-2320 zl = arkusz; liczby plikow 81 / 83 / cz1 33, cz2 17, cz3 32 / "12 STL" w cz1 - zgodne z rzeczywistoscia; tabela DO_WGRANIA (bajty, 16 znakow
  SHA) 8 z 8 zgodna. Ostrzezenie o starych plikach plytek o tych samych nazwach (R54-R57) - jest w README i INSTRUKCJI. Stare plytki opisac i trzymac
  osobno - jest. D6 (ilosci bez zmian), D8-b ("wgranie dopiero po zgodzie"), "jeden ZIP calosci na serwer" (ZIP poza gitem, `NA_SERWER` z nazwa, rozmiarem,
  SHA; rejestracja dopiero po zgodzie) - zgodne. Daty w tresci: tylko data pakietu i daty w nazwach plikow (pakiet R57, raport R59-P, wzor WGRANE R56).
  Nazwiska w nazwach plikow pakietu i wpisow ZIP: 0. Model online: README `:48` i plan `:19` mowia wprost, ze wersja online pokazuje poprzedni uklad, a model
  z nowym ukladem jest w pakiecie - nie odsylaja do niej jako aktualnej.

## 7. Pkt 6 - dane osobowe

- `<MSI>\kod\qc\Prace_test` (tylko odczyt): 37 pozycji, 42 slowa >= 4 liter po odjeciu slow technicznych (moja lista slow
  technicznych jest krotsza niz w rundzie 1 - stad 42 zamiast 36).
- Przeszukane 103 zrodla: pliki tekstowe zmienione od rundy 1 (w tym caly tekstowy pakiet, kopia R57 w archiwum, `Ramki_do_wgrania`, logi, raporty),
  nazwy plikow diffu od rundy 1, nazwy wpisow 3 ZIP-ow, tekst 3 PDF, opisy commitow `f54fd42..b39e911`.
- Trafienia: 51 w 43 zrodlach, 5 roznych slow - wszystkie techniczne albo pospolite (nazwy plikow sesji przegladarki, nazwa uslugi chmurowej, termin
  protetyczny, slowo pospolite); w nazwach plikow, wpisach ZIP i commitach 0. **Nazwisk / nazw zlecen: 0.** Slow nie wypisuje.
- Ograniczenie jak w rundzie 1: slowa krotsze niz 4 litery nie byly szukane.

## 8. Pkt 7 - higiena

- `git diff --name-status origin/main...HEAD`: 581 pozycji (466 A, 99 M, 16 R100 - przeniesienia plikow R57 z `Ramki_pakiet` do archiwum, wykryte przez
  git jako zmiana nazwy); 146 349 linii dodanych, 2 362 usuniete. Od rundy 1: 146 plikow zmienionych, 145 nowych sciezek w PR.
- Sciezki nowe od rundy 1 poza listami subsesji (plan sekcje 6-13 + pliki koordynatora + dopisane decyzja koordynatora): **0** (R59-K: skrypt, `Ramki_pakiet/**`,
  `Ramki_do_wgrania/*R59*`, archiwum pakietu; R59-PDF / R59-D: 3 PDF, skrypt PDF + kopia; R59-P: `stanowisko/**`; R59-U, R59-A, R59-R, koordynator: reszta).
  Dla plikow z rundy 1 obowiazuje jej wynik (0 poza listami).
- STL w diffie: 33 = 13 w `Ramki/Ramki_pakiet/**` + 20 w `Ramki/stanowisko/modele_plytek/**`; poza: 0. `raporty/testy_krawedz/`: 0.
- Znaki sterujace: 0 plikow (95 plikow tekstowych A/M od rundy 1; 270 w calym PR).
- Konce linii: od rundy 1 jeden plik zmieniony tylko koncami linii - `00_NADZOR_STAN.md` (naprawa LF -> CRLF z uwagi 10c, zamierzona); w calym PR 0 z 67 plikow M.
- Nowe pliki nie-ASCII od rundy 1: 45 z 61 nowych plikow tekstowych - `archiwum/**` 34, `Ramki_pakiet/**` 8 (kopie dokumentow), `Ramki_do_wgrania` 2
  (INSTRUKCJA, DO_WGRANIA - jak ich odpowiedniki R57); poza wyjatkami 1: `narzedzia/zbuduj_pakiet_R59.sh` (uwaga 2). Caly PR: 119 z 203.
- Moj slad: import skryptu PDF w pkt 3 utworzyl 2 katalogi `__pycache__` (ignorowane przez `.gitignore`) w `Ramki/narzedzia` i `Ramki/archiwum` - usuniete;
  `git status` czysty (poza tym raportem).

## 9. Pkt 8 - gotowosc do scalenia

- Sprzecznosci w galezi: nie znalazlem. "Zakupy i druk" odsyla do `Ramki_pakiet/` i jego sum - pakiet jest teraz R59 (uwaga z rundy 1 pkt 5 nieaktualna);
  plan wdrozenia, README pakietu i INSTRUKCJA mowia to samo o ukladzie, cenach, plikach i starych plytkach; pakiet zawiera raport rundy 1 (stan z chwili budowy).
- Przed G2 (zalecane, nie zmienia pakietu ani PDF): D1 (straznik skryptu pakietu - kod, ktory zmienia repo i zostaje w `main` jako wzor dla R6x),
  D3 (plik stanu: "NASTEPNE" i zdanie o STL w archiwum). Po poprawce D1 wystarczy test odmowy na przypadkach z D1 (`--proba` w katalogu tymczasowym).
- Moze poczekac: D2 (diakrytyki w skrypcie), D4 (jedno zdanie w "Budowa ramki" - wymagaloby przebudowy PDF i pakietu).
- Po stronie koordynatora (nie uwagi do diffu): testy T0, T3c, T11, T13, T14 nie maja jeszcze dowodow w `R59_odbior/logi`; `R59_raport_koncowy.md` nie istnieje
  (plan pkt 14-15); dwie recenzje poprawki `serwer-laptop` przerwane limitem - stan nieznany.

## 10. Informacje (nie liczone jako uwagi)

- `ui_test.py:384-385`: przy starych ustawieniach podpowiedz pojawia sie w oknie dwa razy (tekst okna i koniec `uklad_komunikat`) - kosmetyka.
- Przy starym `ustawienia.toml` podpowiedz "dopisz `_r54`" pojawi sie przy kazdej niezgodnosci bez pasujacego ukladu, takze przy nowej plytce z zabrudzonym
  stozkiem; `plate.md:32` kaze najpierw oczyscic stozki - wystarczy.
- `metryki_P2.py`: sciezka `uklad_niezgodny` bez testu automatycznego; R59-P sprawdzil ja recznie na zestawie mieszanym (raport R59-P pkt 11).
- INSTRUKCJA wewnatrz ZIP-a calosci opisuje 3 ZIP-y i osobne PDF; wyjasnia to `NA_SERWER` (poza ZIP-em), a README.txt w ZIP-ie jest poprawny.
  Przy nastepnym pakiecie: jedno zdanie w INSTRUKCJI o ZIP-ie calosci.
- ZIP calosci lezy tylko w scratchpadzie koordynatora; jest powtarzalny (pkt 5), wiec przed rejestracja mozna go odtworzyc - po rejestracji trzymac plik zarejestrowany.
- "7/7 porownan wartosci (6 kluczy)" w `00_NADZOR_STAN.md:157` - po poprawce czytelne, bez uwag.

## 11. Czego nie sprawdzono i dlaczego

- Niczego nie uruchamialem: pytest, node (weryfikator), Blender, `buduj_pdf_R59.cmd`, `zbuduj_pakiet_R59.sh` - MSI nie ma pakietow testowych ani node,
  a skrypt pakietu zmienia repo (zakaz zmian w worktree). Zachowanie skryptu pakietu w D1 wynika z czytania kodu i testu samych funkcji `norm` / `w_katalogu`
  oraz warunkow `-ef` na prawdziwych katalogach; pelnego przebiegu `--proba .` nie wykonywalem.
- Wynik weryfikatora dla wariantow D3-b bez `--d3b` - tylko z kodu (brak logu, brak node).
- ZIP calosci jako plik (scratchpad koordynatora) - sprawdzony przez odtworzenie bajtowe, nie przez odczyt pliku.
- Obrazy stron PDF (rysunki 4 i 5, uklad tabeli) - tylko tekst pypdf; wyglad obejrzal koordynator.
- Reszta diffu sprzed rundy 1 - zgodnie ze zleceniem nie recenzowana od nowa (poza miejscami zmienionymi poprawkami).
- Dane osobowe - tylko slowa >= 4 liter z nazw w `Prace_test`.
- Poprawka w repo `serwer-laptop` i rejestracja na serwerze - poza zakresem tej recenzji.
