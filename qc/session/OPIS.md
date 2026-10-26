# qc.session - Sesja kontroli

## Co robi

Prowadzi sesje kontroli: wieczorna (skan plytki z pracami w stanie zielonym, kontrola ukruszen wzgledem projektow STL) i poranna (identyfikacja spieczonych prac: praca -> kuweta/zlecenie). Laczy moduly catalog, plate, match i inspect w jeden przebieg i zapisuje wynik w SQLite.

## Wejscie

- skan plytki (z modulu scanner) i rodzaj sesji: wieczor albo rano,
- pula projektow z katalogu (catalog) i uklad gniazd plytki (plate),
- ustawienia z qc.ustawienia (progi dopasowania i ubytkow, sciezka bazy).

## Wyjscie

- wynik sesji: dla kazdego gniazda praca, zlecenie/kuweta, pokrycie, lista ubytkow,
- zapis sesji w bazie SQLite (sciezki.baza) dla ui, indicate i excel.

## Kryterium "dziala"

Na syntetycznym skanie plytki sesja wieczorna zwraca wszystkie wstawione ubytki bez falszywych, a sesja poranna przypisuje kazda prace do wlasciwego zlecenia; wynik jest odtwarzalny z bazy.

Nie zaimplementowano (etap 3).
