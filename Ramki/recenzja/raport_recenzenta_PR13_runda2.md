# Raport recenzenta PR #13 - runda 2 (przyrostowa)

Data: 2026-11-17. Recenzent: swieza subsesja, niezalezna od wykonawcow poprawek i koordynatora; werdyktu rundy 2 nie znalem.
Stan recenzowany: `origin/przed-skanerem` @ `58a1a36`. Zakres: `git diff a6cf3a4..58a1a36 -- Ramki/stanowisko` (20 plikow:
kod, testy, opisy modulow, raporty wykonawcow; zmian w `00_NADZOR_STAN.md`, planie etapu 3 i raporcie pomiarow
koncowych `P2_P4_pomiary_koncowe_2026-11-17.md` nie recenzowalem). Podstawa: `recenzja/raport_recenzenta_PR13_runda1.md`
(B1, P1-P7, D1-D12) oraz raporty wykonawcow `raporty/PR13_poprawki_obliczenia_2026-11-17.md` i
`raporty/PR13_poprawki_dzien_skanera_2026-11-17.md` (czytane jako twierdzenia do sprawdzenia).

Metoda: czytanie calego diffu kodu i testow oraz kontekstu w plikach (`inspect.py`, `krawedz.py`, `porownaj.py`,
`dzien_skanera_rdzen.py`, `dzien_skanera.py`, czesci `ui_test.py` i narzedzi metryk). Uruchomienia wylacznie na PC
(`<PC-katalog>\app\r13b`, kod z `git archive 58a1a36`, ustawienia = `ustawienia_wzor_pc.toml`, `run.cmd` z limitem
watkow, 1 proces python, wolny RAM 14-18 GB przed startem): jeden skrypt prob `proba_r2.py` (3 proby, ok. 1 min).
Odczytane logi PC: pelny pytest koordynatora `k2\pytest_58a1a36.log`, logi wykonawcow z testami na `a6cf3a4`
(`p1\logi\czerwone_a6cf3a4.log`, `p2\ds_czerwone.log`). Na MSI nie uruchamiano pytest ani obliczen. Cytaty bez znakow
diakrytycznych.

## 0. Werdykt

**do scalenia po poprawkach** - nowe uwagi: B 0 / P 1 / D 9.

Wszystkie uwagi B1 i P1-P7 z rundy 1 sa zalatwione; testy dodane do uwag odtwarzaja scenariusze z rundy 1 (byly
czerwone na `a6cf3a4`: log p1 5 failed / 3 passed - czerwone dokladnie B1, P1 x2, P7 x2; log p2 14 failed - P2-P6, D1,
D10, test okna P4), istniejacych testow nie oslabiono (w czterech plikach testow jedyna usunieta linia to import).
Pelny pytest na `58a1a36`: **434 passed, 3 skipped, 0 failed** (522 s; 1 ostrzezenie z `test_auto_uklad`, niezwiazane)
= 408 + 8 (obliczenia) + 18 (okno), zgodnie z raportami wykonawcow.

Jedna nowa uwaga P (P-n1): poprawka P5 (usuwanie nazw projektow z TEKSTU JSON manifestu) psuje JSON, gdy nazwa
`*_cad.stl` stoi w wielowierszowej notatce za znakiem nowej linii albo tabulatora - pakowanie konczy sie wtedy
wyjatkiem przy kazdej probie (sprawdzone uruchomieniem). Danych to nie niszczy, ale blokuje "Zakoncz i spakuj" z
niezrozumialym komunikatem. Poprawka to kilka linii + test. "Znana granica" P5 (nazwa folderu projektu exocad w
sciezkach innych plikow) nie blokuje scalenia - patrz pkt 3.

## 1. Uwagi rundy 1 -> stan

| Nr | Stan | Co zrobiono / dowod | Test odtwarza scenariusz z rundy 1? |
|---|---|---|---|
| B1 | zalatwione | `inspect.py:506-509`: odleglosc od linii i numer filaru tylko przy `brzeg.drzewo is not None`; bez linii - od z = 0, filar 0 (jak `plamy_pod_powierzchnia:333-337`). `probka_od_linii:392` sprawdza tez `drzewo_O`. Przeczytalem sciezke trybu sumy dla projektu bez linii: `probka_suma` = pelny pas sprzed P2 (czesc od linii pusta, filtr pominiety), wiec probka metody B jest identyczna z trybem `plaszczyzna`; `ocena_brzegu` -> `sprawdzony` = True + uwaga. Zachowanie = sprzed P2, dochodzi tylko uwaga "linii brzegu projektu nie wyznaczono ... (jak przed P2)". `try` w `porownaj` (P7) dodatkowo chroni plytke. | Tak: `test_inspect.py::test_projekt_bez_linii_z_wcieciem_w_trybie_sumy_dziala_jak_przed_p2` = scenariusz z rundy 1 (pudelko 8 x 6 x 5, wglebienie 0,3 mm na scianie i wierzchu); porownuje status, ubytki, wciecia, plamy i `linia_brzegu` z trybem `plaszczyzna` pole po polu; na `a6cf3a4` czerwony (log p1). |
| P1 | zalatwione | `krawedz.LinieProjektu.filary_bez_linii` (z `niecki`: przyjeta i bez wpisu w `filary`; numeracja niecek = `nr` filaru - sprawdzone w `obszary_filarow:327-332` i `wyznacz:786-815`), `stan` = `czesciowe`. `inspect.ocena_brzegu:620-639`: tryb `linia` - wpis w `filary` z kompletem pol, numer w `nie_sprawdzono` -> status `nie_sprawdzono`; tryb sumy - uwaga w `uwagi_linii`. Format wyniku addytywny: w `brzeg` pole tylko gdy niepuste; w `krawedz.opis()` nowy klucz zawsze (lista pusta); wersja pamieci linii bez zmiany, ale `filary_bez_linii` liczy sie ze starych `niecki` (klucz `filar` byl zapisywany juz wczesniej). `stan` czyta tylko JSON i `metryki_krawedz` (licznik). | Tak, syntetycznie: `test_krawedz.py::test_filar_z_niecka_bez_linii_jest_jawny` (podmiana `_warianty_filaru`, takze po `przeksztalc` i zapisie / odczycie npz), `test_inspect.py::test_filar_z_niecka_bez_linii_nie_znika_po_cichu` (tryb `linia` przed poprawka = `ok`; tryb sumy z ukruszeniem na filarze bez linii widzi je pasem od plaszczyzny). Prawdziwego projektu z takim filarem w puli nie ma (jak w rundzie 1). |
| P2 | zalatwione | `Zbieracz._zapisz_znane` (`dzien_skanera_rdzen.py:1439-1449`) przed kazdym zapisem `obserwator.json` wola `Sesja.zapisz_zalegle`; jedyny zapis stanu obserwatora idzie ta droga (sprawdzone wyszukaniem). `znane[...]` jest ustawiane po kopii i przed `dodaj_plik` bez zapisu stanu pomiedzy (`:1794-1814`). Odwrotna awaria (wpis jest, "znany" nie) = ponowna kopia usuwana jako ta sama tresc. Dodatkowo `_zapomnij_kopie_bez_wpisu` przy wznowieniu (sesje zapisane stara wersja). Opis modulu poprawiony (`dzien_skanera.md` pkt 1). | Tak: `test_awaria_w_srodku_serii_stan_obserwatora_nie_wyprzedza_manifestu` (migawka folderu w trakcie kopii drugiego pliku; asercja "znany => w manifescie") i `test_kopia_bez_wpisu_w_manifescie_jest_po_wznowieniu_podjeta_ponownie`; oba czerwone na `a6cf3a4` (log p2). |
| P3 | zalatwione | `plik_roboczy_programu` (`:2037-2049`): plik z manifestu nigdy nie jest roboczy; robocze = `*.czesc` spoza manifestu, `.tmp` / `.bak` czterech plikow zapisu atomowego w korzeniu i `kontrole/*`. Uzywane w `_pliki_sesji` i w liscie "dodatkowe" `--sprawdz`; `--sprawdz` folderu zglasza tez plik z manifestu bez sumy (folder = ZIP). | Tak: `test_pliki_bak_tmp_czesc_ze_skanera_sa_w_paczce_a_pliki_robocze_programu_nie` (sumy, ZIP, `--sprawdz` folderu i ZIP); czerwony na `a6cf3a4`. |
| P4 | zalatwione (scenariusze a i b z rundy 1) | `spakuj`: znaczniki tylko w kopii manifestu w pamieci (`m_po`), wszystkie czesci budowane jako `*.zip.czesc`, `os.replace` dopiero po zbudowaniu wszystkich, stare czesci o innych nazwach kasowane po zamianie, raport i sumy potem, znaczniki w `sesja.json` na koncu; `except BaseException` usuwa `.czesc` i przepuszcza wyjatek; `przerwij()` miedzy plikami. Okno: pytanie przy zamykaniu w trakcie pakowania (odpowiedz "Nie" zostawia okno i zbieranie). Zmiana sesji w trakcie pakowania: porownanie manifestu przed / po, zapis na dysk (D10). Przeszedlem awarie w kazdym kroku sekwencji: przed zamiana stara paczka i stan sesji nietkniete; po zamianie i przed znacznikami - nowa paczka kompletna, sesja "niespakowana" (bezpieczny kierunek). Jedna waska luka poza scenariuszami rundy 1: paczka wieloczesciowa i blad `os.replace` na drugiej czesci - D-n2 (uruchomione). Komunikat startowy po nieudanym PONOWNYM pakowaniu - D-n3. | Tak: `test_nieudane_pakowanie_nie_oznacza_sesji_i_zostawia_stara_paczke` (brak miejsca w trakcie budowy ZIP, pierwsze i ponowne pakowanie, SHA starej paczki bez zmian), `test_pakowanie_przerwane_zamykaniem_programu_i_zmiana_w_trakcie_pakowania`, test okna offscreen; czerwone na `a6cf3a4`. Bledu na etapie zamiany czesci test nie obejmuje. |
| P5 | zalatwione (nazwy plikow), nowy blad P-n1 | `czy_projekt_exocad` (nazwa zrodla / wzglednej / celu), wzor `_cad(__\w+)?\.stl$` lapie `__zmianaN`, `__N` i ich polaczenie; z paczki znikaja pliki, `kontrole/k<id>.*`, `pomiary/k<id>_*`, a nazwy - z manifestu, raportu, logu i stanu obserwatora (takze nazwy znane tylko obserwatorowi). `--sprawdz` ta sama funkcja. Nowa funkcja `bez_nazw_projektow` dziala na tekscie i przy JSON-ie manifestu potrafi go zepsuc - P-n1. "Znana granica" - pkt 3. | Tak: `test_kolejne_wersje_i_duplikaty_projektu_exocad_nie_trafiaja_do_paczki` (druga wersja, dwa razy recznie, projekt zastany tylko w obserwatorze; nazwy szukane w nazwach i TRESCI kazdego wpisu ZIP, w raporcie i sumach); czerwony na `a6cf3a4`. |
| P6 | zalatwione | Rejestr `kopie_folderow` (addytywny klucz manifestu; wszedzie `.get(..., [])`, test starej sesji bez klucza): wpis `w_toku` zapisany przed pierwszym plikiem, wynik po petli (takze po przerwaniu i braku miejsca przed kopiowaniem), `Sesja.wznow` domyka `w_toku` -> `przerwana`, `kompletnosc` daje brak, dopoki ostatnia kopia nie jest `pelna`, `--sprawdz` wiersz KOPIA FOLDERU i kod 3, ponowienie kopiuje tylko brakujace pliki (klucz zrodlo + rozmiar + mtime). Niedostepne podkatalogi liczone i logowane. Uwagi drobne: D-n6, D-n7. | Tak: 4 testy (przerwana: blad pliku + brak miejsca; zabicie programu w trakcie i wznowienie; niedostepny podkatalog; manifest bez klucza). Scenariusz z rundy 1 na starym kodzie wykonawca potwierdzil osobnym skryptem (testy na starym kodzie padaja na `KeyError`) - tego skryptu nie powtarzalem. |
| P7 | zalatwione | `porownaj.dopasuj_fragmenty:194-204`: `try` tylko wokol `I.sprawdz` + `wi.json()`; `MemoryError` jawnie przepuszczany, `KeyboardInterrupt` / `SystemExit` nie sa `Exception`. Wpis `inspekcja_z_bledem`: komplet pol zwyklego wyniku, status `nie_sprawdzono`, uwaga "blad inspekcji: ...", pole `blad`. **Nigdy zielone:** `status_gniazda` daje dla `nie_sprawdzono` zawsze `zolty` (gniazdo szare nie ma inspekcji); mapa PNG i okno koloruja po `status_gniazda`. **Widocznosc:** JSON, ostrzezenie (`ostrzezenia`, "UWAGA:"), wiersz "BLAD INSPEKCJI" w tabeli CLI, licznik `gniazda_nie_sprawdzone` (okno: "z zoltych nie sprawdzono N"), `metryki_inspekcji`: `prace_cale_nie_sprawdzono` (nie alarm). W oknie przyczyna nie jest widoczna - D-n1; metryki nie licza bledow osobno - D-n5. Wybor `nie_sprawdzono` zamiast `sprawdz` uwazam za poprawny (`sprawdz` liczy sie w metrykach jako alarm i znaczy "metoda wskazala ubytek"). | Tak: `test_porownaj_bledy.py` - blad jednego gniazda (wyjatek z B1), CLI zapisuje JSON i PNG, 3 przypadki "nie lap"; dwa pierwsze czerwone na `a6cf3a4`. Prawdziwego wyjatku poza B1 nikt nie zna - test podstawia wyjatek. |

Uwagi D z rundy 1:

| Nr | Stan |
|---|---|
| D1 | zalatwione: `strict_timestamps=False` + test pliku z 1975 r. |
| D2 | zalatwione przed zakresem (`5ef199e`); pelny pytest `58a1a36` bez bledow. |
| D3 | zostaje jako znane (bez zmian, zgodnie z zaleceniem). |
| D4 | zalatwione (zdanie w granicach `match.md`). |
| D5 | zalatwione w zakresie zalecenia: tresc uwagi mowi, czego pas od plaszczyzny nie obejmuje; logika bez zmian (sprawdzone: 0 roznic liczbowych w raporcie wykonawcy, czego nie odtwarzalem). Pomiaru trybu sumy (`1e9c90f`) i zgody wlasciciela (`92914a0`) nie recenzowalem. |
| D6 | zalatwione (zdanie w `synth.md`). |
| D7 | zalatwione: (a) `dzien_skanera.md` pkt 4 + dopisek w raporcie z 16.11; (b) `inspect.md` - akapit "Tryby pasa brzegu", tabela przypadkow bez linii, akapit o bledzie inspekcji. |
| D8 | zalatwione: stala `PRACE` usunieta, `wczytaj_pule(prace)` bez wywolan (sprawdzone wyszukaniem); zostaje nieaktualny opis w README narzedzia - D-n8. |
| D9 | bez zmian (nie wymagalo). |
| D10 | 4 z 8 wziete z testami (pliki w drodze, `zmieniono_po_spakowaniu` na dysku, `--sprawdz` kilku paczek, dwa foldery o tej samej nazwie); 4 zostaja z uzasadnieniem w raporcie wykonawcy - przyjmuje. |
| D11 | zalatwione (testy luk dodane; dwa przechodza takze na starym kodzie - zachowanie bylo dobre). |
| D12 | nie zalatwione: opis PR #13 nadal ma liczby z galezi czesciowych i niezaznaczone pole "pelny pytest"; stan faktyczny `58a1a36`: 434 / 3 skipped / 0 failed. |

## 2. Nowe uwagi

| Nr | Waga | Plik:linia | Scenariusz (wejscie -> zly wynik) | Sprawdzone | Oczekiwane |
|---|---|---|---|---|---|
| P-n1 | P | `Ramki/stanowisko/stanowisko/dzien_skanera_rdzen.py:2059-2072` (`bez_nazw_projektow`, cofanie do separatora w `:2069`), uzycie na tekscie JSON w `manifest_bez_projektow:2108-2112` | Notatka kroku (pole wielowierszowe) zawiera nazwe `*_cad.stl` pliku, ktorego nie ma w manifescie, w drugim lub dalszym wierszu, np. "Powtorka skanu.\nW folderze byl plik Y_cad.stl" (albo po tabulatorze). W `json.dumps` znak nowej linii to dwa znaki `\` `n`; `bez_nazw_projektow` cofa sie do ostatniego ukosnika odwrotnego, wiec wycina `n...Y_cad.stl` i zostawia `\projekt_pominiety` = niedozwolona sekwencja `\p` -> `json.loads` rzuca `JSONDecodeError: Invalid \escape`. `spakuj` konczy sie wyjatkiem przy KAZDEJ probie (stan sesji poprawny, `zakonczono` = None), okno pokazuje "Pakowanie nie udalo sie: JSONDecodeError ..." - technik nie ma jak sie domyslic, ze winna jest notatka. Przed ta runda (zamiana tylko znanych nazw, `str.replace`) tego bledu nie bylo. Nazwy znane (pliki z manifestu) sa zamieniane wczesniej i bledu nie wywoluja; log i stan obserwatora nie sa parsowane, wiec tam blad nie wystepuje. | **Uruchomione na PC** (`r13b\proba_r2.py`, proby 1 i 1b): `manifest_bez_projektow` dla notatek "pierwsza linia\nY_cad.stl" i "pierwsza\tY_cad.stl" -> `JSONDecodeError Invalid \escape`; "zwykla Y_cad.stl" i sciezka z ukosnikami -> poprawnie; pelny `spakuj` na sesji z testowego `sesja_z_plikami` z taka notatka -> `JSONDecodeError`, `zakonczono` na dysku None. | Usuwac nazwy na strukturze (przejscie po wszystkich napisach slownika i `bez_nazw_projektow` na kazdym napisie osobno, z `\n` jako separatorem), a nie na tekscie JSON; test: notatka z nazwa `*_cad.stl` po `\n` i po `\t` -> pakowanie udane, nazwy brak w ZIP. |
| D-n1 | D | `Ramki/stanowisko/stanowisko/ui_test.py:493-496`, `:427-429` (plik niezmieniany); `porownaj.py:488-490` | P7 w oknie: gniazdo z bledem inspekcji jest zolte "nie sprawdzono" - nigdy zielone, liczone w "z zoltych nie sprawdzono" - ale przyczyny okno nie pokazuje (ostrzezenia nie sa przechwytywane), a podglad pisze "brak mapy odchylek (bez projektu)", choc projekt jest. Blad systematyczny (np. zly klucz ustawien, blad kodu na kazdej pracy) przed PR dawal okno "Blad porownania" ze sladem; teraz cala plytka jest zolta "nie sprawdzono", co technik odczyta jako "brak danych skanu przy brzegu" i np. bedzie skanowal ponownie. Tabela CLI ma przed wierszem "BLAD INSPEKCJI" naglowek "NIE SPRAWDZONO (zolte, brzegu nie dalo sie sprawdzic)" - dla bledu nieprawdziwy powod. | Czytaniem. | W oknie pokazac `blad` (np. komunikat, gdy ktores gniazdo ma pole `blad`, i tekst w podgladzie); w tabeli CLI oddzielic gniazda z bledem od "brzegu nie dalo sie sprawdzic". Do paczki okna. |
| D-n2 | D | `dzien_skanera_rdzen.py:2304-2311`; komunikat `dzien_skanera.py:775`; `opisy_modulow/dzien_skanera.md` pkt 7 | P4, paczka wieloczesciowa (dane > 1,9 GB - realne przy kopii calego folderu skanera), ponowne pakowanie tej samej liczby czesci; `os.replace` udaje sie dla czesci 1, a dla czesci 2 pada (Windows: plik otwarty w innym programie, synchronizacja dysku, antywirus). Wynik: w `paczka/` czesc 1 nowa, czesci 2..n stare - stara paczka juz nie jest cala, nowa tez nie; sesja poprawnie "niespakowana", ale okno i opis mowia "poprzednia paczka, jesli byla, zostala bez zmian". `--sprawdz` wykrywa mieszanke (kod 1), ponowne pakowanie naprawia; dane zrodlowe nietkniete. Wykonawca zglosil podobna granice, ale nazwal ja "bezpiecznym kierunkiem". | **Uruchomione na PC** (`proba_r2.py`, proba 2): 4 czesci, blad `PermissionError` na 2. zamianie -> cz1 NOWA, cz2-cz4 STARE, `spakowano` 1, `zmieniono_po_spakowaniu` True, `--sprawdz` folderu paczki = 1 (12 x "rozna tresc w roznych czesciach archiwum"). | Przed zamiana przemianowac stare czesci na `*.zip.stara` i przywracac je w `except` (kasowac po sukcesie) albo co najmniej poprawic komunikat ("paczka w folderze moze byc niespojna - spakuj ponownie"); test bledu na etapie zamiany. |
| D-n3 | D | `dzien_skanera.py:833` (`wybierz_sesje`); `dzien_skanera_rdzen.py:627` (`Sesja.lista` bez `zmieniono_po_spakowaniu`) | Sesja spakowana, potem zmieniona, ponowne pakowanie nieudane (albo tylko zmieniona po spakowaniu). Przy starcie okno pyta "Ostatnia sesja jest zakonczona i spakowana", choc paczka na dysku jest nieaktualna (a po D-n2 - niespojna). Raport wykonawcy (pkt 5.4) twierdzi, ze po nieudanym pakowaniu okno pyta o wznowienie niedokonczonej sesji - prawda tylko dla PIERWSZEGO pakowania (`zakonczono` = None). Czesciowo stan sprzed PR. | Czytaniem. | `Sesja.lista` z `zmieniono_po_spakowaniu`; pytanie startowe "spakowana, ale zmieniona po spakowaniu - otworzyc i spakowac ponownie?". |
| D-n4 | D | `dzien_skanera_rdzen.py:2321` (`paczka.json`: `pominiete_w_paczce`, `sciezka`); granica opisana w `dzien_skanera.md` "Zalozenia i granice" | P5 / dane osobowe, stan sprzed PR (nie regresja): (a) "znana granica" - folder projektu exocad wciagniety do sesji (folder obserwowany albo przeciagniety recznie) daje w ZIP sciezki z nazwa tego folderu, a pozostale pliki projektu exocad zwykle tez maja w nazwie nazwe projektu - wzor `_cad.stl` ich nie lapie; (b) `paczka/paczka.json` lezy obok ZIP w folderze, ktory okno otwiera technikowi "do wyslania", i zawiera pelne nazwy pominietych projektow oraz sciezki z nazwa konta. | Czytaniem. | (b) w `paczka.json` znaczniki zamiast nazw (albo plik poza `paczka/`); (a) przy pakowaniu, gdy znaleziono projekt exocad, wyrazne ostrzezenie z lista folderow zrodlowych projektow ("sprawdz nazwy przed wyslaniem") albo pomijanie calego folderu zrodlowego projektu. |
| D-n5 | D | `porownaj.py:377-457` (`metryki_inspekcji`); narzedzia `metryki_*` | P7 a pomiary: wyjatek inspekcji na pracy calej liczy sie jako `prace_cale_nie_sprawdzono` (nie alarm), na pracy z ubytkiem - jako ubytek niewykryty; licznika bledow inspekcji nie ma. Blad, ktory dotyczy tylko czesci geometrii, w kampanii pomiarowej nie zatrzyma przebiegu, tylko po cichu obnizy wykrywalnosc i (pozornie) liczbe falszywych alarmow. | Czytaniem. | Licznik `bledy_inspekcji` w `metryki_inspekcji` (po polu `blad`), a narzedzia pomiarowe przerywaja albo wyraznie zglaszaja przebieg z bledami > 0. |
| D-n6 | D | `dzien_skanera_rdzen.py:472` (`stan_kopii_folderow`) | `w_manifescie` liczy wpisy `kopia_folderu` ze WSZYSTKICH krokow, nie tylko z ocenianego, wiec "porownanie z lista" (`jest = min(juz + skopiowane, w_manifescie)`) w praktyce ufa liczbom z rejestru. Dzis przycisk kopii jest tylko w jednym kroku, wiec bez skutku. | Uruchomione (proba 3: 2 wpisy w innym kroku daja dla kroku kopii `jest` = 2, `pelna`). | Filtrowac po `krok`. |
| D-n7 | D | `dzien_skanera_rdzen.py:1645-1646, 1668-1675`; `dzien_skanera_kroki.toml:355-362` | P6: plik trzymany na stale przez program skanera z blokada odczytu (baza, log) = kopia NIEPELNA "do skutku": krok 14 nigdy zielony, czerwony komunikat przy kazdym starcie, `--sprawdz` = 3 dla kazdej sesji. Instrukcja kroku 14 kaze "usunac przyczyne i kliknac jeszcze raz", a jednoczesnie "dopiero po spakowaniu zamknij program skanera" - technik nie ma jak usunac przyczyny. Wykonawca opisal to jako granice. | Czytaniem. | W komunikacie NIEPELNA podac nazwy plikow, ktorych nie udalo sie skopiowac, i co zrobic (np. zamknac program skanera i ponowic kopie przed pakowaniem). |
| D-n8 | D | `Ramki/stanowisko/narzedzia/pomiar_skanu/README.md:36`; `narzedzia/pomiar_skanu/c_wspolne.py:17` | Po D8 README nadal opisuje stala `PRACE` ze sciezka komputera testowego; w `c_wspolne.py` zostal zapis `W5 =[` (brak spacji - kosmetyka). | Czytaniem. | Poprawic zdanie w README. |
| D-n9 | D | `porownaj.py:101-104` | Komentarz mowi "bez sciezki konta", ale do `uwagi` / `blad` trafia `str(wyjatku)` (do 300 znakow), a np. `FileNotFoundError` niesie pelna sciezke z nazwa konta. JSON zostaje lokalnie - tylko higiena. | Czytaniem. | Zastapic katalog domowy przez `~` (jak `skroc_sciezke` w oknie dnia skanera) albo zostawic i poprawic komentarz. |

## 3. "Znana granica" P5 - ocena

Wykonawca zglasza, ze nazwa FOLDERU projektu exocad nadal trafia do paczki w sciezkach innych plikow. Ocena: **nie blokuje
scalenia**.
- To nie regresja: ta sama granica istniala przed PR i w rundzie 1 nie byla zgloszona jako blad; poprawka P5 zawezila
  wyciek (wersje, duplikaty, nazwy w logu i stanie obserwatora), niczego nie poszerzyla.
- Scenariusz wymaga, zeby folder projektu exocad znalazl sie w folderze obserwowanym albo zostal przeciagniety recznie.
  Kroki dnia skanera nie uzywaja projektow exocad, zlecenia w programie skanera maja nazwy TEST1 / TEST2 (instrukcja
  kroku "zlecenie" i "Piec zasad"), a okno po spakowaniu wprost kaze sprawdzic nazwy przed wyslaniem
  (`dzien_skanera.py:789`); granica jest opisana w `dzien_skanera.md`.
- Waga, gdyby do tego doszlo, jest jednak wieksza niz "sama nazwa folderu": pozostale pliki projektu exocad zwykle tez
  maja nazwe projektu w nazwie pliku, a `paczka.json` obok ZIP zawiera pelne nazwy pominietych projektow (D-n4). Zalecam
  tania ochrone w nastepnej paczce okna (ostrzezenie przy pakowaniu z lista folderow zrodlowych projektow, znaczniki w
  `paczka.json`), nie przed scaleniem.

## 4. Higiena (skan diffu `a6cf3a4..58a1a36 -- Ramki/stanowisko`)

- Sciezki kont (`<uzytkownik>`, `Administrator`, `C:\Users`) w dodanych liniach: 0. W raportach wykonawcow tylko katalogi
  roboczy PC (`<PC-katalog>\...`).
- Nazwiska: w nowych testach wylacznie nazwy zmyslone (wykonawca to deklaruje; przejrzalem wszystkie wystapienia - to
  slowa utworzone od "zmyslony" / "wymyslony", nie prawdziwe nazwiska); nazw z puli projektow ani folderow zlecen w diffie
  nie znalazlem; projekty w `c_wspolne.py` tylko jako sha16.
- Nowe pliki (`test_porownaj_bledy.py`, dwa raporty PR13, raport pomiarow): ASCII, LF. Zmienione pliki zachowuja swoje
  dotychczasowe zakonczenia linii (CRLF w `inspect.py`, `porownaj.py`, `test_inspect.py`, `inspect.md`, `match.md`,
  `synth.md` - bez mieszania; reszta LF). Polskie znaki w nowych komentarzach i komunikatach `inspect.py` / `porownaj.py`
  / `dzien_skanera*.py` - zgodnie ze stylem tych plikow (byly tam wczesniej).
- Pliki spoza `Ramki/stanowisko` w zakresie commitow: tylko `Ramki/00_NADZOR_STAN.md` i plan etapu 3 (poza recenzja).
  Plikow binarnych / STL / ZIP: 0.

## 5. Liczniki

- Nowe: B 0, P 1 (P-n1), D 9 (D-n1 ... D-n9).
- Runda 1: B1 i P1-P7 zalatwione (P4 z waska luka D-n2 poza scenariuszami rundy 1, P5 z nowym bledem P-n1 w kodzie
  poprawki); D1, D2, D4-D8, D11 zalatwione; D3, D9 zostaja jako znane; D10 czesciowo (4 z 8, reszta uzasadniona);
  D12 nie.
- Uruchomione: 1 skrypt na PC (3 proby: P-n1, D-n2, D-n6); odczyt 3 logow PC (pelny pytest `58a1a36`, testy nowe na
  `a6cf3a4` z obu galezi poprawek). Skrypt i katalog `<PC-katalog>\app\r13b` zostaja na PC (tymczasowe sesje usuniete).

## 6. Czego NIE sprawdzilem

- Testow nowych na `a6cf3a4` nie uruchamialem sam - "czerwone przed" opieram na logach wykonawcow (`p1\logi\czerwone_a6cf3a4.log`,
  `p2\ds_czerwone.log`) i na czytaniu testow. Skryptu wykonawcy odtwarzajacego P6 na starym kodzie nie powtarzalem.
- Dowodu wykonawcy obliczen "16 z 16 skanow - wszystkie pola rowne" (pkt 4.2 jego raportu) ani porownan niezaleznych
  przebiegow nie odtwarzalem.
- Okna (dnia skanera i `ui_test`) nie uruchamialem na ekranie; zachowanie okna przy bledzie inspekcji (D-n1) i przy
  zamknieciu w trakcie pakowania z jednym bardzo duzym plikiem (czekanie 10 s) - tylko czytaniem / z testow offscreen
  w pelnym pytest.
- D-n2 sprawdzilem tylko dla tej samej liczby czesci; przypadek innej liczby czesci (stare czesci zostaja, nowa czesc
  obok, `--sprawdz` folderu bierze pierwsza paczke o tej samej bazie) - tylko czytaniem.
- Scenariusza P1 na prawdziwym projekcie i P7 z prawdziwym (niepodstawionym) wyjatkiem - nikt nie zna takiego wejscia.
- Narzedzi `metryki_*` z wpisem bledu inspekcji nie uruchamialem (D-n5 z czytania).
- Raportu pomiarow koncowych czesci B, planu etapu 3, pliku stanu i karty dnia skanera nie czytalem.
- Kontroli skanu pisanej przez proces podrzedny w trakcie pakowania (log rosnacy miedzy liczeniem sum a ZIP) - stan sprzed
  PR, nie sprawdzalem.
- Prawdziwych skanow nie bylo (decyzja z 15.11) - wszystko na danych sztucznych.
