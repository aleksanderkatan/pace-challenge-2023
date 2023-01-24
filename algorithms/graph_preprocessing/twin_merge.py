import networkx
from algorithms.graph_preprocessing.vertex_index_normalizer import VertexIndexNormalizer

# merges twins as long as they exist
class TwinMerge:
    def __init__(self, graph: networkx.Graph):
        self.graph = graph
        self.merged_graph = self.graph.copy()
        self.merges = []

        while len(self.merged_graph.nodes) > 1:
            success = False
            # we can't do set hashing, because nodes can be neighbours
            for u in self.merged_graph.nodes:
                for v in self.merged_graph.nodes:
                    if u == v:
                        continue

                    u_neighbours = set(self.merged_graph.neighbors(u))
                    if v in u_neighbours:
                        u_neighbours.remove(v)
                    v_neighbours = set(self.merged_graph.neighbors(v))
                    if u in v_neighbours:
                        v_neighbours.remove(u)

                    if u_neighbours == v_neighbours:
                        self.merged_graph.remove_node(u)
                        self.merges.append((u, v))
                        success = True

                    # programming art
                    if success:
                        break
                if success:
                    break
            if not success:
                break

        self.normalizer = VertexIndexNormalizer(self.merged_graph)


    def get_encoded(self):
        return self.normalizer.get_normalized()

    def get_decoded(self, sequence):
        denormalized_sequence = self.normalizer.denormalize_sequence(sequence)
        return self.merges + denormalized_sequence

