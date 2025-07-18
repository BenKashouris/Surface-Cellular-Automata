import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT 
from OpenGL.GL import *
from OpenGL.GLU import *
import imgui
from imgui.integrations.pygame import PygameRenderer

from typing import Dict, Any

class ControlPanel:
    """ImGui control panel for interacting with automaton parameters."""
    def __init__(self):
        imgui.create_context()
        self.imgui_renderer = PygameRenderer()
        imgui.get_io().ini_file_name = None

        self.changes: Dict[str, bool] = {"project": False, "delay": False, "off_color": False, "on_color": False, "change_mesh": False, "draw_mode": False}
        self.state: Dict[str, Any] = {"project": True, "delay": 0.5, "on_color": (1, 1, 1), "off_color": (0, 0, 0), "draw_mode": False}

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
        self.changes["draw_mode"], self.state["draw_mode"] = imgui.checkbox("Enable Draw Mode", self.state["draw_mode"])
        if self.state["draw_mode"]:
            self.changes["project"], self.state["project"] = self.changes["draw_mode"], True
            imgui.checkbox("Enable Projection", True)
        else:
            self.changes["project"], self.state["project"] = imgui.checkbox("Enable Projection", self.state["project"])
        self.changes["delay"], self.state["delay"] = imgui.slider_float("Delay", self.state["delay"], 0.0, 1.5)
        self.changes["off_color"], self.state["off_color"] = imgui.color_edit3("Edit off color", *self.state["off_color"], flags=imgui.COLOR_EDIT_NO_INPUTS)
        self.changes["on_color"], self.state["on_color"] = imgui.color_edit3("Edit on color", *self.state["on_color"], flags=imgui.COLOR_EDIT_NO_INPUTS)
        self.changes["change_mesh"] = imgui.button("Change mesh")
        imgui.end()

    def render(self):
        """Finalizes and renders the ImGui draw data to the screen."""
        io = imgui.get_io()
        io.display_size = pygame.display.get_surface().get_size()
        imgui.new_frame()
        self.draw()
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())