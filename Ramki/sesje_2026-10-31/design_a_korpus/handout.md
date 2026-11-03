# Handout — DESIGN A: korpus, blat, wkładka, pokrywka, tulejka, podkładki, elektronika

Status: **ZAKOŃCZONE** (31.10.2026, kamienie 1–5). Pliki: `handout.md`, `pomiar_stl.py`, `bbox_stl.py`, `pomiary_stl.md`, `pomiary_stl.json`, `znaleziska.md`.

## Przeczytane
- `plan_ramki_v2.md` sekcje 2 (D1–D16), 3 (3.1–3.6), 4 (4.1–4.11), 5, 7, 8, 9, 10, 11, 13 (R1–R52, R50‑1…8, R50‑U1…U20)
- `parametry.json` (273 klucze), `R50_wdrozenie_zmiany.md`, `decyzje_nocne.md`, `00_PODSUMOWANIE_PORANNE.md`, `00_NADZOR_STAN.md` (fragment), `00_PRZEPLYW_I_BRAMKI.md` (sekcje 11–13 przez grep)
- `analiza_odpornosc_R50.md` sekcja 6 (U‑1…U‑20: które odrzucono i dlaczego)
- `wyniki_v2/arkusze/arkusz_wymiarow.md` (gabaryty, wymiary, pasowania w złożeniu)
- `recenzja_koncowa/raport_koncowy.md` sekcje 0–2, 4–8 (trzecie oko: 0 blokujących, U1–U11)
- `Zakupy i druk — stanowisko kontroli cyrkonii.md` (druk drukarnia / FDM / żywica, checklista odbioru)
- `Ramki_pakiet/03_Druk_wlasny/PETG_FDM/SPECYFIKACJA_DRUKU_FDM_wkladka_pokrywka.md`, `spec_3d_ramka_v3.md`
- Korekta 31.10: repo GitHub wycofane ze źródeł; źródła wyłącznie lokalne.

## Ustalenia wstępne (do weryfikacji w części 1)
- Zamówienie w drukarni: w plikach projektu NIE ma śladu, że zamówienie korpusu W/P i blatu ×2 poszło (00_PODSUMOWANIE_PORANNE: „[cytat usuniety]” = lista do zrobienia, nie potwierdzenie). Traktuję korpus/blat jako JESZCZE NIE ZAMÓWIONE, chyba że właściciel potwierdzi inaczej → zmiany korpusu są jeszcze możliwe.
- Odrzucone przez właściciela uproszczenia (nie proponuję ponownie bez nowego argumentu): U‑2 wkręty blatu (ramka P noszona), U‑3 zatrzaski, U‑7 kieszeń DC (Z27: wtyk nie wystaje), U‑11 półki Halla, U‑12 kołek, U‑13 wycięcie palcowe; U‑14 napis korpusu ZOSTAJE (decyzja właściciela).
- Interfejs płytka↔wkładka/blat (zakres DESIGN B po stronie płytki): otwór 96,6 × 96,6 (płytka 96 + 0,3/stronę), półki 12 × 12 na Z +2,5, kołek 4,4 × 4,4 × 5 w wycięciu 5 × 5 (luz 0,4), kieszenie Halla 5,0 × 5,5 pod osiami (±42, ±42), magnes ø5 × 2 cofnięty 0,2, spód płytki 1,0 nad licem czujnika; pokrywka: wnęka 96,6, garby 0,7 w rowek 0,8 na Z −2 od wierzchu płytki.

## Środowisko
- Python: `py -3.12` (numpy, trimesh 5.2 — potwierdzone przez sesję KOD A); `python` w Git Bash = stub Store. `PYTHONUTF8=1`.
- Skrypty pomiarowe: `pomiar_stl.py` (ten folder). Nic nie zapisuję poza tym folderem.

## Pomiary STL (kamień 2) — wynik
- `pomiar_stl.py` → `pomiary_stl.md` + `pomiary_stl.json`: 291 wymiarów (korpus W i P, blat, wkładka, pokrywka, tulejka, 3 podkładki, płytka n1 jako interfejs), 9 sond „przelot” (wszystkie zgodne), 35 pasowań policzonych z wartości zmierzonych; profil haczyka blatu co 0,05 mm, profil garbu pokrywki, profil rowka płytki.
- **0 różnic > 0,05 mm** względem `parametry.json`; wszystkie luzy = plan (kołnierz 0,5; haczyk 0,8/0,2/0,3/0,25; kołek 0,15; magnesy 0,2/0,1; płytka 0,3; kołek orient. 0,4; garb 0,4/0,4; tulejka 0,075; dyfuzor 1,0). Łańcuch wysokości z siatek: 63,6 / 66,1 / 69,6 / 74,1 ✓. W = P poza napisem (0 różnic wierzchołków).
- Pułapki sond (dla kolejnych sesji): blat i pokrywka w STL są obrócone 180° wokół X → tył blatu ma y < 0, przedni garb pokrywki ma y > 0; rowek panelu przechodzi też przez stadion (sonda na osi nie trafia); kanał pod uchem wkładki jest otwarty bokiem (x 63…65).
- Rozbieżności wymiarowe geometria↔parametry: BRAK. Rozbieżności PROJEKT↔TOLERANCJE DRUKU: patrz `znaleziska.md` część 1 (to one są treścią części 1).

## Kamienie 3–5 — wynik (`znaleziska.md`)
- Część 1: geometria↔parametry 0 rozbieżności; 16 pozycji projekt↔tolerancje druku (T1–T16) z liczbami; 3 wysokie: T2 (zahaczenie haczyka 0,2…1,4), T3 (luz Z haczyka −0,1…0,7 → widoczna szczelina blat–korpus), T4 (wkręty tylne: do 0,6 przesunięcia przy luzie 0,1); T9 wypaczenie blatu/dna MJF. Naprawy = liczby w JSON.
- Część 2: P1–P16; rekomendowane: P2 (magnesy zamiast zatrzasków i wkrętów), P3 (kołki stalowe), P5 (bez tulejki: otwór ø8,2 + gniazdo M8×0,75 10 A), P6 (bez podkładek drukowanych), P8a (kątowy wtyk DC Bonnetu), P13 (bez szczelin bocznych), P14, P16 (shadow gap); P1 (korpus+blat jedna bryła, dno od spodu) tylko w wariancie bardzo premium (2–3 dni).
- Część 3: tabela zlecić/samemu per część; kluczowe: „biały PA12” = SLS (MJF jest szary) — arkusz zamówienia do poprawy; korpus/blat MJF lub SLS czarny barwiony + wygładzanie parowe + grawer; pokrywka i wkładka SLS biały zamiast FDM; CNC alu korpusu odrzucone (1 500–3 000 zł/szt., przeprojektowanie); blat alu jako opcja ultra‑premium. Język wizualny: czarna satyna + kość mat, bez reliefów, akcent W indygo / P bursztyn.
- Źródła cen/tolerancji na końcu `znaleziska.md` (Sculpteo, Materialise, 3D Print UK, Cubic Inch PL, Formlabs, Delock).

## Dla następnej sesji
- Decyzja D‑2: płytki szare — uwzględniona (znaleziska.md: wniosek 2, 3.1 p. 9, 3.2 wkładka/pokrywka, 3.3 język wizualny, 3.4 p. 2). Wkładka w kolorze korpusu (czarna barwiona), pokrywka w kolorze płytki (szara surowa).
- Nie zmieniałem żadnych plików projektu ani STL; nic na Drive; GitHub nieużywany (korekta 31.10).
- Decyzje do właściciela: (1) czy korpus/blat już zamówione (w plikach brak śladu); (2) wariant: poprawki 0 zł + P2/P3/P5/P6 czy P1; (3) napis: grawer vs relief; (4) wkładka MJF czarna / pokrywka MJF szara zamiast FDM.
- Po decyzji: edycja `parametry.json` (lista w `znaleziska.md` 3.4 pkt 1) → przebieg generatora → pełna ponowna weryfikacja (reguła zero tolerancji) → wycena.
