# Pierwsze testy na prawdziwym sprzecie - 28-29.11.2026

Dokument dla wlasciciela. Wydrukuj go razem z `ARKUSZ_OBSERWACJI.md`. Stan: 21.11.2026, dla paczki
programu 0.3.3 (jeszcze nie istnieje).

Do tej pory program byl sprawdzany tylko na danych sztucznych i na "atrapach" (program udaje ramke albo
skaner). Cel weekendu: zebrac liczby i pliki, ktorych nie da sie zdobyc bez sprzetu. Nie wszystko musi
zadzialac. Co pojdzie inaczej niz tu napisano, jest wynikiem - zapisz to.

Znaczniki:

- **[NIE SPRAWDZONE BEZ SPRZETU]** - tego nikt nie widzial na prawdziwym urzadzeniu. Moze pojsc inaczej.
- **[DO POTWIERDZENIA NA 0.3.3]** - opis wedlug raportow programistow; bedzie sprawdzony na nowej paczce
  przed weekendem. Gdyby wygladalo to inaczej - zapisz, co widzisz.

Zasady:

1. W programie skanera niczego nie kasuj.
2. Zadnych nazwisk pacjentow: zlecenia nazywaj TEST1, TEST2 i trzymaj je w osobnym folderze testowym
   (P9). Bierz prace probne albo odrzuty.
3. Krok nie udaje sie dluzej niz 15 minut? Zdjecie ekranu telefonem, notatka i dalej.
4. Mozna zrobic sam skaner (czesc 2) bez ramki i sama ramke (czesc 3) bez skanera. Jedna ramka wystarcza.

---

## 0. Pytania do wlasciciela - odpowiedz najpozniej do srody 25.11.2026

Nie znamy odpowiedzi i nie zgadujemy. Te same pytania na jednej stronie, z miejscem na odpowiedz, sa
w pliku `PYTANIA_DO_WLASCICIELA.md` - odpowiedz tam albo przekaz sesji prowadzacej projekt.
Najpilniejsze: P3, P1, P6, P8 - od nich zalezy, co trzeba przygotowac PRZED weekendem.

**P3. Czy Raspberry Pi w ramce jest zlozone z matryca diod i czujnikami, ma karte SD i czy ktos wgral na nia
"program ramki"?**
- Wgrany: cala czesc 3 do zrobienia.
- Nie albo nie wiesz: ktos musi go wgrac PRZED sobota wedlug instrukcji `ramka_raspberry_pi.md` (12 krokow,
  kilka godzin; skrot w `ZALACZNIKI.md`). Inaczej z czesci 3 zostaje tylko krok 3.1. Napisz, kto i kiedy.

**P1. Ktora ramka przyszla: wieczorna, poranna czy obie? Wkladka kwadratowa czy okragla?**
- Wieczorna: plytki 1-3, adres `ramka-w.local`; krok 3.9 odpada.
- Poranna: plytki 4-6, adres `ramka-p.local`; dochodzi krok 3.9 (klawiatura).
- Wkladka okragla: w kroku 3.7 wybierasz plytke okragla ramkowa.

**P6. Jaka siec laczy komputer z ramka (router, hotspot)? Jaka siec Wi-Fi jest wpisana w ramce?**
- Komputer i ramka musza byc w TEJ SAMEJ sieci. Nie wiesz, jaka siec jest w ramce: krok 3.3 moze sie nie
  udac; wtedy z czesci 3 zostaja kroki 3.1 i 3.2.

**P8. Czy ramka ma ustawiony "klucz" (haslo ramki) i czy go znasz?** Program ramki wgrany skryptem z
naszej paczki losuje klucz i zapisuje go w pliku ustawien ramki (zna go osoba, ktora wgrywala program).
- Znasz: przywiez go na kartce (kroki 3.3 i 3.8). Dwie ramki musza miec TEN SAM klucz.
- Nie znasz, a ramka go wymaga: kroki 3.4-3.9 odpadaja, dopoki klucza nie odczyta osoba, ktora wgrywala
  program. Krok 3.3 pokaze, czy ramka wymaga klucza.

**P2. Ktore plytki sa na miejscu i czy maja wklejone magnesy?** Kwadratowe (1-6), okragle ramkowe (1-6),
okragle testowe (8, 9), stare R54.
- Od tego zalezy, co skanujesz w krokach 2.3-2.5a. Bez plytek okraglych krok 2.5a odpada.
- Plytki bez magnesow: krok 3.5 odpada, ramka pod nimi nie zaswieci.

**P4. Na jakim komputerze uruchomisz program?** Windows 10 albo 11, 30 GB wolnego miejsca.
- Laptop stanowiska: dochodzi czesc 4. Inny komputer: czesc 4 odpada.

**P5. Czy skaner stoi przy tym samym komputerze? Do jakiego folderu program skanera zapisuje skany?**
- Przy innym: instalujesz nasz program takze tam (kroki 1.1-1.4) albo przenosisz pliki skanow pendrivem.
  Wtedy krok 2.7 odpada, a 2.4 i 2.5a robisz na przeniesionych plikach.

**P7. Czy masz projekty STL (z exocad) prac probnych?**
- Masz: w kroku 2.7 program porowna prace z projektem. Nie masz: prace beda szare "bez projektu".

**P9. Czy w programie skanera sa juz zlecenia pacjentow? Gdzie mozna zalozyc osobny folder na skany
testowe z tego dnia?**
- Sa (albo nie wiesz): skany testowe ida do osobnego folderu (krok 2.1), a kopie calego folderu zlecen
  (krok 2.6) pomijasz - dane pacjentow nie moga wyjechac z laboratorium.
- Nie ma: krok 2.6 robisz w calosci.

---

## 1. Co przygotowac i zabrac

Pendrive (co najmniej 16 GB):

- [ ] paczka programu `Stanowisko_0.3.3.zip` [DO POTWIERDZENIA NA 0.3.3]
- [ ] instalator Pythona 3.12.10 dla Windows (64-bit) z python.org: `python-3.12.10-amd64.exe`
- [ ] folder `testy_sprzet_2026-11-28` (ten dokument, arkusz, podfolder `narzedzia`)
- [ ] 2-3 projekty STL prac probnych, bez nazwisk w nazwach plikow (P7)

Wydruki: [ ] ten dokument, [ ] arkusz, [ ] karta "Dzien skanera" i sciaga programu skanera (dostaniesz je
razem z tym dokumentem), [ ] kartka z kluczem ramki (P8).

Sprzet:

- [ ] ramka, zasilacz 5 V 4 A; klawiatura numeryczna z odbiornikiem (ramka poranna)
- [ ] wszystkie plytki, pokrywka, zapasowe magnesy
- [ ] 6-10 prac probnych albo odrzutow, 2-3 do celowego ukruszenia
- [ ] suwmiarka, telefon (stoper, zdjecia), dlugopis, tasma papierowa (krok 2.5a)
- [ ] plaski karton wiekszy niz 15 x 15 cm (krok 2.4); sciereczka i pedzelek do stozkow plytek
- [ ] dostep do routera albo telefon z hotspotem (P6)

---

## 2. Skrot dnia

    Czesc 1  komputer i program        ok. 40 min    kroki 1.1 - 1.4
    Czesc 2  skaner                    ok. 2,5 godz. kroki 2.1 - 2.7
    Czesc 3  ramka (jedna wystarczy)   ok. 2 godz.   kroki 3.1 - 3.9
    Czesc 4  laptop stanowiska         ok. 20 min    tylko na laptopie
    Czesc 5  zebranie plikow           ok. 20 min

Cztery najwazniejsze wyniki: (1) wymiar pola skanera - krok 2.4; (2) czy program poznaje plytke okragla,
gdy nie widzi dolkow numeru - krok 2.5a; (3) czy ramka czyta numer kazdej plytki - krok 3.5; (4) czy diody
trafiaja pod gniazda - krok 3.7.

---

## Czesc 1 - komputer i program

### Krok 1.1 - Python 3.12 (5 minut)

Co zrobic: uruchom z pendrive'a `python-3.12.10-amd64.exe`, opcje domyslne, "Install Now".
Udalo sie, gdy: instalator konczy sie napisem "Setup was successful". Zanotuj: arkusz 1.1.
Gdy sie nie uda: zapisz komunikat. Zostaja kroki 3.1, 3.2 i skany zapisywane recznie.
[NIE SPRAWDZONE BEZ SPRZETU: instalator Pythona na obcym komputerze]

### Krok 1.2 - instalacja programu z paczki (10-15 minut)

Co zrobic:

1. Skopiuj `Stanowisko_0.3.3.zip` do `C:\Paczki`. Prawy klawisz -> "Wyodrebnij wszystkie".
2. Zaloz dwa puste foldery: `C:\Stanowisko_test\skany` i `C:\Stanowisko_test\projekty` (tu skopiuj
   projekty STL, jesli je masz).
3. W rozpakowanym folderze kliknij dwa razy `zainstaluj.cmd` (ok. 1 minuty). Pierwszy raz czarne okno
   konczy sie wierszem:

       INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom zainstaluj.cmd ponownie (kod 10)

   To NIE jest blad. Program nie zna jeszcze folderow tego komputera.
4. Otworz `C:\Stanowisko\ustawienia.toml`: prawy klawisz -> "Otworz za pomoca" -> Notatnik. Szukaj przez
   Ctrl+F. Zmien TRZY wiersze (ukosniki w prawo `/`):

       folder_eksportu_skanera = "C:/Stanowisko_test/skany"
       folder_cyrkon = "C:/Stanowisko_test/projekty"
       operatorzy = ["Tester"]

   Zapisz. Kodowania nie zmieniaj; gdyby Notatnik pytal: "UTF-8", NIE "UTF-8 z BOM".
5. Kliknij dwa razy `zainstaluj.cmd` JESZCZE RAZ (kilka sekund).

Udalo sie, gdy: ostatni wiersz to `INSTALACJA: GOTOWA - wersja biezaca ...`, a w `C:\Stanowisko` sa pliki
`Stanowisko.cmd`, `Samokontrola.cmd`, `Polecenie.cmd`, `Dzien_skanera.cmd`. [DO POTWIERDZENIA NA 0.3.3]
Zanotuj: arkusz 1.2.
Gdy sie nie uda: przepisz wiersze `BLAD:` i `CO ZROBIC:` i zrob to, co mowi `CO ZROBIC`. Windows pyta "Czy
chcesz uruchomic ten plik?" - zezwol. Bez instalacji przejdz do kroku 3.1.
[NIE SPRAWDZONE BEZ SPRZETU: laptop firmowy - antywirus, uprawnienia, Notatnik]

### Krok 1.3 - samokontrola i pierwszy start (5 minut)

Co zrobic: kliknij dwa razy `C:\Stanowisko\Samokontrola.cmd`. Potem `C:\Stanowisko\Stanowisko.cmd`; na
pytanie "Kto teraz pracuje?" kliknij "Tester". Popatrz na pasek u gory i zamknij okno.
Udalo sie, gdy: samokontrola konczy sie wierszem `SAMOKONTROLA: ZIELONA` i ma wiersz
`OK modele: uklady plytek z [plytki]: poprawne 10 z 10` [DO POTWIERDZENIA NA 0.3.3]. Wiersze `OSTRZEZENIE`
(ramki, `excel`, `baza`, `pula`) sa teraz normalne. W pasku programu: "Folder skanera: dostepny" i
"Ramki: W: brak polaczenia". Zanotuj: arkusz 1.3.
Gdy sie nie uda: "poprawne 8 z 10" albo "9 z 10" = stara albo niepelna paczka. Przepisz wiersz `BLAD: ...`.
Mozesz isc do czesci 2.
[NIE SPRAWDZONE BEZ SPRZETU: wyglad okna na ekranie laptopa]

### Krok 1.4 - narzedzia dnia sprzetu (2 minuty)

Co zrobic: skopiuj z pendrive'a folder `testy_sprzet_2026-11-28` na dysk jako `C:\Sprzet_testy`.
Udalo sie, gdy: jest folder `C:\Sprzet_testy\narzedzia` z plikami `pole_skanu.cmd` i `ramka.cmd`. Wyniki
zapisuja sie same w `C:\Sprzet_testy\wyniki`, kazdy w osobnym pliku z data i godzina.
Zanotuj: arkusz 1.4 (czy dwuklik i przeciaganie pliku dzialaja - okaze sie w krokach 2.4 i 3.3).
Gdy sie nie uda: kopiuj pliki skanow na pendrive - policzymy je na PC.
[NIE SPRAWDZONE BEZ SPRZETU: dwuklik i przeciaganie na prawdziwym ekranie]
[DO POTWIERDZENIA NA 0.3.3: narzedzia uruchomione z nowej instalacji]

---

## Czesc 2 - skaner

Klikanie w programie skanera: wydrukowana sciaga. Tu tylko to, co dotyczy naszego programu.

### Krok 2.1 - okno "Dzien skanera" (5 minut, PRZED pierwszym skanem)

Co zrobic: kliknij dwa razy `C:\Stanowisko\Dzien_skanera.cmd` [DO POTWIERDZENIA NA 0.3.3]. Kliknij "Dodaj
folder..." i wskaz folder, do ktorego program skanera zapisze skany TESTOWE (P5, P9). Sa w nim zlecenia
pacjentow: ustaw w programie skanera osobny folder zapisu na ten dzien, a gdy sie nie da - wskaz oknu
tylko folder zlecenia TEST1, nigdy caly folder zlecen. Nie znasz folderu: "Nie wiem, gdzie skaner
zapisuje - szukaj". Kliknij na probe "Zrzut ekranu (za 3 s)".
Udalo sie, gdy: otwiera sie okno "Dzien skanera - krok po kroku", na gorze napis "Obserwuje:" i folder.
Zanotuj: arkusz 2.1.
Gdy sie nie uda: brak `Dzien_skanera.cmd` - uzyj `C:\Sprzet_testy\narzedzia\dzien_skanera.cmd` (pliku
`uruchom_dzien_skanera.bat` z wydrukowanej karty nie szukaj). Okna nie ma wcale: po kazdym skanie kopiuj
folder zlecen programu skanera na pendrive; kroki 2.3-2.5a rob bez okna.
[NIE SPRAWDZONE BEZ SPRZETU: zrzut ekranu; praca obok programu skanera; osobny folder zapisu w nim]

### Krok 2.2 - kroki 1-4 okna: ustawienia programu skanera (15 minut)

Co zrobic: idz za instrukcja w oknie. Niczego w programie skanera nie zmieniaj.
Udalo sie, gdy: kroki 1-4 po lewej sa odhaczone albo pominiete z powodem.
Zanotuj: arkusz 2.2 - format pliku skanu i czy jest JEDEN plik na cala plytke (bardzo wazne).
Gdy sie nie uda: "Nie udalo sie / pomijam, bo ..." i jedno zdanie. Idz dalej.
[NIE SPRAWDZONE BEZ SPRZETU: ustawienia prawdziwego programu skanera]

### Krok 2.3 - pierwszy skan: PUSTA plytka (15 minut)

Co zrobic: wyczysc stozki plytki. W oknie kamery programu skanera ustaw linie wysokosci ciecia POWYZEJ
stolika i co najmniej 3 mm PONIZEJ wierzchu plytki. Zeskanuj pusta plytke (krok 5 okna), zmierz czas
stoperem. Zapisz skan jako plik STL calej plytki, bez wygladzania. Wierzchu plytki nie obcinaj; stolik
i podstawke odetnij (linia ciecia przed skanem albo plaszczyzna ciecia, "cutting plane", po skanie).
W tej sprawie obowiazuje ten dokument, nie sciaga skanera ("najlepiej ponizej calej plytki" - nieaktualne).
Udalo sie, gdy: plik sam pojawia sie w oknie, a po kilkunastu sekundach jest zielona ocena "SKAN DOBRY:
cala plytka, ...; obrys ... x ... x ... mm; ...". Zanotuj: arkusz 2.3.
Gdy sie nie uda:

    Widzisz                                  Zrob
    plik sie nie pojawia                     w programie skanera "Explore" albo "Export";
                                             w oknie "Dodaj folder..."
    czerwone "... nie widac trzech           NAJPIERW popatrz na podglad skanu: wokol plytki widac
    stozkow znacznikow (znaleziono 0)"       plaski stolik albo podstawke? To SKAN Z PODLOZEM (nizej).
                                             Nie widac: zrob krok 2.4 - poda wymiar pola
    czerwone "... nie widac plaskiego        skan obciety za wysoko: opusc linie ciecia (3 mm
    wierzchu plytki"                         ponizej wierzchu) i zapisz cala plytke

SKAN Z PODLOZEM - najwieksze ryzyko dnia. Gdy w skanie jest plaski stolik wokol plytki (w naszych probach
bez skanera: 15 cm i wiecej), program nie rozpoznaje plytki: KAZDY skan jest czerwony, a komunikaty mowia
o polu skanera i brudnych stozkach. To zla przyczyna - czyszczenie i ponowny skan nie pomoga.

- Jak rozpoznac: w podgladzie skanu widac plaska plaszczyzne wokol plytki; `pole_skanu.cmd` (krok 2.4)
  pisze "UWAGA: w skanie jest prawdopodobnie PODLOZE".
- Jak obejsc: podnies linie albo plaszczyzne ciecia powyzej stolika. Zrob DWA skany tej samej plytki:
  (A) ciecie tuz nad stolikiem - scianka boczna plytki zostaje w skanie; (B) ciecie 3 mm pod wierzchem
  plytki. Oba pliki sprawdz krokiem 2.4 i wpisz do arkusza 2.3. Dalej skanuj tak, jak w skanie zielonym
  (oba zielone: jak A).

Inna przyczyna czerwonej oceny: pole skanera. W naszych probach bez skanera przy polu 90 mm i mniejszym
program nie rozpoznaje ZADNEJ plytki (przy 95 mm rozpoznaje); ponowny skan nie pomoze.
[NIE SPRAWDZONE BEZ SPRZETU: prawdziwy plik ze skanera - nazwa, format, czas zapisu, szum; czy stolik
trafia do skanu; czy linie ciecia da sie ustawic miedzy stolikiem a wierzchem plytki; skany A i B]

### Krok 2.4 - pole skanera w liczbach (15 minut)

Co zrobic:

1. NAJPIERW karton - to glowny pomiar pola. Poloz na stoliku plaski karton wiekszy niz 15 x 15 cm
   (wiekszy niz pole), linie ciecia opusc pod karton (karton zaslania stolik), zeskanuj i zapisz.
   Przeciagnij plik myszka na `C:\Sprzet_testy\narzedzia\pole_skanu.cmd`. Pytanie o numer: sam Enter.
   Pytanie "Co lezy na stoliku?": wpisz `karton`. Narzedzie napisze "PLYTKA NIE ROZPOZNANA" (to dobrze -
   to karton), a w wierszu 2 wymiar pola: "Dane mieszcza sie w kole o srednicy ok. ... mm" albo "DANE
   NIE SA KOLEM: ... x ... mm" (przepisz OBIE liczby) i zdanie "Dane sa PLASKIE: to plaski arkusz ...".
2. Potem plik skanu plytki z kroku 2.3 (folder programu skanera albo w oknie "Otworz folder sesji" ->
   `kroki`) - pomiar pomocniczy, przyblizony (w naszych probach blad do 5 mm). Pojawi sie 6
   ponumerowanych wierszy i blok "DO ARKUSZA (przepisz):". Wiersz 2 mowi jedno z czterech:
   - "Cala plytka jest w skanie ... pole skanera jest CO NAJMNIEJ takie jak plytka";
   - "POLE SKANERA MA OK. ... mm" - srednica pola liczona z plytki;
   - "POLE NIE JEST KOLEM (albo plytka lezy z boku pola): dane najwezej ... mm x ... mm", czasem z
     dopiskiem "Konce danych pasuja do okregu o srednicy ok. ... mm" - przepisz liczby;
   - "Skan konczy sie tuz przy brzegu plytki ...: wielkosci pola z tego skanu nie da sie podac".

   Przy kazdym z czterech liczy sie wynik z kartonu.

Udalo sie, gdy: masz wymiar pola z kartonu: jedna srednice albo dwie liczby (najwezej x w poprzek).
Zanotuj: arkusz 2.4.
Gdy sie nie uda: przy skanie PLYTKI narzedzie pisze "UWAGA: w skanie jest prawdopodobnie PODLOZE" - to
skan z podlozem, wroc do kroku 2.3. Przy kartonie taka uwage pomin. Inny blad: zabierz plik skanu.
[NIE SPRAWDZONE BEZ SPRZETU: liczby na prawdziwym skanie; skan kartonu; skan z podlozem]

### Krok 2.5 - kolejne skany wedlug okna (ok. 1 godziny)

Co zrobic: kroki 6-13 okna. Najwazniejsze, w tej kolejnosci:

1. plytka z 6-10 pracami calymi (krok 6 okna) i TO SAMO drugi raz bez ruszania plytki (krok 7),
2. plytka z 2-3 pracami celowo ukruszonymi (krok 9) - zapisz, ktore gniazdo i gdzie ukruszenie,
3. kazdy RODZAJ plytki, jaki masz (kwadratowa, okragla ramkowa, okragla testowa, stara) - po jednym skanie
   pustej. Te skany rob w kroku 12 okna ("Skan 7: druga plytka"); w notatce wpisz, ktora to plytka.

Kazdy plik przeciagnij na `pole_skanu.cmd`: numer - sam Enter; "Co lezy na stoliku?" - wpisz, jaka plytka
NAPRAWDE lezy i co na niej jest (np. `kw 2, 8 prac`). Blok "DO ARKUSZA" i godzine z wiersza "Zapisano:"
przepisz do tabeli 2.5 - po godzinie znajdziemy potem plik wyniku.

Udalo sie, gdy: kazdy skan ma w oknie ocene, a w arkuszu wiersz w tabeli 2.5.
Zanotuj: arkusz 2.5, dla KAZDEGO skanu. Wiersz `rowek pokrywki:` podaje liczby, ale nie rozstrzyga -
przepisz je.
Gdy sie nie uda: ocena zolta "inna plytka niz w skanie ..." albo czerwona "TEN SAM plik" - przeczytaj tekst
po "ZROB TAK". Skan nierozpoznany tez wpisz do tabeli.
[NIE SPRAWDZONE BEZ SPRZETU: dolki numeru, scianka boczna i rowek na prawdziwym skanie; prace ukruszone]

### Krok 2.5a - plytki okragle: czy program poznaje ksztalt (ok. 50 minut)

Po co: program poznaje plytke okragla po dolkach numeru albo po sciance bocznej. Gdy w skanie nie ma ani
jednego, ani drugiego, bierze ja za KWADRATOWA i nie ostrzega (plytka ramkowa: mapa gniazd i tak dobra;
testowa 8, 9: zle gniazda). Trzeba zmierzyc, jak czesto to sie zdarza na prawdziwym skanerze.

Co zrobic: plytke okragla zeskanuj trzy razy (krok 12 okna, z notatka): (i) pusta; (ii) z praca
w gniezdzie obok dolkow numeru; (iii) z dolkami zaklejonymi tasma papierowa. Kazdy plik przeciagnij na
`pole_skanu.cmd`; numer - SAM ENTER (podany numer podpowiada programowi ksztalt); "Co lezy na stoliku?" -
np. `okr-ramk 2, dolki zaklejone`.
Ile: jeden skan z zapisem i narzedziem to ok. 7 minut. Minimum (ok. 50 minut): 1 plytka okragla ramkowa
i 1 okragla testowa po 3 skany + 1 kwadratowa pusta dla porownania = 7 skanow. Wszystkie plytki okragle
(do 8 sztuk = 24 skany, prawie 3 godziny) tylko, gdy zostanie czas.
Udalo sie, gdy: tabela 2.5a ma wiersz dla kazdego skanu. Dobry wynik w wierszu `program mowi:` to
"okragla ramkowa (do ramki)" albo "okragla testowa (poza ramka)". Wynik zly, ale bardzo wazny: "kwadratowa"
- przy (i) albo (ii) znaczy, ze skaner nie widzi ani dolkow, ani scianki; tylko przy (iii) - ze jedyna
ochrona jest numer z dolkow.
Zanotuj: arkusz 2.5a; na koncu: ile razy plytka okragla zostala nazwana kwadratowa.
Gdy sie nie uda: nie masz plytek okraglych - pomin. Narzedzie nie dziala - zabierz pliki skanow.
[NIE SPRAWDZONE BEZ SPRZETU: caly krok, takze czas; w naszych probach bez skanera plytka bez scianki
i dolkow: 4 z 4 "kwadratowa"]

### Krok 2.6 - "Zakoncz i spakuj" (10 minut)

UWAGA - dane pacjentow: plik ZIP z tego kroku wyjezdza z laboratorium. Nie moze w nim byc zadnego
zlecenia pacjenta.

Co zrobic: ostatni krok okna ("Na koniec: kopia CALEGO folderu zlecen programu skanera") zrob TYLKO, gdy
w tym folderze sa wylacznie zlecenia testowe z tego dnia (P9). Sa tam zlecenia pacjentow albo nie masz
pewnosci: kliknij "Nie udalo sie / pomijam, bo ..." i wpisz `dane pacjentow` - skany z tego dnia sa juz
w sesji. Potem "Zakoncz i spakuj". Przycisku "Pomiar szczegolowy zaznaczonego skanu" dzis nie potrzebujesz.
Udalo sie, gdy: okno pisze "Sesja spakowana: ... plikow" i podaje plik ZIP w folderze
`C:\Stanowisko\dane\dzien_skanera\<data_godzina>\paczka\` [DO POTWIERDZENIA NA 0.3.3]. Zanotuj: arkusz 2.6.
Gdy sie nie uda (np. brak miejsca): niczego nie kasuj; skopiuj caly folder z data i godzina na pendrive.
[NIE SPRAWDZONE BEZ SPRZETU: kopia prawdziwego folderu zlecen - rozmiar, czas, pliki otwarte w skanerze]

### Krok 2.7 - program "Stanowisko" sam zauwaza prawdziwy skan (20 minut)

Co zrobic:

1. Zamknij okno "Dzien skanera". W programie skanera zaloz NOWE zlecenie testowe (np. TEST5).
2. W `C:\Stanowisko\ustawienia.toml`, w wierszu `folder_eksportu_skanera`, wpisz folder tego zlecenia
   (ukosniki `/`). Nie wskazuj folderu ze starymi zleceniami: program przeanalizuje takze stare skany.
3. `C:\Stanowisko\Samokontrola.cmd` - ma byc wiersz `OK folder_skanera`.
4. `C:\Stanowisko\Stanowisko.cmd`, kliknij "Tester".
5. Zeskanuj plytke z pracami i zapisz skan; wlacz stoper w chwili zapisu. Powtorz z plytka okragla
   o INNYM numerze (ten sam numer: program zapyta "Ponowny skan tej samej plytki?" - krok 3.8 p. 8).

Udalo sie, gdy: po lewej pojawia sie kafelek "Plytka ...", w srodku mapa gniazd (zatrzymaj stoper).
Program pyta "Podaj numer plytki", gdy sam nie odczytal numeru z dolkow (plytka kwadratowa: zalezy od
pola skanera) - kliknij numer wybity na plytce. Plytka okragla: mapa jest kolem, sciecie plytki to
plaska krawedz z szara kreska z przodu po prawej, pod mapa napis "PRZOD PLYTKI"
[DO POTWIERDZENIA NA 0.3.3]. Prace bez projektu STL sa szare "bez projektu".
Zanotuj: arkusz 2.7.
Gdy sie nie uda:

    Widzisz                                  Zrob
    "Analiza skanu nie powiodla sie" i w     przepisz nawias. N = 0: najpierw sprawdz, czy to nie skan
    nawiasie "w skanie widac N z 3           z podlozem (krok 2.3). Inaczej plytka nie miesci sie w polu
    znacznikow plytki - ..."                 albo lezy z boku: ustaw ja na srodku, plik sprawdz krokiem 2.4
    "Plytka nie z tego trybu"                plytka 4-6 wieczorem: kliknij "-> Poranek" w pasku
                                             i zeskanuj ja JESZCZE RAZ
    nic sie nie dzieje                       plik nie konczy sie na .stl albo trafia do innego folderu

Teksty w nawiasach: [DO POTWIERDZENIA NA 0.3.3]. Plikow skanow z tego kroku program nie kopiuje - zabierz
je sam (czesc 5, punkt 3).
[NIE SPRAWDZONE BEZ SPRZETU: jak i jak dlugo program skanera zapisuje plik, pod jaka nazwa]

---

## Czesc 3 - ramka

Na czas krokow 3.3-3.7 i 3.9 ZAMKNIJ program "Stanowisko": ramke obsluguje jeden program naraz.

### Krok 3.1 - ogledziny i pasowanie, BEZ pradu (15 minut)

Co zrobic: wloz kazda plytke we wkladke; sprobuj tez obrocona o cwierc obrotu. Zaloz pokrywke i odwroc.
Zmierz suwmiarka plytke (bok albo srednica, grubosc) i otwor wkladki.
Udalo sie, gdy: plytka wchodzi lekko i lezy plasko tylko w jednym polozeniu. Okragla ramkowa obrocona
lezy krzywo na zebrze (jedna krawedz ok. 4,5 mm wyzej). Zanotuj: arkusz 3.1.
Gdy sie nie uda: zdjecie i wymiar. Idz dalej.
[NIE SPRAWDZONE BEZ SPRZETU: wymiary znamy tylko z projektu]

### Krok 3.2 - wlaczenie pradu (5 minut)

Co zrobic: wloz wtyk zasilacza i wlacz stoper. Patrz na matryce diod.
Udalo sie, gdy: na brzegu matrycy pojawia sie niebieski pierscien (ramka gotowa). Plan: mniej niz 60 s.
Zanotuj: arkusz 3.2.
Gdy sie nie uda: matryca ciemna po 3 minutach = na karcie SD nie ma programu ramki albo nie startuje on
sam (P3). Karty SD nie wyjmuj i nie nadpisuj. Zostaje krok 3.1; przejdz do czesci 2 albo 4.
[NIE SPRAWDZONE BEZ SPRZETU: start po wlaczeniu pradu, kolory, jasnosc, kierunek obrazu]

### Krok 3.3 - czy komputer widzi ramke; klucz ramki (10 minut)

Co zrobic:

1. Polacz komputer z ta sama siecia co ramka (P6).
2. Kliknij dwa razy `C:\Sprzet_testy\narzedzia\ramka.cmd`. Wpisz adres `ramka-w.local` (wieczorna) albo
   `ramka-p.local` (poranna). Wybierz `1` i Enter.
3. Gdy pojawi sie "RAMKA ODPOWIADA, ale wymaga klucza": menu samo zapyta o klucz (pozycja `7`). Przepisz
   go z kartki (P8). Po napisie "KLUCZ DOBRY ..." narzedzie wiecej o klucz nie pyta. Wybierz `1`.

Udalo sie, gdy: jest wiersz `RAMKA ODPOWIADA (... ms): ramka wieczorna (W), program ramki ...` i ponizej
`plytka na ramce: 0`. Zanotuj: arkusz 3.3 (adres - potrzebny w 3.8; czy ramka wymaga klucza).
Gdy sie nie uda: `BRAK POLACZENIA` - sprawdz, czy ramka swieci i czy komputer jest w tej samej sieci;
zamiast nazwy wpisz adres z cyfr (z listy urzadzen routera albo hotspotu). "ZLY KLUCZ" - przepisz go
jeszcze raz, znak po znaku. Bez polaczenia albo bez klucza kroki 3.4-3.9 odpadaja: przejdz do czesci 2.
Klucz zapisuje sie w pliku `C:\Sprzet_testy\narzedzia\klucz_ramki.txt`; do wynikow nie trafia.
[NIE SPRAWDZONE BEZ SPRZETU: nazwa `ramka-w.local`, Wi-Fi, adres ramki, menu z klawiatury]

### Krok 3.4 - test diod (2 minuty)

Co zrobic: w `ramka.cmd` wybierz `2`.
Udalo sie, gdy: cala matryca swieci kolejno na czerwono, zielono, niebiesko i bialo (razem 8 sekund), potem
wraca niebieski pierscien. Zanotuj: arkusz 3.4.
Gdy sie nie uda: zdjecie kazdego koloru i ciemnych pol. Idz dalej.
[NIE SPRAWDZONE BEZ SPRZETU: prawdziwa matryca]

### Krok 3.5 - odczyt numeru kazdej plytki (15 minut)

Co zrobic: w `ramka.cmd` wybierz `3`. Przez 5 minut kladz i zdejmuj plytki, kazda 5 razy. Kazda zmiana
pojawia sie na ekranie, np. `12:01:03.250  plytka 0 -> 2`, i trafia do pliku w
`C:\Sprzet_testy\wyniki\ramka\`. Koniec przed czasem: Ctrl+C.
Udalo sie, gdy: po polozeniu plytki nr 2 jest `0 -> 2`, po zdjeciu `2 -> 0`, za kazdym razem. Na matrycy
przy lezacej plytce ma byc jej numer i napis "BRAK" (to normalne). Zanotuj: arkusz 3.5 (tabela).
Gdy sie nie uda: sprawdz, czy plytka ma magnesy i lezy plasko; zapisz numer wybity i odczytany.
[NIE SPRAWDZONE BEZ SPRZETU: czujniki i magnesy, takze w plytce okraglej]

### Krok 3.6 - plytka krzywo i plytka nie od tej ramki (10 minut)

Co zrobic (dalej pozycja `3`): (a) poloz plytke obrocona, na zebrze; (b) poloz ja skosem, jednym brzegiem;
(c) poloz plytke drugiej ramki (np. nr 4 na wieczornej), jesli ja masz.
Udalo sie, gdy: dla (a) i (b) ramka czyta 0 albo nic sie nie zmienia; dla (c) jest dopisek
`NUMER SPOZA TEJ RAMKI`.
Zanotuj: arkusz 3.6 - kazdy odczytany numer. Odczyt inny niz 0 dla (a) albo (b) jest wazny.
Gdy sie nie uda: zapisz, co widac, i idz dalej.
[NIE SPRAWDZONE BEZ SPRZETU: (a) i (b) w calosci]

### Krok 3.7 - gniazda i diody (20 minut)

Co zrobic: poloz na ramce pusta plytke. W `ramka.cmd` wybierz `4` (wszystkie gniazda naraz). Narzedzie
wypisze rodzaje plytek, ktore zna ramka: sam Enter = plytka kwadratowa tej ramki. Dla plytki okraglej
ramkowej przepisz z listy `okragla_ramkowa_wieczorna` albo `okragla_ramkowa_poranna`
[DO POTWIERDZENIA NA 0.3.3]; gdy ich nie ma - sam Enter (gniazda sa w tych samych miejscach).
Przesuniecia: dwa razy sam Enter. Popatrz z gory.
Udalo sie, gdy: kazdy otwor w dnie gniazda swieci, miedzy gniazdami jest ciemno.
Zanotuj: arkusz 3.7 (osobno wkladka okragla).
Gdy sie nie uda:

- swiatlo obok otworow: uruchom `4` jeszcze raz i podaj przesuniecie w diodach (1 dioda = 2,5 mm), np.
  w prawo `1`, w dol `0`; powtarzaj, az trafi. Potem `5`: swieci jedno gniazdo naraz; Enter = dobrze albo
  wpisz uwage; `k` = koniec. Dzis tylko notujemy liczby.
- `NA RAMCE NIE LEZY PLYTKA TEJ RAMKI`: ramka nie czyta numeru (krok 3.5). Idz do 3.8.

[NIE SPRAWDZONE BEZ SPRZETU: polozenie diod pod gniazdami (policzone z rysunku), takze wkladka okragla]

### Krok 3.8 - program "Stanowisko" razem z ramka (35 minut)

Dwie zasady: przed skanem NASTEPNEJ plytki zdejmij poprzednia z ramki; bierz plytki o ROZNYCH numerach
(np. kwadratowa 1, okragla 2).

Co zrobic:

1. Zamknij `ramka.cmd` (`0`) i poczekaj pol minuty. W `C:\Stanowisko\ustawienia.toml` znajdz (Ctrl+F)
   `[ramki]` i zmien dwa wiersze: adres z kroku 3.3 (ramka poranna: wiersz `poranna_host`) i klucz:

       wieczorna_host = "ramka-w.local"   ->   wieczorna_host = "<adres-IP>"
       klucz = ""                         ->   klucz = "tu-klucz-z-kartki"

   Zapisz. Ramka bez klucza: wiersza `klucz` nie zmieniaj.
2. `C:\Stanowisko\Samokontrola.cmd` - ma byc wiersz `OK ramka_wieczorna: ramka wieczorna odpowiada`.
3. `C:\Stanowisko\Stanowisko.cmd`, "Tester". W pasku u gory: "Ramki: W: gotowa".
4. Poloz plytke na ramce: w pasku "W: gotowa (plytka 1)". Kliknij "Test LED" (matryca swieci kolorami
   ok. 8 sekund). Zdejmij plytke.
5. Zeskanuj plytke z pracami (jak w 2.7; podaj numer, gdy program pyta) i poloz TE plytke na ramce:
   swieca gniazda z pracami. Zdejmij ja: gasna. Poloz jeszcze raz: wieczorem zostaje ciemno, bez
   komunikatu - wynik wraca dopiero po nowym skanie. To normalne.
6. Powtorz punkt 5 z plytka okragla ramkowa o INNYM numerze.
7. Proby celowe - ramka ma NIE swiecic, a nad mapa ma byc zolty panel [DO POTWIERDZENIA NA 0.3.3: tytuly
   paneli z punktow 7 i 8 i z akapitu o ramce porannej]:
   (a) poloz plytke drugiej ramki (np. nr 4 na wieczornej): "Plytka lezy na zlej ramce";
   (b) poloz inna plytke niz ostatnio zeskanowana: "Na ramce lezy inna plytka niz zeskanowana";
   (c) tylko plytka OKRAGLA, ktorej numer program odczytal sam: lezy na ramce i swieci; kliknij przy
   niej "Zmien numer" i podaj inny: "Numer plytki nie zgadza sie ze skanem" ("Podany numer plytki to X,
   a program odczytal ze skanu numer Y"). Plytki NIE zdejmuj. "Zmien numer" z powrotem na wlasciwy:
   panel znika, ramka swieci. Na plytce kwadratowej tej proby nie rob (wyjdzie komunikat b).
8. Ten sam numer drugi raz (gdy jest czas): w ciagu godziny zeskanuj ponownie plytke z punktu 6, gdy
   LEZY na ramce. Program pyta "Ponowny skan tej samej plytki?", ramka gasnie, zolty panel "Dwa skany
   z numerem plytki N - ramka czeka na odpowiedz". Kliknij "Tak, to ponowny skan": ramka swieci nowy
   wynik. ("Nie, to nowy wsad" jest dla INNEJ plytki o tym samym numerze - wtedy najpierw zdejmij z ramki
   te, ktora lezy.)

Udalo sie, gdy: pod plytka swieca gniazda z pracami w kolorach jak na mapie - takze pod plytka okragla
ramkowa [DO POTWIERDZENIA NA 0.3.3] - a proby 7 i 8 daja opisane panele i ciemna ramke.
Zanotuj: arkusz 3.8; kazdy komunikat, ktory pojawil sie BEZ proby celowej, przepisz.
Gdy sie nie uda:

- "brak polaczenia" albo "zly klucz" w pasku: sprawdz adres i klucz w ustawieniach. "drugi laptop":
  zamknij `ramka.cmd` i poczekaj pol minuty.
- Panel (c) po poprawieniu numeru ZLE odczytanego z dolkow zostaje, ramka ciemna: to wynik pomiaru (skaner
  zle czyta dolki), nie awaria. Zapisz numer wybity i odczytany, zeskanuj plytke ponownie.
- Pod plytka swieci wynik INNEJ plytki: na ramce lezala plytka o numerze nowego skanu. Gdy prace maja
  rozne projekty STL, program o nic nie pyta - dlatego pierwsza zasada. Zapisz to.
- Ramka ciemna bez komunikatu: zapisz numer plytki i tekst z paska, zrob zdjecie ekranu.

Ramka poranna (plytki 4-6): w pasku programu kliknij "-> Poranek" i dopiero wtedy skanuj. Plytka
polozona bez skanu: ramka ciemna, bez komunikatu. Po skanie swieca gniazda z pracami - takze bez projektow
STL i bez pliku zlecen; po zdjeciu i ponownym polozeniu wynik WRACA (inaczej niz wieczorem). Program pyta
o numer, a plytka juz lezy na ramce: panel "Plytka na ramce czeka na numer skanu" - wybierz numer
w pytaniu "Podaj numer plytki", ramka zaswieci sama. Plytka inna niz zeskanowane: "Na ramce lezy plytka,
ktorej nie ma w planie pieca". Plytka zeskanowana w trybie "Wieczor" ("Plytka nie z tego trybu"): po
"-> Poranek" zeskanuj ja jeszcze raz - samo przelaczenie nie wystarcza.
[NIE SPRAWDZONE BEZ SPRZETU: prawdziwa siec i ramka; jak czesto komunikat (b) pojawia sie w zwyklej pracy]

### Krok 3.9 - klawiatura ramki porannej (10 minut, tylko ramka poranna)

Co zrobic: poloz na ramce plytke 4, 5 albo 6. W `ramka.cmd` wybierz `6`. Naciskaj na klawiaturze ramki po
kolei: Enter; Backspace; 2 2 2 2 Enter; 9 Enter; gwiazdka, potem Enter.
Udalo sie, gdy: po kazdym kroku na ekranie komputera pojawia sie wiersz (np. "Enter: kuweta potwierdzona
1111"), a na koncu "rodzaje: 5 z 5". Zanotuj: arkusz 3.9.
Gdy sie nie uda: baterie, odbiornik USB w ramce, NumLock. Zapisz, ktore klawisze nie dzialaja.
[NIE SPRAWDZONE BEZ SPRZETU: prawdziwa klawiatura]

---

## Czesc 4 - laptop stanowiska (tylko gdy testy sa na laptopie firmowym)

- **4.1** Po krokach 2.7 i 3.8 nacisnij Windows + R, wpisz `cmd` i Enter. W czarnym oknie wpisz:

      findstr /c:"KnownDlls" /c:"proces silnika" C:\Stanowisko\dane\logi\stanowisko.log

  To sprawdza, czy program analizy nie przerywal pracy. Policz wiersze; ma byc 0 (nic sie nie wypisuje).
- **4.2** Czas analizy plytki: czasy ze stopera z kroku 2.7. Plan: do 40 s.
- **4.3** Skalowanie ekranu (Ustawienia -> System -> Ekran): procent i rozdzielczosc. Czy widac wszystkie
  przyciski programu?
- **4.4** Czy folder OneDrive "Cyrkon" jest na tym laptopie? **4.5** Wolne miejsce na dysku.

Zanotuj: arkusz, czesc 4. Gdy cos sie nie uda: zapisz i idz dalej - to sa tylko odczyty.
[NIE SPRAWDZONE BEZ SPRZETU: wszystko w tej czesci]

---

## Czesc 5 - co przywiezc i gdzie polozyc

Skopiuj na pendrive. Na komputerze testowym nic nie kasuj, dopoki odbior nie zostanie potwierdzony.

1. Paczki okna "Dzien skanera": pliki ZIP z `C:\Stanowisko\dane\dzien_skanera\<data_godzina>\paczka\`.
2. Wyniki narzedzi: caly folder `C:\Sprzet_testy\wyniki` (`pole_skanu` i `ramka`).
3. Skany z krokow 2.7 i 3.8: caly folder zlecenia testowego z programu skanera (ten wpisany w
   `folder_eksportu_skanera`). Program "Stanowisko" ich nie kopiuje.
4. Z `C:\Stanowisko`: foldery `dane\logi` i `dane\wyniki`, pliki `ustawienia.toml` i
   `dziennik_instalacji.txt`.
5. Zdjecia z telefonu: ramka z plytka, diody pod gniazdami, plytka na zebrze, ekran z kazdym bledem (bez
   twarzy, bez kart zlecen).
6. Wypelniony arkusz.

Na PC poloz to w folderze `<PC-katalog>\sprzet_2026-11-28\`:

    skaner\          <- punkt 1        program\   <- punkt 4
    wyniki\          <- punkt 2        zdjecia\   <- punkt 5
    skany_program\   <- punkt 3        arkusz\    <- punkt 6

Nie mozesz tam zapisac: zostaw pendrive i powiedz o tym sesji prowadzacej projekt.

Czego NIE przywozic: folderu z projektami STL, zlecen z danymi pacjentow, pliku bazy programu. Przejrzyj
nazwy plikow i folderow: bez nazwisk. Pliki `ustawienia.toml` i `klucz_ramki.txt` zawieraja klucz ramki -
nie wysylaj ich poczta.

---

## Zbiorcza lista: czego NIE sprawdzono bez sprzetu

Skaner: (1) plik skanu: format, nazwa, liczba plikow, czas zapisu - 2.2, 2.3, 2.7; (2) wymiar i ksztalt
pola skanera - 2.4; (3) stolik albo uchwyt w skanie - 2.3, 2.4; (4) dolki numeru i trzy stozki - 2.3-2.5;
(5) scianka boczna i rowek pokrywki - 2.5; (6) plytka okragla brana za kwadratowa - 2.5a; (7) szum, prace
prawdziwe i ukruszone - 2.5; (8) zrzut ekranu, praca obok programu skanera - 2.1.

Ramka: (9) Raspberry Pi, program ramki, start po wlaczeniu pradu - 3.2; (10) matryca: kolory, jasnosc,
kierunek obrazu - 3.4; (11) czujniki i magnesy, plytka na zebrze i skosem - 3.5, 3.6; (12) diody pod
gniazdami, takze pod wkladka okragla - 3.7; (13) siec, nazwa `ramka-w.local`, klucz - 3.3, 3.8; (14)
komunikaty o plytce na ramce w zwyklej pracy - 3.8; (15) klawiatura - 3.9; pasowanie plytek - 3.1.

Komputer: (16) instalacja na laptopie firmowym - 1.1, 1.2; (17) dwuklik, przeciaganie pliku, menu z
klawiatury - 1.4; (18) wyglad okien, czas analizy na laptopie - 1.3, czesc 4.

Wiecej (program ramki na Raspberry Pi, nazwy w programie, pelne teksty komunikatow): `ZALACZNIKI.md`.
