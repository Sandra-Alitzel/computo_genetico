import math


class SumProblem:
    """Target: tree() == target. Fitness = |tree() - target|. No parsimony."""

    def __init__(self, target=10):
        self.target = target

    def fitness(self, tree):
        try:
            result = tree.evaluate({})
            if not isinstance(result, (int, float)) or math.isnan(result) or math.isinf(result):
                return 1e6
            return abs(result - self.target)
        except Exception:
            return 1e6
