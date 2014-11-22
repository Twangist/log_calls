__doc__ = """
`log_calls` is a Python 3 decorator that can print much useful information
about calls to a decorated function. It can write to `stdout`, to another
stream or file, or to a logger. It can save you from writing, rewriting,
copying, pasting and tweaking a lot of ad hoc, boilerplate code - and it
can keep your codebase free of that clutter.

For each call to a decorated function, `log_calls` can show you:

* the caller,
* the arguments passed to the function, and any default values used,
* the time the function took to execute,
* the complete call chain back to another `log_calls`-decorated caller,
* the number of the call,
* indentation by call level,
* the function's return value,
* and more!

These and other features are optional and configurable settings, which
can be specified for each decorated function via keyword parameters.
You can also dynamically get and set these settings using attributes
with the same names as the keywords, or using a dict-like interface
whose keys are the keywords.

`log_calls` can also collect profiling data and statistics, accessible dynamically:

* number of calls to a function,
* total time taken by the function,
* the function's entire call history (arguments, time elapsed, return values,
  callers, and more), available as text in CSV format and, if Pandas is
  installed, as a DataFrame.

These features and others are optional and configurable settings,
which can be specified for each decorated function via keyword parameters of
the decorator. You can also dynamically get and set these settings using attributes
with the same names as the keywords, or using a dict-like interface whose keys
are the keywords. In fact, through a mechanism of "indirect parameter values",
with just a modest amount of cooperation between decorated functions a calling
function can ensure uniform settings for all `log_calls`-decorated functions in
call chains beneath it.

The package contains two other decorators:

* `record_history`, a stripped-down version of `log_calls`,
only collects call history and statistics, and outputs no messages;
* `used_unused_keywords` lets a function easily determine, per-call,
which of its keyword parameters were actually supplied by the caller,
and which received their default values.

NOTE: This package requires the CPython implementation, as it makes assumptions
about stack frame internals which may not be valid in other interpreters.

See the documentation [online]((http://www.pythonhosted.org/log_calls/index.html)
or at `docs/log_calls.*` for usage, details, examples and *tips und tricks*.
"""
import log_calls

from setuptools import setup
setup(
    name='log_calls',
    version=log_calls.__version__,
    author=log_calls.__author__,       # "Brian O'Neill",
    author_email='twangist@gmail.com',
    description='Debugging and profiling decorator that logs '
                'caller name(s), args+values, execution time, and more. '
                'Eliminates reams of boilerplate code.',
    long_description=__doc__,
    license='MIT',
    keywords='decorator debugging profiling logging function call caller stack recursion teaching',
    url='http://github.com/Twangist/log_calls',
    packages=['log_calls', 'log_calls/tests'],
    test_suite='run_tests.py',     # log_calls.tests
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
