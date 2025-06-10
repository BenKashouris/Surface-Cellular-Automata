# Surface-Cellular-Automata
On Cellular Automata engine on a 3d surface

Probably getting projection errors when a vertex is shared between two faces
Need to work out when to seperate these vertex
There is a one to one mapping from the 3d triangle to the 2d triangle
this means that we have to make a one to many mapping for some vertexs

To Do:
Refactor Main /
Add ordering to the faces
    Sphereical UV? 

    Project all neighbours centroid onto plane defined by face
    Then order based on angle
    Then bijected

Generate a flat surface
Create projection to flat surface

QOL:
Add a drawing mode
Add a make camera dragable
Speed up


Search for generator patterns