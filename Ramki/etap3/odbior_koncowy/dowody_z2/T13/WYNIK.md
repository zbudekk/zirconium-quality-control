WERDYKT T13 (drugi przebieg, galaz e3/odbior2 z dowodami zlecenia 2, commit db329c8): ZAL z odstepstwem O11 i O10 + kopie bajtowe R58 (decyzja wlasciciela nr 1 z 21.11.2026; Z2-N7) - naruszen 0, kod 0

# T13 - drugi przebieg na galezi e3/odbior2 (21.11.2026, wykonawca F5 zlecenia 2)

Pierwszy przebieg T13 (commit wydania 0fedbf6) jest w `../T1/WYNIK.md` (sekcja "T13") i `../T1/t13_wynik.txt`. Ten przebieg sprawdza
stan galezi z dowodami `dowody_z2/` i sekcja 10 `RAPORT.md` - jak drugi przebieg nocy (`../../dowody/T13/drugi_przebieg/`).

- Commit: db329c83bb445edb59f505c9c13b13e52aff6e07 (galaz `e3/odbior2` = `main` 1f231d9 + 3 commity: dowody T0 / T1 / T2 / T12,
  dowody T10, dowody T11 + sekcja 10 raportu). Tego pliku i commita, ktory go dodaje, ten przebieg nie obejmuje (commit nie moze
  sprawdzic sam siebie) - kontrola koncowego HEAD galezi: ostatnia wiadomosc wykonawcy do koordynatora.
- Polecenie (Git Bash, katalog `Ramki/etap3/odbior_koncowy` worktree `<PC-katalog>\qc-wt\odbior2`; `PY` =
  `<PC>\AppData\Local\Programs\Python\Python312\python.exe`), 21.11.2026 21:10:03 - 21:10:04, kod 0:
  `PY -I narzedzia/t13_higiena.py --repo <PC-katalog>/qc-wt/odbior2 --od 2537f6f --do db329c83bb445edb59f505c9c13b13e52aff6e07 --json dowody_z2/T13/t13_wynik.json > dowody_z2/T13/t13_wynik.txt 2> dowody_z2/T13/t13_wynik_stderr.txt`
  (stderr: 0 bajtow). Narzedzie z tej samej galezi (= `main`; bez zmian wobec commita wydania).

| Liczba | Drugi przebieg (db329c8) | Pierwszy przebieg (0fedbf6) | Noc, drugi przebieg (16f209d) |
|---|---|---|---|
| zmienionych plikow od 2537f6f (w tym nowych) | 1350 (1267) | 1145 (1062) | 1051 (973) |
| grupa E3: nowe / zmienione / usuniete | 928 / 29 / 0 | 723 / 29 / 0 | 634 / 24 / 0 |
| NARUSZENIA (grupa E3 i sciezki poza listami) | **0** | 0 | 0 |
| O11: pliki napisow ekranu nie-ASCII na liscie | 7 z 7 (851 wierszy) | 7 z 7 (851 wierszy) | 7 z 7 (807 wierszy) |
| kopie bajtowe R58 (suma = lista R58) | 10 z 10 | 10 z 10 | - (pliki powstaly w zleceniu 2) |
| uwagi R58 / R59 poza wynikiem | 126 | 126 | 126 |

Roznica wobec pierwszego przebiegu: +205 nowych plikow grupy E3 = dowody `dowody_z2/` (198) i pliki dodane do `main` po wydaniu
(1f231d9: opis zawartosci 0.3.3 i 6 raportow recenzji). Wszystkie nowe pliki `dowody_z2/` przeszly kontrole ASCII, koncow linii, danych
i rozmiaru (0 naruszen). Wiersz `WYNIK T13` narzedzia: `ZAL z odstepstwem O11 (0 naruszen; 7 plikow napisow ekranu nie-ASCII; 10 kopii
bajtowych R58 - decyzja wlasciciela nr 1 z 21.11.2026)`. O10 (kontrola na poziomie katalogow paczek) - jak w nocy.

Pliki: `t13_wynik.txt` (wyjscie narzedzia; konce linii poprawione `dowody_lf.py --napraw`), `t13_wynik.json`, `t13_wynik_stderr.txt`
(0 B), `dowody_lf.txt`.
