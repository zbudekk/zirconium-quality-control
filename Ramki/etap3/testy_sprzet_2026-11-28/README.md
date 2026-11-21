# Pierwsze testy na prawdziwym sprzecie 28-29.11.2026 (paczka E3-S1, szkic - etap 1)

- `PIERWSZE_TESTY_NA_SPRZECIE.md` - dokument dla wlasciciela: pytania na poczatku, lista rzeczy do zabrania,
  kroki (komputer, skaner, ramka, laptop), co przywiezc i gdzie polozyc, lista rzeczy niesprawdzonych.
- `ARKUSZ_OBSERWACJI.md` - arkusz do wydruku i wypelniania dlugopisem; numery krokow jak w dokumencie.
- `narzedzia/pole_skanu.py` (+ `pole_skanu.cmd`) - srednica pola skanera, dolki numeru, brzeg i scianka plytki
  z jednego pliku skanu; `narzedzia/ramka_proba.py` (+ `ramka.cmd`) - proba ramki z komputera: stan, odczyt
  plytek, test diod, gniazda, klawiatura; `narzedzia/dzien_skanera.cmd` - okno "Dzien skanera" z instalacji.
- Testy narzedzi (skany sztuczne, atrapa ramki), z katalogu `Ramki/stanowisko`:
  `python -m pytest ../etap3/testy_sprzet_2026-11-28/narzedzia -q -p no:cacheprovider` (26 testow).
- Narzedzia korzystaja z programu tylko przez import; programu, testow programu ani instrukcji nie zmieniaja.
- Stan sprawdzenia, liczby, lista POTRZEBUJE i luki: `Ramki/stanowisko/raporty/E3-S1_2026-11-21.md`.
- Znaczniki w dokumencie: `[NIE SPRAWDZONE BEZ SPRZETU]`, `[ETAP 2: ...]` (do domkniecia po nowym wydaniu).
