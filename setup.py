__doc__ = """
Configurable decorator for debugging that writes caller name(s),
args+values, and, optionally, function return values, to stdout
or to a logger.
NOTE: CPython only -- this uses internals of stack frames
      which may well differ in other interpreters.
See the README file for details, usage info and examples.
"""
import log_calls

from setuptools import setup
setup(
    name='log_calls',
    version=log_calls.__version__,     # '0.1.10-b1',
    author=log_calls.__author__,       # "Brian O'Neill",
    author_email='twangist@gmail.com',
    description='Debugging decorator that writes caller name(s) & args+values.',
    long_description=__doc__,
    license='MIT',
    keywords='debugging decorator logging function call caller arguments',
    url='http://github.com/Twangist/log_calls',
    packages=['log_calls', 'log_calls/tests'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
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
