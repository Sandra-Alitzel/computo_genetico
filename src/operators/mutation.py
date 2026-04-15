import random
import copy
from core.tree import Tree
from core.individual import Individual

def subtree_mutation(individual, function_set, terminal_set, functions, max_depth):
    tree_copy = copy.deepcopy(individual.tree)

    nodes = tree_copy.root.get_all_nodes()
    mutation_point = random.choice(nodes)

    new_subtree = Tree(
        function_set,
        terminal_set,
        functions,   # 👈 clave
        max_depth
    ).root

    new_root = tree_copy.root.replace_node(mutation_point, new_subtree)
    tree_copy.root = new_root

    return Individual(tree_copy)

