# Raport recenzenta - PR #64 (E3-U1b: tryb poranny i panel Excela w nowym oknie), runda 2

Data: 25.11.2026. Recenzent: konto 3 (zlecenie rec-u1b-r2). Recenzja przyrostowa.
Zakres: commity po `233ed1b` na `origin/e3/u1b`, HEAD `b7b085b` (PR #64 otwarty, wersja robocza, baza `e3/u1-okno`).
W tym commit scalenia `1e89ff4` (`origin/e3/u1-okno` 6114846, runda 2 U1a - zmian U1a nie oceniam, tylko czy scalenie
niczego nie zgubilo) i 9 commitow U1b rundy 2: `git diff 1e89ff4 origin/e3/u1b` = 16 plikow, +638 / -17 (w tym 8 PNG).
Miara: raport rundy 1 (`konto3\recenzje\raport_recenzenta_PR64_runda1.md`, uwagi P1-P4, D5-D8), zlecenie poprawek
`konto3\zlecenia\u1b-r2.md`, dalej miara i lista "znane, nie zglaszac" ze zlecenia rundy 1.

Metoda: (1) scalenie sprawdzone porownaniem latek: `diff(e57fabe..233ed1b)` z `diff(6114846..1e89ff4)` i `diff(e57fabe..6114846)`
z `diff(233ed1b..1e89ff4)` (bez naglowkow hunkow); (2) caly diff rundy 2 U1b przeczytany (`ekran_rano.py`, `mapa_rano.py`,
`motyw.py`, `napisy_rano.py`, `okno_excela.py`, `test_ui_poranek.py`) i kod wokol zmian (`PanelKuwet`, `EkranRano.pokaz`,
`okno._polecenie` / `pokaz_stan` - skad bierze sie "stan z tla", rysowanie pierscienia w `mapa.py`, legenda lewej kolumny);
(3) pliki testow okna obu paczek we wlasnej kopii `<PC-katalog>\qc-wt\rec-u1b` (detached `b7b085b`), tor 3; (4) wlasne
proby na atrapie kontrolera (`<PC-katalog>\konto3\robocze\rec-u1b-r2\proby\`, wyniki `proby_wynik.txt`), w tym
powtorzenie pomiaru P1 z rundy 1; (5) 15 wstrzykniec bledu (`wstrzykniecia.ps1`, wyniki `wstrzykniecia_wynik.txt`);
(6) zrzut `rano_kandydaci_1536x864.png` obejrzany, wycinki map z prob obejrzane; (7) `KONIEC_u1b-r2.txt`, sekcja "Runda 2"
raportu paczki i log pelnego pytest przeczytane na koncu. Pelny pytest nie byl powtarzany. Okno nie bylo ogladane na
prawdziwym ekranie (Qt offscreen). Po probach kopia czysta (`git status --short` pusty, HEAD `b7b085b`).

## 0. Werdykt

**Do scalenia po poprawkach.** B 0 / P 1 / D 2 (otwarte po tej rundzie: nowa P9, nowa D10, D7 z rundy 1 odlozona).

Stan uwag rundy 1: **P1 zamknieta, P2 zamknieta, P3 zamknieta czesciowo, P4 zamknieta**; D5, D6, D8 zamkniete; D7 odlozona
(zalezy od decyzji wlasciciela o liczbie plytek - przyjmuje). Najwazniejsze z rundy 1 jest naprawione: klikniecie w liste kuwet
po zmianie z tla nie wybiera juz innej kuwety (moj pomiar: 0 pomylek na 38 klikniec w chwili zmiany, 33 kroki x 3 rozmiary),
a ochrona nie zjada zadnego klikniecia przy szybkim rozkladaniu z okna (0 z 99). Obwodka biezacej kuwety (biala) i pierscien
wybranego gniazda (niebieski) sa na mapie rozroznialne takze wtedy, gdy wybrane gniazdo nalezy do kuwety. Otwarta zostaje druga
polowa P3: objasnienie obwodek wrocilo, ale do legendy na dole przewijanej lewej kolumny - przy oknie zmaksymalizowanym przy
125 % i 150 % (1536x784, 1280x642) w zwyklym piecu z 3 plytkami nie widac z niego ani jednego piksela (uwaga 9).

## 1. Uwagi

### 1.1 Uwagi rundy 1

| Nr | Waga r1 | Stan | Dowod (wlasna proba) |
|---|---|---|---|
| 1 | P | **zamknieta** | Pomiar A z rundy 1 powtorzony (`test_a2_*`, 33 x "Rozlozona" z tla, punkt srodka listy, klikniecie przy KAZDEJ zmianie): zmian kuwety pod punktem 8 / 12 / 18 (1920x1001 / 1536x784 / 1280x642; w rundzie 1 8 / 13 / 19 - roznica to skok wysokosci wiersza usuniety przez D6), w tym bez ochrony **0 / 0 / 0**, pomylek **0 z 38 klikniec**; zmian w dowolnym punkcie pola (co 4 px) bez ochrony 0. Po 850 ms ochrona gasnie i klikniecie wybiera kuwete widoczna pod kursorem (`test_a3`: 3242 pod kursorem -> `wybierz_kuwete 3242`). Szybkie rozkladanie z okna (`test_s1_*`: klik kuwety -> Enter -> po 30 ms klik nastepnej, 33 kuwety x 3 rozmiary): klikniec pominietych **0 z 99**, wybrana inna niz kliknieta 0, Enter potwierdzil kliknieta 99 z 99. Ramka + klik nastepnej widocznej kuwety po 100 ms (`test_s2_*`): pominietych 0 z 29 (ochrona startuje tylko, gdy pod punktami listy naprawde stoi co innego). Kod: ochrona tylko dla stanu "z tla" (`okno._z_tla = not _w_poleceniu`; stan po wlasnym poleceniu przychodzi synchronicznie w `okno._polecenie`). Testy pilnuja obu stron: cofniecie poprawki (N1) wykrywa nowy test rundy 2, ochrone takze po wlasnych poleceniach (N2) - test S3-16 z rundy 1. |
| 2 | P | **zamknieta** | `test_b2`: zakladka "Kompletne i braki" przy otwartym oknie Excela -> "Excel: wskaz wiersz" -> strona `excel`, panel widoczny; "Pozniej" -> wraca na `wynik`, `stan.excel.widoczne` False; ponowne "Excel: wskaz wiersz" -> znow `excel`. Test wykonawcy pada po cofnieciu poprawki (N3). Przycisk zaleglego pieca (ta sama poprawka) bez testu - uwaga 10. |
| 3 | P | **zamknieta czesciowo** | Rozroznialnosc: zamknieta. Odczyt pikseli mapy w oknie (`test_c2_*`, 3 rozmiary): pas r..r+3 px wokol gniazd kuwety 241 / 185 / 123 px bialych (`#F2F2F2`), 0 niebieskich (1280x642: 7 px akcentu z sasiedniego pierscienia); pas pierscienia wybranego gniazda 164 / 130 / 99 px niebieskich (`#338CED`), 0 bialych. Wybrane gniazdo nalezace do kuwety (`test_e_*`, wycinki `wycinek_wybrane_3_w_kuwecie_*.png`): wewnatrz biala obwodka (227 px), na zewnatrz przerwa i niebieski pierscien (408 px) - widac oba znaczenia. Zrzut `rano_kandydaci_1536x864.png`: gniazda 1, 2 kuwety 3221 biale, gniazdo 3 ("wybierz") niebieskie - rozne na pierwszy rzut oka. Kontrast: obwodka / plytka 13,87 : 1, pierscien akcentu / plytka 4,52 : 1, obie pary w `PARY_KONTRASTU`, `test_ui_motyw.py` passed w moim biegu. Test wykonawcy pada po powrocie obwodki do akcentu (N5) i po usunieciu wierszy legendy (N6). **Objasnienie na ekranie: otwarte** - uwaga 9. |
| 4 | P | **zamknieta** | Wstrzykniecia z rundy 1, ktore wtedy przeszly: E7 (N7), K2 (N8), E18 (N9) - teraz wykryte; dodatkowo "Cofnij" aktywne bez osoby (N10) wykryte. |
| 5 | D | zamknieta | N13 wykryte (`test_d5_*`, kazda kuweta scenariusza w 1536x784 i 1280x642). |
| 6 | D | zamknieta | N11 (lista kuwet) i N12 (panel Excela) wykryte; pomiar A2: 12 / 18 zmian zamiast 13 / 19 (brak skoku wiersza). |
| 7 | D | odlozona (decyzja wlasciciela) | `test_c3_*`: 6 plytek przy 1280x642 dalej 13 usterek ukladu ("uklad potrzebuje 1368x618") - bez zmian wobec rundy 1; powod odlozenia (p. 5 pkt 3 rundy 1) przyjmuje. |
| 8 | D | zamknieta | N14, N15 wykryte; `test_d8_*`: "teraz, juz rozlozona" i dopisek w opisie mieszcza sie w 3 rozmiarach (lista bez paska poziomego, 0 usterek ukladu). |

### 1.2 Nowe uwagi rundy 2

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| 9 | P | `ui/ekran_rano.py:257-298` (legenda w `rano_piec_przewijanie`), `testy/test_ui_poranek.py` (`test_mapa_rano_obwodka_kuwety_inna_niz_pierscien_*`, 1920x1001, `e.jest`) | P3, druga polowa ("objasnienie obwodek z powrotem na ekranie" - zlecenie u1b-r2). Objasnienie ("Biala obwodka - gniazda biezacej kuwety", "Niebieski pierscien - gniazdo wybrane kliknieciem") stoi w legendzie "Na plytkach" na dole lewej kolumny, ktora jest polem przewijanym. Pomiar (`test_g_*`, zwykly piec scenariusza z 3 plytkami, okno zaraz po otwarciu): 1920x1001 i 1920x1080 - widac w calosci; 1536x864 - pierwszy wiersz 28 z 34 px, drugi 0 z 34; **1536x784 (1920x1080 przy 125 %) i 1280x642 (150 %) - 0 px calej legendy** (kolumna przewija sie o 202 / 344 px); piec z 6 plytkami - 0 px we wszystkich 5 rozmiarach. Technik przy 125 % / 150 % widzi biale obwodki, ale nigdzie na ekranie nie ma, co znacza, dopoki sam nie przewinie lewej kolumny (w `main` napis o obwodce byl w wierszu biezacej kuwety, zawsze widoczny). Test sprawdza tylko `isVisible` przy 1920x1001, a `sprawdz_uklad` pomija pola przewijane, wiec nic tego nie wykrywa. Zrzuty 1536x864 tego nie pokazuja, bo scena zrzutow ma 2 plytki. | Objasnienie obwodek w miejscu widocznym bez przewijania we wszystkich rozmiarach (np. wiersz legendy oznaczen nad przewijana czescia lewej kolumny albo krotki tekst w wierszu biezacej kuwety w miejsce / obok napisu o ramce - bez zmiany wysokosci wiersza, zeby mapy sie nie przesunely). Test: 3 rozmiary (1920x1001, 1536x784, 1280x642), piec z 3 plytkami: `_widoczny_wycinek == _w_oknie` dla obu wierszy objasnienia. |
| 10 | D | `ui/ekran_rano.py:879` (przycisk zaleglego pieca -> `pokaz_excel`) | P2 objela tez przyciski zaleglych piecow ("Piec n (doba) - ile"), ale zaden test tego nie pilnuje: wstrzykniecie N4 (stare wywolanie `_polecenie("excel_pokaz", sid)` bez przelaczenia zakladki) - 102 passed. Kod jest dzis poprawny (ta sama funkcja co przycisk wyniku, ktora jest testowana). | W tescie P2 dodac klikniecie przycisku zaleglego pieca przy otwartym oknie Excela dla tego pieca -> `strona() == "excel"`. |

Nie zglaszam (znane wg zlecenia rundy 1): `ramka/logika.py`, instrukcje i `opisy_modulow/ui_rano.md`, brak proby na
prawdziwym ekranie, narzedzia odbioru T2 / T3.

## 2. Wlasne proby

Kopia `<PC-katalog>\qc-wt\rec-u1b` (detached `b7b085b`), katalog `Ramki\stanowisko`, `<PC-katalog>\koordynator\narz\py.cmd`,
1 proces python naraz.

| Proba | Polecenie | Wynik |
|---|---|---|
| scalenie U1a | porownanie latek (opis w metodzie) | latka U1b (`e57fabe..233ed1b`) i latka U1a (`e57fabe..6114846`) przeniesione przez scalenie bez zadnej roznicy (0 wierszy roznicy w obu porownaniach); 4 pliki wspolne (`napisy.py`, `okno.py`, `test_ui_motyw.py`, `test_ui_wieczor.py`) maja zmiany obu paczek; `git show --cc 1e89ff4` bez recznie rozwiazanych hunkow |
| testy okna obu paczek | `ciezki.ps1 -Tor 3`: `py.cmd -m pytest -q -p no:cacheprovider` na `test_ui_okno.py test_ui_wieczor.py test_ui_motyw.py test_ui_rano.py test_ui_poranek.py test_p14_ekran.py test_p15_ekran.py test_aplikacja_rano.py test_instrukcje.py test_okragle_ekran.py test_ui_rozdzielczosc.py` | **421 passed, 0 failed** (386 s) - `t_okno.txt` |
| pelny pytest (nie powtarzany) | ostatni wiersz `<PC-katalog>\konto3\log\u1b-r2_pytest.txt` | `2617 passed, 9 skipped, 1 warning in 2178.05s` - 0 failed, 0 wierszy FAILED / ERROR; zgodne z `KONIEC_u1b-r2.txt` |
| A2: P1, pomiar z rundy 1 | `proby\test_proby_r2.py::test_a2_*`, 3 rozmiary | zmian pod punktem 8 / 12 / 18, bez ochrony 0 / 0 / 0, pomylek 0 z 38 klikniec; zmian w dowolnym punkcie bez ochrony 0 |
| A3: klikniecie po ochronie | `test_a3_*` (1280x642) | ochrona tuz po zmianie True, po 850 ms False; klikniecie wyslalo kuwete spod kursora |
| S1: szybkie rozkladanie z okna | `test_s1_*`, 3 rozmiary | pominietych 0 / 0 / 0 z 33, wybrana inna 0, Enter potwierdzil kliknieta 33 / 33 / 33, rozlozonych w kontrolerze 33 / 33 / 33 |
| S2: ramka, potem klik nastepnej | `test_s2_*`, 3 rozmiary | prob 12 / 10 / 7, pominietych 0 |
| B2: P2 i "Pozniej" | `test_b2_*` | `wynik` -> `excel` -> ("Pozniej") `wynik` -> `excel`; 2 x `excel_pokaz` |
| C2: kolory oznaczen w oknie | `test_c2_*`, 3 rozmiary | jak w tabeli 1.1, uwaga 3; usterek ukladu przy otwartej pracy 0 / 0 / 0 |
| E: wybrane gniazdo w kuwecie | `proby\test_proby_r2b.py`, 1920x1001 i 1280x642 | biala obwodka wewnatrz + niebieski pierscien na zewnatrz (wycinki PNG obejrzane) |
| G / C3: legenda bez przewijania | `proby\test_proby_r2c.py`, 5 rozmiarow x 3 / 6 plytek; `test_c3_*` | uwaga 9; 6 plytek: usterek ukladu 0 / 0 / 13 (jak w rundzie 1) |
| D8: nowe napisy | `test_d8_*`, 3 rozmiary | lista "teraz, juz rozlozona", opis z dopiskiem; pasek poziomy listy brak; usterek 0 |
| zrzuty | obejrzany `rano_kandydaci_1536x864.png`; rozmiary 8 PNG z `git cat-file -s` | obwodki rozroznialne (uwaga 3); 8 PNG razem 1 220 060 B (zgodne z raportem wykonawcy) |

Wstrzykniecia (kazde: 1 zamiana w kopii, `pytest -x` na `test_ui_poranek.py test_ui_rano.py test_p14_ekran.py`, przywrocenie
pliku): **14 z 15 wykrytych**.

| Wstrzykniecie | Wynik |
|---|---|
| N1 P1: ochrona listy tylko przy zmianie kolejnosci (stan rundy 1) | wykryte (`test_s3_16_lista_kuwet_przewinieta_w_tle_*`) |
| N2 P1: ochrona takze po wlasnym poleceniu technika | wykryte (`test_s3_16_lista_kuwet_wybiera_po_numerze_*`) |
| N3 P2: "Excel: wskaz wiersz" nie przelacza zakladki | wykryte |
| N4 P2: przycisk zaleglego pieca - stare wywolanie | **NIE wykryte** (102 passed) - uwaga 10 |
| N5 P3: obwodka kuwety w barwie akcentu | wykryte |
| N6 P3: legenda bez wierszy objasnienia | wykryte |
| N7 P4a (E7): napis gniazd tylko z pierwszym gniazdem | wykryte |
| N8 P4b (K2): "To ten projekt" drugiego wysyla pierwszego | wykryte |
| N9 P4c (E18): "Rozlozona" aktywne bez osoby | wykryte |
| N10 P4c: "Cofnij" aktywne bez osoby | wykryte |
| N11 D6: lista kuwet - domyslna wysokosc przed minimalna | wykryte |
| N12 D6: panel Excela - to samo | wykryte |
| N13 D5: dlugi zapis gniazd w ukladzie zwartym | wykryte |
| N14 D8: bez dopisku w wierszu kuwety | wykryte |
| N15 D8: lista "teraz" zamiast "teraz, juz rozlozona" | wykryte |

Roznica z liczbami wykonawcy: wykonawca podaje pomiar P1 po poprawce "zmian pod kursorem 8 / 13 / 19, bez ochrony 0 / 0 / 0";
moj pomiar na HEAD daje 8 / 12 / 18 zmian (bez ochrony tak samo 0). Roznica po 1 zmianie w ukladzie zwartym to skok wysokosci
wiersza usuniety przez D6 - pomiar wykonawcy byl zapewne robiony przed commitem D6. Nie zmienia oceny.

## 3. Kryteria zlecenia poprawek (u1b-r2)

| Kryterium | Ocena | Dowod |
|---|---|---|
| p. 0: scalenie `origin/e3/u1-okno` bez rebase, poprawki obu paczek zostaja, pliki testow okna 0 failed | potwierdzone wlasna proba | porownanie latek 0 roznic; 11 plikow testow okna 421 passed |
| p. 1: kopia raportu recenzenta bez zmian | potwierdzone wlasna proba | `Ramki/recenzja/raport_recenzenta_PR64_runda1.md` identyczny co do bajta z `konto3\recenzje\...runda1.md` (`cmp`) |
| p. 2 P1: pomiar 33 kroki x 3 rozmiary = 0 pomylek | potwierdzone wlasna proba | A2: 0 z 38; S1: ochrona nie blokuje szybkiego rozkladania |
| p. 2 P2 | potwierdzone wlasna proba | B2, N3 |
| p. 2 P3: rozroznialne, objasnienie na ekranie, kontrast >= 4,5 : 1 | **czesciowo** | rozroznialnosc i kontrast potwierdzone (C2, E, zrzut, `test_ui_motyw`); objasnienie na ekranie tylko przy 100 % - uwaga 9 |
| p. 2 P4: trzy testy luk | potwierdzone wstrzyknieciem | N7-N10 wykryte |
| p. 2: kazda poprawka z testem, ktory bez niej pada | potwierdzone wstrzyknieciem | N1, N3, N5, N6, N7-N10 wykryte; luka tylko przy przycisku zaleglego pieca (uwaga 10, D) |
| p. 3: D tanie poprawione, reszta "D odlozone" z powodem; p. 5 rundy 1 nie rozstrzygany | potwierdzone przegladem i wstrzyknieciem | D5, D6, D8 poprawione i pilnowane testami (N11-N15); D7 odlozona z powodem; pozycje p. 5 nie rozstrzygniete (raport R2.2, R2.3) |
| p. 4: pliki tylko z listy, nietykalne nie ruszane | potwierdzone przegladem | sekcja 4 |
| p. 5: zrzuty poranka odswiezone | potwierdzone przegladem | 8 PNG zmienione w `eb8041c`; obejrzany 1 |
| p. 5: pelny pytest 0 failed | potwierdzone w logu (nie powtarzane) | 2617 / 9 / 0 |
| p. 5: raport "Runda 2" (uwaga -> co zrobiono -> dowod -> commit), push, PR roboczy | potwierdzone przegladem | sekcja R2.1-R2.6 raportu paczki; `gh pr view 64`: OPEN, isDraft true, head `b7b085b`. Zdanie raportu "legenda z objasnieniem oznaczen jest w lewej kolumnie kazdego ekranu poranka" jest prawdziwe dla scen zrzutow (2 plytki), nie dla okna przy 125 % / 150 % (uwaga 9) |

## 4. Zakres plikow i zasady

- Pliki rundy 2 U1b (`git diff 1e89ff4 origin/e3/u1b`): `ui/ekran_rano.py`, `ui/mapa_rano.py`, `ui/motyw.py` (2 pary
  kontrastu), `ui/napisy_rano.py`, `ui/okno_excela.py` (2 wiersze), `testy/test_ui_poranek.py`, 8 PNG zrzutow, raport paczki,
  kopia raportu recenzenta - wszystkie z listy zlecenia p. 4. Poza lista: 0. Nietykalne: 0. `narzedzia/zrzuty_okna.py` bez zmian.
- `motyw.py`: tylko 2 nowe pary w `PARY_KONTRASTU` (bez zmiany barw) - w zakresie `ui/**`.
- ASCII: znaki spoza ASCII tylko w `napisy_rano.py` (teksty ekranu, plik istniejacy). Konce linii: 8 zmienionych plikow tekstowych
  - 0 bajtow CR (LF).
- Dane osobowe: brak (atrapa: kuwety fikcyjne, "Technik A"). Duze dane: 8 PNG, razem 1 220 060 B (bylo 1 164 931 B).
- Commity: 9 commitow U1b rundy 2 + scalenie; przedrostek "E3-U1b r2", stopka `Co-Authored-By: Claude Opus 5.5` w 9 z 9.

## 5. Do decyzji wlasciciela

1. (uzupelnia p. 5 pkt 2 rundy 1) Znaczenie barw oznaczen na mapie porannej jest teraz odwrotne niz w programie z `main`, ktory
   technicy znaja: w `main` gniazdo wybrane mialo obrys bialo-ciemny, a gniazda biezacej kuwety bialo-niebieski; teraz gniazda
   kuwety maja obwodke biala z ciemnym brzegiem, a wybrane - niebieski pierscien (zgodnie z SPEC p. 2 i z oknem wieczornym).
   Rozroznialnosc jest dobra; pytanie, czy technik przyzwyczajony do starego okna nie odczyta bialej obwodki jako "wybrane".
2. Pozostale pozycje p. 5 rundy 1 (lista kuwet przy otwartej pracy, liczba plytek w piecu - od niej zalezy D7, klawisze
   rozkladania na innych zakladkach, napisy z cytatow instrukcji) dalej otwarte - wykonawca ich nie rozstrzygal, tak jak kazalo
   zlecenie.
