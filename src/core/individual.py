class Individual:
    def __init__(self, tree):
        self.tree = tree
        self.fitness = None

    def evaluate(self, problem):
        self.fitness = problem.fitness(self.tree)

    def __str__(self):
        return f"{self.tree} | fitness: {self.fitness}"
