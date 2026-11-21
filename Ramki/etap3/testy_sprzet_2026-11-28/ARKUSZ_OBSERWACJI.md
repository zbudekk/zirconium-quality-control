# Arkusz obserwacji - pierwsze testy na sprzecie 28-29.11.2026

Wydrukuj. Wypelniaj dlugopisem w trakcie testow. Numery jak numery krokow w dokumencie
`PIERWSZE_TESTY_NA_SPRZECIE.md`. Bez nazwisk pacjentow i nazw zlecen. Puste pole = "nie robilem".
Gdy cos poszlo inaczej, niz pisze dokument - zapisz JAK. To najcenniejsza informacja z calego dnia.

Data: ...........  Godzina startu: ........  Kto: ......................  Komputer: ................

## Odpowiedzi na pytania P1-P9

Termin: sroda 25.11.2026 (plik `PYTANIA_DO_WLASCICIELA.md`); tu wpisz to samo.

- P1. Ramka: [ ] wieczorna  [ ] poranna  [ ] obie.   Wkladka: [ ] kwadratowa  [ ] okragla
- P2. Plytki na miejscu (zakresl numery):  kwadratowe: 1 2 3 4 5 6    okragle ramkowe: 1 2 3 4 5 6
  okragle testowe: 8 9    stare R54: ....................
  Magnesy wklejone: [ ] we wszystkich  [ ] w czesci: ....................  [ ] nie
- P3. Raspberry Pi w ramce: [ ] zlozone z matryca diod i czujnikami   [ ] karta SD jest
  Program ramki wgrany na karte: [ ] tak  [ ] nie  [ ] nie wiem
  Kto wgrywa i kiedy: ..............................................................
- P4. Komputer: [ ] laptop stanowiska  [ ] PC  [ ] inny: .................   Windows: [ ] 10  [ ] 11
- P5. Skaner przy tym samym komputerze: [ ] tak  [ ] nie, przy: ............................
  Folder, do ktorego program skanera zapisuje skany: ..........................................
- P6. Siec: [ ] router w pracowni  [ ] hotspot z laptopa  [ ] hotspot z telefonu  [ ] kabel
  Nazwa sieci wpisanej w ramce: ..............................
- P7. Projekty STL prac probnych: [ ] mam, ile: ......  [ ] nie mam
- P8. Klucz ramki: [ ] znam  [ ] nie znam  [ ] ramka jest bez klucza.
  Klucz przepisany do `klucz_ramki.txt`: [ ]      Samego klucza w arkuszu NIE zapisujemy.
- P9. W programie skanera sa zlecenia pacjentow: [ ] tak  [ ] nie  [ ] nie wiem
  Folder na skany testowe z tego dnia: ..........................................................

## Czesc 1 - komputer i program

- 1.1 Python 3.12: [ ] byl juz  [ ] dzis, "Setup was successful"  [ ] blad: ...........
- 1.2 Instalacja. Paczka (nazwa pliku): ........................................   czas: ...... min
  Pierwsze `zainstaluj.cmd` - ostatni wiersz: ....................................................
  Drugie `zainstaluj.cmd`: [ ] INSTALACJA: GOTOWA  [ ] inaczej: ..................................
  Wiersze `BLAD:` / `CO ZROBIC:` (przepisz): ......................................................
  ..............................................................................................
  Windows albo antywirus pytal o zgode: [ ] nie  [ ] tak, o co: ..................................
- 1.3 `Samokontrola.cmd`: [ ] ZIELONA  [ ] CZERWONA.   Wiersz `OK modele: ... poprawne ...... z 10`
  Wiersze BLAD (nazwy): ..........................................................................
  Program `Stanowisko.cmd`: okno sie otworzylo [ ] tak, po ...... s  [ ] nie: ......................
- 1.4 Narzedzia skopiowane do `C:\Sprzet_testy`: [ ]
  Dwuklik na `ramka.cmd` dziala: [ ]    Przeciaganie pliku na `pole_skanu.cmd` dziala: [ ]

## Czesc 2 - skaner

- 2.1 Okno "Dzien skanera" (`C:\Stanowisko\Dzien_skanera.cmd`) otwarte: [ ] tak  [ ] nie
  Folder obserwowany ("Obserwuje:"): ..............................................................
- 2.2 Format pliku skanu: [ ] STL  [ ] PLY  [ ] OBJ  [ ] inny: ........
  JEDEN plik na cala plytke: [ ] tak  [ ] nie, osobne pliki na: ..............................
  Nazwa przykladowego pliku skanu (bez nazwisk): ..............................................
- 2.3 Pierwszy skan - PUSTA plytka: ........................ numer wybity: .....
  Czas skanu: ...... min ...... s.    Plik pojawil sie w oknie po: ...... s   [ ] nie pojawil sie
  Ocena w oknie: [ ] zielona  [ ] czerwona.  Tekst: ................................................
  Obrys: ........ x ........ x ........ mm.     W podgladzie skanu widac stolik / podstawke: [ ] tak  [ ] nie
  Linie ciecia da sie ustawic miedzy stolikiem a wierzchem plytki: [ ] tak  [ ] nie: ...............
  Dwa skany tej samej plytki (gdy byl skan z podlozem albo czerwony):
  (A) ciecie tuz nad stolikiem:  plik ..................  ocena: [ ] zielona [ ] czerwona  PODLOZE: [ ]
  (B) ciecie 3 mm pod wierzchem: plik ..................  ocena: [ ] zielona [ ] czerwona  PODLOZE: [ ]
- 2.4 Pole skanera (`pole_skanu.cmd`). NAJPIERW karton (glowny pomiar), godzina wyniku: ...........
  [ ] "Dane mieszcza sie w kole o srednicy ok. ........ mm"
  [ ] "DANE NIE SA KOLEM: ........ x ........ mm"          "Dane sa PLASKIE": [ ]
  Potem skan plytki z kroku 2.3 (pomocniczo, przyblizone) - zaznacz jedno:
  [ ] cala plytka w skanie (pole jest co najmniej takie jak plytka)
  [ ] "POLE SKANERA MA OK. ........ mm"
  [ ] "POLE NIE JEST KOLEM: ........ x ........ mm";  "Konce danych pasuja do okregu ........ mm"
  [ ] "wielkosci pola z tego skanu nie da sie podac"
- 2.5 Tabela skanow. Kazdy plik przeciagnij na `pole_skanu.cmd`; na pytanie "Co lezy na stoliku?" wpisz
  to samo, co w kolumnach "plytka naprawde" i "co na niej". Reszte przepisz z bloku "DO ARKUSZA".
  "Godz." = godzina z wiersza "Zapisano: ..." (po niej znajdziemy plik wyniku).
  Plytka naprawde: kw / okr-ramk / okr-test / stara + nr.

     nr | godz.  | plytka naprawde | co na niej   | program mowi     | nr z   | dolki | scianka | brzeg
        | wyniku | (rodzaj + nr)   | (pusta/prace)| (rodzaj; pewnie  | dolkow | z 4   | T/N,    | z 72
        |        |                 |              |  T/N)            |        |       | do mm   |
     ---|--------|-----------------|--------------|------------------|--------|-------|---------|------
      1 |        |                 |              |                  |        |       |         |
      2 |        |                 |              |                  |        |       |         |
      3 |        |                 |              |                  |        |       |         |
      4 |        |                 |              |                  |        |       |         |
      5 |        |                 |              |                  |        |       |         |
      6 |        |                 |              |                  |        |       |         |
      7 |        |                 |              |                  |        |       |         |
      8 |        |                 |              |                  |        |       |         |

  Wiersz `podloze w skanie:` inny niz "nie" - w ktorych skanach: ..................................
  Rowek pokrywki (plytka okragla ramkowa; wiersz `rowek pokrywki:`):
  skan nr ....: scianka cofa sie o ........ mm w ...... z 72 kierunkow
  skan nr ....: scianka cofa sie o ........ mm w ...... z 72 kierunkow
  skan nr ....: scianka cofa sie o ........ mm w ...... z 72 kierunkow
- 2.5a Plytki okragle - czy program poznaje ksztalt. Minimum: 1 okragla ramkowa, 1 okragla testowa,
  1 kwadratowa pusta (tylko i). W kratce: godzina wyniku; kw albo okr (co mowi program); pewnie T/N;
  numer z dolkow; scianka boczna T/N.

      plytka naprawde      | (i) pusta          | (ii) praca przy    | (iii) dolki
      (rodzaj + numer)     |                    |      dolkach       |       zaklejone
      ---------------------|--------------------|--------------------|--------------------
                           |                    |                    |
                           |                    |                    |
                           |                    |                    |
                           |                    |                    |
                           |                    |                    |
                           |                    |                    |

  Ile razy plytka OKRAGLA zostala nazwana KWADRATOWA: (i) ...... (ii) ...... (iii) ...... z ...... skanow
  Ile minut zajal jeden skan z zapisem i narzedziem: ......
- 2.6 Kopia calego folderu zlecen: [ ] zrobiona (same zlecenia testowe)  [ ] pominieta: dane pacjentow
  "Zakoncz i spakuj": [ ] zrobione.  Liczba plikow: ........  Nazwa pliku ZIP: .................
- 2.7 Program "Stanowisko" sam zauwaza skan. Czas od zapisu do mapy: ...... s  (drugi: ...... s)
  Plytka kwadratowa: numer odczytal sam [ ]  /  zapytal o numer [ ]
  Plytka okragla:    numer odczytal sam [ ]  /  zapytal o numer [ ]
  Mapa okragla ze scieciem z przodu po prawej: [ ]
  Komunikat "Analiza skanu nie powiodla sie" - przepisz tekst w nawiasie
  (np. "w skanie widac .... z 3 znacznikow"): ....................................................
  ..............................................................................................
  Skad skopiowano pliki skanow z tego kroku (folder): ............................................

## Czesc 3 - ramka

- 3.1 Bez pradu. Plytka: bok / srednica ........ mm, grubosc ........ mm; otwor wkladki ........ mm
  Plytka wchodzi: [ ] lekko  [ ] ciasno  [ ] nie wchodzi.    Plytka obrocona lezy krzywo: [ ]
- 3.2 Czas od wlaczenia pradu do niebieskiego pierscienia: ...... s    [ ] nie zaswiecila
- 3.3 Adres ramki: ..............................   (`ramka.cmd`, pozycja 1)
  "RAMKA ODPOWIADA": [ ]   czas odpowiedzi: ...... ms       "BRAK POLACZENIA": [ ]
  "wymaga klucza": [ ]     klucz przyjety ("KLUCZ DOBRY"): [ ]
- 3.4 Test diod (pozycja 2): czerwony [ ]  zielony [ ]  niebieski [ ]  bialy [ ]
  Ciemne pola (gdzie): ..........................................................................
- 3.5 Odczyt numeru plytki (pozycja 3). Kazda plytke poloz i zdejmij 5 razy.

      plytka (rodzaj + numer wybity) | ile razy polozona | ile razy dobry odczyt | zle odczyty
      -------------------------------|-------------------|-----------------------|-------------
                                     |                   |                       |
                                     |                   |                       |
                                     |                   |                       |
                                     |                   |                       |
                                     |                   |                       |
                                     |                   |                       |
                                     |                   |                       |
                                     |                   |                       |

- 3.6 Plytka na zebrze (obrocona): odczyt ........     Plytka skosem: odczyt ........
  Plytka drugiej ramki: dopisek "NUMER SPOZA TEJ RAMKI" [ ]
- 3.7 Gniazda i diody (pozycje 4 i 5). Kierunki jak w narzedziu: w prawo / w lewo / w dol / w gore,
  patrzac z gory od przodu ramki. Przesuniecie w diodach.
  Wkladka kwadratowa: rodzaj plytki wybrany w narzedziu: ....................
  przesuniecie w prawo ...... w dol ......;  gniazd swieci dobrze: ...... z ......
  Wkladka okragla:    rodzaj plytki wybrany w narzedziu: ....................
  przesuniecie w prawo ...... w dol ......;  gniazd swieci dobrze: ...... z ......
  Gniazda, ktore nie trafiaja (numery): ..........................................................
- 3.8 Program "Stanowisko" z ramka. Klucz i adres wpisane w ustawienia: [ ]    `OK ramka_...`: [ ]
  Gniazda swieca w kolorach mapy: [ ]       Plytka okragla ramkowa swieci: [ ]
  Po zdjeciu i ponownym polozeniu plytki: [ ] ciemno  [ ] swieci znowu
  Proby celowe (kratka = panel byl i ramka ciemna):
  [ ] (a) "Plytka lezy na zlej ramce"     [ ] (b) "Na ramce lezy inna plytka niz zeskanowana"
  [ ] (c) "Numer plytki nie zgadza sie ze skanem" (plytka okragla, "Zmien numer"); po powrocie do
      wlasciwego numeru ramka swieci: [ ]
  Pytanie "Ponowny skan tej samej plytki?": [ ] bylo, ile razy: ....  odpowiedz: ...................
  [ ] "Dwa skany z numerem plytki ... - ramka czeka na odpowiedz"    po "Tak" ramka swieci: [ ]
  Komunikaty BEZ proby celowej (ktory, ile razy, przy jakiej plytce): ............................
  ..............................................................................................
  Ramka poranna (tryb "Poranek"): gniazda swieca po skanie [ ]   wynik wraca po ponownym polozeniu [ ]
  [ ] "Plytka na ramce czeka na numer skanu"   [ ] "Na ramce lezy plytka, ktorej nie ma w planie pieca"
  Skad skopiowano pliki skanow z tego kroku (folder): ............................................
- 3.9 Klawiatura ramki porannej (pozycja 6): rodzaje ...... z 5.  Klawisze niedzialajace: ..........

## Czesc 4 - laptop stanowiska (tylko gdy testy byly na laptopie)

- 4.1 Liczba wierszy wypisanych przez `findstr`: ......   (ma byc 0)
- 4.2 Czas analizy plytki: pierwsza ...... s, kolejne ...... s, ...... s
- 4.3 Skalowanie ekranu: ...... %   Rozdzielczosc: ...... x ......   Widac wszystkie przyciski: [ ]
- 4.4 Folder OneDrive "Cyrkon": [ ] jest, sciezka: .....................................  [ ] nie ma
- 4.5 Wolne miejsce na dysku: ........ GB

## Czesc 5 - co przywiezione

- [ ] paczki ZIP "Dnia skanera"
- [ ] folder `C:\Sprzet_testy\wyniki`
- [ ] pliki skanow z krokow 2.7 i 3.8 (folder zlecenia testowego)
- [ ] `C:\Stanowisko\dane\logi`, `dane\wyniki`, `ustawienia.toml`, `dziennik_instalacji.txt`
- [ ] zdjecia (ramka z plytka, ekran) - bez twarzy, bez kart zlecen
- [ ] ten arkusz

## Uwagi / co poszlo inaczej

..............................................................................................

..............................................................................................

..............................................................................................

..............................................................................................

..............................................................................................

..............................................................................................
