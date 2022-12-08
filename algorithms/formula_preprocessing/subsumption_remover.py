from algorithms.formula_preprocessing.abstract_preprocessing_algorithm import AbstractPreprocessingAlgorithm
from pysat.formula import CNFPlus


def _contains(smaller_clause, bigger_clause):
    if len(smaller_clause) > len(bigger_clause):
        return False
    bigger = {var for var in bigger_clause}
    for var in smaller_clause:
        if var not in bigger:
            return False
    return True


# removes formulas that are contained within other.
# eg. for [x, y] v [x, y, -z], the first formula will be removed
# IS UNUSABLE IN PRACTICE
class SubsumptionRemover(AbstractPreprocessingAlgorithm):
    def __init__(self):
        self.formula = None

    # has to be multiple use
    def initialize_with_formula(self, formula):
        self.formula = formula

    def preprocess_formula(self):
        assert issubclass(type(self.formula), CNFPlus)
        clauses_number = len(self.formula.clauses)
        indices_to_remove = set()
        for i in range(clauses_number):
            for j in range(i+1, clauses_number):
                clause = self.formula.clauses[i]
                other = self.formula.clauses[j]
                if _contains(clause, other):
                    indices_to_remove.add(j)
                elif _contains(other, clause):
                    indices_to_remove.add(i)

        new_formula = CNFPlus()
        new_clauses = [clause for i, clause in enumerate(self.formula.clauses) if i not in indices_to_remove]
        for clause in new_clauses:
            new_formula.append(clause)
        for at_most_clause in self.formula.atmosts:
            new_formula.append(at_most_clause, is_atmost=True)
        print(f"SubsumptionRemover shortened clauses from {len(self.formula.clauses)} to {len(new_formula.clauses)}")

        return new_formula

    def reprocess_result(self, result):
        return result
