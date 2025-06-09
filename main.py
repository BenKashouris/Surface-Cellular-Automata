import time
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT

from OpenGL.GL import *
from OpenGL.GLU import *

import Mesh_data
import Automata_Engine

import numpy as np

# Config ----------------
DISPLAY_SIZE = (800, 600)
FOV = 45
Z_NEAR = 0.1
Z_FAR = 50.0
CAMERA_DISTANCE = -15
ROTATION_SPEED = 0.5
FRAME_DELAY_MS = 10
AUTOMATA_UPDATE_INTERVAL = 0.5  # seconds
PROJECT = False


def init_pygame():
    pygame.init()
    pygame.display.set_mode(DISPLAY_SIZE, DOUBLEBUF | OPENGL)

def init_opengl():
    gluPerspective(FOV, DISPLAY_SIZE[0] / DISPLAY_SIZE[1], Z_NEAR, Z_FAR)
    glTranslatef(0.0, 0.0, CAMERA_DISTANCE)
    glEnable(GL_DEPTH_TEST)

def handle_events():
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

def draw_automata(automata):
    glBegin(GL_TRIANGLES)
    for face in automata.get_cells():
        glColor3f(*face.color)
        for vertex in face.get_verts():
            if PROJECT:
                glVertex3fv((vertex.x, vertex.y, vertex.z))
            else:
                glVertex3fv((vertex.x, vertex.y, vertex.z))
    glEnd()

def display_debug_faces(automata):
    import colorsys
    import random
    n = len(automata.cells)
    for i, cell in enumerate(automata.cells):
        r, g, b = colorsys.hsv_to_rgb(random.random(), 1, 1)
        cell.set_color(r, g, b)
    for i in range(1000):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_automata(automata)
        glRotatef(ROTATION_SPEED, 3, 1, 1)
        pygame.display.flip()
        pygame.time.wait(FRAME_DELAY_MS)

def main():
    init_pygame()
    init_opengl()

    #mesh = Mesh_data.Icosphere(3).get_faces()
    mesh = Mesh_data.get_toros_faces()
    automata = Automata_Engine.Engine(mesh)

    last_update_time = time.time() - AUTOMATA_UPDATE_INTERVAL # Force a draw asap
    while True:
        handle_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if not PROJECT: glRotatef(ROTATION_SPEED, 3, 1, 1)

        draw_automata(automata)

        current_time = time.time()
        if current_time - last_update_time >= AUTOMATA_UPDATE_INTERVAL:
            automata.calc_next_state()
            automata.update_state()
            last_update_time = current_time

        pygame.display.flip()
        pygame.time.wait(FRAME_DELAY_MS)


if __name__ == "__main__":
    main()