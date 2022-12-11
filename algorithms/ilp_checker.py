import networkx as nx
from ortools.linear_solver import pywraplp
from algorithms.encodings.relative_ilp_encoder import SatToIlpEncoder


def process(graph: nx.Graph, solver: pywraplp.Solver, tww_upper_bound=None):
    encoder = SatToIlpEncoder(graph, solver, tww_upper_bound)
    return encoder.solve()
