def average_histories(histories):
    """
    histories: lista de listas
    """
    min_len = min(len(h) for h in histories)

    trimmed = [h[:min_len] for h in histories]

    avg = [
        sum(values) / len(values)
        for values in zip(*trimmed)
    ]

    return avg

from collections import defaultdict

def count_functions(node, counter=None):
    if counter is None:
        counter = defaultdict(int)

    if isinstance(node.value, str):
        counter[node.value] += 1

    for child in node.children:
        count_functions(child, counter)

    return counter
def tree_size(node):
    return 1 + sum(tree_size(child) for child in node.children)


