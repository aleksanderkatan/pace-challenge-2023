from pysat.solvers import Solver
from algorithms.relative_encoding.relative_encoder import RelativeEncoder


class RelativeEncodingAlgorithm:
    def __process__(self, graph):
        encoder = RelativeEncoder()
        for i in range(0, 5):
            formula = encoder.generate_formula(graph, i)
            with Solver(bootstrap_with=formula) as solver:
                # 1.1 call the solver for this formula:
                if solver.solve():
                    print(solver.get_model())
                    # TODO: decode and return sequence
                    return i







