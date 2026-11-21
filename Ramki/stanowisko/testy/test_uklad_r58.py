"""Modele plytek okraglych ramkowych n1-n6 (R58) w programie stanowiska - paczka E3-O1 (21.11.2026).

Dwa nowe uklady ``okragla_ramkowa_wieczorna`` (numery 1, 2, 3) i ``okragla_ramkowa_poranna`` (4, 5, 6): 10 plikow w
``modele_plytek/`` to KOPIE BAJTOWE plikow R58 (2 x ``uklad.json`` z ``Ramki/wyniki_v2/json/`` + 6 STL numerowanych
+ 2 STL bazowe; decyzja wlasciciela nr 1 z 21.11.2026). 28 plikow dotychczasowych zostaje bajt w bajt (sumy policzone
z ``main`` beddde7 przed zmianami). ``uklad.py`` nie jest zmieniany: nowe pola R58 (``magnet_pockets``, ``cover_groove``,
``key_slot``) sa przez program pomijane, wierzch plytki (gniazda, stozki, dolki kodu, sciecie) jest taki jak w plytce
okraglej testowej n8 / n9.
"""
from __future__ import annotations

import hashlib
import json
import subprocess

import pytest
import trimesh

from conftest import RAMKI, STANOWISKO
from stanowisko import plate, synth, uklad as U, ustawienia as UST

MODELE = STANOWISKO / "modele_plytek"
RAMKOWE = ("okragla_ramkowa_wieczorna", "okragla_ramkowa_poranna")
NUMERY = {"okragla_ramkowa_wieczorna": [1, 2, 3], "okragla_ramkowa_poranna": [4, 5, 6]}
GNIAZD = {"okragla_ramkowa_wieczorna": 19, "okragla_ramkowa_poranna": 24}
LISTA_R58 = RAMKI / "wyniki_v2" / "raport" / "sha256_stl_po_R58.txt"

# plik w modele_plytek -> (plik zrodlowy R58, SHA-256); sumy STL = lista R58 (LISTA_R58), sumy JSON = pliki R58 w repo
NOWE = {
    "okragla_ramkowa_wieczorna/uklad.json": ("json/uklad_gniazd_okragla_ramkowa_wieczorna.json",
                                             "d66ef99b799f37c241b83b73d979ab70a5810cec7fc4aec369f3e0da6c4c17a9"),
    "okragla_ramkowa_wieczorna/plytka_n1.stl": ("stl/ramka_plytka_okragla_ramkowa_wieczorna_n1_v2.stl",
                                                "84d361e2389bef12fd07278bf3e2e65fd170c83d4012f8fbbfa12b8ad172325f"),
    "okragla_ramkowa_wieczorna/plytka_n2.stl": ("stl/ramka_plytka_okragla_ramkowa_wieczorna_n2_v2.stl",
                                                "7848aa2395638b338e4bd2e83473b1329c53c61500a7ec1ba5a63a8c5aaaaa94"),
    "okragla_ramkowa_wieczorna/plytka_n3.stl": ("stl/ramka_plytka_okragla_ramkowa_wieczorna_n3_v2.stl",
                                                "1b8ac3d390870f0a4607b3289f50201ef28cf2049801ac853aaa1427735321aa"),
    "okragla_ramkowa_wieczorna/plytka_bazowa.stl": ("stl/ramka_plytka_okragla_ramkowa_wieczorna_v2.stl",
                                                    "322eb892b7acf81ce5e0ff5f437436b44f22490a662f1b1bd9939353b4a4125c"),
    "okragla_ramkowa_poranna/uklad.json": ("json/uklad_gniazd_okragla_ramkowa_poranna.json",
                                           "ab6e02a0a9602216d4b9251a725d4281a4e04c1db6d1261af6a7ab97e4517412"),
    "okragla_ramkowa_poranna/plytka_n4.stl": ("stl/ramka_plytka_okragla_ramkowa_poranna_n4_v2.stl",
                                              "5d81f55b8b114ba9cf307bb4ba63e70083aa6570ab0bb646acef69b8cd6cceb5"),
    "okragla_ramkowa_poranna/plytka_n5.stl": ("stl/ramka_plytka_okragla_ramkowa_poranna_n5_v2.stl",
                                              "64867b5b63a31db88715c9c9636c33015566bbe48af2c8f4a90330797f063381"),
    "okragla_ramkowa_poranna/plytka_n6.stl": ("stl/ramka_plytka_okragla_ramkowa_poranna_n6_v2.stl",
                                              "7630a029157b2fc65144c5f6b32ad28c02048f0642855cc3d23c2570ea28991e"),
    "okragla_ramkowa_poranna/plytka_bazowa.stl": ("stl/ramka_plytka_okragla_ramkowa_poranna_v2.stl",
                                                  "845e4bd61b40562010dec24b18ee873e90d8937f07728f81589c407f826ba266"),
}

# 28 plikow modele_plytek/** z main beddde7 (git show beddde7:<plik> | sha256), policzone 21.11.2026 PRZED zmianami paczki
DOTYCHCZASOWE = {
    "okragla_poranna/plytka_bazowa.stl": "e35835d7618e6665fdda84cbe2d65a3c7b46d7f9cef1e99141b42af2eb9e22c7",
    "okragla_poranna/plytka_n9.stl": "f9444e6f14e37d9d0bcc8ae84cfec5249146bce20420c53a86a73965727fd4c4",
    "okragla_poranna/uklad.json": "b943e6c5dd54a8b3b35974908a3910bd654062bb659284a649ee68679174268e",
    "okragla_poranna_r54/plytka_bazowa.stl": "713aef6c0cef1dc2fc3b3809ce3756557b41b0cc4268c85166e985f18f74e0dd",
    "okragla_poranna_r54/plytka_n9.stl": "a87bc6c5f8f0323bc202e5ebfeab6be6d7c8432beba6aafe4a8372d70666e2be",
    "okragla_poranna_r54/uklad.json": "5adcc977dd9b456e5261d1e2225bc386def23a165d79de124b5733fb9ef43d53",
    "okragla_wieczorna/plytka_bazowa.stl": "aad8033e6c1d1f34b43825861d18e82b45599a76ebb453c294400a7713ebbd83",
    "okragla_wieczorna/plytka_n8.stl": "d5591f652ea1b6b23825abb5ad05ac12b78d17f6abb52946bd1a010ef5e4ff54",
    "okragla_wieczorna/uklad.json": "c07791f4bb976be2ad5eddaaeefe011b2384ea71e3fabd25cf55da690eb14a33",
    "okragla_wieczorna_r54/plytka_bazowa.stl": "3ca8178262f7f1f253480ca1d49adbbccf2db3648647814ec2390311e5553ace",
    "okragla_wieczorna_r54/plytka_n8.stl": "c4c8a18d0b83fd2a2903f5d782188a8de4827ee07c55dca9df7bd0d8e4a37d32",
    "okragla_wieczorna_r54/uklad.json": "260f807c630211dcd3c1b552cded03838d1367156c856fc51f3a3f7ec12f0743",
    "poranna/plytka_n4.stl": "20f15f2214f6c9a9baf2b4701e7f99bfbc5f739b6379398294e9f931b8763237",
    "poranna/plytka_n5.stl": "a275775b9c9b5ddd015b68659f213505bdd28b9476cad5e13405bef2df5b64d1",
    "poranna/plytka_n6.stl": "c44be370c8b9ad2b70f9e486c3f6f9d2b227b91f2a6544bfe14bf7e66bd65b21",
    "poranna/uklad.json": "46e474b759c4b78b7975fc8c5580c9916a4cc64c6a88cd4711b2207e3978b98b",
    "poranna_r54/plytka_n4.stl": "a8d07cbeb0dafc0e55d3fe2fe516c7d3e854a6259bce587785b796d34b54c65e",
    "poranna_r54/plytka_n5.stl": "159503ca4cd66b90a1e2441cae64016901ed83390b48a27345f9484ac1a05830",
    "poranna_r54/plytka_n6.stl": "0d5d712d42084a19846f24d385484d01b2254c5c1ec3945d71cfd3493816f15e",
    "poranna_r54/uklad.json": "6e8290c3a7c4becd3b065f8ccd39da9e8f8a2f0cb9bab6a1464fbcda84995812",
    "wieczorna/plytka_n1.stl": "3b0db5452a0cd9533464772c10b67c05fa7a006fcdb3d140a74af275e79946f7",
    "wieczorna/plytka_n2.stl": "b87026134b25cf32a84a231b73d5c4eb9fde4dfeb5b16b627cf09ccc3f29c999",
    "wieczorna/plytka_n3.stl": "59e615d596771c6c0351284c710e94e406a965afef423ffeae5cd18ffa2c4dd3",
    "wieczorna/uklad.json": "7ae07ba861950724cf68ce9de0b45f3a05436089df8f73b3b4fc07bf2cc05869",
    "wieczorna_r54/plytka_n1.stl": "515d32d3dd8a69ae0a94d293a639b201f2d9ce9af19df664ad1b44b59408f775",
    "wieczorna_r54/plytka_n2.stl": "360cff9ddd6bbcf8a84b463fed930532612a38118006f1550c2df01b02fa852d",
    "wieczorna_r54/plytka_n3.stl": "2fc7040e212ace4a8efda17f61909ca09563009513adcd82ecf5bcaac3e98aaf",
    "wieczorna_r54/uklad.json": "a4648f3562105bb19809bd7671e6421461f51fa2a4f29b5ecf0e1d6f29d1fb1e",
}


def suma(dane: bytes) -> str:
    return hashlib.sha256(dane).hexdigest()


def lista_r58() -> dict[str, str]:
    """``stl/<plik>`` -> suma z listy R58 (wiersze ``<suma> *<sciezka>``)."""
    wynik = {}
    for wiersz in LISTA_R58.read_text(encoding="utf-8").split("\n"):
        if wiersz.strip():
            s, nazwa = wiersz.split(maxsplit=1)
            wynik[nazwa.strip().lstrip("*")] = s
    return wynik


def okragla_testowa(nazwa: str) -> str:
    return nazwa.replace("_ramkowa", "")


def kwadrat(nazwa: str) -> str:
    return nazwa.replace("okragla_ramkowa_", "")


# --- (a) 10 nowych plikow = pliki R58 ---------------------------------------------------------------
def test_tablica_sum_zgodna_z_lista_r58_i_plikami_json_r58():
    """Sumy wpisane w tym pliku nie sa wymyslone: STL = lista R58 w repo, JSON = pliki ukladu R58 w repo."""
    r58 = lista_r58()
    for plik, (zrodlo, s) in NOWE.items():
        if zrodlo.startswith("stl/"):
            assert r58[zrodlo] == s, plik
        else:
            assert suma((RAMKI / "wyniki_v2" / zrodlo).read_bytes()) == s, plik
    assert len(NOWE) == 10 and sum(z.startswith("stl/") for z, _ in NOWE.values()) == 8


@pytest.mark.parametrize("plik", sorted(NOWE))
def test_nowy_plik_modelu_jest_kopia_bajtowa_r58(plik):
    sciezka = MODELE / plik
    assert sciezka.is_file(), f"brak pliku modelu {plik}"
    assert suma(sciezka.read_bytes()) == NOWE[plik][1]


def test_nowe_pliki_w_gicie_maja_te_same_bajty():
    """Obiekt git = plik roboczy (bez zamiany koncow linii): suma z ``git show`` dla kazdego z 10 plikow, gdy plik jest sledzony."""
    sledzone = subprocess.run(["git", "ls-files", "modele_plytek"], cwd=STANOWISKO, capture_output=True, text=True, check=True).stdout.split()
    nowe = sorted(s for s in sledzone if s.split("/")[1] in RAMKOWE)
    assert nowe == sorted(f"modele_plytek/{p}" for p in NOWE)
    for s in nowe:
        dane = subprocess.run(["git", "show", f":./{s}"], cwd=STANOWISKO, capture_output=True, check=True).stdout
        assert suma(dane) == NOWE[s.removeprefix("modele_plytek/")][1], s


# --- (c) 28 dotychczasowych plikow bez zmian ---------------------------------------------------------
def test_dotychczasowe_pliki_modeli_bajtowo_bez_zmian():
    assert len(DOTYCHCZASOWE) == 28
    for plik, s in DOTYCHCZASOWE.items():
        assert suma((MODELE / plik).read_bytes()) == s, plik


def test_w_katalogu_modeli_jest_38_plikow_i_nic_wiecej():
    jest = sorted(p.relative_to(MODELE).as_posix() for p in MODELE.rglob("*") if p.is_file())
    assert jest == sorted([*DOTYCHCZASOWE, *NOWE])
    assert len(jest) == 38


# --- (b) uklad.wczytaj -------------------------------------------------------------------------------
@pytest.mark.parametrize("nazwa", RAMKOWE)
def test_wczytaj_numery_i_liczba_gniazd(nazwa):
    uk = U.wczytaj(nazwa)
    assert uk.nazwa == nazwa and uk.numery == NUMERY[nazwa]
    assert len(uk.sockets) == GNIAZD[nazwa] and len(uk.rynienki()) == 1
    assert uk.shape == "round" and uk.d == 100.0 and uk.thickness == 8.0
    assert [d.bit for d in uk.code_dimples] == ["A", "B", "C", "D"]  # dolek D tylko w pliku bazowym (bit D = 0 dla n1-n6)
    assert (uk.katalog / U.PLIK_PLYTKI_BAZOWEJ).exists()
    assert json.loads((uk.katalog / "uklad.json").read_text(encoding="utf-8"))["plate"] == nazwa
    assert synth.poranna(nazwa) == nazwa.endswith("poranna") and U.typ_plytki(nazwa) == nazwa


@pytest.mark.parametrize("nazwa", RAMKOWE)
def test_gniazda_i_stozki_jak_kwadrat_r59_i_okragla_testowa(nazwa):
    uk, kw, okr = U.wczytaj(nazwa), U.wczytaj(kwadrat(nazwa)), U.wczytaj(okragla_testowa(nazwa))
    gniazda = lambda u: [(g.id, g.typ, g.x, g.y, g.depth, g.d_top, g.d_bottom, g.l, g.w, g.angle, g.z_top) for g in u.sockets]  # noqa: E731
    stozki = lambda u: [(m.corner, m.x, m.y, m.d, m.depth) for m in u.markers]  # noqa: E731
    assert gniazda(uk) == gniazda(kw) == gniazda(okr)
    assert stozki(uk) == stozki(kw) == stozki(okr)
    # dolki kodu, sciecie i srednica jak w okraglej testowej (ten sam wierzch); kwadrat ma dolki gdzie indziej
    assert uk.code_dimples == okr.code_dimples and uk.flat == okr.flat and (uk.shape, uk.d, uk.size) == (okr.shape, okr.d, okr.size)
    assert uk.code_dimples != kw.code_dimples
    # numery jak kwadrat (n1-n3 W, n4-n6 P), inne niz okragla testowa (n8 / n9)
    assert uk.numery == kw.numery and not set(uk.numery) & set(okr.numery)


@pytest.mark.parametrize("nazwa", RAMKOWE)
def test_ten_sam_rozstaw_stozkow_co_rodzina_r59(nazwa):
    """Rozstaw stozkow wybiera rodzine: uklad ramkowy nalezy do rodziny kwadratu R59, nie do R54."""
    uk = U.wczytaj(nazwa)
    stozki = [{"x": m.x, "y": m.y} for m in uk.markers]
    assert plate.stozki_pasuja(stozki, U.wczytaj(kwadrat(nazwa))) and plate.stozki_pasuja(stozki, U.wczytaj(okragla_testowa(nazwa)))
    assert not plate.stozki_pasuja(stozki, U.wczytaj(kwadrat(nazwa) + "_r54"))


@pytest.mark.parametrize("nazwa", RAMKOWE)
def test_modele_stl_dla_wszystkich_numerow(nazwa):
    uk = U.wczytaj(nazwa)
    for n in NUMERY[nazwa]:
        m = trimesh.load(uk.plik_stl(n), force="mesh")
        assert m.is_watertight
        assert m.bounds[1, 2] >= uk.thickness - 1e-6  # wierzch na z = thickness (relief numeru wyzej)
        r = float(max(abs(m.bounds[0, :2]).max(), abs(m.bounds[1, :2]).max()))
        assert r == pytest.approx(50.0, abs=0.05)  # plytka fi 100
    with pytest.raises(FileNotFoundError):
        uk.plik_stl(8)


# --- ustawienia: uklady wbudowane --------------------------------------------------------------------
def test_uklady_ramkowe_sa_wbudowane_i_we_wzorze_ustawien():
    assert set(RAMKOWE) <= set(UST.UKLADY_WBUDOWANE) and len(UST.UKLADY_WBUDOWANE) == 10
    ust = UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU)
    for n in RAMKOWE:
        assert ust["plytki"][n] == f"modele_plytek/{n}"
        assert UST.katalog_plytki(ust, n) == (U.KATALOG_MODELI / n).resolve()
    assert len(ust["plytki"]) == 10
    # dotychczasowe 8 ukladow zostaje na poczatku i w tej samej kolejnosci (kolejnosc = kolejnosc kandydatow rozpoznania)
    assert list(ust["plytki"])[:8] == ["wieczorna", "poranna", "okragla_wieczorna", "okragla_poranna",
                                      "wieczorna_r54", "poranna_r54", "okragla_wieczorna_r54", "okragla_poranna_r54"]
    assert UST.UKLADY_WBUDOWANE[:8] == tuple(list(ust["plytki"])[:8]) and UST.UKLADY_WBUDOWANE[8:] == RAMKOWE


def test_stary_plik_ustawien_dostaje_uklady_ramkowe(tmp_path):
    """Lokalny ``ustawienia.toml`` sprzed tej paczki (8 ukladow albo tylko 2 wymagane) dostaje uklady ramkowe przy wczytaniu."""
    tekst = UST.PLIK_PRZYKLADU.read_text(encoding="utf-8")
    for nazwa_pliku, odrzuc in (("osiem.toml", lambda k: k.startswith("okragla_ramkowa_")),
                                ("dwa.toml", lambda k: k.startswith("okragla_") or k.endswith("_r54"))):
        p = tmp_path / nazwa_pliku
        p.write_text("\n".join(w for w in tekst.split("\n") if not odrzuc(w.split("=")[0].strip())), encoding="utf-8")
        ust = UST.wczytaj_ustawienia(p)
        assert set(RAMKOWE) <= set(ust["plytki"]) and len(ust["plytki"]) == 10, nazwa_pliku
        assert list(ust["plytki"])[-2:] == list(RAMKOWE), nazwa_pliku  # dopisane na koncu
