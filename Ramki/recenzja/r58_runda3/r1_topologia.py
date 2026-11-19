import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
from kolizje import Siatka3D, krawedzie, odcinek_trojkaty
for n in ('ramka_wkladka_okragla_v2.stl', 'ramka_pokrywka_okragla_v2.stl'):
    f = os.path.join(STL_NEW, n)
    V, N, raw = wczytaj(f)
    top = topologia(V); P = V.reshape(-1, 3); ar = pola(V)
    nn = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0]); ln = np.linalg.norm(nn, axis=1); nn = nn / ln[:, None]
    zle_n = int((np.einsum('ij,ij->i', nn, N) < 0.99).sum())
    G = Siatka3D(V, cell=2.0); E = krawedzie(V); n_x = 0
    for p, q in E:
        c = G.kandydaci(p, q)
        if len(c) == 0: continue
        T = V[c]
        wsp = (np.all(T == p, axis=2).any(axis=1)) | (np.all(T == q, axis=2).any(axis=1))
        T = T[~wsp]
        if len(T) and odcinek_trojkaty(p, q, T, eps=1e-7).any(): n_x += 1
    print(n, sha(f)[:16], 'tri', len(V), 'vol %.6f' % (objetosc(V) / 1000), 'bbox', np.round(P.min(0), 4), np.round(P.max(0), 4))
    print('   topo', top, 'min pole %.2e' % ar.min(), 'normalne niezgodne', zle_n, 'przeciecia wlasne', n_x, 'liczb -0.0:', int((np.frombuffer(raw, dtype=np.uint32, count=(len(raw) - 84) // 4, offset=84) == 0x80000000).sum()))