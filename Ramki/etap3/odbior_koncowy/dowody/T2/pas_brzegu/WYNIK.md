WYNIK: pas 1,5 odtwarza T10 (40 z 40, 276 z 276, 0 z 127); przy 1,6 / 1,75 / 2,0 praca z T2 jest zolta i kryteria T10 dalej spelnione, ale zadna wartosc nie daje czystej poprawy: 9 / 6 / 11 innych gniazd prac z ubytkiem zmienia status w obie strony, w tym 1 praca z ubytkiem spada z zoltego na zielono.

# pas_brzegu - pomiar "co by bylo, gdyby" dla progu [inspect] pas_brzegu_mm (21.11.2026, 05:45-07:00)

Dane do decyzji wlasciciela; niczego nie zmieniono w repo, w instalacji ani w progach (kontrola w pkt 7).
<K> = <PC-katalog>\t0\odbior\Stanowisko (paczka 0.3.1); <R> = <PC-katalog>\koordynator\robocze\pas_brzegu.

## 1. Pytanie i fakty wyjsciowe

- Pytanie: co stanie sie na 40 skanach R59, gdy pas brzegu bedzie 1,6 / 1,75 / 2,0 mm zamiast 1,5 mm.
- T2 = FAIL w czesci "lista do dofrezowania = prawda": skan sha16 247ee785f428396f, gniazdo 4 - praca z 2 ubytkami
  "wykrywalnymi" wg prawdy (0,93 x 0,32 mm sciana; 0,24 x 0,08 mm krawedz) pokazana na ZIELONO. Silnik znalazl plame
  w miejscu pierwszego, ale 1,569 mm od brzegu = 0,069 mm poza pasem 1,5 mm (rodzaj "poza_pasem"); 6 z 6 analiz.
- T10 z dzisiaj (pas 1,5): wyrownanie 40 z 40, top-1 "dobrze" 276 z 276, falszywe czerwone na pracach calych 0 z 127.

## 2. Sposob pomiaru

- Narzedzie T10 z instalacji (`<K>\Polecenie.cmd narzedzia\metryki_P3a.py`) przyjmuje plik ustawien opcja `--ustawienia`
  - kopia programu NIE byla potrzebna. `<R>\ust_1p5.toml`, `ust_1p6.toml`, `ust_1p75.toml`, `ust_2p0.toml` = kopie bajtowe
  `<K>\ustawienia.toml` ze zmieniona JEDNA wartoscia (wiersz 54 `pas_brzegu_mm`); po wczytaniu rozni sie tylko ten klucz.
- Dowod, ze prog zadzialal: (a) plik wyniku kazdego wariantu ma `zbiorczo.ustawienia_inspect.pas_brzegu_mm` = 1.5 / 1.6 /
  1.75 / 2.0; (b) zrzut plam zapisuje pas przekazany do `porownaj`; (c) plama pracy z T2 (1,563 mm od brzegu w sciezce
  narzedzia) ma rodzaj "poza_pasem" przy 1,5 i "ubytek" od 1,6 w gore.
- Przebiegi: kazdy = pelne 40 skanow, `--procesy 1`, osobno przez `ciezki.ps1 -Tor 2 -Kto pas` (`krok_pas_*.cmd`); kolejnosc
  1,5 -> 1,6 -> 2,0 -> 1,75 -> powtorka 1,5; 5 kodow 0, "Traceback" 0; czasy 828 / 825 / 809 / 790 / 784 s (05:47-06:55).
- Wariant 1,5: polecenie T10 doslownie (inne tylko sciezki wyjscia i ustawien). ODTWORZENIE T10: TAK - 40 z 40 (max
  0,0143 mm), 276 z 276, 0 z 127 (szerzej 0 z 150); liczniki `zbiorczo` jak w T10; gniazdo po gniezdzie: 0 z 397 innych.
- Warianty 1,6 / 1,75 / 2,0 i powtorka 1,5: to samo narzedzie uruchomione przez obserwatora `<R>\pas_plamy.py` (runpy na
  niezmienionym pliku instalacji; dopisuje listy plam i wciec gniazd do `plamy_*.jsonl`, bo rekord narzedzia zostawia
  tylko `ubytki` - plam odrzuconych w nim NIE MA). Obserwator nie zmienia wyniku: powtorka 1,5 = 40 z 40, 276 z 276,
  0 z 127 i 0 z 397 gniazd o innym kolorze niz T10; rozni sie 1 status inspekcji tego samego koloru (falszywe "skan
  ponownie" 1 zamiast 2 - rozrzut miedzy przebiegami znany z R59).
- Liczenie: `<R>\licz_pas.py` (logika `t10_licz.py` + liczniki wg prawdy); na pliku T10 daje liczby T10 i liczby wykonawcy
  T2 (165 prac z ubytkiem w "dobrze": 64 / 99 / 2). Pelne wyniki: `licz_pas.txt`, `licz_pas.json`, `tabela.txt`.

## 3. Tabela wariantow (40 skanow R59; 397 prac w prawdzie)

| Miara | 1,5 | 1,6 | 1,75 | 2,0 |
|---|---|---|---|---|
| wyrownanie | 40 z 40 | 40 z 40 | 40 z 40 | 40 z 40 |
| top-1 "dobrze" | 276 z 276 | 276 z 276 | 276 z 276 | 276 z 276 |
| falszywe czerwone na pracach calych wg R59 pkt 6.2 (szerzej: z 150) | 0 z 127 (0) | 0 z 127 (0) | 0 z 127 (0) | 0 z 127 (0) |
| prace cale: z alarmem (czerwone + zolte "sprawdz") / "nie sprawdzono" | 0 / 9 z 127 | 0 / 9 | 0 / 9 | 0 / 9 |
| falszywe ubytki: miejsca / w tym czerwone (na pracach z ubytkami) | 7 / 2 | 2 / 0 | 3 / 0 | 3 / 0 |
| prace z ubytkiem, "dobrze" (165): czerwone / zolte / ZIELONE | 64 / 99 / 2 | 67 / 97 / 1 | 66 / 98 / 1 | 63 / 101 / 1 |
| prace z ubytkiem, wszystkie scenariusze (247; 7 szarych / pomar.) | 66 / 172 / 2 | 68 / 170 / 2 | 67 / 171 / 2 | 64 / 174 / 2 |
| - z ubytkiem WYKRYWALNYM, wszystkie scenariusze (184): zielone | 2 | 1 | 1 | 1 |
| ubytki wykrywalne wykryte, razem z 249 ("dobrze" z 245) | 226 (223) | 230 (227) | 232 (229) | 229 (226) |
| - metoda A / B / A+B / na czerwono | 189/110/72/83 | 197/113/79/87 | 197/115/79/87 | 197/110/77/83 |
| gniazda o innym statusie niz przy 1,5 (z 397; na pracach calych 0) | - | 10 | 7 | 12 |
| - zolty -> czerwony / zielony -> zolty (mocniej) | - | 5 / 1 | 3 / 1 | 4 / 1 |
| - czerwony -> zolty / zolty -> zielony (slabiej) | - | 3 / 1 | 2 / 1 | 6 / 1 |
| praca z T2: 247ee785f428396f gniazdo 4 | zielony | zolty | zolty | zolty |
| druga zielona z T10: 841d3af39701d069 gniazdo 18 | zielony | zielony | zielony | zielony |

Prace z ubytkiem na zielono (zestaw / plytka / gniazdo / sha16 skanu):
- 1,5: P2 / wieczorna nr 2 / gn. 4 / 247ee785f428396f (praca z T2); P2 / poranna nr 5 / gn. 18 / 841d3af39701d069.
- 1,6, 1,75 i 2,0: P2 / poranna nr 5 / gn. 18 / 841d3af39701d069; NOWA: P3a / wieczorna nr 2 (seed 321) / gn. 2 /
  ddef50e37281d5ab - praca czesciowo widoczna, 1 ubytek 0,22 x 0,075 mm, w prawdzie NIEwykrywalny (plytszy niz prog
  0,08 mm); przy 1,5 byla zolta dzieki wcieciu metody B 0,25 mm, przy szerszym pasie tego wciecia nie ma.

## 4. Praca przeoczona w T2 (247ee785f428396f, gniazdo 4) w kazdym wariancie

- 1,5: zielona ("ok"), 0 ubytkow - jak w T10 i T2 (takze w powtorce 1,5).
- 1,6 / 1,75 / 2,0: ZOLTA ("sprawdz") - 1 ubytek metoda A: plama 0,836 x 0,392 mm, 1,563 mm od brzegu (ubytek prawdy
  0,93 x 0,32 mm: trafiony). W zadnym wariancie nie czerwona (metoda B nie potwierdza: wciecie 0,25 mm o szerokosci
  0,18-0,20 mm = "za_male"). Drugi ubytek prawdy (0,24 x 0,08 mm, krawedz) niewykryty w 4 z 4 wariantow.
- Zapas przy 1,6: 0,037 mm w sciezce narzedzia; w PROGRAMIE (T2, inny wspolczynnik) ta plama lezy 1,569 mm od brzegu,
  czyli zapas 0,031 mm - przebiegu T2 w programie ze zmienionym progiem NIE ZMIERZONO.
- Druga praca zielona z T10 (841d3af39701d069, gn. 18; ubytek 0,37 x 0,13 mm na krawedzi): zielona w 4 z 4. Silnik
  widzi tam plame 0,39 x 0,20 mm na krawedzi, ale bez ostrej krawedzi (rodzaj "lagodna") - pas brzegu jej nie dotyczy.

## 5. Koszt i ograniczenia pomiaru

- Falszywe czerwone na pracach calych: 0 z 127 (0 z 150) w kazdym wariancie; prace cale z jakimkolwiek alarmem: 0;
  zadne gniazdo z praca cala nie zmienilo statusu. Kryteria T10 spelnione w 4 z 4 wariantow.
- Wszystkie zmiany statusow sa na pracach Z ubytkiem w prawdzie i ida w OBIE strony (tabela). Z samego pasa (plama metody
  A lezaca 1,5-X mm od brzegu) wynikaja w kazdym wariancie 2 gniazda: praca z T2 (zielony -> zolty) i ce12847c3942931b
  gn. 5 (zolty -> czerwony). Reszta (8 / 5 / 10 gniazd przy 1,6 / 1,75 / 2,0) to zmiana wciec metody B w miejscach lezacych
  0,09-1,4 mm od brzegu, czyli wewnatrz starego pasa: wciecia bliskie progu pojawiaja sie albo znikaja. Wg kodu metoda B
  probkuje pas losowymi punktami (staly zarodek, liczba zalezy od pola pasa), wiec inny pas = inna proba (nie badane
  osobno). Skutek nie rosnie rowno z pasem i nie jest rozrzutem przebiegow (2 przebiegi przy 1,5 i T10: 0 z 397 gniazd).
- Na slabsza strone: czerwony -> zolty 3 / 2 / 6 prac z ubytkiem (alarm zostaje, ale zolty) oraz 1 praca zolty -> zielony
  (nowa zielona z pkt 3). Liczba prac z ubytkiem na zielono (wszystkie scenariusze) = 2 z 247 w KAZDYM wariancie.
- Plamy odrzucone przy 1,5 jako "poza_pasem": 13 na 40 skanach (zrzut powtorki 1,5; to samo wychodzi z 3 zrzutow
  szerszych pasow; na 5 plytkach wspolnych z wynikami programu z T2: 3 bez takich plam, 2 z ta sama plama +0,006 mm):
  | Odleglosc od brzegu | 1,5-1,6 | 1,6-1,75 | 1,75-2,0 | > 2,0 mm |
  |---|---|---|---|---|
  | prace z ubytkiem, plama przy ubytku prawdy (do 1 mm + promien) | 7 | 0 | 1 | 2 |
  | prace z ubytkiem, plama z dala od ubytku prawdy | 0 | 0 | 0 | 3 (najblizsza 3,06 mm) |
  | prace cale | 0 | 0 | 0 | 0 |
  W tych danych szerszy pas nie ma czego falszywie zglosic na pracach calych; 7 z 8 plam do 2,0 mm lezy w 1,5-1,6 mm.
- Ograniczenie 1: 40 skanow SYNTETYCZNYCH, nie skaner. Wg kodu generator wycina ubytki tylko w pasie brzegu z ustawien
  (1,5 mm), wiec zysku 1,75 / 2,0 ponad 1,6 nie da sie na tych danych zobaczyc. Prace cale maja tylko szum 0,03 mm
  i 0 plam poza pasem - kosztu falszywych alarmow na prawdziwych skanach ten pomiar NIE mierzy.
- Ograniczenie 2: prog bylby dobierany na danych, na ktorych jest oceniany (1 praca, zapas 0,03-0,04 mm przy 1,6).
- Ograniczenie 3: 1 przebieg na wariant (1,5: 2); sciezka narzedzia T10 (wspolczynnik i uklad z prawdy), nie program.
- NIE ZMIERZONO: T2 / T3 w programie ze zmienionym progiem; pelny pytest z innym progiem (testy z liczbami odniesienia);
  zestaw duzy R59 (80 skanow); wartosci posrednie (np. 1,55); prawdziwe skany; skutek wariantu C.

## 6. Warianty decyzji dla wlasciciela (bez rekomendacji)

Zadna wartosc nie daje czystej poprawy: praca z T2 przechodzi na zolto przy kazdym pasie >= 1,6, ale kazda zmiana pasa
przestawia tez 9 / 6 / 11 innych gniazd (w obie strony) i daje 1 nowa prace z ubytkiem na zielono.
- A. Zostawic 1,5 i przyjac granice wykrywania: liczby T10 bez zmian; 2 z 165 prac z ubytkiem ("dobrze") na zielono,
  ubytki wykrywalne 226 z 249; T2 czesc (e) zostaje FAIL na tej pracy, dopoki prawda scenariusza jej tak oznacza.
- B. Zmienic na 1,6 / 1,75 / 2,0: praca z T2 zolta (3 z 3); kryteria T10 dalej spelnione (40 z 40, 276 z 276, 0 z 127);
  ubytki wykrywalne 230 / 232 / 229 z 249; zielone prace z ubytkiem wykrywalnym 2 -> 1; 5 / 3 / 4 prace z zoltego na
  czerwony; koszt: 3 / 2 / 6 prac z ubytkiem z czerwonego na zolty i 1 praca (ubytek ponizej progu glebokosci) z zoltego
  na zielony. Zmiana progu = nowe liczby odniesienia T10 / R59 i powtorka T2, T10 (nie robione tutaj).
- C. Poprawic znacznik "wykrywalny" w prawdzie (uwzglednic pas): pierwszy ubytek pracy z T2 lezy wg prawdy 1,5049 mm od
  linii brzegu (0,005 mm za pasem) - przy regule "odleglosc od linii <= pas" przestalby byc "wykrywalny"; ale drugi
  (0,24 x 0,08 mm na krawedzi) zostaje "wykrywalny" i nie jest wykrywany w zadnym wariancie, wiec sama poprawka pasa w
  znaczniku NIE zmieni wyniku tej pracy w T2. W prawdzie 24 z 249 ubytkow wykrywalnych lezy dalej niz 1,5 mm od linii
  (wykryte przy 1,5: 19 z 24, bo pas liczy sie tez od plaszczyzny). Wymaga zmiany generatora (nietykalny) - nie mierzone.

## 7. Kontrola po pracy (06:56)

- `<K>\ustawienia.toml` SHA-256 przed = po (4303ec76c74fb4a2...); lista plikow instalacji bez venv (150) przed = po: 0 roznic;
  `git -C <PC-katalog>\t0\repo status --short` pusto; moich procesow python 0 (zostal cudzy PID 12012); pliki tylko w `<R>`.
