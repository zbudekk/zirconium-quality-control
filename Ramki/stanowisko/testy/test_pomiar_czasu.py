"""Testy pomocnika ``pomiar_czasu`` (E3-T0p runda 2, recenzja PR #33: B1, P1, P2, P3).

Czesc deterministyczna liczy przestoje z recznie podanych znacznikow wzorcow; dwie proby w czasie rzeczywistym (Windows)
sprawdzaja, ze blokada watku petli przez GIL nie jest odejmowana: watek tla trzymajacy GIL ~300 ms (B1) i czekanie w C
z trzymanym GIL 300 ms (P1).
"""
from __future__ import annotations

import gc
import os
import threading
import time
from array import array

import pytest

import pomiar_czasu as PC

WINDOWS = pytest.mark.skipif(os.name != "nt", reason="ctypes.PyDLL kernel32 / priorytet procesu tylko na Windows")


def pomiar_z_danych(t, cpu, zapisy=()) -> PC.PomiarOdporny:
    """PomiarOdporny bez watkow: znaczniki wzorca procesu (t, cpu) i zapisy wzorca dysku podane wprost."""
    pw = PC.PomiarOdporny(dysk=None)
    pw.t, pw.cpu, pw.zapisy = array("d", t), array("d", cpu), list(zapisy)
    pw._wyznacz_przestoje()
    return pw


def znaczniki(od: float, do: float, krok: float = 0.002):
    n = int(round((do - od) / krok))
    return [od + i * krok for i in range(n + 1)]


# ---------------------------------------------------------------------- B1: GIL zajety to nie dysk
def test_b1_dlugi_zapis_wzorca_dysku_w_przerwie_wzorca_procesu_nie_jest_przestojem_dysku():
    t = znaczniki(0.0, 1.0) + znaczniki(1.3, 2.0)  # wzorzec procesu stoi 1,0-1,3 s
    cpu = [x * 0.1 for x in t[:501]] + [0.1 + 0.3 + (x - 1.3) * 0.1 for x in t[501:]]  # w przerwie proces liczyl (GIL zajety)
    pw = pomiar_z_danych(t, cpu, zapisy=[(0.99, 1.305), (1.5, 1.505)])
    assert pw.przestoje == [] and len(pw.zajete) == 1
    assert pw.przestoj_dysku(0.9, 1.4) <= 0.006  # zostaje tylko 5 ms po przerwie wzorca procesu
    przerwa = pw.przerwy_petli([0.99, 1.31], [0.0, 0.0])[0]
    assert PC.ocen_przerwy([przerwa], 0.2)[0] == PC.BLAD


def test_b1_dlugi_zapis_przy_tykajacym_wzorcu_procesu_to_przestoj_dysku():
    t = znaczniki(0.0, 2.0)
    pw = pomiar_z_danych(t, [x * 0.05 for x in t], zapisy=[(1.0, 1.3)])
    assert pw.przestoj_dysku(0.9, 1.4) == pytest.approx(0.25, abs=1e-6)  # czas zapisu ponad 50 ms
    przerwa = pw.przerwy_petli([0.98, 1.31], [0.0, 0.01])[0]
    assert PC.ocen_przerwy([przerwa], 0.2)[0] == PC.POWTORZ_DYSK


def test_roznica_przedzialow():
    assert PC.roznica_przedzialow([(0, 10)], [(2, 3), (5, 6)]) == [(0, 2), (3, 5), (6, 10)]
    assert PC.roznica_przedzialow([(0, 1), (4, 5)], [(0.5, 4.5)]) == [(0, 0.5), (4.5, 5)]
    assert PC.roznica_przedzialow([(1, 2)], [(0, 3)]) == []


# ---------------------------------------------------------------------- P1: limit odejmowania przestoju procesu
def test_p1_przestoj_procesu_odejmowany_najwyzej_50_ms():
    assert PC.LIMIT_PRZESTOJU_S == 0.050  # recenzja PR #33 runda 2, P2
    t = znaczniki(0.0, 1.0) + znaczniki(1.3, 2.0)  # wzorzec stoi 300 ms, proces bez CPU
    pw = pomiar_z_danych(t, [0.0] * len(t))
    assert len(pw.przestoje) == 1
    assert pw.przestoj(0.9, 1.4) == pytest.approx(PC.LIMIT_PRZESTOJU_S)
    assert pw.wlasny(0.99, 1.31) == pytest.approx(0.32 - PC.LIMIT_PRZESTOJU_S)
    assert PC.ocen_przerwy(pw.przerwy_petli([0.99, 1.31], [0.0, 0.0]), 0.2)[0] == PC.BLAD  # 270 ms po odjeciu 50 ms
    assert PC.ocen_przerwy(pw.przerwy_petli([1.05, 1.29], [0.0, 0.0]), 0.2)[0] == PC.POWTORZ_PROCES  # 240 - 50 ms


# ---------------------------------------------------------------------- P2: przestoj dysku = powtorzenie, nie odejmowanie
def test_p2_ocena_i_limity_powtorzen():
    P = PC.Przerwa
    assert PC.ocen_przerwy([P(0.05), P(0.19)], 0.2)[0] == PC.OK
    assert PC.ocen_przerwy([P(0.25, dysk=0.1)], 0.2)[0] == PC.POWTORZ_DYSK
    assert PC.ocen_przerwy([P(0.25, dysk=0.1), P(0.3)], 0.2)[0] == PC.BLAD  # jedna przerwa bez wyjasnienia wystarczy
    p = PC.Powtorki()
    assert p.dalej(PC.POWTORZ_PROCES, "a") and not p.dalej(PC.POWTORZ_PROCES, "b")  # proces najwyzej raz
    p = PC.Powtorki()
    assert p.dalej(PC.POWTORZ_DYSK, "a") and p.dalej(PC.POWTORZ_DYSK, "b") and not p.dalej(PC.POWTORZ_DYSK, "c")
    p = PC.Powtorki()
    assert p.dalej(PC.POWTORZ_PROCES, "a") and p.dalej(PC.POWTORZ_DYSK, "b") and not p.dalej(PC.POWTORZ_DYSK, "c")
    assert not PC.Powtorki().dalej(PC.BLAD, "x") and not PC.Powtorki().dalej(PC.OK, "x")
    assert "proba 3" in p.opis()
    assert PC.gorsza(PC.OK, PC.POWTORZ_DYSK, PC.POWTORZ_PROCES) == PC.POWTORZ_DYSK


# ---------------------------------------------------------------------- P3: start wzorcow z limitem, sprzatanie
def _stan_procesu():
    klasa = PC._k32.GetPriorityClass(PC._k32.GetCurrentProcess()) if PC._k32 is not None else None
    return klasa, gc.get_freeze_count(), len(gc.callbacks)


def test_p3_wzorzec_dysku_bez_katalogu_blad_w_enter_i_stan_przywrocony(tmp_path):
    przed = _stan_procesu()
    pw = PC.PomiarOdporny(dysk=tmp_path / "nie_ma_takiego_katalogu")
    t0 = time.perf_counter()
    with pytest.raises(RuntimeError, match="nie wystartowal"):
        with pw:
            pass
    assert time.perf_counter() - t0 < PC.LIMIT_STARTU_S + 2
    assert _stan_procesu() == przed
    assert not pw._watek.is_alive() and not pw._watek_dysku.is_alive()


def test_p3_wyjatek_w_pomiarze_i_ponowne_uzycie_przywracaja_stan(tmp_path):
    przed = _stan_procesu()
    pw = PC.PomiarOdporny(dysk=tmp_path)
    with pytest.raises(ZeroDivisionError):
        with pw:
            assert gc.get_freeze_count() > 0
            1 / 0
    assert _stan_procesu() == przed and not pw._watek.is_alive()
    with pytest.raises(RuntimeError):  # watkow wzorca nie da sie uruchomic drugi raz
        with pw:
            pass
    assert _stan_procesu() == przed


# ---------------------------------------------------------------------- proby w czasie rzeczywistym
def petla_10_ms(pw, czas_s: float, w_trakcie) -> list:
    """Petla jak zegar okna (sleep 10 ms) przez ``czas_s``; po 0,3 s jeden raz ``w_trakcie()``; zwraca przerwy petli."""
    zn, cpu, zrobione = [time.perf_counter()], [pw.cpu_watku()], False
    while time.perf_counter() < zn[0] + czas_s:
        time.sleep(0.010)
        if not zrobione and time.perf_counter() > zn[0] + 0.3:
            zrobione = True
            w_trakcie()
        zn.append(time.perf_counter())
        cpu.append(pw.cpu_watku())
    return zn, cpu


def _sum_300_ms() -> int:
    n = 2_000_000
    t0 = time.perf_counter()
    sum(range(n))
    return max(n, int(n * 0.30 / (time.perf_counter() - t0)))


@WINDOWS
def test_b1_watek_tla_trzymajacy_gil_300_ms_to_porazka(tmp_path):
    """Watek tla programu trzyma GIL w C ~300 ms - okno stoi; nie moze byc wyjasnione jako dysk ani przestoj procesu."""
    n = _sum_300_ms()
    for proba in range(3):
        watki = []
        with PC.PomiarOdporny(dysk=tmp_path) as pw:
            def tlo():
                w = threading.Thread(target=lambda: sum(range(n)))
                w.start()
                watki.append(w)

            zn, cpu = petla_10_ms(pw, 1.0, tlo)
            watki[0].join()
        ocena, najdluzsza = PC.ocen_przerwy(pw.przerwy_petli(zn, cpu), 0.2)
        assert najdluzsza.sc > 0.2, f"watek tla nie zablokowal petli: {najdluzsza.opis()}"
        assert ocena == PC.BLAD, (proba, najdluzsza.opis(), pw.opis())


@WINDOWS
def test_p1_czekanie_w_c_z_trzymanym_gil_300_ms_to_porazka(tmp_path):
    """``Sleep(300)`` przez ``ctypes.PyDLL`` (GIL trzymany, CPU 0) wyglada jak przestoj procesu - odjete najwyzej 50 ms."""
    import ctypes

    for proba in range(3):
        with PC.PomiarOdporny(dysk=tmp_path) as pw:
            zn, cpu = petla_10_ms(pw, 0.8, lambda: ctypes.PyDLL("kernel32").Sleep(300))
        ocena, najdluzsza = PC.ocen_przerwy(pw.przerwy_petli(zn, cpu), 0.2)
        assert ocena == PC.BLAD, (proba, najdluzsza.opis(), pw.opis())

@WINDOWS
def test_d1_sciezka_powtorzenia_czekanie_w_c_z_gil_raz_pass_z_ostrzezeniem_zawsze_porazka(tmp_path):
    """Sciezka powtorzenia od poczatku do konca (recenzja PR #33 runda 2, D1): ``PyDLL Sleep(210)`` w petli daje przerwe
    ok. 220 ms (> 200 ms), a po odjeciu najwyzej 50 ms przestoju procesu ok. 170 ms - ocena ``powtorz_proces``.
    (i) tylko w 1. pomiarze -> PASS w 2. pomiarze z ostrzezeniem i historia; (ii) w kazdym pomiarze -> porazka po 2."""
    import ctypes

    def pomiar(z_blokada: bool):
        with PC.PomiarOdporny(dysk=tmp_path) as pw:
            zn, cpu = petla_10_ms(pw, 0.6, (lambda: ctypes.PyDLL("kernel32").Sleep(210)) if z_blokada else (lambda: None))
        ocena, najdluzsza = PC.ocen_przerwy(pw.przerwy_petli(zn, cpu), 0.2)
        return ocena, najdluzsza.opis()

    def caly_test(blokada_w_pomiarze):
        powtorki, n = PC.Powtorki(), 0
        while True:
            ocena, opis = pomiar(blokada_w_pomiarze(n))
            n += 1
            if not powtorki.dalej(ocena, opis):
                return ocena, powtorki

    with pytest.warns(UserWarning, match="dopiero w pomiarze 2"):
        ocena, powtorki = caly_test(lambda n: n == 0)
        powtorki.ostrzez("D1", ocena)
    assert ocena == PC.OK and powtorki.historia[0].startswith(f"proba 1: {PC.POWTORZ_PROCES}"), powtorki.opis()
    ocena, powtorki = caly_test(lambda n: True)
    assert ocena == PC.POWTORZ_PROCES and len(powtorki.historia) == 2, powtorki.opis()


def test_p1_ostrzezenie_tylko_przy_sukcesie_po_powtorzeniu(recwarn):
    p = PC.Powtorki()
    p.dalej(PC.OK, "od razu")
    p.ostrzez("x", PC.OK)
    assert not recwarn.list
    p = PC.Powtorki()
    p.dalej(PC.POWTORZ_DYSK, "zastoj dysku")
    p.dalej(PC.BLAD, "regresja")
    p.ostrzez("x", PC.BLAD)  # porazke zglasza asercja testu, nie ostrzezenie
    assert not recwarn.list


def test_d3_blad_wzorca_dysku_w_opisie():
    pw = pomiar_z_danych(znaczniki(0.0, 0.1), [0.0] * 51)
    pw.dysk, pw.blad_dysku = object(), OSError("dysk pelny")
    assert "BLAD WZORCA DYSKU" in pw.opis() and "dysk pelny" in pw.opis()
