# scanner - obserwacja folderu eksportu skanera (paczka E3-A2, 17.11.2026)

**Co robi.** Patrzy na folder, do ktorego program skanera zapisuje pliki, i dla kazdego nowego pliku STL zglasza
zdarzenie "nowy skan" - dopiero po koncu zapisu i po sprawdzeniu pliku. Plik zly nie daje zdarzenia, tylko wpis
z powodem. Pliki: `stanowisko/scanner.py`, symulator do prob bez skanera `narzedzia/symulator_skanera.py`,
testy `testy/test_scanner.py`. Modul nie laduje numpy, trimesh, Open3D ani Qt (dziala w procesie okna, w zwyklym watku).

**Wejscie.** Folder (docelowo `[sciezki] folder_eksportu_skanera`) i parametry konstruktora `Scanner(...)`:

| Parametr | Domyslnie | Znaczenie |
|---|---|---|
| `wzorzec_pliku` | `*.stl` | wzorzec NAZWY pliku (bez rozrozniania wielkosci liter); inne pliki = wpis `poza_wzorcem` |
| `rekurencyjnie` | tak | czy patrzec w podfoldery (struktury folderu zlecenia nie zakladamy) |
| `stabilizacja_ms` | 300 | tyle bez zmiany rozmiaru i czasu pliku, zanim plik jest oceniany |
| `min_trojkatow` | 1 | mniej trojkatow = wpis `za_malo_trojkatow` |
| `min_rozmiar_mb` | 0 (bez progu) | mniejszy plik = wpis `za_maly` |
| `odrzuc_po_s` | 5 | plik zly i niezmieniany przez tyle sekund = wpis z powodem |
| `okres_s`, `przeglad_s` | 0,05 i 2 | co ile watek oglada pliki, na ktore czeka; co ile przeglada caly folder |
| `zglos_zastane` | nie | czy pliki obecne przy starcie sa nowymi skanami |
| `obserwator` | `watchdog` | `odpytywanie` = bez biblioteki watchdog (np. dysk sieciowy), sam przeglad co `przeglad_s` |
| `start_skanu` | atrapa | funkcja akcji "start skanu" (patrz nizej) |

Podpiecie do `ustawienia.toml` robi paczka A3 (proponowane klucze `[scanner]`: `stabilizacja_ms`, `min_rozmiar_mb`,
`min_trojkatow`, `wzorzec_pliku`).

**Wyjscie.** `ZdarzenieSkanu` (kontrakt z planu etapu 3, sekcja 3.8): `plik`, `sha16` (16 znakow SHA-256 zawartosci),
`rozmiar`, `trojkaty`, `czas_pliku` (+ `mtime_ns`), `czas_zdarzenia`, `nr` (kolejny numer), `ponowny` (ta sama sciezka
byla juz zgloszona), `duplikat` i `duplikat_z` (ta sama zawartosc byla juz zgloszona pod inna nazwa - wskazanie
pierwszego pliku). `Odrzucenie`: `plik`, `powod`, `opis`, `rozmiar`, `czas`. Oba trafiaja do funkcji `na_skan` /
`na_odrzucenie` (wolanych w watku obserwatora) albo, gdy ich nie podano, do kolejki `Scanner.zdarzenia`; odrzucenia sa
tez w `Scanner.odrzucone` (ostatnie 1000) i w logu `stanowisko.scanner` (same nazwy plikow, bez sciezek).

| Powod odrzucenia | Kiedy |
|---|---|
| `pusty` | 0 bajtow |
| `za_krotki` | mniej niz 84 bajty (naglowek binarnego STL) |
| `rozmiar_niezgodny` | rozmiar inny niz 84 + 50 x liczba trojkatow z naglowka: plik uciety, uszkodzony albo nie-STL |
| `stl_tekstowy` | STL tekstowy (zaczyna sie od `solid`, sam tekst) - program przyjmuje tylko binarny |
| `za_malo_trojkatow`, `za_maly` | ponizej progow z konstruktora |
| `poza_wzorcem` | nazwa nie pasuje do wzorca (jeden wpis na plik) |
| `blad_odczytu` | pliku nie dalo sie odczytac w 40 kolejnych probach |

**Jak dziala.** Biblioteka `watchdog` powiadamia o zmianach w folderze; niezaleznie co `przeglad_s` caly folder jest
przegladany (zgubione powiadomienia, folder, ktory pojawil sie pozniej, watchdog, ktory nie wystartowal). Kazdy plik,
ktory sie zmienil, jest "kandydatem". Koniec zapisu = wszystkie warunki naraz: (1) rozmiar i czas pliku bez zmian przez
`stabilizacja_ms`; (2) rozmiar zgodny z naglowkiem; (3) zaden program nie trzyma pliku otwartego do zapisu (Windows);
(4) po policzeniu skrotu rozmiar i czas nadal te same. Plik stabilny, ale zly, czeka `odrzuc_po_s` (moze byc dopisywany
z przerwami) i dopiero wtedy dostaje wpis; odrzucenie nie jest ostateczne - po zmianie pliku ocena zaczyna sie od nowa.
Kilka plikow gotowych w tym samym obiegu jest zglaszanych w kolejnosci czasu zapisu. Plik zapisany ponownie pod ta sama
nazwa (nowy czas albo rozmiar) daje nowe zdarzenie z `ponowny`; plik usuniety i zapisany znowu - takze.

Uzyte ponownie z okna "Dzien skanera" (`dzien_skanera_rdzen`, bez zmian w tamtym pliku): `ktos_pisze` (warunek 3),
`otworz_zrodlo` (odczyt z pelnym wspoldzieleniem: nie blokuje zapisu, zmiany nazwy ani usuniecia przez program
skanera), `pliki_w_folderze` (przeglad). Nie uzyto `Zbieracz`: odpytuje co 1,5 s i potrzebuje 2 zgodnych odczytow
(opoznienie 1,5-3 s wobec wymagania "ponizej 1 s"), kopiuje pliki do folderu sesji i przepuszcza pliki niepelne po 30 s -
to inne zadanie (zebrac wszystko) niz tutaj (zglosic tylko dobry skan, szybko).

**Akcja "start skanu" (decyzja DW5).** `Scanner.start_skanu()` wywoluje funkcje podana w konstruktorze i zwraca
True / False (wyjatek akcji = False). Domyslnie `AtrapaStartuSkanu`: niczego nie klika, zapisuje czasy wywolan.
Prawdziwa akcja (aktywuj okno programu skanera i nacisnij Spacje) powstanie po probach na skanerze (paczka B2).

**Symulator.** `py -3.12 narzedzia/symulator_skanera.py --folder F [--zrodla ...] [--ile N] [--czas 1 5] [--zle uciety
pusty ...] [--pomiar] [--analiza --projekty P]` - zapisuje pliki w kawalkach z przerwami, kilka naraz, dorzuca pliki
zle; z `--pomiar` liczy zdarzenia i opoznienia, z `--analiza` przepuszcza skany przez silnik. Opis w naglowku pliku.

**Pomiary (PC wlasciciela, 17.11.2026).** Liczby i obciazenie komputera w chwili pomiaru: `raporty/E3-A2_2026-11-17.md`.

**Zalozenia i granice.**
- Nazw, struktury folderow ani sposobu zapisu prawdziwego skanera nie znamy (plan etapu 3, S5): wszystko jest
  parametrem; symulator pokazuje trzy sposoby zapisu (plik otwarty caly czas, zamykany po kazdym kawalku, plik
  tymczasowy ze zmiana nazwy), ale to nie jest opis skanera. Sprawdzenie na skanerze: paczka B2.
- Tylko binarny STL. STL tekstowy, PLY, OBJ = wpis z powodem, bez zdarzenia. Jesli skaner eksportuje inaczej - B2.
- Zdarzenie przed koncem zapisu jest wykluczone, gdy program skanera pisze naglowek z ostateczna liczba trojkatow albo
  trzyma plik otwarty do zapisu. Program, ktory od razu rezerwuje pelny rozmiar pliku, zamyka go i dopisuje dane
  pozniej, nie zostalby rozpoznany na Windows inaczej niz po `stabilizacja_ms` (poza Windows `ktos_pisze` zawsze
  zwraca False i decyduje sama stabilizacja oraz naglowek).
- `ktos_pisze` otwiera plik na chwile bez zgody na zapis innych programow; jest wolane dopiero dla pliku stabilnego
  i (dla plikow dobrych) zgodnego z naglowkiem, wiec okno kolizji z programem skanera to pojedyncze wywolania.
- Ponowny zapis, ktory zachowuje rozmiar i czas pliku co do 100 ns (kopia z zachowaniem czasu na ten sam plik bez
  usuwania), nie jest zauwazany - zawartosc jest wtedy w praktyce ta sama.
- Pamiec duplikatow (`sha16` -> pierwszy plik) i numeracja zdarzen zyja tyle, co obiekt `Scanner`; trwala historia
  skanow to zadanie sesji i bazy (A1, A3).
- Folder niedostepny przy starcie albo znikajacy w trakcie nie jest bledem: obserwator czeka i wraca do pracy
  (`stan()["folder_dostepny"]`).
- Funkcje zwrotne sa wolane w watku obserwatora; okno Qt powinno w nich tylko emitowac sygnal albo wkladac do kolejki.
