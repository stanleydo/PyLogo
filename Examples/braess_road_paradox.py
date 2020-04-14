

from pygame import color
from core.agent import Agent
from core.pairs import center_pixel, RowCol, Pixel_xy, Velocity
from core.sim_engine import SimEngine
from core.world_patch_block import World, Patch
from pygame.color import Color
from core.gui import PATCH_ROWS, PATCH_COLS, SCREEN_PIXEL_WIDTH, SCREEN_PIXEL_HEIGHT
from random import choice, randint

# TODO -- Testing:
# Test spawn-commuters rate and make sure we have constants good enough for the tickrate
# Spawn a commuter from a patch and test moving in specified directions
# Test World.reset_all() and setup so that we do not have anything unaccounted for
# Constantly check our numbers for smoothing and averages for NetLogo-like results
# Test what happens when there are multiple turtles on one patch

middle_road = 'middle'
dynamic_road = 'dynamic'
static_road = 'static'

emp_analytical = 'Empirical Analytical'
best_known_w_ran_dev = 'Best Known w/ Random Deviation'
probabilistic_greedy = 'Probabilistic Greedy'
random_route = 'Random'
selfish = 'Selfish Route'

# We specify our own subclass of Agent, so we can add some additional properties.
class Commuter(Agent):

    def __init__(self, spawn_pixel: Pixel_xy, speed: float):
        super().__init__(center_pixel=spawn_pixel, color=Color('Yellow'), scale=1)
        self.speed = speed
        self.base_speed = 3.0

        self.last_patch = None

        self.birth_tick = None
        self.ticks_here = None
        self.route = None

    def move(self, turn_towards: Pixel_xy = None):
        if turn_towards:
            self.face_xy(turn_towards)

        self.forward(self.speed)

    def die(self):
        World.agents.remove(self)

    def end_commute(self):
        # Reports the average travel time.
        # Also reports top, bottom, and middle travel times of the last commuter to end.
        # World.travel_time = (World.ticks - self.birth_tick) / 450
        # World.avg = World.travel_time if World.avg == 0 else ((19 * World.avg + World.travel_time) / 20)
        # if self.route == 0:
        #     World.top = World.travel_time if World.top == 0 else ((World.travel_time) + \
        #                                                           ((World.smoothing - 1) * World.top)) / World.smoothing
        # if self.route == 1:
        #     World.bottom = World.travel_time if World.bottom == 0 else ((World.travel_time)+ \
        #                                                                 ((World.smoothing - 1) * World.bottom)) / World.smoothing
        # Calculate and set World.middle
        pass

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
        self.middle_on = None
        self.travel_time = None
        self.top = None
        self.bottom = None
        self.middle = None
        self.spawn_time = 0
        self.middle_prev = None
        self.avg = None
        self.cars_spawned = 0
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

        self.route_dict = {random_route: self.random_route,
                           emp_analytical: self.emp_analytical,
                           best_known_w_ran_dev: self.best_known_w_ran_dev,
                           probabilistic_greedy: self.probabilistic_greedy,
                           selfish: self.selfish_route}

    def reset_all(self):
        super().reset_all()
        self.travel_time = None
        self.top = None
        self.bottom = None
        self.middle = None
        self.spawn_time = 0
        self.middle_prev = None
        self.avg = None
        self.cars_spawned = 0
        self.top_prob = None
        self.bottom_prob = None
        self.middle_prob = None
        self.top_left = None
        self.top_right = None
        self.bottom_right = None
        self.bottom_left = None

    def setup_roads(self):
        # 1. Cover everything in random green grass (set all patches a random green color)
        for patch in World.patches:
            patch.set_color(Color(randint(0,25),randint(75,135),randint(0,25)))

        # Draw the gray areas around the corners
        for patch in [self.top_left, self.top_right, self.bottom_left, self.bottom_right]:
            for neighbors_8 in patch.neighbors_8():
                neighbors_8.set_color(Color(100,100,100))

        # 2. Set colors and properties on all corners
        self.top_left.set_color(Color('Green'))
        self.top_right.set_color(Color('Blue'))
        self.bottom_left.set_color(Color('Blue'))
        self.bottom_right.set_color(Color('Red'))

        self.draw_roads()

        self.draw_middle(SimEngine.gui_get('middle_on'))

        # 3. Draw roads between corners

        # 4. Set global variable middle_prev to the middle_on from the GUI.

        # 5. Draw the middle road based on whether it's on or off


    def draw_roads(self):
        # Top and Bottom Road
        for row in list(range(1, 4)) + list(range(PATCH_ROWS-4, PATCH_ROWS-1)):
            for col in range(3, PATCH_COLS-3):
                self.patches_array[row][col].set_color(Color(100, 100, 100))

        # Bottom Road
        for col in list(range(1,4)) + list(range(PATCH_COLS-4, PATCH_COLS-1)):
            for row in range(3, PATCH_ROWS-3):
                self.patches_array[row][col].set_color(Color(100, 100, 100))

        self.draw_middle(SimEngine.gui_get('middle_on'))

        # Calculate the direction of the heading from start to finish
        # Loop and go through the patches in the direction of your heading
        # For middle roads, set yourself, left, and bottom patches to gray or textured depending on middle-on
        # For horizontal roads, color the patches on the top and bottom of your path.
        # For vertical roads, color the patches on the left and right of your path to the finish.
        # We can also set attributes such as delay, road-type, and base-delay for these patches as we iterate
        pass

    def draw_middle(self, on_off):

        i = PATCH_ROWS - 5
        j = 4
        cur = self.patches_array[i][j]
        while j < PATCH_COLS - 4:
            cur = self.patches_array[i][j]
            for patch in set(cur.neighbors_8()):
                patch.set_color(Color(100, 100, 100))
            i -= 1
            j += 1

        if on_off:
            i = PATCH_ROWS - 5
            j = 4
            cur = self.patches_array[i][j]
            while j < PATCH_COLS - 4:
                cur = self.patches_array[i][j]
                cur.set_color(Color('Black'))
                i -= 1
                j += 1
        else:
            i = PATCH_ROWS - 5
            j = 4
            cur = self.patches_array[i][j]
            while j < PATCH_COLS - 4:
                cur = self.patches_array[i][j]
                cur.set_color(Color(100,100,100))
                i -= 1
                j += 1

    def check_middle(self):
        # Check-Middle
        # If the middle-on? (GUI) doesn't match the previous middle-on, then do this:
        if self.middle != self.middle_prev:
            if self.middle:
                self.draw_middle(True)
                self.middle_prev = True
            else:
                num_agents_taking_middle = 0
                for commuter in self.agents:
                    if commuter.route == middle_road:
                        num_agents_taking_middle += 1
                if num_agents_taking_middle == 0:
                    self.draw_middle(False)
                    self.middle_prev = False

        # If the the middle is ON(True), draw road a road from the top right to the bottom left with road type 3 (Activated Middle).
        # Then, set the middle-prev to ON (True)
        # If the middle is OFF (else)
        # If the number of commuters (agents) taking route 2 is 0,
        # Draw a road with type 4 from the top right to bottom left (Deactivated road)
        # Then, set the middle-prev to OFF (False)
        pass

    def handle_event(self, _event):
        super().handle_event(_event)

        if _event == 'middle_on':
            self.draw_middle(SimEngine.gui_get('middle_on'))

    def spawn_commuters(self):

        if self.spawn_time >= 250//SimEngine.gui_get('spawn_rate'):
            time = 0
            if SimEngine.gui_get('mode') == selfish:
                route, time = self.route_dict[SimEngine.gui_get('mode')]()
            else:
                route = self.route_dict[SimEngine.gui_get('mode')]()
            # self.agent_class() creates a class at a certain pixel.
            # This line creates an agent at the center pixel of the top left patch.
            new_commuter: Commuter = self.agent_class(spawn_pixel=self.top_left_center_pixel, speed=0.0)
            new_commuter.route = route

            new_commuter.base_speed = new_commuter.base_speed - time
            new_commuter.speed = new_commuter.base_speed

            if new_commuter.route in (middle_road, dynamic_road):
                new_commuter.face_xy(self.top_right_center_pixel)
            # Static Route
            else:
                new_commuter.face_xy(self.bottom_left_center_pixel)

            self.spawn_time = 1

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

        SimEngine.gui_set(key='ticks', value=self.ticks)
        commuters_finished = []
        nbr_commuters = 0
        nbr_commuters_dynamic = 0
        nbr_commuters_static = 0
        nbr_commuters_middle = 0
        # Constantly check the middle in case it's activated mid-go
        # self.check_middle()

        # Keep spawning commuters
        self.spawn_commuters()

        for commuter in self.agents:
            nbr_commuters += 1

            if commuter.route == dynamic_road:
                nbr_commuters_dynamic += 1
            elif commuter.route == static_road:
                nbr_commuters_static += 1
            else:
                nbr_commuters_middle += 1

            current_patch = commuter.current_patch()

            if commuter.last_patch != current_patch:
                if current_patch == self.top_right:
                    commuter.move_to_xy(self.top_right_center_pixel)
                    if commuter.route == middle_road:
                        commuter.speed = 25.0
                        commuter.move(turn_towards=self.bottom_left_center_pixel)
                    else:
                        commuter.move(turn_towards=self.bottom_right_center_pixel)
                elif current_patch == self.bottom_left:
                    if commuter.route == middle_road:
                        commuter.speed = commuter.base_speed
                    commuter.move_to_xy(self.bottom_left_center_pixel)
                    commuter.move(turn_towards=self.bottom_right_center_pixel)
                elif current_patch == self.bottom_right:
                    commuter.end_commute()
                    commuters_finished.append(commuter)
            else:
                commuter.move()

            commuter.last_patch = current_patch

        for finished_commuter in commuters_finished:
            nbr_commuters -= 1
            finished_commuter.die()

        SimEngine.gui_set(key='nbr_commuters', value=nbr_commuters)
        SimEngine.gui_set(key='nbr_commuters_dynamic', value=nbr_commuters_dynamic)
        SimEngine.gui_set(key='nbr_commuters_static', value=nbr_commuters_static)
        SimEngine.gui_set(key='nbr_commuters_middle', value=nbr_commuters_middle)

    def selfish_route(self):
        agents_on_dynamic_road = 0
        agents_on_static_road = 0
        agents_on_middle_road = 0

        for commuter in self.agents:
            if commuter.route == dynamic_road:
                agents_on_dynamic_road += 1
            elif commuter.route == static_road:
                agents_on_static_road += 1
            else:
                agents_on_middle_road += 1

        static_road_rate = SimEngine.gui_get('static')
        dynamic_road_rate = SimEngine.gui_get('dynamic')

        static_road_time = static_road_rate + (agents_on_middle_road + agents_on_static_road) / dynamic_road_rate
        middle_road_time = ((agents_on_dynamic_road + agents_on_middle_road) / dynamic_road_rate) \
                           + ((agents_on_static_road + agents_on_middle_road) / dynamic_road_rate)
        dynamic_road_time = (agents_on_dynamic_road / dynamic_road_rate) + static_road_rate

        if SimEngine.gui_get('middle_on'):
            roads_available = [(static_road, static_road_time/20),
                       (middle_road, middle_road_time/20),
                       (dynamic_road, dynamic_road_time/20)]
        else:
            roads_available = [(static_road, static_road_time/20), (dynamic_road, dynamic_road_time/20)]

        selection = min(roads_available, key=lambda x: x[1])

        return selection

    def random_route(self):
        if SimEngine.gui_get(middle_on) is True:
            return choice([middle_road, dynamic_road, static_road])
        else:
            return choice([dynamic_road, static_road])

    def emp_analytical(self):
        # check each route available, counting the number of commuters in each route
        # the commuter will take the path that with the least number of other commuters
        # Returns 0, 1, or 2
        tt = 0
        tb = 0
        tm = 0

        if tt == 0 or tb == 0 or tm == 0:
            return choice([middle_road, dynamic_road, static_road])
        for commuter in self.agents:
            if commuter.route == dynamic_road:
                tt += 1
            if commuter.route == static_road:
                tb += 1
            else:
                tm += 1
        if SimEngine.gui_get(middle_on) is True:
            t_score = ((tt + tm)/(tt + tb + tm)) * 1 + 1
            b_score = ((tb + tm)/(tt + tb + tm)) * 1 + 1
            m_score = (tm/(tt + tb + tm)) * 2
            if t_score < b_score and t_score < m_score:
                return dynamic_road
            if b_score < m_score and b_score < t_score:
                return static_road
            if t_score == b_score and t_score == m_score:
                return choice([middle_road, dynamic_road, static_road])
            else:
                return middle_road
        else:
            return choice([dynamic_road, static_road])
            t_score = tt / (tt + tb) * 1 + 1
            b_score = tb / (tt + tb) * 1 + 1
            if t_score < b_score:
                return dynamic_road
            else:
                return static_road

    def best_known_w_ran_dev(self):
        # Pick a route that has the best travel time with the gui's randomness chance to deviate to a longer route.
        # Returns 0, 1, or 2
        agents_on_dynamic_road = 0
        agents_on_static_road = 0
        agents_on_middle_road = 0
        static_road_rate = SimEngine.gui_get('static')
        dynamic_road_rate = SimEngine.gui_get('dynamic')
        static_road_time = static_road_rate + (agents_on_middle_road + agents_on_static_road) / dynamic_road_rate
        middle_road_time = ((agents_on_dynamic_road + agents_on_middle_road) / dynamic_road_rate) \
                           + ((agents_on_static_road + agents_on_middle_road) / dynamic_road_rate)
        dynamic_road_time = (agents_on_dynamic_road / dynamic_road_rate) + static_road_rate
        r = SimEngine.gui_get(randomness)
        if agents_on_dynamic_road == 0 or agents_on_static_road == 0 or agents_on_middle_road == 0:
            return choice([dynamic_road, static_road])

    def probabilistic_greedy(self):
        # Picks a route by the probability of how "good it is" (by travel time).
        # Returns 0, 1, or 2
        agents_on_dynamic_road = 0
        agents_on_static_road = 0
        agents_on_middle_road = 0
        static_road_rate = SimEngine.gui_get('static')
        dynamic_road_rate = SimEngine.gui_get('dynamic')
        static_road_time = static_road_rate + (agents_on_middle_road + agents_on_static_road) / dynamic_road_rate
        middle_road_time = ((agents_on_dynamic_road + agents_on_middle_road) / dynamic_road_rate) \
                           + ((agents_on_static_road + agents_on_middle_road) / dynamic_road_rate)
        dynamic_road_time = (agents_on_dynamic_road / dynamic_road_rate) + static_road_rate
        r = SimEngine.gui_get(randomness)
        if agents_on_dynamic_road == 0 or agents_on_static_road == 0 or agents_on_middle_road == 0:
            return choice([dynamic_road, static_road])

# GUI

import PySimpleGUI as sg

middle_on = 'Middle On?' # key is 'middle_on'
spawn_rate = 'Spawn Rate' # key is 'spawn_rate'
smoothing = 'Smoothing' # key is 'smoothing'
mode = 'Mode' # key is 'mode'
randomness = 'Randomness' # key is 'randomness'
static = 'Static Road Times'
dynamic = 'Dynamic Road Times'

ticks = 'Ticks:'

commuters = 'Total Commuters:'
commuters_static = 'On Static Route:'
commuters_dynamic = 'On Dynamic Route:'
commuters_middle = 'On Braess Route:'

braess_left_upper = [
    [sg.Checkbox('Middle On?', default=True, key='middle_on', enable_events=True)],

    [sg.Text(spawn_rate, pad=((0,0),(15,0))),
     sg.Slider(key='spawn_rate', range=(1, 50), resolution=1, default_value=10,
               orientation='horizontal', size=(10, 20))],

    [sg.Text(smoothing, pad=((0, 0), (20, 0))),
     sg.Slider(key='smoothing', range=(1, 10), resolution=1, default_value=1,
               orientation='horizontal', size=(10, 20))],

    [sg.Text(mode, pad=((0, 0), (20, 0))),
     sg.Combo([emp_analytical, best_known_w_ran_dev, probabilistic_greedy, random_route, selfish], key='mode',
              default_value=emp_analytical, size=(28,20), pad=((0, 0), (20, 0)))],

    [sg.Text(randomness, pad=((0, 0), (15, 0))),
     sg.Slider(key='randomness', range=(0,100), resolution=1, default_value=0,
               orientation='horizontal', size=(10, 20))],

    [sg.Text(static, pad=((0, 0), (15, 0))),
     sg.Slider(key='static', range=(0, 100), resolution=1, default_value=10,
               orientation='horizontal', size=(10, 20))],

    [sg.Text(dynamic, pad=((0, 0), (15, 0))),
     sg.Slider(key='dynamic', range=(1, 100), resolution=1, default_value=10,
               orientation='horizontal', size=(10, 20))]
]

braess_right_upper = [
    [sg.Text(ticks),
     sg.Text(0, key='ticks', size=(6,0))],

    [sg.Text(commuters),
     sg.Text(0, key='nbr_commuters', size=(4, 0)),
     sg.Text(commuters_dynamic),
     sg.Text(0, key='nbr_commuters_dynamic', size=(4, 0)),
     sg.Text(commuters_static),
     sg.Text(0, key='nbr_commuters_static', size=(4, 0)),
     sg.Text(commuters_middle),
     sg.Text(0, key='nbr_commuters_middle', size=(4, 0))]
]

if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Braess_World, "Braess' Road Paradox", gui_left_upper=braess_left_upper, gui_right_upper=braess_right_upper,
           agent_class=Commuter, auto_setup=False)
