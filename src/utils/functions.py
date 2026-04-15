import math


FUNCTIONS = {
   "AND": {
       "arity": 2,
       "function": lambda a, b: int(a and b)
   },
   "OR": {
       "arity": 2,
       "function": lambda a, b: int(a or b)
   },
   "NOT": {
       "arity": 1,
       "function": lambda a: int(not a)
   },
   "XOR": {
       "arity": 2,
       "function": lambda a, b: a ^ b
   },


   # Para regresión (los dejamos desde ahora)
   "+": {
       "arity": 2,
       "function": lambda a, b: a + b
   },
   "-": {
       "arity": 2,
       "function": lambda a, b: a - b
   },
   "*": {
       "arity": 2,
       "function": lambda a, b: a * b
   },
   "div": {
       "arity": 2,
       "function": lambda a, b: a / b if b != 0 else 1
   },
   "sin": {
       "arity": 1,
       "function": lambda a: math.sin(a)
   },
   "cos": {
       "arity": 1,
       "function": lambda a: math.cos(a)
   }
}

