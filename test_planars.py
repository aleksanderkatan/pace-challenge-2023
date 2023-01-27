from algorithms.down_up_sat_checker import process_modules, process, process_from_top
from algorithms.encodings.relative_sat_encoder import RelativeSatEncoder
from algorithms.graph_preprocessing_wrapper import graph_preprocessing_wrapper
import networkx
import os

instances_path = "plantri/planar/"
vertices_to_check = [i for i in range(12, 25+1)]


def _get_file_name(v):
    return f"planar_graphs_{v}.txt"


# eg.
# 12 bcdef,afghc,abhid,acije,adjkf,aekgb,bfklh,bglic,chljd,dilke,ejlgf,gkjih
def _scan_graph(graph_string: str) -> networkx.Graph:
    result = networkx.Graph()
    vertices, rest = graph_string.split(" ")
    vertices = int(vertices)

    result.add_nodes_from([i + 1 for i in range(vertices)])

    for out_vertex, edges in enumerate(rest.split(","), start=1):
        for in_vertex in edges:
            result.add_edge(out_vertex, _string_vertex_to_nx_vertex(in_vertex))

    return result


def _string_vertex_to_nx_vertex(v):
    return ord(v) - ord("a") + 1


def preprocess_base_graph(g):
    # return process_modules(g, RelativeSatEncoder(), [], "cadical")
    return process_from_top(g, RelativeSatEncoder(), [], "cadical")
    # return process(g, RelativeSatEncoder(), [], "cadical")


print(f"Planar graphs with min degree 5")
for v in vertices_to_check:
    file_path = os.path.join(instances_path, _get_file_name(v))

    max_tww = 0
    graph_with_max_tww = None
    with open(file_path, "r") as file:
        for line in file:
            graph = _scan_graph(line)
            tww, sequence = graph_preprocessing_wrapper(graph, preprocess_base_graph)
            if tww > max_tww:
                max_tww = tww
                graph_with_max_tww = line

    if graph_with_max_tww is not None:
        print(f"{v} vertices - max tww is {max_tww} for {graph_with_max_tww.strip()}")
    else:
        print(f"{v} vertices - no such graphs")


