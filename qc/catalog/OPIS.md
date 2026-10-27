# qc.catalog - katalog projektow STL

## Co robi

Indeksuje projekty STL z folderow OneDrive/SharePoint "Cyrkon" i "Prywatne" do lokalnej bazy SQLite,
liczy cechy geometryczne do wstepnego filtra kandydatow (modul `match`) i sklada pule projektow:
rano (identyfikacja prac z ostatnich dni roboczych) i wieczorem (kontrola ukruszen prac z dzis i wczoraj
z wspolczynnikiem skali k).

- `nazwy.py` - folder zlecenia -> `Zlecenie(kuweta, nazwisko, nazwa, prywatne)`: kuweta = pierwsza
  samodzielna liczba 1-4 cyfr bez zer wiodacych ("Nowak 0041" -> "41"), "#1234" -> kuweta "#1234" i
  prywatne; nazwisko = pierwsze slowo literowe (z lacznikiem). `numer_zeba(plik)` = numer FDI
  (11-18, 21-28, 31-38, 41-48) jako samodzielna liczba w nazwie pliku. `znormalizuj` do porownan.
- `cechy.py` - `policz(siatka, ziarno)`: objetosc (tylko bryla zamknieta, inaczej None), pole, wymiary
  = rozpietosc wzdluz osi PCA wierzcholkow (numpy eigh) malejaco, D2 = histogram odleglosci 20 000
  losowych par punktow z `trimesh.sample.sample_surface` (64 koszyki od 0 do 1,05 x przekatna wymiarow,
  suma 1, wiec niezalezny od skali). `przeskaluj(k)`, `odleglosc` = 0,5 x L1(d2) + 0,5 x max wzgledna
  roznica wymiarow, `pasuje(skan, projekt, k, ustawienia)` - tolerancje `dopasowanie.tolerancja_objetosci`
  (wzgledna) i `tolerancja_wymiarow_mm`; objetosc pomijana, gdy skan jest otwarty (None).
- `baza.py` - `Baza(sciezka)`: schemat (tabele `projekty`, `wspolczynniki`, PRAGMA user_version = 1),
  rekordy jako dict kolumn, d2 jako BLOB float32. Polaczenie na kazde wywolanie.
- `indeks.py` - `skanuj`: `os.scandir` na glebokosc 2 (folder zlecenia / pliki .stl bez wielkosci
  liter), klucz zmiany (mtime_ns, rozmiar); cechy tylko dla nowych i zmienionych (STL wczytany
  `process=False` + scalenie wierzcholkow); brak pliku -> `usuniety = 1`. Brak calego katalogu zrodla
  (OneDrive niezsynchronizowany) = zrodlo pominiete bez oznaczania usuniec. `pula_rano`: `pula.dni_rano`
  dni roboczych wstecz (sb/nd sie nie licza, pliki z weekendu naleza do piatku), dzis zawsze w puli,
  k = 1,0. `pula_wieczor`: STL z CSV wspolczynnikow z dzis i wczoraj, szukane po nazwie pliku.
- `wspolczynniki.py` - CSV wspolczynnikow skali.

Parser raportow MillBox (BeautifulSoup4/pypdf) czeka na zanonimizowany raport przykladowy. Do tego czasu
plan B: plik CSV `sciezki.wspolczynniki` (UTF-8, srednik, naglowek `plik;krazek;wspolczynnik;data`,
przecinek dziesietny dozwolony, data RRRR-MM-DD), wypelniany przez operatora frezarki przy wycinaniu
krazka: nazwa pliku STL, oznaczenie krazka, wspolczynnik skali z MillBox, data frezowania.

## Wejscie

- `ustawienia` (qc.ustawienia): `sciezki.cyrkon`, `sciezki.prywatne`, `sciezki.baza`,
  `sciezki.wspolczynniki`, `dopasowanie.tolerancja_*`, `pula.dni_rano`, `pula.dni_wieczor`,
  `pula.usuwaj_po_dniach`.
- Foldery `<zrodlo>/<folder zlecenia>/*.stl`; CSV wspolczynnikow.

## Wyjscie

- Baza `dane/qc.sqlite` (tabele `projekty`, `wspolczynniki`); `RaportIndeksu(nowe, zmienione, usuniete)`.
- Pule: `list[Wpis(projekt_id, wspolczynnik)]`, wieczorem dodatkowo liczba STL z CSV nieobecnych w bazie.
- `Cechy` do filtra kandydatow w `match`.

RODO: baza jest lokalna (`dane/qc.sqlite`, w .gitignore), nazwiska i nazwy folderow zostaja tylko na
laptopie stanowiska; w repo i testach wylacznie nazwy fikcyjne i siatki syntetyczne.

## Kryterium "dziala"

- `python -m pytest tests/test_catalog.py` zielone (dane syntetyczne, drzewo folderow w tmp_path).
- Etap 3: pierwszy prawdziwy folder Cyrkon zaindeksowany bez bledu (liczba nowych = liczba plikow
  STL, kuwety i numery zebow zgodne z nazwami folderow w probce sprawdzonej recznie).
