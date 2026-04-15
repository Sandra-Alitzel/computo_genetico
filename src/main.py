from core.genetic_programming import GeneticProgramming
from problems.boolean_problem import BooleanProblem

def main():
    F1 = ["AND", "OR", "NOT"]
    T = ["A", "B", "C", 0, 1]

    problem = BooleanProblem("computo_genetico/data/TablaParidad.csv")

    gp = GeneticProgramming(
        population_size=50,
        function_set=F1,
        terminal_set=T,
        max_depth=5,
        crossover_rate=0.9,
        mutation_rate=0.3,
        generations=30
    )

    best = gp.run(problem)

    print("\nMEJOR SOLUCIÓN FINAL:")
    print(best.tree)
    print("Fitness:", best.fitness)

if __name__ == "__main__":
    main()

