import random
import math


def tournament_selection(population, k=7):
    participants = random.sample(population, min(k, len(population)))
    return min(participants, key=lambda ind: ind.fitness)


def boltzmann_selection(population, temperature=1.0):
    """
    Selección de Boltzmann para minimización.
    Temperatura baja = mayor presión selectiva hacia el mejor individuo.
    Temperatura alta = selección casi uniforme.
    weight_i = exp(-(fitness_i - fitness_min) / T)
    """
    T = max(temperature, 1e-10)
    fitnesses = [ind.fitness for ind in population]
    min_f = min(fitnesses)
    weights = []
    for f in fitnesses:
        exponent = max(-(f - min_f) / T, -500)  # evitar underflow
        weights.append(math.exp(exponent))
    return random.choices(population, weights=weights)[0]


def rank_selection(population):
    """
    Selección por rango lineal (Vasconcelos).
    El mejor individuo recibe el mayor peso (rank n), el peor el menor (rank 1).
    Reduce la dominancia de individuos muy aptos y mantiene diversidad.
    """
    n = len(population)
    sorted_pop = sorted(population, key=lambda ind: ind.fitness)
    weights = list(range(1, n + 1))  # rank 1 = peor, rank n = mejor
    return random.choices(sorted_pop, weights=weights)[0]


def select(population, method, temperature=1.0, k=7):
    """Despachador unificado de selección."""
    if method == "Torneo":
        return tournament_selection(population, k)
    elif method == "Boltzmann":
        return boltzmann_selection(population, temperature)
    elif method == "Vasconcelos":
        return rank_selection(population)
    return tournament_selection(population, k)
