from pysat.solvers import Solver


def encode(g, tww):
    # TODO: implement
    pass


class RelativeEncodingAlgorithm:
    def __process__(self, graph):
        for i in range(0, 5):
            formula = encode(graph, i)
            with Solver(bootstrap_with=formula) as solver:
                # 1.1 call the solver for this formula:
                if solver.solve():
                    print(solver.get_model())
                    # TODO: decode and return sequence
                    return i







