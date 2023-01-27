import networkx as nx
from algorithms.encodings.abstract_sat_encoder import AbstractSatEncoder
from pysat.solvers import Solver
from algorithms.formula_preprocessing.abstract_preprocessing_algorithm import AbstractPreprocessingAlgorithm
from algorithms.modular_decomposition import modular_decomposition


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


def process(graph: nx.Graph, encoder: AbstractSatEncoder, preprocesses: list[AbstractPreprocessingAlgorithm],
            solver_name):
    for i in range(0, len(graph.nodes) + 1):
        encoder.initialize_with_graph(graph, i)
        formula = encoder.encode()
        result = _process(formula, preprocesses, solver_name)
        if result is None:
            continue
        sequence = encoder.decode(result)
        return i, sequence
    raise RuntimeError("How did we get here?")


def process_from_top(graph: nx.Graph, encoder: AbstractSatEncoder, preprocesses: list[AbstractPreprocessingAlgorithm],
            solver_name):
    tww, sequence = None, None
    for i in reversed(range(0, len(graph.nodes) + 1)):
        encoder.initialize_with_graph(graph, i)
        formula = encoder.encode()
        result = _process(formula, preprocesses, solver_name)
        if result is None:
            return tww, sequence
        sequence = encoder.decode(result)
        tww = i
    return 0, sequence


def modules(root):
    if root[0].node_type == 3:
        return (root[1], [root[1]])
    vertices = []
    current_modules = []
    for module in root[1]:
        vert, mods = modules(module)
        vertices = vertices + vert
        current_modules = current_modules + mods
    current_modules.append(vertices)
    return (vertices, current_modules)

def process_modules(graph: nx.Graph, encoder: AbstractSatEncoder,
                    preprocesses: list[AbstractPreprocessingAlgorithm], solver_name):
    a = modular_decomposition(graph)
    ver, mods = modules(a)
    mx = 0
    graphs = []
    for mod in mods:
        graphs.append(graph.subgraph(mod))
    for g in graphs:
        if len(g.nodes) > mx:
            mx = len(g.nodes)
    for i in range(0, mx + 1):
        f = 1
        sequences = []
        for graph in graphs:
            encoder.initialize_with_graph(graph, i)
            formula = encoder.encode()
            result = _process(formula, preprocesses, solver_name)
            if result is None:
                f = 0
                break
            # sequences.append(encoder.decode(result))
        if f:
            return i, sequences
    raise RuntimeError('How did we get here')
