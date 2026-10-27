# modele - uklady gniazd plytek

| Plik | Plytka | Numery | Gniazda |
|---|---|---|---|
| `uklad_gniazd_wieczorna.json` | wieczorna (prace przed spiekaniem) | 1, 2, 3 | 24 stozkowe + 2 rynienki 60 x 15 (id 25, 26) |
| `uklad_gniazd_poranna.json` | poranna (prace po spiekaniu) | 4, 5, 6 | 35 stozkowych + 2 rynienki 50 x 13 (id 36, 37) |

## Skad sa pliki

Pliki generuje skrypt projektu ramek (plan budowy ramek v2, sekcja 4.1, decyzja D6) razem z modelami
plytek do druku. Zrodlem prawdy ukladu jest ramka; qc tylko czyta ten sam format (`qc.uklad.wczytaj`)
i nie zmienia plikow. Sciezki do plikow sa w `ustawienia.toml`, sekcja `[plytki]`.

## Uklad wspolrzednych

- Poczatek: srodek gornej powierzchni plytki; X w prawo (od uzytkownika), Y do tylu (przod = -Y),
  Z w gore; wierzch Z = 0, dno Z = -8 (`thickness`), plytka 96 x 96 mm (`size`), jednostki mm.
- Narozniki: A (-48, -48) przod-lewy, B (-48, 48) tyl-lewy, C (48, 48) tyl-prawy,
  D (48, -48) przod-prawy z wycieciem przelotowym (`notch`).
- Znaczniki A, B, C (`markers`): wklesle stozki d x depth; pod nimi od spodu kieszenie magnesow
  (`magnet_pockets`, d x depth).
- Gniazda (`sockets`): `round` = stozek (d_top, d_bottom = d_top - 2 depth tan 15 st., depth) z otworem
  `hole_d` w osi; `trough` = rynienka-stadion l x w, scianki 15 st., `hole_count` otworow co `hole_pitch`.
  Numeracja id rzedami od przodu, w rzedzie malejace x.
- Walidacja przy wczytaniu jak kontrola K-05 ramki: rzedy symetryczne wzgledem x = 0, obrysy w
  [-45, 45]^2 i poza kwadratami naroznymi, odstep obrysow >= 3 mm, zgodne d_bottom, ciagle id.

## Kod numeru plytki

Dolki kodu (`code_dimples`, bity A, B, C) i magnesy: n = A + 2B + 4C (bit = dolek/magnes obecny):
1 = A, 2 = B, 3 = AB, 4 = C, 5 = AC, 6 = BC; 0 = brak plytki, 7 = rezerwa. Plik bazowy (bez numeru) ma
wszystkie 3 dolki; plytka o numerze n ma tylko dolki bitow = 1 i relief cyfry (`number_relief`).

## Wyjatek od konwencji ASCII

Pola tekstowe `coords` zawieraja polskie znaki (UTF-8), bo pliki pochodza ze zrodla zewnetrznego
(skrypt ramki). Pliki sa w repo bajt w bajt jak z ramki (UTF-8, konce linii LF); qc czyta je jako UTF-8.
Nie poprawiac ich recznie.

## Podmiana po zmianie ramki

1. Skopiowac nowe pliki z ramki bajt w bajt (np. `Copy-Item`), bez formatowania i zmiany kodowania.
2. Porownac sha256 (`Get-FileHash`) z plikami zrodlowymi; po commicie i checkout musza byc takie same.
3. Uruchomic `python -m pytest -q tests/test_uklad.py tests/test_syntetyka_plytka.py`.
Kod nie powinien wymagac zmian; nowe klucze sa ignorowane, brak klucza wymaganego = `BladUkladu`.
