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
            self.subdivide(self.icosahedron[self.icoindices[i][0]],
                           self.icosahedron[self.icoindices[i][1]],
                           self.icosahedron[self.icoindices[i][2]], number_of_subdivides)            

    def _subdivide(self, v1: Vector3, v2: Vector3, v3: Vector3, depth: int):
        if depth == 0:
            self.make_face(v1, v2, v3)
            return

        v12 = v1 + v2
        v23 = v2 + v3
        v31 = v3 + v1

        v12 = v12.normalize()
        v23 = v23.normalize()
        v31 = v31.normalize()

        self.subdivide(v1, v12, v31, depth - 1)
        self.subdivide(v2, v23, v12, depth - 1)
        self.subdivide(v3, v31, v23, depth - 1)
        self.subdivide(v12, v23, v31, depth - 1)

    def _make_face(self, v1, v2, v3):
       self.faces.append((v1, v2, v3))

    def get_faces(self):
        return self.faces

 