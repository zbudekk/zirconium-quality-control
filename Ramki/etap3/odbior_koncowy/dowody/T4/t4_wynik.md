# T4 - Pula: tabela liczb kryterium (odbior 21.11.2026, paczka 0.3.1, commit 571e186)

Narzedzie: <K>\Polecenie.cmd narzedzia\metryki_pula.py (czas x 2, jakosc x 1), --procesy 1, tor 2, jedna proba.
Dane: <PC-katalog>\e3\a5\pomiary\pula400 (400 wpisow, 373 pliki STL, 10 plytek, 187 prac w prawdzie).

| Czesc kryterium | Liczba | Zrodlo | Werdykt |
|---|---|---|---|
| 400 wpisow | 400 wpisow, 400 geometrii (pula_400.csv: 401 wierszy z naglowkiem) | czas: `wpisow`, `geometrii` | tak |
| dwa wspolczynniki na plytce | 10 z 10 plytek ma prace z 1,20 i z 1,25 (razem 187 prac: 100 x 1,20 i 87 x 1,25) | pliki prawdy plytek | tak |
| STL w dwoch raportach | 27 plikow STL ma po 2 wpisy (krazek 1,20 i 1,25); `wpis_niejednoznaczny` = 0 z 187 | pula_400.csv, jakosc k2 | tak |
| top-1 "dobrze" 100 % | pula z blizniakami (k2): projekt 187 z 187, wpis 187 z 187; pula bez blizniakow (k1, 373 wpisy): projekt 187 z 187, wpis 187 z 187; zielone ze zlym wpisem 0 (bledow 0); prace cale z czerwonym 0 z 65 | jakosc: `zbiorczo` | ZAL |
| plytka do 40 s | zimna, plytka 1: 65,16 s (do 40 s: 0 z 1) | czas zimna: `plytki[0].czas_s` | przekroczone - O7 |
|  | zimna, plytki 2-10: maks. 35,53 s, mediana 25,48 s (do 40 s: 9 z 9) | czas zimna: `plytki[1..9].czas_s` | ZAL |
|  | ciepla, plytki 1-10: maks. 31,09 s, mediana 24,21 s (do 40 s: 10 z 10) | czas ciepla: `plytki[].czas_s` | ZAL |
| pamiec do 8 GB | szczyt zbioru roboczego procesu: 3961,5 MB = 3,87 GB (zimna), 3815,3 MB = 3,73 GB (ciepla); okno: wg raportu E3-A5 ok. 1,0 GB, nie mierzone w odbiorze; razem ok. 4,9 GB | czas: `szczyt_mb` (psutil peak_wset) | ZAL |

Czasy plytek [s]:
- zimna: 65,16 / 25,48 / 35,53 / 28,63 / 23,58 / 24,83 / 23,73 / 28,37 / 25,36 / 26,22 (budowa puli 299,59 s, 400 policzonych)
- ciepla: 30,56 / 23,57 / 31,09 / 23,71 / 23,59 / 24,64 / 23,78 / 26,23 / 23,37 / 25,64 (pula z dysku 1,05 s)

Pamiec - kontrola niezalezna (probnik Get-Process co 5 s, PeakWorkingSet64): proces przebiegu zimnego 3962 MB,
cieplego 3815 MB; przebieg `jakosc` (nie nalezy do liczby kryterium): proces roboczy 3821 MB + proces nadrzedny 137 MB.
Pamiec podreczna puli na dysku po przebiegach: 400 plikow, 2126,1 MB.

Wynik T4: ZAL z odstepstwem O7 - plytke 40 s przekracza TYLKO pierwsza plytka po zimnym starcie (65,16 s);
wszystkie plytki przy puli cieplej do 40 s (19 z 19, maks. 35,53 s).

Wolny RAM: 74550 MB przed startem, minimum w trakcie 70785 MB. Co jeszcze liczylo na PC: patrz WYNIK.md.
