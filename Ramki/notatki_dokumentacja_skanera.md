# Notatki z dokumentacji skanera Aidite A-IS Pro / DentalScan 3.0.4

27 października 2026. Źródła: instrukcja PDF A-IS Pro (2020, 93 str.) i https://docs.doc-usermanual.com/aidite/dentalscan/3.0.4/en-us/ (podstrony: scaninterface, workflow-settings, settingscan, settingorder, dataedit, addscan, navigationmode, parameters-scan, shortcut-instruction, third-party-software, dietray, fixture, overview, otheroperation).

## Co potwierdza plan v2

| Temat | Co mówi dokumentacja | Wpływ na plan |
|---|---|---|
| Start skanu | Spacja = „Starts a scan or moves forward”, Esc = przerwij (strona shortcut-instruction) | „Spacja na laptopie” z planu działa wprost w programie producenta; automat (pyautogui) sprowadza się do: aktywuj okno DentalScan + Spacja |
| Folder wyjściowy | Order Save Path do ustawienia (settingorder → General); stary PDF: STL zapisywany w folderze „Scandata” po „Apply”/„Next” | Moduł scanner obserwuje ten folder (watchdog) — bez klikania w eksport |
| Nazwa pliku | „Order File Naming Rule”: elementy nazwy do wyboru | Da się ustalić nazwę przewidywalną dla programu |
| Tryb wielu prac | „Multidie Mode” / „Die Order”: jeden skan całej płytki z wieloma pracami; płytka producenta trzyma prace plasteliną | Nasza płytka zastępuje „Multi-die Fixture”; interfejs mocowania stolika nadal nieopisany (STEP od Aidite) |
| Wymagania PC | Win10 64-bit Pro, i7-9700+, 16 GB, NVIDIA 1060Ti+, 2 × USB 3.0, SSD 256 GB | Laptop z planu (i7/i9, 32 GB, RTX) wystarcza |
| Błyszczące / przezierne | Opcje: „HDR”, „Add details / High Quality”, „Mental tooth” (obiekty odbijające), „reduce high brightness” (tryb die tray), „Save Image” (zapis surowych zdjęć kamer) | Kryterium 5 testu ma co włączać; „Save Image” daje zdjęcia 5 MP płytki za darmo → tani plan B poranka bez osobnej kamery do sprawdzenia |
| Obróbka siatki | Wypełnianie otworów ręczne (promień 2/4/6 mm; ręczne 5 mm domyślnie), cięcie płaszczyzną, kasowanie zaznaczeń; brak udokumentowanego automatycznego wygładzania/upraszczania | Prawdopodobnie da się eksportować „surową” siatkę; do potwierdzenia w teście (lista pytań do Aidite, pkt 3) |

## Co dokumentacja NIE rozstrzyga (zostaje w teście)

1. **Ścieżka skanu bez przechyłu (kryterium 1).** Strategie: basic 6 / medium 9 / advanced 12 pozycji — bez podanych kątów. „Manual Add-scan”: użytkownik obraca model na ekranie do wybranego widoku, skaner dojeżdża. Żadnej udokumentowanej kontroli osi obrotu i przechyłu ani zapisu własnej strategii. Trzeba zobaczyć na egzemplarzu.
2. **Pole skanowania (kryterium 8).** Brak wymiarów w dokumentacji.
3. **Skan bez zlecenia.** Każdy skan wymaga zlecenia w DentalManager (Multidie: „scan now, or save and scan later”). Zlecenie można zapisać raz i wracać do niego — do sprawdzenia, czy jedno zlecenie „Płytka” obsłuży wiele skanów dziennie.
4. **Płaszczyzna cięcia.** Program każe odciąć „jig data” (uchwyt) płaszczyzną — nasze stożki znaczników i dołki kodu muszą zostać NAD płaszczyzną cięcia (cięcie poniżej wierzchu płytki) albo cięcie ustawione raz w zleceniu.

## Ryzyka nowe wobec planu v2

- **Klucz sprzętowy (dongle USB)** i **„Authorization Remaining Days”** z prośbą o przedłużenie: licencja jest czasowa i przypięta do klucza. Do umowy: bezterminowa autoryzacja, praca offline, drugi klucz na laptop deweloperski (plan zakładał „drugą licencję”).
- **Program jest OEM Shining3D** (DentalScan; zasoby na doc-asset.shining3d.com, „MIX Series” = Shining ASDS-MIX, opcja „Mental tooth”). Aktualizacje i wsparcie zależą od Shining, nie Aidite.
- **Brak SDK/API.** Integracja z exocad/DentalWings tylko przez „wspólną bazę danych” i eksport z okna. Automat klikający pozostaje jedyną drogą poza folderem.

## Pytania do Aidite (uzupełnienie listy z planu)

- Jaki model trafi do nas: A-IS Pro (IPBA) czy (IPWA)? (Z‑axis adjust niedostępny dla obu w 3.0.4.)
- Czy w Multidie można zapisać strategię z samym obrotem (bez swing)? Nagranie ekranu.
- Czy eksport STL po „Apply” jest automatyczny do Order Save Path i jaka jest struktura folderu zlecenia?
- Czy „Save Image” zapisuje zdjęcia z obu kamer w pełnej rozdzielczości i w jakim formacie?
- Wymiary pola skanowania i interfejsu stolika (STEP).
