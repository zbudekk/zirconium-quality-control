# Raport recenzenta PR #17 - runda 1

Data: 2026-11-17. Recenzent: swieza subsesja (Fable 5.2), niezalezna od wykonawcow i koordynatora; werdyktu koordynatora nie znam.
Stan recenzowany: `4f31251` (PR #17, `e3/a2` -> `przed-skanerem`), zakres `git diff a6cf3a4...4f31251 -- Ramki/stanowisko`
(8 nowych plikow, +2 855 / -0). W trakcie recenzji galaz dostala `1e72a00` (scalenie `przed-skanerem` `35ec579`) i `9cd0ac9`
(4 linie raportu paczki); z 8 plikow paczki zmienil sie tylko raport - sprawdzone `git diff 4f31251 origin/e3/a2`. Numery
linii ponizej dotycza `4f31251` (kod paczki identyczny w `9cd0ac9`).
Metoda: `scanner.py`, `silnik.py`, oba pliki testow, oba opisy i raport paczki przeczytane w calosci; `symulator_skanera.py`
linie 1-260; z istniejacego kodu: `dzien_skanera_rdzen.py` (`otworz_zrodlo`, `ktos_pisze`, `pliki_w_folderze`), `porownaj.py`
(`porownaj`, `main`), `match.py` (`Projekt`, `Pula`), `synth.py` (`wczytaj_projekt`), `session.py` z `origin/e3/a1`
(`przyjmij_wynik`). Plan etapu 3: sekcje 3.3, 3.8, 4.1, 9, 11.2.
Uruchomienia na PC (`<PC-katalog>\e3\r17`, kod = kopia drzewa `4f31251`, po jednym przebiegu naraz, `OMP_NUM_THREADS=2`):
3 wlasne skrypty (`x\eksp1.py` - 7 prob obserwatora, `x\eksp2.py` - 4 proby silnika z funkcja probna, `x\eksp3.py` - proces
roboczy po zabiciu procesu okna) oraz po jednym przebiegu `testy/test_scanner.py` i `testy/test_silnik.py`. Bez pelnego pytest,
bez analiz na skanach odniesienia. Na MSI nie uruchamiano pytest ani obliczen.
Uchybienie wlasne: `test_scanner.py` wystartowal przy 7 GB wolnego RAM (pomiar i start byly w jednym poleceniu; test nie laduje
ciezkich bibliotek); pozostale przebiegi przy 11-19 GB. Po pracy: 0 moich procesow python na PC (lista procesow z rodzicami).

## 0. Werdykt

**do scalenia po poprawkach** - B 1 / P 6 / D 12.

Budowa jest dobra: obserwator poprawnie czeka na koniec zapisu we wszystkich sposobach zapisu, ktore cwiczy symulator, silnik
nie blokuje okna, awarie analizy i procesu sa obslugiwane, testy przechodza i sprzataja po sobie. Blokuje jedna rzecz (B1):
plik trzymany przez inny program bez zgody na odczyt dluzej niz ok. 2,3 s dostaje wpis "nie da sie odczytac" i juz NIGDY nie
jest brany pod uwage, choc jest dobrym skanem - potwierdzone uruchomieniem w dwoch wariantach. Szesc uwag P dotyczy sytuacji,
w ktorych skan przepada po restarcie programu, stare pliki sa zglaszane jako nowe, wynik dostaje skrot innego skanu albo
nazwa pliku projektu (nazwisko) wychodzi w wyniku. Wszystkie poprawki sa male i mieszcza sie w plikach paczki.

## 1. Uwagi (B = blokujaca, P = poprawic przed scaleniem, D = drobna / moze zostac jako znana)

| Nr | Waga | Plik:linia | Scenariusz (wejscie -> zly wynik) | Sprawdzone | Oczekiwane |
|---|---|---|---|---|---|
| B1 | B | `stanowisko/scanner.py:60` (`PROBY_ODCZYTU = 40`), `112-118`, `424-427`, `461-466` | Program zapisuje caly plik i trzyma go otwartego BEZ zgody na odczyt przez inne programy (uchwyt wylaczny - tak domyslnie otwieraja plik np. `File.Create` / `File.OpenWrite` w .NET) dluzej niz ok. 2,3 s po ostatnim zapisie (0,3 s stabilizacji + 40 obiegow x 0,05 s). Albo: plik jest juz zapisany i zamkniety, a inny program (podglad w programie skanera, antywirus, kopia zapasowa) trzyma go wylacznie przez ponad 2,3 s. `sprawdz_stl` zwraca wtedy `blad_odczytu`; ta galaz nie pyta `ktos_pisze`, nie czeka `odrzuc_po_s`, a po 40 probach wpisuje `_znane[k] = podpis` i zglasza odrzucenie. Zwolnienie pliku nie zmienia rozmiaru ani czasu modyfikacji, wiec przeglad co 2 s pomija plik (`_znane == podpis`), a po restarcie programu jest on "zastany". Skutek: dobry skan nie daje zdarzenia nigdy; technik widzi tylko "pliku nie da sie odczytac (40 prob)". Jesli program skanera zapisuje tak kazdy plik, nie przejdzie zaden skan. Opis modulu mowi co innego ("plik stabilny, ale zly, czeka `odrzuc_po_s`", "odrzucenie nie jest ostateczne"). Wariant lagodniejszy: uchwyt wylaczny i przerwa 3,5 s w srodku zapisu daje falszywy wpis `blad_odczytu`, zdarzenie przychodzi dopiero po zamknieciu. | **Uruchomieniem na PC** (`x\eksp1.py`, parametry domyslne). `a`: zapis wylaczny, uchwyt trzymany 4 s -> odrzucenie `blad_odczytu` w 2,81 s, 0 zdarzen do konca proby (9 s po zamknieciu). `b4`: plik zapisany i zamkniety, potem wylaczny odczyt 4 s -> odrzucenie w 2,81 s, 0 zdarzen. `b1` (to samo, 1 s) -> zdarzenie w 1,01 s. `a2` (przerwa 3,5 s) -> odrzucenie w 2,75 s, zdarzenie w 3,82 s. | Odmowe dostepu z powodu wspoldzielenia traktowac jak "ktos jeszcze trzyma plik" (czekac, nie liczyc prob); limit liczyc czasem, nie liczba obiegow; po wpisie `blad_odczytu` NIE zapamietywac pliku jako rozstrzygnietego (ponawiac przy przegladzie). Testy: uchwyt wylaczny 4 s przy zapisie i po zapisie; w symulatorze sposob zapisu z uchwytem wylacznym. |
| P1 | P | `stanowisko/silnik.py:220` (oraz `365-367`, `199-201`) | Plik skanu zapisany ponownie pod ta sama nazwa, gdy jego zadanie czeka w kolejce (kolejka przy 20 plikach to minuty; staly plik wyjsciowy skanera to mozliwy sposob pracy - struktury eksportu nie znamy). Silnik analizuje to, co lezy na dysku w chwili startu zadania, a w wyniku wpisuje `skan_sha16` ze zdarzenia (stara zawartosc) - bez sprawdzenia skrotu, rozmiaru ani czasu pliku. Wynik plytki B trafia do bazy jako skan A; A1 uzywa `sha16` do rozpoznania ponownego skanu (`session.py:593` na `e3/a1`). `zlec_skan` gubi tez `rozmiar` i `czas_pliku` zdarzenia. | **Uruchomieniem na PC** (`x\eksp2.py s1`, funkcja probna): zadanie A - `skan_sha16` w wyniku `e86185e7ff80c034`, skrot tresci faktycznie analizowanej `7ffe0c59b2e412fc`. | Proces roboczy sprawdza plik przed analiza i po wczytaniu (skrot albo rozmiar + czas ze zdarzenia); niezgodnosc = `blad` "plik skanu zmienil sie", nigdy wynik z cudzym skrotem. Test. (Docelowo kopia skanu do folderu programu w chwili zdarzenia - decyzja A3 / DW4.) |
| P2 | P | `stanowisko/scanner.py:179`, `253-260` (`zglos_zastane=False`); `stanowisko/silnik.py:326-334` | (a) Skan zapisany, gdy program nie dziala (awaria, restart w trakcie wieczoru), albo (b) program zamkniety, gdy skany czekaja w kolejce silnika. Po starcie pliki sa "zastane" i nie daja zdarzenia; `stop()` nie zglasza zadnego zdarzenia dla zadan porzuconych ani dla analizy w toku. Te skany nie sa analizowane nigdy i nikt o tym nie wie. Jedyne wyjscie w paczce to `zglos_zastane=True`, czyli liczenie skrotu KAZDEGO pliku w folderze przy kazdym starcie (folder rosnie) i zdarzenia dla calej historii. Opisy przyznaja to uczciwie (`silnik.md:80-81`, `scanner.md:81-82`) i odsylaja do A1 / A3, ale kontrakt nie daje A3 narzedzia. | Czytaniem; `test_pliki_zastane` potwierdza (a); **uruchomieniem** (`x\eksp2.py s3`): `stop()` przy 1 zadaniu w toku i 3 w kolejce trwal 0,03 s, zdarzenia tylko `gotowy` i `start 1`, 3 zadania zostaja w kolejce bez sladu. | Parametr obserwatora dla startu, np. "pliki nowsze niz podany czas" albo funkcja "czy ten plik (sciezka, rozmiar, czas) jest juz znany" - A3 poda dane z bazy; `stop()` zwraca albo zglasza zadania niewykonane. Albo jawna decyzja wlasciciela, ze takie skany powtarza technik (pytanie w pkt 4). |
| P3 | P | `stanowisko/scanner.py:252-253`, `398-399`, `411-413` | Stare pliki zglaszane jako NOWE skany mimo `zglos_zastane=False`: (a) folder niedostepny przy starcie programu (dysk sieciowy, OneDrive jeszcze niepodlaczony) i pojawia sie pozniej z cala historia - kazdy plik daje zdarzenie i zadanie analizy; (b) chwilowy blad listowania folderu albo podfolderu (`pliki_w_folderze` pomija `OSError`) - pliki nie trafiaja do `widziane`, linia 411-412 kasuje je z `_znane`, nastepny przeglad zglasza je od nowa. Skutek: dziesiatki zbednych analiz po 1 min, prawdziwy nowy skan czeka na koncu kolejki, w bazie stare plytki jako dzisiejsze. | **Uruchomieniem na PC** (`x\eksp1.py`): `e2` - folder pojawia sie 1 s po starcie z 3 starymi plikami -> 3 zdarzenia, `ponowny=False`; `e3` - jeden przeglad zwraca pusta liste (blad listowania udawany podmiana funkcji, tryb odpytywania) -> 3 zdarzenia dla plikow zastanych. Prawdziwego dysku sieciowego nie mialem. | Stan "zastane" ustalac przy PIERWSZYM udanym przegladzie folderu, nie tylko w `przygotuj`; pliku nie zapominac, gdy jego katalogu nie dalo sie wylistowac (`pliki_w_folderze` na `przed-skanerem` ma juz parametr `niedostepne`). Testy obu przypadkow. |
| P4 | P | `stanowisko/silnik.py:178-194` | `wyjscie`: nazwa pliku to `<nazwa skanu>_wynik.json` / `_podglad.npz`. Dwa skany o tej samej nazwie w roznych podfolderach (skaner zapisujacy zlecenia w podfolderach pod stala nazwa) albo ponowny skan pod ta sama nazwa nadpisuja sobie pliki; `ZdarzenieSilnika.pliki` pierwszego zadania wskazuje wtedy dane drugiego - obraz odchylek w oknie (A3) pokaze inna plytke. `silnik.md:84` wspomina tylko ponowna analize tego samego skanu. Zapis nie jest atomowy (urwany JSON po awarii). | **Uruchomieniem na PC** (`x\eksp2.py s2`): `zlec1\scan.stl` i `zlec2\scan.stl` -> jeden plik `scan_wynik.json`; plik wskazany przez zdarzenie zadania 1 zawiera `zadanie_id=2` i skrot drugiego skanu. | Nazwa z `skan_sha16` (np. `<sha16>_wynik.json`) albo podfolder na zadanie; zapis przez plik tymczasowy i `os.replace`. Test. |
| P5 | P | `stanowisko/silnik.py:209-217` (zrodlo tekstu: `synth.py:151`, wolane z `match.py:151`) | K10: projekt w puli, ktorego nie da sie wczytac (pusty, uszkodzony, w trakcie kopiowania przez OneDrive) -> `synth.wczytaj_projekt` ostrzega "pomijam projekt <NAZWA PLIKU>: ...". Silnik przenosi ostrzezenia do `wynik["ostrzezenia"]` bez czyszczenia; `bez_nazw_z_puli` dziala tylko na tekst bledu i tylko na sciezki z folderem puli, a tu jest sama nazwa pliku. Nazwa pliku projektu (nazwisko) trafia do zdarzenia, do `<skan>_wynik.json` w `wyjscie` i dalej do bazy A1 ("wynik JSON zapisywany w calosci"), wbrew regule "poza baza tylko sha16" i kryterium 8 paczki A1. | **Uruchomieniem na PC** (`x\eksp2.py s4`, prawdziwa `match.Pula` w procesie roboczym, plik-smiec o fikcyjnej nazwie): `ostrzezenia: ['pomijam projekt FikcyjnaTestowa-11-crown_cad.stl: ...']` w zdarzeniu i w pliku JSON. | W procesie roboczym zamieniac w ostrzezeniach (i w bledach) nazwy plikow puli na `sha16` albo znacznik - lista plikow puli jest znana (`pliki_projektow`). Test z plikiem-smieciem w puli. |
| P6 | P | `stanowisko/silnik.py:257-261`, `418`; `opisy_modulow/silnik.md:47` | Proces okna zabity twardo (Menedzer zadan, awaria Qt) w trakcie analizy: proces roboczy liczy dalej do konca zadania i konczy sie dopiero przy probie odeslania wyniku. Limit czasu pilnuje nadzorca, ktorego juz nie ma - analiza zawieszona (przypadek z P3a pkt 5.1) zostaje na zawsze, z pula projektow w pamieci (zuzycia RAM nie mierzylem). Technik uruchamia program ponownie -> dwa procesy liczace naraz. Zdanie z opisu "proces roboczy konczy sie sam, gdy zniknie proces okna" jest prawdziwe tylko miedzy zadaniami. | **Uruchomieniem na PC** (`x\eksp3.py`, zadanie probne 25 s, proces okna zakonczony `os._exit`): proces roboczy ZYJE po 0,5 / 5 / 15 / 22 s, znika po 30 s. | Watek w procesie roboczym czekajacy na koniec procesu rodzica (`multiprocessing.parent_process()`), ktory konczy proces od razu; poprawic zdanie w opisie. Test. |
| D1 | D | `stanowisko/scanner.py:263-301`, `391-400`, `242` | Folder obserwowany usuniety i odtworzony miedzy dwoma przegladami: obserwator `watchdog` nie jest uruchamiany od nowa (`_watchdog is not None`), dalej dziala tylko przeglad co 2 s, a `stan()["obserwator"]` nadal mowi `watchdog`. Skan nie ginie, ale S1 ("ponizej 1 s") przestaje byc spelnione do restartu. | **Uruchomieniem** (`x\eksp1.py e6`): plik zapisany w 1,51 s, zdarzenie w 3,86 s (zwykle 0,33 s). Jedna proba. | Sprawdzac w przegladzie, czy obserwator zyje; po zdarzeniu usuniecia katalogu glownego uruchamiac go od nowa. |
| D2 | D | `stanowisko/silnik.py:416-449` (brak sprzatania przy wyjsciu bez `stop()`) | Program konczy sie bez `Silnik.stop()` w trakcie analizy: sprzatanie `multiprocessing` i watek nadzorcy zamykaja ten sam proces jednoczesnie -> na ekranie slad "Exception ignored in atexit callback ... OSError: [WinError 6]"; nadzorca moze tez zdazyc uruchomic nowy proces roboczy w trakcie zamykania. Proces roboczy konczy sie od razu (sprawdzone). | **Uruchomieniem** (`x\eksp2.py miekko`). | `atexit` albo wymaganie w opisie: A3 wola `stop()` w `closeEvent`. |
| D3 | D | `stanowisko/silnik.py:384-390`, `478-481`, `505-507` | `czekaj_na_pusta_kolejke` i `zajety()`: miedzy zdjeciem zadania z kolejki a ustawieniem `_biezace` oraz miedzy `_biezace = None` a wyslaniem zdarzenia `wynik` jest okno, w ktorym funkcja zwraca True przed koncem pracy. Dotyczy testow i narzedzi (`symulator --analiza`), nie wynikow. | Czytaniem. | Ustawiac `_biezace` pod zamkiem razem z kolejka; `None` dopiero po `_zglos`. |
| D4 | D | `stanowisko/silnik.py:457-460`, `511-520` | (a) Limit czasu jest sprawdzany tylko w obiegu bez wiadomosci - zadanie, ktore stale wysyla postep, nie zostanie przerwane. (b) Proces roboczy, ktory zglasza gotowosc i ginie bez zadania, jest uruchamiany od nowa bez konca i bez komunikatu. Oba przypadki malo prawdopodobne. | Czytaniem. | Limit sprawdzac takze po odebraniu wiadomosci; licznik restartow bez zadania. |
| D5 | D | `stanowisko/scanner.py:457-458`, `472`; `stanowisko/silnik.py:201` | Nazwa pliku skanu w logu (poziom INFO) i w tekscie bledu "brak pliku skanu ...". Jesli zlecenia w programie skanera beda nazywane nazwiskami, nazwy trafia do logu. Nazw projektow w logach obu modulow nie ma (poza P5). `Odrzucenie.plik` i `ZdarzenieSkanu.plik` / `duplikat_z` niosa pelna sciezke - to potrzebne, ale A3 nie powinien ich wypisywac. | Czytaniem. | W logu `sha16` i numer zdarzenia; nazwa na poziomie DEBUG. Do decyzji po dniu skanera (B2). |
| D6 | D | `stanowisko/scanner.py:126-129`, `opisy_modulow/scanner.md:72` | STL tekstowy oraz binarny STL z dodatkowymi bajtami za danymi sa odrzucane z powodem (widoczne, nic nie ginie po cichu). To decyzja ponad plan (S2 mowi tylko "rozmiar, liczba trojkatow") - gdyby skaner tak eksportowal, zaden skan nie przejdzie. Opisane w granicach. | Czytaniem; `test_sprawdz_stl_powody`. | Zostaje do B2; wpisac na liste rzeczy do sprawdzenia w dniu skanera. |
| D7 | D | `stanowisko/silnik.py:314`, `360-362`, `553` | `zadanie_id` liczy sie od 1 w kazdym obiekcie `Silnik` (po `stop()` trzeba utworzyc nowy). Sygnaly `wynik(int, object)` / `blad(int, str, str)` niosa tylko numer - A3 musi kluczowac po obiekcie silnika albo brac `zdarzenie(object)`. | Czytaniem. | Zdanie w opisie dla A3. |
| D8 | D | `stanowisko/silnik.py:23-24`, `opisy_modulow/silnik.md:75-76` | Proces roboczy importuje glowny modul programu. Jesli plik startowy A3 importuje PySide6 na gorze, kazdy proces roboczy zaladuje Qt przed Open3D - tej konfiguracji zaden test nie cwiczy (w pytest glownym modulem jest pytest). Brak tez wzmianki o `freeze_support` dla wersji zamrozonej (DY1). | Czytaniem. | Wymaganie dla A3: plik startowy bez importow Qt na poziomie modulu (import w `main()`); test A3 z prawdziwa analiza uruchomiona z tego pliku. |
| D9 | D | `testy/test_scanner.py:233-248`; `testy/test_silnik.py:420-452` | Dwa testy "20 plikow" wymagaja, by zapisy konczace sie co 0,15 s daly zdarzenia w tej samej kolejnosci - zalezne od obciazenia komputera (jedno zaciecie watku ponad 0,15 s = czerwony test). U mnie zielone (1 przebieg). Reszta testow czeka na warunek, nie na czas; procesy i obserwatory zatrzymuje fixtura; katalogi w `tmp_path`. | **Uruchomieniem**: `test_scanner.py` 25 passed w 51,6 s; `test_silnik.py` 21 passed / 5 skipped w 154 s. | Odstep 0,3-0,5 s albo porownanie z kolejnoscia `mtime` bez wymagania zadanej kolejnosci. |
| D10 | D | `testy/test_scanner.py`, `narzedzia/symulator_skanera.py:117-142` | Luki testow: brak uchwytu wylacznego (B1), folderu pojawiajacego sie z plikami i bledu listowania (P3), pliku nadpisanego w kolejce (P1), kolizji nazw w `wyjscie` (P4), usuniecia i odtworzenia folderu (D1), ostrzezenia z nazwa projektu (P5). Symulator otwiera pliki zwyklym `open` (pelne wspoldzielenie) - nie pokazuje programu z uchwytem wylacznym. | Czytaniem. | Dodac przy poprawkach. |
| D11 | D | `stanowisko/scanner.py:221-227`, `141-150`, `401-413` | (a) `stop()` czeka 5 s; gdy watek liczy skrot duzego pliku na wolnym dysku, `stop()` wraca, watek pracuje dalej i moze zglosic zdarzenie po zatrzymaniu, a kolejny `start()` uruchomi drugi watek na tym samym stanie. (b) Liczenie skrotu wstrzymuje ocene pozostalych plikow (bez strat). (c) Caly folder z podfolderami jest listowany co 2 s - przy tysiacach plikow na dysku sieciowym to staly ruch. | Czytaniem. | (a) nie zerowac `_watek`, gdy watek zyje; (b), (c) do pomiaru w B2. |
| D12 | D | `raporty/E3-A2_2026-11-17.md:31`, opis PR | Kryterium 6 (plytka do 60 s) na skanie odniesienia: 1 z 3 - raport mowi to wprost. To czas `porownaj` na zajetym PC, nie wada silnika (narzut: start procesu 2-4 s); u mnie mala plytka z atrap 11,6 s, przerwa petli Qt 11 ms. Kryterium zostaje niespelnione do pomiaru na wolnym PC albo laptopie stanowiska. | Raport + moj przebieg `test_silnik.py`. | Pomiar przed A3 / D4; nie blokuje scalenia. |

## 2. Ocena odstepstw zgloszonych przez wykonawce

**(a) Kryterium 5 - rownosc decyzji zamiast rownosci pol: uczciwe i dopuszczalne, z jednym zastrzezeniem.**
Niepowtarzalnosc `porownaj` potwierdzilem wlasnym przebiegiem `test_silnik.py`: plytka `okragla_poranna` - 18 pol roznych
przy 1e-9 miedzy silnikiem a wierszem polecen (`skala.iteracje` 41 / 20, liczniki punktow o 1, transformacja o ok. 6e-6),
a te same 18 pol miedzy dwoma procesami silnika (test "po restarcie procesu"). To nie silnik wprowadza roznice. Co test
pomija: `bez_czasow` usuwa klucze zaczynajace sie od `czas` na kazdym poziomie; poziom 2 (domyslny, male plytki): liczby
zmiennoprzecinkowe do 2e-3 wzglednie ALBO bezwzglednie, liczniki probek (pola z `punkt` w nazwie, `komorek`, `brak_danych`)
do 2 sztuk albo 1 %, bez `iteracje`; struktura, teksty, wartosci logiczne i pozostale liczby calkowite dokladnie. To nie jest
za luzne - 0,002 mm to wg komentarza w tescie 25 razy mniej niz najmniejszy prog decyzji (0,05 mm; progu sam nie
sprawdzalem), a u mnie na poziomie 2 bylo 0 pol roznych w 4 z 4 typow.
Zastrzezenie: poziom 3 (skany odniesienia) nie porownuje ZADNEJ liczby zmiennoprzecinkowej (`tol = inf`) - ubytek 0,5 mm
i 1,5 mm przeszedlby, jesli status i liczba ubytkow sa te same. Proponuje dodac tam prog posredni (np. 0,1 mm) jako
wymagany - drobne, nie blokuje. Sama niepowtarzalnosc korekty skali w `match` warta jest osobnej decyzji wlasciciela
(wynik tej samej plytki moze sie roznic miedzy dwoma skanami o wiecej niz szum).

**(b) Progi czasu i testy wlaczane zmiennymi: dopuszczalne.** Domyslny przebieg nadal sprawdza rzeczy istotne: liczniki
dokladnie (100 z 100 zdarzen, 0 przed koncem zapisu, 0 zlych skrotow, 0 odrzucen), kolejnosc, 7 rodzajow plikow zlych,
ponowny zapis i duplikat, rownosc wynikow na 4 typach plytek, 6 rodzajow awarii, brak ciezkich bibliotek w procesie okna,
petle Qt. Poluzowane sa tylko progi czasu (mediana 2,0 s zamiast 1,0; plytka 180 s zamiast 60; przerwa petli 1000 ms zamiast
200) - zmierzone u mnie 0,340 s, 11,6 s i 11 ms, czyli z duzym zapasem takze wobec progow scislych. Prog przerwy petli moglby
zostac 200 ms bez ryzyka losowej czerwieni. 5 wariantow na skanach odniesienia wymaga danych spoza repozytorium, wiec `skip`
z opisem jest wlasciwy; nie uruchamialem ich (ograniczenie obciazenia PC).

**(c) Dodatki poza planem: do przyjecia, `wyjscie` po poprawce P4.** `lacznik_qt` jest potrzebny do kryterium 6 i dla A3;
`anuluj` to 8 linii z testem; `pamiec_linii` korzysta z istniejacego `krawedz.ustaw_katalog_pamieci`, pliki nazywane skrotem
projektu (bez nazwisk), domyslnie wylaczona, test potwierdza 4,0 s -> 0,01 s; `wyjscie` daje A3 material na obraz odchylek,
ale ma kolizje nazw (P4). Zaden dodatek nie zmienia istniejacych plikow ani kontraktu 3.8 (pola dodatkowe maja wartosci
domyslne).

**(d) Blad "DLL load failed while importing Shiboken": w aplikacji malo prawdopodobny, ale nie wykluczony.** W programie
okno laduje Qt jako pierwsze, a analizy liczy inny proces, wiec kolejnosc z testu (pierwszy import Qt po analizach) nie
wystapi przy starcie. Przyczyna jest jednak nieustalona, wiec nie wiadomo, czy to samo nie dotknie modulu Qt ladowanego
pozniej (np. okno ustawien albo wydruk otwierane pierwszy raz po kilku analizach). Bledu nie probowalem odtworzyc (wymaga
analiz na skanach odniesienia). Zalecenie dla A3: wszystkie moduly PySide6 importowac przy starcie programu oraz jeden test
"analiza, potem pierwsze otwarcie kazdego okna". Patrz tez D8 (proces roboczy importuje plik startowy programu).

## 3. Co sprawdzilem i nie budzi zastrzezen

- Koniec zapisu: cztery warunki naraz (stabilnosc, rozmiar zgodny z naglowkiem, nikt nie pisze, podpis bez zmian po skrocie);
  zapis w kawalkach z przerwami dluzszymi niz 300 ms, zapis z zamykaniem po kazdym kawalku, plik tymczasowy ze zmiana nazwy,
  uchwyt trzymany po ostatnim kawalku (z pelnym wspoldzieleniem) - testy przechodza, w moim przebiegu 100 z 100 zdarzen,
  0 przed koncem zapisu, mediana 0,340 s, max 0,401 s.
- Odpytywanie zapasowe istnieje (przeglad co 2 s niezaleznie od `watchdog`) i dziala takze bez biblioteki; podfoldery sa
  obslugiwane (`rekurencyjnie=True`); plik odrzucony jako niepelny jest oceniany od nowa po zmianie.
- Wyscigi miedzy watkiem `watchdog` a watkiem obserwatora: watek `watchdog` tylko dopisuje do `deque` i ustawia `Event`;
  caly stan zmienia jeden watek. Nie znalazlem bledu.
- Silnik: metoda `spawn`, lacze `Pipe` zamykane po stronie rodzica (smierc procesu = koniec danych), jedna analiza naraz,
  kolejnosc zlecen, numer zadania sprawdzany przy kazdej wiadomosci (spozniona wiadomosc po limicie czasu nie trafi do
  innego zadania), wyjatek / `SystemExit` / zabity proces / limit czasu / blad startu = `blad` i nastepne zadanie; `stop()`
  nie zakleszcza sie (0,03 s przy analizie w toku, proces roboczy konczy sie). `porownaj` nie uruchamia wlasnych procesow,
  wiec `daemon=True` nie przeszkadza.
- Kontrakty 3.8: `ZdarzenieSkanu` ma `plik`, `sha16`, `rozmiar`, `trojkaty`, `czas_pliku` (sekundy od epoki) - zgodne z tym,
  co czyta `session.przyjmij_wynik` na `e3/a1`; wynik = slownik `porownaj` + `ostrzezenia` + `zadanie_id` + `skan_sha16`
  (test sprawdza rownosc zbioru kluczy z wierszem polecen); `ZadanieAnalizy` ma pola z planu, `rozpoznaj` = `auto`.
- Sygnatura `porownaj` i funkcje brane z `dzien_skanera_rdzen` sa zgodne takze po scaleniu `35ec579` (czytaniem diffu;
  `pliki_w_folderze` dostal tam tylko dodatkowy parametr opcjonalny).
- Higiena: 8 plikow dodanych, 0 zmienionych; 0 znakow spoza ASCII i 0 znakow CR w 8 plikach; importy tylko z biblioteki
  standardowej, `watchdog`, `PySide6`, `numpy` (wszystko w `requirements.txt`); "start skanu" to atrapa, zadnego klikania
  w programie skanera; nazwisk i nazw zlecen w diffie nie ma (dane testowe fikcyjne).
- Raport wykonawcy: liczby, ktore moglem porownac (opoznienie zdarzenia, czas malej plytki, przerwa petli Qt, 25 + 21 testow,
  5 pominietych), zgadzaja sie z moim przebiegiem.

## 4. Pytanie do wlasciciela

1. Gdy program zostanie zamkniety albo zawiesi sie w trakcie wieczoru, a w folderze skanera sa skany jeszcze niesprawdzone
   (zapisane, gdy program nie dzialal, albo czekajace w kolejce): czy po ponownym uruchomieniu program ma je sprawdzic sam?
   Proponuje: tak - wszystkie pliki nowsze niz ostatni skan zapisany w bazie. Dzis takie skany przepadaja bez komunikatu (P2).

## 5. Czego NIE sprawdzilem

- Wariantow na skanach odniesienia 45-55 MB (`E3A2_DANE_REF`, `E3A2_SCISLE`) i liczb z raportu, ktore od nich zaleza
  (16 / 16 decyzji, czasy 49-80 s); pelnego pytest; stanu po scaleniu `9cd0ac9` uruchomieniem (tylko diff).
- Prawdziwego dysku sieciowego i OneDrive (gubienie powiadomien, opoznione czasy plikow, pliki "tylko online"); blad
  listowania w P3 jest udawany. Systemow innych niz Windows.
- Bardzo duzych plikow na wolnym dysku (czas liczenia skrotu), tysiecy plikow w folderze, zuzycia pamieci procesu roboczego
  po wielu analizach z rzedu (proces zyje caly dzien, nie jest odswiezany).
- Odtworzenia bledu Shiboken; `lacznik_qt` w prawdziwym oknie; `symulator_skanera.py` od linii 260 i tryb `--analiza`.
- Czy `watchdog` po usunieciu folderu zglasza cokolwiek (D1 to jedna proba, wynik = opoznienie, nie przyczyna).
- Zachowania prawdziwego programu skanera (sposob otwierania pliku, nazwy, pliki tymczasowe) - nikt go jeszcze nie ma;
  B1 pokazuje, ze od tego zalezy, czy skany w ogole przechodza.
