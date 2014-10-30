__doc__ = """
Configurable decorator for debugging and profiling that writes
caller name(s), args+values, function return values, execution time,
number of call, to stdout or to a logger. log_calls can track
call history and provide it in CSV format.
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
    description='Debugging decorator that writes caller name(s) & args+values.',
    long_description=__doc__,
    license='MIT',
    keywords='debugging decorator logging function call caller arguments',
    url='http://github.com/Twangist/log_calls',
    packages=['log_calls', 'log_calls/tests'],
    test_suite='log_calls.tests',
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
