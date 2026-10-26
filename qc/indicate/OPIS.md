# qc.indicate - Podswietlanie gniazd w ramkach LED

## Co robi

Wysyla do ramek swietlnych (Raspberry Pi z matryca LED) po Wi-Fi (HTTP/WebSocket) numery gniazd i kuwet do podswietlenia oraz odbiera zdarzenia z ramki (klawiatura, czujniki Halla).

## Wejscie

- z sesji porannej: kuweta biezaca i numery gniazd jej prac,
- adresy ramek z ustawien.

## Wyjscie

- komunikaty do ramek zawierajace wylacznie numery gniazd i kuwet (bez danych zlecen),
- zdarzenia z ramek przekazane do session/ui.

## Kryterium "dziala"

Na atrapie ramki (lokalny serwer testowy) zadane gniazda sa podswietlane w zadanej kolejnosci, a utrata polaczenia jest zglaszana operatorowi bez zawieszenia programu.

Nie zaimplementowano (etap 3).
