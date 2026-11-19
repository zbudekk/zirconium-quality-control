"""Pomiar czasu w testach czasu rzeczywistego odporny na obciazenie wspoldzielonego PC (E3-T0p, runda 2).

Testy czasowe (zmiana plytki w ramce < 100 ms, przerwy petli okna < 200 ms) mierza czas scienny. Na PC, na ktorym
licza obce procesy, czas scienny rosnie z powodow spoza kodu: proces testow nie dostaje procesora (wywlaszczenie),
cala sesja pytest ma tysiace obiektow, wiec pelne zbieranie smieci (GC) zatrzymuje wszystkie watki, a pojedynczy
zapis z ``fsync`` (COMMIT SQLite) potrafi czekac na dysk ponad 200 ms (proba na PC bez sztucznego obciazenia:
1 z 1500 zapisow 226 ms przy medianie 5 ms). Kryterium jest liczone na czasie sciennym; ``PomiarOdporny`` usuwa dwie
przyczyny z samego pomiaru, a dwie pozostale moga najwyzej zlecic POWTORZENIE pomiaru - nigdy zamiany porazki w sukces:

1. GC sesji: ``gc.collect()`` + ``gc.freeze()`` tylko na czas pomiaru (po nim ``gc.unfreeze()`` + ``gc.collect()``) -
   obiekty sprzed pomiaru (sesja pytest, ale tez obiekty programu z fixture'ow) poza zbieraniem; obiekty tworzone przez
   kod w trakcie pomiaru sa zbierane normalnie (pauzy GC w trakcie sa zapisywane i licza sie do czasu). Pauzy GC sterty
   programu sprzed pomiaru nie sa wiec mierzone - wzrost sterty programu wymaga osobnego testu.
2. Priorytet: klasa priorytetu procesu testow ABOVE_NORMAL na czas pomiaru (Windows, bez uprawnien administratora;
   tylko gdy proces ma zwykly priorytet NORMAL - proces celowo obnizony zostaje jak byl) - obce procesy o zwyklym
   priorytecie nie odbieraja procesora watkom mierzonym. Nie skraca uspienia ani obliczen w kodzie.
3. Watek-wzorzec procesu: co ``okres_s`` zapisuje ``perf_counter`` i czas procesora calego procesu (``process_time``).
   Przerwa wzorca >= ``PROG_PRZERWY_WZORCA_S``, w ktorej proces zuzyl mniej niz ``UDZIAL_CPU_PRZESTOJU`` jednego rdzenia,
   to PRZESTOJ PROCESU: wzorzec nie tykal, a proces prawie nie liczyl - zawieszenie lub wywlaszczenie procesu, ALE TEZ
   czekanie w bibliotece C z trzymanym GIL albo wywlaszczenie samego wzorca, gdy watek mierzony blokowal. Dlatego
   ``wlasny(a, b)`` odejmuje od czasu sciennego najwyzej ``LIMIT_PRZESTOJU_S`` (50 ms) przestoju na przedzial, a test
   uzywa czasu wlasnego tylko do decyzji "powtorz pomiar" (``ocen_przerwy`` / ``Powtorki``): gdy porazke na czasie
   sciennym usuwa samo odejmowanie przestoju - pomiar jest powtarzany RAZ; gdy znowu - porazka z rozbiciem. UWAGA: ta jedna
   klasa regresji - czekanie w C z trzymanym GIL, dajace przerwe od progu do progu + 50 ms - SAMA wywoluje powtorzenie,
   wiec gdy wystepuje tylko w czesci uruchomien, jest lapana rzadziej niz na czystym czasie sciennym (recenzja PR #33
   runda 2, P2; przy ABOVE_NORMAL prawdziwych przestojow procesu prawie nie ma: 1 x 46 ms w 135 przebiegach pod
   obciazeniem). Kazdy sukces dopiero po powtorzeniu jest zglaszany ``warnings.warn`` (``Powtorki.ostrzez``).
   Nie jest przestojem: blokujace wywolanie w mierzonym watku zwalniajace GIL (sleep, wejscie-wyjscie, COMMIT, czekanie
   na inny watek / proces - wzorzec tyka dalej) ani praca w Pythonie lub w C z GIL (proces zuzywa pelny rdzen).
4. Wzorzec dysku (tylko z ``dysk=katalog``, testy z zapisem w bazie w watku okna): drugi watek co ``OKRES_DYSKU_S``
   robi minimalny COMMIT SQLite (autocommit, ustawienia domyslne jak baza stanowiska: journal DELETE, synchronous FULL)
   w osobnym pliku w tym samym katalogu. Czas zapisu wzorca ponad ``PROG_ZAPISU_S`` to PRZESTOJ DYSKU. Czas zapisu
   obejmuje tez czekanie wzorca na GIL po powrocie z SQLite, wiec z przestojow dysku wycinane sa przerwy wzorca procesu
   (GIL zajety albo proces stal) - zostaje tylko czas, w ktorym GIL byl wolny, a zapis i tak trwal (recenzja PR #33, B1).
   Przestoj dysku NIE jest odejmowany: gdy przerwa petli ponad prog pokrywa sie z przestojem dysku (najwyzej w czasie, gdy
   watek petli nie liczyl), pomiar jest powtarzany - najwyzej 2 razy; regresja (dodatkowe zapisy, blokada) powtarza sie
   i daje porazke, losowy zastoj dysku rzadko trafia dwa razy.
Bez Windows: bez zmiany priorytetu, ``cpu_watku`` z ``time.thread_time``; reszta bez zmian.
"""
from __future__ import annotations

import bisect
import dataclasses
import gc
import os
import sqlite3
import statistics
import threading
import time
import warnings
from array import array
from pathlib import Path

PROG_PRZERWY_WZORCA_S = 0.020  # wzorzec tyka co 2 ms; 20 ms = 10 tykniec opuszczonych
UDZIAL_CPU_PRZESTOJU = 0.25    # przestoj: proces zuzyl < 1/4 jednego rdzenia w czasie przerwy wzorca
LIMIT_PRZESTOJU_S = 0.050      # najwiecej przestoju procesu odejmowane od jednego przedzialu (recenzja PR #33, P1 r1 / P2 r2)
OKRES_DYSKU_S = 0.030          # odstep miedzy zapisami wzorca dysku (zapis trwa zwykle 5-10 ms)
PROG_ZAPISU_S = 0.050          # czas zapisu wzorca dysku ponad to = przestoj dysku (proba: mediana 5 ms, 99. percentyl 10 ms)
LIMIT_STARTU_S = 5.0           # wzorce musza dac pierwszy znacznik w tym czasie (recenzja PR #33, P3)
NORMAL_PRIORITY_CLASS = 0x20
ABOVE_NORMAL_PRIORITY_CLASS = 0x8000

_k32 = None
if os.name == "nt":
    try:
        import ctypes
        from ctypes import wintypes

        _k32 = ctypes.WinDLL("kernel32")
        _k32.GetCurrentProcess.restype = wintypes.HANDLE
        _k32.GetCurrentThread.restype = wintypes.HANDLE
        _k32.GetPriorityClass.argtypes = [wintypes.HANDLE]
        _k32.GetPriorityClass.restype = wintypes.DWORD
        _k32.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        _k32.SetPriorityClass.restype = wintypes.BOOL
        _k32.QueryThreadCycleTime.argtypes = [wintypes.HANDLE, ctypes.POINTER(ctypes.c_uint64)]
        _k32.QueryThreadCycleTime.restype = wintypes.BOOL
    except (OSError, AttributeError):  # pragma: no cover - Windows bez tych funkcji
        _k32 = None


def _licznik_cykli(funkcja, uchwyt):
    import ctypes

    wartosc = ctypes.c_uint64()

    def odczyt() -> int:
        funkcja(uchwyt, ctypes.byref(wartosc))
        return wartosc.value

    return odczyt


def cykle_na_sekunde() -> float:
    """Ile cykli licznika (QueryThreadCycleTime) daje sekunda pracy jednego rdzenia: najwyzsza z 5 prob po 10 ms petli
    liczacej (proba przerwana przez system daje mniej, wiec maksimum)."""
    if _k32 is None:
        return 0.0
    cykle_watku = _licznik_cykli(_k32.QueryThreadCycleTime, _k32.GetCurrentThread())
    najwyzej = 0.0
    for _ in range(5):
        c0, t0 = cykle_watku(), time.perf_counter()
        while time.perf_counter() - t0 < 0.010:
            pass
        c1, t1 = cykle_watku(), time.perf_counter()
        najwyzej = max(najwyzej, (c1 - c0) / (t1 - t0))
    return najwyzej


def _czesc_wspolna(przedzialy: list, poczatki: list, a: float, b: float) -> float:
    """Laczna dlugosc czesci wspolnej [a, b] z posortowanymi, rozlacznymi przedzialami (poczatki = ich poczatki)."""
    if b <= a or not przedzialy:
        return 0.0
    wynik = 0.0
    i = max(0, bisect.bisect_right(poczatki, a) - 1)
    while i < len(przedzialy) and przedzialy[i][0] < b:
        p, k = przedzialy[i]
        wynik += max(0.0, min(b, k) - max(a, p))
        i += 1
    return wynik


def roznica_przedzialow(przedzialy: list, wyciete: list) -> list:
    """Przedzialy (a, b) bez czesci wspolnych z przedzialami ``wyciete`` (oba zbiory posortowane po poczatku)."""
    wynik = []
    poczatki = [c for c, _ in wyciete]
    for a, b in przedzialy:
        kawalki = [(a, b)]
        i = max(0, bisect.bisect_right(poczatki, a) - 1)
        while i < len(wyciete) and wyciete[i][0] < b:
            c, d = wyciete[i]
            nowe = []
            for x, y in kawalki:
                if d <= x or c >= y:
                    nowe.append((x, y))
                    continue
                if x < c:
                    nowe.append((x, c))
                if d < y:
                    nowe.append((d, y))
            kawalki = nowe
            i += 1
        wynik.extend(k for k in kawalki if k[1] > k[0])
    return wynik


# ---------------------------------------------------------------------- ocena przerw i powtorzenia
@dataclasses.dataclass(frozen=True)
class Przerwa:
    """Jedna przerwa (np. miedzy tyknieciami zegara petli): czas scienny, przestoj procesu (juz ograniczony do
    ``LIMIT_PRZESTOJU_S``), czesc wspolna z przestojami dysku (najwyzej czas bez CPU watku petli), CPU watku petli."""

    sc: float
    proces: float = 0.0
    dysk: float = 0.0
    cpu: float = 0.0
    poczatek: float = 0.0

    def opis(self) -> str:
        return (f"{self.sc * 1000:.0f} ms sciennie (przestoj procesu {self.proces * 1000:.0f} ms, przestoj dysku w przerwie "
                f"{self.dysk * 1000:.0f} ms, CPU watku petli {self.cpu * 1000:.0f} ms)")


OK, POWTORZ_PROCES, POWTORZ_DYSK, BLAD = "ok", "powtorz_proces", "powtorz_dysk", "blad"
_WAGA = {OK: 0, POWTORZ_PROCES: 1, POWTORZ_DYSK: 2, BLAD: 3}


def ocen_przerwy(przerwy, prog: float) -> tuple:
    """(ocena, najdluzsza przerwa) dla progu na CZASIE SCIENNYM: ``ok`` - zadna przerwa ponad prog; ``powtorz_proces`` -
    kazda przerwa ponad prog miesci sie w progu po odjeciu przestoju procesu; ``powtorz_dysk`` - po odjeciu przestoju
    procesu i czesci wspolnej z przestojami dysku; ``blad`` - zostaje przerwa ponad prog bez wyjasnienia."""
    przerwy = list(przerwy)
    najdluzsza = max(przerwy, key=lambda p: p.sc, default=Przerwa(0.0))
    zle = [p for p in przerwy if p.sc > prog]
    if not zle:
        return OK, najdluzsza
    if all(p.sc - p.proces <= prog for p in zle):
        return POWTORZ_PROCES, najdluzsza
    if all(p.sc - p.proces - p.dysk <= prog for p in zle):
        return POWTORZ_DYSK, najdluzsza
    return BLAD, najdluzsza


def gorsza(*oceny: str) -> str:
    """Najgorsza z ocen (blad > powtorz_dysk > powtorz_proces > ok)."""
    return max(oceny, key=_WAGA.__getitem__)


class Powtorki:
    """Decyzja o powtorzeniu calego pomiaru: z powodu przestoju procesu najwyzej 1 raz, z powodu przestoju dysku najwyzej
    2 razy, lacznie najwyzej 2 powtorzenia; ``historia`` - opis kazdej proby do komunikatu porazki."""

    def __init__(self):
        self.proces = 0
        self.dysk = 0
        self.historia: list = []

    def dalej(self, ocena: str, opis: str) -> bool:
        self.historia.append(f"proba {len(self.historia) + 1}: {ocena} - {opis}")
        if self.proces + self.dysk >= 2:
            return False
        if ocena == POWTORZ_PROCES and self.proces < 1:
            self.proces += 1
            return True
        if ocena == POWTORZ_DYSK and self.dysk < 2:
            self.dysk += 1
            return True
        return False

    def opis(self) -> str:
        return " | ".join(self.historia)

    def ostrzez(self, nazwa: str, ocena: str) -> None:
        """Sukces dopiero po powtorzeniu = ostrzezenie z historia pomiarow (widoczne w podsumowaniu pytest takze przy PASS).
        Sporadyczna regresja albo czesty zastoj srodowiska nie znika wtedy bez sladu (recenzja PR #33 runda 2, P1)."""
        if ocena == OK and len(self.historia) > 1:
            warnings.warn(f"{nazwa}: kryterium spelnione dopiero w pomiarze {len(self.historia)}: {self.opis()}", stacklevel=2)


# ---------------------------------------------------------------------- pomiar
class PomiarOdporny:
    """Kontekst pomiaru (patrz opis modulu). Po wyjsciu z ``with``: ``przestoj(a, b)``, ``wlasny(a, b)``,
    ``przerwy_petli(znaczniki, cpu)``, ``opis()``. Znaczniki czasu mierzonego kodu bierze sie z ``time.perf_counter``
    (ten sam zegar co wzorce); ``cpu_watku()`` mozna wolac w trakcie pomiaru. Jedna instancja = jeden pomiar."""

    def __init__(self, okres_s: float = 0.002, priorytet: bool = True, zamroz_gc: bool = True, dysk: Path | None = None):
        self.okres_s = okres_s
        self.priorytet = priorytet
        self.zamroz_gc = zamroz_gc
        self.dysk = Path(dysk) if dysk is not None else None
        self.t = array("d")    # znaczniki wzorca (perf_counter)
        self.cpu = array("d")  # czas procesora calego procesu przy kazdym znaczniku (process_time)
        self.zapisy: list = []          # (poczatek, koniec) kazdego zapisu wzorca dysku
        self.pauzy_gc: list = []        # (poczatek, koniec, pokolenie) pauz GC w trakcie pomiaru
        self.przestoje: list = []       # (poczatek, koniec) przestojow procesu
        self.przestoje_dysku: list = []  # czas zapisow wzorca dysku ponad PROG_ZAPISU_S bez przerw wzorca procesu
        self.zajete: list = []          # (poczatek, koniec, udzial CPU) przerw wzorca, w ktorych proces pracowal (GIL zajety)
        self.priorytet_podniesiony = False  # czy w tym pomiarze podniesiono priorytet (do opisu)
        self._do_przywrocenia = False
        self.blad_dysku: BaseException | None = None
        self._cps = 0.0
        self._stara_klasa = 0
        self._gc_zamrozone = False
        self._stop = threading.Event()
        self._watek = threading.Thread(target=self._tykaj, name="pomiar-wzorzec", daemon=True)
        self._watek_dysku = threading.Thread(target=self._zapisuj, name="pomiar-wzorzec-dysku", daemon=True)
        self._gc_start = 0.0
        self._poczatki: list = []
        self._poczatki_dysku: list = []
        self._lokalne = threading.local()

    # ------------------------------------------------------------------ kontekst
    def __enter__(self) -> "PomiarOdporny":
        try:
            if self.zamroz_gc:
                gc.collect()
                gc.freeze()
                self._gc_zamrozone = True
                gc.callbacks.append(self._gc)
            if self.priorytet and _k32 is not None:
                proces = _k32.GetCurrentProcess()
                self._stara_klasa = _k32.GetPriorityClass(proces)
                if self._stara_klasa == NORMAL_PRIORITY_CLASS:
                    self.priorytet_podniesiony = bool(_k32.SetPriorityClass(proces, ABOVE_NORMAL_PRIORITY_CLASS))
                    self._do_przywrocenia = self.priorytet_podniesiony
            self._cps = cykle_na_sekunde()
            self._watek.start()
            if self.dysk is not None:
                self._watek_dysku.start()
            koniec = time.perf_counter() + LIMIT_STARTU_S
            while not self.t or (self.dysk is not None and not self.zapisy):  # pierwsze znaczniki wzorcow przed pomiarem
                if not self._watek.is_alive() or (self.dysk is not None and not self._watek_dysku.is_alive()) \
                        or time.perf_counter() > koniec:
                    raise RuntimeError(f"wzorzec pomiaru nie wystartowal w {LIMIT_STARTU_S:g} s"
                                       + (f" (wzorzec dysku: {self.blad_dysku!r})" if self.blad_dysku else ""))
                time.sleep(0.001)
        except BaseException:
            self._sprzatnij()
            raise
        return self

    def __exit__(self, *wyjatek) -> None:
        try:
            self._sprzatnij()
        finally:
            self._wyznacz_przestoje()

    def _sprzatnij(self) -> None:
        """Zatrzymuje wzorce, przywraca priorytet i GC - kazdy krok takze wtedy, gdy poprzedni sie nie udal."""
        self._stop.set()
        try:
            for w in (self._watek, self._watek_dysku):
                if w.is_alive():
                    w.join(5.0)
        finally:
            try:
                if self._do_przywrocenia:
                    self._do_przywrocenia = False
                    _k32.SetPriorityClass(_k32.GetCurrentProcess(), self._stara_klasa)
            finally:
                if self._gc in gc.callbacks:
                    gc.callbacks.remove(self._gc)
                if self._gc_zamrozone:
                    self._gc_zamrozone = False
                    gc.unfreeze()
                    gc.collect()

    def _gc(self, faza: str, info: dict) -> None:
        if faza == "start":
            self._gc_start = time.perf_counter()
        else:
            self.pauzy_gc.append((self._gc_start, time.perf_counter(), info.get("generation")))

    def _tykaj(self) -> None:
        # CPU procesu z time.process_time (GetProcessTimes: czas naliczany watkowi, ktory pracuje, w kazdym tyknieciu zegara
        # systemu, ok. 15,6 ms). NIE QueryProcessCycleTime: cykle watku, ktory od dawna pracuje bez przelaczenia (np. 300 ms
        # obliczen w C z GIL), sa w sumie procesu doliczane dopiero przy przelaczeniu - proba na PC: 1 z 10 takich obliczen
        # wygladala jak przestoj procesu.
        zegar, spij, t, cpu, cpu_procesu = time.perf_counter, time.sleep, self.t, self.cpu, time.process_time
        while not self._stop.is_set():
            cpu.append(cpu_procesu())
            t.append(zegar())
            spij(self.okres_s)
        cpu.append(cpu_procesu())
        t.append(zegar())

    def _zapisuj(self) -> None:
        try:
            pol = sqlite3.connect(self.dysk / "pomiar_wzorzec_dysku.sqlite", isolation_level=None)
        except BaseException as e:  # noqa: BLE001 - __enter__ zglosi blad zamiast czekac w nieskonczonosc
            self.blad_dysku = e
            return
        try:
            pol.execute("CREATE TABLE IF NOT EXISTS wzorzec (t REAL)")
            while not self._stop.is_set():
                t0 = time.perf_counter()
                pol.execute("INSERT INTO wzorzec (t) VALUES (?)", (t0,))
                self.zapisy.append((t0, time.perf_counter()))
                self._stop.wait(OKRES_DYSKU_S)
        except BaseException as e:  # noqa: BLE001
            self.blad_dysku = e
        finally:
            pol.close()

    def _wyznacz_przestoje(self) -> None:
        self.przestoje, self.zajete = [], []
        t, c = self.t, self.cpu
        for i in range(min(len(t), len(c)) - 1):
            przerwa = t[i + 1] - t[i]
            if przerwa < PROG_PRZERWY_WZORCA_S:
                continue
            udzial = (c[i + 1] - c[i]) / przerwa
            if udzial < UDZIAL_CPU_PRZESTOJU:
                self.przestoje.append((t[i], t[i + 1]))
            else:
                self.zajete.append((t[i], t[i + 1], udzial))
        self._poczatki = [a for a, _ in self.przestoje]
        # przestoj dysku = czas zapisu wzorca PONAD prog, bez przerw wzorca procesu (B1: zapis "trwa" tez wtedy, gdy wzorzec
        # dysku czeka na GIL trzymany przez inny watek - to nie jest dysk)
        dlugie = [(a + PROG_ZAPISU_S, b) for a, b in self.zapisy if b - a > PROG_ZAPISU_S]
        przerwy_wzorca = sorted(self.przestoje + [(a, b) for a, b, _ in self.zajete])
        self.przestoje_dysku = roznica_przedzialow(dlugie, przerwy_wzorca)
        self._poczatki_dysku = [a for a, _ in self.przestoje_dysku]

    # ------------------------------------------------------------------ wyniki
    def przestoj(self, a: float, b: float) -> float:
        """Przestoj procesu w przedziale [a, b] (sekundy), najwyzej ``LIMIT_PRZESTOJU_S``."""
        return min(LIMIT_PRZESTOJU_S, _czesc_wspolna(self.przestoje, self._poczatki, a, b))

    def przestoj_dysku(self, a: float, b: float) -> float:
        """Laczny czas przestojow dysku (wzorzec dysku, bez przerw wzorca procesu) w przedziale [a, b] (sekundy)."""
        return _czesc_wspolna(self.przestoje_dysku, self._poczatki_dysku, a, b)

    def wlasny(self, a: float, b: float) -> float:
        """Czas scienny przedzialu [a, b] bez przestoju procesu (najwyzej ``LIMIT_PRZESTOJU_S`` odjete)."""
        return (b - a) - self.przestoj(a, b)

    def cpu_watku(self) -> float:
        """Czas procesora watku wolajacego [s] (cykle / cykle na sekunde; bez Windows ``time.thread_time``) - do opisu
        przerw: duzo CPU = praca w watku, malo CPU bez przestoju = czekanie (uspienie, wejscie-wyjscie, blokada)."""
        if _k32 is None or self._cps <= 0:
            return time.thread_time()
        if getattr(self._lokalne, "licz", None) is None:
            self._lokalne.licz = _licznik_cykli(_k32.QueryThreadCycleTime, _k32.GetCurrentThread())
        return self._lokalne.licz() / self._cps

    def przerwy_petli(self, znaczniki, cpu) -> list:
        """``Przerwa`` dla kazdej pary kolejnych znacznikow obiegu petli; ``cpu`` - ``cpu_watku()`` watku petli przy kazdym
        znaczniku. ``dysk`` = czesc wspolna z przestojami dysku, najwyzej czas bez przestoju procesu i bez CPU watku petli."""
        przerwy = []
        for i, (a, b) in enumerate(zip(znaczniki, znaczniki[1:])):
            proces = self.przestoj(a, b)
            cpu_przerwy = max(0.0, cpu[i + 1] - cpu[i])
            dysk = min(self.przestoj_dysku(a, b), max(0.0, (b - a) - proces - cpu_przerwy))
            przerwy.append(Przerwa(b - a, proces, dysk, cpu_przerwy, a))
        return przerwy

    def opis(self) -> str:
        przestoje = [b - a for a, b in self.przestoje]
        gc_ms = [(k - p) * 1000 for p, k, _ in self.pauzy_gc]
        zajete = max(((b - a) * 1000 for a, b, _ in self.zajete), default=0.0)
        okres = statistics.median(b - a for a, b in zip(self.t, self.t[1:])) * 1000 if len(self.t) > 1 else 0.0
        tekst = (f"wzorzec {len(self.t)} tykniec (mediana okresu {okres:.1f} ms); przestoje procesu {len(przestoje)} (razem "
                 f"{sum(przestoje) * 1000:.0f} ms, najdluzszy {max(przestoje, default=0.0) * 1000:.0f} ms); przerwy wzorca przy "
                 f"pracy procesu {len(self.zajete)} (najdluzsza {zajete:.0f} ms); GC {len(gc_ms)} pauz (najdluzsza "
                 f"{max(gc_ms, default=0.0):.1f} ms); priorytet ABOVE_NORMAL: {'tak' if self.priorytet_podniesiony else 'nie'}")
        if self.dysk is not None:
            czasy = sorted((b - a) * 1000 for a, b in self.zapisy)
            tekst += (f"; wzorzec dysku {len(czasy)} zapisow (mediana {czasy[len(czasy) // 2] if czasy else 0:.1f} ms, najdluzszy "
                      f"{czasy[-1] if czasy else 0:.0f} ms), przestoje dysku {len(self.przestoje_dysku)} (razem "
                      f"{sum(b - a for a, b in self.przestoje_dysku) * 1000:.0f} ms)")
            if self.blad_dysku is not None:  # D3 r2: wzorzec dysku przerwal prace - dalszych zastojow dysku nie widac
                tekst += f"; BLAD WZORCA DYSKU (dalsze zastoje niewidoczne): {self.blad_dysku!r}"
        return tekst
