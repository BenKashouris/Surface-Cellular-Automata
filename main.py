import time
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT
from OpenGL.GL import *
from OpenGL.GLU import *
from typing import List, Dict, Any

import MeshData
import Automata_Engine
from Camera import Camera

import imgui
from imgui.integrations.pygame import PygameRenderer

# Config ----------------
DISPLAY_SIZE = (800, 600)
FRAME_DELAY_MS = 10


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


class CellularAutomataRenderer:
    """Handles rendering and simulation of the cellular automaton."""
    def __init__(self):
        self.project = True
        self.rotation_speed = 0.5
        self.automata_update_interval = 0.5
        self.last_update_time = time.time() - self.automata_update_interval

        self.mesh = MeshData.get_toros_faces()
        self.automata = Automata_Engine.Engine(self.mesh)
        self.projection_map = self.automata.get_projection_map()

        self.camera = Camera()
        self.camera.setup_camera_view(DISPLAY_SIZE[0], DISPLAY_SIZE[1])
        glEnable(GL_DEPTH_TEST)

    def render(self):
        """Updates the automaton if necessary and draws the mesh."""
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
            glColor3f(*face.color)
            verts = face.get_verts() if not self.project else map(
                lambda vec: pygame.math.Vector3(vec.x, vec.y, 0), self.projection_map[face])
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
            self.camera.reset_view()

        self.project = state["project"]
        self.rotation_speed = state["rotation_speed"]
        self.automata_update_interval = state["delay"]


class ControlPanel:
    """ImGui control panel for interacting with automaton parameters."""
    def __init__(self):
        imgui.create_context()
        self.imgui_renderer = PygameRenderer()
        imgui.get_io().ini_file_name = None
        
        self.changes: Dict[str, bool] = {"project": False, "rotation_speed": False, "delay": False}
        self.state: Dict[str, Any] = {"project": True, "rotation_speed": 0.5, "delay": 0.5}

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
        self.changes["rotation_speed"], self.state["rotation_speed"] = imgui.slider_float("Speed", self.state["rotation_speed"], 0.1, 5.0)
        self.changes["delay"], self.state["delay"] = imgui.slider_float("Delay", self.state["delay"], 0.1, 1.5)
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