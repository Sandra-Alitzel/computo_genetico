from core.population import Population
from problems.boolean_problem import BooleanProblem
from operators.selection import tournament_selection


def main():
    F1 = ["AND", "OR", "NOT"]
    T = ["A", "B", "C", 0, 1]


    problem = BooleanProblem("data/TablaParidad.csv")


    population = Population(
        size=20,
        function_set=F1,
        terminal_set=T,
        max_depth=3
    )


    # 🔹 AQUÍ se define evaluated
    evaluated = population.evaluate(problem)


    # 🔹 ahora sí puedes usarlo
    selected = tournament_selection(evaluated, k=3)


    print("Seleccionado:")
    print(selected)


if __name__ == "__main__":
    main()



