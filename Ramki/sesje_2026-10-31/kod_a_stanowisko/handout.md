# Handout — KOD A: testy edge-case programu stanowiska

Status: **ZAKOŃCZONE** (31.10.2026)
Korekta 31.10: repo GitHub wycofane ze źródeł — sekcja bezpieczeństwa oparta wyłącznie na lokalnych plikach (plan wdrożenia v2, README, opisy modułów).

## Wynik w jednym zdaniu
Istniejące testy zielone (11), geometria płytek w 100 % spójna z `uklad.json`/`parametry.json`/`wyniki_v2`; własne testy edge-case **86 passed, 27 xfailed, 0 failed** — 27 xfail = 27 potwierdzonych znalezisk, z których 5 to **BŁĄD** (B1 przenikanie stożka przez losowe dx,dy; B1b rynienka bez ścianek; B2 `najblizsze_gniazdo`; B3 toml nieczytany; B4 etykieta w rzucie), reszta RYZYKO/UWAGA; bezpieczeństwo oceniane tylko wg planu wdrożenia v2 (w. 365/369). Szczegóły: `znaleziska.md`.

## Pliki
- `znaleziska.md` — 5 najważniejszych + tabele (uklad, synth, narzedzia, testy/dokumentacja, bezpieczeństwo P1–P5).
- `testy_edge/` — `conftest.py` + 4 pliki testów (113 testów). Uruchomienie z cwd `stanowisko/`:
  `set PYTHONUTF8=1` → `py -3.12 -m pytest ../sesje_2026-10-31/kod_a_stanowisko/testy_edge -q` (ok. 60 s; 20 s to celowy timeout testu S3).
  Każdy `xfail(strict=True)` ma w `reason` ID znaleziska; gdy ktoś naprawi kod, test zacznie **XPASS → FAILED**, co pokaże, że można zdjąć marker.
- `wyjscie/` — artefakty (135 MB, można skasować po lekturze): `geometria_stl.py/.txt` (kontrola STL vs JSON), `sondy1-3*.txt` (dowody B2, B1, przyczyna B1), `pytest_edge_wynik.txt`, `stl/` (13 atrap), `syntetyczne/` (skan n2 seed 1: 89,6 MB STL + JSON + PNG).

## Przeczytane
`stanowisko/README.md`, `opisy_modulow/*.md`, `uklad.py`, `synth.py`, `narzedzia/*.py`, `testy/*.py`, `ustawienia.toml`, `requirements.txt`, `.gitignore`, `modele_plytek/*/uklad.json`, `../parametry.json` (`plytka`), `../wyniki_v2/README.md`, `arkusze/kody_plytek.md`, `do_v3.md`, fragmenty planu wdrożenia v2 (w. 63–72, 149, 339–369 o danych).

## Przetestowane (chronologicznie)
1. `py -3.12 -m pytest testy -q`: 11 passed, 2,19 s.
2. Geometria STL (6 płytek) vs `uklad.json` vs `parametry.json`: zgodne; STL bajtowo = `wyniki_v2`.
3. CLI end-to-end do `wyjscie/`: atrapy → synth (`--drgniecie 0.5`) → rzut: 13 prac, 14 ubytków, 1,79 M trójkątów, 89,6 MB (opis modułu mówi 1–1,5 M / 60–75 MB → D1).
4. Sondy: toml nieczytany (B3); `najblizsze_gniazdo` (B2); osadzanie 30 seedów × wszystkie gniazda × 4 typy koron × 2 płytki → przenikanie do 0,73 mm, przyczyna = `luz_xy` po pętli (B1).
5. `testy_edge/`: 86 passed / 27 xfailed.
6. Bezpieczeństwo (wg planu wdrożenia v2 w. 365/369): nazwa pliku projektu w JSON prawdy obok skanu (P1, RYZYKO), przyszły log CSV z nazwą folderu wbrew w. 369 (P3, RYZYKO), ścieżki maszyny w toml w repo (P2, UWAGA — przenośność); PNG i stdout czyste (P4); `git ls-files` bez danych (P5).

## Nie zrobione / poza zakresem
- Nie modyfikowano żadnego pliku projektu ani `testy/` (`git status` czysty), nic nie pisano do `dane/` (atrapy w `dane/stl` są z 27.10, nie moje).
- Nie testowano na prawdziwych STL z exocad (brak w `dane/stl`) — heurystyka orientacji i konwencja nazw plików (P1) do sprawdzenia na 30 prawdziwych plikach, jak zapowiada `synth.md`.
- Test S11 (`.STL` na POSIX) jest `xfail` warunkowo — na Windows przechodzi, nie weryfikowany na Linuksie.

## Co dalej (propozycja dla właściciela)
1. Naprawić B1/B1b w `osadz_w_gniezdzie` (dx,dy przed pętlą + końcowa asercja) — bez tego metryki plate/match na danych syntetycznych są niewiarygodne na poziomie 0,05 mm.
2. `ustawienia.py` z `tomllib` i zdjąć duplikaty z `synth.py` (B3), zgodzić `pas_brzegu`/`srednica` z `[inspect]` (S1).
3. `najblizsze_gniazdo` po obrysie + `None` poza gniazdami (B2) przed pisaniem `plate`.
4. Decyzja o identyfikatorach projektów w prawdzie/logach (P1/P3) przed `catalog`/`excel`.
5. Po poprawkach: uruchomić `testy_edge` — testy XPASS wskażą, które markery `xfail` zdjąć; dobre kandydaty do przeniesienia do `testy/`: `test_osadzenie_*`, `test_scianki_3mm_*`, `test_transformacje_z_prawdy_*`, `test_determinizm_*`, `test_uklad_json_zgodny_z_parametry_json`.
