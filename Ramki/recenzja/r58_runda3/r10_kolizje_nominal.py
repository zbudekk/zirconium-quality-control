import sys, os, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
from kolizje import *
D = os.path.dirname(os.path.abspath(__file__))
def V_plytki(nazwa, theta=0.0, dx=0.0, dy=0.0, dz=0.0):
    V, N, raw = wczytaj(os.path.join(STL_NEW, nazwa)); V = V.copy()
    V[..., 2] += 2.5 + dz     # spod plytki na polce Z 2.5 (uklad wkladki)
    if theta:
        c, s = math.cos(math.radians(theta)), math.sin(math.radians(theta))
        x = V[..., 0].copy(); y = V[..., 1].copy(); V[..., 0] = c * x - s * y; V[..., 1] = s * x + c * y
    V[..., 0] += dx; V[..., 1] += dy
    return V
Vw, _, _ = wczytaj(os.path.join(STL_NEW, 'ramka_wkladka_okragla_v2.stl')); Vw = Vw.copy(); Vw[..., 2] -= 3.5
Vp, _, _ = wczytaj(os.path.join(STL_NEW, 'ramka_pokrywka_okragla_v2.stl')); Vp = Vp.copy(); Vp[..., 1] *= -1; Vp[..., 2] *= -1; Vp[..., 2] += 26.5
lo = Vp.reshape(-1, 3).min(0); hi = Vp.reshape(-1, 3).max(0); print('pokrywka w ukladzie wkladki: Z %.3f..%.3f' % (lo[2], hi[2]))
t0 = time.time()
for nazwa in sys.argv[1:]:
    Vpl = V_plytki(nazwa, dz=0.002)
    a = przeciecia(Vpl, Vw); b = przeciecia(Vpl, Vp)
    print(nazwa, 'plytka(+0.002)-wkladka:', a[0][0], a[1][0], a[0][1][:3], a[1][1][:3], '| plytka-pokrywka:', b[0][0], b[1][0], b[0][1][:3], b[1][1][:3], '%.0fs' % (time.time() - t0))
    Vpl0 = V_plytki(nazwa, dz=0.0)
    a0 = przeciecia(Vpl0, Vw)
    print('    bez podniesienia (czulosc, styk na polce):', a0[0][0], a0[1][0])
c = przeciecia(Vw, Vp)
print('wkladka-pokrywka:', c[0][0], c[1][0], c[0][1][:3])