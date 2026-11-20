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

W oknie polecen skrypt wypisuje dla prowadzacego: kazda Spacje, kazdy podany skan, kazde polecenie osoby widoczne w stanie
programu (wiersze "osoba: ..." z godzina: decyzja, cofniecie, odpowiedz na pytanie, kuweta rozlozona / cofnieta / wybrana,
wybor projektu, zamkniecie pieca) i - po zamknieciu okna - podsumowanie (ile plytek, decyzji, pozycji listy; rano: piec,
kuwety rozlozone wg dziennika, zlecenia kompletne, braki). Kod wyjscia: 0; ``--sprawdz``: 0 = wszystkie
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
        self.rozlozone: list[str] = []  # kuwety potwierdzone przez osobe (po zamknieciu pieca stan programu ich juz nie podaje)
        self._obraz: dict | None = None  # ostatnio widziany stan programu (do wierszy "osoba: ...")
        self._widziane = len(kontroler.starty_skanu)
        self._od: float | None = None
        self._zegar = QTimer()
        self._zegar.setInterval(100)
        self._zegar.timeout.connect(self._tyk)
        self._zegar.start()

    def zatrzymaj(self) -> None:
        self._zegar.stop()

    def obserwuj(self) -> None:
        """Polecenia osoby odczytane ze zmiany stanu programu -> wiersze "osoba: ..." w dzienniku (D9 recenzji PR #40)."""
        try:
            nowy = _obraz_stanu(self.k, self.tryb)
        except Exception:  # noqa: BLE001 - np. baza zajeta przez chwile: nastepny odczyt za 100 ms
            return
        if self._obraz is not None:
            for wiersz in _wiersze_osoby(self._obraz, nowy, self.tryb):
                self.dziennik(wiersz)
        if self.tryb == "rano" and nowy.get("otwarty"):
            self.rozlozone = list(nowy["rozlozone"])
        self._obraz = nowy

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
        self.obserwuj()
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


def _obraz_stanu(k, tryb: str) -> dict:
    """To, co polecenia osoby zmieniaja w stanie programu (porownywane co 100 ms)."""
    s = k.stan()
    if tryb == "wieczor":
        return {"decyzje": {(pl.skan_id, pl.numer, g.nr, i): p.decyzja for pl in s.plytki for g in pl.gniazda
                            for i, p in enumerate(g.prace) if p.decyzja},
                "pytania": sum(1 for q in s.pytania if q.rodzaj == "ponowny_skan"), "lista": len(s.do_dofrezowania_biezaca),
                "osoba": s.operator or ""}
    r = s.rano
    if r is None:
        return {"osoba": s.operator or ""}
    return {"osoba": s.operator or "", "piec": r.sesja_pieca_id, "otwarty": bool(r.otwarty), "plytek": len(r.plytki),
            "rozlozone": [x.kuweta for x in r.kuwety if x.potwierdzona], "biezaca": r.kuweta_biezaca or "",
            "bez_rozstrzygniecia": sum(ile for _, ile in dict(r.nierozstrzygniete).items())}


def _wiersze_osoby(stary: dict, nowy: dict, tryb: str) -> list[str]:
    """Roznica dwoch obrazow stanu jako wiersze dziennika "osoba: ..."."""
    w = []
    if nowy.get("osoba") != stary.get("osoba"):
        w.append("osoba: wybrana osoba" if nowy.get("osoba") else "osoba: brak wybranej osoby")
    if tryb == "wieczor":
        sd, nd = stary.get("decyzje", {}), nowy.get("decyzje", {})
        for klucz in sorted(set(sd) | set(nd), key=str):
            if sd.get(klucz) != nd.get(klucz):
                miejsce = f"plytka {klucz[1] if klucz[1] is not None else '?'}, gniazdo {klucz[2]}"
                w.append(f"osoba: decyzja {nd[klucz]} - {miejsce}" if klucz in nd else f"osoba: decyzja cofnieta albo uniewazniona - {miejsce}")
        if nowy.get("pytania", 0) < stary.get("pytania", 0):
            w.append("osoba: odpowiedz na pytanie o ponowny skan")
        if nowy.get("lista") != stary.get("lista"):
            w.append(f"lista do dofrezowania: {nowy.get('lista')}")
        return w
    if nowy.get("piec") != stary.get("piec") or "otwarty" not in stary:
        return w
    if stary["otwarty"] and not nowy["otwarty"]:
        return w + ["osoba: piec zamkniety"]
    if not stary["otwarty"] and nowy["otwarty"]:
        w.append("osoba: piec otwarty ponownie")
    if nowy["otwarty"]:
        w += [f"osoba: kuweta {x} rozlozona" for x in nowy["rozlozone"] if x not in stary["rozlozone"]]
        w += [f"osoba: kuweta {x} cofnieta" for x in stary["rozlozone"] if x not in nowy["rozlozone"]]
        if nowy["biezaca"] != stary["biezaca"] and nowy["rozlozone"] == stary["rozlozone"] and nowy["biezaca"] and nowy["plytek"] == stary["plytek"]:
            w.append(f"osoba: wybrana kuweta {nowy['biezaca']}")
        if nowy["plytek"] == stary["plytek"] and nowy["bez_rozstrzygniecia"] < stary["bez_rozstrzygniecia"]:
            w.append(f"osoba: praca rozstrzygnieta (bez rozstrzygniecia zostalo: {nowy['bez_rozstrzygniecia']})")
        elif nowy["plytek"] == stary["plytek"] and nowy["bez_rozstrzygniecia"] > stary["bez_rozstrzygniecia"]:
            w.append(f"osoba: wybor cofniety (bez rozstrzygniecia: {nowy['bez_rozstrzygniecia']})")
    return w


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


def podsumowanie(k, tryb: str, rozlozone: list | None = None) -> list[str]:
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
        if rozlozone is None:
            rozlozone = [x.kuweta for x in r.kuwety if x.potwierdzona]
        wiersze.append(f"kuwety rozlozone przed zamknieciem pieca (wg dziennika): {', '.join(rozlozone) or 'brak'}; biezaca: {r.kuweta_biezaca or '-'}")
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
    symulator.obserwuj()
    symulator.zatrzymaj()
    for wiersz in podsumowanie(k, tryb, symulator.rozlozone):
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
        raise SystemExit(f"BLAD: --sprawdz wymaga {narzedzia / 'zrzuty_instrukcji.py'} (katalog programu z podkatalogiem narzedzia: kopia repozytorium albo program z paczki wydania)")
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
        e.odczekaj(250)
        krok('W3 "Ukruszona": podpis gniazda UKRUSZONA', e.okno.mapa.podpisy()[czerwone[0]] == ST.STATUSY["ukruszona"].napis)
        e.klik_gniazdo(czerwone[1])
        e.klik("przycisk_ok")
        e.odczekaj(250)
        krok('W3 "OK": podpis gniazda "OK - zatwierdzona"', e.okno.mapa.podpisy()[czerwone[1]] == ST.STATUSY["zatwierdzona_ok"].napis)
        e.klawisz(Qt.Key.Key_Escape)
        # zadanie 4: popraw ulozenie
        e.klawisz(Qt.Key.Key_Space)
        e.czekaj(lambda: len(symulator.podane) == 2, 20.0, "druga plytka")
        # na plytce 1 zostaly 2 prace do obejrzenia - ekran nie przelacza sam: przycisk nad lista plytek i pole pod nim
        e.czekaj(lambda: e.jest("przycisk_nowa_plytka") and e.jest("panel_nowy_wynik"), 5.0, "sygnal nowej plytki")
        nowa = N.PLYTKA_NR.format(numer=ocz["plytka_do_poprawienia"])
        krok('W4 ekran zostaje na plytce 1: przycisk "Pokaz nowy wynik" i pole "Nowy wynik czeka" nazywaja plytke 2, komunikatu jeszcze nie widac',
             nowa in e.w("przycisk_nowa_plytka").text() and N.NOWY_WYNIK_TYTUL.format(plytki=nowa) in e.teksty()
             and not e.jest("komunikat_skan_do_powtorzenia"))
        e.klik("przycisk_nowa_plytka")
        e.czekaj(lambda: e.jest("komunikat_skan_do_powtorzenia"), 5.0, "komunikat o powtorzeniu skanu")
        powod = ST.POWODY_POWTORZENIA["popraw_ulozenie"].format(gniazda=ocz["popraw_ulozenie"])
        krok('W4 komunikat "Skan do powtorzenia" z powodem i gniazdem', powod in e.teksty()
             and e.okno.mapa.podpisy()[ocz["popraw_ulozenie"]] == ST.STATUSY["popraw_ulozenie"].napis, powod)
        e.klawisz(Qt.Key.Key_Space)
        e.czekaj(lambda: len(symulator.podane) == 3 and e.jest("pytanie_ponowny_skan"), 20.0, "pytanie o ponowny skan")
        e.odczekaj(250)  # czlowiek czyta pytanie; dziennik zdazy je zobaczyc (odczyt stanu co 100 ms)
        e.klik("odp_potwierdz_ponowny_skan")
        e.odczekaj(250)
        zielone = [e.okno.mapa.podpisy()[nr] for nr in scenariusz["wieczor"]["skany"][2]["gniazda"]]
        krok('W4 po ponownym skanie i "Tak, to ponowny skan": plytka 2 zielona, komunikat zniknal',
             not e.jest("komunikat_skan_do_powtorzenia") and set(zielone) == {ST.STATUSY["zielony"].napis}, f"podpisy {zielone}")
        # zadanie 5: lista do dofrezowania
        tabela = e.w("tabela_dofrezowania")
        krok("W5 lista do dofrezowania ma jedna pozycje (kuweta, zab, krazek)", N.LISTA_TYTUL.format(n=1) in e.teksty()
             and tabela.rowCount() == 1 and all(tabela.item(0, i).text() for i in range(3)),
             ", ".join(tabela.item(0, i).text() for i in range(3)) if tabela.rowCount() else "pusta")
        e.odczekaj(250)
        osoba = [w.split(" ", 1)[1] for w in dziennik.wiersze if " osoba: " in w]
        krok("dziennik notuje polecenia osoby (2 decyzje z miejscem, odpowiedz na pytanie)",
             f"osoba: decyzja ukruszona - plytka 1, gniazdo {czerwone[0]}" in osoba and f"osoba: decyzja ok - plytka 1, gniazdo {czerwone[1]}" in osoba
             and "osoba: odpowiedz na pytanie o ponowny skan" in osoba, f"wierszy osoby: {len(osoba)}")
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
        # "Zamknij piec" przed rozstrzygnieciem zoltej pracy: program pyta, Esc wraca do rozstrzygania (piec zostaje otwarty)
        e.klik("przycisk_zamknij_piec")
        e.czekaj(lambda: e.jest("pytanie_zamknij_mimo"), 5.0, "pytanie przed zamknieciem pieca")
        pytanie = NR.ZAMKNIJ_MIMO_TYTUL in e.teksty() and e.jest("zamknij_mimo_wroc") and e.jest("zamknij_mimo_tak")
        e.klawisz(Qt.Key.Key_Escape)
        e.odczekaj(100)
        krok('R6 za wczesnie: pytanie "Zamknac piec mimo prac bez rozstrzygniecia?", Esc = powrot, piec otwarty',
             pytanie and not e.jest("pytanie_zamknij_mimo") and k.stan().rano.otwarty)
        e.klawisz(Qt.Key.Key_Escape)
        e.klik_gniazdo(ocz["zolte"], skan)
        e.czekaj(lambda: e.jest("kandydat_1_wybierz"), 5.0, "dwaj kandydaci")
        e.klik("kandydat_1_wybierz")
        e.odczekaj(250)
        krok('R2 po "To ten projekt" gniazdo zielone (przypisana)',
             e.okno.ekran_rano.mapy()[skan].kolory()[ocz["zolte"]] == ST.status_rano("przypisana").hex)
        e.klawisz(Qt.Key.Key_Escape)
        # zadanie 3: jedna kuweta wedlug ekranu
        pierwsza = biezaca()
        obwiedzione = sum(len(m.biezace()) for m in e.okno.ekran_rano.mapy().values())
        e.klawisz(Qt.Key.Key_Return)
        e.odczekaj(250)
        krok("R3 biezaca kuweta obwiedziona na plytkach, Enter = rozlozona", obwiedzione > 0 and stan_kuwety(pierwsza) == NR.KUWETA_STAN_ROZLOZONA,
             f"kuweta {pierwsza}, gniazd {obwiedzione}")
        # zadanie 4: pomylka
        druga = biezaca()
        e.klawisz(Qt.Key.Key_Return)
        e.odczekaj(250)
        e.klawisz(Qt.Key.Key_Backspace)
        e.odczekaj(250)
        krok("R4 Backspace cofa ostatnia kuwete (znowu biezaca)", biezaca() == druga and stan_kuwety(druga) != NR.KUWETA_STAN_ROZLOZONA,
             f"kuweta {druga}")
        # zadanie 5: kuweta po numerze
        e.wpisz(ocz["kuweta_do_znalezienia"])
        wpisany = NR.BUFOR.split("{")[0] in e.teksty()
        e.klawisz(Qt.Key.Key_Return)
        e.odczekaj(250)
        krok("R5 numer wpisany cyframi i Enter: ta kuweta jest biezaca", wpisany and biezaca() == ocz["kuweta_do_znalezienia"],
             f"kuweta {biezaca()}")
        # zadanie 6: zamknij piec i braki
        e.klik("przycisk_zamknij_piec")
        e.czekaj(lambda: e.jest("tabela_braki"), 5.0, "lista brakow")
        kompletne = [w[0] for w in teksty_tabeli(e.w("tabela_kompletne"))]
        braki = [w[0] for w in teksty_tabeli(e.w("tabela_braki"))]
        krok('R6 po "Zamknij piec": zlecenia kompletne i braki jak w scenariuszu', kompletne == ocz["kompletne"] and braki == ocz["braki"]
             and not k.stan().rano.otwarty, f"kompletne {kompletne}, braki {braki}")
        e.odczekaj(250)
        osoba = [w.split(" ", 1)[1] for w in dziennik.wiersze if " osoba: " in w]
        wiersze = podsumowanie(k, "rano", symulator.rozlozone)
        krok("dziennik notuje polecenia osoby (wybor projektu, kuweta rozlozona i cofnieta, kuweta wybrana, piec zamkniety)",
             all(x in osoba for x in (f"osoba: kuweta {pierwsza} rozlozona", f"osoba: kuweta {druga} rozlozona", f"osoba: kuweta {druga} cofnieta",
                                      f"osoba: wybrana kuweta {ocz['kuweta_do_znalezienia']}", "osoba: piec zamkniety"))
             and any(x.startswith("osoba: praca rozstrzygnieta") for x in osoba)
             and any(f"(wg dziennika): {pierwsza};" in x for x in wiersze), f"wierszy osoby: {len(osoba)}")
        for wiersz in wiersze:
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
