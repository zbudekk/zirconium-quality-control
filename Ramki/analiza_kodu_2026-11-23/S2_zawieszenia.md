# S2 - procesy, baza, kolejki: gdzie program moze stanac (23.11.2026)

Podstawa: galaz `analiza/plan` (= `main` b856b9e + folder planu), worktree `<PC-katalog>\qc-wt\analiza-s2`, galaz `analiza/s2`.
Kod sie nie zmienil. Dowody: `czytanie` albo `proba` (skrypt i logi w `S2/`). Sciezki `plik:linia` licza sie od
`Ramki/stanowisko/stanowisko/`. Wagi: B / P / D jak w `PLAN.md` p. 6. Kazde znalezisko dotyczy KAZDEJ plytki (okragla
ramkowa, okragla R54, kwadratowa) - sciezki procesow, bazy i kolejek nie zaleza od ukladu plytki; w tabeli kolumny "plytka" nie ma.

Liczba znalezisk: B 1, P 7, D 7.

## 0. Najwazniejsze

1. **S2-01 (B, proba)** Pierwszy start na laptopie stanowiska: KAZDY plik `*.stl` zastany w folderze skanera (takze w podfolderach)
   idzie do analizy przed swiezym skanem technika (kolejka w kolejnosci zlecen). Proba: 10 plikow zastanych po 1 s analizy -
   swiezy skan dostal wynik po 10,83 s, jako 11. Przy 100 plikach i 12-18 s na plytke to 20-30 min czekania; stare skany staja sie
   plytkami dzisiejszej doby (w probie: 8 pytan "ponowny skan" i komunikat o konflikcie projektu).
2. **S2-02 (P, proba)** Nowy skan, ktory pojawi sie, gdy baza jest zajeta dluzej niz 5 s, PRZEPADA BEZ KOMUNIKATU do nastepnego
   startu programu, a okno stoi 5,5-7,9 s. Poprawka E3-P14 objela polecenia klikane, nie objela zdarzen skanera.
3. **S2-03 (P, proba)** Wynik analizy przy zajetej bazie: okno stoi 5,5 s przy kazdej probie zapisu; w probie 27,6 s z 40 s (69 %).
   Po zwolnieniu bazy plytka pojawila sie dopiero po 16 s (czekala na kolejna probe).
4. **S2-04 (P, czytanie)** Zawieszona analiza trzyma cala kolejke do 600 s (`limit_zadania_s`); proces, ktory nie zglasza gotowosci -
   do 2 x 180 s, zanim technik zobaczy "Analiza nie dziala". Po smierci procesu (0xC0000005 / 0xC0000409 w trakcie analizy) skan
   dostaje "blad" bez ponowienia i trzeba skanowac plytke ponownie.
5. **S2-05 (P, czytanie)** Watek liczenia puli (`pula-liczenie` / `pula-katalog`) nie ma limitu czasu. Gdy nie odpowie (OneDrive,
   udzial sieciowy), stan puli zostaje "liczenie" i WSZYSTKIE skany czekaja bez konca i bez komunikatu o przyczynie.
6. **S2-06 (P, czytanie)** Jeden blad analizy wstrzymuje wszystkie nastepne skany do konca ponownego liczenia puli
   (`_do_sprawdzenia`); razem z S2-05 = trwale zatrzymanie po pierwszym bledzie.
7. **S2-07 (P, czytanie)** Pula z folderu (`pula_wpisow = false`, wartosc ze wzoru ustawien): cala zawartosc folderu "Cyrkon" jest
   wczytywana W ZADANIU pierwszej plytki, pod limitem 600 s, od nowa po kazdym starcie programu i po kazdej smierci procesu.
   Pliki OneDrive "tylko online" bylyby wtedy pobierane w trakcie analizy. [NIE SPRAWDZONE BEZ SPRZETU]
8. **S2-08 (P, czytanie)** Krok Excela (odczyt arkusza przez COM) idzie w watku okna z zegara `przetworz` - kontroler nie ma
   limitu czasu; Excel z otwartym oknem dialogowym = okno programu stoi (szczegoly po stronie `excel_com` - sesja S3).

## 1. Tabela znalezisk

| id | plik:linia | co jest zle | skutek na stanowisku | waga | dowod | koszt potwierdzenia | na sprzecie 28-29.11 |
|---|---|---|---|---|---|---|---|
| S2-01 | scanner.py:405-426, 431-444, 597-599; silnik.py:1338; aplikacja.py:551-562, 1294-1306 | pliki zastane ida do tej samej kolejki co swieze skany, bez pierwszenstwa i bez limitu liczby | swiezy skan czeka N x czas analizy; N starych plytek w dzisiejszej dobie | B | proba `d` | T (zrobione) | policzyc `*.stl` w folderze skanera PRZED pierwszym startem; start z pustym folderem albo przyjac czas |
| S2-02 | aplikacja.py:1227 (zapis bez krotkiego czekania), 1189-1196 (blad polkniety); scanner.py:710 (plik uznany za rozstrzygniety) | zdarzenie skanu zdjete ze skrzynki ginie, gdy wpis dziennika sie nie uda | skan bez sladu na ekranie, okno stoi 5,5-7,9 s | P | proba `a` | T (zrobione) | otworzyc baze innym programem z blokada zapisu, zeskanowac plytke |
| S2-03 | aplikacja.py:1144-1146, 1412-1418; baza.py:45, 512 | ponowienia zapisu wyniku w watku okna z czekaniem 5 s kazde | okno stoi wiekszosc czasu, dopoki baza jest zajeta | P | proba `b` | T (zrobione) | jak S2-02, blokada zalozona w trakcie analizy |
| S2-04 | silnik.py:79-80, 1594-1597, 1669-1678, 1739-1750; aplikacja.py:74, 1485-1494, 1503 | limity 600 s / 180 s bez komunikatu posredniego; brak ponowienia po smierci procesu | pasek postepu stoi do 10 min, kolejka czeka; skan "blad" | P | czytanie | D (wstrzykniecie zawieszenia w srodowisku wersji, powtorzenia) | zmierzyc zwykly czas plytki i ustawic `limit_zadania_s` na jego wielokrotnosc |
| S2-05 | aplikacja.py:671-701, 721-761, 1295-1299 | `_liczenie_puli` wraca do False tylko po odpowiedzi watku | "liczenie puli" bez konca, skany wstrzymane | P | czytanie | S (proba z funkcja liczaca, ktora nie wraca: ok. 10 min pracy) | odlaczyc siec / wstrzymac OneDrive i kliknac "Odswiez pule" |
| S2-06 | aplikacja.py:1011-1016, 1018-1026, 1295 | po bledzie analizy `_zlec` wstrzymuje kazdy skan do konca liczenia puli | po jednym bledzie kolejne plytki czekaja na przeglad calego folderu | P | czytanie | S (proba: skan z bledem + wolne liczenie puli) | zeskanowac pusta plytke (blad analizy) i zaraz nastepna |
| S2-07 | silnik.py:497-523 (pula w zadaniu), 1058-1060, 237-255 (`rglob` calego folderu w kazdym zadaniu) | budowa puli z folderu nie ma osobnego etapu ani pamieci na dysku | pierwsza plytka po starcie i po kazdej awarii procesu trwa tyle, co wczytanie calego folderu; ponad 600 s = "analiza trwala za dlugo" | P | czytanie | D (pomiar na prawdziwym folderze "Cyrkon") | zmierzyc pierwsza plytke po starcie przy prawdziwym folderze |
| S2-08 | kontroler_api.py:2832-2855, 2888, 2904, 2918 | wywolania Excela w watku okna | okno stoi, gdy Excel nie odpowiada | P | czytanie | D (prawdziwy Excel) | "Zamknij piec" przy Excelu z otwartym oknem dialogowym |
| S2-09 | aplikacja.py:164-168, 205-211, 1257, 1281, 1417, 1497 | `Path.is_file()` na pliku skanu w watku okna | folder skanera na udziale sieciowym bez odpowiedzi: okno stoi przy kazdym wyniku (ok. 21 s wg komentarza aplikacja.py:94-95) | D | czytanie | S | nie dotyczy, gdy folder skanera jest na dysku lokalnym |
| S2-10 | aplikacja.py:1035-1053 | `ustaw_pule` pisze do dziennika bez krotkiego czekania i poza `_polecenie` | przy zajetej bazie 5 s i wyjatek w slocie okna (kontrakt: polecenie nigdy nie rzuca) | D | czytanie | T (nie robione - 1 proba) | - |
| S2-11 | aplikacja.py:1506-1567; scanner.py:349-360; silnik.py:1289, 1554, 1559 | zamkniecie programu sumuje czekania w watku okna | okno "nie odpowiada" do ok. 20 s (1 + 7 + 12 s) plus 5,5 s na kazdy zalegly zapis | D | czytanie | S | zamknac program w trakcie analizy, zmierzyc czas |
| S2-12 | silnik.py:1745, 1748, 1750 | kod wyjscia procesu wypisany dziesietnie (`3221225477`), w innych miejscach szesnastkowo (1475) | w dzienniku i logu trudno rozpoznac 0xC0000005 / 0xC0000409 | D | czytanie | - | - |
| S2-13 | scanner.py:544-550, 668-670, 685-686; dzien_skanera_rdzen.py:253-261 | plik trzymany stale do zapisu przez program skanera jest sprawdzany co 0,05 s bez konca otwarciem bez zgody na zapis | mozliwa odmowa otwarcia pliku po stronie programu skanera [NIE SPRAWDZONE BEZ SPRZETU] | D | czytanie | D | obserwowac folder skanera narzedziem Process Monitor w trakcie skanowania |
| S2-14 | scanner.py:344, 391-401; aplikacja.py:541, 551, 607-617 | start programu w watku okna: przeglad calego folderu skanera, wszystkie wiersze `skany`, wszystkie wpisy `podglad` | czas do pokazania okna rosnie z historia | D | czytanie | S | zmierzyc czas od uruchomienia do okna |
| S2-15 | silnik.py:1583, 1615, 1631, 1657 | `recv` / `send` nadzorcy bez limitu; wpis logu pod zamkiem silnika | nadzorca stojacy w `recv` nie sprawdza limitu zadania (przypadek teoretyczny) | D | czytanie | D | - |

## 2. Opisy

**S2-01.** `Scanner.start()` ustala pliki zastane (scanner.py:405-426); z `znane` z bazy (aplikacja.py:551-559) kazdy plik, ktorego
nie ma w tabeli `skany`, staje sie kandydatem (431-444), dostaje skrot i zdarzenie z `zastany=True`. Wszystkie gotowe pliki sa
rozstrzygane w JEDNYM obiegu watku obserwatora (597-599: skrot SHA-256 kazdego pliku po kolei), wiec plik zapisany w tym czasie
jest zauwazany dopiero po calej serii. `Aplikacja._zlec` (1294-1306) zleca je silnikowi, `Silnik.zlec` dopisuje na koniec (1338).
Technik widzi komunikat "wznowiono N" i licznik kolejki; swojej plytki nie widzi. Przy pustej bazie (pierwszy start) "wszystkie"
znaczy: cala historia folderu `[sciezki] folder_eksportu_skanera` (wzor ustawien: `C:/Aidite/Scandata`, `rekurencyjnie = true`).
To skutek decyzji 25 - tu policzony. Ten sam mechanizm dziala po kazdej przerwie w pracy programu (skany zrobione, gdy program
byl wylaczony).

**S2-02.** `_zdarzenie_skrzynki` (aplikacja.py:1222-1230) najpierw pisze wpis `nowy_skan` (`Baza.zdarzenie`, czekanie polaczenia
5 s - baza.py:45), dopiero potem wola `_nowy_skan`. `BladBazy` lapie `_bezpiecznie` (1189-1196): wpis w logu i koniec. Zdarzenie
jest juz zdjete ze skrzynki, a obserwator ma plik w `_znane` (scanner.py:710), wiec nie zglosi go drugi raz. Komentarz przy
`_bezpiecznie` mowi "wroci przez nadrabianie po nastepnym starcie" - do tego czasu plytka nie istnieje dla programu.
Proba `a`: po zwolnieniu bazy i 15 s pracy - zdarzen skanera 2, plytek w stanie 1, wpisow `nowy_skan` 1, kolejka pusta, komunikatow 0.
Kto zajmuje baze: inny program z otwarta transakcja zapisu (przegladarka bazy, kopia), nie wlasny watek katalogu (jego transakcje
sa krotkie - indeks.py:298, wspolczynniki.py:298). Przyczyna techniczna: baza pracuje w domyslnym trybie dziennika (baza.py:317-325
nie ustawia `journal_mode`), wiec pisarz czeka na kazdego czytelnika i odwrotnie.

**S2-03.** `_zapis_w_bazie` zaczyna `BEGIN IMMEDIATE` (aplikacja.py:1418, baza.py:512) z czekaniem 5 s; nieudany zapis trafia do
`_do_zapisu` i jest ponawiany z `przetworz` po 1, 2, 4, 8, 16, 30 s (1144-1146, `odstep_ponowienia` 249-251) - kazda proba to
kolejne 5,5 s stojacego okna, kazda pozycja osobno. Technik widzi komunikat `baza_zajeta` i pozycje "nie zapisano", ale nie moze
nic kliknac. Skan nie ginie (to dziala).

**S2-04.** Co widzi technik przy procesie analizy:

| zdarzenie | wykrycie | co widzi technik | co dalej |
|---|---|---|---|
| proces ginie w trakcie analizy (0xC0000005, 0xC0000409) | do 0,02 s (`poll`, silnik.py:1582) + do 5 s na zamkniecie (1559) | skan "blad": "Analiza skanu nie powiodla sie - analiza zostala przerwana" (statusy.py:334, 565) | nowy proces przy nastepnym skanie; skan NIE jest ponawiany; pula budowana od nowa |
| proces ginie przy zamykaniu (znane E3-A11w) | - | nic (kod trafia tylko do wyniku `_zamknij_proces`, silnik.py:1560) | - |
| analiza stoi | 600 s (`limit_zadania_s`, ustawienia.przyklad.toml:120; silnik.py:1669-1678) | pasek postepu bez zmian przez 10 min, potem skan "blad": "analiza trwala za dlugo" | kolejne skany czekaly caly ten czas |
| proces nie zglasza gotowosci | 180 s (silnik.py:80, 1594-1597), aplikacja zleca raz ponownie (aplikacja.py:74, 1486-1489) = do 360 s | nic poza licznikiem kolejki, potem "Analiza nie dziala" | skany wstrzymane do ponownego startu programu (1490-1494) |
| `Process.start()` stoi | 3 proby po 30 s (silnik.py:81-82), zadanie zlecane dwa razy = ok. 3 min | jak wyzej | jak wyzej |
| budowa puli wpisow bez postepu | 120 s, 2 proby (silnik.py:110-111, 1598-1602) | pasek budowy puli stoi | potem pule buduje zadanie, pod limitem 600 s |

W procesie roboczym nie ma ograniczenia liczby watkow bibliotek ani obnizonego priorytetu (brak ustawien w pakiecie; silnik.md:201-202
zostawia to "do decyzji po probach na laptopie").

**S2-05.** `_policz_pule` (aplikacja.py:671-701) i `_odswiez_katalog` (721-761) ustawiaja `_liczenie_puli = True` i przy
odswiezeniu glosnym (start programu, "Odswiez pule", zmiana trybu) stan `liczenie`. `_zlec` (1295) przy stanie innym niz `gotowa`
odklada kazdy skan do `_wstrzymane`. Flaga i stan wracaja tylko, gdy watek odlozy wynik do skrzynki (699, 759). Wyjatki sa
obsluzone; brak odpowiedzi - nie. W watku: `rglob` po folderze puli (395-400) albo indeks folderow zlecen z odczytem kazdego nowego
pliku (indeks.py:273) i liczeniem cech (indeks.py:280-282: trimesh, otoczka wypukla, miniatura) - w procesie okna.
Przy odswiezeniu cichym stan zostaje `gotowa`, ale kolejne odswiezenia juz nie rusza (aplikacja.py:680-682, 727-731, 782).

**S2-06.** `_blad_analizy` dla rodzaju `analiza` wola `_sprawdz_pule_po_bledzie` (aplikacja.py:1011-1016): skan trafia do
`_do_sprawdzenia`, rusza ciche liczenie puli. `_zlec` (1295) przy niepustym `_do_sprawdzenia` wstrzymuje KAZDY skan. Czas = jeden
pelny przeglad folderu puli (albo indeksu zlecen); na duzym folderze dziesiatki sekund, przy S2-05 - bez konca.

**S2-07.** Dla puli z folderu `PamiecPul.dla` (silnik.py:497-523) buduje `match.Pula(foldery, ...)` w pierwszym zadaniu (wywolanie
z `_wykonaj`, 1058-1060). `Silnik.przygotuj_pule` (budowa w tle z postepem) dziala tylko dla puli wpisow (1378-1379). Pamiec na
dysku (`pamiec_puli`) tez tylko dla puli wpisow; `_zamknij_proces` kasuje pule procesu (1548). Dodatkowo `CzyscicielNazw`
(237-255) w KAZDYM zadaniu przeglada caly folder puli (`rglob` + `is_file` kazdego wpisu). Znany "zimny start 48,66 s" to ta
sciezka; jej czas zalezy od liczby plikow w folderze, ktorej nie znam (pytanie 3).

**S2-08.** `_przetworz_excel` (kontroler_api.py:2832-2855) wola `excel.propozycje` (2888), `zapisz_cien_bez_odczytu` (2904),
`zaloguj_poprawki` (2918) wprost z `przetworz`, czyli z zegara okna (lacznik: 1189-1190). "Jeden krok na obieg" ogranicza liczbe
wywolan, nie czas jednego.

**S2-09 - S2-15.** Jak w tabeli. Do S2-15: `_krok` wola `lacze.recv()` po udanym `poll` (silnik.py:1582-1583); gdyby proces
roboczy stanal w polowie wysylania wiadomosci wiekszej niz bufor lacza, nadzorca stalby w `recv` i nie sprawdzal limitu (1584) -
nie znalazlem zwyklej sciezki, ktora do tego prowadzi.

## 3. Lista "S2" z planu - odpowiedzi

- **Start procesow, potoki, kolejki.** Jeden proces roboczy (`spawn`), jedno lacze `Pipe`, bez wspolnych kolejek (silnik.py:1501-1502).
  Zdarzenia do okna ida przez `queue.Queue` bez limitu rozmiaru (`Silnik.zdarzenia` 1231, `_skrzynka` aplikacja.py:481) i sa
  oprozniane zegarem okna - zakleszczenia przez pelna kolejke nie ma. Nadzorca wysyla zadanie tylko do procesu wolnego (1598-1617).
- **Co dziala w watku okna** (najdluzsza blokada):

| operacja | plik:linia | najdluzej | co widzi technik |
|---|---|---|---|
| wpis dziennika przy zdarzeniu skanera / silnika | aplikacja.py:1227, 1234, 1258, 1266, 1286, 1291, 1325, 1476, 1493, 1498 | 5 s nominalnie, zmierzone 5,5-7,9 s | okno stoi; S2-02 |
| zapis wyniku / bledu | aplikacja.py:1418 | 5,5 s na probe | okno stoi; S2-03 |
| polecenie klikane | kontroler_api.py:3483 | 0,2 s nominalnie (E3-P14: 0,3-0,7 s) | odmowa i "Ponow teraz" - dziala |
| odczyt stanu | kontroler_api.py:1347 | 0,1 s nominalnie | stan zalegly, nadrabiany co 1 s - dziala |
| zdarzenia ramek | kontroler_api.py:2250 | 0,15 s nominalnie | odlozone na 1 s - dziala |
| krok Excela | kontroler_api.py:2837-2844 | bez limitu | S2-08 |
| istnienie pliku skanu | aplikacja.py:166 | dysk lokalny: milisekundy | S2-09 |
| start programu | aplikacja.py:528-570 | zalezy od liczby plikow i wierszy | S2-14 |
| zamkniecie | aplikacja.py:1506-1567 | ok. 20 s | S2-11 |

  Poza watkiem okna (dobrze): kopiowanie pliku skanu (proces roboczy, silnik.py:609-647), budowa puli (proces roboczy), liczenie
  plikow puli i indeks zlecen (watki `pula-liczenie`, `pula-katalog`), stan pliku wspolczynnikow na udziale sieciowym (watek
  `pula-plik-csv`, aplikacja.py:797-808), obserwacja folderu (watek `scanner`).
- **Zamki.** `Silnik._zamek` (silnik.py:1234), `ProbaStartu.zamek` (736), `_ZAMEK_OBIEKTU` (652), `_ZAMEK_WINAPI` (723), zamek
  lokalny proby startu (1440), `Scanner._zamek_watku` (scanner.py:315), `Scanner._zamek_watchdog` (310), `FiltrNazw._zamek`
  (aplikacja.py:331). Jedyne zagniezdzenie: `_zamek_watku` -> `_zamek_watchdog` (scanner.py:335 -> 461); kolejnosci odwrotnej nie ma.
  Pod `Silnik._zamek` nie ma wywolan zwrotnych ani operacji na laczu; jest jeden wpis logu (1657). Wyliczenie: `S2/wyliczenie_zamki_watki.md`.
- **Sygnaly Qt.** Watki robocze nie emituja sygnalow - wszystko przechodzi przez kolejki oprozniane zegarem (silnik.py:1796-1817,
  kontroler_api.py:1184-1190). Polaczen blokujacych miedzy watkami w zakresie nie znalazlem.
- **baza.** Tryb dziennika domyslny (bez `journal_mode`, baza.py:317-325), `busy_timeout` 5000 ms (45, 324), transakcje
  `BEGIN IMMEDIATE` (512), migracja w jednej transakcji z kopia pliku przed nia (366-378, 381-393). Plik `.blokada`
  (aplikacja.py:258-307): blokada systemowa bez czekania (`LK_NBLCK`), znika z procesem - nie zawiesza startu.
- **scanner.** Plik zajety: ponawianie bez limitu z komunikatem po 10 s i co 60 s (scanner.py:78-81, 723-737) - zamierzone, okna nie
  blokuje. Folder niedostepny: sprawdzany co 2 s w watku obserwatora, komunikat w oknie (aplikacja.py:1198-1211). `Scanner.stan()`
  nie bierze zamka. Setki plikow przy pierwszym starcie: S2-01.
- **pula / pamiec_puli / indeks.** Indeks: cechy liczone przed transakcja, zapis folderu w krotkiej transakcji (indeks.py:250-325).
  Uszkodzony plik pamieci puli = liczony od nowa, licznik `bledy_odczytu` (pamiec_puli.py:188, 246). Sprzatanie pamieci przy starcie
  procesu liczy sie do limitu gotowosci 180 s (silnik.py:1134-1140), tylko przy pierwszym starcie (1507). Czas przy kilkuset
  projektach: pomiaru nie robilem (plan: poza ta runda).
- **samokontrola.** Osobne polecenie, program jej nie wola (brak importu w `aplikacja.py`). Kazde sprawdzenie w watku pomocniczym
  z limitem 30 s (moduly 120 s, Excel 10 s; samokontrola.py:97-101, 293-313, 1311-1316); watki `daemon`. Startu programu nie zawiesi.
- **Zamkniecie i awaria.** Proces roboczy konczy sie zawsze: obiekt zadania Windows z `KILL_ON_JOB_CLOSE` (silnik.py:683, 691-718),
  straznik w procesie (363-369), `kill` po 2 s przy zamknieciu (1554-1558). Proces roboczy nie otwiera bazy stanowiska ani pliku
  blokady - sierota nie moze ich trzymac. Watki procesu okna sa `daemon`.

## 4. Sprawy znane - przyczyna w kodzie

- **E3-P14** (decyzja przy zajetej bazie, okno stoi ok. 15 s): dla polecen klikanych naprawione (`_polecenie`, kontroler_api.py:3483;
  testy `test_p14_baza_zajeta.py`). NIE obejmuje zdarzen skanera i silnika - S2-02, S2-03 - ani `ustaw_pule` (S2-10).
- **Zimny start 48,66 s**: budowa puli w zadaniu pierwszej plytki (S2-07); przy puli wpisow - `przygotuj_pule` w tle, skany czekaja.
- **E3-A11w**: blokada `_wmi` w `__init__.py:22-26` jest; kod wyjscia procesu przy zamykaniu nie jest nigdzie pokazywany (tabela S2-04).

## 5. Proby

Skrypt `S2/proba_s2.py` (prawdziwa `Aplikacja`, analiza sztuczna z `test_kontroler_api`, bez okna), z katalogu `Ramki\stanowisko`:
`<PC-katalog>\koordynator\narz\py.cmd ..\analiza_kodu_2026-11-23\S2\proba_s2.py a` (potem `b`, `d`). Logi: `S2/proba_s2_<litera>.log`, `.json`.

| proba | wynik |
|---|---|
| `a`, blokada EXCLUSIVE | najdluzsze `przetworz` 7,854 s; po zwolnieniu: zdarzen skanera 2, plytek 1, w kolejce 0, komunikatow 0 |
| `a`, blokada IMMEDIATE | najdluzsze `przetworz` 5,522 s; reszta jak wyzej |
| `b`, blokada IMMEDIATE, 40 s | 5 wywolan po 5,52-5,55 s, razem 27,63 s; komunikat `baza_zajeta`; po zwolnieniu plytka po 16,02 s |
| `d`, 10 plikow zastanych x 1 s | swiezy skan z wynikiem po 10,83 s, po 10 z 10 zastanych; 11 plytek, 8 pytan `ponowny_skan` |

Czas PC: ok. 2,5 min (55 s, 62 s, 12 s). Pelnego pytest ani petli powtorzen nie bylo.

## 6. Pytania do wlasciciela

1. Z konta Windows `<uzytkownik>`, na ktorym dziala ta sesja, `git fetch` i `git push` nie dzialaja ("could not read Username"); plan
   mowi, ze z PC dzialaja (konto `<konto-PC>`). Worktree zalozylem od lokalnej kopii `origin/analiza/plan` (480359f; pliki planu
   identyczne z kopia w `<PC-katalog>\analiza_kodu_2026-11-23`). Galaz `analiza/s2` trzeba wypchnac z konta z dostepem.
2. Ile plikow `*.stl` jest dzis w folderze eksportu skanera na laptopie stanowiska (z podfolderami) i czy baza bedzie pusta przy
   pierwszym starcie 28.11? (S2-01)
3. Czy na stanowisku bedzie `pula_wpisow = true`, czy pula z folderu? Ile plikow STL jest w "Cyrkon" i "Prywatne" i czy OneDrive
   trzyma je na dysku, czy "tylko online"? (S2-05, S2-07)
4. Czy w czasie pracy cos poza programem otwiera plik bazy (raport metryk, kopia zapasowa, przegladarka bazy)? (S2-02, S2-03)

## 7. Przeczytane / przejrzane / nieczytane

Przeczytane w calosci (linie): `silnik.py` 1823, `aplikacja.py` 1730, `baza.py` 586, `scanner.py` 753, `pula.py` 442, `indeks.py` 395,
`pamiec_puli.py` 299, `__init__.py` 29, opis `opisy_modulow/silnik.md` 297.
Przejrzane: `kontroler_api.py` (ok. 1050 z ok. 4740 linii: 1-190, 1158-1567, 2048-2317, 2750-2775, 2832-2921, 3113-3136, 3465-3506,
4062-4128), `samokontrola.py` (ok. 320 z 1432: 1-140, 286-321, 1289-1432 i wyszukiwanie czekan), `wspolczynniki.py` 273-402
(tylko transakcje), `dzien_skanera_rdzen.py` 239-262 i 1342-1369 (funkcje uzywane przez `scanner`), testy `test_p14_baza_zajeta.py`
1-100 i 428-460, `test_kontroler_api.py` 1-308.
Nieczytane przeze mnie: `ustawienia.py` 379 (tylko subagent), pozostale opisy modulow (subagent), `match.py` / `synth.py` /
`katalog.py` (zakres S1; sprawdzone tylko wyszukiwaniem uzycia Open3D).

Zlecenia subagentow (Opus 5.5, xhigh):
1. Wyliczenie miejsc czekania bez limitu czasu -> `S2/wyliczenie_czekania.md`.
2. Wyliczenie zamkow, watkow, procesow, sygnalow Qt i pracy w watku okna -> `S2/wyliczenie_zamki_watki.md`.
3. Porownanie opisow modulow z kodem (limity, czasy, ustawienia) -> `S2/opisy_kontra_kod.md`.
4. Uruchomienie prob `proba_s2.py a / b / d` i odpisanie wynikow (jedyny subagent testowy).
