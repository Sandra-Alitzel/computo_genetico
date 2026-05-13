import random
import copy
from core.individual import Individual

def subtree_crossover(parent1, parent2):
    p1 = copy.deepcopy(parent1.tree)
    p2 = copy.deepcopy(parent2.tree)

    nodes1 = p1.root.get_all_nodes()
    nodes2 = p2.root.get_all_nodes()

    n1 = random.choice(nodes1)
    n2 = random.choice(nodes2)

    new_root1 = p1.root.replace_node(n1, copy.deepcopy(n2))
    new_root2 = p2.root.replace_node(n2, copy.deepcopy(n1))

    p1.root = new_root1
    p2.root = new_root2

    return Individual(p1), Individual(p2)

