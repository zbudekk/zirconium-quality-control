# -*- coding: utf-8 -*-
"""
Recenzent R59 - zestawienie obrazow kontrolnych do obejrzenia (python + PIL na PC): cyfry reliefu (8 plikow numerowanych)
i mapy wierzchu (12 plikow) z wyniki/cyfra_*.png i wyniki/mapa_*.png -> wyniki/zestaw_cyfry.png, wyniki/zestaw_mapy_*.png.
Obrazy powstaja w sprawdz_R59.py z siatki promieni (cyfra: bialy = relief z > 0,3; mapa: szary = glebokosc, czarny = przelot,
czerwony = niezgodnosc z modelem oczekiwanym). Uruchomienie: python sprawdz_R59_podglad.py
"""
import os
from PIL import Image, ImageDraw

TU = os.path.dirname(os.path.abspath(__file__))
WYN = os.path.join(TU, "wyniki")
NUM = ["wieczorna_n1", "wieczorna_n2", "wieczorna_n3", "poranna_n4", "poranna_n5", "poranna_n6", "okragla_wieczorna_n8",
       "okragla_poranna_n9"]
WSZ = ["wieczorna", "wieczorna_n1", "wieczorna_n2", "wieczorna_n3", "poranna", "poranna_n4", "poranna_n5", "poranna_n6",
       "okragla_wieczorna", "okragla_wieczorna_n8", "okragla_poranna", "okragla_poranna_n9"]


def arkusz(nazwy, wzor, bok, kolumny, wyj):
    wiersze = (len(nazwy) + kolumny - 1) // kolumny
    img = Image.new("RGB", (kolumny * bok, wiersze * (bok + 18)), (255, 255, 255))
    d = ImageDraw.Draw(img)
    for i, n in enumerate(nazwy):
        p = os.path.join(WYN, wzor % n)
        x = (i % kolumny) * bok
        y = (i // kolumny) * (bok + 18)
        d.text((x + 4, y + 2), n, fill=(0, 0, 160))
        if os.path.isfile(p):
            im = Image.open(p).convert("RGB").resize((bok - 4, bok - 4), Image.LANCZOS)
            img.paste(im, (x + 2, y + 18))
        else:
            d.text((x + 4, y + 30), "BRAK PLIKU", fill=(255, 0, 0))
    img.save(os.path.join(WYN, wyj))
    print("zapisano", wyj, img.size)


arkusz(NUM, "cyfra_ramka_plytka_%s_v2.png", 260, 4, "zestaw_cyfry.png")
arkusz(WSZ[:4], "mapa_ramka_plytka_%s_v2.png", 640, 2, "zestaw_mapy_wieczorna.png")
arkusz(WSZ[4:8], "mapa_ramka_plytka_%s_v2.png", 640, 2, "zestaw_mapy_poranna.png")
arkusz(WSZ[8:], "mapa_ramka_plytka_%s_v2.png", 640, 2, "zestaw_mapy_okragle.png")
