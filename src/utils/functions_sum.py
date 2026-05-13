def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

FUNCTIONS_EXP1 = {
    "+": {"arity": 2, "function": add},
}

FUNCTIONS_EXP2 = {
    "+": {"arity": 2, "function": add},
    "*": {"arity": 2, "function": multiply},
}
