import random
from core.population import Population
from operators.selection import tournament_selection
from operators.crossover import subtree_crossover
from operators.mutation import subtree_mutation

class GeneticProgramming:
    def __init__(
        self,
        population_size,
        function_set,
        terminal_set,
        max_depth,
        crossover_rate,
        mutation_rate,
        generations
    ):
        self.population_size = population_size
        self.function_set = function_set
        self.terminal_set = terminal_set
        self.max_depth = max_depth
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.generations = generations

    def run(self, problem):
        population = Population(
            self.population_size,
            self.function_set,
            self.terminal_set,
            self.max_depth
        )

        best_overall = None

        for gen in range(self.generations):

            # 🔹 EVALUAR
            population.evaluate(problem)

            # 🔹 ORDENAR (YA TODOS tienen fitness)
            population.individuals.sort(key=lambda ind: ind.fitness)

            best = population.individuals[0]

            print(f"Generación {gen} | Mejor fitness: {best.fitness} | {best.tree}")

            # 🔹 GUARDAR MEJOR
            if best_overall is None or best.fitness < best_overall.fitness:
                best_overall = best

            # 🔹 NUEVA GENERACIÓN
            new_individuals = []

            while len(new_individuals) < self.population_size:

                parent1 = tournament_selection(population.individuals)
                parent2 = tournament_selection(population.individuals)

                if random.random() < self.crossover_rate:
                    child1, child2 = subtree_crossover(parent1, parent2)
                else:
                    child1, child2 = parent1, parent2

                if random.random() < self.mutation_rate:
                    child1 = subtree_mutation(
                        child1,
                        self.function_set,
                        self.terminal_set,
                        self.max_depth
                    )

                if random.random() < self.mutation_rate:
                    child2 = subtree_mutation(
                        child2,
                        self.function_set,
                        self.terminal_set,
                        self.max_depth
                    )

                new_individuals.append(child1)

                if len(new_individuals) < self.population_size:
                    new_individuals.append(child2)

            population.individuals = new_individuals

        return best_overall

