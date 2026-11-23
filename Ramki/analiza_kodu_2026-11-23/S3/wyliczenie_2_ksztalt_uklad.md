# S3 / wyliczenie 2 - rozroznienia ksztalt / uklad / numer plytki oraz przeliczenia gniazdo -> mapa / dioda / Excel

Data: 2026-11-23. Worktree: `<PC-katalog>\qc-wt\analiza-s3`. Wszystkie sciezki ponizej sa wzgledne do `Ramki\stanowisko\`
(np. `stanowisko/session.py:129`, `ramka/kalibracja.py:42`, `modele_plytek/okragla_wieczorna/uklad.json:65`).

Metoda: analiza tylko do odczytu. Pliki z zakresu przeczytane w calosci: `stanowisko/ramka_protokol.py`, `stanowisko/ui/mapa.py`,
`stanowisko/ui/mapa_rano.py`, wszystkie `ramka/*.py`, `ramka/README.md`, `stanowisko/uklad.py`, `stanowisko/katalog.py`,
10 plikow `modele_plytek/*/uklad.json`, `ustawienia.przyklad.toml` - bezposrednio; `session.py`, `session_rano.py`, `indicate.py`,
`statusy.py`, `excel.py`, `excel_com.py`, `ui/czesci.py`, `ui/ekran_rano.py`, `ui/okno.py`, `ui/okno_excela.py`, `ui/kandydaci.py`,
`ui/napisy.py`, `ui/napisy_rano.py`, `ui/obraz.py`, `ui/styl.py`, `ui/__init__.py` - w calosci przez czytajacych pomocniczych, a kazda
linia przytoczona w tabelach sprawdzona ponownie Read/Grep. Porownanie list gniazd miedzy plikami `uklad.json` zrobione
`ConvertFrom-Json` (PowerShell, bez Pythona). Cytaty kodu: polskie znaki zamienione na ASCII, znak `|` w cytacie zapisany jako `\|`.
Bez oceny wagi i bez propozycji poprawek.

## Skroty rodzin

| skrot | uklady (klucz `[plytki]` = katalog `modele_plytek/<nazwa>`) | numery plytek (`plytka_n*.stl`) |
|---|---|---|
| K59 | `wieczorna` (-W), `poranna` (-P) - kwadrat, uklad gniazd R59 | W: 1, 2, 3; P: 4, 5, 6 |
| K54 | `wieczorna_r54`, `poranna_r54` - kwadrat, uklad gniazd R54 | W: 1, 2, 3; P: 4, 5, 6 |
| O54 | `okragla_wieczorna_r54`, `okragla_poranna_r54` - okragla R54 | W: 8; P: 9 |
| O59 | `okragla_wieczorna`, `okragla_poranna` - okragla R59 | W: 8; P: 9 |
| OR | `okragla_ramkowa_wieczorna`, `okragla_ramkowa_poranna` - okragla ramkowa | W: 1, 2, 3; P: 4, 5, 6 |

Przyrostek `-W` / `-P` = uklad wieczorny / poranny danej rodziny. "K" = K59 i K54 razem.

---

## Tabela Z - zrodla (skad sie bierze nazwa ukladu, numer plytki, ksztalt)

| nr | plik:linia | element | regula / wartosc |
|---|---|---|---|
| Z01 | stanowisko/uklad.py:22, 318 | `KATALOG_MODELI`, `wczytaj` | `modele_plytek` obok pakietu; katalog ukladu domyslnie `KATALOG_MODELI / nazwa` |
| Z02 | stanowisko/uklad.py:26, 253-255 | `BITY_KODU`, `_waliduj` | dolki kodu `("A", "B", "C", "D")`; w pliku dozwolone A,B,C albo A,B,C,D |
| Z03 | stanowisko/uklad.py:27, 295-309, 356 | `WZOR_PLIKU_PLYTKI`, `_numery_plytek` | numery plytek ukladu = n z `plytka_n<n>.stl`, zakres `1 <= n < 2**liczba_bitow` (:306), lista posortowana (:309) -> `UkladPlytki.numery` |
| Z04 | stanowisko/uklad.py:28, 300-301 | `PLIK_PLYTKI_BAZOWEJ` | `plytka_bazowa.stl` pomijany (jest w 6 katalogach okraglych, nie ma go w 4 kwadratowych) |
| Z05 | stanowisko/uklad.py:29, 32-38 | `WZOR_WERSJI_UKLADU`, `typ_plytki` | usuwa `_r\d+$`: `okragla_poranna_r54` -> `okragla_poranna` |
| Z06 | stanowisko/uklad.py:140, 313-317, 348 | `UkladPlytki.nazwa` | = nazwa przekazana do `wczytaj` (klucz `[plytki]`), NIE pole `plate` z pliku |
| Z07 | stanowisko/uklad.py:149-151, 358-359 | `shape`, `d`, `flat` | `shape` domyslnie `"square"`; `d` tylko dla `"round"`; `flat` = slownik z pliku |
| Z08 | stanowisko/uklad.py:220-225 | `_waliduj` | `shape` tylko `"square"` / `"round"`; wymiar `size` (square) albo `d` (round) |
| Z09 | stanowisko/uklad.py:230-232 | `_waliduj` | `flat` dozwolony tylko przy `shape == "round"` |
| Z10 | stanowisko/uklad.py:327-328 | `wczytaj` | `size = float(d["size"]) if "size" in d else float(d["d"])` - pliki okragle maja oba pola (100.0 / 100.0) |
| Z11 | stanowisko/uklad.py:352 | `wczytaj` | `notch` domyslnie `{}` (pliki okragle nie maja `notch`) |
| Z12 | stanowisko/uklad.py:186-192 | `numer_z_bitow` | n = A + 2*B + 4*C + 8*D (D tylko przy 4 dolkach) |
| Z13 | stanowisko/katalog.py:100-106, 126-127, 163 | `gniazdo_dla`, `zbuduj`, `streszczenie` | rozroznia tylko typ GNIAZDA (`round` / `trough`); slownik plytek nazwa -> (uklad, wspolczynnik) podaje wolajacy; brak warunkow na nazwe / numer / ksztalt plytki |
| Z14 | ustawienia.przyklad.toml:18-22, 28-31, 35-36 | `[plytki]` | 10 kluczy: R59 (:19-22), R54 (:28-31), OR (:35-36); wartosc = `modele_plytek/<klucz>` |
| Z15 | ustawienia.przyklad.toml:23-27 | komentarz | R59: wieczorna 18 + 1 rynienka, poranna 23 + 1; R54: 18 + 2 i 31 + 2; numery te same (n1-n6, n8, n9); uklad rozpoznawany ze skanu |
| Z16 | ustawienia.przyklad.toml:32-34 | komentarz | OR: gniazda, stozki i numery jak kwadrat R59, obrys i dolki kodu jak plytka okragla testowa; wiersze NA KONCU (kolejnosc = kolejnosc kandydatow rozpoznania) |
| Z17 | ustawienia.przyklad.toml:16 | `[sciezki] kalibracja_ramek` | `dane/kalibracja_ramek.json`; brak pliku = wartosci startowe z geometrii plytek |
| Z18 | ustawienia.przyklad.toml:96-101 | `[ramki]` | `port`, `wieczorna_host`, `poranna_host` (rola W / P = host), `klucz`, `odpytywanie_s` |
| Z19 | stanowisko/session.py:402 | `Sesja.przyjmij_wynik` | `uklad=wynik.get("plytka")` - nazwa ukladu z wyniku analizy trafia do bazy jako `skany.uklad` (dalej `s["uklad"]`) |
| Z20 | (kontekst, poza zakresem) stanowisko/ustawienia.py:147-149 | `UKLADY_WBUDOWANE` | te same 10 nazw co Z14 |
| Z21 | (kontekst, poza zakresem) stanowisko/kontroler_api.py:1802, 3210 | `Plytka.typ` | `typ = SE.typ_plytki(s["uklad"])` (rano / wieczor) - wejscie dla A61, A64 |
| Z22 | (kontekst, poza zakresem) stanowisko/kontroler_api.py:131 | `NUMERY_PLYTEK_ZAPASOWE` | `tuple(range(1, 10))` - wejscie dla A66, A70 |
| Z23 | (kontekst, poza zakresem) stanowisko/kontroler_api.py:416 | `Plytka.na_ramce` | komentarz: "kwadratowa albo okragla ramkowa poranna, numer 4-6" |

### Tabela Z-ukl - 10 plikow uklad.json (stan w worktree)

| katalog | `plate` (:2) | `shape` | wymiar | gniazd (okragle + rynienki) | id | pliki STL | dolki kodu | `magnet_pockets` |
|---|---|---|---|---|---|---|---|---|
| wieczorna | wieczorna | square (:65) | size 96 (:66) | 19 (18 + 1) | 1..19 | n1, n2, n3 | 4 (A-D, x = -45) | 3: (-42,-42) (-42,42) (42,42) (:74-96) |
| poranna | poranna | square (:65) | size 96 (:66) | 24 (23 + 1) | 1..24 | n4, n5, n6 | 4 (A-D, x = -45) | 3 jak wyzej |
| wieczorna_r54 | wieczorna | brak klucza (= square) | size 96 (:11) | 20 (18 + 2) | 1..20 | n1, n2, n3 | 3 (A-C) | 3 jak wyzej |
| poranna_r54 | poranna | brak klucza (= square) | size 96 (:11) | 33 (31 + 2) | 1..33 | n4, n5, n6 | 3 (A-C) | 3 jak wyzej |
| okragla_wieczorna_r54 | okragla_wieczorna | round (:65) | size 100, d 100 (:66-67) | 20 (18 + 2) | 1..20 | n8 + bazowa | 4 (A-D) | [] (:75) |
| okragla_poranna_r54 | okragla_poranna | round (:65) | 100 / 100 | 33 (31 + 2) | 1..33 | n9 + bazowa | 4 (A-D) | [] (:75) |
| okragla_wieczorna | okragla_wieczorna | round (:65) | 100 / 100 | 19 (18 + 1) | 1..19 | n8 + bazowa | 4 (A-D) | [] (:75) |
| okragla_poranna | okragla_poranna | round (:65) | 100 / 100 | 24 (23 + 1) | 1..24 | n9 + bazowa | 4 (A-D) | [] (:75) |
| okragla_ramkowa_wieczorna | okragla_ramkowa_wieczorna | round (:65) | 100 / 100 | 19 (18 + 1) | 1..19 | n1, n2, n3 + bazowa | 4 (A-D) | 3 (:75-100) |
| okragla_ramkowa_poranna | okragla_ramkowa_poranna | round (:65) | 100 / 100 | 24 (23 + 1) | 1..24 | n4, n5, n6 + bazowa | 4 (A-D) | 3 (:75-100) |

Porownanie list `sockets` (pole po polu, ConvertFrom-Json): `okragla_wieczorna` = `wieczorna` = `okragla_ramkowa_wieczorna`;
`okragla_poranna` = `poranna` = `okragla_ramkowa_poranna`; `okragla_wieczorna_r54` = `wieczorna_r54`; `okragla_poranna_r54` = `poranna_r54`
(0 roznic w kazdej parze). Klucz `plate` jest wspolny dla R54 i R59 tej samej rodziny (`wieczorna`, `poranna`, `okragla_wieczorna`,
`okragla_poranna`); OR ma `plate` rowne nazwie ukladu.

---

## Tabela A - miejsca rozrozniajace rodzine plytki albo wieczorna / poranna

Kolumna "galezie": K59 / K54 / O54 / O59 / OR wg skrotow wyzej. "nazwa (A04)" = rozroznienie przez funkcje z wiersza A04 itd.

| nr | plik:linia | funkcja | po czym rozroznia | warunek (cytat, 1 linia) | ktore rodziny do ktorej galezi | uklad / numer nieznany (galaz domyslna) |
|---|---|---|---|---|---|---|
| A01 | stanowisko/session.py:78 | (modul) `TYP_PLYTKI_TRYBU` | tryb -> typ plytki (slownik nazw) | `TYP_PLYTKI_TRYBU = {TRYB_WIECZOR: "wieczorna", TRYB_RANO: "poranna"}` | tryb wieczor -> "wieczorna", rano -> "poranna"; rodziny trafiaja tu przez A07 | inny tryb: odrzucany wczesniej w A08 |
| A02 | stanowisko/session.py:129 | (modul) `_WZOR_UKLADU` | nazwa (regex, prefiks `okragla_`, `ramkowa_`, przyrostek `_r\d+`) | `^(?P<okragla>okragla_(?P<ramkowa>ramkowa_)?)?(?P<typ>wieczorna\|poranna)(?P<wersja>_r\d+)?$` | K59: okragla F, ramkowa F, wersja ""; K54: F, F, "_r54"; O54: T, F, "_r54"; O59: T, F, ""; OR: T, T, "" | nazwa spoza wzorca -> brak dopasowania; wzorzec przyjmuje tez nazwy bez katalogu modeli (np. `okragla_ramkowa_poranna_r54`, `poranna_r99`) |
| A03 | stanowisko/session.py:131 | (modul) `NUMERY_RAMKOWE` | numer (slownik po typie) | `NUMERY_RAMKOWE = {"wieczorna": (1, 2, 3), "poranna": (4, 5, 6)}` | uzywany tylko dla OR (A06) | - |
| A04 | stanowisko/session.py:141-142 | `czesci_ukladu` | nazwa (A02) | `m = _WZOR_UKLADU.fullmatch(nazwa) if nazwa else None` | jak A02 -> slownik {okragla, ramkowa, typ, wersja} | nieznana nazwa / None -> None |
| A05 | stanowisko/session.py:149 | `rodzina_ukladu` | nazwa (A04) | `return c["typ"] + c["wersja"] if c else nazwa` | K59, O59, OR -> "wieczorna" / "poranna" (jedna rodzina); K54, O54 -> "wieczorna_r54" / "poranna_r54" | nieznana -> sama nazwa (nie None); None -> None |
| A06 | stanowisko/session.py:155 | `numery_ramkowe` | nazwa (pole `ramkowa`) | `return NUMERY_RAMKOWE[c["typ"]] if c is not None and c["ramkowa"] else None` | OR-W -> (1, 2, 3), OR-P -> (4, 5, 6); K59, K54, O54, O59 -> None | None |
| A07 | stanowisko/session.py:161 | `typ_plytki` | nazwa (A04) | `return c["typ"] if c else None` | wszystkie -W -> "wieczorna", wszystkie -P -> "poranna" (bez ksztaltu i wersji) | None |
| A08 | stanowisko/session.py:166 | `sprawdz_tryb` | tryb (klucze A01) | `if tryb not in TYP_PLYTKI_TRYBU:` | - (tryb programu) | BladSesji |
| A09 | stanowisko/session.py:178-181 | `powod_nie_z_trybu` | nazwa (A07) + tryb | `return f"plytka {typ} w trybie {tryb}" if typ != TYP_PLYTKI_TRYBU[tryb] else None` | -W w trybie wieczor i -P w trybie rano -> None; odwrotnie -> powod | typ None (:179) -> powod "nieznany uklad plytki ..." |
| A10 | stanowisko/session.py:380 | `Sesja.przyjmij_wynik` | nazwa (A09) | `elif powod_nie_z_trybu(wynik.get("plytka"), tryb) is not None:  # takze uklad o nieznanej nazwie` | jak A09 -> status `plytka_nie_z_trybu` (:381); wczesniej :378 `uklad_zgodny` False -> `niezgodny_uklad` | nieznany uklad / brak `plytka` -> `plytka_nie_z_trybu` |
| A11 | stanowisko/session.py:388-392 | `Sesja.przyjmij_wynik` | numer + nazwa (A06) | `if dozwolone is not None and numer is not None and numer not in dozwolone:` | OR-W z numerem spoza 1-3, OR-P spoza 4-6 -> numer None, zrodlo "nieznany"; K59, K54, O54, O59 -> numer zapisany bez sprawdzenia | nieznany uklad -> bez sprawdzenia |
| A12 | stanowisko/session.py:853 | `Sesja.podaj_numer_plytki` | numer | `if n < 1:` | kazda rodzina: kazde n >= 1 przyjete (bez gornej granicy, bez sprawdzenia wg ukladu) | nie-liczba -> n = 0 -> BladSesji |
| A13 | stanowisko/session.py:915 | `Sesja._niezgodnosc` | numer | `if nowy["numer_plytki"] is not None and stary["numer_plytki"] is not None and nowy["numer_plytki"] != stary["numer_plytki"]:` | sam numer: K n1 i OR n1 = ten sam numer | - |
| A14 | stanowisko/session.py:917-918 | `Sesja._niezgodnosc` | nazwa (A05) | `if a and b and a != b:` | K59 / O59 / OR tego samego typu -> zgodne; K54 / O54 -> zgodne; R54 vs R59 -> "inny uklad plytki" | uklad pusty / None -> sprawdzenie pominiete; nieznany -> porownanie surowej nazwy |
| A15 | stanowisko/session.py:985, 989 | `Sesja._propozycja_zastapienia` | numer (SQL) + nazwa (A14) | `AND ((numer_plytki IS NOT NULL AND numer_plytki = ?) OR (sha16 IS NOT NULL AND sha16 = ?))` | kandydat: ten sam numer albo sha16; :989 odrzuca rodziny niezgodne (A14) | - |
| A16 | stanowisko/session.py:1031 | `Sesja._zastap` | numer + nazwa (A13, A14) | `powod = self._niezgodnosc(nowy, poprzedni)` | jak A13 / A14 -> BladSesji przy powodzie | - |
| A17 | stanowisko/session.py:1188 | `Sesja.stan_wieczoru` | nazwa (A09) | `"powod": powod_nie_z_trybu(s["uklad"], s["tryb"]) if s["status"] == STATUS_PLYTKA_NIE_Z_TRYBU else None,` | tylko tekst powodu | jak A09 |
| A18 | stanowisko/session_rano.py:84-85 | (modul) stale | numer | `NUMERY_PLYTEK_PORANNYCH = (4, 5, 6)` / `NUMERY_PLYTEK_OKRAGLYCH_PORANNYCH = (9,)` | uzywane w A21 | - |
| A19 | stanowisko/session_rano.py:110 | `numery_plytki` | nazwa (A04 + A01) | `if c is None or c["typ"] != SE.TYP_PLYTKI_TRYBU[SE.TRYB_RANO]:` | wszystkie -W -> None | nieznany -> None |
| A20 | stanowisko/session_rano.py:112-113 | `numery_plytki` | nazwa (pole `ramkowa`) | `if c["ramkowa"]:  # E3-O2: plytka okragla ramkowa n4-n6 ...` | OR-P -> `SE.numery_ramkowe` = (4, 5, 6) | - |
| A21 | stanowisko/session_rano.py:114 | `numery_plytki` | nazwa (pole `okragla`) | `return NUMERY_PLYTEK_OKRAGLYCH_PORANNYCH if c["okragla"] else NUMERY_PLYTEK_PORANNYCH` | O54-P, O59-P -> (9,); K59-P, K54-P -> (4, 5, 6) | - |
| A22 | stanowisko/session_rano.py:121 | `na_ramce` | nazwa (A04) | `return c is not None and c["typ"] == SE.TYP_PLYTKI_TRYBU[SE.TRYB_RANO] and (not c["okragla"] or c["ramkowa"])` | True: K59-P, K54-P, OR-P; False: O54-P, O59-P i wszystkie -W | False |
| A23 | stanowisko/session_rano.py:202 | `SesjaRano._ostatnia_aktywnosc` | nazwa (A19) | `... if s["id"] not in pominiete and numery_plytki(s["uklad"]) is not None] + [piec["otwarto"]])` | liczone wszystkie -P; -W pomijane | nieznany -> pominiety |
| A24 | stanowisko/session_rano.py:367-368 | `SesjaRano.podaj_numer_plytki` | nazwa (A19) | `if dozwolone is None:` | -W -> BladSesji "nie jest plytka poranna" | nieznany -> BladSesji |
| A25 | stanowisko/session_rano.py:375 | `SesjaRano.podaj_numer_plytki` | numer | `if n not in dozwolone:` | K59-P, K54-P, OR-P: tylko 4, 5, 6; O54-P, O59-P: tylko 9 | nie-liczba -> n None -> BladSesji |
| A26 | stanowisko/session_rano.py:379 | `SesjaRano.podaj_numer_plytki` | numer + nazwa (A22) | `if sk["numer_plytki"] is not None and n != sk["numer_plytki"] and na_ramce(sk["uklad"]):` | kontrola "nowy wsad" tylko K59-P, K54-P, OR-P; O54-P, O59-P pomijane | - |
| A27 | stanowisko/session_rano.py:380-384 | `SesjaRano.podaj_numer_plytki` | numer (SQL) + nazwa (A22) | `for x in (x for x in inne if x["id"] not in pominiete and na_ramce(x["uklad"])):` | skany z tym samym numerem z K59-P, K54-P, OR-P porownywane miedzy soba (bez rodziny) | - |
| A28 | stanowisko/session_rano.py:470-471 | `SesjaRano._propozycje` | numer + nazwa (A05) | `and SE.rodzina_ukladu(s["uklad"]) == SE.rodzina_ukladu(t["uklad"]))` | jedna rodzina: K59-P, O59-P, OR-P; druga: K54-P, O54-P | nieznany: porownanie surowej nazwy; None == None |
| A29 | stanowisko/session_rano.py:817, 821 | `SesjaRano._oblicz` | nazwa (A19, A22) + numer | `"zastepuje_id": s["zastepuje_id"], "na_ramce": na_ramce(s["uklad"]) and s["numer_plytki"] in (dozwolone or ()),` | True tylko K59-P, K54-P, OR-P z numerem 4-6; O54-P, O59-P zawsze False | False |
| A30 | stanowisko/session_rano.py:822 | `SesjaRano._oblicz` | nazwa (A09) | `"powod": SE.powod_nie_z_trybu(s["uklad"], s["tryb"]) if s["status"] == SE.STATUS_PLYTKA_NIE_Z_TRYBU else None, ...` | tylko tekst | jak A09 |
| A31 | stanowisko/session_rano.py:838 | `SesjaRano._oblicz` | nazwa (A22) | `kwadratowe = [s for s in aktywne if na_ramce(s["uklad"])]` | lista "kwadratowe" = K59-P, K54-P i OR-P | -W / nieznane: w zadnej liscie |
| A32 | stanowisko/session_rano.py:839 | `SesjaRano._oblicz` | nazwa (A19, A22) | `okragle = [s for s in aktywne if numery_plytki(s["uklad"]) is not None and not na_ramce(s["uklad"])]` | O54-P, O59-P | - |
| A33 | stanowisko/session_rano.py:840-845 | `SesjaRano._oblicz` | numer (w obrebie A31) | `zdublowane = sorted(n for n, ids in po_numerze.items() if len(ids) > 1)` | duplikat = ten sam numer w K59-P / K54-P / OR-P bez wzgledu na rodzine; `bez_numeru` (:840) tylko z A31 | - |
| A34 | stanowisko/session_rano.py:866-873 | `SesjaRano._oblicz` | numer + nazwa (A05) | `okragle_po_numerze.setdefault((s["numer_plytki"], SE.rodzina_ukladu(s["uklad"])), []).append(s["id"])` | O54-P i O59-P w osobnych grupach; bez numeru / duplikat -> tylko ostrzezenie | - |
| A35 | stanowisko/session_rano.py:905 | `SesjaRano._blokady` | numer | `ponowny = s["numer_plytki"] is not None and any(t["id"] > s["id"] and t["numer_plytki"] == s["numer_plytki"] for t in aktywne)` | sam numer, kazda rodzina | - |
| A36 | stanowisko/session_rano.py:916-919 | `SesjaRano._blokady` | nazwa (A19) | `if dozwolone is None:` | -W -> blokada "nie jest plytka poranna" | nieznany -> blokada |
| A37 | stanowisko/session_rano.py:920-924 | `SesjaRano._blokady` | nazwa (A22) + numer (:922) | `elif not na_ramce(s["uklad"]):  # okragla poranna: numer nie blokuje (ramka jej nie pokazuje)` | O54-P, O59-P -> tylko ostrzezenie (numer inny niz 9 dopisuje "numer spoza 9") | - |
| A38 | stanowisko/session_rano.py:925 | `SesjaRano._blokady` | numer | `elif s["numer_plytki"] is not None and s["numer_plytki"] not in dozwolone:` | K59-P, K54-P, OR-P z numerem spoza 4-6 -> blokada | - |
| A39 | stanowisko/session_rano.py:1303-1306 | `SesjaRano.plan_plytek` | numer, potem pole `na_ramce` (A29) | `if s["numer_plytki"] is None:` / `elif not s["na_ramce"]:` | bez numeru (kazda rodzina) -> `bez_numeru`; O54-P, O59-P -> `poza_ramka`; K59-P, K54-P, OR-P z numerem 4-6 -> plan (tylko skany `aktywny`, :1301) | aktywny skan -W / nieznany z numerem -> `poza_ramka` |
| A40 | stanowisko/session_rano.py:1315 | `SesjaRano.plan_plytek` | numer | `if n in zdublowane or len(po_numerze[n]) > 1:` | ten sam numer na K i OR -> plytka pominieta | - |
| A41 | stanowisko/indicate.py:147 | `KlientRamki.__init__` | rola ramki | `if rola not in ("W", "P"):` | - | ValueError |
| A42 | stanowisko/indicate.py:337, 349, 386, 403, 441, 455, 459, 482, 715, 733, 775, 833, 864, 870, 881, 888, 898, 1019, 1044, 1065, 1141 | rozne metody `KlientRamki` | rola W / P (nie plytka) | np. :482 `if self.rola != "W":` | wynik pojedynczego skanu tylko W; plan pieca i kuwety tylko P | - |
| A43 | stanowisko/indicate.py:500-501 | `KlientRamki._sprawdz_wynik` | numer | `if numer is None:` | kazda rodzina bez numeru -> "bez_numeru" (ramka ciemna) | - |
| A44 | stanowisko/indicate.py:502-503 | `KlientRamki._sprawdz_wynik` | numer (`RP.RODZINY["W"]`) | `if not _int(numer) or numer not in RP.RODZINY["W"]:` | K59-W, K54-W, OR-W (1-3) -> dalej; O54-W, O59-W (8) i kazda -P (4-6, 9) -> "zla_plytka" | inny numer / nie-int -> "zla_plytka" |
| A45 | stanowisko/indicate.py:505-507 | `KlientRamki._sprawdz_wynik` | nazwa (klucz w kalibracji ramki W) | `gn = (kal or {}).get("ramki", {}).get("W", {}).get(uklad, {}).get("gniazda") if isinstance(uklad, str) else None` | domyslne wpisy W: `wieczorna`, `wieczorna_r54`, `okragla_ramkowa_wieczorna` (A80) -> dalej; O54-W / O59-W bez wpisu | brak wpisu -> "brak_kalibracji" |
| A46 | stanowisko/indicate.py:508-512 | `KlientRamki._sprawdz_wynik` | numer gniazda vs klucze kalibracji | `if c is not None and str(int(g)) not in gn:` | gniazdo swiecace bez bloku -> "brak_kalibracji" | klucz nie-liczba (:509) -> "brak_kalibracji" |
| A47 | stanowisko/indicate.py:854 | `KlientRamki._zastosuj` | numer (zdjecie plytki z ramki W) | `if typ == "plytka" and self.rola == "W" and z["poprzednia"] > 0:` | kazdy numer > 0 | - |
| A48 | stanowisko/indicate.py:1019-1029 | `KlientRamki._zbuduj_plan` | rola + delegacja do `RP.plan_rano` (A51, A52) | `if self.rola == "P":` | filtr numeru / kalibracji w ramka_protokol | kalibracja None -> `_blad = "brak_kalibracji"` (:1022-1023) |
| A49 | stanowisko/indicate.py:1035-1039 | `KlientRamki._zbuduj_plan` | delegacja do `RP.plan_wieczor` (A51, A52) | `if not plan["plytki"]:` | plytki odrzucone w A51 / A52 -> brak planu (None) | - |
| A50 | stanowisko/indicate.py:1185 | `KlientRamki._po_planie` | kod bledu ramki | `self._blad = "plan_innej_ramki" if kod == "plan_innej_ramki" else "plan_odrzucony"` | - | "plan_odrzucony" |
| A51 | stanowisko/ramka_protokol.py:149-151 | `_plytki` | numer (`RODZINY[rola]`) | `if n is None or n not in RODZINY[rola]:` | W: 1-3 (K59-W, K54-W, OR-W), P: 4-6 (K59-P, K54-P, OR-P) dalej; 8, 9 (O54, O59) -> `pominiete["zla_plytka"]` | klucz nie-liczba -> pominiety bez wpisu |
| A52 | stanowisko/ramka_protokol.py:154-157 | `_plytki` | nazwa (`uklady[str(n)]`) jako klucz kalibracji | `if gn is None:` (wynik `_gniazda(kal, rola, uklady.get(str(n)), ...)`) | uklad bez wpisu kalibracji w tej roli -> `pominiete["brak_kalibracji"]` | brak ukladu / nie-str (:113) -> `brak_kalibracji` |
| A53 | stanowisko/ramka_protokol.py:202 | `plan_rano` | numer (`MAX_PLYTKA`) | `if _int(p) and 1 <= p <= RPR.MAX_PLYTKA and p not in pl:` | numery plytek kuwety 8, 9 pomijane | - |
| A54 | stanowisko/ramka_protokol.py:288 | `sprawdz_stan` | numer (odpowiedz ramki) | `_wymagaj(d.get("plytka") is None or (_int(d["plytka"]) and 0 <= d["plytka"] <= RPR.MAX_PLYTKA), "stan: plytka")` | 0-7 | BladOdpowiedzi |
| A55 | stanowisko/statusy.py:164 | `status_pracy` | status skanu (wynik A10) | `if status_skanu == "plytka_nie_z_trybu":` | - | - |
| A56 | stanowisko/statusy.py:179 | `status_pracy` | numer znany / nieznany | `return "zielony" if numer_znany or ZIELONE_BEZ_NUMERU_PLYTKI else "czeka_na_numer"` | kazda rodzina tak samo | - |
| A57 | stanowisko/statusy.py:507 | (modul) `RAMKA_KTOREJ` | rola | `RAMKA_KTOREJ = {"W": "wieczornej", "P": "porannej"}` | - | brak klucza domyslnego |
| A58 | stanowisko/statusy.py:508-515 | (modul) `RADY_PLYTKA_NIE_Z_RAMKI` | rola / numer drugiej ramki | `# rada wg roli ramki, gdy numer nalezy do DRUGIEJ ramki; None - numer spoza obu ramek (np. 7)` | "W": numer z P (4-6); "P": numer z W (1-3) | None: kazdy inny numer (7, 8, 9) |
| A59 | stanowisko/statusy.py:555 | (modul) `JAKA_PLYTKA` | typ (A07) - slownik nazw | `JAKA_PLYTKA = {"wieczorna": "plytka wieczorna", "poranna": "plytka poranna", None: "plytka o nieznanym ukladzie"}` | wszystkie -W / -P (bez ksztaltu) | klucz None |
| A60 | stanowisko/statusy.py:556 | (modul) `NAZWY_TRYBOW` | tryb | `NAZWY_TRYBOW = {"wieczor": "Wieczor", "rano": "Poranek"}` | - | brak klucza domyslnego |
| A61 | stanowisko/ui/czesci.py:248 | `napis_dopuszczenia` | typ (`Plytka.typ`, Z21) | `return N.PLYTKA_DOPUSZCZONA.format(jaka=ST.JAKA_PLYTKA.get(plytka.typ, ST.JAKA_PLYTKA[None]))` | -W -> "plytka wieczorna", -P -> "plytka poranna" | `JAKA_PLYTKA[None]` |
| A62 | stanowisko/ui/czesci.py:542 | `PasekStanu.ustaw` | tryb | `inny = ST.NAZWY_TRYBOW["wieczor" if stan.tryb == "rano" else "rano"]` | - | tryb inny niz rano -> "Poranek" |
| A63 | stanowisko/ui/czesci.py:604 | `PasekStanu._ustaw_ramki` | rola ramki | `for x in (r.wieczorna, r.poranna):` | - | ramka None pominieta |
| A64 | stanowisko/ui/czesci.py:739-740 | `panel_pytania` | typ (`Plytka.typ`) - slownik nazw | `rada = {"poranna": N.RADA_PLYTKA_PORANNA, "wieczorna": N.RADA_PLYTKA_WIECZORNA}.get(typ_plytki, N.RADA_PLYTKA_NIEZNANA)` | -P -> RADA_PLYTKA_PORANNA; -W -> RADA_PLYTKA_WIECZORNA (bez ksztaltu) | RADA_PLYTKA_NIEZNANA |
| A65 | stanowisko/ui/ekran_rano.py:58 | (modul) `PYTANE` | rodzaj pytania | `PYTANE = {"brak_numeru_plytki": "podaj_numer_plytki", "plytka_nie_z_trybu": "pomin_skan"}` | rano plytka -W -> akcja `pomin_skan` | - |
| A66 | stanowisko/ui/ekran_rano.py:956-957 | `EkranRano._odswiez_uwagi` | nazwa -> `uklad.json` (`numery`) | `numery = tuple(geometria.numery) if geometria is not None and geometria.numery else K.NUMERY_PLYTEK_ZAPASOWE` | przyciski numerow = `plytka_n*.stl` ukladu: K59-P, K54-P, OR-P -> 4, 5, 6; O54-P, O59-P -> 9 | uklad nie do wczytania -> 1..9 (Z22) |
| A67 | stanowisko/ui/ekran_rano.py:963 | `EkranRano._odswiez_uwagi` | typ (A64) | `budowa.append(lambda q=q, p=p, nazwa=nazwa: panel_pytania(q, stan, p.typ if p is not None else None, nazwa, r))` | jak A64 | jak A64 |
| A68 | stanowisko/ui/okno.py:318 | `OknoWieczor.pokaz_stan` | tryb | `rano = stan.tryb == K.TRYB_RANO` | - | inny tryb -> strona wieczorna |
| A69 | stanowisko/ui/okno.py:753 | `OknoWieczor._odswiez_naglowek` | rodzaj pytania | `pytane = {"brak_numeru_plytki": "podaj_numer_plytki", "plytka_nie_z_trybu": "dopusc_plytke"}` | wieczorem plytka -P -> akcja `dopusc_plytke` | - |
| A70 | stanowisko/ui/okno.py:847-848 | `OknoWieczor._odswiez_uwagi` | nazwa -> `uklad.json` (`numery`) | `numery = tuple(geometria.numery) if geometria is not None and geometria.numery else K.NUMERY_PLYTEK_ZAPASOWE` | K59-W, K54-W, OR-W -> 1, 2, 3; O54-W, O59-W -> 8 | uklad nie do wczytania -> 1..9 (Z22) |
| A71 | stanowisko/ui/okno.py:851 | `OknoWieczor._odswiez_uwagi` | typ (A64) | `budowa += [lambda q=q: panel_pytania(q, stan, plytka.typ, ...) for q in pytania]` | jak A64 | jak A64 |
| A72 | stanowisko/ui/mapa.py:78 | `sciecie_mm` | pole `shape` / `d` | `if uk is None or getattr(uk, "shape", None) != "round" or not getattr(uk, "d", None):` | K59, K54 -> None; O54, O59, OR -> cieciwa z `flat` | uk None -> None |
| A73 | stanowisko/ui/mapa.py:228 | `MapaPlytki._przelicz` | numery gniazd vs `uklad.sockets` | `if uk is None or not set(numery) <= znane:` | wszystkie rodziny: id gniazd w ukladzie -> mapa wg geometrii | uklad None albo id spoza ukladu -> kratka (B04) |
| A74 | stanowisko/ui/mapa.py:231 | `MapaPlytki._przelicz` | pole `shape` | `pol = (uk.d if uk.shape == "round" else uk.size) / 2` | O54, O59, OR -> d = 100; K -> size = 96 | inny ksztalt -> size |
| A75 | stanowisko/ui/mapa.py:255 | `MapaPlytki._obrys_ukladu` | pole `shape` | `if uk.shape != "round":` | K -> prostokat z wycieciem `notch`; O54, O59, OR -> luk + cieciwa (:263-277) | okragla bez `flat` -> elipsa (:264-266) |
| A76 | stanowisko/ui/mapa.py:345 | `MapaPlytki._rysuj_plytke` | pole `shape` + obecnosc `flat` | `if ksztalt == "round" and self._sciecie is None:  # kolo bez pola flat w ukladzie: jak przed E3-O3` | okragla bez `flat` -> elipsa; reszta -> sciezka obrysu | - |
| A77 | ramka/kalibracja.py:42 | (modul) `ROLE_UKLADOW` | pole `plate` z uklad.json - slownik nazw | `ROLE_UKLADOW = {"wieczorna": "W", "poranna": "P"}  # pole "plate" w uklad.json -> ramka (plytki kwadratowe)` | K59 i K54 (wspolne `plate`) | - |
| A78 | ramka/kalibracja.py:44 | (modul) `ROLE_UKLADOW_RAMKOWYCH` | pole `plate` - slownik nazw | `ROLE_UKLADOW_RAMKOWYCH = {"okragla_ramkowa_wieczorna": "W", "okragla_ramkowa_poranna": "P"}` | OR | O54 / O59 (`plate` okragla_wieczorna / okragla_poranna) - brak klucza |
| A79 | ramka/kalibracja.py:82-87 | `rola_ukladu` | pole `shape` + pole `plate` | `ksztalt = uklad.get("shape", "square")` / `if ksztalt == "square":` / `if ksztalt == "round":` | K59, K54 (K54 bez klucza `shape` = square) -> W / P; OR -> W / P; O54, O59 -> None | inny `shape` -> None |
| A80 | ramka/kalibracja.py:96-99 | `domyslna` | wynik A79 | `if rola is None:` | wpisy startowe: W: wieczorna, wieczorna_r54, okragla_ramkowa_wieczorna; P: poranna, poranna_r54, okragla_ramkowa_poranna (klucz = nazwa katalogu) | O54, O59 bez wpisu |
| A81 | ramka/kalibracja.py:188 | `uzupelnij` | nazwa (klucz wpisu) | `if nazwa not in dane["ramki"].get(rola, {}):` | dopisuje brakujace (np. OR w pliku sprzed E3-O2) | - |
| A82 | ramka/protokol.py:41 | (modul) `RODZINY` | numer wg roli | `RODZINY = {"W": (1, 2, 3), "P": (4, 5, 6)}  # numery plytek ramki (plan_ramki_v2 D11)` | W: K59-W, K54-W, OR-W; P: K59-P, K54-P, OR-P | O54, O59 (8, 9) - w zadnej |
| A83 | ramka/protokol.py:190 | `_numer_plytki` | numer | `if not (1 <= n <= MAX_PLYTKA):` | 8, 9 -> 400 `zla_plytka` | - |
| A84 | ramka/protokol.py:259-260 | `sprawdz_plan` | tryb planu vs rola | `if tryb != TRYB_ROLI[rola]:` | - | 409 `plan_innej_ramki` |
| A85 | ramka/protokol.py:266, 277-278 | `sprawdz_plan` | numer vs rodzina ramki | `if n not in rodzina:` | W: 1-3, P: 4-6 | 400 `zla_plytka` |
| A86 | ramka/logika.py:50 | `LogikaRamki.__init__` | rola -> rodzina | `self.rodzina = tuple(rodzina) if rodzina else protokol.RODZINY[rola]` | - | pole `rodzina` z konfiguracji ramki nadpisuje |
| A87 | ramka/logika.py:368 | `LogikaRamki.ustaw_plytke` | rola | `if protokol.KASUJ_PO_ZDJECIU_ROLI[self.rola] and self.plan is not None and stara in self.plan.plytki:` | - (W kasuje wynik po zdjeciu, P nie) | - |
| A88 | ramka/logika.py:561, 570-572 | `LogikaRamki.obraz` | numer z czujnikow vs plan | `ma_plan_plytki = wazny and p in self.plan.plytki` | ramka nie zna ukladu: plytka K i OR o tym samym numerze nieodroznialne | numer spoza planu -> napis "<n> BRAK" |
| A89 | ramka/logika.py:580 | `LogikaRamki.obraz` | rola | `if self.rola == "W" or g.kuweta is None or \` | W: wszystkie gniazda planu; P: regula kuwet | - |
| A90 | ramka/logika.py:403, 435, 584 | `biezaca_kuweta`, `klawisz`, `obraz` | rola | np. :435 `if self.rola != "P" or k not in protokol.KLAWISZE:` | klawiatura i kuwety tylko P | - |
| A91 | ramka/sprzet_rpi.py:123-128 | `SprzetRpi.odczytaj_plytke` | numer (3 czujniki Halla) | `if c.is_active:` (bit i = czujnik i z `piny_halla`) | numer 0..7; plytki 8, 9 nie do odczytania | - |
| A92 | ramka/sprzet_rpi.py:116 | `SprzetRpi.__init__` | rola | `z_klawiatura = rola == "P"` | - | - |
| A93 | ramka/program.py:280-282 | `ProgramRamki.atrapa_plytka` | numer | `if not isinstance(dane, dict) or set(dane) != {"plytka"} or dane["plytka"] not in range(8) \` | 0..7 | 400 `zle_pole` |
| A94 | ramka/sprzet_atrapa.py:38 | `SprzetAtrapa.poloz_plytke` | numer | `if not (0 <= int(n) <= 7):` | 0..7 | ValueError |
| A95 | ramka/test_led.py:28, 103-105 | `_bloki` / `main` | nazwa (klucz kalibracji) | `gn = kal["ramki"][rola][uklad]["gniazda"]` | uklady z wpisem w danej roli | KeyError -> "brak ukladu w kalibracji tej ramki", kod 1 |

Pliki z zakresu bez zadnego rozroznienia rodziny plytki / wieczor-ranek (przeczytane w calosci): `stanowisko/excel.py`
(`excel.py:485` `kuweta.startswith(N.PRYWATNE)` dotyczy prefiksu `#` kuwety), `stanowisko/excel_com.py`, `stanowisko/ui/okno_excela.py`,
`stanowisko/ui/kandydaci.py`, `stanowisko/ui/napisy.py` i `ui/napisy_rano.py` (tylko teksty, np. `napisy.py:147-149` RADA_PLYTKA_*
wybierane w A64), `stanowisko/ui/obraz.py` (`obraz.py:35` `P.shape` = ksztalt tablicy numpy), `stanowisko/ui/styl.py`,
`stanowisko/ui/__init__.py`, `stanowisko/ui/mapa_rano.py`, `ramka/serwer.py` (`serwer.py:186` `startswith("/atrapa/")` = sciezka URL),
`ramka/obraz.py`, `ramka/czcionka.py`, `ramka/sprzet.py`, `ramka/__init__.py`, `ramka/__main__.py`.
Rozroznienia samego trybu programu w session.py bez zwiazku z plytka (pominiete w tabeli): :395, :895-896, :1054, :1073, :1144, :1231, :1279.

---

## Tabela B - przeliczenia numer gniazda -> pozycja mapy / dioda / komorka

| nr | plik:linia | funkcja | wejscie | wyjscie | skad geometria | uklady okragle |
|---|---|---|---|---|---|---|
| B01 | stanowisko/ui/mapa.py:43-70 | `geometria_ukladu` | nazwa ukladu (`plytka.uklad`) | `UkladPlytki` (gniazda, ksztalt, numery) albo None | uklad.json z katalogu `[plytki]` (`UST.katalog_plytki`, :59-62) albo `KATALOG_MODELI/nazwa`; pamiec `_GEOMETRIE`, ponowienie po 60 s (:38) | TAK (wszystkie rodziny, bez galezi) |
| B02 | stanowisko/ui/mapa.py:231-237 | `MapaPlytki._przelicz` (`px`) | x, y w mm ukladu | punkt ekranu `QPointF(cx + x * s, cy - y * s)` (y "do tylu" = w gore, przod plytki na dole) | polowa `d` (round) albo `size` (square) z uklad.json; stale `MARGINES_PX = 14`, `MIEJSCE_NA_PODPIS_PX = 26` (:33-34) | TAK (`d = 100`) |
| B03 | stanowisko/ui/mapa.py:241-248 | `MapaPlytki._przelicz` | numer gniazda (`g.id in numery`) | sciezka `g.obrys(64)`, srodek `px(g.x, g.y)`, promien `g.promien_gorny * s`, szerokosc `(g.d_top if g.okragle else g.l) * s` | uklad.json `sockets` przez `uklad.Gniazdo.obrys` (uklad.py:104-117) | TAK |
| B04 | stanowisko/ui/mapa.py:228-230, 279-289 | `_przelicz` / `_kratka` | numery gniazd w kolejnosci stanu | kola w kratce: kolumna `i % KOLUMN_KRATKI`, wiersz `i // KOLUMN_KRATKI` | stala `KOLUMN_KRATKI = 5` (:35) | niezalezne od ksztaltu (zastepcze, gdy brak ukladu albo id spoza ukladu) |
| B05 | stanowisko/ui/mapa.py:73-89, 251-277 | `sciecie_mm` / `_obrys_ukladu` | `shape`, `d`, `flat.angle_deg`, `flat.dist`, `notch` | obrys plytki na ekranie, konce cieciwy sciecia | uklad.json (`flat`, `notch`, `d` / `size`); stala `ODCINKOW_LUKU = 360` (:36) | TAK (O54, O59, OR maja ten sam `flat`) |
| B06 | stanowisko/ui/mapa.py:405-415 | `MapaPlytki.gniazdo_w_punkcie` | punkt ekranu | numer gniazda (wewnatrz sciezki albo do 8 px od obrysu) | ksztalty z B03 / B04 | TAK |
| B07 | stanowisko/ui/mapa.py:150-171 | `MapaPlytki.sasiad` | numer gniazda + kierunek strzalki | numer najblizszego gniazda w kierunku na ekranie | srodki z B03 / B04 | TAK |
| B08 | stanowisko/ui/mapa.py:189-195 | `srodek_gniazda`, `punkt_probny` | numer gniazda | punkt ekranu | B03 / B04 | TAK |
| B09 | stanowisko/ui/mapa_rano.py:45-49, 58-110, 191-196 | `MapaRano.ustaw_rano`, `_plan`, `punkt_probny` | numer gniazda | rozklad napisow w gniezdzie (nr, kuweta, zab, miniatura); rynienka gdy `szer > 3 * promien` (:67, :194) | dziedziczy B01-B03; progi `PROG_MINIATURY_PX = 25.0`, `PROG_ZEBA_PX = 16.0` (:20-21) | TAK (brak galezi ksztaltu plytki) |
| B10 | stanowisko/ui/okno.py:682, 686 | `OknoWieczor._odswiez` | `plytka.uklad`, `plytka.gniazda`, wybrane gniazdo | `self.mapa.ustaw(plytka, geometria, self._gniazdo)` | B01 | TAK |
| B11 | stanowisko/ui/ekran_rano.py:758, 763 | `EkranRano._odswiez_karty` | `p.uklad`, gniazda, `obwodka` | `karta.mapa.ustaw_rano(p, geometria, wybrane, rano.obwodka(p.skan_id), self._obrazy)` | B01 | TAK |
| B12 | stanowisko/ui/ekran_rano.py:678, 742-746 | `_plytki_widoczne`, `_odswiez_karty` | numer PLYTKI (nie gniazda) | komorka siatki kart (`i // kolumn`, `i % kolumn`), sortowanie po numerze | stala `KOLUMN_PLYTEK = 3` (:48) | niezalezne od rodziny |
| B13 | stanowisko/ui/obraz.py:87-88, 119 | `_Zadanie.run`, `WczytywaczObrazow.zlec` | numer gniazda | klucz w pliku podgladu (punkty + odchylki pracy), obraz skalowany do punktow pracy | plik `*_podglad.npz` (nie uklad.json) | TAK (niezalezne od ksztaltu) |
| B14 | stanowisko/ui/czesci.py:1357-1362 | `ListaDofrezowania.ustaw` | numer plytki, numer gniazda | tekst w kolumnach 4 i 5 tabeli ekranu (wiersz = kolejnosc listy) | brak geometrii | bez nazwy ukladu |
| B15 | stanowisko/session_rano.py:1314-1341 | `SesjaRano.plan_plytek` | numer plytki + `p["gniazdo"]` prac | `plytki[str(n)]["gniazda"] = [{"id", "kolor", ["kuweta"]}]`, `uklady[str(n)] = s["uklad"]` (bez px) | brak geometrii (id przekazane bez zmian) | tylko niektore: K59-P, K54-P, OR-P; O54-P, O59-P -> `poza_ramka` (A39) |
| B16 | stanowisko/indicate.py:489 | `KlientRamki.wynik` | `{gniazdo: kolor}` + uklad (ramka W) | `{int(g): c ...}` zapamietane z ukladem | brak geometrii | TAK (bez galezi) |
| B17 | stanowisko/indicate.py:505-512 | `KlientRamki._sprawdz_wynik` | uklad + numery gniazd | czy kazde swiecace gniazdo ma blok | kalibracja `kal["ramki"]["W"][uklad]["gniazda"]` | tylko niektore: OR-W (oraz K59-W, K54-W); O54-W / O59-W odpadaja wczesniej (A44) |
| B18 | stanowisko/indicate.py:1027-1029, 1035-1037 | `KlientRamki._zbuduj_plan` | plan plytek (P) / wazne wyniki (W) | tresc planu z px (`RP.plan_rano`, `RP.plan_wieczor`) | kalibracja | jak B20 |
| B19 | stanowisko/indicate.py:1195-1212, 1287-1290 | `wczytaj_kalibracje`, `Indicate.z_ustawien` | `[sciezki] kalibracja_ramek` + `korzen / "modele_plytek"` | kalibracja (plik albo startowa z geometrii, uzupelniona o brakujace uklady) | plik `dane/kalibracja_ramek.json` albo uklad.json z katalogu `modele_plytek` programu (nie z `[plytki]`) | tylko niektore: OR tak, O54 / O59 nie (A79) |
| B20 | stanowisko/ramka_protokol.py:91-95, 110-139 | `_blok`, `_gniazda` | lista `{id, kolor[, kuweta]}` + uklad + rola | lista `{id, px: [x, y, w, h], kolor[, kuweta]}` posortowana po id; id spoza 1..64 -> `zle_gniazdo` (:117); brak bloku -> None (cala plytka) | kalibracja przez `KAL.blok` | tylko uklady z wpisem w danej roli |
| B21 | stanowisko/ramka_protokol.py:142-162 | `_plytki` | `{numer: gniazda}` + `uklady` | `plytki` planu | stala `RODZINY` + kalibracja | OR tak; O54, O59 -> `zla_plytka` (A51) |
| B22 | stanowisko/ramka_protokol.py:182-227, 230-242 | `plan_rano`, `plan_wieczor` | plan plytek (P) / wyniki (W) | tresc `PUT /plan`, sprawdzona kodem ramki (`sprawdz_plan`) | jak B20 / B21 | jak B21 |
| B23 | ramka/kalibracja.py:56-60 | `blok_z_mm` | x_mm, y_mm, w, h | `[kol, wiersz, w, h]`: kol = 32 + x / 2.5, wiersz = 32 - y / 2.5, zaokraglenie do piksela | stale `obraz.SZEROKOSC`, `obraz.WYSOKOSC`, `obraz.RASTER_MM` | TAK |
| B24 | ramka/kalibracja.py:63-76 | `domyslna_dla_ukladu` | `sockets` z uklad.json | `{"id": [x, y, w, h]}`; okragle 3 x 3 (`BOK_GNIAZDA`); rynienka: dlugosc `ceil(((hole_count - 1) * hole_pitch + hole_d) / 2.5)` x 3, poziomo gdy kat < 45 albo > 135 (:72) | uklad.json + stale :46-47 | TAK (bloki OR = bloki K59, bo gniazda identyczne) |
| B25 | ramka/kalibracja.py:90-104 | `domyslna` | katalog modeli | `{"W": {katalog: wpis}, "P": {...}}` | wszystkie `*/uklad.json`; klucz wpisu = nazwa katalogu (`plik.parent.name`, :99) | tylko niektore: OR; O54, O59 pominiete (A79) |
| B26 | ramka/kalibracja.py:231-233 | `blok` | (kal, rola, uklad, gniazdo) | `[x, y, w, h]` | plik kalibracji (`kal["ramki"][rola][uklad]["gniazda"][str(int(gniazdo))]`) | wg wpisow pliku |
| B27 | ramka/kalibracja.py:236-245 | `gniazda_planu` | `{id: {kolor, kuweta}}` | lista gniazd planu z px | plik kalibracji | wg wpisow pliku |
| B28 | ramka/protokol.py:201-240 | `_sprawdz_gniazda` | gniazda planu | walidacja: id 1..64, px w `OBSZAR_PLYTKI`, max 48 gniazd, max 800 pikseli, bez nakladania | stale :60-63, `obraz.OBSZAR_PLYTKI` | ramka nie zna ukladow (ramka/__init__.py:5, README.md:126-127) |
| B29 | ramka/logika.py:578-583 | `LogikaRamki.obraz` | `plan.plytki[p].gniazda` (px) dla numeru p z czujnikow | piksele klatki 64 x 64 (`k.blok(x, y, w, h, ...)`) | px z planu laptopa | ramka nie rozroznia ukladu (README.md:403-404) |
| B30 | ramka/obraz.py:73-78, 84-87 | `Klatka.ustaw`, `Klatka.blok` | (x, y) | indeks bufora `(y * 64 + x) * 3` | stale :14-15 | - |
| B31 | ramka/sprzet_rpi.py:58-71, 194-201 | `przeksztalc`, `SprzetRpi.pokaz` | (x, y) klatki | (px, py) panelu: najpierw odbicie (lustro), potem obrot 0 / 90 / 180 / 270 | konfiguracja ramki (`obrot`, `lustro`: program.py:48-49) | - |
| B32 | ramka/test_led.py:27-55 | `_bloki`, `klatka_gniazda`, `klatka_wszystkich`, `uruchom_test` | kal + rola + uklad | klatki testowe kazdego gniazda (blok + numer gniazda na marginesie) | plik kalibracji | tylko uklady z wpisem (README.md:419-420: OR-W 19, OR-P 24 gniazd) |
| B33 | stanowisko/excel.py:353, 358 | `IndeksArkusza.z_wartosci` | wiersze arkusza w kolejnosci odczytu | `nr = konf.pierwszy_wiersz + i`; kolumny A/B/C/H z ustawien (`numer_kolumny`) | ustawienia `[excel]` | gniazdo / plytka / uklad nie wystepuja |
| B34 | stanowisko/excel.py:334, 429 | `IndeksArkusza.__init__`, `dopasuj` | kuweta, folder zlecenia | wiersz arkusza (indeks kuweta -> wiersze; reguly kuweta / `#` prywatne / nazwa folderu / data) | arkusz + ustawienia | jw. |
| B35 | stanowisko/excel.py:593, 879; stanowisko/excel_com.py:139-142 | `Excel.__init__`, `Excel.zatwierdz`, `ustaw_wypelnienie` | nr wiersza + `kolumna_odhaczenia` | `Cells(nr, kolumna).Interior.Color` | ustawienia `[excel]` | jw. |
| B36 | stanowisko/session.py:1272-1276 | `Sesja.zapisz_do_dofrezowania` | `numer_plytki`, `gniazdo` | kolumny "plytka", "gniazdo" pliku CSV (`KOLUMNY_LISTY`, :108) - nie Excel | brak geometrii | bez nazwy ukladu (K n1 i OR n1 nieodroznialne) |

Uwagi do B: numer gniazda pokazywany wylacznie jako tekst (bez pozycji) - ui/czesci.py:1231, ui/kandydaci.py:176 i :222.
Przeliczenia gniazdo -> wiersz / kolumna Excela: brak w calym zakresie (Excel dobiera wiersz po kuwecie i folderze, B33-B35).

---

## Tabela C - porownanie uklad.json ukladow okraglych

Kolumny: R54-W = `okragla_wieczorna_r54`, R59-W = `okragla_wieczorna`, OR-W = `okragla_ramkowa_wieczorna`,
R54-P = `okragla_poranna_r54`, R59-P = `okragla_poranna`, OR-P = `okragla_ramkowa_poranna` (pliki `modele_plytek/<katalog>/uklad.json`).

| nr | cecha (linie) | R54-W | R59-W | OR-W | R54-P | R59-P | OR-P |
|---|---|---|---|---|---|---|---|
| C01 | `plate` (:2) | okragla_wieczorna | okragla_wieczorna | okragla_ramkowa_wieczorna | okragla_poranna | okragla_poranna | okragla_ramkowa_poranna |
| C02 | `version`, `units`, `thickness` (:3, :4, :11) | v2, mm, 8 | v2, mm, 8 | v2, mm, 8 | v2, mm, 8 | v2, mm, 8 | v2, mm, 8 |
| C03 | `shape`, `size`, `d` (:65-67) | round, 100.0, 100.0 | jw. | jw. | jw. | jw. | jw. |
| C04 | `flat` - sciecie (:68-74) | corner D, angle_deg -45.0, chord_w 16, dist 49.3559 | jw. | jw. | jw. | jw. | jw. |
| C05 | obrot / odbicie lustrzane | brak pol; jedyne katy: `flat.angle_deg` -45, `angle` rynienek 0 | jw. | jw. + `magnet_pockets[].angle_deg` 225 / 135 / 45, `key_slot.angle_deg` -45 | jw. | jw. | jw. + jak OR-W |
| C06 | `sockets` (linie) | :82-289 | :82-276 | :120-314 | :82-419 | :82-326 | :120-364 |
| C07 | liczba gniazd (okragle + rynienki) | 20 (18 + 2) | 19 (18 + 1) | 19 (18 + 1) | 33 (31 + 2) | 24 (23 + 1) | 24 (23 + 1) |
| C08 | numeracja | 1..20 ciagla | 1..19 ciagla | 1..19 ciagla | 1..33 ciagla | 1..24 ciagla | 1..24 ciagla |
| C09 | kolejnosc numerow | rzedami od przodu (y < 0) do tylu, w rzedzie od +x do -x | jw. | jw. | jw. | jw. (17 = (0, 8.75) po rzedzie 13-16 y = 8; 18-19 y = 22.85 przed 20-21 y = 23.6) | jak R59-P |
| C10 | rynienki (id: y; l x w; hole_pitch, hole_count) | 1: -31.5; 20: +31.5; 60 x 15; 12, 4 | 1: -30.2; 60 x 15; 12, 4 | jak R59-W | 4: -28; 33: +35.95; 50 x 13; 10, 4 | 1: -35.3; 50 x 13; 10, 4 | jak R59-P |
| C11 | gniazda okragle (id: d_top) | 2-7: 12; 8-14: 9; 15-19: 15 | 2-7: 12; 8-19: 15 | jak R59-W | 1-3: 7.5; 5-11: 10; 12-17: 12.5; 18-32: 7.5 | 2-16: 12.5; 17-19: 15; 20-24: 12.5 | jak R59-P |
| C12 | gniazda identyczne z (porownanie pole po polu) | wieczorna_r54 | wieczorna, okragla_ramkowa_wieczorna | wieczorna, okragla_wieczorna | poranna_r54 | poranna, okragla_ramkowa_poranna | poranna, okragla_poranna |
| C13 | `markers` A, B, C (:12-34; d 5, depth 3) | A(-35.5,-26.5) B(-35.5,26.5) C(35.5,26.5) | A(-35.5,-26.5) B(-31.0,31.5) C(42.0,14.5) | jak R59-W | A(-34.5,-28.0) B(-30.0,32.5) C(30.0,32.5) | A(-30.5,-32.0) B(-37.5,23.5) C(41.5,16.0) | jak R59-P |
| C14 | `code_dimples` A-D (:35-64; d 2, depth 1) | A(-4.5,-43.5) B(-1.5,-43.5) C(1.5,-43.5) D(4.5,-43.5) | jak R54-W | jak R54-W | A(30.5,-31.0) B(30.5,-28.0) C(30.5,-25.0) D(30.5,-22.0) | A(36.5,18.5) B(36.5,21.5) C(43.0,6.0) D(43.0,9.0) | jak R59-P |
| C15 | `magnet_pockets` | [] (:75) | [] (:75) | A 225 deg (-31.8198,-31.8198), B 135 deg (-31.8198,31.8198), C 45 deg (31.8198,31.8198); d 5.2, depth 2.2 (:75-100) | [] (:75) | [] (:75) | jak OR-W (:75-100) |
| C16 | `number_relief` x, y (text_h 5, relief_h 0.6) | (35.0, -26.5) (:76-81) | (35.0, -26.5) (:76-81) | (35.0, -26.5) (:101-106) | (36.5, -24.5) (:76-81) | (-44.0, 5.5) (:76-81) | (-44.0, 5.5) (:101-106) |
| C17 | `cover_groove` | brak | brak | z 2, w 1.0, depth 0.8 (:107-112) | brak | brak | jak OR-W (:107-112) |
| C18 | `key_slot` | brak | brak | angle_deg -45.0, r0 46.0, w 3.6, h 5.0 (:113-119) | brak | brak | jak OR-W (:113-119) |
| C19 | `leds` | {} (:290) | {} (:277) | {} (:315) | {} (:420) | {} (:327) | {} (:365) |
| C20 | numery plytek (STL) | n8 | n8 | n1, n2, n3 | n9 | n9 | n4, n5, n6 |
| C21 | `plytka_bazowa.stl` | jest | jest | jest | jest | jest | jest |

Roznice miedzy R54, R59 i ramkowa (kazda z osobna):
1. `plate`: R54 i R59 maja ten sam `plate` (`okragla_wieczorna` / `okragla_poranna`); OR ma `plate` = nazwa ukladu (C01). `ramka/kalibracja.py:79-87` dobiera role ramki po `plate` i `shape`.
2. Gniazda wieczorne: R54 20 gniazd (2 rynienki: id 1 i 20; 7 gniazd d 9) vs R59 i OR 19 gniazd (1 rynienka id 1; brak d 9; 12 gniazd d 15) (C07, C10, C11).
3. Gniazda poranne: R54 33 gniazda (2 rynienki: id 4 i 33; gniazda d 7.5 i d 10) vs R59 i OR 24 gniazda (1 rynienka id 1; d 12.5 i d 15) (C07, C10, C11).
4. Polozenia rzedow gniazd: R54-W rzedy y = -15 / -1.5 / 13.5 vs R59-W / OR-W y = -13.7 / 2.75 / 18.35 / 33.95; R54-P y = -41.25 / -13.5 / 0.75 / 13.6 / 22.7 vs R59-P / OR-P y = -19.55 / -6.1 / 8 / 8.75 / 22.85 / 23.6 / 37.05.
5. Znaczniki wieczorne: B i C rozne (R54 B(-35.5,26.5) C(35.5,26.5) vs R59 / OR B(-31.0,31.5) C(42.0,14.5)); A wspolny (C13).
6. Znaczniki poranne: wszystkie trzy rozne R54 vs R59 / OR (C13).
7. Dolki kodu wieczorne: identyczne w R54, R59 i OR (C14).
8. Dolki kodu poranne: R54 w kolumnie x = 30.5, y -31..-22 vs R59 / OR dwie pary przy x = 36.5 i x = 43.0 (C14).
9. `number_relief` poranny: R54 (36.5, -24.5) vs R59 / OR (-44.0, 5.5); wieczorny wspolny (35.0, -26.5) (C16).
10. `magnet_pockets`: tylko OR (3 gniazda magnesow na promieniu 45 mm); R54 i R59 puste (C15). Dla porownania kwadrat: `modele_plytek/wieczorna/uklad.json:74-96` magnesy (-42,-42) (-42,42) (42,42), ta sama srednica 5.2 i glebokosc 2.2, bez `angle_deg`.
11. `cover_groove` i `key_slot`: tylko OR (C17, C18); `key_slot.angle_deg` -45 = kierunek `flat`.
12. Numery plytek: R54 i R59 n8 / n9; OR n1-n3 / n4-n6 (C20).
13. OR vs R59 (ta sama pora): identyczne `sockets`, `markers`, `code_dimples`, `number_relief`, `flat`; roznia sie tylko `plate`, `magnet_pockets`, `cover_groove`, `key_slot`, numery STL (oraz przesuniecie linii pliku o 38).
14. Wspolne dla wszystkich szesciu: `shape` round, `size` / `d` 100, `thickness` 8, `flat` identyczny, `version` v2, `leds` {}, `coords` (:5-10), `depth` 4 i `hole_d` 3 kazdego gniazda.

Wieczorna vs poranna: poranna NIE jest odbiciem wieczornej - rozna liczba gniazd (20 / 33, 19 / 24), rozne srednice i rynienki
(W: 60 x 15, rozstaw otworow 12; P: 50 x 13, rozstaw 10), znaczniki nie sa lustrzane (np. R59: W C(42.0,14.5), P C(41.5,16.0) - oba po +x),
`flat` identyczny (-45 deg) w W i P, dolki kodu w innych miejscach; w zadnym pliku nie ma pola obrotu ani odbicia.

---

## Tabela D - stale liczbowe (gniazda, diody, numery plytek)

| nr | plik:linia | stala / wartosc | znaczenie | spojnosc z uklad.json / STL |
|---|---|---|---|---|
| D01 | stanowisko/session.py:131 | `NUMERY_RAMKOWE` W (1, 2, 3), P (4, 5, 6) | numery plytek OR | spojne: okragla_ramkowa_wieczorna n1-n3, okragla_ramkowa_poranna n4-n6 |
| D02 | stanowisko/session_rano.py:84 | `NUMERY_PLYTEK_PORANNYCH = (4, 5, 6)` | numery K59-P i K54-P | spojne: poranna, poranna_r54 n4-n6 |
| D03 | stanowisko/session_rano.py:85 | `NUMERY_PLYTEK_OKRAGLYCH_PORANNYCH = (9,)` | numery O54-P i O59-P | spojne: okragla_poranna, okragla_poranna_r54 n9 |
| D04 | stanowisko/session.py:853 | `if n < 1:` | numer reczny wieczorem: tylko dolna granica | brak gornej granicy i brak listy wg ukladu (por. D01-D03) |
| D05 | ramka/protokol.py:41 | `RODZINY = {"W": (1, 2, 3), "P": (4, 5, 6)}` | numery plytek ramek | spojne z K59, K54, OR; kopie: stanowisko/ramka_protokol.py:30; komentarz ramka/program.py:44; README.md:52, :117 |
| D06 | ramka/protokol.py:59 | `MAX_PLYTKA = 7` | najwiekszy numer plytki w protokole | = 3 bity czujnikow Halla (ramka/sprzet.py:21 "n = A + 2B + 4C"); uzycie: protokol.py:190, :271, :293, :308; ramka_protokol.py:202, :288; README.md:81 "(0-7)"; plytki n8, n9 poza zakresem |
| D07 | ramka/protokol.py:60 | `MAX_ID_GNIAZDA = 64` | najwiekszy id gniazda | spojne: najwiekszy id w uklad.json = 33 (poranna_r54, okragla_poranna_r54); takze ramka/kalibracja.py:145-146 (1..64), README.md:118 |
| D08 | ramka/protokol.py:61 | `MAX_GNIAZD_PLYTKI = 48` | najwiecej gniazd w planie plytki | spojne: najwiecej gniazd = 33; README.md:118 |
| D09 | ramka/protokol.py:62 | `MAX_PIKSELI_PLYTKI = 800` | najwiecej pikseli na plytke | spojne: bloki startowe (B24) najwiecej 363 px (poranna_r54: 31 x 9 + 2 x 42) |
| D10 | ramka/protokol.py:63 | `MAX_BOK_BLOKU = 24` | najdluzszy bok bloku | spojne: najdluzszy blok startowy 16 px (rynienka W: (3 x 12 + 3) / 2.5 -> 16); takze ramka/kalibracja.py:151 (1..24) |
| D11 | ramka/obraz.py:14-17 | `SZEROKOSC = 64`, `WYSOKOSC = 64`, `RASTER_MM = 2.5`, `OBSZAR_PLYTKI = (12, 12, 40, 40)` | matryca i obszar plytki (40 px = 100 mm) | uklady okragle `d` 100 = dokladnie 40 px; kwadrat `size` 96 = 38.4 px; komentarz :5-6 opisuje tylko plytke 96 mm (38,7 px, kolumny 12..51) |
| D12 | ramka/kalibracja.py:46-47 | `BOK_GNIAZDA = 3`, `WYSOKOSC_RYNIENKI = 3` | blok pod gniazdem okraglym 3 x 3 px (7.5 mm), wysokosc pasa rynienki | gniazda okragle d_top 7.5-15 mm |
| D13 | ramka/kalibracja.py:10, 121 | matryca 64 x 64, raster 2,5 mm | format pliku kalibracji | spojne z D11 |
| D14 | ramka/sprzet_rpi.py:75; ramka/program.py:46 | `piny_halla=(19, 25, 8)` | 3 czujniki Halla (A, B, C) | 3 gniazda magnesow A, B, C w K i OR (uklad.json `magnet_pockets`); dolki kodu w uklad.json maja 4 bity (A-D) w K59, O54, O59, OR i 3 bity w K54 (inny nosnik numeru - skan) |
| D15 | ramka/program.py:280-282; ramka/sprzet_atrapa.py:38 | `range(8)`, `0 <= int(n) <= 7` | numer plytki atrapy 0..7 | spojne z D06 |
| D16 | ramka/obraz.py:155-157 | `list(numery)[:4]`, `str(num)[:1]` | prawy margines: najwyzej 4 numery plytek, 1 cyfra | numery plytek ramek 1-7 - jednocyfrowe |
| D17 | ramka_protokol.py:103; ramka/protokol.py:184 | `len(klucz) <= 2` | klucz numeru plytki najwyzej 2 cyfry | - |
| D18 | (poza zakresem, uzyte w zakresie) stanowisko/kontroler_api.py:131 | `NUMERY_PLYTEK_ZAPASOWE = tuple(range(1, 10))` | przyciski numerow, gdy ukladu nie da sie wczytac (ui/okno.py:848, ui/ekran_rano.py:957) | zawiera 7 - zaden katalog nie ma `plytka_n7.stl` |
| D19 | stanowisko/ui/ekran_rano.py:48 | `KOLUMN_PLYTEK = 3` | karty plytek w rzedzie siatki rano | niezwiazane z uklad.json |
| D20 | stanowisko/ui/mapa.py:35 | `KOLUMN_KRATKI = 5` | kratka zastepcza gniazd | niezwiazane z uklad.json |
| D21 | stanowisko/statusy.py:508 | komentarz "np. 7" | przyklad numeru spoza obu ramek | 8 i 9 tez spoza obu ramek (D05) |
| D22 | stanowisko/statusy.py:574, 577 | "z 3 znacznikow" | liczba znacznikow plytki w komunikacie | spojne: 3 `markers` w kazdym uklad.json |
| D23 | ustawienia.przyklad.toml:23-24 | "wieczorna 18 + 1 rynienka, poranna 23 + 1", "R54 (18 + 2 i 31 + 2)", "n1-n6, n8, n9" | liczby gniazd i numery | spojne z Tabela Z-ukl |
| D24 | ramka/README.md:406, 419-420 | "19 z 19 i 24 z 24 gniazd", "(19 gniazd)", "(24 gniazda)" | bloki OR = bloki kwadratu | spojne (C12) |
| D25 | stanowisko/ui/napisy_rano.py:119 | `NIEROZSTRZYGNIETYCH_W_NAPISIE = 8` | liczba pozycji w napisie listy (nie numer plytki) | - |
| D26 | stanowisko/uklad.py:306 | `1 <= n < 2**liczba_bitow` | zakres numerow z nazw plikow STL | 3 bity: 1..7 (K54), 4 bity: 1..15 (pozostale) |

---

## Niespojnosci (fakty, plik:linia po obu stronach)

1. Dwie funkcje `typ_plytki` o roznym wyniku dla tej samej nazwy: `stanowisko/uklad.py:32-38` (`okragla_poranna_r54` -> `okragla_poranna`,
   usuwa tylko przyrostek wersji) vs `stanowisko/session.py:158-161` (`okragla_poranna_r54` -> `poranna`). Ekran (ui/czesci.py:248, :740)
   dostaje wynik wersji z session (kontroler_api.py:1802, :3210).
2. Kontrola numeru plytki zalezy od sciezki wejscia: wieczorem numer reczny `stanowisko/session.py:847-854` przyjmuje kazde n >= 1 dla
   kazdego ukladu (takze OR-W, np. 5 albo 8) vs numer odczytany automatycznie `stanowisko/session.py:388-392` (OR spoza 1-3 / 4-6 -> numer
   nieznany) vs rano `stanowisko/session_rano.py:367-377` (tylko numery ukladu). Dla K59, K54, O54, O59 numer automatyczny wieczorem nie
   jest sprawdzany wcale (session.py:389 dziala tylko przy `numery_ramkowe` != None).
3. Lista zapasowa numerow 1..9: `stanowisko/kontroler_api.py:131` `tuple(range(1, 10))` (uzyta w `stanowisko/ui/okno.py:848` i
   `stanowisko/ui/ekran_rano.py:957`) vs numery z plikow STL (`stanowisko/uklad.py:295-309`): zaden uklad nie ma n7; na ekranie
   porannym lista zawiera tez numery wieczorne 1-3 i 8.
4. Docstring vs kod dla n9 w planie ramki porannej: `stanowisko/ramka_protokol.py:187-188` ("bez kalibracji ... `brak_kalibracji`; np.
   plytka okragla testowa n9") vs `stanowisko/ramka_protokol.py:149-151` (numer 9 nie nalezy do `RODZINY["P"]` -> `zla_plytka`, nie
   `brak_kalibracji`; `brak_kalibracji` dostalaby plytka okragla tylko z numerem 4-6). Dodatkowo `stanowisko/session_rano.py:1305-1306`
   kieruje O54-P i O59-P do `poza_ramka`, zanim plan trafi do `plan_rano`.
5. Docstring vs kod "Zamknij piec": `stanowisko/session_rano.py:23-24` (odmawia przy: brak numeru, ten sam numer na dwoch skanach, ...,
   plytka spoza ramki porannej) vs `stanowisko/session_rano.py:866-873` i `:920-924` (dla O54-P / O59-P brak numeru, powtorzony numer i
   "ramka jej nie pokazuje" = tylko ostrzezenie); blokady dla plytek porannych tylko `:916-919` (uklad nie-poranny) i `:925` (numer spoza
   4-6 dla plytek na ramce).
6. Dwie rozne listy "bez_numeru" w session_rano: `stanowisko/session_rano.py:840` (`stan_pieca["bez_numeru"]`: tylko skany `na_ramce`)
   vs `stanowisko/session_rano.py:1303-1304` (`plan_plytek` `pominiete["bez_numeru"]`: kazdy aktywny skan bez numeru, takze O54-P / O59-P,
   -W i nieznane, bo numer sprawdzany przed `na_ramce` z :1305).
7. Rozne klucze "tej samej plytki" rano: `stanowisko/session_rano.py:842-845` (sam numer, tylko `na_ramce`, bez rodziny) vs
   `:470-471` (numer + `rodzina_ukladu`) vs `:869` (numer + rodzina, tylko O-P) vs `:379-384` (numer + `na_ramce`, bez rodziny) vs `:905`
   (sam numer, dowolny uklad); wieczorem `stanowisko/session.py:915-918` (numer + rodzina). Przyklad z kodu: `poranna_r54` n4 i `poranna`
   n4 w jednym piecu sa `zdublowane` (:845, blokada :931-941), ale `_propozycje` (:471) nie proponuje ponownego skanu (rodziny
   "poranna_r54" i "poranna" rozne), a `session.py:917-919` odrzuca zastapienie ("inny uklad plytki").
8. Rozne zrodla geometrii ekranu i diod: `stanowisko/ui/mapa.py:59-62` (katalog ukladu z `[plytki]` przez `UST.katalog_plytki`) vs
   `stanowisko/indicate.py:1290` (`korzen / "modele_plytek"`) + `ramka/kalibracja.py:94-99` (wszystkie `*/uklad.json`, klucz wpisu =
   nazwa katalogu `plik.parent.name`), a wpis kalibracji wyszukiwany po nazwie ukladu z wyniku (`stanowisko/indicate.py:505`,
   `stanowisko/ramka_protokol.py:154` z `uklady[str(n)] = s["uklad"]` - `stanowisko/session_rano.py:1340`). Zgodne tylko, gdy klucz
   `[plytki]` = nazwa katalogu w `modele_plytek` programu (tak jest w `ustawienia.przyklad.toml:19-36`).
9. Nazwa "okragle testowe n8 / n9" w komentarzach odnosi sie do ukladow R59 (`ramka/kalibracja.py:20`, `ramka/README.md:388`:
   `okragla_wieczorna`, `okragla_poranna`; takze `stanowisko/session_rano.py:119`, `:359`, `:837`), a `ustawienia.przyklad.toml:21-23`
   opisuje te same klucze jako "plytki okragle ... (R57, 2.11.2026)" i "uklad gniazd R59"; uklady `okragla_*_r54` nie sa wymienione w tych
   komentarzach, a kod traktuje je tak samo jak R59 (`ramka/kalibracja.py:85-86` -> None, `stanowisko/session_rano.py:114` -> (9,)).

Powielenia tej samej wartosci (wartosci zgodne, wypisane dla kompletnosci): numery ramek W 1-3 / P 4-6 w `stanowisko/session.py:131`,
`stanowisko/session_rano.py:84`, `ramka/protokol.py:41`, `stanowisko/ramka_protokol.py:30`; `nazwa_plytki` w `stanowisko/ui/czesci.py:205`
i `stanowisko/ui/kandydaci.py:24`; teksty `PLYTKA_NR` w `stanowisko/ui/napisy.py:62` i `stanowisko/ui/napisy_rano.py:26`.

---

Liczba wierszy: Tabela A - 95, Tabela B - 36, Tabela C - 21 (plus 14 punktow roznic), Tabela D - 26; Tabela Z - 23 (plus Z-ukl - 10).
