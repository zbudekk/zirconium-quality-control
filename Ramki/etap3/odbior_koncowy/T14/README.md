# T14 - proba "technik obsluguje program bez instrukcji" (zadanie wlasciciela)

To jedyny test koncowy, ktorego nie moze wykonac program ani wykonawca - potrzebny jest czlowiek, ktory nie widzial
programu. Prowadzi wlasciciel. Ponizej: co dostajesz, jak przygotowac komputer i ile to trwa. Tresci zestawu nie
powtarzam - sa w plikach paczki E3-A11d (od 21.11 w `main` bcd0678: katalog `Ramki/etap3/t14/`, 9 plikow + `obrazki/`).

## Kryterium (plan etapu 3, sekcja 7)

Osoba, ktora nie widziala programu, dostaje jedna strone z obrazkami i zadnych podpowiedzi; symulator podaje skany.
Wieczor 5 zadan, rano 6 zadan. Zaliczenie: **11 z 11 zadan wykonanych, 0 interwencji obserwatora**; miejsca zawahania
dluzszego niz 10 s spisane i poprawione albo swiadomie zostawione.

Decyzja koordynatora (20.11, do odwolania): w etapie 3 proba idzie na udawanym skanerze ("T14 na atrapie"); powtorka na
prawdziwym skanerze jest wymagana dopiero przed praca produkcyjna.

**Stan na 21.11 (runda 1 recenzji PR #44):** paczka A11d jest scalona; sciezki ponizej sprawdzone w `main` bcd0678
(wszystkie pliki z tabeli istnieja), kontrola zestawu ma **22 kroki** ("zgodne 22 z 22 krokow" - `symulator_t14.py`,
`scenariusz_symulatora.md`), a polecenie kontroli z kroku 3 bylo wykonane w probie generalnej 21.11 na instalacji z
paczki (wersja 0.3.1, commit f5c3e01): kod 0, 8,3 s, "zgodne 22 z 22 krokow". Miejsc "do potwierdzenia" juz nie ma.

## Co dostajesz

| Plik (w `main`) | Do czego |
|---|---|
| `Ramki/etap3/t14/README.md` | pelny opis proby: przygotowanie, przebieg, czego nie mowic, co zrobic z wynikiem - **zacznij od tego pliku** |
| `Ramki/etap3/t14/jedna_strona.html` | jedyna pomoc dla osoby badanej - do wydruku (1 strona A4 poziomo, kolor) |
| `Ramki/etap3/t14/arkusz_obserwacji.html` | arkusz dla Ciebie - do wydruku (1 strona A4 pionowo); polecenia W1-W5 i R1-R6 |
| `Ramki/etap3/t14/scenariusz_symulatora.md` | co podaje udawany skaner i co ma byc na ekranie |
| `Ramki/etap3/t14/symulator_t14.py`, `scenariusz_t14.json` | program z udawanym skanerem i dane proby (wylacznie sztuczne) |
| `Ramki/stanowisko/instrukcje/wieczor.html`, `poranek.html`, `co_robic_gdy_nie_dziala.html` | instrukcje jednostronicowe - osoba badana NIE dostaje ich przed proba |

## Przygotowanie komputera z paczki wydania (ok. 15 minut, raz)

Komputer: ekran 1920 x 1080, mysz, klawiatura; Python 3.12 zainstalowany. Moze byc PC albo laptop stanowiska.

1. Rozpakuj paczke `Stanowisko_<numer>.zip` (np. do `C:\Stanowisko_paczka`) i uruchom `zainstaluj.cmd` wg instrukcji
   `instalacja_i_aktualizacja.md` (jest w paczce, w `program\instrukcje\`). Pierwsze uruchomienie konczy sie napisem
   "wstrzymana - uzupelnij ustawienia": wpisz foldery w `C:\Stanowisko\ustawienia.toml` i uruchom `zainstaluj.cmd`
   jeszcze raz. Na koncu samokontrola ma byc zielona.
2. Skopiuj katalog `Ramki\etap3\t14` z repozytorium na ten komputer (np. `C:\Stanowisko_t14`). Paczka wydania go nie
   zawiera (potwierdzone na paczce 0.3.1 z f5c3e01: w paczce sa tylko `stanowisko`, `modele_plytek`, `narzedzia`,
   `ramka`, `instrukcje`, `instalacja` - zestaw T14 bierze sie z repo, krok zostaje).
3. Otworz okno polecen i sprawdz zestaw (bez ekranu, ok. 10 s):

   ```
   set QT_QPA_PLATFORM=offscreen
   C:\Stanowisko\Polecenie.cmd C:\Stanowisko_t14\symulator_t14.py --sprawdz --program .
   set QT_QPA_PLATFORM=
   ```

   Ostatni wiersz ma brzmiec: `SPRAWDZENIE T14 BEZ EKRANU: zgodne 22 z 22 krokow`. Inny wynik = nie zaczynaj proby, zglos
   koordynatorowi. (`Polecenie.cmd` uruchamia Pythona zainstalowanej wersji w katalogu programu, dlatego `--program .`;
   pierwsza i trzecia linia wlaczaja i wylaczaja tryb bez ekranu tylko na czas kontroli - przed proba z osoba zmienna
   `QT_QPA_PLATFORM` ma byc pusta, inaczej okno sie nie pokaze. `scenariusz_symulatora.md` podaje to samo polecenie w
   postaci `PY symulator_t14.py --sprawdz` dla uruchomienia z repo.)
4. Wydrukuj `jedna_strona.html` i `arkusz_obserwacji.html` (przegladarka, A4, skala 100 %, z grafika tla).

## Proba (ok. 30-40 minut z osoba badana)

```
C:\Stanowisko\Polecenie.cmd C:\Stanowisko_t14\symulator_t14.py --program . wieczor --dziennik C:\Stanowisko_t14\t14_wieczor.log
C:\Stanowisko\Polecenie.cmd C:\Stanowisko_t14\symulator_t14.py --program . rano --dziennik C:\Stanowisko_t14\t14_rano.log
```

Przebieg, zdania do powiedzenia osobie i lista "czego nie mowic" sa w `Ramki/etap3/t14/README.md` - trzymaj sie ich
doslownie. Skan uruchamia klawisz Spacja; skanera nie trzeba.

## Ile to trwa

| Krok | Czas |
|---|---|
| Instalacja z paczki i sprawdzenie zestawu | ok. 15 min (raz) |
| Wydruk 2 stron, stoper, dlugopis | ok. 5 min |
| Proba z osoba: wieczor 5 zadan + rano 6 zadan | ok. 30-40 min |
| Spisanie wyniku | ok. 10 min |
| **Razem** | **ok. 1 godziny** |

## Co oddac po probie (dowody T14 - do tego katalogu)

- `arkusz_obserwacji` wypelniony - skan albo zdjecie, **bez nazwiska osoby (same inicjaly)**;
- `t14_wieczor.log`, `t14_rano.log` (dzienniki symulatora - dane wylacznie sztuczne);
- trzy liczby do `RAPORT.md`: ile zadan z 11, ile interwencji, lista zawahan dluzszych niz 10 s z decyzja
  "poprawic" albo "zostawic (dlaczego)".

Wynik inny niz 11 z 11 i 0 interwencji = T14 niezaliczony: poprawki napisow / ekranu / jednej strony przez wlasciwa
paczke, potem powtorka z INNA osoba.
