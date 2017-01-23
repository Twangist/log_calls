#! /usr/bin/env python3
import os
import sys
import unittest


def usage_exit():
    """Usage: <path>/run_tests.py [-v | -q | -h]
       <path> is the path to the directory containing run_tests.py.
              Use . if running it from its own directory.
              All tests in <path>/tests/ are run.
       -v     Verbose output, each test that's run is listed.
       -q     Quiet(est) output.
       -h     Display this message.
    """
    exit(usage_exit.__doc__)


if __name__ == '__main__':
    verbosity = 1
    if len(sys.argv) > 1:
        arg = sys.argv[1].upper()

        if arg.startswith("-H"):    usage_exit()

        if arg.startswith("-Q"):    verbosity = 0
        elif arg.startswith("-V"):  verbosity = 2

    cd = os.getcwd()

    home, _ = os.path.split(__file__)
    tests_dir = os.path.abspath(os.path.join(home, 'tests'))    # 0.3.2 reorg
    # Change to tests_dir so that tests can find settings files
    os.chdir(tests_dir)

    unittest.TextTestRunner(verbosity=verbosity).run(
        unittest.defaultTestLoader.discover(tests_dir)
    )

    os.chdir(cd)
