import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
from kolizje import Siatka3D, krawedzie, odcinek_trojkaty
for f in sorted(glob.glob(os.path.join(STL_NEW, '*.stl'))):
    V, N, raw = wczytaj(f)
    # normalne zapisane vs kolejnosc wierzcholkow
    nn = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0]); ln = np.linalg.norm(nn, axis=1); nn = nn / ln[:, None]
    zle_n = int((np.einsum('ij,ij->i', nn, N) < 0.99).sum())
    # przeciecia wlasne: krawedz vs trojkaty bez wspolnego wierzcholka
    G = Siatka3D(V, cell=2.0)
    E = krawedzie(V)
    n_x = 0
    for p, q in E:
        c = G.kandydaci(p, q)
        if len(c) == 0: continue
        T = V[c]
        wsp = (np.all(np.isclose(T, p, atol=0, rtol=0), axis=2).any(axis=1)) | (np.all(np.isclose(T, q, atol=0, rtol=0), axis=2).any(axis=1))
        T = T[~wsp]
        if len(T) and odcinek_trojkaty(p, q, T, eps=1e-7).any():
            n_x += 1
    print(os.path.basename(f), 'normalne zapisane niezgodne:', zle_n, 'krawedzi przecinajacych inne trojkaty:', n_x, 'naglowek:', raw[:20])