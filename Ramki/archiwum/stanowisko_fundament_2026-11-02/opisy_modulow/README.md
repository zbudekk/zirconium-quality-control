# Opisy modułów

Jeden plik na moduł. Przed zmianą kodu modułu przeczytaj jego opis; po zmianie zaktualizuj sekcję „Założenia i granice”. Opisy modułów jeszcze nienapisanych streszczają zamówienie z planu wdrożenia v2 (sekcja „Oprogramowanie: moduły i jak powstanie”).

| Moduł | Stan | Co robi (jedno zdanie) | Wejście → wyjście | Kryterium „działa” |
|---|---|---|---|---|
| uklad | gotowy | układ płytki z JSON | nazwa → `UkladPlytki` | test_uklad |
| synth | gotowy (v1) | sztuczne skany z prawdą | STL projektów → skan STL + JSON | test_synth |
| catalog | do napisania | indeks projektów: foldery „Cyrkon”/„Prywatne”, raporty MillBox, cechy STL (objętość, wymiary, deskryptor, miniatura), SQLite | foldery → tabela projektów | parser nazw na 50 nazwach folderów bez błędu; parser 10 raportów MillBox: pliki, krążek, współczynnik; cechy 30 STL < 10 s |
| plate | do napisania | wyrównanie skanu po 3 stożkach (ICP), odczyt numeru z dołków, cięcie na gniazda, puste/podwójne/poza gniazdem | STL skanu → fragmenty z numerem gniazda | na skanach syntetycznych: błąd wyrównania < 0,05 mm, numer płytki 100%, każdy fragment w swoim gnieździe |
| match | do napisania | identyfikacja fragmentu: filtr objętość/wymiary → FPFH+RANSAC → ICP → ranking z pewnością | fragment + pula → kandydaci + transformacja | top‑1 ≥ 95% i top‑2 ≥ 99% na 200 fragmentach syntetycznych; później ≥ 85% / ≥ 95% na prawdziwych |
| inspect | do napisania | mapa odchyłek, ubytki (≥ 0,08 mm pod powierzchnią, ø 0,2–1,5 mm, ostra krawędź, pas brzegu 1,5 mm), odrzucenie gładkich poprawek, wykrycie drgnięcia | fragment + projekt → ubytki | na 100 ubytkach syntetycznych: wykryte ≥ 90%, fałszywe ≤ 10%, drgnięcie 100% |
| session | do napisania | stan wieczoru/poranka, decyzje technika, sesja pieca, zliczanie punktów zleceń (trwałe), lista braków, „do dofrezowania”, poprawki | zdarzenia → stan (SQLite) | scenariusz 3 pieców + 1 dofrezowany ząb daje właściwe listy |
| ui | do napisania | ekran wieczorny (mapa płytki, 3D z odchyłkami), poranny (podpisy, kandydaci, kuweta po kuwecie), spacja, klawiatura ramki | stan → ekran | technik obsługuje bez instrukcji na danych syntetycznych |
| indicate | do napisania | gniazdo → piksele matrycy, protokół Wi‑Fi do ramek (plan płytki, stan, potwierdzenia); symulator ramki na laptopie | polecenia → światło | symulator pokazuje plan; prawdziwa ramka po dostawie elektroniki |
| excel | do napisania | wiersz zlecenia wg reguł 1–6 z planu, kolor B (198, 239, 206), log CSV, tryb „[cytat usuniety]” | zlecenie → zmiana + log | 50 kuwet z historii na kopii pliku: 50/50 zgodnych z człowiekiem |
| scanner | do napisania | watchdog na folderze eksportu, walidacja pliku, opcjonalny automat (okno DentalScan + Spacja) | plik → zdarzenie „nowy skan” | plik skopiowany do folderu wywołuje zdarzenie w < 1 s, plik niepełny ignorowany |
