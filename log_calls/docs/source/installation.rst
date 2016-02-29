.. _installation:

Installation
##################


Dependencies and requirements
==============================

The *log_calls* package has no dependencies — it requires no other packages.
All it requires is a standard distribution of Python 3.3 or higher (Python 3.4+ recommended).

Installing `log_calls`
==========================

You have two simple options:

1. Run:

       ``$ pip install log_calls``

   to install `log_calls` from PyPI (the Python Package Index), or

2. download the compressed distribution file (a ``.tar.gz`` or a ``.zip``),
uncompress it into a directory, and run:

       ``$ python setup.py install``

   in that directory.

Here and elsewhere, ``$`` at the *beginning* of a line indicates your command prompt,
whatever it may be.

Whichever you choose, ideally you'll do it in a virtual environment (a *virtualenv*).
In Python 3.3+, it's easy to set up a virtual environment using the
`pyvenv <https://docs.python.org/3/using/scripts.html?highlight=pyvenv#pyvenv-creating-virtual-environments>`_
tool, included in the standard distribution.

Running the tests
=================
Each ``*.py`` file in the ``log_calls/`` directory has at least one corresponding test
file ``test_*.py`` in the ``log_calls/tests/`` directory. The tests provide 96+% coverage.
All tests have passed on every tested platform + Python version (3.3.x through 3.5.y);
however, that's a sparse matrix :) If you encounter any turbulence, do let us know.

Running the tests after installation
---------------------------------------
From the ``log_calls/tests`` directory (beneath ``site-packages`` in a virtualenv, for example), run:

    ``$ python -m unittest discover [-q | -v] log_calls.tests``

which takes switches ``-q`` for "quiet" (the default), ``-v`` for "verbose".

Running the tests after downloading the distribution file
--------------------------------------------------------------
You can run the tests for `log_calls` after downloading it but before installing it,
by running the following command in the directory into which you uncompressed the download:

    ``$ ./run_tests.py [-q | -v | -h]``

which takes switches ``-q`` for "quiet" (the default), ``-v`` for "verbose",
and ``-h`` for "help".

After you've run the tests and installed `log_calls`, you can delete the directory
containing the uncompressed distribution file.

What to expect
--------------
Both of the above commands run all tests in the ``tests/`` subdirectory. If you run
either of them, the output you see should end like so::


    Ran 107 tests in 0.539s

    OK

indicating that all went well. (Depending upon what packages you have installed,
you may see fewer tests reported.) If any test fails, it will tell you.

.. note:: This package *probably* requires the CPython implementation, as it uses internals
 of stack frames which may well differ in other interpreters. It's not guaranteed to
 fail without CPython, it's just untested. (*If you're able and willing
 to run the tests under another interpreter or compiler, please tell us what you find*.)

 We would like `log_calls` to work with PyPy3, once that supports at least
 Python 3.3, and provided it supports the ``inspect`` module. Presently (early 2016,
 well after the release of Python 3.5) the PyPy3 project has still only reached Python 3.2.5,
 with no information available as to their next milestone.
