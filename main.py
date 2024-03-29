from algorithms.encodings.relative_sat_encoder import RelativeSatEncoder
from algorithms.down_up_sat_checker import process_modules, process, process_from_top
# from algorithms.ilp_checker import process
from algorithms.other.helpers import calculate_twinwidth_of_sequence, read_graph
from algorithms.graph_preprocessing_wrapper import graph_preprocessing_wrapper
import networkx as nx
import matplotlib.pyplot as plt
import os

INSTANCES_PATH = 'instances'


def draw_graph(g: nx.Graph):
    pos = nx.spring_layout(g)
    nx.draw_networkx_nodes(g, pos, node_size=256, node_color='green')
    nx.draw_networkx_edges(g, pos, edgelist=g.edges(), edge_color='black')
    nx.draw_networkx_labels(g, pos)
    plt.show()


def preprocess_base_graph(g):
    return process_from_top(g, RelativeSatEncoder(), [], "cadical")
    # return process(g, RelativeSatEncoder(), [], "cadical")
    # return process_modules(g, RelativeSatEncoder(), [], "cadical")


if __name__ == '__main__':
    file_names = os.listdir(INSTANCES_PATH)
    expected_results = [1, 2, 0, 0, 3, 0, 2, 4, 1, 2]
    for file_name, expected_result in zip(sorted(file_names), expected_results):
        file_path = os.path.join(INSTANCES_PATH, file_name)
        graph = read_graph(file_path)

        tww, sequence = graph_preprocessing_wrapper(graph, preprocess_base_graph)
        print(f"{file_path}: {expected_result}/{tww}/{calculate_twinwidth_of_sequence(graph, sequence)}")
        # print(sequence)
        # print("Contraction sequence: \n" + "\n".join([f"{u} => {v}" for u, v in sequence]))
        # draw_graph(graph)
