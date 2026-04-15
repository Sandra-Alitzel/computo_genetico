import random

def tournament_selection(population, k=3):
    participants = random.sample(population, k)
    return min(participants, key=lambda ind: ind.fitness)

