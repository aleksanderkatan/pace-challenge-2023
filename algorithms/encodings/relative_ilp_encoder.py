import networkx as nx
from ortools.linear_solver import pywraplp


def _sum(elements):
    result = elements[0]
    for elem in elements[1:]:
        result = result + elem
    return result


def _implies(p, q):
    return _sum([1 - p_i for p_i in p]) + q >= 1


class SatToIlpEncoder:
    def __init__(self, graph: nx.Graph, tww_upper_bound=None):
        if tww_upper_bound is None:
            tww_upper_bound = len(graph.nodes)
        self.tww_upper_bound = tww_upper_bound
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        self.graph = graph
        self.variables = {}
        n = len(self.graph.nodes)
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                for k in range(1, n + 1):
                    self.variables["r", k, i, j] = self.solver.IntVar(0.0, 1.0, "")
                self.variables["o", i, j] = self.solver.IntVar(0.0, 1.0, "")
                self.variables["p", i, j] = self.solver.IntVar(0.0, 1.0, "")
                self.variables["a", i, j] = self.solver.IntVar(0.0, 1.0, "")
        self.variables["tww"] = self.solver.IntVar(0.0, tww_upper_bound, "")

    def r(self, k, i, j):
        if i < j:
            return self.variables["r", k, i, j]
        return self.variables["r", k, j, i]

    # v_i << v_j
    def o(self, i, j):
        if i < j:
            return self.variables["o", i, j]
        return 1-self.variables["o", j, i]

    # v_i is the child of v_j
    def p(self, i, j):
        if i < j:
            return self.variables["p", i, j]
        return 1-self.variables["p", j, i]

    # there is a red edge between v_i and v_j at some point
    def a(self, i, j):
        if i < j:
            return self.variables["a", i, j]
        return self.variables["a", j, i]

    def tww(self):
        return self.variables["tww"]

    def encode(self):
        n = len(self.graph.nodes)
        # ordering
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                for k in range(1, n + 1):
                    if len({i, j, k}) < 3:
                        continue
                    rel = _implies(
                        [self.o(i, j), self.o(j, k)],
                        self.o(i, k)
                    )
                    self.solver.Add(rel)

        # parents are bigger than their children
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                rel = _implies(
                    [self.p(i, j)],
                    self.o(i, j)
                )
                self.solver.Add(rel)

        # every vertex (except v_n) has at exactly one parent
        for i in range(1, n):
            elements = _sum([self.p(i, j) for j in range(i + 1, n + 1)])
            rel = elements == 1
            self.solver.Add(rel)

        # subsets 1c and 1d
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                for k in range(1, n + 1):
                    if len({i, j, k}) < 3:
                        continue
                    if self.graph.has_edge(i, k) == self.graph.has_edge(j, k):
                        continue
                    rel = _implies(
                        [self.p(i, j), self.o(i, k)],
                        self.r(i, j, k)
                    )
                    self.solver.Add(rel)

        # a
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                for k in range(1, n + 1):
                    if len({i, j, k}) < 3:
                        continue
                    rel = _implies(
                        [self.r(k, i, j)],
                        self.a(i, j)
                    )
                    self.solver.Add(rel)

        # subset 1a
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                for k in range(1, n + 1):
                    for m in range(k + 1, n + 1):
                        if len({i, j, k, m}) < 4:
                            continue
                        rel = _implies(
                            [self.o(i, j), self.o(j, k), self.o(j, m), self.r(i, k, m)],
                            self.r(j, k, m)
                        )
                        self.solver.Add(rel)

        # subset 1b
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                for k in range(1, n + 1):
                    if len({i, j, k}) < 3:
                        continue
                    rel = _implies(
                        [self.p(i, j), self.o(i, k), self.a(i, k)],
                        self.r(i, j, k)
                    )
                    self.solver.Add(rel)

        # cardinality constraints
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                literals = _sum([self.r(i, j, k) for k in range(1, n + 1) if j != k])
                rel = literals <= self.tww()
                self.solver.Add(rel)

        # v_n is the biggest
        for i in range(1, n):
            rel = self.o(i, n) >= 1
            self.solver.Add(rel)

        # if a vertex is no more, then there no edges from it
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                for k in range(1, n + 1):
                    if len({i, j, k}) < 3:
                        continue
                    rel = _implies(
                        [self.o(j, i)],
                        1-self.r(i, j, k)
                    )
                    self.solver.Add(rel)

        self.solver.Minimize(self.tww())
        status = self.solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            return int(self.solver.Objective().Value()), self.decode()
        raise RuntimeError("How did we get here?")

    def decode(self):
        n = len(self.graph.nodes)

        parents = {}
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                if i != j and self.p(i, j).solution_value():
                    parents[i] = j
                    break

        # skip last element
        order = [0] * (n-1)
        for i in range(1, n):
            bigger_than_i = [j for j in range(1, n + 1) if (j != i and self.o(i, j).solution_value())]
            order[n - len(bigger_than_i) - 1] = i

        sequence = [(v, parents[v]) for v in order]
        return sequence
