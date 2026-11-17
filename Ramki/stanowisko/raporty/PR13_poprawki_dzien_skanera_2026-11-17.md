# PR #13 - poprawki okna "Dzien skanera" po recenzji (runda 1)

Data: 2026-11-17. Galaz `przed-skanerem-p2` (od `przed-skanerem` @ `a6cf3a4`). Zrodlo uwag:
`Ramki/recenzja/raport_recenzenta_PR13_runda1.md` - P2, P3, P4, P5, P6, D1, D7 (a), D10, D11.
Zmienione pliki (wzgledem `Ramki/stanowisko/`): `stanowisko/dzien_skanera_rdzen.py`, `stanowisko/dzien_skanera.py`,
`stanowisko/dzien_skanera_kroki.toml`, `testy/test_dzien_skanera.py`, `opisy_modulow/dzien_skanera.md`,
`raporty/dzien_skanera_2026-11-16.md` (jeden dopisek, D7), ten raport. Nic poza tym.
Obliczenia wylacznie na PC (`<PC-katalog>\app\p2`, kopia kodu z `git archive` + pliki robocze); na MSI tylko edycja.
Nazwiska w testach i w probie sa zmyslone.

## 1. Wynik w skrocie

| Uwaga | Stan | Scenariusz z raportu na kodzie `a6cf3a4` | Test (w `testy/test_dzien_skanera.py`) |
|---|---|---|---|
| P2 | zrobione | odtworzony testem: plik "znany" w `obserwator.json`, a w zapisanym manifescie go nie ma | `test_awaria_w_srodku_serii_stan_obserwatora_nie_wyprzedza_manifestu`, `test_kopia_bez_wpisu_w_manifescie_jest_po_wznowieniu_podjeta_ponownie` |
| P3 | zrobione | odtworzony: plik `.bak` z manifestu nie ma sumy, `--sprawdz` ZIP = 1 | `test_pliki_bak_tmp_czesc_ze_skanera_sa_w_paczce_a_pliki_robocze_programu_nie` |
| P4 | zrobione | odtworzony: po nieudanym pakowaniu `zakonczono` ustawione, stary ZIP skasowany | `test_nieudane_pakowanie_nie_oznacza_sesji_i_zostawia_stara_paczke`, `test_pakowanie_przerwane_zamykaniem_programu_i_zmiana_w_trakcie_pakowania`, `test_okno_zamkniecie_w_trakcie_pakowania_pyta_i_nieudane_pakowanie_nie_jest_spakowane` |
| P5 | zrobione | odtworzony: `X_cad__zmiana2.stl` i `X_cad__2.stl` w paczce; dodatkowo nazwa projektu zastanego w `obserwator.json` w ZIP | `test_kolejne_wersje_i_duplikaty_projektu_exocad_nie_trafiaja_do_paczki` |
| P6 | zrobione | odtworzony skryptem (3 z 12 plikow, krok "zrobiony", `--sprawdz` folderu i ZIP = 0) | `test_przerwana_kopia_calego_folderu_zostawia_slad_a_ponowienie_ja_dokancza`, `test_kopia_calego_folderu_przerwana_awaria_jest_po_wznowieniu_oznaczona_i_dokanczana`, `test_kopia_folderu_z_niedostepnym_podkatalogiem_jest_niepelna`, `test_sesja_zapisana_starsza_wersja_bez_rejestru_kopii_otwiera_sie_i_pakuje` |
| D1 | zrobione | odtworzony: `ValueError: ZIP does not support timestamps before 1980` | `test_plik_z_data_sprzed_1980_nie_zatrzymuje_pakowania` |
| D7 (a) | zrobione | - | opis modulu pkt 4, dopisek w `raporty/dzien_skanera_2026-11-16.md` sekcja 2 |
| D10 | 4 z 8 wziete | odtworzone testami (3) | patrz pkt 3 |
| D11 | zrobione | 2 testy luk przechodza takze na starym kodzie (zachowanie bylo dobre, brakowalo testu) | `test_zrodlo_zmienione_w_trakcie_kopii_jest_odrzucane_i_kopiowane_ponownie`, `test_wznowienie_z_pliku_tmp_gdy_manifest_i_kopia_sa_uszkodzone` + testy P2-P5 |

Testy byly najpierw uruchomione na kodzie sprzed poprawki (log PC `p2\ds_czerwone.log`): testy P2, P3, P4, P5 i D1
byly czerwone z powodu opisanego w raporcie recenzenta. Testy P6 padaly na braku rejestru kopii (`KeyError`), dlatego
sam scenariusz P6 potwierdzilem osobnym skryptem na starym kodzie (`p2\p6_odtworzenie.py`: 3 z 12 plikow, krok
"zrobiony", brak sladu przerwania w manifescie, `--sprawdz` folderu i ZIP = 0). Zadna uwaga nie okazala sie
nieodtwarzalna. Z D10: trzy testy (pliki w drodze, dwa foldery o tej samej nazwie, kilka paczek) byly czerwone na
starym kodzie; pozycja "tylko w pamieci" wynika z czytania (jej test padal wczesniej na braku parametru `przerwij`).

## 2. Co zmienione

**P2 - stan obserwatora nie wyprzedza manifestu.** `Zbieracz._zapisz_znane` przed kazdym zapisem `obserwator.json`
wymusza zalegly zapis manifestu (`Sesja.zapisz_zalegle`). Na dysku plik jest "znany" najwczesniej wtedy, gdy jego wpis
jest w zapisanym manifescie; odwrotna kolejnosc awarii (wpis jest, "znany" nie) konczy sie ponowna kopia, ktora jest
usuwana jako ta sama tresc - bez duplikatu. Dodatkowo przy wznowieniu `Zbieracz._zapomnij_kopie_bez_wpisu` przeglada
`kroki/*/pliki/<folder>/`: kopia bez wpisu w manifescie (sesja zapisana wersja sprzed poprawki) powoduje, ze zrodlo
przestaje byc "znane" i jest podejmowane ponownie; `Sesja.cel_wolny` zastepuje wtedy kopie bez wpisu.

**P3 - filtr tylko dla wlasnych plikow roboczych.** Nowa funkcja `plik_roboczy_programu(rel, w_manifescie)`: plik
obecny w manifescie nigdy nie jest roboczy; robocze sa `*.czesc` spoza manifestu, `.tmp` / `.bak` plikow zapisu
atomowego w korzeniu sesji (`sesja.json`, `obserwator.json`, raport, sumy) i `kontrole/*.tmp|.bak`. Uzywa jej
`_pliki_sesji` (sumy, ZIP) i lista "plikow spoza listy sum" w `--sprawdz`. `--sprawdz` folderu zglasza teraz takze
plik z manifestu, ktorego nie ma w sumach (dawniej tylko ZIP dawal blad) - folder i ZIP daja ten sam wynik.

**P4 - znaczniki i wymiana archiwow po sukcesie.** `spakuj`: manifest "po spakowaniu" (z `zakonczono`, `spakowano`)
powstaje tylko w pamieci i trafia do paczki oraz raportu; wszystkie czesci ZIP sa budowane jako `*.zip.czesc`;
dopiero gdy sa gotowe: `os.replace` na nazwy docelowe, usuniecie starych czesci o innych nazwach, zapis raportu, sum
i `paczka.json`, a na koncu znaczniki w `sesja.json`. Wyjatek, brak miejsca albo przerwanie: pliki `.czesc` sa
usuwane, stan sesji i stara paczka zostaja (w logu `pakowanie: nieudane / przerwane`). `spakuj(..., przerwij=)`:
sprawdzane miedzy plikami, wyjatek `Przerwano`; zbieracz podaje `_stop.is_set`. Okno: `closeEvent` w trakcie
pakowania pyta "Zamknac okno mimo to?" (Nie = okno zostaje), po "Tak" pakowanie jest przerywane; komunikat
o nieudanym pakowaniu mowi wprost, ze sesja nie jest spakowana. Wyjatek `_pakowanie` w `Sesja.zapisz` obejmuje juz
tylko zapis znacznikow: zmiana sesji w trakcie pakowania jest wykrywana porownaniem manifestu sprzed i po, zapisywana
na dysk jako "zmieniono po spakowaniu" i uniewaznia sumy (D10: dawniej tylko w pamieci).

**P5 - projekty exocad: decyzja po nazwie zrodla.** `czy_projekt_exocad(wpis)` sprawdza `zrodlo`, `wzgledna` i `cel`;
wzor `_cad(__\w+)?\.stl$` lapie tez nazwy kopii `__zmianaN` i `__N`. Z paczki znikaja: pliki, wyniki ich kontroli
(`kontrole/k<id>.*`), katalogi pomiarow (`pomiary/k<id>_*`), a ich nazwy - z manifestu, raportu, logu i stanu
obserwatora w paczce. Nowe `bez_nazw_projektow`: w tych tekstach zastepowana jest takze kazda INNA nazwa pasujaca do
wzoru (projekt, ktory lezal w folderze skanera przed sesja i jest tylko w `obserwator.json`; plik, ktorego nie udalo
sie skopiowac i jest tylko w logu). `--sprawdz` rozpoznaje projekty ta sama funkcja.

**P6 - kopia calego folderu ze sladem.** Nowy, addytywny klucz manifestu `kopie_folderow` (lista wpisow: `nr`, `krok`,
`start`, `koniec`, `stan`, `powod`, `zrodla`, `plikow`, `bajtow`, `juz_byly`, `skopiowane`, `bledy`, `pominiete`,
`niedostepne_katalogi`, `pierwszy_id`). Wpis `w_toku` jest zapisywany przed pierwszym plikiem, wynik - po petli (takze
po przerwaniu: brak miejsca, zamkniecie okna, bledy plikow). `pliki_w_folderze` oddaje katalogi, ktorych nie da sie
odczytac (`niedostepne`), a kopia je liczy i loguje. `kompletnosc_z_manifestu`: krok z `kontrola = "kopia_folderu"`
ma brak, dopoki ostatnia kopia nie jest `pelna` - nie jest juz "zrobiony" po pierwszym pliku. `--sprawdz`: wiersz
`KOPIA FOLDERU (krok ...): pelna | NIEPELNA (...) - w sesji X z N plikow (...)`, kod 3 przy niepelnej; liczba plikow
kopii w manifescie jest porownywana z liczba z wpisu. Wznowienie: `Sesja.wznow` zamienia `w_toku` na `przerwana`
z liczbami z manifestu, zbieracz wysyla oknu czerwony komunikat; ponowne klikniecie przycisku kopiuje tylko pliki,
ktorych kopia w tym kroku nie ma (zrodlo + rozmiar + czas), wiec dokonczenie nie tworzy duplikatow `__2`.
Manifest bez klucza (sesja zapisana starsza wersja) otwiera sie i jest oceniany jak dawniej (test).

**D1.** `zipfile.ZipFile(..., strict_timestamps=False)`.

**D7 (a).** `opisy_modulow/dzien_skanera.md` pkt 4 i dopisek w `raporty/dzien_skanera_2026-11-16.md`: okno rozpoznaje
uklad przez `plate.rozpoznaj_uklad` (od `502212e`).

## 3. D10 - co wziete, co zostaje

| Pozycja z D10 | Decyzja | Test / powod |
|---|---|---|
| pakowanie nie czeka na pliki w drodze | wziete: przed pakowaniem przeglad folderow i do 20 s czekania na pliki jeszcze nieskopiowane | `test_pakowanie_czeka_na_pliki_w_drodze` |
| `zmieniono_po_spakowaniu = True` tylko w pamieci | wziete (razem z P4) | `test_pakowanie_przerwane_zamykaniem_programu_i_zmiana_w_trakcie_pakowania` |
| `--sprawdz` na folderze z kilkoma paczkami sprawdza pierwsza | wziete: kazda paczka, kod = najgorszy | `test_sprawdz_folderu_z_kilkoma_paczkami_sprawdza_kazda` |
| dwa foldery obserwowane o tej samej nazwie mieszaja sie w kopii | wziete: katalog kopii = etykieta folderu (`Scandata`, `Scandata_2`) | `test_kopia_dwoch_folderow_o_tej_samej_nazwie_nie_miesza_plikow` |
| "dwa stabilne odczyty" to licznik, nie czas | zostaje | warunek czasu wymaga przestawienia zegara w kilkunastu istniejacych testach (obiegi bez uplywu czasu) - nie jest to zmiana tania |
| sonda `ktos_pisze` otwiera zrodlo bez wspoldzielenia zapisu | zostaje | nie znam innego sposobu wykrycia otwartego zapisu bez takiej sondy; do decyzji po pierwszym kontakcie z programem skanera |
| STL z bajtami za danymi = "uciety" bez proby wczytania | zostaje | plik rosnacy z licznikiem 0 w naglowku wyglada tak samo, a `trimesh` i tak odrzuca niezgodna dlugosc - potrzebne wlasne wczytanie |
| `--sprawdz` = 0 dla kroku z samym watpliwym (zoltym) skanem | zostaje | to zmiana znaczenia oceny kroku (zolty = brak), decyzja koordynatora |

## 4. Testy i proba

- `testy/test_dzien_skanera.py`: 53 -> 71 testow; istniejace testy bez zmian (zadnego nie oslabilem). Poza testami
  z tabeli: `test_plik_roboczy_programu_i_usuwanie_nazw_projektow_z_tekstu` (reguly P3 / P5 wprost).
- Pelny pytest na PC: przed (`k2\pytest_5ef199e.log`) 408 passed, 3 skipped, 0 failed; po, na kodzie `2a1b78b`
  (`p2\pytest_p2_2a1b78b.log`, kopia w `p2\f`): **426 passed, 3 skipped, 0 failed** (602 s). Roznica = 18 nowych testow.
  Commit z tym raportem zmienia juz tylko ten plik. Wczesniejszy pelny przebieg na kodzie posrednim urwal sie na 67 %
  bez wyniku (zatrzymanie PC ok. 16:00) i nie jest liczony. Przebieg koncowy ruszyl ok. 16:05, zanim dotarly do mnie
  nowe limity PC (1 proces, watki = 2, kontrola RAM); po nich nie uruchamialem juz zadnych obliczen.
- Proba reczna (przed commitem `2a1b78b`, ktory zmienil tylko kolejnosc czekania przed pakowaniem i dodal test)
  z wiersza polecen (PC, `<PC-katalog>\app\p2\proby`, usuniete po probie): sesja kompletna budowana skryptem przez
  `Sesja` / `Zbieracz` (bez okna), potem `python -m stanowisko.dzien_skanera --sprawdz <folder>` i `<zip>`:
  - r1 (mala sesja, 24 pliki, kopia folderu 12 z 12): folder = 0, ZIP = 0;
  - r2 (to samo + `baza_skanera.db.bak` i `stan.tmp` ze skanera + projekt `..._cad.stl` zapisany dwa razy, 31 plikow):
    folder = 0, ZIP = 0; w ZIP sa oba pliki `.bak` i `.tmp` (z obserwacji i z kopii folderu), 0 nazw z `_cad`,
    0 plikow z nazwiskiem w tresci; w folderze sesji zostaja 3 pliki projektu (2 wersje + kopia folderu).
- [usunieto w kopii: opis dostepu ssh]

## 5. Co widzi technik inaczej (karta i sciaga nie byly zmieniane)

1. Zamkniecie okna w trakcie pakowania: nowe pytanie "Trwa pakowanie sesji ... Zamknac okno mimo to?".
2. Krok 14 (kopia calego folderu): gdy kopia jest niepelna, w panelu po lewej jest brak "kopia calego folderu NIEPELNA:
   w sesji jest X z N plikow ...", a na liscie komunikatow czerwony wiersz; krok nie robi sie zielony po pierwszym
   pliku. Drugie klikniecie przycisku kopiuje tylko brakujace pliki (dawniej: wszystko jeszcze raz z dopiskiem `__2`).
3. Instrukcja kroku 14 w oknie (`dzien_skanera_kroki.toml`) ma nowy punkt 4 (co zrobic przy kopii niepelnej) i zdanie
   "Nie zamykaj okna, dopoki pakowanie trwa"; dawny punkt 4 jest punktem 5.
4. Nieudane pakowanie: komunikat mowi, ze sesja nie jest spakowana; przy nastepnym starcie okno pyta o wznowienie
   niedokonczonej sesji (a nie "ostatnia sesja jest spakowana").
5. "Zakoncz i spakuj" moze poczekac do 20 s, gdy w folderze skanera wlasnie pojawil sie plik (komunikat na liscie).
6. Karta (`Ramki/dzien_skanera_karta_2026-11-16.md`, wiersz 14 i zdanie o czekaniu na koniec kopii i pakowania) jest
   nadal prawdziwa; nie wspomina o komunikacie "NIEPELNA" ani o pytaniu przy zamykaniu.

## 6. Granice i rzeczy do wiedzenia

- "Bez nazwisk" dotyczy nazwy PLIKU `*_cad.stl`. Nazwa FOLDERU projektu exocad (inne pliki z tego folderu ida do paczki
  ze swoja sciezka), nazwy zlecen w programie skanera i tresc zrzutow ekranu nie sa rozpoznawane - jak dotad.
- Zastepowanie nazw w logu i stanie obserwatora siega wstecz do ukosnika, cudzyslowu albo poczatku linii: w wierszu
  logu bez sciezki moze zniknac takze poczatek wiersza (data). Dotyczy tylko nazw, ktorych nie ma w manifescie.
- Rejestr kopii przechowuje liczby, nie liste plikow; porownanie w `--sprawdz` jest liczbowe.
- Folder obserwowany, ktory w chwili kopii nie istnieje, jest pomijany i nie oznacza kopii jako niepelnej (domyslny
  folder z ustawien czesto nie istnieje). Plik zablokowany na stale = kopia niepelna do skutku; pakowac mozna.
- Przerwanie pakowania dziala miedzy plikami; przy jednym bardzo duzym pliku zamkniecie okna czeka do 10 s i konczy
  proces - zostaje wtedy plik `*.zip.czesc` (usuwany przy nastepnym pakowaniu), stan sesji jest poprawny.
- Awaria dokladnie miedzy zamiana czesci archiwum wieloczesciowego a zapisem znacznikow: sesja jest "niespakowana",
  a w `paczka/` moga lezec juz nowe czesci - bezpieczny kierunek (trzeba spakowac ponownie).
