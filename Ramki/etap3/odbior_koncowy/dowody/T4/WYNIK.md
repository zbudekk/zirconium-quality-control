WERDYKT T4: ZAL z odstepstwem O7 - top-1 "dobrze" 187 z 187 (projekt i wpis); plytka: zimna plytka 1 = 65,16 s (0 z 1 do 40 s), zimna plytki 2-10 maks. 35,53 s (9 z 9), ciepla plytki 1-10 maks. 31,09 s (10 z 10); pamiec: szczyt procesu 3,87 GB (3961,5 MB; + okno ok. 1,0 GB wg E3-A5, niemierzone); 400 wpisow tak, dwa wspolczynniki na plytce tak (10 z 10 plytek), STL w dwoch raportach tak (27 plikow); 3 kody 0

# T4 - Pula (odbior, 21.11.2026) - WYNIK wykonawcy

Paczka 0.3.1 (commit 571e186), instalacja wspolna <K> = <PC-katalog>\t0\odbior\Stanowisko (GOTOWE.txt 02:51:47).
<ROB> = <PC-katalog>\koordynator\robocze\odbior\T4. Tor ciezkich krokow: 2. Wykonawca: sesja T4 -> T2.

## Stan przed pomiarem (03:54:01)

- ciezkie.log: ostatni wpis "03:48:55 KONIEC odb-T1 tor 1 | kod 0" - zaden ciezki krok w toku, brak katalogow CIEZKI*.lock.
- Get-Process python: tylko PID 12012 (z 01:37, CPU 0,00 s, bez sciezki - znany, niczyj).
- Wolny RAM: 74655 MB z 95652.
- Dane: <PC-katalog>\e3\a5\pomiary\pula400: pula_400.csv 401 wierszy (400 wpisow + naglowek), stl\ 356 plikow STL
  (w 2 podkatalogach), plytki\ 10 skanow STL + 10 plikow prawdy JSON.

## Polecenia (plik krok_t4.cmd, przez blokade)

powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 2 -Kto T4 -Polecenie <PC-katalog>\koordynator\robocze\odbior\T4\krok_t4.cmd

Trzy polecenia planu DOSLOWNIE (z `call`, wejscie `< NUL`); <ROB>\pamiec i <ROB>\linie nowe i puste przed pierwszym.
Kody i godziny: kody.txt. Probnik procesow python co 5 s (lekki, osobny powershell): t4_procesy.csv.

## Przebieg 1 - czas, pula zimna (03:54:17,36 - 04:04:25,97; kod 0)

- ciezkie.log: "03:54:17 START T4 tor 2 | RAM 74550 MB" (kolejki nie bylo).
- pula: 400 wpisow, 400 geometrii, budowa 299,6 s (lekkie_policzone 400, 0 z dysku = pula zimna), pamiec po puli 794,2 MB.
- plytka 1 (pierwsza po zimnym starcie): 65,2 s (match 60,61 s, w tym linie brzegu od zera - inspect 41,3 s).
- plytki 2-10: 25,5 / 35,5 / 28,6 / 23,6 / 24,8 / 23,7 / 28,4 / 25,4 / 26,2 s -> maks. 35,5 s; do 40 s: 9 z 9.
- szczyt pamieci procesu (peak working set, psutil): 3961,5 MB.
- plik wyniku: t4\t4_surowe_czas_zimna.json.json (narzedzie dopisuje ".json" do --nazwa; polecenie planu podaje nazwe
  z rozszerzeniem - stad podwojne rozszerzenie; polecenia NIE zmienialem).

## Przebieg 2 - czas, pula ciepla (04:04:25,97 - 04:08:45,25; kod 0)

- pula: 400 wpisow, 400 geometrii, 1,0 s (lekkie_z_dysku 400, policzone 0 = pula ciepla), pamiec po puli 332,2 MB.
- plytki 1-10: 30,6 / 23,6 / 31,1 / 23,7 / 23,6 / 24,6 / 23,8 / 26,2 / 23,4 / 25,6 s -> maks. 31,1 s; do 40 s: 10 z 10.
- szczyt pamieci procesu: 3815,3 MB. Plik: t4\t4_surowe_czas_ciepla.json.json.

## Przebieg 3 - jakosc (04:08:45,25 - 04:17:18,53; kod 0)

- ZBIORCZO: k1 (pula bez blizniakow, 373 wpisy na plytke): prac 187, top1_projekt 187, top1_wpis 187, wpis_niejednoznaczny 0,
  bledow 0; k2 (pula 400 wpisow z blizniakami - kazda praca plytki na obu krazkach): prac 187, top1_projekt 187,
  top1_wpis 187, wpis_niejednoznaczny 0, bledow 0; prace cale 65, z czerwonym 0.
- pole `zielone` = 181 z 187 w k1 i k2 (status dopasowania gniazda zielony; 6 prac z trafnym top-1 ma status inny niz
  zielony) - zielonych ze zlym wpisem 0 (lista `bledy` pusta w 10 z 10 plytek).
- ciezkie.log: "04:17:18 KONIEC T4 tor 2 | kod 0 | RAM 74573 MB". Kod ciezki.ps1: 0. Caly krok: 23 min 1 s.
- Jedna proba kazdego przebiegu, bez powtorek. Zdarzen srodowiska (0xC0000142 / 0xC0000409) nie bylo: 3 kody 0.

## Liczby kryterium (tabela: t4_wynik.md)

| Czesc | Liczba | Werdykt |
|---|---|---|
| 400 wpisow | 400 wpisow / 400 geometrii | tak |
| dwa wspolczynniki na plytce | 10 z 10 plytek z pracami 1,20 i 1,25 (100 + 87 = 187 prac) | tak |
| STL w dwoch raportach | 27 plikow STL z dwoma wpisami (1,20 i 1,25); wpis_niejednoznaczny 0 z 187 | tak |
| top-1 "dobrze" 100 % | projekt 187 z 187, wpis 187 z 187 (k1 i k2); zielone ze zlym wpisem 0 | ZAL |
| plytka do 40 s - zimna, plytka 1 | 65,16 s (do 40 s: 0 z 1) | przekroczone -> O7 |
| plytka do 40 s - zimna, plytki 2-10 | maks. 35,53 s (do 40 s: 9 z 9) | ZAL |
| plytka do 40 s - ciepla, plytki 1-10 | maks. 31,09 s (do 40 s: 10 z 10) | ZAL |
| pamiec do 8 GB | szczyt procesu 3961,5 MB = 3,87 GB (zimna), 3815,3 MB (ciepla); okno wg raportu E3-A5 ok. 1,0 GB - nie mierzone w odbiorze; razem ok. 4,9 GB | ZAL |

Regula decyzji koordynatora nr 6 / O7: przekracza TYLKO pierwsza plytka po zimnym starcie (wariant b) ->
**ZAL z odstepstwem O7**, 65,16 s (poprzednie pomiary: 63,4 s E3-A5i, 67,9 s E3-A5). Przy puli cieplej 19 z 19 do 40 s.

## Co jeszcze liczylo na PC w czasie pomiarow (probnik t4_procesy.csv, 698 probek 03:54:12 - 04:17:34)

- Procesy tego kroku: PID 19368 (zimna; CPU 1876 s w 608 s = srednio ok. 3 watki), 28376 (ciepla), 28628 + 12056
  (jakosc: proces roboczy i nadrzedny) oraz procesy posrednie venv (11424, 33340, 22472 - po 8 MB, CPU 0). Probnik
  oznacza interpreter bazowy jako "INNE" (sciezka Python312, proces potomny python.exe z venv instalacji) - to procesy T4.
- Obce: PID 12012 (znany, niczyj, CPU 0,00 s przez caly czas); PID 32084 - 1 probka o 04:10:11 (46 MB, CPU 1,3 s,
  bez sciezki = inne konto albo proces juz konczony) - krotki proces obcy w trakcie przebiegu `jakosc` (poza czasami
  kryterium). W przebiegach `czas` (03:54:17 - 04:08:45) ZADNEGO obcego procesu python liczacego.
- ciezkie.log: w czasie T4 zaden inny ciezki krok (wpis przed: 03:48:55 KONIEC odb-T1; nastepny: START T2 tej sesji).
- Ta sesja w czasie pomiarow: tylko odczyty plikow (PowerShell / Read), bez pythona. Wolny RAM 70785 - 74687 MB.
- Uwaga do interpretacji czasow: `Polecenie.cmd` nie ogranicza liczby watkow bibliotek (regula "2 watki na proces" z
  wspolne.md dotyczy `py.cmd`); polecenie planu wykonane doslownie.

## Polecenia planu - zmiany

- Zadnego polecenia nie zmieniono. Roznica wobec tekstu planu: pliki wyniku nazywaja sie `t4\t4_surowe_czas_zimna.json.json`,
  `t4_surowe_czas_ciepla.json.json`, `t4_surowe_jakosc.json.json` (narzedzie dopisuje `.json` do `--nazwa`, a plan podaje
  `--nazwa` z rozszerzeniem). Narzedzie NIE probowalo pisac obok zestawu w <PC-katalog>\e3 (kopia zestawu niepotrzebna).

## Kontrola danych osobowych plikow surowych (przed kopiami do dowodow) - 04:35

`PY -I <ODB>\narzedzia\t9_dane_osobowe.py --nazwy-z <PC-katalog>\app\Prace_test --nazwy-z <PC-katalog>\e3\a5i\t4\drzewo\Cyrkon --nazwy-z <PC-katalog>\t0\odbior\dane\Cyrkon --cel <ROB>\t4 --cel <ROB>\t4_czas_zimna.log --cel <ROB>\t4_czas_ciepla.log --cel <ROB>\t4_jakosc.log --cel <ROB>\t4_wynik.md --cel <ROB>\WYNIK.md --cel <ROB>\kody.txt --cel <ROB>\t4_procesy.csv --cel <ROB>\krok_t4.cmd --wynik <ROB>\t4_t9.txt`
(BEZ `--dozwolone`) -> kod 0; samotest 435 nazw, 0 nieznalezionych postaci; przeszukanych plikow 11; trafien calych nazw 0
w 0 plikach; "czlony do wyjasnienia" 1 w 1 pliku (WYNIK.md - zwykle slowo bedace czescia nazwy; narzedzie nie podaje
ktore); WYNIK T9: ZAL. Pliki surowe `t4\t4_surowe_*.json.json`: 0 trafien -> kopie do dowodow wykonane:
t4_czas_zimna.json, t4_czas_ciepla.json, t4_jakosc.json (tresc bez zmian; skany oznaczone nazwami sztucznymi z generatora).

## Porzadek w <ROB> po tescie

- `<ROB>\pamiec` (400 plikow, 2,1 GB) i `<ROB>\linie` (2,6 MB) przeniesione po zakonczeniu wszystkich przebiegow do
  `<ROB>\robocze\pamiec` i `<ROB>\robocze\linie` (zasada: duze pliki robocze w `robocze\`; w czasie pomiarow lezaly
  tam, gdzie mowi plan). `<ROB>\t4\` = 3 pliki surowe.
- Get-Process python po kroku (04:17:36 i 04:35:30): tylko PID 12012 (znany, niczyj). Swoich procesow nie zostawilem.

## Do decyzji koordynatora / wlasciciela

1. O7: pierwsza plytka po zimnym starcie puli 400 wpisow = 65,16 s (prog 40 s); do tego budowa puli zimnej 299,6 s
   przed pierwsza plytka (pula ciepla: 1,05 s). Pozycja 3 w RAPORT.md sekcja 4a.
2. Pamiec: w odbiorze zmierzony szczyt JEDNEGO procesu (3,87 GB); proces okna niemierzony (wg E3-A5 ok. 1,0 GB) -
   suma ok. 4,9 GB wobec progu 8 GB (wg decyzji koordynatora nr 6).
3. Nazwy plikow wyniku z podwojnym rozszerzeniem `.json.json` (plan podaje `--nazwa` z `.json`) - do poprawy w tekscie
   planu, bez wplywu na wynik.

## Dowody w <ROB>

t4_wynik.md (tabela liczb, pula zimna i ciepla osobno), t4_czas_zimna.json, t4_czas_ciepla.json, t4_jakosc.json (kopie
plikow surowych po kontroli T9), t4_czas_zimna.log, t4_czas_ciepla.log, t4_jakosc.log, t4_procesy.csv, t4_t9.txt,
kody.txt, krok_t4.cmd, WYNIK.md. Robocze (nie dowody): `t4\` (pliki surowe), `robocze\` (pamiec puli, linie, probnik).

## Kontrola dowodow (kopia w robocze\dowody_kontrola; oryginaly w <ROB> bez zmian) - 04:38

- t9_dane_osobowe.py na kopii 12 plikow dowodow, BEZ --dozwolone: kod 0, 0 trafien calych nazw, 1 czlon do wyjasnienia
  (WYNIK.md) -> ZAL (robocze\t9_dowody.txt).
- dowody_lf.py --napraw na kopii: kod 0, "plikow 12, naruszen 0 (po naprawie)"; CRLF -> LF w 8 plikach (logi `cmd >`,
  kopie JSON, CSV, kody.txt), bajtow spoza ASCII 0 w 12 z 12 (robocze\dowody_lf.txt). W <ROB> logi maja nadal CRLF -
  przed `git add` trzeba wykonac `dowody_lf.py --napraw` wg planu.
