import math

# Funciones nombradas (serializables con pickle) en lugar de lambdas
def boolean_and(a, b):
    return int(a and b)

def boolean_or(a, b):
    return int(a or b)

def boolean_not(a):
    return int(not a)

def boolean_xor(a, b):
    return a ^ b

FUNCTIONS_BOOLEAN = {
    "AND": {"arity": 2, "function": boolean_and},
    "OR": {"arity": 2, "function": boolean_or},
    "NOT": {"arity": 1, "function": boolean_not},
    "XOR": {"arity": 2, "function": boolean_xor},
}

