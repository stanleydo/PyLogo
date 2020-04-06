

from pygame import color
from core.agent import Agent
from core.pairs import center_pixel, RowCol
from core.world_patch_block import World, Patch
from pygame.color import Color
from core.gui import PATCH_ROWS, PATCH_COLS

# We specify our own subclass of Agent, so we can add some additional properties.
class Commuter(Agent):

    def __init__(self):
        super().__init__(center_pixel=center_pixel, color=color, scale=1)
        self.birth_tick = None
        self.ticks_here = None
        self.route = None

    def move(self):
        pass

    def end_commute(self):
        World.travel_time = (World.ticks - self.birth_tick) / 450
        World.avg = World.travel_time if World.avg == 0 else ((19 * World.avg + World.travel_time) / 20)
        if self.route == 0:
            World.top = World.travel_time if World.top == 0 else ((World.travel_time) + \
                                                                  ((World.smoothing - 1) * World.top)) / World.smoothing
        if self.route == 1:
            World.bottom = World.travel_time if World.bottom == 0 else ((World.travel_time)+ \
                                                                        ((World.smoothing - 1) * World.bottom)) / World.smoothing

# We specify our own subclass of Patch, so we can add some additional properties.
class Braess_Patch(Patch):

    def __init__(self):
        super().__init__(row_col=RowCol.patch_to_center_pixel(), color=Color("Black"))
        self.delay = None
        self.base_delay = None
        self.road_type = None
        self.last_here = None

    def reset(self):
        self.delay = None
        self.base_delay = None
        self.road_type = None
        self.last_here = None

    def determine_congestion(self):
        pass

# We specify our own subclass of World, so we can add some additional properties.
class Braess_World(World):

    def __init__(self, patch_class, agent_class):
        super().__init__(patch_class, agent_class)
        self.travel_time = None
        self.top = None
        self.bottom = None
        self.middle = None
        self.spawn_time = None
        self.middle_prev = None
        self.avg = None
        self.cars_spawned = None
        self.top_prob = None
        self.bottom_prob = None
        self.middle_prob = None

        # I might move this into Setup Roads.
        # Define the corner patches.
        self.top_left: Patch = World.patches_array[2][2]
        self.top_right: Patch = World.patches_array[2][PATCH_COLS-3]
        self.bottom_right: Patch = World.patches_array[PATCH_ROWS - 3][PATCH_COLS - 3]
        self.bottom_left: Patch = World.patches_array[PATCH_ROWS-3][2]

    def reset(self):
        self.travel_time = None
        self.top = None
        self.bottom = None
        self.middle = None
        self.spawn_time = None
        self.middle_prev = None
        self.avg = None
        self.cars_spawned = None
        self.top_prob = None
        self.bottom_prob = None
        self.middle_prob = None

    def setup_roads(self):
        # 1. Cover everything in random green grass

        # 2. Set colors and properties on all corners
        self.top_left.set_color(Color('Green'))
        self.top_right.set_color(Color('Blue'))
        self.bottom_left.set_color(Color('Blue'))
        self.bottom_right.set_color(Color('Red'))

        # 3. Draw roads between corners

        # 4. Set global variable middle_prev to the middle_on from the GUI.

        # 5. Draw the middle road based on whether it's on or off


    def draw_roads(self, type_of_road, start, finish):
        pass

    def check_middle(self):
        # Check-Middle
        # If the middle-on? (GUI) doesn't match the previous middle-on, then do this:
        # If the the middle is ON(True), draw road a road from the top right to the bottom left with road type 3 (Activated Middle).
        # Then, set the middle-prev to ON (True)
        # If the middle is OFF (else)
        # If the number of commuters (agents) taking route 2 is 0,
        # Draw a road with type 4 from the top right to bottom left (Deactivated road)
        # Then, set the middle-prev to OFF (False)
        pass

    def spawn_commuters(self):
        pass

    def setup(self):
        # Clear everything
        self.clear_all()

        # Set the corner patches
        self.top_left: Patch = World.patches_array[2][2]
        self.top_right: Patch = World.patches_array[2][PATCH_COLS-3]
        self.bottom_right: Patch = World.patches_array[PATCH_ROWS - 3][PATCH_COLS - 3]
        self.bottom_left: Patch = World.patches_array[PATCH_ROWS-3][2]

        # Set up the roads
        self.setup_roads()

    def go(self):
        self.check_middle()
        self.spawn_commuters()

        for commuter in World.agents:
            commuter.move()

        for patch in [patches for patches in World.patches if patches.road_type == 1]:
            patch.determine_congestion()



# GUI

import PySimpleGUI as sg

middle_on = 'Middle On?' # key is 'middle_on'
spawn_rate = 'Spawn Rate' # key is 'spawn_rate'
smoothing = 'Smoothing' # key is 'smoothing'
mode = 'Mode' # key is 'mode'
emp_analytical = 'Empirical Analytical'
best_known_w_ran_dev = 'Best Known w/ Random Deviation'
probabilistic_greedy = 'Probabilistic Greedy'
randomness = 'Randomness' # key is 'randomness'

braess_left_upper = [
    [sg.Checkbox('Middle On?', default=True, key='middle_on')],

    [sg.Text(spawn_rate, pad=((0,0),(15,0))),
     sg.Slider(key='spawn_rate', range=(1, 10), resolution=1, default_value=10,
            orientation='horizontal', size=(10, 20))],

    [sg.Text(smoothing, pad=((0, 0), (20, 0))),
     sg.Slider(key='smoothing', range=(1, 10), resolution=1, default_value=1,
               orientation='horizontal', size=(10, 20))],

    [sg.Text(mode, pad=((0, 0), (20, 0))),
     sg.Combo([emp_analytical, best_known_w_ran_dev, probabilistic_greedy], key='mode',
              default_value=emp_analytical, size=(28,20), pad=((0, 0), (20, 0)))],

    [sg.Text(randomness, pad=((0, 0), (15, 0))),
     sg.Slider(key='randomness', range=(0,100), resolution=1, default_value=0,
               orientation='horizontal', size=(10, 20))]
]

if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Braess_World, "Braess' Road Paradox", gui_left_upper=braess_left_upper, agent_class=Commuter, auto_setup=False)
