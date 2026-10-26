# qc.ui - Interfejs stanowiska

## Co robi

Interfejs operatora w PySide6 (Qt): start sesji wieczornej i porannej, podglad plytki z gniazdami, lista prac z ukruszeniami do obejrzenia, potwierdzanie i korekta przypisan.

## Wejscie

- wyniki sesji (session) i stan ramek (indicate),
- dzialania operatora: start/stop sesji, akceptacja lub odrzucenie wyniku gniazda.

## Wyjscie

- polecenia dla session, indicate i excel,
- widok stanu plytki i prac, komunikaty po polsku.

## Kryterium "dziala"

Operator przeprowadza sesje wieczorna i poranna na danych syntetycznych bez uzycia konsoli; kazda decyzja operatora trafia do bazy sesji.

Nie zaimplementowano (etap 3).
