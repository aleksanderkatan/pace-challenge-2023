import networkx as nx
from algorithms.encodings.abstract_encoder import AbstractEncoder
from pysat.solvers import Solver
from algorithms.formula_preprocessing.abstract_preprocessing_algorithm import AbstractPreprocessingAlgorithm


# runs preprocessing algorithms one by one
def _process(formula, preprocesses: list[AbstractPreprocessingAlgorithm], solver_name):
    if len(preprocesses) == 0:
        with Solver(bootstrap_with=formula, name=solver_name) as solver:
            if solver.solve():
                return solver.get_model()
            return None

    prep = preprocesses[0]
    prep.initialize_with_formula(formula)
    new_formula = prep.preprocess_formula()
    result = _process(new_formula, preprocesses[1:], solver_name)
    return prep.reprocess_result(result)


def process(graph: nx.Graph, encoder: AbstractEncoder, preprocesses: list[AbstractPreprocessingAlgorithm], solver_name):
    for i in range(0, len(graph.nodes) + 1):
        encoder.initialize_with_graph(graph, i)
        formula = encoder.encode()
        result = _process(formula, preprocesses, solver_name)
        if result is None:
            continue
        sequence = encoder.decode(result)
        return i, sequence
    raise RuntimeError("How did we get here?")
