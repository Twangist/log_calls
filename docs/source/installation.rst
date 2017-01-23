.. _installation:

Installation
##################


Dependencies and requirements
==============================

The *log_calls* package has no dependencies — it requires no other packages.
All it requires is a standard distribution of Python 3.3 or higher (Python 3.4+
recommended).

Installing `log_calls`
==========================

You have two simple options:

1. Run:

       ``$ pip install log_calls``

   to install `log_calls` from PyPI (the Python Package Index), or

    *Here and elsewhere,* ``$`` *at the* beginning *of a line indicates your command prompt,
    whatever it may be.*

2. download the compressed distribution file (a ``.tar.gz`` or a ``.zip``),
   uncompress it into a directory, and run:

       ``$ python setup.py install``

   in that directory.

The complete distribution of `log_calls` (available as a  ``tar.gz`` or a ``zip``
from PyPI or github) contains three subdirectories: ``log_calls``, the package
proper; ``docs``, the documentation source files; and ``tests``, mentioned above.
These last two subdirectories are *not* installed by pip, so to obtain those
files you'll have to download an archive, and then, you may as well install
`log_calls` using method 2.

Whichever you choose, ideally you'll do it in a virtual environment (a *virtualenv*).
In Python 3.3+, it's easy to set up a virtual environment using the
`pyvenv <https://docs.python.org/3/using/scripts.html?highlight=pyvenv#pyvenv-creating-virtual-environments>`_
tool included in the standard distribution.

Running the tests
=================
Each ``*.py`` file in the ``log_calls/`` directory has at least one corresponding test
file ``test_*.py`` in the ``log_calls/tests/`` directory. The tests provide 96+% coverage.
All tests have passed on every tested platform + Python version (3.3.x through 3.6.0);
however, that's a sparse matrix :) If you encounter any turbulence, do let us know.

You can run the tests for `log_calls` after downloading it but before installing it,
by running the following command in the directory into which you uncompressed the download:

    ``$ ./run_tests.py [-q | -v | -h]``

which takes switches ``-q`` for "quiet" (the default), ``-v`` for "verbose",
and ``-h`` for "help".

What to expect
--------------
Both of the above commands run all tests in the ``tests/`` subdirectory. If you run
either of them, the output you see should end like so::

    Ran 112 tests in 2.235s
    OK

indicating that all went well. (**Depending upon which Python version you're using and on
what packages you have installed, you may see fewer tests reported.**) If any test fails, it will tell you.

.. note:: This package *probably* requires the CPython implementation, as it uses internals
 of stack frames which may well differ in other interpreters. It's not guaranteed to
 fail without CPython, it's just untested. (*If you're able and willing
 to run the tests under another interpreter or compiler, please tell us what you find*.)

 **PyPy is not (yet?) compatible with `log_calls`.**
 Finally PyPy3 supports Python 3.3: as of Winter 2017, the PyPy3 project has
 reached Python 3.3.5 with their version PyPy3.3, with 3.5 support in development
 (PyPy3.5, by name). So finally we can test its compatibility with `log_calls`: 8 of 110 tests fail.
 Some of the failures appear to be because PyPy3.3 has incorrect values for
 ``__qualname__``s of inner classes, and we'd expect these tests to pass in PyPy3.5.
 Others may be more fundamental — watch this space for at least a fuller assessment,
 if not a change in compatibility status.
