import math

FUNCTIONS_REGRESSION = {
    "+": {"arity": 2, "function": lambda a, b: a + b},
    "-": {"arity": 2, "function": lambda a, b: a - b},
    "*": {"arity": 2, "function": lambda a, b: a * b},
    "div": {
        "arity": 2,
        "function": lambda a, b: a / b if b != 0 else 1
    },
    "sin": {"arity": 1, "function": lambda a: math.sin(a)},
    "cos": {"arity": 1, "function": lambda a: math.cos(a)},
    "log": {
        "arity": 1,
        "function": lambda a: math.log(abs(a)) if a != 0 else 0
    },
    "exp": {
        "arity": 1,
        "function": lambda a: math.exp(a) if a < 50 else 1e6
    },
    "sqrt": {
        "arity": 1,
        "function": lambda a: math.sqrt(abs(a))
    },
    "abs": {"arity": 1, "function": lambda a: abs(a)},
}


