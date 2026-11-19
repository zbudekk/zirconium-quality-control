"""Pomiar czasu w testach czasu rzeczywistego odporny na obciazenie wspoldzielonego PC (E3-T0p).

Testy czasowe (zmiana plytki w ramce < 100 ms, przerwy petli okna < 200 ms) mierza czas scienny. Na PC, na ktorym
licza obce procesy, czas scienny rosnie z powodow spoza kodu: proces testow nie dostaje procesora (wywlaszczenie),
cala sesja pytest ma tysiace obiektow, wiec pelne zbieranie smieci (GC) zatrzymuje wszystkie watki, a pojedynczy
zapis z ``fsync`` (COMMIT SQLite) potrafi czekac na dysk ponad 200 ms (proba na PC bez sztucznego obciazenia:
1 z 1500 zapisow 226 ms przy medianie 5 ms). ``PomiarOdporny`` usuwa te przyczyny z pomiaru, a nie z kryterium:

1. GC sesji: ``gc.collect()`` + ``gc.freeze()`` przed pomiarem - obiekty calej sesji pytest poza zbieraniem; obiekty
   tworzone przez kod w trakcie pomiaru sa zbierane normalnie (pauzy GC w trakcie sa zapisywane i licza sie do czasu).
2. Priorytet: klasa priorytetu procesu testow ABOVE_NORMAL na czas pomiaru (Windows, bez uprawnien administratora) -
   obce procesy o zwyklym priorytecie nie odbieraja procesora watkom mierzonym. Nie skraca uspienia ani obliczen
   w kodzie, wiec blokujace wywolanie albo ciezka praca w watku okna / petli ramki nadal przekracza prog.
3. Watek-wzorzec: co ``okres_s`` zapisuje zegar wysokiej rozdzielczosci (``perf_counter``) i czas procesora calego
   procesu (``process_time``). Przerwa wzorca >= ``PROG_PRZERWY_WZORCA_S``, w ktorej proces zuzyl mniej niz
   ``UDZIAL_CPU_PRZESTOJU`` jednego rdzenia, to PRZESTOJ PROCESU: zaden watek procesu nie pracowal, bo system go nie
   uruchamial (wywlaszczenie, stronicowanie pamieci). Taki czas odejmuje ``wlasny(a, b)`` od czasu sciennego.
   Nie jest przestojem (liczy sie do czasu wlasnego):
   - blokujace wywolanie w mierzonym watku (sleep, wejscie-wyjscie, czekanie na inny watek / proces) - GIL zwolniony,
     wzorzec tyka dalej, wiec nie ma przerwy wzorca;
   - ciezka praca w Pythonie albo w C/C++ z GIL (rysowanie Qt, GC) - wzorzec czeka na GIL (proba: przerwy do 33 ms przy
     petli w Pythonie), ale proces zuzywa w tym czasie pelny rdzen.
   Ograniczenie: wywolanie biblioteki C, ktore TRZYMA GIL i czeka bez zuzycia procesora, wygladaloby jak przestoj.
4. Wzorzec dysku (tylko z ``dysk=katalog``, testy z zapisem w bazie w watku okna): drugi watek co ``OKRES_DYSKU_S``
   robi minimalny COMMIT SQLite (autocommit, ustawienia domyslne jak baza stanowiska: journal DELETE, synchronous FULL)
   w osobnym pliku w tym samym katalogu. Czas zapisu wzorca ponad ``PROG_ZAPISU_S`` to PRZESTOJ DYSKU (dysk / system
   plikow stal dla kazdego programu). ``przerwy_petli`` odejmuje od przerwy petli czesc wspolna z przestojami dysku, ale
   najwyzej tyle, ile watek petli w tej przerwie NIE liczyl (przerwa - przestoj procesu - CPU watku) - czekanie na dysk
   (czas zapisu wzorca obejmuje tez czekanie na GIL, gdy watek petli liczy - stad to ograniczenie).
   Uspienie, czekanie na inny watek / proces, dodatkowe zapisy o zwyklym czasie - bez przestoju dysku, licza sie w calosci.
   Ograniczenie: blokujace wywolanie w tej samej chwili co przestoj dysku zostaloby (w czesci wspolnej) odjete.
Bez Windows: bez zmiany priorytetu, ``cpu_watku`` z ``time.thread_time``; reszta bez zmian.
"""
from __future__ import annotations

import bisect
import gc
import os
import sqlite3
import threading
import time
from array import array
from pathlib import Path

PROG_PRZERWY_WZORCA_S = 0.020  # wzorzec tyka co 2 ms; 20 ms = 10 tykniec opuszczonych
UDZIAL_CPU_PRZESTOJU = 0.25    # przestoj: proces zuzyl < 1/4 jednego rdzenia w czasie przerwy wzorca
OKRES_DYSKU_S = 0.030          # odstep miedzy zapisami wzorca dysku (zapis trwa zwykle 5-10 ms)
PROG_ZAPISU_S = 0.050          # czas zapisu wzorca dysku ponad to = przestoj dysku (proba: mediana 5 ms, 99. percentyl 10 ms)
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


class PomiarOdporny:
    """Kontekst pomiaru (patrz opis modulu). Po wyjsciu z ``with``: ``przestoj(a, b)``, ``wlasny(a, b)``,
    ``przerwy_petli(znaczniki, cpu)``, ``opis()``. Znaczniki czasu mierzonego kodu bierze sie z ``time.perf_counter``
    (ten sam zegar co wzorce); ``cpu_watku()`` mozna wolac w trakcie pomiaru."""

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
        self.przestoje_dysku: list = []  # (poczatek + PROG_ZAPISU_S, koniec) zapisow wzorca dysku dluzszych niz PROG_ZAPISU_S
        self.zajete: list = []          # (poczatek, koniec, udzial CPU) przerw wzorca, w ktorych proces pracowal (GIL zajety)
        self.priorytet_ustawiony = False
        self._cps = 0.0
        self._stop = threading.Event()
        self._watek = threading.Thread(target=self._tykaj, name="pomiar-wzorzec", daemon=True)
        self._watek_dysku = threading.Thread(target=self._zapisuj, name="pomiar-wzorzec-dysku", daemon=True)
        self._gc_start = 0.0
        self._poczatki: list = []
        self._poczatki_dysku: list = []
        self._lokalne = threading.local()

    # ------------------------------------------------------------------ kontekst
    def __enter__(self) -> "PomiarOdporny":
        if self.zamroz_gc:
            gc.collect()
            gc.freeze()
            gc.callbacks.append(self._gc)
        self._stara_klasa = 0
        if self.priorytet and _k32 is not None:
            proces = _k32.GetCurrentProcess()
            self._stara_klasa = _k32.GetPriorityClass(proces)
            self.priorytet_ustawiony = bool(self._stara_klasa) and bool(_k32.SetPriorityClass(proces, ABOVE_NORMAL_PRIORITY_CLASS))
        self._cps = cykle_na_sekunde()
        self._watek.start()
        if self.dysk is not None:
            self._watek_dysku.start()
        while not self.t or (self.dysk is not None and not self.zapisy):  # pierwsze znaczniki wzorcow przed pomiarem
            time.sleep(0.001)
        return self

    def __exit__(self, *wyjatek) -> None:
        self._stop.set()
        self._watek.join(5.0)
        if self.dysk is not None:
            self._watek_dysku.join(5.0)
        if self.priorytet_ustawiony:
            _k32.SetPriorityClass(_k32.GetCurrentProcess(), self._stara_klasa)
        if self.zamroz_gc:
            gc.callbacks.remove(self._gc)
            gc.unfreeze()
        self._wyznacz_przestoje()

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
        pol = sqlite3.connect(self.dysk / "pomiar_wzorzec_dysku.sqlite", isolation_level=None)
        try:
            pol.execute("CREATE TABLE IF NOT EXISTS wzorzec (t REAL)")
            while not self._stop.is_set():
                t0 = time.perf_counter()
                pol.execute("INSERT INTO wzorzec (t) VALUES (?)", (t0,))
                self.zapisy.append((t0, time.perf_counter()))
                self._stop.wait(OKRES_DYSKU_S)
        finally:
            pol.close()

    def _wyznacz_przestoje(self) -> None:
        t, c = self.t, self.cpu
        for i in range(len(t) - 1):
            przerwa = t[i + 1] - t[i]
            if przerwa < PROG_PRZERWY_WZORCA_S:
                continue
            udzial = (c[i + 1] - c[i]) / przerwa
            if udzial < UDZIAL_CPU_PRZESTOJU:
                self.przestoje.append((t[i], t[i + 1]))
            else:
                self.zajete.append((t[i], t[i + 1], udzial))
        self._poczatki = [a for a, _ in self.przestoje]
        # przestoj dysku = czas zapisu wzorca PONAD prog (pierwsze PROG_ZAPISU_S kazdego zapisu to zwykla praca dysku) -
        # mniej odjete, gdy przestoj dysku przypadkiem trafi na blokujace wywolanie w watku petli
        self.przestoje_dysku = [(a + PROG_ZAPISU_S, b) for a, b in self.zapisy if b - a > PROG_ZAPISU_S]
        self._poczatki_dysku = [a for a, _ in self.przestoje_dysku]

    # ------------------------------------------------------------------ wyniki
    def przestoj(self, a: float, b: float) -> float:
        """Laczny czas przestojow procesu w przedziale [a, b] (sekundy)."""
        return _czesc_wspolna(self.przestoje, self._poczatki, a, b)

    def przestoj_dysku(self, a: float, b: float) -> float:
        """Laczny czas przestojow dysku (wzorzec dysku) w przedziale [a, b] (sekundy)."""
        return _czesc_wspolna(self.przestoje_dysku, self._poczatki_dysku, a, b)

    def wlasny(self, a: float, b: float) -> float:
        """Czas scienny przedzialu [a, b] bez przestojow procesu."""
        return (b - a) - self.przestoj(a, b)

    def cpu_watku(self) -> float:
        """Czas procesora watku wolajacego [s] (cykle / cykle na sekunde; bez Windows ``time.thread_time``) - do opisu
        przerw: duzo CPU = praca w watku, malo CPU bez przestoju = czekanie (uspienie, wejscie-wyjscie, blokada)."""
        if _k32 is None or self._cps <= 0:
            return time.thread_time()
        if getattr(self._lokalne, "licz", None) is None:
            self._lokalne.licz = _licznik_cykli(_k32.QueryThreadCycleTime, _k32.GetCurrentThread())
        return self._lokalne.licz() / self._cps

    def przerwy_petli(self, znaczniki, cpu) -> tuple:
        """(najdluzsza przerwa wlasna [s], opis) dla znacznikow kolejnych obiegow petli; ``cpu`` - ``cpu_watku()`` watku
        petli przy kazdym znaczniku. Przerwa wlasna = scienna - przestoj procesu - czekanie na dysk (czesc wspolna
        z przestojami dysku, najwyzej czas bez CPU watku petli)."""
        przerwy = []
        for i, (a, b) in enumerate(zip(znaczniki, znaczniki[1:])):
            proces = self.przestoj(a, b)
            cpu_przerwy = max(0.0, cpu[i + 1] - cpu[i])
            dysk = min(self.przestoj_dysku(a, b), max(0.0, (b - a) - proces - cpu_przerwy))
            przerwy.append((b - a, (b - a) - proces - dysk, proces, dysk, cpu_przerwy))
        if not przerwy:
            return 0.0, "brak przerw"

        def opis(i: int) -> str:
            sc, wl, proces, dysk, cpu_przerwy = przerwy[i]
            return (f"{sc * 1000:.0f} ms sciennie = {wl * 1000:.0f} ms wlasne + {proces * 1000:.0f} ms przestoju procesu + "
                    f"{dysk * 1000:.0f} ms czekania na dysk (CPU watku petli {cpu_przerwy * 1000:.0f} ms)")

        i_wl = max(range(len(przerwy)), key=lambda i: przerwy[i][1])
        i_sc = max(range(len(przerwy)), key=lambda i: przerwy[i][0])
        return przerwy[i_wl][1], f"najdluzsza wlasna: {opis(i_wl)}; najdluzsza scienna: {opis(i_sc)}"

    def opis(self) -> str:
        przestoje = [b - a for a, b in self.przestoje]
        gc_ms = [(k - p) * 1000 for p, k, _ in self.pauzy_gc]
        zajete = max(((b - a) * 1000 for a, b, _ in self.zajete), default=0.0)
        tekst = (f"wzorzec {len(self.t)} tykniec; przestoje procesu {len(przestoje)} (razem {sum(przestoje) * 1000:.0f} ms, "
                 f"najdluzszy {max(przestoje, default=0.0) * 1000:.0f} ms); przerwy wzorca przy pracy procesu {len(self.zajete)} "
                 f"(najdluzsza {zajete:.0f} ms); GC {len(gc_ms)} pauz (najdluzsza {max(gc_ms, default=0.0):.1f} ms); "
                 f"priorytet ABOVE_NORMAL: {'tak' if self.priorytet_ustawiony else 'nie'}")
        if self.dysk is not None:
            czasy = sorted((b - a) * 1000 for a, b in self.zapisy)
            tekst += (f"; wzorzec dysku {len(czasy)} zapisow (mediana {czasy[len(czasy) // 2] if czasy else 0:.1f} ms, najdluzszy "
                      f"{czasy[-1] if czasy else 0:.0f} ms), przestoje dysku {len(self.przestoje_dysku)}")
        return tekst
