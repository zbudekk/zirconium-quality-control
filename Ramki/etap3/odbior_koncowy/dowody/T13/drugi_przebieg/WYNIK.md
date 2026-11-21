WERDYKT T13 (drugi przebieg, galaz e3/odbior 16f209d - po dodaniu dowodow): ZAL z odstepstwem O11 i O10 (naruszen 0; 7 plikow napisow ekranu nie-ASCII z 7 na liscie; kontrola na poziomie katalogow paczek); proba 1 na 807aa83 = FAIL (2 naruszenia w dowodach: pliki .csv), dowod poprawiony, proba 2 = 0 naruszen

# T13 - Higiena repo, drugi przebieg (po dodaniu dowodow) - 21.11.2026

Wykonawca: paczka E3-ODBIOR (etap 2). Worktree `<PC-katalog>\qc-wt\odbior`, galaz `e3/odbior`. Kroki lekkie, 1 proces python naraz.
`PY` = `<PC>\AppData\Local\Programs\Python\Python312\python.exe`, `<ODB>` = `Ramki\etap3\odbior_koncowy` w worktree.
Narzedzia `t13_higiena.py`, `t13_dozwolone.txt`, `t13_wyjatki_ascii.txt`, `dowody_lf.py` bez zmian (te same pliki co w commicie paczki 571e186).

## Proby (obie zapisane; nic nie powtarzano "az wyjdzie")

| Proba | Commit | Polecenie | Kod | Wynik |
|---|---|---|---|---|
| 1 (05:47:45) | 807aa83 (dowody T2, T4, T8, T11, T7/uzup dodane) | `PY -I <ODB>\narzedzia\t13_higiena.py --repo <PC-katalog>\qc-wt\odbior --od 2537f6f --do 807aa831aaf4bb0d5182d699168d8f7da6ab5124 --json ... > ...\t13_wynik.txt` | 1 | `NARUSZENIA (grupa E3 i sciezki poza listami): 2` - `dowody/T2/t2_procesy.csv` i `dowody/T4/t4_procesy.csv` -> "plik danych (.csv)"; `WYNIK T13: FAIL (2 naruszen)`; pliki: `proba_1_807aa83/` |
| 2 (05:48:14) | 16f209d (po poprawce dowodu) | to samo z `--do 16f209d2bd9de1706ac728df9f93751c8f7086f7` | 0 | `NARUSZENIA (grupa E3 i sciezki poza listami): 0`; `WYNIK T13: ZAL z odstepstwem O11 (0 naruszen; 7 plikow napisow ekranu nie-ASCII)`; stderr pusty; pliki: `t13_wynik.txt`, `t13_wynik.json` |

Przed proba 1 i przed proba 2: `PY -I <ODB>\narzedzia\dowody_lf.py --katalog <ODB>\dowody` BEZ `--napraw` - kod 0 i 0
("plikow 383, naruszen 0" i "plikow 388, naruszen 0"; `dowody_lf_caly_katalog.txt` = przebieg przed proba 2).
`git diff --stat 2537f6f 16f209d` -> `t13_diff_stat.txt` (kod 0): `1035 files changed, 217426 insertions(+), 1268 deletions(-)`.

## Naruszenie z proby 1 i poprawka (poprawiono DOWOD, nie narzedzie)

- Przyczyna: `t13_higiena.py` liczy rozszerzenie `.csv` jako plik danych (lista `DANE`), a wykonawca T2 / T4 zapisal probnik
  procesow (godzina; PID; pamiec; CPU; wolny RAM - 501 i 698 probek, 18 KB i 26 KB) jako `t2_procesy.csv` i `t4_procesy.csv`.
  `dowody_lf.py` przepuszcza `.csv` (lista rozszerzen tekstowych) - dlatego kontrola przed `git add` dala kod 0.
- Poprawka (commit 16f209d): KOPIE w repo przemianowane na `dowody/T2/t2_procesy_csv.txt` i `dowody/T4/t4_procesy_csv.txt`;
  tresc bez zmian (git: zmiana nazwy 100 %). Oryginaly na PC nadal `...\odbior\T2\t2_procesy.csv` i `...\T4\t4_procesy.csv`;
  `WYNIK.md` T2 i T4 oraz `dowody_lf.txt` tych katalogow podaja stara nazwe.
- Do decyzji koordynatora: czy `dowody_lf.py` ma odrzucac `.csv` (dzis dwa narzedzia tej samej paczki maja rozne listy).

## Liczby (proba 2, commit 16f209d)

| Licznik | Pierwszy przebieg (571e186) | Drugi przebieg (16f209d) |
|---|---|---|
| zmienionych sciezek / w tym nowych | 662 / 584 | 1051 / 973 |
| grupa E3: nowe / zmienione / usuniete | 245 / 24 / 0 | 634 / 24 / 0 |
| grupa R58: nowe / zmienione / usuniete | 242 / 4 / 0 | 242 / 4 / 0 |
| grupa R59: nowe / zmienione / usuniete | 97 / 34 / 16 | 97 / 34 / 16 |
| NARUSZENIA (grupa E3 i sciezki poza listami) | 0 | 0 |
| odstepstwo O11: pliki napisow ekranu nie-ASCII | 7 z 7 na liscie | 7 z 7 na liscie (te same liczby wierszy: 109, 134, 102, 240, 66, 111, 45) |
| uwagi w grupach R58 / R59 (poza wynikiem) | 126 | 126 |

Kontrola niezalezna (`git diff --name-status --no-renames`): 2537f6f..16f209d = 973 A + 62 M + 16 D = 1051 (zgodne z narzedziem);
571e186..16f209d = 389 A + 4 M, z czego w `odbior_koncowy/dowody/` 387 sciezek (wszystkie nowe); poza `dowody/` 6 sciezek:
`RAPORT.md`, `POKAZ_G3.md` (nowy), `wydania/README.md`, `wydania/SHA256SUMS_wydania.txt`, `wydania/Stanowisko_0.3.1.wydanie.json`
(nowy), `stanowisko/WERSJA` - 4 ostatnie z `main` c399482 (PR #48, wydanie 0.3.1). Roznica E3 nowe 634 - 245 = 389 (zgodne).

## Zastrzezenia

- Przebieg obejmuje stan galezi 16f209d. Pliki tego katalogu (`drugi_przebieg/`), dowody T9 i koncowy `RAPORT.md` doszly PO
  nim - ich higiene sprawdza `dowody_lf.py` bez `--napraw` na calym `dowody/` w kontroli koncowej paczki (opis: `dowody/README.md`).
- O10 bez zmian: kontrola na poziomie katalogow (przedrostek `Ramki/etap3/` obejmuje caly katalog dowodow).
