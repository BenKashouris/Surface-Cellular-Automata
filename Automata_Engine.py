from typing import Tuple, List, Callable

class EngineSetUp:
    pass

class AutomataCell:
    def __init__(self, 
                face_verts: Tuple[Tuple[float, float, float]],
                rule: Callable[[int], float],
                color=(1, 0.5, 0),
                color_rule: Callable[[float], Tuple[float, float, float]] = lambda v: (v, v, v)
                ):
        
        self.face_verts = face_verts
        self.rule = rule
        self.color: Tuple[float, float, float] = color
        self.color_rule = color_rule

        self.value: float = 0
        self.next_value: float = 0
        self.neighbours = []

    def set_neighbours(self, neighbours: List['AutomataCell']):
        if self.neighbours != []: raise RuntimeError("Neighbours already set")
        self.neighbours = neighbours

    def change_color(self, r: float, g: float, b: float):
        self.color = (r, g, b)

    def calc_next_value(self):
        n = sum(map(lambda p: p.value, self.neighbours))
        self.next_value = self.rule(n)

    def update(self):
        self.value = self.next_value
        self.color = self.color_rule(self.value)



class Engine:
    """Class response for turning mesh into triangle shit and then turning
    then running the engine and sending to opengl"""

    def __init__(self):
        pass