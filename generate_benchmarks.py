from algorithms.graph_preprocessing_wrapper import graph_preprocessing_wrapper
from algorithms.encodings.relative_sat_encoder import RelativeSatEncoder
from algorithms.down_up_sat_checker import process

# from algorithms.ilp_checker import process
from algorithms.other.helpers import read_graph
import os
import time
import func_timeout

INSTANCES_PATH = 'benchmark_instances'
TIMEOUT = 2


def preprocess_base_graph(g):
    return process(g, RelativeSatEncoder(), [], "cadical")


if __name__ == '__main__':
    file_names = os.listdir(INSTANCES_PATH)
    for file_name in sorted(file_names):
        file_path = os.path.join(INSTANCES_PATH, file_name)
        graph = read_graph(file_path)

        print(f"{file_path}: ", end="")
        start_time = time.time()
        try:
            tww, sequence = func_timeout.func_timeout(TIMEOUT,
                                                      lambda: graph_preprocessing_wrapper(graph, preprocess_base_graph))
                                                      # lambda: process(graph, pywraplp.Solver.CreateSolver("SCIP")))
            print(f"time: {time.time() - start_time}, twinwidth: {tww}")
        except func_timeout.FunctionTimedOut:
            print(f"timeout (>{TIMEOUT})")
