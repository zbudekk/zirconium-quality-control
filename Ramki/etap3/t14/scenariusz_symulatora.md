# Proba T14 - scenariusz symulatora (dla prowadzacego)

Symulator to skrypt `symulator_t14.py`: otwiera prawdziwe okno programu na danych sztucznych i udaje skaner. Kazde
nacisniecie Spacji w oknie programu = po 8 sekundach (pasek przy "Analiza" pokazuje postep) program dostaje kolejny skan
z pliku `scenariusz_t14.json`. Spacja nacisnieta w czasie czekania jest pomijana. Nie ma tu skanera, analizy skanu, ramek
ani Excela - sprawdzamy, czy czlowiek rozumie ekran.

Tekst w cudzyslowie to doslowny napis z ekranu programu (pisownia bez polskich znakow).

## Polecenia

Okno polecen w katalogu `Ramki\etap3\t14` kopii repozytorium. `PY` = Python 3.12 z pakietami programu (w kopii roboczej
`py -3.12`; na PC koordynatora `<PC-katalog>\koordynator\narz\py.cmd`). Program zainstalowany gdzie indziej: dodaj
`--program KATALOG` (katalog z pakietem `stanowisko`).

1. Sprawdzenie zestawu bez ekranu (ok. 10 s): `PY symulator_t14.py --sprawdz` - ostatni wiersz ma brzmiec
   `SPRAWDZENIE T14 BEZ EKRANU: zgodne 18 z 18 krokow`.
2. Czesc wieczorna: `PY symulator_t14.py wieczor --dziennik t14_wieczor.log`
3. Czesc poranna (po zamknieciu okna czesci wieczornej): `PY symulator_t14.py rano --dziennik t14_rano.log`

Kazde uruchomienie zaczyna od zera (baza w katalogu tymczasowym, usuwana przy zamknieciu okna) - probe mozna powtarzac.
Okno polecen wypisuje kazda Spacje i kazdy podany skan, a po zamknieciu okna programu podsumowanie (plytki, decyzje,
lista; rano: piec, kuwety, kompletne, braki). Opcja `--opoznienie S` zmienia czas od Spacji do skanu.

## Wieczor - co podaje symulator

Program startuje w trybie "Wieczor" i pyta "Kto teraz pracuje?" (osoby fikcyjne: Technik A, Technik B).

| Zadanie | Spacja nr | Co podaje symulator | Co ma byc na ekranie po poprawnym wykonaniu | Krok sprawdzenia bez ekranu |
|---------|-----|--------------------------|--------------------------------------|---------|
| W1 zeskanuj plytke | 1 | plytka 1: 11 prac | mapa plytki 1; nad mapa "do obejrzenia: 4" | 1-3 |
| W2 wskaz prace do obejrzenia | - | - | czerwone "UBYTEK" w gniazdach 3 i 11, zolte "sprawdz" w 6, szare "bez projektu" w 15 | 4-5 |
| W3 jedna ukruszona, jedna cala | - | - | jedno gniazdo "UKRUSZONA", jedno "OK - zatwierdzona" | 6-7 |
| W4 popraw ulozenie | 2 | plytka 2: gniazdo 4 "popraw ulozenie" | komunikat "Skan do powtorzenia" z powodem "popraw ulozenie pracy (gniazdo 4)"; gdy na plytce 1 zostaly prace bez decyzji, program nie przelacza mapy sam - nad lista plytek jest przycisk nowego wyniku | 8 |
| W4 ciag dalszy | 3 | plytka 2 jeszcze raz, same zielone | pytanie "Ponowny skan tej samej plytki?"; po "Tak, to ponowny skan" plytka 2 zielona, komunikat znika | 9 |
| W5 lista do dofrezowania | - | - | "Do dofrezowania: 1": kuweta 9003 albo 9011, zab, krazek K-1 | 10 |

Czwarta Spacja (zapas): plytka 3, trzy prace zielone. Piata i dalsze: nic nie przychodzi (wpis w oknie polecen).

## Rano - co podaje symulator

Program startuje w trybie "Poranek" i pyta "Kto teraz pracuje?". Ramki i Excela nie ma: program pokazuje
"Ramka poranna nie jest podlaczona" (od razu) i "Excel nie jest podlaczony" (po zamknieciu pieca) - to nie sa bledy proby.

| Zadanie | Spacja nr | Co podaje symulator | Co ma byc na ekranie po poprawnym wykonaniu | Krok sprawdzenia bez ekranu |
|---------|-----|--------------------------|--------------------------------------|---------|
| R1 zeskanuj 2 plytki pieca | 1 i 2 | plytka 4: 6 prac, gniazdo 5 zolte; plytka 5: 3 prace | dwie plytki; piec otwarty | 11-12 |
| R2 rozstrzygnij dwuznaczna | - | - | po kliknieciu gniazda 5 plytki 4: "Ktory to projekt?" i dwaj kandydaci (kuwety 3235 i 3256); po "To ten projekt" gniazdo zielone | 13-14 |
| R3 rozloz jedna kuwete | - | - | pierwsza biezaca "Kuweta 3221" (4 prace, plytki 4 i 5); po Enterze stan "rozlozona", biezaca "Kuweta 3228" | 15 |
| R4 cofnij pomylke | - | - | po Enterze i Backspace kuweta 3228 znowu biezaca | 16 |
| R5 znajdz kuwete po numerze | - | - | po wpisaniu 3242 i Enterze biezaca "Kuweta 3242" (plytka 5, gniazdo 4) | 17 |
| R6 zamknij piec i braki | - | - | po "Zamknij piec": kompletne 3221, 3228, 3235; "Braki w tym piecu: 2" - kuwety 3242 i 3249 | 18 |

Wybor drugiego kandydata w R2 (kuweta 3256) tez jest decyzja zapisana przez program, ale wtedy zlecenie 3235 nie bedzie
kompletne - zapisz to w arkuszu jako blad wykonania, nie jako blad programu.

Trzecia Spacja (zapas): plytka 6, dwie prace rozpoznane. Czwarta i dalsze: nic nie przychodzi.

## Co sprawdzono 20.11.2026 na PC, a czego nie

- Sprawdzone automatycznie, bez ekranu (`--sprawdz`): 18 z 18 krokow - skrypt sam naciska Spacje, klika gniazda i przyciski
  w oknie programu i czyta wynik z ekranu; obejmuje 11 z 11 zadan T14. Uruchomienie `wieczor` i `rano` bez ekranu z samym
  otwarciem i zamknieciem okna (`--zamknij-po 3`): kod 0.
- NIE sprawdzone: okno na prawdziwym ekranie (rozmiar, czytelnosc, mysz i klawiatura czlowieka), czas 8 s jako odczucie
  czekania, druk jednej strony na drukarce pracowni, przebieg z osoba badana. To jest wlasciwa proba T14 - wykonuje ja
  wlasciciel.
- Symulator nie jest programem skanera: w pracy skan uruchamia sie w programie skanera, a program tylko czeka na plik.
  Proba z prawdziwym skanerem to powtorka T14 na stanowisku (plan etapu 3, definicja pracy produkcyjnej).
