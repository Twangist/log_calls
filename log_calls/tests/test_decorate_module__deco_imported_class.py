__author__ = 'brianoneill'

from log_calls import log_calls

###############################################################

def test_decorate_module():
    """
    >>> from log_calls.tests import some_module

    >>> log_calls.decorate_module(some_module)

Functions in module:

    >>> print(some_module.f(0, 0))
    f <== called by <module>
        arguments: a=0, b=0
        g <== called by f
            arguments: a=0, b=0
        g ==> returning to f
    f ==> returning to <module>
    10

    >>> print(some_module.g(1, 0))
    g <== called by <module>
        arguments: a=1, b=0
    g ==> returning to <module>
    1

Classes in module:

    >>> c = some_module.C("Hi")             # doctest: +ELLIPSIS
    C.__init__ <== called by <module>
        arguments: self=<log_calls.tests.some_module.C object at 0x...>, prefix='Hi'
    C.__init__ ==> returning to <module>

    >>> print(c.concat("there!"))           # doctest: +ELLIPSIS
    C.concat <== called by <module>
        arguments: self=<log_calls.tests.some_module.C object at 0x...>, s='there!'
    C.concat ==> returning to <module>
    Hi there!
    """
    pass

def decorate_imported_class():
    """
    >>> from log_calls.tests.some_other_module import N

N is now in the global namespace.

    >>> log_calls.decorate_class(N,
    ...                          args_sep='\\n', log_retval=True)

    >>> enn = N(14)                     # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    N.__init__ <== called by <module>
        arguments:
            self=<log_calls.tests.some_other_module.N object at 0x...>
            n=14
    N.__init__ ==> returning to <module>

    >>> print(enn.n)                    # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    N.n <== called by <module>
        arguments:
            self=<log_calls.tests.some_other_module.N object at 0x...>
        N.n return value: 14
    N.n ==> returning to <module>
    14

    >>> enn.n = -78                     # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    N.n <== called by <module>
        arguments:
            self=<log_calls.tests.some_other_module.N object at 0x...>
            val=-78
        N.n return value: None
    N.n ==> returning to <module>

    >>> print(enn.n)                    # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    N.n <== called by <module>
        arguments:
            self=<log_calls.tests.some_other_module.N object at 0x...>
        N.n return value: -78
    N.n ==> returning to <module>
    -78
    """
    pass


###############################################################

import doctest

# For unittest integration
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    return tests


def buncha_tests_n_examples():
    # from log_calls import log_calls

    # cwd is tests/
    from . import some_module as somemod
    # from log_calls.tests import some_module

    log_calls.decorate_module(somemod)

    # Functions in module:

    print(somemod.f(0, 0))
    """
    f <== called by <module>
        arguments: a=0, b=0
        g <== called by f
            arguments: a=0, b=0
        g ==> returning to f
    f ==> returning to <module>
    10"""

    print(somemod.g(1, 0))
    """
    g <== called by <module>
        arguments: a=1, b=0
    g ==> returning to <module>
    1"""

    # Classes in module:

    c = somemod.C("Hi")
    """
    C.__init__ <== called by <module>
        arguments: self=<log_calls.tests.some_module.C object at 0x...>, prefix='Hi'
    C.__init__ ==> returning to <module>"""

    #### FAILS ####
    print(c.concat("there!"))
    """
    C.concat <== called by <module>
        arguments: self=<log_calls.tests.some_module.C object at 0x...>, s='there!'
    C.concat ==> returning to <module>
    Hi there!"""


###############################################################

OBSERVE = True

import doctest



# For unittest integration
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    # print("Adding tests for test_decorate_things_in_module.py")
    return tests

if __name__ == '__main__':

    if OBSERVE:
        buncha_tests_n_examples()

    doctest.testmod()
