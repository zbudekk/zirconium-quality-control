# Pierwsze testy na prawdziwym sprzecie 28-29.11.2026 (paczki E3-S1 i E3-S2)

- `PIERWSZE_TESTY_NA_SPRZECIE.md` - dokument dla wlasciciela, do wydruku: pytania z terminem,
  co zabrac, kroki (komputer, skaner, ramka, laptop), co przywiezc i gdzie polozyc.
- `PYTANIA_DO_WLASCICIELA.md` - jedna strona: pytania P1-P9 z terminem 25.11.2026, "od czego zalezy"
  i miejscem na odpowiedz; idzie do wlasciciela PRZED reszta dokumentu.
- `ARKUSZ_OBSERWACJI.md` - arkusz do wydruku i wypelniania dlugopisem; numery jak kroki dokumentu.
- `ZALACZNIKI.md` - dla ciekawych i dla wykonawcy: stan sprawdzenia, program ramki na Raspberry Pi
  w skrocie, nazwy wewnetrzne.
- `narzedzia/` - `pole_skanu.cmd` + `pole_skanu.py` (pole skanera, dolki numeru, brzeg, scianka
  plytki z jednego pliku skanu), `ramka.cmd` + `ramka_proba.py` (proba ramki, takze z kluczem),
  `dzien_skanera.cmd` (tylko awaryjnie dla 0.3.1), testy `test_*.py`. `klucz_ramki.txt` powstaje
  przy pracy i nie idzie do gita.
- Testy narzedzi, z katalogu `Ramki\stanowisko`:
  `python -m pytest ..\etap3\testy_sprzet_2026-11-28\narzedzia -q -p no:cacheprovider`
- Narzedzia korzystaja z programu tylko przez import; programu nie zmieniaja.
- Stan (21.11.2026, etap S2b-3): dokument przeszedl krok po kroku na instalacji z paczki probnej (kod
  wersji 0.3.3 przed ostatnia runda recenzji; etap S2b-2); nazwa i rozmiar paczki, liczby instalatora
  i teksty komunikatow potwierdzone na wydaniu 0.3.3 (`Stanowisko_0.3.3.zip`, 447 318 667 bajtow; teksty
  odczytane z programu zainstalowanego). Znacznikow "do potwierdzenia na 0.3.3" nie ma (0); zostaja
  znaczniki `[NIE SPRAWDZONE BEZ SPRZETU]`. Dowody: raport `Ramki/stanowisko/raporty/E3-S2_2026-11-21.md`,
  sekcja "S2b-3". Etap S2b-4 (21.11): odpowiedz wlasciciela z 19:30 ("Obie kwadratowe oraz jedna okragla";
  plytka okragla = testowa R54 nr 8) w P1 / P2 i warianty krokow bez plytek okraglych ramkowych; sekcja "S2b-4".
- Strony do druku (PDF / HTML) powstaja poza repo skryptem `koordynator\robocze\s2\b3\druk.py`; do gita
  nie ida.
