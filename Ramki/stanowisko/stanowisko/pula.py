"""pula - pule projektow dnia z indeksu w bazie: poranna i wieczorna ze wspolczynnikiem kazdej pracy (E3-A4).

Plan etapu 3, sekcja 3.5; decyzje wlasciciela z 17.11.2026 (DW6 = CSV i wpis reczny; doba robocza 06:00-06:00, trzy zmiany).
- Wpis puli (``Wpis``): ``sha16`` projektu, ``wspolczynnik``, ``krazek``, ``frezowanie_id`` (wiersz ``frezowania``, z ktorego
  wpis pochodzi - wynik dopasowania podaje go w ``kandydaci[0].frezowanie_id``, wtedy ``session`` zna krazek), ``projekt_id``,
  kuweta, zeby, typ, zrodlo wspolczynnika. Ten sam STL w dwoch wierszach frezowania = dwa wpisy (K4).
- Pula WIECZORNA (``pula_wieczorna``): wiersze ``frezowania`` z plikiem (CSV, pozniej raport MillBox) z ostatnich
  ``[match] pula_wieczor_dni`` dob roboczych (2 = dzis i wczoraj) polaczone z indeksem. Doba robocza D trwa od D 06:00 do D+1
  06:00, a data frezowania to data kalendarza bez godziny - wiersz nalezy do puli, gdy jego dzien zachodzi na okno dob:
  o 20:00 17.11 (doba 17.11) i o 03:00 18.11 (3. zmiana tej samej doby) pula obejmuje daty 16, 17 i 18.11. Wspolczynnik w tej
  kolejnosci: z wiersza (CSV / raport) -> wpis reczny krazka (najnowszy, ``wspolczynniki.wpisz_reczny``) -> ``wspolczynnik_awaryjny``
  (gdy podany) -> brak: wiersz liczony w ``bez_wspolczynnika``, krazek w ``krazki_bez_wspolczynnika`` (okno prosi o wpis).
  STL z wiersza, ktorego nie ma w indeksie = licznik ``brakujace``.
- Pula PORANNA (``pula_poranna``): wszystkie pliki STL zlecen (folderow), w ktorych cos sie zmienilo od poczatku doby
  ``[match] pula_rano_dni_roboczych`` dni roboczych wstecz (sobota i niedziela sie nie licza - weekend nalezy do piatku;
  biezaca doba zawsze), ale nie dawniej niz ``[match] usun_z_puli_po_dniach`` dni; oba zrodla ("Cyrkon" i "Prywatne"),
  takze zlecenia juz odhaczone; wspolczynnik 1,0 (K3).
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
from . import wspolczynniki as W
from .wspolczynniki import doba_robocza

GRANICA_DOBY_GODZ = 6  # [sesja] granica_doby_godz
DNI_WIECZOR = 2  # [match] pula_wieczor_dni
DNI_RANO = 4  # [match] pula_rano_dni_roboczych
USUN_PO_DNIACH = 10  # [match] usun_z_puli_po_dniach
TRYB_WIECZOR, TRYB_RANO = "wieczor", "rano"
ZRODLO_RANO, ZRODLO_AWARYJNY = "rano", "awaryjny"
BEZ_KRAZKA = "(bez krazka)"
_PORCJA = 500

__all__ = ["Wpis", "Pula", "KatalogPul", "doba_robocza", "poczatek_dni_roboczych", "pula_wieczorna", "pula_poranna", "krazki",
           "sciezki_plikow"]


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


def poczatek_dni_roboczych(dzien: dt.date, dni: int) -> dt.date:
    """Dzien ``dni`` dni roboczych przed ``dzien`` (sobota i niedziela sie nie licza; przeniesione z H)."""
    d = dzien
    while dni > 0:
        d -= dt.timedelta(days=1)
        if d.weekday() < 5:
            dni -= 1
    return d


def _okno_wieczoru(teraz: dt.datetime, dni: int, granica_doby_godz: int) -> tuple[dt.date, dt.datetime, dt.datetime, str, str]:
    """(doba, poczatek okna, koniec okna, pierwsza data, ostatnia data) - daty kalendarza, ktorych dzien zachodzi na okno dob."""
    if not isinstance(dni, int) or dni < 1:
        raise ValueError(f"pula wieczorna: liczba dob musi byc >= 1 (jest {dni!r}; [match] pula_wieczor_dni)")
    doba = doba_robocza(teraz, granica_doby_godz)
    od = _poczatek_doby(doba - dt.timedelta(days=dni - 1), granica_doby_godz)
    do = _poczatek_doby(doba + dt.timedelta(days=1), granica_doby_godz)
    ostatnia = do.date() if do.time() != dt.time(0) else do.date() - dt.timedelta(days=1)
    return doba, od, do, od.date().isoformat(), ostatnia.isoformat()


def _reczne(baza: B.Baza) -> dict[str, dict]:
    """Krazek -> obowiazujacy wpis reczny (najnowsza data, potem najnowszy wiersz)."""
    wynik: dict[str, dict] = {}
    for w in baza.wiersze("SELECT id, krazek, wspolczynnik, data FROM frezowania WHERE zrodlo = ? AND plik_w_raporcie IS NULL "
                          "AND krazek IS NOT NULL ORDER BY data, id", (W.ZRODLO_RECZNY,)):
        wynik[w["krazek"]] = w
    return wynik


def _z_cechami(baza: B.Baza, skroty: set[str]) -> set[str]:
    lista = sorted(skroty)
    znane: set[str] = set()
    for i in range(0, len(lista), _PORCJA):
        czesc = lista[i:i + _PORCJA]
        znane |= {w["sha16"] for w in baza.wiersze(f"SELECT sha16 FROM cechy_stl WHERE sha16 IN ({', '.join('?' * len(czesc))})", tuple(czesc))}
    return znane


def pula_wieczorna(baza: B.Baza, teraz: dt.datetime | None = None, *, dni: int = DNI_WIECZOR,
                   granica_doby_godz: int = GRANICA_DOBY_GODZ, wspolczynnik_awaryjny: float | None = None) -> Pula:
    """Pula wieczorna (opis w naglowku modulu). Nic nie zapisuje: wiersze bez powiazania z indeksem sa laczone w pamieci
    (zapis powiazan: ``wspolczynniki.powiaz_frezowania`` / ``KatalogPul.odswiez``)."""
    teraz = teraz or dt.datetime.now()
    doba, od, do, pierwsza, ostatnia = _okno_wieczoru(teraz, dni, granica_doby_godz)
    indeks = I.IndeksPlikow(baza)
    reczne = _reczne(baza)
    wiersze = baza.wiersze("SELECT id, projekt_id, plik_w_raporcie, krazek, wspolczynnik, data, zrodlo FROM frezowania "
                           "WHERE plik_w_raporcie IS NOT NULL AND data >= ? AND data <= ? ORDER BY id", (pierwsza, ostatnia))
    wpisy: list[Wpis] = []
    lz = {"wierszy": len(wiersze), "wpisow": 0, "brakujace": 0, "niejednoznaczne": 0, "bez_wspolczynnika": 0,
          "krazki_bez_wspolczynnika": [], "bez_sha16": 0, "bez_cech": 0, "sha16_z_kilkoma_wspolczynnikami": 0}
    krazki_bez: set[str] = set()
    for f in wiersze:
        data = dt.date.fromisoformat(f["data"])
        znaleziony, kandydatow = indeks.znajdz(f["plik_w_raporcie"], data)
        lz["niejednoznaczne"] += kandydatow > 1
        projekt = indeks.po_id.get(f["projekt_id"]) or znaleziony  # zapisane powiazanie ma pierwszenstwo, gdy projekt jest w indeksie
        if projekt is None:
            lz["brakujace"] += 1
            continue
        if not projekt["sha16"]:
            lz["bez_sha16"] += 1
            continue
        if f["wspolczynnik"] is not None:
            w, zrodlo = float(f["wspolczynnik"]), f["zrodlo"] or W.ZRODLO_CSV
        elif f["krazek"] in reczne:
            w, zrodlo = float(reczne[f["krazek"]]["wspolczynnik"]), W.ZRODLO_RECZNY
        elif wspolczynnik_awaryjny is not None:
            w, zrodlo = float(wspolczynnik_awaryjny), ZRODLO_AWARYJNY
        else:
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
                 granica_doby_godz: int = GRANICA_DOBY_GODZ) -> Pula:
    """Pula poranna (opis w naglowku modulu): punkty pracy zlecen zmienionych od poczatku okna, wspolczynnik 1,0."""
    teraz = teraz or dt.datetime.now()
    if not isinstance(dni_robocze, int) or dni_robocze < 0:
        raise ValueError(f"pula poranna: liczba dni roboczych musi byc >= 0 (jest {dni_robocze!r}; [match] pula_rano_dni_roboczych)")
    doba = doba_robocza(teraz, granica_doby_godz)
    od = max(_poczatek_doby(poczatek_dni_roboczych(doba, dni_robocze), granica_doby_godz), teraz - dt.timedelta(days=usun_po_dniach))
    od = od.replace(microsecond=0)
    wiersze = baza.wiersze("SELECT p.id, p.sha16, p.zeby, p.typ, p.zlecenie_id, z.kuweta FROM projekty p JOIN zlecenia z ON z.id = p.zlecenie_id "
                           "WHERE z.usuniety = 0 AND p.usuniety = 0 AND z.mtime >= ? ORDER BY p.id", (od.timestamp(),))
    wpisy = [Wpis(sha16=w["sha16"], wspolczynnik=1.0, krazek=None, frezowanie_id=None, projekt_id=w["id"], kuweta=w["kuweta"],
                  zeby=w["zeby"], typ=w["typ"], zrodlo_wspolczynnika=ZRODLO_RANO) for w in wiersze if w["sha16"]]
    pula = Pula(TRYB_RANO, doba.isoformat(), od.isoformat(), teraz.replace(microsecond=0).isoformat(), wpisy)
    z_cechami = _z_cechami(baza, pula.sha16()) if wpisy else set()
    pula.liczniki = {"wpisow": len(wpisy), "zlecen": len({w["zlecenie_id"] for w in wiersze if w["sha16"]}),
                     "bez_sha16": sum(not w["sha16"] for w in wiersze), "bez_cech": sum(w.sha16 not in z_cechami for w in wpisy),
                     "bez_kuwety": sum(w.kuweta is None for w in wpisy)}
    return pula


def krazki(baza: B.Baza, teraz: dt.datetime | None = None, *, dni: int = DNI_WIECZOR, granica_doby_godz: int = GRANICA_DOBY_GODZ) -> list[dict]:
    """Krazki z okna puli wieczornej (wiersze z plikiem i wpisy reczne z tych dob) - lista do wpisu recznego wspolczynnika.

    Pola: ``krazek``, ``plikow`` (wiersze z plikiem w oknie), ``plikow_bez_wspolczynnika``, ``wspolczynniki_csv`` (rozne wartosci
    z wierszy), ``wspolczynnik_reczny`` / ``data_recznego`` / ``frezowanie_reczne_id`` (obowiazujacy wpis reczny, z dowolnego
    dnia), ``brakuje`` (sa pliki bez wspolczynnika, a wpisu recznego nie ma). Kolejnosc: oznaczenie krazka.
    """
    teraz = teraz or dt.datetime.now()
    _, _, _, pierwsza, ostatnia = _okno_wieczoru(teraz, dni, granica_doby_godz)
    reczne = _reczne(baza)
    wynik: dict[str | None, dict] = {}

    def pozycja(k: str | None) -> dict:
        if k not in wynik:
            r = reczne.get(k) if k is not None else None
            wynik[k] = {"krazek": k, "plikow": 0, "plikow_bez_wspolczynnika": 0, "wspolczynniki_csv": set(),
                        "wspolczynnik_reczny": r["wspolczynnik"] if r else None, "data_recznego": r["data"] if r else None,
                        "frezowanie_reczne_id": r["id"] if r else None}
        return wynik[k]

    for f in baza.wiersze("SELECT krazek, wspolczynnik, plik_w_raporcie FROM frezowania WHERE data >= ? AND data <= ? ORDER BY id",
                          (pierwsza, ostatnia)):
        p = pozycja(f["krazek"])
        if f["plik_w_raporcie"] is None:
            continue  # wpis reczny tej doby: krazek na liscie
        p["plikow"] += 1
        if f["wspolczynnik"] is None:
            p["plikow_bez_wspolczynnika"] += 1
        else:
            p["wspolczynniki_csv"].add(round(float(f["wspolczynnik"]), 4))
    lista = []
    for k in sorted(wynik, key=lambda k: (k is None, k or "")):
        p = wynik[k]
        p["wspolczynniki_csv"] = sorted(p["wspolczynniki_csv"])
        p["brakuje"] = p["plikow_bez_wspolczynnika"] > 0 and p["wspolczynnik_reczny"] is None
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

    ``odswiez(teraz)``: indeks folderow + plik CSV wspolczynnikow (jesli jest) + powiazanie wierszy frezowania z indeksem;
    zwraca liczby (bez nazw), zly CSV nie przerywa odswiezenia (``csv_plik = "blad"``, ``csv_blad`` = komunikat z numerami
    linii). Pozostale metody jak funkcje modulu z parametrami z ustawien. Odswiezenie trwa (cechy nowych plikow) - w programie
    okienkowym w watku roboczym, z obiektem utworzonym w tym watku (``z_ustawien``: wlasne polaczenie z baza).
    """

    def __init__(self, baza: B.Baza, zrodla: dict[str, str | Path | None], *, plik_csv: str | Path | None = None,
                 dni_wieczor: int = DNI_WIECZOR, dni_rano: int = DNI_RANO, usun_po_dniach: int = USUN_PO_DNIACH,
                 granica_doby_godz: int = GRANICA_DOBY_GODZ, wspolczynnik_awaryjny: float | None = None, licz_cechy: bool = True,
                 wlasna_baza: bool = False):
        self.baza = baza
        self.zrodla = dict(zrodla)
        self.plik_csv = Path(plik_csv) if plik_csv is not None else None
        self.dni_wieczor = dni_wieczor
        self.dni_rano = dni_rano
        self.usun_po_dniach = usun_po_dniach
        self.granica_doby_godz = granica_doby_godz
        self.wspolczynnik_awaryjny = wspolczynnik_awaryjny
        self.licz_cechy = licz_cechy
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
        r = I.indeksuj(self.baza, self.zrodla, teraz, usun_po_dniach=self.usun_po_dniach, licz_cechy=self.licz_cechy)
        wynik = {"indeks": r.do_slownika(), "csv_plik": None, "csv": None, "csv_blad": None, "powiazanie": None}
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
        wynik["powiazanie"] = W.powiaz_frezowania(self.baza).do_slownika()
        return wynik

    def pula_wieczorna(self, teraz: dt.datetime | None = None) -> Pula:
        return pula_wieczorna(self.baza, teraz, dni=self.dni_wieczor, granica_doby_godz=self.granica_doby_godz,
                              wspolczynnik_awaryjny=self.wspolczynnik_awaryjny)

    def pula_poranna(self, teraz: dt.datetime | None = None) -> Pula:
        return pula_poranna(self.baza, teraz, dni_robocze=self.dni_rano, usun_po_dniach=self.usun_po_dniach,
                            granica_doby_godz=self.granica_doby_godz)

    def krazki(self, teraz: dt.datetime | None = None) -> list[dict]:
        return krazki(self.baza, teraz, dni=self.dni_wieczor, granica_doby_godz=self.granica_doby_godz)

    def wpisz_wspolczynnik(self, krazek: str, wspolczynnik, *, zmien: bool = False, data: str | dt.date | None = None,
                           teraz: dt.datetime | None = None) -> int:
        return W.wpisz_reczny(self.baza, krazek, wspolczynnik, zmien=zmien, data=data, teraz=teraz, granica_doby_godz=self.granica_doby_godz)

    def wspolczynnik_krazka(self, krazek: str) -> dict | None:
        return W.wspolczynnik_krazka(self.baza, krazek)

    def sciezki(self, wpisy) -> dict[int, Path]:
        """Sciezki plikow do wczytania (DANE OSOBOWE - patrz ``sciezki_plikow``)."""
        return sciezki_plikow(self.baza, wpisy, self.zrodla)
