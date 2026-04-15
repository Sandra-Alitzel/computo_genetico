import random
from core.tree import Tree


class Population:
    def __init__(self, size, function_set, terminal_set, max_depth):
        self.size = size
        self.function_set = function_set
        self.terminal_set = terminal_set
        self.max_depth = max_depth


        self.individuals = self.initialize()


    def initialize(self):
        return [
            Tree(self.function_set, self.terminal_set, self.max_depth)
            for _ in range(self.size)
        ]


    def evaluate(self, problem):
        """
        Evalúa todos los individuos y guarda su fitness
        """
        results = []


        for tree in self.individuals:
            fitness = problem.fitness(tree)
            results.append((tree, fitness))


        return results


    def get_best(self, evaluated_population):
        """
        Devuelve el mejor individuo
        """
        return max(evaluated_population, key=lambda x: x[1])



