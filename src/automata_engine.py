from typing import Tuple, List, Dict
from pygame import Vector3, Vector2
import random
from collections import defaultdict
from math import sqrt
from helper_functions import point_in_triangle

SQRT3 = sqrt(3)

class AutomataCell:
    def __init__(self, face_verts: Tuple[Vector3], *, value: float = 0):
        self.verts = face_verts

        self.value: float = value
        self.next_value: float = 0
        self.neighbours = []
        # self.centroid = (self.verts[0] + self.verts[1] + self.verts[2]) / 3
        # self.normal = Vector3.cross(self.verts[0] - self.verts[1], self.verts[0] - self.verts[2])
        self._hash = hash(tuple(map(tuple, self.verts)))

    def set_neighbours(self, neighbours: List['AutomataCell']):
        if self.neighbours != []: raise RuntimeError("Neighbours already set")
        self.neighbours = neighbours

    def calc_next_value(self):
        n = sum(map(lambda p: p.value, self.neighbours))
        #self.next_value = (0, 0, self.value, not self.value)[n]
        self.next_value = (not self.value, 0, 1, not self.value)[n]

    def update(self):
        self.value = self.next_value

    def get_verts(self):
        return self.verts
    
    def __hash__(self):
        return self._hash
    
    def __eq__(self, other):
        if not isinstance(other, AutomataCell): return False
        return all(a == b for a, b in zip(self.verts, other.verts))
    
    def __str__(self):
        return str(id(self))
    
     
class Engine:
    """Class response for turning mesh into a Automata"""
    def __init__(self, mesh):
        self.cells = [AutomataCell(face, value = random.randint(0, 100) < 70) for face in mesh]

        ## Calculating neighbours
        vert_to_cell = defaultdict(list) ## Dictionary that assoicaties a verticies to all the cells that contain it
        for cell in self.cells:
            for vert in cell.get_verts():
                vert_to_cell[tuple(vert)].append(cell)

        cell_to_adjacent_cells = defaultdict(list)
        for vert in vert_to_cell.keys(): ## Loop througth all the vericies
            for cell in vert_to_cell[vert]:  ## Loop througth all cells assoicatied to that verticies
                cell_to_adjacent_cells[cell].extend(vert_to_cell[vert])

        for cell in self.cells: ## Set the neighbours to be those that share exactly 2 vertexs
            neighbours = cell_to_adjacent_cells[cell]
            cell.set_neighbours(list(set(filter(lambda x: neighbours.count(x) == 2, neighbours))))

        ## Ordering the neighbours
        # for cell in self.cells:
        #     neighbour_to_projected_point = {} ## neighbour to its point projected into the plane defined by the cell
        #     for neighbour in cell.neighbours:
        #         neighbour_to_projected_point[neighbour] = proj_point(neighbour.centroid, cell.centroid, cell.normal)
        #     right = proj_point(get_right(cell.centroid), cell.centroid, cell.normal)
        #     cell.neighbours.sort(key = lambda p: neighbour_to_projected_point[p].angle_to(right))

    def calc_next_state(self):
        for cell in self.cells:
            cell.calc_next_value()

    def update_state(self):
        for cell in self.cells:
            cell.update()

    def get_cells(self):
        return self.cells
    
    def make_projection_map(self):
        root = self.cells[0]
        tree = self._build_spanning_tree(root)
        self.projection = {root: (Vector2(0, 0), Vector2(0.1, 0), Vector2(0.05, SQRT3/20))}
        self._traverse_and_place(tree, root)
        return self.projection

    def get_projection_map(self) -> Dict[AutomataCell, Tuple[Vector2, Vector2, Vector2]]:
        return self.projection
    
    def _traverse_and_place(self, tree, current):
        parent_verts_3d = current.get_verts()
        parent_verts_2d = self.projection[current]

        for child, shared_edge in tree[current]:
            child_verts_3d = child.get_verts()

            # Find shared vertices in current and child
            i1 = parent_verts_3d.index(shared_edge[0])
            i2 = parent_verts_3d.index(shared_edge[1])
            P1, P2 = parent_verts_2d[i1], parent_verts_2d[i2]

            # Find the third vertex in the child
            third_3d = next(filter(lambda x: not x in shared_edge, child_verts_3d)) ## We find the third 3d vertex since we already know the other two are the shared verts
            first_shared_index = child_verts_3d.index(shared_edge[0])
            third_index = child_verts_3d.index(third_3d)
            P3 = self._calc_3d_vector(P1, P2, (third_index - first_shared_index) % 3 == 1) # is the third edge in the postive or negative direction given we have forced a anti-clockwise ordering

            # Determine order in child
            ordered = [None] * 3
            for i, v in enumerate(child_verts_3d):
                if v == shared_edge[0]:
                    ordered[i] = P1
                elif v == shared_edge[1]:
                    ordered[i] = P2
                else:
                    ordered[i] = P3

            self.projection[child] = tuple(ordered)
            self._traverse_and_place(tree, child)
    
    def _calc_3d_vector(self, P1: Vector2, P2: Vector2, clockwise: bool):
        V = P2 - P1
        V_rotated = Vector2.rotate(V, -60 if clockwise else 60) 
        return P1 + V_rotated

    def _build_spanning_tree(self, root: AutomataCell):
        tree: Dict[AutomataCell, List[Tuple[AutomataCell, List[Vector3]]]] = defaultdict(list)
        visited = set()
        queue = [root]
        visited.add(root)

        while queue:
            current = queue.pop(0)  # or use deque for efficiency
            current_edges = current.get_verts()
            for neighbour in current.neighbours:
                if not (neighbour in visited):
                    neighbour_verts = neighbour.get_verts()
                    shared_edge = [v for v in current_edges if v in neighbour_verts]
                    tree[current].append((neighbour, shared_edge))
                    visited.add(neighbour)
                    queue.append(neighbour)
        return tree
    
    def clear_values(self):
        for cell in self.cells:
            cell.value = 0

    def get_cell_at_pos_in_proj(self, p: Vector2):
        for cell in self.cells:
            if point_in_triangle(p, self.projection[cell]):
                return cell