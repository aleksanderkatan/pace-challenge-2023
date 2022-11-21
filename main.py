from file_utility.directory_reader import DirectoryReader
from file_utility.graph_scanner import GraphScanner
from algorithms.relative_encoding.relative_encoding_algorithm import RelativeEncodingAlgorithm
from algorithms.sequence_verifier import SequenceVerifier

INSTANCES_PATH = "instances"


if __name__ == '__main__':
    # TODO: implement modular decomposition
    files_data = DirectoryReader().read(INSTANCES_PATH)
    graph_scanner = GraphScanner()
    algorithm = RelativeEncodingAlgorithm()
    sequence_verifier = SequenceVerifier()

    for file_data in files_data:
        file_content, file_name = file_data
        graph, twinwidth = graph_scanner.read_graph(file_content)
        sequence = algorithm.__process__(graph)
        sequence_width = sequence_verifier.calculate_twinwidth(graph, sequence)

        if sequence_width != twinwidth:
            print(f"Actual twinwidth {twinwidth} is not equal to the width of the sequence {sequence_width} "
                  f"for file {file_name}")
