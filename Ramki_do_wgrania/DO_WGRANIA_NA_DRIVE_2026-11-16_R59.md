# Pakiet R59 — DO WGRANIA na Google Drive (folder QC) — pakiet z 2026-11-16, jeszcze NIE wgrany

Wgranie dopiero po zgodzie właściciela. Po wgraniu zapisać potwierdzenie w `WGRANE_NA_DRIVE_2026-11-16_R59.md` (wzór: `WGRANE_NA_DRIVE_2026-11-01_R56.md`).

Folder: QC (Mój dysk > QC), https://drive.google.com/drive/folders/18IztJQMtkOeDU99AvrPX1FsRXg8IBR4o
Zasady: tylko „Nowy → Prześlij plik”, nic nie usuwać, nic nie nadpisywać; każda nazwa poniżej jest nowa (R57 i starsze zostają).
Metoda (jak R56): JS nadpisuje `HTMLInputElement.prototype.click` (przechwycenie input), Nowy → Prześlij plik, `find` „upload-input”, `file_upload` jeden plik na raz; po wgraniu odświeżyć listę i potwierdzić nazwy.

| Plik (ten folder) | Bajty | SHA‑256 (pierwsze 16) |
|---|---|---|
| Ramki_pakiet_2026-11-16_R59_cz1_dokumenty_druk.zip | 4 599 220 | 4bd4432221b43839 |
| Ramki_pakiet_2026-11-16_R59_cz2_model.zip | 8 359 286 | dd199bb1b3e190d4 |
| Ramki_pakiet_2026-11-16_R59_cz3_zrodla.zip | 6 891 313 | 21eaef1533088c95 |
| SHA256SUMS_2026-11-16_R59.txt | 9 169 | 107eb82b4163872c |
| INSTRUKCJA_PAKIET_2026-11-16_R59.md | 4 803 | 7e6233c0bab282bd |
| 01_Plan_wdrozenia_v2_2026-11-16_R59.pdf | 866 864 | 57b5afd703994a90 |
| 02_Zakupy_i_druk_2026-11-16_R59.pdf | 421 241 | 71433fce8c4deb0c |
| 03_Budowa_ramki_decyzje_i_zamienniki_2026-11-16_R59.pdf | 418 238 | 8a16e9dcefbecdf9 |

ZIP‑y zbudowane i sprawdzone skryptem `Ramki/narzedzia/zbuduj_pakiet_R59.sh`: po złożeniu trzech ZIP‑ów w jeden folder 81 z 81 plików zgodnych z SHA256SUMS_2026-11-16_R59.txt (cz1 33 plików razem z README i plikiem sum, cz2 17, cz3 32); każdy ZIP < 10 MB. PDF‑y identyczne z `Ramki_pakiet/01_Dokumenty/`.
