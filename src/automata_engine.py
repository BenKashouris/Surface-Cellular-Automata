from typing import Tuple, List, Dict
from pygame import Vector3, Vector2
import random
from collections import defaultdict
from math import sqrt
from helper_functions import point_in_triangle

SQRT3 = sqrt(3)

class AutomataCell:
    """Represents a single triangle cell in a surface-based cellular automaton."""

    def __init__(self, face_verts: Tuple[Vector3], *, value: float = 0):
        self.verts = face_verts  # Vertices defining the triangle

        self.value: float = value  # Current state of the cell
        self.next_value: float = 0  # Next state after update
        self.neighbours = []  # Adjacent AutomataCells

        # Precompute a hash based on vertex positions for fast equality and lookup
        self._hash = hash(tuple(map(tuple, self.verts)))

    def set_neighbours(self, neighbours: List['AutomataCell']):
        """Assigns neighbors to the cell (only once)."""
        if self.neighbours != []:
            raise RuntimeError("Neighbours already set")
        self.neighbours = neighbours

    def calc_next_value(self, on_rule: Tuple[int, int, int, int], off_rule: Tuple[int, int, int, int]):
        """Determines the cell's next state based on the rules and neighbor values."""
        n = sum(map(lambda p: p.value, self.neighbours))  # Count 'on' neighbors
        self.next_value = on_rule[n] if self.value else off_rule[n]

    def update(self):
        """Updates the cell's state to the computed next state."""
        self.value = self.next_value

    def get_verts(self):
        """Returns the triangle's vertices."""
        return self.verts

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if not isinstance(other, AutomataCell):
            return False
        return all(a == b for a, b in zip(self.verts, other.verts))

    def __str__(self):
        return str(id(self))


class Engine:
    """Handles cellular automaton logic over a mesh of triangle cells."""

    def __init__(self, mesh, on_rule: Tuple[int, int, int, int] = (0, 1, 1, 0), off_rule: Tuple[int, int, int, int] = (0, 1, 1, 0)):
        self.on_rule, self.off_rule = on_rule, off_rule

        # Convert mesh faces into AutomataCells, assigning random initial states (70% chance 'on')
        self.cells = [AutomataCell(face, value=random.randint(0, 100) < 70) for face in mesh]

        # Map vertices to the cells that include them
        vert_to_cell = defaultdict(list)
        for cell in self.cells:
            for vert in cell.get_verts():
                vert_to_cell[tuple(vert)].append(cell)

        # Identify adjacent cells via shared vertices
        cell_to_adjacent_cells = defaultdict(list)
        for vert in vert_to_cell.keys():
            for cell in vert_to_cell[vert]:
                cell_to_adjacent_cells[cell].extend(vert_to_cell[vert])

        # Set neighbors as those that share exactly two vertices (edge adjacency)
        for cell in self.cells:
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
        """Calculates next value for each cell without updating yet."""
        for cell in self.cells:
            cell.calc_next_value(self.on_rule, self.off_rule)

    def update_state(self):
        """Applies the calculated next state to each cell."""
        for cell in self.cells:
            cell.update()

    def get_cells(self):
        return self.cells

    def make_projection_map(self):
        """
        Creates a 2D projection of the 3D mesh starting from an arbitrary root cell.
        Returns a mapping from AutomataCell to its projected 2D triangle.
        """
        root = self.cells[0]
        tree = self._build_spanning_tree(root)
        
        # Start by placing the root triangle flat in 2D space
        self.projection = {
            root: (Vector2(0, 0), Vector2(0.1, 0), Vector2(0.05, SQRT3/20))
        }

        # Recursively layout the rest of the mesh
        self._traverse_and_place(tree, root)
        return self.projection

    def get_projection_map(self) -> Dict[AutomataCell, Tuple[Vector2, Vector2, Vector2]]:
        return self.projection

    def _traverse_and_place(self, tree, current):
        """Recursive function to place each triangle in 2D based on its neighbor and shared edge."""
        parent_verts_3d = current.get_verts()
        parent_verts_2d = self.projection[current]

        for child, shared_edge in tree[current]:
            child_verts_3d = child.get_verts()

            # Find the 2D coordinates of the shared edge
            i1 = parent_verts_3d.index(shared_edge[0])
            i2 = parent_verts_3d.index(shared_edge[1])
            P1, P2 = parent_verts_2d[i1], parent_verts_2d[i2]

            # Identify the third vertex in 3D
            third_3d = next(filter(lambda x: x not in shared_edge, child_verts_3d))
            first_shared_index = child_verts_3d.index(shared_edge[0])
            third_index = child_verts_3d.index(third_3d)

            # Determine rotation direction based on triangle winding
            clockwise = (third_index - first_shared_index) % 3 == 1
            P3 = self._calc_3d_vector(P1, P2, clockwise)

            # Assign correct vertex positions for child
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
        """Rotates vector P2-P1 by ±60 degrees to find the third triangle point in 2D."""
        V = P2 - P1
        V_rotated = Vector2.rotate(V, -60 if clockwise else 60)
        return P1 + V_rotated

    def _build_spanning_tree(self, root: AutomataCell) -> Dict[AutomataCell, List[Tuple[AutomataCell, List[Vector3]]]]:
        """
        Builds a spanning tree from the root cell across the mesh using BFS.
        Used to guide triangle placement in the 2D projection.
        Parameters:
            root (AutomataCell): An arbitrary cell that will act as the tree's root 
        Returns:
            Dict[AutomataCell, List[Tuple[AutomataCell, List[Vector3]]]]: A mapping between a tree and a list of tuples containing the child AutomataCell and a Vector that is the shared edge in 3D.
        """
        tree: Dict[AutomataCell, List[Tuple[AutomataCell, List[Vector3]]]] = defaultdict(list)
        visited = set()
        queue = [root]
        visited.add(root)

        while queue:
            current = queue.pop(0)
            current_edges = current.get_verts()
            for neighbour in current.neighbours:
                if neighbour not in visited:
                    neighbour_verts = neighbour.get_verts()
                    shared_edge = [v for v in current_edges if v in neighbour_verts]
                    tree[current].append((neighbour, shared_edge))
                    visited.add(neighbour)
                    queue.append(neighbour)
        return tree

    def clear_values(self):
        """Resets all cell values to 0."""
        for cell in self.cells:
            cell.value = 0

    def get_cell_at_pos_in_proj(self, p: Vector2):
        """Returns the AutomataCell containing point `p` in the 2D projection."""
        for cell in self.cells:
            if point_in_triangle(p, self.projection[cell]):
                return cell

    def set_rule(self, on_rule: Tuple[int, int, int, int], off_rule: Tuple[int, int, int, int]):
        """Updates the rule sets used for automaton transitions."""
        self.on_rule = on_rule
        self.off_rule = off_rule