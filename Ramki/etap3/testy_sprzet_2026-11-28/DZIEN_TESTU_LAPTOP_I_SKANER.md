# Dzien testu 28.11.2026 - laptop i skaner (program 0.3.9-rc2)

Dla wlasciciela, do wydruku razem z arkuszem (numery A1-D2 sa te same). Ten dokument wystarczy na caly dzien - starego
dokumentu (`PIERWSZE_TESTY_NA_SPRZECIE`) nie trzeba drukowac; numery w nawiasach, np. (2.3), to kroki tamtego dokumentu.

- W cudzyslowie "..." stoja napisy naszego programu, slowo w slowo. Na ekranie sa z polskimi literami, a pauza (-),
  wielokropek (...) i cudzyslowy wygladaja inaczej. Kursywa to napisy Windows albo programu skanera. Kazdy napis
  sprawdzono 26.11 na instalacji z paczki `Stanowisko_0.3.9-rc2.zip`.
- **[NIE SPRAWDZONE BEZ SPRZETU]** - tego nikt nie widzial na laptopie ani na skanerze. Moze pojsc inaczej.
- Zasady: w programie skanera niczego nie kasuj; krok nie wychodzi 15 minut - zdjecie ekranu telefonem, notatka,
  dalej; co poszlo inaczej niz tu, zapisz w arkuszu - to wynik, nie porazka.

**Na sobote przygotuj:** pliki projektow tylko `..._cad.stl` prac, ktore beda skanowane; 2-3 prace celowo ukruszone
(w tym jeden plytki odprysk) i kartke: gniazdo, miejsce, rozmiar; etykiety blokow tych prac (wspolczynnik); tasme
papierowa albo plasteline; plaski karton wiekszy niz 15 x 15 cm; plytke okragla R54 nr 8 i kwadratowe, jesli sa;
pendrive 16 GB lub wiekszy; telefon (zdjecia, stoper); w programie skanera osobne zlecenie testowe (bez pacjentow).

## A. Dzien wczesniej (ok. 30 minut + instalacja)

**A1. Dwa foldery na laptopie.** Zaloz pusty `C:\Skany_test` (tu program skanera bedzie zapisywal skany) i
`C:\Projekty_STL` (skopiuj tu pliki `..._cad.stl` z exocad prac, ktore jutro zeskanujesz - wszystkie luzem w tym
jednym folderze; inne STL z folderow exocad nie). Okno instalatora mowi przy tym folderze "Pliki STL z exocad, w
podfolderach zlecen" - pliki luzem tez sa dobre. Nazwa folderu projektow bez cyfr: program czyta liczbe z nazwy folderu
jako numer kuwety. Plik z nazwiskiem pacjenta w nazwie: zmien nazwisko na TEST1, TEST2... (koncowke, np.
`-11-crown_cad.stl`, zostaw - program czyta z niej zab i typ).

**A2. Pendrive i narzedzia.** Wszystko lezy na PC: paczka programu `<PC-katalog>\wydania\Stanowisko_0.3.9-rc2.zip`
i folder `<PC-katalog>\konto3\DLA_WLASCICIELA_2026-11-28` (tam ten dokument). Na pendrive skopiuj:

1. rozpakowana paczke: prawy klawisz na pliku ZIP -> *Wyodrebnij wszystkie...* -> wskaz pendrive (kilka minut). Ma byc
   folder z plikiem `Instaluj.cmd` (dwuklik wewnatrz ZIP bez rozpakowania nie zadziala - `Instaluj.cmd` sam to powie);
2. folder `narzedzia_dnia` (z `DLA_WLASCICIELA_2026-11-28`; w srodku `pole_skanu.cmd` i `pole_skanu.py`);
3. plik `Pokaz_na_danych_probnych.cmd` (z tego samego folderu).

Na laptopie: zaloz `C:\Sprzet_testy` i skopiuj do niego folder `narzedzia_dnia` (ma byc
`C:\Sprzet_testy\narzedzia_dnia\pole_skanu.cmd`; wyniki narzedzia zapisza sie same w `C:\Sprzet_testy\wyniki`).
`Pokaz_na_danych_probnych.cmd` skopiuj na pulpit.

**A3. Instalacja.** Dwuklik `Instaluj.cmd` na pendrivie. Mignie czarne okno, otworzy sie okno "Stanowisko - instalacja";
po lewej 4 kroki: "Foldery", "Osoby", "Instalacja", "Gotowe". Na dole stale: "Bez internetu. Niczego nie zmienia poza
folderem instalacji i ikonami na pulpicie."

| Krok okna | Co kliknac | Co ma byc widac | Gdy jest inaczej |
|---|---|---|---|
| 1 "Wskaz foldery" | "Folder ze skanami" -> "Wybierz..." -> `C:\Skany_test`; "Folder z projektami" -> "Wybierz..." -> `C:\Projekty_STL`; "Miejsce instalacji" zostaw `C:\Stanowisko`; "Dalej" | pod miejscem: "Potrzeba 1,9 GB wolnego miejsca. Jest ... GB." | czerwony napis, np. "Folder ze skanami nie istnieje: ..." - zrob, co mowi (folder zalozysz tez w okienku "Wybierz...") |
| 2 "Kto bedzie pracowal na stanowisku?" | w pole "Imie i nazwisko albo inicjaly" wpisz `Tester`, "Dodaj", potem "Instaluj" | `Tester` na liscie | "Dodaj co najmniej jedna osobe." - wpisz i "Dodaj" |
| 3 "Instalacja" | nic - czekaj (na PC trwalo 1 minute; z pendrive'a i z antywirusem dluzej) | "Trwa instalacja - kilka minut. Nie zamykaj tego okna."; 9 wierszy dostaje kolejno "gotowe"; najdluzej "5. Program i pakiety (kilka minut)" z rosnacym czasem "trwa..." | "Instalacja sie nie udala" i "Co zrobic: ..." - zdjecie ekranu, zrob to i "Sprobuj ponownie" (wraca na poczatek: znow "Dalej", potem "Instaluj"); "Szczegoly" pokazuje caly zapis |
| 4 "Gotowe" | "Uruchom program" | "Program 'Stanowisko' 0.3.9-rc2 jest zainstalowany w C:\Stanowisko."; "Na pulpicie sa ikony: 'Stanowisko', 'Dzien skanera'."; "Ramki sa wylaczone - program dziala bez nich (rozkladanie wedlug podpisow na ekranie)." | brak ikon: okno podaje plik do klikniecia w `C:\Stanowisko` (`Stanowisko.cmd` albo `Dzien_skanera.cmd`) |

**A4. Pierwszy start.** Program otwiera sie w trybie "Wieczor". Po prawej "Kto teraz pracuje?" - kliknij `Tester`.
Na dolnym pasku: "Folder skanera:" "dostepny", "Folder projektow:" "plikow projektow: ..." (liczba Twoich
plikow STL), "Ramki:" "wylaczone", "wersja 0.3.9-rc2". Po lewej "Jeszcze nie ma skanow.". Liczba plikow to 0: skopiuj
pliki `..._cad.stl` do `C:\Projekty_STL` i kliknij na pasku "Odswiez pule". "Folder skanera:" nie mowi "dostepny":
zdjecie paska, w arkuszu A4. Zamknij program krzyzykiem. [NIE SPRAWDZONE BEZ SPRZETU: wyglad na ekranie laptopa]

**A5. Ikona "Dzien skanera".** Okno "Dzien skanera - krok po kroku (sesja ...)"; na gorze "Obserwuje:" i
`C:\Skany_test`; po lewej 14 krokow, pierwszy "1. Zanim zaczniesz". Zamknij okno (to tylko proba).

**A6. Proba pokazu na danych probnych** (2 minuty; to plan B na pokaz, C6). Dwuklik `Pokaz_na_danych_probnych.cmd` na
pulpicie. Mignie czarne okno, po kilkunastu sekundach otworzy sie program z gotowymi danymi: po lewej "Plytki tej
zmiany" i 5 kafelkow ("Plytka bez numeru", "Plytka 4", "Plytka 3", "Plytka 2", "Plytka 1"), osoba "Technik A".
Zamknij krzyzykiem. Nic sie nie otworzylo: zdjecie, arkusz A6 (w sobote pokaz tylko na prawdziwym skanie).

**A7. Gdy Windows albo program ochronny przeszkadza** [NIE SPRAWDZONE BEZ SPRZETU]:

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

**Pola z gwiazdka.** Kazdy krok okna "Dzien skanera" ma pod instrukcja pola do wpisania; pole z gwiazdka (np.
"Numer plytki *") jest wymagane - puste trafi do paczki jako brak i sesja nie odczyta potem liczb. Wpisuj zawsze:
"Numer plytki" = `8` (dla plytki nr 8), "Wspolczynnik z etykiety bloku" = liczba z etykiety bloku kazdej pracy, po
przecinku (prace spieczone: 1; etykiety nie ma: `nie wiem`), gniazda prac i ukruszen - numery gniazd i co w nich lezy.
Przed kazdym skanem kliknij po lewej wlasciwy krok ("klik = nowe pliki trafiaja do tego kroku"); "Krok zrobiony -
dalej" po kazdym kroku.

**B1 (2.1-2.2). Okno "Dzien skanera"** (ikona, 5 + 15 minut). Pytanie "Znaleziono niedokonczona sesje z ..." "Wznowic ja?"
(zostala po A5) - "Nie", czyli nowa sesja. Na gorze "Obserwuje:" i `C:\Skany_test`. Kroki 1-4 okna ("Zanim
zaczniesz" ... "Zlecenie testowe i ekran skanowania - zrzuty"): rob, co mowi okno; zrzuty ekranu przyciskiem "Zrzut
ekranu (za 3 s)" (krok 2 chce 4 zrzuty, krok 4 - 2). W kroku 2 pole "Folder zapisu zlecen ('Order Save Path') *":
przepisz sciezke z programu skanera albo wpisz `nie wiem`. Nie wychodzi: "Nie udalo sie / pomijam, bo..." i jedno
zdanie. Najwazniejsze do arkusza: format pliku i czy jest JEDEN plik na cala plytke.

**B2 (2.3). Pusta plytka nr 8** (krok okna "5. Skan 1: pusta plytka", 15 minut). Pola: "Ktora plytka" =
`okragla testowa R54`, "Numer plytki" = `8`. Wyczysc stozki plytki. Linia ciecia w programie skanera POWYZEJ stolika
i co najmniej 3 mm PONIZEJ wierzchu plytki; wierzchu nie obcinaj, stolik i podstawke odetnij. Zapis jako STL calej
plytki, bez wygladzania; czas stoperem ("Stoper: start" / "Stoper: stop"). Dobrze: plik sam pojawia sie w oknie,
po kilkunastu sekundach zielona ocena "Skan dobry" (na ekranie wielkimi literami, z obrysem plytki w mm).

| Widzisz | Zrob |
|---|---|
| plik sie nie pojawia po minucie | w programie skanera *Explore* albo *Export*; w oknie "Nie wiem, gdzie skaner zapisuje - szukaj" |
| czerwone "TEN SKAN SIE NIE NADA, bo ... ZROB TAK: ..." | zrob to, co po "ZROB TAK" |
| czerwone, a w podgladzie skanu wokol plytki plaski stolik | SKAN Z PODLOZEM - nizej |

SKAN Z PODLOZEM - najwieksze ryzyko dnia. Gdy w skanie jest plaski stolik wokol plytki, program nie rozpoznaje plytki:
KAZDY skan jest czerwony, a okno mowi o polu skanera i brudnych stozkach - to zla przyczyna, czyszczenie nie pomoze.
Podnies ciecie nad stolik i zrob DWA skany tej samej plytki (oba w kroku 5): (A) ciecie tuz nad stolikiem - scianka
boczna plytki zostaje; (B) ciecie 3 mm pod wierzchem. Oba sprawdz narzedziem jak w B3 (krok 2) i zapisz w arkuszu B2.
Dalej skanuj jak skan zielony (oba zielone: jak A). Inna przyczyna samych czerwonych: pole skanera 90 mm i mniej (B3).
[NIE SPRAWDZONE BEZ SPRZETU: prawdziwy plik skanera; czy stolik trafia do skanu; skany A i B]

**B3 (2.4). Pole skanera w liczbach** (15 minut, obowiazkowo). Narzedzie: plik skanu przeciagnij myszka na
`C:\Sprzet_testy\narzedzia_dnia\pole_skanu.cmd`. Otworzy sie czarne okno z dwoma pytaniami: "Numer wybity na plytce,
cyfra 1-9 (sam Enter = nie wiem):" - sam Enter; "Co lezy na stoliku? ..." - wpisz krotko, co naprawde lezy (bez
nazwisk), Enter. Po kilkunastu sekundach wynik, blok "DO ARKUSZA (przepisz):" i wiersz "Zapisano:"; dowolny klawisz
zamyka okno. Plik skanu: w `C:\Skany_test` albo w oknie "Otworz folder sesji" -> folder `kroki`.

1. NAJPIERW karton (glowny pomiar): plaski karton na stolik, linia ciecia pod karton, skan, zapis (w oknie "Dzien
   skanera" przed skanem kliknij krok 12; plik w zlym kroku: "Przenies zaznaczony plik do innego kroku...").
   W oknie karton dostanie czerwona ocene - to dobrze (to nie plytka), nic nie poprawiaj. Narzedzie, opis `karton`.
   Ma byc "PLYTKA NIE ROZPOZNANA" (to dobrze - to karton), a w punkcie 2 wymiar pola: "Dane mieszcza sie w kole o srednicy ok. ... mm" albo "DANE NIE SA KOLEM: ... x ... mm" (przepisz OBIE liczby) i zdanie
   "Dane sa PLASKIE: ...". Nie ma tego zdania: karton byl wygiety albo widac stolik - liczby i tak przepisz.
2. Potem skan pustej plytki nr 8 z B2 (opis `okr-test 8, pusta`): przepisz wiersz "program mowi" i wiersz o polu.
   "UWAGA: w skanie jest prawdopodobnie PODLOZE" = skan z podlozem - wroc do B2.

Narzedzie nie dziala: zabierz pliki skanow (policzymy na PC). [NIE SPRAWDZONE BEZ SPRZETU: liczby na prawdziwym skanie]

**B4 (2.5). Skany wedlug okna** (ok. 1 godziny), kazdy w swoim kroku okna, wszystko na plytce nr 8, z polami:

| Krok okna | Co polozyc | Pola z gwiazdka (i inne) |
|---|---|---|
| "6. Skan 2: plytka z pracami calymi" | 6-10 prac z projektami z `C:\Projekty_STL` | "Numer plytki", "Wspolczynnik z etykiety bloku", "Czas skanu" (stoper); "W ktorych gniazdach leza prace" |
| "7. Skan 3: TO SAMO drugi raz, bez ruszania plytki" | nic nie ruszaj; zapis pod inna nazwa | "Czas skanu" (stoper) |
| "9. Skan 4: plytka z 2-3 pracami celowo ukruszonymi" | prace ukruszone do TYCH SAMYCH gniazd | "Gniazda z pracami ukruszonymi i miejsce ukruszenia", np. `5: brzeg od strony policzka` |
| "10. Skan 5: praca potracona w trakcie skanu" | tylko gdy bezpiecznie | "W ktorych gniazdach leza prace" |
| "11. Skan 6: praca bokiem i praca czesciowo zaslonieta" | jedna bokiem, jedna zaslonieta | "W ktorych gniazdach leza prace" - ktore bokiem, ktore zasloniete |
| "12. Skan 7: druga plytka (poranna albo okragla), jesli jest" | plytka kwadratowa; tu tez skany B5 | "Ktora plytka", "Numer plytki" |

Kazdy skan ma w oknie ocene; ocena i notatka do arkusza B4. Zolta "Uwaga" przy kroku 11 jest w porzadku.

**B5 (2.5a). Czy program poznaje plytke okragla nr 8** (30 minut, obowiazkowo). Program bierze okragla plytke bez
widocznych dolkow numeru i bez scianki bocznej za KWADRATOWA i nie ostrzega - mierzymy, jak czesto. Plytke nr 8 zeskanuj
trzy razy, w kroku 12 okna (pola: "Ktora plytka" = `okragla testowa R54`, "Numer plytki" = `8`; w notatce: i, ii, iii):
(i) pusta; (ii) z praca w gniezdzie obok dolkow numeru; (iii) z dolkami numeru zaklejonymi tasma papierowa. Gdy jest
kwadratowa - jeden skan pustej dla porownania; PRZED tym skanem zmien w kroku 12 "Numer plytki" z `8` na numer
kwadratowej (nie ma numeru - wyczysc pole), a "Ktora plytka" na `kwadratowa` (okno podaje numer z pola programowi; z `8`
oceniloby kwadratowa jak okragla nr 8). Kazdy plik daj narzedziu z B3: numer - SAM ENTER (podany numer podpowiada
programowi ksztalt), opis np. `okr-test 8, dolki zaklejone`. Przepisz do arkusza B5 wiersze "program mowi" i
"numer z dolkow". Dobrze: "okragla testowa (poza ramka)" ze "stary rozstaw R54"; przy (iii) numer z dolkow 0 albo
"nie odczytany" (dolki zaklejone - tak ma byc). Zle, ale bardzo wazne: "kwadratowa" - zapisz, przy ktorym skanie.
[NIE SPRAWDZONE BEZ SPRZETU: caly krok]

Potem zamknij okno "Dzien skanera" (sesja zostaje).

**B6 (2.7 i proba f). Program "Stanowisko" na prawdziwych skanach** (30 minut). W `C:\Skany_test` leza juz skany z B2-B5.
Ikona "Stanowisko", osoba `Tester`. Program sam bierze kazdy skan, ktorego jeszcze nie liczyl - takze te sprzed
startu (proba f): po lewej kafelek na kazdy skan, na pasku "Analiza:"; wsrod komunikatow "Program wznowil prace" -
"Po ponownym uruchomieniu program dokancza zalegle skany: ..." (komunikaty sa pokazywane po jednym; nastepny pokazuje
przycisk "i jeszcze ..."). Pytania, czy przeliczyc stare skany, w tej wersji jeszcze nie ma - zapisz, ile minut liczyl.
Poczekaj, az pasek pokaze "Analiza:" "nic nie czeka". Potem nowa plytka nr 8 z pracami: zapisz skan i wlacz stoper.
Dobrze: po lewej kafelek "Plytka 8", w srodku mapa (zatrzymaj stoper). Nie odczytal numeru: pytanie "Podaj numer
plytki" - kliknij 8. Kolory prac porownaj z kartka: "OK" zielone, "UBYTEK" czerwone, "sprawdz" zolte, "bez projektu"
szare (brak STL tej pracy w folderze projektow).
[NIE SPRAWDZONE BEZ SPRZETU: czas analizy prawdziwego skanu; odczyt numeru plytki nr 8; czy kolory sie zgadzaja]

| Widzisz | Zrob |
|---|---|
| "Analiza skanu nie powiodla sie" | przepisz tekst w nawiasie, np. "w skanie widac 0 z 3 znacznikow plytki ..." (przy 0 z 3 najpierw sprawdz stolik w skanie, B2) |
| "Plytka nie pasuje do ukladu" | zdjecie, arkusz; plytke ustaw na srodku pola |
| "Ponowny skan tej samej plytki?" | to ta sama plytka bez zmian: "Tak, to ponowny skan"; inne prace: "Nie, to nowy wsad" |
| "Nowy wynik czeka: ..." | ekran zostal na poprzedniej plytce - kliknij "Pokaz nowy wynik" |
| "Ten sam projekt w dwoch gniazdach" ("... sprawdz, ktora praca jest ktora") | sprawdz na plytce, czy w tych gniazdach leza naprawde dwie prace z jednego pliku STL. Tak - "Zamknij". Nie (rozne prace) - program pomylil prace: zdjecie ekranu, oba gniazda do arkusza B6, dopiero potem "Zamknij" |
| nic sie nie dzieje | plik nie konczy sie na `.stl` albo trafil do innego folderu niz `C:\Skany_test` |

**B7. Proby z analizy kodu** (po 5-10 minut, program "Stanowisko" otwarty; kazda proba = nowy skan; wynik do arkusza B7):

- a) 2-3 prace z odpryskiem brzegu roznej wielkosci, w tym jeden bardzo maly - ktore sa "UBYTEK", a ktore "OK"?
- b) ta sama praca z ubytkiem drugi raz, ubytkiem w dol albo w cien; na pytanie "Ponowny skan tej samej plytki?" -
  "Tak, to ponowny skan". Czy zostaje "UBYTEK"?
- c) 2-3 mm brzegu calej pracy zaklejone tasma albo plastelina - czy praca jest "nie sprawdzono" (a nie "OK")?
- d) praca bokiem albo do gory nogami - czy NIE jest zielona "OK"?
- e) dwie plytki kwadratowe jedna po drugiej; przy pierwszej na pytanie "Podaj numer plytki" kliknij "Pozniej".
  Czy przy drugiej panel i kafelki dalej mowia o wlasciwym skanie ("Plytka bez numeru" z godzina skanu)?
- f) zrobiona w B6.

**B8 (2.6). "Zakoncz i spakuj"** (10 minut). Ikona "Dzien skanera"; "Wznowic ja?" - "Tak" (ta sama sesja).
Krok "14. Na koniec: kopia CALEGO folderu zlecen programu skanera": w programie skanera nie ma zlecen pacjentow, wiec
kliknij "Skopiuj caly folder zlecen skanera", potem "Krok zrobiony - dalej". Potem "Zakoncz i spakuj". Pytanie
"Brakuje wymaganych krokow" wymienia braki; "nie wpisano: ..." znaczy puste pole z gwiazdka - kliknij "Nie" (to jest
tez wybor domyslny, sam Enter), wpisz brakujace pole w tamtym kroku i znow "Zakoncz i spakuj". Zostaly tylko braki nie do
zrobienia (np. pominiety krok) - "Tak". Dobrze: okienko "Sesja spakowana" i sam otworzy sie folder z plikiem ZIP
(`C:\Stanowisko\dane\dzien_skanera\<data_godzina>\paczka\`). Nie wychodzi: niczego nie kasuj, skopiuj caly folder sesji
z data i godzina na pendrive. [NIE SPRAWDZONE BEZ SPRZETU: czas pakowania prawdziwych skanow]

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
6. **Plan B - gdy w B6 zaden prawdziwy skan nie dal mapy z praca czerwona** (np. kazdy kafelek "analiza nie powiodla
   sie" albo same zielone): najpierw pokaz krotko prawdziwy skan - kafelek i komunikat programu, co jest nie tak ze
   skanem (to tez wynik dnia). Potem zamknij program "Stanowisko" krzyzykiem i dwuklik `Pokaz_na_danych_probnych.cmd`
   na pulpicie. Powiedz szefowi: **To sa dane probne, nie skan z dzisiaj.** Widac: 5 kafelkow ("Plytka bez
   numeru", "Plytka 4", "Plytka 3", "Plytka 2", "Plytka 1"), osoba "Technik A", na gorze pytanie "Podaj numer plytki -
   skan z ..." ("Program nie odczytal numeru plytki ze skanu. ...") - kliknij "Pozniej". Dalej krok po kroku:
   a) Kliknij kafelek "Plytka 1" (na kafelku "UBYTEK 1"). Na gorze zolty komunikat "Plytka 1, skan z ...: Praca
      niesprawdzona" ("Gniazdo 7: kontrola zakonczyla sie bledem programu - ...") - to tez dane probne, kliknij
      "Zamknij". Na mapie jest jedno czerwone gniazdo - gniazdo 2 (pomaranczowe obok to inna praca).
   b) Kliknij czerwone gniazdo: po prawej "Plytka 1 - gniazdo 2", "UKRUSZONA", "Najwiekszy ubytek: 0,62 mm" i "Decyzja:
      Ukruszona - Technik A, ..." - w danych probnych decyzja juz jest, dlatego "Ukruszona" jest szare.
   c) Kliknij "Cofnij decyzje" (klawisz C): wraca "UBYTEK", "Brak decyzji dla tej pracy", pod mapa "Do dofrezowania:
      0" i "Lista jest pusta.". Powiedz: technik bierze prace do reki i decyduje.
   d) Kliknij "Ukruszona" (klawisz U): znow "UKRUSZONA", "Decyzja: Ukruszona - Technik A, ...", "Do dofrezowania: 1",
      w liscie wiersz z kuweta 9002, plytka 1, gniazdo 2.
   e) Dalej punkty 3 ("Poranek", potem "Wieczor") i 5 (pasek; tu "plikow projektow: 16") jak wyzej.
   f) Powrot do zwyklej pracy: zamknij to okno krzyzykiem, ikona "Stanowisko", osoba `Tester`. Dane probne nie trafiaja
      do bazy ani do folderow skanow i projektow - po zamknieciu okna znikaja.

Czego prototyp jeszcze nie robi (do powiedzenia wprost): Ramki z diodami sa w programie wylaczone, bo ich elektroniki
jeszcze nie ma - dzis prace rozklada sie wedlug ekranu. Program pierwszy raz widzi prawdziwy skaner, wiec rozpoznanie
plytki i kolory prac moga sie jeszcze mylic - po to jest ten dzien; rano numery kuwet podpowiada dopiero z folderow
zlecen i Excela, ktorych na tym laptopie nie ma. Po starcie program sam przelicza wszystkie wczesniejsze skany z folderu
(pytania, czy je przeliczac, jeszcze nie ma), a jeden komunikat o numerze plytki wspomina jeszcze ramke, choc ramki sa
wylaczone.

## D. Co zapisac i co przywiezc

**D1. Na kartce / w arkuszu:** godziny skanow, numer plytki, ktore gniazdo i jaki ubytek (B4, B7), co pokazal ekran
(kolor, napis), czasy ze stopera, liczby z narzedzia (B3, B5), zdjecia ekranu telefonem przy kazdym kroku, ktory poszedl
inaczej niz w dokumencie. Bez nazwisk pacjentow.

**D2. Na pendrive** (16 GB lub wiecej; ZIP sesji ma kazdy skan dwa razy, prawdziwe skany moga miec razem kilka GB
[NIE SPRAWDZONE BEZ SPRZETU: wielkosc skanow]): plik ZIP z "Zakoncz i spakuj" (folder `paczka\` sesji z B8); caly folder
`C:\Skany_test`; folder `C:\Sprzet_testy\wyniki`; folder wynikow programu `C:\Stanowisko\dane` - tylko gdy nazwy plikow w
`C:\Projekty_STL` sa bez nazwisk (baza zapisuje nazwy plikow projektow); zdjecia telefonu; wypelniony arkusz (zdjecie
kazdej strony). Liczby z wnetrza programu (odstep punktow skanu, pierscien brzegu i podobne) odczyta potem sesja z tych
plikow - na miejscu wystarczy kartka.

## Zapytaj przed sobota

> Trzy sprawy do decyzji wlasciciela. Bez odpowiedzi obowiazuje odpowiedz domyslna.
>
> 1. **Proba f):** program po starcie sam liczy wszystkie wczesniejsze skany z folderu - pytania, czy je przeliczyc,
>    w tej wersji nie ma. Czy w B6 wystarczy zapisac, ile minut liczyl? Domyslnie: tak.
> 2. **Wspolczynnik:** prace na plytce testowej moga nie miec etykiety bloku. Co wpisac w polu
>    "Wspolczynnik z etykiety bloku"? Domyslnie: liczba z etykiety bloku, z ktorego frezowano prace; nie wiadomo -
>    `nie wiem` (pole nie moze zostac puste).
> 3. **Obietnice dla szefa:** czy mowic, kiedy beda pytanie o przeliczanie starych skanow i ramki? Domyslnie: bez
>    terminow - powiedz, ze to jest zapisane do zrobienia, a termin bedzie po analizie dzisiejszych skanow.
