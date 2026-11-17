# Plan sesji R59: nowy uklad gniazd plytek (wiecej gniazd fi 15, jedna rynienka)

Data: 2026-11-14. Autor planu: sesja qc (rozpoznanie 14.11; w projekcie nic nie zmieniono).
Adresat: sesja KOORDYNATORA paczki R59. Koordynator uruchamia subsesje, pilnuje bramek, a na koncu SAM testuje wynik.
Numer rewizji: **R59** (R58 jest w dokumentach R57 zarezerwowany dla wkladki i pokrywki plytki okraglej).

Spis: 0 zlecenie - 1 fakty - 2 role i zasady - 3 decyzje wlasciciela (G0) - 4 przebieg - 5 etap 0 - 6..13 subsesje -
14 testy koncowe koordynatora - 15 scalenie i raport - 16 ryzyka - 17 wzor zlecenia - 18 prompt startowy.

## 0. Zlecenie wlasciciela (14.11.2026) i zakres

1. Plytka poranna: mniej malych gniazd (fi 7,5), w ich miejsce wieksze.
2. Plytka poranna: gniazda fi 15 (dzis najwieksze to fi 12,5).
3. Plytka wieczorna: wiecej gniazd fi 15 (dzis 5 sztuk).
4. Obie plytki: usunac jedna z dwoch rynienek (gniazdo na most).
5. Pytanie o dwa mniejsze mosty w jednej rynience - dzis program na to nie pozwala (pkt 1.6); rozstrzyga decyzja D3.

Wlasciciel NIE podal liczb docelowych (ile gniazd ktorej srednicy). Dlatego pierwsza subsesja (R59-U) liczy warianty,
a wlasciciel wybiera na bramce G0. Bez G0 nie wolno zmieniac `parametry.json`.

Poza zakresem: korpus, blat, wkladka, pokrywka, tulejka, podkladki (pliki STL maja zostac BAJTOWO bez zmian), progi
`[match]` / `[inspect]`, wykrywanie ukruszen na krawedzi (galaz `bp/fable-5-2`), wkladka i pokrywka okragla (R58),
program ramki na Raspberry Pi.

## 1. Fakty sprawdzone 14.11.2026 (stan wyjsciowy)

### 1.1 Repo i katalogi
- Repo `mbuasm/qc`, `origin/main` = `4cc6090`. Kod ramek: `Ramki/`. Program stanowiska: `Ramki/stanowisko/`
  (w tym repo pliki sledzone zwykle; zagniezdzonego `Ramki/stanowisko/.git` w glownym katalogu NIE dotykac).
- `.gitignore`: `*.stl` poza `Ramki/Ramki_pakiet/**` i `Ramki/stanowisko/modele_plytek/**`; `Prace_test/` poza gitem.
  Worktree z `origin/main` NIE ma wiec `Ramki/wyniki_v2/stl/*.stl` ani `Ramki/stanowisko/dane/`.
- Pelna kopia z duzymi plikami: MSI `<MSI>\kod\qc` (21 STL w `Ramki\wyniki_v2\stl`, `Ramki\stanowisko\dane\`
  z `syntetyczne_P2`, `syntetyczne_P3a`, `katalog.json`; `Prace_test\` - 16 pozycji) oraz PC `<PC>\Desktop\Ramki`.
- W glownym katalogu MSI sa niezatwierdzone prace innych sesji: `CLAUDE.md` (zasady PC z 12.11),
  `Ramki/plan_sesji_testowych_krawedz_2026-11-06.md`, `Ramki/handout_ubytki_0_02mm_2026-11-06.md`,
  `Ramki/stanowisko/raporty/testy_krawedz/`, `Ramki/stanowisko/raporty/dyskusja_ubytki_0_02mm_2026-11-06.md`. Nie dotykac.
- Galaz `bp/fable-5-2` (niescalona, 54 pliki, tylko `Ramki/stanowisko/raporty/testy_krawedz/**`) - bez kolizji z R59,
  o ile R59 nie rusza tego katalogu.
- `gh auth status` na MSI: **token niewazny** (konto `mbuas`). Bez odnowienia nie bedzie PR (etap 0 pkt 3).

### 1.2 Zrodlo ukladu gniazd
- Jedyne zrodlo liczb: `Ramki/parametry.json`. Uklad: `ev_rows` (wieczorna) i `mo_rows` (poranna), ok. linii 60-75.
  Srednica gniazda jest brana z pola `d` rzedu; klucze `ev_socket_d_s/m/l`, `mo_socket_d_s/m/l` wystepuja w generatorze
  tylko na liscie wymaganych kluczy, wiec fi 15 w porannej nie wymaga nowego klucza.
- Stan R54: wieczorna 18 gniazd + 2 rynienki (7 x fi 9, 6 x fi 12, 5 x fi 15; rynienki 60 x 15 w y = -31,5 i +31,5);
  poranna 31 + 2 (18 x fi 7,5, 7 x fi 10, 6 x fi 12,5; rynienki 50 x 13 w y = -28 i +35,95).
- Od ukladu zaleza w `parametry.json`: `ev_marker_pos`, `mo_marker_pos` (3 stozki znacznikow fi 5 x 3),
  `code_dimples_round` (dolki kodu plytek okraglych, per typ), `number_pos_round` (cyfra okraglych, per typ),
  `ev_/mo_trough_l`, `ev_/mo_trough_w`, `ev_/mo_trough_hole_pitch`, `trough_hole_count` (4, wspolne), opisy kluczy.
- Ograniczenia geometrii (plan `plan_ramki_v2.md` D6, Z20, Z29, 4.1, 4.1a, 4.11; protokol K-05, K-09, K-16, K-61, K-62):
  obrysy gorne gniazd, rynienek i stozkow w kole `socket_zone_r` = 47 od srodka; strefa x, y w [-45, 45]; scianka
  miedzy obrysami >= `socket_wall_min` = 3; rzedy symetryczne wzgledem x = 0; srodek stozka znacznika na promieniu
  <= 44,5 i >= 3 od gniazd; dolki okraglych: promien <= 44, >= 3 od gniazd, >= 1,5 od stozkow; scianka sciecie
  orientacyjne - obrysy >= 3; cyfra okraglych w kole 47, >= 3 od gniazd; kwadrat: dolki kodu w (-45; -36/-33/-30/-27),
  gniazdo - dolek >= 3, wyciecie D i cyfra w rogu przod-prawo, kwadraty narozne 13 mm bez gniazd.
  Uwaga z recenzji R54: uklad nie ma zapasu (scianki 3,000; kolo porannej 46,93 / 47) - kazda korekta tylko skryptem.

### 1.3 Generator (`Ramki/ramka_generator.py`, 4495 linii, Blender 5.2, `import bpy`)
- Uruchomienie: `blender.exe -b -P ramka_generator.py -- --etap A|B|C|ALL|SPRAWDZ --iter n --raport ETYKIETA [--bez-renderow]`.
- 4 typy plytek (`TYPY_PLYTEK`, ok. linii 837): wieczorna, poranna, okragla_wieczorna, okragla_poranna. Okragle biora
  rzedy typu bazowego (K-05 h: lista `sockets` identyczna z kwadratem) - zmiana rzedow zmienia WSZYSTKIE 4 typy.
- `wczytaj_uklad` (ok. linii 950-990): `wyniki_v2/json/uklad_gniazd_<typ>.json` jest tworzony z rzedow TYLKO, gdy go
  nie ma; gdy istnieje, aktualizowane sa tylko pola pochodne, a lista `sockets` zostaje stara. Wniosek: przed
  przebiegiem 4 pliki JSON przeniesc do archiwum.
- Zaszyte w kodzie: objetosci orientacyjne `OBJ_ORIENT` (linie 60-62: plytka wieczorna 62, poranna 61, okragle 49 / 51),
  nazwy `plytka_wieczorna_n1` i `plytka_poranna_n4` (zlozenie K-53, rendery, arkusz wymiarow - ok. 10 miejsc),
  wyrazenie `plytka_(wieczorna|poranna)_n(\d)` (ok. linii 3347) - numer jednocyfrowy. Zmiana numerow plytek (D5-B)
  wymaga zmian kodu.
- Liczby oczekiwane K-05 sa brane z `ev_rows` / `mo_rows` (ok. linii 2014), nie ze stalych.
- Znana pulapka: po przebiegu `ALL` plik `ramka_wkladka_v2.stl` potrafi miec inny znak zera jednej normalnej (siatka
  identyczna). Do pakietu idzie plik o SHA `f4196fbc...` z archiwum (procedura z R55 / R57).

### 1.4 Numery plytek
- Kod 4-bitowy n = A + 2B + 4C + 8D. Zajete: n1-n3 (kwadrat wieczorna), n4-n6 (kwadrat poranna), n8 (okragla
  wieczorna), n9 (okragla poranna). Wolne: 7, 10-15.
- Wg zapisow z 2.11 fizycznie zamowiono plytki ze STARYM ukladem: po 1 kwadratowej wieczornej i porannej oraz okragle
  n8 i n9 (zamowienie planowane na 3.11). Potwierdzic w G0 (D4), bo od tego zalezy, czy program musi znac oba uklady.

### 1.5 Program stanowiska
- Uklad jest dana, nie kodem: `stanowisko/modele_plytek/<nazwa>/uklad.json` + `plytka_n<N>.stl` (okragle takze
  `plytka_bazowa.stl`). Nazwy folderow sa w `ustawienia.przyklad.toml [plytki]` i w `SCHEMAT` w `ustawienia.py`
  (nieznany klucz = blad) oraz na listach wyboru `--plytka` (`synth`, `porownaj`) i w oknie (`ui_test.py`).
- Wybor plytki jest reczny (`--plytka` / lista w oknie). Numer z dolkow sluzy tylko do ostrzezenia, gdy numeru nie
  ma w `uk.numery` (`plate.py` ok. linii 480). Stara plytka o tym samym numerze nie da zadnego ostrzezenia.
- Testy z zaszytymi wartosciami starego ukladu: `test_uklad.py:8` (18+2, 31+2), `:34` (gniazdo 8 = fi 9), `:50`
  (okragle 18+2 / 31+2); `test_edge_uklad.py:89` (20 gniazd), `:96` (rynienka w y = +-31,5), `:158`, `:176` (fi 9);
  `test_synth.py:99` (20 - 3 pustych); `test_plate.py:77-79` (punkt (0; 22,5), gniazdo 20 = rynienka);
  `test_edge_synth.py:52`, `:66` (fi 7,5 w porannej), `:134` (rynienka w = 13); `test_katalog.py:108` (l = 50), `:116`.
- Stan testow z raportu P3a (2.11): `pytest testy` 167 passed, 2 skipped. Metryki P3a (przebieg 5): 40 skanow,
  wyrownanie 40/40 (max 0,0137 mm), top-1 na zestawie P2 271/271. To jest punkt odniesienia; koordynator odtwarza go
  w etapie 0.

### 1.6 Mosty i rynienki w programie
- Praca szersza niz `PROG_MOSTU_MM` = 20 mm trafia tylko do rynienki (`synth.py:45`, `kandydaci_gniazd`). Jedna
  rynienka = jeden most na plytke.
- Jedna praca na gniazdo: `synth` zdejmuje rynienke z listy wolnych po osadzeniu jednej pracy; `plate.py` (ok. linii
  410-415) oznacza dwa fragmenty w jednym gniezdzie jako `podwojny` (fiolet = blad); wyniki `porownaj` i okna sa
  kluczowane numerem gniazda (`stan[gid]`); prace blizej niz 0,5 mm zlewaja sie w jeden fragment.
- Rynienka ma 4 otwory fi 3 (rozstaw 12 / 10 mm, liczba wspolna `trough_hole_count`). Krotka rynienka (podzial jednej
  na dwie) nie pomiesci 4 otworow w rozstawie 12 - wymaga zmiany parametrow i kodu generatora.

### [usunieto w kopii: opis dostepu ssh]
- Konto `michal\<konto-PC>` (bez administratora). Pisze tylko w `<PC-katalog>` (dzis pusty) i wlasnym profilu.
  `<PC>\Desktop\Ramki` jest tylko do odczytu. Polecenie trafia do `cmd.exe`.
- Blender 5.2.3 LTS dziala pelna sciezka: `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"`
  (`blender` nie jest w PATH).
- Python 3.12.10: `<PC>\AppData\Local\Programs\Python\Python312\python.exe` (`python` i `py` nie sa w PATH).
  Z `PYTHONPATH=<kopia programu>;<PC>\Desktop\Ramki\stanowisko\.venv\Lib\site-packages` importuja sie:
  numpy 2.5.4, scipy, trimesh 5.2.0, open3d 0.20.0, PySide6; `pytest` jest.
- Sa: `node` (`C:\Program Files\nodejs`), `git`, `tar`, Chrome (`C:\Program Files\Google\Chrome\Application\chrome.exe`).
- `ramka_generator.py` i `parametry.json` na PC maja to samo SHA-256 co repo (`09268b14...`, `b7b52942...`).
- NIE MA `<PC>\Desktop\Prace_test` (projekty sa na MSI: `<MSI>\kod\qc\Prace_test`).
- Budowa PDF (`narzedzia/buduj_plan_wdrozenia.py`: markdown-it, bs4, playwright + Chromium, pdfplumber, reportlab,
  pypdf) NIE dziala na koncie `<konto-PC>` (brak `markdown_it`, `playwright`, `pdfplumber`; katalog przegladarek
  Playwright konta `<uzytkownik>` = odmowa dostepu) ani na MSI (brak `markdown_it`, `bs4`, `playwright`, `pdfplumber`). Patrz D7.

### 1.8 MSI
- Python 3.12 (`C:\Program Files\Python312`) ma tylko numpy, pypdf, reportlab; BRAK scipy, trimesh, open3d, pytest;
  brak `node`. Wniosek: wszystkie obliczenia, testy programu, Blender i node ida na PC. Na MSI tylko edycja plikow,
  git, male skrypty tekstowe.

## 2. Role, modele i zasady wspolne

### 2.1 Modele (decyzja wlasciciela 14.11.2026)
- **Koordynator: Fable 5.2, effort xhigh ("extra").** Model i effort ustawia czlowiek PRZED pierwsza wiadomoscia
  (nowa sesja startuje na modelu domyslnym; sesja na zlym modelu = powtorka od zera). Koordynator potwierdza model
  narzedziem `get_session` w pierwszej odpowiedzi.
- **Kazda subsesja: Fable 5.2, effort high** - narzedzie Agent: `model: "fable"`, `effort: "high"`,
  `run_in_background: true`, typ `general-purpose`. Dotyczy takze recenzentow (dla tej paczki zastepuje wczesniejsza
  zasade D38 "ponowne recenzje na Opus"). Gdyby narzedzie nie przyjelo modelu albo effortu - stop i pytanie do
  wlasciciela, bez zamiany na inny model.
- Skill `koordynator` (wykonawcy `claude -p` w VM) tej paczki NIE dotyczy; z niego obowiazuja tylko: kontrola kolizji
  przed kazdym startem, zgoda czlowieka na `main` / MSI / wydanie, krotki raport.

### 2.2 Podzial pracy
- Koordynator nie pisze kodu ani dokumentow projektu. Jego pliki: `Ramki/00_NADZOR_STAN.md` (sekcja R59), ten plan
  (kopia w galezi), `Ramki/R59_odbior/**` (dowody testow koncowych), `Ramki/R59_raport_koncowy.md`, commity, PR.
- Subsesja pracuje tylko na swojej liscie plikow (sekcje 6-13). Plik spoza listy = `POTRZEBUJE: <plik>, <powod>` w
  odpowiedzi; koordynator dopisuje go tylko, gdy zadna rownolegla subsesja go nie ma.
- Subsesje NIE robia `git add/commit/push`, nie zmieniaja galezi. Commit robi koordynator po przyjeciu etapu
  (temat <= 60 znakow, np. `R59-A: uklad gniazd w parametrach i generatorze`).
- Recenzent zawsze w SWIEZEJ subsesji (nigdy wznowiony wykonawca, nigdy wznowiony poprzedni recenzent). Poprawki po
  recenzji = wznowienie TEGO SAMEGO wykonawcy (`SendMessage`) z numerowana lista uwag. Limit: 3 iteracje na etap,
  potem stop i decyzja wlasciciela.
- Rownolegle najwyzej 3 subsesje; przed kazdym startem na MSI >= 3 GB wolnego RAM. Na MSI zadnych pomiarow w Pythonie.

### 2.3 Galaz i katalogi robocze
- Galaz paczki = galaz worktree koordynatora (sesja bp `qc` / `r59`: `bp/r59` od `origin/main`). Jeden PR (draft) do
  `main`. Wszystkie subsesje pracuja w TYM SAMYM worktree koordynatora (listy plikow rozlaczne), bez wlasnych worktree.
- Duze pliki na MSI: `Ramki/wyniki_v2/stl/` w worktree (ignorowane przez git).
- PC: katalog paczki `<PC-katalog>\r59\`, podkatalogi:
  - `Ramki\` - kopia robocza generatora (pisze tylko R59-A, potem R59-K),
  - `uklad\` - R59-U, `recenzja\` - R59-B, `program\` - R59-P, `model\` - R59-M, `baseline\` i `odbior\` - koordynator,
  - `Prace_test\` - kopia projektow z MSI (dane z nazwiskami; kasowana na koncu paczki).
- Zrodlem prawdy jest galaz w repo. Z `<PC>\Desktop\Ramki` bierze sie wylacznie srodowisko (`.venv`) i duze
  pliki nieobecne w repo (STL, archiwa, dane syntetyczne). Przed uzyciem pliku z PC porownac SHA z repo.

### 2.4 Zasady PC (do kazdego zlecenia, ktore liczy)
- [usunieto w kopii: opis dostepu ssh]
  (`tar`) i uruchomic, linia polecen max 8 KB; polecenie dluzsze niz ok. 8 min w tle z postepem do pliku.
- [usunieto w kopii: opis dostepu ssh]
  (pliki zatwierdzone) albo `tar -cf - <pliki> | ssh ... "tar -xf - -C ..."`; z powrotem
  [usunieto w kopii: opis dostepu ssh]
- Kopia z pulpitu: `robocopy <PC>\Desktop\Ramki <PC-katalog>\r59\Ramki /E /XD dane .git .pytest_cache __pycache__ /NFL /NDL /NP`
  (kod wyjscia robocopy 0-7 = sukces, 1 = skopiowano - to nie blad).
- Wzor `run.cmd` (subsesja kladzie go w swoim podkatalogu):
  ```
  @echo off
  cd /d <PC-katalog>\r59\<kat>\Ramki\stanowisko
  set PYTHONUTF8=1
  set PYTHONDONTWRITEBYTECODE=1
  set PYTHONPATH=<PC-katalog>\r59\<kat>\Ramki\stanowisko;<PC>\Desktop\Ramki\stanowisko\.venv\Lib\site-packages
  <PC>\AppData\Local\Programs\Python\Python312\python.exe %*
  ```
  Testy: `run.cmd -m pytest testy -q -p no:cacheprovider`.
- PC ma 32 watki i 32 GB RAM: pomiary dzielic na wiele rownoleglych procesow, BEZ limitow watkow i procesow.
- Na PC niczego nie instalowac; nie pisac poza `<PC-katalog>`; odmowa zapisu to zamierzona bariera - nie obchodzic.
  PC nie odpowiada: 3 proby co 60 s, potem raport z tym, co jest, i prosba do wlasciciela o wlaczenie.
- Zmian w `<PC>\Desktop\Ramki` dokonuje tylko czlowiek (zadanie na koniec paczki).

### 2.5 Zasady tresci
- Nowe pliki: polski bez znakow diakrytycznych; tworzone narzedziem Write. Istniejace dokumenty z diakrytykami
  (`plan_ramki_v2.md`, trzy dokumenty stanowiska, raporty) zostaja w swoim stylu.
- Dane osobowe: nazwy plikow i folderow w `Prace_test` zawieraja nazwiska. W raportach, logach, commitach i
  odpowiedziach tylko skrot projektu (16 znakow SHA-256), nigdy nazwa pliku ani folderu zlecenia.
- Uczciwosc wynikow: liczniki (43/50), nie same procenty; kazde odstepstwo opisane; testu nieudanego nie pomijac.
- Przed kazda edycja pliku zrodla prawdy kopia do `Ramki/archiwum/<nazwa>_przed_R59_2026-11-14.<ext>`.
- Nic nie kasowac z `Ramki_do_wgrania/`, z Dysku Google ani z archiwum.

## 3. Decyzje wlasciciela - bramka G0 (jedno zbiorcze pytanie po R59-U)

Koordynator zadaje je RAZ, po raporcie R59-U, razem ze szkicami wariantow (wyslac pliki wlascicielowi). Domyslne =
zalecenie autora planu.

| Id | Decyzja | Opcje | Domyslnie |
|---|---|---|---|
| D1 | Uklad plytki wieczornej | wariant W-a / W-b / W-c z `R59_propozycja_ukladu.md` (liczby gniazd per srednica, ktora rynienka zostaje) | W-b |
| D2 | Uklad plytki porannej | wariant P-a / P-b / P-c (ile fi 7,5 zostaje; ile fi 10 / 12,5 / 15; ktora rynienka zostaje) | P-b |
| D3 | Rynienka | (a) jedna dluga, 1 praca; (b) podzielona na dwie krotkie - 2 krotkie mosty, kazda ma wlasny numer gniazda, zmiana parametrow otworow i kodu generatora; (c) funkcja programu "kilka prac w rynience" - osobna paczka pozniej | (a); (b) tylko gdy wlasciciel chce klasc 2 mosty |
| D4 | Stare plytki fizyczne (uklad R54: kwadrat n1 / n4, okragle n8 / n9) | (TAK) beda jeszcze skanowane - program zachowuje stary uklad jako `*_r54` i dostaje straznika ukladu; (NIE) wycofane - stary uklad tylko w archiwum | TAK |
| D5 | Numery plytek nowego ukladu | (A) te same numery n1-n6, n8, n9; stare plytki opisane i odlozone; (B) nowe numery z wolnych 7, 10-15 (wymaga zmian generatora: numery dwucyfrowe, zaszyte n1 / n4; wolnych kodow jest 7, a plytek 8) | A |
| D6 | Co i ile zamawiamy w nowym ukladzie | kwadrat / okragla / oba; liczba sztuk (`quantities`) | bez zmian ilosci; decyzja o zamowieniu po odbiorze |
| D7 | Budowa PDF | (a) czlowiek uruchamia na PC gotowy `buduj_pdf_R59.cmd` na swoim koncie; (b) zgoda na `pip install` 4 pakietow i Chromium na MSI | (a) |
| D8 | Dysk Google | (a) wgrywa czlowiek wg `DO_WGRANIA_NA_DRIVE_...R59.md`; (b) koordynator przez przegladarke po osobnej zgodzie | (a) |

Osobne zgody pozniej: G1 (akceptacja wynikow przed pakietem) i G2 (scalenie do `main` po testach koncowych).
Odpowiedz wlasciciela koordynator zapisuje doslownie w `00_NADZOR_STAN.md` (sekcja R59) i w `R59_wdrozenie_zmiany.md`.

## 4. Przebieg

| Kod | Kto | Co | Start po | Rownolegle z | Szac. czas |
|---|---|---|---|---|---|
| E0 | koordynator | kolizje, galaz, gh, punkt odniesienia, kopie na PC | - | - | 45 min |
| R59-U | subsesja | studium ukladu, 3 warianty na plytke, szkice | E0 | - | 1,5-2,5 h |
| G0 | wlasciciel | decyzje D1-D8 | R59-U | - | - |
| R59-A | subsesja | parametry, generator, STL, JSON, plan, protokol | G0 | - | 3-5 h |
| R59-B | subsesja swieza | recenzja z siatek | R59-A | R59-P | 2-3 h |
| R59-P | subsesja | program: modele, testy, straznik, dane, metryki | R59-A | R59-B | 4-6 h |
| R59-D | subsesja | 3 dokumenty, arkusz zamowienia, skrypt PDF | R59-B ZALICZONY | R59-M, R59-P | 2 h |
| R59-M | subsesja | model 3D i animacja | R59-B ZALICZONY | R59-D, R59-P | 1,5 h |
| G1 | wlasciciel | akceptacja wynikow, PDF (D7) | B, P, D, M | - | - |
| R59-K | subsesja | pakiet, SHA256SUMS, ZIP, instrukcja | G1 i PDF | - | 1 h |
| T | koordynator | testy koncowe T0-T14 (sekcja 14) | R59-K | R59-R | 1,5-2 h |
| R59-R | subsesja swieza | recenzja PR | R59-K | T | 1 h |
| G2 | wlasciciel | zgoda na scalenie | T i R59-R | - | - |
| E9 | koordynator | scalenie, stan, raport, zadania czlowieka | G2 | - | 30 min |

Po kazdym etapie: commit, wpis w `00_NADZOR_STAN.md` (co zrobione, SHA, co dalej - tak, zeby nowy koordynator mogl
przejac), krotka wiadomosc do wlasciciela (<= 10 linii). Jesli R59-B da NIE ZALICZONY po rozpoczeciu R59-P i zmienia sie
STL albo JSON - R59-P powtarza kopie modeli i przebieg testow (wpisac to w jej zlecenie).

## 5. Etap 0 - koordynator (zanim ruszy jakakolwiek subsesja)

1. **Model:** `get_session` - potwierdz Fable 5.2 xhigh. Inny model = stop, wiadomosc do wlasciciela.
2. **Kolizje:** `git fetch`; `git worktree list`; `git branch -r`; `gh pr list` (po pkt 3); lista sesji (`ListAgents`).
   Koliduje: inna sesja zmieniajaca `Ramki/parametry.json`, `Ramki/ramka_generator.py`, `Ramki/stanowisko/**` (poza
   `raporty/testy_krawedz`), dokumenty, pakiet; inna sesja liczaca w `<PC-katalog>`. Kolizja = stop i propozycja.
3. **GitHub:** `gh auth status`. Token niewazny: NIE `gh auth refresh`; logowanie kodem urzadzenia
   (`echo | GH_BROWSER=echo gh auth login -h github.com -p https -w > <plik>` w tle, 8-znakowy kod dla wlasciciela na
   github.com/login/device). Do czasu logowania praca idzie lokalnie; `git push` sprawdzic osobno.
4. **Galaz i plan:** worktree czysty, galaz od `origin/main`. Skopiuj ten plan do `Ramki/` w galezi i zatwierdz
   (`R59: plan sesji`). Dopisz w `00_NADZOR_STAN.md` sekcje `## R59 (14.11.2026, wlasciciel) - nowy uklad gniazd`.
5. [usunieto w kopii: opis dostepu ssh]
   porownanie SHA `ramka_generator.py`, `parametry.json`, `protokol_weryfikacji_v2.md`, `plan_ramki_v2.md` na PC z
   galezia - roznica = nadpisz plikami z galezi (`git archive`) i zanotuj.
6. **Projekty:** `tar` katalogu `<MSI>\kod\qc\Prace_test` do `<PC-katalog>\r59\Prace_test`
   (tylko pliki STL projektow; bez wypisywania nazw w logu).
7. **Punkt odniesienia (stary uklad, PRZED zmianami) - wyniki do `<PC-katalog>\r59\baseline\` i skrot do
   `Ramki/R59_odbior/baseline.md`:**
   - `pytest testy -q` na programie z `origin/main`: liczba passed / skipped / failed, czas;
   - SHA-256 21 plikow `wyniki_v2/stl` i 4 `wyniki_v2/json` (PC) = `Ramki_pakiet/SHA256SUMS_2026-11-02_R57.txt`
     tam, gdzie plik jest w pakiecie;
   - `blender ... --etap SPRAWDZ --iter 90 --raport BASELINE` na kopii: oczekiwane 0 NIE (potwierdza, ze srodowisko
     konta `<konto-PC>` daje ten sam wynik co dotad; przy bledzie renderow powtorzyc z `--bez-renderow` i zanotowac);
   - `metryki_P3a.py` na `syntetyczne_P2` + `syntetyczne_P3a` z pulpitu (ok. 11 min): tabela jak w
     `stanowisko/raporty/P3a_przekazanie.md` pkt 1;
   - po jednym skanie na kazda z 4 plytek: `synth --ile 1 --seed 7001` + `porownaj --prawda` -> zachowaj `_wynik.json`
     (mapa gniazdo -> projekt -> status) do testu T8.
   Rozjazd punktu odniesienia z raportami z 2.11 (np. inna liczba testow) = zanotuj i idz dalej na liczbach zmierzonych.
8. Wiadomosc do wlasciciela: "[cytat usuniety]" + ewentualne przeszkody; start R59-U.

## 6. Subsesja R59-U - studium ukladu (przed G0)

**Cel:** dla kazdej plytki 3 policzone i sprawdzone warianty ukladu, z ktorych wlasciciel wybierze jeden.
**Pliki (tylko nowe):** `Ramki/R59_propozycja_ukladu.md`, `Ramki/narzedzia/uklad_kolo_R59.js`,
`Ramki/narzedzia/weryfikuj_uklad_R59.js`, `Ramki/R59_szkice/*` (SVG / PNG, `parametry_wariant_<id>.json`).
**Nie zmienia:** `parametry.json` ani niczego innego.
**Czyta:** `parametry.json` (sekcja plytki), `plan_ramki_v2.md` (Z1, Z20, Z29, Z30, D6, D11, 4.1, 4.1a, 4.11),
`protokol_weryfikacji_v2.md` (K-05, K-09, K-16, K-61, K-62), `narzedzia/uklad_kolo_R54.js`,
`narzedzia/weryfikuj_uklad_R54.js`, `R57_wdrozenie_zmiany.md` (jak dobrano dolki i cyfre okraglych),
`stanowisko/stanowisko/synth.py` (`kandydaci_gniazd`, `PROG_MOSTU_MM`, wspolczynnik 0,55), `stanowisko/stanowisko/katalog.py`,
`<MSI>\kod\qc\Ramki\stanowisko\dane\katalog.json` (cechy 17 projektow bez nazw).

Kroki:
1. `uklad_kolo_R59.js` = kopia narzedzia R54 rozszerzona o: dokladnie 1 rynienke (przod albo tyl), wariant z rynienka
   podzielona na dwie krotkie w jednym rzedzie (do D3-b), fi 15 w porannej, dowolny zestaw srednic w rzedach,
   przesuniecie calego bloku w y, rzedy w szachownice. Uruchamiac na PC (`node`), katalog `<PC-katalog>\r59\uklad`.
2. `weryfikuj_uklad_R59.js` = narzedzie R54 rozszerzone o: scianke gniazdo - dolek kwadratu (4 dolki, takze D),
   kwadraty narozne, dolki i cyfre plytek okraglych (`code_dimples_round`, `number_pos_round`), scianke do sciecia
   orientacyjnego (K-61 f), promien dolkow <= 44, trojkat znacznikow (pkt 4). Wynik: linie z "OK" / "BLAD", kod wyjscia.
3. Warianty (kazdy z DOKLADNIE jedna rynienka, chyba ze podwariant D3-b):
   - wieczorna: W-a "najwiecej fi 15", W-b "zrownowazony" (fi 15 kosztem czesci fi 9), W-c "najmniejsza zmiana"
     (rynienka tylna -> rzad fi 15, reszta bez zmian);
   - poranna: P-a "najwiecej duzych" (fi 7,5 ograniczone do minimum), P-b "zrownowazony", P-c "najmniejsza zmiana";
   - dla wybranego kandydata na D3-b: ten sam uklad z rynienka podzielona (dlugosci, ile otworow, jaki rozstaw).
   Szacunek autora planu do sprawdzenia narzedziem (nie przyjmowac na wiare): w wieczornej w miejscu rynienki tylnej
   (y = 31,5) mieszcza sie 3 gniazda fi 15 (x = -18, 0, 18; promien obrysu 43,8), a po przesunieciu calego bloku o
   ok. 0,3 mm i rzedzie w szachownice byc moze 4 - wtedy stozki B i C trzeba przeniesc.
4. Dla kazdego wariantu: pozycje 3 stozkow znacznikow (jak najdalej od siebie; boki trojkata rozne o >= 5 mm, zeby
   program nie pomylil przypisania A / B / C; scianki >= 3), dolki i cyfra plytki okraglej, scianka do sciecia.
5. Uzasadnienie liczbami z `katalog.json`: ile z 17 projektow przy wspolczynniku 1,22 (wieczorna) i 1,0 (poranna)
   wymaga gniazda >= fi 12 / 12,5 / 15 albo rynienki (regula `kandydaci_gniazd`). Zaznaczyc, ze proba jest mala.
6. `R59_propozycja_ukladu.md` (<= 3 strony): tabela "dzis vs warianty" (liczba gniazd per srednica, rynienki, razem),
   dla kazdego wariantu rzedy (y, d, x), max promien obrysu, min scianka (para), pozycje znacznikow / dolkow / cyfry,
   wynik `weryfikuj_uklad_R59.js` (wszystko OK), skutki uboczne (co trzeba przeniesc), zalecenie.
7. Szkice: widok z gory 1:1 (kwadrat 96, kolo 47, kolo 100, gniazda z srednica, rynienka, stozki, dolki, cyfra),
   stary uklad obok nowego; SVG i PNG czytelne na telefonie.

**Gotowe, gdy:** 6 wariantow przechodzi `weryfikuj_uklad_R59.js` bez bledu; dokument i szkice sa; koordynator sam
uruchomil weryfikator na 2 losowych wariantach i dostal ten sam wynik.

## 7. Subsesja R59-A - zrodlo prawdy, generator, pliki plytek (po G0)

**Pliki:** `Ramki/parametry.json`, `Ramki/ramka_generator.py`, `Ramki/plan_ramki_v2.md`,
`Ramki/protokol_weryfikacji_v2.md`, `Ramki/00_PRZEPLYW_I_BRAMKI.md` (tylko wiersz Z20/D6 w sekcji 3),
`Ramki/R59_wdrozenie_zmiany.md` (nowy), `Ramki/wyniki_v2/**`, `Ramki/archiwum/*_przed_R59_2026-11-14.*`,
`Ramki/archiwum/wyniki_v2_przed_R59_2026-11-14/**`. Katalog PC: `<PC-katalog>\r59\Ramki`.
**Nie dotyka:** `stanowisko/`, dokumentow stanowiska, `Ramki_pakiet/`, `Ramki_do_wgrania/`, modelu 3D, `narzedzia/`.
**Czyta najpierw:** ten plan (sekcje 1-3), decyzje G0, `R59_propozycja_ukladu.md`, `R57_wdrozenie_zmiany.md` i
`R54_wdrozenie_zmiany.md` (wzor zakresu), `prompt_wykonawca.md`, `szablon_raport_wykonawcy.md`.

Kroki:
1. Kopie do archiwum: 4 pliki zrodla prawdy; na PC caly `wyniki_v2` (stl, json, arkusze) do
   `archiwum/wyniki_v2_przed_R59_2026-11-14/` + lista `sha256_stl_przed_R59.txt`.
2. `parametry.json`: `ev_rows`, `mo_rows` wg D1 / D2 (+ opis z "R59"), `ev_marker_pos`, `mo_marker_pos`,
   `code_dimples_round`, `number_pos_round`; przy D3-b parametry rynienki i otworow; przy D5-B numery; przy D6
   `quantities`. Opisy kluczy z nowymi liczbami. Nowe klucze tylko gdy konieczne (wtedy lista walidatora R14 w
   generatorze). Plik sie parsuje, liczba kluczy i statusy opisane w raporcie.
3. `node narzedzia/weryfikuj_uklad_R59.js parametry.json` (PC) = wszystko OK. Dopiero potem generator.
4. `ramka_generator.py` - tylko konieczne zmiany, kazda z powodem w raporcie: `OBJ_ORIENT` (objetosci 4 plytek po
   pierwszym przebiegu), teksty i wiersze arkuszy z liczbami starego ukladu, sprawdzenia zakladajace 2 rynienki albo
   rynienke przednia / tylna (K-08, K-16, K-61 f, teksty `odstepstwa_informacyjne_R57`), `lista_wymiarow`; przy D3-b
   liczba i rozstaw otworow per rynienka; przy D5-B numery dwucyfrowe i nazwy `n1` / `n4`.
5. Przenies 4 pliki `wyniki_v2/json/uklad_gniazd_*.json` do archiwum (pkt 1.3). Przebieg na PC:
   `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P ramka_generator.py -- --etap ALL --iter 1 --raport R59`,
   potem `--etap SPRAWDZ --iter <kolejny>`. Cel: 0 NIE (B 0 / P 0 / D 0). Rendery nie dzialaja na koncie `<konto-PC>`
   -> `--bez-renderow`, K-60 opisane jako odstepstwo, zadanie dla czlowieka w raporcie.
6. Pliki nieplytkowe (korpus W, korpus P, blat, wkladka, pokrywka, tulejka DC, 3 podkladki): SHA-256 = 
   `Ramki_pakiet/SHA256SUMS_2026-11-02_R57.txt`. Wkladka: gdy rozni sie tylko znak zera normalnej (porownaj liczbe
   trojkatow i wierzcholki) - przywroc plik `f4196fbc...` z archiwum, wariant odloz do archiwum, opisz.
7. `plan_ramki_v2.md`: Z20 (nowe liczby, stare jako "dawniej"), D6 (tabele rzedow obu plytek, promienie, suma
   wysokosci, znaczniki), 4.1 / 4.1a (liczby), 4.11 (wiersze "Kolo pola skanowania" i "Plytka okragla": promienie,
   scianki), tabela parametrow (zmienione wartosci), 12.1 (gdy zmienia sie lista plikow), rejestr: wiersz R59 po R57
   (z uwaga, ze R58 jest zarezerwowany), sekcja 14: nowy punkt. `protokol_weryfikacji_v2.md`: tabela 1 (objetosci),
   K-05 (liczby), K-08, K-09, K-16, K-61, K-62 (liczby scianek i promieni), K-58 (przy D5-B).
   `00_PRZEPLYW_I_BRAMKI.md` sekcja 3, wiersz Z20/D6: dopisek "[R59]".
8. `R59_wdrozenie_zmiany.md` w ukladzie pliku R57: 0 wynik (tabela 12 STL plytek - 4 bazowe, n1-n6, n8, n9 - i 4 JSON:
   SHA-256, objetosc), 1 decyzje G0 doslownie, 2 parametry stare -> nowe, 3 zmiany generatora, 4 edycje planu,
   5 edycje protokolu, 6 pliki i archiwum, 7 co dalej.
9. Wyniki na MSI: `tar` z PC `wyniki_v2` (json, arkusze, raport, README, `do_v3.md`, render, `.blend`) do worktree;
   STL do `Ramki/wyniki_v2/stl/` (ignorowane). Raport wykonawcy wg szablonu: `wyniki_v2/raport/raport_wykonawcy_R59_iter<n>.md`.

**Gotowe, gdy:** `ALL` i `SPRAWDZ` 0 NIE; 9 plikow nieplytkowych bajtowo jak R57; 12 STL + 4 JSON z SHA w
`R59_wdrozenie_zmiany.md`; lista `sockets` w JSON okraglych = JSON kwadratu tego typu; liczby gniazd = G0.

## 8. Subsesja R59-B - recenzja z siatek (swieza, rownolegle z R59-P)

**Pliki:** `Ramki/recenzja/sprawdz_R59*.py`, `Ramki/recenzja/log_R59_iter<n>.txt`,
`Ramki/recenzja/raport_recenzenta_R59_iter<n>.md`. Wszystko inne tylko do odczytu. PC: `<PC-katalog>\r59\recenzja`
(czyta `<PC-katalog>\r59\Ramki\wyniki_v2`).
**Czyta:** `prompt_recenzent.md`, `szablon_raport_recenzenta.md`, `protokol_weryfikacji_v2.md`, `parametry.json`,
`R59_wdrozenie_zmiany.md`, raport wykonawcy; metode (nie wyniki) z `recenzja/sprawdz_R57.py`, `recenzja/sprawdz_R54*.py`.

Sprawdza NIEZALEZNIE, z siatek STL (Blender albo trimesh na PC), wartosci oczekiwane liczy z `parametry.json`, nie z
JSON ukladu ani ze skryptow wykonawcy:
1. 12 STL plytek: szczelnosc, 1 bryla, normalne, gabaryt (96 x 96 x 8 + relief 0,6; okragla fi 100), objetosc =
   raport +- 0,01 cm3.
2. Kazde gniazdo z rzedow: polozenie, srednica gorna i dolna (kat 15 st.), glebokosc 4, otwor fi 3 na wylot; rynienka:
   obrys stadionu, otwory (liczba, rozstaw).
3. Kontrola odwrotna: w miejscach gniazd i rynienek STAREGO ukladu (z archiwum), ktore nie pokrywaja sie z nowymi,
   jest pelny material (wierzch na z = 8). Stare pozycje stozkow, jesli zmienione - tak samo.
4. Kolo: max promien obrysu <= 47; strefa +-45; min scianka miedzy wszystkimi parami obrysow >= 3 (mapa wierzchu z
   promieni); stozki: polozenie, fi 5 x 3, scianka >= 3; dolki: bity = numer, scianki; cyfra reliefu.
5. Okragle: K-61 (a-f), K-62, K-63; `sockets` okraglej = kwadrat.
6. SHA-256: 12 STL + 4 JSON = `R59_wdrozenie_zmiany.md`; 9 plikow nieplytkowych = SHA256SUMS R57.
7. K-53: plytka n1 - wkladka i pokrywka - plytka: 0 przeciec (wlasny test, nie wynik generatora).
8. Zgodnosc `parametry.json` <-> `plan_ramki_v2.md` D6 <-> `protokol` (liczby gniazd, promienie, scianki) i z G0.

Raport: werdykt ZALICZONY (0 B, 0 P) albo NIE ZALICZONY z lista B / P / D, liczba sond. NIE ZALICZONY: koordynator
wznawia R59-A z lista; ponowna recenzja = NOWA swieza subsesja R59-B (iter 2, 3).

## 9. Subsesja R59-P - program stanowiska (rownolegle z R59-B)

**Pliki:** `Ramki/stanowisko/**` z wyjatkiem `raporty/testy_krawedz/**`, `dane/`, `ustawienia.toml`.
PC: `<PC-katalog>\r59\program` (kopia `Ramki/stanowisko` z galezi + dane).
**Nie zmienia:** progow `[match]` / `[inspect]`, logiki `match.py` / `inspect.py`.
**Czyta najpierw:** `stanowisko/README.md`, `opisy_modulow/{uklad,plate,synth,katalog,ui}.md`,
`raporty/P3a_przekazanie.md`, decyzje G0, `R59_wdrozenie_zmiany.md`.

Kolejnosc "testy, potem kod":
1. **Stary uklad zostaje (D4 = TAK):** foldery `modele_plytek/{wieczorna,poranna,okragla_wieczorna,okragla_poranna}`
   skopiowane BAJTOWO jako `..._r54` (4 nowe foldery; nazwa ukladu w programie = klucz z `[plytki]`). Dopisz je w
   `ustawienia.przyklad.toml [plytki]`, `SCHEMAT` (`ustawienia.py`), listach `--plytka` (`synth`, `porownaj`,
   narzedzia) i w oknie. Przy D4 = NIE: stare modele tylko do `Ramki/archiwum/stanowisko_modele_przed_R59/`.
2. **Testy starego ukladu:** istniejace testy z zaszytymi liczbami (lista w pkt 1.5) przepnij na `*_r54` BEZ zmiany
   oczekiwan - maja przechodzic przed i po zmianie (dowod, ze stary uklad jest nietkniety).
3. **Testy nowego ukladu (najpierw czerwone):** liczby gniazd i srednic liczone z `../parametry.json` (nie stale),
   uklad.json zgodny z `parametry.json`, wszystkie pary obrysow >= 3 mm (takze okragle - rynienka), wszystko w kole 47,
   dokladnie tyle rynienek, ile w G0, w porannej jest gniazdo fi 15, pliki `plytka_n<N>.stl` dla wszystkich numerow,
   most -> rynienka, drugi most -> `pominiete` (albo przy D3-b: dwa krotkie mosty w dwoch rynienkach, zadnego
   `podwojny`), najwieksza korona z puli trafia do fi 15 bez przenikania (<= 1e-6 mm).
4. **Modele:** `uklad.json` = bajtowa kopia `wyniki_v2/json/uklad_gniazd_<typ>.json`; `plytka_n<N>.stl` = bajtowa kopia
   `ramka_plytka_<typ>_n<N>_v2.stl`; okragle: `plytka_bazowa.stl`. Testy z pkt 3 zielone.
5. **Straznik ukladu (D4 = TAK):** najpierw POMIAR: skan syntetyczny na `wieczorna_r54` porownany z `--plytka wieczorna`
   (nowy uklad) i odwrotnie, to samo dla porannej - co dzis zwraca program (ostrzezenia, jakosc wyrownania, kolory
   gniazd). Jesli nie ma jednoznacznego ostrzezenia: minimalna zmiana w `plate.py` - po wyrownaniu porownanie
   glebokosci skanu w srodkach gniazd modelu (poza otworem) z modelem; niezgodnosc powyzej progu ->
   `jakosc["uklad_zgodny"] = False`, ostrzezenie, w `porownaj` / oknie komunikat "plytka nie pasuje do wybranego
   ukladu" i zadnych zielonych gniazd. Prog dobrany na danych syntetycznych (liczniki w raporcie: 0 falszywych na
   plytkach zgodnych, 100 % wykrytych na niezgodnych, puste i pelne plytki). Test + opis w `opisy_modulow/plate.md`.
6. **Dane i metryki (PC, pelna moc):** te same polecenia i seedy co zestawy P2 i P3a (README, `P3a_przekazanie.md`
   pkt 4), ale na nowym ukladzie -> `dane/syntetyczne_R59_P2`, `dane/syntetyczne_R59_P3a`; `metryki_P3a.py` na obu;
   tabela "stary uklad (punkt odniesienia koordynatora) vs nowy". Projekty: `<PC-katalog>\r59\Prace_test`.
   Kryteria: wyrownanie 100 % skanow, blad < 0,05 mm; numer z dolkow na okraglych 100 %; top-1 w scenariuszu
   "dobrze" 100 %; falszywe czerwone na pracach calych 0; wykrycie "dowolna metoda" nie nizsze niz punkt odniesienia
   o wiecej niz 3 pkt proc. (gorzej = analiza per srednica gniazda w raporcie, BEZ strojenia progow).
7. **Pojemnosc:** dla 17 projektow, 20 seedow na plytke: ile prac osadzonych / pominietych, zajetosc per srednica -
   stary vs nowy uklad, osobno wieczorna (1,22) i poranna (1,0). To jest miara korzysci ze zmiany dla wlasciciela.
8. **Opisy:** `opisy_modulow/uklad.md` (liczby, kryterium), `plate.md` (straznik), `synth.md`, `README.md` (lista
   plytek, uklady `_r54`), raport `stanowisko/raporty/R59_<data>.md` (co zmieniono, testy przed -> po, tabele z pkt 6-7,
   czego nie zrobiono).
9. `pytest testy -q` na PC: 0 failed; liczba testow przed -> po.

**Gotowe, gdy:** pytest zielony, modele bajtowo zgodne z `wyniki_v2`, tabele metryk i pojemnosci w raporcie, stary
uklad dziala jak w punkcie odniesienia.

## 10. Subsesja R59-D - dokumenty i arkusz zamowienia (po R59-B ZALICZONY)

**Pliki:** trzy dokumenty `.md` w `Ramki/` (w nazwach jest pauza, nie myslnik): `Stanowisko kontroli cyrkonii * plan
wdrozenia v2.md`, `Zakupy i druk * stanowisko kontroli cyrkonii.md`, `Budowa ramki * decyzje i zamienniki.md`;
`Ramki/narzedzia/arkusz_zamowienia_R59.py`, `Ramki/narzedzia/buduj_pdf_R59.cmd`; trzy `.pdf` po zbudowaniu; kopie
`Ramki/archiwum/*_przed_dokumenty_R59_<data>.*`.

1. Znajdz wszystkie miejsca ze starym ukladem: liczby gniazd (18 + 2, 31 + 2, 7 x fi 9, 6 x fi 12, 5 x fi 15,
   18 x fi 7,5, 7 x fi 10, 6 x fi 12,5), rynienki (dwie, 60 x 15, 50 x 13), SHA-256 plikow plytek, objetosci
   (59 / 61 / 49,01 / 50,56 cm3), sumy i ceny zamowienia. Zamien na liczby z `R59_wdrozenie_zmiany.md` i arkusza.
2. Opisz zmiane zwyczajnym jezykiem: po co (wieksze prace, mniej malych gniazd), co to kosztuje (jeden most na
   plytke; przy D3-b dwa krotkie), co ze starymi plytkami (D4, D5), co zamawiamy (D6).
3. "Budowa ramki": element "Plytki" (jak jest / dlaczego / czy mozna zmienic / co wymusza) i lista zmian z R59.
4. Bez dat, tygodni i ram czasowych w dokumentach (zasada R56). Bez nazwisk.
5. `arkusz_zamowienia_R59.py`: wzor R57, objetosci czytane z raportu / arkusza generatora, nie wpisane recznie.
6. PDF: `buduj_pdf_R59.cmd` z trzema wywolaniami `narzedzia/buduj_plan_wdrozenia.py --md ...` (dokladna skladnia z
   naglowka skryptu i wpisu R57-C w `00_NADZOR_STAN.md`). Uruchomienie wg D7; subsesja NIE instaluje pakietow.
   Do czasu PDF dokumenty `.md` sa gotowe, a w raporcie stoi "PDF: czeka na czlowieka".

**Gotowe, gdy:** w trzech dokumentach nie ma liczb starego ukladu poza miejscami opisanymi jako historia; kazda
liczba ma zrodlo w `parametry.json`, `R59_wdrozenie_zmiany.md` albo arkuszu.

## 11. Subsesja R59-M - model 3D i animacja (po R59-B ZALICZONY)

**Pliki:** `Ramki/ramka_3d.html`, `Ramki/animacja_ramki.html`, `Ramki/narzedzia/zbuduj_model_offline.js`,
`Ramki/wyniki_model_R59/**`. PC: `<PC-katalog>\r59\model`.

1. `ramka_3d.html`: wklejona kopia parametrow (ok. linii 320-375) = aktualny `parametry.json`; maski `EV_WORK` /
   `EV_RED` (ok. linii 994-996) sa przypisane do numerow rzedow i liczby gniazd w rzedzie - dopasuj do nowych rzedow;
   sprawdz odpowiedniki dla plytki porannej i etykiety wymiarow (ok. linii 1120).
2. `animacja_ramki.html`: sprawdz, czy gniazda sa rysowane z parametrow, czy zaszyte; popraw.
3. Budowa na PC: `node narzedzia/zbuduj_model_offline.js wyniki_model_R59/ramka_3d_v3_R59.html` (wkleja 7 STL, w tym
   nowe n1 i n4); kopia animacji do `wyniki_model_R59/`.
4. Sprawdzenie: plik otwarty z dysku w Chrome bez okna (PC): 0 zadan sieciowych, 0 bledow konsoli, 7 plikow STL
   zaladowanych; zrzuty widoku z gory plytki wieczornej i porannej (`wyniki_model_R59/*.jpg`) pokazuja nowy uklad.
   Gdy Chrome nie startuje na koncie `<konto-PC>`: opisz i zostaw sprawdzenie koordynatorowi / czlowiekowi.
5. Opublikowany wczesniej artefakt online modelu nie jest aktualizowany - wpis do raportu ("nieaktualny po R59").

## 12. Subsesja R59-K - pakiet (po G1 i po PDF)

**Pliki:** `Ramki/narzedzia/zbuduj_pakiet_R59.sh`, `Ramki/Ramki_pakiet/**`, `Ramki_do_wgrania/*R59*`.

1. `zbuduj_pakiet_R59.sh` na wzor `zbuduj_pakiet_R57.sh`: `R=R59`, data, nazwy dokumentow, lista STL, przypiete SHA
   plikow plytek (z `R59_wdrozenie_zmiany.md` = raport recenzenta), wkladka `f4196fbc...`, kontrola: 9 plikow
   nieplytkowych bajtowo jak w `SHA256SUMS_2026-11-02_R57.txt`; dokumenty R59, `R59_wdrozenie_zmiany.md`, raporty
   wykonawcy i recenzenta, 4 JSON ukladu, model `wyniki_model_R59`; README z opisem R59.
2. Uruchomienie tam, gdzie sa wszystkie pliki (kopia robocza na PC, `bash` z Git for Windows; Python pelna sciezka).
   Wynik: `Ramki_pakiet/` + `SHA256SUMS_<data>_R59.txt`, `sha256sum -c` = OK.
3. `Ramki_do_wgrania/`: trzy ZIP (`..._R59_cz1_dokumenty_druk.zip`, `..._cz2_model.zip`, `..._cz3_zrodla.zip`, kazdy
   < 10 MB), `SHA256SUMS_<data>_R59.txt`, `INSTRUKCJA_PAKIET_<data>_R59.md`, `DO_WGRANIA_NA_DRIVE_<data>_R59.md`, trzy
   PDF. Niczego starego nie usuwac ani nie nadpisywac.
4. Wyniki `tar` na MSI do worktree.

## 13. Subsesja R59-R - recenzja PR (swieza, rownolegle z testami koordynatora)

Czyta `git diff origin/main...HEAD` (bez binariow), ten plan, G0. Sprawdza: listy plikow subsesji przestrzegane;
spojnosc liczb miedzy `parametry.json`, planem, protokolem, trzema dokumentami, testami i modelami programu; brak
liczb starego ukladu w miejscach biezacych; brak nazwisk i nazw folderow zlecen w zatwierdzonych plikach (porownanie
z listingiem `Prace_test` bez wypisywania nazw); nowe pliki ASCII bez diakrytykow; zadnego STL poza dozwolonymi
katalogami; nic w `raporty/testy_krawedz`; kod straznika i zmiany generatora - poprawnosc i przypadki brzegowe.
Werdykt: "do scalenia" albo numerowana lista. Najwyzej 2 rundy poprawek (wznowienie wlasciwego wykonawcy), ponowna
recenzja = nowa swieza subsesja.

## 14. Testy koncowe koordynatora (wykonuje SAM, na czystej kopii)

Zasada: koordynator nie ufa raportom subsesji - powtarza kluczowe sprawdzenia wlasnymi poleceniami na swiezym
wypakowaniu galezi. Dowody (logi tekstowe, male) do `Ramki/R59_odbior/`, wynik kazdego testu do tabeli w
`Ramki/R59_raport_koncowy.md`: test - kryterium - wynik (liczby) - plik dowodu. Test nieudany = wpis FAIL z wyjsciem,
poprawka przez wlasciwa subsesje, powtorka testu.

| Nr | Test | Jak | Kryterium |
|---|---|---|---|
| T0 | Czysta kopia | `git status` czysty; `git archive HEAD Ramki` -> `<PC-katalog>\r59\odbior`; STL z R59-A do `odbior\Ramki\wyniki_v2\stl` | 21 STL, drzewo = HEAD |
| T1 | Uklad na parametrach | `node narzedzia\weryfikuj_uklad_R59.js parametry.json` | same OK, kod 0; liczby gniazd = G0 |
| T2 | Generator | `blender ... --etap SPRAWDZ --iter <n> --raport ODBIOR` | 0 NIE (poza opisanym K-60 przy braku renderow) |
| T3 | Sumy SHA-256 | (a) 9 plikow nieplytkowych vs SHA256SUMS R57; (b) 12 STL + 4 JSON vs `R59_wdrozenie_zmiany.md` vs raport recenzenta; (c) `sha256sum -c` w `Ramki_pakiet`; (d) `modele_plytek/<typ>` vs `wyniki_v2`; (e) `modele_plytek/*_r54` vs `origin/main` | wszystkie zgodne |
| T4 | Wlasny pomiar siatek | wlasny skrypt (trimesh, promienie z gory), NIE skrypty A / B: szczelnosc, gabaryt, objetosc; dla kazdego gniazda z rzedow punkt 2,0 mm od srodka (poza otworem) -> dno; srodki gniazd starego ukladu lezace >= 1 mm poza nowymi obrysami -> wierzch | dno z = 4,00 +- 0,05 w 100 % gniazd; wierzch z = 8,00 +- 0,05 w 100 % punktow odwrotnych; objetosc = raport +- 0,01 cm3 |
| T5 | Testy programu | `run.cmd -m pytest testy -q -p no:cacheprovider`, log do pliku | 0 failed, 0 errors; passed >= punkt odniesienia; pominiete tylko te z punktu odniesienia |
| T6 | Lancuch na swiezych danych | seedy 9001-9003 (inne niz u R59-P), 4 nowe plytki: `synth` -> `porownaj --prawda` | wyrownanie < 0,05 mm; okragle: numer z dolkow poprawny; kazdy fragment w swoim gniezdzie; puste = prawda; top-1 100 % dla prac ulozonych dobrze |
| T7 | Metryki | tabela R59-P vs punkt odniesienia z etapu 0 (wlasne przeliczenie z plikow JSON metryk) | kryteria z sekcji 9 pkt 6 |
| T8 | Stary uklad | (a) seed 7001 na `*_r54` -> `_wynik.json` = punkt odniesienia (mapa gniazdo -> projekt -> status); (b) skan `*_r54` porownany z nowym ukladem i odwrotnie | (a) identyczne; (b) ostrzezenie i 0 zielonych gniazd w 100 % prob |
| T9 | Gniazda fi 15 | poranna: istnieje gniazdo `d_top == 15`; najszersza pojedyncza korona puli (wsp. 1,0) -> `katalog.gniazdo_dla`; osadzenie w fi 15 | praca w fi 15, przenikanie <= 1e-6 mm, rozpoznana |
| T10 | Mosty | 2 atrapy mostu na plytce: (a) jedna rynienka; (b) przy D3-b dwie krotkie | (a) 1 osadzony, 1 w `pominiete`, 0 `podwojny`; (b) 2 osadzone i rozpoznane |
| T11 | Dokumenty | wyszukanie liczb starego ukladu w 3 dokumentach, planie, protokole (poza historia); PDF: istnieja, nowsze niz `.md`, tekst zawiera "R59" i nowe liczby (`pypdf` na MSI) | 0 trafien poza historia; 3 PDF aktualne |
| T12 | Model 3D | obejrzenie zrzutow widoku z gory W i P (wlasnymi oczami: Read obrazu) + log budowy (7 STL) | uklad na zrzucie = szkic wybranego wariantu |
| T13 | Pakiet | rozpakowanie 3 ZIP do katalogu tymczasowego, `sha256sum -c`, rozmiary, liczba plikow, instrukcja | wszystko OK, kazdy ZIP < 10 MB, brak nazwisk w nazwach plikow |
| T14 | Higiena repo | `git diff --name-only origin/main...HEAD` zawiera sie w sumie list plikow subsesji; brak STL poza dozwolonymi katalogami; nowe pliki ASCII; nic w `raporty/testy_krawedz` | zgodne |

Obrazy dla wlasciciela (wyslac jako pliki): widok z gory 4 nowych plytek (`_mapa.png` z `porownaj` albo
`narzedzia/rzut_z_gory.py`), szkic "stary vs nowy", tabela pojemnosci z R59-P.

## 15. Scalenie, stan, raport (E9)

1. Do wlasciciela: wynik T0-T14 (tabela), werdykt R59-R, lista odstepstw, prosba o G2.
2. Po G2: `gh pr ready`, `gh pr view --json state,mergeable` (UNKNOWN = petla co 5 s), `gh pr merge --merge`;
   kasowanie galezi dopiero po `state` = `MERGED`.
3. Za ta sama zgoda: w `<MSI>\kod\qc` `git pull --ff-only` (nie ruszac niezatwierdzonych plikow
   innych sesji; konflikt = stop i pytanie), stare STL z `Ramki\wyniki_v2\stl` do
   `Ramki\archiwum\wyniki_v2_przed_R59_2026-11-14\stl`, nowe STL na ich miejsce.
4. Sprzatanie PC: usun `<PC-katalog>\r59\Prace_test` (dane z nazwiskami); reszte `<PC-katalog>\r59` zostaw do
   decyzji wlasciciela (zapisz rozmiar).
5. `00_NADZOR_STAN.md`: zamkniecie R59 (SHA plikow do zamowienia, obowiazujacy pakiet, co otwarte).
6. `R59_raport_koncowy.md` i raport w czacie (<= 40 linii): tabela subsesji (iteracje, czas), testy przed -> po,
   pojemnosc stary vs nowy, FAIL-e mechaniki z obejsciem, 3 wnioski.
7. Zadania czlowieka - wypisac w czacie i dodac do Todoist (projekt "Serwer-msi", sekcja `qc * R59 (<dd.mm>)`):
   - opisac i odlozyc stare plytki (D4 / D5),
   - PDF: uruchomic `buduj_pdf_R59.cmd` na PC (jesli D7-a) - to zadanie pojawia sie juz na G1,
   - wgrac pakiet R59 na Dysk Google (jesli D8-a),
   - zaktualizowac `<PC>\Desktop\Ramki` na PC z repo,
   - zamowic plytki (pliki i SHA z `R59_wdrozenie_zmiany.md`),
   - rendery, jesli nie powstaly na koncie `<konto-PC>`.

## 16. Ryzyka i pulapki

- JSON ukladu nie odswiezy sie sam (pkt 1.3) - bez przeniesienia 4 plikow do archiwum powstana STL ze starym ukladem.
- Brak zapasu w kole 47 i na sciankach 3,000: pozycje tylko z narzedzia, nigdy z reki.
- Zmiana rzedow przesuwa numery gniazd (id rzedami od przodu, w rzedzie od prawej): dane syntetyczne i wyniki ze
  starego ukladu nie sa porownywalne po numerze gniazda.
- Wkladka: inny znak zera normalnej po `ALL` - przywrocic plik z archiwum, nie przyjmowac nowego SHA.
- Rendery Cycles i PDF moga nie dzialac na koncie `<konto-PC>` - nie obchodzic bariery, zadanie dla czlowieka.
- [usunieto w kopii: opis dostepu ssh]
- Dwa uklady o tych samych numerach (D5-A) = ryzyko zlego wyboru plytki w oknie - dlatego straznik (sekcja 9 pkt 5).
- D5-B i D3-b to realne zmiany kodu generatora - wydluzaja R59-A o 1-2 iteracje recenzji.
- Kontekst: wykonawca R59-A i R59-P to dlugie zadania; caly stan jest w plikach, wiec przy zapelnieniu kontekstu
  nowa subsesja przejmuje z raportu i `00_NADZOR_STAN.md`.
- Token `gh` niewazny; bez niego paczka konczy sie na galezi lokalnej i wiadomosci do wlasciciela.

## 17. Wzor zlecenia subsesji (koordynator uzupelnia i czyta przed wyslaniem)

```
Jestes subsesja <KOD> paczki R59 projektu qc (stanowisko kontroli cyrkonii, ramki). Model: Fable 5.2, effort high.
Katalog roboczy (worktree koordynatora): <sciezka>. Galaz: <galaz>. NIE rob git add / commit / push.

CEL: <jedno zdanie>.
PRZECZYTAJ NAJPIERW: Ramki/plan_sesji_R59_uklad_gniazd_2026-11-14.md sekcje 1, 2 i <numer sekcji subsesji>; <pliki>.
DECYZJE WLASCICIELA (G0): <doslownie D1-D8>.
TWOJE PLIKI (tylko te mozesz tworzyc / zmieniac): <lista>.
NIE DOTYKAJ: wszystkiego poza lista; w szczegolnosci <lista zakazow>.
KROKI: <z sekcji subsesji>.
PC: zasady z sekcji 2.4 planu; twoj katalog <PC-katalog>\r59\<kat>; PC ma 32 watki i 32 GB - licz rownolegle.
MSI: zadnych pomiarow w Pythonie (brak pakietow, malo RAM).
DANE OSOBOWE: tylko skroty projektow, nigdy nazwy plikow ani folderow zlecen.
GOTOWE, GDY: <kryteria z sekcji>.
ODPOWIEDZ KONCOWA (<= 25 linii): co zrobione, 5-8 najwazniejszych liczb, lista zmienionych plikow, odstepstwa,
czego nie zrobiono i dlaczego, POTRZEBUJE (pliki / decyzje), sciezka do raportu.
```

## 18. Prompt startowy koordynatora (wkleja wlasciciel; sesja Fable 5.2, effort xhigh)

```
Jestes koordynatorem paczki R59 w projekcie qc. Przeczytaj i wykonaj plan:
<MSI>\kod\qc\Ramki\plan_sesji_R59_uklad_gniazd_2026-11-14.md
Zacznij od etapu 0 (sekcja 5). Subsesje uruchamiaj narzedziem Agent: model fable, effort high, w tle.
Na bramkach G0, G1, G2 zatrzymaj sie i zapytaj mnie jednym zbiorczym pytaniem. Pisz krotko - czytam z telefonu.
```
