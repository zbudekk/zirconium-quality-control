# Pierwsze testy na prawdziwym sprzecie - 28-29.11.2026

SZKIC (etap 1, 21.11.2026). Dokument dla wlasciciela. Do wydruku razem z `ARKUSZ_OBSERWACJI.md`.

Do tej pory program byl sprawdzany tylko na danych sztucznych i na "atrapach" (program udaje ramke
albo skaner). Ten weekend to pierwsze spotkanie programu ze skanerem i z ramka. Cel NIE jest taki, zeby
wszystko zadzialalo. Cel: zebrac liczby i pliki, ktorych nie da sie zdobyc bez sprzetu. Kazda rzecz,
ktora pojdzie inaczej niz tu napisano, jest wynikiem - zapisz ja w arkuszu.

Jak czytac znaczniki:

- **[NIE SPRAWDZONE BEZ SPRZETU]** - tego nikt jeszcze nie widzial na prawdziwym urzadzeniu. Moze pojsc
  inaczej. Lista zbiorcza jest na koncu.
- **[ETAP 2: ...]** - to miejsce zostanie poprawione po nowym wydaniu programu (plytki okragle).
- "Sprawdzone 21.11" - uruchomione na PC na instalacji z paczki 0.3.1, na skanach sztucznych albo atrapie.

Zasady na caly dzien:

1. W programie skanera niczego nie kasuj.
2. Zadnych nazwisk pacjentow: zlecenia nazywaj TEST1, TEST2. Do testow bierz prace probne albo odrzuty.
3. Gdy krok sie nie udaje dluzej niz 15 minut - zapisz, co widzisz (zdjecie ekranu telefonem) i idz dalej.
   Przy kazdym kroku jest napisane, dokad mozna przejsc.
4. Czesci 2 (skaner) i 3 (ramka) nie zaleza od siebie. Mozna zaczac od dowolnej.

---

## 0. Pytania do wlasciciela - odpowiedz PRZED testami

Nie znamy odpowiedzi i nie zgadujemy. Wpisz je na pierwszej stronie arkusza. Od kazdej zalezy, ktore kroki
robisz.

**P1. Ktora ramka przyszla: wieczorna, poranna czy obie? Jaka ma wkladke: kwadratowa czy okragla?**
Od odpowiedzi zalezy: krok 3.3 (adres `ramka-w` albo `ramka-p`), 3.5 (ktore numery plytek: wieczorna 1-3,
poranna 4-6), 3.7 (uklad `wieczorna` albo `poranna`), 3.9 (klawiatura jest tylko w porannej).

**P2. Ktore plytki sa na miejscu i czy maja wklejone magnesy?** Kwadratowe nowe (1-6), okragle ramkowe z
zamowienia R58 (1-6), okragle testowe (8, 9), stare R54.
Od odpowiedzi zalezy: krok 2.3-2.5 (co skanujemy), 3.5 (ramka czyta numer tylko z magnesow), 3.1.
Uwaga: program w wersji 0.3.1 nie zna jeszcze plytek okraglych ramkowych 1-6
[ETAP 2: nazwy ukladow okraglych i ich obsluga na ramce].

**P3. Czy Raspberry Pi w ramce jest zlozone z matryca diod i czujnikami, ma karte SD i czy ktos wgral na
nia "program ramki"?** Firma zewnetrzna mogla dostarczyc sama obudowe, sama elektronike albo calosc.
Od odpowiedzi zalezy: cala czesc 3 od kroku 3.2. Bez programu ramki na karcie SD ramka nie zaswieci.
Wtedy zrob tylko krok 3.1 i przeczytaj Zalacznik A. To jest dzis najwieksza luka: nie ma gotowej
instrukcji ani instalatora programu ramki na Raspberry Pi.

**P4. Na jakim komputerze uruchomisz program: laptop stanowiska, PC, inny?** Musi miec Windows 10 albo 11
i ok. 3 GB wolnego miejsca (do "Dnia skanera" 30 GB).
Od odpowiedzi zalezy: krok 1.1 (Python), cala czesc 4 (tylko laptop stanowiska).

**P5. Czy skaner stoi przy tym samym komputerze? Do jakiego folderu program skanera zapisuje skany?**
Od odpowiedzi zalezy: krok 2.1 i 2.7. Gdy skaner jest przy innym komputerze: albo instalujesz nasz program
na komputerze skanera (kroki 1.1-1.4 tam), albo przenosisz pliki skanow pendrivem - wtedy krok 2.7
(program sam zauwaza skan) jest do zrobienia pozniej.

**P6. Jaka siec laczy komputer z ramka: router w pracowni, hotspot z laptopa, hotspot z telefonu?
Jaka siec Wi-Fi jest wpisana w ramce?**
Od odpowiedzi zalezy: krok 3.3. Komputer i ramka musza byc w TEJ SAMEJ sieci. Ramka nie ma hasla, wiec
najlepiej siec, w ktorej jest tylko komputer i ramka (np. hotspot z laptopa).

**P7. Czy masz projekty STL (z exocad) prac probnych, ktore poloze na plytce?**
Od odpowiedzi zalezy: krok 2.7. Bez projektow program pokaze prace jako szare "bez projektu" - to
wystarczy, zeby sprawdzic, czy skan dochodzi i czy plytka jest rozpoznana.

---

## 1. Co przygotowac i zabrac

Pendrive (co najmniej 16 GB, format exFAT albo NTFS), a na nim:

- [ ] paczka programu `Stanowisko_0.3.1.zip` [ETAP 2: numer nowej paczki]
- [ ] instalator Pythona 3.12.10 dla Windows (64-bit) z python.org - plik `python-3.12.10-amd64.exe`
- [ ] folder `testy_sprzet_2026-11-28` (ten dokument, arkusz i podfolder `narzedzia`)
- [ ] 2-3 projekty STL prac probnych (bez nazwisk w nazwach plikow) - jesli masz (P7)

Wydruki:

- [ ] ten dokument i `ARKUSZ_OBSERWACJI.md`
- [ ] `Ramki/dzien_skanera_karta_2026-11-16.md` i `Ramki/sciaga_skaner_DentalScan_2026-11-16.md`
- [ ] instrukcja `instalacja_i_aktualizacja.md` (jest tez w paczce: `program\instrukcje`)

Sprzet i drobiazgi:

- [ ] ramka, jej zasilacz 5 V 4 A z wtykiem 5,5/2,1; klawiatura numeryczna z odbiornikiem (ramka poranna)
- [ ] plytki (wszystkie, jakie sa), pokrywka, zapasowe magnesy
- [ ] 6-10 prac probnych albo odrzutow, 2-3 do celowego ukruszenia
- [ ] suwmiarka, stoper (telefon), telefon do zdjec, dlugopis
- [ ] plaski karton albo sztywna kartka, wieksza niz 15 x 15 cm (krok 2.4)
- [ ] kabel sieciowy i dostep do routera albo telefon z hotspotem (P6)
- [ ] czysta sciereczka i pedzelek (stozki na plytkach musza byc bez pylu)

---

## 2. Kolejnosc w skrocie

    Czesc 1  komputer i program          ok. 40 min   kroki 1.1 - 1.4
    Czesc 2  skaner                      ok. 2 godz.  kroki 2.1 - 2.7
    Czesc 3  ramka (jedna wystarczy)     ok. 2 godz.  kroki 3.1 - 3.9
    Czesc 4  laptop stanowiska           ok. 20 min   kroki 4.1 - 4.5 (tylko na laptopie)
    Czesc 5  zebranie plikow             ok. 15 min

Najwazniejsze trzy liczby dnia: (a) srednica pola skanera - krok 2.4; (b) czy ramka czyta numer kazdej
plytki - krok 3.5; (c) czy diody trafiaja pod gniazda - krok 3.7.

---

## Czesc 1 - komputer i program

### Krok 1.1 - Python 3.12 (5 minut)

Co zrobic: uruchom z pendrive'a `python-3.12.10-amd64.exe`, opcje domyslne, "Install Now".

Udalo sie, gdy: instalator konczy sie napisem "Setup was successful".
Gdy sie nie uda: zapisz komunikat. Bez Pythona nie zrobisz czesci 1, 2.1-2.7 ani 3.3-3.9. Mozesz zrobic
krok 3.1 i 3.2 oraz skany zapisywane recznie na pendrive.
Arkusz: P4 i 1.1.
Stan: instalator Pythona na obcym komputerze [NIE SPRAWDZONE BEZ SPRZETU] (na PC Python juz byl).

### Krok 1.2 - instalacja programu z paczki (10-15 minut)

Co zrobic:

1. Skopiuj `Stanowisko_0.3.1.zip` [ETAP 2: numer paczki] na dysk, np. do `C:\Paczki`.
   Prawy klawisz na pliku -> "Wyodrebnij wszystkie".
2. W rozpakowanym folderze kliknij dwa razy `zainstaluj.cmd`. Pojawi sie czarne okno z krokami [1/9] ... [7/9].
   Trwa to ok. 1 minuty (na PC 51 s; na laptopie moze dluzej).
3. Pierwszy raz okno konczy sie wierszem:

       INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom zainstaluj.cmd ponownie (kod 10)

   To NIE jest blad. Program nie zna jeszcze folderow tego komputera.
4. Zaloz dwa puste foldery (w Eksploratorze): `C:\Stanowisko_test\skany` i `C:\Stanowisko_test\projekty`.
   Do `projekty` skopiuj projekty STL prac probnych, jesli je masz.
5. Otworz w Notatniku plik `C:\Stanowisko\ustawienia.toml`. Zmien TRZY wiersze (ukosniki w prawo `/`):

       folder_eksportu_skanera = "C:/Stanowisko_test/skany"
       folder_cyrkon = "C:/Stanowisko_test/projekty"
       operatorzy = ["Tester"]

   Reszty nie ruszaj. Zapisz (Plik -> Zapisz; kodowanie "UTF-8").
6. Kliknij dwa razy `zainstaluj.cmd` JESZCZE RAZ. Tym razem trwa kilka sekund (na PC 6 s).

Udalo sie, gdy: ostatni wiersz to `INSTALACJA: GOTOWA - wersja biezaca ...`, a w `C:\Stanowisko` sa pliki
`Stanowisko.cmd`, `Samokontrola.cmd`, `Polecenie.cmd`.
Gdy sie nie uda: przepisz do arkusza wiersze zaczynajace sie od `BLAD:` i `CO ZROBIC:` i zrob to, co mowi
`CO ZROBIC`. Najczestsze: `kod 4` = nie ma Pythona 3.12 (krok 1.1). Gdy Windows pyta "Czy chcesz uruchomic
ten plik?" - zezwol i zapisz to w arkuszu. Bez instalacji przejdz do kroku 3.1.
Arkusz: 1.2.
Stan: sprawdzone 21.11 na PC w swiezym katalogu: kod 4 bez Pythona, potem kod 10, po zmianie 3 wierszy
kod 0; sumy paczki 210 z 210; pakiety 73 z 73. Wiersze `folder_prywatne` i `folder_millbox` moga zostac -
daja tylko OSTRZEZENIE. Na laptopie firmowym (antywirus, uprawnienia, "Wyodrebnij wszystkie", Notatnik):
[NIE SPRAWDZONE BEZ SPRZETU].

### Krok 1.3 - samokontrola i pierwszy start (5 minut)

Co zrobic:

1. Kliknij dwa razy `C:\Stanowisko\Samokontrola.cmd`. Ostatni wiersz ma byc `SAMOKONTROLA: ZIELONA`.
   Wiersze `OSTRZEZENIE ramka_wieczorna`, `ramka_poranna`, `excel`, `baza`, `pula` sa teraz normalne.
2. Start na pokaz (dane sztuczne, bez skanera). Nacisnij klawisze Windows + R, wpisz i Enter:

       C:\Stanowisko\Stanowisko.cmd --atrapa

   Ma sie otworzyc okno programu z plytkami. Zamknij je krzyzykiem.
3. Start prawdziwy: kliknij dwa razy `C:\Stanowisko\Stanowisko.cmd`. Na pytanie "Kto teraz pracuje?"
   kliknij "Tester". W pasku u gory zobaczysz m.in. "Folder skanera: dostepny" i "Ramki: W: brak polaczenia"
   (ramki jeszcze nie ma w sieci - to normalne). Zamknij okno.

Udalo sie, gdy: oba okna sie otwieraja, zadne nie znika samo.
Gdy sie nie uda: zapisz, co widac w czarnym oknie (wiersz `BLAD: ...`). Mozesz isc do czesci 2 - okno
"Dzien skanera" jest osobnym programem.
Arkusz: 1.3.
Stan: sprawdzone 21.11 na PC bez ekranu (samokontrola ZIELONA: ok 14, ostrzezenia 7; oba starty kodem 0).
Wyglad okna na prawdziwym ekranie laptopa (skalowanie 125 / 150 %): [NIE SPRAWDZONE BEZ SPRZETU].

### Krok 1.4 - narzedzia dnia sprzetu (2 minuty)

Co zrobic: skopiuj z pendrive'a caly folder `testy_sprzet_2026-11-28` na dysk jako `C:\Sprzet_testy`.
W srodku ma byc `C:\Sprzet_testy\narzedzia` z plikami `dzien_skanera.cmd`, `pole_skanu.cmd`, `ramka.cmd`.
Wyniki narzedzi beda sie zapisywac same w `C:\Sprzet_testy\wyniki`.

Te pliki zakladaja, ze program jest w `C:\Stanowisko`. [ETAP 2: czy narzedzia wejda do paczki programu]

---

## Czesc 2 - skaner

Szczegoly klikania w programie skanera: wydrukowana "sciaga". Tu tylko to, co dotyczy naszego programu.

### Krok 2.1 - okno "Dzien skanera" (5 minut, PRZED pierwszym skanem)

Co zrobic: kliknij dwa razy `C:\Sprzet_testy\narzedzia\dzien_skanera.cmd`.

Uwaga: wydrukowana karta "Dzien skanera" kaze uruchomic `uruchom_dzien_skanera.bat`. W programie
zainstalowanym z paczki tego pliku NIE MA - uzywaj `dzien_skanera.cmd` z folderu narzedzi.
[ETAP 2: wlasciwy skrot w paczce]

Udalo sie, gdy: otwiera sie okno "Dzien skanera - krok po kroku". Na gorze jest napis "Obserwuje:" i folder
`C:\Stanowisko_test\skany`. Kliknij "Zrzut ekranu" na probe.
Potem: kliknij "Dodaj folder..." i wskaz folder, do ktorego zapisuje program skanera (pytanie P5; w programie
skanera to "Order Save Path"). Jesli go nie znasz: przycisk "Nie wiem, gdzie skaner zapisuje - szukaj".
Gdy sie nie uda: po kazdym skanie kopiuj recznie folder zlecen programu skanera na pendrive; ekran
fotografuj telefonem. Przejdz do kroku 2.3 bez okna.
Arkusz: 2.1.
Stan: sprawdzone 21.11 na instalacji 0.3.1: okno startuje, sesja powstaje w
`C:\Stanowisko\dane\dzien_skanera\<data_godzina>`. Przycisk "Zrzut ekranu" i wspolpraca z prawdziwym
programem skanera: [NIE SPRAWDZONE BEZ SPRZETU] (PC testowy nie ma ekranu).

### Krok 2.2 - kroki 1-4 okna: ustawienia programu skanera (15 minut)

Co zrobic: idz za instrukcja w oknie. Zrzuty ekranow ustawien programu skanera, wersja, folder zapisu.
Niczego w programie skanera nie zmieniaj.

Udalo sie, gdy: w oknie po lewej kroki 1-4 sa odhaczone albo pominiete z powodem.
Gdy sie nie uda: "Nie udalo sie / pomijam, bo ..." i jedno zdanie. Idz dalej.
Arkusz: 2.2 (format pliku skanu i czy jest JEDEN plik na cala plytke - to bardzo wazne).

### Krok 2.3 - pierwszy skan: PUSTA plytka (10 minut)

Co zrobic: wyczysc stozki plytki. Zeskanuj pusta plytke (krok 5 okna). Zmierz czas stoperem.
Zapisz skan w programie skanera jako plik STL calej plytki, bez wygladzania i obcinania.

Udalo sie, gdy: plik sam pojawia sie w oknie (na PC po 2-3 s od zapisu), a chwile pozniej (na PC 6-11 s
od zapisu) okno pokazuje ocene:

- zielone "SKAN DOBRY: cala plytka, uklad ...; obrys ... x ... x ... mm; ..." - przepisz "obrys",
- czerwone "TEN SKAN SIE NIE NADA, bo na plytce nie widac trzech stozkow znacznikow" - patrz nizej,
- czerwone "... nie widac plaskiego wierzchu plytki" - skan zostal obciety przy zapisie.

Gdy plik sie nie pojawia: w programie skanera poszukaj "Explore" albo "Export"; w oknie "Dodaj folder...".
Gdy skaner zapisuje inny format niz STL: okno i tak skopiuje plik. Zapisz format w arkuszu.
Gdy ocena jest czerwona: zrob krok 2.4 na tym samym pliku - poda srednice pola. To moze byc glowny wynik
dnia: na skanach sztucznych przy polu 90 mm i mniejszym program nie rozpoznaje ZADNEJ plytki
(stozki siegaja 47 mm od srodka plytki, potrzeba ok. 94 mm), a przy 95 mm rozpoznaje.
Arkusz: 2.3.
Stan: oceny okna sprawdzone 21.11 na 10 skanach sztucznych (takie same z kopii programu i z instalacji:
10 z 10). Prawdziwy plik ze skanera: [NIE SPRAWDZONE BEZ SPRZETU] - nazwa, format, czas zapisu, to czy
jest jeden plik na plytke, szum i gestosc punktow.

### Krok 2.4 - pole skanera w liczbach (5 minut na plik)

Co zrobic: znajdz plik skanu - w folderze programu skanera albo w oknie "Dzien skanera": "Otworz folder
sesji", potem `kroki` i folder kroku. Przeciagnij go myszka na plik
`C:\Sprzet_testy\narzedzia\pole_skanu.cmd`. Na pytanie o numer wpisz numer wybity na plytce i Enter.
Po kilkunastu sekundach pojawi sie 6 ponumerowanych wierszy. Przepisz je do arkusza (albo zrob zdjecie).
To samo zapisuje sie w `C:\Sprzet_testy\wyniki\pole_skanu`.

Co mowia wiersze:

- wiersz 2 "POLE SKANERA MA OK. ... mm" - skan jest mniejszy niz plytka; ta liczba to srednica pola,
- wiersz 2 "CO NAJMNIEJ" - cala plytka jest w skanie; pole jest wieksze niz plytka (patrz nizej),
- wiersz 3 - w ilu z 72 kierunkow widac brzeg plytki,
- wiersz 4 - ile z 4 miejsc na dolki numeru jest w skanie i ktore maja wglebienie,
- wiersz 6 - czy widac scianke boczna plytki i jak gleboko (rowek pokrywki plytki okraglej ramkowej
  lezy 1,5-2,5 mm ponizej wierzchu).

Gdy cala plytka miesci sie w polu: poloz na stoliku skanera plaski karton wiekszy niz 15 x 15 cm,
zeskanuj, zapisz i przeciagnij ten plik na `pole_skanu.cmd`. Narzedzie napisze "Plytka: NIE ROZPOZNANA"
(to dobrze - to karton) i poda srednice kola, w ktorym sa dane. To jest srednica pola.

Udalo sie, gdy: masz w arkuszu srednice pola w mm.
Gdy sie nie uda: skopiuj plik skanu na pendrive - policzymy go na PC.
Arkusz: 2.4.
Stan: narzedzie sprawdzone 21.11 na 22 skanach sztucznych: gdy pole bylo mniejsze niz plytka
(70-120 mm, 14 skanow), podana srednica byla o 0,2-0,6 mm wieksza od prawdziwej. Na prawdziwym skanie:
[NIE SPRAWDZONE BEZ SPRZETU] - zwlaszcza scianka boczna i rowek (skaner patrzy z gory; skany sztuczne
nie maja rowka) oraz proba z kartonem (sprawdzona tylko na plaskiej siatce sztucznej).

### Krok 2.5 - kolejne skany wg okna (ok. 1 godziny)

Co zrobic: kroki 6-13 okna. Dla nas najwazniejsze, w tej kolejnosci:

1. plytka z 6-10 pracami calymi (krok 6 okna) i TO SAMO drugi raz bez ruszania (krok 7),
2. kazdy RODZAJ plytki, jaki masz (kwadratowa, okragla ramkowa, okragla testowa, stara) - po jednym
   skanie pustej plytki; kazdy plik przeciagnij na `pole_skanu.cmd`,
3. plytka okragla z praca w gniezdzie obok dolkow numeru - czy numer nadal sie odczytuje,
4. plytka z 2-3 pracami celowo ukruszonymi (krok 9) - zapisz, ktore gniazdo i gdzie ukruszenie.

Udalo sie, gdy: kazdy skan ma w oknie ocene, a w arkuszu wiersz w tabeli 2.5.
Gdy ocena jest zolta "inna plytka niz w skanie ..." albo czerwona "TEN SAM plik" - przeczytaj tekst po
"ZROB TAK"; plik i tak jest zachowany.
Arkusz: 2.5.
Stan: program 0.3.1 zna 8 ukladow (kwadratowe 1-6, okragle testowe 8 i 9, stare R54). Plytke okragla
ramkowa 1-6 moze nazwac inaczej (pomiar z planu 21.11: "okragla_wieczorna" zamiast ramkowej) - gniazda sa
te same, wiec skan jest przydatny. [ETAP 2: nazwy ukladow okraglych]

### Krok 2.6 - kopia folderu i "Zakoncz i spakuj" (10 minut)

Co zrobic: ostatni krok okna "Skopiuj caly folder zlecen skanera", potem "Zakoncz i spakuj".

Udalo sie, gdy: okno pisze "Sesja spakowana: ... plikow" i podaje sciezke pliku ZIP
(`C:\Stanowisko\dane\dzien_skanera\<data_godzina>\paczka\`). Lista brakow nie blokuje.
Gdy sie nie uda (np. brak miejsca): niczego nie kasuj; skopiuj caly folder sesji na pendrive.
Arkusz: 2.6.
Stan: sprawdzone 21.11 (sesja 20 plikow, 723 MB, pakowanie 14 s, sprawdzenie paczki: sumy 44 z 44).
Przycisk "Pomiar szczegolowy zaznaczonego skanu" w programie z paczki 0.3.1 NIE DZIALA (okno pomiaru
konczy sie bledem zaraz po starcie) - nie uzywaj go; pomiar zrobimy na PC z przywiezionych plikow.

### Krok 2.7 - program "Stanowisko" sam zauwaza prawdziwy skan (20 minut)

Co zrobic:

1. Zamknij okno "Dzien skanera". Otworz w Notatniku `C:\Stanowisko\ustawienia.toml` i w wierszu
   `folder_eksportu_skanera` wpisz folder programu skanera (z ukosnikami `/`). Zapisz.
2. `C:\Stanowisko\Samokontrola.cmd` - wiersz `OK folder_skanera`.
3. `C:\Stanowisko\Stanowisko.cmd`, kliknij "Tester".
4. Zeskanuj plytke z pracami i zapisz skan w programie skanera. Wlacz stoper w chwili zapisu.

Udalo sie, gdy: w programie po lewej pojawia sie kafelek "Plytka ...", a w srodku mapa gniazd. Zatrzymaj
stoper. Dla plytki kwadratowej program zapyta "Podaj numer plytki" - kliknij numer wybity na plytce.
Prace bez projektu STL sa szare "bez projektu" - dzis to wystarczy.
Co program pokazuje w innych przypadkach (sprawdzone 21.11 na skanach sztucznych, 10 z 10 tak samo
z kopii programu i z instalacji):

- "Analiza skanu nie powiodla sie ... Zeskanuj plytke ponownie" - program nie mowi dlaczego. Ten sam
  komunikat jest dla pliku, ktory nie jest plytka, i dla pola skanera za malego (80 i 90 mm). Ponowny
  skan wtedy nie pomoze: sprawdz plik krokiem 2.4.
- "Plik nie jest skanem" - plik uciety; zapisz skan jeszcze raz.
- nic sie nie dzieje - plik ma inne rozszerzenie niz `.stl` (program patrzy tylko na `*.stl`, takze w
  podfolderach) albo trafia do innego folderu.
- "Plytka nie z tego trybu" - plytka poranna w trybie "Wieczor"; kliknij "-> Poranek" w pasku albo
  uzyj plytki wieczornej.

Gdy sie nie uda: wroc do okna "Dzien skanera" (krok 2.1) - ono kopiuje kazdy plik. Zapisz, co widziales.
Arkusz: 2.7.
Stan: na skanach sztucznych: plik zauwazony 0,3 s po koncu zapisu (20 z 20), mapa po 26-41 s (plytki
wieczorne z 6 pracami; pusta plytka 4-7 s).
Na prawdziwym skanerze: [NIE SPRAWDZONE BEZ SPRZETU] - czy program skanera zapisuje plik jednym ruchem,
jak dlugo, pod jaka nazwa i czy nie trzyma go otwartego.

---

## Czesc 3 - ramka

Wystarczy jedna ramka. Zamknij program "Stanowisko" na czas krokow 3.3-3.7 i 3.9 (ramke obsluguje jeden
program naraz).

### Krok 3.1 - ogledziny i pasowanie, BEZ pradu (15 minut)

Co zrobic: wloz kazda plytke we wkladke. Sprobuj wlozyc ja obrocona o cwierc obrotu. Zaloz pokrywke
i odwroc. Zmierz suwmiarka plytke (bok albo srednica, grubosc) i otwor wkladki.

Udalo sie, gdy: plytka wchodzi lekko i lezy plasko tylko w jednym polozeniu. Plytka okragla ramkowa
obrocona ma lezec krzywo na zebrze (jedna krawedz ok. 4,5 mm wyzej) - widac to golym okiem. Plytka
kwadratowa ma wchodzic tylko jedna strona (sciety rog).
Gdy cos nie pasuje: zdjecie, wymiar do arkusza. Idz dalej.
Arkusz: 3.1.
Stan: wymiary znamy tylko z projektu. [NIE SPRAWDZONE BEZ SPRZETU]

### Krok 3.2 - wlaczenie pradu (5 minut)

Co zrobic: wloz wtyk zasilacza i wlacz stoper. Patrz na matryce.

Udalo sie, gdy: na brzegu matrycy pojawia sie niebieski pierscien (ramka gotowa). Plan zaklada mniej niz
60 s. Zatrzymaj stoper.
Gdy matryca jest ciemna po 3 minutach: na karcie SD prawdopodobnie nie ma programu ramki albo nie
startuje on sam (pytanie P3). Zapisz to i przeczytaj Zalacznik A. Mozesz przejsc do czesci 2 albo 4.
Arkusz: 3.2.
Stan: [NIE SPRAWDZONE BEZ SPRZETU] - start po wlaczeniu pradu, kolory, jasnosc, kierunek obrazu.
Na atrapie program ramki startuje w 0,5 s (bez systemu Raspberry Pi).

### Krok 3.3 - czy komputer widzi ramke (10 minut)

Co zrobic:

1. Polacz komputer z ta sama siecia co ramka (P6).
2. Kliknij dwa razy `C:\Sprzet_testy\narzedzia\ramka.cmd`. Na pytanie o adres wpisz `ramka-w.local`
   (wieczorna) albo `ramka-p.local` (poranna) i Enter. Potem wybierz `1` i Enter.

Udalo sie, gdy: pojawia sie wiersz `RAMKA ODPOWIADA (... ms): ramka wieczorna (W), program ramki ...`
i ponizej `plytka na ramce: 0`.
Gdy jest `BRAK POLACZENIA`: (a) sprawdz, czy ramka swieci; (b) zamiast nazwy wpisz adres z cyfr - znajdziesz
go na liscie urzadzen routera albo w Windows: Ustawienia -> Siec -> Hotspot mobilny -> podlaczone
urzadzenia; (c) sprawdz, czy komputer nie jest w innej sieci. Bez polaczenia zrob jeszcze 3.5 "na oko"
(napis na matrycy) i przejdz do czesci 2.
Arkusz: 3.3 (zapisz adres - bedzie potrzebny w 3.8).
Stan: narzedzie sprawdzone 21.11 na atrapie ramki z instalacji 0.3.1 (odpowiedz w 22-26 ms).
Nazwa `ramka-w.local`, Wi-Fi, adres w sieci i to, czy program ramki slucha w sieci (a nie tylko
"u siebie"): [NIE SPRAWDZONE BEZ SPRZETU].

### Krok 3.4 - test diod (2 minuty)

Co zrobic: w `ramka.cmd` wybierz `2`.

Udalo sie, gdy: cala matryca swieci kolejno na czerwono, zielono, niebiesko i bialo, razem 8 sekund,
potem wraca niebieski pierscien.
Gdy sa ciemne pola albo zle kolory: zdjecie kazdego koloru. Idz dalej.
Arkusz: 3.4.
Stan: polecenie sprawdzone na atrapie (4 kolory, powrot po 8,0 s). Prawdziwa matryca:
[NIE SPRAWDZONE BEZ SPRZETU].

### Krok 3.5 - odczyt numeru kazdej plytki (15 minut)

Co zrobic: w `ramka.cmd` wybierz `3`. Przez 5 minut kladz i zdejmuj plytki: kazda 5 razy.
Kazda zmiana pojawia sie na ekranie, np. `12:01:03.250  plytka 0 -> 2`, i trafia do pliku
`C:\Sprzet_testy\wyniki\ramka\plytki_<data>_<godzina>.csv`.

Udalo sie, gdy: po polozeniu plytki nr 2 jest `0 -> 2`, po zdjeciu `2 -> 0`, za kazdym razem.
Wedlug opisu programu ramki na matrycy przy lezacej plytce jest jej numer i napis "BRAK" (brak planu -
to normalne).
Gdy odczyt jest zly albo zaden: sprawdz, czy plytka ma magnesy i lezy plasko; zapisz numer wybity
i numer odczytany. Kod magnesow: 1 = A, 2 = B, 3 = A+B, 4 = C, 5 = A+C, 6 = B+C. Idz dalej.
Arkusz: 3.5 (tabela).
Stan: narzedzie sprawdzone na atrapie (zmiana odczytu po ok. 45 ms). Czujniki i magnesy:
[NIE SPRAWDZONE BEZ SPRZETU].

### Krok 3.6 - plytka krzywo i plytka nie od tej ramki (10 minut)

Co zrobic (dalej w trybie `3`): (a) poloz plytke obrocona, tak zeby lezala na zebrze; (b) poloz ja skosem,
jednym brzegiem; (c) poloz plytke drugiej ramki (np. nr 4 na wieczornej), jesli jest.

Udalo sie, gdy: dla (a) i (b) ramka czyta 0 albo nic sie nie zmienia. Kazdy inny numer zapisz - to wazne:
czujnik jest wtedy ok. 4 mm od magnesu i moze go "zlapac". Dla (c) na ekranie jest dopisek
`NUMER SPOZA TEJ RAMKI`.
Arkusz: 3.6.
Stan: [NIE SPRAWDZONE BEZ SPRZETU]. Program "Stanowisko" 0.3.1 w takiej sytuacji NIE ostrzega (sprawdzone
na atrapie: plytka 5 na ramce wieczornej - w pasku "W: gotowa (plytka 5)", bez komunikatu).
[ETAP 2: ostrzezenie o numerze niepasujacym do ramki]

### Krok 3.7 - gniazda i diody (20 minut)

Co zrobic: poloz na ramce plytke (pusta). W `ramka.cmd` wybierz `4` (wszystkie gniazda naraz).
Uklad: `wieczorna` dla ramki wieczornej, `poranna` dla porannej (stare plytki: `wieczorna_r54`,
`poranna_r54`). Przesuniecia: dwa razy sam Enter. Popatrz z gory i wpisz, co widzisz.

Udalo sie, gdy: kazdy otwor w dnie gniazda swieci, miedzy gniazdami jest ciemno.
Gdy swiatlo jest obok otworow: uruchom `4` jeszcze raz i podaj przesuniecie w diodach (1 dioda = 2,5 mm),
np. w prawo `1`, w dol `0`. Powtarzaj, az trafi; zapisz liczby w arkuszu. Potem wybierz `5` (po kolei):
swieci jedno gniazdo; Enter = dobrze, albo wpisz uwage; `k` = koniec.
Gdy narzedzie pisze `NA RAMCE NIE LEZY PLYTKA TEJ RAMKI`: ramka nie czyta numeru (krok 3.5) - bez
odczytu numeru ramka nie zapali gniazd. Zapisz i idz do 3.8.
Arkusz: 3.7.
Stan: narzedzie sprawdzone na atrapie (19 z 19 gniazd wieczornych i 24 z 24 porannych w swoich blokach
diod). Polozenia diod sa policzone z rysunku plytki, nikt ich nie widzial pod prawdziwa wkladka.
Plytka okragla ramkowa ma gniazda w tych samych miejscach co kwadratowa, wiec uzyj ukladu `wieczorna` /
`poranna`. [NIE SPRAWDZONE BEZ SPRZETU] [ETAP 2: uklady okragle w kalibracji]
Narzedzia, ktore przesuwa diody strzalkami i zapisuje kalibracje, jeszcze nie ma - dzis tylko notujemy.

### Krok 3.8 - program "Stanowisko" razem z ramka (20 minut)

Co zrobic:

1. Zamknij `ramka.cmd` (wybierz `0`). W `C:\Stanowisko\ustawienia.toml`, w sekcji `[ramki]`, wpisz adres
   z kroku 3.3: `wieczorna_host = "..."` albo `poranna_host = "..."`. Zapisz.
2. `C:\Stanowisko\Samokontrola.cmd` - ma byc wiersz `OK ramka_wieczorna: ramka wieczorna odpowiada`.
3. `C:\Stanowisko\Stanowisko.cmd`, kliknij "Tester". W pasku u gory: "Ramki: W: gotowa".
4. Poloz plytke na ramce: w pasku "W: gotowa (plytka 1)". Kliknij "Test LED".
5. Ramka wieczorna + skaner: zeskanuj plytke z pracami (jak w 2.7), podaj numer plytki, poloz TE plytke
   na ramce.

Udalo sie, gdy: pod plytka swieca gniazda z pracami, w kolorach jak na mapie na ekranie; po zdjeciu plytki
gasna (wieczorem po zdjeciu wynik nie wraca - trzeba nowego skanu).
Gdy w pasku jest "brak polaczenia": sprawdz adres; zamknij `ramka.cmd`. Gdy ramka jest ciemna dla plytki
okraglej: w wersji 0.3.1 to normalne [ETAP 2: plytki okragle na ramce].
Arkusz: 3.8.
Stan: sprawdzone 21.11 na atrapach z instalacji 0.3.1: ramki polaczone 3,7 s po starcie programu,
"Test LED" dociera w 0,1 s, po skanie kwadratu nr 1 ramka zapala 6 z 6 gniazd w kolorach mapy
(4 zielone, 2 zolte), po zdjeciu plytki 0 gniazd. Program pyta o numer plytki takze wtedy, gdy plytka
lezy na ramce - numeru z ramki nie bierze. Prawdziwa siec i ramka: [NIE SPRAWDZONE BEZ SPRZETU].

### Krok 3.9 - klawiatura ramki porannej (10 minut, tylko ramka poranna)

Co zrobic: poloz na ramce plytke 4, 5 albo 6. W `ramka.cmd` wybierz `6`. Naciskaj na klawiaturze ramki
po kolei: Enter; Backspace; 2 2 2 2 Enter; 9 Enter; gwiazdka, potem Enter.

Udalo sie, gdy: po kazdym kroku na ekranie komputera pojawia sie wiersz (np. "Enter: kuweta potwierdzona
1111"), a na koncu "rodzaje: 5 z 5".
Gdy klawisze nie reaguja: baterie, odbiornik USB w ramce, NumLock. Zapisz, ktore klawisze nie dzialaja.
Arkusz: 3.9.
Stan: sprawdzone na atrapie (5 z 5). Prawdziwa klawiatura: [NIE SPRAWDZONE BEZ SPRZETU].

---

## Czesc 4 - laptop stanowiska (tylko gdy testy sa na laptopie firmowym)

To sa sprawy 4-6 z listy rzeczy odlozonych. Wiekszosc danych zbiera sie sama w krokach 1.2 i 2.7.

- **4.1** Po krokach 2.7 i 3.8 nacisnij Windows + R, wpisz `cmd` i Enter. W czarnym oknie wpisz:

      findstr /c:"KnownDlls" /c:"proces silnika" C:\Stanowisko\dane\logi\stanowisko.log

  Policz wiersze, ktore sie pojawia. Ma byc 0 (nic sie nie wypisuje).
- **4.2** Czas analizy plytki: przepisz czasy ze stopera z kroku 2.7 (pierwsza plytka po starcie programu
  i kolejne). Plan: do 40 s. Na PC: 26-41 s (plytki wieczorne z 6 pracami sztucznymi).
- **4.3** Skalowanie ekranu: Ustawienia -> System -> Ekran. Zapisz procent i rozdzielczosc. Czy w programie
  widac wszystkie przyciski?
- **4.4** Czy folder OneDrive "Cyrkon" jest na tym laptopie (zsynchronizowany)? Zapisz sciezke.
- **4.5** Wolne miejsce na dysku.

Sprawa 4 (czy zapis na dysk zatrzymuje okno ponad 0,2 s) wymaga plikow testowych, ktorych nie ma w paczce.
Na ten weekend jej NIE robimy. [ETAP 2: gotowe polecenie albo osobny pendrive od koordynatora]

Stan: polecenie `findstr` sprawdzone na PC (na logu z proby: 0 wierszy). Reszta: [NIE SPRAWDZONE BEZ SPRZETU].

---

## Czesc 5 - co przywiezc i gdzie polozyc

Skopiuj na pendrive (nic nie kasuj na komputerze testowym, dopoki koordynator nie potwierdzi odbioru):

1. wszystkie pliki ZIP z `C:\Stanowisko\dane\dzien_skanera\<data_godzina>\paczka\`
2. caly folder `C:\Sprzet_testy\wyniki`
3. folder `C:\Stanowisko\dane\logi`, folder `C:\Stanowisko\dane\wyniki`, plik
   `C:\Stanowisko\dziennik_instalacji.txt`
4. zdjecia z telefonu: ramka, diody, plytka na zebrze, ekrany z bledami (bez twarzy, bez kart zlecen)
5. zdjecie albo skan wypelnionego arkusza

Na PC poloz to w folderze `<PC-katalog>\sprzet_2026-11-28\`, w podfolderach:

    <PC-katalog>\sprzet_2026-11-28\skaner\       <- pliki ZIP z punktu 1
    <PC-katalog>\sprzet_2026-11-28\wyniki\       <- folder z punktu 2 (pole_skanu, ramka)
    <PC-katalog>\sprzet_2026-11-28\program\      <- punkt 3 (logi, wyniki, dziennik_instalacji.txt)
    <PC-katalog>\sprzet_2026-11-28\zdjecia\      <- punkt 4
    <PC-katalog>\sprzet_2026-11-28\arkusz\       <- punkt 5

Czego NIE przywozic: folderu z projektami STL (nazwy plikow moga zawierac nazwiska), zlecen z danymi
pacjentow, pliku bazy programu. Okno "Dzien skanera" samo pomija w paczce pliki `*_cad.stl`. Przed
skopiowaniem przejrzyj nazwy plikow i folderow: bez nazwisk.

Uwaga do sesji "Dnia skanera": jesli ktos uruchomi okno inaczej niz przez `dzien_skanera.cmd` (np.
poleceniem `Polecenie.cmd -m stanowisko.dzien_skanera`), sesja zapisze sie w
`C:\Stanowisko\wersje\<wersja>\program\dane\dzien_skanera\` - zajrzyj tez tam. Nie uzywaj
`Wersje.cmd /usun`, dopoki pliki nie sa odebrane.

---

## Zbiorcza lista: czego NIE sprawdzono bez sprzetu

Skaner:

1. Format, nazwa i liczba plikow skanu; czy jest jeden plik calej plytki; jak i jak dlugo program skanera
   zapisuje plik (kroki 2.2, 2.3, 2.7).
2. Srednica pola skanera (projekt zaklada 100 mm - niezmierzone) i polozenie plytki w polu (2.4).
3. Czy skaner widzi dolki numeru (srednica 2 mm, glebokosc 1 mm, ok. 43,5 mm od srodka plytki okraglej;
   52-58 mm na kwadratowej) i trzy stozki (do 47 mm od srodka) (2.3, 2.4).
4. Czy skaner widzi scianke boczna plytki i rowek pokrywki (2.4).
5. Szum, gestosc punktow, czas skanu; wynik dla prac prawdziwych, ukruszonych, spieczonych (2.5).
6. Przycisk "Zrzut ekranu" w oknie "Dzien skanera" na prawdziwym ekranie (2.1).
7. Czy nasz program moze dzialac na komputerze skanera obok programu skanera (pamiec, karta graficzna).

Ramka:

8. Wszystko, co dotyczy Raspberry Pi: karta SD, instalacja programu ramki, start po wlaczeniu pradu,
   czas startu (plan: do 60 s), praca kilka godzin, temperatura (3.2, Zalacznik A).
9. Matryca diod: kolory, jasnosc, kierunek obrazu (obrot, odbicie lustrzane) (3.4).
10. Czujniki i magnesy: odczyt kazdego numeru, czas odczytu (plan: do 0,1 s), plytka krzywo na zebrze,
    plytka zdejmowana skosem (3.5, 3.6).
11. Polozenie diod pod gniazdami, takze pod wkladka okragla (3.7).
12. Siec: nazwa `ramka-w.local`, Wi-Fi w pracowni, hotspot, zapora Windows dla innego urzadzenia (3.3, 3.8).
13. Klawiatura numeryczna: kody klawiszy, NumLock, zasieg odbiornika (3.9).
14. Pasowanie plytek, wkladki i pokrywki; zebro orientujace (3.1).

Komputer:

15. Instalacja na laptopie firmowym: antywirus, uprawnienia, ostrzezenia Windows, Notatnik (1.1, 1.2).
16. Wyglad okien na ekranie laptopa przy skalowaniu 125 / 150 % (1.3, 4.3).
17. Czas analizy plytki i zachowanie programu na wolniejszym laptopie (4.1, 4.2).

## Zbiorcza lista: miejsca do domkniecia w etapie 2

1. Numer i nazwa nowej paczki programu (kroki 1 i 1.2); czy liczby instalatora sa takie same.
2. Nazwy ukladow plytek okraglych ramkowych 1-6 i to, czy program je rozpoznaje (P2, 2.5).
3. Plytki okragle na ramce: kalibracja diod i ostrzezenie o numerze niepasujacym do ramki (3.6, 3.7, 3.8).
4. Skrot do okna "Dzien skanera" w paczce i katalog jego sesji (2.1, czesc 5).
5. Czy narzedzia `pole_skanu` i `ramka_proba` wejda do paczki; powtorzenie ich prob na nowej instalacji (1.4).
6. Komunikat programu przy skanie bez trzech stozkow / przy za malym polu (2.7).
7. Przycisk "Pomiar szczegolowy" w oknie "Dzien skanera" (2.6).
8. Instrukcja i instalator programu ramki na Raspberry Pi (Zalacznik A).
9. Sprawa 4 laptopa - gotowe polecenie (czesc 4).

---

## Zalacznik A - gdy Raspberry Pi nie ma jeszcze programu ramki

To jest opis z dokumentacji programisty (`ramka/README.md`), NIE gotowa instrukcja. Nikt tego nie wykonal.
Calosc: **[NIE SPRAWDZONE BEZ SPRZETU]**. Potrzebna jest osoba, ktora zna Linuksa, internet i ok. 1-2 godziny.
Jesli nie czujesz sie pewnie - nie rob tego; zapisz w arkuszu "P3: brak programu ramki" i zglos koordynatorowi.

Co musi byc na karcie SD (w tej kolejnosci):

1. System "Raspberry Pi OS Lite 64-bit" wgrany programem Raspberry Pi Imager. W ustawieniach Imagera:
   nazwa urzadzenia `ramka-w` (wieczorna) albo `ramka-p` (poranna), wlaczone SSH, nazwa i haslo sieci Wi-Fi.
2. W pliku `config.txt`: `dtparam=spi=off` i `dtparam=audio=off`; w `cmdline.txt`: `isolcpus=3`.
   Na nakladce diod (Bonnet): zworka E -> 8 i polaczenie GPIO4-GPIO18.
3. Biblioteki: `sudo apt install python3-gpiozero python3-evdev` oraz biblioteka matrycy
   `rpi-rgb-led-matrix` zbudowana z dodatkiem dla Pythona (wymaga internetu i kompilacji).
4. Program ramki: folder `C:\Stanowisko\wersje\<wersja>\program\ramka` skopiowany na Raspberry Pi jako
   `/opt/ramka/ramka` (np. poleceniem `scp -r` z komputera).
5. Reczny start na probe (wieczorna; poranna: `--rola P`):

       cd /opt/ramka
       sudo python3 -m ramka --rola W --sprzet rpi --host 0.0.0.0

   Opcje sa sprawdzone tylko na PC: bez bibliotek sprzetu program konczy sie wierszem
   "sprzet niedostepny: brak biblioteki rgbmatrix" (kod 2). Na Raspberry Pi nie byl uruchamiany.
6. Start samoczynny po wlaczeniu pradu (usluga systemowa) i karta "tylko do odczytu" - opis w
   `ramka/README.md`, punkty 5 i 6. Bez tego krok 3.2 (czas startu) nie ma sensu.

Paczka programu zawiera folder `program\ramka` (pliki programu ramki), ale NIE zawiera: instrukcji dla
osoby niebedacej programista, skryptu instalujacego, pliku uslugi, pliku konfiguracji ani biblioteki
matrycy. [ETAP 2: instrukcja i instalator programu ramki]
