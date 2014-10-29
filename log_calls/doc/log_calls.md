#*log_calls* <br>A decorator for debugging and profiling

---    
`log_calls` is a Python 3 decorator that can log a great deal of useful information about calls to a decorated function, such as:

* the caller of the function,
* the number of the call,
* the arguments passed to the function, and any default values used,
* the time the function took to execute,
* the function's return value, 
* the function's return to the caller. 

The decorator can write its messages to stdout using the `print` function, or to a `Logger` obtained from the Python `logging` module. These features and others are optional and configurable settings, which can be specified for each decorated function via keyword parameters of the decorator. You can also dynamically get and set these settings using attributes with the same names as the keywords, or using a dict-like interface whose keys are the keywords. In fact, through a mechanism of "indirect parameter values", with just a modest amount of cooperation between decorated functions, a caller can ensure uniform settings for all `log_calls`-decorated functions in call chains beneath it.

`log_calls` can collect statistics about the call history of a decorated function, including the history itself (arguments, time elapsed, return value, caller, and more), which can be retrieved as a tuple of records or as text in CSV format.

This document will explain all of these features and illustrate how to use them.

##Dependencies

None – this package requires no others.

##Installation
## *TODO TODO TODO*
*Blah Blah Blah*
You have two simple options:

1. If you're viewing the repository, copy the `log_calls` folder and its subfolders to a location on your `PYTHONPATH`, or 
2. run

    `pip install log_calls`
  
    ideally in a *virtualenv*.

Running 'pip' will also automatically run the tests in the `log_calls/tests/` folder.

###Testing proper installation and compatibility

 ## TODO Maybe make a simple run_tests.py to put in setup directory, or tests directory, or sumpin? and describe that

####Run the test proper
Run all tests in the `log_calls/tests/` directory:

 ## TODO How? if user just copied log_calls folder to somewhere on PYTHONPATH
 ## TODO Should happen automatically on pip install -- yes? (TODO: no, not at present)

Running those tests is even simpler – use this command in the `log_calls/tests/` directory:

    $ python test_log_calls [-v]

If you omit the "verbose" switch `-v`, no news is good news: if no errors were encountered, the command succeeds silently and will return you to a fresh prompt.
If you use the verbose switch, at the end of *a lot * of output you should see:

# *TODO* UPDATE THIS (SURELY IT ISN'T 98 NOW)
        
    1 items passed all tests:
      98 tests in log_calls.md
    98 tests in 1 items.
    98 passed and 0 failed.
    Test passed.
    
####Run this document
This is runnable documentation. When run in the `log_calls/doc/` directory, which contains this file `log_calls.md`, the command:

    $ python -m doctest log_calls.md

should return you to the prompt ($) with no other output, because no errors should have occurred in the roughly 100 tests. Verbose output from `doctest` can be had by adding the `-v` (verbose) option:

    $ python -m doctest -v log_calls.md

Admittedly, running this document is a bit of a stunt – we applaud because it can be run at all, not because it does that so well. A few of the tests had to be skipped using the `#doctest: +SKIP` directive, due to "newline" problems that don't arise with those same doctests in `test_doc_calls.py`. The module `test_doc_calls.py` has the same tests as this document, and none of them are skipped. Furthermore, the tests subdirectory `log_calls/tests/` contains tests of the other modules in the `log_calls` package, which this file doesn't attempt. So, you should definitely run all the tests in `log_calls/tests/`.

#### Credits
Argument logging is based on the Python 2 decorator:
        [https://wiki.python.org/moin/PythonDecoratorLibrary#Easy_Dump_of_Function_Arguments](https://wiki.python.org/moin/PythonDecoratorLibrary#Easy_Dump_of_Function_Arguments)

Changes and improvements to the arg logging of that decorator:

* updated for Python 3 (names of function attributes and the like),
* configurable separator for args,
* handling of *args,
* improved handling of keyword args, properly reflecting what the function receives:
    * the decorated function's explicit keyword args are listed one by one, and
    * if the function declares `**kwargs`, the implicit keyword args are collected in that dictionary.
* display of parameter default values used by calls to decorated functions

`log_calls` provides a lot of flexibility. This document contains many examples covering a wide range of uses, and includes several _tips und tricks_.

##Basic usage
Every example in this document uses `log_calls`, so without further ado:

    >>> from log_calls import log_calls

This section presents the basic parameters of `log_calls`. But first, let's see the most basic examples, which require no parameters at all:

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

###The *enabled* parameter (default – *True*)

The next most basic example:

    >>> @log_calls(enabled=False)
    ... def f(a, b, c):
    ...     pass
    >>> f(1, 2, 3)                # no output

###The *args_sep* parameter (default – `', '`)

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

###The *log_args* parameter (default – *True*)
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

###The *log_retval* parameter (default – *False*)
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

###The *log_exit* parameter (default – *True*)

When false, this parameter suppresses the `... ==> returning to ...` line
that indicates the function's return to its caller.

    >>> @log_calls(log_exit=False)
    ... def f(a, b, c):
    ...     return a + b + c
    >>> _ = f(1, 2, 3)
    f <== called by <module>
        arguments: a=1, b=2, c=3

###The *log_call_numbers* parameter (default – False)
log_calls keeps a running tally of the number of times a decorated function
is called. You can display this number using the `log_call_numbers` parameter:

    >>> @log_calls(log_call_numbers=True)
    ... def f(): pass
    >>> for i in range(2): f()
    f [1] <== called by <module>
    f [1] ==> returning to <module>
    f [2] <== called by <module>
    f [2] ==> returning to <module>

**NOTE**: *As we'll see later [TODO: ANCHOR], logging for a decorated function
can be turned on and off dynamically. In fact,* `log_calls` *also tracks the total
number of calls to a decorated function, and that number is accessible too –
see the section on [the* `stats.num_calls_total` *attribute](#stats.num_calls_total).
When the* `log_call_numbers` *setting is true, the call number displayed is
the logged call number - the rank of that call among the calls to the function
when logging has been enabled. For example, suppose you call* `f` *17 times with logging
enabled and with* `log_call_numbers` *enabled; then you turn logging off and call* `f`
*3 times; finally you re-enable logging and call* `f` *again: the number displayed will
be 18, not 21.*

###The *log_elapsed* parameter (default – *False*)
You can measure the performance of a function using the log_elapsed keyword. When true,
log_calls reports the time the decorated function took to complete, in seconds:

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

###The *prefix* parameter (default - `''`): decorating methods

Especially useful for clarity when decorating methods, the `prefix` keyword
parameter lets you specify a string with which to prefix the name of the
method. `log_calls` uses the prefixed name in its output: when logging
a call to, and a return from, the method; when reporting the method's return
value, and when the method is at the end of a call or return chain.

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

###The remaining parameters
The `logger` and `loglevel` parameters are discussed in the next section,
[Using loggers](#Logging), and in the later section [More on using loggers](#More-on-using-loggers).
The [`record_history`](#record_history-parameter) and [`max_history`](#max_history-parameter)
parameters are discussed in the own subsections of the later section
[Call history and statistics](#call-history-and-statistics).

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
        arguments: v1=5, v2=16
    DEBUG:a_logger:21
    DEBUG:a_logger:somefunc ==> returning to <module>

    >>> @log_calls(logger=logger)
    ... def anotherfunc():
    ...     somefunc(17, 19)
    >>> anotherfunc()       # doctest: +NORMALIZE_WHITESPACE
    DEBUG:a_logger:anotherfunc <== called by <module>
    DEBUG:a_logger:somefunc <== called by anotherfunc
        arguments: v1=17, v2=19
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

##Call chains

`log_calls` does its best to chase back along the call chain to find
the first `log_calls`-decorated function on the stack. If there is such
a function, it displays the entire list of functions on the stack
up to and including that function when logging calls and returns.
Without this, you'd have to guess at what was called in between calls
to functions decorated by `log_calls`.

    >>> @log_calls()
    ... def g1():
    ...     pass
    >>> def g2():
    ...     g1()
    >>> @log_calls()
    ... def g3():
    ...     g2()
    >>> def g4():
    ...     g3()
    >>> @log_calls()
    ... def g5():
    ...     g4()
    >>> g5()
    g5 <== called by <module>
    g3 <== called by g4 <== g5
    g1 <== called by g2 <== g3
    g1 ==> returning to g2 ==> g3
    g3 ==> returning to g4 ==> g5
    g5 ==> returning to <module>

###Call chains and inner functions

When chasing back along the stack, `log_calls` also detects inner functions that it has decorated:

    >>> @log_calls()
    ... def h0(z):
    ...     pass
    >>> def h1(x):
    ...     @log_calls()
    ...     def h1_inner(y):
    ...         h0(x*y)
    ...     return h1_inner
    >>> def h2():
    ...     h1(2)(3)
    >>> def h3():
    ...     h2()
    >>> def h4():
    ...     @log_calls()
    ...     def h4_inner():
    ...         h3()
    ...     return h4_inner
    >>> @log_calls()
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

... even when the inner function is called from within the outer function it's defined in:

    >>> @log_calls()
    ... def j0():
    ...     pass
    >>> def j1():
    ...     j0()
    >>> def j2():
    ...     @log_calls()
    ...     def j2_inner():
    ...         j1()
    ...     j2_inner()
    >>> @log_calls()
    ... def j3():
    ...     j2()
    >>> j3()
    j3 <== called by <module>
    j2_inner <== called by j2 <== j3
    j0 <== called by j1 <== j2_inner
    j0 ==> returning to j1 ==> j2_inner
    j2_inner ==> returning to j2 ==> j3
    j3 ==> returning to <module>

##[Dynamic control of settings using the *log_calls_settings* attribute](id:Dynamic-control-log_calls_settings)

The values given for the parameters of `log_calls`, e.g. `enabled=True`, 
`args_sep=" / "`, are set once the decorated function is interpreted. 
The values are established once and for all when the Python interpreter 
parses the definition of a decorated function and creates a function object.

###The problem
Even if a variable is used as a parameter value, its value at the time
Python processes the definition is "frozen" for the created function object.
Subsequently changing the value of the variable will *not* affect the behavior
of the decorator.

For example, suppose `DEBUG` is a module-level variable initialized to `False`, 
and you use this code:

        @log_calls(enabled=DEBUG)
        def foo(a, *args, **kwargs):  # ...
        
If later you set `Debug = True` and call `foo`, that call won't be logged, because
the decorated `foo`'s *enabled* setting is bound to the original value of `DEBUG`,
established when the definition was processed. To illustrate with a doctest:

    >>> DEBUG = False
    >>> @log_calls(enabled=DEBUG)
    ... def foo(**kwargs):
    ...     pass

    >>> foo()       # No log_calls output
    >>> DEBUG = True
    >>> foo()       # Still no log_calls output

###Solutions
`log_calls` provides *two* ways to dynamically control the settings of a decorated function.
This section presents one of them – using `log_calls_settings`. The next section,
on [indirect values](#Indirect-values), discusses another, rather different solution, 
one which is more intrusive but which affords even more control.

###The *log_calls_settings* attribute
The `log_calls` decorator adds an attribute `log_calls_settings`
to a decorated function, through which you can access the decorator settings
for that function. This attribute is an object which lets you control
the settings for a decorated function via a mapping (dict-like) interface,
and equivalently, via further attributes of the object. The mapping keys and
the attribute names are simply the `log_calls` keywords. `log_calls_settings`
also provides further methods for interacting with the settings in dict-like ways.
It's an instance of the `DecoSettingsMapping` class, defined in `deco_settings.py`.
That class has its own tests, in `log_calls/tests/test_deco_settings.py`,
so there's no need to test it exhaustively here; we'll just go over how to use it.

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

It has a length:

    >>> len(f.log_calls_settings)
    12

Its keys and items can be iterated through:

    >>> keys = []
    >>> for k in f.log_calls_settings: keys.append(k)
    >>> keys                                            # doctest: +NORMALIZE_WHITESPACE
    ['enabled', 'args_sep', 'log_args', 'log_retval',
     'log_exit', 'log_call_numbers', 'log_elapsed',
     'prefix',
     'logger', 'loglevel',
     'record_history', 'max_history']
    >>> items = []
    >>> for k, v in f.log_calls_settings.items(): items.append((k, v))
    >>> items                                           # doctest: +NORMALIZE_WHITESPACE
    [('enabled', False), ('args_sep', ', '), ('log_args', True), ('log_retval', True),
     ('log_exit', True), ('log_call_numbers', False), ('log_elapsed', True),
     ('prefix', ''),
     ('logger', None), ('loglevel', 10),
     ('record_history', False), ('max_history', 0)]

You can use `in` to test for key membership:

    >>> 'enabled' in f.log_calls_settings
    True
    >>> 'no_such_setting' in f.log_calls_settings
    False

Attempting to access a nonexistent setting raises `KeyError`:

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
        f return value: 91
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

But, of course, the new attribute does not become a decorator setting:

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

Retrieve settings (here, we retrieve an OrderedDict because it's more doctest-friendly,
but using `as_dict()` is sufficient):

    >>> od = f.log_calls_settings.as_OrderedDict()
    >>> od                      # doctest: +NORMALIZE_WHITESPACE
    OrderedDict([('enabled', True),           ('args_sep', ', '),
                 ('log_args', True),          ('log_retval', False),
                 ('log_exit', True),          ('log_call_numbers', False),
                 ('log_elapsed', False),      ('prefix', ''),
                 ('logger', None),            ('loglevel', 10),
                 ('record_history', False),   ('max_history', 0)])

change settings temporarily:

    >>> f.log_calls_settings.update(
    ...     log_args=False, log_elapsed=True, log_call_numbers=True,
    ...     log_retval=True)

use the new settings for f:

    >>> _ = f()                     # doctest: +ELLIPSIS
    f [4] <== called by <module>
        f return value: 91
        elapsed time: ... [secs]
    f [4] ==> returning to <module>

and restore original settings, this time passing the retrieved settings
dictionary rather than keywords:

    >>> f.log_calls_settings.update(od)
    >>> od == f.log_calls_settings.as_OrderedDict()
    True

**NOTES**:

1. *The `max_history` setting is immutable (no other setting is), and attempts to change it
directly (e.g.* `f.log_calls_settings.max_history = anything`) *raise* `ValueError`.
*Nevertheless, it* is *an item in the retrieved settings dictionaries. To allow for
the use-case just illustrated, `update()` is considerate enough to skip over
immutable settings.*

2. `log_calls` *continues to track call numbers even when it isn't reporting
them. The last call to f was the 4th, as shown, although the call number of
the 3rd call wasn't displayed.*


##[Dynamic control of settings with indirect values](id:Indirect-values)

Every parameter of `log_calls` except `prefix` and 'max_history' can take 
two kinds of values: *direct* and *indirect*, which you can think of as 
*static* and *dynamic* respectively. Direct/static values are actual values 
used when the decorated function is interpreted, e.g. `enabled=True`, 
`args_sep=" / "`. As discussed in the previous section on 
[`log_call_settings`](#Dynamic-control-log_calls_settings), the values of 
parameters are set once and for all when the Python interpreter creates 
a function object from the source code of a decorated function. Even if you 
use a variable as the value of a setting, subsequently changing the variable's 
value has no effect on the decorator's setting.

To overcome this limitation, `log_calls` lets you specify any parameter 
except `prefix` or `max_history` with one level of indirection, by using 
*indirect values*: an indirect value is a string that names a keyword argument 
*of the decorated function*. It can be an explicit keyword argument present 
in the signature of the function, or an implicit keyword argument that ends up 
in `**kwargs` (if that's present in the function's signature). When the decorated 
function is called, the arguments passed by keyword, and the decorated function's 
explicit keyword parameters with default values, are both searched for the named 
parameter; if it is found and of the correct type, *its* value is used; otherwise 
a default value is used.

To specify an indirect value for a parameter whose normal type is `str`, 
append an `'='` to the value. (Presently, `args_sep` is the only parameter 
this applies to.) For consistency's sake, any parameter value that names 
a keyword parameter of the decorated function can also end in a trailing '=', 
which is stripped. Thus, `enabled='enable_='` indicates an indirect value 
supplied by the keyword (argument or parameter) `enable_` of the decorated function.

Thus, in:

    >>> @log_calls(args_sep='sep=', prefix="*** ")
    ... def f(a, b, c, sep='|'): pass

`args_sep` has an indirect value which names `f`'s explicit keyword parameter `sep`,
and `prefix` has a direct value. A call can dynamically override the default
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

**NOTE**: *This last example illustrates a subtle point: 
if you omit the* `enabled` *parameter altogether, logging will occur, 
as the default value is (the direct value)* `True`; *however, if you 
specify an indirect value for* `enabled` *and the named indirect 
keyword is not supplied in a call, then that call* won't *be logged. 
In other words, if you specify an indirect value for the* `enabled` *parameter 
then the default effective value of the enabled setting is* `False`* -- 
calls are not logged unless the named parameter is found and its value is true.*

###Controlling format 'from above'

This indirection mechanism allows a calling function to control the appearance
of logged calls to functions lower in the call chain, provided they all use
the same indirect parameter keywords.

In the next example, the separator value supplied to `g` by keyword argument
propagates to `f`. Note that the arguments 42 and 99 end up in the "varargs" tuple 
of `g`. We've give the variable-size, collect-all-the-rest arguments unusual names 
to illustrate that whatever you call these parameters, their roles are unambiguous 
and their names are available to `log_calls`, which will use them:

    >>> @log_calls(args_sep='sep=')
    ... def f(a, b, c, **kwargs): pass
    >>> @log_calls(args_sep='sep=')
    ... def g(a, b, c, *g_args, **g_kwargs):
    ...     f(a, b, c, **g_kwargs)
    >>> g(1,2,3, 42, 99, sep='\\n')       # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS, +SKIP
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


###Enabling with *int*s rather than *bool*s

Sometimes it's desirable for a function to print or log debugging messages 
as it executes. It's the oldest form of debugging! Instead of a simple bool,
you can use a nonnegative int as the enabling value and treat it as a level 
of verbosity.

    >>> DEBUG_MSG_BASIC = 1
    >>> DEBUG_MSG_VERBOSE = 2
    >>> DEBUG_MSG_MOREVERBOSE = 3  # etc.
    >>> @log_calls(enabled='debuglevel')
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

### Using `log_calls_settings` to set indirect values
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

##[More on using loggers](id:More-on-using-loggers)

The basic setup:

    >>> import logging
    >>> import sys
    >>> ch = logging.StreamHandler(stream=sys.stdout)
    >>> logging.basicConfig(handlers=[ch])
    >>> logger = logging.getLogger('mylogger')
    >>> logger.setLevel(logging.DEBUG)


####Indirect values for the *logger* parameter

You can use an indirect value for the `logger` parameter to make the logging
destination late-bound.

In the following example, although logger='logger_' is supplied to `log_calls`,
no `logger_=foo` is passed to the wrapped function `r` in the actual call, and no
`logger=bar` is supplied, so `log_calls` uses the default writing function, `print`.
(Furthermore, no args separator is passed with the `sep_` keyword, so `log_calls`
uses the default separator ', '.)

    >>> @log_calls(enabled='enable=', args_sep='sep_=', logger='logger_=')
    ... def r(x, y, z, **kwargs):
    ...     print(x * y + z)
    >>> r(1, 2, 3, enable=True)
    r <== called by <module>
        arguments: x=1, y=2, z=3, [**]kwargs={'enable': True}
    5
    r ==> returning to <module>

Define two more functions, with the outermost function `t` also using
`logger ='logger_'`, and pass `logger_=logger` to `t` when calling it.
Now both `t` and `r` use `logger` for output (and both use the supplied
separator '\\n'):

    >>> def s(x, y, z, **kwargs):
    ...     r(x, y, z, **kwargs)
    >>> @log_calls(enabled='enable=', args_sep='sep_=', logger='logger_=')
    ... def t(x, y, z, **kwargs):
    ...     s(x, y, z, **kwargs)

    >>> # kwargs == {'logger_': <logging.Logger object at 0x...>,
    >>> #            'enable': True, 'sep_': '\\n'}
    >>> t(1,2,3, enable=True, sep_='\\n', logger_=logger)       # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS, +SKIP
    DEBUG:mylogger:t <== called by <module>
        arguments:
            x=1
            y=2
            z=3
            [**]kwargs={...}
    DEBUG:mylogger:r <== called by s <== t
        arguments:
            x=1
            y=2
            z=3
            [**]kwargs={...}
    5
    DEBUG:mylogger:r ==> returning to s ==> t
    DEBUG:mylogger:t ==> returning to <module>

####Test of indirect *loglevel*

    >>> logger.setLevel(logging.INFO)   # raise logger's level to INFO
    >>> @log_calls(logger='logger_=', loglevel='loglevel_')
    ... def indirect_loglevel(a, x, y, **kwargs):
    ...     print(a * x**y)

No log_calls output from indirect_loglevel:
    >>> indirect_loglevel(5, 3, 3,
    ...                   enable=True, sep_='\\n',
    ...                   logger_=logger,
    ...                   loglevel_=logging.DEBUG)   # no log_calls output
    135

but now we do get output:
    >>> indirect_loglevel(5, 3, 3,
    ...                   enable=True, sep_='\\n',
    ...                   logger_=logger,
    ...                   loglevel_=logging.INFO)    # doctest: +ELLIPSIS
    INFO:mylogger:indirect_loglevel <== called by <module>
        arguments: a=5, x=3, y=3, [**]kwargs={...}
    135
    INFO:mylogger:indirect_loglevel ==> returning to <module>

### A realistic example – multiple handlers with different loglevels
Let's add another handler, also sent to `stdout` but best thought of as writing
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

Furthermore, suppose we have two functions: one that's lower-level/
often-called, and another that's "higher-level"/infrequently called.

    >>> @log_calls(logger=logger, loglevel=logging.DEBUG)
    ... def popular():
    ...     pass
    >>> @log_calls(logger=logger, loglevel=logging.INFO)
    ... def infrequent():
    ...     popular()

Set logger level to `DEBUG`:
  the console handler logs calls only for `infrequent`,
  but the "file" handler logs calls for both functions.

    >>> logger.setLevel(logging.DEBUG)
    >>> infrequent()       # doctest: +NORMALIZE_WHITESPACE
    [FILE]     INFO:mylogger: infrequent <== called by <module>
    INFO:mylogger:infrequent <== called by <module>
    [FILE]    DEBUG:mylogger: popular <== called by infrequent
    [FILE]    DEBUG:mylogger: popular ==> returning to infrequent
    [FILE]     INFO:mylogger: infrequent ==> returning to <module>
    INFO:mylogger:infrequent ==> returning to <module>

Now set logger level to `INFO`:
  both handlers logs calls only for `infrequent`:

    >>> logger.setLevel(logging.INFO)
    >>> infrequent()       # doctest: +NORMALIZE_WHITESPACE
    [FILE]     INFO:mylogger: infrequent <== called by <module>
    INFO:mylogger:infrequent <== called by <module>
    [FILE]     INFO:mylogger: infrequent ==> returning to <module>
    INFO:mylogger:infrequent ==> returning to <module>

##[A metaclass example](id:A-metaclass-example)

The following class `A_meta` will serve as the metaclass for classes defined subsequently:

    >>> # - - - - - - - - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - -
    >>> # A_meta, a metaclass
    >>> # - - - - - - - - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - -
    >>> from collections import OrderedDict
    >>> separator = '\n'    # default ', ' gives rather long lines

    >>> A_DBG_BASIC = 1
    >>> A_DBG_INTERNAL = 2

    >>> class A_meta(type):
    ...     @classmethod
    ...     @log_calls(prefix='A_meta.', args_sep=separator, enabled='A_debug')
    ...     def __prepare__(mcs, cls_name, bases, *, A_debug=0, **kwargs):
    ...         if A_debug >= A_DBG_INTERNAL:
    ...             print("    mro =", mcs.__mro__)
    ...         super_dict = super().__prepare__(cls_name, bases, **kwargs)
    ...         if A_debug >= A_DBG_INTERNAL:
    ...             print("    dict from super() = %r" % super_dict)
    ...         super_dict = OrderedDict(super_dict)
    ...         super_dict['key-from-__prepare__'] = 1729
    ...         if A_debug >= A_DBG_INTERNAL:
    ...             print("    Returning dict: %s" % super_dict)
    ...         return super_dict
    ...
    ...     @log_calls(prefix='A_meta.', args_sep=separator, enabled='A_debug')
    ...     def __new__(mcs, cls_name, bases, cls_members: dict, *, A_debug=0, **kwargs):
    ...         cls_members['key-from-__new__'] = "No, Hardy!"
    ...         if A_debug >= A_DBG_INTERNAL:
    ...             print("    calling super() with cls_members = %s" % cls_members)
    ...         return super().__new__(mcs, cls_name, bases, cls_members, **kwargs)
    ...
    ...     @log_calls(prefix='A_meta.', args_sep=separator, enabled='A_debug')
    ...     def __init__(cls, cls_name, bases, cls_members: dict, *, A_debug=0, **kwargs):
    ...         if A_debug >= A_DBG_INTERNAL:
    ...             print("    cls.__mro__:", str(cls.__mro__))
    ...             print("    type(cls).__mro__[1] =", type(cls).__mro__[1])
    ...         try:
    ...             super().__init__(cls_name, bases, cls_members, **kwargs)
    ...         except TypeError as e:
    ...             # call type.__init__
    ...             if A_debug >= A_DBG_INTERNAL:
    ...                 print("    calling type.__init__ with no kwargs")
    ...             type.__init__(cls, cls_name, bases, cls_members)

The class `A_meta` is a metaclass: it derives from `type`,
and defines (overrides) methods `__prepare__`, `__new__` and `__init__`.
All of its methods take an explicit keyword parameter `A_debug`,
used as the indirect value of the `log_calls` keyword parameter `enabled`.
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
        Returning dict: OrderedDict([('key-from-__prepare__', 1729)])
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

    >>> class AA(metaclass=A_meta, A_debug=False):    # doctest: +NORMALIZE_WHITESPACE
    ...     pass

##[Call history and statistics](id:call-history-and-statistics)
`log_calls` always collects a few basic statistics about calls to a decorated
function. It can collect the entire history of calls to a function if asked
to (using [the `record_history` parameter](#record_history-parameter)).
The statistics and history are accessible via the `stats` attribute
which `log_calls` adds to a decorated function.

###The *stats* attribute
The `stats` attribute is an object of class `ClassInstanceAttrProxy`, defined
in `log_calls/proxy_descriptors.py`. That class has its own test suite,
in `log_calls/tests/test_proxy_descriptors.py`; here, we only have to
test and illustrate its use by `log_calls`.

Let's define a decorated function with call-number-logging turned on,
but with exit-logging turned off for brevity:

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

####The *stats.num_calls_logged* attribute
The `stats.num_calls_logged` attribute contains the number of the most
recent logged call to a decorated function. Thus, `f.stats.num_calls_logged`
will equal 2:

    >>> f.stats.num_calls_logged
    2

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
all logged calls to a decorated function. It's not possible to doctest this so
we'll just exhibit its value for the 3 logged calls to `f` above:

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

####The *stats.call_history* attribute
The `stats.call_history` attribute of a decorated function provides the call history
of logged calls to the function as a tuple of records. Here's `f`'s call history,
in human-readable form (ok, almost human-readable!). The CSV presentation pairs
the `argnames` with their values `argvals`, making it even more human-readable,
especially when viewed in a program that presents CSVs nicely:

    >>> print('\\n'.join(map(str, f.stats.call_history)))   # doctest: +SKIP
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

#####The CallRecord namedtuple
For the record, records that comprise a decorated function's call_history are 
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
[`clear_history`](#clear_history-method) method). If the value of `max_history`
is > 0, log_calls will retain that many records, at most, discarding the oldest
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

    >>> print('\\n'.join(map(str, g.stats.call_history)))    # doctest: +SKIP
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

####The *stats.call_history_as_csv* attribute
The value `stats.call_history_as_csv` attribute is a text representation
of a decorated function's call history in CSV format. You can save this string
and import it into the program or tool of your choice for further analysis.
CSV format is only partially human-friendly, but this representation
breaks out each argument into its own column, throwing away information about
whether an argument's value was passed or is a default.

    >>> print(g.stats.call_history_as_csv)        # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    'call_num'|'a'|'retval'|'elapsed_secs'|'timestamp'|'prefixed_fname'|'caller_chain'
    2|1|None|...|...|'g'|['<module>']
    3|2|None|...|...|'g'|['<module>']
    <BLANKLINE>

Ellipses above are for the `elapsed_secs` and `timestamp` fields.

The CSV separator is '|' rather than ',' because some of the fields – `args`,  `kwargs`
and `caller_chain` – use commas intrinsically. Let's examine one more `call_history_as_csv`
for a function that has all of those:

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
    >>> print(f.stats.call_history_as_csv)        # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    'call_num'|'a'|'extra_args'|'x'|'kw_args'|'retval'|'elapsed_secs'|'timestamp'|'prefixed_fname'|'caller_chain'
    1|0|()|1|{}|None|...|...|'f'|['g', 'h']
    2|10|(17, 19)|1|{'z': 100}|None|...|...|'f'|['g', 'h']
    3|20|(3, 4, 6)|5|{'y': 'Yarborough', 'z': 100}|None|...|...|'f'|['g', 'h']
    <BLANKLINE>

As usual, `log_calls` will use whatever names you use for varargs parameters
(here, `extra_args` and `kw_args`). Whatever the name of the `kwargs` parameter,
items within that field are guaranteed to be in sorted order (otherwise this
last example would sometimes fail as a doctest).

####[The *stats.clear_history(max_history=0)* method](id:clear_history-method)
The `stats.clear_history(max_history=0)` method, as you might expect, clears
the call history of a decorated function. Not only does it clear the history
list, it also resets all counters: `num_calls_total` and `num_calls_logged`
are reset to 0, and `elapsed_secs_logged` is reset to 0.0.

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

Let's clear `f`'s history and check that all stats counters are as promised:

    >>> f.stats.clear_history(max_history=33)
    >>> f.log_calls_settings.max_history
    33
    >>> f.stats.num_calls_logged
    0
    >>> f.stats.num_calls_total
    0
    >>> f.stats.elapsed_secs_logged
    0.0

##Appendix – Keyword Parameters Reference

The `log_calls` decorator takes various keyword arguments, all with hopefully sensible defaults:

Keyword parameter | Default value | Description
----------------: | :------------ | :------------------
       `enabled`    | `True`          | An `int`. If true, then logging will occur.
       `args_sep`   | `', '`          | `str` used to separate arguments. The default is  `', '`, which lists all args on the same line. If `args_sep='\n'` is used, or if more generally the `args_sep` string ends in `\n`, then additional spaces are appended to the separator for a neater display. Other separators in which `'\n'` occurs are left unchanged, and are untested – experiment/use at your own risk.
       `log_args`   | `True`          | arguments passed to the decorated function, and default values used by the function, will be logged.
       `log_retval` | `False`         | If true (truthy), log what the decorated function returns. At most 60 chars are printed, with a trailing ellipsis if the value is truncated.
       `log_exit`   | `True`          | If true, the decorator will log an exiting message after calling the function of the form `f returning to ==> caller`, and before returning what the function returned.
       `log_call_number` | `False`    | If true, display the (1-based) number of the function call, e.g. `f [3] called by <== <module>` and `f [3] returning to ==> <module>` for the 3rd logged call. This would correspond to the 3rd record in the function's call history, if `record_history` is true.
       `log_elapsed` | `False`        | If true, display how long it took the function to execute, in seconds.
       `prefix`     | `''`            | A `str` to prefix the function name with in logged messages: on entry, in reporting return value (if `log_retval` is true) and on exit (if `log_exit` is true).
       `logger`     | `None`          | If not `None`, a `Logger` which will be used to write all messages. Otherwise, `print` is used.
       `loglevel`   | `logging.DEBUG` | Logging level, ignored unless a logger is specified. This should be one of the logging levels recognized by the `logging` module – one of the constants defined by that module, or a custom level you've added.
       `record_history` | `False`     | If true, an array of records will be kept, one for each call to the function. Each record holds: call number (1-based), arguments and defaulted keyword arguments, return value, time elapsed, time of call, caller (call chain), prefixed function name.
       `max_history` | `0`            | An `int`. *value* > 0 --> store at most *value*-many records, oldest records overwritten; *value* ≤ 0 --> store unboundedly many records. Ignored unless `record_history` is true.


####— Brian O'Neill, October 2014, NYC
