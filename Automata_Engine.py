from typing import Tuple, List
from Icosphere_Mesh_data import Icosphere
from pygame import Vector3
import random
from collections import defaultdict


class AutomataCell:
    def __init__(self, face_verts: Tuple[Vector3], *, color=(0, 0, 0), value: float = 0):
        
        self.face_verts = face_verts
        self.color: Tuple[float, float, float] = color

        self.value: float = value
        self.next_value: float = 0
        self.neighbours = []

    def set_neighbours(self, neighbours: List['AutomataCell']):
        if self.neighbours != []: raise RuntimeError("Neighbours already set")
        self.neighbours = neighbours

    def set_color(self, r: float, g: float, b: float):
        self.color = (r, g, b)

    def calc_next_value(self):
        n = sum(map(lambda p: p.value, self.neighbours))
        self.next_value = (not self.value, 0, 1, not self.value)[n]

    def update(self):
        self.value = self.next_value
        self.set_color(self.value, self.value, self.value)

    def get_verts(self):
        return self.face_verts
    
    def __str__(self):
        return f"""
Value: {self.value}
Color: {self.color}
Vert1: {self.face_verts[0]}
Vert2: {self.face_verts[1]}
Vert3: {self.face_verts[2]}
"""


class Engine:
    """Class response for turning mesh into triangle shit and then turning
    then running the engine and sending to opengl"""

    def __init__(self, mesh):
        self.cells = [AutomataCell(face, value = random.randint(0, 1)) for face in mesh.get_faces()]

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

        ## Order neighbours - To do

    def calc_next_state(self):
        for cell in self.cells:
            cell.calc_next_value()

    def update_state(self):
        for cell in self.cells:
            cell.update()

    def get_cells(self):
        return self.cells

if __name__ == "__main__":
    from Icosphere_Mesh_data import Icosphere
    x = Engine(Icosphere(3))
    print(x.cells[10].neighbours)