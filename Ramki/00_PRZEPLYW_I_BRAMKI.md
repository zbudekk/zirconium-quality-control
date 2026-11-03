# 00 — Przepływ pracy, bramki i komunikaty (instrukcja dla właściciela)

Cel: pliki z sekcji 12.1 `plan_ramki_v2.md` bez błędów geometrii i spójne między sobą. Trzy role: **wykonawca** (Claude Opus 5.5, effort high, Claude Code), **recenzent** (Claude Fable 5.1, osobna sesja Claude Code), **właściciel** (Ty: bramki). Obie sesje pracują w tym samym folderze `<PC>\Desktop\Ramki`, więc między nimi przenosisz tylko krótkie komunikaty, nie pliki.

## 1. Pliki w folderze i ich rola

| Plik | Rola | Kto czyta | Kto edytuje |
|---|---|---|---|
| `plan_ramki_v2.md` | ŹRÓDŁO PRAWDY: geometria, decyzje, rejestr rozstrzygnięć R1–R47 | wszyscy | tylko Ty (po bramce) |
| `parametry.json` | jedyne źródło wartości liczbowych; tu wpisujesz pomiary | skrypt wykonawcy, recenzent | tylko Ty |
| `protokol_weryfikacji_v2.md` | sprawdzenia K‑01…K‑60 | wykonawca, recenzent | tylko Ty |
| `prompt_wykonawca.md` | pierwsza wiadomość sesji wykonawcy | Ty (wklejasz) | Ty (ścieżka Blendera) |
| `prompt_recenzent.md` | pierwsza wiadomość sesji recenzenta | Ty (wklejasz) | Ty (ścieżka Blendera) |
| `szablon_raport_wykonawcy.md`, `szablon_raport_recenzenta.md` | formaty raportów | obie sesje | nikt |
| `sesja2_pliki.md` | specyfikacja tła (sekcje 1–9); sekcja 0 NIE obowiązuje | obie sesje | nikt |
| `plan_ramki_v1.md`, `spec_3d_ramka.md`, `sesja1_plan.md`, `ramka_3d.html`, `animacja_ramki.html`, `wizualizacja_plan_v1.svg` | archiwum / podgląd 3D; NIE są wejściem dla sesji | nikt z sesji | nikt |
| `wyniki_v2/` | wszystko, co wytwarza wykonawca | recenzent (tylko odczyt) | wykonawca |
| `recenzja/` | skrypty, rzuty i raporty recenzenta | Ty, wykonawca (raporty) | recenzent |

## 2. Etapy, sprawdzenia i bramki

| Etap | Wykonawca wytwarza | Recenzent sprawdza (K‑xx) | Bramka po etapie |
|---|---|---|---|
| G0 | — | — | **G0 Zatwierdzenie źródła prawdy** (sekcja 3) |
| G1 | wiadomość „PLAN WYKONAWCY” (lista części, plan booleanów, 5 trudnych miejsc) | wiadomość „GOTOWOŚĆ RECENZENTA” (K‑xx etapu A, uwagi do sond, metoda sondy) | **G1 Zatwierdzenie planów obu sesji** |
| A | szkielet skryptu, JSON gniazd, 8 STL płytek, pokrywka, `kody_plytek.md`, raport A | K‑01…K‑04b (9 STL), K‑05…K‑22, K‑58 | **G2 Zaliczenie etapu A** (werdykt recenzenta) |
| B | wkładka, rama, blat, korpus W/P, bryły zastępcze, raport B | K‑01…K‑04b (6 STL), K‑23…K‑49 (bez K‑26, K‑41), K‑53 (pary), K‑54–K‑56 | **G3 Zaliczenie etapu B** |
| C | uchwyt kabli, `.blend`, rendery, arkusze, README, raport C | K‑01…K‑04b (1 STL), K‑52, K‑53 (wszystkie), K‑57, K‑59, K‑60 | **G4 Zaliczenie etapu C → pliki gotowe do wyceny** |
| POMIARY | po Twoich pomiarach: przebieg ALL, raport ALL | wszystkie K‑xx | **G5 Zaliczenie ALL → zamówienie** |

Kryterium zaliczenia etapu: raport recenzenta z werdyktem ZALICZONY (0 uwag B, 0 uwag P). Pętla poprawek: wykonawca poprawia wszystkie B i P, nowa iteracja, nowa recenzja. Limit: 5 iteracji na etap — po piątej nieudanej przerywasz i wklejasz do sesji 1 (tej, która to napisała) oba ostatnie raporty z prośbą o rozstrzygnięcie (najczęściej oznacza to błąd w planie lub protokole, nie w kodzie).

## 3. Bramka G0 — co zatwierdzasz PRZED startem (ok. 20 min czytania)

Przejrzyj w `plan_ramki_v2.md` sekcję 13 (R1–R47) i zatwierdź lub zmień pozycje oznaczone **[ZAŁOŻENIE]**. Najważniejsze (zmiana każdej z nich to jedna liczba w `parametry.json` i jedno zdanie w planie):

| Id | Decyzja | Domyślnie | Co zmienić, jeśli nie |
|---|---|---|---|
| R5 | Panel na dystansach 45 mm wkręconych w gwint panelu, podkładka 1 mm; wymaga gwintowanych otworów w panelu | TAK | jeśli panel nie ma gwintu: napisz do sesji 1 — trzeba zaprojektować inne mocowanie (nakrętki od strony diod) |
| R2/R16/R17 | nazwy plików, folder `wyniki_v2/`, sufiks `_v2` | TAK | wpisz własne nazwy w 12.1 i `file_suffix` |
| R4 | warianty n1–n6 do zamówienia, bazowe nie | TAK | — |
| R8 | otwory kołków wkładki ślepe (3,8) | TAK | `blat_pin_hole_depth` 4,1 = przelotowe |
| R11 | wtyk DC Bonnetu domyślnie w stronę przodu | TAK (do pomiaru #10) | wpisz pomiar |
| R13 | id gniazd rzędami od przodu, w rzędzie od prawej | TAK | — (program na laptopie czyta JSON, więc kolejność jest wyłącznie kwestią czytelności) |
| R15 | 3 rendery | TAK | — |
| R22 | font DejaVu Sans Bold | TAK | `font_name` |
| R23/R24/R26/R27 | żebra korpusu, daszki pełne, promienie 3/1, kolory | TAK | parametry `rib_*`, `vent_hood_*`, `fillet_*`, `color_*` |
| Z28/R45 | brak przycisku i czujnika gestu; przednia ścianka gładka z napisem | TAK (Twoja decyzja) | — |
| R31 | ścianki kieszeni DC 2 mm | TAK | `dc_pocket_wall` 2,5 (wtedy kieszeń o 1 mm węższa w świetle) |
| Z20/D6 | 24 + 2 gniazda wieczorna, 35 + 2 poranna, rzędami — **[R54, 1.11.2026]** zastąpione: 18 + 2 wieczorna, 31 + 2 poranna, rzędy przycięte do koła `socket_zone_r` 47 (pole skanowania przy obrocie = koło ø100, Z29); stożki znaczników w kole (`ev_/mo_marker_pos`), kieszenie magnesów w rogach; lista edycji `R54_wdrozenie_zmiany.md` | TAK (R54 zatwierdzone przez właściciela 1.11) | tylko przez sesję 1 (zmiana D6, `ev_/mo_rows` i K‑05) |

| Z27 | kieszeń DC 36 × 24 × 22 | TAK | `dc_pocket_*` |

Dodatkowo na G0: (1) wpisz ścieżkę i wersję Blendera do obu promptów; (2) jeśli masz już pomiary z sekcji 10 planu, wpisz je do `parametry.json` (`value` + `"status": "ZMIERZONE"`) — nie musisz, model powstaje na domyślnych; (3) utwórz puste foldery `wyniki_v2` i `recenzja` (nie musisz — sesje je utworzą).

Zatwierdzenie G0 = nie zmieniasz nic albo wpisujesz zmiany i mówisz o tym sesji 1 (ta rozmowa), żeby zaktualizowała plan v2 i protokół. Dopiero potem otwierasz sesje.

## 4. Jak uruchomić sesje

1. Otwórz nową sesję Claude Code w folderze `<PC>\Desktop\Ramki`, model **Opus 5.5**, effort **high**. Wklej całą treść `prompt_wykonawca.md` (od linii „Jesteś wykonawcą…”). Nazwij sesję „WYKONAWCA”.
2. Otwórz drugą sesję w tym samym folderze, model **Fable 5.1**. Wklej całą treść `prompt_recenzent.md` (od „Jesteś niezależnym recenzentem…”). Nazwij „RECENZENT”.
3. Poczekaj na „PLAN WYKONAWCY” i „GOTOWOŚĆ RECENZENTA”. **Bramka G1**: przeczytaj oba. Jeśli recenzent zgłosił uwagi do sond protokołu — wklej je do sesji 1 (ta rozmowa) jako „Uwagi recenzenta do protokołu: …”; sesja 1 poprawi protokół, a Ty powiesz obu sesjom „Protokół zaktualizowany, przeczytajcie ponownie”. Jeśli wykonawca w „5 trudnych miejscach” proponuje zmianę planu — to samo.
4. Zatwierdź: do WYKONAWCY komunikat **W‑1**.

## 5. Komunikaty między sesjami (kopiuj dosłownie)

| Kod | Do kogo | Treść | Kiedy |
|---|---|---|---|
| W‑1 | wykonawca | `PLAN ZATWIERDZONY. Zacznij etap A.` | po G1 |
| R‑1 | recenzent | `RECENZJA ETAPU A, iteracja 1. Raport wykonawcy: wyniki_v2/raport/raport_wykonawcy_A_iter1.md` | gdy wykonawca zgłosi „ETAP A GOTOWY, iteracja 1” |
| W‑2 | wykonawca | `RECENZJA: recenzja/raport_recenzenta_A_iter1.md — werdykt NIE ZALICZONY. Popraw wszystkie B i P, nowa iteracja.` | gdy recenzent da NIE ZALICZONY |
| R‑2 | recenzent | `RECENZJA ETAPU A, iteracja 2. Raport wykonawcy: wyniki_v2/raport/raport_wykonawcy_A_iter2.md` | po poprawce |
| W‑3 | wykonawca | `ETAP A ZALICZONY — zacznij etap B.` | gdy recenzent da ZALICZONY (bramka G2) |
| … | | analogicznie dla B (G3) i C (G4), z literą etapu i numerem iteracji | |
| W‑P | wykonawca | `POMIARY WPISANE do parametry.json (status ZMIERZONE). Wykonaj pełny przebieg ALL i raport ALL iteracja 1.` | po pomiarach (sekcja 10 planu) |
| R‑P | recenzent | `RECENZJA ETAPU ALL, iteracja 1. Raport: wyniki_v2/raport/raport_wykonawcy_ALL_iter1.md` | po W‑P |
| S‑1 | sesja 1 (ta rozmowa) | `Uwagi do planu v2 / protokołu od {wykonawcy|recenzenta}: …` + wklejony fragment | gdy któraś sesja zgłasza błąd planu, albo po 5 nieudanych iteracjach |

Gdy wykonawca zgłasza w raporcie „odstępstwo wymagające zatwierdzenia”: przeczytaj sekcję 4 jego raportu; jeśli zgadzasz się — wpisz zmianę do planu v2/`parametry.json` sam (jedna liczba) albo przez sesję 1, i napisz wykonawcy `ODSTĘPSTWO #k ZATWIERDZONE, wpisane do parametry.json/planu` lub `ODSTĘPSTWO #k ODRZUCONE, trzymaj się planu`. Recenzent ocenia odstępstwa w sekcji 5 swojego raportu — jego zdanie jest doradcze.

## 6. Co dostajesz do zatwierdzenia na każdej bramce (krótki materiał)

| Bramka | Dokument do przeczytania | Czas | Decyzja |
|---|---|---|---|
| G0 | sekcja 13 planu v2 (tabela R1–R47, kolumna „Typ” = [ZAŁOŻENIE]) + tabela w sekcji 3 tego pliku | 20 min | zatwierdzam / zmieniam R… |
| G1 | „PLAN WYKONAWCY” (1 wiadomość) + „GOTOWOŚĆ RECENZENTA” (1 wiadomość) | 10 min | W‑1 albo S‑1 |
| G2/G3/G4 | sekcja 0 (werdykt) i sekcja 3 (uwagi) raportu recenzenta; sekcja 4 raportu wykonawcy (odstępstwa) | 5–10 min | W‑3 (ZALICZONY) albo W‑2 (poprawki) albo decyzja o odstępstwie |
| G4 dodatkowo | `wyniki_v2/arkusze/arkusz_zamowienia.md` i 3 rendery (obejrzyj: czy to wygląda jak ramka z planu) | 10 min | wysyłka STL do wyceny u 2–3 usługodawców (bez zamawiania) |
| G5 | raport recenzenta ALL + arkusz z objętościami po pomiarach | 10 min | zamówienie |

## 7. Podmiana parametrów DO ZMIERZENIA (bez przerabiania całości)

1. Zmierz wg sekcji 10 planu v2 (20 pozycji, ok. 30 min).
2. W `parametry.json` dla każdej zmierzonej pozycji zmień `"value"` i `"status": "ZMIERZONE"`. Nie dodawaj kluczy, nie zmieniaj nazw. Jeśli `panel_standoff_l` (liczone) wypada poza 40/45/50 — zmień `panel_pad_h` tak, by trafić w dostępną długość, i wpisz to do planu (R28).
3. Komunikat W‑P do wykonawcy, potem R‑P do recenzenta. Wszystko powstaje od nowa z nowych wartości; żaden plik nie jest edytowany ręcznie.
4. Jeśli pomiar zmienia coś, czego parametr nie obejmuje (np. panel ma 6 otworów zamiast 4, albo złącza panelu w miejscu dystansu) — S‑1 do sesji 1: plan v2 → v3.

## 8. Kryteria końca całego procesu
- G5 zaliczone (raport recenzenta ALL: 0 B, 0 P).
- `arkusz_zamowienia.csv` z objętościami z siatek, 13 pozycji, ilości zgodne z R36.
- `wyniki_v2/README.md` pozwala odtworzyć wszystko jednym poleceniem (K‑59 ZAL).
- Lista D (drobne) zapisana jako `wyniki_v2/do_v3.md` (wykonawca tworzy na G4).

## 9. Co jest poza zakresem tego przepływu
Oprogramowanie ramki (Python na Pi), elektronika (sekcja 8 planu) i montaż (sekcja 9) — po dostawie części. Model 3D do oglądania (`ramka_3d.html`) odpowiada planowi v1 i spec_3d; nie jest aktualizowany do v2 w tym przepływie (można go zaktualizować osobnym zadaniem po G4, gdy geometria jest ostateczna).

## 10. Bramka G4b — weryfikacja końcowa „[cytat usuniety]” (wymóg właściciela)

Po zaliczeniu etapu C (G4) i ponownie po pomiarach (G5) uruchamiana jest trzecia, niezależna weryfikacja, inna metodą niż recenzent:
1. **Nowa, świeża sesja** (Fable 5.1, nie recenzent) dostaje tylko `plan_ramki_v2.md`, `parametry.json` i folder `wyniki_v2/` — bez protokołu i bez raportów. Zadanie: zbudować własną „kartę pasowań” z samych plików STL: dla każdej pary stykowej i pasowanej (płytka–wkładka, wkładka–blat, kołki–otwory, magnesy–kieszenie, dyfuzor–kieszeń, rama–panel, rama–bossy, blat–korpus, haczyki–kieszenie, dystanse–podkładki, Pi–bossy, gniazda–otwory, wtyk DC–kieszeń, pokrywka–płytka) zmierzyć w Blenderze luz nominalny z siatek (odległość między powierzchniami w 3 punktach) i porównać z planem (4.11) oraz z regułami 4.8 (0,2–0,3 ruchome, 0,1–0,15 wciskane, +0,3 na SLS). Wynik: tabela pasowań z luzem zmierzonym i werdyktem.
2. **Pełny zrzut wymiarów**: dla każdego STL — gabaryt i 10 najważniejszych wymiarów z `arkusz_wymiarow.md` zmierzonych niezależnie promieniami, porównanych z `parametry.json` (tolerancja 0,05).
3. **Symulacja montażu w `.blend`**: kolejność z sekcji 9 planu; dla każdego kroku test przecięć wstawianej części ze wszystkim, co już jest (nie tylko par statycznych) oraz test „drogi wsuwania”: część przesuwana po prostej z pozycji 20 mm wyżej do pozycji montażowej nie może przeciąć niczego po drodze (wkładka na kołki, płytka na kołek orientacyjny, blat na korpus z haczykami, pokrywka na płytkę).
4. Raport `recenzja_koncowa/raport_koncowy.md` z werdyktem; każda różnica > 0,05 mm względem planu lub luz poza regułą 4.8 = blokujące. Dopiero wynik „0 blokujących” otwiera wysyłkę do wyceny (G4) i zamówienie (G5).

## 11. Co można wydrukować samemu (FDM), a co zamówić — wstępna lista (do potwierdzenia na G4 objętościami z arkusza)

**[R56, 1.11.2026] Sekcje 11, 11a i 12 są historyczne (sprzed R50‑U1/U8, R49 i R55): rama dyfuzora i uchwyty kabli nie istnieją, wkładek gwintowanych nie ma, z żywicy nie drukujemy niczego. Obowiązuje dokument „Zakupy i druk — stanowisko kontroli cyrkonii” (co, gdzie, u kogo) i „Budowa ramki — decyzje i zamienniki” (powody i to, z czego zrezygnowano).**

Zasada właściciela: części widoczne zamawiamy (MJF/SLS PA12), części ukryte lub robocze można drukować samemu z PETG (nie PLA: pokrywka i płytka poranna widzą 40–70 °C).

| Część | Szt. | Widoczna? | Rekomendacja | Dlaczego |
|---|---|---|---|---|
| Korpus W/P | 2 | tak (pokaz) | ZAMÓWIĆ | największa część, gładki grafit, zatrzaski i kieszenie wymagają dokładności |
| Blat | 2 | tak | ZAMÓWIĆ | widoczny z góry, kołnierz 194 mm — FDM się wypacza |
| Płytki n1–n6 | 6 | tak (do skanera) | ZAMÓWIĆ | mat biały dla skanera, temperatura, gniazda ø3 i dołki ø2 — FDM daje zbyt duże błędy na stożkach |
| Wkładka gniazda | 3 | częściowo (biała rama na blacie) | ZAMÓWIĆ 2 + wydrukować 1 testową z PETG PRZED zamówieniem | tania (ok. 16 cm³), ale to ona decyduje o pasowaniu płytki; prototyp FDM sprawdza kołek, półki i kieszenie Halla |
| Pokrywka | 4 | nie (tylko przy przenoszeniu) | WYDRUKOWAĆ SAMEMU (PETG, 0,2 mm) | największa oszczędność: 4 × 30 cm³ ≈ 110–190 zł; zatrzaski 0,7 mm działają w PETG |
| Rama dyfuzora | 2 | nie (wewnątrz) | WYDRUKOWAĆ SAMEMU (PETG) | kołnierz 170 mm w FDM może się wypaczyć 0,3–0,5 mm, ale luz do panelu to 0,5 — dopuszczalne; alternatywnie zamówić (ok. 20 cm³) |
| Uchwyt kabli | 4 | nie | WYDRUKOWAĆ SAMEMU (dowolny materiał) | 6 cm³, bez pasowań |
| Prototypy pasowań | — | — | WYDRUKOWAĆ SAMEMU przed zamówieniem: 1 płytka (dowolna n), 1 wkładka, 1 pokrywka, narożnik blatu z kieszenią zatrzasku + fragment kołnierza z haczykiem (wykonawca może wyeksportować „próbkę zatrzasku” jako dodatkowy STL) | test realnych luzów za kilka złotych filamentu zanim pójdzie 1 500 zł do drukarni |

Szacunkowa oszczędność przy samodzielnym druku pokrywek, ram i uchwytów: 150–280 zł z ok. 1 100–1 900 zł (wariant najtańszy). Jeśli nie ma drukarki FDM: zamówić wszystko, a prototypy pasowań zlecić w tej samej drukarni jako tanie próbki SLS (wkładka + fragment zatrzasku) przed głównym zamówieniem.

## 12. Wkładki gwintowane — kto i jak

- **Decyzja właściciela (R49): BEZ wkładek gwintowanych.** Wkręty formujące gwint (PT 3,0 × 8 i PT 2,5 × 6 do tworzyw, albo zwykłe M3/M2,5) wkręca się bezpośrednio w otwory ø2,5 / ø2,1 w PA12. Pozostałe punkty tej sekcji są nieaktualne i zostają tylko jako alternatywa, gdyby gwint w PA12 się wyrobił (wtedy wkładka M3 w rozwierconym otworze ø4,0).
- **Narzędzia** (sekcja 6 planu): lutownica z regulacją temperatury + grot do wkładek (M3/M2,5), wkładki mosiężne radełkowane: M3 OD ~4,6 × 5,7 (otwór ø4,0), M2,5 OD ~4,0 × 4 (otwór ø3,4).
- **PA12 (SLS/MJF):** nylon topi się przy ~180 °C; grot 230–250 °C, wkładkę wciskać powoli i prostopadle, zatrzymać się 0,2 mm pod licem, odczekać 10 s bez ruchu; nadmiar wypchniętego materiału zeszlifować papierem 400. Ścianki wokół wkładek ≥ 2,0 mm (R48) właśnie po to, żeby nie pękły.
- **Alternatywa bez wtapiania (dopuszczona w 4.8):** wkręty M3/M2,5 bezpośrednio w otwór w PA12 (otwór pod gwintowanie: ø2,5 dla M3, ø2,05 dla M2,5) — trzyma dobrze w nylonie na 5–10 cykli montażu; wymagałoby zmiany średnic otworów w `parametry.json` (`insert_hole_m3`, `insert_hole_m25`) przed zamówieniem — decyzja na G4.
- **Części FDM z PETG:** wkładki wtapia się tak samo (grot 220–240 °C).
- Liczba wkładek na 2 ramki: M3 — 4 (bossy ramy w blacie) + 2 (słupki blatu) + 2 (uchwyty) = 8 na ramkę → 16; M2,5 — 4 (Pi) na ramkę → 8. Panel i dystanse: bez wkładek (gwint w mosiądzu).

## 13. Zapełnienie kontekstu sesji — co robić

- **Wykonawca:** patrz na miernik „Context” w jego sesji. Przy > 70 % albo gdy zaczyna się mylić (np. zapomina klucze parametrów, powtarza przebiegi) — zakończ jego turę i uruchom nową sesję Opus 5.5 (high) z `prompt_wykonawca_wznowienie.md`. Cały stan jest w plikach (`ramka_generator.py`, `wyniki_v2/`, raporty), nic nie ginie. Powiedz sesji nadzorującej, że wykonawca został wznowiony — ona będzie dalej słać komunikaty do nowej sesji.
- **Recenzent:** analogicznie, z `prompt_recenzent.md` + zdanie „przejmujesz po poprzednim recenzencie; jego skrypty i raporty są w `recenzja/`; kontynuuj od etapu …”.
- **Sesja nadzorująca (sesja 1):** jej stan to `00_PRZEPLYW_I_BRAMKI.md`, sekcja 13 planu v2 i raporty; nowa sesja nadzorująca dostaje: „Przejmujesz nadzór wg 00_PRZEPLYW_I_BRAMKI.md; ostatnia bramka zaliczona: G…; aktualny etap: …; sesje WYKONAWCA/RECENZENT są uruchomione, komunikaty wysyłaj po nazwie sesji”.

### 11a. Dostępne drukarki (informacja właściciela): FDM u kolegi, żywiczna (SLA/DLP) w firmie

**[R55, 1.11.2026 — decyzja właściciela: z żywicy nie drukujemy niczego.** Wszystko, co w tabeli niżej ma „[cytat usuniety]”, jest albo zlecane (PA12 w drukarni: płytki n1–n6), albo drukowane u kolegi na FDM z PETG (prototypy pasowań, płytka testowa n1 do testu skanera, tulejka DC, podkładki panelu). Tabela zostaje jako zapis historyczny; obowiązuje plan v2 D2/Z19 i `materials` w `parametry.json`.]

| Część | Technologia własna | Uwagi |
|---|---|---|
| Pokrywka ×4, rama dyfuzora ×2, uchwyt kabli ×4 | FDM, PETG (kolega) | zatrzaski i kołnierze potrzebują ciągliwości — nie żywica standardowa (krucha) |
| Prototyp wkładki + prototyp 1 płytki (test pasowania i kołka orientacyjnego) | żywica w firmie (dokładność ±0,05) | najlepszy test luzów 0,3 przed zamówieniem; nie ma znaczenia kolor |
| Test skanera (Z1: pole 100 × 100, znaczniki, dołki kodu) | żywica w firmie — matowa żywica modelowa (dentystyczna model resin jest matowa) | zrobić PRZED zamówieniem płytek: 1 płytka wieczorna n1 z żywicy, skan w Aidite, sprawdzić czy 96 × 96 wchodzi w całości i czy program widzi 3 stożki i dołki |
| Płytki wieczorne n1–n3 (prace zimne) | żywica w firmie — dopuszczone w spec 3.3, jeśli: pole robocze drukarki ≥ 100 × 100, żywica matowa (biała/kość słoniowa), sztywna | oszczędność ok. 170–300 zł; po teście skanera decyzja na G4 |
| Płytki poranne n4–n6 (40–70 °C) | ZAMÓWIĆ PA12 (albo żywica wysokotemperaturowa HDT ≥ 100 °C, jeśli firma ją ma) | standardowa żywica modelowa się odkształci |
| Korpus, blat, wkładki ×2 | ZAMÓWIĆ PA12 | widoczne / nośne / za duże na żywicę |

Wkładki gwintowane w częściach żywicznych: nie wtapiać (żywica pęka) — w tym projekcie części żywiczne (płytki, prototypy) i tak nie mają wkładek.
