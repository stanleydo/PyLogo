from __future__ import annotations

from core.agent import Agent
import core.gui as gui
from core.sim_engine import SimEngine
from core.utils import int_round
from core.world_patch_block import World

from functools import reduce

from random import choice
from random import random
from random import choices

from matplotlib.figure import Figure

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Minority_Game_Agent(Agent):

    def __init__(self, strategies, starting_patch):
        super().__init__()
        self.label = str(self.id)

        self.strategies = strategies
        self.guess = None
        self.init_agent(starting_patch)

    # noinspection PyAttributeOutsideInit
    def init_agent(self, starting_patch):
        """
        A continuation of __init__ also called from reset_agents(). Includes
        only what's needed to restart a race once one has already been run.
        """
        self.strategy_scores = [0] * len(self.strategies)
        # Could also use:          randint(0, len(self.strategies)-1)
        self.best_strategy_index = choice(range(len(self.strategies)))
        self.right = 0
        # Must do this because the system removes all agents from their patches when setup is called.
        # If this is called from reset_agents(), the agent's current_patch will not have it in its agents set.
        # Must add it so that move_to_patch() can remove it.
        if self not in self.current_patch().agents:
            self.current_patch().agents.add(self)
        self.move_to_patch(starting_patch)
        self.set_heading(90)

    def get_best_strategy_score(self):
        return self.strategy_scores[self.best_strategy_index]

    def make_selection(self, history_index):
        self.guess = self.strategies[self.best_strategy_index][history_index]
        return self.guess

    def update(self, history_as_index, winner):
        """
        Update this agent.
        """
        # Move winning agents forward one step.
        if self.guess == winner:
            self.right += 1
            self.forward(Minority_Game_World.one_step)

        self.update_strategy_scores(history_as_index, winner)

    def update_strategy_scores(self, history_as_index, winner):
        # Update the strategy scores and pick best strategy
        for strategy_id in range(len(self.strategies)):
            if self.strategies[strategy_id][history_as_index] == winner:
                self.strategy_scores[strategy_id] += 1
            # Pick the best strategy to use in the next round.
            if self.strategy_scores[strategy_id] > self.strategy_scores[self.best_strategy_index]:
                # noinspection PyAttributeOutsideInit
                self.best_strategy_index = strategy_id


class Minority_Game_Random_Agent(Minority_Game_Agent):

    def __init__(self, strategies, starting_patch):
        super().__init__(strategies, starting_patch)
        self.label += '-R'

    def get_best_strategy_score(self):
        return None

    def make_selection(self, _history_index):
        self.guess = choice([0, 1])
        return self.guess

    def update_strategy_scores(self, _history_as_index, _winner):
        # No strategies to update
        pass


class Minority_Game_Prev_Best_Strat_Agent(Minority_Game_Agent):
    """
    If there was a previous game, this agent uses its best strategy
    from that previous game throughout this game.
    If this is the first game, this agent does nothing special.
    """

    def __init__(self, strategies, starting_patch):
        super().__init__(strategies, starting_patch)
        self.label += '-PB'
        # Start off with a random strategy
        self.prev_game_best_strategy_index = choice(range(len(self.strategies)))

    def init_agent(self, starting_patch):
        """
        A continuation of __init__ called also from reset_agents(), i.e., for second and
        subsequent games. Includes what's needed to restart a race once one has already
        been run. This agent must save the best strategy from the previous game, if there
        was one, and use it throughout this game.
        """
        super().init_agent(starting_patch)
        ...

    def make_selection(self, history_index):
        """
        You fill in this part. Instead of using self.best_strategy_index
        use the final best_strategy_index from the previous game.
        """
        # History_index returns the index of the strategy.. (the 2^n number)
        # Guess is either 1 or 0, depending on the previous best strategy.
        self.guess = self.strategies[self.prev_game_best_strategy_index][history_index]
        return self.guess

    def update(self, history_as_index, winner):
        """
        Update this agent.
        """
        # Move winning agents forward one step.
        if self.guess == winner:
            self.right += 1
            self.forward(Minority_Game_World.one_step)

        self.update_strategy_scores(history_as_index, winner)

    # When updating strategy scores, we set the previous best game strategy as the strategy ID of the winner.
    # Here, we don't really care about scores. Just the last successful strategy.
    def update_strategy_scores(self, history_as_index, winner):
        # Update the strategy scores and pick best strategy
        for strategy_id in range(len(self.strategies)):
            if self.strategies[strategy_id][history_as_index] == winner:
                self.prev_game_best_strategy_index = strategy_id
                break


class Minority_Game_Spying_Agent(Minority_Game_Agent):
    """
    Before deciding on a selection, this agent spies on the other agents to see what they are going to do.
    """

    def __init__(self, strategies, starting_patch):
        super().__init__(strategies, starting_patch)
        self.label += '-Spy'
        # Cheaters will make a random choice to begin with
        self.guess = choice([0,1])

    def get_best_strategy_score(self):
        return None

    def make_selection(self, history_index):
        """
        You fill in this part.
        Find out what the other agents are going to do and do the opposite of the majority.
        """
        # noinspection PyUnusedLocal
        all_agents = World.agents

        # 2D list initialization, contains a list at 0th index and 1st index
        choices = [[],[]]

        for agent in all_agents:
            if agent.guess is not None:
                # Agents only guess 0 or 1, so add 1 to whatever index it is.
                choices[agent.guess].append(1)

        # Sum both indexes in choices
        choice_1 = sum(choices[0])
        choice_2 = sum(choices[1])

        # the final guess will be the minimum choice
        final_guess = 0 if min(choice_1, choice_2) == choice_1 else 1

        self.guess = final_guess
        return self.guess

    def update_strategy_scores(self, _history_as_index, _winner):
        # No strategies to update
        pass


class Minority_Game_World(World):

    # These values are used by the agents.
    # Make them easy to access by putting them at the Minority_Game_World class level.
    copy_agents = None

    nbr_agents = None
    one_step = None
    steps_to_win = None

    random_agent_ids = None

    # List to keep track of all best scores, worst scores, and average scores
    # Used for plotting 1-1 mapping with tick count
    list_of_best_scores = []
    list_of_worst_scores = []
    list_of_avg_scores = []
    tick_count = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.history_length = None
        self.history = []
        self.agent_vertical_separation = None

        # Sets up the graph
        # Gets the window object
        window = gui.WINDOW

        # Finds canvas element by key
        canvas_elem = window['canvas']
        canvas = canvas_elem.TKCanvas

        # Create matplotlib figure
        fig = Figure(figsize=(3,3))

        # Matplotlib magic
        self.ax = fig.add_subplot(111)
        self.ax.set_xlabel("Ticks")
        self.ax.set_ylabel("Wins")
        self.ax.set_title("Wins vs. Ticks")
        self.ax.grid()

        # Tkinter/Matplotlib Magic
        figure_canvas_agg = FigureCanvasTkAgg(fig, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack()
        self.fig_agg = figure_canvas_agg

    @staticmethod
    def generate_a_strategy(strategy_length):
        strategy = tuple(choice((0, 1)) for _ in range(strategy_length))
        return strategy

    def generate_all_strategies(self):
        # Generate enough strategies for all agents.
        strategy_length = 2 ** self.history_length
        strategies_per_agent = SimEngine.gui_get(STRATEGIES_PER_AGENT)
        strategies = set()
        # Why a while loop rather than a for loop?
        # Why is strategies a set rather than a list?
        # Note strategies is made into a list after the loop.
        while len(strategies) < Minority_Game_World.nbr_agents * strategies_per_agent:
            strategies.add(self.generate_a_strategy(strategy_length))
        strategies = list(strategies)
        return (strategies, strategies_per_agent)
    
    def generate_the_agents(self):
        (strategies, strategies_per_agent) = self.generate_all_strategies()
        self.agent_vertical_separation = gui.PATCH_ROWS / Minority_Game_World.nbr_agents
        for agent_id in range(Minority_Game_World.nbr_agents):
            starting_patch = self.get_starting_patch(agent_id, self.agent_vertical_separation)
            strategies_for_this_agent = strategies[strategies_per_agent*agent_id:strategies_per_agent*(agent_id + 1)]

            # PB = previous best
            # CH = Cheater
            pb_density = SimEngine.get_gui_value(PB_DENSITY) / 100
            ch_density = SimEngine.get_gui_value(CH_DENSITY) / 100

            # Handles balance between cheater density, previous best density, and normal agent density
            if pb_density == 0 and ch_density != 0:
                agent_density = 1 - (ch_density)
            elif ch_density == 0 and pb_density != 0:
                agent_density = 1 - (pb_density)
            else:
                agent_density = 1 - (pb_density + ch_density) / 2

            # Which agent class (or subclass) is this agent?
            # Moved this down a couple of lines
            # agent_class = Minority_Game_Random_Agent if agent_id in Minority_Game_World.random_agent_ids else \
            #               Minority_Game_Agent

            # Choices returns a list of choices (in this case, k=1) based off of weights
            # I like to look at the weights as a probability, so the density determined above will usually determine the 'weight' of the corresponding agent
            agent_class = choices(population=[Minority_Game_Prev_Best_Strat_Agent, Minority_Game_Spying_Agent, Minority_Game_Agent], weights = [pb_density, ch_density, agent_density])[0]

            # Random Agents take priority, otherwise it's what it is before.
            agent_class = Minority_Game_Random_Agent if agent_id in Minority_Game_World.random_agent_ids else \
                          agent_class

            # Create the agent
            agent_class(strategies_for_this_agent, starting_patch)

    # Creates agents that are all the same (same exact strategies),
    # with the exception of some Previous Best Strategy agents (if specified by the gui slider)
    def generate_the_same_agents(self):
        strategy_length = 2 ** self.history_length
        # Spaces out the agents
        self.agent_vertical_separation = gui.PATCH_ROWS / Minority_Game_World.nbr_agents
        strategies_per_agent = SimEngine.get_gui_value(STRATEGIES_PER_AGENT)

        # Use a set to handle any duplicate strategies
        # The set size won't increase if a duplicate strategy is added
        strategies = set()

        # Once we have a 'strategies_per_agent' amount of unique strategies, we can stop the loop
        # This is because these amount of strategies will be used for every agent.
        while len(strategies) < strategies_per_agent:
            # generate_a_strategy() generates a size 'strategy length' string of 0s and 1s
            strategies.add(self.generate_a_strategy(strategy_length))

        # convert the set into a list
        strategies = list(strategies)
        agent_density = SimEngine.get_gui_value(PB_DENSITY)/100
        # Loop through all of the agents
        for agent_id in range(Minority_Game_World.nbr_agents):
            starting_patch = self.get_starting_patch(agent_id, self.agent_vertical_separation)
            # Pick an agent class based off of agent_density
            agent_class = Minority_Game_Agent if random() > agent_density else Minority_Game_Prev_Best_Strat_Agent
            agent_class(strategies, starting_patch)

    def get_starting_patch(self, agent_id, agent_separation):
        starting_patch = self.patches_array[round((agent_id) * agent_separation), 0]
        return starting_patch

    def history_to_index(self):
        # The final argument (0) is optional.
        val = reduce(lambda so_far, next: so_far*2 + next, self.history, 0)
        return val

    @staticmethod
    def max_agent_right():
        return max(agent.right for agent in World.agents)

    # Returns the farthest agent on the left (min amount of spaces to the right)
    @staticmethod
    def min_agent_right():
        return min(agent.right for agent in World.agents)

    @staticmethod
    def avg_agents():
        return sum(agent.right for agent in World.agents)/len(World.agents)

    def print_final_scores(self):
        print('\n\t       % right '
              '\n\t  -----------------'
              '\n\t  agent  best strat'
              )
        for agent in sorted(World.agents, key=lambda agent: agent.id):
            best_strategy_score = agent.get_best_strategy_score()
            print(f'{agent.id:2}.\t  {int_round(100 * agent.right / self.ticks):3}'
                  f'       {"--" if not best_strategy_score else int_round(100 * best_strategy_score / self.ticks)}'
                  )

    def print_step_info(self, history_as_index, winner):
        leading_agent_right = self.max_agent_right()
        leading_agent_strings = [f'{agent.id}: {agent.right}/{Minority_Game_World.steps_to_win}'
                                 for agent in World.agents if agent.right == leading_agent_right]
        leading_agents = '{' + ", ".join(leading_agent_strings) + '}'
        print(f'{self.ticks}. {self.history}, {history_as_index:2}, {winner}, {leading_agents}')

    def reset_agents(self):
        print('\n\nStarting next race with same agents, same strategies, and a new random history.\n')
        self.history = [choice((0, 1)) for _ in range(self.history_length)]
        World.agents = Minority_Game_World.copy_agents
        for agent in World.agents:
            starting_patch = self.get_starting_patch(agent.id, self.agent_vertical_separation)
            agent.init_agent(starting_patch)
        World.done = False

    def setup(self):
        Agent.id = 0
        Minority_Game_World.steps_to_win = SimEngine.gui_get(STEPS_TO_WIN)
        # Adjust how far one step is based on number of steps needed to win
        Minority_Game_World.one_step = (gui.PATCH_COLS - 2) * gui.BLOCK_SPACING() / Minority_Game_World.steps_to_win
        # For longer/shorter races, speed up/slow down frames/second
        gui.set_fps(round(6*Minority_Game_World.steps_to_win/50))

        # self.done will be True if this a repeat game with the same agents.
        if self.done:
            self.reset_agents()
            self.clear_graph()
            return

        # This is the normal setup.
        Minority_Game_World.nbr_agents = SimEngine.gui_get(NBR_AGENTS)
        if Minority_Game_World.nbr_agents % 2 == 0:
            Minority_Game_World.nbr_agents += (1 if Minority_Game_World.nbr_agents < gui.WINDOW[NBR_AGENTS].Range[1]
                                               else (-1))
            # gui.WINDOW[NBR_AGENTS].update(value=Minority_Game_World.nbr_agents)
            SimEngine.gui_set(NBR_AGENTS, value=Minority_Game_World.nbr_agents)
        Minority_Game_World.random_agent_ids = {0, Minority_Game_World.nbr_agents - 1}

        # Generate a random initial history
        self.history_length = SimEngine.gui_get(HISTORY_LENGTH)
        self.history = [choice([0, 1]) for _ in range(self.history_length)]

        # Determines which generate_agents() to use based off of the checkbox 'STRATS_ALL_SAME'
        if SimEngine.get_gui_value(STRATS_ALL_SAME):
            self.generate_the_same_agents()
        else:
            self.generate_the_agents()

        # Clears the current graph for use in the next race
        self.clear_graph()

    # Like NetLogo, PyLogo is a framework: "Don't call us, we'll call you."
    def step(self):
        history_as_index = self.history_to_index()
        one_votes = sum(agent.make_selection(history_as_index) for agent in World.agents)
        winner = 0 if one_votes > Minority_Game_World.nbr_agents/2 else 1
        avg = 0
        for agent in World.agents:
            agent.update(history_as_index, winner)


        self.print_step_info(history_as_index, winner)
        self.history = self.history[1:] + [winner]

        if self.max_agent_right() >= Minority_Game_World.steps_to_win:
            World.done = True
            # Keep the agents so that we can use them in the next game, if there is one.
            Minority_Game_World.copy_agents = World.agents
            self.print_final_scores()

        # Every step will append the max, min, and avg of the agents to lists
        # This is used to create a plot
        self.list_of_best_scores.append(self.max_agent_right())
        self.list_of_worst_scores.append(self.min_agent_right())
        self.list_of_avg_scores.append(self.avg_agents())
        self.tick_count.append(self.ticks)
        # The plot is then updated every tick to give it an animated feel.
        self.update_graph()

    def update_graph(self):
        self.ax.cla()  # clear the subplot
        self.ax.grid()  # draw the grid

        # ax.plot(list of x, list of y, color, etc.) plots at a 1-1 mapping. This means that x and y have to be the same size
        self.ax.plot(self.tick_count, self.list_of_best_scores, color='red')
        self.ax.plot(self.tick_count, self.list_of_avg_scores, color='green')
        self.ax.plot(self.tick_count, self.list_of_worst_scores, color='blue')

        # When the graph is cleared, for some reason the labels dissapear, so we re-write them
        self.ax.set_xlabel("Ticks")
        self.ax.set_ylabel("Wins")
        self.ax.set_title("Wins vs. Ticks")
        self.fig_agg.draw()

    def clear_graph(self):
        # Clears the graph & resets all lists of scores
        self.list_of_best_scores = []
        self.list_of_worst_scores = []
        self.list_of_avg_scores = []
        self.tick_count = []
        self.ax.cla()  # clear the subplot
        # Labels dissapear, so we have to re-write them
        self.ax.set_xlabel("Ticks")
        self.ax.set_ylabel("Wins")
        self.ax.set_title("Wins vs. Ticks")
        self.ax.grid()  # draw the grid
        self.fig_agg.draw()


# ############################################## Define GUI ############################################## #
# GUI string constants
HISTORY_LENGTH = 'History length'
NBR_AGENTS = 'Number of agents'
STEPS_TO_WIN = 'Steps to win'
STRATEGIES_PER_AGENT = 'Strategies per agent'
STRATS_ALL_SAME = 'Strategies all the same'
PB_DENSITY = 'Previous best density'
CH_DENSITY = 'Cheater density'
GRAPH = 'Graph'
MAX = 'Max'
AVG = 'Average'
MIN = 'Min'

import PySimpleGUI as sg

gui_left_upper = [[sg.Text(HISTORY_LENGTH, tooltip='The length of the history record'),
                   sg.Slider(key=HISTORY_LENGTH, range=(0, 8), default_value=5,
                             size=(10, 20), orientation='horizontal',
                             tooltip='The length of the history record')],

                  [sg.Text(NBR_AGENTS,
                           tooltip='The number of agents. \n(Must be an odd number.\nChecked during setup.)'),
                   sg.Slider(key=NBR_AGENTS, range=(1, 35), default_value=25,
                             size=(10, 20), orientation='horizontal',
                             tooltip='The number of agents. \n(Must be an odd number.\nChecked during setup.)')],

                  [sg.Text(STRATEGIES_PER_AGENT, tooltip='The number of strategies generated for each agent'),
                   sg.Slider(key=STRATEGIES_PER_AGENT, range=(1, 200), default_value=100,
                             size=(10, 20), orientation='horizontal',
                             tooltip='The number of strategies generated for each agent')],

                  [sg.Text(STEPS_TO_WIN, tooltip='The number of steps required to win'),
                   sg.Slider(key=STEPS_TO_WIN, range=(1, 500), default_value=50, resolution=25,
                             size=(10, 20), orientation='horizontal',
                             tooltip='The number of steps required to win')],

                  [sg.Checkbox(STRATS_ALL_SAME, key=STRATS_ALL_SAME, tooltip='Each Agent has the same set of strategies', size=(20,1))],

                  [sg.Text(PB_DENSITY, tooltip='Density of agents using the previous best strategy'),
                   sg.Slider(key=PB_DENSITY, range=(0, 100), default_value=48, resolution=1,
                            size=(10, 20), orientation='horizontal',
                            tooltip='Density of agents using the previous best strategy')],

                  [sg.Text(CH_DENSITY, tooltip='Density of spying(cheating) agents'),
                   sg.Slider(key=CH_DENSITY, range=(0, 100), default_value=48, resolution=1,
                             size=(10, 20), orientation='horizontal',
                             tooltip='Density of spying(cheating) agents')],

                  [sg.Canvas(size=(10, 10), background_color='red'), sg.Text(MAX),
                   sg.Canvas(size=(10, 10), background_color='green'), sg.Text(AVG),
                   sg.Canvas(size=(10, 10), background_color='blue'), sg.Text(MIN)],

                  [sg.Canvas(size=(20, 20), key='canvas')],
                  ]


if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(Minority_Game_World, 'Minority game', gui_left_upper, agent_class=Minority_Game_Agent, fps=6)
