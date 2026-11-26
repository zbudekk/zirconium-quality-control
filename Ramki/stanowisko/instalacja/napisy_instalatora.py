"""napisy_instalatora - teksty okna instalatora i trybu bez okna (E3-I1).

Teksty sa po polsku ze znakami diakrytycznymi (czyta je osoba instalujaca; tak jak ``stanowisko/ui/napisy.py`` paczki
E3-U1a) - plik UTF-8, bez Qt. Komentarze i nazwy bez znakow diakrytycznych. Kody wyjscia instalatora (``instalator.KOD_*``)
maja tu zdanie dla czlowieka (``ZDANIA_KODOW``) - test pilnuje, ze kazdy kod ma swoje.
"""
from __future__ import annotations

TYTUL_OKNA = "Stanowisko — instalacja"
NAZWA = "Stanowisko"
PODTYTUL = "Instalacja · wersja {wersja}"
STOPKA_KROKOW = "Bez internetu. Niczego nie zmienia poza folderem instalacji."
KROKI = ("Foldery", "Osoby", "Instalacja", "Gotowe")

# --- przyciski --------------------------------------------------------------------------------------------------------
ANULUJ = "Anuluj"
WSTECZ = "Wstecz"
DALEJ = "Dalej"
INSTALUJ = "Instaluj"
WYBIERZ = "Wybierz…"
ZMIEN = "Zmień…"
DODAJ = "Dodaj"
USUN = "Usuń"
ZAMKNIJ = "Zamknij"
SPROBUJ_PONOWNIE = "Spróbuj ponownie"
URUCHOM_PROGRAM = "Uruchom program"
URUCHOM_DZIEN_SKANERA = "Otwórz „Dzień skanera”"

# --- krok 1: foldery --------------------------------------------------------------------------------------------------
FOLDERY_TYTUL = "Wskaż foldery"
FOLDERY_PODTYTUL = "Możesz je później zmienić w pliku ustawień."
SKANY = "Folder ze skanami"
SKANY_OPIS = "Tu trafiają pliki STL ze skanera. Program sam zauważy każdy nowy plik."
PROJEKTY = "Folder z projektami"
PROJEKTY_OPIS = "Pliki STL z exocad, w podfolderach zleceń. Bez nich prace będą szare („bez projektu”)."
CEL = "Miejsce instalacji"
NIE_WYBRANO = "nie wybrano"
MIEJSCE = "Potrzeba {potrzeba} wolnego miejsca. Jest {wolne}."
MIEJSCE_NIEZNANE = "Potrzeba {potrzeba} wolnego miejsca."
AKTUALIZACJA = ("W tym folderze jest już program (wersja {wersja}). Instalator doda nową wersję obok; ustawienia, foldery, osoby "
                "i dane zostaną bez zmian. Poprzednia wersja zostaje — można do niej wrócić.")
WYBOR_FOLDERU = "Wybierz folder"

# --- krok 2: osoby ----------------------------------------------------------------------------------------------------
OSOBY_TYTUL = "Kto będzie pracował na stanowisku?"
OSOBY_PODTYTUL = "Imiona techników do wyboru na początku zmiany. Wybrana osoba trafia do każdej decyzji."
OSOBA_POLE = "Imię i nazwisko albo inicjały"
OSOBY_AKTUALIZACJA = "Osoby z dotychczasowych ustawień (zostają bez zmian):"

# --- walidacje (zdania bledow kroku 1 i 2) ----------------------------------------------------------------------------
BRAK_SKANOW = "Wskaż folder ze skanami."
SKANY_NIE_ISTNIEJE = "Folder ze skanami nie istnieje: {sciezka}. Wybierz istniejący folder przyciskiem „Wybierz…”."
PROJEKTY_NIE_ISTNIEJE = "Folder z projektami nie istnieje: {sciezka}. Wybierz istniejący folder albo zostaw pole puste."
PROJEKTY_PUSTE = ("Nie wybrano folderu z projektami — instalator założy pusty folder {sciezka}. Dopóki nie będzie w nim projektów STL "
                  "(albo nie wskażesz właściwego folderu w ustawieniach), program nie rozpozna prac: skany będą czekać na projekty. "
                  "Kliknij „Dalej”, aby kontynuować.")
BRAK_CELU = "Wskaż miejsce instalacji."
CEL_WZGLEDNY = "Podaj pełną ścieżkę miejsca instalacji, np. C:\\Stanowisko."
CEL_SYNCHRONIZOWANY = "Miejsce instalacji leży w folderze synchronizowanym (OneDrive / SharePoint). Wybierz folder poza nim, np. C:\\Stanowisko."
CEL_SREDNIK = "Ścieżka miejsca instalacji nie może zawierać średnika (;). Wybierz inną, np. C:\\Stanowisko."
CEL_PLIK = "W miejscu instalacji jest plik, a nie folder: {sciezka}. Wybierz inny folder."
CEL_DYSK = "Nie ma takiego dysku: {sciezka}."
ZA_MALO_MIEJSCA = "Za mało miejsca na dysku: potrzeba {potrzeba}, wolne {wolne}. Zwolnij miejsce albo wybierz inny dysk."
BRAK_OSOB = "Dodaj co najmniej jedną osobę."
OSOBA_PUSTA = "Wpisz imię osoby."
OSOBA_POWTORZONA = "Osoba „{osoba}” jest już na liście."
OSOBA_ZA_DLUGA = "Imię może mieć najwyżej {n} znaków."
OSOBA_ZNAKI = "Imię zawiera niedozwolone znaki (znaki sterujące)."

# --- krok 3: instalacja -----------------------------------------------------------------------------------------------
INSTALACJA_TYTUL = "Instalacja"
INSTALACJA_TRWA = "Trwa instalacja — kilka minut. Nie zamykaj tego okna."
INSTALACJA_BLAD_TYTUL = "Instalacja się nie udała"
SZCZEGOLY = "Szczegóły"
# kroki instalatora ([1/9] ... [9/9] w wyjsciu ``instalator.py zainstaluj``)
KROKI_INSTALATORA = ("Sprawdzenie paczki", "Python", "Folder instalacji", "Ustawienia", "Program i pakiety (kilka minut)",
                     "Kopia bazy", "Samokontrola", "Przełączenie wersji", "Ikony na pulpicie")
STAN_GOTOWE = "gotowe"
STAN_TRWA = "trwa…"
STAN_BLAD = "błąd"
CO_ZROBIC = "Co zrobić: {rada}"
DZIENNIK = "Zapis instalacji: {plik}"
NIE_URUCHOMIONO = "Nie udało się uruchomić instalatora ({blad}). Sprawdź, czy rozpakowano całą paczkę, i spróbuj ponownie."
PRZERWANIE_PYTANIE = "Instalacja trwa. Przerwanie zostawi poprzednią wersję bez zmian. Przerwać?"

# Kod wyjscia instalatora -> zdanie dla czlowieka (kody: instalator.KOD_*; opisy_modulow/instalacja.md, tabela kodow)
ZDANIA_KODOW = {
    0: "Program jest zainstalowany i gotowy do pracy.",
    1: "Samokontrola nowej wersji znalazła błędy. Nowa wersja jest zainstalowana, ale nie została włączona — działa poprzednia.",
    2: "Nie udało się wykonać samokontroli nowej wersji. Nowa wersja nie została włączona — spróbuj ponownie.",
    3: "Paczka instalacyjna jest uszkodzona albo niekompletna. Rozpakuj ją jeszcze raz w całości i spróbuj ponownie.",
    4: "Brak Pythona potrzebnego do instalacji (paczka niekompletna). Rozpakuj paczkę jeszcze raz w całości.",
    5: "Program „Stanowisko” jest uruchomiony albo jego baza jest otwarta w innym programie. Zamknij go i spróbuj ponownie.",
    6: "Nie udało się zainstalować programu w wybranym folderze (miejsce na dysku, prawa zapisu albo przerwanie). Poprzednia wersja działa bez zmian.",
    7: "Plik ustawień ma błąd. Popraw go tak, jak opisano poniżej, i spróbuj ponownie.",
    8: "Powrót do poprzedniej wersji wymaga przywrócenia kopii bazy.",
    9: "Nie ma wersji, do której można wrócić.",
    10: "Program jest zainstalowany, ale ustawienia wymagają uzupełnienia (foldery albo osoby). Popraw je i uruchom instalację ponownie.",
    11: "Powrót anulowany — nic nie zmieniono.",
}
ZDANIE_NIEZNANEGO_KODU = "Instalacja zakończyła się nieoczekiwanym kodem {kod}. Przekaż plik dziennik_instalacji.txt z folderu instalacji."
ZDANIE_WYBORU = "Popraw wybór: {bledy}"  # tryb bez okna: blad walidacji (kod 12), nic nie zmieniono

# --- krok 4: gotowe ---------------------------------------------------------------------------------------------------
GOTOWE_TYTUL = "Gotowe"
GOTOWE_OPIS = "Program „Stanowisko” {wersja} jest zainstalowany w {katalog}."
IKONY_SA = "Na pulpicie są ikony: {ikony}."
IKONA_BRAK = ("Ikony „{nazwa}” nie dało się założyć na pulpicie (zasady tego komputera). Program uruchomisz plikiem {plik} "
              "w folderze instalacji (otwiera też małe okno konsoli — nie zamykaj go).")
RAMKI_WYLACZONE = "Ramki są wyłączone — program działa bez nich (rozkładanie według podpisów na ekranie)."
URUCHAMIAM = "Uruchamiam program…"
