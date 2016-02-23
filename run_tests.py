#! /usr/bin/env python3
import os
import sys
import inspect
import log_calls
import unittest

def usage():
    """Usage: <path>/run_tests.py [-v | -q | -h]
       <path> is the path to the directory containing run_tests.py.
              Use . if running it from its own directory.
       -v     Verbose output, each test that's run is listed.
       -q     Quiet(est) output.
       -h     Display this message.
    """
    exit(usage.__doc__)

verbosity = 1
if len(sys.argv) > 1:
    arg = sys.argv[1].upper()

    if arg.startswith("-H"):
        usage()     # exits

    if arg.startswith("-Q"):
        verbosity = 0
    elif arg.startswith("-V"):
        verbosity = 2

home, _ = os.path.split(__file__)
tests_dir = os.path.join(home, 'log_calls', 'tests')

# 0.2.4 Change to tests_dir so that tests can find settings files
tests_dir = os.path.abspath(tests_dir)
os.chdir(tests_dir)

unittest.TextTestRunner(verbosity=verbosity).run(
    unittest.defaultTestLoader.discover(tests_dir)
)
