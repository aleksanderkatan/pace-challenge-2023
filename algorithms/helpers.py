import os

import networkx as nx
from algorithms.trigraph import Trigraph


def calculate_sequence_twinwidth(graph: nx.Graph, sequence):
    trigraph = Trigraph(graph)
    max_red = 0
    for u, v in sequence:
        trigraph.merge(u, v)
        max_red = max(max_red, trigraph.max_red_degree())

    return max_red


def read_directory(path):
    file_names = os.listdir(path)
    file_contents = []
    for file_name in file_names:
        file_path = os.path.join(path, file_name)
        with open(file_path, 'r') as f:
            c = [line for line in f.read().split("\n") if not line.startswith("c")]
            file_contents.append(c)
    return file_contents


def parse_graph(path):
    lines = _preprocess_file(path)
    n, m = (int(num) for num in lines[0].split(" ")[2:])

    g = nx.Graph()
    for edge_line in lines[1:m+1]:
        u, v = (int(num) for num in edge_line.split(' '))
        g.add_edge(u, v)

    return g


def _preprocess_file(path):
    with open(path, 'r') as f:
        c = [line for line in f.read().split("\n") if not line.startswith("c")]
        return c
