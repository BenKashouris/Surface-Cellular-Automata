from OpenGL.GL import *
from OpenGL.GLU import *
from pygame import Vector3
import math

class Camera:
    def __init__(self):
        self.fov = 45
        self.z_near = 0.1
        self.z_far = 50.0
        self.distance = -5

    def setup_camera_view(self, width: int, height: int) -> None:
        """Applies the perspective projection based on current camera settings."""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, width / height, self.z_near, self.z_far)
        glMatrixMode(GL_MODELVIEW)
        self.reset_orientation()

    def reset_orientation(self) -> None:
        """Resets the view."""
        glLoadIdentity()
        glTranslatef(0.0, 0.0, self.distance)

class OrbitalCamera(Camera):
    def __init__(self):
        super().__init__()
        self.radius = 5.0
        self.azimuth = 0.0     # horizontal angle (theta/yaw)
        self.elevation = 0.0   # vertical angle (phi/pitch)
        self.target = Vector3(0, 0, 0)

    def apply_view(self) -> None:
        x = self.radius * math.cos(self.elevation) * math.sin(self.azimuth)
        y = self.radius * math.sin(self.elevation)
        z = self.radius * math.cos(self.elevation) * math.cos(self.azimuth)

        eye = Vector3(x, y, z) + self.target

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(
            eye.x, eye.y, eye.z,
            self.target.x, self.target.y, self.target.z,
            0, 1, 0
        )

    def rotate(self, delta_azimuth: float, delta_elevation: float) -> None:
        """Rotates the camera around the target"""
        self.azimuth += delta_azimuth * 0.01
        self.elevation -= delta_elevation * 0.01
        self.elevation = max(-math.pi / 2 + 0.01, min(math.pi / 2 - 0.01, self.elevation))

    def zoom(self, zoom_delta: float) -> None:
        """Changes the camera's distance from the target (zoom in/out)."""
        self.radius -= zoom_delta
        self.radius = max(1.0, min(50.0, self.radius))

    def reset_orientation(self) -> None:
        """Resets the camera orientation angles (azimuth and elevation)."""
        self.azimuth = 0.0
        self.elevation = 0.0