# S3 / wyliczenie 1 - status -> kolor / tekst dla technika (ekran, ramka LED, Excel)

Data: 2026-11-23. Worktree: <PC-katalog>\qc-wt\analiza-s3. Analiza tylko do odczytu. Nie uruchamiano kodu ani testow.

Sciezki w tabeli sa wzgledne do `<PC-katalog>\qc-wt\analiza-s3\Ramki\stanowisko\`:
- `stanowisko\...` - program laptopa,
- `ramka\...` - program ramki na Raspberry Pi.

Linia w kolumnie "plik:linia" to linia z wartoscia domyslna albo z definicja mapowania. Numery linii sprawdzono odczytem pliku.

Zasady cytatow:
- polskie znaki sa zamienione na litery bez ogonkow, a pauza na "-";
- "..." oznacza pominiety koniec dlugiej linii;
- dopisek "(l.N)" przy cytacie wskazuje inna linie tego samego pliku.

Kolumna "czy domyslna wyglada jak dobry wynik" przyjmuje trzy wartosci:
- TAK - galaz domyslna albo koncowa daje zielony, "OK", "rozpoznana", odhaczenie albo inny napis pozytywny;
- NIEJASNE - galaz domyslna daje brak oznaczenia, pusty napis albo zalezy od wolajacego;
- NIE - domyslna jest zolta, czerwona, "sprawdz", odmowa, ciemno albo surowy kod.

## Tabela

| nr | plik:linia | funkcja | co zamienia (status -> kolor / tekst / kod diody / komorka Excela) | lista obslugiwanych wartosci | wartosc domyslna dla nieznanego / None / "" (cytat kodu, max 1 linia) | czy domyslna wyglada jak dobry wynik |
|---|---|---|---|---|---|---|
| 1 | stanowisko\statusy.py:57 | `_WIERSZE` (modul) | klucz statusu -> klasa koloru, RGB ekranu, kolor diod (pole `ramka`), napis gniazda, opis | 22 klucze: zielony, czerwony, ukruszona, zatwierdzona_ok, zolty, sprawdz_ulozenie, popraw_ulozenie, skan_ponownie, skan_do_powtorzenia, nie_sprawdzono, blad_inspekcji, szary, pomaranczowy, dofrezowany, nieznana_rano, pusty, podwojny, poza_gniazdem, czeka_na_numer, plytka_nie_z_trybu, nieaktywny, nieznany | wiersz zapasowy (l.91): `_s("nieznany", KOLOR_ZOLTY, (240, 200, 40), "zolty", "sprawdz", ...` | NIE - wiersz zapasowy jest zolty "sprawdz". Fakty o kolumnie `ramka`: `zatwierdzona_ok` ma "zielony" (l.62), tak samo jak `zielony` (l.58); `pusty`, `poza_gniazdem`, `czeka_na_numer`, `plytka_nie_z_trybu` i `nieaktywny` maja None, czyli nie swieca. `pusty` ma napis "" (l.84). |
| 2 | stanowisko\statusy.py:101 | `_WIERSZE_RANO` (modul) | klucz rano_* -> RGB, diody, napis, opis | rano_pewna, rano_przypisana (zielone), rano_dwuznaczna (zolty), rano_konflikt (czerwony), rano_juz_rozpoznany (bursztyn) | w tabeli brak domyslnej; nieznany klucz obsluguje `status()` (l.143) | NIE - patrz wiersz 3 |
| 3 | stanowisko\statusy.py:143 | `status` | klucz -> wiersz `Status` (kolor, napis, opis, diody) | klucze STATUSY i STATUSY_RANO_WIERSZE | `return STATUSY.get(klucz or "") or STATUSY_RANO_WIERSZE.get(klucz or "") or STATUSY["nieznany"]` | NIE - None, "" i nieznany klucz daja zolty "sprawdz" i diody "zolty" |
| 4 | stanowisko\statusy.py:149 | `status_rano` | klasa poranna -> wiersz (`STATUSY_RANO`, l.114-117) | pewna, przypisana, dwuznaczna, nieznana, poprawka, konflikt, do_powtorzenia | `return STATUSY_RANO.get(klasa or "", STATUSY["nieznany"])` | NIE - zolty "sprawdz" |
| 5 | stanowisko\statusy.py:167 | `status_pracy` | kolor pracy None -> klucz statusu | skan aktywny: przyjety, do_powtorzenia (l.129) | `return "nieznany" if status_skanu in STATUSY_SKANU_AKTYWNE else "nieaktywny"` | NIE - skan aktywny: zolty "sprawdz"; nieaktywny: szary "skan nieaktualny" bez diod |
| 6 | stanowisko\statusy.py:176 | `status_pracy` | status inspekcji przy kolorze zielonym -> klucz | "ok" przechodzi dalej; None, "pominieto", "nie_sprawdzono" (l.127) daja nie_sprawdzono; blad daje blad_inspekcji (l.174-175) | `return "nie_sprawdzono" if status_inspekcji in INSPEKCJE_NIESPRAWDZONE else "nieznany"` | NIE - oba statusy sa zolte |
| 7 | stanowisko\statusy.py:177 | `status_pracy` | status dopasowania -> zgoda na zielony | "zielony", "zolty" (l.128); None = "nie sprawdzac" | `if status_match is not None and status_match not in DOPASOWANIA_ZIELONE:` | NIEJASNE - status_match None, takze jako wartosc domyslna parametru (l.153), pomija te kontrole i pozwala na "zielony". kontroler_api.py:3149 zamienia None z bazy na "brak". |
| 8 | stanowisko\statusy.py:179 | `status_pracy` | numer plytki -> "zielony" albo "czeka_na_numer" | numer_znany True albo False; `ZIELONE_BEZ_NUMERU_PLYTKI = False` (l.137) | `return "zielony" if numer_znany or ZIELONE_BEZ_NUMERU_PLYTKI else "czeka_na_numer"` | NIEJASNE - parametr `numer_znany` ma wartosc domyslna True (l.153), wiec wywolanie bez niego daje "zielony". kontroler_api.py:3148 podaje go jawnie. |
| 9 | stanowisko\statusy.py:187 | `status_pracy` | kolor zolty -> dokladny zolty status | nie_sprawdzono, blad_inspekcji, ZOLTE_WG_INSPEKCJI (l.122-123), skan_do_powtorzenia | `return "zolty"` | NIE - zolty "sprawdz" |
| 10 | stanowisko\statusy.py:188 | `status_pracy` | pozostale klasy koloru -> klucz | STATUS_WG_KOLORU (l.131-132): zielony, czerwony, zolty, szary, pomaranczowy, zatwierdzona_ok | `return STATUS_WG_KOLORU.get(kolor, "nieznany")` | NIE - zolty "sprawdz" |
| 11 | stanowisko\statusy.py:203 | `kolor_pracy` | klucz statusu i kolor z sesji -> klasa koloru pracy (liczniki, "do obejrzenia") | czeka_na_numer daje None (l.196-197); zielony tylko dla STATUSY_ZIELONE (l.199-200); nieznany daje zolty (l.201-202) | `return kolor` | NIE - kolor przechodzi bez zmian tylko przy statusie zgodnym z kolorem; zielony przy innym statusie dostaje klase tego statusu |
| 12 | stanowisko\statusy.py:218 | `napis_plytki` | status skanu -> napis plytki | przyjety, do_powtorzenia, zastapiony, niezgodny_uklad, plytka_nie_z_trybu, blad (l.207-214) | `return STATUSY_PLYTKI.get(status_skanu, status_skanu)` | NIEJASNE - nieznany status trafia na ekran jako surowy kod; None daje None (brak napisu); "przyjety" daje "przeanalizowana" |
| 13 | stanowisko\statusy.py:646 | `tekst_komunikatu` | rodzaj komunikatu -> poziom, tytul, tekst | klucze KOMUNIKATY (l.325-493) | `w = KOMUNIKATY.get(rodzaj) or Wzor(POZIOM_OSTRZEZENIE, "Uwaga", "{powod}")` | NIE - ostrzezenie "Uwaga" |
| 14 | stanowisko\statusy.py:651 | `tekst_pytania` | rodzaj pytania -> poziom, tytul, tekst | klucze PYTANIA (l.531-547) | `w = PYTANIA[rodzaj]` (brak domyslnej, KeyError) | NIE - brak domyslnej |
| 15 | stanowisko\statusy.py:657 | `_Braki.__missing__` | brakujace pole w tekscie komunikatu -> napis | pola `{...}` wzoru | `return "?"` | NIE |
| 16 | stanowisko\session.py:1125 | `Sesja._kolor` | status gniazda z analizy i decyzja -> klasa koloru pracy (pole `kolor`) | skan nieaktywny daje None (l.1117-1118); ukruszona daje czerwony; "ok" daje zatwierdzona_ok; do_powtorzenia i zielony daje "zolty" | `return status_gniazda` | NIE - wartosc przechodzi bez zmian, takze None i wartosc nieznana; na "nieznany" (zolty) zamienia ja dopiero statusy.py:167 albo :188. Liczniki sesji (l.1164-1166) licza nieznana klase pod jej nazwa i pomijaja None. |
| 17 | stanowisko\session.py:385 | `Sesja.przyjmij_wynik` | pola wyniku analizy -> status skanu | uklad_zgodny False daje niezgodny_uklad (l.378-379); plytka nie z trybu (l.380-381); `_do_powtorzenia` daje do_powtorzenia (l.382-383) | `status = STATUS_PRZYJETY` | NIEJASNE - wynik ze znanym ukladem `plytka`, ale bez pol `uklad_zgodny`, `gniazda_podwojne`, `poza_gniazdem`, `status_fragmentu` i `inspekcja` (None albo brak klucza), dostaje "przyjety", czyli "przeanalizowana" |
| 18 | stanowisko\session.py:892 | `Sesja._praca_do_decyzji` | status skanu -> rada w odmowie decyzji | zastapiony, do_powtorzenia, niezgodny_uklad, plytka_nie_z_trybu | `}.get(praca["status_skanu"], "ten skan nie nalezy do wieczoru")` | NIE |
| 19 | stanowisko\session_rano.py:782 | `SesjaRano._oblicz` | praca poranna -> klasa | skan nieaktywny daje None (l.770-771); do_powtorzenia (l.772-773); bez projektu dwuznaczna albo nieznana (l.774-776); konflikt (l.777-778); poprawka (l.779-780) | `klasa = KLASA_PRZYPISANA if d is not None else KLASA_PEWNA` | TAK - koncowa galaz `else` daje klase zielona (pewna albo przypisana). Dostaje ja kazda praca aktywnego skanu z przypisanym projektem, ktora nie spelnila zadnego wczesniejszego warunku. |
| 20 | stanowisko\session_rano.py:791 | `SesjaRano._oblicz` | klasa -> klucz statusu (`STATUS_KLASY`, l.56-57) -> kolor i kolor diod (l.792) | 7 klas | `status = STATUS_KLASY.get(klasa) if klasa else None` | NIEJASNE - klasa None albo nieznana daje status, kolor i kolor_ramki None: gniazdo nie ma klasy koloru i nie swieci na ramce (ramka_protokol.py:121-122) |
| 21 | stanowisko\session_rano.py:104 | `kolory_statusu` | klucz statusu -> (kolor ekranu, kolor diod) | klucze STATUSY; zapas STATUSY_ZAPASOWE (l.58) | `return (w.kolor, w.ramka) if w is not None else STATUSY_ZAPASOWE.get(klucz, (None, None))` | NIEJASNE - klucz spoza STATUSY daje (None, None): brak koloru i brak swiecenia. Funkcja czyta tylko STATUSY, bez STATUSY_RANO_WIERSZE. |
| 22 | stanowisko\session_rano.py:581 | `SesjaRano._przypisanie_auto` | status dopasowania -> przypisanie automatyczne (z niego klasa pewna) | tylko "zielony" | `if praca["status_match"] != "zielony" or not sha:` | NIE - inny status i None daja brak przypisania |
| 23 | stanowisko\session_rano.py:1312 | `SesjaRano.plan_plytek` | dwie prace w gniezdzie albo kuweta niepewna -> kolor diod | podwojny daje "zolty", czerwony daje "czerwony" | `kolor_dwie, kolor_sprawdz = kolory_statusu(STATUS_DWIE_PRACE)[1], kolory_statusu(STATUS_SPRAWDZ)[1]` | NIE |
| 24 | stanowisko\session_rano.py:1330 | `SesjaRano.plan_plytek` | kolor_ramki pracy -> kolor gniazda w planie ramki P | wartosci z `kolory_statusu` | `g = {"id": gid, "kolor": p["kolor_ramki"]}` | NIEJASNE - None przechodzi do planu; ramka_protokol.py:121-122 pomija takie gniazdo, wiec jest ciemne |
| 25 | stanowisko\session_rano.py:1337 | `SesjaRano.plan_plytek` | klasa z kuweta (pewna, przypisana, poprawka; l.53) z kuweta pusta albo niezgodna z wzorem -> kolor | - | `g["kolor"] = kolor_sprawdz` | NIE - czerwony |
| 26 | stanowisko\session_rano.py:512 | `SesjaRano._praca_rano` | status skanu -> rada w odmowie decyzji | zastapiony, do_powtorzenia, niezgodny_uklad, plytka_nie_z_trybu | `}.get(p["status_skanu"], "skan nie zostal przyjety")` | NIE |
| 27 | stanowisko\ramka_protokol.py:63 | `kolor_ramki` | status gniazda -> kolor diod ramki W | klucze statusy (kolumna `ramka`) | `return statusy.status(status_klucz).ramka` | NIE - nieznany status daje "zolty"; statusy z `ramka` None daja gniazdo, ktore nie swieci |
| 28 | stanowisko\ramka_protokol.py:122 | `_gniazda` | kolor None -> gniazdo poza planem | - | `continue  # gniazdo bez koloru (puste, skan nieaktywny) - nie swieci` | NIEJASNE - gdy wszystkie gniazda plytki maja None, plytka idzie z `"gniazda": []` (l.159). Ramka przyjmuje taki plan i pokazuje stan "wynik" z zielonym pierscieniem (ramka\logika.py:576). |
| 29 | stanowisko\ramka_protokol.py:127 | `_gniazda` | kolor spoza protokolu -> kolor diod | KOLORY = ramka.obraz.KOLORY: czerwony, zielony, zolty, bursztyn, bialy, niebieski, fioletowy, szary | `kolor = KOLOR_SPRAWDZ` | NIE - "czerwony" (l.33) |
| 30 | stanowisko\ramka_protokol.py:135 | `_gniazda` | odrzucona kuweta -> kolor diod | kuweta `#?[0-9]{1,6}` z listy kuwet | `wpis["kolor"] = KOLOR_SPRAWDZ` | NIE - czerwony |
| 31 | stanowisko\ramka_protokol.py:125 | `_gniazda` | gniazdo z kolorem bez kalibracji -> cala plytka | - | `return None` | NIE - plytka bez obrazu; ramka pokazuje "{p} BRAK" |
| 32 | stanowisko\ramka_protokol.py:158 | `_plytki` | plytka bez kalibracji ukladu -> pominieta | - | `continue` | NIE - jak wiersz 31 |
| 33 | stanowisko\ramka_protokol.py:152 | `_plytki` | numer plytki spoza rodziny roli -> pominieta | W: 1-3, P: 4-6 | `continue` | NIE |
| 34 | stanowisko\indicate.py:344 | `KlientRamki.stan` | kod bledu albo brak polaczenia (l.336) -> komunikat | 10 kodow KOMUNIKATY (l.62-73) | `"komunikat": KOMUNIKATY.get(kod) if kod else None` | NIE - nieznany kod daje brak komunikatu, ale pole `blad` zostaje; kazdy kod ustawiany w klasie jest w slowniku |
| 35 | stanowisko\indicate.py:489 | `KlientRamki.wynik` | kolory gniazd -> wynik do planu W | dowolne; walidacja dopiero w ramka_protokol.py:126-127 | `self._wyniki = {numer_plytki: _Wynik(uklad, {int(g): c for g, c in kolory.items()}, znacznik)}` | NIE - kolory przechodza bez zamiany |
| 36 | stanowisko\indicate.py:501 | `KlientRamki._sprawdz_wynik` | numer plytki None -> powod niewyslania | - | `return WYNIK_BEZ_NUMERU` | NIE - ramka ciemna (l.491-496) |
| 37 | stanowisko\indicate.py:511 | `KlientRamki._sprawdz_wynik` | gniazdo z kolorem bez kalibracji -> caly wynik | - | `if c is not None and str(int(g)) not in gn:` | NIE - caly wynik dostaje "brak_kalibracji" i ramka jest ciemna; gniazd z kolorem None nie sprawdza |
| 38 | stanowisko\indicate.py:496 | `KlientRamki.wynik` | wynik biezacego skanu niewyslany -> tryb ramki | - | `self._zlec_gaszace("PUT", "/tryb", RP.tresc_trybu("gotowa"), "gotowa")` | NIE - ramka "gotowa": niebieski pierscien, gniazda ciemne |
| 39 | stanowisko\indicate.py:1039 | `KlientRamki._zbuduj_plan` | plan W bez plytek -> brak planu | - | `return None` | NIE |
| 40 | stanowisko\indicate.py:1023 | `KlientRamki._zbuduj_plan` | ramka P bez kalibracji -> blad i zgaszenie (l.1024) | - | `self._blad = "brak_kalibracji"` | NIE |
| 41 | stanowisko\indicate.py:1185 | `KlientRamki._po_planie` | kod odrzucenia planu -> kod bledu | plan_innej_ramki; reszta | `self._blad = "plan_innej_ramki" if kod == "plan_innej_ramki" else "plan_odrzucony"` | NIE |
| 42 | stanowisko\ui\czesci.py:171 | `styl_znaczka_poziomu` | poziom -> barwy znaczka | info, ostrzezenie, blad | `tlo, pasek, kolor = styl.POZIOMY.get(poziom, styl.POZIOMY["info"])` | NIE - nieznany poziom daje niebieskie "info" |
| 43 | stanowisko\ui\czesci.py:217 | `do_obejrzenia` | klasa koloru i decyzja -> "praca do obejrzenia" (napis plytki, klawisz N, przelaczanie ekranu) | kolor nie None i nie zielony ani zatwierdzona_ok, brak decyzji, "ukruszona" w dozwolone | `if p.decyzja is None and "ukruszona" in p.dozwolone and p.kolor is not None and p.kolor not in (...)` | NIEJASNE - praca z kolorem None albo bez "ukruszona" w dozwolone nie liczy sie jako do obejrzenia |
| 44 | stanowisko\ui\czesci.py:241 | `stan_obejrzenia` | stan plytki -> napis plytki (kafelek, naglowek mapy) | ponowny skan (l.232-233); napis ze stanu (l.234-235); "do obejrzenia: n" (l.237-238); napis ze stanu bez numeru albo bez decyzji (l.239-240) | `return N.PLYTKA_SPRAWDZONA` | NIEJASNE - "sprawdzona" to galaz koncowa. Wystarcza pusta lista z `do_obejrzenia` (wiersz 43), numer plytki i jedna praca z dozwolona decyzja. |
| 45 | stanowisko\ui\czesci.py:235 | `stan_obejrzenia` | skan inny niz przyjety albo napis nieznany -> napis | - | `return plytka.napis` | NIE |
| 46 | stanowisko\ui\czesci.py:248 | `napis_dopuszczenia` | typ plytki -> napis znacznika | wieczorna, poranna (statusy.py:555) | `ST.JAKA_PLYTKA.get(plytka.typ, ST.JAKA_PLYTKA[None])` | NIE - "plytka o nieznanym ukladzie" |
| 47 | stanowisko\ui\czesci.py:550 | `PasekStanu.ustaw` | stan puli -> napis | napis ze stanu; STANY_PULI | `self.pula.setText(stan.pula.napis or ST.STANY_PULI.get(stan.pula.stan, ""))` | NIEJASNE - nieznany stan bez napisu daje pusty tekst (rola z l.551: wartosc_uwaga) |
| 48 | stanowisko\ui\czesci.py:551 | `PasekStanu.ustaw` | stan puli -> rola pola | gotowa, liczenie | `self._rola(self.pula, "wartosc" if stan.pula.stan in ("gotowa", "liczenie") else "wartosc_uwaga")` | NIE - zolte tlo |
| 49 | stanowisko\ui\czesci.py:577 | `PasekStanu.ustaw` | stan skanera -> napis | dostepny, dziala, zajete, czeka_na_skan (l.568-575) | `self.skaner.setText(N.SKANER_GOTOWY)` | NIE - koncowa galaz "dostepny" wymaga prawdziwych `dostepny` i `dziala`; None daje "niedostepny" albo "nie jest obserwowany" |
| 50 | stanowisko\ui\czesci.py:607 | `PasekStanu._ustaw_ramki` | stan klienta ramki -> klucz stanu | test, gotowa, x.blad, brak_polaczenia | `klucz = "test" if r.test_led else ("gotowa" if x.polaczona and x.blad is None else (x.blad or "brak_polaczenia"))` | NIEJASNE - "gotowa" zalezy tylko od `polaczona` i `blad`. Ostrzezenia (np. brak kalibracji ramki W, indicate.py:197-198) i utracone zdarzenia sa tylko w podpowiedzi (l.610-612). Przy `test_led` obie ramki maja "test" niezaleznie od polaczenia. |
| 51 | stanowisko\ui\czesci.py:608 | `PasekStanu._ustaw_ramki` | klucz -> napis stanu ramki | gotowa, brak_polaczenia, inny_laptop, zly_klucz, blad_sprzetu, test, inny (napisy_rano.py:143-144) | `NR.RAMKA_STANY.get(klucz, NR.RAMKA_STANY["inny"])` | NIE - "blad" |
| 52 | stanowisko\ui\czesci.py:613 | `PasekStanu._ustaw_ramki` | klucz -> rola pola (zwykla albo zolte tlo) | gotowa, test | `dobrze = dobrze and klucz in ("gotowa", "test")` | NIEJASNE - "test" dostaje zwykla role jak "gotowa", takze bez polaczenia |
| 53 | stanowisko\ui\czesci.py:689 | `PanelUwagi.__init__` | poziom pytania albo komunikatu -> barwy panelu | info, ostrzezenie, blad | `tlo, pasek, _ = styl.POZIOMY.get(poziom, styl.POZIOMY["ostrzezenie"])` | NIE |
| 54 | stanowisko\ui\czesci.py:740 | `panel_pytania` | typ plytki -> rada w pytaniu | poranna, wieczorna | `rada = {"poranna": N.RADA_PLYTKA_PORANNA, "wieczorna": N.RADA_PLYTKA_WIECZORNA}.get(typ_plytki, N.RADA_PLYTKA_NIEZNANA)` | NIE |
| 55 | stanowisko\ui\czesci.py:868 | `KafelekPlytki.__init__` | klasa koloru -> kolor i podpowiedz licznika | KLASY_LICZNIKOW (l.38) | `wiersz_st = ST.status(ST.STATUS_WG_KOLORU[klasa])` | NIE |
| 56 | stanowisko\ui\czesci.py:874 | `KafelekPlytki.__init__` | klasa spoza KLASY_LICZNIKOW -> licznik | - | `z = znaczek(str(n), ST.status(None).hex, rozmiar_px=r.znaczek)` | NIE - zolty "sprawdz" |
| 57 | stanowisko\ui\czesci.py:878 | `KafelekPlytki.__init__` | brak licznikow przy aktywnym skanie -> napis | - | `liczniki.addWidget(etykieta(N.PLYTKA_BEZ_PRAC, "slaby"))` | NIE - "brak prac" |
| 58 | stanowisko\ui\czesci.py:1140 | `WidokPracy.__init__` | decyzja -> kolor przycisku | ukruszona, ok | `self._kolory_decyzji[polecenie] = ST.STATUSY[status_koloru].hex` | NIE - brak domyslnej |
| 59 | stanowisko\ui\czesci.py:1233 | `WidokPracy.ustaw` | podpis statusu -> widocznosc znaczka statusu (kolor z l.1234) | podpis ze stanu | `self.status.setVisible(bool(zrodlo.podpis))` | NIEJASNE - pusty podpis ukrywa znaczek statusu, zostaje sam opis |
| 60 | stanowisko\ui\czesci.py:1238 | `WidokPracy.ustaw` | status gniazda z dwiema pracami -> opis | STATUSY | `opis = ST.status(zrodlo.status).opis if zrodlo is gniazdo else praca.opis` | NIE |
| 61 | stanowisko\ui\czesci.py:1246 | `WidokPracy.ustaw` | liczba ubytkow -> napis | wiecej niz 0: rozmiar i liczba (l.1242-1244) | `self.ubytek.setText(N.BEZ_UBYTKOW if praca is not None else "")` | TAK - `ubytki` None (praca bez inspekcji: session.py:476, kontroler_api.py:3176) daje "Program nie wskazal ubytku.", tak samo jak 0 ubytkow |
| 62 | stanowisko\ui\czesci.py:1252 | `WidokPracy.ustaw` | decyzja -> nazwa decyzji | "ok"; reszta | `nazwa_decyzji = ST.PRZYCISKI["ok"] if praca.decyzja == "ok" else ST.PRZYCISKI["ukruszona"]` | NIE - nieznana decyzja daje "Ukruszona" |
| 63 | stanowisko\ui\czesci.py:1396 | `Legenda.ustaw` | status gniazda -> opis w podpowiedzi legendy (znaczek: podpis i rgb, l.1406) | STATUSY | `if ST.status(g.status).opis not in opisy:` | NIE |
| 64 | stanowisko\ui\mapa.py:364 | `MapaPlytki._rysuj_gniazdo` | Gniazdo.rgb -> wypelnienie gniazda | hex ze stanu | `p.setBrush(QBrush(QColor(g.rgb)))` | NIE - widzet nie ma domyslnej; kolor policzyl statusy.status (nieznany = zolty) |
| 65 | stanowisko\ui\mapa.py:367 | `MapaPlytki._rysuj_gniazdo` | obecnosc prac -> kolor napisu | - | `kolor_tekstu = QColor(styl.tekst_na(g.rgb)) if g.prace else QColor("#8a929c")` | NIE |
| 66 | stanowisko\ui\mapa.py:380 | `MapaPlytki._rysuj_gniazdo` | pusty podpis -> sam numer | - | `if not g.podpis:` | NIEJASNE - gniazdo bez podpisu pokazuje numer na kolorze, bez napisu statusu |
| 67 | stanowisko\ui\mapa.py:395 | `MapaPlytki._rysuj_gniazdo` | podpis, ktory sie nie miesci -> sam numer | - | `else:  # A-D7: podpis nie miesci sie nawet najmniejsza czcionka - sam numer ...` | NIEJASNE - napis statusu znika, zostaje kolor gniazda |
| 68 | stanowisko\ui\mapa.py:125 | `MapaPlytki.ustaw` | plytka bez gniazd do narysowania -> napis | - | `self._napis = N.MAPA_BEZ_GNIAZD.format(napis=plytka.napis)` | NIE |
| 69 | stanowisko\ui\okno.py:72 | `blad_programu` | poziom komunikatu -> pasek bledow programu | "blad" albo komunikat trwaly | `return komunikat.poziom == ST.POZIOM_BLAD or komunikat.trwaly` | NIE - inny poziom trafia do zwyklych paneli (barwy ostrzezenia, czesci.py:689) |
| 70 | stanowisko\ui\okno.py:742 | `OknoWieczor._odswiez_naglowek` | stan plytki -> naglowek mapy | czesci.stan_obejrzenia | `napis = stan_obejrzenia(plytka)  # "do obejrzenia: n" / "sprawdzona" albo napis ze stanu` | NIEJASNE - jak wiersz 44 |
| 71 | stanowisko\ui\okno.py:775 | `OknoWieczor._odswiez_naglowek` | praca poza gniazdem -> napis i kolor przycisku (l.776) | rgb i podpis statusu "poza_gniazdem" (kontroler_api.py:3189-3190) | `b = przycisk(p.podpis, f"poza_{i}", None, lambda praca_id=p.praca_id: self._klik_poza(praca_id))` | NIE |
| 72 | stanowisko\ui\styl.py:29 | `POZIOMY` (modul) | poziom komunikatu -> (tlo, pasek, tekst) | info, ostrzezenie, blad | slownik bez domyslnej; domyslne przy uzyciu: czesci.py:171 ("info"), :689 ("ostrzezenie") | NIE - zadna barwa nie jest zielona |
| 73 | stanowisko\ui\obraz.py:41 | `rysuj_odchylki` | odchylka punktu -> kolor (skala odchylki, nie status) | d < -prog: czerwony (l.43); d > prog: niebieski (l.44) | `kolor = np.full((len(d), 3), 186.0)` | NIEJASNE - punkt z abs(d) <= 0,08 mm i punkt z d = NaN (porownania sa falszywe) dostaja szary "zgodnie z projektem" (opis l.9) |
| 74 | stanowisko\ui\obraz.py:36 | `rysuj_odchylki` | brak punktow albo zle wymiary -> obraz | - | `return QImage(tlo.tobytes(), szer, wys, 3 * szer, QImage.Format.Format_RGB888).copy()` | NIEJASNE - powstaje pusty bialy obraz zamiast napisu "Brak obrazu tej pracy."; napis jest tylko przy obrazie None (okno.py:931-932) |
| 75 | stanowisko\ui\ekran_rano.py:112 | `lista_nierozstrzygnietych` | klasa -> napis w nawiasie | 7 klas | `napis = ST.status_rano(x.klasa).napis` | NIE - "sprawdz" |
| 76 | stanowisko\ui\ekran_rano.py:244 | `PanelKuwet.ustaw` | brak kuwety biezacej -> tytul panelu | biezaca; brak pieca (l.240-241) | `self.biezaca.setText(NR.KUWETA_BRAK if rano.otwarty else NR.PIEC_ZAMKNIETY_INFO)` | TAK - napis "Wszystkie kuwety rozlozone - mozesz zamknac piec." (napisy_rano.py:48) wynika tylko z braku kuwety z flaga `biezaca`. Galaz nie sprawdza blokad ani prac nierozstrzygnietych. |
| 77 | stanowisko\ui\ekran_rano.py:259 | `PanelKuwet.ustaw` | flagi kuwety -> kolumna "Stan" | biezaca "teraz", potwierdzona "rozlozona", braki "braki" | `NR.KUWETA_STAN_BRAKI if x.braki else NR.KUWETA_STAN_CZEKA)` | NIEJASNE - stan "czeka" to pusta komorka (napisy_rano.py:58); kuweta rozlozona z brakami pokazuje tylko "rozlozona" |
| 78 | stanowisko\ui\ekran_rano.py:397 | `PanelWyniku._odswiez_reczne` | stan punktu -> "Zab X - {stan}" | napisy STANY_PUNKTU | `self._reczne.addWidget(etykieta(NR.RECZNE_PUNKT.format(zab=b.zeby or NR.BRAK_DANYCH, stan=b.napis), "duzy", zawijaj=True))` | NIEJASNE - pusty napis stanu (kontroler_api.py:1726 daje "" dla None) zostawia punkt bez oznaczenia |
| 79 | stanowisko\ui\ekran_rano.py:399 | `PanelWyniku._odswiez_reczne` | stan punktu -> przyciski powodow | do_dofrezowania; reszta (statusy.py:288-290) | `for kod, napis in ST.powody_zamkniecia(b.stan).items():` | NIE |
| 80 | stanowisko\ui\ekran_rano.py:421 | `PanelWyniku._brakuje` | punkty -> kolumna "Brakuje" | lista zebow | `return ", ".join(b.zeby or NR.BRAK_DANYCH for b in z.brakujace) or NR.LISTA_PUSTA` | NIEJASNE - pusta lista daje pauze |
| 81 | stanowisko\ui\ekran_rano.py:425 | `PanelWyniku._stany` | stany punktow -> kolumna "Stan" | napisy STANY_PUNKTU | `return ", ".join(dict.fromkeys(b.napis for b in z.brakujace)) or NR.LISTA_PUSTA` | NIEJASNE - same puste napisy daja pauze; nieznany kod pokazuje sie surowo |
| 82 | stanowisko\ui\ekran_rano.py:444 | `PanelWyniku.ustaw` | stan pieca -> tytul wyniku | brak, ostatni, otwarty; reszta | `self.tytul.setText(NR.WYNIK_TYTUL_ZAMKNIETY.format(nr=rano.nr_w_dniu, ...` | NIE |
| 83 | stanowisko\ui\ekran_rano.py:460 | `PanelWyniku.ustaw` | z_dofrezowaniem -> kolumna "Uwagi" | True, False | `NR.UWAGA_DOFREZOWANY if z.z_dofrezowaniem else ""` | NIE |
| 84 | stanowisko\ui\ekran_rano.py:464 | `PanelWyniku.ustaw` | prace nierozstrzygniete -> ostrzezenie | lista z kontrolera | `nier = tuple(getattr(rano, "nierozstrzygniete_prace", ()) or ()) if rano is not None else ()` | NIEJASNE - brak pola albo pusta lista ukrywa ostrzezenie (l.470) |
| 85 | stanowisko\ui\ekran_rano.py:477 | `PanelWyniku.ustaw` | zlecenie_odhaczone -> rola "informacja" albo "uwaga" | True, False | `rozpoznane = [x for x in poprawki if not x.zlecenie_odhaczone]` | NIE - False trafia do "uwaga" |
| 86 | stanowisko\ui\ekran_rano.py:485 | `PanelWyniku.ustaw` | ostatni piec -> kolumna "Piec" | int | `str(z.ostatni_piec or NR.BRAK_DANYCH)` | NIE |
| 87 | stanowisko\ui\ekran_rano.py:690 | `EkranRano._wybor_pracy` | gniazdo -> praca w widoku pracy | 0, 1 albo wiecej prac | `return plytka, gniazdo, gniazdo.prace[0] if gniazdo.prace else None` | TAK - gniazdo "podwojny" (na mapie "dwie prace") pokazuje w widoku status PIERWSZEJ pracy, np. zielone "rozpoznana", bo kandydaci.py:180 bierze prace przed gniazdem. Wieczorem czesci.py:1229 bierze w tej sytuacji status gniazda. |
| 88 | stanowisko\ui\ekran_rano.py:738 | `EkranRano._odswiez_karty` | brak widocznych plytek -> napis | brak pieca; reszta | `self.bez_plytek = etykieta(NR.PIEC_BRAK if rano is None or rano.sesja_pieca_id is None else NR.PIEC_ZAMKNIETY_INFO,` | NIEJASNE - napis "Piec zamkniety - ..." pojawia sie takze przy otwartym piecu bez widocznych plytek, bo galaz nie sprawdza `rano.otwarty` |
| 89 | stanowisko\ui\ekran_rano.py:756 | `EkranRano._odswiez_karty` | aktywnosc skanu -> tytul karty plytki | aktywny: sam numer; nieaktywny: numer i napis | `karta.tytul.setText(nazwa_plytki(p.numer) + ("" if p.aktywna else NR.ODSTEP_NAPISU + p.napis))` | NIEJASNE - aktywny skan, takze "do_powtorzenia", nie ma statusu w tytule |
| 90 | stanowisko\ui\ekran_rano.py:778 | `EkranRano._odswiez_karty` | prace poza gniazdem -> liczba | int | `karta.poza.setText(NR.POZA_GNIAZDAMI.format(n=len(p.poza_gniazdem)) if p.poza_gniazdem else "")` | NIEJASNE - sama liczba, bez koloru i statusu tych prac |
| 91 | stanowisko\ui\ekran_rano.py:781 | `EkranRano._odswiez_karty` | skany zastapione -> lista tekstowa | status "zastapiony" | `NR.PLYTKA_NIEAKTYWNA.format(plytka=nazwa_plytki(p.numer), godzina=godzina(p.czas), napis=p.napis)` | NIE |
| 92 | stanowisko\ui\ekran_rano.py:789 | `EkranRano._odswiez_karty` | status gniazda -> napis i dymek znaczka legendy (kolor g.rgb, l.796) | STATUSY i STATUSY_RANO_WIERSZE | `w = ST.status(g.status)` | NIE |
| 93 | stanowisko\ui\ekran_rano.py:810 | `EkranRano._odswiez_naglowek` | liczniki klas -> znaczki licznikow | KOLEJNOSC_KLAS (l.49) | `liczniki = tuple((k, (rano.liczniki or {}).get(k, 0)) for k in KOLEJNOSC_KLAS) if rano is not None else ()` | NIEJASNE - brak klucza daje 0, a 0 nie ma znaczka (l.814); klasa spoza KOLEJNOSC_KLAS nie jest pokazana |
| 94 | stanowisko\ui\ekran_rano.py:815 | `EkranRano._odswiez_naglowek` | klasa -> napis, kolor i dymek licznika | 7 klas | `w = ST.status_rano(klasa)` | NIE - licznik "poprawka" zawsze ma napis "zab dofrezowany", takze dla prac, ktore mapa pokazuje jako "zab juz rozpoznany" |
| 95 | stanowisko\ui\ekran_rano.py:822 | `EkranRano._odswiez_naglowek` | blokady "Zamknij piec" -> napis | teksty z kontrolera | `self.blokady.setText(NR.BLOKADY_TYTUL + " " + " ".join(blokady) if blokady else "")` | NIEJASNE - pusta krotka daje brak napisu |
| 96 | stanowisko\ui\ekran_rano.py:880 | `EkranRano._panel_zamkniecia` | stan brak_po_piecu -> tekst pytania | staly klucz | `ST.STANY_PUNKTU["brak_po_piecu"]` | NIE |
| 97 | stanowisko\ui\mapa_rano.py:140 | `MapaRano._rysuj_gniazdo` | Gniazdo.rgb -> wypelnienie | hex z kontrolera | `p.setBrush(QBrush(QColor(g.rgb)))` | NIE - widzet nie ma domyslnej; domyslna wczesniej daje status_rano zolty |
| 98 | stanowisko\ui\mapa_rano.py:143 | `MapaRano._rysuj_gniazdo` | obecnosc prac -> kolor napisow | - | `kolor_tekstu = QColor(styl.tekst_na(g.rgb)) if g.prace else QColor("#8a929c")` | NIE |
| 99 | stanowisko\ui\mapa_rano.py:63 | `MapaRano._plan` | Gniazdo.podpis (nr kuwety albo napis statusu) -> napis | dowolny tekst | `kuweta = g.podpis or ""` | NIEJASNE - pusty podpis daje sam numer gniazda (l.88-90), bez napisu statusu; kolor zostaje |
| 100 | stanowisko\ui\mapa_rano.py:100 | `MapaRano._plan` | napis, ktory sie nie miesci -> sam numer | - | `plan[:] = []` (tak samo l.107; l.82-83 `if f is None:`) | NIEJASNE - napis ("wybierz", "konflikt", nr kuwety) znika, zostaje kolor i numer, jesli sie miesci |
| 101 | stanowisko\ui\mapa_rano.py:179 | `MapaRano._biezacej` | gniazdo biezacej kuwety -> obwodka | numer w obwodce albo nie | `return g.nr in self._obwodka` | NIE |
| 102 | stanowisko\ui\kandydaci.py:77 | `KartaKandydata.__init__` | pokrycie -> "pasuje w x %" | float | `if kandydat.pokrycie is not None:` | NIEJASNE - None daje brak procentu i brak oznaczenia |
| 103 | stanowisko\ui\kandydaci.py:88 | `KartaKandydata.__init__` | kuweta kandydata -> tekst | str | `kandydat.kuweta or NR.BRAK_DANYCH` | NIE |
| 104 | stanowisko\ui\kandydaci.py:94 | `KartaKandydata.__init__` | projekt_id None i liczba zlecen -> powod zamiast przycisku | zlecen == 0; inne | `powod = NR.KANDYDAT_POZA_INDEKSEM if kandydat.zlecen == 0 else NR.KANDYDAT_KILKA_ZLECEN.format(n=kandydat.zlecen)` | NIE |
| 105 | stanowisko\ui\kandydaci.py:185 | `WidokPracyRano.ustaw` | status pracy albo gniazda -> znaczek (napis; kolor zrodlo.rgb) | STATUSY i STATUSY_RANO_WIERSZE | `status = znaczek(ST.status(zrodlo.status).napis, zrodlo.rgb, "praca_rano_status", r.status_pracy)` | NIE - "sprawdz"; puste gniazdo daje znaczek z pustym napisem |
| 106 | stanowisko\ui\kandydaci.py:189 | `WidokPracyRano.ustaw` | status -> opis | OPIS_W_WIDOKU: rano_dwuznaczna; reszta z ST.status().opis | `opis = NR.OPIS_W_WIDOKU.get(zrodlo.status, "").format(wybierz=ST.PRZYCISKI["wybierz_kandydata"]) or ST.status(zrodlo.status).opis` | NIE |
| 107 | stanowisko\ui\kandydaci.py:208 | `WidokPracyRano.ustaw` | kuweta, zab, typ -> tekst | str | `linia.addWidget(etykieta(wartosc or NR.BRAK_DANYCH, "duzy", f"praca_rano_{klucz}"))` | NIE |
| 108 | stanowisko\ui\kandydaci.py:214 | `WidokPracyRano.ustaw` | decyzja -> nazwa | wybor_kandydata, przypisanie_reczne | `opis = NR.DECYZJE.get(praca.decyzja, praca.decyzja)` | NIE - surowy kod |
| 109 | stanowisko\ui\kandydaci.py:219 | `WidokPracyRano.ustaw` | przypisanie "auto" -> "Przypisanie: program (dopasowanie pewne)." (l.220) | "auto"; inne wartosci i None nic nie pokazuja | `elif praca.przypisanie == "auto":` | TAK - napis zalezy tylko od `przypisanie == "auto"` (session_rano.py:799), nie od klasy. Pojawia sie tez przy klasie konflikt, poprawka i do_powtorzenia, gdy projekt jest znany, a decyzji nie ma. |
| 110 | stanowisko\ui\kandydaci.py:225 | `WidokPracyRano.ustaw` | poprawka i zlecenie_odhaczone -> napis informacyjny | klasa "poprawka" | `u.addWidget(etykieta(NR.POPRAWKA_INFO if praca.zlecenie_odhaczone else NR.JUZ_ROZPOZNANY_INFO, "informacja", ...` | NIE |
| 111 | stanowisko\ui\kandydaci.py:229 | `WidokPracyRano.ustaw` | kuweta_do_sprawdzenia -> napis uwaga | bool | `if praca.kuweta_do_sprawdzenia:` | NIE |
| 112 | stanowisko\ui\kandydaci.py:233 | `WidokPracyRano.ustaw` | stan pieca i skanu -> powod braku decyzji | piec otwarty, zamkniety | `powod = NR.POWOD_PIEC_ZAMKNIETY if not otwarty_piec else NR.POWOD_SKAN.format(napis=plytka.napis)` | NIE |
| 113 | stanowisko\ui\kandydaci.py:239 | `WidokPracyRano.ustaw` | klasa -> czy pokazac karty kandydatow | dwuznaczna, konflikt, nieznana albo jest decyzja | `if praca.kandydaci and praca.klasa in ("dwuznaczna", "konflikt", "nieznana") or (...)` | NIEJASNE - nieznana klasa bez decyzji nie dostaje kart |
| 114 | stanowisko\ui\kandydaci.py:245 | `WidokPracyRano.ustaw` | kandydat rowny projektowi pracy -> "wybrany" | bool | `przypisany=k.projekt_id is not None and k.projekt_id == praca.projekt_id,` | NIEJASNE - "wybrany" pojawia sie tez przy przypisaniu automatycznym, np. przy klasie konflikt bez decyzji osoby |
| 115 | stanowisko\ui\kandydaci.py:298 | `WidokPracyRano._dodaj_przypisanie` | stan punktu projektu -> tekst | 5 kluczy STANY_PUNKTU | `stan=ST.STANY_PUNKTU.get(projekt.stan, projekt.stan or ""))` | NIE - surowy kod albo ""; kontroler podstawia "oczekuje" za None (kontroler_api.py:3970) |
| 116 | stanowisko\ui\napisy_rano.py:58 | (stala) | stan kuwety "czeka" -> tekst | - | `KUWETA_STAN_CZEKA = ""` | NIEJASNE - pusta komorka (uzycie: ekran_rano.py:259) |
| 117 | stanowisko\ui\napisy_rano.py:196 | `dla_technika` | tekst z modulu excel -> tekst dla osoby | dowolny | `if not t:` (dalej `return ""`) | NIEJASNE - brak tekstu |
| 118 | stanowisko\ui\okno_excela.py:67 | `wymaga_wskazania` | klasa i do_sprawdzenia -> czy osoba ma wskazac wiersz | "wskaz_wiersz" (lokalny literal, l.31) albo do_sprawdzenia | `return p.klasa == KLASA_WSKAZ or p.do_sprawdzenia` | TAK - klasa nieznana, None albo "" dziala jak jeden_wiersz: przycisk "Zatwierdz wiersz N" bez wskazania (l.182, l.292) |
| 119 | stanowisko\ui\okno_excela.py:182 | `PanelExcela._cel` | pozycja -> wiersz celu zapisu | wiersz wskazany przez osobe (l.180-181) | `return None if wymaga_wskazania(p) else p.wiersz` | TAK - jak wiersz 118 |
| 120 | stanowisko\ui\okno_excela.py:219 | `PanelExcela.ustaw` | zalatwiona -> pokazana pozycja | pierwsza niezalatwiona | `nastepna = next((p for p in pozycje if not p.zalatwiona), None) or (pozycje[0] if pozycje else None)` | NIE |
| 121 | stanowisko\ui\okno_excela.py:232 | `PanelExcela.ustaw` | tryb Excela -> zdanie o trybie | pytaj, cien (napisy_rano.py:153-154) | `NR.EXCEL_TRYB.get(ex.tryb, "")` | NIEJASNE - nieznany tryb nie ma zdania (pusty tekst odfiltrowany, l.238) |
| 122 | stanowisko\ui\okno_excela.py:233 | `PanelExcela.ustaw` | do_zalatwienia -> "Do zatwierdzenia: n z razem" | int | `NR.EXCEL_ZOSTALO.format(n=ex.do_zalatwienia, razem=len(pozycje))` | NIEJASNE - wartosc domyslna 0 w StanExcel daje "0 z N"; kontroler_api.py:2970 podaje te liczbe jawnie |
| 123 | stanowisko\ui\okno_excela.py:240 | `PanelExcela.ustaw` | blad -> widocznosc etykiety bledu | tekst | `self.blad.setVisible(bool(ex.blad))` | NIEJASNE - None albo "" ukrywa etykiete, jak przy braku bledu |
| 124 | stanowisko\ui\okno_excela.py:250 | `PanelExcela.ustaw` | klasa -> kolumna "Propozycja" | jeden_wiersz, juz_odhaczone, wskaz_wiersz (napisy_rano.py:156-157) | `propozycja = NR.EXCEL_PROPOZYCJA.get(p.klasa, p.klasa).format(wiersz=p.wiersz, n=p.kandydatow)` | NIEJASNE - nieznana klasa jako surowy napis; "" daje pusta komorke |
| 125 | stanowisko\ui\okno_excela.py:251 | `PanelExcela.ustaw` | do_sprawdzenia i poprzedni_blad -> kolumna "Uwagi" | True daje "SPRAWDZ" albo "poprzednio blad" | `uwagi = " ".join(x for x in (NR.EXCEL_UWAGA_SPRAWDZ if p.do_sprawdzenia else "", ...) if x)` | NIEJASNE - wartosc falsy daje pusta komorke |
| 126 | stanowisko\ui\okno_excela.py:253 | `PanelExcela.ustaw` | zalatwiona i wynik -> kolumna "Stan" | None daje "do zatwierdzenia"; zapisano, juz_odhaczone, wskazano_recznie, pominieto, tylko_log, blad, "zapisano bez logu CSV" (napisy_rano.py:160-161) | `NR.EXCEL_STANY.get(p.wynik, p.wynik or "") if p.zalatwiona or p.wynik else NR.EXCEL_STANY[None]])` | NIEJASNE - nieznany wynik jako surowy napis; zalatwiona z wynikiem "" daje pusta komorke |
| 127 | stanowisko\ui\okno_excela.py:268 | `PanelExcela.ustaw` | powod -> etykieta | tekst | `self.powod.setText(NR.dla_technika(p.powod) if p is not None else "")` | NIEJASNE - None albo "" daje pusty tekst |
| 128 | stanowisko\ui\okno_excela.py:269 | `PanelExcela.ustaw` | do_sprawdzenia -> etykieta "SPRAWDZ: ..." | True i pozycja niezalatwiona | `self.sprawdz.setVisible(p is not None and p.do_sprawdzenia and not p.zalatwiona)` | NIEJASNE - wartosc falsy daje brak ostrzezenia |
| 129 | stanowisko\ui\okno_excela.py:272 | `PanelExcela.ustaw` | poprzedni blad i wiersz -> etykieta | z wierszem albo bez | `... if w else NR.EXCEL_POPRZEDNI_BLAD_BEZ_WIERSZA)` | NIE |
| 130 | stanowisko\ui\okno_excela.py:278 | `PanelExcela.ustaw` | kolor B kandydata -> kolumna "Pole B" | zielone daje "zielone", inny kolor daje "inny kolor" | `pole = NR.EXCEL_POLE_ZIELONE if x.zielone else (NR.EXCEL_POLE_INNE if x.kolor_b else "")` | NIE - None daje pusta komorke (nieodhaczone) |
| 131 | stanowisko\ui\okno_excela.py:279 | `PanelExcela.ustaw` | wiersz proponowany -> strzalka przy kandydacie | x.wiersz == p.wiersz | `NR.EXCEL_PROPONOWANY if p is not None and x.wiersz == p.wiersz else ''` | NIE |
| 132 | stanowisko\ui\okno_excela.py:288 | `PanelExcela.ustaw` | stan pozycji -> aktywnosc przyciskow | - | `do_zapisu = osoba and self._wybrana and p is not None and not p.zalatwiona and p.zlecenie_id is not None` | NIE |
| 133 | stanowisko\ui\okno_excela.py:292 | `PanelExcela.ustaw` | cel -> tekst przycisku | int | `self.zatwierdz.setText(NR.EXCEL_ZATWIERDZ.format(wiersz=cel) if cel is not None else NR.EXCEL_ZATWIERDZ_WYBIERZ)` | NIE |
| 134 | stanowisko\ui\okno_excela.py:193 | `PanelExcela._zatwierdz` | stan pozycji -> wyslanie polecenia | - | `if not self._wybrana or p is None or p.zalatwiona or cel is None or p.zlecenie_id is None:` | NIE - cichy powrot (to samo dla `_pomin`, l.204) |
| 135 | stanowisko\excel_com.py:137 | `ArkuszCom.wypelnienie` | wypelnienie komorki B -> (R,G,B) albo None | ColorIndex -4142 daje None (l.135-136) | `return kolor_na_rgb(wnetrze.Color)` | NIE - kazdy inny ColorIndex daje kolor; za zielony uznaje sie tylko kolor rowny konf.kolor |
| 136 | stanowisko\excel_com.py:142 | `ArkuszCom.ustaw_wypelnienie` | kolor -> Interior.Color komorki B (jedyny zapis do arkusza) | tylko konf.kolor (excel.py:879) | `self._arkusz().Cells(nr, kolumna).Interior.Color = rgb_na_kolor(rgb)` | NIE - brak galezi domyslnej |
| 137 | stanowisko\excel.py:448 | `dopasuj.kolor_b` | wypelnienie B -> "bez koloru" albo kolor | None i bialy daja None | `return None if c is None or tuple(c) == BIALY else tuple(c)` | NIE - brak i bialy oznaczaja nieodhaczone |
| 138 | stanowisko\excel.py:677 | `Excel._kolor_b` | to samo przy zatwierdzaniu (l.862, 884, 906) | j.w. | `return None if c is None or tuple(c) == BIALY else tuple(c)` | NIE |
| 139 | stanowisko\excel.py:467 | `dopasuj.wybierz` | kolor B nowszych wierszy -> "nowszy nieodhaczony" | kolor rowny konf.kolor oznacza odhaczony | `nowsze = [x.nr for x in wiersze_grupy if x.nr != w.nr and _nowszy(x, w) and kolor_b(x.nr) != kolor]` | NIE - None, bialy i inny kolor licza sie jako nieodhaczone |
| 140 | stanowisko\excel.py:477 | `dopasuj.wybierz` | kolor B wybranego wiersza -> klasa | None daje jeden_wiersz (l.473); kolor rowny konf.kolor daje juz_odhaczone (l.475) | `return wskaz(kandydaci, f"pole B wiersza {w.nr} ma inne wypelnienie niz zielone - program go nie nadpisuje")` | NIE - inny kolor daje "wskaz wiersz" |
| 141 | stanowisko\excel.py:479 | `dopasuj` | pusta kuweta -> klasa | None, "" | `if not kuweta:` (l.480 `return wskaz((), ...)`) | NIE |
| 142 | stanowisko\excel.py:508 | `dopasuj` | kolory B wierszy z nazwa jak folder -> otwarte albo wszystkie zielone | kolor rowny albo rozny od konf.kolor | `otwarte = [w for w in zgodne if kolor_b(w.nr) != kolor]` | NIE |
| 143 | stanowisko\excel.py:523 | `dopasuj` | zadna regula nie pasuje -> klasa | jeden_wiersz, juz_odhaczone, wskaz_wiersz | `return wskaz(kand, f"H nie pasuje, a najnowszy wiersz kuwety {k} nie ma w H nazwiska z folderu (inna osoba albo same inicjaly)")` | NIE - "wskaz wiersz" |
| 144 | stanowisko\excel.py:397 | `Dopasowanie` (pole) | do_sprawdzenia -> "SPRAWDZ" w oknie i blokada automatycznego wpisu | True, False | `do_sprawdzenia: bool = False` | NIEJASNE - False daje brak ostrzezenia; wartosc domyslna jest uzyta tylko w `wskaz()` (l.451) i w pozycji bledu (l.736), obie z klasa wskaz_wiersz |
| 145 | stanowisko\excel.py:548 | `Pozycja` (pole) | zalatwiona -> kolumna "Stan" w oknie (przez kontroler_api.py:2958) | True, False; `stan` = WYNIK_* | `zalatwiona: bool = False` | NIE - okno pokazuje "do zatwierdzenia" |
| 146 | stanowisko\excel.py:564 | `Pozycja.kandydaci_do_okna` | kolor B kandydata -> "wypelnienie_b" -> okno "Pole B" | surowe RGB albo None | `"wypelnienie_b": self.wypelnienia.get(nr), "wartosci": w})` | NIE - brak daje puste "Pole B". Bialy jest tu pokazany jako "inny kolor", choc l.448 i l.677 traktuja bialy jak brak koloru. |
| 147 | stanowisko\excel.py:690 | `Excel._sprawdz_piec` | stan pieca -> zgoda na zapis (X4) | piec zamkniety; niezamkniety albo brak wiersza daje odmowe (l.693-694) | `if sesja_pieca_id is None or self.baza is None:` (dalej `return`) | TAK - sesja None albo baza None przepuszcza kontrole bez odmowy. Sesje None blokuje dopiero `zatwierdz` (l.835-836); przy bazie None drugiej kontroli nie ma. |
| 148 | stanowisko\excel.py:725 | `Excel.propozycje` | wynik_pieca["zamknieto"] -> dopuszczenie propozycji | wartosc truthy | `if not wynik_pieca or not wynik_pieca.get("zamknieto"):` | NIE - None, "" i brak klucza daja BladExcela |
| 149 | stanowisko\excel.py:731 | `Excel.propozycje` | lista kompletnych zlecen -> pozycje do odhaczenia | slowniki z "zlecenie_id" | `for z in wynik_pieca.get("kompletne", []):` | NIEJASNE - brak klucza daje 0 pozycji bez komunikatu |
| 150 | stanowisko\excel.py:736 | `Excel.propozycje` | blad jednego zlecenia -> pozycja | BladExcela | `d = Dopasowanie(KLASA_WSKAZ_WIERSZ, None, 5, (), f"blad: {e} - zlecenie do sprawdzenia recznie")` | NIE |
| 151 | stanowisko\excel.py:787 | `Excel._loguj` | pola wpisu -> log_excel.csv (nie arkusz) | POLA_LOGU | `self._dopisz_csv(["" if csv_wpis[k] is None else csv_wpis[k] for k in POLA_LOGU])` | NIEJASNE - None daje puste pole CSV |
| 152 | stanowisko\excel.py:803 | `Excel._loguj` | wynik wpisu -> Pozycja.stan | WYNIK_* | `pozycja.stan = wynik` | NIE - brak galezi domyslnej |
| 153 | stanowisko\excel.py:804 | `Excel._loguj` | klasa w wyniku dla programu | klasa jawna albo z dopasowania | `"klasa": klasa or pozycja.dopasowanie.klasa` | NIE |
| 154 | stanowisko\excel.py:827 | `Excel.zatwierdz` | klasa (bez wskazanego wiersza) -> sciezka zapisu | wskaz_wiersz daje odmowe (l.825-826) | `nr, wynik_zapisu, regula = d.wiersz, WYNIK_ZAPISANO, d.regula` | TAK - kazda klasa inna niz wskaz_wiersz, takze spoza KLASY, idzie sciezka zapisu "zapisano". Klasa pochodzi z `dopasuj` (zamknieta lista), a l.871 porownuje ja z propozycja policzona od nowa. |
| 155 | stanowisko\excel.py:832 | `Excel.zatwierdz` | wskazany wiersz -> wynik | wiersz rowny d.wiersz i klasa inna niz wskaz daje zapisano | `wynik_zapisu, regula = (WYNIK_ZAPISANO, d.regula) if (...) else (WYNIK_WSKAZANO, 5)` | NIE |
| 156 | stanowisko\excel.py:833 | `Excel.zatwierdz` | klasa -> czy kontrola X4 | juz_odhaczone na proponowanym wierszu pomija X4 | `moze_zapisac = not (d.klasa == KLASA_JUZ_ODHACZONE and nr == d.wiersz)` | NIE - domyslnie kontrola X4 jest wykonywana |
| 157 | stanowisko\excel.py:842 | `zatwierdz.odmowa` | odmowa -> wpis "blad" i stan "blad" | - | `self._loguj(pozycja, osoba, nr, regula, WYNIK_BLAD)` | NIEJASNE - gdy wpis sie nie uda, stan zostaje poprzedni (np. None) i okno moze pokazac "do zatwierdzenia" |
| 158 | stanowisko\excel.py:867 | `Excel.zatwierdz` | kolor B na swiezym odczycie -> decyzja | rowny konf.kolor daje juz_odhaczone (l.865-866); inny daje odmowe (l.868); None daje zapis | `if c is not None:` | NIE |
| 159 | stanowisko\excel.py:874 | `Excel.zatwierdz` | tryb -> zapis albo tylko log | "cien" | `if self.tryb == TRYB_CIEN:` | NIE - inny tryb oznacza zapis; tryb sprawdzony w l.265-266 |
| 160 | stanowisko\excel.py:889 | `Excel.zatwierdz` | kolor po bledzie COM -> decyzja | rowny konf.kolor: jak zapis; inny: blad (l.891-894); None: ponowienie | `if po_bledzie == self.konf.kolor:` | NIEJASNE - zielona komorka po bledzie wywolania konczy sie "zapisano" po kontroli wierszy |
| 161 | stanowisko\excel.py:912 | `Excel.zatwierdz` | kolor po zapisie -> wynik | rowny konf.kolor daje zapisano albo wskazano_recznie | `if kolor_po != self.konf.kolor:` | NIE |
| 162 | stanowisko\excel.py:923 | `Excel._zalatw` | blad wpisu logu -> zalatwiona i stan | zapisano_kolor daje "zapisano bez logu CSV" (l.922) | `pozycja.zalatwiona = pozycja.zalatwiona or zapisano_kolor` | NIE |
| 163 | stanowisko\excel.py:934 | `Excel.zaloguj_juz_odhaczone` | do_sprawdzenia -> wpis bez czlowieka | klasa juz_odhaczone (l.932) | `if pozycja.dopasowanie.do_sprawdzenia:` | NIEJASNE - wartosc falsy daje wpis bez pytania; dla juz_odhaczone pole jest ustawiane jawnie (l.475-476) |
| 164 | stanowisko\excel.py:961 | `Excel.zapisz_cien` | klasa -> wpis cienia | wskaz_wiersz daje tylko_log bez wiersza (l.959) | `wpisy.append(self.zatwierdz(p, osoba))` | NIEJASNE - kazda inna klasa idzie przez `zatwierdz` |
| 165 | stanowisko\excel.py:987 | `Excel.zapisz_cien_bez_odczytu` | klasa -> wpis | wskaz daje tylko_log bez wiersza (l.983); juz_odhaczone daje juz_odhaczone (l.985) | `wpisy.append(self._zalatw(p, osoba, d.wiersz, d.regula, WYNIK_TYLKO_LOG))` | NIEJASNE - klasa spoza listy dostaje ten sam wpis co pewna propozycja (tylko_log z wierszem); arkusz sie nie zmienia |
| 166 | stanowisko\excel.py:963 | `Excel.zapisz_cien` | wyjatek -> wynik | BladExcela | `wpisy.append({"id": None, "kuweta": p.kuweta, "wiersz": p.dopasowanie.wiersz, "klasa": p.dopasowanie.klasa, "wynik": WYNIK_BLAD,` | NIE - inne wyjatki nie sa lapane |
| 167 | stanowisko\excel.py:1005 | `Excel.zaloguj_poprawki` | poprawka -> wpis | kazda | `wpisy.append(self._zalatw(p, osoba, p.dopasowanie.wiersz, p.dopasowanie.regula, WYNIK_TYLKO_LOG))` | NIEJASNE - zawsze tylko_log; dla klasy wskaz wiersz jest None |
| 168 | stanowisko\excel.py:296 | `Konfiguracja.z_ustawien` | brak klucza tryb -> tryb | pytaj, cien; wartosc spoza listy daje BladExcela (l.266) | `tryb=e.get("tryb", TRYB_PYTAJ)` | NIE |
| 169 | ramka\obraz.py:22 | `KOLORY` (modul) | nazwa koloru gniazda -> RGB | czerwony, zielony, zolty, bursztyn, bialy, niebieski, fioletowy, szary | brak domyslnej; uzycie bez .get: `k.blok(x, y, w, h, obraz.KOLORY[g.kolor])` (logika.py:583) | NIE - brak domyslnej. Zielony (0,255,0) ma ten sam RGB co pierscien "wynik" i ikona "lacznosc" (l.38, l.42). Szary, niebieski i fioletowy sa przyjmowane, choc kolumna `ramka` w statusy.py ich nie uzywa. |
| 170 | ramka\obraz.py:34 | `KOLORY_STANU` (modul) | stan ramki -> RGB pierscienia i ikony | gotowa, skanowanie, analiza, wynik, blad, brak_planu, brak_lacznosci, lacznosc | brak domyslnej; indeksowanie [] (logika.py:591, 592, 595, 596) | NIEJASNE - "wynik" i "lacznosc" maja (0,255,0); patrz wiersze 181 i 189 |
| 171 | ramka\protokol.py:38 | (modul) | lista dozwolonych kolorow (laptop ja importuje) | klucze obraz.KOLORY | `KOLORY_GNIAZD = tuple(obraz.KOLORY)` | NIE |
| 172 | ramka\protokol.py:223 | `_sprawdz_gniazda` | walidacja pola kolor | klucze obraz.KOLORY; wielkosc liter ma znaczenie | `if not isinstance(g["kolor"], str) or g["kolor"] not in obraz.KOLORY:` | NIE - None, "", "bursztynowy", "pomaranczowy" i "zatwierdzona_ok" odrzucaja caly plan (400 zly_kolor), wiec zaden blok nie swieci |
| 173 | ramka\protokol.py:209 | `_sprawdz_gniazda` | brak klucza "kolor" albo nieznane pole | wymagane: id, px, kolor; opcjonalne: kuweta | `_obiekt(g, sg, ("id", "px", "kolor"), ("kuweta",))` | NIE - caly plan jest odrzucany |
| 174 | ramka\protokol.py:202 | `_sprawdz_gniazda` | pusta lista gniazd plytki | 0..48 gniazd, bez minimum | `_lista(lista, sciezka, MAX_GNIAZD_PLYTKI, "za_duzo_gniazd")` | TAK - plan z `{"gniazda": []}` jest przyjmowany. Ramka pokazuje stan "wynik" z zielonym pierscieniem (logika.py:576) i napisem: numer plytki (W) albo "OK" (P). Zadne gniazdo nie swieci. |
| 175 | ramka\protokol.py:299 | `sprawdz_plan` | kuweta przy gniezdzie | rano kuweta z plan.kuwety | `if g.kuweta is not None and g.kuweta not in znane:` | NIE - caly plan jest odrzucany |
| 176 | ramka\protokol.py:277 | `sprawdz_plan` | numer plytki | W: 1-3, P: 4-6 | `if n not in rodzina:` | NIE - caly plan jest odrzucany |
| 177 | ramka\protokol.py:347 | `sprawdz_tryb` | stan z PUT /tryb (kolor pierscienia) | gotowa, skanowanie, analiza, blad, test_led | `if not isinstance(d["stan"], str) or d["stan"] not in STANY_TRYBU:` | NIE - odrzucenie gasi obraz |
| 178 | ramka\logika.py:226 | `LogikaRamki._po_odrzuceniu` | odrzucenie planu -> zgaszenie obrazu | gasza kody spoza KODY_BEZ_ZMIANY_OBRAZU | `self._zgas(teraz, None, "odrzucenie", kod=blad.kod)` | NIEJASNE - gdy plan wyslal wlasciciel, obraz gasnie. W przypadkach z l.221 i l.224-225 zostaje poprzedni obraz w dowolnym kolorze, takze zielony. |
| 179 | ramka\logika.py:583 | `LogikaRamki.obraz` | kolor gniazda -> RGB bloku | klucze obraz.KOLORY | `k.blok(x, y, w, h, obraz.KOLORY[g.kolor])` | NIE - brak domyslnej; po walidacji KeyError nie wystepuje |
| 180 | ramka\logika.py:580 | `LogikaRamki.obraz` | ktore gniazda swieca | W: wszystkie gniazda planu; P: kuweta None albo kuweta biezaca i niepotwierdzona | `if self.rola == "W" or g.kuweta is None or` | NIEJASNE - rano gniazdo innej albo potwierdzonej kuwety jest ciemne, takze czerwone i zolte z kuweta. Gniazdo bez kuwety swieci zawsze. |
| 181 | ramka\logika.py:576 | `LogikaRamki.obraz` | stan "wynik" -> pierscien (obraz.py:38 = (0,255,0)) | blad, skanowanie, analiza, gotowa, brak_planu, wynik | `stan_k = "wynik"` | TAK - pierscien jest zielony niezaleznie od kolorow gniazd, takze przy samych czerwonych i przy pustej liscie gniazd |
| 182 | ramka\logika.py:573 | `LogikaRamki.obraz` | plan plytki jest, ale tryb inny niz wynik | - | `elif self.tryb != "wynik":` (l.574 `stan_k = "gotowa"`) | NIE - niebieski pierscien, gniazda ciemne |
| 183 | ramka\logika.py:568 | `LogikaRamki.obraz` | brak plytki, odczyt niepewny albo awaria (p == 0) | - | `elif p == 0:` | NIE - "gotowa", gniazda ciemne |
| 184 | ramka\logika.py:570 | `LogikaRamki.obraz` | plytka bez planu albo plan niewazny | - | `elif not ma_plan_plytki:` (l.572 `tekst = f"{p} BRAK"`) | NIE - pierscien (255,60,0) |
| 185 | ramka\logika.py:563 | `LogikaRamki.obraz` | awaria albo tryb blad | - | `if self.awaria or self.tryb == "blad":` | NIE - czerwony pierscien, napis "BLAD" |
| 186 | ramka\logika.py:566 | `LogikaRamki.obraz` | skanowanie albo analiza | - | `elif self.tryb in ("skanowanie", "analiza"):` | NIE |
| 187 | ramka\logika.py:554 | `LogikaRamki.obraz` | test_led -> cala matryca | KOLORY_TEST_LED (obraz.py:45): czerwony, zielony, niebieski, bialy | `if self.tryb == "test_led" and teraz - self.tryb_od < CZAS_TEST_LED_S:` | NIEJASNE - przez 1 s z kazdych 4 s cala matryca ma (0,255,0); test uruchamia tylko PUT /tryb test_led, ktory usuwa plan |
| 188 | ramka\logika.py:594 | `LogikaRamki.obraz` | brak lacznosci -> miganie | lacznosc True, False | `if int(teraz * 2.0) % 2 == 0:` | NIE - czerwony pierscien; gniazda swieca dalej, dopoki plan jest wazny |
| 189 | ramka\logika.py:592 | `LogikaRamki.obraz` | lacznosc -> ikona 3x3 | - | `obraz.rysuj_ikone(k, obraz.KOLORY_STANU["lacznosc"])` | NIEJASNE - ikona jest zielona (0,255,0) przy kazdej lacznosci, takze przy "BLAD", "BRAK" i czerwonych gniazdach |
| 190 | ramka\logika.py:543 | `LogikaRamki._tekst_przod_rano` | brak biezacej kuwety -> napis z przodu ramki P | wpisywane cyfry, komunikat, "-"+brak, "OK", "kuweta liczba" | `return "OK", []` | TAK - "OK" pojawia sie, gdy `biezaca_kuweta()` jest None i `plan.braki` jest puste. Tak jest takze wtedy, gdy swieca gniazda bez kuwety (bialy, zolty, czerwony) albo lista gniazd jest pusta. |
| 191 | ramka\logika.py:542 | `LogikaRamki._tekst_przod_rano` | braki -> napis zmieniany co 2 s | plan.braki | `return "-" + self.plan.braki[i], []` | NIE |
| 192 | ramka\logika.py:549 | `LogikaRamki._tekst_przod_rano` | biezaca kuweta -> napis | - | `return (f"{kuw} {liczba}" if liczba else kuw), inne` | NIE |
| 193 | ramka\logika.py:587 | `LogikaRamki.obraz` | ramka W w stanie wynik -> napis | - | `tekst = str(p)` | NIE - tylko numer plytki |
| 194 | ramka\logika.py:589 | `LogikaRamki.obraz` | pytanie "Zamknij piec" -> napis | - | `tekst, inne = "PIEC?", []` | NIE |
| 195 | ramka\logika.py:486 | `LogikaRamki.klawisz` | wpisana nieznana kuweta -> komunikat | - | `self.komunikat = "?" + tekst` | NIE |
| 196 | ramka\logika.py:369 | `LogikaRamki.ustaw_plytke` | ramka W: zdjecie plytki kasuje jej wynik | KASUJ_PO_ZDJECIU_ROLI: W True, P False | `del self.plan.plytki[stara]` | NIE - po powrocie plytki "{p} BRAK" |
| 197 | ramka\logika.py:164 | `LogikaRamki.tick` | wygasniecie planu | - | `self._wyczysc_stan_planu()` | NIE - stan "gotowa", gniazda ciemne |
| 198 | ramka\czcionka.py:48 | `glif` | znak -> glif | 0-9, A B C D E I K L N O P R S, # - _ ? : spacja | `return ZNAKI.get(znak.upper(), ZNAKI["?"])` | NIE |
| 199 | ramka\obraz.py:147 | `rysuj_tekst_przod` | pusty napis | - | `if not tekst:` | NIE - nic nie jest rysowane |
| 200 | ramka\kalibracja.py:241 | `gniazda_planu` | kolor -> pole planu (funkcja pomocnicza, uzywana tylko w testach) | dowolny | `g = {"id": int(gid), "px": blok(kal, rola, uklad, gid), "kolor": wpis["kolor"]}` | NIE - kolor bez walidacji; ramka i tak odrzuci plan (protokol.py:223) |
| 201 | ramka\test_led.py:32 | `klatka_gniazda` | narzedzie testowe: kolor bloku | KOLORY | `def klatka_gniazda(blok, nr: int, kolor: str = "bialy") -> obraz.Klatka:` | NIE - narzedzie, nie wynik |
| 202 | ramka\test_led.py:24 | (modul) | narzedzie testowe: kolory naprzemienne | zielony, czerwony, niebieski, zolty | `KOLORY_NAPRZEMIENNE = ("zielony", "czerwony", "niebieski", "zolty")` | NIEJASNE - co czwarte gniazdo jest zielone, ale tylko w `python -m ramka.test_led --wszystkie` |
| 203 | ramka\program.py:164 | `Program._awaria` | wyjatek w petli -> klatka | - | `klatka = obraz.Klatka()` | NIE - czarna klatka; gdy pokaz zawiedzie, `self.sprzet.wygas()` (l.183) |

Bez mapowania statusu na kolor albo tekst (przeczytane, brak wierszy):
- ramka\sprzet_rpi.py - RGB idzie bez zmian; l.105 ogranicza tylko jasnosc;
- ramka\sprzet_atrapa.py - l.58 daje (0,0,0) przy braku klatki;
- ramka\sprzet.py - l.38 wygas = czarna klatka;
- ramka\serwer.py - zly JSON albo parametr idzie do program.odrzucenie (gaszenie);
- ramka\__init__.py, ramka\__main__.py;
- stanowisko\ui\napisy.py - same stale napisow, uzyte w wierszach 44, 61, 68.

## (a) Stale statusow zdefiniowane w stanowisko\statusy.py

Ogolny fakt: klucze statusow gniazda i pracy nie maja stalych typu `STATUS_ZIELONY`. Sa literalami w wywolaniach `_s(...)` i dalej sa uzywane jako napisy.

Klasy koloru pracy:
- statusy.py:24 `KOLOR_ZIELONY = "zielony"`;
- statusy.py:25 `KOLOR_CZERWONY = "czerwony"`;
- statusy.py:26 `KOLOR_ZOLTY = "zolty"`;
- statusy.py:27 `KOLOR_SZARY = "szary"`;
- statusy.py:28 `KOLOR_POMARANCZOWY = "pomaranczowy"`;
- statusy.py:29 `KOLOR_ZATWIERDZONA_OK = "zatwierdzona_ok"`;
- statusy.py:30 `KOLOR_BURSZTYNOWY = "bursztynowy"`;
- statusy.py:31 `KOLOR_BIALY = "bialy"`;
- statusy.py:32 `KOLORY_PRACY` - szesc klas, bez BURSZTYNOWY i BIALY.

Klucze tabeli `STATUSY` (statusy.py:93):

| linia | klucz |
|---|---|
| 58 | zielony |
| 59 | czerwony |
| 61 | ukruszona |
| 62 | zatwierdzona_ok |
| 64 | zolty |
| 65 | sprawdz_ulozenie |
| 66 | popraw_ulozenie |
| 67 | skan_ponownie |
| 68 | skan_do_powtorzenia |
| 70 | nie_sprawdzono |
| 72 | blad_inspekcji |
| 74 | szary |
| 76 | pomaranczowy |
| 78 | dofrezowany |
| 81 | nieznana_rano |
| 84 | pusty |
| 85 | podwojny |
| 86 | poza_gniazdem |
| 87 | czeka_na_numer |
| 89 | plytka_nie_z_trybu |
| 90 | nieaktywny |
| 91 | nieznany |

Klucze tabeli `STATUSY_RANO_WIERSZE` (statusy.py:113):
- statusy.py:102 rano_pewna;
- statusy.py:103 rano_przypisana;
- statusy.py:105 rano_dwuznaczna;
- statusy.py:107 rano_konflikt;
- statusy.py:110 rano_juz_rozpoznany.

Pozostale stale statusow:

| linia | stala | zawartosc |
|---|---|---|
| 114-117 | `STATUSY_RANO` | klasa poranna -> wiersz; klucze sa literalami, nie session_rano.KLASA_* |
| 118 | `KLASY_RANO_Z_KUWETA` | - |
| 120 | `STATUSY_ZIELONE` | tylko klucze z kolorem KOLOR_ZIELONY, czyli ("zielony",) |
| 122-123 | `ZOLTE_WG_INSPEKCJI` | - |
| 126 | `INSPEKCJA_ZIELONA = "ok"` | - |
| 127 | `INSPEKCJE_NIESPRAWDZONE = (None, "pominieto", "nie_sprawdzono")` | - |
| 128 | `DOPASOWANIA_ZIELONE = ("zielony", "zolty")` | - |
| 129 | `STATUSY_SKANU_AKTYWNE = ("przyjety", "do_powtorzenia")` | kopia session.STATUSY_AKTYWNE |
| 131-132 | `STATUS_WG_KOLORU` | - |
| 133 | `DECYZJE_UKRUSZENIA = ("ukruszona", "ukruszona_niewykryta")` | - |
| 137 | `ZIELONE_BEZ_NUMERU_PLYTKI = False` | - |
| 207-214 | `STATUSY_PLYTKI` | przyjety, do_powtorzenia, zastapiony, niezgodny_uklad, plytka_nie_z_trybu, blad |
| 267 | `KOMUNIKATY_DO_PONOWIENIA` | - |
| 280-281 | `POWODY_ZAMKNIECIA` | - |
| 282 | `POWOD_DOFREZOWANIE` | - |
| 291 | `NAPIS_POMINIETEJ` | - |
| 295-296 | `STANY_PUNKTU` | oczekuje, do_dofrezowania, brak_po_piecu, rozpoznany, zamkniety_recznie |
| 312 | `POZIOM_INFO`, `POZIOM_OSTRZEZENIE`, `POZIOM_BLAD` | - |
| 325 | `KOMUNIKATY` | - |
| 495-505 | `BLEDY_RAMEK` | - |
| 507 | `RAMKA_KTOREJ` | - |
| 529 | `NAPISY_NIEZAPISANE` | - |
| 531 | `PYTANIA` | - |
| 555 | `JAKA_PLYTKA` | - |
| 556 | `NAZWY_TRYBOW` | - |
| 557 | `POWODY_POWTORZENIA` | - |
| 593 | `STANY_PULI` | - |
| 601 | `STANY_PULI_WPISOW` | - |
| 636 | `PODSTAWY_PONOWNEGO_SKANU` | - |

## (b) Status porownywany napisem-literalem zamiast stalej

stanowisko\statusy.py:
- l.164 `if status_skanu == "plytka_nie_z_trybu":`
- l.174 `if status_inspekcji == "nie_sprawdzono" and blad_inspekcji:`
- l.181 `if status_inspekcji == "nie_sprawdzono":`
- l.185 `if status_skanu == "do_powtorzenia" and status_gniazda == KOLOR_ZIELONY:`
- l.196 `if klucz == "czeka_na_numer":`
- l.201 `if klucz == "nieznany" and (...)`
- l.288 `if stan_punktu == "do_dofrezowania":`
- `status_pracy` (l.164-188) zwraca klucze jako literaly.

stanowisko\session.py:
- l.224 `if g.get("status") != "zolty":`
- l.412 `if g.get("status") != "szary":`
- l.465 `if k1 is not None and g.get("status") != "szary":`
- l.1107 `... and praca["status_match"] != "szary" else None`
- l.1121 `if decyzja == "ok":`
- l.1123 `if status_skanu == STATUS_DO_POWTORZENIA and status_gniazda == "zielony":`
- l.1124 `return "zolty"`

stanowisko\session_rano.py:
- l.581 `if praca["status_match"] != "zielony" or not sha:`
- l.56-57 `STATUS_KLASY` - wartosci sa literalami kluczy statusy;
- l.59 `STATUS_DWIE_PRACE = "podwojny"` i l.60 `STATUS_SPRAWDZ = "czerwony"` - kopie literalow, nie stale ze statusy.

stanowisko\ramka_protokol.py:
- l.33 `KOLOR_SPRAWDZ = "czerwony"` - kopia literalu.

stanowisko\indicate.py:
- kody bledu `_blad`: l.322, 540, 624, 723, 804, 886, 945, 997, 1144;
- tryb ramki: l.455, 495, 835, 852 (przypisanie "wynik"), 868, 896, 1065;
- typy zdarzen: l.797, 847, 854, 862, 866, 876, 884, 891, 894, 898, 908, 912;
- kody odpowiedzi ramki: l.1006, 1155, 1163, 1165, 1170, 1174, 1176, 1181, 1185.

stanowisko\ui\czesci.py:
- l.39 `SKAN_PRZYJETY = "przyjety"` - lokalna kopia;
- rodzaj pytania: l.222 i l.734 `== "ponowny_skan"`, l.739 `== "plytka_nie_z_trybu"`;
- stan puli: l.551, 552, 589;
- klucze stanu ramki: l.607, 613, 614;
- l.730 `odp.polecenie == "podaj_numer_plytki"`;
- rodzaj komunikatu: l.804, 808;
- l.1137 pary ("ukruszona", "ukruszona") i ("ok", "zatwierdzona_ok");
- decyzja: l.1252 `praca.decyzja == "ok"`, l.1253 `== "ukruszona_niewykryta"`;
- poziomy jako literaly zamiast ST.POZIOM_*: l.651, 755, 767, 795, 852, 909.

stanowisko\ui\okno.py:
- l.526 `nazwa == "podaj_numer_plytki" and (... odpowiedz.kod == "numer_nowy_wsad")`
- l.669 `q.rodzaj == "ponowny_skan"`
- l.753 klucze slownika `pytane`
- l.760 i l.762 `akcja == "podaj_numer_plytki"`
- l.784 `grupa[0].rodzaj != "konflikt_projektu"`
- l.815 `k.rodzaj == "nowa_zmiana"`
- l.821 `q.rodzaj == "brak_numeru_plytki"`
- l.851 `q.rodzaj != "brak_numeru_plytki"`
- l.202 i l.262 `styl_znaczka_poziomu("ostrzezenie", ...)`

stanowisko\ui\styl.py:
- l.29-33 klucze `POZIOMY` "info", "ostrzezenie", "blad" sa literalami, nie ST.POZIOM_*.

stanowisko\ui\ekran_rano.py:
- l.49 `KOLEJNOSC_KLAS` - literaly klas zamiast session_rano.KLASA_*;
- l.58 klucze `PYTANE`;
- l.677, 685, 780 `status == "zastapiony"` albo `!= "zastapiony"`;
- l.788 `g.status != "pusty"`;
- l.879 poziom "ostrzezenie";
- rodzaj komunikatu albo pytania: l.911, 917, 930.

stanowisko\ui\kandydaci.py:
- l.215 `praca.decyzja == "przypisanie_reczne"`
- l.219 `praca.przypisanie == "auto"`
- l.224 `praca.klasa == "poprawka"`
- l.239 `praca.klasa in ("dwuznaczna", "konflikt", "nieznana")`
- l.254 `praca.decyzja == "przypisanie_reczne"`

stanowisko\ui\napisy_rano.py - klucze slownikow wpisane recznie:
- l.66 "rano_dwuznaczna";
- l.72 "wybor_kandydata", "przypisanie_reczne";
- l.153-154 "pytaj", "cien";
- l.156-157 "jeden_wiersz", "juz_odhaczone", "wskaz_wiersz";
- l.160-161 m.in. "zapisano bez logu CSV".

stanowisko\ui\okno_excela.py:
- l.31 `KLASA_WSKAZ = "wskaz_wiersz"` - lokalna kopia excel.KLASA_WSKAZ_WIERSZ;
- l.67 porownanie z ta kopia.

stanowisko\excel.py, stanowisko\excel_com.py, stanowisko\ui\mapa.py, stanowisko\ui\mapa_rano.py, stanowisko\ui\obraz.py:
- statusy sa porownywane ze stalymi;
- w excel.py literalami sa tylko klucze slownikow wejsciowych: l.725, 727, 731, 997, 1004.

ramka\logika.py:
- tryb ramki: l.165, 169, 205, 292, 430, 554, 563, 566, 573 (literaly zamiast protokol.STANY);
- `stan_k` jako literal: l.564, 569, 571, 574, 576;
- indeks KOLORY_STANU: l.592, 595, 596;
- rola: l.403, 580, 584.

ramka\protokol.py:
- l.261 `rano = tryb == "rano"`.

ramka\test_led.py:
- l.24 i l.32 literaly kolorow.

## (c) Brak wyniku pomijany - nic sie nie rysuje, nie swieci albo nie wpisuje

Laptop - sesja i plan ramki:
- stanowisko\session.py:1164 `if kolor is not None:` - praca bez klasy koloru nie wchodzi do licznikow sesji.
- stanowisko\session_rano.py:806 `if aktywny:` - liczniki i listy liczone tylko ze skanow aktywnych.
- stanowisko\session_rano.py:1301-1302 `if not s["aktywny"]: continue` - skan nieaktywny nie trafia do planu ramki P.
- stanowisko\session_rano.py:1303-1308 - skan bez numeru, plytka poza ramka i skan wstrzymany trafiaja tylko do `pominiete`. Plytka nie ma obrazu, a ramka pokazuje "{p} BRAK".
- stanowisko\session_rano.py:1315-1316 `if n in zdublowane or len(po_numerze[n]) > 1: continue` - plytka z dwoma skanami nie ma obrazu.
- stanowisko\session_rano.py:1320-1321 `if p["gniazdo"] is None: poza += 1` - praca poza gniazdem jest tylko liczona, na ramce jej nie ma.
- stanowisko\ramka_protokol.py:117-119 - zle gniazdo (id spoza zakresu, duplikat) jest pomijane i tylko liczone.
- stanowisko\ramka_protokol.py:121-122 `if kolor is None: continue` - gniazdo nie swieci. Plytka, w ktorej wszystkie gniazda maja None, idzie z pusta lista gniazd.
- stanowisko\ramka_protokol.py:113-114 i :124-125 `return None` - brak kalibracji albo ukladu wylacza cala plytke.
- stanowisko\ramka_protokol.py:149-152 i :156-158 `continue` - plytka spoza rodziny albo bez kalibracji nie trafia do planu.

Laptop - klient ramki:
- stanowisko\indicate.py:491-496 - wynik bez numeru, zablokowany albo niewazny: `_wyniki.clear()` i ramka "gotowa" (ciemna).
- stanowisko\indicate.py:1033-1034 `if not wazne: return None` oraz :1038-1039 `if not plan["plytki"]: return None` - plan nie jest wysylany.
- stanowisko\indicate.py:786-787 `if nr <= self._kursor: continue` - zdarzenia juz odebrane sa pomijane.

Laptop - ekran wieczorny:
- stanowisko\ui\czesci.py:216-217 - prace z kolorem None, z decyzja albo bez "ukruszona" w dozwolone nie licza sie do "do obejrzenia".
- stanowisko\ui\czesci.py:840 `if n` - zerowe liczniki nie maja znaczka.
- stanowisko\ui\czesci.py:877 `if not self._liczniki and plytka.aktywna:` - skan nieaktywny bez licznikow nie dostaje ani licznikow, ani napisu.
- stanowisko\ui\czesci.py:1233 - pusty podpis ukrywa znaczek statusu w widoku pracy.
- stanowisko\ui\czesci.py:1394 `if g.prace and g.podpis:` - legenda pomija gniazda bez prac i bez podpisu.
- stanowisko\ui\czesci.py:605-606 `if x is None: continue` - ramka bez obiektu nie ma wpisu na pasku ramek.
- stanowisko\ui\mapa.py:119 - skan nieaktywny bez prac: zamiast gniazd napis "Plytka {napis}.".
- stanowisko\ui\mapa.py:241-243 `if g.id not in numery: continue` - gniazdo ukladu bez wpisu w stanie nie jest rysowane.
- stanowisko\ui\mapa.py:313-314 `if g.nr in self._ksztalty:` - gniazdo bez ksztaltu nie jest rysowane.
- stanowisko\ui\mapa.py:380-383 i :395-398 - brak podpisu albo podpis za dlugi: zostaje sam numer.
- stanowisko\ui\okno.py:822-823 - komunikaty innej plytki nie maja panelu; jest tylko znacznik "ma komunikat" na kafelku (l.667). Dotyczy to takze poziomu "blad", ktory nie trafia na pasek bledow.
- stanowisko\ui\okno.py:854-859 - panele ponad PANELI nie powstaja; zamiast nich jest napis "jeszcze n".
- stanowisko\ui\okno.py:665 - plytki wczesniejszych zmian sa ukryte za przyciskiem z liczba.
- stanowisko\ui\obraz.py:63-66 - ubytek bez wspolrzednych albo poza obrazem nie jest rysowany.
- stanowisko\ui\obraz.py:87 - gniazdo bez danych podgladu daje obraz None i napis "Brak obrazu".

Laptop - ekran poranny:
- stanowisko\ui\mapa_rano.py:56 `return g.prace[0] if len(g.prace) == 1 else None` - gniazdo z dwiema pracami nie ma zeba ani miniatury.
- stanowisko\ui\mapa_rano.py:88 `if not kuweta:` - pusty podpis daje sam numer.
- stanowisko\ui\mapa_rano.py:82-83 - napis, ktory sie nie miesci, nie jest rysowany.
- stanowisko\ui\mapa_rano.py:166-167 - pominiecie gniazda bez ksztaltu; dotyczy tylko `rysowane()` w testach.
- stanowisko\ui\ekran_rano.py:677 - skany "zastapiony" nie dostaja mapy, sa tylko w napisie (l.780-784).
- stanowisko\ui\ekran_rano.py:690 - z gniazda z dwiema pracami widok pokazuje tylko prace[0].
- stanowisko\ui\ekran_rano.py:758 - skan nieaktywny bez prac nie ma gniazd.
- stanowisko\ui\ekran_rano.py:778 i :787-788 - prace poza gniazdem sa tylko liczba; nie ma ich na mapie ani w legendzie.
- stanowisko\ui\ekran_rano.py:788 - legenda pomija gniazda bez prac.
- stanowisko\ui\ekran_rano.py:810-814 - klasy spoza KOLEJNOSC_KLAS i zera nie maja licznika.
- stanowisko\ui\ekran_rano.py:464 - brak pola `nierozstrzygniete_prace` daje brak ostrzezenia.
- stanowisko\ui\ekran_rano.py:396 - zlecenie bez brakujacych punktow nie ma punktow ani przyciskow.
- stanowisko\ui\ekran_rano.py:916 - komunikat ze `skan_id` plytki wieczornej nie jest pokazany ani przy plytkach, ani w komunikatach ogolnych ekranu porannego.
- stanowisko\ui\ekran_rano.py:968 - panele ponad 3 nie powstaja; zamiast nich jest napis "jeszcze n" (l.972-973).
- stanowisko\ui\kandydaci.py:181-182 `if zrodlo is None: return`
- stanowisko\ui\kandydaci.py:192-193 `if praca is None: return` - puste gniazdo: znaczek z pustym napisem.
- stanowisko\ui\kandydaci.py:196 - blok danych projektu jest ukryty, gdy praca nie ma projektu.
- stanowisko\ui\kandydaci.py:239 i :243 - karty kandydatow tylko dla wybranych klas, najwyzej 2.

Laptop - Excel:
- stanowisko\ui\okno_excela.py:214-215 `if ex is None: return` - panel nie jest czyszczony, zostaje poprzednia tresc.
- stanowisko\ui\okno_excela.py:238 - puste teksty (np. nieznany tryb) sa odfiltrowane.
- stanowisko\ui\okno_excela.py:261-263 - szczegoly None daja pusta tabele kandydatow.
- stanowisko\ui\okno_excela.py:161-162, :193-194, :204-205 - cichy powrot bez komunikatu.
- stanowisko\excel.py:362-363 `if w is None: continue` - pusty wiersz arkusza nie trafia do indeksu.
- stanowisko\excel.py:333 `if w.kuweta:` - wiersz bez kuwety w kolumnie C nie trafia do indeksu kuwet.
- stanowisko\excel.py:731 - brak klucza "kompletne" daje 0 pozycji bez bledu.
- stanowisko\excel.py:955-956 i :978-979 `if p.zalatwiona: continue` - pozycja zalatwiona nie ma wpisu cienia.
- stanowisko\excel.py:998-999 `if not poprawki: return []`
- stanowisko\excel.py:905 - po zapisie wiersz powyzej pierwszego wiersza danych nie jest sprawdzany.
- stanowisko\excel.py:560 `w = self.migawka.get(nr) or ()` - kandydat bez migawki ma puste pola.
- stanowisko\excel_com.py:126-127 `if ostatni < pierwszy_wiersz: return []` - pusty arkusz daje kazdej pozycji "wskaz wiersz".

Ramka (Raspberry Pi):
- ramka\logika.py:578 `for g in self.plan.plytki[p].gniazda:` - gniazdo spoza planu nie jest rysowane, a pierscien jest zielony.
- ramka\protokol.py:202 - pusta lista gniazd jest przyjmowana.
- ramka\logika.py:580 - rano gniazdo kuwety niebiezacej albo potwierdzonej jest ciemne.
- ramka\logika.py:561 - plytka bez wpisu w planie: nic nie swieci, napis "{p} BRAK".
- ramka\logika.py:385 - niepewny odczyt plytki dziala jak brak plytki.
- ramka\logika.py:369 - ramka W: wynik zdjetej plytki jest kasowany.
- ramka\logika.py:164 - wygasly plan daje ciemne gniazda.
- ramka\obraz.py:147 - pusty napis nie jest rysowany.

## Poza zakresem - skad przychodzi wartosc statusu (kontroler_api.py, aplikacja.py)

| miejsce w zakresie | wartosc | zrodlo |
|---|---|---|
| ui\mapa.py, ui\czesci.py (wieczor) | Praca.status, rgb, podpis, kolor | kontroler_api.py:3147-3151 (`ST.status_pracy`, `ST.status`, `ST.kolor_pracy`); l.3149 zamienia status_match None na "brak" |
| ui\mapa.py (wieczor) | Gniazdo | kontroler_api.py:3197-3199 "pusty"; l.3200-3202 "podwojny" tylko dla skanu aktywnego; l.3203-3205 w pozostalych przypadkach, takze skan nieaktywny z 2+ pracami, status z lista[0] |
| ui\okno.py:775-776 | praca poza gniazdem | kontroler_api.py:3189-3190 status "poza_gniazdem" |
| ui\czesci.py:840, 866-876 | liczniki plytki | kontroler_api.py:3207-3209, z p.kolor; None jest pomijany |
| ui\czesci.py:1246 | Praca.ubytki | kontroler_api.py:3176 `ubytki=p["ubytki"]` (None, gdy nie bylo inspekcji: session.py:476) |
| napis plytki | Plytka.napis | kontroler_api.py:3228 (wieczor), :1834 (rano) `ST.napis_plytki(s["status"])` |
| indicate.wynik (ramka W) | kolory gniazd | kontroler_api.py:2698 `RP.kolor_ramki(g.status)`; l.2692-2695 skan nieprzyjety albo nieaktywny daje `k.blad()`; l.2701-2708 numer niezgodny albo pytanie o ponowny skan daje numer None (ramka ciemna) |
| ui\ekran_rano.py, ui\kandydaci.py | PracaRano.status, rgb, podpis | kontroler_api.py:1733-1738 (`ST.status("rano_juz_rozpoznany")`, `ST.status_rano(klasa)`, klasa None daje "plytka_nie_z_trybu" albo "nieaktywny"); gniazda rano l.1788-1796 |
| ui\ekran_rano.py:397, 425 | BrakujacyPunkt.napis | kontroler_api.py:1726 `napis=ST.STANY_PUNKTU.get(b.get("stan"), b.get("stan") or "")` |
| ui\ekran_rano.py:810 | StanRano.liczniki | kontroler_api.py:1995, z session_rano.py:806-807 |
| ui\kandydaci.py:298 | ProjektPuli.stan | kontroler_api.py:3970 `stan=w["stan"] or SE.STAN_OCZEKUJE` |
| ui\okno_excela.py:67, 250, 253 | klasa, zalatwiona, wynik | kontroler_api.py:2956, 2958 |
| ui\okno_excela.py:278 | kolor_b, zielone | kontroler_api.py:3106-3107 |
| excel.py:725, 731 | wynik_pieca | session_rano.py:1124-1127; kontroler_api.py:2882 usuwa z listy zlecenia z wpisem innym niz "blad" (literal "blad" takze w l.2830 i l.2881) |
