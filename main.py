from utility import *
from algorithms.relative_encoding_algorithm import process
import networkx as nx
import matplotlib.pyplot as plt

INSTANCES_PATH = 'instances'


def draw_graph(g: nx.Graph):
    pos = nx.spring_layout(g)
    nx.draw_networkx_nodes(g, pos, node_size=256, node_color='green')
    nx.draw_networkx_edges(g, pos, edgelist=g.edges(), edge_color='black')
    nx.draw_networkx_labels(g, pos)
    plt.show()


if __name__ == '__main__':
    # TODO: implement modular decomposition
    file_names = os.listdir(INSTANCES_PATH)
    for file_name in file_names:
        file_path = os.path.join(INSTANCES_PATH, file_name)
        graph = parse_graph(file_path)
        tww = process(graph)
        print(file_path, tww)

        # sequence = algorithm.__process__(graph)
        # sequence_width = sequence_verifier.calculate_twinwidth(graph, sequence)
        #
        # if sequence_width != twinwidth:
        #     print(f"Actual twinwidth {twinwidth} is not equal to the width of the sequence {sequence_width} "
        #           f"for file {file_name}")
