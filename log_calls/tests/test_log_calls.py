__author__ = "Brian O'Neill"
__version__ = '0.2.3.post1'

from log_calls import log_calls

import doctest
import unittest


#############################################################################
# doctests
#############################################################################

def main_basic():
    """
##[Basic usage](id:Basic-usage)
`log_calls` has many features, and thus many, mostly independent, keyword parameters
(14 in all). This section introduces all but four of them, one at a time,
though of course you can use multiple parameters in any call to the decorator::

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

The two parameters that let you output `log_calls` messages to a `Logger` ([`logger`](#logger-parameter) and [`loglevel`](#loglevel-parameter)) are discussed in [Using loggers](#Logging). The two that determine whether call history is retained ([record_history](#record_history-parameter)), and then how much history ([max_history](#max_history-parameter)), are discussed in [Call history and statistics – the *stats* attribute and the *\*_history* parameters](#call-history-and-statistics).

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

Return values longer than 60 characters are truncated and end with
a trailing ellipsis:

    >>> @log_calls(log_retval=True)
    ... def return_long_str():
    ...     return '*' * 100
    >>> return_long_str()           # doctest: +NORMALIZE_WHITESPACE
    return_long_str <== called by <module>
    return_long_str return value: ************************************************************...
    return_long_str ==> returning to <module>
    '****************************************************************************************************'

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

**NOTE**: *As we'll see later, logging for a decorated function
can be turned on and off dynamically. In fact,* `log_calls` *also tracks the total
number of calls to a decorated function, and that number is accessible too –
see the section on [the* `stats.num_calls_total` *attribute](#stats.num_calls_total).
When the* `log_call_numbers` *setting is true, the call number displayed is
the logged call number - the rank of that call among the calls to the function
when logging has been enabled. For example, suppose you call* `f` *17 times with logging
enabled and with* `log_call_numbers` *enabled; then you turn logging off and call* `f`
*3 times; finally you re-enable logging and call* `f` *again: the number displayed will
be 18, not 21.*

###[The *log_elapsed* parameter (default – *False*)](id:log_elapsed-parameter)
For performance profiling, you can measure the time it took a function to execute
by using the `log_elapsed` keyword. When true, `log_calls` reports the time the
decorated function took to complete, in seconds:

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
The `indent` parameter, when true, indents each new level of logged messages
by 4 spaces, providing a visualization of the call hierarchy.
(`log_calls` indents only when using `print`, not when [using loggers](#Logging).)

A decorated function's logged output is indented only as much as is necessary.
Here, the even numbered functions don't indent, so the indented functions
that they call are indented just one level more than their "inherited"
indentation level:

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
a call to, and a return from, the method; when reporting the method's return
value; and when the method is at the end of a [call or return chain](#Call-chains).

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

The test suite `tests/test_log_calls_more.py` contains more examples of using
`log_calls` with methods of all kinds – instance methods, classmethods and staticmethods.

###[The *file* parameter (default - *sys.stdout*)](id:file-parameter)
The `file` parameter specifies a stream (an instance of `io.TextIOBase`) to which
`log_calls` will print its messages. This value is supplied to the `file` keyword
parameter of the `print` function, and, like that parameter, its default value is
`sys.stdout`. This parameter is ignored if you've supplied a logger for output
using the [`logger`](#logger-parameter) parameter.

If your program writes to the console a lot, you may not want `log_calls` messages
interspersed with your real output: your understanding of both logically distinct
streams can be compromised, so, better to make them two actually distinct streams.
It can also be advantageous to gather all, and only all, of the log_calls messages
in one place. You can use `indent=True` with a file, and the indentations will
appear as intended, whereas that's not possible with loggers.

It's not possible to test this feature with doctest (in fact, there are subtleties
to supporting this feature and using doctest at all), so we'll just give an example
of writing to `stderr`, and reproduce the output:

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

    """
    pass


def main_logging():
    """
##[Using loggers](id:Logging)
`log_calls` works well with loggers obtained from Python's `logging` module.
First, we'll set up a logger with a single handler that writes to the console.
Because `doctest` doesn't capture output written to `stderr` (the default stream
to which console handlers write), we'll send the console handler's output to
`stdout`, using the format `<loglevel>:<loggername>:<message>`.

    >>> import logging
    >>> import sys
    >>> ch = logging.StreamHandler(stream=sys.stdout)
    >>> c_formatter = logging.Formatter('%(levelname)8s:%(name)s:%(message)s')
    >>> ch.setFormatter(c_formatter)
    >>> logger = logging.getLogger('a_logger')
    >>> logger.addHandler(ch)
    >>> logger.setLevel(logging.DEBUG)

###The *logger* parameter (default – *None*)

The `logger` keyword parameter tells `log_calls` to write its output using
that logger rather than the `print` function:

    >>> @log_calls(logger=logger)
    ... def somefunc(v1, v2):
    ...     logger.debug(v1 + v2)
    >>> somefunc(5, 16)             # doctest: +NORMALIZE_WHITESPACE
    DEBUG:a_logger:somefunc <== called by <module>
    DEBUG:a_logger:    arguments: v1=5, v2=16
    DEBUG:a_logger:21
    DEBUG:a_logger:somefunc ==> returning to <module>

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

###The *loglevel* parameter (default – *logging.DEBUG*)

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

The use of loggers, and of these parameters, is explored further in the later
example [Using a logger with multiple handlers that have different loglevels](#logging-multiple-handlers).
    """
    pass


def main__call_chains():
    """
##Call chains

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
intermediate decorated function that has logging disabled:

    >>> @log_calls()
    ... def e(): pass
    >>> def not_decorated_call_e(): e()
    >>> @log_calls()
    ... def f(): not_decorated_call_e()
    >>> def not_decorated_call_f(): f()
    >>> @log_calls(enabled=False, log_call_numbers=True)
    ... def g(): not_decorated_call_f()
    >>> @log_calls()
    ... def h(): g()
    >>> h()
    h <== called by <module>
    f <== called by not_decorated_call_f <== g <== h
    e <== called by not_decorated_call_e <== f
    e ==> returning to not_decorated_call_e ==> f
    f ==> returning to not_decorated_call_f ==> g ==> h
    h ==> returning to <module>

###[Another *indent* example](id:indent-parameter-another)
In the next example, `g3` has logging disabled, so calls to it are not logged.
`log_calls` chases back to the nearest *enabled* decorated function, so that there
aren't gaps between call chains. The indentation levels are as you'd hope them to be:

    >>> @log_calls(indent=True)
    ... def g1():
    ...     pass
    >>> def g2():
    ...     g1()
    >>> @log_calls(enabled=False, indent=True)    # not logged, causes no indentation for g1
    ... def g3():
    ...     g2()
    >>> @log_calls(indent=True)
    ... def g4():
    ...     g3()
    >>> @log_calls(indent=True)
    ... def g5():
    ...     g4()
    >>> g5()
    g5 <== called by <module>
        g4 <== called by g5
            g1 <== called by g2 <== g3 <== g4
            g1 ==> returning to g2 ==> g3 ==> g4
        g4 ==> returning to g5
    g5 ==> returning to <module>

We'll continue to use `indent` throughout this section.

###Call chains and inner functions

When chasing back along the stack, `log_calls` also detects inner functions
that it has decorated:

    >>> @log_calls(indent=True)
    ... def h0(z):
    ...     pass
    >>> def h1(x):
    ...     @log_calls(indent=True)
    ...     def h1_inner(y):
    ...         h0(x*y)
    ...     return h1_inner
    >>> def h2():
    ...     h1(2)(3)
    >>> def h3():
    ...     h2()
    >>> def h4():
    ...     @log_calls(indent=True)
    ...     def h4_inner():
    ...         h3()
    ...     return h4_inner
    >>> @log_calls(indent=True)
    ... def h5():
    ...     h4()()
    >>> h5()
    h5 <== called by <module>
        h4_inner <== called by h5
            h1_inner <== called by h2 <== h3 <== h4_inner
                arguments: y=3
                h0 <== called by h1_inner
                    arguments: z=6
                h0 ==> returning to h1_inner
            h1_inner ==> returning to h2 ==> h3 ==> h4_inner
        h4_inner ==> returning to h5
    h5 ==> returning to <module>

... even when the inner function is called from within the outer function
it's defined in:

    >>> @log_calls(indent=True)
    ... def j0():
    ...     pass
    >>> def j1():
    ...     j0()
    >>> def j2():
    ...     @log_calls(indent=True)
    ...     def j2_inner():
    ...         j1()
    ...     j2_inner()
    >>> @log_calls(indent=True)
    ... def j3():
    ...     j2()
    >>> j3()
    j3 <== called by <module>
        j2_inner <== called by j2 <== j3
            j0 <== called by j1 <== j2_inner
            j0 ==> returning to j1 ==> j2_inner
        j2_inner ==> returning to j2 ==> j3
    j3 ==> returning to <module>

###Call chains and *log_call_numbers*
If a decorated function `g` calls another decorated function `f`,
and if `f` is enabled and has `log_call_numbers` set to true,
then the call number of f will be displayed in the call chain:

    >>> @log_calls()
    ... def f(): pass
    >>> def not_decorated(): f()
    >>> @log_calls(log_call_numbers=True)
    ... def g(): not_decorated()
    >>> g()
    g [1] <== called by <module>
    f <== called by not_decorated <== g [1]
    f ==> returning to not_decorated ==> g [1]
    g [1] ==> returning to <module>

###[Indentation and call numbers with recursion](id:recursion-example)
These features are especially useful in recursive and mutually recursive
situations. We have to use `OrderedDict`s here because of doctest:

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

**NOTE**: *The optional* `key` *parameter is for instructional purposes,
so you can see the key that's paired with the value of* `d` *in the caller's
dictionary. Typically the signature of this function would be just* `def depth(d)`,
*and the recursive case would return* `max(map(depth, d.values())) + 1`.

    """
    pass


def main__log_message():
    """
`log_calls` exposes the method it uses to write its messages, `log_message`,
whose full signature is:

    `log_message(msg, *msgs, sep=' ',
                 extra_indent_level=1, prefix_with_name=False)`

This method takes one or more "messages" (anything you want to see as a string),
and writes one final output message formed by joining messages separated by `sep`.

`extra_indent_level` is a number of 4-columns wide *indent levels* specifying
where to begin writing that message. This value * 4 is an offset in columns
from the left margin of the visual frame established by log_calls – that is,
an offset from the column in which the function entry/exit messages begin. The default
of 1 aligns the message with the "arguments: " line of `log_calls`'s output.

`prefix_with_name` is a bool. If true, the final message is prefaced with the
possibly prefixed name of the function (using the `prefix` setting),
plus possibly its call number in  square brackets (if the `log_call_numbers` setting
is true.

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
    ...                       % (n, "odd" if n%2 else "even"))
    ...         print("*** (n=%d) We'll be right back, after this:" % n)
    ...         f(n-1)
    ...         print("*** (n=%d) We're back." % n)
    >>> f(2)
    f [1] <== called by <module>
        arguments: n=2
    *** n=2 is even,
        but we knew that.
    *** (n=2) We'll be right back, after this:
        f [2] <== called by f [1]
            arguments: n=1
    *** n=1 is odd,
        but we knew that.
    *** (n=1) We'll be right back, after this:
            f [3] <== called by f [2]
                arguments: n=0
    *** Base case n <= 0
            f [3] ==> returning to f [2]
    *** (n=1) We're back.
        f [2] ==> returning to f [1]
    *** (n=2) We're back.
    f [1] ==> returning to <module>

The debugging messages written by `f` literally "stick out", and it gets difficult,
especially in more complex situations with multiple functions and methods,
to figure out who actually wrote which message; hence the "(n=%d)" tag. If instead
`f` uses `log_message`, all of its messages from each invocation align neatly
within the frame presented by `log_calls`. We also take the opportunity to
illustrate the keyword parameters of `log_message`:

    >>> @log_calls(indent=True, log_call_numbers=True)
    ... def f(n):
    ...     if n <= 0:
    ...         f.log_message("Base case n =", n, prefix_with_name=True)
    ...     else:
    ...         f.log_message("n=%d is %s,\\n    but we knew that."
    ...                       % (n, "odd" if n%2 else "even"),
    ...                       prefix_with_name=True)
    ...         f.log_message("We'll be right back", "after this:",
    ...                       sep=", ", prefix_with_name=True)
    ...         f(n-1)
    ...         f.log_message("We're back.", prefix_with_name=True)
    >>> f(2)
    f [1] <== called by <module>
        arguments: n=2
        f [1]: n=2 is even,
            but we knew that.
        f [1]: We'll be right back, after this:
        f [2] <== called by f [1]
            arguments: n=1
            f [2]: n=1 is odd,
                but we knew that.
            f [2]: We'll be right back, after this:
            f [3] <== called by f [2]
                arguments: n=0
                f [3]: Base case n = 0
            f [3] ==> returning to f [2]
            f [2]: We're back.
        f [2] ==> returning to f [1]
        f [1]: We're back.
    f [1] ==> returning to <module>

**NOTES**:

1. *In the example above, `f` accesses one of its attributes added by
`log_calls`, namely, the `log_message()` method. (log_calls in fact adds two
more attributes, discussed in subsequent sections: [`log_calls_settings`]
(#Dynamic-control-log_calls_settings) and [`stats`](#call-history-and-statistics).)
Indeed, any function, and any static method, can access its `log_calls` in the same
syntactically straightforward way. Classmethods and instance methods decorated by
`log_calls` can also use `log_message()`, but each of those kinds of methods requires
its own approach (a little more syntax) to obtaining the `log_calls` wrapper which
hosts the attributes. See the section [Functions and methods accessing their
own *log_calls* attributes](#accessing-own-attrs) for details.*

2. *The keyword parameter `indent_extra` is deprecated, in favor of
`extra_indent_level`; its default value is now `0`, not `4`.
Please convert to `extra_indent_level`, and help `indent_extra` vanish.*
    """
    pass


def main__using_log_calls_settings__dynamic_control_of_settings():
    """
##[Dynamic control of settings using the *log_calls_settings* attribute](id:Dynamic-control-log_calls_settings)

The values given for the parameters of `log_calls`, e.g. `enabled=True`,
`args_sep=" / "`, are set once the decorated function is interpreted.
The values are established once and for all when the Python interpreter
parses the definition of a decorated function and creates a function object.

###[The problem](id:problem)
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

If later you set `Debug = True` and call `foo`, nothing will be written,
because `foo`'s *enabled* setting is bound to the original value
of `DEBUG`, established when the definition was processed:

    >>> DEBUG = True
    >>> foo()       # Still no log_calls output

This is simply how Python processes default values.

###Solutions
`log_calls` provides *two* ways to dynamically control the settings of a decorated function.
This section presents one of them – using `log_calls_settings`. The next section,
on [indirect values](#Indirect-values), discusses another, rather different solution,
one that's more intrusive but which affords even more control.

###The *log_calls_settings* attribute
The `log_calls` decorator adds an attribute `log_calls_settings`
to a decorated function, through which you can access the decorator settings
for that function. This attribute is an object which lets you control
the settings for a decorated function via a mapping (dict-like) interface,
and equivalently, via attributes of the object. The mapping keys and
the attribute names are simply the `log_calls` keywords. `log_calls_settings`
also implements many of the standard `dict` methods for interacting with the
settings in familiar ways.
###The mapping interface and the attribute interface to settings

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

The `log_calls_settings` attribute has a length:

    >>> len(f.log_calls_settings)
    14

Its keys and items can be iterated through:

    >>> keys = []
    >>> for k in f.log_calls_settings: keys.append(k)
    >>> keys                                            # doctest: +NORMALIZE_WHITESPACE
    ['enabled', 'args_sep', 'log_args',
     'log_retval', 'log_elapsed', 'log_exit',
     'indent', 'log_call_numbers',
     'prefix', 'file',
     'logger', 'loglevel',
     'record_history', 'max_history']
    >>> items = []
    >>> for k, v in f.log_calls_settings.items(): items.append((k, v))
    >>> items                                           # doctest: +NORMALIZE_WHITESPACE
    [('enabled', False),   ('args_sep', ', '),    ('log_args', True),
     ('log_retval', True), ('log_elapsed', True), ('log_exit', True),
     ('indent', False),         ('log_call_numbers', False),
     ('prefix', ''),            ('file', None),
     ('logger', None),          ('loglevel', 10),
     ('record_history', False), ('max_history', 0)]

You can use `in` to test for key membership:

    >>> 'enabled' in f.log_calls_settings
    True
    >>> 'no_such_setting' in f.log_calls_settings
    False

As with an ordinary dictionary, attempting to access a nonexistent setting
raises `KeyError`:

    >>> f.log_calls_settings['new_key']                 # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    KeyError: ...

Unlike an ordinary dictionary, you can't add new keys – the `log_calls_settings`
dictionary is closed to new members, and attempts to add one will raise `KeyError`:

    >>> f.log_calls_settings['new_key'] = 'anything'    # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    KeyError: ...

You can use the same keywords as attributes of `log_calls_settings`
instead of as keywords to the mapping interface; they're equivalent:

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
    >>> f()                                     # doctest: +ELLIPSIS
    f [2] <== called by <module>
    f [2] ==> returning to <module>
    91

The only difference is that you *can* add a new attribute to `log_calls_settings`,
simply by using it:

    >>> f.log_calls_settings.new_attr = 'something'
    >>> f.log_calls_settings.new_attr
    'something'

But the new attribute still isn't a decorator setting:

    >>> 'new_attr' in f.log_calls_settings
    False

### The *update()*, *as_OrderedDict()* and *as_dict()* methods
The `log_calls_settings` object provides an `update()` method so that
you can update several settings at once:

    >>> f.log_calls_settings.update(
    ...     log_args=True, log_elapsed=False, log_call_numbers=False,
    ...     log_retval=False)
    >>> _ = f()
    f <== called by <module>
        arguments: <none>
    f ==> returning to <module>

You can retrieve the entire collection of settings as either an `OrderedDict`
using the `as_OrderedDict()` method, or as a `dict` using `as_dict()`.
Either can serve as a snapshot of the settings, so that you can change settings
temporarily, use the new settings, and then restore settings from the snapshot.
in addition to taking keyword arguments, as shown above, the `update()` method
can take one or more dicts – in particular, a dictionary retrieved from one of
the `as_*` methods. For example:

Retrieve settings (here, as an `OrderedDict` because it's more doctest-friendly,
but using `as_dict()` is sufficient):

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
dictionary rather than keywords:

    >>> f.log_calls_settings.update(od)
    >>> od == f.log_calls_settings.as_OrderedDict()
    True

**NOTES**:

1. *The [`max_history`](#max_history-parameter) setting is immutable (no other setting is), and attempts to change it
directly (e.g.* `f.log_calls_settings.max_history = anything`) *raise* `ValueError`.
*Nevertheless, it* is *an item in the retrieved settings dictionaries. To allow for
the use-case just illustrated, `update()` is considerate enough to skip over
immutable settings.*

2. `log_calls` *continues to track call numbers even when it isn't reporting
them. The last call to* `f` *was the 4th, as shown, although the call number of
the 3rd call wasn't displayed.*

    """


def main__indirect_parameter_values__dynamic_control():
    """
##[Dynamic control of settings with indirect values](id:Indirect-values)

Every parameter of `log_calls` except `prefix` and `max_history` can take
two kinds of values: *direct* and *indirect*, which you can think of as
*static* and *dynamic* respectively. Direct/static values are actual values
used when the decorated function is interpreted, e.g. `enabled=True`,
`args_sep=" / "`. As discussed in the previous section on
[`log_call_settings`](#Dynamic-control-log_calls_settings), the values of
parameters are set once and for all when the Python interpreter creates
a function object from the source code of a decorated function. Even if you
use a variable as the value of a setting, subsequently changing the variable's
value has no effect on the decorator's setting.

`log_calls` provides a second way to overcome this limitation. The decorator
lets you specify any parameter
except `prefix` or `max_history` with one level of indirection, by using
*indirect values*: an indirect value is a string that names a keyword argument
*of the decorated function*. It can be an explicit keyword argument present
in the signature of the function, or an implicit keyword argument that ends up
in `**kwargs` (if that's present in the function's signature). When the decorated
function is called, the arguments passed by keyword, and the decorated function's
explicit keyword parameters with default values, are both searched for the named
parameter; if it is found and of the correct type, *its* value is used; otherwise
a default value is used.

To specify an indirect value for a parameter whose normal type is `str` (only
`args_sep`, at present), append an `'='` to the value.  For consistency's sake,
any indirect value can end in a trailing `'='`, which is stripped. Thus,
`enabled='enable_='` indicates an indirect value *to be supplied* by the keyword
(argument or parameter) `enable_` of a decorated function.

So, in:

    >>> @log_calls(args_sep='sep=', prefix="*** ")
    ... def f(a, b, c, sep='|'): pass

`args_sep` has an indirect value which names `f`'s explicit keyword parameter
`sep`, and `prefix` has a direct value as it always does. A call can dynamically
override the default value '|' in the signature of `f` by supplying a value:

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
    ... def func1(a, b, c, **func1_kwargs): pass
    >>> @log_calls(enabled='enable')
    ... def func2(z, **func2_kwargs): func1(z, z+1, z+2, **func2_kwargs)

When the following statement is executed, the calls to both func1 and func2
will be logged:

    >>> func2(17, enable=True)
    func2 <== called by <module>
        arguments: z=17, [**]func2_kwargs={'enable': True}
    func1 <== called by func2
        arguments: a=17, b=18, c=19, [**]func1_kwargs={'enable': True}
    func1 ==> returning to func2
    func2 ==> returning to <module>

whereas neither of the following two statements will trigger logging:

    >>> func2(42, enable=False)     # no log_calls output
    >>> func2(99)                   # no log_calls output

**NOTE**: *This last example illustrates a subtle point:
if you omit the* `enabled` *parameter altogether, logging will occur,
as the default value is (the direct value)* `True`; *however, if you
specify an indirect value for* `enabled` *and the named indirect
keyword is not supplied in a call, then that call* won't *be logged.
In other words, if you specify an indirect value for the* `enabled` *parameter
then the effective default value of the enabled setting is* `False`* --
calls are not logged unless the named parameter is found and its value is true.*

###Controlling format 'from above'

This indirection mechanism allows a calling function to control the appearance
of logged calls to functions lower in the call chain, provided they all use
the same indirect parameter keywords.

In the next example, the separator value supplied to `g` by keyword argument
propagates to `f`. Note that the arguments `42` and `99` end up in `g`'s
positional *varargs* tuple. We've used non-generic names for the *varargs*
to illustrate that whatever you call these parameters, their roles are
unambiguous and `log_calls` will find and use their names:

    >>> @log_calls(args_sep='sep=')
    ... def f(a, b, c, **kwargs): pass


    >>> @log_calls(args_sep='sep=')
    ... def g(a, b, c, *g_args, **g_kwargs):
    ...     f(a, b, c, **g_kwargs)
    >>> g(1,2,3, 42, 99, sep='\\n')       # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    g <== called by <module>
        arguments:
            a=1
            b=2
            c=3
            [*]g_args=(42, 99)
            [**]g_kwargs={'sep': '\\n'}
    f <== called by g
        arguments:
            a=1
            b=2
            c=3
            [**]kwargs={'sep': '\\n'}
    f ==> returning to g
    g ==> returning to <module>

####Controlling indentation 'from above'
Similarly, you can control indentation from above.

    >>> @log_calls(indent='lc_indent', log_call_numbers=True)
    ... def f(n, **kwargs):
    ...     if n <= 0:
    ...         return
    ...     f(n-1, **kwargs)
    >>> @log_calls(indent='lc_indent')
    ... def g(n, **kwargs):
    ...     f(n+1, **kwargs)

Without an indirect value for `indent`, `log_calls` displays this calls to
`f` and `g` in a "flat" way:

    >>> g(1) #, lc_indent=True)
    g <== called by <module>
        arguments: n=1
    f [1] <== called by g
        arguments: n=2
    f [2] <== called by f [1]
        arguments: n=1
    f [3] <== called by f [2]
        arguments: n=0
    f [3] ==> returning to f [2]
    f [2] ==> returning to f [1]
    f [1] ==> returning to g
    g ==> returning to <module>

But the call hierarchy is represented visually when you pass the specified
indirect value:

    >>> g(2, lc_indent=True)
    g <== called by <module>
        arguments: n=2, [**]kwargs={'lc_indent': True}
        f [4] <== called by g
            arguments: n=3, [**]kwargs={'lc_indent': True}
            f [5] <== called by f [4]
                arguments: n=2, [**]kwargs={'lc_indent': True}
                f [6] <== called by f [5]
                    arguments: n=1, [**]kwargs={'lc_indent': True}
                    f [7] <== called by f [6]
                        arguments: n=0, [**]kwargs={'lc_indent': True}
                    f [7] ==> returning to f [6]
                f [6] ==> returning to f [5]
            f [5] ==> returning to f [4]
        f [4] ==> returning to g
    g ==> returning to <module>

###Enabling with *int*s rather than *bool*s

Sometimes it's desirable for a function to print or log debugging messages
as it executes. It's the oldest form of debugging! Instead of a simple `bool`,
you can use a nonnegative `int` as the enabling value and treat it as a level
of verbosity.

    >>> DEBUG_MSG_BASIC = 1
    >>> DEBUG_MSG_VERBOSE = 2
    >>> DEBUG_MSG_MOREVERBOSE = 3  # etc.
    >>> @log_calls(enabled='debuglevel=')
    ... def do_stuff_with_commentary(*args, debuglevel=0):
    ...     if debuglevel >= DEBUG_MSG_VERBOSE:
    ...         print("*** extra debugging info ***")

No output:

    >>> do_stuff_with_commentary()

Only `log_calls` output:

    >>> do_stuff_with_commentary(debuglevel=DEBUG_MSG_BASIC)
    do_stuff_with_commentary <== called by <module>
        arguments: debuglevel=1
    do_stuff_with_commentary ==> returning to <module>

`log_calls` output plus the function's debugging reportage:

    >>> do_stuff_with_commentary(debuglevel=DEBUG_MSG_VERBOSE)
    do_stuff_with_commentary <== called by <module>
        arguments: debuglevel=2
    *** extra debugging info ***
    do_stuff_with_commentary ==> returning to <module>

The [metaclass example](#A-metaclass-example) below also makes use of this technique.

### Using *log_calls_settings* to set indirect values
is perfectly legitimate:

    >>> @log_calls(enabled=False)
    ... def g(*args, **kwargs):
    ...     return sum(args)
    >>> g.log_calls_settings.enabled = 'enable_log_calls='
    >>> g(1, 2, 3, enable_log_calls=True)
    g <== called by <module>
        arguments: [*]args=(1, 2, 3), [**]kwargs={'enable_log_calls': True}
    g ==> returning to <module>
    6
    """
    pass


def main_call_history_and_statistics():
    """
##[Call history and statistics – the *stats* attribute and the *\*_history* parameters](id:call-history-and-statistics)
`log_calls` always collects a few basic statistics about calls to a decorated
function. It can collect the entire history of calls to a function if asked
to (using the [`record_history` parameter](#stats.record_history-parameter)).
The statistics and history are accessible via the `stats` attribute
which `log_calls` adds to a decorated function.

###The *stats* attribute
The `stats` attribute is an object of class `ClassInstanceAttrProxy`, defined
in `log_calls/proxy_descriptors.py`. That class has its own test suite,
in `log_calls/tests/test_proxy_descriptors.py`; here, we only have to
test and illustrate its use by `log_calls`.

Let's define a decorated function with call number logging turned on,
but with exit logging turned off for brevity:

    >>> @log_calls(log_call_numbers=True, log_exit=False)
    ... def f(a, *args, x=1, **kwargs): pass

Now call it 2 times:

    >>> f(0)
    f [1] <== called by <module>
        arguments: a=0
        defaults:  x=1
    >>> f(1, 100, 101, x=1000, y=1001)
    f [2] <== called by <module>
        arguments: a=1, [*]args=(100, 101), x=1000, [**]kwargs={'y': 1001}

and start to explore the `stats` attribute.

####The *stats.num_calls_logged* attribute
The `stats.num_calls_logged` attribute contains the number of the most
recent logged call to a decorated function. Thus, `f.stats.num_calls_logged`
will equal 2:

    >>> f.stats.num_calls_logged
    2

This counter gets incremented when a decorated function is called that has
logging enabled, even if its `log_call_numbers` setting is false.

####[The *stats.num_calls_total* attribute](id:stats.num_calls_total)
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

As a further illustration, let's re-enable logging for `f` and call it again.
The displayed call number will the number of the *logged* call, 3, the same
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

####The *stats.elapsed_secs_logged* attribute
The `stats.elapsed_secs_logged` attribute holds the sum of the elapsed times of
all logged calls to a decorated function, in seconds. It's not possible to doctest
this so we'll just exhibit its value for the 3 logged calls to `f` above:

    >>> f.stats.elapsed_secs_logged   # doctest: +SKIP
    6.67572021484375e-06

###[The *record_history* parameter (default – *False*)](id:record_history-parameter)
When the `record_history` setting is true for a decorated function `f`, `log_calls` will
retain a sequence of records holding the details of each logged call to that function.
That history is accessible via attributes of the `stats` object. We'll illustrate
with a familiar example.

Let's define `f` just as before, but with `record_history` set to true:

    >>> @log_calls(record_history=True, log_call_numbers=True, log_exit=False)
    ... def f(a, *args, x=1, **kwargs): pass

With logging enabled, let's call f three times:

    >>> f(0)
    f [1] <== called by <module>
        arguments: a=0
        defaults:  x=1
    >>> f(1, 100, 101, x=1000, y=1001)
    f [2] <== called by <module>
        arguments: a=1, [*]args=(100, 101), x=1000, [**]kwargs={'y': 1001}
    >>> f(10, 20, z=5000)
    f [3] <== called by <module>
        arguments: a=10, [*]args=(20,), [**]kwargs={'z': 5000}
        defaults:  x=1

No surprises there. But now, f has a call history, which we'll examine next.

####The *stats.history* attribute
The `stats.history` attribute of a decorated function provides the call history
of logged calls to the function as a tuple of records. Here's `f`'s call history,
in human-readable form (ok, almost human-readable!). The CSV presentation pairs
the `argnames` with their values `argvals` (the `argnames` become column headings),
making it even more human-readable, especially when viewed in a program that
presents CSVs nicely:

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

#####The *CallRecord* namedtuple
For the record, the records that comprise a decorated function's history are
`namedtuple`s of type `CallRecord`, whose fields are:

    call_num
    argnames
    argvals
    varargs
    explicit_kwargs
    defaulted_kwargs
    implicit_kwargs
    retval
    elapsed_secs
    timestamp
    prefixed_func_name
    caller_chain

By now, the significance of each field should be clear.

###[The *max_history* parameter (default – 0)](id:max_history-parameter)
The `max_history` parameter determines how many call history records are retained
for a decorated function whose call history is recorded. If this value is 0
(the default) or negative, unboundedly many records are retained (unless or until
you set the `record_history` setting to false, or call the
[`stats.clear_history()`](#stats.clear_history) method). If the value of `max_history`
is > 0, `log_calls` will retain at most that many records, discarding the oldest
records to make room for newer ones if the history reaches capacity.

An example:

    >>> @log_calls(record_history=True, max_history=2,
    ...            log_args=False, log_exit=False, log_call_numbers=True)
    ... def g(a): pass
    >>> for i in range(3): g(i)
    g [1] <== called by <module>
    g [2] <== called by <module>
    g [3] <== called by <module>

Here's `g`'s call history:

    >>> print('\\n'.join(map(str, g.stats.history)))    # doctest: +SKIP
    CallRecord(call_num=2, argnames=['a'], argvals=(1,), varargs=(),
                           explicit_kwargs=OrderedDict(),
                           defaulted_kwargs=OrderedDict(), implicit_kwargs={},
                           retval=None, elapsed_secs=2.1457672119140625e-06,
                           timestamp='10/28/14 20:51:12.376714',
                           prefixed_func_name='g', caller_chain=['<module>'])
    CallRecord(call_num=3, argnames=['a'], argvals=(2,), varargs=(),
                           explicit_kwargs=OrderedDict(),
                           defaulted_kwargs=OrderedDict(), implicit_kwargs={},
                           retval=None, elapsed_secs=2.1457672119140625e-06,
                           timestamp='10/28/14 20:51:12.376977',
                           prefixed_func_name='g', caller_chain=['<module>'])

The first call (`call_num=1`) was discarded to make room for the last call
(`call_num=3`) because the call history size is set to 2.

You cannot change `max_history` using the mapping interface or the attribute
of the same name; attempts to do so raise `ValueError`:

    >>> g.log_calls_settings.max_history = 17   # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: ...

    >>> g.log_calls_settings['max_history'] = 17   # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: ...

The only way to change its value is with the [`clear_history`](#clear_history-method) method.

####The *stats.history_as_csv* attribute
The value `stats.history_as_csv` attribute is a text representation
of a decorated function's call history in CSV format. You can save this string
and import it into the program or tool of your choice for further analysis.
CSV format is only partially human-friendly, but this representation
breaks out each argument into its own column, throwing away information about
whether an argument's value was passed or is a default.

    >>> print(g.stats.history_as_csv)        # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    call_num|a|retval|elapsed_secs|timestamp|prefixed_fname|caller_chain
    2|1|None|...|...|'g'|['<module>']
    3|2|None|...|...|'g'|['<module>']
    <BLANKLINE>

Ellipses above are for the `elapsed_secs` and `timestamp` fields.

The CSV separator is '|' rather than ',' because some of the fields – `args`,  `kwargs`
and `caller_chain` – use commas intrinsically. Let's examine one more `history_as_csv`
for a function that has all of those fields:

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
    >>> print(f.stats.history_as_csv)        # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    call_num|a|extra_args|x|kw_args|retval|elapsed_secs|timestamp|prefixed_fname|caller_chain
    1|0|()|1|{}|None|...|...|'f'|['g', 'h']
    2|10|(17, 19)|1|{'z': 100}|None|...|...|'f'|['g', 'h']
    3|20|(3, 4, 6)|5|{'y': 'Yarborough', 'z': 100}|None|...|...|'f'|['g', 'h']
    <BLANKLINE>

As usual, `log_calls` will use whatever names you use for *varargs* parameters
(here, `extra_args` and `kw_args`). Whatever the name of the `kwargs` parameter,
items within that field are guaranteed to be in sorted order (otherwise this
last example would sometimes fail as a doctest).

####[The *stats.clear_history(max_history=0)* method](id:clear_history-method)
As you might expect, the `stats.clear_history(max_history=0)` method clears
the call history of a decorated function. In addition, it resets all counters:
`num_calls_total` and `num_calls_logged` are reset to 0, and
`elapsed_secs_logged` is reset to 0.0.

**It is the only way to change the value of the `max_history` setting**, via
the optional keyword parameter for which you can supply any (integer) value,
by default 0.

The function `f` has a nonempty history, as we just saw. Let's confirm the
values of all relevant settings and counters:

    >>> f.log_calls_settings.max_history
    0
    >>> f.stats.num_calls_logged
    3
    >>> f.stats.num_calls_total
    3
    >>> f.stats.elapsed_secs_logged     # doctest: +SKIP
    1.4066696166992188e-05

Now let's clear `f`'s history, setting `max_history` to 33, and check that settings
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

    """
    pass


def main__realistic_logging_example():
    """
##[A realistic logging example – multiple handlers with different loglevels](id:logging-multiple-handlers)

#The basic setup:
#
    # This shorter setup doesn't work on 3.4.0 on Linux (Ubuntu 12.04).
    # Perhaps the new-in-3.3 handlers parameter to basicConfig
    # regressed or anyway wasn't working properly.

    # >>> import logging
    # >>> import sys
    # >>> ch = logging.StreamHandler(stream=sys.stdout)
    # >>> logging.basicConfig(handlers=[ch])
    # >>> logger = logging.getLogger('mylogger')
    # >>> logger.setLevel(logging.DEBUG)

First let's set up a logging with a console handler that writes to `stdout`:

    >>> import logging
    >>> import sys
    >>> ch = logging.StreamHandler(stream=sys.stdout)
    >>> c_formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    >>> ch.setFormatter(c_formatter)
    >>> logger = logging.getLogger('mylogger')
    >>> logger.addHandler(ch)
    >>> logger.setLevel(logging.DEBUG)

Now let's add another handler, also sent to `stdout` but best thought of as writing
to a log file. We'll set up the existing console handler with level `INFO`, and
the "file" handler with level `DEBUG` - a typical setup: you want to log all
details to the file, but you only want to write more important messages to
the console.

    >>> fh = logging.StreamHandler(stream=sys.stdout)
    >>> f_formatter = logging.Formatter('[FILE] %(levelname)8s:%(name)s: %(message)s')
    >>> fh.setFormatter(f_formatter)
    >>> fh.setLevel(logging.DEBUG)
    >>> logger.addHandler(fh)
    >>> ch.setLevel(logging.INFO)

Suppose we have two functions: one that's lower-level/often-called,
and another that's "higher-level"/infrequently called.

    >>> @log_calls(logger=logger, loglevel=logging.DEBUG)
    ... def popular():
    ...     pass
    >>> @log_calls(logger=logger, loglevel=logging.INFO)
    ... def infrequent():
    ...     popular()

Set logger level to `DEBUG` –
  the console handler logs calls only for `infrequent`,
  but the "file" handler logs calls for both functions.

    >>> logger.setLevel(logging.DEBUG)
    >>> infrequent()       # doctest: +NORMALIZE_WHITESPACE
    INFO:mylogger:infrequent <== called by <module>
    [FILE]     INFO:mylogger: infrequent <== called by <module>
    [FILE]    DEBUG:mylogger: popular <== called by infrequent
    [FILE]    DEBUG:mylogger: popular ==> returning to infrequent
    INFO:mylogger:infrequent ==> returning to <module>
    [FILE]     INFO:mylogger: infrequent ==> returning to <module>

Now set logger level to `INFO` –
  both handlers logs calls only for `infrequent`:

    >>> logger.setLevel(logging.INFO)
    >>> infrequent()       # doctest: +NORMALIZE_WHITESPACE
    INFO:mylogger:infrequent <== called by <module>
    [FILE]     INFO:mylogger: infrequent <== called by <module>
    INFO:mylogger:infrequent ==> returning to <module>
    [FILE]     INFO:mylogger: infrequent ==> returning to <module>
    """
    pass


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# A_meta, a metaclass
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
from collections import OrderedDict

separator = '\n'    # default ', ' gives rather long lines

A_DBG_BASIC = 1
A_DBG_INTERNAL = 2

# Demonstrates a few techniques:
#       * How to get at log_calls_settings methods for a (meta)method
#         from inside that method
#       * Use of the (new in 0.2.1a) log_message(msg) method,
#         which handles global indentation for you.
#         Useful for verbose debugees that want their blather to align nicely

class A_meta(type):
    @classmethod
    @log_calls(prefix='A_meta.', args_sep=separator, enabled='A_debug=', log_retval=True)
    def __prepare__(mcs, cls_name, bases, *, A_debug=0, **kwargs):
        super_dict = super().__prepare__(cls_name, bases, **kwargs)
        if A_debug >= A_DBG_INTERNAL:
            # note use of .__func__ to get at decorated fn inside the classmethod
            logging_fn = mcs.__prepare__.__func__.log_message
            logging_fn("    mro =", mcs.__mro__)
            logging_fn("    dict from super() = %r" % super_dict)
        super_dict = OrderedDict(super_dict)
        super_dict['key-from-__prepare__'] = 1729
        return super_dict

    @log_calls(prefix='A_meta.', args_sep=separator, enabled='A_debug=')
    def __new__(mcs, cls_name, bases, cls_members: dict, *, A_debug=0, **kwargs):
        cls_members['key-from-__new__'] = "No, Hardy!"
        if A_debug >= A_DBG_INTERNAL:
            logging_fn = mcs.__new__.log_message
            logging_fn("    calling super() with cls_members =", cls_members)
        return super().__new__(mcs, cls_name, bases, cls_members, **kwargs)

    @log_calls(prefix='A_meta.', args_sep=separator, enabled='A_debug=')
    def __init__(cls, cls_name, bases, cls_members: dict, *, A_debug=0, **kwargs):
        if A_debug >= A_DBG_INTERNAL:
            logging_fn = cls._get_init_wrapper().log_message
            logging_fn("    cls.__mro__:", cls.__mro__)
            logging_fn("    type(cls).__mro__[1] =", type(cls).__mro__[1])
        try:
            super().__init__(cls_name, bases, cls_members, **kwargs)
        except TypeError as e:
            # call type.__init__
            if A_debug >= A_DBG_INTERNAL:
                logging_fn("    calling type.__init__ with no kwargs")
            type.__init__(cls, cls_name, bases, cls_members)

    @classmethod
    def _get_init_wrapper(cls):
        return cls.__dict__['__init__']


def main__metaclass_example():
    """
##[A metaclass example](id:A-metaclass-example)

The class `A_meta` is a metaclass: it derives from `type`,
and defines (overrides) methods `__prepare__`, `__new__` and `__init__`.
All of these `log_calls`-decorated methods access their `log_calls` wrapper,
two of them doing so in roundabout ways. The classmethod `__prepare__`
has to interpose `__func__` in order to get at the `log_calls` wrapper inside
the classmethod wrapper. The `__init__` method has to jump through a different
hoop in order to access its wrapper. Nevertheless, all
the methods succeed at doing so, so that they can write their messages using
[the indent-aware method `log_message`](#log_message).

All of `A_meta`'s methods take an explicit keyword parameter `A_debug`,
used as the indirect value of the `log_calls` keyword parameter `enabled`.
The methods treat it as an integer verbosity level: when its value is above
When we include `A_debug=True` as a keyword argument to a class that
uses `A_meta` as its metaclass, that argument gets passed to all of
`A_meta`'s methods, so calls to them will be logged, and those methods
will also print extra debugging information:

    >>> class A(metaclass=A_meta, A_debug=A_DBG_INTERNAL):    # doctest: +NORMALIZE_WHITESPACE
    ...     pass
    A_meta.__prepare__ <== called by <module>
        arguments:
            mcs=<class '__main__.A_meta'>
            cls_name='A'
            bases=()
            A_debug=2
        mro = (<class '__main__.A_meta'>, <class 'type'>, <class 'object'>)
        dict from super() = {}
        A_meta.__prepare__ return value: OrderedDict([('key-from-__prepare__', 1729)])
    A_meta.__prepare__ ==> returning to <module>
    A_meta.__new__ <== called by <module>
        arguments:
            mcs=<class '__main__.A_meta'>
            cls_name='A'
            bases=()
            cls_members=OrderedDict([('key-from-__prepare__', 1729),
                                     ('__module__', '__main__'),
                                     ('__qualname__', 'A')])
            A_debug=2
        calling super() with cls_members = OrderedDict([('key-from-__prepare__', 1729),
                                                        ('__module__', '__main__'),
                                                        ('__qualname__', 'A'),
                                                        ('key-from-__new__', 'No, Hardy!')])
    A_meta.__new__ ==> returning to <module>
    A_meta.__init__ <== called by <module>
        arguments:
            cls=<class '__main__.A'>
            cls_name='A'
            bases=()
            cls_members=OrderedDict([('key-from-__prepare__', 1729),
                                     ('__module__', '__main__'),
                                     ('__qualname__', 'A'),
                                     ('key-from-__new__', 'No, Hardy!')])
            A_debug=2
        cls.__mro__: (<class '__main__.A'>, <class 'object'>)
        type(cls).__mro__[1] = <class 'type'>
    A_meta.__init__ ==> returning to <module>

If we had passed `A_debug=A_DBG_BASIC`, then only `log_calls` output would have
been printed: the metaclass methods would not have printed their extra debugging
statements.

If we pass `A_debug=0` (or omit it), we get no printed output at all either from
`log_calls` or from `A_meta`'s methods:

    >>> class AA(metaclass=A_meta, A_debug=0):    # no output
    ...     pass
    """

# SURGERY:
main__metaclass_example.__doc__ = \
    main__metaclass_example.__doc__.replace("__main__", __name__)


def main__functions_and_methods_accessing_their_attrs():
    """
## [Functions and methods accessing their own *log_calls* attributes](id:accessing-own-attrs)
At times you may want a function or method to access the attributes
added for it by `log_calls`. We've seen examples of this, where
[global functions](#log_message) and [methods](#A-metaclass-example) use the indent-aware method `log_message`
to write debugging messages that align properly with those of `log_calls`.
In the metaclass example, two of the methods – an instance method, and
a classmethod – had to perform extra legerdemain in order to get at their
attributes. Happily, those are the only special cases.

This section collects all the different cases of functions and methods
accessing their `log_calls` attributes.

NOTE: The most artificial aspect of the examples in this section
is that the functions and methods all access their `stats` attribute.
This might be called "excessive introspection", and is probably seldom
useful: when a log_calls-decorated function executes, its call counters
(`stats.num_calls_logged` and `stats.num_calls_total`) have been incremented,
but, as it hasn't yet returned, the value of `stats.elapsed_secs_logged`
(as well as its history) remains as they was before the call began.
We confirm and test this claim in the global and inner functions examples
below.

### [Global functions and inner functions accessing their attributes](id:global-and-inner-functions-accessing-attrs)
Global functions and inner functions can access within their own bodies
the attributes that `log_calls` adds for them (`log_calls_settings`, `stats`, `log_message()`)
using the same syntax that works outside of their bodies.

####[Global function accessing its attributes](id:global-function-accessing-attrs)
A global function can just use the usual syntax:

    >>> @log_calls(enabled=2)
    ... def f():
    ...     f.log_message("f.log_calls_settings.enabled =", f.log_calls_settings.enabled,
    ...                   prefix_with_name=True)
    ...     f.log_message("This is call number", f.stats.num_calls_logged)
    ...     f.log_message("f.stats.elapsed_secs_logged is still", f.stats.elapsed_secs_logged)
    >>> f()
    f <== called by <module>
        f: f.log_calls_settings.enabled = 2
        This is call number 1
        f.stats.elapsed_secs_logged is still 0.0
    f ==> returning to <module>

#### [Inner function accessing its attributes](id:inner-function-accessing-attrs)
Similarly, an inner function can just do the usual thing:

    >>> @log_calls()
    ... def outer(x):
    ...     @log_calls(enabled=7)
    ...     def inner(y):
    ...         inner.log_message("inner.log_calls_settings.enabled =", inner.log_calls_settings.enabled)
    ...         inner.log_message("call number", inner.stats.num_calls_logged, prefix_with_name=True)
    ...         inner.log_message("elapsed_secs_logged =", inner.stats.elapsed_secs_logged, prefix_with_name=True)
    ...         return x + y
    ...     outer.log_message("inner enabled =", inner.log_calls_settings.enabled, prefix_with_name=True)
    ...     outer.log_message("Before call to inner:", extra_indent_level=-1, prefix_with_name=True)
    ...     outer.log_message("its call number (inner.stats.num_calls_logged) =", inner.stats.num_calls_logged)
    ...     outer.log_message("its elapsed_secs_logged =", inner.stats.elapsed_secs_logged)
    ...     inner(2 * x)
    ...     outer.log_message("After call to inner:", extra_indent_level=-1, prefix_with_name=True)
    ...     outer.log_message("its call number =", inner.stats.num_calls_logged)
    ...     outer.log_message("its elapsed_secs_logged =", inner.stats.elapsed_secs_logged)

    >>> outer(3)                # doctest: +ELLIPSIS
    outer <== called by <module>
        arguments: x=3
        outer: inner enabled = 7
    outer: Before call to inner:
        its call number (inner.stats.num_calls_logged) = 0
        its elapsed_secs_logged = 0.0
    inner <== called by outer
        arguments: y=6
        inner.log_calls_settings.enabled = 7
        inner: call number 1
        inner: elapsed_secs_logged = 0.0
    inner ==> returning to outer
    outer: After call to inner:
        its call number = 1
        its elapsed_secs_logged = ...
    outer ==> returning to <module>

### [Methods accessing their attributes](id:methods-accessing-attrs)
Static methods can access their log_calls-added attributes in a straightforward
way. However, the other kinds of methods – class methods and instance methods –
are different: each requires a unique kind of subterfuge to access its `log_calls`
wrapper and thereby its `log_calls` attributes.

Here's a class exhibiting the full range of possibilities:

    >>> class X():
    ...     # Instance methods, including __init__, can obtain their wrappers
    ...     # from their class, via self.__class__.__dict__[method_name]
    ...     @log_calls()
    ...     def __init__(self):
    ...         wrapper = self.__class__.__dict__['__init__']
    ...         logging_fn = wrapper.log_message
    ...         logging_fn(wrapper.log_calls_settings.enabled)
    ...         logging_fn(wrapper.stats.num_calls_logged)
    ...
    ...     @log_calls(enabled=2)
    ...     def my_method(self):
    ...         wrapper = self.__class__.__dict__['my_method']
    ...         logging_fn = wrapper.log_message
    ...         logging_fn(wrapper.log_calls_settings.enabled)
    ...         logging_fn(wrapper.stats.num_calls_logged)
    ...
    ...     # A classmethod can get at its attributes from its own body,
    ...     # via cls.<classmethod>.__func__
    ...     @classmethod
    ...     @log_calls(enabled=12)
    ...     def my_classmethod(cls):
    ...         logging_fn = cls.my_classmethod.__func__.log_message
    ...         logging_fn(cls.my_classmethod.__func__.log_calls_settings.enabled)
    ...         logging_fn(cls.my_classmethod.__func__.stats.num_calls_logged)
    ...
    ...     # A staticmethod can access its attributes from its own body
    ...     # in the obvious way, via <class>.<staticmethod>
    ...     @staticmethod
    ...     @log_calls(enabled=22)
    ...     def my_staticmethod():
    ...         logging_fn = X.my_staticmethod.log_message
    ...         logging_fn(X.my_staticmethod.log_calls_settings.enabled)
    ...         logging_fn(X.my_staticmethod.stats.num_calls_logged)

#### [Instance method tests](id:instance-method-accessing-attrs)

    >>> x = X()                    # doctest: +ELLIPSIS
    __init__ <== called by <module>
        arguments: self=<__main__.X object at ...>
        True
        1
    __init__ ==> returning to <module>

    >>> x.my_method()               # doctest: +ELLIPSIS
    my_method <== called by <module>
        arguments: self=<__main__.X object at ...>
        2
        1
    my_method ==> returning to <module>

#### [Class method test](id:class-method-accessing-attrs)

    >>> x.my_classmethod()      # or X.my_classmethod()
    my_classmethod <== called by <module>
        arguments: cls=<class '__main__.X'>
        12
        1
    my_classmethod ==> returning to <module>

#### [Static method test](id:static-method-accessing-attrs)

    >>> x.my_staticmethod()     # or X.my_staticmethod()
    my_staticmethod <== called by <module>
        22
        1
    my_staticmethod ==> returning to <module>
    """
    pass

# SURGERY:
main__functions_and_methods_accessing_their_attrs.__doc__ = \
    main__functions_and_methods_accessing_their_attrs.__doc__.replace("__main__", __name__)

##############################################################################
# end of tests.
##############################################################################

# For unittest integration
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    return tests


if __name__ == "__main__":

    doctest.testmod()   # (verbose=True)

    # unittest.main()
