import sys, os, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
from kolizje import *
from r10_kolizje_nominal import V_plytki, Vw
u = np.array([math.cos(math.radians(-45)), math.sin(math.radians(-45))])
for nazwa in ['ramka_plytka_okragla_ramkowa_wieczorna_v2.stl', 'ramka_plytka_okragla_ramkowa_poranna_v2.stl']:
    for th in (90, 180, 270, 91.5, 45, 135):
        for s in (0.30,):
            d = -s * u
            a = przeciecia(V_plytki(nazwa, th, d[0], d[1], 0.002), Vw)
            print(nazwa[28:], 'obrot %g, przesuniecie %.2f od sciecia (dx %.3f, dy %.3f): kolizje %d / %d' % (th, s, d[0], d[1], a[0][0], a[1][0]), a[0][1][:2], a[1][1][:2])