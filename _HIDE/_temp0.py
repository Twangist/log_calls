__author__ = 'brianoneill'

from log_calls import log_calls

@log_calls(omit='revint')
class D():
    def __init__(self, n):
        self.n = n if n >= 0 else -n

    @staticmethod
    def revint(x): return int(str(x)[::-1])

    def double(self): return self.n + self.n

    @property
    @log_calls(log_retval=True)
    def revn(self): return self.revint(self.n)

d = D(71)
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
d.double()
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print('~~~\nMy favorite number plus 3 is', d.revn + 3)

@log_calls()
def f(x):
    f.log_message('Yo')
f(2)
