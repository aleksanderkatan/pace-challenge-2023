from algorithms.graph_preprocessing.twin_merge import TwinMerge
import networkx


def graph_preprocessing_wrapper(graph: networkx.Graph, solve_simplified_graph):
    # return solve_simplified_graph(graph)

    twin_merge_preprocessor = TwinMerge(graph)
    graph_without_twins = twin_merge_preprocessor.get_encoded()

    tww, sequence = solve_simplified_graph(graph_without_twins)

    return tww, twin_merge_preprocessor.get_decoded(sequence)
