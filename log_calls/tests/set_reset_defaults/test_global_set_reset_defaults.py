__author__ = 'brianoneill'

from log_calls.tests.set_reset_defaults.global_defaults import *

##############################################################################
# tests
##############################################################################

def test_global_settings():
    """
    >>> @log_calls()
    ... def f(x, y):    return x*(x+1)//2 + y
    >>> @log_calls()
    ... def g(n):       return f(n, 2*n)
    >>> g(2)
    g [1] <== called by <module>
        arguments: n=2
        f [1] <== called by g [1]
            arguments: x=2 $ y=4
            f [1] return value: 7
        g [1] return value: 7
    7

Calling `log_calls.reset_defaults()` won't change the settings of `f` or `g`,
of course -- only of newly decorated functions:

    >>> log_calls.reset_defaults()
    >>> f(1, 2)
    f [2] <== called by <module>
        arguments: x=1 $ y=2
        f [2] return value: 3
    3

    >>> @log_calls()
    ... def h(x, y, z): return x+y+z
    >>> h(1, 2, 3)
    h <== called by <module>
        arguments: x=1, y=2, z=3
    h ==> returning to <module>
    6x
    """
    pass


##############################################################################
# end of tests.
##############################################################################

import doctest

# For unittest integration
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    return tests


if __name__ == "__main__":
    doctest.testmod()   # (verbose=True)
