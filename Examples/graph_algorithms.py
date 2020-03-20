# Import the string constants you need (mainly keys) as well as classes and gui elements
from Examples.graph_framework import (CLUSTER_COEFF, Graph_Node, Graph_World, PATH_LENGTH, TBD, graph_left_upper,
                                      graph_right_upper)
from core.pairs import center_pixel
from core.sim_engine import SimEngine
from core.link import Link
from random import choice

# Import strings from graph_framework
from Examples.graph_framework import PREF_ATTACHMENT, RANDOM, RING, SMALL_WORLD, WHEEL, STAR


class Graph_Algorithms_World(Graph_World):

    # noinspection PyMethodMayBeStatic
    # TODO -- Matthew work on this
    def average_path_length(self):
        return TBD

    # noinspection PyMethodMayBeStatic
    # TODO -- Wilson work on this
    def clustering_coefficient(self):
        return TBD

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
        # TODO -- Need to implement the small world graph into this version (Move over from original networking.py)



if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Graph_Algorithms_World, 'Network test', gui_left_upper=graph_left_upper,
           gui_right_upper=graph_right_upper, agent_class=Graph_Node,
           clear=True, bounce=True, auto_setup=True)
