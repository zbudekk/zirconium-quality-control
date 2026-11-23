# Dzien testu 28-29.11.2026 - wariant: tylko laptop i skaner

Decyzja wlasciciela 23.11.2026: w dniu testu jest laptop i skaner; elektroniki ramki nie ma. Testujemy wszystko,
co sie da bez ramki. Ten plik zmienia zakres `PIERWSZE_TESTY_NA_SPRZECIE.md`; numery krokow odnosza sie do niego.

## Co odpada, co zostaje

- ODPADA cala Czesc 3 (ramka): kroki 3.2-3.9. Krok 3.1 (pasowanie plytek do wydrukowanej ramki, bez pradu) tylko
  wtedy, gdy sama ramka bez elektroniki jest pod reka. Pytania P1, P3, P6, P8 sa nieaktualne.
- ZOSTAJE: Czesc 1 (program na laptopie - nowym instalatorem zamiast krokow 1.1-1.3), Czesc 2 (skaner), Czesc 5
  (co przywiezc). Czesc 4 nie dotyczy (to nie laptop stanowiska).
- Program skanera i program "Stanowisko" dzialaja na TYM SAMYM laptopie, wiec "Stanowisko" samo obserwuje folder,
  do ktorego skaner zapisuje pliki (przyjete z opisu wlasciciela; gdyby skaner mial wlasny komputer - skany
  przenosi sie pendrivem do folderu wskazanego przy instalacji).

## Kolejnosc dnia

1. Instalacja programu z pendrive'a (okno instalatora: folder skanow, folder projektow, osoby).
2. Okno "Dzien skanera": ustawienia programu skanera, skan pustej plytki, pole skanera (kroki 2.1-2.4).
3. Skany wedlug okna: prace cale, to samo drugi raz bez ruszania plytki, prace ukruszone, praca potracona, praca
   bokiem i czesciowo zaslonieta, druga plytka (kroki 2.5, 2.5a). Plytka glowna: okragla testowa R54 nr 8.
4. Program "Stanowisko" na prawdziwych skanach (krok 2.7): czy sam zauwaza skan, czy poznaje plytke i numer, ile
   trwa plytka, czy kolory prac zgadzaja sie z kartka.
5. Proby wynikajace z analizy kodu (nowe, po 5-10 minut kazda):
   - a) 2-3 prace z odpryskiem brzegu roznej wielkosci, w tym jeden plytki odprysk (S1-01, S1-02);
   - b) ta sama praca z ubytkiem zeskanowana drugi raz, ubytkiem w dol albo w cien - czy zostaje czerwona (S3-1);
   - c) 2-3 mm brzegu calej pracy zaklejone tasma albo plastelina - czy wychodzi "nie sprawdzono" (S1-01);
   - d) praca polozona bokiem albo do gory nogami - czy nie jest zielona (S1-04);
   - e) dwie plytki kwadratowe jedna po drugiej bez podania numeru pierwszej - czy panel numeru sie nie myli (S3-3);
   - f) uruchomienie programu, gdy w folderze skanera leza juz wczesniejsze skany - pytanie "Przelicz / Pomin".
6. "Zakoncz i spakuj" w oknie "Dzien skanera" - paczka ZIP na pendrive (krok 2.6).

## Czego wlasciciel NIE odczytuje sam

Liczby potrzebne do rozstrzygniecia znalezisk S1-01 - S1-03 (odstep wierzcholkow siatki skanu, czy sa wierzcholki
na przelomie odprysku, `pierscien_mediana_mm`, `stan_linii`, pary `status` / `status_gniazda`) odczytuje sesja
z paczki ZIP i z folderu wynikow programu. Na miejscu wystarczy kartka: ktore gniazdo, jaki ubytek, co pokazal ekran.

## Co przygotowac

- Projekty STL z exocad (`*_cad.stl`) tych prac, ktore beda skanowane. Bez nich wszystkie prace sa szare ("bez
  projektu") i wykrywania ubytkow nie da sie sprawdzic - zostaje test skanera, plytek i zbierania skanow.
- 2-3 prace celowo ukruszone (w tym jeden plytki odprysk) i kartka: gniazdo, miejsce, przyblizony rozmiar.
- Tasma albo plastelina (proba c), pendrive na paczke ZIP, plytki: okragla R54 nr 8 i kwadratowe, jesli sa.
- W programie skanera osobny folder / zlecenie testowe, zeby dane pacjentow nie trafily do paczki (P9).

## Czego ten dzien nie sprawdzi

Wszystko, co wymaga ramki: diody, odczyt numeru plytki z magnesow, zielony pierscien (S3-7), czas trzymania planu
(S3-10), blad sieci ramki (S3-12), orientacja panelu (S3-17). Excel - tylko gdy jest zainstalowany na laptopie.

## Skutki dla prac przed testem

- Instalator: ramki domyslnie wylaczone (bez ostrzezen o braku polaczenia); ikony "Stanowisko" i "Dzien skanera".
- Dokument `PIERWSZE_TESTY_NA_SPRZECIE.md` i arkusz zostana skrocone do tego wariantu po nowym oknie i instalatorze
  (zmienia sie teksty ekranu i kroki instalacji).
