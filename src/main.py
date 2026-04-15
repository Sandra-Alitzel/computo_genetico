from core.genetic_programming import GeneticProgramming
from problems.boolean_problem import BooleanProblem

def run_experiment(function_set, label):
    problem = BooleanProblem("data/TablaParidad.csv")

    gp = GeneticProgramming(
        population_size=50,
        function_set=function_set,
        terminal_set=["A", "B", "C", 0, 1],
        max_depth=5,
        crossover_rate=0.9,
        mutation_rate=0.3,
        generations=30
    )

    best = gp.run(problem)

    print(f"\nRESULTADO {label}:")
    print("Mejor árbol:", best.tree)
    print("Fitness:", best.fitness)

    return best.fitness

def main():
    F1 = ["AND", "OR", "NOT"]
    F2 = ["AND", "OR", "NOT", "XOR"]

    runs = 5

    results_F1 = []
    results_F2 = []

    print("\n===== F1 =====")
    for i in range(runs):
        print(f"\n--- Corrida {i+1} ---")
        fitness = run_experiment(F1, "F1")
        results_F1.append(fitness)

    print("\n===== F2 =====")
    for i in range(runs):
        print(f"\n--- Corrida {i+1} ---")
        fitness = run_experiment(F2, "F2")
        results_F2.append(fitness)

    print("\n===== RESUMEN =====")
    print("F1:", results_F1)
    print("F2:", results_F2)

    print("\nPromedio F1:", sum(results_F1) / len(results_F1))
    print("Promedio F2:", sum(results_F2) / len(results_F2))


if __name__ == "__main__":
    main()
