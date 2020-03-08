from __future__ import annotations

from pygame import Color
import core.gui as gui
from core.agent import Agent
from core.gui import BLOCK_SPACING, HOR_SEP, SCREEN_PIXEL_HEIGHT, SCREEN_PIXEL_WIDTH
from random import uniform
import core.utils as utils



class NW_World():

    def __init__(self):
        super().__init__()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

nw_left_upper =[
    [sg.Text('layout'),
     sg.Combo(values=['Spring', 'Circle', 'Radial', 'tutte'], key='layout', default_value='Spring'),
     sg.Text('links-to-use'),
     sg.Combo(values=['Undirected', 'Directed'], key='links', default_value='Undirected')
     ],

    [sg.CB('Clear Before Generating?', enable_events=True, size=(20, 1), key='clear')],

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

    HOR_SEP(30, pad=(None, None)),
]



window = sg.Window('Networking', nw_left_upper)

event, values = window.Read()
window.close()

if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(NW_World, 'Networking', gui_left_upper=nw_left_upper, patch_size=3,
           board_rows_cols=(151, 151))




