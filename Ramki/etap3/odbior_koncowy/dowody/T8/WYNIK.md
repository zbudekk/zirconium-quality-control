WERDYKT T8: ZAL - raport jednym poleceniem: tak (2 z 2, kody 3 i 3 = "ponizej progu", nie blad; 0,19 s i 0,21 s); metryki zgodne z liczeniem recznym wg definicji metryki.md: baza T2 5 z 5, baza T3 9 z 9 (wartosc, licznik, mianownik; wiersz M2 bez wartosci poza licznikiem); wartosci informacyjne 27 z 27 i 45 z 45; rozbieznosci 0; NIE ZMIERZONO 0; test_metryki.py 106 passed, kod 0. DO DECYZJI: wzory skrocone z tabeli planu testow daja inne liczby w 3 metrykach; "prace nieznane wieczor" na bazie T2 = 100 % z powodu pustego indeksu projektow

# T8 - Metryki (odbior, 21.11.2026) - WYNIK wykonawcy

Paczka 0.3.1 (commit 571e186), instalacja wspolna <K> = <PC-katalog>\t0\odbior\Stanowisko (tylko uruchamianie).
<ROB> = <PC-katalog>\koordynator\robocze\odbior\T8; kopie baz TYLKO w <ROB>\robocze\ (polecenie koordynatora; plan
pisal <ROB>\baza_t2.sqlite / <ROB>\baza_t3.sqlite - zmiana sciezki, patrz "Polecenia planu zmienione").
Czas pracy: 04:40 - 04:51 (budzet 45 min). Kroki lekkie, bez blokady `ciezki.ps1`.

## 1. Stan wejsciowy (04:40-04:41)

- Baza T2 (oryginal, nie otwierana do zapisu, program na niej nie uruchamiany): ...\odbior\T2\t2\dane\stanowisko.sqlite,
  106496 bajtow, 04:27:21, SHA-256 64e6cb6b6a261f1e1408215e0f711f2d627a04a3b2ebbc7ac312975126bbe554; obok tylko
  `stanowisko.sqlite.blokada` (0 bajtow); plikow -wal / -journal BRAK.
- Baza T3 (oryginal): ...\odbior\T3\t3\baza\stanowisko.sqlite, 94208 bajtow, 02:52:21, SHA-256
  6d67ba9db8b1cfd284a294b7c3dbcdf651efa7ca9b4779f0c7926843b1fc83e7 (= suma zapisana w WYNIK.md T3); obok tylko
  `.blokada` (0 bajtow); -wal / -journal BRAK.
- Kopie (Copy-Item 04:41): <ROB>\robocze\baza_t2.sqlite i baza_t3.sqlite - SHA-256 identyczne z oryginalami.
- Kontrola po wszystkich krokach (04:46): 4 sumy bez zmian (oryginaly i kopie), daty plikow bez zmian, obok kopii nie
  powstal zaden plik -wal / -journal (raport i sql_odczyt nic nie zapisaly).
- Get-Process python przed startem: tylko PID 12012 (znany, niczyj).

## 2. Raport jednym poleceniem (04:41:42 - 04:41:43; plik krok_t8_raporty.cmd, kody w kody.txt)

Polecenia (plan doslownie poza sciezka kopii bazy; `set QT_QPA_PLATFORM=offscreen`, wejscie `< NUL`, stderr osobno):

    call <PC-katalog>\t0\odbior\Stanowisko\Polecenie.cmd narzedzia\raport_metryk.py --baza <PC-katalog>\koordynator\robocze\odbior\T8\robocze\baza_t2.sqlite --tryb wieczor --od 2026-11-20 --do 2026-11-21 --json <PC-katalog>\koordynator\robocze\odbior\T8\t8_wieczor.json > ...\T8\t8_wieczor.txt 2> ...\T8\t8_wieczor_stderr.txt < NUL
    call <PC-katalog>\t0\odbior\Stanowisko\Polecenie.cmd narzedzia\raport_metryk.py --baza <PC-katalog>\koordynator\robocze\odbior\T8\robocze\baza_t3.sqlite --tryb oba --od 2026-11-17 --do 2026-11-19 --json ...\T8\t8_rano.json > ...\T8\t8_rano.txt 2> ...\T8\t8_rano_stderr.txt < NUL

- Okres bazy T2: sterownik T2 biegl 21.11 04:17-04:27, czyli przed 6:00 = doba 2026-11-20; wg pulapki planu
  `--od <dzien przed> --do <dzien T2>` = `--od 2026-11-20 --do 2026-11-21` (wszystkie 36 wpisow dziennika w dobie 20.11).
- Baza T2: kod **3** (PONIZEJ PROGU: nieznane_wieczor, powtorzone_wieczor - wg planu to nie FAIL T8), czas 0,19 s
  (4:41:42,72 -> 4:41:42,91), stderr pusty, strona 28 linii + JSON.
- Baza T3: kod **3** (PONIZEJ PROGU: top2, nieznane_rano, powtorzone_rano), czas 0,21 s (4:41:42,91 -> 4:41:43,12),
  stderr pusty, strona 37 linii + JSON.
- "Jedno polecenie": **TAK** - kazdy raport to jedno polecenie: strona na stdout + JSON z tymi samymi polami. Jedna
  proba kazdego, bez powtorek.
- Liczba wierszy tabeli metryk: baza T2 (tryb wieczor) 6 = 5 z wartoscia + M2 bez wartosci; baza T3 (tryb oba) 10 = 9 z
  wartoscia + M2 bez wartosci.
- Co jeszcze liczylo na PC: w chwili raportow nic (python: tylko PID 12012); T11 `krok_A.cmd` (tor 2) wystartowal
  04:42:47 - po raportach. T8 nie ma kryterium czasowego.

## 3. Liczenie reczne (04:42 - 04:50) - szczegoly w t8_recznie.md

Sposob: zapytania `PY -I <ODB>\narzedzia\sql_odczyt.py --baza <kopia> "<SELECT>"` (logi t8_sql_t2.log - 23 zapytania,
t8_sql_t3.log - 26 zapytan; kody: 0 x 48, 2 x 1), definicje z `opisy_modulow/metryki.md` (klasy prac porannych i "skan
aktywny" z `session.md`), tabela prawdy i pytania programu z plikow wyniku sterownika T2. Kodu `metryki.py` nie czytano.

### Baza T2 (wieczor) - 5 z 5 zgodnych

| Metryka | Raport | Recznie | Zgodne |
|---|---|---|---|
| falszywe alarmy | 0,0 %; 0 / 57 | 0 / 57 (czerwone z "OK": 0; prace 6 skanow przyjetych: 57) | TAK |
| prace nieznane - wieczor | 100,0 %; 57 / 57 | 57 / 57 (brak kandydata 0, ponizej progu 0, zaden kandydat w indeksie 57 - indeks pusty) | TAK |
| czas przy stanowisku | 9,3 min | 558 s = 9,300 min (1 posiedzenie 04:17:59 - 04:27:17, 49 chwil, najdluzsza przerwa 95 s) | TAK (roznica 0,000) |
| skany powtorzone - wieczor | 33,3 %; 3 / 9 | 3 / 9 = 0,33333 (do_powtorzenia 1, niezgodny_uklad 1, plytka_nie_z_trybu 1) | TAK |
| dni bez awarii | 1 dni ("za krotki okres") | 1 (1 doba z wpisami, 1 start + 1 stop, 0 awarii) | TAK |
| M2 | bez wartosci | tabeli testow nie ma w bazie | nie dotyczy |

Wartosci informacyjne strony / JSON (skany, czerwone, tryb cienia, posiedzenia, stabilnosc): 27 z 27 zgodnych.

### Baza T3 (SE10, tryb oba) - 9 z 9 zgodnych

| Metryka | Raport | Recznie | Zgodne |
|---|---|---|---|
| falszywe alarmy | 0,0 %; 0 / 8 | 0 / 8 | TAK |
| top-1 | 87,5 %; 7 / 8 | 7 / 8 (7 prac z projektem = 1. kandydat; 1 odrzucona "bez projektu"; praca bez propozycji poza) | TAK |
| top-2 (kuweta) | 87,5 %; 7 / 8 | 7 / 8 | TAK |
| prace nieznane - wieczor | 0,0 %; 0 / 8 | 0 / 8 | TAK |
| prace nieznane - rano | 11,1 %; 1 / 9 | 1 / 9 = 0,11111 (1. kandydat 0,45 < 0,6) | TAK |
| czas przy stanowisku wieczorem | 1,0 min (JSON 0,98333) | 59 s = 0,98333 min (4 posiedzenia, 1 mierzalne; 2 zmiany, 1 bez danych) | TAK (roznica 0,00000) |
| skany powtorzone - wieczor | 0,0 %; 0 / 3 | 0 / 3 | TAK |
| skany powtorzone - rano | 16,7 %; 1 / 6 | 1 / 6 = 0,16667 (zastapiony 1) | TAK |
| dni bez awarii | 3 dni ("za krotki okres") | 3 (3 doby z wpisami; 4 starty, kazdy po program_stop; 0 awarii) | TAK |
| M2 | bez wartosci | tabeli testow nie ma w bazie | nie dotyczy |

Zakres wymagany planem dla SE10 (top-1, top-2, nieznane rano): 3 z 3. Wartosci informacyjne (klasy prac 6 / 1 / 1 / 1,
czas rano 31,0667 / 15,5333 / 30,0833 min, czas pieca mediana 20,0333 i max 30,0167 min, stabilnosc): 45 z 45 zgodnych.

Uwaga do pulapki planu ("baza SE10 nie ma program_start - dni bez awarii = brak danych"): baza ze sterownika T3 MA
wpisy program_start / program_stop (4 / 4), raport podaje serie 3 dni z ocena "za krotki okres" - zgodne z liczeniem.

### Rozbieznosci i NIE ZMIERZONO

- Rozbieznosci raport - liczenie reczne (wg metryki.md): **0**.
- NIE ZMIERZONO: **0**. M2: raport nie podaje wartosci (wymaga zmiany schematu) - nie ma czego porownac, poza licznikiem.
- Metryk opartych na prawdzie scenariusza ("wykryte / przeoczone wobec prawdy") raport NIE ma - patrz sekcja 4.

## 4. Praca z ubytkiem niezgloszona przez program w T2 (skan 247ee785f428396f, pozycja 8, gniazdo 4)

- W bazie: praca id 50 (skan id 7, gniazdo 4): status_gniazda zielony, status_inspekcji ok, ubytki 0, decyzji 0.
- Raport nie zna prawdy; liczy ocene programu wobec decyzji technika: "czerwone 10: OK 0, Ukruszona 10, bez decyzji 0";
  "tryb cienia: ukruszone, ktorych program nie wskazal 15; wykrywalnosc wzgledem technika 40,0 % (10/25)".
- Te 15 to prace ZOLTE klikniete "Ukruszona" (decyzja `ukruszona_niewykryta`) - program je pokazal do sprawdzenia,
  a raport liczy je jako "nie wskazal" (zgodnie z definicja: "na pracy nieczerwonej").
- Praca przeoczona nie wchodzi do zadnego licznika raportu (zielona, technik jej nie kliknal). Wobec prawdy (plik
  sterownika T2): z ubytkiem 26 = czerwone 10 + zolte 15 + zielone 1, czyli 25 z 26 pokazanych czerwono albo zolto,
  10 z 26 czerwono; cale na czerwono 0 z 31. Raport tych liczb nie podaje i podac nie moze (M2 wymaga tabeli testow).

## 5. Test modulu (04:45:29 - 04:45:32; krok_t8_test.cmd)

    call <K>\Polecenie.cmd -m pytest <ST>\testy\test_metryki.py -q -p no:cacheprovider --rootdir <ST> > <ROB>\t8_test_metryki.log 2>&1 < NUL

Kod **0**; wiersz podsumowania `106 passed in 1.55s` (punkt odniesienia planu: 106 passed). Jedna proba. Kod programu w
tym tescie pochodzi z <REPO> (zwykly `-m pytest`; z paczki interpreter i pakiety) - ten sam commit. W tym czasie
liczyl T11 (tor 2); test nie jest czasowy.

## 6. Niejednoznaczne definicje / roznice opisow (do decyzji koordynatora / wlasciciela)

1. Tabela "Liczenie reczne" w PLAN_TESTOW.md T8 podaje wzory skrocone, ktore daja INNE liczby niz definicje z
   `metryki.md` (raport zgadza sie z `metryki.md`; plan sam wskazuje `metryki.md` jako zrodlo definicji):
   - falszywe alarmy, mianownik: plan "prace czerwone z decyzja" = T2 0 / 10, T3 0 / 1; raport i metryki.md "wszystkie
     prace skanow przyjetych" = 0 / 57 i 0 / 8 (wartosc 0,0 % ta sama);
   - prace nieznane wieczor, baza T2: plan (2 czlony: brak kandydata albo pokrycie < 0,6) = 0 / 57; raport i metryki.md
     (3 czlony, takze "zaden kandydat w indeksie") = 57 / 57;
   - top-1 / top-2, baza T3: plan ("kandydat1 = projekt potwierdzony / prace rozstrzygniete") = 8 / 8; raport i
     metryki.md (bez pracy bez propozycji, "bez projektu" = chybienie) = 7 / 8.
   Do poprawienia jest tekst tabeli planu (albo decyzja, ktora definicja obowiazuje). Wykonawca liczyl wg metryki.md.
2. Baza T2: "prace nieznane - wieczor" = 100,0 % (57 / 57, PONIZEJ progu 10 %) wynika wylacznie z pustego indeksu
   projektow w bazie (tabele `projekty` i `zlecenia`: 0 wierszy; folder projektow przebiegu T2 mial 15 folderow), a
   program dopasowal kazda z 57 prac (pokrycie 1. kandydata >= 0,8867). Do oceny: czy przy pracy wieczornej bez
   zbudowanego indeksu metryka ma pokazywac 100 % nieznanych (definicja to przewiduje), i dlaczego indeks w przebiegu
   T2 byl pusty (wykonawca nie badal przyczyny - poza zakresem T8).
3. "Wykrywalnosc wzgledem technika 40,0 % (10/25)" na bazie T2: prace zolte licza sie jako "program nie wskazal"
   (sekcja 4) - liczba zgodna z definicja, ale latwa do blednego odczytania; praca przeoczona (zielona) jest poza nia.
4. SE10: "klasy: nieznana 1" (praca z decyzja "bez projektu") i "prace nieznane 1 / 9" (praca z kandydatem 0,45) to
   dwie ROZNE prace o tej samej liczbie; o tym, ktora liczy metryka, rozstrzyga dopiero top-1 (7 / 8, odrzucone 1).
   Zgodne z definicja; przy czytaniu strony latwo je utozsamic.

## 7. Odstepstwa i polecenia planu

- Odstepstwa O<n>: brak (T8 wykonalny doslownie). NOWE: brak.
- Polecenia planu zmienione:
  1. sciezka kopii baz: `<ROB>\robocze\baza_t2.sqlite` / `baza_t3.sqlite` zamiast `<ROB>\baza_*.sqlite` (polecenie
     koordynatora: kopie baz tylko w `robocze\`); do polecen dodane `2> ..._stderr.txt` i `< NUL`;
  2. `sql_odczyt.py` odrzucil (kod 2) pierwsze zapytanie o schemat, bo w tekscie zapytania byly nazwy tabel z
     nazwami zlecen (w filtrze NOT IN); zadzialalo: `SELECT type, name, tbl_name FROM sqlite_master ORDER BY 1,2` oraz
     `SELECT name, sql FROM sqlite_master WHERE name IN ('skany','prace','decyzje','sesje_pieca','zdarzenia',...)`.
     Schemat tabel `projekty` / `zlecenia` odczytany z pliku `<ST>\stanowisko\baza.py` (nie z bazy). Liczenie top-1 /
     top-2 / indeksu: pojedyncze `SELECT count(DISTINCT p.id) FROM prace p JOIN projekty ...` (narzedzie dopuszcza).
- Poza planem (dodatkowo): policzone recznie WSZYSTKIE metryki bazy T3 (plan wymagal 3) i wartosci informacyjne obu
  stron.

## 8. Dane osobowe i dowody

- W dowodach tylko sha16 skanow, numery prac / skanow / gniazd i liczby. Jedno zapytanie (t8_sql_t2.log, zdarzenia ui)
  wypisalo pole `dane` z etykieta operatora sterownika T2 ("Technik A" - dana sztuczna sterownika, nie nazwa zlecenia);
  dalsze zapytania pola `dane` juz nie wypisuja. Do oceny T9.
- Kontrola na KOPII dowodow (robocze\dowody_kontrola, 04:48): `dowody_lf.py --napraw` kod 0, "plikow 14, naruszen 0
  (po naprawie)", bajtow spoza ASCII 0; CRLF -> LF w 8 plikach (robocze\dowody_lf.txt). Oryginaly w <ROB> maja CRLF
  z przekierowania `cmd >` - przed `git add` trzeba wykonac `dowody_lf.py --napraw` wg planu. Skanu T9 nie wykonywalem.
- Procesy po tescie (04:48): Get-Process python = PID 12012 (znany) oraz 30160 i 37356 (T11, start 04:47:35 - cudze);
  swoich procesow nie zostawilem. Repo <REPO> bez zmian (`git status --short` pusty).

Dowody w <ROB>: t8_wieczor.txt, t8_wieczor.json, t8_rano.txt, t8_rano.json, t8_recznie.md, t8_test_metryki.log (lista
planu) oraz kody.txt, krok_t8_raporty.cmd, krok_t8_test.cmd, t8_sql_t2.log, t8_sql_t3.log, t8_wieczor_stderr.txt,
t8_rano_stderr.txt (puste), WYNIK.md. Robocze (nie dowody): robocze\baza_t2.sqlite, robocze\baza_t3.sqlite,
robocze\dowody_kontrola\, robocze\dowody_lf.txt.

## 9. Werdykt czesci kryterium

| Czesc kryterium | Liczba | Werdykt |
|---|---|---|
| raport jednym poleceniem na bazie T2 | 1 polecenie, kod 3, 0,19 s, 6 wierszy metryk | ZAL |
| raport jednym poleceniem na bazie T3 | 1 polecenie, kod 3, 0,21 s, 10 wierszy metryk | ZAL |
| wartosci = policzone recznie, baza T2 | 5 z 5 (informacyjne 27 z 27) | ZAL |
| wartosci = policzone recznie, baza T3 | 9 z 9 (informacyjne 45 z 45; zakres planu 3 z 3) | ZAL |
| punkt odniesienia test_metryki.py | 106 passed, kod 0 | zgodne z planem |
| T8 lacznie | | **ZAL** (z lista "do decyzji" - sekcja 6) |
