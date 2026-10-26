# tests/dane - dane testowe (wylacznie syntetyczne)

Wszystkie pliki w tym katalogu sa wygenerowane proceduralnie przez `qc.syntetyka.prace`.
Nie ma tu prawdziwych STL, skanow, nazw zlecen, wierszy Excela ani raportow MillBox (RODO).

| Plik | Co to jest |
|---|---|
| `wzorce/korona-wzorzec.json` | przepis korony (trzonowiec, ziarno 1, krok 0,8 mm) - tylko do regresji |
| `wzorce/korona-wzorzec.stl` | siatka z tego przepisu (STL binarny) |
| `wzorce/most-wzorzec.json` | przepis mostu 3-punktowego (ziarno 1, krok 1,0 mm) - tylko do regresji |
| `wzorce/most-wzorzec.stl` | siatka z tego przepisu (STL binarny) |
| `przepisy/pula30.json` | lista 30 przepisow puli (id, ziarno, rodzaj, krok) bez geometrii |

Gruby krok wzorcow sluzy tylko do sprawdzenia, ze generator daje te same siatki co wczesniej
(test `test_wzorce_zgodne`). Zmiana generatora zmieniajaca geometrie = ponowne wygenerowanie wzorcow
w tym samym PR i opis zmiany.

## Limity

- tylko pliki `.stl`, `.json`, `.md`;
- kazdy plik <= 300 KB (STL binarny: ok. 6000 scian), razem <= 1 MB (test `test_rozmiar_danych`).

## Jak odtworzyc

Z katalogu repo:

```
python -c "from qc.syntetyka import prace; prace.zapisz_dane_testowe('tests/dane')"
```
