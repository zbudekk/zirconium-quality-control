import sys, os, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
from kolizje import *
from r10_kolizje_nominal import V_plytki, Vw
for nazwa, th, dx, dy, dz, opis in [
    ('ramka_plytka_okragla_ramkowa_wieczorna_v2.stl', 0, 0, 0, -0.05, 'kontrola: plytka 0.05 w polce'),
    ('ramka_plytka_okragla_ramkowa_wieczorna_v2.stl', 0, 0.3, -0.3, 0.002, 'kontrola: przesuniecie 0.42 w strone sciecia'),
    ('ramka_plytka_okragla_ramkowa_wieczorna_v2.stl', 90, 0, 0, 0.002, 'obrot 90 w srodku'),
]:
    a = przeciecia(V_plytki(nazwa, th, dx, dy, dz), Vw)
    print(opis, a[0][0], a[1][0], a[0][1][:4], a[1][1][:4])