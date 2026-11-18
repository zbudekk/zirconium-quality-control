# pamiec_puli - pamiec podreczna projektow puli per praca (E3-A5, 18.11.2026)

**Co robi.** Trzyma dla kazdej geometrii puli per praca (projekt STL x wspolczynnik x orientacja) czesc lekka
(`match.ProjektLekki`: obrys, wysokosc, otoczka, profil glebokosci dla filtra wymiarow, chmura 0,3 mm z normalnymi do
rankingu wstepnego) i pelny `match.Projekt` (siatka, 40 tys. punktow, FPFH, scena promieni) - w procesie i na dysku,
jeden plik `.npz` na geometrie. Po co: budowa `match.Projekt` z pliku to 0,1-0,3 s, profil glebokosci kolejne 0,2-0,5 s
(zmierzone na PC na 5 projektach testowych i atrapie), a pula wieczorna ma kilkaset wpisow - bez pamieci kazdy start
programu kosztowalby minuty. Z dysku: czesc lekka 1-2 ms, pelny projekt 12-21 ms.

**Wejscie.** `PamiecPuli(katalog=None, limit_ciezkich=64)`; `z_ustawien(ust)` = katalog `[sciezki] pula_cache` / `projekty`
(klucz juz w ustawieniach, opcjonalny, domyslnie `dane/pula_cache`; obok linii brzegu z `krawedz`). Bez katalogu = tylko
pamiec procesu. Uzywa jej `match.Pula.z_wpisow(..., pamiec=...)` i `porownaj --wpisy` (`--pamiec-puli`).

**Wyjscie / API.** `lekki(plik, sha16, wspolczynnik, orientacja="auto") -> ProjektLekki` (z procesu, z dysku albo policzona
z pliku i zapisana razem z pelnym projektem; `ValueError` = pliku nie da sie wczytac); `projekt(lekki) -> Projekt` (z
procesu, z dysku albo z pliku; profil filtra przepisany z czesci lekkiej; `ValueError`, gdy plik zmienil sie od budowy
puli); `skrot(plik)` (skrot zawartosci, w procesie zapamietany po sciezce, rozmiarze i czasie zmiany); `pliki()`;
`sprzataj(dni)` -> liczba usunietych; `statystyka` (`lekkie_z_pamieci`, `lekkie_z_dysku`, `lekkie_policzone`,
`ciezkie_z_pamieci`, `ciezkie_z_dysku`, `ciezkie_z_pliku`, `bledy_odczytu`, `bledy_zapisu`, `czas_liczenia_s`,
`czas_odczytu_s`); `odcisk()`.

**Klucz i uniewaznianie.**
- Odcisk obejmuje ZRODLA funkcji liczacych dane (`funkcje_odcisku`: `synth.wczytaj_projekt`, `orientacja_brzegiem_do_gory`,
  `brzeg_z_heurystyki`, `strona_brzegu`, `plik_exocad`, `skrot_pliku`, `katalog.cechy`, `typ_i_zeby_z_nazwy`, `Projekt.__init__`,
  `_zbuduj_scene`, `lekki`, `do_tablic`, `z_tablic`, `_fpfh`, `_chmura`), wzorzec nazwy exocad, stale `match` i wersje open3d,
  trimesh, numpy i scipy - poprawka np. heurystyki orientacji daje nowe wpisy bez recznej zmiany `WERSJA` (P2 recenzji PR #25).
- Nazwa pliku: `<sha16>_<wspolczynnik>_<orientacja>_<znacznik>_<odcisk>.npz`; `sha16` = 16 znakow SHA-256 ZAWARTOSCI
  pliku (jak `synth.skrot_pliku`, katalog i A4), wspolczynnik do 6 miejsc, znacznik orientacji `e` (nazwa exocad - brzeg
  na dole z konwencji eksportu) albo `h` (heurystyka z siatki), odcisk = skrot wersji formatu, stalych `match`
  wplywajacych na dane (punkty probki, voxele FPFH / zgrubny / wstepny, krok profilu) i wersji open3d / trimesh.
- Plik zmieniony (inna zawartosc pod ta sama sciezka) = inny skrot = inny wpis; starych danych nie dostanie.
- Zmiana algorytmu albo bibliotek = inny odcisk = nowe wpisy; stare zostaja do `sprzataj`.
- Wpis uszkodzony, obciety albo z kluczem / skrotem / wspolczynnikiem niezgodnym z nazwa = liczony od nowa (licznik
  `bledy_odczytu`), bez wyjatku. Zapis atomowy (plik tymczasowy + `os.replace`) - kilka procesow moze dzielic katalog.
- `sprzataj(dni)`: usuwa wpisy nieuzywane od `dni` dni (kazdy odczyt odswieza czas pliku) i pozostalosci przerwanych
  zapisow starsze niz doba. Kto i kiedy wola sprzatanie - do ustalenia przy integracji z aplikacja (propozycja: przy
  starcie, `dni` = `[match] usun_z_puli_po_dniach` + zapas).

**Dane osobowe.** `match.Projekt` jest budowany z wyciszonymi ostrzezeniami (`synth.wczytaj_projekt` ostrzega z nazwa pliku),
a blad odczytu pliku wraca jako `ValueError` bez sciezki (P3 recenzji PR #25). Na dysku tylko skrot, liczby i cechy z nazwy pliku (zeby, typ pracy) - bez nazwy pliku, folderu i
sciezki (test `test_pamiec_bez_nazw_plikow` przeszukuje tresc plikow pamieci). Sciezka do STL jest wylacznie w pamieci
procesu (`ProjektLekki.zrodlo`), zeby zbudowac pelny projekt, gdy nie ma go na dysku.

**Kryterium "dziala".** `testy/test_pula_match.py`: `test_pamiec_zimna_i_ciepla_te_same_projekty` (drugi proces
wczytuje wszystko z dysku; projekt z pamieci = projekt z pliku: punkty, normalne, FPFH, siatka, transformacja; profil =
`cechy_do_glebokosci` do 1e-6), `test_pamiec_uniewaznienie_zmieniony_plik_uszkodzony_wpis_i_sprzatanie`,
`test_pamiec_bez_nazw_plikow`, `test_pamiec_z_ustawien`. Czasy na puli 400 wpisow: raport E3-A5.

**Zalozenia i granice.**
- Rozmiar na dysku: ok. 3-6 MB na geometrie (siatka + probka + FPFH bez kompresji, zeby odczyt byl szybki) - pula 400
  wpisow to ok. 1,5-2,5 GB; sprzatanie trzyma tylko wpisy z ostatnich dni.
- Czesc lekka nowego STL liczona jest w procesie, ktory buduje pule (pomiar E3-A5 na PC: 0,9 s na wpis, 400 wpisow 361 s); pula kilkuset NOWYCH wpisow
  naraz (pierwszy start, pusta pamiec) to minuty - lepiej budowac pule zaraz po odswiezeniu, przed pierwszym skanem
  (integracja z silnikiem: poza ta paczka, raport E3-A5).
- Pelnych projektow w procesie najwyzej `limit_ciezkich` (64, ok. 10-30 MB kazdy); najdawniej uzyte wypadaja i wracaja z dysku.
- **Wymaganie dla paczki integracji (A5i, D4 recenzji PR #25):** dzis nic poza testem nie wola `sprzataj`, a katalog nie ma limitu
  rozmiaru (ok. 5,5 MB na geometrie, float64 bez kompresji; 200 nowych geometrii dziennie = ok. 1,1 GB dziennie). Paczka, ktora
  podlacza pule wpisow do silnika / aplikacji, musi: wolac `sprzataj(dni)` (przy starcie albo przy odswiezeniu puli), ustalic
  limit rozmiaru katalogu (najstarsze `mtime` pierwsze) i rozwazyc float32 dla siatki, probki i FPFH (ok. polowa miejsca;
  wymaga nowej `WERSJA` i pomiaru zgodnosci). `porownaj --wpisy` bez `--pamiec-puli` pisze do `dane/pula_cache/projekty`.
