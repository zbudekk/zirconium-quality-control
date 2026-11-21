# Dzien skanera - karta na jedna strone (16.11.2026)

Cel dnia: zebrac komplet pierwszych skanow i danych z programu skanera. Pilnuje tego okno "Dzien skanera - krok po
kroku". Na laptopie z programem zainstalowanym z paczki wydania uruchamia je `C:\Stanowisko\Dzien_skanera.cmd` (dwuklik;
`C:\Stanowisko` = katalog instalacji). Tylko w kopii roboczej programu (bez instalacji): `stanowisko\uruchom_dzien_skanera.bat`.
Klikanie w programie skanera: `sciaga_skaner_DentalScan_2026-11-16.md`. (Uruchamianie i sciezki poprawione 21.11.2026.)

## Dzien wczesniej

- [ ] **Plytki** (stare, uklad R54): kwadratowa wieczorna nr 1, kwadratowa poranna nr 4; jesli sa - okragle nr 8 i 9.
      Czyste, stozki w rogach bez pylu.
- [ ] **Prace:** 6-10 calych zielonych koron (pojedyncze, najlepiej z roznych blokow) i **etykiety blokow**
      (wspolczynniki); 2-3 prace do celowego ukruszenia (moga byc odrzuty); jesli sa - kilka prac spieczonych.
- [ ] Narzedzie do ukruszen, cienki patyczek (potracenie pracy), telefon (zdjecia ukruszen).
- [ ] **Laptop z programem stanowiska:** `C:\Stanowisko\Dzien_skanera.cmd` otwiera okno (sprawdzic dzien wczesniej,
      kliknac "Zrzut ekranu" na probe i zamknac). Folder skanera okno bierze z `C:\Stanowisko\ustawienia.toml`
      (wiersz `folder_eksportu_skanera`). Zasilacz. Po takiej probie okno w dniu testu zapyta o niedokonczona
      sesje (0 plikow) - odpowiedz "Tak" albo "Nie", obie odpowiedzi sa dobre.
- [ ] **Wolne miejsce na dysku laptopa:** co najmniej 30 GB (program skanera chce ponad 20 GB na zlecenia; sesja
      z kopia folderu i archiwum to kilka GB). Okno pokazuje wolne miejsce u gory.
- [ ] **Pendrive albo dysk** co najmniej 16 GB, format exFAT albo NTFS.
- [ ] Wydruk: ta karta i sciaga. Kartka i dlugopis na zapas.

## W dniu testu - kolejnosc (taka sama jak w oknie)

| Nr | Krok | Co ma powstac |
|---|---|---|
| - | Instalator podlacza i kalibruje skaner. **Okno "Dzien skanera" uruchom PRZED pierwszym skanem** | u gory okna folder "Obserwuje" |
| 1 | Zanim zaczniesz | zrzut ekranu na probe |
| 2 | Ustawienia programu skanera | 4 zrzuty ("Order Setting", "Scan Setting", "About"), wpisany folder zapisu |
| 3 | Pytania do instalatora (opcjonalnie) | odpowiedzi w notatce |
| 4 | Zlecenie testowe TEST1 ("New Order" -> "Restoration" -> "Multidie Mode") | 2 zrzuty |
| 5 | Skan 1: pusta plytka | plik STL, numer plytki, zielona ocena |
| 6 | Skan 2: plytka z pracami calymi | plik STL, wspolczynniki, czas skanu (stoper). **Potem nie ruszac plytki** |
| 7 | Skan 3: to samo drugi raz, bez ruszania | drugi plik STL (inna nazwa) |
| 8 | Ten sam skan zapisany inaczej (opcjonalnie) | plik STL + co zmieniono |
| 9 | Skan 4: 2-3 prace celowo ukruszone | plik STL, gniazda i miejsca ukruszen |
| 10 | Skan 5: praca potracona w trakcie skanu (opcjonalnie) | plik STL |
| 11 | Skan 6: praca bokiem i praca czesciowo zaslonieta | plik STL, ktore gniazda |
| 12 | Skan 7: druga plytka - poranna albo okragla (opcjonalnie) | plik STL |
| 13 | Zdjecia z kamer "Save Image" (opcjonalnie) | pliki zdjec |
| 14 | Kopia CALEGO folderu zlecen programu skanera | przycisk "Skopiuj caly folder zlecen skanera" |
| - | **"Zakoncz i spakuj"** | raport i archiwum ZIP w `C:\Stanowisko\dane\dzien_skanera\<data>\paczka\` |

Przy kazdym skanie: przeczytaj instrukcje w oknie -> skan w programie skanera (Spacja) -> zapis -> poczekaj na ocene
w oknie (zielone / zolte / czerwone). Czegos nie da sie zrobic: "Nie udalo sie / pomijam, bo ..." i jedno zdanie.

## 5 zasad bezpieczenstwa danych

1. **W programie skanera niczego nie kasuj** - zadnych zlecen, skanow ani zaznaczonych danych (klawisz Delete).
2. **Nie zamykaj zlecenia ani programu skanera, dopoki okno nie pokaze kopii pliku**, a na koniec - dopoki nie
   skonczy sie kopia calego folderu i pakowanie.
3. **Bez wygladzania, wypelniania otworow i obcinania plytki.** Plaszczyzna ciecia zostaje ponizej wierzchu plytki.
4. **Zapisuj wszystko, co program pozwala zapisac.** Watpliwosc = zrzut ekranu (przycisk w oknie) i notatka.
5. **Zadnych nazwisk** w nazwach zlecen i plikow (TEST1, TEST2 ...). **Folderu sesji nie kasuj**, dopoki koordynator
   nie potwierdzi odbioru.

## Gdy cos nie dziala

- Plik nie pojawia sie w oknie: w programie skanera "Explore" (folder zlecenia) albo "Go to Send" -> "Export";
  w oknie "Nie wiem, gdzie skaner zapisuje - szukaj" albo "Dodaj folder...".
- Czerwona ocena: zrob to, co pisze okno po slowach "ZROB TAK". Plik i tak jest zachowany.
- Czerwony pasek "Brak miejsca na dysku": zwolnij miejsce na laptopie (nie w programie skanera); okno skopiuje plik samo.
- Okno zamknelo sie albo laptop sie zawiesil: uruchom `Dzien_skanera.cmd` jeszcze raz i na pytanie
  o niedokonczona sesje odpowiedz "Tak" - nic nie ginie, pliki zapisane w przerwie skopiuja sie same.
- Okno w ogole nie startuje: po kazdym skanie kopiuj recznie caly folder zlecen programu skanera na pendrive,
  zdjecia ekranu rob telefonem, notuj na kartce. Niczego nie kasuj.

## Co wyslac po tescie

1. Wszystkie pliki ZIP z `C:\Stanowisko\dane\dzien_skanera\<data_godzina>\paczka\` (Drive albo pendrive). Z kopii
   roboczej programu: `stanowisko\dane\dzien_skanera\<data_godzina>\paczka\`.
2. Zdjecia ukruszen z telefonu, jesli nie zostaly dodane w oknie.
3. Jedno-dwa zdania: co poszlo inaczej, niz bylo w instrukcjach.

Koordynator sprawdza paczke poleceniem `C:\Stanowisko\Dzien_skanera.cmd --sprawdz <plik zip>` (z kopii roboczej
programu: `py -3.12 -m stanowisko.dzien_skanera --sprawdz <plik zip>`).
