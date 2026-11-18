"""statusy - JEDNA tabela statusow, kolorow i napisow dla technika (plan etapu 3: zalozenia Z8 i Z9; paczka E3-A3a).

Ekran (``ui/``), kontroler (``kontroler_api``, ``aplikacja``) i - pozniej - ramki (``indicate``, A8) biora stad kolory
i teksty; zadnych wlasnych stalych w kodzie ekranow. Nowy status (P2, B4) = nowy wiersz tutaj.

Trzy poziomy nazw:
* ``kolor`` - KLASA koloru pracy wg ``session`` (kontrakt A1, wspolny z ramka): ``zielony``, ``czerwony``, ``zolty``,
  ``szary``, ``pomaranczowy``, ``zatwierdzona_ok`` albo None (gniazdo bez koloru pracy: puste, zablokowane, nieaktywne);
* ``status`` - klucz ``STATUSY``: dokladniejszy stan do pokazania (np. ``nie_sprawdzono`` i ``popraw_ulozenie`` sa oba
  zolte, ale maja inne napisy); kazdy status nalezy do jednej klasy koloru;
* ``napis`` / ``opis`` - teksty dla technika (po polsku, ze znakami diakrytycznymi - jak w oknie testowym).

Z9 - slowo "poprawka" ma dwa znaczenia i dwa ROZNE napisy: ``pomaranczowy`` = praca poprawiana recznie (gladka zmiana
ksztaltu wzgledem projektu), ``dofrezowany`` = zab dofrezowany do zlecenia juz odhaczonego (bursztyn; pojawi sie rano, A6).
Nazwy do zatwierdzenia przez wlasciciela na bramce G1.

Modul uzywa tylko biblioteki standardowej (bez Qt): kolor ekranu to trojka RGB i napis ``#rrggbb``.
"""
from __future__ import annotations

import dataclasses

# klasy koloru pracy wg session.stan_wieczoru (pole ``kolor``)
KOLOR_ZIELONY = "zielony"
KOLOR_CZERWONY = "czerwony"
KOLOR_ZOLTY = "zolty"
KOLOR_SZARY = "szary"
KOLOR_POMARANCZOWY = "pomaranczowy"
KOLOR_ZATWIERDZONA_OK = "zatwierdzona_ok"
KOLOR_BURSZTYNOWY = "bursztynowy"  # rano (A6): zab dofrezowany do zlecenia juz odhaczonego
KOLORY_PRACY = (KOLOR_ZIELONY, KOLOR_CZERWONY, KOLOR_ZOLTY, KOLOR_SZARY, KOLOR_POMARANCZOWY, KOLOR_ZATWIERDZONA_OK)


@dataclasses.dataclass(frozen=True)
class Status:
    """Jeden wiersz tabeli: stan gniazda / pracy do pokazania na ekranie i na ramce."""

    klucz: str
    kolor: str | None  # klasa koloru (KOLORY_PRACY) albo None
    rgb: tuple[int, int, int]  # kolor na ekranie
    ramka: str | None  # kolor diod ramki pod gniazdem (A8): zielony / czerwony / zolty / bialy / bursztyn; None = nie swieci
    napis: str  # krotki podpis gniazda na mapie
    opis: str  # jedno zdanie dla technika (widok pracy, legenda)

    @property
    def hex(self) -> str:
        return "#%02x%02x%02x" % self.rgb


def _s(klucz: str, kolor: str | None, rgb: tuple[int, int, int], ramka: str | None, napis: str, opis: str) -> Status:
    return Status(klucz, kolor, rgb, ramka, napis, opis)


# Kolory zielony / zolty / szary / czerwony / pomaranczowy / pusty / podwojny / poza gniazdem = porownaj.KOLORY (okno testowe
# i mapa PNG z wiersza polecen); zgodnosc pilnuje test_aplikacja.
_WIERSZE = (
    _s("zielony", KOLOR_ZIELONY, (60, 180, 75), "zielony", "OK", "Praca rozpoznana, program nie widzi ubytku."),
    _s("czerwony", KOLOR_CZERWONY, (220, 50, 50), "czerwony", "UBYTEK",
       "Program widzi ubytek. Weź pracę do ręki, obejrzyj wskazane miejsce i wybierz „Ukruszona” albo „OK”."),
    _s("ukruszona", KOLOR_CZERWONY, (220, 50, 50), "czerwony", "UKRUSZONA", "Oznaczona jako ukruszona — jest na liście „do dofrezowania”."),
    _s("zatwierdzona_ok", KOLOR_ZATWIERDZONA_OK, (0, 150, 136), "zielony", "OK — zatwierdzona",
       "Technik obejrzał pracę i uznał ją za całą (fałszywy alarm programu)."),
    _s("zolty", KOLOR_ZOLTY, (240, 200, 40), "zolty", "sprawdź", "Program nie jest pewny. Obejrzyj pracę i wybierz „Ukruszona” albo „OK”."),
    _s("sprawdz_ulozenie", KOLOR_ZOLTY, (240, 200, 40), "zolty", "sprawdź ułożenie", "Praca może leżeć krzywo w gnieździe — obejrzyj ją."),
    _s("popraw_ulozenie", KOLOR_ZOLTY, (240, 200, 40), "zolty", "popraw ułożenie", "Popraw ułożenie pracy w gnieździe i zeskanuj płytkę ponownie."),
    _s("skan_ponownie", KOLOR_ZOLTY, (240, 200, 40), "zolty", "skan poruszony", "Skan tej pracy jest poruszony — zeskanuj płytkę ponownie."),
    _s("skan_do_powtorzenia", KOLOR_ZOLTY, (240, 200, 40), "zolty", "powtórz skan",
       "Ten skan trzeba powtórzyć — do tego czasu żadna praca na płytce nie jest potwierdzona."),
    _s("nie_sprawdzono", KOLOR_ZOLTY, (240, 200, 40), "zolty", "nie sprawdzono",
       "Program nie mógł sprawdzić brzegu tej pracy (brak danych na skanie) — obejrzyj ją sam."),
    _s("blad_inspekcji", KOLOR_ZOLTY, (214, 160, 0), "zolty", "błąd kontroli",
       "Kontrola tej pracy zakończyła się błędem programu — pracy nie sprawdzono, obejrzyj ją sam."),
    _s("szary", KOLOR_SZARY, (170, 170, 170), "bialy", "bez projektu", "Program nie znalazł projektu tej pracy w puli — sprawdź ręcznie."),
    # Z9: dwa znaczenia slowa "poprawka" - dwa rozne napisy
    _s("pomaranczowy", KOLOR_POMARANCZOWY, (245, 140, 30), "zolty", "poprawiana ręcznie",
       "Kształt pracy różni się gładko od projektu (ręczna poprawka) — obejrzyj ją."),
    _s("dofrezowany", KOLOR_BURSZTYNOWY, (255, 191, 0), "bursztyn", "ząb dofrezowany",
       "Ząb dofrezowany do zlecenia, które było już odhaczone."),
    # gniazda bez koloru pracy
    _s("pusty", None, (235, 235, 235), None, "", "Puste gniazdo."),
    _s("podwojny", None, (170, 80, 200), "zolty", "dwie prace", "W gnieździe leżą dwie prace — rozłóż je i zeskanuj płytkę ponownie."),
    _s("poza_gniazdem", None, (160, 0, 0), None, "poza gniazdem", "Praca leży poza gniazdem — włóż ją do gniazda i zeskanuj płytkę ponownie."),
    _s("czeka_na_numer", None, (176, 196, 222), None, "podaj nr płytki",
       "Program nie zna numeru tej płytki — podaj go, wtedy praca zostanie pokazana jako sprawdzona."),
    _s("plytka_nie_z_trybu", None, (120, 120, 140), None, "zablokowana", "Płytka nie z tego trybu — skan jest zablokowany."),
    _s("nieaktywny", None, (205, 205, 205), None, "skan nieaktualny", "Ten skan nie jest już liczony (zastąpiony albo odrzucony)."),
    _s("nieznany", KOLOR_ZOLTY, (240, 200, 40), "zolty", "sprawdź", "Nieznany status z analizy — obejrzyj pracę."),
)
STATUSY: dict[str, Status] = {w.klucz: w for w in _WIERSZE}

STATUSY_ZIELONE = tuple(k for k, w in STATUSY.items() if w.kolor == KOLOR_ZIELONY)  # tylko to wolno pokazac jako "sprawdzona, cala"
# status inspekcji (``prace.status_inspekcji``) -> dokladny status zoltego gniazda
ZOLTE_WG_INSPEKCJI = {"sprawdz": "zolty", "sprawdz_ulozenie": "sprawdz_ulozenie", "popraw_ulozenie": "popraw_ulozenie",
                      "skan_ponownie": "skan_ponownie", "nie_sprawdzono": "nie_sprawdzono"}
# P4 (recenzja PR #20): praca jest zielona TYLKO, gdy kolor z sesji jest zielony ORAZ inspekcja dala "ok" ORAZ dopasowanie ma
# znany status; kazdy inny albo nieznany status inspekcji / dopasowania = "do sprawdzenia" (zolty), nigdy zielony
INSPEKCJA_ZIELONA = "ok"
INSPEKCJE_NIESPRAWDZONE = (None, "pominieto", "nie_sprawdzono")  # inspekcji nie bylo, pominieta albo bez danych -> "nie sprawdzono"
DOPASOWANIA_ZIELONE = ("zielony", "zolty")  # match.STATUSY bez "szary": tylko przy takim dopasowaniu kolor moze byc zielony
STATUSY_SKANU_AKTYWNE = ("przyjety", "do_powtorzenia")  # jak session.STATUSY_AKTYWNE (modul bez importu session)
# klasa koloru z session -> status, gdy nic dokladniejszego nie wiadomo
STATUS_WG_KOLORU = {KOLOR_ZIELONY: "zielony", KOLOR_CZERWONY: "czerwony", KOLOR_ZOLTY: "zolty", KOLOR_SZARY: "szary",
                    KOLOR_POMARANCZOWY: "pomaranczowy", KOLOR_ZATWIERDZONA_OK: "zatwierdzona_ok"}
DECYZJE_UKRUSZENIA = ("ukruszona", "ukruszona_niewykryta")

# Plytka bez numeru (dolki kodu poza polem skanu): prace zielone NIE sa pokazywane jako zielone, dopoki technik nie poda
# numeru (plan 4.1 E3-A3 kryterium 4: "brak numeru plytki = komunikat ..., nic zielonego"). Do potwierdzenia przez wlasciciela.
ZIELONE_BEZ_NUMERU_PLYTKI = False


def status(klucz: str | None) -> Status:
    """Wiersz tabeli; klucz nieznany tej wersji programu (nowy status z analizy) = zolty "sprawdz", nigdy blad i nigdy zielony."""
    return STATUSY.get(klucz or "", STATUSY["nieznany"])


def status_pracy(kolor: str | None, *, status_skanu: str, status_gniazda: str | None = None, status_inspekcji: str | None = None,
                 decyzja: str | None = None, blad_inspekcji: bool = False, numer_znany: bool = True, status_match: str | None = None) -> str:
    """Klucz ``STATUSY`` dla jednej pracy.

    ``kolor`` - pole ``kolor`` pracy z ``session.stan_wieczoru`` (stan PO decyzjach technika; None dla skanu nieaktywnego),
    ``status_skanu`` - status skanu z bazy, ``status_gniazda`` - ocena programu, ``decyzja`` - obowiazujaca decyzja,
    ``status_match`` - status dopasowania (None = nie sprawdzac; kontroler podaje zawsze).

    P4: status zielony TYLKO przy kolorze zielonym, ``status_inspekcji == "ok"`` i znanym dopasowaniu (``DOPASOWANIA_ZIELONE``);
    inspekcji brak / pominieta -> ``nie_sprawdzono``, status inspekcji albo dopasowania nieznany tej wersji -> ``nieznany``
    (oba zolte). D3: skan aktywny bez koloru pracy (wynik bez pola) -> ``nieznany``, nie "skan nieaktualny". Nigdy wyjatek.
    """
    if status_skanu == "plytka_nie_z_trybu":
        return "plytka_nie_z_trybu"
    if kolor is None:
        return "nieznany" if status_skanu in STATUSY_SKANU_AKTYWNE else "nieaktywny"
    if decyzja in DECYZJE_UKRUSZENIA:
        return "ukruszona"
    if kolor == KOLOR_ZATWIERDZONA_OK:
        return "zatwierdzona_ok"
    if kolor == KOLOR_ZIELONY:
        if status_inspekcji != INSPEKCJA_ZIELONA:
            if status_inspekcji == "nie_sprawdzono" and blad_inspekcji:
                return "blad_inspekcji"
            return "nie_sprawdzono" if status_inspekcji in INSPEKCJE_NIESPRAWDZONE else "nieznany"
        if status_match is not None and status_match not in DOPASOWANIA_ZIELONE:
            return "nieznany"
        return "zielony" if numer_znany or ZIELONE_BEZ_NUMERU_PLYTKI else "czeka_na_numer"
    if kolor == KOLOR_ZOLTY:
        if status_inspekcji == "nie_sprawdzono":
            return "blad_inspekcji" if blad_inspekcji else "nie_sprawdzono"
        if status_inspekcji in ZOLTE_WG_INSPEKCJI and ZOLTE_WG_INSPEKCJI[status_inspekcji] != "zolty":
            return ZOLTE_WG_INSPEKCJI[status_inspekcji]
        if status_skanu == "do_powtorzenia" and status_gniazda == KOLOR_ZIELONY:
            return "skan_do_powtorzenia"
        return "zolty"
    return STATUS_WG_KOLORU.get(kolor, "nieznany")


def kolor_pracy(kolor: str | None, klucz: str) -> str | None:
    """Klasa koloru pracy do pokazania (``Praca.kolor``, liczniki) dla statusu ``klucz`` z ``status_pracy``: zielona TYLKO dla
    statusu z ``STATUSY_ZIELONE`` (P4 - zielony z sesji przy innym statusie dostaje klase koloru tego statusu, czyli zolta);
    ``czeka_na_numer`` - brak koloru (plytka bez numeru: nic zielonego); klasa nieznana tej wersji albo brak koloru przy
    statusie ``nieznany`` - zolta."""
    if klucz == "czeka_na_numer":
        return None
    wiersz = status(klucz)
    if kolor == KOLOR_ZIELONY and klucz not in STATUSY_ZIELONE:
        return wiersz.kolor
    if klucz == "nieznany" and (kolor is None or kolor not in KOLORY_PRACY):
        return wiersz.kolor
    return kolor


# --- statusy skanu (plytki) ------------------------------------------------------------------------------------------
STATUSY_PLYTKI = {
    "przyjety": "przeanalizowana",
    "do_powtorzenia": "do ponownego skanu",
    "zastapiony": "zastąpiona nowszym skanem",
    "niezgodny_uklad": "nie pasuje do żadnego układu płytek",
    "plytka_nie_z_trybu": "zablokowana (płytka nie z tego trybu)",
    "blad": "analiza nie powiodła się",
}


def napis_plytki(status_skanu: str) -> str:
    return STATUSY_PLYTKI.get(status_skanu, status_skanu)


# --- przyciski (polecenie okna -> napis) --------------------------------------------------------------------------------
PRZYCISKI = {
    "ukruszona": "Ukruszona",
    "ok": "OK",
    "cofnij": "Cofnij decyzję",
    "potwierdz_ponowny_skan": "Tak, to ponowny skan",
    "odrzuc_ponowny_skan": "Nie, to nowy wsad",
    "cofnij_zastapienie": "Cofnij zastąpienie",
    "dopusc_plytke": "Dopuść tę płytkę",
    "cofnij_dopuszczenie": "Cofnij dopuszczenie",
    "podaj_numer_plytki": "Podaj numer płytki",
    "zamknij_pytanie": "Później",
    "zamknij_komunikat": "Zamknij",
    "start_skanu": "Skanuj (Spacja)",
    "odswiez_pule": "Odśwież pulę",
    "wybierz_operatora": "Wybierz osobę",
    "zamknij": "Zamknij program",
    "zapisz_liste": "Zapisz listę do pliku",
    "ponow_zapis": "Ponów zapis",
}
PRZYCISK_ZESKANUJE_WLASCIWA = "Zeskanuję właściwą płytkę"  # odpowiedz "nie dopuszczam" na pytanie o plytke nie z trybu
PRZYCISK_WYLOGUJ = "Odchodzę od stanowiska"  # wybierz_operatora(None): nikt nie jest wybrany, decyzje niedostepne (D7)


def odmiana(n: int, jedna: str, dwie: str, piec: str) -> str:
    """Polska odmiana rzeczownika po liczbie: 1 decyzja, 2 decyzje, 5 decyzji, 22 decyzje."""
    n = abs(int(n))
    if n == 1:
        return jedna
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return dwie
    return piec


# --- komunikaty i pytania do technika ---------------------------------------------------------------------------------
POZIOM_INFO, POZIOM_OSTRZEZENIE, POZIOM_BLAD = "info", "ostrzezenie", "blad"


@dataclasses.dataclass(frozen=True)
class Wzor:
    """Wzor komunikatu albo pytania: ``tekst`` z polami ``{...}`` wypelnianymi przez kontroler (same liczby i numery -
    nigdy nazwy plikow ani folderow zlecen)."""

    poziom: str
    tytul: str
    tekst: str


KOMUNIKATY: dict[str, Wzor] = {
    # skan / plytka
    "niezgodny_uklad": Wzor(POZIOM_BLAD, "Płytka nie pasuje do układu",
                            "Program nie rozpoznał układu płytki na tym skanie — nic nie zostało sprawdzone. Sprawdź, czy płytka leży "
                            "w skanerze prosto i w całości, i zeskanuj ją ponownie."),
    "skan_do_powtorzenia": Wzor(POZIOM_OSTRZEZENIE, "Skan do powtórzenia",
                                "Zeskanuj płytkę ponownie: {powody}. Do tego czasu żadna praca na tej płytce nie jest potwierdzona."),
    "blad_inspekcji": Wzor(POZIOM_OSTRZEZENIE, "Praca niesprawdzona",
                           "Gniazdo {nr}: kontrola zakończyła się błędem programu — pracy nie sprawdzono. Obejrzyj ją sam."),
    "blad_analizy": Wzor(POZIOM_BLAD, "Analiza skanu nie powiodła się",
                         "Program nie przeanalizował tego skanu ({powod}). Zeskanuj płytkę ponownie."),
    "plik_zajety": Wzor(POZIOM_INFO, "Czeka na zwolnienie pliku",
                        "Plik skanu jest jeszcze zajęty przez inny program (od {od_s} s) — analiza ruszy sama, gdy plik zostanie zwolniony."),
    "plik_niedostepny": Wzor(POZIOM_BLAD, "Nie można odczytać pliku skanu",
                             "Pliku skanu nie udało się odczytać — inny program trzyma go zamkniętego. {dalej}"),
    "plik_zmieniony": Wzor(POZIOM_INFO, "Skan zapisany ponownie",
                           "Plik skanu został zapisany jeszcze raz, zanim ruszyła analiza — program analizuje nową wersję."),
    "plik_odrzucony": Wzor(POZIOM_OSTRZEZENIE, "Plik nie jest skanem",
                           "W folderze skanera pojawił się plik, którego program nie przyjął ({powod})."),
    "skan_juz_jest": Wzor(POZIOM_INFO, "Ten skan już jest w programie",
                          "Skaner zapisał ten sam skan drugi raz — program nie liczy go ponownie."),
    "silnik_nie_startuje": Wzor(POZIOM_BLAD, "Analiza nie działa",
                                "Program nie może uruchomić analizy. Skany nie przepadną — zamknij program i uruchom go ponownie; "
                                "jeśli to nie pomoże, zgłoś awarię."),
    "folder_skanera_niedostepny": Wzor(POZIOM_BLAD, "Brak folderu skanera",
                                       "Program nie widzi folderu, do którego zapisuje skaner. Sprawdź dysk i ustawienia."),
    # pula projektow
    "pula_pusta": Wzor(POZIOM_BLAD, "Brak projektów w puli",
                       "W folderze projektów nie ma plików projektów — skany czekają ({czeka}). Sprawdź, czy pliki projektów są w folderze "
                       "projektów, i kliknij „Odśwież pulę”. Jeśli folder jest inny — zgłoś to."),
    "pula_brak_folderu": Wzor(POZIOM_BLAD, "Brak folderu projektów",
                              "Program nie widzi folderu projektów — skany czekają ({czeka}). Sprawdź, czy dysk z folderem "
                              "projektów jest podłączony, i kliknij „Odśwież pulę”. Jeśli folder jest inny — zgłoś to."),
    "zly_wspolczynnik": Wzor(POZIOM_OSTRZEZENIE, "Zły współczynnik skurczu",
                             "Współczynnik skurczu musi być liczbą od {od} do {do} (zostaw puste pole, żeby program dobrał go sam)."),
    # operator i odmowy
    "brak_operatora": Wzor(POZIOM_OSTRZEZENIE, "Wybierz osobę",
                           "Nie wybrano osoby, która pracuje — wybierz ją z listy. Bez tego nie można zapisywać decyzji."),
    "pusta_lista_operatorow": Wzor(POZIOM_BLAD, "Brak listy osób",
                                   "Lista osób jest pusta — nie można zapisywać decyzji. Poproś o dopisanie osób w ustawieniach programu."),
    "osoba_spoza_listy": Wzor(POZIOM_OSTRZEZENIE, "Nie ma takiej osoby", "Wybranej osoby nie ma na liście."),
    "nowa_zmiana": Wzor(POZIOM_INFO, "Nowa zmiana", "Zaczęła się zmiana {zmiana} — wybierz osobę, która teraz pracuje."),
    "odmowa": Wzor(POZIOM_OSTRZEZENIE, "Nie można tego zrobić", "{powod}"),
    "baza_zajeta": Wzor(POZIOM_BLAD, "Baza jest zajęta", "Inny program trzyma bazę stanowiska — niczego nie zapisano. Spróbuj ponownie za chwilę."),
    "program_zamkniety": Wzor(POZIOM_INFO, "Program się zamyka", "Program się zamyka — polecenie nie zostało wykonane."),
    "start_skanu_nieudany": Wzor(POZIOM_OSTRZEZENIE, "Skaner nie odpowiedział",
                                 "Nie udało się uruchomić skanu z programu — naciśnij Spację w programie skanera."),
    "wznowiono": Wzor(POZIOM_INFO, "Program wznowił pracę",
                      "Po ponownym uruchomieniu program dokańcza zaległe skany: {ile}."),
    "konflikt_projektu": Wzor(POZIOM_OSTRZEZENIE, "Ten sam projekt w dwóch gniazdach",
                              "Ten sam projekt pasuje do {miejsc} prac — sprawdź, która praca jest która."),
    # runda 2 recenzji PR #20 (zmiany kontraktu addytywne)
    "blad_zapisu": Wzor(POZIOM_BLAD, "Nie można zapisać wyniku skanu",
                        "Program nie mógł zapisać wyników skanów ({ile}) — sprawdź dysk (wolne miejsce, podłączenie dysku). "
                        "Skany nie przepadną: program ponawia zapis sam, możesz też kliknąć „Ponów zapis”."),
    "zle_argumenty": Wzor(POZIOM_OSTRZEZENIE, "Nie można tego zrobić",
                          "Błąd programu — nic nie zostało zapisane. Zgłoś to (polecenie „{polecenie}”)."),
    "blad_polecenia": Wzor(POZIOM_BLAD, "Polecenie nie zostało wykonane",
                           "Błąd programu albo dysku — nic nie zostało zapisane. Spróbuj ponownie; jeśli to się powtarza, zgłoś awarię."),
    "lista_nie_zapisana": Wzor(POZIOM_OSTRZEZENIE, "Lista nie została zapisana do pliku",
                               "Nie udało się zapisać listy „do dofrezowania” do pliku — sprawdź dysk. Lista na ekranie jest aktualna; "
                               "program spróbuje ponownie przy następnej zmianie listy (albo kliknij „Zapisz listę do pliku”)."),
    "lista_zapisana": Wzor(POZIOM_INFO, "Lista zapisana", "Lista „do dofrezowania” zapisana do pliku {plik} w folderze danych programu."),
    "wylogowano": Wzor(POZIOM_INFO, "Nikt nie jest wybrany", "Osoba odeszła od stanowiska — wybierz osobę, żeby zapisywać decyzje."),
}
# napis pozycji "nie zapisano" (``StanAplikacji.niezapisane``) wg przyczyny
NAPISY_NIEZAPISANE = {"blad_zapisu": "nie zapisano — błąd zapisu", "baza_zajeta": "nie zapisano — baza zajęta"}

PYTANIA: dict[str, Wzor] = {
    "ponowny_skan": Wzor(POZIOM_OSTRZEZENIE, "Ponowny skan tej samej płytki?",
                         "Płytka nr {numer} była skanowana {minut} min temu. Czy to ponowny skan tych samych prac? {skutek}"),
    "plytka_nie_z_trybu": Wzor(POZIOM_BLAD, "Płytka nie z tego trybu",
                               "To {jaka}, a program pracuje w trybie „{tryb}”. Skan jest zablokowany: nic nie jest zielone "
                               "i nie można zapisywać decyzji."),
    "brak_numeru_plytki": Wzor(POZIOM_OSTRZEZENIE, "Podaj numer płytki",
                               "Program nie odczytał numeru płytki ze skanu. Podaj numer wybity na płytce — do tego czasu "
                               "żadna praca na niej nie jest pokazana jako zielona."),
}
PLIK_NIEDOSTEPNY_PONOWIENIE = "Program próbuje ponownie (próba {proba} z {prob})."
PLIK_NIEDOSTEPNY_KONIEC = "Zamknij podgląd w programie skanera i zeskanuj płytkę ponownie."
SKUTEK_BEZ_DECYZJI = "Poprzedni skan nie ma jeszcze żadnych decyzji."
SKUTEK_Z_DECYZJAMI = ("Po potwierdzeniu przestanie obowiązywać {n} {decyzji} z poprzedniego skanu (w tym „Ukruszona”: {u}) — "
                      "trzeba je będzie zaznaczyć od nowa.")
JAKA_PLYTKA = {"wieczorna": "płytka wieczorna", "poranna": "płytka poranna", None: "płytka o nieznanym układzie"}
NAZWY_TRYBOW = {"wieczor": "Wieczór", "rano": "Poranek"}
POWODY_POWTORZENIA = {
    "skan_ponownie": "skan jest poruszony (gniazdo {gniazda})",
    "popraw_ulozenie": "popraw ułożenie pracy (gniazdo {gniazda})",
    "podwojny": "dwie prace w jednym gnieździe (gniazdo {gniazda})",
    "poza_gniazdem": "praca leży poza gniazdem ({ile})",
}
POWODY_BLEDU_ANALIZY = {
    "analiza": "błąd analizy",
    "proces": "analiza została przerwana",
    "limit_czasu": "analiza trwała za długo",
    "start": "analiza nie wystartowała",
    "plik_niedostepny": "pliku nie dało się odczytać",
    "plik_zmieniony": "plik zmienił się przed analizą",
}
POWODY_ODRZUCENIA = {
    "pusty": "plik pusty",
    "za_krotki": "plik ucięty",
    "rozmiar_niezgodny": "plik ucięty albo uszkodzony",
    "stl_tekstowy": "STL tekstowy zamiast binarnego",
    "za_malo_trojkatow": "za mało trójkątów",
    "za_maly": "plik za mały",
    "poza_wzorcem": "to nie jest plik skanu",
}
ZAB_JUZ_NA_LISCIE = "Ten ząb jest już na liście „do dofrezowania” (skan z {doba}, zmiana {zmiana})."
STANY_PULI = {
    "nieustawiona": "nie wskazano folderu projektów",
    "liczenie": "liczę pliki projektów…",
    "gotowa": "plików projektów: {n}",
    "pusta": "brak plików projektów",
    "brak_folderu": "brak folderu projektów",
}


def tekst_komunikatu(rodzaj: str, **pola) -> tuple[str, str, str]:
    """(poziom, tytul, tekst) komunikatu ``rodzaj`` z wypelnionymi polami; nieznany rodzaj = komunikat ogolny (bez wyjatku)."""
    w = KOMUNIKATY.get(rodzaj) or Wzor(POZIOM_OSTRZEZENIE, "Uwaga", "{powod}")
    return w.poziom, w.tytul, _wypelnij(w.tekst, pola)


def tekst_pytania(rodzaj: str, **pola) -> tuple[str, str, str]:
    w = PYTANIA[rodzaj]
    return w.poziom, w.tytul, _wypelnij(w.tekst, pola)


class _Braki(dict):
    def __missing__(self, klucz: str) -> str:
        return "?"


def _wypelnij(tekst: str, pola: dict) -> str:
    return tekst.format_map(_Braki(pola))
