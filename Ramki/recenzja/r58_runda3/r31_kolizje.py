import sys, os, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
from kolizje import *
def V_plytki(nazwa, theta=0.0, dx=0.0, dy=0.0, dz=0.0):
    V, N, raw = wczytaj(os.path.join(STL_NEW, nazwa)); V = V.copy()
    V[..., 2] += 2.5 + dz
    if theta:
        c, s = math.cos(math.radians(theta)), math.sin(math.radians(theta))
        x = V[..., 0].copy(); y = V[..., 1].copy(); V[..., 0] = c * x - s * y; V[..., 1] = s * x + c * y
    V[..., 0] += dx; V[..., 1] += dy
    return V
Vw, _, _ = wczytaj(os.path.join(STL_NEW, 'ramka_wkladka_okragla_v2.stl')); Vw = Vw.copy(); Vw[..., 2] -= 3.5
def V_pokr(dx=0.0, dy=0.0, dz=0.0):
    Vp, _, _ = wczytaj(os.path.join(STL_NEW, 'ramka_pokrywka_okragla_v2.stl')); Vp = Vp.copy(); Vp[..., 1] *= -1; Vp[..., 2] *= -1; Vp[..., 2] += 26.5 + dz
    Vp[..., 0] += dx; Vp[..., 1] += dy
    return Vp
u = np.array([math.cos(math.radians(-45)), math.sin(math.radians(-45))])
pl = 'ramka_plytka_okragla_ramkowa_wieczorna_v2.stl'
def test(opis, A, B):
    a = przeciecia(A, B)
    print('%-75s %5d / %5d  %s' % (opis, a[0][0], a[1][0], [tuple(x) for x in (a[0][1][:2] + a[1][1][:2])]))
test('nominal: plytka (+0,002) - wkladka', V_plytki(pl, dz=0.002), Vw)
test('nominal: plytka - pokrywka', V_plytki(pl), V_pokr())
test('nominal: wkladka - pokrywka', Vw, V_pokr())
test('kontrola: plytka 0,05 w polce - wkladka', V_plytki(pl, dz=-0.05), Vw)
test('plytka n4 (+0,002) - wkladka', V_plytki('ramka_plytka_okragla_ramkowa_poranna_n4_v2.stl', dz=0.002), Vw)
for sp, sk in ((0.399, 0.30), (0.399, 0.304), (0.399, 0.15)):
    d_pl = -sp * u; d_pk = -(sp + sk) * u
    test('plytka %.3f od D, pokrywka +%.2f od D wzgl. plytki: pokrywka - wkladka' % (sp, sk), V_pokr(d_pk[0], d_pk[1]), Vw)
    test('   ten sam uklad: pokrywka - plytka', V_pokr(d_pk[0], d_pk[1]), V_plytki(pl, dx=d_pl[0], dy=d_pl[1]))
d_pl = 0.399 * u
test('plytka 0,399 w strone D, pokrywka wspolosiowa z plytka: pokrywka - wkladka', V_pokr(d_pl[0], d_pl[1]), Vw)
test('   plytka 0,399 w strone D (+0,002) - wkladka (zebro)', V_plytki(pl, dx=d_pl[0], dy=d_pl[1], dz=0.002), Vw)