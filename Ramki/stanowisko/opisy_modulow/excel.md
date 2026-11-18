# excel - wybor wiersza arkusza zlecen, log, tryby "pytaj" i "cien" (E3-A9, 18.11.2026)

Pliki: `stanowisko/excel.py` (reguly, log, zapis przez interfejs arkusza - tylko biblioteka standardowa),
`stanowisko/excel_com.py` (COM do otwartego Excela, pywin32 - NAPISANA, w E3-A9 NIEURUCHAMIANA na prawdziwym Excelu),
`narzedzia/arkusz_syntetyczny.py` (arkusz 30 tys. wierszy o fikcyjnych nazwach + 200 zapytan o znanej odpowiedzi, atrapa
arkusza `ArkuszWPamieci`), `testy/test_excel.py`. Podpiecie do programu (okno "Excel: wskaz wiersz", przyciski) robi A12.

**Co robi.** Po "Zamknij piec" (`SesjaRano.zamknij_piec` / `wynik_pieca`) bierze zlecenia kompletne (`kompletne`), dla
kazdego czyta z tabeli `zlecenia` nazwe folderu i kuwete (DW2), wybiera wiersz arkusza wedlug regul 1-5 planu wdrozenia
("Dane i integracje", "Reguly znalezienia wiersza") i proponuje: **jeden wiersz** (do zatwierdzenia), **juz odhaczone**
(pole B zielone - tylko log) albo **wskaz wiersz** (lista kandydatow). Po zatwierdzeniu przez czlowieka zmienia wylacznie
kolor wypelnienia pola B jednego wiersza (RGB 198, 239, 206) i zapisuje wpis w `log_excel.csv` (regula 6) oraz w tabeli
`excel_zapisy`. Poprawki z "Zamknij piec" (zab do zlecenia juz odhaczonego, SE5) - tylko wpis w logu.

## Zalozenia o arkuszu - DO POTWIERDZENIA na kopii pliku produkcyjnego (plan etapu 3: D2, X8)

Jedno miejsce w kodzie: `excel.ZALOZENIA_ARKUSZA` + klucze `[excel]` w `ustawienia.toml`.

| Co | Zalozenie | Gdzie zmienic |
|---|---|---|
| Kolumny | odczyt A-I biezacego arkusza; A = data zlecenia, B = numer zlecenia i pole odhaczenia (kolor), C = kuweta, H = nazwa jak folder; D-G, I nieuzywane | `kolumna_daty`, `kolumna_odhaczenia`, `kolumna_kuwety`, `kolumna_nazwy` |
| Wiersze | wiersz 1 = naglowek, dane od 2 do ostatniego uzytego (`UsedRange`); puste wiersze pomijane | `pierwszy_wiersz` |
| Plik i arkusz | Excel juz otwarty z Autozapisem; skoroszyt i arkusz aktywny albo wskazany nazwa | `skoroszyt`, `arkusz` |
| Data w A | komorka daty (COM: `datetime`), tekst `dd.mm.rrrr` / `rrrr-mm-dd` / `dd.mm.rr` / `dd/mm/rrrr`, numer seryjny (1980-2099) | `excel.data_z_komorki` |
| Kuweta w C | rowna dokladnie po normalizacji: liczba albo tekst, zera wiodace i spacje bez znaczenia; `13263`, `3263/2`, `3263a` to nie 3263 | `excel.norm_kuweta` |
| Nazwa w H | porownanie po `nazwy.znormalizuj` (male litery, pojedyncze spacje, liczby bez zer, NFC, "1784PG" = "1784 pg") | `nazwy.znormalizuj` |
| Nazwisko z folderu | slowa (min. 2 litery) przed numerem kuwety; folder zaczynajacy sie numerem - pierwsze slowo po nim, poza kodami `KODY_PRACY` | `excel.nazwisko_z_folderu` |
| "Zielone" | wypelnienie rowne `[excel] kolor_rgb`; biale = brak wypelnienia; INNY kolor = cudze oznaczenie: program go nie nadpisuje | `excel.BIALY`, `kolor_rgb` |
| Zlecenie prywatne `#1234` | numer w kolumnie B (numer zlecenia) albo `#1234` w H; jeden wiersz = propozycja (K12 - potwierdzic na 3 pierwszych zleceniach, D5) | `excel.dopasuj` |

## Reguly (tak, jak dzialaja w kodzie)

1. Kandydaci: wiersze, w ktorych C po normalizacji rowna sie kuwecie (dokladnie).
2. H po normalizacji rowna sie nazwie folderu: jeden taki wiersz = on. **Kilka takich wierszy** (reklamacja z nowym
   wierszem): najnowszy po dacie, gdy jest jedynym nieodhaczonym; gdy wszystkie zielone - "juz odhaczone" (najnowszy);
   gdy nieodhaczonych jest wiecej albo najnowszy nie jest jedyny - "wskaz wiersz". [INTERPRETACJA - plan mowi tylko,
   ze reklamacja "lapie sie regulami 1-3"]
3. H nie pasuje nigdzie: wiersz z najnowsza data w A sposrod WSZYSTKICH kandydatow; przyjety, jesli nazwisko z folderu
   wystepuje w jego H (wszystkie slowa nazwiska jako slowa H) albo H jest puste. Najnowszy wiersz innej osoby = "wskaz
   wiersz" (nie szukamy glebiej - bezpieczniej). Dwa wiersze z ta sama najnowsza data albo wiersz bez daty PONIZEJ
   najnowszego = "wskaz wiersz". **H z samymi inicjalami** ("T.J. 3263") nie zawiera nazwiska = "wskaz wiersz"
   [INTERPRETACJA: dopisek "(inicjaly zamiast nazwiska)" w regule 3 kloci sie z jej warunkiem; przyjety warunek doslownie];
   H z inicjalem imienia i nazwiskiem ("Testowski J. 3263") - przyjety.
4. Wybrany wiersz ma zielone B = nic nie zapisuje, tylko log `juz_odhaczone` (regula 4). Inny kolor B = "wskaz wiersz".
5. Po regulach 1-3 wiecej niz jeden wiersz albo zaden = "Excel: wskaz wiersz" z lista kandydatow; zapis dopiero po wyborze.
   Takze: brak numeru kuwety w nazwie folderu, kuweta niejednoznaczna (`?46,3263` - kandydaci obu numerow).

`Dopasowanie`: `klasa`, `wiersz` (None dla "wskaz"), `regula` (2, 3 = wybor; 4 = juz odhaczone; 5 = wskaz), `kandydaci`
(najpierw wiersze z nazwa jak folder, potem od najnowszej daty), `powod` (tekst do okna, bez nazwisk), `data` (data wybranego
wiersza - okno moze ostrzec o starym wierszu).

## Tryby (DW10: w etapie 3 bez zapisu samodzielnego)

- **"pytaj" (domyslny)**: `propozycje` niczego nie zapisuja; kolor zmienia dopiero `zatwierdz` wywolane po decyzji czlowieka.
- **"cien"**: `zatwierdz` i `zapisz_cien` nie zmieniaja arkusza - tylko log porownawczy (`tylko_log`, tryb `cien`).
- `[excel] tryb_pytaj_przed_zapisem = false` NIE wlacza zapisu samodzielnego (tryb zostaje "pytaj", `Excel.ostrzezenia`).
  Trybu "auto" nie ma (etap 4, po audycie 50 z 50).

## Log (regula 6) i `excel_zapisy`

`log_excel.csv` (`[sciezki] log_excel`, domyslnie `dane/log_excel.csv`; UTF-8 z BOM, srednik - otwiera sie w Excelu):
`data;godzina;kuweta;folder;numer_zlecenia_b;arkusz;wiersz;kto_zatwierdzil` (regula 6, w tej kolejnosci) + `regula;wynik;tryb`.
Kazdy wpis idzie tez do `excel_zapisy` (gdy jest baza): `czas`, `sesja_pieca_id`, `zlecenie_id`, `kuweta`, `folder`,
`numer_zlecenia_b`, `arkusz`, `wiersz`, `regula`, `wynik` (`zapisano` / `juz_odhaczone` / `wskazano_recznie` / `pominieto` /
`tylko_log` / `blad`), `tryb`, `operator`. Schemat bazy bez zmian. DANE OSOBOWE: nazwa folderu tylko w logu CSV (wymaga jej
regula 6) i w `excel_zapisy.folder` (DW2); wartosc H trzyma tylko pamiec (okno wyboru wiersza).

## Bezpieczenstwo zapisu (kryterium "0 zapisow w zlym wierszu")

Przed zapisem: osoba zatwierdzajaca podana; pozycja niezalatwiona (jeden zapis na pozycje); wiersz wskazany recznie
z listy kandydatow; wiersz przeczytany ponownie i rowny migawce z chwili propozycji (wspoledycja: wstawiony albo zmieniony
wiersz = odmowa, wpis `blad`, nic nie zapisane - odswiez i zaproponuj od nowa); pole B: zielone = `juz_odhaczone`, inny kolor
= odmowa; plik logu da sie dopisac. Po zapisie: kolor odczytany ponownie. Zapis = `ustaw_wypelnienie` jednej komorki B.

## API dla A12 (spiecie poranka)

```python
from stanowisko import excel as EX
ex = EX.Excel.z_ustawien(ust, baza=sesja.baza)   # COM leniwie: polaczenie przy pierwszym odczycie; BladExcela = ostrzezenie, program dziala dalej
wynik = sesja_rano.zamknij_piec(operator)         # albo sesja_rano.wynik_pieca(id) po restarcie
ex.odswiez()                                      # swiezy odczyt A-I (inaczej co [excel] odswiez_co_min minut, samo)
pozycje = ex.propozycje(wynik)                    # Pozycja: dopasowanie.klasa / wiersz / kandydaci / powod; kandydaci_do_okna (H tylko na ekran)
ex.zatwierdz(poz, operator)                       # jeden_wiersz: kolor B + log ("pytaj") albo tylko log ("cien"); juz_odhaczone: tylko log
ex.zatwierdz(poz, operator, wiersz=nr)            # "Excel: wskaz wiersz": nr z poz.dopasowanie.kandydaci -> wskazano_recznie
ex.pomin(poz, operator)                           # czlowiek nie wskazal (albo zaznaczyl recznie w Excelu) -> pominieto
ex.zaloguj_poprawki(wynik, operator)              # SE5: poprawki tylko do logu
ex.zapisz_cien(pozycje, operator)                 # tylko tryb "cien": log porownawczy calego pieca bez pytan
```

Wymagania dla A12: (1) w trybie "pytaj" `zatwierdz` tylko po kliknieciu czlowieka (modul nie zna okna); `juz_odhaczone`
mozna zatwierdzic bez pytania (nic nie zapisuje); (2) `operator` = osoba wybrana na zmianie (`[sesja] operatorzy`); (3) kazdy
`BladExcela` pokazac jako komunikat i pracowac dalej (brak Excela, arkusz zmieniony - wtedy `odswiez` i `propozycje`
ponownie); (4) `ex.tryb` i `ex.ostrzezenia` widoczne w oknie; (5) `kandydaci_do_okna[i]["nazwa"]` (H) tylko na ekranie.

## Warstwa COM (`excel_com.py`) - stan: napisana, nieuruchamiana

`polacz(skoroszyt="", arkusz="", aplikacja=None) -> ArkuszCom` (interfejs `ZrodloArkusza`: `odczytaj`, `wiersz`,
`wypelnienie`, `ustaw_wypelnienie`). Tylko `GetActiveObject("Excel.Application")` - nigdy `Workbooks.Open`, `Add`, `Save`,
`SaveAs`, `SaveCopyAs`, `Close`, `Quit` (X1). Odczyt `Range.Value` calego zakresu jednym wywolaniem; kolor
`Interior.ColorIndex` (-4142 = brak) i `Interior.Color` (R + 256 G + 65536 B); zapis `Interior.Color` jednej komorki,
3 proby co 0,5 s (Excel odrzuca wywolania przy edycji komorki). pywin32 importowany dopiero w `polacz` (modul laduje sie
bez Excela). Sprawdzone tylko na atrapie obiektow COM (`test_excel_com_*`). **Do sprawdzenia w D2** (komputer z Excelem,
sesja interaktywna): czas `Range.Value` dla 30 tys. x 9, typy dat z pywintypes, `UsedRange` przy formatowaniu ponizej
danych, plik z SharePointa z Autozapisem i wspoledycja, nazwa skoroszytu i arkusza, `pywin32` w `requirements.txt` laptopa.

## Ustawienia `[excel]`

Wymagane (sprzed etapu 3, bez zmian): `kolumna_kuwety`, `kolumna_nazwy`, `kolumna_odhaczenia`, `kolor_rgb`,
`tryb_pytaj_przed_zapisem`. Opcjonalne (E3-A9; stary plik wczytuje sie bez zmian): `kolumna_daty` ("A"), `pierwszy_wiersz` (2),
`skoroszyt` (""), `arkusz` (""), `tryb` ("pytaj" / "cien"), `odswiez_co_min` (5.0). Walidacja: litery kolumn A-ZZZ, cztery
kolumny rozne, `pierwszy_wiersz >= 1`, `odswiez_co_min > 0`, `tryb` z listy. `[sciezki] log_excel` - plik logu.

## Kryteria i wyniki (testy/test_excel.py, PC)

Arkusz sztuczny 30 000 wierszy A-I (fikcyjne nazwy), 200 zapytan z 27 pulapek (120 jeden wiersz / 21 juz odhaczone /
59 wskaz wiersz): (1) klasa wlasciwa 200 z 200, zapisow w zlym wierszu 0 (154 zapisy w trybie "pytaj"); (2) wyszukanie
- liczby w raporcie E3-A9; (3) log CSV - pola reguly 6; (4) domyslnie "pytaj", "cien": 0 zmian arkusza przy 200 zatwierdzeniach;
(5) zapis zmienia tylko kolor jednej komorki (porownanie wszystkich wartosci i wypelnien przed i po).
Plus: 27 przypadkow regul na malym arkuszu, odmowa po wstawieniu wiersza (wspoledycja), `excel_zapisy` z wyniku pieca,
warstwa COM na atrapie, klucze ustawien.

## Pytania do wlasciciela (decyzje robocze - kazda w jednym miejscu kodu)

1. Kilka wierszy z ta sama nazwa (reklamacja): najnowszy tylko, gdy jest jedynym nieodhaczonym (regula 2/3 wyzej).
2. H z samymi inicjalami = "wskaz wiersz" (warunek reguly 3 doslownie), H z inicjalem imienia + nazwisko = wybor.
3. Pole B w innym kolorze niz zielony: program go nie nadpisuje (cudze oznaczenie?) - czy sa inne kolory w arkuszu?
4. Wiek wiersza: reguly nie ograniczaja daty - zlecenie, ktorego jeszcze nie ma w arkuszu, moze trafic na stary wiersz
   tej kuwety z pustym H (regula 3). Czy ograniczyc wybor do wierszy z ostatnich N dni (np. 60)? Dzis: `Dopasowanie.data`
   do pokazania w oknie.
5. Zlecenia prywatne: numer w B albo `#1234` w H (K12) - potwierdzic na 3 pierwszych zleceniach (D5).

## Granice

- Bez zmian w `aplikacja.py`, `ui/**`, `session*.py`, `baza.py` (schemat bez zmian).
- Modul nie sprawdza, czy `operator` jest na liscie `[sesja] operatorzy` - robi to okno (A12) / session.
- Kandydaci przy kuwecie niejednoznacznej: wiersze obu numerow, bez zawezenia po H.
- Brak "cofnij zapis": pomylke po zapisie poprawia czlowiek w Excelu (log zostaje).
