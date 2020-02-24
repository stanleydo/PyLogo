
import core.gui as gui
from core.gui import HOR_SEP
from core.on_off import on_off_left_upper, OnOffPatch, OnOffWorld
from core.sim_engine import SimEngine
from core.utils import bin_str

from copy import copy

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
        self.init = None

        # self.ca_lines is a list of lines, each of which is a list of 0/1. Each line represents
        # a state of the CA, i.e., all the cells in the line. self.ca_list contains the entire
        # history of the CA.
        self.ca_lines: List[List[int]] = []
        #
        SimEngine.gui_set('rows', value=len(self.ca_lines))

    def build_initial_line(self):
        """
        Construct the initial CA line
        """
        self.init = SimEngine.gui_get(key='init')
        if self.init == 'Random':
            # Set the initial row to random 1/0.
            # You complete this line.
            # Line is basically a list of 0's or 1's with a length of "ca_display_size".
            """
            I wrote a list comprehension that uses random.choice() which picks a random 1 or 0
            for every '_' in the range(self.ca_display_size). Note that we don't actually use '_',
            it's just there to say I want a random choice ca_display_size many times.
            """
            line = [choice([0,1]) for _ in range(self.ca_display_size)]
        else:
            line = [0] * self.ca_display_size
            col = 0 if self.init == 'Left' else \
                  CA_World.ca_display_size // 2 if self.init == 'Center' else \
                  CA_World.ca_display_size - 1   # self.init == 'Right'
            line[col] = 1
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
        ...

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
        ...
        # return new_line
        return None

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

        Use gui.WINDOW['bin_string'].update(value=new_value) to update the value of the widget.
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
        Copy values from self.ca_lines to the patches. One issue is dealing with
        cases in which there are more or fewer lines than Patch row.
        """
        # Create a current row counter
        cur_row = 0
        # self.ca_lines represents a list of lists ..
        # [[0, 1, 0, 1, 1, 1, .... 0], ... [0, 0, 0, 1, 0, 1 .... 1]]
        # We can iterate through each list in self.ca_lines
        # Doing this, we can make sure we set the same amount of rows.
        for line in self.ca_lines:
            # We can use the cur_row index of the reversed patches_array
            '''
            The patches array is a 2D array that contains all the patches on the board.
            We can use this to access patches using a row by column structure and set them to the correct value.
            View world_patch_block.py (World Superclass) to see how it is generated.
            '''
            # We reverse (self.patches_array[::-1]) the patches_array so we can start on the bottom
            # (Rows start from the top normally)
            # We use cur_row to index the patch_row. This will give us a list of all the patch objects in that row.
            patch_row = self.patches_array[::-1][cur_row]
            # Create a line index counter
            line_index = 0
            # Set the patch to either on or off depending on line[line_index]
            for patch in patch_row:
                patch.set_on_off(line[line_index])
                line_index += 1
            cur_row += 1

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
        set self.ca_lines[0] as directed by SimEngine.gui_get('init').

        Copy (the settings on) that line to the bottom row of patches.
        Note that the lists in self.ca_lines are lists of 0/1. They are not lists of Patches.
        """
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
        (b) Extend all lines in ca_lines if the new line is longer than its predecessor.
        (c) Trim the new line and add to self.ca_lines
        (d) Copy self.ca_lines to the display
        """
        # (a)
        new_line = ... # The new state derived from self.ca_lines[-1]

        # (b)
        ... # Extend lines in self.ca_lines at each end as needed.

        # (c)
        trimmed_new_line = ... # Drop extraneous 0s at the end of new_line
        ... # Add trimmed_new_line to the end of self.ca_lines

        # (d)
        ... # Refresh the display from self.ca_lines



# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

""" 
The following appears at the top-left of the window. 
It puts a row consisting of a Text widgit and a ComboBox above the widgets from on_off.py
"""
ca_left_upper = [[sg.Text('Initial row:'),
                  sg.Combo(values=['Left', 'Center', 'Right', 'Random'], key='init', default_value='Right')],
                 [sg.Text('Rows:'), sg.Text('     0', key='rows')],
                 HOR_SEP(30)] + \
                 on_off_left_upper

# The switches are CheckBoxes with keys from CA_World.bin_0_to_7 (in reverse).
# These are the actual GUI widgets, which we access via their keys.
# The pos_to_switch dictionary maps position values in the rule number as a binary number
# to these widgets. Each widget corresponds to a position in the rule number.
# Note how we generate the text for the chechboxes.
switches = [sg.CB(n + '\n 1', key=n, pad=((30, 0), (0, 0)), enable_events=True)
                                             for n in reversed(CA_World.bin_0_to_7)]

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
