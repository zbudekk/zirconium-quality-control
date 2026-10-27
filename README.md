# qc - stanowisko kontroli cyrkonii

Program stanowiska ze skanerem laboratoryjnym 3D we frezowni cyrkonii laboratorium protetycznego.
Wieczorem skanuje plytke z pracami w stanie zielonym, naklada kazda prace na jej projekt STL i oznacza
ukruszenia brzegow, zanim prace trafia do pieca. Rano z tego samego rodzaju skanu rozpoznaje, do
ktorego zlecenia (kuwety) nalezy kazda spieczona praca, a ramka swietlna z matryca LED podswietla
gniazda biezacej kuwety. Zlecenia, ktorych wszystkie punkty wyszly z pieca, program sam odhacza w
firmowym Excelu (zielone pole w kolumnie B) z logiem kazdej zmiany.

Repo zawiera program na laptopie (Python), program ramki na Raspberry Pi, modele plytek z ukladem
gniazd, testy na danych syntetycznych i narzedzia. Plan wdrozenia: "Stanowisko kontroli cyrkonii - plan
wdrozenia v2" (26.10.2026), poza repo.

## Uklad repo

- `qc/` - pakiet programu na laptopie stanowiska; kazdy modul ma `OPIS.md` (co robi, wejscie, wyjscie,
  kryterium "dziala"); `qc/ustawienia.py` wczytuje ustawienia.
- `modele/` - modele plytek z ukladem gniazd.
- `tests/` - testy pytest.
- `tests/dane/` - wylacznie syntetyczne dane testowe (zadnych prawdziwych STL, skanow ani raportow).

## Instalacja

Python 3.12:

```
python -m pip install -r requirements-ci.txt
```

Na Windows bez zainstalowanego Visual C++ Redistributable dodatkowo `python -m pip install msvc-runtime`
(wymagane przez open3d).

## Testy

```
python -m pytest -m "not wolne"
python -m pytest
```

Pierwsze polecenie uruchamia testy szybkie (jak CI dla PR), drugie wszystkie, razem z wolnymi metrykami.

## Watki i biblioteki numeryczne

Wielowatkowy OpenBLAS (mnozenia `@` w numpy) wolany z watku Pythona rownolegle z open3d (OpenMP) w
innym watku konczyl sie access violation. Dlatego `import qc` ustawia jeden watek BLAS
(`OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, przez `setdefault`), a gdy numpy jest juz zaladowane -
`qc.ogranicz_blas()` ustawia to samo w bibliotece OpenBLAS numpy przez ctypes. Program rownolegli
prace w watkach Pythona, wiec BLAS nie musi. open3d zostaje wielowatkowy (`OMP_NUM_THREADS` bez zmian).
Program stanowiska importuje `qc` przed numpy; testy ustawiaja zmienna na poczatku `tests/conftest.py`.

## Ustawienia

Sciezki i progi wykrywania sa w `ustawienia.toml` (nie w kodzie). Sciezki wzgledne liczone sa wzgledem
katalogu tego pliku. Na stanowisku nadpisuje sie je w `ustawienia.lokalne.toml` obok (plik
gitignorowany; moze tylko zmieniac istniejace klucze). Inny plik ustawien wskazuje zmienna
`QC_USTAWIENIA`. W kodzie: `from qc.ustawienia import wczytaj; u = wczytaj()`.
