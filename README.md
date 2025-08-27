# Surface-Cellular-Automata
This project implements a cellular automaton running directly on the surface of a 3D object, rendered with OpenGL. <br>
Each triangle on the mesh is treated as a “cell,” evolving over time according to user-defined rules, with neighbours treated as those with a shared edge.


## ⚡ Features
Runs cellular automata on swappable 3D meshes. <br>
Rules and colors are flexible and customizable. <br>
Project mode: unwraps the 3D mesh into 2D for easier visualization of the automaton. <br>
Draw mode: lets you manually set an initial state by activating or deactivating cells before running the automaton.


## 📖 How the Rules Work
Rules are encoded as a string where each index corresponds to the number of active neighbours.

For example, with a rule string: 

    0101 
    Index 0 → 0 neighbours → OFF
    Index 1 → 1 neighbour → ON 
    Index 2 → 2 neighbours → OFF 
    Index 3 → 3 neighbours → ON 

## 🛠 Installation

    ⚠️ Note: Some versions of Python may not work well with OpenGL. It is recommended to use Python 3.10.11, which was used for development. 

### Step 1
Clone this repository:

    git clone https://github.com/BenKashouris/Surface-Cellular-Automata.git
    cd Surface-Cellular-Automata

### Step 2
Install the required dependencies:

    pip install -r requirements.txt

## 🚀 Usage
After installation, you can run the program with:

    python main.py
