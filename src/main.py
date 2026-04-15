import random


from problems.boolean_problem import BooleanProblem
from problems.regression_problem import RegressionProblem

from utils.functions_boolean import FUNCTIONS_BOOLEAN
from utils.functions_regression import FUNCTIONS_REGRESSION

from utils.analysis import average_histories, count_functions, tree_size
from utils.plotting import (
    plot_fitness,
    plot_comparison,
    plot_average,
    plot_function_frequency,
    plot_tree_sizes,
    plot_regression
)

from core.population import Population
from operators.selection import tournament_selection
from operators.crossover import subtree_crossover
from operators.mutation import subtree_mutation


def run_gp(
    problem,
    function_set,
    terminal_set,
    functions,
    population_size=50,
    max_depth=3,
    crossover_rate=0.7,
    mutation_rate=0.1,
    generations=30
):
    population = Population(
        population_size,
        function_set,
        terminal_set,
        functions,
        max_depth
    )

    best_overall = None
    fitness_history = []

    for gen in range(generations):

        population.evaluate(problem)
        population.individuals.sort(key=lambda ind: ind.fitness)

        best = population.individuals[0]
        fitness_history.append(best.fitness)

        print(f"Generación {gen} | Mejor fitness: {best.fitness} | {best.tree}")

        if best_overall is None or best.fitness < best_overall.fitness:
            best_overall = best

        new_individuals = []

        while len(new_individuals) < population_size:

            parent1 = tournament_selection(population.individuals)
            parent2 = tournament_selection(population.individuals)

            if random.random() < crossover_rate:
                child1, child2 = subtree_crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2

            if random.random() < mutation_rate:
                child1 = subtree_mutation(
                    child1,
                    function_set,
                    terminal_set,
                    functions,
                    max_depth
                )

            if random.random() < mutation_rate:
                child2 = subtree_mutation(
                    child2,
                    function_set,
                    terminal_set,
                    functions,
                    max_depth
                )

            new_individuals.append(child1)

            if len(new_individuals) < population_size:
                new_individuals.append(child2)

        population.individuals = new_individuals

    return best_overall, fitness_history


def run_boolean():
    problem = BooleanProblem("computo_genetico/data/TablaParidad.csv")

    F1 = ["AND", "OR", "NOT"]
    F2 = ["AND", "OR", "NOT", "XOR"]

    T = ["A", "B", "C", 0, 1]

    runs = 5

    histories_F1 = []
    histories_F2 = []

    best1 = None
    best2 = None

    for i in range(runs):
        print(f"\nCorrida {i+1} F1")
        best1, h1 = run_gp(problem, F1, T, FUNCTIONS_BOOLEAN)
        histories_F1.append(h1)

        print(f"\nCorrida {i+1} F2")
        best2, h2 = run_gp(problem, F2, T, FUNCTIONS_BOOLEAN)
        histories_F2.append(h2)

    avg_F1 = average_histories(histories_F1)
    avg_F2 = average_histories(histories_F2)

    print("\nResultados Booleanos:")
    print("F1:", best1.tree, best1.fitness)
    print("F2:", best2.tree, best2.fitness)

    plot_fitness(avg_F1, "F1 promedio", "f1_avg.png")
    plot_fitness(avg_F2, "F2 promedio", "f2_avg.png")
    plot_comparison(avg_F1, avg_F2, "F1", "F2", "comparison.png")

    counter_F1 = count_functions(best1.tree.root)
    counter_F2 = count_functions(best2.tree.root)

    plot_function_frequency(counter_F1)
    plot_function_frequency(counter_F2)

    size_F1 = tree_size(best1.tree.root)
    size_F2 = tree_size(best2.tree.root)

    plot_tree_sizes(size_F1, size_F2)


def run_regression():
    problem = RegressionProblem("computo_genetico/data/RegSymb_v1.csv")

    F = ["+", "-", "*", "div", "sin", "cos", "log", "exp"]
    T = ["x", 1.0, -1.0, 2.0]

    best, history = run_gp(
        problem,
        F,
        T,
        FUNCTIONS_REGRESSION,
        population_size=100,
        max_depth=6,
        generations=50
    )

    print("\nResultado Regresión:")
    print("Expresión:", best.tree)
    print("MSE:", best.fitness)

    plot_fitness(history, "Regresión simbólica", "regression.png")
    plot_regression(best.tree, problem.data, "Modelo vs datos", "regression_fit.png")




def main():
    print("\n===== PROBLEMA BOOLEANO =====")
    run_boolean()

    print("\n===== REGRESIÓN SIMBÓLICA =====")
    run_regression()


if __name__ == "__main__":
    main()


