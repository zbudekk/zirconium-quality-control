import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
S = Siatka(os.path.join(STL_NEW, 'ramka_wkladka_okragla_v2.stl'), shift=(0, 0, -3.5))
for y in (-48.7, -50.5, -52.0):
    for z in (1.25, 4.0):
        tp = S.pierwsze((0, y, z), (1, 0, 0)); tm = S.pierwsze((0, y, z), (-1, 0, 0))
        print('wyciecie palcowe y %.1f Z %.2f: szer %s' % (y, z, None if tp is None or tm is None else round(tp + tm, 4)))
P = S.V.reshape(-1, 3)
zle = ((P[:, 1] < 52.4 - 1e-3) & ((np.abs(P[:, 0]) > 52.4 + 1e-3) | (P[:, 1] < -52.4 - 1e-3))).sum()
print('K-56: wierzcholki poza obrysem ramy dla y < 52.4:', int(zle))
# czy przod ramy przy wycieciu: material od x 15 (pelna wysokosc)
for x in (15.2, 20.0):
    t = S.pierwsze((x, -60, 3.0), (0, 1, 0))
    print('przod x %.1f: pierwszy material od y %.3f' % (x, -60 + t))