"""Katalog projektów STL z folderu (np. pulpit: ``Prace_test/<zlecenie>/*.stl``) — bez nazw plików.

Użycie (z katalogu stanowisko/):
    py -3.12 narzedzia/katalog_projektow.py --projekty C:/Users/.../Prace_test [--wyjscie dane/katalog.json]
        [--mapa dane/mapa_sciezek.json] [--orientacja auto|brzeg_dol|brzeg_gora] [--bez-gniazd]

Do ``dane/katalog.json`` trafiają tylko identyfikatory (16 znaków SHA‑256 pliku), numery zębów,
typ, objętość, wymiary, liczba trójkątów, szczelność, strona brzegu i gniazdo, w które projekt
wchodzi na każdej płytce (wieczorna ×1,22, poranna ×1,0 — ta sama procedura co generator).
Mapowanie id → ścieżka pliku zapisuje osobno do ``dane/mapa_sciezek.json`` (poza repozytorium).
Na stdout: tabela bez nazw.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from stanowisko import katalog as K  # noqa: E402
from stanowisko import synth as S  # noqa: E402
from stanowisko import uklad as U  # noqa: E402
from stanowisko import ustawienia as UST  # noqa: E402

WSPOLCZYNNIK_WIECZORNA = 1.22  # typowy skurcz zielonej cyrkonii (środek [synth] wspolczynnik_min…max)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--projekty", type=Path, required=True, help="folder z STL projektów (z podfolderami zleceń)")
    ap.add_argument("--wyjscie", type=Path, default=Path("dane/katalog.json"))
    ap.add_argument("--mapa", type=Path, default=Path("dane/mapa_sciezek.json"), help="id → ścieżka (poza repozytorium)")
    ap.add_argument("--orientacja", choices=S.ORIENTACJE, default="auto")
    ap.add_argument("--wspolczynnik", type=float, default=WSPOLCZYNNIK_WIECZORNA, help="skurcz dla płytek wieczornych")
    ap.add_argument("--bez-gniazd", action="store_true", help="nie sprawdzaj, w jakie gniazdo projekt wchodzi (szybciej)")
    a = ap.parse_args()
    if not a.projekty.is_dir():
        raise SystemExit(f"brak folderu projektów: {a.projekty}")
    plytki = None
    if not a.bez_gniazd:
        ust = UST.wczytaj_ustawienia()
        plytki = {}
        for nazwa in ("wieczorna", "poranna"):
            plytki[nazwa] = (U.wczytaj(nazwa, UST.katalog_plytki(ust, nazwa)), a.wspolczynnik if nazwa == "wieczorna" else S.WSPOLCZYNNIK_PORANNA[0])
    katalog, mapa = K.zbuduj(a.projekty, plytki, a.orientacja)
    if not katalog["projekty"]:
        raise SystemExit(f"brak plików STL w {a.projekty}")
    K.zapisz(katalog, mapa, a.wyjscie, a.mapa)
    print(K.streszczenie(katalog))
    print(f"\n{katalog['liczba']} projektów (pominiętych: {katalog['pominiete']}), {katalog['czas_s']} s → {a.wyjscie} (mapa ścieżek: {a.mapa})")


if __name__ == "__main__":
    main()
