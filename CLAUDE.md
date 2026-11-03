# qc - zasady pracy

| Stos | |
|---|---|
| runtime | Python 3.12 (skrypty w `Ramki/narzedzia`, `Ramki/stanowisko`, `Ramki/ramka_generator.py`) |
| framework | brak (skrypty + HTML/JS do podgladu 3D) |
| testy | `python -m pytest -q` w katalogu z testami, jesli zadanie je wskazuje |
| CI | brak |
| dystrybucja | pakiety `Ramki_do_wgrania/*.zip` + SHA256SUMS (na Drive) |

Zasady: pliki po polsku bez znakow diakrytycznych (tresc przeniesiona z PC zostaje jak jest);
duze dane (STL skanow, `Prace_test`) nigdy do gita - patrz `.gitignore`; zmiana stosu, modelu danych
albo dystrybucji = najpierw opis dla czlowieka. Stan projektu: `Ramki/00_NADZOR_STAN.md`.

## Testy i Blender na PC (decyzja czlowieka 03.11.2026 - tylko ten projekt)

MSI nie ma RAM-u na Blender i WDAC blokuje czesc pakietow Python; sesje qc zlecaja takie zadania na PC
[usunieto w kopii: opis dostepu ssh]
musi byc wlaczony - WoL z MSI). Zasady: tylko zadania projektu qc, nic nie instaluj i nie kasuj na PC,
pliki robocze PC w `<PC>\Desktop\Ramki` (zrodlo tej kopii), wyniki wracaja na MSI.

- [usunieto w kopii: opis dostepu ssh]
  dluzszy skrypt: `powershell -NoProfile -EncodedCommand <base64 UTF-16LE>` (linia max 8 KB).
- [usunieto w kopii: opis dostepu ssh]
  pelna sciezka z `C:\Program Files\Blender Foundation\Blender 5.2`).
- Python: venv zalozony przez `uv` nie startuje w sesji ssh (blad 448); uzywaj
  `<PC>\AppData\Local\Programs\Python\Python312\python.exe` z `PYTHONPATH` na `.venv\Lib\site-packages`.
- [usunieto w kopii: opis dostepu ssh]
