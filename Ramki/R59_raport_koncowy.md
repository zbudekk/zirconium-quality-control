# R59 - raport koncowy: nowy uklad gniazd plytek

Paczka R59 (zlecenie wlasciciela 14.11.2026), zamknieta 17.11.2026. Plan: `plan_sesji_R59_uklad_gniazd_2026-11-14.md`.
Przebieg i decyzje doslownie: `00_NADZOR_STAN.md`, sekcja "R59". Zrodlo prawdy zmian: `R59_wdrozenie_zmiany.md`.

## 1. Wynik

| Plytka | Bylo (R54-R57) | Jest (R59) |
|---|---|---|
| wieczorna (W-b) | 18 gniazd: 7 x fi 9, 6 x fi 12, 5 x fi 15 + 2 rynienki 60 x 15 | 18 gniazd: 6 x fi 12, 12 x fi 15 + 1 rynienka 60 x 15 |
| poranna (P-e) | 31 gniazd: 18 x fi 7,5, 7 x fi 10, 6 x fi 12,5 + 2 rynienki 50 x 13 | 23 gniazda: 20 x fi 12,5, 3 x fi 15 + 1 rynienka 50 x 13 |

Plytki okragle maja ten sam uklad co kwadratowe tego typu. Korpusy, blat, wkladka, pokrywka, tulejka DC i podkladki sa bez zmian
(9 z 9 bajtowo = R57). Pliki do zamowienia i SHA-256: `R59_wdrozenie_zmiany.md`, sekcja 0. Arkusz zamowienia: `R59_arkusz_zamowienia.md`.
Program stanowiska rozpoznaje stare plytki (modele `*_r54`), a straznik ukladu wykrywa skan zlej plytki: 240 z 240 wykrytych, 0 z 240 falszywych alarmow.

Obowiazujacy pakiet: `Ramki_pakiet/` (82 pliki, `SHA256SUMS_2026-11-16_R59.txt` 81/81).
Pliki na Dysk Google: `Ramki_do_wgrania/*2026-11-16_R59*` (3 ZIP-y, plik sum, instrukcja, 3 PDF).
Serwer: `https://wydania.mbuas.pl/qc/Ramki_pakiet_2026-11-16_R59.zip` (19 852 286 B, SHA-256 d5c8508aa3262e2e90c1a4029aadaed25d6ad96a00d130b54352a56016dbc25a),
zarejestrowany 17.11 07:00, skan sekretow bez trafien.
Scalenie: PR #12 (merge 641186e). Wpis `qc` w rejestrze serwera: PR mbuasm/serwer-laptop #356 (merge 4003791).

## 2. Testy przed -> po

| Test | Przed R59 (E0) | Po R59 |
|---|---|---|
| T0 git / STL | - | czysto, 21 STL |
| T1 weryfikator ukladu | - | kod 0, 103 OK, liczby = G0 |
| T2 generator SPRAWDZ | 58 ZAL / 5 N/D / 0 NIE | 58 ZAL / 5 N/D / 0 NIE |
| T3 a-e sumy i zgodnosc plikow | 23/23 z R57 | 9/9, 16/16, 81/81, 14/14, 14/14 |
| T4 wlasny pomiar siatek | - | 12/12 plikow, 258/258 gniazd, 5064 sondy |
| T5 pytest stanowiska | 166 / 3 / 0 | 252 / 3 / 0 |
| T6 program na nowych plytkach | - | 12/12 |
| T7 metryki | "dobrze" 92,5 % | 89,4 % (-3,1 pkt, przyjete na G1); zestaw kontrolny 93,6 % vs 93,3 % |
| T8 stare plytki i straznik | mapa seed 7001 | 4/4 i 32/32 |
| T9 katalog gniazd | - | 15/15 |
| T10 mosty | - | 6/6 |
| T11 dokumenty i PDF | - | 0 liczb starego ukladu poza miejscami "bylo"; PDF 27/11/16 stron |
| T12 model 3D | - | OK (2. proba; 1. blad WebGL testu) |
| T13 ZIP-y | - | CRC OK, 3 ZIP-y = pakiet 82/82 |
| T14 higiena PR | - | 0 STL poza dozwolonymi, 0 znakow sterujacych |

Recenzje PR: runda 1 B 0 / P 0 / D 12, runda 2 B 0 / P 0 / D 4, runda 3 (przyrostowa) "do scalenia", D 1.
Recenzja z siatek R59-B: ZALICZONY, B 0 / P 0 / D 5.

## 3. Subsesje

| Subsesja | Iteracje | Czas | Wynik |
|---|---|---|---|
| R59-U uklad (studium) | 1 | ok. 1 h | warianty i weryfikator ukladu |
| R59-A wykonawca | 2 + poprawka planu | 34 min + poprawka | parametry, generator, 12 STL, 4 JSON |
| R59-B recenzja z siatek | 1 | 42 min | ZALICZONY |
| R59-M model 3D | 1 | 35 min | `ramka_3d.html` |
| R59-D dokumenty | 1 + poprawka | ok. 40 min | 3 dokumenty, arkusz zamowienia |
| R59-P program | 1 | 100 min | modele `*_r54`, straznik, 252 testy |
| R59-PDF | 2 budowy | ok. 1 h | 3 PDF na MSI (D7-b), poprawka tabeli |
| R59-K pakiet | 3 kroki + poprawka | ok. 2 h | pakiet, 3 ZIP-y, ZIP calosci |
| R59-R recenzja PR | 3 rundy | 29 + 25 + 19 min | do scalenia |
| poprawka serwer-laptop | 1 + 2 recenzje | 45 min | wpis `qc`, katalog wydan |

## 4. Odstepstwa i problemy

- Plytka poranna: wlasciciel zmienil wariant z P-b na P-e (szkic wlasny, bez fi 7,5 i fi 10).
- PDF zbudowane na MSI (D7-b): konto `<konto-PC>` nie ma `py`. Zainstalowano venv `<MSI>\.venvs\qc-pdf` i Chromium Playwright.
- Nowe wymaganie poza planem: publikacja w katalogu wydan serwera jako jeden ZIP (decyzja wlasciciela 15.11).
- Limit modelu Fable 16.11 00:23: 3 subsesje przerwane; dalsza praca na Opus 5.5 po decyzji wlasciciela ("Kontynuuj prace").
- Incydent R59-K 15.11: straznik sciezek przepuscil cel w repo, skrypt wykonal pelna budowe w worktree; cofniete, straznik poprawiony dwukrotnie (runda 2: D1).
- Bledy testow koordynatora (T9, T3c/T11/T14, pierwsza powtorka po recenzji): wszystkie z winy skryptow testowych, poprawione, wyniki powtorzone.
- Dysk Google (D8-b) nie wgrany: sesja nie miala przegladarki ani connectora Drive - zadanie dla wlasciciela.

## 5. Zostaje (poza R59)

- Metryka "dobrze" -3,1 pkt (przyjeta na G1); progi straznika do sprawdzenia na pierwszym prawdziwym skanie.
- PDF: plan pomniejszony do 0,805, Zakupy do 0,751, rozne wielkosci tekstu (wada sprzed R59).
- Jeden mostek na plytke; `mail_aidite_zapytanie.md` nieaktualny; liczby w tekstach generatora; okno programu bez przelacznika straznika.
- "Budowa ramki" linia 96: zdanie o pikselach pod usunietym gniazdem fi 7,5 (takze w PDF) - przy nastepnej budowie PDF.
- Skrypt pakietu: komunikat po przerwanej zamianie i katalog `*.stary_R59` poza `.gitignore` (wzor nastepnego skryptu).
- PC: `<PC-katalog>\r59` po usunieciu 3 kopii `Prace_test` ma 23,5 GB (12 398 plikow) - do decyzji wlasciciela.

## 6. Wnioski

1. Weryfikator ukladu (`weryfikuj_uklad_R59.js`) przed generatorem skrocil iteracje: wariant mozna bylo ocenic w sekundy, zanim powstaly STL.
2. Straznik sciezek trzeba testowac na kopii poza repo i na wszystkich postaciach sciezek (`C:/`, `/c/`, `C:\`); porownanie napisow zawiodlo dwa razy.
3. Skrypty testow koordynatora tez trzeba sprawdzac na danych "bylo / jest": trzy z czterech FAIL-i bylo bledami testu, nie produktu.
