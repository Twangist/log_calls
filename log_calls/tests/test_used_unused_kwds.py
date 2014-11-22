__author__ = "Brian O'Neill"
__version__ = '0.2.4'

from log_calls import used_unused_kwds
from log_calls.used_unused_kwds  import used_unused_keywords
import doctest
import unittest


# For unittest integration
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(used_unused_kwds))
    return tests


if __name__ == "__main__":
    doctest.testmod(used_unused_kwds)   # (verbose=True)
    # unittest.main()

