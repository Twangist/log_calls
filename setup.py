__doc__ = """
Python 3 decorator that can display a great deal of useful information about
calls to a decorated function, such as:

* the caller of the function,
* the number of the call,
* the arguments passed to the function, and any default values used,
* the time the function took to execute,
* display of the complete call chain back to another `log_calls`-decorated caller,
* indentation by call level,
* the function's return value,
* the function's return to the caller.

The decorator can print its messages, to stdout or another stream, or can write
to a Python logger.

It can also collect profiling data and statistics, accessible dynamically:

* number of calls to a function,
* total time taken by the function,
* the function's entire call history (arguments, time elapsed, return values,
  callers, and more), optionally as text in CSV format.

NOTE: CPython only -- this uses internals of stack frames
      which may well differ in other interpreters.
See docs/log_calls.md for details, usage info and examples.
"""
import log_calls

from setuptools import setup
setup(
    name='log_calls',
    version=log_calls.__version__,
    author=log_calls.__author__,       # "Brian O'Neill",
    author_email='twangist@gmail.com',
    description='Debugging and profiling decorator that logs caller name(s), args+values, execution time, and more.',
    long_description=__doc__,
    license='MIT',
    keywords='debugging decorator logging function call caller profiling stack recursion teaching',
    url='http://github.com/Twangist/log_calls',
    packages=['log_calls', 'log_calls/tests'],
    test_suite='log_calls.tests',     # log_calls.tests.run_tests
    scripts=['scripts/log_calls-path-to-docs'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Utilities',
        'Topic :: System :: Logging',
    ]
)
