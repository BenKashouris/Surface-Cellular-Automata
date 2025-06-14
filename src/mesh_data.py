from pygame import Vector3
from math import sqrt

class Icosphere():
    MAGIC_CONSTANT_1 = 2 / sqrt(10 + 2 * sqrt(5))  ## These come from normilzation of vector with 1, golden ratio and 0
    MAGIC_CONSTANT_2 = (1 + sqrt(5)) / sqrt(10 + 2 * sqrt(5))
    icosahedron = [Vector3((-MAGIC_CONSTANT_1, MAGIC_CONSTANT_2, 0.0)),
                    Vector3((MAGIC_CONSTANT_1, MAGIC_CONSTANT_2, 0.0)),
                    Vector3((-MAGIC_CONSTANT_1, -MAGIC_CONSTANT_2, 0.0)),
                    Vector3((MAGIC_CONSTANT_1, -MAGIC_CONSTANT_2, 0.0)),
                    Vector3((0.0, -MAGIC_CONSTANT_1, MAGIC_CONSTANT_2)),
                    Vector3((0.0, MAGIC_CONSTANT_1, MAGIC_CONSTANT_2)),
                    Vector3((0.0, -MAGIC_CONSTANT_1, -MAGIC_CONSTANT_2)),
                    Vector3((0.0, MAGIC_CONSTANT_1, -MAGIC_CONSTANT_2)),
                    Vector3((MAGIC_CONSTANT_2, 0.0, -MAGIC_CONSTANT_1)),
                    Vector3((MAGIC_CONSTANT_2, 0.0, MAGIC_CONSTANT_1)),
                    Vector3((-MAGIC_CONSTANT_2, 0.0, -MAGIC_CONSTANT_1)),
                    Vector3((-MAGIC_CONSTANT_2, 0.0, MAGIC_CONSTANT_1))]
    icoindices = [
        [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
        [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
        [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
        [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]
    ]

    def __init__(self, number_of_subdivides: int):
        self.faces = []
        for i in range(20):
            self._subdivide(self.icosahedron[self.icoindices[i][0]],
                           self.icosahedron[self.icoindices[i][1]],
                           self.icosahedron[self.icoindices[i][2]], number_of_subdivides)            

    def _subdivide(self, v1: Vector3, v2: Vector3, v3: Vector3, depth: int):
        if depth == 0:
            self._make_face(v1, v2, v3)
            return

        v12 = v1 + v2
        v23 = v2 + v3
        v31 = v3 + v1

        v12 = v12.normalize()
        v23 = v23.normalize()
        v31 = v31.normalize()

        self._subdivide(v1, v12, v31, depth - 1)
        self._subdivide(v2, v23, v12, depth - 1)
        self._subdivide(v3, v31, v23, depth - 1)
        self._subdivide(v12, v23, v31, depth - 1)

    def _make_face(self, v1, v2, v3):
       self.faces.append((v1, v2, v3))

    def get_faces(self):
        return self.faces
    
import numpy as np

SQRT3 = np.sqrt(3.0)

def _wrap_key(x, y, width, height, tol=1e-8):
    """Helper: wrap a point into the fundamental parallelogram and round."""
    return (round(x % width, 8), round(y % height, 8))

def generate_torus_tri_mesh(Nu=20, Nv=20, R=3.0, r=1.0):
    # --- 1. Build a *flat* triangular lattice -----------------------------
    a      = 1.0                                # intrinsic edge length
    width  = Nu * a                             # span of the first lattice vector
    height = Nv * (SQRT3 / 2) * a               # span of the second lattice vector

    verts2d, index = [], {}                     # unique 2-D vertices & lookup
    faces   = []                                # triangle index list

    def vid(x, y):
        """Return (and create if needed) the index of wrapped vertex (x,y)."""
        key = _wrap_key(x, y, width, height)
        if key not in index:
            index[key] = len(verts2d)
            verts2d.append(key)                 # already wrapped
        return index[key]

    for j in range(Nv):
        shift     = 0.5 * (j & 1)               # stagger every other row
        shift_up  = 0.5 * ((j + 1) & 1)

        y0 =  j      * (SQRT3 / 2) * a
        y1 = (j + 1) * (SQRT3 / 2) * a

        for i in range(Nu):
            x0  = (i + shift    ) * a          # current row
            x1  = (i + 1 + shift) * a
            xu0 = (i     + shift_up ) * a      # row above
            xu1 = (i + 1 + shift_up) * a

            # vertex indices, automatically wrapped
            v0 = vid(x0,  y0)
            v1 = vid(x1,  y0)
            v2 = vid(xu0, y1)
            v3 = vid(xu1, y1)

            # two triangles per “diamond”, orientation alternates by row
            if (j & 1) == 0:           # even row
                faces.append((v0, v1, v2))
                faces.append((v1, v3, v2))
            else:                      # odd row
                faces.append((v0, v1, v3))
                faces.append((v0, v3, v2))

    # --- 2. Embed the wrapped lattice on a torus ---------------------------
    verts3d = []
    for x, y in verts2d:
        u = (x / width)  * 2.0 * np.pi         # 0‒2π around the hole
        v = (y / height) * 2.0 * np.pi         # 0‒2π through the tube

        X = (R + r * np.cos(v)) * np.cos(u)
        Y = (R + r * np.cos(v)) * np.sin(u)
        Z =  r * np.sin(v)
        verts3d.append((X, Y, Z))

    return np.asarray(verts3d, dtype=float), np.asarray(faces, dtype=int)

from pygame import Vector3
def get_toros_faces():
    V, F = generate_torus_tri_mesh(Nu=10, Nv=10, R=3.0, r=1.0)
    return [(Vector3(*V[i]), Vector3(*V[j]), Vector3(*V[k])) for i, j, k in F]


import trimesh
def export_to_obj(faces, name):
    out_verts = []
    out_faces = []
    for face in faces:
        current_vert_id = []
        for vert in face:
            try:
                current_vert_id.append(out_verts.index(vert))
            except ValueError:
                out_verts.append(vert)
                current_vert_id.append(len(out_verts) - 1)
        out_faces.append(current_vert_id)
    mesh = trimesh.Trimesh(vertices=out_verts, faces=out_faces)

    # Export to OBJ
    mesh.export(name)

if __name__ == "__main__":
    #export_to_obj(Icosphere(2).get_faces(), 'Icosphere2.obj')
    export_to_obj(Icosphere(3).get_faces(), 'Icosphere3.obj')
    #export_to_obj(Icosphere(4).get_faces(), 'Icosphere4.obj')
    #export_to_obj(Icosphere(5).get_faces(), 'Icosphere5.obj')

    export_to_obj(get_toros_faces(), 'toros.obj')