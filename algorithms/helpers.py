import os

import networkx as nx
from algorithms.trigraph import Trigraph


def calculate_sequence_twinwidth(graph: nx.Graph, sequence):
    return 0
    trigraph = Trigraph(graph)
    max_red = 0
    for u, v in sequence:
        trigraph.merge(u, v)
        max_red = max(max_red, trigraph.max_red_degree())

    return max_red


def read_graph(path):
    lines = _preprocess_file(path)
    n, m = (int(num) for num in lines[0].split(" ")[2:])

    g = nx.Graph()
    for edge_line in lines[1:m+1]:
        u, v = (int(num) for num in edge_line.split(' '))
        g.add_edge(u, v)

    return g


def write_graph(graph: nx.Graph, file_name):
    t = [f"p tww {len(graph.nodes)} {len(graph.edges)}"]
    for u, v in graph.edges:
        t.append(f"{u} {v}")
    s = "\n".join(t)
    with open(file_name, "w") as f:
        f.write(s)


def _preprocess_file(path):
    with open(path, 'r') as f:
        c = [line for line in f.read().split("\n") if not line.startswith("c")]
        return c
