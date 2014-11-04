__author__ = "Brian O'Neill"
__version__ = '0.1.14rc1'

from log_calls import helpers
import doctest
import unittest


# For unittest integration
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(helpers))
    return tests


if __name__ == "__main__":
    doctest.testmod(helpers)   # (verbose=True)
    # unittest.main()

