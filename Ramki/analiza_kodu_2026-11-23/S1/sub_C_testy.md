# S1 / sub C - przeglad testow pod katem "falszywego zielonego" (2026-11-23)

Worktree: `<PC-katalog>\qc-wt\analiza-s1\Ramki\stanowisko` (galaz analiza/s1). Tylko czytanie (Read/Grep/Glob).
Nie uruchamiano pythona ani pytest. Numery linii z Read/Grep. Klasy slabosci S1-S6 wg zlecenia; "-" = test w porzadku
w sensie tych klas. Bez oceny wagi i bez propozycji poprawek.

## 0. Zakres, pliki, czego nie przejrzano

- `test_plytki_okragle*.py` - **brak takich plikow** w `testy\`. Zamiast nich przejrzano `test_okragle_ekran.py`,
  `test_okragle_sesja.py`, `test_okragle_wydanie.py` (w calosci) i `test_okragle_ramka.py` (czesciowo, patrz nizej).
- Pliki importujace `stanowisko.inspect` / `stanowisko.porownaj` / `stanowisko.krawedz` (Grep `^\s*(from|import).*`):

| plik | linii | def test_* | import (linia) | przejrzany |
|---|---|---|---|---|
| test_inspect.py | 655 | 26 | inspect, krawedz, porownaj (:14) | w calosci |
| test_porownaj_bledy.py | 129 | 3 | inspect, porownaj (:16) | w calosci |
| test_krawedz.py | 281 | 14 | krawedz (:17) | w calosci |
| test_skala.py | 282 | 12 | inspect, porownaj (:13) | w calosci |
| test_straznik.py | 288 | 10 | porownaj (:24) | w calosci |
| test_auto_uklad.py | 270 | 13 | porownaj (:18) | w calosci |
| test_auto_uklad_r58.py | 536 | 29 | porownaj (:19) | w calosci |
| test_synth.py | 340 | 16 | krawedz lokalnie (:203, :255) | w calosci |
| test_edge_synth.py | 405 | 30 | krawedz lokalnie (:397) | w calosci |
| test_pula_match.py | 791 | 32 | porownaj (:29) | w calosci |
| test_ui.py | 150 | 2 | porownaj (:21) | w calosci |
| test_okragle_ekran.py | 476 | 12 | porownaj lokalnie (:429, :453) | w calosci |
| test_okragle_wydanie.py | 617 | 22 | porownaj lokalnie (:455) | w calosci |
| test_kontroler_api.py | 1758 | 52 | porownaj lokalnie (:781, :1148) | CZESCIOWO: lista testow + :280-410, :745-860, :1140-1195 |
| test_session_wieczor.py | 1630 | 55 | porownaj lokalnie (:1595) | CZESCIOWO: lista testow + :160-200, :510-570, :1575-1631 |

- Pozostale pliki z listy zlecenia (nie importuja tych modulow): test_match.py (217 linii, 12 test_*), test_plate.py
  (176, 9), test_uklad.py (107, 8), test_uklad_r58.py (221, 11), test_uklad_r59.py (321, 12), test_okragle_sesja.py
  (235, 14) - w calosci; test_okragle_ramka.py (1409, 46) - CZESCIOWO: lista testow (Grep) + :1-160, :950-975, :1196-1235.
- Nie importuja, ale tylko wspominaja porownaj: test_aplikacja.py:149, test_pula_aplikacja.py:559 (komentarz),
  test_samokontrola.py:544 (nazwa modulu w zbiorze), test_silnik.py:1710 (uruchamia `python -m stanowisko.porownaj`
  przez subprocess; przejrzane tylko :1690-1795 i lista testow), test_ustawienia.py:384 (`import inspect` = modul
  standardowy). Tych plikow nie przegladano w calosci.
- Brak plikow konfiguracji pytest (pytest.ini / pyproject.toml / setup.cfg / tox.ini) w `Ramki\stanowisko` i `Ramki`
  (find, maxdepth 4; jedyny inny conftest.py: `Ramki\sesje_2026-10-31\kod_a_stanowisko\testy_edge\conftest.py`, archiwum).

Wspolne cechy lancucha w testach inspekcji (fakty):
- Prace = atrapy z `narzedzia/atrapy_koron.py` (siekacz, przedtrzonowy, trzonowy; fixture `korony` w conftest.py:29),
  pula = te same 3 projekty (test_inspect.py:23-27, test_skala.py:25-34, test_porownaj_bledy.py:28-32).
- Jedyny uklad plytki w testach z asercja o wyniku inspekcji: `okragla_wieczorna` (R59, okragla testowa n8).
- Generator: `synth.Opcje` ma domyslnie `ubytki_na_prace=(0, 2)` (synth.py:829); fixture bez nadpisania tego pola
  generuja prace z 0-2 ubytkami.
- Statusy inspect -> kolor gniazda: porownaj.py:63-64 `INSPECT_NA_STATUS` (ok->zielony, ubytek->czerwony, sprawdz /
  sprawdz_ulozenie / popraw_ulozenie / skan_ponownie / nie_sprawdzono -> zolty, poprawka->pomaranczowy, pominieto->None).
- Pas brzegu z ustawien: `pas_brzegu_mm = 1.5`, `pas_brzegu_od = "linia_i_plaszczyzna"` (ustawienia.przyklad.toml:59, :69).

## 1. Tabele per plik

Kolumny: plik:linia | nazwa testu | co faktycznie sprawdza (asercje) | uklad plytki | klasa slabosci.
"(xN)" = parametryzacja.

### 1.1 test_inspect.py (655 linii, 26 test_*)

Pomocnik `_lancuch` (:30-49): `okragla_wieczorna`, numer 8, 3 atrapy x 1,22, plate -> match -> inspect.sprawdz;
asercja tylko `len(out) == len(prawda.prace) > 0` (:48). Fixture `z_ubytkami` (:52-54): seed 5, `ubytki_na_prace=(1, 2)`,
`srednica_ubytku=(0.6, 1.4)`, bez drgniecia.

| plik:linia | test | co sprawdza | uklad | klasa |
|---|---|---|---|---|
| test_inspect.py:58 | test_ubytki_z_prawdy_sa_wykrywane | kazda praca z ubytkiem: k.id == projekt i status inspect in (ubytek, sprawdz, sprawdz_ulozenie) (:61); falszywe_czerwone == 0; metoda/kolor; srednica <= srednica_max+0,5; glebokosc >= 0,08; A+B => czerwony; wyk >= 3; traf_dowolny >= 0,8*wyk; traf_A >= 0,7*wyk; traf_B >= 1; traf_czerwony >= 1 (:74-76). Status gniazda (porownaj) nie jest sprawdzany | okragla_wieczorna | S2 (progi w tescie 0,8 / 0,7 / >=1; w pliku brak wartosci zmierzonej i brak wymagania, do ktorego mozna je porownac), S5 |
| test_inspect.py:79 | test_ubytek_w_ukladzie_plytki_blisko_prawdy | tylko dla wykryc z metoda zaczynajaca sie od "A": odleglosc do najblizszego ubytku prawdy <= 1,0 mm; `odleglosc_od_brzegu_mm <= 1.5 + 0.8 or u.na_krawedzi` (:86) | okragla_wieczorna | S4 (`if u.metoda.startswith("A")`), S2 (tolerancja 2,3 mm przy pasie 1,5 mm) , S5 |
| test_inspect.py:89 | test_praca_cala_bez_alarmu | seed 6, bez ubytkow: status == ok, ubytki == [], brak drgniecia, brak plam ubytek i wciec, udzial_pod < 0,02, abs(mediana) < 0,01 | okragla_wieczorna | S5 |
| test_inspect.py:97 | test_drgniecie_daje_skan_ponownie | p_drgniecia 1, ubytki 0-1: status == skan_ponownie, drgniecie wykryte, ubytki == [], uwaga "skan ponownie" | okragla_wieczorna | S5 |
| test_inspect.py:103 | test_niskie_pokrycie_to_popraw_ulozenie | pokrycie 0,5 podane recznie: popraw_ulozenie, ubytki == []; punkty z podgladu, normalne zastepcze (0,0,1) (:115) | okragla_wieczorna | - |
| test_inspect.py:119 | test_poprawka_reczna_bez_ostrej_krawedzi_to_pomaranczowe | p_poprawki 1, bez ubytkow: `wi.status != "ubytek"` i brak czerwonych (:123); n_pop >= 2 (z 3 prac) (:128) | okragla_wieczorna | S3 (`!= "ubytek"`, dopuszcza ok), S2 (2 z 3), S5 |
| test_inspect.py:131 | test_brak_danych_w_skanie_nie_jest_ubytkiem | p_pokrycie 1 (wyciete 30-60 %), bez ubytkow: `wi.status not in ("ubytek", "skan_ponownie")` (:135), brak czerwonych, brak plam ubytek | okragla_wieczorna | S3 (dopuszcza ok), S5 |
| test_inspect.py:140 | test_praca_bokiem_nigdy_czerwona | seedy 10-12, p_bokiem 1, bez ubytkow: ulozenie bokiem/do_gory_nogami; `if r.status == "szary": continue` (:158); `wi.status != "ubytek"`, brak czerwonych (:161); `n >= 1` (:163) | okragla_wieczorna | S3, S4, S5 |
| test_inspect.py:167 | test_progi_z_ustawien_steruja_wynikiem | prog_glebokosci 5,0 -> zadnego A/A+B i plamy == []; wciecie 5/6 -> wszystkie ubytki A i zolte, wciec == 0; progi drgniecia -> skan_ponownie | okragla_wieczorna (punkty z podgladu, normalne zastepcze) | S4 (`all(...)` na liscie ubytkow, ktora moze byc pusta) |
| test_inspect.py:183 | test_wykryj_drgniecie_na_sztucznych_odchylkach | losowe punkty; dwie warstwy +-0,06 -> drgniecie; przesuniecie -0,2 i plama -> nie | brak | - |
| test_inspect.py:216 | test_plamy_ostra_vs_lagodna | plaska plyta `_Plaski`: dolek ostry fi 0,8 gl. 0,3 -> 1 plama ubytek, ostra, 0,5 < d < 1,2; gladki fi 5 -> poprawka; ostry fi 2 -> sprawdz_ulozenie; plama na skraju danych -> nie ubytek | brak (bryla analityczna) | S5 |
| test_inspect.py:238 | test_dopasuj_do_prawdy | jednostkowy dopasowania wykryc do prawdy | brak | - |
| test_inspect.py:246 | test_status_gniazda_i_scenariusz | `status_gniazda`: (szary, ubytek)=szary, (zielony, ubytek)=czerwony, (zielony, poprawka)=pomaranczowy, (zolty, popraw_ulozenie)=zolty, (zielony, None)=zielony (:251); scenariusz | brak | - (brak przypadkow sprawdz, sprawdz_ulozenie, skan_ponownie) |
| test_inspect.py:259 | test_json_wyniku_bez_tablic | brak _P/_d w json, json.dumps przechodzi, klucze `brzeg` | okragla_wieczorna | S1 |
| test_inspect.py:322 | test_pas_od_linii_obejmuje_brzeg_ponizej_plaszczyzny | filar z wneka 4 mm pod wierzchem + blok; ukruszenie `wytnij_ukruszenie(..., "srodek", 0.3)`; tryb "linia": status in (ubytek, sprawdz), wykrycie A <= 0,6 mm od ukruszenia, filar 1 (:339-342); tryb "plaszczyzna": `stary.status == "ok" and stary.ubytki == []` (:344, komentarz "przed P2: ukruszony brzeg = zielone") | brak (bryla analityczna) | S5; tryb domyslny nie uzyty |
| test_inspect.py:348 | test_tryb_sumy_pasow_obejmuje_brzeg_gleboki_i_stary_pas | tryb suma: status in (ubytek, sprawdz) i wykrycie <= 0,6 mm; czasza r 0,35 na wierzchu przesla ok. 7 mm od linii: wykrywa suma i plaszczyzna, linia nie (poza_pasem) | brak (bryla) | S5 |
| test_inspect.py:380 | test_praca_cala_z_glebokim_brzegiem_jest_zielona | bez ubytkow: ok w suma i linia; brzeg sprawdzony; udzial_sprawdzony >= brzeg_min_sprawdzony; udzial_z_danymi > 0,99 | brak (bryla) | S5 |
| test_inspect.py:395 | test_brak_danych_przy_linii_brzegu_to_nie_sprawdzono | 1/3 obwodu bez danych: suma i linia -> nie_sprawdzono, status_gniazda zolty (:416); 0,55 < udzial < 0,85; 3,0 < przerwa < 6,5; z brzeg_min_sprawdzony 0,5 i przerwa 50 -> ok (:419); przerwa 1,0 -> nie_sprawdzono; plaszczyzna -> ok (:424) | brak (bryla) | S5 |
| test_inspect.py:427 | test_brak_danych_i_ukruszenie_obok_nigdy_czerwone_z_braku_danych | tryb linia: ukruszenie 0,3 na przekroju 180 st. + dziura w danych: status in (ubytek, sprawdz), brzeg niesprawdzony; wszystkie wykrycia <= 1,0 mm od ukruszenia | brak (bryla) | S5; tylko tryb "linia" |
| test_inspect.py:453 | test_linia_projektu_niepewna_albo_brak_linii_to_nie_sprawdzono | tuleja + blok (linia niepewna): suma -> ok, brzeg sprawdzony (:468); linia -> nie_sprawdzono; plaszczyzna -> ok (:475); bryla bez wneki: suma -> ok, stan_linii brak (:480); linia -> nie_sprawdzono | brak (bryla) | S5 |
| test_inspect.py:487 | test_projekt_bez_linii_z_wcieciem_w_trybie_sumy_dziala_jak_przed_p2 | pudelko 8x6x5, wgniecenie plaskie 0,3 mm: suma == plaszczyzna (status, ubytki, wciecia, plamy); `statusy == [("ubytek", [("A+B","czerwony")]), ("sprawdz", [("B","zolty")])]` (:514, komentarz "jak na main"); linia -> nie_sprawdzono | brak (bryla) | S5 |
| test_inspect.py:517 | test_filar_z_niecka_bez_linii_nie_znika_po_cichu | 2 filary, linie filaru 2 usuniete (monkeypatch): linia -> nie_sprawdzono, status_gniazda zolty; suma -> ok, `brzeg["sprawdzony"]`, `nie_sprawdzono == []` (:552); ukruszenie 0,3 na filarze 2: suma status in (ubytek, sprawdz) | brak (bryla) | S5 |
| test_inspect.py:576 | test_prace_bokiem_i_czesciowe_nie_sa_zielone_bez_sprawdzonego_brzegu | seed 9, p_pokrycie 1, bez ubytkow: `if wi.status in ("ok", "nie_sprawdzono")`: `(status == "ok") == brzeg["sprawdzony"]` (:581-583); `n >= 1`. p_bokiem nie ustawione mimo nazwy | okragla_wieczorna | S4, S5 |
| test_inspect.py:587 | test_status_nie_sprawdzono_w_porownaj | mapowanie nie_sprawdzono -> zolty, tabela tekstowa | brak | - |
| test_inspect.py:605 | test_metryki_inspekcji_krawedz_i_sciana_osobno | metryki na slownikach (bez skanu) | brak | - |
| test_inspect.py:643 | test_polozenie_ubytku_starej_prawdy_z_linii_projektu | klasa polozenia z linii projektu; 1,2 mm pod naroznikiem -> sciana, 1,1 < odl < 1,25 | atrapa z puli | - |

### 1.2 test_porownaj_bledy.py (129 linii, 3 test_*)

Fixture `plytka` (:36-49): `okragla_wieczorna`, `ubytki_na_prace=(0, 0)`, asercja: wszystkie 3 gniazda zielony / ok / zielony (:48).

| plik:linia | test | co sprawdza | uklad | klasa |
|---|---|---|---|---|
| test_porownaj_bledy.py:71 | test_blad_inspekcji_jednego_gniazda_nie_kladzie_plytki | wyjatek z `sprawdz` dla 1 gniazda: status_gniazda zolty, inspekcja nie_sprawdzono, uwaga, pola; pozostale gniazda jak wzor | okragla_wieczorna | - |
| test_porownaj_bledy.py:99 | test_cli_zapisuje_wynik_mimo_bledu_inspekcji | CLI: zapis, zolty 1 / zielony 2 / ubytki 0, metryki, PNG, tekst | okragla_wieczorna | - |
| test_porownaj_bledy.py:124 | test_przerwanie_i_brak_pamieci_nie_sa_lapane (x3) | KeyboardInterrupt / SystemExit / MemoryError przepuszczane | okragla_wieczorna | - |

### 1.3 test_krawedz.py (281 linii, 14 test_*)

Naglowek (:3-5): liczby dla 17 prawdziwych projektow sa w raporcie paczki; w testach tylko atrapy i bryly.

| plik:linia | test | co sprawdza | uklad | klasa |
|---|---|---|---|---|
| test_krawedz.py:54 | test_korona_ma_jedna_petle_na_brzegu | atrapa: 1 petla, wiarygodna, udzial_zweryf >= 0,95, przerwa <= 0,5; O na obwodzie < 0,2; 0,6 < szer < 0,9; dlugosc +-2 % | brak | S5 |
| test_krawedz.py:78 | test_most_ma_petle_na_kazdy_filar | most-atrapa: 4 filary, odstep > 4, `f.werdykt in KR.WERDYKTY` (kazdy werdykt), dlugosc > 10 | brak | S1 (werdykt dowolny), S5 |
| test_krawedz.py:91 | test_korona_implantowa_obwod_powierzchni_przylegania | tuleja: wiarygodna, promienie +-0,02, T3 | brak | S5 |
| test_krawedz.py:103 | test_odcinek_niepewny_jest_oznaczony_a_nie_zgadywany | szerokie przekroje niezweryfikowane, stan czesciowe | brak | - |
| test_krawedz.py:121 | test_bryla_bez_wneki_nie_ma_linii (x2) | brak linii, stan brak | brak | - |
| test_krawedz.py:128 | test_filar_z_niecka_bez_linii_jest_jawny | filary_bez_linii, stan czesciowe, npz | brak | - |
| test_krawedz.py:165 | test_skala_i_przesuniecie_nie_zmieniaja_linii | niezaleznosc od skali | brak | - |
| test_krawedz.py:178 | test_zla_skala_odrzucona | ValueError | brak | - |
| test_krawedz.py:184 | test_pamiec_w_module_i_na_dysku | pamiec modulu i dysku | brak | - |
| test_krawedz.py:228 | test_stacje_wszystkich_filarow | liczby stacji | brak | - |
| test_krawedz.py:237 | test_przeksztalcenie_ukladu | skala/przesuniecie linii | brak | - |
| test_krawedz.py:247 | test_najdluzsza_przerwa_kolowa | jednostkowy | brak | - |
| test_krawedz.py:254 | test_fourier_odporny_pomija_odstajace | jednostkowy | brak | - |
| test_krawedz.py:265 | test_niecki_i_dzial_wodny_na_sztucznej_mapie | jednostkowy | brak | - |

### 1.4 test_skala.py (282 linii, 12 test_*)

Fixture `plytka` (:37-53): domyslnie `ubytki=(0, 0)`, uklad `okragla_wieczorna`.

| plik:linia | test | co sprawdza | uklad | klasa |
|---|---|---|---|---|
| test_skala.py:60 | test_estymata_skali_i_korekta (x3: -1; 0; 0,5) | estymata +-0,05 pp, zielony, pokrycie >= 0,85, blad pozy. Docstring "-1 ... +1 %", parametry bez +1 | okragla_wieczorna | - |
| test_skala.py:83 | test_poza_oknem_bez_korekty_z_ostrzezeniem | 2 %: bez korekty, ostrzezenie, status != zielony | okragla_wieczorna | - |
| test_skala.py:95 | test_plytka_poranna_tylko_pomiar | parametr bez_korekty (skan wieczorny) | okragla_wieczorna | - |
| test_skala.py:107 | test_ustawienia_steruja_korekta | ustawienia korekty | okragla_wieczorna | - |
| test_skala.py:129 | test_strefa_brzegu_nie_wplywa_na_skale | brzeg grubszy/odgiety/ukruszony fi 1,2 -> skala identyczna | okragla_wieczorna | - |
| test_skala.py:183 | test_inspekcja_w_skali_skorygowanej_praca_cala | +1 %: bez korekty wszystkie status != ok; z korekta wszystkie ok | okragla_wieczorna | - |
| test_skala.py:193 | test_korekta_nie_zjada_ukruszen | seed 5, ubytki 1-2, fi 0,8-1,4, praca +0,5 %: status in (ubytek, sprawdz, sprawdz_ulozenie) == status odniesienia; falszywe_czerwone == 0; falszywe <= odn+1; traf_kor >= traf_odn-1 i >= 0,8*n; n >= 3 | okragla_wieczorna | S2 (0,8*n; -1; +1), S5 |
| test_skala.py:213 | test_estymata_niepewna_bez_ostrzezenia | inspekcja=False | okragla_wieczorna | - |
| test_skala.py:231 | test_porownaj_pola_skali_i_tabela | prace cale: zielony i inspekcja ok; okragla_poranna: tylko pola skali (inspekcja liczona, nie sprawdzana) | okragla_wieczorna, okragla_poranna | - |
| test_skala.py:259 | test_wzor_ustawien_ma_decyzje_wlasciciela | wartosci w przykladzie | brak | - |
| test_skala.py:266 | test_blad_pozy_dla_podobienstwa | jednostkowy | brak | - |
| test_skala.py:275 | test_pula_wspolczynnik_dla_projektu | wspolczynnik projektu | brak | - |

### 1.5 test_match.py (217 linii, 12 test_*)

Fixture `fragmenty` (:35-51): parametry `okragla_wieczorna_r54`, `okragla_wieczorna`; seed 22; komentarz :43: seedy 21, 27, 29
daja odwrotne dopasowanie siekacza (pokrycie 0,52 -> szary); ubytki domyslne (0, 2), `wersja_ubytkow=1`.

| plik:linia | test | co sprawdza | uklad | klasa |
|---|---|---|---|---|
| test_match.py:54 | test_pula_i_cechy | cechy projektow | brak | - |
| test_match.py:63 | test_dopasowanie_top1_i_transformacja (x2) | top1, pokrycie >= 0,85, rms < 0,04, zielony, blad pozy < 0,05 / 0,5 st. | okragla_wieczorna_r54, okragla_wieczorna | S2 (seed 22 dobrany; 21/27/29 -> szary wg komentarza :43) |
| test_match.py:79 | test_filtr_wymiarow (x2) | filtr wymiarow | j.w. | - |
| test_match.py:98 | test_filtr_nie_odrzuca_pracy_ze_schowanym_dolem (x2) | filtr przy schowanym dole | j.w. | - |
| test_match.py:118 | test_filtr_nadal_ogranicza_pule (x2) | filtr odrzuca obce | j.w. | - |
| test_match.py:138 | test_cechy_projektu_do_glebokosci | cechy do glebokosci | brak | - |
| test_match.py:149 | test_zgrubne_obroty_i_ocena | tylko `_r54`: pok > 0,8; pok2 >= 0,85; RANSAC >= 0,85 | okragla_wieczorna_r54 | S2 (docstring :150-153 "zmierzone": RANSAC seed 0 fragment 0 _r54 = 0,90, R59 = 0,27 -> test ograniczony do _r54; progi 0,8 / 0,85) |
| test_match.py:169 | test_dopasuj_brzegi | puste dane -> szary | brak | - |
| test_match.py:178 | test_statusy_z_progow (x2) | progi -> zolty / szary | j.w. | - |
| test_match.py:192 | test_blad_pozy_tozsamosc | jednostkowy | brak | - |
| test_match.py:201 | test_kandydat_pola_puli_per_praca_domyslne | pola domyslne | brak | - |
| test_match.py:209 | test_pula_z_folderu_klucz_kandydata_i_wspolczynnik (x2) | klucze kandydatow | j.w. | - |

### 1.6 test_plate.py (176 linii, 9 test_*)

| plik:linia | test | co sprawdza | uklad | klasa |
|---|---|---|---|---|
| test_plate.py:36 | test_wyrownanie_numer_i_gniazda (x2) | blad wyrownania, numer 8 z dolkow, gniazda prac, fragmenty | okragla_wieczorna, okragla_wieczorna_r54 | - |
| test_plate.py:55 | test_numer_podany_wygrywa_z_ostrzezeniem (x2) | numer podany 9 vs dolki 8 | j.w. | - |
| test_plate.py:63 | test_kwadrat_dolki_poza_polem_wymaga_numeru (x2) | numer nieznany, bity None | wieczorna_r54, wieczorna | - |
| test_plate.py:76 | test_praca_poza_gniazdem_i_podwojna | poza gniazdem, podwojne | okragla_wieczorna_r54 | - |
| test_plate.py:107 | test_kabsch_2d_bez_odbicia | jednostkowy | brak | - |
| test_plate.py:119 | test_przypisz_znaczniki_z_nadmiarowym_i_permutacja (x2) | przypisanie stozkow | poranna_r54, poranna | - |
| test_plate.py:136 | test_dopasuj_stozek_na_punktach_syntetycznych | jednostkowy | brak | - |
| test_plate.py:150 | test_kandydaci_znacznikow_z_mapy_wysokosci (x4) | kandydaci stozkow z probki modelu STL | wieczorna, poranna, wieczorna_r54, poranna_r54 | S6 (tylko modele kwadratowe; plytki okragle maja inne STL, plate.py ma galaz ksztaltu :737-840) |
| test_plate.py:162 | test_odczytaj_bity_i_blad_tozsamosci (x2) | bity dolkow, blad tozsamosci | okragla_poranna, okragla_poranna_r54 | - |

### 1.7 test_straznik.py (288 linii, 10 test_*)

Skany: `ubytki_na_prace=(0, 0)` (:35).

| plik:linia | test | co sprawdza | uklad | klasa |
|---|---|---|---|---|
| test_straznik.py:55 | test_plytka_innego_ukladu_konczy_sie_niezgodny_uklad (4x2) | NiezgodnyUklad, powod stozki | 4 typy R59 vs _r54 (w tym okragla_*_r54) | - |
| test_straznik.py:71 | test_plytka_zgodna_bez_falszywego_alarmu (x8) | uklad_zgodny, fragmenty = prawda | 8 ukladow | - |
| test_straznik.py:93 | test_zgodnosc_ukladu_na_pustych_plytkach (x4) | zgodny / niezgodny; komentarz "zmierzone >= 440 i >= 280 mm2", asercja > 2 x prog (300 / 100) | 4 typy + _r54 | - |
| test_straznik.py:122 | test_stozki_pasuja_ale_gniazda_inne (x4) | hybryda: NiezgodnyUklad, powod gniazda | tylko pary kwadratowe | S6 |
| test_straznik.py:163 | test_porownaj_niezgodny_uklad_zadnych_gniazd | gniazda [], liczniki 0 | skan okragla_wieczorna_r54 vs okragla_wieczorna | - |
| test_straznik.py:179 | test_porownaj_zgodny_uklad_ma_flage | porownaj z inspekcja: uklad_zgodny, 3 gniazda, numer 8 (inspekcja nie sprawdzana) | okragla_wieczorna_r54 | - |
| test_straznik.py:188 | test_cli_porownaj_niezgodny_zapisuje_wynik_bez_metryk | zielony == 0 | j.w. | - |
| test_straznik.py:200 | test_okno_lista_ukladow_i_komunikat_straznika | okno, kolory pusty | j.w. | - |
| test_straznik.py:241 | test_stary_plik_ustawien_podpowiada_brakujace_uklady_r54 | podpowiedz | j.w., poranna_r54 | - |
| test_straznik.py:267 | test_okno_podpowiada_brak_ukladow_r54 | okno | j.w. | - |

### 1.8 test_auto_uklad.py (270 linii, 13 test_*)

Skany: `ubytki_na_prace=(0, 0)` (:28). Wszystkie testy dotycza rozpoznania ukladu; brak asercji o inspekcji.

| plik:linia | test | co sprawdza | uklad | klasa |
|---|---|---|---|---|
| test_auto_uklad.py:59 | test_rozpoznaje_kazdy_z_osmiu_ukladow_bez_numeru (x8) | wybrany == prawda, pewny, rodzina | 8 ukladow | - |
| test_auto_uklad.py:74 | test_wynik_jak_przy_ukladzie_wybranym_recznie (x8) | macierz, numer, fragmenty jak recznie | 8 | - |
| test_auto_uklad.py:89 | test_plytka_okragla_ma_numer_z_dolkow (x4) | numer z dolkow | okragla_* i okragla_*_r54 | - |
| test_auto_uklad.py:97 | test_kwadrat_z_podanym_numerem (x4) | numer podany | kwadraty | - |
| test_auto_uklad.py:107 | test_numer_spoza_rozpoznanej_rodziny_jest_pomijany | ostrzezenie | poranna_r54 | - |
| test_auto_uklad.py:115 | test_zaden_uklad_nie_pasuje | NierozpoznanyUklad | poranna_r54 | - |
| test_auto_uklad.py:151 | test_porownaj_auto_rozpoznaje_stara_plytke_i_dobiera_wspolczynnik | auto = recznie (status match, kandydat) | wieczorna_r54 | - |
| test_auto_uklad.py:168 | test_porownaj_auto_poranna_ma_wspolczynnik_jeden | inspekcja=False | okragla_poranna_r54 | - |
| test_auto_uklad.py:187 | test_porownaj_auto_nie_rozpoznaje_gdy_brak_ukladu | gniazda [], liczniki 0 | poranna_r54 | - |
| test_auto_uklad.py:200 | test_cli_domyslnie_auto | --bez-inspekcji | wieczorna_r54 | - |
| test_auto_uklad.py:213 | test_stary_plik_ustawien_dostaje_uklady_wbudowane | ustawienia | brak | - |
| test_auto_uklad.py:231 | test_opis_ukladu | teksty | brak | - |
| test_auto_uklad.py:237 | test_okno_domyslnie_rozpoznaje_automatycznie | okno | wieczorna_r54, okragla_poranna | - |

### 1.9 test_auto_uklad_r58.py (536 linii, 29 test_*)

Wszystkie testy dotycza rozpoznania ukladu / narzedzia pomiarowego; brak asercji o inspekcji
(`porownaj` tylko w :303 z `inspekcja=False`).

| plik:linia | test | co sprawdza | uklad | klasa |
|---|---|---|---|---|
| test_auto_uklad_r58.py:75 | test_kandydaci_to_wszystkie_uklady_wbudowane | 10 / 8 kandydatow | 10 | - |
| :83 | test_rozpoznaje_kazdy_z_dziesieciu_ukladow_bez_numeru (x10) | wybrany, pewny, rodzina | 10 | - |
| :97 | test_plytka_ramkowa_ma_numer_z_dolkow_i_po_nim_jest_rozpoznana (x2) | powod numer_z_dolkow | ramkowe | - |
| :111 | test_wynik_ramkowej_jak_przy_ukladzie_wybranym_recznie (x2) | jak recznie | ramkowe | - |
| :123 | test_ramkowa_z_numerem_podanym_zgodnym (x2) | numer podany zgodny | ramkowe | - |
| :132 | test_kwadrat_r59_z_numerem_podanym_rozstrzyga_ksztalt (x2) | powod ksztalt vs numer_podany | wieczorna, poranna | - |
| :146 | test_kwadrat_r54_z_numerem_podanym_bez_zmian (x2) | numer_podany | *_r54 kwadraty | - |
| :155 | test_okragla_testowa_bez_zmian (x2) | 8 i 10 kandydatow | okragla_wieczorna/poranna | - |
| :168 | test_ramkowa_numer_podany_inny_niz_dolki_ten_sam_uklad | numer wyniku = podany 2, dolki 1 tylko w polu; "program ich dzis nie konfrontuje" | okragla_ramkowa_wieczorna | - (utrwala zachowanie, patrz (c)) |
| :179 | test_ramkowa_numer_podany_z_drugiej_pory_jest_pomijany | numer z dolkow | ramkowa | - |
| :189 | test_kwadrat_numer_podany_inny_numer_tej_samej_rodziny | numer podany przyjety bez sprawdzenia | wieczorna | - (patrz (c)) |
| :204 | test_male_pole_96_i_94_uklad_dobry_i_pewny (x5) | dobry_pewny | 5 ukladow | - |
| :216 | test_male_pole_90_i_80_brak_wyniku_blad_wyrownania (x5) | brak wyniku; "zachowanie do utrwalenia" | 5 ukladow | - (patrz (c)) |
| :242 | test_ograniczenie_znane_testowa_z_zaslonietym_dolkiem_pole_98_to_pewny_kwadrat_do_odwrocenia_po_wariancie_c | 10 kandydatow: wybrany "wieczorna", pewny True, dolki_wykluczaja; 8 kandydatow: okragla_wieczorna | okragla_wieczorna (prawda) | - (utrwala zly uklad, patrz (c)) |
| :259 | test_testowa_z_zaslonietym_dolkiem_pole_100_ze_scianka_dobrze_i_pewnie | dobrze i pewnie | okragla_wieczorna | - |
| :268 | test_ograniczenie_znane_ramkowa_z_zaslonietymi_dolkami_bez_scianki_to_pewny_kwadrat_do_odwrocenia_po_wariancie_c | wybrany "wieczorna", pewny True; sockets kwadratu == ramkowej | okragla_ramkowa_wieczorna (prawda) | - (patrz (c)) |
| :286 | test_skan_bez_scianki_bocznej_nie_ma_trojkatow_scianki | konstrukcja skanu | okragla_wieczorna | - |
| :303 | test_porownaj_auto_rozpoznaje_plytke_ramkowa | inspekcja=False; uklad, numer, gniazda | okragla_ramkowa_poranna | - |
| :322-:520 | 11 testow narzedzia (help, numery_niezgodne, ocen_k4, ocen_k3, brak wyniku, bramka pole 100, bez sciezek, granice, z pliku, czas, maly przebieg) | logika narzedzia auto_uklad_r58 na slownikach | brak / ramkowe | - |

### 1.10 test_synth.py (340 linii, 16 test_*)

| plik:linia | test | co sprawdza | uklad | klasa |
|---|---|---|---|---|
| test_synth.py:23 | test_atrapa_szczelna_i_brzeg_na_dole | orientacja | brak | - |
| test_synth.py:34 | test_ubytek_jest_pod_powierzchnia | `(odl > -0.02).mean() > 0.9` (:47), odl.max() > 0,1, ub.z w gornych 2 mm | brak | S2 (prog 0,9; w :148 dla tej samej funkcji `odl.min() > -1e-3`) |
| test_synth.py:53 | test_szum_ma_zadane_odchylenie | 0,025 < std < 0,035 | brak | - |
| test_synth.py:61 | test_osadzenie_w_gniezdzie_trzyma_sie_stozka (x4) | brak przenikania; `if T is None: continue`; osadzen >= 20 | wieczorna, poranna, wieczorna_r54, poranna_r54 | S4 (continue, chroni osadzen >= 20) |
| test_synth.py:85 | test_za_male_gniazdo_odrzuca | None | wieczorna_r54 | - |
| test_synth.py:92 | test_generuj_plytke_i_prawda | prawda, zapis/odczyt | wieczorna_r54 | - |
| test_synth.py:114 | test_okragla_poranna_ma_skale_1 | skala | brak | - |
| test_synth.py:121 | test_uklad_r54_ma_te_sama_skale_co_typ_plytki | skala | brak | - |
| test_synth.py:148 | test_czasza_ubytku_lezy_w_materiale_takze_na_krawedzi | v2: czasza w materiale; v1: >= 6 z 12 w powietrzu | brak | - |
| test_synth.py:167 | test_ubytek_na_scianie_ma_glebokosc_nominalna | glebokosc 0,7 r +-0,03 | brak | - |
| test_synth.py:186 | test_gestosc_punktow_ubytku_z_ustawien | `0.4*pole/odstep^2 < n < 2.5*pole/odstep^2` | brak | S2 (zakres 0,4-2,5 x oczekiwanej) |
| test_synth.py:210 | test_ukruszenie_celowe_na_krawedzi_brzegu (x4) | srodek kuli na powierzchni/linii, glebokosci wg klasy; sciana: `s + SCIANA_OD_KRAWEDZI_MM <= odl <= 1.5 - s + 0.8` (:237) | brak | - |
| test_synth.py:240 | test_ukruszenia_celowe_nie_nachodza_na_siebie_i_brak_linii | odstep, brak linii -> None | brak | - |
| test_synth.py:267 | test_polozenie_wzgledem_brzegu | klasy; 1 mm pod naroznikiem -> sciana 0,9 < odl < 1,01 | brak | - |
| test_synth.py:280 | test_generuj_plytke_z_ukruszeniami_krawedzi | prawda K6, odleglosc_od_linii <= pas | okragla_wieczorna | - |
| test_synth.py:323 | test_wersja_1_generatora_do_odtwarzania_starych_zestawow | determinizm v1 | wieczorna | - |

### 1.11 test_edge_synth.py (405 linii, 30 test_*)

| plik:linia | test | co sprawdza | uklad | klasa |
|---|---|---|---|---|
| test_edge_synth.py:50 | test_osadzenie_nie_przenika_stozka_wiele_seedow | `if T is None: continue`; maks <= 1e-6; brak licznika osadzen | poranna_r54 | S4 (petla moze nie zrobic zadnej asercji) |
| :64 | test_osadzenie_bez_luzu_nie_przenika_stozka | T not None, przenikanie | poranna_r54 | - |
| :76 | test_osadzenie_30_seedow_wszystkie_gniazda_4_typy (x4) | przenikanie; osadzen >= 30*n*3 | 4 kwadraty | - |
| :95 | test_most_w_rynience_nie_przenika_scianek (x4) | box: asercje; most: `if T is not None` bez licznika (:122) | 4 kwadraty | S4 (czesc z mostem) |
| :126, :135, :141, :147, :155 | rynienka obrocona / most za szeroki / praca za szeroka / wisi / przenikanie | osadzanie, odrzucenie | wieczorna_r54, poranna_r54 | - |
| :163 | test_ubytek_o_zerowej_lub_ujemnej_srednicy_odrzucony_od_razu (x3) | ValueError | brak | - |
| :168 | test_ubytki_z_zakresu_inspect_i_flaga_wykrywalny | wykrywalny == (glebokosc >= prog) | wieczorna | - |
| :184 | test_ubytek_w_pasie_brzegu_z_ustawien | `ub.z > bounds_max_z - pas` (pas po wysokosci z) | brak | - |
| :195, :200, :210, :215 | szum nan / szum zero / opcje zle (x9) / opcje z toml | walidacje | brak | - |
| :224, :232 | pusty stl / stl z nan | pomijanie projektu | wieczorna | - |
| :245 | test_transformacje_z_prawdy_sa_sztywne_i_nakladaja_kazda_prace | transformacje; ubytki `odleglosc_od_linii <= pas` (:269) | wieczorna | - |
| :275, :286, :300 | determinizm / prawda bez nazwy pliku / zapis nie nadpisuje | - | wieczorna | - |
| :319, :326, :332, :344 | CLI: zakres ubytkow (x4), zle wartosci (x4), nie nadpisuje, domyslne z ustawien | CLI | brak | - (:346 czyta `UST.PLIK_USTAWIEN`, patrz (e)) |
| :358, :371, :388, :396 | opcje K6 / CLI ukruszenia / CLI K6 zle (x6) / wersja 1 i pamiec linii | K6 | okragla_wieczorna (:374) | - |

### 1.12 test_uklad.py (107, 8), test_uklad_r58.py (221, 11), test_uklad_r59.py (321, 12)

Wszystkie: geometria ukladu, liczby gniazd, sumy SHA plikow modeli, ustawienia; brak skanu z ubytkiem i brak inspekcji.
Klasa "-" dla wszystkich 31 testow. Wazniejsze:
- test_uklad.py:23 test_gniazda_nie_nachodza_i_scianka_3mm (x4) - tylko kwadraty; gniazda okragle == kwadratu sprawdzane w test_uklad.py:53 i test_uklad_r59.py:108.
- test_uklad.py:53 test_plytki_okragle (x2: okragla_wieczorna_r54, okragla_poranna_r54) - ksztalt, dolki w polu, gniazda == kwadrat.
- test_uklad_r58.py:108-221 - kopie bajtowe R58 ukladow ramkowych, wczytanie, numery, stozki, STL (ramkowe).
- test_uklad_r59.py:235 test_praca_poza_gniazdem_i_dwie_w_rynience - plate na okragla_wieczorna (ubytki domyslne 0-2, nie sprawdzane).

### 1.13 test_okragle_ekran.py (476, 12), test_okragle_sesja.py (235, 14), test_okragle_wydanie.py (617, 22)

Brak asercji o inspekcji/ubytkach; klasa "-" dla wszystkich (48 testow). Zawartosc:
- ekran: sciecie z pola `flat` (:163, :179), mapa okragla (:197, :226), klik w gniazda (:248), kwadrat bez zmian (:286),
  roznica obrazu (:303, :309), okno wieczor/rano (:366, :391), `porownaj.opis_ukladu` (:428, :448). Uklady: wszystkie 6 okraglych.
- sesja: nazwy/rodziny ukladow, przyjecie skanow ramkowych, plan ramki, numery, ponowny skan - na wynikach sztucznych
  (`test_session_rano.Stanowisko`), `okragla_ramkowa_*`.
- wydanie: samokontrola (10 ukladow), metryki niezalezne od nazwy ukladu (:207, :228), T13, ZIP, symulator: :436
  (prawda skanu ramkowego z ubytkami 1-1, tylko tabela prawdy), :451 (powtarzalnosc + `plate.rozpoznaj_uklad`, bez inspekcji),
  :472-:600 scenariusz T2 i sterownik.

### 1.14 test_okragle_ramka.py (1409 linii, 46 test_*) - CZESCIOWO

Przejrzane: lista testow (Grep), :1-160, :950-975, :1196-1235. Plik dotyczy kalibracji i planu ramek swietlnych,
komunikatow kontrolera i numerow plytek ramkowych; wyniki skanow sztuczne (`symuluj_skan`, `plan_wieczor` z kolorami
podanymi w tescie). Brak inspekcji. Nie klasyfikowano pozostalych 40 testow.
- :954 test_r2_b1_..._mechanizm_zastany i :1199 test_r3_p2_..._mechanizm_zastany (x2) - patrz (c).

### 1.15 test_pula_match.py (791 linii, 32 test_*)

Fixture `plytka` (:83-96): `okragla_wieczorna`, `wersja_ubytkow=1`, `ubytki_na_prace` NIE nadpisane -> (0, 2).

| plik:linia | test | co sprawdza | uklad | klasa |
|---|---|---|---|---|
| test_pula_match.py:513 | test_porownaj_z_pula_wpisow_i_cli | porownaj z inspekcja: kandydat = wpis prawdy, `g["status"] == "zielony" and g["inspekcja"] is not None` (:526); CLI `--bez-inspekcji` | okragla_wieczorna | S1 (wynik inspekcji na pracach z 0-2 ubytkami nie sprawdzany) |
| test_pula_match.py:605 | test_p3_brak_nazw_plikow_przy_zlym_i_usunietym_stl | porownaj (inspekcja domyslna): tylko brak nazw plikow i uwaga "pominiety" | okragla_wieczorna | - (cel testu: nazwy) |
| test_pula_match.py:660 | test_r3_ocena_fpfh_niezalezna_od_obrotu_pracy | spearman >= 0,8; zmiana oceny <= 25 %; docstring: "gladkie atrapy rozni slabiej", pomiar na prawdziwych w raporcie | okragla_wieczorna | S5 |
| pozostale 29 (:111-:496, :543-:636, :683-:763) | budowa puli z wpisow, pamiec na dysku, kryteria 1-2, ranking wstepny, warianty wspolczynnika (B1 parametryzowany 7x7x2), ratunek | status dopasowania (zielony/zolty/nie zielony), wpisy, pamiec | okragla_wieczorna / brak | - |

### 1.16 test_ui.py (150 linii, 2 test_*)

| plik:linia | test | co sprawdza | uklad | klasa |
|---|---|---|---|---|
| test_ui.py:68 | test_okno_porownaj_mapa_klik_decyzja_zapis | prace z wykrywalnym ubytkiem: `status_gniazda in ("czerwony", "zolty")` (:85); prace cale: `status_gniazda == "zielony"` (:88); kolory mapy; zapis | okragla_wieczorna | S4 (`@pytest.mark.skip(reason=SZKIC_OKNA)` :67, bezwarunkowo) |
| test_ui.py:131 | test_okno_na_skanie_P2 | prace rozpoznane, nie szare, drgniecia zolte | z danych P2 | S4 (skip :129 + skipif :130) |

### 1.17 test_kontroler_api.py (1758 linii, 52 test_*) - CZESCIOWO

Fixture `st` (:317-326): parametry "atrapa" i "aplikacja"; "aplikacja" -> `pytest.skip` gdy brak `stanowisko/aplikacja.py`
(plik istnieje w worktree). Wyniki skanow sa sztuczne (opisy "zwykla"/"czysta"), nie z inspect.

| plik:linia | test | co sprawdza | uklad | klasa |
|---|---|---|---|---|
| test_kontroler_api.py:361 | test_a_kolory_gniazd_rowne_wynikowi_analizy_po_decyzjach | kolory = `kolory_oczekiwane(wynik)` dla 9 gniazd (zielony, czerwony, zolty, szary, pomaranczowy, nie_sprawdzono, blad_inspekcji, ...); decyzje | wieczorna (sztuczny wynik) | - |
| test_kontroler_api.py:761 | test_p4_zielony_tylko_przy_inspekcji_ok_i_znanym_dopasowaniu | "zielony" bez inspekcji / pominieto / nowy status inspect / nowy status match -> nie_sprawdzono / nieznany, kolor zolty | j.w. | - |
| test_kontroler_api.py:778 | test_p4_tabela_zadna_para_poza_zielony_ok_nie_jest_zielona | iloczyn kolor x status inspect x status match x status skanu: zielony tylko dla (zielony, ok, match zielony/zolty/None, skan != plytka_nie_z_trybu); `zielonych > 0` | brak | - |
| test_kontroler_api.py:1147 | test_statusy_jedna_tabela_kolorow_i_napisow | tabela statusow, `STATUSY_ZIELONE == ("zielony",)`, kazdy status inspect ma wiersz | brak | - |
| pozostale 48 | kontrakt kontrolera (decyzje, pytania, rano, polecenia) | - | - | nie klasyfikowano (nie przejrzane) |

### 1.18 test_session_wieczor.py (1630 linii, 55 test_*) - CZESCIOWO

| plik:linia | test | co sprawdza | uklad | klasa |
|---|---|---|---|---|
| test_session_wieczor.py:171 | test_k1_trzy_wyniki_trzy_skany_prace_i_statusy_jak_w_plikach | statusy z plikow `dane_sesji/wynik_plytka*.json` kopiowane 1:1 do bazy | z plikow JSON | - |
| test_session_wieczor.py:515 | test_k4_niezgodny_uklad_i_skan_ponownie_bez_zielonych | skan do powtorzenia: 0 zielonych w stanie, choc w pliku status_gniazda [zielony, zolty, zielony] (:522) | z plikow JSON | - |
| test_session_wieczor.py:1199 | test_d5r3_blad_inspekcji_i_sciezki_wzgledne_w_pliku_wyniku | blad inspekcji -> nie_sprawdzono / zolty w bazie | z plikow JSON | - |
| test_session_wieczor.py:1588 | test_wynik_prawdziwego_porownaj_wchodzi_do_bazy | prawdziwy porownaj (seed 1, ubytki 0-1, fi 0,8-1,4): tylko klucze wyniku, kopia statusow 1:1 do bazy, liczniki; bez porownania z prawda | okragla_wieczorna | S1 (w odniesieniu do wyniku inspekcji) |
| pozostale 51 | decyzje, ponowny skan, blokady, import CSV | - | - | nie klasyfikowano (nie przejrzane) |

## 2. Liczby

Testy (def test_*): przejrzane w calosci 287 (19 plikow); czesciowo 153 (test_okragle_ramka 46, test_kontroler_api 52,
test_session_wieczor 55). Liczby testow na plik - tabela w sekcji 0 i naglowki 1.x.

Klasy (liczone funkcje testowe, test moze miec kilka klas):

| klasa | liczba | testy |
|---|---|---|
| S1 | 4 | test_inspect.py:259; test_krawedz.py:78; test_pula_match.py:513; test_session_wieczor.py:1588 (+ poza zakresem: test_silnik.py:1777 porownuje silnik z CLI na plytkach z ubytkami 0-1, bez prawdy) |
| S2 | 8 | test_inspect.py:58, :79, :119; test_skala.py:193; test_match.py:63, :149; test_synth.py:34, :186 |
| S3 | 3 | test_inspect.py:119, :131, :140 |
| S4 | 9 | test_inspect.py:79, :140, :167, :576; test_ui.py:68, :131; test_synth.py:61; test_edge_synth.py:50, :95 |
| S5 | 22 | test_inspect.py:58, :79, :89, :97, :119, :131, :140, :216, :322, :348, :380, :395, :427, :453, :487, :517, :576; test_skala.py:193; test_krawedz.py:54, :78, :91; test_pula_match.py:660 |
| S6 | 2 | test_plate.py:150; test_straznik.py:122 |

Uwaga do S6: testy inspekcji maja odwrotna sytuacje - uzywaja wylacznie ukladu okraglego `okragla_wieczorna`; zaden
test nie sprawdza inspekcji na ukladzie kwadratowym ani ramkowym (inspect.py nie ma galezi zaleznej od ksztaltu plytki -
Grep `uk.shape` / `okragl` w inspect.py: brak trafien).

## 3. Odpowiedzi

### (a) Status KONCOWY gniazda (status_gniazda z porownaj) dla pracy z ubytkiem

Testy, w ktorych jest asercja o `status_gniazda` (albo kolorze) pracy z ubytkiem:
1. test_ui.py:68 - jedyny test lancucha skan -> porownaj -> `status_gniazda` dla prac z ubytkiem z prawdy
   (`in ("czerwony", "zolty")`, :85) i prac calych (`== "zielony"`, :88). Ubytki: `ubytki_na_prace=(0, 1)`, fi 0,8-1,4,
   polozenie losowe generatora (pas <= 1,5 mm od linii brzegu), seed szukany w petli 1-39 (:40-51). **Zawsze pomijany**
   (`@pytest.mark.skip`, :67).
2. test_inspect.py:246 - mapowanie na slowniku: `status_gniazda("zielony", {"status": "ubytek"}) == "czerwony"` (:248);
   bez skanu, bez ubytku geometrycznego. Mapowanie "sprawdz" / "sprawdz_ulozenie" -> zolty nie jest tu sprawdzane.
3. test_inspect.py:605 - metryki na slownikach (status_gniazda z `INSPECT_NA_STATUS`), bez skanu.
4. test_kontroler_api.py:361, :761, :778 - kolory w kontrolerze z wynikow sztucznych (slowniki), nie z inspect.
5. test_session_wieczor.py:171, :515 - statusy z plikow JSON `dane_sesji`, kopiowane do bazy.

Testy z prawdziwym ubytkiem w skanie, ale z asercja tylko na statusie INSPEKCJI (nie gniazda):
- test_inspect.py:58 (ubytki 1-2/prace, fi 0,6-1,4, glebokosc 0,7 r, losowo w pasie <= 1,5 mm od linii; seed 5);
- test_skala.py:193 (1-2/prace, fi 0,8-1,4; seed 5; +0,5 % skali);
- test_inspect.py:322, :348, :427, :517 (ukruszenie `wytnij_ukruszenie` "srodek", rozmiar 0,3 = promien kuli, na linii
  brzegu, odleglosc 0; :348 dodatkowo czasza r 0,35 na przesle ok. 7 mm od linii);
- test_inspect.py:487 (wgniecenie plaskie 0,3 mm: r 0,6 na scianie 0,7 mm pod wierzchem -> "ubytek"; r 0,8 na wierzchu -> "sprawdz").
Testy z ubytkami w skanie bez asercji o wyniku inspekcji: test_pula_match.py:513 (0-2/prace), test_session_wieczor.py:1588
(0-1/prace), test_okragle_wydanie.py:436/:451 (1/prace, tylko prawda i rozpoznanie), test_silnik.py:1777 (0-1/prace, poza zakresem).

Granica pasa 1,4-1,6 mm od linii brzegu (pas_brzegu_mm = 1,5): **zaden test nie stawia ubytku celowo w tym zakresie**.
Najblizsze: test_inspect.py:652 (ubytek 1,2 mm pod naroznikiem - tylko klasa polozenia "sciana", nie inspekcja),
test_synth.py:274 (1 mm - klasa polozenia), test_inspect.py:363 (ok. 7 mm - poza pasem). Generator losowy trzyma srodki
ubytkow `odleglosc_od_linii <= pas` (asercje test_edge_synth.py:269, test_synth.py:298), wiec srodek > 1,5 mm nie wystepuje;
przypadek 1,4-1,5 mozliwy tylko losowo i nie jest wyrozniony w zadnej asercji.

### (b) Uklady okragla_wieczorna_r54, okragla_poranna_r54, okragla_ramkowa_wieczorna, okragla_ramkowa_poranna

Co jest na nich sprawdzane - tylko rozpoznanie / geometria / UI / sesja / ramka; **zadnej asercji o inspekcji ubytkow**:
- okragla_wieczorna_r54: test_match.py:63, :79, :98, :118, :149, :178, :209 (dopasowanie, filtr, statusy match);
  test_plate.py:36, :55, :76 (wyrownanie, numer, poza gniazdem); test_straznik.py:55, :71, :93, :163, :179, :188, :200, :241,
  :267 (straznik ukladu; :179 porownaj z inspekcja bez asercji o niej, ubytki 0); test_auto_uklad.py:59, :74, :89;
  test_auto_uklad_r58.py:83; test_uklad.py:53; test_uklad_r59.py:188 (SHA); test_okragle_ekran.py:163, :303;
  test_dzien_skanera.py:1464, :1549, :1597, :1844 ("werdykt zielony" = kontrola jakosci skanu dnia skanera, prace bez ubytkow);
  test_session_wieczor.py:752-818 (reguly trybu).
- okragla_poranna_r54: test_plate.py:162 (bity dolkow); test_straznik.py (j.w.); test_auto_uklad.py:59, :74, :89, :168
  (porownaj `inspekcja=False`); test_auto_uklad_r58.py:83; test_uklad.py:53; test_okragle_ekran.py:163, :303;
  test_session_rano.py:783, :1003; test_session_wieczor.py:474, :752, :779-818.
- okragla_ramkowa_wieczorna / okragla_ramkowa_poranna: test_auto_uklad_r58.py (rozpoznanie; :303 porownaj `inspekcja=False`;
  :242, :268 ograniczenia znane); test_uklad_r58.py (pliki, wczytanie, gniazda == kwadrat R59, stozki, STL);
  test_okragle_ekran.py (mapa, klik, opis); test_okragle_sesja.py (sesja); test_okragle_wydanie.py (samokontrola, metryki,
  T13, ZIP, symulator - :451 tylko `rozpoznaj_uklad`); test_okragle_ramka.py (kalibracja, plan, komunikaty);
  test_ramka.py:1504-1508; test_ustawienia.py:48-49.

### (c) test_ograniczenie_znane_* i komentarze "ograniczenie znane" / "utrwala zachowanie"

- test_auto_uklad_r58.py:242 test_ograniczenie_znane_testowa_z_zaslonietym_dolkiem_pole_98_..._do_odwrocenia_po_wariancie_c -
  utrwala: plytka okragla testowa n8 z zaslonietym dolkiem D, pole 98 mm, 10 kandydatow -> `("wieczorna", True,
  "dolki_wykluczaja")`, numer None (:248-249); przy 8 kandydatach dobrze (:256). Docstring: "pogorszenie wprowadzone paczka".
- test_auto_uklad_r58.py:268 test_ograniczenie_znane_ramkowa_z_zaslonietymi_dolkami_bez_scianki_..._do_odwrocenia_po_wariancie_c -
  utrwala: ramkowa n2, 4 dolki zasloniete, bez scianki -> kwadrat "wieczorna", pewny True (z numerem i bez); "mapa gniazd
  dobra, zla nazwa ukladu" (:272, :283).
- test_auto_uklad_r58.py:216 test_male_pole_90_i_80_brak_wyniku_blad_wyrownania - "zachowanie do utrwalenia" (:218):
  brak wyniku (BladWyrownania).
- test_auto_uklad_r58.py:168 / :189 - utrwalaja: numer podany wygrywa nad numerem z dolkow, "program ich dzis nie
  konfrontuje" (:170); na kwadracie numer podany przyjety bez sprawdzenia (:190).
- test_okragle_ramka.py:954 ..._mechanizm_zastany - "Utrwalenie stanu faktycznego": po odpowiedzi "to nowy wsad" bez
  zdjecia plytki z ramki pod plytka z poprzedniego skanu swieci wynik OSTATNIEGO skanu (`swieci >= 5`, :970-971).
- test_okragle_ramka.py:1199 ..._mechanizm_zastany (x2) - "Utrwalenie stanu faktycznego - OGRANICZENIE ZNANE": inna plytka
  z numerem 2 i innymi pracami -> 0 pytan, 0 komunikatow, pod plytka lezaca (skan 1) swieci wynik NOWEGO skanu (:1220-1231);
  "ma zostac ODWROCONY" po twardszej regule (:1203).
- test_inspect.py:344 - utrwala, ze tryb `pas_brzegu_od="plaszczyzna"` daje "ok" i `ubytki == []` dla ukruszonego brzegu
  4 mm pod wierzchem (komentarz "przed P2: ukruszony brzeg = zielone").
- test_inspect.py:466-468 - komentarz "niepewna linia projektu to nasze ograniczenie, nie skanu - zielone z uwaga":
  tryb domyslny -> "ok".
- test_inspect.py:514 - statusy zapisane na sztywno "jak na main" (wgniecenie r 0,8 na wierzchu -> "sprawdz"/zolty).

### (d) Oczekiwane "ok" / "zielony" przy danych niepelnych

- test_inspect.py:135 (praca z wycietymi 30-60 % powierzchni): `assert wi.status not in ("ubytek", "skan_ponownie")` - ok dozwolone.
- test_inspect.py:161 (praca bokiem / do gory nogami, pokrycie < 1): `assert wi.status != "ubytek" and all(u.kolor != "czerwony" ...)` - ok dozwolone.
- test_inspect.py:583 (wyciete czesci powierzchni): `assert (wi.status == "ok") == wi.brzeg["sprawdzony"]` - ok oczekiwane, gdy brzeg sprawdzony.
- test_inspect.py:344 (tryb plaszczyzna, ukruszony brzeg poza pasem): `assert stary.status == "ok" and stary.ubytki == [] and stary.brzeg == {}`.
- test_inspect.py:419 (1/3 obwodu brzegu bez danych, progi z ustawien poluzowane: brzeg_min_sprawdzony 0,5, przerwa 50): `assert luz.status == "ok" and luz.brzeg["sprawdzony"]`.
- test_inspect.py:424 (brak danych przy linii, tryb plaszczyzna): `assert I.sprawdz(..., _ust(ust, pas_brzegu_od="plaszczyzna"), 7).status == "ok"`.
- test_inspect.py:468 (linia projektu niepewna, tryb domyslny): `assert suma.status == "ok" and suma.brzeg["sprawdzony"] and suma.brzeg["filary"][0]["powody"] == []`.
- test_inspect.py:475 (linia niepewna, plaszczyzna): `assert I.sprawdz(..., pas_brzegu_od="plaszczyzna"), 2).status == "ok"`.
- test_inspect.py:480 (brak linii brzegu - bryla bez wneki, tryb domyslny): `assert suma.status == "ok" and suma.brzeg["stan_linii"] == "brak" and "nie wyznaczono" in suma.brzeg["uwagi_linii"]`.
- test_inspect.py:510 (brak linii, tryb domyslny, wgniecenie): `assert suma.brzeg["stan_linii"] == "brak" and suma.brzeg["sprawdzony"] ...` - brzeg "sprawdzony" przy braku linii.
- test_inspect.py:552 (filar 2 bez linii, tryb domyslny): `assert suma.status == "ok" and suma.brzeg["sprawdzony"] and suma.brzeg["nie_sprawdzono"] == []`.
- test_inspect.py:251 (brak inspekcji): `assert PO.status_gniazda("zielony", None) == "zielony"`. (W kontrolerze ten przypadek
  jest zamieniany na nie_sprawdzono/zolty - test_kontroler_api.py:770-771.)

### (e) conftest.py, fixture wspolne, wylaczanie testow

- conftest.py (84 linie): sys.path, `import stanowisko` przed trimesh; fixture `korony` (session; 3 atrapy, rng 3),
  `korona_siekacz`, `uklad_tmp` (kopia uklad.json do tmp); funkcja `zapisz_ascii_stl`. **Brak markerow, brak
  `pytest_collection_modifyitems`, brak `addopts`, brak zmiennych srodowiskowych.** Brak pytest.ini / pyproject.toml /
  setup.cfg / tox.ini. README.md:15, :168: `py -3.12 -m pytest testy -q`. Brak markera typu "wolne".
- Pomijane z listy przegladu: test_ui.py:68 i :131 - zawsze (`@pytest.mark.skip(reason=SZKIC_OKNA)` :67, :129; :131
  dodatkowo skipif braku `dane/syntetyczne_P2` :130). To jedyny test z asercja `status_gniazda` dla prac z ubytkiem z prawdy.
- Warunkowe: test_kontroler_api.py:323/:860/:1731 - skip gdy brak `stanowisko/aplikacja.py` (plik jest w worktree);
  poza lista: test_silnik.py:1958 (warianty :1982, :1988) - skip bez E3A2_DANE_REF / E3A2_PROJEKTY; test_aplikacja.py:1142 -
  skipif bez E3A3_DANE_REF / E3A3_PROJEKTY; E3A2_SCISLE=1 zaostrza porownania w test_silnik (domyslnie poziom 2, tolerancja
  2e-3); liczne skipif `os.name != "nt"` (na Windows uruchamiane); test_katalog.py:133 - skipif braku folderu projektow
  na pulpicie; test_o4_ramka_rpi.py:92/:102/:140 - skip bez bash.
- Fakt srodowiskowy (nie marker): `stanowisko/ustawienia.toml` jest w .gitignore i **nie istnieje w tym worktree** (jest
  tylko `ustawienia.przyklad.toml`); `UST.wczytaj_ustawienia()` bez argumentu rzuca FileNotFoundError (ustawienia.py:348-354).
  Uzywaja go fixture/testy: test_inspect.py:19, test_porownaj_bledy.py:24, test_skala.py:21, test_match.py:17,
  test_straznik.py:156, test_auto_uklad.py:143/:170/:190, test_uklad.py:76, test_pula_match.py:43/:227/:768,
  test_session_wieczor.py:1607, test_ui.py:70/:137; test_edge_synth.py:346 czyta `UST.PLIK_USTAWIEN` wprost. W kopii
  roboczej uzytkownika plik istnieje (`...\Desktop\Ramki\stanowisko\ustawienia.toml`), wiec progi w tych testach pochodza
  z lokalnego pliku maszyny, nie z `ustawienia.przyklad.toml` (zawartosci lokalnego pliku nie czytano).
  test_auto_uklad_r58.py:39 i test_okragle_* uzywaja `UST.PLIK_PRZYKLADU`.
