# S1 - lancuch analizy skanu: skad bierze sie zielone (23.11.2026)

Podstawa: galaz `analiza/s1` od `origin/analiza/plan` 480359f (= `main` b856b9e + folder planu). Kod sie nie zmienil - to raport.
Sesja glowna: Fable 5.2; subagenci: Opus 5.5 xhigh (lista na koncu). Proby: 2 wlasne skrypty, lacznie 37 s czasu PC
(`S1/proba_inspect.py` 9 s, `S1/proba_inspect2.py` 28 s) + bieg testow subagenta (sekcja 9).

Skroty: "zielone" = `status_gniazda` = `zielony` w wyniku `porownaj`; "linia" = linia krawedzi brzegu filaru z `krawedz`;
"pas" = `[inspect] pas_brzegu_mm` = 1,5 mm; tryb domyslny = `pas_brzegu_od = "linia_i_plaszczyzna"`.
Wszystkie proby sa na brylach testowych i skanach sztucznych - zachowanie prawdziwego skanera: `[NIE SPRAWDZONE BEZ SPRZETU]`.

## 0. Odstepstwa od planu przy starcie sesji

- Sesja dziala na koncie Windows `<uzytkownik>`, nie `<konto-PC>`: git zglosil "dubious ownership"; po zgodzie wlasciciela dodany
  wyjatek `safe.directory <PC-katalog>/qc` (globalny gitconfig konta `<uzytkownik>`).
- `git fetch origin` NIE dziala z tego konta ("could not read Username for https://github.com"; `gh auth status`: token
  konta `mbuas` niewazny). Worktree zalozony z lokalnej kopii `origin/analiza/plan` (480359f, 23.11); pliki planu w worktree
  sa bajtowo rowne kopii `<PC-katalog>\analiza_kodu_2026-11-23\` (3 z 3 porownanych plikow).
- `Ramki/stanowisko/ustawienia.toml` nie istnieje ani w worktree, ani w klonie `<PC-katalog>\qc` - proby biora wartosci z
  `ustawienia.przyklad.toml` (sa rowne wartosciom domyslnym; wynik subagenta w sekcji 9).

## 1. Najwazniejsze znaleziska

| Nr | Waga | Jedno zdanie |
|---|---|---|
| S1-01 | B | Ubytek brzegu, ktorego powierzchni przelomu NIE ma w skanie (dziura w siatce), jest zielony - w probie do fi 1,4 mm; dziura w danych skanu wzdluz brzegu do 3,0 mm dlugosci tez daje zielone ("brzeg sprawdzony"). |
| S1-02 | B | Zaglebienie bez "ostrej krawedzi" (plytki odprysk, krawedz wygladzona przez skaner) jest odrzucane po cichu jako `lagodna` - 0,12 mm x fi 1,0 i 0,19 mm x fi 1,8 na samej krawedzi brzegu wychodza na zielono, bez uwagi. |
| Z1 | znane | T2 (e) pozycja 8 - przyczyna w kodzie: plama jest oceniana po SRODKU rdzenia (`inspect.py:354`), a nie po zasiegu; odrzucona plama `poza_pasem` nie zmienia statusu i nie zostawia uwagi. Ubytek fi 0,92 x 0,32 mm, ktorego brzeg siega 1,10 mm od linii, jest zielony. |
| S1-03 | P | Metoda A zalezy od gestosci wierzcholkow skanu: przy odstepie 0,20 mm ubytek fi 0,5 x 0,17 mm jest zielony, a przy 0,15 mm metoda A przestaje dzialac dla wszystkich rozmiarow (zostaje sama B: tylko ubytki >= 0,2 mm glebokie, czerwone dopiero od 0,4 mm). |
| S1-04 | P | Ograniczenie "najwyzej zolty" z `match` (wynik niepewny: niepelne dopasowanie puli, ratunek, fragment wyzszy niz projekt) ginie: `porownaj.status_gniazda` przy inspekcji `ok` daje zielone, a `statusy.py:128` to dopuszcza. |
| S1-05 | P | Projekt bez linii brzegu (bryla bez wneki >= 1 mm, nieudane wyznaczenie) w trybie domyslnym ma `brzeg.sprawdzony = True` bez zadnego wymogu danych - zielone takze wtedy, gdy brzegu w skanie w ogole nie ma (9 % linii widoczne). |
| S1-06 | P | Projekt wczytany do puli w zlej orientacji (plik nie-exocad, heurystyka; ostrzezenie wyciszone) nie ma linii, pas brzegu trafia na strone zujaca - ubytek fi 1,1 mm na brzegu, czerwony przy dobrej orientacji, wychodzi na zielono. |
| S1-07 | P | Mosty / prace wieloczlonowe: niepewna linia filaru i filar bez linii to w trybie domyslnym tylko uwaga; brzeg lezacy glebiej niz 1,5 mm pod wierzchem pracy jest wtedy sprawdzany przy niepewnej linii albo wcale; filar bez przyjetej niecki nie ma nawet uwagi. |
| S1-08 | P | `porownaj.status_gniazda` jest "otwarty na zielone": brak inspekcji, status `pominieto` i kazdy nieznany status inspekcji daja kolor z `match` (zielony). |

Lacznie nowych: B 2, P 6, D 7 (tabela w sekcji 4). Sprawa znana z dopisana przyczyna: Z1.

## 2. T2 (e) "pozycja 8" - sciezka w kodzie (sprawa znana, przyczyna)

Fakty z `Ramki/etap3/odbior_koncowy/RAPORT.md` 5a: ubytek fi 0,926 x 0,324 mm, srodek 1,505 mm od linii brzegu; silnik znalazl
plame (0,839 x 0,394 mm, 726 punktow, 1,569 mm od brzegu) i nadal jej rodzaj `poza_pasem`; praca zielona 6 z 6.

Sciezka (`stanowisko/inspect.py`, funkcja `plamy_pod_powierzchnia`):
1. linia 307: rdzen plamy = punkty skanu `d <= -prog_glebokosci_mm` (0,08);
2. linia 325: `c = Q.mean(0)` - srodek plamy = srednia punktow rdzenia. Rdzen jest przesuniety wzgledem punktu z prawdy
   (generator stawia SRODEK KULI 0,3 r nad powierzchnia, `synth.py:462`, a w prawdzie zapisuje punkt na powierzchni);
3. linie 339-342: `odl_brzegu` = odleglosc `c` od najblizszej stacji linii O / I, w trybie domyslnym `min` z odlegloscia
   pod plaszczyzna z = 0;
4. linia 354: `elif odl_brzegu > ust_i["pas_brzegu_mm"] and not na_kraw: rodzaj = "poza_pasem"` - porownanie SRODKA z pasem;
   zasieg plamy (srednica) nie bierze udzialu;
5. `polacz` (linia 653) bierze tylko plamy `ubytek`; `sprawdz` (linie 732-741) nie ma galezi dla `poza_pasem`, wiec status
   zostaje poczatkowe `"ok"` (linia 691); do `uwagi` trafiaja tylko plamy `brak_danych` (linie 746-748) - plama `poza_pasem`
   jest tylko w liscie `plamy` w JSON;
6. metoda B nie pomaga: probka pasa konczy sie na 1,5 mm od linii (`probka_od_linii`, linia 402), a wciecie musi miec
   >= 0,2 mm cofniecia (linia 484) - na skraju kuli ubytku glebokosc jest mniejsza;
7. `porownaj.status_gniazda` (linie 88-92): `ok` -> `zielony`.

Klasa (proba B w `S1/proba_inspect_wynik.txt`, bryla z wneka, kula fi 0,92 x 0,32 mm na scianie zewnetrznej):

| srodek ubytku od linii | brzeg kuli od linii | plama | status |
|---|---|---|---|
| 1,02 / 1,32 / 1,46 mm | 0,56 / 0,86 / 1,00 mm | `ubytek` | `sprawdz` (zolte) |
| 1,56 mm | 1,10 mm | `poza_pasem` (288 pkt, 0,32 mm) | `ok` (zielone) |
| 1,71 / 2,01 mm | 1,25 / 1,55 mm | `poza_pasem` | `ok` (zielone) |

Inne ubytki tej samej klasy, ktore przejda tak samo:
- kazdy ubytek, ktorego srodek rdzenia lezy dalej niz 1,5 mm od linii, niezaleznie od rozmiaru: przy fi 1,4 mm ubytek siegajacy
  0,8 mm od linii jest zielony; skok jest ostry (1,46 -> zolte, 1,56 -> zielone), bez strefy posredniej;
- ubytki scian przesel i lacznikow ponizej 1,5 mm od wierzchu pracy (poza oboma pasami) - z definicji poza kontrola;
- ubytek na brzegu glebokiego filaru, gdy linia tego filaru "uciekla" (S1-07): odleglosc liczona od zlej linii;
- wyjatek dzialajacy w druga strone: plama do 0,5 mm od ostrej krawedzi projektu (`na_kraw`, linia 343) liczy sie zawsze -
  wiec wynik zalezy od tego, czy projekt ma w tym miejscu krawedz > 40 st. (7 z 17 projektow puli ma < 5 mm takich krawedzi).
Znacznik prawdy `wykrywalny` (`synth.py:925-928`, uzycie 974) nie zna polozenia - to juz jest w RAPORT 5a (wariant 2).
Decyzji nie proponuje (zastrzezona dla wlasciciela); z kodu wynika tylko, ze sa trzy niezalezne dzwignie: kryterium "srodek
czy zasieg", szerokosc pasa, oraz to, czy odrzucona duza plama ma zostawiac zolte / uwage.

## 3. Wszystkie sciezki, ktorymi gniazdo konczy jako zielone

Kolor powstaje w `porownaj.status_gniazda(status_match, inspekcja)` (`porownaj.py:88-92`).

| Nr | Warunek | Czy brzeg faktycznie sprawdzony | Znalezisko |
|---|---|---|---|
| G1 | `match` = `zielony` (pokrycie >= 0,85, pewnosc >= 0,1), inspekcja `ok` | zalezy od wiersza I1-I10 | - |
| G2 | `match` = `zolty` (ograniczenie "najwyzej zolty" przy pokryciu >= 0,85), inspekcja `ok` | jak G1, ale projekt moze byc zly | S1-04 |
| G3 | `match` = `zielony`, `inspekcja` = None (`inspekcja=False` / `--bez-inspekcji`; kandydat bez transformacji) | NIE | S1-08 |
| G4 | `match` = `zielony`, status inspekcji `pominieto` albo nieznany tej wersji | NIE | S1-08 |

Inspekcja konczy sie `ok` (`inspect.py:691` - wartosc poczatkowa; nikt jej potem nie ustawia), gdy:

| Nr | Sytuacja | Miejsce w kodzie | Czy brzeg sprawdzony | Znalezisko |
|---|---|---|---|---|
| I1 | brak punktow <= -0,08 mm, brak wciec, kazdy filar ma dane na >= 90 % linii i przerwe <= 1,5 mm | 307-309, 526-530 | tak (z tolerancja 0,8 mm - I7) | - |
| I2 | plama `poza_pasem` (srodek > 1,5 mm od linii i od z = 0) | 354 | nie dotyczy brzegu | Z1 |
| I3 | plama `lagodna` (pierscien 0,15 mm: mediana abs(d) > 0,04 mm), fi rdzenia <= 1,5 mm | 330, 350-351 | NIE - odrzucona | S1-02 |
| I4 | plama `brak_danych` (pierscien < 6 punktow) | 344-345 | NIE - tylko uwaga "N miejsc bez danych" | S1-03 |
| I5 | plama `za_mala` (fi rdzenia < 0,1 mm) albo skupisko < 6 punktow | 317-318, 352-353 | NIE | S1-03 |
| I6 | wciecie `za_male` (szerokosc < 0,2 mm albo < 6 punktow probki) albo `brak_danych` (otoczenie < 50 %) | 499-502 | NIE | S1-03 |
| I7 | w skanie nie ma punktow w miejscu ubytku, ale w promieniu 0,8 mm jest wierzcholek o zgodnej normalnej | 426, 467-476, 484 | NIE - liczone jako "linia ciagla" | S1-01 |
| I8 | filar ma dane na 90-100 % linii i przerwe <= 1,5 mm (po odjeciu tolerancji 0,8 mm z kazdej strony) | 526-530, 587-591 | czesciowo | S1-01 |
| I9 | projekt bez linii, tryb domyslny: `sprawdzony = True` zawsze; metoda B przy linii < 90 % tylko uwaga | 579-583, 514-518 | NIE | S1-05, S1-06 |
| I10 | linia niepewna / filar bez linii / filar bez niecki, tryb domyslny | 597-607, 622-626; `krawedz.py:779-781, 813-815` | tylko pas od plaszczyzny albo wcale | S1-07 |
| I11 | `pokrycie` = NaN (porownanie `<` zwraca False) | 707 | bramka pokrycia pominieta | S1-10 |

Sciezki NIE dajace zielonego (sprawdzone czytaniem): drgniecie -> `skan_ponownie` (696-700); pokrycie < 0,85 ->
`popraw_ulozenie` (707-716; granica: 0,85 przechodzi, 0,849 nie - proba G); wyjatek w inspekcji -> `nie_sprawdzono`
(`porownaj.py:222-225`); `match` = `szary` -> szare bez inspekcji (`porownaj.py:90, 216`); uklad niezgodny -> zadnych gniazd
(`porownaj.py:288-318`); NaN w punktach / transformacji -> `cKDTree` rzuca `ValueError` -> `nie_sprawdzono`.

## 4. Tabela znalezisk

Plytka: wszystkie znaleziska B i P dotycza KAZDEJ plytki (kod inspekcji i statusu jest wspolny dla kwadratowych, okraglej R54
i okraglych ramkowych n1-n6); wyjatki zaznaczone. Koszt potwierdzenia: T = zrobione w tej sesji (do 3 min).

| Id | plik:linia | Co jest zle | Skutek na stanowisku | Plytka | Waga | Dowod | Koszt | Sprzet 28-29.11 |
|---|---|---|---|---|---|---|---|---|
| S1-01 | `inspect.py:426, 467-484, 587-591, 526-530` | "Dane skanu przy brzegu" = wierzcholek o zgodnej normalnej w 0,8 mm od punktu pasa; brak powierzchni w miejscu ubytku nie jest ani ubytkiem, ani brakiem danych. Dozwolona przerwa 1,5 mm liczy sie PO tej tolerancji. | Praca z odpryskiem brzegu, ktorego skaner nie odwzorowal (dziura w siatce, zaslona), jest zielona; dziura w danych do 3,0 mm wzdluz brzegu nie daje "nie sprawdzono". | kazda | B | proba C i F (`S1/proba_inspect_wynik.txt`) | T | TAK: ukruszona praca na R54 nr 8 - obejrzec siatke skanu w miejscu odprysku (czy sa wierzcholki na przelomie) i wynik; zakleic 2-3 mm brzegu calej pracy czarna tasma / plastelina i sprawdzic, czy wychodzi "nie sprawdzono". |
| S1-02 | `inspect.py:330, 346-351` | Plama bez ostrej krawedzi i o fi rdzenia <= 2,0 mm jest odrzucana (`lagodna`) bez sladu w statusie i uwagach; kryterium ostrosci: mediana abs(d) w pierscieniu 0,15 mm <= 0,04 mm. | Plytki odprysk (0,1-0,2 mm glebokosci) i kazdy ubytek, ktorego krawedz skaner wygladzi, jest zielony. Glebsze (>= 0,2 mm) lapie jeszcze metoda B - na zolto. | kazda | B | proba D | T | TAK: skan pracy z plytkim odpryskiem; w `_wynik.json` gniazda policzyc plamy `rodzaj = lagodna` i ich `pierscien_mediana_mm` - jesli prawdziwe ubytki maja > 0,04, metoda A ich nie widzi. |
| S1-03 | `inspect.py:78, 317, 321, 344` + `[inspect] min_punktow_plamy`, `krawedz_pas_mm` | Progi metody A sa w mm i w liczbie punktow, a punkty = wierzcholki siatki skanera (`plate.py:597, 533`); przy odstepie >= 0,15 mm pierscien 0,15 mm ma < 6 punktow -> `brak_danych`. | Przy rzadszej siatce skanera plytkie ubytki (< 0,2 mm) sa zielone, glebsze tylko zolte (czerwone dopiero od wciecia 0,4 mm). | kazda | P (B, jesli skaner da odstep >= 0,15 mm) | proba H (`S1/proba_inspect2_wynik.txt`) | T | TAK, 5 min: mediana dlugosci krawedzi trojkatow na pracy w pierwszym skanie; jesli > 0,10 mm - wynik metody A z testow sztucznych nie przenosi sie. |
| S1-04 | `porownaj.py:88-92`; `match.py:1220-1226`; `statusy.py:128, 177` | `match` celowo obniza status do `zolty` ("pewnosc wzgledem niedopasowanych kandydatow nieznana", "fragment wyzszy niz projekt"), ale kolor gniazda bierze sie z samej inspekcji: `zolty` + `ok` = zielony. | Praca rozpoznana niepewnie (lezaca bokiem / czesciowo widoczna / duza pula) moze byc zielona wzgledem projektu, ktory nie jest jej projektem; uwaga jest tylko w `uwagi`. | kazda; czesciej przy duzej puli per praca | P | proba A + czytanie | T (logika); S (ile takich prac na zestawach R59: przejrzec wyniki T10 pod katem `status` = zolty i `status_gniazda` = zielony) | TAK: prace polozyc bokiem / do gory nogami i sprawdzic w JSON pary `status` / `status_gniazda`. |
| S1-05 | `inspect.py:579-583, 514-518, 337` | Tryb domyslny: projekt bez zadnej linii brzegu dostaje `sprawdzony: True` bez sprawdzenia danych; gdy linia pasa jest widoczna w < 90 %, metoda B jest pomijana z sama uwaga. | Praca bez wneki >= 1 mm (inlay, onlay, licowka, przeslo) albo z nieudanym wyznaczeniem linii jest zielona takze wtedy, gdy brzeg nie jest w skanie widoczny. | kazda | P | proba E | T | TAK, jesli w puli testowej jest taka praca: w JSON `inspekcja.brzeg.stan_linii = "brak"` oznacza "brzegu nie pilnuje nic poza pasem od wierzchu". |
| S1-06 | `synth.py:209-219`; `match.py:211-213`; skutek w `inspect.py:579-583` | Orientacje pliku innego niz `*_cad.stl` wybiera heurystyka; wynik `niejasny` = zalozenie "brzeg na dole" z ostrzezeniem, ktore `match.Projekt` wycisza. Zla orientacja nie jest potem wykrywana. | Wszystkie prace takiego projektu sa zawsze zielone (brzeg nigdy nie sprawdzony); jedyny slad to uwaga "linii brzegu projektu nie wyznaczono". | kazda; tylko pliki nie-exocad | P | proba I | T | TAK: w kazdym wyniku policzyc prace z `stan_linii = "brak"`; dla koron powinno byc 0. |
| S1-07 | `inspect.py:597-607, 622-626`; `krawedz.py:60-61, 779-781, 813-815` | Tryb domyslny: stacja "sprawdzona" = ma dane skanu; niepewna linia i filar bez linii ida do uwag. Filar, ktorego niecka nie spelnia progu (pole 2 mm2, glebokosc 1,0 mm w skali 1,22), nie trafia nawet do `filary_bez_linii` - brak uwagi, `stan` moze byc `wiarygodne`. | Most: ubytek brzegu filaru przy laczniku (srednio 16 % obwodu filarow prac wieloczlonowych; 9 z 23 petli puli testowej jest `czesciowa`) moze byc zielony, gdy brzeg lezy > 1,5 mm pod wierzchem pracy. | kazda; mosty i prace wieloczlonowe (rynienki) | P | czytanie (liczby z `opisy_modulow/krawedz.md`, `inspect.md`) | D: prawdziwe projekty mostow sa poza repo; trzeba by ubytki stawiac na niezweryfikowanych odcinkach linii (dzis generator tego nie robi - `synth.py:448-450`) | TAK: most z ukruszonym brzegiem filaru od strony przesla; odczytac `brzeg.uwagi_linii`. |
| S1-08 | `porownaj.py:63-64, 90-92` | Brak inspekcji, `pominieto` (mapowane na None) i nieznany status -> `or status_match`, czyli zielony. | W `porownaj` (CLI, mapa PNG, okno testowe, liczniki `statusy_gniazd`, metryki) praca bez inspekcji jest zielona. W programie glownym chroni przed tym `statusy.status_pracy` (S3). | kazda | P | proba A | T | czesciowo: `porownaj --bez-inspekcji` na jednym skanie - mapa cala zielona. |
| S1-09 | `inspect.py:346-349, 736-739` | Plama > 1,5 mm z ostra krawedzia = `sprawdz_ulozenie`; > 2,0 mm bez ostrej krawedzi = `poprawka`. | Duze wylamanie brzegu nie jest czerwone: zolte z napisem "sprawdz ulozenie" albo pomaranczowe "poprawka reczna" (chyba ze metoda B da wciecie >= 0,4 mm). | kazda | D | czytanie | S: proba z kula fi 2-3 mm | TAK: praca z duzym wylamaniem - jaki napis. |
| S1-10 | `inspect.py:707` | `pokrycie < prog` przy NaN jest False - bramka "popraw ulozenie" nie dziala. | Dzis nieosiagalne (`match.ocena` liczy srednia z niepustej tablicy). | kazda | D | proba G | T | nie |
| S1-11 | `inspect.py:691` | Status poczatkowy `"ok"`; kazda galaz, ktora nie ustawi statusu, konczy zielono (takze dodana w przyszlosci). | Zrodlo wierszy I2-I6, I9. | kazda | D | czytanie | - | nie |
| S1-12 | `testy/test_inspect.py:480, 468, 86, 61` (pelna lista: sekcja 8) | Testy utrwalaja zielone w przypadkach S1-05 / S1-07 i maja luzne progi. | Poprawka S1-05 / S1-07 wymaga odwrocenia asercji; testy nie pilnuja granicy pasa. | - | D | czytanie + subagent C | - | nie |
| S1-13 | sekcja 9.2 (11 pozycji) | Rozjazdy opis - kod; regula koloru gniazda nie jest opisana w zadnym pliku opisu. | Nowa sesja czytajaca opis dostaje nieaktualny obraz (np. "uklad wybiera czlowiek"). | - | D | subagent B + sprawdzenie 6 z 6 | T | nie |
| S1-14 | `ustawienia.py:19-21, 348-354`; 18 plikow testow | Testy `inspect` / `skala` / `straznik` / `porownaj_bledy` biora progi z lokalnego, niewersjonowanego `ustawienia.toml`; w czystym worktree 63 ze 142 uruchomionych testow konczy sie bledem przygotowania. | Wynik testow zalezy od pliku na danej maszynie; w tej sesji testow inspekcji nie dalo sie uruchomic. | - | D | subagent D (`S1/log_*.txt`) | T | nie |
| S1-15 | `porownaj.py:201-206` | Wyjatek w `match.dopasuj` / `ratuj_plytke` nie jest lapany na gniazdo (inaczej niz inspekcja). | Blad dopasowania jednej pracy = brak wyniku calej plytki (zakres S2). | kazda | D | czytanie (subagent A) | - | nie |

## 5. Opis znalezisk B i P

### S1-01 (B) - brak powierzchni przelomu w skanie = zielone

Obie metody potrzebuja punktow skanu NA przelomie: A liczy punkty pod powierzchnia projektu (`inspect.py:307`), B szuka dla
kazdego punktu pasa najblizszego wierzcholka skanu o zgodnej normalnej w promieniu `BRAK_DANYCH_MM` = 0,8 mm (linie 426, 467)
i uznaje wciecie tylko wtedy, gdy ten wierzcholek lezy >= 0,2 mm POD punktem pasa i glownie pod nim, nie z boku (linia 484).
Gdy w miejscu odprysku siatka skanu ma dziure, najblizszy wierzcholek lezy z boku na nieuszkodzonej powierzchni: `pod` ~ 0,
wiec punkt liczy sie jako "linia ciagla" i jako "ma dane". Generator skanow sztucznych zawsze wstawia powierzchnie przelomu
(czasza kuli z punktami co 0,05 mm, `synth._wytnij_kule`), wiec zaden pomiar T10 / R59 tego przypadku nie zawiera.

Proba C (ubytek na plaskiej krawedzi brzegu; ta sama bryla, ten sam skan, roznica = usuniete punkty czaszy):

| ubytek | przelom w skanie | przelomu brak |
|---|---|---|
| fi 0,50 x 0,17 mm | `sprawdz` (A, zolte) | `ok` - zielone |
| fi 0,80 x 0,28 mm | `sprawdz` (A, zolte) | `ok` - zielone |
| fi 1,10 x 0,39 mm | `ubytek` (A+B, czerwone) | `ok` - zielone |
| fi 1,40 x 0,49 mm | `ubytek` (A+B, czerwone) | `ok` - zielone |

W kazdym wierszu `brzeg.sprawdzony = True`, `udzial_z_danymi = 1,0`, zero uwag.

Proba F (luk linii brzegu bez zadnych punktow skanu, w pasie 2,5 mm od linii, linia O dlugosci 17,6 mm):

| dlugosc dziury | udzial z danymi | najdluzsza przerwa wg programu | status |
|---|---|---|---|
| 1,0 / 1,5 mm | 1,00 | 0,0 mm | `ok` |
| 2,0 mm | 0,98 | 0,41 mm | `ok` |
| 2,5 mm | 0,95 | 0,94 mm | `ok` |
| 3,0 mm | 0,92 | 1,44 mm | `ok` |
| 3,5 mm | 0,89 | 1,89 mm | `nie_sprawdzono` |

Czyli prog `brzeg_max_przerwa_mm` = 1,5 odpowiada faktycznej dziurze ok. 3 mm (1,5 + 2 x ok. 0,8), a ubytek z planu ma
najwyzej 1,5 mm. Opis `inspect.md` ("dane skanu przy linii = wierzcholek ... w 0,8 mm") podaje regule, ale nie ten skutek.
Czy prawdziwy skaner zostawia dziury na odpryskach (stroma, blyszczaca sciana przelomu), czy je zalepia - `[NIE SPRAWDZONE BEZ
SPRZETU]`; jesli zalepia plaska blona, przypadek przechodzi w S1-02.

### S1-02 (B) - plama bez ostrej krawedzi odrzucana po cichu

`ostra = n_pier >= 6 and med_pier <= prog / 2` (linia 330): w pierscieniu 0,15 mm wokol rdzenia mediana odchylki ma byc
<= 0,04 mm. Plama nieostra: > 2,0 mm -> `poprawka` (pomaranczowe), 1,5-2,0 mm -> `sprawdz_ulozenie` (zolte), <= 1,5 mm ->
`lagodna` = odrzucona (linie 346-351). Rdzen jest mniejszy niz ubytek (fi 1,8 mm o glebokosci 0,19 ma rdzen 0,94 mm), wiec do
`lagodna` trafiaja zaglebienia o srednicy nawet ok. 2,5 mm.

Proba D (zaglebienie g x (1 - (rho/R)^2)^2 na srodku plaskiej krawedzi brzegu, bez szumu):

| glebokosc | srednica | plama | mediana pierscienia | status |
|---|---|---|---|---|
| 0,12 mm | 1,0 mm | `lagodna` | 0,055 | `ok` - zielone |
| 0,19 mm | 1,0 mm | `ubytek` | 0,040 | `sprawdz` |
| 0,19 mm | 1,8 mm | `lagodna` | 0,062 | `ok` - zielone |
| 0,30 mm | 1,0 mm | `ubytek` | 0,032 | `sprawdz` |
| 0,30 mm | 1,8 mm | `lagodna` + wciecie B 0,30 | 0,055 | `sprawdz` (ratuje metoda B) |

Wniosek: ponizej 0,2 mm glebokosci (`wciecie_min_mm`) jedynym detektorem jest metoda A, a ta odrzuca wszystko, co ma lagodne
zbocze. Wynik 0,19 x 1,0 mm lezy dokladnie na progu (0,0396 wobec 0,04) - kazde wygladzenie krawedzi przez skaner przesuwa
go na zielone. `inspect.md` przewiduje to ("scanner wygladza krawedzie ubytkow - pierscien 0,15 mm moze wymagac poszerzenia"),
ale jako strojenie progu; nie mowi, ze skutkiem jest zielone bez uwagi. Szum generatora (sigma 0,03 -> mediana abs(szumu) 0,02)
zostawia tylko 0,02 mm zapasu do progu ostrosci.

### S1-03 (P) - gestosc siatki skanu

Punkty fragmentu to wierzcholki siatki skanu (`plate._przygotuj`, `plate.py:597`; `potnij_na_fragmenty`, linia 533). Metoda A
wymaga >= 6 punktow rdzenia polaczonych co <= 0,25 mm i >= 6 punktow w pierscieniu 0,15 mm. Skany sztuczne maja przy ubytku
punkty co 0,05 mm (`[synth] odstep_ubytku_mm`).

Proba H (ubytek na krawedzi brzegu, przelom w skanie, losowe punkty o zadanym srednim odstepie):

| ubytek | 0,05 mm | 0,10 mm | 0,15 mm | 0,20 mm | 0,25 mm |
|---|---|---|---|---|---|
| fi 0,50 x 0,17 | zolte (A) | zolte (A) | zolte (A, 6 pkt rdzenia, 8 pierscienia - na progu) | ZIELONE | ZIELONE |
| fi 0,80 x 0,28 | zolte (A) | zolte (A) | zolte (B; A = `brak_danych`) | zolte (B) | zolte (B) |
| fi 1,10 x 0,39 | czerwone (A+B) | czerwone (A+B) | zolte (B) | zolte (B) | zolte (B) |
| fi 1,40 x 0,49 | czerwone | czerwone | czerwone | czerwone (B) | czerwone (B) |

Od odstepu 0,15 mm plama metody A dostaje `brak_danych` (pierscien < 6 punktow), wiec czerwone A+B znika, a wszystko ponizej
0,2 mm glebokosci jest zielone. To jest pierwsza rzecz do zmierzenia na prawdziwym skanie.

### S1-04 (P) - zolte z `match` ginie w kolorze gniazda

`match._zakoncz` (linie 1220-1226) zamienia `zielony` na `zolty`, gdy czesc kandydatow nie miala pelnego dopasowania albo gdy
zwyciezca ratunku nie spelnia reguly wysokosci - opis `match.md` 8b (4) podaje powod: "bez tego maly fragment pracy do gory
nogami dostal zielony ze zlym projektem". Inspekcja jest jednak liczona dla kazdego statusu innego niz `szary`
(`porownaj.py:216`) i jej `ok` daje zielone gniazdo (`INSPECT_NA_STATUS`, linia 92); `statusy.DOPASOWANIA_ZIELONE = ("zielony",
"zolty")` (`statusy.py:128`) przepuszcza to do ekranu. Proba A: `status_gniazda("zolty", {"status": "ok"})` = `zielony`.
Kiedy pokrycie >= 0,85 idzie w parze z `zolty`: duza pula per praca (ranking wstepny z wiecej niz 12 kandydatami w marginesie
albo ranking plaski), ratunek pracy, ktora nie przeszla filtru wymiarow, zwyciezca "wyzszy niz projekt".
Test `test_inspect.py::test_status_gniazda_i_scenariusz` - patrz sekcja 8.

### S1-05 (P) i S1-06 (P) - projekt bez linii brzegu; zla orientacja projektu

`ocena_brzegu` dla `linie.filary == []` w trybie domyslnym zwraca `sprawdzony: True` (linie 581-583) - zamysl: "jak przed P2".
Ale przed P2 nie bylo zadnego zabezpieczenia przed brakiem danych, wiec dla takich projektow status `nie_sprawdzono` nie
istnieje. Metoda B przy `udzial_ciagly` < 0,9 zamienia wciecia na `brak_danych` i dopisuje uwage (linie 514-518).

Proba E (pudelko 8 x 6 x 5 mm bez wneki, tryb domyslny / tryb `linia`):

| skan | linia pasa widoczna | tryb domyslny | tryb `linia` |
|---|---|---|---|
| pelny | 100 % | `ok` | `nie_sprawdzono` |
| bez gornych 2 mm po jednej stronie | 62 % | `ok` + uwaga "metoda B pominieta" | `nie_sprawdzono` |
| bez gornych 2 mm w calosci | 9 % | `ok` + uwaga | `nie_sprawdzono` |

Proba I (ta sama bryla z wneka i ubytkiem fi 1,1 x 0,39 mm na krawedzi brzegu): projekt w puli brzegiem do gory -> `ubytek`
(A+B, czerwone); ten sam plik wczytany z obrotem 180 st. (`brzeg_dol` dla bryly z brzegiem na gorze = bledna orientacja) ->
0 filarow, `stan_linii = brak`, plama `poza_pasem` (5,75 mm od "brzegu"), status `ok`, zielone.
Kiedy orientacja moze byc zla: plik o nazwie innej niz `*_cad.stl` (`synth.plik_exocad`), dla ktorego heurystyka krawedzi
wskaze zla strone albo `niejasny` (wtedy "brzeg na dole" + `warnings.warn`, a `match.Projekt.__init__` lapie ostrzezenia:
`match.py:211-213`). Silnik podaje `orientacja = "auto"` (`silnik.py:128`). Opis `synth.md`: heurystyka 29 z 30, myli sie na
pochylonym moscie.

### S1-07 (P) - niepewna linia, filar bez linii, filar bez niecki

Tryb domyslny (`tylko_dane=True`): `spr = dn` (linia 597) - o "sprawdzeniu" stacji decyduja same dane skanu; niepewna linia
daje wpis w `uwagi_linii` (604-607), filar bez linii takze (625-626). Tresc uwagi mowi wprost: "glebiej brzeg jest sprawdzany
wylacznie przy tej niepewnej linii" / "brzeg lezacy glebiej nie jest sprawdzany". To udokumentowana decyzja z 16.11 (przy samej
linii 29 % prac calych dostawalo "nie sprawdzono"), ale nie ma jej na liscie spraw znanych planu, a skutek to zielone bez
kontroli czesci brzegu, wiec zglaszam. Dodatkowo (nowe): filar, ktorego wneka nie spelnia `POLE_MIN` = 2 mm2 i `GLEB_MAX_MIN` =
1,0 mm (`krawedz.py:60-61`, w skali 1,22, czyli 0,82 mm na pracy spieczonej), nie jest "niecka przyjeta", wiec nie trafia do
`filary_bez_linii` i nie ma o nim zadnej uwagi; gdy pozostale filary maja pewne linie, `stan` = `wiarygodne`.
Generator stawia ubytki tylko przy zweryfikowanych stacjach (`synth.py:448-450`), wiec zestawy R59 / T10 tego nie mierza
(to jest w `synth.md`, uwaga D6).

### S1-08 (P) - `status_gniazda` otwarty na zielone

`if status_match == "szary" or not inspekcja: return status_match` oraz `INSPECT_NA_STATUS.get(...) or status_match`
(`porownaj.py:90-92`). Proba A: (`zielony`, None) -> zielony; (`zielony`, `pominieto`) -> zielony; (`zielony`, status nieznany)
-> zielony. Inspekcji nie ma, gdy `inspekcja=False` (parametr `porownaj`, pole zadania silnika `silnik.py:1059`,
`--bez-inspekcji`) albo kandydat nie ma transformacji (`porownaj.py:216`). Program glowny ma osobna ochrone
(`statusy.status_pracy`, `statusy.py:173-176`: inspekcja inna niz `ok` przy kolorze zielonym = "nie sprawdzono" / "nieznany")
- to zakres S3; tu zglaszam zrodlo: liczniki `statusy_gniazd`, mapa PNG, tabela i metryki `porownaj` licza takie prace jako
zielone, a `kontroler_api.py:4121-4122` ma te pary wypisane ("zielony_bez_inspekcji", "zielony_pominieto").

## 6. Pozostale punkty z listy S1

### 6.1 Plytka okragla testowa R54 (nr 8) i ramkowe n1-n6: rozpoznanie i co dalej

- Rozpoznanie rodziny idzie po rozstawie stozkow (`plate.py:785-789`); kwadrat / kolo testowe / kolo ramkowe jednej rodziny
  maja te same gniazda i stozki, wiec zly wybor W RODZINIE nie zmienia ciecia na gniazda ani inspekcji - zmienia nazwe ukladu,
  numer i model STL do odciecia plytki. Zielonego z tego powodu nie znalazlem (czytanie `plate.py:454-865`).
- Pelny lancuch na `okragla_wieczorna_r54` nr 8 (proba J, 3 skany sztuczne, 9 prac z ubytkiem w pasie): uklad rozpoznany 3 z 3
  (`numer_z_dolkow`, pewny), numer 8 z dolkow 3 z 3, zielonych 0 z 9 (czerwone 8, zolte 1).
- Model STL do odciecia plytki przy numerze nieznanym / zlym = pierwszy z listy (`plate.py:563-566`): roznia sie dolki i relief
  numeru; punkty dolka / reliefu staja sie "praca", ale skupisko jest `drobny` (< 3 mm albo < 1,5 mm w z, `plate.py:535`) -
  bez wplywu na gniazda.
- Kieszenie magnesow, rowek pokrywki, rowek klucza (ramkowe): sa tylko w STL; strefy straznika licza sie promieniami z gory, ICP
  bierze z modelu 600 tys. punktow z calej powierzchni, ale dopasowuje do nich tylko punkty wierzchu i stozkow skanu - z
  czytania bez wplywu. `[NIE SPRAWDZONE BEZ SPRZETU]`: czy prawdziwy skaner widzi scianke boczna i rowek (od tego zalezy
  rozroznienie ramkowa / testowa - sprawa znana).
- Poranna / wieczorna: decyduje `uklad.typ_plytki(nazwa).endswith("poranna")` (`synth.py:804-806`), dziala dla
  `okragla_ramkowa_poranna` i `okragla_poranna_r54` (szczegoly miejsc rozrozniajacych po nazwie: `S1/sub_B_opisy_i_uklady.md`).
- Czego T11 ("zielone przy zlym ukladzie 0") nie obejmowal, a co wynika z kodu: T11 mierzyl zly UKLAD; nie obejmuje zlej
  ORIENTACJI projektu (S1-06) ani zlego PROJEKTU przy statusie zoltym (S1-04).

### 6.2 `match`: zly projekt z wysoka pewnoscia, filtr wysokosci

- Zielony wymaga pokrycia >= 0,85 i przewagi >= 0,1 nad najlepszym kandydatem INNEGO projektu z pelnym dopasowaniem
  (`match.py:1208-1215`). Kandydaci bez pelnego dopasowania maja pokrycie 0 i nie obnizaja pewnosci - gdy sa w marginesie,
  status jest obnizany do zoltego (S1-04 pokazuje, ze to obnizenie nie dochodzi do koloru); kandydaci spoza marginesu nie
  licza sie wcale (znane: D5 recenzji A5).
- Dwa prawie identyczne projekty (ten sam zab przeprojektowany, ten sam STL zapisany ponownie z innymi bajtami): pewnosc < 0,1
  -> szary, bez inspekcji. To nie jest zielone, ale technik widzi "bez projektu" dla zwyklej pracy (D, bez numeru - nie w
  zakresie falszywego zielonego).
- Pokrycie jest jednostronne (skan -> projekt): ubytek ani brak polowy pracy go nie obniza. To zalozenie konstrukcji, a
  jedynym zabezpieczeniem przed "nie widac brzegu" jest `ocena_brzegu` - stad waga S1-01, S1-05.
- Filtr wysokosci i przyciecie projektu (`match.py:562-584`): tylko zaweza liste kandydatow; sciezki do zielonego nie znalazlem.

### 6.3 Korekta skali (okno +-1 %)

- Estymata wylacza pas 2,0 mm od plaszczyzny z = 0 (`match.py:897`), ma wagi Tukeya i drugie przejscie bez obszarow
  odbiegajacych (907-913); stosowana tylko, gdy pokrycie po korekcie >= 0,6 i nie spada o > 0,02 (962-973). Lokalnego ubytku
  nie "wchlonie": zmiana skali o 1 % przesuwa powierzchnie korony 10 mm o najwyzej 0,05 mm na obwodzie, a ubytek to >= 0,08 mm
  lokalnie; z czytania brak sciezki do zielonego dla ukruszenia.
- Wchlania natomiast (z zamyslu) rownomierna roznice rozmiaru do 1 %: praca wieczorna wyfrezowana z innym wspolczynnikiem
  jest zielona, ostrzezenie (> 0,3 %) jest tylko w `uwagi` i w polu `skala` - "nie zmienia koloru gniazda" (`match.md`). To
  nie ukruszenie, wiec bez numeru; do wiadomosci wlasciciela (pytanie 3).
- Po korekcie progi inspekcji w mm roznia sie od mm skanu o <= 1 % (0,08 -> 0,0792-0,0808) - pomijalne.

### 6.4 Progi i jednostki

Pelna tabela porownan z progami: `S1/sub_A_wyliczenia.md` (T4). Z wlasnego czytania:
- granica pasa: `odl_brzegu > 1,5` (ostre) - dokladnie 1,5 jest w pasie; `pokrycie < 0,85` (ostre) - 0,85 przechodzi;
- `srednica < srednica_min_mm / 2` (0,1 mm) dla plamy A, ale `szer < srednica_min_mm` (0,2 mm) dla wciecia B - rozne progi tej
  samej nazwy;
- `srednica_max_mm` = 1,5 dotyczy ROZPIETOSCI RDZENIA (2-98 percentyl), ktory jest o 10-50 % mniejszy niz ubytek: ubytek fi 1,8
  ma rdzen 0,94-1,09 mm; nazwa progu sugeruje srednice ubytku;
- stale poza `ustawienia.toml`, ktore decyduja o zielonym: `BRAK_DANYCH_MM` 0,8, `OTOCZENIE_STACJI_MM` 0,3,
  `UDZIAL_DANYCH_STACJI` 0,5, `UDZIAL_POD` 0,7, `ZGODNOSC_NORMALNEJ` 0,2, `EPS_PLAMY_MM` 0,25, `ODLEGLOSC_KRAWEDZI_MM` 0,5
  (`inspect.py:72-83, 426-429`) - wbrew zdaniu modulu "Progi wylacznie w `ustawienia.toml [inspect]`" (`inspect.py:30`).

## 7. `synth` kontra detektor: "pomiar sam siebie potwierdza" - lista do sprawdzenia 28-29.11 na okraglej R54

Zalozenia wspolne generatora i detektora (wynik z czytania, bez pomiarow):

| Nr | Zalozenie w `synth` | To samo zaklada detektor | Co sprawdzic na sprzecie |
|---|---|---|---|
| 1 | ubytek = kula, powierzchnia przelomu zawsze w skanie, punkty co 0,05 mm (`_wytnij_kule`, `odstep_ubytku_mm`) | A i B potrzebuja punktow na przelomie (S1-01) | czy siatka skanu ma wierzcholki na przelomie prawdziwego odprysku |
| 2 | krawedz ubytku idealnie ostra (ciecie sfera) | pierscien 0,15 mm, prog 0,04 (S1-02) | `pierscien_mediana_mm` plam na prawdziwych ubytkach |
| 3 | gestosc punktow pracy = siatka projektu exocad + zageszczenie przy ubytku | progi w liczbie punktow (S1-03) | mediana dlugosci krawedzi siatki skanu na pracy i na plytce |
| 4 | ubytki tylko w pasie 1,5 mm od ZWERYFIKOWANYCH stacji tej samej linii (`synth.py:448-450`), pas i srednice z `[inspect]` | ten sam pas, te same linie (`krawedz.linie_siatki`) | ubytek 1,5-2,5 mm od brzegu; ubytek filaru mostu przy laczniku |
| 5 | `wykrywalny` = glebokosc >= prog i srednica w zakresie `[inspect]` (`synth.py:925-928`) | metryki licza tylko `wykrywalny` | - (definicja; znane z RAPORT 5a) |
| 6 | szum N(0; 0,03) wzdluz normalnej, niezalezny na wierzcholek, bez bledu systematycznego, bez wygladzenia | prog 0,08; pokrycie przy 0,05 (sufit 0,90); drgniecie 0,07 | sigma na plaskim wierzchu plytki; pokrycie prac calych (>= 0,85?) |
| 7 | praca dobrze ulozona ma CALA powierzchnie w skanie (takze spod) | `ocena_brzegu` wymaga danych na 90 % linii | `udzial_z_danymi` na pracach calych: ile jest "nie sprawdzono" |
| 8 | projekt i praca = ta sama siatka x wspolczynnik (bez odchylek frezowania, bez lacznikow / podpor po wycieciu z krazka) | odchylka > 0,08 pod powierzchnia = podejrzenie; nad powierzchnia = ignorowane | slady po lacznikach (sprue) na pracy: plamy "nad" obnizaja pokrycie, zeszlifowane "pod" daja plamy |
| 9 | plytka = model STL + szum; dolki i stozki czyste | prog plytki 0,12 mm, stozek RMS 0,08, dolek 0,4 mm | reszty stozkow, bity dolkow, K1 / K2 straznika na prawdziwej R54 nr 8 |
| 10 | orientacja projektow: nazwy `*_cad.stl` (exocad) | `match.Projekt` - ta sama funkcja | `stan_linii` wszystkich prac (S1-06) |
| 11 | drgniecie = kopia 50 % siatki przesunieta 0,08-0,15 mm | regula "obie strony / rozproszone" | - (bez sprzetu nie do oceny) |

Trzy liczby, ktore najtaniej rozstrzygaja S1-01 - S1-03 na pierwszym prawdziwym skanie pracy z odpryskiem: (a) odstep
wierzcholkow, (b) czy sa wierzcholki na przelomie, (c) `pierscien_mediana_mm` plamy. Wszystkie sa w siatce skanu i w
`_wynik.json` - bez dodatkowych narzedzi i bez zbierania danych przed dostawa skanera.

## 8. Testy, ktore niczego nie pilnuja

Zrodlo: subagent C, `S1/sub_C_testy.md` (474 linie; 19 plikow testow w calosci = 287 funkcji `test_*`, 3 pliki czesciowo).
Sprawdzone wyrywkowo przez sesje glowna: 6 z 6 wskazanych linii zgodnych (`test_ui.py:67-68`, `test_inspect.py:251, 344,
468, 480, 552`).

Klasy slabosci (liczba testow): brak asercji o wyniku 4; prog dobrany pod dane 8; tylko przypadek pozytywny albo
`status != "ubytek"` 3; asercja warunkowa / skip 9; atrapa zamiast prawdziwej siatki 22; tylko uklady kwadratowe 2.

Najwazniejsze dla falszywego zielonego:

| Test | Co jest slabe |
|---|---|
| `test_ui.py:68` | JEDYNY test lancucha skan -> `status_gniazda` czerwony / zolty dla pracy z ubytkiem z prawdy; ma `@pytest.mark.skip` (okno-szkic), czyli nigdy nie dziala. Poza nim kolor gniazda dla ubytku sprawdzaja tylko testy mapowania na slownikach. |
| `test_inspect.py:131` | praca z wycietymi 30-60 % powierzchni: `status not in ("ubytek", "skan_ponownie")` - dopuszcza `ok`. |
| `test_inspect.py:140` | praca bokiem: `status != "ubytek"` (dopuszcza `ok`), szare pomijane, wystarczy 1 przypadek. |
| `test_inspect.py:576` | asercja tylko pod `if status in ("ok", "nie_sprawdzono")`; nazwa mowi "bokiem", a `p_bokiem` nie jest ustawione. |
| `test_inspect.py:58` | progi 0,8 (dowolna metoda) / 0,7 (A) / >= 1 (B, czerwone); 1 ziarno, 3 atrapy; brak asercji o kolorze gniazda. |
| `test_inspect.py:79` | tolerancja odleglosci od brzegu 1,5 + 0,8 = 2,3 mm przy pasie 1,5 mm. |
| `test_inspect.py:251` | `status_gniazda("zielony", None) == "zielony"` - utrwala S1-08. |
| `test_inspect.py:468, 480, 552` | tryb domyslny: `ok` i `brzeg.sprawdzony` przy niepewnej linii, przy braku linii i przy filarze bez linii - utrwala S1-05 / S1-07. |
| `test_inspect.py:344` | tryb `plaszczyzna`: ukruszony brzeg glebokiego filaru = `ok` (zachowanie sprzed P2 zapisane jako oczekiwane). |
| `test_pula_match.py:513`, `test_session_wieczor.py:1588` | `porownaj` z inspekcja na pracach z ubytkami: tylko `inspekcja is not None` / kopiowanie statusow, bez prawdy. |

Braki pokrycia (z odpowiedzi (a)-(e) subagenta):
- zaden test nie stawia ubytku 1,4-1,6 mm od linii (granica pasa); generator trzyma ubytki do 1,5 mm (`test_edge_synth.py:269`);
- zaden test nie sprawdza pary `status_gniazda("zolty", {"status": "ok"})` (S1-04);
- uklady `okragla_wieczorna_r54`, `okragla_poranna_r54`, `okragla_ramkowa_*` sa w testach tylko do rozpoznania, wyrownania,
  dopasowania, straznika, ekranu i ramki; inspekcja ubytkow jest testowana wylacznie na `okragla_wieczorna` (R59) i na brylach.
  Kod inspekcji nie zalezy od ukladu, wiec to brak dowodu, nie blad;
- testy "utrwalajace": `test_auto_uklad_r58.py:242, 268` (okragla = pewny kwadrat - znane), `:216`, `:168, :189`;
  `test_okragle_ramka.py:954, 1199` (wynik innego skanu pod plytka - znane, S3).
- `conftest.py` nie ma znacznikow ani `addopts`; zawsze pomijane: `test_ui.py:68, 131`.

## 9. Opis - kod, wyliczenia, bieg testow

### 9.1 Bieg testow (subagent D, `S1/sub_D_testy_bieg.md`, logi `S1/log_*.txt`)

6 plikow, po kolei, 1 proces python, kazdy raz; lacznie 209,9 s. Wiersze podsumowania sprawdzone przez sesje glowna w logach
(6 z 6 zgodne).

| Plik | Wynik | Czas |
|---|---|---|
| `test_porownaj_bledy.py` | 5 errors | 2,4 s |
| `test_inspect.py` | 5 passed, 21 errors | 5,0 s |
| `test_krawedz.py` | 15 passed | 16,2 s |
| `test_skala.py` | 3 passed, 11 errors | 3,2 s |
| `test_auto_uklad_r58.py` | 52 passed | 176,5 s |
| `test_straznik.py` | 4 passed, 26 errors | 6,6 s |

Razem 79 passed, 0 failed, 63 errors. Wszystkie 63 bledy to ten sam `FileNotFoundError: brak pliku ustawien ...
ustawienia.toml` w przygotowaniu testu (`ustawienia.py:352`) - testy nie doszly do asercji, wiec ich wynik merytoryczny w tym
worktree jest NIEZNANY.

S1-14 (D) - skad testy lancucha biora progi:
- `wczytaj_ustawienia()` bez argumentu czyta tylko `<katalog programu>/ustawienia.toml` (`ustawienia.py:19-21, 348-354`); nie ma
  przejscia na plik przykladowy ani zmiennej srodowiskowej; `conftest.py` niczego nie podmienia; plik jest w `.gitignore`.
- Pliku nie ma w worktree ani w klonie `<PC-katalog>\qc`; jest w `<PC>\Desktop\Ramki\stanowisko\`.
- 18 z 59 plikow testow siega do pliku lokalnego, 13 do `PLIK_PRZYKLADU`. Skutek: testy `inspect` / `skala` / `straznik` /
  `porownaj_bledy` sprawdzaja kod z progami z LOKALNEGO, niewersjonowanego pliku maszyny, na ktorej biegna. Zmiana progu w
  lokalnym pliku moze zmienic wynik testu bez zmiany w repo, a "pelny pytest 0 failed" jest wazny tylko dla tego pliku.
  Tresci pliku z pulpitu nie czytalem (poza `<PC-katalog>`). Pytanie 6 w sekcji 10.

### 9.2 Wyliczenia i opis - kod

Subagent A (`S1/sub_A_wyliczenia.md`; 10 plikow zakresu + `ustawienia.py` + przyklad, w calosci): T1 `except` 41 wierszy,
T2 statusy 61 (+ 8 miejsc z domyslnym `ok` / zielonym), T3 puste dane i NaN 95, T4 porownania z progami 142.
Sprawdzone wyrywkowo: `match.py:340`, `inspect.py:691, 707, 579-583`, `porownaj.py:90-92, 222` - 6 z 6 zgodne z kodem.
- Golego `except:` nie ma. Szerokie `except Exception`, po ktorym wynik wyglada na "brak problemu": tylko `match.py:340`
  (`cechy_do_glebokosci`: `hull = 0.0`, przez co `filtr` w linii 582 pomija kontrole objetosci - dotyczy doboru projektu, nie
  ubytkow). `porownaj.py:222` lapie szeroko, ale daje `nie_sprawdzono` (zolte).
- Domyslne `ok` / zielone: `inspect.py:691`, `porownaj.py:90-91, 92`, `inspect.py:582`, `inspect.py:622-626 + 635`,
  `porownaj.py:524` (`.get("sprawdzony", True)` - tylko tekst tabeli), `porownaj.py:552` (mapa PNG) - pokrywa sie z sekcja 3;
  nowych sciezek do zielonego subagent nie znalazl.
- S1-15 (D): wyjatek w `match.dopasuj` / `match.ratuj_plytke` nie jest lapany na gniazdo (`porownaj.py:201-206` sa poza
  `try` z linii 217) - blad dopasowania JEDNEGO fragmentu konczy analize calej plytki. To nie zielone; skutek dla technika
  (brak wyniku plytki) nalezy do S2.
- Ustawienia: 43 klucze domyslne w `ustawienia.py` = wartosci z `ustawienia.przyklad.toml`, roznic 0; pozostale progi
  `[inspect]` / `[match]` nie maja wartosci domyslnych w kodzie (musza byc w pliku); `krawedz_pas_mm` nie ma sprawdzenia zakresu.
- Jednostki: odchylki w `inspect` sa w mm ukladu puli (projekt x wspolczynnik), po korekcie skali nie sa dzielone przez skale
  (inaczej niz `match.py:607`) - roznica <= 1 %.

Subagent B (`S1/sub_B_opisy_i_uklady.md`; opis - kod dla `uklad`, `katalog`, `metryki`, `synth`; 10 plikow `uklad.json`;
miejsca rozrozniajace plytke po nazwie / numerze). Sprawdzone wyrywkowo: `synth.py:127-129, 181, 758, 806`, `plate.py:563-566`,
`porownaj.py:170` - 6 z 6 zgodne.

S1-13 (D) - rozjazdy opis - kod (wybor; pelna tabela w pliku subagenta):

| Opis | Kod | Roznica |
|---|---|---|
| `uklad.md:7` "uklad wybiera czlowiek" | `porownaj.py:627`, `plate.py:754` | od 15.11 domyslnie `--plytka auto` |
| `uklad.md:31` bit D "dla przyszlych n8 / n9" | `uklad.py:253-255` | D maja tez kwadraty R59 i ramkowe; kod wymaga kolejnosci A, B, C[, D] |
| `synth.md:33` (S11: `.STL` pomijane) | `synth.py:127-129` | nieaktualne: `rglob` + `suffix.lower()` |
| `synth.md:16` "niejasny, gdy nie ma krawedzi" | `synth.py:181` | prog to `max < 1,0 mm` albo stosunek < 1,5; skrot `*_cad.stl` (209-210) nieopisany w `synth.md` |
| `synth.md:28` ubytki przy zweryfikowanych stacjach | `synth.py:449-454` | bez zweryfikowanych stacji: gorny pas z, a przy pustym pasie dowolny wierzcholek |
| `synth.md:5` `Opcje()` | `synth.py:853` | bez `z_toml` zawsze wartosci "wieczorna", takze dla plytki porannej |
| `katalog.md:16` mosty > 15 / 13 mm | `synth.py:758` | odrzucenie juz przy szerokosci > w - 0,4 (14,6 / 12,6) albo dlugosci > l - 1,0 |
| `metryki.md:23` prace dwuznaczne / nieznane | `metryki.py:309-313, 340-341` | pusty kandydat 1 pomijany (kandydat 2 liczony jako "1."); rano lista nieobcieta do 2; brak sprawdzenia koloru szarego |
| `metryki.md:26` "za krotki okres" | `metryki.py:449` | liczy `dni_historii`, nie `dni_pracy` |
| `plate.py:764` docstring "n1-n6 = kwadrat" | `plate.py:832-836` | nieaktualne przy ukladach ramkowych (kod uzywa `uk.numery`) |
| `inspect.py:30` "Progi wylacznie w `ustawienia.toml`" | `inspect.py:72-83, 426-429` | 7 stalych decydujacych o zielonym jest w kodzie (6.4) |

`porownaj.py` i `wspolczynniki.py` nie maja pliku w `opisy_modulow/` (potwierdzone): `wspolczynniki` jest opisany w `pula.md`,
`porownaj` tylko jako polecenie w `README.md`; reguly koloru gniazda (`status_gniazda`) nie ma w zadnym opisie.

`uklad.json` (czesc 2 subagenta B), wazne dla okraglych:
- ramkowa i okragla testowa tej samej rodziny maja identyczny wierzch (stozki, gniazda, dolki, sciecie, fi 100); roznia sie
  numerami (1-3 / 4-6 wobec 8 / 9) i tym, co pod spodem i na obwodzie (kieszenie r 45, rowek pokrywki 2 mm pod wierzchem - w
  pasie oceny ksztaltu 3 mm, rowek klucza);
- `okragla_wieczorna_r54` i `wieczorna_r54`: te same stozki i 20 gniazd; roznia sie ksztaltem, 4 dolkami w kole zamiast 3 poza
  polem, numerem 8;
- w zadnym z 9 przejrzanych modulow nazwy `okragla_ramkowa_*` ani `*_r54` nie trafiaja do zlej galezi: obie poranne sa uznane za
  poranne (`synth.py:806`: wspolczynnik 1,0 i korekta skali tylko mierzona), wieczorne dostaja 1,225;
- najblizsze sasiedztwo: na okraglej porannej R59 dolek A lezy 2,09 mm od stozka C (liczone recznie w rzucie xy).

## 10. Pytania do wlasciciela

1. Plan podaje `modele_plytek/okragla_*` w `Ramki/stanowisko/stanowisko/`; katalog jest w `Ramki/stanowisko/modele_plytek/`.
   Przyjalem ten drugi.
2. Czy pracownia frezuje z cyrkonu prace bez wneki >= 1 mm (inlay, onlay, licowka, most adhezyjny) albo dostaje projekty z
   programu innego niz exocad (nazwa pliku inna niz `*_cad.stl`)? Od tego zalezy waga S1-05 i S1-06 (dzis P).
3. Praca wieczorna o skali rozniacej sie od projektu x wspolczynnik o 0,3-1 % jest zielona z ostrzezeniem tylko w uwagach
   (6.3). Czy tak ma zostac, skoro taka praca po spiekaniu nie bedzie pasowac?
4. Sesja dzialala na koncie `<uzytkownik>` (nie `<konto-PC>`): `git fetch` / `git push` z tego konta nie dzialaja (brak logowania do
   GitHub). Commit raportu jest lokalny na galezi `analiza/s1` - patrz koniec raportu.
5. S1-07 (tryb domyslny a mosty) to decyzja z 16.11 opisana w `inspect.md`, ale nie ma jej w "sprawach znanych" planu.
   Czy traktowac ja jako znana?
6. Z jakim plikiem `ustawienia.toml` biegl pelny pytest (2506 passed) i testy odbioru na koncie `<konto-PC>`, skoro w klonie
   `<PC-katalog>\qc` pliku nie ma (S1-14)? Jesli byl kopiowany - skad i czy jego `[inspect]` / `[match]` sa rowne przykladowi.

## 11. Przeczytane / przejrzane / nieczytane

(liczby linii pliku; "sesja glowna" = Fable)

| Plik | Linii | Sesja glowna | Subagenci |
|---|---|---|---|
| `stanowisko/inspect.py` | 797 | w calosci | A (wyliczenia) |
| `stanowisko/porownaj.py` | 712 | w calosci | A |
| `stanowisko/match.py` | 1345 | 107-237, 530-686, 824-1345 (ok. 810 linii); reszta: sygnatury i stale | A |
| `stanowisko/plate.py` | 877 | 454-865 (412 linii); reszta: sygnatury i stale | A |
| `stanowisko/krawedz.py` | 990 | 770-990 (221 linii); reszta: sygnatury i stale | A |
| `stanowisko/synth.py` | 1302 | 156-220, 394-470, 538-635, 800-1082 (ok. 525 linii); reszta: sygnatury | A, B |
| `stanowisko/uklad.py` | 360 | tylko wyszukiwanie (typ plytki, ksztalt) | A, B |
| `stanowisko/wspolczynniki.py` | 537 | nieczytane | A, B (funkcje publiczne) |
| `stanowisko/metryki.py` | 602 | nieczytane | A, B |
| `stanowisko/katalog.py` | 169 | nieczytane | A, B |
| `modele_plytek/okragla_*/uklad.json` (6) + kwadratowe (4) | - | nieczytane | B (porownanie) |
| `opisy_modulow/inspect.md, krawedz.md, plate.md, match.md, uklad.md, synth.md` | 49 / 85 / 66 / 50 / 35 / 35 | w calosci | B (uklad, synth) |
| `opisy_modulow/katalog.md, metryki.md` | 17 / 63 | nieczytane | B |
| `testy/test_inspect.py` | - | 1-150, 268-320, 395-515, 574-603 | C (w calosci) |
| pozostale testy modulow | - | nieczytane | C |
| poza zakresem, tylko do oceny osiagalnosci: `statusy.py` 95-184, `silnik.py` (wyszukiwanie), `ustawienia.py` 322-361, `ustawienia.przyklad.toml` (wyszukiwanie) | | fragmenty | |
| `analiza_kodu_2026-11-23/PLAN.md`, `JAK_PRACOWAC_MSI_PC.md` | 157 / 128 | w calosci | |
| `etap3/odbior_koncowy/RAPORT.md` | 505 | 216-265 (5, 5a) + wyszukiwanie T2 (e) | |
| `etap3/odbior_koncowy/dowody/T8/WYNIK.md` | - | 85-129 | |
| `00_NADZOR_STAN.md` | 313 | tylko fragmenty o T2 (e) w liniach 297, 308, 309, 312 | |

## 12. Zlecenia subagentow (Opus 5.5 xhigh)

| Nr | Zlecenie | Wynik | Sprawdzenie wyrywkowe sesji glownej |
|---|---|---|---|
| A | wyliczenia `except` / statusy / puste dane i NaN / progi w 10 plikach zakresu | `S1/sub_A_wyliczenia.md` | 6 z 6 linii zgodnych (9.2) |
| B | opis - kod (uklad, katalog, metryki, synth), `uklad.json` 10 ukladow, miejsca rozrozniajace plytke po nazwie / numerze | `S1/sub_B_opisy_i_uklady.md` | 6 z 6 linii zgodnych (9.2); odleglosci w czesci 2 liczone recznie - niesprawdzane |
| C | przeglad testow modulow lancucha (klasy slabosci) | `S1/sub_C_testy.md` | 6 z 6 linii zgodnych (8) |
| D | bieg 6 plikow testow, po kolei, 1 proces python | `S1/sub_D_testy_bieg.md`, `S1/log_*.txt` | 6 z 6 wierszy podsumowania zgodnych z logami (9.1) |

Subagenci A, B, C tylko czytali (bez pythona). Oceny wagi sa wylacznie sesji glownej.

## 13. Czas PC

Proby sesji glownej 37 s (2 uruchomienia + 1 nieudane 2 s: brak `ustawienia.toml`), bieg testow subagenta D 210 s; razem
ok. 4,2 min z 30 min budzetu; zawsze 1 proces python, najdluzsze polecenie 176,5 s (`test_auto_uklad_r58.py`).
Pliki tymczasowe prob (`S1/s1_proba*`) usuniete. W `Ramki/stanowisko` nic nie zmieniono.
