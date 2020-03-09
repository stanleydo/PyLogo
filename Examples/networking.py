from __future__ import annotations

from core.agent import Agent
from core.gui import HOR_SEP, KNOWN_FIGURES
from core.sim_engine import SimEngine
from random import uniform
from core.world_patch_block import World
from core.link import Link, link_exists

import random

# NW_Node is a subclass of Agent
class NW_Node(Agent):

    def __init__(self, **kwargs):
        # Define a shape name. Usable shapes are found gui.SHAPES.
        # Some other examples are "netlogo_figure" (default), "square", and "star".
        # TODO -- Add a GUI Element for selecting SHAPES, similar to "Force_and_effects.py"
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
    def make_ring_links(self, directed, agents_not_yet_linked):
        pass

    # TODO -- All agents should only be linked to the first.
    # Wilson - Work on this here.
    def make_star_links(self, directed, agents_not_yet_linked):
        pass

    # TODO -- Implementation of Spring Layout for Force-Directed-Graphing
    def apply_forces(self):
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

    def check_to_clear(self):
        if self.clear_before_gen:
            self.clear_all()

    def generate_num_agents(self):
        for _ in range(self.nb_nodes):
            # Creates agents and puts them in the World
            self.agent_class()

    # Pref. Attachment, Ring, and Star will later be broken down into smaller parts.
    # This is because they each use 80% of the same code.

    def preferential_attachment(self):

        # Clears the grid if the option is checked.
        self.check_to_clear()

        # Creates nodes based off the number of nodes and places them randomly on the grid
        # Randomly.. meaning a random direction and number of pixels from the center.
        self.generate_num_agents()

        # Since we don't want to touch any of the existing agents, we have to filter them out.
        agents_not_yet_linked = [agent for agent in World.agents if not agent.linked_once]

        # Make a preferential link for all the agents that we've just created.
        for agent in agents_not_yet_linked:
            agent.make_preferential_links(self.directed_link, agents_not_yet_linked)

    def ring(self):

        # Clears the grid if the option is checked.
        self.check_to_clear()

        # Creates nodes based off the number of nodes and places them randomly on the grid
        # Randomly.. meaning a random direction and number of pixels from the center.
        self.generate_num_agents()

        # Since we don't want to touch any of the existing agents, we have to filter them out.
        agents_not_yet_linked = [agent for agent in World.agents if not agent.linked_once]

        for agent in agents_not_yet_linked:
            agent.make_ring_links(self.directed_link, agents_not_yet_linked)

    def star(self):

        # Clears the grid if the option is checked.
        self.check_to_clear()

        # Creates nodes based off the number of nodes and places them randomly on the grid
        # Randomly.. meaning a random direction and number of pixels from the center.
        self.generate_num_agents()

        # Since we don't want to touch any of the existing agents, we have to filter them out.
        agents_not_yet_linked = [agent for agent in World.agents if not agent.linked_once]

        for agent in agents_not_yet_linked:
            agent.make_star_links(self.directed_link, agents_not_yet_linked)

    def small_world(self):
        ...

    def lattice_2D(self):
        ...

    def handle_event(self, event):
        super().handle_event(event)

        # TODO -- Handle events for Small World and Lattice2D.
        # Update values whenever an event occurs, before we perform any other actions.
        if event:
            self.update()

        if event in 'PreAtt':
            self.preferential_attachment()
        elif event in 'Ring':
            self.ring()
        elif event in 'Star':
            self.star()

    def setup(self):

        # This method should clear the board and update its values from the GUI.
        # Not sure what else it should do really.
        self.clear_all()
        self.update()

    def step(self):
        # This method should move the agents to fit the layout
        pass



import PySimpleGUI as sg

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




