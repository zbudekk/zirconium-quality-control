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
- Po budowie dopisz wiersz do `SHA256SUMS_wydania.txt` (`<sha256>  <plik>`) i wiersz do tabeli ponizej.
- Kazdy commit zmienia paczke (numer commita i data sa w `wydanie.json`), takze commit, ktory zmienia tylko pliki spoza
  paczki. Wczesniejsze wydanie odtwarza `--rewizja <commit z tabeli>`.
- Numer wersji: plik `Ramki/stanowisko/WERSJA` (jeden wiersz) albo `--wersja`. Paczka o tym samym numerze i innej tresci
  nie zastapi zainstalowanej wersji biezacej - nowe wydanie = nowy numer.

## Wydania

| Wersja | Data | Commit | Rozmiar ZIP | Uwagi |
|---|---|---|---|---|
| 0.3.0 | 2026-11-20 | `6ebcf3b79e74f0241d44f3cf22987c60f859b6da` (galaz `e3/a11i`) | 444 093 233 bajty (423,5 MB) | pierwsza paczka wariantu B, dowod budowy: 201 plikow + `SHA256SUMS` (program 122, kola 73, kola testowe 3). Zbudowana z samej galezi `e3/a11i` z `--bez-samokontroli` - NIE zawiera `stanowisko/samokontrola.py` (paczka E3-A11s), wiec instalator konczy ja kodem 3 "blad wydania". Paczke do instalacji (testy T0 i T12) buduje koordynator po scaleniu galezi. Opis zawartosci: `Stanowisko_0.3.0.wydanie.json` |
