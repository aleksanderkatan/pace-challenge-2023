import networkx as nx
from algorithms.encodings.abstract_sat_encoder import AbstractSatEncoder
from pysat.solvers import Solver
from algorithms.formula_preprocessing.abstract_preprocessing_algorithm import AbstractPreprocessingAlgorithm
from algorithms.modular_decomposition import modular_decomp


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

def is_prime(g: nx.Graph):
    ver, mods = modular_decomp(g)
    return len(mods) == g.number_of_nodes()

def merge(g: nx.Graph, red_edges, a, b):
    merged_g = nx.Graph()
    merged_red_edges = dict()
    for v in list(g.nodes):
        if v == a:
            continue
        merged_g.add_node(v)
    for edg in list(g.edges):
        u, v = edg
        if (u == a and v == b) or (u == b and v == a):
            continue
        if u == a or u == b:
            merged_g.add_edge(b, v)
            if g.has_edge(b, v) and g.has_edge(a, v) and (a, v) not in red_edges and (b, v) not in red_edges and (v, a) not in red_edges and (v, b) not in red_edges:
                pass
            else:
                merged_red_edges[(b, v)] = True
        elif v == a or v == b:
            merged_g.add_edge(b, u)
            if g.has_edge(a, u) and g.has_edge(b, u) and (a, u) not in red_edges and (b, u) not in red_edges and (u, a) not in red_edges and (u, b) not in red_edges:
                pass
            else:
                merged_red_edges[(b, u)] = True
        else:
            merged_g.add_edge(u, v)
            if (u, v) in red_edges or (v, u) in red_edges:
                merged_red_edges[(u, v)]
    return merged_g, merged_red_edges


def try_contract_with_u(g: nx.Graph, red_edg, u, v):
    for a in list(g.nodes):
        if a == u or a == v:
            continue
        gr, edg_dct = merge(g, red_edg, a, u)
        if len(edg_dct) == 1:
            return a
    return -1

def check_tww_1(g: nx.Graph):
    n = len(g.nodes)
    if n <= 3:
        return False
    f = 0
    for a in list(g.nodes):
        for b in list(g.nodes):
            if a == b:
                continue
            gr, edg_dct = merge(g, dict(), a, b)
            if len(edg_dct) == 1:
                f = 1
                u = a
                v = b
                break
        if f == 1:
            break
    if f == 0:
        return False
    gr, red_edg = merge(g, dict(), u, v)
    for i in range(n-3):
        u, v = next(iter(red_edg))
        a = try_contract_with_u(gr, red_edg, u, v)
        if a != -1:
            gr, red_edg = merge(gr, red_edg, a, u)
            continue
        a = try_contract_with_u(gr, red_edg, v, u)
        if a != -1:
            gr, red_edg = merge(gr, red_edg, a, v)
            continue
        gr, red_edg = merge(gr, red_edg, u, v)
        if len(red_edg) == 0:
            raise RuntimeError('How did we get here')
        if len(red_edg) != 1:
            return False
    return True

    


def process_modules(g: nx.Graph, encoder: AbstractSatEncoder,
                    preprocesses: list[AbstractPreprocessingAlgorithm], solver_name):
    if is_prime(g):
        if check_tww_1(g) == True:
            return 1, []
        return process(g, encoder, preprocesses, solver_name)
    ver, mods = modular_decomp(g)
    mx = 0
    graphs = []
    for mod in mods:
        graphs.append(g.subgraph(mod))
    mx_tww = 0
    for graph in graphs:
        if is_prime(g) and check_tww_1(1) == True:
            tww = 1
        else:
            tww = process(graph, encoder, preprocesses, solver_name)[0]
        if mx_tww < tww:
            mx_tww = tww
    mp = dict()
    mp_val = dict()
    for i, graph in enumerate(graphs):
        for v in list(graph.nodes):
            if v not in mp:
                mp[v] = i
                mp_val[v] = graph.number_of_nodes()
            elif mp_val[v] < graph.number_of_nodes():
                mp[v] = i
                mp_val[v] = graph.number_of_nodes()
    
    quotient = nx.Graph()
    for edg in g.edges:
        u, v = edg
        u = mp[u]+1
        v = mp[v]+1
        if u > v:
            c = u
            u = v
            v = c
        if u == v:      #same module
            continue
        if not quotient.has_edge(u, v):
            quotient.add_edge(u, v)
    
    tww = process(quotient, encoder, preprocesses, solver_name)[0]
    if mx_tww < tww:
        mx_tww = tww
    return mx_tww, []
