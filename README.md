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

## Ustawienia

Sciezki i progi wykrywania sa w `ustawienia.toml` (nie w kodzie). Sciezki wzgledne liczone sa wzgledem
katalogu tego pliku. Na stanowisku nadpisuje sie je w `ustawienia.lokalne.toml` obok (plik
gitignorowany; moze tylko zmieniac istniejace klucze). Inny plik ustawien wskazuje zmienna
`QC_USTAWIENIA`. W kodzie: `from qc.ustawienia import wczytaj; u = wczytaj()`.
