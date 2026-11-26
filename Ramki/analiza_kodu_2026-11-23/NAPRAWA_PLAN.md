# Plan naprawy znalezisk analizy kodu i wydania na dzien testu skanera (23.11.2026)

Zrodla: `S1_lancuch_analizy.md` (B 2 / P 6 / D 7), `S2_zawieszenia.md` (B 1 / P 8 / D 8), `S3_wynik_do_technika.md`
(B 1 / P 6 / D 13) w tym folderze. Termin: testy na sprzecie 28-29.11.2026.

## Decyzje wlasciciela 23.11.2026

1. W dniu testu jest TYLKO laptop wlasciciela i skaner; elektroniki ramki nie ma. Testujemy wszystko, co sie da
   bez ramki - zakres: `../etap3/testy_sprzet_2026-11-28/WARIANT_LAPTOP_I_SKANER.md`. Instalator: ramki domyslnie
   wylaczone.
2. Do wydania na dzien testu wchodza: nowy instalator + 3 bezpieczne naprawy (N1, N2, N3 nizej).
3. Ponowny skan: praca czerwona bez decyzji ZOSTAJE czerwona takze po nowym skanie, do decyzji technika.
4. Stare skany przy starcie: wlasciciel nie odpowiedzial - przyjete domyslnie (do odwolania): program pyta przy
   starcie "W folderze lezy N wczesniejszych skanow: Przelicz je / Pomin"; swieze skany ida od razu.
5. PRZED pozostalymi pracami: okno programu budowane od nowa (`../etap3/nowy_interfejs/SPEC.md`), kolory
   `#338CED`, `#191919`, `#303030`.
6. Instalator: bez terminala i skryptow - okno z wyborem folderow i osob, Python w paczce, ikony na pulpicie.

## Paczki przed dniem testu (w tej kolejnosci)

| Kod | Co | Znaleziska | Pliki (rozlaczne miedzy paczkami biegnacymi naraz) |
|---|---|---|---|
| U1 | nowe okno: wieczor, poranek, panel Excela | S3-3, S3-4, S3-14, S3-15, S3-16 | `stanowisko/ui/**`, testy okna, RGB w `statusy.py` |
| N1 | zielone tylko po kontroli | S1-04 = S3-5, S1-05, S1-06, S1-08, S1-11, S3-9, S1-12 | `porownaj.py`, `inspect.py` (status poczatkowy, brak linii), `match.py` (ostrzezenie orientacji), `statusy.py` (logika), testy |
| N2 | ponowny skan nie zakrywa czerwonego | S3-1 | `session.py`, `kontroler_api.py` (pytanie), teksty w `statusy.py` |
| N3 | stare skany nie blokuja startu | S2-01 | `scanner.py`, `aplikacja.py`, `kontroler_api.py` (pytanie przy starcie) |
| U2 | okno "Dzien skanera" i okno ustawien folderow w nowym motywie | - | `dzien_skanera.py`, nowe `ui/ustawienia_okno.py` |
| I1 | instalator okienkowy | decyzja 6 | `instalacja/**`, `narzedzia/zbuduj_wydanie.py`, instrukcja instalacji |
| W1 | wydanie 0.4.0, testy T0 / T1 / T12 na paczce, proba na laptopie wlasciciela | - | `WERSJA`, `etap3/wydania/` |

Zasady N1: tylko w strone "wiecej zoltego", progi wykrywania bez zmian. Dopasowanie zolte + inspekcja ok = zolte
"sprawdz - projekt niepewny". Brak inspekcji / status nieznany = "nie sprawdzono". Projekt bez linii brzegu
i niepewna orientacja projektu = "nie sprawdzono" (do odpowiedzi na pytanie o inlay / onlay nizej).
N2 i N3 dotykaja `kontroler_api.py` - ida po sobie, nie naraz. N1 moze biec rownolegle z U1.
Kazda paczka: testy przed kodem, recenzja, pelny pytest (ok. 25 min) - razem ok. 7 przebiegow.

## Po testach na sprzecie (potrzebne prawdziwe skany, pomiary albo decyzje)

- S1-01 (ubytek bez powierzchni przelomu w skanie = zielone), S1-02 (plama "lagodna" odrzucana po cichu),
  S1-03 (gestosc siatki skanu), Z1 / T2 (e) "pozycja 8" (srodek czy zasieg plamy), S1-07 (mosty), S1-09.
  Najpierw trzy liczby z pierwszego skanu pracy z odpryskiem: odstep wierzcholkow siatki, czy sa wierzcholki na
  przelomie, `pierscien_mediana_mm` plamy. Potem kampania pomiarowa tylko na ukladach okraglych.
- S2-02, S2-03 (zdarzenia skanera i zapis wyniku przy zajetej bazie), S2-04 (limity 600 s / 180 s), S2-05, S2-06,
  S2-07 (pula bez limitu czasu / w zadaniu pierwszej plytki), S2-16 ("Zamknij piec" zablokowane).
- S2-08 = S3-2 (Excel przez COM w watku okna), S3-6 (rano: progi klasy "pewna"), S3-7 (zielony pierscien ramki -
  decyzja), S3-8, S3-10 - S3-13, S3-17 - S3-19, pozostale D, rozjazdy opis - kod, S1-14 (testy a lokalny
  `ustawienia.toml`).

## Co odczytac 28-29.11 (z raportow, kolumna "na sprzecie")

Siatka skanu w miejscu odprysku; plamy `lagodna` / `poza_pasem` w `_wynik.json`; `stan_linii` wszystkich prac
(dla koron ma byc 0 x "brak"); pary `status` / `status_gniazda`; ta sama praca z ubytkiem zeskanowana dwa razy;
czas pierwszej plytki po starcie; 2-3 mm brzegu zaklejone tasma - czy wychodzi "nie sprawdzono".

## Pytania czekajace na wlasciciela

- P1-P9 przed dniem sprzetu, termin SRODA 25.11: `../etap3/testy_sprzet_2026-11-28/PYTANIA_DO_WLASCICIELA.md`
  (najpilniejsze P3 - czy na Raspberry Pi jest program ramki; P1, P6, P8, P9). P4 i P5 - odpowiedz z 23.11:
  osobny laptop.
- S1: czy pracownia frezuje prace bez wneki (inlay, onlay, licowka) albo dostaje projekty spoza exocad (N1);
  czy praca o skali rozniacej sie o 0,3-1 % ma zostac zielona z sama uwaga.
- S2: ile plikow STL lezy w folderze skanera; pula z folderu czy z wpisow, ile plikow w "Cyrkon", czy OneDrive
  trzyma je na dysku; czy cos poza programem otwiera plik bazy.
- S3: czy zielony pierscien ramki w stanie "wynik" zostaje przy czerwonych gniazdach; czujniki numeru w ramce
  okraglej (magnesy na promieniu 45 mm).
- `00_NADZOR_STAN.md`, "Lista decyzji wlasciciela" 1-20 po zleceniu 2 (m.in. T2 (e), ramka wieczorna a plytki
  o tym samym numerze).
