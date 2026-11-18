# excel - wybor wiersza arkusza zlecen, log, tryby "pytaj" i "cien" (E3-A9, 18.11.2026; runda 2 po recenzji PR #27)

Pliki: `stanowisko/excel.py` (reguly, log, zapis przez interfejs arkusza - tylko biblioteka standardowa),
`stanowisko/excel_com.py` (COM do otwartego Excela, pywin32 - NAPISANA, w E3-A9 NIEURUCHAMIANA na prawdziwym Excelu),
`narzedzia/arkusz_syntetyczny.py` (arkusz 30 tys. wierszy o fikcyjnych nazwach + 200 zapytan o znanej odpowiedzi, atrapa
arkusza `ArkuszWPamieci`), `testy/test_excel.py`. Podpiecie do programu (okno "Excel: wskaz wiersz", przyciski) robi A12.

**Co robi.** Po "Zamknij piec" (`SesjaRano.zamknij_piec` / `wynik_pieca`) bierze zlecenia kompletne (`kompletne`), dla
kazdego czyta z tabeli `zlecenia` nazwe folderu i kuwete (DW2), wybiera wiersz arkusza wedlug regul 1-5 planu wdrozenia
("Dane i integracje", "Reguly znalezienia wiersza") z dwoma bezpiecznikami i proponuje: **jeden wiersz** (do zatwierdzenia),
**juz odhaczone** (pole B zielone - tylko log) albo **wskaz wiersz** (lista kandydatow). Po zatwierdzeniu przez czlowieka
zmienia wylacznie kolor wypelnienia pola B jednego wiersza (RGB 198, 239, 206) i zapisuje wpis w `log_excel.csv` (regula 6)
oraz w tabeli `excel_zapisy`. Poprawki z "Zamknij piec" (zab do zlecenia juz odhaczonego, SE5) - tylko wpis w logu.

## Zalozenia o arkuszu - DO POTWIERDZENIA na kopii pliku produkcyjnego (plan etapu 3: D2, X8)

Jedno miejsce w kodzie: `excel.ZALOZENIA_ARKUSZA` + klucze `[excel]` w `ustawienia.toml`.

| Co | Zalozenie | Gdzie zmienic |
|---|---|---|
| Kolumny | odczyt A-I biezacego arkusza; A = data zlecenia, B = numer zlecenia i pole odhaczenia (kolor), C = kuweta, H = nazwa jak folder; D-G, I nieuzywane | `kolumna_daty`, `kolumna_odhaczenia`, `kolumna_kuwety`, `kolumna_nazwy` |
| Wiersze | wiersz 1 = naglowek, dane od 2 do ostatniego uzytego (`UsedRange`); puste wiersze pomijane | `pierwszy_wiersz` |
| Plik i arkusz | Excel juz otwarty z Autozapisem; skoroszyt i arkusz wskazane nazwa, a gdy puste - aktywne (ostrzezenie z nazwami uzytymi) | `skoroszyt`, `arkusz` |
| Data w A | komorka daty (COM: `datetime`), tekst `dd.mm.rrrr` / `rrrr-mm-dd` / `dd.mm.rr` / `dd/mm/rrrr`, numer seryjny (1980-2099); data pozniejsza niz jutro = brak daty | `excel.data_z_komorki` |
| Kuweta w C | rowna dokladnie po normalizacji: liczba albo tekst, zera wiodace i spacje bez znaczenia; `13263`, `3263/2`, `3263a` to nie 3263 | `excel.norm_kuweta` |
| Nazwa w H | porownanie po `nazwy.znormalizuj` (male litery, pojedyncze spacje, liczby bez zer, NFC, "1784PG" = "1784 pg") | `nazwy.znormalizuj` |
| Nazwisko z folderu | slowa (min. 2 litery) przed numerem kuwety; folder zaczynajacy sie numerem - pierwsze slowo po nim, poza kodami `KODY_PRACY` | `excel.nazwisko_z_folderu` |
| "Zielone" | wypelnienie rowne `[excel] kolor_rgb`; biale = brak wypelnienia; INNY kolor = cudze oznaczenie: program go nie nadpisuje | `excel.BIALY`, `kolor_rgb` |
| Zlecenie prywatne `#1234` | numer w kolumnie B tylko w wierszu bez kuwety w C (wiersz zlecenia prywatnego) albo `#1234` w H; jeden taki wiersz w limicie wieku = propozycja (K12 - potwierdzic na 3 pierwszych zleceniach, D5) | `excel.dopasuj`, `IndeksArkusza` |
| Limit wieku | wybrany wiersz starszy niz 60 dni albo bez daty = "wskaz wiersz" (0 = bez limitu); liczba do potwierdzenia na kopii pliku | `maks_wiek_dni` |

## Reguly (tak, jak dzialaja w kodzie)

1. Kandydaci: wiersze, w ktorych C po normalizacji rowna sie kuwecie (dokladnie).
2. H po normalizacji rowna sie nazwie folderu: jeden taki wiersz = on. **Kilka takich wierszy** (reklamacja z nowym
   wierszem): najnowszy po dacie, gdy jest jedynym nieodhaczonym; gdy wszystkie zielone - "juz odhaczone" (najnowszy);
   gdy nieodhaczonych jest wiecej albo najnowszy nie jest jedyny - "wskaz wiersz" (decyzja 18.11.2026, pytanie 1).
3. H nie pasuje nigdzie: wiersz z najnowsza data w A sposrod WSZYSTKICH kandydatow; przyjety, jesli nazwisko z folderu
   wystepuje w jego H (wszystkie slowa nazwiska jako slowa H) albo H jest puste. Najnowszy wiersz innej osoby = "wskaz
   wiersz". Dwa wiersze z ta sama najnowsza data albo wiersz bez daty PONIZEJ najnowszego = "wskaz wiersz". **H z samymi
   inicjalami** ("T.J. 3263") nie zawiera nazwiska = "wskaz wiersz" (decyzja 18.11.2026, pytanie 2); H z inicjalem imienia
   i nazwiskiem ("Testowski J. 3263") - przyjety.
4. Wybrany wiersz ma zielone B = nic nie zapisuje, tylko log `juz_odhaczone` (regula 4). Inny kolor B = "wskaz wiersz"
   (decyzja 18.11.2026, pytanie 3: program go nie nadpisuje).
5. Po regulach 1-3 wiecej niz jeden wiersz albo zaden = "Excel: wskaz wiersz" z lista kandydatow; zapis dopiero po wyborze.
   Takze: brak numeru kuwety w nazwie folderu, kuweta niejednoznaczna (`?46,3263` - kandydaci obu numerow).

**Bezpieczniki kazdego wyboru jednego wiersza (runda 2, P3; sprawdzane przed regula 4, wiec dotycza tez "juz odhaczone"):**
(a) wiek - `[excel] maks_wiek_dni` (60) > 0 i wybrany wiersz starszy albo bez daty = "wskaz wiersz" (zlecenie jeszcze
niewpisane do arkusza nie trafi na stary wiersz tej kuwety z pustym H); (b) nowszy nieodhaczony wiersz tej samej kuwety
(pozniejsza data albo ta sama / brak daty i wiersz nizej; pole B bez zieleni) = "wskaz wiersz" - takze reklamacja wpisana
w nowym wierszu inaczej niz folder (stary wiersz z H = folder + nowszy otwarty z innym H). (b) wykracza poza doslowna
regule 2 - decyzja robocza po recenzji (bezpieczniej). Ryzyko, ktorego reguly nie widza: zlecenie niewpisane, a najnowszy
wiersz kuwety z ostatnich 60 dni ma puste H - propozycja ma wtedy `do_sprawdzenia = True` (okno pokazuje date wiersza).

`Dopasowanie`: `klasa`, `wiersz` (None dla "wskaz"), `regula` (2, 3 = wybor; 4 = juz odhaczone; 5 = wskaz), `kandydaci`
(najpierw wiersze z nazwa jak folder, potem od najnowszej daty), `powod` (tekst do okna, bez nazwisk), `data` (data wybranego
wiersza), `do_sprawdzenia` (wybor bez zgodnej nazwy - regula 3 albo zlecenie prywatne: okno pokazuje, nie zatwierdza w ciszy,
takze "juz odhaczone").

## Tryby (DW10: w etapie 3 bez zapisu samodzielnego)

- **"pytaj" (domyslny)**: `propozycje` niczego nie zapisuja; kolor zmienia dopiero `zatwierdz` wywolane po decyzji czlowieka.
- **"cien"**: `zatwierdz` i `zapisz_cien` nie zmieniaja arkusza - tylko log porownawczy (`tylko_log`, tryb `cien`).
- `[excel] tryb_pytaj_przed_zapisem = false` NIE wlacza zapisu samodzielnego (tryb zostaje "pytaj", `Excel.ostrzezenia`).
  Trybu "auto" nie ma (etap 4, po audycie 50 z 50).

## Log (regula 6) i `excel_zapisy`

`log_excel.csv` (`[sciezki] log_excel`, domyslnie `dane/log_excel.csv`; poza `dane/` = ostrzezenie; UTF-8 z BOM, srednik):
`data;godzina;kuweta;folder;numer_zlecenia_b;arkusz;wiersz;kto_zatwierdzil` (regula 6, w tej kolejnosci) + `skoroszyt;regula;wynik;tryb`.
Kazdy wpis idzie tez do `excel_zapisy` (gdy jest baza): `czas`, `sesja_pieca_id`, `zlecenie_id`, `kuweta`, `folder`,
`numer_zlecenia_b`, `arkusz` (= "skoroszyt!arkusz" - bez zmiany schematu), `wiersz`, `regula`, `wynik` (`zapisano` /
`juz_odhaczone` / `wskazano_recznie` / `pominieto` / `tylko_log` / `blad`), `tryb`, `operator`. DANE OSOBOWE: nazwa folderu
tylko w logu CSV (wymaga jej regula 6) i w `excel_zapisy.folder` (DW2); wartosc H trzyma tylko pamiec (okno wyboru wiersza).
Blad dopisania CSV po zapisie koloru (plik otwarty w Excelu): wpis w `excel_zapisy` mimo to, `BladExcela` z komunikatem,
`Pozycja.stan = "zapisano bez logu CSV"`, pozycja zalatwiona (bez drugiego zapisu).

## Bezpieczenstwo zapisu (kryterium "0 zapisow w zlym wierszu")

Propozycja (`pozycja`, `propozycje`) i zatwierdzenie zawsze na SWIEZYM odczycie arkusza (P1; niezmienione wiersze z pamieci
poprzedniego odczytu - ponowny odczyt 30 tys. wierszy ok. 15 ms na atrapie). `zatwierdz`: osoba podana; pozycja niezalatwiona;
X4 - w trybie "pytaj" zapis tylko dla pozycji z zamknietego pieca (`sesja_pieca_id`, z baza sprawdzane w `sesje_pieca`);
wiersz wskazany recznie z listy kandydatow. Potem do `PONOWIENIA_ZAPISU` (3) prob CALEGO kroku (B1): swiezy odczyt; ten sam
skoroszyt (nazwa + pelna sciezka) i arkusz co przy propozycji (P2 - kopia arkusza, kopia pliku, "Zapisz jako" = odmowa);
wiersze N-1..N+1 rowne migawce; pole B (zielone = `juz_odhaczone`, inny kolor = odmowa); propozycja policzona od nowa rowna
pierwotnej (nowy wiersz kuwety, zmiana C / H innego wiersza = odmowa); plik logu da sie dopisac; kolor - jedno wywolanie COM;
odrzucone = przerwa 0,5 s i caly krok od nowa. Po zapisie: wiersze N-1..N+1 i kolor czytane ponownie; roznica = wpis `blad`
i komunikat "kolor zapisany, ale wiersz N zmienil sie w trakcie - sprawdz recznie wiersze N-1..N+1" (pozycja zalatwiona).
Kazda odmowa po odczycie arkusza = wpis `blad` w logu. Zapis = `ustaw_wypelnienie` jednej komorki B.

## API dla A12 (spiecie poranka)

```python
from stanowisko import excel as EX
ex = EX.Excel.z_ustawien(ust, baza=sesja.baza)   # COM leniwie: polaczenie przy pierwszym odczycie; BladExcela = ostrzezenie, program dziala dalej
wynik = sesja_rano.zamknij_piec(operator)         # albo sesja_rano.wynik_pieca(id) po restarcie
pozycje = ex.propozycje(wynik)                    # swiezy odczyt; Pozycja: dopasowanie.klasa / wiersz / kandydaci / powod / do_sprawdzenia
ex.zatwierdz(poz, operator)                       # jeden_wiersz: kolor B + log ("pytaj") albo tylko log ("cien")
ex.zatwierdz(poz, operator, wiersz=nr)            # "Excel: wskaz wiersz": nr z poz.dopasowanie.kandydaci -> wskazano_recznie
ex.zaloguj_juz_odhaczone(poz, operator)           # juz_odhaczone: tylko log, bez drogi zapisu
ex.pomin(poz, operator)                           # czlowiek nie wskazal (albo zaznaczyl recznie w Excelu) -> pominieto
ex.zaloguj_poprawki(wynik, operator)              # SE5: poprawki tylko do logu
ex.zapisz_cien(pozycje, operator)                 # tylko tryb "cien": log porownawczy calego pieca bez pytan
ex.rozlacz()                                      # zamkniecie programu i po bledzie COM: zwolnienie obiektow COM
```

Wynik `zatwierdz` / `pomin` / `zaloguj_*` / `zapisz_cien` (`POLA_WYNIKU`, P4): `id` (wiersz `excel_zapisy`), `kuweta`, `wiersz`,
`klasa`, `wynik`, `regula`, `tryb`, `zlecenie_id`, `sesja_pieca_id` - BEZ nazwy folderu i nazwisk (mozna go zapisac w dzienniku).

Wymagania dla A12: (1) w trybie "pytaj" `zatwierdz` tylko po kliknieciu czlowieka (modul nie zna okna); `zaloguj_juz_odhaczone`
mozna wolac bez pytania tylko przy `do_sprawdzenia = False`; (2) `operator` = osoba wybrana na zmianie (`[sesja] operatorzy`);
(3) kazdy `BladExcela` pokazac jako komunikat i pracowac dalej (brak Excela, arkusz zmieniony - wtedy `propozycje` ponownie;
po bledzie COM `rozlacz()`); (4) `ex.tryb` i `ex.ostrzezenia` widoczne w oknie (w tym skoroszyt / arkusz uzyte, gdy nie sa
w ustawieniach - przed pierwszym zatwierdzeniem); (5) `kandydaci_do_okna[i]["nazwa"]` (H) i `Pozycja.folder` tylko na ekranie,
nigdy w dzienniku i komunikatach; (6) wszystkie wywolania jednego obiektu `Excel` z jednego watku (obiekt COM nie przechodzi
miedzy watkami; inny watek wymaga `pythoncom.CoInitialize()` i wlasnego `Excel`); (7) odczyt przez COM i zawieszony Excel
moga blokowac watek na sekundy (brak limitu czasu wywolania COM; przerwa ponowienia do 2 x 0,5 s) - zmierzyc w D2, ewentualnie
watek roboczy wg (6); (8) `pozycja()` bez `sesja_pieca_id` to tylko podglad - zatwierdzenie w trybie "pytaj" odmowi (X4).

## Warstwa COM (`excel_com.py`) - stan: napisana, nieuruchamiana

`polacz(skoroszyt="", arkusz="", aplikacja=None) -> ArkuszCom` (interfejs `ZrodloArkusza`: `odczytaj`, `wiersz`,
`wypelnienie`, `ustaw_wypelnienie`, `nazwa`, `skoroszyt`, `sciezka` - nazwy czytane na zywo; `zwolnij()`). Tylko
`GetActiveObject("Excel.Application")` - nigdy `Workbooks.Open`, `Add`, `Save`, `SaveAs`, `SaveCopyAs`, `Close`, `Quit` (X1).
Odczyt `Range.Value` calego zakresu jednym wywolaniem; kolor `Interior.ColorIndex` (-4142 = brak) i `Interior.Color`
(R + 256 G + 65536 B); zapis `Interior.Color` jednej komorki - JEDNA proba (ponowienie = caly krok w `zatwierdz`, B1).
pywin32 importowany dopiero w `polacz`. Sprawdzone tylko na atrapie obiektow COM (`test_excel_com_*`, `test_b1_*`, `test_d2_*`).

**Lista kontrolna D2** (komputer z Excelem, sesja interaktywna, kopia pliku produkcyjnego): czas `Range.Value` dla
30 tys. x 9 i czas zatwierdzenia (pelny odczyt + kontrola); typy dat z pywintypes; `UsedRange` przy formatowaniu ponizej danych;
plik z SharePointa z Autozapisem i wspoledycja (zapis odrzucony przy edycji komorki - ponowienie calego kroku); nazwa
skoroszytu i arkusza do `ustawienia.toml`; unikalnosc numeru w B (kontrola sasiadow D6); kolor z formatowania warunkowego
(`Interior` != `DisplayFormat.Interior` - zielone z reguly nie bedzie widziane jako odhaczone); kilka instancji Excela
(`GetActiveObject` zwraca jedna); scalone komorki w B; zapis COM czysci stos "Cofnij" uzytkownika laptopa; zawieszony Excel
blokuje watek (brak limitu czasu); format pliku (.xls - paleta 56 kolorow, kolor odczytany inny niz zapisany = komunikat);
kolory pola B uzywane przez ludzi (pytanie 3); wiek wierszy zlecen w chwili "Zamknij piec" (`maks_wiek_dni`); jak czesto H ma
same inicjaly (pytanie 2); `pywin32` w `requirements.txt` laptopa; po zamknieciu Excela czy EXCEL.EXE nie zostaje w tle.

## Ustawienia `[excel]`

Wymagane (sprzed etapu 3, bez zmian): `kolumna_kuwety`, `kolumna_nazwy`, `kolumna_odhaczenia`, `kolor_rgb`,
`tryb_pytaj_przed_zapisem`. Opcjonalne (E3-A9; stary plik wczytuje sie bez zmian): `kolumna_daty` ("A"), `pierwszy_wiersz` (2),
`skoroszyt` (""), `arkusz` (""), `tryb` ("pytaj" / "cien"), `odswiez_co_min` (5.0 - odczyt dla `dopasuj`; propozycja
i zatwierdzenie czytaja zawsze), `maks_wiek_dni` (60; 0 = bez limitu). Walidacja: litery kolumn A-XFD, cztery kolumny rozne
(zglaszany pierwszy powtorzony klucz), `pierwszy_wiersz >= 1`, `odswiez_co_min > 0`, `maks_wiek_dni >= 0`, `tryb` z listy.

## Kryteria i wyniki (testy/test_excel.py, PC) - liczby: raport `raporty/E3-A9_2026-11-18.md`

Arkusz sztuczny 30 000 wierszy A-I (fikcyjne nazwy), 200 zapytan z 31 pulapek (110 jeden wiersz / 19 juz odhaczone /
71 wskaz wiersz), w tym przypadki P1 (wiersz zlecenia dopisany po odczycie) i P3 (zlecenie niewpisane - stary wiersz z pustym H,
reklamacja z innym H, "#1234" = B zwyklego zlecenia). Pelny przebieg "pytaj": zapisy z wyboru programu i zapisy wierszy
wskazanych przez test (czlowiek w oknie "wskaz wiersz") liczone osobno. Plus: 39 przypadkow regul na malym arkuszu, B1 na
atrapie COM (odrzucony zapis + wstawiony wiersz, wiersz zmieniony po zapisie), P2 (kopia arkusza / pliku, "Zapisz jako"),
P5 (zajety plik logu), X4, D1, D2, D5, D8, D9, D10.

## Granice

- Bez zmian w `aplikacja.py`, `ui/**`, `session*.py`, `baza.py` (schemat bez zmian).
- Modul nie sprawdza, czy `operator` jest na liscie `[sesja] operatorzy` - robi to okno (A12) / session.
- Kandydaci przy kuwecie niejednoznacznej: wiersze obu numerow, bez zawezenia po H.
- Brak "cofnij zapis": pomylke po zapisie poprawia czlowiek w Excelu (log zostaje).
- Zlecenie niewpisane do arkusza + najnowszy wiersz kuwety z ostatnich `maks_wiek_dni` z pustym H = propozycja tego wiersza
  (`do_sprawdzenia`) - reguly tego nie odroznia; chroni tylko czlowiek w trybie "pytaj".
