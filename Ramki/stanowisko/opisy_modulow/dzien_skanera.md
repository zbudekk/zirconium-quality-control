# dzien_skanera - okno "Dzien skanera - krok po kroku" (zbieranie pierwszych skanow i danych)

**Co robi.** W dniu dostawy skanera prowadzi czlowieka przez kroki testu i samo zbiera wszystko, co program skanera
zapisuje - tak, zeby komplet danych nie zalezal od znajomosci programu skanera ani od pamieci. Zasada nadrzedna:
lepiej skopiowac za duzo niz za malo; oryginaly sa tylko czytane (nigdy przenoszone, kasowane ani zmieniane); program
pisze wylacznie w folderze sesji. Pliki: `stanowisko/dzien_skanera.py` (okno PySide6), `stanowisko/dzien_skanera_rdzen.py`
(cala logika, bez Qt), `stanowisko/dzien_skanera_kroki.toml` (kroki - dane, nie kod), `uruchom_dzien_skanera.bat`,
`narzedzia/pomiar_skanu/` (pomiar szczegolowy T10, osobny proces). Dokumenty dla czlowieka:
`../sciaga_skaner_DentalScan_2026-11-16.md`, `../dzien_skanera_karta_2026-11-16.md`.

**Wejscie.** Foldery obserwowane (domyslnie `[sciezki] folder_eksportu_skanera`; w oknie "Dodaj folder...", takze kilka),
pliki i foldery dodane recznie albo przeciagniete na okno, klikniecia i teksty czlowieka (notatki, pola kroku, stoper,
pominiecia z powodem), ekran (zrzuty). Uruchomienie: `uruchom_dzien_skanera.bat` albo
`py -3.12 -m stanowisko.dzien_skanera [--nowa] [--sesja FOLDER] [--dane KATALOG] [--folder F ...] [--bez-kontroli]`.

**Wyjscie.** Folder sesji `dane/dzien_skanera/<RRRR-MM-DD_GGMM>/`:

| Co | Gdzie |
|---|---|
| manifest (stan krokow, pola, notatki, kazdy plik: zrodlo, sciezka w sesji, rozmiar, czas, SHA-256, wynik kontroli; od 17.11 rejestr `kopie_folderow` - wynik kazdej kopii calego folderu) | `sesja.json` (+ `sesja.json.bak`) |
| pliki z folderu skanera, ze sciezka wzgledna | `kroki/k<NN>_<id>/pliki/<etykieta folderu>/<sciezka>` |
| pliki dodane recznie / przeciagniete | `kroki/k<NN>_<id>/reczne/...` |
| zrzuty ekranu | `kroki/k<NN>_<id>/zrzuty/zrzut_<data>_<czas>.png` |
| kopia calego folderu zlecen (ostatni krok) | `kroki/k14_kopia_folderu/kopia_folderu/<folder>/...` |
| pelny wynik szybkiej kontroli kazdego skanu + log procesu | `kontrole/k<id>.json`, `kontrole/k<id>.log` |
| pomiary szczegolowe T10 | `pomiary/k<id>_<nazwa>_pomiar/` |
| stan obserwatora (co juz obsluzone), log | `obserwator.json`, `log.txt` |
| po "Zakoncz i spakuj" | `RAPORT_dzien_skanera.md`, `SHA256SUMS.txt`, `paczka/dzien_skanera_<sesja>[_cz<i>z<n>].zip`, `paczka/paczka.json` |

**Jak dziala.**
1. **Sesja** (`Sesja`): manifest zapisywany atomowo (plik tymczasowy, `fsync`, `os.replace`, poprzednia wersja jako
   `.bak`) po KAZDEJ akcji czlowieka; przy serii plikow z folderu skanera zbiorczo - najrzadziej co 5 s i zawsze na
   koncu przegladu folderow (na wolnym dysku kazdy zapis z `fsync` trwa; kopia, ktorej nie ma jeszcze w manifescie,
   po awarii zostaje skopiowana ponownie: stan obserwatora `obserwator.json` jest zapisywany zawsze PO zaleglym
   manifescie, wiec plik nie moze byc "znany", zanim jego wpis jest na dysku, a przy wznowieniu kopia lezaca w folderze
   kroku bez wpisu w manifescie powoduje ponowne podjecie zrodla - `Zbieracz._zapomnij_kopie_bez_wpisu`). Po zamknieciu
   albo awarii `Sesja.wznow` czyta `sesja.json`, a gdy jest uszkodzony - `.bak`. Okno przy starcie proponuje wznowienie
   ostatniej niedokonczonej sesji.
2. **Kroki** z `dzien_skanera_kroki.toml`: id, tytul, instrukcja, wymagany / opcjonalny, ilu i jakich plikow sie
   spodziewamy, rodzaj kontroli, z ktorym krokiem porownac, pola do wypelnienia. Definicje krokow sa kopiowane do
   manifestu (paczka opisuje sie sama; `--sprawdz` nie potrzebuje pliku krokow). Kazdy krok mozna pominac
   ("Nie udalo sie / pomijam, bo ...") - powod jest zapisany, nic nie blokuje.
3. **Zbieracz** (`Zbieracz`, zwykly watek Pythona): co 1,5 s oglada foldery obserwowane (`os.scandir`, z podfolderami).
   Plik nowy albo zmieniony (inny rozmiar lub czas) jest kopiowany, gdy: dwa kolejne odczyty daja ten sam rozmiar
   i czas, nikt nie trzyma go otwartego do zapisu (Windows: proba otwarcia bez zgody na zapis), a binarny STL ma
   rozmiar zgodny z naglowkiem (niezgodny czeka do 30 s, potem jest kopiowany z uwaga). Kopia: strumieniowo po 4 MB
   do `<cel>.czesc`, SHA-256 liczony w locie, `os.replace`; plik zrodlowy otwierany tylko do odczytu z pelnym
   wspoldzieleniem (zapis, zmiana nazwy i usuniecie przez program skanera pozostaja mozliwe). Przed kopia sprawdzenie
   miejsca (plik + 300 MB zapasu) - przy braku czytelny komunikat i ponawianie. Plik trafia do folderu kroku, ktory
   byl biezacy, gdy plik sie pojawil albo zmienil (takze gdy czlowiek przejdzie dalej, zanim kopia sie skonczy).
   Zmieniona wersja tego samego pliku = nowa kopia `<nazwa>__zmiana<N>` (do 8 wersji na krok; ta sama tresc
   nie jest kopiowana drugi raz). Pliki obecne w folderze przed startem ("zastane") nie sa kopiowane - trafiaja do
   kopii calego folderu w ostatnim kroku; przy dodawaniu folderu okno pyta, czy skopiowac je od razu. Po wznowieniu
   sesji pliki, ktore pojawily sie w przerwie, sa kopiowane (stan w `obserwator.json`).
   **Kopia calego folderu** (ostatni krok) ma wpis w rejestrze `kopie_folderow` manifestu: stan `w_toku` zapisany przed
   pierwszym plikiem, na koncu liczby skopiowanych / bledow / pominietych / niedostepnych podfolderow i stan `pelna` |
   `niepelna` | `przerwana` (brak miejsca, zamkniecie okna); kopia "w toku" znaleziona przy wznowieniu sesji (program
   zabity) dostaje stan `przerwana`. Krok jest "zrobiony" dopiero przy kopii pelnej; niepelna = brak kroku w panelu,
   czerwony komunikat w oknie, wiersz `KOPIA FOLDERU ... NIEPELNA` i kod 3 w `--sprawdz`. Ponowne klikniecie przycisku
   kopiuje tylko pliki, ktorych kopia w tym kroku jeszcze nie ma (to samo zrodlo, rozmiar i czas) - bez duplikatow.
   Foldery obserwowane o tej samej nazwie maja w kopii osobne katalogi (etykiety `Scandata`, `Scandata_2`).
4. **Szybka kontrola** kazdego pliku STL / PLY / OBJ (`kontrola_pliku`), w OSOBNYM PROCESIE na plik
   (`python -m stanowisko.dzien_skanera_rdzen --kontrola`; Open3D w watku pod Qt zawisa - `raporty/P3a_postep.md`;
   awaria albo zawieszenie kontroli nie zatrzymuje zbierania, limit 10 min; na Windows priorytet ponizej normalnego -
   stala `NIZSZY_PRIORYTET_KONTROLI` - wiec program skanera ma pierwszenstwo, a przy procesorze zajetym w calosci
   kontrola czeka): liczba trojkatow, obrys, sredni odstep
   wierzcholkow (caly plik, plaski wierzch, prace), czy to cala plytka (plaszczyzna wierzchu, 3 stozki), uklad
   z `[plytki]` i jakosc dopasowania, numer z dolkow, szum plaskiej czesci (`plaszczyzna_rms_mm`), liczba prac
   i gniazda. Rozpoznanie ukladu jest w JEDNEJ funkcji **`rozpoznaj_uklad(siatka, ust, numer)`** - od 16.11.2026
   (commit `502212e`) wola automatyczne rozpoznanie programu `plate.rozpoznaj_uklad` (rozstaw stozkow, numer z dolkow
   albo ksztalt brzegu; to samo co `porownaj --plytka auto`) i tlumaczy jego wynik oraz wyjatki `NierozpoznanyUklad` /
   `BladWyrownania` na slownik dla kontroli. Wynik prostym jezykiem: zielone "SKAN DOBRY: ...", zolte "UWAGA: ...", czerwone
   "TEN SKAN SIE NIE NADA, bo ... ZROB TAK: ...". Do tego oczekiwania kroku (`ocen_w_kroku`): pusta plytka bez prac,
   plytka z pracami, powtorka = porownanie z poprzednim skanem (te same gniazda, przesuniecie srodkow prac, ten sam
   plik = czerwone), inny eksport, ta sama plytka. Fragment "poza gniazdem" w miejscu stozka znacznika (stozek w skanie
   rozni sie od modelu o wiecej niz prog `plate`) jest informacja dla koordynatora, nie zoltym ostrzezeniem.
5. **Zrzuty ekranu**: `PIL.ImageGrab.grab(all_screens=True)` po 3 s od klikniecia (okno chowa sie na ten czas) oraz
   opcja zrzutu automatycznego przy nowym pliku (nie czesciej niz co 10 s).
6. **Kompletnosc** (`kompletnosc_z_manifestu`): stan kroku z dowodow - pliki, pola, notatki - nie tylko z klikniecia;
   panel po lewej pokazuje caly czas, co zrobione i czego brakuje.
7. **"Zakoncz i spakuj"** (`spakuj`): raport, sumy wszystkich plikow sesji (porownane z sumami z chwili kopiowania),
   ZIP w czesciach do 1,9 GB danych. Do sum i paczki nie trafiaja tylko WLASNE pliki robocze programu
   (`plik_roboczy_programu`: niedokonczona kopia `*.czesc` spoza manifestu, `.tmp` / `.bak` manifestu, stanu obserwatora,
   raportu, sum i wynikow kontroli); pliki `*.bak` / `*.tmp` / `*.czesc` skopiowane ze skanera (sa w manifescie) sa
   pakowane jak kazde inne. Projekty exocad nie trafiaja do paczki (`czy_projekt_exocad`: decyduje nazwa ZRODLA zapisana
   w manifescie, wiec takze kolejne wersje `X_cad__zmiana2.stl` i duplikaty `X_cad__2.stl`; do tego wyniki ich kontroli
   i pomiarow), a ich nazwy sa usuwane z manifestu, logu, stanu obserwatora i raportu w paczce - razem z kazda inna
   nazwa `*_cad.stl` w tych tekstach (plik zastany w folderze skanera, plik, ktorego nie udalo sie skopiowac).
   Kolejnosc odporna na awarie: nowe archiwa powstaja jako `*.zip.czesc`; dopiero gdy wszystkie sa gotowe, zastepuja
   stare, potem zapisywane sa raport i sumy, a na koncu znaczniki `zakonczono` / `spakowano` w manifescie. Nieudane
   albo przerwane pakowanie (brak miejsca, wyjatek, zamkniecie okna) = sesja NIE jest oznaczona jako spakowana,
   poprzednia paczka zostaje bez zmian. Zamkniecie okna w trakcie pakowania: pytanie "zamknac mimo to?"; po "Tak"
   pakowanie jest przerywane miedzy plikami (`Przerwano`). Braki wymaganych krokow = wyrazne ostrzezenie, bez blokady.
   Przed pakowaniem okno czeka najwyzej 2 min na trwajace kontrole i najwyzej 20 s na pliki, ktore wlasnie pojawily
   sie w folderze skanera; pozniejszy plik albo wynik kontroli, a takze zmiana sesji w trakcie pakowania, oznacza
   sesje (na dysku) jako zmieniona po spakowaniu ("spakuj ponownie"). Archiwum przyjmuje pliki z data sprzed 1980
   (`strict_timestamps=False`).
8. **Sprawdzenie paczki** (`sprawdz`; `py -3.12 -m stanowisko.dzien_skanera --sprawdz <folder sesji albo zip>`): sumy,
   zgodnosc z manifestem, kompletnosc, wynik kopii calego folderu. Folder sesji i jego archiwum daja ten sam wynik
   (plik z manifestu, ktorego nie ma w sumach, jest bledem takze w folderze). Kod wyjscia: 0 = sumy zgodne i komplet;
   1 = blad integralnosci (brak pliku, zla suma, uszkodzone archiwum, brak czesci); 3 = sumy zgodne, ale brakuje
   wymaganych krokow, sa pominiete albo kopia calego folderu jest niepelna; 2 = nie ma czego sprawdzac. Folder
   z archiwami kilku sesji: sprawdzana jest kazda paczka, kod = najgorszy z wynikow.
9. **Odpornosc**: wyjatek w obsludze okna albo w watku trafia do `log.txt` i na liste komunikatow - okno zyje dalej;
   okno nie uzywa sieci; `Sesja.sciezka` odrzuca kazda sciezke poza folderem sesji; folder sesji lezacy wewnatrz folderu
   obserwowanego nie jest kopiowany do siebie; gdy `ustawienia.toml` jest zly albo go nie ma, okno dziala (zbieranie bez
   kontroli skanow).

**Kryterium "dziala".** `testy/test_dzien_skanera.py` (70 testow; 17 dodanych 17.11 po recenzji PR #13 - awaria
miedzy kopia a manifestem, zrodlo zmienione w trakcie kopii, wznowienie z `.tmp`, pliki `.bak` / `.tmp` skanera
w paczce, nieudane i przerwane pakowanie, zamkniecie okna w trakcie pakowania, kolejne wersje i duplikaty projektu
exocad, przerwana i wznowiona kopia calego folderu, plik sprzed 1980, sesja zapisana starsza wersja): manifest na dysku po kazdej akcji i wznowienie
(takze z `.bak`), obserwacja folderu (nowy plik, podfoldery, typy inne niz STL, plik rosnacy, plik otwarty do zapisu,
niepelny STL, plik zmieniony, limit wersji, folder powstajacy pozniej, wznowienie po przerwie, seria 40 plikow z zapisem
zbiorczym, plik w kroku, w ktorym sie pojawil, sciezka w sesji ponad 260 znakow), oryginaly bez zmian,
SHA, brak miejsca przed kopiowaniem, pominiecie z powodem, zrzuty, raport, ZIP (takze dzielony), `--sprawdz` (takze
uszkodzony plik i brak czesci), kontrola na malych sztucznych skanach (uklad R54: okragla z numerem z dolkow, kwadrat
bez numeru, pusta, powtorka, plik niebedacy plytka, STL uciety), kontrola w osobnym procesie (polecenie i priorytet),
okno offscreen (kroki, przyciski, przeciaganie, pakowanie, pomiar szczegolowy jako osobny proces, wyjatek nie zamyka okna). Proba na prawdziwych rozmiarach i liczby:
`raporty/dzien_skanera_2026-11-16.md`.

**Zalozenia i granice.**
- O programie skanera wiemy tylko to, co w dokumentacji DentalScan 3.0.4. Nie wiemy, gdzie, kiedy i w jakim formacie
  zapisuje pliki - dlatego okno kopiuje KAZDY plik dowolnego typu i ma szukanie swiezych plikow STL / PLY / OBJ na
  dyskach ("Nie wiem, gdzie skaner zapisuje - szukaj").
- Szybka kontrola byla sprawdzana wylacznie na skanach sztucznych. Progi (szum zolty od 0,05 mm, dopisek "rzadko"
  od odstepu 0,08 mm, mniej niz 50 tys. trojkatow = zolte, przesuniecie pracy 0,3 mm w powtorce) sa stalymi na
  poczatku `dzien_skanera_rdzen.py` - wskazowka, nie decyzja. Czerwona ocena nigdy nie usuwa pliku.
- Kwadrat i okragla tego samego ukladu maja te same stozki i gniazda: `rozpoznaj_uklad` rozstrzyga numerem z dolkow
  (okragla: dolki w polu skanera; kwadrat: poza polem). Gdy skaner obejmie dolki kwadratu albo nie obejmie dolkow
  okraglej, wybor moze byc bledny - w wyniku sa wszyscy kandydaci, a czlowiek wpisuje rodzaj i numer plytki w polach.
- Porownanie powtorki ocenia polozenie prac wzgledem plytki (srodki fragmentow). Roznica polozenia calej plytki
  w ukladzie skanera jest tylko informacja (program skanera moze ustawiac model po swojemu). Powtarzalnosc na krawedzi
  brzegu mierzy dopiero narzedzie T10 (`--powtorka`).
- Stabilnosc pliku: program, ktory pisze plik z przerwami dluzszymi niz ok. 3 s i zamyka go miedzy zapisami, da kopie
  czesciowa, a potem kolejna wersje (`__zmiana2`) - nic nie ginie, ale plik czesciowy dostanie czerwona ocene.
- Plik stale zmieniany (baza danych, log programu skanera): po 8 wersjach w kroku dalsze zmiany sa pomijane do
  nastepnego kroku; ostatni stan zabezpiecza kopia calego folderu.
- "Bez nazwisk" w paczce jest zapewnione tylko dla plikow `*_cad.stl` (ich pierwszych i kolejnych wersji oraz
  duplikatow) i tylko dla NAZWY PLIKU. Nazwisk w nazwach zlecen wpisanych w programie skanera ani w nazwie FOLDERU
  projektu exocad (inne pliki z tego folderu trafiaja do paczki ze swoja sciezka) program nie rozpozna - instrukcja
  kaze nazywac zlecenia TEST1, TEST2 i sprawdzic nazwy przed wyslaniem. Zrzut ekranu tez moze pokazywac nazwe.
  Sciezki zrodlowe w manifescie maja katalog domowy uzytkownika zastapiony przez `~`.
- Rejestr kopii calego folderu przechowuje liczby, nie liste plikow: `--sprawdz` porownuje liczbe plikow kopii
  w manifescie z liczba plikow, ktore kopia zastala w folderach. Folder obserwowany, ktory w chwili kopii nie
  istnieje (np. domyslny z ustawien), jest pomijany bez oznaczania kopii jako niepelnej. Plik zablokowany na stale
  przez program skanera oznacza kopie niepelna do czasu, az da sie go odczytac (pakowac mozna mimo to - brak jest
  w raporcie).
- Znane, niepoprawione (lista z recenzji PR #13, D10): "dwa stabilne odczyty" to licznik odczytow, nie czas (polecenie
  z okna budzi watek od razu); sonda `ktos_pisze` otwiera zrodlo na chwile bez zgody na zapis innym; binarny STL
  z bajtami za danymi jest oceniany jako uciety bez proby wczytania; krok z samym zoltym skanem jest "zrobiony"
  (`--sprawdz` = 0).
- Zrzut ekranu wymaga sesji z pulpitem (w sesji ssh bez pulpitu `ImageGrab` zawodzi - komunikat, zbieranie trwa).
  Obraz okna programu skanera na prawdziwym laptopie nie byl sprawdzony.
- Kopia calego folderu powiela pliki skopiowane wczesniej (celowo); przy duzym folderze zlecen paczka rosnie -
  archiwum jest dzielone, a przed pakowaniem sprawdzane jest miejsce.
- Okno nie steruje programem skanera (zadnego klikania ani klawiszy) i nie uruchamia pelnego `porownaj`
  (match / inspect) - do tego sluzy `uruchom_okno.bat` na zebranych plikach.
- Pomiar szczegolowy (`narzedzia/pomiar_skanu`) to kopia narzedzia T10 zalezna od `stanowisko.match` i `inspect`;
  po przebudowie tych modulow wymaga ponownego sprawdzenia.
