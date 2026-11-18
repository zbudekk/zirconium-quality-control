# Raport recenzenta PR #17 - runda 2 (przyrostowa)

Data: 2026-11-17. Recenzent: swieza subsesja (Opus 5.5), niezalezna od wykonawcy i koordynatora; werdyktu koordynatora nie znam.
Stan recenzowany: `fae2a5d` (`origin/e3/a2`), zakres `git diff d06db34..fae2a5d -- Ramki/stanowisko` (8 plikow paczki,
+1370 / -174). Numery linii ponizej dotycza `fae2a5d`.

Metoda: `stanowisko/scanner.py` i `stanowisko/silnik.py` przeczytane w calosci (i porownane ze stanem `d06db34`), diffy obu
plikow testow i symulatora w calosci, oba opisy modulow, sekcja "Runda 2" raportu paczki, raport rundy 1. Z istniejacego kodu:
`dzien_skanera_rdzen.py` (`otworz_zrodlo`, `ktos_pisze`, `pliki_w_folderze`), `porownaj.py` (struktura wyniku), `inspect.py`,
`match.py`, `katalog.py` (slowniki statusow i typow), `synth.py` (ostrzezenia); z `origin/e3/a1`: `session.py` (`_czas_iso`,
nazwy plikow wyniku, odczyt statusow) i `baza.py` (tabela `skany`) - do oceny kontraktu.

Uruchomienia - tylko na PC wlasciciela, konto `<konto-PC>`, katalog `<PC-katalog>\e3\r17b` (kod = `git archive` stanu `fae2a5d`,
w `stary\` stan `d06db34`), `OMP_NUM_THREADS=2`, jeden przebieg naraz, start przy 19-20 GB wolnego RAM (pomiar osobnym poleceniem):
1. Stary kod `d06db34` + NOWE testy (sprawdzenie, ze testy rundy 2 lapia scenariusze rundy 1):
   `test_silnik.py -k "nadpisany_w_kolejce or zmieniony_w_trakcie or konczy_sie_po_smierci"` (2 przebiegi - pierwszy omylkowo
   z `-x`) i `test_scanner.py -k "wylacznie_4_s or blad_listowania or folder_z_historia or podfolder_niedostepny"` z nakladka
   w MOJEJ kopii `conftest.py` na PC (stary `Scanner` przyjmuje i pomija nowe parametry) + jeden przebieg pojedynczego testu B1
   (4 s) dla odczytania powodu - ten jeden bez ponownego pomiaru RAM (minute wczesniej 20 GB; uchybienie wlasne).
2. Nowy kod: wlasne skrypty `x\eks_skaner.py` (S1-S4), `x\eks_silnik.py` (K1-K4, funkcja probna `x\proba_r17b.py`),
   `x\eks_gil.py` (GIL w Open3D / scipy na danych losowych), `x\eks_wyd.py` (wydajnosc `CzyscicielNazw`).
Bez pelnego pytest, bez analiz na skanach odniesienia. Na MSI nie uruchamialem pytest ani obliczen. Po pracy: katalog roboczy
`tmp` pusty; na PC 3 procesy python, wszystkie innego konta (niedostepne dla `<konto-PC>`), moich 0. Proces roboczy z testu P6
na starym kodzie zakonczyl `finally` testu.

## 0. Werdykt

**do scalenia po poprawkach** - nowe uwagi: B 0 / P 2 / D 7.

Poprawki rundy 1 sa zrobione rzetelnie: B1 rozwiazane (uruchomieniem: 20 plikow naraz przechodzi w 0,32-0,37 s mimo pliku
trzymanego wylacznie 25 s; plik zajety daje `Oczekiwanie` i zdarzenie po zwolnieniu, CPU 1,1 % rdzenia), skrot w wyniku jest
skrotem tresci faktycznie analizowanej, `stop()` zwraca zadania, pliki zastane nie wracaja jako nowe, nazwy plikow wyjscia nie
koliduja, nazwy z puli nie wychodza z silnika, proces roboczy konczy sie po smierci okna. Wszystkie 7 nowych testow, ktore
uruchomilem na `d06db34`, sa tam czerwone z wlasciwego powodu (zachowanie, nie brak API). Wyscig znaleziony przez wykonawce
w `scanner` jest poprawiony dobrze.

Dwie nowe rzeczy do poprawy powstaly W poprawkach P1 i P5 (szczegoly w pkt 2):
- **N1**: sprawdzenie skrotu PO analizie myli "pliku nie da sie teraz przeczytac / plik przeniesiony" z "plik zmieniony" - wynik
  dobrej analizy jest odrzucany z komunikatem "nowa tresc ma wlasne zdarzenie skanu", choc zadnego nowego zdarzenia nie ma;
  a kontrakt kaze A3 traktowac `plik_zmieniony` jako "nie awaria". Skan przepada bez wiedzy technika.
- **N2**: `CzyscicielNazw` zamienia KAZDY tekst wyniku, takze pola decyzji - folder `OK` w puli zamienia status inspekcji
  `ok` na `<projekt>`, folder `Waxup` / plik `korona.stl` zamieniaja typ pracy kandydata. Zepsute wartosci ida do bazy A1.
Obie poprawki sa male i mieszcza sie w `silnik.py` + testach.

## 1. Uwagi rundy 1 -> stan

| Nr | Stan | Sprawdzone |
|---|---|---|
| B1 | **zalatwione** | Uruchomione: S1 - plik zapisany i trzymany bez wspoldzielenia 25 s + 20 plikow zapisanych w tej samej chwili (parametry domyslne): 20 zdarzen po 0,32-0,37 s od zapisu, plik zajety: `Oczekiwanie` po 11,7 s (`od_s` 11,4), zdarzenie 0,77 s po zwolnieniu, 0 odrzucen, CPU procesu 0,28 s na 25 s (1,1 % rdzenia), `stan()` w trakcie `czeka 1 / zajete 1`. S2 - plik trzymany z prawem usuniecia i usuniety w trakcie (`os.stat` = `FileNotFoundError`) oraz plik zwolniony i od razu usuniety: 0 zdarzen, 0 odrzucen, nic nie wisi (`czeka 0`). Nowy test 4 s na `d06db34` czerwony (odrzucenie `blad_odczytu`, 40 prob). Czytaniem: plik nie trafia do `_znane`, odstep rosnie do 2 s, `Oczekiwanie` co 60 s; jedyny stan "bez konca i bez informacji" to plik, ktorego rozmiar / czas zmienia sie bez przerwy (ktos go stale dopisuje) - widoczny tylko w `stan()["czeka"]`, to zachowanie wlasciwe. Plik zajety przy zamknieciu programu wraca po restarcie TYLKO z nadrabianiem (S3, patrz D-N1). |
| P1 | **zalatwione** co do cudzego skrotu; **nowa N1** | Testy `plik_nadpisany_w_kolejce` i `plik_zmieniony_w_trakcie` na `d06db34` czerwone (stary kod daje `wynik`). Czytaniem: skrot przed analiza (`silnik.py:401-404`) i po niej (`417-423`); wynik nie moze juz trafic do zdarzenia z innym skrotem (zostaje tylko teoretyczne ABA: tresc B w trakcie i powrot do A przed skrotem koncowym). Ale porazka odczytu po analizie = `plik_zmieniony` - N1. |
| P2 a | **zalatwione** (narzedzie); skutek zalezy od A3 | Uruchomione S3: plik zajety przy `stop()`, restart bez nadrabiania - 0 zdarzen; z `znane` (zawsze False) - 1 zdarzenie `zastany=True`; z `zglos_zastane_od` - 1 zdarzenie. Testy wykonawcy (`od_czasu`, `funkcja_znane`) czytane - skrot tylko dla zgloszonych, `znane` raz na plik. Ten sam plik nie jest zglaszany drugi raz w tym samym przebiegu (kandydat blokuje watchdog i przeglad). Uwagi do kontraktu: D-N1, D-N2. |
| P2 b | **zalatwione** | Uruchomione K4: `stop()` z dwoch watkow naraz w trakcie startu procesu roboczego (prawdziwe `porownaj`, import Open3D): pierwszy 1,08 s i `[1]`, drugi od razu `[]`, proces roboczy zakonczony, jedno zdarzenie `zatrzymany`. Testy wykonawcy czytane. Czytaniem dwa waskie wyscigi: D-N3, D-N4. |
| P3 | **zalatwione** co do falszywych zgloszen; **D-N1** | Testy `blad_listowania`, `folder_z_historia`, `podfolder_niedostepny` na `d06db34` czerwone (3 / 3 / 2 zdarzenia dla plikow zastanych). Czytaniem: plik nieobecny na liscie jest zapominany dopiero po `os.stat` = brak; blad listowania samego folderu nic nie kasuje. Odwrotna strona (nowy skan w folderze, ktory pojawil sie po starcie, przepada bez nadrabiania) - uruchomione S4, D-N1. |
| P4 | **zalatwione** (kolizje, nadpisywanie, urwany zapis); **D-N6** | Czytaniem: zmiana nazwy bez nadpisania (`os.rename` na Windows), kolejny numer `_n`, plik tymczasowy kasowany przy wyjatku. Nazwa skanu w nazwie pliku i sprzatanie po zabiciu - D-N6. |
| P5 | **zalatwione** co do wycieku nazw; **nowa N2** | Czytaniem wszystkie drogi z procesu roboczego: wynik (`oczysc`), ostrzezenia, tekst i slad wyjatku (`czysc`), `PlikZmieniony` (same skroty), postep (stale nazwy etapow z `porownaj` - sprawdzone `porownaj.py:241-300`), `blad_startu` (przed zadaniem, bez puli), `_podglad.npz` (klucze `g<nr>_P` / `_d`), zdarzenia nadzorcy (bez nazw), `repr` zdarzenia (pula = foldery z zadania). Nie czyszczone: wyjscie bibliotek do `plik_logu` (pkt 5). Wydajnosc - uruchomione WYD: pula 400 folderow / 800 plikow = 2000 nazw, budowa 118 ms na zadanie, `oczysc` wyniku z 1042 tekstami 8-13 ms. Falszywe zamiany w polach decyzji - N2. |
| P6 | **zalatwione** dla zwyklej analizy; **D-N5** | Test P6 na `d06db34` czerwony (proces roboczy zyje 20 s po zabiciu okna). Uruchomione `eks_gil.py`: watek Pythona (jak `Straznik`) dostaje czas w trakcie `registration_ransac`, `registration_icp`, `cKDTree`, ale NIE w trakcie `segment_plane` i `estimate_normals` (przerwa watku = czas wywolania) - D-N5. Czytaniem: limit wlasny 630 s nie zabije zwyklego zadania wczesniej niz nadzorca (600 s). |
| D1 | zalatwione | czytane + test wykonawcy (nie uruchamialem) |
| D2 | zostaje (znana, opisana) | `silnik.md:104-107` |
| D3 | zalatwione | czytane: zdjecie z kolejki i `_biezace` pod jednym zamkiem, `None` po `_zglos` |
| D4 a / b | a zalatwione (czytane), b zostaje | |
| D5, D6 | zostaja do B2 | opisane w `scanner.md:118-119`, `:101` |
| D7 | opisane | `silnik.md:108-110` |
| D8 | zalatwione | test czytany (nie uruchamialem) |
| D9 | zalatwione | czytane: kolejnosc liczona z czasu plikow z luzem 0,1 s przy odstepie 0,3 s; test nadal wymaga 20 / 20 i kolejnosci zapisu - porzucone jest tylko zalozenie, ze symulator skonczyl w zadanej kolejnosci (uzasadnione) |
| D10 | czesciowo | brak testow dla N1, N2, D-N1 |
| D11 a / b, c | a zalatwione (test + czytane), b, c zostaja | |
| D12 | bez zmian w ocenie | 41,5 s z raportu nie sprawdzalem |
| prog 0,1 mm | zalatwione | poziom 3: `tol=0.1, tol_wzgl=0` (czytane) |

Testy rundy 1 nie zostaly oslabione poza jednym miejscem: `_sprawdz_rownosc` (`test_silnik.py:821`) czysci teraz takze wynik
wiersza polecen tym samym `CzyscicielNazw` - konieczne, ale przez to porownanie silnik = wiersz polecen nie wykryje zamiany,
ktora psuje wynik (N2). Poziom 3 jest silniejszy niz w rundzie 1.

## 2. Nowe uwagi (B = blokujaca, P = poprawic przed scaleniem, D = drobna / moze zostac jako znana)

| Nr | Waga | Plik:linia | Scenariusz (wejscie -> zly wynik) | Sprawdzone | Oczekiwane |
|---|---|---|---|---|---|
| N1 | P | `stanowisko/silnik.py:417-423` (oraz `401-404`, `487-488`, `321-326`); `opisy_modulow/silnik.md:59-61`; kontrakt w raporcie paczki ("`plik_zmieniony` = nie awaria (nowa tresc ma wlasne zdarzenie)") | Skrot po analizie nie da sie policzyc (`po = None`), choc tresc sie NIE zmienila: (a) w tej chwili inny program trzyma plik bez zgody na odczyt - dokladnie programy z B1 (kopia zapasowa, podglad w programie skanera, antywirus); (b) plik przeniesiony / przemianowany (archiwizacja przez program skanera, technik, synchronizacja) albo usuniety w ciagu 15-60 s analizy. Silnik odrzuca wynik jako `plik_zmieniony` z komunikatem "plik skanu zmienil sie w trakcie analizy (sha16 X -> brak pliku) - wynik odrzucony; nowa tresc ma wlasne zdarzenie skanu". W (a) nowego zdarzenia NIE BEDZIE (rozmiar i czas pliku bez zmian, `scanner` go nie zgloszy) - skan przepada. W (b) przy zmianie nazwy w obserwowanym folderze `scanner` zglasza plik pod nowa nazwa jako `duplikat=True` z TYM SAMYM `sha16` - a kontrakt kaze A3 rozpoznawac powtorki po `sha16`, wiec drugi raz analizy nie bedzie. Technik przy obu nie dostaje informacji, jesli A3 posluchal kontraktu. Do tego `_skrot16` czyta plik zwyklym `open` (bez `FILE_SHARE_DELETE`): dwa dodatkowe okna, w ktorych program skanera nie usunie / nie zastapi pliku (zapis "plik tymczasowy + zamiana" sie nie uda) - analiza robi to samo przy wczytaniu, ale teraz 3 razy na zadanie. | **Uruchomione** (`x\eks_silnik.py`, funkcja probna): K1 - plik trzymany bez wspoldzielenia 5 s pod koniec analizy, tresc bez zmian -> `blad plik_zmieniony`, wynik brak, komunikat jak wyzej. K2 - plik przemianowany w trakcie analizy przy dzialajacym `scanner` -> `blad plik_zmieniony` ("brak pliku") + zdarzenie scannera `skan_przeniesiony.stl`, ten sam `sha16`, `duplikat=True`, `duplikat_z=skan.stl`. | Odroznic "nie da sie przeczytac" od "inna tresc": najprosciej proces roboczy kopiuje skan do wlasnego pliku tymczasowego przez `otworz_zrodlo` (pelne wspoldzielenie), liczy skrot KOPII (= `skan_sha16` wyniku; inny niz w zdarzeniu = `plik_zmieniony` przed analiza) i analizuje kopie - wtedy skrot po analizie jest zbedny, przeniesienie / usuniecie / chwilowa blokada oryginalu nie szkodzi, a program skanera nie jest blokowany (koszt: kopia 50 MB, ulamek sekundy). Jesli zostaje skrot koncowy: przy `OSError` ponawiac jak w B1 i dac osobny rodzaj (np. `plik_niedostepny`) z prawdziwym komunikatem; w opisie dla A3: taki blad pokazac technikowi. Testy: uchwyt wylaczny w chwili skrotu koncowego i zmiana nazwy w trakcie analizy. |
| N2 | P | `stanowisko/silnik.py:174-180` (slownik nazw: kazdy folder z >= 2 literami, kazdy rdzen >= 3 znaki), `207-214` (`oczysc` - kazda wartosc tekstowa), `429`; `testy/test_silnik.py:821` | W puli (dowolnie gleboko - `rglob`) jest folder albo plik o nazwie rownej slowu ze slownika wyniku: folder `OK` (laboratoria trzymaja tak zatwierdzone prace) -> `inspekcja.status` `ok`; `Waxup` / `Most` / `Korona` -> `kandydaci[].typ` (`katalog.py:38`: korona, most, waxup, ...); `Poprawka` / `Ubytek` / `Sprawdz` -> `inspekcja.status` (`inspect.py:70`); kolory `status_gniazda`; plik `korona.stl` (rdzen 6 znakow). Kazde wystapienie w KAZDEJ plytce jest zamieniane na `<projekt>` albo `<projekt sha16>`. Zepsute pola trafiaja do zdarzenia, do pliku w `wyjscie` i do bazy A1 (`session.py:379` zapisuje `status_inspekcji`, `:182` porownuje `inspekcja.status` ze statusami "do powtorzenia"). Test rownosci silnik = wiersz polecen tego nie wykryje, bo obie strony czysci tak samo. | **Uruchomione** (`x\eks_silnik.py` K3, prawdziwy `Silnik` z funkcja probna zwracajaca wynik o ksztalcie `porownaj`; pula z folderami `OK`, `Waxup` i plikiem `korona.stl`): gniazdo 1 `inspekcja.status='<projekt>'` (bylo `ok`), `kandydat.typ='<projekt>'` (bylo `waxup`); gniazdo 2 `kandydat.typ='<projekt 4058de4db261af16>'` (bylo `korona`). Bezposrednio: `oczysc({'status': 'ok', 'typ': 'korona', ...})` -> `<projekt>`, `<projekt 4058...>`. | Czyscic tylko pola tekstow swobodnych (`ostrzezenia`, `uwagi`, `uklad_komunikat`, `blad`, `powod` itp. - lista w jednym miejscu) albo nigdy nie zamieniac wartosci rownej w calosci slowu ze slownikow wyniku (`inspect.STATUSY`, `match.STATUSY`, `porownaj.STATUSY_GNIAZDA`, typy z `katalog`, nazwy ukladow). Test z pula zawierajaca foldery `OK`, `Waxup` i plik `korona.stl`: statusy i typy bez zmian, nazwiska nadal usuniete; w `_sprawdz_rownosc` dodatkowo `oczysc(cli) == cli` dla puli atrap (cleaner nie zmienia wyniku bez nazw osobowych). |
| D-N1 | D | `stanowisko/scanner.py:337-351`, `553-555`, `566-568`; `opisy_modulow/scanner.md:69-75`, `110-114` | Druga strona P3: bez nadrabiania (`znane` / `zglos_zastane_od` / `zglos_zastane`) NOWY skan zapisany do folderu, ktory pojawil sie po starcie programu (dysk sieciowy, OneDrive podlaczony pozniej, folder zakladany przez program skanera przy pierwszym eksporcie) albo do podfolderu nieczytelnego przy starcie, jest "zastany": 0 zdarzen, 0 odrzucen, 0 `Oczekiwanie`, nic w `stan()`. Tak samo plik zajety w chwili zamkniecia programu po restarcie (S3). Z nadrabianiem skan wraca, ale z flaga `zastany=True`, choc zapisano go w czasie pracy programu. W aplikacji zakryte, jesli A3 poda nadrabianie (opis: "A3 MA podac") - dlatego D, nie P; domyslny `Scanner(folder)` (symulator, przyszle narzedzia) gubi po cichu. | **Uruchomione** S4: folder zalozony 1 s po starcie i od razu zapisany `nowy.stl` -> bez nadrabiania 0 zdarzen; `zglos_zastane_od=czas startu` -> 1 zdarzenie `zastany=True`; `znane` -> 1 zdarzenie `zastany=True`. S3 jak w tabeli pkt 1. | Tani bezpiecznik: przy POZNYM ustaleniu zastanych (folder / podfolder pojawil sie po starcie) pliki o czasie modyfikacji pozniejszym niz start obserwatora traktowac jako nowe (`zastany=False`); albo co najmniej ostrzezenie w logu, gdy `Scanner` rusza bez nadrabiania. Test S4. |
| D-N2 | D | `stanowisko/scanner.py:288`, `335` (`przygotuj` w watku `start()`), `554`, `567` (watek `scanner`), `377-378`; `opisy_modulow/scanner.md:21`, `111-114`, `117` | Kontrakt `znane` jest niedookreslony w trzech miejscach: (1) WATEK - `znane` wolane jest w watku, ktory wola `start()` (okno Qt), a dla folderu / podfolderu ustalonego pozniej w watku obserwatora; opis mowi tylko, ze funkcje zwrotne ida w watku obserwatora. Polaczenie `sqlite3` z watku okna rzuci w watku obserwatora `ProgrammingError` -> plik "nieznany" -> cala zawartosc poznego folderu zgloszona od nowa + `LOG.exception` na kazdy plik. (2) FORMAT - A1 trzyma `skany.czas_pliku` jako czas LOKALNY ISO uciety do sekund (`session.py` `_czas_iso`), a `znane` dostaje `mtime_ns`; naiwne porownanie = zawsze "nieznany" = przy kazdym starcie skrot calej historii folderu i zgloszenia do odsiania po `sha16` (strat nie ma, jest koszt i szum). `zglos_zastane_od` z takiego zapisu (uciecie, czas letni) daje tylko duplikaty, nie straty - to w porzadku. (3) ZNACZENIE - "przyjety" musi znaczyc "jest wynik (albo zapisane zadanie z `stop()`)", nie "przyszlo zdarzenie": awaria miedzy zdarzeniem a wynikiem = skan znany, a nieprzeanalizowany. | **Uruchomione** (S3, S4): `znane` wolane w `MainThread` przy starcie, w watku `scanner` dla folderu poznego. Reszta czytaniem (`origin/e3/a1`: `session.py`, `baza.py`). | Zdania w `scanner.md` dla A3 (pkt 3 nizej): watek(i), wymagana bezpiecznosc watkowa (np. zbior wczytany przy starcie), sposob porownania z rekordem A1 (sciezka znormalizowana `normcase(abspath)`, rozmiar, czas w formacie A1), znaczenie "znany". |
| D-N3 | D | `stanowisko/silnik.py:557-566` | `stop()` po `join(czekaj_s)` nie sprawdza, czy watek nadzorcy naprawde sie skonczyl. Gdy `na_zdarzenie` blokuje dluzej niz 5 s na watku, ktory wola `stop()` (np. przekazanie do okna z czekaniem), albo `p.start()` trwa > 5 s (zajety komputer, antywirus): `stop()` zwraca zadanie w toku jako niezakonczone, a nadzorca za chwile dostarcza dla niego `wynik` / `blad` - po restarcie analiza drugi raz; przy wolnym `p.start()` proces roboczy powstaje juz po `_zamknij_proces` (konczy go `Straznik` po wyjsciu programu). Z `lacznik_qt` (zalecany) nie wystepuje. | Czytaniem. | Gdy nadzorca zyje po `join` - czekac dalej albo oznaczyc, ze lista moze sie pokrywac z pozniejszym zdarzeniem; w opisie: `na_zdarzenie` nie moze czekac na watek wolajacy `stop()`. |
| D-N4 | D | `stanowisko/silnik.py:591-597` | `zlec` sprawdza `_zatrzymany` poza zamkiem: `zlec_skan` z watku obserwatora rownolegle ze `stop()` z watku okna moze dopisac zadanie do kolejki juz skopiowanej i wyczyszczonej - `zlec` zwraca numer, zadanie nie ruszy i nie ma go w `niezakonczone`. Okno mikrosekundowe. Kolejnosc w `closeEvent` (najpierw `scanner.stop()`, potem `silnik.stop()`) nie jest nigdzie zapisana; odwrotna daje `RuntimeError` w funkcji `na_skan` (zlapane i zalogowane przez `scanner`, skan wraca tylko z nadrabianiem). | Czytaniem. | Sprawdzenie `_po_stopie` pod zamkiem w `zlec`; kolejnosc zatrzymania w opisie dla A3. |
| D-N5 | D | `stanowisko/silnik.py:241-276`; `opisy_modulow/silnik.md:56-58` | `Straznik` to watek Pythona. Czesc wywolan Open3D trzyma GIL przez cale wywolanie (zmierzone: `segment_plane`, `estimate_normals`; `plate.py:162` uzywa `segment_plane`). Po smierci okna proces roboczy konczy sie dopiero po wyjsciu z biezacego takiego wywolania (sekundy), a zawieszenie W SRODKU takiego wywolania (klasa bledu z P3a pkt 5.1) zostawia proces na zawsze. Zdanie "takze W TRAKCIE analizy (zmierzone: 0,4 s)" opiera sie na tescie z `time.sleep` (zwalnia GIL). | **Uruchomione** `x\eks_gil.py` (1,5 mln punktow losowych): najdluzsza przerwa watku tykajacego co 0,1 s = czas wywolania dla `segment_plane` (0,22 s) i `estimate_normals` (0,84 s); 0,09-0,13 s dla `compute_fpfh_feature`, `registration_ransac_based_on_feature_matching`, `registration_icp`, `cKDTree`. Prawdziwego `porownaj` z zabiciem okna nie uruchamialem. | Pewnosc na poziomie systemu: proces okna wklada proces roboczy do obiektu zadania Windows (Job Object) z `KILL_ON_JOB_CLOSE` - system konczy proces roboczy niezaleznie od jego stanu; albo co najmniej poprawic zdanie w opisie. |
| D-N6 | D | `stanowisko/silnik.py:337-341`, `346`, `370-394`; `opisy_modulow/silnik.md:19`, `40`, `103`; `testy/test_silnik.py:862` | Nazwa pliku w `wyjscie` niesie `_bezpieczna_nazwa(nazwa skanu)` (60 znakow ASCII): jesli program skanera nazywa eksport wg zlecenia, nazwisko (bez polskich liter) laduje w nazwie pliku. A1 swiadomie usunal nazwe skanu z nazwy pliku wyniku (`session.py`: "skaner moze nazywac pliki wg zlecenia ... recenzja PR #16 runda 3, D1 i D2"); nazwa nic nie wnosi (jest czas i `sha16`, A3 ma sciezke w `pliki`). Dlugosc sciezki: nazwa do ok. 125 znakow + folder - w normie dzieki przycieciu do 60. Po zabiciu procesu w trakcie zapisu (limit, `Straznik`) zostaje `<plik>.<pid>.tmp` albo `_wynik.json` bez `_podglad.npz` - nic tego nie sprzata; `FileExistsError` przy `npz` nie jest obsluzony (tylko przy dwoch procesach w jednym folderze w tej samej sekundzie). Komentarz testu "wzor nazw jak w A1" jest nieprawdziwy. | Czytaniem. | Nazwa `<czas>_<sha16>[_n]_wynik.json` / `_podglad.npz` jak w A1 (jedna linia + test i opis); sprzatanie `*.tmp` starszych niz np. 1 dzien przy starcie procesu roboczego - do decyzji. |
| D-N7 | D | `testy/test_silnik.py`, `testy/test_scanner.py` (luki D10 po rundzie 2) | Brak testow: skrot koncowy przy pliku zablokowanym / przeniesionym (N1), pula z nazwami ze slownika wyniku (N2), nowy skan w folderze poznym bez nadrabiania (D-N1), P6 z wywolaniem natywnym trzymajacym GIL (D-N5). `test_stop_nie_gubi_watku_liczacego` liczy watki o nazwie `scanner` w calym procesie - jesli inny test zostawi zywy watek (stop() przekroczy czas), wynik zalezy od kolejnosci testow. | Czytaniem. | Dopisac przy N1 / N2; w tescie D11 liczyc tylko watki tego obiektu (np. `sc._watek`). |

Wyscig z pkt 8 zadania (plik zly odrzucany, gdy skaner dopisal reszte miedzy sprawdzeniem a `ktos_pisze`): poprawka
`scanner.py:604-605` (ponowny `stat` i zgodnosc rozmiaru z `sprawdz_stl`) zamyka okno; pozostaly wyscig (dopisanie po tym
sprawdzeniu) daje najwyzej falszywy wpis, po ktorym zmiana podpisu i tak wywoluje ocene od nowa - bez straty. Zmiana "pliki
zastane spoza wzorca nie dostaja wpisu" - tylko mniej szumu w dzienniku, nic nie ginie (zdarzenia dla nich nie bylo nigdy).

## 3. Ocena kontraktu dla aplikacji (A3)

Kontrakt w `scanner.md` / `silnik.md` / raporcie paczki jest uzyteczny i w wiekszosci kompletny (nadrabianie, `stop()` z lista,
plik startowy bez Qt na gorze, `freeze_support`, `lacznik_qt`). Do dopisania przed A3 (bez zmian kodu, poza N1 / N2):
1. `znane` jest OBOWIAZKOWE (bez niego gina skany z D-N1); znaczenie "znany" = skan z zapisanym wynikiem (dowolny status)
   albo zadanie zapisane z `stop()`; porownanie z rekordem A1: sciezka po `os.path.normcase(os.path.abspath())`, `rozmiar`,
   czas pliku w formacie A1 (lokalny ISO do sekund) - albo A1 / A3 zapisuje `mtime_ns`; funkcja bezpieczna watkowo (wolana
   w watku `start()` i w watku obserwatora) i szybka (przy starcie raz na kazdy plik historii, synchronicznie w `start()`).
2. Jedno zrodlo prawdy dla nadrabiania: zadania z `stop()` zlecane po starcie i zdarzenia `zastany=True` ze `scanner` moga
   dotyczyc tego samego pliku - A3 odsiewa po (sciezka, `sha16`) PRZED `zlec`. `zastany=True` nie znaczy "stary" (D-N1).
3. `closeEvent`: najpierw `scanner.stop()`, potem `niezakonczone = silnik.stop()` (D-N4); `na_zdarzenie` nie czeka na watek
   okna (D-N3) - najprosciej `lacznik_qt`.
4. `blad` `plik_zmieniony` POKAZAC technikowi (do czasu N1 moze znaczyc "plik zablokowany / przeniesiony", bez nowego
   zdarzenia); zdarzenie `duplikat=True` po `plik_zmieniony` tego samego `sha16` analizowac, nie odsiewac.
5. `ZdarzenieSilnika.pliki` - jedyne zrodlo nazw plikow `wyjscie` (nie skladac nazwy samemu; D-N6).
6. Do czasu N2: wartosci statusow i typow w wyniku moga byc zastapione znacznikiem `<projekt>` - A1 / A3 nie powinny na tym
   polegac bez poprawki.

## 4. Czego NIE sprawdzilem

- Pelnego pytest ani calych plikow testow na nowym kodzie - przeczytalem konce logow wykonawcy (`r2_scanner2` 35 passed,
  `r2_silnik1` 33 passed / 5 skipped, `r2_pytest_caly` 507 passed / 8 skipped, `r2_ref` 5 passed; `r2_scanner1` - 1 failed
  przed poprawka wyscigu, zgodnie z raportem). Nowych testow D1, D8, D11, P2, P4, P5 nie uruchamialem ani na nowym, ani na
  starym kodzie.
- Wariantow na skanach odniesienia i liczby 41,5 s (kryterium 6).
- `Straznik` z prawdziwym `porownaj` i zabiciem okna w trakcie (tylko mikroproba GIL na danych losowych); zawieszenia Open3D.
- Wyjscia bibliotek do `plik_logu` pod katem nazw z puli (komunikaty C++ Open3D, `logging` bez obslugi): w sciezce analizy
  nie znalazlem `print` ani `logging` z nazwami (ostrzezenia ida przez `warnings` i sa czyszczone) - tylko czytaniem.
- Prawdziwego dysku sieciowego / OneDrive (bledy listowania w P3 tylko czytaniem), uspienia komputera w trakcie analizy,
  wersji zamrozonej, czasu `start()` przy tysiacach plikow z `znane`.
- Zachowania prawdziwego programu skanera (sposob otwierania i przenoszenia plikow) - od niego zalezy, jak czesto zdarzy sie N1.
