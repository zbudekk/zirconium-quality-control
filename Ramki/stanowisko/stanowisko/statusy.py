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
KOLOR_BIALY = "bialy"  # rano (A6 / E3-A7): praca nieznana - przymiarka na modelach albo przypisanie reczne
KOLORY_PRACY =(KOLOR_ZIELONY, KOLOR_CZERWONY, KOLOR_ZOLTY, KOLOR_SZARY, KOLOR_POMARANCZOWY, KOLOR_ZATWIERDZONA_OK)


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
    # rano (E3-A7, uwaga A6; klucz wg koordynatora): praca nieznana - na ekranie i na ramce biala
    _s("nieznana_rano", KOLOR_BIALY, (250, 250, 250), "bialy", "nieznana",
       "Program nie rozpoznał tej pracy — przymierz ją na modelach albo przypisz ręcznie do projektu."),
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

# --- poranek (E3-A7): klasa pracy porannej z ``session_rano`` -> wiersz tabeli ------------------------------------------
# Rano zielone znaczy "praca rozpoznana, kuweta znana" (nie "sprawdzona, cala" jak wieczorem), dlatego wiersze poranne sa
# osobne (klucze ``rano_*``) i NIE wchodza do ``STATUSY_ZIELONE``; kolor ekranu i diod = wiersz, ktory podaje ``session_rano``
# (``STATUS_KLASY``: zielony / zolty / czerwony; zgodnosc pilnuje test_kontroler_api). Praca nieznana = wiersz ``nieznana_rano``,
# poprawka = ``dofrezowany`` (Z9) albo - gdy zlecenie wciaz ma braki (A6 runda 2, D2) - ``rano_juz_rozpoznany`` (ten sam bursztyn,
# inny napis), skan do powtorzenia = ``skan_do_powtorzenia``.
_WIERSZE_RANO = (
    _s("rano_pewna", KOLOR_ZIELONY, (60, 180, 75), "zielony", "rozpoznana", "Praca rozpoznana — pod gniazdem jej kuweta i ząb."),
    _s("rano_przypisana", KOLOR_ZIELONY, (60, 180, 75), "zielony", "przypisana",
       "Praca przypisana decyzją osoby (wybór kandydata albo przypisanie ręczne)."),
    _s("rano_dwuznaczna", KOLOR_ZOLTY, (240, 200, 40), "zolty", "wybierz",
       "Program waha się między dwoma projektami — kliknij gniazdo i wybierz właściwy projekt."),
    _s("rano_konflikt", KOLOR_CZERWONY, (220, 50, 50), "czerwony", "konflikt",
       "Ten sam projekt pasuje do dwóch prac — dla jednej z nich wybierz inny projekt albo „bez projektu”. "
       "Do tego czasu „Zamknij piec” jest zablokowane."),
    _s("rano_juz_rozpoznany", KOLOR_BURSZTYNOWY, (255, 191, 0), "bursztyn", "ząb już rozpoznany",
       "Ten ząb wyszedł już z wcześniejszego pieca, a zlecenie wciąż ma braki — sprawdź, czy to nie pomyłka (tylko wpis w logu)."),
)
STATUSY_RANO_WIERSZE: dict[str, Status] = {w.klucz: w for w in _WIERSZE_RANO}
STATUSY_RANO: dict[str, Status] = {  # klasa pracy porannej (session_rano.KLASA_*) -> wiersz
    "pewna": STATUSY_RANO_WIERSZE["rano_pewna"], "przypisana": STATUSY_RANO_WIERSZE["rano_przypisana"],
    "dwuznaczna": STATUSY_RANO_WIERSZE["rano_dwuznaczna"], "nieznana": STATUSY["nieznana_rano"], "poprawka": STATUSY["dofrezowany"],
    "konflikt": STATUSY_RANO_WIERSZE["rano_konflikt"], "do_powtorzenia": STATUSY["skan_do_powtorzenia"]}
KLASY_RANO_Z_KUWETA = ("pewna", "przypisana", "poprawka", "konflikt")  # podpis gniazda rano = numer kuwety

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
    """Wiersz tabeli (takze poranny ``rano_*``); klucz nieznany tej wersji programu (nowy status z analizy) = zolty "sprawdz",
    nigdy blad i nigdy zielony."""
    return STATUSY.get(klucz or "") or STATUSY_RANO_WIERSZE.get(klucz or "") or STATUSY["nieznany"]


def status_rano(klasa: str | None) -> Status:
    """Wiersz dla klasy pracy porannej (``session_rano``: pewna / przypisana / dwuznaczna / nieznana / poprawka / konflikt /
    do_powtorzenia). Klasa nieznana tej wersji programu = zolty "sprawdz" (nigdy zielony)."""
    return STATUSY_RANO.get(klasa or "", STATUSY["nieznany"])


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
    "ponow_polecenie": "Ponów teraz",  # E3-P14 (N1): ponowienie polecenia odrzuconego przy zajetej bazie
    # poranek (E3-A7)
    "przelacz_tryb": "Przełącz tryb",
    "wybierz_kandydata": "To ten projekt",
    "przypisz_recznie": "Przypisz ręcznie",
    "cofnij_przypisanie": "Cofnij wybór",
    "zamknij_piec": "Zamknij piec",
    "ustaw_kolejnosc": "Kolejność kuwet",
    "wybierz_kuwete": "Wybierz kuwetę",
    "potwierdz_kuwete": "Rozłożona",
    "cofnij_kuwete": "Cofnij",
    # poranek - runda 2 sesji porannej (A6)
    "pomin_skan": "Pomiń skan",
    "cofnij_pominiecie": "Cofnij pominięcie",
    "zamknij_brak_recznie": "Zamknij brak ręcznie",
    "cofnij_zamkniecie_reczne": "Cofnij zamknięcie ręczne",
    "otworz_piec_ponownie": "Otwórz piec ponownie",
    # poranek - runda 4 sesji porannej (A6): zapomniany "Zamknij piec"
    "zamknij_piec_i_przenies": "Tak, zamknij piec i przenieś nowe skany",
    "cofnij_przeniesienie": "Cofnij przeniesienie",
    # E3-P14 runda 2 (D3): wybor krazka pracy (pula per praca) - nazwa polecenia w komunikacie "decyzja NIE zostala zapisana";
    # brzmienie jak napisy ekranu ``ui.napisy.KRAZEK_*`` (bez polskich znakow - poz. 5 recenzji, do zmiany razem z nimi)
    "wybierz_wpis": "Wybor krazka",
    "cofnij_wpis": "Cofnij wybor krazka",
}
# E3-P14 (N1): komunikat "decyzja NIE zostala zapisana" - zamiast "Zamknij" (zamkniecie = swiadoma rezygnacja z tej decyzji)
PRZYCISK_REZYGNUJE = "Rezygnuję — nie zapisuj"
KOMUNIKATY_DO_PONOWIENIA = ("decyzja_niezapisana", "polecenie_niezapisane")
# opis polecenia w tych komunikatach (pole ``co``): „Ukruszona” — płytka 1, gniazdo 2 / „Rozłożona” — kuweta 3221 / „Zamknij piec”
POLECENIE_NAZWA = "„{napis}”"
POLECENIE_Z_MIEJSCEM = "„{napis}” — {miejsce}"
MIEJSCE_GNIAZDO = "{plytka}, gniazdo {gniazdo}"
MIEJSCE_POZA_GNIAZDEM = "{plytka}, praca poza gniazdem"
MIEJSCE_KUWETA = "kuweta {kuweta}"
NAPIS_NIC_DO_PONOWIENIA = "Tego polecenia nie ma już na liście do ponowienia (zostało zapisane albo z niego zrezygnowano)."
PRZYCISK_NUMER_MIMO = "Zmień numer na {numer} mimo to"  # A6 runda 4: zmiana numeru plytki przy nowym wsadzie - tylko swiadomie
PRZYCISK_NUMER_BEZ_ZMIANY = "Nie zmieniaj"
ZLECENIA_ODMIANA = ("zlecenie", "zlecenia", "zleceń")
I_INNYCH = " i {n} innych"
# powod recznego zamkniecia braku (kody ``session_rano.POWODY_ZAMKNIECIA``) -> napis przycisku
POWODY_ZAMKNIECIA = {"nie_praca_z_cyrkonu": "to nie praca z cyrkonu", "zaginiona": "praca zaginęła", "wydana_bez_skanu": "wydana bez skanu",
                     "inny": "inny powód", "nie_bedzie_dofrezowany": "nie będzie dofrezowany"}
POWOD_DOFREZOWANIE = "nie_bedzie_dofrezowany"  # = session_rano.POWOD_DOFREZOWANIE: jedyny powod dla punktu do_dofrezowania (A6 runda 3)


def powody_zamkniecia(stan_punktu: str | None) -> dict:
    """Powody recznego zamkniecia dozwolone dla punktu w stanie ``stan_punktu`` (A6 runda 3): zab do dofrezowania zamyka tylko
    "nie bedzie dofrezowany", inny punkt - kazdy powod poza nim."""
    if stan_punktu == "do_dofrezowania":
        return {POWOD_DOFREZOWANIE: POWODY_ZAMKNIECIA[POWOD_DOFREZOWANIE]}
    return {k: v for k, v in POWODY_ZAMKNIECIA.items() if k != POWOD_DOFREZOWANIE}
NAPIS_POMINIETEJ = "pominięta (nie liczy się)"  # skan poranny pominiety przez osobe (A6 runda 2)
PRZYCISK_BEZ_PROJEKTU = "Bez projektu"  # przypisz_recznie(praca, None): praca nieznana (przymiarka na modelach), rozstrzygniecie konfliktu
NAZWY_KOLEJNOSCI = {"liczba": "Od najliczniejszej", "numer": "Według numeru"}  # U7 (trzeci sposob: numer wpisany recznie)
# stan punktu zlecenia (``stan_punktow.stan``) na liscie brakow
STANY_PUNKTU = {"oczekuje": "czeka", "do_dofrezowania": "dofrezowywany (ukruszony wieczorem)", "brak_po_piecu": "nie wyszedł z pieca",
                "rozpoznany": "rozpoznany", "zamkniety_recznie": "zamknięty ręcznie"}
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
    # E3-A5i runda 2 (P4): pula per praca - przyczyna pustej puli i krazki bez wspolczynnika (nazwy krazkow, bez nazw zlecen)
    "pula_wpisow_pusta": Wzor(POZIOM_BLAD, "Brak wpisow puli dnia",
                              "Pula dnia nie ma zadnego projektu ze wspolczynnikiem - skany czekaja ({czeka}). Przyczyna: {przyczyna}. "
                              "Popraw plik wspolczynnikow (albo katalog zlecen) i kliknij \u201eOdswiez pule\u201d."),
    "pula_wpisow_brak": Wzor(POZIOM_BLAD, "Katalog zlecen niedostepny",
                             "Program nie odswiezyl katalogu zlecen - skany czekaja ({czeka}). Przyczyna: {przyczyna}. Sprawdz, czy foldery "
                             "zlecen i plik wspolczynnikow sa dostepne, i kliknij \u201eOdswiez pule\u201d."),
    "pula_plytki_pusta": Wzor(POZIOM_OSTRZEZENIE, "Plytka bez swojej puli",
                              "To plytka {typ}, a pula trybu {tryb} jest pusta - prace dopasowano do puli biezacego trybu (inne "
                              "wspolczynniki), wiec sa szare albo niepewne. Kliknij \u201eOdswiez pule\u201d i zeskanuj plytke ponownie."),
    "pula_wpisow_krazki": Wzor(POZIOM_OSTRZEZENIE, "Prace bez wspolczynnika w puli",
                               "{przyczyna}. Prace z tych krazkow nie maja projektu w puli (beda szare), dopoki krazek nie ma jednej "
                               "wartosci w pliku wspolczynnikow (albo potwierdzonego wpisu recznego)."),
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
    # E3-P14 (N1): polecenie technika odrzucone, bo baza byla zajeta - komunikat TRWALY z przyciskiem "Ponów teraz" (ponawia
    # dokladnie to polecenie); znika po udanym zapisie albo po "Rezygnuję". ``co`` - nazwa polecenia i miejsce (plytka, gniazdo)
    "decyzja_niezapisana": Wzor(POZIOM_BLAD, "Decyzja NIE została zapisana",
                                "{co} — decyzja NIE jest zapisana: baza stanowiska była zajęta przez inny program. Kliknij "
                                "„Ponów teraz”; jeśli znowu się nie uda, odczekaj chwilę i kliknij jeszcze raz. Dopóki widzisz ten "
                                "komunikat, tej decyzji nie ma w programie."),
    "polecenie_niezapisane": Wzor(POZIOM_BLAD, "Polecenie NIE zostało wykonane — baza zajęta",
                                  "{co} — NIE wykonano i niczego nie zapisano: baza stanowiska była zajęta przez inny program. Kliknij "
                                  "„Ponów teraz”; jeśli znowu się nie uda, odczekaj chwilę i kliknij jeszcze raz."),
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
    # poranek (E3-A7): ramka i Excel jeszcze niepodlaczone (A12) - program dziala dalej wedlug ekranu
    "ramka_niedostepna": Wzor(POZIOM_INFO, "Ramka poranna nie jest podłączona",
                              "Program działa bez ramki — rozkładaj prace według ekranu: kuweta po kuwecie (Enter = rozłożona, "
                              "Backspace = cofnij, cyfry i Enter = wybór kuwety)."),
    "excel_niedostepny": Wzor(POZIOM_OSTRZEZENIE, "Excel nie jest podłączony",
                              "Program nie zapisuje jeszcze do Excela — odhacz w Excelu zlecenia kompletne pieca nr {nr} z {doba} "
                              "(zamknięty {godzina}; {ile}): {kuwety}. Lista jest też w zakładce „Ostatni zamknięty piec”."),
    "kuweta_spoza_pieca": Wzor(POZIOM_OSTRZEZENIE, "Nie ma takiej kuwety w piecu", "Kuwety {kuweta} nie ma na płytkach tego pieca."),
    "kuwety_rozlozone": Wzor(POZIOM_INFO, "Wszystko rozłożone", "Wszystkie kuwety tego pieca są już rozłożone."),
    "brak_kuwety_do_cofniecia": Wzor(POZIOM_INFO, "Nic do cofnięcia", "Nie ma rozłożonej kuwety do cofnięcia."),
    "brak_pieca": Wzor(POZIOM_OSTRZEZENIE, "Nie ma otwartego pieca",
                       "Nie ma otwartego pieca — piec otwiera pierwszy skan płytki porannej."),
    "analiza_trwa": Wzor(POZIOM_INFO, "Trwa analiza skanu",
                         "Trwa analiza skanu płytki — poczekaj na wynik, potem zamknij piec (wynik po zamknięciu otworzyłby nowy piec)."),
    "skanowanie_trwa": Wzor(POZIOM_INFO, "Trwa skanowanie",
                            "Trwa skanowanie płytki — poczekaj, aż skan trafi do programu, potem zamknij piec (skan po zamknięciu "
                            "otworzyłby nowy piec)."),
    "kuweta_zmienila_sie": Wzor(POZIOM_OSTRZEZENIE, "Bieżąca kuweta jest inna",
                                "Bieżąca kuweta to teraz {kuweta}, a nie {podana} — sprawdź ekran; nic nie zapisano."),
    "rano_niedostepny": Wzor(POZIOM_BLAD, "Stanu pieca nie da się odczytać",
                             "Część poranna ekranu pokazuje ostatni odczytany stan. Spróbuj ponownie za chwilę; jeśli to się powtarza, "
                             "zgłoś awarię."),
    # ramki i Excel w programie (E3-A12; recenzja PR #30 D4 - teksty ostateczne tutaj, nie w kontrolerze)
    "ramka_wieczorna_niedostepna": Wzor(POZIOM_INFO, "Ramka wieczorna nie odpowiada",
                                        "Program działa bez ramki — wynik płytki pokazuje ekran. Sprawdź zasilanie ramki i sieć "
                                        "stanowiska; ramka dołączy sama."),
    "ramka_blad": Wzor(POZIOM_OSTRZEZENIE, "Ramka {ramka}: problem", "{powod}"),
    "ramka_plan_blad": Wzor(POZIOM_OSTRZEZENIE, "Ramka poranna zgaszona",
                            "Planu pieca nie udało się przygotować ({powod}) — ramka jest zgaszona, program ponawia sam. Do tego czasu "
                            "rozkładaj według ekranu."),
    "ramka_piec_zamkniety": Wzor(POZIOM_INFO, "Piec zamknięty klawiszem ramki",
                                 "Piec nr {nr} zamknięty klawiszem „Zamknij piec” na ramce porannej."),
    "ramka_zamknij_odmowa": Wzor(POZIOM_OSTRZEZENIE, "Ramka: „Zamknij piec” nie wykonane",
                                 "{powod} Piec jest nadal otwarty — zamknij go przyciskiem na ekranie, gdy będzie można."),
    "ramka_zamknij_nieaktualne": Wzor(POZIOM_INFO, "Ramka: stare „Zamknij piec”",
                                      "Ramka zgłosiła „Zamknij piec” sprzed ponownego uruchomienia programu, sprzed ponownego otwarcia "
                                      "pieca albo dla innego pieca — piec NIE został zamknięty. Jeśli jest rozłożony, zamknij go "
                                      "przyciskiem na ekranie."),
    "ramki_test_led": Wzor(POZIOM_INFO, "Test diod ramek",
                           "Ramki przez kilka sekund pokazują kolejne kolory na wszystkich diodach; potem wraca plan pieca."),
    # E3-O2 (plytki okragle ramkowe n1-n6; decyzja 5: komunikat + ramka ciemna, skan PRZYJETY, bez twardej blokady):
    # numer plytki lezacej na ramce a rola ramki, numer z ramki a numer plytki ze skanu, numer podany a numer z dolkow kodu
    "plytka_nie_z_ramki": Wzor(POZIOM_OSTRZEZENIE, "Płytka leży na złej ramce",
                               "Na ramce {ramka} leży płytka nr {numer}, a ta ramka podświetla tylko płytki {numery} — ramka nie "
                               "świeci. {rada}"),
    "plytka_inna_niz_skan": Wzor(POZIOM_OSTRZEZENIE, "Na ramce leży inna płytka niż zeskanowana",
                                 "Na ramce wieczornej leży płytka nr {na_ramce}, a ostatni skan to płytka nr {ze_skanu} — ramka nie "
                                 "świeci. Połóż na ramce płytkę nr {ze_skanu}. Jeśli na ramce leży właściwa płytka, to numer skanu "
                                 "jest zły — popraw go przyciskiem „Zmień numer” przy tej płytce na ekranie."),
    "plytka_bez_skanu": Wzor(POZIOM_OSTRZEZENIE, "Na ramce leży płytka, której nie ma w planie pieca",
                             "Na ramce porannej leży płytka nr {na_ramce}, a {w_planie} — ramka nie świeci. Zeskanuj płytkę "
                             "nr {na_ramce}. Jeśli była już skanowana, to numer jej skanu jest zły — popraw go przyciskiem "
                             "„Zmień numer” przy tej płytce na ekranie."),
    # runda 2 (recenzja PR #55, P1): piec ma skan bez numeru plytki - plytka na ramce najpewniej BYLA skanowana i czeka na numer;
    # runda 3 (D7): ``jest_skan`` = ``JEST_SKAN_BEZ_NUMERU`` (jeden skan / kilka), drugie zdanie - plytka mogla nie byc skanowana
    "plytka_czeka_na_numer": Wzor(POZIOM_OSTRZEZENIE, "Płytka na ramce czeka na numer skanu",
                                  "Na ramce porannej leży płytka nr {na_ramce}, a {w_planie} — ramka nie świeci. W tym piecu "
                                  "{jest_skan}, wybierz numer {na_ramce} w pytaniu „Podaj numer płytki” — ramka zaświeci sama. "
                                  "Jeśli tej płytki jeszcze nie skanowano — zeskanuj ją."),
    # runda 2 (recenzja PR #55, B1): wynik skanu wstrzymany na ramce wieczornej do odpowiedzi na pytanie o ponowny skan (napisy
    # przyciskow = ``PRZYCISKI["potwierdz_ponowny_skan"]`` / ``["odrzuc_ponowny_skan"]`` - test paczki pilnuje zgodnosci);
    # runda 3 (P3): rady wg kryterium PYTANIA ("te same prace"), nie "ta sama plytka" - nowy wsad na tej samej plytce to "Nie"
    "dwa_skany_numeru": Wzor(POZIOM_OSTRZEZENIE, "Dwa skany z numerem płytki {numer} — ramka czeka na odpowiedź",
                             "Są dwa skany płytki nr {numer} i płytka nr {numer} leży na ramce wieczornej — ramka nie świeci, dopóki "
                             "nie odpowiesz na pytanie o ponowny skan. Te same prace zeskanowane drugi raz — kliknij „Tak, to "
                             "ponowny skan”, ramka zaświeci. Nowe prace na tej samej płytce — kliknij „Nie, to nowy wsad”, ramka "
                             "zaświeci. Na ramce leży inna płytka niż ta z ostatniego skanu — najpierw zdejmij z ramki tę, która "
                             "leży, potem kliknij „Nie, to nowy wsad”; wynik ostatniego skanu pokaże wtedy ekran."),
    # przycisk przy plytce z numerem ma na ekranie napis "Zmień numer" (``ui.napisy.ZMIEN_NUMER`` - test paczki pilnuje zgodnosci)
    "numer_niezgodny": Wzor(POZIOM_OSTRZEZENIE, "Numer płytki nie zgadza się ze skanem",
                            "Podany numer płytki to {podany}, a program odczytał ze skanu numer {dolki}. Ramka nie podświetla tej "
                            "płytki; skan i wynik zostają. Sprawdź numer wybity na płytce: jeśli podany numer jest zły — popraw go "
                            "przyciskiem „Zmień numer”; jeśli jest dobry — pracuj według ekranu."),
    "excel_blad": Wzor(POZIOM_OSTRZEZENIE, "Excel nie odpowiada",
                       "{powod} — program działa dalej. Otwórz plik zleceń w Excelu i kliknij „Excel: wskaż wiersz” albo odhacz "
                       "ręcznie zlecenia kompletne pieca nr {nr} z {doba} ({ile}): {kuwety}."),
    "excel_cien": Wzor(POZIOM_INFO, "Excel: tryb cienia",
                       "Program nie zmienia arkusza (tryb „cień”) — zapisał w logu, co by zaznaczył dla pieca nr {nr} ({ile}). "
                       "Odhacz zlecenia w Excelu ręcznie."),
    "excel_zalegle": Wzor(POZIOM_OSTRZEZENIE, "Excel: piec czeka na odhaczenie",
                          "Piec nr {nr} z {doba}: {ile} bez wpisu w logu Excela — kliknij „Piec {nr}” na stronie „Kompletne i braki” (albo w oknie Excela) albo "
                          "odhacz ręcznie."),
}
# E3-A12: bledy ramek z ``indicate`` (kod ``stan()["blad"]``) - tekst ostateczny dla osoby (indicate.md: "ustala A12 w statusy.py")
BLEDY_RAMEK = {
    "zly_klucz": "Ramka odrzuca klucz — sprawdź [ramki] klucz w ustawieniach (ten sam co w pliku ramki), potem kliknij „Przejmij ramkę”.",
    "inny_laptop": "Tę ramkę obsługuje drugi laptop — zamknij program na drugim laptopie albo kliknij „Przejmij ramkę”.",
    "blad_sprzetu": "Awaria sprzętu ramki — diody zgaszone; ramka wróci sama, potem wynik pojawi się ponownie.",
    "plan_odrzucony": "Ramka odrzuciła plan (inna wersja programu ramki?) — diody zgaszone; rozkładaj według ekranu.",
    "plan_innej_ramki": "Adresy ramki wieczornej i porannej są zamienione w ustawieniach ([ramki]).",
    "zla_rola": "Pod adresem tej ramki odpowiada ramka innego rodzaju — sprawdź adresy ramek w ustawieniach.",
    "zla_odpowiedz": "Ramka odpowiada niezgodnie z protokołem (inna wersja programu ramki?).",
    "polecenie_odrzucone": "Ramka odrzuca polecenie — program ponawia.",
    "brak_kalibracji": "Brak poprawnej kalibracji diod ramki — gniazda nie będą wskazywane.",
}
# E3-O2: pola komunikatow ``plytka_nie_z_ramki`` / ``plytka_bez_skanu`` (rola ramki: "W" wieczorna, "P" poranna)
RAMKA_KTOREJ = {"W": "wieczornej", "P": "porannej"}
# rada wg roli ramki, gdy numer nalezy do DRUGIEJ ramki; None - numer spoza obu ramek (np. 7)
RADY_PLYTKA_NIE_Z_RAMKI = {
    "W": "To numer płytki porannej — połóż ją na ramce porannej. Jeśli to jednak płytka wieczorna, sprawdź, czy leży równo "
         "w ramce, i połóż ją jeszcze raz.",
    "P": "To numer płytki wieczornej — połóż ją na ramce wieczornej. Jeśli to jednak płytka poranna, sprawdź, czy leży równo "
         "w ramce, i połóż ją jeszcze raz.",
    None: "Sprawdź, czy płytka leży równo w ramce, i połóż ją jeszcze raz.",
}
W_PLANIE_PLYTKI = "ramka ma dla tego pieca tylko płytki: {plytki}"
W_PLANIE_BRAK = "ramka nie ma dla tego pieca żadnej płytki"
# runda 3 (D7): pole ``jest_skan`` komunikatu ``plytka_czeka_na_numer`` - klucz: czy skanow bez numeru jest wiecej niz jeden
JEST_SKAN_BEZ_NUMERU = {False: "jest skan bez numeru płytki: jeśli to skan tej płytki",
                        True: "są skany bez numeru płytki: jeśli jeden z nich to skan tej płytki"}
# E3-A12: napisy odmow polecen ramek i Excela (``Odpowiedz.tekst``)
NAPIS_RAMKI_NIEPODLACZONE = "Ramki nie są podłączone — program pracuje bez ramek (sekcja [ramki] w ustawieniach)."
NAPIS_EXCEL_NIEPODLACZONY = "Excel nie jest podłączony — odhacz zlecenia kompletne ręcznie."
NAPIS_POZYCJA_EXCELA_INNA = "Tej pozycji nie ma już w oknie Excela (lista się zmieniła) — wybierz zlecenie ponownie; nic nie zapisano."
NAPIS_BRAK_PIECA_EXCELA = "Nie ma zamkniętego pieca do odhaczenia w Excelu."
NAPIS_EXCEL_BLAD_PROGRAMU = "Błąd programu przy Excelu (szczegóły w logu)"
NAPIS_BLAD_PROGRAMU_RAMKI = "Błąd programu przy obsłudze klawisza ramki (szczegóły w logu)."
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
    # poranek (A6 runda 4): nastepny wsad przy niezamknietym piecu
    "nowy_wsad": Wzor(POZIOM_OSTRZEZENIE, "Poprzedni piec nie został zamknięty",
                      "Poprzedni piec nie został zamknięty. Zamknąć go i przenieść nowe skany (płytki {plytki}; skanów: {skanow}) "
                      "do nowego pieca?"),
    "numer_nowy_wsad": Wzor(POZIOM_OSTRZEZENIE, "Zmienić numer płytki mimo to?",
                            "Płytka {stary} ma drugi skan z innymi pracami — to chyba nowy wsad przy niezamkniętym piecu: lepiej "
                            "zamknąć poprzedni piec i przenieść nowe skany. Zmień numer na {numer} tylko wtedy, gdy na pewno jest zły."),
}
PLIK_NIEDOSTEPNY_PONOWIENIE = "Program próbuje ponownie (próba {proba} z {prob})."
PLIK_NIEDOSTEPNY_KONIEC = "Zamknij podgląd w programie skanera i zeskanuj płytkę ponownie."
SKUTEK_BEZ_DECYZJI = "Poprzedni skan nie ma jeszcze żadnych decyzji."
SKUTEK_Z_DECYZJAMI = ("Po potwierdzeniu przestanie obowiązywać {n} {decyzji} z poprzedniego skanu (w tym „Ukruszona”: {u}) — "
                      "trzeba je będzie zaznaczyć od nowa.")
SKUTEK_Z_DECYZJAMI_RANO = ("Po potwierdzeniu przestanie obowiązywać {n} {decyzji} z poprzedniego skanu (wybór kandydata, przypisanie) — "
                           "trzeba je będzie podjąć od nowa.")
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
# E3-O2 (przeglad narzedzi E3-S1, poz. 3): przyczyna bledu analizy rozpoznana z opisu bledu w dzienniku (``blad_analizy``) -
# zamiast samego "błąd analizy"; technik wie, CO poprawic przed ponownym skanem (wchodzi w pole ``powod`` komunikatu)
PRZYCZYNY_BLEDU_ANALIZY = {
    "znaczniki": "w skanie widać {n} z 3 znaczników płytki — płytka nie mieści się w polu skanera albo leży poza środkiem; "
                 "ustaw płytkę na środku i sprawdź, czy pole skanowania obejmuje całą płytkę",
    # runda 3: 0 z 3 - druga mozliwa przyczyna (skan z plaskim podlozem wokol plytki: 0 z 3 znacznikow) i rada o cieciu skanu
    "znaczniki_0": "w skanie widać 0 z 3 znaczników płytki — płytka nie mieści się w polu skanera albo leży poza środkiem, albo "
                   "w skanie jest stolik (podłoże) wokół płytki; ustaw płytkę na środku, sprawdź, czy pole skanowania obejmuje "
                   "całą płytkę, i ustaw cięcie skanu powyżej stolika",
    "wierzch": "w skanie nie widać płaskiego wierzchu płytki — to nie jest skan całej płytki; połóż płytkę płasko na środku skanera",
    "pusty": "skan jest prawie pusty — sprawdź, czy płytka leży w skanerze",
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
# E3-A5i: pula per praca ([silnik] pula_wpisow = true; KatalogPul -> wpisy z wspolczynnikami -> silnik) - napisy paska
STANY_PULI_WPISOW = {
    "nieustawiona": "pula wpisow wylaczona",
    "liczenie": "odswiezam katalog zlecen i wspolczynniki...",
    "gotowa": "wpisow puli: {n}{braki}",
    "pusta": "brak wpisow puli dnia (plik wspolczynnikow, katalog zlecen?)",
    "brak_folderu": "katalog zlecen niedostepny - odswiez pule",
}
NAPIS_BUDOWY_PULI = "wpisow puli: {n} - buduje pule: {k} z {r} (analiza czeka)"
NAPIS_BLAD_BUDOWY_PULI = " - budowa w tle nieudana ({blad}); pula powstanie w analizie pierwszego skanu"
# liczniki puli wpisow na pasku (tylko niezerowe): KatalogPul (bez_wspolczynnika, sprzeczne_wspolczynniki, brakujace) i
# match.Pula.z_wpisow (reszta)
LICZNIKI_PULI = {"brak_pliku": "brak pliku", "plik_zmieniony": "plik zmieniony", "bez_wspolczynnika": "bez wspolczynnika",
                 "sprzeczne_wspolczynniki": "sprzeczne wspolczynniki", "brakujace": "spoza katalogu", "pominiete": "nie do wczytania"}
# runda 2 (P4): przyczyny pustej / okrojonej puli wpisow (``Pula.przyczyna``, komunikaty ``pula_wpisow_*``)
PRZYCZYNY_PULI = {
    "csv_brak": "brak pliku wspolczynnikow (wspolczynniki.csv w folderze MillBox)",
    "csv_nie_ustawiono": "nie ustawiono folderu MillBox ([sciezki] folder_millbox)",
    "csv_blad": "plik wspolczynnikow odrzucony ({blad})",
    "bez_wierszy": "w pliku wspolczynnikow nie ma frezowan z ostatnich dob roboczych",
    "sprzeczne": "sprzeczne wspolczynniki krazkow: prac {n} (krazki: {krazki})",
    "bez_wspolczynnika": "prace bez wspolczynnika: {n} (krazki: {krazki})",
    "brakujace": "pliki z pliku wspolczynnikow spoza katalogu zlecen: {n}",
    "rano_brak": "brak zlecen zmienionych w ostatnich dniach roboczych (foldery Cyrkon / Prywatne)",
    "katalog": "blad odswiezenia katalogu ({blad})",
}
OPIS_PROPOZYCJI = "Propozycja programu (ratunek dopasowania) - sprawdz projekt i krazek."
# poranek (E3-A7): dlaczego "Zamknij piec" jest teraz niemozliwe (reguly session_rano)
BLOKADA_BEZ_NUMERU = "Podaj numer płytki ({skany}) — rano numer jest potrzebny przed „Zamknij piec”."
SKAN_Z_GODZINY = "skan z {godzina}"
BLOKADA_KONFLIKT = ("Rozstrzygnij konflikty ({n}): ten sam projekt w kilku gniazdach — dla jednej z prac wybierz inny projekt "
                    "albo „Bez projektu”.")
BLOKADA_DWA_SKANY = "Płytka {numer}: dwa skany z tym samym numerem — potwierdź ponowny skan, popraw numer albo pomiń jeden skan."
BLOKADA_NOWY_WSAD = ("Płytka {numer}: drugi skan z innymi pracami — to chyba nowy wsad: poprzedni piec nie został zamknięty. "
                     "Zamknij go i przenieś nowe skany (pytanie nad płytkami).")
# podstawa propozycji ponownego skanu (``session.PODSTAWA_*``, A6 runda 4: ``do_potwierdzenia[].podstawa``)
PODSTAWY_PONOWNEGO_SKANU = {"ten_sam_plik": "Ten sam plik skanu.", "te_same_prace": "Na obu skanach są te same prace.",
                            "za_malo_rozpoznanych": "Za mało rozpoznanych prac, żeby porównać skany.",
                            "regula_wylaczona": "Porównanie prac wyłączone w ustawieniach."}
PLYTKA_W_BLOKADZIE = "płytka {numer}"
PLYTKA_BEZ_NUMERU_W_BLOKADZIE = "płytka bez numeru"


def tekst_komunikatu(rodzaj: str, **pola) -> tuple[str, str, str]:
    """(poziom, tytul, tekst) komunikatu ``rodzaj`` z wypelnionymi polami; nieznany rodzaj = komunikat ogolny (bez wyjatku).
    E3-O2: pola sa wypelniane takze w tytule (``ramka_blad``: "Ramka {ramka}: problem" szlo na ekran z doslownym "{ramka}")."""
    w = KOMUNIKATY.get(rodzaj) or Wzor(POZIOM_OSTRZEZENIE, "Uwaga", "{powod}")
    return w.poziom, (_wypelnij(w.tytul, pola) if "{" in w.tytul else w.tytul), _wypelnij(w.tekst, pola)


def tekst_pytania(rodzaj: str, **pola) -> tuple[str, str, str]:
    w = PYTANIA[rodzaj]
    return w.poziom, w.tytul, _wypelnij(w.tekst, pola)


class _Braki(dict):
    def __missing__(self, klucz: str) -> str:
        return "?"


def _wypelnij(tekst: str, pola: dict) -> str:
    return tekst.format_map(_Braki(pola))
