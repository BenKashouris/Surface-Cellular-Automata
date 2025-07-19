import trimesh
from pygame import Vector3, Vector2
from tkinter import filedialog, Tk
from typing import List, Tuple

def load_obj(file_name: str) -> List[Tuple[Vector3, Vector3, Vector3]]:
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

def point_in_triangle(p: Vector2, t: Tuple[Vector2, Vector2, Vector2]) -> bool:
    """Checks if the point p is within the triangle t
    Args:
        p (Vector2): The point to check 
        t (Tuple[Vector2, Vector2, Vector2]): The vertexs of the triangle
    Returns:
        bool: true if the point is within the triangle
    """
    a, b, c = t
    # Compute vectors
    v0 = c - a
    v1 = b - a
    v2 = p - a

    # Compute dot products
    dot00 = v0.dot(v0)
    dot01 = v0.dot(v1)
    dot02 = v0.dot(v2)
    dot11 = v1.dot(v1)
    dot12 = v1.dot(v2)

    # Compute barycentric coordinates
    denom = dot00 * dot11 - dot01 * dot01
    if denom == 0:
        return False  # Triangle is degenerate

    inv_denom = 1 / denom
    u = (dot11 * dot02 - dot01 * dot12) * inv_denom
    v = (dot00 * dot12 - dot01 * dot02) * inv_denom

    # Check if point is in triangle
    return (u >= 0) and (v >= 0) and (u + v <= 1)

if __name__ == "__main__":
    load_obj("C:/Users/benja/Documents/CS - Projects/Surface-Cellular-Automata/assets/Icosphere2.obj")