# Lista drobnych (D) do v3

Wygenerowana przez `ramka_generator.py` na bramce G4 (plan, `00_PRZEPLYW_I_BRAMKI.md` §8). Nie blokuje zamówienia.

| # | Źródło | Uwaga |
|---|---|---|
| 1 | recenzja A §6.1 | Dołek kodu a rowek pokrywki: 1,3 mm materiału po przekątnej (< 1,5 z zasady 4.8), przyjęte w R47(10). Do rozważenia: dołki na x = −44,5 (1,7) albo rowek przerwany na odcinku y −38…−28 lewego boku. |
| 2 | recenzja A §6.2 | Ścianka 1,0 mm między dołkami ø2 w rozstawie 3 (głębokość 1, bez wpływu na odczyt). |
| 3 | recenzja A §6.3 | Tabela 3.1 (`code_dimple_x`) i sekcja 11 (objętość pokrywki) — poprawione w planie przez nadzór (stan obecny: −45,0 i 30 cm³). |
| 4 | recenzja B §6.1 | Odbiornik USB klawiatury (tylko P) poza testem K‑53 (korpus P odsunięty); propozycja: proxy w zestawie złożonym jako pozycja hipotetyczna albo osobna para w K‑53. |
| 5 | recenzja B §6.2 | Klucze `rama_ear_d` / `rama_ear_t` obok `rama_tab_size` — nieaktualne: rama dyfuzora i jej klucze usunięte (R50‑U1). |
| 6 | recenzja B iter3 §6.1 | Odbiornik USB (korpus P) poza zestawem K‑53; w etapie C dodany test informacyjny w położeniu hipotetycznym w zestawie W (uwaga przy K‑53 w raporcie C). Do v3: para w K‑53 w protokole. |
| 7 | recenzja B iter3 §6.2 | `insert_depth_m3` 7 w `parametry.json` opisany jako nieużywany po R50 — do usunięcia w v3. |
| 8 | wykonawca (B3) | Plan 4.4 p. 3: słupki „zrośnięte z kołnierzem 95,2…97,2” i 4.11 „wnętrze kołnierza 97,2” — po R48 kołnierz blatu leży na 95,0…97,0 (194,0 zewn.); liczby w skrypcie z `parametry.json`, STL bez zmian. |
| 9 | wykonawca (B3) | `ramka_wkladka_v2.stl`: SHA różni się między przebiegami — w B iter2 wybór przekątnej w 2 płaskich prostokątach fazy (remis BEAUTY), w B iter3 znak zera (−0,0 / +0,0) w składowych zapisanych normalnych; wierzchołki i trójkąty identyczne. Propozycja: w `stl_kanoniczny` zamiana −0,0 na +0,0 i kanoniczna przekątna w remisach (zmienia bajty wszystkich STL, także zatwierdzonych płytek — tylko z decyzją nadzoru). |
| 10 | wykonawca (B3) | Bryła zastępcza gniazda DC bez gwintu ø8 w tulejce: średnica gwintu nie ma klucza (wynik pomiaru #16). |
