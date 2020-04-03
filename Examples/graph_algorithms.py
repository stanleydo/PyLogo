# Import the string constants you need (mainly keys) as well as classes and gui elements
from core.graph_framework import (CLUSTER_COEFF, Graph_Node, Graph_World, PATH_LENGTH, graph_left_upper,
                                  graph_right_upper, LINK_PROB)
from core.pairs import center_pixel
from core.sim_engine import SimEngine
from core.link import Link
from random import choices, random, choice, sample
import math
import sys

# Import strings from graph_framework
from core.graph_framework import PREF_ATTACHMENT, RANDOM, RING, SMALL_WORLD, WHEEL, STAR


class Graph_Algorithms_World(Graph_World):

    # noinspection PyMethodMayBeStatic
    # Matthew's implementation of average_path_length
    def average_path_length(self):
        # a list of all the links in the world
        all_links = self.links
        # place holder variable for the summation of the lengths of all the links
        total = 0
        # adds the lengths of all the links together
        for link in all_links:
            total += link.agent_1.distance_to(link.agent_2)
        # if there's at least one link, return the average length by dividing the summation of link lengths
        # by the amount of links
        # if there are no links return 0.0 to prevent a divide by 0 error
        if len(all_links) > 0:
            return total / len(all_links)
        else:
            return 0.0

    # def average_path_length(self):
    #     all_paths = self.all_pairs_shortest_path()
    #     nbr_links = len(Graph_World.links)
    #     nbr_agents = len(Graph_World.agents)
    #     avg_shortest_path = 0.0
    #
    #     for col in range(nbr_agents):
    #         avg_path = 0.0
    #         non_paths = 0
    #         for row in all_paths:
    #             if row[col] != 0 and row[col] != 99999.0:
    #                 avg_path += row[col]
    #             else:
    #                 non_paths += 1
    #
    #         avg_path = avg_path / nbr_agents-1-non_paths
    #         avg_shortest_path += avg_path
    #
    #     return avg_shortest_path/nbr_agents


    # Wilson & Stanley's implementation of Clustering-Coefficent
    def clustering_coefficient(self):
        """
        v = a node
        kv = degree(number of nodes connected to v)
        Nv: number of links between neighbors of v
        cc = (2 * Nv) / (kv(kv-1))
        """
        all_nodes = list(Graph_World.agents)

        # Top level Clustering Coefficient
        cc_main = 0.0

        # Loop through all of the nodes
        for v in all_nodes:

            # Find the degree of the node (kv), as well as a list of agents that are linked to v
            kv, linked_nodes = self.find_linked_nodes(v)

            # Check if there are actually any connected nodes to v before we do anything
            if kv >= 2:
                # Initialize nv (number of links between neighbors of v)
                nv = 0.0
                # We will use a while loop to pop off agents from linked_nodes
                # This will allow us to search all nodes without adding
                # the additional links from nv
                while linked_nodes:
                    neighbor_node = linked_nodes.pop(0)
                    # Find the number of links that each neighbor has (Where the other agent is in Linked_nodes)
                    # The 0th index is the nbr_links from (nbr_links, list_of_neighbors)
                    # See self.find_linked_nodes() below
                    nbr_links_neighbors = self.find_linked_nodes(neighbor_node, linked_nodes)[0]
                    # Add the number of links between neighbors to nv
                    nv += nbr_links_neighbors
                # Compute cc(v) and add it to cc_main so we can average it later.
                cc_sub_v = (2.0 * nv) / (kv * (kv - 1.0))
                cc_main += cc_sub_v

        # Average cc_main to find the clustering_coefficient of the whole graph
        return cc_main / len(all_nodes)

    @staticmethod
    # Finds the number of nodes linked as well as the agents linked to a specific node.
    # The arrow "-> tuple" is a way to statically type functions in python
    # This just means this method is supposed to return a tuple object.
    def find_linked_nodes(node, agents_to_match=[]) -> tuple:
        # Initialize a number of links and empty list of linked nodes
        num_links = 0
        linked_nodes = []

        # Iterate through the links in the world
        for link in Graph_World.links:
            # Check if a link includes the node we want to check links for
            if link.includes(node):
                # Find the agent in the link that isn't the node we want to check links for
                agent = link.agent_1 if link.agent_1 != node else link.agent_2

                # This will to see if the agent matches an agent in the list
                # If agents_to_match == [], Python will evaluate an empty list as False
                if agents_to_match:
                    if agent in agents_to_match:
                        linked_nodes.append(agent)
                        num_links += 1
                else:
                    # Update number of links and add this agent to the list of linked nodes
                    linked_nodes.append(agent)
                    num_links += 1

        # Returns a tuple of (number of links, linked_node) for the corresponding node
        # Or False if there are no links.
        return num_links, linked_nodes

    def compute_metrics(self):
        cluster_coefficient = self.clustering_coefficient()
        SimEngine.gui_set(CLUSTER_COEFF, value=cluster_coefficient)
        avg_path_length = self.average_path_length()
        SimEngine.gui_set(PATH_LENGTH, value=avg_path_length)

        # self.print_floyds_algorithm()

    def print_floyds_algorithm(self):
        print()
        ag_count = 0
        distances = self.all_pairs_shortest_path()
        for row in distances:
            print("Agent", ag_count, "shortest path lengths:", row)
            ag_count += 1

    # Stanley's implementation of Floyd-Warshall algorithm
    def all_pairs_shortest_path(self):

        inf_value = 99999.0

        # Number of vertices in the graph
        v = len(Graph_World.agents)

        # Initializing a 2D list of -1s
        distances = []
        for _ in range(v):
            distances.append([inf_value for _ in range(v)])

        for agent in Graph_World.agents:
            distances[agent.id][agent.id] = 0.0

        for link in Graph_World.links:
            distances[link.agent_1.id][link.agent_2.id] = link.agent_1.distance_to(link.agent_2)
            distances[link.agent_2.id][link.agent_1.id] = link.agent_2.distance_to(link.agent_1)

        for k in range(0, v):
            for i in range(0, v):
                for j in range(0, v):
                    if distances[i][j] > distances[i][k] + distances[k][j]:
                        distances[i][j] = distances[i][k] + distances[k][j]

        return distances







    @staticmethod
    def link_nodes_for_graph(graph_type, nbr_nodes, ring_node_list):
        """
        Link the nodes to create the requested graph.

        Args:
            graph_type: The name of the graph type.
            nbr_nodes: The total number of nodes the user requested.
                       (Will be > 0 or this method won't be called.)
            ring_node_list: The nodes that have been arranged in a ring.
                            Will contain either:
                            nbr_nodes - 1 if graph type is STAR or WHEEL
                            or nbr_nodes otherwise

        Returns: None

        Overrides this function from graph_framework.
        """

        # Wilson's implementation of:
        # RING, STAR, AND WHEEL
        if graph_type in [RING, STAR, WHEEL]:
            first_node = ring_node_list[0]
            node_a = first_node
            if graph_type in ['star', 'wheel']:
                # move the first node to the center
                first_node.move_to_xy(center_pixel())
            for node_b in ring_node_list if graph_type == 'random' else ring_node_list[1:]:
                if graph_type in ['star']:
                    # connects the center node to all other nodes
                    Link(node_a, node_b)
                elif graph_type in ['ring', 'wheel']:
                    # in the case of ring, connects all the nodes in a ring formation
                    # for wheel, it connects the nodes that are around the center node like ring
                    Link(node_a, node_b)
                    node_a = node_b

            last_node = ring_node_list[-1]
            if graph_type == 'ring':
                # connects the last node to the first node closing the ring
                Link(last_node, first_node)
            elif graph_type == 'wheel':
                # connects the last node to the first node closing the other part of the wheel
                next_node = ring_node_list[1]
                Link(last_node, next_node)
                # creates the spokes of the wheel, like in star
                for node in ring_node_list[2:]:
                    Link(first_node, node)

        # Wilson's implementation of:
        # RANDOM
        elif graph_type == RANDOM:
            # uses the Erdo-Renyl model for random graphs that chooses [n/n-2]/2 edges with link_prob
            link_prob = SimEngine.gui_get(LINK_PROB) / 100
            # initial positions of nodes checked
            v = 1
            w = -1
            if link_prob == 1:
                # links all nodes to all other nodes if link_prob is set to 100
                for agent in ring_node_list:
                    other_agents = [a for a in ring_node_list if a is not agent]
                    for i in range(len(other_agents)):
                        Link(agent, other_agents[i])
            elif 0 < link_prob < 1:
                # lr is divided with lp and added to w to determine the nodes that v will link to
                # cycles through every node(v) and links to only values of w that are within the range of ring_node_list
                lp = math.log(1.0 - link_prob)
                while v < len(ring_node_list):
                    lr = math.log(1.0 - random())
                    w = w + 1 + int(lr / lp)
                    while w >= v and v < len(ring_node_list):
                        w = w - v
                        v = v + 1
                    if v < len(ring_node_list):
                        Link(ring_node_list[v], ring_node_list[w])

        # Stanley's implementation of:
        # PREFERENTIAL ATTACHMENT
        elif graph_type == PREF_ATTACHMENT:

            # Implementation of Preferential Attachment based solely off number of links per agent.
            for agent in ring_node_list:
                other_agents = [a for a in ring_node_list if a is not agent]
                linked_agent_pairs = [(l.agent_1, l.agent_2) for l in Graph_Algorithms_World.links if
                                      not l.includes(agent)]
                linked_agents = [a for pair in linked_agent_pairs for a in pair]
                if not Graph_Algorithms_World.links:
                    Link(agent, choice(other_agents))
                else:
                    if linked_agents:
                        Link(agent, choice(linked_agents))
                    else:
                        Link(agent, choice(other_agents))

            # Another implementation of Preferential Attachment using choices
            # for agent in ring_node_list:
            #     # All the nodes that have yet to get a link, minus this agent
            #     # The agent theoretically should have been just created when this method is called.
            #     other_agents = [a for a in ring_node_list if a is not agent]
            #
            #     # How many links exist in the world?
            #     # This number can not be <= 0, since we divide by it when finding probability.
            #     total_links = len(Graph_World.links) if Graph_World.links else 1
            #
            #     partners = []
            #     partners_probability = []
            #
            #     for a in other_agents:
            #         nbr_links = 0
            #         for link in Graph_World.links:
            #             if link.includes(a):
            #                 nbr_links += 1
            #         partners.append(a)
            #         # We divide number of links by total links to get a probability.
            #         partners_probability.append(nbr_links/total_links)
            #
            #     # Random.choices with k = 1 will pick 1 element from the population using the probability as our weight.
            #     # Population and weights must be the same size, and there is a 1-1 mapping between both.
            #     # This means population[0] will use weights[0] as the probability.
            #     # This will return a list of k elements, which is why we have to get the index at 0.
            #     preferred_agent = choices(population=partners, weights=partners_probability, k=1)[0]
            #
            #     # Create a link with the preferred agent
            #     Link(agent, preferred_agent)

        # Matthew's implementation of Small-World Graph
        elif graph_type == SMALL_WORLD:
            # gets neighborhood size from GUI
            neighborhood_size = SimEngine.gui_get("nbrh_size")
            # if the neighborhood size is not less than half of the number of nodes,
            # then there will be overlap in the links, a links to b and b links to a
            # this if statement prevents that
            if neighborhood_size >= len(ring_node_list) / 2:
                neighborhood_size = int(len(ring_node_list) / 2) - 1 + (len(ring_node_list) % 2)
            # nested for loop that loops through the [neighborhood size] next nodes after node_a
            # for all node_a in ring_node_list
            for node_num_a in range(len(ring_node_list)):
                for node_num_b in range(node_num_a + 1, node_num_a + 1 + neighborhood_size):
                    # loops back around if node_num_b goes past the end of ring_node_list
                    if node_num_b >= len(ring_node_list):
                        node_num_b = node_num_b - len(ring_node_list)
                    # links node_a to node_b
                    Link(ring_node_list[node_num_a], ring_node_list[node_num_b])

            # Now that we have our links, we have to re-wire them according to the rewire probability.
            # Divide by 100 to get a number <= 1
            rewire_prob = SimEngine.gui_get("link_prob")/100

            if rewire_prob != 0:
                # Get the number of links in the world
                nbr_links = len(Graph_World.links)

                # Multiply the rewire_prob by the number of links so we know how many links to re-wire
                # We use math.ceil to round up when converting to an integer.
                # This makes non-zero probabilities at least 1
                nbr_links_to_rewire = math.ceil(rewire_prob * nbr_links)

                # Random sample of the number of links to rewire
                links_rewire_sample = sample(list(Graph_World.links), k=nbr_links_to_rewire)

                # Time to start rewiring
                for link in links_rewire_sample:
                    # Pick a random agent that isn't part of the link.
                    random_agent = choice(list(Graph_World.agents))
                    while link.includes(random_agent):
                        random_agent = choice(list(Graph_World.agents))
                    # Rewire the link's second agent (It doesn't matter if its agent1 or agent2)
                    # to be the random agent
                    link.agent_2 = random_agent

    def setup(self):
        super().setup()
        Agent.id = 0



if __name__ == '__main__':
    from core.agent import PyLogo, Agent

    PyLogo(Graph_Algorithms_World, 'Network test', gui_left_upper=graph_left_upper,
           gui_right_upper=graph_right_upper, agent_class=Graph_Node,
           clear=True, bounce=True, auto_setup=False)
