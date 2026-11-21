# Wydania programu "Stanowisko" - sumy i opisy (bez plikow ZIP)

Paczki wydania (`Stanowisko_<wersja>.zip`, ok. 430 MB) i kola pip NIE trafiaja do repozytorium. Tu leza tylko sumy
SHA-256 zbudowanych paczek (`SHA256SUMS_wydania.txt`) i krotki opis kazdego wydania. Mechanizm, zawartosc paczki
i kroki instalacji: `../../stanowisko/opisy_modulow/instalacja.md`; instrukcja dla osoby instalujacej:
`../../stanowisko/instrukcje/instalacja_i_aktualizacja.md`.

## Jak powstaje wydanie

```
cd Ramki\stanowisko
python narzedzia\zbuduj_wydanie.py --pobierz-kola --kola <PC-katalog>\wydania\kola      (raz, z internetem; takze po zmianie requirements.txt)
python narzedzia\zbuduj_wydanie.py --wyjscie <PC-katalog>\wydania --kola <PC-katalog>\wydania\kola [--wersja X] [--rewizja COMMIT]
```

- Paczka powstaje z commita (domyslnie `HEAD`), nie z katalogu roboczego, i jest powtarzalna bajtowo: ten sam commit
  + te same kola + ten sam interpreter budujacy = ten sam SHA-256. Obok ZIP powstaje plik `<nazwa>.zip.sha256`.
- Po budowie paczki, ktora idzie do ludzi (opublikowanej): dopisz wiersz do `SHA256SUMS_wydania.txt` (`<sha256>  <plik>`)
  i wiersz do tabeli ponizej, potem zwieksz numer w `Ramki/stanowisko/WERSJA` (osobny commit) - plik `WERSJA` wskazuje
  zawsze numer NASTEPNEGO wydania (pilnuje tego test `test_numer_wersji_i_lista_wydan`).
- Kazdy commit zmienia paczke (numer commita i data sa w `wydanie.json`), takze commit, ktory zmienia tylko pliki spoza
  paczki. Wczesniejsze wydanie odtwarza `--rewizja <commit z tabeli>`.
- Numer wersji `0.3.<n>`: plik `Ramki/stanowisko/WERSJA` (jeden wiersz) albo `--wersja`. **Kazda opublikowana budowa = nowy
  numer** (decyzja koordynatora 20.11): paczka o tym samym numerze i innej tresci nie zastapi zainstalowanej wersji biezacej
  ani poprzedniej (instalator: kod 3), a budowa pod numerem z `SHA256SUMS_wydania.txt` o innej sumie wypisuje `OSTRZEZENIE`.
  Numer jest nazwa katalogu w Windows: litery, cyfry, `.`, `_`, `-`; pierwszy i ostatni znak to litera albo cyfra.
- Paczki nie odchudzamy z zaleznosci nieuzywanych (ok. 160 MB): srodowisko wersji = dokladnie to, na ktorym przechodza testy.

## Wydania

| Wersja | Data | Commit | Rozmiar ZIP | Uwagi |
|---|---|---|---|---|
| 0.3.0 | 2026-11-20 | `14376218b891eaced32578a91885effc4fb77d22` (galaz `e3/a11i`) | 444 093 596 bajtow (423,5 MB) | pierwsza paczka wariantu B, dowod budowy: 201 plikow + `SHA256SUMS` (program 122, kola 73, kola testowe 3). Zbudowana z samej galezi `e3/a11i` z `--bez-samokontroli` - NIE zawiera `stanowisko/samokontrola.py` (paczka E3-A11s), wiec instalator konczy ja kodem 3 "blad wydania". Paczke do instalacji (testy T0 i T12) buduje koordynator po scaleniu galezi - pod numerem 0.3.1 (plik `WERSJA`). Opis zawartosci: `Stanowisko_0.3.0.wydanie.json` |
| 0.3.1 | 2026-11-21 | `571e186cb8178209da670dde244dfc56bba5e300` (`main`) | 444 935 199 bajtow (424,3 MB) | paczka koncowa etapu 3 - komplet paczek A11s, A11i, A11w, P14, A11d, P15; 210 plikow + `SHA256SUMS` (program 131, kola 73, kola testowe 3). Na niej wykonano testy koncowe T0-T13: `../odbior_koncowy/RAPORT.md`. Opis zawartosci: `Stanowisko_0.3.1.wydanie.json`. Paczka testowa `Stanowisko_0.3.2.zip` (ten sam commit, `--wersja 0.3.2`, SHA-256 `030c72d86420e9461a3de93b47d7a68baa80bfbb52aa0078bf1907c42abad96c`) sluzy tylko do testu T12 (aktualizacja N -> N+1 -> powrot) - nieopublikowana, bez wiersza w sumach |
