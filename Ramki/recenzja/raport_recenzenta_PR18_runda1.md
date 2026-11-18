# Raport recenzenta PR #18 - runda 1

Data: 2026-11-17. Recenzent: swieza subsesja (Fable 5.2), niezalezna od wykonawcy i koordynatora.
Stan recenzowany: HEAD `a1a5c84`, PR #18 "E3-A4: katalog, pule, wspolczynniki" (`e3/a4` -> `e3/fala2-baza`), zakres
`git diff origin/e3/fala2-baza...origin/e3/a4` (10 nowych plikow, +2 397 / -0, wszystko pod `Ramki/stanowisko/`).
Metoda: czytanie w calosci `nazwy.py`, `indeks.py`, `pula.py`, `wspolczynniki.py`, `drzewo_syntetyczne.py`, `pula.md`,
raportu wykonawcy; testy - lista wszystkich, w calosci kryteria 1-6 i kontrakt z `session`; plan etapu 3 (3.3, 3.4,
3.5, 4.1), `baza.md`, `baza.py` (transakcje, blokada, `zdarzenie`), `session.py` (`_projekt`, `_frezowanie`, `doba`).
Uruchomienia na PC (`<PC-katalog>\e3\r18`, kod z `git archive HEAD`, 1 proces python naraz, wolny RAM 16 GB):
(1) `testy\test_nazwy.py`, `test_indeks.py`, `test_pula.py` - 115 passed w 12,8 s; (2) `proba.py` - 36 nazw folderow
przez `nazwy.rozbierz` + ksztalty nazw z `Prace_test` (tylko odczyt, bez wypisywania nazw); (3) `scen.py` - 11
scenariuszy na bazie tymczasowej z fikcyjnymi nazwami (`licz_cechy=False`, pliki-atrapy), oznaczone nizej S1-S22.
Katalog tymczasowy scenariuszy usuniety. Na MSI nie uruchamiano pytest ani obliczen. Pelnego pytest nie uruchamialem.

## 0. Werdykt

**do scalenia po poprawkach** - B 0 / P 4 / D 13.

Nie znalazlem bledu, ktory przy typowej pracy dawalby po cichu zly wspolczynnik dla dobrze wpisanego wiersza CSV:
okna dob 06:00-06:00, pula poranna (dni robocze, weekend, limit 10 dni), "ten sam STL na dwoch krazkach = dwa wpisy",
atomowosc CSV, "raz na krazek", baza zajeta i brak nazw poza czterema tabelami dzialaja tak, jak opisano (czytanie +
uruchomienie). Cztery uwagi P dotycza sytuacji, w ktorych pula jest zla BEZ wyraznego sygnalu: (P1) wzor dat w
`nazwy.py` zjada numer kuwety, (P2) raz zapisane powiazanie wiersza CSV z plikiem nie jest juz poprawiane, (P3)
poprawka wiersza w CSV zostawia stary wiersz w puli, (P4) sprzeczne wspolczynniki jednego krazka przechodza bez
licznika. Kazda to kilka-kilkanascie linii + test. Zadna nie wymaga zmiany schematu.

## 1. Uwagi (B = blokujaca, P = poprawic przed scaleniem, D = drobna / moze zostac jako znana)

Sciezki wzgledem `Ramki/stanowisko/`.

| Nr | Waga | Plik:linia | Scenariusz (wejscie -> zly wynik) | Sprawdzone | Oczekiwane |
|---|---|---|---|---|---|
| P1 | P | `stanowisko/nazwy.py:31, 55` (wzor `_DATA`); `nazwy.py:52-58` (pierwszy kandydat wygrywa) | (a) Wzor daty nie sprawdza zakresow (miesiac, dzien, rok) i dopuszcza 4 cyfry na poczatku, wiec numer kuwety sklejony separatorem `-`, `_` albo `.` z dwiema liczbami jest brany za date i wycinany: "Nazwisko 3263_16_11_2026" -> kuweta **"2026"** (zla, bez ostrzezenia); "Nazwisko 88_16_11_2026" -> "2026"; "Nazwisko 3263-24-25" (kuweta + zeby) i "Nazwisko_3263_24_25" -> **brak kuwety**. (b) Gdy w nazwie sa dwa kandydaty, wygrywa pierwszy i nic tego nie sygnalizuje: "Nazwisko 16.11 3263" -> "16", "Nazwisko 14.30 3263" -> "14", "Nazwisko 2 korony 3263" -> "2", "Nazwisko 46 3263" -> "46", "Nazwisko 3M2 3263" (kolor) -> "3", "2026 Nazwisko 3263" -> "2026", "Nazwisko 3263 #2" -> prywatne "#2". Zla kuweta = praca rano przypisana do zlej kuwety. | Uruchomione (`proba.py`, wszystkie przytoczone wyniki). W probce prawdziwej (15 folderow) kazda nazwa ma dokladnie 1 kandydata i 0 dat - dlatego P, nie B. | (a) Date uznawac tylko przy poprawnych zakresach (rok 19xx / 20xx albo 2 cyfry, miesiac 1-12, dzien 1-31) i nie zaczynac jej od liczby, ktora sama jest jedynym kandydatem na kuwete; (b) `Zlecenie` z polem "ilu kandydatow" + licznik w `RaportIndeksu` i w `pula_poranna().liczniki` ("kuweta niepewna"), zeby ekran mogl to pokazac; testy na powyzsze nazwy. |
| P2 | P | `stanowisko/wspolczynniki.py:242-246, 276-277`; `stanowisko/pula.py:152` | Powiazanie `frezowania.projekt_id` zapisane przy pierwszym wczytaniu CSV ma pierwszenstwo tak dlugo, jak tamten projekt nie jest usuniety - a foldery starsze niz 10 dni nigdy nie sa oznaczane jako usuniete. Wiersz CSV z sama nazwa pliku wczytany, zanim wlasciwy plik trafil do indeksu (opoznienie OneDrive, wiersz wpisany przed eksportem), wiaze sie z plikiem o tej samej nazwie w starszym folderze i zostaje z nim na stale: pula podaje STARY projekt ze wspolczynnikiem nowego frezowania, wlasciwego projektu w puli nie ma. Ta sama sytuacja na swiezej bazie daje dobry wynik - pula zalezy od kolejnosci zdarzen. | Uruchomione (S1): po pojawieniu sie nowego folderu `odswiez` zwraca `niejednoznaczne = 1`, `powiazanie.powiazane = 0`, pula wskazuje folder stary; swieza baza - folder nowy. | Przy `kandydatow > 1` (albo zawsze dla wierszy z okna puli) przeliczac wybor i poprawiac zapisane powiazanie, gdy wygrywa inny plik; test na S1. |
| P3 | P | `stanowisko/wspolczynniki.py:233-258` (klucz plik + krazek + data; wiersze nieobecne w pliku zostaja); `pula.py:82-88` | Operator poprawia w CSV literowke w krazku, dacie albo nazwie pliku (zmienia sie klucz): stary wiersz zostaje w bazie i przez 2 doby w puli. Przyklad: `a.stl;K-1;1,2500` poprawione na `a.stl;K-2;1,2000` -> pula ma OBA wpisy (1,25 i 1,20), a `Pula.wspolczynniki()` (uzywane do czasu A5) zwraca dla tego projektu NIC - praca wypada z puli; po A5 w puli zostaje kandydat w zlej skali. Poprawka nazwy pliku (pomylka a / b) zostawia w puli projekt, ktorego nie frezowano, ze wspolczynnikiem. Poprawic sie tego z okna programu nie da (wiersz CSV nie ma "usun"). | Uruchomione (S3): 2 wpisy po poprawce krazka, `wspolczynniki() == {}`, 3 wpisy po poprawce nazwy. Test `testy/test_pula.py:299-300` utrwala to zachowanie jako zamierzone. | Wiersze `zrodlo = csv` z tego samego `raport_plik` i z dat WYSTEPUJACYCH w biezacym pliku (albo z okna puli), ktorych w pliku juz nie ma - usuwac albo wylaczac z puli; dni, ktorych plik nie zawiera, zostaja (plik czyszczony codziennie nadal dziala). Patrz pytanie 6. |
| P4 | P | `stanowisko/pula.py:159-162` (kolejnosc zrodel), `pula.py:116-122` (`_reczne`), `pula.py:228-236` (`krazki`) | Krazek ma fizycznie jeden wspolczynnik, a program przyjmuje sprzecznosci bez licznika: (a) dwa wiersze CSV tego samego krazka z roznymi wartosciami (literowka 1,2210 / 1,2120) - kazda praca dostaje swoja; (b) wiersz CSV 1,2210 i wpis reczny tego krazka 1,2500 - po cichu wygrywa CSV; (c) wpis reczny krazka z dowolnie dawnej daty (probka: sprzed 2,5 miesiaca) obowiazuje bez pytania i `brakuje = False` - jesli oznaczenia krazkow sie powtarzaja (numer partii, numeracja od nowa), nowy krazek dostaje stary wspolczynnik. Skutek kazdego: dopasowanie czesci prac w zlej skali. | Uruchomione (S7): `krazki()` pokazuje `wspolczynniki_csv = [1.212, 1.221]`, `wspolczynnik_reczny = 1.25`, `brakuje = False`; liczniki puli puste. | Licznik + lista w `pula_wieczorna().liczniki` (np. `krazki_sprzeczne`) i pole w `krazki()`; dla wpisu recznego starszego niz N dni (np. `usun_z_puli_po_dniach`) `brakuje = True` albo pole "do potwierdzenia". Czy oznaczenia krazkow sa niepowtarzalne - pytanie do wlasciciela (pkt 3, pytanie 8). |
| D1 | D | `stanowisko/pula.py:105-113` | Okno wieczorne liczy doby kalendarza, nie dni robocze: w poniedzialek o 20:00 okno to 15.11 06:00 - 17.11 06:00, frezowania z piatku sa poza pula (wszystkie prace z piatku = "bez projektu"). Zgodne z planem (K4 "dzis i wczoraj"), ale inaczej niz pula poranna. | Uruchomione (S9): pt 20:00 i sob 10:00 - 1 wpis; nd 20:00, pon 07:00, pon 20:00 - 0. | Decyzja wlasciciela (pytanie 7); technicznie wystarczy `pula_wieczor_dni` w dniach roboczych albo wartosc 4. |
| D2 | D | `stanowisko/indeks.py:181-190, 208-213, 202-204` | Katalog zrodla istnieje, ale jest pusty (OneDrive wylogowany / w trakcie pierwszej synchronizacji): wszystkie zlecenia i projekty dostaja `usuniety = 1`. Po powrocie folderow swieze wracaja, a foldery starsze niz 10 dni NIE (sa pomijane przed zapisem) - ich pliki znikaja z `IndeksPlikow` na stale. Ochrona "brak katalogu = bez usuniec" nie obejmuje tego przypadku. | Uruchomione (S4): `zlecenia_usuniete = 2`; po powrocie stary folder nadal `usuniety = 1`, wiersz CSV jego pliku = `brakujace`. | Zrodlo z 0 folderow przy > 0 aktywnych zleceniach w bazie traktowac jak "brak katalogu" (stan "puste - pominiete"); folder stary z `usuniety = 1`, ktory jest na dysku - przywracac. |
| D3 | D | `stanowisko/indeks.py:202-204` | Na swiezej bazie (pierwsze uruchomienie, baza zalozona od nowa, program nieuruchamiany > 10 dni) folder niezmieniany od > 10 dni nie trafia do indeksu; frezowanie pliku z takiego folderu (dofrezowanie starej pracy) = `brakujace`. Licznik jest, wiec nie po cichu. | Uruchomione (S5: `pominiete_stare = 1`, `brakujace`). | Znana granica do opisu; ewentualnie: plik z wiersza CSV z okna puli szukany tez w folderach pominietych. |
| D4 | D | `stanowisko/indeks.py:314-324` (`kandydaci`) | Wiersz CSV ze sciezka, ktorej folder nie jest folderem zlecenia (`C:\MillBox\Jobs\a.stl`) = brak kandydatow, choc plik o tej nazwie jest w indeksie jeden. Sciezka konczaca sie `Cyrkon\<folder>\<plik>` dziala, wielkosc liter i `\` / `/` tez. | Uruchomione (S5). | Gdy sciezka nie pasuje, a sama nazwa daje dokladnie 1 plik - przyjac z licznikiem; albo zostawic i opisac w instrukcji CSV. Do sprawdzenia, jak nazywa pliki MillBox (plan 12.1 poz. 18). |
| D5 | D | `stanowisko/indeks.py:283-284` (nadpisanie `sha16`), `indeks.py:208-213, 268-270` (nowe zlecenie po zmianie nazwy) | (a) Plik zmieniony po frezowaniu (ta sama nazwa, inna tresc): wiersz frezowania wskazuje nowa tresc, starej `sha16` nie ma juz w `projekty` - praca wyfrezowana ze starego pliku jest porownywana z nowym projektem, a `session._projekt(stary sha16)` nic nie znajdzie. (b) Zmiana nazwy folderu = nowe `projekt_id`; pula i powiazanie frezowan to obsluguja, ale `stan_punktow` (lista "do dofrezowania") zostaje przy starym id. | Uruchomione (S18): po zmianie tresci pula ma tylko nowy skrot; po zmianie nazwy `projekt_id` 1 -> 2. | Opisac jako znana granice w `pula.md`; (b) do rozstrzygniecia w A6 (np. przeniesienie wierszy po `sha16`, gdy folder znika, a pojawia sie nowy z tymi samymi plikami). |
| D6 | D | `opisy_modulow/pula.md:20-22` (kontrakt, pkt 3); poza PR: `stanowisko/session.py:387-392` | Kontrakt przekazuje do `session` tylko `sha16` i `frezowanie_id`; `Wpis.projekt_id` nie ma drogi do `prace.projekt_id`. Ten sam plik w dwoch folderach (S18: "Cyrkon" + "Prywatne", takze kopia w archiwum, ktore nigdy nie jest oznaczane jako usuniete) -> `session._projekt` zwraca brak przypisania, choc pula zna projekt. Klucz kandydata (`sha16`, wspolczynnik) nie rozroznia tez dwoch krazkow o tym samym wspolczynniku ani dwoch zlecen z tym samym plikiem w puli porannej (rozne kuwety). | Czytaniem + S18 (2 wpisy poranne z tym samym `sha16`, kuwety rozne). | W A5: kandydat niesie tez `projekt_id` (i `session` go uzywa), klucz wpisu = `frezowanie_id` albo `projekt_id`; dopisac do `pula.md`, co robi silnik przy takich parach. |
| D7 | D | `stanowisko/wspolczynniki.py:165-178, 122-133, 34-35` | Parser CSV - rzeczy glosne, ale typowe dla Excela: srednik na koncu wiersza albo naglowka (5. kolumna) = caly plik odrzucony; pusta linia przed naglowkiem = "brak naglowka"; data `17.11.26` i `2026/11/17` odrzucone. Rzecz cicha: data nie jest sprawdzana z kalendarzem - `2025-11-17` albo `2027-11-17` (literowka roku) przechodzi, wiersz liczy sie jako "nowy" i nigdy nie trafia do puli. Zakres 1,0-1,6 jest szeroki (1,0 przechodzi; literowka 1,125 zamiast 1,225 tez), a w `ustawienia.przyklad.toml` jest juz `wspolczynnik_min = 1.20` / `max = 1.25` w `[synth]`. | Uruchomione (S10, 21 wariantow). UTF-8 z BOM, cp1250, cudzyslowy, naglowek wielkimi literami, przecinek / kropka, duplikaty, atomowosc (zly plik po dobrym: w bazie bez zmian), ponowne wczytanie (takze wiersz bez krazka): poprawne. | Puste pola na koncu wiersza ignorowac; data pozniejsza niz jutro albo starsza niz np. 30 dni = blad linii albo licznik "poza oknem" w `RaportCsv`; zakres z ustawien (wykonawca zglasza to w "POTRZEBUJE"). |
| D8 | D | `stanowisko/wspolczynniki.py:334-349` | `wpisz_reczny(..., data=<dzien wczesniejszy niz ostatni wpis>, zmien=True)`: powstaje wiersz, funkcja zwraca jego id i zapisuje zdarzenie ze zmiana, ale obowiazuje nadal wpis z pozniejsza data (kolejnosc `data DESC`). | Uruchomione (S11): wpis 1,26 z data 10.11 nie obowiazuje, obowiazuje 1,24 z 18.11. Pozostale reguly "raz na krazek" (ta sama wartosc, inna bez / ze `zmien`, ten sam dzien = poprawka, inny = nowy wiersz) - poprawne. | Odmowa, gdy `data` < data obowiazujacego wpisu, albo kolejnosc po `wczytano`. |
| D9 | D | `stanowisko/indeks.py:326-335` | Kilka plikow o tej samej nazwie: wygrywa plik o dacie modyfikacji najblizszej dacie frezowania liczonej w obie strony - plik zapisany PO frezowaniu moze wygrac z plikiem sprzed frezowania. Do puli trafia tylko wybrany (licznik `niejednoznaczne`). | Czytaniem. | Preferowac pliki nie pozniejsze niz data frezowania + 1 dzien; rozwazyc wstawienie do puli wszystkich kandydatow (dopasowanie rozstrzygnie ksztaltem). |
| D10 | D | `stanowisko/nazwy.py:75-80, 66` | `numer_zeba`: fragment daty jest brany za zab ("Nazwisko 16.11 zab 46.stl" -> "16", "korona 11.11.2026 zab 36.stl" -> "11") - dotyczy tylko nazw spoza wzoru exocad (w probce prawdziwej 17 / 17 to nazwy exocad). `znormalizuj` zdejmuje zera takze z numeru prywatnego ("#0123" -> "#123"), a `kuweta` je zostawia - niespojnosc do rozstrzygniecia przy Excelu (A9). | Uruchomione (`proba.py`). | Wyciac daty przed szukaniem zeba (ten sam wzor co po poprawce P1). |
| D11 | D | `stanowisko/indeks.py:197-204, 144-148` | Kazdy przebieg listuje WSZYSTKIE foldery zrodla, takze archiwalne (z przejsciem po podfolderach), zanim sprawdzi wiek - opis "nie jest czytany" jest niescisly (nie sa czytane pliki). Zapytan SQL w petli po starych folderach nie ma; po biezacych 1 zapytanie na folder (uzywa unikatu). | Uruchomione (S22, dysk lokalny PC, pliki-atrapy, bez cech): 600 folderow biezacych + 3 000 archiwalnych - 1. przebieg 3,3 s, kolejne 0,2 s; CSV 302 wiersze 0,12 s; pula wieczorna 0,11 s. Prawdziwy "Cyrkon" na OneDrive niezmierzony. | Zmierzyc na prawdziwym folderze przed A3 (odswiezenie "po nowym pliku"). |
| D12 | D | `testy/test_pula.py`, `testy/test_nazwy.py` | Luki testow: brak testu S1 (powiazanie po pojawieniu sie drugiego pliku), sprzecznych wspolczynnikow krazka, numeru kuwety sklejonego z data / zebami, dwoch kandydatow na kuwete z ostrzezeniem, pustego katalogu zrodla, poniedzialku w puli wieczornej, daty spoza kalendarza w CSV. Istniejace testy kryteriow 1-6 sprawdzaja wynik niezaleznie od kodu (oczekiwania policzone recznie albo z budowy drzewa), tautologii nie znalazlem. | Czytaniem + uruchomienie (115 passed). | Dopisac razem z poprawkami P1-P4. |
| D13 | D | `stanowisko/wspolczynniki.py:181, 188-190`; `pula.py:167, 172` | Pole `krazek` to dowolny tekst z CSV; trafia do wynikow pul (`krazki_bez_wspolczynnika`, `krazki()`) i przy wpisie recznym do dziennika. Gdyby w kolumnie krazka znalazlo sie nazwisko (przesuniete kolumny bez `.stl`), wyjdzie poza cztery tabele. Kontrola jest tylko na koncowke `.STL`. | Czytaniem. | Ograniczyc znaki / dlugosc oznaczenia krazka (np. litery, cyfry, `-`, `/`, do 20 znakow) - inne = blad linii. |

## 2. Co sprawdzilem i nie budzi zastrzezen

- Doba robocza: `wspolczynniki.doba_robocza` = `session.Sesja.doba` (ta sama formula; test parametryczny). Okno wieczorne
  dla `dni = 2`: daty D-1, D, D+1 - o 20:00 17.11 i o 03:00 18.11 daty 16-18.11, o 08:00 18.11 daty 17-19.11 (czytanie +
  testy). Granica 06:00 nie wypada w godzinie zmiany czasu; porownania z czasem plikow ida przez czas lokalny systemu.
  Przelom miesiaca i roku: sama arytmetyka dat, bez tabel.
- Pula poranna: tabela 10 dat w tescie policzona recznie i zgodna z kodem; sobota / niedziela, 05:30 = doba poprzednia,
  limit 10 dni, zlecenia usuniete poza pula, wspolczynnik 1,0 (czytanie + test). Folder bez kuwety zostaje w puli z licznikiem.
- Ten sam STL w dwoch frezowaniach z roznymi wspolczynnikami = 2 wpisy z roznymi `frezowanie_id` (test + S5).
- Plik usuniety i przywrocony, folder usuniety i przywrocony, zmiana nazwy folderu (frezowanie wiazane ponownie po
  nazwie), plik zablokowany / uszkodzony (ponowna proba), wielkosc liter rozszerzenia - poprawne (testy + S18).
- Laczenie CSV z indeksem: bez wielkosci liter, NFC po obu stronach (nazwa NFD z OneDrive pasuje), `\` i `/`,
  spacje na koncach; rozszerzenie `.stl` wymagane po stronie CSV (inaczej blad linii).
- Transakcje: CSV w jednej transakcji po pelnym sprawdzeniu pliku; folder indeksu w jednej krotkiej transakcji, cechy
  liczone przed nia; `BEGIN IMMEDIATE` + `busy_timeout`. Baza zajeta przez inne polaczenie (S12): `odswiez` i
  `wpisz_wspolczynnik` koncza sie `BladBazy` z komunikatem dla czlowieka, odczyt puli dziala, po zwolnieniu wszystko
  przechodzi. Unikat `frezowania` z NULL: modul pilnuje sam (wiersz bez krazka wczytany 2 razy = 1 wiersz; wpis reczny
  sprawdzany przed dopisaniem). Uzycie `baza.wstaw` / `zdarzenie` / `sciezka_z_ustawien` zgodne z `baza.md`; schemat bez zmian.
- Dane osobowe: w `zdarzenia` same liczby, id i krazki; wyjatki CSV podaja numery linii bez tresci pol i bez sciezki;
  bledy odczytu folderow i plikow zamieniane na liczniki; wyniki `pula_*`, `krazki`, `odswiez` bez nazw; nazwy zwraca
  tylko `sciezki_plikow` (opisane) i wewnetrzny `IndeksPlikow`. `drzewo_syntetyczne.py` wypisuje tylko liczby. Dane
  testowe, narzedzie i raport: nazwy fikcyjne (Testowski, Probna, Fikcyjny, Zmyslona, Atrapowicz, Wzorcowy...).
- Higiena: 10 plikow, wszystkie nowe (status A), 0 zmian w istniejacych; ASCII i LF w kazdym (`git ls-files --eol`,
  zliczenie znakow spoza ASCII = 0); nowych bibliotek brak (numpy, trimesh, pillow sa w `requirements.txt`).
- Liczby z raportu wykonawcy, ktore dalo sie sprawdzic: 41 + 18 + 56 = 115 testow, 115 passed; `Prace_test`: 15 folderow,
  15 z kuweta (13 czterocyfrowych, 2 trzycyfrowe), w kazdym dokladnie 1 kandydat na kuwete i 0 dat; 17 plikow STL, wszystkie
  bezposrednio w folderze zlecenia, nazwy w ksztalcie exocad (`RRRR-MM-DD_..._cad.stl`). Ksztalty folderow: "L N4 L" (5),
  "L N4L" (2), "L L. N4 L", "L N3 L", "L N4 L L", "L-L N4 L" i podobne - mieszcza sie w 10 wzorach narzedzia.

## 3. Pytania wykonawcy do wlasciciela - rekomendacje

1. **Zera wiodace ("0412" -> "412").** Rekomendacja: tak, bez zer - zgodnie z planem wdrozenia i z tym, jak czlowiek
   czyta numer. Ryzyko: gdyby na kuwetach albo w Excelu "041" i "41" oznaczaly co innego, program ich nie rozrozni
   (w probce prawdziwej nie ma numeru z zerem na poczatku - warto zapytac technika).
2. **STL w podfolderach pomijane.** Rekomendacja: tak, ale liczbe pominietych pokazac na ekranie przy "Odswiez pule".
   Ryzyko: jesli ktos trzyma wlasciwy projekt w podfolderze (np. "poprawka"), praca wyjdzie jako "bez projektu";
   licznik pozwoli to zauwazyc w pierwszym tygodniu. W probce 17 / 17 plikow lezy bezposrednio w folderze.
3. **Swieto liczone jak dzien roboczy.** Rekomendacja: wystarczy, bez kalendarza swiat. Ryzyko: po swiecie pula poranna
   siega o dzien krocej - praca starsza wyjdzie jako "nieznana"; w tygodniu ze swietem mozna podniesc
   `pula_rano_dni_roboczych` z 4 na 5 (albo ustawic 5 na stale - pula wieksza o ok. jedna czwarta).
4. **"Prywatne" z ta sama regula dat.** Rekomendacja: dla "Prywatne" brac wszystko z ostatnich 10 dni
   (`usun_z_puli_po_dniach`), nie 4 dni robocze - plan (K3) mowi "plus Prywatne", a tych zlecen jest malo. Ryzyko wyboru
   domyslnego: zlecenie prywatne, ktore czekalo dluzej niz 4 dni robocze, rano wyjdzie jako "nieznane".
5. **Kto wpisal wspolczynnik reczny.** Rekomendacja: bez zmiany schematu; nazwe operatora (program zna ja z sesji)
   dopisac do wpisu w dzienniku `zdarzenia` jako opcjonalny parametr `wpisz_reczny`. Ryzyko wyboru domyslnego: przy zlym
   wspolczynniku krazka nie da sie ustalic, kto i na ktorej zmianie go wpisal - zostaje tylko data i godzina.
6. **Wiersz skasowany z CSV zostaje w bazie.** Rekomendacja: zmienic (uwaga P3) - dla dni, ktore sa w biezacym pliku,
   plik jest zrodlem prawdy: wiersz z tych dni, ktorego juz w pliku nie ma, wypada z puli; dni, ktorych plik nie zawiera
   (plik wyczyszczony rano), zostaja. Ryzyko wyboru domyslnego: kazda poprawka literowki w krazku, dacie albo nazwie
   pliku zostawia w puli na 2 doby stary, bledny wiersz - dzis praca wypada wtedy z puli, po paczce A5 moze zostac
   dopasowana w zlej skali.

Dodatkowe pytania recenzenta:

7. **Wieczor po weekendzie (D1).** Czy w poniedzialek wieczorem skanuje sie prace frezowane w piatek? Jesli tak, okno
   wieczorne powinno liczyc dni robocze (jak poranne) albo `pula_wieczor_dni` trzeba podniesc do 4.
8. **Oznaczenia krazkow (P4).** Czy oznaczenie krazka jest niepowtarzalne (numer seryjny), czy moze sie powtorzyc
   (numer partii, numeracja od 1)? Od tego zalezy, czy wpis reczny moze obowiazywac bezterminowo.

## 4. Czego NIE sprawdzilem

- Pelnego pytest (795 / 8 / 0 wg wykonawcy) - uruchomilem tylko 3 pliki testow paczki (115 passed).
- Prawdziwego folderu "Cyrkon" na OneDrive (setki folderow, pliki "tylko w chmurze", czas listowania) i prawdziwego
  pliku CSV z Excela przy frezarce; nazw plikow nadawanych przez MillBox.
- Cech i miniatur na prawdziwych STL (sprawdzone tylko testami paczki na atrapach); wygladu miniatury.
- Zmiany czasu (tylko czytanie), pracy dwoch polaczen w jednym procesie okna (watek roboczy + `session`) pod obciazeniem.
- Modulow `baza.py`, `session.py`, `katalog.py`, `synth.py` jako takich (poza zgodnoscia uzycia); podpiecia do
  aplikacji (A3) i `match` (A5) - nie istnieja; zachowania silnika przy dwoch wpisach tego samego `sha16`.
- Nazw folderow z lone-surrogate / znakami niedozwolonymi w UTF-8 (wyjatek SQLite przy zapisie) - nie probowalem.
