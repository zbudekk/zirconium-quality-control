# Handout — sesja WYKONALNOŚĆ (audyt 31.10.2026)

Status: **ZAKOŃCZONE** (31.10.2026). Wynik: `znaleziska.md` (19 ryzyk, 5 najważniejszych na początku). Żaden plik projektu nie został zmieniony; pisano tylko do tego folderu.

## Zadanie
Niezależna analiza wykonalności i poprawności planu ramek v2 i jego założeń: (1) co może UNIEMOŻLIWIĆ wykonanie, (2) co WYMUSI PÓŹNIEJSZE ZMIANY. Zakaz modyfikacji plików projektu.

## Przeczytane (kamień milowy 1)
- `00_NADZOR_STAN.md`, `00_PODSUMOWANIE_PORANNE.md`, `decyzje_nocne.md` — stan 27.10: G0–G4b zaliczone, 17 STL ostateczne; korpus W+P i blat ×2 „zamów dziś” (brak wpisu, czy zamówiono); płytki/wkładka/pokrywka czekają na pole skanowania; skanera NIE MA; Drive nie wgrane.
- `plan_ramki_v2.md` sekcje 1, 2, 3 (przez JSON), 4, 5, 7, 8, 9, 10, 11, 13; `parametry.json` (273 klucze, 19 DO_ZMIERZENIA — tylko bryły zastępcze).
- `protokol_weryfikacji_v2.md` 0, 1, 2, 8, 9, 10; `analiza_odpornosc_R50.md` 0–4; `R50_wdrozenie_zmiany.md` 3.
- `Stanowisko kontroli cyrkonii — plan wdrozenia v2.md` (całość poza C–G załączników), `Zakupy i druk — stanowisko kontroli cyrkonii.md` (całość).
- `notatki_dokumentacja_skanera.md`, `mail_aidite_zapytanie.md` (projekt — brak śladu wysłania).
- `recenzja_koncowa/raport_koncowy.md` 0–2, 4–8; `wyniki_v2/do_v3.md`; `wyniki_v2/raport/notatki_wykonawcy.md` §4–11; `wyniki_v2/arkusze/arkusz_zamowienia.md`; `wyniki_v2/json/uklad_gniazd_wieczorna.json` (początek).
- `stanowisko/`: README, ustawienia.toml, opisy_modulow/*, requirements, test_uklad.py; git 1 commit.
- Korekta 31.10: repo GitHub wycofane ze źródeł (polecenie właściciela przez koordynatora). Źródła wyłącznie lokalne: `<PC>\Desktop\Ramki` i repo git `stanowisko/`. W‑05 przepisane na podstawie obietnic samego planu wdrożenia (dane pacjentów, nazwiska, sieć); W‑08 wszedł do TOP 5.

## Kamień milowy 2 — pomiar STL i weryfikacja zewnętrzna (zakończony)
- `pomiar_stl.py` (trimesh, tylko odczyt): 17 STL zamknięte; korpus 200 × 200,6 × 59,6, ściany 2,5, dno 3,0, wnętrze 195, otwór DC 12,0 (oś y 89), ścianka za kieszenią zatrzasku 1,5, boss Pi wierzch 8 / otwór do 3; blat kołnierz 194,0 × 2,0, ramię haczyka 1,5; wkładka otwór 96,6; płytka 96 × 96 × 8,6, stożek 3,0, kieszeń magnesu 2,2, dołek 1,0; tulejka 11,848 / 8,200. Zgodne z `parametry.json` i trzecim okiem.
- Źródła zewnętrzne: strona Aidite (A‑IS Pro: 1,3 MP, < 10 µm, 260 × 270 × 420, 1–8 dies); klasa Shining DS‑EX/DS‑EX Pro: pole 100 × 100 × 75; dokumentacja Shining die‑in‑one: max 8 dies; Waveshare P2.5 64×64: 5 V / 3 A, ≤ 20 W, brak danych o otworach (zip „2D Drawing”); Adafruit Bonnet: Pi 2/3/4 (nie Pi 5), 0,12 A × szerokość, zalecane osobne zasilanie Pi; tolerancje MJF: ±0,3 % (Xometry/Wevolver), ±0,3 do 100 mm i ±0,3 % powyżej (Weerg), HP w Z ±0,42–0,60.

## Kamień milowy 3 — grupy ryzyk (zakończony)
A skaner/płytki: W‑01, W‑02, W‑03, W‑14, W‑16. B panel/Pi/łańcuch: W‑06, W‑07. C druk/tolerancje/materiał: W‑04, W‑15. D gwinty/tulejka/DC: W‑10, W‑11, W‑12, W‑13. E chłodzenie/zasilanie: W‑08, W‑09. F program/bezpieczeństwo: W‑05, W‑18, W‑19. G dokumenty: W‑17.

## Najważniejsze wnioski (skrót)
1. Jedyne ryzyko zdolne unieważnić koncepcję: pole i ścieżka skanowania (W‑01) — mail do Aidite nie został wysłany; wysłać dziś.
2. Założenie, że światło przez otwór ø3 pod koroną jest widoczne, nigdy nie było testowane (W‑02) — test za 0 zł przed zamówieniem płytek.
3. Program (W‑03, W‑05): DentalScan (OEM Shining, ≤ 8 dies w Multidie, zlecenie na skan, możliwe usuwanie uchwytu) wymusi zmiany w `scanner` i `plate`; plan wdrożenia obiecuje, że dane pacjentów nie opuszczą laptopa stanowiska i M365, a instrukcja repo `stanowisko/` każe kopiować prawdziwe STL na komputer dewelopera — anonimizacja danych testowych już teraz.
4. Druk: luzy 0,25/0,3/0,5 są ciaśniejsze niż typowe ±0,3 % MJF; biały PA12 = SLS; spodziewać się dopasowania ręcznego (W‑04).
5. Elektronika: prąd — panel do 20 W przy zasilaczu 4 A (W‑08, w TOP 5), chłodzenie (W‑09), obudowa czujnika Halla (W‑13), rozstaw otworów panelu ≤ 149,6 (W‑06) — rozstrzygnąć przy zakupie i na stole przed montażem.

## Pliki tej sesji
- `znaleziska.md` — wynik końcowy.
- `pomiar_stl.py` — skrypt pomiaru (uruchomienie: `py -I pomiar_stl.py` w tym folderze; wymaga trimesh, numpy; tylko odczyt STL).
- `handout.md` — ten plik.
