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
- Stan: tresc pisana na paczke 0.3.3; krok 3.8 przeszedl na atrapach na kodzie wszystkich paczek (S2b-1).
  Miejsca `[DO POTWIERDZENIA NA 0.3.3]` potwierdza etap S2b-2 na instalacji z paczki
  (raport `Ramki/stanowisko/raporty/E3-S2_2026-11-21.md`).
