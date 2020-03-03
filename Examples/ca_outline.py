
from __future__ import annotations

import core.gui as gui
from core.gui import HOR_SEP
from core.on_off import on_off_left_upper, OnOffPatch, OnOffWorld
from core.sim_engine import SimEngine
from core.utils import bin_str

from copy import copy

from itertools import chain, repeat

import numpy as np

from random import choice

from typing import List


class CA_World(OnOffWorld):

    ca_display_size = 151

    # bin_0_to_7 is ['000' .. '111']
    bin_0_to_7 = [bin_str(n, 3) for n in range(8)]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.pos_to_switch is a dictionary that maps position values in a binary number to range(8) represented
        # as 3-digit binary strings:
        #     {1: '000', 2: '001', 4: '010', 8: '011', 16: '100', 32: '101', 64: '110', 128: '111'}
        # The three digits are the rule components and the keys to the switches.
        # To see it, try: print(self.pos_to_switch) after executing the next line.
        # The function bin_str() is defined in utils.py

        # The following two lines do the same thing. Explain how both work.
        pos_to_switch_a = {2**i: bin_str(i, 3) for i in range(8)}
        pos_to_switch_b = dict(zip([2**i for i in range(8)], CA_World.bin_0_to_7))
        assert pos_to_switch_a == pos_to_switch_b
        # self.pos_to_switch = ...  # pos_to_switch_a or pos_to_switch_b
        self.pos_to_switch = pos_to_switch_a

        # The rule number used for this run, initially set to 110 as the default rule.
        # (You might also try rule 165.)
        # The following sets the local variable self.rule_nbr. It doesn't change the 'Rule_nbr' slider widget.
        self.rule_nbr = 110
        # Set the switches and the binary representation of self.rule_nbr.
        self.set_switches_from_rule_nbr()
        self.set_binary_nbr_from_rule_nbr()
        self.get_rule_nbr_from_switches()
        self.make_switches_and_rule_nbr_consistent()

        # self.ca_lines is a list of lines, each of which is a list of 0/1. Each line represents
        # a state of the CA, i.e., all the cells in the line. self.ca_list contains the entire
        # history of the CA.
        self.ca_lines: List[List[int]] = []
        # gui.WINDOW['rows'].update(value=len(self.ca_lines))
        SimEngine.gui_set('rows', value=len(self.ca_lines))

    def build_initial_line(self):
        """
        Construct the initial CA line.
        It is a random line if SimEngine.gui_get('Random?').
        It is a line (of length ca_display_size) if SimEngine.gui_get('init_line') == ''.
        Otherwise it is the string in SimEngine.gui_get('init_line') converted into 0's and 1's.
        (' ' and '0' are converted to 0; everything else is converted to 1.)
        However, if the rule includes 000 -> 1,pad the line with 0's on both ends to fill the display.
        How much to put on each end depends on the user-specific initial line and the requested justification.
        """
        absolute = SimEngine.gui_get('absolute')
        if SimEngine.gui_get('Random?'):
            line = [choice([0,1]) for _ in range(self.ca_display_size)]
        else:
            # A line of 0's.
            padding = [0] * (self.ca_display_size)
            if SimEngine.gui_get('init') == '':
                line = padding
            else:
                line_0 = SimEngine.gui_get('init')
                print(line_0)
                # Convert line_0 to 0's and 1's
                line = [1 if c == '1' else 0 for c in line_0]
                # If the rule include 000 -> 1, fill out the new line with 0's.
                if SimEngine.gui_get('000'):
                    justification = SimEngine.gui_get('justification')
                    line_len = len(line)
                    actual_padding = padding[line_len:]
                    if absolute:
                        line = actual_padding + line if justification == 'Right' else \
                               line + actual_padding if justification == 'Left' else \
                               actual_padding + line + actual_padding #  justification == 'Center'
                    else:
                        actual_padding = [0] * self.ca_display_size
                        line = actual_padding + line + actual_padding
        return line

    @staticmethod
    def drop_extraneous_0s_from_ends_of_new_line(new_line):
        """
        Drop the end cell at each end of new_line if it is 0. Keep it otherwise.
        Return the result.
        Args:
            new_line: ca_state with perhaps extraneous 0 cells at the ends
        Returns: trimmed ca_state without extraneous 0 cells at the ends.
        """
        # checks to see if the last element of new_line is 0
        # if new_line[-1] == 0:
        #     # removes ending 0 from new_line
        #     new_line.pop(-1)
        # # checks if first element of new_line is 0
        # if new_line[0] == 0:
        #     # removes first element of new_line
        #     new_line.pop(0)

        # checks to see if the first and last elements of new_line are both 0
        if new_line[0] == 0 & new_line[-1] == 0:
            # removes ending 0 from new_line
            new_line.pop(-1)
            # removes 0 from beginning of new_line
            new_line.pop(0)

        return new_line

    def extend_ca_lines_if_needed(self, new_line):
        """
        new_line is one cell longer at each then than ca_lines[-1]. If those extra
        cells are 0, delete them. If they are 1, insert a 0 cell at the corresponding
        end of each line in ca_lines
        """
        ...

    @staticmethod
    def generate_new_line_from_current_line(prev_line):
        """
        The argument is (a copy of) the current line, i.e., copy(self.ca_lines[-1]).
        We call it prev_line because that's the role it plays in this method.
        Generate the new line in these steps.
        1. Add 0 to both ends of prev_line. (We do that because we want to allow the
        new line to extend the current line on either end. So start with a default extension.
        2. Insert an additional 0 at each end of prev_line. That's because we need a triple
        to generate the cells at the end of the new line. So, by this time the original
        line has been extended by [0, 0] on both ends.
        3. Apply the rules (i.e., the switches) to the result of step 2. This produces a line
        which is one cell shorter than the current prev_line on each end. That is, it is
        one cell longer on each end than the original prev_line.
        4. Return that newly generated line. It may have 0 or 1 at each end.
        Args:
            prev_line: The current state of the CA.
        Returns: The next state of the CA.
        """
        # Create a copy of the new line
        prev_copy = prev_line.copy()

        # Concatenate 2 zeros to the beginning and end of the copy
        prev_copy = [0, 0] + prev_copy + [0, 0]

        #
        new_line = []
        for i in range(len(prev_copy)-2):
            neighbors = str(prev_copy[i]) + str(prev_copy[i+1]) + str(prev_copy[i+2])
            new_line.append(int(SimEngine.gui_get(key=neighbors)))
        return new_line

    def get_rule_nbr_from_switches(self):
        """
        Translate the on/off of the switches to a rule number.
        This is the inverse of set_switches_from_rule_nbr(), but it doesn't set the 'Rule_nbr' Slider.
        """
        rule_nbr = 0
        for i in range(8):
            # for every element in range(8) -> [0,1,2,3,4,5,6,7]
            # 0, 1, 2, 4, 8, 16, 32 ...
            # 2^0, 2^1, 2^2 ...
            dec_value = 2 ** i

            # switch_key = '000', '001', '002'
            switch_key = self.pos_to_switch[dec_value]
            # 1 or 0, depending on checkbox
            # Implementation of SimEngine.gui_get(switch_key) runs into a None Type error
            switch_value = gui.WINDOW[switch_key].Get()
            # switch_value = SimEngine.gui_get(str(switch_key))

            rule_nbr += (2 ** i) * switch_value

        return rule_nbr

    def handle_event(self, event):
        """
        This is called when a GUI widget is changed and isn't handled by the system.
        The key of the widget that changed is in event.
        If the changed widget has to do with the rule number or switches, make them all consistent.

        This is the function that will trigger all the code you write this week
        """
        # Let OnOffWorld handle color change requests.
        '''
        We call super().handle_event(event) we want the handle_event method associated
        with the superclass 'onOffWorld, rather than the one in this class.
        The handle_event method in the super class handles the events in the color pickers,
        "SELECT_ON_TEXT" and "SELECT_OFF_TEXT" first before we proceed with changing sliders/switches/rule numbers.
        If we don't have super().handle_event(event), the colors wouldn't change unless we added the color handling
        specifically within this method.
        '''
        super().handle_event(event)

        # Handle switches and rule slider
        if event in ['Rule_nbr']:
            self.rule_nbr = SimEngine.gui_get('Rule_nbr')
        # self.bin_0_to_7 is essentially a list of all the checkbox keys
        elif event in self.bin_0_to_7:
            self.rule_nbr = self.get_rule_nbr_from_switches()
        elif event == 'justification':
            self.set_display_from_lines()
        else:
            pass
        self.make_switches_and_rule_nbr_consistent()

    def make_switches_and_rule_nbr_consistent(self):
        """
        Make the Slider, the switches, and the bin number consistent: all should contain self.rule_nbr.
        """
        # gui.WINDOW['Rule_nbr'].update(value=self.rule_nbr)
        SimEngine.gui_set('Rule_nbr', value=self.rule_nbr)
        self.set_switches_from_rule_nbr()
        self.set_binary_nbr_from_rule_nbr()


    def set_binary_nbr_from_rule_nbr(self):
        """
        Translate self.rule_nbr into a binary string and put it into the
        gui.WINDOW['bin_string'] widget. For example, if self.rule_nbr is 110,
        the string '(01101110)' is stored in gui.WINDOW['bin_string']. Include
        the parentheses around the binary number.

        Use SimEngine.gui_set('bin_string', value=new_value) to update the value of the widget.
        """
        binary_list = self.rule_nbr_to_binary_list()
        # [0, 0, 0, 1]
        # ['0', '0', '0', '1']
        binary_list_to_strs = [str(x) for x in binary_list]
        rule_nbr_to_bin_str = ''.join(binary_list_to_strs)
        SimEngine.gui_set('bin_string', value=rule_nbr_to_bin_str)

    def set_display_from_lines(self):
        """
        Copy values from self.ca_lines to the patches. There are two issues.
        1. Is self.ca_lines longer/shorter than the number of Patch rows in the display?
        2. Are there more/fewer cells-per-line than Patches-per-row?
        What do you do in each case?

        This is the most difficult method. Here is the outline I used.
        """
        # Get the current setting of 'justification'.
        justification = SimEngine.gui_get('justification')
        # Get the current setting of 'absolute'
        absolute = SimEngine.gui_get('absolute')

        # Get the two relevant widths.
        display_width = gui.PATCH_COLS

        # All the lines in self.ca_lies are the same length.
        ca_line_width = len(self.ca_lines[0])

        # How many blanks must be prepended to the line to be displayed to fill the display row?
        # Will be 0 if the ca_line is at least as long as the display row or the line is left-justified.
        left_padding_needed = 0 if ca_line_width >= display_width or justification == 'Left' else 0

        # Use [0]*n to get a list of n 0s to use as left padding.
        left_padding = [0]*left_padding_needed
        right_padding = []

        # Which elements of the ca_line are to be displayed?
        # More to the point, what is index of the first element of the line to be displayed?
        # Will be 0 if the display width is greater than or equal to the line width or we are left-justifying.
        left_ca_line_index = 0 if display_width >= ca_line_width or justification == 'Left' else 1

        # Reverse self.ca_lines?
        ca_lines_to_display = reversed(self.ca_lines)
        # Reverse the rows of CA_World.patches_array
        patch_rows_to_display_on = np.flip(CA_World.patches_array, axis=0)

        # Now we can use zip to match up ca_lines_to_display and patch_rows_to_display on.
        # In both cases we are starting at the bottom and working our way up.
        ca_lines_patch_rows = zip(ca_lines_to_display, patch_rows_to_display_on)

        # zip is given two iterables and produces a sequence of pairs of elements, one from each.
        # An important feature of zip is that it stops whenever either of its arguments ends.
        # In particular, the two arguments needn't be the same length. Zip simply uses all the
        # elements of the shorter and pairs them with the initial elements of the longer.

        # We can now step through the corresponding pairs.
        for (ca_line, patch_row) in ca_lines_patch_rows:
            # The values in ca_line are to be displayed on patch_row.
            # The issue now is how to align them.

            # Which elements of ca_line should be displayed?
            # We display the elements starting at left_ca_line_index (computed above).

            # Left absolute justification displays the right half of the line.
            # Center absolute displays everything in the center of the line.
            # Right absolute displays everything in the left half of the line.
            if absolute:
                # Left -> Slice of everything on the left half
                # Center -> Keep as is
                # Right -> Slice of everything on the right half
                ca_line_portion = ca_line[len(ca_line) // 2:] if justification == 'Left' \
                    else ca_line if justification == 'Center' \
                    else ca_line[:(len(ca_line) // 2) + 1]

                num_pad = display_width - len(ca_line_portion)

                if justification == 'Left':
                    right_padding = [0] * num_pad if len(ca_line_portion) < display_width else []

                elif justification == 'Right':
                    if num_pad > 0:
                        left_padding = [0] * num_pad
                    else:
                        center_of_line = len(ca_line_portion)
                        start_to_display = center_of_line - display_width
                        ca_line_portion = ca_line[start_to_display:center_of_line]
                        left_padding = []
            else:
                ca_line_portion = ca_line[:display_width] if justification == 'Left' else \
                                  ca_line if justification == 'Center' else \
                                  ca_line[::-1][:display_width] if len(ca_line) > display_width and justification == 'Right' else \
                                  ca_line[::-1]
                left_padding = [0] * ((len(self.ca_lines[-1]) // 2) - (len(ca_line) // 2))

            if justification == 'Center':
                num_pad = display_width // 2 - len(ca_line_portion) // 2
                if num_pad > 0:
                    left_padding = [0] * num_pad
                    right_padding = [0] * num_pad
                else:
                    center_of_line = len(ca_line_portion) // 2
                    start_to_display = center_of_line - display_width // 2
                    ca_line_portion = ca_line[start_to_display:center_of_line + (display_width // 2) + 1]
                    left_padding = []

            # For the complete display line and the desired justification,
            # we may need to pad ca_line_portion to the left or right (or both).
            # We need left_padding_needed 0's to the left and an arbitrary sequence of 0's to the right.
            # (Use repeat() from itertools for the padding on the right. It doesn't matter if it's too long!)

            # Put the three pieces together to get the full line.
            # Use chain() from itertools to combine the three parts of the line:
            #          left_padding, ca_line_portion, right_padding.

            padded_line = chain(left_padding, ca_line_portion, right_padding)
            # padded_line has the right number of 0's at the left. It then contains the elements from ca_line
            # to be displayed. If we need more elements to display, padded_line includes an unlimted number of
            # trailing 0's.

            # Since padded_line will be dispalyed on patch_row, we can use zip again to pair up the values
            # from padded_line with the Patches in patch_row. Since padded_line includes an unlimited number
            # of 0's at the end, zip will stop when it reaches the last Patch in patch_row.

            ca_values_patchs = zip(padded_line, patch_row)
            if justification == 'Right' and not absolute:
                ca_values_patchs = zip(padded_line, reversed(patch_row))

            # Step through these value/patch pairs and put the values into the associated Patches.
            for (ca_val, patch) in ca_values_patchs:
                # Use the set_on_off method of OnOffPatch to set the patch to ca_val.
                patch.set_on_off(ca_val)

    def set_switches_from_rule_nbr(self):
        """
        Update the settings of the switches based on self.rule_nbr.
        Note that the 2^i position of self.rule_nbr corresponds to self.pos_to_switch[i]. That is,
        self.pos_to_switch[i] returns the key for the switch representing position  2^i.
        Set that switch as follows: gui.WINDOW[self.pos_to_switch[pos]].update(value=new_value).
        Set that switch as follows: SimEngine.gui_set(self.pos_to_switch[pos], value=new_value).
        (new_value will be either True or False, i.e., 1 or 0.)
        This is the inverse of get_rule_nbr_from_switches().
        """

        # List of 0s and 1s... based off of rule number (binary)
        # [0, 1, 1, 0, 1, 1, 1, 0]
        rule_nbr_to_binary = list(reversed(self.rule_nbr_to_binary_list()))

        for i in range(8):
            # for every element in range(8) -> [0,1,2,3,4,5,6,7]
            dec_value = 2 ** i
            SimEngine.gui_set(self.pos_to_switch[dec_value], value=rule_nbr_to_binary[i])
            # checks every element in the list if it is a 0
            # If there is a zero, then the method tells the gui to uncheck the switch at
            # the position corresponding to dec_value. If there is a 1, then
            # it is checked

    def rule_nbr_to_binary_list(self):
        # Rule number is a decimal value.. ex.. 110
        # Method takes the decimal value of the rule number and uses a range of 8 to determine
        # if a 1 or a 0 is added to an array
        temp_rule_nbr = self.rule_nbr
        rule_nbr_to_binary = []
        # Range(8) is an iterator 0, 1, 2, 3, ... 7
        # Reverse it to make it 7, 6, 5, ... 0
        for i in reversed(range(8)):
            # use a sequence incrementing down from 7 to 0 with i being an element in the sequence
            dec_value = 2 ** i
            if temp_rule_nbr >= dec_value:
                temp_rule_nbr -= dec_value
                rule_nbr_to_binary.append(1)
            else:
                rule_nbr_to_binary.append(0)
                # ex. let temp_rule_nbr = 150
                # 150 > 128, 150-128 = 22, [1]
                # 22 < 64, 22, [1,0]
                # 22 < 32, 22, [1,0,0]
                # 22 > 16, 6, [1,0,0,1]
                # 6 < 8, 6, [1,0,0,1,0]
                # 6 > 4, 2, [1,0,0,1,0,1]
                # 2 = 2, 0, [1,0,0,1,0,1,1]
                # [1,0,0,1,0,1,1,0]
        return rule_nbr_to_binary

    def setup(self):
        """
        Make the slider, the switches, and the bin_string of the rule number consistent with each other.
        Give the switches priority.
        That is, if the slider and the switches are both different from self.rule_nbr,
        use the value derived from the switches as the new value of self.rule_nbr.

        Once the slider, the switches, and the bin_string of the rule number are consistent,
        set self.ca_lines[0] as directed by SimEngine.gui_get('justification').

        Copy (the settings on) that line to the bottom row of patches.
        Note that the lists in self.ca_lines are lists of 0/1. They are not lists of Patches.
        """
        # Review by: Wilson Weng
        # The method follows standard PEP 8 indentation and spacing rules.
        # The method sets ca_lines with an empty array to reset any changes
        # The method then adds to ca_lines with values from build_initial_line()
        # values from build_initial_line() dependant on the value select from the Initial Row GUI
        # The method finally calls set_display_from_lines() to setup the first line

        # Reset self.ca_lines
        self.ca_lines = []
        # Build initial line and append it to self.ca_lines
        self.ca_lines.append(self.build_initial_line())
        # Update the display based off of self.ca_lines
        self.set_display_from_lines()

    def step(self):
        """
        Take one step in the simulation.
        (a) Generate an additional line for the ca. (Use a copy of self.ca_lines[-1].)
        (b) Extend all lines in ca_lines if the new line is longer (with additional 1's) than its predecessor.
        (c) Trim the new line and add to self.ca_lines
        (d) Refresh display from values in self.ca_lines.
        """
        # (a)
        new_line = self.generate_new_line_from_current_line(self.ca_lines[-1]) # The new state derived from self.ca_lines[-1]

        # (b)
        # Extend lines in self.ca_lines at each end as needed. (Don't extend for extra 0's at the ends.)
        # Can't drop the 0's first because we then lose track of which end was extended.
        new_line = self.drop_extraneous_0s_from_ends_of_new_line(new_line)

        # (c)
        trimmed_new_line = ... # Drop extraneous 0s at the end of new_line
        # Add trimmed_new_line to the end of self.ca_lines
        self.ca_lines.append(new_line)
        # (d)

        # Refresh the display from self.ca_lines
        self.set_display_from_lines()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

""" 
The following appears at the top-left of the window. 
"""
# By: Wilson Weng
# The method takes PySimpleGui and creates Initial Row and Rows with sg.Text()
# Initial Row is a combo box containing Left, Right ,Center, and Random all set as values
# also sets a key 'init' and defaults to Right
# Rows shows the amount of rows that the program created with a key 'rows'
# values and key in 'Inital Row' are sent to the method build_initial_line
# key in Rows is sent to __init__
ca_left_upper = [[sg.CB('Absolute?', key='absolute', enable_events=True, default=True,
                 tooltip="Sets the justification type to absolute")],

                 [sg.Text('Row justification'),
                 sg.Combo(values=['Left', 'Center', 'Right'], key='justification', default_value='Right')],

                 HOR_SEP(30),

                 [sg.Text('Initial row:', pad=(None, (20, 0)),
                          tooltip="0's and 1's for the initial row. An empty \n" +
                                  "string will set the initial row to all 0's."),
                  sg.Input(default_text="1", key='init', size=(20, None), text_color='white',
                           background_color='steelblue4', justification='center')
                ],

                 [sg.CB('Random?', key='Random?', enable_events=True,
                        tooltip="Set the initial row to random 0's and 1's.")],

                 HOR_SEP(30, pad=(None, None)),

                 [sg.Text('Rows:'), sg.Text('     0', key='rows')],

                 HOR_SEP(30, pad=(None, (0, 10)))

                 ] + on_off_left_upper


# The switches are CheckBoxes with keys from CA_World.bin_0_to_7 (in reverse).
# These are the actual GUI widgets, which we access via their keys.
# The pos_to_switch dictionary maps position values in the rule number as a binary number
# to these widgets. Each widget corresponds to a position in the rule number.
# Note how we generate the text for the chechboxes.
switches = [sg.CB(n+'\n 1', key=n, pad=((30, 0), (0, 0)), enable_events=True) for n in reversed(CA_World.bin_0_to_7)]

""" 
This  material appears above the screen: 
the rule number slider, its binary representation, and the switch settings.
"""
ca_right_upper = [[sg.Text('Rule number', pad=((100, 0), (20, 10))),
                   sg.Slider(key='Rule_nbr', range=(0, 255), orientation='horizontal',
                             enable_events=True, pad=((10, 20), (0, 10))),
                   sg.Text('00000000 (binary)', key='bin_string', enable_events=True, pad=((0, 0), (10, 0)))],

                  switches
                  ]


if __name__ == "__main__":
    """
    Run the CA program. PyLogo is defined at the bottom of core.agent.py.
    """
    from core.agent import PyLogo

    # Note that we are using OnOffPatch as the Patch class. We could define CA_Patch(OnOffPatch),
    # but since it doesn't add anything to OnOffPatch, there is no need for it.
    PyLogo(CA_World, '1D CA', patch_class=OnOffPatch,
           gui_left_upper=ca_left_upper, gui_right_upper=ca_right_upper,
           fps=10, patch_size=3, board_rows_cols=(CA_World.ca_display_size, CA_World.ca_display_size))
