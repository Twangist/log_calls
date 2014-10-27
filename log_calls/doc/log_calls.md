#*log_calls* — a decorator for debugging
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

###The *enabled* parameter (default – *True*)
The most basic example:

    >>> @log_calls()                 # enabled=True is the default
    ... def fn0(a, b, c):
    ...     pass
    >>> fn0(1, 2, 3)
    fn0 <== called by <module>
        arguments: a=1, b=2, c=3
    fn0 ==> returning to <module>

The next most basic:

    >>> @log_calls(enabled=False)    # no output
    ... def fn1(a, b, c):
    ...     pass
    >>> fn1(1, 2, 3)

###The *args_sep* parameter (default – `', '`)
The `args_sep` parameter specifies the character or string used to separate 
arguments. If the string ends in  (or is) `\n`, additional whitespace 
is appended so that arguments line up nicely:

    >>> @log_calls(args_sep='\\n')
    ... def fn2(a, b, c, **kwargs):
    ...     print(a + b + c)
    >>> fn2(1, 2, 3, u='you')        # doctest: +SKIP, +NORMALIZE_WHITESPACE
    fn2 <== called by <module>
        arguments:
            a=1
            b=2
            c=3
            [**]kwargs={'u': 'you'}
    6
    fn2 ==> returning to <module>

**NOTE**: *In all the doctest examples in this document, you'll see* `'\\n'` 
*where in actual code you'd write* `'\n'`. *This is a `doctest` quirk: all 
the examples herein work (as tests, they pass), and they would fail if* 
`'\n'` *were used. The only alternative would be to use raw character strings 
and write* `r'\n'`, *which is not obviously better.*

###The *log_exit* parameter (default – *True*)

When `False`, this parameter suppresses the `... ==> returning to ...` line 
indicating the function's return to its caller.

    >>> @log_calls(log_exit=False)
    ... def fn3(a, b, c):
    ...     return a + b + c
    >>> _ = fn3(1, 2, 3)
    fn3 <== called by <module>
        arguments: a=1, b=2, c=3

###The *log_retval* parameter (default – *False*)

When `True`, this parameter displays the value returned by the function:
 
    >>> @log_calls(log_retval=True)
    ... def fn4(a, b, c):
    ...     return a + b + c
    >>> _ = fn4(1, 2, 3)
    fn4 <== called by <module>
        arguments: a=1, b=2, c=3
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
    ... def g3(optional=''):    # g3 will have an 'arguments:' section
    ...     g2()
    >>> def g4():
    ...     g3()
    >>> @log_calls()
    ... def g5():
    ...     g4()
    >>> g5()
    g5 <== called by <module>
    g3 <== called by g4 <== g5
        arguments: <none>
        defaults:  optional=''
    g1 <== called by g2 <== g3
    g1 ==> returning to g2 ==> g3
    g3 ==> returning to g4 ==> g5
    g5 ==> returning to <module>


###Functions with no parameters, calls with no arguments
In the previous example, four of the five functions have no parameters,
so `log_calls` shows no `arguments:` section for them. `g3` takes one
optional argument but is called with none, so log_calls displays
`arguments: <none>`. It also displays the default value used by the function
for the parameter that wasn't given a value by any argument.

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


##Decorating methods: using the *prefix* keyword parameter

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

    >>> print("length of Point(1, 2) =", round(Point(1, 2).length(), 2))    # doctest: +ELLIPSIS
    Point.length <== called by <module>
        arguments: self=Point(1, 2)
    Point.distance <== called by Point.length
        arguments: pt1=Point(1, 2), pt2=Point(0, 0)
    Point.distance ==> returning to Point.length
        Point.length return value: 2.236...
    Point.length ==> returning to <module>
    length of Point(1, 2) = 2.24


##Direct (static) and indirect (dynamic) parameter values
-------------------------------------------------------
###Dynamical control of logging

Every parameter of `log_calls` except `prefix` and 'max_history' can take 
two kinds of values: *direct* and *indirect*, which you can think of as 
*static* and *dynamic* respectively. Direct/static values are actual values 
used when the decorated function is interpreted, e.g. `enabled=True`, 
`args_sep=" / "`. Such values are established once and for all when 
the Python interpreter parses the definition of a decorated function 
and creates a function object. If a variable is used as a parameter value, 
its value at the time Python processes the definition is "frozen" for 
the created function object. Subsequently changing the value
of the variable will *not* affect the behavior of the decorator.

For example, suppose `DEBUG` is a module-level variable initialized to `False`, and you use this code:

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

**NOTE**: *This last example illustrates a perhaps subtle point: 
if you omit the* `enabled` *parameter altogether, logging will occur, 
as the default value is (the direct value)* `True`; *however, if you 
specify an indirect value for* `enabled` *and the named indirect 
keyword is not supplied in a call, then that call* won't *be logged. 
In other words, if you specify an indirect value for the* `enabled` *parameter 
then the default effective value of the enabled setting is* `False`* -- 
calls are not logged unless the named parameter is found and its value is true.*

Additional tests for *log_args*, *log_retval*, *log_exit* with indirect values
------------------------------------------------------------------------

    >>> @log_calls(log_args='logargs=', log_retval='logretval=', log_exit='logexit=')
    ... def f(x, **kwargs):
    ...     return x**2
    >>> _ = f(2, logexit=False)   # logargs=True, log_retval=False: defaults
    f <== called by <module>
        arguments: x=2, [**]kwargs={'logexit': False}

    >>> _ = f(5, logargs=False, logretval=True) # log_exit=True, default
    f <== called by <module>
        f return value: 25
    f ==> returning to <module>

Controlling format 'from above'
-------------------------------

This indirection mechanism allows a calling function to control the appearance
of logged calls to functions lower in the call chain, provided they all use
the same indirect parameter keywords.

In the next example, the separator value supplied to `g` by keyword argument
propagates to `f` when `g` calls it:

    >>> @log_calls(args_sep='sep_')
    ... def f(a, b, c, *, u='', v=9, **kwargs):
    ...     print(a+b+c)
    >>> f(1,2,3, u='you')                 # doctest: +NORMALIZE_WHITESPACE
    f <== called by <module>
        arguments: a=1, b=2, c=3, u='you'
        defaults:  v=9
    6
    f ==> returning to <module>

    >>> f(1,2,3, u="you", sep_='\\n')     # doctest: +SKIP, +NORMALIZE_WHITESPACE
    f <== called by <module>
        arguments:
            a=1
            b=2
            c=3
            u='you'
            [**]kwargs={'sep_': '\\n'}
        defaults:
            v=9
    6
    f ==> returning to <module>

In the next example, again the separator value supplied to `g` by keyword argument
propagates to `f`. Note that the arguments 42 and 99 end up in the "varargs" tuple 
of `g`. We've give the variable-size, collect-all-the-rest arguments unusual names 
to illustrate that whatever you call these parameters, their roles are unambiguous 
and their names are available to `log_calls`, which will use those names:

    >>> @log_calls(args_sep_kwd='sep_')
    ... def g(a, b, c, *args, **kwargs):
    ...     f(a, b, c, **kwargs)
    >>> g(1,2,3, 42, 99, sep_='\\n')       # doctest: +SKIP, +NORMALIZE_WHITESPACE
    g <== called by <module>
        arguments:
            a=1
            b=2
            c=3
            [*]args=(42, 99)
            [**]kwargs={'sep_': '\\n'}
    f <== called by g
        arguments:
            a=1
            b=2
            c=3
            [**]kwargs={'sep_': '\\n'}
        defaults:
            u=''
            v=9
    6
    f ==> returning to g
    g ==> returning to <module>


###An artificial example, using the most recent *f* and *g*

NOTE: In the following example,

    [**]kwargs={'sep_': ', ', 'u': 'somebody'}
or

    [**]kwargs={'u': 'somebody', 'sep_': ', '}

and similarly for `g_kwargs`. Only the order of items is different,
but doctest is very literal, and provides no way other than ellipsis
to tell it that the order doesn't matter.

    >>> @log_calls(args_sep='sep_=', enabled='enable=')
    ... def h(a, b, *args, enable=True, **kwargs):
    ...     if enable:
    ...         g(a, b, 10, *args, **kwargs)
    >>> for i in range(2):
    ...     h(i, i+1, 'a', 'b', u='somebody', enable=i%2, sep_=', ')       # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    h <== called by <module>
        arguments: a=1, b=2, [*]args=('a', 'b'), enable=1, [**]kwargs={...}
    g <== called by h
        arguments: a=1, b=2, c=10, [*]g_args=('a', 'b'), [**]g_kwargs={...}
    f <== called by g
        arguments: a=1, b=2, c=10, u='somebody', [**]kwargs={'sep_': ', '}
        defaults:  v=9
    13
    f ==> returning to g
    g ==> returning to h
    h ==> returning to <module>

##More examples of dynamically enabling/disabling *log_calls* output

Suppose you use `enabled='debug'` to decorate a function `f`. Then a call to `f`
will be logged if one of the following conditions holds:

1. the keyword is *not* passed, but the function `f` explicitly declares
   the keyword parameter (`debug`) and assigns it a true default value
   (e.g. `def f(x, debug=True)` or `def f(x, debug=2)`), or
2. the call passes the keyword mentioned with a true value,
   e.g.`debug=17`.

**NOTE**: *When referring to values, I'll use* true *with lowercase* t *to mean "truthy", and* false *with lowercase* f *to mean "falsy" .* 

###Examples of condition 1. (explicit parameter)

It's instructive to consider examples where the wrapped function explicitly
provides the keyword named by the `enabled` parameter.

Let the wrapped function provide a default value of `True` for the parameter
named by the `enabled` parameter:

    >>> @log_calls(enabled='debug=')
    ... def do_more_stuff_t(a, debug=True, **kwargs):
    ...     pass

Here we get output by default, without having to pass `debug=True`:

    >>> do_more_stuff_t(9)
    do_more_stuff_t <== called by <module>
        arguments: a=9
        defaults:  debug=True
    do_more_stuff_t ==> returning to <module>

and here we get none:

    >>> do_more_stuff_t(4, debug=False)

Now let the explicit indirect parameter have a false value:

    >>> @log_calls(enabled='debug=')
    ... def do_more_stuff_f(a, debug=False, **kwargs):
    ...     pass

Here we get no output, as `debug=False` (the wrapped function's default value):

    >>> do_more_stuff_f(3)

but here we do:

    >>> do_more_stuff_f(4, debug=True)
    do_more_stuff_f <== called by <module>
        arguments: a=4, debug=True
    do_more_stuff_f ==> returning to <module>

###Examples of condition 2. (implicit parameter)

    >>> @log_calls(enabled='debug=')
    ... def bar(**kwargs):
    ...     pass
    >>> bar(debug=False)  # no output
    >>> bar(debug=True)   # output
    bar <== called by <module>
        arguments: [**]kwargs={'debug': True}
    bar ==> returning to <module>

    >>> bar()         # no output: enabled=<keyword> overrides enabled=True


##Enabling with *int*s rather than *bool*s

Sometimes it's desirable for a function to print or log debugging messages 
as it executes. It's the oldest form of debugging! Instead of a simple bool,
you can use a nonnegative int as the enabling value and treat it as a level 
of verbosity.

    >>> DEBUG_MSG_BASIC = 1
    >>> DEBUG_MSG_VERBOSE = 2
    >>> DEBUG_MSG_MOREVERBOSE = 3  # etc.
    >>> @log_calls(enabled_kwd='debuglevel')
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


##Logging

`log_calls` works well with loggers obtained from Python's `logging` module.
First, we'll set up a logger with a single handler that writes to the console. 
Because `doctest` doesn't capture output written to `stderr` (the default stream 
to which console handlers write), we'll send the console handler's output to 
`stdout`, using the default format for loggers, `<loglevel>:<loggername>:<message>`.

    >>> import logging
    >>> import sys
    >>> ch = logging.StreamHandler(stream=sys.stdout)
    >>> logging.basicConfig(handlers=[ch])
    >>> logger = logging.getLogger('mylogger')
    >>> logger.setLevel(logging.DEBUG)

###The *logger* parameter (default – *None*)

The `logger` keyword parameter tells `log_calls` to write its output using
that logger rather than the `print` function:

    >>> @log_calls(logger=logger)
    ... def somefunc(v1, v2):
    ...     logger.debug(v1 + v2)
    >>> somefunc(5, 16)       # doctest: +NORMALIZE_WHITESPACE
    DEBUG:mylogger:somefunc <== called by <module>
        arguments: v1=5, v2=16
    DEBUG:mylogger:21
    DEBUG:mylogger:somefunc ==> returning to <module>

    >>> @log_calls(logger=logger)
    ... def anotherfunc():
    ...     somefunc(17, 19)
    >>> anotherfunc()       # doctest: +NORMALIZE_WHITESPACE
    DEBUG:mylogger:anotherfunc <== called by <module>
    DEBUG:mylogger:somefunc <== called by anotherfunc
        arguments: v1=17, v2=19
    DEBUG:mylogger:36
    DEBUG:mylogger:somefunc ==> returning to anotherfunc
    DEBUG:mylogger:anotherfunc ==> returning to <module>

###Indirect values for the *logger* parameter
As usual, once you've used the `logger` keyword parameter to specify a logger,
there's no way to change the destination of `log_calls` output subsequently. 
However, you can use an indirect value for the `logger` parameter to make 
the destination late-bound.

In the following example, although logger='logger_' is supplied to `log_calls`,
no `logger_=foo` is passed to the wrapped function `r` in the actual call, and no
`logger=bar` is supplied, so `log_calls` uses the default writing function, `print`.
(Furthermore, no args separator is passed with the `sep` keyword, so `log_calls`
uses the default separator ', '.)

    >>> @log_calls(enabled_kwd='enable', args_sep_kwd='sep_', logger_kwd='logger_')
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
    >>> @log_calls(enabled_kwd='enable', args_sep_kwd='sep_', logger_kwd='logger_')
    ... def t(x, y, z, **kwargs):
    ...     s(x, y, z, **kwargs)

    >>> # kwargs == {'logger_': <logging.Logger object at 0x...>,
    >>> #            'enable': True, 'sep_': '\\n'}
    >>> t(1,2,3, enable=True, sep_='\\n', logger_=logger) # doctest: +SKIP, +NORMALIZE_WHITESPACE, +ELLIPSIS
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

###The *loglevel* parameter (default – *logging.DEBUG*)

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

##Test of indirect loglevel

logger's level is still logging.INFO:
    >>> assert logger.level == logging.INFO

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

###A realistic example

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
  both handlers log calls only for `infrequent`:
  
    >>> logger.setLevel(logging.INFO)
    >>> infrequent()       # doctest: +NORMALIZE_WHITESPACE
    [FILE]     INFO:mylogger: infrequent <== called by <module>
    INFO:mylogger:infrequent <== called by <module>
    [FILE]     INFO:mylogger: infrequent ==> returning to <module>
    INFO:mylogger:infrequent ==> returning to <module>

##Metaclass example

The following class `A_meta` will serve as the metaclass for classes defined subsequently:

    >>> # - - - - - - - - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - -
    >>> # A_meta, a metaclass
    >>> # - - - - - - - - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - -
    >>> from collections import OrderedDict
    >>> separator = '\n'    # default ', ' gives rather long lines
    >>> class A_meta(type):
    ...     @classmethod
    ...     @log_calls(prefix='A_meta.', args_sep=separator, enabled='A_debug')
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
    ...     @log_calls(prefix='A_meta.', args_sep=separator, enabled='A_debug')
    ...     def __new__(mcs, cls_name, bases, cls_members: dict, *, A_debug=False, **kwargs):
    ...         cls_members['key-from-__new__'] = "No, Hardy!"
    ...         if A_debug:
    ...             print("    calling super() with cls_members = %s" % cls_members)
    ...         return super().__new__(mcs, cls_name, bases, cls_members, **kwargs)
    ...
    ...     @log_calls(prefix='A_meta.', args_sep=separator, enabled='A_debug')
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

The class `A_meta` is a metaclass: it derives from `type`,
and defines (overrides) methods `__prepare__`, `__new__` and `__init__`.
All of its methods take an explicit keyword parameter `A_debug`,
used as the indirect value of the `log_calls` keyword parameter `enabled`.
When we include `A_debug=True` as a keyword argument to a class that
uses `A_meta` as its metaclass, that argument gets passed to all of 
`A_meta`'s methods, so calls to them will be logged, and those methods
will also print extra debugging information:

    >>> class A(metaclass=A_meta, A_debug=True):    # doctest: +NORMALIZE_WHITESPACE
    ...     pass
    A_meta.__prepare__ <== called by <module>
        arguments:
            mcs=<class '__main__.A_meta'>
            cls_name='A'
            bases=()
            A_debug=True
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
            A_debug=True
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
            A_debug=True
        cls.__mro__: (<class '__main__.A'>, <class 'object'>)
        type(cls).__mro__[1] = <class 'type'>
    A_meta.__init__ ==> returning to <module>

If we pass `A_debug=False` (or omit it), `A_meta`'s methods won't produce
any debugging output:

    >>> class AA(metaclass=A_meta, A_debug=False):    # doctest: +NORMALIZE_WHITESPACE
    ...     pass

## Attributes added by *log_calls* to a decorated function
The `log_calls` decorator adds two attributes to a decorated function:

* `log_calls_settings`
* `stats`

Each is an object which in turn exposes further attributes that allow you to
access the settings and features of the decorator. The `log_calls_settings`
object provides an interface to the settings of a decorated function.
The `stats` object provides access to decorated function's call history and
to a few of its statistics.

###The *log_calls_settings* attribute
The `log_calls_settings` attribute of a decorated function lets you control 
the decorator's settings for that function, via a mapping (dict-like) interface, 
and equivalently, via further attributes of the object. The mapping keys and
the attribute names are simply the `log_calls` keywords. `log_calls_settings`
also provides further methods for interacting with the settings in dict-like ways.
It's an instance of the `DecoSettingsMapping` class, defined in `deco_settings.py`.
That class has its own tests, in `log_calls/tests/test_deco_settings.py`, 
so there's no need to test it exhaustively here; we'll just go over how to use it.

#### *__getitem__* and *__setitem__* – the mapping interface and the attribute interface to settings

Once you've decorated a function with `log_calls`:

    >>> @log_calls()
    ... def f(*args, **kwargs):
    ...     return 91

you can access and change its settings via the `log_calls_settings` attribute
of the decorated function:

    >>> f.log_calls_settings['enabled'] = False
    >>> f()                                     # no output
    >>> f.log_calls_settings['enabled']
    False
    >>> f.log_calls_settings['log_retval']
    False
    >>> f.log_calls_settings['log_retval'] = True
    >>> f.log_calls_settings['log_elapsed']
    False
    >>> f.log_calls_settings['log_elapsed'] = True

You can use the same keywords as attributes of `log_calls_settings`
instead of as keywords to the mapping interface; they're completely
equivalent:

    >>> f.log_calls_settings.log_elapsed
    True
    >>> f.log_calls_settings.log_call_numbers
    False
    >>> f.log_calls_settings.log_call_numbers = True
    >>> f()                                     # doctest: +ELLIPSIS
    f [1] called by <== <module>
        arguments: <none>
        elapsed time: ... [sec]
        f return value: 91
    f [1] returning to ==> <module>
    >>> f.log_calls_settings.log_args = False
    >>> f.log_calls_settings.log_elapsed = False
    >>> f.log_calls_settings.log_retval = False
    >>> f()                                     # doctest: +ELLIPSIS
    f [2] called by <== <module>
    f [2] returning to ==> <module>

#### The *update*, *as_OrderedDict* and *as_dict* methods
The `log_calls_settings` object provides an `update` function so that
you can update several settings in one call:

    >>> f.log_calls_settings.update(
    ...     log_args=True, log_elapsed=False, log_call_numbers=False,
    ...     log_retval=False)
    >>> f()
    f called by <== <module>
        arguments: <none>
    f returning to ==> <module>

You can retrieve the entire collection of settings as either an `OrderedDict`
using the `as_OrderedDict()` method, or as a `dict` using `as_dict()`. 
Either can serve as a snapshot of the settings, so that you can change settings 
temporarily, and then restore the original settings from the snapshot. 
The update method can take one or more dicts, in addition to keyword arguments
as shown above. For example:

Retrieve settings:

    >>> d = f.log_calls_settings.as_dict()
    >>> d
    blah_dict

change settings temporarily:

    >>> f.log_calls_settings.update(
    ...     log_args=False, log_elapsed=True, log_call_numbers=True,
    ...     log_retval=True)

use the new settings for f:

    >>> # ...

and restore original settings:

    >>> f.log_calls_settings.update(d)
    >>> f.log_calls_settings.as_dict()
    blah_dict-as-before

#### The *log_call_numbers* attribute (default – *False*)
`log_calls` continues to track call numbers even when it isn't reporting
them. The last call to f was the third; the following call will be the fourth:

    >>> f.log_calls_settings['log_call_numbers'] = True
    >>> f()
    f [4] called by <== <module>
        arguments: <none>
    f [4] returning to ==> <module>


#RESUME / *TODO TODO TODO*

You can also use 

You can use `log_calls_settings` to set indirect values: ... TODO ...  

Only restrictions: (which settings can you NOT set... TODO ... )

__getitem__
__setitem__
__len__
__iter__
__contains__
items
__repr__
__str__
update

as_OrderedDict
as_dict


#RESUME / *TODO TODO TODO*

    @log_calls(enabled='enable=', args_sep='sep_=', logger='logger_=')
    def myfunc(x, y, z, **kwargs):
        pass

    print("===============================")
    print("testing descriptors:")

    d = myfunc.log_calls_settings
    d['enabled'] = False
    d['log_retval'] = True
    d['log_exit'] = False
    d['log_args'] = 'log_args='

    # KeyError:
    try:
        print("About to try '%s'" % "d['nosuchsetting'] = True")
        d['nosuchsetting'] = True
    except KeyError as e:
        print("Expected exception:", e)

    # Now try descriptors/properties/err attributes - YES!
    # here's the descriptors' __get__ method being exercised
    print('d.enabled =', d.enabled)
    print('d.log_retval =', d.log_retval)
    print('d.log_exit =', d.log_exit)
    print('d.log_args =', d.log_args)
    print("d.prefix = '%s'" % d.prefix)
    print('d.logger =', d.logger)
    print('d.loglevel =', d.loglevel)
    print("d.args_sep = '%s'" % d.args_sep)

    print("d.record_history =" , d.record_history)
    print("d.max_history =" , d.max_history)
    print("d.log_elapsed =", d.log_elapsed)
    print("d.log_call_number =", d.log_call_number)

###The *stats* attribute

Call history and statistics

#### `stats.num_calls_total`
#### `stats.num_calls_logged`
#### `stats.call_history`
#### `stats.call_history_as_csv`
#### `stats.total_elapsed`

#### Method: `stats.clear_history(max_history=0)`

# *TODO TODO TODO* END.


##Appendix – Keyword Parameters Reference

The `log_calls` decorator takes various keyword arguments, all with hopefully sensible defaults:

Keyword parameter | Default value | Description
----------------: | :------------ | :------------------
       `log_args`   | `True`          | arguments passed to the decorated function, and default values used by the function, will be logged.
       `log_retval` | `False`         | If true (truthy), log what the decorated function returns. At most 60 chars are printed, with a trailing ellipsis if the value is truncated.
       `args_sep`   | `', '`          | `str` used to separate arguments. The default is  `', '`, which lists all args on the same line. If `args_sep='\n'` is used, or if more generally the `args_sep` string ends in `\n`, then additional spaces are appended to the separator for a neater display. Other separators in which `'\n'` occurs are left unchanged, and are untested – experiment/use at your own risk.
       `enabled`    | `True`          | An `int`. If true, then logging will occur.
       `prefix`     | `''`            | A `str` to prefix the function name with in logged messages: on entry, in reporting return value (if `log_retval` is true) and on exit (if `log_exit` is true).
       `log_exit`   | `True`          | If true, the decorator will log an exiting message after calling the function of the form `f returning to ==> caller`, and before returning what the function returned.
       `logger`     | `None`          | If not `None`, a `Logger` which will be used to write all messages. Otherwise, `print` is used.
       `loglevel`   | `logging.DEBUG` | Logging level, ignored unless a logger is specified. This should be one of the logging levels recognized by the `logging` module – one of the constants defined by that module, or a custom level you've added.
       `record_history` | `False`     | If true, an array of records will be kept, one for each call to the function. Each record holds: call number (1-based), arguments and defaulted keyword arguments, return value, time elapsed, time of call, caller (call chain), prefixed function name.
       `max_history` | `0`            | An `int`. *value* > 0 --> store at most *value*-many records, oldest records overwritten; *value* ≤ 0 --> store unboundedly many records. Ignored unless `record_history` is true.
       `log_call_number` | `False`    | If true, display the (1-based) number of the function call, e.g. `f [3] called by <== <module>` and `f [3] returning to ==> <module>` for the 3rd logged call. This would correspond to the 3rd record in the function's call history, if `record_history` is true.
       `log_elapsed` | `False`        | If true, display how long it took the function to execute, in seconds.


####— Brian O'Neill, October 2014, NYC
