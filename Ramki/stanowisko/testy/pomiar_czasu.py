"""Pomiar czasu w testach czasu rzeczywistego odporny na obciazenie wspoldzielonego PC (E3-T0p).

Testy czasowe (zmiana plytki w ramce < 100 ms, przerwy petli okna < 200 ms) mierza czas scienny. Na PC, na ktorym
liczy kilkanascie obcych procesow, czas scienny rosnie z powodow spoza kodu: proces testow nie dostaje procesora
(wywlaszczenie, przelaczanie miedzy rdzeniami), cala sesja pytest ma tysiace obiektow, wiec pelne zbieranie smieci
(GC) zatrzymuje wszystkie watki na dziesiatki ms. ``PomiarOdporny`` usuwa te przyczyny z pomiaru, a nie z kryterium:

1. GC sesji: ``gc.collect()`` + ``gc.freeze()`` przed pomiarem - obiekty calej sesji pytest poza zbieraniem; obiekty
   tworzone przez kod w trakcie pomiaru sa zbierane normalnie (pauzy GC w trakcie sa zapisywane i licza sie do czasu).
2. Priorytet: klasa priorytetu procesu testow ABOVE_NORMAL na czas pomiaru (Windows, bez uprawnien administratora) -
   obce procesy o zwyklym priorytecie nie odbieraja procesora watkom mierzonym. Nie skraca uspienia ani obliczen
   w kodzie, wiec blokujace wywolanie albo ciezka praca w watku okna / petli ramki nadal przekracza prog.
3. Watek-wzorzec: co ``okres_s`` zapisuje zegar wysokiej rozdzielczosci (``perf_counter``) i licznik cykli procesora
   calego procesu (``QueryProcessCycleTime``). Przerwa wzorca >= ``PROG_PRZERWY_WZORCA_S``, w ktorej proces zuzyl mniej
   niz ``UDZIAL_CPU_PRZESTOJU`` jednego rdzenia, to PRZESTOJ PROCESU: zaden watek procesu nie pracowal, bo system go nie
   uruchamial (wywlaszczenie, stronicowanie pamieci). Tylko taki czas odejmuje ``wlasny(a, b)`` od czasu sciennego.
   Nie jest przestojem (liczy sie do czasu wlasnego):
   - blokujace wywolanie w mierzonym watku (sleep, wejscie-wyjscie, czekanie na inny watek / proces) - GIL zwolniony,
     wzorzec tyka dalej, wiec nie ma przerwy wzorca;
   - ciezka praca w Pythonie - wzorzec dostaje GIL co ``sys.getswitchinterval()`` (5 ms);
   - praca w C/C++ trzymajaca GIL (np. rysowanie Qt, GC) - wzorzec stoi, ale proces zuzywa cykle procesora.
   Ograniczenie: wywolanie biblioteki C, ktore TRZYMA GIL i czeka bez zuzycia procesora, wygladaloby jak przestoj.
Bez Windows (brak ``QueryProcessCycleTime``) przestojow nie ma - pomiar = czas scienny (warunki 1 i 2 bez zmian).
"""
from __future__ import annotations

import bisect
import gc
import os
import threading
import time
from array import array

PROG_PRZERWY_WZORCA_S = 0.020  # wzorzec tyka co 2 ms; 20 ms = 10 tykniec opuszczonych
UDZIAL_CPU_PRZESTOJU = 0.25    # przestoj: proces zuzyl < 1/4 jednego rdzenia w czasie przerwy wzorca
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
        _k32.QueryProcessCycleTime.argtypes = [wintypes.HANDLE, ctypes.POINTER(ctypes.c_uint64)]
        _k32.QueryProcessCycleTime.restype = wintypes.BOOL
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


class PomiarOdporny:
    """Kontekst pomiaru (patrz opis modulu). Po wyjsciu z ``with``: ``przestoj(a, b)``, ``wlasny(a, b)``, ``opis()``.
    Znaczniki czasu mierzonego kodu bierze sie z ``time.perf_counter`` (ten sam zegar co wzorzec)."""

    def __init__(self, okres_s: float = 0.002, priorytet: bool = True, zamroz_gc: bool = True):
        self.okres_s = okres_s
        self.priorytet = priorytet
        self.zamroz_gc = zamroz_gc
        self.t = array("d")
        self.cykle = array("d")
        self.pauzy_gc: list = []      # (poczatek, koniec, pokolenie) pauz GC w trakcie pomiaru
        self.przestoje: list = []     # (poczatek, koniec) przestojow procesu
        self.zajete: list = []        # (poczatek, koniec, udzial CPU) przerw wzorca, w ktorych proces pracowal (GIL zajety)
        self.priorytet_ustawiony = False
        self._cps = 0.0
        self._stop = threading.Event()
        self._watek = threading.Thread(target=self._tykaj, name="pomiar-wzorzec", daemon=True)
        self._gc_start = 0.0
        self._poczatki: list = []
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
        while not self.t:  # pierwszy znacznik wzorca przed poczatkiem pomiaru
            time.sleep(0.001)
        return self

    def __exit__(self, *wyjatek) -> None:
        self._stop.set()
        self._watek.join(5.0)
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
        zegar, spij, t, cykle = time.perf_counter, time.sleep, self.t, self.cykle
        if _k32 is not None:
            licz = _licznik_cykli(_k32.QueryProcessCycleTime, _k32.GetCurrentProcess())
        else:
            def licz() -> int:
                return 0
        while not self._stop.is_set():
            cykle.append(float(licz()))
            t.append(zegar())
            spij(self.okres_s)
        cykle.append(float(licz()))
        t.append(zegar())

    def _wyznacz_przestoje(self) -> None:
        t, c = self.t, self.cykle
        for i in range(len(t) - 1):
            przerwa = t[i + 1] - t[i]
            if przerwa < PROG_PRZERWY_WZORCA_S:
                continue
            udzial = (c[i + 1] - c[i]) / (self._cps * przerwa) if self._cps > 0 else float("inf")
            if udzial < UDZIAL_CPU_PRZESTOJU:
                self.przestoje.append((t[i], t[i + 1]))
            else:
                self.zajete.append((t[i], t[i + 1], udzial))
        self._poczatki = [a for a, _ in self.przestoje]

    # ------------------------------------------------------------------ wyniki
    def przestoj(self, a: float, b: float) -> float:
        """Laczny czas przestojow procesu w przedziale [a, b] (sekundy)."""
        if b <= a or not self.przestoje:
            return 0.0
        wynik = 0.0
        i = max(0, bisect.bisect_right(self._poczatki, a) - 1)
        while i < len(self.przestoje) and self.przestoje[i][0] < b:
            p, k = self.przestoje[i]
            wynik += max(0.0, min(b, k) - max(a, p))
            i += 1
        return wynik

    def wlasny(self, a: float, b: float) -> float:
        """Czas scienny przedzialu [a, b] bez przestojow procesu."""
        return (b - a) - self.przestoj(a, b)

    def przerwy(self, znaczniki) -> list:
        """Dla kolejnych znacznikow (perf_counter) lista (czas scienny, czas wlasny, poczatek) kazdej przerwy."""
        return [(b - a, self.wlasny(a, b), a) for a, b in zip(znaczniki, znaczniki[1:])]

    def cpu_watku(self) -> float:
        """Czas procesora watku wolajacego [s] (cykle / cykle na sekunde; bez Windows ``time.thread_time``) - do opisu
        przerw: duzo CPU = praca w watku, malo CPU bez przestoju = czekanie (uspienie, wejscie-wyjscie, blokada)."""
        if _k32 is None or self._cps <= 0:
            return time.thread_time()
        if getattr(self._lokalne, "licz", None) is None:
            self._lokalne.licz = _licznik_cykli(_k32.QueryThreadCycleTime, _k32.GetCurrentThread())
        return self._lokalne.licz() / self._cps

    def przerwy_petli(self, znaczniki, cpu=None) -> tuple:
        """(najdluzsza przerwa wlasna [s], opis) dla znacznikow kolejnych obiegow petli; ``cpu`` - ``cpu_watku()`` przy
        kazdym znaczniku (opcjonalnie). Opis: najdluzsza przerwa wlasna i najdluzsza scienna z rozbiciem."""
        przerwy = self.przerwy(znaczniki)
        if not przerwy:
            return 0.0, "brak przerw"

        def opis(i: int) -> str:
            sc, wl, _ = przerwy[i]
            cpu_txt = f", CPU watku petli {(cpu[i + 1] - cpu[i]) * 1000:.0f} ms" if cpu else ""
            return f"{sc * 1000:.0f} ms sciennie = {wl * 1000:.0f} ms wlasne + {(sc - wl) * 1000:.0f} ms przestoju procesu{cpu_txt}"

        i_wl = max(range(len(przerwy)), key=lambda i: przerwy[i][1])
        i_sc = max(range(len(przerwy)), key=lambda i: przerwy[i][0])
        return przerwy[i_wl][1], f"najdluzsza wlasna: {opis(i_wl)}; najdluzsza scienna: {opis(i_sc)}"

    def opis(self) -> str:
        przestoje = [b - a for a, b in self.przestoje]
        gc_ms = [(k - p) * 1000 for p, k, _ in self.pauzy_gc]
        zajete = max(((b - a) * 1000 for a, b, _ in self.zajete), default=0.0)
        return (f"wzorzec {len(self.t)} tykniec; przestoje procesu {len(przestoje)} (razem {sum(przestoje) * 1000:.0f} ms, "
                f"najdluzszy {max(przestoje, default=0.0) * 1000:.0f} ms); przerwy wzorca przy pracy procesu {len(self.zajete)} "
                f"(najdluzsza {zajete:.0f} ms); GC {len(gc_ms)} pauz (najdluzsza {max(gc_ms, default=0.0):.1f} ms); "
                f"priorytet ABOVE_NORMAL: {'tak' if self.priorytet_ustawiony else 'nie'}")
