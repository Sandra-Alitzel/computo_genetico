from utils.functions import FUNCTIONS


class Node:
   def __init__(self, value, children=None):
       self.value = value
       self.children = children or []


   def is_leaf(self):
       return len(self.children) == 0


   def evaluate(self, context):
       # 🔹 hoja
       if self.is_leaf():
           if isinstance(self.value, str):
               return context[self.value]
           return self.value


       # 🔹 función
       args = [child.evaluate(context) for child in self.children]


       func_info = FUNCTIONS[self.value]
       func = func_info["function"]


       return func(*args)


   def __str__(self):
       if self.is_leaf():
           return str(self.value)
       return f"{self.value}({', '.join(str(child) for child in self.children)})"
