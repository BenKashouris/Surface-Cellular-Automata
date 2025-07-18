import math
import time

from pygame import Vector3
from OpenGL.GL import *
from OpenGL.GLU import *

from camera import OrbitalCamera
import automata_engine


class CellularAutomataRenderer:
    ZOOM_SENSTIVITY = 0.5
    """Handles rendering and simulation of the cellular automaton."""
    def __init__(self, mesh, display_size, starting_changes, starting_state):
        self.last_update_time = -math.inf # Force a update asap
        self.update_state(starting_changes, starting_state)

        self.automata = automata_engine.Engine(mesh)
        self.automata.make_projection_map()
        self.projection_map = self.automata.get_projection_map()

        self.camera = OrbitalCamera()
        self.camera.setup_camera_view(display_size[0], display_size[1])
        glEnable(GL_DEPTH_TEST)

    def render(self):
        """Updates the automaton if necessary and draws the mesh."""
        self.camera.apply_view()
        current_time = time.time() # If we have waited the interval then update the automata
        if current_time - self.last_update_time >= self.automata_update_interval and not self.draw_mode:
            self.automata.calc_next_state()
            self.automata.update_state()
            self.last_update_time = current_time
        self.draw()

    def draw(self):
        """Draws automaton mesh as triangles."""
        glBegin(GL_TRIANGLES)
        for face in self.automata.get_cells():
            color = self.off_color if face.value == 0 else self.on_color
            glColor3f(*color)
            verts = face.get_verts() if not self.project else map(lambda vec: Vector3(vec.x, vec.y, 0), self.projection_map[face])
            for vertex in verts:
                glVertex3fv((vertex.x, vertex.y, vertex.z))
        glEnd()

        if not self.draw_mode: return
        glDisable(GL_DEPTH_TEST)
        for face in self.automata.get_cells():
            glLineWidth(1.5)
            glBegin(GL_LINE_LOOP)
            glColor3f(1, 0, 0)
            for vertex in map(lambda vec: Vector3(vec.x, vec.y, 0), self.projection_map[face]):
                glVertex3fv((vertex.x, vertex.y, vertex.z))
            glEnd()
        glEnable(GL_DEPTH_TEST)

    def update_state(self, changes, state):
        """Applies control panel state changes to the renderer.
        Args:
            changes (Dict[str, bool]): Flags indicating which parameters changed.
            state (Dict[str, Any]): New values from the GUI controls.
        """
        if changes["project"]:
            self.camera.reset_orientation()
        if changes["draw_mode"] and state["draw_mode"]: # If draw mode turned on then clear values
            self.automata.clear_values()

        self.project = state["project"]
        self.automata_update_interval = state["delay"]
        self.off_color = state["off_color"]
        self.on_color = state["on_color"]
        self.draw_mode = state["draw_mode"]

    def handle_mouse_motion(self, rel: tuple[int, int], buttons: tuple[bool, bool, bool]):
        """Handles mouse motion"""
        if buttons[0] and not self.project:  # Left click
            self.camera.rotate(rel[0], rel[1])

    def handle_mouse_wheel(self, y):
        """Handles mouse wheel movement"""
        self.camera.zoom(y * self.ZOOM_SENSTIVITY)

    def handle_mouse_press(self, event):
        if not self.draw_mode: return
        if event.button == 1:
            self.get_cell_at_pos(self.camera.screen_coords_to_world_coords(event.pos[0], event.pos[1]))

    def get_cell_at_pos(self, x, y):
        print(x, y)
