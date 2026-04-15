from utils.functions import FUNCTIONS

class Node:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children or []

    def is_leaf(self):
        return len(self.children) == 0

    def evaluate(self, context):
        if self.is_leaf():
            if isinstance(self.value, str):
                return context[self.value]
            return self.value

        args = [child.evaluate(context) for child in self.children]

        func = FUNCTIONS[self.value]["function"]
        return func(*args)

    def get_all_nodes(self):
        nodes = [self]
        for child in self.children:
            nodes.extend(child.get_all_nodes())
        return nodes

    def replace_node(self, target, replacement):
        if self is target:
            return replacement

        new_children = []
        for child in self.children:
            new_child = child.replace_node(target, replacement)
            new_children.append(new_child)

        self.children = new_children
        return self

    def __str__(self):
        if self.is_leaf():
            return str(self.value)
        return f"{self.value}({', '.join(str(child) for child in self.children)})"


