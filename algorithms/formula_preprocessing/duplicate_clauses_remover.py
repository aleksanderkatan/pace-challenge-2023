from algorithms.formula_preprocessing.abstract_preprocessing_algorithm import AbstractPreprocessingAlgorithm


class DuplicateClauseRemover(AbstractPreprocessingAlgorithm):
    def __init__(self):
        self.formula = None

    # has to be multiple use
    def initialize_with_formula(self, formula):
        self.formula = formula

    def preprocess_formula(self):
        return self.formula

    def reprocess_result(self, result):
        return result
