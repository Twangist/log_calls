__author__ = 'brianoneill'

def make_id(a, b):
    return "%04d-%04d-A" % (a, b)

def make_id2(a, b):
    return "J_%04d_%04d_XYZ" % (a, b)

class N():
    def __init__(self, n):
        self._n = n

    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, val):
        self._n = val
