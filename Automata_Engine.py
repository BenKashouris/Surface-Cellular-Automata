from typing import Tuple, List, Callable
from Icosphere_Mesh_data import Icosphere
from pygame import Vector3
class AutomataCell:
    def __init__(self, face_verts: Tuple[Vector3], color=(1, 0.5, 0)):
        
        self.face_verts = face_verts
        self.color: Tuple[float, float, float] = color

        self.value: float = 0
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


class Engine:
    """Class response for turning mesh into triangle shit and then turning
    then running the engine and sending to opengl"""

    def __init__(self, mesh):
        self.cells = [AutomataCell(face, None) for face in mesh.get_faces()]

        ## Calculating neighbours
        vert_to_cell = {} ## Dictionary that assoicaties a verticies to all the cells that contain it
        for cell in self.cells:
            for vert in cell.get_verts():
                ## assoicative this vert to this cell
                vert_id = str(vert)
                current_value = vert_to_cell.get(vert_id, []) 
                vert_to_cell[vert_id] = current_value + [cell]

        for vert in vert_to_cell.keys(): ## Loop througth all the vericies
            for cell in vert_to_cell[vert]:  ## Loop througth all cells assoicatied to that verticies
                cell.set_neighbours([e for e in vert_to_cell[vert] if e != cell])
                 ## Tell that verticies that it is neighbour to all other vertices associated to that vert
        ## Order neighbours - To do

    def calc_next_state(self):
        for cell in self.cells:
            cell.calc_next_value()

    def update_state(self):
        for cell in self.cells:
            cell.update()

    def get_cells(self):
        return self.cells
