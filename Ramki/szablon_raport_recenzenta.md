# Raport recenzenta — etap {A|B|C|ALL}, iteracja {n}

Plik: `recenzja/raport_recenzenta_{etap}_iter{n}.md`. Wypełnia recenzent po własnych, niezależnych pomiarach plików z `wyniki_v2/` (skrypt `recenzja/sprawdz_{etap}.py`, uruchamiany `blender -b -P recenzja/sprawdz_{etap}.py`).

## 0. Werdykt
**ETAP {etap}: ZALICZONY / NIE ZALICZONY** — B = …, P = …, D = … (liczba sprawdzeń NIE w każdej wadze). Kryterium: ZALICZONY ⇔ B = 0 ∧ P = 0 ∧ brak N/D tam, gdzie etap wymaga wykonania.

## 1. Niezależność pomiaru
- Sumy SHA‑256 sprawdzanych plików zgodne z raportem wykonawcy: TAK / NIE (lista różnic)
- Skrypt recenzenta napisany bez czytania `ramka_generator.py`: TAK (kod wykonawcy otwarto dopiero przy analizie: K‑… )
- Powtarzalność (K‑59, tylko etap C/ALL): przebieg w czystej kopii: TAK/NIE; STL identyczne bajt w bajt: …/… ; różnice objętości max … cm³

## 2. Wyniki sprawdzeń
| Id | Wynik | Zmierzone przez recenzenta | Zadeklarowane przez wykonawcę | Oczekiwane | Waga | Uwaga |
|---|---|---|---|---|---|---|
| K‑01 | … | … | … | … | B | … |

## 3. Uwagi do poprawy (tylko NIE), z numerami
| Nr uwagi | K‑xx | Waga | Plik / cecha | Co jest | Co ma być (odwołanie do planu v2: sekcja, parametr) |
|---|---|---|---|---|---|
| U‑{etap}{n}‑1 | … | B | … | … | … |

## 4. Rozbieżności między raportem wykonawcy a pomiarem recenzenta
(wartości zadeklarowane ≠ zmierzone; każda taka rozbieżność jest co najmniej P)

## 5. Ocena rejestru odstępstw wykonawcy
| # odstępstwa | Zasadne? | Wymaga decyzji właściciela? | Komentarz |
|---|---|---|---|

## 6. Lista drobnych (D) do v3
