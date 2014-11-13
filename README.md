#*log_calls* — A decorator for debugging and profiling
---
<small>*(This document is a work in progress: an overly fat README that I'll be reducing alot [v0.2.2: though not before adding to it] and making more of a "quick intro". Complete documentation is [here](http://www.pythonhosted.org/log_calls). Thanks for your patience/check this space! — BTO)*</small>

`log_calls` is a Python 3 decorator that can print much useful information
about calls to a decorated function. It can write to `stdout`, to another
stream, or to a logger. It can save you from writing, rewriting, copying,
pasting and tweaking a lot of ad hoc, boilerplate code - and it can keep
your codebase free of that clutter.

For each call of a decorated function, `log_calls` can show you:

* the caller,
* the arguments passed to the function, and any default values used,
* the time the function took to execute,
* the complete call chain back to another `log_calls`-decorated caller,
* the number of the call,
* indentation by call level,
* the function's return value,
* and more!

These and other features are optional and configurable settings, which can be specified for each decorated function via keyword parameters. You can also examine and change these settings on the fly using attributes with the same names as the keywords, or using a dict-like interface whose keys are the keywords. 

`log_calls` can also collect profiling data and statistics, accessible at runtime:

* the number of calls to a function,
* total time taken by the function,
* the function's entire call history (arguments, time elapsed, return values, callers, and more), optionally as text in CSV format or as a Pandas DataFrame.

The package contains another decorator, `record_history`, a stripped-down version
of `log_calls` which only collects call history and statistics, and outputs no messages.

This document gives an overview of the decorator's features and their use. A thorough account, including many useful examples, can be found in the complete documentation for [`log_calls`](http://www.pythonhosted.org/log_calls) and [`record_history`](http://www.pythonhosted.org/log_calls/record_history.html).

##[Version](id:Version)
This document describes version `0.2.2` of `log_calls`.

## [What's new](id:What's-new)
* **0.2.2** 
    * [The indent-aware writing method `log_message()`](#log_message), which decorated functions and methods can use to write extra debugging messages that align nicely with `log_calls` messages.
    * [Documentation](http://www.pythonhosted.org/log_calls#log_message) for `log_message()`.
    * [Documentation](http://www.pythonhosted.org/log_calls#accessing-own-attrs) for how functions and methods can access the attributes that `log_calls` adds for them, within their own bodies.
* **0.2.1**
    * The [`stats.history_as_DataFrame` attribute](http://www.pythonhosted.org/log_calls/record_history.html#stats.history_as_DataFrame), whose value is the call history of a decorated function as a [Pandas](http://pandas.pydata.org) [DataFrame](http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe) (if Pandas is installed; else `None`).
    * An IPython notebook (`log_calls/docs/history_to_pandas.ipynb`, browsable as HTML [here](http://www.pythonhosted.org/log_calls/history_to_pandas.html)) which compares the performance of using `record_history` *vs* a vectorized approach using [numpy](http://www.numpy.org/) to amass medium to large datasets, and which concludes that if you can vectorize, by all means do so.
* **0.2.0**
    * Initial public release.
    
##[Preliminaries](id:Preliminaries)
###[Dependencies and requirements](id:Dependencies-requirements)

The *log_calls* package has no dependencies - it requires no other packages. All it does require is a standard distribution of Python 3.2+.

NOTE: This package does require the CPython implementation, as it uses internals
of stack frames which may well differ in other interpreters.

###[Installation](id:Installation)
You have two simple options:

1. Download the compressed repository, uncompress it into a directory, and run:

    `$ python setup.py install`
    
    in that directory, or
  
2. run

    `$ pip install log_calls`
  
  to install log_calls from PyPI (the Python Package Index). Here and elsewhere, `$` at the *beginning* of a line indicates your command prompt, whatever it may be.

Whichever you choose, ideally you'll do it in a virtual environment (a *virtualenv*).

###[Running the tests](id:Testing)
Each `*.py` file in the log_calls directory has a corresponding test file `test_*.py` in the `log_calls/tests/` directory; `log_calls.py` has a second, `test_log_calls_more.py`. The tests provide essentially 100% coverage (98% for `log_calls.py`, 100% for the others). All tests have passed on every tested platform + Python version; however, that's a sparse matrix :) If you encounter any turbulence, do let us know.

You can run the test suites either before or after installing `log_calls`.

####[Running the tests before installation](id:tests-before-install)
To do this, download the compressed repository, as in 1. above.
After you uncompress the archive into a directory, and before you run the install command, first run one of the following commands:

    $ python setup.py test [-q]

(`-q` for "quiet", recommended) or
 
    $ python run_tests.py [-q | -v | -h]

which takes switches `-q` for "quiet", `-v` for "verbose", and `-h` for "help".


####[Running the tests after installation](id:tests-after-install)
You can run the tests for `log_calls` after installing it, using the command:

    $ python -m unittest discover log_calls.tests

####[What to expect](id:tests-ok)
All the above commands run all tests in the `log_calls/tests/` directory. If you run any of them, the output you see should end like so:

    ----------------------------------------------------------------------
    Ran 51 tests in 0.726s
    
    OK

indicating that all went well. If any test fails, it will say so.

##[Basic usage](id:Basic-usage)

`log_calls` has many features, and thus many, mostly independent, keyword parameters (14 in all). This section introduces all but four of them, one at a time, though of course you can use multiple parameters in any call to the decorator:

* [`enabled`](#enabled-parameter)
* [`args_sep`](#args_sep-parameter)
* [`log_args`](#log_args-parameter)
* [`log_retval`](#log_retval-parameter)
* [`log_exit`](#log_exit-parameter)
* [`log_call_numbers`](#log_call_numbers-parameter)
* [`log_elapsed`](#log_elapsed-parameter)
* [`indent`](#indent-parameter)
* [`prefix`](#prefix-parameter)
* [`file`](#file-parameter)

The two parameters that let you output `log_calls` messages to a `Logger` ([`logger`](#logger-parameter) and [`loglevel`](#loglevel-parameter)) are discussed in [Using loggers](#Logging). The two that determine whether call history is retained ([record_history](#record_history-parameter)), and then how much of it ([max_history](#max_history-parameter)), are discussed in [Call history and statistics](#call-history-and-statistics).

Every example in this document uses `log_calls`, so without further ado:

    >>> from log_calls import log_calls

###[Using no parameters](id:No-parameters)
First, let's see the simplest possible examples, using no parameters at all:

    >>> @log_calls()
    ... def f(a, b, c):
    ...     pass
    >>> f(1, 2, 3)
    f <== called by <module>
        arguments: a=1, b=2, c=3
    f ==> returning to <module>

Adding another decorated function to the call chain gives useful information too:

    >>> @log_calls()
    ... def g(a):
    ...     f(a, 2*a, 3*a)
    >>> g(3)
    g <== called by <module>
        arguments: a=3
    f <== called by g
        arguments: a=3, b=6, c=9
    f ==> returning to g
    g ==> returning to <module>

###[The *enabled* parameter (default – *True*)](id:enabled-parameter)

The next most basic example:

    >>> @log_calls(enabled=False)
    ... def f(a, b, c):
    ...     pass
    >>> f(1, 2, 3)                # no output

###[The *args_sep* parameter (default – `', '`)](id:args_sep-parameter)

The `args_sep` parameter specifies the character or string used to separate
arguments. If the string ends in  (or is) `\n`, additional whitespace
is appended so that arguments line up nicely:

    >>> @log_calls(args_sep='\\n')
    ... def f(a, b, c, **kwargs):
    ...     print(a + b + c)
    >>> f(1, 2, 3, u='you')       # doctest: +NORMALIZE_WHITESPACE, +SKIP
    f <== called by <module>
        arguments:
            a=1
            b=2
            c=3
            [**]kwargs={'u': 'you'}
    6
    f ==> returning to <module>

**NOTE**: *In all the doctest examples in this document, you'll see* `'\\n'`
*where in actual code you'd write* `'\n'`. *This is a `doctest` quirk: all
the examples herein work (as tests, they pass), and they would fail if*
`'\n'` *were used. The only alternative would be to use raw character strings
and write* `r'\n'`, *which is not obviously better.*

###[The *log_args* parameter (default – *True*)](id:log_args-parameter)
When true, as seen above, arguments passed to the decorated function are
logged. If the function's signature contains positional and/or keyword
"varargs" (`*args` and/or `**kwargs`), these are included if they're nonempty.
Any default values of keyword parameters with no corresponding argument are also
logged, on a separate line.

    >>> @log_calls()
    ... def f_a(a, *args, something='that thing', **kwargs): pass
    >>> f_a(1, 2, 3, foo='bar')
    f_a <== called by <module>
        arguments: a=1, [*]args=(2, 3), [**]kwargs={'foo': 'bar'}
        defaults:  something='that thing'
    f_a ==> returning to <module>

Here, no argument information is logged at all:

    >>> @log_calls(log_args=False)
    ... def f_b(a, *args, something='that thing', **kwargs): pass
    >>> f_b(1, 2, 3, foo='bar')
    f_b <== called by <module>
    f_b ==> returning to <module>

If a function has no parameters, `log_calls` won't display any "arguments"
section:

    >>> @log_calls()
    ... def f(): pass
    >>> f()
    f <== called by <module>
    f ==> returning to <module>

If a function has parameters but is passed no arguments, `log_calls`
will display `arguments: <none>`, plus any default values used:

    >>> @log_calls()
    ... def ff(*args, **kwargs): pass
    >>> ff()
    ff <== called by <module>
        arguments: <none>
    ff ==> returning to <module>

    >>> @log_calls()
    ... def fff(*args, kw='doh', **kwargs): pass
    >>> fff()
    fff <== called by <module>
        arguments: <none>
        defaults:  kw='doh'
    fff ==> returning to <module>

###[The *log_retval* parameter (default – *False*)](id:log_retval-parameter)
When true, this parameter displays the value returned by the function:

    >>> @log_calls(log_retval=True)
    ... def f(a, b, c):
    ...     return a + b + c
    >>> _ = f(1, 2, 3)
    f <== called by <module>
        arguments: a=1, b=2, c=3
        f return value: 6
    f ==> returning to <module>

###[The *log_exit* parameter (default – *True*)](id:log_exit-parameter)

When false, this parameter suppresses the `... ==> returning to ...` line
that indicates the function's return to its caller.

    >>> @log_calls(log_exit=False)
    ... def f(a, b, c):
    ...     return a + b + c
    >>> _ = f(1, 2, 3)
    f <== called by <module>
        arguments: a=1, b=2, c=3

###[The *log_call_numbers* parameter (default – *False*)](id:log_call_numbers-parameter)
`log_calls` keeps a running tally of the number of times a decorated function
is called. You can display this (1-based) number using the `log_call_numbers` parameter:

    >>> @log_calls(log_call_numbers=True)
    ... def f(): pass
    >>> for i in range(2): f()
    f [1] <== called by <module>
    f [1] ==> returning to <module>
    f [2] <== called by <module>
    f [2] ==> returning to <module>

The call number is also displayed when `log_retval` is true:

    >>> @log_calls(log_call_numbers=True, log_retval=True)
    ... def f():
    ...     return 81
    >>> _ = f()
    f [1] <== called by <module>
        f [1] return value: 81
    f [1] ==> returning to <module>

This is particularly valuable in the presence of recursion, for example.
See the [recursion example](#recursion-example) later, where the feature
is used to good effect.

###[The *log_elapsed* parameter (default – *False*)](id:log_elapsed-parameter)
For performance profiling, you can measure the time it took a function to execute by using the `log_elapsed` keyword. When true, `log_calls` reports the time the decorated function took to complete, in seconds:

    >>> @log_calls(log_elapsed=True)
    ... def f(n):
    ...     for i in range(n):
    ...         # do something time-critical
    ...         pass
    >>> f(5000)                 # doctest: +ELLIPSIS
    f <== called by <module>
        arguments: n=5000
        elapsed time: ... [secs]
    f ==> returning to <module>

###[The *indent* parameter (default - *False*)](id:indent-parameter)
The `indent` parameter, when true, indents each new level of logged messages by 4 spaces, providing a visualization of the call hierarchy.
(`log_calls` indents only when using `print`, not when [using loggers](#Logging).)

A decorated function's logged output is indented only as much as is necessary. Here, the even numbered functions don't indent, so the indented functions that they call are indented just one level more than their "inherited" indentation level:

    >>> @log_calls(indent=True)
    ... def g1():
    ...     pass
    >>> @log_calls()    # no extra indentation for g1
    ... def g2():
    ...     g1()
    >>> @log_calls(indent=True)
    ... def g3():
    ...     g2()
    >>> @log_calls()    # no extra indentation for g3
    ... def g4():
    ...     g3()
    >>> @log_calls(indent=True)
    ... def g5():
    ...     g4()
    >>> g5()
    g5 <== called by <module>
    g4 <== called by g5
        g3 <== called by g4
        g2 <== called by g3
            g1 <== called by g2
            g1 ==> returning to g2
        g2 ==> returning to g3
        g3 ==> returning to g4
    g4 ==> returning to g5
    g5 ==> returning to <module>

###[The *prefix* parameter (default - `''`): decorating methods](id:prefix-parameter)

Especially useful for clarity when decorating methods, the `prefix` keyword
parameter lets you specify a string with which to prefix the name of the
method. `log_calls` uses the prefixed name in its output: when logging
a call to, and a return from, the method; when reporting the method's return value; and when the method is at the end of a [call or return chain](#Call-chains).

    >>> import math
    >>> class Point():
    ...     # NOTE: You can't decorate __init__ :D
    ...     def __init__(self, x, y):
    ...         self.x = x
    ...         self.y = y
    ...     @staticmethod
    ...     @log_calls(prefix='Point.')
    ...     def distance(pt1, pt2):
    ...         return math.sqrt((pt1.x - pt2.x)**2 + (pt1.y - pt2.y)**2)
    ...     @log_calls(log_retval=True, prefix='Point.')
    ...     def length(self):
    ...         return self.distance(self, Point(0, 0))
    ...     @log_calls(prefix='Point.')
    ...     def diag_reflect(self):
    ...         self.x, self.y = self.y, self.x
    ...         return self
    ...     def __repr__(self):
    ...         return "Point" + str((self.x, self.y))

    >>> print("Point(1, 2).diag_reflect() =", Point(1, 2).diag_reflect())
    Point.diag_reflect <== called by <module>
        arguments: self=Point(1, 2)
    Point.diag_reflect ==> returning to <module>
    Point(1, 2).diag_reflect() = Point(2, 1)

    >>> print("length of Point(1, 2) =", round(Point(1, 2).length(), 2))  # doctest: +ELLIPSIS
    Point.length <== called by <module>
        arguments: self=Point(1, 2)
    Point.distance <== called by Point.length
        arguments: pt1=Point(1, 2), pt2=Point(0, 0)
    Point.distance ==> returning to Point.length
        Point.length return value: 2.236...
    Point.length ==> returning to <module>
    length of Point(1, 2) = 2.24

###[The *file* parameter (default - *sys.stdout*)](id:file-parameter)
The `file` parameter specifies a stream (an instance of `io.TextIOBase`) to which `log_calls` will print its messages. This value is supplied to the `file` keyword parameter of the `print` function, and, like that parameter, its default value is `sys.stdout`. This parameter is ignored if you've supplied a logger for output using the [`logger`](#logger-parameter) parameter.

If your program writes to the console a lot, you may not want `log_calls` messages interspersed with your real output: your understanding of both logically distinct streams can be compromised, so, better to make them two actually distinct streams. It can also be advantageous to gather all, and only all, of the log_calls messages in one place. You can use `indent=True` with a file, and the indentations will appear as intended, whereas that's not possible with loggers.

It's not possible to test this feature with doctest (in fact, there are subtleties to supporting this feature and using doctest at all), so we'll just give an example of writing to `stderr`, and reproduce the output:

    >>> import sys
    >>> @log_calls(file=sys.stderr, indent=True)
    ... def f(n):
    ...     if n <= 0:
    ...         return 'a'
    ...     return '(' + f(n-1) + ')'

Running `>>> f(2)` will return '((a))' and will write the following to `stderr`:

    f <== called by <module>
        f <== called by f
            arguments: n=1
            f <== called by f
                arguments: n=0
            f ==> returning to f
        f ==> returning to f
    f ==> returning to <module>

##[Using loggers](id:Logging)
`log_calls` works well with loggers obtained from Python's `logging` module. First, we'll set up a logger with a single handler that writes to the console. Because `doctest` doesn't capture output written to `stderr` (the default stream to which console handlers write), we'll send the console handler's output to `stdout`, using the format `<loglevel>:<loggername>:<message>`.

    >>> import logging
    >>> import sys
    >>> ch = logging.StreamHandler(stream=sys.stdout)
    >>> c_formatter = logging.Formatter('%(levelname)8s:%(name)s:%(message)s')
    >>> ch.setFormatter(c_formatter)
    >>> logger = logging.getLogger('a_logger')
    >>> logger.addHandler(ch)
    >>> logger.setLevel(logging.DEBUG)

###[The *logger* parameter (default – *None*)](id:logger-parameter)

The `logger` keyword parameter tells `log_calls` to write its output using
that logger rather than the `print` function:

    >>> @log_calls(logger=logger)
    ... def somefunc(v1, v2):
    ...     logger.debug(v1 + v2)
    >>> @log_calls(logger=logger)
    ... def anotherfunc():
    ...     somefunc(17, 19)
    >>> anotherfunc()       # doctest: +NORMALIZE_WHITESPACE
    DEBUG:a_logger:anotherfunc <== called by <module>
    DEBUG:a_logger:somefunc <== called by anotherfunc
    DEBUG:a_logger:    arguments: v1=17, v2=19
    DEBUG:a_logger:36
    DEBUG:a_logger:somefunc ==> returning to anotherfunc
    DEBUG:a_logger:anotherfunc ==> returning to <module>

###[The *loglevel* parameter (default – *logging.DEBUG*)](id:loglevel-parameter)

`log_calls` also takes a `loglevel` keyword parameter, whose value must be
one of the `logging` module's constants - `logging.DEBUG`, `logging.INFO`, etc.
– or a custom logging level if you've added any. `log_calls` writes output messages
using `logger.log(loglevel, …)`. Thus, if the `logger`'s log level is higher than
`loglevel`, no output will appear:

    >>> logger.setLevel(logging.INFO)   # raise logger's level to INFO
    >>> @log_calls(logger='logger_=', loglevel=logging.DEBUG)
    ... def f(x, y, z, **kwargs):
    ...     return y + z
    >>> # No log_calls output from f
    >>> # because loglevel for f < level of logger
    >>> f(1,2,3, enable=True, sep_='\\n', logger_=logger)       # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    5

The use of loggers, and of these parameters, is explored further in the main documentation, which contains an example of [using a logger with multiple handlers that have different loglevels](./log_calls/docs/log_calls.html#logging-multiple-handlers).

##[Call chains](id:Call-chains)

`log_calls` does its best to chase back along the call chain to find
the first *enabled* `log_calls`-decorated function on the stack. 
If there's no such function, it just displays the immediate caller. 
If there is such a function, however, it displays the entire list of 
functions on the stack up to and including that function when reporting 
calls and returns. Without this, you'd have to guess at what was called 
in between calls to functions decorated by `log_calls`. If you specified 
a prefix for the decorated caller on the end of a call chain, `log_calls` 
will use the prefixed name:

    >>> @log_calls()
    ... def g1():
    ...     pass
    >>> def g2():
    ...     g1()
    >>> @log_calls(prefix='mid.')
    ... def g3():
    ...     g2()
    >>> def g4():
    ...     g3()
    >>> @log_calls()
    ... def g5():
    ...     g4()
    >>> g5()
    g5 <== called by <module>
    mid.g3 <== called by g4 <== g5
    g1 <== called by g2 <== mid.g3
    g1 ==> returning to g2 ==> mid.g3
    mid.g3 ==> returning to g4 ==> g5
    g5 ==> returning to <module>

In the next example, `g` is `log_calls`-decorated but logging is disabled,
so the reported call chain for `f` stops at its immediate caller:

    >>> @log_calls()
    ... def f(): pass
    >>> def not_decorated(): f()
    >>> @log_calls(enabled=False, log_call_numbers=True)
    ... def g(): not_decorated()
    >>> g()
    f <== called by not_decorated
    f ==> returning to not_decorated

Elaborating on the previous example, here are longer call chains with an 
intermediate decorated function that has logging disabled. We've also enabled indentation:

    >>> @log_calls(indent=True)
    ... def e(): pass
    >>> def not_decorated_call_e(): e()
    >>> @log_calls(indent=True)
    ... def f(): not_decorated_call_e()
    >>> def not_decorated_call_f(): f()
    >>> @log_calls(enabled=False, log_call_numbers=True, indent=True)
    ... def g(): not_decorated_call_f()
    >>> @log_calls(indent=True)
    ... def h(): g()
    >>> h()
    h <== called by <module>
        f <== called by not_decorated_call_f <== g <== h
            e <== called by not_decorated_call_e <== f
            e ==> returning to not_decorated_call_e ==> f
        f ==> returning to not_decorated_call_f ==> g ==> h
    h ==> returning to <module>

`log_calls` chases back to the nearest *enabled* decorated function, so that there aren't gaps between call chains. 

###[Indentation and call numbers with recursion](id:recursion-example)
These features are especially useful in recursive and mutually recursive situations. We have to use `OrderedDict`s here because of doctest:

    >>> from collections import OrderedDict
    >>> @log_calls(log_call_numbers=True, log_retval=True, indent=True)
    ... def depth(d, key=None):
    ...     if not isinstance(d, dict):
    ...         return 0    # base case
    ...     elif not d:
    ...         return 1
    ...     else:
    ...         return max(map(depth, d.values(), d.keys())) + 1
    >>> depth(
    ...     OrderedDict(
    ...         (('a', 0),
    ...          ('b', OrderedDict( (('c1', 10), ('c2', 11)) )),
    ...          ('c', 'text'))
    ...     )
    ... )
    depth [1] <== called by <module>
        arguments: d=OrderedDict([('a', 0), ('b', OrderedDict([('c1', 10), ('c2', 11)])), ('c', 'text')])
        defaults:  key=None
        depth [2] <== called by depth [1]
            arguments: d=0, key='a'
            depth [2] return value: 0
        depth [2] ==> returning to depth [1]
        depth [3] <== called by depth [1]
            arguments: d=OrderedDict([('c1', 10), ('c2', 11)]), key='b'
            depth [4] <== called by depth [3]
                arguments: d=10, key='c1'
                depth [4] return value: 0
            depth [4] ==> returning to depth [3]
            depth [5] <== called by depth [3]
                arguments: d=11, key='c2'
                depth [5] return value: 0
            depth [5] ==> returning to depth [3]
            depth [3] return value: 1
        depth [3] ==> returning to depth [1]
        depth [6] <== called by depth [1]
            arguments: d='text', key='c'
            depth [6] return value: 0
        depth [6] ==> returning to depth [1]
        depth [1] return value: 2
    depth [1] ==> returning to <module>
    2

**NOTE**: *The optional* `key` *parameter is for instructional purposes, so you can see the key that's paired with the value of* `d` *in the caller's dictionary. Typically the signature of this function would be just* `def depth(d)`, *and the recursive case would return* `max(map(depth, d.values())) + 1`.

## [The indent-aware writing method *log_message(msg, indent_extra=4)*](id:log_message)
`log_calls` exposes the method it uses to write its messages, `log_message`,
with full signature:

    `log_message(msg, indent_extra=4, sep=' ', prefix_with_name=False)`

If a decorated function or method writes debugging messages, even multiline
messages, it can use this method to write them so that they sit nicely within
the frame provided by `log_calls`.

Consider the following function:

    >>> @log_calls(indent=True, log_call_numbers=True)
    ... def f(n):
    ...     if n <= 0:
    ...         print("*** Base case n <= 0")
    ...     else:
    ...         print("*** n=%d is %s,\\n    but we knew that."
    ...               % (n, "odd" if n%2 else "even"))
    ...         f(n-1)
    >>> f(2)
    f [1] <== called by <module>
        arguments: n=2
    *** n=2 is even,
        but we knew that.
        f [2] <== called by f [1]
            arguments: n=1
    *** n=1 is odd,
        but we knew that.
            f [3] <== called by f [2]
                arguments: n=0
    *** Base case n <= 0
            f [3] ==> returning to f [2]
        f [2] ==> returning to f [1]
    f [1] ==> returning to <module>

The debugging messages written by `f` literally "stick out", and it gets difficult,
especially in more complex situations with multiple functions and methods,
to figure out who actually wrote which message; hence the "(n=%d)" tag. If instead
`f` uses `log_message`, all of its messages from each invocation align neatly
within the frame presented by `log_calls`. We also take the opportunity to
illustrate the keyword parameters of `log_message`:

    >>> @log_calls(indent=True, log_call_numbers=True)
    ... def f(n):
    ...     if n <= 0:
    ...         f.log_message("Base case n=0", prefix_with_name=True)
    ...     else:
    ...         f.log_message("n=%d is %s,\\n    but we knew that."
    ...                       % (n, "odd" if n%2 else "even"),
    ...                       prefix_with_name=True)
    ...         f.log_message("*** We'll be right back, after this:", indent_extra=0)
    ...         f(n-1)
    ...         f.log_message("*** We're back.", indent_extra=0)
    >>> f(2)
    f [1] <== called by <module>
        arguments: n=2
        f [1]: n=2 is even,
            but we knew that.
    *** We'll be right back, after this:
        f [2] <== called by f [1]
            arguments: n=1
            f [2]: n=1 is odd,
                but we knew that.
        *** We'll be right back, after this:
            f [3] <== called by f [2]
                arguments: n=0
                f [3]: Base case n=0
            f [3] ==> returning to f [2]
        *** We're back.
        f [2] ==> returning to f [1]
    *** We're back.
    f [1] ==> returning to <module>

The `indent_extra` value is an offset from the column in which
the entry and exit messages for the function begin.
`f` uses the default value `indent_extra=4`, so its messages
align with "arguments:". `log_calls` itself explicitly supplies
`indent_extra=0`. Negative values are tolerated :), and do what
you'd expect.

## [Advanced Features](id:Advanced-features)
`log_calls` provides a number of features beyond those already described. We'll only give an overview of them here. For a full account, see [the complete documentation](http://www.pythonhosted.org/log_calls).

### [Dynamic control of settings](id:dynamic-control-of-settings)
Sometimes, you'll need or want to change a `log_calls` setting for a decorated function on the fly. The major impediment to doing so is that the values  of the `log_calls` parameters are set once the decorated function is interpreted. 
Those values are established once and for all when the Python interpreter 
parses the definition of a decorated function and creates a function object.

#### [The problem, and two *log_calls* solutions](id:log_call_settings)
Even if a variable is used as a parameter value, its value at the time
Python processes the definition is "frozen" for the created function object.
Subsequently changing the value of the variable will *not* affect the behavior
of the decorator.

For example, suppose `DEBUG` is a module-level variable initialized to `False`:

    >>> DEBUG = False

and you use this code:

    >>> @log_calls(enabled=DEBUG)
    ... def foo(**kwargs):
    ...     pass
    >>> foo()       # No log_calls output: DEBUG is False

If later you set `Debug = True` and call `foo`, that call won't be logged,
because the decorated `foo`'s *enabled* setting is bound to the original value
of `DEBUG`, established when the definition was processed:

    >>> DEBUG = True
    >>> foo()       # Still no log_calls output

`log_calls` provides *two* ways to overcome this limitation and dynamically control the settings of a decorated function:

* the `log_calls_settings` attribute, which provides a mapping interface and an attribute-based interface to settings, and 
* *indirect values. 

The following two subsections give a brief introduction to these features, which [the main documentation]((http://www.pythonhosted.org/log_calls) presents in depth.

#### [The *log_calls_settings* attribute](id:log_call_settings)
`log_calls` adds an attribute `log_calls_settings`
to a decorated function, through which you can access the decorator settings for that function. This attribute is an object which lets you control the settings for a decorated function via a mapping (`dict`-like) interface, and equivalently, via attributes of the object. The mapping keys and the attribute names are simply the `log_calls` keywords. `log_calls_settings` also implements many of the standard `dict` methods for interacting with the settings in familiar ways.

#####[The mapping interface and the attribute interface to settings](id:mapping-interface)

Once you've decorated a function with `log_calls`,

    >>> @log_calls()
    ... def f(*args, **kwargs):
    ...     return 91

you can access and change its settings via the `log_calls_settings` attribute
of the decorated function, which behaves like a dictionary. You can read and
write settings using the `log_calls` keywords as keys:

    >>> f.log_calls_settings['enabled']
    True
    >>> f.log_calls_settings['enabled'] = False
    >>> _ = f()                   # no output (not even 91, because of "_ = ")
    >>> f.log_calls_settings['enabled']
    False
    >>> f.log_calls_settings['log_retval']
    False
    >>> f.log_calls_settings['log_retval'] = True
    >>> f.log_calls_settings['log_elapsed']
    False
    >>> f.log_calls_settings['log_elapsed'] = True

You can also use the same keywords as attributes of `log_calls_settings`
instead of as keywords to the mapping interface; they're completely
equivalent:

    >>> f.log_calls_settings.log_elapsed
    True
    >>> f.log_calls_settings.log_call_numbers
    False
    >>> f.log_calls_settings.log_call_numbers = True
    >>> f.log_calls_settings.enabled = True     # turn it back on!
    >>> _ = f()                                 # doctest: +ELLIPSIS
    f [1] <== called by <module>
        arguments: <none>
        f [1] return value: 91
        elapsed time: ... [secs]
    f [1] ==> returning to <module>

    >>> f.log_calls_settings.log_args = False
    >>> f.log_calls_settings.log_elapsed = False
    >>> f.log_calls_settings.log_retval = False
    >>> _ = f()                                 # doctest: +ELLIPSIS
    f [2] <== called by <module>
    f [2] ==> returning to <module>

The `log_calls_settings` attribute has a length (14), its keys and `items()` can be iterated through, you can use `in` to test for key membership, and it has an `update()` method. As with an ordinary dictionary, attempting to access a nonexistent setting 
raises `KeyError`. Unlike an ordinary dictionary, you can't add new keys – the `log_calls_settings` dictionary is closed to new members, and attempts to add one will also raise `KeyError`.

###### [The *update()*, *as_OrderedDict()* and *as_dict()* methods – and a typical use-case](id:update-as_etc)
The `update()` method of the `log_calls_settings` object lets you update several settings at once:

    >>> f.log_calls_settings.update(
    ...     log_args=True, log_elapsed=False, log_call_numbers=False,
    ...     log_retval=False)
    >>> _ = f()
    f <== called by <module>
        arguments: <none>
    f ==> returning to <module>

You can retrieve the entire collection of settings as either an `OrderedDict` using the `as_OrderedDict()` method, or as a `dict` using `as_dict()`.
Either can serve as a snapshot of the settings, so that you can change settings temporarily, use the new settings, and then use `update()` restore settings from the snapshot.
in addition to taking keyword arguments, as shown above, `update()` can take one or more dicts – in particular, a dictionary retrieved from one of the `as_*` methods. For example:

Retrieve settings (here, as an `OrderedDict` because those are more doctest-friendly, but using `as_dict()` suffices):

    >>> od = f.log_calls_settings.as_OrderedDict()
    >>> od                      # doctest: +NORMALIZE_WHITESPACE
    OrderedDict([('enabled', True),           ('args_sep', ', '),
                 ('log_args', True),          ('log_retval', False),
                 ('log_elapsed', False),      ('log_exit', True),
                 ('indent', False),           ('log_call_numbers', False),
                 ('prefix', ''),              ('file', None),
                 ('logger', None),            ('loglevel', 10),
                 ('record_history', False),   ('max_history', 0)])

change settings temporarily:

    >>> f.log_calls_settings.update(
    ...     log_args=False, log_elapsed=True, log_call_numbers=True,
    ...     log_retval=True)

use the new settings for `f`:

    >>> _ = f()                     # doctest: +ELLIPSIS
    f [4] <== called by <module>
        f [4] return value: 91
        elapsed time: ... [secs]
    f [4] ==> returning to <module>

and restore original settings, this time passing the retrieved settings
dictionary rather than keywords (we *could* pass `**od`, but that's unnecessary and a pointless expense):

    >>> f.log_calls_settings.update(od)
    >>> od == f.log_calls_settings.as_OrderedDict()
    True

#### [Indirect values](id:Indirect-values)
`log_calls` provides a second way to access and change settings on the fly. The decorator lets you specify any parameter 
except `prefix` or `max_history` with one level of indirection, by using 
*indirect values*: an indirect value is a string that names a keyword argument 
*of the decorated function*. It can be an explicit keyword argument present 
in the signature of the function, or an implicit keyword argument that ends up 
in `**kwargs` (if that's present in the function's signature). When the decorated 
function is called, the arguments passed by keyword, and the decorated function's 
explicit keyword parameters with default values, are both searched for the named 
parameter; if it is found and of the correct type, *its* value is used; otherwise 
the default value for the `log_calls` parameter is used.

To specify an indirect value for a parameter whose normal type is `str` (only 
`args_sep`, at present), append an `'='` to the value.  For consistency, 
any indirect value can end in a trailing `'='`, which is stripped. Thus, 
`enabled='enable_='` indicates an indirect value *to be supplied* by the keyword (argument or parameter) `enable_` of the decorated function.

For example, in:

    >>> @log_calls(args_sep='sep=', prefix="*** ")
    ... def f(a, b, c, sep='|'): pass

`args_sep` has an indirect value which names `f`'s explicit keyword parameter `sep`,
and `prefix` has a direct value as it always does. A call can dynamically override the default
value '|' in the signature of `f` by supplying a value:

    >>> f(1, 2, 3, sep=' / ')
    *** f <== called by <module>
        arguments: a=1 / b=2 / c=3 / sep=' / '
    *** f ==> returning to <module>

or it can use `f`'s default value by not supplying a `sep` argument:

    >>> f(1, 2, 3)
    *** f <== called by <module>
        arguments: a=1|b=2|c=3
        defaults:  sep='|'
    *** f ==> returning to <module>

*A decorated function doesn't have to explicitly declare the parameter 
named as an indirect value*, if its signature includes `**kwargs`: 
the intermediate parameter can be an implicit keyword parameter, 
passed by a caller but not present in the function's signature.
Consider:

    >>> @log_calls(enabled='enable')
    ... def func1(a, b, c, **kwargs): pass
    >>> @log_calls(enabled='enable')
    ... def func2(z, **kwargs): func1(z, z+1, z+2, **kwargs)

When the following statement is executed, the calls to both `func1` and `func2` will be logged:

    >>> func2(17, enable=True)
    func2 <== called by <module>
        arguments: z=17, [**]kwargs={'enable': True}
    func1 <== called by func2
        arguments: a=17, b=18, c=19, [**]kwargs={'enable': True}
    func1 ==> returning to func2
    func2 ==> returning to <module>

whereas neither of the following two statements will trigger logging:

    >>> func2(42, enable=False)     # no log_calls output
    >>> func2(99)                   # no log_calls output

See the section in the full documentation on [indirect values](http://www.pythonhosted.org/log_calls#Indirect-values) for several more examples and useful techniques involving indirect values. The test suite `log_calls/tests/test_log_calls_more.py` also contains further doctests/examples. 

### [Call history and statistics](id:call-history-and-statistics)
`log_calls` always collects a few basic statistics about calls to a decorated
function. It can collect the entire history of calls to a function if asked
to, or just the most recent `n` calls; the \*_history parameters, discussed next, determine these settings. The statistics and history are accessible via the `stats` attribute which `log_calls` adds to a decorated function.

#### [The *record_history* and *max_history* parameters](id:_history-parameters)
The two parameters we haven't yet discussed govern the recording of a decorated function's call history.

#####[The *record_history* parameter (default – *False*)](id:record_history-parameter)
When the `record_history` setting is true for a decorated function `f`, `log_calls` will retain a sequence of records holding the details of each logged call to that function. That history is accessible via attributes of the `stats` object. 

Let's define a function `f` with `record_history` set to true:

    >>> @log_calls(record_history=True, log_call_numbers=True, log_exit=False)
    ... def f(a, *args, x=1, **kwargs): pass

We'll call this function f in the following subsections, manipulate its settings, and examine its statistics.

#####[The *max_history* parameter (default – 0)](id:max_history-parameter)
The `max_history` parameter determines how many call history records are retained for a decorated function whose call history is recorded. If this value is 0 or negative, unboundedly many records are retained (unless or until
you set the `record_history` setting to false, or call the
[`stats.clear_history()`](#stats.clear_history) method). If the value of `max_history` is > 0, `log_calls` will retain at most that many records, discarding the oldest records to make room for newer ones if the history reaches capacity.

You cannot change `max_history` using the mapping interface or the attribute
of the same name; attempts to do so raise `ValueError`. The only way to change its value is with the [`stats.clear_history()`](#stats.clear_history) method, discussed below.

####[The *stats* attribute and *its* attributes](id:stats-attribute)
The `stats` attribute of a decorated function is an object that provides statistics and data about calls to a decorated function:

* [`stats.num_calls_logged`](#stats.num_calls_logged)
* [`stats.num_calls_total`](#stats.num_calls_total)
* [`stats.elapsed_secs_logged`](#elapsed_secs_logged)
* [`stats.history`](#stats.history)
* [`stats.history_as_csv`](#stats.history_as_csv)
* [`stats.history_as_DataFrame`](#stats.history_as_DataFrame)

The first three don't depend on the `record_history` setting at all.The last three yield empty results unless `record_history` is true. 

The `stats` attribute also provides one method, [`stats.clear_history()`](#stats.clear_history).

Let's call the function `f` defined above twice:

    >>> f(0)
    f [1] <== called by <module>
        arguments: a=0
        defaults:  x=1
    >>> f(1, 100, 101, x=1000, y=1001)
    f [2] <== called by <module>
        arguments: a=1, [*]args=(100, 101), x=1000, [**]kwargs={'y': 1001}

and look at its `stats`.

#####[The *num_calls_logged* attribute](id:stats.num_calls_logged)
The `stats.num_calls_logged` attribute contains the number of the most
recent logged call to a decorated function. Thus, `f.stats.num_calls_logged`
will equal 2:

    >>> f.stats.num_calls_logged
    2

This counter gets incremented when a decorated function is called that has logging enabled, even if its `log_call_numbers` setting is false.

#####[The *num_calls_total* attribute](id:stats.num_calls_total)
The `stats.num_calls_total` attribute holds the *total* number of calls
to a decorated function. This counter gets incremented even when logging
is disabled for a function.

For example, let's now *disable* logging for `f` and call it 3 more times:

    >>> f.log_calls_settings.enabled = False
    >>> for i in range(3): f(i)

Now `stats.num_calls_total` will equal 5, but `f.stats.num_calls_logged`
will still equal 2:

    >>> f.stats.num_calls_total
    5
    >>> f.stats.num_calls_logged
    2

Finally, let's re-enable logging for `f` and call it again.
The displayed call number will be the number of the *logged* call, 3, the same
value as `f.stats.num_calls_logged` after the call:

    >>> f.log_calls_settings.enabled = True
    >>> f(10, 20, z=5000)
    f [3] <== called by <module>
        arguments: a=10, [*]args=(20,), [**]kwargs={'z': 5000}
        defaults:  x=1

    >>> f.stats.num_calls_total
    6
    >>> f.stats.num_calls_logged
    3

**ATTENTION**: *Thus,* `log_calls` *has some overhead even when it's disabled, and somewhat more when it's enabled. So, ***comment it out in production code!** 

#####[The *elapsed_secs_logged* attribute](id:elapsed_secs_logged)
The `stats.elapsed_secs_logged` attribute holds the sum of the elapsed times of
all logged calls to a decorated function, in seconds. Here's its value for the 3 logged calls to `f` above:

    >>> f.stats.elapsed_secs_logged   # doctest: +SKIP
    6.67572021484375e-06

#####[The *history* attribute](id:stats.history)
The `stats.history` attribute of a decorated function provides the call history
of logged calls to the function as a tuple of records. Each record is a `namedtuple`of type `CallRecord`. Here's `f`'s call history,
in (almost) human-readable form:

    >>> print('\\n'.join(map(str, f.stats.history)))   # doctest: +SKIP
    CallRecord(call_num=1, argnames=['a'], argvals=(0,), varargs=(),
                           explicit_kwargs=OrderedDict(),
                           defaulted_kwargs=OrderedDict([('x', 1)]), implicit_kwargs={},
                           retval=None, elapsed_secs=2.1457672119140625e-06,
                           timestamp='10/28/14 15:56:13.733763',
                           prefixed_func_name='f', caller_chain=['<module>'])
    CallRecord(call_num=2, argnames=['a'], argvals=(1,), varargs=(100, 101),
                           explicit_kwargs=OrderedDict([('x', 1000)]),
                           defaulted_kwargs=OrderedDict(), implicit_kwargs={'y': 1001},
                           retval=None, elapsed_secs=1.9073486328125e-06,
                           timestamp='10/28/14 15:56:13.734102',
                           prefixed_func_name='f', caller_chain=['<module>'])
    CallRecord(call_num=3, argnames=['a'], argvals=(10,), varargs=(20,),
                           explicit_kwargs=OrderedDict(),
                           defaulted_kwargs=OrderedDict([('x', 1)]), implicit_kwargs={'z': 5000},
                           retval=None, elapsed_secs=2.1457672119140625e-06,
                           timestamp='10/28/14 15:56:13.734412',
                           prefixed_func_name='f', caller_chain=['<module>'])

The CSV representation pairs
the `argnames` with their values in `argvals` (the `argnames` become column headings), 
making it even more human-readable, especially when viewed in a program that 
presents CSVs nicely.

#####[The *history_as_csv* attribute](id:stats.history_as_csv)
The value `stats.history_as_csv` attribute is a text representation in CSV format
of a decorated function's call history. You can save this string
and import it into the program or tool of your choice for further analysis.
(*Note: if your tool of choice is [Pandas](http://pandas.pydata.org), you can use 
the `stats` attribute `stats.history_as_DataFrame` to directly obtain history in 
the representation you ultimately want.*)
The CSV representation
breaks out each argument into its own column, throwing away 
information about whether an argument's value was passed or is a default.

The CSV separator is '|' rather than ',' because some of the fields – `args`,  `kwargs`
and `caller_chain` – use commas intrinsically. Let's examine one more 
`history_as_csv` for a function that has all of those fields:

    >>> @log_calls(record_history=True, log_call_numbers=True,
    ...            log_exit=False, log_args=False)
    ... def f(a, *extra_args, x=1, **kw_args): pass
    >>> def g(a, *args, **kwargs): f(a, *args, **kwargs)
    >>> @log_calls(log_exit=False, log_args=False)
    ... def h(a, *args, **kwargs): g(a, *args, **kwargs)
    >>> h(0)
    h <== called by <module>
    f [1] <== called by g <== h
    >>> h(10, 17, 19, z=100)
    h <== called by <module>
    f [2] <== called by g <== h
    >>> h(20, 3, 4, 6, x=5, y='Yarborough', z=100)
    h <== called by <module>
    f [3] <== called by g <== h
    
Here's the call history in CSV format:

    >>> print(f.stats.history_as_csv)        # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    call_num|a|extra_args|x|kw_args|retval|elapsed_secs|timestamp|prefixed_fname|caller_chain
    1|0|()|1|{}|None|...|...|'f'|['g', 'h']
    2|10|(17, 19)|1|{'z': 100}|None|...|...|'f'|['g', 'h']
    3|20|(3, 4, 6)|5|{'y': 'Yarborough', 'z': 100}|None|...|...|'f'|['g', 'h']
    <BLANKLINE>

Ellipses are for the `elapsed_secs` and `timestamp` fields. As usual, `log_calls` will use whatever names you use for *varargs* parameters
(here, `extra_args` and `kw_args`). Whatever the name of the `kwargs` parameter,
items within that field are guaranteed to be in sorted order.

#####[The *history_as_DataFrame* attribute](id:stats.history_as_DataFrame)
The `stats.history_as_DataFrame` attribute returns the history of a decorated
function as a [Pandas](http://pandas.pydata.org) [DataFrame](http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe), 
if the Pandas library is installed. This saves you the intermediate step of 
calling `DataFrame.from_csv` with the proper arguments (and also saves you from 
having to know or care what those are).

If Pandas is not installed, the value of this attribute is `None`.

#####[The *clear_history(max_history=0)* method](id:stats.clear_history)
As you might expect, the `stats.clear_history(max_history=0)` method clears 
the call history of a decorated function. In addition, it resets all running sums:
`num_calls_total` and `num_calls_logged` are reset to 0, and 
`elapsed_secs_logged` is reset to 0.0.

**It is the only way to change the value of the `max_history` setting**, via
the optional keyword parameter for which you can supply any (integer) value,
by default 0.

The function `f` has a nonempty history, as we just saw. Let's clear `f`'s history, setting `max_history` to 33, and check that settings
and `stats` tallies are reset:

    >>> f.stats.clear_history(max_history=33)
    >>> f.log_calls_settings.max_history
    33
    >>> f.stats.num_calls_logged
    0
    >>> f.stats.num_calls_total
    0
    >>> f.stats.elapsed_secs_logged
    0.0

##[The *record_history* decorator](id:record_history-decorator)
The `record_history` decorator is a stripped-down version of `log_calls` which
records calls to a decorated function but writes no messages. You can think
of it as `log_calls` with the `record_history` and `log_call_numbers` settings
always true, and without any of the message-logging apparatus.

`record_history` has only three keyword parameters:

* `enabled`
* `prefix`
* `max_history`

Just as the settings of `log_calls` for a decorated function are accessible
dynamically through the `log_calls_settings` attribute, these settings of
`record_history` are exposed via a `record_history_settings` attribute.
`record_history_settings` is an object of the same type as `log_calls_settings`,
so it has the same methods and behaviors described in the [`log_calls_settings`](#log_call_settings) section.

Functions decorated by `record_history` have a full-featured `stats` attribute,
as described in the [Call history and statistics](#call-history-and-statistics) section.

See the documentation for [`record_history`](http://www.pythonhosted.org/record_history) for examples and tests.

**ATTENTION**: *Like* `log_calls`, `record_history` *has some overhead. So, ***comment it out in production code!** 

####— Brian O'Neill, October-November 2014, NYC
