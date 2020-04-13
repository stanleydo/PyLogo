

from pygame import color
from core.agent import Agent
from core.pairs import center_pixel, RowCol, Pixel_xy, Velocity
from core.sim_engine import SimEngine
from core.world_patch_block import World, Patch
from pygame.color import Color
from core.gui import PATCH_ROWS, PATCH_COLS, SCREEN_PIXEL_WIDTH, SCREEN_PIXEL_HEIGHT
from random import uniform

# TODO -- Testing:
# Test spawn-commuters rate and make sure we have constants good enough for the tickrate
# Spawn a commuter from a patch and test moving in specified directions
# Test World.reset_all() and setup so that we do not have anything unaccounted for
# Constantly check our numbers for smoothing and averages for NetLogo-like results
# Test what happens when there are multiple turtles on one patch

middle_road = 'middle'
dynamic_road = 'dynamic'
static_road = 'static'

# We specify our own subclass of Agent, so we can add some additional properties.
class Commuter(Agent):

    def __init__(self, spawn_pixel: Pixel_xy, facing: Pixel_xy):
        super().__init__(center_pixel=spawn_pixel, color=Color('Yellow'), scale=1)
        self.set_velocity(Velocity((1,0)))
        self.face_xy(facing)

        self.recently_changed = False
        self.birth_tick = None
        self.ticks_here = None
        self.route = None

    def move(self):
        # We can use self.current_patch() to get the patch this agent is on.
        my_patch = self.current_patch()

        # If I've been here long enough, set the patch's last_here to the World's ticks and move 1 unit
        if self.ticks_here > my_patch.delay:
            my_patch.last_here = World.ticks
            # Move commuter to next patch (in direction its facing)
            # Can be implemented by facing_xy and moving it 1 unit in that direction.
            #Re-set ticks_here to 1
        else:
            self.ticks_here += 1

        # if I reach the top-right and my route is 0, face the bottom right
        # if I reach the top-right and my route is 2, face the bottom left
        # if I reach the bottom left, face the bottom right
        # if I reach the bottom right, i end my commute.

    def new_route(self):
        # new-route
        # in an if-else statement, check the mode selected from the interface
        # go to the associated method
        m = SimEngine.gui_get('mode')
        if m == emp_analytical:
            World.emp_analytical()
        if m == best_known_w_ran_dev:
            World.best_known_w_ran_dev()
        if m == probabilistic_greedy:
            World.probabilistic_greedy()

    def end_commute(self):
        # Reports the average travel time.
        # Also reports top, bottom, and middle travel times of the last commuter to end.
        World.travel_time = (World.ticks - self.birth_tick) / 450
        World.avg = World.travel_time if World.avg == 0 else ((19 * World.avg + World.travel_time) / 20)
        if self.route == 0:
            World.top = World.travel_time if World.top == 0 else ((World.travel_time) + \
                                                                  ((World.smoothing - 1) * World.top)) / World.smoothing
        if self.route == 1:
            World.bottom = World.travel_time if World.bottom == 0 else ((World.travel_time)+ \
                                                                        ((World.smoothing - 1) * World.bottom)) / World.smoothing
        # Calculate and set World.middle
        self.kill()

# We specify our own subclass of Patch, so we can add some additional properties.
class Braess_Patch(Patch):

    def __init__(self, row_col: RowCol, color=Color('black')):
        super.__init__(row_col.patch_to_center_pixel(), color)
        self.delay = None
        self.base_delay = None
        self.road_type = None
        self.last_here = None

    def determine_congestion(self):
        # procedure for dynamic patches
        # if patch last_here is nothing, we can go fast and set delay to base_delay / 2
        # else we set the delay to be (((250 / spawn-rate)/(World.ticks - last_here + 1)) * base_delay)
        # Then we set the patch color to be more red or yellow (255 G 0) depending on the calculation:
        # 255 + floor (255 * (0.5 - (delay / base-delay))) by adding more or less green
        pass

# We specify our own subclass of World, so we can add some additional properties.
class Braess_World(World):

    def __init__(self, patch_class, agent_class):
        super().__init__(patch_class, agent_class)
        self.travel_time = None
        self.top = None
        self.bottom = None
        self.middle = None
        self.spawn_time = 0
        self.middle_prev = None
        self.avg = None
        self.cars_spawned = None
        self.top_prob = None
        self.bottom_prob = None
        self.middle_prob = None

        # Define the corner patches.
        self.top_left = None
        self.top_right = None
        self.bottom_right = None
        self.bottom_left = None

        self.top_left_center_pixel = None
        self.top_right_center_pixel = None
        self.bottom_right_center_pixel = None
        self.bottom_left_center_pixel = None

    def reset_all(self):
        super().reset_all()
        self.travel_time = None
        self.top = None
        self.bottom = None
        self.middle = None
        self.spawn_time = 0
        self.middle_prev = None
        self.avg = None
        self.cars_spawned = None
        self.top_prob = None
        self.bottom_prob = None
        self.middle_prob = None
        self.top_left = None
        self.top_right = None
        self.bottom_right = None
        self.bottom_left = None

    def setup_roads(self):
        # 1. Cover everything in random green grass (set all patches a random green color)

        # 2. Set colors and properties on all corners
        self.top_left.set_color(Color('Green'))
        self.top_right.set_color(Color('Blue'))
        self.bottom_left.set_color(Color('Blue'))
        self.bottom_right.set_color(Color('Red'))

        # 3. Draw roads between corners

        # 4. Set global variable middle_prev to the middle_on from the GUI.

        # 5. Draw the middle road based on whether it's on or off


    def draw_road(self, type_of_road, start, finish):
        # Road types are:
        # 'static' - Static congestion road
        # 'dynamic' - Dynamic congestion road
        # 'middle' - Middle road

        if type_of_road == static_road:
            pass
        elif type_of_road == dynamic_road:
            pass
        # Middle Road ... type_of_road == middle_road
        else:
            pass


        # Calculate the direction of the heading from start to finish
        # Loop and go through the patches in the direction of your heading
        # For middle roads, set yourself, left, and bottom patches to gray or textured depending on middle-on
        # For horizontal roads, color the patches on the top and bottom of your path.
        # For vertical roads, color the patches on the left and right of your path to the finish.
        # We can also set attributes such as delay, road-type, and base-delay for these patches as we iterate
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

        if self.spawn_time > 250/SimEngine.gui_get('spawn_rate'):
            # self.agent_class() creates a class at a certain pixel.
            # This line creates an agent at the center pixel of the top left patch.
            self.agent_class(spawn_pixel=self.top_left_center_pixel,
                             facing=self.top_right_center_pixel)
            self.spawn_time = 0
        else:
            self.spawn_time += 1

        # Note we probably won't use 250.
        # track spawn-time, if spawn-time is greater than 250 / spawn-rate,
        # at the patch in the upper left corner, spawn a commuter
        # with several values associated with time spawned, the time it is still commuting,
        # the route it will take, and it's behavior when choosing a route
        pass

    def setup(self):
        # Clear everything
        self.reset_all()

        # Set the corner patches
        self.top_left: Braess_Patch = World.patches_array[2][2]
        self.top_right: Braess_Patch = World.patches_array[2][PATCH_COLS-3]
        self.bottom_right: Braess_Patch = World.patches_array[PATCH_ROWS - 3][PATCH_COLS - 3]
        self.bottom_left: Braess_Patch = World.patches_array[PATCH_ROWS-3][2]

        self.top_left_center_pixel = self.top_left.row_col.patch_to_center_pixel()
        self.top_right_center_pixel = self.top_right.row_col.patch_to_center_pixel()
        self.bottom_right_center_pixel = self.bottom_right.row_col.patch_to_center_pixel()
        self.bottom_left_center_pixel = self.bottom_left.row_col.patch_to_center_pixel()

        # Set up the roads
        self.setup_roads()

    def step(self):
        # Constantly check the middle in case it's activated mid-go
        # self.check_middle()

        # Keep spawning commuters
        self.spawn_commuters()

        # for commuter in World.agents:
        #     commuter.move()
        #
        # for patch in [patches for patches in World.patches if patches.road_type == 1]:
        #     patch.determine_congestion()

        for agent in self.agents:
            agent.forward(1)
            agent.route = 2

        # Agents in the top right patch
        agents_in_top_right = self.top_right.agents
        # Loop through the agents and check if they are going for the middle route.
        for agent in agents_in_top_right:
            if agent.route == 2 and not agent.recently_changed:
                agent.move_to_xy(self.top_right_center_pixel)
                agent.face_xy(self.bottom_left_center_pixel)
                agent.recently_changed = True

    def emp_analytical(self):
        # check each route available, counting the number of commuters in each route
        # the commuter will take the path that with the least number of other commuters
        # Returns 0, 1, or 2
        pass

    def best_known_w_ran_dev(self):
        # Pick a route that has the best travel time with the gui's randomness chance to deviate to a longer route.
        # Returns 0, 1, or 2
        pass

    def probabilistic_greedy(self):
        # Picks a route by the probability of how "good it is" (by travel time).
        # Returns 0, 1, or 2
        pass


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
