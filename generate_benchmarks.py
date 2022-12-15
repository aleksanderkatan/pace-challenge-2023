import networkx as nx

from algorithms.encodings.relative_sat_encoder import RelativeSatEncoder
from algorithms.down_up_sat_checker import process
from algorithms.helpers import read_graph
import os
import time
import multiprocessing.pool
import functools


def timeout(max_timeout):
    """Timeout decorator, parameter in seconds."""

    def timeout_decorator(item):
        """Wrap the original function."""

        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            # raises a TimeoutError if execution exceeds max_timeout
            return async_result.get(max_timeout)

        return func_wrapper

    return timeout_decorator


INSTANCES_PATH = 'benchmark_instances'
TIMEOUT = 120


@timeout(TIMEOUT)
def run_algorithm(graph: nx.Graph):
    return process(graph, RelativeSatEncoder(), [], "cadical")


if __name__ == '__main__':
    file_names = os.listdir(INSTANCES_PATH)
    for file_name in sorted(file_names):
        file_path = os.path.join(INSTANCES_PATH, file_name)
        graph = read_graph(file_path)

        print(f"{file_path}: ", end="")
        start_time = time.time()
        try:
            tww, sequence = run_algorithm(graph)
            print(f"time: {time.time() - start_time}, twinwidth: {tww}")
        except multiprocessing.context.TimeoutError:
            print(f"timeout (>{TIMEOUT})")
