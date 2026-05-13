import math

# Funciones nombradas (serializables con pickle) en lugar de lambdas
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b if b != 0 else 1

def sine(a):
    return math.sin(a)

def cosine(a):
    return math.cos(a)

def logarithm(a):
    return math.log(abs(a)) if a != 0 else 0

def exponential(a):
    return math.exp(a) if a < 50 else 1e6

def square_root(a):
    return math.sqrt(abs(a))

def absolute(a):
    return abs(a)

def power(a, b):
    # Limitamos el exponente a un rango entre -3 y 3
    b_limited = max(min(b, 3), -3)
    try:
        if abs(a) < 100:
            return pow(abs(a), b_limited)
        else:
            return 1.0
    except:
        return 1.0

def scale(a):
    """Amplificador: multiplica por 20"""
    return a * 20

def half(a):
    """Atenuador: divide entre 2"""
    return a * 0.5

def mul_sin(a, b):
    return a * math.sin(b)

def mul_cos(a, b):
    return a * math.cos(b)

FUNCTIONS_REGRESSION = {
    "+": {"arity": 2, "function": add},
    "-": {"arity": 2, "function": subtract},
    "*": {"arity": 2, "function": multiply},
    "div": {"arity": 2, "function": divide},
    "sin": {"arity": 1, "function": sine},
    "cos": {"arity": 1, "function": cosine},
    "log": {"arity": 1, "function": logarithm},
    "exp": {"arity": 1, "function": exponential},
    "sqrt": {"arity": 1, "function": square_root},
    "abs": {"arity": 1, "function": absolute},
    "pow": {"arity": 2, "function": power},
    "mul_sin": {"arity": 2, "function": mul_sin},
    "mul_cos": {"arity": 2, "function": mul_cos},
    "scale": {"arity": 1, "function": scale},
    "half": {"arity": 1, "function": half}
}


