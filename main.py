import time
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT

from OpenGL.GL import *
from OpenGL.GLU import *

import MeshData
import Automata_Engine

import numpy as np

# Config ----------------
DISPLAY_SIZE = (800, 600)
FOV = 45
Z_NEAR = 0.1
Z_FAR = 50.0
CAMERA_DISTANCE = -5
ROTATION_SPEED = 0.5
FRAME_DELAY_MS = 10
AUTOMATA_UPDATE_INTERVAL = 0.5  # seconds
PROJECT = True


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

def draw_automata(automata, projection_map = None):
    glBegin(GL_TRIANGLES)
    for face in automata.get_cells():
        glColor3f(*face.color)
        if not all(map(lambda x: tuple(x) in projection_map, face.get_verts())): continue
        for vertex in face.get_verts():
            if PROJECT:
                x, y = projection_map[tuple(vertex)]
                glVertex3fv((x, y, 0))
            else:
                glVertex3fv((vertex.x, vertex.y, vertex.z))
    glEnd()

def display_debug_faces(automata):
    import colorsys
    import random
    n = len(automata.cells)

    ### Show neighbours
    for i in range(0, n, 200):
        automata.cells[i].set_color(1, 0, 0)
        for j in range(3):
            automata.cells[i].neighbours[j].set_color(0, 1, 0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            draw_automata(automata)
            glRotatef(ROTATION_SPEED, 3, 1, 1)
            pygame.display.flip()
            pygame.time.wait(1000)

    ### Show all faces colored
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

    mesh = MeshData.Icosphere(1).get_faces()
    #mesh = MeshData.get_toros_faces()
    automata = Automata_Engine.Engine(mesh)

    projection_map = automata.get_projection_map()
    #display_debug_faces(automata)

    last_update_time = time.time() - AUTOMATA_UPDATE_INTERVAL # Force a draw asap
    while True:
        handle_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if not PROJECT: glRotatef(ROTATION_SPEED, 3, 1, 1)

        draw_automata(automata, projection_map)

        current_time = time.time()
        if current_time - last_update_time >= AUTOMATA_UPDATE_INTERVAL:
            automata.calc_next_state()
            automata.update_state()
            last_update_time = current_time

        pygame.display.flip()
        pygame.time.wait(FRAME_DELAY_MS)


if __name__ == "__main__":
    main()