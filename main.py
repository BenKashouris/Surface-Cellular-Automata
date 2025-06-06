import time
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT

from OpenGL.GL import *
from OpenGL.GLU import *

import Icosphere_Mesh_data
import Automata_Engine

# --- Configuration ---
DISPLAY_SIZE = (800, 600)
FOV = 45
Z_NEAR = 0.1
Z_FAR = 50.0
CAMERA_DISTANCE = -5
ROTATION_SPEED = 0.5
FRAME_DELAY_MS = 10
AUTOMATA_UPDATE_INTERVAL = 2.5  # seconds


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
            glVertex3fv((vertex.x, vertex.y, vertex.z))
    glEnd()


def main():
    init_pygame()
    init_opengl()

    glRotatef(-1, 3, 1, 1)  # Initial rotation

    mesh = Icosphere_Mesh_data.Icosphere(3)
    automata = Automata_Engine.Engine(mesh)

    last_update_time = time.time() - AUTOMATA_UPDATE_INTERVAL # Force a draw asap

    while True:
        handle_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glRotatef(ROTATION_SPEED, 3, 1, 1)

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