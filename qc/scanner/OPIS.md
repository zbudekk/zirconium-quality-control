# qc.scanner - Folder eksportu skanera

## Co robi

Obserwuje folder eksportu skanera (watchdog) i przekazuje nowe, kompletnie zapisane skany plytki do sesji; opcjonalnie uruchamia eksport w programie skanera (pyautogui).

## Wejscie

- sciezki.eksport_skanera i skaner.gestosc_mm z ustawien,
- pliki skanow pojawiajace sie w folderze eksportu.

## Wyjscie

- zdarzenie "nowy skan" z sciezka pliku i chmura punktow dla session,
- komunikat o bledzie przy niepelnym lub uszkodzonym pliku.

## Kryterium "dziala"

Syntetyczny skan zapisany do folderu testowego jest wykryty raz, dopiero po zakonczeniu zapisu, i przekazany do sesji.

Nie zaimplementowano (etap 3).
