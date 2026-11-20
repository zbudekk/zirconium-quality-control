import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
files = sorted(glob.glob(os.path.join(STL_NEW, '*.stl')))
ref = ['ramka_plytka_okragla_wieczorna_v2.stl', 'ramka_plytka_okragla_poranna_v2.stl', 'ramka_plytka_okragla_wieczorna_n8_v2.stl', 'ramka_plytka_okragla_poranna_n9_v2.stl', 'ramka_wkladka_v2.stl', 'ramka_pokrywka_v2.stl', 'ramka_plytka_wieczorna_n1_v2.stl', 'ramka_blat_v2.stl']
files += [os.path.join(STL_OLD, r) for r in ref]
for f in files:
    V, N, raw = wczytaj(f)
    top = topologia(V)
    P = V.reshape(-1, 3)
    lo, hi = P.min(0), P.max(0)
    ar = pola(V)
    nan = int(np.isnan(V).sum())
    print(os.path.basename(f), sha(f)[:16], 'tri', len(V), 'vol %.6f' % (objetosc(V) / 1000), 'bbox', np.round(lo, 4), np.round(hi, 4), 'size', np.round(hi - lo, 4))
    print('   topo', top, 'min area %.2e' % ar.min(), 'n<1e-6:', int((ar < 1e-6).sum()), 'nan', nan)