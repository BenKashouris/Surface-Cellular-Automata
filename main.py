import time
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT
from OpenGL.GL import *
from OpenGL.GLU import *
from typing import List, Dict, Any

import MeshData
import Automata_Engine

import imgui
from imgui.integrations.pygame import PygameRenderer

# Config ----------------
DISPLAY_SIZE = (800, 600)
FOV = 45
Z_NEAR = 0.1
Z_FAR = 50.0
CAMERA_DISTANCE = -5
FRAME_DELAY_MS = 10

class CellularAutomataRenderer:
    def __init__(self):
        self.project = True
        self.rotation_speed = 0.5
        self.AUTOMATA_UPDATE_INTERVAL = 0.5
        self.last_update_time = time.time() - self.AUTOMATA_UPDATE_INTERVAL

        self.mesh = MeshData.get_toros_faces()
        self.automata = Automata_Engine.Engine(self.mesh)
        self.projection_map = self.automata.get_projection_map()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(FOV, DISPLAY_SIZE[0] / DISPLAY_SIZE[1], Z_NEAR, Z_FAR)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, CAMERA_DISTANCE)
        glEnable(GL_DEPTH_TEST)

    def render(self):
        current_time = time.time() # If we have waited the interval then update the automata
        if current_time - self.last_update_time >= self.AUTOMATA_UPDATE_INTERVAL:
            self.automata.calc_next_state()
            self.automata.update_state()
            self.last_update_time = current_time
        self.draw()

    def draw(self):
        glBegin(GL_TRIANGLES)
        for face in self.automata.get_cells():
            glColor3f(*face.color)
            verts = face.get_verts() if not self.project else map(
                lambda vec: pygame.math.Vector3(vec.x, vec.y, 0), self.projection_map[face])
            for vertex in verts:
                glVertex3fv((vertex.x, vertex.y, vertex.z))
        glEnd()

    def reset_camera(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, CAMERA_DISTANCE)

    def update_state(self, changes, state):
        if changes["project"]:
            self.reset_camera()

        self.project = state["project"]
        self.rotation_speed = state["rotation_speed"]
        self.AUTOMATA_UPDATE_INTERVAL = state["delay"]

class Gui:
    def __init__(self):
        imgui.create_context()
        self.imgui_renderer = PygameRenderer()
        self.changes = {"project": False, "rotation_speed": False, "delay": False}
        self.state = {"project": True, "rotation_speed": 0.5, "delay": 0.5}

    def get_changes(self) -> Dict[str, bool]:
        return self.changes

    def get_state(self) -> Dict[str, Any]:
        return self.state

    def handle_event(self, event):
        self.imgui_renderer.process_event(event)

    def draw(self):
        imgui.begin("Controls")
        self.changes["project"], self.state["project"] = imgui.checkbox("Enable Projection", self.state["project"])
        self.changes["rotation_speed"], self.state["rotation_speed"] = imgui.slider_float("Speed", self.state["rotation_speed"], 0.1, 5.0)
        self.changes["delay"], self.state["delay"] = imgui.slider_float("Delay", self.state["delay"], 0.1, 1.5)
        imgui.end()

    def render(self):
        io = imgui.get_io()
        io.display_size = pygame.display.get_surface().get_size()
        imgui.new_frame()
        self.draw()
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())

class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_mode(DISPLAY_SIZE, DOUBLEBUF | OPENGL)

        self.celluar_automata_renderer = CellularAutomataRenderer()
        self.GUI = Gui() 

    def run(self):
        while True:
            self.handle_events()
            self.render()
            self.handle_UI_changes()

    def handle_UI_changes(self):
        self.celluar_automata_renderer.update_state(self.GUI.get_changes(), self.GUI.get_state())

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.GUI.render()
        self.celluar_automata_renderer.render()
        pygame.display.flip()
        pygame.time.wait(FRAME_DELAY_MS)

    def handle_events(self):
        for event in pygame.event.get():
            self.GUI.handle_event(event)
            if event.type == QUIT:
                pygame.quit()
                exit()

if __name__ == "__main__":
    app = App()
    app.run()