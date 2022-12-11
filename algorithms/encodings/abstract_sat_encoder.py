import abc
import networkx as nx


# let's try and imitate an interface in python...
class AbstractSatEncoder(abc.ABC):
    @abc.abstractmethod
    def initialize_with_graph(self, graph: nx.Graph, tww):
        pass

    @abc.abstractmethod
    def encode(self):
        pass

    @abc.abstractmethod
    def decode(self, model: list[int]):
        pass
