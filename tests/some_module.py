__author__ = 'brianoneill'

def f(a, b):
    return g(a, b) + 10

def g(a, b):
    return b + (a * (a+1)) // 2

class C():
    def __init__(self, prefix):
        self.prefix = prefix

    def concat(self, s):
        return self.prefix + ' ' + s

class D(C):
    def tacnoc(self, s):
        return self.concat(s)[::-1]

