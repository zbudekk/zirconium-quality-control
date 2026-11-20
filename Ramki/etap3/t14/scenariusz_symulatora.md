# Proba T14 - scenariusz symulatora (dla prowadzacego)

Symulator to skrypt `symulator_t14.py`: otwiera prawdziwe okno programu na danych sztucznych i udaje skaner. Kazde
nacisniecie Spacji w oknie programu = po 8 sekundach (pasek przy "Analiza" pokazuje postep) program dostaje kolejny skan
z pliku `scenariusz_t14.json`. Spacja nacisnieta w czasie czekania jest pomijana. Nie ma tu skanera, analizy skanu, ramek
ani Excela - sprawdzamy, czy czlowiek rozumie ekran.

Tekst w cudzyslowie to doslowny napis z ekranu programu (pisownia bez polskich znakow).

## Polecenia

Dwa sposoby uruchomienia - polecenia roznia sie tylko poczatkiem (`PY`) i sciezkami:

- **Program zainstalowany z paczki wydania** (laptop stanowiska; katalog instalacji np. `C:\Stanowisko`): skopiuj caly
  katalog `Ramki\etap3\t14` na laptop, np. jako `C:\T14`. `PY` = `C:\Stanowisko\Polecenie.cmd` (Python zainstalowanej
  wersji; sam przechodzi do katalogu programu), skrypt i dziennik z pelna sciezka, program wskazany kropka:
  `C:\Stanowisko\Polecenie.cmd C:\T14\symulator_t14.py wieczor --program . --dziennik C:\T14\t14_wieczor.log`.
  Dziennik zawsze poza katalogiem programu (plik dopisany do katalogu programu psuje sumy w `Samokontrola.cmd`).
  Program `Stanowisko.cmd` ma byc w tym czasie zamkniety; symulator nie dotyka danych ani ustawien stanowiska (wlasna baza
  w katalogu tymczasowym).
- **Kopia repozytorium** (komputer programisty): okno polecen w katalogu `Ramki\etap3\t14`, `PY` = `py -3.12` z pakietami
  programu z `Ramki\stanowisko\requirements.txt`; program jest brany z `..\..\stanowisko`.

Polecenia (zapis dla kopii repozytorium; na laptopie stanowiska dopisz sciezki jak wyzej):

1. Sprawdzenie zestawu bez ekranu (ok. 15 s): `PY symulator_t14.py --sprawdz` - ostatni wiersz ma brzmiec
   `SPRAWDZENIE T14 BEZ EKRANU: zgodne 22 z 22 krokow`.
2. Czesc wieczorna: `PY symulator_t14.py wieczor --dziennik t14_wieczor.log`
3. Czesc poranna (po zamknieciu okna czesci wieczornej): `PY symulator_t14.py rano --dziennik t14_rano.log`

Kazde uruchomienie zaczyna od zera (baza w katalogu tymczasowym, usuwana przy zamknieciu okna) - probe mozna powtarzac.
Okno polecen (i plik dziennika) wypisuje z godzina: kazda Spacje, kazdy podany skan i kazde polecenie osoby, ktore zmienilo
stan programu (wiersze `osoba: ...` - decyzja z plytka i gniazdem, cofniecie, odpowiedz na pytanie o ponowny skan, wybor
projektu, kuweta rozlozona / cofnieta / wybrana, piec zamkniety), a po zamknieciu okna programu podsumowanie (plytki,
decyzje, lista; rano: piec, kuwety rozlozone przed zamknieciem pieca, kompletne, braki). Dziennik nie widzi klikniec, ktore
niczego nie zmienily (np. otwarcie pracy). Opcja `--opoznienie S` zmienia czas od Spacji do skanu.

## Wieczor - co podaje symulator

Program startuje w trybie "Wieczor" i pyta "Kto teraz pracuje?" (osoby fikcyjne: Technik A, Technik B).

| Zadanie | Spacja nr | Co podaje symulator | Co ma byc na ekranie po poprawnym wykonaniu | Krok sprawdzenia bez ekranu |
|---------|-----|--------------------------|--------------------------------------|---------|
| W1 zeskanuj plytke | 1 | plytka 1: 11 prac | mapa plytki 1; nad mapa "do obejrzenia: 4" | 1-3 |
| W2 wskaz prace do obejrzenia | - | - | czerwone "UBYTEK" w gniazdach 3 i 11, zolte "sprawdz" w 6, szare "bez projektu" w 15 | 4-5 |
| W3 jedna ukruszona, jedna cala | - | - | jedno gniazdo "UKRUSZONA", jedno "OK - zatwierdzona" | 6-7 |
| W4 popraw ulozenie | 2 | plytka 2: gniazdo 4 "popraw ulozenie" | po W3 na plytce 1 zostaja 2 prace bez decyzji, wiec ekran ZOSTAJE na plytce 1: z lewej, nad lista plytek, przycisk "Pokaz nowy wynik: Plytka 2", pod nim pole "Nowy wynik czeka: Plytka 2". Dopiero po kliknieciu przycisku (albo po decyzjach o 2 pozostalych pracach): komunikat "Skan do powtorzenia" z powodem "popraw ulozenie pracy (gniazdo 4)" | 8-9 |
| W4 ciag dalszy | 3 | plytka 2 jeszcze raz, same zielone | pytanie "Ponowny skan tej samej plytki?" (naglowek mapy: "nowy skan, czeka na odpowiedz"); po "Tak, to ponowny skan" plytka 2 zielona, komunikat znika | 10 |
| W5 lista do dofrezowania | - | - | "Do dofrezowania: 1": kuweta 9003 albo 9011, zab, krazek K-1 | 11 |

Czwarta Spacja (zapas): plytka 3, trzy prace zielone. Piata i dalsze: nic nie przychodzi (wpis w oknie polecen).

## Rano - co podaje symulator

Program startuje w trybie "Poranek" i pyta "Kto teraz pracuje?". Ramki i Excela nie ma: program pokazuje
"Ramka poranna nie jest podlaczona" (od razu) i "Excel nie jest podlaczony" (po zamknieciu pieca) - to nie sa bledy proby.

| Zadanie | Spacja nr | Co podaje symulator | Co ma byc na ekranie po poprawnym wykonaniu | Krok sprawdzenia bez ekranu |
|---------|-----|--------------------------|--------------------------------------|---------|
| R1 zeskanuj 2 plytki pieca | 1 i 2 | plytka 6: 6 prac, gniazdo 7 zolte; plytka 5: 3 prace | dwie plytki; piec otwarty | 13-14 |
| R2 rozstrzygnij dwuznaczna | - | - | po kliknieciu gniazda 7 plytki 6: "Ktory to projekt?" i dwaj kandydaci (kuwety 3291 i 3312); po "To ten projekt" gniazdo zielone | 15, 17 |
| R3 rozloz jedna kuwete | - | - | pierwsza biezaca "Kuweta 3277" (4 prace, plytki 5 i 6); po Enterze stan "rozlozona", biezaca "Kuweta 3284" | 18 |
| R4 cofnij pomylke | - | - | po Enterze i Backspace kuweta 3284 znowu biezaca | 19 |
| R5 znajdz kuwete po numerze | - | - | po wpisaniu 3298 i Enterze biezaca "Kuweta 3298" (plytka 5, gniazdo 5) | 20 |
| R6 zamknij piec i braki | - | - | po "Zamknij piec": kompletne 3277, 3284, 3291; "Braki w tym piecu: 2" - kuwety 3298 i 3305 | 21 |

Kuwety, plytki i gniazda proby sa celowo INNE niz na obrazkach jednej strony (tam: plytki 4 i 5, kuwety 3221-3242) -
obrazek nie podpowiada odpowiedzi.

Wybor drugiego kandydata w R2 (kuweta 3312) tez jest decyzja zapisana przez program, ale wtedy zlecenie 3291 nie bedzie
kompletne - zapisz to w arkuszu jako blad wykonania, nie jako blad programu.

Gdy osoba kliknie "Zamknij piec" przed rozstrzygnieciem zoltej pracy (pominie R2), program pyta
"Zamknac piec mimo prac bez rozstrzygniecia?" z przyciskami "Zamknij piec mimo to" i "Wroc do rozstrzygania" (Esc = wroc;
krok 16 sprawdzenia). Po "Zamknij piec mimo to" listy beda inne niz w arkuszu (zlecenia 3291 nie ma w kompletnych) - zapisz
to jako blad wykonania R2.

Trzecia Spacja (zapas): plytka 4, dwie prace rozpoznane. Czwarta i dalsze: nic nie przychodzi.

## Co sprawdzono 20.11.2026 na PC, a czego nie

- Sprawdzone automatycznie, bez ekranu (`--sprawdz`): 22 z 22 krokow - skrypt sam naciska Spacje, klika gniazda i przyciski
  w oknie programu i czyta wynik z ekranu; obejmuje 11 z 11 zadan T14, pole "Nowy wynik czeka: Plytka 2" (krok 8), pytanie przed
  zamknieciem pieca (krok 16) i wiersze `osoba: ...` dziennika (kroki 12 i 22). Uruchomienie `wieczor` i `rano` bez ekranu
  z samym otwarciem i zamknieciem okna (`--zamknij-po 3`): kod 0. Stan programu: po paczkach E3-P14, A11s, A11i, A11w.
- NIE sprawdzone: uruchomienie przez `Polecenie.cmd` z programu zainstalowanego z paczki wydania (na PC sprawdzono tylko
  te sama postac polecenia - katalog biezacy = katalog programu, `--program .`, skrypt i dziennik z pelna sciezka).
- NIE sprawdzone: okno na prawdziwym ekranie (rozmiar, czytelnosc, mysz i klawiatura czlowieka), czas 8 s jako odczucie
  czekania, druk jednej strony na drukarce pracowni, przebieg z osoba badana. To jest wlasciwa proba T14 - wykonuje ja
  wlasciciel.
- Symulator nie jest programem skanera: w pracy skan uruchamia sie w programie skanera, a program tylko czeka na plik.
  Proba z prawdziwym skanerem to powtorka T14 na stanowisku (plan etapu 3, definicja pracy produkcyjnej).
