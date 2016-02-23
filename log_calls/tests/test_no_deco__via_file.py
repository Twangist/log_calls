__author__ = 'brianoneill'

import doctest
from log_calls import log_calls

#-----------------------------------------------------------------------------

def test_dont_decorate__via_file():
    """
    >>> @log_calls(settings='settings-with-NO_DECO.txt')
    ... def f(n, m):
    ...     return 3*n*n*m + 4*n*m*m

    >>> @log_calls(log_exit=False, settings='settings-with-NO_DECO.txt')
    ... def g(x, y):
    ...     return f(x, y) - 20

    >>> @log_calls(only='method', settings='settings-with-NO_DECO.txt')
    ... class C():
    ...     def __init__(self, prefix=''):
    ...         self.prefix = prefix
    ...
    ...     def method(self, s):
    ...         return self.prefix + s

    >>> print(f(1, 2))
    22
    >>> print(g(3, 4))
    280

    >>> print(C('Hello, ').method('world!'))
    Hello, world!

    >>> hasattr(f, 'log_calls_settings')
    False
    >>> hasattr(g, 'log_calls_settings')
    False
    >>> hasattr(C.method, 'log_calls_settings')
    False
    """
    pass

#-----------------------------------------------------------------------------
# For unittest integration
#-----------------------------------------------------------------------------
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    return tests

#-----------------------------------------------------------------------------
if __name__ == "__main__":

    doctest.testmod()   # (verbose=True)
    # unittest.main()
