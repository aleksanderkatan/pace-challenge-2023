from pysat.solvers import Solver
from pysat.formula import IDPool
import networkx as nx


class Encoder:
    def __init__(self, graph: nx.Graph, tww):
        self.g = graph
        self.tww = tww
        self.pool = IDPool()
        self.v = {}
        self._initialize_variables()

    def _initialize_variables(self):
        n = len(self.g.nodes)

        for i in range(1, n+1):
            for j in range(i+1, n+1):
                for k in range(1, n+1):
                    self.v["r", k, i, j] = self.pool.id(("r", k, i, j))
                self.v["o", i, j] = self.pool.id(("o", i, j))
                self.v["p", i, j] = self.pool.id(("p", i, j))
                self.v["a", i, j] = self.pool.id(("a", i, j))

    # there is a red edge between v_i and v_j after contracting v_i
    def r(self, k, i, j):
        if i < j:
            return self.v["r", k, i, j]
        return -self.v["r", k, j, i]

    # v_i << v_j
    def o(self, i, j):
        if i < j:
            return self.v["o", i, j]
        return -self.v["o", j, i]

    # v_i is the parent of v_j
    def p(self, i, j):
        if i < j:
            return self.v["p", i, j]
        return -self.v["p", j, i]

    # there is a red edge between v_i and v_j at some point
    def a(self, i, j):
        if i < j:
            return self.v["a", i, j]
        return -self.v["a", j, i]

    def encode(self):
        return None


def encode(g, tww):
    # TODO: implement
    pass


def process(graph):
    for i in range(0, 5):
        encoder = Encoder(graph, i)
        formula = encoder.encode()
        # with Solver(bootstrap_with=formula) as solver:
            # if solver.solve():
            #     print(solver.get_model())
            #     TODO: decode and return sequence
                # return i


