__author__ = 'brianoneill'

import doctest
from log_calls import log_calls


DECORATE = False

#-----------------------------------------------------------------------------
settings_dict = {
    '_DONT_DECORATE_': not DECORATE,
    'indent': True,
    'log_retval': True
}

#-----------------------------------------------------------------------------

def test_dont_decorate__via_dict():
    """
    >>> @log_calls(settings=settings_dict)
    ... def f(n, m):
    ...     return 3*n*n*m + 4*n*m*m

    >>> @log_calls(log_exit=False, settings=settings_dict)
    ... def g(x, y):
    ...     if DECORATE:
    ...         g.log_message("Some expressions and their values:")
    ...         g.log_exprs('x', 'y', 'f(x,y)')
    ...     return f(x, y) - 20

    >>> @log_calls(only='method', settings=settings_dict)
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
