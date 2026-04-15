import random


def tournament_selection(evaluated_population, k=3):
    """
    evaluated_population: lista de (tree, fitness)
    fitness = errores → menor es mejor
    """


    # elegir k individuos al azar
    participants = random.sample(evaluated_population, k)


    # elegir el mejor (MENOR fitness)
    best = min(participants, key=lambda x: x[1])


    return best[0]  # regresamos solo el árbol



