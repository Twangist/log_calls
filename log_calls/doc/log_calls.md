#log_calls – a decorator for debugging
---
`log_calls` is a Python 3 decorator that can log the caller of a decorated function, the arguments passed to that function, the function's returned value, and its return to the caller. The decorator can write its messages to stdout using the `print` function, or to a `Logger` from the Python `logging` module. These features and others are optional and configurable settings, which can be specified for each decorated function via keyword parameters of the decorator. You can dynamically get and set a decorated function's settings, using attributes with the same names as the keywords, or a dict-like interface whose keys are the keywords.
In fact, through a mechanism of "indirect parameter values", with just a modest amount of cooperation between decorated functions, a caller can ensure uniform settings for all `log_calls`-decorated functions in call chains beneath it.

##Dependencies

None – this package depends on no others.

##Installation
### TODO TODO TODO
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
Admittedly, running this document is a bit of a stunt – we applaud because it can be run at all, not because it does that so well. A few of the tests had to be skipped using the `#doctest: +SKIP` directive, due to "newline" problems that don't arise when those doctests reside in a .py module. The very same tests appear in `test_doc_calls.py`, and running that test suite is preferred: none of the tests are skipped there. Running those tests is even simpler – use this command in the `log_calls/tests/` directory:

    $ python test_log_calls [-v]

If you omit the "verbose" switch `-v`, no news is good news: if no errors were encountered, the command succeeds silently and will return you to a fresh prompt.
If you use the verbose switch, at the end of *a lot * of output you should see:

# TODO UPDATE THIS (SURELY IT ISN'T 98 NOW)
        
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


Admittedly, running this document is a bit of a stunt – we applaud because it can be run at all, not because it does that so well. A few of the tests had to be skipped using the `#doctest: +SKIP` directive, due to "newline" problems that don't arise with those same doctests in `test_doc_calls.py`. The module `test_doc_calls.py` has the same tests as this document, an none of them are skipped, so running that test suite is preferred.

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

`log_calls` provides a lot of flexibility. This document contains many examples covering a wide range of uses, and includes several _tips und tricks_.

##Basic usage
Every example in this document uses `log_calls`, so without further ado:

    >>> from log_calls import log_calls

###The `enabled` parameter
The most basic example:

    >>> @log_calls()                 # enabled=True is the default
    ... def fn0(a, b, c):
    ...     pass
    >>> fn0(1, 2, 3)
    fn0 <== called by <module>
        args: a=1, b=2, c=3
    fn0 ==> returning to <module>

The next most basic:

    >>> @log_calls(enabled=False)    # no output
    ... def fn1(a, b, c):
    ...     pass
    >>> fn1(1, 2, 3)

###The `args_sep` parameter
**NOTE**: *In all the doctest examples in this document, you'll see* `'\\n'` *where in actual code you'd write* `'\n'`. *This is a `doctest` quirk: all the examples herein work (as tests, they pass), and they would fail if* `'\n'` *were used. The only alternative would be to use raw character strings and write* `r'\n'`*, which is not obviously better.*

    >>> @log_calls(args_sep='\\n')
    ... def fn2(a, b, c, **kwargs):
    ...     print(a + b + c)
    >>> fn2(1, 2, 3, u='you')        # doctest: +SKIP, +NORMALIZE_WHITESPACE
    fn2 <== called by <module>
        args:
            a=1
            b=2
            c=3
            [**]kwargs={'u': 'you'}
    6
    fn2 ==> returning to <module>

###The `log_exit` parameter
    >>> @log_calls(log_exit=False)
    ... def fn3(a, b, c):
    ...     return a + b + c
    >>> _ = fn3(1, 2, 3)
    fn3 <== called by <module>
        args: a=1, b=2, c=3

###The `log_retval` parameter
    >>> @log_calls(log_retval=True)
    ... def fn4(a, b, c):
    ...     return a + b + c
    >>> _ = fn4(1, 2, 3)
    fn4 <== called by <module>
        args: a=1, b=2, c=3
        fn4 return value: 6
    fn4 ==> returning to <module>

Return values longer than 60 characters are truncated and end with a trailing ellipsis:

    >>> @log_calls(log_retval=True)
    ... def return_long_str():
    ...     return '*' * 100
    >>> return_long_str()       # doctest: +NORMALIZE_WHITESPACE
    return_long_str <== called by <module>
    return_long_str return value: ************************************************************...
    return_long_str ==> returning to <module>
    '****************************************************************************************************'


##Call chains

`log_calls` does its best to chase back along the call chain to find the first `log_calls`-decorated function in the stack. If there is such a function, it displays the entire list of functions on the stack up to and including that function when logging calls and returns. Without this, you'd have to guess at what was called in between calls to functions decorated by `log_calls`.

    >>> @log_calls()
    ... def g1():
    ...     pass
    >>> def g2():
    ...     g1()
    >>> @log_calls()
    ... def g3(optional=''):    # g3 will have an 'args:' section
    ...     g2()
    >>> def g4():
    ...     g3()
    >>> @log_calls()
    ... def g5():
    ...     g4()
    >>> g5()
    g5 <== called by <module>
    g3 <== called by g4 <== g5
        args: <none>
    g1 <== called by g2 <== g3
    g1 ==> returning to g2 ==> g3
    g3 ==> returning to g4 ==> g5
    g5 ==> returning to <module>


###Functions with no parameters, calls with no arguments
In the previous example, four of the five functions have no parameters, so `log_calls` shows no `args:` section for them. `g3` takes one optional argument but is called with none, so log_calls displays `args: <none>`.


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
        args: y=3
    h0 <== called by h1_inner
        args: z=6
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


##Decorating methods: using the `prefix` keyword parameter

Especially useful for clarity when decorating methods, the `prefix` keyword parameter lets you specify a string with which to prefix the name of the method. `log_calls` uses the prefixed name in its output: when logging a call to, and a return from, the method; when reporting the method's return value, and when the method is at the end of a call or return chain.

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
        args: self=Point(1, 2)
    Point.diag_reflect ==> returning to <module>
    Point(1, 2).diag_reflect() = Point(2, 1)

    >>> print("length of Point(1, 2) =", round(Point(1, 2).length(), 2))    # doctest: +ELLIPSIS
    Point.length <== called by <module>
        args: self=Point(1, 2)
    Point.distance <== called by Point.length
        args: pt1=Point(1, 2), pt2=Point(0, 0)
    Point.distance ==> returning to Point.length
        Point.length return value: 2.236...
    Point.length ==> returning to <module>
    length of Point(1, 2) = 2.24


##Direct (static) and indirect (dynamic) parameter values
-------------------------------------------------------
###Dynamical control of logging

Every parameter of `log_calls` except `prefix` can take two kinds of values: *direct* and *indirect*, which you can think of as *static* and *dynamic* respectively. Direct/static values are actual values used when the decorated function is interpreted, e.g. `enabled=True`, `args_sep=" / "`. Such values are established once and for all when the Python interpreter parses the definition of a decorated function and creates a function object. If a variable is used as a parameter value, its value at the time Python processes the definition is "frozen" for the created function object. Subsequently changing the value of the variable will *not* affect the behavior of the decorator.

For example, suppose `DEBUG` is a module-level variable initialized to `False`, and you use this code:
        @log_calls(enabled=DEBUG)
        def foo(a, *args, **kwargs): # ...
        
If later you set `Debug = True` and call `foo`, that call won't be logged, because the decorated `foo`'s enabled setting is bound to the original value of `DEBUG`, established when the definition was processed. To illustrate with a doctest:

    >>> DEBUG = False
    >>> @log_calls(enabled=DEBUG)
    ... def foo(**kwargs):
    ...     pass

    >>> foo()       # No log_calls output
    >>> DEBUG = True
    >>> foo()       # Still no log_calls output

To overcome this limitation, `log_calls` lets you specify any parameter except `prefix` with one level of indirection, by using *indirect values*: an indirect value is a string that names a keyword argument *of the decorated function*. It can be an explicit keyword argument present in the signature of the function, or an implicit keyword argument that ends up in `**kwargs` (if that is present in the function's signature). When the decorated function is called, the arguments passed by keyword and the explicit keyword parameters of the decorated function are searched for the named parameter; if it is found and of the correct type, `its` value is used; otherwise a default value is used.

To specify an indirect value for a parameter whose normal type is str, append an `'='` to the value. (Presently, `args_sep` is the only parameter this applies to.) As a concession to consistency, any parameter value that names a keyword parameter of the decorated function can also end in a trailing '=', which is stripped. Thus, `enabled='enable_='` indicates an indirect value supplied by the keyword (argument or parameter) `enable_` of the decorated function.

Thus, in:

    >>> @log_calls(args_sep='sep=', prefix="*** ")
    ... def f(a, b, c, sep='|'): pass

`args_sep` has an indirect value which names `f`'s explicit keyword parameter `sep`, and `prefix` has a direct value. A call can dynamically override the default value `'|'` in the signature of f by supplying a value:

    >>> f(1, 2, 3, sep=' / ')
    *** f <== called by <module>
        args: a=1 / b=2 / c=3 / sep=' / '
    *** f ==> returning to <module>

or it can use `f`'s default value by not supplying a `sep` argument:

    >>> f(1, 2, 3)
    *** f <== called by <module>
        args: a=1|b=2|c=3
    *** f ==> returning to <module>

A decorated function doesn't have to explicitly declare the named parameter, if its signature includes `**kwargs` -- it can be an implicit keyword parameter. Consider:

    >>> @log_calls(enabled='enable')
    ... def func1(a, b, c, **kwargs): pass
    >>> @log_calls(enabled='enable')
    ... def func2(z, **kwargs): func1(z, z+1, z+2, **kwargs)

When the following statement is executed, the calls to both `func1` and `func2` will be logged:

    >>> func2(17, enable=True)
    func2 <== called by <module>
        args: z=17, [**]kwargs={'enable': True}
    func1 <== called by func2
        args: a=17, b=18, c=19, [**]kwargs={'enable': True}
    func1 ==> returning to func2
    func2 ==> returning to <module>

whereas neither of the following two statements will trigger logging:

    >>> func2(42, enable=False)     # no log_calls output
    >>> func2(99)                   # no log_calls output

**NOTE**: This last example illustrates a perhaps subtle point: if you omit the `enabled` parameter altogether, logging will occur, as the default value is (the direct value) True; however, if you specify an indirect value for `enabled` and the named indirect keyword is not supplied in a call, then that call *won't* be logged. In other words, the default value of enabled is `True`, a direct value; but if you specify an indirect value then the default effective value of the enabled setting is False -- calls are not logged unless the named parameter is found and its value is truthy.

Additional Tests for log_args, log_retval, log_exit with indirect values
------------------------------------------------------------------------

    >>> @log_calls(log_args='logargs=', log_retval='logretval=', log_exit='logexit=')
    ... def f(x, **kwargs):
    ...     return x**2
    >>> _ = f(2, logexit=False)   # logargs=True, log_retval=False: defaults
    f <== called by <module>
        args: x=2, [**]kwargs={'logexit': False}

    >>> _ = f(5, logargs=False, logretval=True) # log_exit=True, default
    f <== called by <module>
        f return value: 25
    f ==> returning to <module>


# RESUME RESUME


This mechanism allows a calling function to control the appearance of logged
calls lower in the call chain, provided they all use the same `args_sep_kwd`.

    >>> @log_calls(args_sep_kwd='sep_')
    ... def f(a, b, c, *, u='', v=9, **kwargs):
    ...     print(a+b+c)
    >>> f(1,2,3, u='you')                 # doctest: +NORMALIZE_WHITESPACE
    f <== called by <module>
        args: a=1, b=2, c=3, u='you'
    6
    f ==> returning to <module>

    >>> f(1,2,3, u="you", sep_='\\n')     # doctest: +SKIP, +NORMALIZE_WHITESPACE
    f <== called by <module>
        args:
            a=1
            b=2
            c=3
            u='you'
            [**]kwargs={'sep_': '\\n'}
    6
    f ==> returning to <module>

In the next example, the separator value supplied by keyword argument to `g` 
propagates to `f` when `g` calls it. Note that the arguments `42` and `99` end up
in the `*args` tuple of `g`:

    >>> @log_calls(args_sep_kwd='sep_')
    ... def g(a, b, c, *args, **kwargs):
    ...     f(a, b, c, **kwargs)
    >>> g(1,2,3, 42, 99, sep_='\\n')       # doctest: +SKIP, +NORMALIZE_WHITESPACE
    g <== called by <module>
        args:
            a=1
            b=2
            c=3
            [*]args=(42, 99)
            [**]kwargs={'sep_': '\\n'}
    f <== called by g
        args:
            a=1
            b=2
            c=3
            [**]kwargs={'sep_': '\\n'}
    6
    f ==> returning to g
    g ==> returning to <module>

###[The `enabled_kwd` parameter](id:section__enabled_kwd)
Similarly, although there is no way to change a value supplied with the `enabled`
keyword once a decorated function is defined, you *can* dynamically enable/disable
call-logging for a function by using the `enabled_kwd` keyword parameter. As with
`args_sep_kwd`, the value of this parameter must be a string, which should give
the name of a keyword parameter that will be passed to the wrapped function;
the truthiness of *that* parameter will then determine whether logging is enabled.

`enabled_kwd` takes precedence over `enabled`. 

In the following example,
    `[**]kwargs={'sep_': ', ', 'u': 'somebody'}`
or
    `[**]kwargs={'u': 'somebody', 'sep_': ', '}`
Only the order of items is different, but doctest is very literal, and provides
no way other than ellipsis to tell it that the order doesn't matter.

    >>> @log_calls(args_sep_kwd='sep_', enabled_kwd='enable')
    ... def h(a, b, *args, enable=True, **kwargs):
    ...     if enable:
    ...         g(a, b, 10, *args, **kwargs)
    >>> for i in range(2):
    ...     h(i, i+1, 'a', 'b', u='somebody', enable=i%2, sep_=', ')       # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    h <== called by <module>
        args: a=1, b=2, [*]args=('a', 'b'), enable=1, [**]kwargs={...}
    g <== called by h
        args: a=1, b=2, c=10, [*]args=('a', 'b'), [**]kwargs={...}
    f <== called by g
        args: a=1, b=2, c=10, u='somebody', [**]kwargs={'sep_': ', '}
    13
    f ==> returning to g
    g ==> returning to h
    h ==> returning to <module>

Here's another example of dynamic enabling/disabling of log_calls output.

If `DEBUG` is a module-level variable and you just use:

        @log_calls(enabled=DEBUG)
        def foo(a, *args, debug=DEBUG, **kwargs): pass

then changing the value of `DEBUG` doesn't change whether calls to `foo`
are logged or not -- that is determined by the value of `DEBUG` when
the definition was processed:

    >>> DEBUG = False
    >>> @log_calls(enabled=DEBUG)
    ... def foo(**kwargs):
    ...     pass

    >>> foo()       # No log_calls output
    >>> DEBUG = True
    >>> foo()       # Still no log_calls output

If you use `enabled_kwd`, however, the added level of indirection
lets you control log_calls output for each call. Suppose for example that 
you use `enabled_kwd='debug'` to decorate a function `f`. Then a call 
to `f`  will be logged if one of the following conditions holds:

1. the call passes the keyword mentioned with a 'truthy' value,   
e.g.`debug=True`, or
2. the keyword is *not* passed, but the function `f`explicitly declares  
 the keyword parameter (`debug`) and assigns it a 'truthy' default value   
(e.g. `def f(x, debug=True)`).

Providing both `enabled` and `enabled_kwd` is pointless: if provided,
`enabled_kwd` takes precedence and `enabled` is ignored; a call will
be logged only under one of the two conditions above. Observe:

    >>> @log_calls(enabled=True, enabled_kwd='debug')
    ... def do_stuff(a, **kwargs):
    ...     pass
    >>> do_stuff(3)                # no output: no debug=
    >>> do_stuff(4, debug=537)     # output: debug=<truthy>
    do_stuff <== called by <module>
        args: a=4, [**]kwargs={'debug': 537}
    do_stuff ==> returning to <module>

###Examples of condition 1.

    >>> @log_calls(enabled_kwd='debug')
    ... def bar(**kwargs):
    ...     pass
    >>> bar(debug=False)  # no output
    >>> bar(debug=True)  # output
    bar <== called by <module>
        args: [**]kwargs={'debug': True}
    bar ==> returning to <module>
    >>> bar()         # no output: enabled_kwd overrides enabled=True default

###Examples of condition 2. (explicit parameter)

It's instructive to consider examples where the wrapped function explicitly provides
the keyword named by the `enabled_kwd` parameter.

    >>> @log_calls(enabled_kwd='debug')
    ... def do_more_stuff_f(a, debug=False, **kwargs):
    ...     pass

Here we get no output, as `debug=False` (wrapped function's default value):

    >>> do_more_stuff_f(3)

but here we do get output:

    >>> do_more_stuff_f(4, debug=True)
    do_more_stuff_f <== called by <module>
        args: a=4, debug=True
    do_more_stuff_f ==> returning to <module>

Now, let the wrapped function provide a default value of `True`
for the parameter named by the `enabled_kwd` parameter:

    >>> @log_calls(enabled_kwd='debug')
    ... def do_more_stuff_t(a, debug=True, **kwargs):
    ...     pass

Here we get output, without having to pass `debug=True`:

    >>> do_more_stuff_t(9)
    do_more_stuff_t <== called by <module>
        args: a=9
    do_more_stuff_t ==> returning to <module>

and here we get none:

    >>> do_more_stuff_t(4, debug=False)

###Enabling with ints rather than booleans

Sometimes it's desirable for a function to log debugging messages as it executes.
Instead of a simple bool, you can use a nonnegative int as the enabling value
and treat it as specifying a level of verbosity.

    >>> DEBUG_MSG_BASIC = 1
    >>> DEBUG_MSG_VERBOSE = 2
    >>> DEBUG_MSG_MOREVERBOSE = 3  # etc.
    >>> @log_calls(enabled_kwd='debuglevel')
    ... def do_stuff_with_commentary(*args, debuglevel=0):
    ...     if debuglevel >= DEBUG_MSG_VERBOSE:
    ...         print("*** extra debugging info ***")

No output:

    >>> do_stuff_with_commentary()

Only log_calls output:

    >>> do_stuff_with_commentary(debuglevel=DEBUG_MSG_BASIC)
    do_stuff_with_commentary <== called by <module>
        args: debuglevel=1
    do_stuff_with_commentary ==> returning to <module>

log_calls output plus the function's debugging reportage:

    >>> do_stuff_with_commentary(debuglevel=DEBUG_MSG_VERBOSE)
    do_stuff_with_commentary <== called by <module>
        args: debuglevel=2
    *** extra debugging info ***
    do_stuff_with_commentary ==> returning to <module>


##Logging

`log_calls` works well with loggers obtained from Python's `logging` module.
First, we'll set up a logger with a single, console handler. Because `doctest`
doesn't capture output written to `stderr` (the default stream on which console
handlers write), we'll send the console handler's output to `stdout`, using
the default format for loggers, `<loglevel>:<loggername>:<message>`.

    >>> import logging
    >>> import sys
    >>> ch = logging.StreamHandler(stream=sys.stdout)
    >>> logging.basicConfig(handlers=[ch])
    >>> logger = logging.getLogger('mylogger')
    >>> logger.setLevel(logging.DEBUG)

###The `logger` parameter
The `logger` keyword parameter tells log_calls to write its output using
that logger rather than the `print` function:

    >>> @log_calls(logger=logger)
    ... def somefunc(v1, v2):
    ...     logger.debug(v1 + v2)
    >>> somefunc(5, 16)       # doctest: +NORMALIZE_WHITESPACE
    DEBUG:mylogger:somefunc <== called by <module>
        args: v1=5, v2=16
    DEBUG:mylogger:21
    DEBUG:mylogger:somefunc ==> returning to <module>

    >>> @log_calls(logger=logger)
    ... def anotherfunc():
    ...     somefunc(17, 19)
    >>> anotherfunc()       # doctest: +NORMALIZE_WHITESPACE
    DEBUG:mylogger:anotherfunc <== called by <module>
    DEBUG:mylogger:somefunc <== called by anotherfunc
        args: v1=17, v2=19
    DEBUG:mylogger:36
    DEBUG:mylogger:somefunc ==> returning to anotherfunc
    DEBUG:mylogger:anotherfunc ==> returning to <module>

###The `logger_kwd` parameter
Once you've used the `logger` keyword parameter to specify a logger,there's no way
to change the destination of `log_calls` output subsequently. However, you can use
the `logger_kwd` keyword parameter to make the destination late-bound.
As with other `*_kwd` parameters, the `logger_kwd` parameter specifies the name of
a keyword parameter for the wrapped function; it takes precedence over the
`logger` parameter when it is passed as an argument to that function.

In the following example, although `logger_kwd='logger_'` is supplied to `log_calls`,
no `logger_=foo` is passed to the wrapped function `r` in the actual call, 
and no `logger=bar` is supplied, so `log_calls` uses the default writing function,
`print`.

    >>> @log_calls(enabled_kwd='enable', args_sep_kwd='sep_', logger_kwd='logger_')
    ... def r(x, y, z, **kwargs):
    ...     print(x * y + z)
    >>> r(1, 2, 3, enable=True)
    r <== called by <module>
        args: x=1, y=2, z=3, [**]kwargs={'enable': True}
    5
    r ==> returning to <module>

D    efine two more functions, with the outermost function `t` also using
`logger_kwd ='logger_'`, and pass `logger_=logger` to `t` when calling it.
Now both `t` and `r` use `logger` for output:

    >>> def s(x, y, z, **kwargs):
    ...     r(x, y, z, **kwargs)
    >>> @log_calls(enabled_kwd='enable', args_sep_kwd='sep_', logger_kwd='logger_')
    ... def t(x, y, z, **kwargs):
    ...     s(x, y, z, **kwargs)

    >>> # kwargs == {'logger_': <logging.Logger object at 0x...>,
    >>> #            'enable': True, 'sep_': '\\n'}
    >>> t(1,2,3, enable=True, sep_='\\n', logger_=logger) # doctest: +SKIP, +NORMALIZE_WHITESPACE, +ELLIPSIS
    DEBUG:mylogger:t <== called by <module>
        args:
            x=1
            y=2
            z=3
            [**]kwargs={...}
    DEBUG:mylogger:r <== called by s <== t
        args:
            x=1
            y=2
            z=3
            [**]kwargs={...}
    5
    DEBUG:mylogger:r ==> returning to s ==> t
    DEBUG:mylogger:t ==> returning to <module>

###The `loglevel` parameter
`log_calls` also takes a `loglevel` keyword parameter, whose value must be
one of the `logging` module's constants - `logging.DEBUG`, `logging.INFO`, etc.
`log_calls` writes output messages using `logger.log(loglevel, …)`. Thus,
if the `logger`'s log level is higher than `loglevel`, no output will appear:

    >>> logger.setLevel(logging.INFO)   # raise logger's level to INFO
    >>> @log_calls(logger_kwd='logger_', loglevel=logging.DEBUG)
    ... def tt(x, y, z, **kwargs):
    ...     s(x, y, z, **kwargs)
    >>> # No log_calls output from either tt or r,
    >>> # because loglevel for tt and r < level of logger
    >>> tt(1,2,3, enable=True, sep_='\\n', logger_=logger)       # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    5

###A realistic example

Let's add another handler, also sent to stdout but best thought of as writing
to a log file. We'll set up the existing console handler with level INFO, and
the "file" handler with level DEBUG - a typical setup: you want to log all
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

Set logger level to DEBUG:
  the console handler logs calls only for 'infrequent',
  but the "file" handler logs calls for both functions.
  
    >>> logger.setLevel(logging.DEBUG)
    >>> infrequent()       # doctest: +NORMALIZE_WHITESPACE
    [FILE]     INFO:mylogger: infrequent <== called by <module>
    INFO:mylogger:infrequent <== called by <module>
    [FILE]    DEBUG:mylogger: popular <== called by infrequent
    [FILE]    DEBUG:mylogger: popular ==> returning to infrequent
    [FILE]     INFO:mylogger: infrequent ==> returning to <module>
    INFO:mylogger:infrequent ==> returning to <module>

Now set logger level to INFO:
  both handlers log calls only for 'infrequent':
  
    >>> logger.setLevel(logging.INFO)
    >>> infrequent()       # doctest: +NORMALIZE_WHITESPACE
    [FILE]     INFO:mylogger: infrequent <== called by <module>
    INFO:mylogger:infrequent <== called by <module>
    [FILE]     INFO:mylogger: infrequent ==> returning to <module>
    INFO:mylogger:infrequent ==> returning to <module>

##Metaclass example

The following class will serve as the metaclass for classes defined in later examples:

    >>> # - - - - - - - - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - -
    >>> # A_meta, a metaclass
    >>> # - - - - - - - - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - -
    >>> from collections import OrderedDict
    >>> separator = '\n'    # default ', ' gives rather long lines
    >>> class A_meta(type):
    ...     @classmethod
    ...     @log_calls(prefix='A_meta.', args_sep=separator, enabled_kwd='A_debug')
    ...     def __prepare__(mcs, cls_name, bases, *, A_debug=False, **kwargs):
    ...         if A_debug:
    ...             print("    mro =", mcs.__mro__)
    ...         super_dict = super().__prepare__(cls_name, bases, **kwargs)
    ...         if A_debug:
    ...             print("    dict from super() = %r" % super_dict)
    ...         super_dict = OrderedDict(super_dict)
    ...         super_dict['key-from-__prepare__'] = 1729
    ...         if A_debug:
    ...             print("    Returning dict: %s" % super_dict)
    ...         return super_dict
    ...
    ...     @log_calls(prefix='A_meta.', args_sep=separator, enabled_kwd='A_debug')
    ...     def __new__(mcs, cls_name, bases, cls_members: dict, *, A_debug=False, **kwargs):
    ...         cls_members['key-from-__new__'] = "No, Hardy!"
    ...         if A_debug:
    ...             print("    calling super() with cls_members = %s" % cls_members)
    ...         return super().__new__(mcs, cls_name, bases, cls_members, **kwargs)
    ...
    ...     @log_calls(prefix='A_meta.', args_sep=separator, enabled_kwd='A_debug')
    ...     def __init__(cls, cls_name, bases, cls_members: dict, *, A_debug=False, **kwargs):
    ...         if A_debug:
    ...             print("    cls.__mro__:", str(cls.__mro__))
    ...             print("    type(cls).__mro__[1] =", type(cls).__mro__[1])
    ...         try:
    ...             super().__init__(cls_name, bases, cls_members, **kwargs)
    ...         except TypeError as e:
    ...             # call type.__init__
    ...             if A_debug:
    ...                 print("    calling type.__init__ with no kwargs")
    ...             type.__init__(cls, cls_name, bases, cls_members)

The class `A_meta` defined above is a metaclass: it derives from `type`,
and defines (overrides) methods `__prepare__`, `__new__` and `__init__`.
All of its methods take an explicit keyword parameter `A_debug`,
used as the value of the `log_calls` keyword parameter `enabled_kwd`.
When we include `A_debug=True` as a keyword argument to a class that
uses `A_meta` as its metaclass, that argument gets passed to all of 
`A_meta`'s methods, so calls to them will be logged, and those methods
will also print extra debugging information:

    >>> class A(metaclass=A_meta, A_debug=True):    # doctest: +NORMALIZE_WHITESPACE
    ...     pass
    A_meta.__prepare__ <== called by <module>
        args:
            mcs=<class '__main__.A_meta'>
            cls_name='A'
            bases=()
            A_debug=True
        mro = (<class '__main__.A_meta'>, <class 'type'>, <class 'object'>)
        dict from super() = {}
        Returning dict: OrderedDict([('key-from-__prepare__', 1729)])
    A_meta.__prepare__ ==> returning to <module>
    A_meta.__new__ <== called by <module>
        args:
            mcs=<class '__main__.A_meta'>
            cls_name='A'
            bases=()
            cls_members=OrderedDict([('key-from-__prepare__', 1729),
                                     ('__module__', '__main__'),
                                     ('__qualname__', 'A')])
            A_debug=True
        calling super() with cls_members = OrderedDict([('key-from-__prepare__', 1729),
                                                        ('__module__', '__main__'),
                                                        ('__qualname__', 'A'),
                                                        ('key-from-__new__', 'No, Hardy!')])
    A_meta.__new__ ==> returning to <module>
    A_meta.__init__ <== called by <module>
        args:
            cls=<class '__main__.A'>
            cls_name='A'
            bases=()
            cls_members=OrderedDict([('key-from-__prepare__', 1729),
                                     ('__module__', '__main__'),
                                     ('__qualname__', 'A'),
                                     ('key-from-__new__', 'No, Hardy!')])
            A_debug=True
        cls.__mro__: (<class '__main__.A'>, <class 'object'>)
        type(cls).__mro__[1] = <class 'type'>
    A_meta.__init__ ==> returning to <module>

If we pass `A_debug=False` (or omit it), `A_meta`'s methods won't produce
any debugging output:

    >>> class AA(metaclass=A_meta, A_debug=False):    # doctest: +NORMALIZE_WHITESPACE
    ...     pass


##Appendix – Keyword Parameters Reference

The decorator takes various keyword arguments, all with hopefully sensible defaults:

Keyword parameter | Default value | Description
----------------: | :------------ | :------------------
       log_args   | `True`          | arguments passed to the (decorated) function will be logged.
       log_retval | `False`         | If True/truthy, log what the wrapped function returns. At most 60 chars are printed, with a trailing ellipsis if the value is truncated.
       args_sep   | `', '`          | `str` used to separate args. The default is  ', ', which lists all args on the same line. If args_sep='\n' is used, then additional spaces are appended to that to make for a neater display. Other separators in which '\n' occurs are left unchanged, and are untested -- experiment/use at your own risk.
       args_sep_kwd| `''`            | A `str` giving the name of a keyword arg of the wrapped function, whose value determines the args_sep to use. Takes precedence over args_sep if given.
       enabled    | `True`          | if 'truthy', then logging will occur
       enabled_kwd| `''`            | A `str` giving the name of a keyword arg of the wrapped function, whose value determines whether messages are written (truthy <==> they are written). Takes precedence over 'enabled' if given. See the discussion and examples/doctests in the [`enabled_kwd` section](#section__enabled_kwd) for the precise rules.
       prefix    | `''`          | A `str` to prefix the function name with when it is used in logged messages: on entry, in reporting return value (if log_retval) and on exit (if log_exit).
       log_exit  | `True`          | If True (the default), the decorator will log an exiting message after calling the function, and before returning what the function returned.
       logger    | `None`          | If not `None`, a `Logger` which will be used to write all messages. Otherwise, `print` is used.
       logger_kwd | `''`            | A `str` giving the name of a keyword arg of the wrapped function, and then the logger used is the value of that arg passed to the function, provided that it *is* a `Logger`. Takes precedence over `logger` if given.|
       loglevel    | `logging.DEBUG` | Logging level, ignored unless a logger is specified. This should be one of the constant values defined by the `logging` module, unless you've added your own levels.

