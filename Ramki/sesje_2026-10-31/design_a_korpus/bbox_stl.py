import sys, glob, os
import numpy as np, trimesh
base = r"<PC>\Desktop\Ramki\wyniki_v2\stl"
for f in sorted(glob.glob(os.path.join(base, "*.stl"))):
    m = trimesh.load(f, force="mesh")
    b = m.bounds
    print(f"{os.path.basename(f):42s} min={np.round(b[0],3)} max={np.round(b[1],3)} size={np.round(b[1]-b[0],3)} vol={m.volume/1000:.2f}cm3 wt={m.is_watertight} tri={len(m.faces)}")
