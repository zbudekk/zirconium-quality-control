"""symulator_t14 - program "Stanowisko" z udawanym skanerem do proby T14 "technik obsluguje bez instrukcji" (E3-A11d).

Okno jest prawdziwym oknem programu (``stanowisko.ui``), dane sa wylacznie sztuczne (``kontroler_api.AtrapaKontrolera``:
bez skanera, bez analizy, bez ramek i bez Excela; baza w katalogu tymczasowym, usuwana przy zamknieciu). Skaner udaje
ten skrypt: kazde nacisniecie Spacji w oknie programu = po ``--opoznienie`` sekundach (pasek "Analiza" pokazuje postep)
program dostaje kolejny skan z pliku ``scenariusz_t14.json``. Spacja nacisnieta w trakcie czekania jest pomijana.

Uzycie (wiersz polecen w katalogu Ramki/etap3/t14; PY = python 3.12 z pakietami programu):
    PY symulator_t14.py wieczor            proba wieczorna (5 zadan)
    PY symulator_t14.py rano               proba poranna (6 zadan)
    PY symulator_t14.py --sprawdz          bez ekranu: skrypt sam wykonuje 11 zadan na oknie programu i wypisuje wynik
Opcje: --program KATALOG (katalog programu z pakietem ``stanowisko``; domyslnie ../../stanowisko), --scenariusz PLIK,
--opoznienie S (domyslnie 8), --dziennik PLIK (zapis tego, co skrypt wypisuje w oknie polecen).

W oknie polecen skrypt wypisuje dla prowadzacego: kazda Spacje, kazdy podany skan i - po zamknieciu okna - podsumowanie
(ile plytek, decyzji, pozycji listy; rano: piec, zlecenia kompletne, braki). Kod wyjscia: 0; ``--sprawdz``: 0 = wszystkie
kroki zgodne, 1 = ktorys niezgodny.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
import unicodedata
from pathlib import Path

TU = Path(__file__).resolve().parent
PROGRAM_DOMYSLNY = TU.parent.parent / "stanowisko"
SCENARIUSZ_DOMYSLNY = TU / "scenariusz_t14.json"
FONTY_WINDOWS = Path(r"C:\Windows\Fonts")
TRYBY = ("wieczor", "rano")


def wczytaj_scenariusz(plik: Path) -> dict:
    dane = json.loads(plik.read_text(encoding="ascii"))
    for tryb in TRYBY:
        for skan in dane[tryb]["skany"]:
            skan["gniazda"] = {int(k): v for k, v in skan["gniazda"].items()}
            if skan.get("projekty") is not None:
                skan["projekty"] = {int(k): (tuple(v) if isinstance(v, list) else v) for k, v in skan["projekty"].items()}
    return dane


def bez_ogonkow(tekst: str) -> str:
    """Napis z ekranu programu zapisany w ASCII (okno polecen i plik dziennika nie zaleza od strony kodowej)."""
    tekst = tekst.replace("\u0142", "l").replace("\u0141", "L").replace("\u2014", "-")
    return unicodedata.normalize("NFKD", tekst).encode("ascii", "ignore").decode("ascii")


class Dziennik:
    """Wiersze dla prowadzacego: okno polecen i (opcjonalnie) plik."""

    def __init__(self, plik: Path | None = None):
        self.plik = plik
        self.wiersze: list[str] = []

    def __call__(self, tekst: str) -> None:
        wiersz = f"{dt.datetime.now():%H:%M:%S} {bez_ogonkow(tekst)}"
        self.wiersze.append(wiersz)
        print(wiersz, flush=True)
        if self.plik is not None:
            with open(self.plik, "a", encoding="ascii", newline="\n") as f:
                f.write(wiersz + "\n")


class Symulator:
    """Udawany skaner: po Spacji (``kontroler.starty_skanu`` rosnie) podaje kolejny skan scenariusza po ``opoznienie`` s."""

    def __init__(self, kontroler, tryb: str, skany: list, opoznienie: float, dziennik):
        from PySide6.QtCore import QTimer

        self.k, self.tryb, self.skany, self.opoznienie, self.dziennik = kontroler, tryb, list(skany), float(opoznienie), dziennik
        self.podane: list[int] = []  # skan_id kolejnych skanow
        self._widziane = len(kontroler.starty_skanu)
        self._od: float | None = None
        self._zegar = QTimer()
        self._zegar.setInterval(100)
        self._zegar.timeout.connect(self._tyk)
        self._zegar.start()

    def zatrzymaj(self) -> None:
        self._zegar.stop()

    def _tyk(self) -> None:
        nacisniec = len(self.k.starty_skanu)
        if nacisniec > self._widziane:
            self._widziane = nacisniec
            if self._od is not None:
                self.dziennik("Spacja w trakcie czekania na skan - pominieta")
            elif len(self.podane) >= len(self.skany):
                self.dziennik("Spacja - scenariusz nie ma juz skanow (nic nie przyjdzie)")
            else:
                self._od = time.monotonic()
                self.dziennik(f"Spacja - skan {len(self.podane) + 1} z {len(self.skany)} za {self.opoznienie:g} s")
        if self._od is None:
            return
        udzial = (time.monotonic() - self._od) / self.opoznienie if self.opoznienie > 0 else 1.0
        if udzial < 1.0:
            self.k.symuluj_postep(udzial=min(0.95, udzial))
            return
        self._od = None
        skan = self.skany[len(self.podane)]
        if self.tryb == "rano":
            skan_id = self.k.symuluj_skan_rano(skan["numer"], skan["gniazda"], projekty=skan.get("projekty"))
        else:
            skan_id = self.k.symuluj_skan(skan["rodzaj"], numer=skan["numer"], gniazda=skan["gniazda"], projekty=skan.get("projekty"))
        self.podane.append(skan_id)
        self.dziennik(f"skan podany: {skan['co']}")


def przygotuj_qt(bez_ekranu: bool):
    if bez_ekranu:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        if FONTY_WINDOWS.is_dir():
            os.environ.setdefault("QT_QPA_FONTDIR", str(FONTY_WINDOWS))
    from PySide6 import QtCore, QtGui, QtWidgets  # noqa: F401 - Qt w calosci przed pakietem programu (jak aplikacja.main)

    return QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])


def nowy_kontroler(tryb: str, zegar=None):
    """Atrapa kontrolera w trybie ``tryb``; osoba NIE jest wybrana (jak po kazdym uruchomieniu programu)."""
    from stanowisko import kontroler_api as K

    k = K.AtrapaKontrolera(zegar=zegar)
    if tryb == "rano":
        k.przelacz_tryb(K.TRYB_RANO)
        K.indeks_rano_sztuczny(k.sesja.baza, k.sesja.teraz())
    return k


def podsumowanie(k, tryb: str) -> list[str]:
    """Stan po probie odczytany z kontrolera - pomoc dla prowadzacego przy wypelnianiu arkusza (nie zastepuje obserwacji)."""
    s = k.stan()
    wiersze = [f"PODSUMOWANIE ({tryb}): osoba: {'wybrana' if s.operator else 'NIE WYBRANA'}"]
    if tryb == "wieczor":
        decyzje = [p.decyzja for pl in s.plytki for g in pl.gniazda for p in g.prace if p.decyzja]
        wiersze.append(f"plytek na ekranie: {len(s.plytki)}; decyzji: {len(decyzje)} "
                       f"(ukruszona: {sum(1 for d in decyzje if d.startswith('ukruszona'))}, ok: {sum(1 for d in decyzje if d == 'ok')}); "
                       f"lista do dofrezowania: {len(s.do_dofrezowania_biezaca)}")
        wiersze.append("statusy plytek: " + ", ".join(f"{pl.numer if pl.numer is not None else '?'}: {pl.status}" for pl in s.plytki))
    elif s.rano is not None:
        r = s.rano
        piec = 'brak (nie bylo skanu)' if r.sesja_pieca_id is None else 'otwarty' if r.otwarty else 'ZAMKNIETY'
        wiersze.append(f"piec: {piec}; plytek: {len(r.plytki)}; nierozstrzygniete: "
                       + (", ".join(f"{n} {ile}" for n, ile in dict(r.nierozstrzygniete).items()) or "0"))
        wiersze.append(f"kuwety rozlozone: {', '.join(x.kuweta for x in r.kuwety if x.potwierdzona) or 'brak'}; biezaca: {r.kuweta_biezaca or '-'}")
        wiersze.append(f"kompletne: {', '.join(z.kuweta for z in r.kompletne) or 'brak'}; braki: {', '.join(z.kuweta for z in r.braki) or 'brak'}"
                       + ("" if not r.otwarty else " (piec otwarty - stan prowizoryczny)"))
    return wiersze


def proba(tryb: str, scenariusz: dict, opoznienie: float, dziennik, zamknij_po: float | None = None) -> int:
    """Okno programu dla osoby badanej; wraca po zamknieciu okna (``zamknij_po`` - proba uruchomienia: samo po tylu s)."""
    app = przygotuj_qt(bez_ekranu=False)
    from stanowisko import kontroler_api as K
    from stanowisko import ui

    k = nowy_kontroler(tryb)
    lacznik = K.lacznik_qt(k)
    okno = ui.utworz_okno(k, lacznik)
    symulator = Symulator(k, tryb, scenariusz[tryb]["skany"], opoznienie, dziennik)
    dziennik(f"START proby T14 ({tryb}); skanow w scenariuszu: {len(symulator.skany)}; opoznienie skanu {opoznienie:g} s")
    okno.show()
    if zamknij_po is not None:
        from PySide6.QtCore import QTimer

        QTimer.singleShot(int(zamknij_po * 1000), app.quit)
    app.exec()
    symulator.zatrzymaj()
    for wiersz in podsumowanie(k, tryb):
        dziennik(wiersz)
    lacznik.zatrzymaj()
    k.zamknij()
    return 0


# ----------------------------------------------------------------------------
# --sprawdz: skrypt sam wykonuje 11 zadan T14 na oknie programu (bez ekranu) i czyta wynik z ekranu
# ----------------------------------------------------------------------------
class Kroki:
    def __init__(self, dziennik):
        self.dziennik, self.wyniki = dziennik, []

    def __call__(self, nazwa: str, warunek: bool, szczegoly: str = "") -> bool:
        self.wyniki.append((nazwa, bool(warunek)))
        self.dziennik(f"{'ZGODNE   ' if warunek else 'NIEZGODNE'} {len(self.wyniki):2d}. {nazwa}" + (f" [{szczegoly}]" if szczegoly else ""))
        return bool(warunek)


def _ekran(program: Path):
    narzedzia = program / "narzedzia"
    if not (narzedzia / "zrzuty_instrukcji.py").is_file():
        raise SystemExit(f"BLAD: --sprawdz wymaga {narzedzia / 'zrzuty_instrukcji.py'} (kopia repozytorium, nie sama paczka wydania)")
    sys.path.insert(0, str(narzedzia))
    import zrzuty_instrukcji as Z

    return Z


def sprawdz_wieczor(Z, scenariusz: dict, krok: Kroki, dziennik) -> None:
    from PySide6.QtCore import Qt

    from stanowisko import statusy as ST
    from stanowisko.ui import napisy as N

    ocz = scenariusz["wieczor"]["oczekiwane"]
    k = nowy_kontroler("wieczor", Z.Zegar(Z.WIECZOR))
    e = Z.Ekran(k)
    symulator = Symulator(k, "wieczor", scenariusz["wieczor"]["skany"], 0.3, dziennik)
    try:
        krok("start: program pyta o osobe", e.jest("panel_osoba") and N.KTO_PRACUJE in e.teksty())
        e.klik("osoba_0")
        # zadanie 1: zeskanuj plytke
        e.klawisz(Qt.Key.Key_Space)
        krok("W1 Spacja: program czeka na plik skanu", N.SKANER_CZEKA in e.teksty())
        e.czekaj(lambda: len(symulator.podane) == 1 and e.okno.mapa.numery(), 20.0, "mapa pierwszej plytki")
        podpisy = e.okno.mapa.podpisy()
        krok("W1 po skanie mapa plytki 1 na ekranie", N.PLYTKA_NR.format(numer=1) in e.teksty() and len(podpisy) > 0)
        # zadanie 2: prace do obejrzenia
        czerwone = sorted(nr for nr, p in podpisy.items() if p == ST.STATUSY["czerwony"].napis)
        inne = sorted(nr for nr, p in podpisy.items() if p and p != ST.STATUSY["zielony"].napis)
        krok("W2 czerwone i pozostale prace do obejrzenia jak w scenariuszu", czerwone == ocz["czerwone"] and inne == ocz["do_obejrzenia"],
             f"czerwone {czerwone}, do obejrzenia {inne}")
        e.klik_gniazdo(czerwone[0])
        krok("W2 klikniecie czerwonego gniazda otwiera prace z rozmiarem ubytku",
             e.jest("widok_pracy") and N.NAJWIEKSZY_UBYTEK.split("{")[0] in e.teksty())
        # zadanie 3: jedna ukruszona, jedna OK
        e.klik("przycisk_ukruszona")
        krok('W3 "Ukruszona": podpis gniazda UKRUSZONA', e.okno.mapa.podpisy()[czerwone[0]] == ST.STATUSY["ukruszona"].napis)
        e.klik_gniazdo(czerwone[1])
        e.klik("przycisk_ok")
        krok('W3 "OK": podpis gniazda "OK - zatwierdzona"', e.okno.mapa.podpisy()[czerwone[1]] == ST.STATUSY["zatwierdzona_ok"].napis)
        e.klawisz(Qt.Key.Key_Escape)
        # zadanie 4: popraw ulozenie
        e.klawisz(Qt.Key.Key_Space)
        e.czekaj(lambda: len(symulator.podane) == 2, 20.0, "druga plytka")
        e.czekaj(lambda: e.jest("przycisk_nowa_plytka") or e.jest("komunikat_skan_do_powtorzenia"), 5.0, "sygnal nowej plytki")
        if e.jest("przycisk_nowa_plytka"):  # na plytce 1 zostaly prace do obejrzenia - ekran nie przelacza sam
            e.klik("przycisk_nowa_plytka")
        e.czekaj(lambda: e.jest("komunikat_skan_do_powtorzenia"), 5.0, "komunikat o powtorzeniu skanu")
        powod = ST.POWODY_POWTORZENIA["popraw_ulozenie"].format(gniazda=ocz["popraw_ulozenie"])
        krok('W4 komunikat "Skan do powtorzenia" z powodem i gniazdem', powod in e.teksty()
             and e.okno.mapa.podpisy()[ocz["popraw_ulozenie"]] == ST.STATUSY["popraw_ulozenie"].napis, powod)
        e.klawisz(Qt.Key.Key_Space)
        e.czekaj(lambda: len(symulator.podane) == 3 and e.jest("pytanie_ponowny_skan"), 20.0, "pytanie o ponowny skan")
        e.klik("odp_potwierdz_ponowny_skan")
        e.odczekaj(100)
        zielone = [e.okno.mapa.podpisy()[nr] for nr in scenariusz["wieczor"]["skany"][2]["gniazda"]]
        krok('W4 po ponownym skanie i "Tak, to ponowny skan": plytka 2 zielona, komunikat zniknal',
             not e.jest("komunikat_skan_do_powtorzenia") and set(zielone) == {ST.STATUSY["zielony"].napis}, f"podpisy {zielone}")
        # zadanie 5: lista do dofrezowania
        tabela = e.w("tabela_dofrezowania")
        krok("W5 lista do dofrezowania ma jedna pozycje (kuweta, zab, krazek)", N.LISTA_TYTUL.format(n=1) in e.teksty()
             and tabela.rowCount() == 1 and all(tabela.item(0, i).text() for i in range(3)),
             ", ".join(tabela.item(0, i).text() for i in range(3)) if tabela.rowCount() else "pusta")
        for wiersz in podsumowanie(k, "wieczor"):
            dziennik(wiersz)
    finally:
        symulator.zatrzymaj()
        e.zamknij()
        k.zamknij()


def sprawdz_rano(Z, scenariusz: dict, krok: Kroki, dziennik) -> None:
    from PySide6.QtCore import Qt

    from stanowisko import statusy as ST
    from stanowisko.ui import napisy_rano as NR
    from stanowisko.ui.ekran_rano import teksty_tabeli

    ocz = scenariusz["rano"]["oczekiwane"]
    k = nowy_kontroler("rano", Z.Zegar(Z.RANO))
    e = Z.Ekran(k, Z.OKNO_RANO)
    symulator = Symulator(k, "rano", scenariusz["rano"]["skany"], 0.3, dziennik)

    def biezaca() -> str:
        return e.w("rano_kuweta_biezaca").text().split()[-1]

    def stan_kuwety(kuweta: str) -> str:
        return {w[0]: w[3] for w in teksty_tabeli(e.w("tabela_kuwet"))}.get(kuweta, "?")

    try:
        krok("start: tryb Poranek, program pyta o osobe", e.okno.rano() and e.jest("panel_osoba"))
        e.klik("osoba_0")
        # zadanie 1: dwie plytki pieca
        for n in (1, 2):
            e.klawisz(Qt.Key.Key_Space)
            e.czekaj(lambda: len(symulator.podane) == n and len(e.okno.ekran_rano.mapy()) == n, 20.0, f"plytka {n} pieca")
        krok("R1 dwie plytki pieca na ekranie, piec otwarty", len(e.okno.ekran_rano.mapy()) == 2 and k.stan().rano.otwarty)
        # zadanie 2: dwuznaczna
        skan = symulator.podane[0]
        zolte = [nr for nr, kolor in e.okno.ekran_rano.mapy()[skan].kolory().items() if kolor == ST.status_rano("dwuznaczna").hex]
        krok("R2 zolte gniazdo jak w scenariuszu", zolte == [ocz["zolte"]], f"zolte {zolte}")
        e.klik_gniazdo(ocz["zolte"], skan)
        e.czekaj(lambda: e.jest("kandydat_1_wybierz"), 5.0, "dwaj kandydaci")
        e.klik("kandydat_1_wybierz")
        krok('R2 po "To ten projekt" gniazdo zielone (przypisana)',
             e.okno.ekran_rano.mapy()[skan].kolory()[ocz["zolte"]] == ST.status_rano("przypisana").hex)
        e.klawisz(Qt.Key.Key_Escape)
        # zadanie 3: jedna kuweta wedlug ekranu
        pierwsza = biezaca()
        obwiedzione = sum(len(m.biezace()) for m in e.okno.ekran_rano.mapy().values())
        e.klawisz(Qt.Key.Key_Return)
        krok("R3 biezaca kuweta obwiedziona na plytkach, Enter = rozlozona", obwiedzione > 0 and stan_kuwety(pierwsza) == NR.KUWETA_STAN_ROZLOZONA,
             f"kuweta {pierwsza}, gniazd {obwiedzione}")
        # zadanie 4: pomylka
        druga = biezaca()
        e.klawisz(Qt.Key.Key_Return)
        e.klawisz(Qt.Key.Key_Backspace)
        krok("R4 Backspace cofa ostatnia kuwete (znowu biezaca)", biezaca() == druga and stan_kuwety(druga) != NR.KUWETA_STAN_ROZLOZONA,
             f"kuweta {druga}")
        # zadanie 5: kuweta po numerze
        e.wpisz(ocz["kuweta_do_znalezienia"])
        wpisany = NR.BUFOR.split("{")[0] in e.teksty()
        e.klawisz(Qt.Key.Key_Return)
        krok("R5 numer wpisany cyframi i Enter: ta kuweta jest biezaca", wpisany and biezaca() == ocz["kuweta_do_znalezienia"],
             f"kuweta {biezaca()}")
        # zadanie 6: zamknij piec i braki
        e.klik("przycisk_zamknij_piec")
        e.czekaj(lambda: e.jest("tabela_braki"), 5.0, "lista brakow")
        kompletne = [w[0] for w in teksty_tabeli(e.w("tabela_kompletne"))]
        braki = [w[0] for w in teksty_tabeli(e.w("tabela_braki"))]
        krok('R6 po "Zamknij piec": zlecenia kompletne i braki jak w scenariuszu', kompletne == ocz["kompletne"] and braki == ocz["braki"]
             and not k.stan().rano.otwarty, f"kompletne {kompletne}, braki {braki}")
        for wiersz in podsumowanie(k, "rano"):
            dziennik(wiersz)
    finally:
        symulator.zatrzymaj()
        e.zamknij()
        k.zamknij()


def sprawdz(program: Path, scenariusz: dict, dziennik) -> int:
    przygotuj_qt(bez_ekranu=True)
    Z = _ekran(program)
    Z.przygotuj_qt()
    krok = Kroki(dziennik)
    for nazwa, funkcja in (("wieczor", sprawdz_wieczor), ("rano", sprawdz_rano)):
        try:
            funkcja(Z, scenariusz, krok, dziennik)
        except Exception as blad:  # noqa: BLE001 - krok, ktorego nie dalo sie wykonac, to wynik NIEZGODNE, nie awaria skryptu
            krok(f"{nazwa}: przerwane", False, f"{type(blad).__name__}: {blad}")
    zgodne = sum(1 for _, ok in krok.wyniki if ok)
    dziennik(f"SPRAWDZENIE T14 BEZ EKRANU: zgodne {zgodne} z {len(krok.wyniki)} krokow")
    return 0 if zgodne == len(krok.wyniki) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Proba T14: program "Stanowisko" z udawanym skanerem (dane sztuczne).')
    parser.add_argument("tryb", nargs="?", choices=TRYBY, help="czesc proby: wieczor albo rano")
    parser.add_argument("--sprawdz", action="store_true", help="bez ekranu: skrypt sam wykonuje 11 zadan i wypisuje wynik")
    parser.add_argument("--program", type=Path, default=PROGRAM_DOMYSLNY, help="katalog programu (z pakietem stanowisko)")
    parser.add_argument("--scenariusz", type=Path, default=SCENARIUSZ_DOMYSLNY, help="plik scenariusza (JSON)")
    parser.add_argument("--opoznienie", type=float, default=8.0, metavar="S", help="sekundy od Spacji do skanu (domyslnie 8)")
    parser.add_argument("--dziennik", type=Path, default=None, help="plik, do ktorego trafia to, co skrypt wypisuje")
    parser.add_argument("--zamknij-po", type=float, default=None, metavar="S", help="zamknij okno po S sekundach (proba uruchomienia)")
    args = parser.parse_args(argv)
    if not args.sprawdz and args.tryb is None:
        parser.error("podaj tryb (wieczor albo rano) albo --sprawdz")
    program = args.program.resolve()
    if not (program / "stanowisko" / "kontroler_api.py").is_file():
        print(f"BLAD: w {program} nie ma programu (pakiet stanowisko) - podaj --program KATALOG", file=sys.stderr)
        return 2
    sys.path.insert(0, str(program))
    scenariusz = wczytaj_scenariusz(args.scenariusz)
    dziennik = Dziennik(args.dziennik)
    if args.sprawdz:
        return sprawdz(program, scenariusz, dziennik)
    return proba(args.tryb, scenariusz, args.opoznienie, dziennik, args.zamknij_po)


if __name__ == "__main__":
    raise SystemExit(main())
