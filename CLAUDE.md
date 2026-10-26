# qc - stanowisko kontroli cyrkonii

Program stanowiska kontroli koron i mostow z cyrkonii: kontrola ukruszen wieczorem (skan plytki vs projekt
STL), identyfikacja prac rano (praca -> kuweta/zlecenie), podswietlanie gniazd w ramkach LED i
automatyczne odhaczanie zlecen w Excelu. Zrodlo wymagan: "Stanowisko kontroli cyrkonii - plan wdrozenia
v2" (26.10.2026), sekcje 9 (moduly), 10 (dane i integracje), 14 (testy odbiorcze). Dokumentu nie ma w repo.

## Stos

| Obszar | Wybor |
|---|---|
| Runtime | Python 3.12 na laptopie Windows 11 (i7/i9, 32 GB, RTX); Python 3 na Raspberry Pi 4 (ramki) |
| Geometria i dopasowanie 3D | trimesh, numpy, Open3D (FPFH + RANSAC, ICP) |
| Interfejs | PySide6 (Qt) |
| Dane lokalne | SQLite (wbudowane), foldery OneDrive/SharePoint "Cyrkon" i "Prywatne", raporty MillBox (BeautifulSoup4, pypdf) |
| Integracje | Excel przez COM (pywin32), watchdog (folder eksportu skanera), pyautogui (opcjonalnie) |
| Ramka | rpi-rgb-led-matrix (Adafruit RGB Matrix Bonnet), evdev (klawiatura), czujniki Halla, HTTP/WebSocket po Wi-Fi |
| Testy | pytest na danych syntetycznych (sztuczne skany z prawdziwych STL: skala, szum 0,02-0,04 mm, ubytki 0,2-0,6 mm) |
| CI | GitHub Actions: pytest (do skonfigurowania przy pierwszym kodzie) |
| Dystrybucja | prywatne repo mbuasm/qc; na laptopie stanowiska wersja zamrozona (tag), aktualizacja jednym poleceniem |

Tylko darmowe biblioteki bez subskrypcji.

## Moduly (plan v2, sekcja 9)

`catalog`, `plate`, `match`, `inspect`, `session`, `ui`, `indicate`, `excel`, `scanner` + osobny program ramki.
Kazdy modul ma plik opisu dla Claude Code: co robi, wejscie, wyjscie, kryterium "dziala".
Kolejnosc budowy: generator danych testowych -> catalog/plate/match/inspect z metrykami
(wykryte / pominiete / falszywe) -> session/ui/indicate/excel -> scanner i integracja.

## Testy

```
python -m pytest
```

## Konwencje

- Jezyk plikow, komentarzy i komunikatow: polski bez znakow diakrytycznych.
- Skrypty PowerShell 5.1: ASCII, CRLF, bez `&&`.
- Prace na galeziach, PR do `main`; `main` = wersja do zamrozenia na stanowisku.
- RODO: zadnych prawdziwych STL, skanow, nazw folderow zlecen, wierszy Excela ani raportow MillBox w repo.
  W testach tylko dane syntetyczne/zanonimizowane. Program nic nie wysyla do internetu; ramki dostaja tylko
  numery gniazd i kuwet.
- Excel: zapis wylacznie koloru pola B (RGB 198, 239, 206), kazdy zapis do logu CSV; zmiany w module `excel`
  testuj na kopii pliku, nigdy na produkcyjnym.
- Progi wykrywania i sciezki w jednym pliku ustawien, nie w kodzie.

## Prog zmian

Zmiana stosu (nowa biblioteka zamiast wymienionej, platna zaleznosc, inny jezyk), modelu danych (schemat
SQLite, format pliku ukladu gniazd, format logu Excela), sposobu zapisu do Excela albo dystrybucji =
najpierw opis dla czlowieka (co, dlaczego, skutki), nie samowolna zmiana.
