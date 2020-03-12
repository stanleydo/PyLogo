from __future__ import annotations

from core.agent import Agent
from core.gui import HOR_SEP, KNOWN_FIGURES
from core.sim_engine import SimEngine
from core.utils import normalize_dxdy
from core.world_patch_block import World
from core.link import Link, link_exists
from core.pairs import center_pixel, Pixel_xy, Velocity
from core.gui import BLOCK_SPACING, HOR_SEP, KNOWN_FIGURES, SCREEN_PIXEL_HEIGHT, SCREEN_PIXEL_WIDTH

from math import sqrt

import random

# NW_Node is a subclass of Agent
class NW_Node(Agent):

    def __init__(self, **kwargs):
        # Define a shape, which can be found in gui.KNOWN_FIGURES.
        # Some other examples are "netlogo_figure" (default), "square", and "star".
        shape_name = SimEngine.gui_get('shape')

        # Initialize the super class to take advantage of methods and variables
        super().__init__(shape_name=shape_name, **kwargs)

        # Moves the agent in a random direction a random int (x,y) many pixels
        self.forward(random.randint(10, 300))

        self.linked_once = False

        self.nbr_links = 0

    def make_preferential_links(self, directed, agents_not_yet_linked):
        # All the nodes that have yet to get a link, minus this agent
        # The agent theoretically should have been just created when this method is called.
        possible_nodes = set(agents_not_yet_linked) - {self}

        # How many links exist in the world?
        # This number can not be <= 0, since we divide by it when finding probability.
        total_links = len(World.links) if World.links else 1

        # Create two lists, one for Agents, and the second list with the corresponding Number of links
        partners = []
        partners_probability = []

        # Update the number of links per agent
        # Append the agent to the list of partners
        # Append the number of links for that agent to partners_nbr_links
        for agent in possible_nodes:
            agent.update_nbr_links()
            partners.append(agent)
            # We divide number of links by total links to get a probability.
            partners_probability.append(agent.nbr_links/total_links)

        # Random.choices with k = 1 will pick 1 element from the population using the probability as our weight.
        # Population and weights must be the same size, and there is a 1-1 mapping between both.
        # This means population[0] will use weights[0] as the probability.
        # This will return a list of k elements, which is why we have to get the index at 0.
        preferred_agent = random.choices(population=partners, weights=partners_probability, k=1)[0]

        # Create a link with the preferred agent
        Link(self, preferred_agent, directed)
        # Once this agent has found a link, it should not be selected as a possible node
        # the next time preferential attachment is called in NW_World
        self.linked_once = True

    # Updates the agent's total number of links.
    def update_nbr_links(self):
        self.nbr_links = sum([1 if link.includes(self) else 0 for link in World.links])

    # TODO -- The first agent should link to the next agent, and the last agent should be linked to the first.
    # Matthew - Work on this here.
    def make_ring_links(self, directed, agents_not_yet_linked, next_agent_position):
        # if self is not the last element of agents_not_yet_linked
        # then it links self with the next element in agents_not_yet_linked
        if next_agent_position < len(agents_not_yet_linked):
            Link(self, agents_not_yet_linked[next_agent_position], directed)
        # if self is the last element of agents_not_yet_linked
        # then it links self with the first element in agents_not_yet_linked
        else:
            Link(self, agents_not_yet_linked[0], directed)
        self.linked_once = True

    # TODO -- All agents should only be linked to the first.
    # Wilson - Work on this here.
    def make_star_links(self, directed, agents_not_yet_linked):
        # create links with the first element of agents_not_yet_linked being the star node
        if self != agents_not_yet_linked[0]:
            Link(self, agents_not_yet_linked[0], directed)
        self.linked_once = True

    def make_small_world_links(self, directed, agents_not_yet_linked, agent_position, nb_size, rewire_prob):
        # every agent is linked to the next [nb_size] agents in agents_not_yet_linked
        for i in range(agent_position + 1, agent_position + nb_size + 1):
            # if i < the length of agents_not_yet_linked, then self can link to the agent at i
            if i < len(agents_not_yet_linked):
                Link(self, agents_not_yet_linked[i], directed)
            # if i > the length of agents_not_yet_linked,
            # then it wraps around to the beginning of agents_not_yet_linked
            else:
                Link(self, agents_not_yet_linked[i - len(agents_not_yet_linked)], directed)

        self.linked_once = True

    # TODO -- Implementation of Spring Layout for Force-Directed-Graphing
    def apply_forces(self):
        pass

    def adjust_distances(self, velocity_adjustment):
        dist_unit = 8
        screen_distance_unit = sqrt(SCREEN_PIXEL_WIDTH()**2 + SCREEN_PIXEL_HEIGHT()**2)/dist_unit

        repulsive_force: Velocity = Velocity((0, 0))

        for agent in (World.agents - {self}):
            repulsive_force += self.force_as_dxdy(self.center_pixel, agent.center_pixel, screen_distance_unit,
                                                    repulsive=True)

        # Also consider repulsive force from walls.
        repulsive_wall_force: Velocity = Velocity((0, 0))

        horizontal_walls = [Pixel_xy((0, 0)), Pixel_xy((SCREEN_PIXEL_WIDTH(), 0))]
        x_pixel = Pixel_xy((self.center_pixel.x, 0))
        for h_wall_pixel in horizontal_walls:
            repulsive_wall_force += self.force_as_dxdy(x_pixel, h_wall_pixel, screen_distance_unit, repulsive=True)

        vertical_walls = [Pixel_xy((0, 0)), Pixel_xy((0, SCREEN_PIXEL_HEIGHT()))]
        y_pixel = Pixel_xy((0, self.center_pixel.y))
        for v_wall_pixel in vertical_walls:
            repulsive_wall_force += self.force_as_dxdy(y_pixel, v_wall_pixel, screen_distance_unit, repulsive=True)

        attractive_force: Velocity = Velocity((0, 0))
        for agent in (World.agents - {self}):
            if link_exists(self, agent):
                attractive_force += self.force_as_dxdy(self.center_pixel, agent.center_pixel, screen_distance_unit,
                                                         repulsive=False)

        net_force = repulsive_force + repulsive_wall_force + attractive_force
        normalized_force: Velocity = net_force/max([net_force.x, net_force.y, velocity_adjustment])
        normalized_force *= 10

        if SimEngine.gui_get('Print force values'):
            print(f'{self}. \n'
                  f'rep-force {tuple(repulsive_force.round(2))}; \n'
                  f'rep-wall-force {tuple(repulsive_wall_force.round(2))}; \n'
                  f'att-force {tuple(attractive_force.round(2))}; \n'
                  f'net-force {tuple(net_force.round(2))}; \n'
                  f'normalized_force {tuple(normalized_force.round(2))}; \n\n'
                  )

        self.set_velocity(normalized_force)
        self.forward()

    @staticmethod
    def force_as_dxdy(pixel_a: Pixel_xy, pixel_b: Pixel_xy, screen_distance_unit, repulsive):
        """
        Compute the force between pixel_a pixel and pixel_b and return it as a velocity: direction * force.
        """
        direction: Velocity = normalize_dxdy((pixel_a - pixel_b) if repulsive else (pixel_b - pixel_a))
        d = pixel_a.distance_to(pixel_b, wrap=False)
        if repulsive:
            dist = max(1, pixel_a.distance_to(pixel_b, wrap=False) / screen_distance_unit)
            rep_coefficient = 1
            rep_exponent = -2
            force = direction * (10 ** rep_coefficient) / 10 * dist ** rep_exponent
            return force
        else:  # attraction
            dist = max(1, max(d, screen_distance_unit) / screen_distance_unit)
            att_exponent = 2
            force = direction * dist ** att_exponent
            # If the link is too short, push away instead of attracting.
            if d < screen_distance_unit:
                force = force * (-1)
            att_coefficient = 1
            return 10 ** (att_coefficient - 1) * force

class NW_World(World):

    def __init__(self, patch_class, agent_class):
        super().__init__(patch_class, agent_class)

        self.velocity_adjustment = 1

        # True means the next generation of nodes will have directed links.
        self.directed_link: bool = None

        # Layout defines the way the agents move and react to one another
        # We only need to worry about Spring right now.
        self.layout: str = None

        # If this is True, we want to re-set the board before we generate anything else.
        self.clear_before_gen: bool = None

        # Number of nodes we want to generate
        self.nb_nodes: int = None

        # Small World Neighborhood-size and rewire probability
        self.nb_size: int = None
        self.rewire_probability: int = None

        # Updates the world's values with defaults
        self.update()

        # Dictionary that maps event keys to functions
        self.events_and_functions = {'PreAtt': self.preferential_attachment,
                                     'Ring': self.ring,
                                     'Star': self.star,
                                     'SmallWorld': self.small_world,
                                     'Lattice2D': self.lattice_2D}

    # Updates all of the values in self from their respective gui elements.
    def update(self):
        self.directed_link = bool(int(SimEngine.gui_get(key='directed_link')))
        self.layout = SimEngine.gui_get(key='Layout')
        self.clear_before_gen = bool(int(SimEngine.gui_get(key='clear')))
        self.nb_nodes = SimEngine.gui_get(key='nb-nodes')
        self.nb_size = SimEngine.gui_get('nb-size')
        self.rewire_probability = SimEngine.gui_get('rewire-prob')

    def check_to_clear(self):
        if self.clear_before_gen:
            self.clear_all()

    def generate_num_agents(self):
        for _ in range(self.nb_nodes):
            # Creates agents and puts them in the World
            self.agent_class()

    # Generates the number of agents specified and puts them in the world
    # Returns a list of agents that have yet to undergo a link process (Pref Att, Ring, Star .. etc.)
    def generate_and_get_new_agents(self):
        # Creates nodes based off the number of nodes and places them randomly on the grid
        # Randomly.. meaning a random direction and number of pixels from the center.
        self.generate_num_agents()

        # Since we don't want to touch any of the existing agents, we have to filter them out.
        agents_not_yet_linked = [agent for agent in World.agents if not agent.linked_once]

        return agents_not_yet_linked

    def preferential_attachment(self):
        agents_not_yet_linked = self.generate_and_get_new_agents()

        # Make a preferential link for all the agents that we've just created.
        for agent in agents_not_yet_linked:
            agent.make_preferential_links(self.directed_link, agents_not_yet_linked)

    def ring(self):
        agents_not_yet_linked = self.generate_and_get_new_agents()

        # Make ring links for all the agents that we've just created.
        next_agent_position = 1;
        for agent in agents_not_yet_linked:
            agent.make_ring_links(self.directed_link, agents_not_yet_linked, next_agent_position)
            next_agent_position += 1

    def star(self):
        agents_not_yet_linked = self.generate_and_get_new_agents()

        # Make star links for all the agents that we've just created.
        for agent in agents_not_yet_linked:
            agent.make_star_links(self.directed_link, agents_not_yet_linked)


    # TODO -- Small World implementation
    # Watts and Strogatz's Model
    # Start off with a regular network of N nodes and M neighbors per node (Need to have same pattern of connectivity)
    # Use Beta (probability) * M links (neighbors)
    # Rewire one end of the chosen links to another randomly chosen node
    def small_world(self):

        # Check if the Neighborhood size is less that half of the number of agents
        if self.nb_nodes / 2 > self.nb_size:
            agents_not_yet_linked = self.generate_and_get_new_agents()
            # Make small world links for all the agents that we've just created.
            agent_position = 0
            for agent in agents_not_yet_linked:
                agent.make_small_world_links(self.directed_link, agents_not_yet_linked, agent_position, self.nb_size,
                                             self.rewire_probability)
                agent_position += 1
        else:
            print("Neighborhood size must be less that half of nb-nodes")


    def small_world_rewire(self, agents_not_yet_linked):
        pass


    # TODO -- Lattice 2D implementation
    def lattice_2D(self):

        ...

    def handle_event(self, event):
        super().handle_event(event)

        # TODO -- Handle events for Small World and Lattice2D.
        # Update values whenever an event occurs, before we perform any other actions.
        if event:
            self.update()

        if event in self.events_and_functions:
            self.check_to_clear()
            self.events_and_functions[event]()


    def setup(self):

        # This method should clear the board and update its values from the GUI.
        # Not sure what else it should do really.
        self.clear_all()
        self.update()

    def step(self):
        for node in self.agents:
            node.adjust_distances(self.velocity_adjustment)

        # Set all the links back to normal.
        for lnk in World.links:
            lnk.color = lnk.default_color
            lnk.width = 1

        # self.selected_nodes = [node for node in self.agents if node.selected]
        # # If there are exactly two selected nodes, find the shortest path between them.
        # if len(self.selected_nodes) == 2:
        #     self.shortest_path_links = self.shortest_path()
        #     # self.shortest_path_links will be either a list of links or None
        #     # If there is a path, highlight it.
        #     if self.shortest_path_links:
        #         for lnk in self.shortest_path_links:
        #             lnk.color = Color('red')
        #             lnk.width = 2




import PySimpleGUI as sg

# TODO -- Put the strings at the top?
nw_left_upper =[
    # [sg.Button('Setup', key='Setup'), sg.Button('Go', key='Go'), sg.Button('Go Once', key='Step')],

    [sg.Text('Layout'),
     sg.Combo(values=['Spring', 'Circle', 'Radial', 'Tutte'], key='Layout', default_value='Spring'),
     sg.Text('Shapes:'),
     sg.Combo(KNOWN_FIGURES, key='shape', default_value='circle',
              tooltip='Node shape')
     ],
    [sg.CB('Directed Link?', enable_events=True, key='directed_link', default=False)],
    [sg.CB('Clear Before Generating?', enable_events=True, default=True, size=(20, 1), key='clear')],

    HOR_SEP(30, pad=(None, None)),

    [sg.Text('nb-nodes'),
     sg.Slider(key='nb-nodes', range=(0, 100), default_value=15, orientation='horizontal')],

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




