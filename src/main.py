import random
import json
import concurrent.futures
import numpy as np


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
    plot_regression,
    plot_surface_3d,
    plot_surface_3d_combined
)

from core.population import Population
from operators.selection import tournament_selection
from operators.crossover import subtree_crossover
from operators.mutation import subtree_mutation

def _run_single_experiment_from_task(task):
    """Función auxiliar para desempaquetar y ejecutar una corrida."""
    problem, function_set, terminal_set, problem_type, run_id, config = task
    
    # Importar funciones dentro del proceso worker
    if problem_type == 'boolean':
        functions = FUNCTIONS_BOOLEAN
    elif problem_type == 'regression':
        functions = FUNCTIONS_REGRESSION
    else:
        raise ValueError(f"Tipo de problema desconocido: {problem_type}")
    
    print(f"Iniciando corrida {run_id} con {function_set}")
    best, history = run_gp(
        problem,
        function_set,
        terminal_set,
        functions,
        population_size=config.get('population_size', 300),
        max_depth=config.get('max_depth', 7),
        crossover_rate=config.get('crossover_rate', 0.7),
        mutation_rate=config.get('mutation_rate', 0.2),
        generations=config.get('generations', 200)
    )
    return best, history

def tree_to_string(node):
    if isinstance(node.value, (int, float)):
        return str(round(node.value, 4))
    if not node.children:
        return node.value
    args = [tree_to_string(child) for child in node.children]
    return f"{node.value}({', '.join(args)})"


def count_tree_nodes(node):
    """Cuenta el número de nodos en un árbol."""
    if node is None:
        return 0
    return 1 + sum(count_tree_nodes(child) for child in node.children)


def calculate_population_stats(individuals):
    """Calcula estadísticas de la población."""
    fitness_values = [ind.fitness for ind in individuals]
    
    return {
        "min_fitness": min(fitness_values),
        "max_fitness": max(fitness_values),
        "avg_fitness": sum(fitness_values) / len(fitness_values),
        "variance": np.var(fitness_values),
        "std_dev": np.std(fitness_values)
    }


def run_gp(
    problem,
    function_set,
    terminal_set,
    functions,
    population_size=300,
    max_depth=7,
    crossover_rate=0.7,
    mutation_rate=0.2,
    generations=200,
    logger=None
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

        if logger is not None:
            logger(gen, population, best)

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
    config = {
        'population_size': 500,
        'max_depth': 8,
        'crossover_rate': 0.8,
        'mutation_rate': 0.2,
        'generations': 200
    }

    # Preparar tareas para paralelización
    tasks_F1 = [(problem, F1, T, 'boolean', i, config) for i in range(runs)]
    tasks_F2 = [(problem, F2, T, 'boolean', i, config) for i in range(runs)]

    histories_F1 = []
    histories_F2 = []
    best1 = None
    best2 = None

    # Ejecutar corridas de F1 en paralelo
    print("\n========== Corridas F1 en paralelo ==========")
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        results_F1 = list(executor.map(_run_single_experiment_from_task, tasks_F1))
    
    for best, history in results_F1:
        histories_F1.append(history)
        if best1 is None or best.fitness < best1.fitness:
            best1 = best

    # Ejecutar corridas de F2 en paralelo
    print("\n========== Corridas F2 en paralelo ==========")
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        results_F2 = list(executor.map(_run_single_experiment_from_task, tasks_F2))
    
    for best, history in results_F2:
        histories_F2.append(history)
        if best2 is None or best.fitness < best2.fitness:
            best2 = best

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


def run_regression(runs=1):
    problem = RegressionProblem("computo_genetico/data/symbolic_regression_2.csv")

    #F = ["+", "-", "*", "div", "sin", "cos", "log", "exp"]
    #F = ["+", "-", "*", "div", "sin", "cos"]
    F = ["+", "-", "*", "div", "sin", "cos", "abs", "scale", "half"]
    T = ["x", "y", "const"]
    
    config = {
        'population_size': 1000,
        'max_depth': 7,
        'crossover_rate': 0.8,
        'mutation_rate': 0.2,
        'generations': 200
    }

    if runs == 1:
        # Ejecución secuencial para una sola corrida
        history_log = []

        def logger(generation, population, best):
            # Calcular estadísticas de la población
            pop_stats = calculate_population_stats(population.individuals)
            
            # Tamaño del mejor árbol
            best_tree_size = count_tree_nodes(best.tree.root)
            
            # Información detallada del mejor individuo
            history_log.append({
                "generation": generation,
                "best_fitness": float(best.fitness),
                "avg_fitness": float(pop_stats["avg_fitness"]),
                "min_fitness": float(pop_stats["min_fitness"]),
                "max_fitness": float(pop_stats["max_fitness"]),
                "variance": float(pop_stats["variance"]),
                "std_dev": float(pop_stats["std_dev"]),
                "best_tree_size": best_tree_size,
                "expression": tree_to_string(best.tree.root),
                "convergence_rate": abs(pop_stats["min_fitness"] - pop_stats["max_fitness"]) / (pop_stats["max_fitness"] + 1e-10)
            })
            if generation % 10 == 0:
                print(f"Gen {generation}: best={best.fitness:.6f}, avg={pop_stats['avg_fitness']:.6f}, "
                      f"tree_size={best_tree_size}, variance={pop_stats['variance']:.6f}")

        best, history = run_gp(
            problem,
            F,
            T,
            FUNCTIONS_REGRESSION,
            population_size=config['population_size'],
            max_depth=config['max_depth'],
            generations=config['generations'],
            crossover_rate=config['crossover_rate'],
            mutation_rate=config['mutation_rate'],
            logger=logger 
        )
        with open("gp_history.json", "w") as f:
            json.dump(history_log, f, indent=4)
        
        print("\nBest final:")
        print(f"Fitness: {best.fitness}")
        print(f"Expr: {tree_to_string(best.tree.root)}")
        print(f"Tree size: {count_tree_nodes(best.tree.root)} nodes")

        print("\nResultado Regresión:")
        print("Expresión:", best.tree)
        print("MSE:", best.fitness)

        plot_fitness(history, "Regresión simbólica", "regression.png")
        plot_regression(best.tree, problem.data, "Modelo vs datos", "regression_fit.png")
        
        # Nueva: Visualización 3D de superficies
        print("\nGenerando visualización 3D...")
        error_stats = plot_surface_3d(
            best.tree, 
            problem.data, 
            title="Regresión Simbólica: Superficie Real vs Predicha",
            filename="regression_surface_3d.png"
        )
        
        if error_stats:
            print("\nEstadísticas de Error en Superficie:")
            print(f"  MSE: {error_stats['mse']:.6f}")
            print(f"  RMSE: {error_stats['rmse']:.6f}")
            print(f"  MAE: {error_stats['mae']:.6f}")
            print(f"  Max Error: {error_stats['max_error']:.6f}")
            print(f"  Min Error: {error_stats['min_error']:.6f}")
        
        # Alternativa: Comparación lado a lado
        plot_surface_3d_combined(
            best.tree,
            problem.data,
            title="Comparación: Datos vs Modelo",
            filename="regression_surface_comparison.png"
        )
    else:
        # Paralelización para múltiples corridas
        tasks = [(problem, F, T, 'regression', i, config) for i in range(runs)]
        histories = []
        all_results = []
        best_overall = None

        print(f"\n========== Ejecutando {runs} corridas en paralelo ==========")
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(_run_single_experiment_from_task, tasks))
        
        for run_id, (best, history) in enumerate(results):
            histories.append(history)
            all_results.append({
                "run_id": run_id,
                "best_fitness": float(best.fitness),
                "tree_size": count_tree_nodes(best.tree.root),
                "expression": tree_to_string(best.tree.root),
                "final_history": history
            })
            if best_overall is None or best.fitness < best_overall.fitness:
                best_overall = best
        
        avg_history = average_histories(histories)
        
        # Guardar en JSON con información consolidada
        history_log = {
            "runs": runs,
            "config": config,
            "best_overall": {
                "fitness": float(best_overall.fitness),
                "tree_size": count_tree_nodes(best_overall.tree.root),
                "expression": tree_to_string(best_overall.tree.root)
            },
            "average_history": avg_history,
            "individual_runs": all_results
        }
        
        with open("gp_history.json", "w") as f:
            json.dump(history_log, f, indent=4)
        
        print(f"\n========== RESULTADOS: Mejor de {runs} corridas ==========")
        print(f"Fitness: {best_overall.fitness}")
        print(f"Expr: {tree_to_string(best_overall.tree.root)}")
        print(f"Tree size: {count_tree_nodes(best_overall.tree.root)} nodes")

        plot_fitness(avg_history, "Regresión simbólica promedio", "regression_avg.png")
        plot_regression(best_overall.tree, problem.data, "Modelo vs datos", "regression_fit.png")
        
        # Nueva: Visualización 3D de superficies para el mejor modelo
        print("\nGenerando visualización 3D del mejor modelo...")
        error_stats = plot_surface_3d(
            best_overall.tree, 
            problem.data, 
            title=f"Mejor de {runs} corridas: Superficie Real vs Predicha",
            filename="regression_surface_3d.png"
        )
        
        if error_stats:
            print("\nEstadísticas de Error en Superficie:")
            print(f"  MSE: {error_stats['mse']:.6f}")
            print(f"  RMSE: {error_stats['rmse']:.6f}")
            print(f"  MAE: {error_stats['mae']:.6f}")
            print(f"  Max Error: {error_stats['max_error']:.6f}")
            print(f"  Min Error: {error_stats['min_error']:.6f}")
        
        plot_surface_3d_combined(
            best_overall.tree,
            problem.data,
            title="Mejor Modelo: Datos vs Predicción",
            filename="regression_surface_comparison.png"
        )




def main():
    #print("\n===== PROBLEMA BOOLEANO =====")
    #run_boolean()

    print("\n===== REGRESIÓN SIMBÓLICA =====")
    run_regression(runs=4)  


if __name__ == "__main__":
    main()


