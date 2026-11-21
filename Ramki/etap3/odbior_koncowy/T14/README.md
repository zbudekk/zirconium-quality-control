# T14 - proba "technik obsluguje program bez instrukcji" (zadanie wlasciciela)

To jedyny test koncowy, ktorego nie moze wykonac program ani wykonawca - potrzebny jest czlowiek, ktory nie widzial
programu. Prowadzi wlasciciel. Ponizej: co dostajesz, jak przygotowac komputer i ile to trwa. Tresci zestawu nie
powtarzam - sa w plikach paczki E3-A11d (sciezki ponizej beda w `main` po scaleniu galezi `e3/a11d`).

## Kryterium (plan etapu 3, sekcja 7)

Osoba, ktora nie widziala programu, dostaje jedna strone z obrazkami i zadnych podpowiedzi; symulator podaje skany.
Wieczor 5 zadan, rano 6 zadan. Zaliczenie: **11 z 11 zadan wykonanych, 0 interwencji obserwatora**; miejsca zawahania
dluzszego niz 10 s spisane i poprawione albo swiadomie zostawione.

Decyzja koordynatora (20.11, do odwolania): w etapie 3 proba idzie na udawanym skanerze ("T14 na atrapie"); powtorka na
prawdziwym skanerze jest wymagana dopiero przed praca produkcyjna.

**Stan na 20.11 wieczor (E3-ODB etap 2):** paczka P14 (runda 2) zmienila nazwe przycisku nowego wyniku w oknie na
`przycisk_nowa_plytka` (potwierdzone w kodzie kopii integracyjnej a2236c1: `stanowisko/ui`); zestaw T14 zmienia runda 2
paczki A11d (w toku) - dlatego sciezki, liczba krokow kontroli ("18 z 18") i postac polecen ponizej zostaja
**do potwierdzenia po scaleniu `e3/a11d`** (dwa miejsca oznaczone w tekscie).

## Co dostajesz

| Plik (po scaleniu `e3/a11d`) | Do czego |
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
   zawiera **[DO POTWIERDZENIA PO SCALENIU - jesli A11d dolozy zestaw do paczki, ten krok odpada]**.
3. Otworz okno polecen w `C:\Stanowisko_t14` i sprawdz zestaw (bez ekranu, ok. 10 s wg A11d):

   ```
   C:\Stanowisko\Polecenie.cmd C:\Stanowisko_t14\symulator_t14.py --program . --sprawdz
   ```

   Ostatni wiersz ma brzmiec: `SPRAWDZENIE T14 BEZ EKRANU: zgodne 18 z 18 krokow`. Inny wynik = nie zaczynaj proby, zglos
   koordynatorowi. (`Polecenie.cmd` uruchamia Pythona zainstalowanej wersji w katalogu programu, dlatego `--program .`;
   dokladna postac polecenia `PY` podaje `scenariusz_symulatora.md` **[DO POTWIERDZENIA PO SCALENIU]**.)
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
