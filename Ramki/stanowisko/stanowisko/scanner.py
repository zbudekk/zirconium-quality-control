"""scanner - obserwacja folderu eksportu skanera: nowy plik STL -> zdarzenie "nowy skan" (paczka E3-A2).

Co robi: patrzy na folder (biblioteka ``watchdog`` + okresowy przeglad jako siatka bezpieczenstwa), dla kazdego pliku
pasujacego do wzorca czeka na koniec zapisu, sprawdza go (binarny STL: rozmiar = 84 + 50 x liczba trojkatow) i zglasza
``ZdarzenieSkanu`` (plik, sha16, rozmiar, liczba trojkatow, czas pliku). Plik zly (pusty, uciety, nie-STL, tekstowy,
z niezgodnym naglowkiem, za maly) nie daje zdarzenia, tylko ``Odrzucenie`` z powodem. Modul nie laduje numpy, trimesh,
Open3D ani Qt - dziala w procesie okna w zwyklym watku Pythona.

Koniec zapisu = wszystkie warunki naraz:
  1. rozmiar i czas pliku nie zmienily sie przez ``stabilizacja_ms``,
  2. rozmiar zgadza sie z liczba trojkatow w naglowku (plik w trakcie zapisu prawie nigdy tego nie spelnia),
  3. zaden program nie trzyma pliku otwartego do zapisu (Windows; ``dzien_skanera_rdzen.ktos_pisze``),
  4. po policzeniu skrotu rozmiar i czas sa nadal te same.
Plik stabilny, ale zly, jest odrzucany dopiero po ``odrzuc_po_s`` bez zmian (moze byc jeszcze dopisywany); odrzucenie
nie jest ostateczne - gdy plik sie zmieni, jest oceniany od nowa.

Nie zakladamy nazw ani struktury plikow prawdziwego skanera: wzorzec nazwy, podfoldery i wszystkie czasy sa parametrami
konstruktora (podpiecie do ``ustawienia.toml`` robi paczka A3; proponowane klucze ``[scanner]``: ``stabilizacja_ms``,
``min_rozmiar_mb``, ``min_trojkatow``, ``wzorzec_pliku``).

Akcja "start skanu" (decyzja DW5: Spacje lapie nasze okno, ktore aktywuje okno skanera) jest tu tylko interfejsem:
``Scanner.start_skanu()`` wywoluje podana funkcje; domyslnie ``AtrapaStartuSkanu``, ktora nic nie klika.

Uzyte ponownie z okna "Dzien skanera" (``dzien_skanera_rdzen``, bez zmian w tamtym pliku): ``ktos_pisze``,
``otworz_zrodlo`` (odczyt z pelnym wspoldzieleniem - nie blokuje programu skanera), ``pliki_w_folderze``.

Uzycie:
    sc = Scanner(folder, na_skan=funkcja, na_odrzucenie=funkcja2)   # funkcje sa wolane w watku obserwatora
    sc.start() ... sc.stop()
Bez funkcji zwrotnych zdarzenia trafiaja do kolejki ``sc.zdarzenia``.
"""
from __future__ import annotations

import collections
import dataclasses
import fnmatch
import hashlib
import logging
import os
import queue
import stat
import threading
import time
from pathlib import Path

from .dzien_skanera_rdzen import ktos_pisze, otworz_zrodlo, pliki_w_folderze

LOG = logging.getLogger(__name__)

# wartosci domyslne parametrow konstruktora (jedno miejsce; A3 podepnie je do ustawien)
STABILIZACJA_MS = 300  # tyle bez zmiany rozmiaru i czasu pliku = zapis sie skonczyl (lacznie z warunkami 2-4 z opisu modulu)
MIN_ROZMIAR_MB = 0.0  # 0 = bez progu rozmiaru
MIN_TROJKATOW = 1  # plik bez trojkatow nie jest skanem; prog dla prawdziwego skanera ustali B2
WZORZEC_PLIKU = "*.stl"  # wzorzec NAZWY pliku (fnmatch, bez rozrozniania wielkosci liter)
ODRZUC_PO_S = 5.0  # plik zly i niezmieniany przez tyle sekund = wpis "odrzucony" z powodem
OKRES_S = 0.05  # co ile watek oglada pliki, na ktore czeka
PRZEGLAD_S = 2.0  # co ile caly folder jest przegladany niezaleznie od watchdog (zgubione powiadomienia, dysk sieciowy)
BLOK_ODCZYTU = 4 * 1024 * 1024
LIMIT_DZIENNIKA = 1000  # tyle ostatnich odrzucen pamieta obserwator
PROBY_ODCZYTU = 40  # tyle kolejnych nieudanych odczytow pliku (zajety) zanim powstanie wpis "blad_odczytu"

POWODY = {
    "poza_wzorcem": "nazwa pliku nie pasuje do wzorca skanow",
    "pusty": "plik pusty (0 bajtow)",
    "za_krotki": "plik krotszy niz naglowek binarnego STL (84 bajty) - nie-STL albo uciety",
    "stl_tekstowy": "STL tekstowy (ASCII) - program przyjmuje tylko binarny STL",
    "rozmiar_niezgodny": "rozmiar pliku nie zgadza sie z liczba trojkatow w naglowku (plik uciety, uszkodzony albo nie-STL)",
    "za_malo_trojkatow": "za malo trojkatow",
    "za_maly": "plik mniejszy niz prog rozmiaru",
    "blad_odczytu": "pliku nie da sie odczytac",
}


@dataclasses.dataclass(frozen=True)
class ZdarzenieSkanu:
    """Nowy skan w folderze (kontrakt z planu etapu 3, sekcja 3.8). Obiekt jest prosty - przechodzi do procesu silnika."""

    plik: Path
    sha16: str  # pierwsze 16 znakow SHA-256 zawartosci (ten sam skrot, co synth.skrot_pliku)
    rozmiar: int
    trojkaty: int
    czas_pliku: float  # czas modyfikacji pliku, sekundy od epoki
    mtime_ns: int
    czas_zdarzenia: float  # time.time() w chwili zgloszenia
    nr: int  # kolejny numer zdarzenia tego obserwatora (od 1)
    ponowny: bool = False  # ta sama sciezka byla juz zgloszona (plik zapisany ponownie pod ta sama nazwa)
    duplikat: bool = False  # ta sama zawartosc byla juz zgloszona pod INNA nazwa
    duplikat_z: str | None = None  # sciezka pierwszego pliku o tej zawartosci


@dataclasses.dataclass(frozen=True)
class Odrzucenie:
    """Plik, ktory nie dal zdarzenia - wpis z powodem (kod z ``POWODY``) i opisem dla czlowieka."""

    plik: Path
    powod: str
    opis: str
    rozmiar: int | None
    czas: float


@dataclasses.dataclass(frozen=True)
class WynikWalidacji:
    trojkaty: int | None  # liczba trojkatow z naglowka (None, gdy nie da sie jej odczytac)
    powod: str | None  # None = plik dobry
    opis: str
    rozmiar: int | None


def sprawdz_stl(plik, min_trojkatow: int = MIN_TROJKATOW, min_rozmiar_mb: float = MIN_ROZMIAR_MB) -> WynikWalidacji:
    """Walidacja pliku skanu bez wczytywania siatki: binarny STL ma rozmiar 84 + 50 x liczba trojkatow z naglowka."""
    try:
        rozmiar = os.stat(plik).st_size
        with otworz_zrodlo(plik) as f:
            naglowek = f.read(84)
            poczatek = naglowek + f.read(428) if rozmiar > 84 else naglowek
    except OSError as e:
        return WynikWalidacji(None, "blad_odczytu", f"{POWODY['blad_odczytu']}: {type(e).__name__}", None)
    if rozmiar == 0:
        return WynikWalidacji(None, "pusty", POWODY["pusty"], 0)
    if len(naglowek) < 84:
        return WynikWalidacji(None, "za_krotki", f"{POWODY['za_krotki']}; plik ma {rozmiar} B", rozmiar)
    trojkaty = int.from_bytes(naglowek[80:84], "little")
    oczekiwany = 84 + 50 * trojkaty
    if oczekiwany != rozmiar:
        if naglowek[:5].lower() == b"solid" and _wyglada_na_tekst(poczatek):
            return WynikWalidacji(None, "stl_tekstowy", POWODY["stl_tekstowy"], rozmiar)
        co = "plik uciety" if rozmiar < oczekiwany else "plik dluzszy niz zapowiada naglowek"
        return WynikWalidacji(trojkaty, "rozmiar_niezgodny", f"{co}: naglowek zapowiada {trojkaty} trojkatow ({oczekiwany} B), plik ma {rozmiar} B", rozmiar)
    if trojkaty < min_trojkatow:
        return WynikWalidacji(trojkaty, "za_malo_trojkatow", f"{POWODY['za_malo_trojkatow']}: {trojkaty}, wymagane co najmniej {min_trojkatow}", rozmiar)
    if rozmiar < min_rozmiar_mb * 1024 * 1024:
        return WynikWalidacji(trojkaty, "za_maly", f"{POWODY['za_maly']}: {rozmiar} B, wymagane co najmniej {min_rozmiar_mb} MB", rozmiar)
    return WynikWalidacji(trojkaty, None, "", rozmiar)


def _wyglada_na_tekst(dane: bytes) -> bool:
    return bool(dane) and all(b in (9, 10, 13) or 32 <= b < 127 for b in dane)


def skrot16_pliku(plik) -> str:
    """Pierwsze 16 znakow SHA-256 zawartosci; plik czytany z pelnym wspoldzieleniem (nie blokuje programu skanera)."""
    h = hashlib.sha256()
    with otworz_zrodlo(plik) as f:
        while True:
            blok = f.read(BLOK_ODCZYTU)
            if not blok:
                break
            h.update(blok)
    return h.hexdigest()[:16]


class AtrapaStartuSkanu:
    """Atrapa akcji "start skanu": niczego nie klika, tylko zapisuje czasy wywolan (``wywolania``). Prawdziwa akcja
    (aktywuj okno programu skanera i nacisnij Spacje) powstanie po pierwszych probach na skanerze (paczka B2)."""

    def __init__(self):
        self.wywolania: list[float] = []

    def __call__(self) -> bool:
        self.wywolania.append(time.time())
        return True


def _klucz(sciezka) -> str:
    return os.path.normcase(os.path.abspath(str(sciezka)))


class Scanner:
    """Obserwator folderu eksportu skanera. Parametry - patrz stale na gorze modulu i opis w ``opisy_modulow/scanner.md``.

    ``obserwator``: ``"watchdog"`` (domyslnie; gdy biblioteki nie da sie uzyc - samo odpytywanie) albo ``"odpytywanie"``
    (tylko przeglad folderu co ``przeglad_s``, np. dla dysku sieciowego). ``zglos_zastane``: czy pliki obecne w folderze
    przy starcie sa nowymi skanami (domyslnie nie). ``zegar`` - do testow.
    """

    def __init__(self, folder, na_skan=None, na_odrzucenie=None, *, wzorzec_pliku: str = WZORZEC_PLIKU, rekurencyjnie: bool = True,
                 stabilizacja_ms: float = STABILIZACJA_MS, min_rozmiar_mb: float = MIN_ROZMIAR_MB, min_trojkatow: int = MIN_TROJKATOW,
                 odrzuc_po_s: float = ODRZUC_PO_S, okres_s: float = OKRES_S, przeglad_s: float = PRZEGLAD_S, zglos_zastane: bool = False,
                 obserwator: str = "watchdog", start_skanu=None, zegar=time.monotonic):
        if obserwator not in ("watchdog", "odpytywanie"):
            raise ValueError(f"obserwator: {obserwator!r} (dozwolone: watchdog, odpytywanie)")
        self.folder = Path(folder)
        self.na_skan, self.na_odrzucenie = na_skan, na_odrzucenie
        self.wzorzec_pliku, self.rekurencyjnie = wzorzec_pliku, rekurencyjnie
        self.stabilizacja_s = stabilizacja_ms / 1000.0
        self.min_rozmiar_mb, self.min_trojkatow = min_rozmiar_mb, min_trojkatow
        self.odrzuc_po_s, self.okres_s, self.przeglad_s = odrzuc_po_s, okres_s, przeglad_s
        self.zglos_zastane = zglos_zastane
        self.akcja_startu = start_skanu if start_skanu is not None else AtrapaStartuSkanu()
        self.zegar = zegar
        self.zdarzenia: queue.Queue = queue.Queue()  # ZdarzenieSkanu / Odrzucenie, gdy nie podano funkcji zwrotnych
        self.odrzucone: collections.deque = collections.deque(maxlen=LIMIT_DZIENNIKA)
        self._tryb = obserwator
        self._watchdog = None
        self._zmiany: collections.deque = collections.deque()  # (rodzaj, sciezka) z watku watchdog
        self._budzik = threading.Event()
        self._stop = threading.Event()
        self._watek: threading.Thread | None = None
        self._znane: dict[str, tuple] = {}  # klucz sciezki -> (rozmiar, mtime_ns) wersji juz rozstrzygnietej
        self._kandydaci: dict[str, dict] = {}
        self._pominiete: set[str] = set()  # pliki spoza wzorca, juz wpisane do dziennika
        self._zgloszone: set[str] = set()  # sciezki, ktore daly juz zdarzenie
        self._skroty: dict[str, str] = {}  # sha16 -> sciezka pierwszego pliku o tej zawartosci
        self._nr = 0
        self._odrzucen = 0
        self._ostatni_przeglad = -1e18
        self._folder_dostepny = False
        self._przygotowany = False

    # --- sterowanie
    def start(self) -> None:
        if self._watek is not None and self._watek.is_alive():
            return
        self._stop.clear()
        self.przygotuj()
        self._uruchom_watchdog()  # po stop() i ponownym start() stan zostaje, watchdog rusza od nowa
        self._watek = threading.Thread(target=self._petla, name="scanner", daemon=True)
        self._watek.start()

    def stop(self, czekaj_s: float = 5.0) -> None:
        self._stop.set()
        self._budzik.set()
        if self._watek is not None:
            self._watek.join(czekaj_s)
            self._watek = None
        self._zatrzymaj_watchdog()

    def dziala(self) -> bool:
        return self._watek is not None and self._watek.is_alive()

    def start_skanu(self) -> bool:
        """Akcja "start skanu" (DW5). Zwraca False, gdy akcja sie nie powiodla (wyjatek akcji tez = False)."""
        try:
            return bool(self.akcja_startu())
        except Exception as e:  # noqa: BLE001 - brak okna skanera nie moze wywrocic programu
            LOG.warning("start skanu nie powiodl sie: %s: %s", type(e).__name__, e)
            return False

    def stan(self) -> dict:
        """Liczniki do paska stanu okna."""
        return {"folder": str(self.folder), "folder_dostepny": self._folder_dostepny, "obserwator": "watchdog" if self._watchdog is not None else "odpytywanie",
                "zdarzen": self._nr, "odrzucen": self._odrzucen, "czeka": len(self._kandydaci), "dziala": self.dziala()}

    # --- stan poczatkowy i watchdog
    def przygotuj(self) -> None:
        """Stan poczatkowy: pliki zastane w folderze (nie sa nowymi skanami, chyba ze ``zglos_zastane``) i start watchdog.
        Wolane przez ``start()``; osobno tylko wtedy, gdy obiegi wywoluje test (``obieg()`` bez watku)."""
        if self._przygotowany:
            return
        self._przygotowany = True
        self._folder_dostepny = self.folder.is_dir()
        if self._folder_dostepny and not self.zglos_zastane:
            for rel, rozmiar, mtime_ns in pliki_w_folderze(self.folder):
                if self._w_zakresie(rel):
                    k = _klucz(self.folder / rel)
                    if self._pasuje(rel):
                        self._znane[k] = (rozmiar, mtime_ns)
                    else:
                        self._pominiete.add(k)
        self._uruchom_watchdog()

    def _uruchom_watchdog(self) -> None:
        if self._tryb != "watchdog" or self._watchdog is not None or not self.folder.is_dir():
            return
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer
        except ImportError as e:
            LOG.warning("brak biblioteki watchdog (%s) - obserwacja folderu przez odpytywanie", e)
            self._tryb = "odpytywanie"
            return
        scanner = self

        class Odbiornik(FileSystemEventHandler):
            def on_any_event(self, event) -> None:  # watek watchdog: tylko odnotowanie i pobudka
                if event.is_directory:
                    if event.event_type in ("moved", "deleted"):
                        scanner._zmiany.append(("przeglad", ""))
                        scanner._budzik.set()
                    return
                if event.event_type in ("created", "modified", "closed"):
                    scanner._zmiany.append(("zmiana", os.fsdecode(event.src_path)))
                elif event.event_type == "moved":
                    scanner._zmiany.append(("usuniety", os.fsdecode(event.src_path)))
                    scanner._zmiany.append(("zmiana", os.fsdecode(event.dest_path)))
                elif event.event_type == "deleted":
                    scanner._zmiany.append(("usuniety", os.fsdecode(event.src_path)))
                else:
                    return
                scanner._budzik.set()

        try:
            obs = Observer()
            obs.schedule(Odbiornik(), str(self.folder), recursive=self.rekurencyjnie)
            obs.daemon = True
            obs.start()
        except Exception as e:  # noqa: BLE001 - np. folder zniknal miedzy sprawdzeniem a startem; zostaje przeglad okresowy
            LOG.warning("watchdog nie wystartowal (%s: %s) - na razie odpytywanie", type(e).__name__, e)
            return
        self._watchdog = obs

    def _zatrzymaj_watchdog(self) -> None:
        obs, self._watchdog = self._watchdog, None
        if obs is not None:
            try:
                obs.stop()
                obs.join(2.0)
            except Exception:  # noqa: BLE001
                pass

    # --- watek
    def _petla(self) -> None:
        while not self._stop.is_set():
            try:
                self.obieg()
            except Exception:  # noqa: BLE001 - zaden wyjatek nie konczy obserwacji
                LOG.exception("scanner: blad obiegu")
            if self._kandydaci:
                czekaj = self.okres_s
            elif self._watchdog is not None:
                czekaj = min(self.przeglad_s, 0.5)
            else:
                czekaj = min(self.przeglad_s, 0.5) if self.przeglad_s > 0 else self.okres_s
            self._budzik.wait(max(0.005, czekaj))
            self._budzik.clear()

    def obieg(self) -> None:
        """Jeden obieg: powiadomienia z watchdog, przeglad okresowy folderu, ocena plikow, na ktore czekamy."""
        teraz = self.zegar()
        przeglad = teraz - self._ostatni_przeglad >= self.przeglad_s
        while self._zmiany:
            rodzaj, sciezka = self._zmiany.popleft()
            if rodzaj == "przeglad":
                przeglad = True
            elif rodzaj == "usuniety":
                self._zapomnij(_klucz(sciezka))
            else:
                self._zglos_zmiane(Path(sciezka), teraz)
        if przeglad:
            self._ostatni_przeglad = teraz
            self._przeglad(teraz)
        gotowe = []
        for k, kand in list(self._kandydaci.items()):
            try:
                st = os.stat(kand["sciezka"])
            except FileNotFoundError:
                self._zapomnij(k)
                continue
            except OSError:
                continue  # chwilowo zajety: nastepny obieg
            if stat.S_ISDIR(st.st_mode):
                del self._kandydaci[k]  # katalog o nazwie pasujacej do wzorca
                continue
            podpis = (st.st_size, st.st_mtime_ns)
            if self._znane.get(k) == podpis:
                del self._kandydaci[k]  # echo powiadomienia o pliku juz rozstrzygnietym
                continue
            if podpis != kand["podpis"]:
                kand["podpis"], kand["od"], kand["bledy"] = podpis, teraz, 0
                continue
            if teraz - kand["od"] >= self.stabilizacja_s:
                gotowe.append((st.st_mtime_ns, kand["sciezka"].name, k))
        for _, _, k in sorted(gotowe):  # kilka plikow gotowych w jednym obiegu: w kolejnosci czasu zapisu
            if k in self._kandydaci and not self._stop.is_set():
                self._rozstrzygnij(k, self._kandydaci[k], teraz)

    def _w_zakresie(self, rel: str) -> bool:
        return self.rekurencyjnie or "/" not in rel

    def _pasuje(self, sciezka) -> bool:
        return fnmatch.fnmatchcase(Path(sciezka).name.lower(), self.wzorzec_pliku.lower())

    def _zapomnij(self, k: str) -> None:
        """Plik zniknal (usuniety albo przeniesiony): ta sama nazwa zapisana pozniej jest oceniana od nowa."""
        self._kandydaci.pop(k, None)
        self._znane.pop(k, None)
        self._pominiete.discard(k)

    def _zglos_zmiane(self, sciezka: Path, teraz: float) -> None:
        k = _klucz(sciezka)
        if k in self._kandydaci:
            return
        if not self.rekurencyjnie and _klucz(sciezka.parent) != _klucz(self.folder):
            return
        poza = not self._pasuje(sciezka)
        if poza and k in self._pominiete:
            return  # plik spoza wzorca: jeden wpis w dzienniku, dopoki nie zniknie
        self._kandydaci[k] = {"sciezka": sciezka, "podpis": None, "od": teraz, "bledy": 0, "poza": poza}

    def _przeglad(self, teraz: float) -> None:
        dostepny = self.folder.is_dir()
        if dostepny != self._folder_dostepny:
            self._folder_dostepny = dostepny
            LOG.info("folder eksportu skanera %s: %s", "dostepny" if dostepny else "niedostepny", self.folder)
            if not dostepny:
                self._zatrzymaj_watchdog()
        if not dostepny:
            return
        self._uruchom_watchdog()
        widziane = set()
        for rel, rozmiar, mtime_ns in pliki_w_folderze(self.folder):
            if not self._w_zakresie(rel):
                continue
            sciezka = self.folder / rel
            k = _klucz(sciezka)
            widziane.add(k)
            if k in self._kandydaci or self._znane.get(k) == (rozmiar, mtime_ns):
                continue
            self._zglos_zmiane(sciezka, teraz)
        for k in [k for k in self._znane if k not in widziane]:
            del self._znane[k]
        self._pominiete &= widziane

    def _rozstrzygnij(self, k: str, kand: dict, teraz: float) -> None:
        sciezka = kand["sciezka"]
        if kand["poza"]:  # plik spoza wzorca (np. plik pomocniczy programu skanera): wpis po ustaniu zmian, bez zdarzenia
            if teraz - kand["od"] < self.odrzuc_po_s or ktos_pisze(sciezka):
                return
            del self._kandydaci[k]
            self._pominiete.add(k)
            self._odrzuc(sciezka, "poza_wzorcem", f"{POWODY['poza_wzorcem']} ({self.wzorzec_pliku})", kand["podpis"][0])
            return
        w = sprawdz_stl(sciezka, self.min_trojkatow, self.min_rozmiar_mb)
        if w.powod == "blad_odczytu":
            self._blad_odczytu(k, kand, w.opis)
            return
        if w.powod is not None:
            if teraz - kand["od"] < self.odrzuc_po_s or ktos_pisze(sciezka):
                return  # moze byc jeszcze dopisywany
            self._znane[k] = kand["podpis"]
            del self._kandydaci[k]
            self._odrzuc(sciezka, w.powod, w.opis, w.rozmiar)
            return
        if ktos_pisze(sciezka):
            return  # caly plik juz jest, ale program skanera jeszcze go nie zamknal
        try:
            sha16 = skrot16_pliku(sciezka)
            st = os.stat(sciezka)
        except FileNotFoundError:
            self._zapomnij(k)
            return
        except OSError as e:
            self._blad_odczytu(k, kand, f"{POWODY['blad_odczytu']}: {type(e).__name__}")
            return
        if (st.st_size, st.st_mtime_ns) != kand["podpis"]:
            kand["podpis"], kand["od"] = (st.st_size, st.st_mtime_ns), teraz  # zmienil sie w trakcie liczenia skrotu
            return
        self._znane[k] = kand["podpis"]
        del self._kandydaci[k]
        pierwszy = self._skroty.setdefault(sha16, str(sciezka))
        duplikat = _klucz(pierwszy) != k
        self._nr += 1
        z = ZdarzenieSkanu(plik=sciezka, sha16=sha16, rozmiar=st.st_size, trojkaty=w.trojkaty, czas_pliku=st.st_mtime_ns / 1e9, mtime_ns=st.st_mtime_ns,
                           czas_zdarzenia=time.time(), nr=self._nr, ponowny=k in self._zgloszone, duplikat=duplikat, duplikat_z=pierwszy if duplikat else None)
        self._zgloszone.add(k)
        LOG.info("nowy skan nr %d: %s sha16=%s rozmiar=%d trojkatow=%d%s%s", z.nr, sciezka.name, sha16, z.rozmiar, z.trojkaty,
                 " (ponowny zapis)" if z.ponowny else "", " (duplikat zawartosci)" if duplikat else "")
        self._wyslij(self.na_skan, z)

    def _blad_odczytu(self, k: str, kand: dict, opis: str) -> None:
        kand["bledy"] += 1
        if kand["bledy"] >= PROBY_ODCZYTU:
            self._znane[k] = kand["podpis"]
            del self._kandydaci[k]
            self._odrzuc(kand["sciezka"], "blad_odczytu", f"{opis} ({PROBY_ODCZYTU} prob)", kand["podpis"][0] if kand["podpis"] else None)

    def _odrzuc(self, sciezka: Path, powod: str, opis: str, rozmiar: int | None) -> None:
        o = Odrzucenie(plik=sciezka, powod=powod, opis=opis, rozmiar=rozmiar, czas=time.time())
        self._odrzucen += 1
        self.odrzucone.append(o)
        LOG.info("plik pominiety: %s powod=%s (%s)", sciezka.name, powod, opis)
        self._wyslij(self.na_odrzucenie, o)

    def _wyslij(self, funkcja, obiekt) -> None:
        if funkcja is None:
            self.zdarzenia.put(obiekt)
            return
        try:
            funkcja(obiekt)
        except Exception:  # noqa: BLE001 - blad odbiorcy nie zatrzymuje obserwacji
            LOG.exception("scanner: blad funkcji odbierajacej %s", type(obiekt).__name__)
