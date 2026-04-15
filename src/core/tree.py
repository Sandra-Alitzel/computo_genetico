# Árboles (las expresiones)
import random
from core.node import Node
from utils.functions import FUNCTIONS


class Tree:
   def __init__(self, function_set, terminal_set, max_depth):
       self.function_set = function_set  # F
       self.terminal_set = terminal_set  # T
       self.max_depth = max_depth


       self.root = self.generate_random_tree()


   def generate_random_tree(self, depth=0):
       # 🔹 condición de parada
       if depth >= self.max_depth:
           return self.random_terminal()


       # 🔹 decidir si es función o terminal
       if random.random() < 0.5:
           return self.random_terminal()
       else:
           return self.random_function(depth)


   def random_terminal(self):
       value = random.choice(self.terminal_set)
       return Node(value)


   def random_function(self, depth):
       func_name = random.choice(self.function_set)
       arity = FUNCTIONS[func_name]["arity"]


       children = [
           self.generate_random_tree(depth + 1)
           for _ in range(arity)
       ]


       return Node(func_name, children)


   def evaluate(self, context):
       return self.root.evaluate(context)


   def __str__(self):
       return str(self.root)

