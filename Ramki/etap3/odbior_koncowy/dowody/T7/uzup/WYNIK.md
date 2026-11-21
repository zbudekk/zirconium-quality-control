WERDYKT T7 UZUPELNIENIE: ZAL z odstepstwem O12 - komunikat WIDOCZNY na ekranie programu z paczki w 6 z 6 przypadkow (powtorzenia: 12 z 12 podstawowych + 4 z 4 dodatkowych), FAIL 0, NIE ZMIERZONO 0; tekst doslownie w PW zal. F: 0 z 6 (podobny wiersz: 3 z 6); "mowi, co zrobic": 5 z 6 (przypadek 2 to informacja - niczego nie trzeba robic); dalsza praca po komunikacie: 6 z 6. Zastrzezenia: przypadek 3 - panel komunikatu dopiero, gdy czeka skan; przypadek 4 - sieci fizycznie nie odcinano (adres ramki nieosiagalny).

# T7 - uzupelnienie: tresc komunikatow NA EKRANIE programu z paczki (21.11.2026)

Wykonawca: sesja wykonawcy testow koncowych (uzupelnienie T7), tor 4 ciezkich krokow, `-Kto T7uzup`. Godziny: 04:41 (start) - 05:06:14
(koniec serii) - 05:12 (opis i kontrole koncowe). Program: instalacja `<PC-katalog>\t0\odbior_t12\Stanowisko` (wersja biezaca 0.3.1, paczka
`Stanowisko_0.3.1.zip`, commit 571e186), uruchamiany przez `Polecenie.cmd <sonda>` z WLASNYM plikiem ustawien. Pierwotny `..\WYNIK.md`
bez zmian. Pytanie pomiaru: czy technik COS ZOBACZY - jaki tekst, kiedy, czy mowi, co zrobic, czy jest w PW zal. F.

## Tabela 6 przypadkow

Teksty przepisane BEZ znakow diakrytycznych (w programie maja polskie znaki; cudzyslowy drukarskie zapisane jako "). "Widoczny po" =
od zdarzenia awarii do pierwszego odczytu sondy, w ktorym panel ma `isVisible()` i widoczne piksele (zegar sondy 150 ms).

| Nr | Przypadek | Komunikat na ekranie (doslownie: tytul / tekst / przyciski) | Widoczny po | n z 2 | W zal. F | Mowi, co zrobic | Dalsza praca po komunikacie | Werdykt |
|---|---|---|---|---|---|---|---|---|
| 1 | zabicie silnika w trakcie analizy | "Plytka bez numeru: Analiza skanu nie powiodla sie" / "Program nie przeanalizowal tego skanu (analiza zostala przerwana). Zeskanuj plytke ponownie." / [Zamknij] - panel czerwony nad lista plytek i mapa; kafelek plytki: "analiza nie powiodla sie" | 0,31 s i 0,45 s od polecenia `Stop-Process` dla procesu silnika | 2 z 2 | nie | tak ("Zeskanuj plytke ponownie") | tak - nastepny skan przyjety (25,7 s i 24,3 s od startu zapisu); baza: skany `blad` 1 + `przyjety` 1, zdarzenia `blad_analizy` 1, `blad_analizy_rodzaj` 1 | ZAL z odstepstwem O12 |
| 2 | zamkniecie programu w polowie wieczoru i ponowny start | "Program wznowil prace" / "Po ponownym uruchomieniu program dokancza zalegle skany: 1." / [Zamknij] - panel niebieski (informacja) | 0,40 s i 0,40 s od pojawienia sie okna po ponownym starcie (wariant c - zwykle zamkniecie okna: 0,00 s, w pierwszym odczycie) | 2 z 2 (+ 1 z 1 wariant c) | nie | nie - to informacja; niczego nie trzeba robic (program dokancza sam) | tak - skan przerwany zakonczeniem programu przeanalizowany po restarcie (22,0 s, 22,4 s, c: 23,8 s); pierwszy odczyt ekranu po restarcie: kafelek `plytka_1` i naglowek mapy "Plytka 8 - do obejrzenia: 3" (stan z bazy); baza: skany `przyjety` 2 z 2 | ZAL z odstepstwem O12 |
| 3 | brak folderu "Cyrkon" | "Brak folderu projektow" / "Program nie widzi folderu projektow - skany czekaja (1). Sprawdz, czy dysk z folderem projektow jest podlaczony, i kliknij "Odswiez pule". Jesli folder jest inny - zglos to." / [Odswiez pule] [Zamknij] - panel czerwony; pasek stanu: "Folder projektow: brak folderu projektow", "Analiza: skany czekaja", "czekaja na projekty: 1" | 3a (start bez folderu): 0,47 s i 0,40 s od konca zapisu skanu; 3b (folder znika w trakcie): 5,37 s i 5,42 s od konca zapisu skanu. BEZ czekajacego skanu panelu NIE MA (3a: tylko pasek "brak folderu projektow" od 0,05 s; 3b: nic - pasek nadal "plikow projektow: 17") | 2 z 2 (3a) i 2 z 2 (3b) | podobny (wiersz 2) | tak ("Sprawdz, czy dysk ... jest podlaczony, i kliknij "Odswiez pule"") | tak - po przywroceniu folderu i kliknieciu "Odswiez pule" W KOMUNIKACIE czekajacy skan przeanalizowany (3a: 21,1 s i 20,1 s; 3b: 18,0 s i 13,3 s), komunikat znika; baza: skany `przyjety` 2 z 2 | ZAL z odstepstwem O12 (zastrzezenie: komunikat dopiero przy czekajacym skanie - do decyzji) |
| 4 | brak sieci (adres ramek nieosiagalny) | wieczor: "Ramka wieczorna nie odpowiada" / "Program dziala bez ramki - wynik plytki pokazuje ekran. Sprawdz zasilanie ramki i siec stanowiska; ramka dolaczy sama." / [Zamknij]; poranek: "Ramka poranna nie jest podlaczona" / "Program dziala bez ramki - rozkladaj prace wedlug ekranu: kuweta po kuwecie (Enter = rozlozona, Backspace = cofnij, cyfry i Enter = wybor kuwety)." / [Zamknij] - panele niebieskie; pasek stanu (wyrozniony): "Ramki: W: brak polaczenia | P: brak polaczenia", podpowiedz: "Brak polaczenia z ramka - sprawdz zasilanie ramki i siec stanowiska." | wieczor: 2,05 / 2,11 s (4a) i 2,12 / 1,90 s (4b) od pojawienia sie okna (program czeka 2 s na pierwsze polaczenie); pasek od pierwszego odczytu; poranek: 0,14-0,16 s od klikniecia "-> Poranek" | 2 z 2 (4a) i 2 z 2 (4b) | podobny (wiersze 6 i 8) | tak (wieczor: "Sprawdz zasilanie ramki i siec stanowiska"; poranek: jak pracowac bez ramki) | tak - komunikat daje sie zamknac, tryby sie przelaczaja, pula i silnik gotowe (4 z 4); skan przyjety przy nieosiagalnych ramkach (p4b_2: 49,1 s; takze 9 przebiegow przypadkow 1, 2, 3, 6 - ramki z ustawien instalacji) | ZAL z odstepstwem O12 |
| 5 | brak ramki (skonfigurowana, nikt nie slucha / atrapa wylaczona w trakcie) | te same dwa komunikaty co w przypadku 4 (program nie rozroznia "brak sieci" i "ramka wylaczona"); 5d: pasek przed awaria "Ramki: W: gotowa | P: gotowa", po awarii "W: brak polaczenia | P: brak polaczenia" | 5a (nikt nie slucha): 2,10 / 2,10 s od pojawienia sie okna; 5d (atrapy ramek zakonczone w trakcie pracy): 0,32 s od zakonczenia atrap; poranek: 0,14-0,16 s od przelaczenia | 2 z 2 (5a) + 1 z 1 (5d); wieczor i poranek | podobny (wiersze 6 i 8) | tak (jak w 4) | tak - jak w 4 (3 z 3: zamkniecie komunikatu, przelaczenie trybow, pula i silnik gotowe) | ZAL z odstepstwem O12 |
| 6 | baza zajeta (klikniecie decyzji technika) | "Decyzja NIE zostala zapisana" / ""Ukruszona" - plytka 8, gniazdo 1 - decyzja NIE jest zapisana: baza stanowiska byla zajeta przez inny program. Kliknij "Ponow teraz"; jesli znowu sie nie uda, odczekaj chwile i kliknij jeszcze raz. Dopoki widzisz ten komunikat, tej decyzji nie ma w programie." / [Ponow teraz] [Rezygnuje - nie zapisuj] - panel czerwony | 0,79 s (BEGIN EXCLUSIVE) i 0,32 s (BEGIN IMMEDIATE) od klikniecia "Ukruszona" (okno stoi w kliknieciu 0,68 s / 0,30 s) | 2 z 2 | nie | tak ("Kliknij "Ponow teraz"...") | tak - "Ponow teraz" przy NADAL zajetej bazie: komunikat zostaje (2 z 2); po zwolnieniu bazy "Ponow teraz": decyzja zapisana, komunikat znika, lista "do dofrezowania" 0 -> 1 (2 z 2); baza po zamknieciu: `decyzje` 1 wiersz (2 z 2) | ZAL z odstepstwem O12 |

Liczniki: komunikat widoczny 6 z 6 przypadkow; powtorzenia podstawowe 12 z 12 (po 2 na przypadek; w przypadku 4 podstawowe = 4a,
w 5 = 5a) + dodatkowe 4 z 4 (4b x 2, 2c, 5d) = 16 przebiegow, 16 z 16 z kodem 0 i z komunikatem; przypadkow bez komunikatu
(FAIL): 0; NIE ZMIERZONO: 0. Okienek dialogowych (osobnych okien) program nie pokazal w zadnym przebiegu -
wszystkie komunikaty sa panelami w oknie glownym (jedyne okno najwyzszego poziomu: `okno_wieczor`, 16 z 16).

## Komunikaty a PW zal. F

Zal. F: `<REPO>\Ramki\Stanowisko kontroli cyrkonii - plan wdrozenia v2.md` (plik z pauza w nazwie), sekcja "### F. Co robic, gdy nie
dziala", wiersze pliku 694-705 = 12 wierszy "Objaw | Co zrobic" (numery 1-12 nizej = kolejnosc w tabeli). Zal. F nie zawiera tekstow
komunikatow programu - jest lista objawow.

| Tekst widziany na ekranie | W zal. F | Wiersz zal. F |
|---|---|---|
| "Analiza skanu nie powiodla sie" / "... (analiza zostala przerwana). Zeskanuj plytke ponownie." | nie ma | brak wiersza o nieudanej analizie |
| "Program wznowil prace" / "Po ponownym uruchomieniu program dokancza zalegle skany: 1." | nie ma | najblizszy 11 "Program nie startuje" - inny objaw |
| "Brak folderu projektow" / "Program nie widzi folderu projektow - skany czekaja (1). ..." | jest podobny | 2: "Wszystkie gniazda szare (brak projektow)" -> "Raporty MillBox nie dotarly: skopiowac folder, przycisk "Odswiez pule"" (wspolne: brak projektow i "Odswiez pule"; objaw na ekranie inny - skany czekaja, nie ma szarych gniazd) |
| "Ramka wieczorna nie odpowiada" / "... Sprawdz zasilanie ramki i siec stanowiska; ramka dolaczy sama." | jest podobny | 6: "Diody nie swieca" -> "Zasilanie ramki ..., przycisk "Test LED" ..., ikona Wi-Fi na matrycy; bez diod poranek dziala po podpisach na ekranie laptopa" |
| "Ramka poranna nie jest podlaczona" / "Program dziala bez ramki - rozkladaj prace wedlug ekranu: ..." | jest podobny | 8: "Ramka poranna nie laczy sie z laptopem" -> "... sprawdzic Wi-Fi, w ostatecznosci wlaczyc hotspot laptopa"; 6 (jak wyzej) |
| "Decyzja NIE zostala zapisana" / "... baza stanowiska byla zajeta przez inny program. Kliknij "Ponow teraz" ..." | nie ma | brak wiersza o bazie |

Doslownie w zal. F: 0 z 6; podobny wiersz: 3 z 6 (przypadki 3, 4, 5); brak: 3 z 6 (przypadki 1, 2, 6). Stad O12 w 6 z 6 (decyzja
koordynatora 20.11 nr 3: komunikat jest i program pracuje dalej, tekstu nie ma w zal. F = "ZAL z odstepstwem O12").

## Jak mierzono

- Sonda `sonda_komunikaty.py` (w tym katalogu; naglowek wypisuje KAZDE miejsce, w ktorym zaglada do wnetrza programu): uruchamia
  `stanowisko.aplikacja.main` w procesie sondy (jak sterownik T2), okno offscreen (O4), co 150 ms zapisuje teksty wszystkich paneli
  komunikatow / pytan (`PanelUwagi`, `PanelOsoby` w obszarach `pasek_bledow`, `uwagi`, `rano_pasek_bledow`, `rano_uwagi`,
  `lista_plytek`), paska stanu (`napis_*` + podpowiedz pola ramek) i innych okien najwyzszego poziomu; `isVisible()` i "piksele"
  (`visibleRegion()` niepuste); zrzut `okno.grab().save` przy pierwszym pojawieniu sie panelu. Czynnosci tylko kliknieciami po nazwach
  obiektow (`osoba_0`, `plytka_<id>`, gniazdo mapy, `przycisk_ukruszona`, `komunikat_ponow_polecenie`, `komunikat_odswiez_pule`,
  `przycisk_przelacz_tryb`, `zamknij_komunikat`). Niczego nie podmienia, polecen kontrolera nie wola, do bazy nie pisze.
- Z wnetrza programu czyta (tylko odczyt): `okno.k.stan()` (do sterowania scenariuszem i jako odczyt porownawczy - werdykt "widoczny"
  liczony WYLACZNIE z tekstow widzetow), `okno.pokazana_plytka()`, `ochrona_aktywna()`, `mapa.przygaszona()`, `mapa.srodek_gniazda()`,
  `widok.praca_id`, `multiprocessing.active_children()` (PID silnika), baze po zamknieciu programu (`mode=ro`: liczniki `skany`,
  `zdarzenia`; `decyzje` przez `sql_odczyt.py`). We wszystkich odczytach komunikat w stanie i panel na ekranie byly zgodne.
- Ustawienia kazdego przebiegu: kopia `<K>\ustawienia.toml` z 11 sciezkami `[sciezki]` w `uzup\robocze\<przebieg>\` (funkcja
  `zloz_ustawienia` sterownika T2; `folder_cyrkon` = `uzup\robocze\Cyrkon` albo `Cyrkon3` = kopie `<PC-katalog>\app\Prace_test`, 17
  plikow; `pula_cache` = `uzup\robocze\pula_cache`); `[ramki]` zmieniane tylko w 4b, 5a, 5d. Kazdy przebieg = nowy katalog i nowa baza.
- Awarie (srodki zewnetrzne): (1) `powershell Stop-Process -Id <pid silnika> -Force` 5 s po starcie analizy; PID wg reguly planu -
  procesy Pythona bazowego ze `StartTime` do 5 s po posredniku: dokladnie 2 (program 0,04 / 0,03 s, silnik 1,58 / 1,11 s po
  posredniku), mlodszy = silnik = jedyny proces potomny `multiprocessing` programu (regula i lancuch zgodne 2 z 2); (2) nadzorca
  konczy proces posrednika (`TerminateProcess`) 4 s po starcie analizy 2. skanu - 3 z 3 procesow nie zyje po 1,5 s (2 z 2) - i
  startuje program ponownie; wariant c: `okno.close()` (= krzyzyk) w trakcie analizy; (3) `os.rename` folderu projektow - przed startem
  (3a) i w trakcie pracy po 1. skanie (3b); (4) 4a: adresy z ustawien instalacji `ramka-w.local` / `ramka-p.local` (nazwa sie nie
  rozwiazuje), 4b: 192.0.2.10 / 192.0.2.11 (adresy dokumentacyjne - brak odpowiedzi); (5) 5a: 127.0.0.1:18799, nikt nie slucha;
  5d: `narzedzia\atrapa_ramki.py` (rola W na 127.0.0.2:18765, rola P na 127.0.0.3:18765, osobne procesy) - pasek "W: gotowa | P: gotowa",
  potem nadzorca konczy oba procesy; (6) osobny proces trzyma `BEGIN EXCLUSIVE` (powt. 1) / `BEGIN IMMEDIATE` (powt. 2) na pliku
  bazy przez 16 s (`ROLLBACK`, bez zapisu), w tym czasie klikniecie `przycisk_ukruszona` przy otwartej pracy (plytka 8, gniazdo 1, zolta).
- Skany: 2 pliki ze zrodla proby B3 (`<PC-katalog>\app\dane_ref\syntetyczne_R59_P2`, tylko odczyt; kopie `uzup\robocze\skany\`):
  sha16 75db8c4f9ead0dab (okragla wieczorna, 44,1 MB) i df2e6a790700131d (kwadratowa wieczorna, 54,5 MB) - plytki WIECZORNE, zeby
  skan dostal status `przyjety` (w B3 pierwszego wykonawcy skany dostaly `plytka_nie_z_trybu`); podawane symulatorem programu
  (`narzedzia\symulator_skanera.py --ile 1`, osobny proces). Trzecia kopia (247ee785f428396f) nieuzyta.

## Polecenia (dokladne) i kody

1. `cmd /c <PC-katalog>\koordynator\robocze\odbior\T7\uzup\krok_4a_1.cmd` (krok lekki, 26 s): `p4a_1 KOD=0`.
2. `powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 4 -Kto T7uzup -Polecenie <PC-katalog>\koordynator\robocze\odbior\T7\uzup\krok_seria1.cmd`
   - `ciezkie.log`: START 04:51:28, KONIEC 05:06:14, kod 0. W pliku 15 wierszy postaci
   `call <PC-katalog>\t0\odbior_t12\Stanowisko\Polecenie.cmd <PC-katalog>\koordynator\robocze\odbior\T7\uzup\sonda_komunikaty.py --przypadek <n> [--wariant <x>] --powt <k> [--skan] --limit <s> > <przebieg>.log 2>&1 < NUL`
   (`set QT_QPA_PLATFORM=offscreen` na poczatku). Kody (`kody.txt`): p4a_2, p4b_1, p4b_2, p3_1, p3_2, p2_1, p2_2, p5a_1, p5a_2, p5d_1,
   p6_1, p6_2, p1_1, p1_2, p2c_1 - 15 z 15 `KOD=0`. Kody procesu programu: 0 we wszystkich etapach poza etapem 1 przebiegow p2_1 i p2_2
   (kod 1 = proces zakonczony przez nadzorce - to jest awaria przypadku 2).
3. Po serii: `PY -I robocze\czasy.py` (czasy z odczytow -> `czasy_komunikatow.txt`), `PY -I robocze\porzadek.py` (kopie zrzutow, kontrole).

Co jeszcze liczylo na PC (`ciezkie.log`): tor 2 - T11 `krok_B.cmd` od 04:49:34 (procesy z instalacji wspolnej `t0\odbior` widoczne do
konca serii). Pomiar nie jest kryterium czasowym; czasy "widoczny po" sa mierzone pod tym obciazeniem.

## Obserwacje dodatkowe (nie zmieniaja werdyktu)

1. Przypadek 3: komunikat "Brak folderu projektow" powstaje dopiero, gdy czeka skan. Start bez folderu i bez skanu (8 s): tylko pole
   paska "Folder projektow: brak folderu projektow" (wyroznione kolorem) i przycisk "Odswiez pule" - panelu nie ma (2 z 2). Folder
   znika w trakcie pracy: przez 13 s do konca zapisu nastepnego skanu NIC sie nie zmienia (pasek "plikow projektow: 17", 2 z 2);
   po skanie pasek zmienia sie po 0,5 s, program probuje analizy (log: "analiza skanu <sha16> nie dala wyniku (analiza)"), a panel
   pojawia sie po 5,4 s; skan nie ginie (po "Odswiez pule" przyjety).
2. Przypadek 1: komunikat jest przypiety do plytki. Gdy przychodzi wynik nastepnej plytki (po 33,9 s i 32,4 s), ekran przelacza sie na
   nia i panel "Analiza skanu nie powiodla sie" znika z obszaru komunikatow; zostaje kafelek "Plytka bez numeru / analiza nie powiodla
   sie" ze znaczkiem "ma komunikat" (zrzut `zrzut_p1_1_e1_02...`). Bez nastepnego skanu komunikat stoi (trwaly).
3. Przypadek 2: przy twardym zakonczeniu log po restarcie ma "zadan wznowionych 0, plikow znanych 1" i "(plik zastany - nadrabianie)",
   pliku `zadania_niezakonczone.json` nie ma; przy zwyklym zamknieciu okna plik `zadania_niezakonczone.json` jest miedzy etapami, log
   "zadan wznowionych 1, plikow znanych 2", po restarcie pliku nie ma. Tekst komunikatu w obu drogach ten sam. Osoba po restarcie
   wybierana ponownie (panel "Kto teraz pracuje?" stoi nad komunikatem do klikniecia).
4. Przypadki 4 / 5: komunikat ramki wieczornej widac tylko w trybie Wieczor, porannej tylko w trybie Poranek; pole paska "Ramki" jest
   w obu trybach. Komunikat poranny nie mowi, co sprawdzic przy ramce (mowi to komunikat wieczorny i podpowiedz paska).
5. Drobiazgi ekranu (zrzuty): na mapie plytki z bledem napis "Plytka analiza nie powiodla sie."; gdy na pasku pojawia sie licznik
   kolejki ("czekaja na projekty: 1"), pole "Ramki" jest uciete ("... P: brak po") - okno 1600 x 900 offscreen z czcionka zastepcza,
   na prawdziwym ekranie moze wygladac inaczej.
6. Komunikat "Ten sam projekt w dwoch gniazdach (7 razy)" w przebiegach z dwoma skanami to skutek danych testowych (dwa skany
   sztuczne z tymi samymi pracami), nie awarii.

## Zrzuty PNG

Zrobiono 53 zrzuty (`robocze\zrzuty\`), roznych obrazow 38 (reszta bajtowo identyczna - grupy w `zrzuty_i_kontrole.txt`); KAZDY obejrzany
(wszystkie 38 roznych obrazow otwarte narzedziem Read; pozostale 15 plikow to bajtowo identyczne kopie obejrzanych). Na zadnym nie ma nazw zlecen ani plikow: sa numery plytek i
gniazd, godziny, "Technik A" (osoba z ustawien instalacji), pola "Kuweta / Zab / Krazek" puste. 3 zrzuty p4a_1 maja kwadraty zamiast
liter (offscreen bez czcionek) - nieczytelne, nie sa dowodem. Pozostale 50: komunikaty czytelne (tytul pogrubiony, tekst, przyciski).
Dopuszczone do dowodow (12 szt., 77-231 KB, `zrzuty_dowody\`):

| Plik | Co widac (jedno zdanie) |
|---|---|
| `zrzut_p1_1_e1_01_komunikat_blad_analizy.png` | Czerwony panel "Plytka bez numeru: Analiza skanu nie powiodla sie" z tekstem "Zeskanuj plytke ponownie" nad lista plytek i mapa - czytelny, mowi, co zrobic. |
| `zrzut_p1_1_e1_02_pytanie_brak_numeru_plytki.png` | Po nastepnym skanie: mapa nowej plytki i pytanie "Podaj numer plytki"; panelu bledu juz nie ma, kafelek plytki z bledem ma "analiza nie powiodla sie" i "ma komunikat". |
| `zrzut_p2_1_e2_01_komunikat_wznowiono.png` | Po restarcie (twarde zakonczenie): niebieski panel "Program wznowil prace ... dokancza zalegle skany: 1." pod panelem wyboru osoby, plytka 8 z mapa odtworzona - czytelny. |
| `zrzut_p2c_1_e2_01_komunikat_wznowiono.png` | To samo po zwyklym zamknieciu okna: panel "Program wznowil prace" od pierwszego obrazu okna, pula jeszcze liczona. |
| `zrzut_p3_1_e1_03_start_bez_folderu_bez_skanu.png` | Start bez folderu i bez skanu: panelu o folderze NIE MA, tylko zolte pole paska "Folder projektow: brak folderu projektow" (i panel ramki wieczornej). |
| `zrzut_p3_1_e1_04_komunikat_pula_brak_folderu.png` | Czerwony panel "Brak folderu projektow" z przyciskiem "Odswiez pule" po zapisie skanu, na pasku "skany czekaja" - czytelny, mowi, co zrobic. |
| `zrzut_p3_1_e1_05_3b_po_zniknieciu_bez_skanu.png` | 10 s po zniknieciu folderu w trakcie pracy: nic o folderze, pasek nadal "plikow projektow: 17", mapa plytki 8. |
| `zrzut_p3_1_e1_06_3b_po_skanie.png` | Ten sam stan po zapisie nastepnego skanu: czerwony panel "Brak folderu projektow" nad mapa poprzedniej plytki - czytelny. |
| `zrzut_p4a_2_e1_02_komunikat_ramka_wieczorna_niedostepna.png` | Niebieski panel "Ramka wieczorna nie odpowiada" ("Sprawdz zasilanie ramki i siec stanowiska") i zolte pole paska "W: brak polaczenia | P: brak polaczenia" - czytelny. |
| `zrzut_p4b_1_e1_03_komunikat_ramka_niedostepna.png` | Tryb Poranek: niebieski panel "Ramka poranna nie jest podlaczona" z opisem pracy wedlug ekranu (Enter / Backspace / cyfry) - czytelny. |
| `zrzut_p5d_1_e1_02_ramki_gotowe.png` | Przed awaria 5d: pasek "Ramki: W: gotowa | P: gotowa", zadnego panelu (stan odniesienia; po zakonczeniu atrap ekran jak na zrzucie p4a_2). |
| `zrzut_p6_1_e1_01_komunikat_decyzja_niezapisana.png` | Czerwony panel "Decyzja NIE zostala zapisana" z niebieskim przyciskiem "Ponow teraz" i "Rezygnuje - nie zapisuj", obok otwarta praca (plytka 8, gniazdo 1) - czytelny, mowi, co zrobic. |

Niedopuszczone (41) - opis slowny: 8 x panel wyboru osoby "Kto teraz pracuje?" tuz po starcie (zolty; p4a_2, p4b_1, p4b_2, p3_1,
p3_2, p5a_1, p5a_2, p5d_1); 12 x panele ramek jak na zrzutach dopuszczonych (p4a_2, p4b_1, p4b_2, p5a_1, p5a_2, p5d_1, p3_1, p3_2);
4 x powtorzenie zrzutow przypadku 3 z p3_2 (obrazy jak dopuszczone z p3_1, inne godziny); 10 x ekran z "Ten sam projekt w dwoch
gniazdach (7 razy)" i "Nowy wynik czeka: Plytka bez numeru" po drugim skanie (p3_1, p3_2, p2_1, p2_2, p2c_1 - po 2); 1 x "Program
wznowil prace" z p2_2 (jak p2_1); 2 x p1_2 (jak p1_1); 1 x p6_2 (jak p6_1); 3 x p4a_1 (kwadraty). Zadnego nie odrzucono z powodu
nazw zlecen.

## Ograniczenia

1. Okno offscreen (O4): bez prawdziwego ekranu; zrzut to obraz rysowany przez okno 1600 x 900. Platforma offscreen nie ma czcionek
   systemu - od p4a_2 sonda podaje Qt katalog z kopia 5 czcionek systemowych (`QT_QPA_FONTDIR`); teksty czytane z widzetow nie zaleza
   od czcionek, uklad wierszy na zrzutach moze sie roznic od prawdziwego ekranu.
2. Program biegnie w procesie sondy (jak w T2 / T3), z opcja `--zamknij-po` (bezpiecznik); zegar sondy w watku okna.
3. Przypadek 4: sieci fizycznie NIE odcinano - "brak sieci" = adres ramek nieosiagalny (nazwa nierozwiazywalna / brak odpowiedzi).
   Nie mierzono: utraty sieci w trakcie dzialajacego polaczenia z prawdziwa ramka (najblizszy pomiar: 5d - atrapa zakonczona w
   trakcie, komunikat po 0,32 s), dosylania potwierdzen po powrocie sieci (testy czesci A pierwszego wykonawcy), Excela.
4. Przypadki 4 / 5 rano: piec pusty (bez plytek porannych) - zmierzono komunikat, nie rozkladanie kuwet bez ramki.
5. Przypadek 6: jedna decyzja ("Ukruszona") na jednej pracy; polecen innych niz decyzja o pracy (`polecenie_niezapisane`) i zapisu
   wyniku skanu przy zajetej bazie (`baza_zajeta`) na ekranie nie mierzono (plan: testy czesci A).
6. Czas "widoczny po": dokladnosc okresu zegara (150 ms) i przerw petli okna; w przypadku 6 okno stoi w kliknieciu 0,3-0,7 s.
7. Sonda zmieniana 2 razy w trakcie pomiaru (zapisane w naglowku / komentarzach): czcionki po p4a_1; od p2_1 bez automatycznych
   zrzutow paneli tla (wybor osoby, ramka wieczorna) poza przypadkami 4 / 5. Odczyty tekstow we wszystkich przebiegach te same.

## Stan po pracy

- Procesy `python` moje: 0 (kazdy przebieg: "procesy python pozostale po przebiegu: []"; 05:07 na PC zostaja PID 12012 i 5 procesow
  T11 z `t0\odbior` - cudze, nietkniete).
- Instalacja `odbior_t12` bez zmian: `wersja_biezaca.txt` = 0.3.1 (SHA-256 d9efe4074c06b76df743eb109bd414f65043a25ba26b8340c8406a9f2fd2e90b
  przed i po), `ustawienia.toml` SHA-256 1274f09de600273b69713fd327e1bfa1ba5fa76d098c3e6a50c114ab6da4d022 przed i po; plikow nowszych
  niz start pomiaru w `<PC-katalog>\t0\odbior_t12`: 0. Danych T12 nie ruszano. Repo `<REPO>`: bez zmian (tylko odczyt).
- `uzup\robocze\`: 1,1 GB (16 katalogow przebiegow ze skanami i bazami, kopie puli, czcionki, 53 zrzuty) - NIE do repo.

## Pliki w tym katalogu

`WYNIK.md`; `sonda_komunikaty.py` (sonda, ASCII); `krok_4a_1.cmd`, `krok_seria1.cmd`, `kody.txt`; dla kazdego z 16 przebiegow
`<przebieg>_podsumowanie.txt` (zdarzenia, panele z tekstami, pasek stanu) i `<przebieg>_odczyty_<etap>.txt` (sonda pisze je jako `.jsonl` z CRLF - po serii nazwy zmienione na `.txt`, konce linii na LF; wiersze JSON: kazda
zmiana ekranu; 19 plikow, razem 0,5 MB); `czasy_komunikatow.txt` (czasy i teksty wszystkich przebiegow w jednym pliku);
`zrzuty_i_kontrole.txt` (sumy zrzutow, kontrola nazw puli testowej: 50 nazw, 41 plikow tekstowych, 0 trafien; ASCII i LF: 0 naruszen
poza `.cmd`); `zrzuty_dowody\` (12 PNG). Przebiegi: p1_1, p1_2, p2_1, p2_2, p2c_1, p3_1, p3_2, p4a_1, p4a_2, p4b_1, p4b_2, p5a_1,
p5a_2, p5d_1, p6_1, p6_2.

## Do decyzji koordynatora / wlasciciela

1. (wlasciciel, O12) 6 tekstow komunikatow nie ma doslownie w PW zal. F (3 maja podobny wiersz) - uzupelnic zal. F albo zmienic napisy;
   lista w tabeli "Komunikaty a PW zal. F" (uzupelnia `..\t7_komunikaty.md` o to, co faktycznie stoi na ekranie).
2. (koordynator) Przypadek 3: czy "komunikat dopiero, gdy czeka skan" (bez skanu tylko pole paska - 3a - albo nic - 3b; po skanie w 3b
   panel po 5,4 s) wystarcza. Przyjeto: tak (technik widzi komunikat w chwili, gdy brak folderu ma skutek) - "ZAL z odstepstwem O12";
   wariant surowy: usterka do zgloszenia (program nie zauwaza znikniecia folderu do pierwszego skanu).
3. (koordynator) Przypadek 4: zastrzezenie pierwszego wykonawcy ("brak asercji komunikatu tekstowego") - pomiar pokazuje tekst na
   ekranie 4 z 4; zostaje ograniczenie: sieci fizycznie nie odcinano, a tekst jest wspolny z przypadkiem 5.
4. (koordynator) Zrzuty PNG a repo: `dowody_lf.py` ma `.png` na liscie plikow zakazanych w dowodach repo - 12 zrzutow lezy w
   `uzup\zrzuty_dowody\` poza repo (kazdy opisany wyzej jednym zdaniem); do repo moga isc pliki tekstowe. `dowody_lf.py --katalog uzup`
   uruchomiony na katalogu z `robocze\` konczy sie wyjatkiem `UnicodeEncodeError` (wypisuje nazwy plikow puli na konsole cp1250) -
   przed `git add` uruchamiac na kopii bez `robocze\` i bez `zrzuty_dowody\`.
5. (informacja) Przypadek 1: panel bledu analizy znika z obszaru komunikatow, gdy przyjdzie wynik nastepnej plytki (zostaje znaczek
   "ma komunikat" na kafelku) - do oceny, czy technik nie przeoczy koniecznosci ponownego skanu.
6. (informacja) Drobiazgi ekranu: "Plytka analiza nie powiodla sie." na mapie; uciete pole "Ramki" przy liczniku kolejki (offscreen).
