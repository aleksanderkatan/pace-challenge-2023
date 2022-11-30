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
    expected_results = [1, 2, 0, 0, 3, 0, 2, 4, 1, 2]
    for file_name, expected_result in zip(sorted(file_names), expected_results):
        file_path = os.path.join(INSTANCES_PATH, file_name)
        graph = parse_graph(file_path)
        tww, sequence = process(graph)
        print(f"{file_path}: expected: {expected_result}, our: {tww}")
        print("Contraction sequence: \n" + "\n".join([f"{u} => {v}" for u, v in sequence]))
        # draw_graph(graph)

