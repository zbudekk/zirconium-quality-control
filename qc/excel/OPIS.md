# qc.excel - Odhaczanie zlecen w Excelu

## Co robi

Przez COM (pywin32) oznacza w firmowym Excelu zlecenia, ktorych wszystkie punkty wyszly z pieca: zapisuje wylacznie kolor pola w kolumnie B (RGB 198, 239, 206). Kazdy zapis trafia do logu CSV.

## Wejscie

- lista zakonczonych zlecen z sesji porannej,
- sciezka skoroszytu i sciezki.log_excela z ustawien.

## Wyjscie

- zielone pole B w wierszach zakonczonych zlecen (bez zmiany innych komorek),
- wiersz w logu CSV dla kazdego zapisu.

## Kryterium "dziala"

Na kopii skoroszytu (nigdy na produkcyjnym) zmienia sie tylko kolor pola B wlasciwych wierszy, a log CSV zawiera dokladnie te zapisy.

Nie zaimplementowano (etap 3).
