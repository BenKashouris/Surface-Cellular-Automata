from typing import Tuple, List
from pygame import Vector3
import random
from collections import defaultdict
from math import atan2

##debug
import pickle

def get_right(x: Vector3):
    x = Vector3.normalize(x)
    up = Vector3(0, 0, 1) if x == Vector3(0, 1, 0) or x == -Vector3(0, -1, 0) else Vector3(0, 1, 0)
    return Vector3.normalize(Vector3.cross(x, up))

class AutomataCell:
    def __init__(self, face_verts: Tuple[Vector3], *, color=(0, 0, 0), value: float = 0):
        self.face_verts = face_verts
        self.color: Tuple[float, float, float] = color

        self.value: float = value
        self.next_value: float = 0
        self.neighbours = []
        self.centroid = (self.face_verts[0] + self.face_verts[1] + self.face_verts[2]) / 3
        self.normal = Vector3.cross(self.face_verts[0] - self.face_verts[1], self.face_verts[0] - self.face_verts[2])

    def set_neighbours(self, neighbours: List['AutomataCell']):
        if self.neighbours != []: raise RuntimeError("Neighbours already set")
        self.neighbours = neighbours

    def set_color(self, r: float, g: float, b: float):
        self.color = (r, g, b)

    def calc_next_value(self):
        n = sum(map(lambda p: p.value, self.neighbours))
        #self.next_value = (0, 0, self.value, not self.value)[n]
        self.next_value = (not self.value, 0, 1, not self.value)[n]

    def update(self):
        self.value = self.next_value
        self.set_color(self.value, self.value, self.value)

    def get_verts(self):
        return self.face_verts
    
def proj_point(p: Vector3, q: Vector3, n: Vector3):
    """p: Vector3, the point to be projected \n
       q: Vector3, a point on the plane \n
       n: Vector3, the normal of the plane"""
    v = p - q
    proj_v = ((v * n) / (n * n)) * n
    return p - proj_v
    
            
class Engine:
    """Class response for turning mesh into a Automata"""
    def __init__(self, mesh):
        self.cells = [AutomataCell(face, value = random.randint(0, 100) < 70) for face in mesh]

        ## Calculating neighbours
        vert_to_cell = defaultdict(list) ## Dictionary that assoicaties a verticies to all the cells that contain it
        for cell in self.cells:
            for vert in cell.get_verts():
                vert_to_cell[str(vert)].append(cell)

        cell_to_adjacent_cells = defaultdict(list)
        for vert in vert_to_cell.keys(): ## Loop througth all the vericies
            for cell in vert_to_cell[vert]:  ## Loop througth all cells assoicatied to that verticies
                #cell_to_adjacent_cells[cell].extend([e for e in vert_to_cell[vert] if e != cell])
                cell_to_adjacent_cells[cell].extend(vert_to_cell[vert])

        for cell in self.cells: ## Set the neighbours to be those that share exactly 2 vertexs
            neighbours = cell_to_adjacent_cells[cell]
            cell.set_neighbours(list(set(filter(lambda x: neighbours.count(x) == 2, neighbours))))

        ## Ordering the neighbours
        ## Debug
        data = []
        ## Probably want to encode some info about the origin here
        for cell in self.cells:
            neighbour_to_projected_point = {} ## neighbour to its point projected into the plane defined by the cell
            for neighbour in cell.neighbours:
                neighbour_to_projected_point[neighbour] = proj_point(neighbour.centroid, cell.centroid, cell.normal)
            
            right = proj_point(get_right(cell.centroid), cell.centroid, cell.normal)
            
            ### Debug
            data.append({"cell_centroid": cell.centroid, 
                             "neighbours_centroid": [neighbour.centroid for neighbour in cell.neighbours], 
                             "projected_points": list(neighbour_to_projected_point.values()), 
                             "right": right,
                             "cell_vertices": [vert for vert in cell.get_verts()],
                             "neighbour_verts": [(n.get_verts()[0], n.get_verts()[1], n.get_verts()[2]) for n in cell.neighbours]})
            
            cell.neighbours.sort(key = lambda p: neighbour_to_projected_point[p].angle_to(right))

        ## Debug
        with open("test.data", "ab") as f:
            pickle.dump(data, f)


    def calc_next_state(self):
        for cell in self.cells:
            cell.calc_next_value()

    def update_state(self):
        for cell in self.cells:
            cell.update()

    def get_cells(self):
        return self.cells



if __name__ == "__main__":
    from MeshData import Icosphere, get_toros_faces
    automata = Engine(Icosphere(3).get_faces())
    assert all(len(cell.neighbours) == 3 for cell in automata.cells)

    automata = Engine(get_toros_faces())
    assert all(len(cell.neighbours) == 3 for cell in automata.cells)