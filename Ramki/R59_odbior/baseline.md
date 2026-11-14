# R59 - punkt odniesienia (stary uklad R54/R57, PRZED zmianami)

Data: 2026-11-14, koordynator R59. Kod: `origin/main` 4cc6090. Miejsce: PC, konto `<konto-PC>`, katalog
`<PC-katalog>\r59\baseline\` (program = `git archive HEAD Ramki/stanowisko Ramki/parametry.json`; dane
`syntetyczne_P2`, `syntetyczne_P3a`, `katalog.json`, `ustawienia.toml` skopiowane z pulpitu; projekty
`<PC-katalog>\r59\Prace_test`, 17 STL). Generator: osobna kopia `baseline\gen\Ramki` (kopia `r59\Ramki` bez `stanowisko`).

## 1. Testy programu

| Przebieg | passed | skipped | failed | czas |
|---|---|---|---|---|
| 1 (kopia bez git) | 165 | 3 | 1 | 93 s |
| 2 (kopia z `git init` + `git add -A Ramki`) | **166** | **3** | **0** | 85 s |

- Przebieg 1: `test_ustawienia.py::test_repo_nie_sledzi_danych_ani_ustawien_maszyny` wola `git ls-files`; kopia z
  `git archive` nie jest repozytorium (kod 128). To cecha kopii, nie programu. Kazda kopia testowa na PC (R59-P, T5)
  wymaga wiec `git init -q . && git add -A Ramki` w katalogu nad `Ramki`.
- Pominiete (3): `test_katalog.py:133` i `test_ui.py:126` - brak folderu projektow z pulpitu (na PC nie ma
  `Desktop\Prace_test`); `test_ui.py:67` - okno jest szkicem (P3a).
- Rozjazd z raportem P3a z 2.11 (167 passed, 2 skipped): dzis 169 testow; 2 testy zalezne od folderu z pulpitu sa
  pomijane na koncie `<konto-PC>`. Punkt odniesienia dla T5 = **166 passed, 3 skipped, 0 failed**.
- Log: `baseline/pytest_baseline.log`.

## 2. Sumy SHA-256 (PC `r59\Ramki\wyniki_v2`)

21 STL + 4 JSON: 23 plikow zgodnych z `Ramki_pakiet/SHA256SUMS_2026-11-02_R57.txt`; 2 pliki nie sa w pakiecie
(bazowe kwadratowe `ramka_plytka_wieczorna_v2.stl` fa77f61d..., `ramka_plytka_poranna_v2.stl` dd00fcda...). Kopia MSI
(`<MSI>\kod\qc\Ramki\wyniki_v2`) = PC 25/25. Lista: `baseline/sha256_wyniki_v2_przed_R59.txt`.
Pliki zrodla prawdy PC = galaz 4/4 (generator 09268b14, parametry b7b52942, protokol e910edb2, plan 8ce66391).

## 3. Generator - `--etap SPRAWDZ --iter 90 --raport BASELINE`

Wynik: **B = 0, P = 0, D = 0** (58 ZAL, 5 N/D, 0 NIE), czas ok. 1 min, kod wyjscia 0. Raport:
`<PC-katalog>\r59\baseline\gen\Ramki\wyniki_v2\raport\raport_wykonawcy_BASELINE_iter90.md`. K-60: ZAL na istniejacych
plikach PNG (rozmiary), rendery w trybie SPRAWDZ nie powstaja - czy Cycles dziala na koncie `<konto-PC>`, okaze sie w R59-A.

## 4. Metryki P3a (`narzedzia/metryki_P3a.py`, zestawy P2 + P3a, 11 min 13 s)

40 skanow, 420 prac w prawdzie (449 fragmentow), wyrownanie OK 40/40 (max 0,0137 mm), top-1 411/420, na zestawie P2
271/271; numer z dolkow na okraglych 24/24; czas na plytke (mediana) 12,3 s.

| scenariusz | prac | top-1 bledny | ubytkow wykrywalnych | A | B | A+B | czerwone | dowolna | prace cale | cale z alarmem | cale z czerwonym | falszywe ubytki | falszywe czerwone |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dobrze | 300 | 0 | 279 | 229 | 132 | 103 | 112 | 258 (92,5 %) | 103 | 0 | 0 | 0 | 0 |
| bokiem | 76 | 27 | 3 | 1 | 1 | 1 | 1 | 1 | 20 | 1 | 0 | 3 (B) | 0 |
| czesciowo | 36 | 8 | 0 | - | - | - | - | - | 6 | 0 | 0 | 0 | 0 |
| drgniecie | 37 | 3 | 0 | - | - | - | - | - | 0 | 0 | 0 | 0 | 0 |
| razem | 449 | 38 | 282 | 230 | 133 | 104 | 113 | 259 (91,8 %) | 129 | 1 | 0 | 3 | 0 |

- Drgniecie 28/34, poprawki reczne 12/20. Zgodne z `stanowisko/raporty/P3a_przekazanie.md` pkt 1 we wszystkich
  liczbach wykrywania i top-1.
- Rozjazdy z raportem z 2.11 (drobne, zanotowane): statusy gniazd razem zolte 158 / szare 41 (raport: 157 / 42);
  falszywe "skan ponownie" 1 (raport: 0). Dalej obowiazuja liczby zmierzone dzis.
- Pliki: PC `baseline\metryki\metryki_P3a.json`; skrot `baseline/metryki_P3a_skrot.json`.

## 5. Skany seed 7001 (do testu T8)

Polecenia (katalog programu, `run.cmd` jak w planie pkt 2.4):
`-m stanowisko.synth --projekty <projekty> --plytka <P> --ile 1 --seed 7001 --wspolczynnik <1.22 wieczorne | 1.0 poranne> --drgniecie 0.1 --poza-uklad --pole 100 --wyjscie <t8>`
`-m stanowisko.porownaj --skan <t8>\<skan>.stl --projekty <projekty> --plytka <P> --wspolczynnik <w> --numer <N> --prawda <t8>\<skan>.json --wyjscie <t8>\wynik`

| skan | numer | wyrownanie max [mm] | prac | fragment w swoim gniezdzie | top-1 | zielone / czerwone / zolte |
|---|---|---|---|---|---|---|
| wieczorna n3 | podany | 0,0043 | 9 | 9/9 | 9/9 | 1 / 3 / 5 |
| poranna n6 | podany | 0,0070 | 9 | 9/9 | 9/9 | 3 / 2 / 4 |
| okragla_wieczorna n8 | z dolkow | 0,0014 | 9 | 9/9 | 9/9 | 2 / 2 / 5 |
| okragla_poranna n9 | z dolkow | 0,0015 | 8 | 8/8 | 8/8 | 2 / 3 / 3 |

- `synth` bez `--numer` wylosowal na kwadratach n3 i n6; w T8 podac `--numer 3` / `--numer 6` jawnie.
- Mapa gniazdo -> projekt (skrot) -> status: `baseline/t8_mapa_seed7001.json`. Pelne `_wynik.json` i skany:
  PC `baseline\t8\`.

## 6. Uwagi srodowiskowe

- `gh` na MSI: token niewazny, `git fetch` i `git push` nie dzialaja do czasu logowania wlasciciela kodem urzadzenia.
- Narzedzia Read / Write / Edit / PowerShell zwracaja blad ksztaltu wyniku dla plikow w worktree (maskowanie nazwy
  katalogu przez wtyczke); praca przez Bash.
