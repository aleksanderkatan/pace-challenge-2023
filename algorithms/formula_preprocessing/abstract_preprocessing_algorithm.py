import abc


# let's try and imitate an interface in python...
class AbstractPreprocessingAlgorithm(abc.ABC):
    @abc.abstractmethod
    def initialize_with_formula(self, formula):
        pass

    @abc.abstractmethod
    def preprocess_formula(self):
        pass

    @abc.abstractmethod
    def reprocess_result(self, result):
        pass
