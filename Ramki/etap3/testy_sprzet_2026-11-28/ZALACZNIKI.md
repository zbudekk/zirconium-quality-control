# Zalaczniki do dokumentu "Pierwsze testy na prawdziwym sprzecie" (28-29.11.2026)

Dla ciekawych i dla wykonawcy etapu S2b. Wlasciciel przy sprzecie tego pliku NIE potrzebuje - wystarcza
`PIERWSZE_TESTY_NA_SPRZECIE.md` i `ARKUSZ_OBSERWACJI.md`. Stan: 21.11.2026.

## A. Program ramki na Raspberry Pi - najkrotsza droga

Pelna instrukcja (12 krokow, z arkuszem): `C:\Stanowisko\wersje\<wersja>\program\instrukcje\ramka_raspberry_pi.md`
[DO POTWIERDZENIA NA 0.3.3]. Calosc: [NIE SPRAWDZONE BEZ SPRZETU] - zaden krok nie byl wykonany na prawdziwym
Raspberry Pi. Potrzebny internet i kilka godzin. Karty SD zastanej w ramce nie nadpisuj (uzyj drugiej karty).

1. Karta SD z systemem (krok 1 instrukcji), nazwa urzadzenia `ramka-w` albo `ramka-p`, siec Wi-Fi pracowni.
2. Pierwsze wlaczenie i polaczenie z laptopa (krok 2); ustawienia startowe i pakiety systemu (kroki 3-4).
3. Biblioteka matrycy diod (krok 5) - najdluzszy krok, wymaga internetu.
4. Kopia katalogu `program\ramka` na ramke (krok 6) i instalacja skryptem `zainstaluj_ramke.sh` z katalogu
   `ramka\rpi` (krok 7). Skrypt zaklada plik `/etc/ramka/ramka.json` z LOSOWYM KLUCZEM.
5. Odczyt klucza na ramce: `sudo grep klucz /etc/ramka/ramka.json` - przepisz go na kartke (pytanie P8).
   Druga ramka musi dostac TEN SAM klucz (program ma jedno pole klucza dla obu ramek).
6. Pierwsze uruchomienie reczne i kontrola skryptem `sprawdz_ramke.sh` (kroki 8-9): wiersze OK / BRAK.
7. Test diod wedlug gniazd plytki (krok 10) i autostart po wlaczeniu pradu (krok 11).
8. Klucz i adres ramki wpisuje sie w `C:\Stanowisko\ustawienia.toml`, sekcja `[ramki]` (krok 3.8 dokumentu).

## B. Nazwy uzywane przez program (w dokumencie: "rodzaj plytki")

| W dokumencie | Nazwa w programie i w plikach wynikow | Numery |
|---|---|---|
| plytka kwadratowa wieczorna / poranna | `wieczorna` / `poranna` | 1-3 / 4-6 |
| plytka okragla ramkowa (do ramki) | `okragla_ramkowa_wieczorna` / `okragla_ramkowa_poranna` | 1-3 / 4-6 |
| plytka okragla testowa (poza ramka) | `okragla_wieczorna` / `okragla_poranna` | 8 / 9 |
| stara plytka R54 | `wieczorna_r54` / `poranna_r54` | - |

Okno programu nie wypisuje nazwy rodzaju plytki - plytke opisuje numer ("Plytka 1" ... "Plytka 9") i rysunek
mapy (kwadrat z wycietym naroznikiem albo kolo ze scieciem). Nazwy widac w `pole_skanu` (wiersz 1), w menu
`ramka.cmd` (pozycje 4 i 5) i w plikach wynikow.

Granice rozpoznania (opis: `Ramki/stanowisko/opisy_modulow/plate.md`; propozycja zmiany:
`Ramki/etap3/propozycja_wariant_C_regula_ksztaltu_2026-11-21.md`): plytka okragla bez czytelnych dolkow numeru
i bez scianki bocznej w skanie = "kwadratowa, pewnie". Pole skanera 90 mm i mniej = zadna plytka nie jest
rozpoznana. Krok 2.5a dokumentu mierzy, jak czesto to sie zdarza na prawdziwym skanerze.

## C. Pelne teksty komunikatow programu (wg raportu paczki O2) [DO POTWIERDZENIA NA 0.3.3]

Zolty panel nad mapa, przycisk "Zamknij". We wszystkich trzech sytuacjach ramka jest ciemna, skan zostaje.

- (a) "Plytka lezy na zlej ramce": "Na ramce wieczornej lezy plytka nr 5, a ta ramka podswietla tylko plytki
  1, 2, 3 - ramka nie swieci. To numer plytki porannej - poloz ja na ramce porannej. Jesli to jednak plytka
  wieczorna, sprawdz, czy lezy rowno w ramce, i poloz ja jeszcze raz."
- (b) "Na ramce lezy inna plytka niz zeskanowana": "Na ramce wieczornej lezy plytka nr 2, a ostatni skan to
  plytka nr 1 - ramka nie swieci. Poloz na ramce plytke nr 1. Jesli na ramce lezy wlasciwa plytka, to numer
  skanu jest zly - popraw go przyciskiem "Zmien numer" przy tej plytce na ekranie." Rano tytul brzmi "Na ramce
  lezy plytka, ktorej nie ma w planie pieca".
- (c) "Plytka N: Numer plytki nie zgadza sie ze skanem": "Podany numer plytki to 2, a program odczytal ze
  skanu numer 1. Ramka nie podswietla tej plytki; skan i wynik zostaja. Sprawdz numer wybity na plytce: jesli
  podany numer jest zly - popraw go przyciskiem "Zmien numer"; jesli jest dobry - pracuj wedlug ekranu."
- Blad analizy, tytul "Analiza skanu nie powiodla sie": "Program nie przeanalizowal tego skanu (w skanie widac
  1 z 3 znacznikow plytki - plytka nie miesci sie w polu skanera albo lezy poza srodkiem; ustaw plytke na
  srodku i sprawdz, czy pole skanowania obejmuje cala plytke). Zeskanuj plytke ponownie." Inne nawiasy:
  "(w skanie nie widac plaskiego wierzchu plytki - to nie jest skan calej plytki; poloz plytke plasko na
  srodku skanera)", "(skan jest prawie pusty - sprawdz, czy plytka lezy w skanerze)".
- Pierwszy start po aktualizacji: w podpowiedzi paska "Ramki" ostrzezenie o dopisaniu plytek okraglych
  ramkowych do pliku kalibracji ramek (polozenia diod startowe, z rysunku plytek).

## D. Narzedzia dnia sprzetu - co wypisuja

`pole_skanu.cmd` (przeciagnij plik skanu): 6 wierszy - 1 co mowi program (rodzaj plytki, pewnie / niepewnie,
numer i skad), 2 wymiary danych i pole skanera, 3 brzeg plytki (w ilu z 72 kierunkow), 4 dolki numeru, 5 stozki
znacznikow, 6 scianka boczna i rowek pokrywki - oraz blok "DO ARKUSZA (przepisz):" z wierszami `program mowi:`,
`numer z dolkow:`, `dolki numeru widac:`, `scianka boczna:`, `rowek pokrywki:`, `brzeg plytki:`, `pole:`,
`podloze w skanie:`. Wyniki: `C:\Sprzet_testy\wyniki\pole_skanu\<skan>_<data>_<godzina>_pole.txt / .json / .png`.

`ramka.cmd`: pozycje 1 (czy ramka odpowiada), 2 (test diod), 3 (odczyt numeru plytek, 5 minut), 4 i 5 (gniazda),
6 (klawiatura ramki porannej), 7 (klucz ramki), 0 (koniec). Klucz: opcja `--klucz`, zmienna `RAMKA_KLUCZ`, plik
`narzedzia\klucz_ramki.txt` (zapisuje go pozycja 7) albo wiersz `klucz` w `[ramki]` pliku ustawien programu.

`narzedzia\dzien_skanera.cmd`: tylko awaryjnie, gdy w `C:\Stanowisko` nie ma `Dzien_skanera.cmd` (stara paczka
0.3.1).

Proba okna "Dzien skanera" dzien wczesniej, bez klikania [DO POTWIERDZENIA NA 0.3.3]:
`C:\Stanowisko\Dzien_skanera.cmd --nowa --zamknij-po 5` - ma wypisac wiersz `DZIEN SKANERA: sesja
C:\Stanowisko\dane\dzien_skanera\...; ustawienia C:\Stanowisko\ustawienia.toml; foldery obserwowane: ...`.
Pomiar szczegolowy jednego skanu [DO POTWIERDZENIA NA 0.3.3]:
`C:\Stanowisko\Polecenie.cmd narzedzia\pomiar_skanu\pomiar_skanu.py <skan.stl>`.

## E. Stan sprawdzenia (21.11.2026; liczby i polecenia: raport `Ramki/stanowisko/raporty/E3-S2_2026-11-21.md`)

- Na paczce 0.3.1 i danych sztucznych (etap S1, raport `E3-S1_2026-11-21.md`): instalacja w swiezym katalogu,
  samokontrola, okno "Dzien skanera", oceny skanow, ramka udawana przez program.
- Na kodzie po paczce O1 (21.11): narzedzia `pole_skanu` i `ramka` - 51 testow; plytka okragla bez scianki
  i bez czytelnych dolkow: 4 z 4 skanow sztucznych "kwadratowa, pewnie"; pole 95 mm - plytka rozpoznana,
  pole 90 mm - nierozpoznana (2 z 2).
- Na kodzie galezi O2 i O4 (przed ich scaleniem): narzedzie `ramka` z kluczem - zly klucz odrzucony, dobry
  przyjety; ramka zna plytki okragle ramkowe (19 z 19 i 24 z 24 gniazd na ramce udawanej przez program).
- Nie sprawdzone nigdzie: wszystko z listy zbiorczej dokumentu oraz kazde miejsce [DO POTWIERDZENIA NA 0.3.3]
  (paczka 0.3.3 jeszcze nie istnieje) - lista z poleceniami sprawdzenia jest w raporcie, sekcja "S2b".
- Sprawa 4 laptopa (czy zapis na dysk zatrzymuje okno) - nie na ten weekend; wymaga plikow testowych spoza
  paczki.
