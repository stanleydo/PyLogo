# Import the string constants you need (mainly keys) as well as classes and gui elements
from core.graph_framework import (CLUSTER_COEFF, Graph_Node, Graph_World, PATH_LENGTH, TBD, graph_left_upper,
                                  graph_right_upper)
from core.pairs import center_pixel
from core.sim_engine import SimEngine
from core.link import Link
from random import choice

# Import strings from graph_framework
from core.graph_framework import PREF_ATTACHMENT, RANDOM, RING, SMALL_WORLD, WHEEL, STAR


class Graph_Algorithms_World(Graph_World):

    # noinspection PyMethodMayBeStatic
    # TODO -- Matthew work on this
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

    # noinspection PyMethodMayBeStatic
    def clustering_coefficient(self):
        """
        v = a node
        kv = degree(number of nodes connected to v)
        Nv: number of links between neighbors of v
        cc = (2 * Nv) / (kv(kv-1))
        """
        all_nodes = list(Graph_World.agents)

        # Top level Clustering Coefficient
        cc_main = 0

        # Loop through all of the nodes
        for v in all_nodes:

            # Find the degree of the node (kv), as well as a list of agents that are linked to v
            kv, linked_nodes = self.find_linked_nodes(v)

            # Check if there are actually any connected nodes to v before we do anything
            if kv >= 2:
                # Initialize nv (number of links between neighbors of v)
                nv = 0
                # We will use a while loop to pop off agents from linked_nodes
                # This will allow us to search all nodes without adding
                # the additional links from nv
                while linked_nodes:
                    print()
                    print("linked nodes for ", v.id, " is ", [x.id for x in linked_nodes])
                    neighbor_node = linked_nodes.pop(0)
                    # Find the number of links that each neighbor has (Where the other agent is in Linked_nodes)
                    # The 0th index is the nbr_links from (nbr_links, list_of_neighbors)
                    # See self.find_linked_nodes() below
                    nbr_links_neighbors = self.find_linked_nodes(neighbor_node, linked_nodes)[0]
                    # Add the number of links between neighbors to nv
                    nv += nbr_links_neighbors
                # Compute cc(v) and add it to cc_main so we can average it later.
                cc_sub_v = (2 * nv) / (kv * (kv - 1))
                cc_main += cc_sub_v

        # Average cc_main to find the clustering_coefficient of the whole graph
        return cc_main / len(all_nodes)

    @staticmethod
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
        print("\n\nlink_nodes_for_graph: Your code goes here.")
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
        # PREFERENTIAL ATTACHMENT
        elif graph_type == PREF_ATTACHMENT:
            # Graph_Algorithms_World.links
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
        elif graph_type == SMALL_WORLD:
            pass
        # TODO -- Need to implement the small world graph into this version (Move over from original networking.py)



if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Graph_Algorithms_World, 'Network test', gui_left_upper=graph_left_upper,
           gui_right_upper=graph_right_upper, agent_class=Graph_Node,
           clear=True, bounce=True, auto_setup=True)
