# Dzien testu 28.11.2026 - laptop i skaner (program 0.3.9-rc2)

Dla wlasciciela, do wydruku razem z arkuszem `ARKUSZ_LAPTOP_I_SKANER.md` (numery A1-D2 sa te same). Na ten dzien
zastepuje dokument `PIERWSZE_TESTY_NA_SPRZECIE.md` (stary dokument); numery w nawiasach, np. (2.3), to kroki tamtego dokumentu.

- W cudzyslowie "..." stoja napisy naszego programu, slowo w slowo (na ekranie sa z polskimi literami). Kursywa to
  napisy Windows albo programu skanera. Kazdy napis sprawdzono 26.11 na instalacji z paczki `Stanowisko_0.3.9-rc2.zip`.
- **[NIE SPRAWDZONE BEZ SPRZETU]** - tego nikt nie widzial na laptopie ani na skanerze. Moze pojsc inaczej.
- Zasady: w programie skanera niczego nie kasuj; krok nie wychodzi 15 minut - zdjecie ekranu telefonem, notatka,
  dalej; co poszlo inaczej niz tu, zapisz w arkuszu - to wynik, nie porazka.

## A. Dzien wczesniej (ok. 15 minut + instalacja)

**A1. Dwa foldery na laptopie.** Zaloz pusty `C:\Skany_test` (tu program skanera bedzie zapisywal skany) i
`C:\Projekty_STL` (skopiuj tu pliki STL z exocad prac, ktore jutro zeskanujesz - wszystkie w tym jednym folderze).
Nazwa folderu projektow bez cyfr: program czyta liczbe z nazwy folderu jako numer kuwety. Plik z nazwiskiem pacjenta
w nazwie: zmien nazwisko na TEST1, TEST2... (koncowke, np. `-11-crown_cad.stl`, zostaw - program czyta z niej zab i typ).

**A2. Pendrive:** rozpakowana paczka (folder z plikiem `Instaluj.cmd`) i folder `testy_sprzet_2026-11-28`.
Skopiuj ten drugi na laptop jako `C:\Sprzet_testy` (narzedzie `pole_skanu.cmd` do krokow 2.4 i 2.5a).

**A3. Instalacja.** Dwuklik `Instaluj.cmd` na pendrivie. Mignie czarne okno, otworzy sie okno "Stanowisko - instalacja";
po lewej 4 kroki: "Foldery", "Osoby", "Instalacja", "Gotowe". Na dole stale: "Bez internetu. Niczego nie zmienia poza
folderem instalacji i ikonami na pulpicie."

| Krok okna | Co kliknac | Co ma byc widac | Gdy jest inaczej |
|---|---|---|---|
| 1 "Wskaz foldery" | "Folder ze skanami" -> "Wybierz..." -> `C:\Skany_test`; "Folder z projektami" -> "Wybierz..." -> `C:\Projekty_STL`; "Miejsce instalacji" zostaw `C:\Stanowisko`; "Dalej" | pod miejscem: "Potrzeba 1,9 GB wolnego miejsca. Jest ... GB." | czerwony napis, np. "Folder ze skanami nie istnieje: ..." - zrob, co mowi (folder zalozysz tez w okienku "Wybierz...") |
| 2 "Kto bedzie pracowal na stanowisku?" | w pole "Imie i nazwisko albo inicjaly" wpisz `Tester`, "Dodaj", potem "Instaluj" | `Tester` na liscie | "Dodaj co najmniej jedna osobe." - wpisz i "Dodaj" |
| 3 "Instalacja" | nic - czekaj (na PC trwalo 1 minute; z pendrive'a i z antywirusem dluzej) | "Trwa instalacja - kilka minut. Nie zamykaj tego okna."; 9 wierszy dostaje kolejno "gotowe"; najdluzej "5. Program i pakiety (kilka minut)" z rosnacym czasem "trwa..." | "Instalacja sie nie udala" i "Co zrobic: ..." - zdjecie ekranu, zrob to i "Sprobuj ponownie"; "Szczegoly" pokazuje caly zapis |
| 4 "Gotowe" | "Uruchom program" | "Program 'Stanowisko' 0.3.9-rc2 jest zainstalowany w C:\Stanowisko."; "Na pulpicie sa ikony: 'Stanowisko', 'Dzien skanera'."; "Ramki sa wylaczone - program dziala bez nich (rozkladanie wedlug podpisow na ekranie)." | brak ikon: okno podaje plik do klikniecia w `C:\Stanowisko` (`Stanowisko.cmd` albo `Dzien_skanera.cmd`) |

**A4. Pierwszy start.** Program otwiera sie w trybie "Wieczor". Po prawej "Kto teraz pracuje?" - kliknij `Tester`.
Na dolnym pasku: "Folder skanera:" "dostepny", "Folder projektow:" "plikow projektow: ..." (liczba Twoich
plikow STL), "Ramki:" "wylaczone", "wersja 0.3.9-rc2". Po lewej "Jeszcze nie ma skanow.". Zamknij program krzyzykiem.
Gdy liczba plikow to 0 albo "Folder skanera:" nie mowi "dostepny": zdjecie paska, w arkuszu A4. [NIE SPRAWDZONE BEZ SPRZETU: wyglad
na ekranie laptopa]

**A5. Ikona "Dzien skanera".** Okno "Dzien skanera - krok po kroku (sesja ...)"; na gorze "Obserwuje:" i
`C:\Skany_test`; po lewej 14 krokow, pierwszy "1. Zanim zaczniesz". Zamknij okno (to tylko proba).

**A6. Gdy Windows albo program ochronny przeszkadza** [NIE SPRAWDZONE BEZ SPRZETU]:

- Windows pyta *Czy chcesz uruchomic ten plik?* - *Uruchom*. Niebieskie *System Windows ochronil ten komputer* -
  *Wiecej informacji* -> *Uruchom mimo to*. Windows nie pozwala uruchomic z pendrive'a - skopiuj rozpakowany folder na
  `C:\` i dwuklik `Instaluj.cmd` tam.
- Program ochronny (antywirus) zamknal program, ikona nie dziala albo brakuje plikow w `C:\Stanowisko` (na PC probnym
  Bitdefender tak zrobil): (1) uruchom `C:\Stanowisko\Stanowisko.cmd` (otwiera tez male czarne okno - nie zamykaj go);
  (2) w programie ochronnym przywroc pliki z kwarantanny i dodaj wyjatek na `C:\Stanowisko` (Bitdefender: *Ochrona* ->
  *Advanced Threat Defense* -> *Ustawienia* -> *Wyjatki*; na laptopie firmowym moze to wymagac administratora);
  (3) dalej brakuje plikow - jeszcze raz `Instaluj.cmd` w to samo miejsce (ustawienia i dane zostaja).
  Dlatego instalacja i pierwszy start dzien wczesniej, nie przy szefie.

## B. W sobote - kolejnosc dnia

Plytka glowna: **okragla testowa R54 nr 8** (pomaranczowa). Kwadratowe - gdy sa. W programie skanera ustaw folder
zapisu skanow `C:\Skany_test` [NIE SPRAWDZONE BEZ SPRZETU]. Na kartce zapisuj: ktore gniazdo, jaki ubytek, co pokazal ekran.

**B1 (2.1-2.2). Okno "Dzien skanera"** (ikona, 5 + 15 minut). Pytanie "Znaleziono niedokonczona sesje z ..." "Wznowic ja?"
(zostala po A5) - *No* / *Nie*, czyli nowa sesja. Na gorze "Obserwuje:" i `C:\Skany_test`. Kroki 1-4 okna ("Zanim
zaczniesz" ... "Zlecenie testowe i ekran skanowania - zrzuty"): rob, co mowi okno, potem "Krok zrobiony - dalej".
Nie wychodzi: "Nie udalo sie / pomijam, bo..." i jedno zdanie. Najwazniejsze do arkusza: format pliku i czy jest JEDEN
plik na cala plytke.

**B2 (2.3). Pierwszy skan: pusta plytka nr 8** (krok okna "5. Skan 1: pusta plytka"). Linia ciecia powyzej stolika
i co najmniej 3 mm ponizej wierzchu plytki; zapis jako STL calej plytki, bez wygladzania; czas stoperem.
Dobrze: plik sam pojawia sie w oknie, po kilkunastu sekundach zielona ocena ("skan dobry"). Czerwone "TEN SKAN SIE NIE NADA,
bo ... ZROB TAK: ..." - zrob to, co po "ZROB TAK". Wokol plytki w podgladzie widac plaski stolik = SKAN Z PODLOZEM:
podnies ciecie nad stolik (szczegoly: stary dokument, krok 2.3). Pole skanera kartonem (2.4) - tylko gdy jest czas.
[NIE SPRAWDZONE BEZ SPRZETU: prawdziwy plik skanera; stolik w skanie]

**B3 (2.5). Skany wedlug okna** (ok. 1 godziny), kazdy w swoim kroku okna, wszystko na plytce nr 8:
"6. Skan 2: plytka z pracami calymi" (6-10 prac z projektami z `C:\Projekty_STL`), "7. Skan 3: TO SAMO drugi raz, bez
ruszania plytki", "9. Skan 4: plytka z 2-3 pracami celowo ukruszonymi" (gniazdo i miejsce na kartke), "10. Skan 5: praca
potracona w trakcie skanu", "11. Skan 6: praca bokiem i praca czesciowo zaslonieta", "12. Skan 7: druga plytka
(poranna albo okragla), jesli jest" (kwadratowa). Kazdy skan ma w oknie ocene; ocena i notatka do arkusza B3. Trzy skany
plytki nr 8 na ksztalt (2.5a) - tylko gdy zostanie czas. Potem zamknij okno "Dzien skanera" (sesja zostaje).

**B4 (2.7 i proba f). Program "Stanowisko" na prawdziwych skanach** (30 minut). W `C:\Skany_test` leza juz skany z B2-B3.
Ikona "Stanowisko", osoba `Tester`. Program sam bierze kazdy skan, ktorego jeszcze nie liczyl - takze te sprzed
startu (proba f): po lewej kafelek na kazdy skan, na pasku "Analiza:"; wsrod komunikatow "Program wznowil prace" -
"Po ponownym uruchomieniu program dokancza zalegle skany: ..." (komunikaty sa pokazywane po jednym; nastepny pokazuje
przycisk "i jeszcze ..."). Pytania, czy przeliczyc stare skany, w tej wersji jeszcze nie ma - zapisz, ile minut liczyl.
Potem nowa plytka nr 8 z pracami: zapisz skan i wlacz stoper. Dobrze: po lewej kafelek "Plytka 8", w srodku mapa
(zatrzymaj stoper). Nie odczytal numeru: pytanie "Podaj numer plytki" - kliknij 8. Kolory prac porownaj z kartka:
"OK" zielone, "UBYTEK" czerwone, "sprawdz" zolte, "bez projektu" szare (brak STL tej pracy w folderze projektow).
[NIE SPRAWDZONE BEZ SPRZETU: czas analizy prawdziwego skanu; odczyt numeru plytki nr 8; czy kolory sie zgadzaja]

| Widzisz | Zrob |
|---|---|
| "Analiza skanu nie powiodla sie" | przepisz tekst w nawiasie, np. "w skanie widac 0 z 3 znacznikow plytki ..." (przy 0 z 3 najpierw sprawdz stolik w skanie, B2) |
| "Plytka nie pasuje do ukladu" | zdjecie, arkusz; plytke ustaw na srodku pola |
| "Ponowny skan tej samej plytki?" | to ta sama plytka bez zmian: "Tak, to ponowny skan"; inne prace: "Nie, to nowy wsad" |
| "Nowy wynik czeka: ..." | ekran zostal na poprzedniej plytce - kliknij "Pokaz nowy wynik" |
| "Ten sam projekt w dwoch gniazdach" | dwie prace z jednego pliku STL - to nie blad; "Zamknij" |
| nic sie nie dzieje | plik nie konczy sie na `.stl` albo trafil do innego folderu niz `C:\Skany_test` |

**B5. Proby z analizy kodu** (po 5-10 minut, program "Stanowisko" otwarty; kazda proba = nowy skan; wynik do arkusza B5):

- a) 2-3 prace z odpryskiem brzegu roznej wielkosci, w tym jeden bardzo maly - ktore sa "UBYTEK", a ktore "OK"?
- b) ta sama praca z ubytkiem drugi raz, ubytkiem w dol albo w cien; na pytanie "Ponowny skan tej samej plytki?" -
  "Tak, to ponowny skan". Czy zostaje "UBYTEK"?
- c) 2-3 mm brzegu calej pracy zaklejone tasma albo plastelina - czy praca jest "nie sprawdzono" (a nie "OK")?
- d) praca bokiem albo do gory nogami - czy NIE jest zielona "OK"?
- e) dwie plytki kwadratowe jedna po drugiej; przy pierwszej na pytanie "Podaj numer plytki" kliknij "Pozniej".
  Czy przy drugiej panel i kafelki dalej mowia o wlasciwym skanie ("Plytka bez numeru" z godzina skanu)?
- f) zrobiona w B4.

**B6 (2.6). "Zakoncz i spakuj"** (10 minut). Ikona "Dzien skanera"; "Wznowic ja?" - *Yes* / *Tak* (ta sama sesja).
Krok "14. Na koniec: kopia CALEGO folderu zlecen programu skanera": w programie skanera nie ma zlecen pacjentow, wiec
kliknij "Skopiuj caly folder zlecen skanera", potem "Krok zrobiony - dalej". Potem "Zakoncz i spakuj"; pytanie
"Brakuje wymaganych krokow" ... "Spakowac teraz?" - *Yes* / *Tak* (sam Enter znaczy NIE). Dobrze: "Sesja spakowana: ...
plikow" i plik ZIP w `C:\Stanowisko\dane\dzien_skanera\<data_godzina>\paczka\` ("Otworz folder sesji" go pokaze).
Nie wychodzi: niczego nie kasuj, skopiuj caly folder sesji z data i godzina na pendrive.
[NIE SPRAWDZONE BEZ SPRZETU: napisy przyciskow Yes / No; czas pakowania prawdziwych skanow]

## C. Co pokazac szefowi (10 minut, program "Stanowisko" z prawdziwym skanem plytki nr 8)

1. **Okno wieczorne:** kafelek "Plytka 8" po lewej, mapa plytki z kolorami prac, obok "Na tej plytce" - ile prac w
   jakim kolorze. To jest skan z naszego skanera, nie dane sztuczne.
2. **Praca czerwona i decyzja:** kliknij czerwone gniazdo - po prawej "Plytka 8 - gniazdo ...", "UBYTEK", "Najwiekszy
   ubytek: ... mm" i obraz "Widok z gory: czerwone = brakuje materialu, ...". Technik bierze prace do reki i klika
   "Ukruszona" (klawisz U) albo "OK" (O); pod spodem "Decyzja: Ukruszona - Tester, ...". "Cofnij decyzje" (C) cofa.
3. **Przelaczenie na poranek:** "Poranek" na gornym pasku - ekran pieca ("Jeszcze nie ma pieca - zeskanuj pierwsza
   plytke poranna (piec otworzy sie sam)."), "Rozkladanie kuwet", "Kompletne i braki". Z powrotem: "Wieczor".
   Plytke nr 8 skanuj tylko wieczorem - rano program ja zablokuje ("Plytka nie z tego trybu").
4. **Lista "Do dofrezowania"** pod mapa: po "Ukruszona" praca jest na liscie ("Do dofrezowania: 1", kolumny "Kuweta",
   "Zab", "Plytka", "Gniazdo"); "Zapisz liste do pliku".
5. **Pasek stanu na dole:** "Folder skanera:" "dostepny", "Analiza:" "nic nie czeka", "Folder projektow:" z liczba
   plikow, "Ramki:" "wylaczone", "wersja 0.3.9-rc2" - technik widzi, ze program czuwa.

Czego prototyp jeszcze nie robi (do powiedzenia wprost): Ramki z diodami sa w programie wylaczone, bo ich elektroniki
jeszcze nie ma - dzis prace rozklada sie wedlug ekranu. Program pierwszy raz widzi prawdziwy skaner, wiec rozpoznanie
plytki i kolory prac moga sie jeszcze mylic, a rano bez folderow zlecen i bez Excela nie podpowie numerow kuwet - po
to jest ten dzien. Po starcie program sam przelicza wszystkie wczesniejsze skany z folderu (pytanie, czy przeliczac
stare skany, bedzie w nastepnej wersji), a jeden komunikat o numerze plytki wspomina jeszcze ramke, choc ramki sa wylaczone.

## D. Co zapisac i co przywiezc

**D1. Na kartce / w arkuszu:** godziny skanow, numer plytki, ktore gniazdo i jaki ubytek (B3, B5), co pokazal ekran
(kolor, napis), czasy ze stopera, zdjecia ekranu telefonem przy kazdym kroku, ktory poszedl inaczej niz w dokumencie. Bez nazwisk pacjentow.

**D2. Na pendrive:** plik ZIP z "Zakoncz i spakuj" (folder `paczka\` sesji z B6); caly folder `C:\Skany_test`;
folder `C:\Sprzet_testy\wyniki` (gdy byly kroki 2.4 / 2.5a); folder wynikow programu `C:\Stanowisko\dane` - tylko gdy
nazwy plikow w `C:\Projekty_STL` sa bez nazwisk (baza zapisuje nazwy plikow projektow); zdjecia telefonu; wypelniony
arkusz (zdjecie kazdej strony). Liczby z wnetrza programu (odstep punktow skanu, pierscien brzegu i podobne) odczyta potem sesja z tych plikow -
na miejscu wystarczy kartka.
