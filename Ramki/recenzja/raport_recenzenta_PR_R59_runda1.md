# Raport recenzenta PR R59 - runda 1 (subsesja R59-R)

Data: 2026-11-15. Recenzent: swieza subsesja R59-R (Fable 5.2), niezalezna od wykonawcow.
Stan recenzowany: HEAD `f54fd42`, PR #12 (`bp/r59` -> `main`), baza `origin/main` = `4cc6090`; zakres: `git diff origin/main...HEAD`
(452 pliki: 386 A, 66 M; 115 280 linii dodanych, 1 608 usunietych), bez plikow binarnych.
Metoda: czytanie diffu i plikow w HEAD (Git Bash), male skrypty tekstowe na MSI (Python 3.12, biblioteka standardowa + numpy).
Nie uruchamiano pytest, node ani Blendera; PC nie byl uzyty (do rozstrzygniecia uwag wystarczyly kod, logi koordynatora i rachunek).
Na MSI liczone byly tylko: sumy SHA-256, porownania tekstowe, geometria 2D ukladu z `parametry.json` i jeden raster 192 x 192 (uwaga 4).
Cytaty z plikow z polskimi znakami sa w tym raporcie zapisane bez znakow diakrytycznych.

## 0. Werdykt

**do scalenia po poprawkach D** - B 0 / P 0 / D 12.

Bledow blokujacych ani powaznych nie znalazlem. Listy plikow, sumy SHA-256, liczby ukladu, parametry wklejone w HTML,
testy i straznik ukladu sa spojne z `parametry.json` i z decyzjami G0 / G1. Uwagi D1, D7, D8 (dokumenty i README) warto
poprawic PRZED budowa PDF i pakietu, bo trafia do PDF i do ZIP; pozostale mozna poprawic w tej samej rundzie albo zapisac
do raportu koncowego jako znane. Scalenie do `main` dopiero po PDF i R59-K (patrz pkt 5 - to nie sa uwagi do diffu).

## 1. Uwagi (B = blokujacy, P = powazna, D = drobna)

| Nr | Waga | Wlasciciel | Plik:linia | Co jest zle | Oczekiwane |
|---|---|---|---|---|---|
| 1 | D | R59-P | `Ramki/stanowisko/README.md:43-45, 76-78` | Dwa bloki przykladowych polecen sprzed R59: `porownaj --skan dane/syntetyczne_P2/... --plytka okragla_wieczorna`, `metryki_P2.py` i `metryki_P3a.py --skany dane/syntetyczne_P2 dane/syntetyczne_P3a` bez `--sufiks-ukladu _r54`. Na istniejacych zestawach sprzed R59 koncza sie teraz "PLYTKA NIE PASUJE" albo "zaden z N skanow nie pasuje do ukladu"; nowa sekcja tego samego pliku (linie 57-64) mowi, ze te zestawy wymagaja `_r54`. | Dopisek przy obu blokach (zestawy sprzed R59: `--plytka ..._r54` / `--sufiks-ukladu _r54`) albo poprawione polecenia. |
| 2 | D | R59-P | `Ramki/stanowisko/narzedzia/metryki_P2.py:128-130` | Skan odrzucony przez straznika jest tylko wypisany ("POMINIETY") i znika z mianownika; w JSON wyniku nie ma licznika ani listy (w `metryki_P3a.py` jest `uklad_niezgodny`). Falszywy alarm straznika obnizylby liczbe skanow bez sladu w pliku metryk. | Lista / licznik `uklad_niezgodny` w JSON i w podsumowaniu, jak w `metryki_P3a.py`. |
| 3 | D | R59-P | `Ramki/stanowisko/stanowisko/plate.py:303-312`, `porownaj.py:149-152`, `ui_test.py:375-382`, `opisy_modulow/plate.md:31` | (a) Kazda reszta > 0,3 mm przy >= 3 dopasowanych stozkach daje `NiezgodnyUklad` "plytka nie pasuje do wybranego ukladu" - takze wtedy, gdy jeden z trzech "stozkow" jest falszywy albo zabrudzony (przed R59 komunikat ogolny "stozki nie pasuja"); `plate.md` opisuje jako granice tylko przypadek < 3 stozkow. (b) Przy starym lokalnym `ustawienia.toml` (bez `*_r54`) komunikat brzmi "nie pasuje do zadnego ukladu z listy - sprawdz plytke i skan" i nie podpowiada, ze w `[plytki]` brakuje ukladow `*_r54`; a pierwsze prawdziwe skany beda wlasnie na starych plytkach (G0). | (a) jedno zdanie w `plate.md`; (b) podpowiedz w komunikacie, gdy `uklady_pasujace` jest puste i w `[plytki]` nie ma zadnego klucza `_r<NN>` ("dopisz 4 wiersze z ustawienia.przyklad.toml"). Zadanie czlowieka jest juz zapisane - to poprawka wygody, nie blad. |
| 4 | D | R59-P | `plate.py:63-71, 631-640`; `ui_test.py` (brak przelacznika); `opisy_modulow/plate.md` | Warstwa 2 straznika (mapa gniazd): (a) okno nie ma odpowiednika `--bez-straznika` - przy falszywym alarmie na prawdziwym skanie technik nie przejdzie dalej; progi sa z 17 projektow na skanach syntetycznych (K1 plytki zgodnej max 47,75 przy progu 150). (b) Nieopisana granica: dwa uklady o TYCH SAMYCH stozkach, z ktorych jeden rozni sie tylko podzialem rynienki. Odlozony wariant D3-b (`R59_szkice/parametry_wariant_W-b-D3b.json`) ma stozki i gniazda okragle rowne W-b (sprawdzone skryptem); moj rachunek na rastrze 0,5 mm z regulami stref z `plate.py`: plytka W-b z modelem D3-b K1 = 0, K2 ok. 31 mm2 (< 50); plytka D3-b z modelem W-b K1 ok. 46 mm2 (< 150), K2 = 0 - zadna warstwa ich nie odrozni (kontrola rachunku: pusta R54 z modelem W-b K1 ok. 366, K2 ok. 253 - rzad wielkosci jak w raporcie R59-P). `plate.md:31` opisuje tylko uklady o tych samych stozkach I tych samych gniazdach. | Dopisac (b) do granic w `plate.md` i do listy "do sprawdzenia na prawdziwym skanie (P3b)"; przy ewentualnym D3-b: inny numer plytki albo przesuniety stozek. (a) - przelacznik w oknie albo w `ustawienia.toml` przy naprawie okna (P3a-2). |
| 5 | D | R59-U | `Ramki/narzedzia/weryfikuj_uklad_R59.js:198-200` | Reguly domyslne przyjmuja 2 rynienki w jednym rzedzie (D3-b) jako OK (tylko "UWAGA" o otworach, kod wyjscia 0), choc G0 = D3-a. Plik parametrow z rynienka podzielona przeszedlby test T1 bez przelacznika (stan w `00_NADZOR_STAN.md`: warianty D3-b "kod 0, 0 linii BLAD"). | Po G0 domyslnie dokladnie 1 rynienka (albo przelacznik `--d3=a|b` i zapis w naglowku). Dzis lapia to testy programu (`RYNIENEK_G0 = 1` w `test_uklad_r59.py`) i sondy K-08 generatora - dlatego D. |
| 6 | D | R59-A | `Ramki/ramka_generator.py:4228-4236` (znana uwaga D2 recenzenta siatek - ocena) oraz `Ramki/wyniki_v2/raport/sha256_stl_po_R59_iter1.txt` | Teksty rejestru odstepstw maja wpisane liczby ukladu ("rynienka ukladu P-e lezy w y -35,3", "gniazdem fi 12,5 ... w (31; -19,55)", "naroznik w promieniu 37,5 / 38,2"). Sprawdzilem: 3 z 3 zgodne z `parametry.json` (37,53 / 38,19 z rachunku). To teksty informacyjne, sprawdzen K-xx nie dotykaja - oceniam jako D, zostaje. Druga rzecz: lista `sha256_stl_po_R59_iter1.txt` jest bajtowo rowna liscie iter2 (wkladka f4196fbc), a `raport_wykonawcy_R59_iter1.md:51` podaje dla tego przebiegu de0d26c5 - lista nie oddaje stanu przebiegu 1 (historia jest uczciwie opisana w `R59_wdrozenie_zmiany.md` pkt 6). | Bez zmiany generatora w tej paczce (SHA d3b56f63 = recenzowany); przy nastepnej zmianie ukladu liczby w tekstach liczyc z P. Lista iter1: usunac albo dopisac jedno zdanie w `R59_wdrozenie_zmiany.md`. |
| 7 | D | R59-D | `Ramki/Stanowisko kontroli cyrkonii - plan wdrozenia v2.md:243, 568`; `Ramki/Budowa ramki - decyzje i zamienniki.md:163` | "Wieczorem ... rynienki wymaga wtedy 8 z 17" (2 prace nie mieszcza sie w fi 15). Zrodlo: `R59_propozycja_ukladu.md:42, 48` (regula katalogu, jedno losowanie). Pomiar R59-P daje inaczej: `stanowisko/opisy_modulow/katalog.md:15` i raport `R59_2026-11-14.md` pkt 7 - 6 mostow + 1 trzonowiec zawsze, a drugi trzonowiec wchodzi w fi 15 w 13 z 20 prob. Dwa zrodla w tej samej paczce, dokument dla wlasciciela cytuje mniej dokladne. | "7-8 z 17" albo dopisek "(jedna z dwoch wchodzi w fi 15 w 13 z 20 prob)" - w trzech miejscach, przed budowa PDF. |
| 8 | D | R59-D | `Ramki/Stanowisko kontroli cyrkonii - plan wdrozenia v2.md:118, 647` | Linie zmieniane przez R59: (118) "Trzy stozki w naroznikach pozwalaja programowi wyrownac skan" - od R54 stozki leza w kole gniazd, a linia 647 tego samego dokumentu mowi "przesuniete z naroznikow do kola gniazd"; (647) "Trzy stozki sa jedynym elementem, ktory program mierzy na plytce" - od R59 program porownuje tez mape gniazd z modelem (straznik). | Poprawic oba zdania przed budowa PDF ("trzy stozki znacznikow"; "po stozkach wyrownuje, a uklad gniazd porownuje z modelem"). |
| 9 | D | R59-D | `Ramki/narzedzia/buduj_pdf_R59.cmd:92-141` | Wszystkie galezie bledu koncza sie `goto koniec`; skrypt zawsze konczy kodem 0 (takze "BLAD: interpreter ... nie dziala"). Koordynator uruchamial go przez ssh - niepowodzenia nie widac po kodzie wyjscia, tylko w tekscie. | Zmienna bledu + `exit /b 1` po `pause` w galeziach bledu. |
| 10 | D | koordynator | `Ramki/00_NADZOR_STAN.md:156, 157, 165`; `Ramki/R59_odbior/baseline.md:69` | (a) :165 "288 = 288 kluczy" - kluczy jest 287 (`R59_wdrozenie_zmiany.md:86`, `wyniki_model_R59/sprawdzenie_chrome_R59.json` "kluczy": 287, moje porownanie 287 = 287). (b) :156 "6 kluczy ukladu" i :157 "7/7 kluczy = warianty" - moje porownanie: 6 kluczy (W-b 2, P-e 4). (c) 46 linii sekcji R59 ma konce LF w pliku CRLF (teraz 132 CRLF + 48 LF; na `main` 132 + 2). (d) `baseline.md:69` "w T8 podac --numer 3 / --numer 6 jawnie" - nieprecyzyjne: wg raportu R59-P `--numer` wolno podac tylko w `porownaj`, w `synth` zmienia losowanie (skrypt `t6_t10_program.py` robi to poprawnie). | Poprawic liczby i zdanie; konce linii sekcji R59 ujednolicic przy najblizszej edycji. |
| 11 | D | R59-P (testy) | `Ramki/stanowisko/testy/test_straznik.py:156, 171, 212`; `test_uklad.py:76-78` | Testy biora lokalny `ustawienia.toml` (`UST.wczytaj_ustawienia()`) i wymagaja w nim 8 ukladow. Na maszynie ze starym `ustawienia.toml` (pulpit PC, laptop) czesc testow bedzie czerwona do czasu dopisania 4 wierszy. Wzorzec istnial przed R59 (`test_wszystkie_plytki_z_ustawien`), teraz obejmuje wiecej testow. | Zapisac w raporcie koncowym przy zadaniu czlowieka "dopisac 4 wiersze" (albo testy straznika na `PLIK_PRZYKLADU`). |
| 12 | D | propozycje - pliki NIEZMIENIONE przez R59 albo sekcje pominiete; nie blad paczki | (a) `Ramki/mail_aidite_zapytanie.md:11`; (b) `Ramki/plan_ramki_v2.md:778-779, 787`; (c) `Ramki/stanowisko/testy/test_ui.py:126-137` | (a) "plytke 96 x 96 mm z 24-35 koronami i do 2 mostow" - nieaktualne juz od R54. (b) Sekcja 11 planu (plik zmieniany przez R59): objetosci "62 / 61", razem ok. 1 033 cm3, 935-1 655 zl - szacunek sprzed R54; R59-A opisal to uczciwie w `R59_wdrozenie_zmiany.md` pkt 4, ale w samym planie nie ma dopisku. (c) Test pominiety (`skip`): bierze `dane/syntetyczne_P2` i `prawda.plytka`; po zdjeciu `skip` da "plytka nie pasuje" (zestaw w ukladzie R54). | (a) "18-23 koron i 1 most" przy najblizszej edycji; (b) jedno zdanie "[R59] obowiazuje arkusz: 1 008 cm3, 907-1 613 zl"; (c) przyrostek `_r54` przy naprawie okna. |

## 2. Wyniki punktow 1-5 (liczniki)

### Pkt 1 - listy plikow

- `git diff --name-status origin/main...HEAD`: 452 pliki. Przypisanie do list z planu (sekcje 6-12, pkt 2.2) i plikow dopisanych decyzja koordynatora:
  R59-A 255, R59-U 77, R59-P 59, koordynator 18, R59-M 18, R59-D 11 + 3 dopisane (`narzedzia/buduj_plan_wdrozenia.py`, `R59_arkusz_zamowienia.md/.csv`), R59-B 11. **Poza listami: 0.**
- `Ramki/stanowisko/raporty/testy_krawedz/`: 0 plikow. `ustawienia.toml`, `dane/`: 0. `match.py`, `inspect.py`: nie ma ich w diffie.
- Pliki `.stl` w diffie: 20, wszystkie w `Ramki/stanowisko/modele_plytek/**` (10 M + 10 A w `*_r54`); poza dozwolonymi katalogami: 0.
- `00_PRZEPLYW_I_BRAMKI.md`: 1 linia (wiersz Z20/D6) - zgodnie z lista R59-A.
- Kopie: `archiwum/wyniki_v2_przed_R59_2026-11-14/**` = `origin/main:Ramki/wyniki_v2/**` 188 z 188 (identyczne obiekty git) + 1 nowa lista SHA;
  `modele_plytek/*_r54` = `origin/main:modele_plytek/<typ>` 14 z 14; `modele_plytek/<typ>/uklad.json` = `wyniki_v2/json` 4 z 4.
- Ostatni commit `f54fd42` rozni sie od stanu testowanego przez koordynatora (`bcbd2ea`) tylko plikami `R59_odbior/**` i plikiem stanu (12 plikow).

### Pkt 2 - spojnosc liczb

- Wlasny rachunek z `parametry.json` (skrypt, obie plytki): wieczorna 18 + 1 (6 x fi 12, 12 x fi 15; rynienka 60 x 15), poranna 23 + 1
  (20 x fi 12,5, 3 x fi 15; rynienka 50 x 13); max promien obrysu 45,927 / 46,412; strefa 43,50 / 45,00; min scianka 3,0000 / 3,0000 (id 1-3);
  stozki: promien 44,30 / 44,20 / 44,43 i 44,21 / 44,25 / 44,48, do gniazd 3,52 / 3,23 / 3,19 i 3,45 / 3,02 / 3,48, boki 58,17 / 74,95 / 87,68
  i 55,94 / 79,36 / 86,53; kwadrat dolek-gniazdo 8,27 / 8,61, dolek-stozek 6,01 / 11,03; okragla: krawedz 4,07 / 3,59, stozek-krawedz 3,07 / 3,02,
  sciecie 4,59 / 4,81, dolki 4,80 / 31,86 / 5,27 i 3,55 / 2,09 / 5,07; naroznik cyfry 46,85 / 46,49.
  = tabela w `R59_wdrozenie_zmiany.md` pkt 0, `plan_ramki_v2.md` D6 / 4.1a / 4.11, `protokol_weryfikacji_v2.md` K-05 / K-08 / K-09 / K-13 / K-16 / K-61 / K-62,
  opisy w `parametry.json`, `stanowisko/opisy_modulow/uklad.md`. Roznic: 0. Rachunki skrajnych promieni w tabelach D6 (13 wierszy) przeliczone recznie: 13 z 13.
- JSON ukladu <-> `parametry.json` (gniazda, kolejnosc id, `d_bottom`, stozki, dolki, rynienka; 4 pliki `wyniki_v2/json` + 4 `modele_plytek`): 52 sprawdzenia, 0 niezgodnych.
- SHA-256: policzone 21 STL (`wyniki_v2/stl`, poza gitem), 4 JSON, 28 plikow `modele_plytek`. Pary "nazwa pliku - suma" w dokumentach i raportach:
  **273 zgodne, 2 niezgodne** - obie to znany wariant wkladki de0d26c5 w raportach przebiegow posrednich (`raport_wykonawcy_R59_iter1.md:51`,
  `raport_wykonawcy_SPRAWDZ_iter10.md:41`; opisane). W tym: `R59_wdrozenie_zmiany.md` 16 z 16, "Zakupy i druk" 17 z 17, `wyniki_v2/README.md` 25 z 25,
  log recenzenta 25 z 25, `test_uklad_r59.py` 28 z 28 (14 R59 + 14 `_r54`). STL `modele_plytek` = `wyniki_v2/stl` 10 z 10.
- HTML: blok `params` w `ramka_3d.html` i w `wyniki_model_R59/ramka_3d_v3_R59.html` = `parametry.json` (tekst identyczny, 287 = 287 kluczy, 0 roznic);
  blok `uklad` w `animacja_ramki.html` = `parametry.json` (11 z 11 kluczy); kopia animacji w `wyniki_model_R59` bajtowo rowna zrodlu.
  Maski: `EV_WORK` 5 wpisow o dlugosciach 1 / 6 / 5 / 4 / 3 = `ev_rows`; `EV_RED` [[1,2],[3,2]] wskazuje gniazda z praca; 9 z 18 gniazd z praca.
  Odwolania sieciowe: animacja 0; model offline - lista CDN zostaje w kodzie jako galaz zapasowa (stan sprzed R59), pomiar R59-M: 0 zadan poza plikiem.
- Arkusz zamowienia przeliczony: 10 pozycji 1 008,05 cm3, 907-1 613 / 1 216-2 161 zl; z okraglymi 1 107,05 cm3, 996-1 771 / 1 305-2 320 zl; grupy
  178,98 / 179,84 / 99,00 cm3 - zgodne z `R59_arkusz_zamowienia.md/.csv`, `wyniki_v2/arkusze` i trzema dokumentami (ceny wierszy 161-286, 162-288, 89-158, 44-79 / 45-79).
- Liczby raportu R59-P <-> logi koordynatora: pytest 250 / 3 / 0 (`T5_pytest.log`), metryki 221 / 248, 219 / 245, 659 / 704, 554 / 594 (`T2_T3_T7_skrot.txt`),
  weryfikator 103 OK (`T1_weryfikator.log`), recenzja 475 sprawdzen - bez rozbieznosci. Liczby testow w nowych plikach: 33 i 28 (policzone z parametryzacji).

### Pkt 3 - liczby starego ukladu w miejscach biezacych

- Przeszukane 25 zmienionych plikow opisujacych stan biezacy (13 wzorcow: 18 + 2, 31 + 2, 7 x fi 9, 5 x fi 15, 18 x fi 7,5, 7 x fi 10, 6 x fi 12,5,
  dwie rynienki, objetosci 59,31 / 60,87 / 49,01 / 50,56 i 59,30 / 60,86 / 48,99 / 50,55, fi 9 / 7,5 / 10, stare pozycje stozkow i rynienek):
  332 trafienia = 225 w kontekscie historii ("bylo", "dawniej", R54, `_r54`) + 107 obejrzanych recznie (podkladki fi 9, stopki fi 10, nowe wartosci,
  tabele "bylo -> jest"). **W miejscach biezacych: 0.**
- Stare SHA plytek / JSON: 46 trafien, wszystkie w kontekscie historii (sekcja R57 pliku stanu 6, "Zakupy i druk":216 "tylko do rozpoznania starego pliku" 8,
  `SHA_MODELI_R54` 14, punkt odniesienia 18). **W miejscach biezacych: 0.**
- Poza skanem wzorcow znalezione recznie: uwagi 1, 7, 8, 12b.
- Pliki niezmienione przez R59 (sledzone, poza archiwum i pakietem): 52 z trafieniami; 51 to historia (raporty i narzedzia R54 / R57, modele R53 / R54,
  plany v1, sesje z 31.10), 1 opisuje stan biezacy (`mail_aidite_zapytanie.md`, uwaga 12a); pozycje 12b i 12c znalezione recznie.

### Pkt 4 - dane osobowe

- `<MSI>\kod\qc\Prace_test`: 37 pozycji (foldery + pliki), 36 slow >= 4 liter po odjeciu slow technicznych.
- Dodane linie diffu (119 565 linii z naglowkami, takze nazwy plikow): 55 trafien, 3 rozne slowa - wszystkie techniczne (sprawdzone skrotem
  wobec listy slow technicznych, bez wypisywania): 34 w `wyniki_model_R59/ramka_3d_v3_R59.html` (wklejona biblioteka three.js), 21 w kopiach
  `archiwum/**` plikow sprzed R59. **Trafien nazwisk / nazw zlecen: 0.**
- Opisy commitow (`git log origin/main..HEAD`, 24 commity): 0 trafien. Autor "Michal Budek": tylko linia 3 trzech dokumentow (i ich kopie w archiwum).
- Logi `R59_odbior/logi/*`, raporty: projekty tylko jako skroty 16 znakow.
- Ograniczenie: slowa krotsze niz 4 litery nie byly szukane.

### Pkt 5 - ASCII, znaki sterujace, konce linii

- Nowe pliki tekstowe: 160; ASCII 86; nie-ASCII 74, wszystkie w wyjatkach: `archiwum/**` 44, `R59_szkice/parametry_wariant_*.json` 16,
  `wyniki_v2/**` 6, `modele_plytek/*_r54/uklad.json` 4, `R59_arkusz_zamowienia.md/.csv` 2, HTML modelu 2. **Poza wyjatkami: 0.**
- Znaki sterujace (poza TAB / LF / CR) w 212 plikach tekstowych diffu: **0 plikow**.
- Konce linii: dla 66 plikow M `git diff --numstat` = `--numstat --ignore-cr-at-eol` (66 z 66) - **masowej zmiany CRLF: 0 plikow**.
  Mieszane konce: `00_NADZOR_STAN.md` (uwaga 10c) i 2 kopie raportow R57 w archiwum (stan sprzed R59).
- Skladnia: 36 plikow `.py` (poza archiwum) parsuje sie (ast), 49 plikow `.json` parsuje sie.

## 3. Pkt 6 - kod

### 6a. Straznik ukladu i program

Przeczytane w calosci: diff `plate.py`, `porownaj.py`, `ui_test.py`, `uklad.py`, `synth.py`, `ustawienia.py`, `ustawienia.przyklad.toml`,
`metryki_P3a.py`, `metryki_P2.py`, `katalog_projektow.py`, `rzut_z_gory.py`; nowe `straznik_R59.py`, `pojemnosc_R59.py`, `test_straznik.py`, `test_uklad_r59.py`;
diffy 8 zmienionych plikow testow.

| Przypadek | Ocena |
|---|---|
| Sciezka bez niezgodnosci (stary uklad liczy sie jak przed zmiana) | `przypisz_znaczniki` - refaktoryzacja bez zmiany wyniku (te same permutacje, ta sama kolejnosc sprawdzen); straznik tylko czyta `Ps2`, nie zuzywa `rng`, nie zmienia `T`. `match.py` / `inspect.py` poza diffem; w `ustawienia.przyklad.toml` tylko 7 linii w `[plytki]`. Potwierdzenie pomiarem: T8a 4 z 4. |
| Rozne uklady (R59 <-> R54) | Wlasny rachunek Kabscha na 8 plikach `uklad.json`: reszta miedzy ukladami roznych typow / wersji >= 2,34 mm (prog 0,3); R59 <-> R54 tego samego typu 3,15 (wieczorna) i 8,93 (poranna) - jak w raporcie. Warstwa 1 wystarcza. |
| Kwadrat <-> okragla tego samego ukladu | Reszta 0,00, gniazda identyczne - straznik nie rozrozni; opisane w `plate.md`. Rozstrzyga numer z dolkow (ostrzezenie, zachowanie sprzed R59). |
| Plytka pusta / pelna | K1 dziala na pelnej, K2 maleje; liczniki R59-P 0 z 520 falszywych, 240 z 240 wykrytych. Uwaga do interpretacji: w pomiarze "sam straznik gniazd" K2 zawiera ok. 15 mm2 od stozkow drugiego ukladu, wiec K2 min 54 nie jest zapasem dla ukladow o wspolnych stozkach - decyduje K1 (>= 410). |
| Skan przyciety do pola fi 100, maly wycinek | Piksel bez punktow nie jest dowodem (`dane`); test `maly` w `test_straznik.py`. |
| Mniej niz 3 stozki | `BladWyrownania` ogolny, jak przed R59. |
| 3 stozki, jeden falszywy | Uwaga 3a. |
| Straznik wylaczony | `wyrownaj(straznik=False)`: brak `uklad_zgodny` w `jakosc`, `porownaj` zwraca `None`; `tabela`, `mapa_png`, okno, `metryki_P3a` sprawdzaja `is False`. Poprawne. |
| Stary `ustawienia.toml` bez `_r54` | Program dziala, `uklady_pasujace` puste; uwaga 3b, uwaga 11. `SCHEMAT` celowo bez nowych wymaganych kluczy - opisane jako odstepstwo 1. |
| Wszyscy wolajacy `wyrownaj` / `porownaj` | 6 miejsc (porownaj, okno, 3 narzedzia) - kazde obsluguje `NiezgodnyUklad` / `uklad_zgodny`. Uwaga 2 dla `metryki_P2.py`. |
| `uklad.wczytaj`: `nazwa` = klucz zamiast pola `plate` | Zmiana celowa i opisana; `synth.poranna` przez `typ_plytki` (bez tego `poranna_r54` dostalaby skurcz wieczorny) - test jest. |

Testy: `test_straznik.py` i `test_uklad_r59.py` nie sa tautologia (oczekiwania z `parametry.json`, sumy SHA wpisane, uklad-hybryda dla warstwy 2);
nowych `skip`: 0. Stare testy: 8 plikow, oczekiwan oslabionych 0; 3 testy zawezone do `_r54` (`test_scianki_3mm_takze_okragle_vs_rynienki_i_poranna`,
`test_praca_poza_gniazdem_i_podwojna`, `test_zgrubne_obroty_i_ocena`) - dwa pierwsze maja odpowiedniki R59 w `test_uklad_r59.py`, trzeci jest
opisany jako odstepstwo 2 raportu R59-P (sam RANSAC, seed 0) - przyjmuje.

### 6b. Generator

Diff 42+ / 18-: `OBJ_ORIENT` (60 / 60 / 49 / 50 przy tolerancji +-30 %), teksty rejestru, etykieta K-05, docstring, komentarz, nowa
`odstepstwa_informacyjne_R59` (liczby z `ev_rows` / `mo_rows`). Zadne sprawdzenie K-xx nie zostalo zmienione ani oslabione. Liczby w tekstach: uwaga 6 (D).

### 6c. Narzedzia

- `weryfikuj_uklad_R59.js` (calosc): egzekwuje kolo 47, strefe +-45, scianke >= 3 dla wszystkich par (takze stozki miedzy soba), symetrie kazdego
  wpisu, kwadraty narozne, stozki (promien, gniazda, dolki, magnesy, krawedzie, boki >= 5, zapas Kabscha), dolki i cyfre kwadratu, wyciecie D,
  okragla (krawedz, sciecie, dolki, cyfra). Rzad mieszany, powtorzone y, powtorzone x: obsluzone (powtorzone y i x = BLAD). Luka: uwaga 5.
  Wynik na `parametry.json` (log koordynatora): kod 0, 103 OK - liczby rowne mojemu rachunkowi.
- `uklad_kolo_R59.js` (775 linii): przejrzany naglowek, wejscie / wyjscie, limit czasu; algorytmu przegladu nie recenzowalem - jego wynik sprawdzaja
  niezaleznie weryfikator, generator i recenzja z siatek. Pliki wariantow W-b i P-e = `parametry.json` w 6 z 6 zmienionych kluczy.
- `arkusz_zamowienia_R59.py`: objetosci z raportu generatora, kontrola SHA z `R59_wdrozenie_zmiany.md`, blad przy niezgodnosci - bez uwag.
- `buduj_pdf_R59.cmd`: kontrole wstepne dzialaja (wzorce starych JSON: 7 i 18 trafien w archiwum, 0 w nowych); uwaga 9.
- `buduj_plan_wdrozenia.py` (`opis_gniazd`): odmiana poprawna (18 gniazd, 23 gniazda, 1 rynienka); liczby z tego samego JSON co rysunek.
- `zbuduj_model_offline.js`, `rysuj_szkice_R59.js`: bez uwag (brak odwolan sieciowych, kontrola bloku `uklad`).
- `R59_odbior/t4_pomiar_siatek.py`: sprawdza to, co deklaruje; liczniki z logu zgadzaja sie z rachunkiem (258 gniazd, 1 056 + 1 968 + 2 040 = 5 064 sondy).
  Kontrola odwrotna jest tu waska (102 punkty, 444 pominiete) - pelna jest u recenzenta siatek.
- `R59_odbior/t6_t10_program.py`: T8a generuje skan bez `--numer` (poprawnie); T8b sprawdza tylko warstwe 1 (uklady roznia sie stozkami) - plik
  stanu nie twierdzi wiecej; T9 ma kryterium zmienione po pierwszym przebiegu (2 FAIL z winy testu sa w `T6_T10_program.log`, powtorka w
  osobnym logu) - uczciwie, do tabeli w raporcie koncowym.

### 6d. HTML

Patrz pkt 2. Bez uwag.

## 4. Pkt 7 i 8 - dokumenty i uczciwosc raportow

- Trzy dokumenty: opis zmiany zgodny z programem (dwa uklady, straznik "ostrzega" = wynik bez gniazd i komunikat, jeden most na plytke, okragla =
  te same gniazda co kwadrat, stare plytki opisac, ramka swietlna nie odrozni ukladu - jako decyzja otwarta nr 10). Daty poza linia 3: 0
  (przeszukane wzorcem dat, miesiecy i tygodni; pozostale trafienia to czestotliwosc czynnosci sprzed R59). Nazwiska poza linia 3: 0. Liczby maja
  zrodlo (`parametry.json`, arkusz, `R59_wdrozenie_zmiany.md`, `R59_propozycja_ukladu.md`, raport recenzenta); wyjatki: uwagi 7 i 8.
- `stanowisko/raporty/R59_2026-11-14.md`: liczniki zamiast samych procentow, 10 odstepstw wypisanych, odchylka -3,1 pkt z analiza i bez strojenia progow;
  spojny z logami koordynatora. `R59_wdrozenie_zmiany.md`: 6 przebiegow z wynikami, wariant wkladki, 5 odstepstw.
  `raport_recenzenta_R59_iter1.md`: 475 sprawdzen, kontrola czulosci metody, bledy wlasne skryptow wypisane.
  `baseline.md` i logi: pierwsze przebiegi nieudane sa zachowane (pytest bez git 165 / 3 / 1, T9 3 z 5, T12 proba 1). Nic nieudanego nie pominieto.
- Sprzecznosci miedzy raportami: uwaga 7 (8 z 17 vs 7 + 1 w 7 z 20 prob) i uwaga 10 (liczby kluczy w pliku stanu). Innych nie znalazlem.

## 5. Informacje dla koordynatora (nie sa uwagami do diffu)

- W galezi `Ramki/Ramki_pakiet/` zawiera nadal pliki plytek R57 pod tymi samymi nazwami (n1 = 515d32d3...), a trzy `.pdf` w `Ramki/` sa sprzed R59 -
  to znane (R59-K i PDF czekaja). Dokument "Zakupy i druk" odsyla do `Ramki_pakiet/`, wiec scalenie przed R59-K daloby na `main` pakiet sprzeczny
  z dokumentem. W R59-K rozstrzygnac tez `03_Druk_wlasny/PETG_FDM/ramka_plytka_wieczorna_n1_v2_TEST_SKANERA.stl` (stary uklad).
- Poprawki uwag 1, 7, 8 zmieniaja pliki, ktore ida do PDF / pakietu - zrobic przed ich budowa. Poprawki kodu (uwagi 2, 3, 9) nie zmieniaja wynikow
  pomiarow; po nich wystarczy powtorka `pytest`.

## 6. Czego nie sprawdzono i dlaczego

- Geometrii STL - zgodnie ze zleceniem (R59-B zaliczony); skryptow `recenzja/sprawdz_R59*.py` merytorycznie - tylko skladnia i przeszukania.
- Niczego nie uruchamialem (pytest, node, Blender, okno): MSI nie ma pakietow, a zadna uwaga nie wymagala przebiegu na PC. Wnioski o zachowaniu
  straznika pochodza z czytania kodu, rachunku na `uklad.json` i logow koordynatora.
- Algorytmu przegladu w `uklad_kolo_R59.js`; tresci 6 generowanych raportow `wyniki_v2/raport/*.md` poza sumami SHA; plikow binarnych (PNG, JPG, `.blend`, PDF w archiwum) poza listami.
- PDF i pakietu (nie istnieja); testow T0, T3c, T11, T13, T14 koordynatora.
- Dane osobowe: tylko slowa >= 4 liter z nazw w `Prace_test`.
