__author__ = 'brianoneill'

from log_calls import log_calls

@log_calls()
class A():
    def __init__(self, x): self.x = x
    def __repr__(self): return str(self.x)

a = A(5); print(a)

