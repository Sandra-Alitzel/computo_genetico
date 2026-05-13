import random
import copy
from core.tree import Tree
from core.individual import Individual


def subtree_mutation(individual, function_set, terminal_set, functions, max_depth):
    """Mutación por rama: reemplaza un subárbol aleatorio con uno nuevo aleatorio."""
    tree_copy = copy.deepcopy(individual.tree)
    nodes = tree_copy.root.get_all_nodes()
    mutation_point = random.choice(nodes)
    new_subtree = Tree(function_set, terminal_set, functions, max_depth).root
    tree_copy.root = tree_copy.root.replace_node(mutation_point, new_subtree)
    return Individual(tree_copy)


def node_mutation(individual, terminal_set, functions):
    """Mutación por nodo: reemplaza un nodo hoja aleatorio con otro terminal."""
    tree_copy = copy.deepcopy(individual.tree)
    nodes = tree_copy.root.get_all_nodes()
    leaf_nodes = [n for n in nodes if n.is_leaf()]
    if not leaf_nodes:
        return Individual(tree_copy)
    target = random.choice(leaf_nodes)
    new_value = random.choice(terminal_set)
    target.value = new_value
    return Individual(tree_copy)


def mutate_constant(node):
    if isinstance(node.value, float):
        node.value += random.uniform(-1, 1)
    for child in node.children:
        mutate_constant(child)
