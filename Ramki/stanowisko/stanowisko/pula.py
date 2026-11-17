"""pula - pule projektow dnia z indeksu w bazie: poranna i wieczorna ze wspolczynnikiem kazdej pracy (E3-A4).

Plan etapu 3, sekcja 3.5; decyzje wlasciciela z 17.11.2026 (DW6 = CSV i wpis reczny; doba robocza 06:00-06:00, trzy zmiany).
- Wpis puli (``Wpis``): ``sha16`` projektu, ``wspolczynnik``, ``krazek``, ``frezowanie_id`` (wiersz ``frezowania``, z ktorego
  wpis pochodzi - wynik dopasowania podaje go w ``kandydaci[0].frezowanie_id``, wtedy ``session`` zna krazek), ``projekt_id``,
  kuweta, zeby, typ, zrodlo wspolczynnika. Ten sam STL w dwoch wierszach frezowania = dwa wpisy (K4).
- Pula WIECZORNA (``pula_wieczorna``): aktualne wiersze ``frezowania`` z plikiem (CSV, pozniej raport MillBox) z ostatnich
  ``[match] pula_wieczor_dni`` dob ROBOCZYCH (decyzja robocza 7: 2 = dzis i poprzednia doba robocza; sobota, niedziela i dni
  z ``wolne`` nie zuzywaja okna - w poniedzialek pula obejmuje piatek) polaczone z indeksem od nowa przy kazdym wywolaniu
  (P2). Doba robocza D trwa od D 06:00 do D+1 06:00, a data frezowania to data kalendarza bez godziny - wiersz nalezy do puli,
  gdy jego dzien zachodzi na okno dob: o 20:00 17.11 (doba 17.11) i o 03:00 18.11 (3. zmiana tej samej doby) pula obejmuje daty
  16, 17 i 18.11. Wspolczynnik w tej kolejnosci: z wiersza (CSV / raport) -> wpis reczny krazka obowiazujacy dla doby
  frezowania (najnowszy z data odlegla najwyzej o ``wazny_dni``, ``wspolczynniki.wpisz_reczny``) -> ``wspolczynnik_awaryjny``
  (gdy podany) -> brak: wiersz liczony w ``bez_wspolczynnika``, krazek w ``krazki_bez_wspolczynnika`` (okno prosi o wpis).
  SPRZECZNE wspolczynniki (P4): krazek, ktory w jednej dobie ma w CSV dwie rozne wartosci albo wartosc inna niz obowiazujacy
  wpis reczny, nie daje wspolczynnika ZADNEJ swojej pracy z okna (licznik ``sprzeczne_wspolczynniki``, lista
  ``krazki_sprzeczne``), az czlowiek rozstrzygnie wpisem recznym z ``zmien=True`` (``reczny_potwierdzony``) - obejmuje on
  wiersze CSV wczytane przed nim; wiersz zmieniony pozniej to nowa sprzecznosc. STL z wiersza, ktorego nie ma w indeksie =
  licznik ``brakujace``.
- Pula PORANNA (``pula_poranna``): wszystkie pliki STL zlecen (folderow), w ktorych cos sie zmienilo od poczatku doby
  ``[match] pula_rano_dni_roboczych`` dni roboczych wstecz (sobota i niedziela sie nie licza - weekend nalezy do piatku;
  biezaca doba zawsze; swieta jak dni robocze - decyzja robocza 3, ``DNI_WOLNE`` puste), ale nie dawniej niz
  ``[match] usun_z_puli_po_dniach`` dni; "Prywatne": wszystkie z ostatnich ``dni_prywatne`` (10) dni kalendarzowych
  (decyzja robocza 4); takze zlecenia juz odhaczone; wspolczynnik 1,0 (K3). Licznik ``kuweta_niejednoznaczna`` (P1).
- ``krazki``: lista krazkow doby do wpisu recznego; ``sciezki_plikow``: sciezki do wczytania siatek; ``KatalogPul``: to samo
  z ustawien (``odswiez`` = indeks + plik CSV + powiazanie).

DANE OSOBOWE: wyniki ``pula_wieczorna``, ``pula_poranna``, ``krazki`` i ``KatalogPul.odswiez`` nie zawieraja nazw folderow
ani plikow - tylko ``sha16``, id wierszy, kuwety, zeby, krazki, liczby. JEDYNY wyjatek: ``sciezki_plikow`` (i ``KatalogPul.sciezki``)
zwraca sciezki plikow do wczytania siatki w procesie silnika - nie zapisywac ich, nie logowac i nie pokazywac.
Opis: ``opisy_modulow/pula.md``.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import baza as B
from . import indeks as I
from . import nazwy as N
from . import wspolczynniki as W
from .wspolczynniki import doba_robocza

GRANICA_DOBY_GODZ = 6  # [sesja] granica_doby_godz
DNI_WIECZOR = 2  # [match] pula_wieczor_dni - doby ROBOCZE (decyzja robocza 7)
DNI_RANO = 4  # [match] pula_rano_dni_roboczych
USUN_PO_DNIACH = 10  # [match] usun_z_puli_po_dniach
DNI_PRYWATNE = 10  # decyzja robocza 4: "Prywatne" w puli porannej - wszystkie z ostatnich tylu dni kalendarzowych
DNI_WOLNE: frozenset = frozenset()  # decyzja robocza 3: swieta jak dni robocze (brak kalendarza swiat); daty tu = dni wolne
ZRODLO_PRYWATNE = I.ZRODLA[1]
TRYB_WIECZOR, TRYB_RANO = "wieczor", "rano"
ZRODLO_RANO, ZRODLO_AWARYJNY = "rano", "awaryjny"
BEZ_KRAZKA = "(bez krazka)"
_PORCJA = 500

__all__ = ["Wpis", "Pula", "KatalogPul", "doba_robocza", "poczatek_dni_roboczych", "okno_wieczoru", "pula_wieczorna", "pula_poranna",
           "krazki", "sciezki_plikow"]


@dataclass(frozen=True)
class Wpis:
    """Jeden wpis puli: projekt x wspolczynnik (bez nazw folderow i plikow)."""
    sha16: str
    wspolczynnik: float
    krazek: str | None
    frezowanie_id: int | None  # None w puli porannej
    projekt_id: int
    kuweta: str | None
    zeby: str | None
    typ: str | None
    zrodlo_wspolczynnika: str  # csv / millbox_html / millbox_pdf / reczny / awaryjny / rano
    data: str | None = None  # data frezowania (pula wieczorna)


@dataclass
class Pula:
    """Pula dnia: ``wpisy`` + ``liczniki`` dla ekranu; ``od`` / ``do`` = okno czasu (ISO), ``doba`` = doba robocza chwili budowy."""
    tryb: str
    doba: str
    od: str
    do: str
    wpisy: list[Wpis] = field(default_factory=list)
    liczniki: dict = field(default_factory=dict)

    def do_slownika(self) -> dict:
        return {"tryb": self.tryb, "doba": self.doba, "od": self.od, "do": self.do, "liczniki": dict(self.liczniki),
                "wpisy": [asdict(w) for w in self.wpisy]}

    def sha16(self) -> set[str]:
        return {w.sha16 for w in self.wpisy}

    def wspolczynniki(self) -> dict[str, float]:
        """``sha16`` -> wspolczynnik dla projektow z JEDNYM wspolczynnikiem w puli (obecny ``silnik.OpisPuli.wspolczynniki``
        do czasu paczki A5); projekt z kilkoma wspolczynnikami (``liczniki['sha16_z_kilkoma_wspolczynnikami']``) pomijany."""
        po_sha: dict[str, set[float]] = {}
        for w in self.wpisy:
            po_sha.setdefault(w.sha16, set()).add(round(w.wspolczynnik, 6))
        return {s: next(iter(ws)) for s, ws in po_sha.items() if len(ws) == 1}


def _poczatek_doby(dzien: dt.date, granica_doby_godz: int) -> dt.datetime:
    return dt.datetime.combine(dzien, dt.time(granica_doby_godz))


def poczatek_dni_roboczych(dzien: dt.date, dni: int, wolne=DNI_WOLNE) -> dt.date:
    """Dzien ``dni`` dni roboczych przed ``dzien`` (sobota, niedziela i daty z ``wolne`` sie nie licza; przeniesione z H)."""
    d = dzien
    while dni > 0:
        d -= dt.timedelta(days=1)
        if d.weekday() < 5 and d not in wolne:
            dni -= 1
    return d


def okno_wieczoru(teraz: dt.datetime, dni: int = DNI_WIECZOR, granica_doby_godz: int = GRANICA_DOBY_GODZ,
                  wolne=DNI_WOLNE) -> tuple[dt.date, dt.datetime, dt.datetime, str, str]:
    """(doba, poczatek okna, koniec okna, pierwsza data, ostatnia data) - okno ``dni`` dob roboczych (biezaca doba i ``dni - 1``
    dob roboczych wstecz; weekend i ``wolne`` nie zuzywaja okna - decyzja robocza 7) i daty kalendarza, ktorych dzien zachodzi
    na to okno."""
    if not isinstance(dni, int) or dni < 1:
        raise ValueError(f"pula wieczorna: liczba dob musi byc >= 1 (jest {dni!r}; [match] pula_wieczor_dni)")
    doba = doba_robocza(teraz, granica_doby_godz)
    od = _poczatek_doby(poczatek_dni_roboczych(doba, dni - 1, wolne), granica_doby_godz)
    do = _poczatek_doby(doba + dt.timedelta(days=1), granica_doby_godz)
    ostatnia = do.date() if do.time() != dt.time(0) else do.date() - dt.timedelta(days=1)
    return doba, od, do, od.date().isoformat(), ostatnia.isoformat()


def _wiersze_okna(baza: B.Baza, pierwsza: str, ostatnia: str) -> list[dict]:
    """Aktualne wiersze frezowania z plikiem z dat okna (bez ``csv_nieaktualny``)."""
    return baza.wiersze("SELECT id, projekt_id, plik_w_raporcie, krazek, wspolczynnik, data, zrodlo, wczytano FROM frezowania "
                        "WHERE plik_w_raporcie IS NOT NULL AND data >= ? AND data <= ? AND (zrodlo IS NULL OR zrodlo != ?) ORDER BY id",
                        (pierwsza, ostatnia, W.ZRODLO_CSV_NIEAKTUALNY))


@dataclass
class _Ocena:
    """Wspolczynniki wierszy okna: ``wiersze`` frezowanie_id -> (wspolczynnik albo None, zrodlo albo "sprzeczne" / "brak")."""
    wiersze: dict
    sprzeczne: list  # krazki ze sprzecznymi wspolczynnikami (nierozstrzygnietymi)


def _ocen(wiersze: list[dict], reczne: dict[str, list[dict]], wazny_dni: int) -> _Ocena:
    """Wspolczynnik kazdego wiersza okna (P4). Grupa = (krazek, data): rozne wartosci CSV w grupie albo wartosc CSV inna niz
    wpis reczny obowiazujacy dla tej doby = sprzecznosc; rozstrzyga ja tylko wpis ``reczny_potwierdzony`` wpisany nie
    wczesniej niz wiersze CSV grupy. Krazek z nierozstrzygnieta sprzecznoscia nie daje wspolczynnika zadnej pracy okna."""
    grupy: dict[tuple, list[dict]] = {}
    for f in wiersze:
        if f["krazek"] is not None:
            grupy.setdefault((f["krazek"], f["data"]), []).append(f)
    sprzeczne, rozstrzygniete, obowiazujace = set(), {}, {}
    for (krazek, data), ws in grupy.items():
        r = W.reczny_dla(reczne.get(krazek, ()), dt.date.fromisoformat(data), wazny_dni)
        obowiazujace[(krazek, data)] = r
        z_wartoscia = [f for f in ws if f["wspolczynnik"] is not None]
        wartosci = {round(float(f["wspolczynnik"]), 6) for f in z_wartoscia}
        sprzecznosc = len(wartosci) > 1 or (len(wartosci) == 1 and r is not None and not W._rowne(next(iter(wartosci)), r["wspolczynnik"]))
        if not sprzecznosc:
            continue
        if r is not None and r["zrodlo"] == W.ZRODLO_RECZNY_POTWIERDZONY and (r["wczytano"] or "") >= max(f["wczytano"] or "" for f in z_wartoscia):
            rozstrzygniete[(krazek, data)] = r
        else:
            sprzeczne.add(krazek)
    wynik = {}
    for f in wiersze:
        g = (f["krazek"], f["data"])
        r = obowiazujace.get(g)
        if f["krazek"] in sprzeczne:
            wynik[f["id"]] = (None, "sprzeczne")
        elif g in rozstrzygniete:
            wynik[f["id"]] = (float(rozstrzygniete[g]["wspolczynnik"]), W.ZRODLO_RECZNY)
        elif f["wspolczynnik"] is not None:
            wynik[f["id"]] = (float(f["wspolczynnik"]), f["zrodlo"] or W.ZRODLO_CSV)
        elif r is not None:
            wynik[f["id"]] = (float(r["wspolczynnik"]), W.ZRODLO_RECZNY)
        else:
            wynik[f["id"]] = (None, "brak")
    return _Ocena(wynik, sorted(sprzeczne))


def _z_cechami(baza: B.Baza, skroty: set[str]) -> set[str]:
    lista = sorted(skroty)
    znane: set[str] = set()
    for i in range(0, len(lista), _PORCJA):
        czesc = lista[i:i + _PORCJA]
        znane |= {w["sha16"] for w in baza.wiersze(f"SELECT sha16 FROM cechy_stl WHERE sha16 IN ({', '.join('?' * len(czesc))})", tuple(czesc))}
    return znane


def pula_wieczorna(baza: B.Baza, teraz: dt.datetime | None = None, *, dni: int = DNI_WIECZOR,
                   granica_doby_godz: int = GRANICA_DOBY_GODZ, wspolczynnik_awaryjny: float | None = None,
                   wazny_dni: int = W.WAZNY_DNI, wolne=DNI_WOLNE) -> Pula:
    """Pula wieczorna (opis w naglowku modulu). Nic nie zapisuje: kazdy wiersz jest laczony z indeksem w pamieci od nowa
    (zapisane powiazanie nie ma pierwszenstwa - P2; zapis powiazan: ``wspolczynniki.powiaz_frezowania`` / ``KatalogPul.odswiez``)."""
    teraz = teraz or dt.datetime.now()
    doba, od, do, pierwsza, ostatnia = okno_wieczoru(teraz, dni, granica_doby_godz, wolne)
    indeks = I.IndeksPlikow(baza)
    wiersze = _wiersze_okna(baza, pierwsza, ostatnia)
    ocena = _ocen(wiersze, W.wpisy_reczne(baza), wazny_dni)
    wpisy: list[Wpis] = []
    lz = {"wierszy": len(wiersze), "wpisow": 0, "brakujace": 0, "niejednoznaczne": 0, "po_samej_nazwie": 0, "bez_wspolczynnika": 0,
          "krazki_bez_wspolczynnika": [], "sprzeczne_wspolczynniki": 0, "krazki_sprzeczne": ocena.sprzeczne, "bez_sha16": 0,
          "bez_cech": 0, "sha16_z_kilkoma_wspolczynnikami": 0}
    krazki_bez: set[str] = set()
    for f in wiersze:
        d = indeks.dopasuj(f["plik_w_raporcie"], dt.date.fromisoformat(f["data"]))
        lz["niejednoznaczne"] += d.kandydatow > 1
        lz["po_samej_nazwie"] += d.po_nazwie
        projekt = d.wiersz
        if projekt is None:
            lz["brakujace"] += 1
            continue
        if not projekt["sha16"]:
            lz["bez_sha16"] += 1
            continue
        w, zrodlo = ocena.wiersze[f["id"]]
        if zrodlo == "sprzeczne":
            lz["sprzeczne_wspolczynniki"] += 1
            continue
        if w is None and wspolczynnik_awaryjny is not None:
            w, zrodlo = float(wspolczynnik_awaryjny), ZRODLO_AWARYJNY
        if w is None:
            lz["bez_wspolczynnika"] += 1
            krazki_bez.add(f["krazek"] or BEZ_KRAZKA)
            continue
        wpisy.append(Wpis(sha16=projekt["sha16"], wspolczynnik=w, krazek=f["krazek"], frezowanie_id=f["id"], projekt_id=projekt["id"],
                          kuweta=projekt["kuweta"], zeby=projekt["zeby"], typ=projekt["typ"], zrodlo_wspolczynnika=zrodlo, data=f["data"]))
    pula = Pula(TRYB_WIECZOR, doba.isoformat(), od.isoformat(), do.isoformat(), wpisy)
    lz["krazki_bez_wspolczynnika"] = sorted(krazki_bez)
    lz["wpisow"] = len(wpisy)
    z_cechami = _z_cechami(baza, pula.sha16()) if wpisy else set()
    lz["bez_cech"] = sum(w.sha16 not in z_cechami for w in wpisy)
    lz["sha16_z_kilkoma_wspolczynnikami"] = len(pula.sha16()) - len(pula.wspolczynniki())
    pula.liczniki = lz
    return pula


def pula_poranna(baza: B.Baza, teraz: dt.datetime | None = None, *, dni_robocze: int = DNI_RANO, usun_po_dniach: int = USUN_PO_DNIACH,
                 granica_doby_godz: int = GRANICA_DOBY_GODZ, dni_prywatne: int = DNI_PRYWATNE, wolne=DNI_WOLNE) -> Pula:
    """Pula poranna (opis w naglowku modulu): punkty pracy zlecen zmienionych od poczatku okna, wspolczynnik 1,0. Okno
    "Prywatne": nie krotsze niz ``dni_prywatne`` dni kalendarzowych (decyzja robocza 4), oba nie dawniej niz ``usun_po_dniach``."""
    teraz = teraz or dt.datetime.now()
    if not isinstance(dni_robocze, int) or dni_robocze < 0:
        raise ValueError(f"pula poranna: liczba dni roboczych musi byc >= 0 (jest {dni_robocze!r}; [match] pula_rano_dni_roboczych)")
    doba = doba_robocza(teraz, granica_doby_godz)
    od_robocze = _poczatek_doby(poczatek_dni_roboczych(doba, dni_robocze, wolne), granica_doby_godz)
    limit = teraz - dt.timedelta(days=usun_po_dniach)
    od = max(od_robocze, limit).replace(microsecond=0)
    od_prywatne = max(min(od_robocze, teraz - dt.timedelta(days=dni_prywatne)), limit).replace(microsecond=0)
    wiersze = baza.wiersze("SELECT p.id, p.sha16, p.zeby, p.typ, p.zlecenie_id, z.kuweta FROM projekty p JOIN zlecenia z ON z.id = p.zlecenie_id "
                           "WHERE z.usuniety = 0 AND p.usuniety = 0 AND z.mtime >= (CASE WHEN z.zrodlo = ? THEN ? ELSE ? END) ORDER BY p.id",
                           (ZRODLO_PRYWATNE, od_prywatne.timestamp(), od.timestamp()))
    wpisy = [Wpis(sha16=w["sha16"], wspolczynnik=1.0, krazek=None, frezowanie_id=None, projekt_id=w["id"], kuweta=w["kuweta"],
                  zeby=w["zeby"], typ=w["typ"], zrodlo_wspolczynnika=ZRODLO_RANO) for w in wiersze if w["sha16"]]
    pula = Pula(TRYB_RANO, doba.isoformat(), od.isoformat(), teraz.replace(microsecond=0).isoformat(), wpisy)
    z_cechami = _z_cechami(baza, pula.sha16()) if wpisy else set()
    zlecenia = {w["zlecenie_id"]: w["kuweta"] for w in wiersze if w["sha16"]}
    pula.liczniki = {"wpisow": len(wpisy), "zlecen": len(zlecenia),
                     "bez_sha16": sum(not w["sha16"] for w in wiersze), "bez_cech": sum(w.sha16 not in z_cechami for w in wpisy),
                     "bez_kuwety": sum(w.kuweta is None for w in wpisy),
                     "kuweta_niejednoznaczna": sum(N.czy_niejednoznaczna(k) for k in zlecenia.values())}  # foldery (P1)
    return pula


def krazki(baza: B.Baza, teraz: dt.datetime | None = None, *, dni: int = DNI_WIECZOR, granica_doby_godz: int = GRANICA_DOBY_GODZ,
           wazny_dni: int = W.WAZNY_DNI, wolne=DNI_WOLNE) -> list[dict]:
    """Krazki z okna puli wieczornej (aktualne wiersze z plikiem i wpisy reczne z tych dob) - lista do wpisu recznego.

    Pola: ``krazek``, ``plikow`` (wiersze z plikiem w oknie), ``plikow_bez_wspolczynnika``, ``wspolczynniki_csv`` (rozne wartosci
    z wierszy), ``wspolczynnik_reczny`` / ``data_recznego`` / ``frezowanie_reczne_id`` (ostatni wpis reczny, z dowolnego dnia),
    ``brakuje`` (sa pliki bez wspolczynnika i bez wpisu recznego obowiazujacego dla ich doby - takze, gdy ostatni wpis jest
    starszy niz ``wazny_dni``: program pyta ponownie), ``sprzeczne`` (P4: okno prosi o rozstrzygniecie wpisem z
    ``zmien=True``). Kolejnosc: oznaczenie krazka.
    """
    teraz = teraz or dt.datetime.now()
    _, _, _, pierwsza, ostatnia = okno_wieczoru(teraz, dni, granica_doby_godz, wolne)
    reczne = W.wpisy_reczne(baza)
    wiersze = _wiersze_okna(baza, pierwsza, ostatnia)
    ocena = _ocen(wiersze, reczne, wazny_dni)
    wynik: dict[str | None, dict] = {}

    def pozycja(k: str | None) -> dict:
        if k not in wynik:
            r = reczne[k][-1] if k in reczne else None
            wynik[k] = {"krazek": k, "plikow": 0, "plikow_bez_wspolczynnika": 0, "wspolczynniki_csv": set(),
                        "wspolczynnik_reczny": r["wspolczynnik"] if r else None, "data_recznego": r["data"] if r else None,
                        "frezowanie_reczne_id": r["id"] if r else None, "brakuje": False, "sprzeczne": k in ocena.sprzeczne}
        return wynik[k]

    for k, ws in reczne.items():  # wpis reczny z dob okna: krazek na liscie
        if any(pierwsza <= w["data"] <= ostatnia for w in ws):
            pozycja(k)
    for f in wiersze:
        p = pozycja(f["krazek"])
        p["plikow"] += 1
        if f["wspolczynnik"] is None:
            p["plikow_bez_wspolczynnika"] += 1
        else:
            p["wspolczynniki_csv"].add(round(float(f["wspolczynnik"]), 4))
        p["brakuje"] |= ocena.wiersze[f["id"]][1] == "brak"
    lista = []
    for k in sorted(wynik, key=lambda k: (k is None, k or "")):
        p = wynik[k]
        p["wspolczynniki_csv"] = sorted(p["wspolczynniki_csv"])
        lista.append(p)
    return lista


def sciezki_plikow(baza: B.Baza, wpisy, zrodla: dict[str, str | Path | None]) -> dict[int, Path]:
    """``projekt_id`` -> sciezka pliku STL do wczytania siatki (``zrodla`` jak w ``indeks.indeksuj``).

    DANE OSOBOWE: sciezka zawiera nazwe folderu i pliku zlecenia - tylko do wczytania pliku w procesie silnika; nie zapisywac
    w bazie poza czterema tabelami, w plikach wynikow, logach ani komunikatach (plan 3.4, zasada 1).
    """
    ids = sorted({w.projekt_id for w in wpisy})
    wynik: dict[int, Path] = {}
    for i in range(0, len(ids), _PORCJA):
        czesc = ids[i:i + _PORCJA]
        for w in baza.wiersze(f"SELECT p.id, p.plik, z.folder, z.zrodlo FROM projekty p JOIN zlecenia z ON z.id = p.zlecenie_id "
                              f"WHERE p.id IN ({', '.join('?' * len(czesc))})", tuple(czesc)):
            katalog = zrodla.get(w["zrodlo"])
            if katalog is not None:
                wynik[w["id"]] = Path(katalog) / w["folder"] / w["plik"]
    return wynik


class KatalogPul:
    """Katalog i pule wg ustawien - jeden obiekt dla aplikacji (A3) i silnika (A5).

    ``odswiez(teraz)``: indeks folderow (z folderami starymi, do ktorych odwoluja sie wiersze frezowania z okna puli - D3) +
    plik CSV wspolczynnikow (jesli jest) + powiazanie wierszy frezowania z okna od nowa (P2); zwraca liczby (bez nazw), w tym
    ``sprzeczne_wspolczynniki`` i ``krazki_sprzeczne`` (P4); zly CSV nie przerywa odswiezenia (``csv_plik = "blad"``,
    ``csv_blad`` = komunikat z numerami linii). Pozostale metody jak funkcje modulu z parametrami z ustawien. Odswiezenie trwa
    (cechy nowych plikow) - w programie okienkowym w watku roboczym, z obiektem utworzonym w tym watku (``z_ustawien``: wlasne
    polaczenie z baza).
    """

    def __init__(self, baza: B.Baza, zrodla: dict[str, str | Path | None], *, plik_csv: str | Path | None = None,
                 dni_wieczor: int = DNI_WIECZOR, dni_rano: int = DNI_RANO, usun_po_dniach: int = USUN_PO_DNIACH,
                 granica_doby_godz: int = GRANICA_DOBY_GODZ, wspolczynnik_awaryjny: float | None = None, licz_cechy: bool = True,
                 dni_prywatne: int = DNI_PRYWATNE, wazny_dni: int = W.WAZNY_DNI, wolne=DNI_WOLNE, wlasna_baza: bool = False):
        self.baza = baza
        self.zrodla = dict(zrodla)
        self.plik_csv = Path(plik_csv) if plik_csv is not None else None
        self.dni_wieczor = dni_wieczor
        self.dni_rano = dni_rano
        self.usun_po_dniach = usun_po_dniach
        self.granica_doby_godz = granica_doby_godz
        self.wspolczynnik_awaryjny = wspolczynnik_awaryjny
        self.licz_cechy = licz_cechy
        self.dni_prywatne = dni_prywatne
        self.wazny_dni = wazny_dni
        self.wolne = frozenset(wolne)
        self._wlasna_baza = wlasna_baza

    @classmethod
    def z_ustawien(cls, ust: dict, baza: B.Baza | None = None, *, nazwa_csv: str = "wspolczynniki.csv", **kw) -> "KatalogPul":
        """Z ``ustawienia.toml``: ``[sciezki] folder_cyrkon, folder_prywatne, folder_millbox`` (plik CSV ``nazwa_csv`` w tym folderze),
        ``baza``; ``[match] pula_wieczor_dni, pula_rano_dni_roboczych, usun_z_puli_po_dniach``; ``[sesja] granica_doby_godz``."""
        wlasna = baza is None
        if baza is None:
            baza = B.otworz(B.sciezka_bazy(ust))
        kw.setdefault("plik_csv", B.sciezka_z_ustawien(ust, "folder_millbox") / nazwa_csv)
        return cls(baza, I.zrodla_z_ustawien(ust), dni_wieczor=ust["match"]["pula_wieczor_dni"],
                   dni_rano=ust["match"]["pula_rano_dni_roboczych"], usun_po_dniach=ust["match"]["usun_z_puli_po_dniach"],
                   granica_doby_godz=ust["sesja"]["granica_doby_godz"], wlasna_baza=wlasna, **kw)

    def zamknij(self) -> None:
        if self._wlasna_baza:
            self.baza.zamknij()

    def odswiez(self, teraz: dt.datetime | None = None) -> dict:
        teraz = teraz or dt.datetime.now()
        _, _, _, pierwsza, ostatnia = okno_wieczoru(teraz, self.dni_wieczor, self.granica_doby_godz, self.wolne)
        wymagane = W.pliki_frezowan(self.baza, pierwsza, ostatnia)  # D3: pliki z okna puli - foldery stare tez do indeksu
        if self.plik_csv is not None and self.plik_csv.is_file():
            try:
                wymagane |= {w.plik for w in W.wczytaj_csv(self.plik_csv, dzis=teraz.date()) if pierwsza <= w.data.isoformat() <= ostatnia}
            except W.BladWspolczynnikow:
                pass  # blad pliku zglasza wczytanie nizej
        r = I.indeksuj(self.baza, self.zrodla, teraz, usun_po_dniach=self.usun_po_dniach, licz_cechy=self.licz_cechy, wymagane=wymagane)
        del wymagane
        wynik = {"indeks": r.do_slownika(), "csv_plik": None, "csv": None, "csv_blad": None, "powiazanie": None,
                 "sprzeczne_wspolczynniki": 0, "krazki_sprzeczne": []}
        if self.plik_csv is None:
            wynik["csv_plik"] = "nie ustawiono"
        elif not self.plik_csv.is_file():
            wynik["csv_plik"] = "brak"
        else:
            try:
                wynik["csv"] = W.wczytaj_do_bazy(self.baza, self.plik_csv, teraz=teraz).do_slownika()
                wynik["csv_plik"] = "jest"
            except W.BladWspolczynnikow as e:
                wynik["csv_plik"] = "blad"
                wynik["csv_blad"] = str(e)
                self.baza.zdarzenie("pula", "wspolczynniki_csv_blad", {"linie": e.linie[:50], "blednych": len(e.linie)})
        wynik["powiazanie"] = W.powiaz_frezowania(self.baza, okno=(pierwsza, ostatnia)).do_slownika()
        lz = self.pula_wieczorna(teraz).liczniki
        wynik["sprzeczne_wspolczynniki"], wynik["krazki_sprzeczne"] = lz["sprzeczne_wspolczynniki"], lz["krazki_sprzeczne"]
        if lz["krazki_sprzeczne"]:
            self.baza.zdarzenie("pula", "sprzeczne_wspolczynniki", {"prac": lz["sprzeczne_wspolczynniki"], "krazki": lz["krazki_sprzeczne"]})
        return wynik

    def pula_wieczorna(self, teraz: dt.datetime | None = None) -> Pula:
        return pula_wieczorna(self.baza, teraz, dni=self.dni_wieczor, granica_doby_godz=self.granica_doby_godz,
                              wspolczynnik_awaryjny=self.wspolczynnik_awaryjny, wazny_dni=self.wazny_dni, wolne=self.wolne)

    def pula_poranna(self, teraz: dt.datetime | None = None) -> Pula:
        return pula_poranna(self.baza, teraz, dni_robocze=self.dni_rano, usun_po_dniach=self.usun_po_dniach,
                            granica_doby_godz=self.granica_doby_godz, dni_prywatne=self.dni_prywatne, wolne=self.wolne)

    def krazki(self, teraz: dt.datetime | None = None) -> list[dict]:
        return krazki(self.baza, teraz, dni=self.dni_wieczor, granica_doby_godz=self.granica_doby_godz, wazny_dni=self.wazny_dni,
                      wolne=self.wolne)

    def wpisz_wspolczynnik(self, krazek: str, wspolczynnik, *, operator: str, zmien: bool = False, data: str | dt.date | None = None,
                           teraz: dt.datetime | None = None) -> int:
        """Wpis reczny (``wspolczynniki.wpisz_reczny``); ``operator`` wymagany (decyzja robocza 5), ``zmien=True`` rozstrzyga
        sprzecznosc z CSV (P4)."""
        return W.wpisz_reczny(self.baza, krazek, wspolczynnik, operator=operator, zmien=zmien, data=data, teraz=teraz,
                              granica_doby_godz=self.granica_doby_godz, wazny_dni=self.wazny_dni)

    def wspolczynnik_krazka(self, krazek: str) -> dict | None:
        return W.wspolczynnik_krazka(self.baza, krazek)

    def sciezki(self, wpisy) -> dict[int, Path]:
        """Sciezki plikow do wczytania (DANE OSOBOWE - patrz ``sciezki_plikow``)."""
        return sciezki_plikow(self.baza, wpisy, self.zrodla)
