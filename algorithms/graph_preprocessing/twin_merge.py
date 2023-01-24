import networkx


class TwinMerge:
    def __init__(self, graph: networkx.Graph):
        self.graph = graph

    def get_encoded(self):
        return self.graph

    def get_decoded(self, sequence):
        return sequence
