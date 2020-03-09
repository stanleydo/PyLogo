from __future__ import annotations

from pygame import Color
import core.gui as gui
from core.agent import Agent
from core.gui import BLOCK_SPACING, HOR_SEP, SCREEN_PIXEL_HEIGHT, SCREEN_PIXEL_WIDTH
from core.sim_engine import SimEngine
from random import uniform
import core.utils as utils
from core.world_patch_block import World
from core.pairs import Pixel_xy

import random

# NW_Node is a subclass of Agent
class NW_Node(Agent):

    def __init__(self, **kwargs):
        # Define a shape name. Usable shapes are found gui.SHAPES.
        # Some other examples are "netlogo_figure" (default), "square", and "star".
        # TODO -- Add a GUI Element for selecting SHAPES, similar to "Force_and_effects.py"
        shape_name = 'circle'

        # Initialize the super class to take advantage of methods and variables
        super().__init__(shape_name=shape_name, **kwargs)

        # Moves the agent in a random direction a random int (x,y) many pixels
        self.forward(random.randint(10, 300))

    # TODO
    def make_links(self):
        pass

class NW_World(World):

    def __init__(self, patch_class, agent_class):
        super().__init__(patch_class, agent_class)

        # True means the next generation of nodes will have directed links.
        self.directed_link: bool = None

        # Layout defines the way the agents move and react to one another
        # We only need to worry about Spring right now.
        self.layout: str = None

        # If this is True, we want to re-set the board before we generate anything else.
        self.clear_before_gen: bool = None

        # Number of nodes we want to generate
        self.nb_nodes: int = None

        # Updates the world's values with defaults
        self.update()

    # Updates all of the values in self from their respective gui elements.
    def update(self):
        self.directed_link = bool(int(SimEngine.gui_get(key='directed_link')))
        self.layout = SimEngine.gui_get(key='Layout')
        self.clear_before_gen = bool(int(SimEngine.gui_get(key='clear')))
        self.nb_nodes = SimEngine.gui_get(key='nb-nodes')

    def preferential_attachment(self):

        # Clears the grid if the option is checked.
        if self.clear_before_gen:
            self.clear_all()

        # Creates nodes based off the number of nodes and places them randomly on the grid
        for _ in range(self.nb_nodes):
            self.agent_class()

    def ring(self):
        ...

    def small_world(self):
        ...

    def lattice_2D(self):
        ...

    def handle_event(self, event):
        super().handle_event(event)

        # Update values whenever an event occurs, before we perform any other actions.
        if event:
            self.update()

        if event in 'PreAtt':
            self.preferential_attachment()

    def setup(self):

        # This method should clear the board and update its values from the GUI.
        # Not sure what else it should do really.
        self.clear_all()
        self.update()

    def step(self):
        pass



import PySimpleGUI as sg

nw_left_upper =[
    # [sg.Button('Setup', key='Setup'), sg.Button('Go', key='Go'), sg.Button('Go Once', key='Step')],

    [sg.Text('Layout'),
     sg.Combo(values=['Spring', 'Circle', 'Radial', 'Tutte'], key='Layout', default_value='Spring'),
     sg.CB('Directed Link?', enable_events=True, key='directed_link', default=False)
     ],

    [sg.CB('Clear Before Generating?', enable_events=True, default=True, size=(20, 1), key='clear')],

    HOR_SEP(30, pad=(None, None)),

    [sg.Text('nb-nodes'),
     sg.Slider(key='nb-nodes', range=(0, 1000), default_value=100, orientation='horizontal')],

    [sg.Button(button_text='PreAtt', key='PreAtt'),
     sg.Button(button_text='Ring', key='Ring'),
     sg.Button(button_text='Star', key='Star')],

    HOR_SEP(30, pad=(None, None)),

    [sg.Text('neighborhood-size'),
     sg.Slider(key='nb-size', range=(0, 60), default_value=3, orientation='horizontal')],

    [sg.Button(button_text='SmallWorld', key='SmallWorld'),
     sg.Text('rewire-prob'),
     sg.Slider(key='rewire-prob', range=(0, 1), resolution=.01, default_value=0.2, orientation='horizontal')
     ],

    HOR_SEP(30, pad=(None, None)),

    [sg.Button(button_text='Lattice2D', key='Lattice2D'),
     sg.CB('Wrap?', size=(10, 1), key='wrap')
     ],

    [sg.Text('num-rows'),
     sg.Slider(key='num-rows', range=(0, 20), default_value=8, orientation='horizontal')],

    [sg.Text('num-cols'),
     sg.Slider(key='num-cols', range=(0, 20), default_value=8, orientation='horizontal')],

]

if __name__ == "__main__":
    from core.agent import PyLogo
    # Runs PyLogo using the NW_World and NW_Node
    PyLogo(NW_World, 'Networking', gui_left_upper=nw_left_upper, agent_class=NW_Node, bounce=True)




