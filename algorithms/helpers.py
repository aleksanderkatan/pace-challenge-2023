import networkx as nx
from algorithms.trigraph import Trigraph


def calculate_sequence_twinwidth(graph: nx.Graph, sequence):
	trigraph = Trigraph(graph)
	max_red = 0
	for u, v in sequence:
		trigraph.merge(u, v)
		max_red = max(max_red, trigraph.max_red_degree())

	return max_red

