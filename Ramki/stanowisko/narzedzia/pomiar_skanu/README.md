# pomiar_skanu - pomiar szczegolowy wlasciwosci skanu (narzedzie T10)

Kopia narzedzia z sesji testowej T10 (06.11.2026, `raporty/testy_krawedz/T10/skrypty/` - poza gitem), zeby bylo
dostepne na laptopie w dniu testu skanera. Mierzy z prawdziwego pliku skanu to, co w testach programu bylo zgadywane:
szum i jego korelacje na plaskiej czesci plytki, odstep punktow, blad skali kazdej korony wzgledem projektu
x wspolczynnik, braki danych i zaokraglenie na krawedzi brzegu, a z dwoch skanow bez ruszania - powtarzalnosc.

| Plik | Co | Zmiany wzgledem T10 |
|---|---|---|
| `pomiar_skanu.py` | pomiar i raport (`raport.txt`, `pomiar.json`) | bez zmian (SHA-256 `a609778a71edd4ba...`) |
| `c_wspolne.py` | linie krawedzi z projektu (kopia z T3) | bez zmian (SHA-256 `f45046438231a8b6...`) |
| `pomiar_skanu.cmd` | uruchomienie przez przeciagniecie pliku | tylko sciezki: program stanowiska szukany wzgledem pliku, Python przez `py -3.12` |

## Uzycie

1. Z okna "Dzien skanera": zaznacz skan w tabeli -> "Pomiar szczegolowy zaznaczonego skanu (osobne okno)". Okno pyta
   o wspolczynnik i o folder z projektami STL TYLKO tych koron, ktore leza na plytce (Anuluj = pomiar samej plytki).
   Pomiar idzie w osobnym procesie i nie wplywa na zbieranie plikow. Wynik: `<sesja>/pomiary/k<id>_<nazwa>_pomiar/`
   (trafia do paczki ZIP). W kroku "to samo drugi raz" pomiar dostaje tez skan odniesienia (`--powtorka`).
2. Recznie: przeciagnij plik skanu (albo dwa: skan i powtorke) na `pomiar_skanu.cmd`; projekty w folderze `projekty`
   obok skanu. Wynik w folderze `<skan>_pomiar` obok skanu.
3. Z wiersza polecen (katalog `stanowisko/`):
   `py -3.12 narzedzia/pomiar_skanu/pomiar_skanu.py SKAN.stl [--projekty FOLDER] [--wspolczynnik 1.22] [--powtorka SKAN2.stl] [--wyj KATALOG] [--bez-plytki]`

Jak czytac raport i progi orientacyjne: `raporty/testy_krawedz/T10/INSTRUKCJA_test_skanera.md` (poza gitem) - skrot:
szum sigma do 0,015 mm dobrze, ponad 0,025 zle; odstep punktow do 0,05 mm dobrze, ponad 0,08 zle; blad skali ponizej
0,1 % dobrze, od 0,2 % zle; krawedz bez danych ponizej 5 % dobrze, ponad 10 % zle. Progi pochodza z testow na skanach
sztucznych - to wskazowka, nie decyzja.

## Granice

- Narzedzie importuje `stanowisko.match`, `stanowisko.inspect` i `stanowisko.ustawienia` (tylko odczyt). Po przebudowie
  tych modulow trzeba je uruchomic ponownie na skanie sztucznym i sprawdzic, czy dziala.
- Sprawdzone tylko na koronach pojedynczych (mosty: "brak dopasowania do projektu").
- Raport nie zawiera nazw plikow projektow (projekt = 16 znakow SHA-256), tylko nazwe pliku skanu.
- `c_wspolne.py` ma stale ze sciezka z komputera testowego (`PRACE`); `pomiar_skanu.py` ich nie uzywa.
- Czas wg instrukcji T10: zwykle 2-6 minut na skan (zalezy od liczby koron i projektow).
