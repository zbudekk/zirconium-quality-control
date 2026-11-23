"""Proby sesji S2 (zawieszenia) - prawdziwa ``aplikacja.Aplikacja`` z analiza sztuczna (``test_kontroler_api``), bez okna.

Uruchomienie (z katalogu <worktree>\\Ramki\\stanowisko, 1 proces python + proces roboczy silnika):
    <PC-katalog>\\koordynator\\narz\\py.cmd ..\\analiza_kodu_2026-11-23\\S2\\proba_s2.py a
    <PC-katalog>\\koordynator\\narz\\py.cmd ..\\analiza_kodu_2026-11-23\\S2\\proba_s2.py b
    <PC-katalog>\\koordynator\\narz\\py.cmd ..\\analiza_kodu_2026-11-23\\S2\\proba_s2.py d
Wynik: jedna linia JSON na probe na wyjsciu i w pliku S2\\proba_s2_<litera>.json. Wszystko pisze tylko do S2\\tmp.

a - nowy skan pojawia sie w folderze skanera, gdy baza jest zajeta przez inne polaczenie (EXCLUSIVE, potem IMMEDIATE):
    ile trwa najdluzsze ``przetworz()`` (watek okna) i czy skan po zwolnieniu bazy zostanie przeanalizowany.
b - wynik analizy przychodzi, gdy baza jest zajeta: ile czasu z 40 s watek okna stoi w ``przetworz()``.
d - 10 plikow zastanych w folderze skanera przy starcie (kazdy "analiza" 1 s) + swiezy skan zaraz po starcie:
    po ilu sekundach swiezy skan ma wynik w bazie.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import sys
import time
from pathlib import Path

TU = Path(__file__).resolve().parent
STANOWISKO = TU.parent.parent / "stanowisko"
for _p in (STANOWISKO, STANOWISKO / "testy", STANOWISKO / "narzedzia"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


def _katalog(nazwa: str) -> Path:
    k = TU / "tmp" / nazwa
    shutil.rmtree(k, ignore_errors=True)
    k.mkdir(parents=True, exist_ok=True)
    return k


def _stanowisko(T, tmp: Path):
    return T.StanowiskoAplikacji(tmp, parametry_silnika={"katalog_roboczy": str(tmp / "robocze")})


def _pompuj(st, sekund: float, warunek=None) -> list:
    """Wola ``przetworz()`` co 10 ms przez ``sekund`` (albo do ``warunek()``); zwraca [(chwila od poczatku, czas wywolania)]."""
    t0, czasy = time.monotonic(), []
    while time.monotonic() - t0 < sekund:
        a = time.perf_counter()
        st.k.przetworz()
        czasy.append((round(time.monotonic() - t0, 2), round(time.perf_counter() - a, 3)))
        if warunek is not None and warunek():
            break
        time.sleep(0.01)
    return czasy


def _ile(st, sql: str, parametry: tuple = ()) -> int:
    return st.k.sesja.baza.wiersz(sql, parametry)["n"]


def _dlugie(czasy: list, prog: float = 0.5) -> list:
    return [(t, c) for t, c in czasy if c >= prog]


def proba_a(T) -> list:
    wyniki = []
    for blokada in ("EXCLUSIVE", "IMMEDIATE"):
        st = _stanowisko(T, _katalog(f"a_{blokada.lower()}"))
        try:
            st.k.wybierz_operatora("Technik A")
            st.wrzuc("czysta", numer=1)  # rozgrzewka: proces silnika dziala, jeden skan przyjety
            obcy = sqlite3.connect(str(st.k.sesja.baza.plik), timeout=0.1, isolation_level=None)
            obcy.execute("BEGIN " + blokada)
            st.zapisz(st.opis("czysta", 2, None, None, None, 0))  # nowy skan przy zajetej bazie
            czasy = _pompuj(st, 12.0)
            obcy.execute("ROLLBACK")
            obcy.close()
            po = _pompuj(st, 15.0)
            s = st.k.stan()
            wyniki.append({
                "proba": "a", "blokada": blokada, "max_przetworz_s": max(c for _, c in czasy), "dlugie_przetworz": _dlugie(czasy),
                "max_przetworz_po_zwolnieniu_s": max(c for _, c in po), "zdarzen_scannera": st.k.scanner.stan()["zdarzen"],
                "plytek_w_stanie": len(s.plytki), "skanow_w_bazie": _ile(st, "SELECT count(*) AS n FROM skany"),
                "wpisow_nowy_skan": _ile(st, "SELECT count(*) AS n FROM zdarzenia WHERE typ = 'nowy_skan'"),
                "zlecone": len(st.k._zlecone), "wstrzymane": len(st.k._wstrzymane), "do_zapisu": len(st.k._do_zapisu),
                "kolejka": str(s.kolejka), "komunikaty": [k.rodzaj for k in s.komunikaty]})
        finally:
            st.koniec()
    return wyniki


def proba_b(T) -> list:
    wyniki = []
    for blokada in ("IMMEDIATE",):
        st = _stanowisko(T, _katalog(f"b_{blokada.lower()}"))
        try:
            st.k.wybierz_operatora("Technik A")
            st.wrzuc("czysta", numer=1)
            opis = st.opis("czysta", 2, None, None, None, 0)
            opis["spij"] = 2.0  # analiza trwa 2 s - baza zostaje zajeta w jej trakcie
            st.zapisz(opis)
            _pompuj(st, 20.0, lambda: bool(st.k._zlecone))
            obcy = sqlite3.connect(str(st.k.sesja.baza.plik), timeout=0.1, isolation_level=None)
            obcy.execute("BEGIN " + blokada)
            czasy = _pompuj(st, 40.0)
            s = st.k.stan()
            w_trakcie = {"kolejka": str(s.kolejka), "komunikaty": [k.rodzaj for k in s.komunikaty], "do_zapisu": len(st.k._do_zapisu),
                         "proby_zapisu": [d.proby for d in st.k._do_zapisu]}
            obcy.execute("ROLLBACK")
            obcy.close()
            t0 = time.monotonic()
            _pompuj(st, 60.0, lambda: len(st.k.stan().plytki) >= 2)
            dl = _dlugie(czasy)
            wyniki.append({
                "proba": "b", "blokada": blokada, "okno_pomiaru_s": 40.0, "max_przetworz_s": max(c for _, c in czasy), "dlugie_przetworz": dl,
                "suma_dlugich_s": round(sum(c for _, c in dl), 2), "w_trakcie": w_trakcie,
                "po_zwolnieniu_plytka_po_s": round(time.monotonic() - t0, 2), "plytek_w_stanie": len(st.k.stan().plytki),
                "skanow_w_bazie": _ile(st, "SELECT count(*) AS n FROM skany")})
        finally:
            st.koniec()
    return wyniki


def proba_d(T) -> list:
    tmp = _katalog("d")
    eksport = tmp / "eksport"
    eksport.mkdir(parents=True, exist_ok=True)
    ile = 10
    for i in range(ile):  # pliki zastane: zapisane, zanim program wystartowal
        opis = {"gniazda": {"1": "zielony"}, "numer": 1 + i % 3, "uklad": "wieczorna", "poza": 0, "spij": 1.0, "sol": f"zastany-{i}"}
        (eksport / f"stary_{i:03d}.stl").write_bytes(T.plik_skanu(opis))
    time.sleep(1.2)
    t_start = time.monotonic()
    st = _stanowisko(T, tmp)
    try:
        czas_startu = round(time.monotonic() - t_start, 2)
        plik = st.zapisz(st.opis("czysta", 3, None, None, None, 0))  # swiezy skan technika zaraz po starcie programu
        sha16 = hashlib.sha256(plik.read_bytes()).hexdigest()[:16]
        t0 = time.monotonic()
        _pompuj(st, 120.0, lambda: _ile(st, "SELECT count(*) AS n FROM skany WHERE sha16 = ?", (sha16,)) > 0)
        czekal = round(time.monotonic() - t0, 2)
        przed = _ile(st, "SELECT count(*) AS n FROM skany WHERE sha16 != ?", (sha16,))
        s = st.k.stan()
        return [{"proba": "d", "plikow_zastanych": ile, "analiza_jednego_s": 1.0, "start_programu_s": czas_startu,
                 "swiezy_skan_wynik_po_s": czekal, "skanow_zastanych_przed_swiezym": przed, "plytek_w_stanie": len(s.plytki),
                 "komunikaty": [k.rodzaj for k in s.komunikaty], "pytania": [p.rodzaj for p in s.pytania]}]
    finally:
        st.koniec()


def main() -> int:
    import stanowisko  # noqa: F401 - przed trimesh / numpy (E3-A11w)
    import test_kontroler_api as T

    ktora = (sys.argv[1] if len(sys.argv) > 1 else "").lower()
    funkcja = {"a": proba_a, "b": proba_b, "d": proba_d}.get(ktora)
    if funkcja is None:
        print("uzycie: proba_s2.py a|b|d")
        return 2
    t0 = time.monotonic()
    wyniki = funkcja(T)
    for w in wyniki:
        w["czas_proby_s"] = round(time.monotonic() - t0, 1)
        print(json.dumps(w, ensure_ascii=True))
    (TU / f"proba_s2_{ktora}.json").write_text("\n".join(json.dumps(w, ensure_ascii=True) for w in wyniki) + "\n", encoding="ascii")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
