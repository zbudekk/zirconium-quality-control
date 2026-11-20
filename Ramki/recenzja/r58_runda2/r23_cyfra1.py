import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
from rastr import *
def relief(f, c, shift_z):
    V, N, raw = wczytaj(f); V = V.copy(); V[..., 2] -= shift_z
    k = 0.05; x0 = c[0] - 3; y0 = c[1] - 3.5
    Z = mapa_z(V, x0, y0, k, int(6 / k) + 1, int(7 / k) + 1, 'max')
    return Z > 0.3
a = relief(os.path.join(STL_NEW, 'ramka_plytka_okragla_ramkowa_wieczorna_n1_v2.stl'), (35, -26.5), 8.0)
b = relief(os.path.join(STL_OLD, 'ramka_plytka_wieczorna_n1_v2.stl'), (39.5, -44.5), 8.0)
print('pikseli reliefu (krok 0,05): okragla n1 %d, kwadratowa n1 %d, rozne %d' % (a.sum(), b.sum(), (a != b).sum()))
# najnizszy rzad reliefu
ra = np.nonzero(a.any(axis=1))[0]; rb = np.nonzero(b.any(axis=1))[0]
print('rzedy reliefu okragla', ra.min(), ra.max(), 'kwadrat', rb.min(), rb.max())
for j in range(ra.min(), ra.min() + 4):
    print(''.join('#' if v else '.' for v in a[j, ::2]))