# Raport recenzenta - PR #63 (E3-I1: instalator okienkowy, Python w paczce), runda 1

- Data: 25.11.2026 (19:27 - 20:36), recenzent: konto 3 na PC, zlecenie `rec-i1-r1`, tor ciezkich krokow 4.
- Zakres: `git -C <PC-katalog>\qc diff main...origin/e3/i1`, HEAD `90d4a2c` (21 plikow, +2766 / -85 wg `git diff --stat`).
- Miara: zlecenie `<PC-katalog>\konto3\zlecenia\i1.md` (wymagania 1-6, kryteria K1-K7).
- Metoda: przeglad diffu (instalator, kreator, okno, napisy, starter, skrypty .cmd, budowa, testy, instrukcja), potem wlasne
  proby na paczce probnej `<PC-katalog>\wydania\Stanowisko_0.3.9-i1.zip` rozpakowanej do katalogu z polskimi znakami, spacja
  i nawiasem w nazwie; raport wykonawcy przeczytany na koncu.
- Uruchomiono: proby A-F (4 pelne instalacje z paczki, 1 przerwana, 2 ponowne tej samej wersji, 1 instalacja 0.3.3 starym instalatorem, 5 powrotow), testy paczki
  (48 passed, 2 deselected - patrz P3), 7 wstrzykniec bledow, 10 pomiarow kodu wyjscia procesu pytest. Pelnego pytest nie
  powtarzano. Kopia do prob `<PC-katalog>\qc-wt\rec-i1` po probach czysta (`git status --short` pusty, HEAD `90d4a2c`).
- Logi i skrypty prob: `<PC-katalog>\konto3\robocze\rec-i1-r1\` (nazwy plikow w sekcji 2).
- Uwaga o przebiegu: sesja recenzenta zginela 3 razy (19:54, 19:58, 20:01) - za kazdym razem w tym samym tescie paczki (P3).
  Wnioski sprzed przerwan odtworzono z logow prob i z kodu; kazda liczba ponizej ma log.

## 0. Werdykt

**Do scalenia po poprawkach.** B 0 / P 3 / D 5.

Droga wlasciciela (rozpakowana paczka -> dwuklik `Instaluj.cmd` -> okno -> ikony -> program) dziala w moich probach bez Pythona
w `PATH` i bez zadnego polecenia do wpisania; instalacja nie siega po Pythona z systemu i nie zalezy od paczki po instalacji;
aktualizacja 0.3.3 -> 0.3.9-i1 i powroty zostawiaja ustawienia i baze bez zmian. Nie znalazlem bledu, ktory zatrzyma instalacje
albo zostawi komputer w stanie, z ktorego nie da sie wyjsc ponownym uruchomieniem. Trzy uwagi P: zamkniecie okna w trakcie
instalacji nie przerywa instalatora (P1), testy okna koncza proces pytest kodem awarii (P2), test ikon uruchamia skrot przez
powloke systemu i w mojej sesji 3 razy z 3 zabil cale drzewo procesow sesji (P3).

## 1. Uwagi

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| P1 | P | `instalacja/okno_instalatora.py:586-593` (`closeEvent`), `instalacja/kreator.py:200-212` (`uruchom_instalacje`) | Osoba instalujaca zamyka okno w kroku "Program i pakiety (kilka minut)" i odpowiada twierdzaco na "Przerwac?". Flaga `przerwij` jest sprawdzana tylko po kolejnym wierszu wyjscia instalatora, a w kroku pip wierszy nie ma przez minuty; proces okna konczy sie (watek jest demonem), instalator dziala dalej w tle i trzyma blokade. Proba B: 3 procesy python zyly jeszcze 44 s po zamknieciu okna; ponowne `Instaluj` od razu = kod 6 "inna instalacja albo powrot juz trwa w tym katalogu (drugie okno) / Poczekaj, az tamto okno skonczy" - okna nie ma; potem porzucony instalator pada na `print` (`OSError: [Errno 22]`, slad wyjatku w `dziennik_instalacji.txt`), wersja zostaje `NIEDOKONCZONA`; uruchomienie po odczekaniu sprzata i konczy kodem 0 (83 s). Na laptopie z antywirusem czekanie moze trwac kilka minut. `proces.kill()` zabilby tez tylko `instalator.py` - pip (proces potomny instalatora) zostaje, a blokada jest juz zwolniona. Testu przerwania nie ma (`testy/test_okno_instalatora.py:54` - `przerwij` wystepuje tylko w sygnaturze atrapy). | Po potwierdzeniu przerwania zakonczyc cale drzewo procesow instalatora (np. `taskkill /T /F /PID` albo Job Object z zamknieciem przy koncu okna) i zamknac okno dopiero, gdy proces sie skonczyl; sprawdzac flage niezaleznie od wierszy wyjscia. Albo (prostsze na 28.11): w trakcie instalacji nie pozwalac zamknac okna - komunikat "Poczekaj do konca instalacji". Test: instalator-atrapa, ktory milczy 30 s - po przerwaniu proces i jego potomek nie zyja, ponowna instalacja od razu kod 0. Dopisac zdanie w instrukcji (punkt 1.5). |
| P2 | P | `testy/test_okno_instalatora.py:156`, `:227`, `:270` (testy `test_okno_cztery_kroki`, `test_okno_blad_instalatora_po_polsku_i_ponowna_proba`, `test_zrzuty_czterech_krokow`), fixture `app` `:26-30` | Po tej paczce proces pytest konczy sie kodem -1073741819 (0xC0000005) juz PO wierszu "N passed". Moje pomiary: plik testow okna 3 z 3 przebiegow (w tym raz bez testu z prawdziwa instalacja), kazdy z 3 wymienionych testow uruchomiony osobno (po 1 razie) - awaria 3 z 3; `test_okno_walidacje`, `test_okno_aktualizacja_zostawia_ustawienia`, `test_kazdy_kod...` osobno - kod 0. Pelny pytest wykonawcy tez: `ciezkie.log` "2026-11-25 19:05:35 KONIEC i1 tor 2 kod -1073741819", a pelny pytest paczki u1b tego samego dnia (ta sama baza `main`) - kod 0. Raport wykonawcy podaje "2533 passed / 0 failed" i o kodzie procesu milczy. Skutek: kazdy pelny pytest po scaleniu zwraca kod awarii - `ciezki.ps1`, skrypty i przyszle automaty widza porazke przy komplecie zaliczonych testow, a prawdziwa awaria procesu przestaje byc odroznialna. Samo okno z paczki NIE pada (proba E: kody procesu 0 / 0 / 5 na platformie offscreen i windows). | Znalezc obiekt Qt, ktory dozywa konca interpretera (okno, `_Sygnaly`, watek `instalator`): w testach po `okno.close()` zniszczyc okno (`deleteLater` + `processEvents`) i poczekac na koniec watku, ewentualnie to samo w `closeEvent`. Dowod poprawki: kod procesu 0 dla `pytest testy\test_okno_instalatora.py` i dla pelnego pytest (wiersz `KONIEC ... kod 0` w `ciezkie.log`), podany w raporcie. |
| [usunieto w kopii: opis dostepu ssh]
| D1 | D | `instalacja/okno_instalatora.py:588` | Pytanie "Instalacja trwa... Przerwac?" ma przyciski po angielsku: proba D4 na bibliotece okna z paczki daje `['&Yes', '&No']`; w `okno/` jest 0 plikow tlumaczen `.qm`, kod nie instaluje tlumacza. | `QMessageBox` z wlasnymi przyciskami "Tak" / "Nie" (domyslny "Nie"). Znika razem z wariantem "nie pozwalac zamknac" z P1. |
| D2 | D | `instalacja/kreator.py:102-137`, `instalacja/okno_instalatora.py:545`, `instalacja/instalator.py:1518` | (a) Dlugosc sciezki miejsca instalacji nie jest sprawdzana w kroku 1 okna: proba A - 74 znaki przechodza "Dalej" i "Instaluj", blad dopiero w kroku 3 instalatora (kod 6, limit 68 znakow dla tej paczki); stan czysty (katalog nie powstal). (b) Okno pokazuje wiersze `CO ZROBIC` instalatora doslownie - odsylaja do wiersza polecen: "Wybierz krotszy katalog, np. zainstaluj.cmd /katalog C:\Stanowisko", "uruchom polecenie ponownie" (widac na zrzucie `instalator_5_blad.png`), "uruchom zainstaluj.cmd JESZCZE RAZ". Zdanie kodu po polsku jest nad nimi, wiec da sie zrozumiec. | (a) Ta sama kontrola dlugosci w `sprawdz_foldery` (liczba znakow w komunikacie). (b) W oknie zamieniac w radach "zainstaluj.cmd ..." / "polecenie" na "Sprobuj ponownie" albo dopisac zdanie "W oknie: przycisk Sprobuj ponownie". |
| D3 | D | `instalacja/wzory/start_bez_konsoli.pyw:58` | Plik wyjscia `dane\ostatni_start_<cel>.txt` jest otwierany w trybie `wb`. Drugi dwuklik ikony, gdy program juz dziala (kod 3, bez komunikatu), obcina plik wyjscia dzialajacego programu - pierwszy proces pisze dalej od swojej pozycji. Dotyczy tylko pliku diagnostycznego. Wynik przegladu, nie proby. | Osobny plik na start (np. z godzina, kilka ostatnich) albo otwarcie z dopisywaniem i naglowkiem startu. |
| D4 | D | `instalacja/okno_instalatora.py:299-302`, `:523-530` | W kroku 5 pasek i napisy stoja bez ruchu przez caly czas instalacji pakietow (proba B: od wiersza "instalacja 73 pakietow" do nastepnego wiersza 51 s przy calej instalacji 62-64 s; z pendrive'a i z antywirusem - minuty). Okno wyglada na zawieszone, co zacheca do zamkniecia (P1). | Pasek w trybie "zajety" albo licznik czasu "trwa 2:15" w kroku 5. |
| D5 | D | `instalacja/instalator.py:300`, `instalacja/napisy_instalatora.py:12` | Instalacja dopisuje pliki do ROZPAKOWANEJ PACZKI: po moich probach 61 plikow `__pycache__` w `python/Lib` paczki (1593 -> 1654 pliki; kontrola `SHA256SUMS` ich nie liczy, kolejne instalacje z tej samej paczki przeszly - kod 0, 4 z 4). Kontrola wersji Pythona uruchamia Pythona paczki bez `-B`. Napis okna "Niczego nie zmienia poza folderem instalacji" jest przez to (i przez ikony na pulpicie) niescisly. | `-B` w `sprawdz_pythona` (albo `PYTHONDONTWRITEBYTECODE=1` w srodowisku procesow potomnych z Pythona paczki); napis: "...poza folderem instalacji i ikonami na pulpicie". |

## 2. Wlasne proby

Paczka: `Stanowisko_0.3.9-i1.zip`, 479 314 803 B, SHA-256 `1667ab3e882d9887182956ad7649af868e1f701488a95fc6d814429f88cd7b83` (moj
pomiar = plik `.sha256` = `KONIEC_i1.txt`); po rozpakowaniu 1593 pliki. `wydanie.json`: commit `8272687b2ac2`, Python 1322 pliki,
okno 37 plikow. We wszystkich probach: `PATH` = tylko katalogi Windows (`where python`, `where py`: brak), bez zmiennych
`PYTHON*`, `STANOWISKO_*`, `QT_*`. Foldery prob (paczka, instalacja, skany, projekty, pulpit) maja w nazwach polskie litery i spacje.

| Proba | Polecenie / co zrobiono | Wynik |
|---|---|---|
| A (`proba_a_1_za_dluga.log`) | tryb bez okna z Pythona paczki, miejsce instalacji 74 znaki | kod 6 w 4 s, "sciezka katalogu instalacji jest za dluga", katalog nie powstal (D2) |
| A2 (`proba_a2.log`) | `python\python.exe -I -B program\instalacja\okno_instalatora.py --bez-okna` z folderami i 2 osobami z polskimi literami | kod 0 w 64 s; sumy 1592 z 1592; Python skopiowany 1322 z 1322; pakiety 73 z 73; `SAMOKONTROLA: ZIELONA (ok 14, ostrzezenia 7)`; `pyvenv.cfg home` = `<instalacja>\python\3.12.10`; `ustawienia.toml`: 2 foldery i 2 osoby zapisane poprawnie (UTF-8); 2 ikony, cel `<instalacja>\python\3.12.10\pythonw.exe`, argumenty `-I -B "<instalacja>\start_bez_konsoli.pyw" stanowisko` / `dzien_skanera` |
| A4 (`proba_a2.log`) | katalog paczki zmieniony z nazwy (paczka niedostepna): `Samokontrola.cmd --bez-sieci`, starter `stanowisko --atrapa --zamknij-po 5`, starter `dzien_skanera --nowa --zamknij-po 5` | kody 0 / 0 / 0, samokontrola ZIELONA - program nie zalezy od paczki |
| B (`proba_b.log`, `przerwij.py`) | zamkniecie okna 8 s po starcie instalacji pakietow (logika `kreator.py` z paczki, bez zmian w kodzie) | instalator zyje 44 s po zamknieciu; ponowienie od razu: kod 6 "drugie okno"; po odczekaniu: kod 0 w 83 s, "usunieto niedokonczona instalacje", ikony 2 z 2 (P1) |
| C (`proba_c.log`) | 0.3.3 starym instalatorem (`zainstaluj.cmd /python <Python systemu>`), aktualizacja paczka probna logika okna, `Wersje.cmd`, `Wroc_do_poprzedniej.cmd` 2 razy, starty | kody: 10 (pierwszy przebieg 0.3.3, ustawienia do uzupelnienia - jak przed paczka), 0, 0 (aktualizacja, 68 s), 0, 0; suma `ustawienia.toml` bez zmian w 6 z 6 pomiarow; `Wersje.cmd` pokazuje 2 wersje (BIEZACA / poprzednia); po powrocie do 0.3.3 ikony (cel: Python z katalogu instalacji + starter) uruchamiaja 0.3.3 - kod 0; `Samokontrola.cmd` 0.3.3 i nowej: ZIELONA, kod 0 |
| C5 (`proba_c5.log`, `zaloz_baze.py`) | to samo z zalozona baza (86 016 B): powrot, aktualizacja (wersja juz zainstalowana), powrot, powrot | kody 0 / 0 / 0 / 0; suma bazy bez zmian w 4 z 4 pomiarow, ustawien 4 z 4; kopia bazy przed aktualizacja: 1, "quick_check ok"; wskazniki biezaca / poprzednia zgodne po kazdym kroku |
| D1 (`proba_d.log`) | tryb bez okna, 7 zlych wyborow: brak folderu skanow, brak osoby, folder nie istnieje, sciezka wzgledna, srednik, dysk nie istnieje, osoba powtorzona | kod 12 w 7 z 7, zdanie po polsku w 7 z 7 (np. "Popraw wybor: Wskaz folder ze skanami."), katalog instalacji nie powstal |
| D2 (`proba_d.log`) | 1 bajt dopisany do `python\Lib\this.py` w paczce; osobno: brak kola numpy | kod 3 w 2 z 2: "sumy SHA-256 paczki niezgodne: 1 z 1592 plikow (zmieniony plik ...)" / "(brak pliku ...)", "Niczego nie zmieniono", katalog nie powstal; plik przywrocony (suma zgodna) |
| D3 (`proba_d3_recznie.log`) | `Instaluj.cmd` uruchomiony jak dwuklikiem (`cmd /c`) | kod skryptu 0; proces `pythonw.exe` z katalogu paczki; moduly: 15 z `okno\` paczki, 10 z `python\` paczki, 0 bibliotek Qt / PySide spoza paczki, 0 `python3*.dll` / `.pyd` spoza paczki; `msvcp140*`, `vcruntime140*` ladowane z paczki. Moj skrypt wisial tu 10 min na `Start-Process -Wait` - blad skryptu, nie paczki |
| D4 (`proba_d.log`, `qt_przyciski.py`) | napisy przyciskow pytania na bibliotece okna z paczki | `['&Yes', '&No']`, plikow `.qm` 0 (D1) |
| D5, D6 (`proba_d.log`) | instalacja przy `USERPROFILE`, `APPDATA`, `LOCALAPPDATA`, `TEMP`, `TMP` w katalogu z polskimi literami i spacja; potem 2 startery | kod 0 w 62 s, ZIELONA (ok 14, ostrzezenia 7), `home` = `<instalacja>\python\3.12.10`, ikony 2 z 2; startery 0 / 0 |
| E (`proba_e.log`, `okno_wyjscie.py`) | kod wyjscia procesu okna (Python i Qt z paczki, droga jak `main()`): samo otwarcie i zamkniecie / 4 kroki z atrapa instalatora / blad kod 5; platforma offscreen i windows | 0 / 0 / 5 na obu platformach (6 z 6 zgodne z oczekiwaniem) - okno nie pada przy wyjsciu |
| F1 (`proba_f.log`, `skrot_zapas.py`) | ikony droga zapasowa (`STANOWISKO_SKROT_BEZ_POWERSHELL=1`, wlasny zapis `.lnk`), odczyt przez `WScript.Shell`, start celu skrotu | 2 z 2 skroty; cel, argumenty, katalog roboczy i opis odczytane poprawnie (nazwa z polska litera tez); start celu: kody 0 / 0 |
| F2 (`proba_f.log`) | ikon nie da sie zalozyc (folder pulpitu nie istnieje), ponowna instalacja tej samej wersji | kod 0; "SKROT NIEUDANY" 2 z 2 z pelna sciezka pliku `.cmd`; zdanie: "Ikony ... nie dalo sie zalozyc na pulpicie (zasady tego komputera). Program uruchomisz plikiem Stanowisko.cmd w folderze instalacji..." |
| Sumy i podpisy | `Get-FileHash` pakietu `python.3.12.10.nupkg` (14 515 433 B); `Get-AuthenticodeSignature` 6 plikow paczki | suma `0eb85c2d...e3b8` = `PYTHON_NUGET_SHA256` w kodzie = plik `.sha256` obok pakietu; podpisy Valid 6 z 6 (`python.exe`, `pythonw.exe`, `python312.dll`, `Qt6Core.dll`, `QtWidgets.pyd`, `Shiboken.pyd`) |
| Testy paczki (`testy_paczki4.log`) | `pytest -q` na `test_instalacja_i1.py`, `test_okno_instalatora.py`, `test_zbuduj_wydanie.py`, `test_instalacja.py::test_p6...` z `--deselect test_ikony_na_pulpicie_przez_starter` | 48 passed, 2 deselected, 0 failed w 19,69 s; kod procesu -1073741819 (P2). Przebiegi 1-3 z tym testem (`testy_paczki.log`, `2`, `3`): log urwany po 11 testach, sesja zabita (P3) |
| Kod wyjscia pytest (`kod_wyjscia_pytest.log`) | 10 uruchomien: plik okna 2 razy, plik okna bez testu z prawdziwa instalacja, `test_instalacja_i1.py` bez testu ikon, 6 testow okna pojedynczo | kod -1073741819 w 6 z 10 (zawsze gdy w przebiegu jest ktorys z 3 testow z P2), kod 0 w 4 z 10 |
| Wstrzykniecia (`wstrzykniecia.log`) | 7 zepsuc kodu w mojej kopii, po kazdym test i `git checkout`: budowa bez kontroli sumy pakietu Pythona; pobranie bez kontroli sumy; okno bez kontroli wolnego miejsca; kopia Pythona bez porownania sumy istniejacego pliku; kod 11 bez zdania; okno bez `--python-z-paczki`; wartosci okna nadpisuja istniejacy plik ustawien | wykryte 7 z 7 (test pada). Pierwszy przebieg (`wstrzykniecia_1_bledny_skrypt.log`) mial blad mojego skryptu (zmienna nadpisana) - powtorzony w calosci |
| Log pytest wykonawcy | ostatni wiersz `<PC-katalog>\konto3\robocze\i1\logi\pytest_pelny.log` | "2533 passed, 9 skipped, 1 warning in 1914.79s (0:31:54)" - zgodne z raportem; kod procesu wg `ciezkie.log`: -1073741819 (P2) |

Punkty szczegolne zlecenia recenzji:

1. Bez terminala: od dwukliku do programu nie ma kroku z poleceniem (D3, A2, F - logika okna; samo klikanie w oknie sprawdzaja testy
   paczki z atrapa instalatora, zrzuty 5 z 5 obejrzalem 2: krok Instalacja i ekran bledu). Kazdy z 12 kodow instalatora ma zdanie po
   polsku (test + wstrzykniecie W5); rady `CO ZROBIC` sa pokazywane doslownie i czesc odsyla do polecenia (D2).
2. Python z systemu: `Instaluj.cmd` i okno biora zawsze `python\` z paczki z opcja `-I` (bez `PATH`, `py`, rejestru, zmiennych);
   `STANOWISKO_PYTHON` i `/python` maja pierwszenstwo tylko w `zainstaluj.cmd` (`zainstaluj.cmd:28-34`) - zgodnie ze zleceniem
   paczki, punkt 2. Dowod: A2, D3, D5 (`home`, moduly procesu), A4 (paczka niedostepna).
3. Przerwanie: P1. Zajety plik / dzialajacy program: kod 5 jak dotad (przeglad; bez wlasnej proby). Brak miejsca: kontrola w kroku 1
   okna (test + wstrzykniecie W3) i w instalatorze (przeglad); prawdziwego braku miejsca nie probowalem.
4. Aktualizacja i powrot: C, C5.
5. Sciezki: A2, D5 (polskie litery i spacje w paczce, instalacji, skanach, projektach, pulpicie, profilu i `TEMP`); dluga sciezka: A (D2).
6. Sumy: budowa (testy + W1, W2, pomiar sumy pakietu), instalacja (D2). Okno startuje z plikow paczki przed kontrola sum (inaczej
   sie nie da) - uszkodzony plik Pythona wykrywa krok 1 instalatora; uszkodzona biblioteka okna = okienko systemowe
   "Nie mozna otworzyc okna instalatora..." (`okno_instalatora.py:665-668`, przeglad).
7. Ikony: A2, C, F1, F2.
8. `zainstaluj.cmd`, `Wersje.cmd`, `Wroc_do_poprzedniej.cmd`, samokontrola: wzory `.cmd` bez zmian w diffie (nowy tylko starter),
   `zainstaluj.cmd` +11 / -1 wiersz (galaz `:z_paczki`); proby C i C5 (stary instalator 0.3.3, `Wersje.cmd`, 5 powrotow, `Samokontrola.cmd` 2 razy).

## 3. Kryteria zlecenia

| Kryterium | Ocena | Dowod |
|---|---|---|
| K1 paczka probna | potwierdzone wlasna proba | rozmiar i suma zip z mojego pomiaru; 1592 pliki + `SHA256SUMS` (sumy zgodne 1592 z 1592 w kroku 1 instalatora) |
| K2 instalacja bez Pythona w `PATH` | potwierdzone wlasna proba | A2, D5: kod 0, samokontrola zielona, `pyvenv.cfg home` w katalogu instalacji |
| K3 start programu i "Dnia skanera" | potwierdzone wlasna proba (starter ikon: 11 startow kod 0; `Samokontrola.cmd` 3 razy kod 0); `Stanowisko.cmd` / `Dzien_skanera.cmd` nowej wersji - potwierdzone przegladem (pliki bez zmian) i wg wykonawcy | A4, C, D6, F1 |
| K4 okno - testy bez ekranu, zdania kodow, zrzuty | potwierdzone wlasna proba, z zastrzezeniem P2 | 11 z 11 testow okna zalicza; W3, W5, W6 wykryte; D1 7 z 7; zrzuty 5 plikow PNG w `Ramki/etap3/nowy_interfejs/zrzuty/` |
| K5 aktualizacja 0.3.3 i powrot | potwierdzone wlasna proba | C, C5 |
| K6 pelny pytest 0 failed | potwierdzone w logu wykonawcy co do liczb (2533 / 9 / 0); NIEPOTWIERDZONE co do czystego konca procesu | P2: kod procesu -1073741819; P3: test ikon w mojej sesji nie do uruchomienia |
| K7 lista [NIE SPRAWDZONE BEZ SPRZETU] | potwierdzone przegladem | instrukcja, punkt 8: 6 pozycji |

Wymagania 1-6 zlecenia paczki: 1 (Python w paczce, oryginalne podpisane pliki, suma przy budowie) - potwierdzone proba; 2 (start
dwuklikiem) - potwierdzone proba D3; 3 (okno) - potwierdzone testami i probami logiki, ramki - znane odstepstwo wykonawcy; 4 (ikony
i komunikat) - potwierdzone proba; 5 (aktualizacja, powrot) - potwierdzone proba; 6 (tryb bez okna, ta sama logika) - potwierdzone
proba (wszystkie instalacje prob szly ta droga).

## 4. Zakres plikow i zasady

- 21 plikow, wszystkie z listy zlecenia: `instalacja/**` (7), `narzedzia/zbuduj_wydanie.py`, instrukcja, opis modulu, `README.md`
  wydan, testy (4), raport, 5 zrzutow PNG (33-59 KB kazdy). `stanowisko/ui/**` i `WERSJA` bez zmian (0 plikow w diffie).
  Plikow nietykalnych, schematu bazy, nowych pakietow pip, duzych danych w diffie nie ma.
- Kodowanie i konce linii (pomiar bajtow 16 plikow tekstowych): `.cmd` CRLF 2 z 2; pozostale LF 14 z 14; ASCII 15 z 16 - wyjatek
  `instalacja/napisy_instalatora.py` (402 bajty spoza ASCII: teksty ekranu ze znakami diakrytycznymi, opisane w tabeli plikow
  raportu wykonawcy i w naglowku pliku) - patrz sekcja 5.
- Dane osobowe: w diffie, raporcie i zrzutach tylko dane fikcyjne (zrzuty: "Anna Kowalska", "Piotr W."); sciezek kont uzytkownikow nie ma.
- Raport wykonawcy: liczby K1, K2, K5 zgodne z moimi pomiarami; brak informacji o kodzie wyjscia procesu pelnego pytest (P2).
  Odstepstwa 1-4 opisane uczciwie.

## 5. Do decyzji wlasciciela

1. Zamkniecie okna w trakcie instalacji (P1): prawdziwe przerwanie z zakonczeniem procesow czy zakaz zamykania do konca
   instalacji. Na 28.11 prostszy i bezpieczniejszy jest zakaz; do czasu poprawki rada dla instalujacego: nie zamykac okna
   w kroku 5, a po zamknieciu odczekac kilka minut przed ponowna proba.
2. Znaki diakrytyczne w `napisy_instalatora.py` (teksty, ktore czyta czlowiek w oknie) - odstepstwo od zasady ASCII takie samo
   jak `ui/napisy.py` paczki U1a; proponuje przyjac.
3. Pozycje [NIE SPRAWDZONE BEZ SPRZETU] zostaja otwarte do soboty: jedna proba `Instaluj.cmd` z pendrive'a na dowolnym laptopie
   bez Pythona przed pokazem zamknelaby wiekszosc z nich (ostrzezenie Windows, antywirus, czas do pokazania okna, skalowanie).
