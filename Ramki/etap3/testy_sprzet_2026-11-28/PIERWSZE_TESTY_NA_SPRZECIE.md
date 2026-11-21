# Pierwsze testy na prawdziwym sprzecie - 28-29.11.2026

Dokument dla wlasciciela. Wydrukuj go razem z arkuszem obserwacji. Stan: 21.11.2026 wieczor; przeszedl krok
po kroku na probnej instalacji wersji 0.3.3 programu, bez skanera i bez ramki; nazwa paczki i teksty
komunikatow sa sprawdzone na wydanej wersji 0.3.3.

Program byl dotad sprawdzany tylko na danych sztucznych i "atrapach" (program udaje ramke albo skaner).
Cel weekendu: zebrac liczby i pliki, ktorych nie da sie zdobyc inaczej. Nie wszystko musi zadzialac. Co
pojdzie inaczej niz tu napisano, jest wynikiem - zapisz to.

Znacznik:

- **[NIE SPRAWDZONE BEZ SPRZETU]** - tego nikt nie widzial na prawdziwym urzadzeniu. Moze pojsc inaczej.

Zasady:

1. W programie skanera niczego nie kasuj.
2. Zadnych nazwisk pacjentow: zlecenia nazywaj TEST1, TEST2 i trzymaj je w osobnym folderze testowym
   (P9). Bierz prace probne albo odrzuty.
3. Krok nie udaje sie dluzej niz 15 minut? Zdjecie ekranu telefonem, notatka i dalej.
4. Mozna zrobic sam skaner (czesc 2) bez ramki i sama ramke (czesc 3) bez skanera. Jedna ramka wystarcza.
   Plytek okraglych ramkowych (1-6) jeszcze nie masz (P2): kroki z nimi maja wariant "nie masz jej".

---

## 0. Pytania do wlasciciela - odpowiedz najpozniej do srody 25.11.2026

Nie znamy odpowiedzi i nie zgadujemy. Wpisz odpowiedz w tabeli ("nie wiem" to tez odpowiedz) i przekaz sesji
prowadzacej projekt. Te same pytania z szerszym wyjasnieniem: osobna strona pytan. Najpilniejsze: P3, P1, P6, P8, P9.

| Nr | Pytanie | Od odpowiedzi zalezy | Odpowiedz |
|---|---|---|---|
| P1 | 21.11 odpowiedziales: "Obie kwadratowe oraz jedna okragla" - nie wiemy, czy to ramki, czy plytki. Ile ramek przyszlo: jedna czy dwie? Jaki otwor ma wkladka ramki: kwadratowy czy okragly? Jedna ramka: wieczorna czy poranna? | plytki 1-3 albo 4-6; klawiatura (krok 3.9) tylko przy porannej; wkladka okragla: plytka kwadratowa do niej nie wejdzie - bez plytki okraglej ramkowej z czesci 3 zostaja kroki 3.1-3.4 | .......... |
| P2 | 21.11: zdjecie pliku `ramka_plytka_okragla_wieczorna_n8_v2.stl` = plytka okragla nr 8 starego ukladu R54 (20 gniazd) - to plytka TESTOWA, nie do ramki. Na kazdej plytce policz dlugie rynienki (1 = uklad R59, 2 = stary R54; kwadratowa wieczorna ma 19 albo 20 gniazd, poranna 24 albo 33) i przepisz numer wybity. Czy plytki kwadratowe maja wklejone magnesy? | program zna oba uklady; plytka R54 w kroku 3.7: `wieczorna_r54` / `poranna_r54`; plytka nr 8 nie ma magnesow - na ramce nie swieci; bez magnesow ramka nie odczyta numeru (krok 3.5) | .......... |
| P3 | Czy Raspberry Pi w ramce jest zlozone, ma karte SD i czy ktos wgral na nia program ramki? | cala czesc 3; bez programu ktos musi go wgrac PRZED sobota (kilka godzin) - kto i kiedy? | .......... |
| P4 | Na jakim komputerze uruchomisz program (Windows 10 albo 11, 30 GB wolnego miejsca)? | laptop stanowiska: dochodzi czesc 4 | .......... |
| P5 | Czy skaner stoi przy tym samym komputerze? Do jakiego folderu program skanera zapisuje skany? | inny komputer: skany przenosisz pendrivem, krok 2.7 odpada | .......... |
| P6 | Jaka siec laczy komputer z ramka (router, hotspot)? Jaka siec Wi-Fi jest wpisana w ramce? | bez wspolnej sieci z czesci 3 zostaja kroki 3.1 i 3.2 | .......... |
| P7 | Czy masz projekty STL (z exocad) prac probnych? | bez nich prace w kroku 2.7 beda szare "bez projektu" | .......... |
| P8 | Czy ramka ma ustawiony klucz (haslo ramki) i czy go znasz? Dwie ramki musza miec TEN SAM klucz. | bez klucza odpadaja kroki 3.4-3.9; klucz przywiez na kartce, tu go NIE wpisuj | znam / nie znam / bez klucza |
| P9 | Czy w programie skanera sa juz zlecenia pacjentow? Gdzie zalozyc osobny folder na skany testowe? | sa albo nie wiesz: osobny folder (krok 2.1), kopie calego folderu zlecen (krok 2.6) pomijamy | .......... |

---

## 1. Co przygotowac i zabrac

Pendrive (co najmniej 16 GB):

- [ ] paczka programu `Stanowisko_0.3.3.zip` (ok. 427 MB)
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
- [ ] plaski, sztywny karton albo plyta wiekszy niz 15 x 15 cm (krok 2.4); sciereczka i pedzelek do stozkow plytek
- [ ] dostep do routera albo telefon z hotspotem (P6)

---

## 2. Skrot dnia

    Czesc 1  komputer i program        ok. 40 min    kroki 1.1 - 1.4
    Czesc 2  skaner                    ok. 3,5 godz. kroki 2.1 - 2.7
    Czesc 3  ramka (jedna wystarczy)   ok. 2 godz.   kroki 3.1 - 3.9
    Czesc 4  laptop stanowiska         ok. 20 min    tylko na laptopie
    Czesc 5  zebranie plikow           ok. 20 min

Piec najwazniejszych wynikow: (1) czy skan da sie zrobic bez stolika - krok 2.3; (2) wymiar pola
skanera - 2.4; (3) czy program poznaje plytke okragla bez dolkow numeru - 2.5a (dzis na plytce testowej nr 8);
(4) czy ramka czyta numer kazdej plytki kwadratowej - 3.5; (5) czy diody trafiaja pod gniazda - 3.7.

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
`Stanowisko.cmd`, `Samokontrola.cmd`, `Polecenie.cmd`, `Dzien_skanera.cmd`. Zanotuj: arkusz 1.2.
Gdy sie nie uda: przepisz wiersze `BLAD:` i `CO ZROBIC:` i zrob to, co mowi `CO ZROBIC`. Windows pyta "Czy
chcesz uruchomic ten plik?" - zezwol. Bez instalacji przejdz do kroku 3.1.
[NIE SPRAWDZONE BEZ SPRZETU: laptop firmowy - antywirus, uprawnienia, Notatnik]

### Krok 1.3 - samokontrola i pierwszy start (5 minut)

Co zrobic: kliknij dwa razy `C:\Stanowisko\Samokontrola.cmd`. Potem `C:\Stanowisko\Stanowisko.cmd`; na
pytanie "Kto teraz pracuje?" kliknij "Tester". Popatrz na pasek u gory i zamknij okno.
Udalo sie, gdy: samokontrola konczy sie wierszem `SAMOKONTROLA: ZIELONA` i ma wiersz `OK modele: uklady
plytek z [plytki]: poprawne 10 z 10`. Wiersze `OSTRZEZENIE` (ramki, `excel`, `baza`, `pula`,
`folder_prywatne`, `folder_millbox`) sa teraz normalne. W pasku programu: "Folder skanera: dostepny" i
"Ramki: W: brak polaczenia". Zanotuj: arkusz 1.3.
Gdy sie nie uda: "poprawne 8 z 10" albo "9 z 10" = stara albo niepelna paczka. Przepisz wiersz `BLAD: ...`.
Mozesz isc do czesci 2.
[NIE SPRAWDZONE BEZ SPRZETU: wyglad okna na ekranie laptopa]

### Krok 1.4 - narzedzia dnia sprzetu (2 minuty)

Co zrobic: skopiuj z pendrive'a folder `testy_sprzet_2026-11-28` na dysk jako `C:\Sprzet_testy`.
Udalo sie, gdy: jest folder `C:\Sprzet_testy\narzedzia` z plikami `pole_skanu.cmd` i `ramka.cmd`. Wyniki
zapisuja sie same w `C:\Sprzet_testy\wyniki`, kazdy w osobnym pliku z data i godzina.
Zanotuj: arkusz 1.4 (dwuklik i przeciaganie pliku: okaze sie w krokach 2.4 i 3.3).
Gdy sie nie uda: kopiuj pliki skanow na pendrive - policzymy je na PC.
[NIE SPRAWDZONE BEZ SPRZETU: dwuklik i przeciaganie na prawdziwym ekranie]

---

## Czesc 2 - skaner

Klikanie w programie skanera: wydrukowana sciaga. Tu tylko to, co dotyczy naszego programu.

### Krok 2.1 - okno "Dzien skanera" (5 minut, PRZED pierwszym skanem)

Co zrobic: kliknij dwa razy `C:\Stanowisko\Dzien_skanera.cmd`. Kliknij "Dodaj folder..." i wskaz
folder, do ktorego program skanera zapisze skany TESTOWE (P5, P9). Sa w nim zlecenia pacjentow: ustaw
w programie skanera osobny folder zapisu na ten dzien, a gdy sie nie da - wskaz oknu tylko folder
zlecenia TEST1, nigdy caly folder zlecen. Nie znasz folderu: "Nie wiem, gdzie skaner zapisuje - szukaj".
Kliknij na probe "Zrzut ekranu (za 3 s)".
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
Okno "Dzien skanera" mowi tylko o wierzchu plytki - o stoliku mowia ten dokument i sciaga skanera.
Udalo sie, gdy: plik sam pojawia sie w oknie, a po kilkunastu sekundach jest zielona ocena "SKAN DOBRY:
cala plytka, ...; obrys ... x ... x ... mm; ...". Zanotuj: arkusz 2.3.
Gdy sie nie uda:

    Widzisz                                  Zrob
    plik sie nie pojawia                     w programie skanera "Explore" albo "Export";
                                             w oknie "Dodaj folder..."
    czerwone "... nie widac trzech           popatrz na podglad skanu: wokol plytki widac plaski
    stozkow znacznikow (znaleziono 0)"       stolik albo podstawke? To SKAN Z PODLOZEM (nizej).
                                             Nie widac: zrob krok 2.4 - poda wymiar pola
    czerwone "... nie widac plaskiego        skan obciety za wysoko: opusc linie ciecia i zapisz
    wierzchu plytki"                         cala plytke

SKAN Z PODLOZEM - najwieksze ryzyko dnia. Gdy w skanie jest plaski stolik wokol plytki (w naszych probach
bez skanera: 15 cm i wiecej), program nie rozpoznaje plytki. KAZDY skan jest czerwony, a komunikaty okna
"Dzien skanera" mowia o polu skanera i brudnych stozkach - to zla przyczyna, czyszczenie i ponowny skan
nie pomoga.

- Jak rozpoznac: w podgladzie skanu widac plaska plaszczyzne wokol plytki; `pole_skanu.cmd` (krok 2.4)
  pisze "UWAGA: w skanie jest prawdopodobnie PODLOZE".
- Jak obejsc: podnies linie albo plaszczyzne ciecia powyzej stolika. Zrob DWA skany tej samej plytki:
  (A) ciecie tuz nad stolikiem - scianka boczna plytki zostaje; (B) ciecie 3 mm pod wierzchem. Oba
  sprawdz krokiem 2.4 i wpisz do arkusza 2.3. Dalej skanuj jak w skanie zielonym (oba zielone: jak A).

Inna przyczyna czerwonej oceny: pole skanera 90 mm i mniejsze (w naszych probach bez skanera program nie
rozpoznaje wtedy ZADNEJ plytki; przy 95 mm rozpoznaje).
[NIE SPRAWDZONE BEZ SPRZETU: prawdziwy plik ze skanera; czy stolik trafia do skanu; czy linie ciecia da
sie ustawic miedzy stolikiem a wierzchem plytki; skany A i B]

### Krok 2.4 - pole skanera w liczbach (15 minut)

Co zrobic:

1. NAJPIERW karton - to glowny pomiar pola. Poloz na stoliku plaski karton wiekszy niz 15 x 15 cm,
   linie ciecia opusc pod karton, zeskanuj i zapisz. Przeciagnij plik myszka na
   `C:\Sprzet_testy\narzedzia\pole_skanu.cmd`. Pytanie o numer: sam Enter. Pytanie "Co lezy na
   stoliku?": wpisz `karton`. Ma byc "PLYTKA NIE ROZPOZNANA" (to dobrze - to karton), a w wierszu 2
   wymiar pola: "Dane mieszcza sie w kole o srednicy ok. ... mm" albo "DANE NIE SA KOLEM: ... x ... mm"
   (przepisz OBIE liczby) i zdanie "Dane sa PLASKIE: to plaski arkusz ...".
2. Potem plik skanu plytki z kroku 2.3 (z okna: "Otworz folder sesji" -> `kroki`) - pomiar pomocniczy,
   przyblizony (w naszych probach blad do 5 mm). Pojawi sie 6 wierszy i blok "DO ARKUSZA (przepisz):".
   Wiersz 2 mowi jedno z czterech zdan wypisanych w arkuszu 2.4 ("Cala plytka jest w skanie ...", "POLE
   SKANERA MA OK. ... mm", "POLE NIE JEST KOLEM ...", "... wielkosci pola z tego skanu nie da sie
   podac") - zaznacz je tam i przepisz liczby.

Udalo sie, gdy: masz wymiar pola z kartonu: jedna srednice albo dwie liczby. Zanotuj: arkusz 2.4.
Gdy sie nie uda: Przy KARTONIE nie ma zdania "Dane sa PLASKIE" albo jest uwaga o podlozu: karton byl
wygiety albo wokol niego widac stolik - liczby z wiersza 2 sa mimo to wymiarem pola; przepisz je, kratki
"Dane sa PLASKIE" nie zaznaczaj. Przy skanie PLYTKI narzedzie pisze "UWAGA: w skanie jest prawdopodobnie
PODLOZE" - to skan z podlozem, wroc do kroku 2.3. Inny blad: zabierz plik skanu.
[NIE SPRAWDZONE BEZ SPRZETU: liczby na prawdziwym skanie; skan kartonu; skan z podlozem]

### Krok 2.5 - kolejne skany wedlug okna (ok. 1 godziny)

Co zrobic: kroki 6-13 okna. Najwazniejsze, w tej kolejnosci:

1. plytka z 6-10 pracami calymi (krok 6 okna) i TO SAMO drugi raz bez ruszania plytki (krok 7),
2. plytka z 2-3 pracami celowo ukruszonymi (krok 9) - zapisz, ktore gniazdo i gdzie ukruszenie,
3. kazdy RODZAJ plytki, jaki masz (dzis: kwadratowe i okragla testowa nr 8; okragla ramkowa, gdy
   dojdzie) - po jednym skanie pustej. Te skany rob w kroku 12 okna ("Skan 7: druga plytka"); w notatce
   wpisz, ktora to plytka.

Kazdy plik przeciagnij na `pole_skanu.cmd`: numer - sam Enter; "Co lezy na stoliku?" - wpisz, jaka plytka
NAPRAWDE lezy i co na niej jest (np. `kw 2, 8 prac`). Blok "DO ARKUSZA" i godzine z wiersza "Zapisano:"
przepisz do tabeli 2.5 - po godzinie znajdziemy potem plik wyniku. Godzina to 6 cyfr przed "_pole"
w nazwie pliku z wiersza "Zapisano:", np. `..._20261128_101502_pole.txt` = 10:15:02; wpisz 101502.

Udalo sie, gdy: kazdy skan ma w oknie ocene, a w arkuszu wiersz w tabeli 2.5.
Zanotuj: arkusz 2.5, dla KAZDEGO skanu. Wiersz `rowek pokrywki:` podaje liczby, ale nie rozstrzyga -
przepisz je.
Gdy sie nie uda: ocena zolta "inna plytka niz w skanie ..." albo czerwona "TEN SAM plik" - przeczytaj
tekst po "ZROB TAK". Skan nierozpoznany tez wpisz do tabeli.
[NIE SPRAWDZONE BEZ SPRZETU: dolki numeru, scianka boczna i rowek na prawdziwym skanie; prace ukruszone]

### Krok 2.5a - plytki okragle: czy program poznaje ksztalt (30-50 minut)

Po co: gdy w skanie plytki okraglej nie ma ani dolkow numeru, ani scianki bocznej, program bierze ja za
KWADRATOWA i nie ostrzega. Mierzymy, jak czesto to sie zdarza (skany sztuczne plytki nr 8 R54: 0 z 12).

Co zrobic: plytke okragla zeskanuj trzy razy (krok 12 okna, z notatka): (i) pusta; (ii) z praca
w gniezdzie obok dolkow numeru; (iii) z dolkami zaklejonymi tasma papierowa. Kazdy plik przeciagnij na
`pole_skanu.cmd`; numer - SAM ENTER (podany numer podpowiada programowi ksztalt); "Co lezy na stoliku?" -
np. `okr-test 8, dolki zaklejone`.
Ile: jeden skan z zapisem i narzedziem to ok. 7 minut. Plytki okraglej ramkowej (1-6) jeszcze nie ma:
minimum = plytka okragla nr 8 po 3 skany + 1 kwadratowa pusta dla porownania = 4 skany, ok. 30 minut
(z plytka ramkowa: +3 skany). Wiecej plytek okraglych tylko, gdy zostanie czas.
Udalo sie, gdy: tabela 2.5a ma wiersz dla kazdego skanu. Dobry wynik w wierszu `program mowi:` to
"okragla ramkowa (do ramki)" albo "okragla testowa (poza ramka)" - dla nr 8 z dopiskiem "stary rozstaw
R54"; przy (iii) `numer z dolkow: 0` (dolki nieczytelne - tak ma byc). Wynik zly, ale bardzo wazny:
"kwadratowa" - przy (i) albo (ii): skaner nie widzi ani dolkow, ani scianki; tylko przy (iii): jedyna
ochrona jest numer z dolkow.
Zanotuj: arkusz 2.5a; na koncu: ile razy plytka okragla zostala nazwana kwadratowa.
Gdy sie nie uda: nie masz plytek okraglych - pomin. Narzedzie nie dziala - zabierz pliki skanow.
[NIE SPRAWDZONE BEZ SPRZETU: caly krok, takze czas]

### Krok 2.6 - "Zakoncz i spakuj" (10 minut)

UWAGA - dane pacjentow: plik ZIP z tego kroku wyjezdza z laboratorium. Nie moze w nim byc zadnego
zlecenia pacjenta.

Co zrobic: ostatni krok okna ("Na koniec: kopia CALEGO folderu zlecen programu skanera") zrob TYLKO, gdy
w tym folderze sa wylacznie zlecenia testowe z tego dnia (P9). Inaczej kliknij "Nie udalo sie / pomijam,
bo ..." i wpisz `dane pacjentow`. Potem "Zakoncz i spakuj". Okno zapyta "Brakuje wymaganych krokow ...
Spakowac teraz?" - kliknij "Yes" / "Tak" (sam Enter znaczy NIE).
Udalo sie, gdy: okno pisze "Sesja spakowana: ... plikow" i podaje plik ZIP w folderze
`C:\Stanowisko\dane\dzien_skanera\<data_godzina>\paczka\`. Zanotuj: arkusz 2.6.
Gdy sie nie uda (np. brak miejsca): niczego nie kasuj; skopiuj caly folder z data i godzina na pendrive.
[NIE SPRAWDZONE BEZ SPRZETU: kopia prawdziwego folderu zlecen - rozmiar, czas; napisy przyciskow
w pytaniu przy pakowaniu]

### Krok 2.7 - program "Stanowisko" sam zauwaza prawdziwy skan (20 minut)

Co zrobic:

1. Zamknij okno "Dzien skanera". W programie skanera zaloz NOWE zlecenie testowe (np. TEST5).
2. W `C:\Stanowisko\ustawienia.toml`, w wierszu `folder_eksportu_skanera`, wpisz folder tego zlecenia
   (ukosniki `/`). Nie wskazuj folderu ze starymi zleceniami: program przeanalizuje takze stare skany.
3. `C:\Stanowisko\Samokontrola.cmd` - ma byc wiersz `OK folder_skanera`.
4. `C:\Stanowisko\Stanowisko.cmd`, kliknij "Tester".
5. Zeskanuj plytke z pracami i zapisz skan; wlacz stoper w chwili zapisu. Powtorz z plytka o INNYM
   numerze, np. okragla nr 8 (dlaczego: krok 3.8).

Udalo sie, gdy: po lewej pojawia sie kafelek "Plytka ...", w srodku mapa gniazd (zatrzymaj stoper).
Program pyta "Podaj numer plytki", gdy sam nie odczytal numeru z dolkow (plytka kwadratowa: zalezy od
pola skanera) - kliknij numer wybity na plytce. Po DRUGIM skanie mapa zostaje na poprzedniej plytce,
gdy ta ma prace zolte albo czerwone: po lewej jest "Nowy wynik czeka: Plytka N" - kliknij kafelek nowej
plytki. Plytka okragla: mapa jest kolem, sciecie plytki to plaska krawedz z szara kreska z przodu po
prawej, pod mapa napis "PRZOD PLYTKI". Prace bez projektu STL sa szare "bez projektu".
Zanotuj: arkusz 2.7.
Gdy sie nie uda:

    Widzisz                                  Zrob
    "Analiza skanu nie powiodla sie" i w     przepisz nawias. Gdy jest "0 z 3": program sam
    nawiasie "w skanie widac N z 3           dopisuje "albo w skanie jest stolik (podloze) wokol
    znacznikow plytki - ..."                 plytki" - najpierw sprawdz to (krok 2.3). Inaczej
                                             plytka nie miesci sie w polu albo lezy z boku:
                                             ustaw ja na srodku, plik sprawdz krokiem 2.4
    "Plytka nie z tego trybu"                plytka 4-6 wieczorem: kliknij "-> Poranek" w pasku
                                             i zeskanuj ja JESZCZE RAZ. Stare pytanie zostaje
                                             i ma teraz zdanie bez sensu ("plytka poranna ...
                                             tryb Poranek") - to znany blad napisu, liczy sie
                                             nowy skan
    "Ten sam projekt w dwoch gniazdach"      dwie prace z jednego projektu STL - to nie blad; "Zamknij"
    nic sie nie dzieje                       plik nie konczy sie na .stl albo trafia do innego folderu

W naszych probach bez skanera (pole 90 i 80 mm, skan z podlozem) bylo "0 z 3". Plikow skanow z tego
kroku program nie kopiuje - zabierz je sam (czesc 5, punkt 3).
[NIE SPRAWDZONE BEZ SPRZETU: jak i jak dlugo program skanera zapisuje plik, pod jaka nazwa]

---

## Czesc 3 - ramka

Na czas krokow 3.3-3.7 i 3.9 ZAMKNIJ program "Stanowisko": ramke obsluguje jeden program naraz.

### Krok 3.1 - ogledziny i pasowanie, BEZ pradu (15 minut)

Co zrobic: wloz kazda plytke ramki we wkladke (plytka okragla nr 8 jest testowa, nie do ramki); sprobuj
tez obrocona o cwierc obrotu. Zaloz pokrywke i odwroc. Zmierz suwmiarka plytke (bok albo srednica,
grubosc) i otwor wkladki.
Udalo sie, gdy: plytka wchodzi lekko i lezy plasko tylko w jednym polozeniu. Okragla ramkowa (gdy jest)
obrocona lezy krzywo na zebrze (jedna krawedz ok. 4,5 mm wyzej). Zanotuj: arkusz 3.1.
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
   go z kartki (P8). Po napisie "KLUCZ DOBRY ..." wybierz `1`. Po zmianie adresu zapyta jeszcze raz.

Udalo sie, gdy: jest wiersz `RAMKA ODPOWIADA (... ms): ramka wieczorna (W), program ramki ...` i ponizej
`plytka na ramce: 0`. Zanotuj: arkusz 3.3 (adres - potrzebny w 3.8; czy ramka wymaga klucza).
Gdy sie nie uda: `BRAK POLACZENIA` - sprawdz, czy ramka swieci i czy komputer jest w tej samej sieci;
zamiast nazwy wpisz adres z cyfr (z listy urzadzen routera albo hotspotu). "ZLY KLUCZ" - przepisz go
jeszcze raz, znak po znaku. Bez polaczenia albo bez klucza kroki 3.4-3.9 odpadaja: przejdz do czesci 2.
Klucz zapisuje sie w pliku `C:\Sprzet_testy\narzedzia\klucz_ramki.txt`; do wynikow nie trafia.
Menu nie przyjmuje klawiszy albo samo sie zamyka: Windows + R, wpisz `cmd` i Enter, a w czarnym oknie
uruchamiaj jedna pozycje naraz, np. `C:\Sprzet_testy\narzedzia\ramka.cmd ramka-w.local 7` (klucz), potem
`... ramka-w.local 1`.
[NIE SPRAWDZONE BEZ SPRZETU: nazwa `ramka-w.local`, Wi-Fi, adres ramki, menu z klawiatury]

### Krok 3.4 - test diod (2 minuty)

Co zrobic: w `ramka.cmd` wybierz `2`.
Udalo sie, gdy: cala matryca swieci kolejno na czerwono, zielono, niebiesko i bialo (razem 8 sekund),
potem wraca niebieski pierscien. Zanotuj: arkusz 3.4.
Gdy sie nie uda: zdjecie kazdego koloru i ciemnych pol. Idz dalej.
[NIE SPRAWDZONE BEZ SPRZETU: prawdziwa matryca]

### Krok 3.5 - odczyt numeru kazdej plytki (15 minut)

Co zrobic: w `ramka.cmd` wybierz `3`. Przez 5 minut kladz i zdejmuj plytki, kazda 5 razy. Kazda zmiana
pojawia sie na ekranie, np. `12:01:03.250  plytka 0 -> 2`, i trafia do pliku w
`C:\Sprzet_testy\wyniki\ramka\`. Koniec przed czasem: Ctrl+C.
Udalo sie, gdy: po polozeniu plytki nr 2 jest `0 -> 2`, po zdjeciu `2 -> 0`, za kazdym razem. Na matrycy
przy lezacej plytce ma byc jej numer i napis "BRAK" (to normalne). Plytka okragla nr 8 nie ma magnesow:
ramka jej nie widzi (zostaje `0`) - to dobrze; plytek okraglych ramkowych jeszcze nie ma - pomin je.
Zanotuj: arkusz 3.5 (tabela).
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
wypisze rodzaje plytek, ktore zna ramka: sam Enter = plytka kwadratowa R59 (1 rynienka). Plytka z 2
rynienkami (stary uklad R54, P2): przepisz `wieczorna_r54` albo `poranna_r54` - sam Enter zapali gniazda
R59 obok jej gniazd. Plytka okragla ramkowa: `okragla_ramkowa_wieczorna` albo `okragla_ramkowa_poranna`;
wkladka okragla bez tej plytki - krok pomin (nr 8 nie ma magnesow, kwadratowa nie wejdzie).
Przesuniecia: dwa razy sam Enter. Popatrz z gory; na "Wpisz uwage ..." wpisz `ok` albo co jest zle.
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
(np. kwadratowa 1, okragla ramkowa 2, a bez niej kwadratowa 2).

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
5. Zeskanuj plytke z pracami (jak w 2.7) i poloz TE plytke na ramce: swieca gniazda z pracami. Zdejmij
   ja: gasna. Poloz jeszcze raz: wieczorem zostaje ciemno, bez komunikatu (wynik wraca dopiero po nowym
   skanie) - to normalne. Zdejmij ja.
6. Zeskanuj plytke o INNYM numerze (np. 2; okragla ramkowa, a bez niej kwadratowa) i poloz ja na
   ramce: swieci. Zostaw ja. Kliknij po lewej jej kafelek: "Zmien numer" dotyczy plytki POKAZANEJ nad mapa.
7. Proba celowa (c) - nie masz plytki okraglej ramkowej: pomin. Tylko ta plytka, gdy program sam
   odczytal jej numer, lezy i swieci: nad mapa ma byc "Plytka 2". Kliknij "Zmien numer" i w niebieskim
   panelu inna cyfre, np. 3. Ramka gasnie, nad mapa zolty panel "Plytka 3: Numer plytki nie zgadza
   sie ze skanem" ("Podany numer plytki to 3, a program odczytal ze skanu numer 2"). Plytki NIE zdejmuj. "Zmien numer" z powrotem na 2: panel
   znika, ramka swieci. Na plytce kwadratowej tej proby nie rob - wyjdzie komunikat (b).
8. Ten sam numer drugi raz: zdejmij te plytke i zeskanuj ja ponownie (w ciagu godziny). Program pyta
   "Ponowny skan tej samej plytki?". Zanim odpowiesz, poloz plytke na ramce: ramka jest ciemna, zolty
   panel "Dwa skany z numerem plytki N - ramka czeka na odpowiedz". Kliknij "Tak, to ponowny skan":
   panel znika, ramka swieci nowy wynik. Po "Tak" numeru tej plytki nie da sie juz zmienic ("Nie mozna
   tego zrobic") - dlatego proba (c) jest wczesniej.
9. Proby celowe (a) i (b) - ramka ma NIE swiecic: (a) poloz plytke drugiej ramki (np. nr 4 na
   wieczornej): zolty panel "Plytka lezy na zlej ramce"; (b) poloz inna plytke niz ostatnio zeskanowana:
   "Na ramce lezy inna plytka niz zeskanowana".

Udalo sie, gdy: pod plytka swieca gniazda z pracami w kolorach jak na mapie, a punkty 7-9 (bez plytki
ramkowej: 8-9) daja opisane panele i ciemna ramke. Plytka nr 8 po skanie: ramka ciemna, bez panelu.
Zanotuj: arkusz 3.8; kazdy komunikat, ktory pojawil sie BEZ proby celowej, przepisz.
Gdy sie nie uda:

- Pasek "brak polaczenia" albo "zly klucz": zamknij program, popraw adres i klucz w ustawieniach
  (punkt 1), uruchom program jeszcze raz. "drugi laptop": zamknij `ramka.cmd`, poczekaj pol minuty
  i kliknij w pasku "Przejmij ramke W" (rano: "Przejmij ramke P") - program sam ramki nie przejmuje.
- Panel (c) zostaje po poprawieniu numeru ZLE odczytanego z dolkow: to wynik pomiaru (skaner zle czyta
  dolki), nie awaria. Zapisz numer wybity i odczytany, zeskanuj plytke ponownie.
- Pod plytka swieci wynik INNEJ plytki o tym samym numerze (program nie zawsze pyta o ponowny skan - stad
  pierwsza zasada) albo ramka jest ciemna bez komunikatu: zapisz numer plytki i tekst z paska, zrob
  zdjecie ekranu.
- Pytanie o ponowny skan albo panel "Dwa skany ..." BEZ ponownego skanu: zmieniles numer nie tej plytki -
  kliknij jej kafelek i "Zmien numer" z powrotem.

Ramka poranna (plytki 4-6): najpierw kliknij w pasku programu "-> Poranek". Plytka polozona bez skanu:
ramka ciemna, bez komunikatu. Po skanie swieca gniazda z pracami - takze bez projektow STL i bez pliku
zlecen; po zdjeciu i ponownym polozeniu wynik WRACA. Program pyta o numer, a plytka juz lezy: panel
"Plytka na ramce czeka na numer skanu" - wybierz numer w pytaniu, ramka zaswieci sama. Plytka inna niz
zeskanowane: "Na ramce lezy plytka, ktorej nie ma w planie pieca". Plytke zeskanowana w trybie "Wieczor"
("Plytka nie z tego trybu") zeskanuj po przelaczeniu jeszcze raz. Stare pytanie zostaje i ma teraz zdanie
bez sensu ("plytka poranna ... tryb Poranek") - to znany blad napisu, liczy sie nowy skan.
[NIE SPRAWDZONE BEZ SPRZETU: prawdziwa siec i ramka; jak czesto komunikat (b) pojawia sie w zwyklej pracy;
przycisk 'Przejmij ramke']

### Krok 3.9 - klawiatura ramki porannej (10 minut, tylko ramka poranna)

Co zrobic: poloz na ramce plytke 4, 5 albo 6. W `ramka.cmd` wybierz `6`. Naciskaj na klawiaturze ramki po
kolei: Enter; Backspace; 2 2 2 2 Enter; 9 Enter; gwiazdka, potem Enter.
Udalo sie, gdy: po kazdym kroku na ekranie komputera pojawia sie wiersz (np. "Enter: kuweta potwierdzona
1111"), a na koncu "rodzaje: 5 z 5". Zanotuj: arkusz 3.9.
Gdy sie nie uda: baterie, odbiornik USB w ramce, NumLock. Zapisz, ktore klawisze nie dzialaja.
[NIE SPRAWDZONE BEZ SPRZETU: prawdziwa klawiatura]

---

## Czesc 4 - laptop stanowiska (tylko gdy testy sa na laptopie firmowym)

Arkusz, czesc 4, prowadzi przez piec odczytow (czas analizy z kroku 2.7 - plan: do 40 s; skalowanie
ekranu; folder OneDrive "Cyrkon"; wolne miejsce). Jeden to polecenie: po krokach 2.7 i 3.8 nacisnij
Windows + R, wpisz `cmd` i Enter, a w czarnym oknie:

    findstr /c:"KnownDlls" /c:"proces silnika" C:\Stanowisko\dane\logi\stanowisko.log

Ma nie wypisac nic (0 wierszy) - to znaczy, ze program analizy nie przerywal pracy.

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

Znacznik [NIE SPRAWDZONE BEZ SPRZETU] ma kazdy krok czesci 1-4 (szczegoly przy kroku). Najwazniejsze:
stolik w skanie i linia ciecia - 2.3; pole skanera - 2.4; dolki numeru, scianka boczna, prace ukruszone -
2.5; plytka okragla brana za kwadratowa - 2.5a; plik skanu - 2.2, 2.7; start ramki - 3.2; siec i klucz -
3.3; czujniki i magnesy - 3.5, 3.6; diody pod gniazdami - 3.7; komunikaty w zwyklej pracy - 3.8; laptop
firmowy - 1.2. Wiecej (program ramki, nazwy, pelne teksty komunikatow): zalaczniki.
