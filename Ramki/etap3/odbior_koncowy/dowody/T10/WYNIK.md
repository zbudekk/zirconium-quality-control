WERDYKT T10: ZAL (bez odstepstwa) - wyrownanie 40 z 40; top-1 "dobrze" 276 z 276; falszywe czerwone na pracach calych 0 z 127; kod 0; liczby rowne R59 pkt 6.2

# T10 - Regresja silnika - WYNIK (odbior koncowy etapu 3, paczka 0.3.1, 21.11.2026)

Wykonawca: sesja "T10" (tor 2 ciezkich krokow, jedyna sesja pomiarowa fali T-A).
Kryterium (plan etapu sekcja 7, przepisane w PLAN_TESTOW.md T10): zestawy R59 (40 skanow) - wyrownanie 40 z 40,
top-1 "dobrze" 100 %, falszywe czerwone na pracach calych 0 (R59 pkt 6.2).

## 1. Stan wyjsciowy i przygotowanie (przed GOTOWE.txt)

- 02:47 start sesji; przeczytane: odbior-wspolne.md, wspolne.md, PLAN_TESTOW.md (wstep, Oznaczenia, Ustalenia
  koordynatora, T10 w calosci, wiersze T10 w "Stan sprawdzenia polecen", "Zrodla liczb kryteriow"), raport
  R59_2026-11-14.md pkt 6.1-6.3, kod narzedzia `narzedzia/metryki_P3a.py` i `stanowisko/porownaj.py`
  (`metryki`, `scenariusz`, `metryki_inspekcji`) z `<REPO>` (571e186) - tylko odczyt.
- Dane (tylko odczyt, policzone 02:47): `<PC-katalog>\app\dane_ref\syntetyczne_R59_P2` 24 STL + 24 pliki prawdy,
  `syntetyczne_R59_P3a` 16 + 16 = 40 skanow (wszystkie pasuja do wzorca `skan_*.stl`; innych plikow 0);
  projekty `<PC-katalog>\app\Prace_test`: 15 folderow, 17 STL. Zgodne z planem.
- `<ROB>` = `<PC-katalog>\koordynator\robocze\odbior\T10\`; `<K>` = `<PC-katalog>\t0\odbior\Stanowisko`.
- Plik kroku: `<ROB>\krok_t10.cmd` (CRLF; `call`, `< NUL`, `echo ... KOD=%ERRORLEVEL%` do `<ROB>\kody.txt`,
  `exit /b <kod>`). Polecenie w pliku = polecenie planu doslownie (z `<K>` i `<ROB>` rozwinietymi), pelne 40 skanow,
  `--procesy 1`, bez `--limit`.
- Wlasny skrypt liczenia kryterium z plikow wyniku: `<ROB>\t10_licz.py` (stdlib, `PY -I`; liczy z rekordow skanow i z
  plikow prawdy, `zbiorczo` narzedzia i log tylko porownuje). Proba skryptu na wyniku proby `--limit 2` z nocy
  (`robocze\odb\inst\t10`, to NIE jest wynik odbioru): dziala, 2 rekordy; mianownik "dobrze" z plikow prawdy = 276.

## 2. Definicje uzyte do liczenia (zrodlo: R59 pkt 6.2 + kod `porownaj.py`)

- wyrownanie OK: skan ma rekord w wyniku (nie "uklad niezgodny") i `metryki.wyrownanie.max_przesuniecie_mm` < 0,05 mm
  (R59 pkt 6.2: "wyrownanie 100 % skanow, blad < 0,05 mm"); mianownik = 40 skanow wejsciowych.
- top-1 "dobrze": praca z pliku prawdy w scenariuszu "dobrze" (bez drgniecia, ulozenie "dobrze", pokrycie >= 1,0);
  trafny = pierwszy kandydat gniazda w wyniku == projekt z prawdy; brak gniazda w wyniku albo brak kandydata = bledny.
  Mianownik licze z plikow prawdy (nie z wyniku narzedzia).
- falszywe czerwone na pracach calych (R59 pkt 6.1 wiersz "prace cale: z czerwonym", pkt 6.2 "0 / 127"): praca cala =
  praca z prawdy BEZ ubytkow, bez drgniecia, z trafnym top-1 i policzona inspekcja; falszywe czerwone = taka praca
  ze statusem inspekcji "ubytek" (gniazdo czerwone). Pola narzedzia: `razem.prace_cale_z_czerwonym` /
  `razem.prac_calych`. UWAGA: to NIE jest licznik "falszywe ubytki (miejsca) / w tym czerwone" (R59: 7 / 2) - ten
  dotyczy takze prac z ubytkami w prawdzie i nie nalezy do kryterium (R59 pkt 6.2, akapit "Odstepstwa ... poza
  kryteriami").
- Dodatkowo (informacja, liczenie ostrozniejsze): kazda praca bez ubytkow w prawdzie (takze z drgnieciem, bokiem, z
  blednym top-1) z gniazdem czerwonym albo statusem "ubytek".

## 3. Przebieg

- 02:51:47 `T0\GOTOWE.txt` (przeczytany 02:52:10): instalacja wspolna 0.3.1 gotowa (T0 zielone + krok `/testy`);
  `<K>\wersja_biezaca.txt` = 0.3.1; `<K>\wersje\0.3.1\program\narzedzia\metryki_P3a.py` ma te sama sume SHA-256 co plik w
  `<REPO>` (0ac16e9ea597d496...), brak `NIEDOKONCZONA.txt`. Czekanie na GOTOWE: ok. 4,5 min (bez zuzycia limitu 45 min).
- 02:52:25 start kroku (proces odlaczony, `Start-Process -WindowStyle Hidden`, PID powershell 5440):
  `powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 2 -Kto T10 -Polecenie <PC-katalog>\koordynator\robocze\odbior\T10\krok_t10.cmd`
  Polecenie w `krok_t10.cmd` (jedna linia, doslownie z planu):
  `call <PC-katalog>\t0\odbior\Stanowisko\Polecenie.cmd narzedzia\metryki_P3a.py --skany <PC-katalog>\app\dane_ref\syntetyczne_R59_P2 <PC-katalog>\app\dane_ref\syntetyczne_R59_P3a --projekty <PC-katalog>\app\Prace_test --wyjscie <PC-katalog>\koordynator\robocze\odbior\T10\t10 --nazwa t10_surowe_metryki.json --procesy 1 --ustawienia <PC-katalog>\t0\odbior\Stanowisko\ustawienia.toml > <PC-katalog>\koordynator\robocze\odbior\T10\t10_surowe.log 2>&1 < NUL`
- 02:52:26 `ciezkie.log`: "START T10 tor 2 | RAM 77258 MB" (kolejki nie bylo). Procesy python tego kroku: PID 35176
  (`<K>\wersje\0.3.1\venv\Scripts\python.exe`) + PID 39012 (interpreter bazowy - proces potomny venv), oba 02:52:26.
- Wynik kazdego skanu narzedzie dopisuje do `t10_surowe.log` zaraz po jego policzeniu (wiersz `skan_...`, `flush`);
  plik JSON powstaje dopiero po 40. skanie (tak dziala narzedzie - nie zmieniam).
- 03:06:49 koniec kroku. Kod wyjscia 0: `kody.txt` "t10_metryki KOD=0", `ciezkie.log` "KONIEC T10 tor 2 | kod 0 |
  RAM 74035 MB". Czas scienny kroku 02:52:26,32 - 03:06:49,34 = 14 min 23 s (863 s); `czas_calosci_s` narzedzia 861,4 s.
  Jeden przebieg, bez powtorek (to jest wynik).
- Log `t10_surowe.log`: 437 wierszy = 40 wierszy skanow + 14 wierszy podsumowania (ZBIORCZO 1, GNIAZDA 4,
  SCENARIUSZ 4, POLOZENIE 3, PRACE CALE 1, sciezka pliku wyniku 1) + 1 pusty + 382 ostrzezenia biblioteki Open3D
  ("[Open3D WARNING] Too few correspondences (N) after mutual filter, fall back to original correspondences." - stderr
  w tym samym pliku przez `2>&1`; to nie blad programu); "Traceback" 0; "NIE PASUJE DO UKLADU" 0.
- 03:07 `Get-Process python`: procesow tego kroku brak (PID 5440, 35176, 39012 nie zyja). Zostaly cudze: 12012 (znany,
  01:37), 18516 + 18764 (start 02:53:21 = T1 `krok_4.cmd`), 29076 + 35592 (start 03:07:19) - nie ruszane.
- 03:08 liczenie wlasne: `PY -I <ROB>\t10_licz.py --wynik-json <ROB>\t10\t10_surowe_metryki.json --log <ROB>\t10_surowe.log --skany <PC-katalog>\app\dane_ref\syntetyczne_R59_P2 <PC-katalog>\app\dane_ref\syntetyczne_R59_P3a --md <ROB>\t10_wynik.md --json <ROB>\t10_licz.json`
  -> kod 0 (kod 0 = wszystkie 3 czesci kryterium spelnione). Po pierwszym spojrzeniu w wynik skrypt zostal uzupelniony
  o gniazda z kilkoma wpisami (kilka fragmentow w jednym gniezdzie - narzedzie liczy kazdy wpis osobno; ja licze
  dodatkowo kazda prace z prawdy raz) - stad dwie liczby w wierszu "prace cale" (127 wpisow / 126 prac).
- 03:09:28 kontrola danych osobowych plikow surowych (plan: `T9 N --cel ... --wynik <ROB>\t10_t9.txt`, BEZ `--dozwolone`):
  `PY -I <PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy\narzedzia\t9_dane_osobowe.py --nazwy-z <PC-katalog>\app\Prace_test --nazwy-z <PC-katalog>\e3\a5i\t4\drzewo\Cyrkon --nazwy-z <PC-katalog>\t0\odbior\dane\Cyrkon --cel <ROB>\t10\t10_surowe_metryki.json --cel <ROB>\t10_surowe.log --wynik <ROB>\t10_t9.txt`
  -> kod 0; samotest "nieznalezionych 0"; szukanych nazw 435, czlonow 48; przeszukanych plikow 2; trafien calych nazw 0;
  czlonow do wyjasnienia 0; "WYNIK T9 (cale nazwy): ZAL (0 trafien)". (`N` planu to skrot opcji `--nazwy-z ... --baza ...`
  z sekcji T9; T10 nie ma wlasnej bazy, wiec podalem 3 katalogi nazw: pule testowa, drzewo a5i i folder Cyrkon
  instalacji wspolnej; bazy `<K>\dane` nie otwieralem.)
- 03:10 kopie po kontroli (kod 0): `t10_metryki.json` = kopia bajt w bajt `t10\t10_surowe_metryki.json` (SHA-256 obu
  9264a2756e80d4db..., 1 623 926 B); `t10.log` = kopia `t10_surowe.log` (SHA-256 surowego 13039cbf087eb27f..., 59 667 B)
  po `PY -I <ODB>\narzedzia\dowody_lf.py --katalog <ROB>\robocze\lf --napraw --wynik <ROB>\robocze\lf_naprawa.txt`
  (kod 0: `t10.log` CR 437 -> 0, bajtow spoza ASCII 154 -> 0, znakow zamienionych na "?" 0; `kody.txt` CR 3 -> 0).
  Pliki surowe zostaly nietkniete (naprawa szla na kopiach w `robocze\lf`).

## 4. Liczby kryterium (policzone przeze mnie z rekordow skanow i plikow prawdy; szczegoly: `t10_wynik.md`, `t10_licz.json`)

| Czesc kryterium | Moje liczenie | `zbiorczo` narzedzia | Wiersz logu | Werdykt czesci |
|---|---|---|---|---|
| wyrownanie 40 z 40 | 40 z 40 (40 skanow wejsciowych, 40 rekordow, uklad niezgodny 0; kazdy max blad < 0,05 mm, najwiekszy 0,0143 mm) | `plate_match.wyrownanie_ok` 40 / `skanow` 40 | 40 wierszy skanow | ZAL |
| top-1 "dobrze" 100 % | 276 z 276 prac (mianownik z plikow prawdy; bledne 0; brak gniazda w wyniku 0) | `top1_per_scenariusz.dobrze`: `prac` 276, `top1_bledny` 0 | - | ZAL |
| falszywe czerwone na pracach calych 0 | 0 z 127 wpisow (definicja narzedzia) = 0 z 126 prac z prawdy liczonych raz; lista pusta | `razem.prace_cale_z_czerwonym` 0 / `razem.prac_calych` 127 | "PRACE CALE: 127, z czerwonym 0, z alarmem ... 0, nie sprawdzono 9" | ZAL |

- Moje liczby zgodne z sekcja `zbiorczo` i z wierszem logu: TAK (wszystkie porownania w `t10_licz.json` -> `werdykty`).
- Lista falszywych czerwonych na pracach calych (zestaw / plytka / gniazdo / sha16): PUSTA (0 pozycji).
- Liczenie szersze (informacja): 150 prac bez ubytkow w prawdzie (kazdy scenariusz, takze z drgnieciem i z blednym
  top-1) - z gniazdem czerwonym albo statusem "ubytek": 0.
- Roznica 127 / 126: jedna praca cala lezaca bokiem (zestaw P3a, plytka okragla_poranna nr 9 seed 313, gniazdo 7) ma w
  wyniku 2 wpisy (2 fragmenty w gniezdzie), oba z trafnym projektem i statusem "nie sprawdzono" - narzedzie liczy ja
  2 razy. Gniazd z kilkoma wpisami jest 14 (13 prac bokiem, 1 z drgnieciem; w scenariuszu "dobrze" 0).

## 5. Porownanie z liczbami odniesienia (plan T10)

| Liczba | Ten przebieg (paczka 0.3.1) | R59 pkt 6.2 | E3-A5 runda 4 (pula) | Roznica na gorsze |
|---|---|---|---|---|
| wyrownanie | 40 z 40 (max 0,0143 mm) | 40 z 40 (max 0,0143 mm) | 40 z 40 | brak |
| top-1 "dobrze" | 276 z 276 | 276 z 276 | 276 z 276 | brak |
| falszywe czerwone na pracach calych | 0 z 127 | 0 z 127 | 0 z 132 | brak (licznik 0; mianownik 127 jak w R59, o 5 mniej niz w przebiegu A5 z pula) |

Regresji wobec R59 pkt 6.2 w liczbach kryterium: 0.

## 6. Czasy (NIE sa kryterium T10; mierzone pod obciazeniem)

- Czas na skan (pole `czas_s.razem` kazdego z 40 rekordow): min 9,9 s / mediana 20,7 s / max 50,88 s; suma 849,6 s;
  mediany etapow: plate 2,42 s, match 16,95 s, inspect 1,5 s. Najdluzszy jest pierwszy skan (50,88 s).
- Calosc: 14 min 23 s (plan szacowal 40-60 min; R59 pkt 6.1, przebieg jednoprocesowy 14.11 na starszym kodzie:
  mediana 11,7 s, 40 skanow w 8 min 52 s).
- Co jeszcze liczylo na PC w czasie 02:52:26 - 03:06:49 (wg `<PC-katalog>\koordynator\log\ciezkie.log`):
  tor 1: T1 `krok_4.cmd` (pelny pytest) od 02:53:21, trwal jeszcze po koncu T10;
  tor 4: T12 `krok_A2.cmd` 02:52:15 - 02:53:42, `krok_A4.cmd` 02:54:09 - 02:54:39, `krok_B.cmd` 02:55:37 - 02:59:47,
  `krok_B_uzup.cmd` 03:00:51 - 03:03:55; potem T7 `krok_A.cmd` 03:03:56 - 03:08:06;
  tor 3: T5 `krok_t5_b4.cmd` 03:01:18 - 03:03:56;
  do tego testy lekkie innych wykonawcow (poza `ciezkie.log`). Wolny RAM w tym czasie 67-77 GB z 95,6 GB.
- Postep co 20 s (godzina, liczba policzonych skanow): `robocze\postep.txt`.

## 7. Liczby poza kryterium (informacja; nie zmieniaja werdyktu)

Odniesienie: R59 pkt 6.1 kolumna "R59, zestawy dzisiejsze" i plik wyniku przebiegu jednoprocesowego R59 z 14.11
(`<PC-katalog>\r59\program\Ramki\stanowisko\dane\wyniki_R59\metryki_R59_sekwencyjnie.json`, tylko odczyt).

| Miara | Ten przebieg | R59 |
|---|---|---|
| top-1 razem | 388 z 397 | 382 z 397 |
| wykrycie dowolna metoda, razem | 226 z 249 | 221 z 248 |
| metoda A / B / czerwone | 189 / 110 / 83 | 184 / 107 / 79 |
| prace cale z alarmem (czerwone / zolte "sprawdz") | 0 z 127 | 0 z 127 |
| falszywe ubytki (miejsca) / w tym czerwone | 7 / 2 | 7 / 2 |
| drgniecie wykryte / falszywe "skan ponownie" | 36 z 39, 2 | 35 z 39, 2 (powtorka: 1) |
| poprawki | 5 z 14 | 5 z 14 |
| projekty pominiete | 283 | 283 |
| statusy gniazd (zielony / czerwony / zolty / szary / pomaranczowy) | 116 / 66 / 201 / 26 / 4 | 150 / 65 / 161 / 33 / 4 |

- 2 falszywe czerwone MIEJSCA: jak w R59 na plytce zestawu P3a okragla_poranna nr 9 seed 311, scenariusz "bokiem"
  (praca z ubytkami w prawdzie) - to nie jest "praca cala", nie wchodzi do kryterium (R59 pkt 6.2).
- 2 falszywe "skan ponownie" (prace bez drgniecia w prawdzie, obie bokiem, obie z ubytkami w prawdzie): zestaw P3a /
  plytka okragla_wieczorna nr 8 seed 300 / gniazdo 11 / sha16 066fcc6858e01759 oraz zestaw P3a / plytka
  okragla_wieczorna nr 8 seed 341 / gniazdo 4 / sha16 6570c1796f152c01. Liczba jak w R59 (2) - do zestawienia z
  pozycja 15 sekcji 4a `RAPORT.md`.
- Statusy gniazd: o 34 mniej zielonych i o 40 wiecej zoltych niz w R59. Porownanie gniazdo po gniazdzie z plikiem R59
  (`robocze\porownanie_statusow_R59.txt`; 383 gniazda z jednym wpisem w obu wynikach, 14 gniazd z kilkoma wpisami
  nie porownane):
  - 23 x zielony -> zolty: 22 x "ok" -> "nie sprawdzono" (19 prac czesciowo widocznych, 3 bokiem) i 1 x "ok" ->
    "sprawdz" (czesciowo). Statusu "nie sprawdzono" nie ma w pliku wyniku R59 (w tym przebiegu: 38 wpisow).
  - 4 x zolty "sprawdz" -> czerwony "ubytek" (scenariusz "dobrze", prace z ubytkami w prawdzie); 4 x szary -> zolty.
  - Na slabsza strone, 4 gniazda (wszystkie poza kryterium T10):
    3 x czerwony "ubytek" -> zolty "sprawdz" na pracach Z ubytkami w prawdzie (nadal alarm, ale zolty):
    P3a / okragla_poranna nr 9 seed 311 / gniazdo 1 / sha16 bc137fec92efdba6 (bokiem);
    P3a / okragla_poranna nr 9 seed 351 / gniazdo 5 / sha16 5a3a03ddfb5d8577 (dobrze);
    P3a / okragla_wieczorna nr 8 seed 340 / gniazdo 1 / sha16 ea47d2adbe45456e (dobrze);
    1 x zielony -> szary: P3a / poranna nr 5 seed 330 / gniazdo 8 / sha16 ea47d2adbe45456e (praca czesciowo
    widoczna, bez ubytkow w prawdzie; top-1 w tym przebiegu nietrafny, w R59 gniazdo bylo zielone).
  - W scenariuszu "dobrze" zielonych 111 (R59: 111).
  Nie oceniam tych roznic - kryterium T10 ich nie obejmuje, a miedzy przebiegami jest rozrzut RANSAC (plan: 1 gniazdo);
  podaje, bo liczby roznia sie od tabeli R59.
- Prace cale "nie sprawdzono": 9 z 127 (powod "dane": 9) - zolte, nie alarm.
- W 16 z 40 rekordow skanow jest po 1 ostrzezeniu programu "dolki kodu poza skanem (4 z 4 niewidocznych) ..." -
  nie dotyczy kryterium.

## 8. Dowody w `<PC-katalog>\koordynator\robocze\odbior\T10\`

| Plik | Co to |
|---|---|
| `WYNIK.md` | ten plik |
| `t10_wynik.md` | liczby kryterium policzone skryptem `t10_licz.py` (lista planu) |
| `t10_metryki.json` | KOPIA surowego wyniku narzedzia, po kontroli T9 kod 0 (lista planu) - patrz "do decyzji" 1 |
| `t10.log` | kopia logu po `dowody_lf.py --napraw` (lista planu) |
| `t10_t9.txt` | wynik kontroli danych osobowych plikow surowych (lista planu) |
| `t10_licz.py`, `t10_licz.json` | skrypt liczenia wykonawcy i jego pelny wynik (liczby, listy, porownania) |
| `krok_t10.cmd`, `kody.txt` | plik kroku i kody wyjscia (kody.txt po zamianie CRLF na LF) |
| `t10_dowody_lf.txt`, `t10_t9_dowody.txt` | kontrola koncowa zestawu dowodow (ASCII + LF; dane osobowe) |

Poza dowodami (zostaja w `<ROB>`, nie do repo): surowe `t10\t10_surowe_metryki.json` i `t10_surowe.log` (nazwy z planu,
czlon `surowe`), podkatalog `robocze\` (wyjscie `ciezki.ps1`, postep, proba skryptu, porownanie z R59, kopie do kontroli).

Kontrola koncowa zestawu dowodow (kopie plikow z tabeli w `robocze\dowody_kontrola\`, bez `--napraw`):
- `PY -I <ODB>\narzedzia\dowody_lf.py --katalog <ROB>\robocze\dowody_kontrola --wynik <ROB>\t10_dowody_lf.txt` -> kod 1:
  plikow 9, naruszen 1 = `t10_metryki.json` "ZAKAZANY ... 1586 KB > 1024 KB"; pozostale 8 plikow OK (ASCII + LF,
  `krok_t10.cmd` CRLF).
- `PY -I <ODB>\narzedzia\t9_dane_osobowe.py --nazwy-z <PC-katalog>\app\Prace_test --nazwy-z <PC-katalog>\e3\a5i\t4\drzewo\Cyrkon --nazwy-z <PC-katalog>\t0\odbior\dane\Cyrkon --cel <ROB>\robocze\dowody_kontrola --wynik <ROB>\t10_t9_dowody.txt`
  -> kod 0, trafien calych nazw 0, czlonow do wyjasnienia 0 (9 plikow).
  Proba 1 tej kontroli (03:13, wynik w `robocze\t10_t9_dowody_proba1.txt`): kod 0, calych nazw 0, ale "czlony nazw do
  wyjasnienia: 8 w 3 plikach" (`t10_licz.py` x3, `t10_wynik.md` x2, `WYNIK.md` x3; jeden czlon, sha16 5054e1b14a2e813f).
  Wyjasnienie: to zwykle slowo polskie z MOJEGO tekstu opisu (naglowek jednego z liczen), ktore jest tez czlonem
  jednej z nazw - sprawdzone przez porownanie sha16 slow moich plikow, bez wypisywania nazw. Slowo zastapilem innym w
  `t10_licz.py` i `WYNIK.md`, `t10_wynik.md` i `t10_licz.json` wygenerowalem ponownie (liczby bez zmian) i kontrole
  powtorzylem - wynik wyzej to proba 2.

## 9. Werdykt, odstepstwa, sprawy do decyzji

**WERDYKT T10: ZAL** (bez odstepstwa) - wyrownanie 40 z 40 ZAL; top-1 "dobrze" 276 z 276 ZAL; falszywe czerwone na
pracach calych 0 z 127 ZAL; kod wyjscia narzedzia 0; liczby rowne R59 pkt 6.2.

Odstepstwa od kryterium: brak. Powtorek przebiegu: 0.

Polecenia planu zmienione: zadne (polecenie pomiaru doslownie, pelne 40 skanow, `--procesy 1`). Doprecyzowania wykonawcy:
1. `N` w poleceniu kontroli T9 (skrot planu) = 3 x `--nazwy-z` (pula testowa, drzewo a5i, folder Cyrkon instalacji
   wspolnej); bez `--baza` (T10 nie ma bazy).
2. `ciezki.ps1` uruchomiony jako proces odlaczony (`Start-Process -WindowStyle Hidden`, zalecenie `wspolne.md`).
3. `dowody_lf.py --napraw` wykonany na kopiach (`robocze\lf`), nie na calym `<ROB>` - skrypt naprawia pliki w miejscu i
   zmienilby pliki surowe.

Do decyzji koordynatora:
1. `t10_metryki.json` (pozycja listy dowodow planu) ma 1 623 926 B = 1586 KB; `dowody_lf.py` odrzuca pliki > 1024 KB
   ("ZAKAZANY", kod 1) i takich plikow nie naprawia, a plik ma 69 070 koncow CRLF i 2843 bajty spoza ASCII (po samej
   zamianie CRLF -> LF mialby 1518 KB - nadal ponad limit). Kopia lezy w `<ROB>` jak kaze plan (przeszla T9: 0 trafien).
   Do repo w tej postaci nie przejdzie przez `dowody_lf.py`; mozliwosci: (a) do repo ida `t10_wynik.md` + `t10_licz.json`
   (5 KB, wszystkie liczby i listy), a `t10_metryki.json` zostaje w `<ROB>`; (b) wyjatek od limitu. Zapis zwarty tych
   samych danych w ASCII mialby 957 KB, ale to juz nie "kopia" - nie robilem.
2. Statusy gniazd rozne od tabeli R59 (116 / 66 / 201 / 26 / 4 wobec 150 / 65 / 161 / 33 / 4) - sekcja 7; poza kryterium
   T10. Glowna roznica: 22 gniazda "ok" -> "nie sprawdzono" na pracach czesciowo widocznych / bokiem. 4 gniazda na
   slabsza strone (3 x czerwony -> zolty na pracach z ubytkami, 1 x zielony -> szary) - wypisane w sekcji 7.
3. Pozycja 15 sekcji 4a `RAPORT.md`: w T10 falszywe "skan ponownie" = 2 prace (obie bokiem, zestaw P3a) - tyle samo co
   w R59 pkt 6.2.
4. Czasy T10 (mediana 20,7 s na skan) mierzone przy pelnym pytest T1 i krokach T12 / T5 / T7 w toku - nie sa kryterium
   T10 i nie nadaja sie na odniesienie czasu plytki (to mierzy T4).
