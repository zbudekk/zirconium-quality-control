# Handout — KOD B: testy edge-case generatora i skryptów sprawdzających

Status: **ZAKOŃCZONE** (31.10.2026, ~01:30)

**Korekta 31.10: repo GitHub wycofane ze źródeł; źródła wyłącznie lokalne.** (Polecenie koordynatora/właściciela; wcześniejsza wzmianka o repozytorium w `znaleziska.md` usunięta. Żaden wniosek audytu nie opierał się na tym repozytorium — wszystkie znaleziska pochodzą z plików w `<PC>\Desktop\Ramki` i przebiegów w scratchpadzie.)

## Wynik w jednym akapicie
70 znalezisk (12 BŁĄD / 27 RYZYKO / 31 UWAGA) w `znaleziska.md` (TOP 5 na górze, osobna sekcja „Co się stanie po wpisaniu pomiarów i przebiegu ALL”). Najważniejsze: (1) README każe po pomiarach przeliczyć LICZONE → ALL generuje korpus inny niż zamówiony (plan §10 mówi „zamrożone”), a bez tego ALL się zatrzymuje; (2) bramka G4b (`trzecie_oko`) nigdy nie została policzona na ostatecznej tulejce 11,85 — zapisany raport jest sprzed R52; (3) pusta/uszkodzona siatka wywala generator i skrypty recenzji bez raportu, po skasowaniu `wyniki_v2/stl`; (4) `pi_clearance_top` bez minimum (zerowy luz złącza–Bonnet przechodzi B = 0), luzy bez znaku w `trzecie_oko`; (5) 25 martwych kluczy, gniazda z JSON zamiast z parametrów, skrypt PDF nie czyta `parametry.json`. Nic w projekcie nie zmieniono.

## Zakres (z polecenia nadzoru)
`ramka_generator.py`, `recenzja/sprawdz_*.py`, `recenzja_koncowa/trzecie_oko.py`, `narzedzia/buduj_plan_wdrozenia.py`, spójność `parametry.json` ↔ kod. Nie dotykać `stanowisko/`, `wyniki_v2/`, Google Drive. Pisać tylko do `sesje_2026-10-31/kod_b_generator/`.

## Przeczytane (kamień 1 — gotowe)
- `00_NADZOR_STAN.md` (cały), `protokol_weryfikacji_v2.md` (cały, K‑01…K‑60),
  `plan_ramki_v2.md` sekcje 3 (nagłówek + 3.6), 10 (formularz pomiarów), 12 (przekazanie),
  `prompt_wykonawca.md`, `wyniki_v2/raport/notatki_wykonawcy.md` (cały, §1–11), `wyniki_v2/do_v3.md`,
  `recenzja_koncowa/tabele_auto.md` (nagłówki tabel A–F + lista unikalnych par pasowań).
- Handout sesji siostrzanej KOD A (stanowisko) — tylko do orientacji; nie wchodzę do `stanowisko/`.

## Środowisko
- Blender 5.2.3 LTS: `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` (jest!).
- Python Blendera: `...\Blender 5.2\5.2\python\bin\python.exe` (3.13, numpy 2.3.4) — używany do testów funkcji czystych z atrapą `bpy`.
- Systemowego `python` brak (stub Microsoft Store). Konsola cp1250 → `PYTHONUTF8=1`.
- `parametry.json`: 8 sekcji, 278 kluczy‑liści (191 ZALOZENIE, 53 SPEC, 20 DO_ZMIERZENIA, 9 LICZONE) + `_meta`.

## Kamień 2 — audyt kluczy parametry.json ↔ kod (GOTOWE)
- `WYMAGANE_KLUCZE` (273) = klucze JSON (273): 0 brakujących, 0 nadmiarowych, 0 literówek (skrypt: `testy_edge/test_walidator.py`, sekcja „audyt kluczy” w `znaleziska.md`).
- 25 kluczy JSON **nigdy nie czytanych** przez kod (martwe): `ev_socket_d_l/m/s`, `mo_socket_d_l/m/s`, `ev_trough_l/w`, `mo_trough_l/w`, `panel_hole_threaded` (DO_ZMIERZENIA!), `usb_hole_pitch` (DO_ZMIERZENIA!), `usb_hole_d`, `pi_hole_d`, `panel_screw_hole_d`, `blat_rib`, `cover_snap_count`, `dc_pocket_corner_r`, `fillet_inner_default`, `fillet_outer_default`, `insert_depth_m3`; a `panel_led_h`, `led_gap`, `max_work_height`, `panel_standoff_l` tylko w polach `wzor` LICZONE.
- Gniazda płytek: geometria bierze `uklad['sockets']` z `wyniki_v2/json/` (nie z `ev_rows`/`socket_depth`); JSON gniazd nie jest regenerowany, gdy istnieje.
- Walidator (28 przypadków, Blender): przepuszcza wartości ujemne, zero, NaN, Infinity, string, bool, null, zdublowany klucz w sekcji, nieznany status; `pi_stack_h` ZMIERZONE bez korekty → `BladProjektu` (ALL się zatrzymuje); wzór LICZONE w `eval` z dostępem do `__subclasses__`.

## Kamień 3 — generator (GOTOWE)
- Kopia generatora + plan + JSON w scratchpadzie `…\scratchpad\gen\`; 15 wariantów `parametry.json` (`testy_edge/warianty.py`) przez `testy_edge/uruchom_geometria.sh` → `…\scratchpad\rob\out_<wariant>\`, logi `rob\logi\przebiegi.txt`. Wszystkie wykonane (20–25 s każdy).
- `--etap A --out "…\wyjście_ż (test)"`: działa (kod 0, B 0).
- `--etap SPRAWDZ` (`testy_edge/test_sprawdz.sh`, 6 scenariuszy): nietknięta kopia OK (pliki poza `raport/` bez zmian); brak STL / brak JSON → czytelny `BladProjektu`; **obcięty STL → traceback `ValueError`**; podmiana płytki n1↔n2 → K‑11 B + K‑58 P (wykryte); skala ×1000 → K‑02/K‑04b NIE (wykryte).
- K‑59: `base`/`base2` vs `wyniki_v2/stl`: 16/17 bajtowo identyczne; wkładka różni się 6 bajtami (znak zera w normalnych), kanonicznie identyczna.
- Najważniejsze: README krok 2 vs plan §10 (odmrożenie korpusu), pusta siatka → wyjątek bez raportu po skasowaniu wyników, walidator bez zakresów, `pi_clearance_top` bez minimum, parametry gniazd ignorowane przy istniejącym JSON, tautologiczne oczekiwania K‑54/K‑02/arkusz. Szczegóły: `znaleziska.md` (G‑01…G‑22 + sekcja „Co się stanie po ALL”).

## Kamień 5 — `buduj_plan_wdrozenia.py` (GOTOWE, subagent)
- `draft_buduj_plan.md`: 22 znaleziska (6 BŁĄD / 6 RYZYKO / 10 UWAGA), PDF‑y odbudowane do scratchpada bajtowo = wydane 27.10; skrypt **nie czyta `parametry.json`** (~30 liczb na sztywno, dziś zgodne). Skondensowane w `znaleziska.md` sekcja P; testy `testy_edge/buduj_plan/`.

## Kamień 4 — `sprawdz_*.py` + `trzecie_oko.py` (GOTOWE, subagent)
- `draft_skrypty_sprawdzajace.md`: 26 znalezisk (4 BŁĄD / 11 RYZYKO / 11 UWAGA), tabela pokrycia par z `tabele_auto.md`, przebiegi na lustrze w scratchpadzie (`trzecie_oko.py` z podmienionym ROOT — nic w `recenzja_koncowa/` nie nadpisano). Skondensowane w `znaleziska.md` sekcja S; testy `testy_edge/sprawdzacze/`.
- Gotowy, nieużyty artefakt: `…\scratchpad\audyt_sprawdzacze\wyjscia\tabele_auto.md` = tabele trzeciego oka policzone na OSTATECZNYM zestawie (po R52) — do ewentualnego przeniesienia przez nadzór do `recenzja_koncowa/` jako nowy plik z datą.

## Pliki oddane
- `handout.md` (ten plik), `znaleziska.md` (główny raport), `draft_skrypty_sprawdzajace.md`, `draft_buduj_plan.md`,
- `testy_edge/`: `audyt_kluczy.py`, `test_walidator.py`, `warianty.py`, `uruchom_geometria.sh`, `test_sprawdz.sh`, `sprawdzacze/` (5 skryptów), `buduj_plan/` (3 skrypty). Wszystkie uruchamialne; polecenia w nagłówkach plików. Wyjścia przebiegów tylko w scratchpadzie (ulotne).

## Co dalej (dla nadzoru, nie dla tej sesji)
1. Przed pomiarami: poprawić README krok 2 i komunikat LICZONE (ścieżka „zamrożone 54/59,6/63,6 + `pi_clearance_top` wynikowe”); dodać kontrolę SHA korpusu W/P i blatu względem zamówionych.
2. Ponowić `trzecie_oko.py` na ostatecznych plikach (S‑02) albo przenieść gotowe tabele z lustra.
3. Odporność na pustą siatkę / obcięty STL w generatorze i `sprawdz_*.py` (G‑02, S‑04); kopia `wyniki_v2/stl` przed `wyczysc_wyniki`.
4. K‑44b: minimum luzu 3 niezależne od wpisu; walidacja zakresów parametrów.
