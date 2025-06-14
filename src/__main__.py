import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT 
from OpenGL.GL import *
from OpenGL.GLU import *

import os

from file_manager import load_obj, get_file_from_user
from automata_renderer import CellularAutomataRenderer
from control_panel import ControlPanel


# Config ----------------
DISPLAY_SIZE = (800, 600)
FRAME_DELAY_MS = 10
DEFAULT_MESH_FILE = 'toros10nu10nv0.33r.obj'

class App:
    """Main application class that manages the event loop and rendering pipeline."""
    def __init__(self):
        self.project_root: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.assest_root: str = os.path.join(self.project_root, 'assets')

        pygame.init()
        pygame.display.set_mode(DISPLAY_SIZE, DOUBLEBUF | OPENGL)

        mesh = load_obj(os.path.join(self.assest_root, DEFAULT_MESH_FILE))
        print(len(mesh))

        self.cellular_automata_renderer = CellularAutomataRenderer(mesh, DISPLAY_SIZE)
        self.control_panel = ControlPanel() 

    def run(self):
        """Runs the main application loop, handling input, updates, and rendering."""
        while True:
            self.handle_events()
            self.render()
            self.handle_UI_changes()

    def handle_UI_changes(self):
        """Applies user-changed settings from the UI to the automaton renderer."""
        changes, state = self.control_panel.get_changes(), self.control_panel.get_state()
        if changes["change_mesh"]: self.change_automata()
        self.cellular_automata_renderer.update_state(changes, state)

    def change_automata(self):
        """Prompts the user to select a new `.obj` file and updates the cellular automata renderer."""
        mesh = load_obj(os.path.join(self.assest_root, get_file_from_user(self.assest_root)))
        if mesh == "": return #If the user cancels then stop
        self.cellular_automata_renderer = CellularAutomataRenderer(mesh, DISPLAY_SIZE)

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

    def fix_blurriness(self):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except:
                pass

if __name__ == "__main__":
    app = App()
    app.run()