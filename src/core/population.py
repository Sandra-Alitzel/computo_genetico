from core.tree import Tree
from core.individual import Individual

class Population:
    def __init__(self, size, function_set, terminal_set, max_depth):
        self.size = size
        self.function_set = function_set
        self.terminal_set = terminal_set
        self.max_depth = max_depth

        self.individuals = self.initialize()

    def initialize(self):
        return [
            Individual(
                Tree(self.function_set, self.terminal_set, self.max_depth)
            )
            for _ in range(self.size)
        ]

    def evaluate(self, problem):
        for individual in self.individuals:
            individual.evaluate(problem)

    def get_best(self):
        return min(self.individuals, key=lambda ind: ind.fitness)

