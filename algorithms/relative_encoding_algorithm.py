from pysat.solvers import Solver
from pysat.formula import IDPool
from pysat.formula import CNFPlus
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

    # v_i is the child of v_j
    def p(self, i, j):
        if i < j:
            return self.v["p", i, j]
        return -self.v["p", j, i]

    # there is a red edge between v_i and v_j at some point
    def a(self, i, j):
        if i < j:
            return self.v["a", i, j]
        # no negation here!!!
        return self.v["a", j, i]

    # implies([p_1, p_2, p_3], q) returns a clause equivalent to
    # p_1 && p_2 && p_3 => q
    def implies(self, p, q):
        return [-p_i for p_i in p] + [q]

    def encode(self):
        formula = CNFPlus()
        n = len(self.g.nodes)

        # ordering
        for i in range(1, n+1):
            for j in range(1, n+1):
                for k in range(1, n+1):
                    if len({i, j, k}) < 3:
                        continue
                    clause = self.implies(
                        [self.o(i, j), self.o(j, k)],
                        self.o(i, k)
                    )
                    formula.append(clause)

        # parents are bigger than their children
        # i is the child of j => i << j
        for i in range(1, n+1):
            for j in range(i+1, n+1):
                clause = self.implies(
                    [self.p(i, j)],
                    self.o(i, j)
                )
                formula.append(clause)

        # every vertex (except v_n) has at least one parent
        for i in range(1, n):
            clause = [self.p(i, j) for j in range(i+1, n+1)]
            formula.append(clause)

        # every vertex (except v_n) has at most one parent
        for i in range(1, n):
            for j in range(i+1, n+1):
                for k in range(j+1, n+1):
                    clause = [-self.p(i, j), -self.p(i, k)]
                    formula.append(clause)

        # subsets 1c and 1d
        for i in range(1, n+1):
            for j in range(i+1, n+1):
                for k in range(1, n+1):
                    if len({i, j, k}) < 3:
                        continue
                    if self.g.has_edge(i, k) == self.g.has_edge(j, k):
                        continue
                    clause = self.implies(
                        [self.p(i, j), self.o(i, k)],
                        self.r(i, j, k)
                    )
                    formula.append(clause)

        # a
        for i in range(1, n+1):
            for j in range(i+1, n+1):
                for k in range(1, n+1):
                    if len({i, j, k}) < 3:
                        continue
                    # v1 ----
                    clause = self.implies(
                        [self.o(i, j), self.o(i, k), self.r(i, j, k)],
                        self.a(j, k)
                    )
                    # v2 ----
                    # clause = self.implies(
                    #     [self.r(k, i, j)],
                    #     self.a(i, j)
                    # )
                    formula.append(clause)

        # subset 1a
        for i in range(1, n+1):
            for j in range(1, n+1):
                for k in range(1, n+1):
                    for m in range(k+1, n+1):
                        if len({i, j, k, m}) < 4:
                            continue
                        clause = self.implies(
                            [self.o(i, j), self.o(j, k), self.o(j, m), self.r(i, k, m)],
                            self.r(j, k, m)
                        )
                        formula.append(clause)

        # subset 1b
        for i in range(1, n+1):
            for j in range(i+1, n+1):
                for k in range(1, n+1):
                    if len({i, j, k}) < 3:
                        continue
                    clause = self.implies(
                        [self.p(i, j), self.o(i, k), self.a(i, k)],
                        self.r(i, j, k)
                    )
                    formula.append(clause)

        # cardinality constraints
        for i in range(1, n+1):
            for j in range(1, n+1):
                # if len({i, j}) < 2:
                #     continue
                clause = [self.r(i, j, k) for k in range(1, n+1) if j != k]
                formula.append([clause, self.tww], is_atmost=True)

        # v_n is the biggest
        for i in range(1, n):
            clause = [self.o(i, n)]
            formula.append(clause)

        # if a vertex is no more, then there no edges from it
        for i in range(1, n+1):
            for j in range(i+1, n+1):
                for k in range(1, n+1):
                    if len({i, j, k}) < 3:
                        continue
                    clause = self.implies(
                        [self.o(j, i)],
                        -self.r(i, j, k)
                    )
                    formula.append(clause)

        return formula


def process(graph):
    for i in range(0, 4):
        encoder = Encoder(graph, i)
        formula = encoder.encode()
        with Solver(bootstrap_with=formula, name="gluecard4") as solver:
            if solver.solve():
                # print(solver.get_model())
                # TODO: decode and return sequence
                return i
    return -1


