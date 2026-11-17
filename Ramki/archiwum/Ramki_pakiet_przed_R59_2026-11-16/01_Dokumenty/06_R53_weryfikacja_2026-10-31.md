# Weryfikacja R53 — poprawki pasowań (31.10.2026)

Zestaw: `wyniki_v2/` po przebiegach `--etap B --iter 5`, `--etap C --iter 5` (ponowiony po poprawce opisu reguły w arkuszu), `--etap SPRAWDZ --iter 5` (logi w `logi/`). Kopia sprzed R53: `archiwum/wyniki_v2_przed_R53_2026-10-31/`. Metody niezależne: (1) sprawdzenia generatora K‑01…K‑60, (2) kopie skryptów recenzenta `skrypty/sprawdz_*_R53.py` (Blender), (3) kopia trzeciego oka `skrypty/trzecie_oko_R53.py` (Blender, 17 STL + bryły zastępcze), (4) własny pomiar trimesh `skrypty/pomiar_R53.py` ze znakiem luzu, przed i po (ten sam skrypt, parametry odpowiednio sprzed/po R53).

## 1. Generator (`ramka_generator.py`)

| Przebieg | Wynik | Czas |
|---|---|---|
| etap_B_iter5 | B=0 P=0 D=0 | 28 s |
| etap_C_iter5 | B=0 P=0 D=0 | 38 s |
| etap_SPRAWDZ_iter5 | B=0 P=0 D=0 | 3 s |

Raport SPRAWDZ iter5: ZAL 55, NIE 0. Odstępstwa informacyjne „tabela 3 planu” (wartości sprzed R53 w tabeli 3 planu — poza mandatem sesji): 12.

## 2. Pliki STL: które się zmieniły (SHA‑256 vs kopia zapasowa)

| Plik | przed R53 | po R53 | Status |
|---|---|---|---|
| `ramka_blat_v2.stl` | `060b439bf33d…` | `8c48856eb9ad…` | ZMIENIONY (R53) |
| `ramka_korpus_P_v2.stl` | `9c31c117983a…` | `aadb91c9364c…` | ZMIENIONY (R53) |
| `ramka_korpus_W_v2.stl` | `7e7c9298e50a…` | `bd55871c88cf…` | ZMIENIONY (R53) |
| `ramka_plytka_poranna_n4_v2.stl` | `3186d1ab86f2…` | `3186d1ab86f2…` | IDENTYCZNY bajtowo |
| `ramka_plytka_poranna_n5_v2.stl` | `70bd4dd49950…` | `70bd4dd49950…` | IDENTYCZNY bajtowo |
| `ramka_plytka_poranna_n6_v2.stl` | `562d23f69b9b…` | `562d23f69b9b…` | IDENTYCZNY bajtowo |
| `ramka_plytka_poranna_v2.stl` | `5767cf1d387a…` | `5767cf1d387a…` | IDENTYCZNY bajtowo |
| `ramka_plytka_wieczorna_n1_v2.stl` | `b2803c829885…` | `b2803c829885…` | IDENTYCZNY bajtowo |
| `ramka_plytka_wieczorna_n2_v2.stl` | `8bab264ca661…` | `8bab264ca661…` | IDENTYCZNY bajtowo |
| `ramka_plytka_wieczorna_n3_v2.stl` | `d3a44e8d7122…` | `d3a44e8d7122…` | IDENTYCZNY bajtowo |
| `ramka_plytka_wieczorna_v2.stl` | `f02aed867a60…` | `f02aed867a60…` | IDENTYCZNY bajtowo |
| `ramka_podkladka_panelu_05_v2.stl` | `4260d1f1957f…` | `4260d1f1957f…` | IDENTYCZNY bajtowo |
| `ramka_podkladka_panelu_1_v2.stl` | `e79a80512149…` | `e79a80512149…` | IDENTYCZNY bajtowo |
| `ramka_podkladka_panelu_2_v2.stl` | `9c47aea4fbc9…` | `9c47aea4fbc9…` | IDENTYCZNY bajtowo |
| `ramka_pokrywka_v2.stl` | `ad23444483ac…` | `ad23444483ac…` | IDENTYCZNY bajtowo |
| `ramka_tulejka_dc_v2.stl` | `b393256cd8ca…` | `b393256cd8ca…` | IDENTYCZNY bajtowo |
| `ramka_wkladka_v2.stl` | `ef7503c7de34…` | `f4196fbc6404…` | ZMIENIONY (R53) |

Nieoczekiwanych różnic: 0. Powtarzalność (K‑59): STL z `--etap B --iter 5`, `--etap C --iter 4` i `--etap C --iter 5` porównane bajtowo (`logi/sha256_etapC_iter4.txt`, `…iter5.txt`): 16/17 identyczne; `ramka_wkladka_v2.stl` różni się bajtami między przebiegami C4 i C5 (znany efekt: znak zera w normalnych / przekątna fazy, README K‑59, G‑09) — geometria potwierdzona niezależnie na zestawie C5 (kopie recenzenta B/C, trzecie oko, pomiar własny: wszystkie uruchomione ponownie na C5).

## 3. Pasowania T1–T15 z siatek, ze znakiem luzu (trimesh, `pomiar_R53.py`)

Luz = (powierzchnia części B) − (powierzchnia części A) z jednego punktu w szczelinie; dodatni = szczelina, ujemny = wcisk/przenikanie. „Przed” zmierzone na STL z kopii zapasowej z parametrami sprzed R53; „po” na nowych STL z parametrami R53. Status: |zmierzone − nominał| ≤ 0,05.

| Pasowanie | Nominał przed | Zmierzone przed | Nominał po (R53) | Zmierzone po | Kier. | Status |
|---|---|---|---|---|---|---|
| T1 kołnierz blatu – ściana korpusu W, prawa | 0,500 | 0,500 | 0,700 | 0,700 | X | TAK |
| T1 kołnierz blatu – ściana korpusu W, lewa | 0,500 | 0,500 | 0,700 | 0,700 | X | TAK |
| T1 kołnierz blatu – ściana korpusu W, przednia | 0,500 | 0,500 | 0,700 | 0,700 | Y | TAK |
| T1 kołnierz blatu – ściana korpusu W, tylna (x 30) | 0,500 | 0,500 | 0,700 | 0,700 | Y | TAK |
| T1 kołnierz blatu – ściana korpusu W, tylna (x −30) | 0,500 | 0,500 | 0,700 | 0,700 | Y | TAK |
| T1 kołnierz blatu – ściana korpusu P, prawa | 0,500 | 0,500 | 0,700 | 0,700 | X | TAK |
| T1 kołnierz blatu – ściana korpusu P, lewa | 0,500 | 0,500 | 0,700 | 0,700 | X | TAK |
| T1 kołnierz blatu – ściana korpusu P, przednia | 0,500 | 0,500 | 0,700 | 0,700 | Y | TAK |
| T1 kołnierz blatu – ściana korpusu P, tylna (x 30) | 0,500 | 0,500 | 0,700 | 0,700 | Y | TAK |
| T1 kołnierz blatu – ściana korpusu P, tylna (x −30) | 0,500 | 0,500 | 0,700 | 0,700 | Y | TAK |
| T2 haczyk prawy: zahaczenie (czubek − ściana wewn.) korpus W | 0,800 | 0,800 | 0,800 | 0,800 | X | TAK |
| T2 haczyk prawy: luz czubek – dno kieszeni, korpus W | 0,200 | 0,200 | 0,500 | 0,500 | X | TAK |
| T3 haczyk prawy: luz nad występem (sufit kieszeni − górna krawędź), korpus W | 0,250 | 0,250 | 0,750 | 0,750 | Z | TAK |
| T3 haczyk prawy: luz pod występem (start rampy − dno kieszeni), korpus W | 0,250 | 0,270 | 0,750 | 0,770 | Z | TAK |
| T3c haczyk prawy: luz boczny (kieszeń − haczyk)/2, korpus W | 1,000 | 1,000 | 1,500 | 1,500 | Y | TAK |
| T2 haczyk lewy: zahaczenie (czubek − ściana wewn.) korpus W | 0,800 | 0,800 | 0,800 | 0,800 | X | TAK |
| T2 haczyk lewy: luz czubek – dno kieszeni, korpus W | 0,200 | 0,200 | 0,500 | 0,500 | X | TAK |
| T3 haczyk lewy: luz nad występem (sufit kieszeni − górna krawędź), korpus W | 0,250 | 0,250 | 0,750 | 0,750 | Z | TAK |
| T3 haczyk lewy: luz pod występem (start rampy − dno kieszeni), korpus W | 0,250 | 0,270 | 0,750 | 0,770 | Z | TAK |
| T3c haczyk lewy: luz boczny (kieszeń − haczyk)/2, korpus W | 1,000 | 1,000 | 1,500 | 1,500 | Y | TAK |
| T2 haczyk przedni: zahaczenie (czubek − ściana wewn.) korpus W | 0,800 | 0,800 | 0,800 | 0,800 | Y | TAK |
| T2 haczyk przedni: luz czubek – dno kieszeni, korpus W | 0,200 | 0,200 | 0,500 | 0,500 | Y | TAK |
| T3 haczyk przedni: luz nad występem (sufit kieszeni − górna krawędź), korpus W | 0,250 | 0,250 | 0,750 | 0,750 | Z | TAK |
| T3 haczyk przedni: luz pod występem (start rampy − dno kieszeni), korpus W | 0,250 | 0,270 | 0,750 | 0,770 | Z | TAK |
| T3c haczyk przedni: luz boczny (kieszeń − haczyk)/2, korpus W | 1,000 | 1,000 | 1,500 | 1,500 | X | TAK |
| T2 haczyk tylny: zahaczenie (czubek − ściana wewn.) korpus W | 0,800 | 0,800 | 0,800 | 0,800 | Y | TAK |
| T2 haczyk tylny: luz czubek – dno kieszeni, korpus W | 0,200 | 0,200 | 0,500 | 0,500 | Y | TAK |
| T3 haczyk tylny: luz nad występem (sufit kieszeni − górna krawędź), korpus W | 0,250 | 0,250 | 0,750 | 0,750 | Z | TAK |
| T3 haczyk tylny: luz pod występem (start rampy − dno kieszeni), korpus W | 0,250 | 0,270 | 0,750 | 0,770 | Z | TAK |
| T3c haczyk tylny: luz boczny (kieszeń − haczyk)/2, korpus W | 1,000 | 1,000 | 1,500 | 1,500 | X | TAK |
| T2b ściana korpusu W za kieszenią zatrzasku (prawa) | 1,500 | 1,500 | 1,200 | 1,200 | X | TAK |
| T2b ściana korpusu W za kieszenią zatrzasku (przednia, x 50) | 1,500 | 1,500 | 1,200 | 1,200 | Y | TAK |
| T2 haczyk prawy: zahaczenie (czubek − ściana wewn.) korpus P | 0,800 | 0,800 | 0,800 | 0,800 | X | TAK |
| T2 haczyk prawy: luz czubek – dno kieszeni, korpus P | 0,200 | 0,200 | 0,500 | 0,500 | X | TAK |
| T3 haczyk prawy: luz nad występem (sufit kieszeni − górna krawędź), korpus P | 0,250 | 0,250 | 0,750 | 0,750 | Z | TAK |
| T3 haczyk prawy: luz pod występem (start rampy − dno kieszeni), korpus P | 0,250 | 0,270 | 0,750 | 0,770 | Z | TAK |
| T3c haczyk prawy: luz boczny (kieszeń − haczyk)/2, korpus P | 1,000 | 1,000 | 1,500 | 1,500 | Y | TAK |
| T2 haczyk lewy: zahaczenie (czubek − ściana wewn.) korpus P | 0,800 | 0,800 | 0,800 | 0,800 | X | TAK |
| T2 haczyk lewy: luz czubek – dno kieszeni, korpus P | 0,200 | 0,200 | 0,500 | 0,500 | X | TAK |
| T3 haczyk lewy: luz nad występem (sufit kieszeni − górna krawędź), korpus P | 0,250 | 0,250 | 0,750 | 0,750 | Z | TAK |
| T3 haczyk lewy: luz pod występem (start rampy − dno kieszeni), korpus P | 0,250 | 0,270 | 0,750 | 0,770 | Z | TAK |
| T3c haczyk lewy: luz boczny (kieszeń − haczyk)/2, korpus P | 1,000 | 1,000 | 1,500 | 1,500 | Y | TAK |
| T2 haczyk przedni: zahaczenie (czubek − ściana wewn.) korpus P | 0,800 | 0,800 | 0,800 | 0,800 | Y | TAK |
| T2 haczyk przedni: luz czubek – dno kieszeni, korpus P | 0,200 | 0,200 | 0,500 | 0,500 | Y | TAK |
| T3 haczyk przedni: luz nad występem (sufit kieszeni − górna krawędź), korpus P | 0,250 | 0,250 | 0,750 | 0,750 | Z | TAK |
| T3 haczyk przedni: luz pod występem (start rampy − dno kieszeni), korpus P | 0,250 | 0,270 | 0,750 | 0,770 | Z | TAK |
| T3c haczyk przedni: luz boczny (kieszeń − haczyk)/2, korpus P | 1,000 | 1,000 | 1,500 | 1,500 | X | TAK |
| T2 haczyk tylny: zahaczenie (czubek − ściana wewn.) korpus P | 0,800 | 0,800 | 0,800 | 0,800 | Y | TAK |
| T2 haczyk tylny: luz czubek – dno kieszeni, korpus P | 0,200 | 0,200 | 0,500 | 0,500 | Y | TAK |
| T3 haczyk tylny: luz nad występem (sufit kieszeni − górna krawędź), korpus P | 0,250 | 0,250 | 0,750 | 0,750 | Z | TAK |
| T3 haczyk tylny: luz pod występem (start rampy − dno kieszeni), korpus P | 0,250 | 0,270 | 0,750 | 0,770 | Z | TAK |
| T3c haczyk tylny: luz boczny (kieszeń − haczyk)/2, korpus P | 1,000 | 1,000 | 1,500 | 1,500 | X | TAK |
| T2b ściana korpusu P za kieszenią zatrzasku (prawa) | 1,500 | 1,500 | 1,200 | 1,200 | X | TAK |
| T2b ściana korpusu P za kieszenią zatrzasku (przednia, x 50) | 1,500 | 1,500 | 1,200 | 1,200 | Y | TAK |
| T4 otwór wkrętu blatu x=-75: ø w ścianie (X), korpus W | 3,200 | 3,195 | 3,600 | 3,600 | X | TAK |
| T4 otwór wkrętu blatu x=-75: ø w ścianie (Z), korpus W | 3,200 | 3,193 | 3,600 | 3,592 | Z | TAK |
| T4 otwór wkrętu blatu x=-75: ø przy licu (pogłębienie), korpus W | 6,100 | 6,100 | 6,100 | 6,100 | X | TAK |
| T4 współosiowość otwór ściany – otwór słupka x=-75, korpus W | 0,000 | 0,002 | 0,000 | 0,000 | XZ | TAK |
| T4 otwór wkrętu blatu x=75: ø w ścianie (X), korpus W | 3,200 | 3,195 | 3,600 | 3,600 | X | TAK |
| T4 otwór wkrętu blatu x=75: ø w ścianie (Z), korpus W | 3,200 | 3,193 | 3,600 | 3,592 | Z | TAK |
| T4 otwór wkrętu blatu x=75: ø przy licu (pogłębienie), korpus W | 6,100 | 6,100 | 6,100 | 6,100 | X | TAK |
| T4 współosiowość otwór ściany – otwór słupka x=75, korpus W | 0,000 | 0,002 | 0,000 | 0,000 | XZ | TAK |
| T4 otwór wkrętu blatu x=-75: ø w ścianie (X), korpus P | 3,200 | 3,195 | 3,600 | 3,600 | X | TAK |
| T4 otwór wkrętu blatu x=-75: ø w ścianie (Z), korpus P | 3,200 | 3,193 | 3,600 | 3,592 | Z | TAK |
| T4 otwór wkrętu blatu x=-75: ø przy licu (pogłębienie), korpus P | 6,100 | 6,100 | 6,100 | 6,100 | X | TAK |
| T4 współosiowość otwór ściany – otwór słupka x=-75, korpus P | 0,000 | 0,002 | 0,000 | 0,000 | XZ | TAK |
| T4 otwór wkrętu blatu x=75: ø w ścianie (X), korpus P | 3,200 | 3,195 | 3,600 | 3,600 | X | TAK |
| T4 otwór wkrętu blatu x=75: ø w ścianie (Z), korpus P | 3,200 | 3,193 | 3,600 | 3,592 | Z | TAK |
| T4 otwór wkrętu blatu x=75: ø przy licu (pogłębienie), korpus P | 6,100 | 6,100 | 6,100 | 6,100 | X | TAK |
| T4 współosiowość otwór ściany – otwór słupka x=75, korpus P | 0,000 | 0,002 | 0,000 | 0,000 | XZ | TAK |
| T4 otwór słupka x=-75: ø (blat) | 2,500 | 2,500 | 2,500 | 2,500 | X | TAK |
| T4 otwór słupka x=-75: dno (y) | 91,000 | 91,000 | 90,800 | 90,800 | Y | TAK |
| T4 dno słupka x=-75 pod otworem (materiał) | 1,800 | 1,800 | 1,600 | 1,600 | Y | TAK |
| T4 wkręt M3×8 x=-75: gwint w słupku (lico − (100 − 8)) | 5,000 | 5,000 | 4,800 | 4,800 | Y | TAK |
| T4 otwór słupka x=75: ø (blat) | 2,500 | 2,500 | 2,500 | 2,500 | X | TAK |
| T4 otwór słupka x=75: dno (y) | 91,000 | 91,000 | 90,800 | 90,800 | Y | TAK |
| T4 dno słupka x=75 pod otworem (materiał) | 1,800 | 1,800 | 1,600 | 1,600 | Y | TAK |
| T4 wkręt M3×8 x=75: gwint w słupku (lico − (100 − 8)) | 5,000 | 5,000 | 4,800 | 4,800 | Y | TAK |
| T5 kołek wkładki x=-58 w otworze blatu: luz promieniowy +X | 0,150 | 0,150 | 0,200 | 0,200 | X | TAK |
| T5 kołek wkładki x=-58 w otworze blatu: luz promieniowy −X | 0,150 | 0,150 | 0,200 | 0,195 | X | TAK |
| T5 kołek wkładki x=-58 w otworze blatu: luz promieniowy +Y | 0,150 | 0,151 | 0,200 | 0,202 | Y | TAK |
| T5 kołek wkładki x=-58 w otworze blatu: luz promieniowy −Y | 0,150 | 0,151 | 0,200 | 0,202 | Y | TAK |
| T5 otwór kołka x=-58: ø (blat) | 3,300 | 3,300 | 3,400 | 3,395 | X | TAK |
| T5 kołek x=-58: ø (wkładka) | 3,000 | 3,000 | 3,000 | 3,000 | X | TAK |
| T5 kołek x=-58: luz osiowy (koniec kołka − dno otworu) | 0,300 | 0,300 | 0,300 | 0,300 | Z | TAK |
| T5 kołek wkładki x=58 w otworze blatu: luz promieniowy +X | 0,150 | 0,150 | 0,200 | 0,200 | X | TAK |
| T5 kołek wkładki x=58 w otworze blatu: luz promieniowy −X | 0,150 | 0,150 | 0,200 | 0,195 | X | TAK |
| T5 kołek wkładki x=58 w otworze blatu: luz promieniowy +Y | 0,150 | 0,151 | 0,200 | 0,202 | Y | TAK |
| T5 kołek wkładki x=58 w otworze blatu: luz promieniowy −Y | 0,150 | 0,151 | 0,200 | 0,202 | Y | TAK |
| T5 otwór kołka x=58: ø (blat) | 3,300 | 3,300 | 3,400 | 3,395 | X | TAK |
| T5 kołek x=58: ø (wkładka) | 3,000 | 3,000 | 3,000 | 3,000 | X | TAK |
| T5 kołek x=58: luz osiowy (koniec kołka − dno otworu) | 0,300 | 0,300 | 0,300 | 0,300 | Z | TAK |
| T6 płytka n1 – wkładka: prawa y=20 | 0,300 | 0,300 | 0,400 | 0,400 | X | TAK |
| T6 płytka n1 – wkładka: prawa y=−30 | 0,300 | 0,300 | 0,400 | 0,400 | X | TAK |
| T6 płytka n1 – wkładka: lewa y=20 | 0,300 | 0,300 | 0,400 | 0,400 | X | TAK |
| T6 płytka n1 – wkładka: tylna x=20 | 0,300 | 0,300 | 0,400 | 0,400 | Y | TAK |
| T6 płytka n1 – wkładka: przednia x=30 | 0,300 | 0,300 | 0,400 | 0,400 | Y | TAK |
| T6 płytka n1 – wkładka: przednia x=−30 | 0,300 | 0,300 | 0,400 | 0,400 | Y | TAK |
| T6 otwór wkładki X (cięciwa) | 96,600 | 96,600 | 96,800 | 96,800 | X | TAK |
| T6 otwór wkładki Y (cięciwa, x 20) | 96,600 | 96,600 | 96,800 | 96,800 | Y | TAK |
| T6 rama wkładki zewn. X | 104,600 | 104,600 | 104,800 | 104,800 | X | TAK |
| T6 gabaryt wkładki Y (bbox) | 148,300 | 148,300 | 148,400 | 148,400 | Y | TAK |
| T6 płytka n1 bok X (promienie z zewnątrz) | 96,000 | 96,000 | 96,000 | 96,000 | X | TAK |
| T6 kołek orientacyjny – wycięcie płytki (x, strona otwarta) | 0,400 | 0,400 | 0,400 | 0,400 | X | TAK |
| T6 kołek orientacyjny – ściana otworu (x) | 0,500 | 0,500 | 0,600 | 0,600 | X | TAK |
| T6 margines matrycy: krawędź ramy → krawędź panelu (80) | 27,700 | 27,700 | 27,600 | 27,600 | X | TAK |
| T12 rowek panelu (60,60): szerokość prostopadle do przekątnej, korpus W | 3,400 | 3,400 | 3,600 | 3,600 | N | TAK |
| T12 rowek panelu: cięciwa wzdłuż X (= szer·√2), korpus W | 4,808 | 4,808 | 5,091 | 5,091 | X | TAK |
| T12 rowek panelu (60,60): szerokość prostopadle do przekątnej, korpus P | 3,400 | 3,400 | 3,600 | 3,600 | N | TAK |
| T12 rowek panelu: cięciwa wzdłuż X (= szer·√2), korpus P | 4,808 | 4,808 | 5,091 | 5,091 | X | TAK |
| T7 tulejka DC: ø walca (STL) | 11,850 | 11,849 | 11,850 | 11,849 | X | TAK |
| T7 otwór DC ø w korpusie W (Y) | 12,000 | 11,999 | 12,000 | 11,999 | Y | TAK |
| T7 tulejka w otworze: luz/stronę (ujemny = wcisk) | 0,075 | 0,075 | 0,075 | 0,075 | Y | TAK |
| łańcuch: wierzch ściany korpusu W | 59,600 | 59,600 | 59,600 | 59,600 | Z | TAK |
| łańcuch: wierzch blatu (90, 0) | 63,600 | 63,600 | 63,600 | 63,600 | Z | TAK |
| łańcuch: spód blatu na wierzchu ściany (styk) | 0,000 | 0,000 | 0,000 | 0,000 | Z | TAK |
| łańcuch: wierzch ramy wkładki (0, 50,3) | 69,600 | 69,600 | 69,600 | 69,600 | Z | TAK |
| łańcuch: wierzch płytki n1 (0, −46,5) | 74,100 | 74,100 | 74,100 | 74,100 | Z | TAK |

Pomiarów: 118; niezgodnych po R53: 0.

## 4. Kopie skryptów recenzenta (`skrypty/sprawdz_*_R53.py`)

| Skrypt | Sprawdzeń | NIE | Uwagi |
|---|---|---|---|
| wyniki_A_iterR53.json | 125 | 0 | płytki (pokrywka pominięta flagą `--bez-pokrywki`, jak w recenzji C1/C2; S‑05) |
| wyniki_A_iterR53pok.json | 136 | 3 | przebieg z pokrywką: 3 znane fałszywe NIE K‑02/K‑19/K‑21 (S‑05, pokrywka bajtowo bez zmian) — tylko dla objętości do K‑57; NIE: K-02 ramka_pokrywka_v2; K-19 ramka_pokrywka_v2; K-21 ramka_pokrywka_v2 |
| wyniki_B_iterR53.json | 73 | 0 | wkładka, blat, korpusy W/P, złożenie |
| wyniki_C_iterR53.json | 27 | 0 | tulejka, podkładki, K‑57, K‑60 |
| sprawdz_B_kanaly_R53 | 3 | 0 | ciągłość kanałów Halla A/B/C: C ciągły, B ciągły, A ciągły |

NIE łącznie (bez znanych fałszywych S‑05): 0.

## 5. Trzecie oko (kopia `trzecie_oko_R53.py`, G4b ponowione na zestawie R53)

Pasowania 671, wymiary 781, ścianki 107, kroki montażu 76. Blokujące surowe: 0.

Pasowania R53 w karcie trzeciego oka (wybór):

| Para | Miejsce | Luz z planu | Zmierzony | Werdykt |
|---|---|---|---|---|
| wkładka – blat: kołek ø3 w otworze ø3,4 (R53) | kołek x=-58, X, Z=62.6 | 0,200 | 0,200 | OK |
| wkładka – blat: kołek ø3 w otworze ø3,4 (R53) | kołek x=-58, -X, Z=62.6 | 0,200 | 0,195 | OK |
| wkładka – blat: kołek ø3 w otworze ø3,4 (R53) | kołek x=-58, Y, Z=62.6 | 0,200 | 0,202 | OK |
| wkładka – blat: kołek ø3 w otworze ø3,4 (R53) | kołek x=-58, -Y, Z=62.6 | 0,200 | 0,202 | OK |
| wkładka – blat: kołek ø3 w otworze ø3,4 (R53) | kołek x=-58, X, Z=61.1 | 0,200 | 0,200 | OK |
| wkładka – blat: kołek ø3 w otworze ø3,4 (R53) | kołek x=-58, -X, Z=61.1 | 0,200 | 0,195 | OK |
| wkładka – blat: kołek ø3 w otworze ø3,4 (R53) | kołek x=-58, Y, Z=61.1 | 0,200 | 0,202 | OK |
| wkładka – blat: kołek ø3 w otworze ø3,4 (R53) | kołek x=-58, -Y, Z=61.1 | 0,200 | 0,202 | OK |
| wkładka – blat: kołek ø3 w otworze ø3,4 (R53) | kołek x=58, X, Z=62.6 | 0,200 | 0,200 | OK |
| wkładka – blat: kołek ø3 w otworze ø3,4 (R53) | kołek x=58, -X, Z=62.6 | 0,200 | 0,195 | OK |
| wkładka – blat: kołek ø3 w otworze ø3,4 (R53) | kołek x=58, Y, Z=62.6 | 0,200 | 0,202 | OK |
| wkładka – blat: kołek ø3 w otworze ø3,4 (R53) | kołek x=58, -Y, Z=62.6 | 0,200 | 0,202 | OK |
| wkładka – blat: kołek ø3 w otworze ø3,4 (R53) | kołek x=58, X, Z=61.1 | 0,200 | 0,200 | OK |
| wkładka – blat: kołek ø3 w otworze ø3,4 (R53) | kołek x=58, -X, Z=61.1 | 0,200 | 0,195 | OK |
| wkładka – blat: kołek ø3 w otworze ø3,4 (R53) | kołek x=58, Y, Z=61.1 | 0,200 | 0,202 | OK |
| wkładka – blat: kołek ø3 w otworze ø3,4 (R53) | kołek x=58, -Y, Z=61.1 | 0,200 | 0,202 | OK |
| pokrywka – wkładka: kołnierz nad ramą | (30,-49.5) | 0,500 | 0,500 | OK |
| pokrywka – wkładka: kołnierz nad ramą | (-30,49.5) | 0,500 | 0,500 | OK |
| blat – korpus W: kołnierz 194,0 w 195 | X w (97.15,30,54.6) | 0,700 | 0,700 | OK |
| blat – korpus W: kołnierz 194,0 w 195 | -X w (-97.15,30,54.6) | 0,700 | 0,700 | OK |
| blat – korpus W: kołnierz 194,0 w 195 | -Y w (30,-97.15,54.6) | 0,700 | 0,700 | OK |
| blat – korpus W: kołnierz 194,0 w 195 | -Y w (-30,-97.15,54.6) | 0,700 | 0,700 | OK |
| blat – korpus W: kołnierz 194,0 w 195 | Y w (30,97.15,54.6) | 0,700 | 0,700 | OK |
| blat – korpus W: haczyk prawy — zahaczenie | czubek 98.300 − ściana wewn. 97.500 | 0,800 | 0,800 | OK |
| blat – korpus W: haczyk prawy — luz do dna kieszeni | dno 98.800 − czubek 98.300 | 0,500 | 0,500 | OK |
| blat – korpus W: haczyk prawy — luz pod występem (Z) | start rampy 52.87 − dno kieszeni 52.10 | 0,750 | 0,770 | OK |
| blat – korpus W: haczyk prawy — luz nad występem (Z) | sufit kieszeni 55.60 − górna krawędź występu 54.84 | 0,750 | 0,760 | OK |
| blat – korpus W: haczyk prawy — szerokość 8 w kieszeni 10 | luz wzdłuż Y na stronę | 1,500 | 1,500 | OK |
| blat – korpus W: haczyk lewy — zahaczenie | czubek 98.300 − ściana wewn. 97.500 | 0,800 | 0,800 | OK |
| blat – korpus W: haczyk lewy — luz do dna kieszeni | dno 98.800 − czubek 98.300 | 0,500 | 0,500 | OK |
| blat – korpus W: haczyk lewy — luz pod występem (Z) | start rampy 52.87 − dno kieszeni 52.10 | 0,750 | 0,770 | OK |
| blat – korpus W: haczyk lewy — luz nad występem (Z) | sufit kieszeni 55.60 − górna krawędź występu 54.84 | 0,750 | 0,760 | OK |
| blat – korpus W: haczyk lewy — szerokość 8 w kieszeni 10 | luz wzdłuż Y na stronę | 1,500 | 1,500 | OK |
| blat – korpus W: haczyk przedni — zahaczenie | czubek 98.300 − ściana wewn. 97.500 | 0,800 | 0,800 | OK |
| blat – korpus W: haczyk przedni — luz do dna kieszeni | dno 98.800 − czubek 98.300 | 0,500 | 0,500 | OK |
| blat – korpus W: haczyk przedni — luz pod występem (Z) | start rampy 52.87 − dno kieszeni 52.10 | 0,750 | 0,770 | OK |
| blat – korpus W: haczyk przedni — luz nad występem (Z) | sufit kieszeni 55.60 − górna krawędź występu 54.85 | 0,750 | 0,750 | OK |
| blat – korpus W: haczyk przedni — szerokość 8 w kieszeni 10 | luz wzdłuż X na stronę | 1,500 | 1,500 | OK |
| blat – korpus W: haczyk tylny — zahaczenie | czubek 98.300 − ściana wewn. 97.500 | 0,800 | 0,800 | OK |
| blat – korpus W: haczyk tylny — luz do dna kieszeni | dno 98.800 − czubek 98.300 | 0,500 | 0,500 | OK |
| blat – korpus W: haczyk tylny — luz pod występem (Z) | start rampy 52.87 − dno kieszeni 52.10 | 0,750 | 0,770 | OK |
| blat – korpus W: haczyk tylny — luz nad występem (Z) | sufit kieszeni 55.60 − górna krawędź występu 54.84 | 0,750 | 0,760 | OK |
| blat – korpus W: haczyk tylny — szerokość 8 w kieszeni 10 | luz wzdłuż X na stronę | 1,500 | 1,500 | OK |
| blat – korpus W: wkręt x=-75 — współosiowość otworów | ściana ø3,2 vs słupek ø2,5 (XZ) | 0,000 | 0,000 | OK |
| blat – korpus W: wkręt x=-75 — ø w ścianie | cięciwa X | 3,600 | 3,600 | OK |
| blat – korpus W: wkręt x=-75 — ø w słupku | cięciwa X | 2,500 | 2,500 | OK |
| blat – korpus W: wkręt x=75 — współosiowość otworów | ściana ø3,2 vs słupek ø2,5 (XZ) | 0,000 | 0,000 | OK |
| blat – korpus W: wkręt x=75 — ø w ścianie | cięciwa X | 3,600 | 3,600 | OK |
| blat – korpus W: wkręt x=75 — ø w słupku | cięciwa X | 2,500 | 2,500 | OK |
| blat – korpus P: kołnierz 194,0 w 195 | X w (97.15,30,54.6) | 0,700 | 0,700 | OK |
| blat – korpus P: kołnierz 194,0 w 195 | -X w (-97.15,30,54.6) | 0,700 | 0,700 | OK |
| blat – korpus P: kołnierz 194,0 w 195 | -Y w (30,-97.15,54.6) | 0,700 | 0,700 | OK |
| blat – korpus P: kołnierz 194,0 w 195 | -Y w (-30,-97.15,54.6) | 0,700 | 0,700 | OK |
| blat – korpus P: kołnierz 194,0 w 195 | Y w (30,97.15,54.6) | 0,700 | 0,700 | OK |
| blat – korpus P: haczyk prawy — zahaczenie | czubek 98.300 − ściana wewn. 97.500 | 0,800 | 0,800 | OK |
| blat – korpus P: haczyk prawy — luz do dna kieszeni | dno 98.800 − czubek 98.300 | 0,500 | 0,500 | OK |
| blat – korpus P: haczyk prawy — luz pod występem (Z) | start rampy 52.87 − dno kieszeni 52.10 | 0,750 | 0,770 | OK |
| blat – korpus P: haczyk prawy — luz nad występem (Z) | sufit kieszeni 55.60 − górna krawędź występu 54.84 | 0,750 | 0,760 | OK |
| blat – korpus P: haczyk prawy — szerokość 8 w kieszeni 10 | luz wzdłuż Y na stronę | 1,500 | 1,500 | OK |
| blat – korpus P: haczyk lewy — zahaczenie | czubek 98.300 − ściana wewn. 97.500 | 0,800 | 0,800 | OK |

Montaż (wybór): korpus W: blat na korpus (haczyki; z góry 20) → OK (ugięcie haczyka 0.80 ≤ 1.50); wkładka na kołki blatu (z góry 20) → OK; pokrywka na płytkę wieczorna_n1 (z góry 20) → OK (ugięcie garbu 0.40 ≤ 0.45); korpus P: blat na korpus (haczyki; z góry 20) → OK (ugięcie haczyka 0.80 ≤ 1.50)

Kroków montażu z werdyktem innym niż OK: 8 — wszystkie oznaczone „INFORMACYJNIE” (wtyk prosty 40 w osi, gniazdo USB po prostej 20 mm, wtyk Bonnetu 20 mm w −X/+Y): identyczne jak w pierwotnym raporcie G4b z 27.10 (`recenzja_koncowa/tabele_auto.md`), nie dotyczą R53. W 1. przebiegu kopii trzeciego oka wykryto 1 realne przenikanie (kołek orientacyjny wkładki vs R 1,5 wnęki pokrywki, 0,059 mm) → T6c `orient_post_gap` 0,6, regeneracja, ponowna pełna weryfikacja (ten raport).

## 6. Arkusze, README, model

- Części NIE objęte R53 (8 płytek, pokrywka, tulejka, 3 podkładki): bajtowo identyczne z kopią zapasową (tabela 2); `json/uklad_gniazd_*.json` i `arkusze/kody_plytek.md` identyczne z kopią.

- `arkusz_wymiarow.md`: zrzut `parametry.json` SHA `f57f1d084bc1…` = bieżącym `parametry.json` (`f57f1d084bc1…`).
- arkusz pasowań: kołnierz blatu – ściana korpusu (x) → zmierzone 0,700, nominał 0,700, 0,000 ✓
- arkusz pasowań: haczyk blatu: zahaczenie w kieszeni korpusu (x) → zmierzone -0,800, nominał -0,800, 0,000 ✓
- arkusz pasowań: haczyk blatu: luz do dna kieszeni (x) → zmierzone 0,500, nominał 0,500, 0,000 ✓
- arkusz pasowań: haczyk blatu: luz nad występem (z) → zmierzone 0,750, nominał 0,750, 0,000 ✓
- arkusz pasowań: kołek wkładki w otworze blatu (x) → zmierzone 0,200, nominał 0,200, 0,000 ✓
- arkusz pasowań: płytka w otworze wkładki (x) → zmierzone 0,400, nominał 0,400, 0,000 ✓
- arkusz pasowań: kołek orientacyjny w wycięciu płytki (x) → zmierzone 0,400, nominał 0,400, 0,000 ✓
- arkusz pasowań: tulejka DC w otworze ściany skrzynki (y) → zmierzone 0,076, nominał 0,075, 0,001 ✓
- `arkusz_zamowienia.csv`: 15 wierszy; wkładka gabaryt 130,0 × 148,4 × 11,0.
- `README.md`: ostatni przebieg: etap C, iteracja 5, raport `raport/raport_wykonawcy_C_iter5.md` (sumy SHA‑256 wszystkich plików).

## 7. Werdykt

**0 NIE.** Generator B=0/P=0/D=0 (B5, C5, SPRAWDZ5); kopie recenzenta A/B/C/kanały 0 NIE (3 znane fałszywe NIE pokrywki S‑05 tylko w przebiegu pomocniczym z pokrywką); trzecie oko 0 blokujących na 17 STL + bryły zastępcze; pomiar własny ze znakiem 118/118 zgodnych po R53 (i 118/118 dla stanu sprzed R53 — metoda potwierdzona). Wszystkie pasowania T1–T15 zgodne z `R53_projekt.md`.
