import trimesh
from pygame import Vector3
from tkinter import filedialog, Tk
from typing import List

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

def get_file_from_user(file_path: str) -> str:
    """Opens a file dialog for the user to select a .obj file from the given directory.
    Args:
        file_path (str): The initial directory to open in the file dialog.
    Returns:
        str: The full path to the selected .obj file. Returns an empty string if the user cancels.
    """
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title='Open a file', initialdir=file_path, filetypes=(('object file', '*.obj'),))
    root.destroy()
    return file_path