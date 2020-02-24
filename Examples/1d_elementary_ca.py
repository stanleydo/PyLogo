from pygame.color import Color

import core.gui as gui
from core.gui import HOR_SEP
from core.utils import rgb_to_hex
from core.world_patch_block import Patch, World

import PySimpleGUI as sg

from random import randint

from typing import Tuple

# '1D Elementary Cellular Automaton'
# Mostly derived from 'Game_of_Life'


class CA_Patch(Patch):
    # These are rgb colors
    bg_color = Color('black')
    fg_color = Color('white')

    def __init__(self, *args, **kw_args):
        super().__init__(*args, **kw_args)

    # Left, middle, right status
    def LMR_status(self):
        return tuple([1 if p.is_alive else 0 for p in self.neighbors(((0,-1),(0,0),(0,1)))])

    def set_alive_or_dead(self, alive_or_dead: bool):
        self.is_alive = alive_or_dead
        self.set_color(CA_Patch.fg_color if self.is_alive else CA_Patch.bg_color)




class Life_World(World):
    WHITE = '#ffffff'
    BLACK = '#000000'

    fg_color_chooser = sg.ColorChooserButton('foreground', button_color=(WHITE, WHITE), size=(10, 1))
    bg_color_chooser = sg.ColorChooserButton('background', button_color=(BLACK, BLACK), size=(10, 1))

    SELECT_FOREGROUND_TEXT = 'Select foreground color'
    SELECT_BACKGROUND_TEXT = 'Select background color'

    current_row_index = 0
    rule = None

    # The key is the state (L, M, R), and the value is the rule number (or index in a binary string)
    # Ex. Rule 110 is '01110110' in binary. If we take allstates[(0,0,0)], we can get 7, and use that index to get the on/off result.
    all_states = {(0,0,0): 7, (0,0,1):6, (0,1,0):5, (0,1,1):4, (1,0,0):3, (1,0,1): 2, (1,1,0):1, (1,1,1):0}

    def get_color_and_update_button(self, button, default_color_string, values=None):
        if not values:
            values = self.values
        key = button.get_text()
        color_string = values.get(key, '')
        if color_string in {'None', '', None}:
            color_string = default_color_string
        button.update(button_color=(color_string, color_string))
        color = Color(color_string)
        return color

    def get_colors(self):
        CA_Patch.bg_color = self.get_color_and_update_button(
            self.bg_color_chooser,
            default_color_string=rgb_to_hex(CA_Patch.bg_color))
        CA_Patch.fg_color = self.get_color_and_update_button(
            self.fg_color_chooser,
            default_color_string=rgb_to_hex(CA_Patch.fg_color))

    def handle_event_and_values(self):
        """
        This method handles the color chooser. It does it in a round-about way because
        the color chooser can't generate events. Consequently, the user is asked to click
        a button next to the color-chooser. In processing that button-click, we ".click()"
        the color-chooser button. The user selects a color, which we retrieve by reading
        the window. We then color the color-chooser button with that color.
        """
        foreground = self.event == Life_World.SELECT_FOREGROUND_TEXT
        # There are two color-choosers: foreground and background. Determine and select the
        # desired color chooser based on the label on the button the user clicked.
        color_chooser_button = Life_World.fg_color_chooser if foreground else Life_World.bg_color_chooser
        # Run it
        color_chooser_button.click()

        # Create a default color_string in case the user had cancelled color selection.
        # The default color string is the string of the current color.
        default_color_string = rgb_to_hex(CA_Patch.fg_color if foreground else CA_Patch.bg_color)
        # Retrieve the color choice by reading the window.
        (_event, values) = gui.WINDOW.read(timeout=10)

        color = self.get_color_and_update_button(color_chooser_button, default_color_string, values)

        # Set the color to the new choice
        if foreground:
            CA_Patch.fg_color = color
        else:
            CA_Patch.bg_color = color

        # Update the patches.
        for patch in self.patches:
            patch.set_alive_or_dead(patch.is_alive)

    def mouse_click(self, xy: Tuple[int, int]):
        """ Toggle clicked patch's aliveness. """
        patch = self.pixel_tuple_to_patch(xy)
        patch.set_alive_or_dead(not patch.is_alive)

    def setup(self):
        self.get_colors()
        # Converts the gui value 'rule' into 8 bit binary
        self.rule = format(self.get_gui_value('rule'),'08b')
        density = self.get_gui_value('density')
        self.current_row_index = 0

        # iterate through the first row of patches and fill it in with the desired density
        for patch in self.patches[self.current_row_index:self.current_row_index+gui.PATCH_COLS]:
            is_alive = randint(0, 100) < density
            patch.set_alive_or_dead(is_alive)

    def step(self):

        # Currently works only if number of rows == number of cols
        # Since self.patches is just one long list, I can find out the first column of the last row
        # If our starting point is the first column of the last row, we move that last row to the top and empty the rest of the board.
        if self.current_row_index == gui.PATCH_COLS * (gui.PATCH_COLS-1):
            patch_num = 0
            for patch in self.patches[self.current_row_index-gui.PATCH_COLS: self.current_row_index+gui.PATCH_COLS]:
                if patch.is_alive:
                    self.patches[patch_num].set_alive_or_dead(True)
                else:
                    self.patches[patch_num].set_alive_or_dead(False)
                patch_num += 1
            self.current_row_index = 0
            for patch in self.patches[self.current_row_index + gui.PATCH_COLS:]:
                patch.set_alive_or_dead(False)



        # Determine and set whether each patch is_alive in the next state.
        self.get_colors()

        # cur_index gives you the index of the next row, but same column.
        cur_index = self.current_row_index + gui.PATCH_COLS
        # Iterate through the patches in the current row
        for patch in self.patches[self.current_row_index:self.current_row_index+gui.PATCH_COLS]:

            # patch_state will return a tuple (L, M, R), ex.. (0, 1, 0)
            # (0, 1, 0) means the left is off, middle is on, and right is off.
            patch_state = patch.LMR_status()
            # Returns a 0 or 1 depending on the binary index given by the state
            dead_or_alive = self.rule[self.all_states[patch_state]]

            if dead_or_alive == '0':
                self.patches[cur_index].set_alive_or_dead(False)
            else:
                self.patches[cur_index].set_alive_or_dead(True)

            cur_index += 1

        self.current_row_index += gui.PATCH_COLS


# ############################################## Define GUI ############################################## #
gui_elements = [[sg.Text('Rule #'),
                 sg.Slider(key='rule', range=(0, 255), resolution=1, size=(20, 20),
                           default_value=110, orientation='horizontal', pad=((0, 0), (0, 20)),
                           tooltip='The rules which determines the status of the next agents')],
                [sg.Text('Density'),
                 sg.Slider(key='density', range=(0, 100), resolution=1, size=(20, 20),
                           default_value=10, orientation='horizontal', pad=((0, 0), (0, 20)),
                           tooltip='The ratio of alive cells to all cells')],
                [sg.Button(Life_World.SELECT_FOREGROUND_TEXT), Life_World.fg_color_chooser],

                [sg.Button(Life_World.SELECT_BACKGROUND_TEXT), Life_World.bg_color_chooser],

                HOR_SEP(),

                [sg.Text('Cells can be toggled when\nthe system is stopped.')],
                ]

if __name__ == "__main__":
    from core.agent import PyLogo

    # Specify patch rows and columns, in case we want a larger/smaller grid
    gui.PATCH_COLS = 51
    gui.PATCH_ROWS = 51
    PyLogo(Life_World, '1D Elementary Cellular Automaton', gui_elements, patch_class=CA_Patch, bounce=None, fps=10, patch_size=5)