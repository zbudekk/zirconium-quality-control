"""silnik - analiza skanu (``porownaj.porownaj``) w OSOBNYM PROCESIE: kolejka zadan, postep, obsluga awarii (paczka E3-A2).

Po co: Open3D uruchomione w watku pod Qt zawisa (okno testowe: 195 s bez wyniku, raporty/P3a_przekazanie.md pkt 5.1),
wiec proces okna nie moze liczyc. ``Silnik`` trzyma jeden proces roboczy (``multiprocessing``, metoda ``spawn``), wysyla mu
zadania po jednym, odbiera postep i wynik, a po awarii (wyjatek analizy, zabity proces, przekroczony limit czasu) zglasza
blad tego zadania, w razie potrzeby uruchamia proces od nowa i bierze nastepne zadanie. Ten modul na poziomie importu
uzywa tylko biblioteki standardowej - numpy, trimesh i Open3D laduje wylacznie proces roboczy.

Kontrakty (plan etapu 3, sekcja 3.8):
* ``ZadanieAnalizy`` - skan, tryb (wieczor / rano), uklad (``auto`` = rozpoznaj; zalozenie Z2), numer plytki albo brak,
  opis puli (``OpisPuli``: foldery projektow, wspolczynnik albo None = domyslny dla rozpoznanej plytki);
* wynik - slownik zwracany przez ``porownaj.porownaj`` w postaci z pliku ``<skan>_wynik.json`` (lacznie z ``ostrzezenia``,
  jak w wierszu polecen) + ``zadanie_id`` + ``skan_sha16`` (skrot tresci FAKTYCZNIE analizowanej);
* ``ZdarzenieSilnika`` - ``gotowy`` / ``start`` / ``postep`` / ``wynik`` / ``blad`` (``rodzaj``: ``analiza``, ``proces``,
  ``limit_czasu``, ``start``, ``plik_zmieniony``) / ``zatrzymany`` (``niezakonczone``: zadania przerwane przez ``stop()``).

Plik skanu zmieniony po zdarzeniu (nadpisany, gdy zadanie czekalo w kolejce, albo w trakcie analizy): skrot sprawdzany
przed analiza i po niej; niezgodnosc = ``blad`` rodzaju ``plik_zmieniony`` bez wyniku - nowa tresc ma wlasne zdarzenie
ze ``scanner``. Teksty wychodzace z procesu roboczego (ostrzezenia, uwagi, bledy, pliki w ``wyjscie``) sa czyszczone
z nazw plikow i folderow puli projektow (``CzyscicielNazw``: nazwiska). Proces roboczy pilnuje sie sam (``Straznik``):
konczy sie w ok. 1 s po zniknieciu procesu okna (takze w trakcie analizy) i po przekroczeniu limitu zadania z zapasem.

Uzycie:
    s = Silnik(na_zdarzenie=funkcja)      # funkcja wolana w watku nadzorcy (zwykly watek Pythona, bez Open3D i bez Qt)
    s.start()
    nr = s.zlec(ZadanieAnalizy(skan=plik, pula=OpisPuli(foldery=(folder,))))   # albo s.zlec_skan(zdarzenie_skanu, pula)
    ... niezakonczone = s.stop()          # zadania w toku i w kolejce - do ponownego zlecenia po starcie programu
Bez ``na_zdarzenie`` zdarzenia trafiaja do kolejki ``s.zdarzenia``. W oknie Qt: ``lacznik_qt(s)`` zamienia je na sygnaly
emitowane w watku okna (zegar Qt oproznia kolejke). Program uruchamiajacy silnik musi miec glowny modul chroniony przez
``if __name__ == "__main__":`` (wymaganie ``multiprocessing`` na Windows), a ten plik startowy nie moze importowac Qt na
poziomie modulu: proces roboczy wykonuje go ponownie (jako ``__mp_main__``) i zaladowalby Qt obok Open3D (D8).

Pula projektow zostaje w pamieci procesu roboczego miedzy zadaniami (``PamiecPul``): budowana raz na (foldery,
wspolczynnik, orientacja, lista plikow w folderach), od nowa po zmianie plikow w folderze.
"""
from __future__ import annotations

import collections
import dataclasses
import hashlib
import importlib
import json
import logging
import multiprocessing
import os
import queue
import re
import sys
import threading
import time
import traceback
import warnings
from pathlib import Path

LOG = logging.getLogger(__name__)

FUNKCJA_ANALIZY = "stanowisko.porownaj:porownaj"  # "modul:funkcja" o sygnaturze porownaj.porownaj
LIMIT_ZADANIA_S = 600.0  # analiza dluzsza niz to = proces zabity, blad "limit_czasu", nastepne zadanie
LIMIT_STARTU_S = 180.0  # proces roboczy, ktory nie zglosi gotowosci w tym czasie, jest zabijany
PUL_W_PAMIECI = 2  # np. pula wieczorna (wspolczynnik krazka) i poranna (1,0)
OKRES_S = 0.02  # co ile nadzorca zaglada do lacza z procesem
RODZAJE_BLEDU = ("analiza", "proces", "limit_czasu", "start", "plik_zmieniony")
ZNACZNIK_PULI = "<projekt>"  # w miejsce sciezki albo nazwy z puli projektow; nazwa pliku z puli -> "<projekt sha16>"
POLA_BEZ_CZYSZCZENIA = ("foldery_projektow",)  # pola wyniku, ktorych CzyscicielNazw nie rusza (foldery puli z zadania)
ZAPAS_LIMITU_S = 30.0  # proces roboczy konczy sie sam po limit_zadania_s + tyle (nadzorcy moze juz nie byc)
OKRES_STRAZNIKA_S = 0.5  # co ile straznik w procesie roboczym sprawdza proces okna i czas zadania
KOD_BEZ_PROCESU_OKNA = 91  # kod wyjscia procesu roboczego: zniknal proces okna
KOD_LIMIT_ZADANIA = 92  # kod wyjscia procesu roboczego: zadanie przekroczylo limit (z zapasem)


@dataclasses.dataclass(frozen=True)
class OpisPuli:
    """Z czego silnik buduje pule projektow. ``wspolczynnik`` None = domyslny dla rozpoznanego typu plytki (jak w wierszu
    polecen). ``wspolczynniki`` (opcjonalnie): skrot projektu -> wspolczynnik pojedynczej pracy (``match.Pula``)."""

    foldery: tuple
    wspolczynnik: float | None = None
    orientacja: str = "auto"
    wspolczynniki: dict | None = None


@dataclasses.dataclass(frozen=True)
class ZadanieAnalizy:
    skan: Path
    pula: OpisPuli
    tryb: str = "wieczor"  # wieczor / rano - dla odbiorcy wyniku (sesja); analiza od trybu nie zalezy
    uklad: str = "auto"  # "auto" albo "rozpoznaj" = program rozpoznaje uklad; inaczej nazwa ukladu z [plytki]
    numer: int | None = None  # numer plytki, gdy dolki kodu sa poza skanem
    skan_sha16: str | None = None  # z ZdarzenieSkanu; None = silnik policzy sam
    inspekcja: bool = True
    bez_filtru: bool = False
    straznik: bool = True
    wyjscie: Path | None = None  # folder na <czas>_<sha16>_<skan>_wynik.json i ..._podglad.npz (punkty i odchylki gniazd)
    zadanie_id: int = 0  # nadaje Silnik.zlec
    przyjete: float | None = None  # czas przyjecia zadania (time.time()) - nadaje Silnik.zlec; poczatek nazw plikow w wyjscie


@dataclasses.dataclass(frozen=True)
class ZdarzenieSilnika:
    typ: str  # gotowy | start | postep | wynik | blad | zatrzymany
    czas: float  # time.time()
    zadanie_id: int | None = None
    zadanie: ZadanieAnalizy | None = None
    etap: str = ""  # postep: nazwa etapu z porownaj
    udzial: float = 0.0  # postep: 0-1
    wynik: dict | None = None
    pliki: dict | None = None  # wynik: sciezki plikow zapisanych w ``wyjscie`` (klucze: wynik, podglad)
    rodzaj: str = ""  # blad: jeden z RODZAJE_BLEDU
    blad: str = ""  # blad: komunikat jednym zdaniem
    szczegoly: str = ""  # blad: slad wyjatku z procesu roboczego (do logu, nie dla technika)
    czas_s: float | None = None  # wynik / blad: ile trwalo zadanie od wyslania do procesu
    niezakonczone: tuple = ()  # zatrzymany: zadania niezakonczone (w toku pierwsze, potem kolejka) - do ponownego zlecenia


# ----------------------------------------------------------------------------
# proces roboczy
# ----------------------------------------------------------------------------
def bez_nazw_z_puli(tekst: str, foldery) -> str:
    """Usuwa z komunikatu sciezki plikow lezacych w folderach puli (nazwy folderow zlecen i plikow zawieraja nazwiska -
    nie moga wyjsc do logow ani na ekran; plan etapu 3, wymaganie K10): sciezka -> ``<projekt>``. Sama sciezka folderu
    puli zostaje. Gole nazwy plikow i folderow (bez sciezki) czysci ``CzyscicielNazw``."""
    for f in foldery:
        f = str(f).rstrip("\\/")
        if not f:
            continue
        warianty = {f, f.replace("\\", "/"), f.replace("/", "\\"), f.replace("\\", "\\\\"), f.replace("/", "\\\\")}
        for w in sorted(warianty, key=len, reverse=True):
            tekst = re.sub(re.escape(w) + r"[\\/]+[^'\"\n;|<>]*", lambda m: ZNACZNIK_PULI, tekst, flags=re.IGNORECASE)
    return tekst


def _liter(s: str) -> int:
    return sum(1 for c in s if c.isalpha())


class CzyscicielNazw:
    """Czysci teksty wychodzace z procesu roboczego z nazw z puli projektow (P5, wymaganie K10 - nazwy plikow i folderow
    zlecen zawieraja nazwiska; poza baza tylko sha16).

    * pelna sciezka pod folderem puli -> ``<projekt>`` (``bez_nazw_z_puli``);
    * sama nazwa pliku z puli (z rozszerzeniem albo bez) -> ``<projekt sha16>`` (skrot zawartosci, jak ``synth.skrot_pliku``;
      liczony dopiero, gdy nazwa wystapi w tekscie); nazwa wspolna dla kilku plikow -> ``<projekt>``;
    * nazwa folderu w puli -> ``<projekt>``.
    Nazwy dopasowywane bez rozrozniania wielkosci liter i tylko w calosci (nie jako czesc dluzszej nazwy). Zostaja: sam
    folder puli z zadania, nazwy folderow z mniej niz 2 literami (np. numer kuwety ``12``) i rdzenie nazw plikow krotsze niz
    3 znaki albo z mniej niz 2 literami (nie sa danymi osobowymi, a ich zamiana psulaby liczby i zwykle slowa).
    ``pomin`` - pliki, ktorych nazw nie ruszac (skan zadania, gdy lezy w folderze puli). Wywolanie ``czysciciel(tekst)``;
    ``czysciciel.oczysc(struktura_json)`` - kopia z oczyszczonymi tekstami (klucze i liczby bez zmian, pola
    ``POLA_BEZ_CZYSZCZENIA`` bez zmian)."""

    def __init__(self, foldery, pomin=()):
        self.foldery: list[str] = []
        self._mapa: dict[str, Path | None] = {}  # nazwa malymi literami -> plik (None = folder albo nazwa niejednoznaczna)
        self._skroty: dict[Path, str] = {}
        self._wzor = None
        try:
            self.foldery = [str(f) for f in foldery if str(f)]
            pomijane = {os.path.normcase(os.path.abspath(str(p))) for p in pomin}
            for f in self.foldery:
                korzen = Path(f)
                try:
                    wpisy = list(korzen.rglob("*")) if korzen.is_dir() else []
                except OSError:
                    wpisy = []
                for p in wpisy:
                    try:
                        plik = p.is_file()
                    except OSError:
                        continue
                    if plik:
                        if os.path.normcase(os.path.abspath(str(p))) in pomijane:
                            continue
                        self._dodaj(p.name, p)
                        if len(p.stem) >= 3 and _liter(p.stem) >= 2:
                            self._dodaj(p.stem, p)
                    elif _liter(p.name) >= 2:
                        self._dodaj(p.name, None)
            if self._mapa:
                nazwy = sorted(self._mapa, key=len, reverse=True)
                self._wzor = re.compile(r"(?<![\w\-.])(?:" + "|".join(re.escape(n) for n in nazwy) + r")(?![\w\-]|\.\w)", re.IGNORECASE)
        except Exception:  # noqa: BLE001 - zostaje samo czyszczenie sciezek; analiza nie moze sie o to wywrocic
            self._mapa, self._wzor = {}, None

    def _dodaj(self, nazwa: str, cel: Path | None) -> None:
        k = nazwa.lower()
        self._mapa[k] = None if (k in self._mapa and self._mapa[k] != cel) else cel

    def _zamien(self, m) -> str:
        cel = self._mapa.get(m.group(0).lower())
        if cel is None:
            return ZNACZNIK_PULI
        s = self._skroty.get(cel)
        if s is None:
            try:
                s = _skrot16(cel)
            except OSError:
                s = ""
            self._skroty[cel] = s
        return f"<projekt {s}>" if s else ZNACZNIK_PULI

    def __call__(self, tekst):
        if not isinstance(tekst, str) or not tekst:
            return tekst
        tekst = bez_nazw_z_puli(tekst, self.foldery)
        return self._wzor.sub(self._zamien, tekst) if self._wzor is not None else tekst

    def oczysc(self, o):
        if isinstance(o, str):
            return self(o)
        if isinstance(o, dict):
            return {k: (v if k in POLA_BEZ_CZYSZCZENIA else self.oczysc(v)) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [self.oczysc(v) for v in o]
        return o


class PlikZmieniony(Exception):
    """Tresc pliku skanu nie jest ta, ktorej dotyczy zadanie (P1) - wynik nie moze dostac cudzego skrotu."""


def _zakoncz_proces(kod: int) -> None:
    """Natychmiastowy koniec procesu roboczego, bez sprzatania bibliotek (watek analizy moze byc w srodku Open3D)."""
    try:
        sys.stderr.write(f"silnik: proces roboczy konczy sie sam (kod {kod})\n")
        sys.stderr.flush()
    except Exception:  # noqa: BLE001
        pass
    if os.name == "nt":
        try:
            import ctypes

            k32 = ctypes.WinDLL("kernel32", use_last_error=True)
            k32.GetCurrentProcess.restype = ctypes.c_void_p
            k32.TerminateProcess.argtypes = [ctypes.c_void_p, ctypes.c_uint]
            k32.TerminateProcess(k32.GetCurrentProcess(), kod)
        except Exception:  # noqa: BLE001
            pass
    os._exit(kod)


class Straznik:
    """Pilnuje procesu roboczego od srodka (P6). Proces okna zabity twardo (Menedzer zadan, awaria Qt) nie zamyka lacza
    w trakcie analizy, a limitu czasu pilnuje nadzorca, ktorego juz nie ma - wiec proces roboczy sam: konczy sie, gdy
    zniknie proces okna (``rodzic_zyje()`` False) albo gdy zadanie trwa dluzej niz ``limit_zadania_s`` + ``ZAPAS_LIMITU_S``.
    ``sprawdz()`` - jedno sprawdzenie; ``uruchom()`` - watek sprawdzajacy co ``OKRES_STRAZNIKA_S``."""

    def __init__(self, rodzic_zyje, limit_zadania_s: float | None = LIMIT_ZADANIA_S, zakoncz=_zakoncz_proces, zegar=time.monotonic):
        self.rodzic_zyje, self.limit_zadania_s, self.zakoncz, self.zegar = rodzic_zyje, limit_zadania_s, zakoncz, zegar
        self._od: float | None = None

    def poczatek_zadania(self) -> None:
        self._od = self.zegar()

    def koniec_zadania(self) -> None:
        self._od = None

    def sprawdz(self) -> None:
        if not self.rodzic_zyje():
            self.zakoncz(KOD_BEZ_PROCESU_OKNA)
            return
        od, limit = self._od, self.limit_zadania_s
        if od is not None and limit is not None and self.zegar() - od > limit + ZAPAS_LIMITU_S:
            self.zakoncz(KOD_LIMIT_ZADANIA)

    def uruchom(self, okres_s: float = OKRES_STRAZNIKA_S) -> threading.Thread:
        def petla() -> None:
            while True:
                try:
                    self.sprawdz()
                except Exception:  # noqa: BLE001 - straznik nie moze sie skonczyc
                    pass
                time.sleep(okres_s)

        w = threading.Thread(target=petla, name="silnik-straznik", daemon=True)
        w.start()
        return w


class PamiecPul:
    """Pule projektow trzymane w procesie roboczym miedzy zadaniami (budowa puli to sekundy, plytek jest kilkanascie dziennie)."""

    def __init__(self, limit: int = PUL_W_PAMIECI):
        self.limit = max(1, limit)
        self._pule: collections.OrderedDict = collections.OrderedDict()

    def __len__(self) -> int:
        return len(self._pule)

    def dla(self, opis: OpisPuli):
        """Funkcja ``pula_dla(wspolczynnik) -> match.Pula`` dla ``porownaj``."""

        def pula_dla(w: float):
            from . import match as M
            from . import synth as S

            foldery = [Path(f) for f in opis.foldery]
            h = hashlib.sha256()
            for f in foldery:  # lista plikow projektow: zmiana w folderze = nowa pula
                for p in S.pliki_projektow(f):
                    st = p.stat()
                    h.update(f"{p.relative_to(f).as_posix()}|{st.st_size}|{st.st_mtime_ns}\n".encode("utf-8"))
            klucz = (tuple(str(f) for f in foldery), round(float(w), 9), opis.orientacja,
                     tuple(sorted((opis.wspolczynniki or {}).items())), h.hexdigest())
            if klucz in self._pule:
                self._pule.move_to_end(klucz)
                return self._pule[klucz]
            pula = M.Pula(foldery, w, opis.orientacja, opis.wspolczynniki) if opis.wspolczynniki else M.Pula(foldery, w, opis.orientacja)
            self._pule[klucz] = pula
            while len(self._pule) > self.limit:
                self._pule.popitem(last=False)
            return pula

        return pula_dla


def _wczytaj_funkcje(nazwa: str):
    modul, _, funkcja = nazwa.partition(":")
    return getattr(importlib.import_module(modul), funkcja)


def _skrot16(plik: Path) -> str:
    h = hashlib.sha256()
    with open(plik, "rb") as f:
        for blok in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(blok)
    return h.hexdigest()[:16]


def wczytaj_podglad(plik) -> dict:
    """Plik ``..._podglad.npz`` z silnika -> {numer gniazda: (punkty N x 3 w ukladzie plytki, odchylka kazdego punktu w mm)}."""
    import numpy as np

    with np.load(plik) as z:
        return {int(k[1:-2]): (z[k], z[k[:-2] + "_d"]) for k in z.files if k.endswith("_P")}


def _bezpieczna_nazwa(s: str, dlugosc: int = 60) -> str:
    """Nazwa pliku z dowolnego tekstu: litery ASCII, cyfry, kropka, myslnik, podkreslenie."""
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("._")
    return s[:dlugosc] or "skan"


def _zapisz_bez_nadpisania(cel: Path, zapisz) -> None:
    """Zapis przez plik tymczasowy i zmiane nazwy, ktora NIE nadpisuje istniejacego pliku (wtedy ``FileExistsError``):
    urwany zapis nie zostawia polowy pliku pod docelowa nazwa, a plik innego zadania nie moze zostac zastapiony."""
    tmp = cel.with_name(f"{cel.name}.{os.getpid()}.tmp")
    try:
        with open(tmp, "wb") as f:
            zapisz(f)
        if os.name == "nt":
            os.rename(tmp, cel)  # Windows: zmiana nazwy nigdy nie nadpisuje istniejacego pliku
        else:
            os.link(tmp, cel)
            os.unlink(tmp)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _zapisz_wyjscie(zadanie: ZadanieAnalizy, wynik: dict, podglad: dict) -> dict:
    """P4: pliki unikalne na zadanie - ``<czas przyjecia>_<sha16>_<bezpieczna nazwa skanu>[_n]_wynik.json`` i ``..._podglad.npz``
    (ten sam rdzen); istniejacy plik nigdy nie jest nadpisywany (kolejny wolny numer ``_n``)."""
    import numpy as np

    wyj = Path(zadanie.wyjscie)
    wyj.mkdir(parents=True, exist_ok=True)
    czas = time.strftime("%Y%m%d_%H%M%S", time.localtime(zadanie.przyjete if zadanie.przyjete is not None else time.time()))
    baza = f"{czas}_{wynik['skan_sha16']}_{_bezpieczna_nazwa(Path(zadanie.skan).stem)}"
    tablice = {}
    for gniazdo, wi in podglad.items():
        P, d = getattr(wi, "_P", None), getattr(wi, "_d", None)
        if gniazdo is None or P is None or d is None:
            continue
        tablice[f"g{int(gniazdo)}_P"] = np.asarray(P, dtype=np.float32)
        tablice[f"g{int(gniazdo)}_d"] = np.asarray(d, dtype=np.float32)
    dane = json.dumps(wynik, ensure_ascii=False, indent=1).encode("utf-8")
    for n in range(1, 10000):
        rdzen = baza if n == 1 else f"{baza}_{n}"
        p_json, p_npz = wyj / f"{rdzen}_wynik.json", wyj / f"{rdzen}_podglad.npz"
        if p_json.exists() or p_npz.exists():
            continue
        try:
            _zapisz_bez_nadpisania(p_json, lambda f: f.write(dane))
        except FileExistsError:
            continue
        pliki = {"wynik": str(p_json)}
        if tablice:
            _zapisz_bez_nadpisania(p_npz, lambda f: np.savez(f, **tablice))
            pliki["podglad"] = str(p_npz)
        return pliki
    raise FileExistsError(f"brak wolnej nazwy pliku wyniku {baza} w folderze wyjscia")


def _wykonaj(zadanie: ZadanieAnalizy, funkcja, ust: dict, pamiec: PamiecPul, lacze, czysc: CzyscicielNazw) -> tuple[dict, dict | None]:
    skan = Path(zadanie.skan)
    if not skan.is_file():
        raise FileNotFoundError(f"brak pliku skanu {skan.name}")
    sha16 = _skrot16(skan)  # P1: skrot tresci, ktora za chwile przeczyta analiza
    if zadanie.skan_sha16 and sha16 != zadanie.skan_sha16:
        raise PlikZmieniony(f"plik skanu zmienil sie, zanim analiza ruszyla (zdarzenie: sha16 {zadanie.skan_sha16}, plik teraz: sha16 {sha16}) - "
                            "analiza pominieta; nowa tresc ma wlasne zdarzenie skanu")
    uklad = "auto" if zadanie.uklad in (None, "", "auto", "rozpoznaj") else zadanie.uklad
    foldery = [Path(f) for f in zadanie.pula.foldery]
    podglad: dict | None = {} if zadanie.wyjscie is not None else None

    def postep(etap, udzial) -> None:
        lacze.send(("postep", zadanie.zadanie_id, str(etap), float(udzial)))

    with warnings.catch_warnings(record=True) as ostrz:  # jak w wierszu polecen: ostrzezenia trafiaja do wyniku
        warnings.simplefilter("always")
        wynik = funkcja(skan, foldery, uklad, ust, zadanie.pula.wspolczynnik, zadanie.numer, zadanie.pula.orientacja, zadanie.bez_filtru, None,
                        inspekcja=zadanie.inspekcja, podglad=podglad, postep=postep, straznik=zadanie.straznik,
                        pula_dla=pamiec.dla(zadanie.pula), kontekst={})
    try:
        po = _skrot16(skan)
    except OSError:
        po = None
    if po != sha16:  # nie wiadomo, ktora tresc przeczytala analiza: wyniku nie przypisujemy zadnej
        raise PlikZmieniony(f"plik skanu zmienil sie w trakcie analizy (sha16 {sha16} -> {po or 'brak pliku'}) - wynik odrzucony; "
                            "nowa tresc ma wlasne zdarzenie skanu")
    if not isinstance(wynik, dict):
        raise TypeError(f"funkcja analizy zwrocila {type(wynik).__name__}, oczekiwany slownik")
    wynik = dict(wynik)
    wynik["ostrzezenia"] = [str(o.message) for o in ostrz]
    wynik = json.loads(json.dumps(wynik, ensure_ascii=False))  # postac jak w <skan>_wynik.json: same typy JSON
    wynik = czysc.oczysc(wynik)  # P5: bez nazw plikow i folderow puli (ostrzezenia "pomijam projekt ...", uwagi, bledy inspekcji)
    wynik["zadanie_id"] = zadanie.zadanie_id
    wynik["skan_sha16"] = sha16
    pliki = _zapisz_wyjscie(zadanie, wynik, podglad or {}) if zadanie.wyjscie is not None else None
    return wynik, pliki


def _robotnik(lacze, ust: dict | None, plik_ustawien, funkcja: str, pul_w_pamieci: int, plik_logu, pamiec_linii=None,
              limit_zadania_s: float | None = LIMIT_ZADANIA_S) -> None:
    """Cialo procesu roboczego: laduje ustawienia i funkcje analizy, potem wykonuje zadania z lacza, jedno naraz."""
    rodzic = multiprocessing.parent_process()
    straznik = Straznik(rodzic.is_alive if rodzic is not None else (lambda: True), limit_zadania_s)
    straznik.uruchom()  # P6: od pierwszej chwili - takze w trakcie ladowania bibliotek i w trakcie analizy
    if plik_logu is not None:
        try:  # wszystko, co biblioteki wypisuja (takze z C++), trafia do pliku; bez pliku zostaje wyjscie odziedziczone
            log = open(plik_logu, "ab", buffering=0)
            os.dup2(log.fileno(), 1)
            os.dup2(log.fileno(), 2)
            sys.stdout = open(1, "w", encoding="utf-8", errors="replace", closefd=False, buffering=1)
            sys.stderr = open(2, "w", encoding="utf-8", errors="replace", closefd=False, buffering=1)
        except OSError:
            pass
    if sys.stdout is None or sys.stderr is None:  # pythonw: brak konsoli
        sys.stdout = sys.stderr = open(os.devnull, "w")
    try:
        f = _wczytaj_funkcje(funkcja)
        if ust is None:
            from . import ustawienia as UST

            ust = UST.wczytaj_ustawienia(Path(plik_ustawien) if plik_ustawien is not None else None)
        if pamiec_linii is not None:  # linie brzegu projektow (P2) takze na dysku: przezywaja restart procesu i programu
            from . import krawedz as KR

            Path(pamiec_linii).mkdir(parents=True, exist_ok=True)
            KR.ustaw_katalog_pamieci(pamiec_linii)
        pamiec = PamiecPul(pul_w_pamieci)
    except BaseException as e:  # noqa: BLE001 - brak pakietu, zly plik ustawien: nadzorca dostaje komunikat
        try:
            lacze.send(("blad_startu", f"{type(e).__name__}: {e}", traceback.format_exc()))
        except OSError:
            pass
        return
    lacze.send(("gotowy", os.getpid()))
    while True:
        try:
            wiadomosc = lacze.recv()
        except (EOFError, OSError):
            return  # proces okna zniknal
        if wiadomosc[0] == "koniec":
            return
        zadanie: ZadanieAnalizy = wiadomosc[1]
        straznik.poczatek_zadania()
        czysc = CzyscicielNazw(zadanie.pula.foldery, pomin=(zadanie.skan,))  # lista plikow puli: nazwy do usuniecia z tekstow
        try:
            wynik, pliki = _wykonaj(zadanie, f, ust, pamiec, lacze, czysc)
            odpowiedz = ("wynik", zadanie.zadanie_id, wynik, pliki)
        except KeyboardInterrupt:
            return
        except PlikZmieniony as e:
            odpowiedz = ("blad", zadanie.zadanie_id, czysc(str(e)), "", "plik_zmieniony")
        except BaseException as e:  # noqa: BLE001 - takze SystemExit z porownaj ("brak projektow STL"); proces pracuje dalej
            odpowiedz = ("blad", zadanie.zadanie_id, czysc(f"{type(e).__name__}: {e}"), czysc(traceback.format_exc()), "analiza")
        finally:
            straznik.koniec_zadania()
        try:
            lacze.send(odpowiedz)
        except OSError:
            return


# ----------------------------------------------------------------------------
# nadzorca w procesie okna
# ----------------------------------------------------------------------------
class Silnik:
    """Kolejka analiz wykonywanych w jednym procesie roboczym, jedna naraz, w kolejnosci zlecen.

    ``ust`` - slownik ustawien przekazany do procesu; None = proces sam wczyta ``plik_ustawien`` (None = ``ustawienia.toml``
    programu, jak wiersz polecen). ``funkcja`` - ``"modul:funkcja"`` analizy (domyslnie ``porownaj.porownaj``).
    ``limit_zadania_s`` - najdluzszy czas jednej analizy. ``plik_logu`` - dokad proces roboczy wypisuje to, co biblioteki
    drukuja na ekran. ``pamiec_linii`` - katalog pamieci podrecznej linii brzegu projektow (``krawedz.ustaw_katalog_pamieci``;
    None = tylko pamiec procesu, na dysk nic nie trafia). ``na_zdarzenie`` - funkcja wolana z kazdym ``ZdarzenieSilnika``
    w watku nadzorcy.
    """

    def __init__(self, ust: dict | None = None, plik_ustawien=None, *, funkcja: str = FUNKCJA_ANALIZY, limit_zadania_s: float = LIMIT_ZADANIA_S,
                 limit_startu_s: float = LIMIT_STARTU_S, pul_w_pamieci: int = PUL_W_PAMIECI, plik_logu=None, pamiec_linii=None,
                 na_zdarzenie=None):
        self.ust, self.plik_ustawien, self.funkcja = ust, plik_ustawien, funkcja
        self.limit_zadania_s, self.limit_startu_s, self.pul_w_pamieci, self.plik_logu = limit_zadania_s, limit_startu_s, pul_w_pamieci, plik_logu
        self.pamiec_linii = str(pamiec_linii) if pamiec_linii is not None else None
        self.na_zdarzenie = na_zdarzenie
        self.zdarzenia: queue.Queue = queue.Queue()  # ZdarzenieSilnika, gdy nie podano ``na_zdarzenie``
        self._ctx = multiprocessing.get_context("spawn")
        self._kolejka: collections.deque = collections.deque()
        self._zamek = threading.Lock()
        self._stop = threading.Event()
        self._watek: threading.Thread | None = None
        self._zatrzymany = False
        self._proces = None
        self._lacze = None
        self._gotowy = False
        self._start_procesu = 0.0
        self._biezace: ZadanieAnalizy | None = None
        self._biezace_od = 0.0
        self._nastepny_id = 1
        self._starty = 0
        self._nieudany_start: tuple | None = None  # (tekst, szczegoly) ostatniego nieudanego startu procesu
        self._po_stopie = False

    # --- sterowanie
    def start(self) -> None:
        if self._zatrzymany:
            raise RuntimeError("silnik zatrzymany - utworz nowy obiekt Silnik")
        if self._watek is None or not self._watek.is_alive():
            self._watek = threading.Thread(target=self._petla, name="silnik-nadzorca", daemon=True)
            self._watek.start()

    def stop(self, czekaj_s: float = 5.0) -> list:
        """Konczy prace: trwajaca analiza jest przerywana razem z procesem, kolejka oprozniana. Zwraca liste zadan
        niezakonczonych (``ZadanieAnalizy``: w toku pierwsze, potem kolejka) i zglasza ja zdarzeniem ``zatrzymany``
        (P2) - aplikacja zapisuje je i zleca ponownie po starcie. Zadne z nich nie dostaje zdarzenia ``wynik`` ani
        ``blad``. Zdarzenie ``zatrzymany`` jest wolane w watku wywolujacym ``stop()``. Kolejne wywolanie zwraca []."""
        with self._zamek:
            if self._po_stopie:
                return []
            self._po_stopie = True
        self._zatrzymany = True
        self._stop.set()
        if self._watek is not None:
            self._watek.join(czekaj_s)
            self._watek = None
        with self._zamek:
            biezace = self._biezace
            niezakonczone = ([biezace] if biezace is not None else []) + list(self._kolejka)
            self._kolejka.clear()
            self._biezace = None
        self._zamknij_proces(grzecznie=biezace is None)
        self._zglos("zatrzymany", niezakonczone=tuple(niezakonczone))
        return niezakonczone

    def __enter__(self) -> Silnik:
        self.start()
        return self

    def __exit__(self, *exc) -> None:
        self.stop()

    def dziala(self) -> bool:
        return self._watek is not None and self._watek.is_alive()

    @property
    def pid(self) -> int | None:
        """Numer procesu roboczego (None, gdy go nie ma)."""
        p = self._proces
        try:
            return p.pid if p is not None and p.is_alive() else None
        except ValueError:  # proces wlasnie zamkniety przez nadzorce
            return None

    def zlec(self, zadanie: ZadanieAnalizy) -> int:
        """Dodaje zadanie na koniec kolejki; zwraca ``zadanie_id`` (rosnace od 1 w kazdym obiekcie ``Silnik``) i ustawia
        ``przyjete`` (czas przyjecia). Zadanie z ``stop()`` innego obiektu mozna zlecic ponownie - dostanie nowy numer."""
        if self._zatrzymany:
            raise RuntimeError("silnik zatrzymany - zadanie nie zostalo przyjete")
        with self._zamek:
            nr = self._nastepny_id
            self._nastepny_id += 1
            self._kolejka.append(dataclasses.replace(zadanie, zadanie_id=nr, przyjete=time.time()))
        return nr

    def zlec_skan(self, zdarzenie, pula: OpisPuli, **pola) -> int:
        """Zadanie z ``scanner.ZdarzenieSkanu``: sciezka i skrot skanu ze zdarzenia, reszta pol jak w ``ZadanieAnalizy``.
        Skrot ze zdarzenia jest sprawdzany przed analiza i po niej (P1: plik nadpisany = ``blad`` ``plik_zmieniony``)."""
        return self.zlec(ZadanieAnalizy(skan=Path(zdarzenie.plik), pula=pula, skan_sha16=zdarzenie.sha16, **pola))

    def anuluj(self, zadanie_id: int) -> bool:
        """Usuwa z kolejki zadanie, ktore jeszcze nie ruszylo. Zadania w toku nie da sie anulowac."""
        with self._zamek:
            for z in self._kolejka:
                if z.zadanie_id == zadanie_id:
                    self._kolejka.remove(z)
                    return True
        return False

    def w_kolejce(self) -> int:
        return len(self._kolejka)

    def zajety(self) -> bool:
        return self._biezace is not None

    def czekaj_na_pusta_kolejke(self, limit_s: float) -> bool:
        """True, gdy kolejka jest pusta, a ostatnie zadanie zakonczone i zgloszone (D3); False po ``limit_s``."""
        t0 = time.monotonic()
        while True:
            with self._zamek:
                pusto = not self._kolejka and self._biezace is None
            if pusto:
                return True
            if time.monotonic() - t0 > limit_s:
                return False
            time.sleep(0.02)

    def stan(self) -> dict:
        b = self._biezace
        return {"dziala": self.dziala(), "proces_gotowy": self._gotowy, "pid": self.pid, "w_kolejce": len(self._kolejka),
                "biezace": b.zadanie_id if b is not None else None, "starty_procesu": self._starty}

    # --- nadzorca
    def _zglos(self, typ: str, **pola) -> None:
        z = ZdarzenieSilnika(typ=typ, czas=time.time(), **pola)
        if self.na_zdarzenie is None:
            self.zdarzenia.put(z)
            return
        try:
            self.na_zdarzenie(z)
        except Exception:  # noqa: BLE001 - blad odbiorcy nie zatrzymuje silnika
            LOG.exception("silnik: blad funkcji odbierajacej zdarzenie %s", typ)

    def _petla(self) -> None:
        while not self._stop.is_set():
            try:
                self._krok()
            except Exception:  # noqa: BLE001 - nadzorca nie moze sie skonczyc
                LOG.exception("silnik: blad nadzorcy")
                time.sleep(0.2)

    def _uruchom_proces(self) -> None:
        rodzic, dziecko = self._ctx.Pipe()
        p = self._ctx.Process(target=_robotnik, name="silnik-analiza", daemon=True,
                              args=(dziecko, self.ust, self.plik_ustawien, self.funkcja, self.pul_w_pamieci, self.plik_logu, self.pamiec_linii,
                                    self.limit_zadania_s))
        p.start()
        dziecko.close()  # koniec lacza po stronie procesu roboczego zostaje tylko u niego: jego smierc = koniec danych
        self._proces, self._lacze, self._gotowy, self._start_procesu = p, rodzic, False, time.monotonic()
        self._starty += 1

    def _zamknij_proces(self, grzecznie: bool = False) -> int | None:
        p, lacze = self._proces, self._lacze
        self._proces, self._lacze, self._gotowy = None, None, False
        kod = None
        if p is not None:
            if grzecznie and p.is_alive() and lacze is not None:
                try:
                    lacze.send(("koniec",))
                    p.join(2.0)
                except OSError:
                    pass
            if p.is_alive():
                p.kill()
            p.join(5.0)
            kod = p.exitcode
            try:
                p.close()
            except ValueError:
                pass
        if lacze is not None:
            try:
                lacze.close()
            except OSError:
                pass
        return kod

    def _krok(self) -> None:
        if self._proces is None:
            if self._nieudany_start is not None and not self._kolejka:
                time.sleep(0.05)  # po nieudanym starcie kolejna proba dopiero, gdy jest dla kogo
                return
            self._uruchom_proces()
        try:
            if self._lacze.poll(OKRES_S):
                self._odbierz(self._lacze.recv())
                self._sprawdz_limit()  # D4 (a): zadanie, ktore stale przysyla postep, tez ma limit czasu
                return
        except (EOFError, OSError):
            self._po_smierci_procesu()
            return
        teraz = time.monotonic()
        if not self._proces.is_alive():
            self._po_smierci_procesu()
        elif self._biezace is not None:
            self._sprawdz_limit()
        elif not self._gotowy:
            if teraz - self._start_procesu > self.limit_startu_s:
                self._zamknij_proces()
                self._nieudany_start_procesu(f"proces silnika nie zglosil gotowosci w {self.limit_startu_s:.0f} s", "")
        else:
            with self._zamek:  # D3: zdjecie z kolejki i "w toku" razem - czekaj_na_pusta_kolejke nie widzi luki
                zadanie = self._kolejka.popleft() if self._kolejka else None
                if zadanie is not None:
                    self._biezace, self._biezace_od = zadanie, teraz
            if zadanie is not None:
                self._zglos("start", zadanie_id=zadanie.zadanie_id, zadanie=zadanie)
                try:
                    self._lacze.send(("zadanie", zadanie))
                except OSError:
                    self._po_smierci_procesu()

    def _sprawdz_limit(self) -> None:
        zadanie = self._biezace
        if zadanie is None or self._proces is None:
            return
        czas = time.monotonic() - self._biezace_od
        if czas <= self.limit_zadania_s:
            return
        self._zamknij_proces()
        self._zglos("blad", zadanie_id=zadanie.zadanie_id, zadanie=zadanie, rodzaj="limit_czasu", czas_s=round(czas, 3),
                    blad=f"analiza trwala dluzej niz {self.limit_zadania_s:.0f} s i zostala przerwana")
        self._biezace = None

    def _odbierz(self, w: tuple) -> None:
        rodzaj = w[0]
        if rodzaj == "gotowy":
            self._gotowy, self._nieudany_start = True, None
            self._zglos("gotowy", czas_s=round(time.monotonic() - self._start_procesu, 3))
            return
        if rodzaj == "blad_startu":
            self._zamknij_proces()
            self._nieudany_start_procesu(f"proces silnika nie wystartowal: {w[1]}", w[2])
            return
        zadanie = self._biezace
        if zadanie is None or w[1] != zadanie.zadanie_id:
            return  # spozniona wiadomosc zadania juz zamknietego
        if rodzaj == "postep":
            self._zglos("postep", zadanie_id=zadanie.zadanie_id, zadanie=zadanie, etap=w[2], udzial=w[3])
            return
        czas_s = round(time.monotonic() - self._biezace_od, 3)
        if rodzaj == "wynik":
            self._zglos("wynik", zadanie_id=zadanie.zadanie_id, zadanie=zadanie, wynik=w[2], pliki=w[3], czas_s=czas_s)
        elif rodzaj == "blad":
            self._zglos("blad", zadanie_id=zadanie.zadanie_id, zadanie=zadanie, rodzaj=w[4] if len(w) > 4 else "analiza", blad=w[2], szczegoly=w[3],
                        czas_s=czas_s)
        self._biezace = None  # D3: "wolny" dopiero po zgloszeniu wyniku

    def _po_smierci_procesu(self) -> None:
        """Proces roboczy zniknal (zabity, awaria biblioteki): blad biezacego zadania; nowy proces ruszy w nastepnym kroku."""
        gotowy, zadanie, od = self._gotowy, self._biezace, self._biezace_od
        kod = self._zamknij_proces()
        if zadanie is not None:
            self._zglos("blad", zadanie_id=zadanie.zadanie_id, zadanie=zadanie, rodzaj="proces", czas_s=round(time.monotonic() - od, 3),
                        blad=f"proces silnika zakonczyl sie w trakcie analizy (kod wyjscia {kod}); analiza przerwana")
            self._biezace = None
        elif not gotowy:
            self._nieudany_start_procesu(f"proces silnika zakonczyl sie przy starcie (kod wyjscia {kod})", "")

    def _nieudany_start_procesu(self, tekst: str, szczegoly: str) -> None:
        """Proces nie wystartowal: blad dostaje pierwsze zadanie z kolejki (kazde zadanie = najwyzej jedna nieudana proba)."""
        LOG.error("%s", tekst)
        self._nieudany_start = (tekst, szczegoly)
        with self._zamek:
            zadanie = self._kolejka.popleft() if self._kolejka else None
        if zadanie is not None:
            self._zglos("blad", zadanie_id=zadanie.zadanie_id, zadanie=zadanie, rodzaj="start", blad=tekst, szczegoly=szczegoly, czas_s=0.0)


# ----------------------------------------------------------------------------
# lacznik z petla Qt (PySide6 importowane dopiero tutaj)
# ----------------------------------------------------------------------------
_KLASA_LACZNIKA = None


def lacznik_qt(silnik: Silnik, okres_ms: int = 30, rodzic=None):
    """Obiekt Qt z sygnalami silnika emitowanymi w watku okna: ``gotowy()``, ``start(int)``, ``postep(int, str, float)``,
    ``wynik(int, object)`` (slownik wyniku), ``blad(int, str, str)`` (numer, rodzaj, komunikat) i ``zdarzenie(object)``
    (kazde ``ZdarzenieSilnika``). Zegar Qt co ``okres_ms`` oproznia kolejke ``silnik.zdarzenia`` - silnik nie moze miec
    wtedy wlasnego ``na_zdarzenie``. ``zatrzymaj()`` wylacza zegar."""
    global _KLASA_LACZNIKA
    if silnik.na_zdarzenie is not None:
        raise ValueError("lacznik_qt: silnik ma juz funkcje na_zdarzenie")
    if _KLASA_LACZNIKA is None:
        from PySide6.QtCore import QObject, QTimer, Signal

        class LacznikQt(QObject):
            gotowy = Signal()
            start = Signal(int)
            postep = Signal(int, str, float)
            wynik = Signal(int, object)
            blad = Signal(int, str, str)
            zdarzenie = Signal(object)

            def __init__(self, silnik_: Silnik, okres_ms_: int, rodzic_=None):
                super().__init__(rodzic_)
                self.silnik = silnik_
                self._zegar = QTimer(self)
                self._zegar.setInterval(okres_ms_)
                self._zegar.timeout.connect(self.oproznij)
                self._zegar.start()

            def oproznij(self) -> None:
                for _ in range(200):  # najwyzej tyle zdarzen na jedno tykniecie - petla okna nie czeka
                    try:
                        z = self.silnik.zdarzenia.get_nowait()
                    except queue.Empty:
                        return
                    self.zdarzenie.emit(z)
                    if z.typ == "gotowy":
                        self.gotowy.emit()
                    elif z.typ == "start":
                        self.start.emit(z.zadanie_id)
                    elif z.typ == "postep":
                        self.postep.emit(z.zadanie_id, z.etap, z.udzial)
                    elif z.typ == "wynik":
                        self.wynik.emit(z.zadanie_id, z.wynik)
                    elif z.typ == "blad":
                        self.blad.emit(z.zadanie_id, z.rodzaj, z.blad)

            def zatrzymaj(self) -> None:
                self._zegar.stop()

        _KLASA_LACZNIKA = LacznikQt
    return _KLASA_LACZNIKA(silnik, okres_ms, rodzic)
