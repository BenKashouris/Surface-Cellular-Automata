import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from random import randint
import time

import Icosphere_Mesh_data
import Automata_Engine


def main():
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

    glTranslatef(0.0,0.0, -5)
    glEnable(GL_DEPTH_TEST)
    glRotatef(-1, 3, 1, 1)

    Icosphere_mesh = Icosphere_Mesh_data.Icosphere(3)
    Automata = Automata_Engine.Engine(Icosphere_mesh)

    t1 = time.time()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glRotatef(1, 3, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        glBegin(GL_TRIANGLES)
        for face in Automata.get_cells():
            for vertex in face.get_verts():
                glColor3f(*face.color)
                glVertex3fv((vertex.x, vertex.y, vertex.z))
        glEnd()

        if time.time() - t1 >= 1:
            Automata.calc_next_state()
            Automata.update_state()
            t1 = time.time()

        pygame.display.flip()
        pygame.time.wait(10)

main()