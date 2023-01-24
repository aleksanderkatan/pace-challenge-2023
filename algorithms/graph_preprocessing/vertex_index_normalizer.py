import networkx


# makes it so graph vertices are from 1 to n
class VertexIndexNormalizer:
    def __init__(self, graph: networkx.Graph):
        self.graph = graph
        self.normalized_graph = networkx.Graph()

        self.normalized_indices = {}
        self.denormalized_indices = {}

        for vertex in graph.nodes:
            self.normalized_indices[vertex] = len(self.normalized_indices) + 1
            self.denormalized_indices[self.normalized_indices[vertex]] = vertex

        for u, v in self.graph.edges:
            self.normalized_graph.add_edge(self.normalized_indices[u], self.normalized_indices[v])


    def get_normalized(self):
        return self.normalized_graph

    def denormalize_sequence(self, sequence):
        return [(self.denormalized_indices[u], self.denormalized_indices[v]) for u, v in sequence]
