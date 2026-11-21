# T10 - liczby kryterium policzone z plikow wyniku (t10_licz.py)

Zrodlo: rekordy skanow pliku wyniku narzedzia + pliki prawdy zestawow (mianowniki); sekcja `zbiorczo` i log tylko do porownania.

| Czesc kryterium | Policzone z rekordow / prawdy | `zbiorczo` narzedzia | Log | R59 pkt 6.2 | E3-A5 r4 | Ocena |
|---|---|---|---|---|---|---|
| wyrownanie (max blad < 0,05 mm) | 40 z 40 (rekordow 40, uklad niezgodny 0, max 0.0143 mm) | 40 z 40 | wierszy skanow 40 | 40 z 40 | 40 z 40 | spelnione |
| top-1 scenariusz "dobrze" | 276 z 276 (bledne 0) | prac 276, bledne 0 | - | 276 z 276 | 276 z 276 | spelnione |
| falszywe czerwone na pracach calych | wpisy (jak narzedzie): 0 z 127; prace z prawdy (kazda raz): 0 z 126 | 0 z 127 | 0 z 127 | 0 z 127 | 0 z 132 | spelnione |

Moje liczby zgodne z `zbiorczo` narzedzia i z wierszem logu "PRACE CA...": TAK.

Liczenie szersze (informacja): prac bez ubytkow w prawdzie 150 (kazdy scenariusz, kazdy top-1), z gniazdem czerwonym / statusem "ubytek": 0.

Falszywe czerwone na pracach calych (definicja R59): 0

Liczenie szersze - czerwone na pracach bez ubytkow w prawdzie: 0

Bledny top-1 w scenariuszu "dobrze": 0

Gniazda z wiecej niz jednym wpisem w wyniku (kilka fragmentow w gniezdzie): 14, wg scenariusza pracy: dobrze 0, bokiem 13, czesciowo 0, drgniecie 1.

Prace w prawdzie wg scenariusza (prac / top-1 trafny / brak gniazda w wyniku): dobrze 276 / 276 / 0; bokiem 44 / 26 / 0; czesciowo 37 / 35 / 0; drgniecie 40 / 38 / 0; razem 397.

Czas na skan (pole `czas_s.razem`, 40 skanow): min 12.51 s, mediana 23.16 s, max 51.32 s; suma 983.9 s; mediany etapow: plate 2.83 s, match 19.11 s, inspect 1.67 s; czas calosci wg narzedzia 996.2 s. Mierzone pod obciazeniem (patrz WYNIK.md).

Liczby poza kryterium T10 (informacja; odniesienie R59 pkt 6.1, kolumna "R59, zestawy dzisiejsze"):

| Miara | Ten przebieg | R59 pkt 6.1 |
|---|---|---|
| top-1 razem | 388 z 397 | 382 z 397 |
| wykrycie dowolna metoda, razem | 226 z 249 | 221 z 248 |
| metoda A / B / czerwone | 189 / 110 / 83 | 184 / 107 / 79 |
| prace cale z alarmem | 0 z 127 | 0 z 127 |
| falszywe ubytki (miejsca) / w tym czerwone | 7 / 2 | 7 / 2 |
| drgniecie wykryte / prac, falszywe "skan ponownie" | {'prac': 39, 'wykryte': 36, 'falszywe': 1} | 35 / 39, 2 (powtorka 1) |
| poprawki | {'prac': 14, 'wykryte': 5, 'falszywe': 0} | 5 / 14 |
| statusy gniazd | {'zielony': 116, 'czerwony': 66, 'zolty': 200, 'szary': 27, 'pomaranczowy': 4} | zolte 162 / szare 32 (powtorka 161 / 33) |
| projekty pominiete | 283 | 283 |
| prace cale "nie sprawdzono" | 9 (powody: {"dane": 9}) | - |

Log: wierszy 437, wierszy skanow 40, "Traceback" 0, "NIE PASUJE" 0.
