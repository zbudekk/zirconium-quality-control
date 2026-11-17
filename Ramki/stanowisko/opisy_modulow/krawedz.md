# krawedz - linie krawedzi brzegu kazdego filaru projektu

**Co robi.** Z siatki STL projektu wyznacza linie krawedzi brzegu KAZDEGO czlonu z brzegiem (filaru): korona
pojedyncza = 1 petla, most / praca wieloczlonowa = petla na kazdy filar (przesla nie maja brzegu), korona implantowa bez
lacznika = obwod powierzchni przylegania (styk z Ti-base, kanal sruby; decyzja wlasciciela 06.11.2026: liczy sie jako
krawedz brzegu). Z linii korzystaja: `inspect` (pas brzegu liczony od linii, status "nie sprawdzono") i `synth`
(ukruszenia stawiane celowo na krawedzi, klasa polozenia ubytku). Zamowienie: P2 i P4 z
`raporty/testy_krawedz/WNIOSKI_I_DECYZJE_2026-11-09.md`, zgoda wlasciciela 15.11.2026. Metoda = prototyp sesji testowej
T9 (06.11.2026) przeniesiony bez zmiany konstrukcji i stalych.

**Wejscie.** Siatka projektu brzegiem do gory, os z = os wprowadzenia wspolna dla calej pracy (eksport exocad) - czyli
`match.Projekt.siatka` albo praca w `synth` przed ulozeniem w gniezdzie. `linie_siatki(siatka, skala, klucz)`:
`skala` = ile razy siatka jest wieksza od pliku projektu (wspolczynnik skurczu), `klucz` = skrot SHA-256 pliku projektu.

**Wyjscie.** `LinieProjektu`: `filary` (lista `Filar`), `niecki` (opis znalezionych wnek), `uwagi`, `stan`
(`wiarygodne` = kazdy filar ma linie i jest wiarygodny | `czesciowe` | `brak` = zadnego filaru z linia),
`filary_bez_linii` (numery filarow, ktorych niecka zostala przyjeta, ale zaden wariant nie dal linii - w `uwagi` jest
wtedy "filar N: ... linii nie wyznaczono", filaru nie ma na liscie `filary`, a `stan` to najwyzej `czesciowe`; liczone z
`niecki`, wiec dziala takze dla linii z pamieci na dysku), `opis()` (liczniki do JSON, w tym `filary_bez_linii`).
`Filar`: `nr`, `srodek` (os przekrojow), linie `O` (naroznik zewnetrzny plaskiej krawedzi), `I` (naroznik wewnetrzny) i
`S` (srodek plaskiej krawedzi zrzutowany NA powierzchnie projektu) jako zamkniete lamane ze stacjami co ok. 0,05 mm
(`Linia.X`, `zweryf` na stacji, `dlugosc`); to samo na przekroj (`O`, `I`, `S`, `udany`, `zweryf` - 720 przekrojow co
0,5 st.); miary: `werdykt` (`wiarygodna` | `czesciowa` | `niepewna`), `udzial_zweryf`, `najdl_ciag_st`,
`najdl_przerwa_mm`, `wariant`, `kontrola` (liczniki posrednie). Wspolrzedne sa w ukladzie siatki wejsciowej.
`stacje(linie, ("O", "I"))` sklada stacje wszystkich filarow w jedna tablice (do drzewa odleglosci).

**Jak dziala** (`wyznacz`, w skali odniesienia).
1. Mapa wysokosci z gory (promienie w dol, piksel 0,05 mm). Niecki = piksele, ktore po wypelnieniu niecek od ramki
   obrazu ("priority flood") leza > 0,3 mm pod poziomem wypelnienia; niecka filaru: pole >= 2 mm2 i glebokosc >= 1,0 mm.
   Kanal sruby (brak trafienia wewnatrz pracy) tez jest niecka. Przeslo nie ma niecki - nie dostaje petli.
2. Obszar filaru = dzial wodny ze znacznikami (zalewanie Meyera: znaczniki niecek + tlo). Granica obszaru biegnie po
   grzbiecie brzegu, takze gdy wysokosc grzbietu zmienia sie o kilka mm.
3. Przekroje promieniowe wokol srodka wneki co 0,5 st. W przekroju: od wezla startowego po lamanej w obie strony, dopoki
   normalna odcinka nie odchyli sie o > 25 st. od sredniej normalnej przebytej krawedzi - konce to narozniki O (wiekszy
   promien) i I. Wezel startowy na dwa niezalezne sposoby: wariant 1 - najwyzszy wezel "do gory" w 0,6 mm od granicy
   obszaru z dzialu wodnego; wariant 2 - wezel najblizszy koncowi sciany wneki (od dna wneki na zewnatrz po pikselach o
   normalnej skierowanej do srodka, pierwszy piksel skierowany do gory); wariant 3 - przekroje, w ktorych 1 i 2 daja O
   blizej niz 0,10 mm, a spory rozstrzyga odporna krzywa Fouriera (rzad 16). Grzbiet odstajacy > 0,4 mm od krzywej
   rzedu 8 jest zastepowany krzywa; punkt O odstajacy > 0,25 mm = przekroj odrzucony. Potem filtr medianowy (+-4
   przekroje, 0,15 mm), interpolacja nieudanych przekrojow, stacje.
4. Wybor wariantu na filar: "dobry" = najdluzsza przerwa linii O <= 5 st. i skok surowej linii O miedzy kolejnymi
   przekrojami <= 0,6 mm; kolejnosc 3, 1, 2; bez dobrego - najmniejsze (przerwa / 5 + skok / 0,6), `wybor_pewny` = False.
5. Weryfikacja przekroju (niezalezna od wyboru): przekroj udany (nie interpolowany), co najmniej dwa wyznaczenia punktu
   O zgodne do 0,10 mm (wariant 1, wariant 2, a dla pracy z jednym filarem takze linia "T3": os w srodku obrysu, start
   w najwyzszym wezle przekroju), szerokosc plaskiej krawedzi O-I 0,10-1,50 mm. Petla `wiarygodna`: >= 90 % przekrojow
   zweryfikowanych i najdluzszy ciag niezweryfikowanych <= 10 st.; `czesciowa`: >= 60 %; inaczej `niepewna`.
   Odcinki niezweryfikowane zostaja w linii (oznaczone), nie sa usuwane ani poprawiane.

**Skala i pamiec podreczna.** Stale metody sa w milimetrach pracy zielonej (projekt x 1,22 = `SKALA_ODNIESIENIA`, warunki
sprawdzenia w T9). `linie_siatki` przelicza siatke na te skale (srodek obrysu xy i najwyzszy punkt w poczatku ukladu,
jak uklad puli), liczy linie RAZ na projekt i trzyma je w pamieci modulu pod kluczem projektu; wynik dla dowolnej skali
i przesuniecia to przeliczenie wspolrzednych. `ustaw_katalog_pamieci(katalog)` wlacza dodatkowo pamiec na dysku (plik
`<klucz>_v<WERSJA>.npz` na projekt, wspolna dla procesow) - domyslnie wylaczona, modul sam nic nie pisze na dysk.
Zmiana konstrukcji albo stalych = nowy `WERSJA`.

**Kryterium "dziala".** `testy/test_krawedz.py` (15): korona-atrapa = 1 petla na zewnetrznym obwodzie brzegu, I nizej i
blizej osi, S na powierzchni; most-atrapa = 4 petle (jedna na wneke); tuleja z kanalem na wylot = obwod powierzchni
przylegania; krawedz szersza niz kryterium na czesci obwodu = odcinek oznaczony jako niezweryfikowany; bryla bez wneki =
jawny brak linii; filar z przyjeta niecka bez linii = numer w `filary_bez_linii` i `stan` `czesciowe` (poprawka P1 po
recenzji PR #13); niezaleznosc od skali i przesuniecia; pamiec w module i na dysku (takze uszkodzony plik); funkcje
pomocnicze. Na 17 prawdziwych projektach (`narzedzia/metryki_krawedz.py linie`): 23 petle, 14 wiarygodnych, 9
czesciowych, 0 niepewnych; liczba petli, wariant i liczba zweryfikowanych przekrojow kazdego filaru = T9 (23 z 23).

**Zalozenia i granice.**
- Dane wejsciowe: os z = os wprowadzenia, wneka kazdego filaru otwarta do gory i bez podciec (eksport exocad). Praca
  w innej orientacji albo bez wneki / kanalu = `stan` `brak` (inspect: w trybie `linia` "nie sprawdzono", w trybie
  domyslnym `linia_i_plaszczyzna` pas brzegu sprzed P2 z uwaga w wyniku).
- Filar z przyjeta niecka, dla ktorego zaden wariant nie dal linii (za malo udanych przekrojow), nie dostaje petli:
  jest tylko w `niecki`, `uwagi` i `filary_bez_linii`. `inspect` liczy go w trybie `linia` jako "nie sprawdzono", a w
  trybie domyslnym sprawdza jego brzeg samym pasem od plaszczyzny i zapisuje uwage. W puli 17 projektow przypadek nie
  wystapil (23 petle z 23); test wywoluje go sztucznie.
- Przy lacznikach mostow powierzchnia za brzegiem czesto wznosi sie zamiast opadac - brzeg nie jest tam grzbietem,
  warianty startu rozjezdzaja sie, linia potrafi "uciec" po laczniku. Te odcinki sa niezweryfikowane (srednio 16 %
  obwodu filarow prac wieloczlonowych w puli testowej; 7 z 17 projektow ma petle `czesciowa`).
- Kryteria weryfikacji (zgodnosc 0,10 mm, szerokosc 0,10-1,50 mm) pochodza z T9 i nie byly strojone; jeden projekt
  (korona z gleboka, szeroka polka brzegu) ma trzy zgodne wyznaczenia, ale nie spelnia kryterium szerokosci.
- Warianty 1 i 2 roznia sie tylko wezlem startowym - zgodnosc nie wykryje bledu wspolnego w definicji naroznikow.
  Naroznik wewnetrzny I jest mniej jednoznaczny niz O (faza / polka wewnetrzna).
- Powierzchnia przylegania implantowa: petla jest geometrycznie pewna (zgodnosc 97-100 %), plaska krawedz 0,18-0,80 mm.
- Przekroj przechodzacy dokladnie przez wierzcholki siatki (siatki budowane analitycznie, os w srodku symetrii) nie
  daje odcinkow - w siatkach exocad nie wystepuje; w testach wierzcholki sa przesuniete o faze.
- Czas: 3-9 s na projekt (17 projektow rownolegle), raz na projekt w procesie; stale w kodzie (`krawedz.py`) sa
  czescia konstrukcji metody, nie progami decyzji - progi decyzji o kolorze sa w `ustawienia.toml [inspect]`.
- Nie robiono: poprawiania linii przy lacznikach (start z konca sciany ograniczony do najblizszego zalamania albo
  sledzenie naroznika wzdluz petli - propozycja T9), linii na skanie (metody krawedziowe M / C2 / G - poza zakresem).
