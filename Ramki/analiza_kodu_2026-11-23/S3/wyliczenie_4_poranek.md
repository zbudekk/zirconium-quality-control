# Wyliczenie 4 - poranek (session_rano + ekran poranny) - fakty z kodu

Data: 2026-11-23. Analiza tylko do odczytu (bez uruchamiania). Worktree: <PC-katalog>\qc-wt\analiza-s3.

Skroty plikow (wszystkie w Ramki\stanowisko\):
- SR  = stanowisko\session_rano.py
- EK  = stanowisko\ui\ekran_rano.py
- MR  = stanowisko\ui\mapa_rano.py
- KA  = stanowisko\ui\kandydaci.py
- NR  = stanowisko\ui\napisy_rano.py
- KO  = stanowisko\kontroler_api.py (pomocniczo: zrodlo StanRano i wykonanie polecen)
- SE  = stanowisko\session.py (pomocniczo)
- ST  = stanowisko\statusy.py (pomocniczo)
- OK  = stanowisko\ui\okno.py (pomocniczo)
- MP  = stanowisko\ui\mapa.py (pomocniczo, klasa bazowa MapaRano)
- DS  = opisy_modulow\session.md, DU = opisy_modulow\ui_rano.md

Pojecia uzyte nizej:
- "przypisanie" pracy = kolumna `prace.projekt_id` (SR:599-601 `_zapisz_przypisanie`). Klasa pracy NIE jest zapisywana w bazie -
  liczy ja `_oblicz` przy kazdym `stan_pieca` (SR:720-893).
- `pr` = `nastepcy.get(p["projekt_id"], p["projekt_id"])` (SR:768) - przypisanie z bazy, podmienione na jedynego zywego nastepce,
  gdy projekt ma `usuniety = 1` (SR:736-738, `_nastepcy` SR:644-656).
- `d` = `obow.get(p["id"])` (SR:766) - ostatnia niecofnieta decyzja `wybor_kandydata` / `przypisanie_reczne` tej pracy
  (SR:730-733, `_obowiazujaca` SR:138-141, `_obowiazujace` SR:132-135).

---------------------------------------------------------------------------------------------------------------------------

## A. Przypisanie projektu do pracy rano

### A.0 Tabela decyzyjna klasy pracy (`SesjaRano._oblicz`, SR:770-782; kolejnosc galezi = pierwszenstwo)

| # | Warunek (cytat z kodu) | Klasa | Linia |
|---|---|---|---|
| 1 | `if not aktywny:` (aktywny = `s["id"] in aktywne_ids`, SR:763; aktywne = `s["status"] in SE.STATUSY_AKTYWNE and s["id"] not in pominiete`, SR:726; STATUSY_AKTYWNE = (przyjety, do_powtorzenia), SE:77) | None (brak klasy) | SR:770-771 |
| 2 | `elif s["status"] == SE.STATUS_DO_POWTORZENIA:` | do_powtorzenia | SR:772-773 |
| 3 | `elif pr is None:` oraz `dwuznaczna = (d is None and (p["kandydat1_pokrycie"] or 0.0) >= self.prog_kandydata and any(k["projekty"] for k in kand))` | dwuznaczna gdy `dwuznaczna`, inaczej nieznana | SR:774-776 |
| 4 | `elif pr in w_konflikcie:` (ten sam `pr` w >1 miejscach `(skan_id, gniazdo)` skanow aktywnych o statusie przyjety; praca bez gniazda = miejsce `f"poza-{x['id']}"`; dwa fragmenty w jednym gniezdzie = jedno miejsce) | konflikt | SR:777-778 (zbior: SR:747-752) |
| 5 | `elif wczesniej(st):` = `st is not None and st["stan"] in STANY_KONCOWE and (st["sesja_pieca_id"] is None or (st["sesja_pieca_id"] != pid if otwarty else st["sesja_pieca_id"] < pid))` | poprawka | SR:779-780 (funkcja SR:742-744) |
| 6 domyslna | `else: klasa = KLASA_PRZYPISANA if d is not None else KLASA_PEWNA` | przypisana (jest decyzja) / pewna (brak decyzji) | SR:781-782 |

Skutki klasy: `liczona = klasa in KLASY_LICZONE` (SR:796; KLASY_LICZONE = pewna, przypisana, SR:52); `status = STATUS_KLASY.get(klasa)`
(SR:791; mapa SR:56-57: pewna/przypisana -> "zielony", dwuznaczna -> "zolty", nieznana -> "nieznana_rano", poprawka -> "dofrezowany",
konflikt -> "czerwony", do_powtorzenia -> "skan_do_powtorzenia"); `kolor, kolor_ramki = kolory_statusu(status)` (SR:792; klucz nieznany
tabeli ST.STATUSY -> STATUSY_ZAPASOWE, a bez wpisu tam -> (None, None), SR:101-104).

Pola wyniku uzywane przez klase:
- `prace.projekt_id` (przez `pr`) - galezie 3-6.
- decyzja `d` - galezie 3 i 6.
- `kandydat1_pokrycie` - tylko galaz 3 (None -> 0.0, czyli zawsze nieznana).
- `kandydat1_sha16` / `kandydat2_sha16` - tylko przez `kand` (SR:754-758: kandydat z niepustym sha16; `projekty` = projekty
  `usuniety = 0` o tym sha16 w CALYM indeksie, `_projekty_sha` SR:615-620). Do dwuznacznej wystarcza, ze KTORYKOLWIEK z dwoch
  kandydatow ma projekt w indeksie.
- NIE uzywane przez klase: `status_match`, `pewnosc`, `kandydat2_pokrycie` (sa tylko kopiowane do wpisu, SR:795, SR:755).
  `status_match` dziala posrednio - tylko w przypisaniu automatycznym (A.1).
- Stan punktu `st = stany.get(pr)` (SR:769; `_stany` SR:658-668 - wlasny wiersz `stan_punktow` albo odziedziczony po usunietym
  poprzedniku) - tylko galaz 5. Brak wiersza -> None -> nie poprawka.
- Projekt `pr` istnieje w bazie, ale ma `usuniety = 1` i nie ma jedynego nastepcy: `pr` = id usunietego projektu, klasa jak dla
  zywego (galaz 6 itd.); `info` z `_projekty_id` (SR:622-623 - bez filtra `usuniety`) daje jego kuwete.
- `pr` bez wiersza w `projekty`: `info` None -> `kuweta` None, `kuweta_do_sprawdzenia` True (SR:804), klasa pewna/przypisana mozliwa.

### A.1 Przypisanie automatyczne po skanie
- Miejsce: `przyjmij_wynik` SR:292-304; dla kazdej pracy nowego skanu `self._zapisz_przypisanie(p["id"], self._przypisanie_auto(p))`
  (SR:302-303). Nadpisuje `projekt_id`, ktore wpisal `Sesja._wstaw_prace` (SE:462-467, SE:477).
- `_przypisanie_auto` (SR:576-591):
  - SR:580-582 `sha = praca["kandydat1_sha16"]`; `if praca["status_match"] != "zielony" or not sha: return None`.
    status_match None / zolty / szary / nieznany -> None. kandydat1_sha16 None -> None.
  - SR:583 `z_puli = self.sesja.wpis_puli_pracy(praca["id"], praca["skan_id"])` (SE:666-682: pamiec ostatniego skanu albo dziennik;
    None = pula z folderu albo praca szara / brak wpisu).
  - SR:584-589 (pula per praca): `pid = z_puli["projekt_id"]`; `info = self._projekty_id([pid]).get(pid) if pid is not None else None`;
    `if info is None: return None` (pid None = wpisy z roznymi projektami, albo projektu nie ma); `return pid if not info["usuniety"] else
    self._nastepcy({pid: info}).get(pid)` (usuniety bez jedynego nastepcy -> None). Ta galaz NIE sprawdza, ile projektow ma ten sha16.
  - SR:590-591 (bez wpisu puli): `projekty = self._projekty_sha([sha]).get(sha, [])`; `return projekty[0]["projekt_id"] if len(projekty) == 1 else None`
    (0 albo >=2 projektow o tym sha16 -> None).
  - Nie uzywa: `pewnosc`, `kandydat1_pokrycie`, kandydata 2.
- Klasa wynikowa: projekt != None -> pewna (o ile nie konflikt / poprawka / do_powtorzenia); None -> dwuznaczna albo nieznana (galaz 3).

### A.2 Wybor kandydata (`wybierz_kandydata`, SR:523-540)
- Warunki: osoba z listy (SR:526, `_osoba` SR:178-189); praca poranna, skan `przyjety`, niepominiety, piec otwarty (`_praca_rano` SR:498-517).
- SR:529 `kandydaci = [k for k in (p["kandydat1_sha16"], p["kandydat2_sha16"]) if k]`; SR:530 `if not sha16 or sha16 not in kandydaci:` -> BladSesji.
- SR:533-536 `projekty = self._projekty_sha([sha16]).get(sha16, [])`; `if len(projekty) != 1:` -> BladSesji (0 = "nie ma projektu w indeksie",
  >1 = "jest w N zleceniach naraz"). Szukanie po sha16 w calym indeksie (`usuniety = 0`), nie po puli.
- SR:537-538 decyzja `wybor_kandydata`, `wartosc=sha16`; SR:539 `self._zapisz_przypisanie(p["id"], projekty[0]["projekt_id"])`.
- Nie sprawdza: pokrycia kandydata (2. kandydat o dowolnym pokryciu wolno wybrac), status_match, pewnosci.
- Klasa: przypisana (galaz 6), chyba ze konflikt (4) albo poprawka (5).

### A.3 Przypisanie reczne (`przypisz_recznie`, SR:542-557)
- Warunki jak A.2 (SR:545-547). `projekt_id` nie None: `if isinstance(projekt_id, bool) or not str(projekt_id).isdigit():` -> BladSesji
  (SR:549-550); `SELECT id FROM projekty WHERE id = ? AND usuniety = 0` pusty -> BladSesji (SR:552-553). Brak ograniczenia do puli,
  kuwety, kandydatow ani do punktow niezamknietych.
- SR:554-555 decyzja `przypisanie_reczne`, `wartosc = BEZ_PROJEKTU ("") if projekt_id is None else str(projekt_id)`; SR:556 zapis.
- Klasa: z projektem -> przypisana (albo konflikt / poprawka); `projekt_id=None` -> `pr` None i `d` nie None -> nieznana (galaz 3,
  `d is None` falsz).

### A.4 Cofniecie przypisania (`cofnij_przypisanie`, SR:559-574)
- SR:565-567 `ob = self._decyzja_przypisania(p["id"])`; None -> BladSesji. SR:568-569 `if decyzja_id is not None and ob["id"] != decyzja_id:` -> BladSesji.
- SR:570-571 wiersz `cofniecie` z `wartosc=str(ob["id"])`.
- SR:572-573 `nowa = self._decyzja_przypisania(p["id"])`; `self._zapisz_przypisanie(p["id"], self._projekt_z_decyzji(nowa) if nowa is not None else self._przypisanie_auto(p))`.
- `_projekt_z_decyzji` (SR:593-597): `wybor_kandydata` -> ponownie `_projekty_sha([wartosc])`, jeden projekt -> jego id, inaczej None
  (wynik moze byc inny niz w chwili decyzji, jesli indeks sie zmienil); `przypisanie_reczne` -> `int(wartosc)` gdy cyfry, inaczej None
  (bez sprawdzenia istnienia / `usuniety`).
- Klasa po cofnieciu: wg A.1 (gdy brak decyzji) albo wg poprzedniej decyzji; poprzednia `wybor_kandydata`, ktorej sha16 jest teraz
  w 0 albo >=2 projektach -> `projekt_id` None przy `d` nie None -> nieznana.

### A.5 "Zamknij piec" (`_zamknij`, SR:1084-1131)
- SR:1101-1102 dla kazdej pracy liczonej `self._zapisz_przypisanie(p["id"], p["projekt_id"])` - zapisuje `pr` (nastepce po zmianie nazwy,
  SR:797 `"projekt_id": pr`). Jedyna sciezka poza decyzjami, ktora zmienia `prace.projekt_id` istniejacej pracy.

### A.6 Ponowny skan (`zastap_skan` SR:330-349, `cofnij_zastapienie` SR:351-355)
- SesjaRano nie zmienia `prace.projekt_id`. `Sesja._zastap` ustawia staremu skanowi status `zastapiony` (SE:1002-1037);
  `_przelicz_punkty_skanu` jest dla rano bez skutku (`if projekt_id is None or tryb != TRYB_WIECZOR: return`, SE:1054-1055).
- Prace skanu zastapionego: klasa None (galaz 1). Prace nowego skanu maja przypisanie z A.1 (z chwili przyjecia) - decyzje starego
  skanu nie przechodza (SR:332).
- `cofnij_zastapienie`: stary skan znow aktywny (SE:794) z WLASNYM `projekt_id` i decyzjami (decyzje nie byly usuwane) - klasa liczona od nowa.

### A.7 Pominiecie skanu (`pomin_skan` SR:412-430, `cofnij_pominiecie` SR:432-441)
- Bez zmiany `projekt_id`. Pominiety -> poza `aktywne` (SR:726) -> klasa None. Cofniecie -> klasa liczona od nowa.

### A.8 Przeniesienie skanow (`zamknij_piec_i_przenies` SR:982-1028, `cofnij_przeniesienie` SR:1030-1065)
- Zmienia tylko `skany.sesja_pieca_id` (SR:1020, SR:1023, SR:1058); `projekt_id` i decyzje prac bez zmian.
- Klasa w nowym piecu liczona od nowa: `wczesniej` porownuje z `pid` nowego pieca (SR:744), wiec praca przeniesiona z projektem, ktorego
  punkt wlasnie zamknal stary piec (SR:1021 przed SR:1022), dostaje klase poprawka; konflikt liczony tylko w obrebie nowego pieca.

### A.9 Ponowne otwarcie pieca (`otworz_piec_ponownie` SR:1151-1176)
- Przywraca tylko `stan_punktow` (`_przywroc_zamkniecie` SR:1178-1191) i `zamknieto/zamknal` (SR:1171). `prace.projekt_id` zapisane
  przez A.5 (nastepca) zostaje. Klasa liczona od nowa (punkt przywrocony -> zwykle znika poprawka).

### A.10 Inne sciezki
- Odczyt: podmiana na nastepce w `_oblicz` (SR:768) bez zapisu (zapis dopiero A.5).
- `podaj_numer_plytki`, `dopusc_plytke` (zawsze odmowa, SR:399-404), `cofnij_dopuszczenie` (SR:406-410): bez zmiany `projekt_id`;
  `cofnij_dopuszczenie` zmienia status skanu -> klasa None.
- `przyjmij_blad` (SR:306-313): skan bez prac.

---------------------------------------------------------------------------------------------------------------------------

## B. "Zlecenie kompletne" i "Zamknij piec"

### B.1 Zlecenie kompletne
- Zlecenia rozpatrywane: tylko zlecenia prac liczonych tego pieca: `punkty = self._punkty_zlecen([w["zlecenie_id"] for w in liczone.values()])`
  (SR:825); `liczone[pr] = wpis` tylko dla `klasa in KLASY_LICZONE` przy skanie aktywnym (SR:806, SR:812-813).
- Punkty zlecenia = projekty `usuniety = 0` zlecenia poza `TYPY_BEZ_PUNKTU` (dzis pusta, SR:86), ze stanem obowiazujacym (SR:670-681).
- `_zlecenie` (SR:700-713): punkt `if pt["projekt_id"] in teraz_ids:` (liczony w tym piecu) -> rozpoznany; `elif not wczesniej.get(pt["projekt_id"], False):`
  -> brakujacy. `"kompletne": not brakujace` (SR:712).
- `wczesniej_pt = {pt["projekt_id"]: wczesniej(pt) ...}` (SR:826) - ta sama funkcja co galaz 5: stan `rozpoznany` / `zamkniety_recznie`
  i (`sesja_pieca_id` None albo dla pieca otwartego: KAZDY inny piec `!= pid`; dla zamknietego: `< pid`) (SR:742-744).
- Piec zamkniety: `kompletne` / `braki` / `zlecenia` / `poprawki` z zapisu "Zamknij piec" (SR:961-964), klasy prac - ze stanu bazy teraz.

### B.2 Co blokuje "Zamknij piec"
Odmowa (BladSesji, nic nie zapisane):
1. Brak osoby z listy - `_osoba` (SR:978, SR:178-189).
2. Brak otwartego pieca biezacego (bez wskazania) albo wskazany `plan_id` / `sesja_pieca_id` nie jest otwarty (`_piec_do_zamkniecia` SR:1067-1082).
3. Kazda pozycja `stan["blokady"]` liczona w tej samej transakcji: `if stan["blokady"]: raise` (SR:1086-1088). `_blokady` (SR:895-945):
   - skany pominiete albo `zastapiony` - pomijane: `if s["id"] in pominiete or s["status"] == SE.STATUS_ZASTAPIONY: continue` (SR:902-903);
   - skan nieaktywny (blad, niezgodny_uklad, plytka_nie_z_trybu, kazdy inny status poza aktywnymi) - blokada, chyba ze `ponowny =
     s["numer_plytki"] is not None and any(t["id"] > s["id"] and t["numer_plytki"] == s["numer_plytki"] for t in aktywne)` (SR:904-912).
     Skan `blad` nie ma numeru (SE:450-452), a `podaj_numer_plytki` go nie przyjmie (SR:367-370) - odblokowuje go tylko `pomin_skan`;
   - `if s["status"] == SE.STATUS_DO_POWTORZENIA:` (SR:913-915);
   - `if dozwolone is None:` - uklad nie poranny / nieznany (SR:916-919);
   - plytka na ramce z numerem spoza dozwolonych: `elif s["numer_plytki"] is not None and s["numer_plytki"] not in dozwolone:` (SR:925-927);
   - `if bez_numeru:` - aktywne plytki na ramce bez numeru (SR:928-930; lista SR:838-840);
   - `for n in zdublowane:` - dwa aktywne skany plytek na ramce z tym samym numerem (SR:931-941; lista SR:841-845, klucz = sam numer);
   - `if konflikty:` (SR:942-944).
4. Kontroler (pomocniczo): `zamknij_piec` odmawia, gdy `self._zajety()` (analiza w toku / skanowanie) (KO:3786-3788); `dozwolone`
   zawiera "zamknij_piec" tylko `if st["otwarty"] and zajety is None` i `if not st["blokady"]` (KO:2026-2029).
5. Ekran (pomocniczo): przycisk aktywny tylko z "zamknij_piec" w `rano.dozwolone` i z osoba (EK:828); przy niepustym
   `nierozstrzygniete_prace` przycisk nie wysyla polecenia, tylko pyta (EK:842-845) - to nie blokada sesji.
Nie blokuja: dwuznaczne, nieznane, poprawki (nie sa w `_blokady`); plytki okragle poza ramka (n9) bez numeru / numer spoza / kilka
z tym samym numerem - tylko ostrzezenia (SR:920-924, SR:864-873); inne otwarte piece - ostrzezenie (SR:877-882).

### B.3 Co jest pomijane przy liczeniu
- Lista prac liczonych przy zamknieciu: `liczone = [p for s in stan["skany"] for p in s["prace"] if p["liczona"] and s["aktywny"]]` (SR:1090).
- pominiete skany - poza `aktywne` (SR:726) -> klasa None -> nie licza sie; nie blokuja (SR:902).
- zastapione - status poza STATUSY_AKTYWNE -> klasa None; nie blokuja (SR:902).
- do_powtorzenia - aktywne, ale klasa do_powtorzenia (nie w KLASY_LICZONE); blokuja.
- blad / niezgodny_uklad / plytka_nie_z_trybu - klasa None; blokuja do ponownego skanu z numerem albo pominiecia.
- plytka na ramce bez numeru - jej prace MAJA klasy i sa liczone (klasa nie zalezy od numeru), ale skan blokuje zamkniecie (SR:928-930).
  Okragla n9 bez numeru - liczona, tylko ostrzezenie (SR:866-867).
- dwa skany z tym samym numerem - prace obu maja klasy i sa liczone; blokada (SR:931-941). Ten sam projekt na obu skanach = konflikt
  (inne `skan_id`, SR:752).
- skany `wstrzymane` (numer niezgodny z dolkami) - pomijane tylko w planie ramki; liczone normalnie (SR:1307-1308).
- praca bez gniazda na skanie `przyjety` - klasa jak kazda; jesli pewna/przypisana - liczona (nie trafia do planu ramki, SR:1320-1321).

### B.4 Czy praca zolta / czerwona / biala moze domknac zlecenie
- Nie. Punkt domyka tylko `klasa in KLASY_LICZONE` = (pewna, przypisana) (SR:52, SR:796, SR:1090, SR:1105).
  dwuznaczna (zolty), do_powtorzenia (zolty), nieznana (bialy), poprawka (bursztyn) - nie licza sie; konflikt (czerwony) blokuje.
- Zastrzezenia z kodu: "pewna" = kazda praca z `projekt_id` i bez decyzji (galaz 6) - klasa nie sprawdza ponownie `status_match`;
  `projekt_id` automatycznie dostaje tylko praca ze `status_match == "zielony"` (SR:581). "przypisana" przez `wybierz_kandydata`
  mozliwa takze dla 2. kandydata o dowolnym pokryciu (SR:529-539).
- "Zamknij piec": `brakujace` w stanie `oczekuje` -> `brak_po_piecu` (`if b["stan"] == SE.STAN_OCZEKUJE:`, SR:1113-1115); inne stany
  brakujacych (np. do_dofrezowania) bez zmiany.

---------------------------------------------------------------------------------------------------------------------------

## C. `plan_plytek` (SR:1274-1351)

### C.1 Wejscie i odmowy
- `if kolejnosc not in KOLEJNOSCI:` -> BladSesji (SR:1287-1288; KOLEJNOSCI = ("liczba", "numer"), SR:80).
- `biezacy = self.otwarty_piec()`; None -> BladSesji (SR:1289-1291); `sesja_pieca_id` inny niz biezacy -> BladSesji (SR:1292-1294).
- `stan = self.stan_pieca(piec["id"])` (SR:1296) - wszystkie pola ponizej pochodza z `_oblicz`.

### C.2 Struktura zwracana (SR:1347-1351)
| Pole | Wartosc / zrodlo |
|---|---|
| `plan_id` | `plan_id(piec)` = `f"{piec['data']}-p{piec['nr_w_dniu']}"` (SR:153-155, SR:1347) |
| `tryb` | `SE.TRYB_RANO` ("rano") (SR:1347) |
| `sesja_pieca_id` | `piec["id"]` (SR:1347) |
| `plytki` | `{str(n): {"gniazda": lista}}` (SR:1339); gniazdo: `{"id": gid, "kolor": ...}` + opcjonalnie `"kuweta"` (SR:1325-1338) |
| `kuwety` | `[{"kuweta": k, "plytki": sorted(na_plytkach[k])} for k in porzadek]` (SR:1348) |
| `braki` | `sorted({z["kuweta"] for z in stan["braki"] if z["kuweta"] and WZOR_KUWETY_RAMKI.fullmatch(z["kuweta"])}, key=_klucz_kuwety)[:MAX_BRAKOW_PLANU]` (SR:1346, SR:1348; MAX = 100, SR:82) |
| `uklady` | `{str(n): s["uklad"]}` (SR:1340) |
| `skany` | `{str(n): s["id"]}` (SR:1341) |
| `liczba_prac` | `{k: liczba[k] for k in porzadek}` (SR:1349) - liczba GNIAZD z jedna praca klasy z kuweta zgodna ze wzorem |
| `pominiete.bez_numeru` | id skanow aktywnych bez numeru - KAZDEGO ukladu (sprawdzane jako pierwsze, SR:1303-1304) |
| `pominiete.poza_gniazdem` | liczba (int) prac bez gniazda na plytkach planu (SR:1320-1321) |
| `pominiete.zdublowane_plytki` | `sorted(set(stan["zdublowane_plytki"]))` (SR:1311) |
| `pominiete.poza_ramka` | id skanow z numerem i `not s["na_ramce"]` (SR:1305-1306); `na_ramce` = `na_ramce(uklad) and numer in dozwolone` (SR:821) |
| `pominiete.numer_niezgodny` | id skanow z argumentu `wstrzymane` (SR:1307-1308) |

### C.3 Wybor plytek i gniazd
- Petla po `stan["skany"]`: `if not s["aktywny"]: continue` (SR:1301-1302) - aktywny obejmuje `do_powtorzenia`.
- `for n in sorted(po_numerze): if n in zdublowane or len(po_numerze[n]) > 1: continue` (SR:1314-1316) - plytka o numerze z dubla nie ma
  wpisu w `plytki`. `zdublowane` ze stanu obejmuje tez skany `wstrzymane`, wiec dubel ze skanem wstrzymanym usuwa z planu takze drugi skan.
- Gniazda bez prac nie sa wymieniane w liscie (SR:1318-1325 - tylko gniazda z praca).
- `if len(gniazda[gid]) > 1:` -> `{"id": gid, "kolor": kolor_dwie}` bez kuwety (SR:1326-1328); `kolor_dwie = kolory_statusu("podwojny")[1]`
  (SR:1312) = "zolty" (ST:85).
- Jedna praca: `g = {"id": gid, "kolor": p["kolor_ramki"]}` (SR:1330); `if p["klasa"] in KLASY_Z_KUWETA:` (pewna, przypisana, poprawka - SR:53):
  kuweta zgodna z `#?[0-9]{1,6}` (SR:81) -> `g["kuweta"]`, licznik i plytki kuwety (SR:1332-1335); inaczej `g["kolor"] = kolor_sprawdz`
  (= ramka statusu "czerwony", SR:60, SR:1312, SR:1336-1337) bez kuwety i bez licznika.

### C.4 Co jest w planie dla klas (kolor = `kolor_ramki` z SR:792 przez STATUS_KLASY SR:56-57 i ST)
- pewna / przypisana: "zielony" (ST:58) + kuweta (albo "czerwony" bez kuwety przy kuwecie pustej/niejednoznacznej).
- poprawka: "bursztyn" (ST:78, wiersz "dofrezowany") + kuweta; liczy sie do `kuwety` i `liczba_prac` (KLASY_Z_KUWETA). Bez rozroznienia
  `zlecenie_odhaczone`.
- dwuznaczna: "zolty" (ST:64), bez kuwety.
- nieznana: "bialy" (ST:81, wiersz "nieznana_rano"; zapas SR:58 nieuzywany, bo wiersz istnieje), bez kuwety.
- konflikt: "czerwony" (ST:59), bez kuwety.
- skan do_powtorzenia: plytka JEST w planie (jesli numer jedyny i na ramce); gniazda "zolty" (ST:68) bez kuwety; dwie prace - "zolty".
- plytka bez numeru: tylko `pominiete.bez_numeru` (SR:1303-1304).
- dwa skany z tym samym numerem: zaden nie trafia do `plytki`; numer w `pominiete.zdublowane_plytki`; ich kuwety nie licza sie do
  `kuwety`/`liczba_prac`, ale `braki` (ze `stan["braki"]`) moga zawierac kuwety ich zlecen.

### C.5 Kolejnosc kuwet i "biezaca kuweta"
- `if kolejnosc == "liczba": porzadek = sorted(liczba, key=lambda k: (-liczba[k], _klucz_kuwety(k)))` inaczej `sorted(liczba, key=_klucz_kuwety)`
  (SR:1342-1345). `_klucz_kuwety` (SR:124-129): zwykle numery rosnaco (0, int), potem "#" (1, int), reszta (2, 0, tekst) - do planu
  trafiaja tylko kuwety zgodne ze wzorem, wiec grupa 2 w planie nie wystepuje.
- `plan_plytek` NIE ma pola "biezaca kuweta". Biezaca kuwete trzyma kontroler: `self._kuweta_biezaca[plan_id]`; gdy nie ma jej w liczniku
  - pierwsza w kolejnosci nierozlozona (KO:1713-1720). Lista kuwet ekranu liczona osobno w KO:1679-1721 - bierze tez plytki z numerem
  poza ramka (komentarz KO:1698) i skany wstrzymane; `plan_plytek` je pomija (SR:1305-1308).

---------------------------------------------------------------------------------------------------------------------------

## D. Numery plytek i uklady w session_rano

| # | Miejsce | Warunek / zachowanie | Uklad / numer nieznany |
|---|---|---|---|
| 1 | Stale SR:84-85 | `NUMERY_PLYTEK_PORANNYCH = (4, 5, 6)`, `NUMERY_PLYTEK_OKRAGLYCH_PORANNYCH = (9,)` | - |
| 2 | `numery_plytki` SR:107-114 | `c = SE.czesci_ukladu(uklad)`; `if c is None or c["typ"] != SE.TYP_PLYTKI_TRYBU[SE.TRYB_RANO]: return None`; `if c["ramkowa"]: return SE.numery_ramkowe(uklad)` (4,5,6 - SE:131,152-155); `return (9,) if c["okragla"] else (4,5,6)` | nazwa spoza wzoru `^(okragla_(ramkowa_)?)?(wieczorna\|poranna)(_r\d+)?$` (SE:129, fullmatch SE:141) albo wieczorna -> None. Wersja `_rNN` ignorowana: `poranna_r54` -> (4,5,6), `okragla_poranna_r54` -> (9,) |
| 3 | `na_ramce` SR:117-121 | `c is not None and c["typ"] == poranna and (not c["okragla"] or c["ramkowa"])` | False; wersja ignorowana (`poranna_r54` = na ramce) |
| 4 | `_ostatnia_aktywnosc` SR:202 | skan przedluza piec tylko `if ... numery_plytki(s["uklad"]) is not None` | uklad nieznany nie przedluza |
| 5 | `podaj_numer_plytki` SR:367-377 | `dozwolone = numery_plytki(sk["uklad"])`; `if dozwolone is None:` -> BladSesji; `n = int(numer)` (blad -> None); `if n not in dozwolone:` -> BladSesji | uklad nieznany / nie poranny / skan blad (uklad None) -> odmowa. `int(4.9)` = 4 - liczba niecalkowita jest obcinana i przyjmowana |
| 6 | `podaj_numer_plytki` SR:379-392 | kontrola "nowy wsad" tylko `if sk["numer_plytki"] is not None and n != sk["numer_plytki"] and na_ramce(sk["uklad"])`; inne skany filtrowane `na_ramce(x["uklad"])` (SR:384) | plytka poza ramka - bez kontroli |
| 7 | `_propozycje` SR:469-471 | `ten_sam_plik = bool(s["sha16"]) and s["sha16"] == t["sha16"]`; `ta_sama_plytka = numer not None and rowny and SE.rodzina_ukladu(s) == SE.rodzina_ukladu(t)` | rodzina zawiera wersje (`poranna` != `poranna_r54`); uklad nieznany -> rodzina = nazwa (SE:149) |
| 8 | `_oblicz` SR:817-822 | `"na_ramce": na_ramce(s["uklad"]) and s["numer_plytki"] in (dozwolone or ())`; `"powod"` tylko dla `plytka_nie_z_trybu` | numer None / spoza -> `na_ramce` False |
| 9 | `_oblicz` SR:838-845 | `kwadratowe = [s for s in aktywne if na_ramce(s["uklad"])]` (takze okragla ramkowa); `okragle = [... numery_plytki(...) is not None and not na_ramce(...)]`; `bez_numeru` (kwadratowe bez numeru); `po_numerze` klucz = SAM numer (kwadrat, okragla ramkowa i `poranna_r54` o tym samym numerze = dubel) | aktywny skan ukladu nieznanego nie jest ani w `kwadratowe`, ani w `okragle` |
| 10 | `_oblicz` SR:864-873 | okragle: brak numeru -> ostrzezenie; klucz `(numer, SE.rodzina_ukladu(uklad))` >1 skan -> ostrzezenie | - |
| 11 | `_blokady` SR:905 | `ponowny` = pozniejszy aktywny skan z tym samym numerem (bez porownania ukladu) | skan bez numeru nigdy "ponowny" |
| 12 | `_blokady` SR:916-927 | `dozwolone is None` -> blokada; okragla poza ramka -> ostrzezenie (z dopiskiem przy numerze spoza); na ramce z numerem spoza -> blokada | uklad nieznany/nie poranny na skanie aktywnym -> blokada (SR:917-919) |
| 13 | `dopusc_plytke` SR:399-404 | zawsze BladSesji (plytki nie z trybu rano nie dopuszcza sie) | - |
| 14 | `plan_plytek` SR:1303-1310 | `numer_plytki is None` -> bez_numeru; `not s["na_ramce"]` -> poza_ramka; `id in wstrzymane` -> numer_niezgodny | uklad nieznany: bez_numeru albo poza_ramka |
| 15 | `_oblicz` SR:822 / `_blokady` SR:908 | tekst powodu `SE.powod_nie_z_trybu(uklad, tryb)` (SE:171-181: nieznany uklad -> "nieznany uklad plytki ...") | - |
Uwaga: sam status skanu `plytka_nie_z_trybu` (takze dla ukladu nieznanego) nadaje `Sesja.przyjmij_wynik` (SE:380-381), nie session_rano.
Numer z analizy dla plytki NIE ramkowej nie jest normalizowany (SE:388-392 tylko uklady ramkowe) - moze byc spoza 4-6 / 9.

---------------------------------------------------------------------------------------------------------------------------

## E. Ekran poranny (EK, MR, KA)

### E.1 Kolor i podpis gniazda
- Ekran nie liczy koloru: `MapaRano._rysuj_gniazdo` maluje `g.rgb` (MR:140), podpis `g.podpis` (MR:63). `Gniazdo` buduje kontroler
  `_plytka_rano` (KO:1786-1796): bez prac -> `ST.status("pusty")` (rgb (235,235,235), napis ""); >1 praca na skanie aktywnym ->
  `ST.status("podwojny")`; inaczej status/rgb/podpis pierwszej pracy.
- Praca (KO `_praca_rano` KO:1732-1738): `klasa == "poprawka" and not zlecenie_odhaczone` -> `ST.status("rano_juz_rozpoznany")`;
  inna klasa nie None -> `ST.status_rano(klasa)` (ST:146-149; klasa spoza tabeli -> "nieznany", zolty "sprawdz"); klasa None ->
  `ST.status("plytka_nie_z_trybu" if ... else "nieaktywny")`. `rgb = st.hex`.
- Podpis (KO:1752-1755): `if klasa in ST.KLASY_RANO_Z_KUWETA and p["kuweta"]: podpis = p["kuweta"]` (KLASY_RANO_Z_KUWETA = pewna,
  przypisana, poprawka, KONFLIKT - ST:118) else `st.napis`. Kuweta niejednoznaczna jest pokazywana jako tekst kuwety (ramka: "czerwony"
  bez kuwety). Konflikt: ekran pokazuje kuwete, plan ramki nie (SR:53 bez konfliktu).
- Pole `PracaRano.kolor` (= `kolor` z SR:792, wiersze wieczorne "zielony"/"zolty"...) nie jest uzywane do rysowania.
- Legenda: `ST.status(g.status)` (EK:789). Liczniki w naglowku: `ST.status_rano(klasa)` (EK:815). Widok pracy: `ST.status(zrodlo.status)` (KA:185, KA:189).
- Gniazdo bez pracy: tlo (235,235,235), podpis "" -> `if not kuweta: tekst("nr", str(g.nr), ...)` - sam numer gniazda (MR:88-90) kolorem
  "#8a929c" (MR:143). Klikniecie dziala (EK:1007-1012): widok pracy pokazuje tytul i status "pusty" (KA:176-191), bez przyciskow.
  Plytka nieaktywna bez prac: mapa bez gniazd, napis `MAPA_BEZ_GNIAZD` (MP:119, MP:124-125).
- Klasa nieznana: tlo (250,250,250) (ST:81), podpis "nieznana" rysowany w miejscu kuwety (MR:63, MR:91-102), bez zeba (`praca.kuweta`
  None, MR:64) i bez miniatury (`sha16` None, MR:65).

### E.2 Pamiec ekranu miedzy odswiezeniami (pola kluczowane gniazdem / indeksem oznaczone [G] / [I])
| Pole | Klucz | Ustawiane | Czyszczone | Czy moze wskazac inna prace / obiekt |
|---|---|---|---|---|
| `EkranRano._wybor` EK:503 [G] | (skan_id, nr gniazda) | klik mapy EK:1010; "Wroc do rozstrzygania" EK:861 | Esc/"Zamknij" EK:1014-1016, EK:1079-1081; gdy plytki/gniazda nie ma w stanie albo skan `zastapiony` EK:684-689, EK:698-700. NIE przy zamknieciu pieca ani zmianie strony | Praca = `gniazdo.prace[0]` wyliczana przy kazdym odswiezeniu (EK:690). Prace skanu sa wstawiane raz (SE:409-411), wiec ten sam (skan_id, nr) daje ta sama praca_id; zmieniaja sie jej dane (klasa, projekt, decyzja_id). Druga praca w gniezdzie i prace bez gniazda nie sa osiagalne z mapy |
| `MapaPlytki._wybrane` MP:104, MP:121 [G] | nr gniazda | `ustaw_rano(..., wybrane, ...)` z EK:762-763 | przy kazdym ustaw | tylko podswietlenie |
| `MapaPlytki._ksztalty` MP:107 [G] | nr gniazda -> geometria | przeliczane | przy zmianie ukladu/rozmiaru | trafienie klikniecia `gniazdo_w_punkcie` MP:405-415 |
| `MapaRano._obwodka` MR:42, MR:48 [G] | frozenset nr gniazd | z `StanRano.obwodka(skan_id)` KO:754-757 przy kazdym odswiezeniu | j.w. | tylko rysunek |
| `PanelKuwet._kuwety` EK:199, EK:235 [I] | indeks wiersza tabeli | `ustaw` (gdy zmieni sie sygnatura EK:227-232) | nadpisywane | `_klik(wiersz)` EK:270-272 wysyla `self._kuwety[wiersz].kuweta`. Tabela i `_kuwety` zmieniane razem; brak ochrony przed przestawieniem wierszy (ochrona 800 ms dotyczy tylko map, EK:749-752, EK:1008) - po nowym stanie wiersz pod kursorem moze byc inna kuweta niz widziana |
| `PanelWyniku._biezace` EK:289, EK:483 [I] | indeks wiersza listy brakow | `ustaw` - tylko na stronie "wynik" (EK:721-722) | nadpisywane | `_klik_braku(wiersz)` EK:350-353 bierze zlecenie z biezacej krotki; zapis idzie dopiero z przycisku powodu (projekt_id z panelu) |
| `PanelWyniku._wybrane` EK:287 | zlecenie_id | `_klik_braku` EK:353 | gdy zlecenia nie ma w `_biezace` EK:390-392; ponowny klik | - |
| `PanelWyniku._ostatnie` EK:288 | (projekt_id, kuweta, zab) | po udanym `zamknij_brak_recznie` EK:365 | tylko po udanym cofnieciu EK:381 (inaczej do restartu okna) | `cofnij_zamkniecie_reczne(self._ostatnie[0])` EK:379 - wartosc zapamietana |
| `WidokPracyRano.praca_id` KA:117 | praca_id | `ustaw` KA:164 | `wyczysc` KA:156 | - |
| `WidokPracyRano._przypisanie/_kuweta_szukana/_wyniki` KA:120-123 | - / tekst / krotka `ProjektPuli` | `_szukaj` KA:310-316 | zmiana praca_id KA:162-163, `wyczysc` KA:158 | `_wyniki` = migawka `projekty_kuwety` z chwili szukania (stan punktu nieodswiezany do nowego szukania) |
| `EkranRano._numer_dla` EK:506 | skan_id | EK:1004 | EK:997, EK:1004, EK:933 | - |
| `EkranRano._pytanie_zamkniecia` EK:507 | sesja_pieca_id | EK:843 | EK:851, EK:870 | sprawdzane z biezacym stanem EK:853 |
| `EkranRano._piec_widziany` EK:508 | (sesja_pieca_id, otwarty) | EK:655 | - | przelacza strone EK:649-654 |
| `EkranRano._bufor` EK:504 | tekst numeru kuwety | EK:1045 | Enter EK:1061, Esc EK:1076, Backspace EK:1069 | nie czyszczony przy zmianie pieca |
| `EkranRano._obrazy` EK:509 | sha16 | EK:662-664 | nigdy | - |
| `EkranRano._karty` EK:510 | skan_id | EK:736-746 | przy zmianie zestawu | - |
| `EkranRano._sygnatury` EK:511 | nazwa czesci | `_zmienione` EK:667-671 | `ustaw_tryb` EK:640 | - |

### E.3 Polecenia wysylane z ekranu (droga: `okno._polecenie` OK:511-536 -> `k.wykonaj`)
| Polecenie | Argumenty | Skad argumenty | Linia |
|---|---|---|---|
| `wybierz_kandydata` | (praca_id, sha16) | praca_id zapamietany w lambdzie przy budowie widoku (`p=praca.praca_id`), sha16 kandydata z budowy karty | KA:247, KA:97 |
| `przypisz_recznie` | (praca_id,) = "Bez projektu" | lambda przy budowie | KA:252 |
| `przypisz_recznie` | (praca_id, projekt_id) | lambda przy budowie listy `_wyniki` | KA:300 |
| `cofnij_przypisanie` | (praca_id, decyzja_id) albo (praca_id,) gdy decyzja_id None | lambda przy budowie | KA:262 |
| (przekazanie z widoku) | `lambda nazwa, argumenty: self._polecenie(nazwa, *argumenty)` - bez sprawdzenia, ze widok pokazuje prace z `_wybor` (wieczorem `okno._decyzja` to sprawdza, OK:541-548) | - | EK:608 |
| `zamknij_piec` | (sesja_pieca_id,) | biezacy `self._stan.rano` w chwili klikniecia | EK:835-846 |
| `zamknij_piec` (po pytaniu) | (piec,) | zapamietany `_pytanie_zamkniecia`, porownany z biezacym `rano.sesja_pieca_id` i `otwarty` | EK:851-858 |
| `otworz_piec_ponownie`, `cofnij_przeniesienie` | (sesja_pieca_id,) | biezacy stan w chwili klikniecia | EK:557, EK:560, EK:893-900 |
| `potwierdz_kuwete` | (kuweta,) | `rano.kuweta_biezaca` z biezacego stanu (kontroler odmawia, gdy inna, KO:3907-3911) | EK:189, EK:981-984, EK:1065 |
| `cofnij_kuwete` | (kuweta,) | `rano.kuweta_do_cofniecia` z biezacego stanu | EK:190, EK:986-993, EK:1072 |
| `wybierz_kuwete` | (kuweta,) | `self._kuwety[wiersz]` (zapamietana krotka, indeks wiersza) | EK:272 |
| `wybierz_kuwete` | (bufor,) | `_bufor` | EK:1062 |
| `ustaw_kolejnosc` | (k,) | stala przycisku | EK:176 |
| `cofnij_zastapienie` / `cofnij_dopuszczenie` / `pomin_skan` / `cofnij_pominiecie` | (skan_id,) | lambda przy budowie akcji karty (karta ma staly skan_id) | EK:775 |
| `zamknij_brak_recznie` | (projekt_id, powod) | `b` zapamietany w lambdzie przy budowie panelu | EK:400, EK:363 |
| `cofnij_zamkniecie_reczne` | (projekt_id,) | `_ostatnie[0]` (zapamietane) | EK:379 |
| `excel_pokaz` | (sesja_pieca_id,) | biezacy stan / `sid` zapamietany przy budowie przycisku zaleglego | EK:372-374, EK:453-454 |
| panele (numer plytki, pytania, komunikaty) | wg panelu | argumenty wbudowane w panel przy jego budowie (`czesci.py`, poza zakresem) | EK:959, EK:963-970 |
| zapytanie `projekty_kuwety` | (kuweta,) | tekst pola; wywolanie wprost kontrolera, nie przez okno | KA:314, EK:607 |
Zadne polecenie ekranu nie niesie numeru gniazda ani sha16 skanu. Mapa wysyla (skan_id, nr) tylko lokalnie (EK:144-145).

---------------------------------------------------------------------------------------------------------------------------

## F. Rozjazdy opis - kod

### F.1 opisy_modulow\session.md (czesc od linii 75 do konca)
1. DS:77 "konflikt (ten sam projekt na dwoch plytkach)" - SR:751-752: konflikt = ten sam projekt w dwoch miejscach (skan_id, gniazdo),
   takze dwa gniazda JEDNEJ plytki i dwie prace bez gniazda; nie potrzeba dwoch plytek.
2. DS:82 `podaj_numer_plytki` "(tylko numer plytki porannej ukladu: kwadratowe 4-6, okragle 9; ...)" - SR:107-114, SR:367-377: okragla
   ramkowa poranna -> 4-6 (nie 9). (Opis uzupelnia to dopiero DS:198.)
3. DS:85 "kod z POWODY_ZAMKNIECIA: nie_praca_z_cyrkonu, zaginiona, wydana_bez_skanu, inny" - SR:76: piec kodow, takze "nie_bedzie_dofrezowany".
4. DS:89 "plan_plytek() i zamknij_piec() = tylko piec biezacy (bez niego odmowa z lista starych piecow)" - lista starych piecow tylko
   w `zamknij_piec` (SR:1073-1075); `plan_plytek` odmawia bez listy (SR:1290-1291).
5. DS:89 "Kontrakt dla A7 (D4 r3): piec otwarty ponownie nie musi byc biezacy - okno pracuje wtedy na sesja_pieca_id / plan_id z wyniku
   otworz_piec_ponownie (stan_pieca(id), zamknij_piec(sesja_pieca_id=...))" - KO:1968-1975: stan ekranu bierze tylko `otwarty_piec()`
   (biezacy), a bez niego ostatni ZAMKNIETY; piec otwarty ponownie, ktory nie jest biezacy, nie jest pokazywany, a "Zamknij piec"
   ekranu wysyla id pokazanego pieca (EK:846).
6. DS:91 "Zlecenie kompletne = kazdy jego punkt ma stan rozpoznany (w tym albo w poprzednim piecu) albo zamkniety_recznie" - SR:742-744,
   SR:826: dla pieca otwartego liczy sie rozpoznanie przez KAZDY inny piec (`!= pid`), takze pozniejszy; "w tym piecu" = praca liczona
   (SR:704), nie stan.
7. DS:99 tabela, `pewna`: "dopasowanie zielony (pokrycie >= 0,85 i przewaga >= 0,1), jeden projekt o tym sha16" - klasa pewna = kazda
   praca z `projekt_id` bez decyzji (SR:781-782); `projekt_id` z SR:581-591: progow pokrycia/przewagi session_rano nie sprawdza (tylko
   `status_match == "zielony"`), a w galezi puli per praca (SR:584-589) liczba projektow o tym sha16 nie jest sprawdzana.
8. DS:101 tabela, `dwuznaczna`: "1. kandydat z pokryciem >= prog_kandydata (0,6), kandydat w indeksie" - SR:775:
   `any(k["projekty"] for k in kand)` - wystarczy, ze w indeksie jest 1. ALBO 2. kandydat.
9. DS:102 tabela, `nieznana`: "brak kandydata, kandydat slabszy niz prog albo decyzja 'bez projektu'" - SR:775-776: takze 1. kandydat
   >= progu bez zadnego kandydata w indeksie; takze decyzja `wybor_kandydata`, ktorej sha16 po cofnieciu nowszej decyzji nie daje
   jednego projektu (SR:573, SR:594-596).
10. DS:103 tabela, `poprawka`: "projekt, ktorego punkt zamknal juz WCZESNIEJSZY piec" - SR:744: w piecu otwartym kazdy inny piec (`!= pid`).
11. DS:107 "Napis dofrezowany ... przy false ... okno powinno pokazac inny napis" - kontroler tak robi dla gniazda/widoku (KO:1733-1734),
    ale licznik w naglowku ekranu bierze `ST.status_rano("poprawka")` = "zab dofrezowany" dla kazdej poprawki (EK:810-819).
12. DS:107 "Pola pracy: id, skan_id, ..., kuweta_do_sprawdzenia" oraz "kandydaci (... miniatura z cechy_stl po sha16)" - SR:794-804 zwraca
    tez `nr_fragmentu`, `status_fragmentu`, `status_match`, `pewnosc`, `czas_decyzji`; miniatur session_rano nie zwraca (dokleja je kontroler).
13. DS:109 "decyzja poranna nie zmienia stan_punktow" - zmieniaja: `zamkniecie_reczne` (SR:1240-1243), `otworz_piec_ponownie`
    (SR:1169), cofniecie zamkniecia recznego (SR:1264-1267), `cofnij_przeniesienie` (SR:1055); prawdziwe tylko dla decyzji o pracach.
14. DS:111 "Dwa aktywne skany z tym samym numerem = BLOKADA (B2): plytka nie idzie do planu ramki ..., 'Zamknij piec' odmawia" - SR:838-845:
    tylko plytki na ramce; dwie okragle n9 z tym samym numerem - ostrzezenie (SR:870-873), prace licza sie.
15. DS:113 "(4) skan blad, niezgodny_uklad, plytka_nie_z_trybu - odblokowuje go pozniejszy aktywny skan z tym samym numerem plytki albo
    pomin_skan" - SR:905 wymaga numeru na skanie blokujacym; skan `blad` nie ma numeru (SE:450-452) i nie mozna go podac (SR:367-370) -
    odblokowuje go tylko `pomin_skan`.
16. DS:123 "pominiete (bez_numeru, zdublowane_plytki, poza_ramka - okragle testowe, nie poranne, numer spoza, ...)" - SR:1303-1306: brak
    numeru sprawdzany najpierw, wiec okragla testowa i plytka nie poranna BEZ numeru trafiaja do `bez_numeru`, nie do `poza_ramka`.
17. DS:168-169 "przypisanie automatyczne pracy zielonej = projekt wpisu puli z wyniku (Sesja.projekt_wpisu_puli ...), gdy jest i nie jest
    usuniety; inaczej jak dotad po sha16" - SR:583-591: funkcja `wpis_puli_pracy`; wpis puli z `projekt_id` None albo brakujacym projektem
    -> None (bez szukania po sha16); usuniety -> nastepca. Po sha16 tylko, gdy wpisu puli nie ma. (Zgodnie z pozniejszym DS:177-179.)
18. DS:202 "skan plytki okraglej ramkowej po skanie kwadratu o tym samym numerze ... w oknie 60 min z tymi samymi pracami daje PYTANIE" -
    rano `_propozycje` (SR:454-478) nie ma okna czasu (zgodnie z DS:111 "Bez okna czasu w piecu").

### F.2 opisy_modulow\ui_rano.md
1. DU:25 "panele (najwyzej 3)" - EK:942-949: panel osoby i pytanie "Zamknac piec mimo ..." dodawane poza limitem; limit PANELI=3
   (EK:46, EK:968) dotyczy pozostalych; do tego etykieta "jeszcze n" (EK:972-973).
2. DU:39-40 "przy zleceniu z brakami (A6 D2) - ten sam bursztyn, napis 'zab juz rozpoznany'" - licznik naglowka zawsze "zab dofrezowany"
   (EK:815 `ST.status_rano(klasa)`, ST:116); mapa i widok - zgodnie.
3. DU:45-46 "Pole numeru kuwety ... (po wyszukaniu fokus zostaje w polu)" - KA:281, KA:283, KA:286-288: fokus wraca tylko po Enter
   w polu; po przycisku "Pokaz projekty" (`fokus=False`) nie.
4. DU:47-48 "po zmianie zestawu plytek (nowa plytka, zastapienie) mapy sa przez 800 ms przygaszone" - EK:749: `if stare and stare != set(self._karty)`
   - gdy poprzedni zestaw byl pusty (pierwsza plytka na ekranie, nowy piec po pustym), ochrony nie ma.
5. DU:56 "na ekranie nie ma sciezek ani nazw plikow / folderow" - NR:167 `EXCEL_FOLDER = "Kuweta {kuweta} (kropka srodkowa) folder zlecenia: {folder}"`
   (panel Excela; sam opis DU:81 mowi "folder tylko na ekranie"). okno_excela.py nie byl czytany.
6. DU:114-115 "'Wroc do rozstrzygania' (... otwiera sie pierwsza taka praca)" - EK:859: pierwsza taka praca W GNIEZDZIE
   (`x.gniazdo is not None`); praca bez gniazda nie otwiera sie (i nie da sie jej otworzyc z mapy, E.2).
7. DU:117-118 "przy otwartym pytaniu Esc = 'Wroc do rozstrzygania', Enter nie potwierdza kuwety" - EK:1053 `and not self._bufor`:
   z wpisanym numerem kuwety Esc czysci bufor (EK:1075-1078), a Enter wysyla `wybierz_kuwete(bufor)` (EK:1060-1063).
Niepewne (nie rozstrzygniete statycznie): DU:54-55 "Okno i ekran bez cykli referencji (weakref ..., slaba(metoda) dla funkcji podanych
widokowi pracy)" - sygnaly laczone z lambdami przechwytujacymi `self` ekranu: EK:560, EK:591-593, EK:608, EK:773, EK:775
(slaba() tylko EK:144, EK:607, EK:610, EK:884). Czy to tworzy cykl widoczny dla GC - nie ustalono.

### F.3 Liczba zdan zgodnych (liczone: zdanie albo pozycja listy/tabeli = jedno twierdzenie)
- session.md (linie 75-206): zgodnych 131; rozjazdow 18 (F.1); niesprawdzalnych bez uruchomienia albo dotyczacych tylko session.py
  czesci wieczornej / A4 / okno_excela / testow: ok. 17.
- ui_rano.md: zgodnych 43; rozjazdow 7 (F.2) + 1 niepewny; niesprawdzalnych statycznie (piksele, testy, okno.py, czesci.py,
  okno_excela.py, pytania kontrolera): ok. 20.
