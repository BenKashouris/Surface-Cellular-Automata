import trimesh

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