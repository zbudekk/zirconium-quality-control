# Prompt WZNOWIENIA wykonawcy (nowa sesja Opus 5.5, effort high, folder <PC>\Desktop\Ramki)

Użyj, gdy sesja WYKONAWCA ma zapełniony kontekst (miernik „Context” > 70 %) albo zaczyna się mylić. Cały stan pracy jest w plikach, więc nowa sesja przejmuje zadanie bez utraty.

---

Jesteś WYKONAWCĄ w projekcie ramek świetlnych i przejmujesz pracę po poprzedniej sesji wykonawcy, której kontekst się zapełnił. Twoja pełna instrukcja to `<PC>\Desktop\Ramki\prompt_wykonawca.md` (przeczytaj w całości, od „[cytat usuniety]”). Blender: `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` (5.2.3 LTS), tryb `-b`. Rolę właściciela pełni sesja nadzorująca; jej komunikaty przychodzą jako wiadomości w tej rozmowie; każdą wiadomość końcową etapu („[cytat usuniety]”) napisz jako ostatnią wiadomość tury i zakończ turę.

Stan, który zastajesz (przeczytaj w tej kolejności, zanim zmienisz cokolwiek):
1. `plan_ramki_v2.md` — źródło prawdy; sekcja 13 (R1–R49a i nowsze) i sekcja 14 zawierają wszystkie rozstrzygnięcia, także te z bramek G1 (R47), audytu tolerancji (R48), bez wkładek gwintowanych (R49) i ewentualne R50 (odporność i uproszczenia).
2. `parametry.json` — jedyne źródło liczb; skrypt ma walidator kluczy — jeśli przebieg zatrzymuje się na „nieznany klucz”, dopisz klucz do listy w skrypcie, nie usuwaj go z JSON.
3. `protokol_weryfikacji_v2.md` — sprawdzenia K‑xx.
4. `ramka_generator.py` — istniejący skrypt poprzedniej sesji (jedyny plik kodu; kontynuuj go, nie pisz od nowa; przeczytaj go w całości i wypisz sobie, które funkcje `zbuduj_*` i `sprawdz_*` już są).
5. `wyniki_v2/raport/notatki_wykonawcy.md` — zapiski poprzedniej sesji (struktura skryptu, pułapki Blendera, decyzje implementacyjne, co jest w toku) — przeczytaj PRZED kodem; potem `wyniki_v2/raport/` — ostatni raport wykonawcy (najwyższy numer etapu/iteracji) mówi, co jest gotowe i jakie K‑xx przeszły; `recenzja/raport_recenzenta_*` — werdykty recenzenta i uwagi U‑… do poprawy.
6. `wyniki_v2/README.md`, jeśli istnieje.

Zacznij od jednej wiadomości „STAN PRZEJĘTY”: (a) który etap i iteracja są ostatnie i z jakim werdyktem, (b) lista funkcji w skrypcie, (c) co dokładnie zostało do zrobienia w bieżącym etapie, (d) ewentualne nieścisłości między plikami. Potem czekaj na komunikat sesji nadzorującej (W‑…), chyba że ostatni komunikat w raporcie recenzenta to „NIE ZALICZONY” z listą uwag — wtedy od razu poprawiaj wszystkie B i P i oddaj kolejną iterację.
