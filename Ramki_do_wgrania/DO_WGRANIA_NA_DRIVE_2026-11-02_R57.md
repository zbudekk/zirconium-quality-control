# Pakiet R57 — DO WGRANIA na Google Drive (folder QC) — NIE wgrany 2.11.2026 ok. 18:05

Powód: Claude in Chrome niepołączony (`list_connected_browsers` = 0 przeglądarek, dwie próby). Łącznik Google Drive w sesji przyjmuje treść tylko inline (base64) — nie nadaje się do ZIP‑ów 4,5–7,6 MB ani PDF‑ów; nic nie wgrano częściowo.

Folder: QC (Mój dysk > QC), https://drive.google.com/drive/folders/18IztJQMtkOeDU99AvrPX1FsRXg8IBR4o
Zasady: tylko „Nowy → Prześlij plik”, nic nie usuwać, nic nie nadpisywać; każda nazwa poniżej jest nowa (R56 i starsze zostają).
Metoda (jak R56): JS nadpisuje `HTMLInputElement.prototype.click` (przechwycenie input), Nowy → Prześlij plik, `find` „upload-input”, `file_upload` jeden plik na raz; po wgraniu odświeżyć listę i potwierdzić nazwy; zapis `WGRANE_NA_DRIVE_2026-11-02_R57.md`.

| Plik (ten folder) | Bajty | SHA‑256 (pierwsze 16) |
|---|---|---|
| Ramki_pakiet_2026-11-02_R57_cz1_dokumenty_druk.zip | 4 516 613 | 770d2053387ec3cd |
| Ramki_pakiet_2026-11-02_R57_cz2_model.zip | 7 583 041 | 440143f74ffa86a7 |
| Ramki_pakiet_2026-11-02_R57_cz3_zrodla.zip | 6 311 180 | bffe1d4c234c8ae1 |
| SHA256SUMS_2026-11-02_R57.txt | 7 067 | c85da672a05acea1 |
| INSTRUKCJA_PAKIET_2026-11-02_R57.md | 2 635 | 177eb3c063cdc135 |
| 01_Plan_wdrozenia_v2_2026-11-02_R57.pdf | 848 386 | 838b2e72cd0654dd |
| 02_Zakupy_i_druk_2026-11-02_R57.pdf | 409 036 | fa4c8707aed735fd |
| 03_Budowa_ramki_decyzje_i_zamienniki_2026-11-02_R57.pdf | 410 622 | b043365f7f92cc5b |

ZIP‑y sprawdzone: po rozpakowaniu do jednego folderu SHA256SUMS 63/63 OK. PDF‑y identyczne z `Ramki_pakiet/01_Dokumenty/`.
