import math


FUNCTIONS_BOOLEAN = {
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

}

