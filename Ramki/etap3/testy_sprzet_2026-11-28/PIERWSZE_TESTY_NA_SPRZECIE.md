# Pierwsze testy na prawdziwym sprzecie - 28-29.11.2026

Dokument dla wlasciciela. Wydrukuj go razem z `ARKUSZ_OBSERWACJI.md`. Stan: 21.11.2026, wersja dla paczki
programu 0.3.3 (paczka jeszcze nie istnieje).

Do tej pory program byl sprawdzany tylko na danych sztucznych i na "atrapach" (program udaje ramke albo
skaner). Ten weekend to pierwsze spotkanie programu ze skanerem i z ramka. Cel NIE jest taki, zeby wszystko
zadzialalo. Cel: zebrac liczby i pliki, ktorych nie da sie zdobyc bez sprzetu. Kazda rzecz, ktora pojdzie
inaczej niz tu napisano, jest wynikiem - zapisz ja w arkuszu.

Znaczniki w tekscie:

- **[NIE SPRAWDZONE BEZ SPRZETU]** - tego nikt nie widzial na prawdziwym urzadzeniu. Moze pojsc inaczej.
  Lista zbiorcza jest na koncu.
- **[DO POTWIERDZENIA NA 0.3.3]** - opis wedlug raportow programistow; zostanie sprawdzony na nowej paczce
  programu przed weekendem. Gdyby na miejscu wygladalo to inaczej - zapisz, co widzisz.

Zasady na caly dzien:

1. W programie skanera niczego nie kasuj.
2. Zadnych nazwisk pacjentow: zlecenia nazywaj TEST1, TEST2. Do testow bierz prace probne albo odrzuty.
3. Krok nie udaje sie dluzej niz 15 minut? Zrob zdjecie ekranu telefonem, zapisz i idz dalej. Przy kazdym
   kroku jest napisane, dokad mozna przejsc.
4. Czesc 2 (skaner) i czesc 3 (ramka) nie zaleza od siebie. Mozna zrobic sam skaner bez ramki i odwrotnie.
   Jedna ramka wystarcza.

---

## 0. Pytania do wlasciciela - odpowiedz najpozniej do srody 25.11.2026

Nie znamy odpowiedzi i nie zgadujemy. Odpowiedzi dopisz w tym pliku pod pytaniem albo przekaz sesji
prowadzacej projekt. Te same odpowiedzi wpisz na pierwszej stronie arkusza. Najpilniejsze sa P3, P1, P6
i P8: od nich zalezy, co trzeba przygotowac PRZED weekendem.

**P3. Czy Raspberry Pi w ramce jest zlozone z matryca diod i czujnikami, ma karte SD i czy ktos wgral na nia
"program ramki"?** Firma zewnetrzna mogla dostarczyc sama obudowe, sama elektronike albo calosc.
- Program ramki jest wgrany: cala czesc 3 do zrobienia.
- Nie ma go albo nie wiesz: ktos musi go wgrac PRZED sobota wedlug instrukcji `ramka_raspberry_pi.md`
  (12 krokow, kilka godzin, potrzebny internet; skrot w `ZALACZNIKI.md`). Bez tego z czesci 3 zostaje tylko
  krok 3.1 (ogledziny bez pradu), a ok. 2 godziny planu odpadaja. Napisz, kto i kiedy to zrobi.

**P1. Ktora ramka przyszla: wieczorna, poranna czy obie? Jaka ma wkladke: kwadratowa czy okragla?**
- Wieczorna: plytki 1-3, adres `ramka-w.local`. Krok 3.9 (klawiatura) odpada.
- Poranna: plytki 4-6, adres `ramka-p.local`. Dochodzi krok 3.9.
- Wkladka okragla: w kroku 3.7 wybierasz rodzaj plytki "okragla ramkowa"; polozenie diod pod taka wkladka
  jest policzone tylko z rysunku.

**P6. Jaka siec laczy komputer z ramka: router w pracowni, hotspot z laptopa, hotspot z telefonu? Jaka siec
Wi-Fi jest wpisana w ramce?**
- Komputer i ramka musza byc w TEJ SAMEJ sieci. Od odpowiedzi zalezy krok 3.3.
- Nie wiesz, jaka siec jest wpisana w ramce: krok 3.3 moze sie nie udac - wtedy z czesci 3 zostaja kroki
  3.1, 3.2 i ogledziny napisow na matrycy.

**P8. Czy ramka ma ustawiony "klucz" (haslo ramki) i czy go znasz?** Program ramki wgrany skryptem z naszej
paczki losuje klucz i zapisuje go na ramce w pliku `/etc/ramka/ramka.json`.
- Znasz klucz: przywiez go na kartce. Wpiszesz go raz w kroku 3.3 i raz w kroku 3.8.
- Nie znasz, a ramka go wymaga: kroki 3.4-3.9 odpadaja, dopoki klucza nie odczyta osoba, ktora wgrywala
  program (instrukcja `ramka_raspberry_pi.md`, krok 7). Krok 3.3 sam pokaze, czy ramka wymaga klucza.

**P2. Ktore plytki sa na miejscu i czy maja wklejone magnesy?** Kwadratowe nowe (1-6), okragle ramkowe
(1-6), okragle testowe (8, 9), stare R54.
- Od tego zalezy, co skanujesz w krokach 2.3-2.5a. Im wiecej rodzajow, tym lepiej.
- Plytki bez magnesow: krok 3.5 odpada (ramka czyta numer tylko z magnesow), a ramka nie zaswieci pod nimi.
- Nie ma zadnej plytki okraglej: krok 2.5a odpada.

**P4. Na jakim komputerze uruchomisz program: laptop stanowiska, PC, inny?** Musi miec Windows 10 albo 11
i ok. 3 GB wolnego miejsca (z oknem "Dzien skanera" 30 GB).
- Laptop stanowiska: dochodzi czesc 4. Inny komputer: czesc 4 odpada.

**P5. Czy skaner stoi przy tym samym komputerze? Do jakiego folderu program skanera zapisuje skany?**
- Przy tym samym: kroki 2.1 i 2.7 jak w opisie.
- Przy innym: albo instalujesz nasz program na komputerze skanera (kroki 1.1-1.4 tam), albo przenosisz
  pliki skanow pendrivem. Wtedy krok 2.7 odpada, a kroki 2.4 i 2.5a robisz na przeniesionych plikach.

**P7. Czy masz projekty STL (z exocad) prac probnych, ktore polozysz na plytce?**
- Masz: w kroku 2.7 program porowna prace z projektem.
- Nie masz: prace beda szare "bez projektu". To wystarczy, zeby sprawdzic, czy skan dochodzi.

---

## 1. Co przygotowac i zabrac

Pendrive (co najmniej 16 GB), a na nim:

- [ ] paczka programu `Stanowisko_0.3.3.zip` [DO POTWIERDZENIA NA 0.3.3]
- [ ] instalator Pythona 3.12.10 dla Windows (64-bit) z python.org: `python-3.12.10-amd64.exe`
- [ ] folder `testy_sprzet_2026-11-28` (ten dokument, arkusz, podfolder `narzedzia`)
- [ ] 2-3 projekty STL prac probnych, bez nazwisk w nazwach plikow (P7)

Wydruki: [ ] ten dokument, [ ] arkusz, [ ] karta "Dzien skanera" i sciaga programu skanera (dostaniesz je
razem z tym dokumentem), [ ] kartka z kluczem ramki (P8).

Sprzet i drobiazgi:

- [ ] ramka, zasilacz 5 V 4 A z wtykiem 5,5/2,1; klawiatura numeryczna z odbiornikiem (ramka poranna)
- [ ] plytki (wszystkie, jakie sa), pokrywka, zapasowe magnesy
- [ ] 6-10 prac probnych albo odrzutow, 2-3 do celowego ukruszenia
- [ ] suwmiarka, stoper (telefon), telefon do zdjec, dlugopis, tasma papierowa (krok 2.5a)
- [ ] plaski karton albo sztywna kartka, wieksza niz 15 x 15 cm (krok 2.4)
- [ ] dostep do routera albo telefon z hotspotem (P6)
- [ ] czysta sciereczka i pedzelek (stozki na plytkach musza byc bez pylu)

---

## 2. Skrot dnia

    Czesc 1  komputer i program          ok. 40 min   kroki 1.1 - 1.4
    Czesc 2  skaner                      ok. 2,5 godz. kroki 2.1 - 2.7
    Czesc 3  ramka (jedna wystarczy)     ok. 2 godz.  kroki 3.1 - 3.9
    Czesc 4  laptop stanowiska           ok. 20 min   kroki 4.1 - 4.5 (tylko na laptopie)
    Czesc 5  zebranie plikow             ok. 20 min

Cztery najwazniejsze wyniki dnia:

1. wymiar pola skanera (krok 2.4),
2. czy program poznaje plytke okragla, gdy nie widzi dolkow numeru (krok 2.5a),
3. czy ramka czyta numer kazdej plytki (krok 3.5),
4. czy diody trafiaja pod gniazda (krok 3.7).

Wyjscia awaryjne: nie ma Pythona albo instalacja sie nie udala - zrob 3.1, 3.2 i skany zapisywane recznie
na pendrive. Ramka nie odpowiada - zrob cala czesc 2. Skaner nie daje pliku STL - zrob cala czesc 3.

---

## Czesc 1 - komputer i program

### Krok 1.1 - Python 3.12 (5 minut)

Co zrobic: uruchom z pendrive'a `python-3.12.10-amd64.exe`, opcje domyslne, "Install Now".
Udalo sie, gdy: instalator konczy sie napisem "Setup was successful".
Zanotuj (arkusz 1.1): czy sie udalo, pytania Windows.
Gdy sie nie uda: zapisz komunikat. Zostaja kroki 3.1, 3.2 i skany zapisywane recznie na pendrive.
[NIE SPRAWDZONE BEZ SPRZETU: instalator Pythona na obcym komputerze]

### Krok 1.2 - instalacja programu z paczki (10-15 minut)

Co zrobic:

1. Skopiuj `Stanowisko_0.3.3.zip` na dysk, np. do `C:\Paczki`. Prawy klawisz -> "Wyodrebnij wszystkie".
2. Zaloz dwa puste foldery: `C:\Stanowisko_test\skany` i `C:\Stanowisko_test\projekty`. Do `projekty`
   skopiuj projekty STL prac probnych, jesli je masz.
3. W rozpakowanym folderze kliknij dwa razy `zainstaluj.cmd`. Czarne okno pokazuje kroki [1/9] ... [7/9]
   (ok. 1 minuty). Pierwszy raz konczy sie wierszem:

       INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom zainstaluj.cmd ponownie (kod 10)

   To NIE jest blad. Program nie zna jeszcze folderow tego komputera.
4. Otworz plik `C:\Stanowisko\ustawienia.toml`: prawy klawisz -> "Otworz za pomoca" -> Notatnik. Wiersze
   znajdziesz przez Ctrl+F. Zmien TRZY wiersze (ukosniki w prawo `/`):

       folder_eksportu_skanera = "C:/Stanowisko_test/skany"
       folder_cyrkon = "C:/Stanowisko_test/projekty"
       operatorzy = ["Tester"]

   Reszty nie ruszaj. Zapisz (Plik -> Zapisz). Kodowania nie zmieniaj; gdyby Notatnik pytal: "UTF-8",
   NIE "UTF-8 z BOM".
5. Kliknij dwa razy `zainstaluj.cmd` JESZCZE RAZ (kilka sekund).

Udalo sie, gdy: ostatni wiersz to `INSTALACJA: GOTOWA - wersja biezaca ...`, a w `C:\Stanowisko` sa pliki
`Stanowisko.cmd`, `Samokontrola.cmd`, `Polecenie.cmd`, `Dzien_skanera.cmd`. [DO POTWIERDZENIA NA 0.3.3]
Zanotuj (arkusz 1.2): czas, ostatni wiersz, pytania Windows.
Gdy sie nie uda: przepisz wiersze zaczynajace sie od `BLAD:` i `CO ZROBIC:` i zrob to, co mowi `CO ZROBIC`.
Gdy Windows pyta "Czy chcesz uruchomic ten plik?" - zezwol. Bez instalacji przejdz do kroku 3.1.
[NIE SPRAWDZONE BEZ SPRZETU: laptop firmowy - antywirus, uprawnienia, Notatnik]

### Krok 1.3 - samokontrola i pierwszy start (5 minut)

Co zrobic:

1. Kliknij dwa razy `C:\Stanowisko\Samokontrola.cmd`.
2. Kliknij dwa razy `C:\Stanowisko\Stanowisko.cmd`. Na pytanie "Kto teraz pracuje?" kliknij "Tester".
   Popatrz na pasek u gory i zamknij okno.

Udalo sie, gdy: samokontrola konczy sie wierszem `SAMOKONTROLA: ZIELONA` i ma wiersz
`OK modele: uklady plytek z [plytki]: poprawne 10 z 10` [DO POTWIERDZENIA NA 0.3.3]. Wiersze
`OSTRZEZENIE ramka_wieczorna`, `ramka_poranna`, `excel`, `baza`, `pula` sa teraz normalne. W pasku programu
jest "Folder skanera: dostepny" i "Ramki: W: brak polaczenia" (ramki jeszcze nie ma w sieci).
Zanotuj (arkusz 1.3): kolor samokontroli, wiersz `OK modele`, czy okno sie otwiera.
Gdy sie nie uda: "poprawne 8 z 10" albo "9 z 10" = stara albo niepelna paczka - zapisz to. Przepisz wiersz
`BLAD: ...`. Mozesz isc do czesci 2: okno "Dzien skanera" jest osobnym programem.
[NIE SPRAWDZONE BEZ SPRZETU: wyglad okna na ekranie laptopa]

### Krok 1.4 - narzedzia dnia sprzetu (2 minuty)

Co zrobic: skopiuj z pendrive'a caly folder `testy_sprzet_2026-11-28` na dysk jako `C:\Sprzet_testy`.
Udalo sie, gdy: jest folder `C:\Sprzet_testy\narzedzia` z plikami `pole_skanu.cmd` i `ramka.cmd`. Wyniki
narzedzi zapisuja sie same w `C:\Sprzet_testy\wyniki` (kazdy wynik w osobnym pliku z data i godzina).
Zanotuj (arkusz 1.4): czy dwuklik i przeciaganie pliku dzialaja (okaze sie w krokach 2.4 i 3.3).
Gdy sie nie uda: narzedzia zakladaja, ze program jest w `C:\Stanowisko`. Jesli jest gdzie indziej - zapisz
to; pliki skanow policzymy pozniej na PC.
[NIE SPRAWDZONE BEZ SPRZETU: dwuklik i przeciaganie plikow na prawdziwym ekranie]
[DO POTWIERDZENIA NA 0.3.3: narzedzia uruchomione z nowej instalacji]

---

## Czesc 2 - skaner

Klikanie w programie skanera: wydrukowana sciaga. Tu tylko to, co dotyczy naszego programu.

### Krok 2.1 - okno "Dzien skanera" (5 minut, PRZED pierwszym skanem)

Co zrobic: kliknij dwa razy `C:\Stanowisko\Dzien_skanera.cmd` [DO POTWIERDZENIA NA 0.3.3]. Kliknij
"Dodaj folder..." i wskaz folder, do ktorego zapisuje program skanera (P5; w programie skanera to "Order
Save Path"). Nie znasz go: przycisk "Nie wiem, gdzie skaner zapisuje - szukaj". Kliknij "Zrzut ekranu
(za 3 s)" na probe.
Udalo sie, gdy: otwiera sie okno "Dzien skanera - krok po kroku", na gorze jest napis "Obserwuje:" i folder.
Zanotuj (arkusz 2.1): czy okno sie otwarlo, jaki folder obserwuje.
Gdy sie nie uda: wydrukowana karta wspomina plik `uruchom_dzien_skanera.bat` - w zainstalowanym programie go
nie ma. Gdy brak tez `Dzien_skanera.cmd`, kliknij dwa razy `C:\Sprzet_testy\narzedzia\dzien_skanera.cmd`.
Gdy okna nie ma wcale: po kazdym skanie kopiuj recznie folder zlecen programu skanera na pendrive, ekran
fotografuj telefonem i rob kroki 2.3-2.5a bez okna.
[NIE SPRAWDZONE BEZ SPRZETU: przycisk zrzutu ekranu, praca obok prawdziwego programu skanera]

### Krok 2.2 - kroki 1-4 okna: ustawienia programu skanera (15 minut)

Co zrobic: idz za instrukcja w oknie. Niczego w programie skanera nie zmieniaj.
Udalo sie, gdy: w oknie po lewej kroki 1-4 sa odhaczone albo pominiete z powodem.
Zanotuj (arkusz 2.2): format pliku skanu i czy jest JEDEN plik na cala plytke - to bardzo wazne.
Gdy sie nie uda: "Nie udalo sie / pomijam, bo ..." i jedno zdanie. Idz dalej.

### Krok 2.3 - pierwszy skan: PUSTA plytka (10 minut)

Co zrobic: wyczysc stozki plytki. Zeskanuj pusta plytke (krok 5 okna). Zmierz czas stoperem. Zapisz skan w
programie skanera jako plik STL calej plytki, bez wygladzania i obcinania.
Udalo sie, gdy: plik sam pojawia sie w oknie, a po kilkunastu sekundach okno pokazuje zielona ocene
"SKAN DOBRY: cala plytka, ...; obrys ... x ... x ... mm; ...".
Zanotuj (arkusz 2.3): czas skanu, kolor i tekst oceny, "obrys", czy w skanie widac stolik.

Gdy sie nie uda:

    Widzisz                                       Zrob
    plik sie nie pojawia                          w programie skanera szukaj "Explore" albo "Export";
                                                  w oknie "Dodaj folder..."
    czerwone "... nie widac trzech stozkow        zrob krok 2.4 na tym pliku: poda wymiar pola skanera
    znacznikow"
    czerwone "... nie widac plaskiego wierzchu"   skan zostal obciety przy zapisie; zapisz cala plytke
    inny format niz STL                           okno i tak skopiuje plik; zapisz format w arkuszu

Wazne: na skanach sztucznych program nie rozpoznaje ZADNEJ plytki, gdy pole skanera ma 90 mm albo mniej
(trzy stozki siegaja 47 mm od srodka plytki). Przy 95 mm rozpoznaje. Ponowny skan wtedy nie pomoze - to
bylby glowny wynik dnia. Druga mozliwa przyczyna czerwonej oceny: skaner zapisal razem z plytka stolik
albo uchwyt (krok 2.4 to pokaze).
[NIE SPRAWDZONE BEZ SPRZETU: prawdziwy plik ze skanera - nazwa, format, czas zapisu, szum, podloze w skanie]

### Krok 2.4 - pole skanera w liczbach (5 minut na plik)

Co zrobic: znajdz plik skanu - w folderze programu skanera albo w oknie: "Otworz folder sesji", potem
`kroki` i folder kroku. Przeciagnij go myszka na `C:\Sprzet_testy\narzedzia\pole_skanu.cmd`. Na pytanie o
numer nacisnij sam Enter. Po kilkunastu sekundach pojawi sie 6 ponumerowanych wierszy i blok
"DO ARKUSZA (przepisz):".

Co mowi wiersz 2:

- "Cala plytka jest w skanie ... pole skanera jest CO NAJMNIEJ takie jak plytka" - pole jest wieksze niz
  plytka. Zmierz je kartonem (nizej).
- "Plytka NIE jest cala w skanie" i "POLE SKANERA MA OK. ... mm" - ta liczba to srednica pola.
- "POLE NIE JEST KOLEM (albo plytka lezy z boku pola): dane najwezej ... mm x ... mm" - przepisz obie
  liczby. Przesun plytke na srodek stolika i zeskanuj jeszcze raz.

Proba z kartonem (gdy cala plytka miesci sie w polu): poloz na stoliku plaski karton wiekszy niz 15 x 15 cm,
zeskanuj, zapisz i przeciagnij plik na `pole_skanu.cmd`. Narzedzie napisze "PLYTKA NIE ROZPOZNANA" (to
dobrze - to karton) i poda wymiary danych: najwezej, w poprzek i - gdy dane sa kolem - srednice kola.

Udalo sie, gdy: masz w arkuszu wymiar pola: jedna srednice albo dwie liczby (najwezej x w poprzek).
Zanotuj (arkusz 2.4): liczby z wiersza 2; z bloku "DO ARKUSZA" wiersz `podloze w skanie:`.
Gdy sie nie uda: narzedzie pisze "w skanie jest prawdopodobnie PODLOZE (stolik / uchwyt)" - zrob zdjecie
ekranu programu skanera i zapisz to; poszukaj w programie skanera ustawienia, ktore obcina podloze. Inny
blad albo nic sie nie dzieje: skopiuj plik skanu na pendrive - policzymy go na PC.
[NIE SPRAWDZONE BEZ SPRZETU: liczby na prawdziwym skanie; proba z kartonem; skan z podlozem]

### Krok 2.5 - kolejne skany wedlug okna (ok. 1 godziny)

Co zrobic: kroki 6-13 okna. Najwazniejsze, w tej kolejnosci:

1. plytka z 6-10 pracami calymi (krok 6 okna) i TO SAMO drugi raz bez ruszania plytki (krok 7),
2. plytka z 2-3 pracami celowo ukruszonymi (krok 9) - zapisz, ktore gniazdo i gdzie ukruszenie,
3. kazdy RODZAJ plytki, jaki masz (kwadratowa, okragla ramkowa, okragla testowa, stara) - po jednym skanie
   pustej plytki. Te dodatkowe skany rob w kroku 12 okna ("Skan 7: druga plytka"); w polu notatki wpisz,
   ktora to plytka.

Kazdy plik przeciagnij na `pole_skanu.cmd` (sam Enter na pytanie o numer) i przepisz blok "DO ARKUSZA" do
tabeli 2.5.

Udalo sie, gdy: kazdy skan ma w oknie ocene, a w arkuszu wiersz w tabeli 2.5.
Zanotuj (arkusz 2.5): dla KAZDEGO skanu: jaka to plytka naprawde, co mowi program, numer z dolkow, ile
dolkow widac, czy widac scianke boczna, brzeg. Dla plytki okraglej ramkowej takze wiersz `rowek pokrywki:`
(narzedzie podaje liczby, ale samo nie rozstrzyga, czy rowek widac).
Gdy sie nie uda: ocena zolta "inna plytka niz w skanie ..." albo czerwona "TEN SAM plik" - przeczytaj tekst
po "ZROB TAK"; plik i tak jest zachowany. Skan nierozpoznany tez wpisz do tabeli.
[NIE SPRAWDZONE BEZ SPRZETU: dolki numeru (2 mm srednicy, 1 mm glebokosci), scianka boczna i rowek na
prawdziwym skanie; prace prawdziwe i ukruszone]

### Krok 2.5a - plytki okragle: czy program poznaje ksztalt (30 minut)

Po co: program poznaje plytke okragla po dolkach numeru albo po sciance bocznej. Gdy skaner nie pokaze ani
dolkow, ani scianki, program wezmie plytke okragla za KWADRATOWA i nie ostrzeze. Dla plytki okraglej
ramkowej gniazda sa te same, wiec mapa bedzie dobra. Dla plytki testowej (8, 9) program zapyta o numer i
pokaze zle gniazda. Trzeba zmierzyc, jak czesto to sie zdarza na prawdziwym skanerze.

Co zrobic: dla KAZDEJ plytki okraglej, jaka masz, zrob trzy skany (w kroku 12 okna, z notatka):

1. plytka pusta,
2. plytka z praca w gniezdzie obok dolkow numeru,
3. plytka z dolkami numeru zaklejonymi kawalkiem tasmy papierowej.

Kazdy plik przeciagnij na `pole_skanu.cmd`. Na pytanie o numer nacisnij SAM ENTER (inaczej narzedzie
podpowie programowi ksztalt). Przepisz wiersz `program mowi:`.

Udalo sie, gdy: tabela 2.5a ma wiersz dla kazdego skanu. Dobry wynik: "plytka okragla ramkowa (do ramki)"
albo "okragla testowa (poza ramka)", "PEWNIE". Zly wynik, ale bardzo wazny: "kwadratowa" dla plytki
okraglej. [DO POTWIERDZENIA NA 0.3.3: te napisy na nowej instalacji]
Zanotuj (arkusz 2.5a): program mowi (kwadratowa / okragla, pewnie / niepewnie), numer z dolkow, dolki
widac, scianka boczna; na koncu: ile razy plytka okragla zostala nazwana kwadratowa.
Gdy sie nie uda: nie masz plytek okraglych - pomin. Narzedzie nie dziala - skopiuj pliki, policzymy na PC.
[NIE SPRAWDZONE BEZ SPRZETU: caly krok; na skanach sztucznych bez scianki i bez dolkow: 4 z 4 "kwadratowa"]

### Krok 2.6 - kopia folderu i "Zakoncz i spakuj" (10 minut)

Co zrobic: ostatni krok okna ("Na koniec: kopia CALEGO folderu zlecen programu skanera"), potem "Zakoncz
i spakuj".
Udalo sie, gdy: okno pisze "Sesja spakowana: ... plikow" i podaje sciezke pliku ZIP w folderze
`C:\Stanowisko\dane\dzien_skanera\<data_godzina>\paczka\`. Lista brakow nie blokuje.
Zanotuj (arkusz 2.6): liczba plikow, nazwa pliku ZIP.
Gdy sie nie uda (np. brak miejsca): niczego nie kasuj; skopiuj caly folder z data i godzina na pendrive.
Przycisk "Pomiar szczegolowy zaznaczonego skanu": w starej paczce nie dzialal; nie jest dzis potrzebny.
[DO POTWIERDZENIA NA 0.3.3: przycisk pomiaru i folder paczek]

### Krok 2.7 - program "Stanowisko" sam zauwaza prawdziwy skan (20 minut)

Co zrobic:

1. Zamknij okno "Dzien skanera". W programie skanera zaloz NOWE zlecenie testowe (np. TEST5).
2. W `C:\Stanowisko\ustawienia.toml` w wierszu `folder_eksportu_skanera` wpisz folder tego nowego zlecenia
   (z ukosnikami `/`). Zapisz. Nie wskazuj folderu ze starymi zleceniami: program przeanalizuje takze
   stare skany, ktore juz w nim leza.
3. `C:\Stanowisko\Samokontrola.cmd` - ma byc wiersz `OK folder_skanera`.
4. `C:\Stanowisko\Stanowisko.cmd`, kliknij "Tester".
5. Zeskanuj plytke z pracami i zapisz skan. Wlacz stoper w chwili zapisu. Powtorz z plytka okragla.

Udalo sie, gdy: po lewej pojawia sie kafelek "Plytka ...", w srodku mapa gniazd. Zatrzymaj stoper.

- Plytka kwadratowa: program pyta "Podaj numer plytki" - kliknij numer wybity na plytce.
- Plytka okragla: program czyta numer sam z dolkow. Mapa jest kolem; sciecie plytki jest plaska krawedzia
  z gruba szara kreska z przodu po prawej; pod mapa napis "PRZOD PLYTKI". Gdy dolki sa nieczytelne, program
  pyta o numer. [DO POTWIERDZENIA NA 0.3.3]
- Prace bez projektu STL sa szare "bez projektu" - dzis to wystarczy.

Zanotuj (arkusz 2.7): czas od zapisu do mapy; czy program pytal o numer; ksztalt mapy; tekst komunikatu.

Gdy sie nie uda:

    Widzisz                                       Zrob
    "Analiza skanu nie powiodla sie" i w          przepisz nawias; N = 0, 1 albo 2 znaczy: plytka nie
    nawiasie "w skanie widac N z 3 znacznikow     miesci sie w polu albo lezy z boku. Ustaw ja na srodku;
    plytki - plytka nie miesci sie w polu         sprawdz plik krokiem 2.4
    skanera albo lezy poza srodkiem ..."
    "... nie widac plaskiego wierzchu plytki"     skan obciety albo to nie plytka; zapisz cala plytke
    "... skan jest prawie pusty"                  sprawdz, czy plytka lezy w skanerze
    "Plik nie jest skanem"                        plik uciety; zapisz skan jeszcze raz
    "Plytka nie z tego trybu"                     plytka poranna (4-6) wieczorem: kliknij "-> Poranek"
                                                  w pasku albo wez plytke 1-3
    nic sie nie dzieje                            plik nie konczy sie na .stl albo trafia do innego
                                                  folderu; wroc do okna "Dzien skanera" (krok 2.1)

Teksty w nawiasach: [DO POTWIERDZENIA NA 0.3.3]. Plikow skanow z tego kroku program nie kopiuje - zabierz
je sam (czesc 5, punkt 3).
[NIE SPRAWDZONE BEZ SPRZETU: jak i jak dlugo program skanera zapisuje plik, pod jaka nazwa]

---

## Czesc 3 - ramka

Wystarczy jedna ramka. Na czas krokow 3.3-3.7 i 3.9 ZAMKNIJ program "Stanowisko": ramke obsluguje jeden
program naraz.

### Krok 3.1 - ogledziny i pasowanie, BEZ pradu (15 minut)

Co zrobic: wloz kazda plytke we wkladke. Sprobuj wlozyc ja obrocona o cwierc obrotu. Zaloz pokrywke
i odwroc. Zmierz suwmiarka plytke (bok albo srednica, grubosc) i otwor wkladki.
Udalo sie, gdy: plytka wchodzi lekko i lezy plasko tylko w jednym polozeniu. Plytka okragla ramkowa
obrocona lezy krzywo na zebrze (jedna krawedz ok. 4,5 mm wyzej). Kwadratowa wchodzi tylko jedna strona
(sciety rog).
Zanotuj (arkusz 3.1): wymiary, co nie pasuje.
Gdy sie nie uda: zdjecie, wymiar do arkusza. Idz dalej.
[NIE SPRAWDZONE BEZ SPRZETU: wymiary znamy tylko z projektu]

### Krok 3.2 - wlaczenie pradu (5 minut)

Co zrobic: wloz wtyk zasilacza i wlacz stoper. Patrz na matryce diod.
Udalo sie, gdy: na brzegu matrycy pojawia sie niebieski pierscien (ramka gotowa). Plan: mniej niz 60 s.
Zanotuj (arkusz 3.2): czas do pierscienia, co widac na matrycy.
Gdy sie nie uda: matryca ciemna po 3 minutach = na karcie SD nie ma programu ramki albo nie startuje on sam
(P3). Zapisz to. Karty SD nie wyjmuj i nie nadpisuj. Zostaje krok 3.1; przejdz do czesci 2 albo 4.
[NIE SPRAWDZONE BEZ SPRZETU: start po wlaczeniu pradu, kolory, jasnosc, kierunek obrazu]

### Krok 3.3 - czy komputer widzi ramke; klucz ramki (10 minut)

Co zrobic:

1. Polacz komputer z ta sama siecia co ramka (P6).
2. Kliknij dwa razy `C:\Sprzet_testy\narzedzia\ramka.cmd`. Na pytanie o adres wpisz `ramka-w.local`
   (wieczorna) albo `ramka-p.local` (poranna). Wybierz `1` i Enter.
3. Gdy pojawi sie "RAMKA ODPOWIADA, ale wymaga klucza": menu samo zapyta o klucz (pozycja `7`). Przepisz
   klucz z kartki (P8). Po napisie "KLUCZ DOBRY ..." narzedzie pamieta klucz i wiecej nie pyta. Wybierz `1`.

Udalo sie, gdy: jest wiersz `RAMKA ODPOWIADA (... ms): ramka wieczorna (W), program ramki ...` i ponizej
`plytka na ramce: 0`.
Zanotuj (arkusz 3.3): adres (bedzie potrzebny w 3.8), czy ramka wymaga klucza, czas odpowiedzi.
Gdy sie nie uda:

- `BRAK POLACZENIA`: sprawdz, czy ramka swieci. Zamiast nazwy wpisz adres z cyfr - znajdziesz go na liscie
  urzadzen routera albo w Windows: Ustawienia -> Siec -> Hotspot mobilny. Sprawdz, czy komputer nie jest w
  innej sieci.
- "ZLY KLUCZ": przepisz klucz jeszcze raz, litera po literze. Nie znasz klucza: kroki 3.4-3.9 odpadaja;
  obejrzyj jeszcze napisy na matrycy przy kladzeniu plytek (jak w 3.5) i przejdz do czesci 2.

Klucz zapisuje sie w pliku `C:\Sprzet_testy\narzedzia\klucz_ramki.txt`. Nie trafia do wynikow.
[NIE SPRAWDZONE BEZ SPRZETU: nazwa `ramka-w.local`, Wi-Fi, adres ramki w sieci, menu z klawiatury]

### Krok 3.4 - test diod (2 minuty)

Co zrobic: w `ramka.cmd` wybierz `2`.
Udalo sie, gdy: cala matryca swieci kolejno na czerwono, zielono, niebiesko i bialo, razem 8 sekund, potem
wraca niebieski pierscien.
Zanotuj (arkusz 3.4): kolory, ciemne pola.
Gdy sie nie uda: zdjecie kazdego koloru. Idz dalej.
[NIE SPRAWDZONE BEZ SPRZETU: prawdziwa matryca]

### Krok 3.5 - odczyt numeru kazdej plytki (15 minut)

Co zrobic: w `ramka.cmd` wybierz `3`. Przez 5 minut kladz i zdejmuj plytki: kazda 5 razy. Kazda zmiana
pojawia sie na ekranie, np. `12:01:03.250  plytka 0 -> 2`, i trafia do pliku w
`C:\Sprzet_testy\wyniki\ramka\`. Koniec przed czasem: Ctrl+C.
Udalo sie, gdy: po polozeniu plytki nr 2 jest `0 -> 2`, po zdjeciu `2 -> 0`, za kazdym razem. Na matrycy
przy lezacej plytce ma byc jej numer i napis "BRAK" (ramka nie ma jeszcze wyniku - to normalne).
Zanotuj (arkusz 3.5, tabela): dla kazdej plytki: ile razy polozona, ile dobrych odczytow, zle odczyty.
Gdy sie nie uda: sprawdz, czy plytka ma magnesy i lezy plasko; zapisz numer wybity i odczytany. Magnesy:
1 = A, 2 = B, 3 = A+B, 4 = C, 5 = A+C, 6 = B+C. Idz dalej.
[NIE SPRAWDZONE BEZ SPRZETU: czujniki i magnesy, takze w plytce okraglej]

### Krok 3.6 - plytka krzywo i plytka nie od tej ramki (10 minut)

Co zrobic (dalej pozycja `3`): (a) poloz plytke obrocona, tak zeby lezala na zebrze; (b) poloz ja skosem,
jednym brzegiem; (c) poloz plytke drugiej ramki (np. nr 4 na wieczornej), jesli ja masz.
Udalo sie, gdy: dla (a) i (b) ramka czyta 0 albo nic sie nie zmienia. Dla (c) na ekranie jest dopisek
`NUMER SPOZA TEJ RAMKI`.
Zanotuj (arkusz 3.6): kazdy odczytany numer. Odczyt inny niz 0 dla (a) albo (b) jest wazny: czujnik jest
wtedy ok. 4 mm od magnesu i moze go "zlapac".
Gdy sie nie uda: zapisz, co widac, i idz dalej. Co program "Stanowisko" mowi o plytce na zlej ramce,
sprawdzisz w kroku 3.8.
[NIE SPRAWDZONE BEZ SPRZETU: (a) i (b) w calosci]

### Krok 3.7 - gniazda i diody (20 minut)

Co zrobic: poloz na ramce pusta plytke. W `ramka.cmd` wybierz `4` (wszystkie gniazda naraz). Narzedzie
wypisze, jakie rodzaje plytek zna ramka, i zapyta o rodzaj: sam Enter = plytka kwadratowa tej ramki. Dla
plytki okraglej ramkowej przepisz z listy nazwe `okragla_ramkowa_wieczorna` albo `okragla_ramkowa_poranna`
[DO POTWIERDZENIA NA 0.3.3: te nazwy na liscie]; gdy ich nie ma - sam Enter (gniazda sa w tych samych
miejscach). Przesuniecia: dwa razy sam Enter. Popatrz z gory.
Udalo sie, gdy: kazdy otwor w dnie gniazda swieci, miedzy gniazdami jest ciemno.
Zanotuj (arkusz 3.7): rodzaj plytki, przesuniecie, ile gniazd swieci dobrze. Osobno dla wkladki okraglej.
Gdy sie nie uda:

- swiatlo jest obok otworow: uruchom `4` jeszcze raz i podaj przesuniecie w diodach (1 dioda = 2,5 mm),
  np. w prawo `1`, w dol `0`. Powtarzaj, az trafi. Potem `5` (po kolei): swieci jedno gniazdo;
  Enter = dobrze, albo wpisz uwage; `k` = koniec. Dzis tylko notujemy liczby - poprawke wpisze programista.
- `NA RAMCE NIE LEZY PLYTKA TEJ RAMKI`: ramka nie czyta numeru (krok 3.5) i nie zapali gniazd. Idz do 3.8.
- "zamknij program Stanowisko": ramke trzyma inny program - zamknij go i powtorz.

[NIE SPRAWDZONE BEZ SPRZETU: polozenie diod pod gniazdami - policzone z rysunku, takze dla wkladki okraglej]

### Krok 3.8 - program "Stanowisko" razem z ramka (25 minut)

Co zrobic:

1. Zamknij `ramka.cmd` (wybierz `0`). W `C:\Stanowisko\ustawienia.toml` znajdz (Ctrl+F) `[ramki]` i zmien
   dwa wiersze - adres z kroku 3.3 i klucz z kartki (dla ramki porannej wiersz `poranna_host`):

       wieczorna_host = "ramka-w.local"     ->   wieczorna_host = "<adres-IP>"
       klucz = ""                           ->   klucz = "tu-klucz-z-kartki"

   Zapisz. Ramka bez klucza: wiersz `klucz` zostaw bez zmian. [DO POTWIERDZENIA NA 0.3.3]
2. `C:\Stanowisko\Samokontrola.cmd` - ma byc wiersz `OK ramka_wieczorna: ramka wieczorna odpowiada`.
3. `C:\Stanowisko\Stanowisko.cmd`, kliknij "Tester". W pasku u gory: "Ramki: W: gotowa".
4. Poloz plytke na ramce: w pasku "W: gotowa (plytka 1)". Kliknij "Test LED".
5. Zeskanuj plytke z pracami (jak w 2.7) i poloz TE plytke na ramce. Powtorz z plytka okragla ramkowa.
6. Proby celowe: (a) poloz na ramce plytke drugiej ramki; (b) poloz inna plytke niz zeskanowana; (c) przy
   plytce kwadratowej podaj inny numer niz wybity.

Udalo sie, gdy: pod plytka swieca gniazda z pracami, w kolorach jak na mapie na ekranie - takze pod plytka
okragla ramkowa [DO POTWIERDZENIA NA 0.3.3]. Po zdjeciu plytki gasna; wieczorem po zdjeciu wynik nie wraca
- trzeba nowego skanu. W probach celowych ramka NIE swieci, a nad mapa jest zolty panel
[DO POTWIERDZENIA NA 0.3.3]:

- (a) "Plytka lezy na zlej ramce": "Na ramce wieczornej lezy plytka nr 5, a ta ramka podswietla tylko
  plytki 1, 2, 3 - ramka nie swieci. ..."
- (b) "Na ramce lezy inna plytka niz zeskanowana": "Na ramce wieczornej lezy plytka nr 2, a ostatni skan to
  plytka nr 1 - ramka nie swieci. Poloz na ramce plytke nr 1. ..."
- (c) "Numer plytki nie zgadza sie ze skanem": "Podany numer plytki to 2, a program odczytal ze skanu
  numer 1. Ramka nie podswietla tej plytki; skan i wynik zostaja. ..." - popraw przyciskiem "Zmien numer".

Zanotuj (arkusz 3.8): czy gniazda swieca w kolorach mapy; ktore komunikaty widziales i ile razy; kazdy
komunikat, ktory pojawil sie BEZ proby celowej (przepisz tekst).
Gdy sie nie uda: w pasku "brak polaczenia" - sprawdz adres i klucz w ustawieniach; zamknij `ramka.cmd`.
Ramka ciemna bez komunikatu - zapisz numer plytki i co jest w pasku; zrob zdjecie ekranu.
[NIE SPRAWDZONE BEZ SPRZETU: prawdziwa siec i ramka; jak czesto komunikat (b) pojawia sie w zwyklej pracy]

### Krok 3.9 - klawiatura ramki porannej (10 minut, tylko ramka poranna)

Co zrobic: poloz na ramce plytke 4, 5 albo 6. W `ramka.cmd` wybierz `6`. Naciskaj na klawiaturze ramki po
kolei: Enter; Backspace; 2 2 2 2 Enter; 9 Enter; gwiazdka, potem Enter.
Udalo sie, gdy: po kazdym kroku na ekranie komputera pojawia sie wiersz (np. "Enter: kuweta potwierdzona
1111"), a na koncu "rodzaje: 5 z 5".
Zanotuj (arkusz 3.9): ile rodzajow z 5, ktore klawisze nie dzialaja.
Gdy sie nie uda: baterie, odbiornik USB w ramce, NumLock. Idz dalej.
[NIE SPRAWDZONE BEZ SPRZETU: prawdziwa klawiatura]

---

## Czesc 4 - laptop stanowiska (tylko gdy testy sa na laptopie firmowym)

- **4.1** Po krokach 2.7 i 3.8 nacisnij Windows + R, wpisz `cmd` i Enter. W czarnym oknie wpisz:

      findstr /c:"KnownDlls" /c:"proces silnika" C:\Stanowisko\dane\logi\stanowisko.log

  To sprawdza, czy program analizy nie przerywal pracy. Policz wiersze. Ma byc 0 (nic sie nie wypisuje).
- **4.2** Czas analizy plytki: przepisz czasy ze stopera z kroku 2.7 (pierwsza plytka po starcie programu
  i kolejne). Plan: do 40 s.
- **4.3** Skalowanie ekranu: Ustawienia -> System -> Ekran. Zapisz procent i rozdzielczosc. Czy w programie
  widac wszystkie przyciski?
- **4.4** Czy folder OneDrive "Cyrkon" jest na tym laptopie? Zapisz sciezke.
- **4.5** Wolne miejsce na dysku.

Gdy cos sie nie uda: zapisz i idz dalej - to sa tylko odczyty. Arkusz: czesc 4.
[NIE SPRAWDZONE BEZ SPRZETU: wszystko w tej czesci]

---

## Czesc 5 - co przywiezc i gdzie polozyc

Skopiuj na pendrive. Na komputerze testowym nic nie kasuj, dopoki odbior nie zostanie potwierdzony.

1. Paczki okna "Dzien skanera": wszystkie pliki ZIP z
   `C:\Stanowisko\dane\dzien_skanera\<data_godzina>\paczka\`.
2. Wyniki narzedzi: caly folder `C:\Sprzet_testy\wyniki` (`pole_skanu` i `ramka`).
3. Skany z krokow 2.7 i 3.8: caly folder zlecenia testowego z programu skanera - ten, ktory wpisales w
   `folder_eksportu_skanera`. Program "Stanowisko" tych plikow nie kopiuje. Gdy pokazal "Analiza skanu nie
   powiodla sie", ten plik jest jedynym dowodem.
4. Z programu: foldery `C:\Stanowisko\dane\logi` i `C:\Stanowisko\dane\wyniki`, pliki
   `C:\Stanowisko\ustawienia.toml` i `C:\Stanowisko\dziennik_instalacji.txt`.
5. Zdjecia z telefonu: ramka z plytka, diody pod gniazdami, plytka na zebrze, ekran z kazdym bledem (bez
   twarzy, bez kart zlecen).
6. Wypelniony arkusz (kartki albo zdjecia kartek).

Na PC poloz to w folderze `<PC-katalog>\sprzet_2026-11-28\`:

    skaner\          <- punkt 1        program\   <- punkt 4
    wyniki\          <- punkt 2        zdjecia\   <- punkt 5
    skany_program\   <- punkt 3        arkusz\    <- punkt 6

Gdy nie mozesz tam zapisac: zostaw pendrive i powiedz o tym sesji prowadzacej projekt.

Czego NIE przywozic: folderu z projektami STL (nazwy plikow moga zawierac nazwiska), zlecen z danymi
pacjentow, pliku bazy programu. Przed skopiowaniem przejrzyj nazwy plikow i folderow: bez nazwisk. Plik
`ustawienia.toml` zawiera klucz ramki - nie wysylaj go nikomu poczta.

---

## Zbiorcza lista: czego NIE sprawdzono bez sprzetu

Skaner:

1. Format, nazwa i liczba plikow skanu; czy jest jeden plik calej plytki; jak dlugo program skanera
   zapisuje plik (2.2, 2.3, 2.7).
2. Wymiar i ksztalt pola skanera (projekt zaklada 100 mm) i polozenie plytki w polu (2.4).
3. Czy w skanie jest stolik albo uchwyt i czy program rozpoznaje wtedy plytke (2.3, 2.4).
4. Czy skaner widzi dolki numeru (ok. 43,5 mm od srodka plytki okraglej; 52-58 mm na kwadratowej) i trzy
   stozki (do 47 mm od srodka) (2.3-2.5).
5. Czy skaner widzi scianke boczna plytki i rowek pokrywki (2.5).
6. Jak czesto plytka okragla jest brana za kwadratowa (2.5a).
7. Szum, czas skanu; wynik dla prac prawdziwych i ukruszonych (2.5).
8. Przycisk zrzutu ekranu; nasz program obok programu skanera na jednym komputerze (2.1).

Ramka:

9. Raspberry Pi: karta SD, instalacja programu ramki, start po wlaczeniu pradu, czas startu (3.2).
10. Matryca diod: kolory, jasnosc, kierunek obrazu (3.4).
11. Czujniki i magnesy: odczyt kazdego numeru, plytka krzywo na zebrze, plytka skosem (3.5, 3.6).
12. Polozenie diod pod gniazdami, takze pod wkladka okragla (3.7).
13. Siec: nazwa `ramka-w.local`, Wi-Fi w pracowni, hotspot, zapora Windows; klucz ramki przepisany recznie
    (3.3, 3.8).
14. Komunikaty programu o plytce na ramce w zwyklej pracy (3.8).
15. Klawiatura numeryczna (3.9); pasowanie plytek, wkladki i pokrywki (3.1).

Komputer:

16. Instalacja na laptopie firmowym: antywirus, uprawnienia, ostrzezenia Windows, Notatnik (1.1, 1.2).
17. Dwuklik plikow `.cmd`, przeciaganie pliku na `pole_skanu.cmd`, menu `ramka.cmd` z klawiatury (1.4).
18. Wyglad okien przy skalowaniu ekranu 125 / 150 %; czas analizy na wolniejszym laptopie (1.3, czesc 4).

Wiecej (program ramki na Raspberry Pi w skrocie, nazwy uzywane przez program, co i jak sprawdzono na
danych sztucznych): plik `ZALACZNIKI.md`.
