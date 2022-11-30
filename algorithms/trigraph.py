import networkx as nx


class Vertex:
    def __init__(self, indices):
        self.indices = indices

    def merge_with(self, other):
        return Vertex(self.indices.union(other.indices))



class Trigraph:
    def __init__(self, graph: nx.Graph):
        n = len(graph.nodes)
        self.vertices = {Vertex({i}) for i in range(1, n+1)}
        edges = {vertex: {} for vertex in self.vertices}
        for u, v in graph.edges:
            vertex_u = self._find_vertex(u)
            vertex_v = self._find_vertex(v)
            edges[vertex_u][vertex_v] = "BLACK"
            edges[vertex_v][vertex_u] = "BLACK"

        self.edges = edges

    def merge(self, u, v):
        vertex_u = self._find_vertex(u)
        vertex_v = self._find_vertex(v)
        u_edges = self.edges[vertex_u]
        v_edges = self.edges[vertex_v]

        # add new
        merged_vertex = vertex_u.merge_with(vertex_v)
        self.vertices.add(merged_vertex)

        # fill edges
        edges_from_merged = {}
        combined_neighbourhood = {k for k in u_edges.keys()}.union({k for k in v_edges.keys()})
        for vertex in combined_neighbourhood:
            if vertex not in u_edges or vertex not in v_edges:
                edges_from_merged[vertex] = "RED"
            elif u_edges[vertex] == "RED" or v_edges[vertex] == "RED":
                edges_from_merged[vertex] = "RED"
            else:
                edges_from_merged[vertex] = "BLACK"
            self.edges[vertex][merged_vertex] = edges_from_merged[vertex]
        self.edges[merged_vertex] = edges_from_merged

        # remove old
        self._remove_vertex(vertex_u)
        self._remove_vertex(vertex_v)

    def _remove_vertex(self, v):
        self.vertices.remove(v)
        del self.edges[v]
        for vertex in self.vertices:
            if v in self.edges[vertex]:
                del self.edges[vertex][v]

    def _find_vertex(self, v):
        for vertex in self.vertices:
            if v in vertex.indices:
                return vertex
        raise RuntimeError("Vertex not found")

    def max_red_degree(self):
        m = 0
        for vertex in self.vertices:
            m = max(m, len([1 for vertex, color in self.edges[vertex].items() if color == "RED"]))
        return m
