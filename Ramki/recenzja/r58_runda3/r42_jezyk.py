# Jezyk pokrywki: belka wspornikowa (rachunek recenzenta)
E = 2000.0      # MPa, PETG (1900...2100)
b, t = 12.0, 1.5
I = b * t ** 3 / 12
for L_sz in (12.0, 15.0):
    a = L_sz - 2.0                       # garb (srodek Z -18) 2 mm nad wolna krawedzia, nasada na koncu szczeliny
    for d, opis in ((0.40, 'nominal (czubek 49,6 vs plytka 50,0)'), (0.55, 'otwor FDM zanizony o 0,3 na srednicy'), (0.70, 'pokrywka zsunieta o luz 0,3 - jedna strona')):
        P = 3 * E * I * d / a ** 3
        eps = 3 * d * (t / 2) / a ** 2
        print('szczelina %4.1f (a %4.1f): ugiecie %.2f -> sila na garb %5.1f N, odksztalcenie nasady %.2f %% (naprezenie %4.1f MPa) - %s' % (L_sz, a, d, P, 100 * eps, E * eps, opis))