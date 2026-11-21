"""E3-P15 p. 2-4: drobne poprawki przed paczka koncowa.

* p. 2 - komunikat ``lista_nie_zapisana`` po odmowie "Zapisz liste do pliku" znika, gdy pozniejszy zapis listy (samoczynny
  albo reczny) sie udal;
* p. 3 - ``Baza.kolumny`` przy bazie zajetej przez inny program: ``BladBazy`` (jak sasiednie metody), nie surowy blad SQLite;
* p. 4 - ``ui/kandydaci.py`` (plik nowy w etapie 3, bez napisow ekranu) ma same bajty ASCII (kontrola higieny T13).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

import test_ui_wieczor as UW

STANOWISKO = Path(__file__).resolve().parents[1]


def _lista_nie_zapisana(k) -> list:
    return sorted(x.id for x in k.stan().komunikaty if x.rodzaj == "lista_nie_zapisana" and not x.ukryte)


@pytest.mark.parametrize("pozniejszy_zapis", ("samoczynny", "reczny"))
def test_p15_lista_nie_zapisana_znika_po_pozniejszym_udanym_zapisie(tmp_path, monkeypatch, pozniejszy_zapis):
    """Odmowa "Zapisz liste do pliku" (dysk nie przyjal pliku) zostawia komunikat ``lista_nie_zapisana``. Gdy potem zapis sie
    uda - samoczynny po zmianie listy albo reczny - komunikatu nie ma (plik jest zapisany, nie ma czego ponawiac)."""
    from stanowisko import kontroler_api as K

    k = K.AtrapaKontrolera(tmp_path / "atrapa", zegar=UW.Zegar())
    try:
        assert k.wybierz_operatora("Technik A")
        skan_id = k.symuluj_skan("zwykla", numer=1)
        plik = k.sesja.baza.plik.parent / K.PLIK_LISTY
        assert k.stan().lista_zapisana and not _lista_nie_zapisana(k)
        prawdziwy = k.sesja.zapisz_do_dofrezowania

        def zepsuty(*a, **kw):
            raise OSError("dysk nie przyjmuje pliku (proba)")

        monkeypatch.setattr(k.sesja, "zapisz_do_dofrezowania", zepsuty)
        odp = k.zapisz_liste()
        assert not odp.ok and odp.kod == "lista_nie_zapisana"
        assert "odmowa:lista_nie_zapisana" in _lista_nie_zapisana(k)
        monkeypatch.setattr(k.sesja, "zapisz_do_dofrezowania", prawdziwy)
        if pozniejszy_zapis == "samoczynny":
            praca = next(g.praca for g in k.stan().plytka(skan_id).gniazda if g.praca is not None)
            assert k.ukruszona(praca.praca_id)  # lista sie zmienila -> kontroler zapisuje plik sam
            assert len(plik.read_text(encoding="utf-8").splitlines()) == 2  # naglowek + 1 pozycja
        else:
            assert k.zapisz_liste().ok
        assert plik.is_file() and k.stan().lista_zapisana
        assert _lista_nie_zapisana(k) == []
    finally:
        k.zamknij()


def test_p15_baza_kolumny_przy_zajetej_bazie_to_blad_bazy(tmp_path):
    """Pierwszy odczyt kolumn tabeli (``PRAGMA table_info``), gdy inny program trzyma baze na wylacznosc: ``BladBazy`` z
    komunikatem "baza jest zajeta" jak w ``wykonaj`` / ``wiersze`` / ``transakcja``; po zwolnieniu ten sam odczyt przechodzi."""
    from stanowisko import baza as B

    plik = tmp_path / "stanowisko.sqlite"
    b = B.otworz(plik, czekaj_ms=100)
    inny = sqlite3.connect(str(plik), isolation_level=None)
    tabela = B.TABELE[0] if not isinstance(B.TABELE, dict) else next(iter(B.TABELE))
    try:
        b._kolumny.clear()
        inny.execute("BEGIN EXCLUSIVE")
        with pytest.raises(B.BladBazy, match="zajeta"):
            b.kolumny(tabela)
        assert tabela not in b._kolumny
        inny.execute("ROLLBACK")
        assert b.kolumny(tabela) and b.kolumny(tabela) == b._kolumny[tabela]
        with pytest.raises(B.BladBazy, match="nieznana tabela"):
            b.kolumny("nie_ma_takiej")
    finally:
        inny.close()
        b.zamknij()


def test_p15_kandydaci_py_same_bajty_ascii():
    dane = (STANOWISKO / "stanowisko" / "ui" / "kandydaci.py").read_bytes()
    obce = [(nr, wiersz[:60]) for nr, wiersz in enumerate(dane.split(b"\n"), 1) if any(b > 127 for b in wiersz)]
    assert not obce, f"wiersze ze znakiem spoza ASCII: {obce}"
