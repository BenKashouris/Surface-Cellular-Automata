import time
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT
from pygame import Vector3  
from OpenGL.GL import *
from OpenGL.GLU import *
from typing import List, Dict, Any
import math
import os

import mesh_data
import automata_engine
from camera import Camera, OrbitalCamera

import imgui
from imgui.integrations.pygame import PygameRenderer

import trimesh

# Config ----------------
DISPLAY_SIZE = (800, 600)
FRAME_DELAY_MS = 10
ZOOM_SENSTIVITY = 0.5
project_root: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
assest_root: str = os.path.join(project_root, 'assets')


def load_obj(file_name: str) -> List[tuple[Vector3, Vector3, Vector3]]:
    """Loads an OBJ file and converts it into a list of triangle faces.
    Args:
        file_name (str): The path to the OBJ file to load.
    Returns:
        List[tuple[Vector3, Vector3, Vector3]]: A list of faces, where each face
        is represented as a tuple of three Vector3 objects corresponding to the
        triangle's vertices.
    """
    mesh = trimesh.load_mesh(file_name)
    verts, faces_indexs = mesh.vertices, mesh.faces
    return [(Vector3(*verts[i]), Vector3(*verts[j]), Vector3(*verts[k])) for i, j, k in faces_indexs]


class App:
    """Main application class that manages the event loop and rendering pipeline."""
    def __init__(self):
        pygame.init()
        pygame.display.set_mode(DISPLAY_SIZE, DOUBLEBUF | OPENGL)

        self.cellular_automata_renderer = CellularAutomataRenderer()
        self.control_panel = ControlPanel() 

    def run(self):
        """Runs the main application loop, handling input, updates, and rendering."""
        while True:
            self.handle_events()
            self.render()
            self.handle_UI_changes()

    def handle_UI_changes(self):
        """Applies user-changed settings from the UI to the automaton renderer."""
        self.cellular_automata_renderer.update_state(self.control_panel.get_changes(), self.control_panel.get_state())

    def render(self):
        """Clears the screen and draws the automaton and control panel panel."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.cellular_automata_renderer.render()
        self.control_panel.render()
        pygame.display.flip()
        pygame.time.wait(FRAME_DELAY_MS)

    def handle_events(self):
        """Handles window events and delegates UI interaction to the control panel."""
        for event in pygame.event.get():
            self.control_panel.handle_event(event)
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEMOTION:
                self.cellular_automata_renderer.handle_mouse_motion(event.rel, pygame.mouse.get_pressed())
            if event.type == pygame.MOUSEWHEEL:
                self.cellular_automata_renderer.handle_mouse_wheel(event.y)


class CellularAutomataRenderer:
    """Handles rendering and simulation of the cellular automaton."""
    def __init__(self):
        self.project = False
        self.automata_update_interval = 0
        self.off_color, self.on_color = (0, 0, 0), (0, 0, 0)
        self.last_update_time = -math.inf # Force a update asap

        mesh = load_obj(os.path.join(assest_root, 'toros10nu10nv0.33r.obj'))
        print(len(mesh))
        self.automata = automata_engine.Engine(mesh)
        self.projection_map = self.automata.get_projection_map()

        self.camera = OrbitalCamera()
        self.camera.setup_camera_view(DISPLAY_SIZE[0], DISPLAY_SIZE[1])
        glEnable(GL_DEPTH_TEST)

    def render(self):
        """Updates the automaton if necessary and draws the mesh."""
        self.camera.apply_view()
        current_time = time.time() # If we have waited the interval then update the automata
        if current_time - self.last_update_time >= self.automata_update_interval:
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
            verts = face.get_verts() if not self.project else map(
                lambda vec: Vector3(vec.x, vec.y, 0), self.projection_map[face])
            for vertex in verts:
                glVertex3fv((vertex.x, vertex.y, vertex.z))
        glEnd()

    def update_state(self, changes, state):
        """Applies control panel state changes to the renderer.
        Args:
            changes (Dict[str, bool]): Flags indicating which parameters changed.
            state (Dict[str, Any]): New values from the GUI controls.
        """
        if changes["project"]:
            self.camera.reset_orientation()

        self.project = state["project"]
        self.automata_update_interval = state["delay"]
        self.off_color = state["off_color"]
        self.on_color = state["on_color"]

    def handle_mouse_motion(self, rel: tuple[int, int], buttons: tuple[bool, bool, bool]):
        """Handles mouse motion"""
        if buttons[0] and not self.project:  # Left click
            self.camera.rotate(rel[0], rel[1])

    def handle_mouse_wheel(self, y):
        """Handles mouse wheel movement"""
        self.camera.zoom(y * ZOOM_SENSTIVITY)


class ControlPanel:
    """ImGui control panel for interacting with automaton parameters."""
    def __init__(self):
        imgui.create_context()
        self.imgui_renderer = PygameRenderer()
        imgui.get_io().ini_file_name = None

        self.changes: Dict[str, bool] = {"project": False, "delay": False, "off_color": False, "on_color": False}
        self.state: Dict[str, Any] = {"project": True, "delay": 0.5, "on_color": (1, 1, 1), "off_color": (0, 0, 0)}

    def get_changes(self) -> Dict[str, bool]:
        """Returns flags indicating which control values changed."""
        return self.changes

    def get_state(self) -> Dict[str, Any]:
        """Returns the current state of all control parameters."""
        return self.state

    def handle_event(self, event: pygame.event.Event):
        """Passes Pygame input events to the ImGui renderer for UI interaction"""
        self.imgui_renderer.process_event(event)

    def draw(self):
        """Builds, renders and gets states of the ImGui UI window with control widgets."""
        imgui.begin("Controls")
        self.changes["project"], self.state["project"] = imgui.checkbox("Enable Projection", self.state["project"])
        self.changes["delay"], self.state["delay"] = imgui.slider_float("Delay", self.state["delay"], 0.0, 1.5)
        self.changes["off_color"], self.state["off_color"] = imgui.color_edit3("Edit off color", *self.state["off_color"], flags=imgui.COLOR_EDIT_NO_INPUTS)
        self.changes["on_color"], self.state["on_color"] = imgui.color_edit3("Edit on color", *self.state["on_color"], flags=imgui.COLOR_EDIT_NO_INPUTS)
        imgui.end()

    def render(self):
        """Finalizes and renders the ImGui draw data to the screen."""
        io = imgui.get_io()
        io.display_size = pygame.display.get_surface().get_size()
        imgui.new_frame()
        self.draw()
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())


if __name__ == "__main__":
    app = App()
    app.run()