from algorithms.helpers import write_graph
import networkx as nx
import random

path = "../benchmark_instances/"


def write(graph, file_name):
    write_graph(graph, path + file_name)


def random_edge_chance(n, chance):
    g = nx.Graph()
    for u in range(1, n+1):
        for v in range(u+1, n+1):
            if random.random() < chance:
                g.add_edge(u, v)
    return g


instances = [
    (nx.random_cograph(4), "cograph_16.gr"),
    (nx.random_cograph(5), "cograph_32.gr"),
    (nx.random_cograph(6), "cograph_64.gr"),
    (nx.random_tree(2**4), "tree_16.gr"),
    (nx.random_tree(2**5), "tree_32.gr"),
    (nx.random_tree(2**6), "tree_64.gr"),
    (nx.complete_graph(2**4), "clique_16.gr"),
    (nx.complete_graph(2**5), "clique_32.gr"),
    (nx.complete_graph(2**6), "clique_64.gr"),
    (nx.cycle_graph(2**4), "cycle_16.gr"),
    (nx.cycle_graph(2**5), "cycle_32.gr"),
    (nx.cycle_graph(2**6), "cycle_64.gr"),
    (nx.path_graph(2**4), "path_16.gr"),
    (nx.path_graph(2**5), "path_32.gr"),
    (nx.path_graph(2**6), "path_64.gr"),
    (nx.star_graph(2**4), "star_16.gr"),
    (nx.star_graph(2**5), "star_32.gr"),
    (nx.star_graph(2**6), "star_64.gr"),
    (nx.grid_2d_graph(4, 4), "grid_4x4.gr"),
    (nx.grid_2d_graph(6, 6), "grid_6x6.gr"),
    (nx.grid_2d_graph(8, 8), "grid_8x8.gr"),
    (random_edge_chance(16, 0.5), "edge_chance_0.5_16.gr"),
    (random_edge_chance(32, 0.5), "edge_chance_0.5_32.gr"),
    (random_edge_chance(64, 0.5), "edge_chance_0.5_64.gr"),
]

for graph, name in instances:
    write(graph, name)

