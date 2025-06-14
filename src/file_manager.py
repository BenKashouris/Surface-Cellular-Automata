import trimesh
from pygame import Vector3
from tkinter import filedialog, Tk
import trimesh

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

def validate_obj_mesh(mesh):
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError("Loaded object is not a triangular mesh")

    # Check if all faces are triangles
    if not mesh.faces.shape[1] == 3:
        raise ValueError("Mesh contains non-triangular faces")

    # Check number of neighbors per triangle
    adjacency = mesh.face_adjacency  # shape: (n_adjacent_edges, 2)
    face_neighbor_counts = [0] * len(mesh.faces)

    for a, b in adjacency:
        face_neighbor_counts[a] += 1
        face_neighbor_counts[b] += 1

    for i, count in enumerate(face_neighbor_counts):
        if count != 3:
            raise ValueError(f"Triangle {i} has {count} neighbors (should be 3)")
    return True

def validate_spanning_tree(mesh):
    pass
    ### Validate no cycles and surjective

if __name__ == "__main__":
    validate_obj_mesh("toros.obj")
    validate_obj_mesh("s.da")