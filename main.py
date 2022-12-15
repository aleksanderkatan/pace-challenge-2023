from algorithms.formula_preprocessing.subsumption_remover import SubsumptionRemover
from algorithms.encodings.relative_sat_encoder import RelativeSatEncoder
from algorithms.down_up_sat_checker import process
# from algorithms.ilp_checker import process
from algorithms.helpers import calculate_sequence_twinwidth, read_graph
import networkx as nx
import matplotlib.pyplot as plt
from ortools.linear_solver import pywraplp
import os

INSTANCES_PATH = ''


def draw_graph(g: nx.Graph):
    pos = nx.spring_layout(g)
    nx.draw_networkx_nodes(g, pos, node_size=256, node_color='green')
    nx.draw_networkx_edges(g, pos, edgelist=g.edges(), edge_color='black')
    nx.draw_networkx_labels(g, pos)
    plt.show()


if __name__ == '__main__':
    file_names = os.listdir(INSTANCES_PATH)
    expected_results = [1, 2, 0, 0, 3, 0, 2, 4, 1, 2]
    for file_name, expected_result in zip(sorted(file_names), expected_results):
        file_path = os.path.join(INSTANCES_PATH, file_name)
        graph = read_graph(file_path)

        # tww, sequence = process(graph, pywraplp.Solver.CreateSolver("SCIP"))
        # tww, sequence = process(graph, RelativeSatEncoder(), [SubsumptionRemover()], "gluecard4")
        tww, sequence = process(graph, RelativeSatEncoder(), [], "cadical")
        print(f"{file_path}: {expected_result}/{tww}/{calculate_sequence_twinwidth(graph, sequence)}")
        # print("Contraction sequence: \n" + "\n".join([f"{u} => {v}" for u, v in sequence]))
        # draw_graph(graph)

